---
title: "Agreement under omission failures: non-uniformity and weak validity"
date: 2025-08-12 00:05:00 -04:00
tags:
- omission
author: Ittai Abraham and Gilad Stern
---


In this post, we study non-uniform agreement and weak validity under [synchronous networks](https://decentralizedthoughts.github.io/2019-06-01-2019-5-31-models/) with general omission failures, where faulty parties may lose both incoming and outgoing messages.

In this model, agreement concerns only non-faulty parties. Omission-faulty parties may disagree, and validity is weak: the output must equal some party’s input. We present a protocol for $f < n$ omission faults that runs in $\min\{f+1,n-1\}$ rounds. We then show that both non-uniformity and weak validity are necessary for $f < n$.



## Broadcast for $f<n$

> Think of it as: PBFT is to Paxos as Dolev–Strong is to this protocol.


Let's start with a broadcast protocol that is essentially the non-Byzantine version of the classic [Dolev Strong protocol for Byzantine broadcast](https://decentralizedthoughts.github.io/2019-12-22-dolev-strong/). 

```
Broadcast for f<n:

let k=min{f+1,n-1}
Round 1: leader sends its value to everyone
Rounds 2...k: if you hear a value for the first time, send it to everyone
End of round k: if you heard a value at any time then output it, 
                otherwise output ⊥
```


**Liveness (all non-faulty output):**
All non-faulty parties output in round $k$ by construction of the protocol.


**Validity (non-faulty leader then output is its input, otherwise may be $\bot$)**: 
The first part follows from the first round and the second from an easy induction showing that nobody sends a message other than the leader's input.

**Non-uniform Agreement (all non-faulty output same value)**:
It is useful to reason in terms of message chains: if some party sends a value in round $r$, then some party must have sent that value in round $r-1$, which in turn must have come from a send in round $r-2$, and so on—tracing back to the leader’s initial message in round $1$. Each link in the chain is a distinct sender, since parties send a value at most once.

*Case 1.* No non-faulty party receives a value during the entire protocol. Then all output ⊥.  

*Case 2.* Some non-faulty party receives a value before the final round. It forwards the value, ensuring that by the next round, all non-faulty parties receive it and output the same value.  

*Case 3.* A non-faulty party first receives a value in the final round $k$. This message is the end of a chain of length $k$:  
– If $k = f+1$, the chain must include at least one non-faulty sender. By Case 2, all non-faulty parties will have received the value by the end.  
– If $k = n-1$, the chain must include all other parties. This implies all others are faulty, so agreement among the single non-faulty party is trivial.

Thus, in all cases, all non-faulty parties output the same value, completing the proof.

## Agreement for $f<n$

The protocol is simply to let all parties broadcast and then take (say) the maximum value:

```
Agreement for f<n:

let k=min{f+1,n-1}
Round 1: each party broadcasts its value (using above)
End of round k: output the maximum non-⊥ value from any broadcast
```

**Weak Validity (output is the input of some party):**
Since at least one party is non-faulty, the validity of broadcast ensures that every party receives at least one input value, and that all received values are actual inputs of parties. Each party then outputs one of these values.

**Liveness (all non-faulty output):**
By construction, all non-faulty parties produce an output in round $k$.

**Non-uniform Agreement (all non-faulty output the same value):**
All non-faulty parties agree on the complete set of broadcast values and compute the same maximum among them. Note: this maximum may originate from a faulty party.



## What about stronger validity or uniform agreement

In uniform agreement we want all parties that decide (even if faulty) to output the same value. This is useful because a party may not know its faulty or when a party needs to convince an (external) client.

In strong validity we want the decision to be $x$ if all non-faulty have the value $x$. This is useful when we want the inputs of the non-faulty. For example, if the input is some external event that non-faulty parties observe.




### Strong validity requires $f<n/2$

*Strong validity* means: if all *non‑faulty* parties have the same input $v$, then every non‑faulty party must output $v$. (By contrast, weak validity only requires the output to equal some party’s input, possibly faulty.)

**Lemma**: Any protocol that guarantees strong validity (together with non‑uniform agreement and liveness) against $f$ faults must have $f<n/2$.

*Proof*: Assume toward contradiction that $f\ge n/2$. Consider an input assignment with exactly $n/2$ parties holding $0$ and $n/2$ holding $1$.

Construct two executions in a fully synchronous, reliable network, for all parties:

* World $E_0$: The $0$‑holders are designated non‑faulty and the $1$‑holders are designated faulty. Faulty parties behave honestly according to the protocol on input $1$.
* World $E_1$: Roles swap. The $1$‑holders are non‑faulty; the $0$‑holders are faulty and (again) behave honestly on input $0$.

Because in both worlds every party follows the protocol (faulty parties happen to act in a non-faulty manner), every party sees exactly the same sequence of messages with the same senders. Hence each party’s local view—and thus its output under the protocol—is identical in $E_0$ and $E_1$.

However, strong validity demands different outputs: in $E_0$, all non‑faulty parties (the $0$‑holders) must output $0$; in $E_1$, all non‑faulty parties (the $1$‑holders) must output $1$. This contradicts the indistinguishability of the two executions. Therefore $f<n/2$.

### Uniform agreement requires $f<n/2$


We can see this from the simple case $n = 2$ and $f = 1$.

* World A: Both parties input is 0 and party $B$ crashes before sending any messages. By validity, $A$ must decide $0$.
* World B: Both parties input is 1 and party $A$ crashes before sending any messages. By the same reasoning, $B$ must decide $1$.
* World C: Party $A$’s input is $0$, party $B$’s input is $1$, and all messages between them are omitted.

From $A$’s perspective, worlds A and C are indistinguishable: $B$ never sends any messages in either, so $A$ must decide $0$ in world C.
From $B$’s perspective, worlds B and C are indistinguishable, so $B$ must decide $1$ in world C.

This violates uniform agreement, since in world C the two non-faulty parties output different values.

Thus, uniform agreement is impossible when $f \ge n/2$.

See a similar statement for [state machine replication](https://decentralizedthoughts.github.io/2019-11-02-primary-backup-for-2-servers-and-omission-failures-is-impossible/) (and also see a [strengthening](https://decentralizedthoughts.github.io/2024-01-30-between-crash-and-omission/)).




## What about Byzantine failures

Note that weak validity in omission is similar to [external validity](https://decentralizedthoughts.github.io/2022-12-12-what-about-validity/) in the Byzantine setting.

Note that uniform agreement in omission is similar to provable agreement in the Byzantine setting. Provable agreement allows clients and other offline parties to verify the agreement outcome.

Indeed, the broadcast protocol in omission is similar to the [Dolev Strong broadcast](https://decentralizedthoughts.github.io/2019-12-22-dolev-strong/) in the Byzantine setting that has external validity but is not provable.



## Acknowledgments

Please leave comments on [X]()
