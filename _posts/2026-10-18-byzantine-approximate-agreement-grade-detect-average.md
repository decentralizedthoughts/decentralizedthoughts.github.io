---
title: "Byzantine Approximate Agreement: Grade, Detect, Average"
date: 2026-10-18 04:00:00 -05:00
tags:
  - approximate-agreement
author: Ittai Abraham, Gilad Stern
background:
  - /2026-10-17-approximate-agreement-complete-protocol/
  - /2019-10-22-flavours-of-broadcast/
continue_reading:
  - /2026-10-18-approximate-agreement-with-omissions/
  - /2026-10-19-approximate-agreement-send-omissions-lower-bound/
---

The [previous post](https://decentralizedthoughts.github.io/2026-10-17-approximate-agreement-complete-protocol/) gave a complete approximate agreement protocol: send the current value, remove the $f$ largest and $f$ smallest values, and take the midpoint. Each round halves the span of the honest values. Starting in $[0,1]$, reaching span less than $1/n$ takes $O(\log n)$ rounds.

[Ben-Or, Dolev, and Hoch][bdh] improve this bound to $O(\log n / \log\log n)$. The core idea is to prevent the same Byzantine party from causing disagreement repeatedly. They use **[gradecast][dt-gc]**: parties relay what they heard and assign each sender a grade. If one honest party accepts a sender's value and another rejects it, every honest party **detects** that the sender is Byzantine and *ignores* its messages in later iterations.

We call this protocol **Grade, Detect, Average (GDA)**. It also replaces the trimmed midpoint with a trimmed **average**. The difference between two averages depends on how many senders caused disagreement in that iteration. Across all iterations, there are at most $f$ such senders. This reduces the round count to $O(\log n/\log\log n)$ for precision $1/n$, matching the deterministic round lower bound when $f=\Theta(n)$, even with [send omissions](/2026-10-19-approximate-agreement-send-omissions-lower-bound/).

## The result

There are $n>3f$ parties, of which at most $f$ are Byzantine. Channels identify senders; no digital signatures are needed. Communication takes place in lock-step synchronous rounds: every honest message sent in a round arrives before that round ends.

Each honest party starts with a rational input in $[0,1]$ and must output a rational value. Everyone knows the same parameter $0<\epsilon\le1$. As before, $G_r$ is the multiset of honest current values after iteration $r$, and

$$
\operatorname{span}(G_r)=\max(G_r)-\min(G_r).
$$

Here $r$ counts iterations, each containing three rounds. $G_0$ contains the honest inputs.

**Theorem.** In the synchronous model with $n>3f$ and at most $f$ Byzantine parties, GDA keeps every honest current value in the honest input range. After each completed iteration $r$,

$$
\operatorname{span}(G_r)
\le \operatorname{span}(G_0)
\left(\frac{f}{(n-2f)r}\right)^r.
$$

Let $R$ be the smallest positive integer with $R^R\ge1/\epsilon$. Every honest party decides after $3R$ rounds with honest output span strictly less than $\epsilon$.

## Gradecast in three rounds

In each gradecast instance, a designated sender $q$ sends a value. Every honest receiver outputs $(\mathit{value},\mathit{grade})$, where $\mathit{grade}\in\{0,1,2\}$ and $\mathit{value}=\bot$ when the grade is zero. The three-round protocol below first sends the designated sender's value, then applies the two rounds of our [graded consensus protocol][dt-gc].

For repeated gradecasts, party $i$ maintains a set $\mathrm{bad}_i$ of parties it has identified as Byzantine, initially empty. During an iteration, it ignores messages **from** parties in this set. The set remains fixed throughout all gradecast instances in that iteration. Parties may have different sets.

Even if $q\in\mathrm{bad}_i$, party $i$ still processes messages from parties outside $\mathrm{bad}_i$ in $q$'s gradecast instance.

```text
gradecast(r, q, v, bad), executed by party i:
    r: iteration number
    q: designated sender
    v: party i's current rational value
    bad: fixed set of ignored senders
    n: number of parties; f: fault bound, with n > 3f
    bot: no value

initialize a local table received[k][j] = bot
    for k = 1,2,3 and j = 1,...,n.

upon receiving <r, q, x> from party j in round k of this instance:
    if j not in bad and x is rational and received[k][j] = bot:
        received[k][j] := x

at the start of round 1:
    if i = q:
        received[1][i] := v
        send <r, q, v> to every other party

at the start of round 2:
    if received[1][q] != bot:
        x := received[1][q]
        received[2][i] := x
        send <r, q, x> to every other party

at the start of round 3:
    if received[2] contains the same rational value x
        from at least n-f distinct parties:
            received[3][i] := x
            send <r, q, x> to every other party

at the end of round 3:
    if received[3] contains the same rational value x
        from at least n-f distinct parties:
            output (x, 2)
    otherwise, if received[3] contains the same rational value x
        from at least f+1 distinct parties:
            output (x, 1)
    otherwise, output (bot, 0)
```

**Claim 1.** If every honest party's $\mathrm{bad}$ set contains only Byzantine parties, gradecast guarantees:

1. If sender $q$ is honest, every honest party outputs $q$'s value with grade two.
2. All honest outputs with positive grades have the same value.
3. If one honest party outputs grade two, every honest party outputs a positive grade.
4. If every honest party ignores $q$, every honest party outputs $(\bot,0)$.

**Proof.** If $q$ is honest, every honest party receives its value in round 1 and relays it in round 2. Every honest party therefore sees at least $n-f$ copies, sends that value in round 3, and outputs it with grade two.

No two honest parties can send different values in round 3. Otherwise, they must have received different values from two sets of at least $n-f$ senders in round 2. Those sets intersect in at least $n-2f>f$ parties, including an honest party. But each honest party sends at most one value in round 2. This is the Weak Agreement argument from the [earlier proof][dt-gc].

A positive grade requires $f+1$ senders in round 3, including an honest one. Since all honest round 3 messages contain the same value, all honest outputs with positive grades agree. If one honest party outputs grade two, at least $n-2f>f$ honest parties sent that value in round 3. Every honest receiver counts those messages and therefore outputs a positive grade.

These arguments still hold when parties ignore messages from Byzantine senders, because every honest message is still counted.

Finally, if every honest party ignores $q$, no honest party sends in round 2 of its instance. At most $f$ round 2 messages remain, so no honest party sends in round 3. The at most $f$ Byzantine messages in round 3 cannot give a positive grade.

## The protocol

Three changes to the previous protocol produce the faster convergence:

* **Gradecast** each current value, so honest outputs with positive grades for the same sender agree exactly.
* **Detect** senders with grade at most one and ignore their messages in later iterations.
* **Average** the retained values after trimming, so each differing entry has a bounded contribution.

If a sender gets grade zero at one honest party and a positive grade at another, Claim 1 rules out grade two at every honest party. Every honest party therefore adds the sender to $\mathrm{bad}$ and outputs $(\bot,0)$ for it in all later iterations.

A Byzantine sender can still make every honest party accept the same arbitrary value. This creates no differing entry. Trimming keeps the average within the honest range even when accepted Byzantine values lie outside it.

```text
grade_detect_average, executed by party i:
    input: rational value input in [0,1].
    parameters: n parties, fault bound f with n > 3f,
                common precision 0 < epsilon <= 1.

v := input
bad := {}
iterations := the smallest positive integer t with t^t >= 1/epsilon

for r = 1,...,iterations:
    in parallel for q = 1,...,n:
        run gradecast(r, q, v, bad) in rounds 3r-2, 3r-1, 3r
        store its output as (value[q], grade[q])

    at the end of round 3r:
        values := the multiset {value[1],...,value[n]}
        order bot below every rational value
        remove the f smallest and f largest entries from values
        v := sum(values)/(n-2f)
        bad := bad union {q : grade[q] <= 1}

decide v
```

All gradecast instances finish before $\mathrm{bad}_i$ changes. The next iteration uses the updated set.

**Claim 2.** No honest party is ever added to an honest party's $\mathrm{bad}$ set, and every honest current value after an iteration lies in the preceding honest range.

**Proof.** Initially the sets are empty. If they contain only Byzantine parties, Claim 1 gives every honest sender's value grade two at every honest receiver. Thus the update adds only Byzantine senders, proving the first statement by induction.

By Claim 1, each honest receiver's multiset contains every honest party's current value. At most $f$ entries are Byzantine values or $\bot$. Consequently, removing the $f$ smallest and $f$ largest entries leaves only values between $\min(G_{r-1})$ and $\max(G_{r-1})$. Every $\bot$ is removed. The average is rational and remains in this interval, proving the second statement.

In particular, repeated updates preserve the initial honest range.

## A Byzantine sender can cause disagreement only once

Let $b_r$ count the senders whose gradecast has grade zero at one honest party and a positive grade at another in iteration $r$. This is a quantity for the proof; parties do not compute it.

**Claim 3.** Each sender is counted at most once, and

$$
\sum_{r=1}^R b_r\le f.
$$

**Proof.** As observed above, every sender counted by $b_r$ is added to every honest party's $\mathrm{bad}$ set at the end of iteration $r$. Every honest party outputs $(\bot,0)$ for it in later iterations, so it cannot be counted again. Claim 2 says every such sender is Byzantine.

## How much can $b_r$ different entries change an average?

**Claim 4.** One iteration gives

$$
\operatorname{span}(G_r)
\le\frac{b_r}{n-2f}\operatorname{span}(G_{r-1}).
$$

**Proof.** Fix two honest receivers $i$ and $j$. Let $T_i$ and $T_j$ be the multisets they retain after trimming. Each contains $n-2f$ entries, and their updated values are

$$
v_i=\frac{\sum_{x\in T_i}x}{n-2f},
\qquad
v_j=\frac{\sum_{x\in T_j}x}{n-2f}.
$$

Before trimming, all honest receivers have the same entry for every sender not counted by $b_r$: either the same value with a positive grade, by Claim 1, or $\bot$ at every receiver. These give $n-b_r$ common entries.

For the proof, order entries by value, breaking ties by sender identity; this does not change either average. Among the common entries, remove the $f$ smallest and $f$ largest. The remaining $n-b_r-2f$ entries survive trimming at both receivers. Each has at least $f$ common entries before it, so it cannot be among either receiver's $f$ smallest entries. It also has at least $f$ common entries after it, so it cannot be among either receiver's $f$ largest entries.

Thus both $T_i$ and $T_j$ contain these $n-2f-b_r$ common entries. Cancel them when subtracting the two sums. Each sum now has

$$
(n-2f)-(n-2f-b_r)=b_r
$$

entries left.

Let $L=\min(G_{r-1})$ and $H=\max(G_{r-1})$. By Claim 2, every retained entry lies in $[L,H]$. Pair the remaining entries arbitrarily. Each pair differs by at most $H-L$, so

$$
\lvert v_i-v_j\rvert
\le\frac{b_r(H-L)}{n-2f}
=\frac{b_r}{n-2f}\operatorname{span}(G_{r-1}).
$$

This holds for every pair of honest receivers and proves the claim. If $b_r=0$, all entries cancel and the updated values coincide.

## Putting it together

**Claim 5.** GDA satisfies convex validity, approximate agreement, and termination after $3R$ rounds.

**Proof.** Claim 2 keeps every honest current value in the preceding honest range. Repeating this argument proves convex validity. Applying Claim 4 repeatedly gives

$$
\operatorname{span}(G_r)
\le\operatorname{span}(G_0)
\prod_{s=1}^r\frac{b_s}{n-2f}.
$$

The [arithmetic-geometric mean inequality](https://en.wikipedia.org/wiki/AM%E2%80%93GM_inequality) states that, for nonnegative numbers $a_1,\ldots,a_r$,

$$
\sqrt[r]{a_1\cdots a_r}
\le\frac{a_1+\cdots+a_r}{r}.
$$

Apply it to $b_1,\ldots,b_r$ and raise both sides to the $r$th power. Since these counts sum to at most $f$, by Claim 3,

$$
\begin{aligned}
\prod_{s=1}^r b_s
&\le\left(\frac{b_1+\cdots+b_r}{r}\right)^r\\
&\le\left(\frac fr\right)^r.
\end{aligned}
$$

Substituting proves the theorem's span bound, including when some $b_s$ is zero.

Since $\operatorname{span}(G_0)\le1$ and $f/(n-2f)<1$, our choice $R^R\ge1/\epsilon$ gives

$$
\operatorname{span}(G_R)
\le\frac1{R^R}\left(\frac{f}{n-2f}\right)^R
<\frac1{R^R}
\le\epsilon.
$$

Every honest party decides its current value at the end of iteration $R$, so this proves approximate agreement. Each iteration ends after three synchronous rounds, so every honest party decides after exactly $3R$ rounds.

For $\epsilon=1/n$, the stopping condition is simply $R^R\ge n$, or $R\log R\ge\log n$. The smallest such $R$ is $\Theta(\log n/\log\log n)$: writing $L=\log n$, a value of order $L/\log L$ has logarithm of order $\log L$, and their product is of order $L$. Hence the protocol uses $O(\log n/\log\log n)$ rounds.

## Notes

* Gradecast was introduced by [Feldman and Micali][fm]. This [DT post][dt-gradecast] presents several flavours of broadcast, including gradecast.
* The [omission approximate agreement protocol][omission-aa] uses the same counting argument: only parties that abort in an iteration can cause different accepted entries, and each party can abort only once.
* **Question.** Robust Midpoint sends $O(n^2)$ values per round, while this protocol sends $O(n^3)$. Can a deterministic approximate agreement protocol, with $n>3f$ and no signatures, reach honest output span less than $1/n$ in $O(\log n/\log\log n)$ rounds using $O(n^2)$ messages of $O(\log n)$ bits per round, for $O(\log n)$-bit inputs in $[0,1]$?

Your thoughts/comments on [X](https://x.com/ittaia/status/2112206481227387357).

[bdh]: https://arxiv.org/pdf/1007.1049#page=7
[fm]: https://doi.org/10.1145/62212.62225
[dt-gc]: https://decentralizedthoughts.github.io/2022-06-09-phase-king-via-gradecast/
[dt-gradecast]: https://decentralizedthoughts.github.io/2019-10-22-flavours-of-broadcast/#crusader-broadcast-and-gradecast
[omission-aa]: https://decentralizedthoughts.github.io/2026-10-18-approximate-agreement-with-omissions/
