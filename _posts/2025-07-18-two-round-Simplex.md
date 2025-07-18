---
title: 2-round BFT in Simplex style
date: 2025-07-18 00:00:00 -04:00
tags:
- consensus
- BFT
author: Ittai Abraham, Yuval Efron, and Ling Ren
---

[Simplex](https://simplex.blog/) is a recent partially synchronous Byzantine Fault Tolerant (BFT) protocol that is gaining popularity. We take this opportunity to rehash several classic results in the Simplex style. [The first post](https://decentralizedthoughts.github.io/2025-06-18-simplex/) explained the key difference between Simplex and Tendermint. This second post is on 2-round BFT. The next post will explore protocols that integrate concurrent 2-round and 3-round paths. 

Mainstream partially synchronous BFT protocols tolerate $f<n/3$ Byzantine faults and have [3-round commit latency](https://decentralizedthoughts.github.io/2021-02-28-good-case-latency-of-byzantine-broadcast-a-complete-categorization/) under an honest leader. This latency can be reduced to 2 rounds, if we decrease the fault tolerance from <33% to <20%. 

Recently, there has been renewed interest in 2-round partially synchronous BFT. In this post, we present a natural 2-round BFT protocol in the Simplex style. A very similar protocol is independently proposed by Commonware and called [Minimmit](https://commonware.xyz/blogs/minimmit.html). 

## Two-round commit intuition

As usual, the first round is for a leader to propose a value, and the second round is for parties to vote for the leader's proposal. In partial synchrony, since $f$ parties can be Byzantine, we can only wait for $n-f$ messages at any step. Thus, if any party receives $n-f$ votes on the *same* value $x$, it commits $x$. 

The tricky case (for BFT in general) is that some party $p$ receives $n-f$ votes and commits $x$, and then $p$ experiences a network outage immediately after committing $x$. The remaining parties cannot wait for $p$ indefinitely, so they must proceed without $p$. To preserve the safety of the protocol, they must eventually commit $x$ rather than any other value. 

Given that $p$ has committed $x$, there were $n-f$ votes for $x$. If another party $q$ waits for a set of $n-f$ votes, it is guaranteed to see: 
* At least $n-3f$ votes for $x$: there are at most $f$ honest parties whose votes did not make it to $p$, and $f$ Byzantine parties who may equivocate; 
* At most $2f$ votes for $x'\neq x$: $f$ honest parties who legitemaly voted $x'$, and $f$ Byzantine parties who voted $x$ but lie. 

It is natural that parties "prefer" the most voted value. Therefore, we need $n-3f>2f$, i.e., $n \geq 5f+1$. Otherwise, parties have no reason to prefer $x$ over $x'$, and safety would be violated. (As it turns out, [$n \geq 5f-1$](https://decentralizedthoughts.github.io/2021-03-03-2-round-bft-smr-with-n-equals-4-f-equals-1/) would be sufficient and necessary to get 2-round commit. But we assume $n \geq 5f+1$ in this post for simplicity.) 

To our knowledge, [FaB](https://ieeexplore.ieee.org/document/1467815) (2005) was the first 2-round $n\ge 5f+1$ BFT protocol, building on an earlier work by [Kursawe](https://ieeexplore.ieee.org/abstract/document/1180196) (2002). In this post, we adapt Simplex to 2-round with $n\ge 5f+1$. 


## Two-round Simplex protocol with $n=5f+1$

The main idea of Simplex is to generate for each view either a lock certificate or a no-commit certificate. Subsequent leaders use these to justify their proposals. We refer the reader to our [last post](https://decentralizedthoughts.github.io/2025-06-18-simplex/) or [the Simplex blog](https://simplex.blog/) for a more detailed explanation. 

In our context, a party votes for a special timeout value $\bot$ in a view if it does not receive a leader's proposal in time. After that, the party will not vote for any leader proposal in this view. Then, $n-3f$ votes for $\bot$ serve as a no-commit certificate for the view, because at this point, at most $3f$ honest and $f$ Byzantine can vote for the leader, and a commit requires $n-f \geq 4f+1$ votes. 

We consider single-shot consensus for simplicity. The protocol proceeds in increasing views. Let Cert(k, x) denote a collection of $n-f$ votes from view k for value x. For convenience, we think of an empty string as Cert(0, x) for any x. All messages are signed and sent to all. 


```
1. Upon entering view k: 
    Everyone starts a local timer T_k 
    Leader sends (Propose, k, x, Cert(k’, x)) for the highest k’ 
    
2. Upon received (Propose, k, x, Cert(k’, x)) and Cert(l, bot) for all k' < l < k and has not sent Vote 
    Send (Vote, k, x) to all     // Denote n-3f (Vote, k, x) as Cert(k, x)  

3. Upon T_k = 2 Delta; and has not sent Vote
    Send (Vote, k, bot) to all   // Denote n-3f (Vote, k, bot) as Cert(k, bot) 

4. Upon receiving n-f (Vote, k, x)   // Monitored even after exiting view k
    Decide x 
    Forward these n-f (Vote, k, x)
    Terminate 

5. Upon receiving n-f (Vote, k, *) but no Cert(k, x) for any x 
    Send (Vote, k, bot) to all

6. Upon receiving Cert(k, *) 
    Forward Cert(k, *) 
    Enter view k+1 if in view k  
```


The first four Upon blocks correspond to leader proposal, vote, timeout, and commit, respectively. The sixth Upon block is Simplex's mechanism of advancing views using certificates (for either a value or no-commit).

The fifth Upon block warrants additional explanation. Without it, there is one subtle liveness challenge. A Byzantine leader can propose different values to different parties. Then, it could happen that none of the value (including $\bot$) gets enough votes to form a certificate. Since Simplex advances views using certificates, the protocol gets stuck and loses liveness. 

But recall that we argued earlier that if a value $x$ has been committed, then there must be a Cert(k, x) among the $n-f$ (Vote, k, \*) messages. Therefore, if no certificate exists among the $n-f$ (Vote, k, \*) messages, the party can be confident that no commit could occur in this view, and hence can send (Vote, k, $\bot$) **even if** it has already voted for some proposal of the leader. With this additional $\bot$ vote step, a certificate (possibly for $\bot$) is guaranteed to form. 

We remark that the $n-f$ (Vote, k, \*) messages that contain no commit certificate could also serve as a no-commit certificate. The only downside is that this no-commit certificate cannot be compressed into a threshold/multi-signature. If one does not plan to use threshold/multi-signature, this extra step is not needed.

## Safety and liveness proof sketches

**Lemma 1**: If an honest party commits $x$ in view $k$, then Cert(k, $\bot$) or Cert(k, x') for $x' \neq  x$ cannot form. 

*Proof sketch*: A commit requires $n-f$ votes for $x$, so no other value can get $n-3f$ votes by quorum intersection. 

**Lemma 2**: If an honest party commits $x$ in view $k$, no honest party votes for $x' \neq x$ ($x' \neq \bot$) in any view higher than $k$.

*Proof sketch*: Since all honest leave view $k$ with Cert(k, x), then inductivly it can be shown that in any higher view $k'>k$, any honest only votes for $x$ or $\bot$, and only gets Cert(k', $\bot$) or Cert(k', x). 

Safety is straightforward from Lemma 2. Liveness follows from the lemmas below. 

**Lemma 3**: If no honest party commits in views $k$ or lower, then every honest party eventually receives either Cert(k, x) for some $x \neq \bot$ or Cert(k, $\bot$). 

*Proof sketch*: If any honest gets Cert(k, x), it forwards the certificate. Otherwise, all honest eventually vote for $\bot$ by the fifth Upon rule, so all honest eventually get a Cert(k, $\bot$). 

**Lemma 4**: If view $k$ starts after GST, and the leader of view $k$ is honest, then all honest parties commit in view $\leq k$.

*Proof sketch*: If an honest party commits in view $<k$, it forwards the commit certificate, so all honest parties commit in view $<k$. If no honest party commits in view $<k$, then given synchrony after GST, all honest parties enter view $k$, vote for the honest leader, and commit in time.

### Acknowledgment
The work is done during the authors' visit to a16z Crypto Research. The authors thank Kartik Nayak for helpful discussions. 
