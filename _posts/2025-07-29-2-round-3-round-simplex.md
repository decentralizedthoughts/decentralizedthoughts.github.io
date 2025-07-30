---
title: Concurrent 2-round and 3-round BFT in Simplex style
date: 2025-07-29 00:00:00 -04:00
published: false
tags:
- consensus
- BFT
author: Ittai Abraham, Yuval Efron, Kartik Nayak, and Ling Ren
---

In the last two posts, we presented two partially synchronous BFT protocols in the [Simplex style](https://eprint.iacr.org/2023/463.pdf): a [3-round protocol](https://decentralizedthoughts.github.io/2025-06-18-simplex/) with $n\geq3f+1$ and a [2-round protocol](https://decentralizedthoughts.github.io/2025-07-18-two-round-Simplex/) with $n\geq 5f+1$. In this post, we describe a protocol that runs a 2-round commit rule and a 3-round commit rule concurrently. 

A new parameter $p$ ($0 \leq p \leq f$) is introduced and the goal is to design protocols that have $n \geq 3f+2p+1$ parties and the following properties:

- Safety and liveness in the presence of $f$ Byzantine parties;
- If the leader is honest, the network is synchronous (GST=0), and at most $f$ parties are Byzantine, then all honest parties commit in 3 rounds; and
- If the leader is honest, the network is synchronous (GST=0), and at most $p$ parties are Byzantine, then all honest parties commit in 2 rounds. 

To our knowledge, such protocols were first proposed in [FaB](https://ieeexplore.ieee.org/document/1467815) and [Zyzzyva](https://dl.acm.org/doi/10.1145/1658357.1658358) around 2005. Those initial protocols [had safety and liveness errors](https://arxiv.org/abs/1712.01367) that were later [fixed](https://arxiv.org/pdf/1801.10022) (and implemented in [SBFT](https://arxiv.org/pdf/1804.01626)). Recently, there has been increased interest in this line of research with [Banyan](https://arxiv.org/pdf/2312.05869), [Kudzu](https://arxiv.org/abs/2505.08771), and [Alpenglow](https://www.anza.xyz/alpenglow-1-1) that gave [Simplex](https://simplex.blog/)-inspired variants.


In this post, we describe a natural Simplex-style protocol achieving the above guarantees. Our approach is simply to merge the 3-round and 2-round protocols from our last two posts with virtually no additional modifications. 


## 2 round $n=5f+1$ recast to $n=3f+2p+1$

To start, here is the $n=5f+1$ protocol, adapted to $n=3f+2p+1$ to obtain safety for up to $f$ Byzantine faults and liveness assuming up to $p$ Byzantine and an honest leader. The only changes are that the commit quorum size becomes $n-p$, and the certificate size becomes $n-p-2f$. (See our [last post](https://decentralizedthoughts.github.io/2025-07-18-two-round-Simplex/) for why the certificate size should be $2f$ less than commit quorum size.) 




```
2-round commit BFT

1. Upon entering view k: 
    Everyone starts a local timer T_k 
    Leader sends (Propose, k, x, Fast-Cert(k’, x)) for the highest k’ 
    
2. Upon received (Propose, k, x, Fast-Cert(k’, x)) and Fast-Cert(l, bot) for all k' < l < k and has not sent Vote 
    Send (Vote, k, x) to all     // Denote n-2f-p (Vote, k, x) as Fast-Cert(k, x)  

3. Upon T_k = 2 Δ and has not sent Vote
    Send (Vote, k, bot) to all   // Denote n-2f-p (Vote, k, bot) as Fast-Cert(k, bot) 

4. Upon receiving n-p (Vote, k, x)   // Monitored even after exiting view k
    Decide x 
    Forward these n-p (Vote, k, x)
    Terminate 

5. Upon receiving n-f (Vote, k, *) but no Fast-Cert(k, x) for any x 
    Send (Vote, k, bot) to all

6. Upon receiving Fast-Cert(k, *) 
    Forward Fast-Cert(k, *) 
    Enter view k+1 if in view k  
```


## 3 round $n=3f+1$ recast to $n=3f+2p+1$

Now here is the $n=3f+1$ protocol, adopted to $n=3f+2p+1$ to obtain safety and liveness for $f$ Byzantine. The only change is that the quorum size is reduced from $n-f$ to $n-f-p$, because now two quorums of $n-f-p$ intersect at $2(n-f-p)-n \geq f+1$.


```
3-round commit BFT


1. Upon entering view k: 
    Everyone starts a local timer T_k 
    Leader sends (Propose, k, x, Slow-Cert(k’, x)) for the highest k’ 
    
2. Upon received (Propose, k, x, Slow-Cert(k’, x)) and Slow-Cert(l, bot) for all k' < l < k and has not sent Vote 
    Send (Vote, k, x) to all     // Denote n-f-p (Vote, k, x) as Slow-Cert(k, x)  

3. Upon receiving n-f-p (Vote, k, x)   // Monitored even after exiting view k
    Send (Final, k, x) to all     
    
4. Upon T_k = 3 Δ; and has not sent Final
    Send (Final, k, bot) to all   // Denote n-f-p (Final, k, bot) as Slow-Cert(k, bot) 

5. Upon receiving n-f-p (Final, k, x)   // Monitored even after exiting view k
    Decide x 
    Forward these n-f-p (Final, k, x)
    Terminate 

6. Upon receiving Slow-Cert(k, *) 
    Forward Cert(k, *) 
    Enter view k+1 if in view k  
```


## Merged 2-round and 3-round 

Let's merge the 2-round and 3-round protocols for $n=3f+2p+1$. Note that the merge is seamless in that all the certificates remain exactly as in their original protocols above:

* $n-f-p$ votes is a slow cert
* $n-f-p$ finals of ⊥ is a slow cert of ⊥
* $n-2f-p$ votes is a fast cert
* $n-2f-p$ votes of ⊥ is a fast cert of ⊥
* $n-p$ votes is a fast commit
* $n-f-p$ finals is a slow commit
 
Two important aspects of the merge:

* We order certificates first by view and then by **Fast < Slow**. For example, a proposal in view 4 with Fast-Cert(2,x) would be voted for if Slow-Cert(2,⊥), Fast-Cert(3,⊥), Slow-Cert(3,⊥) exist. While voting for a proposal in view 4 with Slow-Cert(2,x) only needs a Fast-Cert(3,⊥) and Slow-Cert(3,⊥) to exist.
* We wait to get both a slow cert and fast cert to compete a view (Upon 8). 
 
 
```
2-round and 3-round BTF

1. Upon entering view k: 
    Everyone starts a local timer T_k 
    Leader sends (Propose, k, x, X-Cert(k’, x)) for the highest k’, 
            where certs are ordered first by view and then by Fast < Slow 
    
2. Upon received (Propose, k, x, X-Cert(k’, x)) for some X in {Fast, Slow} 
            and ⊥ certificates for all higher certificates of view <k, 
            and has not sent Vote 
    Send (Vote, k, x) to all     // Denote n-2f-p (Vote,k,x) as Fast-Cert(k,x)
                                 // Denote n-f-p (Vote,k,x) as Slow-Cert(k,x) 

3. Upon Slow-Cert(k,x); and has not sent Final
    Send (Final, k, x) to all  
    
4. Upon receiving n-f-p (Final, k, x) or n-p (Vote, k, x)    // Monitored even after exiting view k
    Decide x 
    Forward commit proof 
    Terminate 

5. Upon T_k = 2 Δ; and has not sent Vote
    Send (Vote, k, ⊥) to all   // Denote n-2f-p (Vote,k,⊥) as Fast-Cert(k,⊥)

6. Upon T_k = 3 Δ; and has not sent Final
    Send (Final, k, ⊥) to all   // Denote n-f-p (Final,k,⊥) as Slow-Cert(k,⊥) 

7. Upon receiving n-f (Vote, k, *) but no Cert(k, x) for any x 
    Send (Vote, k, ⊥) to all

8. Upon receiving Slow-Cert(k, *) and Fast-Cert(k, *) 
    Forward both 
    Enter view k+1 if in view k  
```







## Safety and liveness proof sketches

**Lemma 1**: If an honest party fast commits $x$ in view $k$, then X-Cert(k, $\bot$) or X-Cert(k, x') for $x' \neq  x$ and $X \in \{Fast, Slow\}$ cannot form. 

*Proof sketch*: A fast commit requires $n-p$ votes for $x$, so no other value can get $n-2f-p$ votes by quorum intersection. 

**Lemma 2**: If an honest party slow commits $x$ in view $k$, then Slow-Cert(k, $\bot$) or Slow-Cert(k, x') for $x' \neq  x$  cannot form. 

*Proof sketch*: A slow commit requires $n-f-p$ votes for $x$, so no other value can get $n-f-p$ votes by quorum intersection. In addition, a slow commit requires $n-f-p$ final for $x$, so no $n-f-p$ final for $\bot$ by quorum intersection. Note that a we dont care about Fast-Certs for this view because they are weaker.



**Lemma 3**: If an honest party commits $x$ in view $k$, no honest party votes for $x' \neq x$ ($x' \neq \bot$) in any view higher than $k$.

*Proof sketch:* Consider the leader's proposal in view $k+1$, with accompaning certificate X-Cert(k',x). There are two cases:

1. $k'<k$: Lemma 1 and Lemma 2 imply that X-Cert(k,$\bot$) do not exist for *both* $X\in \{Fast,Slow\}$, and hence the proposal isn't valid.
2. $k'=k$: Lemma 1 and Lemma 2 imply that the proposal must be for x.

This completes the proof for $k+1$, the proof for higher views follows by induction.



Safety is straightforward from Lemma 3. Liveness follows from the lemmas below. 

**Lemma 4**: If no honest party commits in views $k$ or lower, then every honest party eventually receives either X-Cert(k, x) for some $x \neq \bot$ or X-Cert(k, $\bot$) for each $X \in \{Fast, Slow\}$. 

*Proof sketch*: If any honest party gets Fast-Cert(k, x), it forwards the certificate. Otherwise, all honest parties eventually vote for $\bot$ by the fifth Upon rule, so all honest parties eventually get a Fast-Cert(k, $\bot$). Moreover, each party either gets a Slow-Cert(k, x) forwarded to it, or by definition, hold a Slow-Cert(k, ⊥).

**Lemma 5**: If view $k$ starts after GST, and the leader of view $k$ is honest, then all honest parties commit in view $\leq k$.

*Proof sketch*: If an honest party commits in view $<k$, it forwards the commit certificate, so all honest parties commit in view $<k$. If no honest party commits in view $<k$, then given synchrony after GST, all honest parties enter view $k$, vote for the honest leader.

If there are $<p$ Byzantine then all will and commit in view $k$ in 2 rounds.

If there are $<f$ Byzantine then all honest will send final and commit in view $k$ in 3 rounds.



## Acknowledgments

We would like to thank Quentin Kniep, Jakub Sliwinski, and Roger Wattenhofer for insightful discussions and feedback. Yuval participated in this work while affiliated with a16z Crypto Research.


Your thoughts/comments on [X]().
