---
title: "Matroids"
description: "A ground set with a hereditary family of independent sets that satisfies the exchange property; exactly the structures on which the heaviest-first greedy algorithm finds a maximum-weight basis for every choice of weights."
tags: [concept, algorithms, greedy]
aliases: ["matroid", "graphic matroid", "linear matroid", "uniform matroid", "exchange property", "GreedyBasis", "matroid optimization"]
---

> [!definition] Definition — matroid
> A **matroid** $(S, \mathcal{I})$ is a finite ground set $S$ with a family $\mathcal{I}$ of **independent** subsets such that $\varnothing\in\mathcal{I}$; every subset of an independent set is independent (**heredity**); and if $X, Y\in\mathcal{I}$ with $\lvert X\rvert > \lvert Y\rvert$, then $Y\cup\{x\}\in\mathcal{I}$ for some $x\in X\setminus Y$ (**exchange**). A **basis** is a maximal independent set — all bases have the same size — and a **circuit** is a minimal dependent set.
> - **Uniform** $U_{k,n}$: the sets of at most $k$ of $n$ elements. **Linear:** linearly independent sets of columns of a matrix. **Graphic** $M(G)$: the forests of a graph; bases are the spanning trees of a connected $G$, circuits its cycles. **Scheduling:** sets of unit tasks that can all meet their deadlines.
> - **GreedyBasis:** sort by decreasing weight; keep each element whose addition leaves the kept set independent. On a matroid it returns a **maximum-weight basis** for every weight function (Theorem E.1), in $O(n\log n + n\,F(n))$ time when independence is tested in $F(n)$ time.

**Why it works.** Compare the greedy basis $g_1, g_2, \ldots$ with any basis $h_1, h_2, \ldots$, both sorted by weight. If $w(g_i) < w(h_i)$ at the first index where greedy falls behind, exchange gives an $h_j$ with $j\le i$ that extends $\{g_1, \ldots, g_{i-1}\}$; it is heavier than $g_i$, so greedy met it earlier and would have kept it. Conversely, if exchange fails for $X$ and $Y$ with $\lvert Y\rvert = m$, weights $m+2$ on $Y$, $m+1$ on $X\setminus Y$ and 0 elsewhere make greedy take $Y$ and get stuck at $m(m+2) < (m+1)^2\le w(X)$ (Theorem E.2). So a hereditary family is a matroid **exactly when** greedy is optimal for all non-negative weights (Rado–Edmonds).

> [!recipe] Recipe — using the matroid view
> 1. **Name the ground set and the independent sets**, and check heredity.
> 2. **Check exchange**: for independent $\lvert X\rvert = \lvert Y\rvert + 1$, find an $x\in X\setminus Y$ with $Y + x$ independent — or a pair where none works, which is a counterexample family for greedy.
> 3. **Give an independence test** and its time $F(n)$; GreedyBasis then costs $O(n\log n + nF(n))$.
> 4. For a minimum-weight basis, scan from the lightest element instead (all bases have the same size, so this is the maximum for $-w$).

> [!trap]
> - **Heredity is not enough**: non-overlapping classes and matchings as edge sets are hereditary but not matroids, and heaviest-first greedy fails on them.
> - **Weights of any sign** are fine for a maximum-weight *basis*; for a maximum-weight independent set, stop before the first negative weight.
> - **In a CS 374 proof**, prove the greedy algorithm directly with an exchange argument; "it is a matroid" without a proof of exchange proves nothing.

**Example.** Ground set: the vectors $v_1 = (1,0,0)$, $v_2 = (0,1,0)$, $v_3 = (1,1,0)$, $v_4 = (0,0,1)$, $v_5 = (1,1,1)$ with weights 5, 4, 6, 2, 3 (a linear matroid of rank 3). Greedy scans $v_3, v_1, v_2, v_5, v_4$: it keeps $v_3$ and $v_1$, rejects $v_2 = v_3 - v_1$, keeps $v_5$ (not in the plane $z = 0$), and rejects $v_4$, which would make four vectors in $\mathbb{R}^3$. The basis $\{v_3, v_1, v_5\}$ weighs $6 + 5 + 3 = 14$, the maximum over the 8 bases (the next best weighs 13). $\{v_1, v_2, v_3\}$ is a circuit: dependent, while any two of its vectors are independent.

**Where it appears.** [[4-lecture-notes/e-matroids#e1-definitions|Note E §E.1]] (definitions, the six examples, Theorems E.1 and E.2), [[4-lecture-notes/e-matroids#e2-scheduling-with-deadlines|§E.2]] (scheduling with deadlines); the exchange arguments of [[2-algorithms/04-greedy-algorithms#43-the-general-pattern|§4.3]], and [[2-algorithms/07-minimum-spanning-trees#75-kruskals-algorithm|Kruskal's algorithm]], which is GreedyBasis on the graphic matroid.

Related: [[concepts/greedy-algorithms]] · [[concepts/minimum-spanning-trees]] · [[concepts/interval-scheduling]] · [[concepts/union-find]]
