---
title: "Flow reductions"
description: "Solving a problem by building a flow network from its input and computing a maximum flow or minimum cut as a black box: the four-part write-up with the two-direction proof and integrality, unit capacities for edge-disjoint paths, vertex splitting for vertex capacities and vertex-disjoint paths, and cut reductions."
tags: [concept, algorithms, flows]
aliases: ["flow reduction", "reduction to maximum flow", "edge-disjoint paths", "vertex-disjoint paths", "vertex splitting", "vertex capacities", "Menger's theorem", "tuple selection", "baseball elimination", "project selection"]
---

> [!definition] Definition — flow reduction
> A **flow reduction** solves a problem by (1) building a flow network — vertices, directed edges, capacities, a source and a target — as explicit functions of the input; (2) proving that the input has a solution of size $k$ **if and only if** the network has an integral $(s,t)$-flow of value $k$; (3) computing a maximum flow, and if needed a flow decomposition or a minimum cut, with a standard algorithm used as a **black box**; (4) stating the time in the input's parameters. In a **cut reduction** step (2) instead matches solutions with finite cuts, the capacity being an explicit function of the solution's value.

**Why it works.** Two theorems of Chapter 10 do the work. The **integrality theorem** — integer capacities admit an integral maximum flow, and Ford–Fulkerson finds one — makes the direction "flow ⇒ solution" possible, since only an integral flow can be read as discrete objects; **flow decomposition** splits an integral flow of value $k$ into $k$ unit paths (plus cycles, which are discarded), each one a piece of the solution. Capacities are the constraints: a capacity bounds how many pieces may use an edge, and a vertex capacity is enforced by **vertex splitting** — $v$ becomes an edge $v_{\text{in}}\to v_{\text{out}}$ of capacity $c(v)$, and every edge $u\to v$ becomes $u_{\text{out}}\to v_{\text{in}}$. Infinite capacities can never cross a finite cut, which encodes constraints such as prerequisites (project selection), and a small cut certifies that no large solution exists (baseball elimination). As in a [[concepts/graph-reductions|graph reduction]], all the creativity goes into the network; the algorithm is never modified.

> [!template] Template — the four parts
> 1. **Network:** "Let $H$ be the directed graph with vertices … and edges …, with capacities …; source …, target …."
> 2. **Claim:** "The input has [$k$ disjoint paths / a matching of size $k$ / a schedule for $k$ items] iff $H$ has an integral flow of value $k$." *(⇒)* Push one unit along the path of each piece; check every capacity and conservation. *(⇐)* By the integrality theorem take an integral flow; decompose it into $k$ unit paths; read each path back as a piece; the capacities give the constraints.
> 3. **Algorithm:** Ford–Fulkerson, $O(E\lvert f^*\rvert)$, when $\lvert f^*\rvert$ is small (with unit capacities, $\lvert f^*\rvert\le V$); otherwise Orlin, $O(VE)$. A minimum cut: the vertices reachable from $s$ in the final residual graph.
> 4. **Time:** count $V$ and $E$ of $H$ in the input's parameters.

> [!trap]
> - **Proving one direction only.** "Solution ⇒ flow" shows that the maximum flow is at least the optimum; "integral flow ⇒ solution" is needed for the converse.
> - **Forgetting integrality:** a fractional flow cannot be read as paths or matchings; write "by the integrality theorem, take an integral maximum flow".
> - **Undirected edges:** two directed edges of the same capacity, and cancel any flow that uses both.
> - **Vertex-disjoint is not edge-disjoint:** split the vertices, keep capacity 1 on the edges, and do not cap $s$ and $t$.
> - **Ford–Fulkerson with large capacities** is only pseudo-polynomial; cite Orlin's $O(VE)$.

**Example — reviewer assignment.** *Each of $n$ papers needs $r$ different reviewers; reviewer $j$ reviews at most $L[j]$ papers, and only papers in a list $\mathit{Ok}[j]$. Can every paper get its $r$ reviews?*
- **Network:** vertices $s$, $t$, one per paper and one per reviewer; edges $s\to i$ of capacity $r$ for every paper $i$, $i\to j$ of capacity 1 whenever paper $i$ is in $\mathit{Ok}[j]$, and $j\to t$ of capacity $L[j]$ for every reviewer $j$.
- **Claim:** assignments with $k$ reviews in all (each paper–reviewer pair at most once, all limits respected) ⇔ integral flows of value $k$. An assignment pushes one unit along $s\to i\to j\to t$ per review. Conversely, an integral flow puts 0 or 1 on every middle edge; the edges carrying 1 are the reviews — distinct reviewers for each paper because the middle capacities are 1, at most $r$ per paper and $L[j]$ per reviewer by the outer capacities. So every paper is fully reviewed iff the maximum flow is $rn$.
- **Algorithm:** Ford–Fulkerson, since $\lvert f^*\rvert\le rn$.
- **Time:** with $m$ reviewers and $q$ acceptable pairs, the network has $n+m+q$ edges: $O(rn(n+m+q))$.

With papers $P_1, P_2, P_3$, $r = 2$, and reviewers $A$ (papers $P_1, P_2$), $B$ ($P_1, P_3$) and $C$ ($P_2, P_3$), each with limit 2, the maximum flow is $6 = 2\cdot 3$: $P_1$ gets $A$ and $B$, $P_2$ gets $A$ and $C$, $P_3$ gets $B$ and $C$. Lower $C$'s limit to 1, and the edges into $t$ have total capacity $2+2+1 = 5 < 6$: some paper misses a review.

**Where it appears.** [[2-algorithms/11-applications-of-flows-and-cuts#111-edge-disjoint-paths|§11.1]] (edge-disjoint paths, Menger's theorem), [[2-algorithms/11-applications-of-flows-and-cuts#112-vertex-capacities-and-vertex-disjoint-paths|§11.2]] (vertex splitting, vertex-disjoint paths), [[2-algorithms/11-applications-of-flows-and-cuts#114-tuple-selection|§11.4]] (tuple selection, exam scheduling), [[2-algorithms/11-applications-of-flows-and-cuts#116-baseball-elimination|§11.6]] (baseball elimination and its certificate cut), [[2-algorithms/11-applications-of-flows-and-cuts#117-project-selection|§11.7]] (project selection, a cut reduction); the black boxes are in [[2-algorithms/10-maximum-flows-and-minimum-cuts|Chapter 10]].

Related: [[concepts/maximum-flow]] · [[concepts/ford-fulkerson]] · [[concepts/bipartite-matching]] · [[concepts/graph-reductions]] · [[concepts/polynomial-time-reductions]]
