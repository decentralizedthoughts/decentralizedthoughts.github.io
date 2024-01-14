---
title: 'The Ideal State Machine Model: Multiple Clients and Linearizability'
date: 2021-10-16 15:45:00 -04:00
tags:
- dist101
author: Ittai Abraham
---

We introduced state machines and [state machine replication](https://decentralizedthoughts.github.io/2019-10-15-consensus-for-state-machine-replication/) in an earlier post. In this post, we elaborate on the exact notion of safety and liveness that can be obtained by an ideal state machine when there are multiple clients.

First, these definitions highlight the challenges of serving multiple clients. Second, when we implement a *replicated* state machine we need to formally argue that this real environment behaves the same as some ideal environment also with respect to multiple clients. This post will connect the notion of an ideal state machine to Herlihy and Wing's seminal notion of [linearizability](https://cs.brown.edu/~mph/HerlihyW90/p463-herlihy.pdf) from 1987. Linearizability is the *gold standard* in concurrent programming. It captures the powerful and elegant property that overlapping function calls to a *linearizable object* behave as if each function call is executed instantaneously.


### The Ideal State Machine Model
In the *ideal model*, there is a single *server* and a set of *clients*. Clients only communicate with the server. The adversary can corrupt clients and cause them to have omission failures. A client that is not corrupted is called *non-faulty*. We assume a synchronous model of communication where the adversary can delay messages by at most some known bound $\Delta$.  In order to focus on the communication delay effects, we assume that local computation takes zero time.


### A Sequential Client

The client is modeled as a simple state machine that sends commands to the server and listens to the server responses. Importantly, the client is *sequential*: it waits to receive the response of its previous command before sending a new command. This simplifies the client and in some settings also provides a basic flow control mechanism that bounds the total number of in-flight commands as a function of the number of permissioned clients. We model the client as having an external ```command-queue``` and ```response-queue```. Finally, we assume each command has a unique identifier, and the output includes this identifier. Hence, the client can match the response to the request and avoid duplication.


```
// Client state machine
pending = empty
while true
    if pending = empty and command-queue is not empty
        cmd = command-queue.dequeue()
        send <cmd> to server
        pending = cmd
    on <response> from server where response matches pending
        response-queue.enqueue(response)
        pending = empty
```

Note that if a ```<response>``` arrives without a matching pending command it is ignored.

### A batched server implementing a sequential state machine: 
The state machine is defined by the *transition function*  ```apply()``` that takes the existing state and a new command and outputs the new state and the response: ```(state, response) = apply(state, cmd)```. The server uses a *timer* that ticks every $\Delta$ time to batch client commands into *blocks*. It then executes each block and sends the responses to the relevant clients. 

To maintain the history, the blocks of commands are recorded in a log of blocks.

```
// Server state machine
state = init
log = []
counter = 1
while true
    on <cmd> from client
        add (cmd, client) to log[counter]
    on Delta-timer ticking
        for each (cmd,client) in log[counter]
            (state, response) = apply(state, cmd)
            send <response> to client
        counter++
```
We assume here that the server can process all the commands in zero time. Recalls that the adversary controls message delays by up to $\Delta$.

### The Client Experience: Liveness

When a non-faulty client sends a command, it may take up to $3 \Delta$ of network delay before it gets a response: one $\Delta$ to send the command, one $\Delta$ delay for batching, and a final $\Delta$ delay for the response. Here we explicitly ignore the processing and computation time (assume it's zero). So we can state a simple liveness property:

**Liveness**: Each non-faulty client request gets a response after at most $3 \Delta$ time of network delay.

The above requirement is for non-faulty clients. If the client is faulty (can suffer omission faults) then it may happen that the client never receives a response (because the adversary omits the responses at the client).

### The Client Experience: Safety
Now that we defined the liveness property we need to ask: given a request, what should we consider as a correct response from the server? More generally, we will look at a full *client history* (all the requests and responses of all the clients) and ask: is this history correct?

We will give two answers to this question. The first is by saying that a history is correct if it can be generated in an execution in our ideal model:


**Safety (relative to the ideal model)**: a client history is safe if it can be generated in the ideal model.

Our second answer is to use the definition of **[linearizability](http://www.cs.tau.ac.il/~shanir/multiprocessor-synch-2003/linear/notes/linear.pdf)**. We can view each request-response pair as a function call to the state machine object and require that each function call has a **linearization point** at some time between the request and the response. The behavior of the system is as if the function occurs instantaneously at its linearization point and the object behaves like its sequential definition.

Note that since clients may fail, the last client request may not have a response in the client history. Formally, we require that a request with no response either has a linearization point that is after the request or there is no linearization point for this request.

**Safety (linearizability)**: a client history is safe if it is linearizable. 



So these are two ways to say the same thing! Let's say a few words about why that is the case. The single server executes requests as a sequential state machine. The linearization point of a request is precisely the point in time when the server sequentially executes the request (and a request that has no response and no linearization point is exactly the case that this request message was omitted by the adversary).

### Is this a good definition?

On the positive side, we have defined a natural ideal model and showed its equivalent to the strong consistency notion of linearizability. This seems like a good definition - it prevents behaviors that seem to be obviously incorrect, like ignoring commands and reordering them in ways that ignore the client responses. Safety violations like double-spending or equivocation can all be viewed as violations of the ideal model (or essentially of linearizability).

On the negative side, there is considerable arbitrariness in the ideal model: The adversary has the power to delay messages (by at most $\Delta$) and this way can control the order of requests in the blocks. A server can reorder requests and still maintain the definition of safety. Even worse, a server can see the content of client messages but behave as if the message arrived later. During this time, the server can collude with other clients that can send commands based on this information (known as [sandwich attacks](https://medium.com/coinmonks/defi-sandwich-attack-explain-776f6f43b2fd) in the DeFi world). 

Recently there is much interest in this powder of the server and the adversary to reorder, censor, and front-run. The term [Miner Extractable Value (MEV)](https://arxiv.org/abs/1904.05234) captures this in the context of economic value. One approach is to use [MPC](https://eprint.iacr.org/2020/248) to build a functionality that limits the ability of the adversary. We will explore this topic in later posts.

Let's now show how to implement a system that behaves like an ideal system even though it is composed of failure-prone servers.


## Implementing an Ideal State Machine with Two Servers Where One Can Crash

In this part, we will extend the protocol in our [previous post](https://decentralizedthoughts.github.io/2019-11-01-primary-backup/) to the multi-client setting.

### The Two-Server One-Crash Model
There are two *servers* we call ```Primary``` and ```Backup``` and a set of *clients*. Clients only communicate with the two servers. The adversary can cause a crash failure to one of the two servers and also cause omission failures to any number of clients. Clients that have no omission failures are called non-faulty. Communication is synchronous: the adversary can delay messages by at most some known bound $\Delta$.  

Note that the adversary in this model can both control the network delays, cause client omission faults, and crash one of the servers while the adversary in the Ideal Model can only control network delays and cause client omission faults.

Our goal is to obtain a protocol with the following two properties:

1. **Liveness**: Each non-faulty client request gets a response after at most $8 \Delta$ time. Note that we changed the required response time from $3 \Delta$ to $8 \Delta$ and that we only require this for non-faulty clients.
2. **Safety**: for every client history that is created when running this protocol is a client history that can be generated in the ideal model. In more detail, for any adversary behavior in this model when running the protocol, there exists some adversary behavior in the ideal model that generates the client history. 
Note that the adversary behavior captures all the power the adversary has in each model. 

### A Fault-Tolerant Client

The basic idea is to interact with the Primary server until the Backup informs the client to change view with a new ```<view change>``` message.

The second idea is to resend the request if a ```<view change>``` message arrives but no response.

```
// Client state machine
pending = empty
leader = Primary
while true
    if pending = empty and command-queue is not empty
        cmd = command-queue.dequeue()
        send <cmd> to leader
        pending = cmd
    on <response> where response matches pending
        response-queue.enqueue(response)
        pending = empty
    on <view change> from Backup
        leader = Backup
        if pending not empty
            send <cmd> to leader
```

Here it may happen that the same ```<response>``` arrives twice (once from the Primary and once from the Backup). The protocol will simply ignore the second ```<response>```.

### The Primary

The main change is that the Primary sends the block of requests to the Backup server *before* executing them. Note that even if there are no client requests, an empty block is sent to the Backup every $\Delta$ time - this is a form of a heartbeat that will allow the Backup to detect if the Primary has crashed.

```
// Primary state machine
state = init
log = []
counter = 1
while true
    on <cmd> from client
        add (cmd, client) to log[counter]
    on Delta-timer ticking
        send <log[counter]> to Backup
        for each (cmd, client) in log[counter]
            (state, response) = apply(state, cmd)
            send <response> to client
        counter++
```

### The Backup

The backup waits to receive a block message. If it does not arrive on time then it deduces that the Primary crashed and assumes the role of the leader.

When the Backup is not the leader it does not send responses to the clients. When the Backup becomes the leader is will send the ```responses``` of the previous block (in case the Primary crashed before sending the responses). In this case, the client may receive a response twice (having unique request ids allows to ignore the second response).

Finally, the client may need to resend its command. The Backup may receive the same command: once from the Primary and once from the client resend. So the Backup checks the command from the client is not already part of a previous block.


```
// Backup state machine
state = init
log = []
counter = 1
leader = Primary
set view-change-timer to 2 Delta
while true
    // as a follower
    on <log[counter]> from leader and 
         responses = empty
         for each (cmd, client) in log[counter]
            (state, response) = apply(state, cmd)
            add (response, client) to responses
        counter++
        reset view-change-timer to 2 Delta
    // view change
    on view-change-timer expiring
        leader = Backup
        for each (response, client) in responses
            send <response> to client
        for each client
            send <view change> to client
    // as a leader
    on <cmd> from client and leader = Backup
        if (cmd, client) not in log[counter] or log[counter-1]
            add (cmd, client) to log[counter]
    on Delta-timer ticking and leader = Backup
        for each (cmd,client) in log[counter]
            (state, response) = apply(state, cmd)
            send <response> to client
        counter++
```



### Liveness analysis

First, as long as the Primary does not crash, the Backup will not initiate a view change. In that case, commands sent by a client will arrive in $<\Delta$ time, be processed in a batch in $<\Delta$ time, and sent a response in $<\Delta$ time, for a total of $<3\Delta$ time.

Now consider a client command and the Primary crashing. There are two cases:

1. The Primary crashes after sending the client command to the Backup (but before sending a response). In this case, the Backup will receive the command at time $<3\Delta$. Will detect the Primary crashed by time $<5\Delta$, and will send the response. The client will receive the response in at most $<6\Delta$ time.


2. The Primary crashes just before sending the client command to the Backup, so just at $<2 \Delta$ from when the client sends a command. This means that the last command from the Primary to the Backup is sent at $<\Delta$ and arrives at $<2\Delta$ from the client command. So the Backup will start a view change at time $<4\Delta$. The client will receive the view change in time $<5\Delta$. The client will resend the command to the Backup and get a response after $<3 \Delta$. So the client will receive a response in at most $<8 \Delta$ time.

Finally, after the view change, each command sent to the Backup will get a response in $<3 \Delta$ time.

### Safety analysis  

For a client command, let's define its linearization point as:

1. **Type 1**: If the Primary sends the command to the Backup then the time it sends is the linearization point.
2. **Type 2**: Otherwise, the Primary crashed before sending the command to the Backup so define the linearization point as the time the Backup executes the command.

Observe that these points are indeed between the client request and the response and that this definition captures all cases.

Given this, let's show that the response is equal to a response of the sequential execution that respects the linearization points.

**The core observation**: due to the Backup's $2 \Delta$ view change timer, all the type 1 linearization points reflect messages that will arrive at the backup and be executed by the Backup before all the executions that are related to type 2 linearization points. 

Since the Primary is sequential, all the type 1 linearization points respect the sequential execution at the Primary. If Primary crashes, then all the type 1 linearization points are also respected at the backup since it is sequential, and it receives all of them.

Since the Backup is sequential, then all the type 2 linearization points respect the sequential execution at the Backup and they all appear after all the type 1 linearization points as needed.

### Acknowledgments
Many thanks to Matan, Avihu, and Noa for fixing several bugs in the Backup state machine pseudo code.



Your decentralized thoughts and comments on [Twitter](https://twitter.com/ittaia/status/1451515584139730949?s=20)
