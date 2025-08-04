---
title: Crusader Broadcast
date: 2022-06-19 03:11:00 -04:00
tags:
- consensus
author: Gilad Stern and Ittai Abraham
---

In  previous posts we showed that the classic [Dolev-Strong](https://decentralizedthoughts.github.io/2019-12-22-dolev-strong/) broadcast protocol takes $O(n^3)$ words and $t+1$ rounds and that [Dolev Reischuk](https://decentralizedthoughts.github.io/2019-08-16-byzantine-agreement-needs-quadratic-messages/) show that $\Omega(n^2)$ is needed and [it is also known that](https://decentralizedthoughts.github.io/2019-12-15-synchrony-uncommitted-lower-bound/) $t+1$ rounds are needed. So while the number of rounds is optimal, to this day it remains an open question of obtaining $O(n^2)$ broadcast against a strongly adaptive adversary (see [post](https://decentralizedthoughts.github.io/2021-09-20-optimal-communication-complexity-of-authenticated-byzantine-agreement/) for recent progress).

In this post we will show that for a problem that is easier than broadcast, called **Crusader Broadcast**, $O(n^2)$ words and $O(1)$ rounds is doable for any $f<n$ given a PKI. In later posts we will ask if $\Omega(n^2)$ words are needed for Crusader Broadcast and tie this result to known [Eclipse style attacks in the world of blockchain, and to new Dolev Reischuk type lower bounds](https://eprint.iacr.org/2022/730.pdf).


## Crusader Broadcast: from Byzantine to Omission

A basic tool in the distributed algorithm toolbox is a *non equivocation round*. In such a round, we have a sender $s$ that wants to send a single message $m$ to all parties. Without faults this is extremely straightforward to do: just send the message. With faults however, this can be more complicated. For example, if the sender is Byzantine, it might send different messages to different parties. If our protocol assumes that all parties receive the same message, this might break things.

In order to solve this issue, we use the notion of a non-equivocation round in which two nonfaulty parties may not output different messages $m\neq m'$. One way to model such a round is [Crusader Broadcast](https://decentralizedthoughts.github.io/2019-10-22-flavours-of-broadcast/), which is closely related to the notion of [Crusader Agreement](https://decentralizedthoughts.github.io/2021-10-04-crusader-agreement-with-dollars-slash-leq-1-slash-3$-error-is-impossible-for-$n-slash-leq-3f$-if-the-adversary-can-simulate/), which we discussed before.

For a formal definition, consider a network of $n$ parties with up to $f$ Byzantine faults. Let $s$ be a designated sender with some input $m$. Every party outputs either a message $m'$ from the protocol, or a special non-message value, $\bot$. This value is used to signify that either no message was received from the sender, or that conflicting messages were received.

A Crusader Broadcast protocol has the following properties:

* **Validity**: If $s$ is nonfaulty, then all nonfaulty parties output $m$.  
* **Weak Agreement**: If two nonfaulty parties output $m,m'$ such that $m\neq \bot$ and $m'\neq \bot$, then $m=m'$.

Observing the agreement property closely, we can see that if the sender is faulty, parties are always allowed to output $\bot$. However, if some nonfaulty party outputs $m$, then any other party must either output $m$ or $\bot$.

As done previously, we can also relax the requirements of the protocol to define $p$-correct Crusader Broadcast in which the properties must hold with probability $p$ or greater (for $0\leq p \leq 1$).

## Crusader Broadcast Protocol

Here is a simple Crusader Broadcast protocol, in a synchronous network, resilient to any number of faults $f$, assuming that $n>f$. The protocol assumes a public key infrastructure (PKI) which we model using a perfect signature scheme. What does that actually mean?

By a PKI setup, we mean that every party $i$ has a signing key $sk_i$ and a public key $pk_i$ associated with it. All parties know every public key, but only $i$ knows its signing key $sk_i$. Using these keys, parties can sign messages using the $Sign$ function. That is, $i$ can compute a signature $\sigma=Sign(sk_i,m)$ for the message $m$. Every party can then verify that signature by using the $Verify$ function. More specifically, $Verify(pk_i,m,\sigma)$ returns $1$ if $\sigma$ looks like a correct signature by party $i$ on the message $m$, and $0$ otherwise. For simplicity, we will assume that the signature scheme is perfect in the sense that only $i$ can produce a signature $\sigma$ for $m$ such that $Verify(pk_i,m,\sigma)=1$.

Let $\Delta$ be the maximal message delay in the system. The protocol works as follows:


* Round 0: The sender $s$ computes $\sigma=Sign(sk_s,m)$ and sends $\langle \text{value}, m, \sigma\rangle$ to all parties.
* Round 1: Every party initializes $val=\bot$ and waits for $\Delta$ time. After waiting, if a party received a single message $\langle \text{value}, m, \sigma\rangle$ from $s$ such that $Verify(pk_s,m,\sigma)=1$, they update $val$ to $m$ and forward the message by sending a $\langle \text{forward}, m, \sigma\rangle$ message to all parties.
* Round 2: Every party now waits for $\Delta$ time more time. If while it waits, a party receives a $\langle \text{forward}, m, \sigma\rangle$ message such that $Verify(pk_s,m,\sigma)=1$ and $m\neq val$, it updates $val$ to $\bot$. Finally, after the $\Delta$ time has passed, output $val$.

This protocol in words: The sender sends its signed message, parties wait for $\Delta$ time, and forward the first message they receive. They then wait for $\Delta$ more time, if they hear of any equivocation by the sender, they output $\bot$ and otherwise they output the value they heard from the sender (if they've heard any value). This protocol is also widely used as a building block in many consensus protocols and  distributed algorithms.

## Correctness
As usual, the validity property is almost obviously true, while the true insight comes in the agreement property.

***Claim 1***: The protocol achieves Validity for any $n>f$.

Assume the sender $s$ is nonfaulty. In that case, it starts by computing $\sigma=Sign(sk_s,m)$ and sending $\langle \text{value}, m, \sigma\rangle$ to all parties. Every nonfaulty party receives that message by time $\Delta$, sees that the signature verifies, and updates $val$ to $m$. The sender only sent a signature $\sigma$ on the message $m$, so no party receives a $\langle \text{forward}, m', \sigma'\rangle$ message such that $m'\neq m$, and the signature verifies. Therefore, no nonfaulty party reverts $val$ back to $\bot$, which means that they output $m$ after $\Delta$ more time has passed.

***Claim 2***: The protocol achieves Weak Agreement for any $n>f$.

In order to prove that, we need to show that no two nonfaulty parties output $m$ and $m'$ such that $m\neq \bot$ and $m'\neq \bot$, and yet $m\neq m'$. We will show that by assuming some nonfaulty party output a value $m\neq \bot$ and then show that every other nonfaulty party either outputs $m$ or $\bot$.

Assume some nonfaulty party $i$ outputs $m\neq \bot$ at the end of the protocol, and observe some other nonfaulty party $j$. If $i$ output $m$, then it received a message $\langle \text{value}, m, \sigma\rangle$ from $s$ with a verifying signature, and sent a $\langle \text{forward}, m, \sigma\rangle$ message to every party at time $\Delta$. Every nonfaulty party receives that message before time $2\Delta$ and sees that the signature verifies. Then, every nonfaulty party that has $val\neq m$ at that time updates $val$ to $\bot$ by time $2\Delta$. In other words, at time $2\Delta$, every nonfaulty party either has $val=m$ or $val=\bot$. Nonfaulty parties output $val$ after $2\Delta$ time, meaning that they all output $m$ or $\bot$, as required.

## Efficiency

The protocol described above has two main sending rounds. In the beginning $s$ sends $n$ messages. Parties then inform each other of the messages they received, in a quadratic all-to-all round. Overall, this protocol requires $\Theta(n^2)$ messages and words to be sent. 

## Conclusion

Do we actually need $O(n^2)$ messages for such a weak notion of agreement? In the next post we will show that for a pretty strong adversary, this message complexity is actually required, and tie this result to known Eclipse style attacks in the world of blockchain, and to new Dolev Reischuk type lower bounds.

### Scratch your brains
Can you turn this protocol to *linear*? under what conditions? 

Your thoughts/comments on [Twitter](https://twitter.com/ittaia/status/1538486701575782400?s=20&t=tPd5SjTv4rWnFb78CbqJ7Q).
