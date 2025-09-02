---
title: A Simple and Succinct Zero Knowledge Proof
date: 2020-12-08 13:37:00 -05:00
tags:
- cryptography
author: Ittai Abraham, Alin Tomescu
---

There is a popular belief that **succinct proofs** and **zero-knowledge proofs** are a type of [moon math](https://medium.com/@VitalikButerin/quadratic-arithmetic-programs-from-zero-to-hero-f6d558cea649). In this post, our goal is to present a simple proof system that can provide an introduction and intuition to this space. Perhaps surprisingly, the only tool we will use is the [Theorem](/2020-07-17-the-marvels-of-polynomials-over-a-field) that non-trivial degree-at-most-$d$ polynomials over a field have at most $d$ roots.

### Start with Succinctness, add Zero Knowledge later
Traditional Computer Science Curriculum typically starts with a zero knowledge scheme based on proving [3-colorability of a graph](https://crypto.stanford.edu/cs355/18sp/lec3.pdf) ([MIT demo](http://web.mit.edu/~ezyang/Public/graph/svg.html) or [Vipul Goyal](https://www.cs.cmu.edu/~goyal/s18/15503/scribe_notes/lecture23.pdf)), or on proving the existence of a Hamiltonian cycle (see [Boaz Barak](https://www.boazbarak.org/cs127spring16/chap14_zero_knowledge.html), or [Sanjam Garg](https://people.eecs.berkeley.edu/~sanjamg/classes/cs294-spring16/scribes/7.pdf)). The wonderful [9th BIU Winter School on Cryptography and Zero Knowledge](https://cyber.biu.ac.il/event/the-9th-biu-winter-school-on-cryptography/) also takes a similar approach.

The advantage of this approach is that it immediately gives very general Zero Knowledge results via [Karp-based reductions](https://en.wikipedia.org/wiki/Polynomial-time_reduction) to any problem in NP. 
This is because Colorability, Hamiltonicity and Satisfiability are all [NP-complete](https://en.wikipedia.org/wiki/NP-completeness) problems.

Succinct proofs (and *arguments*, but will ignore the distinction here) are often taught at a [later phase](https://crypto.stanford.edu/cs355/19sp/lec17.pdf) and in connection to the [PCP](https://en.wikipedia.org/wiki/PCP_theorem) theorem. Alessandro Chiesa's course on [Foundations of Probabilistic Proofs](https://people.eecs.berkeley.edu/~alexch/classes/CS294-F2020.html) is a great resource.


In this post, we take a different approach whose goal is to provide a simple and self-contained construction that can provide intuition for many of the constructions that are used in practice.
We start with a seemingly useless problem, one that is not NP-complete (in fact, solvable in polynomial time). We provide a solution in a non-standard *virtual cloud* communication model. Perhaps surprisingly, we will show in later posts that this simple problem is the basis of more general results in this area.


### The setting
We will assume two parties: a *Prover*, and a *Verifier*. 

The Prover has an input $S=\langle s_0,\dots,s_{d-1}\rangle$ which is a vector of say $d=10^{10}$ field elements (for each $i$, $s_i \in \mathbb{F}_p$). It will be important to assume that $p$ is large relative to $d$ (say $p \approx 2^{256}$). All the Prover wants to do is prove to the Verifier this simple *boolean* fact:
> Is $S$ the all-zero vector or not?

We will assume the only way the Prover and Verifier can interact is via a special communication channel we will call the *virtual cloud*:
1. The Prover has to *commit* to its input $S$ by uploading a polynomial $g(x)$ such that
  * $g(x)$ is of degree at most $d-1$. 
  * for all $0\leq i \leq d-1$ we have $g(i) = s_i$.
  * The prover creates $g$ via [Lagrange interpolation](https://decentralizedthoughts.github.io/2020-07-17-polynomial-secret-sharing-and-the-lagrange-basis/) of $S$:
$g(x) = \sum\_{i\in[0,d-1]} s\_i \prod\_{j\in[0, d-1], j\ne i} \frac{x - j}{i - j}$

2. The Verifier is allowed to *query* the virtual cloud by sending it an element $r$ and the virtual cloud responds back with $g(r)$, the evaluation of $r$ on $g$.


### A non-succinct solution, with no error
How can the Verifier be *sure* that $S$ is all-zero and hence $g$ is the zero (trivial) polynomial? 

When $S$ is all-zero then $g$ is the (trivial) zero polynomial. But if $S$ is not all-zero then the [fundamental theorem of arithmetic adapted to finite field polynomials](https://decentralizedthoughts.github.io/2020-07-17-the-marvels-of-polynomials-over-a-field/) says that $g$ has at most $d-1$ roots. So the verifier has a way to distinguish: it can query $d=10^{10}$ distinct points and check if they are all zero.

This solution is not succinct as it requires the Verifier to send $d$ queries. Can the Verifier use fewer queries? Can the Verifier query just one point?

### A succinct solution, with small error
We will now use the fact that we are working over the field $\mathbb{F}_p$ where $p\gg d$. By now, it should be quite clear how the Verifier can get a succinct proof that $S$ is all-zero or not.

> The Verifier chooses a uniformly random element $r \in_R \mathbb{F}_p$ and queries the virtual cloud just once with $r$:

1. If $g(r) \neq 0$, then $g$ is not the trivial polynomial, so $S$ is not all-zeros.
2. What if $g(r)=0$? Then, we use the [Theorem](/2020-07-17-the-marvels-of-polynomials-over-a-field) that, if $g$ is non-zero, then it has at most $d-1$ roots to say: If $r\in_R \mathbb{F_p}$ and $g(r)=0$, then the probability that $g$ is non-zero is at most $(d-1)/p$ (where $p$ is the size of the field).

We can choose $p\gg d$, so the error probability is as low as we want. If $g(r)=0$, then the Verifier declares that $S$ is all-zero.

That's it! This is a very succinct proof: instead of querying $d=10^{10}$ points, the Verifier can succinctly query just one (local) point and learn about a (global) property $S$ (with a small error probability).

At the core of this succinct proof is the power of randomization: by accepting a small probability of error, it is possible to prove $g(r) \neq 0$ using one query instead of $d$ queries. Quite remarkably, this mathematical fact can be boosted to much more general succinct proofs (with small error).

### Adding Zero Knowledge

The Prover managed to prove that $S$ is not zero using a succinct proof. Clearly, if $g=0$ then we know everything about $S$. However, when $g\neq 0$, what if we would also want the Verifier to learn nothing about $S$ other than that it's not all-zero?

The Verifier can query for some $0 \leq i \leq d-1$, receive back $g(i)=s_i$, and hence learn some $s_i \in S$, so the first thing we need to do is restrict the Verifier to query a random element $r$ that is outside of $\\{0,\dots,d-1\\}$.

Even that may leak information, for example, for $d=2$, the vector $S$ is of size $2$ and $g$ is a degree one polynomial (such that $g(0)=s_0$ and $g(1)=s_1)$. If the Verifier queries, say $r=10$, it learns the value of $g(10)$. Since $g$ has degree 1, the Verifier has learned some linear relation between $s_0$ and $s_1$! As a concrete example, if $g(10)=1$ then the Verifier has learned that it cannot be the case that $s_0=1$ and $s_1 \neq 1$.

To make sure the adversary can learn nothing about $S$, the Prover extends its vector $S$ with one more field element $t$. Given $S$, let $S'=\langle s_0,\dots,s_{d-1}, t\rangle $ be the extended vector. If $S$ is the all-zero vector, then the Prover sets $t=0$. Otherwise, the Prover chooses $t$ uniformly at random. So instead of the polynomial $g$ of degree $d-1$, the Prover now commits to a polynomial $g'$ of degree $d$ such that for all $0\leq i \leq d-1$, $g'(i)=s_i$ and $g'(d)=t$. Using an argument that is similar to the one in [our secret sharing post](/2020-07-17-polynomial-secret-sharing-and-the-lagrange-basis), it can be seen that for any non-zero vector $S$, given a uniformly distributed $t$ in $\mathbb{F}_p$, the Verifier's view, $g'(r)$, for any $r>d$, is uniformly distributed in $\mathbb{F}_p$. Hence the only information the Verifier gains from the protocol, the Verifier could have simulated locally without any interaction. So the Verifier gains no information at all.

In our example above, for $|S|=2$, $g'$ will now be a degree two polynomial, such that $g'(0)=s_0, g'(1)=s_1, g'(2)=t$ where $t$ is uniform.
Since for any $s_0$ and $s_1$, and for any $r>2$, the distribution of $g'(r)$ is uniform, the Verifier learns nothing about $S$.

The Verifier queries a random point $r$ uniformly in $[d+1,p-1]$. If $g(r) \neq 0$ then the Verifier has a proof that $S$ is not the all-zero vector. If $g(r)=0$ then the Verifier has a proof that $S$ is most likely the all-zero vector. The probability of error is at most $d/(p-(d+1))$ (if $S$ is not the all zero-vector, then $g'$ has at most $d$ roots and the Verifier samples $r$ uniformly from $p-(d+1)$ elements).

We have shown how the Verifier obtains a succinct zero-knowledge proof!

### Removing the strange virtual cloud communication channel

A major complaint against this scheme is the strange communication mechanism.
1. First, it required the Prover to upload the polynomial $g$. This naively seems to be a non-succinct operation and requires some trusted cloud to store a lot of information. Luckily, we will show in a later post how cryptographic tools can implement this succinctly over a standard communication channel.
2. Secondly, it required the virtual cloud to respond to a query $r$ with the value $g(r)$. This may seem to require a trusted computing cloud. Luckily, again, we will show in a later post how cryptographic tools can implement this functionality over a standard communication channel.
3. Finally, recall that we needed $d\ll p$. There is sometimes a challenge in forcing the Prover to use a degree-at-most-$d$ polynomial and not one of higher degree. Again we will see techniques in later posts to force the Prover to use a low degree polynomial.

### Acknowledgments
We thank [Radu Grigore](http://rgrig.appspot.com/) for pointing out typos and helping improve this post.


Please answer/discuss/comment/ask on [Twitter](https://twitter.com/ittaia/status/1336363509492424704?s=20).
