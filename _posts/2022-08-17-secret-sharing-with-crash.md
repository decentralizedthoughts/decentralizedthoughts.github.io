---
title: Polynomial Secret Sharing with crash failures
date: 2022-08-17 08:00:00 -04:00
tags:
- cryptography
author: Ittai Abraham
---

We continue our series on polynomial secret sharing. In the [previous post](https://decentralizedthoughts.github.io/2020-07-17-polynomial-secret-sharing-and-the-lagrange-basis/) of this series we discussed secret sharing with a [passive adversary](https://decentralizedthoughts.github.io/2019-06-07-modeling-the-adversary/). In this post we assume **crash failures** and in later posts we extend to [malicious failures](https://decentralizedthoughts.github.io/2022-08-24-BGW-secret-sharing/). As before, we must assume parties have **private channels**: the adversary cannot see the content of messages sent between two non-faulty parties.

### What is a Secret Sharing scheme?

A *secret sharing scheme* is composed of two protocols: *Share* and *Reconstruct*. These protocols are run by the $n$ parties. The dealer has a *secret* $s$ in a commonly known finite field $\mathbb{F}_p$ with $p>n$, which is given as *input* to the Share protocol. The two properties are:

1. **Validity**: If the share protocol completes, the output of the Reconstruct protocol is the dealer's input value $s$.
2. **Hiding**: If no honest party has begun the Reconstruct protocol, then the adversary can gain no information about $s$. 

In later posts we will address the malicious dealer case which will introduce the third property: **Binding**.

We also need termination properties:

3. **Weak Termination of Share**: if the dealer is non-faulty then all non-faulty parties complete the Share protocol.
   In some cases a stronger property is needed:
   **Strong Termination of Share**: if non-faulty completes the Share protocol then all non-faulty parties complete the Share protocol.
4. **Termination of Reconstruct**: if all non-faulty parties complete the share protocol then all non-faulty parties complete the Reconstruct protocol.

See the last section of this post for a discussion on the strong termination property.

### The main idea

TL;DR: **For an adversary controlling $f$ parties, use a degree $f$ polynomial and $n>2f$.**

Parties are enumerated $N=\{1,2,3,\dots,n\}$. Given input $s \in \mathbb{F}_p$, the dealer chooses a uniformly random polynomial $p(x)$, conditioned on $p(0)=s$. The dealer then gives party $i$ the value $p(i)$ which we call its *share*.  

The adversary controls $f$ parties, hence gets to see $f$ shares and can also crash these parties. So what degree should $p(x)$ be? and how many parties do we need to tolerate $f$ crash failures?

1. For **Hiding** to hold, we need to share using a polynomial of degree $\geq f$ (otherwise the adversary can learn the secret during the Share protocol simply by interpolating its shares). 
2. Since at least $f+1$ shares are required for unique reconstruction (for a polynomial of degree $\geq f$) and $f$ parties may crash, then we need $n \geq 2f+1$ for **Validity**.

Hence, we choose $p(x)$ from all polynomials of degree at most $f$ and choose $n=2f+1$.

### Secret Sharing with weak termination

**Share protocol**:
Given a secret $s$ as input, the dealer *randomly* chooses $f$ values $p_1,\dots,p_{f} \in_R \mathbb{F}_p$ and defines a degree $\le f$ polynomial:

$$p(X)=s+p_1 X + \dots + p_f X^f$$

The dealer then sends $p(i)$ to party $i$, for each $i \in N$.

**Reconstruct protocol**: 
Each party $i$ sends its share $p(i)$ to all other parties. 
Each party receives at least $n-f$ shares. Let $I$ be the subset of the first $f+1$ parties whose shares are received. Note that at most $f$ parties may crash, so at least $n-f \geq f+1$ shares will arrive (here we use $n>2f$). 

Each party outputs the dealer's original secret $s$ as follows:

$$s=p(0)=\sum_{i \in I} \lambda_i p(i)$$

Here, $p(i)$ is the share sent by party $i \in I$ and $\lambda_i$ are the Lagrange interpolation coefficients:

$$\lambda_i = \frac{\prod_{j \in I \setminus \{i\}} j}{\prod_{j \in I \setminus \{i\}} (j-i)}$$

### Proof of Validity, Hiding, and Weak Termination

Validity follows from the one-to-one mapping of degree at most $f$ polynomials and any $f+1$ shares. 

Similarly, Hiding follows since, for any $s$, conditioned on $p(0)=s$, the one-to-one mapping of degree at most $f$ polynomials to any $f$ shares (held by the adversary) implies that the uniform distribution on the coefficients $p_1,\dots,p_f$ induce a uniform distribution on the adversary view. The adversary view is therefore independently and uniformly random, for any value $s$. You can find a more detailed proof in our [previous post](https://decentralizedthoughts.github.io/2020-07-17-polynomial-secret-sharing-and-the-lagrange-basis/).

Weak Termination follows since the share is non-blocking and the reconstruct only needs $n-f \geq f+1$ shares.

### Note on strong termination of the share protocol

As written, the dealer may crash in the middle of sending shares and parties have no way of knowing if all non-faulty parties received their phase. So parties need to **reach agreement** on whether the dealer completed or not. In particular all the [lower bounds on agreement](https://decentralizedthoughts.github.io/2019-12-15-synchrony-uncommitted-lower-bound/) must hold.

One way to handle this is to abstract it away :-). Simply assume parties have access to **broadcast channel**. So the dealer, after sending all the shares, simply broadcasts ```OK```. If parties dont hear an OK, they know the dealer crashed and use 0 as the reconstruct value. 

In this model, the share protocol requires $O(n)$ words to be sent on private channels and $O(1)$ words of broadcast. The reconstruct protocol requires $O(n^2)$ words on private channels.

Exercise: build a share protocol that provides strong termination using $O(n^2)$ communication without a broadcast channel. 

Comments on [Twitter](https://twitter.com/ittaia/status/1559924466687397889?s=21&t=FOnqNyQ4un6Z5PKwNta_cg).
