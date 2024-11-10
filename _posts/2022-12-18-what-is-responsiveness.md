---
title: What is Responsiveness?
date: 2022-12-18 04:00:00 -05:00
tags:
- dist101
author: Ittai Abraham and Kartik Nayak
---

In asynchronous protocols, latency to commit is a function of the actual maximum network delay $\delta$. In synchronous protocols, message delay is bounded by $\Delta$, and for $n/3 \leq f < n/2$, the $\Delta$ bound is used to obtain both safety and liveness. In partial synchrony, message delay is bounded by $\Delta$ after GST, and the $\Delta$ bound is used to obtain liveness.


What if the *actual* network delay $\delta$ in an execution is much smaller than the maximum delay $\Delta$? Can a protocol provide bounds that are a function of $O(\delta)$ instead of $O(\Delta)$? This type of performance is called “responsiveness” and sometimes "network speed" because it guarantees progress as fast as the actual network delays allow.  


Here is a definition of a responsive execution:

>  **Responsive execution** [[Attiya, Dwork, Lynch, Stockmeyer 1991](https://groups.csail.mit.edu/tds/papers/Lynch/stoc91.pdf)], [[Hertzberg, Kutten, 2000](https://www.researchgate.net/publication/220618470_Early_Detection_of_Message_Forwarding_Faults)], [[Pass, Shi, 2016](https://eprint.iacr.org/2016/917.pdf)]: an execution is *responsive* if the total latency is only a function of the actual network delays, i.e., if the actual network delays are at most $\delta$, the total latency is $O(\delta)$.

For partial synchrony it is natural to define an eventually responsive execution:

> **Eventual responsive execution**: an execution is eventually responsive if for any time $T$, such that from time $T$ and onward the network delays are at most $\delta$, then the completion time is at most $T+O(\delta)$.


Can we obtain responsiveness for every execution of consensus in the synchronous and partially synchronous models? In general, no! As we have [seen](https://decentralizedthoughts.github.io/2019-12-15-synchrony-uncommitted-lower-bound/), in the worst case, even one single-shot consensus can take $O(f \Delta)$ time even if the actual network delays are $\delta \ll \Delta$. Pass and Shi ask the following natural question:

> Under what conditions can a consensus protocol be responsive?
> -- [Pass and Shi, 2017](https://eprint.iacr.org/2017/913.pdf)

#### Intuition for deriving conditions for responsiveness in broadcast protocols


*First condition*: when considering a broadcast protocol, the sender/leader in the broadcast needs to be non-faulty; otherwise, trivially, a faulty party would not send the message within the bounded delay $\Delta$ causing the latency to be $> \Delta$. 

*Second condition*: The bane of responsiveness in the Byzantine model is the *split brain attack* where one party commits to $v$ and another party commits to $v' \neq v$.

To avoid this attack, a responsive commit strategy needs to hear from a majority of honest parties. So at least $>f+ (n-f)/2 = (n+f)/2$ parties, where $f$ denotes the number of Byzantine parties.

This quorum size ensures that the condition cannot be satisfied for two non-faulty parties: while the $f$ Byzantine parties may potentially equivocate with the two non-faulty parties, only one of the two honest parties would have the honest majority $> (n+f)/2$. Consequently, in an execution with responsiveness, the number of non-faulty parties in the system $n-t$ needs to be at least $> (n+f)/2$ where $t\le f$ is the actual number of failures in the execution.


#### Responsive broadcast protocols: worst case resilience and conditions for responsiveness

It turns out that these two conditions are sufficient! There exist responsive protocols requiring only these two conditions to be met. Here are some examples:



| Worst Case Resilience                    | Responsiveness Condition        | Protocol                                                                                                                                             |
| ---------------------------------------- | ------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| $f<n/2$ Omission faults                  | non-faulty leader               | Paxos                                                                                                                                                |
| $f<n/3$ Byzantine faults                 | non-faulty leader               | [PBFT](https://pmg.csail.mit.edu/papers/osdi99.pdf), [SBFT](https://arxiv.org/abs/1804.01626), [HotStuff](https://arxiv.org/pdf/1803.05069.pdf), etc |
| $f<n/2$ Byzantine faults under synchrony | non-faulty leader and $t < n/4$ | [PS'17](https://eprint.iacr.org/2017/913.pdf), [ANRS'21](https://eprint.iacr.org/2020/458.pdf),    [ANS'22](https://eprint.iacr.org/2021/1138.pdf)   |


In words, omission failure resilient protocols can be responsive in executions where the leader is non-faulty. Byzantine failure resilient protocols, in addition, require $n-t > (n+f)/2$ where $f$ is the maximum number of faults and $t \le f$ is the actual number of faults in the execution. This condition is always true for $f<n/3$ protocols, but for $n=2f+1$ this only holds when $t<n/4$.

These protocols have the maximal resilience and in addition provide responsiveness is some subset of optimistic executions.

#### Responsiveness in the multi-shot case

When designing protocols for multi-shot consensus, the conditions for responsiveness are a function of exactly how the protocol is designed. For a view-based protocol that performs one consensus per view and switches views, every say $10\Delta$ timeout, then to do $k$ decisions, even if all parties are non-faulty, would take $O(\Delta k)$ time even if the actual network delays are $<< \Delta$. The question naturally extends to whether we can achieve responsive [log replication](https://decentralizedthoughts.github.io/2022-11-19-from-single-shot-to-smr/).

**Responsiveness for log replication**: an execution is responsive if the actual network delays are at most $\delta$ then to drive $k$ decisions the total latency is $O(k \delta)$.

We can again ask the natural question: 

> Under what conditions can a log replication protocol obtain responsiveness?

For *leader based* protocols, a responsive log replication protocol for $k$ decisions terminates in $O(k \delta)$ latency when the leader is non-faulty. When considering a *stable leader* protocol, the leader needs to be non-faulty. When considering a *rotating leader* protocol, we need each of the rotating leaders for the $k$ decisions to be non-faulty. In fact, the examples described in the table earlier are all multi-shot instances. While PBFT, SBFT, PS'17, and ANRS'21 assume a stable leader, HotStuff and ANS'22 allow for rotating leaders. 

### Does responsiveness matter?

Does it matter if we get $(k \Delta)$ or $O(k \delta)$? If the gap between $\delta$ and $\Delta$ is not large, then it does not matter much. In some systems, there is no need to move faster than one decision per $O(\Delta)$ time. However, in some settings obtaining better good-case performance is critical for higher performance when the system is not under active attack. 

In the worst case, even one decision may take $O(\Delta f)$ time, so being responsiveness only improves in some good conditions but not in the worst case.

For $f<n/3$ a counterargument against responsiveness is that by using randomization, it is possible to *always* obtain expected latency of $O(\delta)$ in asynchrony for agreement. However, these randomized approaches seem to inherently require $\Omega(n^2)$ messages, even in executions where all parties are non-faulty. 

In contrast, responsive protocol can obtain eventual responsiveness in partial synchrony and require just a linear message complexity (after GST) under the condition that the leader is non-faulty.


Your thoughts on [Twitter](https://twitter.com/kartik1507/status/1604498852006211584?s=61&t=65S2XC6f0QGX_9FlxpLbyg).

