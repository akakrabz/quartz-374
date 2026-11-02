---
title: "Recursion trees"
description: "Solve a divide-and-conquer recurrence by adding up its recursion tree level by level: decreasing level sums mean the root dominates, equal sums mean levels times level sum, increasing sums mean the leaves dominate. With the n^d shortcut, floors and ceilings, and recurrences that fit none of the cases."
tags: [concept, algorithms, recursion, midterm-2]
aliases: ["recursion tree", "recursion-tree method", "solving recurrences", "level sums"]
---

> [!key] The recursion-tree method
> A recursion tree has one node per recursive subproblem, valued at the work done there *excluding* recursive calls; the running time is the sum of all values. For $T(n) = r\,T(n/c) + f(n)$, level $i$ has $r^i$ nodes of value $f(n/c^i)$, the depth is $L = \log_c n$, there are $n^{\log_c r}$ leaves, and
> $$
> T(n) = \sum_{i=0}^{L} r^i f(n/c^i).
> $$
> - **Decreasing** geometric level sums: the root dominates, $T(n) = \Theta(f(n))$.
> - **Equal** level sums: $T(n) = \Theta(f(n)\log n)$.
> - **Increasing** geometric level sums: the leaves dominate, $T(n) = \Theta(n^{\log_c r})$.
>
> For $f(n) = n^d$: compare $r$ with $c^d$ — smaller gives $\Theta(n^d)$, equal gives $\Theta(n^d\log n)$, larger gives $\Theta(n^{\log_c r})$.

**Why it works.** A geometric series is within a constant factor of its largest term. When the level sums shrink, that term is the root's $f(n)$; when they grow, it is the bottom level, made of $n^{\log_c r}$ leaves of constant value; when they are equal, all $L+1 = \Theta(\log n)$ levels count. Nothing requires the tree to be balanced — only the level sums matter — and floors, ceilings and lower-order terms can be removed by a domain transformation, so they are ignored.

> [!recipe] Using it
> 1. Write the recurrence; drop floors, ceilings and lower-order terms.
> 2. Draw the root and two more levels, and add up each level.
> 3. Name the case. In the increasing case, count the leaves: $r^{\log_c n} = n^{\log_c r}$.
> 4. If no case applies, bound each level and the number of levels separately (at most $n$ per level times $O(\log n)$ levels), or sum the series exactly.
> 5. On an exam, write the recurrence *and* the solution, and say which case applies.

> [!trap]
> - "Equal" means equal level **sums**, not equal node values.
> - Level sums that shrink by a non-geometric amount fit no case: $2T(n/2) + n\lg n$ has level sums $n(\lg n - i)$ and solution $\Theta(n\log^2 n)$, not $\Theta(n\log n)$.
> - The base of a logarithm matters in an exponent ($n^{\log_2 3}\ne n^{\log_4 3}$) but not in a factor ($\log_2 n = \Theta(\log_3 n)$).
> - $T(n) = T(n-1) + n$ is not a divide-and-conquer recurrence: the tree is a path of $n$ nodes; sum it directly ($\Theta(n^2)$).
> - $T(n) = T(n/3) + T(2n/3) + O(n)$ is $\Theta(n\log n)$, not $\Theta(n)$: the subproblem sizes add up to $n$, so the level sums do not shrink.

**Example: Strassen's recurrence.** $T(n) = 7T(n/2) + n^2$ (the recurrence of Strassen's matrix multiplication). Level $i$ has $7^i$ nodes of value $(n/2^i)^2 = n^2/4^i$, so it sums to $(7/4)^i n^2$ — increasing. The leaves dominate: there are $7^{\lg n} = n^{\lg 7}$ of them, so $T(n) = \Theta(n^{\lg 7}) \approx \Theta(n^{2.807})$, beating the $\Theta(n^3)$ of $8T(n/2) + n^2$. With $T(1) = 1$ the exact value at powers of two is $T(2^k) = (7^{k+1} - 4^{k+1})/3$.

The same three cases as a formula for $T(n) = a\,T(n/b) + f(n)$ — with exact conditions, the recurrences they miss, and Akra–Bazzi for unequal splits — are the [[concepts/master-theorem|Master Theorem]].

**Where it appears.** [[2-algorithms/01-recursion#17-recursion-trees|§1.7]] (the method, a table of worked recurrences, ignoring floors and ceilings), [[2-algorithms/01-recursion#14-mergesort|§1.4]] mergesort (equal), [[2-algorithms/01-recursion#18-linear-time-selection|§1.8]] selection (decreasing, and why blocks of 3 fail), [[2-algorithms/01-recursion#19-fast-multiplication|§1.9]] multiplication (increasing), [[2-algorithms/01-recursion#110-exponentiation|§1.10]] repeated squaring.

Related: [[concepts/divide-and-conquer]] · [[concepts/recursion]] · [[concepts/linear-time-selection]]
