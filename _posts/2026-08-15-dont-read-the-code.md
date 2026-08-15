---
layout: post
title: "Don't read the code"
date: 2026-08-15
tags: [ai, agents, agentic engineering, formal methods, user stories, devops, opinion]
summary: "Managers adapted to AI agents faster than engineers did, because they had already given up reading the code. Here's the job engineers are moving into."
---

I've recently gone from Director to IC, and I've taken the opportunity to get deep in agentic engineering.
Even before making the change, I've been digging in deep on how to get the most out of agents. There's a lot
of things that really don't work well, producing slop. There are some techniques that work kind of okay,
but need a lot of handholding.

Even if we just speed up how fast we're generating code, we're not actually addressing the bottlenecks and 
challenges that make writing software *hard* - we're just getting to the hard part faster! And to some
degree, I think this is why engineering managers (and especially middle managers) are having an easier time
with the new agentic tools.

One of the things you have to give up as an engineering manager or director, or even a technical lead, is
direct control over code. You may no longer have the time to be the main reviewer, so you inevitably turn
to other tools for ensuring high quality - delegating to senior engineers for reviews, and focusing on
process and *really, really clear outcomes* to help your engineers drive towards the right solution.

I was exposed to this very early in my career at GDS and again when consulting for NHS Digital while
still working as a frontline developer. The philosophy they use to drive high quality results is 
[The Service Standard](https://www.gov.uk/service-manual/service-standard). It's a quick read, but the
hallmarks are first and foremost really understanding the whole problem you are trying to solve, and being
open to throwing away work in the journey to making the right solution.

Another insight was solidified for me recently when listening to [this interview with Charity Majors](https://www.youtube.com/watch?v=HC8T1OlgYi0).
In it, she points out that Ops and QA have worked effectively for a long time without reading code.

So, Engineer who is reading this post. It's time for you to stop reading the code. Code is for robots
and enthusiasts now.

Don't write it. Don't read it. Don't review it.

That's the agent's job now. You are no longer a machine that turns coffee into code. You are nuanced,
flawed, but most importantly human. Coffee optional.

Your main value now is *understanding and communicating problems, and expressing the properties of a good solution*.

## An elegant weapon for a more civilized age

Rejoice! The days of toil are over! Yet now you are required to learn techniques and gain wisdom that
previously were the reserve of the leadership. You are no longer a digger, but a gardener. It's up to you
to create the conditions in which agents can do good work.

### User stories

We must dust off the tools of those who came before - the User Researchers and Product Owners - and take
a fistful of leaves out of their book. Understanding the problems we are solving is vital, and we cannot
understand a problem without understanding those who are suffering from it.

You don't need to walk in their shoes; just beside them for a little bit while they relate their problems
to you is enough. We record what they want to achieve in [User Stories](https://en.wikipedia.org/wiki/User_story).

### Tickets

You have been the slave of tickets for some time now. It's time to become the master of them; treat them
as a place to store information about a problem, nurture them carefully, and relentlessly strike down
the ones that are not worth your time. There will always be more work than you are capable of taking on,
but you won't know what any of it is, or if it's worth your time, unless you write it down.

### Formal Methods

Among the wizards of the recent past there are whispers of machines that can predict the behaviour of
other machines, and find errors before a program is ever run.

You can use those same techniques to find issues early and tightly bound the space of possible programs
that your LLMs will produce. Showing that your user stories are satisfied with tests and proofs all the way
through your codebase is a *strong assurance that your agent is actually successfully completing the tasks you
give it*, and not just assuming that it is.

SMT solvers and proof assistants are now easier and cheaper to integrate into your work, with the added
benefit of your agents wasting less time chasing things that will never work. Start where the leverage is
highest: [TLA+](https://lamport.azurewebsites.net/tla/tla.html) and [Alloy](https://alloytools.org/) for
checking that a design holds before anyone writes it, and [Z3](https://microsoft.github.io/z3guide/) for
the constraints buried inside the code your agents are already producing.

### Testing in real environments

You must give your agents the ability to deploy infrastructure somewhere safe to test that it will actually
work. Your app is useless until it is deployed, and cannot be fully verified until the observable behaviour
specified in your user stories can be tested in a real end to end test. This is the final proof that the
agent actually made what you want.

### Machine, review thyself

Agents are better at code review than you are. Let them do it, and let them use the evidence from formal
methods, real deployments, and end-to-end tests to give them the best shot at doing a good job. Give them
standards and bars and make them adversarial to each other.

## You, 2 years in the future

The last couple of years were hard, but you're in a good place now. You've just come off a call with Sarah,
one of your customers, about an issue she's having with your systems. It's not the first time you've heard
it, and over a few days you've had time to come up with a good general solution.

You take your draft notes from your notebook and take a picture, with some short instructions to turn this
into a ticket. By the time you're sat at your desk, there's a draft ready to review, with notes pulled in
from your recent discussions about this. You check that you agree with the writeup. There are a few open
questions about the problem. You talk to another engineer, Rob, and together you sit down with the problem
and hammer out the last few kinks.

Once you're happy with the draft, you dispatch it, and go to get some lunch.

One overpriced sandwich later, your phone buzzes - the prototype behaviour is ready. You sit back down at
your workstation and try out the prototype. You leave a few notes. A few minutes later, an updated
prototype is ready, and it's good to go.

You ping Sarah a link - "can you tell me what you think of this?".

Sarah has some notes; that's fine. You adjust the prototype one more time, ping it back, and Sarah responds
with a rocket ship emoji.

You approve the prototype.

A couple of hours later, it's running in production. A couple days later, you get a note from Sarah thanking
you for prioritizing this issue, and that her team is very happy with the changes.

## What it takes to get there

Honestly - not much that's *new*. Almost every tool above already exists and most of them are older than
you are; what changes is who they're pointed at. What you need to be doing right now is mapping out your
personal working process and figuring out how you can bust every bottleneck.

It's a better time than ever to read [The Phoenix Project](https://itrevolution.com/product/the-phoenix-project/).
I wrote about pointing it at agents in [The Phoenix Reborn](https://sourceless.org/posts/the-phoenix-reborn.html).
