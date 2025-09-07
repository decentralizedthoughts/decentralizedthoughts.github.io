---
title: Set Replication - fault tolerance without total ordering
date: 2022-12-27 04:00:00 -05:00
tags:
- research
author: Ittai Abraham
---

State machine replication is the gold standard for implementing any (public) ideal functionality. It totally orders all transactions and as a consequence solves Byzantine agreement. But solving agreement, in non-optimistic cases, is quadratic in cost and is not constant time. In some cases this overhead is unnecessary because there is no need to totally order all transactions.

As a canonical example, suppose Alice is transferring a token to Bob and Carol is transferring a token to Dan. There is no need to totally order these two token transfer transactions. It is okay that some clients see the first transfer happened before the second while some other clients see the second transfer as happening before the first.

In the non-byzantine setting, the *fundamental* observation that sometimes a weaker problem than consensus needs to be solved goes back to the foundational work of [Lamport 2005](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/tr-2005-33.pdf):

> Consensus has been regarded as the fundamental problem that must be solved to implement a fault-tolerant distributed system. However, only a weaker problem than traditional consensus need be solved. We generalize the consensus problem to include both traditional consensus and this weaker version. --[Generalized Consensus and Paxos, 2005](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/tr-2005-33.pdf)

In many natural use cases, in particular the canonical simple token transfer use case, total ordering is not needed. This approach is taken by [FastPay](https://arxiv.org/pdf/2003.11506.pdf), [Guerraoui et al, 2019](https://arxiv.org/pdf/1906.05574), [Sliwinski and Wattenhofer, 2019](https://arxiv.org/abs/1909.10926), applied to privacy preserving transactions (see [UTT](https://eprint.iacr.org/2022/452.pdf) and [Zef](https://eprint.iacr.org/2022/083.pdf)), planned to be used in the [Sui platform](https://github.com/MystenLabs/sui/blob/main/doc/paper/sui.pdf) and in [Linera](https://linera.io/whitepaper).

There is considerable research in ways to relax total ordering requirements to gain better performance. For example, see [EPaxos](https://www.cs.cmu.edu/~dga/papers/epaxos-sosp2013.pdf) (and also [EPaxos Revisited](https://www.usenix.org/conference/nsdi21/presentation/tollman)). The first work that aimed to relax the total order requirements in the blockchain space is by [Lewenberg, Sompolinsky, and Zohar, 2015](https://fc15.ifca.ai/preproceedings/paper_101.pdf) and its follow-up work [Specture, 2016](https://eprint.iacr.org/2016/1159.pdf). See this post on [DAG-based protocols](https://decentralizedthoughts.github.io/2022-06-28-DAG-meets-BFT/) for advances in recent years and how DAG-based protocols are emerging as a powerful tool for getting better throughput mempools and BFT.

### The benefits of decomposing a multi writer object into independent single writer objects

In traditional state machine replication, the system is modeled as a single multi-writer object, and a total ordering protocol is used to serialize all commands. This requires solving agreement among replicas, which is costly: even in the case of omission failures, it can require a quadratic number of messages, and the number of rounds is worst case linear in the synchronous case and unbounded in the asynchronous case.

An alternative is to decompose the state machine into independent single-writer objects. In this setting, we only need to totally order commands per object, rather than across the entire system. This relaxation dramatically reduces complexity: for each single-writer object, total ordering can be achieved with linear communication and constant time, even in the presence of Byzantine failures and asynchrony.


## Set Replication


Just as **log replication** captures the core agreement requirements of traditional state machine replication, we define **set replication** to model the weaker agreement essence that arises when the system is composed of independent single-writer state machines.

To ground this idea, we begin by recalling the definition of log replication, which formalizes the agreement problem inherent in totally ordering commands for a shared, multi-writer state machine.


### Reminder: definition of Log Replication

There are clients and $n$ servers. Clients can make two types of requests: ```read``` which returns a **log of values** (or $\bot$ for the empty log)  as a response; and ```write(v)``` which gets an input value and also returns a response that is a log of values.

Clients can have multiple input values at different times. 

**Termination**: If a non-faulty client issues a *request* then it eventually receives a *response*.

**Agreement**: Any two requests return logs such that one is a prefix of the other.

**Validity**: Each value in the log can be uniquely mapped to a valid write request.

**Correctness**: For a write request with value $v$, its response, and any response from a request that started after this write response, returns a log of values that includes $v$.

The definition for set replication is simply to **remove the agreement property** and return unordered **sets** instead of sequential **logs**.

### Definition of Set Replication

Clients and $n$ servers. Clients can make two types of requests: ```read``` which returns a **set of values** (or $\bot$ for the empty set)  as a response; and ```write(v)``` which gets an input value and also returns a response that is a set of values.

**Termination**: If a non-faulty client issues a valid *request* then it eventually receives a *response*.

**Validity**: Each value in the set can be uniquely mapped to a valid write request.

**Correctness**: For a write request with value $v$, its response, and any response from a request that started after this write response, returns a set of values that includes $v$.

### Discussion: no difference for a single writer

Observe that when there is just a single writer client there is no difference between log replication and set replication - the (single writer) client can sequentially submit commands by adding a sequence number to its operations and implement a log of its commands on top of the set abstraction.

In fact set replication is solving multi-shot consensus for single writer objects (see [Guerraoui et al, 2019](https://arxiv.org/pdf/1906.05574)).

Moreover, if the system is partitioned into single writer objects, such that each object can be written to by a single client (the owner of the private key associated with the object's public key) then multiple clients can transact in parallel as long as each one is writing to a different object.

The difference between log replication and set replication can be seen when there are two or more writers. For example if two writers need to decide which one wrote first (say they both want to swap money on an [AMM](https://arxiv.org/pdf/2102.11350.pdf)) then log replication will provide an ordering of these two transactions but set replication cannot do this. 


### Implementing Set Replication via Locked Broadcast: it is linear and works in asynchrony

Log replication requires solving multi-shot agreement and even one agreement may take $f+1$ rounds in the worst case in synchrony and have infinite executions in asynchrony. Moreover, even one agreement needs $\Omega(f^2)$ messages in the worst case for omission failures and beyond. In previous posts [we showed](https://decentralizedthoughts.github.io/2022-11-20-pbft-via-locked-braodcast/) how to solve [log replication](https://decentralizedthoughts.github.io/2022-11-24-two-round-HS/) via a repeated application of [locked broadcast](https://decentralizedthoughts.github.io/2022-09-10-provable-broadcast/) in the Byzantine setting.


Set replication is an easier problem. In the asynchronous Byzantine setting, it can be implemented as a single instance of *locked broadcast*:

```
Write(v): 
    client drives LockedBroadcast(v)

Read():
    client queries all the replicas
    replicas respond with the set all values that have a lock-certificate
    client waits for n-f responses and takes the union
```

Writing a value is just running a single locked broadcast. Reading all values is just reading all the lock certificates. 


### Complexity

Observe: both Write and Read protocols take constant rounds and work in asynchrony. Each such operation can have a linear message complexity.


### Analysis

Recall that Locked Broadcast produces a *delivery-certificate*, such that $n-2f$ honest parties received a *lock-certificate* for this value, and no other value can have a *lock-certificate*. Moreover, the value in the certificate has *External-Validity*.

The analysis follows directly from the locked broadcast properties: Termination for a write operation of a non-faulty client follows from the termination of locked broadcast for a non-faulty client. Termination for read operation from waiting for just $n-f$ parties. Validity follows from the fact that write requests are validated and signed by the client. 

Finally, Correctness follows from the *Unique-Lock-Availability* property of locked broadcast and from quorum intersection of any read operation with that set of $f+1$ non-faulty parties.


### From set replication to UTXO replication.

A simple example for using set replication is to maintain a *UTXO* set (a set of unspent transactions). For a simple UTXO system, the system maintains a set of tokens where each token is a pair $tok=(id,pk)$: a unique identifier and a public key (here we omit using denominations for simplicity). A valid write value is of the form $Tx=(tok,tok', sig, lock{-}cert)$ where sig is a signature on $(tok,tok')$ that verifies under the public key $tok.pk$ and the $lock{-}cert$ is a proof that $tok$ is a valid token. The identifier $tok.id$ of the token is used to fix the session id of the locked broadcast instance (to avoid double spending). The External validity check of the lock broadcast checks the validity of the signature.

This means that each token is essentially a write-once object. A transaction marks an active token as spent and creates a new active token in the UTXO set.

Real systems also need to implement more efficient read operations via indexing and timestamping, add check-pointing and garbage collection. 

Reads can also be made linearizable by adding an additional round. We will discuss this in later rounds. For now just mention that the property we would like to obtain is:

* Read correctness: For a read request with response $S$, any response from a request that started after this response, returns a set of values that includes $S$.

Its a good exercise to see why the above protocol does not obtain read correctness and how to fix that (and stay linear communication). Another good exercise is to see how correctness and read correctness implies [linearizability](https://decentralizedthoughts.github.io/2021-10-16-the-ideal-state-machine-model-multiple-clients-and-linearizability/).

It is also possible to carefully *combine* log replication with set replication to get the best of both worlds (fulfilling Lamport’s vision for the Byzantine setting). See [Kuznetsov, Pignolet, Ponomarev, Tonkikh, 2022](https://arxiv.org/pdf/2212.04895.pdf). We plan to cover this in future posts.


### Set Replication, Data Availability, and Verifiable Information Dispersal 

Set replication is a formal way to define some of the requirements that are often informally called **data availability** in the blockchain space and can be formally mapped to [verifiable information dispersal](https://decentralizedthoughts.github.io/2024-08-08-vid/).

> Data availability is the guarantee that the block proposer published all transaction data for a block and that the transaction data is available to other network participants.  --[ethereum](https://ethereum.org/en/developers/docs/data-availability/)


Note that while our protocol above is linear in terms of number of messages, it uses $O(\ell n)$ bits to write and read a message of size $\ell$ bits. In later posts, we will discuss how [VIDs](https://decentralizedthoughts.github.io/2024-08-08-vid/) obtain better guarantees for set replication - for example paying just $O(1)$ per bit when $\ell$ is large enough.

### Acknowledgments

Many thanks to Adithya Bhat and Kartik Nayak for insightful comments.

Your thoughts on [Twitter](https://twitter.com/ittaia/status/1607674657397694465?s=61&t=5e3KM2Kmf3CDaCNUuFLing).