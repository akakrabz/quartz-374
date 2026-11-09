---
title: "Adversary arguments"
description: "Lower bounds by playing against the algorithm: an adversary answers every query consistently but unhelpfully, and an algorithm that stops early cannot tell apart two inputs with different answers. Evasive properties (all bits or all adjacency entries must be read), the maximum (n − 1 comparisons) and min-and-max (⌈3n/2⌉ − 2)."
tags: [concept, algorithms, lower-bounds]
aliases: ["adversary argument", "adversary", "evasive property", "evasive", "evasive graph property"]
---

> [!definition] Definition — adversary argument, evasive
> To prove that every algorithm in a model needs at least $q$ queries in the worst case, describe an **adversary** that answers each query, always consistently with at least one input, and show: after fewer than $q$ queries, two inputs are consistent with every answer given but require different outputs. The algorithm's output depends only on the answers, so it is wrong on one of them.
>
> A property of $n$-bit strings — or of $n$-vertex graphs given by an adjacency matrix — is **evasive** if every algorithm must examine all $n$ bits (all $\binom n2$ entries) in the worst case.

**Why it works.** The algorithm never sees the input, only answers; an adversary that answers consistently is indistinguishable from an honest user who fixed the input in advance, so it may postpone choosing the input until the end. It assumes nothing about the algorithm, so one adversary defeats every algorithm at once. Counting outputs ([[concepts/comparison-lower-bounds]]) fails when there are few outputs; an adversary still works.

> [!recipe] Recipe — writing an adversary argument
> 1. **Model**: what one query is (a bit, an adjacency entry, a comparison).
> 2. **State**: what the adversary has committed to so far — marks, a prefix and suffix, a "yes" graph and a "maybe" graph.
> 3. **Answer rule** for **every** possible query, and an invariant showing some input agrees with all answers.
> 4. **Progress measure**: the algorithm must reduce some quantity by $R$, and **every** possible query reduces it by at most $c$, so it needs at least $R/c$ queries.
> 5. **Ending**: if it stops earlier, exhibit two consistent inputs with different correct outputs.

| problem | model | lower bound | the adversary |
|---|---|---|---|
| is any bit 1? | bit probes | $n$: evasive | always answer 0 |
| does the string contain 01? | bit probes | $n$ iff $n$ is even | keep 1s up to $\ell$, 0s from $r$, an even gap |
| is the graph connected? | adjacency matrix | $\binom n2$: evasive | delete the edge unless that disconnects |
| maximum of $n$ | comparisons | $n - 1$ | answer as if $x_i = i$; each comparison has one new loser |
| minimum and maximum | comparisons | $\lceil 3n/2\rceil - 2$ | $2n - 2$ of $2n$ marks must go; at most $\lfloor n/2\rfloor$ comparisons remove two |

> [!trap]
> - **Consistency is the whole point.** At the end the adversary must exhibit actual inputs that agree with every answer; an adversary that "changes its mind" inconsistently proves nothing.
> - **Every query order.** An argument that assumes the algorithm scans left to right bounds only those algorithms. (Assuming no query is repeated is harmless: a repeated query gets the same answer, so dropping it never costs more.)
> - **Evasiveness depends on $n$.** 01 is evasive only for even $n$; for odd $n$, $n - 1$ probes suffice.

**Example.** Is $x_1 < x_2 < \cdots < x_n$? There are only 2 outputs, so counting gives 1, but $n - 1$ comparisons are needed. The adversary answers as if $x_i = i$. If the algorithm stops without having compared some neighbors $x_i$ and $x_{i+1}$, swap their values: no other element lies between them, so every answer stays the same, but the input is no longer sorted. Exhaustive search over comparison trees confirms $n - 1$ for $n\le 6$.

**Where it appears.** The maximum in [[4-lecture-notes/12-lower-bounds#126-finding-the-maximum-and-adversaries|§12.6]]; bit strings in [[4-lecture-notes/13-adversary-arguments#132-n-card-monte|§13.2]] and [[4-lecture-notes/13-adversary-arguments#133-finding-patterns-in-bit-strings|§13.3]]; graph properties in [[4-lecture-notes/13-adversary-arguments#134-evasive-graph-properties|§13.4]]–[[4-lecture-notes/13-adversary-arguments#136-an-evasive-conjecture|§13.6]]; min and max in [[4-lecture-notes/13-adversary-arguments#137-finding-the-minimum-and-maximum|§13.7]]; the median in [[4-lecture-notes/13-adversary-arguments#138-finding-the-median|§13.8]]. Fooling sets ([[concepts/fooling-sets]]) are the automata version of the same idea.

Related: [[concepts/comparison-lower-bounds]] · [[concepts/fooling-sets]] · [[concepts/linear-time-selection]] · [[concepts/minimum-spanning-trees]]
