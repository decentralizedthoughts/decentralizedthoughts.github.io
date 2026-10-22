---
title: Authenticated Broadcast in $O(n^{2.5}\log n)$ Communication
date: 2026-10-23 00:00:00 -04:00
published: false
tags:
- research
author: Yuval Efron, Jovan Komatovic, Ling Ren
---

The [Dolev–Strong](https://decentralizedthoughts.github.io/2019-12-22-dolev-strong/) protocol is the best-known protocol for Byzantine broadcast. It is a deterministic protocol and tolerates any number $t<n$ of corruptions (assuming digital signatures). It runs in $t+1$ rounds, which is optimal for deterministic protocols. Its communication complexity is $O(n^2t\lambda)$ bits, which is $O(n^3\lambda)$ for $t=\Theta(n)$. The [Dolev–Reischuk](https://decentralizedthoughts.github.io/2019-08-16-byzantine-agreement-needs-quadratic-messages/) lower bound, by contrast, is only quadratic. Despite four decades of research, no deterministic protocol tolerating a dishonest majority has improved on the communication complexity of Dolev–Strong.

In a [new paper](https://eprint.iacr.org/2026/2504), we give a deterministic Byzantine broadcast protocol with $\widetilde O(n^2)$ communication for any $t<n$, assuming digital signatures and a collision-resistant hash function. ChatGPT substantially assisted with protocol design and proof development.

In this post, we show an elementary protocol that already breaks the cubic barrier.

**Theorem**: Assuming digital signatures and PKI, there is a deterministic Byzantine broadcast protocol that tolerates $t \le n - \sqrt n$ faults, runs in $3t+1$ rounds, and has $O(n^{2.5}\log(n)\lambda)$ bits of communication. 

#### Model

There are $n$ parties, communicating in synchronous rounds, and a designated leader with an input bit $b$. An adversary corrupts up to $t$ parties. We want the usual [broadcast properties](https://decentralizedthoughts.github.io/2019-06-27-defining-consensus/):
1. _Termination_: every honest party outputs a bit.
2. _Agreement_: all honest parties output the same bit.
3. _Validity_: if the leader is honest, all honest parties output its input.

(The leader is usually called a *sender*, but we reserve the term *sender* for another purpose in this work.)

We assume each signature is $\lambda$-bit, where $\lambda > \log n$. Communication complexity is the total number of bits sent by honest parties in the worst case. For simplicity, assume $n$ is a perfect square.

#### The graph

The protocol uses a fixed sparse graph on the parties, known to everyone.

**Lemma**: There is a graph $G$ with $n$ vertices with maximum degree $O(\sqrt n\log n)$, such that any two disjoint sets of $\sqrt n$ vertices are joined by an edge of $G$.

*Proof*. Let $G$ be the union of $m=3\sqrt n\ln n$ independent uniformly random permutations $\pi_1,\ldots,\pi_m$ of the vertices: add an edge $(\{v,\pi_j(v)\})$ for every $v$ and $j$, ignoring self-loops. The degree of $G$ is at most $2m$. Fix disjoint $X,Y$ of size $\sqrt n$ (larger sets only help). A single permutation maps no element of $X$ into $Y$ with probability at most $(1-1/\sqrt n)^{\sqrt n}\le e^{-1}$, so no edge joins $X$ and $Y$ with probability at most $e^{-m}=n^{-3\sqrt n}$. A union bound over the at most $n^{2\sqrt n}$ choices of $X$ and $Y$ shows that $G$ has the property with positive probability.

Let each vertex be a party. We write $N(p)$ for the neighbors of party $p$ in $G$. Note that the graph does not restrict who talks to whom: messages still go over the complete network. It only decides *which signatures* a party forwards.

#### Dolev–Strong, recalled

In round $0$, the leader signs its input and multicasts it. From then on, a party accepts a bit $b$ in round $r\le t+1$ if, by then, it has received signatures on $b$ from $r$ distinct parties, including the leader. When a party accepts $b$, it signs $b$ and multicasts all $r+1$ signatures, so that every other party accepts $b$ in the next round. After round $t+1$, each party outputs the unique bit it accepted, or a default value if it accepted neither bit or both.

**Agreement.** If an honest party accepts $b$ in round $r\le t$, then every honest party accepts $b$ by round $r+1$. If an honest party first accepts $b$ in round $t+1$, it holds $t+1$ signatures, so one of them is from an honest party, which accepted $b$ earlier, a contradiction.

**Where the $n^3$ comes from.** An honest party may accept late, holding $\Theta(n)$ signatures, and multicast all of them. If $\Theta(n)$ honest parties do so in the same round, this costs $\Theta(n)\cdot\Theta(n)\cdot\Theta(n)$ signatures.

Note, however, that when many honest parties accept together, they also create many *fresh* signatures: their own. This is a central observation behind the new protocol.

#### Dolev–Strong in steps of three rounds

We split each round of Dolev–Strong into a *step* of three rounds:
1. In the first round of step $r$, a party that holds $r$ signatures (including the leader's) accepts $b$. If a party newly accepts $b$, it multicasts only *its own* signature on $b$ in a signed $\langle\mathsf{accept},b\rangle_p$ message.
2. In the second round, if fewer than $\sqrt n$ parties sent $\langle\mathsf{accept},b\rangle_*$ messages in the last round, then a party that newly accepts $b$ falls back to Dolev–Strong: multicasts all the signatures it holds to everyone.  This is cheap since few honest parties will do the same. Otherwise, the party holds signatures from at least $n + \sqrt n$ distinct parties; in this case, the party sends each party $q$ only the signatures of $q$'s neighbors. 
3. In the third round, each party forwards to everyone the signatures of its own neighbors (at most once for each neighbor in the entire protocol).

The graph guarantees that, at the end of the step, each honest party misses fewer than $\sqrt n$ signatures. So it holds at least $r+1$ of them, and accepts $b$ in the next step.

#### The protocol

Each party $p$ maintains $A(b)$, the set of valid $\mathsf{accept}$ messages for $b$ it has received, one per signer. This includes its own, and those carried inside other messages. A non-leader's $\mathsf{accept}$ message is valid only together with $\langle\mathsf{accept},b\rangle_\ell$ ($\ell$ is the leader), so every message below also carries the leader's. For a set $S$ of $\mathsf{accept}$ messages and a set $X$ of parties, $S\cap X$ denotes the messages in $S$ signed by parties in $X$.

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
            send ⟨data, b, A(b) ∩ N(q)⟩ to each party q.
  Round 3:
    For each bit b:
        Z = the messages in A(b) ∩ N(p) that p has not forwarded before;
        if Z is nonempty: multicast ⟨forward, b, Z⟩.

At the end of step t+1:
    Also accept each b with |A(b)| ≥ t+1 and ⟨accept, b⟩_ℓ ∈ A(b).
    Output the accepted bit if there is exactly one, and 0 otherwise.
```

#### Analysis

**Propagation.** If an honest party $p$ accepts $b$ in step $r\le t$, then every honest party accepts $b$ by step $r+1$.

If $p$ is the honest leader, every honest party accepts its input in step $1$. We focus on the case of $p \neq \ell$.

After Round 1, $p$'s set $A(b)$ contains at least $r+1$ signers. If $p$ sends a $\mathsf{certificate}$, every honest party receives these $r+1$ signatures, and accepts $b$ by step $r+1$.

Otherwise, $p$ holds at least $r+\sqrt n$ signatures. Fix an honest party $q$, and suppose that, at the end of step $r$, $q$ still misses the $\mathsf{accept}$ messages of a set $Y$ of $\sqrt n$ of signers in $p$'s $A(b)$. Each honest party has multicast its own $\mathsf{accept}$ message, so $Y$ contains only corrupt parties. The set $H$ of honest parties is disjoint from $Y$, and $|H|\ge n-t\ge\sqrt n$. So by the lemma, some $h\in H$ and $y\in Y$ are neighbors. In Round 2, $h$ received $y$'s $\mathsf{accept}$ message from $p$, and in Round 3, $h$ forwarded the message to everyone (unless it had done so before). Thus, $q$ has $y$'s message, contradicting $y\in Y$. So $q$ misses fewer than $\sqrt n$ signers and it holds signatures from at least
$$(r+\sqrt n)-(\sqrt n-1)=r+1$$
signers, including the leader, and accepts $b$ by step $r+1$.

The rest of the agreement proof is identical to that of Dolev-Strong.

**Communication.** Fix a bit $b$. 
- *Accept.* Each honest party sends its $\mathsf{accept}$ message once, for $O(n^2\lambda)$ bits in total.
- *Certificates.* By propagation, honest parties accept $b$ in at most two consecutive steps. An honest party sends a $\mathsf{certificate}$ message in a round only if fewer than $\sqrt n$ honest parties do so in the same round, so fewer than $2\sqrt n$ honest parties ever send $\mathsf{certificate}$. Each has at most $n$ signatures and goes to $n$ parties, for $O(n^{2.5}\lambda)$ bits.
- *Data.* Each honest party sends $\mathsf{data}$ messages, which contain $|N(q)|=O(\sqrt n\log n)$ signatures, to each $q$ once, for $O(n^{2.5}\log(n)\lambda)$ bits in total.
- *Forwarding.* Each party forwards each neighbor's $\mathsf{accept}$ message at most once, to $n$ parties, for $O(n^{2.5}\log(n)\lambda)$ bits in total.
  
Summing over the two bits gives $O(n^{2.5}\log(n)\lambda)$ bits. 

#### From $n^{2.5}$ to $n^2$

How do we remove the remaining $\sqrt n$ term? In the protocol above, the convinced parties still *push* their signatures to everyone, through the graph. In the [paper](https://eprint.iacr.org/2026/2504), we shift the responsibility to the parties that are not yet convinced. These parties *pull* the signatures they lack from the parties that announced acceptance. Pulling efficiently against both corrupt senders and corrupt receivers takes a few more ideas: a binary-search procedure that splits the work among the senders, requests that grow gently, and vector commitments to the sender list. Together they bring the communication down to $\widetilde O(n^2)$, for every $t<n$, in $O(t)$ rounds.

Please leave comments on [X](TODO).
