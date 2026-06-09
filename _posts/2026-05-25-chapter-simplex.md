---
title: "Chapter: Simplex"
date: 2026-05-25 04:00:00 -05:00
tags:
- consensus
author: Ittai Abraham
---

This post is a map of the
[Simplex](https://eprint.iacr.org/2023/463)
line of posts on Decentralized Thoughts. It is meant to be read as a chapter:
first the core Simplex idea, then some of the main ways to vary it.

A salient property of Simplex is that parties leave a view
only with a value certificate or a skip certificate. This is in contrast to
protocols like PBFT, HotStuff, Casper, and Tendermint, where a view may end
without an explicit certificate for that view.

This insistence on explicit certificates for values and for skipped views
gives a $3\delta$ good-case at $n=3f+1$ with a worst-case view latency of
$3\Delta+\delta$. From there, the Simplex family splits along several axes:
same resilience but better worst-case view latency, more validators for a two
round good-case, fixed view schedules, and variants that control certificate
growth.

## The Core Simplex Idea

If you are familiar with Tendermint, then
[from Tendermint to Simplex](https://decentralizedthoughts.github.io/2025-06-18-simplex/)
is the best entry point.
That post starts from a Tendermint style protocol and changes it into Simplex.
The important change is having either a value certificate or a skip certificate for view $v$ and using the fact that a skip certificate for view $v$ proves that no decision certificate can form in that view. 

This is what removes the Tendermint leader wait. In Tendermint, a leader waits
because some party may hold a hidden lock from the previous view. In Simplex, a proposal can instead include a value certificate from the highest relevant view and skip certificates for the intervening views. A party that verifies those
certificates can vote without waiting for the leader to collect every hidden
lock.

The original sources around this point are:

* [Simplex Consensus](https://simplex.blog/), Ben Chan and Rafael Pass's
  presentation of the protocol.
* [Simplex Consensus: A Simple and Fast Consensus Protocol](https://eprint.iacr.org/2023/463),
  the paper.
* [Sing a Song of Simplex](https://eprint.iacr.org/2023/1916), Victor Shoup's
  follow up with DispersedSimplex, stable leaders, and implementation
  optimizations.
* [Commonware's Simplex module](https://docs.rs/commonware-consensus/latest/commonware_consensus/simplex/index.html),
  an implementation oriented reference.

Two later DT posts give a second path into the same protocol:
[Benign Simplex](https://decentralizedthoughts.github.io/2025-11-08-benign-simplex/)
and
[From Benign Simplex to Byzantine Simplex](https://decentralizedthoughts.github.io/2025-11-15-simplex-from-benign/).
The benign post isolates the explicit `NoVote` message under omission
failures: if enough parties report that they did not see a value in a view,
then parties can skip that view. The Byzantine post turns this into signed
bottom votes, Byzantine quorum intersection, external validity, and the exact
Simplex skip property:

> if a view has $n-f$ bottom votes, then no decision certificate can form in
> that view.

This pair is useful because it makes the authenticated Simplex proof feel like
a small change to a simpler omission failure protocol.

The benign presentation also connects Simplex to earlier DT posts on
[Benign HotStuff](https://decentralizedthoughts.github.io/2021-04-02-benign-hotstuff/),
[Chained Raft](https://decentralizedthoughts.github.io/2021-07-17-simplifying-raft-with-chaining/),
and
[Log Paxos](https://decentralizedthoughts.github.io/2021-09-30-distributed-consensus-made-simple-for-real-this-time/).
Those posts are not Simplex variants, but they explain the rotating leader and
chain based viewpoint behind the benign construction.

## The Modular View

[Deconstructing Simplex](https://decentralizedthoughts.github.io/2026-04-23-deconstructing-simplex/)
turns the protocol into two pieces:

1. an outer proposal rule that says when a proposal is valid based on previous value certificates and skip certificates;
2. an inner Certifying Graded Broadcast (CGB) instance that produces a regular
   certificate, a strong certificate, or a skip certificate for each view.

We will use this decomposition in the rest of the chapter. Many Simplex
variants leave the outer proposal rule essentially unchanged and replace the inner
certificate structure. 

The same decomposition also explains how to move from single-shot Simplex to a
chained protocol.
[From Single-Shot Simplex to Chained Simplex](https://decentralizedthoughts.github.io/2026-05-20-from-single-shot-to-chained/)
shows how to run the Simplex logic as a state machine replication protocol,
where each decided block extends a previous decided prefix. The construction can be applied to Simplex variants that keep the same outer proposal
structure and the same inner certificate properties. This is the bridge from the
single-shot protocols in the chapter to blockchain style executions with a
growing chain of blocks.

The decomposition post also explains the relationship with the earlier DT post
on
[PBFT via Locked Broadcast and Recover Max Lock](https://decentralizedthoughts.github.io/2022-11-20-pbft-via-locked-braodcast/).
PBFT style protocols prove safety by collecting enough locks. Simplex proves
safety by showing skip certificates for the views that might otherwise hide a
decision. The inner CGB building block is also close
in spirit to authenticated
[Reliable Broadcast](https://decentralizedthoughts.github.io/2020-09-19-living-with-asynchrony-brachas-reliable-broadcast/)
with external validity, in the framework of
[Cachin, Kursawe, Petzold, and Shoup](https://www.iacr.org/archive/crypto2001/21390524.pdf).

## Better Worst-Case View Latency at $3f+1$

The first direction keeps the same authenticated $n=3f+1$ setting and tries to
reduce worst case view latency.

[C-Simplex and Kuplex](https://decentralizedthoughts.github.io/2025-09-24-Kuplex/)
contains two variants:

* **C-Simplex** improves silent views. If the leader is silent, parties can
  send a bottom final message after $2\Delta$, so the silent view ends within
  $2\Delta+\delta$. The worst case view latency remains $3\Delta+\delta$.
* **Kuplex** improves the worst case view latency when the actual delay
  $\delta$ is much smaller than the timeout parameter $\Delta$. It uses an
  early negative vote and a second value vote, obtaining worst case view
  latency $2\Delta+2\delta$ and silent view latency $2\Delta+\delta$.

These protocols are best understood as local changes to the Simplex inner protocol.

This section is also where [Kudzu](https://arxiv.org/abs/2505.08771) enters
the picture. Kudzu is designed around a fast path and high throughput. The
Kuplex post extracts the $3f+1$ view latency aspect into a Simplex style
variant.

[Information-Theoretic Kuplex](https://decentralizedthoughts.github.io/2026-06-05-IT-Kuplex/)
takes this same view-latency direction without signatures. Quorums are no
longer transferable certificates, so parties act only on messages they receive
directly. The post uses aged quorums to recover a one-$\Delta$ view entrance
gap after GST, obtaining robust $3\delta$ good-case latency, worst-case view
latency $3\Delta+2\delta$ at $n=3f+1$, and $3\Delta+\delta$ at $n=4f+1$.

## Two Round Good Case With More Validators

The second direction asks for a different improvement: can an honest leader
decide after one proposal and one vote round?

At optimal resilience, the answer is no. The post
[Why BFT Needs Three Rounds](https://decentralizedthoughts.github.io/2025-11-22-three-round-BFT/)
explains the lower bound: for $n\leq 5f-2$, Byzantine broadcast in partial
synchrony needs at least three rounds in the good case. This is why PBFT,
Tendermint, Casper FFG, HotStuff, and Simplex all have the familiar proposal
plus two voting rounds at $n=3f+1$.

The way around the lower bound is to use more validators.

[2-round BFT in Simplex style](https://decentralizedthoughts.github.io/2025-07-18-two-round-Simplex/)
gives the clean $n=5f+1$ version. A decision requires $n-f$ votes for one
value. A small value certificate has size $n-3f$. If a party sees $n-f$ votes
but no small value certificate, that collection proves that no decision
certificate formed in the view; it can be used to produce a no commit (skip) certificate for that view.

This is the same Simplex idea with different thresholds. The proposal rule
still uses the highest previous value certificate and skip certificates for
the intervening views. What changes is the per-view certificate arithmetic.

The two round Simplex post also places the result in the older fast BFT line:
[FaB Paxos](https://www.cs.cornell.edu/lorenzo/papers/fab.pdf),
[Kursawe's optimistic Byzantine agreement](https://research.ibm.com/publications/optimistic-byzantine-agreement),
[Zyzzyva](https://cacm.acm.org/research/zyzzyva-speculative-byzantine-fault-tolerance/),
and later fixes such as
[SBFT](https://arxiv.org/abs/1804.01626). It also points to current Simplex
like systems, including
[Minimmit](https://commonware.xyz/blogs/minimmit),
the [Minimmit paper](https://arxiv.org/abs/2508.10862),
[ChonkyBFT](https://arxiv.org/abs/2503.15380), and
[Tempo's Minimmit post](https://dankradfeist.de/tempo/2025/12/31/minimmit-simple-fast-consensus.html).

The next step is to combine the two round and three round paths.
[Concurrent 2-round and 3-round Simplex-style BFT](https://decentralizedthoughts.github.io/2025-07-29-2-round-3-round-simplex/)
uses $n=3f+2p+1$. It keeps safety and liveness for $f$ Byzantine faults, gives
a three round good case with $f$ Byzantine faults, and gives a two round good
case when the execution has at most $p$ Byzantine faults. The key point is to
order certificates first by view and then by fast before slow, and to complete
each view with both the fast and slow certificates.

The follow-up
[2-round BFT in Simplex style for $n=5f-1$](https://decentralizedthoughts.github.io/2025-08-06-5fminus1-simplex/)
tightens the $5f+1$ threshold to $5f-1$. The trick is to treat leader
equivocation as a separate case. If the leader does not equivocate, a special
certificate combines votes for $x$ and votes for $\bot$. If the leader does
equivocate, parties ignore the leader's own vote and use only non-leader votes.
The same idea extends the concurrent protocol to $n=3f+2p-1$.

Other protocols in this neighborhood include
[Banyan](https://arxiv.org/abs/2312.05869),
[Kudzu](https://arxiv.org/abs/2505.08771),
[Alpenglow](https://www.anza.xyz/blog/alpenglow-a-new-consensus-for-solana),
and
[Hydrangea](https://eprint.iacr.org/2025/1112). They make different choices
about fast paths, fallback paths, leader equivocation, data dissemination, and
mixed Byzantine and crash faults. The Simplex style posts are useful because
they isolate the quorum arithmetic in a very small protocol.

### Granular Synchrony

The post
[Concurrent 2-round and 3-round BFT protocols under granular synchrony](https://decentralizedthoughts.github.io/2026-01-24-two-round-ps/)
belongs with the two round line. It asks how much timing structure is needed
to get the $n=3f+2p+1$ numbers when the leader may equivocate.

Under plain partial synchrony, the protocol must sometimes wait for $n-f$
votes to know that a fast commit did not happen. If the leader cannot
equivocate, or if granular synchrony bounds how many honest messages can be
late to each recipient, then the protocol can wait for fewer votes and still
infer that a fast certificate would have appeared. This gives another way to
understand the relationship among the Simplex style concurrent protocol,
Alpenglow, and Hydrangea.

## Fixed View Schedules

The fixed view schedule direction starts with a different question. Modern
systems often have good clocks, and fixed view boundaries are operationally
attractive. Can Simplex run with predetermined view start times instead of
event driven view advancement?

[Synchronized Clocks, Fixed View Schedules, and Simultaneous Agreement](https://decentralizedthoughts.github.io/2026-03-07-simultaneous-agreement/)
overviews the advantages and disadvantages of having a fixed view schedule.

[Simplex on a Fixed View Schedule](https://decentralizedthoughts.github.io/2026-05-14-simplex-FVS/)
shows how Simplex can be put on a fixed view schedule with view length
$3\Delta$. A new catch up
claim says that after GST, every previous view eventually yields either a
value certificate or a skip certificate.

[Fast Simplex on a Fixed View Schedule](https://decentralizedthoughts.github.io/2026-05-17-fast-simplex-fvs/)
pushes this fixed view schedule line through the two round Simplex certificate
structure. It uses $n=5f+1$ and view length $2\Delta$. 

## Harsh Partial Synchrony and Complex

The post
[Partial Synchrony variants](https://decentralizedthoughts.github.io/2025-12-19-cc-under-harsh-ps/)
explains a subtle cost of Simplex. In bounded partial synchrony, messages sent
before GST are delayed but eventually arrive by $GST+\Delta$. In unbounded or
lossy partial synchrony, old skip certificates may be delayed for an unbounded
time or lost. This matters because a Simplex proposal may need skip
certificates for many intervening views.

That model distinction connects directly to
[From Simplex to Complex](https://decentralizedthoughts.github.io/2026-04-26-complex/).
Simplex has better worst case view latency than Tendermint, but it may need a
growing number of certificates in a proposal. Tendermint keeps certificate
state bounded, but pays an extra wait. Complex is the middle point: it keeps
the Simplex view latency $3\Delta+\delta$ while requiring only a constant
number of certificates per view.

The way Complex does this is to keep the Simplex inner CGB and change the
outer proposal rule toward a Tendermint style lock rule. A proposal uses a
recent lock certificate, and if the lock is not from the immediately previous
view, it also includes a skip certificate for the previous view. This turns the
long Simplex list of intervening skips into a constant size check.


## Reading Map

For the core Simplex path, read:

* [From Tendermint to Simplex](https://decentralizedthoughts.github.io/2025-06-18-simplex/)
* [Benign HotStuff](https://decentralizedthoughts.github.io/2021-04-02-benign-hotstuff/)
* [Chained Raft](https://decentralizedthoughts.github.io/2021-07-17-simplifying-raft-with-chaining/)
* [Log Paxos](https://decentralizedthoughts.github.io/2021-09-30-distributed-consensus-made-simple-for-real-this-time/)
* [Benign Simplex](https://decentralizedthoughts.github.io/2025-11-08-benign-simplex/)
* [From Benign Simplex to Byzantine Simplex](https://decentralizedthoughts.github.io/2025-11-15-simplex-from-benign/)
* [Deconstructing Simplex](https://decentralizedthoughts.github.io/2026-04-23-deconstructing-simplex/)
* [From Single-Shot Simplex to Chained Simplex](https://decentralizedthoughts.github.io/2026-05-20-from-single-shot-to-chained/)

For background on partial synchrony BFT, read:

* [Key Principles Underlying Partial Synchrony BFT](https://decentralizedthoughts.github.io/2025-02-14-partial-synchrony-protocols/)
* [Practical Byzantine Fault Tolerant Consensus](https://decentralizedthoughts.github.io/2025-02-14-PBFT/)
* [The Lock-Commit Paradigm](https://decentralizedthoughts.github.io/2020-11-29-the-lock-commit-paradigm/)
* [PBFT via Locked Broadcast and Recover Max Lock](https://decentralizedthoughts.github.io/2022-11-20-pbft-via-locked-braodcast/)
* [Reliable Broadcast](https://decentralizedthoughts.github.io/2020-09-19-living-with-asynchrony-brachas-reliable-broadcast/)

For same resilience latency variants, read:

* [C-Simplex and Kuplex](https://decentralizedthoughts.github.io/2025-09-24-Kuplex/)
* [Information-Theoretic Kuplex](https://decentralizedthoughts.github.io/2026-06-05-IT-Kuplex/)

For two round good case variants, read:

* [2-round BFT in Simplex style](https://decentralizedthoughts.github.io/2025-07-18-two-round-Simplex/)
* [Concurrent 2-round and 3-round Simplex-style BFT](https://decentralizedthoughts.github.io/2025-07-29-2-round-3-round-simplex/)
* [2-round BFT in Simplex style for $n=5f-1$](https://decentralizedthoughts.github.io/2025-08-06-5fminus1-simplex/)
* [Why BFT Needs Three Rounds](https://decentralizedthoughts.github.io/2025-11-22-three-round-BFT/)
* [Concurrent 2-round and 3-round BFT protocols under granular synchrony](https://decentralizedthoughts.github.io/2026-01-24-two-round-ps/)

For fixed view schedules, read:

* [Synchronized Clocks, Fixed View Schedules, and Simultaneous Agreement](https://decentralizedthoughts.github.io/2026-03-07-simultaneous-agreement/)
* [Simplex on a Fixed View Schedule](https://decentralizedthoughts.github.io/2026-05-14-simplex-FVS/)
* [Fast Simplex on a Fixed View Schedule](https://decentralizedthoughts.github.io/2026-05-17-fast-simplex-fvs/)

For harsh partial synchrony and certificate growth, read:

* [Partial Synchrony variants](https://decentralizedthoughts.github.io/2025-12-19-cc-under-harsh-ps/)
* [From Simplex to Complex](https://decentralizedthoughts.github.io/2026-04-26-complex/)

For external Simplex and Simplex like resources, see:

* [Simplex Consensus](https://simplex.blog/)
* [Simplex Consensus paper](https://eprint.iacr.org/2023/463)
* [Sing a Song of Simplex](https://eprint.iacr.org/2023/1916)
* [Commonware Simplex](https://docs.rs/commonware-consensus/latest/commonware_consensus/simplex/index.html)
* [Tendermint](https://arxiv.org/abs/1807.04938)
* [DLS partial synchrony](https://groups.csail.mit.edu/tds/papers/Lynch/jacm88.pdf)
* [FaB Paxos](https://www.cs.cornell.edu/lorenzo/papers/fab.pdf)
* [Kursawe optimistic Byzantine agreement](https://research.ibm.com/publications/optimistic-byzantine-agreement)
* [Zyzzyva](https://cacm.acm.org/research/zyzzyva-speculative-byzantine-fault-tolerance/)
* [SBFT](https://arxiv.org/abs/1804.01626)
* [Banyan](https://arxiv.org/abs/2312.05869)
* [Kudzu](https://arxiv.org/abs/2505.08771)
* [Alpenglow](https://www.anza.xyz/blog/alpenglow-a-new-consensus-for-solana)
* [Minimmit](https://commonware.xyz/blogs/minimmit)
* [Minimmit paper](https://arxiv.org/abs/2508.10862)
* [ChonkyBFT](https://arxiv.org/abs/2503.15380)
* [Hydrangea](https://eprint.iacr.org/2025/1112)

## Acknowledgments

Thanks to Ling Ren, Kartik Nayak, Tim Roughgarden, Yuval Efron, Gilad Stern,
Neil Giridharan, Andrew Lewis-Pye, Joachim Neu, Ertem Nusret Tas, and Alejandro
Ranchal-Pedrosa for insightful discussions and feedback across the Simplex
series and beyond.

Your thoughts on X.
