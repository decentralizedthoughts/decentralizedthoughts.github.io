---
title: Authenticated Broadcast in $O(n^{2.5}\log n)$ Communication
date: 2026-10-23 00:00:00 -04:00
published: false
tags:
- research
author: Yuval Efron, Jovan Komatovic, Ling Ren
---

The [Dolev–Strong](https://decentralizedthoughts.github.io/2019-12-22-dolev-strong/) protocol, from 1983, is the best-known protocol for Byzantine broadcast. With a PKI, it tolerates any number $t<n$ of corruptions, and it runs in $t+1$ rounds, which is optimal for deterministic protocols. Its communication complexity is $O(n^2t\lambda)$ bits, which is $O(n^3\lambda)$ for $t=\Theta(n)$. The [Dolev–Reischuk](https://decentralizedthoughts.github.io/2019-08-16-byzantine-agreement-needs-quadratic-messages/) lower bound, by contrast, is only quadratic. Despite four decades of research, no deterministic protocol tolerating a dishonest majority had improved on the communication complexity of Dolev–Strong.

In a [new paper](https://eprint.iacr.org/2026/2504), we give a deterministic Byzantine broadcast protocol with $\widetilde O(n^2)$ communication for any $t<n$, assuming a PKI and a collision-resistant hash function. In this post, we show an elementary protocol that already breaks the cubic barrier, using only a PKI:

**Theorem**: Assume a PKI, and $n-t\ge\sqrt n$. There is a deterministic Byzantine broadcast protocol with $O(n^{2.5}\log(n)\,\lambda)$ bits of communication and $3t+1$ rounds.

#### Model

There are $n$ parties, communicating in synchronous rounds, and a designated leader $\ell$ with an input bit $b$. An adversary corrupts up to $t$ parties. We want the usual [broadcast properties](https://decentralizedthoughts.github.io/2019-06-27-defining-consensus/):
1. _Termination_: every honest party outputs a bit.
2. _Agreement_: all honest parties output the same bit.
3. _Validity_: if the leader is honest, all honest parties output its input.

We assume a PKI, and count each signature as $\lambda$ bits, where $\lambda\ge\log n$. Communication complexity is the worst-case total number of bits sent by honest parties. For simplicity, $n$ is a perfect square.

#### The graph

The protocol uses a fixed sparse graph on the parties, known to everyone.

**Lemma**: There is a graph $G$ on the $n$ parties with maximum degree $O(\sqrt n\log n)$, such that any two disjoint sets of at least $\sqrt n$ parties are joined by an edge of $G$.

*Proof*. Let $G$ be the union of $m=3\sqrt n\ln n$ independent uniformly random permutations $\pi_1,\ldots,\pi_m$ of the parties: an edge $\{v,\pi_j(v)\}$ for every $v$ and $j$, ignoring self-loops. Every degree is at most $2m$. Fix disjoint $X,Y$ of size $\sqrt n$ (larger sets only help). A single permutation maps no element of $X$ into $Y$ with probability at most $(1-1/\sqrt n)^{\sqrt n}\le e^{-1}$, so no edge joins $X$ and $Y$ with probability at most $e^{-m}=n^{-3\sqrt n}$. A union bound over the at most $n^{2\sqrt n}$ choices of $X$ and $Y$ shows that $G$ has the property with positive probability.

We write $N(p)$ for the neighbors of party $p$ in $G$. Note that the graph does not restrict who talks to whom: messages still go over the complete network. It only decides *which signatures* a party forwards.

#### Dolev–Strong, recalled

In round $0$, the leader signs its input and multicasts it. From then on, a party accepts a bit $b$ in round $r\le t+1$ if, by then, it has received signatures on $b$ from $r$ distinct parties, including $\ell$. When a party accepts $b$, it signs $b$ and multicasts all $r+1$ signatures, so that every other party accepts $b$ in the next round. After round $t+1$, each party outputs the unique bit it accepted, or a default value if it accepted neither bit or both.

**Agreement.** If an honest party accepts $b$ in round $r\le t$, then every honest party accepts $b$ by round $r+1$. If an honest party first accepts $b$ in round $t+1$, it holds $t+1$ signatures, so one of them is from an honest party, which accepted $b$ earlier, a contradiction.

**Where the $n^3$ comes from.** An honest party may accept late, holding $\Theta(n)$ signatures, and multicast all of them. If $\Theta(n)$ honest parties do so in the same round, this costs $\Theta(n)\cdot\Theta(n)\cdot\Theta(n)$ signatures.

Note, however, that when many honest parties accept together, they also create many *fresh* signatures: their own. Our protocol uses them.

#### Dolev–Strong in steps of three rounds

We split each round of Dolev–Strong into a *step* of three rounds:
1. In the first round of step $r$, a party that holds signatures on $b$ from $r$ parties, including $\ell$, accepts $b$. It multicasts only *its own* signature on $b$, its $\langle\mathsf{accept},b\rangle_p$ message.
2. In the second round, it counts the signatures it holds, including the new $\mathsf{accept}$ messages of the parties that accepted together with it. If it holds fewer than $r+\sqrt n$, which happens only if fewer than $\sqrt n$ honest parties accepted together with it, it falls back to Dolev–Strong and multicasts everything it holds, in a $\mathsf{certificate}$ message. This is cheap, since few honest parties do it. Otherwise, it fixes a witness $W$ of $r+\sqrt n$ signatures, and sends each party $q$ only the part of $W$ signed by $q$'s neighbors.
3. In the third round, every party forwards to everyone the signatures of its own neighbors, each at most once.

The graph guarantees that, at the end of the step, each honest party misses fewer than $\sqrt n$ signers of $W$. So it holds at least $r+1$ of them, and accepts $b$ in the next step.

#### The protocol

Each party $p$ maintains $A(b)$, the set of valid $\mathsf{accept}$ messages for $b$ it has received, one per signer. This includes its own, and those carried inside other messages. A non-leader's $\mathsf{accept}$ message is valid only together with $\langle\mathsf{accept},b\rangle_\ell$, so every message below also carries the leader's. For a set $S$ of $\mathsf{accept}$ messages and a set $X$ of parties, $S\cap X$ denotes the messages in $S$ signed by parties in $X$.

```
// Party p, with neighbors N(p) in G
Round 0:
    If p = ℓ: accept its input b, and multicast ⟨accept, b⟩_ℓ.

For each step r = 1, ..., t:
  Round 1:
    For each bit b not yet accepted, with |A(b)| ≥ r and ⟨accept, b⟩_ℓ ∈ A(b):
        accept b; multicast ⟨accept, b⟩_p.
  Round 2:
    For each bit b accepted in Round 1:
        If |A(b)| < r + √n:
            multicast ⟨certificate, b, A(b)⟩.
        Else:
            choose W ⊆ A(b) with |W| = r + √n and ⟨accept, b⟩_ℓ ∈ W;
            send ⟨data, b, W ∩ N(q)⟩ to each party q.
  Round 3:
    For each bit b:
        Z = the messages in A(b) ∩ N(p) that p has not forwarded before;
        if Z is nonempty: multicast ⟨forward, b, Z⟩.

At the start of step t+1:
    Also accept each b with |A(b)| ≥ t+1 and ⟨accept, b⟩_ℓ ∈ A(b).
    Output the accepted bit if there is exactly one, and 0 otherwise.
```

#### Analysis

**Propagation.** If an honest party $p$ accepts $b$ in step $r\le t$, then every honest party accepts $b$ by step $r+1$.

If the leader is honest, every honest party accepts its input in step $1$. Otherwise $p$ is not the leader, so after Round 1 its set $A(b)$ contains its own new $\mathsf{accept}$ message, and has at least $r+1$ signers. If $p$ sends a $\mathsf{certificate}$, every honest party receives these $r+1$ signatures, and accepts $b$ by step $r+1$.

Otherwise $p$ sends the parts of $W$, which has $r+\sqrt n$ signers. Fix an honest party $q$, and suppose that, at the end of step $r$, $q$ still misses the $\mathsf{accept}$ messages of a set $Y$ of $\sqrt n$ signers of $W$. Each honest party has multicast its own $\mathsf{accept}$ message, so $Y$ contains only corrupt parties. The set $H$ of honest parties is disjoint from $Y$, and $|H|\ge n-t\ge\sqrt n$. So by the lemma, some $h\in H$ and $y\in Y$ are neighbors. In Round 2, $h$ received $y$'s $\mathsf{accept}$ message from $p$, as part of $W\cap N(h)$. In Round 3, it forwarded the message to everyone, unless it had forwarded it before. Either way, $q$ has $y$'s message, contradicting $y\in Y$. So $q$ misses fewer than $\sqrt n$ signers of $W$. It therefore holds at least
$$(r+\sqrt n)-(\sqrt n-1)=r+1$$
signers, including the leader, and accepts $b$ by step $r+1$.

**Agreement.** As in Dolev–Strong, it suffices to show that if an honest party accepts $b$ at the start of step $t+1$, some honest party accepted $b$ earlier: then, by propagation, every honest party has accepted $b$ by step $t+1$. If the leader is honest, this is immediate. Otherwise, the party holds $t+1$ signers, one of them honest and not the leader, which accepted $b$ in an earlier step.

**Validity.** If the leader is honest, every honest party accepts its input in step $1$, and no party can accept the other bit, which lacks the leader's signature.

**Communication.** Fix a bit. Each honest party sends its $\mathsf{accept}$ message once, for $O(n^2\lambda)$ bits in total.
- *Certificates.* Suppose $a$ honest parties accept $b$ in step $r$. Each of them held at least $r$ signers before the step, and receives all $a$ new $\mathsf{accept}$ messages in Round 1, so it holds at least $r+a$ signers in Round 2. So an honest party sends a $\mathsf{certificate}$ only if $a<\sqrt n$. By propagation, honest parties accept $b$ in at most two consecutive steps, so fewer than $2\sqrt n$ of them send a $\mathsf{certificate}$. Each has at most $n$ signatures and goes to $n$ parties, for $O(n^{2.5}\lambda)$ bits.
- *Data.* Each honest party sends $\mathsf{data}$ messages at most once, with $|N(q)|=O(\sqrt n\log n)$ signatures to each $q$, for $O(n^{2.5}\log(n)\,\lambda)$ bits in total.
- *Forwarding.* Each party forwards each neighbor's $\mathsf{accept}$ message at most once, to $n$ parties, for $O(n^{2.5}\log(n)\,\lambda)$ bits in total.

Summing over the two bits gives $O(n^{2.5}\log(n)\,\lambda)$ bits. There are $3t+1$ rounds, plus the local test at the start of step $t+1$.

#### From $n^{2.5}$ to $n^2$

Where does the remaining $\sqrt n$ go? In the protocol above, the convinced parties still *push* their signatures to everyone, through the graph. In the [paper](https://eprint.iacr.org/2026/2504), we shift the responsibility to the parties that are not yet convinced. These parties *pull* the signatures they lack from the parties that announced acceptance. Pulling efficiently against both corrupt senders and corrupt receivers takes a few more ideas: a binary-search procedure that splits the work among the senders, requests that grow gently, and vector commitments to the sender list. Together they bring the communication down to $\widetilde O(n^2)$, for every $t<n$, in $O(t)$ rounds.

Please leave comments on [Twitter](TODO).
