---
title: A Payment Channel is a two person BFS-SMR system
date: 2019-10-25 14:22:00 -07:00
tags:
- SMR
- blockchain101
author: Ittai Abraham
---

This posts views payment channels as essentially a [two person BFS-SMR](https://decentralizedthoughts.github.io/2019-10-25-flavours-of-state-machine-replication/) system along with a carefully implemented mechanism for safe termination (channel closing) under assumptions of synchrony. 

Suppose Alice wants to Pay Bob 10,000 times. The obvious solution is to do 10,000 transactions on a main State Machine Replication System. Let's call this system the *Layer 1 system* and assume Layer 1 is a large Byzantine Fault Tolerant State Machine Replication system. This type of solution may cause the Layer 1 system to have considerable traffic. Payment channels (and more generally Layer 2 solutions) offer a way to relive this traffic and scale the system. 

The basic idea of a payment channel:
1. Alice *opens* the channel by locking value on Layer 1 and dedicating it to the channel.
2. Alice and Bob exchange 10,000 payment commands privately in a *payment channel* (in a 2 person *SMR*, see below). They maintain the current balance after each payment.
3. Bob (or Alice) *close* the channel by submitting the latest state of the channel to the Layer 1 system.  

Important details of implementing a basic payment channel:
1. When Alice locks value on Layer 1 for this payment channel she should not be able to double-spend and use the locked funds for other uses. This can be guaranteed for example by having Alice essentially *pay* the channel.
2. When Alice or Bob try to close the channel they cannot report a channel state (balance) that never occured. This can be guaranteed by having both Alice and Bob sign each transaction *execution* and its resulting state. So the Layer 1 system will only accept a state from the layer 2 channel that is singed by both Alice and Bob.
3. When Alice or Bob try to close the channel they cannot report a state that is not the most *recent state*. This requires two things: 

   3.1. Alice and Bob sign each transactions in a log of operations. by doing this, ALice and Bob are essentially implementing a [two person Byzantine Fault Safe State Machine Replication](https://decentralizedthoughts.github.io/2019-10-25-flavours-of-state-machine-replication/) system run by Alice and Bob. So formally this BFS-SMR has $n=2, f=1$ and maintains its safety, optimistic liveness and safe termination as long as either Alice or Bob are honest.

   3.2. If say Alice sends an old state to Layer 1 then Bob needs to report that there is a newer state to Layer 1 in a timely manner. This requires Bob to be able to synchronously communicate with the Layer 1 system. A typical solution is to allow a very large window (say 2 weeks) for Bob to respond.

4. If a violation is detected then it is possible to apply a *punishment mechanism*. In particular, if Alice reports an old state and Bob proves this then we can use the locked funds to punish Alice. A two pay channel would require both Alice and Bob to lock funds and allow both to be punished if needed. 

5. If both Alice and Bob are malicious then the only thing they can do is re-distribute the dedicated channel value between them. The Layer 1 system prevents them from doing anything else. 


### Conclusion

A payment channel is a way for any two participants to *open* a private two person BFS-SMR system, *execute* transactions on this private BFS-SMR system and then *close* the channel under assumptions of synchrony. 

The main challenge in these systems is how to safely terminate (close) a channel and correctly report the latest state of the channel to the layer 1 system. The standard solution typically assumes synchrony and requires the honest participant of the channel to report the correct state to the Layer 1 system in a timely manner.  


Please leave comments on [Twitter](https://twitter.com/ittaia/status/1187864507571421186?s=20)