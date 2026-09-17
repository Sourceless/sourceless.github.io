---
layout: post
title: "Infrastructure as Data"
date: 2026-09-17
tags: [infrastructure, terraform, devops, sre, formal methods, datalog, talks]
summary: "A talk about treating infrastructure state as queryable facts rather than an opaque JSON blob, so you can search it, simulate changes against it, and have a solver work out a safe ordering before anything is applied."
---

This is the talk I gave on infrastructure as data: the slides, and what I said over each
one. The idea is that if you treat infrastructure as data, you can test things that don't
exist yet.

The code is at [github.com/Sourceless/infratomic](https://github.com/Sourceless/infratomic).
There's a [glossary](#glossary) at the end for the terms that get used in passing.

## The gap

<figure class="slide">
  <img src="{{ '/assets/talks/infrastructure-as-data/slide-02.png' | relative_url }}" alt="Two pyramids on a shared six-row grid. Software fills all six rows: type checks, property-based tests, unit tests, integration tests, e2e test in non-prod, e2e test in prod. Infrastructure has only plan at the bottom, then one enormous dashed box marked ????, then prod-like deployment and prod deployment." loading="lazy">
</figure>

In software we get plenty of chances to exercise our code before production. In
infrastructure we hope we've got a decent pre-prod, and the plan is worthless beyond
listing the API calls it'll make.

## Where state lives

<figure class="slide">
  <img src="{{ '/assets/talks/infrastructure-as-data/slide-03.png' | relative_url }}" alt="Five state backends - S3, GCS, Azure Blob, Postgres, local file - all funnelling into one opaque JSON blob. Postgres is flagged: one row per workspace, state in a text column." loading="lazy">
</figure>

Part of the reason is where state lives. It's a JSON blob, wherever you put it, even in the
Postgres backend, and there isn't a great deal you can do with a blob.

## Reality is bigger than the snapshot

<figure class="slide">
  <img src="{{ '/assets/talks/infrastructure-as-data/slide-04.png' | relative_url }}" alt="A field of small circles representing real resources, with four larger lassos drawn over them representing state snapshots. Two of the lassos overlap, and the three resources in the overlap are red. A few more red resources sit outside every lasso." loading="lazy">
</figure>

Each dot is a resource, and each circle is a state snapshot. Some are misconfigured, some
are managed in two places at once, and plenty aren't managed at all, which never really
goes away.

## Take the blob apart

<figure class="slide">
  <img src="{{ '/assets/talks/infrastructure-as-data/slide-05.png' | relative_url }}" alt="The state blob marked desired and a cylinder marked actual, both arrowing into one entity / attribute / value table. Rows read sg-0a91f3 :type security-group, sg-0a91f3 :vpc vpc-77c1, sg-0a91f3 :direction in, sg-0a91f3 :port 22, sg-0a91f3 :range 0.0.0.0/0, vpc-77c1 :type vpc." loading="lazy">
</figure>

We can start to fix this by storing both the desired state and the actual state somewhere
easy to query, like a database, where every resource is an entity and every attribute and
relationship is a fact.

## What kind of database

<figure class="slide">
  <img src="{{ '/assets/talks/infrastructure-as-data/slide-06.png' | relative_url }}" alt="Four cards. Append only: keep all of history. Graph: have relationships we can follow. Temporal: look into the past. Speculative: look into the future." loading="lazy">
</figure>

It's append only, so we keep the history and can audit it. It's a graph, so we can follow
relationships. It's temporal, so we can look back. It's speculative, so we can try things
before committing.

## The architecture

<figure class="slide">
  <img src="{{ '/assets/talks/infrastructure-as-data/slide-07.png' | relative_url }}" alt="A CLI feeding a custom state backend, which talks to Terraform, which talks to the cloud provider. The custom state backend writes into a state database, which is also fed by a state sync worker reading from the cloud provider." loading="lazy">
</figure>

A sample architecture. Terraform still makes every change, its state lives in a database,
and a worker syncs the cloud's view in. The CLI in front is where we run our own checks.
I've got four.

## Question 1: are there dangerous rules?

<figure class="slide">
  <img src="{{ '/assets/talks/infrastructure-as-data/slide-08.png' | relative_url }}" alt="A Datalog query finding rule ids where direction is In, port is 22, and the range is not private. Beside it a table of four rules; row 2 (port 22, 0.0.0.0/0) and row 4 (port 22, 10.0.0.0/6) are flagged in red." loading="lazy">
</figure>

So, some problems we can solve now. First, searching our infrastructure for dangerous
rules. A toy example, looking for firewall rules that let an attacker straight in. Row four
is the sneaky one.

<figure class="slide">
  <img src="{{ '/assets/talks/infrastructure-as-data/slide-09.png' | relative_url }}" alt="A proposed change adding an ingress rule for port 22 from 0.0.0.0/0, written into a draft state alongside the existing rules, where the new row is flagged red, and the change is rejected." loading="lazy">
</figure>

If we can detect a problem, we can also prevent it. Take the proposed change, write it into
a draft state, and run the same check statically against that, before anything is applied.

## Question 2: what will this change?

<figure class="slide">
  <img src="{{ '/assets/talks/infrastructure-as-data/slide-10.png' | relative_url }}" alt="Ten roles attached to a policy before an apply, one after, with terraform reporting 1 added, 0 changed, 0 destroyed underneath." loading="lazy">
</figure>

There's a fun terraform feature called authoritative resources, which can quietly destroy
or change things you didn't intend to. Plan looks fine, apply looks fine, and then the
alarms go off. How do we catch it?

<figure class="slide">
  <img src="{{ '/assets/talks/infrastructure-as-data/slide-11.png' | relative_url }}" alt="A proposed policy attachment written into a draft state, showing one role kept and nine marked for removal, and the change rejected with 9 removed." loading="lazy">
</figure>

Because we have the cloud state too, we can pull the same trick again. We know how
authoritative resources behave, so we can simulate the apply and see the blast radius, nine
roles in this case.

## Question 3: why can't these two talk?

<figure class="slide">
  <img src="{{ '/assets/talks/infrastructure-as-data/slide-12.png' | relative_url }}" alt="A tree of two VPCs with subnets beneath and a node under each. A green path climbs from the left-hand node up to its VPC and stops at a red cross on the peering. Caption: no route across the peering." loading="lazy">
</figure>

Here's one I'm sure a lot of us have burned time on. It looks easy drawn out like this. In
reality it's reachability analyzers, route tables and security group rules. With a graph,
it's a search problem.

<figure class="slide">
  <img src="{{ '/assets/talks/infrastructure-as-data/slide-13.png' | relative_url }}" alt="A spec reading choose routes to add, require reachable(a, b), minimise how many, fed into a first-order logic solver, which outputs one route across the peering. The same tree beneath now has a complete green path." loading="lazy">
</figure>

And with some ancient technology from the 1970s, we can ask a more useful question. What do
I need to change to make these two talk to each other? One route, it turns out.

## Question 4: will this deploy cause downtime?

<figure class="slide">
  <img src="{{ '/assets/talks/infrastructure-as-data/slide-14.png' | relative_url }}" alt="Traffic into a load balancer with an edge to v1, which is serving, and a dashed v2 that doesn't exist yet. Beneath: invariant - at least one instance is always serving." loading="lazy">
</figure>

A common job for us is a zero downtime deploy, so here's a toy example. We want to get v2
of this service serving traffic without ever dropping any of it.

<figure class="slide">
  <img src="{{ '/assets/talks/infrastructure-as-data/slide-15.png' | relative_url }}" alt="A filmstrip of the system after each step of a bad ordering: deregister v1 (serving 0), stop v1 (serving 0), start v2 (serving 0), register v2 (serving 1). Caption: nothing is serving." loading="lazy">
</figure>

This is an example of how not to do it. Deregister, stop, start, register, and for three
steps nothing is serving. There are twenty three wrong ways to do this.

<figure class="slide">
  <img src="{{ '/assets/talks/infrastructure-as-data/slide-16.png' | relative_url }}" alt="The start state with v1 registered and v2 absent, the end state with v2 registered and v1 absent, and the invariant serving >= 1, all fed into a first-order logic solver." loading="lazy">
</figure>

We know where we want to start and where we want to end up, and we know that something
always has to be serving. That's everything the solver needs.

<figure class="slide">
  <img src="{{ '/assets/talks/infrastructure-as-data/slide-17.png' | relative_url }}" alt="A permutation tree. Four first actions branch from the root: start v2 is green, register v2, deregister v1 and stop v1 are each crossed out in red. A green path runs from start v2 to a leaf. To the right: 24 orderings, 1 survives." loading="lazy">
</figure>

The solver is more ancient technology that searches this space efficiently. It works
through the orderings, throws out the ones that break the rule, and in this case there's
one left.

<figure class="slide">
  <img src="{{ '/assets/talks/infrastructure-as-data/slide-18.png' | relative_url }}" alt="Five states of the system in a row with the four moves labelled between them - start v2, register v2, deregister v1, stop v1 - and serving counts of 1, 1, 2, 1, 1 underneath. Caption: the rule holds at every one." loading="lazy">
</figure>

So now we have something that can make a change without breaking things, or tell us that
what we've asked for is impossible. It's a toy example, but this approach scales.

## The gap, filled

<figure class="slide">
  <img src="{{ '/assets/talks/infrastructure-as-data/slide-19.png' | relative_url }}" alt="The two pyramids from the start again. The infrastructure side's dashed ???? has been replaced by three green layers: static property checks, simulate changes, and temporal behaviour modeling." loading="lazy">
</figure>

So here's my proposal. None of this is new, and we deserve tools that stop us making
mistakes that were always avoidable. We just have to start treating infrastructure as data.

The code is on GitHub at [Sourceless/infratomic](https://github.com/Sourceless/infratomic).

## Glossary
{: #glossary}

**append-only** - a store where facts are added and never overwritten, so the whole history
stays available.

**authoritative resource** - an IaC resource that claims exclusive ownership of a set of
things, so creating it removes anything in that set it doesn't declare.
`aws_iam_policy_attachment` is the example used here.

**blast radius** - everything a change actually affects, as opposed to what it was meant to
affect.

**CIDR block** - a range of IP addresses written as an address and a prefix length. A
smaller prefix means a larger range: `10.0.0.0/8` is private, while `10.0.0.0/6` spans
8.0.0.0 to 11.255.255.255 and is not.

**constraint solver** - a program that takes a set of logical constraints and either finds
something satisfying all of them or proves nothing does.

**Datalog** - a declarative query language based on logic, good at recursive queries over
relations. Late 1970s.

**draft state** - a speculative copy of the model with a proposed change applied, used for
checking and then thrown away.

**entity, attribute, value** - the shape of a single fact: which thing, which property,
what it is set to.

**first-order logic** - the logic of predicates, variables and quantifiers, and the basis
of the solvers used here.

**IaC** - infrastructure as code. Defining infrastructure in files that a tool applies,
rather than by hand.

**ingress rule** - a firewall rule permitting inbound traffic to a resource, on some port,
from some address range.

**invariant** - a property that has to hold in every state, not only at the start and the
end.

**peering** - a connection joining two VPCs so resources in them can route to each other.

**plan and apply** - terraform's two phases. Work out which API calls to make, then make
them.

**reachability** - whether traffic can get from one resource to another given everything in
between. A transitive question about a graph.

**route table** - the rules deciding where traffic leaving a subnet is sent.

**security group** - a stateful firewall attached to resources, made up of ingress and
egress rules.

**speculative transaction** - a write to the database that is never committed, so the
result can be queried and then discarded.

**state** - terraform's record of the resources it manages and their attributes.

**state backend** - where terraform keeps that state (S3, GCS, Azure Blob, Postgres, a
local file) and the interface it uses to do so.

**subnet** - a slice of a VPC's address range, with its own routing.

**temporal database** - one that records when each fact was true, so earlier states can be
queried.

**VPC** - an isolated virtual network inside a cloud account, containing subnets.

**zero downtime deploy** - replacing a running version with a new one without any interval
where nothing is serving.
