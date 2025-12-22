---
title: Simplex vs Tendermint under Flavors of Partial Synchrony
date: 2025-12-19 23:00:00 -05:00
tags:
- models
author: Ittai Abraham, Yuval Efron, Kartik Nayak, and Ling Ren
---

---
title: Partial Synchrony variants
date: 2025-12-19 23:00:00 -05:00
tags:
- models
author: Ittai Abraham, Yuval Efron, Kartik Nayak, and Ling Ren
---


In this post we observe three variants of **Partial Synchrony (PS)**: 

1. Many modern systems use the following definition of [Partial Synchrony](https://decentralizedthoughts.github.io/2019-06-01-2019-5-31-models/):

    > **Bounded Partial Synchrony (BPS)**: A message sent at time $t$ arrives by time at most $\max\{t, GST\}+\Delta$


    This definition implicitly assumes that messages sent before $GST$ are delayed but not lost, and that they all arrive by time $GST+\Delta$.


2. The original [DLS88](https://groups.csail.mit.edu/tds/papers/Lynch/jacm88.pdf) paper defined a more challenging model that we call *Unbounded Partial Synchrony*:

    > **Unbounded Partial Synchrony (UPS)**:  A message sent at time $t\geq GST$ arrives at time at most $t+\Delta$. Other messages may have unbounded delay.


    In contrast to (Bounded) Partial Synchrony, UPS allows messages sent before     $GST$ to have unbounded delay. UPS models systems where the network before GST is asynchronous.


3. In fact there is an even more harsh definition where messages before $GST$ may be lost. We call that *Lossy Partial Synchrony*:

    > **Lossy Partial Synchrony (LPS)**:  A message sent at time $t\geq GST$ arrives at time at most $t+\Delta$. Other messages may have unbounded delay or may be dropped.
    
    LPS models systems where the network and the local storage of parties before $GST$ are so unreliable that messages may be lost.
    
    




### Communication Complexity in Partial Synchrony: Bounded, Unbounded, and Lossy

In **Simplex**, safety is maintained because an honest party will vote for a leader’s proposal only if it has seen a skip certificate for every view higher than the leader’s certificate (this is described as Change \#2 in our [Simplex post](https://decentralizedthoughts.github.io/2025-06-18-simplex/)). If the party does not have these skip certificates, they cannot vote and liveness is lost.

How does a party in Simplex ensure that it has access to these interim skip certificates? 

1. In bounded partial synchrony, any message sent at time $t$ by an honest party arrives by time $\max\{t, GST\}+\Delta$. Thus, after GST, the party would receive all the skip certificates for all the previous views. There may exist an unbounded number of skip certificates sent before GST, but they will all arrive by time $GST+\Delta$. Hence, the party can always collect these skip certificates without resending any messages. This results in a communication complexity of $O(n^2)$ words per view because these skip certificates can be amortized to messages sent in previous views.
2. In unbounded partial synchrony though, this does not hold. There may exist an unbounded number of skip certificates sent before GST with unbounded delay. So an honest leader after $GST$ may not obtain these skip certificates in a timely manner, hindering performance significantly, and rendering the protocol to be as slow as asynchronous protocols. The naive way of overcoming this requires resending an unbounded number of messages after $GST$, resulting, in the worst case, in an *unbounded communication complexity* in a view. Moreover, this resending of messages may also cause an additional delay in the view.
3. In lossy partial synchrony, Simplex without resends is not even eventually live. As in UPS, the naive way to resend certificates after GST in LPS requires *unbounded communication complexity* in a view.


**Tendermint**, on the other hand, retains all of it's properties even in LSP. In particular, Tendermint's communication complexity remains $O(n^2)$ words per view even in lossy partial synchrony. This is because safety in Tendermint depends on maintaining a single lock certificate, hence liveness requires bounded space and communication. The locks are (re)-sent in the view change of each subsequent view. Due to similar reasons, other protocols in the same "family" such as Casper, HotStuff and Hydrangea also have bounded communication complexity in a view.


### Communication Complexity in Partial Synchrony in Practice

Observe that unbounded communication complexity occurs when *both* of the following conditions hold:

1. Some honest party does not receive messages for several consecutive views: this could easily happen if for example, a party crashes and is attempting to recover, or if the party loses network access;
2. During these several consecutive views, none of the blocks were finalized (so skip certificates where created): this is only possible if $>t$ parties crash/lose network access or if there is a catastrophic network failure. 


If either of the above conditions is relaxed, or if the number of views is small, then the increase in communication complexity is probably insignificant in practice.

Nevertheless, implementations of Simplex need to consider the possibility of unbounded or lossy partial synchrony, and, at the very least, implement a protocol for resending certificates.


### Notes

* The [unknown $\Delta$ flavor](https://decentralizedthoughts.github.io/2019-09-13-flavours-of-partial-synchrony/) of Partial Synchrony is BPS. But it is unclear to us if the $GST$ based flavor as defined in DLS** is UPS or LPS.
* LPS is not subsumed by asynchrony, where as both UPS and BPS are.
* In LPS protocols can never reach a termination configuration where all non-faulty parties are in a state where they do not need to listen to messages. 


### Epilogue


Should we design protocols in Partial Synchrony? Which model should be used: bounded, unbounded, or lossy? Regardless, it seems important to be explicit about which synchrony assumptions you use, since these assumptions have direct implications for communication complexity under recovery.


Your thoughts/comments on [X]().
