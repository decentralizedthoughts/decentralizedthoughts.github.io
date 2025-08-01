---
title: Authenticated Synchronous BFT
date: 2019-11-11 03:01:00 -05:00
tags:
- research
author: Kartik Nayak, Ittai Abraham, Ling Ren
---

<span style="color:grey"> ![](https://github.githubassets.com/images/icons/emoji/unicode/23f0.png?v8) Post updated in March 2021</span>


Different modeling assumptions under which we construct BFT protocols often make it hard to compare two protocols and understand their relative contributions. In this post we discuss *[synchronous](https://decentralizedthoughts.github.io/2019-06-01-2019-5-31-models/)* protocols in the *[authenticated](https://decentralizedthoughts.github.io/2019-07-18-setup-assumptions/)* model (assuming a PKI).

A protocol runs in the [synchronous model](https://decentralizedthoughts.github.io/2019-06-01-2019-5-31-models/) if it assumes a **bounded message delay**, i.e., all messages will arrive within a bounded delay of $\Delta$. A common strengthening of the synchronous model is *lock-step* synchrony, i.e., replicas execute the protocol in rounds in a synchronized manner. A message sent at the start of a round arrives by the end of the round.

### Is the synchronous model practical?
The short answer is, it's hard to say. For practitioners, the synchrony assumption may seem strong for several reasons. First, if the bounded-message delay assumption does not hold *even* for a single message between honest parties, then we may have a safety violation. Second, lock-step execution may be hard to implement in practice. Finally, waiting for multiple rounds/$\Delta$’s implies a high latency to commit. On the other hand, research in the synchronous setting has been improving all of these aspects to bring synchrony closer to practice.

### The advantage of synchrony: tolerating a minority corruption
The [DLS](https://decentralizedthoughts.github.io/2019-06-25-on-the-impossibility-of-byzantine-agreement-for-n-equals-3f-in-partial-synchrony/) lower bound implies that we can tolerate at most one-third corruption with weaker assumptions such as partial synchrony/asynchrony.
The synchronous model, together with digital signatures or PoW, can tolerate up to minority corruption.

### Comparing authenticated synchronous BFT protocols
To evaluate and compare authenticated synchronous protocols we analyze them in the following dimensions:
1. *Consensus definition.* Whether the protocol was intended to solve Byzantine Broadcast ([BB](https://decentralizedthoughts.github.io/2019-06-27-defining-consensus/)), Byzantine Agreement ([BA](https://decentralizedthoughts.github.io/2019-06-27-defining-consensus/)), or State Machine Replication ([SMR](https://decentralizedthoughts.github.io/2019-10-15-consensus-for-state-machine-replication/)).
2. *Lock-step vs bounded-message delay.* Whether the protocol requires a lock-step execution of replicas, or can they rely only on bounded-message delay.
3. *Latency to commit.* For protocols with lock-step execution, the (expected) latency is measured in the number of \#rounds to commit. For protocols that only assume bounded-message delay, the (expected) latency is measured in terms of $\Delta$. For protocols in SMR that use the [steady-state-and-view-change paradigm](https://decentralizedthoughts.github.io/2019-10-15-consensus-for-state-machine-replication/), we mention the latency as a tuple of (steady state time to commit, expected time to arrive at the next steady state through view changes).
4. *Communication complexity.* The (expected) number of signatures sent by honest parties. Wherever applicable, the message complexity is described assuming the presence of threshold signatures.
5. *Optimistic responsiveness (OR).* Some protocols can commit in time independent of $\Delta$ when certain *optimistic* conditions hold. e.g., the actual number of Byzantine behaving parties is less than $n/4$. We discuss this further in a [separate post](https://decentralizedthoughts.github.io/2020-06-12-optimal-optimistic-responsiveness/).
6. *Adaptive adversary.* Is the protocol resilient to an [adaptive adversary](https://decentralizedthoughts.github.io/2019-06-07-modeling-the-adversary/)?

|                                                                                                                               | Defn  | Lock-step? | Latency                                             | Communication complexity        | OR? | Adaptive? |
|-------------------------------------------------------------------------------------------------------------------------------|-------|------------|-----------------------------------------------------|---------------------------|-----|-----------|
| [LSP \[1982\]](https://people.eecs.berkeley.edu/~luca/cs174/byzantine.pdf)                               | BB/BA | Y          | $O(n)$ rounds                                       | $O(2^n)$                  | N   | Y         |
| [Dolev-Strong \[1982\]](https://www.researchgate.net/publication/220616485_Authenticated_Algorithms_for_Byzantine_Agreement) | BB    | Y          | $O(n)$ rounds                                       | $O(n^2f)$                 | N   | Y         |
| [Katz-Koo \[2006\]](https://eprint.iacr.org/2006/065.pdf)                                                                    | BA    | Y          | $29$ rounds                                         | $O(n^2)$                  | N   | Y         |
| [Micali-Vaikuntanathan \[2017\]](https://dspace.mit.edu/bitstream/handle/1721.1/107927/MIT-CSAIL-TR-2017-004.pdf?sequence=1&isAllowed=y)\* | BB  | Y | $\kappa$ rounds | $O(\kappa n^3)$ | N | Y |
| [Abraham et al. \[2017\]](https://eprint.iacr.org/2018/1028.pdf)                                                                 | BB/BA | Y          | $16$ rounds                                         | $O(n^2)$                  | N   | Y         |
| [XFT \[2016\]](https://www.usenix.org/system/files/conference/osdi16/osdi16-liu.pdf)               | SMR   | N           | ($O(\delta)$, $O({n \choose f} \Delta)$ ) | ($O(n)$, $O{n \choose f}$) | Y    | N         |
| [Dfinity \[2018\]](https://dfinity.org/static/dfinity-consensus-0325c35128c72b42df7dd30c22c41208.pdf)                                                              | SMR   | N          | $9\Delta$                                           | [$O(n^2)$](https://eprint.iacr.org/2018/1153.pdf)                 | N   | N         |
| [PiLi \[2018\]](https://eprint.iacr.org/2018/980.pdf)\*\*                                                                            | SMR   | Y          | $65\Delta$                                         | $O(n^2)$                  | Y   | N         |
| [Sync HotStuff \[2019\]](https://eprint.iacr.org/2019/270.pdf)\*\*                                                                   | SMR   | N          | $(2\Delta, O(\Delta))$                                | $(O(n^2), O(n^2))$        | Y   | N         |
| [OptSync \[2020\]](https://eprint.iacr.org/2020/458.pdf)$^+$ | SMR | N | $((2\delta, 2\Delta), O(\Delta))$ | $(O(n^2), O(n^2))$ | Y | N |
| [Near-optimal Good-case Latency \[2020\]](https://arxiv.org/abs/2003.13155) | SMR | N | $\Delta + 2\delta$ | $(O(n^2), O(n^2))$ | N | N |
| [Optimal Good-case Latency \[2021\]](https://arxiv.org/pdf/2102.07240.pdf)$^{++}$ | BB | N | $(1+\frac{1}{2m})\Delta + 1.5\delta$ | $O(mn^2)$ | N | N |

\* The protocol by Micali and Vaikuntanathan requires $\kappa$ rounds where $\kappa$ is a statistical security parameter and obtains a "player replaceability" notion of adaptive security.

\*\* PiLi and Sync HotStuff also handle a weaker synchrony model with *mobile sluggish faults*.

$^+$ For OptSync, in steady state, we describe the latency for the optimistic case as well as the regular case.

$^{++}$ For the work on optimal good-case latency, we have $m \geq 1$. The parameters are described assuming an *unsynchronized start* between different parties. The latency is optimal when $m \rightarrow \infty$. If different parties start at the same time, the latency is $\Delta + \delta$ and communication complexity is $O(n^3)$.

**Lock-step execution vs. bounded-message delay.** As can be seen in the latency column, lock-step protocols express latency in terms of \#rounds, whereas non-lock-step protocols in terms of $\Delta$.
This distinction is minor in theory (or asymptotically) because one can obtain lock-step execution from a bounded message delay assumption, by merely using a *clock synchronization* protocol such as [Dolev et al.](http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.499.2250&rep=rep1&type=pdf) and [Abraham et al.](https://eprint.iacr.org/2018/1028.pdf).
Specifically, these protocols have $O(n^2)$ message complexity and can synchronize honest parties' clocks within $\Delta$ time.
Thus, using rounds of duration $2\Delta$ suffices to implement lock-step execution.
However, state-of-art non-lock-step protocols can achieve lower latency by avoiding such transformations.

**Remark.** All protocols derived from Nakamoto consensus rely on synchrony. We will discuss them separately [here](https://decentralizedthoughts.github.io/2019-11-29-Analysis-Nakamoto/).

Please leave comments on [Twitter](https://twitter.com/kartik1507/status/1194393359399497733?s=20) 
