---
title: "Dijkstra's algorithm"
description: "Best-first search for shortest paths: a priority queue keyed by tentative distance. With non-negative weights each vertex is extracted once, in increasing order of distance, and the algorithm runs in O(E log V) time with a binary heap; with negative edges the simplified version fails and the re-inserting version can take exponential time."
tags: [concept, algorithms, graphs, midterm-2]
aliases: ["Dijkstra", "Dijkstra's algorithm", "NonnegativeDijkstra"]
---

> [!key] Dijkstra's algorithm (Lemmas 8.3, 8.4, Theorem 8.5)
> ```text
> Dijkstra(s):
>     InitSSSP(s)
>     Insert(s, 0)
>     while the priority queue is not empty
>         u ← ExtractMin()
>         for all edges u→v
>             if u→v is tense
>                 Relax(u→v)
>                 if v is in the priority queue
>                     DecreaseKey(v, dist(v))
>                 else
>                     Insert(v, dist(v))
> ```
> If no edge weight is negative, the vertices are extracted in non-decreasing order of $\mathit{dist}$, each at most once, and at the end $\mathit{dist}(v) = \delta(v)$ for every $v$. With a binary heap: at most $V$ Insert and ExtractMin and $E$ DecreaseKey operations, **$O(E\log V)$ time** ($O(V^2)$ with an array, $O(E + V\log V)$ with a Fibonacci heap).

**Why it works.** It is Ford's algorithm (a tense edge always leaves a vertex in the queue or the one being scanned) with the most promising vertex first. With non-negative weights, relaxing an edge out of $u$ never gives a key below $\mathit{dist}(u)$, so the extracted keys never decrease (Lemma 8.3); a vertex extracted twice would need a smaller key the second time, so that never happens (Lemma 8.4), and a vertex's distance is final the moment it is extracted. With negative edges but no negative cycles this version is still correct, but vertices may be extracted again and again — exponentially often on the Shier–Witzgall graphs. The textbook version that inserts every vertex at the start (NonnegativeDijkstra) is simply wrong with negative edges.

> [!template] Template — invoking it on an exam
> "All edge weights of $G$ are non-negative, so Dijkstra's algorithm from $s$ computes $\delta(v)$ for every vertex $v$, and a shortest-path tree, in $O(E\log V)$ time." Give $E$ and $V$ in the input's parameters.

> [!trap]
> - **Negative weights:** use Bellman–Ford, or DagSSSP on a dag. Adding a constant to every weight does not help.
> - **Unweighted graph or dag:** breadth-first search or DagSSSP is faster; Dijkstra costs a point.
> - **Prim is not Dijkstra:** the key is $\mathit{dist}(u) + w(u\to v)$, not $w(u\to v)$.
> - **The time is $O(E\log V)$**, not $O(V\log V)$: every edge may cause a DecreaseKey.
> - **One target:** with non-negative weights the search may stop when $t$ is extracted; its distance is final then. With a negative edge it may not: $t$ can leave the queue before its distance is final ([[3-homework-and-exams/lab-10a|Lab 10a]], Problem 1).

**Example.** Undirected (both directions), with $sa = 4$, $sb = 1$, $ba = 2$, $at = 1$, $bt = 5$. Dijkstra from $s$ extracts $s$ (0), $b$ (1), $a$ (3, lowered from 4), $t$ (4, lowered from 6), so $\delta(t) = 4$ along $s\,b\,a\,t$ — three edges, where breadth-first search would choose a two-edge path, $s\,a\,t$ of length 5 or $s\,b\,t$ of length 6.

**Where it appears.** [[2-algorithms/08-shortest-paths#86-best-first-dijkstras-algorithm|§8.6]] (the algorithm, the proofs, the implementations, negative edges), [[2-algorithms/05-basic-graph-algorithms#56-important-variants|§5.6]] (as best-first search), [[2-algorithms/08-shortest-paths#shortest-paths-by-graph-reduction|reductions]] (the cheapest route with a coupon), [[2-algorithms/09-all-pairs-shortest-paths|Chapter 9]] (run from every vertex after reweighting).

Related: [[concepts/shortest-paths]] · [[concepts/breadth-first-search]] · [[concepts/bellman-ford]] · [[concepts/whatever-first-search]] · [[concepts/minimum-spanning-trees]] · [[concepts/johnsons-algorithm]]
