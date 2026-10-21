---
title: "Dynamic programming on dags"
description: "Every recurrence has a dependency dag: memoization is a depth-first search of it and dynamic programming evaluates it in postorder (reverse topological order). The model problem — longest or shortest paths in a dag in O(V + E) time — and how sequence-type dynamic programs such as LIS and edit distance are paths in dags."
tags: [concept, algorithms, dynamic-programming, graphs, midterm-2]
aliases: ["DP on dags", "longest path in a dag", "shortest path in a dag", "dependency graph", "evaluation order"]
---

> [!definition] The pattern
> In the **dependency graph** of a recurrence, every subproblem is a vertex, with an edge $x\to y$ when evaluating $x$ needs $y$; it is a dag, or the recursion would not halt. **Memoized recursion is a depth-first search** of this dag, and **dynamic programming evaluates it in postorder** — a reverse topological order, every subproblem after the ones it needs. The model problem is the longest path to $t$ in a dag $G$ with edge weights $\ell$:
> $$
> \textsf{LLP}(v) = \begin{cases} 0 & \text{if } v = t\\ \max\{\ell(v\to w) + \textsf{LLP}(w) \mid v\to w\in E\} & \text{otherwise,}\end{cases}\qquad \max\varnothing = -\infty,
> $$
> whose dependency graph is $G$ itself: memoize in the vertices, evaluate in postorder, $O(V+E)$ time. Shortest paths use $\min$ (and $\min\varnothing = +\infty$); weights may be negative.

**Why it works.** In a dag every edge $v\to w$ has $v.\mathit{post} > w.\mathit{post}$, so in postorder every value is computed before it is read, and each vertex costs $O(1 + \text{out-degree})$. Acyclicity is essential: in a general directed graph the longest path problem is NP-hard. Almost every dynamic program that picks an optimal **sequence** of decisions is a longest or shortest path in its dependency dag; tree-shaped ones (optimal binary search trees, independent sets in trees) are not.

> [!recipe] Recipe — a problem that is a path in a dag (graph-reduction write-up)
> 1. **The graph:** vertices, **directed** edges and weights as explicit functions of the input; say why it is acyclic (for instance, every edge goes from a smaller index to a larger one).
> 2. **The problem on the graph:** "the answer is the longest (shortest) path from … to …", and why paths correspond to the objects being optimized.
> 3. **The algorithm:** longest (shortest) path in a dag by dynamic programming ($\textsf{LLP}$ above, evaluated in postorder) — cite it.
> 4. **The time** $O(V+E)$, rewritten in the input's parameters.

> [!trap]
> - **A cycle breaks it.** If the graph may have cycles, first contract the strong components (they form a dag) — or the problem may be NP-hard.
> - **Unreachable targets** get $-\infty$ (or $+\infty$ for shortest paths), not 0.
> - **"Try all paths with DFS"** is exponential; the dynamic program visits each vertex and edge once.
> - **Count the edges:** a dag built from an array of length $n$ can have $\Theta(n^2)$ edges, and the time is $O(V+E)$, not $O(V)$.
> - The book's two chapters draw dependency edges in opposite directions; with edges from a needed subproblem to the one that needs it, the evaluation order is a topological order rather than a reverse one. Say which convention you use.

**Example — longest increasing subsequence as a longest path.** Given $A[1\,..\,n]$, add sentinels $A[0] = -\infty$ and $A[n+1] = +\infty$. Build the graph with vertices $0, 1, \ldots, n+1$ and an edge $i\to j$ of weight 1 whenever $i < j$ and $A[i] < A[j]$; it is a dag because every edge goes left to right. Increasing subsequences of $A$ correspond exactly to the inner vertices of paths from $0$ to $n+1$, so the length of the longest increasing subsequence is $\textsf{LLP}(0) - 1$ with target $t = n+1$. The graph has $O(n^2)$ edges, so the time is $O(n^2)$ — the bound of the dynamic programs of Chapter 3. For $A = [5, 2, 8, 6, 3, 6, 9, 7]$ the graph has 10 vertices and 36 edges, $\textsf{LLP}(0) = 5$, and the answer is 4, for example $2, 3, 6, 9$.

**Where it appears.** [[2-algorithms/06-depth-first-search#64-memoization-and-dynamic-programming|§6.4]] (memoization as depth-first search, LongestPath in both forms, the weighted example, edit distance as a shortest path), [[2-algorithms/03-dynamic-programming#34-the-pattern-smart-recursion|§3.4]] (dependencies and evaluation orders), [[2-algorithms/03-dynamic-programming#36-longest-increasing-subsequence|§3.6]] and [[2-algorithms/03-dynamic-programming#37-edit-distance|§3.7]] (the recurrences that become paths).

Related: [[concepts/dynamic-programming]] · [[concepts/memoization]] · [[concepts/topological-sort]] · [[concepts/depth-first-search]] · [[concepts/longest-increasing-subsequence]] · [[concepts/edit-distance]] · [[concepts/dynamic-programming-on-trees]]
