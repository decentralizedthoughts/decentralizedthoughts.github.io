---
title: Multi-Shot Benign Simplex on a Fixed View Schedule
date: 2026-11-08 09:00:00 +02:00
tags:
- consensus
- SMR
author: Ittai Abraham
chapters:
  - /2026-05-25-chapter-simplex/
background:
  - /2025-11-08-benign-simplex/
  - /2026-05-14-simplex-FVS/
  - /2026-03-07-simultaneous-agreement/
continue_reading:
  - /2026-05-20-from-single-shot-to-chained/
  - /2026-05-17-fast-simplex-fvs/
---

Can it get any simpler than this?

In this post we give a state machine replication protocol for partial synchrony against a minority of omission failures. We put multi-shot [Benign Simplex](https://decentralizedthoughts.github.io/2025-11-08-benign-simplex/) on a fixed view schedule with rotating leaders. Views have length $2\Delta$ and a good proposal commits in $2\delta$. Rotating leaders and running on a fixed view schedule make the protocol and its analysis surprisingly simple.

## Model

There are $n>2f$ parties, at most $f$ with omission failures. Faulty parties follow the protocol but may omit sending or receiving messages. A message sent at time $t$ between non-faulty parties arrives before $\max\{GST,t\}+\delta$, where $\delta\leq\Delta$.

Clocks are perfectly synchronized. View $v=1,2,\ldots$ starts at time

$$
s_v=2(v-1)\Delta.
$$

View $v$ has proposer `Leader(v)`, chosen in round robin order. `Extend(C)` appends the proposer's next input block to $C$. The block must be valid after $C$.

Any two committed chains must agree on every block position they share (uniform agreement). Every committed block must be valid after the blocks preceding it (validity). If valid blocks remain available, every non-faulty party must keep committing new blocks indefinitely (liveness).

## Votes and decisions

A `Vote(v, X)` proposes chain $X$ if sent by `Leader(v)`, or relays that proposal. A party that receives it by the deadline sends `Final(v, X)`. Otherwise it sends `NoFinal(v)`, promising never to send Final in that view.

A `Decide(v, X)` reports $n-f$ Finals for $X$, which commits $X$. A `NoDecide(v)` reports $n-f$ NoFinals, which means that view $v$ cannot commit.

A proposal in view $v$ appends the proposer's input block to either:

- a proposal $X_w$ from some view $0<w<v$, with `NoDecide(j)` for every $w<j<v$; or
- genesis, with `NoDecide(j)` for every $1\leq j<v$.

The function `ProposalRule(v)` uses the messages already received by the proposer. It chooses the largest $w$ satisfying one of the two conditions above, with $X_0$ denoting genesis, and returns `Extend(X_w)`. If no such $w$ exists, it returns $\bot$.

## The protocol

Process messages delivered at a scheduled time before that time's scheduled actions.

```text
Fixed view schedule B-Simplex

1. At time s_v:
    Enter view v
    If self = Leader(v):
        X := ProposalRule(v)
        If X ≠ ⊥:
            Send (Vote, v, X)

2. Upon first receiving (Vote, v, X):
    Send (Vote, v, X)
    If the time is at most s_v + Δ:
        Send (Final, v, X)

3. At time s_v + Δ, if no Final was sent in view v:
    Send (NoFinal, v)

4. Upon first receiving n−f (NoFinal, v)
   or one (NoDecide, v):
    Send (NoDecide, v)

5. Upon first receiving n−f (Final, v, X)
   or one (Decide, v, X):
    Commit X
    Send (Decide, v, X)
```

A Vote and NoDecide can coexist; receiving NoDecide does not prevent relaying a later proposal. Finals are sent only in the first half of their view. The next view starts at $s_v+2\Delta$ regardless of which messages have arrived; forwarding and commits continue in the background.

## Safety

**Claim 1.** Each view has at most one proposal. A view cannot have both Decide and NoDecide.

**Proof.** By Rule 1, only `Leader(v)` originates a proposal in view $v$, and it does so at most once. Rule 2 only relays that proposal. This also holds for parties with omission failures.

Rules 2 and 3 prevent a party from sending both Final and NoFinal in a view: Final is sent only by $s_v+\Delta$, and NoFinal is sent then only if no Final was sent. Since $n>2f$, their quorums intersect and cannot coexist. NoDecide originates from a NoFinal quorum (Rule 4), and Decide from a Final quorum (Rule 5), so they cannot coexist in the same view.

**Claim 2.** If $X$ commits in view $j$, every proposal in a later view extends $X$.

**Proof.** A commit in view $j$ implies a Final quorum (Rule 5), so the quorum argument in Claim 1 excludes `NoDecide(j)`.

Induct on $v>j$. In Rule 1, `ProposalRule(v)` requires NoDecide for every view between the chosen parent and $v$. A parent from before $j$, including genesis, would therefore require `NoDecide(j)`. If the parent is from $j$, it is $X$ by uniqueness. If it is from a view $j<w<v$, it extends $X$ by induction. In either case, `ProposalRule(v)` extends that parent.

Uniform agreement follows. Validity follows because `ProposalRule(v)` uses `Extend` to append a valid block to its parent chain.

## Catch up and latency

**Claim 3.** For every view $j$, all non-faulty parties obtain either its proposal or `NoDecide(j)` by

$$
\max\{GST,s_j+\Delta\}+\delta.
$$

**Proof.** If a non-faulty party sends Final in view $j$, it also relays the proposal by $s_j+\Delta$ (Rule 2), so all non-faulty parties receive it by the claimed time. Otherwise all non-faulty parties send NoFinal at $s_j+\Delta$ (Rule 3). Each receives a NoFinal quorum and sends NoDecide by the claimed time (Rule 4).

At every view start $s_v\geq GST+\delta$, each non-faulty party has a proposal or NoDecide for every earlier view $j<v$, since

$$
\max\{GST,s_j+\Delta\}+\delta\leq s_v.
$$

Let $w$ be the latest earlier view whose proposal the proposer has received, or $w=0$ if it has none. It has `NoDecide(j)` for every $w<j<v$, so `ProposalRule(v)` returns the chain `Extend(X_w)`.

**Claim 4.** If $s_v\geq GST+\delta$ and `Leader(v)` is non-faulty, all non-faulty parties commit its proposal by $s_v+2\delta$.

**Proof.** By Claim 3, `ProposalRule(v)` returns a chain, which Rule 1 sends at $s_v$. All non-faulty parties receive it by $s_v+\delta\leq s_v+\Delta$ and send Final (Rule 2). They receive a Final quorum and commit by $s_v+2\delta\leq s_v+2\Delta$ (Rule 5).

Starting at view $v$ with $s_v\geq GST+\delta$, if $t$ faulty scheduled proposers precede the next non-faulty proposer, all non-faulty parties commit within $2t\Delta+2\delta$.

Round robin gives non-faulty parties infinitely many turns to propose. Each such proposal after $GST+\delta$ extends every earlier committed chain by at least one block (Claim 2) and commits at every non-faulty party (Claim 4), giving unbounded growth.

The protocol uses $O(n^2)$ messages per view, excluding the size of proposal histories.
