---
title: "$3f+1$ is needed in Partial Synchrony even against a Rollback adversary"
date: 2023-06-26 07:00:00 -04:00
tags:
- lowerbound
- dist101
author: Ittai Abraham
---

In this post we show that trusted execution environments (TEEs) don't help against the classic $3f$ lower bound for partial synchrony, when these TEEs have no persistent storage, against a rollback adversary.

We covered the classic [DLS88 split brain](https://decentralizedthoughts.github.io/2019-06-25-on-the-impossibility-of-byzantine-agreement-for-n-equals-3f-in-partial-synchrony/) impossibility result against a Byzantine adversary in a previous post:

**[DLS88](https://groups.csail.mit.edu/tds/papers/Lynch/jacm88.pdf):** (Theorem 4.4) It is impossible to solve [Agreement](https://ittaiab.github.io/2019-06-27-defining-consensus/) under partial synchrony against a ***Byzantine adversary*** if $f \geq n/3$.

In a follow-up post, we discussed how [CJKR12](https://decentralizedthoughts.github.io/2021-06-14-neither-non-equivocation-nor-transferability-alone-is-enough-for-tolerating-minority-corruptions-in-asynchrony/) strengthen this result by observing that it holds even if the adversary is weaker in that it must faithfully transfer messages. 
In this post we strengthen this result yet again by observing that it holds even against a much weaker **rollback adversary** suggested by [Matetic, Kostiainen, Dhar, Sommer, Gervais, Juels, Capkun 2017](https://www.usenix.org/system/files/conference/usenixsecurity17/sec17-matetic.pdf):

**DLS88:** (modern version) It is impossible to solve Agreement under partial synchrony against a ***rollback adversary*** if $f \geq n/3$.

The rollback adversary is a model that captures the power of the adversary given a  trusted execution environment (TEE) that does not have any local trusted state or persistent storage.

### The Rollback Adversary

Recall that an *omission adversary* can block any message sent to or from a corrupted party, but it must run the correct protocol, from its correct beginning state, in an honest manner even on a corrupted party. In contrast, a *Byzantine adversary* can run any protocol on a corrupted party. 
A **Rollback adversary** has slightly more power than an omission adversary:

1. The adversary can block any message sent to or from a corrupted party.
2. All parties start from a correct initial state and run the honest protocol 
3. On any corrupted party, the adversary can choose to:
   * Either make one more step forward in executing the honest protocol;
   * Or rollback the execution to its correct initial state

The Rollback adversary models an adversary that cannot corrupt the execution, but since the execution is stateless, it can rollback the execution to an earlier state and feed it different interactions and inputs. See [Matetic et al 2017](https://www.usenix.org/system/files/conference/usenixsecurity17/sec17-matetic.pdf) for more discussion on this adversary. This model captures the (limited) power of an adversary that can control everything inside a node except for a secure enclave (trusted execution environment) under the assumption that the secure enclave (or TEE) does not have any access to trusted storage (like a trusted monotonic counter). 


### The proof

Observe that to execute the lower bound of [DLS88](https://decentralizedthoughts.github.io/2019-06-25-on-the-impossibility-of-byzantine-agreement-for-n-equals-3f-in-partial-synchrony/), all the adversary needs to do is to run two "split brains". This can be done if the adversary is allowed to run two instances in parallel, or as in the case of the rollback adversary, run one instance and then rollback to run the other.

For the $n=3, f=1$ case, assume the adversary is $B$ and the honest parties are $A,C$ and as usual, communication between $A$ and $C$ will be delayed. Here is the relevant part of the proof in [our blog post on DLS](https://decentralizedthoughts.github.io/2019-06-25-on-the-impossibility-of-byzantine-agreement-for-n-equals-3f-in-partial-synchrony/):

> The adversary will use its Byzantine power to corrupt $B$ to perform a **split-brain** attack and make $A$ and $C$ each believe that they are in their respective worlds. $B$ will equivocate and act as if its starting value is 1 when communicating with $A$ and as if its 0 when communicating with $C$. If the adversary delays messages between $A$ and $C$ for longer than the time it takes for $A$ and $C$ to decide in their respective worlds, then by an indistinguishability argument, $A$ will commit to 1 and $C$ will commit to 0 (recall the time to decide cannot depend on GST or $\Delta$). This violates the agreement property.

A rollback adversary that has two inputs can do the following:

1. Start $B$ in its initial correct state; 
2. Give $B$ input 1, and communicate only with $A$, using its power of omission failures to block messages to $C$;
3. Wait for $B$ to terminate, and then rollback $B$ to its initial correct state;
4. Give $B$ input 1, and communicate only with $C$, using its power of omission failures to block messages to $A$;

We also need to assume the adversary has access to two different inputs, in this case "0" and "1" (and that the input is not part of its "sealed" correct beginning state). In the state machine replication setting, this implies having more than one client or having one client that has more than one choice of input value.

This concludes the observation that the main "split brain" world can be conducted by a rollback adversary. The remainder of the proof follows exactly as in [our blog post about the DLS88 lower bound](https://decentralizedthoughts.github.io/2019-06-25-on-the-impossibility-of-byzantine-agreement-for-n-equals-3f-in-partial-synchrony/) showing that agreement is impossible in partial synchrony.

### Extension to Broadcast and write once objects

As in [this post](https://decentralizedthoughts.github.io/2021-06-14-neither-non-equivocation-nor-transferability-alone-is-enough-for-tolerating-minority-corruptions-in-asynchrony/), the lower bound also holds for [Reliable Broadcast](https://decentralizedthoughts.github.io/2020-09-19-living-with-asynchrony-brachas-reliable-broadcast/), in fact, it even holds for [Provable Broadcast](https://decentralizedthoughts.github.io/2022-09-10-provable-broadcast/). In the state machine replication setting, this implies that the lower bound holds if the client can be malicious and may have (at least) two different values to output, or if there are two different clients and clients can have omission failures. In particular, it holds for [write once objects](https://decentralizedthoughts.github.io/2022-12-27-set-replication/) in this setting.

### ROTE: Rollback Protection for Trusted Execution requires $3f+1$ to be safe and live

[Matetic et al 2017](https://www.usenix.org/system/files/conference/usenixsecurity17/sec17-matetic.pdf) suggest a system called **ROTE** that provides rollback protection. ROTE uses $n=f+2u+1$ severs to overcome $f$ malicious servers and to provide liveness when there are $u$ unresponsive servers. With $f$ malicious servers that can also be unresponsive, Rote would need $u=f$ and hence $n=3f+1$ servers to obtain safety and liveness (not circumventing the lower bound). Setting $u$ < $f$ would imply that ROTE is not live if $f$ servers are unresponsive and hence any protocol relying on it would not obtain liveness so would not solve agreement (again not circumventing the lower bound).


### A snapshot rollback adversary

The rollback adversary needed for this lower bound could only rollback to the initial correct state. In reality a slightly more powerful adversary may be able to create snapshots and rollback a corrected party to any previous snapshot (not just the initial state). This can be a useful attack in a multi-shot (SMR or ledger) setting.


### Rollback or Crash with no FIFO

Instead of assuming adversary can rollback and omit. Assume a model where the adversary can rollback or crash and assume channels have no FIFO. We use asynchrony to delay the messages as if they are omissions.

Note that in practical settings, if servers try to establish say a TLS connection, then the attack can happen assuming rollback or crash, because TLS handshake blocks for an ack.


## So how can you get $2f+1$ using a TEE?

There are two ingredients:

1.  The first is to make sure each TEE chooses a new unique private key each time it reboots, and it uses its corresponding public key as its unique identifier. This means that a TEE that reboots is essentially a new TEE that needs to join the system. The security of this technique depends on the assumption that the memory of the TEE is indeed rollback protected.
2.  The second is to use a *consensus oracle* or a *setup assumption of a consensus* on the unique identities (public keys) of the TEEs. Note that these identities are fragile, as they are reboot dependent and the security of the system depends on the security of the setup assumption or the consensus oracle.
  
As eluded above, in order to deal with reboots, you need to reconfigure the system to add a new TEE. This can be done if there are $n-f$ TEES that have not rebooted (and hence the system is live), but this means that the system will halt if $>f$ TEE reboot at the same time. The alternative is to use an external "consensus oracle" (similar to the one used during setup) and then of course the security of the system depends on the security of that oracle.


### Acknowledgments

Many thanks to Andrew Miller and Guy Gueta for insightful discussions.

Your comments on [Twitter](https://twitter.com/ittaia/status/1673476144996261889?s=20).
