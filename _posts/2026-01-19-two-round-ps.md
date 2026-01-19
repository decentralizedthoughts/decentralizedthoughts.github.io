---
title: On Optimistic 2-round Fast Path under Partial Synchrony (!?!)
date: 2026-01-19 01:00:00 -05:00
author: Ittai Abraham, Kartik Nayak, and Alejandro Ranchal-pedrosa
---

Consensus protocols for $n=3f+1$ can tolerate $f$ Byzantine faults under partial synchrony. However, they also require a latency of [3 rounds in the good-case](https://decentralizedthoughts.github.io/2021-02-28-good-case-latency-of-byzantine-broadcast-a-complete-categorization/) when the leader is non-faulty and the system is synchronous. *Can we get a protocol with better latency, or tolerate more faults, if we assume $n=3f+2p+1$?*

1. **Better latency:** If the actual number of Byzantine faults in an execution are fewer, then the protocol can commit faster. Starting with [Fab](https://www.cs.cornell.edu/lorenzo/papers/fab.pdf) (and see technical reports [here](https://lpdwww.epfl.ch/upload/documents/publications/567931850DGV-feb-05.pdf) and [here](https://lamport.azurewebsites.net/pubs/lower-bound.pdf)), later [SBFT](https://arxiv.org/pdf/1804.01626.pdf), and recently [KudzuBFT](https://arxiv.org/pdf/2505.08771.pdf), there is a line of protocols for $n = 3f + 2p + 1$ that can have a two round fast path when there are at most $p$ Byzantine faults, and a regular three round path when there are up to $f$ Byzantine faults, for $p\le f$. See [our post on this topic]().

2. **Tolerating more faults:** There are folklore constructions with $n = 3f+2c+1$ that can tolerate up to $f$ Byzantine faults *and* $c$ crash faults, that obtain a latency of 3 rounds in the good case.

Thus, a natural question is whether we can obtain the best of both worlds:
(A) Good case 2 rounds when there are $\le p$ Byzantine faults, and simultaneously; and
(B) Good case 3 round when there are $f$ Byzantine *and* $p$ crash faults.

[Hydrangea](https://eprint.iacr.org/2025/1112.pdf) address this question. For $n = 3f+2c+k+1$ (where $k$ is a parameter), they show a protocol with: (i) a good case 2 rounds when there $\le p = (c+k)/2$ Byzantine faults, and (ii) a good case 3 rounds when there are $f$ Byzantine and $c$ crashes. As an example, when setting $c = k (= p)$, we have $n = 3f+3p+1$. Moreover, they show this is tight by presenting a matching lower bound under partial synchrony.

[Alpenglow](https://www.anza.xyz/alpenglow-1-1) also address this question. They show that under the assumption that the leader cannot equivocate (*Assumption 3* in their paper), it is possible to get $n = 3f + 2p + 1$ with a two round good case when there are at most $p$ Byzantine faults, and a regular three round good case when there are $f$ Byzantine *and*  $p$ crashes.

Assuming the leader cannot equivocate is traditionally interpreted as a strong synchrony style assumption. In this post we explore potentially weaker synchrony assumptions that still enables the same quorum arithmetic.

## Intuition

We assume a view based protocol wherein in each view, there is a designated leader who proposes blocks, and parties vote on these blocks. Quorums of votes are collected into certificates. Observe that in partially synchronous protocols with $n = 3f+2p+1$ tolerating $f$ Byzantine faults and $p$ crashes without any optimistic latency commits, quorums will be of size $n-f-p$ (since two quorums of this size always intersect in at least 1 non-faulty party). In a 3-round commit rule with two voting phases, the first phase guarantees that only up to one value $B$ can be certified, and the second voting phase guarantees that if some party commits, then sufficiently many parties ($n-f-p$ to be precise) are locked on $B$. It also guarantees that, during view change, if the next leader waits for responses from $n-f-p$ parties, it will receive a certificate for $B$ from this view (or a higher view).

If we enable an optimistic commit rule where there is only one voting phase, say with $n-p$ votes for some value $B$ in view $v$, of course, the leader in view $v+1$ will learn about votes for $B$ (since the quorum of $n-p$ votes for $B$ and the quorum of $n-f-p$ parties the view $v+1$ leader hears from during view change, intersects in $f+1$ parties). The problem, though, is that this value $B$ may not be uniquely voted for in view $v$. In fact, if there are $n-p$ votes ($n-f-p$ honest votes) for $B$, the remaining $n-(n-f-p)$ parties could have potentially voted for a different value $B'$. Moreover, during view change, the leader of view $v+1$ could receive all of the $f+p$ votes for $B'$. From the leader's perspective, $B$ only has $f+1$ votes while $B'$ has $f+p$ votes, and it will wrongly prefer $B'$ (when $p \geq 1$).

This is intuitively the key hurdle for supporting a fast path when $n = 3f+2p+1$ with $f$ Byzantine and $c$ crash faults under partial synchrony. What if we make a slightly stronger synchrony assumption to enable this property?

## Quorum sizes

We first summarize the quorum sizes of interest: 

* $n-f-p$, a slow certificate, is the quorum used in the non-optimistic case for progress under $f$ Byzantine and $p$ crashes;
* $f+p+1$, a weak certificate, is the quorum used during view change to account for a fast path commit in earlier views
* $n-p$, fast commit threshold

## The additional granular synchrony assumption

Fix a delay bound $\Gamma$.

**Assumption.** For every honest party, at all times, there are at most $f$ honest parties whose messages to it may be delayed by more than $\Gamma$. We note that this is a specific instantiation of the more general [granular synchrony model](https://arxiv.org/pdf/2408.12853).

This assumption is used for safety, because parties use the absence of a weak certificate after waiting $\Gamma$ to infer that no commit certificate can exist.

## The view change rule to support fast path

The leader waits for only $n - f - p$ messages and at least until $\Gamma$ time. Then, it applies the following rule:

* Let $B'$ be the value for which it receives a weak certificate of size $f+p+1$ from the highest view $v'$. $B'$ could be $\bot$ if such a value does not exist; ; in that case $v' = 0$.
* Let $B''$ be the value for which it receives a slow certificate from the highest view $v''$. $B''$ could be $\bot$ if such a value does not exist; in that case $v'' = 0$.
* To propose, if $\max(v', v'') = 0$, it could propose any value. Otherwise, if $v' > v''$, it will propose $B'$ along with the slow certificate, else, it will proposer $v''$ with the fast certificate.

Note that the above rule could be modified to wait for $\Gamma$ time only in pessimistic cases. In particular, on receiving $n-f-p$ messages, the leader needs to wait only if it observes an equivocating vote from the same or higher view than the highest weak certificate. Otherwise, the potential additional $f+p$ messages received could not result in a weak certificate.

## Why does the granular synchrony assumption address the aforementioned concern?

Assume that some value $B$ was fast committed with $n - p$ votes.

Then, at least $n-p - f$ of these votes were sent by honest parties. 

Thus, during view change, by the granular synchrony assumption, an honest leader of view $v+1$ will receive messages from all $f$ parties within $\Delta$ time. Thus, it will receive $\geq (n-p-f)-f = f+p+1$ of the honest votes, which is the threshold for the weak certificate. Observe that, while an equivocating value $B'$ could also have support, $f+p+1$ is a majority among $n-p-f = 2f+p+1$ view change messages.

Contrapositively, if after waiting $\Delta$ the leader does not see any weak certificate of size $f + p + 1$, then no value could receive $n - p$ votes.

**Acknowledgment.** We would like to thank Yuval Efron, Ling Ren, Quentin Kniep, Kobi Sliwinski, and Roger Wattenhofer for discussions and insights on this topic.
