---
title: Multi-world Validated Asynchronous Byzantine Agreement
date: 2024-12-10 03:15:00 -05:00
tags:
- research
- asynchrony
author: Ittai Abraham, Alexander Spiegelman
---

In this post, we show how to solve Validated Asynchronous Byzantine Agreement using the multi-world VABA approach from [Abraham, Malkhi, and Spiegelman 2018](https://arxiv.org/pdf/1811.01332). 

## What is Validated Asynchronous Byzantine Agreement?

Given $n$ parties, with at most $f < n/3$ malicious (the optimal ratio for consensus with asynchronous communication), parties share an agreed-upon **external validity function** $EV(val)$ that defines the set of *valid* values. 

Each party holds a valid input value (the adversary may have multiple valid inputs). 

A **commit certificate** consists of a value and a **commit proof**. 

A **VABA** (Validated Asynchronous Byzantine Agreement) is a **protocol** that includes a **commit proof validity function** $CV(cert)$ and satisfies three essential properties:

1. **External validity**: If $CV(cert) = true$, then $EV(cert.val) = true$. Any commit certificate accepted by the commit proof validity function has a value accepted by the external validity function.
2. **Liveness**: In an expected constant number of rounds, all nonfaulty parties hold some $cert$ such that $CV(cert) = true$.
3. **Safety**: If $CV(cert) = true$ and $CV(cert') = true$, then $cert.val = cert'.val$. There cannot be two commit certificates on different values both accepted by the commit proof validity function.

## How to solve Validated Asynchronous Byzantine Agreement?

The [multi-world VABA](https://arxiv.org/pdf/1811.01332) combines two primitives:

1. A **randomness beacon** (e.g., a [threshold verifiable random function](https://eprint.iacr.org/2000/034.pdf) or [unique threshold signature scheme](https://www.iacr.org/archive/asiacrypt2001/22480516.pdf)) with these properties:

    1. *Beacon correctness*: For a given round, all parties output the same beacon value in $[1..n]$.  
    2. *Beacon liveness*: If all non-faulty parties output their beacon share, all will compute the beacon value.
    3. *Beacon unpredictability*: The adversary’s probability of guessing the beacon value for round $r$ before any non-faulty party releases its beacon share for round $r$ is $1/n$ (up to negligible advantage).

2. Running $n$ **instances in parallel** of (almost any) view-based **partial synchrony** validated Byzantine agreement protocol — for example, [PBFT](https://decentralizedthoughts.github.io/2022-11-20-pbft-via-locked-braodcast/) or [HotStuff](https://arxiv.org/pdf/1803.05069). These protocols satisfy:

    1. *Asynchronous Safety*: The partial synchrony protocol maintains safety for any *agreed* mapping of proposers to views. The beacon is used to choose (in hindsight) the agreed-upon mapping in each view.
    2. *Asynchronous Responsiveness*: If all non-faulty parties start a view whose proposer is non-faulty and no non-faulty party leaves the view for a constant number of rounds, they will all decide and terminate. This property is stronger than the minimum *liveness in synchrony* required by partial synchrony protocols.
    3. *External Validity*: The partial synchrony protocol’s decision is externally valid.

### Advantages of the multi-world VABA approach

1. It decomposes asynchronous challenges into simpler components: partial synchrony "worlds" and a randomness beacon. This modularity aids component reuse and simplifies understanding.
2. It achieves the asymptotically optimal $O(n^2)$ expected communication complexity.
3. As we will show in later posts, it can be extended to improve throughput and latency significantly.

## A sketch of the multi-world VABA protocol

Multi-world VABA is a *view-based protocol*. For view $v$:

Run $n$ instances (or worlds) of view $v$. In instance $i$, party $i$ is the proposer. Each instance runs independently as if others do not exist.

Once the proposer has a *commit certificate* in its instance, it sends that certificate to all parties and waits for $n{-}f$ confirmations, called a **done certificate**. The proposer then broadcasts the done certificate to all parties.

Each party waits for $n{-}f$ done certificates from $n{-}f$ *different instances*. Seeing proof that $n{-}f$ different instances have done certificates triggers the party to reveal its *share* of the beacon random value for view $v$.

Once the beacon value $b_v$ is revealed (typically after $n{-}f$ parties reveal their beacon shares for view $v$), parties proceed as in the partial synchrony protocol where $b_v$ is the agreed proposer for view $v$. All other instances are ignored (they become decoys in hindsight).

Obtaining the beacon value also triggers a *view change* to move from view $v$ to view $v+1$.

To start view $v+1$, parties send their *view change* information based on having $b_v$ as the proposer in view $v$.

### Sketch of liveness:

Consider the first nonfaulty party to see $n{-}f$ done certificates from $n{-}f$ different worlds. With constant probability, the beacon selects an instance in this set whose proposer completed a done certificate. Thus, as in a partial synchrony protocol, at least $f+1$ nonfaulty parties hold a commit certificate, so all parties will see this certificate in view $v+1$ (since any $n{-}f$ parties include at least one nonfaulty party with a commit certificate).

Note that the adversary must commit to a set of $n{-}f$ instances with done certificates **before** seeing the beacon value at a time when the beacon is unpredictable. This exemplifies the [general framework of using binding and randomization](/2024-12-10-bind-and-rand.md).

The result is that all nonfaulty parties will see a commit certificate after a constant expected number of views.

### Sketch of safety:

Each view has one real instance of a partial synchrony protocol; all others are decoys. Each view has exactly one agreed proposer, as in the partial synchrony protocol, so safety directly follows from the partial synchrony protocol’s safety.

### Sketch of external validity:

Like safety, this follows immediately from the external validity of the partial synchrony protocol.

### Scaling the multi-world VABA protocol:

The multi-world protocol runs $n$ instances per view. If each instance is linear, the expected cost is $O(n^2)$ words since the expected number of views until decision is constant.

One way to ensure linear cost per instance is to run the **robust keyed broadcast**, which involves running 4 instances of [provable broadcast](https://decentralizedthoughts.github.io/2022-09-10-provable-broadcast/).

Thus, $O(n^2)$ communication is spent to agree on $O(1)$ sized data, yielding an $O(n^2)$ ratio. We can improve throughput while keeping communication the same by using [batching](https://decentralizedthoughts.github.io/2023-09-30-scaling/).

We will expand on these ideas in future posts. For now, here is an overview:

1. Agreeing on a linear-size validated input using a **provable AVID** protocol (see [here](https://decentralizedthoughts.github.io/2024-08-08-vid/)). Each instance disperses its $O(n)$ input via provable dispersal costing $O(n)$, and after the beacon, we retrieve only the chosen instance at $O(n^2)$ cost. This maintains $O(n^2)$ communication while allowing agreement on $O(n)$ size data, improving throughput and achieving an $O(n)$ ratio.
2. If different proposers have different validated inputs, each can aggregate $O(n)$ dispersals into a single proposal. This keeps $O(n^2)$ communication while agreeing on $O(n)$ different validated inputs, each of size $O(n^2)$. If only data availability is needed, this improves scalability to [the asymptotically optimal $O(1)$ ratio](https://decentralizedthoughts.github.io/2023-09-30-scaling/).

### What about latency and log replication?

Extending this single-shot protocol to log replication is straightforward: just use a log replication partial synchrony protocol in each instance.

Improving latency requires protocol modifications. We will discuss this and handling imperfect randomness beacons in a later post.

Your thoughts and comments on [X](https://x.com/ittaia/status/1866608517140062650).