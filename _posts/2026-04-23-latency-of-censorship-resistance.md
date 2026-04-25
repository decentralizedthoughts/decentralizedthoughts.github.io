---
title: Latency cost of censorship resistance
date: 2026-04-23 01:00:00 -05:00
tags:
- consensus
author: Ittai Abraham, Yuval Efron, and Ling Ren
---



This post covers our new lower bound on the [latency cost of censorship resistance](https://eprint.iacr.org/2025/2136). In a traditional [partial synchrony](https://decentralizedthoughts.github.io/2019-06-01-2019-5-31-models/) BFT protocol, the *leader* has two roles: (1) It *constructs* the input; and (2) It *proposes* the input. The natural validity property:

* **Validity**: if the leader is honest and the network is synchronous (GST=0), its input value is eventually decided by all honest parties.

Moreover, it is natural to optimize for the *good-case latency*: 

* **Good-case latency**: if the leader is honest and the network is synchronous (GST=0), all honest parties decide within $\ell$ rounds.


When the number of faults is more than $n/5$, the [good-case latency lower bound](https://decentralizedthoughts.github.io/2025-11-22-three-round-BFT/) proves that the best one can hope for is $\ell=3$ (because obtaining $\ell=2$ is impossible).

The leader's **monopoly** over both *construction* and *proposal* of the input creates a **censorship** problem: A malicious leader can ignore inputs from other parties (censor them). In blockchain systems this corresponds to validators excluding user transactions for profit (MEV). Censorship-resistant protocols break this monopoly by decoupling input construction and proposal: An *input* party $I$, holds the value to be committed, while another party, the *expediter* $E$, is in charge of driving a low-latency commit.


So the traditional validity and good-case latency can be replaced by:

1. **Censorship resistance**: if $I$ is honest and the network is synchronous (GST=0), $I$'s input value is eventually decided by all honest parties.
2. **Good-case latency**: if $E$ is honest and the network is synchronous (GST=0), all honest parties decide within $k$ rounds.

Naively, $k=4$ seems achievable: $I$ sends its value to $E$ in round 1, and an honest $E$ commits in 3 more rounds (the best we can do given the 3-round lower bound when the number of faults is more than $n/5$). But a malicious $E$ can claim it heard nothing and commit an empty value. The [fix](https://decentralizedthoughts.github.io/2026-03-23-strong-chain-quality/) is for $I$ to broadcast its value to *all* parties that then add this value to their *inclusion list*. Now $E$ cannot censor, but doing this takes an additional round. This suggests $k=5$, and we show this is tight (when the number of faults is more than $n/5$).

> In partial synchrony, the best achievable good-case latency is $k=5$ rounds, two more than standard BFT.

## The result: the latency cost of censorship resistance

**Theorem**: *Any protocol that solves consensus in partial synchrony for $n \leq 5f-6$ and satisfies censorship resistance requires good-case latency at least $5$ rounds.*


Assume for contradiction that protocol $\Pi$ achieves censorship resistance with good-case latency $k = 4$: whenever the expediter $E$ is honest and GST $= 0$, all honest parties decide within $4$ rounds. We derive a contradiction that relies on two prior results: the [AS-FFD technique](https://decentralizedthoughts.github.io/2024-01-28-early-stopping-lower-bounds/) and the [3-round lower bound](https://decentralizedthoughts.github.io/2025-11-22-three-round-BFT/) for Byzantine broadcast.

## Proof Part 1: Constructing the round-2 AS-FFD pair

Part 1 sets GST $= 0$ throughout. Two configurations are **almost same (AS)** if they agree on every party's state except possibly one. They are **failure-free different (FFD)** if their failure-free extensions decide distinct values.

**Initial AS-FFD pair.** Consider the two initial configurations:

- $C_v$: $I$ holds input $v$.
- $C_\bot$: $I$ crashes at the beginning of the execution.

$C_v$ and $C_\bot$ are AS (they differ only in $I$'s state) and FFD: from $C_v$ the failure-free execution decides $v$ (by censorship resistance), and from $C_\bot$ it decides some $\bot \neq v$ (by liveness). The only party whose state differs is $I$, so $I$ is the **initial pivot**.

**Round 1: the pivot is not $E$.** Label $I$'s outgoing round-1 messages $m_1, \ldots, m_n$ to recipients $r_1, \ldots, r_n$, placing $E$ last. Let $\alpha^i$ be the execution where $I$ sends $m_1, \ldots, m_i$ and omits the remaining round-1 messages (but continues participating normally in later rounds). Since $\alpha^0$ corresponds to $C_\bot$ (decides $\bot$) and $\alpha^n$ corresponds to $C_v$ (decides $v$), let $i^\star$ be the smallest index such that $\alpha^{i^\star}$ decides $v$ but $\alpha^{i^\star-1}$ decides $\bot$, and let $p = r_{i^\star}$.

We claim $p \neq E$. Suppose $p = E$. Then $\alpha^{i^\star-1}$ has $I$ sending to all parties except $E$ (omitting only $m_{i^\star}$), yet decides $\bot$. Now consider an execution where $I$ is honest and sends to all $n$ parties, while $E$ is Byzantine and follows the same behavior as in $\alpha^{i^\star-1}$ (which $E$ can do faithfully, since it received nothing from $I$ there). Every honest party's view is identical to $\alpha^{i^\star-1}$, so honest parties decide $\bot$. But $I$ is honest with input $v$, violating censorship resistance. Therefore, $p \neq E$.

So we have found an omission fault for $I$ that makes $p$ the round-1 pivot. We now show that $E$ is the round-2 pivot.

**Round 2: the pivot must be $E$.** Consider the AS-FFD interpolation on $p$'s round-2 messages, again placing $E$ last: start with $p$ sending to nobody (decides $\bot$) and introduce $p$'s round-2 messages one at a time. We claim $E$ is the first and only round-2 pivot.

Seeking a contradiction: Prior to introducing $p$'s message to $E$, assume that after introducing $p$'s message to a party $q\neq E$, the decision flips from $\bot$ to $v$. From this point, we have three omission failures, so from the [early stopping](https://decentralizedthoughts.github.io/2024-01-28-early-stopping-lower-bounds/) lower bound, we know that even if $E$ is the round-3 pivot, and even if $E$ is honest, we need at least 2 more rounds for a total of 5 rounds, contradicting the good-case latency of 4. So $E$ must be the only round-2 pivot.

So we obtain the following **round-2 AS-FFD** pair:

- **World $W^-$**: $I$ sent to $r_1, \ldots, r_{i^\star}$ and omitted to the remaining parties; $p$ omits its round-2 message to $E$; all other round-1 and round-2 messages are delivered. We know that the decision in the failure-free extension of $W^-$ is $\bot$.
- **World $W^+$**: $I$ sent to $r_1, \ldots, r_{i^\star}$ and omitted to the remaining parties; all other round-1 and round-2 messages are delivered. We know that the decision in the failure-free extension of $W^+$ is $v$.

Note that in $W^+$, $p$ is failure-free, and in $W^-$, $E$ is the only witness to $p$'s fault.

## Proof Part 2: Crash Augmentation

The 3-round lower bound uses two validity worlds with different crash sets of $f'=f-1$ parties. We construct $W^{--}$ from $W^-$ by crashing $p$ and then $f'-1$ non-$E$ parties one by one to obtain a set $C$ of crashed parties. We construct $W^{++}$ from $W^+$ by crashing $f'$ non-$C$ and non-$E$ parties one by one.

If crashing any such party in round 3 flips the decision, then we have a round-3 bivalent pair with non-$E$ pivot. This implies that a decision cannot be reached in round 4 because this round-3 pivot may have omission faults (decision cannot happen one round after a bivalent pivot).

So the remaining case is that crashing any such party in round 3 does not flip the decision. In this case, we have the following two worlds:

- **$W^{--}$**: crash a set of $f'$ validators that includes $p$. Decides $\bot$.
- **$W^{++}$**: crash a different set of $f'$ validators. Decides $v$.

## Proof Part 3: Three rounds are needed starting from round 3

The [3-round lower bound](https://decentralizedthoughts.github.io/2025-11-22-three-round-BFT/) for Byzantine broadcast constructs 5 worlds. Two of them are the validity worlds $W^{--}$ and $W^{++}$ above. In all these worlds, $I$ is omission-faulted, so we have $f'=f-1$ faults to place. The other three worlds are essentially a mix of $W^{--}$ and $W^{++}$, obtained by a malicious $E$ and additional $f'-1$ Byzantine faults. So the total number of faults is $f$ ($f'-1=f-2$ plus one for $E$ and one for $I$); moreover, the number of parties is $n'=n-1$ as these worlds are obtained by crashing $I$.

Since the 3-round lower bound shows that no decision can be reached in round 4 starting from $W^{--}$ and $W^{++}$, we have a contradiction to the good-case latency of 4.

Finally, note that the 3-round lower bound requires $n' \leq 5f'-2$, which gives us $n-1 \leq 5(f-1)-2$, or $n \leq 5f-6$. For more details see our full version on the [latency cost of censorship resistance](https://eprint.iacr.org/2025/2136). 

## Acknowledgments

We thank Tim Roughgarden for suggesting the problem of the latency cost of censorship resistance and for his insightful feedback.

Your thoughts on [X](TBD).
