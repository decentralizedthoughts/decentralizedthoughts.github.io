---
title: Blockchains + TEEs Day 1 Summary
date: 2023-04-09 01:00:00 -04:00
tags:
- blockchain
author: Kartik Nayak, Ittai Abraham, Aniket Kate
---

Our [workshop on Blockchains + TEEs](https://blockchainsplusx.github.io) concluded last week. We had a fantastic series of talks and discussions on both days of the workshop. In this two part post, we highlight some key takeaways from each of the days.

#### Natacha Crooks: In Trusted BFT Components, we (Mostly?) Trust
In her talk, Natacha discussed the potential areas where TEEs can be beneficial or not in the context of consensus protocols.


In consensus, it is [known](http://news.cs.nyu.edu/~jinyang/fa08/papers/a2m.pdf) that trusted hardware can be used as a non-equivocation mechanism and thus, can help towards reducing the replication factor for BFT protocols from 3f+1 to 2f+1. In the talk, she mentions that while this reduction holds, it is not efficient. In particular, there are three key limitations with using a BFT protocol with trusted hardware and only 2f+1 replicas:
- *Limited responsiveness:* if there are fewer replicas, then opportunities for responsiveness in the protocol is limited since Byzantine replicas can easily delay some parts of the protocol.
- *Lack of parallelism:* tying messages to a *sequence number* implies only sequential processing of transactions, reducing throughput
- *Inefficiency of counters for defending against rollbacks:* existing BFT protocols require attestations for every message

She then presents a FlexiTrust protocol that can achieve a high throughput per replica participating in the system. In fact, while still relying on 3f+1 replicas, they address the three issues discussed earlier and (i) reduce the number of phases of communication, and (ii) the communication cost in the protocol. 

To learn more, you can find her talk [here](https://youtu.be/9-nhNQO5_Js?t=207) and the slides [here](https://blockchainsplusx.github.io/docs/tees/NatachaCrooks.pptx).

#### Heidi Howard: Confidential Consortium Framework: Building Secure Multiparty Services in the Cloud

Heidi discussed some properties of the Confidential Consortium Framework (CCF) in her talk. At a high level, CCF aims to build a general-purpose foundation for trustworthy multiparty services on untrusted infrastructure. The key properties obtained by CCF include:
- Confidentiality and integrity: confidentiality and executional integrity is provided by TEEs whereas for data integrity, CCF leverages an immutable ledger and the use of Merkle trees outside the trust boundary
- Availability: leverages the existence of an immutable ledger 
- Address rollback attacks: by treating nodes as ephemeral but do not allow a restart from a persistent state
- Allows for reconfiguration and disaster recovery to a valid state

In all, CCF tightly couple TEEs and blockchains. First, it leverage TEEs to build better blockchains by fundamentally decoupling operators and consortium members. Second, it leverages blockchains to build better TEEs by enabling confidentiality, integrity and availability on untrusted infrastructure.

Learn more about CCF [here](https://youtu.be/9-nhNQO5_Js?t=2290). Slides can be found [here](https://blockchainsplusx.github.io/docs/tees/HeidiHoward.pdf).

#### Mic Bowman: Building Decentralized Trust with a Trusted Execution Environment

The key takeaway from Mic’s talk is that *there are no perfect security technologies, but we should consider using TEEs because it is worth the risk.*

Well, all protocols/systems make assumptions. For instance, Blockchains assume the existence of less than an f bad actors (or 49% bad actors). Similarly, with trusted hardware, there is a chance that assumptions may break down. In that sense, there are no perfect solutions, and we should think about the use of TEEs as managing risk instead of a bullet-proof solution.

While most users are looking for confidentiality when using TEEs, in decentralized computing we care more about verifiable integrity. In effect, when leveraging TEEs in decentralized computation, we aim to get the same properties as what we would get with a “community vote” system, but the hope is that we can make this process more efficient. For instance, TEEs can help increase resilience, or help build private data objects through smart contracts executed within TEEs.

Should you trust TEE as a sole arbiter of truth? There are two extreme schools of thought:
(i) It works and should be used everywhere
(ii) It doesn’t work and shouldn’t be used anywhere

Mic suggests that should aim for a middle ground. In that sense, the way to think about TEEs is that it:
- Works unless explicitly broken
- It is expensive to break
- One piece of a security solution, and not *the* solution

Mic's talk can be found [here](https://youtu.be/9-nhNQO5_Js?t=4415). Here are the [slides](https://blockchainsplusx.github.io/docs/tees/MicBowman.pdf).


#### Matt Green: Ask not what secure hardware can do for ledgers, but what ledgers can do for secure hardware

The key question Matt asks is *how blockchains can be used as a first-class cryptographic objects to secure TEEs and other systems?*

To answer this question, he focuses on *what can’t TEEs do?* There are two key aspects. First, to communicate with the world, TEEs are almost always dependent on an untrusted host. The host can be malicious and can censor. Second, the cannot store state reliably. Storage is typically handled by the host machine, and TEEs are always susceptible to rollback attacks.

The key takeaway from his talk is that, blockchains can help solve both of these problems, i.e., statekeeping and providing a verifiable input to a TEE. A key property that enables the solution is a *proof of publication*, e.g., with Bitcoin, one can provide an economic guarantee that some x number of blocks have been produced.

Learn more about the use of blockchains to secure TEEs from Matt [here](https://youtu.be/9-nhNQO5_Js?t=8942). Here are the [slides]() from the talk.


#### Jonathan Passerat-Palmbach: Privacy x MEV: Mitigation, Collaboration, Decentralisation

Jonathan explained the concept of maximal extractable value (MEV) as the profit a party can earn by inserting, removing or reordering transactions. At a high level, the goal is to reduce MEV as much as possible, and where it cannot be reduced (or for the "good" MEV), it should be redistributed.

How does Flashbots attempt to solve this problem? At a high-level, a new classes of parties called searchers and builders that compete with each other in creating and ordering transactions and engage in a sealed-bid auction. The goal is thus to have decentralization of validators (since validators only tend to follow a simple protocol to pick the highest bid) while searchers and builders can perform the sophisticated job of extracting MEV.

Ensuring this process currently is riddled with a problem: if validators learn the contents of the block produced by searchers and builders, then they can steal all of the profits from these entities. On the other hand, if they do not learn all the content, then they are essentially relying on these entities to reveal the blocks; if they do not, then validators would get slashed. Thus, the current ecosystem uses *trusted relays* such as a Flashbots to achieve this guarantee. 

Some of the key challenges they face include: 
(i) Centralization of builders, (ii) Trusted relays, and (iii) Users do not benefit from MEV

Given this background, Jonathan discussed the following key research questions: 
- How can SGX be used to address these concerns?
- Taking into account commercially available TEEs' known design flaws, how could we strengthen them further?
- How could we design a network made of heterogeneous TEEs considering they currently have different threat models?
- Exploring how encrypted mempools can help solve some of these challenges.

Learn more details about the challenges and research questions from Jonathan's talk [here](https://youtu.be/9-nhNQO5_Js?t=10870). Here are the [slides]() from the talk.

Please add your thoughts on [Twitter](https://twitter.com/kartik1507/status/1649041738810507264?s=20).
