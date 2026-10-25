---
title: Blockchain Resource Pools and a CAP-esque Impossibility Result
date: 2022-03-03 12:09:00 -05:00
tags:
- research
- lowerbound
- blockchain
author: Andrew Lewis-Pye, Tim Roughgarden
chapters:
  - /2026-06-28-chapter-lower-bounds/
---

The consensus layers of different blockchain protocols can look very
different from one another.  For example, to achieve sybil-resistance,
some protocols use *proof-of-work* (selecting each block producer
randomly, with probability proportional to its computational power),
while some use *proof-of-stake* (with probabilities proportional to the
amount of locked-up stake).  To achieve consensus, some blockchain
protocols use a longest-chain rule to resolve forks in-protocol, while
others use BFT-style consensus to (with high probability) avoid forks
and achieve instant finality.  (These lists are not exhaustive, and
some blockchain protocols take still other approaches to
sybil-resistance or consensus.)  Bitcoin is one example (among
several) of a proof-of-work longest-chain protocol.  Algorand is one
example (among many) of a proof-of-stake BFT-style protocol.

Different blockchain consensus protocols also provide different sets
of mathematical guarantees.  For example, typical proof-of-work (PoW)
longest-chain protocols like Bitcoin achieve liveness (i.e.,
outstanding transactions are continually processed) and probabilistic
finality (i.e., with high probability, confirmed transactions do not
get rolled back), under two assumptions: (i) at least 51% of the block
production power (i.e., hashrate) is controlled by nodes that honestly
follow the intended protocol; and (ii) the communication network is
reliable (in the sense of the synchronous model), with all messages
arriving at their destinations in a bounded amount of time (see
<https://eprint.iacr.org/2014/765.pdf>,
<https://eprint.iacr.org/2016/454.pdf>, or
<https://arxiv.org/pdf/2005.10484.pdf> for details).  Such a protocol
does not offer any finality guarantees if there can be unbounded
network delays---for example, if there is a lengthy network partition,
each side of the partition will grow its own longest chain
independently, and the shorter of the two will be rolled back when the
partition ends and the two sides compare notes.

A typical proof-of-stake (PoS) BFT-type blockchain protocol like
Algorand satisfies an incomparable set of promises, as for liveness
and probabilistic finality it requires a stronger version of
assumption (i) and a weaker version of (ii).  Specifically, the
protocol is guaranteed to satisfy liveness only if at least 67% of the
stake is honest.  On the other hand, the protocol satisfies
probabilistic finality even in the partially synchronous model, in
which messages can suffer unbounded delays (due, e.g., to network
outages or denial-of-service attacks).  (For Algorand specifically,
see <https://eprint.iacr.org/2018/377.pdf> for details.)

The recurring question investigated in our joint research is:
>to what extent do the desired guarantees of a blockchain protocol dictate how
the protocol needs to be implemented?  Which design decisions are the
fundamental drivers behind the mathematical differences between, say,
the Bitcoin and Algorand protocols?  Is it because one uses PoW while
the other uses PoS?  Or that one uses a longest-chain rule while the
other uses BFT-style consensus?  Both?  Something else?

The rest of this blog post highlights one impossibility result from
our work, which effectively shows that PoS sybil resistance (or
something like it) is indeed fundamental to the probabilistic finality
guarantees of a protocol like Algorand.

An impossibility result requires a formal model of what a blockchain
protocol can do.  Our work offers a general model that enables direct
comparisons between very different blockchain protocols (e.g., PoW
longest-chain protocols vs.\ PoS BFT-style protocols).  The most
salient part of the model is the notion of a *resource pool* (e.g.,
hashrate or stake), which controls the extent to which different nodes
can produce blocks, vote, etc.  (See our paper linked at the end of
this post for more details and comparisons to previous work.)

Our work shows that there is a big difference between resource pools
that are "sized," meaning that the blockchain state determines all the
resource balances, and those that are "unsized," with the resource
balances independent of the blockchain state.  Typical PoS blockchains
are appropriately modeled with a sized resource pool (as stake amounts
are recorded as part of the blockchain state), while unsized resource
pools provide a good model for reasoning about typical PoW blockchains
(as nodes' hashrates can change independently of any updates to the
blockchain state).

Here's the statement of today's impossibility result (phrased in the
same "choose 2 of 3" format as the CAP Theorem from distributed
systems):

**Theorem:** No blockchain protocol:
1. operates in the unsized setting;
2. is adaptively live in the synchronous setting; and
3. satisfies probabilistic finality in the partially synchronous
setting.

In the theorem statement, "adaptively live" means that liveness must
hold even in the face of massive (e.g., 100x) changes in the total
resource balance.  In the sized setting (e.g., typical PoS), any such
change would be immediately detectable on-chain and thus easy to
adapt to automatically.  In the unsized setting (e.g., typical PoW),
liveness with respect to constant resource balances does not
automatically imply adaptive liveness.  Nonetheless, a typical PoW
longest-chain protocol like Bitcoin does indeed satisfy adaptive
liveness---if the total hashrate suddenly drops by a factor of~100,
the rate of block production also drops by a factor of~100 (at least
until the next difficulty adjustment) but remains bounded away from
zero.

Thus, PoW longest-chain protocols like Bitcoin satisfy (1) and (2),
while PoS BFT-style protocols like Algorand satisfy (2) and (3).
Our impossibility result shows that you can't have them all!  In
particular, there's no hope of offering Algorand-like guarantees
without using PoS sybil-resistance or some alternative with resource
balances directly observable on-chain.  Said another way, Bitcoin's
reliance on PoW sybil-resistance forces the other compromises that it
makes.

Here's a very rough sketch of the proof (see our paper for details).
Suppose we're in the unsized setting (property (1)), and suppose a
node with a nonzero resource balance stops hearing any new messages
from anybody else.  This node cannot distinguish between two plausible
scenarios: (i) all the other nodes have lost all their resources and
therefore can no longer participate in the protocol; or (ii) all the
messages incoming to the node have been massively delayed.  (In the
sized setting, these scenarios *would* be distinguishable because the
other nodes' resource balances would be directly observable via the
blockchain's state.)  Now the node faces a catch-22 situation.  It
must choose whether to stop producing new blocks or not.  If it does
stop and (i) is the actual reality, the node will violate adaptive
liveness (property (2)).  If it plows ahead with block production and
(ii) is the actual reality (which is a possibility in the partially
synchronous setting), the node will violate finality (as any blocks it
produces might well conflict with as-yet-unheard-of blocks that other
nodes have busily been producing, triggering later rollbacks).
[end proof sketch]

This result exemplifies our research agenda, to understand the extent
to which the desired guarantees of a blockchain protocol dictate its
implementation.  We expect that many more results along such lines are
possible.

Further reading/listening:
* paper: <http://timroughgarden.org/papers/RPCAP_public_arxiv.pdf>
* talk: <https://www.youtube.com/watch?v=EfsSV7ni2ZM>

Your thoughts/comments on [twitter](...)
