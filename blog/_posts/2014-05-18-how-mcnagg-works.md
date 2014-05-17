---
title: How mcnagg Works
layout: post
---

[Mike](http://icbmikeblag.azurewebsites.net/) has been bugging me to write a
blog post for a while now, so here's one on [mcnagg](http://mcnagg.tv), why I
made it, what it does, and how it works (also a rambly middle section where I go
on about merging Python iterators).

## What is mcnagg?

mcnagg is the **M**ind**C**rack **N**etwork **agg**regator. If you aren't
familiar, the [Mindcrack Network](http://mindcracklp.com/) is a group of content
creators who collaborate on mostly video game based YouTube content. The network
consists of upwards of 25 members with millions of combined subscribers. From
what I can tell using Google Analytics, mcnagg seems to have a few dozen regular
users.

I created mcnagg because at the time (June 2012) YouTube subscriptions really
sucked (they have gotten better recently, especially with the [collections
feature](https://support.google.com/youtube/answer/3123405?hl=en)). I was having
a hard time keeping up with all the content being produced, and often missing
videos. mcnagg aggregates videos from the Mindcrackers into an easy to skim and
filter list, making it much easier to catch all the videos you want to watch. It
also shows the latest tweets from the Mindcrackers and the top few
[/r/mindcrack](https://reddit.com/r/mindcrack) posts, but that's mainly just to
fill out the right hand side of the page and isn't terribly interesting.

By the way, I am aware that the name is terrible.

## How does it work?

mcnagg is a fairly simple application built in [Python](https://www.python.org/)
using [Tornado](http://www.tornadoweb.org) deployed on [Heroku](www.heroku.com).
Tornado consumes a Mindcrack module which abstracts interaction with the
[YouTube API](https://developers.google.com/youtube/) and manages the data which
powers the website. The front end uses [Bootstrap](http://getbootstrap.com/) and
a mild amount of [jQuery](http://jquery.com/), nothing really to phone home
about.

## The Tornado part

To be honest I haven't really touched the Tornado part since I originally start
the project two years ago. All of my more recent web projects in Python have
been using [Flask](http://flask.pocoo.org/) to create an API which is consumed
by a JavaScript front end. mcnagg is more traditional; the back end serves up
HTML which is generated from templates by the server. As far as I can remember,
Tornado was pretty nice to work with :v.

## The data part

The Tornado part of the application depends on a seperate module which abstracts
the interaction with the YouTube API. This part and the web interface are what I
mainly tinker with and are much more interesting.

The first iteration of mcnagg scraped the YouTube uploads of each Mindcracker
periodically and stored new videos in a [Postgres](http://www.postgresql.org/)
database. Results of database queries by the website were cached in
[memcached](http://memcached.org/). This approach, although I learnt a lot from
implementing it, turned out to be untenable since it was difficult and
computationally intensive to synchronize the two sets of data (YouTube and
Postgres). It turns out that once a video is uploaded it often has its title or
description changed, which wasn't very nice for me.

Currently mcnagg uses the (deprecated) [version 2 of the YouTube Data
API](https://developers.google.com/youtube/2.0/reference).  The first challenge
I faced was loading the data efficiently from YouTube. The V2 api doesn't have a
good way of batching requests, so I had to make a separate HTTP request for each
Mindcracker's uploads. The easy way to optimize this was to parallelize the
requests. Unfortunately the state of multi-threading in Python 2 is really
abysmal, but that's a topic for another blog post. Eventually I got that working
using [ThreadPools (an undocumented but very useful part of the Python
stdlib)](http://stackoverflow.com/questions/3033952 /python-thread-pool-similar-
to-the-multiprocessing-pool).

The next challenge was how to merge these data streams into a chronologically
sorted list. The uploads of each Mindcracker were lazily loaded from YouTube in
descending date order using generator functions, so it was not possible to
simply load all of the videos and sort them. It would also not have been correct
to simply load the first page of each Mindcracker's uploads and take the latest
30 odd videos, because it could be possible that there was a newer video on the
second page of one user than on the first page of another.

After a few false starts I realised that the data structure I needed was a heap.
I could keep taking the latest video from the set of the first video from each
sorted list of videos, and as lists were exhausted they could load the next page
from YouTube as required. Luckily the Python
[heapq](https://docs.python.org/2/library/heapq.html) module provides an easy
way to do this using `heapq.merge()`, which merges iterators into a single
sorted stream without pulling all of the data into memory.

Since the V2 API has been deprecated I have been experimenting with the V3 API
and the [Python bindings for it](https://developers.google.com/api-client-
library/python/). It has some nice batching abilities, but I have yet to find a
good way to reproduce what I have achieved with the V2 api.

Of course a simpler way to do this whole thing would be to maintain a YouTube
account which subscribes to each Mindcracker and pull the subscriptions feed
from that account, but who takes the easy way out when they're messing about
trying to create something cool and learn stuff?

## The front end part

The front end of the website is fairly simple. It presents a list of filters and
a list of videos. Changing the filters will change the list of videos. There are
no accounts or anything super fancy (though your filter preferences are stored
in a cookie). It's very simple and pretty easy to use.

The site initially started off in Bootstrap 2. Recently I have migrated it to
Bootstrap 3. Unfortunately during the transition the site lost a lot of it's
customizations, so it's looking decidedly more Bootstrappy than it used to.
Bootstrap is nice because it makes it super easy to build responsive sites.
mcnagg was the first project I really used Bootstrap in and the experience is
what really sold me on it.

## The future of mcnagg

mcnagg is fun to work on, and I reckon I'll be tinkering with it for ages, but
as YouTube subscriptions start to suck less and I have less time to watch as
much Mindcrack as I'd like, I find myself actually using the site less.
Additionally, the Mindcrack website now has similar functionality to mcnagg
(though not nearly as full featured). When I started mcnagg, there **was no**
Mindcrack website. The utility of mcnagg is starting to fade as other sites step
up their game.

## Final thoughts

This turned into a rambly post on how to merge Python iterators (which is
actually a post I've been meaning to write for months) but hopefully Mike
appreciates the additional SEO he gets from me linking him. Also, if you'd like
to see the source for mcnagg (and the aforementioned iterator merging) you can
of course [view it here](https://github.com/bighuggies/mcnagg).
