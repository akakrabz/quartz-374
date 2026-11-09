---
title: "Comparison lower bounds"
description: "Decision trees and the information-theoretic lower bound: a problem with N possible outputs needs depth ⌈log_k N⌉, so every comparison sort makes at least ⌈lg n!⌉ = Ω(n log n) comparisons in the worst case — and what the bound does not cover (radix sort, hashing, problems with few outputs)."
tags: [concept, algorithms, lower-bounds]
aliases: ["decision tree", "decision-tree model", "comparison tree", "sorting lower bound", "information-theoretic lower bound", "information-theoretic bound"]
---

> [!key] The information-theoretic lower bound
> In the **decision-tree model** an algorithm is a tree: each internal node asks a query about the input, each edge is one answer, each leaf an output; the worst-case running time is the depth. In a **comparison tree** every query is "is $x_i < x_j$?" (two answers).
> - A problem with $N$ possible outputs needs $N$ leaves, so every $k$-ary decision tree for it has depth at least $\lceil\log_k N\rceil$.
> - **Sorting** $n$ distinct items has $n!$ outputs, so every comparison sort makes at least
> $$
> \lceil\lg n!\rceil \;\ge\; n\lg n - n\lg e \;=\; \Omega(n\log n)
> $$
> comparisons in the worst case. Mergesort and heapsort match it: sorting by comparisons is $\Theta(n\log n)$.

**Why it works.** A tree of depth $d$ with at most $k$ answers per query has at most $k^d$ leaves. Two inputs that need different outputs must reach different leaves, so the tree has at least as many leaves as there are outputs. Stirling's formula $n! > (n/e)^n$ turns $\lg n!$ into $n\lg n - O(n)$. The bound counts queries only, which is a lower bound on any real running time.

> [!recipe] Recipe — a counting lower bound
> 1. **Fix the model**: what one query is and how many answers it has (comparisons: 2).
> 2. **Count the outputs** $N$ that some inputs force — answers that must be told apart.
> 3. **Conclude** depth $\ge\lceil\log_k N\rceil$ and simplify ($\lg n! = n\lg n - O(n)$; $k\lg(n/k)\le\lg\binom{n}{k}\le k\lg(en/k)$).
> 4. If $N$ is small (a yes/no answer, an index), counting is weak: use an [[concepts/adversary-arguments|adversary argument]] instead.

> [!trap]
> - **The bound lives in the model.** Counting sort, radix sort and bucket sort use the values as array indices — queries with many outcomes; counting sort sorts $n$ integers from $\{0, \ldots, K-1\}$ in $O(n + K)$ time without a single comparison. Hashing answers membership in $O(1)$ expected time. Neither contradicts the bound.
> - **Few outputs, weak bound.** The maximum has only $n$ possible answers ($\lceil\lg n\rceil$ from counting) but needs $n - 1$ comparisons; "is the array sorted?" has 2 answers but also needs $n - 1$.
> - **It bounds the problem, not an algorithm.** "Sorting needs $\Omega(n\log n)$ comparisons" is the theorem; quicksort with arbitrary pivots still takes $\Theta(n^2)$ in its worst case.
> - **Worst case, comparisons.** It says nothing about the best case (insertion sort: $n - 1$ comparisons on sorted input), and nothing about other operations.

**Example.** Sorting 5 items: $\lceil\lg 120\rceil = 7$ comparisons are necessary. Mergesort uses up to 8. An exhaustive search over all comparison trees finds one of depth 7, so for $n = 5$ the bound is exact (it is for every $n\le 5$; for $n = 12$ it is known not to be: 30 comparisons are needed, not 29).

**Where it appears.** [[4-lecture-notes/12-lower-bounds#122-decision-trees|§12.2]] (decision trees), [[4-lecture-notes/12-lower-bounds#123-information-theory|§12.3]] (the bound, binary search), [[4-lecture-notes/12-lower-bounds#124-but-wait-a-second|§12.4]] (hashing), [[4-lecture-notes/12-lower-bounds#125-sorting|§12.5]] (sorting); combined with an adversary for the median in [[4-lecture-notes/13-adversary-arguments#138-finding-the-median|§13.8]]; mergesort and quicksort in [[2-algorithms/01-recursion#14-mergesort|§1.4]] and [[2-algorithms/01-recursion#15-quicksort|§1.5]].

Related: [[concepts/adversary-arguments]] · [[concepts/divide-and-conquer]] · [[concepts/linear-time-selection]] · [[concepts/fooling-sets]]
