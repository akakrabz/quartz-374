---
title: "Shortest paths"
description: "Single-source shortest paths in a weighted directed graph: distances, shortest-path trees, negative edges and negative cycles, tense edges and relaxation, and Ford's generic algorithm, of which breadth-first search, DagSSSP, Dijkstra and Bellman–Ford are the four instances."
tags: [concept, algorithms, graphs, midterm-2]
aliases: ["SSSP", "single-source shortest paths", "shortest-path tree", "shortest path tree", "relaxation", "tense edge", "negative cycle", "Ford's algorithm", "FordSSSP"]
---

> [!definition] Shortest paths and relaxation
> In a directed graph with edge weights $w$, the length of a walk is the sum of its edge weights, and $\delta(v)$ is the length of a shortest walk from the source $s$ to $v$: $+\infty$ if $s$ cannot reach $v$, and undefined ($-\infty$) if some walk from $s$ to $v$ touches a **negative cycle**. **SSSP** asks for $\delta(v)$ and a shortest path for every $v$, stored as a **shortest-path tree** of predecessor pointers. Every algorithm keeps a tentative $\mathit{dist}(v)$ and $\mathit{pred}(v)$, starting from $\mathit{dist}(s) = 0$ and $\mathit{dist}(v) = \infty$ otherwise, and repeatedly **relaxes** a **tense** edge $u\to v$:
> $$
> \mathit{dist}(u) + w(u\to v) < \mathit{dist}(v) \quad\Longrightarrow\quad \mathit{dist}(v)\leftarrow\mathit{dist}(u) + w(u\to v),\ \ \mathit{pred}(v)\leftarrow u .
> $$
> **Ford's generic algorithm** relaxes tense edges, in any order, until none is left.

**Why it works.** At every moment $\mathit{dist}(v)$ is the length of some walk from $s$ to $v$, so it never drops below $\delta(v)$, and it never increases. When no edge is tense, $\mathit{dist}(v_j)\le\mathit{dist}(v_{j-1}) + w(v_{j-1}\to v_j)$ along any walk from $s$, so $\mathit{dist}(v)$ is at most the length of every walk to $v$: it equals $\delta(v)$, and the predecessor pointers trace shortest paths. Without negative cycles every value is the length of a path, so the algorithm halts; with a negative cycle reachable from $s$, some edge is always tense and it never halts.

> [!recipe] Recipe — which instance of Ford's algorithm
> | the graph | algorithm | time |
> |---|---|---|
> | unweighted (all weights equal) | [[concepts/breadth-first-search\|breadth-first search]] | $O(V+E)$ |
> | a dag, any weights | DagSSSP: relax in topological order | $O(V+E)$ |
> | non-negative weights | [[concepts/dijkstras-algorithm\|Dijkstra]] | $O(E\log V)$ |
> | anything else (and to detect negative cycles) | [[concepts/bellman-ford\|Bellman–Ford]] | $O(VE)$ |
>
> Take the first row that applies: a slower algorithm than necessary costs a point under the graph-reduction rubric.

> [!trap]
> - **Breadth-first search counts edges, not weight**; Dijkstra needs non-negative weights for its $O(E\log V)$ bound (and the textbook version, NonnegativeDijkstra, to be correct at all).
> - **A negative edge is not a negative cycle**, and only cycles that $s$ can reach matter.
> - **Adding a constant to every weight** changes which path is shortest (paths with more edges grow more).
> - **An undirected negative edge is not two directed edges**: that makes a negative 2-cycle.
> - **A shortest-path tree is not a minimum spanning tree.**

**Example.** Take $s\to t$ of weight 7 and the path $s\to a\to b\to t$ of weights 2, 2, 1. Every run of Ford's algorithm ends with $\mathit{dist}(a) = 2$, $\mathit{dist}(b) = 4$ and $\mathit{dist}(t) = 5$, with $\mathit{pred}(t) = b$ — although breadth-first search would pick the one-edge path. The number of relaxations depends on the order: relaxing $s\to t$ first wastes one (7, later lowered to 5), for 4 in all; relaxing $s\to a$, $a\to b$, $b\to t$ first leaves $s\to t$ not tense, for 3.

**Where it appears.** [[2-algorithms/08-shortest-paths#81-shortest-path-trees|§8.1]] (shortest-path trees), [[2-algorithms/08-shortest-paths#82-negative-edges|§8.2]] (negative edges and cycles, undirected graphs), [[2-algorithms/08-shortest-paths#83-the-only-sssp-algorithm|§8.3]] (relaxation, Ford's algorithm and its four claims), [[2-algorithms/08-shortest-paths#which-algorithm-when|which algorithm when]] and [[2-algorithms/08-shortest-paths#shortest-paths-by-graph-reduction|reductions]]; best-first search in [[2-algorithms/05-basic-graph-algorithms#56-important-variants|§5.6]]; all pairs in [[2-algorithms/09-all-pairs-shortest-paths|Chapter 9]].

Related: [[concepts/breadth-first-search]] · [[concepts/dijkstras-algorithm]] · [[concepts/bellman-ford]] · [[concepts/dynamic-programming-on-dags]] · [[concepts/graph-reductions]] · [[concepts/minimum-spanning-trees]] · [[concepts/all-pairs-shortest-paths]]
