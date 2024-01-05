---
title: The First Blockchain or How to Time-Stamp a Digital Document
date: 2020-07-05 19:58:00 -07:00
tags:
- blockchain101
author: Ittai Abraham
---

This post is about the work of Stuart Haber and W. Scott Stornetta from 1991 on [How to Time-Stamp a Digital Document](https://www.anf.es/pdf/Haber_Stornetta.pdf) and their followup paper [Improving the Efficiency and Reliability of Digital Time-Stamping](http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.71.4891&rep=rep1&type=pdf). In many ways, this work introduced the idea of a chain of hashes to create a total order of commitments to a dynamically growing set of documents. It's no wonder these two papers are cited by the [Bitcoin whitepaper](https://bitcoin.org/bitcoin.pdf). 

> Who watches the watchmen?
> Quis custodiet ipsos custodes?
> -- <cite> [Juvenal](https://en.wikipedia.org/wiki/Juvenal) </cite>


From 1995, the ideas of this paper have been in use by a company called [Surety](http://www.surety.com/solutions/intellectual-property-protection/sign-seal). This makes it the longest-running chain of hashes! Here are two photos from 2018 of Stuart Haber (photos credit: [Dahlia Malkhi](https://malkhi.com/)) with the current hash circled in red on the New York Times:

<p align="center">
    <img src="/uploads/Haber1.jpeg" width="600" title="The first blockchain">
</p>

<p align="center">
    <img src="/uploads/Haber2.jpeg" width="600" title="The first blockchain">
</p>

## How to Time-Stamp a Digital Document?
In 1991, Haber and Stornetta asked this very basic question. Today, after 30 years of exponential growth in digital documents, this question is even more relevant! Let's describe their basic scheme:

The system is composed of users, a Time-Stamp Service (TSS), and a repository. At some regular interval, the TSS publishes an "interval hash" to a "widely available repository".

1. Users send *certification requests* to the TSS. 

2. The TSS creates a *Merkle tree* of all the requests. 

3. The "hash chaining" happens: The *new interval hash* is computed by taking the *root hash* of the Merkle tree and hashing it with the *previous interval hash*. 

4. The TSS publishes the new interval hash to the *public repository*.

5. The TSS also sends each requester a *Merkle proof* that their document is committed in the Merkle tree. 

6. Users can *validate* a document's time-stamp by querying the repository for the relevant interval hash and use the Merkle proof to compare the relevant leaf to the hash of the document.

In their own words, if we assume the repository is durable and trusted (think about the New York Times weekend circulation) then:

1.  "The TSS cannot forward-date a document, because the certificate must contain bits from requests that immediately preceded the desired time, yet the TSS has not received them." -- note that this assumes there is enough uncertainty in the future requests that is beyond the control of the TSS.

2. "The TSS cannot feasibly back-date a document by preparing a fake time-stamp for an earlier time, because bits from the document in question must be embedded in certificates immediately following that earlier time, yet these certificates have already been issued." -- Note that this assumes the hash function is collision-resistant.

3. "The only possible spoof is to prepare a fake chain of time-stamps, long enough to exhaust the most suspicious challenger that one anticipates." -- quite remarkable that even the notion of the longest chain has origins in this paper!


Note that there are some underlying assumptions here. We are trusting the TSS (Surety) to *not censor users* and we are trusting the repository (New York Times) to be *durable and show a consistent version to all users*. 

This is a very simple and intuitive scheme. It does make quite strong trust assumptions. Can we remove them?

## Connection to Bitcoin and Cryptocurrencies

The Bitcoin whitepaper made a breakthrough connection between this time-stamping scheme and proof-of-work: instead of assuming a centralized trusted TSS and a centralized trusted repository, it uses the chain of hashes to incentivize miners to implement the TSS and the repository in a decentralized manner! A miner that wins the race to produce a proof-of-work is incentivized to implement the TSS functionality and correctly publish a new interval hash. Censorship resistance is obtained by randomizing the winning miner and by adding fees that reward adding user requests. Miners are collectively incentivized to implement a replicated repository. Consistency is obtained by incentivizing miners to use the notion of the *longest (PoW heaviest) chain of hashes*.


Seen from the lens of distributed computing, the Bitcoin blockchain implements the TSS state machine and the repository is replicated via a byzantine fault-tolerant protocol called [Nakamoto Consensus](https://decentralizedthoughts.github.io/2019-11-29-Analysis-Nakamoto/). Seen from the lens of game theory, the contents of the documents recorded are restricted to be transactions over an internal digital asset with a controlled supply. Using this scarce resource, Bitcoin builds a novel incentive scheme that [typically](https://decentralizedthoughts.github.io/2020-02-26-selfish-mining/) incentivizes miners to implement the TSS and the public repository.

## Is it only about Cryptocurrencies?

The ability to order (time-stamp) all transactions in a trusted and immutable manner is a key ingredient of many decentralized state machines. This is a core enabler of many cryptocurrencies.

There could be many other cases where a trusted method to time-stamp digital documents is beneficial and a central trusted party is acceptable. Here are some examples:

1. The git protocol implements a [hash chain on all commits](https://git-scm.com/docs/commit-graph). In a way, [GitHub](https://stackoverflow.com/questions/46192377/why-is-git-not-considered-a-block-chain) can be viewed as a centralized implementation of a TSS and public repository for documents (in particular, for code).

2. [Certificate transparency](https://www.certificate-transparency.org/log-proofs-work) uses a chain of hashes (in fact, a Merkle tree) to maintain a public log of certificates and their revocations.

3. The [InterPlanetary File System (IPFS) protocol](https://ipfs.io/) uses elements of the TSS and repository idea to build a verifiable file system with a global namespace using a Distributed Hash Table (DHT).

4. Digital news outlets, blogs, or any web server could be able to provide a signed certificate of the time-stamp of their documents. For example, a blogger could prove [that their posts are not backdated](https://medium.com/@cryptofuse/the-legendary-nick-szabo-bitgold-smart-contracts-cryptocurrency-and-blockchain-story-3523db6766a3).

5. Educational institutions, Medical institutions, Government authorities could be able to provide a signed certificate of the time-stamp of their documents. This could allow digital verification of certificates of education, health, licenses, title, and more.

6. Financial institutions and multi-party business transactions could all rely on a trusted party to sign certificates about financial facts. Having a single source of truth that all parties can verify could reduce friction and risk in many transactions.

I can imagine that sometime in the future many digital documents will use some form of time-stamp based on the work of Haber and Stornetta. 

**Acknowledgment.** Thanks to [Kartik](https://users.cs.duke.edu/~kartik/), [Avishay](https://research.vmware.com/researchers/avishay-yanai), [Ittay](https://webee.technion.ac.il/people/ittay/), and [Alin](https://research.vmware.com/researchers/alin-tomescu) for helpful feedback on this post.


Please leave comments on [Twitter](https://twitter.com/ittaia/status/1279716517140140032?s=20).
