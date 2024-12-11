---
title: Multi-world Validated Asynchronous Byzantine Agreement
date: 2024-12-10 03:15:00 -05:00
tags:
- dist101
- asynchrony
author: Ittai Abraham, Alexander Spiegelman
---

In this post, we show how to solve Validated Asynchronous Byzantine Agreement via the multi-world VABA approach of [Abraham, Malkhi, and Spiegelman 2018](https://arxiv.org/pdf/1811.01332). 

## What is Validated Asynchronous Byzantine Agreement?


Given $n$ parties, and at most $f<n/3$ of them can be malicious (this is the optimal ratio for consensus with asynchronous communication). Parties have an agreed-upon **external validity function** $EV(val)$ that defines the set of *valid* values. 

Each party possesses a valid input value (the adversary may have multiple valid input values). 

A **commit certificate** consists of a value and a **commit proof**. 

A **VABA** (Validated Asynchronous Byzantine Agreement) is a **protocol** that includes a **commit proof validity function** $CV(cert)$ and has three essential properties:


1. **External validity**: If $CV(cert)=true$, then $EV(cert.val)=true$. Any commit certificate that the commit proof validity function returns true on has a value that the external validity function returns true on.
2. **Liveness**: In an expected constant number of rounds, all nonfaulty parties hold some $cert$ such that $CV(cert)=true$ (a commit certificate that the commit proof validity function returns true on).
3. **Safety**: If $CV(cert)=true$ and $CV(cert')=true$, then $cert.val=cert'.val$. There cannot be two commit certificates on two different values that the commit proof validity function returns true on.


## How to solve Validated Asynchronous Byzantine Agreement?

The [multi-world VABA](https://arxiv.org/pdf/1811.01332) works via a combination of two primitives:

1. A **randomness beacon** (for example, a [threshold verifiable random function](https://eprint.iacr.org/2000/034.pdf) or [unique threshold signature scheme](https://www.iacr.org/archive/asiacrypt2001/22480516.pdf)) with the following properties:

    1. *Beacon correctness*: For a given round, all parties output the same beacon value in $[1..n]$.  
    2. *Beacon liveness*: If all non-faulty parties output their beacon share, then all will compute the beacon value.
    3. *Beacon unpredictability*: The adversary’s probability of guessing the beacon value for round $r$ before any non-faulty party releases its beacon share for round $r$ is $1/n$ (up to a negligible advantage).

2. Running $n$ **instances in parallel** of (almost any) view-based **partial synchrony** validated Byzantine agreement protocol (for example, [PBFT](https://decentralizedthoughts.github.io/2022-11-20-pbft-via-locked-braodcast/) or [HotStuff](https://arxiv.org/pdf/1803.05069)). We will use the following properties:
 
    1. *Asynchronous Safety*: The partial synchrony protocol maintains safety for any *agreed* mapping of proposers to views. Looking ahead, we will use the beacon above to choose (in hindsight) the agreed-upon mapping in each view.
    2. *Asynchronous Responsiveness*: If all non-faulty parties start a view whose proposer is non-faulty and no non-faulty leaves the view for a constant number of rounds, then they will all decide and terminate. Note that this property does not hold if, for example, a protocol needs a timeout in addition to a constant number of rounds (as may happen sometimes in two-round hotstuff). In this sense, this property is stronger than the minimum *liveness in synchrony* needed by partial synchrony protocols. 
    3. *External Validity*: The partial synchrony protocol decision is externally valid.





### The advantages of the multi-world VABA approach to solving VABA

1. It deconstructs asynchronous challenges into simpler challenges: partial synchrony "worlds" and a randomness beacon. This modular nature may help with component reuse and simplify learning.
2. It can obtain the asymptotically optimal $O(n^2)$ expected communication complexity.
3. As we show in later posts, it is possible to add significant throughput and latency improvements to this basic scheme.



## A sketch of the multi-world VABA protocol



Multi-world VABA is a *view-based protocol*. Here is the sketch of view $v$:

Run $n$ instances (or worlds) of view $v$. In instance $i$, the proposer is party $i$. Each instance runs logically as if the other instances do not exist.

Once the proposer has a *commit certificate* in its instance, it sends that certificate to all parties and waits for $n{-}f$ confirmations, which we call a **done certificate**. The proposer then sends the done certificate to all parties.


Each party then waits for $n{-}f$ done certificates from different instances. Seeing proof that $n{-}f$ instances have a done certificate is the trigger for it to reveal its share of the beacon random value for view $v$.

Once the beacon value $b_v$ is revealed, the parties act as they would if the partial synchrony protocol mapped proposer $b_v$ in view $v$. All other instances are ignored (they are essentially decoys in hindsight).

Obtaining the beacon value (typically when $n{-}f$ parties reveal their beacon share for view $v$) also serves as a *view change trigger* to move to the next view (view $v+1$).


To start view $v+1$, parties send their *view change* information based on having $b_v$ as the proposer in view $v$. 


### Sketch of liveness:

With constant probability, the beacon chooses an instance that has completed a done certificate, so just like in a partial synchrony protocol, there is now a commit certificate and all parties will see this certificate in view $v+1$.


Note that the adversary needs to bind to a set of $n{-}f$ instances that have a done certificate **before** seeing the beacon value at a stage when the beacon is unpredictable. This is an example of the [general framework of using binding and randomization](/2024-12-10-bind-and-rand.md).

### Sketch of safety:

Each view has one real instance of a partial synchrony protocol, and all the others are decoys. So each view has one agreed upon proposer, which is exactly what happens in the partial synchrony protocol - so the safety of this protocol is immediate from the safety of the partial synchrony protocol.


### Sketch of external validity:

Just like safety, this follows directly from the external validity of the partial synchrony protocol.



### Scaling the multi-world VABA protocol:


The multi-world protocol requires running $n$ instances per view. If each instance is linear then the expected cost is $O(n^2)$ words since the expected number of views till decision is constant.

A concrete way to obtain linear cost in each instance is to run the **robust keyed broadcast** which is just running 4 instances of [provable broadcast](https://decentralizedthoughts.github.io/2022-09-10-provable-broadcast/).

So we spend $O(n^2)$ communication to agree on a $O(1)$ size data. This gives a $O(n^2)$ ratio. We can improve the throughput while keeping the same communication to reduce this ratio?

We will expand on these ideas in future posts. For now here is an overview:

1. Agreeing on a linear-size validated input by using a **provable AVID** protocol (see [here](https://decentralizedthoughts.github.io/2024-08-08-vid/)). This keeps the $O(n^2)$ communication while allowing to agree on $O(n)$ size data improving the throughput. This gives a $O(n)$ ratio.
2. If different proposers have different validated inputs then each proposer can aggregate $O(n)$ dispersals and aggregate that into a single proposal. This still keeps the $O(n^2)$ communication while allowing to agree on $O(n)$ different validated inputs each of size $O(n^2)$. This improves the throughput to asymptotically optimal $O(1)$ ratio.


### What about latency and log replication?

Extending the sketch above from a single shot to a log replication protocol is strait forward: just use a log replication partial synchrony protocol in each instance.

Improving the latency requires changing the protocol. We will discuss this and dealing with non-perfect randomness beacons in a later post.

Your thoughts and comments on [X](https://x.com/ittaia/status/1866608517140062650).