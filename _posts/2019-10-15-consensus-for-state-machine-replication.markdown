---
title: Consensus for State Machine Replication
date: 2019-10-15 22:58:00 -04:00
tags:
- dist101
author: Kartik Nayak, Ittai Abraham, Ling Ren
---

We introduced definitions for consensus, Byzantine Broadcast (BB) and Byzantine Agreement (BA), in an [earlier post](https://decentralizedthoughts.github.io/2019-06-27-defining-consensus/). In this post, we discuss how consensus protocols are used in **State Machine Replication** ([SMR](https://en.wikipedia.org/wiki/State_machine_replication)), a fundamental approach in distributed computing for building fault-tolerant systems. We compare and contrast this setting to that of traditional BB and BA. A [follow-up post](https://decentralizedthoughts.github.io/2022-11-19-from-single-shot-to-smr/) discusses the reductions from one abstraction to the other in the omission failure model.

(Note: the definitions and discussion below are updated in October 2024 to improve rigor and clarity.) 

### State machine

Let's start with the definition of a state machine. A state machine, at any point, stores a *state* of the system. It receives *inputs* (also referred to as *commands*). The state machine applies these inputs in a *sequential order* using a deterministic *transition function* to generate an *output* and an *updated* state. A succinct description of the state machine is as follows:

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

An example state machine is the Bitcoin ledger. The state consists of the set of public keys along with the associated Bitcoins (see [UTXO](https://www.mycryptopedia.com/bitcoin-utxo-unspent-transaction-output-set-explained/)). Each input (or cmd) to the state machine is a transaction (see [Bitcoin core api](https://bitcoin.org/en/developer-reference#bitcoin-core-apis)). The log corresponds to the Bitcoin ledger. The transition function `apply` is the function that determines whether a transaction is valid, and if it is, performs the desired bitcoin script operation (see [script](https://en.bitcoin.it/wiki/Script)).



### Multi-shot consensus - a server centric definition

The central building block of state machine replication is *multi-shot consensus*. In this variant of the consensus problem, a set of servers (also called replicas) agree on a dynamically growing log of commands. These commands arrive as input to the servers over time (presumably from clients but we abstract that away).

Let $log_i[s]$ be the $s$-th entry in the log of replica $i$. Initially, $log_i[s]=\bot$ for all $s$ and $i$. Replica $i$ writes each $log_i[s]$ *only once* to a value that is not $\bot$. 

**Safety:** Non-faulty replicas agree on each log entry, i.e., if two non-faulty replicas $i$ and $j$ have $log_i[s] \neq \bot$ and $log_j[s] \neq \bot$, then $log_i[s] = log_j[s]$.

**Liveness:** Every input $x$ that arrives at a non-faulty replica is eventually recorded in the log, i.e., eventually  $\exists s$ and non-faulty replica $i$ such that $log_i[s] = x$.

**Validity:** There is an *injective mapping* from the set of log entries (not including $\bot$) to the set of inputs. In other words, every log entry must originate from an input and every input appears in the log at most once. Many systems have additional *external validity* requirements (discussed soon).
  
**Prefix completeness:** If a non-faulty replica $i$ has $log_i[s] \neq \bot$, then for all non-faulty replica $j$ and all indices $s' \le s$, eventually $log_j[s'] \neq \bot$. 

#### Comparison to single-shot consensus, broadcast, and other notes

The requirements are similar in multi-shot consensus and single-shot consensus.  However, there are some differences:

1. **Consensus on a sequence of values.** Conceptually, one can sequentially compose single-shot consensus instances to obtain multi-shot consensus. In practice, there are better designs than sequential composition, such as the popular steady-state + view-change paradigm.

2. **External validity.** Besides the above injective mapping validity, multi-shot consensus typically satisfies *external validity*, i.e., additional validity requirements imposed by the application. For example, a system may require that any command that makes it into the log must have the right format and be generated by the right client (e.g., signed by the client who owns the bitcoin). Other systems may be more "liberal" when adding commands to the log and choose to weed out invalid commands at the execution stage. 
 
3. **Fairness.** The liveness requirement above only guarantees that each input is *eventually* committed but does not say how two different inputs need to be ordered relative to each other. Many protocols desire some stronger degree of fairness on the ordering of commands. We plan to expand on this issue in future posts as it is deeply connected to challenges in MEV.

We now move to a client centric view of the world for state machine replication and show how multi-shot consensus can be used to implement state machine replication. 

### State machine replication - a client centric definition

Here, we assume that in addition to servers (some of which may be faulty), there are also clients. Any number of clients can be fault -- crash, omission, or Byzantine in the respective model. 

Let $L$ be a log of consecutive commands and $SM(L)$ be the state machine after applying this sequence of commands. Each $SM(L)$ also includes an output, denoted $out$, as part of the resulting state, and $out$ is sent back to the client as a response. 

The requirements for state machine replication are:

**SMR Liveness**: If a non-faulty client issues a *request*, then it eventually gets a *response*. 

**SMR Safety**: If two requests return outputs $out_1$ and $out_2$, then there are two logs $L_1$ and $L_2$ such that: one is a prefix of the other, $out_1$ is the output of $SM(L_1)$, and $out_2$ is the output of $SM(L_2)$.

**SMR Validity**: Any response $out$ returned to a non-faulty client is the output of some $SM(L)$ where there is an injective mapping from values in $L$ to the set of client requests.

**SMR Correctness**: For a request with value $cmd$, its response, and any response from a request that started after this response for $cmd$ arrives, returns the output of some $SM(L)$ such that $L$ includes $cmd$.

* The first three requirements are analogous to the *Liveness, Safety, and Validity* of multi-shot consensus. The SMR Correctness property has no analog as it is a consistency property between the client, not the servers. There may be variants of this property that provide weaker consistency between clients, or slightly stronger properties that aim to simulate an ideal functionality (see [this post](https://decentralizedthoughts.github.io/2021-10-16-the-ideal-state-machine-model-multiple-clients-and-linearizability/)).

See our [follow-up post](https://decentralizedthoughts.github.io/2022-11-19-from-single-shot-to-smr/) for more about this definition.

The client centric nature of SMR has a direct consequence on fault tolerance. We know of Byzantine broadcast protocols such as Dolev-Strong that can tolerate $f < n-1$ Byzantine faults among $n$ parties. A client centric SMR protocol can tolerate at most minority Byzantine faults.


### From multi-shot consensus to state machine replication

To achieve the client centric state machine replication given a multi-shot consensus protocol, all we need is a client protocol that maintains the SMR Correctness property. We present one next.

The servers run a multi-shot consensus protocol. The clients send requests to the servers. Once a server sees a request, it uses the request as an input to the multi-shot consensus. 
A server executes a request $cmd \neq \bot$, if all the previous entries in the log are non-$\bot$ and have been executed. A server returns a response to the client once it executes the request.

#### Proof sketch
SMR Liveness follows from Liveness and Prefix completeness of multi-shot consensus.
SMR Safety follows directly from Safety of multi-shot consensus.
SMR Validity follows directly from Validity of multi-shot consensus.
For SMR Correctness, consider a response for $cmd$ that is placed in $\log_i[k]$. We know that all log entries from 1 to $k$ are filled and executed. So clearly any request that starts after this response must be committed to a slot $>k$ in the log. Hence, from SMR Safety, this new response will see $\log[k]=cmd$ as required.


### Separation into sub-systems

The process of adding a new command to a state machine replication protocol can be decomposed into three tasks:

1. Disseminating the command 
2. Committing the command in multi-shot consensus
3. Executing the command  

Many modern state machine replication systems have separate sub-systems for each task. This allows us to optimize and tune each sub-system separately. See [this post](https://decentralizedthoughts.github.io/2019-12-06-dce-the-three-scalability-bottlenecks-of-state-machine-replication/) for the basics of SMR task separation and [this post](https://decentralizedthoughts.github.io/2022-06-28-DAG-meets-BFT/) for the modern separation of the data dissemination stage. 

### Acknowledgments

Thanks to [Maxwill](https://twitter.com/tensorfi) and Julian Loss for suggestions to improve the definition.

Please leave comments on [Twitter](https://twitter.com/kartik1507/status/1185321750881538050?s=20)
