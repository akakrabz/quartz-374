---
title: "Johnson's algorithm"
description: "All-pairs shortest paths with negative edges in O(VE log V) time: reweight the edges by vertex prices — distances from a new vertex — so that every weight is nonnegative without changing any shortest path, then run Dijkstra from every vertex."
tags: [concept, algorithms, graphs]
aliases: ["reweighting", "Johnson's reweighting", "JohnsonAPSP", "vertex prices", "reduced weights"]
---

> [!key] Reweighting, and Johnson's algorithm
> For any **prices** $\pi(v)$, the **reduced weights** $w'(u\to v) = \pi(u) + w(u\to v) - \pi(v)$ change every path from $u$ to $v$ by exactly $\pi(u) - \pi(v)$, so shortest paths are preserved and $\textsf{dist}(u, v) = \textsf{dist}'(u, v) - \pi(u) + \pi(v)$. If $\pi(v) = \textsf{dist}(s, v)$ for a vertex $s$ that reaches every vertex, every reduced weight is **nonnegative**. **Johnson's algorithm:** add a new vertex $s$ with an edge $s\to v$ of weight 0 to every vertex; run Bellman–Ford from $s$ (stop if it finds a negative cycle); set $\pi(v) = \textsf{dist}(s, v)$ and reweight; run Dijkstra on $w'$ from every vertex; convert back. Time $O(VE\log V)$ with a binary heap.

**Why it works.** Along a path $v_0\to v_1\to\cdots\to v_k$ the reduced weights telescope: every intermediate price is added once and subtracted once, leaving $\pi(v_0) + w(P) - \pi(v_k)$. A cycle keeps its length, so negative cycles stay. With $\pi = \textsf{dist}(s, \cdot)$, nonnegativity is the statement that no edge is tense after Bellman–Ford: $\textsf{dist}(s, v)\le\textsf{dist}(s, u) + w(u\to v)$. The new vertex has no incoming edges, so it changes no distance between old vertices, lies on no cycle, and makes every price finite (at most 0). The time is one Bellman–Ford, $O(VE)$, plus $V$ Dijkstras, $O(VE\log V)$, plus $O(V^2)$ to convert the output.

> [!recipe] Recipe — using it
> - Cite it as a standard algorithm: "all-pairs shortest paths with Johnson's algorithm, $O(VE\log V)$ time". It also reports a negative cycle.
> - Prefer it for **sparse** graphs with negative edges; for dense graphs Floyd–Warshall's $O(V^3)$ is faster and simpler.
> - The same trick speeds up any repeated shortest-path computation on a fixed graph with negative edges: one Bellman–Ford to get prices, then Dijkstra as often as needed.

> [!trap]
> - **Adding the same constant to every edge is not reweighting**: a path with $k$ edges grows by $k$ times the constant, so shortest paths change. Prices on **vertices** are what keep every path between the same endpoints in step.
> - Prices from an **old** vertex can be $\infty$ (if it does not reach everything); that is why the new vertex $s$ is added.
> - Converting back: $\textsf{dist}(u, v) = \textsf{dist}'(u, v) - \pi(u) + \pi(v)$ — not $\textsf{dist}'(u, v)$, and not with the signs swapped.
> - Reduced lengths of paths between **different** pairs of vertices cannot be compared.

**Example.** Vertices $a, b, c$; edges $a\to b$ ($-2$), $b\to c$ (1), $a\to c$ (3), $c\to a$ (2); the cycles $a\to b\to c\to a$ and $a\to c\to a$ have lengths 1 and 5. From the new vertex, $\pi(a), \pi(b), \pi(c) = 0, -2, -1$. The reduced weights are $w'(a\to b) = 0 - 2 + 2 = 0$, $w'(b\to c) = -2 + 1 + 1 = 0$, $w'(a\to c) = 0 + 3 + 1 = 4$ and $w'(c\to a) = -1 + 2 - 0 = 1$, all nonnegative; the cycles still have lengths $0 + 0 + 1 = 1$ and $4 + 1 = 5$. Dijkstra on $w'$ gives $\textsf{dist}'(a, c) = 0$ (via $b$), so $\textsf{dist}(a, c) = 0 - 0 + (-1) = -1$, the length of $a\to b\to c$; and $\textsf{dist}'(c, b) = 1$, so $\textsf{dist}(c, b) = 1 + 1 - 2 = 0$, the length of $c\to a\to b$.

**Where it appears.** [[2-algorithms/09-all-pairs-shortest-paths#93-reweighting|§9.3]] (prices, the telescoping lemma, why adding a constant fails), [[2-algorithms/09-all-pairs-shortest-paths#94-johnsons-algorithm|§9.4]] (the algorithm, its analysis and a worked example), and the single-source algorithms it uses, [[2-algorithms/08-shortest-paths#87-relax-all-the-edges-bellmanford|Bellman–Ford]] and [[2-algorithms/08-shortest-paths#86-best-first-dijkstras-algorithm|Dijkstra]].

Related: [[concepts/all-pairs-shortest-paths]] · [[concepts/shortest-paths]] · [[concepts/bellman-ford]] · [[concepts/dijkstras-algorithm]] · [[concepts/floyd-warshall]]
