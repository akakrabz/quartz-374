---
title: "Bipartite matching"
description: "Maximum matching in a bipartite graph: the unit-capacity flow network s → L → R → t, the alternating-path algorithm (Ford–Fulkerson in disguise) in O(VE) time, Berge's theorem, and minimum disjoint-path covers of dags as matchings."
tags: [concept, algorithms, flows]
aliases: ["maximum matching", "maximum bipartite matching", "alternating path", "Berge's theorem", "Hopcroft–Karp", "disjoint-path cover", "minimum path cover"]
---

> [!definition] Definition — maximum bipartite matching
> A **matching** is a set of edges no two of which share a vertex. Given a bipartite graph $G = (L\cup R, E)$, find a matching with as many edges as possible. **Reduction:** the network $G'$ with edges $s\to\ell$ for $\ell\in L$, $\ell\to r$ for every edge $\ell r$ (oriented from $L$ to $R$) and $r\to t$ for $r\in R$, all of capacity 1. Matchings of size $k$ correspond to integral flows of value $k$, so Ford–Fulkerson finds a maximum matching in **$O(VE)$ time** ($\lvert f^*\rvert\le V/2$).

**Why it works.** Flow can reach $\ell$ only through the single edge $s\to\ell$ of capacity 1, so at most one edge out of $\ell$ carries flow; symmetrically at $r$. So the edges $\ell\to r$ carrying flow in an integral flow form a matching of size $\lvert f\rvert$, and every matching is such a flow. Seen in $G$, the augmenting paths of Ford–Fulkerson are **alternating paths**: paths from an unmatched vertex of $L$ to an unmatched vertex of $R$ whose edges are alternately outside and inside the matching $M$; replacing $M$ by $M\oplus P$ gains one edge. **Berge's theorem (1957):** $M$ is maximum if and only if it has no alternating path. Hopcroft and Karp augment along many disjoint shortest alternating paths at once and need only $O(\sqrt V\,E)$ time.

> [!recipe] Recipe — matching problems
> 1. Identify the two sides and the acceptable pairs: they are the edges, oriented from one side to the other.
> 2. If a vertex may be used up to $b$ times, give its edge from $s$ (or to $t$) capacity $b$: no longer a matching, but the same flow reduction.
> 3. Cite "a maximum bipartite matching can be computed in $O(VE)$ time" and give $V$ and $E$ in the input's parameters.
> 4. **Minimum disjoint-path cover of a dag:** give each vertex $v$ a copy $v^\flat$ on the left and $v^\sharp$ on the right, and an edge $u^\flat v^\sharp$ for every edge $u\to v$. The minimum number of disjoint paths covering the dag is $V$ minus the size of a maximum matching, and the matched edges are the edges of the paths.

> [!trap]
> - **Maximal is not maximum:** a matching that no edge can extend may still be too small (example below).
> - **Only bipartite graphs:** the reduction needs the sides to orient every edge; general graphs need Edmonds' blossom algorithm.
> - **Path covers need a dag:** in a graph with cycles a matching can turn into cycles, and the problem is NP-hard (Hamiltonian path).
> - **Not stable matching:** nobody's preferences count, only the number of pairs.

**Example.** $L = \{1,2,3,4\}$, $R = \{A,B,C\}$, edges $1A$, $1B$, $2A$, $2C$, $3C$, $4C$. Taking edges greedily in this order gives $\{1A, 2C\}$, which no edge extends. But $3\,C\,2\,A\,1\,B$ is an alternating path, and switching along it gives $\{1B, 2A, 3C\}$, a maximum matching. Vertex 4 stays unmatched: 3 and 4 both accept only $C$. Ford–Fulkerson certifies this with the minimum cut whose source side is $\{s, 3, 4, C\}$: it is crossed by $s\to 1$, $s\to 2$ and $C\to t$, capacity 3.

**Where it appears.** [[2-algorithms/11-applications-of-flows-and-cuts#113-bipartite-matching|§11.3]] (the reduction, alternating paths, Berge's theorem, $O(VE)$ and Hopcroft–Karp), [[2-algorithms/11-applications-of-flows-and-cuts#114-tuple-selection|§11.4]] (tuple selection generalizes it), [[2-algorithms/11-applications-of-flows-and-cuts#115-disjoint-path-covers|§11.5]] (path covers of dags, minimal faculty hiring); contrast [[2-algorithms/04-greedy-algorithms#45-stable-matching|stable matching]] (§4.5).

Related: [[concepts/flow-reductions]] · [[concepts/maximum-flow]] · [[concepts/ford-fulkerson]] · [[concepts/stable-matching]] · [[concepts/hamiltonian-cycle]]
