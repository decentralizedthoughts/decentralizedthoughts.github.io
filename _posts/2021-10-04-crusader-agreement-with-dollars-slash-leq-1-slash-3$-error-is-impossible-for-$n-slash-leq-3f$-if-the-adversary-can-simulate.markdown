---
title: Crusader Agreement with $\leq 1/3$ Error is Impossible for $n\leq 3f$ if the
  Adversary can Simulate
date: 2021-10-04 10:46:00 -04:00
tags:
- lowerbound
- dist101
author: Ittai Abraham and Kartik Nayak
---

The classic [FLM lower bound](https://groups.csail.mit.edu/tds/papers/Lynch/FischerLynchMerritt-dc.pdf) says that in Synchrony, Byzantine Agreement is impossible when $n \leq 3f$. We discussed this important bound in a [previous post](https://decentralizedthoughts.github.io/2019-08-02-byzantine-agreement-is-impossible-for-$n-slash-leq-3-f$-is-the-adversary-can-easily-simulate/). In this post we strengthen the FLM lower bound in two important ways:
1. Maybe randomization allows circumventing the FLM lower bound? No! Even allowing $\leq 1/3$ error, this bound still holds (based on unpublished work of Yao and Karlin, see the work of [Graham and Yao, 1989](http://www.math.ucsd.edu/~ronspubs/89_08_byzantine.pdf)).
2. Maybe primitives that are weaker than Byzantine Agreement can circumvent this lower bound? No! Even when we weaken the agreement property this bound still holds (based on [Dolev's](https://www.cs.huji.ac.il/~dolev/pubs/byz-strike-again.pdf) work on Crusader Agreement).


### Crusader Agreement

Consider $n$ parties in the synchronous model, where at most $f$ of them are Byzantine: each party $i$ has an input $b_i \in \{0,1\}$ and must output a value in $\{0,1,\bot\}$.

1. **(Validity)**: If all honest parties have the same input then this must be the output of all honest parties.
2. **(Weak Agreement)**: It is never the case that one honest outputs 1 and another honest outputs 0.

***Exercise***: show a constant round protocol that solves Crusader agreement for any $n>3f$ (first correct answer on [twitter](https://twitter.com/kartik1507/status/1445048662430683138?s=20) gets $(n-f)$ DT coins).  

### Crusader Agreement with $\epsilon$-error

This is an even easier problem where you are allowed some probability $\epsilon$ of error:

1. **(Validity with $\epsilon$-error)**: If all honest parties have the same input then, for any adversary strategy, with probability at least $1-\epsilon$, this input value must be the output of all honest parties.
2. **(Weak Agreement with $\epsilon$-error)**: For any adversary strategy, with probability at least $1-\epsilon$, it is not the case that one honest outputs 1 and another honest outputs 0.

For example, a protocol that solves Crusader Agreement with $1/10$-error only needs to maintain Validity and Agreement, in expectation, in 9 out of 10 executions. Note that the probability distribution is on the coins of the honest parties.

### Strengthened Lower Bound:

***Theorem (FLM, KY, D)***: It is impossible to solve *Crusader Agreement with $\epsilon$-error* for any $\epsilon <1/3$ for $n \leq 3f$ if the adversary can simulate.

Before going into the proof, let us unpack this statement. It says that even if you allow considerable error (at most $1/3$) for both Validity and Agreement and **also** weaken the Agreement property to Weak Agreement it is still impossible when $n \leq 3f$.

Side note: one may wonder if *Crusader Ageement* is substantially weaker than Agreement? Indeed there is a significant round complexity separation:  We can solve Crusader agreement using a worst case constant number of rounds (for any $f<n/3$). But for Agreement there is $f+1$ round [lower bound](https://decentralizedthoughts.github.io/2019-12-15-synchrony-uncommitted-lower-bound/) on the worst case number of rounds (for any $f<n/3$).

### The Proof

As an indication of the strength of the FLM covering technique, the proof is quite similar. Here we show the $n=3$ case.

Six parties are connected in a cycle $A,B,C,A',B',C'$. Parties $A,B,C$ have input of 1 (shown in the blue color) and parties $A',B',C'$ have an input of 0 (shown in the red color). This is a great time to stop and ask: why is this setup well-formed? Why is it okay to take a protocol for three parties and wire it with six parties?

The beauty of the FLM proof is that this six node configuration is a valid, well-formed execution. Consider any two consecutive parties and examine the world where these two parties are honest and the adversary strategy is to simulate all the four remaining parties.

![World 1](https://i.imgur.com/Dx9ioKx.jpg)


In World 1, parties $B$ and $C$ have an input of 1. Since $B$ and $C$ are honest, from the Validity property, with $epsilon$-error, $C$ must decide 1 with probability of at least $2/3$. The adversary (depicted in red) simulates the parties $A,C',B',A'$ with inputs $1,0,0,0$ and relays messages between $B$ and $A$ and between $C$ and $A'$.

![World 2](https://i.imgur.com/0X5HUio.jpg)

In World 2, parties $A'$ and $B'$ have input of 0. From Validity, with $\epsilon$-error, $A'$ must decide 0 with probability at least $2/3$. The adversary (depicted in red) simulates the parties $A,C',B',A'$ with inputs $1,0,0,0$ and relays messages between $B$ and $A$ and between $C$ and $A'$.

![World 3](https://i.imgur.com/rtfI6zp.jpg)

Finally, consider World 3, where $C$ and $A'$ are honest. Note that $C$'s view is indistinguishable from World 1, so it will decide 1 with probability $>2/3$. Similarly, $A'$'s view is indistinguishable from World 2, so it will decide 0 with probability $>2/3$. Hence with probability, $>1/3$ $C$ and $A'$ will disagree on a non-$\bot$ value. This is a contradiction to the Agreement with $1/3$-error property.

![Indistinguishability for C](https://imgur.com/xMuacm3.png)


### Discussion

We have shown that the FLM lower bound holds for Agreement, and even for Crusader Agreement, even if you are allowed a constant error probability. 

Lower bounds in distributed computing are protocols for the adversary. The FLM lower bound is a striking example of a non-trivial adversary strategy: The adversary uses the protocol against itself.   

What if we weaken the Validity property instead of the Agreement property: **(Weak Validity)**: if all parties are non-faulty and have the same input then this is the output value. Can you solve this problem for $n=3$? What about solving this problem with probability $0.99$?

Your decentralized thoughts on [twitter](https://twitter.com/kartik1507/status/1445048662430683138?s=20)
