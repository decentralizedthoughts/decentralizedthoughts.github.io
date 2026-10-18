---
title: "Approximate Agreement with Omissions: From Midpoints to Averages"
date: 2026-10-18 09:00:00 +03:00
tags:
  - approximate-agreement
author: Ittai Abraham
---

The [Byzantine approximate agreement posts][midpoint] start with a protocol that halves the span of honest values and [repeat it to obtain a complete protocol][complete]. The [Grade, Detect, Average post][gda] improves its convergence by identifying parties that cause disagreement. With omission failures, both arguments become simpler, and $n>2f$ parties suffice.

We first give a **Midpoint** protocol that halves the span in each round. We then add receipt reports: a party averages the reported values only if at least $n-f$ reports acknowledge its own value; otherwise it aborts. In this **Average or Abort** protocol, the averages of continuing parties can differ only in values from parties that abort in that iteration. Each party can abort only once. Following [Fekete's convergence argument][fekete], this gives a span below $k^{-k}$ after $k$ iterations, each taking two rounds. Reaching span less than $1/n$ therefore takes $O(\log n/\log\log n)$ rounds instead of $O(\log n)$.

## The problem

There are $n>2f$ parties. At most $f$ parties may suffer send omissions, receive omissions, or both; every party otherwise follows the protocol. Communication takes place in synchronous rounds. Each message either arrives in full in its round or is omitted. Channels identify senders. There are no digital signatures.

Every party starts with a rational input in $[0,1]$. Everyone knows the same parameter $0<\epsilon\leq1$. A party may **abort**, after which it stops participating and produces no output. We require:

* **Convex validity.** Every output lies between the smallest and largest initial inputs.
* **Approximate agreement.** Any two outputs differ by less than $\epsilon$, including outputs of parties with omissions.
* **Termination.** Every nonfaulty party decides and never aborts.

In this omission model, convex validity refers to the inputs of all parties. In the Byzantine model, it refers only to honest parties' inputs.

For each protocol, let $B_r$ be the set of parties that have aborted by the end of iteration $r$, and let $G_r=\{1,\ldots,n\}\setminus B_r$ be the set of parties that have not aborted. Initially, $B_0=\varnothing$ and $G_0=\{1,\ldots,n\}$. A party with omissions remains in $G_r$ until it aborts. These sets are used only in the proof; parties do not maintain them.

Let $X_r$ be the multiset of current values of parties in $G_r$, with $X_0$ containing all initial inputs. As before,

$$
\operatorname{span}(X_r)=\max(X_r)-\min(X_r).
$$

An iteration takes one round in Midpoint and two rounds in Average or Abort.

**Theorem.** With $n>2f$ and at most $f$ parties with send or receive omissions, both protocols preserve the initial input range, and no nonfaulty party aborts. After $k\geq1$ iterations, their spans satisfy

$$
\begin{aligned}
\text{Midpoint:}\qquad
\operatorname{span}(X_k)
&\leq 2^{-k}\operatorname{span}(X_0),\\
\text{Average or Abort:}\qquad
\operatorname{span}(X_k)
&\leq\left(\frac{f}{k(n-f)}\right)^k\operatorname{span}(X_0).
\end{aligned}
$$

Midpoint solves approximate agreement after $\lfloor\log_2(1/\epsilon)\rfloor+1$ rounds. Average or Abort does so after $2R$ rounds, where $R$ is the smallest positive integer with $R^R\geq1/\epsilon$.

## The Midpoint protocol: halving the span

At party $i$, `input` is its initial input, `v` is its current value, and `received` is a vector of $n$ entries indexed by sender. The symbol `bot` denotes a missing value. The multiset `V` contains the received values. Square brackets in a comprehension denote a multiset, so equal values from different senders remain separate entries.

```text
Set v = input.
Set R = floor(log2(1/epsilon)) + 1.

For r = 1,...,R:
    1. At the start of round r:
           Set received = [bot,...,bot].
           Set received[i] = v.
           Send <r, v> to every other party.

    2. Upon receiving <r, x> from j during round r:
           Set received[j] = x.

    3. At the end of round r:
           Set V = [received[j] : j in {1,...,n}, received[j] != bot].
           If |V| < n-f:
               Abort.
           Else:
               Set v = (min(V) + max(V)) / 2.
               If r = R:
                   Decide v.
```

**Claim 1.** No nonfaulty party aborts. Every update stays in the preceding range, and

$$
\operatorname{span}(X_r)\leq\frac{\operatorname{span}(X_{r-1})}{2}.
$$

**Proof.** Inductively, all nonfaulty parties enter the round and receive each other's values. There are at least $n-f$ of them, so each passes the check.

Let $V_i$ be the multiset used by a party that continues. Every entry belongs to $X_{r-1}$. Also, $\lvert V_i\rvert\geq n-f>n/2$, so $V_i$ contains more than half of the entries of $X_{r-1}$. Its interval therefore contains the median of $X_{r-1}$:

$$
\min(X_{r-1})\leq\min(V_i)
\leq\operatorname{median}(X_{r-1})
\leq\max(V_i)\leq\max(X_{r-1}).
$$

Adding the bounds on $\min(V_i)$ and $\max(V_i)$ and dividing by two places every new value in

$$
\left[
\frac{\min(X_{r-1})+\operatorname{median}(X_{r-1})}{2},
\frac{\operatorname{median}(X_{r-1})+\max(X_{r-1})}{2}
\right].
$$

This interval lies in the preceding range and has half its width. This is the same median argument as in the [Byzantine protocol][midpoint], with no trimming needed.

## The Average or Abort protocol: faster convergence

At party $i$, `input`, `v`, `received`, and `bot` have the same meanings as in Midpoint. Each iteration takes two rounds. Parties first send their current values, then report the vectors they received.

At the end of the second round, party $i$ counts the reports it received that contain its current value in the entry for sender $i$, including its own report. If fewer than $n-f$ reports contain this entry, $i$ must **abort**: it stops participating and produces no output. Otherwise, it averages the values appearing in the reports, counting each original sender once. Thus receiving enough reports is not sufficient; enough of them must acknowledge $i$'s value.

The **abort** rule is critical to the faster convergence bound. It ensures that a party that continues has its current value included in every continuing party's average. Only values from parties that abort in this iteration can appear in some averages and not others. Each party can abort only once, and at most $f$ parties abort in total. As we prove below, this limits the differences between averages by the number of new aborts in each iteration, giving the product bound that leads to $O(\log n/\log\log n)$ rounds for $\epsilon=1/n$.

The vector `report` has $n$ entries indexed by reporter: `report[k]` is the vector reported by party $k$, or `bot` if its report is missing. In the pseudocode, `q` denotes a report vector, `j` an original sender, and `k` a reporter. The variable `acks` counts reports containing $i$'s value. The set `U` contains pairs `(j, x)` of an original sender and its reported value; `V` is the multiset of their values.

The set `U` removes repeated reports of the same sender. Its entries for that sender agree because omissions cannot change message contents. The multiset `V` retains equal values from different senders.

```text
Set v = input.
Set R = min {k in {1,2,...} : k^k >= 1/epsilon}.

For r = 1,...,R:
    1. At the start of round 2r-1:
           Set received = [bot,...,bot].
           Set received[i] = v.
           Send <r, v> to every other party.

    2. Upon receiving <r, x> from j during round 2r-1:
           Set received[j] = x.

    3. At the start of round 2r:
           Set report = [bot,...,bot].
           Set report[i] = received.
           Send <r, received> to every other party.

    4. Upon receiving <r, q> from k during round 2r:
           Set report[k] = q.

    5. At the end of round 2r:
           Set acks = |{k in {1,...,n} :
                        report[k] != bot and report[k][i] != bot}|.
           If acks < n-f:
               Abort.
           Else:
               Set U = {(j, report[k][j]) : k,j in {1,...,n},
                        report[k] != bot and report[k][j] != bot}.
               Set V = [x : (j, x) in U].
               Set v = average(V).
               If r = R:
                   Decide v.
```

## Only new aborts can cause different averages

In Midpoint, the same party can omit messages in every round. In Average or Abort, the report check makes every continuing party's value appear in every continuing party's update. Only values from parties that abort now can appear in some averages and not others.

**Claim 2.** No nonfaulty party aborts. In iteration $r$, every party in $G_r$ includes in its average the previous value of every party in $G_r$, and no value from a party in $B_{r-1}$.

**Proof.** Inductively, every nonfaulty party receives every nonfaulty sender's value and reports it. Each nonfaulty sender receives these at least $n-f$ reports and passes its check.

Now fix parties $i$ and $j$ that both continue. Party $j$ received at least $n-f$ reports containing its value. Party $i$ received at least $n-f$ reports, since it passed its own check. These two sets of reporters intersect, because

$$
(n-f)+(n-f)-n=n-2f>0.
$$

A reporter in the intersection sent the same vector to both parties. Its report to $i$ therefore contains $j$'s value, which $i$ includes in its average.

A party that aborted earlier sends no value in this iteration, so no report can contain a value from it.

Let $b_r=\lvert B_r\setminus B_{r-1}\rvert$ be the number of parties that abort in iteration $r$. There are $\lvert G_{r-1}\rvert$ parties entering the iteration and $\lvert G_r\rvert$ continuing afterward, so $b_r=\lvert G_{r-1}\rvert-\lvert G_r\rvert$. By Claim 2, the multisets being averaged can differ only on values from parties in $B_r\setminus B_{r-1}$. Aborts are permanent, so $B_{r-1}\subseteq B_r$. Only faulty parties abort, hence

$$
\sum_{r=1}^k b_r=\lvert B_k\rvert\leq f.
$$

**Claim 3.** Every update stays in the preceding range, and

$$
\operatorname{span}(X_r)
\leq\frac{b_r}{\lvert G_{r-1}\rvert}\operatorname{span}(X_{r-1}).
$$

**Proof.** Let $L=\min(X_{r-1})$, $H=\max(X_{r-1})$, and $D=H-L$. Every reported value lies in $[L,H]$, so every average also lies in this interval. This proves range preservation.

Now consider two continuing parties with accepted multisets $V_i,V_j$ and new values

$$
\mu_i=\operatorname{average}(V_i),
\qquad
\mu_j=\operatorname{average}(V_j).
$$

Assume $\lvert V_i\rvert\leq \lvert V_j\rvert$, and write $m=\lvert V_j\rvert$.

The two averages may have different denominators. To compare them, pad $V_i$ with $m-\lvert V_i\rvert$ copies of $\mu_i$. This does not change its average:

$$
\frac{\sum_{x\in V_i}x+(m-\lvert V_i\rvert)\mu_i}{m}
=\frac{\lvert V_i\rvert\mu_i+(m-\lvert V_i\rvert)\mu_i}{m}
=\mu_i.
$$

The added values also lie in $[L,H]$.

By Claim 2, both multisets contain the previous value of every party in $G_r$. Cancel these $\lvert G_r\rvert$ common entries when subtracting the two sums. Each multiset now has $m-\lvert G_r\rvert$ entries left. Pair them arbitrarily. Each pair differs by at most $D$, so

$$
\lvert \mu_i-\mu_j\rvert
\leq \frac{m-\lvert G_r\rvert}{m}\,D.
$$

Each accepted multiset contains at most one value per party entering the iteration, so $m\leq \lvert G_{r-1}\rvert$. Therefore,

$$
\frac{m-\lvert G_r\rvert}{m}
=1-\frac{\lvert G_r\rvert}{m}
\leq 1-\frac{\lvert G_r\rvert}{\lvert G_{r-1}\rvert}
=\frac{b_r}{\lvert G_{r-1}\rvert}.
$$

Applying this bound to every pair of continuing parties gives

$$
\operatorname{span}(X_r)
\leq \frac{b_r}{\lvert G_{r-1}\rvert}\operatorname{span}(X_{r-1}).
$$

In particular, if no party aborts in this iteration, then $b_r=0$: every continuing party averages exactly the same values, and their new values coincide.

## Putting it together

**Claim 4.** Both protocols satisfy convex validity, approximate agreement, and termination with the stated stopping rules.

**Proof.** Claims 1 and 3 keep every update in the preceding range, and hence in the initial input range. All values remain rational. Claims 1 and 2 show that nonfaulty parties never abort. Every continuing party decides after the prescribed number of synchronous rounds.

For Midpoint, Claim 1 gives

$$
\operatorname{span}(X_R)\leq2^{-R}\operatorname{span}(X_0)
\leq2^{-R}<\epsilon.
$$

For Average or Abort, at least $n-f$ parties continue in every iteration. Iterating Claim 3 gives

$$
\begin{aligned}
\operatorname{span}(X_k)
&\leq\operatorname{span}(X_0)
\prod_{r=1}^k\frac{b_r}{\lvert G_{r-1}\rvert}\\
&\leq\frac{\operatorname{span}(X_0)}{(n-f)^k}
\prod_{r=1}^k b_r.
\end{aligned}
$$

Recall the [arithmetic-geometric mean inequality][am-gm] (AM–GM): for nonnegative numbers $a_1,\ldots,a_k$,

$$
\sqrt[k]{a_1\cdots a_k}
\leq\frac{a_1+\cdots+a_k}{k}.
$$

Apply it to the abort counts $b_1,\ldots,b_k$ and raise both sides to the $k$th power. Since $b_1+\cdots+b_k=\lvert B_k\rvert\leq f$,

$$
\prod_{r=1}^k b_r
\leq\left(\frac{b_1+\cdots+b_k}{k}\right)^k
\leq\left(\frac{f}{k}\right)^k.
$$

Combining these bounds gives

$$
\operatorname{span}(X_k)
\leq\operatorname{span}(X_0)
\left(\frac{f}{k(n-f)}\right)^k.
$$

Since $\operatorname{span}(X_0)\leq1$ and $f<n-f$, choosing $R^R\geq1/\epsilon$ gives

$$
\operatorname{span}(X_R)
\leq\left(\frac{f}{n-f}\right)^R\frac1{R^R}
<\frac1{R^R}\leq\epsilon.
$$

For $\epsilon=1/n$, the condition is $R\log R\geq\log n$. The smallest such $R$ is $\Theta(\log n/\log\log n)$, so $2R$ rounds give the claimed improvement.

## Notes

* [Fekete][fekete] gave asymptotically optimal approximate agreement protocols for omissions, using detection to bound convergence by a product of new failures. The receipt report protocol here has a direct proof of this convergence rate. A later post (TBD) will give the matching $\Omega(\log n/\log\log n)$ worst-case round lower bound for deterministic protocols when $\epsilon=1/n$ and $f=\Theta(n)$, even with send omissions alone.
* This is another example of detection helping agreement. Here a party detects that too few reports acknowledge its value and aborts. In the [faster Byzantine protocol][gda], parties use gradecast to identify senders that cause different receivers to accept different entries.
* **Communication cost.** Assuming each rational value fits in one word, Midpoint sends $O(n^2)$ words per iteration, while Average or Abort sends $O(n^3)$ words. Both send $O(n^2)$ messages per iteration, but each second-round message in Average or Abort contains a vector of $n$ values. Its faster convergence therefore comes at the cost of a factor of $n$ more communication per iteration.
* Future omission clock synchronization posts will apply these two ideas to clock measurements: interval midpoints (TBD) and acknowledged averages (TBD). Their additional arguments will account for delay uncertainty and clocks updating at different times.

[midpoint]: https://decentralizedthoughts.github.io/2022-06-07-approx-agreement-one/
[complete]: https://decentralizedthoughts.github.io/2026-10-17-approximate-agreement-complete-protocol/
[fekete]: https://groups.csail.mit.edu/tds/papers/Fekete/DistComp90.pdf
[am-gm]: https://en.wikipedia.org/wiki/AM%E2%80%93GM_inequality

[gda]: /2026-10-18-byzantine-approximate-agreement-grade-detect-average/
