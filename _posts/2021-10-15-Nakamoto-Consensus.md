---
title: Nakamoto's Longest-Chain Wins Protocol
date: 2021-10-15 00:00:00 -04:00
tags:
- blockchain101
author: Kartik Nayak
background:
  - /2019-10-15-consensus-for-state-machine-replication/
  - /2020-08-28-what-is-a-cryptographic-hash-function/
  - /2019-11-29-Analysis-Nakamoto/
continue_reading:
  - /2022-03-10-eip1559/
---

In this post, we will cover Nakamoto's Consensus protocol presented in the [Bitcoin whitepaper](https://bitcoin.org/bitcoin.pdf). There are a lot of posts and videos that explain this seminal and simple protocol. Our goal in this post will be to *intuitively* piece out the need for different aspects of the protocol, such as proof-of-work and how network synchrony plays a role in the protocol.

> The proof-of-work chain is a solution to the Byzantine Generals' Problem. I'll try to rephrase it in that context. [Satoshi Nakamoto 2008-11-13](https://satoshi.nakamotoinstitute.org/emails/cryptography/11/)

We are in the setting described in our [state machine replication](https://decentralizedthoughts.github.io/2019-10-15-consensus-for-state-machine-replication/) post where a group of $n$ server replicas known to each other agrees on a sequence of values. For simplicity, we start with reaching consensus on a single value. In the second part of this post, we will generalize it to multiple values.

The key intuition behind Nakamoto's protocol is to ask a majority of the parties what should be committed. What the majority says is decided peculiarly by building chains and using the "longest chain wins" rule. For now, it is unclear why we should be building chains to learn about how a majority of the parties think. We will revisit this question later in the post.

In the following, we will describe a simpler version of the protocol to get an intuitive understanding of its core aspects.

```
Let v denote a replica's input

Each replica maintains a set of chains, initially empty.

The protocol proceeds in rounds. In each round r:
- A unique replica is elected uniformly at random to be the leader L of round r.
- L adds an empty vote block to the longest chain known to it. 
  If no chain is known, it creates a new chain with a single block with input v.
- L shares the longest chain with all replicas.
- All replicas update their set of chains based on L's message.

Commit rule: If some chain is k blocks long, commit the value in the first block. 
             Share the chain with all other replicas.
```

Observe that there are two simplifications made in the above protocol. First, the input value is added only to the first block (a proposal). Subsequent blocks are empty (which act as votes). Second, we did not discuss how a unique leader is elected uniformly at random each round and how everyone knows that this replica is the leader. For now, we will assume that there is an oracle that provides us with this abstraction.

Let us understand how the protocol under some specific scenarios:
- **All replicas are honest.** In this scenario, the first-round leader proposes a value v in the first block, and in the next k rounds, the honest leaders in those rounds extend the only chain that exists.

<p align="center">
<img src="https://i.imgur.com/6eQNWsB.png" width="512" title="Scenario 1">
</p>

- **20% of the replicas are Byzantine, and Byzantine replicas attempt to create a different chain.** Observe that if 20% of the replicas are Byzantine, then in expectation, they will be leaders in 20% of the rounds.

    For example, we may have HHBBHHHHH... as the sequence of leaders resulting in the chain as follows. 

<p align="center">
<img src="https://i.imgur.com/DcvCxKi.png" width="512" title="Scenario 2a">
</p>

Here, the Byzantine leader in the third round started a different chain, with the first block having value v = Orange (or orange chain) even when a longer blue chain existed. Eventually, the blue chain was committed.

However, the order could have been HHBBBHHHH... resulting in the following chain.

<p align="center">
<img src="https://i.imgur.com/nDMRMFJ.png" width="512" title="Scenario 2b">
</p>

In this scenario, the orange chain grew longer, and eventually, all replicas committed value v = Orange. It is important to stress that, from a consensus standpoint, all honest replicas have still committed the same value. Thus, we have safety and liveness so far as the orange value is a valid value (as per some validity rule). 

However, when we achieve consensus on many values instead of just one, a situation where the fraction of Byzantine values committed is higher than the fraction of Byzantine replicas in the system is not ideal. For instance, if all blocks committed are proposed by Byzantine replicas, then we have concerns such as censorship, fairness, etc. This ratio of honest blocks to the total number of blocks is also referred to as *chain quality*. Ideally, we want this ratio to be the same as the fraction of honest replicas. The attack described here will not yield a worse chain quality. However, there exist other attacks to worsen chain quality, e.g., selfish mining attack (described in an earlier [post](https://decentralizedthoughts.github.io/2020-02-26-selfish-mining/)).
    
- **80% of the replicas are Byzantine, attempting to create a different chain.** In this scenario, Byzantine replicas can easily create a "private chain" of length k before honest replicas do. When honest replicas reach length k, by selectively revealing the private chain to only some honest replicas, the Byzantine replicas can cause a safety violation.

    As an example, the leader order can be BBHBHBBBHBHBHB.... 

<p align="center">
<img src="https://i.imgur.com/eV3TXOV.png" width="768" title="Scenario 3">
</p>

Observe that if the Byzantine replicas do not show a chain to honest replicas, an honest leader in the third round can start a new chain instead.

- **49% of the replicas are Byzantine, attempting to create a different chain.** Byzantine replicas can attempt the same attack as in Scenario 3. The probability with which they win any election is 0.49. Since each of these elections happens independently at random, it can be shown that the probability with which Byzantine chain reaches length $k$ before honest chain is $e^{-O(\text{k})}$. In other words, when Byzantine replicas are in the minority, they will win a private chain attack only with probability exponentially small in $k$.

Thus, for a sufficiently large $k$ (security parameter), a private chain attack by Byzantine replicas does not succeed against Nakamoto's protocol so far as they are in minority. This was shown using some analytical evaluation in the original [Bitcoin whitepaper](https://bitcoin.org/bitcoin.pdf). We should caution you that this is not a proof of security for the protocol -- it is just a security argument against *one of the attacks*. A proof (of the more generalized version of the protocol) has been shown by [GKL'15](https://eprint.iacr.org/2014/765.pdf), [PSS'17](https://eprint.iacr.org/2016/454.pdf) and more recently by [Ren'19](https://decentralizedthoughts.github.io/2019-11-29-Analysis-Nakamoto/) (with an accompanying [blog post](https://decentralizedthoughts.github.io/2019-11-29-Analysis-Nakamoto/)). Having said that, it has also been shown [recently](https://arxiv.org/pdf/2005.10484.pdf) that a private-chain attack is indeed the worst attack possible when there is no network delay.

### From single-shot consensus to consensus for multiple values

How do we commit more than one value? Of course, an option is to have multiple values in the same block. But note that we cannot have all values in one block due to arrival of values at a later point such that they depend on previous ones. Thus, committing multiple blocks is necessary for any SMR system. Nakamoto achieves this by pipelining this process in an intuitive manner: each block acts as a proposer for a value (or values) and a vote for all the blocks that precede it. So, there is a genesis block, with only one longest chain that extends the genesis, and every block plays both roles in this longest chain.

<p align="center">
<img src="https://i.imgur.com/CxhdIWa.png" width="768" title="Many values">
</p>

A block can be committed if it is on the longest chain starting from genesis and if at least k blocks extend it. Thus, the commit latency for each block is still k. Due to pipelining, a block is committed every round (or a constant number of rounds in expectation). Since all blocks are now connected to the genesis, the notion of creating a new chain by a Byzantine replica is now replaced by a *fork* from the longest chain.


### Permissionlessness, proof-of-work, and need for synchrony

Earlier, we made several simplifying assumptions: 1. there is a fixed number of replicas that know each other, 2. there is a well-defined notion of *rounds*, and 3. there is a leader election oracle that uniquely and verifiably identifies a leader uniformly at random. Given our basic understanding of the protocol, we will now either relax these assumptions or learn how to realize these oracles.

**Permissioned vs. permissionless.** The notion of having a set of replicas that know each other is called the *permissioned* setting. In effect, any replica that needs to join the system requires permission to be a part of it. Bitcoin works in a more generic setting where any replica can leave or join the system at any point in time. Moreover, the replicas do not have any identity associated with them -- all replicas are pseudonymous. Yet, the expectation is that the protocol still provides us with safety and liveness guarantees. This setting is referred to as *permissionless*, and it is strictly harder to design permissionless protocols.

Since replicas can join at any time and replicas do not have identities associated with them, an adversary can masquerade itself as many replicas, also referred to as *Sybil replicas*. Given our leader election protocol, this is concerning: if elections happen uniformly at random, almost all elections will be won by (a Sybil of) the adversary. It can then always pull off a private chain attack described earlier, leading to a safety violation.

**Resource constraints and proof-of-work.** Nakamoto consensus solves this problem by making an additional assumption that relates the *computation power* of honest and Byzantine replicas and uses the computation power to determine leaders. Specifically, the protocol is only secure so far as the honest computation power is more than Byzantine computation power. To elect leaders, all replicas engage in a continuous randomized competition that depends on the number of hashes they can compute at any time. The winner of each iteration of this competition needs to present a proof-of-work (explained in more detail in this [post](https://decentralizedthoughts.github.io/2020-08-28-what-is-a-cryptographic-hash-function/)). The process of finding the next block is also referred to as *mining*; hence, the replicas are referred to as miners.

Thus, an updated version of the protocol looks like the following:

```
Maintain a tree rooted at a publicly defined genesis block

At any point in time, let C denote the longest chain known to the replica
while (true) {
    in parallel, do the following:
    1. attempt to find the next block (containing values/transactions) on C 
       with a valid proof-of-work // compute intensive step
    2. if the replica receives a new longest chain, 
       update C to be this longest chain
}

Commit rule: if the longest chain has length x, commit the first x-k blocks.
             Share the chain with all other replicas.
```

Proof-of-work provides us with a verifiable unique leader elected uniformly at random in intermittent intervals (earlier referred to as rounds). Well, almost! It turns out that, when parameterized correctly, we achieve these properties with high probability. But in some cases, the uniqueness property does not hold. Why? Each attempt at finding a proof-of-work for the next block involves computing a hash function based on random input (nonce), and thus this process is memoryless (i.e., success in an attempt does not depend on previous attempts). Thus, the arrival rate of the next block in the entire system is governed by a *Poisson process*, and we may have two replicas (both of them potentially honest) who mine a block within a short time interval. If this time interval is short enough that the replicas do not receive each other's block, we have an honest fork in the system. Observe that this fork exists purely due to a delay in the network. This is why Bitcoin is parameterized to produce a block every ten minutes -- this ensures that honest forks are rare. On the other hand, protocols such as Ethereum generate blocks faster and observe a higher honest forking rate. Honest forking rate reduces the effective computation power of honest replicas, which was shown quantitatively in a previous [post](https://decentralizedthoughts.github.io/2019-11-29-Analysis-Nakamoto/). A graphical illustration of the relationship between the two, shown below, was plotted by [DKT+19](https://eprint.iacr.org/2020/601.pdf) in their analysis.

<p align="center">
<img src="https://i.imgur.com/G5xpPyq.png" width="512" title="Graph">
</p>

In the above figure, the x-axis represents the block time relative to the synchronous network delay. The y-axis represents the adversarial fraction, and the blue line represents the adversarial fraction tolerated for a given block time. When block time is large, e.g., 60, there is little reduction in the effective computation power, and we can tolerate an adversarial power close to 50%. On the other hand, when block time is small, e.g., 0.1, we observe a reduction. The other lines in the graph represent adversarial lower bounds shown by some other works.

This also explains why a synchrony assumption is critical for Nakamoto consensus. Once an honest block is mined in an asynchronous or partially synchronous network, it may not arrive at any other replica, leading to forks (even without Byzantine participation). 

**Remarks.**
- There is a key distinction between Nakamoto consensus and "classical BFT" protocols that primarily exist in the permissioned setting. Classical techniques typically maintain safety at all times in the protocol execution; if conditions are favorable, the protocol achieves liveness too. On the other hand, Nakamoto consensus maintains liveness at all points in time; safety holds (probabilistically) only under favorable conditions.
- In a purely permissionless setting (no identities associated with replicas), the only class of solutions known is Nakamoto consensus or variants therein, e.g., [Ghost](https://www.avivz.net/pubs/15/btc_ghost_full.pdf) protocol. This is why "what the majority says" is decided using such a chain-based protocol. On the other hand, for the permissioned setting and protocols that use proof-of-stake, one can use classical BFT protocols as well as Nakamoto consensus.
- In terms of [setup assumptions](https://decentralizedthoughts.github.io/2019-07-19-setup-assumptions/), observe that the permissioned version of this protocol requires setup, e.g., PKI setup, to verifiably elect leaders. On the other hand, in a proof-of-work world, the only setup needed is to agree on a genesis block (which is a public setup). In both cases, we circumvent the [FLM bound](https://decentralizedthoughts.github.io/2019-08-02-byzantine-agreement-is-impossible-for-$n-slash-leq-3-f$-is-the-adversary-can-easily-simulate/) to tolerate more than one-third adversaries.
- The expected time to mine a block depends on the difficulty of proof-of-work and the computation power invested by all miners participating in the protocol. Since the participants (and consequently the computation power) can change over time, proof-of-work mining difficulty is adjusted every two weeks in Bitcoin to still maintain a mean rate of one block every ten minutes. However, the protocol cannot tolerate a sudden surge or drop in computation power.

**Acknowledgment.** We would like to thank Ittai Abraham and Ling Ren for providing feedback on this post!

Please share your comments on [Twitter](https://twitter.com/kartik1507/status/1449379437586354191?s=20).
