---
title: 'Consensus tolerating one mobile crash in synchrony or one crash is asynchrony must have infinite executions for the same simple reason'
date: 2024-03-07 12:05:00 -05:00
tags:
- lowerbound
author: Ittai Abraham and Gilad Stern
---

In a consensus protocol parties have an input (at least two possible values, say 0 or 1) and may output a decision value such that:

* **Uniform Agreement**: all decision values are the same.
* **Validity**: if all inputs are the same, then this is the output value.

The third property is **Termination**, and the following lower bounds are known:

**Theorem [[FLP83](https://decentralizedthoughts.github.io/2019-12-15-asynchrony-uncommitted-lower-bound/)]**: any protocol solving consensus in an asynchronous model that is resilient to one crash failure must have an infinite execution.

**Theorem [[SW89](https://dl.acm.org/doi/10.5555/73228.73254)]**: any protocol solving consensus in a synchronous model that is resilient to one mobile crash failure must have an infinite execution.

We prove both results by a *reduction* to a common weaker adversary we call the ***mobile delay adversary*** in synchrony with a single failure and then prove that any consensus protocol resilient to it must have infinite executions. This gives a rather simple and unified proof, for both mobile crash and asynchrony.

Our proof initially followed the [Layered Analysis of Consensus, 2002](http://courses.csail.mit.edu/6.897/fall04/papers/Moses/layering.pdf) by [Moses and Rajsbaum](https://epubs.siam.org/doi/10.1137/S0097539799364006), with simplifications for maintaining just two configurations. Following feedback from Eli and Giuliano, we adopt the insights of [Time is not a Healer, but it Sure Makes Hindsight 20:20, 2023](https://arxiv.org/abs/2305.02295) by [Gafni and Losa](https://dl.acm.org/doi/abs/10.1007/978-3-031-44274-2_6). This approach is based on the work of [Volzer, 2004](https://citeseerx.ist.psu.edu/document?repid=rep1&type=pdf&doi=043ac773bfcc3adb84dcdad6e726f2096a742f5b) and requires to maintain just one configuration. An interesting takeaway from these approaches is the understanding that the FLP notion of [bi-valency](https://citeseerx.ist.psu.edu/document?repid=rep1&type=pdf&doi=043ac773bfcc3adb84dcdad6e726f2096a742f5b) may not be the most natural definition for proving these results.

## Definitions 

We follow the definitions of Volzer and of Gafni and Losa:

A *configuration* is a set of all the states of all the parties and the set of undelivered messages.

***Definition***: For a configuration $C$ let $val(C)$ be the decision in the failure free extension that starts with configuration $C$.

***Definition***: For a configuration $C$ and party $p$ let $val(C-p)$ be the decision in the extension that starts with configuration $C$ in which party $p$ is infinitily delayed (essentailly crashed).

***Definition of a $p$-pivot configuration:*** For a party $p$ we say that a configuration $C$ is a $p$-pivot if $val(C) \neq val (C-p)$.

Compared to bi-valency, this definition is more explicit and constructive in terms of the extensions that lead to opposing decision values.

## Mobile delay adversary

The mobile delay adversary with one failure, in lock step, in each round, can choose one party to *delay*. Once a party is delayed, its remaining outgoing messages suffer one additional round of delay. The adversary can corrupt a party with a delay at any point in the round.

Note that the adversary can continue to delay the same party indefinitely and this is equivalent to crashing the party. 


## Mobile delay adversary lower bound

Not surprisingly, we start by showing that some initial configurations must be a $p$-pivot configuration.

***Lemma 1***: *Any consensus protocol that is resilient to at least 1 mobile delay failure has a $p$-pivot  initial configuration.*

*Proof*: For $0 \leq i \le n$ let $C_i$ be the initial configuration where parties 1 to $i$ have input 1 (empty set for $i=0$) and the rest have input 0.  From validity, $val(C_0)=0$ and $val(C_n)=1$, so the (trivial) [one dimension Sperner's Lemma](https://en.wikipedia.org/wiki/Sperner%27s_lemma#One-dimensional_case) implies that there exists $1 \le i \le n$ and two ajecent configurations such that $val(C_{i-1}) =0$ and $val(C_{i})=1$.

Note that the only difference between $C_{i-1}$ and $C_i$ is the initial value of party $i$. Let $C'$ be the execution where party $i$ crashes (is delayed forever) at the beginning of the execution. Critically, $C'$ could be reached from either $C_{i-1}$ or $C_i$ and all parties' views would be indistinguishable. So we have 

$$val(C')=val(C_{i-1}-i)=val(C_i-i)$$ 

So by definition if $val(C')=1$ then $C_{i-1}$ is an $i$-pivot configuration and similarlty if $val(C')=0$ then $C_i$ is an $i$-pivot configuraiton. This completes the proof.

As expected, we now show we can always extend a $p$-pivot configuration by one round to a $p'$-pivot configuration, thus creating an infinite execution.


***Lemma 2***: *If $C$ is a $p$-pivot configuration at the beginning of round $k$, then there is an extension of $C$ to $C'$ by one round in the mobile delay model where $C'$ is a $p'$-pivot configuration.*


*Proof*: Given a $p$-pivot configuration $C$, consider the extension to $D$ by the delay of party $p$ in the beginning of round $k$.

Case 1 (trivial): If $val(D) \neq val(D-p)$ then $D$ is a $p$-pivot configuration and we are done.

Case 2: Otherwise $val(D) = val(D-p)$. From the definition of $D$, $val (C-p)=val(D-p)$. From the assumption on $C$, $val(C-p) \neq val(C)$. We conclude that $val(D) \neq val (C)$. Without loss of generality assume that $val(D)=0$, hence $val(C)=1$.

So consider the $n+1$ configurations $D=C_0,C_1,\dots,C_n=C$ where $C_j$ is the configuration in which the adversary delays party $i$ after it sends its messages to $j$ parties. 

The (trivial) [one dimension Sperner's Lemma](https://en.wikipedia.org/wiki/Sperner%27s_lemma#One-dimensional_case) implies that there exists $1 \le i \le n$ and two ajecent configurations such that $val(C_{i-1}) =0$ and $val(C_{i})=1$.

As in the previous lemma, the only difference between $C_{i-1}$ and $C_i$ is the state of party $i$. Let $C'$ be the execution where party $i$ crashes (is delayed forever) at the beginning of round $k$. Like before, $C'$ could be reached from either $C_{i-1}$ or $C_i$ with all parties' views being indistinguishable. So again we have 

$$val(C')=val(C_{i-1}-i)=val(C_i-i)$$ 

By definition, if $val(C')=1$ then $C_{i-1}$ is an $i$-pivot configuration and similarlty if $val(C')=0$ then $C_i$ is an $i$-pivot configuraiton. This completes the proof.

## Completing the proof and extending to non-uniform agreement

We can now observe the execution which proceeds through an infinite series of $p$-pivot configurations (with different $p$'s). Assume by way of contradiction that at some point in this execution, $2$ different parties decide on a value. At least one of them is not the pivot $p$ of the round in which they both first decided. If that party outputs $val(C)$ for that configuration, simply crash $p$ to reach a contradiction.
Otherwise, the party output $val(C-p)$, in which case we continue the execution without faults to reach the contradiction.

The lower bound also holds for non-uniform agreement:

* **Agreement**: all decision values from eventually non-faulty parties are the same.

The trick is to look at the first configuration $C$ where at least *two* parties decide.

By definition, at least one of the parties that decided, $q$, is not the $p$-pivot of $C$ hence we can generate an agreement violation for $q$ by either running $C$ or $C-p$, which means that $q$ is eventually non-faulty.

## Reductions from mobile delay to asynchrony and mobile crash

The following claims are almost immediate, we provide them for completeness:

**Claim 1**: If there is a protocol that is resilient to one crash in asynchrony, then there is a protocol resilient to one mobile delay in lock step.

*Proof of claim 1*: Assume there is an asynchronous protocol that is resilient to $1$ crash and let there be some adversary to the mobile delay protocol. If messages from party $q$ are delayed for any finite amount in the mobile delay setting, we can simulate this via an asynchronous environment that delays these messages by that amount. If a party is indefinitely delayed at some point in the execution, then the asynchronous adversary can simulate this by crashing this party at that point in the execution. Since this is a possible execution in the asynchronous environment, the protocol is resilient to this (arbitrary) mobile delay adversary.

**Claim 2**: If there is a protocol that is resilient to one mobile crash in synchrony, then there is a protocol resilient to one mobile delay in lock step.

*Proof of claim 2*: Mobile crash has more power because it erases the messages sent after the crash, while mobile delay just delays them. So a mobile crash protocol can be transformed into a mobile delay protocol, by instructing parties to ignore any message they receive late and running the original protocol (thus simulating crashes).

The theorems at the top of this post follow from Claims 1 and 2 and the existence of infinite execution in the mobile delay lock step model.

Gafni and Losa prove an even stronger result, showing that synchronous single mobile crash and asynchronous single crash are equivalent in the sense that they can simulate each other (and showing two additional equivalent models).


## Notes

* The mobile delay adversary is used as a base for reductions to both the mobile crash and the asynchronous case. This highlights how little asynchrony is needed and the deep connection between asynchrony and mobile faults. 
* Compared to the FLP proof via [bi-valency](https://decentralizedthoughts.github.io/2019-12-15-asynchrony-uncommitted-lower-bound/), this proof is more constructive in showing a fair execution.
* Compared to the Almost Same but Failure Free different notion of our post on [early stopping](https://decentralizedthoughts.github.io/2024-01-28-early-stopping-lower-bounds/), here we maintain just one configuration instead of two but the proofs are very similar. It currently seems that early stopping needs to maintain two configurations because it needs to reason about a configuration that is one round in the future.
* The constructive round by round nature of this proof approach shows that all the adversary needs to do is guess the pivot and its action (which can be done with probability $1/2n$ each round). This immediately shows that any protocol (even a randomized one and even one that uses fancy cryptography) that runs for at most $c$ rounds must have an error probability of at least $(2n)^{-c} (1/2)$.

Please leave comments on [Twitter](...).