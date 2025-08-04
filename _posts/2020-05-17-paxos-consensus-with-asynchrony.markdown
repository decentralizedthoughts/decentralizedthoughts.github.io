---
title: Paxos - Consensus with Crash Failures under Asynchrony
date: 2020-05-17 03:10:00 -07:00
published: false
tags:
- dist101
- SMR
- consensus
- crash
author: Kartik Nayak
---

We continue our series of posts on [State Machine Replication](https://decentralizedthoughts.github.io/2019-10-15-consensus-for-state-machine-replication/) (SMR). In this post, we extend our post on [Primary-Backup for crash failures](https://decentralizedthoughts.github.io/2019-11-01-primary-backup/) to consider [asynchronous](https://decentralizedthoughts.github.io/2019-06-01-2019-5-31-models/) communication between replicas. The idea discussed here forms the key underpinning for the celebrated [Paxos](https://lamport.azurewebsites.net/pubs/paxos-simple.pdf) protocol.

To explain this idea, we start with the generalized Primary-Backup SMR with crash failures under synchrony (discussed in this [post](https://decentralizedthoughts.github.io/2019-11-01-primary-backup/)). We will discuss what goes wrong under asynchrony and how to fix it.

### Generalized Primary-Backup

Recall that in a generalized primary-backup system, the primary behaves exactly like an ideal state machine until it crashes. If it does crash, the backup takes over the execution to continue serving the client. To provide the client with an interface of a single non-faulty server, the primary sends client commands to all backups before updating the state machine and responding to the client. The backups passively replicate all the commands sent by the primary. In case the primary fails, which is detected by the absence of a "heartbeat", the next designated backup replica j invokes a ("view change", $j$) to all replicas along with the last command sent by the primary in view $j-1$. It then becomes the primary.

For completeness, we have repeated the generalized primary-backup pseudocode below. Assume $n$ replicas with identifiers $\{0,1,2,\dots,n-1\}$.

```
// Replica j

state = init
log = []
resend = []
view = 0
while true:
   // as a Backup
   on receiving cmd from replica[view]:
      log.append(cmd)
      state, output = apply(cmd, state)
      resend = cmd        
   // as a Primary
   on receiving cmd from a client library (and view == j):
      send cmd to all replicas
      log.append(cmd)
      state, output = apply(cmd, state)
      send output to the client library
   // View change
   on missing "heartbeat" from replica[view] in the last t + $\Delta$ time units:
      view = view + 1
      if view == j
         send ("view change", j) to all client libraries
         send resend to all replicas (in order)
   // Heartbeat from primary
   if no client message for some predetermined time t: 
      send "heartbeat" to all replicas (in order)
```

Can we use the above protocol under an asynchronous network communication? No! Here is where the protocol fails:
1. In the above protocol, the primary sends the command cmd to all backup replicas and then immediately executes the state machine (executing apply(cmd, state)) and responds to the client library. Under asynchronous communication, it may so happen that no replica has received the cmd. The primary then crashes without having any backup replicate the command sent by it.

2. In the above protocol, a backup can ascertain whether the primary has crashed -- if it does not receive a cmd or a heartbeat within a prespecified amount of time ($t+\Delta$), then it must be the case that the primary has crashed. However, under asynchronous communication, a backup cannot distinguish between a crashed primary and a delayed heartbeat due to asynchrony in the network. This indistinguishability is fundamental and is the key underpinnning of the famous [FLP](https://decentralizedthoughts.github.io/2019-12-15-asynchrony-uncommitted-lower-bound/) impossibility result.

3. In the above protocol, when a backup needs to invoke a view-change to become the new primary, under asynchrony, it may not know the last command that was executed. Simply maintaining a "resend" variable consisting of the last command does not suffice since the last few commands may not have been received by the backup.

**Attempt 1.** Here is an attempt to fix the above protocol. The key property that synchrony provided was guaranteed delivery within a bounded time. We will attempt to replicate this by having a backup replica acknowledge a message received from the primary -- this ensures that the primary learns of the receipt of the message. Thus, under a modified protocol, the primary will send cmd "request" received from the client to all backup replicas. The primary then waits for an acknowledgment "ack" from all $n$ replicas. Once it receives these acknowledgments, it executes the cmd and responds to the client. It also informs all backup replicas about the receipt of $n$ acknowledgments. The backup replicas execute the cmd only on the receipt of all acknowledgments (and not when it receives a "request").

The modified protocol is simple: it tries to emulate synchrony using acknowledgments. However, a careful reader may have observed that this protocol works *only when no backup replicas have crashed*. In other words, despite using $n$ backups, it cannot tolerate a single crash fault (which is perhaps worse than using a single state machine). If any backup crashes, then the primary will never receive all $n$ acknowledgments, ultimately stopping progress. Due to the FLP impossibility result, the primary cannot distinguish between a crash and an acknowledgement delayed due to asynchrony in the network. Interestingly, the synchronous protocol described earlier could tolerate $f < n$ faults.

**The Paxos approach.** The Paxos approach to fix the above concern is to follow the basic idea in Attempt 1. However, there is a key modification: instead of waiting for acknowledgments from all $n$ replicas, the primary waits for only $> n/2$ acknowledgments. In terms of fault tolerance, it tolerates $< n/2$ crash faults. The fault tolerance is optimal under an asynchronous network (see exercise 5 in this [post](https://decentralizedthoughts.github.io/2019-06-25-on-the-impossibility-of-byzantine-agreement-for-n-equals-3f-in-partial-synchrony/)). We first explain the protocol under a fixed primary; we will discuss the view-change process later.

```
// Replica j

state = init
log = []
last-executed = 0
seq-no = 0
view = 0
acks = []

while true:
   // as a Backup
   on receiving ("request", cmd, seq-no) from replica[view]:
      log[seq-no] = (cmd, "requested")
      send ("ack", cmd, seq-no) to replica[view]
      
   on receiving ("acks", cmd, seq-no) from replica[view]:
      log[seq-no] = (cmd, "acks-received")
      
      // execute commands in the order of their seq-no
      while log.length >= last-executed and log[last-executed].second == "acks-received":
         state, output = apply(log[last-executed].first, state)
         log[last-executed].second = "executed"
         last-executed = last-executed + 1
      
   // as a Primary
   on receiving cmd from a client library (and view == j):
      send ("request", cmd, seq-no) to all replicas
      log.append(cmd, "requested")
      seq-no = seq-no + 1
      
   on receiving ("ack", cmd, seq-no) from a backup replica r:
      acks[seq-no] = acks[seq-no + 1] // TODO(ASSUMES RECEIVES A MESSAGE ONLY ONCE)
      if acks[seq-no] > n/2: // TODO(SHOULD DO THIS ONLY ONCE for a seq-no)
         send ("acks", cmd, seq-no) to all replicas
         log[seq-no] = (cmd, "acks-received")
         // execute commands in the order of their seq-no
         while log.length >= last-executed and log[last-executed].second == "acks-received":
            state, output = apply(log[last-executed].first, state)
            send output to the client library
            log[last-executed].second = "executed"
            last-executed = last-executed + 1
```

EXPLAIN PROTOCOL UNDER GOOD PRIMARY

EXPLAIN WHEN VIEW-CHANGE CAN HAPPEN

PROVIDE CODE FOR VIEW-CHANGE

EXPLAIN HOW A BACKUP TAKES OVER (IN PAXOS AND RAFT)
