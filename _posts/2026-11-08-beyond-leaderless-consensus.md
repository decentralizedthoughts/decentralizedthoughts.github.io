---
title: Beyond Leaderless Consensus
date: 2026-11-08 10:00:00 +02:00
tags:
- consensus
- randomness
author: Ittai Abraham, Kaya Alpturer, Pranav Garimidi, Joachim Neu, Tim Roughgarden, Ertem Nusret Tas
background:
  - /2026-05-14-simplex-FVS/
  - /2024-03-07-mobile-is-FLP/
continue_reading:
  - /2024-12-10-bind-and-rand/
---

Most consensus protocols are leader based.
If the current leader crashes or acts maliciously, progress stops until another leader is elected.
An adversary that can change which replica it crashes each round can target
every current leader and prevent the protocol from
[terminating](https://decentralizedthoughts.github.io/2024-03-07-mobile-is-FLP/).

In this post we present **Multi-Leader Fixed-View Simplex (ML-FVS)** from our paper
[*Beyond Leaderless: Randomized Consensus Against Mobile Crashes*][paper].
It modifies [Simplex][fvs] to tolerate mobile crashes.

The core idea is to choose the leader *in hindsight*, as in [Multi-world VABA][multiworld].
Two potential leaders propose, and replicas vote on *both their proposals* instead of on a single proposal.
A randomness beacon revealed after the voting then ranks the leaders.
The adversary must choose which proposal broadcast to interrupt
[before learning the priority order][binding].

## Model and result

There are $n=3f+1$ replicas. The adversary has a total fault budget of $f$
and a mobile crash budget of one:

* *Byzantine corruption at time $t$*: The adversary chooses a replica to corrupt, spending one unit from its total fault budget $f$ permanently. After a delay, the target becomes Byzantine
  at $t+\Delta$.
* *Mobile crash at time $t$*: The adversary chooses a replica to immediately crash and use one unit of both budgets. A crash
  may interrupt a broadcast after messages have been sent to only some recipients.
  Crashes preserve local state and reveal no secrets to the adversary.
* *Healing at time $t$*: The adversary can heal a crashed party and that immediately resumes it. At time $t+\Delta$, the adversary gets back one unit of both the mobile crash and the total budget. Messages arriving at a crashed replica are buffered and processed when it heals.

We assume a partially synchronous network: a message sent at time $t$ arrives before $\max\{t,\mathrm{GST}\}+\Delta$. Replicas have synchronized clocks. View $v$ starts at $s_v=3v\Delta$.

Let $\mathrm{Leaders}(v)$ be the set of two distinct replicas that lead view $v$.
Their identities are public by $s_v$.

A view $v$ is a **good case view** if $s_v\geq\mathrm{GST}+\Delta$ and both
leaders are not corrupted at time $s_v$.

**Theorem.** For $n=3f+1$ and $f\geq1$, ML-FVS guarantees:

* **Agreement and validity.** All finalized blocks are externally valid and
  lie on a single chain.
* **Good case latency.** With an ideal threshold beacon, in each good case
  view $v$, every replica that remains active and honest throughout the view
  obtains a final certificate by $s_v+3\Delta$ with probability at least $1/2$.

Starting from a fixed view, if every successive view is a good case view
until success, the expected latency is at most $6\Delta$.

## Selecting the block in hindsight

**Vote sets.** At $s_v+\Delta$, each replica forms a set containing the first
valid proposal it has received from each of the two leaders. It sends one
signed Vote containing this set and its beacon share.

**Beacon reconstruction.** For each view $v$, the beacon outputs a uniformly random
ranking $\mathrm{rank}_v$ of the potential leaders, together with a verifiable proof.
Each leader $j$ receives a distinct rank $\mathrm{rank}_v(j)$; smaller ranks have
higher priority. Any $n-f$ valid shares from distinct replicas reconstruct the
same ranking and proof. Rankings are independent across views and unpredictable
before $n-f$ shares are available. Honest replicas fix their vote sets before
processing shares released at the voting deadline.

**Resolving votes.** A vote resolves to the leader and block pair of the proposal
whose leader has the smallest $\mathrm{rank}_v(j)$ in its set, or to $\bot$ if
its set is empty. A valid vote is
signed and contains only valid proposals for its own view, at most one per
leader. A vote certificate
$\mathrm{VC}_v(x)$ contains $n-f$ valid votes from distinct replicas resolving
to the same leader and block $x$, together with the verified beacon output
and proof.

If $\mathrm{rank}_v(j)<\mathrm{rank}_v(i)$, votes containing
$\{B_i,B_j\}$ and $\{B_j\}$ both resolve to $(j,B_j)$, so the vote sets
need not be identical to form a certificate.

## Multi-Leader Fixed-View Simplex

We use the messages $\mathrm{Vote}, \mathrm{Final},$ and $\mathrm{Skip}$. As usual, we form a certificate when $n-f$ distinct signed messages agree. For view $v$:

- A Vote message $\langle\mathrm{Vote}(v,R,s)\rangle$ contains a set of proposals $R$ and a beacon share $s$. A $\mathrm{VC}_v(x)$ combines $n-f$ votes from distinct replicas that resolve to the same leader and block $x$. Each nonempty vote selects the proposal whose leader has the smallest $\mathrm{rank}_v(j)$ in its set.
- A Final message $\langle\mathrm{Final}(v,x,C)\rangle$ includes a valid vote
certificate $C$ for view $v$ and block $x$. A final certificate
$\mathrm{FC}_v(x)$ contains $n-f$ signed Final messages agreeing on $(v,x)$.
- A skip certificate $\mathrm{SC}_v$ contains $n-f$ signed
$\langle\mathrm{Skip}(v)\rangle$ messages.

A proposal from replica $j$ for view $v$ has the form

$$
\langle\mathrm{Propose}(v,x,w)\rangle.
$$

It includes an external validity proof for $x$ and the certificates specified
below. The proposal is valid if $j\in\mathrm{Leaders}(v)$,
$x$ is externally valid, $0\leq w<v$, all included certificates verify, and:

* If $w=0$, then $x$ extends genesis and the proposal includes
  $\mathrm{SC}_u$ for every $0<u<v$.
* If $w>0$, then the proposal includes $\mathrm{VC}_w(y)$ for a block $y$
  that $x$ extends, and $\mathrm{SC}_u$ for every $w<u<v$.

In the pseudocode below, we denote signed messages by `<M>` and the
replica's beacon share for view `v` as `share_v`.

```text
1. Propose: At time s_v, each leader in Leaders(v):
    If a valid proposal can be formed from its known certificates:
        Let <Propose(v, x, w)> be such a proposal with maximum w
        Send <Propose(v, x, w)> to all

2. Vote and send beacon share: At time s_v + Δ:
    Let R_v be the set of first valid proposals for v received from each leader in Leaders(v)
    Send <Vote(v, R_v, share_v)> to all

3. Resolve and send Final or Skip: At time s_v + 2Δ:
    If n-f valid beacon shares for v are known:
        Reconstruct rank_v and its proof

    If rank_v has been verified:
        For each known valid <Vote(v, R, share)>:
            If R is empty:
                Resolve this Vote to ⊥
            Else:
                Let j minimize rank_v(j) among leaders with a proposal in R
                Let x be the block in that proposal
                Resolve this Vote to (j, x)

        If n-f Votes from distinct replicas resolve to the same (j, x):
            Form VC_v(x) with these Votes, rank_v, and its proof

    If VC_v(x) is known:
        Send <Final(v, x, VC_v(x))> to all
    Else:
        Send <Skip(v)> to all

4. Decide and advance: At time s_v + 3Δ:
    For each known final certificate FC_w(x), including earlier views:
        Decide x
    Enter view v+1

5. Form and forward certificates: At all times, for every view w:
    If n-f valid Final messages for (w,x) are known and no FC_w is known:
        Form FC_w(x)

    If n-f valid Skip messages for w are known and no SC_w is known:
        Form SC_w

    If a valid final or skip certificate C is known and has not yet been forwarded:
        Send C to all
```

## Agreement

Observe that two quorums of $n-f$ intersect in at least $f+1$ replicas as usual. Since at most $f$ replicas ever become Byzantine, their intersection contains an always honest replica.
Its vote resolves to one leader and block pair, so a view has at most one certified pair. Every certified block is
externally valid because its certificate includes an honest vote. Hence at most one block gets a vote certificate in each view and it must be externally valid.

A final certificate and a skip certificate cannot coexist in one view:
an always honest replica in their intersection would have signed both.
If $\mathrm{FC}_v(x)$ exists, a later valid proposal cannot use genesis or a view
before $v$, since that would require
$\mathrm{SC}_v$. It must extend a block certified in a view at least $v$.
Induction on later views, starting with uniqueness in view $v$, shows that
every later certified block extends $x$.

## Tolerating mobile crashes

**Claim 1: Active honest quorums.** For every time $t$, at least $n-f$ replicas
remain active and honest throughout $(t,t+\Delta]$.

**Proof.** Every replica crashed at some time in $(t,t+\Delta]$ either
remains crashed at the end or heals at a time $h>t$, leaving its charge
outstanding until $h+\Delta>t+\Delta$. Add the permanent charges for
replicas Byzantine by the interval's end. At most $f$ replicas have these
charges, leaving at least $n-f$ active and honest throughout.

**Claim 2: Certificate catch up.** For every view $w$, an honest replica
active at time $t\geq\max\{\mathrm{GST},s_w+2\Delta\}+\Delta$ has either
a vote certificate or a skip certificate for $w$.

**Proof.** By Claim 1, a quorum stays active and honest throughout
$(s_w+\Delta,s_w+2\Delta]$.
At $s_w+2\Delta$, either one member sends Final with a vote certificate,
or all members send Skip. The attached certificate or $n-f$ skip votes
arrive by the claimed time and are processed on arrival or healing.

At a view start $s_v\geq\mathrm{GST}+\Delta$, Claim 2 applies to every
earlier view. An active honest leader can therefore propose: it uses its
highest earlier vote certificate and skip certificates for all intervening
views, or extends genesis if it has only skip certificates.

**Claim 3: Good case latency.** In a good case view $v$, every replica that
remains active and honest throughout the view obtains a final certificate
by $s_v+3\Delta$ with probability at least $1/2$.

**Proof.** During the proposal step, at most one leader can have an
outstanding crash charge. Healing cannot return that charge during the
step. Thus at least one leader completes its valid proposal broadcast at
$s_v$. Neither leader is corrupted at $s_v$, so neither can become Byzantine
before $s_v+\Delta$. The set of completed broadcasts is
fixed before the beacon is revealed, so the leader with the smallest rank in
$\mathrm{Leaders}(v)$ is in that set with probability at least $1/2$.

Condition on this event, and let $x$ be that leader's block. For
$a\in\{0,1,2\}$, let $H_a$ be the replicas active and honest throughout
$(s_v+a\Delta,s_v+(a+1)\Delta]$. Each set has at least $n-f$ replicas by
Claim 1.

Every member of $H_0$ receives $x$'s proposal before the voting deadline.
Its leader cannot send a conflicting proposal before that deadline, so this
is the first valid proposal received from that leader. All $H_0$ votes
therefore resolve to the same leader and block $x$.

Every member of $H_1$ receives these $n-f$ votes and beacon shares by
$s_v+2\Delta$ and sends Final for $x$ with the resulting vote certificate
at that time.

Every member of $H_2$ receives these $n-f$ Final messages by
$s_v+3\Delta$, forms the final certificate, and finalizes $x$ at that time.
Every replica that remains active and honest throughout the view belongs
to $H_2$.

Starting from a fixed view, suppose successive views meet the good case
conditions until success. Each fails with conditional probability at most
$1/2$. If $N$ counts views through the first success, then

$$
\Pr[N>m]\leq 2^{-m},\qquad \mathbb{E}[N]\leq 2.
$$

Each view lasts $3\Delta$, so expected latency is at most $6\Delta$, and
the probability of failing forever is zero.

With a mobile crash budget of $c\leq f$ and the same refund delay, $c+1$
leaders give success probability at least $1/(c+1)$ in each good case view
and expected latency at most $3\Delta(c+1)$ over successive good case views.
Here, a good case view requires all $c+1$ leaders to be uncorrupted at its start.

> Read our [paper on arXiv][paper] for more!

## Notes

**Mobile suspensions.** Antoniadis et al.’s
[*Leaderless Consensus*](https://gramoli.github.io/pubs/ICDCS2021-leaderless.pdf)
solves consensus when the adversary can crash (suspend) one replica every round only for the *entire* round. We use randomization to tolerate a stronger form of mobile failure: the adversary can crash a replica at any point
during a round, including in the middle of its broadcast, when only some
replicas have received the proposal.

**Adaptive corruptions.** Choosing a leader *in hindsight* is used by
[Katz and Koo][katz-koo] and
[VABA][vaba].
Both use this idea to handle adaptive corruptions: parties send messages
before the random leader choice is revealed.

**DAG protocols.** [Mysticeti-C](https://arxiv.org/abs/2310.14821) also uses
multiple leaders per round, but its proposer order is determined in advance.

**Timing games.** Our [paper][paper] also studies leaders that delay proposals
to collect more valuable transactions. In our evaluation with random network
delays and leader stalls, adding a second leader reduces failed views even
when leaders delay their proposals strategically.

[fvs]: https://decentralizedthoughts.github.io/2026-05-14-simplex-FVS/
[mobile]: https://decentralizedthoughts.github.io/2024-03-07-mobile-is-FLP/
[binding]: https://decentralizedthoughts.github.io/2024-12-10-bind-and-rand/
[multiworld]: https://decentralizedthoughts.github.io/2024-12-10-multi-world-vaba/
[katz-koo]: https://www.cs.umd.edu/~jkatz/papers/BA.pdf
[vaba]: https://arxiv.org/abs/1811.01332
[paper]: https://arxiv.org/abs/2611.01323
