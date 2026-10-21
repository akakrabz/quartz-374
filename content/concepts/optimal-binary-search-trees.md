---
title: "Optimal binary search trees"
description: "Sorted keys with search frequencies: build the binary search tree with the least total search cost by an interval recurrence over the choice of root — O(n^2) subproblems, O(n^3) time — and why the most frequent key need not be the root."
tags: [concept, algorithms, dynamic-programming, midterm-2]
aliases: ["optimal BST", "OptCost", "optimal search tree"]
---

> [!definition] Problem and recurrence
> Given sorted keys $A[1\,..\,n]$ and frequencies $f[1\,..\,n]$, find a binary search tree minimizing $\sum_i f[i]\cdot \mathrm{depth}(A[i])$, where the root has depth 1 (the total number of comparisons). Let $F[i,k] = f[i] + \cdots + f[k]$, and for $1\le i\le n+1$, $i-1\le k\le n$ let $\textsf{OptCost}(i,k)$ be the cost of an optimal tree for the keys $A[i\,..\,k]$; we need $\textsf{OptCost}(1,n)$.
> $$
> \textsf{OptCost}(i,k) = \begin{cases} 0 & \text{if } i > k\\ F[i,k] + \min\limits_{i\le r\le k}\big\{\textsf{OptCost}(i,r-1) + \textsf{OptCost}(r+1,k)\big\} & \text{otherwise}\end{cases}
> $$
> Memoize in $\mathit{OptCost}[1\,..\,n+1,\ 0\,..\,n]$ after precomputing $F$ in $O(n^2)$; fill by increasing $k - i$ (or rows bottom-up, or columns left to right): $O(n^2)$ space, $O(n^3)$ time.

**Why it works.** Whichever key $A[r]$ is at the root, every search passes through it — that is the $F[i,k]$ term, one comparison per search — and below the root the left and right subtrees are search trees for $A[i\,..\,r-1]$ and $A[r+1\,..\,k]$. Each must be optimal for its own interval (otherwise swapping in a better one improves the whole tree), so trying every root $r$ finds the optimum.

> [!recipe] Recipe — the interval pattern
> 1. Subproblem = a contiguous **interval** $A[i\,..\,k]$ ([[concepts/dynamic-programming|rubric]]: "the portion of the input is an interval").
> 2. Choose a split point $r$ inside the interval; combine the two smaller intervals with a cost computed from $i$, $k$ and $r$ (here $F[i,k]$, the same for every $r$).
> 3. Evaluate shorter intervals first; $O(n^2)$ intervals $\times$ $O(n)$ split points $= O(n^3)$ time.
> 4. Two parameters predict $O(n^2)$ space; three free indices $i, k, r$ predict $O(n^3)$ time.

> [!trap]
> - **Greed fails.** "Put the most frequent key at the root" is wrong already for three keys with $f = (2,3,4)$: it builds the path $A[3], A[2], A[1]$ with cost $4\cdot1 + 3\cdot2 + 2\cdot3 = 16$, but the balanced tree with root $A[2]$ costs $3\cdot1 + (2+4)\cdot2 = 15$.
> - Add the whole $F[i,k]$, not just $f[r]$: every key in the interval gets one level deeper.
> - The empty intervals $\textsf{OptCost}(i,i-1) = 0$ are base cases for all $1\le i\le n+1$.
> - Row by row from the top is **not** a valid order: entry $(i,k)$ reads entries below it in column $k$.
> - $O(n^2)$ entries, but $O(n)$ work each: $O(n^3)$ time.

**Example.** For $f = (2,3,4)$: $F[1,3] = 9$, and the roots $r = 1, 2, 3$ give $\mathit{OptCost}[2,3] = 10$, $\mathit{OptCost}[1,1] + \mathit{OptCost}[3,3] = 2 + 4 = 6$, and $\mathit{OptCost}[1,2] = 7$. The minimum is 6, at $r = 2$, so $\mathit{OptCost}[1,3] = 9 + 6 = 15$ — the balanced tree, not the greedy one.

**Where it appears.** [[2-algorithms/03-dynamic-programming#39-optimal-binary-search-trees|§3.9]] (the dynamic program, three evaluation orders, a five-key example and an off-by-one in the book's column order), [[2-algorithms/02-backtracking#28-optimal-binary-search-trees|§2.8]] (the backtracking recurrence it memoizes), [[2-algorithms/03-dynamic-programming#34-the-pattern-smart-recursion|§3.4]] (its dependency picture).

Related: [[concepts/dynamic-programming]] · [[concepts/backtracking]] · [[concepts/memoization]] · [[concepts/edit-distance]]
