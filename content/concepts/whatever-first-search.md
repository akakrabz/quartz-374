---
title: "Whatever-first search"
description: "The generic graph traversal: keep candidate edges in a bag, mark each vertex the first time it comes out. It marks exactly the vertices reachable from the start in O(V + ET) time; a stack gives depth-first search, a queue breadth-first search, a priority queue best-first search."
tags: [concept, algorithms, graphs, midterm-2]
aliases: ["WhateverFirstSearch", "WFS", "breadth-first search", "BFS", "best-first search", "graph traversal", "reachability"]
---

> [!key] Whatever-first search (Lemma 5.1)
> ```text
> WhateverFirstSearch(s):
>     put (∅, s) into the bag
>     while the bag is not empty
>         take (p, v) from the bag
>         if v is unmarked
>             mark v
>             parent(v) ← p
>             for each edge vw
>                 put (v, w) into the bag
> ```
> It marks **exactly the vertices reachable from $s$**, and the parent edges form a spanning tree of them, rooted at $s$ (in a directed graph, with every edge directed away from $s$). At most $2E+1$ pairs pass through the bag ($E+1$ if directed), so with a standard adjacency list it takes $O(V + ET)$ time, where $T$ is the cost of one bag operation.

| bag | search | time | what the parent tree gives |
|---|---|---|---|
| stack | depth-first | $O(V+E)$ | a long, skinny tree; pre- and postorder (Chapter 6) |
| queue | breadth-first | $O(V+E)$ | shortest paths from $s$ by number of edges |
| priority queue | best-first | $O(V+E\log E)$ | minimum spanning tree, shortest paths, widest paths |

**Why it works.** A reachable vertex $v$ is marked, by induction on its distance from $s$: the vertex $u$ before $v$ on a shortest path is marked first, puts $(u,v)$ into the bag, and the bag is emptied before the search ends. A marked vertex is reachable, because its parent was marked earlier and parent edges are edges. The $k$ marked vertices are connected by their $k-1$ parent edges, so these form a tree. Time: a vertex enters the bag once per marked neighbor — up to $\deg(v)$ times — so the bag sees $\sum_v\deg(v) = 2E$ pairs plus the first one.

> [!template] Template — invoking it on an exam
> "Run whatever-first search in $G$ from $s$. It marks exactly the vertices reachable from $s$, in $O(V+E)$ time." \
> Use **breadth-first search** only when you need fewest edges, a **weighted** shortest-path algorithm only when there are weights, and **WFSAll** (one search from each unmarked vertex) to cover every vertex or count components, still in $O(V+E)$ time. Cite the algorithm; do not re-explain it.

> [!trap]
> - **Mark when taking out, not when putting in.** "Eager" marking is still breadth-first search with a queue, but with a stack it is not depth-first search.
> - **Without the test "if $v$ is unmarked"** the loop never ends in an undirected graph once $s$ has an edge.
> - **Depth-first search does not find shortest paths**, and breadth-first search finds fewest *edges*, not least total *weight*.
> - **The bag holds up to $2E+1$ pairs**, not $V$; on an adjacency matrix the search takes $\Theta(V^2)$ time.
> - **Whatever-first search finds one path to each vertex**, not all paths.

**Example — a complete graph.** In $K_5$ (5 vertices, every pair adjacent, $E = 10$), a search from any vertex marks 5 vertices but moves $2\cdot 10 + 1 = 21$ pairs through the bag: each vertex enters it 4 times, once from each neighbor, and the start once more. With a stack the parent tree is a path through all five vertices — every newly marked vertex still has unmarked neighbors, and its own pairs are on top of the stack. With a queue it is a star: the start vertex is the parent of everyone.

**Where it appears.** [[2-algorithms/05-basic-graph-algorithms#55-whatever-first-search|§5.5]] (the algorithm, Lemma 5.1 and the analysis), [[2-algorithms/05-basic-graph-algorithms#56-important-variants|§5.6]] (stack, queue and priority queue; components; directed graphs), [[2-algorithms/05-basic-graph-algorithms#57-graph-reductions-flood-fill|§5.7]] (as a black box in a reduction); depth-first search in [[2-algorithms/06-depth-first-search|Chapter 6]].

Related: [[concepts/graphs]] · [[concepts/graph-reductions]] · [[concepts/depth-first-search]]
