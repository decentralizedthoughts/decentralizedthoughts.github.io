---
title: Consensus tolerating one mobile crash in synchrony or one crash is asynchrony
  must have infinite executions for the same simple reason
date: 2024-03-07 12:05:00 -05:00
tags:
- lowerbound
author: Ittai Abraham and Gilad Stern
---

In a consensus protocol, parties have an input (at least two possible values, say 0 or 1) and may output a decision value such that:

* **Uniform Agreement**: all decision values are the same.
* **Validity**: if all inputs are the same, then this is the output value.

The third property is **Termination**, and the following two influential lower bounds correspond to two [Dijkstra prizes](https://www.podc.org/dijkstra/) (awarded in [2001](https://www.podc.org/influential/2001-influential-paper/) and [2024](https://www.podc.org/2024-edsger-w-dijkstra-prize-in-distributed-computing/)):

**Theorem [[FLP83](https://decentralizedthoughts.github.io/2019-12-15-asynchrony-uncommitted-lower-bound/)]**: any protocol solving consensus in an asynchronous model that is resilient to one crash failure must have an infinite execution.

**Theorem [[SW89](https://dl.acm.org/doi/10.5555/73228.73254)]**: any protocol solving consensus in a synchronous model that is resilient to one mobile crash failure must have an infinite execution.

We prove both results by a *reduction* to a common weaker adversary we call the ***mobile delay adversary*** in synchrony with a single failure and then prove that any consensus protocol resilient to it must have infinite executions. This gives a rather simple and unified proof, for both a **single mobile crash in synchrony** and a **single crash in asynchrony**.


## Definitions 

A *configuration* is a set of all the states of all the parties and the set of currently undelivered messages.

***Definition***: For a configuration $C$ let $val(C)$ be the decision value in the *failure-free extension* that starts with configuration $C$ and runs in synchrony (all messages arrive after one lockstep delay) with no failures.

Minor note: we assume $val(C)$ is well-defined because the execution reaches a decision - if it does not terminate then we have found a non-terminating execution.

***Definition***: For a configuration $C$ and party $p$ let $val(C-p)$ be the decision in the extension that starts with configuration $C$ and runs in synchrony (all messages arrive after one lockstep delay) except that all party $p$'s outgoing messages are infinitely delayed  and all other parties are failure-free. 

Minor note: The outgoing messages sent by $p$ in $C$ that have not been delivered are also delayed. Since we assume the execution $val(C-p)$ terminates in a finite number of rounds, we can set the delay of $p$'s messages to be longer than this time.

***Definition of a $p$-pivot configuration:*** For a party $p$ we say that a configuration $C$ is a $p$-pivot if $val(C) \neq val (C-p)$.

In words, a $p$-pivot configuration is a configuration where the decision value of its failure-free extension is *different* from the decision value of its extension where no party sees any message from $p$ and all others are failure-free. Compared to the definition of bi-valency, this definition is more explicit and constructive in terms of the extensions that lead to opposing decision values.

## Mobile delay adversary

The mobile delay adversary with one failure, in lockstep, at each round, can choose one party to *delay* some of its messages. Once a party is delayed, its remaining outgoing messages suffer one additional round of delay. The adversary can corrupt a party with a delay at any point in the round. So for example it can delay all the outgoing messages, or only the last outgoing message, etc.

Note that the adversary can continue to delay the same party for any finite number of rounds and this is essentially equivalent to crashing the party.

## Mobile delay adversary lower bound

Not surprisingly, we start by showing that some initial configuration must be a $p$-pivot configuration.

***Lemma 1***: *Any consensus protocol that is resilient to at least 1 mobile delay failure has a $p$-pivot initial configuration.*

*Proof*: For $0 \leq i \le n$ let $C_i$ be the initial configuration where parties 1 to $i$ have input 1 (empty set for $i=0$) and the rest have input 0.  From validity, $val(C_0)=0$ and $val(C_n)=1$, so the (trivial) [one-dimensional Sperner's Lemma](https://en.wikipedia.org/wiki/Sperner%27s_lemma#One-dimensional_case) implies that there exists $1 \le i \le n$ and two adjacent configurations such that $val(C_{i-1}) =0$ and $val(C_{i})=1$.

Note that the only difference between $C_{i-1}$ and $C_i$ is the initial value of party $i$. Consider executions where party $i$ crashes (is delayed forever) at the beginning of the execution. Since there is no way to know the state of party $i$ we have

$$val(C_{i-1}-i)=val(C_i-i)$$

If this value is 1 then $C_{i-1}$ is an $i$-pivot configuration and similarly if this value is 0 then $C_i$ is an $i$-pivot configuration. This completes the proof.

We now show that we can always extend a $p$-pivot configuration $C$ by one round to a $p'$-pivot configuration $C'$, thus creating an infinite execution. In each such *round* all parties progress in lockstep except for at most one party which we may delay its outgoing messages.

***Lemma 2***: *If $C$ is a $p$-pivot configuration at the beginning of round $k$, then there is an extension of $C$ to $C'$ by one round in the mobile delay model where $C'$ is a $p'$-pivot configuration at the beginning of round $k+1$.*

*Proof*: Given a $p$-pivot configuration $C$ at the beginning of round $k$:

Define configuration $D$ as: the extension of configuration $C$ by one round (to the beginning of round $k+1$), where all of party $p$'s outgoing messages are delayed in round $k$ by one more round.

Note that we delay also outgoing messages by $p$ that have not been delivered in $C$ and that in the failure-free extension of $D$ all delayed messages will be delivered in round $k+1$.

Case 1 (trivial): If $val(D) \neq val(D-p)$ then $D$ is one round extension of $C$ and it is a $p$-pivot configuration. So the Lemma holds.

Case 2: Otherwise $val(D) = val(D-p)$. From the definition of $D$, $val(C-p)=val(D-p)$ because both executions are identical: no message sent from $p$ arrives after the beginning of round $k$. From the assumption that $C$ is a $p$-pivot, $val(C-p) \neq val(C)$. Therefore $val(D) \neq val(C)$. Without loss of generality, assume that $val(D)=0$, hence $val(C)=1$.

Observe that the only difference between $C$ and $D$ is that in $D$ we delay all of $p$'s outgoing messages in round $k$ for one more round.

Consider the $n+1$ configurations $D=C_0,C_1,\dots,C_n$ where $C_j$ is the configuration in which the adversary delays party $p$'s outgoing messages after it sends its messages to $j$ parties. 

Note that $C_n$ is simply the first failure-free round after $C$, hence $val(C_n)=val(C)=1$. Also note that by definition $D=C_0$, hence $val(C_0)=0$

The (trivial) [one-dimensional Sperner's Lemma](https://en.wikipedia.org/wiki/Sperner%27s_lemma#One-dimensional_case) implies that there exists $1 \le q \le n$ and two adjacent configurations such that $val(C_{q-1}) =0$ and $val(C_{q})=1$.

The only difference between $C_{q-1}$ and $C_q$ is the state of party $q$ that either receives the messages from $p$ to $q$ or does not receive it in round $k$. In both worlds, consider the extension where $q$'s outgoing messages are delayed forever from round $k+1$. 

As in Lemma 1, the configurations  $C_{q-1} - q$ and $C_q -q$ are indistinguishable for all non-$q$ parties. Because in both worlds no party hears from party $q$ in round $k+1$ or later so it does not matter what party $q$ saw in round $k$. So


$$val(C_{q-1} - q)=val(C_q - q)$$ 

If this value is 1, then $C_{q-1}$ is a $q$-pivot configuration at the beginning of round $k+1$. Otherwise, if this value is 0 then $C_q$ is a $q$-pivot configuration at the beginning of round $k+1$. This completes the proof.

## Extending the proof to non-uniform agreement

Consider the execution which proceeds through an infinite series of pivot configurations. Assume by way of contradiction that some round $k$ in this execution is the first round in which at least two different parties decide on a value before the beginning of round $k$.

Let $C$ be the $p$-pivot configuration in the beginning of round $k$. At least one of the two deciding parties is not the pivot $p$ of the round $k$. If party $q\neq p$ decided $val(C)$ before the beginning of round $k$, crash $p$ in round $k$ to reach a contradiction. Otherwise, party $q$ decides $val(C-p)$, in which case we continue the execution without faults to reach the contradiction.

Note that this argument above holds for non-uniform agreement:

* **Agreement**: all decision values from eventually non-faulty parties are the same.

## Reductions from mobile delay to asynchrony and mobile crash

The following claims are almost immediate, we provide them for completeness:

**Claim 1**: If there is a protocol that is resilient to one crash in asynchrony, then there is a protocol resilient to one mobile delay in lock step.

*Proof of claim 1*: Assume there is an asynchronous protocol that is resilient to $1$ crash and let there be some adversary to the mobile delay protocol. If messages from party $q$ are delayed for any finite amount in the mobile delay setting, we can simulate this via an asynchronous environment that delays these messages by that amount. If a party is indefinitely delayed at some point in the execution, then the asynchronous adversary can simulate this by crashing this party at that point in the execution. Since this is a possible execution in the asynchronous environment, the protocol is resilient to this (arbitrary) mobile delay adversary.

**Claim 2**: If there is a protocol that is resilient to one mobile crash in synchrony, then there is a protocol resilient to one mobile delay in lock step.

*Proof of claim 2*: Mobile crash has more power because it erases the messages sent after the crash, while mobile delay just delays them. So a mobile crash protocol can be transformed into a mobile delay protocol, by instructing parties to ignore any message they receive late and running the original protocol (thus simulating crashes).

The theorems at the top of this post follow from Claims 1 and 2 and the existence of infinite execution in the mobile delay lock-step model.

## Related work and acknowledgments

Our proof initially followed the [Layered Analysis of Consensus, 2002](http://courses.csail.mit.edu/6.897/fall04/papers/Moses/layering.pdf) by [Moses and Rajsbaum](https://epubs.siam.org/doi/10.1137/S0097539799364006), with simplifications for maintaining just two configurations. Following feedback from [Gafni and Losa](https://dl.acm.org/doi/abs/10.1007/978-3-031-44274-2_6), we adopt the insights of [Time is not a Healer, but it Sure Makes Hindsight 20:20, 2023](https://arxiv.org/abs/2305.02295) which is based on the work of [Volzer, 2004](https://citeseerx.ist.psu.edu/document?repid=rep1&type=pdf&doi=043ac773bfcc3adb84dcdad6e726f2096a742f5b) and maintains just one configuration. 

Gafni and Losa prove an even stronger result, showing that synchronous single mobile crash and asynchronous single crash are equivalent in the sense that they can simulate each other (and showing two additional equivalent models).


## Notes

* The mobile delay adversary is used as a base for reductions to both the mobile crash and the asynchronous case. This highlights how little asynchrony is needed and the deep connection between asynchrony and mobile faults. 
* Compared to the FLP proof via [bi-valency](https://decentralizedthoughts.github.io/2019-12-15-asynchrony-uncommitted-lower-bound/), this proof is more constructive in showing a fair execution. The FLP notion of [bi-valency](https://citeseerx.ist.psu.edu/document?repid=rep1&type=pdf&doi=043ac773bfcc3adb84dcdad6e726f2096a742f5b) may not be the most natural definition for proving these results.
* Compared to the *Almost Same but Failure Free different* notion of our post on [early stopping](https://decentralizedthoughts.github.io/2024-01-28-early-stopping-lower-bounds/), here we maintain just one configuration instead of two. However, the proofs are very similar. It currently seems that early stopping needs to maintain two configurations because it needs to reason about a configuration that is one round in the future.
* The constructive round by round nature of this proof approach shows that all the adversary needs to do is guess the pivot and its action (which can be done with probability $1/2n$ each round). This immediately shows that any protocol (even a randomized one and even one that uses fancy cryptography) that runs for at most $c$ rounds must have an error probability of at least $(2n)^{-c} (1/2)$.

Please leave comments on [Twitter](https://x.com/ittaia/status/1772026991111217657).
