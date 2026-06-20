---
title: What is Consensus?
date: 2019-06-27 15:00:00 -04:00
tags:
- consensus101
author: Kartik Nayak, Ittai Abraham
---

Consensus broadly means different parties reaching agreement. In distributed computing, consensus is a core functionality. In this post, we define the consensus problem and its variants.

> In modern parliaments, the passing of decrees is hindered by disagreement among legislators
> -- <cite> Leslie Lamport, [Part-Time Parliament](https://lamport.azurewebsites.net/pubs/lamport-paxos.pdf) </cite>

Let us begin with the simplest consensus problem: *agreement*.


## The Agreement Problem

In this problem, we assume a set of $n$ parties where each party $i$ has some input $v_i$ from some known set of input values $v_i \in V$. A party *decides* when it irrevocably outputs a value. A protocol that solves agreement must satisfy:

**Agreement:** no two honest parties *decide* on different values.

**Validity:** if all honest parties have the same input value $v$, then the decision value must be $v$.

**Termination:** all honest parties must eventually *decide* on some value in $V$.

The problem becomes interesting once parties may fail or deviate. Its solvability then depends on the communication model ([synchrony, asynchrony, or partial synchrony](https://decentralizedthoughts.github.io/2019-06-01-2019-5-31-models/)), the [threshold of the adversary](https://decentralizedthoughts.github.io/2019-06-17-the-threshold-adversary/), and other details about the [power](https://decentralizedthoughts.github.io/2019-06-07-modeling-the-adversary/) of the adversary.

In the *binary agreement* problem, we assume the set of possible inputs $V$ contains just two values: $0$ and $1$.

For lower bounds, it is often beneficial to define an even easier problem of *agreement with weak validity*, where validity is replaced with:

**Weak Validity:** if all parties are honest and all have the same input value $v$, then $v$ must be the decision value.

More validity options and the notion of **external validity** are discussed in [this post](https://decentralizedthoughts.github.io/2022-12-12-what-about-validity/).

### Uniform vs. non-uniform agreement

With crash or omission faults, the agreement property above is called *non-uniform agreement*: it constrains only honest parties. A stronger variant is *uniform agreement*, where no two parties that decide, including parties that later crash or omit messages, decide on different values. This distinction is meaningful for faults in which faulty parties still follow the protocol; with malicious corruptions, a faulty party can simply claim any output.

For example, the difference is relevant in a [state machine replication](https://decentralizedthoughts.github.io/2019-10-15-consensus-for-state-machine-replication/) setting with omission faults. For another example, see [this later post](https://decentralizedthoughts.github.io/2020-09-13-synchronous-consensus-omission-faults/).

### Provable vs. non-provable agreement

For Byzantine faults, an analogue of uniform agreement is *provable agreement*. This notion requires a cryptographic setup: before the protocol begins, the parties agree on a public key infrastructure (PKI) associating each party with a public verification key. Protocol messages are digitally signed, and signatures cannot be forged for honest parties.

A *decision certificate* for a value $v$ is a forwardable collection of signed protocol messages that anyone can verify using the PKI.

**Provable Agreement:** for every probabilistic polynomial-time adversary, the probability that it produces two valid decision certificates for different values is negligible in the security parameter.

Provable agreement therefore allows clients and offline parties to verify the outcome without knowing a party's local transcript. For example, in [Simplex FVS](https://decentralizedthoughts.github.io/2026-05-14-simplex-FVS/), all protocol messages are signed, and a decision certificate consists of $n-f$ signed `Final` messages.

By contrast, *non-provable agreement* guarantees only that no two honest parties decide differently. Such a protocol may still use a PKI and digital signatures, but its decisions need not have independently verifiable certificates. For example, [Dolev--Strong](https://decentralizedthoughts.github.io/2019-12-22-dolev-strong/) uses signed messages, but whether a signature chain is accepted depends on the round in which it is received.

## The Broadcast Problem

Here there is a designated party, called the sender, with input $v$. A protocol that solves broadcast must have the following properties:

**Agreement:** no two honest parties *decide* on different values.

**Validity:** if the sender is honest, then every honest party must eventually *decide* on $v$.

For synchrony: **Termination:** all honest parties must eventually *decide* on some value in $V$.

For asynchrony: **Totality:** if an honest party *decides*, then all honest parties must eventually *decide* on some value in $V$.
 

Broadcast and agreement are deeply connected in synchrony. A nice exercise is to solve broadcast given agreement. Another good exercise is to solve agreement given broadcast. You can find these solutions in [this post](https://decentralizedthoughts.github.io/2020-09-14-broadcast-from-agreement-and-agreement-from-broadcast/).

Please leave comments on [Twitter](https://twitter.com/ittaia/status/1421066572207169544?s=20).
