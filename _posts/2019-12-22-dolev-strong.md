---
title: Dolev-Strong Authenticated Broadcast
date: 2019-12-22 12:05:00 -05:00
tags:
- dist101
author: Ittai Abraham, Kartik Nayak
---

This post is about the classic result from 1983 on authenticated broadcast against a Byzantine adversary:

**Theorem ([Dolev-Strong \[1983\]](https://www.cse.huji.ac.il/~dolev/pubs/authenticated.pdf)):** *there exists an authenticated protocol for solving broadcast, against any adversary controlling $t<n$ out of $n$ parties, in $t+1$ rounds, using $O(n^2t)$ words*


Recall [Broadcast properties](https://decentralizedthoughts.github.io/2019-06-27-defining-consensus/): (1) *Termination* -  all honest parties decide and terminate; (2) *Validity* - if the leader is honest, its value is the decision value; and (3) *Agreement* - all honest parties decide the same value.


The Dolev-Strong protocol requires: (1) a *synchronous* model, in this post, we will assume *lock-step*; (2) an *authenticated* setting.  In this setting, we assume a PKI infrastructure. Denote the signature of message $m$ by party $i$ as $sign(m,i)$. We assume signature unforgeability.

As a first attempt, let's try to implement Broadcast for $t=1$ in 2 rounds. In the first round, the leader sends a signed message. In the second round, an honest party forwards the leader message to everyone:

```
// Attempt 1:

Round 1: Leader (party 1) sends message <v, sign(v,1)> to all parties
Round 2: If party i receives <v, sign(v,1)> from leader,
            then add v to V_i and send <v, sign(v,1)> to all
End of round 2: 
         If party i receives <v, sign(v,1)> from anyone
            then add v to V_i
Decision rule:
         If the set V_i contains only a single value v,
            then output v
         Otherwise output a default value bot
```

**Validity**: if the leader is honest then due to signature unforgeability, all honest parties will see exactly a single value.

**Termination**: All parties terminate at the end of round 2.

**Agreement (partial)**: If a malicious leader sends a value to some honest in round 1, all honest parties will receive it at the end of round 2. If a malicious leader sends two different values in round 1, then all honest parties will see two different values and decide $\bot$.

So does this protocol work?

No! the problem with agreement is that a Byzantine leader can send no value in round 1, then send a value to only a few honest parties in round 2. The honest parties who receive the value will output that value whereas other honest parties will output a $\bot$.

The core problem is that you may learn the decision value in the last round (round 2) but you are not sure that all other honest parties will also receive this value. You cannot forward your messages because this is the last round. Dolev and Strong show a very elegant way to guarantee agreement even if the value decided is revealed in the last round.

In round 1: accept a value if it's signed by the leader, but in round 2: accept a value only if it's signed by both the leader and another party.


```
// Attempt 2:

Round 1: Leader (party 1) sends message <v, sign(v,1)> to all parties
Round 2: If party i receives <v, sign(v,1)> from leader,
            then add v to V_i and send <v, sign(v,1), sign(v,i)> to all
End of round 2: 
         If party i receives <v, sign(v,1), sign (v,j)> from j>1
            then add v to V_i
Decision rule:
         If the set V_i contains only a single value v,
            then output v
         Otherwise output a default value bot
```

This protocol is resilient to 1 Byzantine failure because you only accept a value in the last round if t+1=2 parties signed it! if there are two signatures then one of them is from an honest party, so all honest parties will see this value. 

The principle is to only accept a value in the last round if its contents can certify that all parties have received this value. This leads to a very powerful idea in the synchronous model:
***The validity of a message is a function also of the time it is received***

The Dolev-Strong protocol implements this idea via **signatures chains**. Signature chains have two essential properties that allow honest parties to agree on a value at the end of $t+1$ rounds.
- A signature chain consists of signatures from *distinct* parties. So, if we have a signature chain of length $t+1$, it will certainly contain an honest signature by honest party $h$. Party $h$ can send the value to all parties.
- In round $i$, an honest party will accept (consider valid) only a signature chain of length $i$. So even if the adversary forms a Byzantine-only chain of length $\leq t$, then if it sends this chain in round $t+1$ it will not be accepted.

Messages in the protocol are signature chains where a *k-signature chain* is defined recursively as follows:

A **1-signature chain** on $v$ is a pair $(v, sign(v,1))$.

For $k>1$, a **k-signature chain** on $v$ is a pair $(m, sign (m,i))$ where $m$ is a $(k-1)$-signature chain on $v$ that *does not* contain a signature from $i$. In other words, a message (signature chain) received by party $i$ at the end of round $k$ is said to be valid if
- The first signer of the signature chain is the leader
- All signers in the chain are distinct
- All signatures are valid
- The signature chain has length $k$


The protocol:
```
// Leader (party 1) with input v

Round 1: send <v, sign(v,1)> to all parties.
```

Party $i$ does the following:
```
// Party i in round j = 2 to t+1

For a message m received in round j-1:
  if party i has sent less than two messages; and
    if m is a valid (j-1)-signature chain on $v$ not already signed by i, then
        add v to V
        send <m, sign(m,i)> to all parties

For a message m received in round t+1:
  if m is a valid (t+1)-signature chain on $v$  not already signed by i, then
        add v to V
```



```
// Party i decision rule

Decision at the end of round t+1:
  Let V be the set of values for party i received a valid signature chain
  If |V|=0 or |V|>1, then decide default value bot
  Otherwise decide v, where V={v}
```

The protocol satisfies agreement, validity, and termination:

**Termination**: The protocol is deterministic and terminates in $t+1$ rounds.

**Validity**: The (honest) leader will only sign one value, and this value will be sent to all honest parties in the first round. Due to the unforgeability of digital signatures, no other signature chain can exist.

**Agreement.** If an honest party receives a $k$-signature chain at the end of round $k$, then it will send it to all honest parties in round $k+1$. This holds for all rounds except the last round, round $t+1$. But since the honest party can only receive a $t+1$-sized chain in round $t+1$ and a $t+1$-sized chain contains at least one honest party $h$, $h$ must have already sent this value to all other honest parties. Thus, every value received by one honest party will be received by all other parties. (This does not hold in the case where the leader has sent more than two values. But the protocol ensures that all honest parties receive at least two of the values and hence they will agree on a default value).

#### Complexity measures and Notes
Every party sends at most two values, and each value may contain $O(t)$ signatures. The total communication is $O(n^2t)$ signatures.

Here is an open question: for $t<n$, reduce communication to $o(n^3)$ against some type of adaptive adversary, or perhaps show that $O(n^3)$ is required under some conditions.

Note that this protocol relies heavily on synchrony and [does not work for $t \geq n/2$](https://decentralizedthoughts.github.io/2019-11-02-primary-backup-for-2-servers-and-omission-failures-is-impossible/) in the client-server model where the clients are passive or maybe offline.
In the Dolev-Strong protocol,  an online server accepts a length $k$ chain in round $k$ but must reject it in round $>k$. However, there is no way for a server to prove to a client when it received a message (other than to sign and send and the client to verify online in the next round).

Another great description and proof of the Dolev-Strong protocol can be found in Jonathan Katz's [Advanced Topics in Cryptography course notes](http://www.cs.umd.edu/~jkatz/gradcrypto2/NOTES/lecture26.pdf). In the blockchain space, the Dolev-Strong protocol is mentioned by [Spacemesh](https://spacemesh.io/byzantine-agreement-algorithms-and-dolev-strong/). Buterin's [post](https://vitalik.ca/general/2018/08/07/99_fault_tolerant.html) explains how to implement Dolev-Strong in the synchronous model and hints at how it could be used as a finality gadget for stronger $99\%$ fault tolerance for online observers.

Historically, a very similar protocol for the authenticated setting was suggested by Lamport, Shostak, and Pease in their seminal paper [The Byzantine Generals problem](https://lamport.azurewebsites.net/pubs/byz.pdf). However, it seems that the authenticated protocol in Section 4 does not explicitly mention that length $k$ chains must not be accepted at time $>k$.


Please leave comments on [Twitter](https://twitter.com/ittaia/status/1208871356516966401?s=20)
