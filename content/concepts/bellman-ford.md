---
title: "Bellman–Ford"
description: "Shortest paths with arbitrary edge weights: relax every edge V − 1 times, then one more pass detects a negative cycle reachable from the source; O(VE) time. It is Bellman's dynamic program over the number of edges — DagSSSP in a layered dag — and Moore's queue version is its practical form."
tags: [concept, algorithms, graphs, dynamic-programming, midterm-2]
aliases: ["Bellman-Ford", "BellmanFord", "Bellman–Ford algorithm", "Bellman's equation", "Moore's improvement"]
---

> [!key] Bellman–Ford (Lemma 8.6)
> ```text
> BellmanFord(s):
>     InitSSSP(s)
>     repeat V − 1 times
>         for every edge u→v
>             if u→v is tense
>                 Relax(u→v)
>     for every edge u→v
>         if u→v is tense
>             return "Negative cycle!"
> ```
> For any edge weights it runs in **$O(VE)$ time**. If no negative cycle is reachable from $s$, it ends with $\mathit{dist}(v) = \delta(v)$ for every $v$ and a shortest-path tree; it returns "Negative cycle!" if and only if a negative cycle is reachable from $s$. The dynamic program behind it, for the shortest walk with at most $i$ edges:
> $$
> \mathit{dist}_{\le i}(v) = \min\Bigl\{\mathit{dist}_{\le i-1}(v),\ \min_{u\to v}\bigl(\mathit{dist}_{\le i-1}(u) + w(u\to v)\bigr)\Bigr\}\quad\text{for } i\ge 1,
> $$
> with $\mathit{dist}_{\le 0}(s) = 0$ and $\mathit{dist}_{\le 0}(v) = \infty$ for $v\ne s$.

**Why it works.** After $i$ rounds, $\mathit{dist}(v)\le\mathit{dist}_{\le i}(v)$ (Lemma 8.6): round $i$ relaxes the last edge of a best walk with at most $i$ edges. Without negative cycles a shortest walk is a path with at most $V-1$ edges, so $V-1$ rounds suffice. A reachable negative cycle keeps one of its edges tense forever — if none were tense, summing $\mathit{dist}(v)\le\mathit{dist}(u) + w(u\to v)$ around the cycle would give $0\le w(C) < 0$ — so the final pass catches it.

> [!template] Template — invoking it on an exam
> "The weights of $G$ may be negative (and $G$ may have cycles), so we run Bellman–Ford from $s$: in $O(VE)$ time it computes $\delta(v)$ for every vertex $v$, or reports that a negative cycle is reachable from $s$." \
> To find a negative cycle anywhere, first add a new vertex with an edge of weight 0 to every vertex. Written out as a dynamic program, use the rubric's format: the function $\mathit{dist}_{\le i}(v)$ in words, the recurrence above, a table $\mathit{dist}[0\,..\,V-1, V]$, $i$ increasing in the outer loop, $O(VE)$ time.

> [!trap]
> - **Non-negative weights, or a dag:** Dijkstra or DagSSSP is faster; Bellman–Ford is the slowest of the four instances.
> - **$V-1$ rounds**, then the test pass; "until nothing changes" never stops on a negative cycle.
> - **Only negative cycles reachable from $s$ are detected.**
> - **The subproblem needs the edge count $i$**: "$\mathit{dist}(v)$" alone has no evaluation order in a graph with cycles.

**Example.** Take $s\to a$ (2), $s\to c$ (4), $a\to b$ (1), $b\to c$ ($-3$) and $c\to a$ (3). The cycle $a\,b\,c\,a$ weighs $+1$; after $V - 1 = 3$ rounds the distances are $a$ 2, $b$ 3, $c$ 0, no edge is tense, and nothing is reported. Change $c\to a$ to weight 1: the cycle now weighs $-1$, $\mathit{dist}(a)$, $\mathit{dist}(b)$ and $\mathit{dist}(c)$ keep falling in every round, and the test pass finds a tense edge and returns "Negative cycle!".

**Where it appears.** [[2-algorithms/08-shortest-paths#87-relax-all-the-edges-bellmanford|§8.7]] (both forms, Lemma 8.6, the $\mathit{dist}_{\le i}$ table, Moore's improvement and Lemma 8.7, the dynamic program), [[2-algorithms/08-shortest-paths#83-the-only-sssp-algorithm|§8.3]] (Ford's algorithm), [[2-algorithms/08-shortest-paths#shortest-paths-by-graph-reduction|reductions]] (shortest walks with at most $k$ edges in a layered dag), [[2-algorithms/09-all-pairs-shortest-paths|Chapter 9]] (Johnson's algorithm and the dynamic programs for all pairs).

Related: [[concepts/shortest-paths]] · [[concepts/dijkstras-algorithm]] · [[concepts/dynamic-programming]] · [[concepts/dynamic-programming-on-dags]] · [[concepts/johnsons-algorithm]] · [[concepts/all-pairs-shortest-paths]]
