---
title: 'Living with Asynchrony: the Gather protocol'
date: 2021-03-26 06:54:00 -04:00
tags:
- dist101
- asynchrony
author: Gilad Stern and Ittai Abraham
---

A very useful tool in [Asynchronus](https://decentralizedthoughts.github.io/2019-06-01-2019-5-31-models/) distributed computing is [Reliable Broadcast](https://decentralizedthoughts.github.io/2020-09-19-living-with-asynchrony-brachas-reliable-broadcast/), or simply called *Broadcast*. It allows a leader to send a message, knowing that all parties will eventually receive the same message, even if a malicious adversary control $f$ parties and $f<n/3$. Broadcast is deterministic and takes just a constant number of rounds. 


A natural extension of broadcast is a *Multi-Broadcast*, where each party has an input. Ideally, you may want all parties to *agree on the same set* of outputs.
We discuss this primitive, called *Agreement on a Core Set* (ACS) in a [separate post](https://decentralizedthoughts.github.io/2023-07-22-agreeemnt-on-a-core-set/) (also see  [Canetti](http://www.cs.technion.ac.il/users/wwwb/cgi-bin/tr-get.cgi/1993/CS/CS0755.pdf) page 15). ACS requires to solve Consensus in asynchrony, [which we know must have infinite executions](https://decentralizedthoughts.github.io/2019-12-15z-asynchrony-uncommitted-lower-bound/). Running ACS typically also incurs high costs, traditionally using $n$ binary agreements.


In this post, we explore a surprising alternative, called **Gather** which runs in a constant number of rounds. To the best of our knowledge, this primitive first appeared as the main building block in Canetti and Rabin's [Asynchronous Byzantine Agreement protocol](https://dl.acm.org/doi/10.1145/167088.167105). Variations of this primitive have many uses, for example in [Asynchronous Approximate Agreement](https://www.cs.huji.ac.il/~ittaia/papers/AAD-OPODIS04.pdf), [Asynchronous Distributed Key Generation](https://arxiv.org/abs/2102.09041) and recently for [multi-valued oblivious common coin](https://eprint.iacr.org/2023/1003) and [ACS](https://eprint.iacr.org/2023/1130) in constant expected time. 



In a Gather protocol, each party has an input, and each party outputs a set of received values and the parties who sent them (i.e. of pairs $(j,x)$ where $j$ is the index of a party, and $x$ is the value it sent). The properties are:


1. **Common core**: There exists a **core** set $S^{\*}$ of size at least $n-f$ such that all nonfaulty parties include $S^{\*}$ in their output set. 

2. **Validity**: If a nonfaulty party includes $(j,x_j)$ in its output set, and $j$ is a nonfaulty party, then $x_j$ must be $j$'s input. 

3. **Agreement**: All parties that include some pair for a party $j$ agree on the value it sent. More precisely, if two nonfaulty parties include the pairs $(j,x)$ and $(j,x')$ in their outputs, then $x=x'$. 

At first glance, it may seem as if Gather is solving agreement, but that is not the case!  The crucial observation is that all parties output a set that includes the core $S^{\*}$ but they don't necessarily know what $S^{\*}$ is.


### Basic Gather in not always enough

It is very important to note that the gather protocol in this post is no enough for applications that need unpredictable randomness. For that one needs a binding core property. See [this post](https://decentralizedthoughts.github.io/2024-01-09-gather-with-binding-and-verifiability/) for gather with additional properties. See [this paper of Shoup](https://eprint.iacr.org/2024/1235.pdf) on cases were a basic gather can cause liveness violations.


## The basic Gather protocol

We will define $x_i$ to be party $i$'s input. Since this protocol uses broadcast, we will assume that $f<\frac{n}{3}$. The protocol proceeds in $4$ conceptual rounds that look very similar to each other:

1. Broadcast $x_i$ (using Bracha's Reliable Broadcast protocol).
2. Define the set $S_i$ of pairs $(j,x_j)$, where $x_j$ was received from $j$. Once $S_i$ contains $n-f$ pairs send $S_i$ to every party.
3. When receiving a message $S_j$ from party $j$, accept the message after receiving the broadcast $x_k$ from $k$ for every $(k,x_k)\in S_j$. After accepting $n-f$ sets $S_j$, send $T_i=\cup S_j$ to all parties.
4. When receiving a message $T_j$ from party $j$, accept the message after receiving the broadcast $x_k$ from $k$ for every $(k,x_k)\in T_j$. After accepting $n-f$ sets $T_j$, output $U_i=\cup T_j$.

See the similarity in rounds 3 and 4? it may seem like adding another identical round doesn't do much, but we will see that is not the case at all.
Let's try to understand the protocol gradually and see what each round adds to the process.

## Round breakdown

### Rounds 1-2
We start off by Broadcasting values (via Reliable Broadcast), then collect $n-f$ broadcasted values and send them as a set. So *if an honest party accepts some set then eventually all honest parties will accept that set*. Hence the Agreement and Validity properties of Gather follow from the Agreement and Validity properties of [Reliable Broadcast](https://decentralizedthoughts.github.io/2020-09-19-living-with-asynchrony-brachas-reliable-broadcast/).

### Round 3
The first non-trivial property we achieve happens after nonfaulty parties accept $n-f$ $S$ sets:

* **Weak core**: Let $G$ be the $n-f$ first nonfaulty parties that complete round 3. There exists a round 2 set $S^{\*}$ sent by a nonfaulty party such that $f+1$ nonfaulty parties include $S^{\*}$ in their $T$ sets.
More formally: there exists a set $W \subset G$ of size $\|W\|=f+1$, such that for any $i\in W$, $S^{\*}\subseteq T_i$. 


Lets count how many sets are received by $G$ that are sent from nonfaulty parties in round 2. Since each party in $G$ gathers $n-f$ sets in round 3, then at least $n-2f$ of those set were sent from nonfaulty parties. By assumption $f<\frac{n}{3}$, so $n-2f\geq f+1$. Hence, each nonfaulty party in $G$ receives round 2 sets from at least $f+1$ nonfaulty parties. In total, parties in $G$ receive *at least* $(f+1)(n-f)$ round 2 sets.

Assume the property above is false, so every round 2 set from a nonfaulty party is received by at most $f$ nonfaulty parties in $G$. This means that the total number of rounds 2 sets from nonfaulty parties that are received by nonfaulty parties is *at most* *$f(n-f)$*. This is a contradiction (clearly $f(n-f)<(f+1)(n-f)$).



### Round 4

We use the weak core property to achieve a common core in one more round. 

* **Common core**: There exists a round 2 set $S^{\*}$ sent by a nonfaulty party that all nonfaulty parties include in their $U$ sets. 

By the weak core property, there is a set $S^{\*}$  such that at least $\|W\|=f+1$ nonfaulty parties include $S^{\*}$ in their round 3 sets. Every nonfaulty party computes their round 4 sets as a union of $n-f$ round 3 sets. By quorum intersection of $n-f$ and $f+1$, at least one such set must have come from $W$, hence $U$ must include $S^{\*}$. Note that $S^{\*}$ is of size $n-f$ or greater because nonfaulty parties wait for their round 2 sets to be of that size before sending them. This means that our common core also fulfills our size requirement.


## Gather protocol complexity

Each party sends a single broadcast (which requires $O(n^2)$ words), requiring $O(n^3)$ words to be sent overall. In addition, we have a constant number of all-to-all communication rounds in which parties send sets of $O(n)$ elements to each other. This also totals in $O(n^3)$ words sent overall. This brings our sum-total to $O(n^3)$ words sent overall.



## Acknowledgments

We would like to thank Victor Shoup for insightful comments.

Please answer/discuss/comment/ask on [Twitter](https://twitter.com/ittaia/status/1375454545103499264?s=20).  

