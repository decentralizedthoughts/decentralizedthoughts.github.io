---
title: 'Early Stopping, Same but Different: Two Rounds Are Needed Even in Failure Free Executions'
date: 2024-01-28 12:05:00 -05:00
tags:
- lowerbound
author: Ittai Abraham and Gilad Stern
---

**TL;DR:** Even in *failure-free* executions, consensus protocols resilient to crash failures often require at least two rounds. This follows from the early stopping lower bound: executions with $f$ actual crashes require at least $\min \{f+2, t+1\}$ rounds when tolerating $t$ possible failures. Thus, the possibility of a failure forces extra rounds, even when no failures occur.

Many systems aim to optimize executions that are *failure-free*. If we knew with certainty that there would be no failures, parties could simply exchange their inputs and reach consensus by outputting, for example, the majority value. The protocol would then complete in just one round. What happens if there may be a crash failure? Say you have 100 servers and at most one can crash, can you devise a consensus protocol that stops in just one round *in executions where there are no failures*? 

> The answer is **No**: one round is not always enough. Sometimes you need 2 rounds even in *failure-free* executions.

The *threat* of a potential failure forces the protocol to run longer, even if no failure actually occurs.

This result follows from the fundamental lower bound on **early stopping**: the number of rounds for consensus protocols in the synchronous model that can tolerate at most $t$ crash failures in executions where there at most $f \le t$ failures is at least $\min \{f+2,t+1\}$.

Just to repeat this subtle point, we [already know](https://decentralizedthoughts.github.io/2019-12-15-consensus-model-for-FLP/) that if we want to design a protocol to be resilient to $t$ faults, in the worst case we might need $t+1$ rounds. However, even in executions of this protocol with a few actual failures $f<t$, we need at least $f+2$ rounds.

This post is based on the beautiful 2001 tutorial by Idit Keidar and Sergio Rajsbaum: [On the Cost of Fault-Tolerant Consensus When There are No Faults - A Tutorial](https://iditkeidar.com/wp-content/uploads/files/ftp/consensus-bounds.pdf). 

We start with two definitions, mention 3 models, then the $f=0$ case, followed by the general case.

## Definitions 


***Definition 1:*** *Two configurations are **Almost Same (AS)** if the state of all parties except for a single party $i$ are the same.*

***Definition 2:*** *Two Almost Same (AS) configurations are **Failure Free Different (FFD)** if the failure free continuation of one configuration leads to a different decision value than the failure free continuation of the other configuration.*

In other words, two configurations are *AS but FFD* if the state of all parties except for one are the same, and continuing one without faults leads to a different decision value than doing so with the other.

## Models

There are slightly different lower bounds for 3 different adversary models and problems:


***Early Stopping for Consensus under Crashes with Fixed First ($ES{-}C{-}Cfix$)*** : Early stopping for consensus in protocols where the first message sent in the round a party is crashed is fixed. Note this models includes omission failures and also deterministic protocols that always follow the same sending order.

***Early Deciding for Uniform Consensus under Crashes with Fixed First ($ED{-}UC{-}Cfix$)*** : Early deciding for [uniform consensus](https://decentralizedthoughts.github.io/2019-06-27-defining-consensus/) in the same fault model above where the first message sent in the round a party is crashed is fixed.

***Early Stopping for Consensus under Crashes ($ES{-}C{-}C$)*** : The standard crash model where parties can decide the order of messages sent in each round (potentially as a function of its state).

## The $f=0$ case

***Theorem for $f=0$***: *Let there be a protocol in the synchronous model for $n$ parties that is resilient to $n-2 \geq t \geq 1$ failures. Then in failure-free executions:*

1. $ES{-}C{-}Cfix$ : *the protocol must have an execution with at least 2 rounds.*
2. $ED{-}UC{-}Cfix$ : *for $t>1$, the protocol must have an execution where a decision is made after at least 2 rounds.*
3. $ES{-}C{-}C$ : *for $t>1$, the protocol must have an execution with at least 2 rounds.*


The theorem follows from Lemma 1 and Lemma 2.

***Lemma 1***: *Any consensus protocol that is resilient to at least 1 crash failure must have two initial configurations that are Almost Same but Failure Free Different (AS but FFD).*

*Proof*: For any $0 \leq i \le n$ consider the initial configuration $C_i$ where parties 1 to $i$ have input 1 (empty set for $i=0$) and the rest have input 0. Let $val(i)$ be the decision in the failure free execution that starts with configuration $C_i$. By validity, $val(0)=0$ and $val(n)=1$. The (trivial) [one dimensional Sperner's Lemma](https://en.wikipedia.org/wiki/Sperner%27s_lemma#One-dimensional_case) then implies that there exists $1 \le i \le n$ and two configurations $C_{i-1},C_{i}$ such that:

* $val(i-1) = 0$ while $val(i) = 1$
* The only difference between configurations $C_{i-1}$ and $C_i$ is the state of party $i$.

Hence, $C_{i-1},C_{i}$ are two AS but FFD configurations. 

This might not sound like much, but the next lemma shows that if there are two AS but FFD configurations, it is not possible to terminate (or decide) in one round starting in either one of them. Intuitively, seeking a contradiction, any party hearing all parties must decide and stop in one round in both configurations. But the configurations are so similar with just one party that has a different state. This causes problems because this party may crash after sending its message to just one party, who then decides and stops, but others don't know what value to choose.


***Lemma 2***: *If $C,C'$ are two AS but FFD configurations at the beginning of a round, and in both configurations the adversary has at least $c \in\{1,2\}$ more crash failures (so has previously crashed at most $t-c$ parties) then:*

1. $ES{-}C{-}Cfix$ : *any protocol must have an execution with at least 2 more rounds.*
2. $ED{-}UC{-}Cfix$ : *for $c=2$, must have an execution where a decision is done after at least  2 more rounds.*
3. $ES{-}C{-}C$ : *for $c=2$, must have an execution with at least 2 more rounds.*


*Proof*: For contradiction, assume a binary consensus protocol where all parties stop in one more round in any failure free execution (or for case 2 above, all parties decide in one more round in failure free executions).

Let party $i$ be the difference between $C$ and $C'$. We will start by proving this lemma with the simplifying assumption that $i$ sends its messages in the same order starting in either configuration $C$ or $C'$ (model $ES{-}C{-}Cfix$).

World $A$: from configuration $C$, party $i$ sends to one party $j$ and then crashes. For party $j$, this looks exactly like the configuration where party $i$, and all other parties are non-faulty in this round, hence by our assumptions party $j$ must decide and stop at the end of the round.

World $A'$: from configuration $C'$, party $i$ sends to the same party $j$ as above and then crashes. For party $j$, this looks exactly like the configuration where party $i$, and all other parties are non-faulty in this round, hence by our assumptions party $j$ must decide and stop at the end of the round.

The executions in worlds $A$ and $A'$ look like continuations of configuration $C$ and $C'$ without failures, so $j$ must terminate by the end of the round. Since we chose $C$ and $C'$ to be FFDs, this means that $j$ must output different values in these executions. However, for all other parties, what they see is that $i$ (that crashed) and $j$ (that stopped) stop responding but cannot distinguish between worlds $A$ and $A'$, and thus must disagree with $j$ in at least one of these worlds.

This completes the proof when parties have a fixed sending order because in both worlds $A$ and $A'$ it is party $j$ that stops. In model $ES{-}C{-}Cfix$ we can force this to be the case by simply choosing some specific party $j$ to be the first to receive messages from $i$.

For model $ED{-}UC{-}Cfix$, uniform consensus, the adversary also crashes party $j$ and this proves that party $j$ cannot decide early. This requires $c = 2$ because the adversary crashes both $i$ and $j$.

For model $ES{-}C{-}C$, for crash failures where parties can control the order of messages, party $i$ may send its first message to party $j_1$ in world $A$ and send its first message to another party $j_2$ in world $A'$. This will prevent our previous attack from working because $j$ stops responding in both worlds, so other parties cannot tell the difference.

In order to fix this, in world $A$, $j_1$ terminates after receiving $i$'s message and the adversary crashes $j_2$. This means that neither $j_1$ nor $j_2$ continue participating in the next round. Similarly, in world $A'$, the adversary crashes $j_1$ and $j_2$ terminates so both $j_1,j_2$ stop responding. Hence, the remaining parties cannot distinguish between worlds $A$ and $A'$. Note that $c = 2$ because the adversary crashes both $i$ and one of the $j$'s in each world.

## The general case

***Theorem***: *Any protocol in the synchronous model for $n$ parties that is resilient to $n-2 \geq t \geq 1$ failures, then in executions with $f$ failures:*

1. $ES{-}C{-}Cfix$ : *for $f\le t-1$ any protocol must have an execution with at least $f+2$ rounds.*
2. $ED{-}UC{-}Cfix$ : *for $f \le t-2$, must have an execution where a decision is done after at least $f+2$ rounds.*
3. $ES{-}C{-}C$ : *for $f \le t-2$, must have an execution with at least $f+2$ rounds.*

Looking at the proof for $f=0$, it has two steps:

1. Show that there are configurations in the beginning of round $1$ that are AS but FFD.
2. Show that we need at least two more rounds when starting from such a pair of configurations (if we have enough of a corruption budget).

Following this logic, we now only need to show that for the values of $f \le t-1$ or $\le t-2$, it is possible to find two AS and FFD configurations in the beginning of round $f+1$ by only using $f$ faults. We will do so by showing in ***Lemma 3*** that each time we start with such a pair of configurations in round $k$, we can find another pair in round $k+1$ using only one more fault. We then just do that for $f$ rounds. More precisely:

*Proof of Theorem for $0<f$*: Start with Lemma 1, then apply Lemma 3 $f$ times, to reach two AS but FFD configurations in the beginning round $f+1$. From Lemma 2, parties cannot complete (terminate or decide) the protocol in this round and thus must do so in round $f+2$ or greater.

***Lemma 3***: *If $C,C'$ are two AS but FFD configurations at the beginning of round $k$, then there are two configurations $D, D'$ that are AS but FFD that each extend $C,C'$ by one round in which the adversary crashed at most one party in round $k$.*

*Proof of Lemma 3*: Let party $i$ be the only difference between $C$ and $C'$ and wlog assume that if party $i$ crashes in the beginning of the round then the failure free execution has a *different* value than the failure free extension of $C$ (otherwise use $C'$).

Now consider the $n+1$ configurations $C_0,C_1,\dots,C_n=C$ where $C_j$ is the configuration in which the adversary crashes party $i$ after it sends to $j$ parties. Clearly any two consecutive configurations are AS because they differ in one party $j$ that either received or did not receive $i$'s message.

Note that $C_0$ is the execution in which $i$ crashes in the beginning of the round. This means that from our above assumption we know that if we continue from $C_0$ without faults the decision value is going to be different from the decision value in a failure-free extension of configuration $C$. Using the (trivial) [one dimension Sperner's Lemma](https://en.wikipedia.org/wiki/Sperner%27s_lemma#One-dimensional_case), we know that there must exist two consecutive configurations that are AS but FFD.

This completes the proof of Lemma 3.

## Notes

* Comparing the technique of [uncommitted configurations](https://decentralizedthoughts.github.io/2019-12-15-consensus-model-for-FLP/) (bi-valency) to the technique of a pair of AS FFD configurations: The latter is strictly stronger:
    1. If $C,C'$ are two AS but FFD configurations then both are uncommitted (bi-valent).
    2. Moreover, their uncommitted-ness is structured: for each configuration, one side is from a failure free execution. 

* Lemma 3 can be applied $t$ times (after Lemma 1) to prove that protocols resilient to $t$ crashes cannot always terminate after $t$ rounds. This is an alternative proof for the $t+1$ round lower bound to the [proof that uses uncommitted configurations](https://decentralizedthoughts.github.io/2019-12-15-synchrony-uncommitted-lower-bound/).

* To apply Lemma 3 in the crash model, we looked at the failure free decision if $i$ crashes. In the **mobile adversary model**, we look at the failure free decision if $i$ crashes for one round (and then heals) in both $C$ and $C'$. If its not the same value, then Lemma 3 holds by applying this crash to both $C$ and $C'$. Otherwise, the failure free decision if $i$ crashes for one round is fixed (wlog to the value opposite of $C$) so Lemma 3 holds by looking at the hybrid worlds where $i$ crashes for just one round after sending to $j$ parties (and then heals). This argument implies that [infinite executions must exist](https://link.springer.com/chapter/10.1007/BFb0028994) with even just **one** mobile crash. Hence, deterministic solutions are impossible and randomization is needed in the mobile adversary model. 

* Note that the bound $\min \\{ f+2,t+1 \\}$ does not hold for $ES{-}C{-}C$ or $ED{-}UC{-}Cfix$, in those models the bound is:

$$
\begin{align}
 & 
  \begin{cases}
    f+2\hphantom{-\sqrt{-}} & \text{if } f \le t-2,\\
    f+1 & \text{otherwise}
  \end{cases}
 \end{align}
$$

* *Exercise*: devise a protocol that stops early in one round for $t=1$ and the crash model $ES{-}C{-}C$ where parties can choose the order they send messages in each round. That is, show that if there are no faults and parties can choose to send messages in different orders depending on their state, they can complete the protocol after one round in all failure free executions. Note that your protocol has to deal with the case that some party terminated early because it did not see faults, but others might continue running because they did.




Please leave comments on [Twitter](https://x.com/ittaia/status/1751743296219529283?s=20).
