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

The leader's **monopoly** over both *construction* and *proposal* of the input creates a **censorship** problem: A malicious leader can ignore inputs from other parties (censor them). In blockchain systems this corresponds to validators excluding user transactions for profit (MEV). Censorship-resistant protocols break this monopoly by decoupling input construction and proposal: An *input* party $I$ holds the value to be committed, while another party, the *expediter* $E$, is in charge of driving a low-latency commit.


So the traditional validity and good-case latency can be replaced by:

1. **Censorship resistance**: if $I$ is honest and the network is synchronous (GST=0), $I$'s input value is eventually decided by all honest parties.
2. **Good-case latency**: if $E$ is honest and the network is synchronous (GST=0), all honest parties decide within $k$ rounds.

Naively, $k=4$ seems achievable: $I$ sends its value to $E$ in round 1, and an honest $E$ commits in 3 more rounds (the minimum, by the [3-round lower bound](https://decentralizedthoughts.github.io/2025-11-22-three-round-BFT/) above). But a malicious $E$ can claim it heard nothing and commit an empty value. The [fix](https://decentralizedthoughts.github.io/2026-03-23-strong-chain-quality/) is for $I$ to broadcast its value to *all* parties that then add this value to their *inclusion list*. Now $E$ cannot censor, but doing this takes an additional round. This suggests $k=5$, and we show this is tight (when the number of faults is more than $n/5$).

> In partial synchrony, the best achievable good-case latency is $k=5$ rounds, two more than standard BFT.

## The result: the latency cost of censorship resistance

**Theorem**: *Any protocol satisfying censorship resistance that solves consensus in partial synchrony with $n \leq 5t-6$ and $t \geq 4$ requires good-case latency at least $5$ rounds.*


Assume for contradiction that protocol $\Pi$ achieves censorship resistance with good-case latency $k = 4$: whenever the expediter $E$ is honest and GST $= 0$, all honest parties decide within $4$ rounds. We derive a contradiction that relies on two prior results: the [AS-FFD technique](https://decentralizedthoughts.github.io/2024-01-28-early-stopping-lower-bounds/) and the [3-round lower bound](https://decentralizedthoughts.github.io/2025-11-22-three-round-BFT/) for Byzantine broadcast.

## Proof Part 1: reaching round 3 with $E$ as a pivot

Part 1 sets GST $= 0$ throughout. Two configurations are **almost same (AS)** if they agree on every party's state except possibly one. They are **failure-free different (FFD)** if their failure-free extensions decide distinct values.

**Round 1: the pivot is $I$.** Assume $I$ holds input $v$ and consider the two initial configurations:

- $C_v$: $I$ is non-faulty.
- $C_\bot$: $I$ crashes at the beginning of the execution and recovers at the beginning of round 2, holding input $\bot \neq v$.

We claim that if $k=4$ then $C_\bot$ cannot decide $v$ by round 4. If it did, since $I$ sent nothing in round 1, $E$ must have learned $v$ from other parties by the end of round 2 and would then drive a decision in only 2 more rounds, contradicting the 3-round lower bound for Byzantine broadcast. Therefore, $C_v$ and $C_\bot$ are AS and FFD. So $I$ is the **initial pivot**.

**Round 2: the pivot is not $E$.** Label $I$'s outgoing round 1 messages $m_1, \ldots, m_n$ to recipients $r_1, \ldots, r_n$, placing $E$ *last*. Let $\alpha^i$ be the execution where $I$ sends $m_1, \ldots, m_i$ and omits the remaining round 1 messages (but continues participating normally in later rounds). Since $\alpha^0$ is indistinguishable from $C_\bot$ through round 1 (both have $I$ sending nothing), so $\alpha^0$ also decides $\bot$; and $\alpha^n$ corresponds to $C_v$ (decides $v$), let $i^\star$ be the smallest index such that $\alpha^{i^\star}$ decides $v$ but $\alpha^{i^\star-1}$ decides $\bot$, and let $p = r_{i^\star}$.

We claim $p \neq E$. Suppose $p = E$. Then $\alpha^{i^\star-1}$ has $I$ sending to all parties except $E$ (omitting only $m_{i^\star}$), yet decides $\bot$. Now consider an execution where $I$ is honest and sends to all $n$ parties, while $E$ is Byzantine and follows the same behavior as in $\alpha^{i^\star-1}$ (which $E$ can do faithfully, since it received nothing from $I$ there). Every honest party's view is identical to $\alpha^{i^\star-1}$, so honest parties decide $\bot$. But $I$ is honest with input $v$, violating censorship resistance. Therefore, $p \neq E$.

So we have found an omission fault for $I$ that makes $p$ the pivot of round 2. We now show that $E$ is the pivot of round 3.

**Round 3: the pivot must be $E$.** Consider the interpolation on $p$'s round 2 messages, again placing $E$ last: start with $p$ sending to nobody (decides $\bot$) and introduce $p$'s round 2 messages one at a time. We claim $E$ is the first and only pivot of round 3.

Seeking a contradiction: Prior to introducing $p$'s message to $E$, assume that after introducing $p$'s message to a party $q\neq E$, the failure free decision flips from $\bot$ to $v$. At this point, the adversary has used three omission failures, so from the [$\min \{f+2,t+1\}$ early stopping](https://decentralizedthoughts.github.io/2024-01-28-early-stopping-lower-bounds/) lower bound, by the early-stopping lower bound, $f=3$ crash faults require at least $f+2=5$ total rounds to decide, contradicting the good-case latency of $k=4$. So $E$ must be the only pivot of round 3.

So we obtain the following **AS-FFD** pair:

- **World $W^-$**: $I$ sent to $r_1, \ldots, r_{i^\star}$ and omitted to the remaining parties; $p$ omits its round 2 message to $E$; all other round 1 and round 2 messages are delivered. We know that the decision in the failure-free extension of $W^-$ is $\bot$.
- **World $W^+$**: $I$ sent to $r_1, \ldots, r_{i^\star}$ and omitted to the remaining parties; all other round 1 and round 2 messages are delivered. We know that the decision in the failure-free extension of $W^+$ is $v$.

Note that in $W^+$, $p$ is failure-free, and in $W^-$, $E$ is the only witness to $p$'s fault.

## Proof Part 2: Crash Augmentation

The 3-round lower bound uses two validity worlds with different crash sets of $t'=t-1$ parties. We construct $W^{--}$ from $W^-$ by crashing $p$ and then $t'-1$ non-$E$ parties one by one to obtain a set $C$ of crashed parties. We construct $W^{++}$ from $W^+$ by crashing $t'$ non-$C$ and non-$E$ parties one by one.

If crashing any such party in round 3 flips the decision, then we have a round 3 bivalent pair with non-$E$ pivot. This implies that a decision cannot be reached in round 4 because this round 3 pivot may have omission faults (decision cannot happen one round after a bivalent pivot).

So the remaining case is that crashing any such party in round 3 does not flip the decision. In this case, we have the following two worlds:

- **$W^{--}$**: crash a set of $t'$ validators that includes $p$. Decides $\bot$.
- **$W^{++}$**: crash a different set of $t'$ validators. Decides $v$.

## Proof Part 3: Three rounds are needed starting from round 3

The [3-round lower bound](https://decentralizedthoughts.github.io/2025-11-22-three-round-BFT/) for Byzantine broadcast constructs 5 worlds. Two of them are the validity worlds $W^{--}$ and $W^{++}$ above. In all these worlds, $I$ is omission-faulted, so we have $t'=t-1$ faults to place. The other three worlds are essentially a mix of $W^{--}$ and $W^{++}$, obtained by a malicious $E$ and additional $t'-1$ Byzantine faults. So the total number of faults is $t$ ($t'-1=t-2$ plus one for $E$ and one for $I$); moreover, the number of parties is $n'=n-1$ as these worlds are obtained by crashing $I$.

Since the 3-round lower bound shows that no decision can be reached in round 4 starting from $W^{--}$ and $W^{++}$, we have a contradiction to the good-case latency of 4.

Finally, note that the 3-round lower bound requires $n' \leq 5t'-2$, which gives us $n-1 \leq 5(t-1)-2$, or $n \leq 5t-6$. For more details see our full version on the [latency cost of censorship resistance](https://eprint.iacr.org/2025/2136). 

## Notes

The fact that any protocol that provides censorship resistance requires some execution with good-case latency of at least $5$ rounds holds also for randomized protocols. By guessing the pivot in each round, the probability of reaching 5 rounds is at least $n^{-O(1)}$. This does not preclude the possibility of a randomized protocol that achieves expected good-case latency of $4+\epsilon$, which remains an open question.

## Acknowledgments

We thank Tim Roughgarden for suggesting the problem of the latency cost of censorship resistance and for his insightful feedback.

Your thoughts on [X](TBD).
