---
title: "Memoization"
description: "Store the value of every recursive call the first time it is computed and look it up afterwards: the step that turns an exponential backtracking algorithm into a polynomial one, and how memoized recursion differs from deliberate table filling."
tags: [concept, algorithms, dynamic-programming, midterm-2]
aliases: ["memoisation", "memoized recursion", "memo table", "top-down dynamic programming"]
---

> [!definition] Definition — memoization
> **Memoization** (yes, without an "r") stores the value of each recursive call, the first time it is computed, in a data structure indexed by the call's parameters, and answers every later call with the same parameters by a look-up. A memoized algorithm does the non-recursive work of each **distinct** subproblem once, so its running time is the sum of that work over all distinct subproblems (plus $O(1)$ per look-up).

**Why it helps.** The recursion tree of a backtracking algorithm often contains the same subtree many times: RecFibo$(n)$ calls RecFibo$(n-k)$ $F_{k+1}$ times, $2F_{n+1}-1$ calls in all, while MemFibo$(n)$ makes only $2n-1$. Memoization changes *how often* a value is computed, never *what* it is: the algorithm is correct exactly when the recurrence is.

**Memoized recursion versus dynamic programming.** A memoized recursion fills its table in whatever order the recursion reaches the entries (MemFibo happens to fill $F[2], F[3], \ldots$ bottom up). A dynamic programming algorithm fills the same table **deliberately**, with loops, in an order where every entry's dependencies come first. The time bound is usually the same; the loops make the order and the analysis explicit and avoid deep recursion. Memoization evaluates only the subproblems that are actually reached, while the loops fill every entry — for subset sum, all $(n+1)(T+1)$ of them.

> [!recipe] Recipe — memoizing a recursive algorithm
> 1. Check that the function's value depends **only on its parameters** (and the fixed input).
> 2. Allocate an array indexed by the parameters, every entry "undefined".
> 3. In each call: if the entry is defined, return it; otherwise evaluate the recurrence, store the value, return it.
> 4. Time: (number of distinct subproblems) $\times$ (work per subproblem, not counting recursive calls).
> 5. Then, usually, replace the recursion by loops in a valid evaluation order (see [[concepts/dynamic-programming]]).

> [!trap]
> - **State outside the parameters** ("the best total so far", a global flag) makes memoized values wrong: two calls with equal parameters must have equal values.
> - **Hash tables** are not an acceptable memoization structure in this course's rubric; use an array indexed by the parameters (or fields in the nodes of a tree).
> - **Count distinct subproblems, not calls** — but if the parameters range over subsets or arbitrary strings, there are exponentially many distinct subproblems and memoization does not help.
> - Memoizing a **wrong recurrence** gives a fast wrong algorithm.

**Example — binomial coefficients.** $\textsf{Choose}(n,k) = \textsf{Choose}(n-1,k-1) + \textsf{Choose}(n-1,k)$, with $\textsf{Choose}(n,0) = \textsf{Choose}(n,n) = 1$. Without memoization the recursion tree has $\binom{n}{k}$ leaves, each returning 1, so it makes $2\binom{n}{k} - 1$ calls: $503$ calls for $\binom{10}{5} = 252$. Memoized, the only non-base subproblems are $\textsf{Choose}(n', k')$ with $1\le k'\le k$ and $1\le n'-k'\le n-k$ — exactly $k(n-k) = 25$ of them, each computed once — and the algorithm makes $2k(n-k)+1 = 51$ calls: $O(nk)$ time instead of exponential.

**Where it appears.** [[2-algorithms/03-dynamic-programming#31-matravrtta-fibonacci-numbers|§3.1]] (RecFibo, MemFibo and the recursion tree trimmed by memoization), [[2-algorithms/03-dynamic-programming#33-interpunctio-verborum-redux|§3.3]] (memoizing $\textsf{Splittable}$), [[2-algorithms/03-dynamic-programming#34-the-pattern-smart-recursion|§3.4]] (choosing a memoization structure), [[2-algorithms/03-dynamic-programming#38-subset-sum|§3.8]] (when filling every entry is wasteful), [[2-algorithms/03-dynamic-programming#310-dynamic-programming-on-trees|§3.10]] (memoizing in the tree's nodes).

Related: [[concepts/dynamic-programming]] · [[concepts/backtracking]] · [[concepts/recursion]] · [[concepts/dynamic-programming-on-trees]]
