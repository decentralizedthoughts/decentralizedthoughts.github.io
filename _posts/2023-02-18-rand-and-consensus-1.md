---
title: Randomization and Consensus - synchronous binary agreement for crash failures
  with a perfect common coin
date: 2023-02-18 06:00:00 -05:00
tags:
- consensus
- consensus101
- randomness
- crash
author: Ittai Abraham
---

What is the simplest setting where **randomization** can help solve **consensus**? Assume *lock-step* (**synchrony**) with $f<n$ **crash** failures. We know that in the [worst case](https://decentralizedthoughts.github.io/2019-12-15-synchrony-uncommitted-lower-bound/) reaching agreement takes at least $f+1$ rounds. This lower bound holds even if the protocol is randomized so the natural question is:

> Can randomization help reduce the *expected* number of rounds?

This post can be used as a prequel for our posts on how to use [randomness](https://decentralizedthoughts.github.io/2022-03-30-asynchronous-agreement-part-three-a-modern-version-of-ben-ors-protocol/) to solve [asynchronous agreement](https://decentralizedthoughts.github.io/2022-03-30-asynchronous-agreement-part-one-defining-the-problem/).


### Perfect common coin
Assume that in each round $j$, parties have access to a **perfect common coin**, ```coin_j```. The coin for round $j$ is *unpredictable* before the end of round $j$ and is *uniformly* distributed. A perfect coin is a strong assumption. We will show in later posts build it. 

### Binary agreement for crash failures with a perfect common coin

Each party has an input 0 or 1 and the goal is to output a  common value (agreement) that is an input value (validity). 

```
value := input

round j:
    send <value> to all parties
    if coin_j = value, then output value
    if hear both <0> and <1>, then value := coin_j
```

This protocol is so simple: if the coin equals your value then decide. Otherwise change to the coin value if you hear both 0 and 1. 

Adding a termination gadget is also easy:
```
Once you output value,
    then send <decide value> and terminate
Once you see <decide value>, 
    then output value 
```

### Analysis

**Validity**: clearly if all parties start with $b$ then they will never change their value. 

**Agreement**: consider the first round $v^\star$ where some party $i$ outputs $b$. So party $i$ did not crash before sending $b$ to all parties and the coin in round $v^\star$ is $b$.  At the end of round $v^\star$ all parties heard the value $b$ from $i$ so will either use the coin to set their value to $b$ or keep the value $b$. Similar to the validity argument above,  in any round $> v^\star$, since all parties start with $b$ then they will leave with $b$.

**Expected Termination**: Conditioned on no party outputting a value in any round $<j$, consider the first party to not crash in round $j$. With probability $1/2$ the coin will be equal to its values and it will output its value.

So we have shown that in expected 2 rounds there will be at least one party that outputs a value.

Conditioned on a party outputting value $b$ in round $<j'$, we know from agreement and validity that all parties enter round $j'$ with the value $b$. With probability $1/2$ the coin in round $j'$ will be $b$ and all non-faulty parties will output their value in round $j'$. 

So we have shown that in expected 4 rounds all non-faulty parties output a value. So terminate in expected 5 rounds.

In other words, given a perfect common coin, for any $f<n$ the expected number of rounds till all non-faulty parties terminate is constant.


### Zooming out
How did randomization help? we used the common coin as a *virtual leader*. To maintain *validity*, we only listen to the virtual leader when we hear both 0 and 1. For *safety* we decide only when the condition ```coin_j = value``` is true, this guarantees all other parties assign ```coin_j = value```.

Finally, why does the protocol end in an expected 5 rounds? it's because we assumed the coin is unpredictable! If the adversary knew the coin values in advance it could force a $f+1$ round execution.

By assuming the coin is unpredictable we implicitly assume there is a limit to the adaptive power of the adversary. It must send its round $j$ message before learning the round $j$ coin. In later posts, we will be even more explicit about the adaptive power of the adversary.

*Exercise*: consider a *super adaptive adversary with future-vision* that at the beginning of round $j$ knows in advance the coin value and can decide what parties to crash in round $j$ based on this information. Show a strategy for this adversary that forces a $f+1$ round execution.

The protocol relies heavily on assuming a perfect common coin. In the [next post](https://decentralizedthoughts.github.io/2023-02-19-rand-and-consensus-2/), we will solve consensus for omission failures without this assumption by building a weak common coin.
## Acknowledgments

Many thanks to Sravya Yandamuri and Naama Ben-David for insightful discussions and comments.

Your thoughts (and solution to the exercise) on [Twitter](https://twitter.com/ittaia/status/1626993583986249728?s=20).