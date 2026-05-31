---
title: Simplex on a Fixed View Schedule
date: 2026-05-14 04:00:00 -05:00
tags:
- consensus
author: Ittai Abraham
---

This post gives a **fixed view schedule** version of
[Simplex](https://decentralizedthoughts.github.io/2025-11-15-simplex-from-benign/), called **Simplex FVS**, with the advantages of a fixed view schedule discussed
[here](https://decentralizedthoughts.github.io/2026-03-07-simultaneous-agreement/). 
For a map of the surrounding Simplex line, see the [Simplex chapter](https://decentralizedthoughts.github.io/2026-05-25-chapter-simplex/).

In the FVS design, the start and end times of each view are fixed in advance;
this requires synchronized clocks. We number protocol views starting at $1$,
and view $v$ starts at time $3v\Delta$. After a view ends, parties no longer
sign new messages for it, but certificates and decisions from that view may
still be forwarded and processed in the background. A two round version with
views of length $2\Delta$ is
[Fast Simplex FVS](https://decentralizedthoughts.github.io/2026-05-17-fast-simplex-fvs/).

Simplex FVS keeps the exact same safety mechanism: quorum thresholds, certificate
types, proposal rule, and agreement proof are unchanged. What changes is the
liveness argument: parties do not wait for a certificate before moving to the
next view. They advance on a fixed global schedule, and the key catch up claim
is that after GST, each old view eventually yields either a value certificate
or a skip certificate that later leaders can use.

In the language of [deconstructing Simplex](https://decentralizedthoughts.github.io/2026-04-23-deconstructing-simplex/), this keeps the same outer proposal rule and safety argument, as well as the same per-view certificate machinery. What changes is the liveness interface between them: a view no longer has to deliver a value or skip certificate before parties move on. Instead, certificate forwarding continues in the background, and after GST the catch up argument ensures that later leaders have the certificates they need.

## Model

There are $n\geq 3f+1$ parties, at most $f$
[Byzantine](https://decentralizedthoughts.github.io/2019-06-07-modeling-the-adversary/).
All protocol messages are signed. A certificate is a forwardable set of signed
messages.

The network model is
[partial synchrony](https://decentralizedthoughts.github.io/2019-06-01-2019-5-31-models/).
Before GST, message delay is unbounded. After GST, every message from one
honest party to another is delivered within $\delta\leq\Delta$ of the later of
GST and its send time.

We also assume synchronized clocks, so all honest parties use the same scheduled
times for view starts and scheduled actions.

As in all Simplex protocols, it runs in *views*. The designated leader $\mathrm{Leader}(v)$ is
public. The leader schedule is round robin.

At scheduled action times, messages delivered by that time are processed
before the scheduled action.

Each honest party has an
[externally valid](https://decentralizedthoughts.github.io/2026-04-23-deconstructing-simplex/#single-shot-provable-consensus-with-external-validity)
input that it may use as a fresh value. The goals are:

**Liveness.** Every honest party eventually obtains a valid decision certificate.

**Agreement.** All valid decision certificates have the same value.

**Validity.** If a decision certificate is valid, then its value is externally valid.

## Certificates

Let

$$
Q=n-f.
$$

For view $v$:

1. $\mathrm{VC}_v(x)$ is $Q$ signed $\mathrm{Vote}(v,x)$ messages.
2. $\mathrm{FC}_v(x)$ is $Q$ signed $\mathrm{Final}(v,x)$ messages. This is
   the decision certificate for $x$ in view $v$.
3. $\mathrm{SC}_v$ is $Q$ signed $\mathrm{Skip}(v)$ messages.

Each honest party signs at most one $\mathrm{Vote}$ message, at most one
$\mathrm{Final}$ message, and at most one $\mathrm{Skip}$ message in a view.
It may sign both $\mathrm{Vote}(v,x)$ and $\mathrm{Skip}(v)$. After signing
$\mathrm{Skip}(v)$, an honest party never signs $\mathrm{Final}(v,\cdot)$.
After signing $\mathrm{Final}(v,x)$, an honest party never signs
$\mathrm{Vote}(v,\cdot)$ or $\mathrm{Skip}(v)$.

A skip certificate may coexist with a value certificate. It cannot coexist
with a final certificate.

Whenever an honest party forms or receives a certificate, it broadcasts that
certificate.

## Proposals

A proposal message in view $v$ is

$$
\langle\mathrm{Propose},v,x,w\rangle.
$$

It may also include certificates.

A valid proposal in view $v\geq 1$ is a proposal sent by $\mathrm{Leader}(v)$ for
which $x$ is externally valid, all included certificates verify, and either
$w=0$ or $0<w<v$.

The case $w=0$ is a sentinel meaning that the proposal is fresh; there is no
protocol view $0$.

If $0<w<v$, then the proposal includes $\mathrm{VC}_w(x)$ and
$\mathrm{SC}_y$ for every $w<y<v$.

If $w=0$, then $x$ is fresh, and the proposal includes $\mathrm{SC}_y$ for
every $0<y<v$.

At time $s_v$, an honest leader sends a valid proposal with maximum $w$ among
the valid proposals it can form from the certificates it has at that time. If
it can form no valid proposal, it sends no proposal. This is the leader side
proposal rule.

## Simplex FVS

View $v$ starts at

$$
s_v=3v\Delta.
$$

```text
Fixed view schedule Simplex, view v:

1. Leader proposal:
      At time s_v, Leader(v) applies the leader side
      proposal rule.

2. Vote:
      Upon delivering the first valid view v proposal
      <Propose, v, x, w> at or before time s_v + Delta,
      if no Vote, Final, or Skip has been signed in v:
          sign and broadcast <Vote, v, x>.

3. Final:
      Upon having VC_v(x), if no Final or Skip has been
      signed in v:
          sign and broadcast <Final, v, x>.

4. Skip:
      At time s_v + 2Delta, if no VC_v(*) is known and no
      Final or Skip has been signed in v:
          sign and broadcast <Skip, v>.

5. Decide:
      Upon having FC_v(x):
          decide x.

6. View boundary:
      At time s_v + 3Delta:
          enter view v+1.
```

After leaving a view, a party signs no new $\mathrm{Vote}$, $\mathrm{Final}$,
or $\mathrm{Skip}$ messages for that view. Certificate forwarding and
decisions continue in the background. An honest party outputs only its first
decision.

## Claim 1: Agreement

All valid decision certificates have the same value.

*Proof.* This is exactly the agreement argument for
[Simplex](https://decentralizedthoughts.github.io/2025-11-15-simplex-from-benign/).
The fixed view schedule changes when parties move, not the signing rules or
proposal validity. The same quorum intersections give uniqueness of value and
final certificates within a view and rule out coexistence of skip and final
certificates; the usual earliest decision view induction then fixes the value
of every later valid proposal, value certificate, and decision certificate.

## Claim 2: Good Case Latency

In every view $v$ that starts after GST with an honest leader that has a valid
proposal at $s_v$, every honest party decides by time $s_v+3\delta$, where
$s_v=3v\Delta$ is the view start time.

*Proof.* This is exactly the good leader latency argument for
[Simplex](https://decentralizedthoughts.github.io/2025-11-15-simplex-from-benign/),
once the honest leader has a valid proposal at $s_v$. The proposal reaches
everyone by $s_v+\delta$, yielding $\mathrm{VC}_v(x)$ by $s_v+2\delta$ and
$\mathrm{FC}_v(x)$ by $s_v+3\delta$.

## Claim 3: Certificate Catch Up

This new liveness statement shows why replacing Simplex's event driven view
advancement with a fixed view schedule still works.

For every view $w$, every honest party has either $\mathrm{VC}_w(x)$ for some
$x$ or $\mathrm{SC}_w$ by time

$$
\max\{GST,s_w+2\Delta\}+\delta .
$$

In particular, if view $w$ starts after GST, every honest party has such a
certificate by $s_w+3\Delta$.

*Proof.* Any honest vote sent in view $w$ is sent by time $s_w+\Delta$.
At time $s_w+2\Delta$,
either some honest party has $\mathrm{VC}_w(x)$ and broadcasts it, or no
honest party has a value certificate and every honest party signs
$\mathrm{Skip}(w)$. In either case, the value certificate or the skip messages
reach every honest party within one delay after both GST and $s_w+2\Delta$.

## Combining It All

Simplex FVS uses the view schedule $s_v=3v\Delta$ and
satisfies liveness, agreement, and validity for $n\geq3f+1$ in authenticated
partial synchrony.

Agreement is Claim 1. Validity follows as in Simplex: a final certificate
contains an honest final signature, which follows an honest vote for an
externally valid proposal.

For liveness, choose a view $r\geq 1$ with an honest leader and
$s_r\geq GST+\delta$. For every real predecessor $1\leq y<r$, we have
$s_y+2\Delta\leq s_r-\Delta$, so Claim 3 gives the leader a value or skip
certificate for every previous view by time $s_r$. Therefore the leader can
form a valid proposal: it uses the highest previous value certificate if one
exists, with skip certificates for all intervening views, and otherwise
proposes a fresh value. Claim 2 then gives a decision.

*For the surrounding Simplex line and related background posts, see the [Simplex chapter](https://decentralizedthoughts.github.io/2026-05-25-chapter-simplex/).*

Your thoughts/comments [here](https://x.com/ittaia/status/2055245094014316941?s=20).
