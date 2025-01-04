---
title: The BGW Verifiable Secret Sharing Protocol
date: 2022-08-24 08:00:00 -04:00
tags:
- secret sharing
author: Ittai Abraham and Gilad Asharov
---

In this post, we present the classic [Ben-or, Goldwasser, and Wigderson, 1988](https://inst.eecs.berkeley.edu/~cs276/fa20/notes/BGW88.pdf) (**BGW**) Verifiable Secret Sharing protocol (**VSS**) with the simplifications of [Feldman, 1988](https://dspace.mit.edu/handle/1721.1/14368). The analysis and notation in this post are based on the full proof of the BGW MPC protocol of [Asharov and Lindell](https://eprint.iacr.org/2011/136.pdf). This post is a continuation of our previous posts on secret sharing for [passive](https://decentralizedthoughts.github.io/2020-07-17-polynomial-secret-sharing-and-the-lagrange-basis/) and [crash](https://decentralizedthoughts.github.io/2022-08-17-secret-sharing-with-crash/) failures.

Consider a **malicious adversary** controlling at most $f$ parties. The only restriction on the adversary is that honest parties have **private channels**: the adversary cannot see the content of messages sent between any two honest parties.

For simplicity, we abstract consensus and broadcast away, and assume parties have access to a **Broadcast channel**. We will discuss the challenges and concrete costs of broadcast in more detail in later posts. Note for now that broadcast [requires](https://decentralizedthoughts.github.io/2019-08-02-byzantine-agreement-is-impossible-for-$n-slash-leq-3-f$-is-the-adversary-can-easily-simulate/) to assume $f<n/3$.  

### Verifiable Secret Sharing properties

A *secret sharing scheme* is composed of two protocols: *Share* and *Reconstruct*. These protocols are run by the $n$ parties. A designated *dealer* has a *secret* $s$ in a commonly known finite field $\mathbb{F}_p$ with $p>n$, which is given as *input* to the Share protocol. The adversary is malicious - and corrupted parties are not guaranteed to follow the protocol specification. A secret sharing protocol that tolerates such adversaries is called **verifiable secret sharing (VSS)**. 
The three properties of VSS:

1. **Validity**: If the dealer is honest, the output of the Reconstruct protocol is the dealer's input value $s$.
2. **Hiding**: If the dealer is honest and no honest party has begun the Reconstruct protocol, then the adversary can gain no information about $s$.
3. **Binding**: At the end of the Share protocol, the output of the Reconstruct protocol is well-defined. Namely, there exists an (efficient) algorithm that takes the view of the honest parties in the end of the Share protocol and outputs a value $s$ such that, when parties later execute the Reconstruction protocol, the output will be $s$. 


Note that the binding property forces a malicious dealer to **fix** its shared value by the end of the Share protocol. 

We also need termination properties:

1. **Termination of Share**: if an honest party completes the Share protocol then all honest parties complete the Share protocol.
2. **Termination of Reconstruct**: if all honest parties complete the Share protocol and all honest parties start the Reconstruct protocol then all honest parties complete the Reconstruct protocol.

### The main idea

There are 5 challenges VSS needs to solve:

1. What if during the Reconstruct protocol the corrupted parties send incorrect shares? The solution is to uniquely interpolate with errors by using  [Reed Solomon error correction](http://cyber.biu.ac.il/wp-content/uploads/2020/02/Threshold-Secret-SharingToPublish.pdf). To overcome $f$ errors of a degree $f$ polynomial with unique decoding requires at least $2f+1$ correct shares. Hence VSS requires $n>3f$ and that all honest parties have the correct share (assume $n=3f+1$ for this post).
2. What if a malicious dealer sends shares to some honest parties, but not to all of them? The BGW approach is to enable the honest parties that are missing their share to publicly broadcast a *complaint*, asking for their shares. The dealer will need to publicly broadcast these shares.
3. What if a malicious dealer sends inconsistent shares to the honest parties? Inconsistent shares imply that the shares held at the honest parties form a polynomial of degree higher than $f$. This will lead to failure of unique interpolation during Reconstruct. The BGW solution is to prove that the sharing is of degree at most $f$ by an interactive distributed zero knowledge protocol. The insight is to share a bi-variate polynomial of degree at most $f$ in each variable:
Instead of sharing some degree-$f$ polynomial $g(x)$, the dealer shares a bi-variate polynomial $p(x,y)$ such that $p(x,0)=g(x)$, by sharing the $i$th row and $i$th column to party $i$. That is, party $P_i$ receives both $p(x,i)$ and $p(i,y)$. Now every two parties $i,j$ can *privately* exchange $p(i,j)$ and $p(j,i)$. On the one hand, this reveals no new information about $g(x)$ - this is the perfect zero knowledge part. On the other hand, if *all* honest parties $i,j$ agree on $p(i,j)$ and $p(j,i)$ then this is a *proof* that the dealer shared a degree at most $f$ bi-variate polynomial.
4. But what if some pairs of parties disagree on the privately exchanged points? The BGW solution is to have parties publicly broadcast a *complaint* and to have the dealer broadcast a *resolution* making the row and column of the parties *public*. 
5. Finally, what if the resolution by the dealer is inconsistent with the private shares of honest parties? parties check that their private values are consistent with the public values and that the dealer responded to all complaints. If enough honest parties broadcast $\langle 1\rangle$ then BGW prove that even a malicious dealer must have uniquely fixed the reconstruct value at the end of the Share protocol.  


### The BGW secret sharing protocol (VSS)

The **Share protocol** has five rounds: share, exchange sub-shares, publicly complain, publicly resolve, and publicly accept.

1. **Dealer sends rows and columns**: The dealer, given $s$, uniformly chooses coefficients $a_{i,j}$ for all $i,j \in \{0,\dots, f\}$ except for $a_{0,0}$.
    It defines a bi-variate polynomial of degree at most $f$:
    
    $$
    p(x,y) = s + \sum_{(i,j) \in \{0,\dots,f \}^2\mid(i,j) \neq (0,0)} a_{i,j} x^i y^j .
    $$
    
    It defines projection univariate polynomials: $row_i(x)=p(i, x)$ and $col_i(x)=p(x, i)$, and sends each party $i$ the two polynomials $\langle row_i(x), col_i(x)\rangle$.
    If a party does not receive a valid message, it sets its value to 0.
1. **Parties exchange sub-shares**: Each party $i$ sends each party $j$ the two values $\langle row_i(j)$, $col_i(j)\rangle$.
   
2. **Parties publicly complain**: If a party $i$ receives a pair from party $j$ that is different than its share, it **broadcasts** a complaint with 4 values $\langle i,j,row_i(j), col_i(j)\rangle$.
3. **Dealer publicly resolves complaints**: if the dealer hears a complaint from party $i$ that does not agree with $p(x,y)$ then it **broadcasts** $\langle row_i(x), col_i(x)\rangle$ of the row and column of party $i$. We call party $i$ *public*.
4. **Parties publicly accept**: if a non-public party $i$: (1) has row and column shares that agree with all the public parties values and all the non-public parties complaint values; (2) for each two parties $j,k$ with disagreeing complaints, at least one of them is public, then it is *happy* and **broadcasts** $\langle 1 \rangle$. Otherwise it **broadcasts** $\langle 0\rangle$. 

   If less than $2f+1$ parties broadcast $\langle 1\rangle$ then set your shares $row_i(x), col_i(x)$ to be zero.


The **Reconstruct protocol** is just robust univariate interpolation using the public values:

1. Each non-public party $i$ sends $\langle col_i(0) \rangle$ to all parties. 
2. Each party interpolates a degree at most $f$ polynomial with at most $f$ errors using the values  $col_1(0),\dots, col_n(0)$, where $col_j(0)$ uses the public value if party $j$ is *public*, or the value party $j$ sent during reconstruct otherwise. If a non-public party sends nothing you can interpret this as 0. 

### Proof of Validity (when the dealer is honest)

Since the dealer is honest, no two honest parties will complain on each other. 

If a corrupt party complains about an honest party or vice versa, then the honest dealer will agree with the honest party so only the corrupt party may become public. Moreover, these two points $p(i,j), p(j,i)$ are already known to the adversary from the dealer so the adversary learns no new information.

Finally, if two corrupt parties complain about each other, then the adversary learns no new information and they may become public.

So in the end of the Share protocol, all honest parties will remain non-public and will agree with each other privately and agree with the public values. If a pair of corrupted parties send conflicting values, at least one of them will become public. Hence all honest parties will broadcast $\langle 1\rangle$.

The validity of the Reconstruct protocol follows from the fact that the $n-f \geq 2f+1$ honest parties are enough to error correct any $f$ errors.

### Proof of Hiding (when the dealer is honest)

The polynomial $p(x,y)$ contains $(f+1)^2$ coefficients, $f^2+2f$ are chosen uniformly at random, and $1$ is the secret. Thus, the dealer has $f^2+2f$ degrees of freedom. The adversary view has $f^2$ points from each pair $i,j$ that the adversary controls, another $f$ points for each of the rows, and another $f$ points for each of the columns - for a total of $f^2 +2f$ points.

As in the univariate case, for any $s$, conditioned on $p(0,0)=s$, there is a one-to-one mapping between these spaces. This follows since any non-trivial bi-variate polynomial of degree at most $f$ cannot have $f+1$ rows (or $f+1$ columns) that are univariate roots - their projection is the zero (trivial) univariate polynomial. 


The one-to-one mapping means that for any secret $s$, the dealer's uniform distribution over the remaining $f^2+2f$ degrees of freedom induces a uniform distribution over the adversary view. 

So the view of the adversary reveals nothing about $s$. Note that whenever the honest dealer publicly reveals some polynomial, it is a polynomial that is already known to the adversary and the adversary learns nothing new when resolving the complaints. 

<details>
  <summary><b>More proof details</b>:</summary> <p>
  
  
  Fix a set $I \subset N$ such that $|I|=f$ are the parties controlled by the adversary. Let $V_I=\{p(i,j) \mid i,j \in I\} \cup \{ p(0,i), p(i,0) \mid I \in I\}$ and observe that $V_I$ completely defines the view of the adversary and that $|V_I|=f^2+2f$.
  
  
Observe that a bi-variate polynomial where each variable has degree at most $f$ has $(f+1)^2$ coefficients.


Fix a secret $s$ and consider the function $\phi: \mathbb{F}^{f^2+2f} \to V_I$ that maps the remaining coefficients of $p$ to the points that the adversary sees. The domain and co-domain have equal cardinality. So in order to prove that $\phi$ is one-to-one all we need is to prove that $\phi$ is a bijection.


Assume that $\phi( \vec{a} )=\phi( \vec{b} )$, and consider the bi-variate polynomial $p'$ of degree at most $f$ with coefficients $0, ( \vec{a} - \vec{b} )$. For any $j \in I \cup \{0\}$, consider the univariate polynomial $p'(j,x)$. Observe that for any $i\in I$ we have $p'(j,i) = 0$ (because $\phi( \vec{a} ) = \phi( \vec{b} )$). Hence $p'(j,x)$ is the zero polynomial.
Similarly, for any $j \in I \cup \{0\}$, $p'(x,j)$ is the zero polynomial.


Now consider any $k$ and the univariate polynomial $p'(k,x)$. Since $p'(k,i)=0$ for all $i\in I \cup \{0\}$, it follows that $p'(k,x)$ is the zero polynomial.
Similarly, $p'(x,k)$ is the zero polynomial.


Hence $p'$ is the zero polynomial, so $a=b$, and therefore $\phi$ is a bijection.



Since $\phi$ is one-to-one, then for any secret $s$, the  uniform distribution on the $f^2+2f$ remaining coefficients induces a uniform distribution on $V_I$. 
</p></details>

### Proof of Binding (when the dealer is corrupt)

In this case consider the set $G$, consisting of the first $f+1$ honest parties that broadcast $\langle 1\rangle$.

We will show that the rows and columns of the parties in $G$ define a unique bi-variate polynomial $g(x,y)$ of degree at most $f$ such that $g(0,0)$ is the binded value.


Indeed, observe that the parties in $G$ define $(f+1)^2$ points from each pair $i,j \in G$. Consider the unique polynomial $g(x,y)$ induced by these points, we will show that all honest parties and all public resolutions agree with $g(x,y)$ and hence it is as if the dealer was honest and shared $g(x,y)$ (but may have caused honest parties to be public).

Clearly, $g(x,y)$ agrees with all the points of all the parties in $G$. 

If an honest party $\notin G$ agrees with all the sub-shares of all the $f+1$ parties in $G$ then this party must agree with $g(x,y)$ as well.

If an honest party $j$ received shares conflicting with sub-shares of parties in $G$, it will complain, and since the $f+1$ parties in $G$ sent $\langle 1\rangle$, it must be that the dealer resolution made $j$ public and this public information must agree with $g(x,y)$ as well.

So given that the $f+1$ honest parties in $G$ sent $\langle 1\rangle$, it is as if the malicious dealer is acting in a way that is consistent with a dealer that honestly shares $g(x,y)$ to honest non-public parties and publicly resolved all remaining parties consistent with $g(x,y)$.

In particular, all honest parties are either: non-public and agree with $g$ or public and agree with $g$. So there are at least $n-f\geq 2f+1$ honest parties (some may be public) and at most $f$ corrupt non-public parties. Hence no matter what the corrupt parties send during Reconstruct protocol, robust interpolation with error correction will uniquely reconstruct $g(x,y)$ with the secret being $g(0,0)$.

### Notes

*Complexity*: in the Share protocol, the dealer first sends $O(n)$ words to each party. In the second round, each party privately sends $O(n)$ words. In the public complain round, each party broadcasts at most $O(n)$ words. In the resolve round, the dealer broadcasts at most $O(n^2)$ words. Finally in the fifth round, each party broadcasts one word.

Total of $O(n^2)$ words in private channels and $O(n^2)$ words of broadcast for the Share protocol. Note that $O(n^2)$ words of broadcast requires at least $O(n^3)$ words to be received overall. 


  
*Open question*: can the worst case word complexity of VSS Share protocol in this setting be reduced to  $o(n^3)$ received words?

*Good case complexity*: if all parties are honest, then we can use [two rounds of silence](https://arxiv.org/abs/1805.07954) to replace the broadcast protocol to indicate the public complain round is empty which implies that the protocol can be optimized to use just two rounds of $O(n^2)$ words followed by two rounds of silence. 
 
 
-*Future posts* on VSS: we will explore how VSS is the gateway to full MPC, benefits of VSS in the computational setting, how VSS works in asynchrony, how to pack many secrets in a single VSS, and much more.

#### Acknowledgements

We would like to thank Gilad Stern for insightful comments and feedback.



Comments on [Twitter](https://twitter.com/ittaia/status/1562449944853614593?s=20&t=5Tmd0Wj6UZtg2ntYgIIHkw).
