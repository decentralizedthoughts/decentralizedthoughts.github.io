---
title: Latency cost of censorship resistance
date: 2026-04-23 05:00:00 -05:00
tags:
- consensus
author: Ittai Abraham, Yuval Efron, and Ling Ren
---



This post covers our new lower bound on the [latency cost of censorship resistance](https://eprint.iacr.org/2025/2136). In a traditional BFT protocol, the *leader* has two roles: (1) It *constructs* (and therefore holds) the input; and (2) It *proposes* the input. Many BFT protocols optimize for the *good case* when the leader is honest. For [partial synchrony](https://decentralizedthoughts.github.io/2019-06-01-2019-5-31-models/), with $n \leq 5f-2$ parties, the [good-case latency is 3 rounds](https://decentralizedthoughts.github.io/2025-11-22-three-round-BFT/). 

The leader's **monopoly** over both construction and proposal of the input creates a **censorship** problem: A malicious leader can ignore client inputs and substitute its own choice. In blockchain systems this corresponds to validators excluding user transactions for profit (MEV). Censorship-resistant protocols break this monopoly by decoupling input construction and proposal: A *client*, the *input holder* $I$, holds the value to be committed, while a validator, the *expediter* $E$, drives the commit. The fault budget $f$ counts only validator faults; client faults are not charged against it. The traditional [good-case latency](https://arxiv.org/abs/2102.07240) and validity desiderata now split in two:

1. **Censorship resistance**: if $I$ is honest and the network is synchronous (GST=0), its value is eventually decided by all honest parties.
2. **Good-case efficiency**: if $E$ is honest and the network is synchronous (GST=0), all honest parties decide within $k$ rounds.

Naively, $k=4$ seems achievable: $I$ sends its value to $E$ in round 1, and an honest $E$ commits in 3 more rounds (the best we can do give the 3 round lower bound). But a malicious $E$ can claim it heard nothing and commit an empty value. The fix is for $I$ to broadcast its value to *all* parties so that $E$ cannot hide it, which takes an additional round. This suggests $k=5$, and we show this is tight.

> In partial synchrony, the best achievable good-case latency is $k=5$ rounds, two more than standard BFT.

The [MCP protocol](https://eprint.iacr.org/2025/1772) of Garimidi, Neu, and Resnick achieves this bound. Our result shows the 2-round overhead is *inherent*: no censorship-resistant BFT protocol with $n \leq 5f-2$ can do better, regardless of design.

## The result: the latency cost of censorship resistance

**Theorem**: *Any protocol that solves consensus in partial synchrony for $n \leq 5f-6$ and satisfies censorship resistance requires good-case latency at least $5$ rounds.*

The threshold $n \leq 5f-6$ (vs. $n \leq 5f-2$ for standard BFT) reflects a structural cost of censorship resistance: the proof requires an extra validator $p$ as a round-2 pivot distinct from $E$. Partitioning the $n$ validators into $E$, $p$, and five groups of sizes $f-1, f-2, f-2, f-2, f-1$ gives $n = 2 + 2(f-1) + 3(f-2) = 5f-6$.

Assume for contradiction that protocol $\Pi$ achieves censorship resistance with good-case latency $k = 4$: whenever the expediter $E$ is honest and GST $= 0$, all honest parties decide within $4$ rounds. We derive a contradiction. We rely on two prior results: the [AS-FFD technique](https://decentralizedthoughts.github.io/2024-01-28-early-stopping-lower-bounds/) and the [3-round lower bound](https://decentralizedthoughts.github.io/2025-11-22-three-round-BFT/) for Byzantine broadcast.

## Proof Part 1: The expediter is not the round-2 pivot

Part 1 sets GST $= 0$ throughout. Step 1 uses censorship resistance to trace the round-1 AS-FFD pivot to a validator $p \neq E$; Step 2 uses the expediter property to show the round-2 pivot is a message to $E$. Throughout, $I$ is a client sending only in round 1; its faults do not consume the validator fault budget. (Since $\Pi$ tolerates $f$ Byzantine validator faults, it tolerates crash and omission failures as special cases.)

Two configurations are **almost same (AS)** if they agree on every party's state except possibly one. They are **failure-free different (FFD)** if their failure-free extensions decide distinct values.

**Initial AS-FFD pair.** Consider the two initial configurations:

- $C_v$: $I$ holds input $v$; all others hold their default initial state.
- $C_\bot$: $I$ is absent (equivalently, has no input); all others hold the same state as in $C_v$.

$C_v$ and $C_\bot$ are AS (they differ only in $I$'s state) and FFD: from $C_v$ the failure-free execution decides $v$ (by censorship resistance), and from $C_\bot$ it decides some $\bot \neq v$ (by liveness). The only party whose state differs is $I$, so $I$ is the **initial pivot**.

**Step 1: tracing the pivot through round 1.** Label $I$'s outgoing round-1 messages $m_1, \ldots, m_n$ to recipients $r_1, \ldots, r_n$ in any order. Let $\alpha^i$ be the execution where $I$ sends $m_1, \ldots, m_i$ and omits the remaining messages (but continues participating normally in later rounds). Since $\alpha^0$ corresponds to $C_\bot$ (decides $\bot$) and $\alpha^n$ corresponds to $C_v$ (decides $v$), there is a smallest $i^\star$ such that $\alpha^{i^\star}$ decides $v$ but $\alpha^{i^\star-1}$ decides $\bot$. Let $p = r_{i^\star}$.

We claim $p \neq E$. Suppose $p = E$. Then $\alpha^{i^\star-1}$ has $I$ sending to all parties except $E$ (omitting only $m_{i^\star}$), yet decides $\bot$. Now consider an execution where $I$ is honest and sends to all $n$ parties, while $E$ is Byzantine and follows the same behavior as in $\alpha^{i^\star-1}$ (which $E$ can do faithfully, since it received nothing from $I$ there). Every honest party's view is identical to $\alpha^{i^\star-1}$, so honest parties decide $\bot$. But $I$ is honest with input $v$, violating censorship resistance. Therefore $p \neq E$.

Since $p \neq E$, party $E$ has the same round-1 state in both $\alpha^{i^\star-1}$ and $\alpha^{i^\star}$. The end-of-round-1 configurations form the **round-1 AS-FFD**, with $p$ as the sole differing party and $E$ in the same state in both executions.

**Step 2: the round-2 pivot is a message to $E$.** Unlike step 1, this is less of a step and more just an assumption we can make w.l.o.g. As otherwise, the proof is straightforward! Since $p$ is the sole differing party in the round-1 AS-FFD pair, the only round-2 messages that can differ between the two executions are sent by $p$.

Consider the AS-FFD interpolation on $p$'s round-2 messages, placing $E$ last: start with $p$ sending to nobody (decides $\bot$) and introduce $p$'s round-2 messages one at a time. We claim $E$ is the first and only pivot.

Suppose not: Prior to introducing it to $E$, after introducing $p$'s message to a party $q\neq E$, the decision flips from $\bot$ to $v$. Let $q \neq E$ be the first party whose receiving $p$'s message flips the decision to $v$. Now consider an execution where $I$ is honest *and* $E$ is honest. By censorship resistance, honest parties must decide $v$ regardless of $E$'s behavior, and by good case efficiency they must do so in 4 rounds. Note however that $q$ is a round-2 pivot. From this point, an argument similar to the one found in [AS-FFD technique](https://decentralizedthoughts.github.io/2024-01-28-early-stopping-lower-bounds/) closes out the proof by contradicting good-case efficiency; we omit it from this writeup for brevity.

<!-- Let $X$ denote the parties after $E$ in the ordering. By the same argument, no party in $X$ is a pivot: if $q \in X$ receiving $p$'s message determined the commit, $E$ would again not be essential. Removing $p$'s messages to $X$ therefore preserves both the $\bot$ and $v$ decisions./ -->

Having established that $E$ is the sole pivot, and by setting $E$ last in the order, we obtain the following **round-2 AS-FFD** pair:

- **World $W^-$**: $I$ sent to $r_1, \ldots, r_{i^\star}$ and omitted to the remaining parties; $p$ omits its round-2 message to $E$, and has it delivered to all other parties. Failure-free decision: $\bot$.
- **World $W^+$**: same, except $p$ sends its round-2 message to all parties, including $E$, with the rest being omitted. Failure-free decision: $v$.

Note that in $W^+$, $p$ is failure-free, and in $W^-$, $E$ is the only witness to $p$'s fault.

## Proof Part 2: Replacing failures with asynchrony

The worlds $W^-$ and $W^+$ from Part 1 were constructed using one client fault ($I$'s selective sending in round 1) and one validator omission ($p$'s omission to $E$ in round 2). Since the $f$-fault budget counts only validator faults, $I$'s fault is free. And $p$'s validator omission can be replaced by asynchrony.

Since $\Pi$ is a partial-synchrony protocol, messages can be delayed arbitrarily before GST. Set GST to occur after round 4. Then:

- **$I$'s client fault costs nothing**: $I$ sends only in round 1 (clients don't participate further), so whether we model its selective sending as an omission or a crash is irrelevant to rounds 2 onward. Equivalently, let $I$ be honest but let its messages to parties outside $\{r_1, \ldots, r_{i^\star}\}$ arrive after GST. Since validators count only validator faults toward the threshold $f$, no validator is misled into thinking the fast-deciding path has been vacated.

- **In place of $p$'s omission**: let $p$ be honest, but delay $p$'s round-2 message to $E$ until after round 4. From $E$'s perspective this is indistinguishable from $p$ having omitted the message. Every other validator received $p$'s message on time, so their views are consistent with a synchronous execution.

No validator faults are consumed. The full $f$-fault budget is available for Part 3.

**Crash augmentation.** The 3-round lower bound uses two validity worlds with different crash sets. We construct $W^{--}$ and $W^{++}$ independently. If crashing any validator flips the decision, we obtain a new initial AS-FFD pair; Parts 1 and 2 applied to it yield a new round-2 AS-FFD pair with the full fault budget, giving $k \geq 5$, a contradiction. So WLOG decisions are preserved under crashes.

- **$W^{--}$**: crash a set $A$ of $f$ validators with $p \notin A$. Decides $\bot$.
- **$W^{++}$**: crash $p$ and $f-1$ additional validators $\mathcal{E}'$ (disjoint from $p$), giving crash set $\mathsf{E} = \{p\} \cup \mathcal{E}'$ of size $f$. Decides $v$.

## Proof Part 3: Three rounds are needed starting from round 3

The [3-round lower bound](https://decentralizedthoughts.github.io/2025-11-22-three-round-BFT/) for Byzantine broadcast constructs a mixed world $M$ in which $E$ is Byzantine and proves a contradiction via two cases. In both cases $I$ remains omission-faulted (as a client, this consumes none of the $f$ validator faults), so $M$ may place $E$ as Byzantine and use $f-1$ additional crashes. If $M$ decides $v$: compare $M$ with $W^{--}$ (crash set $A$ of size $f$, decides $\bot$): $I$'s omission and $p$'s behavior in $M$ match $W^-$, making $M$ indistinguishable from $W^{--}$ to one side of the partition. If $M$ decides $\bot$: compare $M$ with $W^{++}$ (crash set $\mathsf{E}$ of size $f$, decides $v$): Byzantine-silent $p$ in $M$ matches the crash in $W^{++}$, making $M$ indistinguishable from $W^{++}$ to the other side. In both cases, $E$ first acts on its new information in round 3 (having received $p$'s message in round 2), so the 3-round lower bound implies parties cannot decide before round $3 + 2 = 5$. This contradicts $k = 4$. $\square$.

For more details see our full version on the [latency cost of censorship resistance](https://eprint.iacr.org/2025/2136). 

## Acknowledgments


Your thoughts on [X](TBD).
