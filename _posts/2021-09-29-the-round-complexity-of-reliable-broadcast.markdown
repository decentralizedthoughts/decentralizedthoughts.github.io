---
title: The round complexity of Reliable Broadcast
date: 2021-09-29 06:05:00 -04:00
tags:
- dist101
- research
- lowerbound
author: Ittai Abraham, Zhuolun Xiang, Ling Ren
---

[Reliable Broadcast](https://decentralizedthoughts.github.io/2020-09-19-living-with-asynchrony-brachas-reliable-broadcast/) is an important building block of many [Asynchronous](https://decentralizedthoughts.github.io/2019-06-01-2019-5-31-models/) protocols. There is a broadcaster that has some *input value*, $v$, and a non-faulty party that *terminates* needs to *output* a value. Reliable Broadcast is defined via two properties: 

**Validity**: If the broadcaster is non-faulty then *eventually* all non-faulty parties will output the broadcaster's input.

**Agreement**: If some non-faulty party outputs a value then *eventually* all non-faulty parties will output the same value.

Let's try to better understand and optimize the notion of *"eventually"*. There are many reasons to outright [stop using the term "eventually"](https://twitter.com/heidiann360/status/1315608969470189568?s=20). Can we be more precise? Instead of "eventually", can we provide a concrete measure of the worst case round complexity? 


## What is the round complexity of a synchronous protocol?

In the synchronous model, there is an upper bound $\Delta$ on the message delay between any two non-faulty parties. Let $roundComplexity(e)$ of an execution $e$ be the *total time divided by $\Delta$*. 

Define $roundComplexity(P)$ of a protocol $P$ to be the maximum $roundComplexity(e)$ over all executions and adversary strategies.

## What is the round complexity of an asynchronous protocol?

Let's adopt the synchronous definition above to the asynchronous model. The immediate problem is that we do not have any known bound $\Delta$ on the length of a round. In the asynchronous model, there is no apriori bound on the message delay between any two non-faulty. So the trick is to look at the execution *in hindsight* and define the longest delay after the adversary fixed all the delays. 

Imagine having an external clock that can provide an ideal clock time for each event. Consider a protocol $P$.

1. For a message $m$ that is sent and received between two non-faulty parties, define $messageDelay(m)$ as the time elapsed between the send and receive time points.
2. For an execution $e$, define  $totalTime(e)$ as the elapsed time between the earliest time a non-faulty sends a message and the latest time a non-faulty party terminates. 
3. For an execution $e$, define $roundComplexity(e)$ as $\frac{ totalTime(e) }{ \max_{m \in M} messageDelay(m) }.$
4. For the protocol $P$, define $roundComplexity(P)$ as the maximum $roundComplexity(e)$ over all executions and adversary strategies.  In later posts, we will generalize this definition to randomized protocols and expected round complexity.



There is nothing in the round complexity of an execution that forces it to be an integer. Nevertheless, the round complexity of a protocol is often manifested when an asynchronous protocol is executed in a *lock step* schedule (and hence is an integer). In fact, it's [very surprising](https://decentralizedthoughts.github.io/2021-03-09-good-case-latency-of-byzantine-broadcast-the-synchronous-case/) when it's not an integer.


## Reliable Broadcast and round complexity

Armed with these formal definitions of round complexity in Asynchrony we can finally  
 replace "eventually" with a more precise notion of *round complexity*:

**Validity**: If the broadcaster is non-faulty then, *after at most $R_g$ rounds*, all non-faulty parties will output the broadcaster's input.

**Agreement**: If some non-faulty party outputs a value then, *after at most $R_{ex}$ round*, all non-faulty parties will output the same value.

We call $R_g$ the *good-case latency*, and define $R_b=R_g+R_{ex}$ to be the *bad-case latency*. We say a Reliable Broadcast protocol is $(R_g,R_b)$-round protocol if it has good-case $R_g$ rounds and bad-case $R_b$ rounds.

> *Exercise 1*: Go back to the post on [Reliable Broadcast](https://decentralizedthoughts.github.io/2020-09-19-living-with-asynchrony-brachas-reliable-broadcast/) and verify that indeed it takes three rounds when the broadcaster is non-faulty and at most one more round to reach agreement and terminate. In other words, it is $(3,4)$-round protocol. 
<!-- Roughly speaking, it's because in the first round the broadcaster *sends*, then the parties *echo*, then they *vote*.  -->


Given a concrete measure of round complexity, we ask: is *three* rounds the best we can do?

## Can Reliable Broadcast take just two rounds?

We will show two protocols for Reliable Broadcast that have good-case round complexity of 2. The first works for $n\geq 3f+1$ and uses a Public Key Infrastructure (PKI), and the second works for $n \geq 4f$ (and does not need a PKI).

### 2-round Reliable Broadcast for $n \geq 3f+1$ using a PKI:

This protocol appears in section 3 of our [good-case latency categorization](https://arxiv.org/pdf/2102.07240.pdf) paper.

       // broadcaster s with input v
       send <v>_s to all parties

       // Party j
       on receiving the first proposal <v>_s from broadcaster s:
          send <echo, v>_j to all parties

       on receiving <echo, v>_* signed by n-f distinct parties:
          send the <echo, v>_* signed by n-f distinct parties to all parties
          deliver v and termiante

The main insight: a party that delivers a value has a cryptographic proof that it can transfer to other parties.


> *Exercise 2*: Prove that for $n\geq 3f+1$, Agreement and Validity hold assuming the adversary is computationally bounded (cannot forge signatures), and the protocol is $(2,3)$-round.



### 2-round Reliable Broadcast for $n \geq 4f$ without PKI:

Do we have to assume a PKI to get to 2 rounds? This protocol decides in 2 rounds when the broadcaster is honest and requires $n\geq 4f$. The first trick is to have a *fast path* to decide early, the second trick is to ignore the broadcaster in all rounds but the first.



       // broadcaster with input v
       send <v> to all parties

       // Party j 
       on receiving the first proposal <v> from broadcaster:
          send <echo 0, v> to all parties

       on receiving <echo 0, v>  by n-f-1 distinct non-broadcaster parties:
          deliver v, send <echo 1, v> and <echo 2, v> to all parties and terminate

       on receiving <echo 0, v>  by n-2f distinct non-broadcaster parties:
          send <echo 1, v> (if not sent yet) to all parties
          
       on receiving <echo 1, v>  by n-f-1 distinct non-broadcaster parties:
          send <echo 2, v> (if not sent yet) to all parties

       on receiving <echo 2, v>  by n-f-1 distinct non-broadcaster parties:
          deliver v and terminate

       on receiving <echo 2, v>  by f+1 distinct non-broadcaster parties:
          send <echo 2, v> (if not sent yet) to all parties


<!-- *Validity claim: When the broadcaster is honest, all honest parties decide broadcaster's value in 2 rounds.* -->


**Agreement claim**: If an honest commits $v$, then no honest will see $n-2f$ ```<echo 0, v'>```, or send ```<echo 1, v'>``` or ```<echo 2, v'>``` for any $v' \neq v$. Moreover, eventually all honest will see $n-2f$ ```<echo 0, v>```, so eventually all honest will send ```<echo 1, v>```, so eventually all honest will send ```<echo 2, v>```.

***Proof***: 
1. If the broadcaster is honest - trivial.
2. Otherwise, there are at most $f-1$ faulty non-broadcaster parties.
   
    2A. If even one honest party sees $n-f-1$ ```<echo 0, v>``` then at least $n-f-1-(f-1)=n-2f$ honest send ```<echo 0, v>``` and at most $2f-1$ remaining non-broadcasters can send  ```<echo 0, v'>```. Hence all honest will send ```<echo 1, v>``` and then ```<echo 2, v>``` and then decide $v$.

    2B. Otherwise some honest saw $n-f-1$ ```<echo 2, v>```, so at least $n-f-1-(f-1)=n-2f>f+1$ honest send ```<echo 2, v>```. We will now show that no honest sent ```<echo 2, v'>``` hence all honest will decide $v$: Since some honest sent ```<echo 2, v>``` then at least $n-2f$ honest sent ```<echo 1, v>```, hence there can be at most $2f-1$ non-broadcasters that send ```<echo 1, v'>```.

> *Exercise 3*: Verify that the above protocol satisfies validity and agreement, and has $(2,4)$-round.

### $n\geq 4f$ is optimal for 2-round unauthenticated Reliable Broadcast

The previous 2-round reliable broadcast protocol that assumes no authentication requires $n\geq 4f$. This is worse than the $n\geq 3f+1$ of 2-round reliable broadcast with PKI. Can we do better?

It turns out that $n\geq 4f$ is the best we can do without signatures. We prove this *lower bound* in our [new paper](https://arxiv.org/pdf/2109.12454.pdf): *any unauthenticated reliable broadcast under $n\leq 4f-1$ cannot achieve good-case 2 rounds*.

## How many rounds does Reliable Broadcast need when the broadcaster is bad?

In the *good case* (when the broadcaster is non-faulty), we know that we can do Reliable Broadcast in 2 rounds, either for $n\geq 3f+1$ with PKI, or for $n\geq 4f$ without a PKI. What is the round complexity when the broadcaster is faulty?

If the faulty broadcaster sends no message, Reliable Broadcast allows non-faulty parties to never output. The tricky case is when the faulty broadcaster together with other faulty parties intentionally tries to make some non-faulty party output, but not the others. To satisfy the *agreement* property, the protocol needs to take extra rounds to have all honest parties terminate and output the same value. An interesting question is, how many extra rounds do we need for this *bad case*? The previous 2-round protocol without PKI has bad case 4 rounds, can we do better?

In our [paper](https://arxiv.org/pdf/2109.12454.pdf), we give a *complete categorization* of how many extra rounds are needed for solving 2-round unauthenticated Reliable Broadcast in the bad case. In particular, for $f\geq 3$, it is impossible to achieve the following three conditions simultaneously: (1) output in 2 rounds under non-faulty broadcaster (2) one extra round for all non-faulty parties to output once any non-faulty party outputs (3) have resilience $n\leq 5f-2$ assuming no authentication. 

We then present [four Reliable Broadcast protocols](https://arxiv.org/pdf/2109.12454.pdf), with good-case latency 2 rounds that are optimal with respect to the above impossibility result. For $f=1$, a $(2,2)$-round protocol under $n\geq 4f$; For $f=2$, a $(2,3)$-round protocol under $n\geq 4f$; For $f\geq 3$, we show two protocols, one presented earlier that has $(2,4)$-round and requires $n\geq 4f$, another one that has $(2,3)$-round and requires $n\geq 5f-1$. Below we present the $(2,3)$-round Reliable Broadcast for $n\geq 5f-1$.


<!-- 
### (2,3) Reliable Broadcast for $n=8,f=2$ and (2,4) for $n\ge 4f$


These protocols decide in two rounds when the broadcaster is honest.



       // broadcaster with input v
       send <v> to all parties

       on receiving <v> from broadcaster:
          if first mesage form broadcaster:
             send <echo, v> to all parties

       on receiving <echo, v>  by n-f-1 distinct non-broadcaster parties:
          deliver v and terminate

       on receiving <echo, v>  from j ( and j is not you and not the broadcaster):
          if first mesage form j:
             send <vote, j, v> to all parties
          
       on receiving <vote,j,v> by n-f-1 distinct non-broadcaster and non-j parties:
          resolve j to v

       on resolving n-f-1 non-broadcaster parties to v:
          deliver v and terminate


For the case of $f\ge 3$ and $n\ge 4f-2$ we add two more rules and get (2,4):



       on resolving n-2f+1 non-broadcaster parties to v:
          send <echo 2 ,v> (if not sent yet) to all parties

       on receiving <echo 2, v>  by n-f-1 distinct non-broadcaster parties:
          deliver v and terminate
    

This works because for a bad $j$, if an honest sees $n-f-1$ votes then all honest will see $n-f-1 -(f-2)=n-2f+1$ and when $n \ge 4f-1$ we have that $n-2f+1$ is a strict majority out of $n-1$.

 -->
### $(2,3)$-round Reliable Broadcast without PKI for $n \geq 5f-1$
A similar protocol was shown by  [Imbs and Raynal](https://www.worldscientific.com/doi/abs/10.1142/S0129626416500171?journalCode=ppl) for $n\geq 5f+1$, and we improve the resilience of their protocol by distinguishing the messages from the broadcaster and the non-broadcasters.


       // broadcaster with input v
       send <v> to all parties

       // Party j
       on receiving the first proposal <v> from broadcaster:
          send <echo, v> to all parties

       on receiving <echo, v>  by n-2f distinct non-broadcaster parties:
         if not yet sent echo for v:
             send <echo, v> to all parties

       on receiving <echo, v>  by n-f-1 distinct non-broadcaster parties:
         deliver v and terminate


Validity in two rounds follows since all $n-f$ non-faulty parties will echo the non-faulty broadcaster's value in the end of the second round.

For Agreement, when the broadcaster is faulty, if a non-faulty party decides $v$, there there are at least $n-2f$ non-faulty non-broadcasters that echo $v$. So from quorum intersection, no value $v' \neq v$ can receive $n-2f$ echoes. Hence all non-faulty will hear $n-2f$ echo $v$ and after at most one more round will send echo $v$. By the end of this round, all non-faulty parties will hear $n-f$ echoes and terminate.


For more results, check out our [good-case and bad-case latency paper](https://arxiv.org/pdf/2109.12454.pdf).


Your comments and decentralized thoughts on [Twitter](https://twitter.com/ittaia/status/1443160799665610758?s=20).  

