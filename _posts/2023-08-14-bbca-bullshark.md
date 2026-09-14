---
title: The Differences between BBCA-Chain and Bullshark
date: 2023-08-14 08:00:00 -04:00
published: false
tags:
- research
author: Dahlia Malkhi, Chrysa Stathakopoulou, Ted Yin
---

In a recent post, we introduced [BBCA-Chain](https://blog.chain.link/bbca-chain-single-broadcast-consensus-on-a-dag/), a one-message consensus protocol on a DAG. This post explains the differences between BBCA-Chain and [Bullshark](https://arxiv.org/abs/2209.05633). The description below provides a piece-by-piece explanation by "migrating" Bullshark, step by step, into BBCA-Chain (familiarity with both is needed). 

The first part focuses on reducing latency, the second on removing layering constraints. In addition to the tangible latency improvements, overall the transformation makes the consensus protocol somewhat more simple. 


## Background

A consensus protocol allows a network of nodes to form a committed sequence of blocks. Quite naturally, early solutions operate in a sequential manner, extending the committed prefix one block at a time. Over the years, theoretical solutions reached optimal communication complexity ([HotStuff:2019](https://arxiv.org/abs/1803.05069)), and practical systems achieved throughput of tens-of-thousand tps ([Narwhal-HS:2022](https://sonnino.com/papers/narwhal-and-tusk.pdf)). At that point, allowing non-sequential transmissions became the next promising direction to break the sequential barrier and reach a higher throughput. 

A ha! Lamport causal-ordering comes to the rescue. Recent advances employ causally-ordered reliable broadcasts to allow blocks to be broadcast in parallel and become committed in bundles. The causal ordering of blocks forms a Direct Acyclic Graph (DAG). The cool idea is that nodes interpret their local DAGs and, because of causality, they reach consistent commit decisions forming a totally ordered sequence of blocks.

More specifically, nodes form a **backbone** sequence of leader-blocks on the DAG (see picture below). When a leader-block becomes committed, every block it causally references become committed as well. This allows great throughput.

However, the current generation of [DAG-riding solutions](https://decentralizedthoughts.github.io/2022-06-28-DAG-meets-BFT/) incurs increased latency and a complicated logic. For example, in Bullshark, each block in the DAG is sent via a consistent broadcast ("CBC") primitive, and it takes a minimum of $4$ chained CBCs for a block to become committed. The figure below illustrates Bullshark: leaders broadcast proposals on even layers of the DAG. Non-leaders can broadcast blocks on both odd and even layers. Blocks in odd-layers are interpreted as votes if they causally follow a leader proposal on the preceding layer. If there are $f+1$ votes in an odd layer for a leader proposal in the preceding layer, it becomes committed. 

![](https://hackmd.io/_uploads/SJnO-HB3h.png)

## Reducing Bullshark Latency

We first describe how to reduce Bullshark latency in three steps. 

### Step 1. Using BBCA for Leader-Blocks

By peeking inside the CBC protocol, we can observe that it already has multiple rounds of messages similar to a consensus protocol. [BBCA](https://blog.chain.link/bbca-chain-single-broadcast-consensus-on-a-dag/) adds a thin shim on top of CBC, that add reliability and allows "peeking" into the local state of the broadcast protocol. The key new feature property is a *Commit-Adopt* API: If a value is delivered by a BBCA broadcast, then a quorum peeking via `BBCA-probe()` would adopt it. Importantly, it is implemented on top of reliable broadcast completely locally without incurring additional communication. More details on implementing BBCA on top of CBC are provided later below.

The first step is to replace the CBC primitive by which leader-blocks are sent with a BBCA broadcast. This step achieves a one-broadcast consensus protocol, as well as reduces latency to reach consensus decisions.  

We also need to modify how a node "complains" if it times-out waiting in a "voting" layer for a leader-block: it first invokes a local `BBCA-probe()`, and then it embeds the result (`BBCA-adopt` or `BBCA-noadopt`) in its complaint broadcast (the one that doesn't follow the leader proposal).

The modified version, namely Bullshark using BBCA for leader-blocks and removing voting blocks, is depicted below.

![](https://hackmd.io/_uploads/BJU_ESS32.png)

The commit rule of Bullshark remains as before, but note that a BBCA block commits by itself, without any voting blocks. When a leader-block has in its causal past an embedded leader-block, it handles the embedded information like a normal leader-block.

This change reduces the latency to commit a **leader-block** from $2 \times$ CBC to $1 \times$ BBCA:

* In an all-all protocol, $2 \times$ CBCs take 4 trips and BBCA 3.
* In a linear protocol, $2 \times$ CBC takes 6 trips and BBCA 5.

All commits (both leader and non-leader blocks) depend on the latency for leader-block commits, hence this save $1$ network trip to commit every block on the DAG.

### Step 2. Getting Rid of Specialized Layers

Next, we apply further latency reduction on commiting **non-leader blocks**, by removing the dedicated layers for "voting"/"proposing" altogether. This requires a bit of explaining: 

In Bullshark, voting occurs on the layer that follows a leader-block, because voting blocks must causally follow the proposal they vote for. The first modification (above) already gets rid of voting blocks, but if a node times-out waiting for a leader-block, it needs to broadcast `adopt/no-adopt` in complaint-blocks. The trick is that compaint-blocks can occur on the same layer as the leader-block, because there is no causality reference.

The protocol is depicted below after this modification: On the left, a scenario without complaints, and on the right, one layer incurs compaints.

![](https://hackmd.io/_uploads/Bk64g0732.png)

This change reduces the high latency Bullshark incurs for non-leader blocks from $4 \times$ CBC (on blocks in previously "proposing" layers) to ($1 \times$ CBC + $1 \times$ BBCA). This saves--on top of one network trip saved for the leader-block to commit above--additional $2$ network trips in all-all protocols, and $3$ trips in linear protocols.

We remark that a similar reduction is achieved by a trick implemented by Mysten Labs. It interleaves two backbones, each formed by one Bullshark instance, where both are simultaneously operating on the same DAG but have alternating proposing and voting layers. Getting rid of specialized layers achieves the same reduction but seems simpler. 

### Step 3. Getting Rid of CBC for Non-Leader Blocks

Consensus on leader-blocks suffices to deterministically include unique blocks in the total ordering. Bullshark needs voting-blocks to be non-equivocating, but because we already got rid of voting-blocks, there is no need to use CBC for any non-leader block. 

This change allows further reduction in latency by $1$ network trip against CBC that uses an all-all protocol, and by $2$ network trips against a linear protocol.

We depict Bullshark without CBCs via "thin" blocks below.

![](https://hackmd.io/_uploads/ByeZbRQ3n.png)

It is worth noting that there is a tradeoff here: using CBC for non-leader blocks avoids keeping equivocating blocks in the DAG. 

### Putting 1-2-3 Together

The figure below depicts the overall improvement from Bullshark to BBCA-Chain: Bullshark before (right) and after (left). The relaxation of inter-layer constraints is discussed next.

![](https://hackmd.io/_uploads/Syz9_eX3n.png)

Applying all 3 steps and using an all-all regime for BBCA broadcast, we achieve a super simple single-broadcast protocol with a best-case latency of $4$ network trips. Not only is this a reduction of $8$ network trips from the best-case latency in Bullshark (for blocks on proposing layers, and factoring a linear CBC implementation), $4$ trips is optimal latency for Byzantine consensus. 

### Details on converting CBC to BBCA

We first briefly recall how nodes in Bullshark broadcast blocks.

Blocks are formed after a *smart mempool transport* pre-disseminates transactions and obtains a certificate of uniqueness and date-availability ("CERT") for them. This takes $2$ network trips done by worker-threads on the node: a worker-sender multicasts a transaction to all nodes, then nodes respond with signed acknowledgements and the worker aggregates $2f+1$ signatures into a certificate. The transaction dissemination by the smart mempool layer is not considered in the critical path of Consensus and not counted in our latency analysis. 

Whenever a node is ready to send a block in a new layer, it assembles multiple CERTs into a **block**, adds references to $2f+1$ delivered blocks in the previous layer, and employs a Consistent Broadcast (CBC) primitive that enforces uniqueness and causal ordering to send the block. 

In a **linear form**, CBC takes $3$ network trips:

1. A node multicasts the block to all nodes
2. After validating the format of a block, obtaining all causal predecessors, and nodes respond to the first broadcast by a sender in a layer with a signed acknowledgement over a hash of the block
3. The sender multicasts an aggregate containing $2f+1$ signed hashes. 

Nodes deliver a block into their local copy of the DAG once they receive the block with the aggregate signature. 

We now describe how to convert CBC into BBCA. In order to implement BBCA on top of linear CBC, we would delay the delivery another roundtrip:

4. Nodes respond to an aggregate signature by the sender with a signed acknowledgement over the aggregate signature
5. The sender multicasts an aggregate containing $2f+1$ signed aggregates. 

`BBCA-probe()` stops a node from participating in the BBCA protocol, and returns one of two values:

1. `BBCA-adopt(`$b$`)` if the node obtained an aggregate signature for block $b$
2. `BBCA-noadopt()` otherwise.

We remark that a similar implementation of BBCA can be constructed over an all-all "Bracha-style" CBC, adding one network trip. Because there is only one BBCA broadcast per layer, it might make sense to implement it via an all-all protocol and avoid signatures.

## Relaxing the Structured-DAG Layering

In addition to the commit latency reductions, we comment briefly on relaxing the sturcture-DAG layering constraints. 

Bullshark requires each block to reference $2f+1$ predecessors in the previous layer. This requirement is not needed for BBCA-Chain correctness and can be relaxed and fine-tuned by system designers to their needs. However, in order to preserve correctness of the consensus logic, relaxing the predecessor requirement must done with care.

In particular, leader-blocks at each layer must reference either the a leader-block in the previous layer or $2f+1$ complaint-blocks. In the original layered-DAG of Bullshark, this requirement is enforced at the DAG level. BBCA-Chain enforces this rule inside the BBCA broadcast primitive: nodes will not acknowledge a leader BBCA-broadcast if it does not fulfill it. 

We remark that system designers may choose to structure the DAG to address various other considerations. For example, a system may require $f+1$ predecessors for censorship resistence. Another system may require a constant number of predecessors to achieve certain parallelism. Additionally, systems may advaptively adjust the required number of predecessors at runtime based on their workload. Finally, structuring may also help with garbage collection and keeping node progress in sync at the network substrate level. Removing structured-layering from consensus logic shifts the fine-tuning of structuring outside the consensus logic. 

*Acknowledgements: We are grateful to George Danezis, Eleftherios Kokoris Kogias, and Alberto Sonnino for useful comments about this post.*
