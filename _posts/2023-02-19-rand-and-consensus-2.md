---
title: Randomization and Consensus - synchronous binary agreement for minority omission
  failures
date: 2023-02-19 06:00:00 -05:00
tags:
- dist101
- randomness
author: Ittai Abraham
---

Continuing the series on [simple ways](https://decentralizedthoughts.github.io/2023-02-18-rand-and-consensus-1/) where randomization can help solve consensus. The model is **lock-step** (synchrony) with $f<n/2$ **omission** failures. We know that in the [worst case](https://decentralizedthoughts.github.io/2019-12-15-synchrony-uncommitted-lower-bound/) reaching agreement takes at least $f+1$ rounds. Can randomization help reduce the expected number of rounds? In the post, we show a simple randomized consensus algorithm including a simple weak coin protocol that works against a weak adaptive adversary.

***Theorem: there exists a binary agreement protocol that is resilient to a weak adaptive adversary that can cause omission failures on a minority of parties. The expected number of rounds to terminate is constant and the expected number of messages is $O(n^2)$.*** 


### Weak adaptive adversaries

As in the [previous post](https://decentralizedthoughts.github.io/2023-02-18-rand-and-consensus-1/) for crash failures and in any use of randomness, we need to make sure that the randomness is *unpredictable* and that the adversary can only *adapt* to the randomness when it's too late for it to matter.

Here we show how to build a weak common coin against a *weakly adaptive adversary*. 

A *weak adaptive adversary* in the lock-step model that decides to corrupt a party after seeing its round $j$ message can only corrupt after the party sends all its round $j$ messages.

One way to think about this model is that the adversary is adaptive but needs one round of delay to take action in order to corrupt parties. This is in contrast to an *adaptive adversary* which can corrupt parties immediately after seeing what messages they sent, and a *strong adaptive adversary* that can also * and even *claw back* messages in the same round it corrupts.

### A weak common coin for minority omission failures against a weak adaptive adversary

A weak common coin for round $j$ has the following properties:

**Unpredictable**: The coin value for round $j$ cannot be predicted before seeing the round $j$ messages. 

**$\epsilon$-correct**: for any $b \in \{0,1\}$, with probability at least $\epsilon$, all parties output $b$. In particular, here we will aim for $1/4$-correct.

The following one round protocol for $f<n/2$ omission faults is a $1/4$ correct weak coin:
```
Each party randomly chooses:
    a rank in [1,...,n^2]
    a bit in [0,1]
    sends (rank,bit) to all parties

Each party that hears n-f (rank,bit) values:
    outputs the bit associated with the highest rank it heard
    (break ties arbitrarily)
```

*Unpredictability* holds because the randomness is chosen in round $j$. The weak adversary can either choose to act before seeing the messages - in which case the value is unpredictable, or after seeing a message - in which case the weak adversary must let that party round $j$ messages reach all parties before corrupting.

For $\epsilon$-correctness: with probability at least $1/2$, the maximum rank is obtained by a non-faulty party and is unique. Conditioned on this event, all non-faulty parties will output the coin of this non-faulty party. Hence, we obtain $1/4$-correctness.

Note that the argument above uses the fact that the adaptive power of the adversary is weak. Otherwise, it could have learned the value of the max rank and adaptively corrupted that party to potentially cause disagreement.

*Exercise*: show how an adversary that can see all the random coins in round $j$ and then decide how to corrupt parties in round $j$ can cause an execution of $\Omega(f)$ rounds. Can you show $f+1$ rounds?


Next, we build an agreement protocol from this simple $1/4$-correct weak random coin.


### Binary agreement for minority omission failures

Each party has an input 0 or 1 and the goal is to output a  common value (agreement) that is an input value (validity). 

The protocol runs in *phases*. Each phase consists of 3 *rounds*. A party that does not hear $n-f$ messages can simply shut itself down (crash) because it knows it has omission failures:



```
value := input

round 3j-2:
    send <value> to all parties
    wait for n-f or crash
    if all values are b, then value := b
    otherwise value := bot

round 3j-1:
    send <value> to all parties
    wait for n-f or crash
    if some value is b not bot, then value := b
    if all values are b, then output b

round 3f:
    send <rank, bit> to all parties
    wait for n-f or crash
    Let bit be from the highest rank
    if value := bot, then value := bit
```

Protocol in words: in the first round parties send their value and then either keep their value or switch to $\bot$ if they hear a conflict. In the second round, parties stay with $\bot$ only if they don't hear any other value and they output $b$ if they hear $n-f$ values of $b$. Finally, in the third round, parties that end with $\bot$ use the weak coin protocol to obtain a new value.


The protocol's analysis relies on *quorum intersection*: when $f<n/2$, any two sets of size $n-f$ must intersect by at least $n-2f>0$ elements.  


### Analysis

**Validity**: if all parties start with $b$ then all parties will hear $n-f$ values of $b$ in round one and hence all non-faulty will send $b$ in round 2. Hence all non-faulty will output $b$ at the end of round 2.

**Weak agreement for first round**: By quorum intersection, at the end of round one, it cannot be the case that parties have values 0 and 1. 

**Agreement**: consider the first phase $v^\star$ where a party $i$ outputs $b$ in the second round of phase $v^\star$. Since $i$ saw $n-f$ messages for $b$ and from quorum intersection, any party that reaches the end of round 2 must see at least one value of $b$. Moreover, from the weak agreement for the first round, no party will see $1-b$. Hence all such parties have their value set to $b$ and hence will ignore the coin value. Then in phase $v^\star +1$, all parties start with $b$, so similar to the validity property will output $b$ in the second round of this phase.


**Expected Termination**: Conditioned on no party outputting a value in phases $<j$, the adversary must choose either to cause all parties to output $\bot$ or to lean into one of the values. Assume the adversary chooses to bind to the value $b$.

We use the fact that the adversary had to choose which value to bind to before it know the value of the coin:

From the weak common coin properties, with probability of at least $1/4$ all parties will see $b$. Hence by the end of phase $j$ all parties have the value $b$. Either because this is the value they had at end of the second round, or because they use the coin value at the end of the third round.

This shows expected decision in constant number of rounds. *Exercise*: add a termination gadget that stops after one more round of helping.


**Message complexity**: each round has each party send an $O(1)$ size messages to all other parties, except for the rank which needs $O(\log n)$ bit size messages. One way to get to $O(n^2)$ expected bits is to only send a rank if its in the top $\log n / n$ percentile. This may increase the round complexity by a constant. 

### Zooming out

Each phase of the protocol consists of a graded crusader agreement protocol followed by a weak common coin protocol. This approach can be extended to the asynchronous setting as done in [this post](https://decentralizedthoughts.github.io/2022-03-30-asynchronous-agreement-part-three-a-modern-version-of-ben-ors-protocol/).

How did randomization help? we used the common coin as a *virtual leader*. To maintain validity, we only listen to the virtual leader when we are sure no party outputs a value in this round. Finally, for safety, parties that output $b$ are guaranteed that all parties have the value $b$.

## Acknowledgments

Many thanks to Sravya Yandamuri and Naama Ben-David for insightful discussions and comments.


Your thoughts on [Twitter](https://twitter.com/ittaia/status/1627375659889704962?s=20).

