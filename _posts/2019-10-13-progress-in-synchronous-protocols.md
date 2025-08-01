---
title: Progress in Synchronous BFT Protocols
date: 2019-10-13 22:58:00 -04:00
published: false
tags:
- research
- synchronous protocols
author: Kartik Nayak
---

Different modeling assumptions under which we construct BFT protocols often make it hard to compare two protocols and understand their relative contributions. In this post, we explain the assumptions made in *synchronous* protocols and present a timeline of contributions of the ones that use digital signatures. 

A protocol is assumed to be running in the [synchronous model](https://decentralizedthoughts.github.io/2019-06-01-2019-5-31-models/) assumes that:
- **Bounded message delay.** All messages will arrive within a bounded delay of $\Delta$.

A common strengthening of synchronous model is called that *lock-step* model:
- **Lock-step execution.** Replicas execute the protocol in rounds in a synchronized manner. A message sent at the start of a round arrives by the end of the round.

**Lock-step execution vs. bounded message delay.** Some papers refer to their protocol latency in terms of \#rounds, whereas some others in terms of $\Delta$. It turns out that one can obtain lock-step execution from a bounded message delay assumption, by merely using a *clock synchronization* protocol. Due to works by [Dolev et al.](http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.499.2250&rep=rep1&type=pdf) and [Abraham et al.](https://eprint.iacr.org/2018/1028.pdf), we have solutions with $O(n^2)$ message complexity to achieve such synchronization. Specifically, they show that a $2\Delta$ time suffices to implement a lock-step round. Thus, conceptually, the two assumptions boil down to just assuming a bounded message delay.

**Are the above assumptions reasonable?** For practitioners, the synchrony assumption may seem strong. First, if the bounded message delay assumption does not hold *even* for a single message, then we may have a safety violation. Second, lock-step execution may be hard to implement in practice. Finally, waiting for multiple rounds/$\Delta$’s implies a high latency to commit. Research in the synchronous setting has been improving all of these aspects to bring synchrony closer to practice.

**Why should we tackle all of these problems and improve synchronous protocols?** Because the lower bound by [DLS](https://decentralizedthoughts.github.io/2019-06-25-on-the-impossibility-of-byzantine-agreement-for-n-equals-3f-in-partial-synchrony/) says that we cannot tolerate a minority corruption by making weaker assumptions such as partial synchrony/asynchrony. (Due to the [FLM](https://decentralizedthoughts.github.io/2019-08-02-byzantine-agreement-is-impossible-for-$n-slash-leq-3-f$-is-the-adversary-can-easily-simulate/) lower bound, digital signatures/PoW is also necessary to disallow an adversary from simulating multiple parties and tolerate a minority corruption.)

*A note on the bounded message delay.* Bounded message delay $\Delta$ refers to a pessimistic bound for the time it takes a message to arrive. In practice, the actual message delay in the network denoted $\delta$, can be much smaller.

**Timeline of synchronous consensus protocols.** 
- \[1982\] [Lamport, Shostak, and Pease](https://people.eecs.berkeley.edu/~luca/cs174/byzantine.pdf) introduced the first synchronous protocol in the Byzantine setting. Their protocol, however, required an exponential message complexity. 
- \[1982\] [Dolev and Strong](https://www.researchgate.net/publication/220616485_Authenticated_Algorithms_for_Byzantine_Agreement) provide a simple and elegant [Byzantine Broadcast](https://decentralizedthoughts.github.io/2019-06-27-defining-consensus/) construction with polynomial message complexity. Their protocol required every replica to only send up to two messages to every other replica (but each message could be a chain of size $O(f)$ signatures). However, the protocol executed for $O(n)$ synchronous rounds to tolerate $f < n-1$ Byzantine faults. For a large $n$, the latency is not desirable.
- \[1982\] Separately, it was also shown by [Lamport and Fischer](https://lamport.azurewebsites.net/pubs/trans.pdf) that an $O(f)$ round latency is necessary for any deterministic synchronous protocol. Thus, Dolev-Strong was optimal in terms of commit latency for deterministic protocols. 
- \[2006\] [Katz and Koo](https://eprint.iacr.org/2006/065.pdf) showed the first expected $O(1)$ round protocol with $O(n^2)$ communication assuming $n>2f$. Their protocol required 29 rounds in expectation against an adaptive adversary. 
- \[2016\] The [XFT protocol](https://www.usenix.org/system/files/conference/osdi16/osdi16-liu.pdf) also assume a PKI and $n>2f$ and suggest a different approach to architect the system; in the steady-state, the protocol only relied on messages from a fixed, predetermined set of $f+1$ of replicas. If these replicas are all honest,  they could run the protocol without waiting for any network delay $\Delta$. However, if there are failures, they need to view-change to a new fixed all-honest majority of replicas. It turns out that if the number of faults $f$ is high (e.g., linear in $n$), as is tolerated by most consensus protocols, one will require an *exponential* number of view-changes to arrive at all-honest majority replicas. Thus, XFT provides an interesting design point where the steady-state is fast (independent of $\Delta$), but convergence to the steady state can be extremely slow.
- \[2017\] [Abraham et al.](https://eprint.iacr.org/2018/1028.pdf) showed a different version of the Katz-Koo protocol that terminates in 10 rounds against a static adversary and 16 rounds against an adaptive adversary. Using threshold signatures they obtain the first $O(n^2)$ message complexity protocol in this setting. Their work also introduced the clock synchronization protocol for translating rounds to $\Delta$’s while still maintaining $O(n^2)$ message complexity.
- \[2018\] [Dfinity Consensus](https://eprint.iacr.org/2018/1153.pdf) showed a protocol that takes expected $8\Delta$ time to achieve consensus (assuming $\delta << \Delta$). Similar to XFT, some steps of their protocol did not rely on $\Delta$, and the replicas could run at the "network speed." Importantly, all replicas participated in all views and did not require an exponential number of view-changes. 
- \[2019\] Recently, [Sync HotStuff](https://eprint.iacr.org/2019/270.pdf) presented a simple solution in the SMR setting with a $2\Delta$ latency under a stable leader. This will be discussed more in a later post.

**Remark.** All protocols derived from Nakamoto consensus rely on synchrony. We will discuss them separately in a later post.
