---
title: On Paxos from Recoverable Broadcast
date: 2022-11-04 05:00:00 -04:00
tags:
- dist101
- omission
author: Ittai Abraham
---

There are many ways to learn about the [Paxos](https://lamport.azurewebsites.net/pubs/lamport-paxos.pdf) protocol (see [Lampson](https://www.microsoft.com/en-us/research/publication/the-abcds-of-paxos/), [Cachin](https://cachin.com/cc/papers/pax.pdf), [Howard](https://www.youtube.com/watch?v=0K6kt39wyH0), [Howard 2](https://www.youtube.com/watch?v=s8JqcZtvnsM), [Guerraoui](https://www.youtube.com/watch?v=WX4gjowx45E), [Kladov](https://matklad.github.io/2020/11/01/notes-on-paxos.html), [Krzyzanowski](https://people.cs.rutgers.edu/~pxk/417/notes/paxos.html), [Lamport](https://www.youtube.com/watch?v=tw3gsBms-f8), [Wikipedia](https://en.wikipedia.org/wiki/Paxos_(computer_science)) and many more). The emphasis of this post is on a **decomposition** of Paxos for *omission failures* that will later help when we do a similar decomposition for *Byzantine failures* (for [PBFT](https://decentralizedthoughts.github.io/2022-11-20-pbft-via-locked-braodcast/) and [HotStuff](https://decentralizedthoughts.github.io/2022-11-24-two-round-HS/)).

The model is [partial synchrony](https://decentralizedthoughts.github.io/2019-06-01-2019-5-31-models/) with $f<n/2$ [omission failures](https://decentralizedthoughts.github.io/2019-06-07-modeling-the-adversary/) and the goal is [consensus](https://decentralizedthoughts.github.io/2019-06-27-defining-consensus/) (see below for exact details). 

> The Paxon parliament’s protocol provides a new way of implementing the state-machine approach to the design of distributed systems. [Lamport, The Part-Time Parliament](https://lamport.azurewebsites.net/pubs/lamport-paxos.pdf).

We introduce Paxos with two simplifications:

1. Use a *simple revolving primary* strategy based on the assumptions of perfectly synchronized clocks. A later post shows how to extend to a *stable leader* strategy, how to rotate leaders with *responsiveness*, and how not to rely on clock synchronization.
2. Focus on a *single-shot* consensus. A [later post](https://decentralizedthoughts.github.io/2022-11-19-from-single-shot-to-smr/) shows how to extend to *multi-shot* consensus and *state machine replication*.

In essence, our goal is to focus first on *safety* and move as much of the *liveness* and *multi-shot* complications to a later post. 

## View-based protocol with simple revolving primary

The protocol progresses in **views**, each view has a designated **primary** party. The role of the primary is rotated. For simplicity, the primary of view $v$ is party $v \bmod n$. 

In Partial Synchrony, the parameter $\Delta$ (the maximum message delay after GST) is known. So we define **view $v$** is set to be the time interval $[v(10 \Delta),(v+1)(10 \Delta))$ (see liveness proof for how this can be optimized). In other words, each $10\Delta$ clock ticks each party triggers a **view change** and increments the view by one. Here we assume clocks are perfectly synchronized, so all parties move in and out of each view in complete synchrony (lock step). We will discuss relaxations in future posts.

## Single-shot consensus

In this setting, each party has some *input value* and the goal is to *output a single value* with the following three properties:

**Uniform Agreement**: if any two parties output $X$ and $X'$ then $X=X'$. Note that this is a strictly stronger property than **Agreement** which just requires that all *non-faulty* parties that output a value, output the same value.

**Termination**: all non-faulty parties eventually output a value and terminate. This is a strictly stronger property than **Liveness** which just requires that all non-faulty parties eventually output a value. Note that we are in partial synchrony, and our protocol is deterministic, obtaining this property will require reasoning about events after GST.

**Validity**: the output is an input of one of the parties. Note that this is a strictly stronger property than **Weak Validity** which just requires that if *all* parties have the same input value then this is the output value.

## What is the core safety problem of view-based consensus protocols?

The core safety problem that all view-based consensus protocols need to solve is the risk of an agreement violation when one primary causes some parties to commit $X$, but some later primary misses this event and causes other parties to commit to $Y \neq X$.

With synchrony and crash failures, this is easy, the primary sends its decision to all the next primaries. But with asynchrony and omission corruptions, how can a primary write a message in a way that later primaries will be guaranteed to read it?

The solution that all Paxos based protocols use a **Quorum System**: The primary guarantees that it writes to a write-quorum (typically of size $n-f$) and then each new primary first reads from a read-quorum (again, typically of size $n-f$). This guarantees that the new primary read-quorum will intersect with any previous write-quorum and be able to *recover* these previous values.

The second challenge then emerges: a new primary that reads from a read-quorum may see many messages from many previous primaries. Which one should it use? It turns our that it is critical that each primary also includes its view number and then the new primary can *adopt the value associated to the highest view it saw*. This choice is essential for the safety of all Paxos protocols (see proof below).

Here we will do this by decomposing Paxos to a *recoverable-broadcast* protocol that write to a quorum and a *recover max protocol* that reads from a quorum and chooses the value associated with the highest view:

1. The primary runs a **recoverable-broadcast** protocol that guarantees that if some party commits to the primary's value $X$ in view $v$, then there is *sufficient* evidence to *recover* the pair $(v,X)$ in a later view. Sufficient evidence here is write-quorum set $W$ of size $n-f$ that holds $(v,X)$.
2. The primary of any view (except the first) tries to recover a previously committed value via a **recover protocol** that guarantees that if some previous primary caused some party to commit, then the recover protocol will return this value. The primary will then **adopt** this recovered value, instead of using its own input value, as the value it tries to broadcast for committing. The recover protocol does this by reading from a read-quorum $R$ of size $n-f$ that will hence intersect any previous write-quorum. 
3. The primary may recover different pairs $(v_1, X_1),\dots,(v_k, X_k)$. So it runs a uses a **recover max protocol** that returns the pair $(v^\star, X^\star)$ that has the highest view ($\forall i, v^\star \geq v_i$). By adopting the value associated with the highest view we can guarantee that the new primary will adopt a value that was committed by a previous primary.

In this post we *decompose* Paxos into an outer *view-based protocol* and two inner protocols:  *recoverable broadcast*  and *recover max*.

## The Paxos Outer Shell Protocol

This outer shell protocol is rather simple. The main thing to note is that if the ```recover-max(v)``` protocol returns a non-$\bot$ value then the primary must adopt it.

```
For view 1, the primary of view 1 with input X: 
recoverable-broadcast(1, X)
```

```
For view v > 1, the primary of view v with input X:

Y := recover-max(v)

if Y = bot then 
    // use your own input
    recoverable-broadcast(v, X)
else 
    // adopt the value from recover-max
    recoverable-broadcast(v, Y)
```

We'll next define ```recoverable-broadcast``` and ```recover-max```.

## Recoverable-broadcast and recover-max for $f<n/2$ Omission Corruptions

### Recoverable-broadcast protocol


The ```recoverable-broadcast``` protocol has a designated *primary* party with *input value* ```Z``` and a view number ```v```. 

```
Upon start of view v,
 Primary sends <v, Z> to all

Upon receiving n-f <"echo", v, Z>, 
 output Z
```

All parties run the following while in view ```v```:
```
Upon receiving <v, Z> from primary, 
 send <"echo", v, Z> to all
```

Observe that for simplicity, the primary also acts as a regular party. So it also sends ```<v, Z>``` to itself and upon seeing its own message, it sends an ```<"echo", v, Z>``` message to all parties (again including sending it to itself). 

### Recoverable-broadcast properties

**Validity**: If a party echos or outputs a value in Broadcast then it's the input value of the primary of that view.

**Weak Termination**: If the primary of view ```v``` is non-faulty and all non-faulty are in view ```v``` then all non-faulty parties output a value and terminate.

**Recoverability**: If some party outputs ```Z``` in view ```v``` then at least $n-f$ parties sent ```<"echo", v, Z>```. Note this is the write-quorum.

#### Proof of recoverable-broadcast properties

**Validity**:

1. For a party to output a value, it needs to receive $n-f$ ```<"echo", v, Z>``` messages.
2. An ```<"echo", v, Z>``` message is only generated upon receiving a ```<v, Z>``` from the primary.
3. The primary of view ```v``` with input ```Z``` sends its input value ```<v, Z>```.

**Weak Termination**:

1. Since the primary is non-faulty, it sends the ```<v, Z>``` message to all parties, including itself.
2. Upon receiving ```<v, Z>``` from the primary, each non-faulty party sends ```<"echo", v,  Z>``` to all.
3. Since there are at most $f$ omission failures, there are at least $n-f$ non-faulty parties.
4. Each non-faulty party will therefore receive at least $n-f$ ```<"echo", v,  Z>``` messages and output the value ```Z```.

**Recoverability**:

1. For a party to output a value ```Z```, it must receive $n-f$ ```<"echo", v,  Z>``` messages.
2. If a party receives $n-f$ such messages, it implies that at least $n-f$ parties have sent the ```<"echo", v,  Z>``` message.
3. Note we did not say that all these $n-f$ are non-faulty. This weaker property is sufficient for recover-max as we show below.

### Recover-max protocol

 The ```recover-max``` protocol has a view number ```u``` as input and outputs either a broadcast value or a special $\bot$ value (which we write as ```bot``` in pseudo-code). Each replica sends ```<"recover", u, w, Z>``` associated with the *highest* view echo ```<"echo", w, Z>``` it ever sent. The primary waits for $n-f$ ``` <"recover", u, *, *>```  messages and outputs $\bot$ if all recover messages are $\bot$, and otherwise outputs the value associated with the *highest* view it saw:

```
Upon start of view u,
 if you never sent any <"echo", *, *>,
    then send <"recover", u, bot> to the primary
 otherwise,
    let <"echo", w, Z> be the maximal w
    send <"recover", u, w, Z> to the primary
Upon primary receiving n-f <"recover", u, *>,
    if all are <"recover", u, bot>
      then output bot
    otherwise
      let <"recover", u, y, Z> be with the maximal y
      output Z 
```

### Recover-max properties:

**Validity**: If a party outputs a value in recover-max then it is either some primary's input value or $\bot$.

**Termination**: If all parties start recover-max for view $u$, and the primary is non-faulty then it will output a value.

**Recover-max after recoverable-broadcast**: If $n-f$ parties send echo in view $v$ for recoverable-broadcast then for recover-max of view $u>v$, the output is a value from view $y$ with $v\le y$.


### Proof of recover-max properties:

**Validity**: 

1. The primary outputs a value in `recover-max` upon receiving $n-f$ ```<"recover", u, *, *>``` messages.
2. Any `<"recover", u, w, Z>` follows an `<"echo", w, Z>`. By the recoverable-broadcast validity property this is the view $w$ primary's input value.
3. Otherwise, if all received messages are `<"recover", u, bot>`, the primary outputs $\bot$.

**Termination**:

1. Every party sends a `<"recover", u, *, *>` message, be it `<"recover", u, w, Z>` or `<"recover", u, bot>`.
2. A non-faulty primary will definitely receive $n-f$ `<"recover", u, *, *>` messages since at most $f$ parties can omit messages.
3. Upon receiving $n-f$ such messages, the non-faulty primary will make an output, be it $Z$ or $\bot$.

**Recover-max after recoverable-broadcast**:

1. *From recoverability of recoverable-broadcast*: At least $n-f$ parties sent `"<echo", v, Z>`. Let's denote the set of these parties as $ W $ (for the write-quorum).

2. *Progression of Echoes*: At view $u$, parties in $ W $ send echoes from views that are at least $ v $ (and possibly from higher views if they've encountered them).

3. *Quorum intersection*: The primary of view $u$ waits for $n-f$ `recover` messages. Let's denote the set of these sending parties as $R$ (for the read-quorum). Given $ f < n/2 $ and the fact that both $ W $ and $ R $ have at least $ n-f $ parties, the intersection of $ W $ and $ R $ is non-empty. This is because $W \cap R$ contains at least $ 2(n-f) - n = n - 2f \geq 1 $ parties.

4. *Primary chooses the highest*: Because of the non-empty intersection between $ W $ and $ R $ the primary receives recover messages that indicate echoes from a view of at least $ v $. Note that the view may be higher since (1) the party in the intersection may have a higher view echo, or the set $W$ contains some higher higher view echo. The primary then chooses the value associated with the highest view number.



## The Paxos outer shell protocol (repeated from above for readability)

**The main Paxos algorithmic insight is that for guaranteeing agreement the primary must:**
> **Choose the recovered value associated with the most recent view you hear!**

```
For view 1, the primary of view 1 with input X: 
recoverable-broadcast(1, X)
```

```
For view v > 1, the primary of view v with input X:

Y := recover-max(v)

if Y = bot then 
    // use your own input
    recoverable-broadcast(v, X)
else 
    // adopt the value from recover-max
    recoverable-broadcast(v, Y)
```

Finally, define that a party *decides* and outputs a value the first time a recoverable-broadcast subroutine outputs a value. 


### Agreement (Safety)

The agreement property follows from the safety lemma:

**Safety lemma**: Let $v^{\star}$ be the first view with $n-f$ echoes of $(v^\star, W)$, then for any view $v \ge v^\star$ the proposal value of ```recoverable-broadcast(v, W)``` must be $W$.

Before we prove the lemma, let's see why it implies uniform agreement.

*Proof of uniform agreement property given the safety lemma*: consider any party that outputs a value $X'$ in view $v'$.  It cannot be that $v' < v^\star$ because outputting a value requires seeing at least $n-f$ echo messages $(v',X')$, but by definition $v^{\star}$ is the first such view. So it must be that $v' \geq v^\star$ and hence $X'=W$ because the only values that are sent in recoverable-broadcast for these views is with the value $W$.

We now prove the lemma, which is the essence of Paxos safety.

*Proof of the safety lemma*:

For the base case when $v=v^\star$ lemma is true by the validity of ```recoverable-broadcast(v, W)```.

By induction, assume the lemma is true for all views $v$ such that $v^\star \le v<u$. To prove the lemma for view $u$, use the **recover-max after recoverable-broadcast** property: the output in view $u$ is a value from view $y$ with $v^\star \le y$. 

1. From the induction hypothesis, in all views $v^\star \le v<u$ the proposal value of ```recoverable-broadcast(v, W)``` is $W$;
2. During recover-max for view $u$ there are no recoverable-broadcast for view $u$ or higher views, so there are no echoes for view $u$ or higher. 
Hence, the value of recover-max in view $u$ must be $W \neq \bot$, so the value of recoverable-broadcast in view $u$ must be $W$ as well. This concludes the induction argument with concludes the proof of the safety Lemma.

### Liveness

We proved (uniform) agreement, now let's prove that eventually, after GST, all *non-faulty* parties output a value.

Consider the view $v^+$ with the *first* non-faulty primary that starts after GST. Denote this start time as $T$. Since we are after GST, then on or before time $T+ \Delta$ the primary will receive ```<"recover", v+, *)>``` from all non-faulty parties (at least $n-f$). Hence, the primary will start a ```recoverable-broadcast(v+,Z)>``` that will arrive at all non-faulty parties on or before time $T+2\Delta$. Hence, all non-faulty parties will send ```<"echo", v+, Z>``` (because they are still in view $v^+$). So all non-faulty parties will hear $n-f$ ```<"echo", v+, Z>``` on or before time $T+3\Delta$. So all non-faulty will decide $Z$ because they are still in view $v^+$.

This concludes the liveness proof. 

Note that all we needed here is that all non-faulty parties are in the same view for $3\Delta$ time. So we could have defined view $v$ to just be the time interval $[v(3 \Delta),(v+1)(3 \Delta))$.


### Termination

We proved that all non-faulty parties output a value, but our protocol never terminates! For that, we add the following *termination gadget*:

```
If the consensus protocol outputs Z,
 then send <decide, Z> to all

Upon receiving <decide, Z>
 If you did not output yet,
 Then output Z and send <decide, Z> to all

Upon receiving n-f <decide, Z>
 Terminate

``` 

*Proof*:

The tricky party of the proof is to only use the liveness property when we are sure all non-faulty parties are still running the protocol. 

Claim: It cannot be the case that there is an execution where no honest party receives a `<decide, Z>` message. Proof of claim: in that case all honest parties will continue to run the protocol and by the liveness property, consider the time the first non-faulty outputs a value - it will send a decide message to all.

The remaining part of the proof is natural:

So consider the first non-faulty party that receives a  `<decide, Z>` message or outputs a value. In both cases it will send a `<decide, Z>` message to all parties. So eventually all non-faulty parties will receive a `<decide, Z>` message. So all non-faulty will eventually send a `<decide, Z>` message to all parties. So all non-faulty will see at least $n-f$ `<decide, Z>` messages and terminate.

Note that here we used the safety property: all parties that decide will indeed decide the same value.

Note that this argument just used the liveness and safety properties, so this gadget is generic and can be used with any consensus protocol.

### Validity

Observe that validity is rather trivial in these protocols. By induction, the only values used are the inputs of the parties.

What if a party has several different values (for example it received several different values from several different clients)? This is an example of how the standard validity of consensus does not address the challenges of MEV. More on that in later posts. 

### Message Complexity

Note that the time and number of messages before GST can be both unbounded. So for this post, we will measure the time and message complexity after GST.

**Time complexity**: since the Liveness proof waits for the first non-faulty primary that starts after GST this may take in the worst case: almost one "interrupted" view, then $f$ views of faulty primaries, then a view of a non-faulty party. So all parties will output a value in at most $(f+2)10 \Delta$ time after GST. A more careful analysis can improve the first and the last durations. We show [here](https://decentralizedthoughts.github.io/2019-12-15-synchrony-uncommitted-lower-bound/) that $(f+1) \Delta$ is a worst case that cannot be avoided (but can have a small probability when using randomization).

**Message Complexity**: since each round has an all-to-all message exchange, the total number of messages sent after GST is $O((f+1) \times n^2) = O(n^3)$. We show [here](https://decentralizedthoughts.github.io/2019-08-16-byzantine-agreement-needs-quadratic-messages/) that $O(n^2)$ is the best you can hope for (for deterministic protocols or against strongly adaptive adversaries).

*Exercise: Modify the protocol above to use just $O(n)$ messages per view (so total of $O(n^2)$ after GST). Explain why the proof still works, in particular, detail the Liveness proof and the Time complexity.*

## Canonical examples

The following 3 examples are helpful to understand Paxos.

All these examples will have $n=3$ and $f=1$. Assume party 1 has input ```A``` and party 2 has ```B```.

1. **Only party 1 outputs in view 1**. In view 1: party 1 sends ```A```, parties 1 and 2 echo and party 1 outputs ```A```. In view 2: party 2 receives recover from parties 1 and 2, hence will see the echo from view 1, hence will use that echo as its value  ```recoverable-broadcast(2, A)```.
2. **No one outputs in view 1** In view 1: party 1 sends ```A```, party 1 sends echo. View 2 is *exactly* like in the above example. Party 2 receives recover from parties 1 and 2, hence uses ```B```, but in fact its just because it cannot distinguish between this and the previous example.
3. **View 1 like example 2 and View 2 only party 2 outputs**. In view 1: party 1 sends ```A```, party 1 sends echo. In view 2:  party 2 receives recover from parties 2 and 3, hence will see $\bot$ so it will use it input for ```recoverable-broadcast(2, B)```. Parties 2 and 3 echo, party 2 outputs ```B```. Now at view 3: party 3 receives  ecover from parties 1 and 3: it hears ```A``` from 1 and ```B``` from 3, so what will it choose? Since ```A``` is associated with view 1 and ```B``` is associated with view 2, so ```B``` must be chosen.

## Acknowledgments

Many thanks to Kartik Nayak and Gilad Stern for insightful comments.

Your comments on [Twitter](https://twitter.com/ittaia/status/1599150005432250368?s=20&t=JiegXa5IVUUcfNM6ZietBA).