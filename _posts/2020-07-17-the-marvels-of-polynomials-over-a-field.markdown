---
title: The Marvels of Polynomials over a Field
date: 2020-07-17 13:55:00 -04:00
tags:
- math
- cryptography
author: Ittai Abraham
---

In this series of posts, we explore the mathematical foundations of polynomials over a field. These objects are at the heart of several results in computer science: [secret sharing](/2020-07-17-polynomial-secret-sharing-and-the-lagrange-basis), [Multi Party Computation](https://eprint.iacr.org/2011/136.pdf), [Complexity](https://lance.fortnow.com/papers/files/ip.pdf), and [Zero](https://www.iacr.org/archive/asiacrypt2010/6477178/6477178.pdf) [Knowledge](https://cyber.biu.ac.il/event/the-9th-biu-winter-school-on-cryptography/) [protocols](https://eprint.iacr.org/2019/953.pdf) (and see [this post](https://decentralizedthoughts.github.io/2020-12-08-a-simple-and-succinct-zero-knowledge-proof/)).

All this wonder and more can be traced back to a very useful fact about polynomials over a field:

**Theorem: any non-trivial polynomial over a field of degree at most $d$ has at most $d$ roots**

Let's unpack this statement.
Let $K$ be a [field](https://en.wikipedia.org/wiki/Field_(mathematics)) and let $p_0,...,p_m \in K$ be *coefficients*.
A polynomial over $K$ is an element of $K[X]$. Here is an example of one:

$$
P=p_0+p_1 X + p_2 X^2 + p_3 X^3 +...+ p_{m-1} X^{m-1} + p_m X^m
$$

Recall that a field supports both multiplication and division (i.e., every non-zero element has a unique multiplicative inverse). An important property of fields is that the additive and multiplicative inverses are *unique*.  Note that the set of [polynomials](https://en.wikipedia.org/wiki/Polynomial_ring) $K[X]$ is a [ring](https://en.wikipedia.org/wiki/Ring_(mathematics)), so it supports multiplication, but not every element has a multiplicative inverse (more on division in $K[X]$ later).

A polynomial is *non-trivial* if some coefficient of it is non-zero. Then, we define the *degree* of $P$, denoted $deg(P)$, to be the maximal $i$ such that $p_i \neq 0$. Observe that $deg(P+Q)\leq \max\{deg(P),deg(Q)\}$. It is natural to define the degree of the trivial polynomial to be $- \infty$. This way $deg(P  Q) = \deg(P) + \deg(Q)$ always holds.

We say that $a \in K$ is a *root* of $P \in K[X]$ if $P(a)=0$ and say that $P$ has *at most $d$ roots* if there are at most $d$ elements in $K$ that are a root of $P$. 

For example, consider the polynomial $P=2X-4$. It is clearly a polynomial of degree one and we all know that, over the rational field $K=\mathbb{Q}$, it has just one root (at $2$).  Now, consider that same polynomial over the finite field $K=\mathbb{Z}_7$, which are just the integers modulo 7: i.e., $\\{0,1,2,\dots,6\\}$.
Then, a quick check shows that $2$ is still the only root of $P$. In other words, the equation $2X=4 \pmod 7$ has exactly one solution: $2$.

Note that if instead of a field $K=\mathbb{Z}\_7$ we chose the _ring_ $K=\mathbb{Z}_{12}$, then the equation $2X=4 \pmod {12}$ would have 2 (!) solutions: $2$ (because $2\times 2 - 4 = 0$) and $8$ (because $2\times 8 - 4 = 16 - 4 = 12$, which is equal to 0 modulo 12). In other words, $P$ has more roots (two) than its degree (one)!

## Proof

To prove the theorem, we prove an important claim:

**Claim: If $deg(P)\geq 1$ and $P(a)=0$ then there exists polynomial $Q$ such that $P=(X-a)Q$ and $deg(Q)<deg(P)$.**

The proof is by induction on $d$. 

For the base case $deg(P)=1$, denote $P(X)=p_0 + p_1 X$ with $p_1\neq 0$. Let $a= -(p_0) (p_1)^{-1}$ (this is well defined since $K$ is a field) and let $Q(X)=p_1$. Note that $Q$ is a non-trivial degree zero polynomial. It is easy to check that indeed $(X-a) Q = p_1 X + p_0 = P$.

For the general case $deg(P)=d>1$, denote $P(X)=p_0 + \dots+ p_d X^d$.

Define 

$$
P' = P - p_d X^{d-1} (X-a),
$$

note that $p_d$ is the largest coefficient of $P$. Lets make a few observations about $P'$:

1. The degree of $P'$ is smaller than $d$. This is because the $d$th coefficient of $p_d X^{d-1} (X-a)$ equals $p_d$, so it will cancel out.
2. $a$ is a root of $P'$. This is because $P(a)=0$ and because $p_d X^{d-1} (X-a)$ also has a root at $a$.

Hence, we can apply the induction hypothesis on $P'$ to obtain that there exists $Q'$ such that $P'=(X-a)Q'$ and $deg(Q') < d-1$.

Since:

$$
P =P'+ p_d X^{d-1} (X-a)
$$

Then, we can substitute $P'=(X-a)Q'$ and get:

$$
P= (X-a)Q' + (X-a) p_d X^{d-1}
$$

Hence, we have proved that:

$$
P = (X-a)Q\ \text{with}\ Q=Q'+ p_d X^{d-1}
$$

Since $deg(Q) \leq \max \{ deg(Q'), deg(p_d X^{d-1})\}$ then $Q$ has degree at most $d-1$. This completes the proof of the claim.

### Proof of the Theorem from the claim

The proof is by induction on $d=deg(P)$. 

For $d=0$, since $P$ is non-trivial, we have $p_0 \neq 0$ and hence $P$ has no roots (as it should be).

For $d=1$, we use the fact that $K$ is a field. The unique root of $P=p_0+p_1 X$ (for $p_1 \neq 0$) is the *unique* element $-p_0/p_1 = -(p_0) (p_1)^{-1}$. This follows from the uniqueness of the inverse for both addition and multiplication in a field (if $K$ were just a ring and not a field (e.g., $K=\mathbb{Z}_{12}$), then the inverse of $p_1$ may not exist or, more worrisome, may not be unique!).

For $d\geq 2$, we use an induction step. There are two cases:

If $P$ has no roots, then we are done.

Otherwise, let $a \in K$ be such that $P(a)=0$. Using the claim above, there exists a polynomial $Q$ of degree $<d$ such that $P=(X-a) Q$. Since $deg(Q)<d$ we use the induction hypothesis on $Q$. So $P$ can have at most $d-1$ roots from $Q$ and at most one more root (at $a$) from the degree one polynomial $(X-a)$.

### Discussion

In the next posts, we will use this very useful fact about roots of polynomials over finite fields.
First, we will use it as the foundation for [secret sharing](/2020-07-17-polynomial-secret-sharing-and-the-lagrange-basis).
We also use it as the foundation for [succinct proofs and zero knowledge proofs](https://decentralizedthoughts.github.io/2020-12-08-a-simple-and-succinct-zero-knowledge-proof/).

A significantly more general result about polynomials over a field views them as a special case of a [unique factorization domain](https://en.wikipedia.org/wiki/Unique_factorization_domain). This view exposes deep connections between the natural numbers, polynomials over a field, and the [fundamental theorem of Arithmetic](https://www.maths.tcd.ie/pub/Maths/Courseware/Primality/Primality.pdf).  

**Acknowledgment.** Thanks to [Alin](https://research.vmware.com/researchers/alin-tomescu) for helpful feedback on this post.

Please leave comments on [Twitter](https://twitter.com/ittaia/status/1283904819019886592).



