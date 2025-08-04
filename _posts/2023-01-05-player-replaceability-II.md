---
title: Player Replaceability - Towards Adaptive Security and Sub-quadratic Communication
  Simultaneously (Part II)
date: 2023-01-05 00:00:00 -05:00
tags:
- blockchain
- research
author: Kartik Nayak
---

This is part II of a two-part post on player-replaceability. Part I can be found [here](https://decentralizedthoughts.github.io/2023-01-05-player-replaceability-I/).

### Towards Adaptive Security for a Committee-based Protocol

The protocol described in the previous post achieved sub-quadratic communication. At a high-level, the key idea is to randomly sample an appropriate number parties in a committee, run consensus among the committee members, and disseminate the result to all other parties. It works well so far as the adversary is [static](https://decentralizedthoughts.github.io/2019-06-07-modeling-the-adversary/). However, since the committee size $\kappa$ is typically much smaller than $n$, an adaptive adversary can easily corrupt the entire committee after it is elected and consequently we lose all security properties. In fact, this would be a real concern in practice since an adversary can simply resort to bribing a small number of committee members, which is much easier than bribing up to $n/3$ parties.

Observe that if we can secretly generate a new committee for every round of the protocol uniformly at random, then we can also achieve the *ephemerality* property described earlier. Here, by *secretly*, we mean that before a committee member sends a message, only the member knows that it is in the committee. We must also stress that the committee should change after *every round*; thus, once a party is elected, it is only required to send a *single* message. Consequently, even if an adversary corrupts this party after it has sent the message, it may not be helpful since subsequent round elections are independent of previous rounds (some subtleties discussed later).

Thus, the key challenge is to secretly and verifiably elect this committee uniformly at random. [Verifiable random functions](https://dash.harvard.edu/bitstream/handle/1/5028196/Vadhan_VerifRandomFunction.pdf) (or VRFs) help us achieve this property. At a high-level, a VRF is a public key primitive with key-pair $(pk_i, sk_i)$. A VRF evaluation $VRF_{sk_i}(x)$, given the secret key $sk_i$ and an input $x$ produces a string $\rho_{i,x}$ and a proof $\pi_{i,x}$. The output of the evaluation has the following properties:
- **Verifiable:** Given the parties public key $pk_i$ and proof $\pi_{i,x}$, any party can indeed verify that $\rho_{i,x}$ was correctly computed by party $i$ on input $x$.
- **Random:** To any party that does not have $sk_i$, the output $\rho_{i,x}$ is computationally indistinguishable from a uniform random string.
- **Unique:** There does not exist $(\rho_{i,x}', \pi_{i,x}') \neq (\rho_{i,x}, \pi_{i,x})$ such that the verification process succeeds with public key $pk_i$ and input $x$.

Given VRFs, secret committee election can be achieved using the following simple rule given an input seed $x$. For round $j$, each party $i$ computes $\rho_{i,j} := VRF_{sk_i}(j, x)$. If this value is $< \kappa/n$ (when scaled to a number between 0 and 1), then the party is elected in the committee. This would ensure that we have a committee with expected size $\kappa$. If we need to elect a single leader in a round instead (for instance, to play the role of a leader in HotStuff), then each of the committee members would effectively send a message playing the role of the leader, and the party with the smallest value of $\rho_{i,j}$ can be selected as the leader.

<figure>
<p align="center">
<img align="center" height=250 src="https://i.imgur.com/hnQXrcA.png">
    </p>
</figure>

Thus, the protocol execution looks like the above picture. In each round $j$, a committee of expected size $\kappa$ is elected. They send round $j$ messages to all parties. The committee in round $j+1$ receive these messages and carry on the baton to send the next round message, effectively replacing the players in the previous round. Observe that every party receives messages from all the committee members in a round and it can thus, play the role of any committee member when called upon. Effectively, the committee as described in the static protocol is replaced by a virtual committee where the role of a committee member is played by a new party each time. The total communication complexity of the protocol is $O(\text{poly}(\kappa)\cdot n)$ so far as the number of rounds of execution and message sizes are bounded by $\text{poly}(k)$.
 
A final subtlety is related to the integrity of the messages sent by a committee member in the presence of an adaptive adversary. The adversary can perhaps not take back a message sent by a committee member --- however, it can make the committee member send signed equivocating messages potentially leading to safety (and liveness) violations. This can be dealt with using *ephemeral keys* or forward secure signature schemes. Informally, in a forward secure signing scheme, in the beginning, a party has a key that can sign any messages from any round; after signing a message for round $t$, the party updates its key to one that can henceforth sign only messages for round $t + 1$ or higher, and the round-$t$ secret key should be immediately erased at this point. This way, even if the attacker instantly corrupts a party, it cannot  send an equivocating message in the same round.

To summarize, we can obtain all of the desirable adaptivity properties described earlier. We obtain unpredictability and verifiability due to the use of VRFs to elect committees. We obtain integrity of messages using forward secure signature schemes. Finally, we obtain ephemerality by changing the committee in each round, requiring a committee member to send no more than a single message once it is elected.

Some additional pointers:
- **Extending to proof-of-stake:** All of the above discussion is relevant when considering player replaceability for a protocol with a fixed number of parties. When considering a proof-of-stake system, there are other aspects to consider. For instance, newer parties can join the system when they obtain some stake for the first time for. In the process, they would setup a new public key pair that may increase their chances of being on a committee for a given input $x$ used in the election. We will discuss these considerations in a future post.
- **Leader election challenges:** In the above protocol, parties, including the leader, may not be sure of who the leader is. In practice, it may be beneficial if there is a single secret leader who can prove to the world that it is indeed the leader. This primitive is called [Single Secret Leader Election (or SSLE)](https://eprint.iacr.org/2020/025.pdf).
- We used HotStuff as an example in this post to achieve sub-quadratic communication. In general, if we replace this by any protocol where the number of rounds and message sizes are (sub-)linear (or even polynomial) in the number of parties, we can potentially convert it into its player-replaceable counterpart.

**Acknowledgment.** Thanks to Ittai Abraham and Dahlia Malkhi for insightful comments on this post.

Please add your thoughts and comments on [Twitter](https://twitter.com/kartik1507/status/1611756421561057281?s=20)!
