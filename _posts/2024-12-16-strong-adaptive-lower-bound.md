---
title: Agreement against strongly adaptive adversaries needs quadratic communication
date: 2024-12-16 07:30:00 -05:00
tags:
- lowerbound
- adaptive
author: Ittai Abraham, Kartik Nayak, Ling Ren
---

In this post, we prove a result of [Abraham, Hubert Chan, Dolev, Nayak, Pass, Ren, Shi, 2019](https://users.cs.duke.edu/~kartik/papers/podc2019.pdf) showing that:

**Theorem: Any broadcast protocol in synchrony that is resilient to $f$ strongly adaptive omission failures and has less than $1/8$ probability of error must have an expected communication of at least $f^2/64$ messages.**  

The classic [Dolev and Reischuk 1982](https://www.cs.huji.ac.il/~dolev/pubs/p132-dolev.pdf) lower bound for *deterministic* protocols is covered [in this post](https://decentralizedthoughts.github.io/2019-08-16-byzantine-agreement-needs-quadratic-messages/).

The lower bound in this post extends this proof to holds even for *randomized protocols* but assumes the adversary is [strongly adaptive](https://decentralizedthoughts.github.io/2019-06-07-modeling-the-adversary/).

> What are strongly adaptive adversaries and why are they required for the lower bound?

* A strongly adaptive adversary can adaptively corrupt parties and, in addition, once a party is corrupted, it can *claw back* messages that have been sent but not delivered yet.
* The core idea of the Dolev and Reischuk lower bound is to isolate some party $p$ and make sure it does not receive any message and hence will not reach agreement. But in a randomized protocol, how can the adversary isolate party $p$? The answer is that it uses its ability to claw back: once it sees any party send a message to $p$, it immediately corrupts that party and claws back that message.

Note that the lower bound on broadcast in synchrony implies a lower bound on agreement in synchrony. In turn, this implies a lower bound on agreement in asynchrony.


### Proof idea

As in Dolev and Reischuk 1982, we will show that some party $p$ gets no message and hence must cause a error with a (large) constant probability. This is done by defining two worlds. In world 1 there are $f/2$ parties with omission failures. In world 2, we choose a uniformly random party $p$ from this set of $f/2$ and un-corrupt it. Instead we add omission failures to the $f/2$ first messages sent to $p$.

Seeking a contradiction, we look at world 1 and use Markov inequity to argue that with a large probability the protocol sends not too much messages. Conditioned on this event, there is still a large probability that the party $p$ gets no more than $f/2$ messages. Conditioned on this event, there is a probability that all parties output the leader value (there is no error).

We then show indistingushability between world 1 and world 2. Then in world 2, conditioned on these three events, party $p$ sees no message, so there is a constant probability that party $p$ has either a safety error or a liveness error. 


### Proof

Consider a broadcast problem, where the *designated sender* has a binary input. 

Observe what happens to a party that receives no messages: it will either not decide 0 with probability at least 1/2 or not decide 1 with probability at least 1/2. Without loss of generality, assume that a majority of parties (other than the designated sender) that receive no message will not decide 1 with probability at least 1/2. Let $Q$ be this set of parties and note that $\|Q\| \geq (n-1)/2$.

As with Dolev and Reischuk 1982, the proof describes two worlds and uses indistinguishability. 

### World 1

In World 1, the adversary corrupts a set $V \subset Q$ of $f/2$ parties that do not include the designated sender. Let $U$ denote the remaining parties (not in $V$). All parties in $V$ run the designated protocol but suffer from omission failures as follows: 

1. Each $v \in V$ omits the first $f/2$ messages sent to $v$ from parties in $U$, 
2. Each $v \in V$ omits all messages it sends to and receives from parties in $V$. 

Note that messages sent from parties in $V$ to parties in $U$ are not omitted.

Set the non-faulty designated sender with input 0. So from the validity property, all non-faulty parties must output 0. 

#### The events $\mathcal{X}_1$,  $\mathcal{X}_2$, and $\mathcal{X}_3$

Let $\mathcal{X}_1$ be the event that the parties in $V$ send at most $f^2/8$ messages to parties in $U$. Since the expected number of messages is at most $f^2/64$, we have that $\Pr[\mathcal{X}_1] \le 1-1/8$. This is because from Markov Inequality:

$$
\Pr[ \text{not } \mathcal{X}_1] = \Pr[\text{more than }f^2/8] = \Pr[\text{more than }8\mu] < 1/8.
$$

Let $p\in U$ be a uniformly randomly chosen party in $U$ and let $\mathcal{X}_2$ be the event that there are at least $f/4$ parties in $U$ that receive more messages from parties in $V$ than $p$ (so $p$ is below the median).

So, $\Pr[\mathcal{X}_2] = 1/2$.

We can bound $\Pr[\mathcal{X}_1 \cap \mathcal{X}_2] \ge 1/2 +1 - 1/8 -1 =3/8$.


If event $\mathcal{X}_1 \cap \mathcal{X}_2$ occurs, then party $p$ receives at most $f/2$ messages from parties in $U$. This is because otherwise, there are $f/4$ parties that receive $f/2$ messages for a total of $f^2/8$, which is a contradiction. 

Let $\mathcal{X}_3$ be the event that all non-faulty parties output 0. From validity in world 1 and the fact that the error is at most 1/8, we have that $\Pr[\mathcal{X}_3] \geq 1 - 1/8$.

So we can bound $\Pr[(\mathcal{X}_1 \cap \mathcal{X}_2) \cap \mathcal{X}_3] \ge 3/8 +1 - 1/8 -1 = 1/4$.

Observe that conditioned on $\mathcal{X}_1 \cap \mathcal{X}_2 \cap \mathcal{X}_3$, in world 1, with probability at least $1/4$:

1. All non-faulty parties output 0.
2. The faulty party $p$ sees no messages.



### World 2

In world 2, the adversary does everything as in World 1, except:

1. It does not corrupt the randomly chosen party $p$, and
2. It corrupts all parties in $U$ that correspond to the first $f/2$ messages sent to $p$. Messages sent by these omission corrupt parties to $p$ are omitted, and claw back is used if needed. Call this set $W$.

Clearly the adversary can do this because it corrupts at most $f/2$ in $V$ and at most $f/2$ in $W$.


#### Worlds are indistinguishable

The only difference between worlds 1 and 2 is that in world 1 it’s party $p$ that blocks the first $f/2$ *incoming* messages from $W$ and in world 2 it’s the parties in $W$ that block these same messages to $p$ as *outgoing* messages.



#### The event $\mathcal{Y}$

Due to world 1 and 2 being  indistinguishable, we have that, conditioned on $\mathcal{X}_1 \cap \mathcal{X}_2 \cap \mathcal{X}_3$, in world 2, with probability at least $1/4$:

1. All non-faulty parties output 0.
2. The non-faulty party $p$ sees no messages.


Now we use the fact that in world 2, $p$ is non-faulty, sees no message, and hence does not output 0 with probability at least 1/2. Moreover, since $p$ sees no message, this probability is independent of the events $\mathcal{X}_1 \cap \mathcal{X}_2 \cap \mathcal{X}_3$. Let $\mathcal{Y}$ be the event that $p$ either does not terminate or outputs 1. 

$$
\Pr[\mathcal{Y} \mid \mathcal{X}_1 \cap \mathcal{X}_2 \cap \mathcal{X}_3 ] >1/2
$$

So in world 2, we have an error of more than 1/8:

$$\Pr[\mathcal{X}_1 \cap \mathcal{X}_2 \cap \mathcal{X}_3 \cap \mathcal{Y}] > 1/8$$

Which is a contradiction.


Please leave comments on [X](https://x.com/ittaia/status/1868794373267448243). 

