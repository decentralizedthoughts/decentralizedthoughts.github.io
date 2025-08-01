---
title: Optimal Communication Complexity of Authenticated Byzantine Agreement
date: 2021-09-20 15:28:00 -04:00
tags:
- research
author: Atsuki Momose, Ling Ren
---

Communication complexity of [Byzantine Agreement (BA)](https://decentralizedthoughts.github.io/2020-09-14-broadcast-from-agreement-and-agreement-from-broadcast/) has been studied for decades. [Dolev and Reischuk](https://decentralizedthoughts.github.io/2019-08-16-byzantine-agreement-needs-quadratic-messages/) showed that quadratic communication is necessary for BA with perfect security, i.e., without error. [Berman, Garay, and Perry](https://dl.acm.org/doi/10.5555/166961.167018) showed that this lower bound is tight for the [unauthenticated setting](https://decentralizedthoughts.github.io/2019-08-02-byzantine-agreement-is-impossible-for-$n-slash-leq-3-f$-is-the-adversary-can-easily-simulate/) (without signatures) with $f < n/3$. However, for $f \ge n/3$, the best solution so far is still the [Dolev-Strong protocol](https://decentralizedthoughts.github.io/2019-12-22-dolev-strong/) with cubic communication, so a linear gap remains. 

[Our recent paper](https://arxiv.org/abs/2007.13175) gives two new protocols (see the table below) towards closing this gap. 

| model               | fault tolerance              | communication         | reference     |
| ------------------- | ---------------------------- | --------------------- | ------------- |
| unauthenticated     | $f < n/3$                  | $O(n^2)$              | Berman et al. |
| PKI                 | $f < n/2$                    | $O(\kappa n^2 + n^3)$ | Dolev-Strong  |
| threshold signature | $f < n/2$                    | $O(\kappa n^2)$       | **our work**  |
| PKI                 | $f \le (1/2 - \varepsilon)n$ | $O(\kappa n^2)$       | **our work**  |

For ease of explanation, we will consider a simpler problem in this post: detecting equivocation. Equivocation, i.e., saying different things to different nodes, is arguably the most common attack in Byzantine consensus. The key technical contribution of our paper is a new method to detect equivocation based on expander graphs. 

## Existing techniques to detect equivocation 

Let's consider the following simple and perhaps easiest agreement problem. Each node has its own input binary value, and

- **Safety**: If two honest nodes decide $b$ and $b'$, then $b = b'$.
- **Liveness**: If all honest nodes have the same input $b$, all honest nodes decide on $b$.
 
Note that it's allowed that someone decides but others do not if honest nodes input different values. As one can easily expect, the challenge is mostly on how to achieve safety despite equivocation by faulty nodes.


With $f < n/3$ faults, this is very easy:

- In round 1. Each node sends a vote for $b$ for its own input value $b$.
- In round 2. If a node receives $n-f$ votes for $b$ for a value $b$, decide on $b$.

If any node decides on a value $b$ upon collecting votes on $b$ from a quorum of $n-f > 2f$ nodes, then $n-f$ votes on $b'$ cannot exists, because that would require at least $2(n-f) - n = n-2f > f$ nodes to vote for both $b$ and $b'$ — this is what is called the *quorum-intersection argument.* The communication complexity is quadratic in this simple protocol as all nodes just send their own votes.


With $f \ge n/3$ faults, the above approach does not work, because faulty nodes can launch the so-called ["split-brain" attack](https://decentralizedthoughts.github.io/2019-06-25-on-the-impossibility-of-byzantine-agreement-for-n-equals-3f-in-partial-synchrony/). Suppose the network consists of three partitions $P_0, P_1, P_f$ of $n/3$ nodes each, and $P_f$ is faulty. $P_0$ and $P_1$ honestly send "vote for 0" and "vote for 1", respectively. On the other hand, $P_f$ send "vote on 0" to $P_0$ and "vote on 1" to $P_1$, i.e., perform equivocation. Then, $P_0$ will collect "vote on 0" from $2n/3 = n-f$ nodes, and $P_1$ will collect "vote on 1" from $n-f$ nodes, and hence $P_0$ and $P_1$ decide differently.


A simple and natural solution is to have each node forward the received votes to other nodes. This will detect $P_f$'s equivocation. In fact, it is the most common approach to handle equivocation with $f < n/2$ faults, e.g., in [Abraham, Devadas, Dolev, Nayak, and Ren](https://eprint.iacr.org/2018/1028.pdf). However, each node forwarding linear votes would require cubic communication. One can rely on threshold signatures to compress a set of votes into a single vote. But threshold signatures require a trusted dealer to generate public and private keys for all nodes, which is a strong assumption. Can we detect equivocation with quadratic communication and $f \ge n/3$ faults without such a strong setup?

## Using an expander to efficiently detect equivocation

To solve this challenge, we utilize an expander. Intuitively, an expander is a graph with sparse edges but good overall connectivity, as defined as follows.

**Expander**:  For any $0 < \alpha < \beta < 1$, an $(n,\alpha,\beta)$-expander is a graph of $n$ nodes such that any subset of $\alpha n$ nodes have neighbors of more than $\beta n$ nodes.

It is well known that for any $n$ and $0 < \alpha < \beta < 1$, a constant-degree $(n,\alpha,\beta)$-expander exists. We use $(n,2\varepsilon,1-2\varepsilon)$-expander, denoted $G_{n,\varepsilon}$, to detect equivocation with $f \le (1/2-\varepsilon)n$ faults for any positive constant $\varepsilon$.


Our key idea is to forward votes along the expander edges. We observe that the good connectivity of expander is enough to detect equivocation and prevent inconsistent decisions between honest nodes. The protocol for $f \le (1/2-\varepsilon)n$ faults is shown below. The key step is marked in **bold**: each node forwards the $n-f$ received votes to their neighbors in the expander, as opposed to all nodes. 

- In round 1. Each node sends a vote on $b$ for its own input value $b$.
- In round 2. If a node receives $n-f$ votes for $b$, forward them to **the neighbors in the expander $G_{n,\varepsilon}$**.
- In round 3. If a node forwarded  $n-f$ votes on $b$ in round 2, and does not receive $n-f$ votes on $b'$, it sends "decide on $b$"
- In round 4. If a node receives "decide on $b$" from $n-f$ nodes, it decides on $b$.

Suppose $n-f$ "decide on $b$" are sent. Then at least $n-2f \ge 2\varepsilon n$ honest nodes must have forwarded $n-f$ votes on $b$ in round 2. Due to the expansion property of $G_{n,\varepsilon}$, more than $(1-2\varepsilon)n = 2f$ nodes must have received $n-f$ votes on $b$.  Out of these, more than $f$ are honest nodes, and they would not send "decide on $b'$". Therefore, $n-f$ "decide on $b'$" cannot exist, and honest nodes will not decide on $b'$. Since the expander $G_{n,\varepsilon}$ has a constant degree, the total communication is quadratic.

## From equivocation detection to graded agreement and Byzantine agreement 

We utilize the above equivocation detection technique to improve a primitive called *Graded Agreement (GA)* to have quadratic communication and tolerate minority Byzantine faults. 
We also observe that the Berman et al. paper can be viewed as a recursive method to build a quadratic Byzantine Agreement (BA) from quadratic GA. 
We refer interested readers to [our paper](https://arxiv.org/abs/2007.13175) and a [future post](https://decentralizedthoughts.github.io/2024-09-15-divide-and-conquer/) for more details on the GA constructions and the recursive method. 

[Atsuki Momose](https://twitter.com/AtsukiMomose) and [Ling Ren](https://sites.google.com/view/renling) 

