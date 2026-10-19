---
title: "Byzantine Approximate Agreement: From One Round to a Complete Protocol"
date: 2026-10-17 09:00:00 +03:00
tags:
  - approximate-agreement
author: Ittai Abraham, Gilad Stern
---

The [previous post][previous] showed that one round of the **Robust Midpoint** protocol keeps every honest value inside the old honest range and cuts the span of those values in half. Repeating this round gives approximate agreement. We do this formally in this post by specifying how many rounds to run and when parties decide.

The update is the same as in the previous post: send the current value, discard the $f$ smallest and $f$ largest received values, and take the midpoint of what remains.

## The problem

There are $n>3f$ parties, of which at most $f$ are Byzantine. Every party has a reliable channel to every other party, and a receiver knows which party sent each message. Communication takes place in synchronous rounds: honest parties send at the start of each round, and their messages arrive by its end. Byzantine parties can send different messages to different recipients or send nothing. The adversary is computationally unbounded.

Each honest party starts with a rational input in $[0,1]$ and must output a rational value. For a common parameter $0<\epsilon\leq1$, approximate agreement requires:

* **Convex validity.** Every honest output lies between the smallest and largest honest inputs.
* **Approximate agreement.** Any two honest outputs differ by less than $\epsilon$.
* **Termination.** Every honest party eventually decides.

The known input interval and target approximation let everyone choose the same number of rounds before sending any messages. Set

$$
R=\left\lfloor\log_2\frac1\epsilon\right\rfloor+1.
$$

This choice gives $2^{-R}<\epsilon$. The $+1$ ensures strict inequality even when $1/\epsilon$ is a power of two.

**Theorem.** In the synchronous model with $n>3f$ and at most $f$ Byzantine parties, Robust Midpoint solves approximate agreement for honest rational inputs in $[0,1]$ and common target $0<\epsilon\leq1$. Every honest party decides after $R$ rounds, its output lies in the honest input range, and the honest output span is at most $2^{-R}<\epsilon$.

## The protocol

Each party keeps a current value $v$, initially its input. A message $\langle r,v\rangle$ sends a rational value $v$ for round $r$.

In round $r$, let $V$ contain the party's own value once and the first rational value received from each other party in a message for that round. Missing messages contribute no entry. Messages for other rounds and further messages from the same sender are ignored. $V$ is a multiset: equal values from different parties are separate entries.

For a multiset $V$, let $\operatorname{trim}(V)$ remove its $f$ smallest and $f$ largest entries. Each party runs the following for each round $r=1,\ldots,R$. It sends at the start of the round, collects values through the end, and then updates its value.

```text
1. Set V = {v} and send <r, v> to every other party.
2. Collect values into V through the end of the round,
   accepting the first rational value per other sender for round r.

3. Set T = trim(V).
4. Set v = (min(T) + max(T)) / 2.

5. If r = R:
       Decide v.
```

Due to synchrony, every $V$ contains all honest values, including the receiver's own. Thus $\lvert V\rvert\geq n-f>2f$, so trimming always leaves at least one value. No party waits for a Byzantine message.

## Analysis

Let $G_r$ be the multiset of honest values after round $r$, with $G_0$ the honest inputs. As in the previous post, define

$$
\operatorname{span}(G_r)=\max(G_r)-\min(G_r).
$$

We apply the two claims from the [previous post][previous] to each round and include their proofs here for completeness.

For an honest party $i$ in round $r$, let $V_i$ and $T_i$ be its received and trimmed multisets, and let $v_i$ be its value after the update.

**Claim 1.** Every honest party's trimmed interval lies in the old honest range and contains $\operatorname{median}(G_{r-1})$:

$$
\min(G_{r-1})
\leq\min(T_i)
\leq\operatorname{median}(G_{r-1})
\leq\max(T_i)
\leq\max(G_{r-1}).
$$

**Proof.** Only Byzantine entries can lie below $\min(G_{r-1})$ or above $\max(G_{r-1})$. There are at most $f$ such entries on either side, so trimming removes all of them.

There are at least $n-f\geq2f+1$ honest values. Hence at least $f+1$ honest values are at most their median, and at least $f+1$ are at least their median. All appear in $V_i$. Its $(f+1)$st smallest entry is therefore at most this median; this is $\min(T_i)$. Its $(f+1)$st largest entry is at least this median; this is $\max(T_i)$.

**Claim 2.** Each round halves the honest span:

$$
\operatorname{span}(G_r)\leq\frac{\operatorname{span}(G_{r-1})}{2}.
$$

**Proof.** Party $i$ sets $v_i$ to the midpoint of its trimmed interval. Claim 1 gives

$$
\frac{\min(G_{r-1})+\operatorname{median}(G_{r-1})}{2}
\leq v_i
\leq\frac{\operatorname{median}(G_{r-1})+\max(G_{r-1})}{2}.
$$

Every honest party's new value lies in this interval. Its width is

$$
\begin{gathered}
\frac{\operatorname{median}(G_{r-1})+\max(G_{r-1})}{2}
-\frac{\min(G_{r-1})+\operatorname{median}(G_{r-1})}{2}\\
=\frac{\max(G_{r-1})-\min(G_{r-1})}{2}
=\frac{\operatorname{span}(G_{r-1})}{2}.
\end{gathered}
$$

## Putting it together

**Claim 3.** The protocol satisfies convex validity, approximate agreement, and termination.

**Proof.** By Claim 1, every honest value after a round lies in the honest range before that round. Inductively, all honest values remain in the initial honest range, proving convex validity.

Applying Claim 2 in each round gives

$$
\operatorname{span}(G_R)
\leq\frac{\operatorname{span}(G_0)}{2^R}
\leq\frac1{2^R}
<\epsilon.
$$

Finally, each round ends without waiting for Byzantine parties, and all honest parties decide at the end of round $R$.

## Notes

For $\epsilon=1/n$, this protocol uses $\lfloor\log_2 n\rfloor+1$ rounds. The [Grade, Detect, Average post][gda] covers the work of [Ben-Or, Dolev, and Hoch][gradecast] that obtains $O(\log n/\log\log n)$ rounds.

For a simpler example of faster convergence, the [post on approximate agreement with omissions][omissions] replaces Byzantine failures with omissions and moves from midpoints to averages.

The [send-omission lower-bound post](/2026-10-19-approximate-agreement-send-omissions-lower-bound/) presents a modern proof of [Fekete’s lower bound][fekete] for approximate agreement. The Byzantine asymptotic lower bound was stated earlier by [Dolev, Lynch, Pinter, Stark, and Weihl][dolev]. For $\epsilon=1/n$ and $n=3f+1$, this implies an $\Omega(\log n/\log\log n)$ worst-case round lower bound for deterministic protocols.

[previous]: https://decentralizedthoughts.github.io/2022-06-07-approx-agreement-one/
[omissions]: /2026-10-18-approximate-agreement-with-omissions/
[gradecast]: https://arxiv.org/abs/1007.1049
[dolev]: https://groups.csail.mit.edu/tds/papers/Lynch/jacm86.pdf
[fekete]: https://groups.csail.mit.edu/tds/papers/Fekete/DistComp90.pdf

[gda]: /2026-10-18-byzantine-approximate-agreement-grade-detect-average/
