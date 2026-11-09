---
title: "Treaps and skip lists"
description: "Randomized search structures: a treap is a binary search tree on keys that is a min-heap on random priorities (expected depth H_k + H_{n−k+1} − 2 < 2 ln n, O(log n) with high probability); a skip list is a sorted list with coin-flip shortcuts (O(log n) levels and searches with high probability)."
tags: [concept, algorithms, data-structures]
aliases: ["treap", "randomized treap", "Cartesian tree", "randomized binary search tree", "skip list", "skip lists"]
---

> [!definition] Definition
> A **treap** is a binary tree whose nodes have a search key and a priority, in binary-search-tree order by key and in min-heap order by priority. With distinct keys and priorities its shape is unique: the BST obtained by inserting the nodes in increasing order of priority. Insert = BST insertion + rotations up while the new node's priority is smaller than its parent's; delete = rotate down at the child of smaller priority, then cut; split and join use a dummy node of priority $-\infty$. A **randomized treap** draws each priority independently and uniformly at random; then, for the node $x_k$ of $k$th smallest key,
> $$
> \begin{aligned}
> \Pr[x_i \text{ is a proper ancestor of } x_k] &= \frac{[i\ne k]}{\lvert k-i\rvert+1},\\
> \mathrm{E}[\mathit{depth}(x_k)] &= H_k + H_{n-k+1} - 2 < 2\ln n .
> \end{aligned}
> $$
> A **skip list** stores a sorted list on level 0 and copies each element up one level per heads in a row of fair coin flips; a search moves right on each level as far as it can without passing the target, then drops down.

**Why it works.** $x_i$ is an ancestor of $x_k$ exactly when its priority is the smallest among the $\lvert k-i\rvert+1$ nodes with keys between them, each equally likely; summing gives the depth. The indicators on each side of $k$ are mutually independent, so a Chernoff bound gives depth $\le 8\ln n$ for all nodes with probability $> 1 - 2/n$. In a skip list a key reaches level $\ell$ with probability $2^{-\ell}$; by the union bound there are at least $c\lg n$ levels with probability at most $1/n^{c-1}$, and a search, traced backwards, climbs one level per heads.

> [!recipe] Recipe — expected cost by indicator variables
> 1. Write the cost as a sum of 0/1 events, e.g. $\mathit{depth}(x_k) = \sum_i[x_i\text{ is an ancestor of }x_k]$.
> 2. Characterize each event by the random choices alone (here: "$x_i$ has the smallest priority in $X(i,k)$").
> 3. Compute each probability by symmetry and add: harmonic sums give logarithms.
> 4. For "with high probability", check which indicators are independent and apply a Chernoff bound, then a union bound over the $n$ nodes.

> [!trap]
> - **Only the priorities are random.** Keys and operations must not depend on the random choices; an adversary who sees them can force bad behavior.
> - **Heap order is min-order here**: the root has the *smallest* priority.
> - **$\mathrm{E}[\text{max depth}]$ is not $\max\mathrm{E}[\text{depth}]$**: the expected-depth formula is per node; the bound on the height needs a tail inequality.
> - **Not all ancestor indicators are independent** — only those on one side of $k$; the high-probability proof splits the depth in two.

**Example.** For $n = 4$, the 24 priority orders give expected depths $13/12$, $4/3$, $4/3$, $13/12$ for $x_1,\dots,x_4$, matching $H_k + H_{5-k} - 2$; for instance $x_1$ is an ancestor of $x_4$ in exactly the $6 = 24/4$ orders in which $x_1$ comes first among the four. The total, $29/6 = 2\cdot5\cdot H_4 - 16$, is the expected number of comparisons of randomized quicksort on 4 keys. For a skip list with $n = 1000$ keys, $\Pr[L\ge 20]\le 1000/2^{20} < 0.001$.

**Where it appears.** Erickson's note 3: [[4-lecture-notes/03-treaps-and-skip-lists#311-definitions|§3.1.1]] (definition, uniqueness), [[4-lecture-notes/03-treaps-and-skip-lists#312-treap-operations|§3.1.2]] (rotations, insert, delete, split, join), [[4-lecture-notes/03-treaps-and-skip-lists#313-random-priorities|§3.1.3]] (expected depth), [[4-lecture-notes/03-treaps-and-skip-lists#314-randomized-quicksort-again|§3.1.4]] (quicksort), [[4-lecture-notes/03-treaps-and-skip-lists#32-skip-lists|§3.2]] (skip lists); note 4: [[4-lecture-notes/04-tail-inequalities#48-back-to-treaps-take-2|§4.8]] (depth $O(\log n)$ with high probability); random-pivot quicksort in [[2-algorithms/01-recursion#15-quicksort|§1.5]].

Related: [[concepts/discrete-probability]] · [[concepts/tail-inequalities]] · [[concepts/optimal-binary-search-trees]] · [[concepts/splay-trees]] · [[concepts/divide-and-conquer]]
