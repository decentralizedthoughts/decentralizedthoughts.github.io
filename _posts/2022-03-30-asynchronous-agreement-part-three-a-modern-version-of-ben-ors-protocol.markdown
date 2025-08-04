---
title: 'Asynchronous Agreement Part Three: a Modern version of Ben-Or''s protocol'
date: 2022-03-30 07:21:00 -04:00
tags:
- asynchrony
- consensus
- research
author: Ittai Abraham, Naama Ben-David, Sravya Yandamuri
---

In this series of posts, we explore the marvelous world of consensus in the [Asynchronous model](https://decentralizedthoughts.github.io/2019-06-01-2019-5-31-models/). In this third post, we present a modern version of Ben-Or's classic [protocol](https://homepage.cs.uiowa.edu/~ghosh/BenOr.pdf) that is part of our new work on Asynchronous Agreement. In the [first post](https://decentralizedthoughts.github.io/2022-03-30-asynchronous-agreement-part-one-defining-the-problem/) we defined the problem and in the [second post](https://decentralizedthoughts.github.io/2022-03-30-asynchronous-agreement-part-two-ben-ors-protocol/) we presented Ben-Or's protocol. This is a simplified version extracted from our [paper](https://eprint.iacr.org/2022/711.pdf).

We decompose Ben-Or's protocol into an outer protocol and an inner protocol (which we call *Graded Binding Crusader Agreement (GBCA)*). This decomposition allows us to reason more modularly and easily about each part. In particular, we show how to carefully reason about an adaptive adversary, by forcing the adversary to ***bind*** to a certain value so that its future options are limited by the protocol.

## Graded Binding Crusader Agreement (GBCA)
Graded Binding Crusader agreement is similar to other agreement problems in that each party has an input value, and must eventually decide on an output value. There are two differences: First, in addition to deciding on an output value, each party also decides on a $grade \in \{0,1,2\}$. Second, while the input value is either 0 or 1, the output value can be either 0, or 1, or a special value $\bot$. GBCA has the following five properties:

* **Weak Agreement**: If two parties output values $x$ and $y$, then either $x=y$ or at least one of the values is $\bot$.
* **Validity**: If all parties have the same input $x$, then all outputs will be with value $x$ and grade 2.
* **Termination**: All non-faulty parties terminate after a constant number of rounds.

The grade is used for the fourth property: 

* **Knowledge of Agreement**: If a party outputs value $x$ and grade 2, then all outputs will be with value $x$ with grade $\geq 1$.

It is critical to prevent the adversary from being able to pick the output value of a party *after* seeing the first non-faulty party output a value. We call this additional property ***Binding*** since the adversary is bound to a specific output value from each crusader agreement instance. We do so with the fifth property:

* **Binding:** At the time at which the first party outputs a value, there is a value $b \in \{0,1\}$ such that no party outputs value $1−b$ in any extension of this execution.

Intuitively, GBCA does two things useful for asynchronous agreement. First, it forces the adversary to choose either non-0 or non-1, before the adversary knows the coin values. Second, it lets a party decide if it sees a grade of 2. Given these properties it's easy to implement *Asynchronous Agreement*:

## Asynchronous Agreement from Graded Binding Crusader Agreement

The pseudo-code for Asynchronous Agreement from Graded Binding Crusader Agreement is quite simple:

```
Asynchronous Agreement for party i

input: v (0 or 1)
r:= 1

while true
    (value, grade) := GBCA(r,v)
    if grade = 2, then decide(value)
    if value = bot, then v:= coin()
    otherwise v:= value
    r++    
```

Note that we add the round number $r$ to each GBCA instance to differentiate the instances of each round. For termination, we use the folklore termination gadget described in [the previous post](https://decentralizedthoughts.github.io/2022-03-30-asynchronous-agreement-part-two-ben-ors-protocol/).

The Asynchronous Agreement property of **Weak Validity** follows from the GBCA Validity property directly. Similarly, the Asynchronous Agreement property of **Agreement** follows from the GBCA Knowledge of Agreement property. So let's focus on the Asynchronous Agreement property of **Finite Expected Termination**.

**Claim:** The protocol terminates in an expected $O(2^n)$ rounds.

*Proof:*  in every round $r$ the adversary has to bind to some value $b$ before seeing any coin value. Now with probability $O(2^{-n})$ all the coins for this round $r$ turn out to be $b$. If this event happens, then from the GBCA Weak Agreement property, all parties end the GBCA with either $b$ or $\bot$. In either case, since all coins are $b$, each party that starts round $r+1$ will have the same value $b$. Hence they will all decide $b$ and terminate at the end of round $r+1$. 

Note that this bound is significantly better than the $O(2^{2n})$ bound obtained by [Aguilera and Toueg 1998](https://ecommons.cornell.edu/bitstream/handle/1813/7336/98-1682.pdf?sequence=1&isAllowed=y). Moreover, we will discuss in later posts, our protocol provides better bounds with a weak common coin.

We hope that the relative simplicity of the termination argument is convincing evidence of the advantage of modularizing the protocol. All we need to do now is provide a protocol that solves Graded Binding Crusader Agreement against an adaptive adversary.

## A protocol for Graded Binding Crusader Agreement

The protocol for GBCA is rather simple, using three rounds of exchange:

```
GBCA for party i

input: v (0 or 1)
input: r (round number)

send <echo1, r, v> to all
wait for n-f <echo1, r, *>
    if all have value w, then send <echo2, r, w> to all
    otherwise, send <echo2, r, bot> to all
wait for n-f <echo2, r, *>
    if all have value w, then send <echo3, r, w> to all
    otherwise, send <echo3, r, bot> to all
wait for n-f <echo3, r, *>
    if all have the same non-bot value u, then output u, grade 2
    if all have the value bot, then output bot, grade 0
    otherwise, if u is a non-bot value from <echo3, r, *>, then output u, grade 1
```

Let's go over the five GBCA properties and prove them one by one assuming $n>2f$ and the adversary can corrupt and apply crash faults to at most $f$ parties:


*Weak Agreement*: this follows from quorum intersection on echo1 messages. Since $n>2f$, it cannot be that $n-f$ parties send `<echo1,r,1>` and $n-f$ parties send `<echo1,r,0>`. Thus, only one non-bot value can be sent in an `<echo2, r, *>` message, and therefore the same applies to echo3 messages, and to the decision value.

*Validity*: follows from the first condition of each of the three rounds.

*Termination*: follows since parties only wait for $n-f$ responses for each of the three rounds.

*Knowledge of Agreement*: follows from Weak Agreement and the echo3 quorum intersection, it cannot be that one party sees $n-f$ `<echo3,r,b>` for value $b$ (has grade 2), but some other party sees $n-f$ `<echo3,r,*>` with not even one having value $b$.

*Binding*: Consider the time at which the first non-faulty party $i$ sends `<echo3, r, *>`. Case 1: if any of the $n-f$ `<echo2, r, *>` messages $i$ received had a non-$\bot$ value $w$, then from  Weak Agreement the adversary has binding to $w$. So the only remaining case is Case 2: that party $i$ heard $n-f$ `<echo2, r, bot>` messages. In that case, from quorum intersection on echo2, any party that sees $n-f$ `<echo2, r, *>` messages must see at least one `<echo2, r, bot>`, hence all such parties will send `<echo3, r, bot>`. Therefore, in this case, all parties will output $\bot$ hence the adversary binding to both 1 and 0. 


To conclude, the first round gives Weak Agreement, the second round gives Binding, and the third round gives Knowledge of Agreement. 

Observe that the binding event happens when the first non-faulty sends echo3, which is one round earlier than the first party ends of the protocol. This will be important when more sophisticated common coins are used. 

In the [next post](https://decentralizedthoughts.github.io/2022-04-05-aa-part-four-CA-and-BCA/) we will consider the Byzantine adversary case.


Your thoughts and comments on [Twitter](https://twitter.com/ittaia/status/1509241231628505089?s=20&t=fAtKRZZronoJUDA2PtDEWw)
