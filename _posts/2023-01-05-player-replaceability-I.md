---
title: Player Replaceability - Towards Adaptive Security and Sub-quadratic Communication
  Simultaneously (Part I)
date: 2023-01-05 00:00:00 -05:00
tags:
- blockchain
- research
author: Kartik Nayak
---

This is part I of a two-part post on the concept of player-replaceability.

In Nakamoto consensus, proof-of-work (PoW) provides us with an interesting set of properties with respect to the adaptivity of the adversary:
- **Unpredictability.** Block winners are elected uniformly at random proportional to their computation power, thus, an adversary cannot predict *who* the block winner would be (and thus cannot corrupt it) ahead of time 
- **Verifiability of elected party.** Once a miner is chosen as a block winner, the miner can prove it to the world that it has indeed been chosen to propose a block by showing a PoW,
- **Integrity of elected parties' message.** Once the block has been created, an adversary cannot modify the contents of the block even if it corrupts the miner since it requires creating another PoW with a new payload, and finally,
- **Ephemerality of power.** After disseminating the block, the miner that mined the block is not any more powerful than it was, before mining the block.

Essentially, these properties make the miners ephemeral where they are in a position of power for a very short amount of time. Until they succeed in solving a proof-of-work puzzle, they have no "power", and once they have mined and shared the block, they have no "power" again. When the miner mines a PoW successfully, no other party knows about its success. Thus, it maintains security even in the presence of an adaptive adversary. Moreover, by relying on computational power to produce blocks, the protocol can reach consensus even if each step is executed by a totally new party in each round. In that sense, the protocol is *player-replaceable*. Observe that the use of PoW is central to achieving these properties in Bitcoin's Nakamoto Consensus. Thus, a natural question is: 

**Can we achieve these properties without PoW, for instance, in a setting where there are a fixed set of parties or a protocol that relies on proof-of-stake?**

To answer this question, we must first ask when is the property of player-replaceability useful? As an example, consider a setting with a fixed set of parties running a protocol such as HotStuff or PBFT. In these protocols, committing a value typically requires *all* parties to send messages. Even if a threshold adversary decides to adaptively corrupt some of these parties, so far as the protocol assumptions hold, the adversary would only delay committing a value. For example, corrupting a non-leader party in HotStuff would not help since there are sufficiently many honest parties to ensure safety and livenes. The adversary can corrupt the protocol leader who is only responsible for liveness; however, eventually, after some view changes, we would have an honest leader and we would commit values. On the other hand, if a protocol involves only a few (sublinear) parties sending messages to all parties, in the absence of the properties discussed earlier, an adverarsary can corrupt all these senders. They can then send equivocating messages, eventually leading to safety (and liveness) violation.

Thus, player-replaceability is a relevant property for a protocol that has only a sub-linear number of parties sending messages (thus obtaining sub-quadratic communication) and needs to be simultaneously secure under an adaptive adversary. Chen and Micali, in [Algorand](https://arxiv.org/pdf/1607.01341.pdf), originally described it as *a protocol that correctly and efficiently reaches consensus even if each of its step is executed by a totally new, and randomly and independently selected, subset of parties with little intersection between the subset*s.

## How do we Achieve Player-Replaceability?

Chen and Micali presented a player-replaceable protocol in Algorand. Interestingly, it turns out that the ideas they used are general enough to convert many existing protocols with a fixed number of parties into their player-replaceable counterparts.

We will describe this as a two-step process starting with a protocol with a fixed number of parties. The first step is to achieve a committee-based sub-quadratic communication protocol. In the second step, we will discuss how to achieve security under an adaptive adversary. For concreteness, we will use HotStuff as the example underlying protocol.

### Towards a Committee-based Sub-quadratic Communication Protocol

To achieve a sub-quadratic communication protocol, the key idea is to randomly sample an appropriate number parties in a *committee*, run consensus among the committee members, and disseminate the result to all other parties. Thus, so far as other parties know who the committee members are, they can learn the result by receiving messages from each of the committee members. 

```
// Protocol for party i

C = Randomly select k parties among n parties // C is  known to everyone

if party i is in C:
    newCommand := getNextVal()
    ouptut o := run BFT-C(newCommand)
    send output o to all parties
    Output o
else:
    wait for the same output o from a majority of parties in C
    Output o
```

The above protocol describes a simple committee-based variant starting from a generic BFT protocol such as HotStuff. For simplicity, we consider a single-shot variant. In the protocol, we first randomly elect a committee $C$ of size $\kappa$. For instance, we can rely on a value $r$ generated by an external randomness beacon as a source of randomness. Given $r$, any simple rule such as picking the parties $j$ with the smallest $\kappa$ values among $H(r, 1)$, $H(r, 2)$, ..., $H(r, j)$, ..., $H(r, n)$ can be used to elect the committee.

Once the committee is elected, only members of the committee engage in the consensus protocol. Thus, each member obtains an uncommitted client command using the function ```getNextVal()``` and runs a BFT protocol among the committee members to obtain output $o$. In the protocol, `BFT-C()` denotes that the BFT protocol is run only among the $\kappa$ committee members. They share the result with all parties. 

Parties who are not elected wait to hear the output from the committee. If a majority of parties in $C$ output the same value, these parties output the value too. 

Note that, so far as the Byzantine parties within the committee $C$ are bounded to one-third the committee (as required by HotStuff), the entire protocol obtains all of the safety and liveness properties. In terms of communication complexity, if the BFT protocol needs $O(\text{poly}(N))$ communication for running the protocol among $N$ parties, then the above described protocol requires $O(\text{poly}(\kappa) + \kappa n)$ communication. The latter term is the communication complexity for disseminating the result to all parties.

Wait, it appears that we are now running the protocol among a smaller committee, which appears substantially better. Is this free lunch? How does this relate to the [Dolev-Reischuk lower bound](https://decentralizedthoughts.github.io/2019-08-16-byzantine-agreement-needs-quadratic-messages/) on communication complexity?

No, its not free lunch. There are trade-offs:
- First, for the protocol to achieve the desired properties, we need the number of Byzantine parties within the committee to be bounded, e.g., $< \kappa/3$ Byzantine faults for HotStuff. Since we elect the $\kappa$ parties uniformly at random, a simple Chernoff bound requires that the total number of faults we can tolerate is $t < (1-\epsilon)n/3$ instead of $t < n/3$ for some $\epsilon > 0$. Moreover, the $\kappa/3$ corruption bound can be exceeded with probability $\exp(-\Omega(\kappa))$. Thus, we think of $\kappa$ as the security parameter.

    The following graph from [Algorand](https://dspace.mit.edu/bitstream/handle/1721.1/137789/p51-gilad.pdf?sequence=2&isAllowed=y) presents a trade-off between $\epsilon$ (or the percentage of honest users in the population) and the committee size $\kappa$ for achieving a failure probability of $5\cdot 10^{-9}$. Thus, this strategy works only when the total number of parties are large enough and we are okay with the reduction in fault tolerance due to the slack parameter $\epsilon$ for a given committee size.

<figure>
<p align="center">
<img align="center" height=300 src="https://i.imgur.com/AsTE5sw.png">
    </p>
</figure>

- Second, observe that the communication complexity of this protocol does not contradict the [Dolev-Reischuk lower bound](https://decentralizedthoughts.github.io/2019-08-16-byzantine-agreement-needs-quadratic-messages/). In particular, this protocol makes use of randomness to elect the committee whereas the lower bound only applies to deterministic protocols. However, at the same time, we do add an additional [setup assumption](https://decentralizedthoughts.github.io/2019-07-19-setup-assumptions/) of an agreed upon random value. Currently, all known protocols to generate this random value require $\text{poly}(n)$ communication. Nevertheless, once this random value is generated, all subsequent communication is sub-quadratic in $n$, and this can be used for consensus on multiple values too.
- Finally, an adaptive adversary can corrupt the entire committee, rendering all of the efficiency gains useless. We describe how to address this concern in the next [post](https://decentralizedthoughts.github.io/2023-01-05-player-replaceability-II/).

Please add your thoughts and comments on [Twitter](https://twitter.com/kartik1507/status/1611756421561057281?s=20)!
