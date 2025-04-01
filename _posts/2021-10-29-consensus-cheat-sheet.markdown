---
title: Consensus cheat sheet
date: 2021-10-29 08:18:00 -04:00
tags:
- dist101
author: Ittai Abraham
---

| | Crash | Omission | Byzantine |
| --- | --- | ---- | --- |
| Synchrony |  ![](https://github.githubassets.com/images/icons/emoji/unicode/2714.png?v8) $f<n$ [is possible](https://decentralizedthoughts.github.io/2019-11-01-primary-backup/) <br /> ![](https://github.githubassets.com/images/icons/emoji/unicode/1f422.png?v8) $f+1$ round executions [must exist](https://decentralizedthoughts.github.io/2019-12-15-synchrony-uncommitted-lower-bound/)| ![](https://github.githubassets.com/images/icons/emoji/unicode/1f62d.png?v8) $f \geq n/2$ [is impossible](https://decentralizedthoughts.github.io/2019-11-02-primary-backup-for-2-servers-and-omission-failures-is-impossible/)| ![](https://github.githubassets.com/images/icons/emoji/unicode/2714.png?v8) $f<n/2$ possible with [PKI](https://decentralizedthoughts.github.io/2019-11-11-authenticated-synchronous-bft/) / possible with [PoW](https://decentralizedthoughts.github.io/2021-10-15-Nakamoto-Consensus/) <br /> ![](https://github.githubassets.com/images/icons/emoji/unicode/1f62d.png?v8) FLM: $f \geq n/3$ [impossible without PKI/PoW](https://decentralizedthoughts.github.io/2019-08-02-byzantine-agreement-is-impossible-for-$n-slash-leq-3-f$-is-the-adversary-can-easily-simulate/)|
| Partial Synchrony | ![](https://github.githubassets.com/images/icons/emoji/unicode/1f62d.png?v8) CAP: $f\geq n/2$ [is impossible](https://decentralizedthoughts.github.io/2023-07-09-CAP-two-servers-in-psynch/) | ![](https://github.githubassets.com/images/icons/emoji/unicode/2714.png?v8) Paxos: $f<n/2$ [is possible](https://decentralizedthoughts.github.io/2022-11-04-paxos-via-recoverable-broadcast/)|  ![](https://github.githubassets.com/images/icons/emoji/unicode/2714.png?v8) $f<n/3$ [is possible](http://pmg.csail.mit.edu/papers/osdi99.pdf) <br /> ![](https://github.githubassets.com/images/icons/emoji/unicode/1f62d.png?v8) DLS: $f \geq n/3$ [is impossible](https://decentralizedthoughts.github.io/2019-06-25-on-the-impossibility-of-byzantine-agreement-for-n-equals-3f-in-partial-synchrony/)|
| Asynchrony |  ![](https://github.githubassets.com/images/icons/emoji/unicode/1f422.png?v8) FLP: non-terminating executions [must exist](https://decentralizedthoughts.github.io/2019-12-15-asynchrony-uncommitted-lower-bound/)| ![](https://github.githubassets.com/images/icons/emoji/unicode/2714.png?v8) $f<n/2$ possible in $O(1)$ expected rounds| ![](https://github.githubassets.com/images/icons/emoji/unicode/2714.png?v8) $f<n/3$ [possible](https://dspace.mit.edu/bitstream/handle/1721.1/14368/20051076-MIT.pdf) in $O(1)$ [expected](https://decentralizedthoughts.github.io/2024-12-10-multi-world-vaba/) rounds|


Here $n$ is the number of parties, and $f$ is the number of parties that the [adversary can corrupt](https://decentralizedthoughts.github.io/2019-06-17-the-threshold-adversary/). Recall [that](https://decentralizedthoughts.github.io/2019-06-01-2019-5-31-models/) **Synchrony** $\subseteq$ **Partial Synchrony** $\subseteq$ **Asynchrony**. Similarly, [that](https://decentralizedthoughts.github.io/2019-06-07-modeling-the-adversary/) **Crash**  $\subseteq$ **Omission** $\subseteq$ **Byzantine**. Therefore,

1. Any upper bound holds if you go up and/or to the left in the table. e.g., the $O(1)$ expected round upper bounds under asynchrony also hold in partial synchrony and in synchrony.
2. Any lower bound holds if you go down and/or to the right in the table. e.g., the impossibility of $f \geq n/3$ with Byzantine adversaries in partial synchrony carries over to asynchrony, and the $t+1$ round lower bound carries over from crash to omission and Byzantine.

**Acknowledgments**: many thanks to Kartik Nayak for help with this post!

Your thoughts on [twitter](https://twitter.com/ittaia/status/1454065908415090696?s=20). 
