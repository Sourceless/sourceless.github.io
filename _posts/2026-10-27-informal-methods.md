---
layout: post
title: "Informal Methods"
date: 2026-10-27
tags: [ai, agents, agentic engineering, formal methods, user stories, testing, bdd]
summary: "Formal methods let you trust agents to write code unsupervised, but they're intimidating to start with. Here are some informal methods borrowed from UX, Product, Delivery and QA that get you most of the way there."
---

In my (unfinished) final year of university, I worked on a project to translate
Alloy programs into equivalent Prolog programs. Now, I never finished that
project, but it gave me an understanding of both logic programming and
lightweight formal methods. Over a decade later, both of those things have
turned out to be really important to my career (much to my surprise!).
{: .aside}

## What are Formal Methods?

Formal methods are a set of tools for specifying programs in a way that they
can be mathematically tested to show that they are correct (or incorrect).

There's a lot of different tools out there, such as Alloy, TLA+, and Lean just
to name a few.

One consequence of using formal methods is that you can draw a very neat box
around an implementation and use an agent to fill it in. We can then very
cheaply test if the implementation is correct. This gives us a huge amount
of confidence in the correctness of an implementation, which in turn means
we can leave agents to do this unsupervised and unreviewed!

Here's [a great article on applying this to a real world problem](https://kim-em.github.io/blog/2026-7-24-why-lean-is-faster-than-rust/).

## Informal Methods

That's nice and all, but if you're new to formal methods they can be a bit
intimidating to approach. Instead, let me recommend to you some *informal methods*,
ways of getting higher quality output from your agents before you resort
to formal specs!

All of these approaches are less used by engineers than they perhaps should be,
but are VERY common in the professions that surround and support software
engineers: User Experience, Product, Delivery Management, and QA.

As a well-rounded engineer, it's good to know about these approaches, because
by learning from our colleagues, we can make better software.

### User Stories
We look to our UX and Product friends for inspiration here. Ultimately what matters
to our users is the *observable behaviour* of the systems we create.

User stories are a way of capturing important pieces of that observable behaviour
from the perspective of the people who'll be using our system.

> **As a** driver\\
> **I want to** start my car\\
> **So that** I can drive to the store

Nowhere in there did I say that the car should use a key or a push-button start;
I'm trying to get to the store, and the type of car I'm using shouldn't matter.

As is often the case, gov.uk has [great guidance on this](https://www.gov.uk/service-manual/agile-delivery/writing-user-stories).

### Tracer Bullets
It's much easier for both humans and agents to get smaller things right. It's
also no secret that breaking up work is a skill in its own right!

To get better results with agents, it's important to have a tight verification loop.
The last thing you want is to build a huge amount of pieces just to find that it
doesn't fit together; you've wasted a lot of your own time!

The fix to this is annoyingly simple; we try to work on much smaller versions of a whole problem.
We build finger sandwiches instead of subs.

Matt Pocock has [a good article on this](https://www.aihero.dev/tracer-bullets).

### Traceability Matrices
How do we make sure that our requirements actually get addressed, and none
of them get forgotten? Delivery managers have been doing this forever using
scary Excel sheets: the traceability matrix.

The core idea here is very simple: you match each requirement you identified to
an observable outcome or test.

That's it, really. It looks a lot scarier than it is. The trick is that you can demand
this of your agents and it'll act as a guide to force them to check their own work.

Here's [a primer on traceability matrices](https://www.geeksforgeeks.org/software-testing/requirement-traceability-matrix/).

### Black-Box Testing

Our friends in QA have historically had a very difficult job: take code you didn't
write, and make sure that it does what it's supposed to.

Sound familiar? If you ever want to trust your agents to write code and not have
to read it, this is a skill you're going to have to master!

To do this well you have to put yourself in the shoes of that QA specialist: how
do you test something when you don't know how it works? Well - if you know
the problem being solved and what the solution *should* do, then it's possible
to write tests about that. And if you're clever, you can even be an evil supervillain
and try to make it fail.

You don't have to handwrite the test cases, you just need to think of them.

If you followed the earlier advice to use user stories, then you can use
BDD-style tests and you get the tests and traceability matrix for free!

Here's [a little info on BDD](https://en.wikipedia.org/wiki/Behavior-driven_development).

## Wrapping it up

TL;DR look around you at the people who don't write software day-to-day and ask
yourself how *they* trust what you're doing. That's how you're going to be able
to trust your agents.
