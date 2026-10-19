---
title: 'Approximate Agreement: definitions and the Robust Midpoint protocol'
date: 2022-06-07 03:11:00 -04:00
tags:
- consensus
author: Ittai Abraham and Gilad Stern
---

This post covers the basics of **Approximate Agreement**. We define the problem, explain in what way it's an interesting variation of classic [Agreement](https://decentralizedthoughts.github.io/2019-06-27-defining-consensus/), and describe the idea behind the Robust Midpoint protocol.


In classic consensus, the space of possible decision values is just a set and the goal is to agree on a decision value that must be the input value if all honest parties have the same input value. *Approximate Agreement* is a variation, first suggested by [Dolev, Lynch, Pinter, Stark, Weihl, 1985-86](https://groups.csail.mit.edu/tds/papers/Lynch/jacm86.pdf), where the goal is to approximately agree on a value that is in the convex hull of the honest input values. In this post, inputs and outputs are rational numbers in $\mathbb{Q}$, and the distance between two values is their absolute difference.

There are many cases where (approximate) agreement on a rational value makes sense. For example, if parties want to reach approximate agreement on the current exchange rate of dollar vs euro, we can define the distance between two exchange rates as say the distance in US cents. Similarly, if parties want to reach approximate agreement on the current temperature, we can define the distance between two measurements as say the distance in degrees of Celsius.


For a parameter $\epsilon>0$, *Approximate Agreement* has three requirements:

* **Convex validity**: every honest party's output lies between the minimum and maximum honest input values, that is, in their [convex hull](https://en.wikipedia.org/wiki/Convex_hull).
* **$\epsilon$-Approximate agreement**: if two honest parties output $v_i$ and $v_j$, then $\lvert v_j-v_i\rvert<\epsilon$.
* **Termination**: every honest party eventually outputs.

Convex validity implies classic validity: if all honest inputs equal $v$, every honest output must equal $v$. Informally, classic agreement requires everyone to decide on exactly the same value; approximate agreement allows slightly different decisions, but requires each decision to stay within the range of the honest inputs.


## Why is Approximate Agreement interesting?


From a foundations perspective, relaxing to **approximate consensus** allows to circumvent fundamental limitations of classic (exact) consensus and obtain qualitatively better round complexity. We will see in a later post that this relaxation circumvents the $f+1$ round lower bound in synchrony and the infinite execution lower bound in asynchrony. On the other hand, the strengthening to **convex validity** seems to require more resources and hence is an interesting trade-off.

From a practical perspective, there are use cases (many in the blockchain world) where we would like an *oracle service* to (approximately) agree on some external values and often these values have a natural notion of convexity (for example, the exchange rate of two assets or the interest rate, etc). In many of these cases the input values of honest parties are close but not exactly the same. The classic validity property allows any value to be output in this case, which clearly does not seem like the desired outcome. Convex validity captures a very natural requirement of outputting a value in the convex hull of these inputs (for example, if all honest inputs are in the range [3.99,4.01], we would want the output value to be in that range as well!).


## Convex validity using a broadcast channel

Let's jump right in and assume we have $n=3f+1$ parties and at most $f$ Byzantine parties controlled by an adversary. Party $i$ has input $v_i \in \mathbb{Q}$.

In this section we assume parties have access to a powerful [broadcast channel](https://decentralizedthoughts.github.io/2019-06-27-defining-consensus/) (a blockchain). This makes everything much easier :-). The first step of the protocol is trivial:
```
Each party i broadcasts its input v_i
```

Assuming synchrony for now, we assume that all honest parties obtain the same multi-set $V$ by the end of the round. It contains every honest party's input (including one's own exactly once) and at most one rational number per Byzantine sender. Thus $V$ contains between $n-f$ and $n$ values. Having the same $V$ is essential for exact agreement. Receiving the same value for each broadcast does not ensure that everyone has collected the same broadcasts before deciding. The only question is how does a party extract a single decision value from this multi-set $V$?

What can the adversary do? Intuitively, if the adversary chooses to send values inside the convex hull of the honest inputs, it wouldn't do us much harm. These values are roughly where they should be. However, it can cause the $f$ parties it controls to post very high or very low inputs. So it is very natural to *trim* (or remove) the $f$ smallest and $f$ largest values from the multi-set $V$. Given a representation of $V$ as an ordered sequence $V=\\{v_1,v_2,\dots, v_k\\}$, define the **trim** of $V$ by $f$ values as the sub-multi-set formed by removing the lowest $f$ values and the highest $f$ values from the sequence.

$$
T=trim(V)=\{v_{f+1},\dots,v_{k-f}\}
$$

Observe that $\lvert T\rvert = \lvert V\rvert-2f$ so $T$ is only well defined when $\lvert V\rvert \geq 2f+1$ (indeed this is why we required $n=3f+1$ and hence assured to see at least $n-f \geq 2f+1$ values). BTW the idea of trimming the outliers is deeply connected to [robust statistics](https://en.wikipedia.org/wiki/Robust_statistics).

Let $G_0$ be the multi-set of input values of all the honest parties.

We are now ready to state a simple but important fact about $\max(T)$ and $\min(T)$ relative to $\max(G_0), \min(G_0)$ and $median(G_0)$.

**Claim 1:** $median(G_0) \leq \max(T) \leq \max(G_0)$ and similarly $\min(G_0) \leq \min(T) \leq median(G_0)$.

*Proof:* 
To see that $\max(T) \leq \max(G_0)$ observe that the worst the adversary can do is post $f$ values that are higher than $\max(G_0)$ but those will be removed by $T=trim(V)$.

The same argument shows that $\min(G_0) \leq \min(T)$, since at most $f$ values can be below $\min(G_0)$.

Let $m=median(G_0)$. Since $\lvert G_0\rvert\geq 2f+1$, at least $f+1$ honest inputs are at or below $m$, and at least $f+1$ are at or above $m$. All these inputs occur in $V$, so its $(f+1)$-st smallest entry is at most $m$, and its $(f+1)$-st largest entry is at least $m$. These entries are precisely $\min(T)$ and $\max(T)$, respectively. Thus $\min(T)\leq m\leq\max(T)$. The median lies between $\min(T)$ and $\max(T)$, even when it is not an entry of $T$.

We can finally complete the Robust Midpoint protocol:

```
Given a multi-set V let T=trim(V)
output (max(T)+min(T))/2
```


*Proof:* Termination follows because all honest parties obtain $V$ by the end of the round. Exact agreement follows because all honest parties compute the same midpoint from the same multi-set $V$. For convex validity, the claim above shows that $\min(G_0) \leq \min(T) \leq \max(T) \leq \max(G_0)$.

Note that any function that outputs a value in the convex hull of $T$ would be fine. For example some oracle services use the median (see [Chainlink](https://research.chain.link/whitepaper-v2.pdf)).



### In synchrony without a broadcast channel

Assume synchronous rounds: all honest parties send at the start of a round, and their messages arrive by its end. Let's look at one round of the natural Robust Midpoint protocol. It halves the span of honest values; one round alone need not achieve $\epsilon$-approximate agreement.

```
Each party i includes its own input v_i in V_i exactly once
At the start of the round, i sends v_i to every other party
Through the end of the round, i collects at most one rational number
  per other sender into V_i
let T_i=trim(V_i)
output (min(T_i)+max(T_i))/2
```

Each honest party collects through the end of the round, rather than stopping after $n-f$ values. Thus every honest input appears in every honest party's $V_i$, and $n-f\leq \lvert V_i\rvert\leq n$. Byzantine senders may contribute different values to different parties.

*Proof:* Termination is immediate at the end of the round. Convex validity follows by applying Claim 1 to each $T_i$. What about (approximate) agreement?


For example with $n=4$, party A may see $V_A=\\{0,0,1,1\\}$ from parties A,B,C,D (so it outputs 1/2) and  party D may see $V_D = \\{0,1,1,1\\}$ from parties $A,B,C,D$ (so it outputs 1). We don't have agreement, did we make progress?

Yes! It's time to introduce an important measure for a multi-set of values held by honest parties:

$$ 
span(G_0) = \max(G_0)-\min(G_0)
$$

Let $G_0$ be the multi-set of input values of the honest parties and $G_1$ be the multi-set of output values of the honest parties from the protocol (so $G_1=\\{\frac{\min(T_i)+\max(T_i)}{2}\\}_{i\text{ honest}}$):

**Claim 2:** $span(G_1) \leq span(G_0)/2$.

*Proof:* 
From Claim 1, for every honest party $i$, we have

$$
median(G_0) \leq \max(T_i) \leq \max(G_0)
$$

and 

$$
\min(G_0) \leq \min(T_i) \leq median(G_0)
$$

Recall that

$$
\min(G_1) = \min_{i\text{ honest}} \frac{\min(T_i)+\max(T_i)}{2}
$$ 

So we have

$$
\min(G_1) \geq \frac{\min(G_0) + median(G_0)}{2}
$$ 

and similarly 

$$
\max(G_1) \leq \frac{\max(G_0) + median(G_0)}{2}
$$

Hence 

$$
span(G_1) =  \max(G_1) - \min(G_1) \\
\leq \frac{\max(G_0) + median(G_0)}{2} - \frac{\min(G_0) + median(G_0)}{2}\\
= \frac{\max(G_0) -\min(G_0)}{2} = span(G_0)/2
$$

Every time we do this calculation we are re-surprised how everything cleans up so nicely :-)

So what did we achieve? The Robust Midpoint protocol allows parties to output values in the convex hull of their inputs, while cutting their span in half!

Can this protocol also work in asynchrony?

## Notes

* The [complete-protocol post](/2026-10-17-approximate-agreement-complete-protocol/) adds a known interval containing all honest inputs and a stopping rule, showing how repeating this round achieves $\epsilon$-approximate agreement.
* The [send-omission lower-bound post](/2026-10-19-approximate-agreement-send-omissions-lower-bound/) shows why achieving span below $1/n$ requires $\Omega(\log n/\log\log n)$ rounds when $f=\Theta(n)$, even with send omissions alone.

Your thoughts/comments on [Twitter](https://twitter.com/ittaia/status/1534074996083109888?s=20&t=ytroU493gGzJind9MeGJKQ).
