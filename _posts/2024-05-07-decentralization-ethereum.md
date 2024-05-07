---
title: Decentralization of Ethereum Builder Market
date: 2024-05-07 13:05:00 -04:00
tags:
- MEV
author: Sen Yang, Kartik Nayak, and Fan Zhang
---

Decentralization is a core underpinning of blockchains. Is today's blockchain really decentralized?

In a [recent work](https://arxiv.org/pdf/2405.01329), we explore this question in the context of the *builder market* in Ethereum. The market was introduced to avoid centralization caused by Maximal Extractable Value (MEV). After two years in operation, however, the builder market has evolved to a highly centralized one with three builders producing most of the blocks. As can be seen in the following figure, Beaver, Rsync and Blocknative produce more than 90% of the blocks


|![Market share of builders. The builder market is arguably one of the least decentralized parts of Ethereum!](https://hackmd.io/_uploads/HJgkDOMMC.png)|
|:---:|
| **Market share of builders. The builder market is arguably one of the least decentralized parts of Ethereum!** |

This leads to two natural questions:

***1. Why does the builder market centralize, given that it is permissionless and anyone can join?***

***2. What are the security implications of a centralized builder market to MEV-Boost auctions?***

Through a rigorous empirical study of the builder market’s core mechanism, MEV-Boost auctions, we answered these two questions using a large-scale auction dataset we curated since 2022. Our work focuses on *why* builders win auctions and we shed light on the **openness**, **competitiveness**, and **efficiency** of MEV-Boost auctions.

This post provides a summary of our findings from the empirical study, and we encourage readers to read the full version of our [paper](https://arxiv.org/abs/2405.01329).


## Why does the builder market centralize, given that it is permissionless and anyone can join?


### Finding 1: Private order flows contribute to 60% of the MEV in over 50% of the blocks in MEV-Boost.

The builder market is technically open to everyone, but the barrier to accessing profitable private order flows forms an implicit access barrier. We illustrate the importance of private order flow to the success of builders by plotting the fraction of builder income from private order flows. Currently, approximately 60% of the block value comes from private order flows.

| ![daily_private_order_flow](https://hackmd.io/_uploads/BkOHPuMGA.png)|
|:--:|
| **Fraction of builder income from private order flows.** |

### Finding 2: We identified five pivotal providers (MEV-Share, MEV Blocker, jaredfromsubway.eth, Banana Gun, Maestro) who had a sustained influence on the outcome of more than half of MEV-Boost auctions.


We define a provider $P$ as pivotal for an instance of MEV-Boost auction if removing $P$'s transactions from the winning block causes the winner to lose the auction. For each pivotal provider, we compute the fraction of auctions in which it is pivotal. We refer to this metric as *pivotal level*, a number ranging from 0 to 1, which can be used to quantify the importance of individual providers.

We plot the weekly pivotal level for the top-5 pivotal providers. A positive trend towards decentralization is observed as the pivotal level of the searcher jaredfromsubway.eth decreased, while the pivotal level of MEV-Share and MEV Blocker increased. These two providers positively impact decentralization because they have relatively clear requirements for accessing their order flows. However, their reliance on upstream providers like Maestro is alarming.


| ![pivotal-level](https://hackmd.io/_uploads/SJxPMRDzR.png)|
|:--:|
| **The pivotal level of top-5 pivotal providers over time. A line may not start from the beginning because the provider did not exist at that point. Maestro became an independent provider around December 2023.** |

### Finding 3: To access private order flows, new builders need to pay up to 1.4 ETH to enter the market.


The private order flow providers impose reputation requirements on the builders, which are usually evaluated based on market share. These reputation requirements act as a proxy for trust, e.g., ensuring builders do not unbundle transactions. Thus, new builders face a chicken-and-egg problem as they need access to private order flows to win auctions and gain market share, but the private order flow providers only serve builders with a decent market share.

Builders thus resort to subsidizing their bids, i.e., bidding higher than the true value of a block, to win auctions. We compute the minimal subsidy needed to establish a 1% market share for one week (which is the requirement of MEV Blocker) to quantify the entry barrier for new builders. Initially, this cost was nearly zero before May 2023, but it has steadily increased, surpassing 1.4 ETH by March 2024.


|![market-share-cost](https://hackmd.io/_uploads/rkTt3dGzR.png)|
|:--:|
|**Subsidy required to establish a 1% market share, as required by MEV Blocker. This quantifies the cost of accessing private order flows.**


## What are the security implications of a centralized builder market to MEV-Boost auctions?




### Finding 4: The inequality in block building is highest among tail builders, followed by middle and least among top builders, and it worsens when MEV increases.


We first compare the true values across different builders for the same auction to understand the variations in builders' abilities to extract values.  We used the quartile coefficient of dispersion (QCD) to quantify the inequality of true values across builders. 


The distribution of the QCD for MEV-Boost auction reveals two trends. First, within a given MEV tier, inequality is greatest among tail builders, followed by middle builders, and is least among top builders. Fortunately, the inequality among top builders is not significant, which supports the premise of competitiveness and efficiency. Second, the inequality worsens as the MEV tier increases. 


|![qcd-mev](https://hackmd.io/_uploads/r1FKwcMf0.png)|
|:--:|
| **Violin graphs for the distribution of the QCD across three MEV tiers, for top, middle, and tail builders** |


### Finding 5: 88.84% of the MEV-Boost auctions are competitive, with proposers' losses from uncompetitive auctions amounting to 0.98% of total gains.

We further quantify whether an auction is competitive or efficient by using true values. We define an MEV-Boost auction as competitive if the winning bid is not less than the second-highest true value.

Our results reveal that 88.84% of the MEV-Boost auctions we analyzed were competitive. However, we also found that the auctions tend to be less competitive as the MEV of a slot increases. We further quantify the loss for proposers, and the results show that proposers incurred total losses amounting to 221.09 ETH in 16,498 uncompetitive auctions, which represents 0.98% of the total gains.

| ![EPI_v2-min](https://hackmd.io/_uploads/ryiPwqzMA.png) |
| :--: |
| **The distribution of CI and EI, where each dot represents an auction. The color represents density when multiple dots overlap.** |


### Finding 6: 79.74% of the MEV-Boost auctions are efficient, and 51.4% of the inefficient auctions are caused by block subsidization.

We define an MEV-Boost auction as efficient if the winner has the highest true value. An interesting finding is that more than 20% of MEV-Boost auctions are inefficient and the auctions tend to be inefficient when the MEV in an MEV-Boost auction is low. Further analysis reveals that over half of the inefficient auctions are caused by block subsidization. Moreover, block subsidization is more common when the extractable value is small, because the cost will be relatively low.

<!-- Using the true values, we propose two metrics, *competitive index* (CI) and *efficient index* (EI), to quantify whether an auction is competitive or efficient, respectively.


In a given slot $s$, suppose builders $p_1,\cdots,p_n$ are ordered by their true value from high to low, i.e., $TV(p_1, s) \geq \dots \geq TV(p_n, s)$, $BV_w(s)$ is the bid value of the winner and $TV_w(s)$ is the corresponding true value, the competitive index of slot $s$, $CI(s)$ is defined as:
$$
    CI(s) = \frac{BV_w(s)-TV(p_2, s)}{TV(p_2, s)} \times 100\%.
$$

The efficient index, $EI(s)$, is defined as:
$$
    EI(s) = \frac{TV_w(s)-TV(p_2, s)}{TV(p_2, s)} \times 100\%.
$$

Namely, $CI(s)$ measures the relative difference between the winning bid and the second-highest true value. $CI(s) \geq 0$ indicates that the winning bid value is not less than the second-highest true value, satisfying the definition of a competitive auction. $EI(s) > 0$ indicates that the winner has the highest true value, whereas $EI(s) \leq 0$ implies that the bidder with the highest true value lost the auction. 

We plot the distribution of the calculated CI and EI across all MEV-Boost auctions in the ultra sound relay dataset, which 
 that more than 88% of auctions are competitive and only 79% of auctions are efficient. Further analysis reveals that proposers incurred total losses amounting to 221.09 ETH in the uncompetitive auctions, which is 0.98% of the total gains of the proposers. Additionally, over half of the inefficient auctions are caused by block subsidization. -->



