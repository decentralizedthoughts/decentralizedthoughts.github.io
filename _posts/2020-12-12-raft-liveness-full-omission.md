---
title: Raft does not Guarantee Liveness in the face of Network Faults
date: 2020-12-12 09:01:00 -05:00
tags:
- omission
- consensus
author: Heidi Howard, Ittai Abraham
---

Last month, [Cloudflare published a postmortem](https://blog.cloudflare.com/a-byzantine-failure-in-the-real-world/) of a recent 6-hour outage caused by a partial switch failure which left [etcd](https://etcd.io) unavailable as it was unable to establish a stable leader. This outage has understandably led to [discussion online](https://twitter.com/heidiann360/status/1332711011451867139) about exactly what liveness guarantees are provided by the [Raft](https://raft.github.io) consensus algorithm in the face of network failures.

The [original Raft paper](https://raft.github.io/raft.pdf) makes the following claim:
> [Consensus algorithms] are fully functional (available) as long as any majority of the servers are operational and can communicate with each other and with clients.

This statement implies that consensus algorithms such as Raft should tolerate network failures (also known as [omission faults](https://decentralizedthoughts.github.io/2019-06-07-modeling-the-adversary/)) as long as they do not impact communication between the majority of servers.
In this post, we will consider whether Raft can guarantee liveness, and specifically whether it can establish a stable leader, if a network fault means that some servers are no longer connected to each other.

## Does Raft guarantee liveness in the presence of network failures?

Unfortunately, Raft, as described in the original paper, does not guarantee liveness in all such cases. Consider the following example.


We have 5 servers and servers 1, 2, and 3 are connected to each other. Server 4 is only connected to server 2 and server 5 is only connected to server 3. Initially, server 3 is the leader. Server 4 is not connected to the leader so it will timeout, increment its term and send a RequestVote RPC to server 2. Server 2 will update its term and then force server 3 to do the same and thus step down. Eventually, a new leader will be elected (either server 1, 2, or 3) but either server 4 or server 5 (or both) will not be connected to the leader and thus will timeout, updating its term and forcing the leader to step down. This system will not be able to establish a stable leader.

<figure class="image">
  <img src="/uploads/RAFT 1.jpg" width="80%">
  <figcaption><center>Partially connected servers 4 and 5 constantly interrupt the elected leader.</center></figcaption>
</figure>





In order to guarantee liveness, Raft must ensure that if a leader is up and connected to a majority of responding servers then it will not be forced to step down. Fortunately, section 9.6 of [Diego Ongaro’s thesis](https://web.stanford.edu/~ouster/cgi-bin/papers/OngaroPhD.pdf) suggests how this can be achieved using **PreVote**. PreVote requires potential candidates to run a trial election to test if they can win an election before incrementing their term and running a normal election using RequestVote. A server only pre-votes for a potential candidate during the PreVote phase if it would vote for it during a normal election, and importantly, if it has not received an AppendEntries RPC from the leader with in the election timeout. PreVote fixes the problem have we described as servers 4 and 5 will not update their terms as they will not receive pre-votes from the majority of servers.

An alternative fix is to require servers to ignore RequestVote RPCs if they have received an AppendEntries RPC from the leader within the election timeout. This was suggested in section 6 in the [Raft paper](https://raft.github.io/raft.pdf) as mitigation for liveness issues during reconfiguration. However, we will focus on PreVote instead.

## So, does Raft with PreVote guarantee liveness then?

Unfortunately not. In fact, PreVote introduces new liveness issues to Raft. Consider the following example. We have 5 servers and servers 1, 2, and 3 are connected to each other. Server 4 is connected only to server 2 and server 5 has failed.



Initially, server 4 is the leader. It was elected before its links to the other servers (except server 2) failed. Server 4 is now unable to make progress as it is not connected to a majority of servers. Servers 1 and 3 will not hear from the leader so they will timeout and begin the PreVote phase. Neither server will complete its PreVote phase as server 2 will not pre-vote for either server as it still receives regular AppendEntries from the leader (server 4). This system will not able to elect a new leader and the old leader will not be able to make progress.

<figure class="image">
  <img src="/uploads/RAFT 2.jpg" width="80%">
  <figcaption><center>The leader, Server 4, suffers partial network faults but does not step down. Server 2 does not timeout, severs 1 and 3 will fail PreVote because of server 2.</center></figcaption>
</figure>




This can be addressed by requiring leaders to actively step down if they do not receive AppendEntries responses from a majority of servers. This optimisation is sometimes referred to as CheckQuourm and related matters are mentioned in section 6.2 of [Ongaro’s thesis](https://web.stanford.edu/~ouster/cgi-bin/papers/OngaroPhD.pdf) and in [raft discussions](https://github.com/etcd-io/etcd/issues/3866).

## Does Raft with PreVote and CheckQuorum guarantee liveness?

Yes. If there is no leader, then an election (or series of elections) will occur and eventually, a server will be elected leader. To be elected leader, the server must be connected to a majority of servers as it received votes from a majority of servers in the PreVote and RequestVote phases.

CheckQuorum ensures that if the elected leader is no longer connected to a majority of responding servers, it will step down and allow a new leader to be elected.

There will always be at least one server that can win an election. This is the server (or servers) with the most up-to-date log (logs) within the subset of servers which are all online and connected to a majority of responding servers. PreVote ensures that once a leader from this set has been elected, the system will be stable as it will not be forced to step down.


Please answer/discuss/comment/ask on [Twitter](https://twitter.com/heidiann360/status/1338564664523943936?s=20).
