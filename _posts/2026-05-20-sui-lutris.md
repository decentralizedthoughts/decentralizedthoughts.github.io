---
title: "Lutris: Safe Composition of Broadcast and Consensus"
author: Lefteris Kokoris Kogias, Alberto Sonnino
date: 2026-05-20 14:29:56 +0300
description: "Hybrid protocol composing Byzantine consistent broadcast with BFT consensus (Mysticeti) for low-latency single-writer paths."
tags:
- consensus
- broadcast
- blockchain
---

---

> **TL;DR** Lutris is a hybrid distributed system protocol that integrates Byzantine Consistent Broadcast with a BFT consensus DAG to minimize latency of specific types of transactions.
>
> - **Hybrid Consistency:** Uses broadcast for single-writer operations and consensus for shared-state contention.
> - **Unified State Machine:** Maintains linearizability across both paths via versioned object locking.
> - **Liveness Recovery:** Solves the "eternal lock" problem of previous broadcast protocols using epoch-based reconfiguration.
> - **Hybrid Reconfiguration:** Leverages the consensus path to safely rotate the validator set of the broadcast path without service interruption.

---

In distributed systems, there is a fundamental trade-off between **latency** and **ordering**. Total ordering, via consensus, is [expensive](https://decentralizedthoughts.github.io/2019-08-16-byzantine-agreement-needs-quadratic-messages/) and [slow](https://decentralizedthoughts.github.io/2025-11-22-three-round-BFT/), while partial ordering, via broadcast, is linear and fast but limited in expressivity. 

**Lutris** is a distributed system protocol designed to bridge this gap. It avoids the "consensus-for-everything" approach and instead composes two distinct protocols: a **Consistent Broadcast** implementation for owned assets and a **BFT Consensus** (see [Mysticeti](https://decentralizedthoughts.github.io/2026-03-06-mysticeti-revolutionizing-consensus-on-sui/)) for shared state.

This post dissects how Lutris safely composes these protocols and solves the resulting liveness and reconfiguration challenges.

## The System Model: Objects and Versions

To understand Lutris, start with its state model. Unlike the account-based model or the UTXO model, Lutris operates on **Versioned Objects**.

- Every object has a unique ID and a version number $v$.
- A transaction takes a set of input objects $\{O_1(v_a), O_2(v_b), \ldots\}$ and produces a set of output objects with strictly higher versions.
- **Single-Writer Objects:** Objects owned by a specific address. Only that address can sign transactions mutating them.
- **Shared Objects:** Objects that can be mutated by any user.

This distinction allows Lutris to apply different consistency requirements to different transactions.

## The Dual-Path Architecture

Lutris routes transactions based on the contention level of their inputs.

### 1. The Broadcast Path (Single-Writer)

If a transaction involves only single-writer objects, it is [causally independent of other transactions](https://decentralizedthoughts.github.io/2022-12-27-set-replication) (barring double-spends by the owner). Lutris treats this as a **Byzantine Consistent Broadcast** problem.

1. **Proposal:** The user sends the transaction to validators.
2. **Locking:** Each validator checks if the input object versions match the current state and are unlocked. If so, it locks the inputs and returns a signature.
3. **Certification:** Once the user collects $2f+1$ signatures, a certificate is formed.
4. **Finality:** This certificate is effectively the commit message. It allows the user to execute the transaction immediately without waiting for consensus.

This path achieves the theoretical minimum latency ($1$ RTT).

### 2. The Consensus Path (Shared Objects)

If a transaction involves shared objects, total ordering is required to resolve race conditions.

1. **Submission:** The user submits the transaction (or certificate) to the consensus engine.
2. **Ordering:** The consensus engine globally orders transactions (total order).
3. **Execution:** Transactions are then executed in that determined order, updating the object versions.

![Sui_Architecture](/uploads/lutris.png)


## The Composition Challenge: Safety via Versioned Locking

The core innovation of Lutris is not running these two paths per se, but safely **composing** them. A naive implementation could allow a double-spend where one branch uses the broadcast path and another uses the consensus path.

Lutris enforces safety via a **Unified Locking Table** residing on each validator.

- **The Rule:** A validator $V$ will only sign a transaction $T$ (or vote for a consensus block containing $T$) if the input objects $O(v)$ are currently unlocked at version $v$.
- **The State Transition:** Upon signing (or voting), the validator updates its local state to mark $O(v)$ as locked.

Because both the broadcast path and the consensus path must acquire locks from the same local table, and because acquiring a lock requires $2f+1$ quorum participation, safety is guaranteed. A confirmed fast-path transaction effectively "burns" the input versions, making them invalid for any subsequent consensus transaction.

## Liveness and Reconfiguration

Previous broadcast-only systems suffered from a critical liveness issue: **Equivocation Locking**. If a malicious or buggy client attempts to double-spend an asset, the validators would lock their inputs indefinitely, freezing the funds forever. 

Lutris solves this by integrating **Epoch-Based Reconfiguration**.

### The "Unlock" Mechanism

At the end of every epoch (typically 24 hours), the system undergoes a reconfiguration protocol. This acts as a global "garbage collection" event for locks.

First, validators stop signing new broadcast transactions and submit all pending certificates to the consensus engine. Once $2f+1$ validators have signaled that they are finished, the next consensus checkpoint becomes the final checkpoint for the epoch. It represents the canonical history of that epoch. Then, the system transitions to the new epoch and **all locks on objects that were not consumed by a final certificate are released.** This ensures that even if a client equivocates and locks their objects, the lock is only temporary. At the epoch boundary, the "uncommitted" lock is cleared, restoring liveness to the asset.

### Hybrid Reconfiguration

The unique challenge Lutris solves is not just changing the committee, but determining *exactly which* transactions are finalized at epoch $E$ versus epoch $E+1$, given that broadcast transactions are asynchronous to consensus.

Lutris solves this by using the consensus engine to enforce a hard boundary:

1. **Consensus as a Clock:** The system uses the total ordering of the consensus path to reach agreement on the exact moment the epoch ends (the reconfiguration commit).
2. **State Snapshot:** This commit creates a checkpoint containing the effects of all finalized broadcast transactions up to that moment.
3. **Safe Handover:** The new committee of epoch $E+1$ is initialized using this checkpoint. This guarantees that no fast-path transaction from the old epoch can be replayed or double-spent in the new epoch, providing a provably safe reconfiguration for a system that otherwise lacks a global clock.

## Conclusion

Lutris demonstrates that one does not need to choose between the low latency of broadcast and the expressivity of consensus. By formally modeling the interaction between single-writer and shared state, Lutris allows the system to run at the speed of the network for the majority of traffic (payments, NFT transfers), while falling back to consensus speed only when strictly necessary.

For the formal proofs of safety and liveness, refer to the [Lutris paper](https://arxiv.org/abs/2310.18042) (Best Paper Award @ CCS 2024).
