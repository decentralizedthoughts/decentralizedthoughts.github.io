---
title: 'Carry: HotStuff Linearity with Tail-Forking-Resilience'
date: 2025-09-27 21:30:00 -04:00
tags:
- BFT
author: Dakai Kang, Suyash Gupta, Dahlia Malkhi, Mohammad Sadoghi
---

The recently identified tail-forking attack shows how malicious leaders can degrade throughput by skipping over honest proposals in streamlined BFT protocols like HotStuff. To address this challenge, we introduce Carry, a lightweight mechanism that preserves HotStuff’s linearity while protecting against tail-forking. Carry also supports commits by honest-but-sluggish leaders whose messages are benignly delayed.

## Synopsis

In a “streamlined” Byzantine Fault Tolerant (BFT) consensus approach, pioneered by [HotStuff](https://api.semanticscholar.org/CorpusID:197644531), the consensus protocol has a simple and uniform structure: each *view* is a single quorum exchange between a leader and voters, and each such exchange carries a new leader proposal. Herein lies a vulnerability exposed in [BeeGees](https://api.semanticscholar.org/CorpusID:256274482): since a single quorum exchange does not suffice to achieve a consensus decision, leaders must rely on the next leader to drive a second exchange that commits the previous proposal. In a *tail-forking* attack, a malicious next leader might skip over the previous leader’s proposal.Repeated attacks by bad leaders may significantly degrade throughput.

The solution presented in BeeGees is to force the next leader to **prove** that it extends the most recent quorum-certified proposal. This proof approach borrows from [PBFT](https://api.semanticscholar.org/CorpusID:221599614), and like it, requires either quadratic communication or computationally heavy SNARKs.

Our recent work ["Carry the Tail in Consensus Protocols"](https://arxiv.org/abs/2508.12173) inroduces **Carry**, a lightweight, drop-in mechanism for streamlined protocols that defends against tail-forking. Notably, Carry incurs only linear communication overhead per view. Not only that, suppose a preceding leader's proposal was benignly sluggish and did not reach all replicas in time. An honest leader in Carry seizes the opportunity to help by *reinstating* the sluggish proposal, without requiring a quorum of votes to certify it. In BeeGees, even if `2F` honest replicas voted for the sluggish proposal, it will not commit. 

Carry is a generic mechanism. We demonstrate its application to HotStuff-2 to create **Carry-the-Tail (Ctail)**, a full consensus solution.

## Overview of Ctail

### Model

The setting for this work is described in the standard BFT in partial synchrony. Briefly, the system consists of `N = 3F + 1` replicas with up to `F` Byzantine faulty, or `F_actual` faulty in an actual execution, `F_actual ≤ F`, and partially synchronous communication. (For a detailed problem model, see the [Carry full paper](https://arxiv.org/abs/2508.12173).)

Carry is the name we give to a generic liveness-boost for protocols in the HotStuff family. A full-fledged application of Carry on HotStuff-2 which is described here is referred to as **Carry-the-Tail (Ctail)**. 

---

### Proposing and Voting

The Ctail protocol operates in a view-by-view manner. Each view `v` has a known designated leader `L_v` performing a single quorum-exchange with replicas. The leader broadcasts a proposal `B_v` to the replicas; replicas respond (subject to safety rules) with a NEW-VIEW message carrying a signature-share on `B_v`. The signature-share is referred to as a *vote* on `B_v`.

A Quorum-Certificate (`QC`) consists of a threshold-signature by a quorum of `2F+1` replicas. We say that the proposal `B_v` is *certified* when a QC for it--`QC(v)`--is formed. To form QCs, leaders collect signature-shares for previous proposals and aggregate them. Broadcasting a QC incurs only linear word-communication complexity. 

---

### Commit Safety and Liveness

Each proposal `B_v` includes an opaque payload and meta-information. The meta-information references a history known to the leader. It includes `B_v.QC`, the highest known certified tail prior to view `v`. Chaining proposals to one another using cryptographic certificates is utilized along with protocol voting and commit rules to ensure **safety**.

<p align="center">
  <img src="/uploads/carry_figure1.png" width="60%" title="carry figure 1">
</p>
**Figure 1: Carry-the-tail basic flow.**

Figure 1 depicts a failure-free flow of the protocol with leader proposals chained to one another via QCs. Upon receiving a proposal `B_v`, a replica becomes *locked* on `B_v.QC`. Locking ensures safety: in the future, the replica pledges it will only accept proposals that extend `B_v.QC` or a QC from a higher view. 

A *commit* requires two consecutive successful views. If a leader `L_v` forms `QC(v-1)` for the proposal `B_v-1`, then the proposal becomes committed once `2F+1` signature-shares on `B_v` form `QC(v)`. Anyone observing a QC on `B_v`, where `B_v.QC = QC(v-1)` learns that `B_v-1` is committed. In Figure 1, `B_1` and `B_2` have been committed.

To guarantee **liveness**, a leader proposes if it received a QC from the immediately preceding view or a timeout. In the latter case, the preceding view is *failed*. The timeout is implemented by a separate view-synchronization (Pacemaker) module;  any (linear) Pacemaker can be plugged here (e.g., [RareSync](https://api.semanticscholar.org/CorpusID:266258469), [Lewis-Pye](https://api.semanticscholar.org/CorpusID:245668696), [Lumiere](https://api.semanticscholar.org/CorpusID:265157987)).

---

### The Problem with Failed Views and Tail-Forking

The problem exposed in BeeGees is that previously, HotStuff lets a leader pretend the preceding view failed by ignoring votes for the preceding proposal. Figure 2 below shows how a malicious `L_3` could exploit this and omit votes for `B_2` to wrongfully skip it. 

<p align="center">
  <img src="/uploads/carry_figure2.png" width="80%" title="carry figure 2">
</p>
**Figure 2: Without tail protection, the two cases here are indistinguishable: on left `B_2` failed and is benignly skipped; and on right, `B_2` is tail-forked.**

More precisely, we say that a view `v` suffers a *tail-forking* attack if `2F+1` signature shares are sent by honest replicas on `B_v`, but the next leader `L_v+1` (intentionally ignores and) does not extend `B_v`. Regardless of the cause, tail-forking causes significant performance degradation:
- Proposals are unnecessarily dropped.  
- Commit latency increases.  
- Throughput can degrade by `O(N)` and latency can increase by `O(N)` if `F` bad leaders are interspersed among honest ones (see Figure 3 below).  

Carry prevents these tail-forking attacks.

---

### Protecting the Tail

In lieu of a vote, replicas in any case must send the next leader a NEW-VIEW message indicating a timer expiration. In this case, Carry piggybcks a signature-share on an empty vote (`⊥`).

A leader *justifies* skipping over a tail `B_v` by attaching (in lieu of a QC) an *Empty Certificate* for v, denoted `EC(v)`, consisting of a threshold signature by `2F+1` replicas on `⊥`. Note that a bad leader cannot succeed in forming an EC if `F+1` honest replicas voted for `B_v`. Figure 3 shows on the left a justified skip over `B2` accompanied by `EC(2)`.

<p align="center">
  <img src="/uploads/carry_figure3.png" width="80%" title="carry figure 3">
</p>
**Figure 3: With Carry protection, on left `B_2` failed and it is skipped via an `EC(2)` justifying skipping it; on right, `B_2` is reinstated.**

---

### Reinstating Uncertified Tails

If there is neither a QC nor an EC, previous solutions (e.g., BeeGees) required leaders to justify skipping the tail with a proof that incorporates information about all votes and resulted in quadratic communication per leader; faced with a worst-case cascade of `F` bad leaders, this could result in cubic communication.

In Carry, a leader can *reinstate* an uncertified tail `B_v` in a `reinstate` reference. Figure 3 shows two scenarios: on left, a justified skip accompanied by an EC; on right, a reinstated, uncertified proposal.

The new proposal inherits from `B_v` its own QC, EC, and/or reinstate references. Care must be taken in order to preserve safety when incorporating these references, e.g., when skipping views between the current proposal and `v`, and between `v` and the highest known QC. For details, see the [Carry full paper](https://arxiv.org/abs/2508.12173). 

We remark that the reinstating mechanism is beneficial also in case the previous leader was benignly sluggish and fell short of obtaining a full quorum or votes. Carry guarantees that even a single vote reaches an honest next leader it can reinstate it.  

---

### ρ-Tail-Resilience

Unfortunately, requiring an EC to skip only the last view would not suffice to protect an honest tail `B_v` against two consecutive bad leaders, `L_v+1` and `L_v+2`: `L_v+1` would not just ignore votes for `B_v`, it would omit proposing anything for view `v+1`. Therefore, replicas would send empty vote-shares for `v+1` and `L_v+2` would form `EC(v+1)` to justify skipping view `v+1`, but would not need to justify skipping `B_v`. Therefore, `L_v+2` could (again) ignore votes for `B_v`, and propose `B_v+2` that extends the highest QC **preceding** view `v`.

To protect against 2--or more generally, against `ρ`--consecutive bad leaders, Carry repeats the tail protection up to `ρ` views preceding the next leader's view. In this way, Carry can protect a tail unless it is followed by `ρ` consecutive bad views with `O(ρN)` word communication.

More specifically, each replica piggybacks on a NEW-VIEW message its own vote-shares (possibly empty) from the last `ρ` views (in addition to its highest locked QC). When a leader proposes, if the highest QC it knows is at most `ρ` views earlier, then it must justify every skipped view back to this QC or to an interim reinstated proposal. Care must be taken to interleave reinstated proposals without blowing the communication overhead. For details, see the [Carry full paper](https://arxiv.org/abs/2508.12173). 

Figure 4 illustates the performance degradation of carry under different choices of `ρ`: For `ρ=0` (top left), there is no tail protection.`ρ=1` (top right) provides defense against a single bad leader at a time, but (bottom left), no tail protection against two consecutive bad leaders each time. Finally, `ρ=2` (bottom right) provides defense against two consecutive bad leaders each time.



<p align="center">
  <img src="/uploads/carry_figure4.png" width="100%" title="carry figure 4">
</p>

**Figure 4: Performance degradation under different choices of `ρ`.**

**ρ-Tail-Resilience** guarantees that in each rotation of `N` leaders, all but `(F_actual / ρ)` proposals are protected from tail-forking. In practice, for modest values of `ρ`, the probability of `ρ` consecutive bad leaders is very small, especially if leader rotation is randomized.

---

### Comparing ρ-Tail-Resilience with AHL

BeeGees defined the **Any-Honest-Leader commit** (AHL) property: after GST, once an honest leader proposes, that block will subsequently be committed as soon as a constant number (e.g., 3 in HotStuff-2) of consecutive views with honest-leaders occur. To achieve this, BeeGees uses a complex leader handover, with quadratic communication or computationally heavy SNARKs. 

Carry’s **ρ-tail-resilience** guarantees that a large constant fraction of honest leader proposals, namely all except `F_actual/ρ`, do become committed even under worst-case tail-forking. By setting `ρ = f`, Carry achieves the same AHL property as BeeGees with the same communication burden. However, arguably Carry has simpler logic and also allows `ρ` to be a tunable parameter in production.

Additionally, an honest leader in Carry may help commit a benignly-sluggish previous proposal which did not reach all replicas. Supporting **sluggish-leaders** may have far-reaching performance benefits on real systems which experience transient network delays.   


|             | honest leader commit       |  word comm. overhead per-view | word comm. overhead worst-case | sluggish-leader commit supported |
|-------------|----------------------------|-------------------------|------------------------------|-------------|
| **BeeGees** [G+ 2022] | always                     |  O(n²) *or SNARK             | O(n³) *or O(n)-SNARKS          | no | 
| **Carry** [GKMS 2025] | All except (F_actual/𝝆)    |  O(𝝆·n)                      | O(𝝆·n²)                        | yes | 


