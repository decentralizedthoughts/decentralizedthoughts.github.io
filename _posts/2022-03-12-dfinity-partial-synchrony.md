---
title: Consensus by Dfinity - Part II (Internet Computer Consensus)
date: 2022-03-12 00:00:00 -05:00
tags:
- blockchain
- research
author: Kartik Nayak
---

This post is part two of a two-part post on consensus protocols published by the [Dfinity Foundation](https://dfinity.org/); you can find part one [here](https://decentralizedthoughts.github.io/2022-03-12-dfinity-synchrony/). This post will intuitively explain the [Internet Computer Consensus](https://eprint.iacr.org/2021/632.pdf).

The differences between DSC and ICC are primarily due to the underlying network model that they assume --- while DSC works under synchrony and tolerates $t < n/2$ Byzantine faults, ICC works under partial synchrony and tolerates $t < n/3$ Byzantine faults. Recall that the fault tolerance is optimal under the respective network models ([cheat sheet](https://decentralizedthoughts.github.io/2021-10-29-consensus-cheat-sheet/)).

## High-Level Idea

The core idea in ICC seems to be heavily inspired by DSC, and our description will be reminiscent of the [one for DSC](https://decentralizedthoughts.github.io/2022-03-12-dfinity-synchrony/). The ICC protocol works in iterations and forming *certified* blocks in an iterattion. A block is said to be certified if it receives greater than two-third quourum of votes. In each iteration, ICC guarantees the formation of at least one certified block while attempting to obtain a unique certified block. If a block in an iteration is indeed uniquely certified, all the blocks until this block will eventually be committed.

In some more detail, the protocol works as follows. In every iteration, each replica is randomly assigned a unique rank; the replica with the lowest rank is called the leader. At the beginning of each iteration, every replica proposes a block and broadcasts it to all other replicas. To prioritize proposals from the leader and lower-ranked replicas, replicas wait for some time before proposing --- a replica with a higher rank will wait longer. When a replica receives a block, it will vote for this block. Again, to prioritize voting for proposals from the leader and lower-ranked replicas, replicas will wait until an appropriate amount of time before voting. However, if it receives a lower-ranked block than the last block it has voted for, it will vote for the new block too. 

Once a block receives $n-t$ votes (called a *certificate*), a replica will forward the certificate to all replicas and transition to the next iteration. All other replicas will transition upon receiving this certificate. Thus, at least one and possibly many blocks will be certified in each iteration. This ensures that the protocol keeps making progress in proposing and certifying blocks but not necessarily committing them.

Suppose the leader is honest and the network is synchronous during an iteration. In that case, all honest replicas will prioritize voting for only the leader's block, and only that block will be certified. If a replica observes that a block is uniquely certified in an iteration (in its local view), then it will broadcast a commit message for the certified block. The block and its predecessors will be committed if it receives $n-t$ commit messages.

### Key Invariants in the Internet Computer Consensus

The core protocol relies on the following three invariants. The first two are necessary for liveness, whereas the last one is necessary for safety.

**I. If the network is synchronous for a "sufficiently long time", an honest leader's block will be uniquely certified in an iteration for all honest replicas.**

To see why this invariant holds, observe that replicas send proposals and vote for proposals at different times depending on the proposal rank. Thus, when the network is synchronous if the delay we set between two consecutive proposals is "long enough" (to account for the time difference between two replicas to move to the next iteration and the time to receive the proposal), the honest leader's block will arrive at all replicas first. Thus, honest replicas will vote for the block. Moreover, replicas will not vote for any other proposal since those proposals have a higher rank.

**II. At least one block and possibly many will be certified in each iteration.**

As explained in the previous paragraph, Invariant II holds when the leader is honest, and the network is synchronous for sufficiently long. What happens when the leader is Byzantine, or the network is not synchronous? In the former case, a Byzantine leader can have multiple blocks certified. But at least one of them will be certified. In particular, similar analysis as described in [Invariant II for SDC](https://decentralizedthoughts.github.io/2022-03-12-dfinity-synchrony/) will apply here too. In the latter case, replicas just wait until at least one block is certified in an iteration. Note that, under partial synchrony, this will eventually happen.

We can see how Invariants I and II together ensure liveness. Invariant I ensures that the protocol can commit to a chain of blocks once there is an honest leader and we have network synchrony. Invariant II ensures that we will move on from a Byzantine leader until we get an honest one while still certifying a block in an iteration.

**III. At the end of an iteration $k$, if a block $B_k$ is uniquely certified according to $\geq t+1$ honest replicas, then no other block $B'_k$ can be committed at height $k$.**
Observe that if $\geq t+1$ honest replicas observe $B_k$ being uniquely certified, they would send a commit message for $B_k$. More importantly, since a commit message is sent for at most one block in an iteration, they would not send a commit message for a different block $B'_k$. Thus, $B'_k$ will not be able to receive $n-t$ commit messages! This ensures the safety of $B_k$ if it is committed.

Also, observe that as per Invariant I, when the leader is honest and the network is synchronous, a block $B_k$ will be uniquely certified at the end of iteration $k$ for *all $n-t$ honest replicas*. Since these $n-t$ honest replicas will send a commit message for $B_k$, $B_k$ will eventually be committed.

## Notes

**Remark 1: Differences between ICC and DSC.** As you may have observed, the two protocols are similar. Here are the primary differences:

- DSC relies on waiting for $2\Delta$ time at the start of an iteration; however, all replicas propose at the start of this timer. The wait time guarantees that an honest leader's proposal is prioritized. ICC replaces this with a softer condition with staggered proposal and voting; if the network is synchronous, it achieves the same effect.
- The unique extensibility invariant for iteration $k$ in DSC relies on a strong synchrony assumption to detect the absence of additional blocks at height $k-1$ potentially pointing to other certified blocks at height $k-2$. In ICC, such a condition cannot be met under partial synchrony. Replicas instead send a commit message when they believe that a block is uniquely certified (uniquely extensible). The block will be committed if an $n-t$ quorum of replicas sends this message; thus, an ICC commit relies on a quorum intersection argument instead of synchrony. This is also the reason why we are able to tolerate only $t < n/3$ faults.

**Remark 2: Communication complexity.** Due to partial synchrony, even if the leader in an iteration is honest, under an adversarial block arrival ordering, each replica may end up voting for each of the $n$ proposals. Thus, in the worst case, the communciation complexity in an iteration would be $O(n^3)$ for $O(1)$-sized blocks. However, if the network is synchronous, the expected communication complexity is $O(n^2)$ (similar reasoning as in DSC).

**Remark 3:** The [ICC paper](https://eprint.iacr.org/2021/632.pdf) describes three different protocols dubbed ICC0, ICC1, ICC2. In this post, we intuitively describe ICC0. 

ICC1 introduces some optimizations to ICC0 so that it can be used in a peer-to-peer gossip layer. For example, it introduces additional conditions for a replica to propose a new block and bound the number of stray proposals.

ICC2, in addition, aims to improve the communication complexity of the protocol when the block sizes are much larger than other protocol messages. In particular, they use [erasure codes](https://en.wikipedia.org/wiki/Erasure_code) to reduce this communication complexity. Such techniques have been used in several prior works; we will explain this technique in relation to consensus in more detail in a separate post.

Please add comments on [Twitter](https://twitter.com/kartik1507/status/1504899744618872832?s=20&t=og7wq7vnJHctbC0E17hryw).

**Acknowledgment.** We would like to thank Ittai Abraham and the authors of Internet Consensus Computer (Jan, Manu, Timo, Yvonne-Anne, Victor and Dominic) for useful discussions.
