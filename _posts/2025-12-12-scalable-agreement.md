---
title: Scalable Agreement - Near Linear Communication and Constant Expected Time
date: 2025-12-12 06:00:00 -05:00
tags:
- randomness
author: Ittai Abraham
---

Agreement needs quadratic communication and linear time in the worst case. **Scalable Agreement** aims for *near linear communication* and *constant time* in expectation. In this post, we show Scalable consensus against a [weak adaptive adversary](https://decentralizedthoughts.github.io/2019-06-07-modeling-the-adversary/) that can cause **omission failures**. This will be the basis for the Byzantine case that we will explore in future posts.

Previous posts focused on simple randomized protocols that solve consensus for [crash failures](https://decentralizedthoughts.github.io/2023-02-18-rand-and-consensus-1/) and for [omission failures](https://decentralizedthoughts.github.io/2023-02-19-rand-and-consensus-2/) in **constant expected time**. However, those protocols had **quadratic message complexity**. 


### What is the best we can hope for?

Three lower bounds and barriers stand in our way:

1. In the [worst case](https://decentralizedthoughts.github.io/2019-12-15-synchrony-uncommitted-lower-bound/) reaching agreement takes at least $f+1$ rounds. 
    * We will use randomization to reduce the *expected* number of rounds to constant.
2. In the [worst case](https://decentralizedthoughts.github.io/2019-08-16-byzantine-agreement-needs-quadratic-messages/) reaching agreement with no error requires $\Omega(n^2)$ communication. 
    * Assuming a weak adaptive adversary we will reduce the *expected* communication to $O(n \log^\gamma n)$ (for some fixed constant $\gamma$) and in doing so incur a non-zero probability of error (denoted $\delta$).

3. We know that the [best resilience](https://decentralizedthoughts.github.io/2019-11-02-primary-backup-for-2-servers-and-omission-failures-is-impossible/) one can hope for is $f<n/2$. It is not known how to obtain this tight bound with $o(n^2)$ expected communication (see [Ramboud, Theorem 5](https://eprint.iacr.org/2023/1757)).
    *  So we assume some $\epsilon>0$ and obtain *near-optimal* resilience $f<n/(2+\epsilon)$. 

Given this the best we can hope for is following theorem:

***Theorem:*** *there exists a synchronous binary agreement protocol with $\delta$ error that is resilient to a weak adaptive adversary that can cause omission failures to $f<n/(2+\epsilon)$ parties. The expected number of rounds to terminate is constant and the expected communication complexity is $O(n \log^\gamma n)$.*

Specifically, we obtain **super-polynomially small error** $\delta= n^{-O(\log n)}$, **sub linear near optimal resilience** $\epsilon=1/\log n$, and **near linear message complexity** with $\gamma=7$.

This post aims for simplicity and does not optimize the parameter $\gamma$ or explore the full space of options for $\epsilon$ and $\delta$. 

### Main Ideas

Instead of having all parties speak in each round, we will have only a *poly-logarithmic* number of parties speak in each round. This reduces the communication from $O(n^2)$ to $O(n \log^{O(1)} n)$. We will then adopt the analysis of the [previous protocols with constant expected time](https://decentralizedthoughts.github.io/2023-02-19-rand-and-consensus-2/) to work with this subsampling.

Each party will choose a random rank in $[1..n]$ and only parties with rank at most $k=\log^6 n$ will send messages in that round. These elected parties will speak just once. So the weak adaptive adversary cannot predict who will speak in round $j$ before round $j$ starts, and corrupting them after seeing their messages is too late. This paradigm is called *You Only Speak Once* (YOSO) and was first introduced in the context of  [Blockchains by Algorand](https://people.csail.mit.edu/nickolai/papers/gilad-algorand-eprint.pdf) and [MPC by Gentry et al](https://eprint.iacr.org/2021/210).


### Using measure concentration

Fix a round $j$. Each party independently chooses a fresh random rank in $[1..n]$. Define
$$
k=\log^6 n,\qquad \ell = k-\log^4 n,\qquad h = k+\log^4 n.
$$

Let $C=C_j$ be the random set of parties whose rank is at most $k$ in round $j$ and $F$ be the set of parties that are faulty before round $j$. The adversary can corrupt at most $f<n/(2+\epsilon)$ parties with $\epsilon=1/\log n$.

**Lemma 1 (committee size concentration):**

* *Fix $\delta_1=2e^{-\log^2 n/3}=n^{-O(\log n)}$. With probability at least $1-\delta_1$,*
$$
\|C\|\in[\ell,h].
$$

From Lemma 1, with probability $1-\delta_1$ the committee size in round $j$ is in $[\ell,h]$. We next show that, conditioned on this event, the committee contains many parties that are not faulty before round $j$.


Define
$$
q=h-\ell/2.
$$

**Lemma 2 (many non-faulty in the committee):**

* Condition on the event $\mathcal{G}_j$ that $\|C\|\in[\ell,h]$. Then, with probability at least $1-\delta_2$,
$$
\|C\setminus F\|\ge q,$$  

where $\delta_2=\exp(-\Omega(\log^4 n))$.

This means that in round $j$, any party can wait for $q$ round $j$ messages.

Since $q > \|C\|/2$ hold on the same high probability event:

* Any set of at least $q$ round $j$ messages contains at least one message sent by a party in $C\setminus F$.
* Any two sets of at least $q$ round $j$ messages intersect in at least one sender.

These properties will be used repeatedly to obtain probabilistic quorum intersection guarantees.The proofs for both lemmas appear at the end of the post. For convenience, define $\delta=\delta_1+\delta_2$, and note that $\delta=n^{-O(\log n)}$.


### Weak adaptive adversaries

As in the [previous post](https://decentralizedthoughts.github.io/2023-02-18-rand-and-consensus-2/), we need to make sure that the randomness is *unpredictable* and that the adversary can only *adapt* to the randomness when it's too late for it to matter.

Recall the weak adaptive adversary in the lock-step model: If the adversary decides to corrupt a party after seeing the content of its round $j$ message then it can only corrupt it after the party sends all its round $j$ messages to all parties.


### A Near Linear Weak Common Coin against a weak adaptive adversary

A *near linear weak common coin* for round $j$ has the following properties against any weak adaptive minority omission failures:


**Unpredictable**: The coin value for round $j$ cannot be predicted before seeing the round $j$ messages. 

**$\alpha$-correct**: for any $b \in \{0,1\}$, with probability at least $\alpha$, all parties output $b$. In particular, here we will aim for $\alpha =1/5$. Note that a totally fair coin is $\alpha=1/2$.

**Near linear**: the message complexity is $n \log^{O(1)} n$. 

**$\delta$ error liveness**: all non-faulty parties output a coin value with probability $1-\delta$.


The main idea is simple, every party chooses a random rank, and random bit. Only parties with rank at most $k$ send their rank and bit. Parties choose the bit from the *lowest* rank they hear:

```
Each party randomly chooses:
    a rank in [1,...,n]
    a bit in [0,1]
    if rank <= k then
        send (rank,bit) to all parties

Each party that hears q (rank,bit) values:
    outputs the bit associated with the lowest rank it heard
    (break ties arbitrarily)
```

#### Proof for the weak coin

*Unpredictability* holds because the randomness is chosen in round $j$. The weak adaptive adversary can either choose to act before seeing a party's messages - in which case the value is unpredictable, or after seeing its message - in which case its too late.

For *$1/5$-correctness*: let $C_j$ be the set of parties with rank at most $k$ in round $j$. The minimum is unique except with probability at most $O(k^2/n)$, since a tie for the minimum implies that at least two parties picked the same rank in $[1..n]$, and there are at most $k$ ranks that could be the minimum.

Let $E$ be the event that $C_j \in [\ell,h]$, the minimum rank in $C_j$ is unique, and $p$ is not corrupted before round $j$. Since the adversary corrupts fewer than $n/(2+\epsilon)$ parties overall, we have $\Pr[p\ \text{is non-faulty before round}\ j] \ge 1-1/(2+\epsilon) > 1/2$. For sufficiently large $n$, the other two conditions fail with negligible probability, hence $\Pr[E] > 2/5$.

On event $E$, party $p$ sends $(\text{rank},\text{bit})$ in round $j$, and since messages between non-faulty parties are delivered reliably, every non-faulty party receives this message. Because $p$ has the minimum rank, every non-faulty party outputs $p$'s bit. Therefore, for each $b\in\{0,1\}$, with probability at least $\Pr[E]/2 \ge 1/5$, all non-faulty parties output $b$.

For *near linear*: by Lemma 1, in round $j$ only $\|C_j\|=O(\log^6 n)$ parties send, so the total number of messages in the coin round is $O(n\log^6 n)$.


For *$\delta$ error liveness*: conditioned on Lemma 1 and 2, $C_j$ will contain at least $q$ non-faulty members.

### Near Linear Binary agreement from a Near Linear Weak Common Coin

Each party has an input 0 or 1, and the goal is to output a common value (agreement) that is an input value (validity).

We use the same sampling rule in every round: in round $r$, parties with rank at most $k=\log^6 n$ send. Let $C_r$ be the set of parties that speak in round $r$.

Fix any round $r$ and condition on the good event $\mathcal{G}_r$ that Lemma 1 holds for that round, namely $\|C_r\|\in[\ell,h]$. By Lemma 2, with probability at least $1-\delta$ we have $\|C_r\setminus F\|\ge q$. Messages from parties in $C_r\setminus F$ are delivered reliably to all non-faulty parties in round $r$, so every non-faulty party receives at least $q$ round $r$ messages. 

Also under $\mathcal{G}_r$, we have $q > \|C_r\|/2$, so any two sets of at least $q$ round $r$ messages intersect in at least one sender from $C_r\setminus F$. We use this as our probabilistic quorum intersection guarantee.

The protocol runs in *phases*. Each phase consists of 3 *rounds*. 

```
value := input

Round 3j-2:
    Choose a rank in [1,...,n]
    If rank <= k then
       send <value> to all parties
    If fewer than q messages are received then
       shut down
    If all received values are b then
       value := b
    Otherwise
       value := ⊥

Round 3j-1:
    Choose a rank in [1,...,n]
    If rank <= k then
        send <value> to all parties
    If fewer than q messages are received then
       shut down
    If some received value is b and not ⊥ then
       value := b
    If all received values are b and not ⊥ then
       output b

Round 3j:
    Choose a rank in [1,...,n]
    Choose a bit in [0,1]
    If rank <= k then
        send <rank, bit> to all parties
    If fewer than q messages are received then
       shut down
    Let bit be from the lowest rank
    If value = ⊥ then
       value := bit
```

Protocol in words: in the first round, a random subset of parties send their value and all parties either keep their value or switch to $\bot$ if they hear a conflict. In the second round, a random subset of parties send their value again. This time parties stay with $\bot$ only if they don't hear value, and they output a bit if all received values are identical and not $\bot$. Finally, in the third round, parties that end with $\bot$ use the weak coin protocol to obtain a new value.



### Proof for the Agreement protocol

**Validity**: assume all parties start with input $b$. Condition on $\mathcal{G}_{1}$ and $\mathcal{G}_{2}$. In round $1$, every non-faulty party receives at least $q$ messages, and all values received are $b$, so every non-faulty party sets its value to $b$. In round $2$, again every non-faulty party receives at least $q$ messages, all equal to $b$, so every non-faulty party outputs $b$.


**No split values after round $3j-2$**: fix a phase $j$ and condition on $\mathcal{G}_{3j-2}$. Suppose some non-faulty party ends round $3j-2$ with value $b\in\{0,1\}$ (not $\bot$). Then it received at least $q$ messages in round $3j-2$, all equal to $b$. Any other non-faulty party that reaches the end of round $3j-2$ also received at least $q$ messages in that round. Since $q>\|C_{3j-2}\|/2$, the two size-$q$ sender sets intersect in at least one sender from $C_{3j-2}\setminus F$, and that sender sent value $b$ to all parties. Therefore the second party received at least one message with value $b$ and cannot end round $3j-2$ with value $1-b$.

We conclude that there exists a bit $b\in\{0,1\}$ such that every party that starts the coin round $3j$ has a value in $\{b,\bot\}$.

**Agreement**: let $j^\star$ be the first phase in which some non-faulty party outputs a value at the end of round $3j^\star-1$, and let this value be $b$. Condition on $\mathcal{G}_{3j^\star-1}$. The deciding party received at least $q$ messages in round $3j^\star-1$, all equal to $b$. Any other non-faulty party that reaches the end of round $3j^\star-1$ also received at least $q$ messages in that round, and since $q>\|C_{3j^\star-1}\|/2$ their sender sets intersect in at least one sender from $C_{3j^\star-1}\setminus F$, so it received at least one message with value $b$. Hence any party that enters the next phase has value $b$. In the next phase, conditioned on $\mathcal{G}_{3(j^\star+1)-2}$ and $\mathcal{G}_{3(j^\star+1)-1}$, an argument similar to the validity above implies that all non-faulty parties output $b$ by the end of round $3(j^\star+1)-1$.


**Expected Termination**: fix a phase $j$ and condition on the good events $\mathcal{G}_{3j-2}$ and $\mathcal{G}_{3j-1}$. If no party outputs a value by the end of round $3j-1$, then by the previous claim there exists a bit $b$ such that every non-faulty party starts the coin round $3j$ with value in $\{b,\bot\}$. In the coin round, the weak coin is $\alpha$-correct with $\alpha\ge 1/5$, so for this particular bit $b$ we have that with probability at least $1/5$ all non-faulty parties output coin value $b$. Parties with value $\bot$ adopt the coin bit, so at the end of round $3j$ all non-faulty parties have value $b$. In the next phase, conditioned on $\mathcal{G}_{3(j+1)-2}$ and $\mathcal{G}_{3(j+1)-1}$, an argument similar to the validity above implies that all non-faulty parties output $b$ by the end of round $3(j+1)-1$. Therefore, each phase leads to a decision with constant probability, so the expected number of phases, and hence rounds, to decide is constant.

**Message complexity**: in each round $r$, only the committee $C_r$ sends messages, and each sender broadcasts to all $n$ parties, so the number of messages in round $r$ is $n\cdot \|C_r\|$. Conditioned on $\mathcal{G}_r$, Lemma 1 gives $\|C_r\|\in[\ell,h]=\Theta(\log^6 n)$, hence the message complexity per round is $\Theta(n\log^6 n)$. In the agreement rounds, each message carries a constant size value, so the bit complexity per agreement round is $\Theta(n\log^6 n)$. In the coin round, each sender also includes a rank in $[1..n]$, which costs $\Theta(\log n)$ bits, so the bit complexity of the coin round is $\Theta(n\log^6 n\log n)$. Over a constant expected number of phases, the expected total communication is $O(n\log^\gamma n)$ for $\gamma=7$.

### Proofs for measure concentration lemmas

**Proof of Lemma 1**:

Let $K$ be the random variable that counts the number of parties that have rank at most $k$. Then $K$ is binomial with $\Pr[\text{rank} \le k]=k/n$, and from linearity of expectation, $E[K]=\mu=\log^6 n$.

For simplicity, we apply measure concentration via a generic two sided [Chernoff bound](https://math.mit.edu/~goemans/18310S15/chernoff-notes.pdf). For $0<\beta<1$:


$$
Pr[\|K-\mu\| \geq \beta \mu] \leq 2 e^{-\mu \beta^2/3}
$$

Taking $\mu=\log^6 n$ and $\beta = \log^{-2} n$ we get $\beta\mu=\log^4 n$ and $\mu\beta^2=\log^2 n$, hence:

$$
Pr[\|K-\mu\| \geq \log^4 n] \leq 2e^{-\log^2 n /3} = n^{-O(\log n)}
$$

This concludes the proof with $\delta_1=2e^{-\log^2 n /3} = n^{-O(\log n)}$. Here $\log$ is the natural logarithm, changing the base only affects constants.

We will apply this lemma a polynomially bounded number of times, so even when we union bound over all applications we get an error of $\delta = n^{-O(\log n)}$.

**Proof of Lemma 2**: 

Condition on $\|C\|=m\in[\ell,h]$ and on the set $F$ of parties corrupted before round $j$. Since ranks in round $j$ are fresh and independent, $C$ is a uniform size-$m$ subset of $[n]$.

Let $X=\|C\cap F\|$ be the number of faulty parties in $C$. Since $C$ is sampled uniformly without replacement, $X$ is hypergeometric with
$\mu = E[X\mid m] = m\cdot\frac{\|F\|}{n} \le \frac{m}{2+\epsilon}$.

We must show $X \le m-q$. The worst case is $m=\ell$, in which case
$m-q = 3\ell/2-h = \frac{k}{2}-\frac{5}{2}\log^4 n =: T$.

With $\epsilon=1/\log n$,
$\mu \le \frac{\ell}{2+\epsilon} = \frac{k}{2}-\Theta(\log^5 n)$.
Thus, $T=(1+\alpha)\mu$ for some $\alpha=\Theta(1/\log n)$. Using an upper-tail Chernoff bound,
$\Pr[X\ge T] \le \exp(-\Omega(\mu\alpha^2)) = \exp(-\Omega(\log^4 n))$.

Therefore, conditioned on $\|C\|\in[\ell,h]$, with probability at least $1-\delta_2$, we have $X\le m-q$, equivalently $\|C\setminus F\|\ge q$.


Your thoughts on [Twitter]().
