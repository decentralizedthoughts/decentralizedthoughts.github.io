---
title: What about Validity?
date: 2022-12-12 04:00:00 -05:00
tags:
- dist101
- lowerbound
author: Ittai Abraham and Christian Cachin
---

Perhaps the archetypical [trilemma](https://twitter.com/el33th4xor/status/1191820205456023552?s=20&t=RcutJw0wQUsTmrO0OXzpXw) is **consensus** - it requires three properties: **agreement**, **liveness**, and **validity**. Getting any two is easy, but all three together is what makes consensus such a facinating problem that continues to create new challenges even after 40 years of research.

A lot of research focuses on *agreement* and *liveness* properties. In this series of posts, we highlight some classic and some more recent research on **validity** in the context of consensus and blockchain protocols. 

## Classic validity vs External validity

The classic Byzantine agreement **validity** property: 

**Validity**: *if all honest parties have the same value then this is the output value.*

Sometimes an even weaker property is required:

**Weak Validity**: *if all parties are honest and have the same value then this is the output value.*

In many contexts, these validity properties are too weak. In a state machine replication (blockchain) setting, it will almost always be the case that not all (honest) replicas see exactly the same set of client requests in exactly the same order.

This led [Cachin, Kursawe, Petzold, and Shoup, 2001](https://www.iacr.org/archive/crypto2001/21390524.pdf) to the notion of **external validity**, which intuitively limits the adversary from inventing non-existing values. 


In consensus with external validity, there is some validity check "callback function" (in the application, outside of the consensus protocol) that is guaranteed to be eventually true if it is true for any non-faulty party. The canonical example is to check the command is correctly signed by the client (or the owner of the digital asset).


External validity is the standard for all authenticated blockchain protocols, and we will describe it in a later post (also see our post on [provable broadcast](https://decentralizedthoughts.github.io/2022-09-10-provable-broadcast/)). In this post, we explore other directions for strengthening validity and why (in some sense) they lead to dead ends (or back to reductions to consensus with external validity).

## Strengthening validity without external mechanisms

It is natural to try to obtain stronger validity properties when thinking of consensus as a **voting protocol** or when requiring stronger notions of **fairness** from consensus. One motivation is blockchain systems that aim to provide voting and fairness capabilities. 


## Consensus with honest input validity 

[Neiger](https://smartech.gatech.edu/bitstream/handle/1853/6776/GIT-CC-93-45.pdf) in 1994 studied a variant of consensus that we call **consensus with honest input validity** which requires standard termination and agreement properties and a stronger validity property:
 
**Honest Input Validity**: *The output must be an input of some honest party.*

Note that Neiger called this problem *Strong Consensus* but we choose to use a more explicit name here to avoid overloading the term *strong*.

### A lower bound for honest input validity in synchrony

**Theorem [Neiger, 1994]**: Consensus with honest input validity and $m$ possible input values cannot be solved in *synchrony* for $n \leq \max(3, m) f$ and a malicious adversary controlling $f$ parties.

*Proof idea*: $n \leq 3f$ is the [standard FLM impossibility](https://decentralizedthoughts.github.io/2019-08-02-byzantine-agreement-is-impossible-for-$n-slash-leq-3-f$-is-the-adversary-can-easily-simulate/). 


Neiger's original proof was for deterministic protocols, here we present a modern version that covers even randomized protocols.

Seeking a contradiction, assume $n=mf$ and $n > 3f$. So there must be $m>3$ possible input values. Assume with loss of generality that the possible input values are $1,\dots,m$. Partition the parties into sets of size $f$: $S_1,\dots,S_m$ and have parties in set $S_i$ start with input $i$. 



Consider two worlds. In world A, there are no malicious parties. If the protocol is deterministic then assume without loss of generality it outputs value 1. Even if the protocol is randomized, there must be some value, that with probability at least $1/m$ is the output in world A. Without loss of generality assume this is value 1.


Consider world B, where the adversary corrupts parties in $S_1$ and acts as if they have input $1$. The honest parties in the protocol have no way to distinguish between world A and world B. So just as in world A, in world B the output will be $1$ (which is not an input of honest parties) with a probability of at least $1/m$.

However, in world B the non-faulty parties have input values $2,\dots,m$, hence honest input validity is violated with probability at least $1/m$.

### A tight upper bound for honest input validity in synchrony

Consensus with honest input validity in synchrony (for $m=3$ possible values assuming $n>3f$ and for $m>3$ possible values assuming $n>mf$).

We solve consensus with honest input validity via a reduction from gradecast and consensus with external validity:

1. In round 1, each party sends its input $v_i$ to all parties via [gradecast](https://decentralizedthoughts.github.io/2022-06-09-phase-king-via-gradecast/).
2. In round two, let $S_i$ be the set of grade 2 values. Let $v$ be the [mode](https://en.wikipedia.org/wiki/Mode_(statistics)) (most frequent value), and break ties arbitrarily. Use $<v,S_i>$ as your proposal to a consensus protocol with external validity. 
3. A proposal $<v,S_i>$ is valid if:
    1.  no party outside $S_i$ has grade 2; and
    2.  $\|S_i\|\geq n-f$; and
    3.  all parties in $S_i$ have grade at least 1; and
    4.  the mode of $S_i$ is $v$.

*Proof idea*: When $n>mf$, then at least one value held by non-faulty parties will appear at least $f+1$ times with grade 2, while any value held only by faulty parties will appear at most $f$ times. 

Due to the use of gradecast, even the malicious parties must use a valid input (or be ignored).

Note that we are implicitly using $<v,S_i>$ and the 4 conditions above as an external validity condition.

#### A lower bound for honest input validity in asynchrony

In 2002 [Fitzi and Garay](https://eprint.iacr.org/2002/085) extended this result to prove that solving asynchronous consensus with honest input validity in a domain with $m$ values is impossible for $n \leq max(3,m+1)f$:

**Theorem [[Fitzi and Garay, 2002](https://eprint.iacr.org/2002/085)]**: Consensus with honest input validity and $m$ possible input values cannot be solved in *asynchrony* for $n \leq (m+1) f$ and a malicious adversary controlling $f$ parties.

*Proof idea*: consider $n=(m+1)f$ and partition the parties into sets of size $f$: $S_1,\dots,S_m,S_{m+1}$. 

In world A, there are no malicious parties, parties in $S_i$ for $i\leq m$, have input $i$, and parties in $S_{m+1}$ have input $m$ and are slow. Assuming the protocol is randomized then without loss of generality assume that with probability at least $1/m$, the output in world $1$ is value $1$. 

Consider world B, where the adversary corrupts parties in $S_1$ and acts as if they have input $1$. Just as in world A, parties in $S_{m+1}$ are slow. Due to indistinguishability, in world B, the output of honest parties will be $1$ (which is not an input of any honest parties) with a probability of at least $1/m$.

#### A tight upper bound for honest input validity in asynchrony


Consensus with honest input validity in asynchrony for $m=2$ possible values assuming $n>3f$ and for $m>2$ possible values assuming $n>(m+1)f$ is possible.

Again it's a reduction: from consensus with honest input validity to reliable broadcast and consensus with external validity.


1. In round 1, each party sends its input to all parties via [reliable broadcast](https://decentralizedthoughts.github.io/2020-09-19-living-with-asynchrony-brachas-reliable-broadcast/).
2. In round 2, each party waits for $n-f$ senders $S_i$, then takes the mode $v$ (most frequent value), breaking ties arbitrarily. Party $i$ uses $<v,S_i>$ as it’s proposal to an asynchronous consensus protocol with external validity.
3. A proposal $<v,S_i>$ becomes valid if:
    1. $\|S_i\| \geq n-f$; and
    2. all the Reliable Broadcasts in $S_i$ complete; and
    3. the mode of $S_i$ is $v$.

*Proof idea*: When $n>(m+1)f$, then $n-f > mf$. So it cannot be the case that all $m$ values of honest parties appear just $f$ times in any set of $n-f$ values. Hence there must exist at least one value from an honest party that appears at least $f+1$ times in any set of $n-f$. 

Values that are not input values of honest parties can appear at most $f$ times in any set of $n-f$ values. Hence the mode of any set of $n-f$ values will be an input value of an honest party.

Due to the reliable broadcast, and the validity check, a valid input of any party, even a malicious party, must be a value of one of the honest parties.

### Honest-input-or-default validity

One way to slightly relax validity with honest input validity is to allow a default value $\bot$ when not all honest parties have the same input.

**Honest-Input-or-Default Validity**: *If all honest have the same input then this must be the output value. Otherwise, the output must be an input of some honest party or a special value $\bot$.*

Note that [Cachin,  Guerraoui, Rodrigues, 2011](https://www.distributedprogramming.net) called this problem *Strong Validity* but we choose to use a more explicit name here to avoid overloading the term *strong*.


Note that this variation does not suffer from stronger lower bounds than regular consensus. See exercise 5.11 in [CGR11](https://www.distributedprogramming.net) for how to solve consensus with honest-input-or-default validity. In a nutshll, this is done again via a reduction to consensus with external validity (where the validity condition is that at least $f+1$ parties sent this input).

### Majority validity and advantaged validity

In honest input validity, we want the output to be one of the honest inputs. So it's okay that the output is 1 even if just one honest party has input 1 and all the other honest have input 0.

In cases where we view consensus as a **voting scheme** this seems too weak. If all-but-one honest parties vote for 0 we would like 0 to be the output! 

The natural way to capture this is via a validity requirement, that the output must be the majority value of the **honest** parties' inputs. More generally, for $m>2$, the [mode](https://en.wikipedia.org/wiki/Mode_(statistics)) of the **honest** parties inputs.


**Majority Validity**: *The output is the mode of the input of the *honest* parties. Note that for $m=2$, this is equivalent to saying that the output is the *majority* of the input values of the honest parties.*

Majority consensus feels very hard to obtain, perhaps it's impossible? How can we learn the mode of the honest parties if the malicious parties **and** asynchrony are colluding against us?

Indeed, [Fitzi and Garay](https://eprint.iacr.org/2002/085) prove that even a weaker validity requirement is **impossible** in asynchrony.

Consider the requirement to output the unique mode only if it has **at least $k$ honest votes more** than the honest votes of any other value. 

**$k$-advantaged Validity**: *If the unique mode of the honest parties has at least $k$ honest votes more than the number of honest votes for any other value, then this is the output.*

#### Impossibility of $2f$-advantaged validity in asynchrony


**Theorem [Fitzi and Garay, 2002]**: consensus with $2f$-advantaged Validity cannot be solved in asynchrony for any $n$ and any $f$ with a malicious adversary controlling $f$ parties, even for $m=2$.



*Proof idea*: suppose $G_1$ honest parties have the value 1 and $G_0$  honest parties have the value 0 and $\|G_1\|=\|G_0\|+2f$, but $f$ parties in $G_1$ are slow and the adversaries uses the value 0 as input for the $f$ malicious parties.

So parties will hear  $\|G_1\| -f$ parties with 1 and $\|G_0\|+f$ parties with 0.  The protocol may be randomized, so without loss of generality assume the decision will be 0 with probability at least 1/2. 

A decision of 0 violates the $2f$-advantaged validity property.

#### A tight upper bound for $2f+1$-advantaged validity in asynchrony

On the other hand,  $2f+1$-advantaged validity can be solved using a slight variation of the protocol above for consensus with honest input validity.


### Relevance of $k$-advantaged validity to voting on ordering

Consider the following scenario: two clients send commands and the replicas want to decide which client sent the command first. 

Note that this is essentially a voting problem - each replica can cast a vote on the order and malicious replicas can lie without any natural way of being detected.


This post discusses lower bounds that show that even for this simple binary decision, the best we can do is solve $2f+1$ advantaged consensus (see [Cachin, Micic, Steinhauer, and Zanolini, 2021](https://arxiv.org/abs/2112.06615)).

Note that for $n=3f+1$, the problem of $2f+1$ advantaged consensus is basically weak validity. This motivates looking at higher thresholds like $n>4f$.

Your thoughts on [Twitter](https://twitter.com/ittaia/status/1602310854510256128?s=20&t=w9YoXZkVX71peaPS1UN62g).

