---
title: Fast Simplex on a Fixed View Schedule
date: 2026-05-17 00:00:00 -05:00
tags:
- consensus
author: Ittai Abraham
---

[Simplex FVS](https://decentralizedthoughts.github.io/2026-05-14-simplex-FVS/)
uses [fixed views](https://decentralizedthoughts.github.io/2026-03-07-simultaneous-agreement/) of length $3\Delta$. This post gives a two round version with
view length $2\Delta$, using the
[two round Simplex](https://decentralizedthoughts.github.io/2025-07-18-two-round-Simplex/)
certificate structure.
For a map of the surrounding Simplex line, see the [Simplex chapter](https://decentralizedthoughts.github.io/2026-05-25-chapter-simplex/).

The price is the usual one for two round BFT: we use $n=5f+1$ parties. A view
has only one leader proposal and one round of votes. If a later leader needs to
skip the view, it does not wait for a skip vote sent at the boundary. It uses
the two round Simplex no commit certificate: a vector of votes containing
no small value certificate.

## Model

There are

$$
n=5f+1
$$

parties, at most $f$
[Byzantine](https://decentralizedthoughts.github.io/2019-06-07-modeling-the-adversary/).
All protocol messages are signed. A certificate is a forwardable set of signed
messages.

The network is
[partially synchronous](https://decentralizedthoughts.github.io/2019-06-01-2019-5-31-models/).
Before GST, message delay is unbounded. After GST, every message from one
honest party to another is delivered within $\delta\leq\Delta$ of the later of
GST and its send time.

We assume synchronized clocks, so all honest parties use the same scheduled
times for view starts and scheduled actions. The
designated leader $\mathrm{Leader}(v)$ is public, and the leader schedule is
round robin.

At scheduled action times, messages delivered by that time are processed
before the scheduled action.

Values satisfy an
[external validity](https://decentralizedthoughts.github.io/2026-04-23-deconstructing-simplex/#single-shot-provable-consensus-with-external-validity)
predicate. Honest leaders propose only valid values, and honest parties vote
only for valid proposals. Each honest party has an externally valid input that
it may use as a fresh value.

The goals are:

**Liveness.** Every honest party eventually obtains a valid decision
certificate.

**Agreement.** All valid decision certificates have the same value.

**Validity.** If a decision certificate is valid, then its value is externally
valid.

## Certificates

Let

$$
Q=n-f=4f+1,\qquad C=n-3f=2f+1.
$$

$Q$ is the decision threshold. $C$ is the value certificate threshold. The
useful intersections are

$$
Q+C-n=f+1
\qquad\text{and}\qquad
Q+Q-n=3f+1.
$$

The view-$v$ messages are signed $\mathrm{Vote}(v,z)$ messages, where
$z$ is either an externally valid value or $\bot$.

The certificates are:

1. Decision: $\mathrm{DC}_v(x)$ is $Q$ signed $\mathrm{Vote}(v,x)$ messages for a
   non-$\bot$ value $x$. This is the decision certificate for $x$ in view $v$.
2. Value: $\mathrm{VC}_v(x)$ is $C$ signed $\mathrm{Vote}(v,x)$ messages for a
   non-$\bot$ value $x$. This is the value certificate for $x$ in view $v$.
3. Bottom: $\mathrm{BC}_v$ is $C$ signed $\mathrm{Vote}(v,\bot)$ messages.
4. No Commit: $\mathrm{NC}_v$ is $Q$ signed view-$v$ votes, with at most one vote per
   sender, such that no non-$\bot$ value appears at least $C$ times.

A skip certificate for view $v$ is either $\mathrm{BC}_v$ or
$\mathrm{NC}_v$.

Each honest party signs at most one vote in a view. Whenever an honest party
forms or receives a certificate, it broadcasts that certificate.

## Proposals

A proposal message in view $v$ is

$$
\langle\mathrm{Propose},v,x,w\rangle.
$$

It may also include certificates.

A valid proposal in view $v\geq 1$ is a proposal sent by
$\mathrm{Leader}(v)$ for which $x$ is externally valid, all included
certificates verify, and either $w=0$ or $0<w<v$.

The case $w=0$ is a sentinel meaning that the proposal is fresh; there is no
protocol view $0$.

If $0<w<v$, then the proposal includes $\mathrm{VC}_w(x)$ and a skip
certificate for every $w<y<v$.

If $w=0$, then $x$ is fresh, and the proposal includes a skip certificate for
every $0<y<v$.

At time $s_v$, an honest leader sends a valid proposal with maximum $w$ among
the valid proposals it can form from the certificates it has at that time. If
it can form no valid proposal, it sends no proposal. If several values have
certificates in the same maximal view, the leader may choose any one of them.

## Fast Simplex FVS

View $v$ starts at

$$
s_v=2v\Delta.
$$

```text
Fast Simplex FVS, view v:

1. Leader proposal:
      At time s_v, Leader(v) applies the leader side
      proposal rule.

2. Vote:
      Upon delivering the first valid view v proposal
      <Propose, v, x, w> at or before time s_v + Delta,
      if no vote has been signed in v:
          sign and broadcast <Vote, v, x>.

3. Bottom vote:
      At time s_v + Delta, if no vote has been signed in v:
          sign and broadcast <Vote, v, bot>.

4. Decide:
      Upon having DC_v(x):
          decide x.

5. View boundary:
      At time s_v + 2Delta:
          enter view v+1.
```

After leaving a view, a party signs no new vote for that view. Certificate
forwarding and decisions continue in the background. An honest party outputs
only its first decision.

## Claim 1: Decision Certificate Exclusion

If $\mathrm{DC}_v(x)$ exists, then no $\mathrm{VC}_v(y)$ exists for
$y\neq x$, and no skip certificate for view $v$ exists.

*Proof.* The decision certificate contains $Q=4f+1$ votes for $x$. At least
$Q-f=3f+1$ of these votes are honest, and honest parties sign only one vote
in a view. Hence at most $2f$ parties can vote for any other value or for
$\bot$, so no $\mathrm{VC}_v(y)$ with $y\neq x$ and no $\mathrm{BC}_v$ can
exist.

Now consider a possible $\mathrm{NC}_v$. It contains $Q$ votes, and therefore
intersects $\mathrm{DC}_v(x)$ in at least $Q+Q-n=3f+1$ parties. At most $f$
of these parties are Byzantine, so the intersection contains at least
$2f+1=C$ honest votes for $x$. Thus the $\mathrm{NC}_v$ vector would contain
$C$ votes for $x$, contradicting the definition of $\mathrm{NC}_v$.

## Claim 2: Agreement

All valid decision certificates have the same value.

*Proof.* Two decision certificates in the same view intersect in at least
$Q+Q-n=3f+1$ parties, including an honest party. Since an honest party signs
only one vote in a view, same-view decision certificates have the same value.

Now let $v$ be the earliest view with a valid decision certificate, and let
that certificate be $\mathrm{DC}_v(x)$. By Claim 1, a later valid proposal
cannot skip view $v$ and cannot use a conflicting value certificate from view
$v$.

If a later proposal uses a value certificate from a still later view $w>v$,
then that value certificate contains an honest vote in view $w$. That honest
vote was for a valid proposal in view $w$, and by induction that proposal has
value $x$. Thus every later value certificate, and therefore every later
decision certificate, has value $x$.

## Claim 3: Good Case Latency

In every view $v$ that starts after GST with an honest leader that has a valid
proposal at $s_v$, every honest party decides by time $s_v+2\delta$, where
$s_v=2v\Delta$ is the view start time.

*Proof.* The proposal reaches every honest party by $s_v+\delta$. All honest
parties vote for it immediately. Their $Q=n-f$ honest votes reach every
honest party by $s_v+2\delta$, giving every honest party
$\mathrm{DC}_v(x)$.

## Claim 4: Certificate Catch Up

This liveness statement is the reason the fixed view schedule can use view
length $2\Delta$.

For every view $w$, every honest party has either $\mathrm{VC}_w(x)$ for some
non-$\bot$ value $x$ or a skip certificate for view $w$ by time

$$
\max\{GST,s_w+\Delta\}+\delta .
$$

In particular, if view $w$ starts after GST, every honest party has such a
certificate by $s_w+2\Delta$, no later than the next view boundary.

*Proof.* By time $s_w+\Delta$, every honest party has signed exactly one
view-$w$ vote: either a vote for a valid proposal or a vote for $\bot$. After
GST, every honest party receives all of these honest votes within one delay.

If some non-$\bot$ value $x$ appears in at least $C$ honest votes, then every
honest party has $\mathrm{VC}_w(x)$. Otherwise, the $Q=n-f$ honest votes
themselves form an $\mathrm{NC}_w$: they contain no non-$\bot$ value at
threshold $C$.

## Combining It All

Fast Simplex FVS uses the view schedule $s_v=2v\Delta$ and satisfies
liveness, agreement, and validity for $n=5f+1$ in authenticated partial
synchrony.

Agreement is Claim 2. Validity follows because a decision certificate contains
an honest vote for an externally valid proposal.

For liveness, choose a later view $r$ whose leader is honest, whose scheduled
vote deadline is after GST, and whose previous views have caught up at every
honest party by time $s_r$. Claim 4 gives this catch up for views whose vote
deadline is after GST, and earlier views catch up after GST.

Therefore, at time $s_r$, the honest leader can form a valid proposal: it uses
the highest previous value certificate if one exists, with skip certificates
for all intervening views, and otherwise proposes a fresh value. Claim 3 gives
a decision by $s_r+2\delta$.

## Notes

- No commit certificate size in the normal case: The no commit certificate
  $\mathrm{NC}_v$ is naively linear size: it contains $Q=n-f$ signed votes and
  a check that no non-$\bot$ value appears $C=n-3f$ times. In many common
  executions this is not a problem. If the leader does not equivocate, then the
  view has only two vote values, the leader value $x$ and $\bot$, so ordinary
  multi signatures can compress $\mathrm{NC}_v$.

- No commit certificate size in the worst case: The linear certificate is only needed for
  the malicious equivocation case, when many different values may appear in the
  same view. The signed proposals can be used to slash the leader. In that
  case, an implementation can either send the linear certificate, or use a
  SNARK whose public statement says that the committed vector contains $Q$
  valid signed view-$v$ votes, with at most one vote per sender, and no
  non-$\bot$ value reaches threshold $C$.

- Getting $n=5f-1$: just as in the variable view schedule model, it is
  possible to get the
  [two round good case in $5f-1$](https://decentralizedthoughts.github.io/2025-08-06-5fminus1-simplex/)
  by refining the certificate definitions. The decision threshold becomes
  $Q=n-f=4f-1$. A value certificate for $x$ is either the equivocation case,
  with $2f$ votes for $x$ from parties other than the leader after ignoring the
  equivocating leader, or the no equivocation case, with $2f-1$ votes for $x$
  and $2f$ votes for $\bot$. A bottom certificate is $2f+1$ votes for
  $\bot$. The fixed view schedule is unchanged; the proof only has to replace
  Claim 1 with the corresponding exclusion argument for these two value
  certificate forms.

- Getting $2\Delta+\delta$ in the variable view schedule model: the
  [two round Simplex post](https://decentralizedthoughts.github.io/2025-07-18-two-round-Simplex/)
  uses an extra bottom vote step to avoid sending the large no commit
  certificate. Namely, upon receiving $n-f$ view-$k$ votes with no value
  certificate inside, a party sends $\mathrm{Vote}(k,\bot)$; the resulting
  $\bot$ certificate forms one delay later. This gives a worst case bad view of
  $2\Delta+2\delta$.

  To get $2\Delta+\delta$, define the same $\mathrm{NC}_k$ certificate used in
  this post: $n-f$ signed view-$k$ votes, with at most one vote per sender, and
  no value appearing $n-3f$ times. Then delete the extra bottom vote step and
  treat $\mathrm{NC}_k$ as another no commit certificate. The existing view
  change rule applies: after a party has sent a view-$k$ vote and receives
  $\mathrm{NC}_k$, it forwards $\mathrm{NC}_k$ and enters view $k+1$. Leaders
  may use $\mathrm{NC}_k$ exactly as they use a bottom certificate when
  proposing in later views. The price is that this no commit certificate is
  linear size, unless it is compressed with a SNARK.

- For the broader fixed-view-schedule and two-round Simplex context, see the [Simplex chapter](https://decentralizedthoughts.github.io/2026-05-25-chapter-simplex/).

Your thoughts/comments here.
