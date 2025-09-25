---
title: Graded dispersal with perfect security
date: 2025-08-01 07:00:00 -04:00
tags:
- VID
author: Ittai Abraham, Gilad Asharov, Anirudh Chandramouli
---

In a [previous post](https://decentralizedthoughts.github.io/2024-08-08-vid) we covered the basics of *Asynchronous Verifiable Information Dispersal* (AVID) and the classic AVID of [Cachin and Tessaro, 2004](https://homes.cs.washington.edu/~tessaro/papers/dds.pdf). 

That protocol allows a sender to disperse a message of $O(n\log n)$ bits at a cost of just $O(n^2 \log^2 n)$ bits. However,

* It incurs a $O(\log n)$ storage overhead.
* It uses a cryptographic hash function, and obtains computational security.

It's natural to ask:

> Do VID protocols require cryptography? Can they obtain $O(1)$ storage overhead without computational assumptions?


In 2020 Jinyuan Chen published a [breakthrough result](https://arxiv.org/abs/2009.10965) (also see [DISC 2021](https://drops.dagstuhl.de/storage/00lipics/lipics-vol209-disc2021/LIPIcs.DISC.2021.17/LIPIcs.DISC.2021.17.pdf)), proving that Multi-valued Byzantine agreement with perfect security and optimal resilience in synchrony can be obtained with the asymptotically optimal $O(n)$ overhead!

The crux of Jinyuan's breakthrough is a new VID variation that has **perfect security**, where dispersal of $O(n\log n)$ bits cost just $O(n^2 \log n)$ bits.

Jinyuan's VID protocol is natural, but its proof is based on rather intricate arguments that combine coding theory, graph theory, and linear algebra. In this post we show a slightly improved version of this result with a simpler proof that is based on our recent work  [Simple is COOL: Graded Dispersal and its Applications for Byzantine Fault Tolerance](https://eprint.iacr.org/2024/2036). You can also watch a video about this work [here](https://www.youtube.com/watch?v=QuGvDU2NFuE).

Using this graded VID we prove two results:

**Theorem 1 [[SZR22]](https://eprint.iacr.org/2022/052)**: perfect security Reliable broadcast of $O(n\log n)$ bits at a cost of $O(n^2 \log^2 n)$ bits and $O(1)$ rounds in asynchrony against $f<n/3$ malicious corruptions.

**Theorem 2 [[C20]](https://arxiv.org/abs/2009.10965)**: perfect security multi-valued Agreement with inputs of $O(n\log n)$ bits at a cost of $O(n^2 \log^2 n)$ bits and $O(n)$ rounds in synchrony against $f<n/3$ malicious corruptions.


## Does perfect security matter

Let's first answer the question: in a world with abundant cryptography why should we care about non-cryptographic constructions and perfect security?

* Everlasting security and composability: cryptography depends on assumptions that may break and on security parameters that may become weak over time. Perfect security will always remain secure and is easy to compose.
* Simplicity and elegance: cryptography often increases the attack surface and requires more complex constructions. Perfect security is often simple and easy to verify. Simplicity also makes these schemes easy to learn and understand.
* Perfect security constructions provide a baseline upon which cryptography can then try to improve. This may expose the places where cryptography is necessary.



## Graded dispersal with perfect security

The core building block is a new **graded dispersal** protocol with **perfect security**. There are $n=3t+1$ parties that work over a field $\mathbb{F}$ with $n<\|\mathbb{F}\|$. Denote $w= \log \|\mathbb{F}\|$ and assume there are $t$ malicious parties. 

In this ***Graded Dispersal*** parties start with an input value of size $(t/3) w$ bits and output a value and a grade $0,1,2$, with the following properties:

1. **Validity**: If all honest parties start with the same input, they all output this value and grade $2$.
2. **Weak Graded Agreement**: If an honest party outputs grade 2, then all honest parties with grade $\geq 1$ output the same value and there are at least $t+1$ honest with grade $\geq 1$.

Note that if no honest party has grade 2, then honest parties with non-$\bot$ output and grade 1 may disagree on their output value. Moreover, grade 2 does not imply full agreement among the honest parties. Nevertheless, we show that this **Weak Graded Agreement** property is sufficient to work well with the Data Dissemination protocol (see Section [Data Dissemination](#data-dissemination)).





## A protocol for graded dispersal

The core protocol takes just 3 rounds.

**Input:** Each party $P_i$ holds $f_i(x)$ of degree at most $d = \lfloor t / 3 \rfloor$ over $\mathbb{F}$.

```
Graded Dispersal Protocol:

Round 1 - exchange points:
   Pi sends (f_i(i), f_i(j)) to each Pj

Round 2 - dynamic Set A1
   Let (u_j, v_j) be the two values that Pi receives from Pj
   If f_i(j) = u_j and f_i(i) = v_j 
      add j to A1
   If |A1| >= n - t
      send OK1 to all parties.

Round 3 - dynamic Set A2
   If OK1 is received from Pj and j in A1
      add j to A2
   If |A2| >= n - t
      send OK2 to all parties.

End of round 3 - output
   If OK2 was sent, and at least 2t + 1 OK2 messages were received
      output (f_i(x), 2)
   If OK2 was sent, but <= 2t OK2 messages were received
      output (f_i(x), 1)
   Otherwise
      output (bot, 0)
```


Each party sends two field elements and at most two more bits to each other party, so the total message complexity is $O(n^2 w)$ bits.



### Proof of the validity property 

If all honest parties start with the same polynomial $f(x)$:

1. All honest parties exchange consistent evaluation points $f(i)$ during round 1.
2. The $A^1$ set for each honest party will include all other honest parties.
3. Every honest party will broadcast an $\text{OK}_1$ message to all others.
4. Since no honest party is excluded from any honest $A^1$ set, all honest parties send $\text{OK}_2$ messages.
5. Each honest party receives $2t+1$ $\text{OK}_2$ messages, ensuring all output grade 2.

Thus, validity holds as all honest parties output grade 2 when starting with the same polynomial. This reasoning also holds in asynchrony.

### Proof of the weak graded agreement property 

We do this via three claims:

#### Claim 1: No three honest parties with different inputs can send $\text{OK}_1$ 

Seeking a contradiction, assume there are $t$ malicious parties, so there are 2t+1 honest and that honest parties 1,2,3 have different inputs and $\lvert B_1^1\rvert,\lvert B_2^1\rvert,\lvert B_3^1\rvert \geq 2t+1$.

Let $B_i^1$ be the honest parties in $A_i^1$, so $\lvert B_i^1\rvert \geq t+1$:


- Observe that  $\lvert B_i^1 \cap B_j^1\rvert \leq d$ for any $i,j \in \{1,2,3\}$ because we assume they all have a different degree at most $d$ inputs, so [can have at most $d$ points in common](https://decentralizedthoughts.github.io/2020-07-17-the-marvels-of-polynomials-over-a-field/).
- So by the [Inclusion-Exclusion Principle](https://en.wikipedia.org/wiki/Inclusion–exclusion_principle) we get $\lvert B_1^1 \cup B_2^1 \cup B_3^1\rvert \geq 3t+3 -3d$ but since $d=t/3$, this means there are more than $2t+1$ honest, creating a contradiction.

So we conclude that there are at most two inputs that have honest parties that send $\text{OK}_1$.




#### Claim 2: If there is a set of at least $t+1$ honest parties holding the same input, only parties from that set may send $\text{OK}_2$ 


- From claim 1, at most two values may send $OK_1$. Call them, the majority set with input $g$ and the minority set with input $f$.
- Any party $i$ in the minority set such that $f(i) \neq g(i)$ will not send $OK_1$ because they can get at most $t+t$ values in $A^1$. Because at most $t$ from being the minority and at most $t$ from the adversary.
- So at most $d$ parties in the minority set can send $OK_1$.
- Moreover, their $A^1$ set contains at most $d$ parties from the majority set, so no party in the minority set will see enough $OK_1$ in their $A^1$ set to send an $OK_2$.  Because at most $d$ from the majority, $d$ from the minority, and $t$ from the adversary, and using $2d+t<2t+1$ (since 2d<t).

#### Claim 3: If no set of at least $t+1$ parties exists, no honest party outputs grade 2



- From claim 1, at most two values may send $OK_1$.
- Similar to claim 2, at most $d$ parties in each value will send $OK_1$
- And similarly, their $A^1$ sets will contain at most $d$ parties from the other value.
- Hence, no party will see enough $OK_1$ in their $A^1$ set to send an $OK_2$ (because $2d+t<2t+1$).


---

By combining these claims, *Weak Graded Agreement* holds: if any party outputs grade 2, there must be at least $t+1$ honest parties outputting grade $\geq 1$ with the same input.





## Theorem 1: adding a post-round for totality in asynchrony

In the post-round parties send a "grade 2" message if they have grade 2, or they hear $t+1$ "grade 2" messages. Parties terminate if they hear $n-t$ "grade 2" messages.

* **Totality**: If an honest party terminates then eventually all honest parties terminate with grade 2.

Note that there is no guaranteed termination in this version.


### Adding a pre-round for a designated dealer

In dispersal, there is a designated dealer. In the pre-round the dealer sends its input to all parties. Then parties run graded dispersal. So we have

* **Validity**: If the designated sender is honest then all honest parties eventually output the sender's value and grade $2$. Moreover, with the post-round, all honest parties are guaranteed to terminate in this case.




## Theorem 2: adding a post-binary agreement for termination

In this variation, parties with grade 2 enter a binary agreement with 1 and otherwise enter with 0. If the outcome of the binary agreement is 1, then at least one honest party has grade 2, hence the retrieval protocol below will succeed.


### Retrieval protocol:

The retrieval protocol is run after the graded dispersal protocol. It has the following properties:

* **Binding**: If some honest party has output $f,2$ in the graded dispersal protocol then all parties output $f$ in the retrieval.


If some honest party has output $f$ with grade 2 then from Weak Graded Agreement there are $t+1$ honest that have $f$ and all other honest either have $f$ or know they don't.

```
Retrieval protocol

Round 1 - send point
   If Pi has grade >= 1
      send f_i(j) to each Pj

Round 2 - take the t+1
   If Pi has grade 0, and a value is sent t+1 times
      send this value to all
   If Pi has grade >=1
      send f_i(i) to all

End of round 2
   Wait to have 2t+1 values that agree on a degree <= t polynomial f
      output f
```


Your feedback on [X](https://x.com/ittaia/status/1951364975265718756).
