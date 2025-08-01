---
title: Safe Permissionless Consensus
date: 2022-06-21 08:00:00 -04:00
tags:
- research
author: Youer Pu, Lorenzo Alvisi, and Ittay Eyal
---

Nakamoto's consensus protocol works in a permissionless model, where nodes can join and leave without notice. However,  it guarantees agreement only probabilistically. Is this weaker guarantee a necessary concession to the severe demands of supporting a permissionless model? 

We show that, at least in a benign failure model, it is not. We present _Sandglass_, the first permissionless consensus algorithm that guarantees deterministic agreement and termination with probability 1 under general omission failures. Like Nakamoto, Sandglass adopts a _hybrid synchronous_ communication model, where, at all times, a majority of nodes (though their number is unknown) are correct  and synchronously connected, and allows nodes to join and leave at any time. 

## Permissionless Blockchains with Deterministic Consistency? 

The publication of Bitcoin’s white paper, besides jumpstarting an industry whose market is expected to reach [over $67B by 2026](https://www.researchandmarkets.com), presented the distributed computing community with a fundamental question: how should the agreement protocol at the core of Nakamoto’s blockchain construction be understood in light of the combination of consensus and state machine replication that the community has studied for over 30 years? The similarities are striking: in both cases, the goal is to create an append-only distributed ledger that everyone agrees upon, which Nakamoto calls a blockchain. But so are the differences. Unlike traditional consensus algorithms, where the set of participants _n_ is known and can only be changed by running an explicit reconfiguration protocol, Nakamoto’s consensus is permissionless: it does not enforce access control and allows the number and identity of participants to change without notice. To operate under these much weaker assumptions, Nakamoto adopts a new mechanism for reaching agreement: since the precise value of _n_ is unknown, Nakamoto forsakes explicit majority voting and relies instead on a Proof of Work (PoW) lottery mechanism [19], designed to drive agreement towards the blockchain whose construction required the majority of the computational power of all participants. Finally, whereas traditional consensus protocols guarantee agreement deterministically, NC can do so only probabilistically; furthermore, that probability approaches 1 only as termination time approaches infinity. 

> **Is settling for these weaker guarantees the inevitable price of running consensus in a permissionless setting?**

Defying [Betteridge](https://en.wikipedia.org/wiki/Betteridge%27s_law_of_headlines), the answer is yes – we show that one can do much better. 

In a [technical report](https://eprint.iacr.org/2022/796) we publish today, we show that these weaker probabilistic guarantees do not arise from permissionlessness, but rather from the choice of a probabilistic PoW mechanism: In Bitcoin (and all PoW blockchains), the miners provide only statistical proof they have calculated a certain number of hash functions. The safety of these protocols relies on the majority of computational power generating the majority of blocks; however, with some probability, even a small miner might get lucky and generate the majority of blocks. 

<p align="center">
  <img width="350" src="https://images.unsplash.com/photo-1633265486501-0cf524a07213?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1170&q=80">
</p>

## Sandglass 

We show that if instead we can send _all work_, achieving a full (rather than statistical) PoW, it is possible to achieve _deterministic safety in a permssionless model_. 

We present _Sandglass_, a permissionless consensus algorithm that guarantees deterministic agreement and terminates with probability 1. It operates in a model based on Nakamoto's. Our model allows an arbitrary number of participants to join and leave the system at any time and stipulates that at no time the number of participants exceeds an upper bound N (though the actual number _n_ of participants at any given time is unknown). Further, like Nakamoto's, it is hybrid synchronous, in that, at all times, a majority of participants are correct and able to communicate synchronously with one another. We call these participants good; our protocol's safety and liveness guarantees apply to them. Participants that are not good (whether because they crash, perform omission failures, and/or experience asynchronous network connections) we call _defective_. 

Sandglass proceeds in virtual rounds. Nodes propose a value by broadcasting it;  in the first round, each node proposes its initial value; in subsequent rounds, nodes propose a value chosen among those received in the previous round. Values come with an associated priority, initialized to 0. The priority of _v_  depends on the number of consecutive rounds during which _v_ was the only value received by the node proposing _v_ -- whenever a node receives a value other than _v_, it resets _v_'s  priority back to 0. 
When proposing a value in a given round, node _p_ selects the highest priority value received in the previous round; if multiple values have the same priority, then it selects randomly among them. 
A node can safely decide a value _v_ after sufficiently many consecutive rounds in which the proposals it receives unanimously endorse _v_ (i.e., when _v_'s priority is sufficiently high); and termination follows from the non-zero probability that the necessary sequence of unanimous, consecutive rounds will actually eventually occur.

The keen eye might notice that Sandglass is surprisingly reminiscent of [Ben-Or's classic consensus protocol](https://decentralizedthoughts.github.io/2022-03-30-asynchronous-agreement-part-two-ben-ors-protocol/). However, Ben-Or establishes that it is safe for a node to decide _v_ after having observed two consecutive, unanimous endorsements of _v_. This is because any two majority sets of its fixed set of _n_ nodes will intersect in at least one correct node. 
This approach is clearly no longer feasible in a permissionless setting, where _n_ is unknown and the set of nodes can change at any time. Instead, Sandglass’s approach to establish safety is inspired by one of the key properties of  Nakamoto's PoW: whatever the value of _n_, whatever the identity of the nodes participating in the protocol at any time,  the synchronously connected majority of good nodes will be faster in proceeding to new rounds than the defective nodes that do not communicate with good nodes. So much faster, that eventually defective nodes either propose the same value as the good nodes, or their round is so far behind that they cannot affect the good nodes. 

<p align="center">
  <img width="350" src="https://i.pinimg.com/564x/5d/ea/d0/5dead0a5403ba51c7988315cc795e91a.jpg">
</p>
 
## Conclusion

The discovery that deterministic safety is possible in a permissionless setting leads to the question of whether there exists a protocol that also achieves deterministic termination in a hybrid synchronous model. Another natural question is whether there exists a deterministically-safe solution to consensus in a hybrid-synchronous model with Byzantine failures ([Lewis-Pye and Roughgarden](https://arxiv.org/pdf/2101.07095.pdf) have shown that a deterministic-consesus protocol does not exist). Answering these questions might pave the way to a qualitative improvement of permissionless systems that would provide deterministic guarantees; or, at the very least, give us more insight about the nature of consensus. 

Read more in our [technical report](https://eprint.iacr.org/2022/796). 

<a href="https://twitter.com/IttayEyal" class="twitter-follow-button" data-show-count="false">Follow @IttayEyal</a><script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
