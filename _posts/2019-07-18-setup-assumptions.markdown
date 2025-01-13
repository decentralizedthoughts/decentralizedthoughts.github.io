---
title: The Trusted Setup Phase
date: 2019-07-18 19:29:00 -11:00
tags:
- dist101
- models
- crypto101
layout: post
---

<p align="center">
  co-authored with <a href="https://www.yanai.io/">Avishay</a> <a href="https://twitter.com/AvishaiY">Yanai</a>
</p>


> By failing to prepare, you are preparing to fail
> <cite> [The Biblical World, 1919](https://quoteinvestigator.com/2018/07/08/plan/) </cite>

When you want to understand a decentralized system, one of the first things you need to ask is: *does it have a trusted setup phase?* 

Here is a question: [do Bitcoin and Ethereum have a trusted setup phase?](https://ittaiab.github.io/2019-07-18-do-bitcoin-and-ethereum-have-any-trusted-setup-assumptions/)

Many protocols in distributed computing and cryptography require a **trusted setup**. A trusted setup is a special case of a multi-phase protocol. We call the first phase the *setup phase* and the second phase the *main phase*. There are two properties that often distinguish a setup phase from the main phase:

1. Typically the main phase implements some repeated task. The setup phase is done once and enables repeating many instances of the main phase.

2. The setup phase is often *input-independent*, namely, it does not use the private inputs of the parties. Furthermore, sometimes the setup phase is even *function-independent*, meaning that the specific function that the parties wish to compute is irrelevant; the parties at this phase only know that they want to compute *some* function. As such, the setup and main phases are often called *offline* (or *preprocessing*) and *online* respectively (i.e. parties may run the offline phase when they realize that *in some later point in time* they will want to run some function on inputs they do not know yet). 

You can think of a setup phase as an ideal functionality run by a completely trusted entity, denoted $T$, that we take for granted. For instance, assuming Public-Key Infrastructure (PKI) means that we assume there is a completely trusted entity to which every party submits its own public encryption (and verification) key and that entity broadcasts those keys to all parties. 
In this post, we will review some of the common types of trusted setup assumptions by looking at the ideal functionalities that they imply.

One way to model that trusted entity follows:
There is an initial set of parties $P_1,...,P_n$ who interact with the trusted entity $T$. The parties may send inputs $x_1,...,x_n$ to $T$ (where $x_i$ is $P_i$'s input), who in turn, runs some function $F(r, x_1,...,x_n)$ where $r$ is a uniformly random string, obtains outputs $y_1,...,y_n$ and hands $y_i$ to $P_i$. This process may be "reactive", namely, it may repeat multiple times. As this already describes an idealized world, we always assume that the communication channels between the parties and the trusted entity are secure.

In the following, we argue that most of those functionalities fall into one of out of the five categories below:

1. *No setup*: 
This is the simplest case, in which we don't really use any trusted entity or any trusted setup. The minimal communication assumption is that parties have access to some type of communication medium. Often, though, "no setup" also refers to a setting where parties' identities are globally known.
2. *Pairwise setup*:
Here we assume there is some set of initial parties $P_1,...,P_n$ and each two parties have a reliable communication channel between them. In particular, in the simplest pairwise setup assumption when party $P_i$ receives a message on the $(i,j)$ channel it knows that party $P_j$ sent this message.
3. *Broadcast setup*: 
We assume a setup whose implementation requires no secrets. The canonical example is a [PKI setup](https://en.wikipedia.org/wiki/Public_key_infrastructure) that requires [broadcast](https://ittaiab.github.io/2019-06-27-defining-consensus/) only to relay the public keys. 
4. *Partially public setup*: often called the *Common Reference String* ([CRS](https://en.wikipedia.org/wiki/Common_reference_string_model)) model. Many cryptographic protocols leverage this setup for improved efficiency. A special case of this setup is a [randomness beacon](http://www.copenhagen-interpretation.com/home/cryptography/cryptographic-beacons).
5. *Fully private setup*: often called the *offline phase* in the context of secure multiparty computation (MPC) protocols. Here, the setup phase computes a rather complex output that is party-dependant. For example, a phase that creates [OT and multiplication triplets](https://github.com/bristolcrypto/SPDZ-2) in SPDZ-2.

Let's detail these five setup variants, give some examples and discuss their advantages and disadvantages. In the end, we will also discuss some potential alternatives for having a setup phase. We use $n$ to denote the number of parties engaged in a system and $f$ the number of 'faulty' (or Byzantine) parties (who may behave arbitrarily).


## 1. No setup
If a protocol has no setup, then there is nothing to worry about. It's easier to trust such protocols. On the other hand, there are inherent limitations.

A setting with no setup has two main flavors.
The first assumes *really nothing* on the knowledge of the parties and is sometimes called [*anonymous channel model*](https://allquantor.at/blockchainbib/pdf/okun2008efficient.pdf)
The second assumes global knowledge of the identities of all parties, which is quite acceptable in many real world applications.
Both flavors suffer from non-authenticated channels, meaning that the adversary can launch man-in-the-middle attacks arbitrarily. 

In traditional cryptography (where the adversary is polynomially-bounded), this type of model was first studied by [Dolev, Dwork and Naor](https://www.cs.huji.ac.il/~dolev/pubs/nmc.pdf), for specific tasks like non-malleable encryption and zero-knowledge and later generalized to arbitrary computations by [Barak et al](https://eprint.iacr.org/2007/464.pdf). (The latter assumes global identities.) 


Another line of research, in the anonymous model, is based on a more refined assumption on the adversarial power.
Namely, the assumption limits the computational power of the adversary (e.g., hash rate) *compared to the computational power of the honest parties*. It was shown possible to construct a limited notion of PKI *from scratch* even in this slim model. For example see [Aspnes, Jackson and Krishnamurthy](http://www.cs.yale.edu/publications/techreports/tr1332.pdf) and several approaches directly inspired by Bitcoin-type puzzles (see [Katz, Miller and Shi](https://eprint.iacr.org/2014/857.pdf), [Andrychowicz and Dziembowski](https://www.iacr.org/archive/crypto2015/92160235/92160235.pdf), and [Garay, Kiayias, Kiayias and Panagiotakos](https://eprint.iacr.org/2016/991.pdf)).



## 2. Pairwise setup
Here, we assume that the communication channel between every pair of parties is authenticated.
This is a classic assumption in distributed cryptography and distributed computing.
The [Fisher, Lynch and Merritt 1985](https://groups.csail.mit.edu/tds/papers/Lynch/FischerLynchMerritt-dc.pdf) lower bounds show that even weak forms of Byzantine Agreement are impossible when $n \leq 3f$ even given this setup, and even against a traditional polynomially-bounded adversary.

For $n>3f$, on the other hand, this setup allows perfect implementation of any functionality. This is the celebrated result of [Ben-Or, Goldwasser and Widgerson 1988](http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.116.2968&rep=rep1&type=pdf) (see [Asharov and Lindell](https://eprint.iacr.org/2011/136.pdf) for a full proof).


## 3. Broadcast setup
*Broadcast* means that the security of the system wouldn't be damaged even if the trusted entity is 'transparent', namely, all inputs/outputs it receives/sends and its random string are publicly known. 
The canonical examples are protocols that use a trusted entity to [broadcast](https://ittaiab.github.io/2019-06-27-defining-consensus/) the public keys of all parties.

Having a PKI both improves the complexity of asynchronous Byzantine Agreement (for example, see [Cachin, Kursawe and Shoup](https://eprint.iacr.org/2000/034.pdf)) and improves the fault tolerance to $n=2f+1$ for synchronous Byzantine Agreement (for example, see [Katz and Koo](https://eprint.iacr.org/2006/065.pdf)).

Note there is a risk of a circular argument: With a PKI setup it is possible to solve Byzantine agreement in the synchronous model for $n=2f+1$ and Byzantine broadcast for $n=f+1$ (see [Dolev and Strong](https://www.cs.huji.ac.il/~dolev/pubs/authenticated.pdf)). But setting up a PKI requires *broadcast* which requires $n>3f$ if there is no PKI (in the standard models).

Advantages: an important advantage of a fully-public setup is its relative simplicity and reduced attack surface. 

Risks: failure of this setup often means equivocation. Giving different parties different keys may cause later protocols to fail.

## 4. Partially public setup

*Partially public* means that the output from the trusted entity, $T$, is known to all parties, however it may be required the parties' inputs $x_1,...,x_n$ and $T$'s random string, $r$, should be kept secret. 
As an example, consider a system that continuously receives messages from users such that in some future time $t$ all messages should be revealed (at once). Such a system may use a trusted setup as follows: the function $F$ receives no inputs from the parties, and proceeds as follows: generate a key-pair $(sk,pk)$ for an encryption scheme, then generate a Rivest, Shamir and Wagner [time-lock-puzzle](http://people.csail.mit.edu/rivest/RivestShamirWagner-timelock.pdf) $p$ that hides $sk$ until time $t$ arrives; finally, output to all parties the puzzle $p$ and the encryption key $pk$, which concludes the setup phase. 
In the main phase, users can encrypt their messages using $pk$ and broadcast them. In addition, they begin to solve the puzzle so that in time $t$ they will obtain the decryption key $sk$, which allows them to decrypt all messages. Note that all outputs of the functionality $F$ are public to all parties, but the internal state of the trusted entity (namely, the random string by which the pair $(sk,pk)$ was generated) must kept secret.

Having a trusted pre-computed procedure with secret values often provides significant benefits.  The risk of these setups is that the properties of the system now depend on the *privacy* of the setup. It is much harder to detect information leaking during setup (an attacker that learns secrets can hide this knowledge).

The advantage of requiring the setup to publish a common public value is that it's relatively easy to ensure this property (relative to sending private values to parties). This model is often referred to as a *Common Reference String* ([CRS](https://en.wikipedia.org/wiki/Common_reference_string_model)) model.
Here we give two examples:

1. Setup for efficient Verifiable Secret Sharing --
[Kate, Zaverucha, and Goldberg](https://www.cypherpunks.ca/~iang/pubs/PolyCommit-AsiaCrypt.pdf) propose a scheme that requires a trusted setup to generate a random public generator $g$ and a secret key $\alpha$. The setup then broadcasts powers of the form $g^{(\alpha^i)}$. Using this setup one can obtain the most efficient [Asynchronous Verifiable Secret Sharing](https://eprint.iacr.org/2012/619). 

2. Setup for efficient Zero-Knowledge --
Several efficient Zero-Knowledge protocols require CRS setups. Often implementing these setups in a trusted manner requires some non-trivial [MPC](http://u.cs.biu.ac.il/~lindell/MPC-resources.html) protocol. For example, see [Bowe, Gabizon and Miers](https://eprint.iacr.org/2017/1050). In fact just running an MPC protocol is not enough, often a whole [setup ceremony](https://z.cash/technology/paramgen/) is necessary in order to establish public verifiability.

## 5. Fully private setup
This is the most general form of setup, in which even the outputs that the functionality hands to the parties should be kept secret from one another. Obviously, the big advantage here is that such setups allow running powerful protocols on top of them. As instantiation (or realization) of such setup functionalities are quite complex, they typically expose a larger attack surface.

We focus here on two type of examples: Distributed Key Generation and Offline phases for Secure Multi-Party Computation.


### Distributed Key Generation and setup for threshold signatures

[Threshold](https://www.iacr.org/archive/eurocrypt2000/1807/18070209-new.pdf) signatures [schemes](https://www.iacr.org/archive/pkc2003/25670031/25670031.pdf) often provide benefits in terms of reduced word complexity and reduced total computation cost (see for example [here](https://eprint.iacr.org/2000/034.pdf)). The problem with threshold signatures is that they require a setup.
Setting up a threshold signature scheme is often referred to as a Distributed Key Generation ([DKG](https://en.wikipedia.org/wiki/Distributed_key_generation)) setup. 

The DKG functionality receives just random bits from each party, generates an $(sk,pk)$ pair, outputs $pk$ to everyone and shares of $sk$ to the parties such that party $P_i$ receives $sk_i$, which must be kept secret from other parties.

Risks: There are two things that can fail in such a setup, the first is that the secret is leaked when collusion reaches the threshold and the second is that some parties might receive incorrect shares. There are ways for a party to verify the validity of their shares, so the main risk is when parties are offline.


### Trusted setup for secure computation
Protocols for [secure multiparty computation (MPC)](https://en.wikipedia.org/wiki/Secure_multi-party_computation) allows a set of $n$ parties $P_1,...,P_n$ to compute a circuit $C$ (Boolean or arithmetic) over their private inputs $x_1,...,x_n$, and reveal only the output $y=C(x_1,...,x_n)$ (suppose all parties should learn the same output). For instance, the circuit $C$ may compute the summation of all inputs.

Modern MPC protocols are designed to work in an offline-online manner, where the offline serves as a setup phase, which is typically fully private. One prevalent example is a trusted setup that shares *multiplication triples* (also known as *Beaver triples*) to the parties. Specifically, the trusted setup hands random $a_i, b_i$ and $c_i$ to party $P_i$ such that $(a_1 + ... + a_n)ֿ\cdot(b_1 + ... + b_n)=(c_1 + ... + c_n)$. 
Then, in the main phase of the protocol (also known as the online phase) the parties share their inputs, namely, party $P_i$ shares its input $x'$ by sending $x'_j$ to party $P_j$ such that $x'_1 + ... + x'_n = x'$. The parties now can compute any arithmetic operation over the shared values, that is, given a sharing of secret values $x$ and $y$, such that party $P_i$ holds $x_i$ and $y_i$ where $x_1+...+x_n=x$ and $y_1+...+y_n=y$, then the parties may perform the following procedures (we omit some details in the description below):

- *Opening* - Given a sharing $x_1,...,x_n$ the parties can obtain $x=x_1+...+x_n$.
- *Addition/subtraction* - The parties can compute a sharing of $z=x+y$ by having each party $P_i$ locally compute $z_i=x_i+y_i$. Obviously, it follows that $z_1+...+z_n = (x_1+...+x_n)+(y_1+...+y_n)$.
- *Scaling* - Given a value $c$ known to all parties, they can compute a sharing of $z=cx$ by having each party locally compute $z_i=cx_i$. Again, it follows that $z_1+...+z_n = (cx_1+...+cx_n) = c(x_1+...+x_n)=cx$.
- *Multiplication* - The parties can compute a sharing of $z=xy$ by *sacrificing* a single multiplication triple from the setup. For simplicity, denote a sharing $(x_1+...+x_n)$ by $\[x\]$. The parties have the sharings $\[x\]$, $\[y\]$ and the triple $\[a\],\[b\],\[c\]$ from the setup (remember that $c=ab$). The parties open the differences $\[s\]=\[x\]-\[a\]$ and $\[t\]=\[y\]-\[b\]$. These do not leak any information since the values $a$ and $b$ are chosen uniformly by the trusted setup, thus, the values $s$ and $t$ are uniform and do not reveal anything about $x$ and $y$. Then, the parties compute $\[xy\] = s\[y\] + t\[x\] + st - \[c\]$. This computation is composed of scaling and addition/subtraction only and can be computed locally by the parties to obtain a sharing of $\[z\]=\[xy\]$.

Risks and advantages: As mentioned above, such a setup phase has a large attack surface. The output from the setup phase must be kept secret.
That is, in the above procedure for multiplication, note that if some coalition of $t$ parties obtain the shares $a_1,...,a_n$ of all parties then they can learn the secret value $x$ by computing $\[x\]=\[s\]-\[a\]$. 
Note that privacy is not the only concern in such setup phases: we must also make sure that the triples are correct!
Namely, that $ab$ indeed equals $c$, since otherwise the output of the computation would not be correct. Protecting the triples from leakage and from being influenced by malicious parties is a hard task and therefore incurs a huge overhead to MPC protocols. On the other hand, given the output multiplication triples from the setup phase, the main phase of the protocol becomes super fast.

## Are there alternatives to Trusted Setups?
Here we mention some potential alternatives:
1. A setup shifts considerable amount of trust from the online phase of the system to some historic setup phase. This introduces new risks and security holes. 
One potential alternative is to have a never-ending setup phase. In such schemes there is a *continuously updatable CRS*. One recent example is [SONIC](https://eprint.iacr.org/2019/099.pdf).
2. Another approach is to have multiple setups generating multiple common reference strings.
In this approach we only assume that *some* of them are done faithfully. See [Groth and Ostrovsky](https://eprint.iacr.org/2006/407.pdf).

## Acknowledgments

Special thanks to [Alin Tomescu](http://twitter.com/alinush407) for reviewing this post.

Please leave comments on [Twitter](https://twitter.com/ittaia/status/1151977685154971648?s=20)
