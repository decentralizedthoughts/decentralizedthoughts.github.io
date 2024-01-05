---
title: The threshold adversary
date: 2019-06-17 09:11:00 -04:00
tags:
- dist101
- models
author: Ittai Abraham
---

In addition to limiting the adversary via a communication model [synchrony, asynchrony, or partial synchrony](https://decentralizedthoughts.github.io/2019-06-01-2019-5-31-models/), we need some way to limit the power of the adversary to corrupt parties. 


> Power tends to corrupt, and absolute power corrupts absolutely.
> -- <cite> [John Dalberg-Acton 1887](https://en.wikipedia.org/wiki/John_Dalberg-Acton,_1st_Baron_Acton) </cite>

As John observed almost 150 years ago, if the adversary has no limits to his power, then there is very little we can do. Let's begin with the traditional notion of a *threshold adversary* as used in Distributed Computing and Cryptography to limit the power of the adversary. 

## The threshold adversary 
The traditional and simple model is that of a *threshold adversary* given a static group of ***n*** nodes. 

A threshold adversary is an adversary that can corrupt up to ***f*** nodes. There are three typical thresholds:
1. $f<n$ where the adversary can corrupt all parties but one. Sometimes called the *dishonest majority* model or the [anytrust](https://www.ohmygodel.com/publications/d3-eurosec12.pdf) model.
2. $f<n/2$ where the adversary can corrupt a minority of the nodes. Often called the *dishonest minority* model.  
3. $f<n/3$ where the adversary can corrupt less than a third of the nodes. 

There are many examples of protocols that work in the above threshold models. Here are some classics:
1. The Dolev, Strong [Broadcast protocol](https://www.cs.huji.ac.il/~dolev/pubs/authenticated.pdf)  solves Byzantine broadcast assuming an adversary that can corrupt up to $n-1$ parties out of $n$ in the Synchronous model. See [this post](https://decentralizedthoughts.github.io/2019-12-22-dolev-strong/) for details.
2. Lamport's [Paxos](https://lamport.azurewebsites.net/pubs/lamport-paxos.pdf) protocol solves state machine replication assuming an adversary that can corrupt less than $n/2$ parties out of $n$ in the Partially synchronous model. See [this post](https://decentralizedthoughts.github.io/2022-11-04-paxos-via-recoverable-broadcast/) for details.
3. Ben Or's [randomized protocol](http://www.cs.utexas.edu/users/lorenzo/corsi/cs380d/papers/p27-ben-or.pdf) solves Byzantine agreement in the Asynchronous model assuming a $f<n/5$ threshold. This was later [improved by Bracha](https://core.ac.uk/download/pdf/82523202.pdf) to the optimal $f<n/3$ bound. See [this series of posts](https://decentralizedthoughts.github.io/2022-03-30-asynchronous-agreement-part-one-defining-the-problem/) for details.

## Proof of work and proof of stake

The blockchain disruption brought significant interest settings where the set of participants are not static and not fixed in advance. Two main models are **proof of work (PoW)** and **proof of stake (PoS)**. Both use the idea of some *bounded resource*:

1. **Proof of work**: In [Nakamoto Consensus](https://decentralizedthoughts.github.io/2021-10-15-Nakamoto-Consensus/) (the consensus mechanism used by Bitcoin), one can consider the bounded resource to be the total CPU power of the participants. The assumption is then that the adversary controls less CPU power than the honest nodes (a minority adversary). The Nakamoto authors explicitly mention the assumption of a resource bounded *minority* adversary:
> The system is secure as long as honest nodes collectively control more CPU power than any cooperating group of attacker nodes.
> -- <cite>[Bitcoin whitepaper](https://bitcoin.org/bitcoin.pdf) </cite>

1. **Proof of stake**: In systems that use [proof-of-stake](https://www.investopedia.com/terms/p/proof-stake-pos.asp) the assumption is that the bounded resource is some finite set of coins. It is then natural to assume that the adversary controls a threshold of the total coins. One can often map voting power based on the relative amount of coins at a given time. For example, Tendermint mentions the total voting power of the adversary is bounded by a third:
> it requires that the total voting power of faulty processes is smaller than one-third of the total voting power
> -- <cite> [Tendermint whitepaper](https://arxiv.org/pdf/1807.04938.pdf) </cite>

## Generalized bounded resource threshold adversary 

In this model instead of having a static total *n* that represents the total number of nodes or participating parties, we assume some general **_bounded resource_** (see Szabo definition of [scarce object](https://nakamotoinstitute.org/scarce-objects/)). A generalized threshold adversary is an adversary that can corrupt some **_fraction_** of this *bounded resource*. Again, there are three typical thresholds, typically with a small $0<\epsilon$ parameter:

1. The adversary can corrupt at most $1-\epsilon$ fraction of the bounded resource (say 99 percent).
2. The adversary can corrupt at most $1/2 - \epsilon$ fraction of the bounded resource (say at most 49 percent).
3. The adversary can corrupt at most $1/3 - \epsilon$ fraction of the total bounded resource (say 32 percent). 

In this model the total amount of resources and its allocation can dynamically change over time. Typically, the assumption is that the above threshold restrictions hold at any given time (and sometimes as a function of the *active* participants). If this is not the case at all times then special care is needed.

# Notes

## On *stake* based bounded resources
Basing the security assumption on the adversary controlling a threshold of some set of coins issued by the system (stake) has both advantages and disadvantages.
1. On the one hand, using a resource that is issued by the platform allows one to control the resource allocation in ways that are not possible when the resource is external. In particular, the platform can create *punishment mechanisms* to better incentivize honest behavior. For example, [Buterin suggests](https://medium.com/@VitalikButerin/minimal-slashing-conditions-20f0b500fc6c) conditions to detect malicious behavior and then punish the adversary by reducing (slashing) the offender's stake.
2. On the other hand, if the value of the stake depends on the platform, this may cause some circular reasoning about security and in particular a bootstrapping problem of how to set the external cost of buying stake. If the cost of buying stake is too high, then it may happen that not enough honest entities will sign up, and the system will lose liveness. If the cost of buying stake is initially too low, then an attacker can gain early monopoly power. One option is to bootstrap proof-of-stake using an existing decentralized high-value proof-of-work coin or high-value traditional fiat (see [here](https://bitcoinist.com/visa-paypal-10-million-run-facebook-coin-node/)). This type of solution assumes that the adversary does not already have monopoly power on the bootstrapping resource. Another option is to bootstrap a proof-of-stake system from an existing high-value proof-of-work system (for example, see [eth2.0](https://github.com/ethereum/eth2.0-specs)).


## On distributed computing vs game theory
The threshold adversary model captures the ability of the adversary to corrupt some fraction of the parties and allow them to deviate from the prescribed behavior. It divides parties into honest and corrupt. This is rather different from traditional *Game Theory* models where all parties are considered *rational*. 

As mentioned above, in the *proof of stake* setting there is a notion of *slashing* which captures the fact that deviating coalitions may suffer economic loss and that may deter them from deviation.

In fact, there are deep connections between the models. In particular, just like distributed computing protocols quantify over all possible adversaries that can modify the behavior of up to $f$ parties, a Nash equilibrium (and its extension to a coalition resilient equilibrium) can be viewed as quantifying over a rational adversary that can modify the behavior of up to $f$ parties.
%
In later posts, we will cover the amazing connections in detail.

## On permissioned vs permissionless

The traditional model with $n$ parties is often called the **permissioned model** because the parties are fixed in advance and in essence there is some initial source of trust that granted permission to these specific $n$ parties. Typically, all participants know the identity of all other participants.

In contrast, many of the generalized bounded resource models are often considered part of a wider class of **permissionless models**. In these models there is some bounded resource, sometimes the allocation of this bounded resource can dynamically change. Participation in these systems is called *permissionless* because anyone holding this resource can participate. In some cases can participation can be done without needing to have an explicit identity and without all participants knowing each other. 

The fact that the protocol is permissionless in the sense that anyone holding the bounded resource is allowed to participate does not mean that obtaining the bounded resource is without restrictions (both economic and permission based). In essence, it is moving the task of granting the bounded resource to an external process. For example, it may be that obtaining specific hardware or buying staking tokens is a permission process.

The work of Lewis-Pye and Roughgarden on [Permissionless Consensus](https://arxiv.org/pdf/2304.14701.pdf) provides a comprehensive categorization and deep analysis of this model.


## Acknowledgments

Many thanks to Kartik Nayak and Gilad Stern for insightful comments

Please comment on [Twitter](https://twitter.com/ittaia/status/1141475000278556674?s=20)

