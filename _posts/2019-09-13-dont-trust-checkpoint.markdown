---
title: Dont Trust. Verify. and Checkpoint?
date: 2019-09-13 16:32:00 -04:00
tags:
- blockchain
author: Ittai Abraham
---

Imagine that that Aliens land on earth with a new superfast SHA256 machine. Imagine this machine always gives them more than 51% of the current world Bitcoin hash power (but not enough hash power to completely break SHA256). Suppose they decide to build a chain from the [Bitcoin Genesis block](https://ittaiab.github.io/2019-07-18-do-bitcoin-and-ethereum-have-any-trusted-setup-assumptions/) that is longer than any other chain on earth and put only empty blocks on it. *Could they erase all bitcoin transactions?*

Anticipating this type of attack, Satoshi suggested the following [security safeguard](https://satoshi.nakamotoinstitute.org/posts/bitcointalk/232/): 


> The security safeguard makes it so even if someone does have more than 50% of the network's CPU power, they can't try to go back and redo the block chain before yesterday.  (if you have this update)
>
> I'll probably put a checkpoint in each version from now on.  Once the software has settled what the widely accepted block chain is, there's no point in leaving open the unwanted non-zero possibility of revision months later.  -- [Satoshi 2010](https://bitcointalk.org/index.php?topic=437)

So the answer is that the Aliens with a superfast SHA256 will fail. By [default](https://github.com/bitcoin/bitcoin/blob/master/src/validation.cpp#L120) the bitcoin core client enforces a set of [checkpoints](https://github.com/bitcoin/bitcoin/blob/master/src/chainparams.cpp#L138). In fact it seems that the person behind the Satoshi email in 2010 suggested to add a checkpoint **in each version from now on**.


A **checkpoint** on a blockchain is pair (block number, hash). For example the checkpoint (295000, 0x00000000000000004d9b4ef50f0f9d686fd69db2e03af35a100370c64632a983) indicates that the hash of the 295000th block must be 0x00000000000000004d9b4ef50f0f9d686fd69db2e03af35a100370c64632a983.
A checkpoint provides **finality**. All the transactions till block 295000 are final, there is no way to revert them, even if you are an alien with a superfast SHA256 machine [^1].

[^1]: This is assuming the superfast machine is just faster than all the current world hashpower - not a machine that can completely break SHA256.  

While some believe this is [not a security feature](https://bitcoin.stackexchange.com/questions/39097/do-all-bitcoin-client-enforce-checkpoints), it does effectively enforce a consensus decision (by default) that forces all users using the same codebase to accept this checkpoint and everything before it as final.

The idea of adding checkpoints by publishing hardcoded values into a [github](https://github.com/bitcoin) repository is somewhat controversial. It's essentially a way for a code base to create a new genesis and effectively disallows any alternative chain from the previous genesis. On the one hand this is a strong security measure but on the other hand this gives non-trivial power to the maintainers of the github repository. The real question then becomes: who decides what will be a checkpoint? who decides how often? what will be its value?  

The Bitcoin core client uses checkpoints in a sporadic manner.  Seems to be used till 2014 and later abandoned. Their motivation seems to be that it [protects against header flooding attacks](https://github.com/bitcoin/bitcoin/issues/15095 
). However there seems to be no documented systematic reasoning as to when to use checkpoints.

The [Casper finality gadget](https://arxiv.org/abs/1710.09437) can be viewed as a way to use a [BFT based](https://ittaiab.github.io/2019-06-23-what-is-the-difference-between/) sub-system to decide on checkpoints that is governed by a set of validators (instead of a set of Github maintainers). More on finality gadgets in a later post.

Please leave comments on [Twitter](https://twitter.com/ittaia/status/1181022613511888896?s=20)
