---
title: Synchronized Clocks, Fixed View Schedules, and Simultaneous Agreement
date: 2026-03-08 00:59:27 -05:00
tags:
- consensus
- lowerbound
author: Ittai Abraham
unlisted: true
sitemap: false
---

Most modern blockchain protocols use [partial synchrony](https://decentralizedthoughts.github.io/2019-06-01-2019-5-31-models/) based BFT protocols that proceed in views. Each view has a designated leader. This naturally leads to the following design question:

> How should parties synchronize the transition from view $i$ to view $i+1$?

[Dwork, Lynch, Stockmeyer, *Consensus in the Presence of Partial Synchrony*](https://groups.csail.mit.edu/tds/papers/Lynch/jacm88.pdf) considered two models: one with synchronized clocks, and one with unbounded clock drift pre-GST. We argue that the former is a natural fit for most modern systems:

* servers have access to reasonably good local clocks, under a conservative $15$ [ppm](https://en.wikipedia.org/wiki/Parts-per_notation) drift bound, the worst case drift over 60 seconds is at most $15 \cdot 10^{-6}\cdot 60 = 900\ \mu s < 1\ \text{ms}$;
* there are well-established protocols for keeping clocks synchronized (NTP/PTP), and modern NTP security has improved via NTS ([RFC 8915](https://www.rfc-editor.org/info/rfc8915)), with updated authentication guidance ([RFC 8573](https://www.rfc-editor.org/info/rfc8573));
* modern cloud providers offer additional synchronization services and measurements (for example, [AWS](https://aws.amazon.com/blogs/compute/its-about-time-microsecond-accurate-clocks-on-amazon-ec2-instances/) and [Meta](https://engineering.fb.com/2022/11/21/production-engineering/precision-time-protocol-at-meta/)).

Given this, assuming clock synchronization is very reasonable and opens two approaches to view synchronization:

1. **Fixed View Schedule (FVS)**

    In an FVS design, the start and end times of view $i$ are fixed in advance.

    *Pros*:
      - parties are tightly synchronized on view boundaries;
      - view synchronization is straightforward to implement and reason about.

    *Cons*:
      - view length is fixed to accommodate worst-case events, which can lead to unnecessarily long good-case view latency.

2. **Optimistic Responsiveness (OR)**

    In an optimistically responsive design (see [What is Responsiveness?](https://decentralizedthoughts.github.io/2022-12-18-what-is-responsiveness/) and [Optimistic Responsiveness](https://decentralizedthoughts.github.io/2020-06-12-optimal-optimistic-responsiveness/)), good-case views complete as quickly as the network allows.

    *Pros*:
      - good-case view latency can be $O(\delta)$ and commit time as small as $3\delta$ (for optimal resilience, see [here](https://decentralizedthoughts.github.io/2025-11-22-three-round-BFT/)). Even in synchrony, these protocols can have $O(\delta)$ good-case view latency (see [here](https://decentralizedthoughts.github.io/2021-12-07-good-case-latency-of-rotating-leader-synchronous-bft/)).
  
    *Cons*:
      - parties may begin views with a gap of up to $\Delta$ (the maximum message delay);
      - this gap increases timeout timers, which in turn increases worst-case view latency.


## The cryptoeconomic angle

The leader of a view has temporary monopoly power over what to propose and when to propose. Waiting close to the maximum allowed time is a strict best response, because more transactions and fees may arrive, and there is more time to construct a block with higher MEV opportunities. This means that even if a protocol allows faster good-case views, incentives may still push behavior toward the maximal view length. 

So fixed schedules are a very reasonable design choice, but can we still get good-case speedups with a fixed view schedule?

## Fixed schedules with good-case speedups imply simultaneous agreement


This leads to the next question:

> Can we have a fixed view schedule (all parties agree to start the next view at the same time) that also allows for good-case speedups (start the next view early in the good-case)?


A natural idea is the following:

1. use a fixed schedule default (say $4\Delta$ per view),
2. if the previous view commits early in the good case (say around $3\delta \ll 3\Delta$), then jointly switch the next view to an earlier start time of say $X<4\Delta$.

However, this is effectively solving the following problem:

> all non-faulty parties must not only agree on the same next-view start time, but also agree on this before time $X$.

This is no longer a classic agreement problem, as it introduces a timing constraint. This is called **simultaneous agreement** in the literature, and it is strictly harder than standard agreement.


## Simultaneous agreement


**Classic lower bound**: for up to $t$ crashes, any protocol solving agreement has an execution that requires at least $t+1$ rounds (see [Synchrony Uncommitted Lower Bound](https://decentralizedthoughts.github.io/2019-12-15-synchrony-uncommitted-lower-bound/) and [Early Stopping Lower Bounds](https://decentralizedthoughts.github.io/2024-01-28-early-stopping-lower-bounds/)).

*Simultaneous agreement with time $X$* (for a fixed parameter $X$) requires that in addition to being a standard agreement protocol, there is no execution in which some correct party decides at or before $X$ and some correct party decides after $X$.

**Theorem**  
For up to $t$ crashes, any protocol solving simultaneous agreement with time $X$ that has some execution that decides at or before $X$ must have $X \ge t+1$.


## Proof

Given a protocol $P$, define protocol $P'$ as follows: each party runs $P$, and when it decides in $P$ at round $r$, it outputs 0 iff $r \le X$, and outputs 1 otherwise. Seek a contradiction, and assume $X < t+1$ and there exists an execution in which $P'$ decides 0.

From simultaneous agreement with time $X$ of $P$, protocol $P'$ has agreement: in every execution, all correct parties are on the same side of threshold $X$. From termination of $P$, protocol $P'$ has termination.

There are three cases:

1. If $P'$ always decides 0, then $P$ (not $P'$) violates the classic $t+1$ lower bound as a consensus protocol. So this cannot be the case.
2. If $P'$ always decides 1, this is a contradiction to the assumption above.  
3. So there is an initial configuration and adversary strategy that lead $P'$ to decision 0, and an initial configuration and adversary strategy that lead $P'$ to decision 1.
    * Therefore, $P'$ has a bivalent initial configuration (otherwise, if all initial configurations were univalent for some bit $b$, then $P'$ would always decide $b$; and if some were univalent for $b$ and others for $1-b$, standard adjacency arguments imply the existence of a bivalent initial configuration).
    * By the standard synchronous crash valency argument (as in the uncommitted/early-stopping lower-bound arguments cited above), there exists an execution with at most $t$ crashes that starts from this bivalent initial configuration and reaches a bivalent configuration at the end of round $t$. From that configuration, there is an admissible continuation in which decision value 0 is reached only after round $t$ (that is, at round $t+1$ or later). Since $X < t+1$, this decision occurs strictly after time $X$, contradicting the definition of $P'$ (output 0 iff decision is by round $X$). This is a contradiction.



## Conclusion

It seems that fixed view schedules are incompatible with good-case speedups; at least the natural approach of simultaneous switching to an earlier start time in the next view if the previous view commits early in the good case is not possible. Obtaining view synchronization that benefits from the best of both worlds (fixed schedules and optimistic responsiveness) is an interesting open question.



### Notes

Simultaneous agreement was studied extensively in the 1980s and 1990s:

* [Dolev, Reischuk, Strong, *Early Stopping in Byzantine Agreement*](https://dl.acm.org/doi/pdf/10.1145/96559.96565)
* [Coan, Dwork, *Simultaneity Is Harder than Agreement*](https://www.sciencedirect.com/science/article/pii/089054019190067C)
* [Dwork, Moses, *Knowledge and common knowledge in a Byzantine environment: Crash failures*](https://www.sciencedirect.com/science/article/pii/0890540190900149/pdfft?isDTMRedir=true)
* [Moses, Raynal, *Revisiting simultaneous consensus with crash failures*](https://www.sciencedirect.com/science/article/pii/S0743731509000045/pdfft?isDTMRedir=true)




### Acknowledgements

We would like to thank Gilad Stern, Karthik Nayak, Nusret Tas, Joachim Neu, and Pranav Garimidi for helpful discussions and feedback on this post.

---

Please leave [comments on X]().
