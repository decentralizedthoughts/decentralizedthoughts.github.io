---
title: In between Crash and Omission failures
date: 2024-01-30 12:05:00 -05:00
tags:
- lowerbound
- models
author: Ittai Abraham
---

In this post we explore adversary failure models that lie between crash and omission failures:

1. **Send Omissions (SO)**: the adversary can corrupt a party and block any message that the party attempts to send. The corrupted party is not aware that it is corrupted or that the message it wanted to send was blocked. 
2. **Receive Omissions (RO)**: the adversary can corrupt a party and decide to block any message that the party receives. The corrupted party is not aware that it is corrupted or that the message it was supposed to receive was blocked.
3. **Send or Receive Omissions (SRO)**: the adversary can corrupt a party with either send omissions or receive omissions, but not both.

Can you guess in which models state machine replication is possible for any $f<n$ and for which ones we cannot do better than $f<n/2$? The answer is that in models where failures are **detectable**, one can tolerate $f<n$.

## Primary Backup for Send Omissions for $n=2$ and $f=1$

The solution is similar to the primary backup solution for [crash failures](https://decentralizedthoughts.github.io/2019-11-01-primary-backup/) with the following two changes:

To deal with send omissions from the primary to the client, the backup also sends the response to the client.

To deal with send omissions from the primary to the backup: The primary sends a heartbeat every $\Lambda$ time. If the backup does not hear a heartbeat in $\Delta+\Lambda$ period it sends a message to the primary (and everyone) saying that the primary is faulty. The primary then halts, and the backup becomes the new primary. The client may need to re-transmit its request to the new primary. Note that the primary’s failure can be unequivocally detected.

## Primary Backup for Receive Omissions for $n=2$ and $f=1$

The solution is again similar to the primary backup solution for [crash failures](https://decentralizedthoughts.github.io/2019-11-01-primary-backup/) with the following two changes:

To deal with receive omissions between the client and the primary: the client sends to both the primary and the backup and the backup forwards the request to the primary. The primary executes commands only once via unique identifiers.

To deal with receive omissions of the primary from the backup: The backup sends a heartbeat every $\Lambda$ time units. If the primary does not hear a heartbeat within a $\Delta+\Lambda$ period it broadcasts a message stating that it has crashed. The primary then halts itself and the backup becomes the new primary. The client may need to re-transmit its request to the new primary. Note that the primary’s failure can be unequivocally detected.

## Primary Backup for Send or Receive Omissions is impossible $n=2$ and $f=1$

Recall that here the adversary can corrupt at most one server with either send or receive omissions (but not both) and can also corrupt any number of clients (again with either send or receive omissions).

In the figures below, arrowless lines represent bidirectional communication, while lines with an arrow represent communication **only** in the direction of the arrow (other direction is blocked).

The main idea of the lower bound is that when communication from Server 2 to Server 1 fails we cannot detect if the problem is Server 1 having receive omissions or Server 2 having send omissions. We use the fact that clients can also have omissions to make sure that clients also cannot detect the problem.


### World A: Server 1 has Receive Omission failures

Server 1 cannot receive any messages. Nevertheless, Client 2 and Server 2 must complete the request locally. Note that Server 1 learns nothing of this request.

<p align="center">
  <img src="/uploads/SRO1.jpg" width="512" title="World A">
</p>


### World B: Server 2 has Send Omission failures

Server 2 cannot send any messages. Nevertheless, Client 1 and Server 1 must complete the request. Note that Server 2 may learn of this request but cannot convey any outgoing information.

<p align="center">
  <img src="/uploads/SRO2.jpg" width="512" title="World B">
</p>

### The hybrid world: Server 2 has Send Omission failures and Client 1 has Receive Omission failures

Here we start with Client 2 and Server 2 executing a run that is indistinguishable from World A. Once this completes we let Client 1 and Server 1 execute a run that is indistinguishable from World B.

Note that Server 2 may detect a problem with the second request, but it cannot convey any outgoing information to Client 1 or Server 1.

<p align="center">
  <img src="/uploads/SRO3.jpg" width="512" title="Hybrid World">
</p>


Client 2 and Server 2 observe command 2 and must log it because in World A they would have done so. They then possibly see command 1 as well.
Client 1 and Server 1 on the other hand only see command 1 and log it because they would have done so in World B.

This creates a safety violation.

## Notes

This lower bound is strictly stronger than the one for [omission failures in synchrony](https://decentralizedthoughts.github.io/2019-11-02-primary-backup-for-2-servers-and-omission-failures-is-impossible/).

The upper bounds can extend to $f<n$ and the lower bound to any $f \geq n/2$.

## Acknowledgments

Many thanks to Alon Hovav for noting the lower bound and to Gilad Stern and Kartik Nayak for helpful comments.

Please leave comments on [Twitter](https://x.com/ittaia/status/1752630191006814254?s=20)
