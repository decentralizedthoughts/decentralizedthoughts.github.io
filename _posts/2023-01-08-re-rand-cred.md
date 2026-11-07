---
title: Pairing-based Anonymous Credentials and the Power of Re-randomization
date: 2023-01-08 04:00:00 -05:00
tags:
- privacy
- randomness
author: Ittai Abraham and Alin Tomescu
---

David Chaum [wrote in 1985](https://www.cs.ru.nl/~jhh/pub/secsem/chaum1985bigbrother.pdf):
>Large-scale automated transaction systems are imminent. The architecture chosen for these systems may have a long-term impact on the centralization of our economic system, on some of our basic liberties, and even on our democracy. The initial choice of direction will gather economic and societal momentum, making reversal increasingly less likely.

In this post, we highlight one of the main ideas in [[Chaum, 1985]](https://www.cs.ru.nl/~jhh/pub/secsem/chaum1985bigbrother.pdf), that of **anonymous credentials**. In a standard *credential*  system there are three entities with the following use case: 
1. **Issuers**, that given a vector of values can create a *credential* for it. For example, a nation may issue a credential indicating that Alice was born in 1994. 
2. **Users**, that given credentials on values can generate: *statements* about the values, and accompanying *proofs*. For example, Alice can state that _"I have a valid credential that indicates I am at least 21 years old"_ and provide a proof. 
3. **Verifiers**, that given a statement and a proof can verify if indeed there exists a vector of values with a credential for which this statement is true. 

The obvious solution to the problem above is to use **digital signatures**. 
* An Issuer can sign on the data, and hand a credential that includes the data, "Alice was born in 1994", and a signature by the issuer on the data. 
* A User can send the credential (the data with the signature) and the statement to the Verifier. 
* A Verifier first checks the validity of the credential (that the data has a valid signature from the issuer); and then that the statement is true given the data..

This is the type of solution that Chaum wanted to avoid! The obvious problem with this approach is that *way too much* information is revealed to the Verifier! 

In the above example, Alice just wanted to reveal she is above 21, but she revealed a lot more: the fact that her name is Alice and her exact year of birth. Moreover, there is an underlying linkability problem: every time Alice shows a credential, it is the *same credential*, so her statements can be linked to each other.

Over the last 30+ years there have been several approaches to solve this problem, with different trade-offs. In this post we focus on a specific path that uses **anonymous credentials**, first formally defined and constructed by [Camenisch and Lysyanskaya, 2001](https://groups.csail.mit.edu/mac/classes/6.805/articles/privacy/anon-credentials.pdf).

## Anonymous credentials

Anonymous credential can be built out of non-interactive zero-knowledge arguments [NIZK](https://en.wikipedia.org/wiki/Non-interactive_zero-knowledge_proof)s and **re-randomization**. In this post we focus on the re-randomization and do not cover the details related to NIZK (which we plan to cover in future posts).


As in a standard credential system, *issuers*, given a vector of values can create a *credential* for it. In fact, more complicated forms of issuance are possible where the issuer does not need to fully know what it's signing on (we will cover this in later posts).

When a user holds a credential and wants to prove a *statements* about its underlying values:

It first creates a new credential on the same data. This new credential looks completely random. That's why the operation of taking the credential and creating a new one out of it is called **re-randomizing the credential**. This requires a special type of credential, one that allows users to create new credentials on the same data without the issuer's help!


The user then send this new (re-randomized) credential to the Verifier, along with a statement about the content of the new credential. In particular, this statement can be a [NIZK](https://www.cs.umd.edu/~jkatz/gradcrypto2/NOTES/lecture13.pdf).

The Verifier, first checks the validity of the certificate; and then checks the truth of the statement relative to this certificate. Privacy is now preserved: the Verifier cannot learn anything other than the truth of the statement from the NIZK and cannot link the new credential to any previous credential!

## A construction of anonymous credentials

In this post we show how to construct a **re-randomizable** credential from [pairing-based cryptography](https://alinush.github.io/2022/12/31/pairings-or-bilinear-maps.html). An example of this for anonymous coin credentials can be found in our [UTT paper](https://eprint.iacr.org/2022/452.pdf) and [implementation](https://github.com/vmware/concord-bft/tree/master/utt).

We describe these re-randomizable credentials in 4 steps:
1. Introduce *Pedersen commitments*, which are re-randomizable.
2. As we work over pairing-friendly groups, extend Pedersen commitments to *Dual commitments*. 
3. Introduce the re-randomizable signature scheme of *Pointcheval and Sanders*.
4. Finally, show how easy it is to re-randomize both the commitment and the signature!



### 1. Committing to a vector of values
Fixing a finite field $\mathbb{F}$, you are given a vector of values $\vec{m}=\langle m_1, \dots, m_\ell\rangle \in \mathbb{F}^\ell$. An elegant and succinct way to commit to $\vec{m}$ is via a [Pedersen commitment](https://link.springer.com/content/pdf/10.1007/3-540-46766-1_9.pdf).

Pedersen commitment uses a group $\mathbb{G}$ of large prime order, a uniformly random generator $g$ and $\ell$ secret field elements $\langle y_1,\dots,y_\ell\rangle \in \mathbb{F}^\ell$.


To setup the scheme a **commitment key** is created, which is denoted as $\mathbf{ck} = (g, \vec{\mathbf{g}} = \langle g_1 , \dots ,g_\ell\rangle)\in \mathbb{G}^{\ell +1 }$, where $g_i= g^{y_i}$ for each $1\le I\le \ell$.

We use a subroutine $\mathsf{Rand}(\mathbb{F})$ that returns a field element picked uniformly at random.

A *Pedersen commitment* to vector $\vec{\mathbf{m}}$ is computed as:

$$r \gets \mathsf{Rand}(\mathbb{F})$$

$$cm \gets g^r \prod_{1\le i\le \ell} g_i^{m_i}$$

and denote this operation as

$$cm \gets \mathsf{Commit}([m_1,\dots,m_\ell]; r)$$

Pedersen commitments have amazing properties: 
* **Perfectly Hiding**: the commitment leaks no information about $\vec{\mathbf{m}}$, in fact it is uniformly distributed in $\mathbb{G}$.
* **Computationally Binding**: under the hardness of the [discrete log](https://en.wikipedia.org/wiki/Discrete_logarithm) assumption you cannot find $\vec{\mathbf{m}} \neq  \vec{\mathbf{m}}'$ and $r,r'$ such that $\mathsf{Commit}(\vec{\mathbf{m}}; r) = \mathsf{Commit}(\vec{\mathbf{m}}'; r')$
* **Re-randomizable**: given a commitment $cm$, anyone can generate a new commitment $cm'$ such that:
    * the new commitment is also bound to $\vec{\mathbf{m}}$
    * the new commitment is uniformly, independently distributed in $\mathbb{G}$ (in particular, independent of $cm$)

Re-randomization of a Pedersen commitment is easy:

$$
r' \gets \mathsf{Rand}(\mathbb{F})\\
cm' \gets cm \cdot g^ {r'}
$$

and denote this operation as

$$
cm' \gets \mathsf{CM.Rerand}(cm; r')
$$

Observe that $cm'= \mathsf{Commit}(\vec{\mathbf{m}}; r+r')$ and the re-randomization above is a special case of a more general property:

* **Homorphism**: given  $cm_1 = \mathsf{Commit}(\vec{\mathbf{m_1}}; r_1)$ and $cm_2 = \mathsf{Commit}(\vec{\mathbf{m_2}}; r_2)$, one can simply multiply them and get:

$$ cm_1\cdot cm_2= \mathsf{Commit}(\vec{\mathbf{m_1}}+\vec{\mathbf{m_2}}; r_1+r_2). $$


### 2. Dual commitments



We will be working over pairing-friendly groups $\mathbb{G},\widetilde{\mathbb{G}}$ and $\mathbb{G}_T$. See this post for [more about pairings](https://alinush.github.io/2022/12/31/pairings-or-bilinear-maps.html). The important fact about pairing-friendly groups, is the existence of a map $ e: \mathbb{G} \times \widetilde{\mathbb{G}} \to \mathbb{G}_T $ such that for any elements $a \in \mathbb{G}, \widetilde{a} \in \widetilde{\mathbb{G}}$ and field elements $x,y \in \mathbb{F}$:

$$
e(a^x,\widetilde{a}^y)=e(a,\widetilde{a})^{xy}
$$


Given this, it will be beneficial to use dual commitments computed over both $\mathbb{G}$ and $\widetilde{\mathbb{G}}$ that have a *correlated* base.

So, instead of having just $\ell+1$ generators in $\mathbb{G}$ that are derived from $ g \in \mathbb{G} $ and the $\ell$ secret field elements in $\vec{\mathbf{y}}$, also choose a random generator $\widetilde{g}$ in $\widetilde{\mathbb{G}}$ and use an additional $\ell+1$ generators in $\widetilde{\mathbb{G}}$ denoted $ (\widetilde{g}, \vec{\mathbf{\widetilde{g}}} = \langle \widetilde{g_1},\dots,\widetilde{g_\ell}\rangle)$.

Just as $g_i=g^{y_i}$, also set $\widetilde{g_i}=\widetilde{g}^{y_i}$.

Given these dual bases, a commitment for $\vec{\mathbf{m}}$:

$$
r \gets \mathsf{Rand}(\mathbb{F})
$$

$$
cm \gets g^r \prod_{1\le i\le \ell} g_i^{m_i}
$$

$$
\widetilde{cm} \gets \widetilde{g}^r \prod_{1\le i\le \ell} \widetilde{g}_i^{m_i}
$$


and denote this operation as:

$$
(cm, \widetilde{cm}) \gets \mathsf{DualCommit}([m_1,\dots,m_\ell]; r)
$$



Clearly, any dual commitment $(cm,\widetilde{cm})$ can be *re-randomized* to $(cm',\widetilde{cm}')$:

$$
r' \gets \mathsf{Rand}(\mathbb{F})\\
cm' \gets cm \cdot g^ {r'} \\
\widetilde{cm}'  \gets \widetilde{cm}\cdot \widetilde{g}^{r'} 
$$

Finally, to make sure that a dual commitment $(cm,\widetilde{cm})$ is **valid**, meaning both the $\mathbb{G}$ and $\widetilde{\mathbb{G}}$ components commit to the same message $\vec{\mathbf{m}}$, you can check that:

$$
e(cm,\widetilde{g})=e(g,\widetilde{cm})
$$


### 3. Re-randomizable signatures

We now show a way to create a signature scheme that allows signing dual Pedersen commitments computed under the **commitment key**  $\mathbf{ck}=\langle g,\vec{\mathbf{g}}, \widetilde{g}, \vec{\mathbf{\widetilde{g}}}\rangle$ from above.

We use the *re-randomizable signature (RS) scheme* by [Pointcheval and Sanders](https://eprint.iacr.org/2015/525.pdf)[^PS16].

Given two uniformly random generators $g \in \mathbb{G}$, $\widetilde{g} \in \widetilde{\mathbb{G}}$, the scheme uses a secret key consisting of $\ell+1$ field elements $(x,\vec{\mathbf{y}} = \langle y_1,\dots,y_\ell \rangle)\in \mathbb{F}^{\ell+1}$.

The public key consists of (1) a **verification key**

$$
vk = \widetilde{X} = \widetilde{g}^x \in \widetilde{\mathbb{G}}
$$ 

and (2) the commitment key $\mathbf{ck}$ from above, consisting of $2 \ell+2$ group elements:

$$
\mathbf{ck} = \langle g,\vec{\mathbf{g}}, \widetilde{g}, \vec{\mathbf{\widetilde{g}}} \rangle \in \mathbb{G} \times \mathbb{G}^\ell \times \widetilde{\mathbb{G}}\times \widetilde{\mathbb{G}}^\ell
$$

Where $g_i=g^{y_i}$ and $\widetilde{g}_i=\widetilde{g}^{y_i}$ for each $1\le i \le \ell$


To sign a dual commitment, we compute a secret key: 

$$
sk = X = g^x \in \mathbb{G}
$$

and only sign the $cm$ part as:

$$
u \gets \mathsf{Rand}(\mathbb{F})
$$

$$
\sigma = \mathsf{RS}.\mathsf{Sign}_{\mathbf{ck}}(sk, cm; u) \stackrel{\mathsf{def}}{=} (g^u, (sk \cdot cm)^u) \stackrel{\mathsf{def}}{=} (\sigma_1, \sigma_2)
$$

Crucially, the commitment $cm$ must be computed under the same  $\mathbf{ck}$ commitment key from the verification key above.

To verify a signature $\sigma=(\sigma_1,\sigma_2)$ for a dual commitment $(cm,\widetilde{cm})$, the  verification algorithm $\mathsf{RS}.\mathsf{Verify}_{\mathbf{ck}}(vk, (cm,\widetilde{cm}), \sigma)$ needs $\widetilde{cm}\in\widetilde{\mathbb{G}}$ and, of course, the *verification key* $vk =\widetilde{X}$.


The verification algorithm checks that $\sigma_1 \neq 1_{\mathbb{G}}$ and that:

$$
e(\sigma_1, \widetilde{X}\cdot \widetilde{cm})=e(\sigma_2, \widetilde{g})
$$

It is crucial not to reuse the same value $u$ for two different signatures, which would lead to a forgery.


### 4. Re-randomizing a credential

Given a credential $c$ that consists of a commitment $cm$ with a signature $\sigma$ we would like to re-randomize $c$ into a new credential $ c' $ that could not be linked back to $c$.

This is done by *re-randomizing* $\sigma$ into a new signature $\sigma'$ on a re-randomized commitment $cm'$ defined below:

$$
cm'= \mathsf{CM.Rerand}(cm; r')
$$

via 

$$
\sigma' = \mathsf{RS.Rerand}(\sigma, r', u')
$$

as follows:

$$
r' \gets  \mathsf{Rand}(\mathbb{F})
$$

$$
cm' \gets  \mathsf{CM.Rerand}(cm; r') = cm \cdot g^{r'}
$$

$$
\widetilde{cm'} \gets \mathsf{CM.Rerand}(\widetilde{cm}; r') = \widetilde{cm} \cdot g^{r'}
$$

$$
u' \gets \mathsf{Rand}(\mathbb{F})
$$

$$
\sigma_1' \gets (\sigma_1)^{u'}
$$

$$
\sigma_2' \gets \left(\sigma_2 \cdot (\sigma_1)^{r'}\right)^{u'}
$$



As a consequence, a signer cannot link the old, known credential $(cm,\sigma)$ with the fresh, re-randomized credential $(cm',\sigma')$.

However, note that $(cm',\sigma')$ verifies for $\vec{\mathbf{m}}$ because $\mathsf{RS.Verify}_\mathbf{ck}(vk, (cm', \widetilde{cm}'), \sigma')$ still passes: 

$$ 
e \left(\sigma_1', \widetilde{X}\cdot \widetilde{cm'}\right) 
= e\left(\sigma_2', \widetilde{g}\right) \Leftrightarrow\\
%
e\left(\sigma_1^{u'}, \left(\widetilde{X} \cdot \widetilde{cm} \cdot \widetilde{g}^{r'}\right)\right) = e\left( (\sigma_2 \cdot (\sigma_1)^{r'})^{u'}, \widetilde{g}\right)\Leftrightarrow\\
%
e\left(\sigma_1, \left(\widetilde{X} \cdot \widetilde{cm} \cdot \widetilde{g}^{r'}\right)\right) = e\left( \sigma_2 \cdot (\sigma_1)^{r'}, \widetilde{g}\right)\Leftrightarrow\\
%
e\left(\sigma_1, \widetilde{X} \cdot \widetilde{cm} \right) e\left(\sigma_1, \widetilde{g}^{r'}\right) = e\left(\sigma_2, \widetilde{g}\right)\cdot e\left((\sigma_1)^{r'}, \widetilde{g}\right)\Leftrightarrow\\
%
e\left(\sigma_1, \widetilde{X} \cdot \widetilde{cm} \right)  = e\left(\sigma_2, \widetilde{g}\right)
$$

Note that this last equation is exactly the verification equation of the original signature $\sigma$ on $(cm,\widetilde{cm})$ before re-randomization.

In other words, we proved that the re-randomized $\sigma'$ verifiers if and only if the original $\sigma$ verifies:

$$\mathsf{RS.Verify}_\mathbf{ck}(vk, (cm', \widetilde{cm}'), \sigma') = 1\Leftrightarrow \mathsf{RS.Verify}_\mathbf{ck}(vk, (cm, \widetilde{cm}), \sigma) = 1$$




[^PS16]: **Short Randomizable Signatures**, by Pointcheval, David and Sanders, Olivier, *in CT-RSA 2016*, 2016