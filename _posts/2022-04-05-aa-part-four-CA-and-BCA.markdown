---
title: 'Asynchronous Agreement Part 4: Crusader Agreement and Binding Crusader Agreement'
date: 2022-04-05 06:11:00 -04:00
tags:
- asynchrony
- consensus
- research
author: 'Ittai Abraham, Naama Ben-David, Sravya Yandamuri '
---

In this post we introduce a key building block in the *Byzantine* Model called **Binding Crusader Agreement**. We show how to use it in the [next post](https://decentralizedthoughts.github.io/2022-04-05-aa-part-five-ABBA/). This is a simplified version extracted from our [paper](https://eprint.iacr.org/2022/711.pdf).


In the three previous posts we (1) [defined the problem](https://decentralizedthoughts.github.io/2022-03-30-asynchronous-agreement-part-one-defining-the-problem/) and discussed the [FLP theorem](https://decentralizedthoughts.github.io/2019-12-15-asynchrony-uncommitted-lower-bound/); (2) presented [Ben-Or's protocol](https://decentralizedthoughts.github.io/2022-03-30-asynchronous-agreement-part-two-ben-ors-protocol/) for crash failures; and (3)  [a modern version](https://decentralizedthoughts.github.io/2022-03-30-asynchronous-agreement-part-three-a-modern-version-of-ben-ors-protocol/) for crash failures.



## Crusader Agreement (CA) 
We begin by recalling a useful agreement primitive called Crusader Agreement, first introduced by [Dolev 1981](https://www.cs.huji.ac.il/~dolev/pubs/byz-strike-again.pdf) which we adopt to the asynchronous model following the *BV-broadcast* protocol of [Mostefaoui, Hamouma, Raynal 2015](https://hal.archives-ouvertes.fr/hal-01176110/document).

Crusader agreement is similar to other agreement problems in that each party receives an input, and must eventually decide on an output. However, in crusader agreement, instead of requiring all non-faulty parties to decide the same value, the agreement property is weakened; non-faulty parties are allowed to decide a special value $\bot$ despite some others deciding a non-$\bot$ value.

* **Weak Agreement**: If two non-faulty parties output values $x$ and $y$, then either $x=y$ or one of the values is $\bot$.
* **Validity**: If all non-faulty parties have the same input, then this is the only possible output. Furthermore, if a non-faulty party outputs $x \neq \bot$, then $x$ was the input of some non-faulty party.
* **Liveness**: If all non-faulty parties start the protocol then all non-faulty parties eventually output a value.


Here is a simple pseudocode for crusader agreement with $n$ parties that tolerates a malicious adversary that controls $f<n/3$ parties:

```
CA for party i

input: v (0 or 1)

send <echo1, v> to all
if didnt send <echo1, 1-v> and see f+1 <echo1, 1-v>
    send <echo1, 1-v> to all
if didnt send <echo2, *> and see n-f <echo1, w>
    send <echo2, w>
if see n-f <echo2, u> and n-f <echo1, u>
    output(u)
if see n-f <echo1, 0> and n-f <echo1, 1>
    output(bot)
```

Proof of properties.

*Weak Agreement*: this follows from quorum intersection on echo2 messages. Since $n>3f$ and each non-faulty party sends only one echo2 message, it cannot be that $n-f$ parties send `<echo2,1>` and $n-f$ parties send `<echo2,0>` because that would imply that at least $n-2f \geq f+1$ parties sent conflicting echo2 messages, but we assume there are only $f$ malicious parties.

*Validity*: if all non-faulty parties start with $x$ then no non-faulty will send `<echo1, 1-x>` because there can be at most $f$ malicious parties that send `<echo1, 1-x>`. In addition, all non-faulty parties will send `<echo1, x>`, hence all non-faulty parties will see at least $n-f$ `<echo1, x>` messages and send `<echo2, x>` within one communication round, hence all non-faulty parties will `output x` in one more round.

Proving *Liveness* is done in 3 steps:

**Claim 1**: All non-faulty parties will eventualy send an echo2 message.
*Proof*: Let $x$ be an input value that at least $f+1$ non-faulty parties have. Since there are only two possible input values and at least $2f+1$ non-faulty parties, such a value exists. So all non-faulty parties will send `<echo1, x>` after at most one communication round, hence a round later they will all send `<echo2, x>` if they have not sent `<echo2, 1-x>` earlier.

**Claim 2**: If non-faulty parties send both `<echo2, 0>` and `<echo2, 1>` then all non-faulty parties output a value.
*Proof*: For a non-faulty party to send `<echo2, u>`, it must have seen at least $n-f$ `<echo1, u>` messages. Therefore, at least $n-2f\geq f+1$ non-faulty parties sent `<echo1, u>`. In the case specified by the claim, this is true for both $0$ and $1$. Since non-faulty parties send additional echo1 messages for any value they've seen at least $f+1$ times, all non-faulty parties will eventually send both `<echo1, 0>` and `<echo1, 1>`. Hence all non-faulty parties that do not output $v \neq \bot$ will eventually output $\bot$. 



**Claim 3**: If all non-faulty parties send `<echo2, u>` for the same value $u$, then all non-faulty parties output a value.
*Proof*: Clearly, in this case eventaully all of them will see at least $n-f$ `<echo2, u>` and hence output $u$ if they did not output $\bot$ earlier.

### Adding a Termination Gadget 

Note that as described, Crusader Agreement (and the similar [BV-broadcast](https://hal.archives-ouvertes.fr/hal-01176110/document)) does not terminate; for Claim 2 to be correct, a party that outputs $x \neq \bot$ needs to continue running the protocol at least until it has sent both `<echo1, 0>` and `<echo1, 1>`.



Hence even after outputting value $x \neq \bot$, a party is required to keep maintaining state and running the protocol in order to help others output a value. Let's strengthen CA and obtain:  

* **Termination:** If all non-faulty start the protocol then all non-faulty parties eventually Terminate.

Without the Termination property, sequentially running $k$ instances requires maintaining $O(k \times n)$ local memory. With Termination, only the latest instance needs to be maintained, so local memory is bounded by just $O(n)$. 


Here is the psedocode for termination:

```
if output(bot)
    send <output bot> to all
    Terminate
if output(v)
    send <output v> to all
if see f+1 <output v> and did not output yet
    output(v)
if see n-f <output v>
    Terminate
if see <output bot> and you output(v) and you sent <echo1,1> and <echo1,0>
    Terminate
```

There are two claims about CA + Termination Gadget:

**Claim 4**: The liveness property holds.
*Proof*: As mentioned, Claim 2 requires all non-faulty parties to send echo1 for both values. So the only non-trivial case is when parties terminate after seeing $n-f$ `<output v>` messages. But in this case all non-faulty parties will see at least $n-2f \geq f+1$ `<output v>` and hence all non-faulty will output a value.


**Claim 5**: If all non-faulty parties output a value then eventually all non-faulty parties terminate.
*Proof*: Note that trivially, parties that output $\bot$ terminate. Furthermore, if all non-faulty parties output $v$ then this is immediate. The non-trivial case is when some but not all non-faulty parties output $\bot$; we must show that parties that output $v \neq \bot$ also terminate in this case. Note that for a non-faulty party to output $\bot$, it must have seen at least $n-f$ echo1s for both values. As argued when showing liveness, this means that eventually all non-faulty parties will see $n-f$ echo1 for both values, hence the termination condition for $v$ will hold. 



### Pipelining the Termination Gadget

As we will show in the [next post](https://decentralizedthoughts.github.io/2022-04-05-aa-part-five-ABBA/), often multiple Crusader Agreement instances are executed in a sequence $CA_1,CA_2, \dots$.

In this case we can send the `<output x>` message of instance $CA_j$ along with the first message of instance $CA_{j+1}$, saving a communication round. The `<output x>` message of instance $j$ can be used as a signal to garbage collect the previous instance. 





## Binding Crusader Agreement (BCA)


A more subtle property that Crusader Agreement (and BV-broadcast) lacks is a way to prevent the adversary from being able to pick the output value of a non-faulty party *after* seeing the output of other non-faulty parties. In particular, we would like to prevent the adversary from conducting the following attack when CA is used inside a randomized agreement algorithm: let the first non-faulty party (or first $f+1$ non-faulty parties) output $\bot$, then learn the coin value, then force the remaining non-faulty parties to output the value opposite of the coin.

We call this additional property **binding**, since the adversary is bound to a specific output value from each crusader agreement instance.

* **Binding:** At the time at which the first non-faulty party outputs a value, there is a value $b$ such that no non-faulty party outputs the value $1−b$ in any extension of this execution.


Here is a pseudocode for BCA with just three message types:

```
BCA for party i

input: v (0 or 1)

//echo1
send <echo1, v> to all
if didnt send <echo1, 1-v> and see f+1 <echo1, 1-v>
    send <echo1, 1-v> to all

//echo2
if didnt send <echo2, *> and see n-f <echo1, w>
    send <echo2, w> to all
if didnt send <echo2, bot> and see
    n-f <echo1, 0> and n-f <echo1, 1>
        send <echo2, bot> and <echo3, bot> to all

//echo3
if didnt send <echo3, *> and see n-f <echo2, u> and n-f <echo1, u>
    send <echo3, u> to all


//output condition
wait for n-f <echo3, *> 
    if see n-f with u, then output(u)
    otherwise, if you sent <echo2, bot>, then output(bot)
```

Proof of properties:

Note that this algorithm is very similar to the one for CA, but adds an echo3 message. Intuitively, this is where we get binding. An `<echo3, u>` message is sent in the same case in which we would output $u$ in the CA algorithm (for $u$ being any value, including $\bot$). If the BCA algorithm outputs $\bot$ then it would have output $\bot$ in the CA algorithm. The BCA algorithm outputs $u \neq \bot$ if it sees enough non-faulty parties that would have output $u$ in the CA algorithm. Therefore, the Weak Agreement and Validity properties of BCA follow from the same argument as in CA.

For Liveness, again by the argument for CA, we know that all non-faulty parties send an echo3 message. If all of them send `<echo3, u>` for a non-$\bot$ value $u$, then clearly we have liveness. Otherwise, note that if a non-faulty sent `<echo3, bot>` then eventually all non-faulty will send echo1 for both 0 and 1, so eventually they will all send `<echo2, bot>` and output $\bot$ if they didn't output before. 

The new addition is binding:

*Binding*: Consider the first non-faulty party that sees $n-f$ echo3 messages. There are two cases; if some non-faulty party sent a non-$\bot$ echo3 message then we have binding from the Weak Agreement property (recall that we have Weak Agreement on echo3 messages from the CA algorithm). Otherwise there are at least $f+1$ non-faulty parties that sent `<echo3, bot>`. This means that no other non-faulty party can see $n-f$ echo3 messages with a non-$\bot$ value, so $\bot$ is the only possible output, hence we have (trivially) binding for both 0 and 1.



### Termination and Pipelining 

Just as with CA, we add the same Termination Gadget mechanism for BCA and the same proof holds.

Similarly, if multiple BCA instances are executed serially, then the `<output>` message can be pipelined in the same way.

## Message complexity of CA and BCA
Observe that in CA each non-faulty party sends at most 3 messages (and just 2 if all non-faulty parties have the same input). In BCA each non-faulty party sends at most 4 messages (and just 3 if all non-faulty parties have the same input). Finally, the termination gadget adds one more message, but this message can be pipelined if instances of CA or BCA are run sequentially.

So the total message complexity is $O(n^2)$, with low constants.

In the next post we show how to use BCA for [Asynchronous Byzantine Agreement](https://decentralizedthoughts.github.io/2022-04-05-aa-part-five-ABBA/).


Your thoughts and comments on [Twitter](https://twitter.com/ittaia/status/1511665005699248136?s=20&t=gJEZwTvUN72KwbNBJ53eYQ). 
