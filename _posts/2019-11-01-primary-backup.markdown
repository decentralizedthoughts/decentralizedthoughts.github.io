---
title: Primary-Backup State Machine Replication for Crash Failures
date: 2019-11-01 06:10:00 -04:00
tags:
- SMR
- crash
author: Ittai Abraham, Kartik Nayak
---

We continue our series of posts on [State Machine Replication](https://decentralizedthoughts.github.io/2019-10-15-consensus-for-state-machine-replication/) (SMR). In this post we discuss the most simple form of SMR: Primary-Backup for crash failures. We will assume [synchronous](https://decentralizedthoughts.github.io/2019-06-01-2019-5-31-models/) communication. For simplicity, we will consider the case with two replicas, out of which one can crash. Recall that when a party *crashes*, it irrevocably terminates.  

### The Primary-Backup Protocol

The goal is to give the clients exactly the same experience as if they are interacting with an ideal state machine as described below. 

```
// Ideal State Machine

state = init
log = []
while true:
   on receiving cmd from a client:
      log.append(cmd)
      state, output = apply(cmd, state)
      send output to the client
```

1. To avoid duplication of input, each command ```cmd``` includes a unique identifier. 
2. To avoid duplication of output, each ```output``` includes a unique identifier and also the unique identifier of the ```cmd```.

The above state machine can be made tolerant to a single crash failure with via the primary-backup paradigm. 

**Primary.** The ```primary``` behaves exactly like an ideal state machine until it crashes. However, if it does crash, it needs the backup to take over the execution and continue serving the client. 

```
// Primary

state = init
log = []
while true:
   on receiving cmd from a client library:
     send cmd to the backup
     log.append(cmd)
     state, output = apply(cmd, state)
     send output to the client library
   if no client message for some predetermined time t: 
     send "heartbeat" to backup
```

The code for the primary is the same as that of an ideal state machine except for two changes. First, it needs to maintain an invariant: *update the backup before responding back to the client*. Due to synchrony, the message is bound to reach the backup within a known bounded delay $\Delta$. Second, the backup may not be able to differentiate between a crashed primary and absence of client commands. In either case, the backup receives no information. Hence, the primary sends an occasional *heartbeat* to indicate that it has not crashed.

**Backup.** The ```backup``` passively replicates as long as it either hears client commands or heartbeats. If it receives neither, then it invokes a *view change* by sending ("view change", 1) to the clients. Once a view-change has occurred, it is also responsible for responding back to the client. 

```
// Backup

state = init
log = []
view = 0
while true:
   on receiving cmd for the first time from the primary or a client library:
      log.append(cmd)
      state, output = apply(cmd, state)
   if view == 1:
      send output to the client library
   on missing "heartbeat" from primary in the last t + $\Delta$ time units:
      view = 1
      send ("view change", 1) to all client libraries
```

Note that in some cases ```cmd``` may arrive twice (from both the primary and the client library), in this case the backup ignores the second time (here we use the fact that ```cmd``` contains a unique identifier that can detect this duplication).


**Client.** In the ideal world, the client needs to interact with only a single state machine. With the primary-backup paradigm, it needs to be aware of their existence and send messages accordingly. Thus, we augment the client with a *client library*. The ```client library``` acts as the required relay between the client in the ideal world and the real world protocol. It implements a mechanism to switch from primary to backup:

```
// Client library 

view = 0
replica = [primary, backup]
while true:
   on receiving cmd from client
      send cmd to replica[view]
   on receiving output for the first time from a replica
      send output to client
   on receiving ("view change", 1) from backup
      view = 1
```

Note that in some cases, the same ```output``` may arrive twice (from both the primary and the backup), in this case the client library ignores the second time (here we use the fact that ```output``` contains a unique identifier and can detect this duplication).

Due to the invariant maintained by the primary, a client knows that the response it got from a primary must have been sent to the backup. If the backup crashes then the primary will continue to serve the clients. If the primary is faulty and crashes then the backup is guaranteed to have seen any command whose output was returned to the client.

**A couple of remarks on the setting.**

1. We assumed that the adversary can crash any client and that all non-fualty client messages arrive at the primary/backup and vice-versa. This Primary-Backup protocol works even if we assume that the adversary can fail any client by [omission failures](https://decentralizedthoughts.github.io/2019-06-07-modeling-the-adversary/). To handle this model, even with an ideal state machine we need to maintain a unique identifier for every command sent to the state machine and use a retry mechanism.

2. In practice, there is often an out-of-band procedure to reset the system to allow the primary to be the primary again after it recovers from its failure. For example, one can first stop the backup and then restart the whole system. 

3. In the above description, we assume that there will be at most 1 crash. We now discuss a mechanism for $n > 2$ capable of tolerating any $f<n$ crash faults.

### Generalized Primary-Backup

When there are $n>2$ replicas the new primary must do some more work to continue to maintain the invariant: **send the command to all the backups before responding back to the client**. 

Assume $n$ replicas with identifiers $\{0,1,2,\dots,n-1\}$. A major problem is that a replica may crash in the middle of sending to all the backups. We fix this using two measures:

1. The primary sends the command to the backup **in order**, so messages first arrive to the next primary, then to the next next primary and so on.
2. Each ```replica j``` maintains a *resend* variable that stores the last command it received from the primary. If $j$ becomes the new primary it resends the last command to all replicas when it does a view change. 

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
      send cmd to all replicas (in order)
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

This protocol implements state machine replication with $n$ servers in synchrony that is resilient to $n-1$ crash failures.


### Notes

1. Clients need a mechanism to discover who is the current primary. For example, they can send a query to all replicas to learn what is the current view number.
2. The crash model is actually quite useful to model replicas with secure hardware.  
3. If sending in a particular order is not allowed, or we want to use randomization to choose the next primary, then an additional round is needed where each party sends to the new primary its latest command, and then the new primary can resend it.


### Acknowledgments

We would like to thank Tim Roughgarden for insightful comments and noticing an error in the $n>2$ case. 

Please leave comments on [Twitter](https://twitter.com/ittaia/status/1191141070685507586?s=20)