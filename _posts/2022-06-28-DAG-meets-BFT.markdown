---
title: DAG Meets BFT - The Next Generation of BFT Consensus
date: 2022-06-28 08:00:00 -04:00
author: Alexander Spiegelman
tags:
- consensus
- research
---

This post explains in simple words a recent development in the theory and practice of directed acyclic graph-based (DAG-based) Byzantine Fault Tolerance (BFT) consensus, published in three prestigious peer-reviewed conferences, and currently being implemented by several Blockchain companies, e.g., Aptos, Celo, Mysten Labs, and Somelier.


* [DAG-Rider: All You Need Is DAG](https://arxiv.org/abs/2102.08325) (PODC 2021). 
[I. Keidar,  E. Kokoris-Kogias, O. Naor, A. Spiegelman]
* [Narwhal&Tusk](https://arxiv.org/abs/2105.11827) (EuroSys 2022 **Best paper award**) 
[G. Danezis, E. Kokoris-Kogias, A. Sonnino, A. Spiegelman]
* [Bullshark](https://arxiv.org/abs/2201.05677) (To appear at CCS 2022) 
[A. Spiegelman, N. Giridharan, A. Sonnino, E. Kokoris-Kogias]

**TL;DR: Decoupling data dissemination from metadata ordering is the key mechanism to allow scalable and high throughput consensus systems. Moreover, using an efficient implementation of a DAG to abstract the network communication layer from the (zero communication overhead) consensus logic allows for embarrassingly simple and efficient implementations (e.g., more than one order of magnitude throughput improvement compared to Hotstuff).**


## DAG-based Consensus

In the context of Blockchain, BFT consensus is a problem in which $n$ validators, $f$ of which might be Byzantine, try to agree on an infinitely growing sequence of transactions. The idea of DAG-based BFT consensus (e.g., [HashGraph](https://eclass.upatras.gr/modules/document/file.php/CEID1175/Pool-of-Research-Papers%5B0%5D/31.HASH-GRAPH.pdf) and [Aleph](https://arxiv.org/abs/1908.05156)) is to separate the network communication layer from the consensus logic. Each message contains a set of transactions, and a set of references to previous messages. Together, all the messages form a DAG that keeps growing -- a message is a vertex and its references are edges.

The consensus logic adds zero communication overhead. That is, each validator independently  looks at its local view of the DAG and totally (fully) orders all the vertices without sending a single extra message. This is done by interpreting the structure of the DAG as a consensus protocol, i.e., a vertex can be a proposal and an edge can be a vote.

Importantly, due to the asynchronous nature of the network, different validators may see slightly different DAGs at any point in time. A key challenge then is how to guarantee that all the validators agree on the same total order.



#### Round-based DAG

In a round-based DAG (first introduced in [Aleph](https://arxiv.org/abs/1908.05156)), each vertex is associated with a round number. Each validator broadcasts one message per round and each message references at least $n-f$ messages. That is, to advance to round $r$, a validator first needs to get $n-f$ messages (from different validators) in round $r-1$. Below is an illustration of what the local view of some validator of a round-based DAG might look like:

![](https://i.imgur.com/HSyNhAC.png =x300)

#### Non-equivocation


[Aleph](https://arxiv.org/abs/1908.05156) and [DAG-Rider](https://arxiv.org/abs/2102.08325) use reliable broadcast to disseminate the vertices, which guarantees that all honest validators eventually deliver the same vertices and all vertices by honest validators are eventually delivered. Therefore:

> For any validator v and round r, if two validators have a vertex from v in round r in their local views, then both validators have exactly the same vertex (same transactions and references). 

>Hence, recursively, the vertex's causal history in both local views is exactly the same. 

The non-equivocation property eliminates the ability of Byzantine validators to lie, which drastically simplifies the consensus logic. As we explain shortly, [Narwhal](https://arxiv.org/abs/2105.11827) and [Bullshark](https://arxiv.org/abs/2201.05677) provide an efficient reliabile broadcast implementation.


#### Network speed throughput and chain quality


Once a vertex $v$ is committed via the consensus protocol, $v$’s entire causal history (all vertices for which there is a path from $v$ to them ) can be immediately ordered. This allows for:
* Perfect utilization of the network communication:
    * Messages are never wasted (as opposed to, for example, a vote on a proposal that is never committed in a monolithic protocol).
    * Total consensus throughput is **network speed** even if the consensus latency is high.
* Chain Quality. Since every round in v’s causal history contains at least n-f vertices, at least half (>f) of the vertices ordered in every round were broadcast by honest parties.


#### Protocol comparison

[DAGRider](https://arxiv.org/abs/2102.08325), [Tusk](https://arxiv.org/abs/2105.11827) , and [Bullshark](https://arxiv.org/abs/2201.05677) are all *zero communication* overhead consensus protocols to order the DAG’s vertices. That is, given a local view of a round-based DAG as described above, these protocols totally order vertices just by  locally interpreting the DAG structure (without sending any additional messages).

The table below summarizes the main differences.  Latency is measured by the number of DAG rounds required in between two commits. All protocols guarantee liveness even against a worst-case asynchronous adversary. Due to the [FLP](https://groups.csail.mit.edu/tds/papers/Lynch/jacm85.pdf) lower bound, randomness is required to solve asynchronous consensus, hence the latency is measured in expectation. Fairness means that even slow validators are able to contribute to the sequence of committed vertices (total order). 

|  |   Common case round latency  |  Asynchronous round latency   | Garbage collection | Fairness |
| -------- | --- | --- | -------- | -------- |
| [DAGRider](https://arxiv.org/abs/2102.08325)   |  4   |  E(6)   |  no   |   yes                |
| [Tusk](https://arxiv.org/abs/2105.11827)        |  3   |  E(7)   |  yes  |   no                 |
| [Bullshark](https://arxiv.org/abs/2201.05677)   |  2   |  E(6)   |  yes  | during synchrony     |

In this post we focus on [Bullshark](https://arxiv.org/abs/2201.05677), which offers better properties compared to the others.

#### Garbage collection

As the DAG grows indefinitely, it is necessary to garbage collect vertices from old rounds. As explained in more detail below, [Bullshark](https://arxiv.org/abs/2201.05677) provides garbage collection under all conditions with fairness during synchronous periods. This is the best we can hope for, because, as we will explain shortly, it's impossible to provide both garbage collection and fairness during asynchronous periods.


## Narwhal: Scalability and Throughput Breakthrough 

The main takeaway from the [Narwhal&Tusk](https://arxiv.org/abs/2105.11827) paper is that in scalable and high throughput consensus systems, ***data dissemination should be reliable and decoupled from the ordering mechanism.*** 

The Narwhal system implements a highly scalable and efficient DAG construction, which together with Tusk/Bullshark, sequences 100k+ transactions per second (tps) in a geo-replicated environment while keeping latency below 3s. For comparison, Hotstuff sequences less than 2k tps in the same environment.

Moreover, since data dissemination is completely symmetric among validators, the system is resilient to faults (a weak spot in many previous systems) -  tps is only affected because faulty validators do not disseminate data. 

Each validator consists of a number of workers and a primary. Workers continuously stream batches of data to each other and forward the digests of the batches to their primaries. The primaries form a round-based DAG on metadata (vertices contain digests). Importantly, the data is disseminated by the workers at network speed regarding the metadata DAG construction by the primaries. To form the DAG, validators use the follwoing [broadcast protocol](https://link.springer.com/book/10.1007/978-3-642-15260-3) that satisfies reliable broadcast properties with a linear number of messages on the critical path.

In each round (see Figure 2 in [Narwhal&Tusk](https://arxiv.org/abs/2105.11827) for illustration):
1. Each validator prepares and sends to all other validators a message with the metadata corresponding to the DAG vertex: i.e. batch digests and n-f references to vertices from the previous round.
1. Upon receiving such a message, a validator replies with a signature if:
    * Its workers persisted the data corresponding to the digests in the vertex (for data-availability).
    * It has not replied to this validator in this round before (for non-equivocation). 
1. The sender forms a quorum certificate from n-f such signatures and sends it back to the validators as part of its vertex for this round. 
2. A validator advances to the next round once it receives n-f vertices with valid certificates.


The purpose of the quorum certificates is threefold:

* **Non-equivocation:** since validators sign at most one vertex per validator per round, quorum intersection guarantees non-equivocation on the DAG. That is, Byzantine validators cannot get quorum certificates on two different vertices in the same round.
* **Data availability:** since validators sign only if they locally store the data corresponding to the digests in the vertex, when a quorum certificate is formed it is guaranteed that the data will be available for any validator to later retrieve. 
* **History availability:** since certified blocks contain the certificates of the blocks from the previous round, a certificate of a block guarantees the availability of the entire causal history of the block. A new validator can join by learning the certificates of just the prior round. This simplifies garbage collection.

The separation between data dissemination and the metadata ordering guarantees network speed throughput regardless of the DAG construction speed or the latency of the consensus used for the ordering. Data is disseminated at network speed by the workers, and the DAG contains digests that refer to all the disseminated data. Once a vertex in the DAG is committed, the vertex's entire causal history (that contains most of the disseminated data) is ordered. 

## The Bullshark Protocol

The [Bullshark](https://arxiv.org/abs/2201.05677) paper presents two versions of the protocol. The first is an asynchronous protocol with a 2-round fast path during synchrony, and the second is a partially synchronous 2-round protocol. This blog post describes the second, i.e. the partially synchronous, version. 

Compared to previous partially synchronous BFT consensus protocols (e.g., [PBFT](https://moodlearchive.epfl.ch/2020-2021/pluginfile.php/2452092/mod_resource/content/1/castro99practical.pdf), [SBFT](https://www.researchgate.net/profile/Alin-Tomescu/publication/324245804_SBFT_a_Scalable_Decentralized_Trust_Infrastructure_for_Blockchains/links/5ad4b960aca272fdaf7bf982/SBFT-a-Scalable-Decentralized-Trust-Infrastructure-for-Blockchains.pdf), [Tendermint](https://knowen-production.s3.amazonaws.com/uploads/attachment/file/1814/Buchman_Ethan_201606_Msater%2Bthesis.pdf)/[Hotstuff](https://arxiv.org/pdf/1803.05069.pdf)), Bullshark has (arguably) the simplest implementation (200 lines of code on top of the Narwhal system).
 
When it comes to the simplicity of consensus protocols, the devil is always in the details, in particular, the view-change and view-synchronization mechanisms. Some allegedly simple consensus protocols (e.g., Hotstuff and Raft), present happy path and hide synchronization details. In fact, the Hotstuff protocol was adopted for the Diem project due to its alleged simplicity, but the engineering team soon found out that the Pacemaker black-box (that was magically assumed to synchronize the views in the paper), was quite complex, tricky to implement in production, and was a serious bottleneck when experiencing faults.

**[Bullshark](https://arxiv.org/abs/2201.05677) needs neither a view-change nor a view-synchronization mechanism!**

Since the DAG encodes full information, there is no need to "agree" on skipping and discarding slow/faulty leaders via timeout complaints. Instead, as explained shortly, once a validator commits an anchor (leader) vertex $v$ on the DAG, it traverses back over $v$'s causal history and orders anchors that it previously skipped but could have been committed by other validators. As for synchronization, the all to all communication nature of constructing the round-based DAG takes care of it.

Moreover, the DAG construction is leaderless and enjoys perfect symmetry and load balancing between validators. DAG vertices are totally ordered without any additional communication among the validators. Instead, each validator locally interprets the structure of its view of the DAG. Below is an illustration of the [Bullshark](https://arxiv.org/abs/2201.05677) protocol with $n=4$ and $f=1$:


![](https://i.imgur.com/zu1DbtK.png =x300) 


Each odd round in the DAG has a predefined anchor vertex (highlighted in solid green above) and the goal is to first decide which anchors to commit. Then, to totally order all the vertices in the DAG, a validator goes one by one over all the committed anchors and orders their causal histories by some deterministic rule. Anchor 2 causal history is marked by green vertices in the above figure.

![](https://i.imgur.com/PkiC2vk.png =x300)

Each vertex in an even round can contribute one vote for the previous round anchor. In particular, a vertex in round $r$ votes for the anchor of round $r-1$ if there is an edge between them.  The commit rule is simple: an anchor is committed if it has at least $f+1$ votes. In the figure above, A2 is committed with 3 votes, whereas A1 only has 1 vote and is not committed.

Recall that due to the asynchronous nature of the network, the local views of the DAG might differ for different validators. That is, some vertices might be delivered and added to the local view of the DAG of some of the validators but not yet delivered by the others. Therefore, even though some validators have not committed A1, others might have.


![](https://i.imgur.com/zXPx8mz.jpg)


In the example above, validator 2 sees two ($f+1$) votes for anchor A1 and thus commits it even though validator 1 has not. Therefore, to guarantee total order (safety), validator 1 has to order anchor 1 before anchor 2. To achieve this, Bullshark relies on quorum intersection: 


> Since the commit rule requires $f+1$ votes and each vertex in the DAG has at least *n-f* edges to vertices from the previous round, it is guaranteed that if some validator commits an anchor A then all future anchors will have a path to at least one vertex that voted for A, and thus will have a path to A.

Therefore, we get the following corollary:

> **Safe to skip:** if there is no path to an anchor A from a future anchor, then it is guaranteed that no validator committed A and it is safe to skip A. 

The mechanism to order anchors is the following: when an anchor $i$ is committed, the validator checks if there is a path between anchor $i$ to $i-1$. If this is the case, anchor $i-1$ is ordered before $i$ and the mechanism is recursively restarted from $i-1$. Otherwise, anchor $i-1$ is skipped and the validator checks if there is a path between $i$ to $i-2$. If there is a path, $i-2$ is ordered before $i$ and the mechanism is recursively restarted from $i-2$. Otherwise, anchor $i-2$ is skipped and the process continues in the same way. The process stops when it reaches an anchor that was previously committed (as all the anchors before it are already ordered). 

![](https://i.imgur.com/k6zzHEy.png)

In the above figure, anchors A1 and A2 do not have enough votes to be committed and once the validator commits A3 it has to decide whether to order them. Since there is no path from A3 to A2, by corollary safe-to-skip A2 can be skipped. However, since there is a path between A3 and A1, A1 is ordered before A3 (it is possible that some validator committed A1). Next, the validator needs to check if there is a path between A1 to A0 (not in the figure) to decide whether to order A0 before A1.

Please see below details on the specific DAG construction and refer to the [Bullshark](https://arxiv.org/abs/2201.05677) paper for formal pseudocode and rigorous Safety and Liveness proofs. 

## Fairness and Garbage Collection 

A desired fairness property in a Blockchain system is that no validator is ignored and even the slow validators can contribute transactions to the total order. In the context of DAG-based BFT, every validator should be able to add vertices to the DAG.

Recall that $f$ validators can be byzantine and thus never broadcast their vertices. Since it is impossible to distinguish between such validators and slow validators during asynchronous periods, honest validators should not wait for more than $n-f$ vertices in order to advance to the next round. As a result, a slow validator might always be late and never add a vertex to the DAG (i.e., other validators advance to round $i$ before receiving its vertex at round $i-1$). 

To solve this problem, [DAG-Rider](https://arxiv.org/abs/2102.08325) introduced weak edges that point to vertices from older rounds. These edges are ignored by the consensus mechanism (i.e., they do not count as votes). Their only purpose is to help all vertices by all honest validators to eventually be added to the DAG (and become totally ordered as a part of a future anchor’s causal history. See an illustration below:


![](https://i.imgur.com/Ru0HAWV.png =x300)


The drawback of this approach is garbage collection. In asynchrony it might take an unbounded time for a vertex to be delivered, and thus it is never safe to garbage collect a round for which not all vertices are in the DAG. This is unacceptable from a practical point of view.

**[Bullshark](https://arxiv.org/abs/2201.05677), on the other hand, establishes a sweet spot between garbage collection and fairness.** The DAG is constantly garbage collected and fairness is guaranteed during synchronous periods.

To accomplish this, validators attach their local time to each vertex they broadcast. Once an anchor is committed and ready for ordering, the anchor’s timestamp is computed as a median of times in its parents’ vertices. Then, while traversing back over the anchor’s causal history (to deterministically order it), a timestamp of each round is computed as the median of times in the round vertices. When a round $r$ whose timestamp is smaller than the anchor’s timestamp by more than some predefined $\Delta$ time is reached, then $r$ and all the rounds smaller than $r$ are garbage collected. Vertices that have yet been added to the DAG in these rounds will need to be re-broadcast in future rounds. However, it is guaranteed that if a slow validator is able to broadcast its vertex in *delta* time, the vertex will be added to the DAG and totally ordered. 

![](https://i.imgur.com/bR4XDV2.png =x350)

Once the anchor in the above figure is ordered, its timestamp is computed to 5 based on its parents' times. The timestamps of rounds $i,i+1,i+2$, and $i+3$, are computed based on the times in the vertices in these rounds in the anchor’s causal history. In this example, $\Delta =2$ and thus round $i$ and all rounds below it are garbage collected. Validator 4 is slow, but since it was able to broadcast its vertex in time, the vertex is ordered thanks to the weak links.

## Logical vs Physical DAG

[DAGRider](https://arxiv.org/abs/2102.08325) and [Tusk](https://arxiv.org/abs/2105.11827) are randomized asynchronous protocols that build the DAG in network speed: once $n-f$ vertices in round $r$ are delivered, validators broadcast their vertices for round $r+1$. No information from the consensus level is required to build the DAG as the randomness for each round is produced via threshold signatures - each vertex includes a signature share on the vertex’s round number, which can be easily precomputed.

[Bullshark](https://arxiv.org/abs/2201.05677) leverages synchronous periods to reduce commit latency. Ideally, for implementation simplicity, it would be great to keep the clean separation between networking (DAG abstraction) and the local consensus logic to order the DAG.

> However, there is rarely magic in the world and we know that due to [FLP](https://groups.csail.mit.edu/tds/papers/Lynch/jacm85.pdf), a deterministic consensus protocols cannot guarantee liveness in partial synchrony without timeouts.

Therefore, any partially synchronous DAG-based protocol will need to integrate timeouts and break the separation between the DAG networking abstraction and the consensus layer in one way or another. 

For [Bullshark](https://arxiv.org/abs/2201.05677) we compared two alternatives:
* Physical DAG: use consensus timeouts to build the DAG.
* Logical DAG: add a logical DAG on top of the physical DAG to integrate the timeouts.


### Physical DAG
The problem in advancing rounds whenever $n-f$ vertices are delivered is that validators might not vote for the anchor even if the validator that broadcast it is just slightly slower than the rest. 

To deal with this, [Bullshark](https://arxiv.org/abs/2201.05677) integrates timeouts into the DAG construction. In addition to waiting for $n-f$ vertices in each round, validators wait either for the anchor or a timeout in an odd round. Similarly, in an even round, validators wait for either f+1 vertices that vote for the anchor, or 2f+1 vertices that do not, or a timeout.

Note that data is still disseminated in network speed as this is done by the workers (outside of the DAG construction) by the underneath [Narwhal](https://arxiv.org/abs/2105.11827) system.


### Logical DAG

In brief, the idea of separating DAG into physical and logical layers is that the physical DAG keeps advancing in network speed, i.e., validators advance physical rounds immediately after $n-f$ vertices are delivered. The logical DAG is piggybacked on top of the physical DAG - each vertex has an additional bit that indicates whether the vertex belongs to the logical DAG. A logical edge between two logical vertices exists if there is a physical path between them. The timeouts are integrated into the logical DAG similarly to how they are integrated into the physical DAG in the description above. The consensus logic runs on top of the logical DAG and once an anchor is committed, its entire causal history on the physical DAG is ordered.

![](https://i.imgur.com/KrFQ9oN.jpg)

In the example above, the right figure is the logical DAG that is piggybacked on top of the physical DAG in the left figure. Validator 1 gets vertices 1,2, and 3 in the physical DAG before getting vertex A1. Therefore, it advances to round two in the physical DAG without marking its vertex as logical. Its vertex in round 3, however, is marked as logical even though it does not have a path to A1 because its local timeout expired.

### Comparison in practice 

One may expect that the logical DAG approach would increase the system throughput because validators never wait for a timeout to broadcast vertices on the physical DAG. However, since [Narwhal](https://arxiv.org/abs/2105.11827) separates data dissemination from metadata this makes no difference in practice. [Narwhal](https://arxiv.org/abs/2105.11827) workers keep broadcasting batches of transactions at network speed and the DAG contains only metadata information such as batches digests. Therefore, if the DAG construction is slowed down due to a timeout, the next block will simply include more digests. Moreover, the latency in the logical approach may actually increase -- this is because if a logical vertex is not ready to be piggybacked when the physical vertex is broadcast, it will need to wait for the next round.

We evaluated and compared both approaches and the physical DAG outperformed the logical DAG. Throughput with the logical DAG was lower perhaps because the logical DAG approach consumes more memory and bandwidth, and latency was higher because of the reason mentioned above. 


In general, from our experience, slightly back pressuring (slowing down) the DAG construction leads to maximum performance since the vertices contain more digests. Moreover, the logical DAG approach is likely to require more complex implementation. 


## Bullshark Evaluation

We implemented [Bullshark](https://arxiv.org/abs/2201.05677) in Rust in less than 200 LOC on top of the [Narwhal](https://arxiv.org/abs/2105.11827) DAG system. Our implementation uses tokio for asynchronous networking, ed25519-dalek for elliptic curve-based signatures, and Rocksdb for persistent data storage. BullShark does not require additional protocol messages or cryptographic tools compared to Narwhal. The code, as well as the Amazon web services orchestration scripts and measurement data required to reproduce the results, are [open-sourced](https://github.com/asonnino/narwhal/tree/bullshark). 

We evaluated [Bullshark](https://arxiv.org/abs/2201.05677) against [Tusk](https://arxiv.org/abs/2105.11827) and Hotstuff in a geo-replicated environment. Since the vanilla Hotstuff protocol produces very poor performance in our setting (never exceeds 1,800 tps, see Figure 6 in [Narwhal](https://arxiv.org/abs/2105.11827)), we also implemented an improved version of Hotstuff by applying insight from [Narwhal](https://arxiv.org/abs/2105.11827), i.e., we separated data dissemination and used HotStuff to order metadata only. 


The figure below illustrates the latency and throughput of [Bullshark](https://arxiv.org/abs/2201.05677), [Tusk](https://arxiv.org/abs/2105.11827), and an improved version of HotStuff for varying numbers of validators in the failure-free case:

![](https://i.imgur.com/zQDHz4G.png)

As the figure shows, [Bullshark](https://arxiv.org/abs/2201.05677) strikes a balance between the high throughput of Tusk and the low latency of HotStuff. Its throughput is 2x higher than HotStuff, reaching 110,000 tx/s (for a committee of 10) and 130,000 tx/s (for a committee of 50), while its latency is 33% lower than [Tusk](https://arxiv.org/abs/2105.11827). This is because [Bullshark](https://arxiv.org/abs/2201.05677) commits in two rounds on the DAG while Tusk requires 3. Both [Bullshark](https://arxiv.org/abs/2201.05677)  and [Tusk](https://arxiv.org/abs/2105.11827) scale better than HotStuff when increasing the committee size due to the underlying [Narwhal](https://arxiv.org/abs/2105.11827) system. 

The figure below depicts the performance of [Bullshark](https://arxiv.org/abs/2201.05677), [Tusk](https://arxiv.org/abs/2105.11827), and an improved version of HotStuff when a committee of 10 validators suffers 1 to 3 crash faults:

![](https://i.imgur.com/i1v9E56.png =x400)

HotStuff suffers a massive degradation in throughput as well as a dramatic increase in latency. For 3 faults, the throughput of HotStuff drops by over 10x and its latency increases by 15x compared to no faults. In contrast, both [Bullshark](https://arxiv.org/abs/2201.05677) and [Tusk](https://arxiv.org/abs/2105.11827) maintain high throughput: the underlying [Narwhal](https://arxiv.org/abs/2105.11827) DAG continues collecting and disseminating transactions despite the crash faults, and is not overly affected by the faulty validators. The reduction in throughput is in great part due to losing the capacity of faulty validators to disseminate transactions. When operating with 3 faults, both [Bullshark](https://arxiv.org/abs/2201.05677) and [Tusk](https://arxiv.org/abs/2105.11827) provide a 10x throughput increase and about 7x latency reduction with respect to HotStuff.

> Many thanks to Rati Gelashvili, Eleftherios Kokoris-Kogias, and Alberto Sonnino for helping shape this blog post.
### 