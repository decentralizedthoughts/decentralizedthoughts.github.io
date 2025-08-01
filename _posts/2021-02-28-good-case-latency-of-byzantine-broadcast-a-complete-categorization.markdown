---
title: 'Good-case Latency of Byzantine Broadcast: a Complete Categorization'
date: 2021-02-28 13:07:00 -05:00
tags:
- research
- lowerbound
author: Zhuolun Xiang
---

<span style="color:grey"> Guest post by [Zhuolun Xiang](https://sites.google.com/site/danielxiangzl/)  </span>




## State Machine Replication and Broadcast

Many existing permission blockchains are built using *Byzantine fault-tolerant state machine replication (BFT SMR)*, which ensures all honest replicas agree on the same sequence of client inputs. Most of the practical solutions for BFT SMR are based on the **Primary-Backup paradigm**. In this approach, in each view, there is a leader in charge to drive decisions efficiently, until replaced by the next leader. The Primary-Backup approach for SMR exposes deep connections to *broadcast*. Each view in BFT SMR is similar to an instance of broadcast where the leader taking on a similar role as the broadcaster, and hence **an efficient broadcast protocol can be converted to an SMR protocol with similar efficiency guarantees**.



## Good-case Latency


Practical SMR solutions care about the **good case** performance measured as the *latency to commit when the Primary is honest*. For many applications, *latency* is crucial. In a [talk from 2000](https://youtu.be/Uj638eFIWg8?t=800), Barbara Liskov, the author of [PBFT](http://pmg.csail.mit.edu/papers/osdi99.pdf), commented on PBFT needing 3 rounds in the good case:
>I don't know about a minimality proof that would show you require three phases, though I certainly haven't been able to think of a way of doing it with fewer.

Therefore, it is natural and important to ask

{: .box-note}
What is the best latency a BFT SMR can achieve to commit decisions in the good case?


We refer to the above latency notion as *good-case latency*. For broadcast, we similarly define the good-case latency to be the *latency to commit when the broadcaster is honest*.

Somehow surprisingly, the above question has not been formally answered yet. Although a sequence of efforts improves the good-case latency of BFT SMR, there lacks a complete and rigorous characterization of the whole picture. Before we present our results, let's take a quick look at the **existing best solutions** for BFT SMR on the good-case latency. For the synchrony model where the network delay is bounded by $\Delta$, [Sync HotStuff](https://decentralizedthoughts.github.io/2019-11-12-Sync-HotStuff/) commits in $2\Delta$ under $n\geq 2f+1$. For the partial synchrony model where the network delay is bounded only after a Global Stable Time (GST), [PBFT](http://pmg.csail.mit.edu/papers/osdi99.pdf) commits in 3 rounds after GST under $n\geq 3f+1$, and [FaB](https://ieeexplore.ieee.org/document/1467815) commits in 2 rounds after GST under $n\geq 5f+1$. **We show that all these protocols can be improved!**


## Results Overview

### ![](https://github.githubassets.com/images/icons/emoji/unicode/1f4a1.png?v8)  **Theory**
Our **[good-case latency paper](https://arxiv.org/abs/2102.07240)** gives a **complete categorization** of the good-case latency for broadcast, under *synchrony, partial synchrony and asynchrony*. As mentioned, the protocols for broadcast can be converted to BFT SMR with similar good-case latency guarantees. The lower bound results also shed light on what is the limitation of good-case latency for BFT SMR. All of our bounds are **tight** except for just one case, as summarized in the table below (new and non-trivial results are marked bold). 

![](https://i.imgur.com/Okje5V8.png)


- For asynchrony, Byzantine broadcast is impossible and the standard broadcast formulation is *Byzantine reliable broadcast (BRB)*, which has a **tight bound of 2 rounds** for the good-case latency. 
- For partial synchrony, we propose a new broadcast formulation called *partially synchronous Byzantine broadcast (Psync-BB)* that captures a single-shot of BFT SMR protocols like PBFT. We show that **$n\geq 5f-1$ is the tight resilience bound** for solving psync-BB with good-case latency of 2 rounds. Since psync-BB solves a single-shot of BFT SMR, our results directly refute the claim made in [FaB](https://ieeexplore.ieee.org/document/1467815) saying that $n=5f+1$ is the best possible resilience for $2$-round BFT SMR protocols. 
- For synchrony, we reveal a surprisingly rich structure of the good-case latency for Byzantine broadcast (BB). For a more accurate characterization, we adopt the separation of *assumed network delay $\Delta$* and the *actual (unknown) network delay $\delta$*. For instance, 1 round in the bounds for asynchrony and partial synchrony above equals $\delta$, as the protocols can proceed with the network speed. We also distinguish two assumptions about the clock synchronization -- the *synchronized start* case where all parties can start the protocol and local clock at the same time, and the *unsynchronized start* case where all parties start the protocol and local clock within $\Delta$ time of each other. To strengthen the results, all lower bounds assume sync start and all upper bounds assume unsynchronized start, except the case when $n/3<f<n/2$, which is especially interesting as the *tight bounds depend on the clock synchronization assumption*, and for unsynchronized start the tight bound is $\Delta+1.5\delta$, *not even an integer multiple of the delay*!



### ![](https://github.githubassets.com/images/icons/emoji/unicode/1f680.png?v8) **Practice**
For the practical side, the investigation on good-case latency leads to **better BFT SMR protocols** over [PBFT](http://pmg.csail.mit.edu/papers/osdi99.pdf), [FaB](https://ieeexplore.ieee.org/document/1467815), and [Sync HotStuff](https://decentralizedthoughts.github.io/2019-11-12-Sync-HotStuff/) in terms of good-case latency. 
- For partial synchrony, we obtain a **[2-round BFT SMR](https://arxiv.org/abs/2102.07932)** protocol that only requires $n\geq 5f-1$. Our protocol refutes the claim made in [FaB](https://ieeexplore.ieee.org/document/1467815) saying that $n=5f+1$ is the best possible resilience for $2$-round BFT SMR protocols. Interestingly, for the canonical example with $n=4$ and $f=1$, we can have a 2-round PBFT protocol with the optimal resilience!
- For synchrony, we obtain a **[$1\Delta$-SMR](https://arxiv.org/abs/2003.13155)** protocol that commits in $\Delta+2\delta$ with $n\geq 2f+1$, reducing the commit latency (which is $2\Delta$) of [Sync HotStuff](https://decentralizedthoughts.github.io/2019-11-12-Sync-HotStuff/) by almost half when $\delta\ll\Delta$.



## Protocols and Impossibility Proofs
Check out our [next post](https://decentralizedthoughts.github.io/2021-03-03-2-round-bft-smr-with-n-equals-4-f-equals-1/) and the [next one](https://decentralizedthoughts.github.io/2021-03-09-good-case-latency-of-byzantine-broadcast-the-synchronous-case/)!

Please answer/discuss/comment/ask on [Twitter](https://twitter.com/ittaia/status/1366106073145442304?s=20).


