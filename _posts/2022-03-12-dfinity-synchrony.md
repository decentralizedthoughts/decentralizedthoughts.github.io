---
title: Consensus by Dfinity - Part I
date: 2022-03-12 00:00:00 -05:00
tags:
- blockchain
- research
author: Jannis Stoeter, Kartik Nayak
---

This is part one of a two-part post on consensus protocols published by the [Dfinity Foundation](https://dfinity.org/).

Dfinity published two protocols:
1. The first, published in 2018, is a [BFT protocol under synchrony](https://decentralizedthoughts.github.io/2019-11-11-authenticated-synchronous-bft/)  by [Hanke, Movahedi, and Williams](https://arxiv.org/abs/1805.04548). We will call this protocol  Dfinity's Synchronous Consensus  (DSC). An independent report called [Dfinity Consensus Explored](https://eprint.iacr.org/2018/1153) also explained the core consensus aspects of this protocol.
2. The second, published in 2021, is a BFT protocol under [partial synchrony](https://decentralizedthoughts.github.io/2019-06-01-2019-5-31-models/) by [Camenisch, Drijvers, Hanke, Pignolet, Shoup, and Williams](https://eprint.iacr.org/2021/632.pdf), called the Internet Computer Consensus (ICC).


This post will discuss Dfinity's Synchronous Consensus (DSC) from 2018. This protocol introduces many ideas subsequently used in Internet Consensus Computer (ICC) which is explained in the [next post](https://decentralizedthoughts.github.io/2022-03-12-dfinity-partial-synchrony/). Our goal is to describe the protocol and its invariants intuitively.

DSC solves synchronous [state machine replication](https://decentralizedthoughts.github.io/2019-10-15-consensus-for-state-machine-replication/) among $n \geq 2t + 1$ server replicas, where $t$ denotes a bound on the number of Byzantine parties. All messages reach their destination within bounded $\Delta$ time in the synchronous model. DSC assumes the need for a threshold signature scheme where the secret key is shared among the replicas. Among other things, threshold signatures provide the capability of obtaining a random beacon in each iteration of the protocol.

## High-Level Idea

Many existing BFT protocols such as [PBFT, HotStuff](https://decentralizedthoughts.github.io/2019-06-23-what-is-the-difference-between/), and [Sync HotStuff](https://decentralizedthoughts.github.io/2019-11-12-Sync-HotStuff/) divide the execution into iterations (or views). In each iteration, participating replicas vote for *at most one block*. In that sense, replicas are judicious in how they vote, and we may possibly end up in an iteration where no block is certified (a block is certified if it receives a majority quourum of votes). Thus, these protocols are *sparse* from the perspective of creating certified blocks. If a block is uniquely certified within the iteration, the replicas commit the block. If not, they engage in a view-change process to move to the next iteration, potentially without making any progress in the current iteration. 

DSC takes a slightly different approach. They attempt to uniquely certify blocks in an iteration but they allow replicas to vote for more than one block in an iteration. They maintain the invariant that *at least one block in an iteration must be certified*. In that sense, the DSC protocol is *dense* from the perspective of creating certified blocks. Having said that, they commit a block only if it was uniquely certified in that iteration. This uniqueness test is performed in hindsight. Thus, so far as the test succeeds relatively often, this has the advantage of always making progress in growing the chain and committing blocks at regular intervals.

In some more detail, the protocol works as follows. Each replica is randomly assigned a unique rank in every iteration using the random beacon; the replica with the lowest rank is called the leader. At the beginning of each iteration, every replica $p$ proposes a block, broadcasts it to all other replicas, and waits for $2\Delta$ time. After the wait time, each replica votes for the lowest-ranked block(s) it received. If it receives a lower-ranked block compared to the block(s) it has voted for, it will also go ahead and vote for that block. If a replica receives more than one block proposoal from a single replica (duh, stupid mistake!), it will broadcast a blame message and attach the two blocks as proof of misbehavior. The Byzantine replica will be removed as a consequence. We call this step equivocation check.

Once a block receives $n-t$ votes (called a *certificate*), a replica will forward it to all replicas and transition to the next iteration. All other replicas will transition upon receiving this certificate. Thus, at least one and possibly many blocks will be certified in each iteration. This ensures that the protocol keeps making progress in proposing and certifying blocks but not necessarily committing them.

However, if there is an honest leader (i.e., the lowest-ranked block is by an honest replica), then exactly one block will be certified. A block will be committed once it is deemed to be **uniquely extensible**. Since every iteration has a new random leader, we expect an honest leader every other iteration. After that iteration, all parties will commit to the chain extended by the honest leader’s uniquely certified block.

We provide a full technical specification at the end of this post.

## Commit Rule through Unique Extensibility

You may already have noticed that there is a difference between certified blocks and committed blocks. For now, keep in mind that every committed block must once have been certified, but that not every certified block must eventually be committed.

DSC commits to a block once it can be considered uniquely extensible. Intuitively, no other path (fork) at this height can be extended, and thus it is safe to commit the block. In more technical terms, *a replica $p$ will commit to a chain of blocks until iteration $(k-2)$ if all iteration $(k-1)$ blocks received in iteration $k$ extend the same block $B_{k-2}.$* In other words, if at the beginning of an iteration all blocks from the previous iteration extend the same block, then we will commit to this extended block. Otherwise, we will defer our commitment decision to a later iteration.

Fig. 1 illustrates three possible scenarios. Observe that in scenarios $A$ and $B,$ we can commit to an iteration-$(k-2)$ block, whereas, in scenario $C$, no block can be committed.

<figure>
<p align="center">
<img align="center" height=300 src="https://i.imgur.com/FTxGnDq.png">
    </p>
<figcaption align = "center"><b>Figure 1: Illustration of commit rule.</b></figcaption>
</figure>

### Key Invariants in Dfinity's Synchronous Consensus

Dfinity's synchronous consensus is built on three key invariants as its pillars; the first two primarily ensure liveness, whereas the third one primarily ensures safety. The invariants are closely related to unique extensibility. Thus, a natural question in this context is how a block can become uniquely extensible? In DSC, unique extensibility can arise in three possible ways: 

(1): we have an honest leader,\
(2): we have a Byzantine leader, but a uniquely certified block,\
(3): we have a Byzantine leader and multiple certified blocks, all of which extend the same previous block.

Note that (2) and (3) merely mark opportunities to commit to a block even when the leader is Byzantine. We can, however, not assume that (2) and (3) will ever happen.

We will show that DSC is always able to reach unique extensibility under the given assumptions by introducing the following two invariants:

**I. An honest leader's block will be uniquely certified in an iteration.\
II. In each iteration, at least one block and possibly many will be certified.**

Remember that the protocol selects a new random leader at the beginning of each iteration. In the case of an honest leader, Invariant I ensures that we will be able to commit to a chain of blocks up until the honest leader's block within the next two iterations. In the case of a Byzantine leader, Invariant II will ensure that we can move on to a new leader.

**Intuition for Invariant I:**

To see why this invariant holds, we will look at a simple example in a 3-replica setup. In particular, we will want to see how the initial wait of $2\Delta$ time suffices for even the replica who transitioned to the next iteration first to receive the new leader's block. Suppose we have the following setup:

$1, 2,\hat{3}$ (numbers = ranks in iteration $k$)

Since $1$ has the lowest rank in iteration $k$, it will be the leader of that iteration. Let $\hat{3}$ be Byzantine (denoted by the hat).

Suppose that $2$ is the first replica to transition from iteration-$(k-1),$ then:

- 2 sends $C(B_{k-1})$ to all and transitions to iteration $k.$
- 2 proposes a new block $B_k$ and waits for $2\Delta$ time.
- 1 receives $C(B_{k-1})$ within $\Delta$ time of 2's transition and also transitions to iteration $k.$
- 1 proposes a new block $B'_k$ and waits for $2\Delta$ time.
- 2 receives $B'_k$ within $\Delta$ time after 1 sent it and votes only for that block, since $1$ has the lowest rank.

<figure>
<p align="center">
<img align="center" height=300 src="https://i.imgur.com/9lHRgeR.png">
    </p>
<figcaption align = "center"><b>Figure 2: View of iteration-$k$ when the leader is honest. Proposals by 2 have been omitted for clarity.</b></figcaption>
</figure>

Since 2 only votes for 1's block and 1 also only votes for its block, $B'_k$ is the only block that receives $t+1 = 2$ votes in iteration $k.$ It will thus be the uniquely certified block.

A good question to ask here would be whether a Byzantine replica could also get a block certified in iteration-$k.$ The answer is: no, since it cannot fake its rank and since we showed that even the first honest party to transition receives an honest leader's block before starting to vote.

**Intuition for Invariant II:**

If the leader is honest, we see that its block is uniquely certified thus this invariant holds. The goal of this invariant is to ensure that we will be able to move on to the next iteration while making some progress w.r.t. certifying a block even when the leader is Byzantine. Let's think about what a Byzantine leader could do.

*Scenario 1: A Byzantine leader proposes no blocks.*

This case is relatively simple. Since all honest parties propose a block, this scenario becomes just like the case where we have an honest leader. In other words, the block proposed by the honest replica with the lowest rank among others will be uniquely certified in this iteration.

*Scenario 2: A Byzantine leader proposes several blocks or proposes blocks later.*

Your first thought here may be that it should be impossible for a Byzantine leader to have multiple blocks certified under the equivocation check without being blamed.

Let's look at a scenario where a Byzantine leader can have multiple blocks certified. Again suppose we have a 3-party system, where numbers correspond to ranks in iteration-$k$.

Let $1$ (the leader in iteration-$k$) be Byzantine:

$\hat{1}, 2, 3$

Suppose we have the following order of events:

- 1 proposes a block $B_k$ to 2 and a different block $B'_k$ to 3.
- After the $2\Delta$ time wait, 2 will vote for $B_k$ and 3 will vote for $B'_k.$ Both will send their votes to 1. 
- 1 votes for both $B_k$ and $B'_k.$
- Now, both $B'_k$ and $B_k$ have received $n-t$ votes, such that we have certificates for both.
- 1 will send $C(B_k)$ to 2 and $C(B'_k)$ to 3.
- Upon receiving $C(B_k)$ and $C(B'_k),$ 2 and 3 will transition to iteration-$(k+1).$

<figure>
<p align="center">
<img align="center" height=300 src="https://i.imgur.com/85gtx1K.png">
    </p>
<figcaption align = "center"><b>Figure 3: View of iteration-$k$ when the leader is Byzantine and proposes multiple blocks. Some edges have been omitted for clarity.</b></figcaption>
</figure>

In this case, multiple blocks get certified and all honest parties move on to the next iteration. Here we can see why certification does not imply a commit. Certification here merely ensures "some progress" such that one of these committed blocks is eventually committed.

A slightly different scenario where this can happen is when a Byzantine leader initially does not propose anything but waits for an honest vote on an honest replica's proposal and then sends a different proposal. Since honest parties vote for all lower-ranked blocks, multiple blocks will be certified.

*Scenario 3: A Byzantine leader delays progress.*

Suppose we are in the very unlucky situation and all $t-$lowest ranked replicas are Byzantine. In this case, a feasible strategy for the attacker could be to have the $t$-lowest-ranked replica propose a block $B_k$ to a single honest party, which will vote for the block and broadcast it. Yet, before the vote reaches the last honest replica, the $(t-1)$-lowest-ranked replica proposes a new block $B'_k$ to that honest replica. Consequently, when $n= 2t+1$, $B_k$ will only receive $2t+1 - t - 1 = t$ votes and will not be certified. Observe, however, that even in this unlikely case, the adversary can delay progress by at most $O(t\Delta)$ time. Eventually, the lowest-ranked replica will need to propose a block, and that block will be certified.

**Liveness.** We can see how Invariants I and II together ensure liveness. Invariant I ensures that the protocol can commit to a chain of blocks with an honest leader. Invariant II ensures that we will move on from a Byzantine leader until we get an honest one.

**Safety.** Now, let's look at how the commit rule introduced earlier ensures safety. Remember that we are in the synchronous setting and that for a block to be certified, at least one honest party must vote for it. The honest party will forward the block to all other honest parties upon voting. Thus, all honest parties will have received all iteration-$(k-1)$ blocks after the initial wait in iteration-$k.$ Further observe that there cannot be any future iteration-$(k-1)$ block since an honest party will only vote for an iteration-$(k-1)$ block in iteration-$(k-1)$ itself. Consequently, if all of the iteration-$(k-1)$ blocks extend the same previous block $B_{k-2}$, then any future chain will extend the subchain up to $B_{k-2}$.

We will thus use the commit rule as our third and last protocol invariant:

**III. At the end of iteration $k$, if all iteration-$(k-1)$ blocks extend the same block $B_{k-2}$, then $B_{k-2}$ is uniquely extensible; no other iteration-$(k-2)$ block can be extended from then on.**

## Complexity Metrics
**Latency.** Finally, let's look at the expected latency of committing a block:

In this context, we can observe a very neat feature of the protocol: all operations except for the initial wait of $2\Delta$ can occur at the actual network speed. As far as we know, this is the first work that explores progress at actual network speed under the synchrony assumption. When the actual network delay is $<< \Delta,$ we expect each iteration to last $2\Delta$ time. Since every iteration has a new random leader, we can expect to have an honest leader within two iterations, after which it takes exactly two iterations to commit the block. Thus, the expected latency in this case is $2 \times 2\Delta + 2 \times 2\Delta = 8\Delta$.

When the network delay is close to $\Delta$, each iteration first incurs the initial $2\Delta$ wait time. In the case in which the adversary controls the replicas with $t-$lowest ranks, which happens with probability $2^{t+1},$ all other operations take at most $(t+1)\Delta$ time. Thus, in expectation, we would need to wait for another $2\Delta$ per iteration. This results in an expected latency to commit of: $2 \times 4\Delta + 4\Delta + 2\Delta = 14 \Delta.$ Note that we can commit immediately after the initial $2\Delta$ wait in iteration-$k+2,$ when iteration-$k$ had an honest leader.

**Communication complexity.** In the protocol, if replicas with top $k$ ranks are Byzantine in an iteration, then the communciation complexity of that iteration is $(2k+1)n^2$. This is because each replica forwards at most 2 messages for the proposal of each Byzantine replica with the low rank. However, this happens with probability $2^{-(k+1)}$. Thus, the expected communication complexity is $O(n^2)$.

## Full Protocol Specification

> 
> Each replica $p$ maintains a state of all valid iteration-$k$ blocks in a set $\mathcal{B}_k.$
>
>The protocol proceeds in iterations:
>- In each iteration $k$, every replica is assigned a unique, random, and verifiable rank $r_p(k)$. The replica with lowest rank is the leader of iteration $k$
>- Once assigned a rank, for each replica $p$ and each iteration $k:$
>1. Propose and wait:
> - $p$ creates a new block $B_k$ by extending any certified block $B_{k-1}$ from the previous iteration. 
> - $p$ broadcasts $B_k$ and waits for $2\Delta$ time.
>2. Vote for the best ranked block(s):
> - $p$ votes for the block with lowest rank that is has not yet seen by forwarding it to all other replicas.
> - If $p$ receives two or more blocks from the same proposer, it will notify other replicas of the equivocation by issuing a blame message and attaching two blocks as proof. This increases the leader's effective rank.
> - $p$ will then vote for the block with next-lowest rank.
> - $p$ repeats this step until:
> a) $p$ has accumulated $t+1$ votes for a block $B_k$: $p$ certifies $B_k$ and broadcasts the certificate $C(B_{k})$.
> b) or $p$ receives a certificate $C(B_{k})$ for some block $B_k.$
> 3. Forward certificates.
> - Upon receiving or generating $C(B_{k})$ for some iteration-$k$ block $B_k$, $p$ broadcasts the certificate and enters iteration $k+1$.
>
>
> Committing (can be executed anytime after the initial wait): if all received $B_{k-1}$ blocks extend the same block $B_{k-2},$ consider $B_{k-2}$ committed.

Please add comments on [Twitter](https://twitter.com/kartik1507/status/1504899744618872832?s=20&t=og7wq7vnJHctbC0E17hryw).

**Acknowledgment.** We would like to thank Ittai Abraham and the authors of Internet Consensus Computer (Jan, Manu, Timo, Yvonne-Anne, Victor and Dominic) for useful discussions.
