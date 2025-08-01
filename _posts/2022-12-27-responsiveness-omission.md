---
title: Responsiveness under omission failures
date: 2022-12-27 08:00:00 -05:00
tags:
- research
- omission
author: Ittai Abraham and Kartik Nayak
---

In this post, we discuss log replication [responsiveness](https://decentralizedthoughts.github.io/2022-12-18-what-is-responsiveness/) in the context of omission failures. We show how to transform the protocol in our [previous post](https://decentralizedthoughts.github.io/2022-11-04-paxos-via-recoverable-broadcast/) to a multi-shot version of Paxos for omission faults. The Byzantine failure case uses similar ideas and is covered in the next post of this series.


### Obtaining responsiveness in log replication with a stable leader

In the [previous post](https://decentralizedthoughts.github.io/2022-11-04-paxos-via-recoverable-broadcast/) we replaced leaders every $10 \Delta$ time (the constant 10 was chosen for simplicity). What if instead of replacing leaders, we keep the same leader and replace it only when it fails. This is called the **stable leader** approach.  The same *stable leader* consecutively commits commands using [recoverable broadcast](https://decentralizedthoughts.github.io/2022-11-04-paxos-via-recoverable-broadcast/) without any additional waiting and without calling [recover-max](https://decentralizedthoughts.github.io/2022-11-04-paxos-via-recoverable-broadcast/) in between each new decision. 

Assume the primary has a function ```getNextVal``` that returns the next uncommitted client command. Here is the protocol for the stable primary:
```
c := Recover-Max(v)

while (true)
    newCommand := getNextVal()
    c := c <- newCommand 
    send <propose(v,c)> to all
    wait for n-f echoes for <v,c>
    mark newCommand as committed 
```

Note the first iteration uses ```Recover-Max``` and appends the new command to it, all the later iterations use the previous committed log and appends the new command to it.


This protocol obtains multi-shot responsiveness. When the stable leader is non-faulty, there are no timeouts between proposals.

There is no safety concern: each consensus instance has its independent safety properties maintained. The primary must wait for $n-f$ echeos before moving forward. Moreover, just as before, echoes are only sent by parties that are in view $v$. 

But what about liveness? There is a new challenge: we cannot use a fixed timer to change views because we want the leader to continue driving decisions. A mechanism to decide when to move to a new view is needed. New problems emerge: how do we decide when to change views, and how do we make sure this move is synchronized between all parties? Here is a common state machine approach:

For a view $v$, a party can be in one of three states:
1. ```start-view-v``` this is the state in which the party listens to the view $v$ primary;
2. ```blame-v``` this is the state where the party sees something wrong in view $v$; 
3. ```stop-view-v``` this is the state where the party stops listening to the view $v$ primary.

Let's go over each transition:

* From ```start-view-v``` to ```blame-v```: this is when a party is not seeing progress in the current view (or more generally, anything wrong in this view). A reason to blame is if a heartbeat or message from the current primary does not arrive in $2 \Delta$ from the previous one. A second reason to blame is if a client request arrives but the primary does not reach a decision on it in the required time. In either case, when moving to ```blame-v```, the party sends a ```<blame, v>``` message to all parties.
* From ```blame-v``` to ```stop-v```: should a party in ```blame-v``` stop processing messages in view $v$?  Not so fast. Maybe the blaming party is omission faulty and the primary is actually non-faulty. To overcome this ambiguity, a party waits for $f+1$ distinct ```<blame, v>``` messages before moving to ```stop-view-v```. When moving to ```stop-view-v``` the party sends a ```<stop-view, v>``` message to all parties. At this point, the party stops responding to view $v$ messages (in particular it does not echo messages for view $v$).
* From ```stop-v``` to ```start-v+1```: should the party move to view $v+1$ when it reaches ```stop-v```? Not so fast, maybe the party is the only non-faulty party that reached ```stop-v```. To synchronize, we make ```stop-v``` contagious! If a party hears a ```<stop-view v>``` message and it did not send it yet then it sends ```<stop-view, v>``` to all parties.
* Parties ```start-view-v+1``` (start recover-max for view $v+1$) when they hear $f+1$ ```stop-view-v``` messages.


**Lemma**: After GST, if a party starts view $v+1$ at time $t$, then all non-faulty parties will start view $v+1$ at time at most $t+2\Delta$.

*Proof*: A party starts view $v+1$ at time $T$ if it hears $f+1$ ```<stop-view, v>``` messages. At least one of them is from a non-faulty party. So all non-faulty parties will receive at least one ```<stop-view, v>``` by time $T+\Delta$, and hence all non-faulty parties will send ```<stop-view, v>```  by time $T+\Delta$. So all non-faulty parties will receive at least $f+1$ ```<stop-view v>``` by time $T+2\Delta$.



With this three-state technique, parties make sure that a non-faulty primary after GST will not be removed (incorrectly blamed), while in any case of a view change, all parties will be moving in sync (up to $2\Delta$). The first property is critical for achieving responsiveness with a stable leader and the second property is critical for liveness.

For multi-shot responsiveness, do we have to use a stable leader? Can we do the same for a sequence of non-faulty rotating leaders?

### Obtaining responsiveness in log replication with rotating leaders

With a stable leader, we could keep the same view and same leader for multiple consecutive commands. For rotating leaders, we need to change views each time we change primaries. The idea is to use the $n-f$ ```<echo>``` messages for view $v$ as both a commit message for view $v$ and also an implicit ```<echoed-max>``` message for view $v+1$. So once the primary for view $v+1$ sees $n-f$ echo messages for view $v$ it can immediately propose the next value for view $v+1$.

Here is the protocol for the optimistic path:
```
If you see n-f echos for <v,c> 
   and you are the leader of view v+1
    then
        newCommand := getNextVal
        c := c <- newCommand 
        send <propose(v+1,c)> to all
```


For safety, why is recoverability okay even though we did not explicitly send ```<echoed-max>``` between views? Recover max for view $v+1$ only needs the echo from the highest view, and we have an echo in view $v$ which is the highest possible (at the beginning of view $v+1$). So safety is maintained. Moreover, we obtain the required multi-shot responsiveness. What about liveness?

We again use the three states: (1) ```start-view-v```; (2) ```blame-v```; (3) ```stop-view-v```. We will use two paths to progress to ```start-view-v+1```:

1. Optimistic path: the primary of view $v+1$ hears $n-f$ echos from view $v$ and uses this as an implicit ```start-view-v+1``` and recover max for view $v+1$. Any party that hears a proposal for view $v+1$ uses this to trigger ```start-view-v+1```.
2. Pessimistic path: Use a $10 \Delta$ timer for moving into ```blame-v```; or cancel the timer if you hear $n-f$ echos for view $v$.



For liveness, the pessimistic path is similar to the stable leader case. For the optimistic case, the decision is driven by a primary that synchronizes all parties. Note that a primary can only make progress if the previous primary's echo reached $n-f$ parties.


Your thoughts on [Twitter](https://twitter.com/kartik1507/status/1607756048575909890?s=61&t=m3prllqHF_JFxgGe6bfMnw).

