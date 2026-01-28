---
title: Concurrent 2-round and 3-round BFT protocols under granular synchrony
date: 2026-01-24 01:00:00 -05:00
author: Ittai Abraham, Kartik Nayak, and Alejandro Ranchal-pedrosa
---

Consensus protocols for $n=3f+1$ can tolerate $f$ Byzantine faults under partial synchrony. However, they also require a latency of [3 rounds in the good-case](https://decentralizedthoughts.github.io/2021-02-28-good-case-latency-of-byzantine-broadcast-a-complete-categorization/) when the leader is non-faulty, and the system is synchronous. *Can we get a protocol with better latency, or tolerate more faults, if we assume $n=3f+2p+1$?*

1. **Better latency:** If the actual number of Byzantine faults in an execution are fewer, then the protocol can commit faster. Starting with [Fab](https://www.cs.cornell.edu/lorenzo/papers/fab.pdf) and [Zyzzyva](https://dl.acm.org/doi/10.1145/1658357.1658358) (also see technical reports [here](https://lpdwww.epfl.ch/upload/documents/publications/567931850DGV-feb-05.pdf) and [here](https://lamport.azurewebsites.net/pubs/lower-bound.pdf)), later [SBFT](https://arxiv.org/pdf/1804.01626.pdf), and recently [KudzuBFT](https://arxiv.org/pdf/2505.08771.pdf), there is a line of protocols for $n = 3f + 2p + 1$ that can have a two round fast path when there are at most $p$ Byzantine faults, and a regular three round path when there are up to $f$ Byzantine faults, for $p\le f$. See [our post on this topic](https://decentralizedthoughts.github.io/2025-07-29-2-round-3-round-simplex/).

2. **Tolerating more faults:** There are folklore constructions with $n = 3f+2c+1$ that can tolerate up to $f$ Byzantine faults *and* $c$ crash faults, which obtain a latency of 3 rounds in the good case.

Thus, a natural question is whether we can obtain the best of both worlds:

1.  Good case 2 rounds when there are $\le p$ Byzantine faults, and simultaneously;
2.  Good case 3 rounds when there are $f$ Byzantine **and** $p$ crash faults.

There are three ways to address this question:

1. [Hydrangea](https://eprint.iacr.org/2025/1112.pdf) address this question assuming partial synchrony. For $n = 3f+2c+k+1$ (where $k$ is a parameter), they show a protocol with: (i) a good case 2 rounds when there $\le p = (c+k)/2$ Byzantine faults, and (ii) a good case 3 rounds when there are $f$ Byzantine and $c$ crashes. As an example, when setting $c = k (= p)$, we have $n = 3f+3p+1$. Moreover, they show this is tight by presenting a matching lower bound under partial synchrony.

2. [Alpenglow](https://www.anza.xyz/alpenglow-1-1) address this question assuming partial synchrony and that no leader can equivocate (*Assumption 3* in their paper). For $n = 3f + 2p + 1$, they get a two-round good case when there are at most $p$ Byzantine faults, and a regular three-round good case when there are $f$ Byzantine *and* $p$ crashes.

    Assuming the leader cannot equivocate is traditionally interpreted as a full synchrony style assumption (see the [DLS lower bound](https://decentralizedthoughts.github.io/2019-06-25-on-the-impossibility-of-byzantine-agreement-for-n-equals-3f-in-partial-synchrony/)). 

3. In this post, we explore potentially weaker synchrony assumptions that still enable the same quorum arithmetic. We show that it is possible to get $n = 3f + 2p + 1$ in a model that is in between partial synchrony and synchrony:

    Fix delay bounds $\Delta \le \Gamma$. After GST, any message sent at time $t$ arrives by time $t+\Delta$. Before GST, we assume the granular synchrony condition below:

    **Granular synchrony before GST:** Before GST, for every honest party, at all times, there are at most $f$ honest parties whose messages to it may be delayed by more than $\Gamma$. We note that this is a specific instantiation of the more general [granular synchrony model](https://arxiv.org/pdf/2408.12853).

    This assumption is strictly stronger than partial synchrony and strictly weaker than full synchrony or a non-equivocating leader assumption. Importantly, it is used primarily for safety reasoning, specifically to infer the non-existence of a fast commit from the absence of a fast certificate after waiting $\Gamma$.

    In this post, we will show how to use this assumption to modify the [Concurrent 2-round and 3-round Simplex-style BFT](https://decentralizedthoughts.github.io/2025-07-29-2-round-3-round-simplex/) by essentially changing *one line*. Similar results can be obtained by minimal changes in similar protocols (like Alpenglow or Hydrangea).

    Specifically, the result obtained is:

    * Honest leader post GST with $p$ Byzantine faults: commit in $2\delta$.
    * Honest leader post GST with $f$ Byzantine faults and $p$ crashes: commit in $3\delta$.
    * Non equivocating leader post GST: view completes in at most $3\Delta + \delta$.
    * Equivocating leader post GST: view completes in at most $2\Gamma + 5\Delta + \delta$ and the leader is publicly detected as malicious.
    * Safety under up to $f$ Byzantine faults and $p$ crashes given the granular synchrony assumption before GST.



## Intuition

**Why waiting for $n-f$ is required under partial synchrony and equivocation**

In partial synchrony, the only case where the [2,3 protocol](https://decentralizedthoughts.github.io/2025-07-29-2-round-3-round-simplex/) is required to wait for $n-f$ messages is to provide safety in the case that some party has a fast commit (see Upon 7 in the [blog post](https://decentralizedthoughts.github.io/2025-07-29-2-round-3-round-simplex/)).

If a party fast commits, we want all other parties to leave the view with a fast certificate for that value. Since a fast commit is $n-p$ votes, then waiting for $n-f$ implies hearing at least $n-p-f-f$ honest votes and since $n-p-2f = f+p+1$, this is a fast certificate.

If we only wait for $n-p-f$ votes, we may see only $n-p-f-f-p$ honest votes and hence only $f+1$ votes. But this may not be unique; a malicious leader may cause us to see two values with $f+1$ votes!

**Why non-equivocation allows waiting for $n-f-p$**

The first observation is that a non-equivocating leader cannot cause this problem. Each honest party either votes for the common value or for $\bot$, hence either half of the $2f+2p+1$ honest parties vote for the leader's value $x$ or half vote for $\bot$. In either case, at least $f+p+1$ honest votes are for the same value, hence fast certificate will eventually form.


**Why granular synchrony replaces non-equivocation**

The second observation is that waiting for $n-p-f$ and a timeout is safe under our granular synchrony assumption: Out of the $n-p-f$ honest that helped a fast commit of $n-p$ to form, at most $f$ of them are delayed by more than $\Gamma$, hence everyone waiting sufficiently long will hear $n-p-f-f$ of them which is $f+p+1$ and is enough to obtain the required fast certificate. If the timeout expires and no fast certificate is seen, then it means it is safe to vote for $\bot$.


## Quorum sizes

Recall the quorum sizes of interest from the [2,3 protocol](https://decentralizedthoughts.github.io/2025-07-29-2-round-3-round-simplex/) post: 

* $n-f-p$, a slow certificate, is the quorum used in the non-optimistic case for progress under $f$ Byzantine and $p$ crashes;
* $f+p+1$, a fast certificate, is the quorum used during view change to account for a fast path commit in earlier views
* $n-p$, fast commit threshold



## The protocol change


Our [2,3 protocol](https://decentralizedthoughts.github.io/2025-07-29-2-round-3-round-simplex/) has the following rule, which is the only one that requires $n-f$:

```
7. Upon receiving n-f (Vote, k, *) but no Fast-Cert(k, x) for any x 

    Send (Vote, k, ⊥) 

```

We modify it by adding a $\Lambda = 2\Gamma + 2\Delta$ wait and changing the threshold from $n-f$ to $n-f-p$:

```
7.   Upon receiving n-f-p (Vote, k, *) but no Fast-Cert(k, x) for any x 

     Start timer T2_k
   
7'.  Upon T2_k = Λ  // will only happen if we stay in view

     Send (Vote, k, ⊥)  

```

## Proof sketch

### Liveness: no additional wait for a non-equivocating leader

After GST with a non-equivocating leader that proposes $x$, all honest parties vote for either $x$ or $\bot$. Hence a majority of the $2f+2p+1$ honest parties  will either form a fast certificate for $x$ or for $\bot$ (a fast certificate requires $f+p+1$ votes). Hence a fast certificate of size $f+p+1$ forms without the $\Lambda$ wait.

### Liveness: additional wait for an equivocating leader

After GST, if no fast certificate is formed by the time all honest end their $\Lambda$ wait, then all honest will send a vote for $\bot$ and hence a fast certificate will form. The worst case latency of such a view is $\Lambda + 3\Delta+\delta = 2\Gamma + 5\Delta+\delta$. Moreover, the leader of this view is publicly detected as malicious.


### Safety: Fast commit for $x$ implies at most $f+p$ votes for any other value and a fast certificate for $x$ after at most $\Gamma$.

Assume a fast commit for $x$ was formed with $n - p = 3f + p + 1$ votes.

Consider any honest party that receives $n - f - p = 2f + p + 1$ votes at time $t$, since that set contains at least $f+1$ honest votes we know from the granular synchrony assumption that every honest party must hear at least one of them by time $t+\Gamma$. Hence all honest must start their view by time $t + \Gamma$.

Honest parties only vote for a non-$\bot$ value in the first $2\Delta$ time after starting the view, so by time $t + \Gamma + 2\Delta + \Gamma = \Lambda$ all honest votes for $x$ that are at most $\Gamma$ delayed must have been seen.

Therefore, if a fast commit of $n - p = 3f + p + 1$ votes was formed then least $(3f + p + 1) - f = 2f + p + 1$ of these votes were sent by honest parties and from the above reasoning, after the $\Lambda$ wait, each honest party will have seen at least $(2f + p + 1) - f = f + p + 1$ votes for $x$ and hence a fast certificate for $x$ and therefore will not vote for $\bot$.


## Summary

There are currently three ways to get a 2-round good case with $p$ Byzantine and a 3-round good case with $f$ Byzantine and $p$ crash:

1. Assuming asynchrony before GST, [Hydrangea](https://eprint.iacr.org/2025/1112.pdf) gets it with $n=3f+3p+1$.
2. Assuming the leader cannot ever equivocate,  [Alpenglow](https://www.anza.xyz/alpenglow-1-1) gets it with $n=3f+2p+1$.
3. Assuming granular synchrony before GST, that at most $f$ honest can be asynchronous and the rest are $\Gamma$ bounded, this post also gets it with $n=3f+2p+1$.

## Notes

We note that a similar change under the same granular synchrony assumption allows Hydrangea to operate under $n = 3f+2p+1$. Specifically, if there is a fast commit for $x$ with $n-p$ votes in a view, a subsequent leader will obtain a fast certificate for $x$ since, $n-p-f$ of these votes are honest, and by the granular synchrony assumption, the leader receives $\geq n-p-2f = f+p+1$ of these votes. A similar change applies to Alpenglow as well.

## Acknowledgments

We would like to thank our co-authors Yuval Efron and Ling Ren. We also thank  Lefteris Kokoris-Kogias, Quentin Kniep, Kobi Sliwinski, and Roger Wattenhofer for discussions and insights on this topic.
