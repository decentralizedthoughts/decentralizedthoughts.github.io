---
title: Optimal Clock Synchronization When There Are No Failures or Drift
date: 2026-10-13 04:17:27 -05:00
tags:
  - clock-synchronization
  - lowerbound
author: Ittai Abraham, Jennifer Welch
---

Synchronized clocks help servers coordinate. For example, servers with synchronized clocks following the same schedule can switch leaders at nearly the same time.

A natural approach is for servers to exchange their current clock values and take the average. But messages take time to arrive. By the time a server receives another server’s clock value, that clock has already advanced. If the delay were known, the receiver could account for it. The difficulty is that the delay is usually uncertain. We assume every message takes between $d-u$ and $d$ units of time, where $d$ is the maximum delay and $u$ is the width of the uncertainty interval. Synchronizing clocks despite this uncertainty is the central challenge of this post.


The lower bound of $d-u$ can be thought of as modeling the limits of the speed of light, while the upper bound of $d$ captures our modeling of the maximal additional latency due to switching and routing costs. For illustration, take $d=100$ milliseconds and $u=5$ milliseconds, so messages take between $95$ and $100$ milliseconds.

How closely can we synchronize clocks despite this uncertainty? This series starts with the simplest case: everyone follows the protocol, and every clock runs at exactly the correct rate. Later posts add Byzantine failures, clock drift, and periods when messages take longer than $d$.

This post is based on the protocol and matching lower bound of [Lundelius and Lynch 1984](https://groups.csail.mit.edu/tds/papers/Lynch/ic84.pdf).

## The model

There are $n$ parties with no failures. Every party has a direct, reliable channel to every other party. 

**Hardware clocks.** At real time $t$, party $i$ can read

$$
H_i(t)=t+h_i,
$$

where $h_i$ is its arbitrary, unknown hardware offset. Thus clocks may disagree about the time, but all advance at the same rate. Party $i$ can read $H_i$ but cannot change it or observe real time $t$. 

**Communication.** The parties know two parameters, $0\leq u\leq d$. Every message takes between $d-u$ and $d$ units of real time from sending to receipt. 

**Startup.** Every party eventually starts, the first local wakeup or message arrival starts the protocol.


## What does synchronization require?

We want the parties' clocks to show nearly the same time. The **skew** is the largest difference between two parties’ clocks at the same real time.


Party $i$ cannot change $H_i$, but it can add a correction $a_i$. The resulting *logical* clock is

$$
C_i(t)=H_i(t)+a_i.
$$

Each party must eventually output its correction and keep it fixed. $C_i$ continues at the same rate as $H_i$.

Formally, the **skew** at real time $t$ is

$$
\operatorname{skew}(t)=\max_i C_i(t)-\min_i C_i(t).
$$

Note that once adjustments $a_1,\ldots,a_n$ are fixed, $\operatorname{skew}(t)=\max_i (h_i+a_i) -\min_i (h_i+a_i)$ without a dependence on $t$.


**Theorem (Lundelius and Lynch, 1984).** For $n$ parties, with no failures, no clock drifts, and delays in $[d-u,d]$, there is a protocol that terminates after one message exchange and guarantees adjustments $a_1,\ldots,a_n$ such that

$$
\boxed{\operatorname{skew}\leq u\left(1-\frac1n\right).}
$$

Moreover, no protocol can guarantee a smaller bound, regardless of how many messages it exchanges.




## What one message tells us


Consider party $i$ receiving a message from party $j$. Let $\ell \in [d-u,d]$ be the actual message delay. In order for party $i$ to choose its correction $a_i$, it needs to estimate the gap $H_j(t)-H_i(t) = h_j-h_i$.

Suppose $j$ sends at real time $t$, so it sends $s=H_j(t)$. When the message arrives at time $t+\ell$, $i$'s hardware clock is at $r=H_i(t+\ell)$. Therefore



$$
r-s = H_i(t+\ell)-H_j(t)= \ell+h_i-h_j.
$$

The receiver cannot tell how much of $r-s$ comes from the message delay ($\ell$) and how much comes from the clocks disagreeing ($h_i-h_j$).

Since $d-u\leq\ell\leq d$, the message places the clock difference in the interval

$$
h_j-h_i \in [d-u-(r-s),\; d-(r-s)].
$$

Let $m$ be the midpoint of this interval:

$$
m=(d-u/2)-(r-s).
$$

**Claim 1.** For every real time $t$,

$$
|m-(H_j(t)-H_i(t))|\leq u/2.
$$

**Proof.** Since $r-s=\ell+h_i-h_j$ and $H_j(t)-H_i(t)=h_j-h_i$,

$$
m-(H_j(t)-H_i(t))=(d-u/2)-\ell\in[-u/2,u/2].
$$

Setting $a_i=m$ therefore gives $|C_i(t+\ell)-H_j(t+\ell)|\leq u/2$ at receipt.


![Suppose the sender sends s=1000 and the receiver observes r=1098, with message delay between 95 and 100 milliseconds. The observed difference is r-s=98. The clock difference lies in [95-98,100-98]=[-3,2], so the midpoint correction is m=97.5-98=-0.5. The corrected clock is 1097.5, within 2.5 milliseconds of the sender’s hardware clock at receipt.](/img/clock-sync-no-drift-midpoint.png)



*Suppose $s=1000$, $r=1098$, and the delay is between $95$ and $100$ milliseconds. Then $r-s=98$, so the correction is $m=97.5-98=-0.5$.*

## The protocol

The above discussion shows that the best we can do from one message is to estimate it based on its midpoint delay $d-u/2$. So the natural thing to do is simply to take an average of all these estimates.

Each party maintains a local list `estimate` that starts with `{0}`, since its own clock difference is exactly zero.

```text
1. On startup:
    Send H_i(t) to every other party.

2. Upon receiving s_j from j != i:
    Add (d - u/2) - (H_i(t) - s_j) to estimate.
    If |estimate| = n:
        Set a_i = sum(estimate)/n.
```

All parties eventually send, and every message is delivered, so all parties finish. 

**Claim 2.** After every party has set its correction,

$$
\operatorname{skew}(t)\leq u\left(1-\frac1n\right).
$$

**Proof.** Fix any such time $t$. By Claim 1, the entry for each $j\ne i$ in party $i$'s list `estimate` differs from $H_j(t)-H_i(t)$ by at most $u/2$. The entry for $j=i$ is exact. Since $a_i$ is the average of these $n$ entries,

$$
\begin{aligned}
\left|C_i(t)-\frac1n\sum_{j=1}^n H_j(t)\right|
&=\left|a_i-\frac1n\sum_{j=1}^n\bigl(H_j(t)-H_i(t)\bigr)\right|\\
&=\frac1n\left|\operatorname{sum}(\texttt{estimate})-\sum_{j=1}^n\bigl(H_j(t)-H_i(t)\bigr)\right|\\
&\leq\frac1n\cdot0+\frac1n(n-1)\frac u2\\
&=\frac{(n-1)u}{2n}.
\end{aligned}
$$

Every corrected clock is within $(n-1)u/(2n)$ of the same average $\frac1n\sum_{j=1}^n H_j(t)$. Any two are therefore at most $(n-1)u/n$ apart.

## Why no protocol can do better

Fix any protocol that eventually sets its corrections.

### The base world

In world $W_0$, every party has $h_i=0$, so $H_i(t)=t$. All parties start at real time $u$. A message from party $i$ to party $j$ takes $d-u$ time if $i<j$, and $d$ time if $i>j$.

Run the protocol in this world, and let $a_i$ be party $i$'s final correction. After it finishes, $C_i(t)=t+a_i$.

### The shifted worlds

For each $k=1,\ldots,n-1$, construct world $W_k$ by moving every event of parties $1,\ldots,k$ earlier by $u$ and increasing their hardware offsets to $u$. Leave the other parties unchanged.

We will now show that every party sees exactly the same messages, in the same order, and the same values of $H_i$ at every event in each of the worlds. This means that worlds are *indistinguishable*. Thus each party $i$ must choose the same correction $a_i$ in every world.

**Claim 3.** Each shifted world obeys the model and is indistinguishable from $W_0$ to every party.

**Proof.** Shifted parties start at time $0$; the others start at time $u$. A message from a shifted party to an unchanged party now takes $(d-u)+u=d$ time. In the reverse direction, it takes $d-u$ time. All other message delays are unchanged.

For a shifted party, an event at real time $t$ now occurs at $t-u$, but its hardware clock still equals

$$
H_i(t-u)=(t-u)+u=t.
$$

Each party therefore sees the same messages, in the same order, and the same values of $H_i$ at every event in each of the worlds. Hence party $i$ must choose the same correction $a_i$ in every world.

![Two sample messages between parties i and j, where i is in the shifted prefix and j is outside it. In Wk, i sends and receives u earlier and has hardware offset u. The channel delays exchange d-u and d, while every corresponding event has the same hardware clock value as in W0.](/img/clock-sync-no-drift-shift.png)

*The shift preserves each party's hardware clock value at every event.*

**Claim 4.** At least one of $W_0,\ldots,W_{n-1}$ has final skew at least $u(1-1/n)$.

**Proof.** Compare clocks at a real time $t$ after all parties have finished in all these worlds. In $W_0$,

$$
C_n(t)-C_1(t)=a_n-a_1.
$$

In each $W_k$, party $k$ has hardware offset $u$, while party $k+1$ has hardware offset $0$. By Claim 3, their corrections remain $a_k$ and $a_{k+1}$, so

$$
C_k(t)-C_{k+1}(t)=a_k+u-a_{k+1}.
$$

Take one clock difference from each world:

$$
\begin{aligned}
&\underbrace{C_n(t)-C_1(t)}_{W_0}
+\underbrace{C_1(t)-C_2(t)}_{W_1}
+\cdots+
\underbrace{C_{n-1}(t)-C_n(t)}_{W_{n-1}}\\
&\quad=(a_n-a_1)+(a_1+u-a_2)+\cdots+(a_{n-1}+u-a_n)\\
&\quad=(n-1)u.
\end{aligned}
$$

These are $n$ clock differences whose sum is $(n-1)u$. Therefore, one difference is at least $(n-1)u/n$, and the skew in its world is at least that large.

## Notes

* **Different channel delays**: The same tight bound holds if the channel from $j$ to $i$ has known delay bounds $[d_{ij}-u,d_{ij}]$ with $d_{ij}\geq u$. Use $d_{ij}$ instead of $d$ when computing its estimate. Claim 1 still gives error at most $u/2$, so Claim 2 gives the same skew bound. For the lower bound, assign each channel its lower or upper delay using the same index order. The shifts exchange the two endpoints on channels between shifted and unchanged parties.

* **Another proof of Claim 2.** After all corrections are set, compare $C_i(t)$ and $C_j(t)$ for $i\ne j$. Expanding their corrections cancels the true clock differences. By Claim 1, $i$'s estimate of $H_j(t)-H_i(t)$ and $j$'s estimate of $H_i(t)-H_j(t)$ each contribute error at most $u/2$. For each other party $k$, both $i$ and $j$ estimate their clock difference from $k$. By Claim 1, each estimate has error at most $u/2$, so the difference between these errors is at most $u$ in magnitude. The $n-2$ other parties therefore contribute at most $(n-2)u$. Thus

    $$
    |C_i(t)-C_j(t)|
    \leq\frac1n\left(\frac u2+\frac u2+(n-2)u\right)
    =u\left(1-\frac1n\right).
    $$

* **Lower bounds**: Our [lower bounds chapter](https://decentralizedthoughts.github.io/2026-06-28-chapter-lower-bounds/) collects more results and proof techniques. For more on indistinguishability, see our [post on Byzantine agreement under partial synchrony](https://decentralizedthoughts.github.io/2019-06-25-on-the-impossibility-of-byzantine-agreement-for-n-equals-3f-in-partial-synchrony/).

* **Tolerating failures**:  The [next post](TBD) adds Byzantine failures, still with no clock drift.

Your thoughts on [X](TBD)
