---
title: "All-pairs shortest paths"
description: "Computing dist(u, v) and pred(u, v) for every pair of vertices of a weighted directed graph: the two V × V output arrays, the algorithms (V single-source runs, Johnson, the dynamic programs, min-plus matrix powers, Floyd–Warshall) with their running times, and how to choose one."
tags: [concept, algorithms, graphs, midterm-2]
aliases: ["APSP", "all pairs shortest paths", "distance matrix", "min-plus matrix multiplication", "min-plus product", "funny matrix multiplication"]
---

> [!definition] Definition
> Given a directed graph $G = (V, E)$ with edge weights $w(u\to v)$ of any sign, compute for every pair of vertices the distance $\textsf{dist}(u, v)$ and the predecessor $\textsf{pred}(u, v)$, the second-to-last vertex of a shortest path — two $V\times V$ arrays. By convention $\textsf{dist}(u, v) = \infty$ if $v$ is unreachable from $u$, $-\infty$ if some walk from $u$ to $v$ runs through a negative cycle, and otherwise $\textsf{dist}(u, u) = 0$; $\textsf{pred}$ is $\textsf{Null}$ in all three cases. Row $u$ of $\textsf{pred}$ is the shortest-path tree rooted at $u$.
>
> | algorithm | weights | time |
> |---|---|---|
> | $V\times$ breadth-first search, or $V\times$ the dag dynamic program | unweighted; dag | $O(VE)$ |
> | $V\times$ Dijkstra (binary heap) | nonnegative | $O(VE\log V)$ |
> | $V\times$ Bellman–Ford | any | $O(V^2E)$ |
> | Johnson: reweight, then $V\times$ Dijkstra | any | $O(VE\log V)$ |
> | Shimbel (by number of edges) | no negative cycle | $O(V^2E) = O(V^4)$ |
> | Fischer–Meyer, Leyzorek (repeated squaring) | no negative cycle | $O(V^3\log V)$ |
> | Floyd–Warshall | no negative cycle (detects one) | $O(V^3)$ |

**Why these bounds.** One family runs a single-source algorithm from every vertex; [[concepts/johnsons-algorithm|reweighting]] removes the factor of $V$ that negative edges would cost. The other is dynamic programming. The shortest walk with at most $\ell$ edges is entry $(u, v)$ of the **min-plus power** $W^{\otimes\ell}$, where $W$ holds the edge weights, 0 on the diagonal and $\infty$ elsewhere, and $(A\otimes B)[i, j] = \min_k (A[i,k] + B[k,j])$ is ordinary matrix multiplication with $+$ replaced by $\min$ and $\times$ by $+$. Without negative cycles, $W^{\otimes(V-1)}$ is the distance matrix: $V-1$ products give $O(V^4)$, repeated squaring $O(V^3\log V)$. [[concepts/floyd-warshall|Floyd–Warshall]] restricts the intermediate vertices instead of the number of edges and needs a single pass, $O(V^3)$. Fast matrix multiplication does not help: it needs subtraction, and $\min$ has no inverse.

> [!recipe] Recipe — choosing an algorithm
> 1. **Do you need all pairs?** If the answer only involves distances from a few fixed vertices $s$ (or to a few fixed $t$), run a single-source algorithm from $s$ in $G$ (from $t$ in the reversed graph) — cheaper, and the rubric deducts for a slower algorithm than necessary.
> 2. **Unweighted:** breadth-first search from every vertex. **Dag:** the dag dynamic program from every vertex. Both $O(VE)$.
> 3. **Nonnegative weights:** Dijkstra from every vertex, $O(VE\log V)$.
> 4. **Negative edges:** Johnson ($O(VE\log V)$, best for sparse graphs) or Floyd–Warshall ($O(V^3)$, best for dense graphs and simplest to write).
> 5. **Negative cycles possible:** Johnson's Bellman–Ford step reports one; Floyd–Warshall leaves a negative diagonal entry.
> 6. State the time in the **input's** parameters.

> [!trap]
> - **Adding a constant** to every weight to remove negative edges changes shortest paths: paths with more edges grow faster.
> - The dynamic programs assume **no negative cycle**; without that assumption their output is meaningless (except the diagonal of Floyd–Warshall or of the repeated-squaring algorithms: some entry is negative iff there is a negative cycle).
> - $O(V^3)$ is not always better than $O(VE\log V)$: for sparse graphs ($E = O(V)$) the latter is $O(V^2\log V)$.
> - Any algorithm needs $\Omega(V^2)$ time just to write the output.

**Example.** Vertices $a, b, c$ and edges $a\to b$ (2), $b\to c$ ($-1$), $a\to c$ (4), $c\to b$ (3); the only cycle, $b\to c\to b$, has length 2. Rows $a, b, c$ of the distance matrix are $(0, 2, 1)$, $(\infty, 0, -1)$ and $(\infty, 3, 0)$: the path $a\to b\to c$ (length 1) beats the edge $a\to c$, so $\textsf{pred}(a, c) = b$, and nothing reaches $a$. Since $V - 1 = 2$, one min-plus squaring suffices: $W^{\otimes2}$ is exactly this matrix, while $W$ itself still has 4 in entry $(a, c)$.

**Where it appears.** [[2-algorithms/09-all-pairs-shortest-paths#91-introduction|§9.1]] (the problem and its output), [[2-algorithms/09-all-pairs-shortest-paths#92-lots-of-single-sources|§9.2]] ($V$ single-source runs), [[2-algorithms/09-all-pairs-shortest-paths#94-johnsons-algorithm|§9.4]] (Johnson), [[2-algorithms/09-all-pairs-shortest-paths#95-dynamic-programming|§9.5]] (Shimbel), [[2-algorithms/09-all-pairs-shortest-paths#96-divide-and-conquer|§9.6]] (Fischer–Meyer, Leyzorek), [[2-algorithms/09-all-pairs-shortest-paths#97-funny-matrix-multiplication|§9.7]] (min-plus products), [[2-algorithms/09-all-pairs-shortest-paths#98-floydwarshall|§9.8]] (Floyd–Warshall), and the single-source algorithms of [[2-algorithms/08-shortest-paths|Chapter 8]].

Related: [[concepts/shortest-paths]] · [[concepts/johnsons-algorithm]] · [[concepts/floyd-warshall]] · [[concepts/dijkstras-algorithm]] · [[concepts/bellman-ford]] · [[concepts/breadth-first-search]] · [[concepts/dynamic-programming]]
