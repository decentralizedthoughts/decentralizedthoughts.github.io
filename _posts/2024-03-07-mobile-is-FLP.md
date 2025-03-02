---
title: Consensus with One Mobile Crash in Synchrony or One Crash in Asynchrony Must
  Have Infinite Executions
date: 2024-03-07 12:05:00 -05:00
tags:
- lowerbound
author: Ittai Abraham and Gilad Stern
---

In a consensus protocol, parties have an input (with at least two possible values, such as 0 or 1) and must output a decision value that satisfies the following properties:

* **Uniform Agreement**: all decision values are the same.
* **Validity**: if all inputs are the same, then this is the output value.

The third property is **Termination**, and the following two influential lower bounds correspond to two [Dijkstra prizes](https://www.podc.org/dijkstra/) (awarded in [2001](https://www.podc.org/influential/2001-influential-paper/) and [2024](https://www.podc.org/2024-edsger-w-dijkstra-prize-in-distributed-computing/)) on fundamental limits to termination properties:

**Theorem [[FLP83](https://decentralizedthoughts.github.io/2019-12-15-asynchrony-uncommitted-lower-bound/)]**: any protocol solving consensus in an asynchronous model that is resilient to one crash failure must have an infinite execution.

**Theorem [[SW89](https://dl.acm.org/doi/10.5555/73228.73254)]**: any protocol solving consensus in a synchronous model that is resilient to one mobile crash failure must have an infinite execution.

We prove both results via *reduction* to a common weaker adversary we call the ***mobile delay adversary*** in synchrony with a single failure and then prove that any consensus protocol resilient to it must have infinite executions. This gives a rather simple and unified proof, for both a **single mobile crash in synchrony** and a **single crash in asynchrony**.


## Definitions 

A *configuration* is a set of all the states of all the parties and the set of currently undelivered messages.

***Definition 1***: For a configuration $C$ let $E(C)$ be the *failure-free extension* that starts with configuration $C$ and runs in lockstep synchrony with no failures. In particular, all pending messages in $C$ arrive immediately, and all messages sent after that arrive after one lockstep delay.


***Definition 2***: For a configuration $C$, let $val(C)$ be the decision value in the execution $E(C)$.

Note that $val(C)$ is well-defined if $E(C)$ reaches a decision - if it does not terminate then we have found a non-terminating execution.

***Definition 3***: For a configuration $C$ and a party $p$, let $E(C-p)$ be the execution that starts with configuration $C$, crashes $p$, and then runs in lockstep synchrony with no failures. In particular, all pending messages in $C$ arrive immediately, and all message sent after $p$ crashes arrive after one lockstep delay.

***Definition 4***: For a configuration $C$, let $val(C-p)$ be the decision value in the execution $E(C-p)$.

Similarly, $val(C-p)$ is well-defined if $E(C-p)$ reaches a decision - if it does not terminate then we have found a non-terminating execution.

We are now ready for a key definition:

***Definition of a $p$-pivot configuration:*** For a party $p$ we say that a configuration $C$ is a $p$-pivot if $val(C) \neq val (C-p)$.

In words, a $p$-pivot configuration is a configuration where the decision value of its failure-free extension is *different* from the decision value of its extension where no party sees any message from $p$ after $c(p)$ and all others are failure-free. Compared to the definition of bi-valency, this definition is more explicit and constructive in terms of the extensions that lead to opposing decision values.

## Mobile delay adversary

The mobile delay adversary with one failure, in lockstep, at each round, can choose one party to *delay* some of its messages. Once a party is delayed, its remaining outgoing messages suffer one additional round of delay. The adversary can delay a party at any point in the round. So for example it can delay all the outgoing messages, or only the last outgoing message, etc.

Note that the adversary can continue to delay the same party for any finite number of rounds and this is essentially equivalent to crashing the party.

## Mobile delay adversary lower bound

Not surprisingly, we start by showing that some initial configuration must be a $p$-pivot configuration.

***Lemma 1***: *Any consensus protocol that is resilient to at least 1 mobile delay failure has a $p$-pivot initial configuration.*

*Proof*: For $0 \leq i \le n$ let $C_i$ be the initial configuration where parties 1 to $i$ have input 1 (empty set for $i=0$) and the rest have input 0.  From validity, $val(C_0)=0$ and $val(C_n)=1$, so the (trivial) [one-dimensional Sperner's Lemma](https://en.wikipedia.org/wiki/Sperner%27s_lemma#One-dimensional_case) implies that there exists $1 \le i \le n$ and two adjacent configurations such that $val(C_{i-1}) =0$ and $val(C_{i})=1$.

Note that the only difference between $E(C_{i-1})$ and $E(C_i)$ is the initial value of party $i$. Consider executions where party $i$ crashes (is delayed forever) at the beginning of the execution. Since there is no way to know the state of party $i$, we have

$$val(C_{i-1}-i)=val(C_i-i)$$

If this value is 1 then $C_{i-1}$ is an $i$-pivot configuration and similarly if this value is 0 then $C_i$ is an $i$-pivot configuration. This completes the proof.

We now show that we can always extend a $p$-pivot configuration $C$ by $\ell \geq 1$ rounds to a $p'$-pivot configuration $C'$, thus creating an infinite execution. In each *round* of this infinite execution, all parties progress in lockstep except for at most one party which we may delay its outgoing messages for a finite time.

***Lemma 2***: *If $C$ is a $p$-pivot configuration at the beginning of round $k$, then there is an extension of $C$ to $C'$ by \ell \geq 1$ rounds in the mobile delay model where $C'$ is a $p'$-pivot configuration, where $p' \neq p$.*

*Proof*: Given a $p$-pivot configuration $C$ at the beginning of round $k$:


For any $\ell$, let $C_{k+\ell}$ be the configuration that extends $C$ for $\ell$ rounds of lock step with no errors except for party $p$. For party $p$, any outgoing message at $C$ is immediately delivered, but all other outgoing messages that $p$ sends afterwards are delayed and arrive only at the end of round $k+\ell$.

Observe that the view of any party $\neq p$ after $C$ but before $C_{k+\ell}$ is as if party $p$ crashed after $C$.

Since $C$ is a $p$-pivot configuration, there must be some finite delay $L$ such that all parties decide $val(C-p) \neq val(C)$. So define $D=C_{k+\ell}$ as the configuration with the minimal $\ell$ for which $val(D) = val(C-p) \neq val(C)$. Since $val(C_{k+0})=val(C)$, it must be that $\ell>0$.

By the minimality of $D$, $val(C_{k+\ell-1})=val(C)$.

Consider the $n+1$ configurations $D_0,D_1,\dots,D_n$ where $D_j$ is the configuration that extends $C_{k+\ell-1}$ by one round, in which the adversary causes $p$'s outgoing messages to arrive to the parties $\{i \mid 0<i\le j\}$, and delays all other $p$'s outgoing messages by one round. 

By definition, $D_0$ is equal to $D$. Hence $val(D_0)=val(D) \neq val(C)$

Also by definition, $D_n$ is equal to $C_{k+\ell-1}$. Hence $val(D_n)=val(C_{k+\ell-1})=val(C)$.

The (trivial) [one-dimensional Sperner's Lemma](https://en.wikipedia.org/wiki/Sperner%27s_lemma#One-dimensional_case) implies that there exists $1 \le q \le n$ and two adjacent configurations such that $val(D_{q-1}) \neq val(D_{q})$.

The only difference between $D_{q-1}$ and $D_q$ is the state of party $q$ that either receives the messages from $p$ to $q$ or does not receive it in round $k+\ell$. In both worlds, consider the extension where $q$'s outgoing messages are delayed forever from round $k+\ell+1$. 

As in Lemma 1, the executions  $E(D_{q-1} - q)$ and $E(D_{q} -q)$ are indistinguishable for all non-$q$ parties. Because in both worlds no party hears from party $q$ in round $k+\ell+1$ or later so it does not matter what message party $q$ received in round $k+\ell$.

So

$$
val(D_{q-1} - q)=val(D_q - q)
$$ 

Without loss of generality, if this value is 1, then $D_{q-1}$ is a $q$-pivot configuration at the beginning of round $k+\ell+1$. Otherwise, if this value is 0 then $D_q$ is a $q$-pivot configuration at the beginning of round $k+\ell+1$. This completes the proof.



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

## Acknowledgments

We would like to thank Tim Roughgarden for insightful comments and for finding and fixing a major error in a previous version of the proof of Lemma 2.

Please leave comments on [Twitter](https://x.com/ittaia/status/1772026991111217657).
