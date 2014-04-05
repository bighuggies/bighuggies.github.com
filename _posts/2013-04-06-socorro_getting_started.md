---
title: A Project Involving Socorro
layout: post
---

As part of my Bachelor of Engineering at the University of Auckland, I am
required to complete a year long research project with a partner. At the end of
the project we present our work along with a comprehensive report detailing what
we've learned. Fortunately my partner is [Tony](http://rfw.name), and Tony had
an awesome time interning for Mozilla over the (New Zealand) summer. Using his
wit and charm he managed to swing us a Mozilla sponsored project revolving
around Socorro, Mozilla's distributed crash collection system.

## What is Socorro?

Socorro is one of those back end things which are critically important, but not
particularly glamorous. Before Tony worked on it for his internship, I had never
heard of it. Mozilla uses Socorro to collect crash reports from, among other
things, Firefox, which with ~450,000,000 users is no small task. To see how
Socorro's architecture is distributed and to get an idea of how it might scale,
you can read [Tony's overview of it's
architecture](http://rfw.name/blog/2013/04/07/making_socorro_easy.html).

## What are we doing to Socorro?

It's currently week 5 of the project, and we've spent most of that time deciding
and planning our direction for this project. We intend on improving what are
some of the wartiest parts of Socorro.

### Configurator

The configurator will be a web tool which will help generate and validate
Socorro configuration files. Socorro is configured with a [collection of INI
files](https://github.com/mozilla/socorro/tree/master/config) which can be hard
to keep in sync. Our configuration tool should hopefully make this simpler by
generating correct config files from a form based web interface. We hope to be
able to export a topology graph of the nodes and storages in the Socorro config,
which should make it easier to spot any derps in the set up.

### Operations Dashboard

Currently Socorro has a [status page](https://crash-stats.mozilla.com/status)
which gives information mainly about jobs in the system. We hope to improve on
this by creating a dashboard which has information about the system components
themselves (the collectors, processors, etc.), including stuff like uptime and
load, with the intent of making it easier to debug problems in the system.

## Going forward

Keep an eye on this blog and on [Tony's](http://rfw.name) as we go forward with
this project. The final deliverable is due in September, so until then expect
fairly frequent updates between us about our progress.
