---
title: Byzantine Agreement is Impossible for $n \leq 3 f$ if the Adversary can Simulate
date: 2019-08-02 13:55:00 -04:00
tags:
- lowerbound
author: Kartik Nayak, Ittai Abraham
share-img: "/uploads/FLM-world3.png"
Field name: 
---

The [Fischer, Lynch, and Merritt, 1985](https://groups.csail.mit.edu/tds/papers/Lynch/FischerLynchMerritt-dc.pdf) lower bound states that Byzantine agreement is impossible if the adversary controls $f>n/3$ parties. It is well known that this lower bound does not hold if there is a PKI setup.

The modern view of this lower bound is that it holds if the adversary can *simulate* $n+f$ parties.

The ability to simulate a polynomial number of honest parties is trivial with a traditional poly-time adversary (assuming no PKI setup). A key modern observation is that in the *proof-of-work*  setting, an adversary controlling $f$ parties cannot simulate $n+f$ parties. So the FLM lower bound does not hold in these models. Indeed  Byzantine Agreement may be possible even if there is no PKI setup (in the *proof-of-work*  setting)!

> When nothing is known, anything is possible
> <cite> [Margaret Drabble](http://jacobjwalker.effectiveeducation.org/blog/2013/11/29/quote-of-the-day-when-nothing-is-known-anything-is-possible/)</cite>

In this series of posts, we are revisiting classic lower bounds from the 1980s. Most of them focused on *deterministic* protocols and computationally *unbounded* adversaries. Part of our goal is to provide a more modern view that also considers *randomized* protocols and *computational restrictions* on the adversary.

In our [first post](https://ittaiab.github.io/2019-06-25-on-the-impossibility-of-byzantine-agreement-for-n-equals-3f-in-partial-synchrony/) we reviewed the classic lower for [Partial synchrony](https://ittaiab.github.io/2019-06-01-2019-5-31-models/). That lower bound turned out to be very robust, it holds even against a static adversary and even if there is [trusted PKI setup](https://ittaiab.github.io/2019-07-18-setup-assumptions/).

In this post, we discuss another classic impossibility result. This time in the [synchronous model](https://ittaiab.github.io/2019-06-01-2019-5-31-models/). This lower bound shows that with $n
\leq 3f$ parties, one cannot solve Byzantine agreement in the face of an adversary controlling $f$ parties. We show the version where $n=3$ and $f=1$.

Informally this lower bound captures the following:
*if there are only three parties $A,B,C$ and say $B$ and $C$ blame each other for lying and provide no proof-of-malice to $A$, then $A$ has no way to decide between $B$ and $C$. $A$ has no way to know who to trust and agree with.*

**[Fisher, Lynch, and Merritt, 1985](https://groups.csail.mit.edu/tds/papers/Lynch/FischerLynchMerritt-dc.pdf): It is impossible to solve synchronous [agreement](https://ittaiab.github.io/2019-06-27-defining-consensus/) in a plain authenticated channels model if $f \geq n/3$.**

We will show a stronger modern version:

**[FLM 85 modern version] It is impossible to solve synchronous agreement against a Byzantine adversary that can simulate $n+f$ parties if $f \geq n/3$.**


See our follow-up [blog post](https://decentralizedthoughts.github.io/2021-10-04-crusader-agreement-with-dollars-slash-leq-1-slash-3$-error-is-impossible-for-$n-slash-leq-3f$-if-the-adversary-can-simulate/) for even stronger version of this lower bound. The high-level approach will be similar to our previous lower bound. We will use two powerful techniques: *indistinguishability* (where some parties can not tell between two potential worlds) and *hybridization* (where we build intermediate worlds between the two contradicting worlds and use a chain of indistinguishability arguments for a contradiction.).


As you will see below, the proof uses an adversary strategy that crucially relies on the ability of an adversary to **simulate** multiple other parties.

The proof is by contradiction. Suppose there is a protocol that can achieve Byzantine agreement with three parties. We will define worlds 1, 2, and 3:

**World 1:**
<p align="center">
  <img src="/uploads/FLM-world1.png" width="256" title="FLM world 1">
</p>

In World 1, parties $A$ and $B$ start with input 1. Corrupt party $C$ simulates the execution of four players, $C, A', B', C'$ connected in a peculiar fashion as shown in the figure. $C$ starts with input 1 whereas, $A', B'$ and $C'$ start with input 0. Thus, $B$ interacts with an instance of $C$ that starts with input 1 and $A$ interacts with an instance of $C$ (i.e., $C'$) that starts with input 0. Intuitively, by sending messages to $B$ based on what it receives from $A'$, $C$ is framing $A$ as if $A$ started with input 0. Similarly, $C'$ is framing $B$ by sending messages received from $B'$. The connections in the peculiar order ensures that the simulated parties can send appropriate messages to $A$ and $B$.

Now, since validity property holds despite what the corrupt party $C$ does, $A$ and $B$ commit to 1.

**World 2:**
<p align="center">
  <img src="/uploads/FLM-world2.png" width="256" title="FLM world 2">
</p>

In World 2, parties $B$ and $C$ start with input 0. Corrupt party $A$ simulates the execution of four players, $A$, $B'$, $C'$, and $A'$ connected as shown in the figure. The simulation is similar to world 1. Here, when $A$ is sending messages to $B$, it is framing $C$ to have sent 1. Similarly, $A'$ is framing $B$. Again, since the validity property holds, $B$ and $C$ commit to 0.

**World 3:**
<p align="center">
  <img src="/uploads/FLM-world3.png" width="256" title="FLM world 3">
</p>

In World 3, party $A$ starts with 1 and $C$ starts with 0. Corrupt party $B$ simulates the execution of four players, $B$, $C'$, $A'$, and $B'$ as shown in the figure. Parties $B$ and $C'$ start with input 1 whereas $A'$ and $B'$ start with input 0.

The question is: what do $A$ and $C$ output?

We argue that $A$ outputs 1 and $C$ outputs 0. Why?

<p align="center">
  <img src="/uploads/FLM-indistinguishability.png" width="512" title="Indistinguishability between World 1 and World 3 for A">
</p>

Observe that from party $A$'s perspective, World 3 is the same as World 1. From the figure, it can be seen that if we start from a double-circled $A$ and go clock-wise, the connections and inputs from parties are exactly the same. Intuitively, observe that in World 1, $C'$ started with input 0 and framed $B$ to have input 0 (the fully connected hexagon is necessary to make the argument more formal). However, $A$ decided to output 1 in World 1. Since party $A$ sees exactly the same set of messages in World 3, party $A$ outputs 1. By a similar argument party $C$ outputs 0.

Thus, if the validity property holds in Worlds 1 and 2, the agreement property cannot hold in World 3 (we cannot show absence of validity in World 3 since the honest parties started with different values).

### Simulation of parties by the adversary

The main thing to observe is that the proof requires the adversary to simulate the execution of $4$ parties (in general, $n+f$ parties). Thus, this proof fails if the adversary cannot simulate $n$ additional parties. Here are a couple of interesting cases where the adversary cannot simulate:

- Trusted setup: Under the *classic* computational assumptions that assume the adversary is *polynomially bounded*, this lower bound still holds assuming there is no setup. If there is a [trusted PKI setup](https://ittaiab.github.io/2019-07-18-setup-assumptions/), then the adversary will not be able to simulate any of the other parties.

- Computationally bounded adversaries: Under more fine-grained assumptions where the adversaries' power to solve certain computational puzzles is restricted, it is in fact possible to circumvent this lower bound - without any trusted setup. See [KMS](https://eprint.iacr.org/2014/857.pdf), [AD](https://www.iacr.org/archive/crypto2015/92160235/92160235.pdf), and [GGLP](https://eprint.iacr.org/2016/991.pdf).

- In particular, Nakamoto Consensus is an example of a Byzantine Agreement protocol that only requires an unpredictable random genesis as a setup and can withstand $(n/2)(1+\epsilon)>f>n/3$ corruptions (see [GKL](https://eprint.iacr.org/2014/765.pdf)) or this [blog post](https://decentralizedthoughts.github.io/2019-11-29-Analysis-Nakamoto/).

The other thing to observe is that when the FLM bound holds, it holds in a strong way for randomized protocols, disallowing even protocols that reach agreement with a small constant probability of error. Moreover, FLM holds even from Crusader Agreement (when we weaken the Agreement to Weak Agreement). See our follow-up [blog post](https://decentralizedthoughts.github.io/2021-10-04-crusader-agreement-with-dollars-slash-leq-1-slash-3$-error-is-impossible-for-$n-slash-leq-3f$-if-the-adversary-can-simulate/) for both extensions.  

Finally, we note that this lower bound holds even for [Broadcast](https://decentralizedthoughts.github.io/2019-06-27-defining-consensus/), not just for Agreement.

Please leave comments on [Twitter](https://twitter.com/ittaia/status/1158276207860838400?s=20)

**Acknowledgment.** We thank Georgios Konstantopoulos and Avishay Yanai for identifying typographical errors and helping improve the post.
