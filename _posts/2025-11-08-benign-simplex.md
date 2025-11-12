---
title: Benign Simplex
date: 2025-11-08 04:30:00 -05:00
tags:
- dist101
author: Ittai Abraham
---

The goal of this post is to describe a *single-shot* [consensus](https://decentralizedthoughts.github.io/2019-06-27-defining-consensus/) protocol that is resilient to *f < n/2* [omission failures](https://decentralizedthoughts.github.io/2019-06-07-modeling-the-adversary/), under [partial synchrony](https://decentralizedthoughts.github.io/2019-06-01-2019-5-31-models/).
This protocol is inspired by the multi-shot [Simplex for crash faults](https://simplex.blog/crashfaults/) protocol and our earlier posts on [Chained Raft](https://decentralizedthoughts.github.io/2021-07-17-simplifying-raft-with-chaining/), [Benign HotStuff](https://decentralizedthoughts.github.io/2021-04-02-benign-hotstuff/), and [Log Paxos](https://decentralizedthoughts.github.io/2021-09-30-distributed-consensus-made-simple-for-real-this-time/).

## Single-Shot Consensus

Each party starts with an *input value*. We denote by $\bot$ a special value that is not an input value.

1. **Liveness**: All non-faulty eventually *decide* on some value.
2. **Validity**: Decision value is one of the parties’ input values.
3. **Uniform Agreement**: All decision values are the same.

## The single-shot benign simplex protocol

As with all partial synchrony protocols, this one progress with a series of *views*. Each view $k$ has a designated leader denoted by *Leader(k)* (for example using a round-robin).


```text
B-Simplex

val := input

1. Upon entering view k:
    Start a local timer T_k
    Leader(k) sends (Vote, k, val)

2. Upon receiving (Vote, k, x):
    If x ≠ ⊥:
        val := x        // lock on x
        If T_k < 2Δ:
            Send (Final, k, x)
    Send (Vote, k, x)
    Enter view k+1

3. Upon T_k = 2Δ and not yet sent Final:
    Send (NoVote, k)

4. Upon receiving n−f (NoVote, k):
    Send (Vote, k, ⊥)
    Enter view k+1

5. Upon receiving n−f (Final, k, x) or one (Decide, x):
    Decide x
    Send (Decide, x)
    Terminate
```

## Partial Synchrony

We work in the partial synchrony model with a global stabilization time $GST$. After $GST$ every message arrives after at most $\Delta$ delay. For a given execution, we denote by $\delta \le \Delta$ the actual maximal delay after $GST$.

## Liveness

### Claim 1 (non-faulty start $\delta$ apart)

If a non-faulty party starts view $k+1$ at time $t > GST$, then all non-faulty parties start view $k+1$ before $t + \delta$.

**Proof:**  
Entering view $k+1$ requires leaving view $k$, which always includes sending a `Vote` message. Any `Vote` that triggered the first party to leave view $k$ is delivered to all others within $\delta$, so all leave $k$ and start $k+1$ by $t + \delta$.



### Claim 2 (views are short)

Let $t$ be the time all non-faulty parties have entered view $k$. Then all non-faulty parties leave view $k$ before $t + 2\Delta +\delta$.

**Proof:**  
If some `Vote(k, x)` is delivered while $T_k < 2\Delta$, rule 2 makes each receiver immediately send `(Vote, k, x)` and enter view $k+1$, by $t + 2\Delta+\delta$.

If no `Vote` arrives before $T_k = 2\Delta$, every non-faulty party sends `NoVote(k)` by time $t + 2\Delta$. Collecting $n - f$ `NoVote` messages then takes one $\delta$ time, after which rule 4 sends `(Vote, k, ⊥)` and immediately enters view $k+1$. Thus all leave by $t + 2\Delta+\delta$.



### Claim 3 (good leader decides after GST)

Let $k$ be the first view where all non-faulty parties start at a time $t > GST$ and that has a non-faulty leader. If no party has seen $n - f$ `Final` messages from any earlier view, then all non-faulty parties decide in view $k$ by time $t + 2\delta$.

**Proof:**  
At time $t$ the non-faulty leader sends `(Vote, k, x)`. Within one $\delta$ time all non-faulty parties receive this `Vote`. Since $T_k < 2\Delta$ they all send `(Final, k, x)`. Within one $\delta$ time each non-faulty party accumulates $n - f$ `Final(k, x)` messages and triggers decision by rule 5. 


### Claim 4 (liveness)

All non-faulty parties decide before $GST + 2f\Delta + (f+2)\delta \le GST + 3f\Delta+2\Delta$

**Proof:**  
After $GST$, Claim 1 keeps views aligned within $\Delta$. There can be at most $f$ views with faulty leaders. Each such view lasts at most $2\Delta +\delta$ by Claim 2. In the first view with a non-faulty leader, Claim 3 ensures decision within an additional $2\delta$


## Safety

### Claim 5 (if any party decides, all parties lock)

If $n - f$ parties send `(Final, k, x)`, then any party leaving view $k$ sets `val := x` during view $k$.

**Proof:**  
If a party leaves via rule 2 with a non-$\bot$ value, it must have seen some `(Vote, k, x)` and therefore sets `val := x` before leaving. The only way to send `Vote(k, ⊥)` is after receiving $n - f$ `NoVote(k)` messages, which contradicts the existence of $n - f$ `(Final, k, x)` messages for the same view. Hence, every party sets `val := x` before leaving view $k$.


### Claim 6 (uniform agreement)

Let $k$ be the first view where $n - f$ parties send `(Final, k, x)`. Then any later `Vote` is for $x$.

**Proof:**  
By Claim 5, all non-faulty parties have `val := x` when entering view $k+1$. Rule 2 propagates only the current `val`. Induction over the views gives that any `Vote` in a view grater than $k$ is for the value $x$, establishing uniform agreement.


## Validity

### Claim 7 (validity)

The decided value is the input of some party.

**Proof:**  
Initially each `val` equals the party's input. Later views only propagate existing `val` values through `Vote`, so by induction the decided value must be an original input.

---

## Notes


1. Message complexity is $O(n^2)$ per view, hence $O(n^3)$ after $GST$ in the worst case. This is not optimal, but may be a good practical trade-off.
2. The protocol does not always wait for $n - f$ to change views. Waiting for $n - f$ happens only when all observed messages are `NoVote`. A single `Vote` is sufficient to move forward, which reduces latency in the common case.
3. The use of an explicit `NoVote` is a critical tool for better latency that is borrowed from Simplex and what makes this protocol different from many other Paxos based protocols.
4. Open problem: is it possible to improve the worst case latency or obtain this latency with $O(n^2)$ message complexity?

## Acknowledgments

Many thanks for Kartik Nayak for insightful comments.

Your thoughts on [X]()
