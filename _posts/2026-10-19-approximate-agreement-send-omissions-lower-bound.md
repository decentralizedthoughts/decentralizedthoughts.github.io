---
title: "A Lower Bound for Approximate Agreement with Send Omissions"
date: 2026-10-19 09:00:00 +03:00
tags:
  - approximate-agreement
  - lowerbound
author: Ittai Abraham, Gilad Stern
chapters:
  - /2026-06-28-chapter-lower-bounds/
background:
  - /2022-06-07-approx-agreement-one/
continue_reading:
  - /2026-10-18-byzantine-approximate-agreement-grade-detect-average/
  - /2026-10-18-approximate-agreement-with-omissions/
---

In **approximate agreement**, parties start with numerical inputs in $[0,1]$. Every nonfaulty party must terminate with an output in the input range, and their outputs must differ by less than a given $\epsilon>0$.

Define the **output span** of an execution as the difference between the largest and smallest nonfaulty outputs. Approximate agreement requires this span to be less than $\epsilon$.

We present a modern version of [Fekete's lower bound][fekete] for approximate agreement with send omissions where faulty parties may omit outgoing messages but otherwise follow the protocol. The lower bound holds in a synchronous network even if each message is delayed by exactly $d$ (and $d$ is known), all parties start at exactly the same time and all clocks are perfectly synchronized. The lower bound deals with the time required for the protocol to reach a certain output span.


**Theorem.** Suppose $n>f+1$ and $f\geq\alpha n$, for a fixed constant $\alpha>0$. For every $1\leq k\leq f$, any approximate agreement protocol for inputs in $[0,1]$ that tolerates $f$ send-omission faulty parties and guarantees completion by time $kd$ has an execution with nonfaulty output span at least

$$
\frac1{(ck)^k},
$$

where $c$ depends only on $\alpha$. 

Thus, for any target output span $0<\epsilon\leq1$, guaranteeing output span less than $\epsilon$ by time $kd$, with $1\leq k\leq f$, requires

$$
k\log(ck)>\log\frac1\epsilon.
$$


Indeed this is asymptotically tight. For example, starting with inputs in $[0,1]$, the [GDA Byzantine approximate agreement protocol][faster] reaches output span below $1/n$ in $O(\log n/\log\log n)$ rounds for $n>3f$. When $n>f+1$ and $f=\Theta(n)$, even send omissions require $\Omega(d\log n/\log\log n)$ time to reach span below $1/n$.

Additional background can be found in the [Robust Midpoint](/2022-06-07-approx-agreement-one/) post. Additional upper bound posts: [for omission](/2026-10-18-approximate-agreement-with-omissions/) and [for Byzantine](/2026-10-17-approximate-agreement-complete-protocol/).


## The model

All parties start simultaneously at the known real time $0$ and have perfectly synchronized clocks $H_i(t)=t$. These facts and the delay bound $d$ are common knowledge. 

At most $f$ parties are *send omission* faulty. Any of their outgoing messages may be dropped, but they otherwise follow the protocol. In fact, in our lower bound, for each faulty party, we may drop selected messages in one simulated round and all of its messages thereafter. This is sometimes referred to as a crash failure in which there are no guarantees on message delivery in the round a party crashes.

Each party starts with a rational input in $[0,1]$. For a common parameter $0<\epsilon\leq1$, every nonfaulty party must terminate with an output, and the span of these outputs must be less than $\epsilon$.

Convex validity, whether defined using all inputs or only nonfaulty inputs, implies the **weak validity** needed for our lower bound: if all parties are nonfaulty and have the same input $v$, they must all output $v$. In this case, either input range is $\{v\}$.

## Grouping messages by sending time

For the lower bound, we choose executions in which every message is delivered after exactly $d$ time.

Group the original messages by sender, recipient, and sending interval:

$$
[0,d),\quad [d,2d),\quad\ldots,\quad[(k-1)d,kd).
$$

For each group, the simulation sends one message containing the original messages and their sending times.

**Claim 1.** If all messages are delivered in exactly $d$ time, a protocol that finishes by time $kd$ can be simulated in $k$ rounds, with the same nonfaulty outputs and at most $f$ faulty parties.

**Proof.** In round $r$, each party sends each recipient the simulated message for $[(r-1)d,rd)$.

The party can compute this message from earlier simulated messages: every original message arriving before $rd$ was sent before $(r-1)d$. The simulation also reproduces clock readings $H_i(t)=t$ and all local timer actions. It therefore need not receive this round's messages before sending its own.

Omitting a simulated message means omitting all the original messages it contains, so the same parties can be faulty. After $k$ rounds, each party can determine every original message received by time $kd$, including arrivals exactly at $kd$, and compute the same output.

From now on, messages and rounds refer to this simulation. A **world** specifies the inputs, faulty parties, and omitted messages throughout all $k$ rounds. All worlds use the same start time, clocks, and public timing parameters. Two worlds are **indistinguishable to a party through round $r$** if it has the same input and receives the same messages in the first $r$ rounds. Keep each party's random choices the same in every world. Indistinguishability through round $k$ gives identical timed incoming messages and therefore identical clock observations, timer actions, and outputs.

## A path of worlds from zero to one

We construct a path of $N+1$ worlds joined by $N$ edges, with these endpoints:

* **World $W_0$.** All parties are nonfaulty and have input $0$. By weak validity, all must output $0$.
* **World $W_N$.** All parties are nonfaulty and have input $1$. By weak validity, all must output $1$.

$$
W_0\overset{p_1}{\longleftrightarrow}W_1
\overset{p_2}{\longleftrightarrow}\cdots
\overset{p_N}{\longleftrightarrow}W_N.
$$

The edge labeled $p_j$ joins worlds that are indistinguishable to $p_j$ through round $k$, with $p_j$ nonfaulty in both.

**Claim 2.** If there is such a path of $N+1$ worlds, some world in it has output span at least $1/N$.

**Proof.** Let $y_j$ be $p_j$'s output, which is the same in $W_{j-1}$ and $W_j$. The endpoint worlds give $y_1=0$ and $y_N=1$. In each intermediate world $W_j$, both $y_j$ and $y_{j+1}$ are nonfaulty outputs. If every world's output span were at most $\epsilon$, then

$$
1=|y_N-y_1|
\leq\sum_{j=1}^{N-1}|y_{j+1}-y_j|
\leq(N-1)\epsilon
\leq N\epsilon.
$$

We will construct such a path with $N\leq(ck)^k$ edges, where $c$ depends only on $\alpha$. Claim 2 then gives a world with output span at least $1/(ck)^k$.

## Constructing the path

Fix $1\leq k\leq f$ and set $q=\lfloor f/k\rfloor$. We construct the path one round at a time such that after the step for round $r$, every world has at most $rq$ faulty parties, giving at most $kq\leq f$ faults. Partition the parties into sets $V_1,\ldots,V_m$, each of size at most $q$, where $m=\lceil n/q\rceil$.

We will construct the worlds iteratively. In iteration $r$ (starting with $r=0$), the worlds are going to be indistinguishable until round $r$, but not necessarily afterwards.

### Iteration $0$

We start with a path that is indistinguishable until round $0$. That is, before any party sends any message. If parties do not send any messages, then they have an indistinguishable view if their *inputs* are identical in neighboring worlds.

For $i=0,\ldots,m$, define **world $W_i$**:

* Parties in $V_1,\ldots,V_i$ have input $1$; all other parties have input $0$.
* All parties are nonfaulty.

This means that our starting path is this:

$$
W_0\longleftrightarrow W_1\longleftrightarrow\cdots\longleftrightarrow W_m.
$$

Note that in $W_0$, all parties have input $0$ and in $W_m$ they all have input $1$.

Looking at the parties' view before any message is sent, we can see that the only parties that notice any difference when moving from world $W_{i-1}$ to world $W_i$ are the parties in $V_i$. Every other party's input remains unchanged in these two worlds. This means we can choose any party not in $V_i$ to be the party with indistinguishable views until round $0$.

### Iteration $k>r\geq 1$

Assuming we have a path that is indistinguishable until round $r-1$ for some $k>r\geq 1$, we will construct a path that is indistinguishable until round $r$. This means we won't get the full theorem yet, we will still need to take one final step to get to round $k$. 

For $1\leq r<k$, replace each edge $W_{i-1}\longleftrightarrow W_i$ by

$$
W_{i,0}\longleftrightarrow W_{i,1}\longleftrightarrow\cdots
\longleftrightarrow W_{i,2m+3},
$$

where $W_{i,0}=W_{i-1}$ and $W_{i,2m+3}=W_i$. Since we're expanding the path from world $W_{i-1}$ to world $W_i$, we keep two indices: the first index, $i$, indicates which edge we're expanding, and the second index indicates how far we are along the expanded path.

For the edge we are expanding, choose a partition set $S$ such that the worlds have the same nonfaulty parties outside $S$, and these parties have identical views through round $r-1$. The initial construction gives this property for $r=1$, and Claim 3 preserves it for later iterations.

Our plan is to take the set $S$, whose parties might have **distinguishable** views (not indistinguishable!) by the end of round $r-1$, and make it faulty, changing its view from the one it had in one side of the edge, to the view it had in the other. At each step, all nonfaulty parties should have identical views through round $r$ except for parties in some set $V_j$. This means that in the next step we will also be able to choose a set $S$ with this property. Note that this is already the case in our round $0$ construction.

We gradually omit the round $r$ messages from $S$, one recipient set at a time. Once nobody receives them, we switch to the neighboring world’s inputs and history. We then restore the messages in reverse order.

In all of our new worlds, $W_{i,1},\ldots,W_{i,2m+2}$, the parties in $S$ are faulty, in addition to any other faulty parties that were made faulty in previous iterations. In addition, all messages by parties in $S$ are dropped after round $r$.

In the first half of the worlds, $W_{i,1},\ldots,W_{i,m+1}$ all parties have the same input and receive the same messages through round $r-1$ as they do in $W_{i-1}$ and in the second half, they have the same input and receive the same messages through round $r-1$ as in $W_{i}$. 


In world $W_{i,j}$ for $1\leq j \leq m+1$, messages sent by $S$ in round $r$ are delivered to parties in the set $V_j,\ldots,V_m$. In particular, this means that in world $W_{i,1}$ they are delivered to everybody, and in $W_{i,m+1}$ they are delivered to nobody. In this description, we use the convention that since our starting index is $m+1$, more than the number of sets, no messages are sent.
Continuing, in reverse this time, in world $W_{i,m+2+j}$ for $0\leq j\leq m$, messages sent by $S$ in round $r$ are delivered to $V_{m+1-j},\ldots,V_m$.

These rules are summarized in the table below:

| Worlds, in order | Same inputs as | Recipients of the round $r$ messages from $S$, in order |
| --- | --- | --- |
| $W_{i,1},\ldots,W_{i,m+1}$ | $W_{i-1}$ | All sets; $V_2,\ldots,V_m$; $V_3,\ldots,V_m$; $\ldots$; none |
| $W_{i,m+2},\ldots,W_{i,2m+2}$ | $W_i$ | None; $V_m$; $V_{m-1},V_m$; $\ldots$; all sets |


**Claim 3.** For every neighboring pair, there is a set $V_j$ such that the worlds have the same nonfaulty parties outside $V_j$. The worlds are indistinguishable to these nonfaulty parties until round $r$.

**Proof.** There are three kinds of edges:

* **$W_{i,0},W_{i,1}$.** Every party that is nonfaulty up until round $r-1$ and is not in $S$ is nonfaulty and has indistinguishable views until round $r$, because each of these parties receives the same round $r$ messages in both worlds.
* **$W_{i,j},W_{i,j+1}$, for $1\leq j\leq m$.** The faulty set is the same in both worlds: $S$ together with the parties made faulty in earlier iterations.  Only parties in $V_j$ can receive different round $r$ messages.
* **$W_{i,m+1},W_{i,m+2}$.** Every party outside $S$ has the same input, receives the same messages from outside $S$, and receives no messages from parties in $S$.

The second half is symmetric. Every world on this path has at most $rq$ faulty parties.

Note that in each world we only make one set $V_j$ faulty. Each iteration adds at most $q$ new faulty parties, so by round $r$ there are at most $rq$ faulty parties.

### The final iteration

Until now, we have maintained the following property: on each edge, the nonfaulty parties outside one partition set have identical views. After round $r$, each world has at most $rq$ faulty parties, and the partition set with distinguishable views contains at most $q$ more parties. This leaves at least $n-(r+1)q$ nonfaulty parties with identical views in both worlds. For $r<k$, this number is at least $n-kq\ge2$. For $r=k$, however, the bound need not be positive, so we cannot rely on the same argument.

In the final round, we can use a weaker property: each edge only needs **one** nonfaulty party with identical views in its two worlds. We no longer need to prepare the path for another iteration. We will use the two parties available before the final round to replace each edge with a path of three edges: one party will have identical views across the two outer edges, and the other will have identical views across the middle edge.

We will now take our construction until round $k-1$ and extend it one more round. Observe two neighboring worlds $W_{i-1},W_{i}$ and choose the partition set $V_j$ supplied for this edge by the preceding construction. Outside $V_j$, the worlds have the same nonfaulty parties, and these parties have identical views through round $k-1$. This follows from Claim 3, or from the initial construction when $k=1$.

In total up until now, at most $(k-1)q$ parties have been made faulty, and $|V_j|\leq q$, so there are at least $n-kq\geq 2$ parties that are nonfaulty and currently have indistinguishable views.
Choose two such parties, $p$ and $p'$.

We will now extend the path, into the worlds $W_{i,0},\ldots,W_{i,3}$. The two ends remain the same, $W_{i,0}=W_{i-1}$ and $W_{i,3}=W_i$. In the two middle worlds, we add $V_j$ to the set of faulty parties, and deliver their round $k$ messages only to $p$. 

We added at most $q$ new faulty parties, so the total is at most $qk\leq f$, within our fault budget. 

**Claim 4.** The worlds on each edge below are indistinguishable through round $k$ to the indicated party, which is nonfaulty in both:

$$
W_{i,0}\overset{p}{\longleftrightarrow}W_{i,1}
\overset{p'}{\longleftrightarrow}W_{i,2}
\overset{p}{\longleftrightarrow}W_{i,3}.
$$

**Proof.** On the edges $W_{i,0}\leftrightarrow W_{i,1}$ and $W_{i,2}\leftrightarrow W_{i,3}$ the worlds are indistinguishable to $p$ through round $k-1$, and $p$ receives the same messages in round $k$.

On the edge $W_{i,1}\leftrightarrow W_{i,2}$, the worlds are indistinguishable to $p'$ through round $k-1$. It receives identical messages from every nonfaulty sender outside $V_j$ or the other faulty parties. 

## Counting the path length

**Claim 5.** In some execution, the nonfaulty output span is at least $1/(3m+2)^k$ after $k$ rounds.

**Proof.** The initial path has $m$ edges. For each of the first $k-1$ rounds, we replace every edge by $2m+3$ edges. For round $k$, we replace each edge by three. Thus

$$
N\leq3m(2m+3)^{k-1}\leq(3m+2)^k.
$$

In our construction, we had at least one honest party with indistinguishable views in each pair of neighboring worlds and there are $N$ edges in total. Applying our previous claims, we get our result.

Note that each time we expanded an edge, we kept its endpoints and only added worlds in between. This means that our path still starts at the world where all parties are nonfaulty and have input $0$, and ends at the world where all parties are nonfaulty and have input $1$, as needed for Claim 2.

## Combining It All

Claim 5 gives

$$
\text{output span}\geq
\frac{1}{\left(3m+2\right)^k}.
$$

Recall that $m$ was defined to be $\lceil n/q\rceil$ and $q$ is defined to be $\lfloor f/k\rfloor$. Combining these facts, and the assumption that $f=\Theta(n)$, we get $m=\Theta(kn/f)=\Theta(k)$. Choosing some $c$ such that $3m+2\leq ck$, the previous statement shows that the output span is at least $1/(ck)^k$.

To guarantee span less than $\epsilon$ by time $kd$, we therefore need

$$
\epsilon>\frac1{(ck)^k}
\qquad \Longrightarrow\qquad
k\log(ck)>\log\frac1\epsilon.
$$


## Notes

* **Attribution.** [Fekete, Section 8][fekete] proves the corresponding lower bound for synchronous rounds with crashes. We construct the path one round at a time, with weaker constants, and use Claim 1 to also show that the bound holds when considering the time taken. The Byzantine asymptotic bound was stated earlier by [Dolev, Lynch, Pinter, Stark, and Weihl][dlpsw], in their [1985 preprint][dlpsw-preprint] and 1986 journal paper. Fekete's Section 7 proves the sharper Byzantine bound $L_k(f)/(n+f)^k$, where $L_k(f)$ is the largest product of $k$ nonnegative integers with sum at most $f$.
* **Crashes and sending order.** The same bound on output span after $k$ rounds holds when a party follows the protocol before its crash round, may omit any subset of its outgoing messages in that round, and sends nothing thereafter. Our construction already omits all later messages from each faulty party, so stopping it after that round leaves every nonfaulty party's view unchanged. This is Fekete's synchronous crash model. If the protocol chooses the sending order and a crash can interrupt only a prefix, the four-round protocol (TBD) reaches span below $1/n$ for sufficiently large $n$ when $n>2f$.
* **Crashes in elapsed time.** Repeated Average (TBD) reaches any target $\epsilon>0$ within $4d$, for every $n>f$. It sends many copies within one interval of length $d$; a crash can interrupt only one copy's broadcast. Omissions can discard selected copies throughout that interval. The distinction between round bounds and elapsed-time bounds is discussed by [Aguilera, Le Lann, and Toueg, Section 8][timed-consensus].
* **Exact agreement.** At $k=f$, Claim 5 is still positive. Exact agreement therefore cannot be guaranteed by time $fd$. This conclusion needs only $n>f+1$ and $f\geq1$.
* **Randomization.** As with [FLP][flp], the lower bound also holds for randomized protocols as a worst-case execution bound. It does not imply the same bound on expected running time.
* **Related proofs.** The [synchronous consensus][round-lb] and [early-stopping][early-stopping] lower bounds also change which recipients hear from a faulty sender. The [mobile-failure post][mobile-lb] studies how one additional failure changes the outcome. The clock-synchronization sequel (TBD) uses the path of worlds with endpoints shifted in real time instead of the all-zero and all-one inputs.

## Acknowledgments

We thank Jennifer Welch, Kartik Nayak, and Julian Loss for insightful comments.

Your thoughts/comments on [X](https://x.com/ittaia/status/2112206476819452060).

[faster]: https://decentralizedthoughts.github.io/2026-10-18-byzantine-approximate-agreement-grade-detect-average/
[fekete]: https://groups.csail.mit.edu/tds/papers/Fekete/DistComp90.pdf#page=16
[dlpsw]: https://groups.csail.mit.edu/tds/papers/Lynch/jacm86.pdf#page=18
[dlpsw-preprint]: https://www3.cs.stonybrook.edu/~stark/REPORTS/approx.pdf#page=27
[flp]: https://decentralizedthoughts.github.io/2019-12-15-asynchrony-uncommitted-lower-bound/
[timed-consensus]: https://www.rocq.inria.fr/novaltis/publications/DISC%202002.pdf#page=14
[round-lb]: https://decentralizedthoughts.github.io/2019-12-15-synchrony-uncommitted-lower-bound/
[early-stopping]: https://decentralizedthoughts.github.io/2024-01-28-early-stopping-lower-bounds/
[mobile-lb]: https://decentralizedthoughts.github.io/2024-03-07-mobile-is-FLP/
