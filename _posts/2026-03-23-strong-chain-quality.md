---
title: Strong Chain Quality
date: 2026-03-23 00:00:00 -05:00
tags:
- blockchain
author: Ittai Abraham, Pranav Garimidi, Joachim Neu
---

**Chain Quality (CQ)** is a core blockchain property. Roughly speaking, it says:
> Owning $3\%$ of the stake gives you inclusion rights over valid inputs of your choice in roughly $3\%$ of the blockspace ***over time***.

For Nakamoto style chains, this is called *Ideal CQ* (see [here](https://eprint.iacr.org/2014/765.pdf)). Chain quality was sufficient for early generations of blockchains that had low throughput, but modern blockchains have much higher bandwidth and can commit many transactions within a single block. This motivates a stronger, more fine-grained notion that captures the division of blockspace inside each block, rather than only the fraction of blocks averaged over time. 

We call it **Strong Chain Quality (SCQ)**:
> Owning $3\%$ of the stake guarantees inclusion of your valid inputs up to $3\%$ of the blockspace ***in every block***. 

In essence, SCQ gives stakeholders the ability to have *virtual lanes* inside a high-throughput blockchain that guarantee transaction inclusion. Here, we review the origins of CQ and SCQ and explain why SCQ is so useful. 

The core version of this Strong Chain Quality post appears on the [a16z Crypto research blog](https://a16zcrypto.com/posts/article/strong-chain-quality-for-blockspace-every-block/); the longer version here includes additional academic references and technical details.

## Chain Quality as a BFT Validity Property

BFT protocols must satisfy [safety, liveness, and validity properties](https://decentralizedthoughts.github.io/2019-06-27-defining-consensus/). A protocol that always outputs 0 satisfies both agreement (safety) and termination (liveness), but is useless in the sense that it performs no meaningful decision or computation. What's missing is *validity*. Modern blockchains typically require two critical validity properties:

1. [External Validity](https://www.iacr.org/archive/crypto2001/21390524.pdf): Typically means there is a deterministic binary function $isValid(B, state)$ that outputs true if the proposed block $B$ is valid based on the current $state$ of the state machine.
2. [Chain Quality](https://eprint.iacr.org/2014/765.pdf): In any sufficiently long segment of the chain after GST, the fraction of blocks proposed by honest parties is proportional to their fraction of the total stake.

Most pre-blockchain BFT systems were based on a fixed-leader paradigm that implemented external validity but not chain quality. Why is chain quality important for blockchains? 

## Chain Quality for blockchains

One of Bitcoin's key innovations, now present in virtually every blockchain, is the introduction of an **in-protocol reward mechanism** for block proposers: newly minted tokens and transaction fees are granted to the party that successfully appends a block to the state machine. These rewards are specified in the state-transition function and reflected in the resulting system state.

In traditional distributed computing, parties are split into *honest* and *malicious*. There is no need to reward honest parties for correct behavior; their honesty is assumed as part of the model. In the cryptoeconomic model, parties are modeled as *rational* actors, possibly with unknown utility functions, and the goal is to design incentives so that their profit-maximizing behavior aligns with the success of the protocol. Together with the in-protocol reward mechanism, this leads to the following idealized definition of Chain Quality:

**Chain Quality (CQ)**:
> A coalition that holds $X\%$ of the total stake has, after GST, probability $X\%$ of being the proposer of each block that enters the chain.

A chain that deviates from chain quality may allow coalitions to accumulate an outsized portion of the reward, hence disincentivizing honest behavior and threatening the security of the protocol.

Many modern blockchains satisfy, or aim to satisfy, this property. Some notable challenges:
* [Eyal and Sirer, 2013](https://webee.technion.ac.il/people/ittay/publications/btcProcFC.pdf) famously showed that Bitcoin does not satisfy ideal CQ, see Eyal's post on [Blockchain Selfish Mining](https://decentralizedthoughts.github.io/2020-02-26-selfish-mining/) and Remark 4 and the discussion of p. 6--7 in [the Bitcoin Backbone paper](https://eprint.iacr.org/2014/765.pdf) for more. Also see this [follow up post](https://decentralizedthoughts.github.io/2022-03-07-colordag-from-always-almost-to-almost-always-50-percent-selfish-mining-resilience/) for research efforts like Fruitchain and Colordag towards obtaining ideal CQ in the PoW setting.
* Obtaining Chain Quality for linear chains where each leader speaks once poses additional challenges. See recent works on [BG](https://arxiv.org/abs/2205.11652), Monad's [tail forking resistance](https://arxiv.org/abs/2502.20692) and [Carry](https://decentralizedthoughts.github.io/2025-09-27-carry-the-tail/).
* Chain Quality is also challenging in the context of Ethereum's [LMD GHOST](https://eth2book.info/latest/part2/consensus/lmd_ghost/) protocol (there, CQ issues are often called "reorgs") in the [ebb-and-flow model](https://decentralizedthoughts.github.io/2020-11-01-ebb-and-flow-protocols-a-resolution-of-the-availability-finality-dilemma/). See [Goldfish](https://eprint.iacr.org/2022/1171.pdf) for a recent survey of problems and the way to fix them.

In contrast, most modern proof-of-stake blockchains implement stake-weighted randomized leader rotation on PBFT-style protocols and therefore satisfy chain quality in a direct way.

## Strong Chain Quality 

When blockspace is abundant, there is no need to give a single proposer monopoly power over the content of the entire block. Instead, blockspace can be divided among multiple parties for the same block. The following cryptoeconomic definition of Strong Chain Quality captures this idea:

**Strong Chain Quality**:
> A coalition that holds $X\%$ of the total stake has, after GST, guaranteed inclusion of its valid inputs up to $X\%$ of the blockspace *in each block*.

This idealized property implicitly leads to the abstraction of *virtual lanes*, where coalitions effectively control a dedicated fraction of blockspace within each block. From an economic perspective, owning a virtual lane corresponds to holding a productive asset that may yield fees and MEV revenue. Competition among external entities to acquire and maintain such lanes, through stake accumulation, creates sustained demand for the underlying L1 token. The greater the economic value that a given lane can generate, the stronger the incentives to compete for stake, and the more value accrues to the L1 stake that governs access to that blockspace.

This abstraction allows for stronger notions of censorship resistance that are captured by the SCQ validity property of the protocol.

## Strong Chain Quality and Censorship Resistance

[Recent work](https://arxiv.org/abs/2301.13321) highlights the importance of censorship-resistant protocols that include all inputs from honest parties immediately rather than only eventually. SCQ can be viewed as an extension of this property to a setting with fixed block-capacity constraints. In practice, no protocol can satisfy the ideal notion of censorship resistance if there is more demand for transaction inclusion than available blockspace. SCQ addresses this limitation by not requiring that all honest transactions always be included, but rather giving all staked nodes a budget under which they are guaranteed transaction inclusion.

The [MCP protocol](https://eprint.iacr.org/2025/1772.pdf) was proposed as a gadget on top of existing PBFT-style consensus protocols to make them censorship resistant. This protocol additionally satisfies SCQ by assigning proposers blockspace pro rata based on stake (cf. Section 5.3 of [MCP](https://eprint.iacr.org/2025/1772.pdf)). Existing [DAG-based BFT](https://decentralizedthoughts.github.io/2022-06-28-DAG-meets-BFT/) protocols provide a way to implement a [multi-writer mempool](https://decentralizedthoughts.github.io/2025-08-08-DAGs/) that also provides some level of censorship resistance. Standard implementations of these protocols fall short of strictly achieving SCQ because they allow leaders to selectively delay subsets of transactions. However, slight modifications to these protocols can allow them to regain SCQ (see recent results [here](https://eprint.iacr.org/2026/126.pdf) and [here](https://www.arxiv.org/pdf/2602.02892)). A related topic is [forced transaction inclusion](https://ethresear.ch/t/fork-choice-enforced-inclusion-lists-focil-a-simple-committee-based-inclusion-list-proposal/19870) for reducing censorship (also see [EIP-7805](https://eips.ethereum.org/EIPS/eip-7805)).

[MCP](https://eprint.iacr.org/2025/1772.pdf) additionally shows how to obtain a stronger *hiding property* that essentially allows stakeholders to create *virtual private lanes* whose content is only revealed when the whole block is made public. We will expand on this aspect in future posts.

## Strong Chain Quality requires two more rounds, not just one

Recent work has shown that Strong Chain Quality and censorship resistance [require two more rounds](https://eprint.iacr.org/2025/2136) (so the good case takes $5$ rounds for $3f+1$ and $4$ rounds for $5f+1$ BFT). We will expand on this result in later posts.

Obtaining SCQ post-GST requires guaranteeing that the proposer cannot censor the inputs of the stakeholders. This is achieved via a two-round protocol with two small changes to almost any BFT protocol:

* **Round 1**: Each party sends its valid input to all parties.
* **Round 2**: Each party adds every unique valid input it received to its *inclusion list*, signs the list, and sends it to the leader.
* **BFT Proposal**: The leader proposes a block.
* **BFT vote**: A party only votes for a block if all the values in its inclusion list appear in the block and the block contains at most one valid input per party.

It is easy to check that this protocol sketch can be converted into a full protocol that satisfies post-GST SCQ, provides censorship resistance, and is live for an honest leader. Adding pre-GST SCQ would also require waiting for a quorum of values or lists in each round. See [DPasS](https://decentralizedthoughts.github.io/2025-12-12-dpaas/) for how this protocol is used for censorship resistance in the context of PBS. We will expand on this protocol and its generalizations in later posts.

## Strong Chain Quality and ordering

While Strong Chain Quality dictates the fraction of blockspace that a coalition can control, it does not fully specify how transactions are *ordered*. SCQ can be interpreted as reserving space in a set for every staked node with no guarantees on how the transactions in that set are ordered. This opens a rich area of research into the design of transaction ordering mechanisms that can further enhance fairness and efficiency within the blockchain ecosystem. One promising approach is to order transactions according to priority fees. We will expand on the nuances of ordering in future posts. 

## Strong Chain Quality and Last Look

Strong Chain Quality governs inclusion, but it does not by itself remove the "last look" advantage of a proposer, which may still commit to its own content later than honest parties or abort that content at the last minute. We will expand on this in later posts.

---

Your thoughts and comments on [X](https://x.com/ittaia/status/2036191286739226758?s=20).


---

# Additional notes

## Strong Chain Quality vs Chain Quality

Chain Quality is a long horizon proportionality property: over time, a coalition that holds $X\%$ of the stake obtains roughly $X\%$ of the blocks. Strong Chain Quality is an intra block proportionality property: in every block, a coalition that holds $X\%$ of the stake is guaranteed inclusion of its valid inputs up to $X\%$ of the available blockspace. 

Let $B$ be the fraction of the block that is allocated to a coalition that holds $X\%$ of the stake. Both properties imply that $E[B\mid CQ] = E[B\mid SCQ] = X$, but observe that $VAR[B\mid SCQ] = 0$ while $VAR[B\mid CQ] = X(1-X) \gg 0$. This reduced uncertainty could lead to a competitive advantage in markets where consistency in winning races is critical.

## Chain Quality in Asynchrony

Chain Quality often appears in *asynchronous* BFT protocols, where random leader election is required for liveness. The asynchronous chain quality in [VABA](https://arxiv.org/pdf/1811.01332.pdf) protocols says that the probability the decided block is proposed by an honest party is proportional to $(h-f)/(n-f)$, where $h = n-f$ is the number of honest parties. With optimal resilience $n = 3f + 1$, this is roughly one half. This is shown to be [tight in asynchrony](https://arxiv.org/pdf/2011.04719.pdf). The Chain Quality definition [in the validity section above](#chain-quality-as-a-bft-validity-property) can be viewed as a strengthening of asynchronous chain quality to partial synchrony.

## Strong Chain Quality and Agreement on a Core Set

While traditional agreement protocols focus on a single value, many applications in asynchrony require agreement on a set of values. The canonical example is asynchronous secure multiparty computation, where parties must agree on the set of inputs to be used in the computation. In this context, we can view *Strong Chain Quality* as a property that guarantees that the fraction of values from honest parties is proportional to their fraction of the stake. This is indeed the standard definition of validity in the context of [Agreement on a Core Set](https://decentralizedthoughts.github.io/2023-07-22-agreeemnt-on-a-core-set/) (ACS). 

This leads to a natural strengthening of Strong Chain Quality in the context of ACS to partial synchrony, where $h$ is the number of honest parties and $f = n - h$ is the number of Byzantine parties:

**Strong Chain Quality for ACS in partial synchrony**:
> Before GST, at least $h-f$ of the honest parties are included in the output set. After GST, all $h$ honest parties are included in the output set.

Note that even getting at least $h - f$ honest parties in the output set is a type of censorship resistance property: the adversary cannot censor more than $f$ honest parties.

This is a stronger property than the standard definition of validity for ACS. After GST, the adversary cannot censor any honest party.
