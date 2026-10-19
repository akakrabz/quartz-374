---
title: "Dynamic programming on trees"
description: "When the input is a tree: subproblems are subtrees, the memoization structure is the tree itself, the evaluation order is post-order, and the time is O(n) — maximum independent set and minimum vertex cover as examples."
tags: [concept, algorithms, dynamic-programming, midterm-2]
aliases: ["tree DP", "DP on trees", "maximum independent set in a tree", "post-order dynamic programming"]
---

> [!definition] The pattern
> Root the tree at any vertex $r$. For every vertex $v$, define one function — or one per **state** of $v$, such as "$v$ is in the solution" and "$v$ is not" — of the **subtree rooted at $v$**, by a recurrence over the children of $v$ (leaves are the base cases). Memoize each value in a **field of the node** $v$, evaluate in **post-order** (every vertex after its children), and the total time is
> $$
> \sum_{v} O(1 + \text{number of children of } v) = O(n),
> $$
> because every vertex except the root is the child of exactly one vertex.

**Why it works.** Removing $v$ splits its subtree into the children's subtrees, which share no edges, so a solution for the subtree of $v$ is a choice for $v$ plus independent solutions for the children's subtrees — compatible with the choice at $v$. Recording the choice at $v$ as a state (in/out) is what makes the children's subproblems independent of one another.

> [!recipe] Recipe — writing up a tree dynamic program
> 1. "Root $T$ at an arbitrary vertex $r$." (Unrooted trees need this sentence.)
> 2. Define the functions on subtrees, in English, one per state: "$\textsf{MISyes}(v)$ is the size of a largest independent set of the subtree rooted at $v$ that contains $v$; $\textsf{MISno}(v)$, one that excludes $v$. We need $\max\{\textsf{MISyes}(r), \textsf{MISno}(r)\}$."
> 3. Recurrences over the children: $\textsf{MISyes}(v) = 1 + \sum_{w\downarrow v}\textsf{MISno}(w)$, $\textsf{MISno}(v) = \sum_{w\downarrow v}\max\{\textsf{MISyes}(w), \textsf{MISno}(w)\}$.
> 4. Memoization: two fields per node (or arrays indexed by vertex number). Order: post-order traversal. Time: $O(n)$.

> [!trap]
> - **Forgetting a state.** One function "largest independent set of the subtree" needs the grandchildren to handle "$v$ is in" (the book's first version); two states need only children.
> - **No memoization.** The grandchildren recurrence evaluated naively recomputes subtrees: on an $n$-vertex path rooted at an end it makes $F_{n+2} - 1$ calls — exponential.
> - **"Portion of the input"** for the rubric is *the subtree rooted at $v$*: say so.
> - A hash table keyed by vertices still earns nothing; use node fields or an array indexed by vertex.

**Example — smallest vertex cover of a tree.** A **vertex cover** contains at least one endpoint of every edge. For every vertex $v$ let $\textsf{VCin}(v)$ and $\textsf{VCout}(v)$ be the sizes of a smallest vertex cover of the subtree rooted at $v$ that contains, respectively excludes, $v$:
$$
\textsf{VCin}(v) = 1 + \sum_{w\downarrow v}\min\{\textsf{VCin}(w), \textsf{VCout}(w)\},\qquad \textsf{VCout}(v) = \sum_{w\downarrow v}\textsf{VCin}(w),
$$
because if $v$ is left out, every child must cover its edge to $v$. We need $\min\{\textsf{VCin}(r), \textsf{VCout}(r)\}$, in $O(n)$ time. On the 11-vertex tree of the [[2-algorithms/03-dynamic-programming#310-dynamic-programming-on-trees|§3.10 figure]] the answer is 3 — for example the root and its two grandchildren that are not leaves — and $3 = 11 - 8$, as it must be: in any graph, the complement of an independent set is a vertex cover, and the complement of a vertex cover is an independent set.

**Where it appears.** [[2-algorithms/03-dynamic-programming#310-dynamic-programming-on-trees|§3.10]] (maximum independent set in a tree: the one-function and the two-function versions, TreeMIS and TreeMIS2, and the figure), [[2-algorithms/03-dynamic-programming#34-the-pattern-smart-recursion|§3.4]] (choosing a memoization structure that is not an array).

Related: [[concepts/dynamic-programming]] · [[concepts/memoization]] · [[concepts/recursion]] · [[concepts/backtracking]]
