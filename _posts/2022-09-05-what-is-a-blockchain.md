---
title: What is a Blockchain?
date: 2022-09-05 00:00:00 -04:00
tags:
- blockchain101
author: Ittai Abraham
---

## TL;DR: A blockchain is a trusted coordination mechanism.

Of course, the answer depends on who you ask :-)

My seven-word answer: **A blockchain is a trusted coordination mechanism**. 

What is your definition of a blockchain? [Reply with your seven-word answer on Twitter](https://twitter.com/ittaia/status/1566870358837321731?s=46&t=VDqZSRpxsraPaBX11I_JaA). 


My answer to this question evolved over the years: from a more trust-oriented description: "*a computer with trust*" (inspired by [Ben Horowitz](https://www.youtube.com/watch?v=l7QdIQVTly0)) to adding an economic angle "*trusted coordination mechanism*" (inspired by [Yuval Noah Harari](https://www.ted.com/talks/yuval_noah_harari_what_explains_the_rise_of_humans/transcript?language=en")).

Other very similar answers: [Dan Boneh's](https://berkeley-defi.github.io/assets/material/lec2-dan-tech-intro.pdf)  "*a blockchain provides coordination between many parties, when there is no single trusted party*". [Chris Dixon's](https://a16z.com/2020/01/27/computers-that-make-commitments/)  "*Blockchains are Computers That Can Make Commitments*",  [Albert Wenger's](https://continuations.com/post/671863718643105792/web3crypto-why-bother) *a blockchain is a database not controlled by a single entity*, and [Tim Roughgarden's](https://timroughgarden.github.io/fob21/l/l1.pdf) "*a programmable computer that lives in the sky, that is not owned by anyone and that anyone can use*" -- which is a great metaphor! but slightly more than seven words :-).

All these answers have a common theme, but let's start with the origin of the word "blockchain"



<!---
The idea that money is simply a trusted ledger (aka a blockchain) of all transactions goes back to [Narayana R. Kocherlakota 1996](https://researchdatabase.minneapolisfed.org/downloads/pr76f356g) iconic paper "Money is Memory".
--->



 
## Origin of the word "Blockchain" 

Emails from [Satoshi](https://plan99.net/~mike/satoshi-emails/thread1.html) in 2009 mention "the block chain". However, Satoshi's emails and the [Bitcoin whitepaper](https://bitcoin.org/bitcoin.pdf) do not use the word "blockchain".  There was some initial debate between using "block chain" vs "blockchain", but by 2014, the official [Bitcoin forums](https://groups.google.com/g/bitcoin-documentation/c/D9aqm8uDQG0) seem to have converged on using "blockchain". 

So what does this "chain of blocks" do? The answer seems clear in [Satoshi Nakamoto's 2008](https://www.metzdowd.com/pipermail/cryptography/2008-November/014849.html) groundbreaking insight:
> The proof-of-work chain is a solution to the Byzantine Generals' Problem.  I'll try to rephrase it in that context. -- Satoshi Nakamoto

Similarly, [Hal Finney, 2008](https://www.metzdowd.com/pipermail/cryptography/2008-November/014848.html) explained that Bitcoin is solving a very hard problem of building a global, massively decentralized database:
 > ... bitcoin is two independent ideas: a way of ...
creating a globally consistent but decentralized database; and then using
it for a system similar to Wei Dai's b-money ... Solving the
global, massively decentralized database problem is arguably the harder
part...  -- Hal Finney

So how should we call this part of Bitcoin’s innovation? Vitalik Buterin's 2013 [Ethereum whitepaper](https://ethereum.org/en/whitepaper/) teases out *blockchain* as a generic term:
> another - arguably more important - part of the Bitcoin experiment is the underlying **blockchain technology** as a tool of distributed consensus, and attention is rapidly starting to shift to this other aspect of Bitcoin


## What is a Blockchain, in more than seven words?

How can a blockchain be a **trusted coordination mechanism**?

Viewed through the lens of computer science and distributed computing, my answer is: a blockchain is a trusted coordination mechanism via: 

1. Byzantine Fault Tolerant State Machine Replication ("trusted"); with
2. Openness and Auditability ("coordination"),
3. Incentives to provide guarantees ("mechanism").

### 1. Byzantine Fault Tolerant State Machine Replication ("trusted")

A *trusted coordination mechanism* is a shorthand for the more academic definition of **Byzantine Fault Tolerant State Machine Replication (BFT SMR)**. The State Machine *paradigm* is covered by [Fred Schneider's 1990 tutorial](https://www.cs.cornell.edu/fbs/publications/ibmFault.sm.pdf) and goes back to Lamport's seminal 1978 paper on [Time, Clocks, and the Ordering of Events in a Distributed System](https://lamport.azurewebsites.net/pubs/time-clocks.pdf) (see page 562). The adaptation of the State Machine paradigm to Byzantine Fault tolerance and the emphasis on a *generic* service was pioneered by Barbara Liskov and her group at MIT with [PBFT](https://pmg.csail.mit.edu/papers/osdi99.pdf) and [BASE](http://www.sosp.org/2001/papers/rodrigues.pdf). BASE advocates using *abstraction* and *generality* which is the conceptual precursor to the idea of a *blockchain computer*. 

The idea of replacing any ideal functionality (state machine) with a replicated service built on mathematical protocols to obtain trust (which includes security, and in some extensions, privacy) is at the **core of cryptography**. [Boaz Barak](https://www.boazbarak.org/cs127spring16/chap17_sfe) says it best: "Cryptography is about replacing trust with mathematics". This foundational idea is at the center of [Secure Multi Party Computation](https://u.cs.biu.ac.il/~lindell/MPC-resources.html).


### 2. Openness and Auditability ("coordination")

As Yuval Noah Harari writes in [Sapiens 2014](https://www.ynharari.com/topic/power-and-imagination/):

> Fiction has enabled us not merely to imagine things, but to do so collectively. We can weave common myths ...(which) give Sapiens the unprecedented ability to cooperate flexibly in large numbers 

Through this lens, trust in blockchains can be viewed as a common fiction that allows untrusting parties to coordinate on a common source of truth. How can such a system provide a trusted system for coordination? Technically, a Byzantine fault tolerant state machine provides this trusted coordination. But how can parties trust the state machine? And how can they guarantee access to such a system?

Two properties of *permissionless blockchains* that allow such untrusted coordination are **openness** and **auditability**. These properties are not captured explicitly by traditional BFT SMR and aim at allowing untrusting parties to trust the system and hence enable them to coordinate. 

Conceptually, *Openness* can be viewed as the blockchain equivalent of the [US First Amendment](https://en.wikipedia.org/wiki/First_Amendment_to_the_United_States_Constitution). Technically it can be split into two parts. The first is that the set of validators (or block producers) is not fixed, but dynamic and open for participation. Often, a certain type of resource is required to become a validator, but minimal discrimination beyond this resource requirement. In Bitcoin to become a block producer (validator) all that is needed is the ability to compute proof-of-work puzzles. In several proof-of-stake systems, to become a block producer (validator) all that is needed is to stake some amount.

The second part of *Openness* is about the execution engine (the state machine), which can again be split in two: (1) openness in writing: there is often minimal inherent discrimination as to who can submit a transaction; (2) openness in reading: there is minimal inherent discrimination in the ability to read the state of the ledger and verify the transitions of the state machine;

Openness is not an absolute property, there are often various requirements to limit it or balance it with other values. Regulator pressure could in the future require a more limited form of openness. A recent example is the [US treasury sanctions](https://home.treasury.gov/news/press-releases/jy0916) imposed on the tornado cash mixer, and the resulting debate on [First Amendment rights](https://www.eff.org/deeplinks/2022/08/code-speech-and-tornado-cash-mixer) and [Fourth Amendment rights](https://mirror.xyz/haunventures.eth/E-iD-jqgD-WmqrZOjCnGjv6U-R_N5tUk8xPzxUHhQGc).


Another important historical example of the limits of openness is that to update themselves, blockchains sometimes need to hard fork. As an example, [an early Bitcoin hard fork](https://freedom-to-tinker.com/2015/07/28/analyzing-the-2013-bitcoin-fork-centralized-decision-making-saved-the-day/) inadvertently discriminated against some transactions and caused a perceived [double spend](https://bitcointalk.org/index.php?topic=152348.0). Another famous example is the Ethereum DAO hard fork that caused a form of [discrimination against a presumed attacker](https://blog.slock.it/hard-fork-specification-24b889e70703#.io9ej36yq).


*Auditability* can be viewed as a strengthening of the ability of external parties to read and in particular to *audit* the system: (1) verify there is no double spend (audit for consensus violations); (2) verify that the execution is valid (audit for execution violations); (3) verify that the data is available (audit for data availability violations). Buterin argues about the importance of allowing [low resource users to be able to audit a blockchain](https://vitalik.ca/general/2021/05/23/scaling.html).



### 3. Incentives to provide guarantees ("mechanism")

Finally, traditional cryptographic models in computer science assume a binary: *good guys / bad guys* view of the world. These models assume some fraction of parties are inherently honest and the remaining parties are controlled by a malicious adversary whose sole goal is to break the protocol guarantees. 

Arguably, the breakthrough in blockchain systems is going beyond this model and focus on a 
**Cryptoeconomic model** where most parties are presumed to be motivated by rational preferences and incentives.

As Buterin says in his 2019 [talk on Cryptoeconomics](https://youtu.be/GQR1xjQn5Pg):

> What did Satoshi really invent? Satoshi invented **Cryptoeconomics**, the use of incentives to provide guarantees about applications. 

To provide a means for trusted coordination, blockchains need to provide **incentives**: (1) for the validators to operate the system (over the alternatives of doing other things, free riding, or misbehaving); (2) and for users to choose to use the system (over other alternatives of using other systems).

Taking into account incentives and modeling parties as rational agents is a non-trivial difference between blockchains and the traditional Cryptographic model of assuming honest parties and a malicious adversary.

Instead of assuming most parties are honest and will follow the consensus protocol to maintain safety and liveness, some blockchains explicitly offer incentives to [maintain safety](https://medium.com/@VitalikButerin/minimal-slashing-conditions-20f0b500fc6c) and [maintain liveness](https://eth2book.info/altair/part2/incentives/inactivity#inactivity-leak).  

The use of punishment strategies to disincentivize unwanted behavior is particularly effective when the blockchain system has a native means to force parties to commit economic resources and suffer **slashing** events in case of misbehavior. This is the basis of [optimistic rollups](https://ethereum.org/en/developers/docs/scaling/optimistic-rollups/) and the usability of fraud proofs.

Another key aspect of blockchains is that as a limited resource, they need some way to decide which transactions to include. This is a classic resource allocation problem with limited supply. The cryptoeconomic solution is to have a mechanism that selects the transactions whose users are willing to pay the most. For example the Ethereum [1559 transaction pricing mechanism](https://github.com/ethereum/EIPs/blob/master/EIPS/eip-1559.md) whose goal is to stabilize the fee market and price congestion. As a side effect, these mechanisms also allocate revenue to validators. 


Cryptoeconomics and incentive considerations appear in many surprising places across blockchain technologies, from [selfish mining](https://decentralizedthoughts.github.io/2020-02-26-selfish-mining/) to the equilibrium between *staking and lending*.

#### What is a Blockchain? Notable posts and responses

**Chris Dixon**: ability to coordinate people and capital at internet scale, with ownership embedded directly into the system. See [full blog post](https://x.com/cdixon/status/2019837259575607401?s=20).

**Balaji Srinivasan**: massively multiclient databases, where every user is a root user. See [full blog post](https://balajis.com/p/yes-you-may-need-a-blockchain).

**Virgil Griffith**: is an unprecedented arena for playing cooperative games. See [full blog post](https://medium.com/@virgilgr/ethereum-is-game-changing-technology-literally-d67e01a01cf8).

**@artofkot**: collusion resistant coordination tool. Check out the excellent [full blog post](https://artofkot.xyz/blog/why-blockchains).

**@JoshaTobkin**: a shared immutable ledger 

**@dfren_eth**: blockchains are digital and political states.

**@yossi_sheriff**: a machine version of cultural trust capital




#### Acknowledgments

Many thanks to Tim Roughgarden for insightful comments and suggestions.





Your thoughts on [Twitter](https://twitter.com/ittaia/status/1566870358837321731?s=46&t=VDqZSRpxsraPaBX11I_JaA).
