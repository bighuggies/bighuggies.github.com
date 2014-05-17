---
title: Merging Iterators in Python
layout: post
---

Python iterators lel

## Merging iterators

* Getting videos from a bunch of different YouTube channels
* Return generators for each YouTuber
* Generators get videos in batches
* We need to sort the list of videos by latest videos
* Round robin? Doesn't work
* Enumerate all of the generators to sort
* Each iteration, take the most recent video from the top of the generator
* heapq merge
* heapq is a min heap
* need a key function for complex objects
* reversed \_\_lt\_\_ because min heap
