---
title: State Machine Replication for Two Servers and One Omission Failure is Impossible
  even in a lock-step model
date: 2019-11-02 14:12:00 -04:00
tags:
- lowerbound
- SMR
- dist101
author: Ittai Abraham
---

In a [previous post](https://decentralizedthoughts.github.io/2019-11-01-primary-backup/), we show that State Machine Replication for any $f<n$ failures is possible in the synchronous model when the adversary can only cause parties to *crash*. In this post, we show that *omission* failures are more challenging. Implementing SMR requires at most $f<n/2$ omission failures.

**Theorem:** *It is impossible to implement State Machine Replication with two replicas for two clients and an adversary that can cause omission failures to one replica (and any number of clients) even in a lock-step model.* 

As in our previous [lower bounds](https://decentralizedthoughts.github.io/2019-06-25-on-the-impossibility-of-byzantine-agreement-for-n-equals-3f-in-partial-synchrony/), we assume a solution that is [safe and live](https://decentralizedthoughts.github.io/2019-10-15-consensus-for-state-machine-replication/) and reach a contradiction. For the contradiction, we define three worlds and use an indistinguishability argument. In each world, there are two clients called client $1$ and client $2$ and two servers called server $1$ and server $2$.

### World A:

In this world, client $1$ wants to send command $C1$, and the adversary blocks all communication to and from server $2$ (server $2$ is omission faulty). Since the protocol is safe and live, any correct solution must notify client $1$ that command $C1$ is the only committed command.

![WorldA](https://hackmd.io/_uploads/Bka1-zsdp.jpg)


### World B:

In this world, client $2$ wants to send command $C2$, and the adversary blocks all communication to and from server $1$ (server $1$ is omission faulty). Since the protocol is safe and live, any correct solution must notify client $2$ that command $C2$ is the only committed command.

![WorldB](https://hackmd.io/_uploads/Sk8lbzod6.jpg)


### World C:

In this world, client $1$ wants to send command $C1$, and client $2$ wants to send command $C2$. The adversary causes both clients to fail by omission as follows: it blocks all communication between client $1$ and server $2$ and all communication between client $2$ and server $1$. Finally, without loss of generality, the adversary also causes server 2 to have omission failures by blocking all communication between server $1$ and server $2$.

![WorldC](https://hackmd.io/_uploads/BJeb-GiOa.jpg)

Observe that the view of server 1 in world A and world C is indistinguishable. Since in worlds A and C, client $1$ only communicates with server $1$, it also has indistinguishable views.

Similarly, the view of server 2 in world B and world C is indistinguishable. Since in worlds B and C, client $2$ only communicates with server $2$, it also has indistinguishable views.

So in world C, the two clients will see conflicting states and this is a violation of safety.


Notes:

1. The proof heavily uses the fact that the clients are prone to omission failures. If clients can just crash (or are non-faulty) then the clients can implement SMR using the replicas as relays.
2. This lower bound can be generalized to $n$ replicas and $f$ omission failures for any $n\leq 2f$.
3. Since it just requires omission faults, this lower bound holds even if there is a setup and a PKI.
4. This post was updated in November 2021 to stress that the lower bound requires at least two clients. In fact, the state machine we need is a simple two-client write-once register.
5. While this post focuses on synchrony and omission faults for both one server and all clients, it can also be cast in asynchrony (or partial synchrony) with just one sever. It's a good exercise!
6. Nancy Lynch's book has a variant of this lower bound for atomic objects in asynchrony. See Theorem 17.6 in her [book](https://dl.acm.org/doi/book/10.5555/2821576). This was later [extended](https://users.ece.cmu.edu/~adrian/731-sp04/readings/GL-cap.pdf) by Gilbert and Lynch to partial synchrony and connected to Browers conjecture.

Please leave comments on [Twitter](https://twitter.com/ittaia/status/1191305159638503426?s=20)


