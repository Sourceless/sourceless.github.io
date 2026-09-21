---
layout: post
title: "Infrastructure as Data"
date: 2026-09-17
tags: [infrastructure, terraform, devops, sre, formal methods, datalog, talks]
summary: "If you treat infrastructure as data, you can test things that don't exist yet. The slides and transcript from my DevOpsDays London 2026 talk."
---

I gave this talk at DevOpsDays London 2026.

<div class="video">
  <iframe src="https://www.youtube-nocookie.com/embed/KBIPkWFv8P4" title="Infrastructure as Data, DevOpsDays London 2026" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen loading="lazy"></iframe>
</div>

<figure class="slide">
  <img src="{{ '/assets/talks/infrastructure-as-data/slide-01.png' | relative_url }}" alt="Title slide. Infrastructure as Data. Laurence Pakenham-Smith, Director, SRE, Kevel." loading="lazy">
</figure>

I'm Laurence, I run SRE at Kevel. The idea I want to talk to you about today is that if you
treat infrastructure as data, you can test things that don't exist yet.

<figure class="slide">
  <img src="{{ '/assets/talks/infrastructure-as-data/slide-02.png' | relative_url }}" alt="Two pyramids on a shared six-row grid. Software fills all six rows: type checks, property-based tests, unit tests, integration tests, e2e test in non-prod, e2e test in prod. Infrastructure has only plan at the bottom, then one enormous dashed box marked ????, then prod-like deployment and prod deployment." loading="lazy">
</figure>

In software we get plenty of chances to exercise our code before production. In
infrastructure we hope we've got a decent pre-prod, and the plan is worthless beyond
listing the API calls it'll make.

<figure class="slide">
  <img src="{{ '/assets/talks/infrastructure-as-data/slide-03.png' | relative_url }}" alt="Five state backends - S3, GCS, Azure Blob, Postgres, local file - all funnelling into one opaque JSON blob. Postgres is flagged: one row per workspace, state in a text column." loading="lazy">
</figure>

Part of the reason is where state lives. It's a JSON blob, wherever you put it, even in the
Postgres backend, and there isn't a great deal you can do with a blob.

<figure class="slide">
  <img src="{{ '/assets/talks/infrastructure-as-data/slide-04.png' | relative_url }}" alt="A field of small circles representing real resources, with four larger lassos drawn over them representing state snapshots. Two of the lassos overlap, and the three resources in the overlap are red. A few more red resources sit outside every lasso." loading="lazy">
</figure>

Each dot is a resource, and each circle is a state snapshot. Some are misconfigured, some
are managed in two places at once, and plenty aren't managed at all, which never really
goes away.

<figure class="slide">
  <img src="{{ '/assets/talks/infrastructure-as-data/slide-05.png' | relative_url }}" alt="The state blob marked desired and a cylinder marked actual, both arrowing into one entity / attribute / value table. Rows read sg-0a91f3 :type security-group, sg-0a91f3 :vpc vpc-77c1, sg-0a91f3 :direction in, sg-0a91f3 :port 22, sg-0a91f3 :range 0.0.0.0/0, vpc-77c1 :type vpc." loading="lazy">
</figure>

We can start to fix this by storing both the desired state and the actual state somewhere
easy to query, like a database, where every resource is an entity and every attribute and
relationship is a fact.

<figure class="slide">
  <img src="{{ '/assets/talks/infrastructure-as-data/slide-06.png' | relative_url }}" alt="Four cards. Append only: keep all of history. Graph: have relationships we can follow. Temporal: look into the past. Speculative: look into the future." loading="lazy">
</figure>

It's append only, so we keep the history and can audit it. It's a graph, so we can follow
relationships. It's temporal, so we can look back. It's speculative, so we can try things
before committing.

<figure class="slide">
  <img src="{{ '/assets/talks/infrastructure-as-data/slide-07.png' | relative_url }}" alt="A CLI feeding a custom state backend, which talks to Terraform, which talks to the cloud provider. The custom state backend writes into a state database, which is also fed by a state sync worker reading from the cloud provider." loading="lazy">
</figure>

A sample architecture. Terraform still makes every change, its state lives in a database,
and a worker syncs the cloud's view in. The CLI in front is where we run our own checks.
I've got four.

<figure class="slide">
  <img src="{{ '/assets/talks/infrastructure-as-data/slide-08.png' | relative_url }}" alt="Question 1: are there dangerous rules? A Datalog query finding rule ids where direction is In, port is 22, and the range is not private. Beside it a table of four rules; row 2 (port 22, 0.0.0.0/0) and row 4 (port 22, 10.0.0.0/6) are flagged in red." loading="lazy">
</figure>

So, some problems we can solve now. First, searching our infrastructure for dangerous
rules. A toy example, looking for firewall rules that let an attacker straight in. Row four
is the sneaky one.

<figure class="slide">
  <img src="{{ '/assets/talks/infrastructure-as-data/slide-09.png' | relative_url }}" alt="Preventing dangerous states. A proposed change adding an ingress rule for port 22 from 0.0.0.0/0, written into a draft state alongside the existing rules, where the new row is flagged red, and the change is rejected." loading="lazy">
</figure>

If we can detect a problem, we can also prevent it. Take the proposed change, write it into
a draft state, and run the same check statically against that, before anything is applied.

<figure class="slide">
  <img src="{{ '/assets/talks/infrastructure-as-data/slide-10.png' | relative_url }}" alt="Question 2: what will this change? Ten roles attached to a policy before an apply, one after, with terraform reporting 1 added, 0 changed, 0 destroyed underneath." loading="lazy">
</figure>

There's a fun terraform feature called authoritative resources, which can quietly destroy
or change things you didn't intend to. Plan looks fine, apply looks fine, and then the
alarms go off. How do we catch it?

<figure class="slide">
  <img src="{{ '/assets/talks/infrastructure-as-data/slide-11.png' | relative_url }}" alt="Simulating the change. A proposed policy attachment written into a draft state, showing one role kept and nine marked for removal, and the change rejected with 9 removed." loading="lazy">
</figure>

Because we have the cloud state too, we can pull the same trick again. We know how
authoritative resources behave, so we can simulate the apply and see the blast radius, nine
roles in this case.

<figure class="slide">
  <img src="{{ '/assets/talks/infrastructure-as-data/slide-12.png' | relative_url }}" alt="Question 3: why can't these two talk? A tree of two VPCs with subnets beneath and a node under each. A green path climbs from the left-hand node up to its VPC and stops at a red cross on the peering. Caption: no route across the peering." loading="lazy">
</figure>

Here's one I'm sure a lot of us have burned time on. It looks easy drawn out like this. In
reality it's reachability analyzers, route tables and security group rules. With a graph,
it's a search problem.

<figure class="slide">
  <img src="{{ '/assets/talks/infrastructure-as-data/slide-13.png' | relative_url }}" alt="Generating the fix. A spec reading choose routes to add, require reachable(a, b), minimise how many, fed into a first-order logic solver, which outputs one route across the peering. The same tree beneath now has a complete green path." loading="lazy">
</figure>

And with some ancient technology from the 1970s, we can ask a more useful question. What do
I need to change to make these two talk to each other? One route, it turns out.

<figure class="slide">
  <img src="{{ '/assets/talks/infrastructure-as-data/slide-14.png' | relative_url }}" alt="Question 4: will this deploy cause downtime? Traffic into a load balancer with an edge to v1, which is serving, and a dashed v2 that doesn't exist yet. Beneath: invariant - at least one instance is always serving." loading="lazy">
</figure>

A common job for us is a zero downtime deploy, so here's a toy example. We want to get v2
of this service serving traffic without ever dropping any of it.

<figure class="slide">
  <img src="{{ '/assets/talks/infrastructure-as-data/slide-15.png' | relative_url }}" alt="A bad ordering. A filmstrip of the system after each step: deregister v1 (serving 0), stop v1 (serving 0), start v2 (serving 0), register v2 (serving 1). Caption: nothing is serving." loading="lazy">
</figure>

This is an example of how not to do it. Deregister, stop, start, register, and for three
steps nothing is serving. There are twenty three wrong ways to do this.

<figure class="slide">
  <img src="{{ '/assets/talks/infrastructure-as-data/slide-16.png' | relative_url }}" alt="Hand it to a solver. The start state with v1 registered and v2 absent, the end state with v2 registered and v1 absent, and the invariant serving >= 1, all fed into a first-order logic solver." loading="lazy">
</figure>

We know where we want to start and where we want to end up, and we know that something
always has to be serving. That's everything the solver needs.

<figure class="slide">
  <img src="{{ '/assets/talks/infrastructure-as-data/slide-17.png' | relative_url }}" alt="It tries every ordering. A permutation tree. Four first actions branch from the root: start v2 is green, register v2, deregister v1 and stop v1 are each crossed out in red. A green path runs from start v2 to a leaf. To the right: 24 orderings, 1 survives." loading="lazy">
</figure>

The solver is more ancient technology that searches this space efficiently. It works
through the orderings, throws out the ones that break the rule, and in this case there's
one left.

<figure class="slide">
  <img src="{{ '/assets/talks/infrastructure-as-data/slide-18.png' | relative_url }}" alt="The output is a sequence of states. Five states of the system in a row with the four moves labelled between them - start v2, register v2, deregister v1, stop v1 - and serving counts of 1, 1, 2, 1, 1 underneath. Caption: the rule holds at every one." loading="lazy">
</figure>

So now we have something that can make a change without breaking things, or tell us that
what we've asked for is impossible. It's a toy example, but this approach scales.

<figure class="slide">
  <img src="{{ '/assets/talks/infrastructure-as-data/slide-19.png' | relative_url }}" alt="The two pyramids from the start again. The infrastructure side's dashed ???? has been replaced by three green layers: static property checks, simulate changes, and temporal behaviour modeling." loading="lazy">
</figure>

So here's my proposal. None of this is new, and we deserve tools that stop us making
mistakes that were always avoidable. We just have to start treating infrastructure as data.

<figure class="slide">
  <img src="{{ '/assets/talks/infrastructure-as-data/slide-20.png' | relative_url }}" alt="Two links. github.com/Sourceless/infratomic, marked code. sourceless.org, marked slides and transcript." loading="lazy">
</figure>

Thank you for listening. I'm working on this problem in the open, the code is
[on GitHub](https://github.com/Sourceless/infratomic), and these slides and the transcript
are on my website.
