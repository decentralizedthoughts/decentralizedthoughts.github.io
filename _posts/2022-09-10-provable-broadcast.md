---
title: Provable Broadcast
date: 2022-09-10 08:00:00 -04:00
tags:
- consensus
- research
author: Ittai Abraham, Alexander Spiegelman
---

We explore a family of broadcast protocols in the authenticated setting in which a designated *sender* wants to create a *delivery-certificate* of its input value. After describing the base protocol we call **Provable Broadcast** ($PB$),  we explore the surprising power of simply running $PB$ two times in a row, then three times, and finally four times in a row. 

These protocols are secure against a [malicious adversary](https://decentralizedthoughts.github.io/2019-06-17-the-threshold-adversary/) controlling $f<n/3$ parties in the [asynchronous model](https://decentralizedthoughts.github.io/2019-06-01-2019-5-31-models/).

Provable Broadcast based protocols are the backbone of many authenticated consensus protocols. When used as part of a consensus protocol, the *delivery-certificate* of $PB$ is often called a *commit-certificate*. In this post, we focus just on the $PB$ primitive and hence use the term *delivery-certificate*. We will refer to it as a *commit-certificate* in the follow-up posts that explain consensus protocols that use $PB$.

  

**Provable Broadcast**: is a simple one round-trip building block going back to [Reiter 94](https://dl.acm.org/doi/pdf/10.1145/191177.191194)'s **Echo Broadcast**. Echo Broadcast produces a *delivery-certificate* proving that $n-2f$ honest parties delivered the sender's value. This is the *Weak-Availability* property. Moreover, even if the sender is Byzantine, the *Uniqueness* property guarantees that there is at most one such value.
Echo Broadcast can be slightly extended to *Validated Echo Broadcast*, which we call [Provable Broadcast](https://research.vmware.com/files/attachments/0/0/0/0/0/7/8/practical_aba_2_.pdf), which also provides an *External-Validity* property (see [below](#on-external-validity)). This allows sequencing provable broadcast instances to achieve stronger properties:

1. **Locked Broadcast**:  by running *two* consecutive $PB$s, we get a two round-trip protocol. This protocol additionally provides a *Unique-Lock-Availability* property: a *delivery-certificate* is a proof that $n-2f$ honest parties received a *lock-certificate* for this value, and no other value can have a *lock-certificate*.  Locked Broadcast is the main sub-loop of [Tendermint](https://arxiv.org/abs/1807.04938), [Casper FFG](https://arxiv.org/abs/1710.09437), [linear PBFT](https://research.vmware.com/files/attachments/0/0/0/0/0/7/2/sbft_scaling_up_byzantine_fault_tolerance_5_.pdf), [two-chain-HotStuff](https://arxiv.org/pdf/1803.05069v1.pdf).
2. **Keyed Broadcast**: by running *three* consecutive $PB$s, we get a three round-trip protocol. As before, a *delivery-certificate* is a proof that $n-2f$ honest parties received a *lock-certificate*. In addition, this protocol provides a *Unique-Key-Availability* property: if a *lock-certificate* exists, then $n-2f$ honest parties hold a *key-certificate* and there can only be one value with a *key-certificate*. Keyed Broadcast is the main loop of [three-chain-HotStuff](https://research.vmware.com/files/attachments/0/0/0/0/0/7/7/podc.pdf) and overcomes the *hidden lock problem*.
3. **Robust Keyed Broadcast**: by running *four* consecutive $PB$s, we get a four round-trip protocol. This protocol additionally provides a *Robust-Delivery* property: there is proof that at least $n-2f$ honest parties have a *Delivery-Certificate*.  Robust Keyed Broadcast is the main sub-loop of Asynchronous protocols: [VABA](https://research.vmware.com/files/attachments/0/0/0/0/0/7/8/practical_aba_2_.pdf), [ACE](https://arxiv.org/abs/1911.10486), [AllYouNeedIsDag](https://arxiv.org/abs/2102.08325).


*Note:* Some recent consensus protocols opt for *three* consecutive $PB$s for obtaining **Robust Locked Broadcast** that provides *Robust-Delivery* with *Unique-Lock-Availability* (but without *Unique-Key-Availability*), see [Tusk](https://arxiv.org/abs/2105.11827?context=cs.DC).

#### On External Validity
We assume there is some *External Validity* ($EV$) Boolean predicate that is provided to each party. $EV$ takes as input a  value $v$ and a $proof$. If $EV(v,proof)=1$ we say that $v$ is *externally valid*. A simple example of external validity is a check that the value is signed by the sender and/or is signed by the client that controls the asset etc. External validity is based on the framework of [Cachin, Kursawe, Petzold, and Shoup, 2001](https://www.iacr.org/archive/crypto2001/21390524.pdf). In later posts, we will extend $EV$ to also take the internal state of the party as input.

#### Properties of the Broadcast protocols 
All four protocols above  have the following properties:

* **Termination**: If the sender is honest and has an *externally valid* input $v$, then after a constant number of rounds the sender will obtain a *delivery-certificate* of $v$. Note that the Termination property requires just the sender to hold the certificate.
* **Uniqueness**: There can be at most one value that obtains a *delivery-certificate*. So there cannot be two *delivery-certificates* with different values.
* **External Validity**: If there is a *delivery-certificate* with value $v$ and $proof$ then $v$ is *externally valid*. So $EV(v,proof)=1$.

The four protocols differ by providing additional properties:

1. *Echo Broadcast* obtains **Weak-Availability**: If a  *delivery-certificate* exists for $v$ then at least $n-2f$ honest parties hold the value $v$.
2. *Locked Broadcast* obtains **Unique-Lock-Availability**: If a  *delivery-certificate* exists for $v$ then there can only exist a *lock-certificate* for $v$ and there are at least $n-2f$ honest parties that hold this *lock-certificate*.
3. *Keyed Broadcast* obtains **Unique-Key-Availability**: If a *lock-certificate* exists for $v$ then there can only exist a *key-certificate* for $v$ and there are at least $n-2f$ honest parties that hold this *key-certificate*.
4. *Robust Keyed Broadcast* obtains **Robust-Delivery**: If a *robust-certificate* exists then there are at least $n-2f$ honest parties that hold a *delivery-certificate*. 

## Provable Broadcast (Validated Echo Broadcast) and Weak-Availability


Provable Broadcast calls a Boolean external validity function $EV(v,proof)$ as a subroutine. For now, consider the case where $EV$ just checks that $proof$ is a valid signature on $v$ relative to the designated sender’s public key. 


$PB$ is a super simple protocol: the Sender sends a value, parties check the *first* value they see is *valid*, and if it is, *sign* it back to the sender. The sender accumulates signatures  until a *delivery-certificate* is formed.

![Provable Broadcast](https://i.imgur.com/YqdQCKH.jpg)


```
Sender s:
input v
input proof = <v>_s //signature by s on v

send <v, proof>_s to all

Party i:
For the first <v, proof> received from s:
    If EV(v, proof) then send <v, proof>_i to s

Delivery-Certificate for v:
    n-f distinct signers on <v, proof>
```

***Proof***: 

*External Validity*: since honest parties check $EV$ and at least $n-2f$ honest parties need to sign for a *delivery-certificate* to form.

*Uniqueness* follows from quorum intersection - seeking a contradiction assume there are two values $v \neq v'$ with a *delivery-certificate*. Hence there are two sets of size $n-f$, and they must intersect in at least $n-2f$ parties. Since $n>3f$, this implies that at least $f+1$ parties signed both certificates, but we assume the adversary can corrupt up to $f$ parties. Hence contradiction.

*Termination* follows from the sender needing to wait for only $n-f$ signatures for a *delivery-certificate* to form.

*Weak-availability* from counting: at least $n-f$ parties signed for the *delivery-certificate* to form, so at least $n-2f \geq f+1$ of them are honest. 

Make sure you go over the proof once in detail. Now, let's start composing :-)

## Locked Broadcast and Unique-Lock-Availability

The sender runs **two** $PB$ consecutively: $PB_1,PB_2$. For $PB_1$ the external validity function $EV_1$ for now just checks the sender signature (in later posts, we will use Locked Broadcast as part of a consensus protocol, and add a PBFT-style view change check to $EV_1$). For $PB_2$ we define $EV_2(v,p)$ to check that $p$ is a *delivery-certificate* on $v$ from $PB_1$ (so $EV_2$ checks that $p$ contains $n-f$ distinct valid signatures on $<v,proof>$). That’s it!

![Locked Broadcast](https://i.imgur.com/dKKXky7.jpg)


```
Sender s:
input v
input proof = <v>_s //signature by s on v

send <v, proof>_s to all
send <v, cert_1(v)>_s to all when you obtain cert_1(v)

Party i:
For the first <v, proof> you receive from s:
    If EV_1(v,proof) then send <v, proof>_i to s

For the first <v, cert_1(v)> you receive from s:
    If EV_2(v, cert_1(v)) then send <v, cert_1(v)>_i to s
    
Cert_1(v), "lock-certificate for v":
    n-f distinct signers on <v, proof> 

Cert_2(v), "delivery-certificate for v":
    n-f distinct signers on <v, cert_1(v)>
```

***Proof***: We get *External Validity* and *Uniqueness* from $PB_1$. *Termination* follows from needing just $n-f$. *Unique-Lock-Availability* follows from the Uniqueness of $PB_1$ and the Weak-availability of $PB_2$. Directly: if there is a $cert_2(v)$ then from $PB_1$ there can be at most one $cert_1(v)$ and due to $PB_2$ at least $n-2f$ honest hold $cert_1(v)$.

*Note 1*: Unique-Lock-Availability is the core of what allows a safe view-change in all [authenticated PBFT](https://pmg.csail.mit.edu/papers/osdi99.pdf) style protocols.
<details>
  <summary><b>More on PBFT-style view change</b>:</summary> <p>
  
  
 

It means that if a party committed to $v$ in view $k$ due to seeing a Certificate $cert_2(v,k)$ then any leader of any view $>k$, by querying $n-f$ parties, must intersect with one of the $n-2f$ honest holding $cert_1(v,k)$ hence this query must contain $cert_1(v,k)$, and no other $cert_1(v',k)$ can exist (here we use the Unique-Lock-Availability property). 

Moreover, the new leader, by sending all the $n-f$ certificates it queried as the proof, and proposing value $v$ from $cert_1(v,k)$ of the highest view $k$ in this set, can prove its proposal is safe. $EV_1$ checks that the proposal is indeed of the highest view, using this proof. 
    </p></details>


*Note 2*: In some protocols, Unique-Lock-Availability is not enough. When using Tendermint-style view change, if not using a timeout, the new leader may not be aware of all the Lock-Certificates held by honest parties. This is called the  **hidden lock problem**. HotStuff is a Tendermint-style protocol that has the property that if any honest party has a Lock-Certificate then the new leader will not miss this lock, even if the new leader just waits for the first $n-f$ responses. HotStuff obtains this property by using *Keyed Broadcast*.  


<details>
  <summary><b>More on Tendermint-style view change</b>:</summary> <p>
  
  
 

In the Tendermint view change protocol, the new leader only sends $cert_1(v,k)$, but does not prove this is the certificate with the highest view. Instead,  $EV_1$ checks that the proposed value $v$ has a $cert_1(v,k)$ from a view $k$ that is at least as high as the highest $cert_1(v',k’)$ that the validator has ever seen. In a later post we will cover this in detail. For now, it's sufficient to grasp at a high level a problem with this protocol: a new honest leader, that does not use a timeout,  may query $n-f$ parties and observe the highest $cert_1(v,k)$ is from view $k$, but due to it only waiting for the first $n-f$, may miss a $cert_1(v',k’)$ held by an honest party with $k<k’$. This may cause the new leader to fail Termination of its $PB$, and is called the *hidden lock problem*. 
    </p></details>



## Keyed Broadcast and Unique-Key-Availability

Solving the hidden lock problem is critical for *efficient* solutions in asynchrony and *efficient* solutions obtaining responsiveness in partial synchrony. 

In Keyed Broadcast the sender runs **three** $PB$s consecutively: $PB_1,PB_2, PB_3$. As before, for $PB_1$ we assume for now $EV_1$ just checks the sender signature (in later posts, we will use Keyed Broadcast as part of a consensus protocol, and add a Tendermint-style lock check condition to $EV_1$). As before, $EV_2(v,proof)$ checks that $proof$ is a delivery-certificate on $v$ from $PB_1$. As you can imagine, $EV_3(v,proof)$ just checks that $proof$ is a *delivery-certificate* on $v$ from $PB_2$. That’s it!

![](https://i.imgur.com/aK4WmFP.jpg)



```
Sender s:
input v
input proof = <v>_s //signature by s on v

send <v, proof>_s to all
send <v, cert_1(v)>_s to all when you obtain cert_1(v)
send <v, cert_2(v)>_s to all when you obtain cert_2(v)

Party i:
For the first <v, proof> received from s:
    If EV_1(v,proof) then send <v, proof>_i to s

For the first <v, cert_1(v)> received from s:
    If EV_2(v, cert_1(v)) then send <v, cert_1(v)>_i to s
    
For the first <v, cert_2(v)> received from s:
    If EV_3(v, cert_2(v)) then send <v, cert_2(v)>_i to s

Cert_1(v), "key-certificate for v":
    n-f distinct signers on <v, proof> 

Cert_2(v), "lock-certificate for v":
    n-f distinct signers on <v, cert_1(v)>

Cert_3(v), "delivery-certificate for v":
    n-f distinct signers on <v, cert_2(v)>
```

***Proof***: *External Validity* and *Uniqueness* follow from $PB_1$, *Unique-Lock-Availability* from  $PB_2 + PB_3$, *Unique-Key-Availability* follows from $PB_1 + PB_2$, and *Termination* follows from needing just $n-f$ in each of the three $PB$s. 

To guarantee that there is no hidden lock: if an honest party has a *lock-certificate*  $cert_2(v)$ then at least $n-2f$ honest have a *key-certificate* $cert_1(v)$ and there cannot be *key-certificates* on other values (due to $PB_1$). Hence during view change, even in asynchrony, a new honest leader is guaranteed to see at least one *key-certificate* for any *lock-certificate* held by any honest party. So the new honest leader can propose the value that has the *key-certificate* with the highest view.

In partial synchrony, this three round-trip protocol is the core of how [HotStuff](https://research.vmware.com/files/attachments/0/0/0/0/0/7/7/podc.pdf) obtains **responsiveness**.

Finally, for termination in asynchrony, we want to know that many parties have a *delivery-certificate*. Simply add one more $PB$!

## Robust Keyed Broadcast and Robust-Delivery

Run **four** consecutive $PB$s, where the fourth $PB$'s goal is to output a robust-certificate that indicates that at least $n-2f$ honest parties hold a delivery-certificate. A ```Deliver v``` event is explicitly added when a valid *delivery-certificate*, $cert_3(v)$, is received.

![](https://i.imgur.com/pVTaCSY.jpg)


For completeness here is the protocol:

```
Sender s:
input v
input proof = <v>_s 

send <v, proof>_s to all
send <v, cert_1(v)>_s to all when you obtain cert_1(v)
send <v, cert_2(v)>_s to all when you obtain cert_2(v)
send <v, cert_3(v)>_s to all when you obtain cert_3(v)

Party i:
For the first <v, proof> received from s:
    If EV_1(v,proof) then send <v, proof>_i to s

For the first <v, cert_1(v)> received from s:
    If EV_2(v, cert_1(v)) then send <v, cert_1(v)>_i to s
    
For the first <v, cert_2(v)> received from s:
    If EV_3(v, cert_2(v)) then send <v, cert_2(v)>_i to s

For the first <v, cert_3(v)> received from s:
    If EV_4(v, cert_3(v)) then 
        Deliver v; and
        send <v, cert_3(v)>_i to s


Cert_1(v), "key-certificate for v":
    n-f distinct signers on <v, proof> 

Cert_2(v), "lock-certificate for v":
    n-f distinct signers on <v, cert_1(v)>

Cert_3(v), "delivery-certificate for v":
    n-f distinct signers on <v, cert_2(v)>

Cert_4(v), "robust-certificate for v":
    n-f distinct signers on <v, cert_3(v)>
```

***Proof***: *Termination* is again obtained since we just need $n-f$ valid responses. *Robust-Delivery* follows from Weak-Availability of $PB_4$ and the uniqueness of $PB_1$.


## Linearity

All $PB$ protocols have a linear message complexity. When using threshold signatures they require a total of just $O(n)$ words of communication. When using multi-signatures they require just $O(n)$ authenticators (where each authenticator includes $n$ bits and a single signature whose length depends on the security parameter).

## Next Posts and Notes


In the next posts, we will see how:
1. Locked Broadcast is the core building block of [two-round-Hotstuff, 2018](https://arxiv.org/pdf/1803.05069v1.pdf).
2. Keyed Broadcast is the core building block of [Hotstuff, 2018](https://research.vmware.com/files/attachments/0/0/0/0/0/7/7/podc.pdf).
3. Robust Keyed Broadcast is the core building block for obtaining a [VABA, 2018](https://arxiv.org/pdf/1811.01332.pdf). The exposition in this post is based on the *$f+1$-Provable-Broadcast* and *$4$-stage-$f+1$-Provable-Broadcast* of [VABA, 2018](https://arxiv.org/pdf/1811.01332.pdf).



Your thoughts and comments on [Twitter](https://twitter.com/ittaia/status/1569035923668574211?s=21&t=c8iwi-gLXT9wLT-o0wnUbQ).
