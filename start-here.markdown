---
title: Start Here
date: 2020-09-21 09:34:00 -04:00
---

{: .box-note}
This page contains material for a graduate course on Blockchains and Distributed Computing with a dash of Cryptography (stay tuned for more). Or read [posts chronologically](https://decentralizedthoughts.github.io/).

We would love to get your feedback. If you find a post helpful, have a suggestion to improve, or any other comment: [drop us a comment](https://twitter.com/ittaia/status/1421066572207169544?s=20) or send us email - your feedback is very valuable.


## Basics, Foundations, and Classics

Start with the definition of [Consensus and Agreement](/2019-06-27-defining-consensus/). Then learn about the [network model](/2019-06-01-2019-5-31-models/), the [threshold adversary](/2019-06-17-the-threshold-adversary/) model, and the [power of the adversary](/2019-06-07-modeling-the-adversary/). Many protocols need a [trusted setup phase](/2019-07-19-setup-assumptions/).
The [consensus cheat sheet](https://decentralizedthoughts.github.io/2021-10-29-consensus-cheat-sheet/) gives a quick overview of what is possible and impossible. You can build half a course just from the upper bounds and lower bounds linked from it. 

### Variants of Consensus and Broadcast 

[Approximate agreement](https://decentralizedthoughts.github.io/2022-06-07-approx-agreement-one/) is a variation that considers rational input values.

This post covers several [relaxations of Broadcast](/2019-10-22-flavours-of-broadcast/).


## Synchronous Protocols

The Synchronous model is a good place to start because protocols are simpler.

- Classic Byzantine agreement protocol: the [Phase-King](https://decentralizedthoughts.github.io/2022-06-09-phase-king-via-gradecast/).
- Classic Byzantine Broadcast protocol (with a PKI) for $f < n$: the [Dolev-Strong Authenticated Broadcast protocol](/2019-12-22-dolev-strong/). 
- A non-equivocation protocol (with a PKI) for  $f < n$: [Crusader Broadcast](https://decentralizedthoughts.github.io/2022-06-19-crusader-braodcast/). 

More recent State Machine Replication protocols:

- [Sync HotStuff](/2019-11-12-Sync-HotStuff/).
- An [optimal optimistically responsive synchronous protocol](/2020-06-12-optimal-optimistic-responsiveness/).
- A simple, streamlined synchronous protocol called [Streamlet](/2020-05-14-streamlet/). 
- Survey of [authenticated protocols under the synchrony assumption](/2019-11-11-authenticated-synchronous-bft/).

Use of randomization in synchronous agreement protocols:

- For [crash failures](https://decentralizedthoughts.github.io/2023-02-18-rand-and-consensus-1/).
- For [omission failures](https://decentralizedthoughts.github.io/2023-02-19-rand-and-consensus-2/).


## Partially Synchronous Protocols

[Partial synchrony](/2019-09-13-flavours-of-partial-synchrony/) is one of the most used models in real word systems today.


Single shot [Paxos](https://decentralizedthoughts.github.io/2022-11-04-paxos-via-recoverable-broadcast/).


Taking ideas from the Byzantine setting and applying them to the benign setting:

 -  [Benign Hotstuff](https://decentralizedthoughts.github.io/2021-04-02-benign-hotstuff/).
 -  [Simplifing Raft with Chaining](https://decentralizedthoughts.github.io/2021-07-17-simplifying-raft-with-chaining/). 
 -  [Log Paxos](https://decentralizedthoughts.github.io/2021-09-30-distributed-consensus-made-simple-for-real-this-time/) is a modern take on multi-Paxos. 

The Byzantine setting:

- An important building block: [provable broadcast](https://decentralizedthoughts.github.io/2022-09-10-provable-broadcast/).
- Single shot [PBFT](https://decentralizedthoughts.github.io/2022-11-20-pbft-via-locked-braodcast/).
- [Two Round HotStuff](https://decentralizedthoughts.github.io/2022-11-24-two-round-HS/) with SMR and accountability. 
- Single shot to SMR is covered [here](https://decentralizedthoughts.github.io/2022-11-19-from-single-shot-to-smr/).
- [Information Theoretic HotStuff](https://decentralizedthoughts.github.io/2021-09-20-information-theoretic-hotstuff-it-hs-part-one/).

## Asynchronous Protocols

Fundamental lower bound in asynchrony: The  [FLP lower bound](/2019-12-15-consensus-model-for-FLP/) showing the impossibility of consensus under even one crash fault. 

Important building blocks in asynchrony:

1. The [Reliable Broadcast](https://decentralizedthoughts.github.io/2020-09-19-living-with-asynchrony-brachas-reliable-broadcast/) protocol. 
2. The [Reliable Gather](https://decentralizedthoughts.github.io/2021-03-26-living-with-asynchrony-the-gather-protocol/) is a multi-leader generalization of reliable broadcast.
3. We discuss how to measure [round complexity in asynchrony](https://decentralizedthoughts.github.io/2021-09-29-the-round-complexity-of-reliable-broadcast/) and also improved round complexity for reliable broadcast. 

Series on Asynchronous Agreement: 

1. [Define the problem](https://decentralizedthoughts.github.io/2022-03-30-asynchronous-agreement-part-one-defining-the-problem/);
2. present [Ben-Or's protocol](https://decentralizedthoughts.github.io/2022-03-30-asynchronous-agreement-part-two-ben-ors-protocol/);
3. provide a [modern version](https://decentralizedthoughts.github.io/2022-03-30-asynchronous-agreement-part-three-a-modern-version-of-ben-ors-protocol/);
4. Introduce [Crusader Agreement and Binding Crusader Agreement](https://decentralizedthoughts.github.io/2022-04-05-aa-part-four-CA-and-BCA/); 
5. use BCA to efficiently solve [Binary Byzantine Agreement from a strong common coin](https://decentralizedthoughts.github.io/2022-04-05-aa-part-five-ABBA/).
 
Reaching [Asynchronous Agreement on a Core Set](https://decentralizedthoughts.github.io/2023-07-22-agreeemnt-on-a-core-set/).

## State Machine Replication

Define [state machine replication](/2019-10-15-consensus-for-state-machine-replication/) (SMR). 

Levels of [SMR fault tolerance](/2019-10-25-flavours-of-state-machine-replication/). 

The [ideal state machine model and Linearizability](https://decentralizedthoughts.github.io/2021-10-16-the-ideal-state-machine-model-multiple-clients-and-linearizability/). 

The scalability and performance of a State Machine Replication system are not just about [consensus, but also about data and execution](/2019-12-06-dce-the-three-scalability-bottlenecks-of-state-machine-replication/).

How [DAGs improve the performance of SMR](https://decentralizedthoughts.github.io/2022-06-28-DAG-meets-BFT/).

To learn about upper bounds, start with a [simple SMR for crash failures](/2019-11-01-primary-backup/). Then extend SMR to omission failures: [First via single shot](/2020-09-13-synchronous-consensus-omission-faults/) and then via the [lock-commit](https://decentralizedthoughts.github.io/2020-11-30-the-lock-commit-paradigm-multi-shot-and-mixed-faults/) paradigm to [multi-shot consensus](https://decentralizedthoughts.github.io/2020-11-30-the-lock-commit-paradigm-multi-shot-and-mixed-faults/).


## Nakamoto Consensus

The bitcoin revolution brought many breakthroughs in distributed computing, economics and cryptography. One of the striking breakthroughs in distributed computing was a new form of Byzantine Agreement now called **Nakamoto Consensus**.

- What is [Nakamoto consensus](https://decentralizedthoughts.github.io/2021-10-15-Nakamoto-Consensus/)?
- Bitcoin's [setup assumption](https://decentralizedthoughts.github.io/2019-07-18-do-bitcoin-and-ethereum-have-any-trusted-setup-assumptions/).
- Security proof of [Nakamoto consensus](https://decentralizedthoughts.github.io/2023-10-30-Analysis-Nakamoto/) and an [older post](https://decentralizedthoughts.github.io/2019-11-29-Analysis-Nakamoto/).
- What is the problem of [selfish mining](/2020-02-26-selfish-mining/)?


## Lower Bounds

Lower bounds give us powerful tools to understand the fundamental limitations and model assumptions. 

### Lower bounds on the size of the adversary:

- State Machine replication can work only for minority failures:
  - The [CAP theorem for partial synchrony](https://decentralizedthoughts.github.io/2023-07-09-CAP-two-servers-in-psynch/): Any system, in the face of a perceived 50-50 split, can either maintain safety or liveness, but not both.
  - The CAP theorem for synchrony and omission: [Consensus with Omission failures even in lock step](/2019-11-02-primary-backup-for-2-servers-and-omission-failures-is-impossible/) requires $f<n/2$.
  - Strengthening the lower bound: $f<n/2$ is required in lock step [even if the adversary can choose either send omission or receive omission](https://decentralizedthoughts.github.io/2024-01-30-between-crash-and-omission/) (but not both).
  - [CAP type theorems in the permissionless setting](https://decentralizedthoughts.github.io/2022-03-03-blockchain-resource-pools-and-a-cap-esque-impossibility-result/)
  
- Split brain lower bounds:
  - Dwork, Lynch, Stockmeyer 1988 ([DLS](https://groups.csail.mit.edu/tds/papers/Lynch/jacm88.pdf)) lower bound: [Byzantine Consensus in Partial Synchrony](/2019-06-25-on-the-impossibility-of-byzantine-agreement-for-n-equals-3f-in-partial-synchrony/) requires $f<n/3$.
  - CJKR lower bound: Neither Non-equivocation nor Transferability alone is enough for [tolerating minority corruptions in asynchrony](https://decentralizedthoughts.github.io/2021-06-14-neither-non-equivocation-nor-transferability-alone-is-enough-for-tolerating-minority-corruptions-in-asynchrony/).
  - TEEs without state need $3f+1$ in Partial Synchrony because of the [rollback adversary](https://decentralizedthoughts.github.io/2023-06-26-dls-meets-rollback/).

- Fischer, Lynch, Merritt ([FLM](https://groups.csail.mit.edu/tds/papers/Lynch/FischerLynchMerritt-dc.pdf)) lower bound: [Byzantine Consensus with no PKI](/2019-08-02-byzantine-agreement-is-impossible-for-$n-slash-leq-3-f$-is-the-adversary-can-easily-simulate/) (or more generally when the adversary can simulate) requires $f<n/3$. 

- Strengthening the FLM lower bound with randomization and a weaker problem: [Crusader Agreement with $\leq 1/3$ error is impossible for $n\leq 3f$ if the adversary can simulate](https://decentralizedthoughts.github.io/2021-10-04-crusader-agreement-with-dollars-slash-leq-1-slash-3$-error-is-impossible-for-$n-slash-leq-3f$-if-the-adversary-can-simulate/).

### Lower bounds on the number of messages

- Dolev and Reischuk 1982 ([DR](https://www.cs.huji.ac.il/~dolev/pubs/p132-dolev.pdf)) lower bound: [Consensus (even with omission failures) needs a quadratic number of messages](/2019-08-16-byzantine-agreement-needs-quadratic-messages/).
- Extending Dolev and Reischuk to [Byzantine crusader broadcast](https://decentralizedthoughts.github.io/2022-08-14-new-DR-LB/).

### Lower bounds on the round complexity and existence of infinite executions

- The simplest proof that [any consensus protocol in asynchrony must have an infinite execution](https://decentralizedthoughts.github.io/2024-03-07-mobile-is-FLP/) even against a single crash failure.

- The same proof also shows that [any consensus protocol in synchrony must have an infinite execution](https://decentralizedthoughts.github.io/2024-03-07-mobile-is-FLP/) against a single **mobile** crash failure.

- [Early stopping lower bounds](https://decentralizedthoughts.github.io/2024-01-28-early-stopping-lower-bounds/) provide a bound on the number of rounds in execution where there are $0\leq f\leq t$ faults. In particular, in the best case executions where there are no faults at all ($f=0$).
  - $\min\\{f+2,t+1\\}$ round lower bound for Early Stopping for consensus with crashes and Early Deciding for uniform consensus with omission (crashes with fixed first)

- Fischer, Lynch, Paterson 1985 ([FLP](https://groups.csail.mit.edu/tds/papers/Lynch/jacm85.pdf)) lower bound, three part series using bi-valency (uncommitted configuration) arguments: 
  - Consensus must have some initial state that is [uncommitted](/2019-12-15-consensus-model-for-FLP/):
  - This implies [executions with at least $f+1$ rounds in Synchrony](/2019-12-15-synchrony-uncommitted-lower-bound/).
  - The FLP result: [non-terminating executions in Asynchrony](/2019-12-15-asynchrony-uncommitted-lower-bound/).

- Lower bounds on the *good case latency* - the number of rounds when the broadcaster is non-faulty and the network is synchronous: [a complete categorization](https://decentralizedthoughts.github.io/2021-02-28-good-case-latency-of-byzantine-broadcast-a-complete-categorization/)
- The [good case latency of optimistically responsive rotating leader protocols](https://decentralizedthoughts.github.io/2021-12-07-good-case-latency-of-rotating-leader-synchronous-bft/) requires $2\Delta$.

### Lower bounds due to privacy requirements

- Ben-Or, Kelmer, Rabin 1994 ([BKR](https://dl.acm.org/doi/10.1145/197917.198088)) lower bound: Asynchronous Verifiable Secret Sharing must have a [non-zero probability of not terminating](https://decentralizedthoughts.github.io/2020-07-15-asynchronous-fault-tolerant-computation-with-optimal-resilience/) when $n/4 \leq f < n/3$. So Asynchronous Verifiable Secret sharing (and Asynchronous MPC) with perfect security needs $f<n/4$. 

### Liveness attacks

- Raft does not guarantee liveness under [omission faults](https://decentralizedthoughts.github.io/2020-12-12-raft-liveness-full-omission/).

### Lower bounds on stronger notions of validity

- [Lower bounds for strong validity](https://decentralizedthoughts.github.io/2022-12-12-what-about-validity/)

## Blockchains

What is a [blockchain?](https://decentralizedthoughts.github.io/2022-09-05-what-is-a-blockchain/)

What are [blockchains useful for, really](https://decentralizedthoughts.github.io/2023-01-12-what-are-blockchains-useful-for-really/)?

What was the [first blockchain (or how to timestamp a digital document)](/2020-07-05-the-first-blockchain-or-how-to-time-stamp-a-digital-document/)? 

Do proof-of-work blockchains need any [setup assumptions?](/2019-07-18-do-bitcoin-and-ethereum-have-any-trusted-setup-assumptions/)?

What does [checkpointing a blockchain](/2019-09-13-dont-trust-checkpoint/) mean?

The simplest L2 solution is a [payment channel](/2019-10-25-payment-channels-are-just-a-two-person-bfs-smr-systems/).

What is player replaceability? A series:
- [Defining the problem and achieving a committee-based sub-quadratic communication protocol](https://decentralizedthoughts.github.io/2023-01-05-player-replaceability-I/)
- [Achieving adaptive security for the committee-based protocol](https://decentralizedthoughts.github.io/2023-01-05-player-replaceability-II/)

## Cryptography


- [Cryptographic hash functions](/2020-08-28-what-is-a-cryptographic-hash-function/).
- [Merkle trees](https://decentralizedthoughts.github.io/2020-12-22-what-is-a-merkle-tree/).
- A glimpse at [Zero knowledge proofs](https://decentralizedthoughts.github.io/2020-12-08-a-simple-and-succinct-zero-knowledge-proof/)
- [Bilinear accumulators](/2020-04-02-bilinear-accumulators-for-cryptocurrency/) from polynomial commitments.
- [Range proofs](/2020-03-03-range-proofs-from-polynomial-commitments-reexplained/) from polynomial commitments.
- Private set intersection: [part 1](/2020-03-29-private-set-intersection-a-soft-introduction/) and [part 2](/2020-07-26-private-set-intersection-2/). Apple is using PSI for [CSAM detection](https://decentralizedthoughts.github.io/2021-08-29-the-private-set-intersection-psi-protocol-of-the-apple-csam-detection-system/).

### Polynomials

- A lightweight intro to [Polynomials over a finite field](/2020-07-17-the-marvels-of-polynomials-over-a-field/).
- The basics of [Polynomial secret sharing](/2020-07-17-polynomial-secret-sharing-and-the-lagrange-basis/).
- [The Fast Fourier Transform over finite fields](https://decentralizedthoughts.github.io/2023-09-01-FFT/).
- What is [Verifiable Information Dispersal](https://decentralizedthoughts.github.io/2024-08-08-vid/).

### Secret Sharing and MPC

Polynomial secret sharing is a base for deep connections between cryptography and distributed computing.

- Polynomial secret sharing against a [passive adversary](https://decentralizedthoughts.github.io/2020-07-17-polynomial-secret-sharing-and-the-lagrange-basis/)
- Against a [crash adversary](https://decentralizedthoughts.github.io/2022-08-17-secret-sharing-with-crash/).
- The [BGW88](https://inst.eecs.berkeley.edu/~cs276/fa20/notes/BGW88.pdf) protocol for [Verifiable Secret Sharing](https://decentralizedthoughts.github.io/2022-08-24-BGW-secret-sharing/).
- Chaum’s [Dining Cryptographers](https://users.ece.cmu.edu/~adrian/731-sp04/readings/dcnets.html) and [the additivity of polynomial secret sharing](https://decentralizedthoughts.github.io/2022-08-25-dining-cryptographers-additive/).

# Research Oriented Posts

- [What is the difference between PBFT, Tendermint, SBFT, and HotStuff ?](/2019-06-23-what-is-the-difference-between/) and [How does HotStuff-2 relate to these protocols?](/2023-04-01-hotstuff-2/)

- [Survey of modern Authenticated Synchronous BFT protocols](/2019-11-11-authenticated-synchronous-bft/) (updated in March 2021).

- [Sync HotStuff](/2019-11-12-Sync-HotStuff/).

- [Optimal Optimistic Responsivness](/2020-06-12-optimal-optimistic-responsiveness/).

- Encrypted Blockchain Databases [part 1](/2020-07-10-encrypted-blockchain-databases-part-i/) and [part 2](/2020-07-10-encrypted-blockchain-databases-part-ii/).

- [Asynchronous Fault-Tolerant Computation with Optimal Resilience](/2020-07-15-asynchronous-fault-tolerant-computation-with-optimal-resilience/).

- [Resolving the Availability-Finality Dilemma](/2020-10-31-ebb-and-flow-protocols-a-resolution-of-the-availability-finality-dilemma/).

- [BFT Protocol Forensics](/2020-11-19-bft-protocol-forensics/).

- [Can we Obtain Player Replaceability and Forensic Support Simultaneously?](https://decentralizedthoughts.github.io/2023-01-30-player-replaceability-forensic-support/)

- Good-case Latency of Byzantine Broadcast: [the Synchronous Case](https://decentralizedthoughts.github.io/2021-03-09-good-case-latency-of-byzantine-broadcast-the-synchronous-case/) and [a Complete Categorization](https://decentralizedthoughts.github.io/2021-02-28-good-case-latency-of-byzantine-broadcast-a-complete-categorization/).

- [2-round BFT SMR with n=4, f=1](https://decentralizedthoughts.github.io/2021-03-03-2-round-bft-smr-with-n-equals-4-f-equals-1/).

- [Optimal Communication Complexity of Authenticated Byzantine Agreement](https://decentralizedthoughts.github.io/2021-09-20-optimal-communication-complexity-of-authenticated-byzantine-agreement/)

- [Good-case Latency of Rotating Leader Synchronous BFT](https://decentralizedthoughts.github.io/2021-12-07-good-case-latency-of-rotating-leader-synchronous-bft/)

- [EIP-1559 in Retrospect](https://decentralizedthoughts.github.io/2022-03-10-eip1559/)

- [Colordag: From always-almost to almost-always 50% selfish mining resilience](https://decentralizedthoughts.github.io/2022-03-07-colordag-from-always-almost-to-almost-always-50-percent-selfish-mining-resilience/)

- [Consensus by Dfinity: in synchrony](https://decentralizedthoughts.github.io/2022-03-12-dfinity-synchrony/) and [Consensus by Dfinity - Part II (Internet Computer Consensus): in partial synchrony](https://decentralizedthoughts.github.io/2022-03-12-dfinity-partial-synchrony/) 

- [Sandglass: Safe Permissionless Consensus](https://decentralizedthoughts.github.io/2022-06-21-sandglass/).

- [DAG Meets BFT - The Next Generation of BFT Consensus](https://decentralizedthoughts.github.io/2022-06-28-DAG-meets-BFT/).

- [He-HTLC - Revisiting Incentives in HTLC](https://decentralizedthoughts.github.io/2022-08-12-hehtlc/).

- [Decentralization of Ethereum Builder Market](https://decentralizedthoughts.github.io/2024-05-07-decentralization-ethereum/).
- [Sailfish: Improving the Latency of DAG-based BFT](https://decentralizedthoughts.github.io/2024-05-23-sailfish/).
- [Shoal++: High Throughput DAG-BFT Can Be Fast!](https://decentralizedthoughts.github.io/2024-06-12-shoalpp/)