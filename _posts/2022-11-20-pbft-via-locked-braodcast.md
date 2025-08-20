---
title: 'Linear PBFT: a gentle introduction to Practical Byzantine Fault Tolerance'
date: 2022-11-20 04:00:00 -05:00
tags:
- consensus
author: Ittai Abraham
---

[PBFT](https://pmg.csail.mit.edu/bft/) is a foundational multi-year project led by [Barbara Liskov](https://pmg.csail.mit.edu/~liskov/) and her students, obtaining major advances in both the theory and practice of Byzantine Fault Tolerance. The PBFT [conference version](https://pmg.csail.mit.edu/papers/osdi99.pdf), [journal version](https://pmg.csail.mit.edu/papers/bft-tocs.pdf), Castro's [thesis](https://pmg.csail.mit.edu/~castro/thesis.pdf), Liskov's [talk](https://www.youtube.com/watch?v=Uj638eFIWg8), and follow-up work on [BASE](http://www.sosp.org/2001/papers/rodrigues.pdf) are all required reading for anyone who wants to deeply understand BFT systems.

In this post we describe a variation of the authenticated version of [PBFT](https://pmg.csail.mit.edu/papers/osdi99.pdf) using [Locked Broadcast](https://decentralizedthoughts.github.io/2022-09-10-provable-broadcast/) that follows a similar path as our previous post on [Paxos using Recoverable Broadcast](https://decentralizedthoughts.github.io/2022-11-04-paxos-via-recoverable-broadcast/). I call this protocol **linear PBFT** because the number of messages per view is linear. However, the size of the view change message in the worst case is large. We discuss improving this in a [later post](https://decentralizedthoughts.github.io/2022-11-24-two-round-HS/) on [Two Round HotStuff](https://arxiv.org/pdf/1803.05069v1.pdf) using [Locked Broadcast](https://decentralizedthoughts.github.io/2022-09-10-provable-broadcast/). Other ways of reducing the view change message size are to use [Three Round HotStuff](https://arxiv.org/pdf/1803.05069.pdf) via [Keyed Broadcast](https://decentralizedthoughts.github.io/2022-09-10-provable-broadcast/), or to use SNARKs.

Variants of the linear PBFT protocol are used by [SBFT](https://arxiv.org/pdf/1804.01626.pdf), [Tusk](https://arxiv.org/pdf/2105.11827.pdf), [Jolteon](https://arxiv.org/pdf/2106.10362.pdf), [DiemBFTv4](https://developers.diem.com/papers/diem-consensus-state-machine-replication-in-the-diem-blockchain/2021-08-17.pdf), and [Aptos](https://github.com/aptos-labs/aptos-core/blob/main/developer-docs-site/static/papers/whitepaper.pdf).


The model is [partial synchrony](https://decentralizedthoughts.github.io/2019-06-01-2019-5-31-models/) with $f<n/3$ [Byzantine failures](https://decentralizedthoughts.github.io/2019-06-07-modeling-the-adversary/) and the goal is *consensus with external validity* (see below for exact details). 

As with Paxos, we present PBFT with two major simplifications:

1. Use a *simple revolving primary* strategy assuming perfectly synchronized clocks. This approach follows Section 6 of [Two Round HotStuff](https://arxiv.org/pdf/1803.05069v1.pdf).
2. Focus on a *single-shot* consensus while PBFT is designed as a full State Machine Replication system. See [here](https://decentralizedthoughts.github.io/2022-11-19-from-single-shot-to-smr/) for the next steps.


## View-based protocol with simple rotating primary

Just as in [Paxos](https://decentralizedthoughts.github.io/2022-11-04-paxos-via-recoverable-broadcast/), the protocol progresses in **views**, each view has a designated **primary** party. For simplicity, the primary of view $v$ is party $v \bmod n$. 

Clocks are synchronized, and $\Delta$ (the delay after GST) is known, so set view $v$ to be the time interval $[v(10 \Delta),(v+1)(10 \Delta))$. In other words, every $10\Delta$ ticks, each party triggers a **view change** and increments the view by one. Since clocks are assumed to be perfectly synchronized, all parties move in and out of each view in complete synchrony.

## Single-shot Consensus with External Validity

There is some *External Validity* Boolean function ($EV_{\text{consensus}}$) that is provided to each party. $EV_{\text{consensus}}$ takes as input a value $v$ and a proof $proof$. If $EV_{\text{consensus}}(v, proof)=1$ we say that $v$ is *externally valid*. A simple example of external validity is a check that the value is signed by the client that controls the asset. External validity is based on the framework of [Cachin, Kursawe, Petzold, and Shoup, 2001](https://www.iacr.org/archive/crypto2001/21390524.pdf). 

In this setting, each party has some externally valid *input values* (one or more) and the goal is to *output a single externally valid value*, which is a (value, proof) pair with the following three properties:

**Agreement**: all non-faulty parties output the same (value, proof) pair. 

**Termination**: all non-faulty parties eventually output a (value, proof) pair and terminate. 

**External Validity**: the output is externally valid, $EV_{\text{consensus}}(value,proof)=1$.

Linear PBFT is decomposed to use two building blocks: *Locked-Broadcast* and *Recover-Max-Lock*. Let's start with the outer shell of the linear PBFT that calls them.


# Linear PBFT via Locked-Broadcast and Recover-Max-Lock

```
For view 1, the primary of view 1 with input (val, val-proof): 
    Locked-Broadcast (1, val, val-proof)
```

```
For view v>1, the primary of view v with input (val, val-proof):

    (p, R) := Recover-Max-Lock(v)

    if p = bot then 
        Locked-Broadcast (v, val, val-proof, R)
    otherwise 
        Locked-Broadcast (v, p, R)

```

Termination protocol:

```
If a Locked-Broadcast outputs a valid delivery-certificate dc for x
    Send <decide, x, dc> to all
    Terminate
    
Upon receiving a valid <decide, x, dc> 
    Send <decide, x, dc> to all
    Terminate
``` 

In words, the primary first tries to recover the lock-certificate with the maximal view. If no lock-certificate is seen, the primary is free to choose its own externally valid input $val$, but even in that case, it adds the proof $R$ from the Recover-Max-Lock protocol. Otherwise, it proposes the output value $p$ from the Recover-Max-Lock along with its proof $R$.  Note the similarity to the Paxos protocol variant of the [previous post](https://decentralizedthoughts.github.io/2022-11-04-paxos-via-recoverable-broadcast/).

All that remains is to define  *Locked-Broadcast* and *Recover-Max-Lock*.

## Locked-Broadcast

[Locked-Broadcast](https://decentralizedthoughts.github.io/2022-09-10-provable-broadcast/) is the application of two provable broadcasts with an *external validity function*, $EV_{\text{LB}}$, which obtains the following properties:

* **Termination**: If the sender is honest and has an *externally valid* input $x$, then after a constant number of rounds the sender will obtain a *delivery-certificate* of $x$. Note that the Termination property guarantees that only the sender holds the certificate (so we will need to propagate it via another round).
* **Uniqueness**: If a  *delivery-certificate* exists for $x$  then there cannot exist a *delivery-certificate* for $x' \neq x$.
* **External Validity**: If there is a *delivery-certificate* on $x=(value, proof)$ then $x$ is *externally valid*. So $EV_{\text{LB}}(value, proof)=1$.
* **Unique-Lock-Availability**: If a *delivery-certificate* exists for $x$ then: (1) there cannot exist a *lock-certificate* for $x' \neq x$; and (2) there are at least $n-2f\geq f+1$ honest parties that hold a *lock-certificate* for $x$.

Note that Locked-Broadcast needs to define an external validity function $EV_{\text{LB}}$, which controls what outputs are allowed. $EV_{\text{LB}}$ is different from $EV_{\text{consensus}}$ (the external validity function of the underlying consensus protocol). 

Before we define $EV_{\text{LB-PBFT}}$ for the Locked-Broadcast protocol in PBFT, we detail the Recover-Max-Lock protocol. Similar to [Recover-Max of this Paxos](https://decentralizedthoughts.github.io/2022-11-04-paxos-via-recoverable-broadcast/), the Recover-Max-Lock protocol returns the highest lock-certificate it sees. Unlike Paxos, it also returns a ```proof``` that the primary chose the highest lock-certificate it saw out of a set of $n{-}f$ distinct lock-certificates it received. The external validity $EV_{\text{LB-PBFT}}$ of the locked-broadcast will check the validity of this proof.

### Recover-Max-Lock for PBFT-based protocols

Recover-Max-Lock for view $v$ finds the *highest* lock-certificate and returns not only the associated value but also the $n{-}f$ responses that allows one to verify that indeed the highest lock-certificate among some set of $n{-}f$ *valid responses* was used. A valid response is a response which includes a valid lock-certificate, and a valid lock-certificate includes $n{-}f$ distinct signatures.

```
Recover-Max-Lock(v):

Party i upon start of view v
    If it does not have any lock-certificate   
       send <echoed-max(v, bot)>_i to primary 
    Otherwise let  v' be the highest view with a lock-certificate
        let LC(v',p') be this lock certificate for value p'
        send <echoed-max(v, v', p', LC(v',p') )> to primary

Primary waits for n-f valid <echoed-max(v,*)>
    Let R be this set
    If all values in R are bot then output (bot, R)
    otherwise, output (p, R) 
        where p is the value associated with the highest view in R
```

With the Recover-Max-Lock defined, the definition of $EV_{\text{LB-PBFT}}$ for Locked-Broadcast should be natural. The Primary will input $(p,R)$ to Locked-Broadcast and the parties will check that $p$ is indeed the value associated with the highest view in R (or an externally valid value and all values in R are for $\bot$).

### External Validity for the Locked-Broadcast of Linear PBFT

To define Locked-Broadcast for PBFT let's define $EV_{\text{LB-PBFT}}$ which controls what messages to accept. The $EV_{\text{LB-PBFT}}$ function checks the validity of the primary's messages. In view 1 and in the case the message is $(val,val{-}proof,R)$ we also use the external $EV_{\text{consensus}}$ as a subroutine to verify $val$ relative to $val{-}proof$. 

Informally, $EV_{\text{LB-PBFT}}$ for view $v>1$, either checks that $n{-}f$ parties say they saw no lock-certificate and the new value is externally valid for consensus; or that the primary proposes the value that is associated with a lock-certificate and the view of this lock-certificate is the highest one among a set of $n{-}f$  valid ```<echoed-max(v, * )>``` messages.


Define $EV_{\text{LB-PBFT}}$ for view $v$:

```
For view 1 set EV-LB-PBFT (1, val, val-proof) = EV-consensus(val, val-proof)
```

```
For view v>1 there are two cases for EV-LB-PBFT(v, *):

Given * is a 3-tuple (val, val-proof, R):
    1. Check R consists of n-f distinct valid <echoed-max(v, bot)> messages
    2. Check EV-consensus(val, val-proof) = 1

Given * is a 2-tuple (p, R):
    1. Check R consists of n-f distinct valid <echoed-max(v, * )> messages
    2. Check each <echoed-max(v, v', p', LC(v',p') )> in R:
        has a valid lock-certificate LC(v') for view v' and value p'
    3. Let w, q, LC(w,q) be the valid <echoed-max(v, * )> response with the highest view w in R
        Check p = q (p is from the lock-certificate with highest view in R).
```

Observe that a valid proof ```R``` may contain up to $n{-}f$ distinct lock-certificates (from different views) and each valid lock-certificate contains $n{-}f$ distinct signatures (from different parties) so without compressing, ```R``` contains $O(n^2)$ words. 

This completes the description of the consensus protocol. The protocol is detailed in 4 places: the linear PBFT consensus protocol, the recover-max lock protocol, the locked-broadcast protocol, and finally the external validity of the locked-broadcast. Let's prove that the three properties of consensus hold:


### Agreement (Safety)

**Safety Lemma**: Let $v^{\star}$ be the first view with a commit-certificate on $(v^\star, x)$, then for any view $v \geq v^\star$, if a lock-certificate forms for view $v$, it must be with value $x$.

*Exercise: Prove the Agreement property follows from the Safety Lemma above.*

Let's prove the safety lemma, which is the essence of PBFT.

*Proof of Safety Lemma*: Let $S$ (for Sentinels) be the set of **non-faulty** parties among the $n{-}f$ parties that sent a lock-certificate in the second round of locked broadcast of view $v^\star$. Note that $\|S\| \geq n{-}2f \geq f{+}1$.

Induction statement: for any view $v\geq v^\star$:

1. If there is a lock-certificate for view $v$, then it has value $x$.
2. For each party in $S$, in view $v$, its lock-certificate with the highest view $v'$ is such that: 
    1. $v' \geq v^\star$; and
    2. The value of this lock-certificate is $x$.

For the base case, $v=v^\star$: (1.) follows from the *Uniqueness* property of locked broadcast of view $v^\star$ and (2.) follows from the *Unique-Lock-Availability* property of locked broadcast.

Now suppose the induction statement holds for all views $v^\star \leq v$ and consider view $v+1$:

Use the *External Validity* property of locked broadcast and the definition of $EV_{\text{LB-PBFT}}$ above: to form a lock-certificate, the primary needs at least $n{-}2f$ non-faulty parties to view its proposal as valid. 

Observe that by definition of $EV_{\text{LB-PBFT}}$ for view $v+1$: any valid ```R``` must include a lock-certificate sent by some member of $S$ for view $v+1$. This is true because ```R``` must include $n{-}f$ distinct and valid ```<echoed-max v, *>``` responses and the set $S$ is of size at least $f+1$. 

Use the induction hypothesis on views $v^\star \leq v$: from (2.) and the above argument, ```R``` must contain a lock-certificate of view at least $v^\star $ and value $x$. From (1.) any lock-certificate in ```R``` is either of view $< v^\star$ or of value $x$. Hence, the value associated with the maximal view lock-certificate in ```R``` must be $x$. This concludes the proof of (1.) for view $v+1$.

Given (1.) for view $v+1$, (2.) follows, because the only thing that may happen is that some members in $S$ see a lock-certificate for view $v+1$ and update their highest lock-certificate. The value will remain $x$. This concludes the proof of the Safety Lemma.

### Liveness

Consider the view $v^+$ with the *first* non-faulty Primary that started after GST. Denote this start time as time $T$. Due to clock synchronization and being after GST, then on or before time $T+ \Delta$ the primary will receive ```<echoed-max(v+,*)>``` from all non-faulty parties (at least $n{-}f$ parties). So the primary will send a value $LB(v^+, *)$ that (1) will arrive at all non-faulty parties on or before time $T+2\Delta$ and (2) will have a $proof$ that is valid. Hence, all non-faulty parties will pass the $EV_{\text{LB-PBFT}}$ condition for view $v^+ $ (they are still in view $v^+$). So the primary will obtain a delivery-certificate on or before time $T+5\Delta$ (locked broadcast takes at most $4 \Delta$) and all non-faulty will decide on or before time $T+6\Delta$.

This concludes the proof of Liveness.

### Termination

Add the following validated *termination gadget*:

```
If the consensus protocol outputs x and valid delivery-certificate dc for x
    Send <decide, x, dc> to all
    Terminate
    
Upon receiving a valid <decide, x, dc> 
    Send <decide, x, dc> to all
    Terminate
``` 

*Exercise: Prove that if a non-faulty party terminates, then eventually all non-faulty parties terminate.*



### External Validity

External validity is proven by induction on the chain of lock-certificates. For a lock-certificate that is formed with an $EV_{\text{LB-PBFT}}$ check that has no prior lock certificate, external validity is part of the $EV_{\text{LB-PBFT}}$ function check. For a lock-certificate that is formed with an $EV_{\text{LB-PBFT}}$ check that checks a previous lock-certificate, then this new lock-certificate must use the same value as the previous lock-certificate. An induction argument shows that any lock-certificate must have an externally valid value.

### Time and Message Complexity

The time and number of messages before GST can be both unbounded, so we measure the time and message complexity after GST.

**Time complexity**:  since the liveness proof requires waiting for the first non-faulty primary after GST, this may take: an interrupted view of an honest primary, then in the worst case, another $f$ views of faulty primaries, then finally a good view. So all parties will output a value in at most $(f+2)10 \Delta = O(f \Delta)$ time after GST. This is asymptotically optimal but not optimized.

**Message Complexity**: since each view has a linear message exchange, the total number of messages sent after GST is $O(f \times n) = O(n^2)$. This is asymptotically optimal. 

However, the number of bits in each message is large and not optimal. The size of a lock-certificate or a delivery-certificate is $O(n)$ signatures. More worrisome, the size of ```R``` that is sent in the locked broadcast can be $O(n^2)$ signatures because it may contain $O(n)$ lock-certificates (for different views).

Lock-certificates can be reduced to a single signature by using threshold signatures. Reducing the size of ```R``` below $O(n)$ signatures requires either more powerful succinct proofs (for example, a SNARK) or a slightly different protocol. We will explore both in future posts.

## Notes

In later posts, we will show other view synchronization solutions, and HotStuff also provides responsiveness.

## Acknowledgments

Many thanks to Kartik Nayak for insightful comments.

Your comments on [Twitter](https://twitter.com/ittaia/status/1599893500866088961?s=20&t=RUTyrxNgaIvudyiV5O5IAA).

