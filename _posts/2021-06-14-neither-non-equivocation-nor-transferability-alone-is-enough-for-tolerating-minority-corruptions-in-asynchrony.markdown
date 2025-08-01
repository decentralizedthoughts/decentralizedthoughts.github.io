---
title: Neither Non-equivocation nor Transferability alone is enough for tolerating
  minority corruptions in asynchrony
date: 2021-06-14 12:04:00 -04:00
tags:
- lowerbound
- research
author: Sravya Yandamuri, Naama Ben David
---

In this post, we explore a theorem of [Clement, Junqueira, Kate, and Rodrigues](https://www.cs.purdue.edu/homes/akate/publications/Non-equivocation.pdf) from PODC 2012 regarding the limits of non-equivocation. Informally, this theorem says that neither *Non-equivocation* nor *Transferability* alone is enough for tolerating minority corruptions in asynchrony.


**Theorem [CJKR12](https://www.cs.purdue.edu/homes/akate/publications/Non-equivocation.pdf):** *Neither non-equivocation nor transferability is individually sufficient to solve asynchronous Reliable Broadcast given $n \leq 3f$ and a malicious adversary that can control $f$ parties.*


Let's define the notions of *transferable authentication* and *non-equivocation*:

**Transferable Authentication**
Transferability captures the notion of a party being able to transfer a proof of a statement to another party, such that if $p_i$ is able to evaluate the validity of statement $s$ using proof $q$, then $p_j$, who receives the same $s$ and $q$ from $p_i$, can also evaluate $s$ and obtain the same result. For the purposes of this post, we use a more specific definition for transferable authentication. A message $m$ is said to be authenticated if it is accompanied by a proof, $\sigma_i$, that it was sent by party $p_i$. Any party that receives $m$ and $\sigma_i$ can verify that $m$ was sent by $p_i$ using the function $verify(m, \sigma_{i})$. Note that authentication should be unforgeable, meaning that if $verify(m,\sigma_{i})=true$, and $p_i$ is non-faulty, $m$ must have been sent by $p_i$. We then define transferable authentication as when correct parties $p_j$ and $p_k$ always obtain the same result from $verify(m,\sigma_{i})$ when $p_k$ receives $m$ and $\sigma_i$ from $p_j$.

**Non-Equivocation**
[Chun et al.](https://dl.acm.org/doi/pdf/10.1145/1323293.1294280?casa_token=ntow64zqPTIAAAAA:R1ogvwWbiSeQHRR3LTrXt1xzEz3u__dOe_c8pb6JcKiij8xHvgV3bNFt5r-bW_1PKcvNt7EqsdSD) first defined equivocation as the ability of a Byzantine party to lie in different ways to different parties (or clients). In order to distinguish between equivocation and transferable authentication, we present the following picture. Consider a network in which each party has a trusted hardware module that all of their messages must pass through. The trusted hardware module only allows a message to be sent if the sender is not equivocating. So, if the sender $p_i$ sends $m$ to a party, they cannot send $m'!=m$ to any party. Note that this definition of equivocation does not imply transferability. A party knows that $m$ was sent by $p_i$ only because they received $m$ on an authenticated channel from $p_i$. If they send $m$ to another party, they cannot prove that it was sent from $p_i$.
![](https://i.imgur.com/bJE1Iaa.png)
In the image, there are 3 parties, each of which has a trusted hardware module. Each message sent by a party is passed through its trusted hardware module, enforcing that it does not equivocate.

**The proof**

See [this post](https://decentralizedthoughts.github.io/2019-06-25-on-the-impossibility-of-byzantine-agreement-for-n-equals-3f-in-partial-synchrony/) for an explanation on why Byzantine agreement in the partial synchrony setting (and asynchrony) requires $n\geq{3t+1}$.

We will prove the theorem for *Reliable Broadcast*, which is strictly weaker than consensus, as it does not guarantee termination in the case of a faulty leader. For a more in-depth description of Reliable Broadcast, see [this post](https://decentralizedthoughts.github.io/2020-09-19-living-with-asynchrony-brachas-reliable-broadcast/). To recap, the properties guaranteed by Reliable Broadcast can be summarized as follows:

**(validity)**: If the leader is non-faulty then eventually all non-faulty parties will output the leader’s input.

**(agreement)**: If some non-faulty party outputs a value then eventually all non-faulty parties will output the same value.

The proof of the theorem follows from the two claims below:

**Claim 1:** *Transferability without Non-Equivocation is not enough.*

Roughly speaking, for $n=3$, if the leader can equivocate it can break agreement. Transferability does not help because asynchrony can delay the messages between the two honest parties. 

We use an **indistinguishability proof**. See [this post](https://decentralizedthoughts.github.io/2019-06-25-on-the-impossibility-of-byzantine-agreement-for-n-equals-3f-in-partial-synchrony/) for a brief introduction to this proof technique. Imagine a network with three parties: A, B, and C. Party A is always the leader.

**World 1:** 
![](https://i.imgur.com/KaaCemV.png)
A and C are correct. A sends $m$ to B and C. B crashes before sending anything to C. Since A is a correct party, C decides $m$ by validity.


**World 2:** 
![](https://i.imgur.com/H5laWbd.png)
A and B are correct. A sends $m'$ to B and C. C crashes before sending anything to B. By validity, B decides $m'$.


**World 3:** 
![](https://i.imgur.com/gjfRiyw.png)
B and C are correct, and A is Byzantine. A sends $m'$ to B and $m$ to C. C cannot distinguish between World 3 and World 1 and delivers $m$. Messages between B and C are delayed. B cannot distinguish between World 3 and World 2 and delivers $m'$. This scenario violates agreement, as two honest parties B and C deliver different values.

**Claim 2:** *Non-Equivocation without Transferability is not enough.*


Roughly speaking, for $n=3$, if the leader is delayed then an honest party must rely on the third party. But if there is no transferability then this party can send a conflicting message and break validity.

Again, imagine a network with three parties: A, B, and C such that A is always the leader.

**World 1:** A, B, and C are all correct parties. A sends $m'$ to B and C, however its message to C is delayed until sometime $t'$. C receives $m'$ from B before $t'$. By validity, B delivers $m'$ before $t'$. By agreement (since B is deciding m'), C decides $m'$ before time $t'$ .
![](https://i.imgur.com/Ob5gClu.png)



**World 2:** A and C are correct, and B is Byzantine. A sends $m$ to B and C; however, A's message to C is delayed. C receives $m'$ from B prior to receiving a message from A. Since C cannot distinguish World 2 from World 1, it decides $m'$. By the property of validity, A decides $m$.
![](https://i.imgur.com/WNYZMbQ.png)


This scenario violates agreement, as two correct parties A and C decided different values. Note that in none of the worlds did any party equivocate by sending different messages to different parties.

This concludes the proof of the theorem. Note that the proof that non-equivocation alone is insufficient for Reliable Broadcast does not take into account the fact that A could have waited to hear from C that it heard the value $m'$. Although A and C delivering a value other than $m$ violates validity, they could still satisfy agreement. Perhaps a weaker primitive than Reliable Broadcast is possible with non-equivocation alone and $n\geq{2t+1}$. 

On the positive side, [Clement, Junqueira, Kate, and Rodrigues](https://www.cs.purdue.edu/homes/akate/publications/Non-equivocation.pdf) prove that given both non-equivocation **and** transferability, Reliable Broadcast for any $n > 2f$ is possible. 


**Acknowledgments** We would like to thank [Flavio Junqueira](https://scholar.google.com/citations?user=48qKfREAAAAJ&hl=en) for his insightful feedback and Ittai Abraham for his help with this post!

Please comment on [Twitter](https://twitter.com/ittaia/status/1405923076211097602?s=20).
