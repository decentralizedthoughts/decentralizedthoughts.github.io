---
title: Living with asynchrony and eventually reaching agreement by combining binding
  and randomness
date: 2024-12-10 03:00:00 -05:00
tags:
- dist101
- asynchrony
author: Ittai Abraham, Gilad Stern
---

The prevailing view on fault-tolerant agreement is that it is impossible in asynchrony for deterministic protocols, but adding randomization solves the problem. This statement is confusing in two aspects:

1. The FLP result says that any protocol, even a randomized protocol, must have a non-terminating execution where every configuration is bivalent (or uncommitted or is a [pivot configuration](https://decentralizedthoughts.github.io/2024-03-07-mobile-is-FLP/)). The difference is that in a randomized protocol, the probability of non-terminating executions may be small. Non-termination may even be a zero-probability event ([almost surely](https://en.wikipedia.org/wiki/Almost_surely) termination).
2. It’s not clear why using randomness helps without binding; what is needed is a delicate interplay between **binding the adversary** and then causing them to **fail with probability $\geq \alpha$** using **unpredictable randomness**. Here failure means that the protocol reaches a **univalent configuration** where the decision value is fixed.

The focus of this post is on this second point: the subtle interplay of both binding and randomization to achieve termination in finite expected [number of rounds](https://decentralizedthoughts.github.io/2021-09-29-the-round-complexity-of-reliable-broadcast/). 


We present a framework that is common to all asynchronous agreement protocols that we are aware of (for both crash failures and Byzantine failures) and works even with a strongly adaptive adversary. We first discuss some concrete examples.

## Examples of solving agreement in asynchrony using binding before revealing the randomness:

* In binary agreement protocols (see this series [1](https://decentralizedthoughts.github.io/2022-03-30-asynchronous-agreement-part-one-defining-the-problem/), [2](https://decentralizedthoughts.github.io/2022-03-30-asynchronous-agreement-part-two-ben-ors-protocol/), [3](https://decentralizedthoughts.github.io/2022-03-30-asynchronous-agreement-part-three-a-modern-version-of-ben-ors-protocol/), [4](https://decentralizedthoughts.github.io/2022-04-05-aa-part-four-CA-and-BCA/), [5](https://decentralizedthoughts.github.io/2022-04-05-aa-part-five-ABBA/)) the binding protocol forces the adversary to choose $B \in \\{0,1\\}$. The protocol reaches a univalent state (decision) if the common coin $r$ equals $B$. It is critical that the choice of the bound value $B$ is done before knowing the coin value.
* In multi-value Byzantine agreement protocols that use a randomness beacon (like [VABA](https://arxiv.org/abs/1811.01332)), the binding protocol often forces the adversary to choose $B$ as a set of $n-f$ parties (or $f+1$ honest parties) that completed some step. The protocol reaches a univalent state if the randomness beacon outputs a leader that is in this set. Again, it is critical that the choice of the set $B$ is done before knowing the output of the randomness beacon.
* In multi-value Byzantine agreement protocols (like [NWH](https://arxiv.org/abs/2102.09041)) that  build randomness from verifiable secret sharing (VSS), the binding protocol often forces the adversary to choose a *core set* $B$ as a set of $n-f$ parties (or $f+1$ honest parties). This is often done via a [binding gather protocol](https://decentralizedthoughts.github.io/2024-01-09-gather-with-binding-and-verifiability/). The binding and hiding properties of the VSS are used to fix all the required randomness to guarantee the $\alpha$-correctness and unpredictability properties. The protocol reaches a univalent state if the randomness of the VSS causes all non-faulty parties to choose the same leader (or proposal) that is a member of this core set $B$. Here too, it is critical that the choice of the core set $B$ is done before seeing the output of the relevant VSS values.

## The abstract framework: combination of Binding and Randomization

The high-level idea is simple: first force the adversary to bind to some choice, then reveal a random value that will cause the adversary to fail with some probability. We will make this formal in this section.


We use two protocols: a binding protocol and a common randomness protocol. For the binding protocol, assume a set $\mathcal{B}$ of possible binding values.  

Our goal is to reach a configuration where the decision value is fixed (a univalent or [committed configuration](https://decentralizedthoughts.github.io/2019-12-15-consensus-model-for-FLP/)).

The first protocol is the **binding protocol**, with the following properties:

1. *Liveness*: if all non-faulty start the binding protocol, then all non-faulty will complete it.
2. *Binding*: at the time the first non-faulty completes the protocol, the adversary must fix some choice $B \in \mathcal{B}$. This choice is a function of the view of all the non-faulty parties. The effect of this choice is defined below.

The second protocol is the **common randomness protocol**, it has the following properties:

1. *Liveness*: if all non-faulty start the common randomness protocol, then all non-faulty will complete it and output some value.
2. *Univalency*: For any choice $B \in \mathcal{B}$, there exists some event $G_B$ that happens when the first non-faulty completes the common randomness protocol that causes the execution to be univalent (reach a [committed configuration](https://decentralizedthoughts.github.io/2019-12-15-consensus-model-for-FLP/) where the decision value is fixed). 
3. *$\alpha$-Correctness*: There exists some $\alpha$ such that for any $B \in \mathcal{B}$, the probability of $G_B$ given $B$ is at least $\alpha$. i.e. $\exists \alpha, \forall B \in \mathcal{B}, \Pr[G_B \mid B] \ge \alpha$.   
4. *Unpredictability*: For any choice $B \in \mathcal{B}$ and any (poly-time) adversary that is using its view before the first non-faulty completes the common randomness protocol, the probability of guessing if $G_B$ will occur given $B$ is at most $\alpha$ (or negligibly better).  


## Notes

* The correctness property defines the expected run time. Assuming the number of rounds for the binding protocol and the common randomness protocol is both constant, then the expected number of rounds till reaching agreement is $O(1/\alpha)$. This is because reaching a univalent configuration is essentially a Bernoulli random variable with parameter $\alpha$.
* The binding property implies the existence of an extractor that can extract the binded value at the time the first non-faulty completes the binding protocol.
* The unpredictability property is often proven by proving a stronger property, like the unpredictability of the [common coin](https://decentralizedthoughts.github.io/2022-04-05-aa-part-five-ABBA/), or of the random beacon value, or the unpredictability of the random rank of some parties (in particular those in the core).

Your thoughts on [X](https://x.com/ittaia/status/1866421772838383981).