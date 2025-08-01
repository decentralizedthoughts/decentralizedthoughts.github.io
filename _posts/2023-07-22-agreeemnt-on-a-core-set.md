---
title: Asynchronous Agreement on a Core Set
date: 2023-07-22 08:00:00 -04:00
tags:
- consensus
- asynchrony
author: Gilad Stern, Ittai Abraham
---

A challenging step in many *asynchronous* protocols is agreeing on a set of parties that completed some task. For example, an asynchronous protocol might start off with parties [reliably broadcasting](https://decentralizedthoughts.github.io/2020-09-19-living-with-asynchrony-brachas-reliable-broadcast/) a value. Due to asynchrony and having $\leq f$ corruptions, honest parties can only wait for $n-f$ parties to complete the task.
Parties may need to **agree** on a core set of $n-f$ such broadcasts and use them in the next rounds. This is challenging because in asynchrony, some parties may see that a given party completed its task very early, while other parties may see this much later. 

In *asynchronous secure multi party computation* (MPC) parties need to agree on a set of at least $n-f$ parties whose input value (often shared using *verifiable secret sharing* (VSS)) is used to compute the desired functionality. The task of agreeing on a set of parties that completed a task was called **agreement on a core set**, or **ACS**, in 1993 by Ben-Or, Canetti, and Goldreich [BCG93](https://dl.acm.org/doi/pdf/10.1145/167088.167109).
 
ACS is similar to [gather](https://decentralizedthoughts.github.io/2021-03-26-living-with-asynchrony-the-gather-protocol/). In *gather*, parties output sets that *include* the same common core of size $n-f$ of parties that completed a task, but parties don't know which of their output values are in the common core and which aren't (so gather does not implement agreement directly). In ACS parties all agree on the same common core set.

We start by defining ACS, then show the canonical construction from 1994 by Ben-Or, Kelmer, and Rabin, [BKR94](https://dl.acm.org/doi/pdf/10.1145/197917.198088).

### Modeling the validation of asynchronous leader based tasks

We want to model the successful completion and validation of a leader based task using a generic *asynchronous validity function* (also called a [dynamic predicate](https://dl.acm.org/doi/pdf/10.1145/197917.198088)). For example, party $i$ may want to evaluate the statement "I've accepted leader $j$'s broadcast and its content is valid". Note that this condition is a function of the current state of party $i$, not necessarily just a function of the messages that party $j$ sent to party $i$. At any point in time, different parties might have different opinions about the validity of party $j$. 

To formally model this, assume each party $i$ has access to an asynchronous validity predicate $valid_i(j)$ for each leader $j$. This predicate takes the full state of party $i$ and outputs $1$ if the input is currently *valid* and $0$ if it is not currently valid. In the above example, $valid_i(j)$ would equal $1$ if $i$ heard $j$ complete its reliable broadcast and $0$ otherwise.

An *asynchronous validity predicate* has the following properties:

* **Finality:** If party $i$ is honest and $valid_i(j)=1$ at time $t$, then for any time $t'>t$, $valid_i(j)$ at time $t'$.
* **Eventual consistency:** If party $i$ is honest and $valid_i(j)=1$, then for any honest party $k$ eventually $valid_k(j)=1$ as well.
* **Eventual liveness:** If party $j$ is honest, then for any honest party $i$ eventually $valid_i(j)=1$.

### Agreement on a Core Set

Given an asynchronous validity predicate, $valid_i(j)$, a protocol solving ACS has each party $i$ output a set $S_i \subseteq [n]$ with the following properties:

* **ACS Validity:** If an honest party $i$ outputs $S_i$, then $\|S_i\|\geq n-f$ and eventually $valid_i(j)=1$ for every $j\in S_i$.
* **Agreement.** Honest parties output the same set $S$ from the protocol.
* **Termination.** All honest parties eventually complete the protocol and output a set.

ACS is a an important building block, used in asynchronous BFT protocols (example [here](https://www.shoup.net/papers/ckps.pdf) and [here](https://eprint.iacr.org/2016/199.pdf)), asynchronous [DKG protocols](https://eprint.iacr.org/2021/1591.pdf), and of course asynchronous [MPC protocols](https://crypto.ethz.ch/publications/files/BeeHir07.pdf). 

Note that some of the choices above are somewhat arbitrary. We could have also chosen to agree on a $S\subseteq V$ for a general $V$, and not only on indices in $[n]$. We could have also generalized the size of the set to be $k$ and not necessarily $n-f$ (and we would need to also assume that parties are guaranteed to have at least $k$ valid values). Since the case of agreeing on $n-f$ "good" parties is so ubiquitous we focus on this task with these parameters.

## BKR94's ACS Construction

As a core part of their asynchronous MPC work, BKR constructed an elegant ACS protocol that uses at most $n$ instances of [asynchronous binary agreements](https://decentralizedthoughts.github.io/2022-04-05-aa-part-five-ABBA/).

In an *asynchronous binary agreement protocol*, each party has either $0$ or $1$ as input. Parties need to reach **agreement** on the same bit $b$. In addition to outputting the same bit, **validity:** if all honest parties have the same input $b$, they must output $b$ from the protocol. Moreover, **termination** is guaranteed if all honest parties start the protocol, or if any honest terminates.

The construction works by agreeing, for each party $j$, whether to include it in the output of the ACS protocol. Denote $BA_j$ when referring to the instance of the binary agreement protocol used for agreeing on whether to add party $j$ to the set. 

Party $i$'s protocol:

```
wait := 1

Upon seeing valid_i(j) = 1 and wait = 1, 
    start BA_j with input 1

Upon seeing n-f instances of BA complete with input 1,
    wait := 0
    start all un-started BA instances with input 0
    
Upon completing all BA instances,
    output the set S_i of parties whose BA_j had output 1
```

### Proof of BKR94's ACS protocol

**Agreement:** Follows directly from the agreement property of each binary agreement.

**Termination:**

If all honest parties eventually set ```wait := 0```, then all BA instances will eventually have all honest inputs. From the termination property of each BA instance, the ACS protocol will terminate.

So we need to prove that all honest parties eventually set ```wait := 0```. Seeking a contradiction, there are two cases to consider:

1. Some honest party $i$ sets ```wait := 0```, but another honest party never does. So party $i$ saw at least $n-f$ BA instances output 1, hence from the agreement and termination properties of the BA instances, all parties will eventually see at least $n-f$ BA instances output 1, and this will trigger ```wait := 0```. Hence a contradiction. 
We note that this proof can be extended even to the case that the termination condition of the BA holds only if all honest participate.
3. No honest party sets ```wait := 0```. In that case, due to the eventual liveness property and the validity property of the binary agreement, all $BA$ for honest parties will eventually output 1 and this will trigger ```wait := 0```. Hence a contradiction. 

**ACS Validity:**

1. If an honest party $i$ outputs $1$ for $BA_j$, then from the validity property of the binary agreement it cannot be the case that all honest parties start $BA_j$ with input 0. Hence some honest party $k$ had $valid_k(j)$. From the eventual consistency property, party $i$ will eventually have $valid_i(j)$.
2. To show $\|S_i\| \geq n-f$ consider the first party to set ```wait := 0``` (see termination for why this is not empty). At that point, there are at least $n-f$ BA instances that ended with 1. Hence from the agreement property of the binary agreement, all parties will see at least $n-f$ BA instances with 1.

Note on termination: it is easy to require a slightly stronger termination condition, where $valid_i(k)=1$ holds for every $k\in S_i$ at the time of termination by waiting for that event before outputting a value (follows from the eventual consistency property).

### BKR94's ACS Round Complexity

{: .box-note}
TLDR: the expected round complexity of the BKR ACS is $O(\log n)$.

Recall that the number of rounds of an execution is the total time till termination divided by the longest message delay. The expected round complexity of a protocol is the maximum over all adaptive adversary strategies, of the expected round complexity, where the expectation is taken over the honest parties' random coins. See [this post](https://decentralizedthoughts.github.io/2021-09-29-the-round-complexity-of-reliable-broadcast/) (or this [one](https://decentralizedthoughts.github.io/2022-03-30-asynchronous-agreement-part-one-defining-the-problem/)) for how to formally measure round complexity of an asynchronous protocol.


Ben-Or and El-Yaniv make the following observation in [their paper](https://csaws.cs.technion.ac.il/~rani/papers/interactive-consistency.pdf) from 2003:

**Observation:** Let $X_1,X_2,\dots,X_n$ be independent random variables such that for every $i, \Pr[X_i > j] =q^j$ (for some $0<q<1$). If $Y=\max\{X_i\}$, then $E[Y]= \Theta(\log n)$.

Indeed, the most efficient binary $BA$ protocols that we are aware of have round complexities distributed like the $X_i$ variables described above. While for each $i$, the expected round complexity is constant, $E(i)=O(1)$, the ACS protocol terminates only when the **last** BA instance terminates. This means, that the round complexity of the ACS protocol is $Y=\max\{X_i\}$, so the expected round complexity for all instances to terminate is $E[Y]= \Theta(\log n)$.

### Message Complexity

The protocol requires running $n$ instances of binary byzantine agreement for an expected $\log n$ rounds. If each round of each takes $f(n) = \Omega(n^2)$ messages, then this is $O(f(n) n \log n) = \Omega(n^3 \log n)$

### Getting ACS with a constant expected number of rounds

We do not know how to get $O(1)$ expected round complexity using a linear number of binary agreements in the information theoretic setting and it seems that the observation above is a natural barrier when using a linear number of independent binary agreement instances.

We note that back in 1994, BKR94 did claim that using techniques of Ben-Or and El-Yaniv (BOEY03) it is possible to get $O(1)$ expected round complexity. However, the [2003 paper](https://csaws.cs.technion.ac.il/~rani/papers/interactive-consistency.pdf) from Ben-Or and El-Yaniv does not mention ACS at all. Moreover,  while BOEY03 solves several important multi-valued agreement problems, we are not aware of any direct way to use them to solve ACS.

In the next post, we will show how to use a single instance of multi-valued asynchronously validated agreement protocol to get to the asymptotically optimal $O(1)$ expected time.

Your thoughts and comments on [Twitter](https://twitter.com/ittaia/status/1682847063132741632?s=20).


