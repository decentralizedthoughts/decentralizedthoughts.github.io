---
title: 'Mobile delay is same but different: infinite executions for mobile crash and
  FLP'
date: 2024-03-07 12:05:00 -05:00
tags:
- lowerbound
author: Ittai Abraham and Gilad Stern
---

Both the *synchronous mobile single crash adversary* and the *asynchronous single crash adversary* (aka [FLP](https://decentralizedthoughts.github.io/2019-12-15-asynchrony-uncommitted-lower-bound/)) must have infinite executions (if they always reach agreement).

We prove both results by *reducing* the problem to a common weaker adversary we call the ***mobile delay adversary*** in synchrony with a single failure and then prove that any consensus protocol resilient to it must have infinite executions. 

This gives a rather simple and unified proof, for both mobile crash and asynchrony.

## Definitions 

Same definitions as our [previous post on early stopping](https://decentralizedthoughts.github.io/2024-01-28-early-stopping-lower-bounds/).

***Definition 1:*** *Two configurations are **Almost Same (AS)** if the state of all parties except for a single party $i$ are the same.*

***Definition 2:*** *Two Almost Same (AS) configurations are **Failure Free Different (FFD)** if the failure free continuation of one configuration leads to a different decision value than the failure free continuation of the other configuration.*

## Mobile delay adversary

The mobile delay adversary with one crash failure, in lock step, in each round, can choose one party to *delay*. Once a party is delayed, its remaining outgoing messages suffer an additional round of delay. The adversary can corrupt a party with a delay at any point in the round.

Note that the adversary can continue to delay the same party indefinitely and this is equivalent to crashing the party. The following claims are immediate:

**Claim 1**: If there is an asynchronous protocol that is resilient to one crash, then there is a protocol resilient to one mobile delay.

*Proof of claim 1*: Assume there is an asynchronous protocol that is resilient to $1$ crash and let there be some adversary to the mobile delay protocol. If a party is delayed for any finite amount in the mobile delay setting, we can simulate this via an asynchronous environment that delivers all messages synchronously in each round, but simply delays these messages by that amount. If a party is indefinitely delayed, then the asynchronous adversary can simulate this by crashing this party. Since this is a possible execution in the asynchronous environment, the protocol is resilient to this (arbitrary) mobile delay adversary.

**Claim 2**: If there is a protocol that is resilient to one mobile crash, then there is a protocol resilient to one mobile delay.

*Proof of claim 2*: Mobile crash has more power because it erases the messages sent after the crash, while mobile delay just delays them. So a mobile crash protocol can be transformed to a mobile delay protocol, by instructing parties to ignore any message they receive late and running the original protocol (thus simulating crashes).

## Mobile delay adversary lower bound

We start with the following Lemma from the [previous post](https://decentralizedthoughts.github.io/2024-01-28-early-stopping-lower-bounds/). We quickly repeat the proof for completeness.

***Lemma 1***: *Any consensus protocol that is resilient to at least 1 crash failure must have two initial configurations that are Almost Same but Failure Free Different (AS but FFD).*

*Proof*: For $0 \leq i \le n$ let $C_i$ be the initial configuration where parties 1 to $i$ have input 1 (empty set for $i=0$) and the rest have input 0. Let $val(i)$ be the decision in the failure free execution that starts with configuration $C_i$. From validity, $val(0)=0$ and $val(n)=1$, so the (trivial) [one dimension Sperner's Lemma](https://en.wikipedia.org/wiki/Sperner%27s_lemma#One-dimensional_case) implies that there exists $1 \le i \le n$ and two configurations $C_{i-1},C_{i}$ that are AS but FFD.



The core of the lower bound is in the following (which is similar to [the previous post as well](https://decentralizedthoughts.github.io/2024-01-28-early-stopping-lower-bounds/)):

***Lemma 2***: *If $C,C'$ are two AS but FFD configurations at the beginning of round $k$, then there are two configurations that are AS but FFD that extend $C$ and/or $C'$ by one round in which the adversary delays at most one party in round $k$.*


*Proof*: Let party $i$ be the only difference between $C$ and $C'$.

Look at the extension of $C$ to $D$ and $C'$ to $D'$ by the delay of party $i$ in the beginning of round $k$.

Case 1: If $D$ and $D'$ are FFD, then the lemma holds immediately since they are also AS.

Case 2: Both failure free executions of $D$ and $D'$ have the same output value. Wlog, their FF value is *different* from the FF value of $C$ (otherwise use $C'$ below).

Now consider the $n+1$ configurations $D=C_0,C_1,\dots,C_n=C$ where $C_j$ is the configuration in which the adversary delays party $i$ after it sends its messages to $j$ parties. At the end of round $k$, any two consecutive configurations are AS because they differ in one party $j$ that either received or did not receive $i$'s message. Note that party $i$ has the same state: it sent all its messages.

Note that $C_0$ is the execution $D$ in which the adversary delays party $i$ in the beginning of the round. This means that from our above assumption, we know that if we continue from $C_0$ without faults the decision value is going to be different than the decision value in a failure-free extension of configuration $C$. Using the (trivial) [one dimension Sperner's Lemma](https://en.wikipedia.org/wiki/Sperner%27s_lemma#One-dimensional_case), we know that there must exist two consecutive configurations that are AS but FFD.

This completes the proof of Lemma 2.

### Lemma 1 + Lemma 2 implies an infinite execution

Starting with Lemma 1 and repeatedly applying Lemma 2 creates a process that extends the round $k$ tree with two leaves. This process induces a branch of infinite length. This branch of infinite length is an execution that represents the adversary strategy.


**Claim 3**: No two parties can decide in the execution defined by the branch of infinite length.

*Proof*: Consider the first round $k$ where at least two parties have decided on the execution induced by this branch. By definition, at least one of the parties that decided has an indistinguishable state at round $k$ between its execution on the branch and the other execution that is AS but FFD for round $k$.

There are two different configurations whose failure free execution from this point onwards leads to different values. But these configurations are indistinguishable for the deciding party. So the deciding party must have a safety violation in one of these configurations. This is a contradiction to the assumption that the protocol is always safe.


This proves that infinite executions with at most one decision must exist for the mobile delay adversary, and thus clearly some parties don't output values (unless $n=1$).

From Claims 1 and 2, this also proves that infinite executions with at most one decision must exist for a single mobile crash failure and for a [single crash failure in asynchrony](FLP).

## Notes

* The proof in the post is based on  [a layered analysis of consensus](http://courses.csail.mit.edu/6.897/fall04/papers/Moses/layering.pdf) by [Moses and Rajsbaum](https://epubs.siam.org/doi/10.1137/S0097539799364006). The main difference is the effort to maintain just two configurations in each layer (not all configurations). This weaker argument is somewhat more constructive. 
* Another difference is the mobile delay adversary as a base for reductions to both the mobile crash and the asynchronous case. This highlights how little asynchrony is needed and the deep connection between asynchrony and mobile faults. 
* Compared to the FLP proof via bi-valency, this proof is more direct in showing a fair execution, and in our view, this makes the proof somewhat simpler. On the other hand, the need to reason about two configurations and the fact that this process induces an infinite branch is somewhat more involved than the single infinite execution via the bi-valency argument.

Please leave comments on [Twitter](...).