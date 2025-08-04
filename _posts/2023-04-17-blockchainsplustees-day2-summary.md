---
title: Blockchains + TEEs Day 2 Summary
date: 2023-04-17 01:00:00 -04:00
tags:
- blockchain
author: Kartik Nayak, Ittai Abraham, Aniket Kate
---

This is the second of the two part post on the [workshop on Blockchains + TEEs](https://blockchainsplusx.github.io) that concluded last week. Here are the key ideas from Day 2. You can find the post summarizing Day 1 [here](https://decentralizedthoughts.github.io/2023-04-09-blockchainsplustees-day1-summary/).

#### Nick Hynes: Practical Secure Decentralized Computing

Nick discussed the use of TEEs by Oasis. At a high level, Oasis network creates a scalable network for TEE-enabled blockchain layer 1. Oasis Sapphire provides a confidential EVM by putting the EVM in a TEE; it has lower fees, support for general purpose smart contract, full composability and a developer experience identical to that of Ethereum. And with Oasis Privacy Layer, smart contracts have access to a TEE. In essence, one can augment any home network from an L1 with a contract with public data to also support private logic and secrets.


The primary challenges with Oasis include UX concerns related to privacy such as security-usability trade-offs, the ability for developers to reason about side channels, and agreeing on what the privacy goals are.

Nick then spoke about how Blockchains can be used as a trust layer for TEEs. It provides transparency, audibility, and a way to detect TEE misuse. He then described the key idea behind his new startup where he is building Escrin, a secure decentralized computing network.

You can find more details in his talk [here](https://youtu.be/zIU3gFTb2PM?t=402) and his slides [here](https://docs.google.com/presentation/d/1jMwMky4m9DbP3CrpH50ldJITyOsE-u56DfmHsthdCSg/edit#slide=id.p).

#### Andrew Miller: TEE-based Smart Contracts: Pitfalls and Challenges

Andrew started with summarizing the different ways in which blockchains and TEEs interact with each other, beautifully capturing the talks in the workshop. Reproducing his slide here for reference.

![](https://i.imgur.com/bUrq2Fl.png)

Andrew then spoke about the different privacy needs for blockchains and the support we have for smart contracts today. For instance, a simple commit and reveal can be easily implemented today. For more complicated instances, one can rely on ZK proofs. Finally, for arbitrary requirements, e.g., auctions, one may use TEEs or secure multiparty computation. In that vein, Andrew spoke about his new venture on hbCL, which is a privacy-preserving credit network using TEEs, which falls in the last category.

Subsequently, his talk focused on issues related to using TEEs in blockchains.

For instance, where are the keys in the enclave? With solutions like SecretNetwork and Obscuro, there is a single decryption key that is replicated in all enclaves. This can be problematic in theory and in practice. Instead, in the design with Oasis and Phala, there are somewhat trusted key manager enclaves, and worker enclaves only receive contract-specific keys.

He then spoke about his work on SGXonerate where the issues are not related to breaking SGX but how it is used. For instance, one can attempt to modify the code around the enclave and attempt to learn the key. Finally, he spoke about issues related to rollback attacks.

He concluded the talk by discussing some open challenges and opportunities in this space. 

You can find the talk [here](https://youtu.be/zIU3gFTb2PM?t=1668) and his slides [here]().

#### Ittay Eyal: TEEchain: A Secure Payment Network with Asynchronous Blockchain Access

Ittay started the talk discussing what we can achieve using TEEs and blockchains individually. With blockchains, while payments are possible, they take a long time today when used naively. An alternative is to use TEEs only --- but this results in a 2-Generals problem.

Ittay then explained the key idea behind lightning network that works on the Bitcoin blockchain; in a nutshell, it provides a bidirectional payment channel between two parties. However, to ensure that the channel works correctly, the parties need to monitor the blockchain and take appropriate actions within a given timeframe to close the channel. 

Ittay’s work on TEEchain instead relies on using TEEs with blockchains to provide instant payments. With his solution, parties do not need to monitor the blockchain or use it at specified time intervals. Ittay then spoke about how to extend TEEchain to a multihop scenario. 

Learn more about the details in his talk [here](https://youtu.be/zIU3gFTb2PM?t=7039). His slides are available [here](https://blockchainsplusx.github.io/docs/tees/IttayEyal.pdf).

#### Guy Zyskind: Secret's Journey: Lessons Learned from 2.5 Years of Running TEEs in Production

Secret Network is the first blockchain enabling secure computation. It has been in production for 2.5 years and has run more than a million private computations. Guy described the use of TEE in Secret Network for privacy which is needed in multiple applications such as e-voting, auctions, games, identity, MEV, etc. Secret Network relies on private smart contracts or “secret contracts” to achieve these privacy goals.

Guy then discussed the Secret architecture at a high level. One key aspect that he touched upon is the use of a single shared secret across all TEEs on different nodes. While there are many other alternative approaches, he discussed some tradeoff including how external/social factors can play a role in such decisions.

Finally, he discussed applications on Secret Network, such as NFTs and private messaging networks. Finally, he ended the talk by discussing some challenges faced by Secret Network.

Listen to the talk [here](https://youtu.be/zIU3gFTb2PM?t=9020). His slides are available [here]().

Please add your thoughts on [Twitter](https://twitter.com/kartik1507/status/1649041738810507264?s=20).
