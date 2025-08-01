---
title: 'Information Theoretic HotStuff (IT-HS): Part One'
date: 2021-09-20 08:07:00 -04:00
tags:
- research
author: Gilad Stern, Ittai Abraham
---

This post is the first of two on [Information Theoretic HotStuff (IT-HS)](https://arxiv.org/abs/2009.12828). Information Theoretic HotStuff is a [Byzantine Consensus](https://decentralizedthoughts.github.io/2019-06-27-defining-consensus/) protocol in the [partially synchronous](https://decentralizedthoughts.github.io/2019-06-01-2019-5-31-models/) model. It replaces all of [HotStuff's](https://arxiv.org/abs/1803.05069) cryptographic signatures with simple information theoretic message passing techniques over [authenticated channels](https://decentralizedthoughts.github.io/2019-07-19-setup-assumptions/). Information theoretic protocols are often easy to reason about, form a great introduction for learning the basics of consensus, have less of an attack surface, and highlight useful core distributed computing techniques.

<details>
  <summary>Click this line for a short refresher on Byzantine consensus and Partial Synchrony.</summary>

In a system with Byzantine faults, we assume there are $n$ parties, and $f$ of them might be corrupt. All honest (i.e. non-corrupt) parties run a protocol, and the corrupt parties can try to actively sabotage the process by deviating from the protocol. A Byzantine consensus protocol has three properties:

(1) **Termination**: If all honest parties participate in the protocol, they eventually complete it.
(2) **Correctness**: Every honest party that completes the protocol outputs the same value.
(3) **Validity**: If all parties are honest, and they have the same value $x$, then they output $x$.

Finally, a partially synchronous system is one that starts off as a completely unreliable network and eventually stabilizes. More precisely, in the beginning of the protocol messages sent by honest parties eventually reach their destination, but could take any finite amount of time. At some point in time called the Global Stabilization Time ($GST$), the network becomes stable. After $GST$, all messages are delivered in at most $\Delta$ time, for some known $\Delta$. This also means that any message sent before $GST$ is delivered by time $GST+\Delta$.
</details>


## High level overview

We start with an overview of the *messages* and their intuitive role in the protocol. Like Paxos, PBFT, and HotStuff, the IT-HS protocol is *view-based*. This means that there are many sequential attempts to reach *consensus*, each with its own *leader*. Except for the commit message, each message has an associated *view number*. This helps parties know in which view the message was sent.


1. ```<'commit',b>``` messages: when you hear $f+1$ ```commit``` messages you can also commit to the value $b$ and send a ```commit``` message. When you hear $n-f$ ```commit``` messages you can terminate. This guarantees that if you terminate then all honest parties will eventually commit and terminate.
2. ```<'lock',b,v>``` messages: when you hear $n-f$ ```lock``` messages in view $v$ you can commit to value $b$, this guarantees that at least $f+1$ honest are locked on $(b,v)$ if you commit. By locked on $(b,v)$, we mean that you will not be willing to accept any other proposal without sufficient evidence that no commitment took place in view $v$. This idea is elaborated upon later when talking about the safety of our protocol. This is the basis of the [lock-commit paradigm](https://decentralizedthoughts.github.io/2020-11-29-the-lock-commit-paradigm/).
3. ```<'accept',b,v>``` messages: when you hear $n-f$ ```accept``` messages for value $b$ in view $v$, you *lock* on $(b,v)$. If you hear $f+1$ ```accept``` messages you send an ```accept``` message. This guarantees that if you have a lock on $(b,v)$ then eventually all honest will see this lock. This key property is used to *transfer* a proof that the content of the lock in the ```propose``` message is not made up.
4. ```<'echo',b,v>``` message: when you hear $n-f$ ```echo``` messages for value $b$ and view $v$ you send an ```accept``` message with $b,v$. This guarantees that the honest parties never send ```accept``` on conflicting values in the same view.  
5. ```<'propose',l,v>``` messages where ```l=(b,w)```: this is the message sent by the leader to propose a value $b$. To guarantee liveness, the leader proposes the value of the *lock* with the highest *view* it saw. Importantly, you send an ```echo``` on a proposal only if the leader sends a *valid* lock (i.e. for which you heard n-f ```accept``` messages) whose view $w$ is at least as high as the lock with the highest view that you have seen.  
6. ```<'suggest',l,v>``` messages where ```l=(b,w)```: this is the message sent by parties to the new leader when there is a view change. It contains the lock with the highest view that you have seen.   

## The IT-HS protocol

Now that we have an overview of the messages in the protocol, let's describe it more precisely. The protocol proceeds in views, the leader of view $v$ is party $v.leader$. Each party has a local field $lock$ which we describe as a tuple $lock=(lock.view,lock.val)$. Initially, parties set $lock.view=0$ and $lock.val$ to be their input. The following describes the protocol for party $i$ in view $v$:


*To simplify the protocol exposition, we omit the checks that send a message just once (this can be easily checked each time a message is sent). Similarly, for a given view and a given message type, we omit the check that a party accepts just the first messages of that view and type (this can be easily checked each time a message is received).*


### The view change protocol
In this sub-protocol each party *suggests* its lock to the leader. The leader waits enough time to hear the suggested locks from all honest parties and *proposes* the highest lock it heard. 
```
// party i view change to view v

//suggest round
send <'suggest',lock,v> to party v.leader

// propose round

only party i == v.leader: 
wait 2 Delta
upon receiving a message <'suggest',l,v> with l=(b,w), and
     receiving <'accept',b,w> from n-f parties:
        accept the suggested lock (b,w)
upon 2 Delta time passing, and accepting n-f suggestions:
     let l'=(b',w') be the accepted lock with the highest view w'
     send <'propose',l',v> to all parties
```

### The main protocol

```
// party at view v

// echo round
upon receiving <'propose',l=(b,w),v> from the leader of view v, and
    receiving <'echo',b,w> from n-f parties, and
    w>=lock.view:
        send <'echo',b,view> to all parties
                
//accept round
upon receiving <'echo',b,v> from n-f parties:
    send <'accept',b,v> to all parties 
        
//lock round
upon receiving <'accept',b,v> from n-f parties:
    set lock.view=v, lock.val=b
    send <'lock',b,v> to all parties

//commit round
upon receiving <'lock',b,v> from n-f parties:
    send <'commit',b> to all parties 
```

### Background protocol for boosting and terminating

```

// always run in the background, regardless of your view

upon receiving <'accept',b,w> from f+1 parties:
    send <'accept',b,w> to all parties 

upon receiving <'commit',b> from f+1 parties:
    send <'commit',b> to all parties 

upon receiving <'commit',b> from n-f parties:
    output b and terminate
    
```

In this post, we assume that all clocks are perfectly synchronized. After $GST$, all messages are delivered in at most $\Delta$ time, for some known $\Delta$. Any message sent before $GST$ is delivered by time $GST+\Delta$. This means each replica simply triggers a change to view $i$ at time $i (10 \Delta)$. We use the constant 10 here because it is large enough to allow an honest leader to cause all to commit. Note that at view $i$, parties don't send messages or take other actions associated with view $<i$ (such as updating locks). The only exceptions are the ones explicitly stated in the background protocol for boosting and terminating. In the next post we will explore the notions of *view-change trigger*, *view synchronization*, and  *responsiveness* that allow parties to start a view change early if they ever see that the current leader is acting dishonestly or delaying messages unnecessarily. In this post we present a simpler version of the protocol that assumes synchronized clocks and has all parties trigger view changes based on their clocks.

We've described the protocol, now let's understand why it works.

## The Boosting Protocol
Let's first look at the boosting and the termination sub-protocols. These sub-protocols are both similar to [Reliable Broadcast](https://decentralizedthoughts.github.io/2020-09-19-living-with-asynchrony-brachas-reliable-broadcast/) and both obtain similar properties. The first property is that if an honest party sees $n-f$ ```accept``` (or ```commit```) messages, every honest party eventually will see this. The second is that no two honest parties ever send ```accept``` messages with differing values in a given view. Similarly, no two honest parties ever send ```commit``` messages with differing values. 

We prove that these properties hold below.

***Claim 1***: *If some honest party receives $n-f$ ```accept``` messages with some view and value, then eventually all honest parties receive $n-f$ ```accept``` messages with that view and value.*

If some honest party receives $n-f$ ```accept``` messages with some value $b$, then at least $(n-f)-f\geq 3f+1-2f=f+1$ of those messages were sent by honest parties. Since they're honest, they send the same message to all parties. Therefore, every honest party will eventually receive at least $f+1$ ```accept``` messages with the value $b$ in that view and send an ```accept``` message with that value as well. There are at least $n-f$ honest parties, so this proves our claim. 

Note that for this property to hold, parties have to continue sending such messages at any time, and not only during the current view. Using similar arguments, if an honest party receives $n-f$ ```commit``` messages with a certain value, eventually every honest party does.

***Claim 2***: *No two honest parties send ```accept``` messages with differing values in the same view.*

Assume this is not the case. Therefore, two honest parties send two ```accept``` messages with the values $b$ and $b'$. Consider the first two such parties. Since they are the first honest parties to have sent ```accept``` messages with those values, they received no more than $f$ ```accept``` messages with those values before. Therefore, they sent their respective ```accept``` messages after receiving $n-f$ ```echo``` messages. From Byzantine Quorum intersection, they received at least one of those messages from an honest party. Honest parties only send a single message with a single value to all parties, so $b=b'$, reaching a contradiction.


## Safety

When thinking of running many consecutive views, we want to make sure that we only send ```accept``` messages containing *safe* values. What does *safe* mean in this context? Only values that don't contradict the committed output of other honest parties are considered *safe*. This suggests the following: 
**Safety property**: *Once the first honest party sends a commit message with some value in a given view, no honest party sends an accept message in that view or in any later view with a different value*. 
It is essential that this property always holds, even when the network is still unstable (before $GST$).

There are two main mechanisms that help ensure safety in our protocol. The use of the echo mechanism, and the use of the lock mechanism. In proving safety we will actually prove two smaller claims first. In the first claim we will show that the way parties send ```echo``` messages guarantees that honest parties cannot commit to different values in the same view. In the second claim we will deal with safety across views. More specifically we show that the locking mechanism guarantees that once a commitment takes place, no other value can be accepted.

***Claim 3***: *No two honest parties send ```commit``` messages with different values in the commit round of view $v$.*

We've shown that all honest parties that send ```accept``` messages in view $v$ do so with the same value $b$. Honest parties only send ```lock``` messages with a value $b'$ after receiving at least $n-f$ ```accept``` messages with the value $b'$. Since $n-f>f$, at least one of those messages has to have been received from an honest party, and thus $b'=b$. Using similar reasoning, every honest party that sends a ```commit``` message in the commit round of view $v$ does so with the value $b$.



***Claim 4***: *If some honest party sends a ```commit``` message in the commit round of view $v$ with the value $b$, then no honest party sends an ```accept``` message with a different value $b'$ of any later view $v'>v$.* 

Why should that be true? Before sending a ```commit``` message with the value $b$ in view $v$, an honest party waits to receive $n-f$ ```lock``` messages with that same value. At least $(n-f)-f\geq 3f+1-2f=f+1$ of those messages were sent by honest parties. We will call the set of those parties $I$. Since the parties in $I$ sent a ```lock``` message, they also set their current lock to $(b,v)$. These $f+1$ honest parties will act as *sentinels*. They will refuse to send an ```echo``` message about any other value in any subsequent view. In order to proceed into the accept round (or later rounds), parties must receive at least $n-f$ ```echo``` messages. There are a total of $n$ parties, so at least one of those messages must have been sent by a party in $I$. These parties refuse to do so, preventing any other value $b'$ from reaching the accept round (and hence also the lock round and commit round). 

For a more formal proof, assume by way of contradiction that some party $i\in I$ sends an echo message with a different value $b'\neq b$ in some view $v'$ such that $v'>v$. Observe the first $v'$ in which this happens. Party $i$ sent the echo message after receiving a proposal from the leader with $l=(b',w)$ such that $i$ sees that $w>=lock.view$.In addition, $i$ receives at least $n-f$ accept messages from view $w$ with the value $b'$. We know that $i$ updated its lock to $(b,v)$ in view $v$, and throughout the protocol parties only increase their $lock.view$. This means that in view $v'$, $w>=lock.view>=v$.  First we would like to show that it is impossible that $w=v$. By assumption, $i$ set its $lock$ variable to the tuple $(b,v)$ in view $v$. Before doing so, $i$ must have received $n-f$ accept messages with the value $b$ in view $v$. From Claim 2, we know that no honest party receives $n-f$ accept messages with any other value in view $v$, contradicting the fact that $i$ is assumed to have received such messages. 

Now assume that $w>v$ and observe the first honest party $j$ that sent an ```accept``` message in view $v'$. By assumption, no party in $I$ sent an ```echo``` message with the value $b'$ in view $w$ because $v'>w>v$, and $v'$ is the first view in which this happens. Using this observation, we know that $j$ could have received at most $n-(f+1)$ ```echo``` message with the value $b'$ in view $w$. Therefore, $j$ didn't send the message as a result of receiving $n-f$ ```echo``` messages with the value $b'$ in view $w$. The only other option is that $j$ sent the message after receiving an ```accept``` message with the value $b'$ in view $w$ from $f+1$ parties. At least one of those parties is honest, which contradicts the fact that $j$ is the *first* honest party to send such a message. We ran out of options, so we must conclude that the parties in $I$ never sent an ```echo``` message with any other value in any $v'$ later than $v$. 

Using similar arguments we can show that no honest party sends an ```accept``` message with any other value in any later view. Assume some honest party sends an ```accept``` message with a different value $b'\neq b$ in some $v'>v$. Observe the first such party, and guarantee that it couldn't have done so.

Finally, no honest party sends a ```lock``` message with a different value $b'\neq b$ in any $v'>v$. That is because, in order to do so, they must have first received $n-f$ ```accept``` messages with that value $b'$, and they could have received no more than $f$ such messages from the corrupt parties. For the same reasons, no honest party sends a ```commit``` message with a value $b'\neq b$ in the commit round of any view $v'>v$.

In order to achieve safety, we showed that once the first honest party sends a ```commit``` message with the value $b$ in the commit round of view $v$, no honest party sends an ```accept``` message with any other value $b'$ in any view $v'\geq v$. This implies that no two honest parties send ```commit``` messages with different values in the commit round of any view $v'\geq v$. Following the exact same logic of Claim 2, we can conclude that after the first honest party sends a ```commit``` message about a value $b$, no honest party ever sends a ```commit``` message about any other value $b'\neq b$ in any stage of the protocol. In other words, only one value $b$ might have more than $f$ ```commit``` messages sent about it, and therefore that is the only value honest parties might output. 

## Liveness
Safety without *Liveness* is trivial, just do nothing:-). For Liveness, we want to eventually make progress! A corrupt leader can just remain silent and prevent any progress from being made in its view. Even more worrying, an honest leader might send messages, but before $GST$ they can be delayed so long that timeouts take place. This suggests that we cannot guarantee progress before $GST$. The **Liveness property**  we can get is: *all honest parties terminate in the first view with an honest leader that starts after $GST$*.

For this post we assume clocks are perfectly synchronized and this makes liveness much easier. Our goal is to make sure that after $GST$, honest leaders send propose messages which convince all honest parties to send an ```echo``` message. If this happens, it is pretty straightforward to see that since all honest parties start the view at the same time, then all honest parties will then send ```echo```, then ```lock```, and eventually ```commit``` messages as a consequence of receiving the previous round's messages. We do this in two claims.

***Claim 5***: *Consider a view $v$ with an honest leader that starts after $GST$. The leader will accept all of the ```suggest``` messages that honest parties send in view $v$.*

Honest parties send suggest messages that contain their $lock=(b,w)$. Before setting their $lock$ variable to $(b,w)$, honest parties receive $n-f$ ```accept``` messages with the value $b$ in view $w$. From Claim 1 about ```accept``` messages, we know that honest leaders eventually also receive those ```accept``` messages and accept the honest suggestions. A strengthening of Claim 1: if an honest party receives $n-f$ ```accept``` messages with a value $b$, then after $GST$, all parties receive $n-f$ ```accept``` messages with that value quickly (no longer than $2\Delta$ later). The protocol's timeouts and the time the leader waits are adjusted accordingly. 

***Remark***: This claim highlights an important property of the boosting protocol. We know that if some honest party receives $n-f$ ```accept``` messages from a given view, every honest party eventually will. We think of this process as providing a *transferable* proof that a value received enough support in that view.


***Claim 6***: *Consider a view $v$ with an honest leader that started after $GST$. All honest parties send ```echo``` messages in view $v$.*

Before sending a proposal, an honest leader waits $2\Delta$ time to guarantee that it hears ```<'suggest',(b,w),view>``` messages from *all* honest parties. From Claim 5 we know that the leader accepted the ```suggest``` messages sent by all honest parties. Since the leader chose the ```suggest``` message with the highest view, we know that $w$ is greater than or equal to all honest parties' $lock.view$. As highlighted in the previous remark, the ```accept``` messages are transferable proofs. We know that the leader received $n-f$ ```accept``` messages with the value $b$ in view $w$, so all honest parties will receive $n-f$ such messages too. Combining these observations, every other honest party will also send an ```echo``` message with the value $b$.

After receiving $n-f$ ```echo``` messages from honest parties with the value $v$, all honest parties will send ```accept``` messages with that value. After receiving $n-f$ messages from the previous round, all honest parties send ```lock``` and then ```commit``` messages, and finally terminate.

***Remark***: There is a valid concern with parties possibly terminating mid-view. This would render some of the arguments above untrue because parties might not respond when they should. This is solved by (1) assuming all honest parties start the view at the same time; (2) all honest parties stay in the view for sufficient time; (3) if an honest party terminates, we know that it received $n-f$ ```commit``` messages with the value $v$. From Claim 1, every other honest party also eventually receives $n-f$ such messages and terminates as well. In the next post we will discuss how to remove this dependency on synchronized clocks.

## Final notes
Taking a step back, let's reflect on some key aspects of IT-HS: The locking mechanism makes sure that if an honest party commits, there are $f+1$ honest parties that won't ever send ```echo``` messages about any other value in any later view. This prevents any other value from having more than $f$ ```accept``` messages sent about it in any later view. In that sense, the $n-f$ ```accept``` messages required for setting a lock are essentially a proof that no other commitment took place in an earlier view. This also means that any party that sees a lock from a view $v$ and receives the required ```accept``` messages can disregard any lock it has from older views because it is not actually required for safeguarding any committed value. Another key property of these proofs comes from the Boosting protocol: if one honest party receives such a proof and believes it, it knows that every other honest party will believe this proof as well. The downside of the approach in this post is that it requires to constantly keep track of messages from previous views, thus requiring storage that is proportional in the worse case to the number of views (that can grow arbitrarily large before $GST$). In our next post we will look into ways to require just a (small) finite amount of storage.

Let us know your thoughts on [Twitter](https://twitter.com/ittaia/status/1439932202477932550?s=20).