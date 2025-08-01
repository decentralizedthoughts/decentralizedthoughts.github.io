---
title: Flavours of State Machine Replication
date: 2019-10-25 15:54:00 -04:00
tags:
- SMR
author: Ittai Abraham
---

[State Machine Replication](https://www.cs.cornell.edu/fbs/publications/ibmFault.sm.pdf) is a fundamental approach in distributed computing for building fault tolerant systems. This post is a followup to our basic post on [Fault Tolerant State Machine Replication](https://decentralizedthoughts.github.io/2019-10-15-consensus-for-state-machine-replication/).


After defining what a state machine is and the transition function `apply` we then defined a Fault Tolerant State Machine Replication system as having two properties: 

**(Safety)** Any two honest replicas store the same sequence of commands in their logs.

**(Liveness)** Honest server replicas will eventually (when the system is synchronous) execute a command proposed by a client.

In this post we elaborate on several common types of State Machine Replication Systems  as a function of the [type of corruption](https://decentralizedthoughts.github.io/2019-06-07-modeling-the-adversary/) and the system guarantees. We first make a distinction between Omission failures and Byzantine failures. Then we make a distinction between *fault tolerance* (masking failures) and *fault safety* (losing liveness but safely terminating when a failure is detected).   

### Omission Fault Tolerant State Machine Replication (OFT-SMR)

This is the classic setting of [Paxos](https://lamport.azurewebsites.net/pubs/paxos-simple.pdf) where we assume there are $n>2f$ replicas and at most $f$ of them can fail by [omission](https://decentralizedthoughts.github.io/2019-06-07-modeling-the-adversary/).  Two well-known examples of OFT-SMR systems that implement some Paxos protocol variants are [Raft](https://raft.github.io/) and [ZooKeeper](https://www.confluent.io/blog/distributed-consensus-reloaded-apache-zookeeper-and-replication-in-kafka/).

### Byzantine Fault Tolerant State Machine Replication (BFT-SMR)

This is the setting of many *Blockchain* based systems. The canonical example is perhaps [PBFT](http://pmg.csail.mit.edu/papers/osdi99.pdf) and [BASE](http://cygnus-x1.cs.duke.edu/courses/cps210/spring06/papers/base.pdf). We assume there are $n>3f$ replicas and at most $f$ of them can fail by being [Byzantine](https://decentralizedthoughts.github.io/2019-06-07-modeling-the-adversary/) and act maliciously. There are many other systems that implement Byzantine Fault Tolerant State Machine Replication. Here is a [post](https://decentralizedthoughts.github.io/2019-06-23-what-is-the-difference-between/) that discusses some of them.

## Fault Safety vs Fault Tolerance

The traditional approach to State Machine Replication is to mask failures. We use the term *fault tolerance* to indicate a system's ability to maintain both safety and liveness.

But what if we could design a system that is *safe* but instead of masking failures and maintaining liveness, it would *detect* failure and then allow other systems to handle the failure?

For this to work we must also add the ability for any honest replica to *safely terminate* if it *detects* that there is a liveness problem.
In this approach we maintain the safety property but weaken the liveness to be optimistic: 

**(Safety)** Any two honest replicas store the same sequence of commands in their logs.

**(Optimistic Liveness)** If all replicas are honest and the system is synchronous then all honest replicas will execute a command proposed by a client in a timely manner.

**(Safe Termination)** If an honest replicas does not make progress it can terminate and guarantee that no honest replica will make further progress.

### Omission Fault Safe State Machine Replication (OFS-SMR)

The idea of building a Fault Safe State Machine Replication system that is resilient to Fail-Stop failures can be traced to the chain replication work of [van Renesse and Schneider 2004](http://www.cs.cornell.edu/home/rvr/papers/OSDI04.pdf). 

The basic idea is simple: a chain contains $f+1$ replicas ordered in a sequence from *head* to *tail*. When the head receives a command from the client it sends it along the chain. When the tail (the last replica in the chain) receives the command, the command is *committed*. The tail can then cause the replicas and the client to *learn* about the command being committed by traveling the chain in the reverse direction.

More generally, there is no need to use a chain: a primary can send the command and wait for all the $f+1$ replicas to acknowledge the command before committing. 

Optimistic liveness is obvious. For Safe Termination note that if an honest replica decides to terminate then no further progress can be made. Safety follows but requires careful handling of failures.

This design has been extended to handle transient or omission failures in [CORFU](http://www.cs.yale.edu/homes/mahesh/papers/corfumain-final.pdf) and was suggested for using to replicate [Flash storage units](https://www.microsoft.com/en-us/research/wp-content/uploads/2012/01/malki-acmstyle.pdf). The survey of 
[Christopher Meiklejohn](https://paperswelove.org/2015/topic/christopher-meiklejohns-a-brief-history-of-chain-replication/) provides a good overview of chain replication follow up papers.


### Byzantine Fault Safe State Machine Replication (BFS-SMR)

Chain replication was extended to the Byzantine setting by [van Renesse, Ho, and Schiper 2012](http://www.cs.cornell.edu/~ns672/publications/2012OPODIS.pdf). 
The main idea is to use a chain of $2f+1$ replicas instead of $f+1$. So in [partial synchrony](https://decentralizedthoughts.github.io/2019-09-13-flavours-of-partial-synchrony/), even if $f$ replicas are malicious there will be at least one honest replica that can provide the latest committed state.

With $2f+1$ replicas, obtaining a safe termination requires an explicit wedging operation.

In a [synchronous](https://decentralizedthoughts.github.io/2019-06-01-2019-5-31-models/) model it is possible to use just $f+1$ replicas and as we mentioned before there is no need to use a chain. This is the approach taken by [XFT 2016](https://www.usenix.org/system/files/conference/osdi16/osdi16-liu.pdf). XFT use a BFT-SMR system that only decides what is the group of $f+1$ that should make progress. The $f+1$ group implement a Byzantine Fault Safe SMR system using signatures.

When there is an assumption of synchrony, obtaining safe termination is immediate. A specific group of $f+1$ replicas is needed for progress and if just one honest group member stops responding then the group cannot make more progress. Care must be taken so that malicious members do not report old values of the state machine after it is terminated.

If this sounds similar to what happens in a payment channel this is not a coincidence. This follow up post explains how [Layer 2 is a smaller BFS-SMR that is opened and closed by the larger Layer 1 BFT-SMR](https://decentralizedthoughts.github.io/2019-10-25-payment-channels-are-just-a-two-person-bfs-smr-systems/).


Please leave comments on [Twitter](https://twitter.com/ittaia/status/1187864506074046464?s=20)


 

