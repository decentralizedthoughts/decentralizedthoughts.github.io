---
title: 2-round BFT in Simplex style
date: 2025-07-18 00:00:00 -04:00
tags:
- consensus
- BFT
author: Ittai Abraham, Yuval Efron, and Ling Ren
---

[Simplex](https://simplex.blog/) is a recent partially synchronous Byzantine Fault Tolerant (BFT) protocol that some in the field find easier to understand. We will take this opportunity to rehash several classic results in the Simplex style. [The first post](https://decentralizedthoughts.github.io/2025-06-18-simplex/) explained the key difference between Simplex and Tendermint. This second post is on 2-round BFT. The next post will explore protocols that integrate parallel 2-round and 3-round paths. 

Mainstream partially synchronous Byzantine Fault Tolerant (BFT) protocols tolerate 33% Byzantine faults and have 3-round commit latency under an honest leader. This latency can be reduced to 2 rounds, if we decrease the fault tolerance from 33% to ~20%. 

Recently, there is renewed interest in 2-round partially synchronous BFT. In this post, we present a natural 2-round BFT protocol in the Simplex style. The protocol is independently proposed by [Commonware](https://commonware.xyz/blogs/minimmit.html). 

Let us first establish some intuition on what it takes to support 2-round commit. The first two rounds, as always, are for a leader to propose a value, and for parties to vote for the leader's proposal. In partial synchrony, we can only wait for $n-f$ messages at any step. Thus, if any party receives $n-f$ votes on the same value $x$, it commits $x$. 

Now, here is the tricky case (for BFT in general). It is possible that only one party $p$ receives $n-f$ votes and commits $x$, and then $p$ experiences network outage immediately after committing $x$.  The remaining parties cannot wait for $p$ indefinitely, so they must proceed without $p$. To preserve the safety of the protocol, they must eventually commit $x$ rather than any other value. 

Given that $p$ has committed $x$, there were $n-f$ votes for $x$. If another party $q$ waits for a set of $n-f$ votes (denoted $S$), it is guaranteed to see $n-3f$ votes for $x$: $f$ honest parties whose votes did not make it into $S$, and $f$ Byzantine who lie. At the same time, there can be $2f$ votes for $x'\neq x$: f honest parties who legitemaly voted $x'$ plus $f$ Byzantine parties who voted $x$ but lie. 

It is natural that parties "prefer" the most voted value when they proceed without $p$. Therefore, we need $n-3f>2f$. This is the intuition why we need $n \geq 5f+1$. Otherwise, parties have no reason to prefer $x$ over $x'$, and safety would be violated. (As it turns out, [our earlier work and post](https://decentralizedthoughts.github.io/2021-03-03-2-round-bft-smr-with-n-equals-4-f-equals-1/) show that $n \geq 5f-1$ would be sufficient to get 2-round commit. But we assume $n \geq 5f+1$ in this post for simplicity.) 

With the above intuition, we can adapt a classic partially synchronous BFT protocol, such as PBFT and Tendermint, from 3-round with $n\ge 3f+1$ to 2-round with $n\ge 5f+1$. [This post](https://decentralizedthoughts.github.io/2021-03-03-2-round-bft-smr-with-n-equals-4-f-equals-1/) gave some examples. 

In this post, we adapt Simplex to 2-round with $n\ge 5f+1$. We refer the reader to our [previous post](https://decentralizedthoughts.github.io/2025-06-18-simplex/) or [the Simplex blog](https://simplex.blog/) for an explanation of Simplex. 

The main idea of Simplex is to generate no-commit certificates that subsequent leaders use to justify their proposals. In our context, a party sends votes for a special timeout value $\bot$ in a view if it does not receive a leader's proposal in time. After that, the party will not vote for any leader proposal in this view. Then, $n-3f$ votes for $\bot$ serve as a no-commit certificate for the view, because at this point, at most $3f$ honest and $f$ Byzantine can vote for the leader and a commit requires $n-f \geq 4f+1$ votes. 

We can give the 2-round Simplex protocol below. We consider single-shot consensus for simplicity. The protocol proceeds in increasing views. Let Cert(k, x) denote a collection of $n-f$ votes from view k for value x. For convenience, we think of an empty string as Cert(0, x) for any x. All messages are signed and sent to all. 


----------------
Upon entering view k: <br>
    Everyone starts a local timer T~k~ <br>
    Leader sends (Propose, k, x, Cert(k’, x)) for the highest k’ <br>
    
Upon received (Propose, k, x, Cert(k’, x)) and Cert(l, $\bot$) for all k' < l < k and has not sent Vote <br>
    Send (Vote, k, x) to all     // Denote n-3f (Vote, k, x) as Cert(k, x) <br> 

Upon T~k~ = 2&Delta; and has not sent Vote <br>
    Send (Vote, k, $\bot$) to all   // Denote n-3f (Vote, k, $\bot$) as Cert(k, $\bot$) <br>

Upon receiving n-f (Vote, k, x) <br>
    Decide x <br>
    Forward these n-f (Vote, k, x) <br>
    Terminate <br>

Upon receiving n-f (Vote, k, *) but no Cert(k, x) for any x <br>
    Send (Vote, k, $\bot$) to all

Upon receiving Cert(k, *)    // possibly Cert(k, $\bot$) <br>
    Forward Cert(k, *) <br>
    Enter view k+1 
    
----------------


The first four "upon" blocks correspond to leader proposal, vote, timeout, and commit, respectively. The last "upon" block is Simplex's mechanism of advancing views based on certificates (for either a value or no-commit).

The last but one "upon" block warrants additional explanation. Without it, there is one sutble issue. Suppose we have a Byzantine in view k. The leader can propose different values to different parties. Then, it could happen that none of the value (including $\bot$ gets enough votes to form a certificate. Since Simplex advances views using certificates, the protocol gets stuck and loses liveness. 

But recall that we argued earlier that if a value x has been committed, then there must be a Cert(k, x) among the n-f (Vote, k, *) messages. Therefore, if no certificate exists among the n-f (Vote, k, *) messages, the party can be confident that no commit could occur in this view, and hence can send (Vote, k, $\bot$) **even if** it has already voted for some proposal of the leader. This ensures a certificate (possibly for $\bot$) will definitely form. 

We also remark that the n-f (Vote, k, *) messages that contain no-commit certificate could also serve as a no-commit certificate. The only downside is that a no-commit certificate cannot be compressed into a threshold/multi signature. If one does not plan to use threshold/multi signature, this extra step is not needed.

Lastly, we give a skeleton of the safety and liveness proofs for the protocol. We leave the actual proof as simple exercises for the reader. 

Lemma 1: If an honest party commits x in view k, then Cert(k, $\bot$) or Cert(k, x') for x' != x cannot form. 

Lemma 2: If an honest party commits x in view k, no honest party votes for x' != x in any view higher than k. 

Safety is straightforward from Lemma 2. Liveness follows from the lemmas below. 

Lemma 3: If one honest party commits, all honest parties eventually commit.

Lemma 4: If no honest party commits in views k or lower, then every honest party eventually receives either Cert(k, x) for some x != $\bot$ or Cert(k, x). 

Lemma 5: If no honest party commits in views k or lower, view k starts after GST, and the leader of view k is honest, then all honest parties commit in view k. 






