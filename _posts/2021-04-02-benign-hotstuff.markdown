---
title: Benign Hotstuff
date: 2021-04-02 05:54:00 -04:00
tags:
- blockchain
- SMR
- crash
author: Ittai Abraham, Heidi Howard, and Kartik Nayak
---

In this post we describe a variant of [Paxos](https://lamport.azurewebsites.net/pubs/lamport-paxos.pdf) (or [Raft](https://raft.github.io/raft.pdf) or [Lock-Commit](https://decentralizedthoughts.github.io/2020-11-30-the-lock-commit-paradigm-multi-shot-and-mixed-faults/)) that is [inspired by looking through the lens](https://dahliamalkhi.github.io/posts/2018/03/bft-lens-casper/) of [HotStuff](https://research.vmware.com/files/attachments/0/0/0/0/0/7/7/podc.pdf) and Blockchain protocols. The most noticeable difference is that while Paxos and Raft aim to maintain a stable Primary/Leader (and change views infrequently), in Benign Hotstuff (as in HotStuff), the Primary is rotated every round! A more subtle difference is that in Paxos and Raft each block of commands is associated with both a view and a *position* in the log, in Benign Hotstuff (as in HotStuff), each block of commands is associated with a view and a *pointer to a previous block*.



The setting is that of clients that can issue commands and $n$ *replicas* that implement a replicated log of committed commands  (or more generally a replicated state machine). An adversary can cause $f<n/2$ [crash failures](https://decentralizedthoughts.github.io/2019-06-07-modeling-the-adversary/) in the [partial synchrony](https://decentralizedthoughts.github.io/2019-06-01-2019-5-31-models/) model (this is the [optimal](https://decentralizedthoughts.github.io/2019-11-02-primary-backup-for-2-servers-and-omission-failures-is-impossible/) threshold). Communication is reliable, but initially network delays may be unbounded. There is an unknown time, called Global Stabilization Time (GST), after which all message delays are bounded by a known value $\Delta$.

The goal is for the replicas to maintain a log of committed commands such that:

* **Always safe**: no two parties disagree on a prefix of their commit log 
* **Live after GST**: client commands are added to the commit log in a timely manner


## Benign Hotstuff protocol

We enumerate the replicas as $0,\dots,n{-}1$. The protocol follows the **Primary-Backup** paradigm and is **view based**: in view $v$ the **Primary** is simply replica $v\pmod{n}$. 

Each replica stores its current view; initially, all replicas are in view 0. Each replica increases its view over time in response to messages received and timeouts. In the steady state, replicas in view $i$ send a ```vote``` message to the view $v$ Primary, and the view $v$ Primary sends back a ```propose``` message that triggers the replicas to increment their view to $v{+}1$ (and hence send a ```vote``` message to the view $v{+}1$ Primary and so on).






### Data structures:
1. **block**: is a triple consisting of a sequence of commands, a view number, and a pointer to a block with a lower view. The *genesis block* is empty and has the lowest view. We say that block $A$ *extends* block $B$ if there is a path of pointers from block $A$ to block $B$.

2. **highestBlock**: the block with the highest view number that the replica saw a ```propose``` message for. Updated each time a ```propose``` message is received. Initially set to the genesis block. 

3. **blockChain**: a rooted tree of blocks. Each block points to a block of a lower view number. The root of the tree is the empty *genesis block*, and the block with the highest view is called *highestBlock*.

4. **commitMark**: a pointer to the block in the *blockChain* with the highest view that is marked as *committed*. All blocks on the path from the genesis block to this block are considered committed. Initially set to the genesis block and updated when a ```propose``` message is received. 


### Three message types:
1. ```<vote, v, B>```: contains a view number and a block. Used to vote for proposals. As expected, $n{-}f$ votes on the same block in the same view cause it to be committed.
2. ```<propose, B, mark>```: contains a block and a commitMark (the view number is embedded inside the block). Used by the Primary to propose additions to the log, notify of committed blocks, and causes the view to increment.
3. ```<goto, v>```: contains a view number. Used by the Primary, when it perceives a delay, to notify replicas to *fast-forward* their view. In the failure free steady state, this message is not used.


### The protocol:

Initially, each replica executes "Change to view 0 and vote". 

1. The Primary of view $v$:
    1. **Gather votes**: Gathers ```vote``` messages for view $v$ and updates $highestBlock$ to be the block in those vote messages with the highest view (note the view in the block is lower than $v$). As part of *State Transfer*: If the block in the vote message points to earlier blocks that the Primary does not have it asks for them.
    2. **Send goto**: If $n-f$ ```vote``` messages for view $v$ do not arrive by $\Delta$ time, the Primary can send ```<goto, v>``` to all replicas.
    4. **Propose and try to commit**: Once $n-f$ ```vote``` messages for view $v$ arrive:
        1. The Primary creates a new proposal block $B=(cmd, v, highestBlock)$ to extend the blockChain, where $cmd$ is the commands from the clients.
        2. **Commit rule**: If $n-f$ ```vote``` messages for view $v$  have the same $highestBlock$ and $highestBlock$ is from view $v-1$ then the Primary increments its $commitMark$ to be $highestBlock$.
        3. The Primary sends ```<propose, B, commitMark>``` to all replicas. The Primary then changes to view $v{+}1$.

4. Change to view $v$ and vote:
    1. **Start Timer**: Set $T_{v}$ for $5\Delta$.
    2. **Vote**: Send ```<vote, v, highestBlock>``` to the primary of view $v$, where $highestBlock$ is the block with the highest view that the replica has seen in a ```propose``` message. 

2. Triggers to change to view $v+1$:
    1. **Due to a propose**: If a replica in any view $\le v$ receives a ```propose``` message for view $v$ it updates $highestBlock$ and $commitMark$ as needed and changes to view $v+1$. As part of *State Transfer*: If the ```propose``` message points to earlier blocks that the replica does not have it asks for them.
    2. **Due to a goto**:If a replica in any view $\le v$ receives a ```<goto, v+1>``` it changes to view $v{+}1$.
    3. **Due to a timeout**:If a replica in view $v$ fails to receive a ```propose``` message for view $v$ when the timer $T_v$ expires, it changes to view $v{+}1$. 
    4. **Due to a vote**: If the replica that would be the primary of view $v+1$ is in any view $\le v$ and it receives a ```vote``` message for view $v{+}1$ it changes to view $v{+}1$.

## Examples

Observe that orphan blocks (and even orphan sub-trees) may occur and represent proposals that were eventually abandoned. In the first example below, Primary 0 sends a ```propose``` message, and all replicas ```vote``` for it. The Primary of view 1 sees $n{-}f$ votes for block 0, so it updates $commitBlock$ to point to block 0 and forwards this along with the proposal of block 1. The Primary of view 2 locally commits to block 1 and creates a proposal at view 2 that extends block 1 but all its messages are delayed. View 3 is triggered by  $T_2$, the view 2 timer expiring at all replicas. The Primary of view 3 gathers $n{-}f=2$ votes that do not include replica 2. Note that since block 1 had $n{-}f$ votes, then Primary 3 will commit block 1. It creates a block with view 3 that extends the block at view 1. Replica 1 which is the Primary of view 4 gathers $n{-}f=2$ votes with this block and commits block 3. Replica 2 receives the $commitMark$ at block 3, so it's $blockChain$ includes an orphan block at view 2.


![](https://i.imgur.com/EmKTWP7.jpg)


In the second example below, Primary 0 sends a ```propose```, and all replicas ```vote``` for it. The Primary of view 1 sees $n{-}f$ votes for block 0, so it updates $commitBlock$ to point to block 0 and forwards this along with the proposal of block 1. Then replica 2 which is the Primary of. view 2 crashes. Here we assume that the timer $T_2$ of replica 0 expires much sooner and it switches to view 3. As replica 2 crashed and replica 1 is still in view 2, replica 3 does not receive $n{-}f=2$ votes, so it sends a ```goto``` message. This message causes replica 2 to move to view 3 and allows replica 0 to gather $n{-}f=2$ votes for view 3 and move the $commitMark$ to block 1.

![](https://i.imgur.com/TC5xNVI.jpg)




## Safety and Liveness analysis 


Fix a block $B$. Let $v$ be the first view in which there are $n{-}f$ replicas $Q$ that vote for the same block $A$ at view $v$ such that:
1. Either $A=B$ or $A$ extends $B$.
2. The block $A$ is form view $v-1$.

**Safety claim**: Any ```propose``` message of any view $v$ or higher must extend $B$.

**Proof**: For the base case, the ```propose``` block $A$ of view $v-1$, by definition, is either $B$ or extends $B$.

Assume the statement is true for all ```propose``` messages from view $v$ to view $u{-}1$ and consider view $u$. 

By the induction hypothesis, all ```propose``` messages from view $v$ to view $u{-}1$ extend $B$, so at the beginning of view $u$, the highest block of any replica in $Q$ must either be $B$ or extend $B$. 

The Primary of view $u$ collects votes from $n{-}f$  replicas $R$ and extends the block in $R$ with the highest view.  By quorum intersection, the sets $Q$ and $R$ must intersect ($n-2f>0$), so the Primary of view $u$ must see at least one block of view at least $v$ and at most $u{-}1$ from a replica in $Q$. Since all blocks of view at least $v$ extend $B$ then the Primary of view $u$ must also extend $B$.


**Live after GST claim**: when the system is in synchrony, then a sequence of two good primaries will make progress.

**Proof**: Consider the first time $t$ where a message for the highest view $v$ is sent at $t$ and no timer expires before $t+5\Delta$. Observe that this happens at most $5\Delta$ after GST. Also, note that by this time all the State Transfer has concluded.

Lets first assume that the replicas of view $v$ and $v+1$ do not crash:

By $t+\Delta$, the Primary of view $v$ will receive a message and will change to view $v$. By $t+2\Delta$ it will send ```<goto, v>```, so all replicas will move to view $v$ by $t+3\Delta$ and the primary will gather $n-f$ votes by time $t+4\Delta$, by time $t+5\Delta$ all replicas will get the view $v$ ```propose``` message and send their ```vote``` message to the Primary of view $v+1$.

The Primary of view $v+1$ will get $n-f$ votes on the same block from view $v$ and hence will update its $commitMark$. All replicas will receive this $commitMark$ by time $t+6\Delta$.

If some replicas crash, then consider the first two consecutive nonfaulty replicas at views $v<v'$. In the worst case, it may take $O(\Delta f)$ rounds to have two consecutive nonfaulty replicas.


## Complexity analysis 
Benign Hotsuff maintains a linear message complexity per view. In each round either all replicas send to the Primary or the Primary sends to all replicas. In the failure free case, the amortized cost of committing a block is just $2n$ messages. In the worst case, the total number of messages to commit to one block after GST is $O(fn)$ which is [asymptotically optimal](https://decentralizedthoughts.github.io/2019-08-16-byzantine-agreement-needs-quadratic-messages/). 

## Adding a relaxed one chain rule
The commit rule requires the view $v$ Primary to gather $n{-}f$ votes on a block from view $v-1$. Can we relax this and allow to commit even if the votes are on a previous block?  This is a relaxed  "one chain" safety rule that allows to "skip" replicas that crashed. 

The core observation is that at view $v$ in order to commit a block of view $v'<v$ we need to say that we did not vote for any other block (other than $v'$) in all views $v'<u<v$. Note, this statement is trivial when $v'=v-1$.

We make two changes, the first is to add a Boolean flag ```power``` in the vote message:

*  **Vote with power**: Send ```<vote, v, highestBlock, power>``` to the primary of view $v$, where $highestBlock$ is the block with the highest view $v'$ that the replica has seen in a ```propose``` message, such that:
    1. If any ```vote``` in the views between $v'+1$ and $v-1$ are for $highestBlock' \neq highestBlock$ then set ```power=weak```.
    2. Otherwise (all votes in the views between $v'+1$ and view $v-1$ where for $highestBlock$ or were skipped), then set ```power=strong```.

The second change is for the commit rule to only use strong votes:

* **Relaxed commit rule**: If $n-f$ ```vote``` messages for view $v$  have the same $highestBlock$ and ```power=strong```  then the Primary increments its $commitMark$ to be $highestBlock$.

For safety observe that in all the views $v'<u<v$ there could not be any party that commits any block that does not extend $B$. Moreover, any proposal of $v'<u<v$ will be lower than the proposals from the member of $Q$ of view at least $v$.


In the following posts, we will see how the Byzantine variants of Hotsuff can be extended to these relaxed "two chain" (and "three chain") safety rules in order to add non-equivocation (and responsiveness).



## More notes 

Note that the path from $highestBlock$ to the genesis consists of a sub-path of un-committed blocks and a sub-path from the $commitMark$ to the genesis of committed blocks. During State Transfer, replicas can safely exchange the $commitMark$ and any missing blocks on this path. 


The ```goto``` message is used to synchronize the replicas. We could have the Primary send it every round but chose to optimize it away in the synchronized failure free steady state case. 

We describe Benign Hotstuff as a system for replicating a log, but the same can be used to implement any [replicated state machine](https://decentralizedthoughts.github.io/2019-10-15-consensus-for-state-machine-replication/).


Please answer/discuss/comment/ask on [Twitter](https://twitter.com/ittaia/status/1379061379899006984?s=20).  
