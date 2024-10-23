---
title: 'Phase-King through the lens of Gradecast: A simple unauthenticated synchronous
  Byzantine Agreement protocol'
date: 2022-06-09 07:11:00 -04:00
tags:
- dist101
author: Ittai Abraham and Andrew Lewis-Pye
---

In this post we overview a **simple** unauthenticated synchronous Byzantine Agreement protocol that is based on the Phase-King protocol of [Berman, Garay, and Perry 1989-92](http://plan9.bell-labs.co/who/garay/bit.ps). We refer also to [Jonathan Katz's excellent write-up](https://www.cs.umd.edu/~jkatz/gradcrypto2/f13/BA.pdf) on this same protocol from 2013. We offer a modern approach that decomposes the Phase-King protocol into a Graded Consensus building block.

Phase-King has optimal resilience of $n=3t+1$, runs in asymptotically optimal $3(t+1)$ rounds (recall that $t+1$ rounds is [optimal](https://decentralizedthoughts.github.io/2019-12-15-synchrony-uncommitted-lower-bound/)) and each message contains just a few bits for a total of $O(n^3)$ messages (recall that $\Omega(n^2)$ messages are [needed](https://decentralizedthoughts.github.io/2019-08-16-byzantine-agreement-needs-quadratic-messages/) and we will show how to get it in later posts).

Each party has an input $v \in \{V\}$ and parties are ordered $P_1,\dots, P_n$. For simplicity, we describe the protocol in the lock step model.

### Gradecast and Graded Consensus

Gradecast and Graded Consensus are key building blocks. In **Graded Consensus** each party has an input $v \in \{V\}$ and needs to output a $value \in \{V\}$ and a $grade \in \{0, 1,2\}$ with the following properties:

* **(Validity):** If all honest parties have the same input value, then all of them output this value with grade 2.
* **(Knowledge of Agreement):** If an honest party outputs a value with grade 2, then all honest parties output this value and grade > 0.

In Gradecast we assume there is a designated sender, and we replace the validity condition with the condition that the sender is honest. An authenticated variant of Graded Consensus called *Graded Byzantine Agreement* appears in [Momose and Ren 2021](https://arxiv.org/pdf/2007.13175), see this [blog post](https://decentralizedthoughts.github.io/2021-09-20-optimal-communication-complexity-of-authenticated-byzantine-agreement/ ) for more details.

Consider the following two-round Graded Consensus protocol for $t<n/3$: 

```
v := input

Round 1: send v to all parties
Round 2: if n-t distinct parties sent b in round 1, 
                then send b to all parties
End of round 2:
    If n-t distinct parties sent b in round 2,
                then output b with grade 2
    Otherwise, if t+1 distinct parties sent b in round 2,
                then output b with grade 1
    Otherwise, output v with grade 0
```

*Proof of Validity:* At least $n-t$ parties will send the same value $v$ in round 1, hence at least $n-t$ parties will send $v$ in round 2, hence all honest parties output value $v$ with grade 2.

To prove the Knowledge of Agreement property, we first prove a Weak Agreement property:

**(Weak Agreement):** No two honest parties send conflicting round 2 messages.
*Proof of Weak Agreement:* It cannot be the case that one honest party sees $n-t$ round 1 messages for $v$ and another honest party sees $n-t$ messages for $v' \neq v$ because any two sets of $n-t$ parties have least $t+1$ parties in the intersection. At least one of those must be honest, but honest parties send only one value in round 1. 

*Proof of Knowledge of Agreement:* If an honest party has grade 2, then it sees at least $n-t$ round 2 messages, hence all honest parties see at least $n-2t=t+1$ round 2 messages. Moreover, from the Weak Agreement property, we know that there cannot be $t+1$ round 2 messages for any other value.


*Note*: If we ran the protocol for just one round (instead of two rounds) we would not get Knowledge of Agreement. One honest party may see $n-t$ for value $b$, but another honest party may see $t+1$ for value $1-b$ (in addition to seeing $t+1$ for value $b$) so would not know which value to choose from.

### The Phase-King protocol in the lens of Graded Consensus

In this protocol each party has an input $v \in \{V\}$ and needs to decide on a value such that:

* **(Validity):** If all honest parties have the same input value, then all of them decide this value.
* **(Agreement):** All honest decide on the same value.

Using Graded Consensus the Phase-King protocol is rather simple. We consider $t+1$ phases, each of which consists of three rounds. In the first two rounds of each phase $i$, we run an instance of Graded Consensus. In the last round of phase $i$, we consider $P_i$ to be 'king'. The role of the king is to establish agreement in the case that honest parties are split between different values. The king sends their value to all parties, who change their value to $P_i$'s value unless their grade is 2: 

```
input v[0]

For i=1 to t+1:
    rounds 3i-2,3i-1:
        (v[i], grade[i]) := gradedconsensus(v[i-1])
    round 3i:
        party P_i: send v[i] to all parties
        if grade[i] < 2 then v[i] := party P_i's reported value
        
End of round 3(t+1):
    Decide v[t+1]
```

*Proof of Validity:* This follows from the Validity property of Graded Consensus and the fact that, in each phase, the grade will be 2, meaning that the king's value will be ignored.

*Proof of Agreement:* Consider the first phase with an honest king. If any honest party has a value with grade 2 in this phase, then from the Knowledge of Agreement property, this is the king's value and the value of any honest with grade 2, so all honest parties will either switch to the king's value, or already have that value with grade 2. Otherwise, all honest have grade $< 2$ in this phase, so they will switch to the king's value. In either case at the end of this phase all honest have the same value. Similar to the Validity argument above, will keep this value to the end and ignore all later kings, because all later Graded Consensus instances will end with grade 2 to all honest parties.

This concludes the proof for the Phase-King protocol. In the [next post](https://x.com/ittaia/status/1835357484195709231), we show how to use it recursively to reduce the message complexity to the optimal $O(n^2)$.

Your thoughts/comments on [Twitter](https://twitter.com/ittaia/status/1534873601358368769?s=20&t=h3N-bj0BKuqFb-D5eFreig).