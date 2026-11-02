---
title: "Union-find"
description: "The disjoint-set data structure — MakeSet, Find, Union — that tracks merging components, as in Kruskal's algorithm: labels with relabel-the-smaller-set give O(1) Find and O(V log V) for all Unions; a forest with union by rank and path compression gives O(α(V)) amortized per operation."
tags: [concept, algorithms, graphs]
aliases: ["Union-Find", "disjoint sets", "disjoint-set data structure", "disjoint-set forest", "union by rank", "path compression", "MakeSet", "inverse Ackermann function"]
---

> [!definition] Definition — union-find (disjoint sets)
> A **union-find** structure maintains a partition of a set of elements into disjoint sets under three operations:
> - MakeSet$(v)$: create the set $\{v\}$;
> - Find$(v)$: return an identifier of the set containing $v$ — equal for two elements exactly when they are in the same set;
> - Union$(u, v)$: replace the sets containing $u$ and $v$ by their union.

**Two implementations.**
- **Labels, relabel the smaller set** (the one in the book). Every element stores its set's label, and every set a list of its members. Find returns the label: $O(1)$. Union rewrites the labels of the **smaller** set: $O(\text{size of the smaller set})$. An element is relabeled only when its set at least doubles in size, so at most $\log_2 n$ times; any sequence of Unions on $n$ elements takes $O(n\log n)$ time in all.
- **A forest with union by rank and path compression** (the book's footnote). Every set is a rooted tree, and its root identifies it:

```text
MakeSet(v):
    parent(v) ← v;  rank(v) ← 0

Find(v):
    if parent(v) ≠ v
        parent(v) ← Find(parent(v))        ⟨⟨path compression⟩⟩
    return parent(v)

Union(u, v):
    x ← Find(u);  y ← Find(v)
    if x = y
        return
    if rank(x) > rank(y)
        swap x and y                       ⟨⟨union by rank⟩⟩
    parent(x) ← y
    if rank(x) = rank(y)
        rank(y) ← rank(y) + 1
```

Each operation takes $O(\alpha(n))$ amortized time (Tarjan, 1975), where $\alpha$ is the inverse Ackermann function — at most 4 for any input that fits in the universe. (Union by rank alone already keeps every tree's height at most $\log_2 n$.)

**Why it matters.** Kruskal's algorithm ([[2-algorithms/07-minimum-spanning-trees#75-kruskals-algorithm|§7.5]]) adds an edge $uv$ exactly when Find$(u)\ne$ Find$(v)$: it performs $V$ MakeSets, $2E$ Finds and $V-1$ Unions, which cost $O(E + V\log V)$ with labels or $O(E\,\alpha(V))$ with the forest — less than the $O(E\log V)$ sort either way. The same test detects cycles while edges are added to an undirected graph one at a time: $uv$ closes a cycle exactly when Find$(u) =$ Find$(v)$.

> [!trap]
> - **Union combines whole sets.** Linking $u$ to $v$ instead of root to root (or relabeling only $u$) breaks the partition.
> - **Relabel or link the smaller side.** Always relabeling the set of $u$, say, costs $\Theta(n)$ per Union in the worst case and $\Theta(n^2)$ in all; linking roots arbitrarily can build a path of height $n - 1$, making Find $\Theta(n)$.
> - **Identifiers change.** Compare Find$(u)$ and Find$(v)$ at the moment you need the answer; a label or root read before a Union may be stale.
> - **Amortized, not worst-case:** a single Union with labels can take $\Theta(n)$ time; only the total is $O(n\log n)$.

**Example.** Eight elements $1, \ldots, 8$ with labels, merged in balanced rounds: Union$(1,2)$, Union$(3,4)$, Union$(5,6)$, Union$(7,8)$, then Union$(1,3)$, Union$(5,7)$, then Union$(1,5)$, where on a tie the set of the second argument takes the first one's label. Each round relabels 4 elements, 12 relabelings in all, and element 8 — labeled $8$, then $7$, then $5$, then $1$ — is relabeled $3 = \log_2 8$ times: the bound is tight. The forest version on the same sequence ends with one tree of rank 3.

**Where it appears.** [[2-algorithms/07-minimum-spanning-trees#75-kruskals-algorithm|§7.5]] (Kruskal's algorithm and the analysis); component labels computed from scratch by CountAndLabel in [[2-algorithms/05-basic-graph-algorithms#56-important-variants|§5.6]] and in Borůvka's algorithm ([[2-algorithms/07-minimum-spanning-trees#73-borůvkas-algorithm|§7.3]]).

Related: [[concepts/minimum-spanning-trees]] · [[concepts/graphs]] · [[concepts/whatever-first-search]]
