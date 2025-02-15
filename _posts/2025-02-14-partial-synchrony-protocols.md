---
title: Byzantine Fault Tolerant Partial Synchrony Protocols
date: 2025-02-14 09:30:00 -05:00
tags:
- BFT
- dist101
author: Kartik Nayak, Ittai Abraham
---

Many blockchain protocols work under [partial synchrony](https://decentralizedthoughts.github.io/2019-09-13-flavours-of-partial-synchrony/). Examples include [PBFT](https://pmg.csail.mit.edu/papers/osdi99.pdf), [SBFT](https://arxiv.org/abs/1804.01626), Cosmos ([Tendermint](https://arxiv.org/abs/1807.04938)), Diem ([DiemBFT](https://developers.diem.com/papers/diem-consensus-state-machine-replication-in-the-diem-blockchain/2021-08-17.pdf)), [Jolteon](https://arxiv.org/abs/2106.10362),  Espresso Systems ([HotStuff](https://eprint.iacr.org/2023/397.pdf)), Dfinity ([Internet Computer Consensus](https://eprint.iacr.org/2021/632.pdf)) and Ethereum ([Casper](https://arxiv.org/pdf/1710.09437)).

In this post, we discuss key principles behind the design of partially synchronous blockchain protocols. These principles, in some form, apply to all of these protocols (even though the exact protocol specification may be different, and protocols may use slight variants of these ideas). In a [subsequent post](https://decentralizedthoughts.github.io/2025-02-14-PBFT/), we will elaborate on PBFT, a canonical and classic use of these principles.

## High-Level Approach

When viewed from 20,000 feet, the core approach taken by partial synchrony protocols is the following:

In each iteration, there is a designated party called the leader (or the primary). The leader collects a batch of transactions, orders them in a block and attempts to achieve consensus on this block.

Let us zoom in to figure out when we would obtain "good results" using this approach, and how exactly should we achieve consensus. Observe that if the designated leader is honest and the network is synchronous, then we can essentially run a Byzantine Broadcast protocol to achieve consensus. In each iteration, we will agree on a new block, thus adding to the parties' state machine replication log.

However, both of the requirements, namely, honesty of the leader, and synchrony in the network may not hold true. In fact, we do not know when they do not hold true. Thus, we need to account for situations where either or both of those are false, and ensure that the protocol is still safe and live. *What exactly can go wrong with either requirements?*

**Concern 1:** The leader is Byzantine. Such a leader can choose to send no block, or perhaps send conflicting blocks to parties, or selectively send them to only some parties. If the network is synchronous, the protocol may have consistency (agreement/safety) but not liveness.

**Concern 2:** The network is not synchronous. In this case, we may not have progress, and using a synchronous BB can cause agreement violation too.

## Attempt 1: Using a Reliable Broadcast (RBC) Protocol

To address these concerns, an approach is to rely on a protocol making a weaker assumption, e.g., an asynchronous Reliable Broadcast protocol instead. Let us consider one such asynchronous protocol from [this paper](https://arxiv.org/pdf/2102.07240) and also described in a previous [blog post](https://decentralizedthoughts.github.io/2021-09-29-the-round-complexity-of-reliable-broadcast/).

```
// Leader S with input b
send <propose, b>_S to all parties

// Party i (including the leader)
on receiving the first proposal <propose, b>_s from leader:
  send <vote, b>_i to all parties

on receiving <vote, b>_* signed by n-t distinct parties:
  forward <vote, b>_* signed by n-t distinct parties to all parties
  commit b
```

The protocol runs in two rounds where, in the first round the leader sends a proposal (block) to all parties. On receiving the first proposal from the leader, a party sends a vote on that proposal to all the parties. When a party receives $n-t$ distinct votes, it commits the value and sends the distinct votes to all parties. 

The first step of voting for a single proposal and then waiting for $n-t$ vote messages ensures that different parties cannot commit on different values. In particular, any two sets of $n-t$ must intersect at $\geq n-2t \geq t+1$ parties. Since honest parties vote for only a single proposal, two different proposals cannot both receive $n-t$ votes.

The second step of forwarding the $n-t$ distinct votes to all parties ensures that if one honest party commits, then eventually all honest parties commit too.

Under asynchrony, the protocol achieves agreement, i.e., two honest parties will not disagree on the output) and validity, i.e., if the leader is honest then eventually all honest parties will output the leader’s input.


***Does this work for our purpose in the high-level approach for partial synchrony described earlier?*** The agreement property works well, but the validity part does not. In particular, validity only holds *eventually* in an asynchronous reliable broadcast protocol and *when* the leader is honest. If the leader is Byzantine, then we may not commit on anything and end up waiting forever. This guarantee is not acceptable in a state machine replication protocol where the goal is to agree on a sequence of blocks. In general, when we reach such a state where a party has not committed on a block, it does not know whether this is because the leader is Byzantine or because the network is not currently synchronous.

A typical approach to address this situation is to change leaders after some time (in fact, most of the blockchain protocols change leaders after every iteration). The hope with changing leaders is that, we would eventually reach a state where the leader is honest and the network will become synchronous (GST would have reached). At that point, we would start deciding blocks in the protocol.

Thus, to summarize, parties run the protocol in iterations wherein, in an iteration, a designated leader attempts agreement on a block. Due to the agreement property of the reliable broadcast protocol, two honest parties will never disagree. However, it may be possible that not all parties commit within a time bound, due to which we change leaders in the next iteration.

***What happens if some honest party has committed on a block in an iteration but not all honest parties have?*** This can happen when the network is asynchronous. For concreteness, say a party $P_i$ has committed a block $b$ at some position in the log. In such situations, we need subsequent leaders to ensure that all parties commit on the block $b$ at the same position in the log. How does a new leader learn about this block? It turns out that the above RBC protocol doesn't suffice; we modify it to ensure subsequent leaders have a means to learn about this block.

## Attempt 2: A Modified Protocol within an Iteration

```
// Leader S with input b
send <propose, b>_S to all parties

// Party i (including the leader)
on receiving the first proposal <propose, b>_s from leader:
  send <vote, b>_i to all parties

on receiving <vote, b>_* signed by n-t distinct parties:
  C(b): certificate with n-t distinct votes on b
  send <vote2, b, C(b)>_* to all parties        // Lock on b
  
on receiving <vote2, b>_* signed by n-t distinct parties:
  forward the n-t vote2 messages to all parties
  commit b
```

The first step involving the first round of votes still guarantees that parties cannot disagree. However, the decision is delayed by one more round of votes to ensure subsequent leaders can learn of a value that may have been committed in this iteration. In particular, after receiving $n-t$ distinct first round of votes, parties collect them as a *certificate* and send this certificate to all parties as another round of votes, denoted vote2. On receiving $n-t$ distinct vote2 messages, a party commits. When a party obtains a certificate and chooses to send a vote2 message, we say that the party is *locked* on this value. Thus, if a party $P_i$ commits $b$ in this iteration, it is guaranteed that at least $n-t$ parties, and thus, at least $n-2t \geq t+1$ honest parties are locked on $b$ in this iteration. In essence, the honest parties locked on $b$ guard the safety of $P_i$'s commit and ensure that any conflicting block proposed in subsequent iterations will not be committed. This principle is commonly referred to as the ***Lock-Commit paradigm***, i.e., if one party commits, then at least $n-2t \geq t+1$ lock on the committed value. 

***How exactly does a subsequent leader learn about the potentially committed value?*** If the leader collects $n-t$ statuses of locks in the next iteration, then at least one of the $n-2t \geq t+1$ honest locks will definitely reach the leader enabling it to propose the next block appropriately. Thus, an honest leader can always choose to propose the correct value. Well, *what if a Byzantine leader chooses to ignore the lock and propose a value inconsistent with the commit?* Addressing this question, requires the leader to somehow prove that it is indeed proposing the correct value. As we will see in the next posts, different protocols will deal with this issue differently.

Coming back to the big picture, the high-level sketch for partial synchrony protocols look like the following:

In each iteration, do the following:

**Step 1:** A designated leader learns if there is some block "in progress", i.e., potentially committed by some party, in previous iterations. This is done by learning the locks from sufficiently many parties.

**Step 2:** The leader then runs the modified reliable broadcast protocol with the block in progress (or a new block). In the proposal, it shares an appropriate proof that enables parties to vote on the proposal.

Armed with this intuition, in the [next post](https://decentralizedthoughts.github.io/2025-02-14-PBFT/) we will describe the Practical Byzantine Fault Tolerance (PBFT) protocol.

We thank Nibesh Shrestha for feedback on this post.

Please leave comments on [X](). 
