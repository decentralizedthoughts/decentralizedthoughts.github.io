---
title: Preferred Sets in Concurrent Simplex and Alpenglow
published: true
unlisted: true
sitemap: false
tags:
  - consensus
author: Ittai Abraham, Clément Burgelin, Antoine Murat, Joachim Neu
---

Recent consensus protocols like [Alpenglow](https://www.anza.xyz/blog/alpenglow-a-new-consensus-for-solana) or [Concurrent Simplex](https://decentralizedthoughts.github.io/2025-07-29-2-round-3-round-simplex/) run two confirmation paths concurrently:
a "slow" path with two rounds of voting at a *small* quorum,
and a "fast" path with only one round of voting but at a *large* quorum.
Somewhat counterintuitively, though, in geodistributed deployments, the "slow" path can end up faster than the "fast" path.
The experiments in [Banyan](https://arxiv.org/pdf/2312.05869) (see section 9.3 and references therein) illustrate this effect: two smaller "slow" quorums can be formed with votes from nearby parties, without waiting for votes from the furthest datacenter, while one larger "fast" quorum must include, and thus wait for, the votes from far away.

> Can choosing who votes let us require even fewer votes in the two round path?

**The idea in a nutshell**: Let $f$ be the Byzantine fault bound of the two round voting path. Each proposer $i$ designates a *preferred set $P_i$ of $3f+1$ parties*. The parties know these sets in advance. When $i$ proposes, each of the two voting rounds *requires only $2f+1$ votes, but they must be from $P_i$*. These voters form a *preferred quorum*.

**The preferred set lets us collect fewer votes while retaining the original Byzantine fault bound.** 
In Alpenglow's stake notation, the two round path changes from 60% (among all parties) to 40% (among the parties in the preferred set, holding 60%). The one round path stays unchanged, at 80%.
Concurrent Simplex has a second fault parameter $0\le p\le f$: its one round path tolerates at most $p$ Byzantine parties. In Concurrent Simplex, the two round path changes from $2f+p+1$ (among all parties) to $2f+1$ (among the preferred set, of size $3f+1$).

We give two constructions. Concurrent Simplex needs three minor changes to its two round path quorum conditions. Alpenglow needs four minor certificate changes and an additional condition for skipping a slot.

**Going forward, "slow" refers to two-round path, and "fast" refers to one-round path.** Even if in real commit speed the two-round path may be faster than the one-round path.


## Preferred sets in more detail

Consider $n$ parties with at most $f$ Byzantine in partial synchrony. We retain each protocol's leader schedule, timers, and proposal rules, and Alpenglow's block dissemination and repair assumptions.

Each proposer chooses its **preferred set** $P_i$ of $3f+1$ parties. A very natural choice would be the parties that are nearest to $i$ or the parties that $i$ deems as most reliable. (A proposer can request to update $P_i$ through consensus, with activation at an agreed epoch transition or checkpoint. We leave those details out for simplicity.)

A **preferred quorum** consists of at least $2f+1$ parties *from the preferred set $P_i$*. Two preferred quorums for the same proposer and configuration intersect in at least one honest party. Every preferred set also contains at least $2f+1$ honest parties.

**Theorem.** *Consider Concurrent Simplex with $n=3f+2p+1$ and $0\le p\le f$, and Alpenglow with $n=5f+1$, where $f$ is the bound on the Byzantine adversary. After GST, when the proposer is honest:*

1. *Concurrent Simplex commits and Alpenglow finalizes within two voting rounds, with a quorum of $2f+1$ votes from $P_i$ in each round.*
2. *The one round commit rule still requires $n-p$ votes in Concurrent Simplex (live for $\leq p$ faults), or $4f+1$ votes in Alpenglow (live for $\leq f$ faults).*

The result is that on Concurrent Simplex's two-round path, we require only $2f+1$ rather than $2f+p+1$ votes, and Alpenglow's two-round threshold reduces from 60% to 40% of total stake,
all while preserving the protocols' Byzantine fault bounds.


## Concurrent Simplex with preferred sets

### Protocol changes

Start with the merged protocol in the [Concurrent Simplex post](https://decentralizedthoughts.github.io/2025-07-29-2-round-3-round-simplex/#merged-2-round-and-3-round). In a view $k$ led by $i$, replace its three slow quorum conditions:

| Condition | New requirement |
| --- | --- |
| $\mathrm{Slow\text{-}Cert}(k,x)$ | $2f+1$ votes for $x$ from $P_i$ |
| Slow commit of $x$ | $2f+1$ finals for $x$ from $P_i$ |
| $\mathrm{Slow\text{-}Cert}(k,\bot)$ | $2f+1$ finals for $\bot$ from $P_i$ |

Here $x\ne\bot$. Fast certificates still require $f+p+1$ votes, and fast commits still require $n-p=3f+p+1$ votes.

All remaining rules stay unchanged. Certificates are ordered by view, then by Fast before Slow. A proposal includes bottom certificates for all intervening higher certificate positions. Completing a view requires both a fast certificate and a slow certificate, and the party must have sent its Vote and Final. The timers and the rule permitting a bottom vote after receiving $n-f$ votes without a fast value certificate also remain unchanged.

The preferred quorum replaces the original slow quorum. It reduces the number of votes needed from $2f+p+1$ to $2f+1$.

### Why safety still holds

**Claim 1. If an honest party slow commits $x$ in view $k$, no slow certificate for another value or for $\bot$ can form in view $k$.**

An honest party sends $(\mathrm{Final},k,x)$ only after receiving $\mathrm{Slow\text{-}Cert}(k,x)$. Two quorums of $2f+1$ parties from $P_i$ intersect in at least one honest party. An honest party sends a Vote for at most one value other than $\bot$ in a view, so two slow value certificates cannot be for different values. An honest party also sends only one Final in a view, so a quorum of finals for $x$ and a quorum of finals for $\bot$ cannot both form.

**Claim 2. If an honest party fast commits $x$ in view $k$, no value certificate for another value and no fast certificate for $\bot$ can form in view $k$.**

A fast commit requires $n-p=3f+p+1$ votes for $x$, including at least $2f+p+1$ honest parties. A fast certificate for another value requires $f+p+1$ votes, but only $f+p$ parties could send those votes. The fast commit quorum and any quorum of $2f+1$ parties from $P_i$ intersect in at least $2f-p+1\ge f+1$ parties, so a slow certificate for another value cannot form.

Consider the first of these honest parties to send $(\mathrm{Vote},k,\bot)$. It already sent $(\mathrm{Vote},k,x)$, so this must be [Upon 7 in the merged 2-/3-round Concurrent Simplex protocol](https://decentralizedthoughts.github.io/2025-07-29-2-round-3-round-simplex/#merged-2-round-and-3-round). Among its $n-f$ received votes, at least $f+p+1$ are from these honest parties and are for $x$. Thus it already has $\mathrm{Fast\text{-}Cert}(k,x)$, contradicting Upon 7. No such party can vote for $\bot$, and the remaining $f+p$ parties cannot form $\mathrm{Fast\text{-}Cert}(k,\bot)$.

**Claim 3. If an honest party commits $x$ in view $k$, no honest party votes for a different value other than $\bot$ in a higher view.**

Consider the first view $\ell>k$ in which an honest party votes for $x'\ne x$, where $x'\ne\bot$. Its proposal includes a value certificate from some view $k'<\ell$.

If $k'<k$, the proposal requires both $\mathrm{Fast\text{-}Cert}(k,\bot)$ and $\mathrm{Slow\text{-}Cert}(k,\bot)$. By Claim 1 and Claim 2, at least one cannot form. If $k'=k$ and the commit was fast, no value certificate for $x'$ can form. If the commit was slow, $\mathrm{Slow\text{-}Cert}(k,x')$ cannot form. A proposal with $\mathrm{Fast\text{-}Cert}(k,x')$ requires $\mathrm{Slow\text{-}Cert}(k,\bot)$ because Fast < Slow, and that certificate cannot form either. Finally, if $k<k'<\ell$, the certificate requires an honest vote for $x'$ in view $k'$, contradicting the choice of $\ell$. Thus no such vote exists, and later commits must be for $x$.

### Why liveness still holds

Suppose no honest party commits and all honest parties enter view $k$. If an honest party receives $\mathrm{Slow\text{-}Cert}(k,x)$ for some $x\ne\bot$, the same votes form $\mathrm{Fast\text{-}Cert}(k,x)$, since $2f+1\ge f+p+1$. [Upon 5 in the merged 2-/3-round Concurrent Simplex protocol](https://decentralizedthoughts.github.io/2025-07-29-2-round-3-round-simplex/#merged-2-round-and-3-round) and Upon 6 ensure it has sent a Vote and a Final, so it forwards both certificates by Upon 8. This also applies if it sent $(\mathrm{Final},k,\bot)$ before receiving $\mathrm{Slow\text{-}Cert}(k,x)$. Otherwise all honest parties eventually send $(\mathrm{Final},k,\bot)$, and the $2f+1$ honest parties in $P_i$ form $\mathrm{Slow\text{-}Cert}(k,\bot)$.

An honest party with $\mathrm{Fast\text{-}Cert}(k,x)$ therefore eventually receives a slow certificate and forwards both. If no honest party receives a fast certificate for any $x\ne\bot$, every honest party eventually receives $n-f$ votes. Each party then sends $(\mathrm{Vote},k,\bot)$ by Upon 7, even if it previously voted for a value. These votes form $\mathrm{Fast\text{-}Cert}(k,\bot)$.

Thus all honest parties receive both certificates and complete the view. The next leader can choose its highest value certificate and include bottom certificates for all higher certificates, so its proposal is valid. The original honest leader argument after GST applies, with at least $2f+1$ honest parties in $P_i$ to vote and then send Final. An honest party that commits earlier forwards the commit proof, so all honest parties eventually commit and terminate.


## Alpenglow with preferred sets

We modify Votor, Alpenglow's voting protocol. For the main construction, use equal weight parties with $n=5f+1$. The relevant rules are Table 6, Definitions 15 and 16, and Algorithms 1 and 2 of the [Alpenglow white paper v1.2](https://drive.google.com/file/d/1RPJ9OyohFMuFfLmTB5ydPYlrKTIlUxq9/view), dated July 29, 2026.

### Protocol changes

Keep one preferred set $P_i$ for all slots in proposer $i$'s leader window. Change the certificate thresholds as follows:

| Certificate | New requirement |
| --- | --- |
| Notarization | $2f+1$ initial notarization votes from $P_i$ |
| Finalization | $2f+1$ finalization votes from $P_i$ |
| NotarFallback | $2f+1$ notarization or notarization fallback votes from $P_i$ |
| Skip | $2f+1$ skip or skip fallback votes from $P_i$ |
| FastFinalization | $4f+1$ initial notarization votes  |

Each signer is counted once in a certificate. Preserve the vote counts in the existing fallback conditions.

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

The party must hold $b$. If $s$ is not the first slot of the leader window, it must also identify $b$'s parent and obtain a NotarFallback certificate for that parent. A Notarization certificate also meets the NotarFallback requirement. These inherited conditions remain unchanged.

There is one additional change. A preferred quorum can certify one branch while other honest parties vote for a conflicting branch and its descendants. In a later slot, those descendants may have enough votes to prevent the original skip condition, but their parents cannot obtain the certificates required for fallback. Changing only the certificate thresholds can therefore leave the window stuck.

Extend $\mathrm{SafeToSkip}(s)$ with the following alternative condition:

1. The party has received at least $2f+1$ initial notarization votes for a block $b$ in slot $s$.
2. It has a preferred notarization certificate for a block $c$ in an earlier slot of the same leader window.
3. It has retrieved and verified the ancestry of $b$, and $c$ is not the ancestor of $b$ in that earlier slot.

Retain the original event restriction that the party has already cast its initial vote in $s$, which was not a skip vote. The existing handler and its signing restrictions remain unchanged: it first skips other unvoted slots in the window, then sends a skip fallback vote in $s$ only if it has not sent a finalization vote in $s$. A party that previously sent a fallback vote cannot subsequently send a finalization vote in that slot. No change is made to $\mathrm{SafeToNotar}$.

### Why safety still holds

**Claim 4. If a block is directly finalized, no certificate for another block or skip certificate can form in its slot.**

Two notarization quorums from $P_i$ have an honest party in common, so they cannot be for different blocks. A slow finalization of $b$ requires $f+1$ honest parties in $P_i$ that cast notarization votes for $b$ and finalization votes for its slot. These parties cast no skip vote, vote for another block, or fallback vote. Only $2f$ parties in $P_i$ remain, which is not enough for a conflicting certificate.

A fast finalization of $b$ requires at least $2f+1$ initial votes from $P_i$, which also form a notarization certificate for $b$. It requires $3f+1$ honest initial voters, including $f+1$ in $P_i$. At most $2f$ parties can vote to skip or notarize another block. Thus the original $\mathrm{SafeToSkip}$ condition and $\mathrm{SafeToNotar}$ for another block cannot hold. By Claim 5, the new skip condition cannot hold either. The $f+1$ honest parties in $P_i$ therefore cast no votes for a conflicting certificate.

**Claim 5. The new skip condition and fast finalization cannot occur in the same slot.**

The $2f+1$ initial votes for $b$ required by the new condition must intersect any $4f+1$ fast quorum for another block in an honest party, which cannot cast two initial votes. A fast quorum for $b$ itself must intersect the earlier notarization quorum for $c$ in an honest party. That party voted for both $c$ and the ancestor of $b$ in $c$'s slot. The new condition requires these to be different blocks, a contradiction.

**Claim 6. Every later certified block is a descendant of any directly finalized block.**

A notarization or notar-fallback certificate for $b$ has either $f+1$ honest initial voters from $P_i$ or an honest fallback voter from $P_i$. The initial voters also voted for every ancestor in the window. Outside the first slot, the fallback voter observed a parent certificate. By induction, every earlier ancestor in the window has a certificate or $f+1$ honest initial voters from $P_i$. Suppose a different block was directly finalized in that ancestor's slot. If the ancestor has a certificate, Claim 4 gives a contradiction. Otherwise, the $f+1$ honest voters have a voter in common with the finalized block's notarization quorum, again a contradiction. This uses the same $P_i$ throughout the window.

Every such certificate also requires an honest initial voter: even an honest fallback vote requires at least $f+1$ initial notarization votes. That party voted for the first block in the window after its Pool emitted $\mathrm{ParentReady}$ for the parent $p$. Thus $p$ has a certificate, with skip certificates for all slots between $p$ and that first block.

Now let $a$ be a directly finalized block in an earlier window. If $p$ is in an earlier slot than $a$, $\mathrm{ParentReady}$ requires a skip certificate for $a$'s slot, contradicting Claim 4. If $p$ is in $a$'s slot, Claim 4 requires $p=a$. Otherwise, $p$ is a descendant of $a$ by the argument above if they share a window, or by induction over windows. Thus $b$ is also a descendant of $a$. All directly finalized blocks and their ancestors are on one chain.

### Why liveness still holds

Suppose all honest parties have set the timeouts for the slots of a leader window. Each party eventually casts an initial notarization or skip vote in every slot. Suppose, for contradiction, that no honest party ever emits $\mathrm{ParentReady}$ for the next window.

Let $r$ be the highest slot in this window for which an honest party ever observes a notarization certificate, and let $c$ be the block in that certificate. The certificate is broadcast. We will show that all honest parties eventually observe a notar-fallback certificate or a skip certificate in every slot after $r$. If no such certificate for $c$ exists, consider every slot in the window.

No honest party casts a finalization vote in these slots, since that requires a notarization certificate. A block in these slots cannot be finalized by an honest party through a later block either: a later finalization in this window requires a later notarization certificate, and a later window requires a $\mathrm{ParentReady}$ event first. Honest parties therefore still store the blocks for which they cast initial votes in these slots.

Consider one such slot $s$. If no block has more than $2f$ honest initial notarization votes, the $4f+1$ honest initial votes are enough for the original $\mathrm{SafeToSkip}$ inequality. The inequality also holds with Byzantine votes. Each honest party either already cast a skip vote or emits $\mathrm{SafeToSkip}$ and casts a skip-fallback vote. The votes of the honest parties in $P_i$ form a skip certificate.

Otherwise some block $b$ has at least $2f+1$ honest initial notarization votes. These parties also voted for every ancestor of $b$ in this window. If $c$ exists, retrieve these blocks down to slot $r+1$ and compare the parent hash of the block in slot $r+1$ with the hash of $c$. If they are different, the additional skip condition holds. Each honest party that did not cast a skip vote casts a skip-fallback vote, so a skip certificate can form.

If the hashes are equal, use $c$'s certificate as the parent certificate and reason by induction on the slot, from $r+1$ up to $s$. If there is no $c$, start at the first slot of the window, where $\mathrm{SafeToNotar}$ requires no parent certificate. Every block in this chain has $2f+1$ honest initial notarization votes. Once an honest party has received these votes, retrieved the block, and observed any required parent certificate, it either already voted for the block or casts a notar-fallback vote. No honest party has cast a finalization vote in these slots. Thus the votes from the honest parties in $P_i$ form a notar-fallback certificate at each slot, including one for $b$.

Choose the highest slot in the window with a notarization or notar-fallback certificate observed by an honest party. That certificate and the skip certificates for every later slot are enough to emit $\mathrm{ParentReady}$ for the next window. If every slot was skipped, use the parent and skip certificates from the current window's $\mathrm{ParentReady}$ event together with the new skip certificates. This contradicts the assumption. The certificates are broadcast, so all honest parties eventually emit $\mathrm{ParentReady}$ and set the timeouts for the next window.

In a window with an honest leader, all valid blocks form one chain, so the additional skip condition cannot hold. The original timing argument applies. At least $2f+1$ honest parties in $P_i$ can cast notarization and finalization votes, so honest parties finalize within two voting rounds.

## Notes

The construction does not provide Alpenglow's 20+20 guarantee, which requires Rotor non-equivocation. So in a way we are trading off better good-case performance for worst bad-case liveness.
