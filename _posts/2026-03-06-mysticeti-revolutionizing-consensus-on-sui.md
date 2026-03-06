---
title: "Mysticeti: Revolutionizing Consensus on Sui"
date: 2026-03-06 00:00:00 -05:00
tags:
- blockchain
author: Lefteris Kokoris Kogias, Alberto Sonnino, George Danezis
---

---

> TL;DR Mysticeti is a novel Byzantine consensus protocol deployed on the Sui blockchain that revolutionizes transaction processing.
>
> - **Eliminates explicit certification**, reducing good-case latency to the theoretical minimum.
> - **Crash-fault masking**, avoiding head-of-line blocking for pipelined rounds.
> - **40% CPU usage reduction** for consensus in production.
> - **80% latency reduction** compared to Bullshark on Sui Mainnet (from ~1.9s to ~400ms).

---

**Mysticeti** is a novel Byzantine consensus protocol recently deployed on the Sui blockchain. It improves DAG-based consensus in both latency and throughput by lowering the number of rounds per commit and reducing signature generation and verification (i.e., CPU) costs. In this post, we delve into why Mysticeti is currently one of the fastest consensus algorithms in production.

## System Model

Mysticeti is designed for a standard Byzantine Fault Tolerant (BFT) setting consisting of **$n = 3f+1$ validators**, where up to $f$ validators can be Byzantine (arbitrarily malicious).

The protocol operates under [**partial synchrony**](https://decentralizedthoughts.github.io/2019-06-01-2019-5-31-models/):

- **Safety** is guaranteed under **asynchrony**, meaning the protocol remains consistent regardless of network delays.
- **Liveness** relies on **partial synchrony**, meaning the protocol guarantees progress once the network stabilizes (Global Stabilization Time, or GST, is reached).

## The Power of Uncertified DAGs

The key idea behind Mysticeti is to forgo the explicit certification step that previous protocols, like [Bullshark](https://decentralizedthoughts.github.io/2022-06-28-DAG-meets-BFT/), used to achieve equivocation tolerance and block availability. Instead, Mysticeti operates on an **uncertified block DAG**. Mysticeti advances the DAG by receiving $n-f$ messages, not by certifying $n-f$ signatures, hence saving considerable CPU overhead.

Certification alone has a high round-trip overhead and introduces as much latency as a commit in PBFT, the lowest-latency traditional consensus algorithm. Given other overheads, this meant that a [certified DAG](https://decentralizedthoughts.github.io/2025-08-08-DAGs/) could not strictly achieve optimal latency.

Mysticeti introduces three key innovations to solve this:

### 1. Elimination of Explicit Block Certification

In previous systems like [Bullshark](https://arxiv.org/abs/2201.05677), each block required individual certification before being shared, resulting in **3 rounds per block only for certification** as well as **$O(n)$ CPU cost per block for signature generation and verification**. Mysticeti goes without certification, which allows for:

- **Reduced CPU Load:** Validators no longer need to aggregate signatures to form and verify certificates. Instead, they simply sign their blocks and send them. Everyone else receives the block and verifies a single signature.

### 2. Multi-Proposer & Pipelined Rounds

In previous DAG-based protocols, new blocks are proposed at the beginning of each wave, and each wave takes several rounds to commit. The leader proposes a block and includes, as causal dependencies, all uncommitted blocks from prior rounds. This means that a block formed after the beginning of a wave must wait until the beginning of the next wave to be proposed. When the leader is decided, the full subDAG is committed; however, non-leader blocks still experience additional latency compared to the leader block. A second benefit of Mysticeti is removing this bottleneck in the good case:

- **Faster Commits:** Unlike previous algorithms that commit only every few rounds, Mysticeti allows every block to be a potential proposer slot. This enables [the optimal **three round** good-case latency](https://decentralizedthoughts.github.io/2025-11-22-three-round-BFT/) for all blocks.

### 3. Crash-Fault Masking

The faster-commits optimization for every block only works if all proposer slots commit on-time in the pipeline. In the bad case where some candidate proposer slot has a crashed leader, the protocol needs to fall back to wave-by-wave commit. In essence the pipeline algorithm suffers from **head-of-line blocking.**

A novel commit rule enables Mysticeti to detect benign crash faults after $2\Delta+\delta$ and skip them without breaking the pipeline. This minimizes the effect of benign crash faults and allows the optimal good-case latency to be achieved most of the time.

---

## The Protocol: Proposer Slots and Commit Rules

To achieve these goals, Mysticeti introduces the concept of **proposer slots**. A proposer slot represents a tuple `(validator, round, proposal)`, where `proposal` can be either empty or contain the validator's proposal. If the validator is Byzantine, the proposal may contain more than one (equivocating) block. A proposer slot can assume one of three global states: **to-commit**, **to-skip**, or **undecided**. All slots are initially set to undecided, and the goal of the protocol is to classify them as to-commit or to-skip. Different validators might move toward to-commit or to-skip in different rounds, but they will all eventually agree.

### The Direct Decision Rule

How do we commit a block without a certificate? We use the DAG structure itself as a "virtual" certificate.

The rule: a block at round R is committed if:

1. **Layer 1 (Witnesses):** It is referenced by at least $2f+1$ blocks in round $R+1$.
2. **Layer 2 (Confirmation):** Those R+1 blocks are themselves referenced by $2f+1$ blocks in round $R+2$.

**Intuition:** "I see a quorum of witnesses ($R+1$) who all claim to have seen the block ($R$). And I have a quorum of confirmations ($R+2$) proving that the witnesses' claim is stable." This is essentially the [classic PBFT style "two rounds of voting".](https://decentralizedthoughts.github.io/2025-02-14-PBFT/)

**Skip Decision:** A slot is marked *to-skip* if it observes $2f+1$ blocks from round $R+1$ that *do not* reference it.

This pattern allows Mysticeti to commit in **$3\delta$** in the good case, observed in 99% of cases on Sui. Additionally, it skips crashed proposers and resumes the pipeline in **$2\Delta+\delta$.** In production we start with a very small $\Delta \approx \delta$ for efficiency and increase it if we observe a large number of skips.

The figure below illustrates an example of a validator's local view, which we use to present an example run. The validator processes each slot individually, starting from the highest, and applies the Mysticeti direct decision rule. Let’s take the example of L4b. This slot is marked as *to-commit* because each block in the set {L6b, L6c, L6d} causally references the set {L5a, L5b, L5d}, whose blocks in turn each reference L4b. If the direct decision rule fails to classify the block, the validators applies the indirect decision rule (below).
![mysticeti local view](/uploads/mysticeti-local-view.png)

### The Indirect Decision Rule

If neither condition is satisfied, the slot remains *undecided*, and the validator leverages the indirect decision rule:

1. **Find an Anchor:** Search for the lowest slot with round $R$' > $R + 2$ that is already decided by the direct commit rule.
2. **Inherit Decision:** If the anchor is *to-skip* then look for the next anchor. When we find the first anchor marked as *to-commit*, the slot inherits that decision if $2f+1$ blocks link to it; otherwise, it is skipped and not considered a valid proposing slot. Nevertheless, even if there is a single link, it will still get committed as a causal dependency.

For a detailed step-by-step example run and formal proofs, please refer to the [NDSS 2025](https://www.ndss-symposium.org/wp-content/uploads/2025-929-paper.pdf) Mysticeti paper.

---

## **Addressing Challenges of Uncertified DAGs**

While uncertified DAGs offer simplicity and low latency, they come with their own set of challenges. Mysticeti addresses these challenges to maintain robustness under unfavorable conditions.

- **Block Availability:** Although Mysticeti advances the DAG without certification, it still implicitly certifies sub-DAGs by looking for to-commit patterns and only committing implicitly certified sub-DAGs. This maintains robustness for off-the-critical-path synchronization, as anyone can still synchronize blocks that were committed in the same way as in Bullshark.
- **Live Synchronization and Backpressure:** At the critical path of liveness, uncertified DAGs face tradeoffs with certified ones. This area is an active research front for Mysten Labs, where we explore push synchronization (i.e., sending dependencies along with a block proposal to slow nodes) versus pull synchronization (i.e., asking for dependencies when a block proposal is too far ahead). Both approaches have pros and cons, and we plan to combine them with garbage collection, which limits the need to synchronize older dependencies and helps provide backpressure between consensus and execution. Using the natural synchronization backpressure that comes with uncertified DAGs has led to a control system that is easier to understand and more scalable than Bullshark's. This is because it creates a natural negative feedback loop. Our planned garbage collection deployment further bounds the synchronization window, making the resulting system the easiest-to-tune DAG-based consensus to date.
- **Partial Network Failure Resilience:** A final potential criticism is that uncertified DAGs might lose robustness when the network is unstable, since they do not have explicit certificates to propagate between partially disconnected regions. Counterintuitively, this can be a strength: uncertified DAGs can be more robust under partial network failures because they only need one node connected to $2f+1$ peers to maintain liveness, as implicit certification can be relayed instead of explicitly built. In contrast, certified DAGs will completely lose liveness in this scenario.

---

## Performance Implications

Mysticeti exhibits one of the highest performance profiles seen in BFT consensus protocols among $100$ validators.

- **Latency:** $\approx 500$ milliseconds commit latency in world scale experiments.
- **Throughput:** $>100,000$ TPS ($512$B transactions).
- **Scalability:** $>400,000$ TPS with $1.5$s latency.

> Note: These numbers are achieved without reputation-based leader election. The Sui production deployment includes HammerHead for further optimization.
>
![Mysticeti Performance](/uploads/mysticeti-performance.png)

### Real-World Impact on Sui

Mysticeti has been running on the **Sui Mainnet since July 2024**.

- **Latency Reduction:** $80$% decrease ($1900$ms to $400$ms).
![mysticeti sui latency reduction](/uploads/mysticeti-sui-latency-reduction.png)

---

- **CPU Overhead Reduction:** Deployed across $106$ geo-distributed independent validators with immediate reduction in CPU cost (from ~$48$% to ~$29$%).
![mysticeti sui cpu reduction](/uploads/mysticeti-sui-cpu-reduction.jpg)

### Conclusion and Future Directions

Mysticeti represents a significant advancement in DAG-based consensus protocols. By addressing specific bottlenecks in previous approaches, it achieves a compelling balance of latency, throughput, and robustness. As Mysticeti continues to be deployed and tested in real-world scenarios on the Sui blockchain, we anticipate further insights into its performance characteristics and potential applications beyond Sui.

We are already engaged in improving the Mysticeti design and production implementation in various ways, such as:

- **Hammerhead:** which selects the most reliable validators as anchors, lowering the observed latency further.
- **Garbage collection:** which limits the synchronization requirements and the DoS attack surface.
- **Fast-path integration:** which will allow extremely low latency for owned-object transactions.
- **Auto-unlock integration:** which will add equivocation tolerance in seconds instead of epochs, and remove the need to add certification latency in the critical path of shared-object transactions for Sui.
- **Better sync algorithms and DAG dissemination:** which will allow full nodes to experience near-identical latency to validators without the explicit need for execution certificates.
- **Round-jumping:** The Mysticeti protocol does not specify the round-jumping behavior used by some implementations. [Recent work](https://flint.cs.yale.edu/flint/publications/sp26.pdf) shows how round-jumping must be carefully restricted to preserve liveness, providing a formally verified variant of Mysticeti with sound round-jumping semantics.

For more technical information, see the [NDSS 2025 paper](https://www.ndss-symposium.org/wp-content/uploads/2025-929-paper.pdf) and the open-source implementation ([https://github.com/mystenlabs/sui](https://github.com/mystenlabs/sui)).
