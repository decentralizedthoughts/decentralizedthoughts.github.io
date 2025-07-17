---
title: An Analysis of Latency and Block Capacity in Nakamoto Consensus
date: 2025-07-14 00:00:00 -04:00
published: false
tags:
- blockchain
- consensus
- game theory
- latency
author: Michele Fabi
---

> While research is now focusing on application–layer topics—MEV extraction, roll‑up economics, danksharding—several questions on **Layer‑1 fundamentals** remain open.  This post provides a game‑theoretical analysis of one such gap: **the impact of block propagation latency on the supply of block capacity**, based on Fabi’s paper “Latency Trade-offs in Blockchain Capacity Management” (2025).  

> The framework outlined here is most relevant when target block times are in the order of seconds or milliseconds, making propagation delays quantitatively meaningful.


## Setting the Stage

Ren’s work on the **Security Proof for Nakamoto Consensus** ([2019 blog post here](https://decentralizedthoughts.github.io/2019-11-29-Analysis-Nakamoto/)) introduces a Poisson-process model for block arrivals and a synchronous network with bounded delay Δ.  

Building directly on this setting, we **add a micro-foundation**: miners now **choose the block capacity k** strategically. All the original assumptions remain identical, except that blocks now face a (fixed) propagation delay that scales linearly with block size (Δ k). 

The timeline below illustrates how honest blocks that are mined too close in time (< Δk) may *fork* or *tailgate* one another.

<p align="center">
  <img src="uploads/fork-probability.png" width="60%">
   <figcaption><em> Poisson arrivals and tailgated blocks under a bounded network delay (adapted from Ren 2019).</em></figcaption>
</p>

### Notation Table


| Symbol | Meaning |
|--------|---------|
| $Δ$  | Propagation delay per kB |
| $μ$  | Block production rate |
| $α$  | Transaction‑data inflow |
| $τ$  | Fee per kB |
| $π$  | Coinbase reward (fixed) |
| $k$  | Block capacity |
| $λ$  | Growth rate of the honest chain |
| $ρ$  | System load $=α/λk$ |
| $A c$ | Adversary cost per second |


## 1. Latency and Strategic Block Capacity

In each mining round (starting when a new block is added to the honest chain), miner $m$ selects a block capacity $k_m \in \mathbb{R}_{+}$ for the next proposed block.  
We make the following assumptions on the two opposing forces that shape this choice:

* **Fee revenue.** Transaction fees are earned at a marginal rate $\tau$ per kB of data, so expected gross revenue increases linearly with block size: $\tau k_m$.
* **Latency risk.** Block propagation time increases linearly in size, $\Delta k_m$; a larger block takes longer to reach the network, raising the chance that it is overtaken and orphaned by a faster competitor.

Importantly, the probability that miner $m$’s block is accepted depends not only on its own capacity choice but also on those chosen by all other miners. Let $\mathbf{k}_{-m} = (k_{1}, \ldots, k_{m-1}, k_{m+1}, \ldots, k_{M})$ denote the vector of competing capacities. The win probability is given by

$$
P_m(k_m; \mathbf{k}_{-m}) = \Pr\left[ T_m + \Delta k_m < \min_{j \neq m} \left\{ T_j + \Delta k_j \right\} \right],
$$

where $T_j \sim \text{Exp}(\mu/M)$ are independent exponential random variables representing Poisson block arrival times, and $\mu$ is the aggregate block production rate.

The expected payoff for miner $m$ is

$$
R_m(k_m; \mathbf{k}_{-m}) = P_m(k_m; \mathbf{k}_{-m}) \cdot (\pi + \tau k_m),
$$

with $\pi$ the fixed coinbase reward. A miner's best response to the capacity profile of others is

$$
k_m^{\star} = \arg\max_{k_m \geq 0} \; R_m(k_m; \mathbf{k}_{-m})
$$

This interdependence makes the capacity choice a fully strategic decision: each miner’s optimal block size depends on beliefs about the sizes chosen by others. 

## 2. Equilibrium Block Capacity

Each miner’s chosen capacity cannot exceed the current mempool size $Q$ nor fall below zero.  When these bounds are not binding, the block capacity that arises in the unique symmetric Nash equilibrium of the game is   

$$
k_m^{\mathrm{NE}}(\pi,\tau,\mu)=\frac{\mu_{-m}^{-1}}{\Delta}-\frac{\pi}{\tau}.
$$

Here  

$$
\mu_{-m}\;=\;\mu\,\frac{M-1}{M}
$$

is the aggregate block‑production rate of the *other* miners (assuming homogeneous hash rates).  The term $\mu_{-m}^{-1}/\Delta$ captures the ratio of their expected inter‑block time to the per‑unit propagation delay, while $\pi/τ$ expresses the relative weight of the size‑independent coinbase reward.

We can see that:
* Small Δ relative to $\mu_{-m}^{-1}$ ⇒ larger blocks.  
* Large $\pi/\tau$ ⇒ smaller blocks.  
* As $M\to\infty$, $\mu_{-m}\to\mu$.

The effects of these ratios on the equilibrium block size are intuitive: if the transmission delay is short relative to the block production time, then the increase in forking risk caused by recording more transactions becomes less of a concern, thus miners increase block capacity.

On the other hand, since fees rise from recording more transactions but the coinbase does not, a larger coinbase lowers miners’ incentive to add transactions. Extra transactions prolong propagation and raise orphan risk, so a higher coinbase shifts the cost‑benefit cutoff to a lower equilibrium capacity.

When the mining population is large ($M\to\infty$), $\mu_{-m}$ converges to aggregate block‑production rate $\mu$.  

## 3. Blockchain and Mempool Dynamics


To connect miner incentives with user latency we model the mempool as a **continuous bulk‑service queue**: transactions flow in at rate α, while blocks of endogenously chosen size *k* clear data in batches. This extends the discrete M/M[K]/1 framework of Huberman‑Leshno‑Moallemi (2019) and the binary‑block M/M/1 queues of Hinzen et al. (2019) and Easley et al. (2019).  Similar stochastic processes are also found in inventory theory and in neuroscience to model integrate-and-fire neurons.

The mempool size $Q_t$ follows  
$$
d Q_t=\alpha\,d t-\min\{k,Q_t\}\,d B_t,\qquad 
B_t\sim\text{Poisson}\!\bigl(\lambda\bigr),
\tag{SDE}
$$
where  
$$
\lambda=\mu\,e^{-\mu\Delta k(\pi,\tau,\mu)}
$$
is the **growth of the honest chain**—the raw discovery rate μ multiplied by the probability that a discovered block is not orphaned.

<p align="center">
  <img src="uploads/process.png" width="80%">
   <figcaption><em> Evolution of the sample path of the mempool size process.</em></figcaption>
</p>


By redefining the above process in terms of normalized  backlog, $b=Q/k$, its  statistical properties can be fully characterized by the **load**
$$
\rho=\frac{\alpha}{\lambda k}\in(0,1).
$$

When $\rho<1$, the normalized backlog has an exponential stationary law with parameter  
$\kappa(\rho)=\tfrac1\rho+\mathcal W\!\bigl(-e^{-1/\rho}/\rho\bigr)$---$W$ is the ProductLog function.


<p align="center">
  <img src="uploads/densities_matlab.png" width="50%">
   <figcaption><em> Backlog Density Function.</em></figcaption>
</p>

### User Performance Metrics

Two performance metrics for users can be derived in semi-closed form:

* **Partial‑utilization probability**  
<p align="center">
  <img src="uploads/partial_utilization_with_asympt.png" width="50%">
</p>

The Partial‑utilization probability is the probability that the next block can absorb **all** pending data.

* **Block‑inclusion probability**  
 <p align="center">
  <img src="uploads/inclusion_prob_continuous.png" width="50%">

</p>
The Block‑inclusion probability is  the probability that a randomly chosen transaction is included in the next block under random order‑of‑service (ROS).

<p align="center"> </p>
<p align="center"> </p>

 

Both performance metrics decline monotonically in $\rho$. So keeping $\rho$ as low as possible (given a fixed demand for blocksize) will lead to a user-optimal design.  

## 4. Optimality Conditions

### Miner‑optimal capacity  

Aggregate miner revenue per unit of time is given by
$$
   \mu\,e^{-\mu\Delta k}\,\bigl(\pi+\tau k\bigr),
$$
where the exponential term is the probability that blocks are not tailgated by their predecessors.  Maximizing this expression with respect to $k$ yields  

$$
k^{\mathrm{opt}}(\pi,\tau,\mu)=\frac{\mu^{-1}}{\Delta}-\frac{\pi}{\tau}.
$$

As $M$ tends to infinity, so that the mining market is composed by a large number of atomistic miners, the Nash equilibrium of the block‑size game converges to $k^{\mathrm{opt}}$; thus, in the atomistic limit, the Nash Equilibrium capacity $k_m^{\mathrm{NE}}(\pi,\tau,\mu)$ is both revenue‑maximizing and coincides with the competitive equilibrium capacity.


### User-optimal capacity  

The benchmark for user‑level performance is the **efficient load**

$$
\rho^{*}= \min_{\mu,k>0}\frac{\alpha}{\mu k\,e^{-\mu\Delta k}}
$$

obtained by solving for the pair $(\mu^{*},k^{*})$ that satisfies  

$$
\mu^{*}=\frac{1}{\Delta k^{*}}, \qquad k^{*}\in(0,\infty),
$$

i.e. the block‑production time equals the propagation delay of a block of capacity $k^{*}$.  

The above formula  extends for arbitrary block size an expression that appears in  theorems that bound the maximum sustainable block rate for a given latency. These results are now well-established  both the distributed‑systems literature (Pass & Shi 2017) and in the economics literature (Hinzen et al. 2022).


Comparing the efficient capacity $k^{*}$ with the miner–optimal capacity $k(\pi,\tau,\mu)$ gives  

$$
k^{*}=k(\pi,\tau,\mu)+\frac{\pi}{\tau}.
$$

Since $\pi/\tau\ge 0$, the competitive equilibrium yields  

$$
k(\pi,\tau,\mu)\;\le\;k^{*},
$$
with equality—hence efficient load—**only when the block reward is zero $(\pi=0)$**.  
Any positive coinbase shrinks blocks, lifts the load, and allows miners to earn the fixed reward more often.

The minimal attainable load is  

$$
\rho^{*}=e\,\frac{\Delta}{\alpha^{-1}} , $$
where $e$ is the Euler number. That is,  

$$ \rho^{*} =  e \times  \frac{\textsf{Time to propagate 1 byte of data}} {\textsf{Time to receive 1 byte of new data}} $$

Reaching $\rho^{*}$ requires funding miner security strictly through transaction fees; introducing a coinbase leads to a higher load.  

## 5. Security Implications  

In Nakamoto consensus safety is guaranteed only if honest miners burn **at least as many resources per unit time as any attacker could**.  

Let  
$A$: computational power of a hypothetical adversary (block rate),  
$c$: unit cost of that power, so $A c$ is the **attack cost per unit of time**,  
$\lambda$: rate at which the honest chain grows by one block,  
$\pi+\tau k$: reward paid to the miner of such a block.

A minimal safety requirement is  

$$
\lambda(\pi+\tau k)\;\ge\;A c. \tag{SC}
$$


Suppose we suppress the coinbase $(\pi=0)$ to reach the efficient capacity ($\mu^{-1}=\Delta k$).  
At this parameter configuration  $\lambda k = 1/(e\Delta)$ because the fork probability equals $1- e^{-1}$.  
Plugging into (SC) gives

$$
\frac{\tau}{\Delta}\;\ge\; e\,(A c). \tag{FC}
$$

> *Interpretation*: **To secure the chain using only fees, the fee rate collected per byte must exceed the marginal cost of  attacking the chain by a factor of $e$ (≈ 2.718)**.  

If inequality (FC) holds, security is achievable *without* a coinbase and the load attains its minimum.  
Otherwise a positive $\pi$ is required, miners reduce the equilibrium block size, and the system operates at a second‑best (higher) load.


## 6. Discussion and Caveats
  

### Rewarding orphaned (“uncle”) blocks  

How does the equilibrium change when miners are paid a coinbase reward $\phi$ even for  forked blocks?  

This shifts the equilibrium capacity to  

$$
k(\pi,\tau,\mu,\phi)=\frac{\mu^{-1}}{\Delta}-\frac{\pi-\phi}{\tau}
.
$$

*Setting $\pi=\phi$ neutralizes the fixed‑reward distortion, so the efficient capacity $k^{*}$ is attained for **any** fee rate τ.*  
Hence uncle rewards enlarge the parameter region in which the chain can be both secure and efficient.  

To assess the impact of uncle rewards, there are other considerations beyond this simplified setting: For example, if the attacker is rational, paying out $\phi$ may subsidize deliberate forking and weaken security guarantees.

### Discrete latency  

If propagation delay is *piece‑wise* (no delay below a packet size $\underline k$, full delay Δ above it), strategic complementarities generate **multiple pure‑strategy equilibria**. The qualitative comparative statics remain unaffected—larger Δ or higher $\pi/\tau$ induces  miners to choose smaller blocks.

### Demand Elasticity and Fee–Reward Calibration

The model so far treats the transaction flow α as fixed. Taking the analysis one step further requires calibrating the elasticity of transaction demand to fees. 

---

*Feedback welcome at michele.fabi@ensae.fr.