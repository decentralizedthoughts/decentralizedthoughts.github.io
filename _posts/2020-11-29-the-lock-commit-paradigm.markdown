---
title: The Lock-Commit Paradigm
date: 2020-11-29 08:02:00 -05:00
tags:
- consensus101
author: Ittai Abraham, Kartik Nayak
---

In this post, we explore one of the most celebrated and widely used techniques for reaching consensus: the **Lock-Commit paradigm**. This approach is a key technique of [DLS88](https://groups.csail.mit.edu/tds/papers/Lynch/jacm88.pdf), Lamport's [Paxos](https://lamport.azurewebsites.net/pubs/lamport-paxos.pdf), and many subsequent protocols. Protocols like [Raft](https://raft.github.io/), [PBFT](http://pmg.csail.mit.edu/papers/osdi99.pdf), [Tendermint](https://arxiv.org/pdf/1807.04938.pdf), [SBFT](https://arxiv.org/pdf/1804.01626.pdf), [Casper FFG](https://arxiv.org/pdf/1710.09437.pdf), [HotStuff](https://arxiv.org/pdf/1803.05069.pdf), etc., are all based on this paradigm.

We exemplify the *Lock-Commit paradigm* with a simple single-shot [synchronous protocol](/2019-06-01-2019-5-31-models/) (with message delay at most $\Delta$) for [uniform consensus](/2019-06-27-defining-consensus/) that is tolerant to $f$ [omission](/2020-09-13-synchronous-consensus-omission-faults/) failures, given $2f<n$.

Related posts:

1. It is [impossible to solve consensus](/2019-11-02-primary-backup-for-2-servers-and-omission-failures-is-impossible/) with  $2f \geq n$ omission failures. As an exercise: extend this lower bound to show it is impossible to tolerate $k\+2f \\geq n$ for $k$ crash failures and $f$ omission failures.

2. Using the [Commit-Notify paradigm](/2020-09-13-synchronous-consensus-omission-faults/) in synchrony, *non-uniform* consensus is possible for $t<n/2$ *omission* failures (recall that for omision failures, non-uniform consensus means that faulty replicas may commit on incorrect values). 

3. In synchrony, consensus is possible for $k$ [crash failures](/2019-10-31-primary-backup/), for any $k<n$.


4. In a [follow-up post](/2020-11-30-the-lock-commit-paradigm-multi-shot-and-mixed-faults/), we extend the lock-commit paradigm to a multi-shot protocol that can tolerate both $f$ omission failures and $k$ [crash](/2019-06-07-modeling-the-adversary/) failures given $k\+2f<n$.

5. Protocols in partial synchrony that use the lock-commit paradigm: [Streamlet](https://decentralizedthoughts.github.io/2020-05-14-streamlet/), [Benign Hotstuff](https://decentralizedthoughts.github.io/2021-04-02-benign-hotstuff/), [Raft with Chaining](https://decentralizedthoughts.github.io/2021-07-17-simplifying-raft-with-chaining/), [Information Theoretic HotStuff](https://decentralizedthoughts.github.io/2021-09-20-information-theoretic-hotstuff-it-hs-part-one/).

## Lock-Commit Paradigm

Consider the task of solving consensus in a system with *clients* and $n$ *replicas*. Clients send commands to the replicas and the goal of the replicacs (in the single shot case) is to decide on one command. In the **Primary-Backup approach**, the protocol progresses in *views*. In each view $v$, one designated replica is the *primary replica* and the other replicas are the *backup replicas* of this view. The primary of a view needs to *propose* a command and replica need to eventually *commit* (or decide) on a command.  There is a *view change trigger* protocol that decides when to globally execute a *view change* protocol that increments the view. 

The main safety risk in Primary-Backup based consensus protocols is that a replica *commits* to a value and later a different replica commits to a different value. The only way this can happen is if a new primary in a new view proposes a different value. To guarantee this will not happen the **Lock-Commit paradigm** does two crucial things:

1. *Lock a quorum before you Commit*. To commit a value $cmd$, the primary of view $v$ first makes sure there is a **quorum** of replicas that store a lock that consists of a **lock-value** $cmd$ and a **lock-view** $v$. This is typically done by having the primary *propose* the value $cmd$ and receive $n-f$ *acknowledgments* that the value $cmd$ is locked in view $v$.

2. *Read a quorum before you Propose*. When a new primary starts a new view, it runs a *view change* protocol. In this protocol, the new primary of view $v$ needs to decide which value to propose (and eventually commit) in view $v$. The new Primary must read the locks of previous views from a **quorum** of replicas and must adopt the *lock-value* with the **highest** *lock-view* it sees.

Intuitively, this approach is safe is because *any two quorum sets must have a non-empty intersection, hence if the primary proposes the lock-value with the highest lock-view then this value must be the the committed value* (see the proof below). In this post, we assume $n=2f+1$ and use majority quorums that consist of $n-f=f\+1$ replicas.

This Lock-Commit paradigm is the core of Paxos. It is extended to many settings:

1. Since Lock-Commit is based on *quorum intersection*, safety does not rely on any synchrony. Indeed unlike the [Commit-Notify](https://decentralizedthoughts.github.io/2020-09-13-synchronous-consensus-omission-faults/) paradigm, the Lock-Commit paradigm is often used for safety in asynchrony (and partially synchrony).

2. The Lock-Commit paradigm guarantees [uniform consensus](/2019-06-27-defining-consensus/) (so even omission-faulty replicas commit on the same value). In essence, it guarantees that a replica does not decide before the *system* is in a [committed](/2019-12-15-consensus-model-for-FLP/) state.

3. The Lock-Commit paradigm can be extended to tolerate malicious adversaries. For $n>2f$, by using [signatures and synchrony](/2019-11-10-authenticated-synchronous-bft/); and for $n>3f$, by using a quorum system where every two sets intersect by at least $f\+1$ replicas.



Here is a Lock-Commit based (uniform) consensus protocol tolerating $f<n/2$ omission faults for a single slot:

## Lock-Commit for omission failures

    // pseudocode for Replica j
    
    log = []     // a log (of size 1) of committed values
    view = 1     // view number that indicates the current Primary
    lock-view = 0     // the highest view a propose was heard
    lock-value = null // the value associated with the highest lock
    start timer(1) // start timer for view 1 (for duration 8 Delta)
    
    
    while true:
       // as primary 1: replica 1 and view is 1
       on receiving first cmd from client and j == 1 and view == 1:
             send ("propose", cmd, view) to all replicas
       
       // as a backup replica 
       on receiving ("propose", cmd, v) and v == view:
             lock-view = v
             lock-value = cmd
             send ("lock", cmd, v) to the primary j
       
       // as a primary: replica j and view is j
       on receiving ("lock", cmd, view) from n-f distinct replicas and view == j:
             // commit (after you know enough have locked)
             log[0] = cmd
             send ("commit", cmd) to all replicas
             terminate
       
       // as a replica: commit and terminate
       on receiving ("commit", cmd):
             log[0] = cmd
             send ("commit", cmd) to all replicas
             terminate

When does a replica move from one view to another? When it sees that the current primary is not making progress. This is the **view change trigger** protocol:

      on timer(i) expiring and log[0] == null and view == i; or
      on receiving ("blame", i) from f+1 distinct replicas
             send ("blame", i) to all replicas
      on receiving ("blame", i) from n-f distinct and view <= i:
             // this will trigger a timer and a "highest lock message"
             send ("view change", i+1) to all replicas (including self)

Note that the view change trigger protocol can be simplified and also altered to have a linear communication optimistic path. Assuming synchrony, we could for example, simply trigger a view change after each 8 message delays. The more elaborate option described above will allow us to generalize in later posts.

What do the next primaries propose? To maintain safety, they must read from a quorum and use the lock-value with the highest lock-view. This is the essence of the **view change** protocol:

       // send your highest lock
       on receiving ("view change", v) and view < v:
             view = v
             // start timer for 8 Delta
             start timer(v)
             send ("highest lock", lock-value, lock-view, v) to replica v
             
       // as the primary (you are replica j and view is j)
       on receiving ("highest lock", l-val, l-view, j) from n-f distinct replicas and view == j:
             if all l-val are null (all l-view are 0):
                 my-val = any value heard from the clients
             otherwise:
                 my-val = l-val with the highest l-view
             send ("propose", my-val, view) to all replicas


### Argument for Safety

The key intuition for safety is a quorum intersection argument between two quorums:
$W$: A set of replicas who sent a lock message on the committed value (and are hence locked on it).
$R$: A set of replicas who send their highest locks to a primary in any higher view.

If $\|W \cap R\| \geq 1$ replica, then the committed value is always passed on to the next leader as a lock-value whose lock-view is maximal. This argument thus holds for all subsequent views and is formalized using induction in the following claim.

**Claim:** Let $v$ be the first view where some replica commits to some value $cmd$.
Then, no primary will propose $cmd' \\neq cmd$ at any view $v'\\geq v$.

*Proof:*

By induction on $v' \\geq v$. For view $v'=v$, this follows since the primary sends just one "propose" value per view. Assume the hypothesis holds for all views $\\leq v'$ and consider the view change of primary $v'\+1$ to view $v'\+1$.

Let $W$ be the set of $n-f$ distinct replicas that set $lock-view = v$ and sent $("lock", cmd, v)$ to the primary $v$ in view $v$.

Let $R$ be the $n-f$ replicas that the primary $v'\+1$ received their $("highest$ $lock", lock$-$val, lock$-$view, v'\+1)$ for view $v'\+1$.

Since $W \\cap R \\neq \\emptyset$, then the primary of $v'\+1$ must hear from a member of $R$. 
Fix some $a \in W \\cap R$.
By the definition of $R$ and from the induction hypothesis we know that for the view change to view $v'+1$, replica $a$'s lock-view is at least view $v$ and its lock-value must remain $cmd$. In addition, from the induction hypothesis, we know that no other member of $W$ can have a lock that has a lock-view that is at least $v$ with a lock-value $cmd' \\neq cmd$.

Hence, during the view change of view $v'\+1$, the value with the maximum view in $W$ must have the value $cmd$ and be with a view $\\geq v$.

Observe that this argument did not rely on synchrony.

### Argument for Liveness

**Claim:** Let $v$ be the first view with a non-faulty primary. 
Then, all non-faulty replicas will commit by the end of view $v$.

*Proof:*

Observe that in any view $<v$, either some non-faulty commits and hence all non-faulty commit and terminate one message delay later; or otherwise, all non-faulty do not commit, and hence will send a "blame" and hence all non-faulty will send a "view change" and join the next view within one round trip.

Observe that this argument requires synchrony: it uses the fact that the timers will expire and all start the next view within one message delay.

If some non-faulty replicas have not decided before entering view $v$, then all non-faulty will enter view $v$ within one message delay. In view $v$, the non-faulty primary will gather $n-f$ distinct "lock" messages and will send a commit message that will arrive to all non-faulty replicas before their $timer(v)$ expires (assuming the timer is larger than 8 message delays and using the fact that they all started their timer with a gap of at most one message delay). Hence, even if all faulty replicas send a "blame" message, there will not be enough "blame" messages to form a "view change" message.

Again observe the use of synchrony.


### Remarks
1. We did not fully specify how the clients send commands to the replicas. For simplicity, we can assume that clients broadcast their requests to all replicas. In practice, one can add a mechanism to track the primary and resend commands only to the new primary when there is a view change.

2. In this post, we do not talk about executing the commands (as discussed in a [state machine replication protocol](/2019-10-15-consensus-for-state-machine-replication/)) or running multiple consensus instantces. 

3. The only requirement for Safety is that $\|W \cap R\| \geq 1$ (honest) replica. Thus, while we consider using quorums of size $n-f = f+1$, the sizes are flexible and do not have to be symmetric. This is the idea behind [Flexible Paxos](https://arxiv.org/pdf/1608.06696v1.pdf).

### Acknowlegment
Many thanks to [Alin Tomescu](https://alinush.github.io/) for valuable comments and insights!

Please answer/discuss/comment/ask on [Twitter](https://twitter.com/ittaia/status/1339895006610542594?s=20).
