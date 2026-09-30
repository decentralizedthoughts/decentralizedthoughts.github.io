---
title: Information Checking Protocols
date: 2026-09-30 04:00:00 -05:00
tags:
- cryptography
author: Ittai Abraham, Gilad Asharov, Gilad Stern
---

The siege is over. The colony's **archivist** brings its **captain** a recorded message from their **founder**, Hari. He predicted the attack, she says, and the choices that would let them survive.

Hari is long dead. Did he foresee the siege, or did the archivist fake the recording last week?

This story is inspired by Hari Seldon's recorded messages in [Isaac Asimov's *Foundation*](https://en.wikipedia.org/wiki/Foundation_%28Asimov_novel%29). Before the expedition leaves Earth, Hari records his prediction and entrusts the message to the archivist. The captain is to hear it only after the colony's first crisis. Knowing it beforehand could change her decisions.

The captain agrees to wait, but wants a way to check that the archivist has preserved Hari's words. The archivist refuses to spend thirty years guarding a message only to be accused of forging it. What if Hari has arranged for the genuine message to fail the captain's check? He will be long dead when she is left to take the blame. She wants to discover that betrayal before she leaves Earth.

A [digital signature based on public key cryptography](https://en.wikipedia.org/wiki/Digital_signature) seems an obvious answer. Hari signs the message, and his public key lets the archivist verify it before departure and the captain verify it when it is revealed. But the ship will travel so close to the speed of light that thirty years will pass aboard while three thousand pass on Earth and at their destination. The civilizations they encounter may have vastly more powerful computers, or know mathematics that nobody on Earth has yet imagined. A signature trusted at departure might be easy to forge on arrival.

All three can still meet before launch. Can they prepare now so that the captain can authenticate the message decades later, without learning its contents today and without relying on computational problems remaining hard?

This is the problem of **information checking**. Information checking protocols, or ICPs, provide **statistical security against a computationally unbounded adversary**. Their guarantees allow a small error probability, but do not depend on the adversary's computing power. Even three thousand years of faster computers and new mathematics would not weaken that guarantee.

## Information Checking

In the Information Checking Protocol (ICP) there are three parties: a **dealer** $D$, an **intermediary** $I$, and a **receiver** $R$. In the story, these are the founder, archivist, and captain.


[Rabin and Ben-Or (1989)](https://www.cs.umd.edu/~gasarch/TOPICS/secretsharing/rabinVSS.pdf) introduced information checking as a building block for verifiable secret sharing and secure multi party computation. In this post we present a variation of the ICP of [Cramer, Damgård, Dziembowski, Hirt, and Rabin (1999)](https://crypto.ethz.ch/publications/files/CDDHR99.pdf).


### Definition and Guarantees


The protocol has two phases: commitment and revelation.
The first phase is a *commitment* phase, in which all three parties set the interaction up, making sure that the intermediary will be able to provide the correct message in the future.
Think of this stage as the dealer sending a signed message to the intermediary.

We will work with messages over a finite field $\mathbb{F}$ of order $q$.
The size of the field acts as a security parameter: the larger the field, the more secure the protocol (but messages grow accordingly).
The error probability in each security bound below is at most $1/q$ and we choose $q$ large enough to make this negligible.

We formally describe the protocols with the dealer and intermediary already holding the message as input, and the protocol just authenticating it (we can think of the dealer as sending the message in advance).
In the commitment phase, the dealer calls $\mathsf{Commit}(m)$ and the intermediary calls $\mathsf{Verify}(m')$ with $m,m'\in\mathbb{F}$.
The intermediary finds out if the commitment succeeds and outputs $OK$ if it does.

Following the commitment phase, we can proceed to the reveal phase. In that phase, the intermediary can call $\mathsf{Reveal}()$, after which the receiver outputs the message $m'$.

Thinking about our story above, we want the following properties to hold:

1. **Correctness.** If all parties are honest and $m=m'$, verification succeeds. In addition, if the intermediary calls $\mathsf{Reveal}$ later, then the receiver outputs $m$.
2. **Unforgeability** (against a dishonest intermediary). If the dealer and receiver are honest, the probability that the receiver outputs a message $m'\ne m$ in the reveal phase is negligible.
3. **Nonrepudiation** (against a dishonest dealer). If the intermediary and receiver are honest, the probability that the intermediary outputs $OK$ in the commitment phase, but the receiver does not output $m'$ in the reveal phase is negligible.
4. **Perfect privacy** (against a dishonest receiver). If the dealer and intermediary are honest and $m=m'$, the receiver learns nothing about that message before revelation.


Digital signatures separate key setup from signing. Once the signing key is established, $D$ can sign messages without $R$ participating. $R$ then verifies the messages and signatures using $D$'s public key. In the ICP protocol, the commitment phase also establishes $R$'s private verification data for the message, and all three parties must participate in the commitment phase.

In addition, a digital signature can be checked by anyone with $D$'s public key. However, in the ICP protocol, verification uses private data held by the designated receiver. $R$ can forward the message, but the ICP does not give it publicly verifiable proof that the message came from $D$.


### The Protocol


The high level idea is simple: the dealer samples a line of the form $ax+b$, and sends the description of the line (i.e., the coefficients $a,b$) to the receiver, while sending the evaluation at $m$ (i.e., $t=am+b$) to the intermediary.

The description of the line is entirely independent of $m$, so it reveals no information. Then, during the reveal phase, the intermediary can send both $m$ and $t$ to the receiver, who can then check that the evaluation is correct.

The intermediary doesn't know anything about $a,b$ other than the fact that $am+b=t$.
This is one equation in two unknowns, so there is still one degree of freedom given its information.
If $I$ were to try to send an incorrect message $m'$, it would have to guess the unique $t'=am'+b$, which is highly unlikely.

Now comes a slight complication: the dealer might be dishonest. It could give $I$ and $R$ inconsistent information, leaving $I$ holding a message that $R$ will refuse to accept.
To check that the dealer is not lying, the dealer samples two lines $a_0x+b_0$ and $a_1x+b_1$, and sends both descriptions to $R$ and both evaluations to $I$.
$R$ then sends a random combination of the lines to $I$.
This combination keeps the second line hidden, while allowing $I$ to combine the evaluations in the same way and check that its evaluations are correct.

**Commitment Phase**




In the protocols below, it is important that each party proceeds to a given round after completing everything in the previous lines. For example, in line $4$, $R$ sends $c$ to $D$ after receiving $\mathsf{Ack}$ from $I$, *and* completing line $2$.

**$\mathsf{Commit}(m)$**:

1. The dealer acts as follows:

   Sample independent uniform $a_0,a_1,b_0,b_1\in\mathbb F$. Set

   $$
    t_0=a_0 m+ b_0,
   \qquad
    t_1=a_1 m+ b_1.
   $$
   Send $( m, t_0, t_1)$ to $I$.
   Send $(a_0, b_0,a_1, b_1)$ to $R$.
2. **Upon** receiving $(a_0, b_0,a_1, b_1)$ from $D$, $R$ does the following:

   Uniformly sample $c\in\mathbb F$. Set

   $$
   A=a_0+ca_1,
   \qquad
    B= b_0+c b_1.
   $$
   Send $C_R=(c,A, B)$ to $I$.



**$\mathsf{Verify}(m')$**:

3. The intermediary waits to receive $(m, t_0, t_1)$ from $D$ and $C_R$ from $R$, and then does the following: If $m= m'$, send $\mathsf{Ack}$ to $R$.
4. **Upon** receiving $\mathsf{Ack}$ from $I$, $R$ sends $c$ to $D$.
5. **Upon** receiving $c$ from $R$, $D$ sends $C_D=(c,a_0+ca_1, b_0+c b_1)$ to $I$.
6. **Upon** receiving $C_D$ from $D$, $I$ does the following:  If $C_D=C_R$ and $t_0+c t_1=A m'+ B$, output *OK*.

The extra steps ensure that $I$ receives its message and tags before $D$ learns the challenge $c$, and that $D$ confirms the combined coefficients before $I$ checks its tags.
This confirmation also protects privacy when the protocol is used as part of a larger protocol: a dishonest $R$ cannot supply incorrect combined coefficients and learn about $m$ by observing whether $I$ outputs $OK$.

**Reveal**

7. The intermediary sends $(m', t_1)$ to $R$.
8. **Upon** receiving the first pair $(m', t_1)$ from $I$, $R$ checks if $t_1=a_1m'+b_1$. If this is the case, output $m'$.



<iframe src="https://decentralizedthoughts.github.io/uploads/icp-player.html" width="100%" height="900" title="Information Checking Protocol: step through Rules 1 to 8" style="border:0;" loading="lazy"></iframe>

[Open the interactive protocol at full size](https://decentralizedthoughts.github.io/uploads/icp-player.html)

<!--
[![Animated message flow between the dealer, intermediary, and receiver in Rules 1 through 8.](https://decentralizedthoughts.github.io/uploads/icp-protocol.gif)](https://decentralizedthoughts.github.io/uploads/icp-protocol.gif)

*One successful execution of the protocol. Tap or click to view at full size.*
-->

### Why It Works

**Correctness.** Suppose all parties are honest and $D$ and $I$ input the same message $m$. The dealer sends evaluations and coefficients to $I$ and $R$, respectively, after which $R$ sends a random combination $(c,A,B)$ to $I$.
$I$ sends an $\mathsf{Ack}$, after which $R$ sends $c$ to $D$.
The dealer then performs the same computation as $R$, and sends the same tuple $(c,A,B)$ to $I$.
Finally, $I$ sees that it receives the same tuples, sees that its evaluations are correct, and outputs $OK$.

If $I$ calls $\mathsf{Reveal}$, it sends the correct message $m$ and evaluation $t_1$. $R$ sees that the evaluation is correct and outputs $m$.

**Nonrepudiation.** Suppose $I$ and $R$ are honest.
$D$ only finds $c$ out after both $I$ and $R$ receive messages from it, as $R$ waits to receive an $\mathsf{Ack}$ message before sending $c$.
The dealer's initial messages are fixed independently of $c$.
We would like to bound the probability that $I$ outputs $OK$, but $R$ does not output $m'$ during the reveal phase.

The only way that $I$ would not be able to reveal the message $m'$, is if $t_1\neq a_1 m' + b_1$, where $t_0,t_1$ are the values it received from $D$, and $a_0,a_1,b_0,b_1$ are the values $R$ received from $D$.
However, if $D$ sent an incompatible $t_1$ value, then there is a tiny probability of $I$'s verification succeeding.
In particular, for $I$ to output $OK$, it must be the case that:
$$
    t_0+ct_1 = Am'+B = (a_0+ca_1)m' + (b_0+cb_1) = (a_0 m' + b_0) + c (a_1m'+b_1).
$$

Using the fact that $t_1\ne a_1m'+b_1$, we can isolate $c$ and see that it must equal:
$$
    c = -\frac{t_0-a_0m'-b_0}{t_1-a_1m'-b_1}.
$$
Since $c$ is uniform and independent of those fixed messages, this equality holds with probability $1/q$.

**Unforgeability.** Suppose $D$ and $R$ are honest. Consider $I$'s view before its forgery attempt. It holds the message, the two evaluations, and the random combination chosen by $R$. In other words, it has the values $m, t_0, t_1, c, A, B$.
For these values, it knows that there are values $a_0,b_0,a_1,b_1\in\mathbb{F}$ such that:

$$t_0 = a_0m+b_0,\quad t_1=a_1m+b_1, \quad A = a_0 + c a_1,\quad B=b_0+cb_1.$$

This looks bad, these are four equations in four variables, when considering the intermediary's view as constant.
Luckily, these equations are linearly related!
In particular:
$$
Am+B=t_0+ct_1.
$$

This means that there is still a single degree of freedom in the system.

For our purposes, we want to show that $a_1$ is independent of $I$'s view.
For any choice of $a_1$ there is a single possible assignment of all other variables: $t_1$ and $A$ define $b_1$ and $a_0$, then using these values, $B$ (or $t_0$) defines $b_0$.
This means that each $a_1$ is at least possible.

Each choice of $a_1$ determines exactly one compatible key tuple. All key tuples were sampled with equal probability, so $a_1$ remains uniform given $I$'s view.


However, $I$ successfully revealing a message $m'\ne m$ is equivalent to it guessing $a_1$.
To forge such a message, $I$ will have to send $m',t'$ such that $t'=a_1m'+b_1$, because $R$ only accepts messages for which this holds.
In addition, $I$ knows that $t_1=a_1m+b_1$.
Combining these two equations, we get:

$$
t'-t_1=(a_1m' + b_1) - (a_1 m + b_1) = a_1(m'-m).
$$

Since $m'-m\ne0$, $I$ could perform the same calculation, divide by $m'-m$ and get:

$$
a_1=\frac{t'-t_1}{m'-m}.
$$

In other words, forging a message is equivalent to guessing $a_1$, which $I$ can only do with probability $1/q$.

**Perfect privacy.** Suppose $D$ and $I$ are honest and input the same message $m$.
The coefficients $a_0,b_0,a_1,b_1$ are sampled independently of $m$. Since $D$ and $I$ are honest and have matching inputs, $I$ sends $\mathsf{Ack}$ regardless of the values in $C_R$. Thus, neither the coefficients nor the acknowledgment reveal information about $m$ to $R$.

In addition, for any choice of $c$, $I$ only checks the received messages if it receives the same (correct) random combinations $(c,a_0+ca_1,b_0+cb_1)$ from $D$ and $R$, and thus it only outputs $OK$ if $R$ sent the correct values, which $R$ already knows.

**Communication.** For a message $m\in\mathbb F$, parties send a constant number of field elements throughout both phases. The total communication is therefore $O(\log q)$ bits, or $O(1)$ field elements.


Your thoughts/comments on [X](TBD).