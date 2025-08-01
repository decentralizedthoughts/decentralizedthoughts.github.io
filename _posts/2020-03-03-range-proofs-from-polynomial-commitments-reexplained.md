---
title: Range Proofs from Polynomial Commitments, Re-explained
date: 2020-03-03 03:00:00 -05:00
tags:
- cryptography
author: Alin Tomescu
---

This is a re-exposition of [a post here](https://hackmd.io/@dabo/B1U4kx8XI) by _Dan Boneh, Ben Fisch, Ariel Gabizon, and Zac Williamson_, with a few more details on why the polynomial relations hold.

They construct a simple zero knowledge *range proof* from a hiding _polynomial commitment scheme (PCS)_, such as KZG<!--more-->[^KZG10a].

<p hidden>$$
\def\Fp{\mathbb{F}_p}
\def\FF{\Fp^{\scriptscriptstyle{(<n)}}[X]}
\def\polycommit{\mathbf{PolyCommit}}
\def\range#1{[{#1}]}
$$</p>

Specifically, the _prover_ has $z\in \Fp$ and wants to efficiently convince a _verifier_ who only has a commitment of $z$ that $z$ is in the range $0 \leq z < 2^n$. 

They give a novel _honest-verifier zero-knowledge (HVZK)_ range proof which is much more efficient if instantiated with constant-sized polynomial commitments such as KZG[^KZG10a]. 

In this post, we'll refer to this range proof scheme as **BFGW**, according to the authors' last names.

At a high level, the BFGW prover:

 1. Commits to **two** polynomials of degree $(n+1)$
 2. Proves **three** evaluations on one of these polynomials and some other specially-crafted polynomial

Depending on the PCS scheme used, many BFGW instantiations are possible, each with different (trusted) setup assumptions, proof sizes and verification times.
See [the original post](https://hackmd.io/@dabo/B1U4kx8XI) for a discussion on this.

## Notation

 - $\FF$ denotes polynomials in $\Fp[X]$ of degree less than $n$.
 - Assume $n$ divides $p-1$ so as to have _roots of unity_ in $\Fp$.
    + Specifically, $\exists$ a primitive root of unity $\omega \in \Fp$ of order $n$.
 - Let $H = \\{1,\omega,\omega^2,\ldots,\omega^{n-1}\\}$ denote the set of all $n$ $n$th roots of unity.
 - Let $\polycommit(f)$ denote a commitment to a polynomial $f\in \FF$ using the PCS

## Requirements for PCS

Their range proof requires a PCS with the following properties.

 - PCS for polynomials in $\FF$,
 - PCS must be "hiding",
 - PCS must have evaluation binding,
 - PCS evaluation protocol must be HVZK,
    + **Q:** Does KZG have this?
 - PCS must be additively homomorphic.

## The BFGW scheme

Remember that the setting of any range proof scheme is:

 - The prover has $z\in [0,2^n)$,
 - The verifier has a commitment to $z$,
 - The prover wants to convince the verifier **in zero-knowledge** that $z\in [0,2^n)$.

In BFGW, the verifier's commitment to $z$ is done via the PCS itself, rather than a Pedersen commitment.

 - **Q:** How does this affect protocols where $z$ is committed using Pedersen?
 - *A:* Might need to prove (in ZK) that value committed in the Pedersen commitment is the same as in the polynomial commitment

Specifically, a polynomial $f \in \FF$ is picked such that $f(1) = z$ (e.g., $f(X) = z$ is good enough) and the commitment to $z$ is just $\polycommit(f)$

Let $z_0, \ldots, z_{n-1} \in \\{0,1\\}$ be the binary digits of $z$, so that $z = \sum_{i=0}^{n-1} 2^{i} \cdot z_i$.

The prover "encodes" $z$ in a degree-$(n-1)$ polynomial $g \in \FF$ as follows:

\begin{align}
g(\omega^{n-1}) &= z_{n-1}\\\\\
g(\omega^{i}) &= 2 g(\omega^{i+1}) + z_{i}, \forall i=n-2,\ldots,0
\end{align}

Note that $g$ can be computed very fast using an inverse Fast Fourier Transform (FFT).

{: .box-note}
To see why $g(1) = z$, note that:
\begin{align\*}
g(1) &= g(\omega^0)\\\\\
     &= 2 g(\omega^1) + z_0\\\\\
     &= 2 \left(2 g(\omega^2) + z_1\right) + z_0\\\\\
     &= 2^2 g(\omega^2) + 2^1 z_1 + z_0\\\\\
     &= 2^2 \left(2 g(\omega^3) + z_2\right) + 2^1 z_1 + z_0\\\\\
     &= 2^3 g(\omega^3) + 2^2 z_2 + 2^1 z_1 + z_0\\\\\
     &= \dots\\\\\
     &= \sum_{i=0}^{n-1} 2^{i} \cdot z_i = z
\end{align\*}

The prover will send $\polycommit(g)$ to the verifier.

Now, to prove $z$ is in range, the prover need only prove **three conditions** hold:

 1. $g(1) = f(1)$,
 2. $g(\omega^{n-1}) \in \\{0,1\\}$,
 3. $g(X) - 2 g(X \omega) \in \\{0,1\\}, \forall X \in H \setminus \\{\omega^{n-1}\\}$.

As mentioned in [the original post](https://hackmd.io/@dabo/B1U4kx8XI), these three conditions are equivalent to $z$ being in range.
Specifically:

 1. is equivalent to $g(1) = z$
 2. is equivalent to $z_{n-1}$ is a binary digit
 3. is equivalent to $z_i$ is a binary digit, for all $i\in [0, n-1)$  **and** $z = \sum_{i=0}^{n-1} z_i$

{: .box-note}
Note that condition 3 (i.e., $g(X) - 2 g(X \omega) \in \\{0,1\\}$) seems inherently difficult to prove, given just a commitment to $g(X)$.

Next, the prover will prove the three conditions hold by proving the following polynomials evaluate to zero for all $X\in H$:

\begin{align}
w_1(X) &= (g - f) \cdot \left(\frac{X^{n}-1}{X-1}\right),\label{eq:w1}\\\\\
w_2(X) &= g \cdot (1 - g) \cdot \left(\frac{X^{n}-1}{X-\omega^{n-1}}\right),\label{eq:w2}\\\\\
w_3(X) &= \big[g(X) - 2 g(X \omega)\big] \cdot \big[1 - g(X) + 2 g(X \omega)\big] \cdot (X - \omega^{n-1})\label{eq:w3}.
\end{align}

<!-- TODO: Explain X^N - 1 = \prod_i (X-\omega^i) and that the X-1 in the denominator and (X-\omega^{n-1}) cancel out -->

Next, we'll explain why these polynomials being zero over $H$ is equivalent to conditions (1) through (3) holding.

### How do the $w_1,w_2,w_3$ polynomials work?

Note that Equations $\ref{eq:w1}$ through $\ref{eq:w3}$ are using _vanishing polynomials_ that evaluate to zero when $X$ is in a specific subset of $H$.

 - e.g., $\frac{X^{n}-1}{X-1}$ is zero $\forall X = \omega^i$ except for $X = \omega^0 = 1$.
 - e.g., $\frac{X^{n}-1}{X-\omega^{n-1}}$ is zero $\forall X = \omega^i$ except for $X = \omega^{n-1}$.
 - e.g., $X-\omega^{n-1}$ is zero only at $X=\omega^{n-1}$ 

First, let's show that:
$g(1) = f(1) \Leftrightarrow (g-f)\left(\frac{X^n - 1}{X-1}\right) = 0, \forall X\in H$.
Let $h=(g-f)\left(\frac{X^n - 1}{X-1}\right)$.

Let's start with the "$g(1) = f(1) \Rightarrow h(X) = 0$" direction.
Since the vanishing polynomial $\frac{X^n - 1}{X-1}$ is zero at all $X$ in $H\setminus\\{\omega^0\\}$, it follows that $h(X) = 0, \forall X \in H\setminus\\{\omega^{0}\\}$.
Furthermore, since $g(1) = f(1)$, it follows that $h(X)=0$ for $X=1=\omega^0$.
Thus, $h(X) = 0$ for all $X$ in $H$.

For the "$\Leftarrow$" direction, note that since $h(X) = 0, \forall X\in H$ and the vanishing polynomial is zero only for all $X\in H\setminus\\{\omega^0\\}$, it follows that $g(X) - f(X)$ has to be zero at $X=\omega^0$.
So, it follows that $g(1) = f(1)$.

Second, we need to show that $g(\omega^{n-1}) \in \\{0,1\\}\Leftrightarrow g \cdot (1 - g) \cdot \left(\frac{X^{n}-1}{X-\omega^{n-1}}\right) = 0, \forall X\in H$.
This follows from the same reasoning as above, except the vanishing polynomial $\frac{X^{n}-1}{X-\omega^{n-1}}$ vanishes everywhere but $\omega^{n-1}$.

Third, we need to show that:
$g(X) - 2 g(X \omega) \in \\{0,1\\}, \forall X \in H \setminus \\{\omega^{n-1}\\} \Leftrightarrow \big[g(X) - 2 g(X \omega)\big] \cdot \big[1 - g(X) + 2 g(X \omega)\big] \cdot (X - \omega^{n-1}) = 0, \forall X \in H$
The same reasoning applies here too, except the vanishing polynomial $X-\omega^{n-1}$ only vanishes at $X = \omega^{n-1}$.

### Back to the BFGW protocol

The next idea is to reduce proving that $w_1, w_2$ and $w_3$ are zero $\forall X\in H$ to proving that a random linear combination of them is zero $\forall X\in H$.

In other words, the task is reduced to proving:

$$R(X) = w_1(X) + \tau w_2(X) + \tau^2 w_3(X) = 0, \forall X\in H$$

Here $\tau\in \Fp$ is picked uniformly at random **by the verifier**.

The prover divides $R(X)$ by $X^n-1$, which yields a quotient polynomial $q$ and sends $\polycommit(q)$ to the verifier:

$$q(X) = R(X) // (X^n-1).$$

(Here, $//$ denotes a division operator that only yields the quotient.)

The prover's goal is to prove that the following polynomial is zero **everywhere**:

$$w(X) = R(X) - q(X) \cdot (X^n - 1) = w_1 + \tau w_2 + \tau^2 w_3 - q \cdot (X^{n}-1)$$

This is equivalent to proving $R(X) = 0, \forall X\in H$
Looked at differently, $q$ would be a KZG batch proof for $R(X)= 0, \forall X\in H$.

The problem is the verifier cannot check this batch proof because it does not have (and, as far as we can tell, cannot be provably given) a commitment to $R(X)$.

Instead, what the prover *can* do is convince the verifier that $w(X)$ is zero by opening it at a random point $\rho$ chosen by the verifier.

So let's expand $w(X)$ to see what extra information the verifier will need to be given in order to check that $w(\rho)=0$.

First, the verifier knows that:
\begin{align\*}
    w(X) &= w_1(X) + \tau \cdot w_2(X) + \tau^2 \cdot w_3(X) - q(X) \cdot (X^{n}-1)\\\\\
         &= (g(X) - f(X)) \cdot \left(\frac{X^{n}-1}{X-1}\right)\\\\\
         &  + \tau \cdot g(X) \cdot (1 - g(X)) \cdot \left(\frac{X^{n}-1}{X-\omega^{n-1}}\right)\\\\\
         &  + \tau^2 \cdot \big[g(X) - 2 g(X \omega)\big] \cdot \big[1 - g(X) + 2 g(X \omega)\big] \cdot (X - \omega^{n-1})\\\\\
         &  - q(X) \cdot (X^{n}-1)
\end{align\*}

Second, checking that $w(\rho) = 0$ is equivalent to checking that:
\begin{align}
    w(\rho) &= (g(\rho) - f(\rho)) \cdot \left(\frac{\rho^{n}-1}{\rho-1}\right)\label{eq:wrho-start}\\\\\
         & + \tau \cdot g(\rho) \cdot (1 - g(\rho)) \cdot \left(\frac{\rho^{n}-1}{\rho-\omega^{n-1}}\right)\\\\\
         & + \tau^2 \cdot \big[g(\rho) - 2 g(\rho \omega)\big] \cdot \big[1 - g(\rho) + 2 g(\rho \omega)\big] \cdot (\rho - \omega^{n-1})\\\\\
         & - q(\rho) \cdot (\rho^{n}-1) = 0\label{eq:wrho-end}
\end{align}

Note that, with a little help, the verifier can actually check the relation above holds:

 - The verifier has commitments to $f(X)$, $g(X)$ and $q(X)$
 - The verifier can be given $g(\rho)$ and $g(\rho\omega)$ and check them against $\polycommit(g)$, which it has.
 - The verifier can easily compute all the vanishing polynomials evaluated at $\rho$ (e.g., $\frac{\rho^{n}-1}{\rho-1}$) .
 - The verifier knows $\tau$, so it could combine the results if it were given the **few missing pieces of the puzzle.**

The only thing the verifier is missing is a "small chunk" of the equation above.
Specifically, if we let:

\begin{align}
    \hat{w}(X) = f(X) \cdot \left(\frac{\rho^n - 1}{\rho-1}\right) + q(X) \cdot (\rho^n - 1)
\end{align}

...then, the verifier only needs to be given $\hat{w}(\rho)$ to "complete its puzzle" and compute $w(\rho)$.
Importantly, note that the verifier can reconstruct $\polycommit(\hat{w})$ given $\polycommit(f)$ and $\polycommit(q)$, which it has.

To summarize, the verifier is given $g(\rho)$, $g(\rho \omega)$ and $\hat{w}(\rho)$ along with $\rho$ and $\tau$ and this is sufficient to evaluate $w(\rho)$ and check that it is zero. 
This, in turn, ensures that $w(X)=0,\forall X\in\Fp$

{: .box-note}
The prover can actually compute a constant-sized proof for the three evaluations $g(\rho)$, $g(\rho \omega)$ and $\hat{w}(\rho)$, as mentioned in the [original post](https://hackmd.io/@dabo/B1U4kx8XI).

### Time complexities

The computational cost for the prover is:

 - Compute two polynomial commitments, one to $g(X)$ (of degree $n+1$) and one to $q(X)$ (of degree $2n+1$)
    + $g$ has degree $n+1$ when adding ZK
    + $w_1$ has degree $\deg(g) + \deg(\frac{X^n - 1}{X-1}) = (n + 1) + (n - 1) = 2n$ 
        + (assuming $f$ has degree smaller than $g$)
    - $w_2$ has degree $2\deg(g) + \deg(\frac{X^n-1}{X-\omega^{n-1}})=2 n + 2 + n - 1 = 3n + 1$  
    - $w_3$ has degree $2\deg(g) + \deg(X-\omega^{n-1}) = 2n + 3$
    - $R(X)$ has degree $\max(\deg(w_1),\deg(w_2),\deg(w_3))=3n+1$
    - $q(X)=\frac{R(X)}{X^n - 1}$ has degree $2n+1$
 - Evaluate $g(\rho)$, $g(\rho \omega)$ and $\hat{w}(\rho)$,
    - $\deg(\hat{w}(X)) = \deg(q)=2n+1$
 - Use the PCS to prove the evaluations are correct.
    + Quotients in proofs for $g$ have degree $n$
    - Quotient in proof for $\hat{w}$ has degree $2n$

The verifier has to compute the following:

 - Reconstruct a commitment to $\hat{w}(X)$
    + Two exponentiations
 - Verify the three evaluation proofs
    + 6 pairings (can batch)
 - Carry out the operations in Equations \ref{eq:wrho-start} to \ref{eq:wrho-end} to check $w(\rho)=0$
    - Several field operations (cheap)

## A few notes

{: .box-note}
The protocol above is interactive, but can be made non-interactive using the Fiat-Shamir[^FS87] transform.

{: .box-note}
Why not use a KZG batch proof to prove that $R(X) = 0, \forall X\in H$: i.e., a commitment to a polynomial $q(X)$ such that $R(X) = q(X) \cdot (x^n - 1)$.
My guess is BFGW doesn't take this route because the verifier doesn't have a commitment to $R(X)$.
If the verifier were given commitments to $w_1, w_2$ and $w_3$ that he can verify against a commitment to $g(X)$, then he could verify the commitment to $R(X)$.
However, verifying a commitment to $w_3$ seems difficult.

### References

[^KZG10a]: **Constant-Size Commitments to Polynomials and Their Applications**, by Kate, Aniket and Zaverucha, Gregory M. and Goldberg, Ian, *in ASIACRYPT '10*, 2010
[^FS87]: **How To Prove Yourself: Practical Solutions to Identification and Signature Problems**, by Fiat, Amos and Shamir, Adi, *in Advances in Cryptology --- CRYPTO' 86*, 1987
