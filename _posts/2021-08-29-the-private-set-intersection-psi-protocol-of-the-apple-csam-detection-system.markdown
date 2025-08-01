---
title: The Private Set Intersection (PSI) Protocol of the Apple CSAM Detection System
date: 2021-08-29 17:55:00 -04:00
tags:
- cryptography
author: Benny Pinkas
---

In this post, we will discuss the cryptographic construction used in Apple's new system for detecting CSAM - Child Sexual Abuse Material. This cryptographic construction implements a new variant of PSI - Private Set Intersection.  While a lot of attention has been paid to the broad implications of this system, the technical details of the PSI construction have not been highlighted, even though Apple published a detailed [technical description of the system](https://www.apple.com/child-safety/pdf/Apple_PSI_System_Security_Protocol_and_Analysis.pdf), and Eric Rescorla published a [technical overview](https://educatedguesswork.org/posts/apple-csam-intro/) of the system.

This blog post will focus on the cryptographic PSI construction used within the CSAM detection system, rather than discussing policy issues and implications. An appendix at the end of this post will describe the "big picture" of the system which uses this PSI protocol.

The PSI construction is very interesting by its own sake, since it implements a threshold version of PSI, which reveals the intersection only if the intersection size is greater than some threshold. The PSI protocol utilizes a number of technical tools not previously used in this context. These include Diffie-Hellman random self-reducibility (due to Naor and Reingold), which is used to generate keys for encrypting information related to the input items, and Coppersmith and Sudan's algorithm for decoding an interleaved Reed-Solomon code under random noise, which is used for identifying correct shares as part of implementing the threshold functionality.



 
### Private Set Intersection - PSI
Private set intersection - *PSI*, is a cryptographic protocol that allows two parties, each with a private input set, to compute the intersection of these sets without disclosing any other information about them. A lot of information about PSI is available on the web, for example [here](https://cyber.biu.ac.il/wp-content/uploads/2017/01/15.pdf), [here](https://decentralizedthoughts.github.io/tags/#private-set-intersection), or [here](https://www.youtube.com/watch?v=I3bux0mO4wA).
In principle, PSI seems to be relevant in detecting CSAM or other sensitive material: A server (e.g., Apple) will have an input set which contains the items that are searched for. (In the case of this system, the set contains perceptual hash values of known CSAM photos.) The other participant in the protocol, the client, will be a user device whose is the set of perceptual hashes of photos which the device uploads to the cloud. The protocol will identify the intersection of these sets while hiding the server's input set from the device, and hiding from the server all information about device photos which do not appear in the server's input set.  
In reality, the situation is more complicated. We list below some of the requirements that the PSI protocol must meet in the current application, and explain these requirements in more detail in the appendix.

### Functional requirements  
The PSI protocol must satisfy the following requirements, which are needed for the CSAM detection system:


- ***(Server-only output)*** Only the server learns the result of the intersection. The client must learn nothing.  This requirement is fairly standard and is met by many PSI protocols.
- ***(Threshold PSI)*** If the size of the intersection is smaller than or equal to a specific threshold then the server cannot identify the items in the intersection or learn the exact size of the intersection.
- ***(Threshold PSI)*** Each input item of the client has some additional information that is associated with it and is sent encrypted.  If the size of the intersection is greater than the threshold then the server is able to learn the information associated with the items in the intersection.
The *"threshold PSI"* requirement is not supported by the majority of existing PSI protocols. In most current protocols, one or both parties can identify all equalities between the items in the two sets, whereas the threshold variant requires to hide information until the number of equalities reaches the threshold. There are newer "[PSI analytics](https://eprint.iacr.org/2019/241.pdf)" protocols that don't reveal the items in the intersection, but rather apply an arbitrary computation to these values and only reveal the output of that computation. These protocols are quite efficient and can be used to implement threshold PSI, for example by computing a function which first checks if the size of the intersection is greater than the threshold and only then output additional information. However, these protocols are based on an MPC computation of a circuit, which means that they are more complicated to implement, and additional require communication.
- ***(Dynamic input)*** Most existing PSI protocols are designed for two parties with static input sets. In this application, the server has a static input set which does not change often. The device/client, on the other hand, might add new input elements on a regular basis. The performance overhead per new item must not depend on the total size of the set.
- ***(Input consistency)*** The PSI protocol must ensure that the server provides the same input to all protocol executions with all users and at all times.

### High-level protocol design
The requirements that were listed above define the basic structure of the protocol.  


The requirements for **input consistency** and **server-only output** are satisfied by running a two-message PSI protocol in which the server sends the first message to the client. This message is publicly published and therefore all clients can verify that they receive the same message. (We discuss in the appendix how Apple implements this first message.) Since this is a two-message protocol, the client sends back a message to the server but receives no answer. Therefore clients do not learn any output.

**Dynamic device input** is supported by the client sending a message to the server whenever it receives a new input item  (i.e., uploads a new photo). The server processes each message as it is received and checks if it is a PSI match. Periodically, the server checks whether the number of matches exceeds the threshold.


The hardest feature to support is satisfying the **threshold PSI** requirement. Supporting this requirement calls for the usage of *[secret sharing](https://en.wikipedia.org/wiki/Shamir%27s_Secret_Sharing):* any data item in the intersection will reveal a share to the server, while still keeping secret the data associated with the item.  When the number of revealed shares reaches the threshold, the server has enough shares to recover a key which enables it to decrypt the data associated with the items in the intersection.  
There is one particular problem with this suggestion: While the server cannot recover the key if the intersection size is smaller than the threshold, it nonetheless learns how many matches were uploaded by the client. To prevent that, the protocol also requires the client to upload "synthetic matches". These are items that are periodically and randomly uploaded by the client, seem to be in the intersection, but include shares containing random information. Suppose that the threshold is 30. The server might determine, for example, that a certain client has 95 input elements that pass the initial PSI screening, but if these elements contain only 25 real matches and 70 synthetic matches, the server will not have enough shares to recover the key. In this case, the server will not be able to determine how many real matches there are and which photos are associated with them. (Of course, the server's degree of uncertainty about the number of matches depends on the probability distribution that the device utilizes to determine when to upload synthetic matches.) Applying this approach requires the server to be able to identify the correct shares when their number reaches the threshold. This is implemented using a decoding algorithm due to Coppersmith and Sudan, which we describe below.

The basic structure of the protocol is depicted in the following drawing:

![](https://i.imgur.com/OYu1Q3l.png)






### Overview of the technical tools
The PSI protocol is based on using multiple tools, on which we will elaborate shortly.
First, the server's input set that is sent to the clients is encoded as a **cuckoo table**. This data structure enables clients to efficiently lookup the data that is relevant for each input item that they have.
The data associated with each item of the server is encoded in the table as a Diffie-Hellman tuple. The **Diffie-Hellman hardness assumption** prevents the client from identifying this data, and thus prevents it from learning which items are encoded in the cuckoo table.
For each input item of the client, the client uses the data that it reads from the cuckoo table to generate a cryptographic key. The key is generated using the **Naor-Reingold Diffie-Hellman random self-reducibility** construction. This ensures that if this item is not in the database, and hence the data read from the cuckoo table is not a Diffie-Hellman tuple, then the key is random and unknown to the server. This key is used to encrypt the data associated with this item. Therefore the server can only decrypt data associated with items which exist in the server's input set, as well as the data associated with synthetic matches.  
If the items uploaded by a client include more than the threshold number of items from the server's input set, then the server must be able to identify these items and separate them from the synthetic matches. This is done using an algorithm of Coppersmith and Sudan for **decoding interleaved Reed-Solomon code under random noise**.

### More information about the technical tools used in the protocol
**Cuckoo tables**
[Cuckoo hashing](https://en.wikipedia.org/wiki/Cuckoo_hashing) is a method for storing items in a hash table while avoiding most collisions. The items are mapped to a table T using two random hash functions $h1,h2$ with a range of size |T|. The main property is that a set of $n$ items can, with high probability, be mapped to a table of size $(2+\epsilon)n$ with no collisions, where each item *x* is mapped either to entry $T[h1(x)]$ or to entry $T[h2(x)]$. Cuckoo hashing was introduced by [Pagh and Rodler](https://www.brics.dk/RS/01/32/BRICS-RS-01-32.pdf)  (see [here](https://twitter.com/RasmusPagh1/status/1431608756589187073?s=20) as well). An excellent survey of this topic appears [here](https://udiwieder.files.wordpress.com/2014/10/hashbook21.pdf).

In Apple's PSI protocol, the server encodes in a cuckoo table information about its input set (i.e., the hash values of CSAM photos). When the client has an input item $x$ (a hash value of a photo that it uploads), the client retrieves from the table the contents of entries $T[h1(x)]$ and $T[h2(x)]$, and uses them to compute the PSI values that will be sent to the server about this item. This means that two such values will be sent for each item.

[Apple's description](https://www.apple.com/child-safety/pdf/Apple_PSI_System_Security_Protocol_and_Analysis.pdf) of the usage of cuckoo hashing refers to a cuckoo table of size $(1+\epsilon)$*n* which stores information about a database of $n$ items. While the constants are not defined in the document, it is mentioned there that the table size will not suffice for storing all $n$ items of the CSAM database. Therefore Apple's input will consist of a (large) subset of that database. In this aspect, the protocol is very different than PSI protocols described in the academic literature, as the definition of PSI does not allow to omit any input item of the participants. However, for the CSAM detection application, it is fine to encode in the cuckoo table a subset of the CSAM database, as this suffices in order to identify users who have a large number of CSAM photos.

We note that the usage of the cuckoo table in the protocol can be more efficient by making the following changes:  (1) using three hash functions instead of two, and (2) if we denote by $D(x)$ the value that should be retrieved for an input $x$, then instead of storing $D(x)$ in one of the locations to which $x$ is mapped, storing in these locations three values whose sum is equal to $D(x)$. In other words, the client retrieves a value from the table by computing $T[h1(x)] + T[h2(x)] + T[h3(x)] = D(x)$. This variant was mentioned in Remark 7 in [Apple's technical description](https://www.apple.com/child-safety/pdf/Apple_PSI_System_Security_Protocol_and_Analysis.pdf), and is analyzed [here](https://eprint.iacr.org/2021/883.pdf) in the context of PSI and other applications. With this approach, it is possible to store all $n$ input items in a table of size approximately $1.25n$ rather than $(2+\epsilon)n$. Furthermore, since this modified PSI protocol retrieves only one item from the table, rather than two items in vanilla cuckoo hashing, the client computes and sends one message, rather than two, for each item.
       
**The Diffie-Hellman hardness assumption**
We use the notation of [Apple's description](https://www.apple.com/child-safety/pdf/Apple_PSI_System_Security_Protocol_and_Analysis.pdf)  of the PSI system, with the group operation being addition, as in elliptic curve groups.
Let $G$ be a group of prime order $q$, and let $g$ be a generator of this group.
A triple $(L,T,P)$ of group elements is a *Diffie-Hellman tuple* (DH tuple) if there exists a value $\alpha \in [1,q]$ such that $L=\alpha g$ and $P = \alpha T$.

The Diffie-Hellman hardness assumption states that any polynomial-time algorithm has only negligible success probability in distinguishing between the values $[g,(L,T,P)]$, where $(L,T,P)$ is a Diffie-Hellman tuple with $L,T$ being random group elements, and $[g,(L_1,L_2,L_3)]$, where $L_1,L_2,L_3$ are random elements in the group.  


**Naor-Reingold Diffie-Hellman random self-reducibility**
The Apple PSI system makes novel usage of Diffie-Hellman [random self-reducibility](https://en.wikipedia.org/wiki/Random_self-reducibility) in order to generate keys for the PSI protocol.  
[Naor and Reingold](https://dl.acm.org/doi/10.1145/972639.972643) described a random self reduction for DH tuples: Given a triple $(L,T,P)$ of group elements, choose random $\beta, \gamma$ in $[1,q]$ and compute $Q = \beta T + \gamma g$ and $S = \beta P + \gamma L$.
The following property holds:
- If $(L,T,P)$ is a DH tuple, i.e. it is of the form $(L=\alpha g,T,P=\alpha T)$ for some $\alpha$, then $(L,Q,S) = (L,\beta T + \gamma g, \beta P + \gamma L)$ is also a DH tuple. Furthermore,  $Q= \beta T + \gamma g$ is uniformly distributed in $G$.
- Otherwise (i.e., if $(L,T,P)$ is *not* a DH tuple), $(Q,S)$ is a uniformly chosen pair of values in $G$.

**Generating key using the random self-reducibility:** Diffie-Hellman random self-reducibility is used in the Apple PSI system in the following way. The server chooses a master secret key $\alpha$, which is used for all clients. It sends to the clients a cuckoo table $T$ which, for a value $x$ appearing in the server's input, stores in either $T[h1(x)]$ or in $T[h2(x)]$ the value $\alpha H(x)$, with $H()$ being a random hash function mapping values to the group. The server also sends the value $\alpha g$ to the clients.
Note that for a value $x$ that is encoded in the table, either $(\alpha g, H(x), T[h1(x)])$ or $(\alpha g, H(x), T[h2(x)])$ is a DH tuple. Otherwise, these are not DH tuples, except with negligible probability.      

The client recovers from the cuckoo table the two entries corresponding to each of its input values $x$. If this value is encoded in the table then one of these two entries results, as described above, in a DH tuple. However, the client cannot determine whether this is the case due to the Diffie-Hellman assumption (namely, that it is difficult to distinguish DH tuples from random tuples).
The next step is the client applying the Naor-Reingold reduction to randomize each tuple it generated from the table. Based on the random self-reducibility property, if the original tuple was a DH tuple then so is the resulting tuple. Otherwise, the client obtains a uniformly random tuple.
The client then uses the resulting tuple to generate a key, which is denoted in Apple's technical description as ***rkey***, and is unique per item.
The key *rkey* is used to encrypt data about this item that is sent in the PSI protocol. If the tuple is a DH tuple then the server is able to recover *rkey* by utilizing its knowledge of $\alpha$. If the tuple is *not* a DH tuple, *rkey* is uniformly random and is independent of any information known to the server.


**Decoding an interleaved Reed-Solomon code under random noise, and the usage of this technique in the Apple PSI protocol**
The following algorithm was described by [Coppersmith and Sudan](https://madhu.seas.harvard.edu/papers/2003/copper-conf.pdf). The important property of this algorithm is that given $t+1$ correct shares and $s$ random shares, it can efficiently identify the correct shares. (Each share will be of length $s+1$.) This algorithm can therefore be used by the protocol to identify shares that are hidden among synthetic matches.

In more detail, the input is a matrix of $m$ columns, where each column includes $s+1$ elements. The matrix is constructed in the following way:
There are $s$ random polynomials $P_1(),...,P_s()$ of degree $t-1$. A "good" column, which corresponds to a correct share, is of the form $[x,P_1(x),...,P_s(x)]$ for a randomly chosen $x$. A random column contains $s+1$ random values.  
We assume that the number of good columns is at least $t+1$. We also denote the number of random columns as $s$, and since the total number of columns is $m$ it must hold that $s<m-t$.  
The algorithm of Coppersmith and Sudan identifies the set of good columns.

This algorithm can be used for identifying $t+1$ correct shares which are hidden among at most $s$ additional random shares. Note that $s$ must be defined in advance, and that the size of each share is larger by a factor of $s+1$ compared to a single value in the relevant field.  This is not a major issue in the context of the CSAM detection system since (as described in the appendix) each uploaded photo is accompanied by a low-resolution encrypted version of the photo, and the size of this data dominates the size of the expanded share.

### Putting the pieces together for the PSI protocol
The system works in the following way, which is also depicted in the drawing at the end of this section. The value $t+1$ is the threshold for the number of items that are needed in order to open the items in the intersection.

The server publishes a cuckoo table that encodes the items in the server's input set.
Each client chooses a key, denoted ***adkey***, which encrypts data associated with the input items of the client. (In the CSAM detection protocol, this data includes a low-resolution visual derivative of the photo.)
In order to encode the key *adkey*, the client uses secret sharing with threshold $t+1$. A share of *adkey* is attached to every item, and it has the format $[x,P_1(x),...,P_s(x)]$, with $P_1(),...,P_s()$ being random polynomials of degree $t-1$. This share is encrypted, in a way that is described below.  


For each of its input items, the device retrieves from the cuckoo table the two entries that are keyed by this item. The client uses the Naor-Reingold self-reduction to generate a key ***rkey*** using these entries. If the item is encoded in the cuckoo table then *rkey* can be decoded by the server using its knowledge of $\alpha$. Otherwise this key looks random to the server. The client uses *rkey* to encrypt the share of this item using authenticated encryption (i.e., encryption which enables to verify whether the decryption was correct).
Additionally, the client periodically uploads synthetic matches: These are random values $[x,x_1,...,x_s]$ which have the same format as a share. Synthetic shares are encrypted by generating a random DH tuple from $\alpha g$, and generating a key from this tuple, as when generating keys for real shares. Therefore, the server can decrypt all synthetic matches, but will obtain random shares.


To sum up, the client generates for each of its input elements an encryption with the key *adkey* of the data associated with this element, and an encryption with the key *rkey* of a share of *adkey*. The server attempts to compute the corresponding *rkey* and use it to decrypt the share of *adkey*. A successful decryption can be identified by the server due to the usage of authenticated encryption.
A successful decryption happens either for an actual match with the server's input set, or for a synthetic match. The former includes a share of *adkey* whereas the latter includes a random share. The server cannot distinguish between the two cases, but it tries to run the Coppersmith-Sudan algorithm for decoding the shares. As soon as the server obtains $t+1$ correct shares, while the number of random shares is at most $s$, the algorithm succeeds and identifies the correct shares. The server can then recover the key *adkey* and decrypt the data associated with the items in the intersection.


![](https://i.imgur.com/hyCnYxC.png)


## Security
We will not include here a detailed security proof of the protocol. A simulation based proof appears in the original [protocol description](https://www.apple.com/child-safety/pdf/Apple_PSI_System_Security_Protocol_and_Analysis.pdf), and a game based proof appears in [Mihir Bellare's analysis](https://www.apple.com/child-safety/pdf/Technical_Assessment_of_CSAM_Detection_Mihir_Bellare.pdf).  We only highlight here the following high-level claims about the security of the PSI protocol.
- The privacy of the server's input set that is encoded in the cuckoo table, is based on the Diffie-Hellman assumption. This assumption guarantees that the cuckoo table looks pseudo-random to the client. The only information that the client learns is the size of the table.
- The privacy of the client, namely the assurance that the server cannot decrypt information which does not correspond to entries in the cuckoo table, is ensured by symmetric key encryption using a key derived by the random self-reduction. This key is uniformly random for items which are not encoded in the cuckoo table. The only security assumption that is needed is the security of a symmetric cipher such as AES. Furthermore, if the cipher that is used is AES256 or a cipher with a similar key length, security is also guaranteed against quantum attacks.

With regards to a potentially malicious behavior of the server and client, the following claims can be verified:
- Privacy for the server: A malicious client does not learn anything about the input set of the server, except for its size. This claim follows from the fact that the only information that the client receives in the protocol is the first message that is sent by the server, and therefore is not affected by the client's behavior.
-  Privacy for the client: A malicious server does not learn anything about items which the server did not encode in the cuckoo table sent to the client.
- Correctness with respect to a malicious client: The protocol does not prevent a malicious client from affecting the output of the protocol. In particular, the client can reduce the size of the intersection. This can be done for example by replacing protocol messages with arbitrary values, which is equivalent to replacing input items with random values, or by sending more synthetic matches than are allowed, in order to disrupt the Coppersmith-Sudan decoding algorithm. A malicious client can also increase the number of hits that appear in the intersection. (This attack should be handled by other components of the CSAM detection system.)
- Correctness with respect to a malicious server: A malicious server might encode in the cuckoo table more items than are allowed by the protocol.  It was shown in [recent work](https://eprint.iacr.org/2021/883.pdf) that this type of "overfitting" attack does not succeed beyond the size of the cuckoo table: If the table is of size $\ell'$ bits, and is expected to encode  $n$ items where each item is represented as an $\ell$ bit output of a random oracle, then encoding more than $\ell' / \ell$ items is impossible since it is equivalent to compressing the representation of a random function. In other words, if the size of the table is $\ell' = (1+\epsilon)n\ell$ bits, it cannot be encoded more than $(1+\epsilon)n$ items.  
This result still enables a malicious server to encode in the table an extra $\epsilon n$ values. In the PSI protocol, the table must store $n$ hash values that are all raised to the same secret exponent $\alpha$. Therefore, in the context of the CSAM detection application that is described in the appendix, these hash values can be certified by an additional entity such as NCMEC. Standard zero-knowledge proof techniques can be used to prove, without disclosing the actual hash values, that $n$ table entries satisfy the required discrete-log relations, and the other table $\epsilon n$ entries are pseudo-random and therefore do not encode any elements.  



---

## Appendix - Apple's CSAM detection system
This appendix is intended to give the context in which PSI is used as part for a larger system for detecting child sexual abuse material - CSAM. We emphasize again that the purpose of this post is not to evaluate or discuss the CSAM detection system, but rather to focus on the PSI protocol.

Apple recently announced an upcoming system for detecting CSAM, in photos that are uploaded to iCloud. The system is based on a perceptual hashing algorithm, called *NeuralHash*. With this algorithm, photos are mapped to binary strings while ensuring that different variations of the same photo, under simple transformations such as cropping or resizing, are mapped to the same string. Apple will receive lists of perceptual hashes of known CSAM images from organizations such as NCMEC - the National Center for Missing and Exploited Children, and will use the system to identify whether the perceptual hash values of photos uploaded to iCloud appear in this list of hash values.
 
The system handles very sensitive data. The CSAM photo database must remain secret, and Apple employees are not allowed to see it. The photos that users upload to iCloud are also sensitive, and Apple does not wish to scan them on iCloud. The consequences of identifying a user as having CSAM material are very severe, so the false positive probability must be negligible. The system must therefore satisfy a number of conflicting requirements:

1. Apple does not receive the database of CSAM images from NCMEC. It only receives the hash values of these images.
2. Apple learns nothing about uploaded photos which do not match the CSAM database.
3. Even if a user uploads photos whose hash is in the CSAM database, Apple will only be able to access data associated with these photos after identifying that the user uploaded more than a threshold number of such photos (currently this threshold is defined to be 30).
4. The risk of false positives, namely of incorrectly identifying users as uploading CSAM, must be extremely low.
6. Users must not be able to access the database of hashes of CSAM images.
7. Users must not be able to learn which of their photos is identified as CSAM.

Note that the first four requirements are intended to protect the privacy of users, and to protect users from erroneous identification. The last two requirements protect the system from adversarial users who want to identify which photos appear in the CSAM database, or try to investigate ways for evading the system.


The introduction of this system raised many trust questions: how can the system be prevented from searching for content that is not CSAM (for example, by governments forcing Apple to add such content to the database)? Could users be tricked into uploading seemingly innocent photos whose hash values match those of CSAM photos? What would be the implications of such an attack?
These questions are beyond the scope of this post. The questions are discussed in a document that Apple published about the [security threat review of this system](https://www.apple.com/child-safety/pdf/Security_Threat_Model_Review_of_Apple_Child_Safety_Features.pdf). (The document, for example, states that the system will only search for photos appearing in CSAM datasets provided by two or more organizations from different jurisdictions. It also states that after a user account is identified as uploading more than the threshold number of CSAM photos, these photos will be scanned by another perceptual hash algorithm and by a human operator.) Apple also gave a [presentation](https://www.apple.com/105/media/us/child-safety/2021/7bc1183f-32b5-41da-8757-f7625cf634a3/films/usenix-security-symposium/child-safety-usenix-security-symposium-tpl-us-2021_16x9.m3u8) of these issues in the Usenix Security Symposium 2021.

### Functional requirements  
The CSAM detection system has unique features which prevent it from using an off-the-shelf PSI protocol. In particular, the PSI protocol must satisfy the following additional requirements:


- ***(Server-only output)*** Only Apple should learn the result of the intersection. The device must learn nothing.
- ***(Threshold PSI)*** If the size of the intersection is smaller than or equal to the threshold then Apple must not be able to identify the photos in the intersection, or learn the exact size of the intersection. Otherwise, Apple should be able to learn additional information about the photos in the intersection. (In the deployed system this additional information will be a low-resolution “visual derivative” of the original photo, which will be examined by human operators to verify that looks like CSAM.)
- ***(Dynamic input)*** Apple has a static input set which does not change often. (In fact, Apple stated that this set will only change during OS updates, which happen every few months.) The device, on the other hand, might upload photos on a regular basis. Therefore, the system must enable the device to dynamically add items to its input set. The performance overhead per new item must not depend on the total size of the set.
- ***(Input consistency)*** Another subtle requirement of this application is about the set of hash values that is input by Apple to the protocol. PSI protocols, and MPC protocols in general, are primarily concerned with enabling multiple parties to compute a specific function with the same security and privacy guarantees that are satisfied when that function is computed by a trusted party. (This is the ideal-model / real-model paradigm.) Researchers in this field study *how to compute* a function securely, rather than *which function* should be computed or how to *verify the inputs* that are used. With the CSAM system, there is a concern that Apple might use the system, or be coerced to use it, to track specific users for specific content. For example, Apple might provide the protocol with different inputs for different user groups or at different times.
This concern raises the requirement that the PSI protocol must ensure **input consistency**, namely ensuring that Apple provides the same input to all protocol executions with all users and at all times.

The **input consistency** and **server-only output** requirements are satisfied by running a two-message PSI protocol in which Apple incorporates the first protocol message into the operating system. Since Apple distributes a universal operating system for all users worldwide, the PSI protocol uses the same input for all users. This assurance is based on Apple's statement about the code of the operating system, but a deviation from this statement can be detected by reverse engineering the operating system. The resulting two-message PSI  protocol has Apple sending a single message to all devices, and the devices sending messages to Apple but receiving no answer. Therefore devices do not learn any output.


(We note that for the purposes of this writeup, we assumed that each user has a single device. The real system actually checks photos uploaded by the same *user account*, which might use multiple devices. We ignored this fact in order to simplify the description.)