---
title: Communication Complexity under Harsh Partial Synchrony
date: 2025-12-19 23:00:00 -05:00
tags:
- models
author: Ittai Abraham, Yuval Efron, Kartik Nayak, and Ling Ren
---

In the last several posts we explored several [Simplex style](https://eprint.iacr.org/2023/463.pdf) protocols in partial synchrony: [3-round protocol](https://decentralizedthoughts.github.io/2025-06-18-simplex/), [2-round protocol](https://decentralizedthoughts.github.io/2025-07-18-two-round-Simplex/), [concurrent 2 and 3 round protocols](https://decentralizedthoughts.github.io/2025-07-29-2-round-3-round-simplex/), [benign version](https://decentralizedthoughts.github.io/2025-11-08-benign-simplex/).

In this post, we take a step back and focus on the models of **Partial Synchrony (PS)** and **Harsh Partial Synchrony (HPS)**. 

Many modern systems use the following definition of [Partial Synchrony](https://decentralizedthoughts.github.io/2019-06-01-2019-5-31-models/):

> **Partial Synchrony**: A message sent at time $t$ arrives by time at most $\max\{t, GST\}+\Delta$


This definition implicitly assumes that messages sent before $GST$ are delayed but not lost, and that they all arrive by time $GST+\Delta$.


The original [DLS88](https://groups.csail.mit.edu/tds/papers/Lynch/jacm88.pdf) paper defined a more challenging model that we will call *Harsh Partial Synchrony*:

> **Harsh Partial Synchrony (HPS)**:  A message sent at time $t\geq GST$ arrives at time at most $t+\Delta$. Other messages may have unbounded delay.


In contrast to Partial Synchrony, HPS allows messages sent before $GST$ to have unbounded delay.
HPS models systems where the network and the local storage of parties before GST are so unreliable that messages may essentially appear so late that it is as if they are lost.



### Communication Complexity in Partial Synchrony and Harsh Partial Synchrony in Theory

In **Simplex**, safety is maintained because an honest party will vote for a leader’s proposal only if it has seen a skip certificate for every view higher than the leader’s certificate (this is described as Change \#2 in our [Simplex post](https://decentralizedthoughts.github.io/2025-06-18-simplex/)). If the party does not have these skip certificates, they cannot vote and liveness is lost.

How does a party in Simplex ensure that it has access to these interim skip certificates? 

* In partial synchrony, any message sent at time $t$ by an honest party arrives by time $\max\{t, GST\}+\Delta$. Thus, after GST, the party would receive all the skip certificates for all the previous views. There may exist an unbounded number of skip certificates sent before GST, but they will all arrive by time $GST+\Delta$. Hence, the party can always collect these skip certificates without resending any messages. This results in a communication complexity of $O(n^2)$ words per view because these skip certificates can be amortized to messages sent in previous views.
* In harsh partial synchrony though, this does not hold. There may exist an unbounded number of skip certificates sent before GST with unbounded delay (essentially dropped). Overcoming this requires resending an unbounded number of messages after $GST$, resulting in the worst case in an *unbounded communication complexity* in a view. Moreover, this resending of messages may also cause an additional delay in the view.

In **Tendermint**, the communication complexity remains $O(n^2)$ words per view even in harsh partial synchrony. This is because safety in Tendermint depends on maintaining a single lock certificate, hence requires bounded space and communication. Due to similar reasons, other protocols in the same "family" such as Casper, HotStuff and Hydrangea also have bounded communication complexity in a view.


### Communication Complexity in Partial Synchrony and Harsh Partial Synchrony in Practice

Observe that unbounded communication complexity occurs when both of the following conditions hold:

1. Some honest party does not receive messages for several consecutive views: this could easily happen if for example, a party crashes and is attempting to recover, or if the party loses network access;
2. During these several consecutive views, none of the blocks was finalized: this is only possible if $>t$ parties crash/lose network access or if there is a catastrophic network failure. 


If either of the above conditions are relaxed, or if the number of views is small, then the increase in communication complexity is probably insignificant in practice.

Nevertheless, implementations of Simplex need to consider the possibility of harsh partial synchrony and at the very least implement a protocol for resending certificates.


### Epilogue


Should we design protocols in Partial Synchrony or in Harsh Partial Synchrony? Perhaps like many other cases in distributed systems, there is a model that is a middle ground between the two that captures practical scenarios better.

Your thoughts/comments on [X]().
