---
title: Why BFT with Byzantine and Crash Faults Needs Three Rounds
date: 2026-09-26 04:00:00 -04:00
tags:
- lowerbound
author: Ittai Abraham, Aniket Kate, Kartik Nayak, Nibesh Shrestha, Alberto Sonnino
---

How many parties do we need to decide after one proposal and one round of
voting, when some faults are Byzantine and others are crashes? The answer
depends on both the faults we must tolerate for eventual progress and the
faults we want to tolerate on the fast path.

This post is based on the elegant 2005 lower bound in the unpublished technical
report of [Dutta, Guerraoui, and Vukolić][dgv]. A similar bound was proven in
[Hydrangea](https://eprint.iacr.org/2025/1112.pdf). This bound extends
[Why BFT Needs Three Rounds][three-round-bft] in two ways:

* It requires the protocol to be safe and live against $f$ Byzantine faults
  and $c$ crash faults. For $c=0$ and $p=f$, the $n=5f-2$ lower bound already
  appears in [Abraham et al.][anrz21] and
  [Kuznetsov, Tonkikh, and Zhang][ktz21].
* It requires the protocol to have a two round good case when there are at
  most $p$ faulty parties. For $c=0$, the $n=3f+2p-2$ lower bound already
  appears in [Kuznetsov, Tonkikh, and Zhang][ktz21].

## The generalized result

There are $n$ parties, including the leader. The adversary may control at most
$f$ Byzantine parties and at most $c$ additional crash faulty parties. The two
fault sets are disjoint. A Byzantine party may behave arbitrarily. A crash
faulty party follows the protocol until it crashes and then sends no more
messages.

We place no computational bound on the adversary.

The protocol must always satisfy agreement, must satisfy validity when the
leader is honest and GST is $0$, and must terminate after GST against the full
bounds of $f$ Byzantine faults and $c$ crash faults. We say that its two round
good case tolerates $p$ faulty parties if all correct parties decide within
two message delays ($2\delta$) whenever GST is $0$, the leader is honest, and at most $p$ parties
are faulty, with the Byzantine and crash faults respecting their respective
bounds.

Here GST is the global stabilization time. Before GST, message delay is unbounded. After GST, every message from one
correct party to another is delivered within $\delta\leq\Delta$ of the later
of GST and its send time. The good case latency is the time from the leader's
initial proposal until every correct party decides. Thus, two rounds means
one proposal followed by one round of voting, rather than two voting rounds.

The main result is:

**Theorem.** Let $f\geq1$, $c\geq0$, and $p$ be integers satisfying

$$
1\leq p\leq f+c.
$$

There is no protocol with $n=3f+c+2p-2$ parties that solves Byzantine
Broadcast in partial synchrony against at most $f$ Byzantine faults and $c$
additional crash faults and has a two round good case tolerating $p$ faulty
parties.

When $(c+2)/2\leq p\leq f+c$, this is tight: with $n=3f+c+2p-1$, a
two round good case tolerating the same $p$ faulty parties is possible, as we
will show in a future post.

The good news is that proving this generalized result requires only minor
changes to the parameters in the [base proof][three-round-bft].

## Proof

As in the [base proof][three-round-bft], we present the argument with the
leader proposing first and other parties then voting. Input-independent
messages sent before the proposal can be handled by the standard extension
in [Abraham et al.][anrz21].

The proof is by contradiction. Assume that a protocol with
$n=3f+c+2p-2$ has a two round good case tolerating $p$ faulty parties and show
that it must violate agreement.

The case $f=1,c=0$ forces $p=1$ and $n=3$, where Byzantine Broadcast is
already impossible against one Byzantine fault. Hence, assume $f+c\geq2$, so
the set $C$ defined below is nonempty.

Partition the parties into the leader and five sets $A,B,C,D,E$ with sizes

$$
|A|=|E|=p,
\qquad
|B|=|D|=f-1,
\qquad
|C|=f+c-1.
$$

The sets $B$ and $D$ may be empty. In particular, when $f=1$,
$B=D=\varnothing$. The prescribed Byzantine behavior of $B$ and $D$ is then
vacuous.

Indeed,

$$
1+|A|+|B|+|C|+|D|+|E|
=1+2p+2(f-1)+(f+c-1)
=3f+c+2p-2.
$$

The condition $p\leq f+c$ implies that either $A$ or $E$ can be made entirely
faulty using at most $f$ Byzantine faults and $c$ crash faults.

We consider three executions: a mixed world $M$, a corrupt world $\hat D$,
and a validity world $V$.

### World $M$ (mixed)

![Mixed world: the leader equivocates and C is silent.](/uploads/mixed-world-plus-crashes.svg)

In the mixed world, the leader is Byzantine. Of the parties in $C$, $f-1$
are Byzantine and the remaining $c$ are crash faulty. Thus, all parties in
$C$ are silent and the execution has exactly $f$ Byzantine faults and $c$
crash faults. Also, GST is $0$.

The leader sends $0$ to $A,B$ and $1$ to $D,E$. Since the protocol must
eventually terminate even when the leader is Byzantine, all correct parties
eventually decide the same value. Assume without loss of generality that they
decide $1$. If they decide $0$ instead, swap $A$ with $E$, $B$ with $D$, and the
roles of $0$ and $1$. We discuss randomized protocols below.

### World $V$ (validity)

![Validity world: the leader proposes 0 and E is silent.](/uploads/validity-world-plus-crashes.svg)

In the validity world, GST is $0$ and the leader is honest with input $0$.
All parties in $E$ are faulty and remain silent. This is an allowed execution:
$|E|=p\leq f+c$, so these faults can be divided into at most $f$ Byzantine
faults and at most $c$ crash faults. It is also an execution to which the
assumed two round good case applies because $|E|=p$.

The parties in $C$ hear the leader's value $0$ and receive the same first-round voting
messages for $0$ from $A,B,D$. Since the leader is honest, validity requires
every correct party to decide $0$. The assumed good case latency requires the
parties in $C$ to decide $0$ within two rounds.

### World $\hat D$ (corrupt)

![Corrupt world: D equivocates and messages from C are delayed.](/uploads/corrupt-world-plus-crashes.svg)

In this world, the leader and all parties in $D$ are Byzantine. Since
$|D|=f-1$, there are exactly $f$ Byzantine parties. This execution does not
need to use any of the allowed crash faults. Keep the network asynchronous
until after the decisions described below, and then let GST occur.

The leader sends $0$ to $A,B,C$ and $1$ to $E$. The Byzantine parties in $D$
behave toward $A,B,E$ as if they had received $1$, exactly as the honest
parties in $D$ do in world $M$. Toward $C$, they send the first-round voting messages
they would have sent after receiving $0$, exactly as the honest parties in
$D$ do in world $V$.

Before GST, delay every message sent by a party in $C$ to a party outside $C$,
and delay every message from $E$ to $C$. Deliver all other messages so that:

* the parties in $B,E$ see the same messages as in world $M$ until they
  decide; and
* the parties in $C$ see the same messages as in world $V$ through their two
  round decision point.

The parties in $B,E$ cannot distinguish worlds $M$ and $\hat D$ through their
decision points. Therefore, they decide $1$ in world $\hat D$. In particular,
$E$ is nonempty because $p\geq1$, so at least one correct party decides $1$.
The parties in $C$ cannot distinguish worlds $\hat D$ and $V$ through the good
case decision point. Therefore, they decide $0$ in world $\hat D$.

### The contradiction

World $\hat D$ has only $f$ Byzantine parties and no crash faults, yet correct
parties decide different values. This violates agreement.

To group the indistinguishability claims: first, $B,E$ cannot distinguish
worlds $M$ and $\hat D$, which moves the decision $1$ from $M$ to $\hat D$.
Second, $C$ cannot distinguish worlds $\hat D$ and $V$ through its decision
point, which moves the decision $0$ from $V$ to $\hat D$. The two links force
conflicting decisions in the same execution.

This contradicts the assumption that the protocol has good case latency of
two rounds.

### Notes

* For randomized protocols with always-correct agreement and validity and
  almost-sure termination, choose a value decided in $M$ with positive
  probability (at least one half for binary decisions). There is then a
  finite time $T$ by which that value is decided with positive probability.
  Couple the random choices in the indistinguishable views and set GST in
  the corrupt world later than both $T$ and $2\delta$. The same construction
  violates agreement with positive probability. This avoids choosing GST
  based on an unbounded wait for a randomized decision.

* The parameter $p$ removes the even or odd case distinction that appears in
  the original proof of
  [Hydrangea](https://eprint.iacr.org/2025/1112.pdf). The sets $A$ and $E$ both
  contain $p$ parties, while $C$ contains $f-1$ Byzantine parties and all $c$
  crash faulty parties in the mixed world. The sets $B$ and $D$ stay at size
  $f-1$.

* The proof requires a Byzantine leader, so the theorem assumes $f\geq1$.
  When $f=0$, no leader can equivocate and two round crash tolerant consensus
  is possible with $n=2c+1$. More generally, if there is a way to prevent even
  a Byzantine leader from equivocating, then a two round good case is possible
  already with $n=3f+2c-1$. [Alpenglow][alpenglow] obtains the closely related
  bound $n=3f+2c+1$ under its [Assumption 3][alpenglow-assumption-3], which
  prevents the leader from equivocating. It tolerates $f+c$ faults and its fast
  path finalizes when $n-p$ parties participate. Thus, the Byzantine and crash
  only cases do not meet continuously at $f=0$ because the lower bound relies
  specifically on a Byzantine leader equivocating.

* In their unpublished technical report
  [*Best-Case Complexity of Asynchronous Byzantine Consensus*][dgv],
  Partha Dutta, Rachid Guerraoui, and Marko Vukolić give the bound
  $N_a>2Q+F+2M-2$ in Proposition L.4 (Section 4.2, page 19).
  In their notation, $N_a$ is the number of acceptors, $M$ bounds malicious
  acceptors, $F$ bounds total acceptor failures tolerated for liveness, and
  $Q$ bounds failures tolerated in the two round good case. Taking
  $M=f$, $F=f+c$, and $Q=p$ gives $n>3f+c+2p-2$.
  Their formulation distinguishes proposers, acceptors, and learners, with
  the privileged proposer also counted as an acceptor. Their proof uses a
  learner that decides and then crashes. Here, the parties in $C$ decide
  and remain correct in the corrupt world, while their outgoing messages
  are delayed. The report is EPFL I&C Technical Report 200499, revised
  February 2005.

* [Hydrozoan][hydrozoan], by Qianyu Yu, Lefteris Kokoris-Kogias, and
  Alberto Sonnino, studies the same tradeoff in DAG-based consensus. Its
  basic construction uses $n=3f+c+2p+1$ validators and combines a two round
  fast path tolerating $p$ faults with a three round path under the full
  fault bounds. Section VI presents **Optimal-Hydrozoan**, a variant with
  $n\geq3f+c+2p-1$, subject also to $n\geq3f+2c+1$. 

Your thoughts/comments on [X](TBD).

[dgv]: https://lpdwww.epfl.ch/upload/documents/publications/567931850DGV-feb-05.pdf
[three-round-bft]: https://decentralizedthoughts.github.io/2025-11-22-three-round-BFT/
[anrz21]: https://arxiv.org/abs/2102.07240
[ktz21]: https://arxiv.org/abs/2102.12825
[hydrozoan]: https://sonnino.com/papers/hydrozoan.pdf
[alpenglow]: https://www.anza.xyz/blog/alpenglow-a-new-consensus-for-solana
[alpenglow-assumption-3]: https://drive.google.com/file/d/1RPJ9OyohFMuFfLmTB5ydPYlrKTIlUxq9/view?usp=sharing
