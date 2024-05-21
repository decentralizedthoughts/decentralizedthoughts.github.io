---
title: Course
layout: page
---

## Course

### Week 1: models and definitions

- The [network model](/2019-06-01-2019-5-31-models/), the [threshold adversary](/2019-06-17-the-threshold-adversary/) model, and the [power of the adversary](/2019-06-07-modeling-the-adversary/). 
- Definition of [Consensus and Agreement](/2019-06-27-defining-consensus/).
- State machine replication (https://decentralizedthoughts.github.io/2019-10-15-consensus-for-state-machine-replication/).
- State Machine Replication for [crash failures](/2019-11-01-primary-backup/).
- From single agreement to [state machine replication](https://decentralizedthoughts.github.io/2022-11-19-from-single-shot-to-smr/).
- The [ideal state machine model and Linearizability](https://decentralizedthoughts.github.io/2021-10-16-the-ideal-state-machine-model-multiple-clients-and-linearizability/). 

### Week 2: synchrony with omission failures

- Upper bound: [Consensus with Omission failures](https://decentralizedthoughts.github.io/2022-11-04-paxos-via-recoverable-broadcast/).
- Lower bound: [Consensus with Omission failures](/2019-11-02-primary-backup-for-2-servers-and-omission-failures-is-impossible/) requires $f<n/2$.

### Week 3: lower bounds for partial synchrony

- Lower bound: the [CAP theorem](https://decentralizedthoughts.github.io/2023-07-09-CAP-two-servers-in-psynch/).
- Lower bound: Consensus with [Byzantine failures in Partial Synchrony](https://decentralizedthoughts.github.io/2019-06-25-on-the-impossibility-of-byzantine-agreement-for-n-equals-3f-in-partial-synchrony/) requires f<n/3

### Week 4: Byzantine adversaries

- Upper bound: partial synchrony, single shot [PBFT](https://decentralizedthoughts.github.io/2022-11-20-pbft-via-locked-braodcast/) using [locked broadcast](https://decentralizedthoughts.github.io/2022-09-10-provable-broadcast/).

### Week 5: asynchrony

- Upper bound: [Reliable broadcast](https://decentralizedthoughts.github.io/2020-09-19-living-with-asynchrony-brachas-reliable-broadcast/).
- Lower bound: FLP and [single mobile failure](https://decentralizedthoughts.github.io/2024-03-07-mobile-is-FLP/).