---
title: Divide and Conquer in Distributed Computing - synchronous BFT with quadratic
  communication via recursive phase king
date: 2024-09-15 07:00:00 -04:00
tags:
- dist101
author: Ittai Abraham, Renas Bacho, and Gilad Stern
---

The idea of decomposing a hard problem into easier problems is a fundamental algorithm design pattern in Computer Science. [Divide and Conquer](https://en.wikipedia.org/wiki/Divide-and-conquer_algorithm) is used in so many domains: sorting, [multiplication](https://www.youtube.com/watch?v=JCbZayFr9RE), and [FFT](https://decentralizedthoughts.github.io/2023-09-01-FFT/), to mention a few. But what about distributed computing?

In this post we will highlight how divide and conquer can help unauthenticated synchronous Byzantine agreement obtain **quadratic communication**, which is asymptotically optimal due to [Dolev and Reischuk's lower bound](https://decentralizedthoughts.github.io/2019-08-16-byzantine-agreement-needs-quadratic-messages/).

***Theorem: [Coan and Welch, 1992](https://www.sciencedirect.com/science/article/pii/089054019290004Yhttps://www.sciencedirect.com/science/article/pii/089054019290004Y), and [Berman, Garay, and Perry, 1992](https://link.springer.com/chapter/10.1007/978-1-4615-3422-8_27): there exists a synchronous agreement protocol with $O(n^2)$ message complexity that can tolerate $f<n/3$ Byzantine parties.***

The idea is to run a [phase king protocol](https://decentralizedthoughts.github.io/2022-06-09-phase-king-via-gradecast/), with two (instead of $f+1$) phases. Recall that in the original phase king protocol, each phase had a king whose value was used if the **graded consensus** does not have grade 2. Here we replace the king, with taking majority on the outcome of a recursive call on half the parties.

See our [previous post](https://decentralizedthoughts.github.io/2022-06-09-phase-king-via-gradecast/) for implementing graded consensus and its properties.


```
Protocol for N parties that are split into two halves: N1, N2 


v[0] := input

//phase 1:

(v[1], grade[1]) := gradeconsensus(v[0])

Parties in N1:
    c: = Consensus-on-N1(v[1])

Each party in N1 sends its c value to everyone, 
if grade[1] < 2 then v[1] := majority of N1 c values


//phase 2:

(v[2], grade[2]) := gradeconsensus(v[1])

Parties in N2:
    c: = Consensus-on-N2(v[2])

Each party in N2 sends its c value to everyone, 
if grade[2] < 2 then v[2] := majority of N2 c values


Decide v[2]
```

At first glance, it seems like we're solving consensus using consensus, which isn't all that impressive. However, note that consensus for $n$ parties is solved assuming we know how to solve consensus for $n/2$ parties. Each consensus instance is then solved recursively by breaking that instance into two as well. We can continue dividing the number of parties until we get to such a small number of parties that solving consensus is almost trivial. At that point we can use any protocol we want (as long as it's not very inefficient). We then use the output in the small instances to reach consensus in the bigger instances.

### Proof

*Proof of Validity*: As in the regular Phase King protocol, if all honest parties have the same input $b$, then from the validity property of graded consensus, in each phase, the grade will be 2, so the value will not change. Hence, the output will be $b$ as well. 

*Proof of Agreement*: Since $N$ has less than $1/3$ malicious, then either $N_1$ or $N_2$ must have less than a $1/3$ fraction of malicious parties (even Byzantine parties cannot live in [Lake Wobegon](https://en.wikipedia.org/wiki/Lake_Wobegon)). So let $i$ be the (first) index $i \in 1,2$ such that $N_i$ has less than a $1/3$ fraction of malicious parties and consider two cases:

* Case 1: some honest party gets grade 2 in the graded consensus of phase $i$, then all honest parties have the same value $v[i]$, and from the validity of the consensus, this is the decision value in $N_i$. This means that every party will either have that value because its grade was $2$ in the graded consensus, or adopt the value it received from a majority of the parties in $N_i$. Since all honest parties in $N_i$ output $v[i]$ and the majority of the parties in $N_i$ are honest, every party will receive $v[i]$ from a majority of parties in $N_1$ and adopt $v[i]$ as well. 

* Case 2: no honest party gets grade 2 in the graded consensus of phase $i$, then let $b$ be the decision value in the consensus on $N_i$. So all honest parties will hear a majority of parties in $N_i$ say $b$ and hence adopt that value because their grade is $<2$ and thus set $v[i] := b$. 

Finally, in either of the above cases, if $i=1$, then all honest parties will get grade 2 in phase 2, hence agree on this value ($v[1] = v[2]$). On the other hand, if $i=2$, they will simply output $v[2]$ after phase $2$.

### Quadratic message complexity

Let's prove by induction that the message complexity for a set of $n$ parties is at most $d n^2$ for some constant $d >8$.

Base case for $n=4$: use the regular [phase king protocol](https://decentralizedthoughts.github.io/2022-06-09-phase-king-via-gradecast/) that for $t=1$ runs in 2 phases where each phase has a graded consensus and an all to all send. So choosing $d=9$ is fine.

Now from the induction hypothesis, the consensus protocol for $n/2$ parties has message complexity of $d n^2/4$. Consider the message complexity of the protocol above for $n$ parties: it consists of two graded consensus instances, two all to all sends, and two consensus invocations on sets of size $n/2$ each. Since each graded consensus is at most $2n^2$, the total is less than:

$$
6 n^2 + d n^2/4
$$

Which is smaller than $d n^2$ for $d >8$.

### Notes

* This is a follow-up post to our post on [graded consensus and the phase king protocol](https://decentralizedthoughts.github.io/2022-06-09-phase-king-via-gradecast/).

* This recursive solution can also be used in the authenticated setting to obtain $O(n^2)$ communication and resilience of $t<n/2$ (or $t<n/(2+\epsilon)$). See [Momose and Ren 2021](https://arxiv.org/pdf/2007.13175), they are also the first to make the connection to an abstract graded consensus (or graded Byzantine agreement) as a building block. See this [blog post](https://decentralizedthoughts.github.io/2021-09-20-optimal-communication-complexity-of-authenticated-byzantine-agreement/ ) for more details.


### Acknowledgments

Many thanks to Ling Ren for insightful comments and pointers

Your thoughts/comments on [Twitter](https://x.com/ittaia/status/1835357484195709231). 