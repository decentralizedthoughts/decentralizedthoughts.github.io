---
title: Consensus for State Machine Replication
date: 2019-10-15 22:58:00 -04:00
published: false
tags:
- dist101
author: Kartik Nayak, Ittai Abraham
---

We introduced definitions for consensus, Byzantine Broadcast (BB) and Byzantine Agreement (BA), in an [earlier post](https://decentralizedthoughts.github.io/2019-06-27-defining-consensus/). In this post, we will discuss how consensus protocols are used in State Machine Replication ([SMR](https://en.wikipedia.org/wiki/State_machine_replication)), a fundamental approach in distributed computing for building fault-tolerant systems. We will compare and contrast this setting to that of traditional BB and BA. A [follow up post](https://decentralizedthoughts.github.io/2022-11-19-from-single-shot-to-smr/) discusses the reductions from one abstraction to the other in the omission failure model.



### State machine
We will start with the definition of a state machine. A state machine, at any point, stores a *state* of the system. It receives *inputs* (also referred to as *commands*). The state machine applies these inputs in a sequential order using a *transition function* to generate an *output* and an *updated* state. A succinct description of the state machine is as follows:

```
state = init
log = []
while true:
  on receiving cmd:
    log.append(cmd)
    state, output = apply(cmd, state)
```

Here, the state machine is initialized to an initial state `init`. When it receives an input `cmd`, it first adds the input to a `log`. It then *executes* the `cmd` by applying the transition function `apply` to the state. As a result, it obtains an updated state and an output `output`. 

In a client-server setting, the server maintains the state machine, and clients send commands to the server. The output is then sent back to the client.

An example state machine is the Bitcoin ledger. The state consists of the set of public keys along with the associated Bitcoins (see [UTXO](https://www.mycryptopedia.com/bitcoin-utxo-unspent-transaction-output-set-explained/)). The input (or cmd) to the state machine is a transaction between parties (see [Bitcoin core api](https://bitcoin.org/en/developer-reference#bitcoin-core-apis)). The log corresponds to the Bitcoin ledger. And the transition function `apply` is the function that determines whether a transaction is valid, and if it is, performs the desired bitcoin script operation (see [script](https://en.bitcoin.it/wiki/Script)).

### Fault-tolerant state machine replication
Maintaining a state machine using a single server is prone to crashes or Byzantine faults. Thus, the *Fault-Tolerant State Machine replication* (FT-SMR) approach uses multiple servers, some of which can be faulty. The group of servers, also called replicas, presents the same interface as that of a single server to the clients.  

The server replicas all initially start with the same state. However, when they receive concurrent requests from a client, honest replicas first need to agree on the sequence of client commands received by them. This problem is called **log replication**, and it is a multi-shot version of consensus. After the sequence is agreed upon, the replicas apply the commands one by one, in the order they appear in the log, using the `apply` transition. Assuming the transition is deterministic, all honest server replicas maintain an identical state at all times.

Thus, a FT-SMR system needs to perform fault-tolerant log replication and then execute the commands in the log. Informally, we (at least) need the following guarantees:

**Safety:** Honest replicas agree on each log entry.  

**Liveness:** Honest replicas will eventually apply (execute) every command proposed by every client. 

The requirements for FT-SMR seem similar to those for BB and BA. Safety is akin to the agreement property, whereas liveness is similar to the termination property. However, there are a few differences between them:
1. **Consensus on a sequence of values.** FT-SMR needs log replication, or multi-shot consensus. Conceptually, one can sequentially compose single-shot consensus protocol instances. In practice, SMR protocols may use more clever methods than sequential composition (more discussed below).

2. **Who are the learners?** In BB and BA, the parties executing the protocol are the ones learning the result. In FT-SMR, the replicas engage in the consensus protocol but eventually need to convince clients of the result. In the presence of Byzantine faults, a client may communicate with multiple replicas to learn about the commit. If there are $f$ Byzantine faults, the client needs to communicate with at least $f+1$ replicas to make sure that it has communicated with at least one honest replica.

3. **Fault tolerance.** An essential consequence of clients not participating in the protocol is the best fault tolerance one can hope for. With BB, we know of protocols such as Dolev-Strong that can tolerate $f < n-1$ Byzantine faults among $n$ replicas. SMR protocols can tolerate at most minority Byzantine faults.

4. **External validity.** FT-SMR protocols generally satisfy *external validity*, i.e., every command that makes it into the log must pass some application-level validity checks (e.g., signed by the right client who owns the bitcoin).
 
5. **Fairness.** The liveness requirement above only guarantees that each client command will *eventually* be executed but does not say how two different clients' commands need to be ordered relative to each other. Typically, FT-SMR aims to provide some stronger degree of fairness on the ordering of commands. We will expand on this in future posts.

### Optimizing for a sequence of values

Since FT-SMR protocols agree on a sequence of values, practical approaches for SMR (such as [PBFT](http://pmg.csail.mit.edu/papers/osdi99.pdf), [Paxos](https://lamport.azurewebsites.net/pubs/paxos-simple.pdf), etc.) use a steady-state-and-view-change approach to architect log replication. In the steady-state, there is a designated leader that drives consensus. Typically, the leader does not change until it fails to make progress (e.g., due to network delays) or if Byzantine behavior is detected. If either case, the replicas vote to de-throne the leader and elect a new one. The process of choosing a new leader is called view-change. The presence of a single leader for more extended periods yields simplicity and efficiency when the leader is honest. However, it also reduces the amount of *decentralization* and can cause delays if Byzantine replicas are elected as leaders.

### Formal definition of state machine replication
Formally defining the FT-SMR problem (or the log replication problem) turns out to be somewhat tricky. For starters, our informal definition above only talks about replicas that agree on and apply commands; it does not capture the requirement that clients need to receive confirmation that their commands have been applied. 

The informal definition also allows the following problematic situations. Some command is committed at log entry $k$, and no command will ever be committed at entry $k-1$ but honest replicas do not know that. This is problematic because honest replicas must execute each command one by one, but entry $k-1$ has a "hole" that will never be filled and stall the protocol forever. For another example, the informal definition also allows one command to be committed multiple times in the state machine. This is problematic if the command is *not idempotent*, e.g., "transfer 1 dollar from A to B". 

It requires a lot of care to come up with a formal definition that covers all the good protocols following diverse paradigms but also rejects all the contrived problematic protocols. Below is our latest attempt. 

Let $log_i[s]$ be the $s$-th entry in the log of replica $i$. Initially, $log_i[s]=\bot$ for all $s$ and $i$. Replica $i$ will write each $log_i[s]$ only once to a value that is not $\bot$. 

**Safety:** If two honest replicas $i$ and $j$ have $log_i[s] \neq \bot$ and $log_j[s] \neq \bot$, then $log_i[s] = log_j[s]$.

**Liveness:** If an honest client sends command $x$, then eventually there exists some $i$ and a unique $s$ such that the client receives a proof that $log_i[s] = x$.

**Proof soundness:** If a client receives a proof that $log_i[s] = x$, then some honest replica $j$ has $log_j[s] = x$. 
  
**Completeness:** If an honest replica $i$ has $log_i[s] \neq \bot$, then for all honest replica $j$, and all $s' \geq s$, eventually $log_j[s'] \neq \bot$. 

**Integrity:** If $log_i[s] = x$ where $i$ is an honest replica and $x$ is a command that only client $c$ can generate, then $c$ indeed sent command $x$. 

In the above definition, safety is self-explanatory. Liveness is stated from the client's perspective, and it also makes sure a command is committed only once. 
Proof soundness says that (Byzantine) faulty replicas cannot fool a client. Completeness prevents "holes" in the log. Integrity says that a command can only be created by the right client. 

### Separation of concerns

The process of adding a new command to a FT-SMR can be decomposed into three tasks:

1. Disseminating the command 
2. Committing the command
3. Executing the command  

Many modern FT-SMR systems have separate sub-systems for each task. This allows each task to work as a separate system in parallel. Each sub-system can optimize for parallelization, can have a separate buffer of incoming requests, and can stream tasks to the next sub-system. Separating into sub-systems allows to optimize and tune each one and to better detect bottlenecks. See [this post](https://decentralizedthoughts.github.io/2019-12-06-dce-the-three-scalability-bottlenecks-of-state-machine-replication/) for the basics of SMR task separation and [this post](https://decentralizedthoughts.github.io/2022-06-28-DAG-meets-BFT/) for the modern separation of the data dissemination stage. 


### Acknowledgments

Thanks to [Maxwill](https://twitter.com/tensorfi) for suggestions to improve the definition of safety and liveness.

Please leave comments on [Twitter](https://twitter.com/kartik1507/status/1185321750881538050?s=20)
