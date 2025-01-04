---
title: Dining Cryptographers and the additivity of polynomial secret sharing
date: 2022-08-25 08:00:00 -04:00
tags:
- cryptography
- secret sharing
author: Ittai Abraham
---

David Chaum’s [dining cryptographer problem](https://en.wikipedia.org/wiki/Dining_cryptographers_problem) is a pioneering work on the foundations of privacy. It shows the amazing power of information-theoretic Secure Multi Party Computation. The [original paper](https://users.ece.cmu.edu/~adrian/731-sp04/readings/dcnets.html) from 1988 is super accessible and fun to read. Many systems in the last 20 years for anonymity and privacy-preserving communication are based on the Dining Cryptographers problem. [Herbivore](https://www.cs.cornell.edu/people/egs/herbivore/documentation.html), [Dissent](https://dedis.cs.yale.edu/dissent/), [Riposte](https://arxiv.org/pdf/1503.06115.pdf), [Blinder](https://eprint.iacr.org/2020/248.pdf), and many others.

Here is a modern version of the story:

> $n$ cryptographers get together and decide to order dinner online. The delivery person arrives with the food and says that the bill was paid *anonymously* and promises that: *the payer is either one of the cryptographers or the [NSA](https://www.nsa.gov)*.
> The cryptographers want to respect the anonymity of the bill payer, if it is one of the cryptographers - but they do want to learn **one bit**: is the payer the NSA or one of the cryptographers?

Importantly, in case it's one of the cryptographers, they don't want to reveal who it is!

Chaum’s protocol uses [additive secret sharing](https://www1.cs.columbia.edu/~tal/4261/F19/secretsharingf19.pdf) which we will cover in later posts. Here we adapt Chaum’s protocol to use [polynomial secret sharing](https://decentralizedthoughts.github.io/2020-07-17-polynomial-secret-sharing-and-the-lagrange-basis/) of our previous post. 

There are $n$ parties (cryptographers) and while being **honest**, the cryptographers are naturally **curious**. Formally, we assume a [passive](https://decentralizedthoughts.github.io/2019-06-07-modeling-the-adversary/) (aka honest-but-curious) adversary controlling $f<n$ parties. Communication is lock-step (synchrony).

Fixing a finite field larger than $n$, for a secret $\alpha$, let $p(x)$ be a *polynomial secret sharing* of $\alpha$, which has degree at most $n-1$ such that $p(0)=\alpha$ and all the remaining $n-1$ coefficients are chosen uniformly at random.

Let $\ell_1,\dots,\ell_n$ be the Lagrange coefficients such that for any $p(1)=v_1,\dots,p(n)=v_n$ of a degree at most $n-1$ polynomial $p$:

$$
p(0)= \sum_{1 \leq i \leq n} \ell_i v_i
$$

Recall these interpolation coefficients are [fixed](https://decentralizedthoughts.github.io/2020-07-17-polynomial-secret-sharing-and-the-lagrange-basis/) for all polynomials of a fixed degree. Just to re-emphasize: the $\mathbf{n}$ cryptographers use degree at most $\mathbf{n{-}1}$ polynomials.


The cryptographers run the following two round protocol:
```
Each party i has an input s_i: either 0 or 1
Global promise: at most one party has input 1

Party i:

Round 1:
Randomly choose a_1,…,a_{n-1}
Let p_i(x)=s_i + sum_{1<=j<n} (a_j x^j)
For each j, send p_i(j) to party j

Round 2:
Given shares p_1(i),…,p_n(i)
Let v_i = p_1(i)+,…,+p_n(i)
Send v_i to all parties

End of round 2:
Given shares v_1,…,v_n
Output (l_1 * v_1)+…+(l_n * v_n)
Where l_i are the Lagrange coefficients of eqn (1) above
```

The protocol is conceptually very simple: each cryptographer shares its secret bit using polynomial secret sharing, then parties reconstruct the *sum* of the shares.

Miraculously, in this protocol each party outputs the sum of the bits: $0$ if the NSA paid and $1$ if one of the cryptographers paid. Even more miraculously, no subset of cryptographers learn any additional information other than what they can learn from this single bit!

In particular, any subset of $f$ non-paying cryptographers has no information on which one of the remaining $n-f$ cryptographers is the one that paid.

How do we define this property formally? How do we prove it's correct?

Not surprisingly, we will use the [Validity and Hiding](https://decentralizedthoughts.github.io/2020-07-17-polynomial-secret-sharing-and-the-lagrange-basis/) properties of polynomial secret sharing, and use a powerful observation - that polynomial secret sharing is **additive**.

### Proof of Validity - the power of additivity

We would like to say that the output of this protocol is the same as an ideal functionality that takes the inputs from all the parties $s_1,\dots,s_n$ and outputs the sum $s= \sum s_i$.

This follows from the additive nature of polynomial secret sharing. The one-to-one mapping $F(p_0, \dots,p_{n-1})=p(1),\dots, p(n)$ between the $n$ coefficients of a degree $n-1$ polynomial and its $n$ point evaluation is also an *isomorphism with regard to addition*: $F( \vec{p} )+F( \vec{q} ) = F(p_0+q_0, \dots, p_{n-1}+q_{n-1})= p(1)+q(1), \dots, p(n)+q(n)$. This follows almost immediately from the additivity of polynomials over a field. 

### Proof of Hiding - the adversary learns nothing other than the output of the ideal functionality

Clearly, the adversary learns $s=s_1+\dots,s_n$, so the non-trivial case is when  $f \leq n-2$ because for $f=n-1$, once $s$ is revealed, the adversary knows exactly who payed (even in the ideal world).

For any $f\leq n-2$ we would like to say that the adversary controlling any subset $F \subset N= \lbrace 1,\dots,n \rbrace$ with $\|F\|=f$ learns nothing other than the sum $s$. Formally, for *any* $\lbrace s_i \rbrace_{i \in N \setminus F}$, other than the value of the sum $s$, the distribution of the view of the adversary is uniformly random.

For the first round, this follows directly from the Hiding property for any $f<n$ parties of each of the polynomial secret sharing. 

For the second round, the adversary learns $v_1,\dots,v_n$, which corresponds to the polynomial $p=p_1+\dots+p_n$. We again use the isomorphism of addition: for any choice of $\lbrace p_i \rbrace_{i \in F}$ for an adversary controlling the parties in $F$, while the first coefficient of $p$ is $s$, the remaining $n-1$ coefficients of $p$ are uniformly random. This follows because adding a uniformly random value to any known value results in a uniformly random value. Hence round 2 is identical to a secret sharing of $s$ via a uniformly random polynomial $p$ by an honest dealer.

### What else can we do with the additivity of polynomial secret sharing?

#### Unpredictable randomness

One of the main uses of additivity of polynomial secret sharing is for generating **unpredictable randomness**. By adding $f+1$ secret sharings of *uniformly random secrets*, we can guarantee that the adversary cannot predict the sum!

This idea is a key ingredient to many [Distributed Key Generation protocols](https://arxiv.org/pdf/2102.09041.pdf), efficient [Randomized Consensus protocols](https://eprint.iacr.org/2006/065.pdf), and the core of [Secure Multi Party Computation](https://eprint.iacr.org/2011/136.pdf).


#### Degree reduction for MPC

As we will see in later posts, additivity and the linearity of interpolation are the key enablers for building interactive MPC multiplication protocols from addition protocols - once addition and multiplication are both possible, the sky is the limit.

While addition is possible, multiplication has the annoying property that the degree of the secret increases. The solution is to run a *degree reduction* protocol after each multiplication gate. The degree reduction is simply a protocol that uses the additively of polynomials to compute a linear combination using the Lagrange coefficients. So given a secret shared polynomial of degree $2f$, each party can share its share as a polynomial of degree $f$ and the linear combination (using the degree $2f$ Lagrange coefficients) produces a degree $f$ polynomial that shares the same secret as the original degree $2f$ one! 

### Notes

There are many things one may wish to improve on this basic scheme. Can we handle malicious cryptographers? Can we handle asynchrony in communication? What about denial of service? Can we scale to thousands or even millions of cryptographers? Can cryptographic protocols (signatures, zero knowledge proofs, etc) improve the performance and complexity?  Many of the papers mentioned above have made significant advances on these challenges. We will cover some of this in future posts.

#### Acknowledgements

Many thanks to [Thor Kamphefner](https://thork.net) for insightful comments and suggestions. 


Your thoughts on [Twitter](https://twitter.com/ittaia/status/1562777337753587712?s=21&t=dilr4XTgVUq0e5Q-10sRtg)