---
title: Two Round Information-Theoretic Chained BFT at n=5f-1
date: 2026-07-12 04:00:00 -05:00
tags:
- consensus
- partial-synchrony
- information-theoretic
- fast-simplex
author: Ittai Abraham, Sourav Das, Yuval Efron, Jovan Komatovic, Alejandro Ranchal-Pedrosa, Gilad Stern
---

[Information-Theoretic Kuplex](https://decentralizedthoughts.github.io/2026-06-05-IT-Kuplex/)
gives a signature-free Simplex protocol in which quorums cannot be transferred
between parties. This post makes the earlier
[two round BFT protocol for $n=5f-1$](https://decentralizedthoughts.github.io/2025-08-06-5fminus1-simplex/)
signature-free in the same way. We use the
[Chained Simplex](https://decentralizedthoughts.github.io/2026-05-20-from-single-shot-to-chained/)
outer protocol: a leader extends a certified chain by one valid block. For a
map of the surrounding Simplex line, see the
[Simplex chapter](https://decentralizedthoughts.github.io/2026-05-25-chapter-simplex/).

We view this as a simple extension of IT-Kuplex. We would not be surprised if
other groups have independently obtained similar results.

The single-shot version also refutes a conjecture in
[[ANRZ21](https://arxiv.org/abs/2102.07240)]. In its conclusion, that work
conjectured that under partial synchrony two round Byzantine broadcast without
signatures requires $n\geq 5f+1$. The protocol below achieves $n=5f-1$.

The inner protocol uses the IT-Kuplex grade notation, but it has only grades 1
and 2. When deciding whether to propose or vote, a party can combine matching
grade-1 and grade-2 messages, counting each sender once. A party that leaves a
view with $n-f$ matching grade-2 messages for a chain $C$ before sending a
grade-1 message votes for $C$ rather than bottom. This can complete a decision
for $C$ while the parties continue building the chain. In the good case,
the votes that decide $C$ also let the next honest leader extend $C$, even
before entering the next view.

**Theorem.** For $n=5f-1$ and $f\ge 2$, the protocol below is a signature-free
chained BFT protocol with chain agreement, chain validity, good case block
latency $2\delta$, and worst case view latency $2\Delta+2\delta$. If valid
blocks remain available, the height of chains decided by all honest parties
grows without bound.

Here, "valid blocks remain available" means that an honest leader can construct
a valid one-block extension of any valid parent chain that it is allowed to
extend. The good case is an honest-leader proposal after GST when valid blocks
remain available and no honest party entered that view or a higher view, or
sent a message for any such view, before GST.

## Definitions and Quorums

There are $n$ parties, of which at most $f$ are Byzantine. We assume partial
synchrony and authenticated channels. Before GST, message delay is unbounded.
After GST, every message from one honest party to another is delivered within
$\delta\leq\Delta$ of the later of GST and its send time. Only finitely many
protocol events occur in finite time. The protocol uses local view timers.
Leaders follow a round robin schedule. Every quorum below consists of messages
received directly by the party using it.

$$
Q=n-f=4f-1,\qquad A=2f+1,\qquad H=f+1,\qquad M=2f.
$$

The messages in view $v$ are

1. $\langle\mathrm{Propose},v,C^+,w\rangle$;
2. Vote$(v,g,C)$ for a chain $C$ and $g\in\{1,2\}$; and
3. Bot$(v,g)$ for $g\in\{1,2\}$.

Every message threshold counts distinct senders.

From each sender in each view, a party retains only the first well-formed
grade-1 message it receives and ignores later grade-1 messages from that
sender. Every use of a grade-1 message below, including $\mathrm{Q1}$ and the
mixed counts, refers to the retained message.

An honest party sends at most one grade-1 message in a view: Vote$(v,1,C)$ for
one chain $C$, or Bot$(v,1)$. It sends each grade-2 message at most once, but
grade-2 messages are not exclusive: as in IT-Kuplex, it can send
Vote$(v,2,C)$ for several chains $C$ and can also send Bot$(v,2)$.

A grade-1 $Q$-set contains $Q$ retained grade-1 messages from distinct senders.
A non-leader $Q$-set contains $Q$ retained grade-1 messages from distinct
parties other than $\mathrm{Leader}(v)$. For either set $S$, let

$$
\mathrm{count}_S(C)=\#\{\mathrm{Vote}(v,1,C)\in S\}.
$$

Let $\mathrm{mix}_v(C)$ count distinct senders from which the party has
retained Vote$(v,1,C)$ or received Vote$(v,2,C)$, counting a sender only once
even if both messages were received. Define $\mathrm{mixB}_v$ in the same way
using retained Bot$(v,1)$ and received Bot$(v,2)$.

The grade-2 rules use five local tests:

1. $\mathrm{UniqueH}_v(C)$: some grade-1 $Q$-set has
   $\mathrm{count}_S(C)\ge H$ and $\mathrm{count}_S(D)<H$ for every $D\neq C$.
2. $\mathrm{MultipleH}_v$: some grade-1 $Q$-set has two chains whose counts
   are at least $H$.
3. $\mathrm{NoH}_v$: some grade-1 $Q$-set has no chain whose count reaches $H$.
4. $\mathrm{NonLeaderM}_v(C)$: some non-leader $Q$-set $N$ has
   $\mathrm{count}_N(C)\ge M$.
5. $\mathrm{NonLeaderNoM}_v$: some non-leader $Q$-set $N$ has
   $\mathrm{count}_N(C)<M$ for every chain $C$.

The protocol uses four quorums:

1. $\mathrm{Q1}_v(C)$ is $Q=n-f$ retained Vote$(v,1,C)$ messages.
2. $\mathrm{X2}_v(C)$ is $Q=n-f$ Vote$(v,2,C)$ messages;
   $\mathrm{X2}_v(\bot)$ is $Q$ Bot$(v,2)$ messages. A party in view $v$ uses
   either quorum to enter view $v+1$.
3. $\mathrm{L2}_v(C)$ is either $A=2f+1$ Vote$(v,2,C)$ messages or
   $\mathrm{mix}_v(C)\ge 3f+1$; $\mathrm{L2}_v(\bot)$ is either
   $A$ Bot$(v,2)$ messages or $\mathrm{mixB}_v\ge 3f+1$. An honest leader uses
   $\mathrm{L2}$ to choose a proposal.
4. $\mathrm{R2}_v(C)$ is either $H=f+1$ Vote$(v,2,C)$ messages or
   $\mathrm{mix}_v(C)\ge 2f+1$; $\mathrm{R2}_v(\bot)$ is either
   $H$ Bot$(v,2)$ messages or $\mathrm{mixB}_v\ge 2f+1$. A recipient uses
   $\mathrm{R2}$ to validate a proposal.

Parties start in view $1$ and start $T_1$. Once started, $T_v$ measures the
time since the party entered view $v$. Let $G$ be the public genesis chain. In
a proposal $\langle\mathrm{Propose},v,C^+,w\rangle$, $C^+=C\circ B$ must be a
valid one-block extension of $C$. When $w=0$, $C=G$; when $w>0$, view $w$
supplies $C$. Write $C\preceq D$ when $C$ is a prefix of $D$.

For $Z\in\{\mathrm{L2},\mathrm{R2}\}$, a party has $Z$ for
$(v,C^+,w)$ when

1. $0\leq w<v$;
2. $Z_y(\bot)$ for every $w<y<v$; and
3. either $w=0$ and $C=G$, or $w>0$ and $Z_w(C)$.

When $(v,C^+,w)$ is clear from context, we simply say L2 or R2.

Both checks may hold before the party enters view $v$, and neither starts its
timer. Only the last protocol rule changes a party's current view.

## Protocol

A party continues applying the protocol after deciding a chain or leaving a
view.

```text
5f-1 two round IT protocol with view v and Leader(v):

1. When Leader(v) has L2 for at least one (v,C^+,w),
   if it has not proposed in v:
       Choose any such (C^+,w) and send <Propose,v,C^+,w>

2. Upon having a valid <Propose,v,C^+,w> from Leader(v)
   and R2 for (v,C^+,w),
   if no Vote(v,1,*) or Bot(v,1) has been sent:
       Send Vote(v,1,C^+)

3. At T_v = 2Δ, if no Vote(v,1,*) or Bot(v,1) has been sent:
       Send Bot(v,1)

4. Upon Q1_v(C):
       Decide C

5. Whenever one of these conditions holds:
       // C alone reaches f+1 votes in some Q-set,
       // or C reaches 2f votes in a non-leader Q-set
       UniqueH_v(C), or NonLeaderM_v(C):
           Send Vote(v,2,C)
       // some Q-set has no chain with f+1 votes,
       // or two chains do and some non-leader Q-set has none with 2f
       NoH_v, or (MultipleH_v and NonLeaderNoM_v):
           Send Bot(v,2)

6. Upon f+1 identical grade-2 messages:
       Send that grade-2 message

7. Whenever view = v and either X2_v(C) for some chain C
   or X2_v(⊥):
       If no Vote(v,1,*) or Bot(v,1) has been sent:
           If X2_v(C) for some chain C:
               Send Vote(v,1,C) for any such C
           Else:
               Send Bot(v,1)
       Set view = v+1 and start T_{v+1}
```

Rule 1 lets the leader choose any pair for which it has L2, but sends only one
proposal. The proposal extends the parent chain supported by L2 by one valid
block. Claim 3 handles any such parent chain, Claims 1 and 2 use the
one-proposal condition, and Claim 6 shows that L2 at the leader gives every
recipient R2 within one message delay. Rule 1 needs no view or timer condition
because rule 2 determines whether a party can vote.

In rule 2, R2 is the safety check in Claim 3 and the recipient threshold in
Claim 6. The grade-1 guard ensures that an honest party sends only one grade-1
message in a view, which is used in Claims 2 and 3. It also rejects a proposal
for a view the party has left, because rule 7 sends a grade-1 message before
changing views. No timer condition is needed: rule 3 sends bottom at the
deadline only if the party has not sent a grade-1 message.

Rule 3 supplies the missing grade-1 messages in Claims 5 and 7; Claim 6 shows
that it does not send bottom during the good case. Rule 4 is exactly the
decision condition used in Claims 2, 3, and 6. Continuing after deciding is
needed in Claims 4 and 7. Continuing the decision and grade-2 rules for an old
view is used in Claims 4 and 5, and lets a rule 7 vote complete a late decision
quorum.

Rule 5 creates grade-2 messages. Its two branches give the exclusion in Claim 2
and the common grade-2 message in Claims 5 and 7.
$\mathrm{NonLeaderM}_v(C)$ needs no separate $\mathrm{MultipleH}_v$ check: its
$Q$-set either has $C$ as the only chain with at least $H$ votes, in which case
$\mathrm{UniqueH}_v(C)$ holds, or has another chain with at least $H$ votes,
in which case $\mathrm{MultipleH}_v$ holds. Rule 6 propagates grade-2 messages,
which gives Claim 4 and prevents a conflicting relay from being the first
honest conflicting grade-2 message in Claim 2. The at-most-once condition
prevents repeated rule 5 or rule 6 triggers from resending the same message;
allowing different grade-2 messages is used in Claim 5.

Rule 7 changes views one at a time: it applies only when the party is in view
$v$, and it changes the view to $v+1$. Claims 4, 6, and 7 use this sequential
change. Before changing views, the grade-1 guard checks whether the party has
already sent a grade-1 message. The chain branch is used in Claims 1 and 6;
Claim 2 shows that its choice cannot conflict with a decision, and the bottom
branch is used in Claim 5. Starting $T_{v+1}$ supplies the deadlines in Claims
5--7. An $\mathrm{X2}$ quorum traces to a grade-1 $Q$-set, so at most $f$
parties still have not sent a grade-1 message when they take the chain branch.
Their votes can complete $\mathrm{Q1}$ in the view being left.

## Why the Protocol Works

### Claim 1: Chain Validity

Every $\mathrm{Q1}_v(C)$, $\mathrm{R2}_v(C)$, $\mathrm{L2}_v(C)$, or
$\mathrm{X2}_v(C)$ can be traced back to an honest Vote$(v,1,C)$ sent under
rule 2. Every such chain is valid from genesis.

**Proof.** Each listed quorum contains an honest matching message: a retained
grade-1 message or a grade-2 message. An honest grade-2 vote is sent under rule
5 only after more than $f$ retained grade-1 votes for $C$, or under rule 6 only
after $H=f+1$ earlier grade-2 votes. An honest grade-1 vote is either sent under
rule 2 or follows an earlier $\mathrm{X2}_v(C)$ under rule 7. Tracing earlier
messages must therefore end at an honest Vote$(v,1,C)$ sent under rule 2.

Now induct on the view of that rule 2 vote. Its proposal has
$C=C'\circ B$, where $B$ is valid after $C'$. If $w=0$, then $C'=G$. If
$w>0$, the proposal's R2 includes $\mathrm{R2}_w(C')$, which traces to an
honest rule 2 vote for $C'$ in the earlier view $w$. By induction, $C'$ is
valid from genesis, and therefore so is $C$.

### Claim 2: Safety in a View

If $\mathrm{Q1}_v(C)$ exists, no conflicting $\mathrm{Q1}$ exists, and no
$\mathrm{R2}$, $\mathrm{L2}$, or $\mathrm{X2}$ exists for another chain or
bottom in view $v$.

**Proof.** Two decision quorums intersect in $2Q-n=n-2f>f$ parties, including
an honest party, so they cannot be for different chains. Suppose
$\mathrm{Q1}_v(C)$ exists. It contains at least $n-2f=3f-1$ honest votes for
$C$. Every honest sender sends one grade-1 message, so its vote is retained by
every party that receives it. Any retained grade-1 $Q$-set omits at most $f$
parties, so it contains at least

$$
n-3f=2f-1\ge H
$$

honest votes for $C$. Therefore a $Q$-set with no chain appearing $H$ times
cannot exist, and if exactly one chain appears $H$ times, that chain is $C$.

If a $Q$-set contains two chains that each appear at least $H=f+1$ times,
Claim 1 traces an honest vote for each chain to a proposal from the leader. The
leader therefore sent different proposals and is Byzantine. All honest parties
that voted for $C$ are then not the leader. A non-leader $Q$-set omits at most
$f-1$ parties other than the leader, so it contains at least

$$
(n-2f)-(f-1)=2f=M
$$

honest votes for $C$. A different chain has at most $f$ honest non-leader votes
and $f-1$ Byzantine non-leader votes, for at most $2f-1<M$ votes. Hence no
honest party sends Vote$(v,2,D)$ for $D\neq C$ or Bot$(v,2)$ under rule 5.

A conflicting grade-2 message cannot begin under rule 6: the first honest
relayer would need $H=f+1$ earlier senders, including an honest sender. Thus no
conflicting grade-2 quorum exists.

It remains to exclude the mixed quorums. At most $f$ honest parties sent a
grade-1 vote for any $D\neq C$, and at most $f$ honest parties sent a grade-1
bottom message. Including all $f$ Byzantine parties therefore gives

$$
\mathrm{mix}_v(D)\leq 2f<2f+1
\qquad\text{and}\qquad
\mathrm{mixB}_v\leq 2f<2f+1.
$$

Thus neither mixed $\mathrm{R2}$ nor mixed $\mathrm{L2}$ exists. Together with
the grade-2 argument, this proves the claim.

### Claim 3: Chain Agreement

If honest parties decide chains $C$ and $D$, then $C\preceq D$ or
$D\preceq C$.

**Proof.** Same-view agreement is Claim 2. Suppose $\mathrm{Q1}_k(C)$ exists.
We prove by induction on $r>k$ that every honest rule 2 vote in view $r$ is for
a chain extending $C$. Such a vote follows a proposal $D=E\circ B$ with parent
view $w<r$. If $w<k$, its R2 requires $\mathrm{R2}_k(\bot)$, contradicting
Claim 2. If $w=k$, its R2 requires $\mathrm{R2}_k(E)$, so Claim 2 gives $E=C$.
If $k<w<r$, Claim 1 traces $\mathrm{R2}_w(E)$ to an honest rule 2 vote for $E$
in view $w$; by induction, $C\preceq E$. In the last two cases,
$C\preceq D$.

Any later decision quorum for $D$ contains an honest grade-1 vote for $D$,
which Claim 1 traces to a rule 2 vote for $D$ in that view. Hence an earlier
decided chain is a prefix of every later decided chain.

### Claim 4: Totality

If an honest party has $\mathrm{X2}_v(C)$ or $\mathrm{X2}_v(\bot)$, every
honest party eventually has its own corresponding quorum.

**Proof.** The quorum contains at least $Q-f=n-2f\geq H$ honest senders. Every
honest party eventually receives those messages. If it has not already sent
the same grade-2 message, rule 6 makes it do so. It then receives $n-f$
matching grade-2 messages from honest parties and has its own quorum.

Sequential view changes also give catch up. If an honest party enters view
$v$, then for every $1\leq y<v$ it changed from view $y$ to view $y+1$ using
some $\mathrm{X2}_y$ quorum under rule 7. The first part of this claim gives
each of those quorums to every honest party. Whenever another honest party is
in view $y$, its stored $\mathrm{X2}_y$ quorum enables rule 7. Induction on
$y$ brings every honest party to view $v$ or a higher view.

### Claim 5: Worst Case View Latency Is $2\Delta+2\delta$

Once all honest parties have entered a view $v$ and the last entrance occurs
after GST, the view produces $n-f$ matching grade-2 messages within
$2\Delta+2\delta$ of that last entrance.

**Proof.** Let $t_{\mathrm{last}}$ be the last honest entrance into view $v$.
By $t_{\mathrm{last}}+2\Delta$, every honest party has sent
Vote$(v,1,\cdot)$ or Bot$(v,1)$; a party that leaves earlier sends a grade-1
message under rule 7. By $t_{\mathrm{last}}+2\Delta+\delta$, every honest party
has all honest grade-1 messages. For the proof, fix any $Q=n-f$ honest senders
and let $S_v$ contain their grade-1 messages. Each honest sender sends only one
grade-1 message, so every honest party retains all of $S_v$ by this time. The
set enables the same branch of rule 5 at every honest party:

1. If no chain appears $H$ times in $S_v$, every honest party sends Bot$(v,2)$.
2. If exactly one chain $C$ appears at least $H$ times, every honest party sends
   Vote$(v,2,C)$.
3. If at least two chains appear $H$ times, Claim 1 traces an honest vote for
   each chain to a proposal from the leader. The leader is therefore Byzantine,
   so $S_v$ is a non-leader $Q$-set. If some $C$ appears at least $M$ times,
   every honest party sends Vote$(v,2,C)$; such a $C$ is unique because
   $2M=4f>n-f$. If no chain appears $M$ times, every honest party sends
   Bot$(v,2)$.

Thus all honest parties send the same grade-2 message by
$t_{\mathrm{last}}+2\Delta+\delta$ and receive $n-f$ matching grade-2 messages
by $t_{\mathrm{last}}+2\Delta+2\delta$.

### Computing Rule 5

**Claim.** A party stores at most $n$ grade-1 messages per view. From these
retained messages, it can maintain all rule 5 triggers in expected $O(n)$ total
time, or deterministic $O(n\log n)$ total time, using $O(n)$ space.

**Proof.** Let $a(C)$ count retained Vote$(v,1,C)$ messages and let $b$ count
retained Bot$(v,1)$ messages. Let $a^-(C)$ and $b^-$ be the corresponding
counts after excluding the leader, and set

$$
r=b+\sum_C a(C),
\qquad
r^-=b^-+\sum_C a^-(C).
$$

Because each sender has one retained grade-1 message, the five tests are

$$
\mathrm{NoH}_v
\iff
b+\sum_C\min\{a(C),H-1\}\ge Q,
$$

$$
\mathrm{UniqueH}_v(C)
\iff
a(C)\ge H
\quad\text{and}\quad
b+a(C)+\sum_{D\ne C}\min\{a(D),H-1\}\ge Q,
$$

$$
\mathrm{MultipleH}_v
\iff
r\ge Q
\quad\text{and at least two chains have count at least }H,
$$

$$
\mathrm{NonLeaderM}_v(C)
\iff
r^-\ge Q
\quad\text{and}\quad
a^-(C)\ge M,
$$

and

$$
\mathrm{NonLeaderNoM}_v
\iff
b^-+\sum_C\min\{a^-(C),M-1\}\ge Q.
$$

For example, the first capped sum is the largest number of retained messages
that can be placed in a $Q$-set while keeping every chain below $H$. The other
formulas follow in the same way; the $\mathrm{MultipleH}$ formula also uses
$2H\leq Q$, which holds for $f\geq2$.

Each retained message updates one count and the two capped sums. At most
$\lfloor n/H\rfloor\leq4$ chains can reach $H$, so every candidate test can be
updated in constant additional work. A hash table gives expected $O(n)$ total
time, while a balanced map gives deterministic $O(n\log n)$ total time. The
retained messages and the count map use $O(n)$ space. A later grade-1 message
from the same sender is discarded after one sender-table lookup.

### Claim 6: Good Case Block Latency Is $2\delta$

Suppose no honest party enters view $v$ or a higher view, or sends a message for
any such view, before GST, and valid blocks remain available. If an honest
leader sends $\langle\mathrm{Propose},v,D,w\rangle$ under rule 1 at time
$t_L\geq\mathrm{GST}$, then all honest parties decide $D$, and hence its new
block, by $t_L+2\delta$.

**Proof.** Each pure $\mathrm{L2}$ quorum used by the leader contains
$A-f=H$ honest senders, while each mixed $\mathrm{L2}$ quorum contains
$(3f+1)-f=2f+1$ honest senders. The honest messages in either quorum reach every
honest party within $\delta$; honest grade-1 messages are retained by every
recipient. Hence every honest party has R2 for $(v,D,w)$ and the proposal by
$t_L+\delta$. A party below view $v$ can vote before entering it; voting does
not enter view $v$ or start its timer.

If no honest party enters view $v$ before receiving the proposal and R2, no
timer can expire before the party votes. Otherwise, let
$\tau\geq\mathrm{GST}$ be the first honest entrance. For every $1\leq y<v$,
the first entrant changed from view $y$ to view $y+1$ using an
$\mathrm{X2}_y$ quorum. Let $w'$ be the highest such view in which it has a
chain quorum $\mathrm{X2}_{w'}(C)$, or let $w'=0$ if there is none. It has
$\mathrm{X2}_y(\bot)$ for every $w'<y<v$. Each of these quorums contains at
least $Q-f=n-2f\ge A$ honest grade-2 messages. By $\tau+\delta$, the honest
leader therefore has L2 for a valid extension of $C$ when $w'>0$, or a valid
extension of $G$ when $w'=0$. Rule 1 sends its only proposal as soon as it has
L2 for any such extension, so $t_L\leq\tau+\delta$. The first entrant receives
the proposal and R2 by

$$
t_L+\delta\leq\tau+2\delta\leq\tau+2\Delta.
$$

The first entrant therefore votes under rule 2 by its deadline, and every later
entrant has a later deadline. Since rule 7 changes views one at a time, a party
can move above view $v$ only after entering it and obtaining an
$\mathrm{X2}_v$ quorum.

No honest party sends a bottom message in view $v$ before all honest parties
vote. Rule 3 cannot do so because every entered party receives the proposal and
R2 by its deadline. The first honest Bot$(v,2)$ cannot be sent under rule 6,
because it would require an earlier honest sender. Nor can it be sent under
rule 5: every honest grade-1 message in its $Q$-set is Vote$(v,1,D)$. Rule 2
votes for the honest leader's only proposal; a chain vote under rule 7 is also
for $D$ by Claim 1; and a bottom vote under rule 7 would already require an
earlier honest Bot$(v,2)$. The $Q$-set therefore contains at least
$Q-f=n-2f$ votes for $D$, while every other chain has at most $f$ votes. Neither
bottom condition in rule 5 holds. Thus $\mathrm{X2}_v(\bot)$ cannot form.

Because the honest leader sent only the proposal for $D$, Claim 1 also implies
that every chain $\mathrm{X2}_v$ quorum is for $D$. Consequently, by
$t_L+\delta$ every honest party has sent Vote$(v,1,D)$: a party that already
changed from view $v$ sent it under rule 7, and every other party sends it under
rule 2. All honest parties receive $n-f$ honest grade-1 votes by
$t_L+2\delta$ and decide $D$ under rule 4. The same messages give every honest
party $\mathrm{mix}_v(D)\geq Q\geq3f+1$, and hence
$\mathrm{L2}_v(D)$. If the next leader is honest and has a valid block, rule 1
lets it propose an extension of $D$ by $t_L+2\delta$, even before entering view
$v+1$.

### Claim 7: Chain Growth

If valid blocks remain available, the height of chains decided by all honest
parties grows without bound.

**Proof.** First, honest view numbers are unbounded. Otherwise, let $u$ be the
largest view entered by an honest party. Claim 4 brings every honest party into
$u$. Rule 3 makes every honest party that has not sent a grade-1 message in $u$
send bottom. After GST, all honest grade-1 messages are delivered. The same
three cases used in Claim 5 then give every honest party an $\mathrm{X2}_u$
quorum, and rule 7 moves it to $u+1$, a contradiction.

Choose views above every view that an honest party entered or sent a message
for before GST. Sequential unbounded view changes and round-robin leaders give
infinitely many such views with honest leaders. In each one, the first
entrant's earlier $\mathrm{X2}$ quorums give the leader L2 for a valid
one-block extension within $\delta$. Claim 6 makes every honest party decide
that extension, and the parties continue the protocol. By Claim 3, each later
decided chain extends every earlier one. Each successful honest-leader view
adds a block, so decided chain height grows without bound.

## Notes

- When $n\geq 5f+1$, any decision quorum contains at least
  $n-2f\geq 3f+1$ honest grade-1 senders. Once those messages arrive, every
  honest party has mixed $\mathrm{L2}$, even if the leader is Byzantine. This
  quorum implication does not require synchrony. Synchrony is needed only for
  timing: after GST, these honest messages reach every honest party within one
  message delay.
