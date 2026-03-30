---
layout: post
title: "The Phoenix Reborn"
date: 2026-03-30
tags: [ai, llms, claude, phoenix project]
---

If you haven't read "The Phoenix Project" yet, this is your sign from the universe
telling you that it's time. Go on, this post will still be here when you get back.

Still here? Cool.

### A very quick Phoenix Project Recap

An extremely condensed take on the central point of "The Phoenix Project" is:

> Shorten feedback loops as much as possible

In the book and day-to-day DevOps, that's achieved in several ways:
* Colocating ops resources on dev teams, instead of siloing them in separate orgs
* Making use of CI to provide fast feedback in a dev-like environment
* Making use of tests in the development flow
* Having prod-like environments available for testing

Each of these seeks to reduce the amount of time a problem sits waiting before it
can be addressed by someone with the knowledge to fix it.

### Code is free but specification is still expensive

The step in quality of output from top-tier LLMs in late 2025 changed the game.
Code is now easy to produce in good quality and high quantity. The new gap is one
that has always existed: understand whole problems and write a plan detailed enough
to make a solution.

Spec-driven development is a particularly promising output of this; structured input
that captures every possible problem, solution, and decision in a small problem space.

But specs alone aren't enough; fortunately, however, Claude and co are very, VERY
good at writing tests, pipelines, and just about any other verification tooling you
could ever want, including lightweight (or heavyweight!) formal methods.

### Give the AI the tools it needs to succeed

This is the only takeaway that you need from this post. *You must shorten the feedback
loops for the AI as much as possible*. You need to make it possible for it to test
its own work if you want high quality outputs.

At a minimum:
* Linter
* Autoformatter
* Tests
* CI/CD pipelines

This is how you provide fast feedback and get good results; it's exactly the same
principle that devops was built on.

Make your AI aware of them, make it use them, and make it constantly review its own work
(or get another model to do it).
