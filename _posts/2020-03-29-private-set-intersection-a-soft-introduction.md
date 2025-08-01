---
title: Private Set Intersection
date: 2020-03-29 14:00:00 -04:00
tags:
- cryptography
layout: post
author: Avishay Yanai
---

Private Set Intersection (PSI) is a problem within the broader field of [secure computation](https://en.wikipedia.org/wiki/Secure_multi-party_computation).


## The PSI problem

There are two friends Alice and Bob such that Alice has a set of items $A=(a_1,\ldots,a_n)$ and Bob has the set $B=(b_1,\ldots,b_n)$.

_The goal is to design a protocol by which Alice and Bob obtain the intersection $A\cap B$_, under the following privacy restriction: The protocol must not reveal anything about items that are not in the intersection.

If $a_i\notin B$ then Bob learns nothing about it. In other words, Bob's apriori knowledge about whether Alice has item $z$, where $z$ is not in the intersection, is not affected by the execution of the protocol.

For example, the following solution is not private: Alice sends $A$ to Bob, Bob computes $A\cap B$ and sends the result to Alice. This is not private because Bob learns that Alice has item $a_j$ even if $a_j\notin A\cap B$.

Another problematic solution would be: Alice and Bob agree on some cryptographic hash function $H$. Alice computes $\hat A=H(a_1),\ldots,H(a_n)$ and Bob computes $\hat B=H(b_1),\ldots,H(b_n)$. In addition, for each $b_i$ Bob stores the entry $D_B[H(b_i)]=b_i$ in a dictionary $D_B$. Then, Alice sends $\hat A$ to Bob, who computes $\hat A \cap \hat B$. For every item $c\in \hat A \cap \hat B$ Bob outputs $D_B[c]$ as the intersection.

In general this is not a private solution since if the items of the parties are from a small space (e.g. phone numbers and SSN) then Bob may launch a brute force attack to learn all of Alice's items. Specifically, if the space of all possible items is $S$ and it is of size $N$, then Bob can compute $\hat S=H(s_1),\ldots,H(s_N)$ and store $D_B[H(s_i)]=s_i$ for every $i=1,\ldots,N$. Then, for every item $\hat a_i\in \hat A$ that Bob receives from Alice it computes $D_B[\hat a_i]$ to learn $a_i$. That is, Bob learns all Alice's items, regardless of whether they are in the intersection or not.

### Is PSI an important problem?

The answer is yes, it finds applications in many areas.

**An example**.
Suppose you sequenced your DNA and obtained a set of genes $A=a_1,\ldots,a_n$. You want to find the risk of having a complex disease in the future. To this end, you use the service of a research institute, which found a set of genes, $B=b_1,\ldots,b_m$, that increase the risk for complex diseases. Say that having the gene $b_i$ in your sequence increases the risk by a constant $1/c$. You don't want to reveal to the institue your set of genes (since it is a highly personal and sensitive information) and the institute does not want to reveal its findings. Then, you conduct a PSI protocol with the institute, obtain $A\cap B$ and conclude that your risk is $\|A\cap B\|/cm$. In fact, there are variants of PSI protocols that reveal to you (and to the institute) $\|A\cap B\|$ only (rather than the set itself); such variants are called PSI-Cardinality.


**Other applications**:
- Contact discovery (see [this](https://eprint.iacr.org/2018/579.pdf) and references within)
- Remote diagnostic (see [this](https://www.cs.cornell.edu/~shmat/shmat_ccs07.pdf))
- Record linkage (see [this](https://arxiv.org/pdf/1702.00535.pdf))
- Measuring the effectiveness of online advertising (see [this](https://eprint.iacr.org/2017/738.pdf))
- and many more...

Providing a comprehensive set of applications of PSI is worth a separate blog post, will do that soon!

### What are the rules? What can we use when designing a PSI protocol?

As in any problem in secure computation, we can design a protocol that involves a trusted third party (TTP), called Steve, to which Alice and Bob send $A$ and $B$ respectively. Then Steve computes the set $A\cap B$ and sends it back to Alice and Bob. Such a protocol is not acceptable as Alice and Bob want to avoid the disclosure of their items to anyone. They are willing to reveal $A\cap B$ to each other only.

In addition, Alice and Bob do not want to rely on a hardware solution like SGX or any other trusted execution environment (TEE).

They do, however, agree to use the service of an **untrusted** third party:

## PSI with an untrusted third party (also known as "server aided PSI")

In this setting there is an additional party, called Steve again, with which Alice and Bob interact. But the privacy requirement remains: **Steve should not learn information about the items of Alice and Bob**.

In this model we assume **no collusion**, meaning that Alice and Steve do not collude in order to fool Bob (i.e. make Bob conclude the intersection has more/less items than it really has) nor to break Bob's privacy (i.e. revealing information about Bob's items). Bob and Steve do not collude as well.

(It is possible to design a protocol that does not require a third party at all, not even an untrusted one. We'll keep this to a future post).

## The protocol

We are going to use following ingredient:

**_Pseudorandom function (PRF)_** - a function $F$ over two arguments, a key $K$ and an input $X$, outputs $Y$. $F$ is pseudorandom if for every $X$, the output $Y=F(K,X)$ looks random to someone who does not know the key $K$.

Now, the protocol proceeds as follows:
1. Alice has $A=\{a_1,\ldots,a_n\}$, Bob has $B=\{b_1,\ldots,b_n\}$.
2. Alice, Bob and Steve agree on a PRF $F$ they are going to use.
3. Alice and Bob agree on a key $K$ for $F$. This key remains secret to Steve.
4. For each $i=1,\ldots,n$, Alice sends $\hat a_i=F(K,a_i)$ to Steve. Alice also stores $D_A[\hat a_i]=a_i$.
5. For each $i=1,\ldots,n$, Bob sends $\hat b_i=F(K,b_i)$ to Steve. Bob also stores $D_B[\hat b_i]=b_i$.
6. Steve computes $\hat A\cap \hat B$, namely, the intersection between $\{\hat a_1,\ldots,\hat a_n\}$ and $\{\hat b_1,\ldots,\hat b_n\}$ and sends $\hat A\cap \hat B$ to Alice and Bob.
7. Let $\hat A\cap \hat B=(c_1,\ldots,c_m)$.
8. For each $i=1,\ldots,m$, Alice (resp. Bob) outputs $D_A[c_i]$ (resp. $D_B[c_i]$) as the intersection.

## Is the protocol private?

The only information leaked to Steve is the number of items Alice and Bob originally have and the size of the intersection, $\|A\cap B\|$. But let's assume this is acceptable (for now).

Steve does not learn anything about the _value_ of the items (neither those in the intersection nor the rest) because all he sees are outputs of $F$, and these look random to him, since he doesn't know $K$.

Alice learns only what items are in the intersection and nothing more, since Steve doesn't sends her $\hat b_j$ that are not in $\hat A\cap \hat B$.

## Is the protocol secure?

It depends, if we assume that Steve follows the protocol faithfully then yes. If we suspect Steve tries to cheat (i.e. fool Alice and Bob to conclude with a wrong intersection) then no, the protocol is not secure.

### Steve may cheat (1)

Steve may send Alice and Bob a different set of values, even values that are not in the intersection. 

**Example:**
Let $A=\{a_1,a_2,a_3,a_4,a_5\}$ and $B=\{b_1,b_2,b_3,b_4,b_5\}$ such that $a_1=b_1$ and $a_2=b_2$ and $A\cap B=\{a_1,a_2\}=\{b_1,b_2\}$. Then Steve receives $\hat A=\{\hat a_1,\hat a_2,\hat a_3,\hat a_4,\hat a_5\}$ from Alice and $\hat B=\{\hat b_1,\hat b_2,\hat b_3,\hat b_4,\hat b_5\}$ from Bob.

Steve may send $\{\hat a_1,\hat a_2,\hat a_3\}$ back to Alice and $\{\hat b_3, \hat b_4\}$ back to Bob so Alice outputs $a_1, a_2, a_3$ and Bob outputs $b_3,b_4$ as the intersection. This way, not only Alice and Bob do not agree on the result, they output incorrect results, specifically none of $a_3, b_3$ and $b_4$ are in the intersection.

**A solution by equality test.**
Fortunately, this cheat can be detected by Alice and Bob as follows: Alice and Bob will sort the items that they are about to output as the intersection and compute a hash on that set. Then, they will verify that they obtained the same hash value, this could be done by Alice sending the hash value to Bob, or in a safer way, by running a private equality test (PET) protocol on their results.

### Steve may cheat (2)

The above verification that the two output sets are the same is not sufficient. Specifically, Steve may send the same set to both Alice and Bob and still result in an incorrect output. For example, Steve may send the value $\hat a_1$, alone, to the parties, by which they output only $a_1$ as the intersection (instead of $\{a_1,a_2\}$). 

In general, Steve could claim that the intersection is smaller than it really is.


## How to detect cheating?

We will show 2 different ways to detect the above cheating strategy:


## Redundancy-based proof (based on [[KMRS14]](https://fc14.ifca.ai/papers/fc14_submission_52.pdf))
This is based on a work by Seny Kamara, Payman Mohassel, Mariana Raykova and Saeed Sadeghian.

The idea is this, choose some redundancy parameter $t$, now Alice, instead of sending to Steve only $\hat{a}_i=F(K,a_i)$ (for all $i$), she will send $t$ values $\hat a^1_i, \hat a^2_i,\ldots,\hat a^t_i$ where $\hat a^j_i=F(K,a_i\|\|j)$ (the term $a_i\|\|j$ means a concatenation of values $\hat a_i$ and $j$). 
In addition, Alice stores $D_A[\hat a^j_i]=a_i$ for every $j=1,\ldots,t$.
Bob will do the same, for every $i=1,\ldots, n$ he sends $\hat b^1_i, \hat b^2_i,\ldots, \hat b^t_i$ where $\hat b^j_i=F(K,b_i\|\|j)$. In addition, Bob stores $D_B[\hat b^j_i]=b_i$ for every $j=1,\ldots,t$.

But now, it is important that before Alice and Bob send $\hat A$ and $\hat B$ to Steve, they will shuffle them. This is in order to prevent a linkage between the $t$ PRF's results (e.g. $\hat a^1_i, \hat a^2_i,\ldots,\hat a^t_i$) that actually refer to the same original item (e.g. $a_i$).

Steve receives $n\cdot t$ values in total from Alice and from Bob. Obviously, if $\|A\cap B\|=q$ then now Steve finds that $\|\hat A\cap \hat B\|=q\cdot t$ because each value appears $t$ times.

When Alice and Bob receive the list $\hat A\cap \hat B$ from Steve, they will check that each item appears $t$ times. That is, Alice will check that for each item $x$ in the intersection there are exactly $t$ values $c_1,\ldots,c_t$ such that $D_A[c_i]=x$. If that doesn't hold then Alice conclude that either Steve is cheating or Bob is cheating.

Now, suppose Steve wants to omit one value, say $a_i$, from the intersection, he will have to omit $t$ values $\hat a^1_i, \hat a^2_i,\ldots,\hat a^t_i$, but those are spread randomly all over the list $\hat A$ so he could not tell (except with small probability) where they are.

Take our concrete example above and fix $t=3$, Steve receives $n\cdot t=5\cdot 3=15$ values from Alice and from Bob. If Steve wants to omit $a_1$ from the result intersection then it has to find the 3 values associated with $a_1$, that is, the values $\hat a^1_1, \hat a^2_1$ and $\hat a^3_1$. Since the set $\hat A$ is randomly shuffled, the probability of guessing correctly is $\binom{5}{3}^{-1}=1/10$. In general, the probability to remove a specific value from the intersection would be $\binom{n}{t}^{-1}$.

### Are we done?

No. There are two edge cases:
1. Steve can omit _all_ values from the intersection and simply give back an empty list to Alice and Bob.
2. Steve can send back to Alice her _entire list_ $\hat A$ and to Bob his _entire list_ $\hat B$. However, recall that we have already treated this case. This is considered as cheating only if $\hat A\neq \hat B$, which is covered by the equality test performed by Alice and Bob after receiving the result. 

To solve the first case, Alice and Bob agree on a set of $s$ values $E=\{e_1,\ldots,e_s\}$ such that both Alice and Bob take $E$ as part of their input sets. So now instead of computing the intersection $A\cap B$, they will compute the intersection $(A\cup E)\cap (B\cup E)$ which has at least $s$ items. This way, Bob could not return an empty set.


## Polynomial-based proof (based on [[LRG19]](https://eprint.iacr.org/2019/1338.pdf))
Phi Hung Le, Samuel Ranellucci and Dov Gordon proposed a different approach for solving the above cheating potential by Steve without the need for redunduncy. In their solution, Steve sends back to Alice and Bob the intersection $\hat A\cap \hat B$ as described above. In addition, if $\|\hat A\cap \hat B\|=k$, then Steve also proves to Alice and Bob that (1) there are at least $2n-k$ values in the union $A\cup B$ (which implies there are at most $k$ values in the intersection) and that (2) there are at least $k$ values in the intersection. Since the intersection and union sizes complete each other to a sum of $2n$, these two proofs are sufficient for convincing Alice and Bob that Steve does not cheat.

For more details see [the next post](https://decentralizedthoughts.github.io/2020-07-26-private-set-intersection-2/) in the series.
