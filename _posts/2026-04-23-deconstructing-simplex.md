---
title: Deconstructing Simplex
date: 2026-04-23 00:00:00 -05:00
tags:
- consensus
author: Ittai Abraham
---


In a [previous post](https://decentralizedthoughts.github.io/2022-11-20-pbft-via-locked-braodcast/) we decomposed PBFT into an outer shell and an inner shell consisting of two building blocks: *Locked-Broadcast* (LB) and *Recover-Max-Lock*. Here we similarly decompose [Simplex](https://decentralizedthoughts.github.io/2025-06-18-simplex/) into an outer shell and an inner shell consisting of a single building block: **Graded-Broadcast** (GB).



The model is [partial synchrony](https://decentralizedthoughts.github.io/2019-06-01-2019-5-31-models/) with $f<n/3$ [Byzantine failures](https://decentralizedthoughts.github.io/2019-06-07-modeling-the-adversary/), and the goal is *single-shot provable consensus with external validity*. 


## Single-shot Provable Consensus with External Validity

There is some *External Validity* Boolean function ($EV_{\text{consensus}}$) that is provided to each party. $EV_{\text{consensus}}$ takes as input a value $val$ and a proof $proof$. If $EV_{\text{consensus}}(val, proof)=1$ we say that $val$ is *externally valid*. A simple example of external validity is a check that the value is signed by the client that controls the asset. External validity is based on the framework of [Cachin, Kursawe, Petzold, and Shoup, 2001](https://www.iacr.org/archive/crypto2001/21390524.pdf). 

In this setting, each party has one or more externally valid input values. There is a Boolean function to verify a commit certificate, $verify(cert)$. We say a commit certificate is **valid** if $verify(cert)=true$.

The protocol has the following three properties:

**Liveness**: all honest parties eventually hold a valid commit certificate. 

**External Validity**: the adversary cannot form a valid commit certificate whose value is not externally valid.

**Provable Agreement**: the adversary cannot form two valid commit certificates with different values.




## Deconstructing Simplex into an Inner and Outer Protocol

The outer protocol:

```
For view v, the primary of view v with input (val, val-proof):

    if a certSet is not empty,
        let p in certSet be the certificate of highest view w
        let C be the set of skip certificates from skipSet for all views w < y < v
        Graded-Broadcast (v, p.val, (p,C))
    otherwise
        let C be the set of skip certificates from skipSet for all views y < v
        Graded-Broadcast (v, val, (val-proof, C))

```

Using the following event handlers (certificates can arrive from Graded-Broadcast or forwarded):

```
On first skip certificate for view v, add it to skipSet, and move to view v+1 (if not there yet)

On first certificate for view v, add it to certSet, and move to view v+1 (if not there yet)

On first strong certificate, decide and forward it
```




The **Simplex voting rule** is the external-validity function passed to Graded-Broadcast:
```
For view v:

    if receive (v, p.val, (p,C)) check that p is a valid certificate
        and that C contains a valid skip certificate for each view p.view < y < v

    if receive (v, val, (val-proof, C)) check that val-proof is a proof that val is valid
        and that C contains a valid skip certificate for each view y < v
``` 

In words, if the primary has a certificate, it proposes the value of the certificate together with skip certificates for all views between that certificate and the current view. If there are no certificates, it uses its own input together with skip certificates for all lower views.

Intuitively, since a skip for view $y$ is a proof that no commit happened in view $y$, showing all the relevant skips proves that if any value was previously committed, then the proposed value must be that value.
 

All that remains is to define the inner protocol *Graded-Broadcast*.


## Graded-Broadcast

Graded-Broadcast is a non-trivial extension of classic (authenticated) [Reliable Broadcast](https://decentralizedthoughts.github.io/2020-09-19-living-with-asynchrony-brachas-reliable-broadcast/) (with external validity) to partial synchrony. Recall that authenticated Reliable Broadcast with external validity provides *uniqueness*: all valid certificates have the same value; *totality*: if any honest party delivers a certificate then eventually all honest parties deliver it; *external validity*: if a certificate is valid then its value is externally valid; and *validity*: if the sender is honest then it obtains a certificate whose value is its input.

An instance of Graded-Broadcast has a designated sender and an instance tag $v$. During the instance, a party may deliver three kinds of certificates:

1. a **regular certificate** for some value $x$ and tag $v$;
2. a **strong certificate** for some value $x$ and tag $v$; or
3. a **skip certificate** with tag $v$.

A party may deliver one certificate and later deliver another, but delivering one certificate does not imply that any additional certificate will ever be delivered. When a party delivers a certificate, it does not yet know whether this will be the only certificate it ever delivers in that instance. In the outer protocol, a regular certificate plays the role of a certificate, a strong certificate plays the role of a commit certificate, and a skip certificate serves as proof that no commit certificate was formed in that view.

The intended intuition is that Graded-Broadcast is to partial synchrony what gradecast is to synchrony. A strong certificate has grade 2, a regular certificate has grade 1, and a skip certificate has grade 0. Relative to Reliable Broadcast, the main change is that we strengthen liveness and weaken validity: unlike Reliable Broadcast, Graded-Broadcast always terminates by eventually delivering at least one certificate, but when the sender is honest and the network is still asynchronous, honest parties may deliver a skip certificate or a regular certificate instead of a strong certificate.

Here are the properties of Graded-Broadcast:

1. **Liveness**: At least one certificate is eventually delivered. However, unlike Reliable Broadcast, in Graded-Broadcast a party may asynchronously deliver more than one certificate. Moreover, after GST, all honest parties deliver their first certificate within $\Delta$ time of each other.
2. **Uniqueness**: the adversary cannot produce two valid certificates with the same tag, each of which is either a regular certificate or a strong certificate, with different values.
3. **Totality**: if any honest party delivers a certificate (strong, regular, or skip), then eventually all honest parties deliver it.
4. **Grade Safety**: the adversary cannot produce both a valid strong certificate and a valid skip certificate with the same tag.
5. **External Validity**: the adversary cannot produce a valid regular certificate or a valid strong certificate whose value is not externally valid.
6. **Strong Validity**: if the sender is honest, $GST=0$, and all honest parties start within $\Delta$ time of each other, then all honest parties eventually deliver a strong certificate whose value is the sender's input.

The three new properties are liveness, grade safety, and strong validity. Liveness is what allows the outer protocol to always move on. Strong validity is the good-case guarantee that an honest sender under synchrony causes all honest parties to deliver grade 2. Grade safety is the key separation property: once grade 2 exists, grade 0 cannot.

In particular, Uniqueness and Grade Safety together imply that if an honest party delivers a strong certificate for some value $x$, then the first non-skip certificate delivered by any honest party in that same instance also has value $x$.

### Implementing Graded-Broadcast

We now extract Graded-Broadcast from the Simplex protocol of the [previous post](https://decentralizedthoughts.github.io/2025-11-15-simplex-from-benign/). In an instance with tag $v$, the designated sender has input `(x, proof)`. A proposal `<Propose, v, x, proof>` is *valid* if it passes the Simplex voting rule, which is the external-validity function supplied by the outer shell.

In this implementation, a **regular certificate** for $x$ with tag $v$ consists of:

1. a valid proposal `<Propose, v, x, proof>` from the sender; and
2. $n-f$ distinct `<Vote, v, x>` messages.

A **strong certificate** for $x$ with tag $v$ consists of:

1. a valid proposal `<Propose, v, x, proof>` from the sender; and
2. $n-f$ distinct `<Final, v, x>` messages.

A **skip certificate** with tag $v$ consists of $n-f$ distinct `<Vote, v, ⊥>` messages.

When a party forwards a certificate, it forwards the bundled signed messages that make up the certificate.

```text
Graded-Broadcast with tag v and designated sender Sender(v)
and sender input (x, proof):

1. Upon entering the instance:
    Start a local timer T_v
    Sender(v) sends <Propose, v, x, proof>

2. Upon receiving the first valid <Propose, v, x, proof> from Sender(v):
    Send <Vote, v, x>

3. Upon receiving a valid regular certificate rc for x for the first time:
    Deliver rc
    Send rc to all
    If T_v < 3Δ:
        Send <Final, v, x>

4. Upon T_v = 3Δ and not yet sent Final:
    Send <Vote, v, ⊥>

5. Upon receiving a valid skip certificate sc for the first time:
    Deliver sc
    Send sc to all

6. Upon receiving a valid strong certificate sc for x for the first time:
    Deliver sc
    Send sc to all
```

### Proving the Implementation

We now prove that the implementation above satisfies the six Graded-Broadcast properties.

### Liveness

If some honest party sends `<Final, v, x>`, then all honest parties will receive a regular certificate.

Otherwise, no honest party sends `<Final, v, x>`. Then every honest party reaches time $T_v = 3\Delta$ and sends `<Vote, v, ⊥>`. Hence every honest party will see a skip certificate. Clearly after GST the gap is at most $\Delta$.

### Uniqueness

Since a regular certificate requires $n-f$ `Vote` messages, no conflicting regular certificates can form. This implies no conflicting strong certificates can form.

### Totality

Follows from the fact that certificates are forwarded.

### Grade Safety

Suppose for contradiction that the adversary produces both a valid strong certificate for $x$ and a valid skip certificate with tag $v$. Their two sets of $n-f$ messages intersect in some honest party.

But an honest party never sends both `<Final, v, x>` and `<Vote, v, ⊥>`: it sends `<Vote, v, ⊥>` only if it has not yet sent `Final`. This is a contradiction.

### External Validity

Suppose the adversary produces a valid regular certificate for $x$. Among its $n-f$ votes, at least $n-2f \geq 1$ are from honest parties. An honest party sends `<Vote, v, x>` only after checking that the proposal `<Propose, v, x, proof>` is valid according to the Simplex voting rule. Therefore $x$ is externally valid.

A valid strong certificate implies a valid regular certificate for the same value, as shown in the proof of Uniqueness. So the same argument applies to strong certificates as well.

### Strong Validity

With $GST=0$, the honest sender broadcasts at time $t_s$; all honest parties start by $t_s + \Delta$ and receive the proposal by $t_s + \Delta$. By $t_s + 2\Delta$, every honest party has $n-f$ votes and delivers the regular certificate. Each honest party's timer started no earlier than $t_s - \Delta$, so it fires no earlier than $t_s + 2\Delta$, strictly later because parties start *strictly* within $\Delta$ of each other. Thus every honest party delivers the regular certificate with $T_v < 3\Delta$, sends `<Final, v, x>`, and by $t_s + 3\Delta$ delivers a strong certificate for $x$.

## Proving the Outer Protocol

We now prove that the outer protocol satisfies the three provable consensus properties above. The proof uses only the fact that in view $v$ the protocol runs Graded-Broadcast with tag $v$ and with the Simplex voting rule as its external-validity function, together with the six properties of Graded-Broadcast.

### Claim 1 (provable agreement)

Let $k$ be the first view with a valid commit certificate for value $x$. We show by induction that any honest party accepting a proposal in any view $v > k$ accepts only $x$.

*Grade Safety* implies no valid skip certificate with tag $k$; *Uniqueness* implies every valid certificate with tag $k$ has value $x$. A fresh proposal in any view $v > k$ requires a skip certificate for all views $y < v$, which includes tag $k$: impossible. So any accepted proposal uses a certificate from some view $w < v$; since $w < k$ also requires a skip certificate for tag $k$, we have $w \geq k$. If $w = k$, *Uniqueness* gives value $x$; if $w > k$, the induction hypothesis gives value $x$.

Provable Agreement follows: any later commit certificate contains an honest `Final` sender, who voted only after accepting a proposal, hence for value $x$.

### External Validity

Any valid commit certificate is a valid strong certificate of some Graded-Broadcast instance. By the *External Validity* property of Graded-Broadcast, its value must be externally valid.

### Claim 2 (liveness)

All honest parties eventually hold a valid commit certificate.

If any honest party delivers a strong certificate, *Totality* propagates it to all. Otherwise, consider the first post-GST view $v^+$ with an honest primary that starts after all earlier certificates have propagated. By the $\Delta$-gap part of *Liveness*, all honest parties enter $v^+$ within $\Delta$ of each other, satisfying *Strong Validity*'s premise.

By *Liveness*, every earlier view delivered a certificate or skip certificate. The primary's highest certificate from view $w$ (if any) is accompanied by skip certificates for all views $w < y < v^+$; if there is no certificate, skip certificates cover all views $y < v^+$. In either case the proposal satisfies the Simplex voting rule at every honest party, so by *Strong Validity* all honest parties deliver a strong certificate in view $v^+$.

Finally, since all honest parties start within $\Delta$ of each other, then even if the honest proposer starts $\Delta$ late, all honest parties will hold a strong certificate before their $3\Delta$ timer expires.

## Notes

There are multiple advantages for a modular decomposition of Simplex both in practice and in theory. In follow up posts we will show how to use this decomposition to obtain new protocols.


How does GB differ from PBFT's Locked-Broadcast (LB)? First note that in LB there is no notion of a skip certificate, just a lock certificate (similar to a certificate in GB). In both protocols the goal is to prove that the lock/certificate is safe in the sense that there is no higher view in which there could have been a commit:

1. In Simplex this is done by showing a skip certificate for every higher view.
2. For PBFT, this is done by showing the $n-f$ highest locks that are not higher than the proposal.

## Acknowledgments

Many thanks to Kartik and Joachim for insightful comments and suggestions.

Your thoughts on [X](https://x.com/home).
