---
title: Test your understanding of the basics of fault tolerant distributed computing
date: 2025-10-22 05:30:00 -04:00
tags:
- dist101
- models
author: Ittai Abraham
---

The goal of this post is to motivate you to learn the basics of distributed computing by providing a set of simple questions that test your understanding of the basic definitions. In 2025, LLM-based chatbots score 100 on this test, so that's what you should aim for. The questions cover the standard models and fault assumptions you encounter in the first lectures of any distributed computing course.

The first questions cover the [network model](https://decentralizedthoughts.github.io/2019-06-01-2019-5-31-models/), the [threshold adversary model](https://decentralizedthoughts.github.io/2019-06-17-the-threshold-adversary/), and the [power of the adversary](https://decentralizedthoughts.github.io/2019-06-07-modeling-the-adversary/).

For the last question see the post on [state machine replication](https://decentralizedthoughts.github.io/2019-10-15-consensus-for-state-machine-replication/), then on [primary backup](https://decentralizedthoughts.github.io/2019-11-01-primary-backup/) and optionally [this post on linearizability](https://decentralizedthoughts.github.io/2021-10-16-the-ideal-state-machine-model-multiple-clients-and-linearizability/).

---

A

In the Synchronous model with parameter Δ which of the following are true:

1. Some message is sent at time t and arrives at time t+Δ/4.
2. Some message is sent at time t and arrives at time t+3Δ.
3. Any message sent at any time t arrives at time at most 2t.
4. The protocol designer does not know the value of Δ.

---

B

In the Asynchronous model which of the following are true:

1. There is some finite number Δ such that for every finite execution, all message delays in that execution are at most Δ.
2. Some messages that are sent may never arrive to their destinations.
3. For every finite execution, there is some finite number Δ such that all message delays in that execution are at most Δ.
4. The protocol designer can always assume that message sent will arrive after at most 1 day.

---

C

In the Partially Synchronous model with parameter Δ which of the following are true:

1. The protocol designer can design protocols that wait until they detect the Global Stabilization Time (GST) and then take advantage of synchrony.
2. A message sent 2Δ time before GST will have a delay of at most 3Δ.
3. There is some finite number λ such that for every execution, messages sent before GST have a delay of at most λ.
4. A message sent 2Δ time after GST will have a delay of at most 2Δ.

---

D

Which of the following are true:

1. Any execution in the Partially Synchronous model with parameter Δ is also a legal execution in the Synchronous model with parameter Δ.
2. Any execution in the Synchronous model with parameter 2Δ is also a legal execution in the Partially Synchronous model with parameter Δ.
3. Any execution in the Partially Synchronous model with parameter 2Δ is also a legal execution in the Asynchronous model.
4. There exists a number Δ, such that any execution in the Asynchronous model is also a legal execution in the Synchronous model with parameter Δ.


---

E

Which of the following are true:

1. In the dishonest minority model the adversary can corrupt at most half the parties but no more than that.
2. If the adversary can corrupt at most f<n/3 parties then for a fixed f, the smallest number n where this holds is n=3f+1.
3. If the adversary can corrupt at most f<n/2 parties, then any set of k<n/2 must contain at least one non-corrupt party.
4. When f<n/4 then any two sets of size n-f have at least 2f non-corrupt parties in the intersection.


---

F

Which of the following are true:

1. If f<n/3 then any two sets of size n-f intersect with at least f+1 non-faulty parties.
2. If f<n/5 then any two sets of size n-f intersect with at least 3f+1 parties.
3. If f<n/4 then any two sets of size n-f have at least 2f+1 parties in their intersection.
4. If f<n/2 then any two set of size n-f have at least two parties in their intersection.

---

G

Against a deterministic protocol:

1. An adaptive adversary has the same power as a static adversary.
2. A strongly adaptive adversary for omission faults can create executions that an adaptive adversary for omission cannot create.
3. The full information adversary has more information than the private channel adversary.
4. The mobile adversary has the same power as a fixed model adversary.

---

H

Which of the following are true:

1. Any adversary that can cause f omission corruptions can simulate an adversary that can cause f crash corruptions.
2. Any adversary that can cause f crash corruptions can simulate an adversary that can cause f malicious corruptions.
3. A static malicious adversary can always simulate an adaptive adversary that just does crash corruptions (for the same number of corruptions).
4. An omission corruption adversary can either block incoming messages or outgoing messages but not both.

---

I

In the first round, a protocol chooses a uniformly random sub-committee of size $<f$. Then only parties in the sub-committee send messages for two rounds.

1. A static adversary can always manage to block the sub-committee from sending messages.
2. A strongly adaptive adversary can always manage to block the sub-committee from sending messages.
3. A weakly adaptive adversary with parameter k=3 can always manage to block the sub-committee from sending messages their second round of messages.
4. A delayed adaptive adversary can always block the sub-committee from sending messages their first round of messages.

---

J

Consider a primary backup protocol (two clients and two servers, at most one server and all clients may crash, links are FIFO):

1. Show a concrete execution where the client library gets the same output sent to it more than once.
2. Show a concrete execution where the backup gets the same command sent to it more than once.


Once you’ve answered all parts (A–J), compare your reasoning with the models and examples linked above. Understanding not just which statements are true but why they are true is the key to mastering distributed computing.

Share your thoughts and questions on [X](https://x.com/ittaia/status/1980954770472132699).