---
title: 'Private Set Intersection #2'
date: 2020-07-26 19:00:00 -04:00
tags:
- cryptography
layout: post
author: Avishay Yanai
---

In the [first post on Private Set Intersection](https://decentralizedthoughts.github.io/2020-03-29-private-set-intersection-a-soft-introduction/), I presented the problem of Private Set Intersection, its applications and the simple protocol of [[KMRS14]](https://fc14.ifca.ai/papers/fc14_submission_52.pdf), that allows Alice and Bob to learn the intersection of their sets with the aid of an untrusted third party Steve who is assumed to not collude with Alice or with Bob.

The main challenge in that protocol was to make sure that the 3rd party, Steve, does not cheat.
In this post, I will present another, more recent protocol, proposed by Phi Hung Le, Samuel Ranellucci, and Dov Gordon [[LRG19]](https://eprint.iacr.org/2019/1338.pdf). They tackle the challenge from a different angle, which is somewhat more elegant, but could be quite expensive in some cases.

I will now re-iterate the problem statement and then present a simple protocol that works when the parties are assumed to be [semi-honest]((https://decentralizedthoughts.github.io/2019-06-07-modeling-the-adversary/)). Then I'll move to the description of detecting a cheating Steve according to [[LRG19]](https://eprint.iacr.org/2019/1338.pdf). For more introduction to Private Set Intersection please read the [first post](https://decentralizedthoughts.github.io/2020-03-29-private-set-intersection-a-soft-introduction/).

## The problem
Recall the problem of Private Set Intersection:
There are two friends Alice and Bob. Alice has a set of items $A=(a_1,\ldots, a_n)$ and Bob has a set of items $B=(b_1,\ldots,b_m)$.
They wish to learn the intersection $A\cap B$ such that Alice will not learn anything about items $b’\in B$ that are not in the intersection (and same for Bob). To do that, they are willing to use the service of a 3rd party Steve, but they do not trust him to follow the protocol faithfully. So they have to verify whatever Steve claims. If any deviation from the protocol is detected (by either of the parties) then the protocol aborts.

We note that the sets sizes $n$ and $m$ are public, so there is no effort to hide them in the protocol.


## A simple protocol
Let's begin with a slightly different goal, in which Alice and Bob are not interested in the intersection $A\cap B$ itself, but rather they are interested just in its size $|A\cap B|$. This problem is called _Private Set Intersection Cardinality (PSI-CA)_.

Let’s also relax the setting and suppose that Alice and Bob do not want Steve to learn their items but they _do_ trust him to return the correct result $|A\cap B|$ (formally we assume that Steve is also semi-honest).
The protocol:

1. Alice has $A={a_1,\ldots,a_n}$ and Bob has $B={b_1,\ldots,b_m}$.
2. All parties agree on a [PRF](https://crypto.stanford.edu/pbc/notes/crypto/prf.html) $F$.
3. Alice and Bob agree on a secret key $k$ (which remains secret from Steve).
4. Alice sends $A’={a’_1,\ldots,a’_n}$ to Steve where $a’_i=F(k,a_i)$.
5. Bob sends $B’={b’_1,\ldots, b’_m}$ to Steve where $b’_i=F(k,b_i)$.
6. Steve computes $z=\|A’ \cap B’\|$ and sends $z$ to Alice and Bob.

Obviously, since $F$ is deterministic the result $z$ is the correct intersection cardinality, i.e. $\|A\cap B\| = \|A’ \cap B’\|$. The privacy of Alice and Bob is preserved since Steve does not know the secret key $k$ and therefore he cannot distinguish $a’_i$’s and $b’_i$’s from random.


### What if Steve cheats?

Steve can send a value of $z$ that is different than the intersection cardinality.
To prevent this attack, we force Steve to prove to Alice and Bob that $z=\|A\cap B\|$. The proof is broken into two parts:
1. Steve proves that $z \leq \|A cup B\|$. Namely, that $z$ is a _lower bound on the union_ of $A$ and $B$. This is equivalent to $z$ being an _upper bound on the intersection_ of $A$ and $B$, i.e. $z \geq \|A \cap B\|$.
2. Steve proves that $z \leq \|A \cap B\|$.

With these two proofs, Alice and Bob are convinced that $z \geq \|A \cap B\|$ and $z \leq \|A \cap B\|$ and therefore it follows that $z = \|A \cap B\|$.

Before describing the proofs, we briefly cover the necessary details about two secret sharing schemes.

## Two secret sharing schemes
Recall that there are two types of cryptographic secret sharing schemes: [Shamir Secret Sharing](https://decentralizedthoughts.github.io/2020-07-17-polynomial-secret-sharing-and-the-lagrange-basis/) and Additive Secret Sharing:

-In [Shamir Secret Sharing](https://en.wikipedia.org/wiki/Shamir%27s_Secret_Sharing) a dealer with a secret $s \in \mathbb{F}$, where $\mathbb{F}$ is a finite field, picks a polynomial $p(\cdot)$ of degree $d$. That is, the polynomial $p(x)=p_0 + p_1x+ p_2x^2+\ldots + p_dx^d$ such that $p_1,\ldots,p_d$ are chosen uniformly from the field and $p_0=s$. Then, the dealer can produce many shares of $s$ (up to $\|\mathbb{F}\|-1$ distinct shares) such that the point $(e, p(e))$ is a share, for some $e \in \mathbb{F}$.
Obviously, if someone can get $d+1$ distinct shares, it can [interpolate](https://en.wikipedia.org/wiki/Lagrange_polynomial) the polynomial $p(\dot)$ and find the secret by evaluating $s=p(0)$.
On the other hand, if someone obtains only $d$ or less shares then it learns nothing about the secret (that is, given the shares obtained, for every pair $s_1$ and $s_2$, the probability that $p(0)=s_1$ equals the probability that $p(0)=s_2$). This type of secret sharing is sufficient for the first proof.

-In [Additive Secret Sharing](https://en.wikipedia.org/wiki/Secret_sharing#Trivial_secret_sharing) a dealer with a secret $s \in \mathbb{F}$ wants to break $s$ to $N$ pieces $s_1,\ldots, s_N$ such that $s=s_1+\ldots,s_N$ (where addition is taken over the field $\mathbb{F})$. The first $N-1$ pieces are chosen uniformly from the field and the last piece is computed by $s_N=s-(s_1+\ldots+s_{N-1})$. Each of the $N$ pieces is a share.
Obviously, if someone has less than $N$ shares it learns nothing about $s$ because these are just random values from the field. But one who gets all $N$ shares can clearly obtain $s$ by summing up all of them. In the second proof below Alice and Bob will use Additive Secret Sharing with $N=2$ such that both Alice and Bob know the secret, they produce the two shares only for items that are in the intersection, so Steve would be able to get two shares of a secret exactly $\|A \cap B\|$ number of times.


## First proof: $z\geq \|A \cap B\|$

Instead of proving that $z$ is an upper bound on the intersection, Steve proves that $z’=n+m-z$ is a  lower bound on the union. 
The following steps are added after the simple protocol described above (i.e. Steve already notified Alice and Bob about the intersection $z$ he found):

 7) Alice and Bob choose a secret value, $s$, from the field and also choose a random polynomial $p(\cdot)$ of degree $z’-1$ by which they will produce Shamir shares. That is, $p(x)=s+p_1x+\ldots + p_{z’-1}x^{z’-1}$.

 8) Recall that  $A’=(a’_1,\ldots,a’_n)$ is the set that Alice sent in step 4 above, Alice now sends to Steve $n$ shares: the point $(a’_i, p(a’_i))$ for every $a’_i \in A’$. Call this set of points $V$.

 9) Recall that  $B’=(b’_1,\ldots,b’_m)$ is the set that Bob sent in step 5 above, Bob now sends to Steve $m$ shares: the point $(b’_i, p(b’_i))$ for every $b’_i \in B’$. Call this set of points $W$.

The goal of Steve in the proof is to convince Alice and Bob that there are at least $z’$ values in the union of $A$ and $B$, which is equivalent to having at least $z’$ distinct shares of the secret $s$ sent to Steve from Alice and Bob together. And if there are $z’$ distinct shares of $s$ it means that Steve can find $s$ (by polynomial interpolation), so Steve concludes the proof by sending $s$ to Alice and Bob. Formally:

 10) Steve uses the points in $V \cup W$ to interpolate a $z’-1$ degree polynomial $p(\cdot)$ and evaluate $s=p(0)$. Steve sends $s$ to Alice and Bob.

By now, Alice and Bob should be convinced that the size of the union $A \cup B$ is at least $z’$, meaning that the size of the intersection $A\cap B$ is at most $z=n+m-z’$.
Otherwise, if the size of the union was less than $z'$ then Steve could not obtain $z'$ distinct points on $p$.

With only this proof, it is possible for Steve to cheat and claim that the intersection is larger, i.e. $z+c$ instead of $z$, or equivalently claim that the lower bound on the union is smaller, i.e. $z’-c$ instead of $z’$. Note that Steve has enough points for doing so (that is, more than $z’-c$ points for interpolating $p$, in fact, it has $z’$ points). In order to force Steve to not cheat, by which to set $c=0$, Alice and Bob wait for his second proof.

Note that I omit from the description above the measures taken by Steve to ensure that Alice and Bob do not cheat by sending wrong shares (points) in $V$ and $W$. Without such a precaution, a corrupt Alice, for instance, could learn whether Bob has a specific item, which is not allowed (Alice and Bob should learn only the cardinality and nothing else).

## Second proof: $z\leq \|A \cap B\|$

This proof works almost the same as the first one with a simple twist. Let’s first realize why using the proof described above in order to prove $z\leq \|A \cap B\|$ is problematic. In such a proof Alice and Bob agree on a secret $s$ and on a degree $z-1$ polynomial $p(x)=s+p_1x+\ldots p_{z-1}x^{z-1}$ and send Steve the shares $V$ and $W$ as before. Now, it is clear that Bob has enough points in order to interpolate $p$ and find the secret $s=p(0)$, because the degree $z-1$ is either equal to or smaller than $n$ and Steve has at least $n$ distinct shares of $s$ (given from Alice in the set $V$). Therefore, finding the secret $s$ in this case would not convince Alice or Bob that the intersection cardinality is indeed $z$. It could be smaller.
So how can we design a proof system in which Steve could find the secret $s=p(0)$ only if the intersection cardinality is indeed $z$?

The idea is to send Steve shares of shares!
Instead of sending to Steve sets of shares of $s$ (i.e. the set of points $V$ and $W$), for each such a point $(x, p(x))$ Alice and Bob will maintain an Additive Sharing with two shares, such that Alice will send the point $(x, p(x)_A)$ and Bob will send the point $(x,p(x)_B)$ where $p(x)_A$ and $p(x)_B$ are Additive shares of $p(x)$. That is, $p(x)_A + p(x)_B = p(x)$.

So let’s say that $q=a_i=b_j$, then Alice and Bob send to Steve the value $q’=F(k,q)$ in their sets $A’$ and $B’$, as described in steps 4-5 above. Then, after Alice and Bob given the claimed intersection cardinality $z$ from Steve and chosen a secret $s$ and a $z-1$ degree polynomial $p$, they send two shares of $p(q’)$: Alice sends the point $(q’, r_q)$ and Bob sends the point $(q’, p(q)\oplus r_q)$ where $r_q$ is a pseudo random value that depends on $q$ (i.e. $r_q=F(k’, q)$ for some secret key $k’$ known to Alice and Bob but not to Steve). In this case, Steve has both shares relevant to $q'$, so it can compute $p(q')$ by $r_q \oplus (p(q')\oplus r_q)$ and use the point $(q',p(q'))$ when interpolating the polynomial $p$.

For any other item $a$ of Alice which is not in the intersection, Steve will have the point $(a’, r_a)$ from Alice, but not the point $(a’, p(a’)\oplus r_a)$ from Bob, therefore, it could not obtain the point $p(a’)$ so it does not help him interpolating the polynomial $p$.

From the above, it follows that Steve will have at most $\|A\cap B\|$ values for which it can obtain points on the polynomial $p$ which would be sufficient to interpolate $p$ and learn the secret $s$. So if Steve cheats and claims that $z$ is larger than $\|A\cap B\|$, it will not be able to find enough points on $p$ and so could not find $s$.


## How to output the intersection itself? (and not only the cardinality)

In the above we were interested in finding the _cardinality_ of the two sets, but what if Alice and Bob do actually want to know the _intersection itself_?

It is easier for Steve to convince Alice and Bob that the intersection has at least $z$ items by simply sending them the set $C’=A’ \cap B’$. Now Alice and Bob compute $q=F^{-1}(k, q’)$ for every $q\in C’$ and verify that $q\in A$ and $q\in B$, if it is not then they raise a flag which means that someone cheated (either the one who raised the flag or Steve, we do not know) and the protocol aborts.

Suppose that the above step went through, then Alice and Bob are convinced that there are at least $\|C'\|$ values in the intersection, but how can they be sure that there are no more items? That is, how can they be convinced that Steve did not omit anything from $A'\cap B'$? 
In [KMRS14] (see the previous post) this was proven by adding dummy items to $A$ and $B$. In [LRG19], however, the parties simply follow the first proof described above, which completes the protocol.


## Limitation of the protocol

Suppose that $n=m$.
The two proofs described above would be computationally expensive when the sizes of the sets, $n$, is very large (i.e. one million items). This is because in the proofs Alice and Bob have to evaluate a polynomial of degree $z$ or $z’=2n-z$ for $n$ times in order to produce the shares (points) needed to be sent to Steve. This task would cost them $O(n \log^2 n)$ using a [DFT-based algorithm for batch polynomial evaluation](https://github.com/AvishayYanay/FastPolynomial).

We stress that the usual way to tackle such problems is to map the items into bins before running the protocol and then to run the protocol for each bin separately and leverage the fact that each bin contains much fewer items. That is, Alice and Bob choose a hash function $H$,  then Alice maps an item $a\in A$ to bin number $H(a)$ and Bob maps an item $b\in B$ to bin number $H(b)$. If Alice and Bob have the same item then this item would be mapped to the same bin by both of them, meaning that we can run the above protocol per bin rather than over all the items.

If there are $n/\log n$ bins then we expect each bin to have $O(\log n)$ items and so the communication of the proofs becomes $O(n \log\log^2 n)$. However, such a protocol would reveal much more information than required. Specifically, it would reveal the cardinality of the intersection of many subsets of items rather than a single cardinality of the intersection of all items. Therefore, that type of optimization is not allowed in this protocol.


## Concluding 

This was the second post on _PSI with the aid of a 3rd untrusted party_. In the next posts, I will cover more settings: How can Alice and Bob obtain the intersection (or the intersection cardinality) without the aid of any 3rd party? How can a set of more than 2 parties obtain the intersection of their sets?
