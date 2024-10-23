---
title: Consensus for State Machine Replication
date: 2019-10-15 22:58:00 -04:00
tags:
- dist101
author: Kartik Nayak, Ittai Abraham, Ling Ren
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

An example state machine is the Bitcoin ledger. The state consists of the set of public keys along with the associated Bitcoins (see [UTXO](https://www.mycryptopedia.com/bitcoin-utxo-unspent-transaction-output-set-explained/)). The input (or cmd) to the state machine is a transaction (see [Bitcoin core api](https://bitcoin.org/en/developer-reference#bitcoin-core-apis)). The log corresponds to the Bitcoin ledger. The transition function `apply` is the function that determines whether a transaction is valid, and if it is, performs the desired bitcoin script operation (see [script](https://en.bitcoin.it/wiki/Script)).

### Fault-tolerant state machine replication

Maintaining a state machine using a single server is prone to crashes or Byzantine faults. Thus, the *Fault-Tolerant State Machine Replication* (FT-SMR) approach uses multiple servers, some of which can be faulty. The group of servers, also called replicas, presents the same interface as that of a single server to the clients.  

The server replicas all initially start with the same state. When they receive concurrent commands from clients, honest replicas first need to agree on the sequence of client commands they receive. This problem is called **log replication**, and it is a multi-shot version of consensus. After the sequence is agreed upon, the replicas apply the commands one by one, in the order they appear in the log, using the `apply` transition function. Assuming the transition function is deterministic, all honest server replicas maintain an identical state at all times.

(Note: the formal definition and discussion below are updated in October 2024 to improve rigor and clarity.) 

Next, we will give a formal definition of the FT-SMR problem. Let $log_i[s]$ be the $s$-th entry in the log of replica $i$. Initially, $log_i[s]=\bot$ for all $s$ and $i$. Replica $i$ writes each $log_i[s]$ only once to a value that is not $\bot$. 

**Safety:** Honest replicas agree on each log entry. More precisely, if two honest replicas $i$ and $j$ have $log_i[s] \neq \bot$ and $log_j[s] \neq \bot$, then $log_i[s] = log_j[s]$.

**Liveness:** Every client command is eventually applied (executed). More precisely, if an honest client sends command $x$, then the client eventually receives a proof that $log_i[s] = x$ for some honest replica $i$ and a unique $s$.
  
**Prefix completeness:** If an honest replica $i$ has $log_i[s] \neq \bot$, then for all honest replica $j$ and all indexes $s' \le s$, eventually $log_j[s'] \neq \bot$. 

Some of the requirements for FT-SMR are similar to those for BB and BA. Safety is akin to the agreement property, whereas liveness is similar to the termination property. However, there are a few differences between them:

1. **Consensus on a sequence of values.** FT-SMR needs log replication, or multi-shot consensus. Conceptually, one can sequentially compose single-shot consensus protocol instances. In practice, there are better designs than sequential composition (more discussed below).

2. **Who are the learners?** In BB and BA, the parties executing the protocol are the ones learning the result. In FT-SMR, the replicas engage in the consensus protocol but eventually need to convince external clients of the result. This is reflected in the liveness formulation that the client receives a proof (confirmation) that its command has been applied. In the presence of Byzantine faults, the client may need to communicate with multiple replicas to learn about the result. 

3. **Fault tolerance.** An essential consequence of clients learning the results without participating in the protocol is the best fault tolerance one can hope for. With BB, we know of protocols such as Dolev-Strong that can tolerate $f < n-1$ Byzantine faults among $n$ replicas. SMR protocols can tolerate at most minority Byzantine faults.

4. **External validity.** We do not include a validity requirement in the definition because FT-SMR protocols generally satisfy *external validity*, i.e., validity is left to the application. Some systems may require that any command that makes it into the log pass some application-level validity checks or be generated by the right client (e.g., in the right format or signed by the client who owns the bitcoin). Other systems are more "liberal" when adding commands to the log and choose to weed out invalid commands at the execution stage. 
 
 5. **Fairness.** The liveness requirement above only guarantees that each client command will *eventually* be executed but does not say how two different clients' commands need to be ordered relative to each other. Typically, FT-SMR aims to provide some stronger degree of fairness on the ordering of commands. We will expand on this in future posts.

We make a few additional important remarks about the above definition.
First, we implicitly assume that a proof is sound, i.e., Byzantine replicas cannot fabricate a proof for a false statement. Second, the unique $s$ in liveness makes sure that a command is committed only once. This is important if the command is *non-idempotent*, i.e., the result changes when the command is executed multiple times (e.g., send 1 dollar from A to B). Third, completeness is added to forbid "holes" in the log that stall the execution (honest replicas are unsure whether they will ever be filled).

### Optimizing for a sequence of values

Since FT-SMR protocols agree on a sequence of values, practical approaches for SMR (such as [PBFT](http://pmg.csail.mit.edu/papers/osdi99.pdf), [Paxos](https://lamport.azurewebsites.net/pubs/paxos-simple.pdf), etc.) use a steady-state-and-view-change approach to design log replication. In the steady state, there is a designated leader that drives consensus. Typically, the leader does not change until it fails to make progress (e.g., due to network delays) or if Byzantine behavior is detected. In either case, the replicas vote to de-throne the leader and elect a new one. The process of choosing a new leader is called view-change. The stable leader for extended periods yields simplicity and efficiency when the leader is honest. However, it also reduces the amount of *decentralization* and can cause delays if Byzantine replicas are elected as leaders.

### Separation of concerns

The process of adding a new command to a FT-SMR can be decomposed into three tasks:

1. Disseminating the command 
2. Committing the command
3. Executing the command  

Many modern FT-SMR systems have separate sub-systems for each task. This allows each task to work as a separate system in parallel. Each sub-system can optimize for parallelization, can have a separate buffer of incoming requests, and can stream tasks to the next sub-system. Separating into sub-systems allows to optimize and tune each one and to better detect bottlenecks. See [this post](https://decentralizedthoughts.github.io/2019-12-06-dce-the-three-scalability-bottlenecks-of-state-machine-replication/) for the basics of SMR task separation and [this post](https://decentralizedthoughts.github.io/2022-06-28-DAG-meets-BFT/) for the modern separation of the data dissemination stage. 


### Acknowledgments

Thanks to [Maxwill](https://twitter.com/tensorfi) and Julian Loss for suggestions to improve the definition.

Please leave comments on [Twitter](https://twitter.com/kartik1507/status/1185321750881538050?s=20)
