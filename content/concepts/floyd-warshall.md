---
title: "Floyd–Warshall"
description: "The O(V³)-time, O(V²)-space dynamic program for all-pairs shortest paths that restricts the intermediate vertices of a path to 1, …, r; its recurrence in the rubric's format, why updating in place is safe, negative-cycle detection, and Warshall's transitive closure."
tags: [concept, algorithms, graphs, dynamic-programming, midterm-2]
aliases: ["Floyd-Warshall", "Floyd–Warshall algorithm", "FloydWarshall", "Kleene–Roy–Floyd–Warshall", "Warshall's algorithm", "transitive closure"]
---

> [!definition] The recurrence
> Number the vertices $1, \ldots, V$. For all vertices $u, v$ and $0\le r\le V$, let $\textsf{dist}(u, v, r)$ be the length of the shortest path from $u$ to $v$ whose **intermediate** vertices (all but the endpoints) are numbered at most $r$. With no negative cycle,
> $$
> \textsf{dist}(u, v, r) = \begin{cases} w(u\to v) & \text{if } r = 0\\ \min\{\textsf{dist}(u, v, r-1),\ \textsf{dist}(u, r, r-1) + \textsf{dist}(r, v, r-1)\} & \text{otherwise,}\end{cases}
> $$
> where $w(v\to v) = 0$ and $w(u\to v) = \infty$ for non-edges; $\textsf{dist}(u, v, V)$ is the distance.
> ```text
> FloydWarshall(V, E, w):
>     for all vertices u, v:  dist[u, v] ← w(u→v)
>     for all vertices r
>         for all vertices u
>             for all vertices v
>                 if dist[u, v] > dist[u, r] + dist[r, v]
>                     dist[u, v] ← dist[u, r] + dist[r, v]
> ```

**Why it works.** A shortest path with intermediate vertices at most $r$ either avoids $r$, or passes through it once and splits there into two paths with intermediate vertices at most $r - 1$. The table can be a single $V\times V$ array updated in place because phase $r$ never changes row $r$ or column $r$ (they would improve by $\mathit{dist}[r, r] = 0$). Time $O(V^3)$, space $O(V^2)$. The same loops with "or" for $\min$ and "and" for $+$ are **Warshall's algorithm** for the transitive closure; the same recursion is Kleene's 1951 proof that every finite automaton has a regular expression.

> [!template] Template — the dynamic-programming write-up
> **Function:** $\textsf{dist}(u, v, r)$ = length of the shortest path from $u$ to $v$ whose intermediate vertices are all at most $r$; answer $\textsf{dist}(u, v, V)$. \
> **Recurrence:** as above, with base case $r = 0$. \
> **Memoization:** $\mathit{dist}[1\,..\,V,\ 1\,..\,V,\ 0\,..\,V]$, or one $V\times V$ array in place. \
> **Evaluation order:** $r$ increasing in the **outer** loop; $u$, $v$ in any order inside. \
> **Time:** $V^2(V+1)$ entries, $O(1)$ each: $O(V^3)$.

> [!trap]
> - **$r$ must be the outer loop.** With $u$, $v$, $r$ nested the other way, one pass can miss paths of three or more edges.
> - Initialize the diagonal to **0** and missing edges to $\infty$.
> - The recurrence assumes **no negative cycle**. With one, the off-diagonal values are not the distances (nor $-\infty$) — but some diagonal entry ends **negative**, which is how Floyd–Warshall detects it.
> - $O(V^3)$ is not always the best choice: for sparse graphs with nonnegative weights, $V$ Dijkstras take $O(VE\log V)$.

**Example.** Vertices 1, 2, 3; edges $1\to2$ (3), $2\to3$ ($-1$), $3\to1$ (2), $1\to3$ (4). The rows of the matrix are $(0, 3, 4), (\infty, 0, -1), (2, \infty, 0)$ at the start; phase 1 finds $3\to1\to2$ (5); phase 2 improves $(1, 3)$ to $3 - 1 = 2$; phase 3 finds $2\to3\to1$ (1). Final rows: $(0, 3, 2), (1, 0, -1), (2, 5, 0)$. Changing $w(3\to1)$ to $-3$ makes the cycle $1\to2\to3\to1$ negative ($3 - 1 - 3 = -1$), and the run ends with diagonal entries $-1, -1, -2$ — all negative, since all three vertices lie on the cycle — and meaningless values such as $-4$ for $(3, 1)$ elsewhere. With the diagonal initialized to $\infty$ instead, the original graph ends with 4 on the diagonal: the shortest cycle through each vertex.

**Where it appears.** [[2-algorithms/09-all-pairs-shortest-paths#98-floydwarshall|§9.8]] (recurrence, KleeneAPSP and FloydWarshall, the phases of the running example, negative cycles, predecessors, transitive closure, shortest cycles), [[2-algorithms/09-all-pairs-shortest-paths#96-divide-and-conquer|§9.6]] (LeyzorekAPSP, the same loop body with the loops in another order); Kleene's construction in [[1-models-of-computation/04-nondeterministic-automata#44-kleenes-theorem|§4.4]] and [[1-models-of-computation/04-nondeterministic-automata#48-nfa-to-regular-expression-state-elimination|§4.8]].

Related: [[concepts/all-pairs-shortest-paths]] · [[concepts/dynamic-programming]] · [[concepts/johnsons-algorithm]] · [[concepts/shortest-paths]] · [[concepts/kleenes-theorem]] · [[concepts/state-elimination]]
