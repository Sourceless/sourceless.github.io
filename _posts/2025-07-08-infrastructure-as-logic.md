---
layout: post
title: "Infrastructure as Logic"
date: 2025-07-08
tags: [infrastructure, iac, logic programming]
---
## Infrastructure as Logic

I work in SRE for my day job. As a Director, no less. I'm not all that close
to the coalface anymore, but there are plenty of things I want to know about
the infrastructure for which I'm responsible.

In the last couple of months I've needed to know:
* Which resources aren't tagged?
* What does our network map look like?
* Is this complicated certificate auth configuration correct?
* Is there a network connection between these machines?
* Can I make an alert when we detect this kind of misconfiguration?
* Can we fix that misconfiguration automatically?

All of these you have likely seen before -- many have well-known, productised
solutions! On AWS, where I spend most of my time, there are either products
or existing solutions that address some of these questions.

But I very often hit issues once I want to do something a little strange,
or that the tools I'm given were not intended to solve.

Every one of the things I've listed above follows a common pattern: one or
more connected resources that have some sort of known structural pattern.

### Dropping out
I dropped out of university in my third year. My dissertation project, which
I barely started, was producing a recipe book for converting Alloy programs
to an equivalent representation in Prolog.

That has haunted me for a long time; but the ideas I learned over a decade
ago in proofs and logic programming have found an application in an unlikely
place.

Infrastructure.

### Asking questions
Assuming you have a dump of your cloud state (exercise very much left to the
reader...), you can convert it in to a format such that it fits in to a
knowledge base.

You can then create predicates that talk about the relationships between
resources, from the simple foreign-key sort of relationship, all the way
to structural matching.

The simplest form of this is the
