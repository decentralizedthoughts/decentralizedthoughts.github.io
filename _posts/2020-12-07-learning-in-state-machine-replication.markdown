---
title: Learning in State Machine Replication
date: 2020-12-07 09:30:00 -05:00
published: false
---

A [state machine replication](https://decentralizedthoughts.github.io/2019-10-15-consensus-for-state-machine-replication/) system needs to do roughly three things (in a fault-tolerant manner): (1) decide on commands; (2) learn about previously decided commands; (3) execute decided commands. In this post, we provide an overview of the *learning* part of SMR. Most of the ideas of this post appear in [PBFT](https://www.microsoft.com/en-us/research/wp-content/uploads/2017/01/thesis-mcastro.pdf) and are extended here to the case where digital signatures are used.

In distributed computing, *learning* has many manifestations. Learning by clients is often called issuing a *read-only* command. Once a log of commands is compacted, then learning is sometimes referred to as *state transfer*. We will explain these keywords below.

Before understanding the learning process, let us understand the different states that the system and individual replicas can be in when committing a single command:

1. **[Committed configuration](https://decentralizedthoughts.github.io/2019-12-15-asynchrony-uncommitted-lower-bound/):** This is a state of the system where the decision value is set (known as a uni-valiant configuration). Recall that you may be in a committed configuration without any of the replicas knowing about it.

2. **[Decided configuration](https://decentralizedthoughts.github.io/2019-12-15-asynchrony-uncommitted-lower-bound/):** This is a state of the system where all replicas have decided.

Let's introduce a new type of configuration:

3. **Checkpointed configuration:** This is a configuration between being committed and being decided in which there are at least $n-f$ replicas that have decided.

Conceptually, **learning** is the protocol for obtaining the decided command after the system is in a checkpointed configuration. 

## Learning in a single-shot consensus system

In many situations, a non-faulty replica or a client may have missed the decision and wants to catch up and learn the decision. The consensus algorithm already agreed on a value. Now a replica simply wants to *read* or *learn* the decision value. How can it do this?

1. If we have uniform consensus (or in the Byzantine case, if decisions have a cryptographically verified certificate), it's enough to receive one (certified) decision message. If the system is in a checkpointed configuration, then it is enough to wait for $f+1$ responses (because one of these responses must intersect with the $n-f$ decided replicas). As an optimistic optimization, one can ask just one replica and hope to receive a decision before asking more replicas.

2. If we have non-uniform consensus (or in the un-authenticated Byzantine case), then you need to wait for at least $f+1$ replicas to send the same decision value.  If the system is in a checkpointed configuration, then it is enough to wait for $n-f$ responses (because at least $f+1$ of these responses must intersect with the $n-f$ decided replicas). As an optimistic optimization, one can ask just $f+1$ replicas and hope to receive the same response from all before asking more replicas.


## Learning in a multi-shot consensus system

A State Machine Replication system makes a *sequence* $c_1,c_2,c_3,\dots$ of decisions. In such a multi-shot consensus protocol, we will call the $i$-th decision in the sequence: *slot $i$*. In the basic version of such systems, the decision for slot $i+1$ is done only after the decision for slot $i$. More generally, there is often some active window $x$, such that the decision for slot $i+x$ can only be made after the decision for slot $i$ is done. Even more generally, there may be some periodic *checkpoint* that is done every $y<x$ slots (often $y=x/2)$ and the active window is all the $x$ from the latest checkpoint (this is what PBFT does). We will expand on checkpoints in the next section.

For now, it's enough to assume that each replica maintains the *latest consecutive decided slot*. If this value is $l$, it means that the replica has locally decided on all slots from 1 to $l$ but slot $l+1$ has not been locally decided yet. 

If a replica or client wants to catch up and *learn* about all the decided slots, what should it do?

Clearly, it can just try to learn each slot independently but how will it learn which slots are decided and which are not?

- In a uniform consensus setting or a Byzantine failure setting with commit certificates, the learning party can ask $f+1$ other replicas for the *last (consecutively) decided slot*. The asking party can then take the minimum value $m$ out of the $f+1$ responses. It can know for sure that decisions from 1 to $m$ are in a checkpointed configuration and learning will succeed.

- In a non-uniform consensus or Byzantine failure setting without certificates, the learning party can ask $2f+1$ other replicas for the *last (consecutively) decide slot*. The asking party can then take the minimum value $m$ such that at least $f+1$ replicas say that their last consecutively decide slot is *at least* $m$.  It can know for sure that decisions from 1 to $m$ are in a checkpointed configuration and learning will succeed.


Even when certificates are used, if you want your learning (reads) to be linearizable, then in an asynchronous setting you need to read from $2f+1$ replicas and take the certified value that appears in at least $f+1$ replicas, also see [Section 5.1.3 in PBFT](https://www.microsoft.com/en-us/research/wp-content/uploads/2017/01/thesis-mcastro.pdf).

## Learning with Checkpoints

When a Replicated State Machine creates periodic checkpoints it allows a replica to catchup by comparing its state to the latest checkpoint and then add only the latest updates. This is similar to the restore from snapshot backup vs restore from an incremental backup.

A learning replica can now (1) learn the latest checkpoint; then (2) update to the latest checkpoint; then (3) update the decisions in the active window.

Step (1) is a learning query, and step (3) is similar to the learning described in the previous section. For step (2), we can use a specialized protocol for **state transfer**. For example, one can use anti-entropy via a Merkle tree to learn the missing pieces of the latest checkpoint. See [Section 5.3 in PBFT](https://www.microsoft.com/en-us/research/wp-content/uploads/2017/01/thesis-mcastro.pdf) and also [Bessani etal](https://www.usenix.org/system/files/conference/atc13/atc13-bessani.pdf). 

## Learning complexity, optimization, and denial of service protection

In a na\"ive form of learning, each faulty replica can ask each non-faulty replica for the missing decision. This would lead to a  $O(n^2 L)$ total word complexity for a decision of length $L$. Let's cover two important optimizations:

1. Instead of asking the decision from $f+1$ replicas, the asking replica can ask the decision from one replica and ask the [cryptographic hash](https://decentralizedthoughts.github.io/2020-08-28-what-is-a-cryptographic-hash-function/) of the decision from the remaining $f$ replicas. Modeling the size of the hash as a word, this reduces the total word complexity to $O(n^2 + n L)$. The problem with this approach is that a malicious asker can ask for the decision value from more than one replica. So the worst-case word complexity could again reach $O(n^2 L)$.

2. To solve the denial of service attack, instead of sending the decision, we can use [error correcting codes](https://users.ece.cmu.edu/~jwylie/pubs/CMU-PDL-03-104.pdf) to split the decision value to $O(m/n)$ shares. Each non-faulty party will send its share to all parties. So the total word complexity is just $O(M/n)$ times $O(n^2)$ which is $O(n M)$ (where the leading constant is at least 3).


Please answer/discuss/comment/ask on Twitter.

