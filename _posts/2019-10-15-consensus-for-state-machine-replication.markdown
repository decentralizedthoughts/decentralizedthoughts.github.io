---
title: Consensus for State Machine Replication
date: 2019-10-15 22:58:00 -04:00
published: false
tags:
- dist101
author: Kartik Nayak, Ittai Abraham
---

We introduced definitions for consensus, Byzantine Broadcast (BB) and Byzantine Agreement (BA), in an [earlier post](https://decentralizedthoughts.github.io/2019-06-27-defining-consensus/). In this post, we will discuss how consensus protocols are used in State Machine Replication ([SMR](https://en.wikipedia.org/wiki/State_machine_replication)). We will compare and contrast this setting to that of traditional BB and BA. A [follow up post](https://decentralizedthoughts.github.io/2022-11-19-from-single-shot-to-smr/) discusses the reductions from one abstraction to the other in the omission failure model.

[State Machine Replication](https://www.cs.cornell.edu/fbs/publications/ibmFault.sm.pdf) is a fundamental approach in distributed computing for building fault tolerant systems.

**State machine.** A state machine, at any point, stores a *state* of the system. It receives *inputs* (also referred to as *commands*). The state machine applies these inputs in a sequential order using a *transition function* to generate an *output* and an *updated* state. A succinct description of the state machine is as follows:

```
state = init
log = []
while true:
  on receiving cmd from a client:
    log.append(cmd)
    state, output = apply(cmd, state)
    send output to the client
```

Here, the state machine is initialized to an initial state `init`. When it receives an input `cmd` from a client, it first adds the input to a `log`. It then *executes* the `cmd` by applying the transition function `apply` to the state. As a result, it obtains an updated state and an output `output`. The output is then sent back to the client.

An example state machine is the Bitcoin ledger. The state consists of the set of public keys along with the associated Bitcoins (see [UTXO](https://www.mycryptopedia.com/bitcoin-utxo-unspent-transaction-output-set-explained/)). The input (or cmd) to the state machine is a transaction between parties (see [Bitcoin core api](https://bitcoin.org/en/developer-reference#bitcoin-core-apis)). The log corresponds to the Bitcoin ledger. And the transition function `apply` is the function that determines whether a transaction is valid, and if it is, performs the desired bitcoin script operation (see [script](https://en.bitcoin.it/wiki/Script)).

**Fault Tolerant State machine replication (FT-SMR).** In a client-server setting, the servers maintain a state machine and clients send commands to the servers. Maintaining a state machine using a single server is prone to crashes or Byzantine faults. Thus, the state machine *replication* (SMR) approach uses multiple server replicas, some of which can be faulty. The group of servers presents the same interface as that of a single server to the clients.  

The server replicas all initially start with the same state. However, when they receive concurrent requests from a client, honest replicas first need to agree on the sequence of client commands received by them. This problem is called **log replication**, and it is a multi-shot version of consensus. After the sequence is agreed upon, the replicas apply the commands one by one, in the order they appear in the log, using the `apply` transition. Assuming the transition is deterministic, all honest server replicas maintain an identical state at all times.

Thus, a Fault Tolerant SMR system needs to perform log replication efficiently and then execute the commands in the log. More formally we need to guarantee the following:

**Safety:** Any two honest replicas store the same prefix of commands in their logs. In other words, if an honest replica appends $cmd$ as the $i$th entry of its log, then no honest replica will append $cmd' \neq cmd$ as the $i$th entry of its log.

**Liveness:** Honest replicas will eventually apply (execute) a command proposed by a client. In other words, if a client proposes a command $cmd$, then eventually all honest replicas will (1) have a log entry $cmd$ appended as some $j$th entry in the log and (2) all previous positions $i<j$ in the log will be set.

**Validity:** Each entry in the log of an honest replica can be *uniquely* mapped to a command proposed by a client request.

The requirements for a FT-SMR seem similar to those for BB and BA. Safety is akin to the agreement property, whereas liveness is similar to the termination property. However, there are a few differences between them:
1. **Consensus on a sequence of values.** FT-SMR  needs log replication, or multi-shot consensus. Conceptually, one can sequentially compose single-shot consensus protocol instances. In practice, SMR protocols may use more clever methods than sequential composition (more discussed below).

2. **Who are the learners?** In BB and BA, the parties executing the protocol are the ones learning the result. In FT-SMR, the replicas engage in the consensus protocol but eventually need to convince clients of the result. In the presence of Byzantine faults, the clients in an FT-SMR protocol may communicate with multiple replicas to learn about the commit. If there are $f$ Byzantine faults, the client needs to communicate with at least $f+1$ replicas to ensure that it has communicated with at least one honest replica.

3. **Fault tolerance.** An essential consequence of clients not participating in the protocol is the fault tolerance one can obtain. With BB, we know of protocols such as Dolev-Strong that can tolerate $f < n-1$ Byzantine faults among $n$ replicas. SMR protocols can tolerate at most minority corruption.

4. **External validity.** In the authenticated Byzantine failure model, FT-SMR protocols generally satisfy *external validity*, i.e., a command is said to be valid so far as the client signs the command.

5. **Fairness.** Typically, FT-SMR aims to provide some stronger degree of fairness on the ordering of commands. The liveness definition provided above only guarantees that each client command will *eventually* be executed but does not say how two different clients' commands need to be ordered relative to each other. We will expand on this in future posts.

### Optimizing for a sequence of values

Since FT-SMR protocols agree on a sequence of values, practical approaches for SMR (such as [PBFT](http://pmg.csail.mit.edu/papers/osdi99.pdf), [Paxos](https://lamport.azurewebsites.net/pubs/paxos-simple.pdf), etc.) use a steady-state-and-view-change approach to architect log replication. In the steady-state, there is a designated leader that drives consensus. Typically, the leader does not change until it fails to make progress (e.g., due to network delays) or if Byzantine behavior is detected. If either case, the replicas vote to de-throne the leader and elect a new one. The process of choosing a new leader is called view-change. The presence of a single leader for more extended periods yields simplicity and efficiency when the leader is honest. However, it also reduces the amount of *decentralization* and can cause delays if Byzantine replicas are elected as leaders.


### Separation of concerns

The process of adding a new command to a FT-SMR can be decomposed into three tasks:

1. Disseminating the command 
2. Committing the command
3. Executing the command  

Many modern FT-SMR systems have separate sub-systems for each task. This allows each task to work as a separate system in parallel. Each sub-system can optimize for parallelization, can have a separate buffer of incoming requests, and can stream tasks to the next sub-system. Separating into sub-systems allows to optimize and tune each one and to better detect bottlenecks. See [this post](https://decentralizedthoughts.github.io/2019-12-06-dce-the-three-scalability-bottlenecks-of-state-machine-replication/) for the basics of SMR task separation and [this post](https://decentralizedthoughts.github.io/2022-06-28-DAG-meets-BFT/) for the modern separation of the data dissemination stage. 


### Acknowledgments

Thanks to [Maxwill](https://twitter.com/tensorfi) for suggestions to improve the definition of safety and liveness.

Please leave comments on [Twitter](https://twitter.com/kartik1507/status/1185321750881538050?s=20)
