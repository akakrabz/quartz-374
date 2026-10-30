---
title: "Maximum flows and minimum cuts"
description: "Flow networks, feasible (s,t)-flows and their value, (s,t)-cuts and their capacity: every flow is at most every cut, the maximum flow equals the minimum cut, a maximum flow's residual graph yields a minimum cut, and with integer capacities some maximum flow is integral."
tags: [concept, algorithms, flows]
aliases: ["maxflow", "max flow", "maximum flow", "minimum cut", "min cut", "mincut", "maxflow-mincut theorem", "max-flow min-cut theorem", "flow network", "residual graph", "integrality theorem"]
---

> [!key] The maxflow-mincut theorem (with Lemma 10.1 and the integrality theorem)
> A **flow network** is a directed graph with a source $s$, a target $t$ and capacities $c\ge 0$ on the edges. An **$(s,t)$-flow** $f$ satisfies conservation, $\sum_u f(u\to v) = \sum_w f(v\to w)$, at every $v\ne s,t$; it is **feasible** if $0\le f\le c$; its **value** is $|f| = \sum_w f(s\to w) - \sum_u f(u\to s)$. An **$(s,t)$-cut** is a partition $V = S\cup T$ with $s\in S$, $t\in T$; its **capacity** is $\lVert S,T\rVert = \sum_{v\in S,\,w\in T} c(v\to w)$.
> - **Lemma 10.1:** $|f|\le\lVert S,T\rVert$ for every feasible flow and every cut, with equality iff $f$ saturates every edge from $S$ to $T$ and avoids every edge from $T$ to $S$.
> - **Maxflow-mincut:** $\max_f |f| = \min_{(S,T)}\lVert S,T\rVert$. A feasible $f$ is maximum iff its **residual graph** $G_f$ — an edge $u\to v$ of capacity $c(u\to v) - f(u\to v)$ if that is positive, and a reversed edge $v\to u$ of capacity $f(u\to v)$ if that is positive — has no path from $s$ to $t$; then the vertices $s$ reaches in $G_f$ form a minimum cut.
> - **Integrality:** if all capacities are integers, some maximum flow is integral on every edge.

**Why it works.** Summing the net outflow over the vertices of $S$ gives $|f|$ = (flow from $S$ to $T$) − (flow from $T$ to $S$), which is at most the capacity from $S$ to $T$. If $G_f$ has an $s$–$t$ path, pushing its bottleneck along it — forward on unused capacity, backward by cancelling flow — gives a larger feasible flow. If it has none, every edge leaving the reachable set $S$ is saturated and every edge entering it is empty, so Lemma 10.1 holds with equality. Ford–Fulkerson turns this into an algorithm, and with integer capacities every augmentation is an integer, which proves integrality.

> [!recipe] Recipe — certifying and finding optimal flows and cuts
> 1. **To prove a flow is maximum**, exhibit a cut of the same capacity (and vice versa): both are then optimal.
> 2. **To find a maximum flow**, cite $O(VE)$ (Orlin), or Ford–Fulkerson's $O(E|f^*|)$ when the flow value is small.
> 3. **To find a minimum cut**, compute a maximum flow $f$, build $G_f$, and run whatever-first search from $s$: $S$ = the marked vertices, $O(V+E)$ extra time. This is the minimum cut with the smallest $S$.

> [!trap]
> - **The capacity counts only edges from $S$ to $T$**; edges from $T$ to $S$ count, negatively, in the net flow across the cut, never in its capacity.
> - **The value is a net flow**: subtract the flow into $s$.
> - **The reachable set of $G_f$ is a minimum cut only when $f$ is maximum.**
> - **Integrality promises *some* integral maximum flow**, not that every maximum flow is integral, and nothing for non-integer capacities.
> - **Minimum cuts need not be unique**, and "minimum" means least capacity, not fewest edges.

**Example.** Edges $s\to a$ (3), $s\to b$ (2), $a\to b$ (1), $a\to t$ (2), $b\to t$ (3). The flow $3, 2, 1, 2, 3$ on these edges is feasible and conserved ($a$: in 3, out $1 + 2$; $b$: in $2 + 1$, out 3) and has value 5. The cut $S = \{s\}$ has capacity $3 + 2 = 5$, so both are optimal — and the flow is the only maximum flow, because value 5 forces $s\to a$ and $s\to b$ to be saturated, which forces the rest. The minimum cut is not unique: $S = \{s,a\}$ ($2 + 1 + 2$) and $S = \{s,a,b\}$ ($2 + 3$) also have capacity 5, while $S = \{s,b\}$ has 6. Both edges out of $s$ are saturated, so in the residual graph $s$ reaches nothing: the recipe returns $S = \{s\}$, the smallest.

**Where it appears.** [[2-algorithms/10-maximum-flows-and-minimum-cuts#101-flows|§10.1]] (flows), [[2-algorithms/10-maximum-flows-and-minimum-cuts#102-cuts|§10.2]] (cuts, Lemma 10.1), [[2-algorithms/10-maximum-flows-and-minimum-cuts#103-the-maxflow-mincut-theorem|§10.3]] (residual graphs, the theorem and its proof, minimum cuts from maximum flows), [[2-algorithms/10-maximum-flows-and-minimum-cuts#104-ford-and-fulkersons-augmenting-path-algorithm|§10.4]] (integrality), [[2-algorithms/10-maximum-flows-and-minimum-cuts#105-combining-and-decomposing-flows|§10.5]] (flow decomposition), and every application in [[2-algorithms/11-applications-of-flows-and-cuts|Chapter 11]]. Flows are not on the CS 374 exams this semester.

Related: [[concepts/ford-fulkerson]] · [[concepts/flow-reductions]] · [[concepts/bipartite-matching]] · [[concepts/graph-reductions]] · [[concepts/whatever-first-search]] · [[concepts/graphs]]
