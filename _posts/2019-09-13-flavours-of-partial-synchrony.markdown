---
title: Flavours of Partial Synchrony
date: 2019-09-13 18:00:00 -04:00
tags:
- dist101
author: Ittai Abraham
---

This is a follow-up post to the post on [Synchrony, Asynchrony and Partial synchrony](https://ittaiab.github.io/2019-06-01-2019-5-31-models/). The partial synchrony model of [DLS88](https://groups.csail.mit.edu/tds/papers/Lynch/jacm88.pdf) comes in two flavors: **GST** and **Unknown Latency**. In this post we discuss:

1. Why, *in practice*, the GST flavor seems to be a better model of the real world.
2. Why, *in theory*, a solution for the Unknown Latency flavor implies a solution for the GST flavors - but the opposite is not clear.

{: .box-note}
**Note:** this post was updated in September 2024 based on the work of [Constantinescu,  Ghinea,  Sliwinski, and Wattenhofer](https://arxiv.org/abs/2405.10249).

### The GST flavor of Partial Synchrony

The **Global Stabilization Time** (GST) model for Partial Synchrony assumes that:

1. There is an event called *GST* that occurs after some finite time. 
2. There is no bound on message delays before *GST*, but after *GST* all message must arrive within some known bound $\Delta$.

Note that in this model, there is no signal that GST happened and no party knows when GST will happen.

The real world definitely does not behave like this, so why is this model so popular? It's because it abstracts away a much more plausible model of how networks behave:

1. Say 99% of the time the network is stable, and message delays are bounded. For example, it's probably true that internet latencies are less than a second 99% of the time (more formally, the 99% percentile of latency is less than a second).
2. During times of crisis (for example, when under a Denial-of-Service attack) there is no good way to bound latency.

The *GST* flavor allows building systems that perform well in the *best case* but maintain safety even if the conservative assumptions on latency fail in *rare cases*. This allows protocol designers to fix the parameter $\Delta$ based on reasonably conservative values.

### The Unknown Latency flavor of Partial Synchrony

In the *UL* flavor, the system is always *synchronous*, but the bound of the maximum delay is *unknown* to the protocol designer.

There are several advantages of this flavor in terms of simplicity. First, it requires fewer parameters (no GST, just $\Delta)$. Second, it avoids defining asynchronous communication.  

The way the *Unknown Latency* models the real world is somewhat problematic, it essentially strives to set the latency of the protocol to be as large as the *worst case* latency that will ever occur.

Unlike the GST flavor where $\Delta$ can be set conservatively, in the UL flavor the estimation of latency needs to grow based on the worst case behavior of the system.

For example, many early academic BFT systems had mechanisms that **double** the protocol's estimation of $\Delta$ each time there was a timeout. [Prime](http://www.dsn.jhu.edu/pub/papers/Prime_tdsc_accepted.pdf) showed that this may cause a serious denial of service attack.

### Theoretical relationship between the flavors of Partial Synchrony

We start with the easy observation that a protocol that solves agreement in the UL flavor also solves agreement in the GST model.

We then discuss the challenges of a reduction in the other direction.

### From Unknown Latency to Global Stabilization Time

Assume a protocol $Q$ that obtains safety and liveness in the Unknown Latency flavor. Does $Q$ also obtain safety and liveness in the GST flavor?

Yes! Consider an execution in the GST flavor and let $\Gamma$ be the maximum of $\Delta$ and the time until $GST$ starts. Observe that by definition, $Q$ has safety and liveness assuming that the unknown latency is $\Gamma$, because its true for any finite latency.

Note that this reduction is extremely wasteful: the value of $\Gamma$ may be huge. Many systems may strive to adjust their estimate of $\Delta$ both up and down.

### From Global Stabilization Time to Unknown Latency


Assume a protocol $P$ that obtains safety and liveness in the GST flavor (with a known parameter $\Lambda$ after GST). Does $P$ also obtain safety and liveness in the Unknown Latency flavor?


#### First approach (and its problems)

The idea was to start with some estimation $\Lambda$ of the actual UL parameter $\Delta$. Each time a protocol timeout expires, increment $\Lambda$. 

For safety, we need to argue that incrementing $\Lambda$ does not break safety, one trivial way to do that to assume this is a property of $P$, indeed this is the case with many protocols. however, it is not clear that a generic protocol has this property. For example, as currently stated, $P$ may do very different things for different values of $\Lambda$.

For liveness, the idea was to say that at some point $\Lambda$ will grow to be larger than $\Delta$. At that point and onwards, we need to argue that the protocol obtains liveness. 

#### Second approach of [Constantinescu,  Ghinea,  Sliwinski, and Wattenhofer](https://arxiv.org/abs/2405.10249).

Instead of incrementing $\Lambda$, simply slow down the clock. This means we assume that we can control the internal clock. In many ways, slowing down the clock, or increasing the timer is rather similar. But this slow down allows the protocol to continue running with the same parameters and the only thing that changes is the external rate of the clock.

For safety, observe that slowing down the clock does not break safety. This is true because we could simulate this delay via additional message delay and our assumption that $P$ is safe no matter the message delay (safe in asynchrony).

For liveness, observe that at some point $T$ the amount of clock slow down is such that $\Lambda$ time in the slowed down clock is more than $\Delta$ in the real time. Any message sent will arrive in time at most $\Delta$ and from the properties of $P$ we know that once messages arrive in less than $\Lambda$ time then it obtains liveness. So indeed we can show that from $T$ onwards the protocol $P$ behaves as if it is after GST.

#### Notes 

The idea of dynamically incrementing the estimation of the maximum latency (or dynamically slowing down the node) has efficiency challenges:

1. Incrementing $\Lambda$ too slowly means that it may take a lot of time to reach consensus. This is a type of denial-of-service that slows down the system.
2. Incrementing  $\Lambda$ too aggressively (say by doubling) means that while we may reach  $\Lambda>\Delta$ quickly, it may still happen that there are at least $f$ more timeouts due to malicious primaries. So $\Lambda$ may grow exponentially. This again may cause a denial-of-service that slows down the system.

In practice systems often adjust their estimate of $\Delta$ both up and down (sometimes using an explore-exploit type online learning algorithm). 

**Acknowledgment.** We would like to thank [L. Astefanoaei](https://twitter.com/3zambile)  for helpful feedback on this post.

We would like to thank Ling Ren and Tim Roughgarden for pointing out the incorrect proof in the previous version.

Please leave comments on [Twitter](https://twitter.com/ittaia/status/1181013611491184640?s=20)
