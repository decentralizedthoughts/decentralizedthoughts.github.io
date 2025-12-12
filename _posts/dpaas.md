---
title: DPaaS - Improving Decentralization by Removing Relays in Ethereum PBS
date: 2025-12-12 06:00:00 -05:00
tags:
- PBS
author: Chenyang Liu, Ittai Abraham, Matthew Lentz, Kartik Nayak
---


:::success
:bulb: In this blog post, we will explain the core ideas of DPaaS, a side-car protocol that removes centralized and unconditionally trusted relays in current Ethereum Proposer-Builder Separation (PBS). The full paper is on the [eprint](https://eprint.iacr.org/2025/2126).
:::

## PBS and MEV-Boost
[Proposer-Builder Separation (PBS)](https://ethereum.org/roadmap/pbs/) was proposed to mitigate the validator centralization brought by the inequality of mining MEV. PBS is inherently a trade between the proposer and builder, requiring fair exchange with the following properties:
* Failed Trade Privacy: Failed builders should keep their block payload secret.
* Block Availability: The proposer can finally get the whole winning block.
* Block Validity: The block is valid and the proposer can be paid the bid.

Today’s Ethereum relies heavily on a side-car protocol called [MEV-Boost](https://boost.flashbots.net/). MEV-Boost solves the fair-exchange problem by introducing a trusted third party—the relay—which acts as both an auctioneer and an escrow for plaintext blocks. However, this unconditional trust comes with risks: relays become a single point of failure and have already been exploited in practice, enabling [attackers to steal funds from users](https://collective.flashbots.net/t/post-mortem-april-3rd-2023-mev-boost-relay-incident-and-related-timing-issue/1540).

## Efforts to Remove Relays
The community has come to the consensus that relays should be removed. 
[TEE-Boost](https://collective.flashbots.net/t/tee-boost/3741) proposed to eliminate the relay by having builders run Trusted Execution Environments (TEEs) to enable the proposer to validate the block without seeing the contents via attestations. However, it only addresses block validity for fair exchange, while the tension between data availability and builder privacy remains unsolved.

Based on TEE-Boost, a [post by Paradigm](https://www.paradigm.xyz/2024/10/removing-the-relays) proposed to leverage a validator committee for [Silent Threshold Encryption](https://www.paradigm.xyz/2024/10/removing-the-relays). This can guarantee fair exchange, but it requires changing Ethereum's consensus layer and is at odds with the Dynamic Availability property in Ethereum.

[Enshrined PBS (ePBS)](https://eips.ethereum.org/EIPS/eip-7732) aims to bring MEV-Boost into the protocol and eliminate relays, but it still faces key limitations—builder staking excludes smaller builders, [p2p-based auctions may reduce throughput and miss profitable bids](https://ethresear.ch/t/builder-bidding-behaviors-in-epbs/20129), and its [single-bid design](https://ethresear.ch/t/builder-bidding-behaviors-in-epbs/20129) prevents [bid cancellations](https://ethresear.ch/t/bid-cancellations-considered-harmful/15500) and more advanced bidding strategies. These constraints suggest that, even in an ePBS world, the ecosystem will continue to demand side-car bidding. A decentralized, secure, and efficient alternative to relay-based MEV-Boost is therefore still needed.

## Decentralized Proposer-as-a-Service
To meet the community’s demand to remove relays and at the same time address the shortcomings of earlier solutions, we propose [Decentralized Proposer-as-a-Service (DPaaS)](https://eprint.iacr.org/2025/2126). Our insight is to decentralize the combined roles of the proposer and relay among a DPaaS instance consisting of different Proposer Entities (PEs). The DPaaS instance now is not only the auctioneer and escrow for bidding, but also the proposer. 

<figure style="text-align: center;">
  <img src="https://hackmd.io/_uploads/Hk0atbHGbx.svg" width="100%">
  <figcaption><em>Figure 1: Overview of DPaaS and its comparison with relay-based MEV-Boost.</em></figcaption>
</figure>


The PEs are requried to run on different TEEs across different availiability zones to provide isolated faulty. We assume $f$ out of $n=5f-1$ PEs can be compromised, which is a much stronger threat model than current MEV-Boost design with relays. Though TEEs are relative harder to be compromised, we adapt such a security-in-depth approach in case some TEEs are compromised due to side-channels or a privileged attacker (e.g. malicious host of the PE). 

On the builder side, to achieve a better trade-off between security and performace, we choose to add a minimal software component called Builder TEEs (BT) based on some trusted hardware. BT is trusted for integrity, which means it can run some attested code that can validate blocks and generate TEE proofs. This is akin to TEE-Boost, but we reduced the TCB significantly by excluding the builder software.

### Challenges
To realize DPaaS and make it a secure and efficient side-car for current Ethereum, several challenges remain:
1. How to obtain full compatibility with Ethereum’s existing consensus protocol, by appearing as a single entity (i.e., tied to one public key) with respect to the rest of the Ethereum network, despite being distributed across multiple TEEs?
2. How to maintain security guarantees for ensuring fair exchange despite the presence of a small fraction of faulty TEEs and/or partially synchronous
networks? 
3. How to achieve performance comparable to existing centralized, relay-based systems, ensuring that its decentralized design remains practically deployable without compromising efficiency?

## Solution to Challenge 1
### BLS Signature Scheme
Thanks to [BLS signatures](https://eth2book.info/latest/part2/building_blocks/signatures/)—which are used by Ethereum and naturally support both [aggregation](https://crypto.stanford.edu/~dabo/pubs/papers/BLSmultisig.html) and [thresholding](https://eprint.iacr.org/2002/118)—a group of PEs can jointly produce a single, standard-looking validator signature. This allows DPaaS to plug into today’s Ethereum validator ecosystem without changing how signatures are verified.

During an offline setup, each PE$_i$ can independently generate BLS key pairs ($sk_V^i$/$pk_V^i$). They then exchange their public keys and combine them into a single aggregated validator public key: $pk_V = \sum_{i=0}^{n-1}pk_V^i$ by sharing $pk_V^i$ with each other during offline setup. Using a Threshold Signature Scheme (TSS) with threshold $f+1$, any subset of $f+1$ honest PEs can collaboratively produce a partial signature on the same message. These partial signatures interpolate into one final BLS signature $\sigma$ that verifies under the aggregated key $pk_V$—exactly the way a normal validator signature does. From the outside, a DPaaS Instance of $n$ PEs can appear as one validator on the network.

## Solution to Challenges 2 & 3 


### In-Auction Bidding & Post-Auction Recovery
A fundamental challenge in fair exchange is balancing Failed Trade Privacy (failed builders must not leak their block contents) with Block Availability (the winning block must always be recoverable). If a builder reveals its block early to guarantee availability, it risks exposing its strategy in the event that it loses the auction.

DPaaS breaks this tension by introducing Builder TEEs (BT). We make the BT validate every block built in builder software. If validation succeeds, it generates a TEE proof (i.e., attestation) and secret shares the block with the PEs. The secret shares of the block, TEE proof, and some public data (e.g. block header) forms the block package which effectively hides the block contents during auction. Moreover, as the BT is trusted for integrity, Block Validity is inherently guaranteed.

At the end of the auction, PEs should recover the winning block and propose it. The secret sharing and BLS TSS ensures that eventually any $f+1$ PEs can reconstruct the block and interpolate the signature. However, this is not sufficient to guarantee the remaining two properties: Failed Trade Privacy & Block Availability. Essentially, we should make sure **all honest/uncompromised PEs can correctly help with the same and only winner's block reconstruction and signature interpolation**, while Byzantine/compromised PEs can't tamper with availability and recover more blocks. That is precisely where **consensus** becomes necessary.

### Consensus to Determine the Winner
To achieve consensus, one final challenge remains: the potential for inconsistent views at the end of the auction. Factors such as [bid cancellations](https://ethresear.ch/t/empirical-analysis-of-builders-behavioral-profiles-bbps/16327), Byzantine PEs, and asynchronous network delays can cause different PEs to observe divergent bidding histories—and, as a result, to compute different local winners.

To reconcile these divergent views and agree on a single final winner, we build our design on top of the [$(5f-1)$-psync-VBB protocol](https://decentralizedthoughts.github.io/2021-03-03-2-round-bft-smr-with-n-equals-4-f-equals-1/). We rely on this protocol solely for its low latency—in our setting with $n = 4$, it is equivalent to a $3f+1$ protocol. Otherwise, with just one additional round, a standard $3f+1$ protocol would suffice. Our key design choice is to have all PEs first agree on a shared set of local views using this base protocol, and then apply a deterministic function to that agreed-upon set to derive the final winner. 

### Parallel handling of reconstruction and signing
In Ethereum today, the proposer signs only the root hash of the block. This root can be derived either by knowing all block fields in plaintext or by knowing the hash-tree roots of those fields. Our design leverages this [property](https://eth2book.info/capella/part2/building_blocks/merkleization): the BT supplies only the **root of the block payload**, enabling PEs to compute the final block root—and therefore generate a valid signature—without ever exposing or revealing the payload itself.

As such, there's no data-dependency between block reconstruction and signing and signature interpolation. The two process can be handled paralled by every PE. 
## Evaluation
We implemented and then evaluated our prototype which is deployed to $n=4$ PEs based on AMD SEV-SNP across $4$ different availability zones, as configured in Figure 2. All evaluation was driven by real-world bid traces in 9/2023-12/2023 provided by Ultra Sound Relay.
<figure style="text-align: center;">
  <img src="https://hackmd.io/_uploads/BJJOLJ4Gbg.svg" width="70%">
  <figcaption><em>Figure 2: DPaaS deployment for our evaluation (n = 4),
showing topology labeled by round-trip times (including
signature signing and verification).</em></figcaption>
</figure>


### During Auction
Compared to the current MEV-Boost pipeline, DPaaS removes block validation from the proposer’s critical path to BT. On the PE side, bid processing remains extremely fast—even under stress tests it stays below 5 ms (Figure 3), whereas [prior relay analyses](https://frontier.tech/optimistic-relays-and-where-to-find-them) reported 100–200 ms processing times. 

<figure style="text-align: center;">
  <img src="https://hackmd.io/_uploads/B1vTH14Mbl.svg" width="70%">
  <figcaption><em>Figure 3: Average processing latency versus bid throughput while varying CPU cores in one PE. PDF shows real-world peak throughput from full-bid dataset.</em></figcaption>
</figure>

Although shifting validation out of the PE introduces more work for the builder—since BT must simulate the block and generate a TEE proof—we provided a detailed breakdown of this overhead in the paper. Block simulation is the dominant cost, but it can be substantially reduced through warm-up or prefetching. As shown in Figure 4a, our traces from 10 builders indicate that simulating the first block in each slot can incur a “cold-start” latency of up to 1.5 s. However, when the BT is allowed to run across multiple slots, this amortizes the initialization cost and reduces the per-slot first-simulation latency, reading only 281 ms after running 6k slots. Figure 4b further shows that all subsequent simulations within the same slot experience “warm-up” latency, remaining below 62 ms. Therefore, by keeping the BT active across slots and prefetching to warm up at the beginning of each slot, we can substantially reduce BT’s overall overhead.

<figure style="float: left; width: 38%; text-align: center;">
  <img src="https://hackmd.io/_uploads/rJ-Gd14M-e.svg" width="100%">
  <figcaption><em>Figure 4a: Average "Cold-start" latency
for the first block in each slot.</em></figcaption>
</figure>

<figure style="float: right; width: 38%; text-align: center;">
  <img src="https://hackmd.io/_uploads/Sy-z_kNM-x.svg" width="100%">
  <figcaption><em>Figure 4b: “Warmed-up”
latency for subsequent blocks in each slot versus number of
transactions.</em></figcaption>
</figure>

<div style="clear: both;"></div>

### Post-Auction
Compared to the status-quo MEV-Boost pipeline, DPaaS eliminates the original commit–reveal interaction between proposers and relays (GetHeader–GetPayload), which—as shown by Ultra Sound Relay data and [prior work](https://arxiv.org/abs/2305.09032)—can contribute up to 850 ms of latency. DPaaS substantially reduces this post-auction delay by finalizing the auction through inter-PE communication. In the best case, when all PEs are honest, our evaluation shows a post-auction latency of just 55.75 ms. Even in the worst case—where the leader PE crashes during the consensus phase—the post-auction latency is 172.33 ms. Both scenarios outperform today’s relays.

### MEV Earnings
Given the time-sensitivity of MEV-Boost, we also evaluated how well DPaaS converts performance into MEV capture as shown in Figure 5. We sampled 3,000 slots from December 2023 and replayed all bids to a DPaaS instance; fixing the target proposal time $t_P$, we infer the end-of-auction time as $t_e = t_P - T$, where T is the estimated post-auction latency. In both the best case (all four PEs honest) and the worst case (one PE crashed), DPaaS consistently outperforms the relay in MEV captured. Although all curves converge after t = 2 seconds, [prior work](https://arxiv.org/abs/2305.09032) shows that choosing a target proposal time beyond 2 seconds carries an increased risk of missed slots.

<figure style="text-align: center;">
  <img src="https://hackmd.io/_uploads/rJfcVJ4MWe.svg" width="70%">
  <figcaption><em>Figure 5: Median winning bid value based on different target
proposal times for DPaaS versus Relays.</em></figcaption>
</figure>


## Acknowledgements
This work is supported in part by Flashbots MEV Fellowship Grants. We appreciate the valuable discussions with Jonathan Passerat-Palmbach and Quintus Kilbourn. We are grateful to Ultra Sound Relay and Sen Yang for sharing the full-bid dataset and providing access to relay-timestamp information. 
