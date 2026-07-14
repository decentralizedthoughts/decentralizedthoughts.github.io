---
title: "Time Is Money: Incentivized Causal Transaction Ordering"
date: 2026-07-14 17:00:00 -05:00
tags:
- blockchain
author: Hongyin Chen, Xu Zheng, Jichen Li, Ittay Eyal
---

Front-running is a pervasive and costly problem on blockchains. Users earn rewards by publishing functional transactions that keeps markets efficient, such as arbitrage. But an attacker can [observe such a transaction before it is ordered and publish her own ahead of it](https://a16zcrypto.com/posts/article/mev-explained/), seizing the reward and eroding users' incentive to issue these transactions at all. The problem is well known and has drawn sustained effort from both industry and academia, yet it remains open. 

The fundamental challenge is that preventing front-running means enforcing causality: A transaction published in reaction to another must be ordered later, but this causal relationship is visible only to the attacker who reacts, and the protocol cannot observe it. We present PRECEDE, which takes a distinct angle: Instead of constraining how transactions are ordered, as every prior approach does, it removes the economic incentive to front-run, so the attacker never even tries. To our knowledge, PRECEDE is the first mechanism to address front-running this way. We call this principle **entry deterrence**.

## A running example: an arbitrage

We start with a typical example of front-running. On a blockchain, people trade on a market by publishing transactions, and validators decide the order in which these transactions execute. Suppose the market's current state lets anyone buy an asset below its price on other markets. A single transaction captures this gap, a profit worth $R$. Such an opportunity is called arbitrage. Because the first such trade closes this gap, the profit goes to whoever gets ordered first. A user spots the gap and publishes a transaction to capture it. 
<p align="center">
<img src="/uploads/opportunity.png" alt="An arbitrage opportunity" width="488">
</p>

<p align="center" style="font-size: 0.75em"><em>An arbitrage opportunity worth $R = 20$. The user publishes $\mathrm{TX\_U}$ with bid $9$; the validator orders by bid, so her arbitrage trade captures the reward.</em></p>


But before validators order it in the blockchain, the transaction is visible to everyone, including an attacker, who submits the same trade and pays the validator to place her own transaction ahead of the user's. The attacker's transaction executes first and earns $R$, while the user, who found the opportunity, earns nothing.



In practical systems like [Ethereum](https://ethereum.org/en/whitepaper/) and [Solana](https://solana.com/solana-whitepaper.pdf), validators order transactions by how much each one pays them, so the higher payer goes first. Front-running then turns into a bidding war: The user pays the validator more to stay ahead, the attacker pays more again, and the two keep raising until most of $R$ has gone to the validator. The reward that should have gone to whoever found the opportunity is competed away in fees, a race to the bottom. This is not hypothetical: On Flashbots, the winner of an arbitrage pays the validator a median of more than 90% of $R$. Whether the user loses the reward to the attacker or spends it outbidding her, her incentive to search for such opportunities erodes, and so does the market efficiency that depends on it. 

<p align="center">
<img src="/uploads/front-running.png" alt="An attacker front-runs the user" width="488">
</p>

<p align="center" style="font-size: 0.75em"><em>Front-running. The attacker copies the trade as $\mathrm{TX\_A}$ with a higher bid of $10$. Ordering by bid places it ahead of $\mathrm{TX\_U}$, so the attacker seizes the reward and the user earns nothing.</em></p>

<!-- We return to this arbitrage once the mechanism is in place. -->

## The limits of existing defenses

A large body of work constrains how validators may order transactions. Three families dominate, but front-running attackers slip past all of them. 

- **Order by arrival time.** A committee of nodes orders transactions by when each node receives them, so the user's transaction, sent first, should come ahead of the attacker's later reaction. But this has been [proven impossible](https://cryptobern.github.io/quickfairorder/). Network delays make the nodes receive the transactions in different orders, so they cannot agree on which came first, and the protocol is left to settle the disagreement arbitrarily. The attacker can bend this in her favor: As one of the committee nodes, she misreports when she received the user's transaction, so her later transaction still ends up first.

  <p align="center">
  <img src="/uploads/observation.png" alt="Three validators receive the transactions in different orders" width="600">
  </p>

  <p align="center" style="font-size: 0.75em"><em>Network delays leave each validator with a different local order.</em></p>

  <p align="center">
  <img src="/uploads/timestamp-based-ordering.png" alt="Majority voting on each pair yields a cycle" width="600">
  </p>

  <p align="center" style="font-size: 0.75em"><em>The ordering protocol must aggregate the validators' reports into a single global order. Majority voting on each pair of transactions, for example, yields a cycle rather than an order.</em></p>

- **Randomize the order.** The protocol orders the transactions in a block uniformly at random, removing the deterministic priority an attacker could exploit. But uniform randomization invites spam: A participant's chance of being ordered first grows with the number of transactions she publishes, so the attacker publishes many copies of her transaction. Such spam burdens the system while still allowing front-running.

  <p align="center">
  <img src="/uploads/randonmized.png" alt="Uniform randomization gives each transaction an equal chance" width="450">
  </p>

  <p align="center" style="font-size: 0.75em"><em>Randomized ordering. The protocol picks the first transaction uniformly at random, so the user and attacker are each first with probability $1/2$.</em></p>

  <p align="center">
  <img src="/uploads/spam.png" alt="Spam skews the random draw toward the attacker" width="450">
  </p>

  <p align="center" style="font-size: 0.75em"><em>But randomization invites spam. The attacker publishes extra copies, so with two transactions against the user's one she is first with probability $2/3$.</em></p>
- **Encrypt the content.** This approach hides transaction content until the order is fixed, so an attacker cannot see what a transaction does and copy it. But such schemes still leave room for front-running. Even encrypted, a transaction reveals its timing, propagation, and creator metadata, [enough to speculatively race ahead](https://a16zcrypto.com/posts/article/limits-encrypted-mempools/), and whoever holds the key to open it can be paid to peek early or leak the content.


## The Underlying Challenge: Causality

Preventing front-running is fundamentally hard. It is a matter of **causality**: If a participant publishes her transaction after observing another's, it should appear later on chain. But this causal relationship is private to the attacker who issues the later transaction. In a decentralized system we cannot compel participants to follow the protocol, neither to refrain from front-running nor to report honestly when they acted; classical solutions like Lamport timestamps do not apply, because a participant can misreport her timestamp and the chain cannot verify it. Instead, each participant takes whichever action maximizes her own revenue.

The protocol can therefore make no trust assumption, which participants may violate for gain.  It must rely only on signals the blockchain can observe. It does not even know the reward $R$, which varies across orders of magnitude, so any defense must hold across the full range. Together, these constraints force the protocol to defend blindly: against any rational adversary, at any revenue scale, using only signals the chain can verify.

## Deterrence: order before ordering

Our goal is that the attacker never tries to front-run, so the ordering itself never needs to learn the causal order. We call this *entry deterrence*: The user publishes a bid high enough that no attacker can profit by entering to compete, so the attackers abstain. 

We realize this with **PRECEDE**, **P**ower-weighted **R**andomization for **E**nforcing **C**ausal-ordering through **E**ntry **DE**terrence. PRECEDE orders transactions solely by the bid each carries, which is on-chain and verifiable, rather than by timestamps or arrival times. A transaction with bid $b$ has weight $w(b) = b^k$ for a parameter $k > 1$, and is placed first with probability proportional to its weight. We assume the chain is [censorship-resistant](https://decentralizedthoughts.github.io/2026-04-27-beyond-CR/): Every published transaction enters the same ordering, so an attacker cannot drop the user's transaction or place it in a separate one, and must outbid it instead.

As $k$ grows toward infinity, the highest bid wins with probability approaching one, and the design degenerates into the deterministic descending-bid ordering of deployed blockchains. Under that rule the user can deter entry only by bidding the entire reward $R$: With any smaller bid, the attacker bids slightly higher, wins with certainty, and profits. Such deterrence leaves the user nothing. A carefully chosen $k$ softens this rule, letting her deter more cheaply. Overbidding no longer guarantees a win, and a counter-bid is paid for whether or not it wins. The attacker then faces a dilemma: A small counter-bid is cheap but, against the user's large weight, wins too rarely to profit, while a large one wins often but, since $k > 1$, must be so large that its cost exceeds $R$. Neither option yields positive expected revenue, so a bid strictly below $R$ suffices to deter her.

At the other extreme, $k = 0$ makes every bid weigh the same, degenerating the order into a uniform random pick. A participant's chance of being first then grows with the number of transactions she publishes, inviting spam. An exponent $k > 1$ removes this incentive: Because $b^k$ is superadditive, a single bid outweighs the same amount split across many, so merging into one transaction beats spamming. Each participant therefore publishes a single bid.

Return to the arbitrage with $k = 2$. Assuming that the user publishes a single bid of $R/2$, of weight $(R/2)^2 = R^2/4$. An attacker who enters with bid $b$ has weight $b^2$ and is placed first with probability $b^2/(b^2 + R^2/4)$. Paying her full bid whether she wins or loses, her expected revenue is

$$ \frac{b^2}{b^2 + R^2/4}\,R \;-\; b \;=\; -\,\frac{b\,(b - R/2)^2}{b^2 + R^2/4} \;\le\; 0 . $$

The result is never positive, so no bid earns the attacker anything: She stays out, and the user's single transaction wins. The user keeps half of $R$, instead of losing nearly all of it to a bidding war. This is deterrence: The attacker never competes, because competing never pays.

<p align="center">
<img src="/uploads/precede.png" alt="Entry deterrence with PRECEDE" width="560">
</p>

<p align="center" style="font-size: 0.75em"><em>Entry deterrence. The user publishes a single $\mathrm{TX\_U}$ with bid $R/2 = 10$. Any attacker who competes earns revenue $\le 0$, so she abstains, and $\mathrm{TX\_U}$ captures the reward.</em></p>


## Generalization and Results

The example fixed two things the mechanism leaves free: the exponent $k = 2$, and the assumption that a losing bid is paid in full. In general the exponent is any $k > 1$, and a losing transaction does not pay its bid in full: It reverts and pays a fraction $\gamma$ of its bid, the **losing-fee rate**. The example took $\gamma = 1$.

The user deters by publishing the **deterring bid** $b_{\mathrm{det}}$, the smallest bid that holds every attacker's expected revenue at or below zero. It has a closed form,

$$ b_{\mathrm{det}} \;=\; R\left(\frac{(k-1)^{k-1}}{\gamma\,k^{k}}\right)^{1/k} . $$

The simple case above is $k = 2$ and $\gamma = 1$, where this is $R/2$.

Knowing the deterring bid is not yet enough for the mechanism to work. Three further properties are needed, and each holds only for a suitable range of the exponent $k$. The system designer picks a single $k$ that satisfies all three, and this $k$ is common knowledge in the system.

**Anti-spam.** As discussed above, the superadditivity of the weight $b^k$ already makes merging win more often than spamming. But that gain is not free when $\gamma < 1$: A losing transaction pays only $\gamma b$ while the winner pays its full bid, so concentrating the whole bid on one transaction raises the expected payment. Single bids dominate only when $k$ is large enough that the merging gain outweighs this extra cost, namely $k \ge \ln 2 / \ln(1+\gamma)$.

**Profitability.** Deterring entry costs the user a bid, and she profits only if that bid leaves her something, $b_{\mathrm{det}} < R$. This is not automatic, since as $k \to \infty$ the deterring bid climbs toward the whole reward. It stays below $R$ exactly when $\gamma > (k-1)^{k-1}/k^k$. 
But this condition already holds due to the anti-spam bound above. 

**Game and Equilibrium.** Existence of the deterrence bid is not enough: Rational players might prefer to deviate. We model the competition as a sequential game in which the user and the attacker act in alternating turns, each observing all earlier moves. The attacker moves last, reflecting her advantage in observing and reacting to others' transactions, whether from lower network latency or from controlling the set of placed transactions as the validator. 

The deterrence strategy, with the attacker abstaining in response, is a subgame-perfect equilibrium whenever $k \ge \max\{2,\ \exp(1/\gamma)/\gamma\}$, regardless of the game's length. This bound is only sufficient and far from tight: We have no closed form for the exact threshold, but our numerical analysis shows it is either already covered by the anti-spam bound or above it by at most $0.2$, hence very close to the anti-spam bound in every case.


## Takeaways

- Front-running is hard because the blockchain cannot see causality. 
- Entry deterrence is PRECEDE's answer: It removes the incentive to front-run instead of enforcing causality through the order, so the attacker never enters and the validator does not have to divine who reacted to whom.
- Since chains often already order by bid, they can easily use PRECEDE: Use the power-weighted random ordering in which a transaction with bid $b$ is placed first with probability proportional to $b^k$, tuned by a single exponent $k$ between highest-bid-wins and a uniform draw, using only the on-chain bid.
- A closed-form deterring bid makes front-running unprofitable, so the attacker stays out.
- Choosing the exponent $k$ within a suitable range makes the mechanism anti-spam and profitable, and makes the user's deterrence, with the attacker abstaining, an equilibrium.

For the full model and the proofs, see our paper, [PRECEDE](https://arxiv.org/abs/2607.11496).
