---
title: Synchronous Consensus Lower Bound via Uncommitted Configurations
date: 2019-12-15 12:05:00 -05:00
tags:
- lowerbound
author: Ittai Abraham
---

In this second post, we show the fundamental lower bound on the number of rounds for consensus protocols in the synchronous model.

**Theorem**: Any protocol solving consensus in the *synchronous* model for $n$ parties that is resilient to $n-2 \geq t \geq 1$ crash failures must have an execution with at least $t+1$ rounds.


* **Bad news**: Deterministic synchronous consensus is *slow*. Even for crash failures, it requires $\Omega(n)$ rounds when the number of failures is any constant fraction of $n$.
* **Good news**: With randomization, synchronous consensus is possible in constant expected time (even against a strongly adaptive adversary). See [this post](https://decentralizedthoughts.github.io/2019-11-11-authenticated-synchronous-bft/) for a survey. Note that randomization does not circumvent the existence of an execution that takes $t+1$ rounds, it just (exponentially) reduces the probability of this event.


We use the proof approach of [Aguilera and Toueg](https://ecommons.cornell.edu/bitstream/handle/1813/7355/98-1701.pdf?sequence=1&isAllowed=y) that is based on **uncommitted** (bivalent) configurations. The high-level idea: show that there must exist an adversary strategy, that crashes just one party each round, and creates a sequence of $t-1$ uncommitted configurations.  


Recall that an **uncommitted configuration** is a configuration where no party can decide because the adversary can still change the decision value. We assume you are familiar with the [definitions in the previous post](https://decentralizedthoughts.github.io/2019-12-15-consensus-model-for-FLP/) and with  Lemma 1 of that previous post:

**Lemma 1: ([Lemma 2 of FLP85](https://lamport.azurewebsites.net/pubs/trans.pdf))**: Any protocol that solves consensus, resilient to one crash failure, must have an initial configuration that is an **uncommitted configuration**.


To prove Theorem 1 above we prove the following two lemmas:

**Lemma 2: Uncommitted configuration at end of round $(t{-}1)$ ([Lemma 3 of AT98](https://ecommons.cornell.edu/bitstream/handle/1813/7355/98-1701.pdf?sequence=1&isAllowed=y))**: If $\mathcal{P}$ solves consensus and is resilient to an adversary that can crash at most one party every round, for $t$ rounds, then there must exist an **uncommitted configuration** at the end of round $t{-}1$.

Recall the **proof pattern** for showing the existence of an **uncommitted configuration**:

1. Proof by *contradiction*: assume all configurations are either 1-committed or 0-committed.
2. Define some notion of **adjacency**. Find *two adjacent* configurations $C$ and $C'$ such that $C$ is 1-committed and $C'$ is 0-committed.
3. Reach a contradiction due to an **indistinguishability** argument between the two adjacent configurations, $C$ and $C'$. The adjacency allows the adversary to cause indistinguishability via *crashing of just one* party.


**Proof of Lemma 2: Uncommitted configuration at end of round $(t{-}1)$**: The proof shows the existence of a sequence of **uncommitted configurations** $C_0 \rightarrow,\dots. \rightarrow C_{t-1}$, where for each $0 \leq k \leq t-1$, $C_k$ is an **uncommitted configuration** at the end of round $k$, where the adversary can crash at most one party each round. The proof is by induction on $k$. 

The base case of $k=0$, that an uncommitted initial configuration $C_0$ exists follows from *Lemma 1*. 

For the induction step, assume we are at an uncommitted round $0 \le k \le t-2$ configuration $C_k$. Let's show that there must exist a round $k{+}1$ uncommitted configuration $C_{k+1}$ where the adversary can crash at most one party in round $k{+}1$. Naturally we will use the recurring *proof pattern*:

1. Seeking a contradiction, assume all round $k{+}1$ configurations $C$ that extend $C_k$,  $C_k \rightarrow C$, with at most one crash, are either 1-committed or 0-committed.
2. Assume (without loss of generality) that with no crashes in round $k{+}1$, the system is 1-committed at the end of round $k{+}1$. 
3. Case 1: There exist some parties $j,i$ that have not crashed at the beginning of round $k{+}1$, such that $j$' crash in round $k{+}1$ before sending to $i$ changes the configuration to be 0-committed, while $j$'s crash after sending to $i$ keeps the configuration 1-committed. Consider in both these configurations the case where party $i$ crashes at the beginning of round $k{+}2$ (the adversary is allowed to crash because $k+2\leq t$). These two configurations are indistinguishable because only party $i$ sees the difference in $j$'s behavior and party $i$ crashes before it can convey this information. Hence, the remaining parties in both worlds must decide the same value. But this implies a safety violation because one world is 1-committed and the other is 0-committed. This is a contradiction to the assumption that there are no uncommitted configurations in round $k{+}1$.
4. Case 2: there exists some party $j$ whose crash at the end of round $k{+}1$ changes the configuration to be 0-committed. But now consider the execution where party $j$ crashes at the beginning  of round $k{+}2$. This 1-committed world is indistinguishable from the 0-committed world where party $j$ crashes at the end of round $k{+}1$. Hence, again a contradiction.

This concludes the induction step, which concludes the proof.

The proof shows the existence of an **uncommitted configuration** $C_k$ in the end of round $k$ for each $0 \leq k \leq t-1$. This concludes the proof of lemma 2.


So we reached the end of round $t{-}1$ with an **uncommitted configuration**. Can we decide in one round and terminate in round $t$? The following Lemma shows we cannot, and completes Theorem 1:

**Lemma 3: Round $t$ cannot always decide ([Lemma 1 of AT99](https://ecommons.cornell.edu/bitstream/handle/1813/7355/98-1701.pdf?sequence=1&isAllowed=y))**: If $\mathcal{P}$ has an execution that crashes at most one party every round for $t$ rounds and leads to an uncommitted configuration at the end of round $t-1$, then in that execution $\mathcal{P}$ cannot always decide by the end of round $t$.


**Proof of Lemma 3** is a simple variation of the **proof pattern** that looks at deciding configurations instead of committed configurations.

1. Seeking a contradiction, assume that with $\mathcal{P}$ all non-faulty parties decide after $t$ rounds (for any adversary strategy). So all round $t$ configurations $C_{t-1} \rightarrow C$ are either 0-deciding or 1-deciding.

2. Define two round-$t$ configurations $C,C'$ as *$j,i$-adjacent* if the only difference is that in $C$ party $j$ crashes right before sending to non-crashed party $i$ and in $C'$ party $j$ crashes right after sending to party $i$ (and $j$ is the only new crash happening in round $k+1$).  By adjacency, we can construct two $j,i$-adjacent configurations in the end of round $t$ such that $C$ is 1-deciding and $C'$ is 0-deciding. Note that it cannot be that $j$ crashing at the end changes the decision value, because other players cannot distinguish this event.

3. Given $n>t+1$ there are at least two non-crashed parties in round $t$, so at least one of them is not $i$ or $j$. However, this non-faulty party has no way to distinguish between the two deciding configurations $C$ and $C'$. This is a contradiction.

This concludes the proof of Lemma 3, which concludes the proof of the main Theorem.

### Discussion

The proof started with an initial **uncommitted configuration** (Lemma 1) and then showed that we could continue for $t-1$ rounds to reach an **uncommitted configuration** (Lemma 2) at the end of round $t-1$. Finally, we used one more crash to show that we cannot always decide at the end of $t$ rounds (Lemma 3). Note that the theorem is non-constructive, and all it shows is that a $t+1$ round execution must exist (but does not say what is the probability measure of this event).

A fascinating observation from this lower bound is that in order to create a long execution the adversary must corrupt parties *gradually*: just one party every round. This fact is critical for some upper bounds and will be discussed in later posts.

For Lemma 3 we needed $n>t+1$. For $n=t{+}1$ we can still apply Lemma 2 and show that a $t=n-1$ round execution must exist.

In a [follow-up post we discuss lower bounds for early stopping](), lower bounds for the number of rounds in executions where the actual number of failures is $f \le t$.  It seems that for this we need some definitions that are stronger than uncommitted configurations.

In the [next post](https://decentralizedthoughts.github.io/2019-12-15-asynchrony-uncommitted-lower-bound/), we use the same proof approach to prove that in the *asynchronous* model, there must exist an *infinite* execution even for protocols that are resilient to just one crash failure.

### Acknowledgment

Many thanks to Kartik Nayak for valuable feedback on this post.

Please leave comments on [Twitter](https://twitter.com/ittaia/status/1206297946045767680?s=20)
