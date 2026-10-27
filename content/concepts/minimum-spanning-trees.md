---
title: "Minimum spanning trees"
description: "The spanning tree of least total weight in a connected weighted graph: safe and useless edges, the cut property, the generic algorithm, and Borůvka's, Jarník's (Prim's) and Kruskal's algorithms compared — all O(E log V)."
tags: [concept, algorithms, graphs, greedy]
aliases: ["minimum spanning tree", "MST", "minimum spanning forest", "Kruskal's algorithm", "Prim's algorithm", "Jarník's algorithm", "Borůvka's algorithm", "cut property", "safe edge", "useless edge", "generic MST algorithm"]
---

> [!key] Minimum spanning trees
> Given a connected, undirected graph $G = (V, E)$ with real edge weights, a **minimum spanning tree** (MST) is a spanning tree $T$ minimizing $w(T) = \sum_{e\in T} w(e)$. With **distinct** weights it is unique (Lemma 7.1). For a forest $F$ inside the MST, an edge is **safe** if it is the lightest edge with exactly one endpoint in some component of $F$, and **useless** if both endpoints are in one component.
> - **Cut property** (Lemma 7.2): for every vertex set $\varnothing\ne S\ne V$, the lightest edge with exactly one endpoint in $S$ is in the MST. So every safe edge is in the MST; no useless edge is (Lemma 7.3).
> - **Generic algorithm:** start with $F = (V,\varnothing)$ and add safe edges until $F$ is one tree; it is the MST.

| algorithm | adds | implementation | time |
|---|---|---|---|
| Borůvka | the safe edge of **every** component, then recurses | CountAndLabel per phase; $\le\lfloor\log_2 V\rfloor$ phases | $O(E\log V)$ |
| Jarník ("Prim") | the safe edge of the **one** tree grown from $s$ | best-first search, binary heap | $O(E\log V)$ |
| | | Fibonacci heap of vertices with DecreaseKey | $O(E + V\log V)$ |
| Kruskal | the next edge in sorted order that joins two components | sort + [[concepts/union-find\|union-find]] | $O(E\log V)$ |

**Why it works.** The cut property is a greedy exchange argument. If a spanning tree $T$ misses the lightest edge $e$ crossing $S$, the path in $T$ between the endpoints of $e$ crosses $S$ along some heavier edge $e'$, and $T - e' + e$ is a lighter spanning tree. Each of the three algorithms only ever adds edges that are safe at the moment they are added, so each is the generic algorithm.

> [!template] Template — the cut-property exchange
> "Let $S$ be [a vertex set] and $e$ the lightest edge with exactly one endpoint in $S$. Let $T$ be a spanning tree without $e$. The path in $T$ between the endpoints of $e$ contains an edge $e'$ with exactly one endpoint in $S$; $T - e' + e$ is a spanning tree, lighter because $w(e') > w(e)$. So every minimum spanning tree contains $e$."

> [!trap]
> - **Ties:** with equal weights the MST need not be unique; break ties with one consistent rule — compare $\big(w(ij), \min\{i,j\}, \max\{i,j\}\big)$ — or Borůvka can even add a cycle.
> - **Jarník's priority is one edge's weight**, $\min_{v\in T} w(uv)$, not a path length as in Dijkstra's algorithm; an MST is not a shortest-path tree.
> - **Lemma 7.3 needs $F$ inside the MST**; the cut property needs nothing.
> - **Kruskal's sort dominates**: $O(E\log V)$ however fast the union-find.
> - **Negative weights are fine**; adding a constant to every weight leaves the MST unchanged, and a maximum spanning tree is an MST of $-w$.

**Example.** Take the square $pqrs$ with edges $pq = 1$, $rs = 2$, $pr = 3$, $qr = 4$, $ps = 5$. The MST is $\{pq, rs, pr\}$, weight 6, and the three algorithms reach it in three different orders. Kruskal adds $pq$, $rs$, $pr$ and skips $qr$ and $ps$. Jarník from $s$ adds $rs$, $pr$, $pq$. Borůvka adds $pq$ (picked by $p$ and $q$) and $rs$ (picked by $r$ and $s$) in its first phase, and $pr$, the safe edge of both $\{p, q\}$ and $\{r, s\}$, in its second.

**Where it appears.** [[2-algorithms/07-minimum-spanning-trees#71-distinct-edge-weights|§7.1]] (uniqueness, tie-breaking), [[2-algorithms/07-minimum-spanning-trees#72-the-only-minimum-spanning-tree-algorithm|§7.2]] (safe and useless edges, the cut property, the generic algorithm), [[2-algorithms/07-minimum-spanning-trees#73-borůvkas-algorithm|§7.3]] (Borůvka), [[2-algorithms/07-minimum-spanning-trees#74-jarníks-prims-algorithm|§7.4]] (Jarník), [[2-algorithms/07-minimum-spanning-trees#75-kruskals-algorithm|§7.5]] (Kruskal); "Prim" as best-first search in [[2-algorithms/05-basic-graph-algorithms#56-important-variants|§5.6]].

Related: [[concepts/union-find]] · [[concepts/greedy-algorithms]] · [[concepts/whatever-first-search]] · [[concepts/graphs]] · [[concepts/dijkstras-algorithm]]
