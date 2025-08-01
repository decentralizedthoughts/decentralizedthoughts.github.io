---
title: Commit-Notify Paradigm for Synchronous Consensus with Omission Faults
date: 2020-09-13 15:09:00 -04:00
tags:
- consensus
- SMR
author: Kartik Nayak, Ittai Abraham
Field name: 
---

We continue our series of posts on [State Machine Replication](https://decentralizedthoughts.github.io/2019-10-15-consensus-for-state-machine-replication/) (SMR). In this post, we move from consensus under [crash failures](https://decentralizedthoughts.github.io/2019-11-01-primary-backup/) to consensus under [omission failures](https://decentralizedthoughts.github.io/2019-06-07-modeling-the-adversary/). We still keep the [synchrony](https://decentralizedthoughts.github.io/2019-06-01-2019-5-31-models/) assumption.

Let's begin with a quick overview of what we covered in previous posts:

1. [Upper bound](https://decentralizedthoughts.github.io/2019-11-01-primary-backup/): We can tolerate up to $n-1$ *crash* failures.

2. [Lower bound](https://decentralizedthoughts.github.io/2019-11-02-primary-backup-for-2-servers-and-omission-failures-is-impossible/): The best we can hope for is to tolerate less than $n/2$ *omission* failures.






### Recap: Primary-Backup for $n$ Replicas Under Crash Faults

In the crash model, the primary behaves as an ideal state machine until it crashes. If it does crash, the backup takes over the execution to continue serving the clients. To provide the clients with an interface of a single non-faulty server, the primary sends client commands to all backups before updating the state machine and responding to the client. The backups passively replicate all the commands sent by the primary. In case the primary fails, which is detected by the absence of a "heartbeat", the next designated backup replica $j$ invokes a ("view change", $j$) to all replicas along with the last command sent by the primary in view $j-1$. It then becomes the primary.

For completeness, we repeat the primary-backup pseudocode below for $n$ replicas with identifiers ${0,1,2,\dots,n-1}$.

    // Replica j

    state = init
    log = []
    view = 0
    while true:

       // as a primary
       on receiving cmd from a client library (and view == j):
          send cmd to all replicas
          log.append(cmd)
          state, output = apply(cmd, state)
          send output to the client library

       // as a backup
       on receiving cmd from replica[view]:
          log.append(cmd)
          state, output = apply(cmd, state)

       // heartbeat from primary
       if no client message for some predetermined time t (and view == j):
          send ("heartbeat", j) to all replicas (in order)

       // view change
       on missing "heartbeat" or cmd from replica[view] in the last t + $\Delta$ time units:
          view = view + 1
          if view == j // I am the leader
             send ("view change", j) to all client libraries
             send resend to all replicas (in order)

Can we use the above protocol under omission failures? ... unfortunately not! This is due to a big difference between crash and omission failures. With crash failures you know who is faulty: if a message does not arrive you know the sender has crashed. With omission failures, you don't know if a missed message is due to a faulty sender or faulty receiver. So a replica may be faulty without knowing it is faulty.

With omission failures, a faulty primary may omit messages to the replicas, then send a message to the client, then crash. So a client receives 'cmd', but there is no backup replicating the command. So how can you commit safely?

### Two choices for safety: Lock-Commit vs Commit-Notify

There are two different ways to solve this problem:
1. The *Lock-Commit* (asynchrony) approach: **before** you *commit* to $x$, make sure that at least $n-f$ non-faulty replicas received a *lock* on $x$. Since any later view change will hear from $n-f$ parties, then quorum intersection will guarantee to hear from at least one party locked on $x$. We will cover the lock-commit approach in a later post - it is the core idea behind [Paxos](https://lamport.azurewebsites.net/pubs/lamport-paxos.pdf)!

2. The *Commit-Notify* (synchrony) approach: **after** you *commit* to $x$, send to all a *notify* of $x$. In addition, make sure the view change waits sufficient time for the notify message to arrive. Since any later view change will hear from $n-f$ parties, then quorum intersection will guarantee the new primary will hear from at least one party that heard the notify of $x$.


A clear advantage of the Commit-Notify approach is that the commit happens one round earlier!
Note that Commit-Notify also comes with several disadvantages:
1. Safety depends on synchrony.
2. Safety is only guaranteed for non-faulty replicas ([non-uniform agreement](https://decentralizedthoughts.github.io/2019-06-27-defining-consensus/)): A replica may commit and then crash before any notify message is sent.

**Simplifying assumption: single shot.** To simplify the presentation we will focus on just *one* decision, not a sequence of decisions. [In the next post](...) we will show how to extend this to multi-shot agreement.


### Commit-Notify: in the steady state

We detail the steady-state protocol tolerating omission failures under a fixed primary; we later discuss the view-change protocol.

    // Replica j

    state = init // the state of the state machine
    log = []     // a log (of size 1) of committed commands
    view = 0     // view number that indicates the current Primary
    highestView = view
    mycmd = null
    active = true // is the replica active in this view

    while true:

       // as a primary
       on receiving cmd from client library and log[0] is empty and view == j: or
       // as a primary or a backup replica
       on receiving ("notify", cmd, view) from any replica and log[0] is empty:
          // update (mycmd, highestView) since some replica may have committed
          (mycmd, highestView) = (cmd, view) 
          // if the replica did not decide yet and has not quit view
          if active == true and log[0] is empty: 
             // commit
             log[0] = cmd
             state, output = apply(cmd, state)
             send output to the client library
             // notify
             send ("notify", cmd, view) to all replicas

In the steady state protocol, the primary receives commands from the client. It sends the command to every replica through ("notify", cmd, view) message. On receiving a ("notify", cmd, view) message, a replica does the following: If it is active in the view and has not committed yet, (1) it commits the cmd, and (2) notifies all replicas. If it is not active in the view, then it just updates the mycmd and highestView variables to "lock" on a value that may have been committed by some other non-faulty replica (useful during view-change). 

Since we have non-uniform agreement, the client needs to wait for f+1 distinct replicas. If a client receives the same output from $f+1$ distinct replicas, then it commits the command with the given output.

The steady-state protocol ensures the following:

**Claim 1:** *Two non-faulty replicas cannot commit to (and be notified of) different values in the same view.*

*Proof:* A primary, even if faulty, will not propose conflicting values since it is an omission fault. Hence, non-faulty replicas cannot commit to different values in the same view. By extension, two honest replicas cannot be notified of different values in the same view.

**Claim 2:** *If a non-faulty replica commits a cmd at time $t$, then all non-faulty replicas $r'$ are notified by time $t+\Delta$. Moreover, if a replica $r'$ is still active in the view and has not committed to a value, it will commit to the same cmd.*

*Proof:* The first statement follows from synchrony assumption. For the second statement, observe that a different value could not have been committed (due to Claim 1) and hence $r'$ will commit the same cmd if it is active in the view and has not committed a value.

Now we need to detail the mechanism for changing views:


### Commit-Notify: changing view with synchrony

       // Replica j
       
       // blame the current primary
       on missing a notify from replica[view] in last t + $\Delta$ time units:
          send ("blame", view) to all replicas

       // as a primary or backup
       on receiving ("blame", view) from f+1 replicas for this view:
          // make other replicas quit view 
          send ("quit view", view) messages to all replicas
          // stop committing in this view
          active = false
          // wait to be notified of commits by other replicas
          wait $2\Delta$ time 
          // set mycmd to cmd with highest view heard (including yourself)
          (mycmd, highestView) = (cmd, view) pair with the highest view herd
          // switch to new view and send status to the new primary
          send ("status", mycmd, highestView) to replica[view]
          send ("primary change", view) to all client libraries
          view = view + 1
          // backups transition to steady state
          active = true 

       // new primary
       on receiving ("status", cmd, view) from f+1 distinct replicas and view == j:
          // set mycmd to cmd with highest view herd (including yourself)
          (mycmd, highestView) = (cmd, view) pair with the highest view herd
          if mycmd != null:
             send ("notify", mycmd, view) to all replicas
          // transition to steady state



The view-change protocol works as follows. If a replica does not receive a notify from the primary for a sufficient amount of time, it sends a "blame" message to all replicas. Any replica, on receiving "blame" messages from $f+1$ distinct replicas will quit view and forward this message to all other replicas. 

After quitting the view, the replicas wait for some time ($2\Delta$ time) to receive any notifications from the commit of a non-faulty replica (we will explain the magic $2\Delta$ number soon). After that, it enters the new view, notifies the new primary of its mycmd value through a status message, notifies client libraries of the primary change, and then transitions to the steady state. The new primary, on receiving a status from $f+1$ distinct replicas, picks a cmd with the highestView and notifies it to all replicas. If all the cmd are empty then the new primary is free to choose any client cmd. It then transitions to the steady state.

We begin the proof by observing that view changing of non-faulty replicas are at most $\Delta$ apart:

**Claim 3:** *If a non-faulty replica quits view (or enters the next view) at time $t$, all non-faulty replicas quit view (or enter the next view) by time $< t+\Delta$.*

*Proof:* This is simply because of the forwarding of the "quit view" message, which arrives within $\Delta$ time.

We are now ready for the key safety claim:

**Commit-Notify Safety:** *If a non-faulty replica $r$ commits cmd in view $v$, then for any non-faulty replicas $r'$, for any view $v'\geq v$ we have that its $(highestCmd, highestView)$ is such that $highestCmd == cmd$ and $highestView \geq v$.*

*Proof:* We will show this in two parts. First, we will show that at the end of view $v$, all non-faulty replicas $r'$ will have $mycmd == cmd$. Then, we will show that for any view $v'>v$ we have that its $(highestCmd, highestView)$ is such that $highestCmd == cmd$ and $highestView \geq v$.*

Since $r$ is non-faulty it will send a notify message to all replicas. If $r$ commits at time $t$, then observe that all other non-faulty replicas must have been in view $v$ until time $t-\Delta$. Otherwise, by Claim 3, $r$ would have quit view by time $t$ and not committed cmd (since active == false). This also implies that no honest replica enters the next view before time $t+\Delta$ (due to the $2\Delta$ wait during view-change). This time suffices for all non-faulty replicas to receive $r$'s notification. Moreover, due to Claim 1, there can be no other value that can be notified. Hence, all non-faulty replicas must store $mycmd == cmd$ and send that in their status message. 

Since the new primary in the next view waits for a status message from $f+1 = n-f$ replicas, at least one of them will be from a non-faulty replica. Since other non-faulty replicas cannot have a mycmd with a view $> v$, the primary of view $v+1$ cannot propose a value other than $cmd$. We can now continue by induction on the views: since the primary must wait for $n-f$ responses, then it must hear from at least one non-faulty party and since it chooses the highest view, it must choose the value cmd (since it is only an omission fault).

Please discuss/comment/ask on [Twitter](https://twitter.com/kartik1507/status/1305245177603330050).

