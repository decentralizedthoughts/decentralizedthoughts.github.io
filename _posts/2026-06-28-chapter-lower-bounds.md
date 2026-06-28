---
title: "Chapter: Lower Bounds"
date: 2026-06-28 04:00:00 -05:00
tags:
- consensus
- lowerbound
author: Ittai Abraham
---

This post is a map of the lower-bound posts on Decentralized Thoughts.
The [Start Here](https://decentralizedthoughts.github.io/start-here/)
page already lists many of these results by topic, and the
[lowerbound tag](https://decentralizedthoughts.github.io/tags/#lowerbound)
lists the posts themselves. Here we turn that list into a chapter: first the
main fault-threshold barriers, then communication, round complexity, latency,
validity, privacy, and liveness.

In distributed computing, an upper bound is often a condition and a *protocol
for the honest parties*. Under that condition, the protocol lets the honest
parties satisfy the target property against any adversary. A useful way to
think about lower bounds is this:

> A lower bound is a condition and a *protocol for the adversary*. Under that
> condition, the protocol lets the adversary violate the target property of
> any honest-party protocol.

This symmetry is the beauty of lower bounds. They are not only abstract
statements about what is impossible; they often give an explicit adversarial
strategy. A proof is often a recipe: assume all but one of the desired
properties, then show that the adversary can break the last one.

## Fault Thresholds

The most basic question is how many faults a system can tolerate.

The first answer is the familiar majority barrier. In state machine
replication, a 50-50 split forces a choice: keep safety, or keep liveness, but
not both. This is the message of the
[CAP theorem for partial synchrony](https://decentralizedthoughts.github.io/2023-07-09-CAP-two-servers-in-psynch/).
The same majority barrier appears even in lock step synchrony with omission
faults:
[State Machine Replication for Two Servers and One Omission Failure is Impossible](https://decentralizedthoughts.github.io/2019-11-02-primary-backup-for-2-servers-and-omission-failures-is-impossible/).
The post
[In between Crash and Omission failures](https://decentralizedthoughts.github.io/2024-01-30-between-crash-and-omission/)
sharpens this picture by looking at weaker omission models.

There is also a permissionless version of the same obstruction:
[Blockchain Resource Pools and a CAP-esque Impossibility Result](https://decentralizedthoughts.github.io/2022-03-03-blockchain-resource-pools-and-a-cap-esque-impossibility-result/).
The language is different, but the adversary is again exploiting a split in
available resources.

The next barrier concerns Byzantine faults. In partial synchrony,
[Dwork, Lynch, and Stockmeyer](https://groups.csail.mit.edu/tds/papers/Lynch/jacm88.pdf)
showed that Byzantine agreement needs $n>3f$. The DT post
[Byzantine Agreement is impossible for $n\leq 3f$ under partial synchrony](https://decentralizedthoughts.github.io/2019-06-25-on-the-impossibility-of-byzantine-agreement-for-n-equals-3f-in-partial-synchrony/)
gives the split brain proof in blog form.

The unauthenticated version has the same threshold for a different reason, and
the lower bound holds even in synchrony.
The
[Fischer, Lynch, and Merritt](https://groups.csail.mit.edu/tds/papers/Lynch/FischerLynchMerritt-dc.pdf)
simulation lower bound says that without a PKI, or more generally when the
adversary can simulate parties, Byzantine agreement requires $n>3f$. See
[Byzantine Agreement is Impossible for $n\leq 3f$ if the Adversary can Simulate](https://decentralizedthoughts.github.io/2019-08-02-byzantine-agreement-is-impossible-for-%24n-slash-leq-3-f%24-is-the-adversary-can-easily-simulate/).
The same simulation idea can be strengthened to rule out even
[Crusader Agreement with $\leq 1/3$ Error](https://decentralizedthoughts.github.io/2021-10-04-crusader-agreement-with-dollars-slash-leq-1-slash-3%24-error-is-impossible-for-%24n-slash-leq-3f%24-if-the-adversary-can-simulate/)
at $n\leq 3f$.

Cryptographic or hardware restrictions can help, but only if they give the
right property. The post
[Neither Non-equivocation nor Transferability alone is enough](https://decentralizedthoughts.github.io/2021-06-14-neither-non-equivocation-nor-transferability-alone-is-enough-for-tolerating-minority-corruptions-in-asynchrony/)
explains why each property alone is insufficient for minority corruptions in
asynchrony. In a related direction, TEEs without persistent state do not escape
the Byzantine threshold in partial synchrony:
[$3f+1$ is needed in Partial Synchrony even against a Rollback adversary](https://decentralizedthoughts.github.io/2023-06-26-dls-meets-rollback/).

At a glance:

| Barrier | Adversary picture | What changes the conclusion |
|---|---|---|
| [CAP](https://decentralizedthoughts.github.io/2023-07-09-CAP-two-servers-in-psynch/) | split the replicas or resources into two plausible worlds | a non-faulty majority, or bounded timing assumptions |
| [Byzantine split brain](https://decentralizedthoughts.github.io/2019-06-25-on-the-impossibility-of-byzantine-agreement-for-n-equals-3f-in-partial-synchrony/) | split the honest parties into two sides, with Byzantine parties bridging the views | an honest $>2/3$ majority |
| [Unauthenticated Byzantine agreement](https://decentralizedthoughts.github.io/2019-08-02-byzantine-agreement-is-impossible-for-%24n-slash-leq-3-f%24-is-the-adversary-can-easily-simulate/) | simulate parties from another execution | non-simulatable identities, such as a PKI |
| [Non-equivocation or transferability alone](https://decentralizedthoughts.github.io/2021-06-14-neither-non-equivocation-nor-transferability-alone-is-enough-for-tolerating-minority-corruptions-in-asynchrony/) | give the protocol one property but not the other | a mechanism that provides both properties together |
| [Rollback attacks](https://decentralizedthoughts.github.io/2023-06-26-dls-meets-rollback/) | erase the memory that would have carried safety forward | persistent state, or the usual $3f+1$ threshold |

## Communication

The next question is how many messages agreement needs.

The classic answer is the
[Dolev-Reischuk](https://www.cs.huji.ac.il/~dolev/pubs/p132-dolev.pdf)
lower bound: deterministic Byzantine agreement needs quadratically many
messages in the worst case. The DT post
[The Dolev and Reischuk Lower Bound](https://decentralizedthoughts.github.io/2019-08-16-byzantine-agreement-needs-quadratic-messages/)
gives the main isolation argument. If too few messages are sent, the adversary
can isolate a party and make it unable to tell which decision is required.

The same isolation template can be reused for other primitives. In
[A new Dolev-Reischuk style Lower Bound](https://decentralizedthoughts.github.io/2022-08-14-new-DR-LB/),
the target is Byzantine Crusader Broadcast rather than agreement.

Randomization does not automatically remove this barrier. The post
[Agreement against strongly adaptive adversaries needs quadratic communication](https://decentralizedthoughts.github.io/2024-12-16-strong-adaptive-lower-bound/)
extends the message lower bound to randomized protocols against a strongly
adaptive omission adversary that can claw back in-flight messages from newly
corrupted parties. The adversary waits to see who sends a message to the party
it wants to isolate, corrupts that sender, and then claws back the
still-undelivered message. This claw-back ability is the mathematical property
that makes the lower bound go through.

The takeaway is that subquadratic agreement requires both randomization and a
weaker adversary.

At a glance:

| Lower bound | Adversary recipe | Moral |
|---|---|---|
| [Dolev-Reischuk](https://decentralizedthoughts.github.io/2019-08-16-byzantine-agreement-needs-quadratic-messages/) | isolate one party | agreement needs enough messages to reach everyone |
| [DR for Crusader Broadcast](https://decentralizedthoughts.github.io/2022-08-14-new-DR-LB/) | reuse isolation for a weaker broadcast task | the same isolation argument applies beyond agreement |
| [DR for strongly adaptive randomized agreement](https://decentralizedthoughts.github.io/2024-12-16-strong-adaptive-lower-bound/) | corrupt senders after seeing them and claw back in-flight messages | randomness is not enough against adaptive with claw-back power |

## Rounds and Infinite Executions

The next natural question is how many rounds agreement or other tasks need.

The introductory post is
[Consensus Lower Bounds via Uncommitted Configurations](https://decentralizedthoughts.github.io/2019-12-15-consensus-model-for-FLP/).
It sets up the language of committed and uncommitted configurations (univalent
and bivalent). A configuration is uncommitted when the adversary can force at
least two futures with different decision values.

In synchrony, this gives the classic $t+1$ round lower bound:
[Synchronous Consensus Lower Bound via Uncommitted Configurations](https://decentralizedthoughts.github.io/2019-12-15-synchrony-uncommitted-lower-bound/).
Even with crash faults, an adversary can spend one crash per round and keep
the execution uncommitted. Note that this $t+1$ round lower bound holds even
for randomized protocols.

In asynchrony, the same idea gives FLP:
[The FLP Impossibility](https://decentralizedthoughts.github.io/2019-12-15-asynchrony-uncommitted-lower-bound/).
The original paper is
[Fischer, Lynch, and Paterson](https://groups.csail.mit.edu/tds/papers/Lynch/jacm85.pdf).
The real implication is that:

> Every protocol solving consensus in asynchrony (even randomized ones) must
> have an infinite execution even against one crash fault.

This statement also implies the weaker statement that has been more commonly
quoted:

> Deterministic consensus in asynchrony is impossible even against one crash
> fault.

But note that the infinite execution statement is stronger: it applies to
randomized protocols, and it applies to any protocol that solves consensus, not
just deterministic ones.

The post
[Consensus with One Mobile Crash in Synchrony or One Crash in Asynchrony Has Infinite Executions](https://decentralizedthoughts.github.io/2024-03-07-mobile-is-FLP/)
puts FLP and the Santoro-Widmayer mobile crash lower bound into one view. The
proof tracks a pivot configuration and moves the pivot forward. The post also
offers a simpler, more modern proof of the FLP theorem.

Finally,
[Early Stopping, Same but Different](https://decentralizedthoughts.github.io/2024-01-28-early-stopping-lower-bounds/)
asks what happens when the actual number of failures is smaller than the
maximum number the protocol tolerates. The lower bound is still a pivot
argument, but now the question is how soon the protocol can decide in
executions with few or no failures.

This is also the right place to read
[Synchronized Clocks, Fixed View Schedules, and Simultaneous Agreement](https://decentralizedthoughts.github.io/2026-03-07-simultaneous-agreement/).
Trying to let a fixed view schedule jump early after a fast good case forces
parties to agree not only on a value, but also on which side of a time
threshold they decide. That is simultaneous agreement, and it has the same
$t+1$ barrier.

At a glance:

| Setting | What the adversary preserves | Resulting barrier |
|---|---|---|
| [Synchronous consensus](https://decentralizedthoughts.github.io/2019-12-15-synchrony-uncommitted-lower-bound/) | an uncommitted configuration | $t+1$ rounds |
| [Asynchronous consensus](https://decentralizedthoughts.github.io/2019-12-15-asynchrony-uncommitted-lower-bound/) | an uncommitted configuration | an infinite execution |
| [Mobile crash in synchrony](https://decentralizedthoughts.github.io/2024-03-07-mobile-is-FLP/) | a pivotal configuration | infinite executions again |
| [Early stopping](https://decentralizedthoughts.github.io/2024-01-28-early-stopping-lower-bounds/) | a pair of AS-FFD configurations | even good executions may need two more rounds |
| [Simultaneous agreement](https://decentralizedthoughts.github.io/2026-03-07-simultaneous-agreement/) | disagreement about which side of a time threshold was crossed | the $t+1$ barrier returns |

## Good Case Latency

Good case latency lower bounds ask a more refined question:

> If the leader is honest and the network is synchronous, how quickly can all
> honest parties decide?

The broad map is
[Good-case Latency of Byzantine Broadcast: a Complete Categorization](https://decentralizedthoughts.github.io/2021-02-28-good-case-latency-of-byzantine-broadcast-a-complete-categorization/),
with the corresponding paper
[Good-case Latency of Byzantine Broadcast: A Complete Categorization](https://arxiv.org/abs/2102.07240).
The post separates synchrony, partial synchrony, and asynchrony. It is not
one lower bound, but a collection of tight bounds across several regimes.

A related post,
[The round complexity of Reliable Broadcast](https://decentralizedthoughts.github.io/2021-09-29-the-round-complexity-of-reliable-broadcast/),
asks the same kind of question for reliable broadcast, measuring asynchrony by
causal message chains rather than real time. There the clean split is between
authenticated and unauthenticated settings: two-round good-case reliable
broadcast is possible at $n\geq 3f+1$ with a PKI, while without a PKI the same
good case needs $n\geq 4f$.

For synchrony, read
[Good-case Latency of Byzantine Broadcast: the Synchronous Case](https://decentralizedthoughts.github.io/2021-03-09-good-case-latency-of-byzantine-broadcast-the-synchronous-case/).
The main theme is equivocation detection. Depending on the exact resilience
regime, the best latency is not always an integer number of full delay bounds.

For rotating leaders in synchrony, read
[Good-case Latency of Rotating Leader Synchronous BFT](https://decentralizedthoughts.github.io/2021-12-07-good-case-latency-of-rotating-leader-synchronous-bft/).
It explains why, when leaders rotate and propose responsively, a single slot
cannot beat the $2\Delta$ barrier.

For partial synchrony, there is an especially important lower bound:
[Why BFT Needs Three Rounds](https://decentralizedthoughts.github.io/2025-11-22-three-round-BFT/).
For $n\leq 5f-2$, a Byzantine broadcast protocol in partial synchrony needs at
least three rounds in the good case. This is why PBFT, Tendermint, HotStuff,
Casper FFG, and Simplex all have the proposal plus two voting round pattern at
optimal resilience. Two-round good-case protocols need more validators, a
different timing assumption, or a weaker target.

The related responsiveness lower bound is
[On the Optimality of Optimistic Responsiveness](https://decentralizedthoughts.github.io/2020-06-12-optimal-optimistic-responsiveness/).
Optimistic responsiveness is powerful, but it does not make the adversary's
view gap disappear for free.

At a glance:

| Setting | Best possible latency or lower-bound tradeoff | What changes the conclusion |
|---|---|---|
| [Asynchronous reliable broadcast, authenticated](https://decentralizedthoughts.github.io/2021-02-28-good-case-latency-of-byzantine-broadcast-a-complete-categorization/) | tight 2-round good case | this is reliable broadcast, not partial-synchronous BFT SMR |
| [Unauthenticated reliable broadcast](https://decentralizedthoughts.github.io/2021-09-29-the-round-complexity-of-reliable-broadcast/) | 2-round good case iff $n\geq 4f$; one-round bad-case catch-up for $f\geq 3$ needs $n\geq 5f-1$ | signatures reduce the threshold to $n\geq 3f+1$ |
| [Partial synchrony, $n\leq 5f-2$](https://decentralizedthoughts.github.io/2025-11-22-three-round-BFT/) | at least 3 good-case rounds | more validators, stronger timing, or a weaker target |
| [Partial synchrony, $n\geq 5f-1$](https://decentralizedthoughts.github.io/2021-02-28-good-case-latency-of-byzantine-broadcast-a-complete-categorization/) | tight 2-round good case | dropping below $5f-1$ brings back the 3-round lower bound |
| [Synchrony, $0<f<n/3$](https://decentralizedthoughts.github.io/2021-03-09-good-case-latency-of-byzantine-broadcast-the-synchronous-case/) | tight $2\delta$ | at $f=n/3$ the bound jumps to $\Delta+\delta$ |
| [Synchrony, $f=n/3$](https://decentralizedthoughts.github.io/2021-03-09-good-case-latency-of-byzantine-broadcast-the-synchronous-case/) | tight $\Delta+\delta$ | below this threshold, two actual-delay rounds suffice |
| [Synchrony, $n/3<f<n/2$](https://decentralizedthoughts.github.io/2021-03-09-good-case-latency-of-byzantine-broadcast-the-synchronous-case/) | tight $\Delta+\delta$ with synchronized start; tight $\Delta+1.5\delta$ with unsynchronized start | clock synchronization changes the exact optimum |
| [Synchrony, $n/2\leq f<n$](https://decentralizedthoughts.github.io/2021-03-09-good-case-latency-of-byzantine-broadcast-the-synchronous-case/) | known lower bound $\lfloor n/(n-f)\rfloor\Delta$ and $O(n/(n-f))\Delta$ upper bound | reducing the fault fraction moves back to the tight $f<n/2$ regimes |
| [Rotating-leader synchrony](https://decentralizedthoughts.github.io/2021-12-07-good-case-latency-of-rotating-leader-synchronous-bft/) | single-slot responsive rotation needs $2\Delta-O(\delta)$ and is matched by $2\Delta+O(\delta)$ | stable leaders or pipelining change the latency target |
| [Optimistic responsiveness with a fault-tolerant fast path](https://decentralizedthoughts.github.io/2020-06-12-optimal-optimistic-responsiveness/) | responsive $O(\delta)$ commit forces synchronous fallback at least $2\Delta-O(\delta)$ | a zero-fault optimistic path avoids this tradeoff |
| [Optimistic responsiveness with a zero-fault fast path](https://decentralizedthoughts.github.io/2020-06-12-optimal-optimistic-responsiveness/) | $\Delta$ synchronous latency is possible | the optimistic condition no longer tolerates even one fault |

## Validity and Censorship Resistance

Many lower bounds become sharper once validity is made more explicit.

The starting point is
[What about Validity?](https://decentralizedthoughts.github.io/2022-12-12-what-about-validity/).
Classic validity is weak for blockchain protocols, where values are usually
client requests or application states. External validity solves one problem:
the protocol can check that a proposed value is valid without requiring all
honest parties to start with the same input. Stronger validity notions, such
as honest input validity or majority validity, create new lower bounds.

Censorship resistance changes the good case latency problem. In a traditional
leader based BFT protocol, the leader both constructs the input and proposes
it. Censorship resistance separates these roles: an input holder has the
value, while an expediter drives the protocol. The post
[Latency cost of censorship resistance](https://decentralizedthoughts.github.io/2026-04-23-latency-of-censorship-resistance/)
shows that this separation costs two rounds in partial synchrony. For
$n\leq 5t-6$ and $t\geq 4$, a censorship resistant protocol cannot have good
case latency below five rounds.

The natural follow up is
[Beyond censorship resistance: hiding, simultaneous binding, and accountable last look](https://decentralizedthoughts.github.io/2026-04-27-beyond-CR/).
That post is more about goals than lower bounds: once censorship resistance is
paid for, hiding, simultaneous binding, and last-look protection can be added
under synchrony with the same two extra rounds.

At a glance:

| Property | Bound or tight point | What changes the conclusion |
|---|---|---|
| [Honest input validity, synchrony](https://decentralizedthoughts.github.io/2022-12-12-what-about-validity/) | impossible for $n\leq \max(3,m)f$ with $m$ input values | above the threshold, gradecast reduces the problem to external validity |
| [Honest input validity, asynchrony](https://decentralizedthoughts.github.io/2022-12-12-what-about-validity/) | impossible for $n\leq (m+1)f$ | above the threshold, reliable broadcast plus external validity is enough |
| [Honest-input-or-default validity](https://decentralizedthoughts.github.io/2022-12-12-what-about-validity/) | no stronger lower bound than ordinary consensus | allowing $\bot$ lets the property reduce back to external validity |
| [Majority / $k$-advantaged validity](https://decentralizedthoughts.github.io/2022-12-12-what-about-validity/) | $2f$-advantaged validity is impossible in asynchrony for any $n/f$, even binary | $2f+1$-advantaged validity is achievable |
| [Censorship resistance in partial synchrony](https://decentralizedthoughts.github.io/2026-04-23-latency-of-censorship-resistance/) | at least 5 good-case rounds for $n\leq 5t-6$ and $t\geq 4$ | ordinary leader-based BFT can stop at 3; separating input holder $I$ from expediter $E$ costs two rounds |
| [CR + SCQ + hiding + simultaneous binding + accountable last look](https://decentralizedthoughts.github.io/2026-04-27-beyond-CR/) | under synchrony and $n\geq 3f+1$, any BFT protocol can be augmented with two extra rounds | the three market protections are needed together: hiding, simultaneous binding, and last-look protection |

## Privacy and Secret State

Privacy lower bounds are different from agreement lower bounds because the
adversary is not only trying to split decisions. It is also trying to learn or
expose a secret before the protocol has enough agreement about who is allowed
to know it.

The post
[Asynchronous Fault Tolerant Computation with Optimal Resilience](https://decentralizedthoughts.github.io/2020-07-15-asynchronous-fault-tolerant-computation-with-optimal-resilience/)
explains the Ben-Or, Kelmer, Rabin lower bound: asynchronous verifiable secret
sharing with perfect security has a nonzero probability of nontermination
when $n/4\leq f<n/3$. This is why perfectly secure asynchronous MPC has the
familiar $n>4f$ threshold.

The post
[The SAP theorem for storing secret keys](https://decentralizedthoughts.github.io/2024-08-09-sap/)
is the secret key analogue of CAP. If a system wants secret availability and
secret privacy under partitions, it must pay with another assumption or give
up one of the properties.

At a glance:

| Object being protected | Adversary goal | Lower-bound shape |
|---|---|---|
| [Agreement value](https://decentralizedthoughts.github.io/2019-12-15-consensus-model-for-FLP/) | make honest parties decide differently | split worlds and pivots |
| [VSS or MPC secret](https://decentralizedthoughts.github.io/2020-07-15-asynchronous-fault-tolerant-computation-with-optimal-resilience/) | learn before reconstruction is safe | privacy hybrids |
| [Stored secret key](https://decentralizedthoughts.github.io/2024-08-09-sap/) | keep availability and privacy through partitions | SAP-style CAP tradeoff |

## Liveness Attacks

Lower bounds are not always about agreement. Some are about progress.

[Raft does not Guarantee Liveness in the face of Network Faults](https://decentralizedthoughts.github.io/2020-12-12-raft-liveness-full-omission/)
shows that omission faults can keep Raft from making progress. The issue is
not safety; it is that the leader election and message pattern allow the
adversary to prevent a stable leader from getting the messages it needs.

This is a useful reminder for partially synchronous BFT as well. A safety
proof does not automatically give a liveness proof. In protocols like Simplex,
Complex, Kuplex, and fixed view schedule variants, the liveness argument has
to explain exactly why some future leader can form a valid proposal.

At a glance:

| Safety proof says | Liveness proof must also show |
|---|---|
| [old decisions cannot conflict](https://decentralizedthoughts.github.io/2020-12-12-raft-liveness-full-omission/) | a new leader can still find usable support |
| [old locks remain safe](https://decentralizedthoughts.github.io/2020-12-12-raft-liveness-full-omission/) | old evidence can be found, relayed, or bypassed |
| [view change preserves safety](https://decentralizedthoughts.github.io/2020-12-12-raft-liveness-full-omission/) | some view change eventually produces a valid proposal |
| [omission faults do not break agreement](https://decentralizedthoughts.github.io/2020-12-12-raft-liveness-full-omission/) | omission faults cannot starve every leader forever |

## Proof Techniques

It is useful to read the posts not only by result, but also by technique.

**Split brain.** Partition the parties so that two sides see different legal
executions. This is the core of CAP, DLS, and many partial synchrony
threshold lower bounds.

**Simulation.** Let Byzantine parties imitate honest parties from other
executions. This is the FLM technique and also appears in Crusader Agreement
lower bounds.

**Isolation.** Keep one party from receiving enough messages. This is the
Dolev-Reischuk template and its strongly adaptive variants.

**Bivalence and pivots.** Keep the execution uncommitted by moving one
critical difference forward. This is the FLP line, the synchronous $t+1$
round lower bound, early stopping, and simultaneous agreement.

**Validity worlds.** Build one execution where validity forces value $0$ and
another where validity forces value $1$, then connect them through a mixed
execution. This is the proof style behind many good-case latency lower bounds.

**Privacy hybrids.** Change one party's secret or one share at a time while
preserving what the adversary can see. This is the natural language of privacy
and secret state lower bounds.

At a glance:

| Technique | Adversary move | Where to read |
|---|---|---|
| Split brain | make two sides see different legal executions | [CAP](https://decentralizedthoughts.github.io/2023-07-09-CAP-two-servers-in-psynch/), [DLS](https://decentralizedthoughts.github.io/2019-06-25-on-the-impossibility-of-byzantine-agreement-for-n-equals-3f-in-partial-synchrony/) |
| Simulation | make Byzantine parties imitate another world | [FLM](https://decentralizedthoughts.github.io/2019-08-02-byzantine-agreement-is-impossible-for-%24n-slash-leq-3-f%24-is-the-adversary-can-easily-simulate/), [Crusader Agreement](https://decentralizedthoughts.github.io/2021-10-04-crusader-agreement-with-dollars-slash-leq-1-slash-3%24-error-is-impossible-for-%24n-slash-leq-3f%24-if-the-adversary-can-simulate/) |
| Isolation | keep one party below the evidence threshold | [Dolev-Reischuk](https://decentralizedthoughts.github.io/2019-08-16-byzantine-agreement-needs-quadratic-messages/), [strong adaptivity](https://decentralizedthoughts.github.io/2024-12-16-strong-adaptive-lower-bound/) |
| Bivalence and pivots | move the critical difference forward | [FLP model](https://decentralizedthoughts.github.io/2019-12-15-consensus-model-for-FLP/), [synchronous $t+1$](https://decentralizedthoughts.github.io/2019-12-15-synchrony-uncommitted-lower-bound/), [early stopping](https://decentralizedthoughts.github.io/2024-01-28-early-stopping-lower-bounds/) |
| Validity worlds | force 0 in one world and 1 in another | [good-case latency](https://decentralizedthoughts.github.io/2021-02-28-good-case-latency-of-byzantine-broadcast-a-complete-categorization/), [three-round BFT](https://decentralizedthoughts.github.io/2025-11-22-three-round-BFT/) |
| Privacy hybrids | change one secret or share at a time | [asynchronous MPC](https://decentralizedthoughts.github.io/2020-07-15-asynchronous-fault-tolerant-computation-with-optimal-resilience/), [SAP](https://decentralizedthoughts.github.io/2024-08-09-sap/) |

## Reading Map

For fault thresholds, read:

* [The CAP theorem for partial synchrony](https://decentralizedthoughts.github.io/2023-07-09-CAP-two-servers-in-psynch/)
* [State Machine Replication for Two Servers and One Omission Failure is Impossible](https://decentralizedthoughts.github.io/2019-11-02-primary-backup-for-2-servers-and-omission-failures-is-impossible/)
* [In between Crash and Omission failures](https://decentralizedthoughts.github.io/2024-01-30-between-crash-and-omission/)
* [Blockchain Resource Pools and a CAP-esque Impossibility Result](https://decentralizedthoughts.github.io/2022-03-03-blockchain-resource-pools-and-a-cap-esque-impossibility-result/)
* [Byzantine Agreement is impossible for $n\leq 3f$ under partial synchrony](https://decentralizedthoughts.github.io/2019-06-25-on-the-impossibility-of-byzantine-agreement-for-n-equals-3f-in-partial-synchrony/)
* [Byzantine Agreement is Impossible for $n\leq 3f$ if the Adversary can Simulate](https://decentralizedthoughts.github.io/2019-08-02-byzantine-agreement-is-impossible-for-%24n-slash-leq-3-f%24-is-the-adversary-can-easily-simulate/)
* [Crusader Agreement with $\leq 1/3$ Error is Impossible for $n\leq 3f$](https://decentralizedthoughts.github.io/2021-10-04-crusader-agreement-with-dollars-slash-leq-1-slash-3%24-error-is-impossible-for-%24n-slash-leq-3f%24-if-the-adversary-can-simulate/)
* [Neither Non-equivocation nor Transferability alone is enough](https://decentralizedthoughts.github.io/2021-06-14-neither-non-equivocation-nor-transferability-alone-is-enough-for-tolerating-minority-corruptions-in-asynchrony/)
* [$3f+1$ is needed in Partial Synchrony even against a Rollback adversary](https://decentralizedthoughts.github.io/2023-06-26-dls-meets-rollback/)

For communication lower bounds, read:

* [The Dolev and Reischuk Lower Bound](https://decentralizedthoughts.github.io/2019-08-16-byzantine-agreement-needs-quadratic-messages/)
* [A new Dolev-Reischuk style Lower Bound](https://decentralizedthoughts.github.io/2022-08-14-new-DR-LB/)
* [Agreement against strongly adaptive adversaries needs quadratic communication](https://decentralizedthoughts.github.io/2024-12-16-strong-adaptive-lower-bound/)

For rounds and infinite executions, read:

* [Consensus Lower Bounds via Uncommitted Configurations](https://decentralizedthoughts.github.io/2019-12-15-consensus-model-for-FLP/)
* [Synchronous Consensus Lower Bound via Uncommitted Configurations](https://decentralizedthoughts.github.io/2019-12-15-synchrony-uncommitted-lower-bound/)
* [The FLP Impossibility](https://decentralizedthoughts.github.io/2019-12-15-asynchrony-uncommitted-lower-bound/)
* [Consensus with One Mobile Crash in Synchrony or One Crash in Asynchrony Has Infinite Executions](https://decentralizedthoughts.github.io/2024-03-07-mobile-is-FLP/)
* [Early Stopping, Same but Different](https://decentralizedthoughts.github.io/2024-01-28-early-stopping-lower-bounds/)
* [Synchronized Clocks, Fixed View Schedules, and Simultaneous Agreement](https://decentralizedthoughts.github.io/2026-03-07-simultaneous-agreement/)

For good case latency, read:

* [Good-case Latency of Byzantine Broadcast: a Complete Categorization](https://decentralizedthoughts.github.io/2021-02-28-good-case-latency-of-byzantine-broadcast-a-complete-categorization/)
* [The round complexity of Reliable Broadcast](https://decentralizedthoughts.github.io/2021-09-29-the-round-complexity-of-reliable-broadcast/)
* [Good-case Latency of Byzantine Broadcast: the Synchronous Case](https://decentralizedthoughts.github.io/2021-03-09-good-case-latency-of-byzantine-broadcast-the-synchronous-case/)
* [Good-case Latency of Rotating Leader Synchronous BFT](https://decentralizedthoughts.github.io/2021-12-07-good-case-latency-of-rotating-leader-synchronous-bft/)
* [Why BFT Needs Three Rounds](https://decentralizedthoughts.github.io/2025-11-22-three-round-BFT/)
* [On the Optimality of Optimistic Responsiveness](https://decentralizedthoughts.github.io/2020-06-12-optimal-optimistic-responsiveness/)

For validity and censorship resistance, read:

* [What about Validity?](https://decentralizedthoughts.github.io/2022-12-12-what-about-validity/)
* [Latency cost of censorship resistance](https://decentralizedthoughts.github.io/2026-04-23-latency-of-censorship-resistance/)
* [Beyond censorship resistance](https://decentralizedthoughts.github.io/2026-04-27-beyond-CR/)

For privacy and secret state, read:

* [Asynchronous Fault Tolerant Computation with Optimal Resilience](https://decentralizedthoughts.github.io/2020-07-15-asynchronous-fault-tolerant-computation-with-optimal-resilience/)
* [The SAP theorem for storing secret keys](https://decentralizedthoughts.github.io/2024-08-09-sap/)

For liveness attacks, read:

* [Raft does not Guarantee Liveness in the face of Network Faults](https://decentralizedthoughts.github.io/2020-12-12-raft-liveness-full-omission/)

For classic external papers, read:

* [Dwork, Lynch, Stockmeyer: Consensus in the Presence of Partial Synchrony](https://groups.csail.mit.edu/tds/papers/Lynch/jacm88.pdf)
* [Fischer, Lynch, Paterson: Impossibility of Distributed Consensus with One Faulty Process](https://groups.csail.mit.edu/tds/papers/Lynch/jacm85.pdf)
* [Fischer, Lynch, Merritt: Easy Impossibility Proofs for Distributed Consensus Problems](https://groups.csail.mit.edu/tds/papers/Lynch/FischerLynchMerritt-dc.pdf)
* [Dolev and Reischuk: Bounds on Information Exchange for Byzantine Agreement](https://www.cs.huji.ac.il/~dolev/pubs/p132-dolev.pdf)
* [Ben-Or, Kelmer, Rabin: Asynchronous Secure Computations with Optimal Resilience](https://arxiv.org/abs/2006.16686)
* [Good-case Latency of Byzantine Broadcast: A Complete Categorization](https://arxiv.org/abs/2102.07240)
