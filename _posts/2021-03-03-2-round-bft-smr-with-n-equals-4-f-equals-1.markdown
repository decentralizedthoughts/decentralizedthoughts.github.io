---
title: 2-round BFT SMR with n=4, f=1
date: 2021-03-03 06:37:00 -05:00
tags:
- research
- SMR
author: Zhuolun Xiang
background:
  - /2021-02-28-good-case-latency-of-byzantine-broadcast-a-complete-categorization/
  - /2019-06-01-2019-5-31-models/
continue_reading:
  - /2025-12-12-dpaas/
---

<span style="color:grey"> Guest post by [Zhuolun Xiang](https://sites.google.com/site/danielxiangzl/)  </span>


In the [previous post](https://decentralizedthoughts.github.io/2021-02-28-good-case-latency-of-byzantine-broadcast-a-complete-categorization/), we presented a summary of our **good-case latency** results for Byzantine broadcast and Byzantine fault tolerant state machine replication (BFT SMR), where the good case measures the latency to commit given that the leader/broadcaster is honest. In this post, we describe a new Byzantine Fault Tolerant (BFT) State Machine Replication (SMR) protocol for [partial synchrony](https://decentralizedthoughts.github.io/2019-06-01-2019-5-31-models/), where the network becomes synchronous after an unknown Global Stable Time (GST). The details of the protocol can be found in our **[paper](https://arxiv.org/abs/2102.07932)**.

{: .box-note}
Our **[(5f-1)-SMR protocol](https://arxiv.org/abs/2102.07932)** can commit a decision within $2$ rounds after GST with an honest leader, and only requires $n\geq 5f-1$ replicas. 


Our protocol refutes the claim made in [Fast Byzantine Consensus (FaB)](https://ieeexplore.ieee.org/document/1467815) saying that $n=5f+1$ is the best possible resilience for $2$-round BFT SMR protocols. Interstingly, for the canonical example with $n=4$ and $f=1$, we can have a 2-round [PBFT]((http://pmg.csail.mit.edu/papers/osdi99.pdf)) protocol with the optimal resilience!

## [PBFT](http://pmg.csail.mit.edu/papers/osdi99.pdf): 3 rounds with $n=3f+1$

PBFT may be the most well-known BFT SMR protocol for partial synchrony. Briefly, the protocol consists of two components, a steady state protocol that aims to commit decisions when the leader is honest, and a view-change protocol that replaces the leader if not enough progress is made. PBFT achieves the optimal resilience $n\geq 3f+1$ for partial synchrony, and let's assume $n=3f+1$ for simplicity. Now we describe a version of PBFT that has a commit latency of 3 rounds when the leader is honest and the network is synchronous. The protocol proceeds in views $k=1,2,...$ each with a leader.
- In the steady state, PBFT has *1 round of proposing* plus *2 rounds of voting*, as follows. 
    - (Proposing) The leader of view k proposes a value `v` with a `proof`. 
    - (Voting 1) Upon receiving from the leader, parties multicast `<vote1, v, k>` for `v`, if `v` is the value of the highest `lock` in `proof`. 
    - (Voting 2) Upon receiving $n-f=2f+1$ `vote1` for the same value `v`, the party multicasts `<vote2, v, k>` for `v` and sets its `lock` to be the set of `vote1` messages. 
    - (Commit) Upon receiving $2f+1$ `vote2` for the same value `v`, the party commits `v`.
- In the view-change, parties blame the leader of the current view k by multicasting `<timeout, k>` messages, if it does not commit the value in view k quick enough. The next leader of view k+1, once collects $f+1$ `timeout` messages of view k, will multicast it to all parties as a proof for entering the new view. Then all parties send its `lock` to the new leader, and the new leader will propose the value of the highest `lock` (ranked by view numbers) among $2f+1$ received `lock`s. The `proof` for the proposal is the $2f+1$ `lock`s.

<p align="center">
  <img width="500" src="https://i.imgur.com/2QQTcfX.png">
</p>

 ![](https://github.githubassets.com/images/icons/emoji/unicode/1f4a1.png?v8)  **Correctness.** The safety of the protocol relies on quorum intersection -- any two sets of $2f+1$ votes must contain at least $f+1$ honest parties each, and thus intersect at least $2(f+1)-(n-f)=1$ honest party. Therefore, within a view, there will not be two sets of votes for different values. For safety across views, again it is due to the quorum intersection between the set of parties that locks a value and the set of `lock`s contained in leader's `proof`. Since any committed value `v` are locked by $2f+1$ parties (who sent `vote2`), the set of parties locked on `v` and the set of `lock`s contained in the leader's `proof` must intersect at 1 honest party whose `lock` is for `v`. Thus the leader has to repropose `v`, if `v` has been committed.



<p align="center">
  <img width="300" src="https://i.imgur.com/CCncNpX.png">
</p>


## [FaB](https://ieeexplore.ieee.org/document/1467815): 2 rounds with $n=5f+1$

Fast Byzantine Consensus (FaB) reduces 1 round of voting in PBFT, so its steady state has *1 round of proposing* and *1 round of voting*. The latency improvement does not come for free, FaB tolerates fewer faults as it requires $n\geq 5f+1$. After the leader proposes, the parties can commit if they receive $n-f=4f+1$ votes for the same value. For brevity, we will not present the whole protocol, but just the intuition.


<p align="center">
  <img width="500" src="https://i.imgur.com/8k8OM4S.png">
</p>

 ![](https://github.githubassets.com/images/icons/emoji/unicode/1f4a1.png?v8)  **Intuition.** Now $n=5f+1$, the quorum size becomes $n-f=4f+1$. Parties commit a value if they receive $4f+1$ votes for the value. No different values can be committed in the same view due to the quorum intersection of the votes. For safety across different views, any committed value `v` has been voted by $3f+1$ honest parties. In the `timeout` message, these parties will attach the voted value `v`. Then, the next leader, when receiving $4f+1$ `timeout` messages, can choose `v` to propose. It is because the set contains at least $(4f+1-f)+(3f+1)-(n-f)=2f+1$ honest parties that voted for `v`, and $2f+1$ is a supermajority of $4f+1$. Any other value will not be voted by the honest parties, as they also receive $4f+1$ `timeout` message and decide to only vote for `v` for ensuring safety.

It seems like $n=5f+1$ is the best we can have for 2-round commit. If we let $n=5f$, then the quorum size becomes $n-f=4f$, and any committed value `v` is voted by $3f$ honest parties. For any set of $4f$ `timeout` messages, it could be that $2f$ `timeout` messages are from the $3f$ honest parties that voted for `v`, and the rest $2f$ `timeout` messages are from the remaining $f$ honest parties that voted for `v'` and $f$ Byzantine parties. In this case, the leader or any honest party cannot break the tie and safely choose the next proposal. The authors of FaB also present a **lower bound saying that any 2-round consensus is impossible iff $n\leq 5f$, and claim that FaB has optimal resilience.**

<p align="center">
  <img width="300" src="https://i.imgur.com/bVAbQJj.png">
</p>


## [(5f-1)-SMR](https://arxiv.org/abs/2102.07932): 2 rounds with $n=5f-1$

However, we show the resilience of FaB can be further improved to $n=5f-1$. The key observation we have is to <span style="background-color: #FFFF00">use signatures to detect the equivocation of the leader</span>
, as the leader must sign its proposed value. Our protocol also has 1 round of proposing and 1 round of voting in the steady state. After the leader proposes, the parties can commit if they receive $n-f=4f-1$ votes for the same value.


<p align="center">
  <img width="500" src="https://i.imgur.com/8k8OM4S.png">
</p>

 ![](https://github.githubassets.com/images/icons/emoji/unicode/1f4a1.png?v8)  **Intuition.** Now with $n=5f-1$, the quorum size becomes $n-f=4f-1$. Parties commit a value if they receive $4f-1$ votes for the value. No different values can be committed in the same view due to the quorum intersection of the votes. For safety across different views, if any value `v` is committed, then at least $3f-1$ honest parties have voted for `v`. Consider the set of $4f-1$ `timeout` messages received by any party during the view-change. If the `timeout` messages contain no value other than `v` signed by the leader, the party knows only `v` can be re-proposed. Otherwise, if the `timeout` messages contain a different value `v'` signed by the leader, then the *leader must be Byzantine*: it signed and proposed different values. Then, the party can just wait for one more `timeout` message from any party other than the leader, which means it can receive $4f-1$ `timeout` messages from at most $f-1$ Byzantine parties and hence at least $3f$ honest parties. If `v` is committed, at least $3f-1$ honest parties have voted for `v`, hence the above set of `timeout` messages must contain $3f+(3f-1)-(n-f)=2f$ messages from the honest parties that voted for `v`. Since $2f$ is a supermajority of $4f-1$, the next leader and any honest party can uniquely choose `v` to be the next proposal.
In this way, we are able to construct a BFT SMR protocol that commits in 2 rounds in the good case and only requires $n=5f-1$.


<p align="center">
  <img width="300" src="https://i.imgur.com/IxDL6KN.png">
</p>


> Wait.. what about the *lower bound* in FaB we just mentioned? Does it mean our result contradicts the lower bound? 

The answer turns out to be NO. As pointed out in a [concurrent work](https://arxiv.org/abs/2102.12825), the lower bound proof in FaB assumes a family of consensus protocols that with seperate sets of proposers and acceptors, i.e., the set of parties that propose values and the set of parties that run the consensus are disjoint. For this family of protocols, our technique of detecting leader equivocation with signatures won't work, since the proposal is from a different set of parties. We also note that, even for general protocols, authentication (using signatures) is crucial for our protocol construction and the lower bound proof. We believe that the right resilience bound is back to $n=5f+1$ for unauthenticated protocols.

> So, how do we know if it is optimal?

In our **[good-case latency paper](https://arxiv.org/abs/2102.07240)**, we argue the optimality of the resilience $n=5f-1$ for authenticated BFT protocols under partial synchrony, by defining a new broadcast formulation called **partially synchronous validated Byzantine broadcast (psync-VBB)**. Any solution for psync-VBB directly solves a single shot of BFT SMR, and most of the existing Primary-Backup-based BFT SMR solutions like PBFT also solve psync-VBB. In our **[good-case latency paper](https://arxiv.org/abs/2102.07240)**, we formally proves that $n=5f-1$ is the resilience boundary for 2-round psync-VBB, i.e., psync-VBB can have good-case latency of 2 rounds iff $n\geq 5f-1$. It would be astonishing to have a Primary-Backup-based BFT SMR protocol that is not captured by psync-VBB and has a better resilience.


{: .box-note}
At the time when writing this post, we noticed a concurrent work by Petr Kuznetsov, Andrei Tonkikh, and Yan X Zhang titled "[**Revisiting Optimal Resilience of Fast Byzantine Consensus**](https://arxiv.org/abs/2102.12825)" that independently obtains almost the same set of results mentioned in this post, though stated for the problem formulation of Byzantine agreement instead of broadcast. We believe the protocols and lower bound proofs in the above work and [our work](https://arxiv.org/abs/2102.07240) (the partial synchrony part) share very similar intuition and construction, and can actually imply one another.


Please answer/discuss/comment/ask on [Twitter](https://twitter.com/ittaia/status/1367143317687963651?s=20).
