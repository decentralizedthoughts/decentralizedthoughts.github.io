---
title: Simple Payment Systems with Unlinkability
date: 2026-01-21 02:00:00 -05:00
author: Ittai Abraham, Gilad Stern, and Alin Tomescu
---


In this post, we discuss payment systems. There is a set of *users* who wish to pay each other.

1. We start with perhaps the simplest form, which is based just on [digital signatures](https://alinush.github.io/signatures) and a single *bank*. 
2. We then show how the bank can be implemented as a fault tolerant distributed system with $n$ servers.
3. Finally, we show a modern version of [ecash](https://chaum.com/wp-content/uploads/2022/01/Chaum-blind-signatures.pdf), where [blind signatures](https://decentralizedthoughts.github.io/2026-01-21-blind-and-threshold/) are used to obtain an important privacy property that hides the transaction flow. This property is called **unlinkability**.

## Single Bank, Public, Interactive Payments

The bank generates a key-pair: a secret key $s$ and a public key $PK$ known by everyone.


### System Model and Intuition

Tokens are the coins of the system. Each token represents exactly one unit of value and consists of a fresh public key together with a bank signature on that key. Ownership of a token is defined by knowledge of the corresponding secret key.

Each token is associated with a one-time signing key pair. When a token is spent, its key is permanently invalidated and never reused. The recipient receives a completely new token associated with a fresh public key.

The bank does not maintain accounts or balances. Its only persistent state is a set of public keys that have already been spent, called the nullifier set. Spending a token means proving ownership of its key, adding that key to the nullifier set, and issuing a new signed key for the recipient.

Formally, the bank maintains a set $N$ of spent public keys. Initially $N$ is empty.

A token $T$ is a pair $(P, \sigma)$ where $P$ is a public key and $\sigma = \textsf{Sign}(s, P)$ is a digital signature of $P$ under the bank’s secret signing key $s$. So $\textsf{Verify}(PK, P,\sigma)=1$.

A token $T=(P,\sigma)$ is *unspent* relative to a nullifier set $N$ if $P \notin N$.

### Payment protocol

Suppose Alice has a signing key $sk_a$ with associated public key $PK_a$ (i.e., a **signing key pair**) and a token $(PK_a, \sigma_a)$ and wants to pay Bob: 

1. Bob samples a new signing key pair $(sk_b, PK_b)$ and sends $PK_b$ to Alice.
2. Alice proves ownership of the token by signing a **transaction** $((PK_a,\sigma_a), PK_b)$ using her signing key $sk_a$, producing a signature $\tau_a \leftarrow \textsf{Sign}(sk_a, (PK_a,\sigma_a), PK_b)$.
3. Alice sends the transaction and its signature $((PK_a,\sigma_a), PK_b, \tau_a)$ to the bank.
4. The bank checks that it indeed issued the token, that it is unspent, and that the payer is authorized to spend it:

    * The token is issued by the bank: $\textsf{Verify}(PK, PK_a,\sigma_a)=1$
    * The token is unspent: $PK_a \notin N$
    * The transaction is authorized: $\textsf{Verify}(PK_a, ((PK_a,\sigma_a), PK_b), \tau_a)=1$
    
    If all hold:
    * Mark the token as spent by adding $PK_a$ to $N$
    * Issue a new token for Bob by computing $\sigma_b \leftarrow \textsf{Sign}(s, PK_b)$ and output $\sigma_b$.


The scheme satisfies the following properties, assuming secure digital signatures and computationally-bounded adversaries:

1. **Unforgeability**: No adversary can create a valid token $(P,\sigma)$ such that $\textsf{Verify}(PK, P,\sigma)=1$ unless the bank previously signed $P$.
2. **Authorization Unforgeability**: No adversary can cause a token to be spent unless it can produce a valid authorization signature under the public key embedded in that token.
3. **No Double Spend**: Assuming an honest bank, no token $T$ can be successfully spent more than once.
4. **Liveness**: If an honest user holding a valid unspent token initiates a payment and the bank is honest and available, the payment completes successfully.
5. **Conservation of Value**: Assuming an honest bank, the number of valid unspent tokens in the system is invariant over time.




### Many things missing from this simple scheme

1. The bank must be trusted to be honest and available. 
2. Anyone observing the bank’s output learns the entire transaction graph: which public keys paid which other public keys.
3. Payments are interactive and require the payee to be online and interact with the payer for each transaction. 
4. Each payment has a unit denomination; there is no way to make change.
5. Anyone observing the bank’s output learns how many payments are done in the system.
6. Anyone observing the inputs to the bank learns who is initiating the payments.
   
We will start addressing 1 and 2 in the next sections and address the others in later posts.

## Decentralizing the Bank

We can decentralize the bank by implementing it as a fault tolerant distributed system with $n$ servers, tolerating up to $f$ Byzantine faulty servers, where $n \geq 3f+1$, in an asynchronous network.

The bank’s secret signing key $s$ is shared among the $n$ servers using a $(2f+1)$-out-of-$n$ [threshold signature scheme](https://alinush.github.io/threshold-bls). Each server $i$ holds a share $s_i$ of the signing key. As before, the associated public key $PK$ is known to all parties.

Each server also maintains its own local **nullifier set** $N_i$ of spent public keys.

Here is a version of the payment protocol that is based on [provable broadcast](https://decentralizedthoughts.github.io/2022-09-10-provable-broadcast/) using the fact that tokens are single-writer objects:

1. Bob samples a signing key pair $(sk_b, PK_b)$ and sends $PK_b$ to Alice.
2. Alice proves ownership of the token by signing the transaction $((PK_a,\sigma_a), PK_b)$ using her signing key $sk_a$, producing a signature $\tau_a \leftarrow \textsf{Sign}(sk_a, (PK_a,\sigma_a), PK_b)$.
3. Alice sends the transaction and signature $((PK_a,\sigma_a), PK_b, \tau_a)$ to all the $n$ bank servers.
4. Each server $i$ checks:
    * The transaction is authorized: $\textsf{Verify}(PK_a,((PK_a,\sigma_a), PK_b),\tau_a)=1$
    * The token is issued by the bank: $\textsf{Verify}(PK, PK_a,\sigma_a)=1$
    * The token is unspent: $PK_a \notin N_i$
    If all hold, server $i$ adds $PK_a$ to $N_i$ and computes a signature share $\sigma_{i} \leftarrow \textsf{Sign}(s_i, PK_b)$ and outputs $\sigma_{i}$.
5. Any party (in particular, Bob) seeing at least $2f+1$ valid signature shares on $PK_b$ from distinct servers combines them to form $\sigma = \textsf{Sign}(s, PK_b)$, a signature under the key $s$. This creates a new token $(PK_b, \sigma_b)$.

Since $n=3f+1$, any two sets of $2f+1$ servers intersect in at least one honest server, and an honest server will not sign two different spend requests for the same $PK_a$. In other words, two conflicting transactions cannot both obtain a valid quorum certificate $\sigma$.

We can now replace the assumption that the bank is honest with the assumption that at most $f$ of the servers implementing the bank are malicious.


1. **Unforgeability**: No adversary can create a valid token $(P,\sigma)$ such that $\textsf{Verify}(PK, P,\sigma)=1$ unless at least $2f+1$ servers previously signed $P$ with their shares of the bank key $s$.
2. **Authorization Unforgeability**: No adversary can cause a token to be spent unless it can produce a valid authorization signature under the public key embedded in that token.
3. **No Double Spend**: No token $T$ can be successfully spent more than once.
4. **Liveness**: If an honest user holding a valid unspent token initiates a payment, the payment completes successfully.
5. **Conservation of Value**: The number of valid unspent tokens in the system is invariant over time.

Note that the No Double Spend holds since we require $2f+1$ signatures of nullification.




## Hiding the Transaction Graph with a single bank

To hide the transaction graph from the bank in the centralized setting, we can use [blind signatures](https://decentralizedthoughts.github.io/2026-01-21-blind-and-threshold/), which hide the message being signed from the signer.

The idea is to have Bob hide his public key $PK_b$ from the bank when Alice requests a signature on it. This can be achieved using a blinding function $\textsf{Blind}(PK_b, r)$ that takes as input the public key $PK_b$ and a random blinding factor $r$, producing a blinded public key $PK'_b$. There is also an unblinding function $\textsf{Unblind}(\sigma', r)$ that takes as input a signature $\sigma'$ on the blinded public key and the blinding factor $r$, producing a valid signature $\sigma_b$ on the original public key $PK_b$.

The blinding process ensures that the bank cannot see the actual public key being signed, thus hiding the recipient. This yields unlinkability: when the token is later used, the adversary cannot know from which previous transaction this token was generated.

This protocol is almost identical to the basic payment protocol described above. The key differences are:

* The payee (Bob) blinds its public key before sending it to the payer (Alice).
* The authorization signature is computed over the blinded public key.
* The bank signs a blinded public key rather than the public key itself.

We restate the full protocol below to keep this section self-contained.

### Modified Payment Protocol (Blind Signatures)

1. Bob samples a signing key pair $(sk_b, PK_b)$.
2. Bob blinds $PK_b$ using a blinding factor $r$, producing a blinded public key $PK'_b = \textsf{Blind}(PK_b, r)$.
3. Bob sends $PK'_b$ to Alice.
4. Alice proves ownership of the token by signing the transaction $((PK_a,\sigma_a), PK'_b)$ using her signing key $sk_a$, producing a signature $\tau_a \leftarrow \textsf{Sign}(sk_a,(PK_a,\sigma_a), PK'_b)$.
5. Alice sends $((PK_a,\sigma_a), PK'_b, \tau_a)$ to the bank.
6. The bank checks:
    * $\textsf{Verify}(PK_a,((PK_a,\sigma_a), PK'_b),\tau_a)=1$
    * $\textsf{Verify}(PK, PK_a,\sigma_a)=1$
    * $PK_a \notin N$
    The authorization signature binds Alice to the blinded public key, preventing substitution of a different recipient after unblinding.
    If all hold, the bank adds $PK_a$ to $N$ and computes a signature $\sigma_B \leftarrow \textsf{Sign}(s, PK'_b)$ on the blinded public key.
7. Bob receives $\sigma_B$ and unblinds it using the blinding factor $r$, producing $\sigma_b = \textsf{Unblind}(\sigma_B, r)$, which is a valid signature on his original public key $PK_b$.


In addition to *Token Unforgeability*,  *Authorization Unforgeability*, *No Double Spend*, *Liveness*, and *Conservation of Value*, this scheme obtains a new property under the assumption that the blind signature scheme is unforgeable and blind:

* **Unlinkability**: The adversary cannot link a spend of a token to the transaction where the token was created. 

Specifically, assuming anonymous channels, given two different transaction graphs, with the same number of transactions and the same set of users, where the malicious users observe the same transaction flow, an adversary cannot tell which is which.



### Privacy Properties Not Provided

The scheme does not hide the identity of the transaction initiator from the bank. Achieving payer anonymity requires additional mechanisms such as anonymous communication channels that will be explored in future posts.

The scheme also does not hide payment timing, payment volume, or the total number of payments in the system. Addressing these forms of metadata leakage requires additional mechanisms that will be explored in future posts.

## Unlinkability in a Decentralized Bank

The blind signature approach can be adapted to the decentralized bank setting by a [threshold signature](https://decentralizedthoughts.github.io/2026-01-21-blind-and-threshold/) on the blinded public key $PK'_b$. The structure of the protocol is otherwise unchanged.


### Privacy Properties that depend on non-collusion

Even when the secret key is decentralized, one may worry that $2f+1$ servers may collude and secretly mint more coins. In future posts we will see how to prevent that from happening (using SNARKs).
