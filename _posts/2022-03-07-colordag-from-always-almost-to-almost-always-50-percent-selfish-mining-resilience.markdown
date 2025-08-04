---
title: 'Colordag: From always-almost to almost-always 50% selfish mining resilience'
date: 2022-03-07 10:19:00 -05:00
tags:
- blockchain
- incentives
- research
author: Ittay Eyal, Ittai Abraham
---

The Selfish mining attack against blockchain protocols was discovered and formalized in 2013 by [Eyal and Sirer](https://webee.technion.ac.il/people/ittay/publications/btcProcFC.pdf) (also see our [blog post](https://decentralizedthoughts.github.io/2020-02-26-selfish-mining/)). The Bitcoin community has mentioned similar types of [attacks in 2010](https://bitcointalk.org/index.php?topic=2227.msg30083#msg30083). This attack remains a vulnerability of all operational blockchains we are aware of. For Bitcoin’s blockchain algorithm (under reasonable network assumptions), a coalition controlling over 1/4 of the mining power can improve its revenue using this attack. The situation is even worse if we consider more powerful attacks (see [Sapirshtein, Sompolinsky, Zohar](https://arxiv.org/pdf/1507.06183.pdf), [Heilman et al.](https://www.usenix.org/system/files/conference/usenixsecurity15/sec15-paper-heilman.pdf), and [Nakak et al.](http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.712.5613&rep=rep1&type=pdf)).

Pass and Shi’s [Fruitchain](https://dl.acm.org/doi/abs/10.1145/3087801.3087809) is the state of the art in this context. Given the Fruitchain reward mechanism, the authors suggest a strategy that even with coalitions of almost 50%, any other strategy can only increase the coalition's utility by a negligible amount.  However, we show that a simple deviation from the suggested strategy is always at least as profitable as the suggested strategy. Thus, it is **strictly** better for miners, of any size, not to follow the suggested strategy. Even worse, if all miners deviate in this way, the system may become unstable. 

## Colordag: An Incentive-Compatible Reward Scheme
We present *Colordag*, a novel blockchain reward scheme that is joint work with our co-authors Danny Dolev and Joe Halpern. Given the Colordag reward structure, we provide an equilibrium strategy that is *almost always* a best response, even with coalitions of almost 50%. Unlike Fruitchain’s suggested strategy where deviation is *always at least as profitable as good behavior*, the deviation from the Colordag suggested strategy is *almost always strictly less profitable*. 

Colordag utilizes three techniques to achieve strong incentives for equilibrium. In this post, we briefly explain the intuition behind those techniques. Our [Technical Report](https://eprint.iacr.org/2022/308) details all three and the formal proof and analysis. 

### Architecture 

Colordag forms a directed acyclic graph (dag), where every block has multiple parents. Using dags was suggested in [several](https://allquantor.at/blockchainbib/pdf/lewenberg2015inclusive.pdf) [other](https://dl.acm.org/doi/pdf/10.1145/3479722.3480990) [works](https://dl.acm.org/doi/pdf/10.1145/3319535.3363213) for increasing throughput. Here our goal is different – to incentivize playing the suggested strategy via *mechanism design*. While our protocol may generate a dag that might be wide, we use new techniques to incentivize the formation of a single longest chain with as few bifurcations as possible. This longest chain is the one that determines the order of transactions. 

## Technique 1: Random Coloring 

Like Bitcoin and subsequent protocols, Colordag uses the longest chain to identify the series of blocks generated with more mining power. However, occasionally forks form naturally due to network latency (hundreds of such forks happen on [Ethereum each day](https://etherscan.io/chart/uncles)) and slow the chain extension. The first challenge is thus handling the advantage of an attacker with consolidated mining power and no natural forking. Such an attacker has an advantage in generating a long chain over honest players: she doesn’t “lose” blocks in forks. 

To reduce the adversary’s advantage, we introduce a novel **random coloring technique**: each block is assigned a color, actually a number chosen uniformly at random in some range (0, …, *k*-1). Technically, the color is calculated by hashing the block’s hash (which includes the PoW hash) and taking, e.g., the MSB. This way, a miner cannot change the color of a block once generated, and cannot bias the color of the block (except with negligible probability). 

To define the reward structure, we consider the *[graph minors](https://en.wikipedia.org/wiki/Graph_minor)* for the full dag induced by the random  coloring. A minor is derived from the dag by taking all vertices of a certain color, and placing an edge between two vertices if there is a directed path between them that does not include another block of that color (see example below). For each such minor, the probability of a fork is much smaller than in the full graph, and we can make it arbitrarily smaller by increasing the number of colors. Note that the number of colors does not affect the block generation rate. 

![](https://i.imgur.com/ToR0WSY.png)
 
Random coloring reduces the probability of naturally occurring forks between honest miners, thus eliminating a main advantage of an attacker with consolidated mining power. In a way, it provides similar advantages as [Prism](https://dl.acm.org/doi/pdf/10.1145/3319535.3363213) while maintaining just one chain.

## Technique 2: Penalties 

Now that well-behaved miners produce longest chains in each minor with hardly any forks, we can easily identify when a deviation is likely to have occurred – whenever there is a fork. Unfortunately, we cannot in general tell which side of the fork was generated by the deviator and which side by honest miners. Therefore Colordag punishes both sides. Specifically, if two blocks have the same depth (distance from genesis, called height in the Blockchain literature), both receive zero rewards. 

Intuitively, this disincentivizes misbehavior and incentivizes the creation of a single, narrow, chain. The miner gets a  reward of 0 for either not extending the longest chain or not immediately publishing her block. Of course, there is also a penalty for the honest miners, but what each miner cares about is its fraction of the total reward (due to [difficulty](https://en.bitcoin.it/wiki/Difficulty) [adjustment](https://dlt-repo.net/mining-difficulty-in-ethereum/), an increase in the fraction of the total reward corresponds to a probability of mining a block that is higher than the miners’ fraction of the total mining power). Since the utility depends on the relative reward, we can show that such a deviation is strictly worse than following the suggested protocol. 

## Technique 3: Acceptability 

But now a new problem emerges: according to the protocol so far, an attacker could cause honest blocks to be penalized by creating a sibling block. Even worse, the attacker could use this attack even on very old blocks; this would violate what we call *revenue consistency*, the requirement that a miner’s revenue for a block eventually stabilizes (which didn’t need a name previously, as it followed trivially from the blockchain data structure in previous work). 

To prevent this, Colordag ignores blocks unless, roughly speaking, they are on a path that is almost as long as the longest path.  Blocks added much later will not have this property.  Blocks that are ignored in this way do not get any reward.

## Analysis 

We analyze Colordag under the assumption that we are dealing with an extremely strong adversary, who knows when miners will generate blocks and controls the (synchronous) network. Even with such a strong adversary, following Colordag gives what we call an **epsilon-sure Nash Equilibrium**, resilient to coalitions that control a minority of the mining power, where an epsilon-sure Nash Equilibrium is one in which following the protocol is almost surely (i.e., with probability $1-\varepsilon$, for an arbitrarily small $\varepsilon$) the miners’ strict best response. 

The gritty details are in our [Technical Report](https://eprint.iacr.org/2022/308). 

Please leave comments on [Twitter](https://twitter.com/ittayeyal/status/1500943944384929792?s=20&t=Q-QPZI9PfIXFnLAyqs3ygQ).


