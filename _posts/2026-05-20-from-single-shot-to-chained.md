---
title: From Single-Shot Simplex to Chained Simplex
date: 2026-05-20 09:00:00 +0300
tags:
- consensus
author: Ittai Abraham, Joachim Neu
---

In this post we construct **Chained Simplex** from
[single-shot Simplex](https://decentralizedthoughts.github.io/2025-06-18-simplex/).
The chained construction is a simple modification of the single-shot protocol
and applies to any Simplex variant with the same
inner certificate properties and outer proposal structure. See [here](https://decentralizedthoughts.github.io/2022-11-19-from-single-shot-to-smr/) for more generic constructions.

We will use the decomposition from
[deconstructing Simplex](https://decentralizedthoughts.github.io/2026-04-23-deconstructing-simplex/)
to make the construction explicit. That post separates Simplex into:

1. an inner protocol, which produces value certificates, decision
   certificates, and skip certificates per view; and
2. an outer protocol, which forms proposals and tells honest parties which
   proposals to vote for.

We keep the inner protocol unchanged and only slightly change the
outer protocol.

## The Inner Protocol

In view $v$, the inner protocol may produce:

1. $\mathrm{VC}_v(x)$, a value certificate for $x$.
2. $\mathrm{DC}_v(x)$, a decision certificate for $x$.
3. $\mathrm{SC}_v$, a skip certificate for view $v$.

We use the following properties of the inner protocol.

**Same View Agreement.** There are no two valid value certificates
$\mathrm{VC}_v(x)$ and $\mathrm{VC}_v(y)$ with $x\neq y$.

**Decision Implies Value.** A valid $\mathrm{DC}_v(x)$ implies a valid
$\mathrm{VC}_v(x)$.

**Skip Decision Exclusion.** There is no valid pair
$\mathrm{DC}_v(x),\mathrm{SC}_v$.

Every valid value certificate contains an honest vote for its value. Honest
parties vote only after the outer protocol accepts the proposal for that value.

Certificates are forwardable. After GST, if an honest party obtains a valid
value, decision, or skip certificate, then every honest party eventually
obtains it.

After GST, in each entered view, some honest party eventually obtains either a
valid value certificate or a valid skip certificate.

In an honest leader good case, if the leader has a valid proposal, the view
produces the corresponding decision certificate within the usual good case
latency.

## Single-Shot Simplex Outer Protocol

In single-shot Simplex, honest parties vote for a proposal in view $v$ in one
of two cases.

First, if the proposal repeats the value from a previous value certificate and
includes skip certificates for the intervening views:

```text
value:
    x
vote when:
    VC_w(x)
    SC_{w+1}, ..., SC_{v-1}
```

where $0<w<v$.

Second, if the proposal uses a fresh value and includes skip certificates for the
intervening views:

```text
value:
    x
vote when:
    x passes external validity
    SC_1, ..., SC_{v-1}
```

Thus, a proposal either repeats a previous value, or starts from a fresh
externally valid value.

## Chained Simplex Outer Protocol

Here is the whole change: instead of re-proposing a certified value, the
leader extends it by one valid block.

Values are now chains, so a value certificate represents a chain certificate.
A proposal for view $v$ chooses an earlier chain
certificate $\mathrm{VC}_w(C)$, proves that all intervening views between $w$ and $v$ were skipped,
and proposes one valid extension $C^+=C\circ B$:

```text
value:
    C^+ = C o B
vote when:
    VC_w(C)
    SC_{w+1}, ..., SC_{v-1}
    C -> valid C o B
```

where $0\leq w<v$.

For the first block, use the public genesis chain $\bot_{\mathsf{gen}}$ and
its public certificate $\mathrm{VC}&#95;0(\bot&#95;{\mathsf{gen}})$.

That is it. The certified chain is the prefix; the new block is checked against
the state reached by that prefix.

Write $C\preceq D$ when $C$ is a prefix of $D$. The chain represents a
[state machine](https://decentralizedthoughts.github.io/2019-10-15-consensus-for-state-machine-replication/)
execution. We assume an external application validity relation

$$
C \xrightarrow{\mathrm{valid}} C\circ B,
$$

meaning that block $B$ is valid relative to the state reached by $C$.

If view $v$ produces $\mathrm{DC}_v(C^+)$, then $C^+$ is decided. If it
produces only $\mathrm{VC}_v(C^+)$, then $C^+$ is not decided yet, but later
views may extend it. If view $v$ produces $\mathrm{SC}_v$, then no new chain is
decided in view $v$.

## Chained Simplex Properties

A chain $C$ is decided if there is a valid decision certificate
$\mathrm{DC}_v(C)$ for some view $v$.

The chain protocol has the following properties.

**Chain Agreement.** If $\mathrm{DC}_i(C)$ and $\mathrm{DC}_j(D)$ are valid,
then $C\preceq D$ or $D\preceq C$.

We only require prefix agreement for decided chains. Value certificates without
decisions need not become decided chains.

**Chain Validity.** If $\mathrm{VC}_v(C)$ is valid, then $C$ is valid from
genesis: each block is externally valid after its prefix. Therefore, the same
holds for every valid $\mathrm{DC}_v(C)$.

**Chain Growth.** After GST, if valid blocks remain available and honest
leaders occur infinitely often, the height of decided chains grows without
bound.

## Why It Works

**Agreement.** If $i=j$, then decision implies value and same view agreement
give $C=D$. So it remains to show that if $\mathrm{DC}_i(C)$ and
$\mathrm{VC}_j(D)$ are valid with $i<j$, then $C\preceq D$.

Since $\mathrm{VC}&#95;j(D)$ contains an honest vote, $D$ came from an accepted
chain proposal. Thus, $D=D^\prime\circ B$ for some predecessor certificate
$\mathrm{VC}&#95;w(D^\prime)$ and skips
$\mathrm{SC}&#95;{w+1},\ldots,\mathrm{SC}&#95;{j-1}$.

If $w=i$, then decision implies value and same view agreement give $C=D^\prime$,
so $C\preceq D$. If $w<i<j$, then the proposal included $\mathrm{SC}_i$,
contradicting $\mathrm{DC}_i(C)$ by skip decision exclusion. If $i<w$, repeat
the same argument with $\mathrm{VC}&#95;w(D^\prime)$ in place of $\mathrm{VC}_j(D)$. The
view number decreases, so this eventually proves $C\preceq D$.

Chain agreement follows because every decision certificate implies a value
certificate for the same chain.

**Validity.** We prove by induction on $v$ that every valid
$\mathrm{VC}_v(E)$ has an externally valid chain. The genesis certificate is
valid. For $v>0$, a value certificate contains an honest vote, so its proposal
was for $E=C\circ B$, used a valid predecessor $\mathrm{VC}_w(C)$ with
$w<v$, and checked $C \xrightarrow{\mathrm{valid}} C\circ B$. By induction,
$C$ is valid, so $E$ is valid. A decision certificate implies a value
certificate for the same chain.

**Growth.** Consider an honest leader in a post-GST view $v$ after it has
obtained, for every earlier view, either a value certificate or a skip
certificate. Let $w<v$ be the highest view for which it has a value certificate
$\mathrm{VC}_w(C)$. By the catch-up assumption, every view $y$ with $w<y<v$
has either a value certificate or a skip certificate. Since $w$ is the highest
view with a value certificate, all such views have skip certificates. If a
valid next block is available, the chained outer protocol lets the leader
propose $C\circ B$, and the good case gives a decision certificate for the
extended chain.

## Takeaway

Chained Simplex uses the same inner protocol as single-shot Simplex. The only
change is in the
[outer proposal rule](https://decentralizedthoughts.github.io/2026-04-23-deconstructing-simplex/):
each leader extends a certified chain by one valid block.

This is why we often use a single-shot presentation: it isolates the core
consensus mechanism, while chaining is just an outer-protocol change.


Your thoughts on [X](https://x.com/ittaia/status/2058196711483269149?s=20).
