---
title: Flavours of Broadcast
date: 2019-10-22 10:44:00 -04:00
author: Ittai Abraham
background:
  - /2019-06-27-defining-consensus/
  - /2019-06-01-2019-5-31-models/
continue_reading:
  - /2022-06-19-crusader-braodcast/
  - /2022-06-09-phase-king-via-gradecast/
---

What is the difference between broadcast, crusader broadcast, gradecast, weak broadcast, detectable broadcast, and broadcast with abort? This post is a follow up to our basic post on: [What is Broadcast?](https://decentralizedthoughts.github.io/2019-06-27-defining-consensus/)

The focus of this post is on [computationally unbounded adversaries](https://decentralizedthoughts.github.io/2019-06-07-modeling-the-adversary/) in the [synchronous model](https://decentralizedthoughts.github.io/2019-06-01-2019-5-31-models/), but we begin with considering both bounded and unbounded adversaries for the (classic) Broadcast problem. 

### Broadcast

Let's start by defining the basic *Broadcast problem* again. We assume a set of $n$ parties. One party is designated as being called the *sender*. We assume the sender has some initial *value*.

A protocol solves the (classic) **broadcast** problem:
1. **Agreement**: If an honest party outputs $x$, then all honest parties output $x$.
2. **Validity**: If the sender is honest, then all honest parties output the sender's value.

Assuming a PKI and a [computationally bounded](https://decentralizedthoughts.github.io/2019-06-07-modeling-the-adversary/) adversary, the [Dolev-Strong](https://www.cs.huji.ac.il/~dolev/pubs/authenticated.pdf) Broadcast protocol solves Byzantine broadcast assuming an adversary that can control up to $n−1$ parties out of $n$ in the Synchronous model.

For computationally unbounded adversaries the [FLM lower bound](https://decentralizedthoughts.github.io/2019-08-02-byzantine-agreement-is-impossible-for-$n-slash-leq-3-f$-is-the-adversary-can-easily-simulate/) shows that broadcast is possible only when $n>3f$.

So for computationally unbounded adversaries, it is natural to ask *are there relaxations of the broadcast problem that circumvent the $n\leq 3f$ lower bound?* 


### Weak Broadcast and Detectable Broadcast

If we keep the agreement property and relax the validity property we arrive at the classic weak Byzantine Broadcast problem of [Lamport from 1984](https://zoo.cs.yale.edu/classes/cs426/2014/bib/lamport83theweak.pdf). 

A protocol solves the **weak broadcast** problem:
1. **Agreement**: If an honest party outputs $x$, then all honest parties output $x$.
2. **Weak Validity**: If the sender is honest, then all honest parties output either sender's value or *⊥*.
3. **Non-triviality**: If all parties are honest, then all parties output the sender's value.
 
Note on lower bounds: [Fischer, Lynch, and Merritt](https://groups.csail.mit.edu/tds/papers/Lynch/FischerLynchMerritt-dc.pdf) show that weak broadcast is impossible for deterministic protocols for $n \leq 3f$. 

For randomized protocols [Karlin and Yao 1984, unpublished](http://www.math.ucsd.edu/~ronspubs/89_08_byzantine.pdf) show that Broadcast must have a constant (more than $1/3$) error probability for $n\leq 3f$.  

This lower bound for randomized protocols does not hold for weak Broadcast. Using randomization and private channels, [Fitzi, Gisin, Maurer, and von Rotz 2002](https://iacr.org/archive/eurocrypt2002/23320478/qbc.pdf
) strengthen Weak Broadcast to a notion of *Detectable Broadcast* that also provides a stronger notion of fairness that is important for SMPC. They show that it is possible to solve weak broadcast for $n>2f$ with just a [negligible error probability](post on security definitions).

[Fitzi, Gottesman, Hirt, Holenstein, and Smith 2002](https://groups.csail.mit.edu/tds/papers/Smith-Adam/fghhs-PODC2002-new-final.pdf) improve this bound to $n>f$ again with just a [negligible error probability](post on security definitions).



### Crusader Broadcast and Gradecast

An alternate way to relax the broadcast problem is to keep the validity property and relax the agreement property. This gives us the **Crusader broadcast** of [Dolev 1981](http://infolab.stanford.edu/pub/cstr/reports/cs/tr/81/846/CS-TR-81-846.pdf).

A protocol solves the **crusader broadcast** problem:
1. **Weak Agreement**: If an honest party outputs x, then all honest parties output either x or ⊥.
2. **Validity**: If the sender is honest, then all honest parties output the sender's value.


See [this post](https://decentralizedthoughts.github.io/2022-06-19-crusader-braodcast/) for Crusader Boardcast with $O(n^2)$ words and $O(1)$ rounds, for any $f<n$ given a PKI.

[Feldman and Micali 1988, 1997](https://people.csail.mit.edu/silvio/Selected%20Scientific%20Papers/Distributed%20Computation/An%20Optimal%20Probabilistic%20Algorithm%20for%20Byzantine%20Agreement.pdf) strengthened the definition of crusader agreement so the output of the protocol is *both* a decision value and a $grade \in \{0,1,2\}$.

A protocol solves the **Gradecast** problem:
1. **Knowledge of Agreement**: If an honest party outputs x with grade 2 then all honest parties output $x$ with $grade \in \{1,2\}$.
2. **Weak Agreement**: If an honest party outputs x, then all honest parties output either x or ⊥.
3. **Validity with knowledge**: If the sender is honest, then all honest parties output the sender's value with grade $2$.

Gradecast [and its variants](https://eprint.iacr.org/2006/065.pdf) are very important building blocks in many MPC and Byzantine Agreement protocols.

Note on lower bounds for adversaries that can simulate (for example computationally unbounded adversaries): impossibility for $n\leq 3f$ for deterministic protocol was shown by [Dolev 1982](https://www.cse.huji.ac.il/~dolev/pubs/byz-strike-again.pdf). For randomized protocols, even a small constant error is impossible. This extension of the FLM lower bound to crusader agreement is folklore and was first mention by [Goldwasser and Lindell, 2002](https://eprint.iacr.org/2002/040.pdf), see [this post](https://decentralizedthoughts.github.io/2021-10-04-crusader-agreement-with-dollars-slash-leq-1-slash-3$-error-is-impossible-for-$n-slash-leq-3f$-if-the-adversary-can-simulate/) for more details.


### Broadcast with Abort

If we relax both Agreement and Validity we obtain the notion of *Broadcast with abort* of [Goldwasser and Lindell](https://eprint.iacr.org/2002/040.pdf), [2002](http://groups.csail.mit.edu/cis/pubs/shafi/2002-disc.pdf).



A protocol solves the **Broadcast with abort** problem:
1. **Weak Agreement**: If an honest party outputs x, then all honest parties output either x or ⊥.
2. **Weak Validity**: If the sender is honest, then all honest parties output either sender's value or ⊥.
3. **Non-triviality**: If all parties are honest, then all parties output the sender's value.

Goldwasser and Lindell show that this relaxation can be solved even if the adversary controls $n-1$ parties out of $n$. The solution is a natural two-round protocol and obtains [perfect security](post on security definitions). Here is the protocol for Broadcast with abort:

1. The sender sends $x$ to all parties.
2. Denote by $x_i$ the value received by party $i$ from the sender in the previous round. If $i$ did not receive a value from the sender in the first round, then it sets $x_i = ⊥$. Then, every party $i$ (for $i > 1$) sends its value $x_i$ to all other parties.
3. Denote the value received by $i$ from $j$ in the previous round by $x_{i,j}$ Then, $i$ outputs $x_i$ if this is the only
value that it saw ($\forall i>1: x_i=x_{i,j}$). Otherwise, it
outputs $⊥$.


### Notes

Many of the results of this post have been extended to Secure Multi Party Computation. More on that in later posts.


Please leave comments on [Twitter](https://twitter.com/ittaia/status/1186630509931184134?s=20)




















