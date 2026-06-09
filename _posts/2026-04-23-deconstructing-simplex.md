---
title: Deconstructing Simplex
date: 2026-04-23 00:00:00 -05:00
tags:
- consensus
author: Ittai Abraham
---


In a [previous post](https://decentralizedthoughts.github.io/2022-11-20-pbft-via-locked-braodcast/) we decomposed PBFT into an outer shell and an inner shell consisting of two building blocks: *Locked-Broadcast* (LB) and *Recover-Max-Lock*. Here we similarly decompose [Simplex](https://decentralizedthoughts.github.io/2025-06-18-simplex/) into an outer shell and an inner shell consisting of a single building block: **Certifying Graded Broadcast** (CGB). For a map of the surrounding Simplex line, see the [Simplex chapter](https://decentralizedthoughts.github.io/2026-05-25-chapter-simplex/).



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

```text
For view v, the primary of view v
with input (val, val-proof):

    if certSet is not empty:
        let p be the certificate in certSet
            with highest view w
        let C be skip certificates from skipSet
            for all views w < y < v
        CGB(v, p.val, (p, C))

    otherwise:
        let C be skip certificates from skipSet
            for all views y < v
        CGB(v, val, (val-proof, C))

```

Using the following event handlers (certificates can arrive from CGB or be
forwarded):

```text
On first skip certificate for view v:
    add it to skipSet
    move to view v+1, if not there yet

On first certificate for view v:
    add it to certSet
    move to view v+1, if not there yet

On first strong certificate:
    decide
    forward it
```




The **Simplex voting rule** is the external-validity function passed to
CGB:
```text
For view v:

    if receive (v, p.val, (p, C)):
        check p is a valid certificate
        check C contains a valid skip certificate
            for each view p.view < y < v

    if receive (v, val, (val-proof, C)):
        check val-proof proves val is valid
        check C contains a valid skip certificate
            for each view y < v
``` 

In words, if the primary has a certificate, it proposes the value of the certificate together with skip certificates for all views between that certificate and the current view. If there are no certificates, it uses its own input together with skip certificates for all lower views.

Intuitively, since a skip for view $y$ is a proof that no commit happened in view $y$, showing all the relevant skips proves that if any value was previously committed, then the proposed value must be that value.
 

All that remains is to define the inner protocol
*Certifying Graded Broadcast* (CGB).


## Certifying Graded Broadcast

Certifying Graded Broadcast (CGB) is a non-trivial extension of classic
(authenticated) [Reliable Broadcast](https://decentralizedthoughts.github.io/2020-09-19-living-with-asynchrony-brachas-reliable-broadcast/)
(with external validity) to partial synchrony. Recall that authenticated
Reliable Broadcast with external validity provides *uniqueness*: all valid
certificates have the same value; *totality*: if any honest party delivers a
certificate then eventually all honest parties deliver it; *external validity*:
if a certificate is valid then its value is externally valid; and *validity*:
if the sender is honest then it obtains a certificate whose value is its input.

An instance of Certifying Graded Broadcast has a designated sender and an
instance tag $v$. During the instance, a party may deliver three kinds of
certificates:

1. a **regular certificate** for some value $x$ and tag $v$;
2. a **strong certificate** for some value $x$ and tag $v$; or
3. a **skip certificate** with tag $v$.

A party may deliver one certificate and later deliver another, but delivering one certificate does not imply that any additional certificate will ever be delivered. When a party delivers a certificate, it does not yet know whether this will be the only certificate it ever delivers in that instance. In the outer protocol, a regular certificate plays the role of a certificate, a strong certificate plays the role of a commit certificate, and a skip certificate serves as proof that no commit certificate was formed in that view.

The intended intuition is that CGB is to partial synchrony what gradecast is to
synchrony. A strong certificate has grade 2, a regular certificate has grade 1,
and a skip certificate has grade 0. Relative to Reliable Broadcast, the main
change is that we guarantee a first certificate and weaken uniqueness into a
graded safety guarantee: unlike Reliable Broadcast, CGB always gives each
honest party at least one certificate, but when the sender is honest and the
network is still asynchronous, honest parties may deliver a skip certificate or
a regular certificate instead of a strong certificate.

The word "certifying" is deliberate: delivering a certificate is an output
event, not termination of the instance. Parties may continue running the
background rules and may later deliver additional certificates.

Here are the properties of CGB:

1. **Certificate Liveness**: even in asynchrony, each honest party eventually
   delivers at least one certificate. However, a party may asynchronously
   deliver more than one certificate. Moreover, after GST, if an honest party
   is the first honest party to deliver a certificate in an instance at time
   $t$, then every honest party delivers a certificate in that instance by time
   $t+\Delta$.
2. **Certificate Totality**: if any honest party delivers a certificate
   (strong, regular, or skip), then eventually all honest parties deliver it.
3. **Strong-Grade Safety**: the adversary cannot produce both a valid strong
   certificate for $x$ and either a valid skip certificate or a valid
   regular/strong certificate for $y\neq x$ with the same tag.
4. **External Validity**: the adversary cannot produce a valid regular
   certificate or a valid strong certificate whose value is not externally
   valid.
5. **Synchronous Strong Validity**: if the sender is honest, $GST=0$, and all
   honest parties start within $\Delta$ time of each other, then all honest
   parties eventually deliver a strong certificate whose value is the sender's
   input.

The three new properties are certificate liveness, strong-grade safety, and
synchronous strong validity. Certificate liveness is what allows the outer
protocol to always move on. Synchronous strong validity is the good-case
guarantee that an honest sender under synchrony causes all honest parties to
deliver grade 2. Strong-grade safety is the key separation property: once grade
2 exists for $x$, grade 0 and any conflicting grade-1 or grade-2 certificate
are excluded.

In particular, Strong-Grade Safety implies that if a strong certificate for $x$
exists, then no skip certificate and no non-skip certificate for $y\neq x$ can
exist in that same instance.

### Implementing Certifying Graded Broadcast

We now extract CGB from the Simplex protocol of the
[previous post](https://decentralizedthoughts.github.io/2025-11-15-simplex-from-benign/).
In an instance with tag $v$, the designated sender has input `(x, proof)`. A
proposal `<Propose, v, x, proof>` is *valid* if it passes the Simplex voting
rule, which is the external-validity function supplied by the outer shell.

In this implementation, a **regular certificate** for $x$ with tag $v$ consists of:

1. a valid proposal `<Propose, v, x, proof>` from the sender; and
2. $n-f$ distinct `<Vote, v, x>` messages.

A **strong certificate** for $x$ with tag $v$ consists of:

1. a valid proposal `<Propose, v, x, proof>` from the sender; and
2. $n-f$ distinct `<Final, v, x>` messages.

A **skip certificate** with tag $v$ consists of $n-f$ distinct `<Vote, v, ⊥>` messages.

When a party forwards a certificate, it forwards the bundled signed messages that make up the certificate.

```text
CGB with tag v
and designated sender Sender(v)
with sender input (x, proof):

1. Upon entering the instance:
    Start a local timer T_v
    Sender(v) sends <Propose, v, x, proof>

2. Upon receiving the first valid
   <Propose, v, x, proof> from Sender(v):
    Send <Vote, v, x>

3. Upon receiving a valid regular certificate rc
   for x for the first time:
    Deliver rc
    Send rc to all
    If T_v <= 3Δ and no <Vote, v, ⊥> sent:
        Send <Final, v, x>

4. Upon T_v > 3Δ
   and not yet sent Final:
    Send <Vote, v, ⊥>

5. Upon receiving a valid skip certificate sc
   for the first time:
    Deliver sc
    Send sc to all

6. Upon receiving a valid strong certificate sc
   for x for the first time:
    Deliver sc
    Send sc to all
```

### Proving the Implementation

We now prove that the implementation above satisfies the five
CGB properties.

### Certificate Liveness

If some honest party sends `<Final, v, x>`, then it first delivered a regular
certificate for $x$ and forwarded it. Eventually all honest parties receive and
deliver that regular certificate.

Otherwise, no honest party sends `<Final, v, x>`. Then every honest party
eventually reaches time $T_v > 3\Delta$ and sends `<Vote, v, ⊥>`. Hence every
honest party eventually sees a skip certificate.

For the post-GST gap, consider the first honest party that delivers a
certificate in the instance after GST. It forwards the certificate, and every
honest party receives it within $\Delta$ and delivers a certificate.

### Certificate Totality

Follows from the fact that certificates are forwarded.

### Strong-Grade Safety

First observe that two valid regular certificates for different values cannot
exist. Two sets of $n-f$ value votes intersect in at least $n-2f>f$ parties,
and an honest party sends a value vote for at most one value.

Also, any valid strong certificate for $x$ implies that a valid regular
certificate for $x$ exists: among the $n-f$ Final$(v,x)$ messages in the strong
certificate, at least one was sent by an honest party, and an honest party sends
Final$(v,x)$ only after receiving a valid regular certificate for $x$.

Now suppose for contradiction that the adversary produces both a valid strong
certificate for $x$ and a valid skip certificate with tag $v$. Their two sets
of $n-f$ messages intersect in an honest party.

But an honest party never sends both `<Final, v, x>` and `<Vote, v, ⊥>`: it
sends `<Vote, v, ⊥>` only if it has not yet sent `Final`. This is a
contradiction.

Finally, suppose there is also a valid regular or strong certificate for
$y\neq x$. If it is regular, this contradicts the regular-certificate
observation above. If it is strong, then it implies a valid regular certificate
for $y$, again contradicting the regular-certificate observation.

### External Validity

Suppose the adversary produces a valid regular certificate for $x$. Among its $n-f$ votes, at least $n-2f \geq 1$ are from honest parties. An honest party sends `<Vote, v, x>` only after checking that the proposal `<Propose, v, x, proof>` is valid according to the Simplex voting rule. Therefore $x$ is externally valid.

A valid strong certificate implies a valid regular certificate for the same
value, as shown in the proof of Strong-Grade Safety. So the same argument
applies to strong certificates as well.

### Synchronous Strong Validity

With $GST=0$, the honest sender broadcasts at time $t_s$; all honest parties
start by $t_s + \Delta$ and receive the proposal by $t_s + \Delta$. By
$t_s + 2\Delta$, every honest party has $n-f$ votes and delivers the regular
certificate. Each honest party's timer started no earlier than $t_s-\Delta$,
so at time $t_s+2\Delta$ its timer is at most $3\Delta$. Thus every honest
party delivers the regular certificate with $T_v \leq 3\Delta$, sends
`<Final, v, x>`, and by $t_s+3\Delta$ delivers a strong certificate for $x$.

## Proving the Outer Protocol

We now prove that the outer protocol satisfies the three provable consensus
properties above. The proof uses only the fact that in view $v$ the protocol
runs CGB with tag $v$ and with the Simplex voting rule as its
external-validity function, together with the five properties of CGB.

### Claim 1 (provable agreement)

Let $k$ be the first view with a valid commit certificate for value $x$. We show
by induction that any honest party accepting a proposal in any view $v > k$
accepts only $x$.

*Strong-Grade Safety* implies no valid skip certificate with tag $k$, and no
valid non-skip certificate with tag $k$ for a value different from $x$.

A fresh proposal in any view $v > k$ requires a skip certificate for all views
$y < v$, which includes tag $k$: impossible. So any accepted proposal uses a
certificate from some view $w < v$. Since $w < k$ also requires a skip
certificate for tag $k$, we have $w \geq k$. If $w = k$, *Strong-Grade
Safety* gives value $x$. If $w > k$, the certificate for view $w$ contains, or
implies the existence of, a regular certificate for its value. That regular
certificate contains an honest value vote, and by the induction hypothesis that
vote is for $x$.

Provable Agreement follows: any later commit certificate for a value $y$
contains an honest Final$(v,y)$ sender, who sent Final only after receiving a
regular certificate for $y$. That regular certificate contains an honest value
vote for $y$, and the induction argument above gives $y=x$.

### External Validity

Any valid commit certificate is a valid strong certificate of some CGB
instance. By the *External Validity* property of CGB, its value must be
externally valid.

### Claim 2 (liveness)

All honest parties eventually hold a valid commit certificate.

If any honest party delivers a strong certificate, *Certificate Totality*
propagates it to all. Otherwise, consider the first post-GST view $v^+$ with an
honest primary that starts after all earlier certificates have propagated. By
the $\Delta$-gap part of *Certificate Liveness*, all honest parties enter
$v^+$ within $\Delta$ of each other, satisfying *Synchronous Strong Validity*'s
premise.

By *Certificate Liveness*, every earlier view delivered at least one
certificate. Since all earlier certificates have propagated, the primary has
them. Let $w$ be the highest view below $v^+$ for which the primary has a
non-skip certificate, if such a view exists. For every $w<y<v^+$, the primary
has some certificate for view $y$, and by the choice of $w$ that certificate
must be a skip certificate. If no such $w$ exists, then the primary has skip
certificates for all views $y<v^+$. In either case the proposal satisfies the
Simplex voting rule at every honest party, so by *Synchronous Strong Validity*
all honest parties deliver a strong certificate in view $v^+$.


## Notes

There are multiple advantages for a modular decomposition of Simplex both in practice and in theory. In follow up posts we will show how to use this decomposition to obtain new protocols.


How does CGB differ from PBFT's Locked-Broadcast (LB)? First note that in LB
there is no notion of a skip certificate, just a lock certificate (similar to a
regular certificate in CGB). In both protocols the goal is to prove that the
lock/certificate is safe in the sense that there is no higher view in which
there could have been a commit:

1. In Simplex this is done by showing a skip certificate for every higher view.
2. For PBFT, this is done by showing the $n-f$ highest locks that are not higher than the proposal.

For where this decomposition sits in the broader Simplex line, see the [Simplex chapter](https://decentralizedthoughts.github.io/2026-05-25-chapter-simplex/).

## Acknowledgments

Many thanks to Kartik and Joachim for insightful comments and suggestions.

Your thoughts on [X](https://x.com/ittaia/status/2048079690364080367?s=20).
