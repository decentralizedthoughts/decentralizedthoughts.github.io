---
title: 'Asynchronous Agreement Part Two: Ben-Or''s protocol'
date: 2022-03-30 07:16:00 -04:00
tags:
- asynchrony
- consensus101
- consensus
author: Ittai Abraham, Namma Ben-David, Sravya Yandamuri
---

We continue to explore the marvelous world of consensus in the [Asynchronous model](https://decentralizedthoughts.github.io/2019-06-01-2019-5-31-models/). In this post, we present Ben-Or's classic [protocol](https://homepage.cs.uiowa.edu/~ghosh/BenOr.pdf) from 1983. In the next post, we will present a [more modern version](https://decentralizedthoughts.github.io/2022-03-30-asynchronous-agreement-part-three-a-modern-version-of-ben-ors-protocol/) that is a simplified version from our [paper](https://eprint.iacr.org/2022/711.pdf).

In the [previous post](https://decentralizedthoughts.github.io/2022-03-30-asynchronous-agreement-part-one-defining-the-problem/) we defined the problem of Asynchronous Agreement, so without further ado, here is Ben-Or's protocol for Binary Asynchronous Agreement with $n=2f+1$ parties assuming the adversary can crash $f$ parties:

```
Ben-Or's Protocol for party i

input: v (0 or 1)
r:=1

while true
    send <echo1, r, v> to all
    wait for f+1 <echo1, r, *>
        if all have value w, then send <echo2, r, w> to all
        otherwise send <echo2, r, bot> to all
    wait for f+1 <echo2, r, *>
        if all have the same non-bot value u, then decide(u)
        if all have the value bot, then v:= coin()
        otherwise, v:=u where u is a non-bot value from <echo2, r, *>
    r++    
```

Note that this protocol does not terminate when it decides. Adding a *termination gadget* that provides termination in the crash model is quite simple:
```
Termination Gadget for crash failures

If receive <decide u>, then
    decide(u) 
If decide(u), then
    send <decide u> to all
    Terminate
```


Why does Ben-Or's protocol work? The first thing to check is **Weak Validity** (if all are non-faulty and start with $b$ then all decide $b$). Indeed, if all parties have the same input $b$, and no party is faulty, then clearly all parties will send `<echo1, 1, b>`, hence will see $f+1$ `<echo1, 1, b>` message after one round, hence will send `<echo2, 1, b>`, hence will see $f+1$ `<echo2, 1, b>` message and decide (and terminate from the termination gadget).

The next property to verify is **Agreement** (that no two parties decide on different values). This follows from two simple claims:

*Claim 1*: there cannot be `<echo2, r, 0>` and `<echo2, r, 1>`. This follows from quorum intersection, sending echo2 requires $f+1$ echo1 of the same value, but this would mean one party sent both `<echo1, r, 0>` and `<echo1, r, 1>` which is not possible. 

*Claim 2*: if one party sees $f+1$ messages for `<echo2, r, u>` then all parties will see at least one message for `<echo2, r, u>`. This follows since at least one of the $f+1$ parties that sent `<echo2, r, u>` is non-faulty and again from quorum intersection.

Combing both claims, we can now look at the first round $r$ in which a party decided value $u$, and conclude that any party that reaches the end of round $r$ will have $v=u$. We can now use the argument above for Weak Validity and prove that all non-faulty parties will decide $u$ by round $r+1$.

Now for the hard part. Why does this protocol have **Finite Expected Termination**?

It turns out that this is a non-trivial theorem for an adaptive adversary. It took over 15 years to realize via a rather complicated argument:

**[Theorem: [Aguilera, Toueg 1998]](https://ecommons.cornell.edu/bitstream/handle/1813/7336/98-1682.pdf?sequence=1&isAllowed=y)**: Ben-Or's protocol with $n=2f+1$ parties has an Finite Expected Termination of $O(2^{2n})$.

This leaves us in an unsatisfying state. While Ben-Or's protocol is elegant, the proof for Finite Expected Termination is non-trivial and not easily taught in a standard class (or a short blog post). Is there a simpler proof? Maybe there is a reason for the complexity? Another concrete question is about efficiency: can we improve the $O(2^{2n})$  bound to a more natural $O(2^n)$ bound? 

More fundamentally, the question we ask is: how should we argue about the expected termination of Asynchronous protocols with an adaptive adversary? Is there a more general framework that can allow us to decompose the problem?

We will answer this [in the next post](https://decentralizedthoughts.github.io/2022-03-30-asynchronous-agreement-part-three-a-modern-version-of-ben-ors-protocol/).


Thoughts and comments on [Twitter](https://twitter.com/ittaia/status/1509211437306163202?s=20&t=Ow_DBFvPTgVP6BQK4BIRLg).

