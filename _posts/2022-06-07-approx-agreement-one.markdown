---
title: 'Approximate Agreement: definitions and the robust midpoint protocol'
date: 2022-06-07 03:11:00 -04:00
tags:
- consensus
author: Ittai Abraham and Gilad Stern
---

This post covers the basics of **Approximate Agreement**. We define the problem, explain in what way its an interesting variation of classic [Agreement](https://decentralizedthoughts.github.io/2019-06-27-defining-consensus/), and describe the idea behind the robust midpoint protocol.


In classic consensus, the space of possible decision values is just a set and the goal is to agree on a decision value that must be the input value if all non-faulty have the same input value. *Approximate Agreement* is a variation, first suggested by [Dolev, Lynch, Pinter, Stark, Weihl, 1985-86](https://groups.csail.mit.edu/tds/papers/Lynch/jacm86.pdf), where the goal is to approximately agree (up to some $<\epsilon$ difference) on a value that is in the convex hull of the non-faulty input values. To make this well defined, in approximate agreement the space of possible decision values is a [convex set](https://en.wikipedia.org/wiki/Convex_set), for this post just assume the rational numbers $\mathcal{R}$. This naturally induces a notion of two values being *close* to each other  and that a value is *in between* two other values.

There are many cases where (approximate) agreement on a rational value makes sense. For example, if parties want to reach approximate agreement on the current exchange rate of dollar vs euro, we can define the distance between two exchange rates as say the distance in US cents. Similarly, if parties want to reach approximate agreement on the current temperature, we can define the distance between two measurements as say the distance in degrees of Celsius.


As in classic Agreement:

* **Validity**: if all non-faulty parties have the same value then this is the decision value.
* **Termination**: all non-faulty decide.

Unlike classic agreement, *Approximate Agreement* strengthens the validity property and weakens (relaxes) the agreement property:
* **Convex validity**: if a non-faulty party outputs $v$ then there exists some non-faulty parties with inputs $c_1$ and $c_2$ such that $c_1 \leq v \leq c_2$. More generally, we can say that $v$ must belong to the [convex hull](https://en.wikipedia.org/wiki/Convex_hull) of the non-faulty input values.
* **$\epsilon$-Approximate consensus**: if two non-faulty parties output $v_i$ and $v_j$  then $\|v_j-v_i\|<\epsilon$ (or more generally, $d(v_i,v_j)<\epsilon$). In other words, the decisions of all non-faulty are $\epsilon$-close to each other.


## Why is Approximate Agreement interesting?


From a foundations perspective, relaxing to **approximate consensus** allows to circumvent fundamental limitations of classic (exact) consensus and obtain qualitatively better round complexity. We will see in a [later post](..) that this relaxation circumvents the $f+1$ round lower bound in synchrony and the infinite execution lower bound in asnychrony. On the other hand, the strengthening to **convex validity** seems to require more resources and hence is an interesting trade-off.

From a practical perspective, there are use cases (many in the blockchain world) where we would like an *oracle service* to (approximately) agree on some external values and often these values have a natural notion of convexity (for example, the exchange rate of two assets or the interest rate, etc). In many of these cases the input values of non-faulty parties are close but not exactly the same. The classic validity property allows any value to be output in this case, which clearly does not seem like the desired outcome. Convex validity captures a very natural requirement of outputting a value in the convex hull of these inputs (for example, if all non-faulty inputs are in the range [3.99,4.01], we would want the output value to be in that range as well!).


## Convex validity using a broadcast channel

Let's jump right in and assume we have $n=3f+1$ parties and a malicious adversary that can control at most $f$ parties. Party $i$ has input $v_i \in \mathcal{R}$.

In this section we assume parties have access to a powerful a [broadcast channel](https://decentralizedthoughts.github.io/2019-06-27-defining-consensus/) (a blockchain). This makes everything much easier :-). The first step of the protocol is trivial:
```
Each party i broadcasts its input v_i
```

Assuming synchrony for now, each party gathers a multi-set $V$ of between $n-f$ and $n$ values from the broadcast values. The only question is how does a party extract a single decision value from this multi-set $V$?

What can the adversary do? Intuitively, if the adversary chooses to send values inside the non-faulty convex hull, it wouldn't do us much harm. These values are roughly where they should be. However, it can cause the $f$ parties it controls to post very high or very low inputs. So it is very natural to *trim* (or remove) the $f$ smallest and $f$ largest values from the multi-set $V$. Given a representation of $V$ as an ordered sequence $V=\\{v_1,v_2,\dots, v_k\\}$, define the **trim** of $V$ by $f$ values as the sub-multi-set formed by removing the lowest $f$ values and the highest $f$ values from the sequence.  

$$
T=trim(V)=\{v_{f+1},\dots,v_{k-f}\}
$$

Observe that $\|T\| = \|V\|-2f$ so $T$ is only well defined when $\|V\| \geq 2f+1$ (indeed this is why we required $n=3f+1$ and hence assured to see at least $n-f \geq 2f+1$ values). BTW the idea of trimming the outliers is deeply connected to [robust statistics](https://en.wikipedia.org/wiki/Robust_statistics).  

Let $G$ be the multi-set of input values of all the non-faulty parties.

We are now ready to state a simple but important fact about $\max(T)$ and $\min(T)$ relative to $\max(G), \min(G)$ and $median(G)$.

**Claim 1:** $median(G) \leq \max(T) \leq \max(G)$ and similarly $\min(G) \leq \min(T) \leq median(G)$.

*Proof:* 
To see that $\max(T) \leq \max(G)$ observe that the worst the adversary can do is post $f$ values that are higher than $\max(G)$ but those will be removed by $T=trim(V)$.

Recall that $T=trim(V)$ and $V$ is the set of all values that are broadcast. So in particular we have $G \subseteq V$.

To see that $median(G) \leq \max(T)$ observe that $2f+1 \leq  \|G\|$ hence even if the top $f$ values will be removed by $T=trim(V)$, the $median(G)$ value will remain.

The proof for $\min(G) \leq \min(T) \leq median(G)$ is identical.

We can finally complete the protocol, return the robust midpoint:

```
Given a multi-set V let T=trim(V)
output (max(T)+min(T))/2
```


*Proof:* Trivially we have termination and (exact) agreement from using the powerful the broadcast channel assumption. For convex validity, the claim above shows that $\min(G) \leq \min(T) \leq \max(T) \leq \max(G)$.

Note that any function that outputs a value in the convex hull of $T$ would be fine. For example some oracle services use the median (see [Chainlink](https://research.chain.link/whitepaper-v2.pdf)).



### In synchrony without a broadcast channel

Let's look at the natural robust midpoint protocol:
```
Each party i sends its input v_i to all
Each party waits for 2 Delta to gather a multi-set V
let T=trim(V)
output (min(T)+max(T))/2
```

*Proof:* Termination is immediate. Convex validity follows from Claim 1. What about (approximate) agreement?


For example with $n=4$, party A may see $V_1=\\{0,0,1,1\\}$ from parties A,B,C,D (so it outputs 1/2) and  party D may see $V_2 = \\{0,1,1,1\\}$ from parties $A,B,C,D$ (so it outputs 1). We don't have agreement, did we make progress? 

Yes! It's time to introduce an important measure for a multi-set of non-faulty parties:

$$ 
span(G) = \max(G)-\min(G)
$$

Let $G$ be the multi-set of input values of the non-faulty parties and $G_1$ be the multi-set of output values of the non-faulty from the protocol (so $G_1=\\{\frac{\min(T_i)+\max(T_i)}{2}\\}_{i \in G}$):

**Claim 2:** $span(G_1) \leq span(G)/2$.

*Proof:* 
From Claim 1 we have 

$$
median(G) \leq \max(T) \leq \max(G)
$$

and 

$$
\min(G) \leq \min(T) \leq median(G)
$$

Recall that

$$
\min(G_1) = \min_{i \in G} \frac{\min(T_i)+\max(T_i)}{2}
$$ 

So we have

$$
\min(G_1) \geq \frac{\min(G) + median(G)}{2}
$$ 

and similarly 

$$
\max(G_1) \leq \frac{\max(G) + median(G)}{2}
$$

Hence 

$$
span(G_1) =  \max(G_1) - \min(G_1) \\
\leq \frac{\max(G) + median(G)}{2} - \frac{\min(G) + median(G)}{2}\\
= \frac{\max(G) -\min(G)}{2} = span(G)/2
$$

Every time we do this calculation we are re-surprised how everything cleans up so nicely :-)

So what did we achieve? The robust mid-point protocol allows parties to output values in the convex hull of their inputs, while cutting their span in half!

In the next posts we will see how repeating this one round protocol can eventually cut the span to any desired $<\epsilon$ and how to terminate with approximate agreement.

Cant wait for the follow up post? Let us know if this protocol can also work in asynchrony?

Your thoughts/comments on [Twitter](https://twitter.com/ittaia/status/1534074996083109888?s=20&t=ytroU493gGzJind9MeGJKQ).

