---
title: "Breadth-first search"
description: "Whatever-first search with a FIFO queue: in an unweighted graph it finds the fewest-edge distance from the source to every vertex, and a tree of shortest paths, in O(V + E) time, processing the vertices layer by layer."
tags: [concept, algorithms, graphs, midterm-2]
aliases: ["BFS", "breadth-first search", "BFSWithToken", "breadth-first spanning tree"]
---

> [!key] Breadth-first search (Lemma 8.1, Theorem 8.2)
> ```text
> BFS(s):
>     InitSSSP(s)
>     Push(s)
>     while the queue is not empty
>         u ← Pull()
>         for all edges u→v
>             if dist(v) > dist(u) + 1
>                 dist(v) ← dist(u) + 1
>                 pred(v) ← u
>                 Push(v)
> ```
> In a directed or undirected graph without weights, BFS ends with $\mathit{dist}(v)$ equal to the **number of edges of a shortest path** from $s$ to $v$ ($\infty$ if unreachable), and the predecessor pointers form a tree of shortest paths. Each vertex is pushed and pulled at most once and each edge tested at most once: $O(V+E)$ time.

**Why it works.** It is Ford's algorithm with every weight 1, and whatever-first search with a queue. A first-in first-out queue processes the vertices in **layers**: when the vertices at distance $i-1$ are pulled, they push exactly the new vertices at distance $i$ behind them, so at the end of the $i$th phase the queue holds exactly the vertices with $\mathit{dist}(v) = i$ (Lemma 8.1). Labels are therefore assigned in non-decreasing order and each one only once; the test can even be "$\mathit{dist}(v) = \infty$", which makes the labels the marks.

> [!template] Template — invoking it on an exam
> "Run breadth-first search in $G$ from $s$. It computes, for every vertex $v$, the number of edges on a shortest path from $s$ to $v$, in $O(V+E)$ time." \
> Use it whenever every edge counts as **one move**. Distances **to** a target $t$ from every vertex: breadth-first search from $t$ in the reversed graph. Several possible starts: add one new vertex with an edge to each, and subtract 1.

> [!trap]
> - **Weighted graphs:** breadth-first search minimizes the number of edges, not the total weight; use Dijkstra or Bellman–Ford.
> - **Dijkstra on an unweighted graph** is correct but slower, $O(E\log V)$: the graph-reduction rubric deducts a point.
> - **Depth-first search does not find shortest paths.**
> - **Only reachability needed?** Then plain whatever-first search suffices, and naming BFS is "more specific than necessary" (−½).

**Example.** In the $3\times 3$ grid graph (cells adjacent horizontally or vertically, 12 undirected edges), breadth-first search from the corner $(1,1)$ gives cell $(i,j)$ the label $i + j - 2$. Its five phases pull 1, 2, 3, 2 and 1 cells, the vertices at distance 0, 1, 2, 3 and 4 from the corner, and each of the 24 directed edges is tested exactly once.

**Where it appears.** [[2-algorithms/08-shortest-paths#84-unweighted-graphs-breadth-first-search|§8.4]] (the algorithm, the token and phases, Lemma 8.1, Theorem 8.2, the book's example), [[2-algorithms/05-basic-graph-algorithms#56-important-variants|§5.6]] (the queue variant of whatever-first search), [[2-algorithms/08-shortest-paths#87-relax-all-the-edges-bellmanford|§8.7]] (Moore's weighted version), [[2-algorithms/08-shortest-paths#shortest-paths-by-graph-reduction|reductions]] (fewest moves in a layered graph), [[3-homework-and-exams/lab-09a|Lab 9a]].

Related: [[concepts/whatever-first-search]] · [[concepts/shortest-paths]] · [[concepts/dijkstras-algorithm]] · [[concepts/graph-reductions]] · [[concepts/graphs]]
