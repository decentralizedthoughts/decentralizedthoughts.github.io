---
title: 'Good-case Latency of Byzantine Broadcast: the Synchronous Case'
date: 2021-03-09 11:00:00 -05:00
tags:
- lowerbound
- research
author: Zhuolun Xiang
---

In our [first post](https://decentralizedthoughts.github.io/2021-02-28-good-case-latency-of-byzantine-broadcast-a-complete-categorization/), we presented a summary of our [good-case latency](https://arxiv.org/abs/2102.07240) results for Byzantine broadcast (BB) and state machine replication (SMR), where the good case measures the latency to commit given that the broadcaster or leader is honest. In our [second post](https://decentralizedthoughts.github.io/2021-03-03-2-round-bft-smr-with-n-equals-4-f-equals-1/), we discussed our results for partial synchrony, and described a new BFT SMR protocol named [(5f-1)-SMR](https://arxiv.org/abs/2102.07932) that can commit a decision within $2$ rounds in the good case and only requires $n\geq 5f-1$ replicas. In this third post, we highlight some of our results for synchrony, and provide intuition on how they improve the current best solutions.

Synchronous BFT SMR has received significant attention due to its $f<n/2$ resilience, in contrast to the $f<n/3$ resilience for partially synchronous BFT SMR. There has been a [sequence of work](https://decentralizedthoughts.github.io/2019-11-11-authenticated-synchronous-bft/) focusing on developing latency efficient BFT SMR protocol under synchrony. The state-of-the-art synchronous BFT SMR is [Sync HotStuff](https://decentralizedthoughts.github.io/2019-11-12-Sync-HotStuff/) with a good-case latency of $2\Delta +\delta$, where $\Delta$ is the assumed upper bound for network delay and $\delta\ll\Delta$ is the actual network delay. In this post, we show how to <mark>reduce the $2\Delta+\delta$ latency to $\Delta+2\delta$ for BFT SMR</mark>, and further improve it to the <mark>optimal $\Delta+1.5\delta$ for Byzantine broadcast</mark>.

## Sync HotStuff: Good-case Latency of $2\Delta +\delta$

[This post](https://decentralizedthoughts.github.io/2019-11-12-Sync-HotStuff/) describes Sync HotStuff, so we will just briefly recap here. The steady-state of the protocol works as follows:
1. **Propose**. The leader proposes its value.
2. **Vote.** On receiving the first valid proposal from the leader, a party will broadcast a vote for it. When a party votes, it also forwards the leader proposal to all other parties.
3. **Commit.** If a party does not receive a proposal for a conflicting value within $2\Delta$ time after voting, commit the value.

The good-case latency of the protocol is $2\Delta+\delta$, since the proposal from the leader reaches all parties within $\delta$, and parties wait for $2\Delta$ before commit.

<p align="center">
  <img width="350" src="https://i.imgur.com/myOd7pD.png">
</p>

![](https://github.githubassets.com/images/icons/emoji/unicode/1f4a1.png?v8) **Intuition.** Sync HotStuff uses a $2\Delta$ time to detect if the leader equivocated, and commit after $2\Delta$ if the party detects no equivocation. The time $2\Delta$ is sufficient: Suppose any party receives $v$ from the leader at time $t$ and commit $v$ at time $t+2\Delta$. The forwarded proposal will reach all honest parties within time $t+\Delta$. All honest parties will vote if they did not receive any conflicting value, and the value will be certified. Otherwise, if any honest party receives a conflicting value $v'$ before $t+\Delta$, the forwarded proposal of $v'$ will reach the first honest party before time $t+2\Delta$, and prevents it from committing $v$. Since the propose message may take time $\delta$ from the leader to all parties, the overall latency is $2\Delta +\delta$.

## $1\Delta$-SMR: Good-case Latency of $\Delta+2\delta$

Our [$1\Delta$-SMR protocol](https://arxiv.org/abs/2003.13155) improves the good-case latency of Sync HotStuff to $\Delta+2\delta$, by reducing the above equivocation detection time from $2\Delta$ to $\Delta$. The steady-state of our protocol works as follows:
1. **Propose.** The leader proposes its value.
2. **Vote.** On receiving the first valid proposal from the leader, a party forwards the proposal to all other parties, and wait for $\Delta$ time to detect equivocation. If no conflicting value is received during the $\Delta$ time, the party votes for the value.
3. **Commit.** If a party receives $f+1$ votes for the same value, commit the value.

The good-case latency of the protocol is $\Delta+2\delta$, since it takes $\delta$ to receive from the leader, $\Delta$ to detect equivocation, and $\delta$ to exchange votes.

<p align="center">
  <img width="350" src="https://i.imgur.com/g0PSsed.png">
</p>

![](https://github.githubassets.com/images/icons/emoji/unicode/1f4a1.png?v8)  **Intuition.** The key insight is that *a $\Delta$ time waiting period for equivocation detection is enough to ensure that no two honest parties vote for different values*. Suppose the first party in the figure is the earliest honest party that sends a vote. It receives $v$ for the leader at time $t$ and votes for $v$ at time $t+\Delta$. The forwarded value $v$ from the first honest party will reach all other honest parties within their $\Delta$ period and thus prevents them from voting for a different value $v'$. Since no two honest parties vote for different values, there can be at most one value with a certificate ($f+1$ votes), ensuring that all honest parties lock on the committed value. 

*Further improving the good-case latency in this paradigm, however, is nontrivial.* If we allow the parties to vote before the $\Delta$ period ends, there may be honest parties voting for different values before they detect equivocation. Then certificates for different values will be formed since $f$ Byzantine parties can double vote, and honest parties cannot tell which is the value that has been actually committed.



## $(\Delta+1.5\delta)$-BB: Optimal Good-case Latency of $\Delta+1.5\delta$

In our [good-case latency paper](https://arxiv.org/abs/2102.07240), we finally push the result to be optimal. Surprisingly, we discovered the tight bound is $\Delta+1.5\delta$, which **is not an integer multiple of the delay bound**. Our $(\Delta+1.5\delta)$-BB protocol is very different from conventional ones whose latency have always been an integer multiple of the message delay. Briefly, we describe the main steps of our $(\Delta+1.5\delta)$-BB protocol corresponding to the steady-state protocols from the previous sections.
1. **Propose.** The leader proposes its value.
2. **Vote.** For any value $d\in [0,\Delta]$, after $\Delta-0.5d$ time since receiving the proposed value $v$, parties send a vote containing $d$ and $v$, if no equivocation has been detected so far.
3. **Commit.** If $f+1$ votes with the same parameter $d$ and the same value $v$ are received, and no equivocation is detected for $\Delta+0.5d$ time since receiving $v$, a party can commit $v$. 


<p align="center">
  <img width="350" src="https://i.imgur.com/n6Bk4df.png">
</p>

![](https://github.githubassets.com/images/icons/emoji/unicode/1f4a5.png?v8) **Intuition.**  The novelty of our $(\Delta+1.5\delta)$-BB is to break the indistinguishability mentioned at the end of the previous section, by (1) allowing parties to *early vote* with a parameter $d$ that *guesses* all possible values of $\delta$, and (2) ranking the certificates by the value of $d$ (a smaller $d$ ranks higher). So in our protocol, **though honest parties may vote for different values, only the one with the highest rank will win**, and we will guarantee that the certificate for any committed value always has the highest rank. More specifically, we have the following claim.
> If any honest party commits $v$ with paramter $d$, the our protocol guarantees that no honest party can vote for any other value $v'\neq v$ with a parameter $d'\leq d$. 

The intuition is that, as shown in the figure, if the second honest party receives the proposal $v'$ no later than some time threshold, its forwarded proposal will stop the first honest party from committing $v$. But if the second honest party receives $v'$ later than the time threshold, the forwarded proposal of $v$ from the first honest party will stop it from sending any votes with parameter $d'\leq d$ due to detecting equivocation.

*Our construction guarantees a good-case latency of $\Delta+1.5\delta$.* When the broadcaster is honest, all honest parties receive the value within time $\delta$, send vote with $d=\delta$ within time $\delta+\Delta-0.5\delta$, and receive $f+1$ votes from honest parties and commit within time $\delta+\Delta-0.5\delta+\delta=\Delta+1.5\delta$. 


Note: The $(\Delta+1.5\delta)$-BB protocol is purely theoretical as the message complexity is unbounded, and its purpose is to show the tightness of the $\Delta+1.5\delta$ bound. In fact, we can easily parameterize the number of votes in the protocol to achieve a tradeoff between good-case latency $(1+\frac{1}{2m})\Delta+1.5\delta$ and communication cost $O(mn^2)$. For practice, our [$1\Delta$-SMR protocol](https://arxiv.org/abs/2003.13155) is a better option, which has $O(n^2)$ communication complexity for the steady-state (same as Sync HotStuff) and near-optimal good-case latency of $\Delta+2\delta$.

## What's More: the Complete Categorization for Synchrony

The $(\Delta+1.5\delta)$-BB protocol is in fact optimal in terms of latency for any $n/3<f<n/2$. Our [good-case latency paper](https://arxiv.org/abs/2102.07240) reveals the interesting structure of the good-case latency for broadcast as a function of the size of the adversary.  Our complete categorization of good-case latency under synchrony is summarized in the table below. Please check our paper for more details!

|   Resilience  |                         Lower Bound                        |                         Upper Bound                        |
|:-------------:|:----------------------------------------------------------:|:----------------------------------------------------------:|
|   $0<f<n/3$   |                          $2\delta$                         |                          $2\delta$                         |
|    $f=n/3$    |                       $\Delta+\delta$                      |                       $\Delta+\delta$                      |
|  $n/3<f<n/2$ \*  | $\Delta+1.5\delta$ | $\Delta+1.5\delta$ |
| $n/2\leq f<n$ |           $(\lfloor \frac{n}{n-f}\rfloor)\Delta$           |                  $O(\frac{n}{n-f})\Delta$                  |

\* The $\Delta+1.5\delta$ result assumes an unsynchronized start between different parties. If different parties start at the same time (have perfectly synchronized clocks), the optimal good-case latency is $\Delta+\delta$ for this case. 



Please answer/discuss/comment/ask on [Twitter](https://twitter.com/ittaia/status/1369327021831168000).