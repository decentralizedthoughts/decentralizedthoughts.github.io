---
title: From Benign Simplex to Byzantine Simplex
date: 2025-11-15 04:30:00 -05:00
tags:
- dist101
author: Ittai Abraham
---

In this post we present a [Simplex](https://simplex.blog)  protocol that solves single shot [consensus](https://decentralizedthoughts.github.io/2019-06-27-defining-consensus/) and is resilient to $f < n/3$ [Byzantine failures](https://decentralizedthoughts.github.io/2019-06-07-modeling-the-adversary/), under [partial synchrony](https://decentralizedthoughts.github.io/2019-06-01-2019-5-31-models/). In a previous post we showed how to move [from Tendermint to Simplex](https://decentralizedthoughts.github.io/2025-06-18-simplex/).

In this post we show how to move from [Benign Simplex](https://decentralizedthoughts.github.io/2025-11-08-benign-simplex/) to Simplex. Benign Simplex is resilient to $f<n/2$ omission failures in the same setting. Moving from omission failures to Byzantine failures requires three changes:

1. To prevent the adversary from controlling more than $f$ parties, we add signatures to all messages. This prevents the adversary from forging incorrect proposals when the leader is honest or forge votes from honest voters.
2. To prevent a malicious leader from equivocating, we require $f<n/3$ and the protocol waits for $n{-}f$ votes for the same value. When honest parties vote for at most one value, this prevents having $n{-}f$ votes for two different values. Because for $f<n/3$, any two sets of size $n{-}f$ must intersect by more than $f$, indicating some honest party voted twice.
3. To protect against a malicious leader proposing an *unsafe* value in view $k$. An unsafe value is a value that is different from the value that was committed in a previous view. To do this, Simplex obtains the following skip property:
    
    * **Skip property**: If a view $v$ has $n{-}f$ `<Vote, v, ⊥>` messages,  then no decision certificate can form in this view.    
    
    Simplex uses this property to verify that the leader's proposal comes from the highest view $w<k$ in which there could have been a decision for $x$, this guarantees that the proposal is safe. This verification is done by checking that:

    1. All views $w<v<k$ have $n{-}f$ `<Vote, v, ⊥>`.
    2. If $w>0$ then there are $n{-}f$ `<Vote, w, x>`.
    3. If $w=0$ we check that $x$ is externally valid (signed by a client).
    
    Safety is provided because a view with a decision certificate cannot be skipped, hence forcing the proposer to use a proposal from that view or higher (and higher is safe via induction).

That's it! With these three changes we get Provable Validated Byzantine Agreement.

## Single-Shot Provable Validated Byzantine Agreement

Each party starts with an *input value* that is externally valid (signed by some client). We denote by $\bot$ a special value that is not an input value.

1. **Liveness**: All honest eventually obtain a *decision certificate*.
2. **External Validity**: Decision certificates have an externally valid value.
3. **Provable Agreement**: All decision certificates have the same value.

## The single-shot simplex protocol

```text
Simplex

val := input
w := 0       // the view this input came from


1. Upon entering view k:
    Start a local timer T_k
    Leader(k) sends <Propose, k, val, w>

2. Upon receiving <Propose, k, x, w>
        from leader(k) for the first time
        and for all views w < v < k exists n−f <Vote, v, ⊥>
        and if w > 0, exists n-f <Vote, w, x>
        and if w = 0, x is externally valid:
    Send <Vote, k, x>


3. Upon receiving n−f <Vote, k, x>:
    If x ≠ ⊥:
        val := x
        w := k
        If T_k < 3Δ:
            Send <Final, k, x>
    Send n-f <Vote, k, x>
    Enter view k+1

4. Upon T_k = 3Δ and not yet sent Final:
    Send <Vote, k, ⊥>

5. Upon receiving n−f <Vote, k, ⊥>:
    Send n−f <Vote, k, ⊥>
    Enter view k+1

6. Upon receiving n−f <Final, k, x>:
    This is a decision certificate for x
    Send n−f <Final, k, x>
    Terminate
```

## Partial Synchrony

We work in the partial synchrony model with a global stabilization time $GST$. After $GST$ every message arrives after at most $\Delta$ delay. For a given execution, we denote by $\delta \le \Delta$ the actual maximal delay after $GST$.

## Liveness

### Claim 1 (honest start $\delta$ apart)

If an honest party starts view $k+1$ at time $t > GST$, then all honest parties start view $k+1$ before $t + \delta$.

**Proof:**  
Entering view $k+1$ requires leaving view $k$, which always includes sending $n{-}f$ `Vote` messages. Any $n{-}f$ `Vote` messages that triggered the first party to leave view $k$ is delivered to all others within $\delta$, so all leave $k$ and start $k+1$ by $t + \delta$.

### Claim 2 (views are short)

Let $t$ be the time all honest parties have entered view $k$. Then all honest parties leave view $k$ before $t + 3\Delta +\delta$.

**Proof:**  
If some `<Final, k, x>` is sent by an honest party then it happened $\le 3 \Delta$, along with $n{-}f$ `<Vote, k, x>`, so all honest enter view $k+1$, by $t + 3\Delta+\delta$.

If no honest sends `<Final, k, x>` then all honest send `<Vote, k, ⊥>` by $t+3\Delta$, so by $t + 3\Delta+\delta$ all honest see $n{-}f$ `<Vote, k, ⊥>` and enter view $k+1$.

### Claim 3 (good leader decides after GST)

Let $k$ be the first view where all honest parties start at a time $t > GST$ and that has an honest leader. If no honest has seen $n - f$ `Final` messages from any earlier view, then all honest parties decide in view $k$ by time $t + 3\delta$.

**Proof:**  
At time $t$ the honest leader sends `<Propose, k, x, w>`. Within one $\delta$ time all honest parties receive this `Propose`. 

Since the leader is honest it sends the value $x$ from the highest view $w$ for which it saw $n{-}f$ `<Vote, w, x>` and that means for all higher views $w<v<k$ it saw $n{-}f$ `<Vote, v, ⊥>`. Hence for all views $w \le v<k$ the leader has previously sent for each view $v$ the required verification.

Since we are after $GST$, those will all arrive to all honest parties before (or with) the proposal, hence all honest will send `<Vote, k, x>`.


Within one more $\delta$, all honest will see $n{-}f$ `<Vote, k, x>` and send  `<Final, k, x>`. Within one $\delta$ time each honest party accumulates $n{-}f$ `<Final, k, x>` messages and triggers decision. 


### Claim 4 (liveness)

All honest parties hold a decision certificate before $GST + 3f\Delta + (f+3)\delta \le GST + 4f\Delta+3\Delta$.

**Proof:**  
After $GST$, Claim 1 keeps views aligned within $\Delta$. There can be at most $f$ views with faulty leaders. Each such view lasts at most $3\Delta +\delta$ by Claim 2. In the first view with an honest leader, Claim 3 ensures decision within an additional $3\delta$

## Safety

### Claim 5 (no skip in decision view)

If $n - f$ parties send `<Final, k, x>`, then any honest party leaving view $k$ sets `val := x` and `w := k` during view $k$. Moreover, there cannot be $n{-}f$ `<Vote, k, ⊥>`.

**Proof:**  
If an honest party leaves due to $n{-}f$ non-$\bot$ votes, due to quorum intersection it must be that this value is $x$ and therefore sets `val := x` and `w := k` before leaving. 

This is because $2(n − f) > n + f$ when $f < n/3$, so any two quorums of size $n − f$ intersect in at least $n − 2f > f$ parties


The only other way to leave view $k$ is due to $n{-}f$ `<Vote, k, ⊥>`, but since we know there are $n{-}f$ `<Final, k, x>` messages, again due to quorum intersection this cannot happen as honest parties do not send both `<Final, k, x>` and `<Vote, k, ⊥>` messages.


### Claim 6 (provable agreement)

Let $k$ be the first view where $n{-}f$ parties send `<Final, k, x>`. Then any honest that sends a `Vote` in any view $>k$ is only for the value $x$.

**Proof:**  
By Claim 5, there cannot be $n{-}f$ `<Vote, k, ⊥>`, hence the only way to accept a proposal is if it has $w\ge k$. (This is because accepting a proposal for $w<k$ requires showing $n{-}f$ `<Vote, k, ⊥>`).


An induction argument shows that this implies that the only `Vote` from an honest party is for a value $x$.

Claim 6 implies that any $n{-}f$ `<Final, k', x'>` for $k'>k$ must be for $x'=x$ hence we get provable agreement.

## Validity

### Claim 7 (validity)

The decided value is externally valid (signed by a client).

**Proof:**  
Initially each `val` is externally valid and this is checked before voting. Later views only propagate existing `val` values through $n{-}f$ `Vote`, so by induction the decided value must be externally valid.


Your thoughts on [X](...)