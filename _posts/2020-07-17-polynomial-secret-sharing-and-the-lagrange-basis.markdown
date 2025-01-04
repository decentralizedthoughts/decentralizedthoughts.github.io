---
title: Polynomial Secret Sharing and the Lagrange Basis
date: 2020-07-17 14:23:00 -04:00
tags:
- secret sharing
author: Ittai Abraham, Alin Tomescu
---

In this post, we highlight an amazing result: Shamir's [secret sharing scheme](https://cs.jhu.edu/~sdoshi/crypto/papers/shamirturing.pdf). This is one of the most powerful uses of [polynomials over a finite field](/2020-07-17-the-marvels-of-polynomials-over-a-field) in distributed computing.
Intuitively, this scheme allows a $Dealer$ to *commit* to a *secret* $s$ by splitting it into *shares* distributed to $n$ parties. The secret is hidden and requires a threshold of $f+1$ parties in order to be reconstructed, where $f < n$.

In the basic scheme, we will assume a [passive adversary](https://decentralizedthoughts.github.io/2019-06-07-modeling-the-adversary/) that controls [any $f$ out of the $n$ parties](https://decentralizedthoughts.github.io/2019-06-17-the-threshold-adversary/).
A passive adversary (sometimes called [Honest-But-Curious](https://eprint.iacr.org/2011/136.pdf) or [Semi-Honest](http://www.wisdom.weizmann.ac.il/~oded/foc-vol2.html)) does not deviate from the protocol but can learn all possible information from its _view_: i.e., the messages received by parties it controls. In the follow up posts, we extend the secret sharing scheme to [crash adversaries](https://decentralizedthoughts.github.io/2022-08-17-secret-sharing-with-crash/),  the BGW VSS with [malicious adversaries](https://decentralizedthoughts.github.io/2022-08-24-BGW-secret-sharing/), and highlight the [additivity](https://decentralizedthoughts.github.io/2022-08-25-dining-cryptographers-additive/) of polynomial secret sharing.

A *secret sharing scheme* is composed of two protocols: *Share* and *Reconstruct*.
These protocols are distributed: they are run by the $n$ parties, jointly.
The Dealer has a *secret* $s$, which is given as _input_ to the Share protocol.
Intuitively, if the Share protocol "succeeds", then the Reconstruct protocol will *output* that same secret $s$.

These properties of a secret sharing scheme can be described more formally as:

**Binding**: Once the first non-faulty party completes the Share protocol, there exists some value $r$ such that $r$ is the output value of all non-faulty parties that complete the Reconstruct protocol.

**Validity**: If the Dealer is non-faulty, then the output of the Reconstruct protocol is the Dealer's input value $s$.

**Hiding**: If the dealer is non-faulty, and no honest party has begun the Reconstruct protocol, then the adversary can gain no information about $s$. 


The first two properties seem well defined, but what about the hiding property? What does it mean that the adversary "gains no information about $s$"? We will be more formal about this later but, informally, this means that anything the adversary can output by interacting with this protocol, the adversary could have output the same without any interaction at all.

### Shamir's scheme

We enumerate the parties via the integers $\\{1,2,3,\dots,n\\}$. We also assume there is a commonly known finite field $\mathbb{F}_p$ with $p>n$.

**Share protocol**: Given a secret $s$ as input, the Dealer _randomly_ chooses $f$ values $p_1,\dots,p_f \in_R \mathbb{F}_p$ and defines a degree $\le f$ polynomial

$$p(X)=s+p_1 X + \dots + p_f X^f$$

The Dealer then sends $p(i)$ to each party $i$.
We refer to $p(i)$ as party $i$'s _share_ of the secret $s$.

{: .box-note}
**Important:** The Dealer's secret $s$ is "stored" in the polynomial as $p(0) = s$.

**Reconstruct protocol**: 
Each party $i$ sends its share $p(i)$ to all other parties. 
Each party receives all the shares $p(1),\dots,p(n)$ and outputs the Dealer's original secret $s$ as follows:

$$s=p(0)=\sum_{i \in I} \lambda_i p(i)$$

Here, $I$ is the subset of parties whose shares are used to reconstruct $s$.
Specifically, $I$ can be any $(f+1)$-sized subset of $\\{1,2,\dots,n\\}$ but, for simplicity, let us stick to $I = \\{ 1,\dots,f+1 \\}$.
Furthermore:

$$\lambda_i = \frac{\prod_{j \in I \setminus \{i\}} j}{\prod_{j \in I \setminus \{i\}} (j-i)}$$

This looks like magic, no?
No worries.
We explain how this reconstruction of the secret $s$ from the parties' shares works next. 

### Lagrange Basis

Lets dig deeper into how and why the values $\lambda_1,\dots,\lambda_{f+1}$ are defined. 
As mentioned before, we could have used *any* set of $f+1$ shares to reconstruct the secret.

For any set $Z=\\{z_1,\dots,z_{f+1}\\}$ of size $f+1$ we can define the *Lagrange basis* for degree-at-most-$f$ polynomials as follows:

For every $z \in Z$, let $\mathcal{L}_z:Z \mapsto \\{0,1\\}$ be the [indicator function](https://en.wikipedia.org/wiki/Indicator_function) such that:

$$\mathcal{L}_z(x) = \begin{cases} 1,\ \text{if}\ x=z\\0,\ \text{if}\ x \neq z\end{cases}$$

We can then *extend* this function $\mathcal{L}_z(x)$ to a function $L_z : \mathbb{F}_p \mapsto \mathbb{F}_p$, such that for all $x\in Z:\ \mathcal{L}_z(X)=L_z(X)$ by defining $L_z(X)$ as a degree $f$ polynomial!

$$L_z(X)= \frac{\prod_{j \in Z \setminus \{z\}} (X-j)}{\prod_{j \in Z \setminus \{z\}} (z-j)}$$


Take a moment to verify the equality on all $x\in Z$. This seemingly simple idea of [extending](http://people.cs.georgetown.edu/jthaler/IPsandextensions.pdf) a function from $Z \mapsto \\{0,1\\}$ to a low degree polynomial is a very powerful tool! It and its generalization to multivariate polynomials form the basis of [many](https://pdfs.semanticscholar.org/a87d/3febd2e02c41a9b0a4e423089b6677eaef3b.pdf) [results](https://eccc.weizmann.ac.il/report/2017/108/download/) in computer science. 

We can now claim that, for *any* degree $f$ polynomial $p$, we have:

$$p(X)=\sum_{z \in Z} L_z(X) p(z)$$

Why does this equality hold?
It's because both $p(X)$ and $\sum_{z \in Z} L_z(X) p(z)$ are degree-at-most-$f$ polynomials so their difference is also of degree-at-most-$f$ and has $f+1$ zeros, since $|Z|=f+1$.
From the [main theorem in our previous post on polynomials](/2020-07-17-the-marvels-of-polynomials-over-a-field), this means that $p(X)-\sum_{z\in Z} L_z(X) p(z)$ must be the zero polynomial.
Thus, $p(X)=\sum_{z \in Z} L_z(X) p(z)$ follows from the fact that non-trivial degree-at-most-$f$ polynomials have at most $d$ roots!

This argument shows that there is a *unique representation* of $p=(p_0,\dots,p_f)$ for the Lagrange basis induced by $Z=\\{z_1,\dots,z_{f+1}\\}$.
Specifically, this representation is $\left(p(z_1),\dots,p(z_{f+1})\right)$.

Let $\phi(p_0,\dots,p_f) = \left(p(z_1),\dots,p(z_{f+1})\right)$ for $Z=\\{ z_1,\dots,z_{f+1}\\}$. 


**Claim:** $\phi$ is a bijective map from the set of degree-at-most-$f$ polynomials to their evaluations at the points in $Z$, where $\|Z\|=f+1$.

**Proof.** To show that $\phi : \mathbb{F}_p^{f+1} \mapsto \mathbb{F}_p^{f+1}$ is [bijective](https://en.wikipedia.org/wiki/Bijection), it is enough to show that $\phi$'s domain and [image](https://en.wikipedia.org/wiki/Image_(mathematics)) are of the same size and that $\phi$ is [injective](https://en.wikipedia.org/wiki/Injective_function).


Since $\phi$ takes as input degree-at-most-$f$ polynomials with coefficients over $\mathbb{F}\_p$, there are exactly $\|\mathbb{F\_p}\|^{f+1} = p^{f+1}$ such polynomials.
In other words, $\phi$'s domain is $\mathbb{F}\_p^{f+1}$.
Also, since its image is the set of all possible $f+1$ evaluations $(p(z_1),\dots,p(z_{f+1}))$, with each evaluation being an element of $\mathbb{F}\_p$, it follows that $\phi$'s image is exactly $\mathbb{F}\_p^{f+1}$.
Thus, $\phi$'s domain is of the same size as its image.

To show that $\phi$ is injective, assume the opposite.
This means there exist two polynomials $p=(p_0,\dots,p_f)$ and $p'=(p'_0, \dots, p'_f)$ such that $p\ne p'$, but $\phi(p_0, \dots, p_f) = \phi(p'_0, \dots, p'_f)$ which means $p(z)=p'(z),\forall z \in Z$.
Since $|Z|=f+1$, this implies that $p-p'$ is a degree-at-most-$f$ polynomial that has at least $f+1$ zeros.
From the [main theorem of our previous post](/2020-07-17-the-marvels-of-polynomials-over-a-field), this means that $p-p'=0$ and hence $p=p'$.
This is a contradiction.
Therefore, $\phi$ is injective.

We conclude that $\phi$ is bijective. In fact $\phi$ is a [linear isomorphism](https://en.wikipedia.org/wiki/Linear_map) and so $L_{z_1},\dots,L_{z_{f+1}}$ is a [basis](https://en.wikipedia.org/wiki/Basis_(linear_algebra)) for the set of degree-at-most-$f$ polynomials (for any set $Z=\\{z_1, \dots,z_{f+1}\\}$). 

We can now use our new insights to prove the secret sharing properties. 

### Proof of the Secret Sharing properties

**Proof for Binding and Validity**:

Since the adversary is passive, all we need to do is show that indeed all parties will output $s$. Recall that the Reconstruct protocol outputs:

$$p(0)=\sum_{1\leq i \leq f+1} \lambda_i p(i)$$

where

$$\lambda_i = \frac{\prod_{j \in \{1,\dots,f+1\} \setminus \{i\}} j}{\prod_{j \in \{1,\dots,f+1\} \setminus \{i\}} (j-i)}$$

{: .box-warning}
Here, we are restricting ourselves to reconstructing from parties $1,2,\dots, f+1$, but this works for any set of parties $Z\subseteq \\{1,2,\dots,n\\}$ with $\|Z\|=f+1$.

The proof follows directly from the fact that  $p(X)=\sum_{1\leq i \leq f+1} L_i(X) p(i)$ and so $p(0)= \sum_{1\leq i \leq f+1} L_i(0) p(i) = \sum_{1\leq i \leq f+1} \lambda_i p(i) = s$, where $p(i)$ is the share of party $i$.

{: .box-warning}
Recall that the Lagrange polynomial $L_i(X)$ is defined w.r.t. the set of parties $Z$ as $L_i(X)=\prod_{j\in Z\setminus\\{i\\}} \frac{X-j}{i-j}$ and that $\lambda_i = L_i(0)$.

**Proof of Hiding**: 

Let's define the *view* of an adversary that controls the parties $B=\\{b_1,\dots,b_f\\}$ as the messages that the adversary sees during the Share protocol.
In our case, this is just $\\{ p(b_1),\dots,p(b_{f}) \\}$, which are the shares that the parties in $B$ receive from the Dealer during the Share protocol.

To prove the hiding property, we will show that, no matter what the secret $s$ is, the distribution of the view of the adversary is a [uniform distribution](https://en.wikipedia.org/wiki/Discrete_uniform_distribution).

We have shown above that $\phi$ is a bijective mapping from $p_0,\dots,p_{f}$ to $p(z_1),\dots,p(z_{f+1})$ for any set $Z=\\{z_1,\dots,z_{f+1}\\}$. 

**Claim:** For any $Z=\\{z_0, z_1, z_2,\dots,z_f\\}$, $\phi$ maps the uniform distribution $\mathcal{D}$ on $p=(p_0,p_1,\dots,p_{f})$ to the uniform distribution on $p(z_0),p(z_1),\dots, p(z_{f})$.

**Proof:** For *any* $w_0,\dots,w_{f} \in \mathbb{F}\_{p}^{f+1}$, by definition of the uniform distribution we have:

\begin{align}
\label{eq:uniform}
\Pr_{ \mathcal{p \sim D} } \big[(p_0,p_1,\dots,p_f)=(w_0,w_1,\dots,w_f)\big] = 1/|\mathbb{F}_{p}|^{f+1}
\end{align}

We want to show that, $\forall y_0,\dots, y_{f} \in \mathbb{F}\_{p}^{f+1}$:

\begin{align}
\label{eq:claim}
\Pr_{\mathcal{p \sim D}}\big[(p(z_0),p(z_1),\dots,p(z_f))=(y_0,y_1,\dots,y_f)\big] = 1/|\mathbb{F}_{p}|^{f+1}
\end{align}

We can apply the isomorphism $\phi^{-1}$ inside this probability and get:

\begin{align}
   & \Pr_{\mathcal{p \sim D}}\big[(p(z_0),p(z_1),\dots,p(z_f))=(y_0,y_1,\dots,y_f)\big] =\\\\\ 
 = & \Pr_{\mathcal{p \sim D}}\big[\phi^{-1}(p(z_0),p(z_1),\dots,p(z_f))=\phi^{-1}(y_0,y_1,\dots,y_f)\big] =\\\\\
 = &\Pr_{\mathcal{p \sim D}}\big[(p_0,p_1\dots,p_f)=(a_0,a_1,\dots,a_f)\big]
\end{align}

Here, $(a_0,a_1,\dots,a_f) = \phi^{-1}(y_0,y_1,\dots,y_f)$.

Fortunately, we know from Equation $\ref{eq:uniform}$ that, for any $a_0,a_1,\dots,a_f \in \mathbb{F}_p$, $\Pr\_{\mathcal{p \sim D}}\big[(p_0,p_1\dots,p_f)=(a_0,a_1,\dots,a_f)\big] = 1/\|\mathbb{F}\|_p^{f+1}$.
It therefore follows that Equation $\ref{eq:claim}$ holds. 

Now, consider the set $Z=\\{0\\} \cup B$, where $B=\\{b_1,\dots,b_f\\}$ is the set of parties controlled by the passive adversary.
(Here, we use the assumption that party identities start from 1.)

Observe that, since $0 \in Z$, the first output of $\phi$ is $p(0)=p_0$, which matches the first input of $\phi$, which is $p_0$.

From the above observation, we immediately get that for any *fixed* $s=p_0$, $\phi$ must map the uniform distribution on $p_1,\dots,p_{f}$ to the uniform distribution on $p(b_1),\dots,p(b_{f})$.

Since, for any input $s=p_0$, the Dealer uses the uniform distribution to pick the coefficients $p_1,\dots,p_{f}$, then for any input $s$ the *view* of the adversary $p(b_1),\dots,p(b_f)$ is also uniformly distributed!

In what sense does this mean that the adversary learns nothing about the secret $s=p(0)=p_0$? In the sense that, no matter what the secret is, the *distribution of the view* of the adversary is the same and is independent of the actual secret.

In other words, anything the adversary could learn by observing the distribution of its views, it could learn by just sampling from this distribution without any interaction.

### Notes


* The adversary in this post is *passive*, so the main challenge is in the hiding property. The binding propoerty will be less trivial in future posts about stronger adversaries. See our [follow-up post on the Byzantine case](https://decentralizedthoughts.github.io/2022-08-24-BGW-secret-sharing/).
* In the share protocol we rather arbitrarily used the integers from 1 to $n$ as the shares sent to parties 1 to $n$. In fact one can use any fixed set $w_1,\dots,w_n$ of field elements. Since in many cases we want to use [FFT](https://decentralizedthoughts.github.io/2023-09-01-FFT/) it is often beneficial to **use roots of unity** and set $w_i \omega^i$, so party $i$ gets the share $P(\omega^i)$.


Please leave comments on [Twitter](https://twitter.com/ittaia/status/1284267077587677184?s=20).
