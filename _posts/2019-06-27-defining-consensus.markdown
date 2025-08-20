---
title: What is Consensus?
date: 2019-06-27 15:00:00 -04:00
tags:
- consensus101
author: Kartik Nayak, Ittai Abraham
---

Consensus broadly means different parties reaching agreement. In distributed computing, Consensus is a core functionality. In this post, we define the consensus problem and its variants.

> In modern parliaments, the passing of decrees is hindered by disagreement among legislators
> -- <cite> Leslie Lamport, [Part-Time Parliament](https://lamport.azurewebsites.net/pubs/lamport-paxos.pdf) </cite>

Let us begin with the simplest consensus problem: *agreement*.


## The Agreement Problem

In this problem, we assume a set of $n$ parties where each party $i$ has some input $v_i$ from some known set of input values $v_i \in V$. A protocol that solves Agreement must satisfy:

**Agreement:** no two honest parties *decide* on different values.

**Validity:** if all honest parties have the same input value $v$, then the decision value must be $v$.

**Termination:** all honest parties must eventually *decide* on some value in $V$ and terminate.

Agreement is trivial if all parties are honest and the system is synchronous. To make it non-trivial, we must fix the communication model [synchrony, asynchrony, or partial synchrony](https://ittaiab.github.io/2019-06-01-2019-5-31-models/) and then fix the [threshold of the adversary](https://ittaiab.github.io/2019-06-17-the-threshold-adversary/) and other details about the [power](https://ittaiab.github.io/2019-06-07-modeling-the-adversary/) of the adversary.

In the *binary agreement* problem, we assume the set of possible inputs $V$ contains just two values: 0 and 1.

For lower bounds it's often beneficial to define an even easier problem of *agreement  with weak validity* where validity is replaced with:

**Weak Validity:** if all parties are honest and all have the same input value $v$, then $v$ must be the decision value.

More validity options and the notion of **external validity** is discussed in [this post](https://decentralizedthoughts.github.io/2022-12-12-what-about-validity/).

### Uniform vs. non-uniform agreement

With omission or crash adversaries, the property above is called *non-uniform agreement*. 
A stronger variant is *uniform agreement*, where no two parties (even faulty ones) *decide* on different values. 
This is called *uniform agreement* and assumes an omission or a crash adversary (this definition is meaningless with malicious corruptions).

For example, the difference will be relevant in a [state machine replication](https://ittaiab.github.io/2019-06-07-modeling-the-adversary/) setting with omission faults. For another example, see [this later post](https://decentralizedthoughts.github.io/2020-09-13-synchronous-consensus-omission-faults/).

## The Broadcast Problem

Here there is a designated party, often called the leader (or dealer), with input $v$. A protocol that solves Broadcast must have the following properties:

**Agreement:** no two honest parties *decide* on different values.

**Validity:** if the leader is honest, then the decision value must be $v$, and all honest parties must terminate.

For synchrony: **Termination:** all honest parties must eventually *decide* on some value in $V$ and terminate.

For asynchrony: **Totality:** if an honest party terminates, then all honest parties must eventually *decide* on some value in $V$ and terminate.
 

Broadcast and Agreement are deeply connected in synchrony. A nice exercise is to solve Broadcast given Agreement. Another good exercise is to solve Agreement given Broadcast. You can find this solution in [this post](https://decentralizedthoughts.github.io/2020-09-14-broadcast-from-agreement-and-agreement-from-broadcast/).

Please leave comments on [Twitter](https://twitter.com/ittaia/status/1421066572207169544?s=20).