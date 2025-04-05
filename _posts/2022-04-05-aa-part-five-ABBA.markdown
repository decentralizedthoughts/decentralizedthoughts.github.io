---
title: 'Asynchronous Agreement Part 5: Binary Byzantine Agreement from a strong common
  coin'
date: 2022-04-05 08:11:00 -04:00
tags:
- asynchrony
- dist101
- research
author: 'Ittai Abraham, Naama Ben-David, Sravya Yandamuri '
---

In this post we show how to use Binding Crusader Agreement from the [previous post](https://decentralizedthoughts.github.io/2022-04-05-aa-part-four-CA-and-BCA/), along with a strong common coin to get a simple and efficient  Binary Byzantine Agreement with only an expected $O(n^2)$ message complexity. This is a simplified version from our [paper](https://eprint.iacr.org/2022/711.pdf).


In the four previous posts we: (1) [defined the problem](https://decentralizedthoughts.github.io/2022-03-30-asynchronous-agreement-part-one-defining-the-problem/) and discussed the [FLP theorem](https://decentralizedthoughts.github.io/2019-12-15-asynchrony-uncommitted-lower-bound/); (2) [Ben-Or's protocol](https://decentralizedthoughts.github.io/2022-03-30-asynchronous-agreement-part-two-ben-ors-protocol/) for crash failures;  (3)  [a modern version](https://decentralizedthoughts.github.io/2022-03-30-asynchronous-agreement-part-three-a-modern-version-of-ben-ors-protocol/) for crash failures; and (4) Crusader Agreement and [Binding Crusader Agreement](https://decentralizedthoughts.github.io/2022-04-05-aa-part-four-CA-and-BCA/) in the Byzantine Model.



Over the years, many solutions have been proposed for Asynchronous Binary Byzantine Agreement that use random coin flips. In this post, we aim to present existing algorithms for ABA under a common framework, and to make reasoning about such algorithms as simple as possible.

## Common Coins

First we need to define *random common coins* with two parameters, controlling their fairness and their unpredicability, as follows.

> An **$\epsilon$-good $d$-unpredictable common coin** provides an *access* primitive that takes no arguments and outputs either $0$ or $1$ with the following properties:
>* The output value for all parties is completely unpredictable until at least $d+1$ parties have accessed the coin.
>* With probability at least $\epsilon$, all non-faulty parties get $0$, and with probability at least $\epsilon$, all non-faulty parties get $1$.

In this post, we focus on the simplest setting: we assume that we have access to a *strong common coin*:

**Strong common coin**: is a $1/2$-good $f$-unpredictable coin where $f$ is the maximum number of faulty parties in the system.

In other words, all parties have access to a shared source of randomness which outputs either 0 to all parties or 1 to all parties, this value is not revealed until at least one non-faulty party accesses the strong common coin. In later posts, we'll relax this assumption and show how that affects algorithms for ABA.

Before showing an algorithm that *does* work, lets first look at a protocol that seems to work and understand where it fails. 

## Crusader Agreement (CA) is not enough for Asynchronous Binary Byzantine Agreement with a strong common coin
Recall that in Crusader Agreement, parties have an input of either 0 or 1 and an output of either 0, or 1, or a special value $\bot$ such that:

* **Weak Agreement**: If two non-faulty parties output values $x$ and $y$, then either $x=y$ or one of the values is $\bot$.
* **Validity**: If all non-faulty parties have the same input, then this is the only possible output. Furthermore, if a non-faulty party outputs $x \neq \bot$, then $x$ was the input of some non-faulty party.
* **Termination**: All non-faulty parties eventually terminate.

Many ABA algorithms in the literature can be viewed as operating in rounds of crusader agreement followed by coin flips. We illustrate this concept in the following pseudocode.

In this pseudocode, we call CrusaderAgreement with a round number. We assume that each new round number gets a new CrusaderAgreement instance in which all variables are reinitialized, and that messages with different round numbers are ignored. The StrongCommonCoin() function returns $0$ for all parties with probability $1/2$ and $1$ for all parties with the remaining probability $1/2$.

```
Atempting Asynchronous Binary Byzantine Agreement via Crusader Agreement

input: v (0 or 1)
r:= 1

while true
    value := CrusaderAgreement(r,v)
    c:= StrongCommonCoin()
    if value != bot, then
        v:= value
        if c = v, then decide(v) 
    otherwise v:= c
    r++    
```

The PODC 2014 version of [Mostefaoui, Moumen, Raynal](https://dl.acm.org/doi/10.1145/2611462.2611468) has a similar structure. However, it is known that against an adaptive adversary this protocol **will never terminate**.

Consider the following execution, with $n=4$ and $f=1$. Parties $X$ and $Y$ are non-faulty, party $B$ is Byzantine, and party $S$ is non-faulty but slow. $X$’s input is 0 and $Y$’s input is 1.
Let $X$ and $Y$ call crusader agreement, and let them both decide $\bot$. Then, we have $X$ and $Y$ reveal the coin, $c$. The adversary, knowing $c$, will now force $S$ to decide $1-c$ in its crusader agreement. This will ensure that while $X$ and $Y$ both start the next round with value $c$, $S$ starts the next round with $1-c$. We can then continue this execution forever, rotating $X,Y,S$ roles since we can always create rounds in which not all non-faulty parties have the same input.
Note that by the definition of crusader agreement as stated at the beginning of this post, there is nothing to prevent the above scenario from happening. Indeed, many implementations of crusader agreement do allow this to happen. 

We can see that crusader agreement alone is not enough to solve ABA in the framework illustrated in the pseudocode above.


##  Asynchronous Binary Byzantine Agreement with a strong common coin from Binding Crusader Agreement (BCA)
Recall that in Binding Crusader Agreement (BCA) strengthens the definition of crusader agreement by adding:

* **Binding:** At the time at which the first non-faulty party outputs a value, there is a value $b$ such that no non-faulty party outputs the value $1−b$ in any extension of this execution.



We show that simply **replacing** the line ``value:= CrusaderAgreement(r,v)``  with ``value:= BindingCrusaderAgreement(r,v)``  in the pseudocode above **yields a correct ABA algorithm**. To do so, we first recall the definition of Asynchronous Byzantine Agreement:

* **Agreement:** If two non-faulty parties decide $x$ and $y$ respectively, then $x=y$.
* **Weak Validity:** If all parties are non-faulty and have the same input $x$, then no non-faulty party decides a value $y \neq x$.
* **Finite Expected Termination:** All non-faulty parties decide in a finite expected number of rounds.

In fact we will show that with a strong common coin, the protocol above terminates in a **constant** expected number of rounds. 

Proof of Correctness of ABA with Binding Crusader Agreement and a Strong Common Coin.

**Lemma 1:** If all non-faulty parties start a round $r$ with the same value $b$, then all non-faulty parties will decide $b$ within a constant expected number of rounds.

*Proof:* As expected, we use the properties of Binding Crusader Agreement (BCA). By BCA Validity, since every non-faulty party inputs $b$ to the instance of BCA, all non-faulty parties output $b$. If $c=b$ then all non-faulty parties `decide(b)` in this round. Otherwise, all non-faulty parties set `v:= b` and start the next round. This continues for each round until we reach a round in which $c=b$, which happens in an expected constant number of rounds from round $r$.

Using this lemma, it is now easy to show the correctness of the ABA algorithm.

**Agreement:** 
Note that a non-faulty party $X$ only decides a value in a round $r$ if the coin agreed with its value and it was the output of $X$’s BCA in round $r$. Let $X$ be the first non-faulty party that decides, and let $r$ be the round in which it decides. Note that in round $r$, no other value can be decided, since the decision value is always the same as the coin of that round. Recall that BCA ensures that if a non-faulty party outputs $x$ from BCA, every other non-faulty party outputs either $\bot$ or $x$ from that instance of BCA. Since the coin value was $x$ in round $r$, all non-faulty parties must have started round $r+1$ with $v:=x$. Therefore, by the lemma above, every other correct party Y must also decide x.

**Validity:**
If all non-faulty parties have the same input, then they all start round $r=1$ with the same value. Therefore, by Lemma 1, they will all decide on that input in a constant expected number of rounds.

**Constant Expected  Termination:**
Note that if in any round, either all non-faulty parties decide $\bot$ in their BCA, or the coin is the same as the non-$\bot$ decision value of BCA, then Lemma 1 applies in the next round. Furthermore, by the binding property of BCA, the adversary is bound to some non-$\bot$ decision value of the BCA in any round $r$ (if there is one) by the time the first non-faulty party finishes its BCA in round $r$. In particular, this must happen before the coin value is revealed in any coin that is $f$ unpredictable. Therefore, in each round, with probability at least $1/2$ the BCA **binded** value $b$ will be the same as the Strong Common Coin.

**Message Complexity:**
Since each round takes $O(n^2)$ messages of constant size, the expected message complexity is $O(n^2)$ which is asymptotically optimal.  

### A note on Byzantine Finality Gadgets

Much like in the [crash-model](https://decentralizedthoughts.github.io/2022-03-30-asynchronous-agreement-part-two-ben-ors-protocol/), we can add a folklore Byzantine Termination Gadget to ensure termination:

```
Termination Gadegt for Byzantine failures

If receive f+1 <decide u>, then
    decide(u) 
If decide(u), then
    send <decide u> to all
If receive n-f <decide u>, then
    Terminate.
```

Note that the first condition is safe, since it means that at least one non-faulty party sent `<decide u>`. Second, if all non-faulty parties decide, then they terminate in one round due to the third condition. Finally the activation of the third condition implies that all non-faulty parties will eventually activate the first condition which in turn implies all non-faulty parties will terminate (even if they did not decide yet).

Thoughts and comments on [Twitter](https://twitter.com/ittaia/status/1511665002188574727?s=20&t=gJEZwTvUN72KwbNBJ53eYQ).
