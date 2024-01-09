---
title: 'Living with Asynchrony: the Gather Protocol with Binding and Verifiability'
date: 2024-01-09 18:00:00 -05:00
tags:
- asynchrony
author: Gilad Stern and Ittai Abraham
---

We extend the [Gather protocol](https://decentralizedthoughts.github.io/2021-03-26-living-with-asynchrony-the-gather-protocol/) with two important properties: *Binding* and *Verifiability*. This post is based on and somewhat simplifies the *information theoretic* gather protocol in our recent [ACS work](https://eprint.iacr.org/2023/1130) with Gilad Asharov and Arpita Patra.

Recall that we are in an asynchronous model, assuming $f<n/3$, with at most $f$ Byzantine corruptions.

## Basic Gather Refresher

As a quick reminder, each party $i$ has an input $x_i$ to the protocol and outputs a set $S_i$ of at least $n-f$ tuples of the form $(j,x)$. The basic *validity* property: for every $(j,x)\in S_i$ such that $i$ and $j$ are nonfaulty, $x=x_j$. The more subtle property is *common core existence*: there exists some set $S^*$ of at least $n-f$ tuples that every nonfaulty party includes in its output (formally, for every nonfaulty $i$, $S^*\subseteq S_i$).

The protocol [in our previous post](https://decentralizedthoughts.github.io/2021-03-26-living-with-asynchrony-the-gather-protocol/) works as follows:

1. Broadcast $x_i$ (using [reliable broadcast](https://decentralizedthoughts.github.io/2020-09-19-living-with-asynchrony-brachas-reliable-broadcast/)).
2. Let $S_i$ be the set of pairs $(j,x_j)$, where $x_j$ was received from $j$. Once $S_i$ contains $n-f$ pairs send $S_i$ to every party.
3. When receiving a message $S_j$ from party $j$, accept the message after receiving the broadcast $x_k$ from $k$ for every $(k,x_k)\in S_j$. After accepting $n-f$ sets $S_j$, send $T_i=\cup S_j$ to all parties.
4. When receiving a message $T_j$ from party $j$, accept the message after receiving the broadcast $x_k$ from $k$ for every $(k,x_k)\in T_j$. After accepting $n-f$ sets $T_j$, output $U_i=\cup T_j$.

## Extending Gather with Binding: gathering secrets before revealing them

When the values sent in the gather protocol are all public, for example as in [approximate agreement](https://www.cs.huji.ac.il/w~ittaia/papers/AAD-OPODIS04.pdf), the properties of basic Gather are sufficient.

But for other [applications](https://arxiv.org/abs/2102.09041), the gather values are [secret shares](https://decentralizedthoughts.github.io/2020-07-17-polynomial-secret-sharing-and-the-lagrange-basis/), and **we want to reveal the secrets only after a common core is fixed**. In some settings, secret values may be revealed once $n-2f$ nonfaulty parties complete the gather. So we want the property that the *core is fixed once the first nonfaulty completes the gather protocol*. We call this property ***binding***. Generally, a protocol is binding if it defines the output (or parts of it) at the time the first nonfaulty party completes the protocol. 

**Binding Core**: The common core $S^*$ is **fixed** at the time of the execution in which the first nonfaulty party completes the gather protocol. 

<details>

<summary>More Formal definition of <b>fixed</b>.</summary>

**Binding Core**: There exists an (efficient) extractor algorithm $X$ that takes the views of all nonfaulty parties and outputs a set $X(V)=S$ such that if $V^*$ is the views of the nonfaulty at the time of the execution in which the first nonfaulty party completes the gather protocol then $X(V^*)=S^*$ and the output of any nonfaulty party contains $S^*$.

</details>

Note that basic gather does not have Binding Core! While eventually there is some common-core that all nonfaulty parties include in their output, that core can be chosen by the adversary at the time the last nonfaulty party completes the gather protocol. 

Observe that [our proof of basic Gather core existence](https://decentralizedthoughts.github.io/2021-03-26-living-with-asynchrony-the-gather-protocol/) uses a counting argument to define the core, but that argument is made with respect to the outputs of all nonfaulty parties (and thus we define the core late in our proof as well).

### Gather with Binding

{: .box-note}
To achieve binding, we employ the most important trick in distributed computing: **adding another round**:

1. Broadcast $x_i$ ([reliable broadcast](https://decentralizedthoughts.github.io/2020-09-19-living-with-asynchrony-brachas-reliable-broadcast/)).
2. Define the set $S_i$ of pairs $(j,x_j)$, where $x_j$ was received from $j$. Once $S_i$ contains $n-f$ pairs send $S_i$ to every party.
3. When receiving a message $S_j$ from party $j$, accept the message after receiving the broadcast $x_k$ from $k$ for every $(k,x_k)\in S_j$. After accepting $n-f$ sets $S_j$, send $T_i=\cup S_j$ to all parties.
4. When receiving a message $T_j$ from party $j$, accept the message after receiving the broadcast $x_k$ from $k$ for every $(k,x_k)\in T_j$. After accepting $n-f$ sets $T_j$, send $U_i=\cup T_j$ to all parties.
5. When receiving a message $U_j$ from party $j$, accept the message after receiving the broadcast $x_k$ from $k$ for every $(k,x_k)\in U_j$. After accepting $n-f$ sets $U_j$, output $V_i=\cup U_j$.

The proofs of the validity and termination properties of this protocol remain straightforward. Let's prove that the protocol has a binding common core: 

Consider the *first nonfaulty party* that completed the protocol. Denote its output as $V$. The set $V$ contains $n{-}f~$ $U$ sets, so least $n{-}2f$ of these $U$ sets must be from nonfaulty parties.

Let $U^1,\dots,U^{f+1}$ be some $f+1$ sets from nonfaulty that form the set $V$ (for concreteness, choose the $f+1$ lexicographically first). Define:
$$
S^*= \bigcap_1^{f+1} U^i
$$

By its definition, $S^*$ is fixed once the first nonfaulty completes the gather protocol.

The proof concludes with the following two claims:

**Claim 1:** $|S^*| \geq n-f$.

**Claim 2:** Any nonfaulty output contains $S^*$.


*Proof of claim 1:* This follows from the regular common core property on the first 4 rounds (see proof in [previous post](https://decentralizedthoughts.github.io/2021-03-26-living-with-asynchrony-the-gather-protocol/)). So there must exist a set $S$ of at least $n-f$ tuples such that $S\subseteq U_i$ for all nonfaulty parties $i$ (because that would have been $i$'s output in the basic Gather protocol). Note that all we know is that eventually there exists some $S$ such that $S \subseteq S^*$ and in fact, $S$ may not be fixed yet.

Note the little trick we did here. We do not know which set will eventually be the core as we defined it for the "regular" gather protocol. However, we do know that when nonfaulty parties eventually send their $U_i$ sets, all of these sets must have a large intersection. This immediately means that any number of $U_i$ sets sent by nonfaulty parties will have a large intersection as well.

*Proof of claim 2:* any nonfaulty party that completes the protocol waits to first receive $n-f$ sets $U_i$ and outputs the union of these sets. From quorum intersection, at least one of the $U_i$ sets was received from one of the nonfaulty parties defined above. These parties sent the sets $U^1,\dots, U^{f+1}$ that all include the core $S^*$, and thus every party will include the core in its output.

Note that $S^*$ is defined at the time the first nonfaulty party completes the protocol, and thus the core is binding.


## Extending Gather with Verifiability: verifying that a faulty party's output also includes the common core

In Gather, all nonfaulty parties output sets that include a common core. However faulty parties can output sets that do not include the core. For some protocols (for example, when proving you chose the correct leader in asynchrony) it is important that faulty parties must not be able to output sets that do not include the common core.

We cannot force faulty parties to include the common core but we can do the next best thing: make them prove that their output contains the common core. For this, we need to be able to *verify* the output of parties.


We formalize with a function $Verify$ that takes as input a set $S$ and the local state of the party and outputs either 0 or 1. We denote $Verify_i$ the function with the state of party $i$.

$Verify$ has three properties:

1. **Monotonicity**: If $Verify_i(S)=1$, then $Verify_i(S)=1$ at any later time.
2. **Safety**: If $Verify_i(S)=1$, then $S$ contains the common core.
3. **Liveness**: If $S$ is the output of a nonfaulty party, then eventually there is a time when $Verify_i(S)=1$.

Note that we do ***not*** require $Verify$ to have **transferability**. If $Verify_i(S)=1$ then without transferability it is not necessarily the case that eventually $Verify_i(S)=1$ for all non-faulty. We will discuss how to add this at the end.

### Gather with Verifiability

{: .box-note}
To obtain verifiability, we again employ the most important trick in distributed computing: **adding another round**.

So we run the same protocol as above, but instead of outputting the sets $V_i$, we send these to all parties. We then add the following unsurprising code:

6. Upon receiving a message $V_j$ from party $j$, accept the message after receiving the broadcast $x_k$ from $k$ for every $(k,x_k)\in V_j$. After accepting $n-f$ sets $V_j$, output $W_i=\cup V_j$.

How does this help us in verification? We know that every nonfaulty party $j$ has the set $S^*$ in its $V_j$ set. This means that we can indirectly check if $S^*$ is contained in $S$ by checking if at least one nonfaulty party's $V$ set is contained in $S$. We can easily do that by simply checking if $S$ contains at least $f+1$ sets $V_j$, since at least one of those sets will be a set sent by a nonfaulty party. 

Using this trick, we also know that nonfaulty parties will accept each other's sets. That is because a nonfaulty $i$ outputs a set $W_i$ that is the union of $n-f$ sets $V_j$. At least $f+1$ of those sets were sent by nonfaulty parties that send these sets to everybody. Every nonfaulty party will eventually receive these sets and accept $W_i$.  

This leads us to the following manner of verifying a set $S$:

* Upon receiving $V_j$ sets from $f+1$ parties such that $V_j\subseteq S$, output 1 (and wait until this happens if this is not the case).

## Notes and an exercise 

* Instead of sending sets that include pairs, we can include just  the index of the sender. This allows us to optimize the protocols, especially when the $x_i$ are large.

* In this post and the previous we present a version of gather where the sets are not broadcast. See [here](https://arxiv.org/abs/2102.09041) for a variation of gather that broadcasts the sets. 
* The common core in this post is of size $n-f$. While the conference version of [Canetti and Rabin 93](https://dl.acm.org/doi/10.1145/167088.167105) is underspecified, the version in [Canetti's thesis](https://www.wisdom.weizmann.ac.il/~oded/ran-phd.html) seems to offer a binding core of size $n-2f$. For some use cases a core of size $f+1$ is sufficient.
* **Exercise 1:** Suppose that parties need to broadcast their output - how can you guarantee the **transferability** property defined above?
* **Exercise 2:** For $n=4$ provide a concrete Binding violation example for the basic gather protocol.


Please send your feedback/comments and solutions on [Twitter]().