---
title: 2-round BFT in Simplex style for n=5f-1
date: 2025-08-06 00:00:00 -04:00
tags:
- consensus
- BFT
author: Ittai Abraham and Ling Ren
---

In our [previous post](https://decentralizedthoughts.github.io/2025-07-18-two-round-Simplex/), we described a 2-round [partially synchronous](https://decentralizedthoughts.github.io/2019-06-01-2019-5-31-models/) BFT protocol for $n = 5f+1$. In this follow-up post, we **push the bound to $n = 5f-1$**, achieving [optimal 2-round commit](https://decentralizedthoughts.github.io/2021-02-28-good-case-latency-of-byzantine-broadcast-a-complete-categorization/) in the [Simplex style](https://decentralizedthoughts.github.io/2025-06-18-simplex/). 


We then extend the result to $n=3f+2p-1$ for $0<p\leq f$ that obtains liveness for $p$ Byzantine. This can be used to obtain a [concurrent 2 round and 3 round protocol](https://decentralizedthoughts.github.io/2025-07-29-2-round-3-round-simplex/) with the optimal fault tolerance.


## Intuition

A party commits a value $x$ after receiving $n-f$ votes for $x$.  
We want to understand what evidence remains for the other honest parties if some honest party commits $x$ and then becomes unavailable due to network asynchrony.

Let $n = 5f-1$ where $f$ is the maximum number of Byzantine faults.

* $n-f = 4f-1$ votes are needed for commit.
* Among these, at least $n-2f = 3f-1$ are honest votes.
* Any other honest party waiting for $n-f$ votes will see at least $n-3f = 2f-1$ votes for $x$.

This leads to two cases.

1. If the leader does not equivocate, then every honest party that did not vote for $x$ must vote for $\bot$. So another honest party sees at least $2f-1$ votes for $x$, and the remaining votes can be viewed as votes for $\bot$. This motivates a **special certificate** for $x$: $2f-1$ votes for $x$ together with $2f$ votes for $\bot$.

2. If the leader does equivocate, then a party that detects equivocation ignores the leader's vote and waits for one more vote. Now it looks at $4f$ non-leader votes. Among them, at least $n-3f+1 = 2f$ are for $x$, while there can be at most $2f-1$ non-$x$ votes: at most $f$ honest parties may have received a conflicting proposal, and at most $f-1$ non-leader Byzantine parties may equivocate. So the party can favor $x$. This motivates a **regular certificate** for $x$: $2f$ votes for $x$.

Define a **skip certificate** as $2f+1$ votes for $\bot$. A commit in a view implies at least $n-2f$ honest votes for some $x$, so a skip certificate cannot form in the same view.

---

## Two-round Simplex protocol for $n=5f-1$

Let `Cert(k, x)` denote a collection of votes for $x  \neq \bot$ in view $k$ sufficient to certify $x$:

* $2f$ votes for $x$ (regular cert), or
* $2f-1$ votes for $x$ and $2f$ votes for $\bot$ (special cert).

Let `Cert(k, bot)` denote a collection of $2f+1$ votes for $\bot$ in view $k$.

Once we define the certs above (with modified thresholds and the special cert), the protocol is actually unchanged from the [previous post](https://decentralizedthoughts.github.io/2025-07-18-two-round-Simplex/). 

```
1. Upon entering view k:
    Start local timer T_k
    Leader sends (Propose, k, x, Cert(k’, x)) for highest k’

2. Upon receiving (Propose, k, x, Cert(k’, x)) 
        and Cert(l, bot) for all k' < l < k and has not sent Vote
    Send (Vote, k, x) 

3. Upon T_k = 2Δ and has not sent Vote
    Send (Vote, k, bot) 

4. Upon receiving n-f (Vote, k, x)
    Decide x
    Forward these votes
    Terminate

5. Upon receiving n-f (Vote, k, *), but no Cert(k, x)
    Send (Vote, k, bot) 

6. Upon receiving Cert(k, *) and has sent Vote
    Forward Cert(k, *)
    Enter view k+1
```



## Two-round Simplex protocol for $n=3f+2p-1$ where $0<p\leq f$

We now extend the protocol to $n=3f+2p-1$, obtaining safety against $f$ Byzantine faults and liveness when at most $p$ parties are Byzantine. A commit now requires $n-p=3f+p-1$ votes, of which at least $2f+p-1$ are honest. Therefore, any other honest party waiting for $n-f$ votes sees at least $f+p-1$ votes for the committed value. If equivocation is detected, the party can again wait for one more vote.

This leads to three natural changes to the protocol:

A. `Cert(k, x)` is a collection of votes for $x  \neq \bot$ in view $k$ sufficient to certify $x$:

* $f+p$ votes for $x$ (regular cert), or
* $f+p-1$ votes for $x$ and $f+p$ votes for $\bot$ (special cert).

B. `Cert(k, bot)` is a collection of $f+p+1$ votes for $\bot$ in view $k$.

C. The commit rule requires $n-p$ votes:

```
4. Upon receiving n-p (Vote, k, x):
    Decide x;
    Forward these votes;
    Terminate
```


Finally, to obtain a [concurrent 2 round and 3 round protocol](https://decentralizedthoughts.github.io/2025-07-29-2-round-3-round-simplex/) with $n=3f+2p-1$, the quorum size for the 3-round path needs to be $n-(f+p-1)=2f+p$ so that two such quorums intersect in at least $f+1$ parties.


## Proof Sketches

The proof sketches below refer to the generalized $n=3f+2p-1$ protocol above.

**Lemma 1 (Safety)**:
If an honest party commits $x$ in view $k$, all honest parties eventually obtain a cert for $x$.

*Proof sketch*: A commit requires $n-p = 3f+p-1$ votes for $x$, of which at least $2f+p-1$ are honest. Any other honest party gathering $n-f$ votes will see at least $f+p-1$ votes for $x$.  

If equivocation is detected, it waits for $n-f+1 = 3f+p$ votes and sees at least $f+p$ for $x$, which dominates any conflicting votes ($\le f+p-1$).

If no equivocation is detected, it sees exactly $f+p-1$ votes for $x$, then the remaining $f+p$ votes are for $\bot$, so a special cert is formed. If $f+p$ votes or more arrive for $x$, then a regular cert is formed.


**Lemma 2 (No-commit detection)**:  
If no honest party commits in view $k$, all honest parties eventually see either a `Cert(k, x)` or a `Cert(k, bot)`.

*Proof sketch*:  If a certificate for some $x$ exists, it is forwarded.  If no certificate exists, by the fifth `Upon` rule all honest parties eventually vote $\bot$, forming a `Cert(k, bot)`.


**Lemma 3 (Liveness)**:  
If the leader of some view $k$ is honest and GST has occurred, all honest parties commit in view $\le k$.

*Proof sketch*: If a commit already occurs in a prior view, the commit certificate is forwarded. Otherwise, all honest parties eventually vote for the honest leader in view $k$, producing $n-p$ votes and committing.


## Acknowledgments

This work is done in part during the authors' visits to a16z Crypto Research. The authors thank Yuval Efron and Kartik Nayak for insightful discussions. We thank Brendan Kobayashi Chou, Andrew Lewis-Pye, Patrick O'Grady for spotting a liveness error in a previous version. 


Your thoughts/comments on [X](https://x.com/ittaia/status/1954109234917883985).
