---
title: "Ford–Fulkerson and Edmonds–Karp"
description: "The augmenting-path algorithm for maximum flows: repeatedly push the bottleneck amount along an s–t path in the residual graph. O(E|f*|) time with integer capacities, exponential in the worst case and possibly endless with irrational ones; Edmonds and Karp's fattest-path rule, O(E² log E log|f*|), and shortest-path rule, O(VE²) for any capacities, make it polynomial."
tags: [concept, algorithms, flows]
aliases: ["Ford–Fulkerson", "Ford-Fulkerson", "Ford–Fulkerson algorithm", "augmenting path", "augmenting paths", "Edmonds–Karp", "Edmonds-Karp", "shortest augmenting paths", "fattest augmenting paths"]
---

> [!key] Ford–Fulkerson (§10.4) and Edmonds–Karp's rules (§10.6)
> ```text
> FordFulkerson(G, c, s, t):
>     for every edge u→v
>         f(u→v) ← 0
>     while G_f has a path from s to t
>         P ← any path from s to t in G_f
>         F ← min{c_f(u→v) : u→v ∈ P}
>         for every edge u→v of P
>             if u→v ∈ E
>                 f(u→v) ← f(u→v) + F
>             else
>                 f(v→u) ← f(v→u) − F
>     return f
> ```
> $G_f$ is the residual graph: forward edges with $c - f > 0$, backward edges with $f > 0$. When the loop ends, $f$ is a maximum flow.
>
> | rule for $P$ | found by | time |
> |---|---|---|
> | any path, integer capacities | whatever-first search | $O(E\lvert f^*\rvert)$ — at most $\lvert f^*\rvert$ augmentations |
> | fattest path (largest bottleneck), integer capacities | best-first search, $O(E\log V)$ | $O(E^2\log E\log\lvert f^*\rvert)$ |
> | shortest path (Edmonds–Karp), any capacities | breadth-first search | $O(VE^2)$ — at most $VE$ augmentations |

**Why it works.** Each augmentation keeps the flow feasible and raises its value by the bottleneck $F > 0$; it stops exactly when $G_f$ has no $s$–$t$ path, which by the maxflow-mincut theorem means the flow is maximum. With integer capacities, $F\ge 1$ is an integer, so there are at most $|f^*|$ rounds of $O(E)$ time. The fattest path carries at least a $1/E$ fraction of what is still missing (decompose a maximum flow of $G_f$ into at most $E$ paths and cycles), so the gap shrinks geometrically. With shortest paths, breadth-first levels in $G_f$ never decrease (Lemma 10.2), so each edge can disappear from $G_f$ only $V/2$ times (Lemma 10.3).

> [!template] Template — citing it
> "All capacities are integers and the maximum flow value is at most $k$, so Ford–Fulkerson computes an integral maximum flow in $O(Ek)$ time." \
> Otherwise: "A maximum flow can be computed in $O(VE)$ time (Orlin)", and add "integral, by the integrality theorem" when the proof needs whole units.

> [!trap]
> - **$O(E|f^*|)$ is pseudo-polynomial**: on Edmonds and Karp's network ($X, X, 1, X, X$) a bad choice of paths takes $2X$ augmentations, exponential in the number of bits.
> - **Irrational (or floating-point) capacities**: plain Ford–Fulkerson may never stop, and its flows may converge to far less than the maximum (Zwick's network).
> - **The residual graph needs backward edges**; without them the algorithm can stop below the maximum.
> - **"Edmonds–Karp" is the shortest-path rule**: polynomial for any capacities. The fattest-path rule's bound depends on $|f^*|$.

**Example.** Edges $s\to a$, $s\to b$, $a\to b$, $a\to t$, $b\to t$, all of capacity 1. An unlucky Ford–Fulkerson first augments along $s\to a\to b\to t$; then the only augmenting path is $s\to b\to a\to t$, whose backward edge $b\to a$ cancels the unit on $a\to b$, and the flow reaches its maximum 2 (the cut $\{s\}$ has capacity 2). Edmonds–Karp never takes that detour: breadth-first search finds the two-edge paths $s\to a\to t$ and $s\to b\to t$, and the edge $a\to b$ stays empty.

**Where it appears.** [[2-algorithms/10-maximum-flows-and-minimum-cuts#103-the-maxflow-mincut-theorem|§10.3]] (augmenting paths in the proof of the maxflow-mincut theorem), [[2-algorithms/10-maximum-flows-and-minimum-cuts#104-ford-and-fulkersons-augmenting-path-algorithm|§10.4]] (the algorithm, integrality, running time, bad examples), [[2-algorithms/10-maximum-flows-and-minimum-cuts#106-edmonds-and-karps-algorithms|§10.6]] (fattest and shortest paths, Lemmas 10.2 and 10.3), [[2-algorithms/10-maximum-flows-and-minimum-cuts#107-further-progress|§10.7]] (faster algorithms), and as the black box of [[2-algorithms/11-applications-of-flows-and-cuts|Chapter 11]]. Flows are not on the CS 374 exams this semester.

Related: [[concepts/maximum-flow]] · [[concepts/flow-reductions]] · [[concepts/breadth-first-search]] · [[concepts/dijkstras-algorithm]] · [[concepts/whatever-first-search]]
