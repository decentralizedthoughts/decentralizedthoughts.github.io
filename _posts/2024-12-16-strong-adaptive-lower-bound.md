---
title: Agreement against strongly adaptive adversaries needs quadratic communication
date: 2024-12-16 07:30:00 -05:00
tags:
- lowerbound
- research
author: Ittai Abraham, Kartik Nayak, Ling Ren
chapters:
  - /2026-06-28-chapter-lower-bounds/
background:
  - /2019-08-16-byzantine-agreement-needs-quadratic-messages/
  - /2019-06-07-modeling-the-adversary/
---

In this post, we revisit the quadratic communication lower bound of [Abraham, Hubert Chan, Dolev, Nayak, Pass, Ren, Shi, 2019](https://arxiv.org/abs/1805.03391). We give a direct coupling proof with the following explicit constant:

**Theorem:** Any synchronous broadcast protocol for $n$ parties that tolerates $f$ strongly adaptive omission failures and has error probability at most $\epsilon<1/8$ has worst-case expected communication of at least $f^2/16$ messages.

Here, error means a violation of agreement, validity, or termination among non-faulty parties. Communication counts point-to-point messages sent by non-faulty parties, and the worst case is over the sender's input and admissible adversaries. Thus the bound also applies when counting messages sent by all parties.

The classic [Dolev and Reischuk 1982](https://www.cs.huji.ac.il/~dolev/pubs/p132-dolev.pdf) lower bound for *deterministic* protocols is covered [in this post](https://decentralizedthoughts.github.io/2019-08-16-byzantine-agreement-needs-quadratic-messages/). Here we allow *randomized protocols*, but require the adversary to be [strongly adaptive](https://decentralizedthoughts.github.io/2019-06-07-modeling-the-adversary/).

> Why is strong adaptivity needed?

A strongly adaptive adversary can observe a message being sent, immediately corrupt its sender, and *claw back* the message before delivery. Our adversary uses only omission failures: corrupted parties otherwise follow the protocol, including its prescribed random choices.

### Proof idea

We compare two worlds using the same random tapes and message-delivery schedule. In World 1, a set $V$ of faulty parties ignores its first few incoming messages. We choose a uniformly random party $p\in V$. In World 2, $p$ is honest, and the adversary instead corrupts the senders of those messages and omits them at the source. Every party sees the same protocol messages in both worlds.

If communication is small, $p$ probably has so few incoming messages that all of them are omitted. We choose $V$ so that a party receiving no messages has probability at least $1/2$ of failing to output the sender's bit. A union bound combines this event with low communication and successful outputs by the other honest parties. Recall that the union bound holds even when the events are correlated.

### Choosing the parties and the input

Consider each party other than the designated sender in a hypothetical execution in which it receives no messages from other parties. It still takes local steps, uses its random tape, and processes its timers. For each such party, at least one bit has probability at most $1/2$ of being its output. Non-termination counts as failing to output either bit.

By the pigeonhole principle, there is a bit $b$ and a set $Q$ of at least $\lceil(n-1)/2\rceil$ parties such that every party in $Q$ fails to output $b$ with probability at least $1/2$ in its no-message execution. By symmetry, call this bit 0 and give the designated sender input 0.

Set

$$
k=\lceil f/2\rceil,\qquad m=\lfloor f/2\rfloor.
$$

Choose a fixed set $V\subseteq Q$ of size $k$, and let $U$ contain the remaining parties, including the sender. Such a $V$ exists because $f<n$. For even $f$, both $k$ and $m$ are simply $f/2$; these definitions also handle odd $f$ and $f=1$.

### World 1: omit at the receiver

The adversary corrupts $V$. These parties follow the protocol except that:

1. Every party in $V$ ignores the first $m$ messages attempted from $U$ to it.
2. All messages between distinct parties in $V$ are omitted.

Messages from $V$ to $U$ are delivered normally. Fix any admissible synchronous delivery schedule for messages that are not omitted.

Let $B$ be the protocol's worst-case expected communication. Independently of this execution, choose $p$ uniformly from $V$. Let $M_p$ count all messages attempted from $U$ to $p$, including omitted messages. Since all parties in $U$ are non-faulty in World 1,

$$
\mathbb E[M_p]
=\frac1k\mathbb E\left[\sum_{v\in V}M_v\right]
\leq\frac Bk.
$$

Define three events on these random tapes and the choice of $p$:

* $S$: $M_p\leq m$, so every message to $p$ is omitted.
* $C$: every party in $U$ outputs 0 in World 1.
* $D$: the hypothetical no-message execution of $p$, using the same random tape and initial setup, does not output 0.

Recall that we set $k=\lceil f/2\rceil$ and $m=\lfloor f/2\rfloor$: $k=|V|$ is the number of initially faulty parties, and $m$ is the number of incoming messages each of them ignores. Markov's inequality gives

$$
\Pr[\neg S]=\Pr[M_p\geq m+1]
\leq\frac{\mathbb E[M_p]}{m+1}
\leq\frac{B}{k(m+1)}.
$$

The honest sender has input 0 in World 1, so correctness gives $\Pr[C]\geq1-\epsilon$. Our choice of $V\subseteq Q$ gives $\Pr[D]\geq1/2$. We will combine these unconditional probabilities after constructing World 2.

### World 2: omit at the sender

This adversary chooses $p$ uniformly from $V$, leaves $p$ honest, and corrupts $V\setminus\{p\}$. Messages between members of $V$ are still omitted; every such message has a corrupt endpoint.

For each of the first $m$ attempted messages from $U$ to $p$, the adversary corrupts its sender, if necessary, and removes that message before delivery. Let $W\subseteq U$ be the set of senders corrupted this way. These parties follow the protocol otherwise. In particular, attempts after the first $m$ are delivered normally, even if their senders are already corrupt.

The total number of corrupt parties is at most

$$
(k-1)+|W|\leq(k-1)+m=f-1\leq f.
$$

This is an online adversary: it needs no prediction of future messages or random choices. Strong adaptivity lets it remove a message immediately after observing the attempt to send it.

### Coupling the worlds

Use the same initial setup, random tapes, choice of $p$, and delivery schedule in both worlds. Whenever a corrupt party follows the protocol, it uses the same random tape as its counterpart.

**Claim (indistinguishability).** Under this coupling, every party has the same local protocol history in both worlds. In particular, the parties that remain honest cannot distinguish the two worlds. This holds whether or not event $S$ occurs.

*Proof.* The first $m$ messages from $U$ to $p$ are ignored at the receiver in World 1 and removed at the sender in World 2. If more than $m$ messages are attempted, message $m+1$ and every later message are delivered normally in both worlds, even when their senders have already been corrupted in World 2. Messages between members of $V$ are omitted in both worlds, and all remaining messages have the same delivery behavior.

Inductively, identical local histories and random tapes produce identical protocol actions, and these delivery rules give identical received messages at the next step. Corruption changes which parties we require to satisfy correctness, but does not otherwise change their protocol behavior in this construction. This proves the claim.

### When the coupling gives an error

On event $S$, $p$ receives no messages in either world. Its actual behavior then agrees with the hypothetical execution defining $D$. Thus, on $S\cap C\cap D$:

* the honest party $p$ in World 2 either does not terminate or outputs 1;
* every party in $U\setminus W$ remains honest in World 2 and outputs 0.

There is at least one such other honest party, since

$$
|U\setminus W|\geq n-k-m=n-f\geq1.
$$

Consequently, $S\cap C\cap D$ implies a termination or agreement error in World 2.

### One union bound

The three events may be correlated. A union bound still gives:

$$
\begin{aligned}
\Pr[\text{error in World 2}]
&\geq\Pr[S\cap C\cap D]\\
&\geq\Pr[D]-\Pr[\neg S]-\Pr[\neg C]\\
&\geq\frac12-\frac{B}{k(m+1)}-\epsilon.
\end{aligned}
$$

Correctness bounds World 2's error by $\epsilon$ as well. Rearranging,

$$
B\geq\left(\frac12-2\epsilon\right)k(m+1).
$$

For every integer $f\geq1$, we have $k\geq f/2$ and $m+1>f/2$, so $k(m+1)\geq f^2/4$. Since $\epsilon<1/8$,

$$
B>\frac14\,k(m+1)\geq\frac{f^2}{16}.
$$

This proves the theorem. The same calculation also gives the error-dependent bound

$$
B\geq\left(\frac18-\frac\epsilon2\right)f^2
\qquad\text{for }\epsilon<1/4.
$$

Please leave comments on [X](https://x.com/ittaia/status/1868794373267448243).
