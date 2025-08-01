---
title: 2019 10 08 Techniques For Consensus - Equivocation check and quorum intersection
date: 2019-10-08 17:34:52.668000000 -07:00
published: false
tags:
- consensus
author: Kartik Nayak
---

In this post, we discuss two key techniques, equivocation check, and quorum intersection, that are at the heart of most consensus protocols. Synchronous protocols typically rely on both of these techniques, whereas partially synchronous and asynchronous protocols depend only on the latter. In this post, we will only elaborate on the approaches. We will show how different protocols use them in subsequent posts. For concreteness, we discuss these in the context of State Machine Replication (SMR) with a steady-state leader. 

### Equivocation check
An equivocation check is used to detect if the leader has been sending conflicting messages to different replicas. If so, they may commit to conflicting values, and there can be a consistency violation. A leader equivocation check can be performed by replicas forwarding the leader-message to all other replicas. If the replicas observe conflicting values $v$ and $v’$ sent by the leader, they detect that the leader is Byzantine and can engage in a view-change protocol to replace it. 

Performing an equivocation check has three essential requirements:
1. **Digitally signed messages.** Digital signatures allow public verifiability of messages sent by a party. Thus, if a replica $r$ forwards a digitally signed leader-message $m$ to replica $r’$, $r’$ can verify that the message $m$ was indeed sent by the leader. In the absence of a signature, the $r'$ may not be able to ascertain whether the leader or replica $r’$ is Byzantine.
2. **Clock synchronization.** Due to message delays in the network, no consensus protocol guarantees that all replicas commit at the same instant of time. Then, an equivocation check may fail in the following scenario: a fast-replica $r$ commits before slow-replica $r’$. Immediately after $r$ has committed, $r’$ receives an equivocating leader-message. Now, even if $r’$ forwards the equivocating message, $r$ cannot "un-commit" the other value. If there was synchronization between the two replicas, the fast-replica could have waited *long enough* until the slow-replica would stop honoring conflicting leader-messages. Before that time, if the slow-replica forwards a leader equivocation, it should arrive at the fast-replica, thereby preventing it from committing. This brings us to our third requirement of synchronous message delay.
3. **Synchrony.** How long should the fast-replica wait? It depends on how much the slow-replica is lagging as well as the time it takes for the slow-replicas’ forwarded equivocation message to arrive. If either of these two delays are not bounded, then the fast-replica will not be able to decide whether to commit to a value (and assume the slow-replica may have crashed or is Byzantine) or to wait for the slow-replica’s message. Thus, bounded message-delay or synchrony is essential for an equivocation check to succeed.

The last two requirements are the reason why we see this technique being used only by synchronous consensus protocols.

### Quorum intersection. 
If the network is not synchronous, how should replicas decide whether to commit a value? Of course, equivocation checks will fail because a slow-replicas’ forwarded message may not arrive on time. Indeed, the adversary can use a network partition to cause a consistency violation. The principle of quorum intersection applies a less stringent requirement for avoiding consistency violation. It says the following: *if a sufficiently large quorum of replicas convinces honest replica $r$ to commit to a value $v$, no other honest replica $r’$ will commit to different value $v’$.* Observe that if the convincing quorum is large enough, at least one of the honest replicas $r’’$ that convinces replica $r$ will be required in convincing $r’$ too. Since honest replica $r’’$ will send the same message to both $r$ and $r’$, they will not commit to different values. Here, replica $r’’$ is referred to as being the **one honest replica in the intersection of quorums.**

How large is a sufficiently large quorum? We consider two cases:
1. **Crash faults.** Suppose all replicas are honest, and we tolerate only crash faults. Then, an honest majority quorum suffices, as shown in the figure below. 
2. **Byzantine faults.** If the faults can be Byzantine, then a Byzantine replica $r’’$ in the intersection can send different values to $r$ and $r’$. Thus, if there are $f$ Byzantine faults, one needs at least $f+1$ replicas in the intersection. One possible scenario when $f < n/3$ is to have quorums of size $2f+1$ so that they intersect in $f+1$ replicas, as shown in the figure.

The quorum intersection technique is used in all partially synchronous and asynchronous consensus protocols. Synchronous protocols may also use a quorum intersection. However, due to synchrony, they can handle larger quorum sizes and make stronger conclusions. Larger quorum sizes also allow them to tolerate more faults.
