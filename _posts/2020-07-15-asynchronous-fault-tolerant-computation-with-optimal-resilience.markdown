---
title: Asynchronous Fault Tolerant Computation with Optimal Resilience
date: 2020-07-15 04:39:00 -04:00
tags:
- lowerbound
- asynchrony
author: Ittai Abraham, Danny Dolev, Gilad Stern
---

A basic question of distributed computing:
**Is there a fundamental limit to fault tolerant computation in the Asynchronous model?**

The celebrated [FLP](https://decentralizedthoughts.github.io/2019-12-15-asynchrony-uncommitted-lower-bound/) theorem says that any protocol that solves Agreement in the asynchronous
model that is resilient to at least one crash failure must have a non-terminating execution. This means that deterministic asynchronous consensus is *impossible*, but with randomization, asynchronous consensus is possible in constant expected time. Randomization does not circumvent the existence of a non-terminating execution, it just reduces the probability measure of this event to have [measure zero](https://en.wikipedia.org/wiki/Almost_surely).

Given the above, the following question is natural:
**Is this potentially measure zero event of non-termination the only limitation for fault tolerant computation in the asynchronous model?**



In 1983,  [Ben-Or, Canetti, and Goldreich](https://dl.acm.org/doi/10.1145/167088.167109) initiated the study of [secure multiparty computation](https://en.wikipedia.org/wiki/Secure_multi-party_computation) in the *asynchronous model*. Their fundamental result is that the answer above is **yes** when there are $n >4t$ servers and an adversary that can corrupt at most $t$ parties in a Byzantine manner. They show that **perfect** security with finite expected run time can be obtained for any functionality.

The BCG83 work left open the domain of $3t<n \le 4t$.
In 1993, [Canetti and Rabin](https://dl.acm.org/doi/10.1145/167088.167105) obtained a protocol for Asynchronous Byzantine Agreement with optimal resilience ($3t<n$) and conditioned on terminating, had a constant expected running time. Their protocol had an *"annoying property"*: the non-termination event has a **non-zero** probability measure. This problematic non-zero probability of non-termination came from their verifiable secret sharing protocol.

In 1994, [Ben-Or, Kelmer, and Rabin](https://dl.acm.org/doi/10.1145/197917.198088) addressed this problem. They provided an optimal resilience asynchronous secure multiparty computation protocol with the same "annoying property": the non-termination event has a **non-zero** probability measure. Moreover, BKR94  claim that this is unavoidable. That is, if $n\le 4t$ then any t-resilient asynchronous verifiable secret sharing protocol $A$ must have some **non-zero** probability $q_A>0$ of not terminating. 

In other words, there is a fundamental limit to Asynchronous Fault Tolerant Computation with Optimal Resilience:

**Theorem [BKR94]: any protocol solving verifiable secret sharing in the asynchronous model with optimal resilience must have a positive probability of deadlock.**

In this blog post, we provide a proof overview of this lower bound. For a full proof that strengthens the BKR statement (and a fascinating new upper bound showing what can be done without a non-zero probability of non-termination) please see our [PODC 2020 paper](https://arxiv.org/pdf/2006.16686.pdf). 


### What is Verifiable Secret Sharing (VSS)?

Verifiable Secret Sharing (VSS) is a pair of protocols: *Share* and *Reconstruct*, with one designated party, called the *Dealer*. The Dealer has an *input value* $s$ for the Share protocol. The Reconstruct protocol has an output value. VSS has the following properties:

**Termination:**
1. If the dealer is non-faulty, and all non-faulty participate, then all non-faulty will complete the Share protocol.
2. If any non-faulty completes the Share protocol, then every non-faulty that participates in the Share protocol completes it.
3. If all non-faulty complete the Share protocol, then if all non-faulty start the Reconstruct protocol, then all non-faulty will complete the Reconstruct protocol.

**Binding:**
Once the first non-faulty completes the Share protocol there exists some value $r$ such that:
1. If the dealer is honest, then $r=s$ ($r$ is the Dealer's input value).
2. Any non-faulty that completes the Reconstruct protocol outputs $r$.

**Hiding:**
If the dealer is non-faulty, and no honest party has begun the Reconstruct protocol, then the adversary can gain no information about the Dealer's input value, $s$.


In other words, the Share protocol forces a dealer that completes Share to *commit* to a value of its choice. For non-faulty dealers that will be its input. If the dealer is non-faulty, the Hiding property keeps the value hidden from the adversary (as long as no non-faulty start the Reconstruct protocol). If the dealer is faulty, the Binding property prevents the adversary from changing the committed value (once one non-faulty completed the Share protocol). 

### Lower bound techniques

Like many previous lower bounds, this lower bound heavily relies on two powerful techniques: *indistinguishability* (where some parties can not tell between two potential worlds) and *hybridization* (where we build intermediate worlds between the two contradicting worlds and use a chain of indistinguishability arguments for a contradiction.). Unlike previous [lower bounds](https://decentralizedthoughts.github.io/2019-06-25-on-the-impossibility-of-byzantine-agreement-for-n-equals-3f-in-partial-synchrony/) we have seen in this [blog](https://decentralizedthoughts.github.io/2019-08-02-byzantine-agreement-is-impossible-for-$n-slash-leq-3-f$-is-the-adversary-can-easily-simulate/), this one uses indistinguishability more subtly. We will call this **indistinguishability boosting**:
1. Start with a very weak notion of *conditional indistinguishability*: that there is a non-zero probability event during the Share protocol, such that conditioned on this event two worlds are indistinguishable.
2. Boost this conditional indistinguishability event in the Share protocol to prove the existence of a full indistinguishability event in the Reconstruct protocol. 

### The setting
We have four parties $A,B,C,D$, where $D$ is the dealer and at most one party may be byzantine  (so $n=4$, $f=1$). Using standard techniques, this can be generalized to any $3f <n \leq 4f$. The network is fully asynchronous so messages can be delayed by any finite amount.


**Crash World 0:**
In Crash World 0, party $C$ is slow, $D$ has input 0 and $A$ is passive (honest but curious).

**Crash World C:**
In Crash World C, party $C$ is crashed and $D$ has input 0.

From $B$ and $D$'s point of view, Crash World $0$ and Crash World C are entirely indistinguishable. In crash world 0, all non-faulty participate in the Share protocol and thus must complete it. Since the worlds are indistinguishable, $A$,$B$ and $D$ complete the protocol even if $C$ is slow throughout it.

In Crash World 0 $A$ is faulty so it must not know that the value $0$ was shared (otherwise the Hiding property would be violated). This almost obvious statement gives us a very powerful tool: whichever messages $A$ exchanged throughout the Share protocol, it must be possible for those messages to be exchanged, regardless of the value $D$ shared. There is nothing special in this argument about $A$ or the value $0$, so we can use this argument with $B$ or with $1$. This tool will be very important for the rest of our arguments.


**Share World A:**
In Share World A, party $C$ is crashed, and $D$ has input 0.


**Share World B:**
In Share World B, party $C$ is crashed, and $D$ has input 1.

**Share World Hybrid:**
In Share World Hybrid, party $C$ is slow, party $D$ is malicious, and acts as if its input is 0 to $A$ and as if its input is 1 to $B$.


Note that in Share Worlds A and B, all non-faulty must complete the Share Protocol. The important question to ask if the Share World Hybrid will complete the Share protocol. Because if it always completes then one could derive an easy lower bound. Either in Share Worlds A or in B there would be a violation of the Binding property (that $r=s$) with constant probability.

BKR's insight was that it's enough to prove that the Share World Hybrid has some non-zero probability of completing the Share protocol! Indeed it can be shown that if the Adversary guesses the random bits of the honest parties then completion of the Share protocol is guaranteed. This happens because conditioned on this event, $D$ can predict how $A$ and $B$ will respond to its messages. As shown above, every set of messages $A$ and $B$ can exchange must be possible regardless of the value $D$ shared. This means that $D$ can tailor the messages it sends to $A$ and $B$ such that $A$ sees Share World A, $B$ sees Share World B, and the messages they exchange with each other are entirely compatible with both of their views. Since the worlds $A$ and $B$ see are indistinguishable from worlds in which they complete the Share protocol, they do so in Share World Hybrid, but only if $D$ guesses their randomness correctly.

To conclude, we created a strategy for a malicious dealer such that with an extremely small (but non-zero) probability, the Share protocol will complete, and if it completes then the two non-faulty parties $A$ and $B$ are at a disagreement about the Reconstruct output value.

This already shows an important point: **perfect VSS is impossible in this setting and some (non-zero) probability of error is unavoidable**. But BKR claimed something stronger: that some (non-zero) probability of deadlock is unavoidable (even with constant error probability)!

### Boosting a non-zero error probability in the Share protocol to a constant error probability in the Reconstruct protocol

The idea will be to boost this malicious strategy for the Share phase that obtains a non-zero probability of error, under the assumption that there is no deadlock, to a malicious strategy for the Reconstruct protocol that obtains a constant probability of error.

**Reconstruct World A:**
In Reconstruct World A, party $C$ is slow during Share, $D$ has input 0 and is slow during Reconstruct, party $B$ is malicious: during Share, it acts correctly, but during Reconstruct, it acts as if $D$ had input 1.


**Reconstruct World B:**
In Reconstruct World B, party $C$ is slow during Share, $D$ has input 1 and is slow during Reconstruct, party $A$ is malicious: during Share, it acts correctly, but during Reconstruct, it acts as if $D$ had input 0.

**Reconstruct World Hybrid:**
In Reconstruct World Hybrid, $D$ is malicious and executes the attack in Share World Hybrid. After completing the Share protocol, $D$ goes silent and lets $A$, $B$ and $C$ run without interruption in the Reconstruct protocol.

The main challenge here is to show that the malicious party can "act as if $D$ had the opposite value" by using the probability distribution induced by the conditional event of completing the Share protocol in the Share World Hybrid. As shown above, whichever messages $A$ and $B$ exchange during the Share protocol, those messages must be possible both in the case that $D$ shares 0 and in the case that $D$ shares $1$. We will show the attack for Reconstruct World A (the same attack works for Reconstruct World B). After completing the Share protocol, $A$ can claim that $D$ guessed its randomness correctly and sent it messages corresponding to sharing the value $1$. $A$ already knows which messages it exchanged with $B$, and those messages must be possible if $D$ shares the value $1$. This means that $A$ can find some set of messages $D$ could have sent that would result in $A$ sending the messages it sent. Very importantly, even though the original attack in Share World Hybrid would only succeed with some nonzero probability, $A$ can *always* claim $D$'s attack succeeded, because it already knows which messages it exchanged with $B$. This also means that Reconstruct World A is indistinguishable from Reconstruct World Hybrid conditioned upon the event that $D$'s original attack succeeded. This is the core of the *boosting* technique.

We can now finally look at party $C$ and construct a chain of indistinguishable worlds: Reconstruct World A is indistinguishable from Reconstruct World Hybrid, conditioned upon $D$'s attack succeeding, which is indistinguishable from Reconstruct World B. In Reconstruct World Hybrid, if $D$'s attack succeeds, all non-faulty complete the Share protocol and start the Reconstruct protocol. This also means that they all complete the Reconstruct protocol and output some value. Since Reconstruct Worlds A and B are indistinguishable from Reconstruct World Hybrid conditioned upon $D$'s attack succeeding, all non-faulty complete the Reconstruct protocol in those worlds as well. The fact that Reconstruct World A is indistinguishable from Reconstruct world B implies that party $C$ must output the wrong value with a constant (large) probability. Proving this indistinguishability chain by using the conditional probability distribution of completing the Share protocol in the Reconstruct World Hybrid is subtle and non-trivial.

Observe that to get a constant probability of error, we strongly used the fact that party $C$ **must** complete the Reconstruct protocol and output some value. The reason party $C$ must complete and cannot wait for a message from $D$ is that it could be that we are in Reconstruct World Hybrid and $D$ will never respond.
Let's see where this proof would fail if we allowed even a small probability of deadlock: in that case party $C$ could decide to wait for one more response! If $C$ were in either Reconstruct World A or B, it could indeed wait for $D$. This would only violate the termination property of the Reconstruct protocol in Reconstruct World Hybrid, but would only do so with a very small probability because there is a very small probability that the Share protocol of Share World Hybrid will complete!

To conclude we showed that if you assume there is no deadlock, then a malicious strategy in the Share protocol causing a small (non-zero) error probability can be boosted to a malicious strategy in the Reconstruct protocol causing a large (constant) probability of error, under the assumption that there is never a deadlock.

The contrapositive is: there cannot be a protocol that is both: (1) correct with some constant probability, and (2) has a measure zero probability of deadlock. This concludes the lower bound overview.

For a full proof that strengthens the BKR statement (and a fascinating new upper bound showing what can be done without a non-zero probability of non-termination) please see our [PODC 2020 paper](https://arxiv.org/pdf/2006.16686.pdf). 

Please leave comments on [Twitter](https://twitter.com/ittaia/status/1283411228677857284?s=20).



