---
title: The FLP Impossibility, Asynchronous Consensus Lower Bound via Uncommitted Configurations
date: 2019-12-15 12:15:00 -05:00
tags:
- asynchrony
- lowerbound
author: Ittai Abraham
---

In this third post, we conclude with the celebrated Fischer, Lynch, and Paterson impossibility result from 1985. It is the fundamental lower bound for consensus in the [asynchronous model](https://decentralizedthoughts.github.io/2019-06-01-2019-5-31-models/).

**[Theorem 1 (FLP85)](https://groups.csail.mit.edu/tds/papers/Lynch/jacm85.pdf)**: Any protocol $\mathcal{P}$ solving consensus in the *asynchronous* model that is resilient to even just one crash failure must have an infinite execution.


* **Bad news**: Deterministic asynchronous consensus is *impossible*.
* **Good news**: With randomization, asynchronous consensus is possible in constant expected time. See [this paper](https://research.vmware.com/files/attachments/0/0/0/0/0/7/8/practical_aba_2_.pdf) for a recent result. Note that randomization does not circumvent the existence of a non-terminating execution, it just reduces the probability measure of this event to have [measure zero](https://en.wikipedia.org/wiki/Almost_surely).

{: .box-note}
A much simpler proof for this theorem [in this post](https://decentralizedthoughts.github.io/2024-03-07-mobile-is-FLP/).

This post assumes you are familiar with the [definitions of the first post](https://decentralizedthoughts.github.io/2019-12-15-consensus-model-for-FLP/) and with Lemma 1 that we proved in the first post:


**Lemma 1: (Lemma 2 of FLP85)**: $\mathcal{P}$ has an initial **uncommitted configuration**.

Recall that given a configuration $C$ there is a set $M$ of pending messages. These are messages that have been sent but not delivered yet. For $e \in M$ we write $e=(p,m)$ to denote that party $p$ has been sent a message $m$. Also, recall that an [**uncommitted configuration**](https://decentralizedthoughts.github.io/2019-12-15-consensus-model-for-FLP/) is a configuration where no party can decide because the adversary can still change the decision value.


Given an initial **uncommitted configuration**, our goal will be to build an infinite execution such that:

1. The sequence is **uncommitted**: every configuration of the infinite execution is **uncommitted**. If a configuration is **uncommitted**, then no party can decide.
2. The sequence is *fair*: every message sent is eventually delivered. This is the essence of asynchrony, the adversary can delay messages, but only by a finite amount.

To prove the theorem, we use the following key technical Lemma:

**Lemma 2: Uncommitted Configurations Can Always be Extended ([Lemma 3 of FLP85](https://groups.csail.mit.edu/tds/papers/Lynch/jacm85.pdf))**: If $C$ is an **uncommitted configuration** and $e=(p,m)$ is any pending message of $C$, then there exists some $C \stackrel{\pi}{\rightsquigarrow} C' \xrightarrow{e=(p,m)} C''$ such that $e \notin \pi$ and $C''$ is an **uncommitted configuration**.

#### Proof of Theorem 1 from Lemma 1 and Lemma 2:

Start with Lemma 1, which gives us an initial **uncommitted configuration**. Repeat Lemma 2 infinitely often; each time apply it to the pending messages in a FIFO order. Clearly, from Lemma 2, the sequence is **uncommitted**. For fairness, due to FIFO, a message $e$ that has $\|M\|$ pending messages before it will be derived after at most $\|M\|+1$ applications of Lemma 2.

#### Proof of Lemma 2:

Recall the **proof pattern** for showing the existence of an ***uncommitted configuration***:

1. Proof by *contradiction*: assume all configurations are either 1-committed or 0-committed.
2. Find a *local structure*: two **adjacent configurations** $X$ and $X'$ such that $X$ is 1-committed and $X'$ is 0-committed.
3. Reach a contradiction due to an **indistinguishability** argument between the two adjacent configurations, $X$ and $X'$ using the adversary's ability to crash one party.


**Proof of Lemma 2** follows this pattern exactly:
The *contradiction* of the statement of Lemma 2 is that: there exists a configuration $C$ and a message $e=(p,m)$ such that for all $\pi$ with $e \notin \pi$, let $C \stackrel{\pi}{\rightsquigarrow} C'$, let $C' \xrightarrow{e=(p,m)} C''$, then either $C''$ is 1-committed or $C''$ is 0-committed ($C''$ is not **uncommitted**).


![](https://i.imgur.com/6eb3I6t.jpg)


Define two configurations $X,X'$ as **adjacent** (i.e., differing by a single pending message delivery) if $X \xrightarrow{T', e'=(p',m')} X'$ and $e'$ is a pending message in $X$.

**Claim**: there must exist two **adjacent configurations** $Y \xrightarrow{T', e'} Y'$ and a pending message $e'=(p',m')$ in $Y$ such that:

1. $C \rightsquigarrow Y \xrightarrow{e} Z$ and Z is 1-committed.
2. $C \rightsquigarrow Y \xrightarrow{T', e'} Y' \xrightarrow{e} Z'$ and $Z'$ is 0-committed.


**Proof of claim**: Since $C$ is an **uncommitted configuration**, there must exist two sequences $\tau_0$ and $\tau_1$ such that $C \stackrel{\tau_0}{\rightsquigarrow} D_0$ and $C \stackrel{\tau_1}{\rightsquigarrow} D_1$, where $D_0$ is 0-committed and $D_1$ is 1-committed. 

For each $i \in \{0,1\}$, let $\pi_i$ be the longest prefix of $\tau_i$ that does not contain $e$. Let $C \stackrel{\pi_0}{\rightsquigarrow} C_0 \xrightarrow{e} C'_0$ and $C \stackrel{\pi_1}{\rightsquigarrow} C_1 \xrightarrow{e} C'_1$. It follows from the assumption that $C'_0,C'_1$ must be committed and from $\tau_0,\tau_1$ that $C'_0$ is 0-committed and $C'_1$ is 1-committed.

Since $\pi_0,\pi_1$ start from the same configuration $C$, let $G$ be the least common ancestor configuration of $\pi_0,\pi_1$ and assume without loss of generality that $G\xrightarrow{e} G'$ is such that $G'$ is 1-committed. 

![](https://i.imgur.com/sZWp2VU.jpg)


Now examine the sub-sequence $G=Y_1,\dots,Y_k=C_0$ of $\pi_0$ from $G$ to $C_0$. Let $G'=Z_1,\dots,Z_k=C'_0$ be such that $Y_i \xrightarrow{e} Z_i$. Since $Z_1=G'$ is 1-committed and $Z_k=C'_0$ is 0-committed then clearly there must exist two **adjacent configurations** $Y \xrightarrow{T', e'} Y'$ (in the path $Y_1,\dots,Y_k$) such that that $Z$ is 1-committed and $Z'$ is 0-committed where $Y \xrightarrow{e} Z$ and $Y' \xrightarrow{e} Z'$. Note that this follows from the [discrete version of the intermediate value theorem](https://en.wikipedia.org/wiki/Sperner%27s_lemma#One-dimensional_case).


![](https://i.imgur.com/TLWm47j.jpg)

#### Proof of Lemma 2 given the claim

Let $Y,Y'$ be these two **adjacent configurations**. There are three cases to consider when looking at $e=(p,m)$, $e'=(p',m')$ and $T’$. In each case we derive a contradiction: 

* *Case 1*: $Y \xrightarrow{T'} Y''$ is such that $Y'' \xrightarrow{e} Z''$ is 0-committed. This means that the time of receiving $e$ is the only difference between these two worlds. But in this case $p$ may crash in both worlds after receiving $e$. Then $Y \xrightarrow{T'} Y'' \xrightarrow{e} Z'' \xrightarrow{p ~~crashes} W'' $ is indistinguishable from $Y \xrightarrow{e} Z \xrightarrow{p ~~crashes, T'} W$ but $W''$ is 0-committed (due to $Y''$) and $W$ is 1-committed (due to $Z$).

* *Case 2A*: (trivial case): $p \neq p'$. This implies that processing $e$ before $e'$ will lead to a different outcome than processing $e'$ before $e$. But since $e$ and $e'$ reach different parties there is no way to distinguish these two worlds, but again one is 0-committed and the other is 1-committed.


* *Case 2B*:  $p=p'$. This implies that the committed value must change between the world where $p$ receives $m$ first and $m'$ later relative to the world where $p$ receives $m'$ first and $m$ later. But what if in both worlds, $p$ crashes right after receiving both messages? These two worlds will be indistinguishable to the rest of the parties, but again one is 0-committed and the other is 1-committed.


This completes the proof of Lemma 2, and that completes the proof of the FLP Theorem.

### Discussion

We started from an **uncommitted configuration** (Lemma 1) and then showed that we could extend this to another **uncommitted configuration** infinitely many times and do this while eventually delivering every pending message (Lemma 2).

This proof is non-constructive; it shows that an infinite execution must exist. Using randomization, there are protocols that are *almost surely terminating* (their probability measure of terminating is one). There exist asynchronous consensus protocols that terminate in an expected constant number of rounds. More on that in later posts.

### Acknowledgments

We would like to thank Nancy Lynch, Kartik Nayak, Ling Ren, [Nibesh Shrestha](https://twitter.com/NibeshShrestha1), Sravya Yandamuri for valuable feedback on this post.


Please leave comments on [Twitter](https://twitter.com/ittaia/status/1206298743823355905?s=20)
