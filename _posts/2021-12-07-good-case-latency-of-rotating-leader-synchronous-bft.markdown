---
title: Good-case Latency of Rotating Leader Synchronous BFT
date: 2021-12-07 04:39:00 -05:00
tags:
- research
author: Nibesh Shrestha, Ittai Abraha, Kartik Nayak
---

[Synchronous consensus protocols](https://decentralizedthoughts.github.io/2019-11-11-authenticated-synchronous-bft/) can tolerate $f < n/2$ Byzantine failures but for $n/3 <f <n/2$ must depend on the *maximum network delay* $\Delta$ for their safety and progress. So these protocols must *set* $\Delta$ to be much larger than the *actual network delay* $\delta \ll \Delta$. The good news is in the multi-shot (blockchain) scenarios, modern synchronous protocols such as [Sync HotStuff](https://decentralizedthoughts.github.io/2019-11-12-Sync-HotStuff/) can essentially ***pipeline*** the $\Delta$-dependent delay:


* Under an honest leader Sync HotStuff can commit $k$ blocks in $2\Delta+O(k\delta)$ time. 

Protocols such as Sync HotStuff fall under the *stable-leader* paradigm where a single leader coordinates multiple blocks until a *view-change* is executed to replace the faulty leader. In this post, we focus on the [*rotating-leader* paradigm](https://decentralizedthoughts.github.io/2019-06-23-what-is-the-difference-between/) where the leader is rotated after every proposal. The stable-leader approach typically provides better performance metrics. The rotating-leader approach provides better *fairness and censorship resistance* and overall more uniform distribution of work. Our main result shows that:
* Under a sequence of $k$ consecutive honest leaders our protocol can commit $k$ blocks in $2\Delta+O(k\delta)$ time.



In our [paper](https://eprint.iacr.org/2021/1138.pdf), we provide tight upper and lower bounds:

1. A lower bound showing that an optimistically responsive rotating-leader protocol tolerating $f < n/2$ Byzantine faults must have a commit latency for a single slot of at least $2\Delta$ time.
2. An optimistically responsive synchronous BFT protocol tolerating $f < n/2$ Byzantine faults in the rotating-leader paradigm with a commit latency of $2\Delta + O(\delta)$.

Combing these two results shows that committing $k$ blocks in $2\Delta+O(k\delta)$ time under a sequence of $k$ consecutive honest leaders is asymptotically optimal (when $\delta$ is negligible).  


![](https://i.imgur.com/xqg7ZRJ.png)




<!---
This [previous post](https://decentralizedthoughts.github.io/2021-02-28-good-case-latency-of-byzantine-broadcast-a-complete-categorization/) discusses the notion of *good-case latency*, to capture latency to *commit a decision* when the designated sender or leader is *honest*. The [Sync hotstuff paper](https://eprint.iacr.org/2019/270.pdf) observes that the DLS lower bound implies that any synchronous consensus protocol tolerating $f < n/2$ Byzantine failures must incur at least $\Delta$ time to commit a decision. This [follow-up post](https://decentralizedthoughts.github.io/2021-03-09-good-case-latency-of-byzantine-broadcast-the-synchronous-case/) discusses a Byzantine fault tolerant state machine replication (BFT SMR) protocol with a good-case latency of $\Delta + O(\delta)$ latency which is optimal. Such protocols fall under a *stable-leader* paradigm where a *single leader* coordinates the participating replicas into reaching consensus. In general, stable-leader protocols are generally favored for their high throughput and better latency as they avoid a complicated and expensive *view-change* phase as long as the current leader is honest.
-->


## Background and Related Work

An [earlier post](https://decentralizedthoughts.github.io/2021-02-28-good-case-latency-of-byzantine-broadcast-a-complete-categorization/) discusses the notion of *good-case* latency to capture commit latency in the stable-leader paradigm. A [follow-up post](https://decentralizedthoughts.github.io/2021-03-09-good-case-latency-of-byzantine-broadcast-the-synchronous-case/) discusses a Byzantine fault tolerant state machine replication (BFT SMR) protocol with a good-case latency of $\Delta + O(\delta)$ latency which is optimal.
<!--- The [Sync hotstuff paper](https://eprint.iacr.org/2019/270.pdf) observes that the DLS lower bound implies that any synchronous consensus protocol tolerating $f < n/2$ Byzantine failures must incur at least $\Delta$ time to commit a decision. --> 

Several recent BFT SMR protocols ([Dfinity](https://arxiv.org/pdf/1805.04548.pdf), [PiLi](https://eprint.iacr.org/2018/980.pdf), [Streamlet](https://decentralizedthoughts.github.io/2020-05-14-streamlet/), and [HotStuff](https://dl.acm.org/doi/10.1145/3293611.3331591)) have been designed in the rotating leader paradigm. However, Synchronous BFT protocols such as PiLi and Streamlet incur large latency ($65\Delta$ and $12\Delta$ respectively) to commit a single decision. Moreover, naively using Sync HotStuff and [optimal good-case latency BFT protocols](https://decentralizedthoughts.github.io/2021-03-09-good-case-latency-of-byzantine-broadcast-the-synchronous-case/) in rotating-leader paradigm would incur at least $3\Delta$ time to commit and change leaders as they incur $\Delta$ and $2\Delta$ time respectively in the view-change phase. In [our work](https://eprint.iacr.org/2021/1138.pdf), we study the [good-case latency](https://decentralizedthoughts.github.io/2021-02-28-good-case-latency-of-byzantine-broadcast-a-complete-categorization/) in the context of rotating-leader protocols. In a rotating-leader paradigm, the leaders keep changing through a view-change process after each block proposal. Thus, the overall latency of a rotating-leader protocol depends on the combination of good-case latency and the latency of the view-change. In our work, we explore protocols that change leaders and have the new leader propose responsively in $O(\delta)$ time compared to waiting for $\Omega(\Delta)$ delay during view-change. We call such protocols *optimistically responsive* rotating-leader protocols.


## A Lower Bound on the Good-Case Latency of Optimistically Responsive Rotating-leader Protocols
Our lower bound studies the good-case latency of rotating leader protocols where the next leaders propose responsively without waiting for $\Omega(\Delta)$ time after receiving proposals from previous leaders. In particular, the lower bound captures the relationship between the latency of the view-change and the good-case latency to commit a decision. Essentially, it says that if a consensus protocol tolerating $f <  n/2$ Byzantine faults allows a new leader to propose responsively in $O(\delta)$ time, the commit latency for a single slot cannot be less than $2\Delta-O(\delta)$. Thus, the sum of latencies has to be at least $2\Delta$.

Informally, our lower bound result says the following:
There exists an execution in an optimistically responsive rotating-leader consensus protocol that can tolerate $n/3 \le f < n/2$ Byzantine faults and when all messages between non-faulty replicas arrive instantaneously, where the following two conditions do not hold simultaneously:  
  - the good-case commit latency is less than $2\Delta-O(\delta)$, and 
  - honest leaders propose responsively in at most $O(\delta)$ time after receiving a proposal from the previous honest leader.



## Rotating Leader Synchronous BFT protocol with Optimal Good-case latency
We give a complete picture and provide a rotating-leader synchronous BFT protocol with optimal good-case commit latency of $2\Delta$ time. Our protocol follows "block-chaining" paradigm where a block extends a previously proposed block called its *parent*. Our protocol allows a new leader to propose a block responsively as soon as it receives a certificate (i.e., $f+1$ votes assuming $n=2f+1$) for a block proposed by a previous leader. Replicas then commit a decision within $2\Delta$ time of receiving a certificate for the proposed block.

1. **Enter view.** Upon receiving a certificate for a block proposed by previous leader, enter view $v$ and set *view-timer* to $7\Delta$ and start counting down.
2. **Propose.** Upon entering the view, the current leader proposes its current block proposal $B_k$.
3. **Vote.** On receiving the first valid block proposal from the leader, echo the proposal and multicast a *vote* for proposed block $B_k$. 
5. **Commit.** Upon receiving $f+1$ votes for block $B_k$, echo the certificate. If certificate for $B_k$ received such that *view-timer* $\ge 2\Delta$ then commit $B_k$ within $2\Delta$ if nothing bad happens.

BFT protocols usually include a *certificate ranking* rule to rank the certificate. In our protocol, we rank the certificates by their view i.e., certificates in higher view are ranked higher. In general, BFT protocols ensure that a certificate for a block to be committed is unique and sufficient honest replicas have received the highest ranked certificate before they vote in a higher view. Honest replicas do not vote on blocks that do not extend the highest ranked certificate known to them. This ensures safety of committed blocks.

In our protocol, replicas wait for a certificate for proposed block $B_k$, echo the certificate and wait for $2\Delta$ time to check for any "bad events" from the leader before committing $B_k$. This ensures two properties (i) a conflicting block proposal certificate does not exist (the argument is similar to the one presented in [Sync HotStuff](https://decentralizedthoughts.github.io/2019-11-12-Sync-HotStuff/)), and (ii) all honest replicas receive the highest ranked block certificate. In our protocol, each leader proposes a single block in a view. Thus, the certificate for $B_k$ is already the highest ranked. In addition, all honest replicas enter a view within $\Delta$ time of each other. This is due to the synchrony assumption. Since an honest replica commits only when it receives the certificate for $B_k$ such that there is sufficient time in the view (i.e., *view-timer* $\ge 2\Delta$), all honest replicas will receive a certificate for $B_k$ before they enter a higher view. This ensures no honest replica will vote blocks that do not extend $B_k$.

<!---
In general, BFT protocols include a *certificate ranking rule* to rank certificates. For simplicity, we rank certificates by their view such that certificates from higher views are ranked higher. Consensus protocols generally require that all honest replicas receive and lock on a certificate for a block $B_h$ to be committed to ensure no honest replicas vote for blocks that do not extend $B_h$ to ensure safety of a commit. In prior protocols such as [Sync HotStuff](https://decentralizedthoughts.github.io/2019-11-12-Sync-HotStuff/), this was achieved by waiting for $\Omega(\Delta)$ time during the view-change phase and inherently make the protocol non-responsive. To make the protocol responsive, we perform a responsive view-change as soon as a certificate for the proposed block $B_k$ is received.  Replicas can responsively receive the vote messages and hence the certificate. In addition, a single block is proposed in a view. Thus, if the next leader receives the certificate for the current proposed value, it can propose immediately as it is already the highest ranked certificate and all honest replicas will vote for the block extending this certificate.

(Work in Progress)
before starting a *commit-timer* to commit the proposal and forwards the received certificate.
As mentioned before, we need to ensure that all honest replicas receive a certificate for the proposed block to be committed. This is ensured by starting the *commit-timer* only after receiving the $f+1$ vote messages for the proposed block i.e., the certificate.
Replicas multicast the certificate and wait for *$2\Delta$*. If no bad events are detected during that time, replicas commit the proposed block. Waiting for $2\Delta$ time after multicasting the certificate ensures (i) no honest replicas vote for a conflicting proposal in the view; thus a conflicting block certificate cannot exist in the view, and (ii) all honest replicas receive the certificate. Thus, honest replicas will not vote for blocks that do not extend the certificate of the committed block.
-->

Read more about it [here](https://eprint.iacr.org/2021/1138.pdf), and your thoughts on [Twitter](https://twitter.com/ittaia/status/1468159598112788485?s=20&t=0uPOdnjhqf0lEekSPZ2QMA).