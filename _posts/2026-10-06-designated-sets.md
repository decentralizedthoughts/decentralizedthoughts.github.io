---
title: Designated Sets in Concurrent Simplex and Alpenglow
date: 2026-10-06 08:44:54 -05:00
tags:
  - consensus
author: Ittai Abraham, Clément Burgelin, Antoine Murat, Joachim Neu
---

Recent consensus protocols like [Alpenglow](https://www.anza.xyz/blog/alpenglow-a-new-consensus-for-solana) or [Concurrent Simplex](https://decentralizedthoughts.github.io/2025-07-29-2-round-3-round-simplex/) run two confirmation paths concurrently: a "slow" path with two voting rounds, each using a *small* quorum, and a "fast" path with a single voting round using a *large* quorum.

The "slow" path can actually finish first because distances are not uniform in a geographically distributed system. Some parties are nearby, often on the same continent, while others are across an ocean. In [Banyan's experiments](https://arxiv.org/pdf/2312.05869#page=11), the two smaller quorums can form without waiting for the furthest datacenter, while the larger one-round quorum requires votes from all datacenters. Two voting rounds among nearby parties can therefore take less time than a single voting round among globally dispersed parties.

> **Can we reduce the quorum size on the two-round path to take greater advantage of locality, while keeping the same Byzantine fault bound?**

**The idea in a nutshell**: Let $f$ be the Byzantine fault bound. Each proposer $i$ has an agreed *designated set $D_i$ of $3f+1$ parties*, chosen with locality in mind. When $i$ proposes, each of the two voting rounds *requires only $2f+1$ votes, but they must be from $D_i$*. All parties still cast initial votes. The one-round path keeps its original global threshold, while the two-round path uses the smaller designated-set quorums. The protocol-specific fallback and progress rules are described below.

In Alpenglow's stake notation, the two-round voting path requires 60% of total stake in each round. With designated sets, each round requires only 40% of total stake from a designated set holding 60%. Suppose 40% of total stake is nearby, but collecting 60% requires votes from across an ocean. If that nearby 40% is included in the designated set and responds, both voting rounds can finish locally. Two local rounds can finish before even a single round requiring 60%. Alpenglow's one-round voting path still requires 80%, including distant votes in this example.

Concurrent Simplex uses $n=3f+2p+1$ parties, where $0\le p\le f$. Each round of its two-round voting path changes from $2f+p+1$ votes among all parties to $2f+1$ votes from the designated set of $3f+1$ parties.

## Designated sets in more detail

Consider a partially synchronous system of $n$ parties, at most $f$ of which are Byzantine. We retain each protocol's leader schedule, timers, and proposal rules, and Alpenglow's block dissemination and repair assumptions.

Each proposer $i$ chooses $3f+1$ **designated parties**, forming the set $D_i$. A natural choice is the parties that are nearest to $i$, or those that $i$ considers most reliable. The parties agree on these sets before using them. A proposer can request to update $D_i$ through consensus, with activation at an agreed epoch transition or checkpoint. We leave those details out for simplicity.

Even the worst possible designated set contains at least $2f+1$ honest parties, because there are at most $f$ Byzantine parties overall. So honest parties alone can form a quorum, while any two quorums of $2f+1$ parties from the same $D_i$ overlap in at least $f+1$ parties, including an honest party.

The proofs below show that decisions through either voting path cannot conflict, and that honest parties can advance to the next view or leader window.

**Theorem.** *Consider Concurrent Simplex with $n=3f+2p+1$ and $0\le p\le f$, and Alpenglow with $n=5f+1$, where $f$ is the bound on the Byzantine adversary. After GST, when the proposer is honest:*

1. *Concurrent Simplex commits and Alpenglow finalizes within two voting rounds, with a quorum of $2f+1$ votes from $D_i$ in each round.*
2. *The one-round commit rule still requires $n-p$ votes in Concurrent Simplex (live for $\leq p$ faults), or $4f+1$ votes in Alpenglow (live for $\leq f$ faults).*

Thus, Concurrent Simplex's two-round quorum drops from $2f+p+1$ to $2f+1$ votes, while Alpenglow's drops from 60% to 40% of total stake, without reducing either protocol's Byzantine fault bound.

## Concurrent Simplex with designated sets

Start with the merged protocol in the [Concurrent Simplex post](https://decentralizedthoughts.github.io/2025-07-29-2-round-3-round-simplex/#merged-2-round-and-3-round). In a view $k$ led by $i$, replace the following three quorum conditions:

| Condition | New requirement |
| --- | --- |
| $\mathrm{Slow\text{-}Cert}(k,x)$ | $2f+1$ votes for $x$ from $D_i$ |
| Commit of $x$ through the two-round voting path | $2f+1$ finals for $x$ from $D_i$ |
| $\mathrm{Slow\text{-}Cert}(k,\bot)$ | $2f+1$ finals for $\bot$ from $D_i$ |

Here $x\ne\bot$. The voting rules remain unchanged. Fast certificates still require $f+p+1$ votes, and the one-round commit rule still requires $n-p=3f+p+1$ votes.

Two quorums of $2f+1$ parties from the same $D_i$ intersect in an honest party, and every quorum for the one-round commit rule also intersects each such quorum in an honest party. With an honest proposer, the $2f+1$ honest parties in $D_i$ can supply both rounds of voting. The [Concurrent Simplex with designated sets analysis](#concurrent-simplex-with-designated-sets-analysis) checks the certificates needed to advance between views and commit.

## Alpenglow with designated sets

We modify Votor, Alpenglow's voting protocol. For the main construction, use equal-weight parties with $n=5f+1$. The relevant rules are Table 6, Definitions 15 and 16, and Algorithms 1 and 2 of the [Alpenglow white paper v1.2](https://drive.google.com/file/d/1RPJ9OyohFMuFfLmTB5ydPYlrKTIlUxq9/view), dated July 29, 2026.

Keep one designated set $D_i$ for all slots in proposer $i$'s leader window. Change the certificate thresholds as follows:

| Certificate | New requirement |
| --- | --- |
| Notarization | $2f+1$ initial notarization votes from $D_i$ |
| Finalization | $2f+1$ finalization votes from $D_i$ |
| NotarFallback | $2f+1$ notarization or notarization fallback votes from $D_i$ |
| Skip | $2f+1$ skip or skip fallback votes from $D_i$ |
| FastFinalization | $4f+1$ initial notarization votes |

Each signer is counted once in a certificate. Initial notarization votes from all parties still count toward finalization through the one-round voting path. The existing fallback conditions also count initial votes from all parties, using only the first initial vote received from each party in the slot. Finalization and fallback votes from outside $D_i$ do not contribute to the certificates. Apart from the additional skip condition below, the voting rules remain unchanged.

There is one additional change. A quorum of $2f+1$ parties from $D_i$ can certify one branch while other honest parties vote for a conflicting branch and its descendants. Those descendants may later receive enough initial votes to prevent the original skip condition from firing, while lacking the parent certificates needed for fallback notarization. Thus, changing only the certificate thresholds can leave the leader window stuck.

Extend $\mathrm{SafeToSkip}(s)$ with the following alternative condition:

1. The party has received at least $2f+1$ initial notarization votes for a block $b$ in slot $s$.
2. It has a notarization certificate formed from votes by $D_i$ for a block $c$ in an earlier slot of the same leader window.
3. It has retrieved and verified the ancestry of $b$, and $c$ is not the ancestor of $b$ in that earlier slot.

The additional condition uses the existing skip fallback handler and signing restrictions. The [Alpenglow with designated sets analysis](#alpenglow-with-designated-sets-analysis) includes these rules and the original fallback conditions.

This condition lets honest parties skip descendants of a conflicting branch. It cannot coexist with finalization through the one-round voting path in the same slot: the quorum intersections would require an honest party to vote for two different blocks in one slot. The proof also shows that honest parties can obtain the certificates needed to advance to the next leader window.

## Alpenglow's additional crash tolerance

The construction preserves the Byzantine fault bound but does not preserve Alpenglow's 20+20 guarantee, which also tolerates crashed stake under Rotor non-equivocation. Byzantine and crashed stake can concentrate inside the designated set, leaving too little responsive stake to form a notarization certificate. Rotor non-equivocation does not prevent this.

For example, a designated set holding 60% of total stake could contain 19% Byzantine stake that withholds votes and 19% crashed stake. Only 22% of total stake then responds inside the set, below the required 40%, even though 62% responds globally. The same concentration can prevent skip certificates from forming, so progress to the next leader window is not guaranteed under 20+20 either.

## Conclusion

Agreeing on designated sets lets each proposer favor nearby voters and use smaller quorums in the two-round voting path. Only small changes are required for both protocols, though Alpenglow's extra crash tolerance is lost (this guarantee already relied on Assumption 3, a Rotor non-equivocation assumption that seems to require [stronger synchrony](https://decentralizedthoughts.github.io/2026-01-24-two-round-ps/)).

Your thoughts/comments on [X](https://x.com/ittaia/status/2107469780647354545?s=20).

---

<details markdown="1">
<summary><strong>Proofs: safety and liveness</strong></summary>

## Concurrent Simplex with designated sets analysis

Recall the original voting and view change rules, which remain unchanged.

Certificates are ordered by view, then by Fast before Slow. A proposal includes bottom certificates for all intervening higher certificate positions. Completing a view requires both a fast certificate and a slow certificate, and the party must have sent its Vote and Final. A party can send a bottom vote after receiving $n-f$ votes without a fast value certificate, as in Upon 7 of the merged protocol.

### Safety

**Claim 1. If an honest party commits $x$ through the two-round voting path in view $k$, no slow certificate for another value or for $\bot$ can form in view $k$.**

An honest party sends $(\mathrm{Final},k,x)$ only after receiving $\mathrm{Slow\text{-}Cert}(k,x)$. Two quorums of $2f+1$ parties from $D_i$ intersect in at least one honest party. An honest party sends a Vote for at most one value other than $\bot$ in a view, so two slow value certificates cannot be for different values. An honest party also sends only one Final in a view, so a quorum of finals for $x$ and a quorum of finals for $\bot$ cannot both form.

**Claim 2. If an honest party commits $x$ through the one-round voting path in view $k$, no value certificate for another value and no fast certificate for $\bot$ can form in view $k$.**

A commit through the one-round voting path requires $n-p=3f+p+1$ votes for $x$, including at least $2f+p+1$ honest parties. A fast certificate for another value requires $f+p+1$ votes, but only $f+p$ parties could send those votes. The quorum for this commit and any quorum of $2f+1$ parties from $D_i$ intersect in at least $2f-p+1\ge f+1$ parties, so a slow certificate for another value cannot form.

Consider the first of these honest parties to send $(\mathrm{Vote},k,\bot)$. It already sent $(\mathrm{Vote},k,x)$, so this must be [Upon 7 in the merged 2-/3-round Concurrent Simplex protocol](https://decentralizedthoughts.github.io/2025-07-29-2-round-3-round-simplex/#merged-2-round-and-3-round). Among its $n-f$ received votes, at least $f+p+1$ are from these honest parties and are for $x$. Thus it already has $\mathrm{Fast\text{-}Cert}(k,x)$, contradicting Upon 7. No such party can vote for $\bot$, and the remaining $f+p$ parties cannot form $\mathrm{Fast\text{-}Cert}(k,\bot)$.

**Claim 3. If an honest party commits $x$ in view $k$, no honest party votes for a different value other than $\bot$ in a higher view.**

Consider the first view $\ell>k$ in which an honest party votes for $x'\ne x$, where $x'\ne\bot$. Its proposal includes a value certificate from some view $k'<\ell$.

If $k'<k$, the proposal requires both $\mathrm{Fast\text{-}Cert}(k,\bot)$ and $\mathrm{Slow\text{-}Cert}(k,\bot)$. By Claim 1 and Claim 2, at least one cannot form. If $k'=k$ and the commit used the one-round voting path, no value certificate for $x'$ can form. If the commit used the two-round voting path, $\mathrm{Slow\text{-}Cert}(k,x')$ cannot form. A proposal with $\mathrm{Fast\text{-}Cert}(k,x')$ requires $\mathrm{Slow\text{-}Cert}(k,\bot)$ because Fast < Slow, and that certificate cannot form either. Finally, if $k<k'<\ell$, the certificate requires an honest vote for $x'$ in view $k'$, contradicting the choice of $\ell$. Thus no such vote exists, and later commits must be for $x$.

### Liveness

Suppose no honest party commits and all honest parties enter view $k$. If an honest party receives $\mathrm{Slow\text{-}Cert}(k,x)$ for some $x\ne\bot$, the same votes form $\mathrm{Fast\text{-}Cert}(k,x)$, since $2f+1\ge f+p+1$. [Upon 5 in the merged 2-/3-round Concurrent Simplex protocol](https://decentralizedthoughts.github.io/2025-07-29-2-round-3-round-simplex/#merged-2-round-and-3-round) and Upon 6 ensure it has sent a Vote and a Final, so it forwards both certificates by Upon 8. This also applies if it sent $(\mathrm{Final},k,\bot)$ before receiving $\mathrm{Slow\text{-}Cert}(k,x)$. Otherwise all honest parties eventually send $(\mathrm{Final},k,\bot)$, and the $2f+1$ honest parties in $D_i$ form $\mathrm{Slow\text{-}Cert}(k,\bot)$.

An honest party with $\mathrm{Fast\text{-}Cert}(k,x)$ therefore eventually receives a slow certificate and forwards both. If no honest party receives a fast certificate for any $x\ne\bot$, every honest party eventually receives $n-f$ votes. Each party then sends $(\mathrm{Vote},k,\bot)$ by Upon 7, even if it previously voted for a value. These votes form $\mathrm{Fast\text{-}Cert}(k,\bot)$.

Thus all honest parties receive both certificates and complete the view. The next leader can choose its highest value certificate and include bottom certificates for all higher certificates, so its proposal is valid. The original honest leader argument after GST applies, with at least $2f+1$ honest parties in $D_i$ to vote and then send Final. An honest party that commits earlier forwards the commit proof, so all honest parties eventually commit and terminate.

## Alpenglow with designated sets analysis

Recall the original fallback conditions and signing restrictions, which remain unchanged.

For a slot $s$, let $\mathrm{notar}(b)$ count received initial notarization votes for block $b$ in that slot, and let $\mathrm{skip}(s)$ count received initial skip votes. These counts include all parties, using only the first initial vote received from each party in the slot. The original $\mathrm{SafeToSkip}(s)$ inequality is

$$
\mathrm{skip}(s)+\sum_b\mathrm{notar}(b)-\max_b\mathrm{notar}(b)\ge 2f+1,
$$

where the sum and maximum range over blocks in slot $s$.

For $\mathrm{SafeToNotar}$ on a block $b$ in slot $s$, the party must already have cast an initial vote in $s$, other than a notarization vote for $b$, and must have

$$
\mathrm{notar}(b)\ge 2f+1
\quad\text{or}\quad
\bigl(\mathrm{skip}(s)+\mathrm{notar}(b)\ge 3f+1
\ \text{and}\ \mathrm{notar}(b)\ge f+1\bigr).
$$

The party must hold $b$. If $s$ is not the first slot of the leader window, it must also identify $b$'s parent and obtain a NotarFallback certificate for that parent. A Notarization certificate also meets the NotarFallback requirement.

The skip fallback handler requires that the party has already cast its initial vote in $s$, which was not a skip vote. It first skips other unvoted slots in the window, then sends a skip fallback vote in $s$ only if it has not sent a finalization vote in $s$. A party that previously sent a fallback vote cannot subsequently send a finalization vote in that slot.

### Safety

**Claim 4. If a block is directly finalized, no certificate for another block or skip certificate can form in its slot.**

Two notarization quorums from $D_i$ have an honest party in common, so they cannot be for different blocks. Finalization of $b$ through the two-round voting path requires $f+1$ honest parties in $D_i$ that cast notarization votes for $b$ and finalization votes for its slot. These parties cast no skip vote, vote for another block, or fallback vote. Only $2f$ parties in $D_i$ remain, which is not enough for a conflicting certificate.

Finalization of $b$ through the one-round voting path requires at least $2f+1$ initial votes from $D_i$, which also form a notarization certificate for $b$. It requires $3f+1$ honest initial voters, including $f+1$ in $D_i$. At most $2f$ parties can vote to skip or notarize another block. Thus the original $\mathrm{SafeToSkip}$ condition and $\mathrm{SafeToNotar}$ for another block cannot hold. By Claim 5, the new skip condition cannot hold either. The $f+1$ honest parties in $D_i$ therefore cast no votes for a conflicting certificate.

**Claim 5. The new skip condition and finalization through the one-round voting path cannot occur in the same slot.**

The $2f+1$ initial votes for $b$ required by the new condition must intersect any quorum of $4f+1$ initial notarization votes for another block in an honest party, which cannot cast two initial votes. Such a quorum for $b$ itself must intersect the earlier notarization quorum for $c$ in an honest party. That party voted for both $c$ and the ancestor of $b$ in $c$'s slot. The new condition requires these to be different blocks, a contradiction.

**Claim 6. Every later certified block is a descendant of any directly finalized block.**

A notarization or notar-fallback certificate for $b$ has either $f+1$ honest initial voters from $D_i$ or an honest fallback voter from $D_i$. The initial voters also voted for every ancestor in the window. Outside the first slot, the fallback voter observed a parent certificate. By induction, every earlier ancestor in the window has a certificate or $f+1$ honest initial voters from $D_i$. Suppose a different block was directly finalized in that ancestor's slot. If the ancestor has a certificate, Claim 4 gives a contradiction. Otherwise, the $f+1$ honest voters have a voter in common with the finalized block's notarization quorum, again a contradiction. This uses the same $D_i$ throughout the window.

Every such certificate also requires an honest initial voter: even an honest fallback vote requires at least $f+1$ initial notarization votes. That party voted for the first block in the window after its Pool emitted $\mathrm{ParentReady}$ for the parent $p$. Thus $p$ has a certificate, with skip certificates for all slots between $p$ and that first block.

Now let $a$ be a directly finalized block in an earlier window. If $p$ is in an earlier slot than $a$, $\mathrm{ParentReady}$ requires a skip certificate for $a$'s slot, contradicting Claim 4. If $p$ is in $a$'s slot, Claim 4 requires $p=a$. Otherwise, $p$ is a descendant of $a$ by the argument above if they share a window, or by induction over windows. Thus $b$ is also a descendant of $a$. All directly finalized blocks and their ancestors are on one chain.

### Liveness

Suppose all honest parties have set the timeouts for the slots of a leader window. Each party eventually casts an initial notarization or skip vote in every slot. Suppose, for contradiction, that no honest party ever emits $\mathrm{ParentReady}$ for the next window.

Let $r$ be the highest slot in this window for which an honest party ever observes a notarization certificate, and let $c$ be the block in that certificate. The certificate is broadcast. We will show that all honest parties eventually observe a notar-fallback certificate or a skip certificate in every slot after $r$. If no such certificate for $c$ exists, consider every slot in the window.

No honest party casts a finalization vote in these slots, since that requires a notarization certificate. A block in these slots cannot be finalized by an honest party through a later block either: a later finalization in this window requires a later notarization certificate, and a later window requires a $\mathrm{ParentReady}$ event first. Honest parties therefore still store the blocks for which they cast initial votes in these slots.

Consider one such slot $s$. If no block has more than $2f$ honest initial notarization votes, the $4f+1$ honest initial votes are enough for the original $\mathrm{SafeToSkip}$ inequality. The inequality also holds with Byzantine votes. Each honest party either already cast a skip vote or emits $\mathrm{SafeToSkip}$ and casts a skip-fallback vote. The votes of the honest parties in $D_i$ form a skip certificate.

Otherwise some block $b$ has at least $2f+1$ honest initial notarization votes. These parties also voted for every ancestor of $b$ in this window. If $c$ exists, retrieve these blocks down to slot $r+1$ and compare the parent hash of the block in slot $r+1$ with the hash of $c$. If they are different, the additional skip condition holds. Each honest party that did not cast a skip vote casts a skip-fallback vote, so a skip certificate can form.

If the hashes are equal, use $c$'s certificate as the parent certificate and reason by induction on the slot, from $r+1$ up to $s$. If there is no $c$, start at the first slot of the window, where $\mathrm{SafeToNotar}$ requires no parent certificate. Every block in this chain has $2f+1$ honest initial notarization votes. Once an honest party has received these votes, retrieved the block, and observed any required parent certificate, it either already voted for the block or casts a notar-fallback vote. No honest party has cast a finalization vote in these slots. Thus the votes from the honest parties in $D_i$ form a notar-fallback certificate at each slot, including one for $b$.

Choose the highest slot in the window with a notarization or notar-fallback certificate observed by an honest party. That certificate and the skip certificates for every later slot are enough to emit $\mathrm{ParentReady}$ for the next window. If every slot was skipped, use the parent and skip certificates from the current window's $\mathrm{ParentReady}$ event together with the new skip certificates. This contradicts the assumption. The certificates are broadcast, so all honest parties eventually emit $\mathrm{ParentReady}$ and set the timeouts for the next window.

In a window with an honest leader, all valid blocks form one chain, so the additional skip condition cannot hold. The original timing argument applies. At least $2f+1$ honest parties in $D_i$ can cast notarization and finalization votes, so honest parties finalize within two voting rounds.

</details>
