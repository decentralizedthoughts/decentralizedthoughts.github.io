---
title: From Single-Shot Agreement to State Machine Replication
date: 2022-11-19 04:00:00 -05:00
tags:
- SMR
- omission
author: Ittai Abraham and Kartik Nayak
---

In this post we explore the path from *Single-Shot Agreement*, via *Write-Once Registers*, to *Log Replication*, and finally to *State Machine Replication*. We begin by defining all four problems assuming *minority omission failures* and *partial synchrony*. This post continues our previous posts on [Paxos from Recoverable Broadcast](https://decentralizedthoughts.github.io/2022-11-04-paxos-via-recoverable-broadcast/) and on [State Machine Replication](https://decentralizedthoughts.github.io/2019-10-15-consensus-for-state-machine-replication/). 

### (Single-Shot) Agreement

In *Agreement* (interchangeably called *Consensus*) there are $n$ parties. A minority of the servers may have omission failures. Each party has an input value, and its goal is to output a value such that:

**Uniform Agreement**: Any two parties that output values, these values are equal. 
(*) In the Byzantine case **Agreement**: Any two non-faulty parties output the same value.

**Termination**: All non-faulty parties eventually output a value and terminate.

**Validity**: The output is an input of one of the parties.
(*) In the authenticated Byzantine case **External Validity**: The output is externally valid (for example signed by the client).



Note that [Agreement and Broadcast](https://decentralizedthoughts.github.io/2019-06-27-defining-consensus/) are [deeply connected](https://decentralizedthoughts.github.io/2020-09-14-broadcast-from-agreement-and-agreement-from-broadcast/) in this setting.

### Write-Once Register State Machine Replication

Instead of just $n$ parties, there are two types of entities: some *clients* and $n$ *servers* (sometimes also called *replicas*). A minority of the servers and *any* number of clients may have omission failures.

Each client has a *local* component called a **client library**. The client interacts with the client library and the library interacts with the servers. Essentially, the client library provides the client with the illusion of talking to a single (ideal) entity. 

The clients have inputs and they can send *requests* to their client library. Clients are sequential and will send a new request only after the client library sends back a *response* to the existing request. 

For a Write-Once Register there are two types of requests: ```write(v)``` which gets an input value and returns a value; and ```read``` which returns a response with either an output value or a special value $\bot$, with the following properties:

**Termination**: If a non-faulty client issues a *request* then it eventually receives a *response*.

**Write-Once Agreement**: If two requests return $x$ and $x'$ and  $x$ and $x'$ are both not $\bot$ then $x=x'$. Equivalently, $\|x \cup x' \setminus \{\bot \}\| \leq 1$. 

**Write-Once Validity**: If a request returns a non-$\bot$ value then there was some client write request with this value.

We also require the system to return a non-$\bot$ value after any write.

**Write-Once Correctness**: Any write response, or any response from a request that started after a write response must return a non-$\bot$ value.


Note that if there is just one write request with value $v$, then from correctness and validity the response must be $v$.

*Exercise 1: Show how to implement a fault-tolerant Write-Once Register given an agreement protocol. You will need to implement the client library.*

An alternative way to define a Write-Once Register is that it abstracts an *ideal functionality* that writes down the first value it hears (literally a register that only writes once).

### Log Replication

The setting is the same as above: some clients and $n$ servers and same fault model. Clients can make two types of requests: ```read``` which now returns a **log of values** (or $\bot$ for the empty log)  as a response; and ```write(v)``` which gets an input value and also returns a response that is a log of values.

Clients can have multiple input values at different times. 

**Termination**: If a non-faulty client issues a *request* then it eventually receives a *response*.

**Log Agreement**: Any two requests return logs then one is a prefix of the other.

**Log Validity**: Each value in the log can be uniquely mapped to a write request.

**Log Correctness**: For a write request with value $v$, its response, and any response from a request that started after this write response arrives, returns a log of values that includes $v$.

The ```read``` request may not scale well because the log may have an unbounded size. A more refined read request can ask for parts of the log. We choose this generic interface for simplicity.

An alternative way to define Log Replication is that it abstracts an *ideal functionality* that adds write commands to a log.


### State Machine Replication

There is a state machine which is a function that takes input $cmd$ and current state $S$ and returns the output $out$ and the next state $S'$:

$$
SM(cmd, S)=(out,S')
$$

The state machine has some *genesis state* $S_0$. Note that this is a very general definition. Clients can submit requests  ```cmd``` (can define ```read``` and ```write``` commands via the state machine).  Given a log $L=c_1,\dots,c_k$, naturally define $SM(L)=(out,S)$ as the sequential application of the log of commands $L$ on $SM$ starting with $S_0$. 

The core difference (in terms of what the client sees) between Log replication and SMR replication is that instead of returning a log of values $L$, the client library returns the output of $SM(L)$. So the servers (or the client library) need to execute state machine transactions based on the command log.

The properties of Termination, Agreement, Validity, and Correctness are all as in Log Replication but on the induced log:

**Termination**: If a non-faulty client issues a *request* then it eventually gets a *response*.

**SMR Agreement**: If two requests return outputs $out_1$ and $out_2$ then there are two logs $L_1$ and $L_2$ such that: one is a prefix of the other, $out_1$ is the output of $SM(L_1)$, and $out_2$ is the output of $SM(L_2)$.

**SMR Validity**: The request returns $out$ which is the output of some $SM(L)$ and each value in $L$ can be mapped uniquely to a client request.

**SMR Correctness**: For a request with value $cmd$, its response, and any response from a request that started after this response for $cmd$ arrives, returns the output of some $SM(L)$ such that $L$ includes $cmd$.


Note that SMR replication can implement *any* state machine. In particular, it can also (trivially) implement Log Replication. See this [post](https://decentralizedthoughts.github.io/2019-10-15-consensus-for-state-machine-replication/) and [Schneider's classic](https://www.cs.cornell.edu/fbs/publications/ibmFault.sm.pdf) for more. 

*Exercise 2: Show how to implement SMR Replication given Log replication. In particular, using a bounded amount of space at the client library.*



## From Write-Once Registers to Log Replication

There are two main ways to obtain Log Replication from Write-Once Registers:

- **Array**: servers maintain an array consisting of separate write-once register instances for each position in the array. While each instance is independent, the view number of each instance is global and common to all instances. Once the write-once register instance at position $j$ in the array reaches agreement, the servers start the write-once register instance in the array at position $j+1$. This approach can be extended to use a sliding window of $c \geq 1$ pending write-once register instances. If all write-once register instances for positions  1 up to $x$ in the array are all committed, parties participate (in parallel) in write-once register instances for positions $x+1,\dots,x+c$ of the array. This allows running multiple write-once register instances in parallel. It also makes the reduction to SMR more delicate: must use the largest *consecutive* sequence in the array that is committed to define the actual committed log. As an example, this is the path PBFT takes.


- **Linked list**: servers participate in a perpetual single instance of a write-once register. Each server stores its currently committed log as a linked list $L = c_j \rightarrow ... \rightarrow c_{1}$. Each server then sets its input (proposal) to be a new linked whose head is an uncommitted client command $cmd$ that points to the committed log:  $L' = cmd \rightarrow c_j \rightarrow ... \rightarrow c_{1}$. Agreement is reached on the whole log and each time a new log is committed the servers continue to propose a larger log. While this does not allow parallel agreement instances, it does allow to *pipeline* consecutive agreement instances and also allows for optimistic execution in the SMR setting. For some underlying agreement protocols, pipelining and optimism can provide performance benefits. As an example, this is the path HotStuff takes. 

Your comments on [Twitter](https://twitter.com/ittaia/status/1599895548416270338?s=20&t=RUTyrxNgaIvudyiV5O5IAA).