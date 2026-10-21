---
title: "Graphs"
description: "A graph is a set of pairs of things: directed and undirected graphs, the V/E conventions, degrees, walks, paths, cycles, reachability, components, trees, forests and dags, and the two standard data structures — adjacency lists and adjacency matrices — with what each operation costs."
tags: [concept, algorithms, graphs, midterm-2]
aliases: ["graph", "undirected graph", "directed graph", "adjacency list", "adjacency matrix", "graph terminology"]
---

> [!definition] Definition — graph
> A **graph** $G = (V,E)$ is a nonempty finite set $V$ of **vertices** and a set $E$ of pairs of vertices, the **edges**: unordered pairs $uv$ in an **undirected** graph, ordered pairs $u\to v$ (tail $u$, head $v$) in a **directed** one. By convention $V$ and $E$ also denote the *numbers* of vertices and edges, so
> $$
> E\le\frac{V(V-1)}{2}\ \text{(undirected)},\qquad E\le V(V-1)\ \text{(directed, no loops)},
> $$
> and in an undirected graph the degrees add up to $\sum_{v}\deg(v) = 2E$ (the **handshake lemma**: each edge is counted at both ends).
> A **walk** follows edges and may repeat vertices; a **path** visits each vertex at most once; $v$ is **reachable** from $u$ if some walk — equivalently some path — leads from $u$ to $v$. The **components** of an undirected graph are its maximal connected subgraphs. A **tree** is a connected acyclic graph (with $V-1$ edges), a **forest** an acyclic one; a **dag** is a directed graph without directed cycles.

**Why it matters.** "A graph is a set of pairs of things": road maps, dependency graphs of recurrences, configuration graphs of puzzles, DFAs, pointer structures — all are graphs, and once a problem is phrased as a question about a graph, a handful of standard algorithms answer it. The vocabulary is what makes the phrasing precise: "reachable" (not "connected") in a directed graph, "path" (not "walk") when repeated vertices are forbidden, $O(V+E)$ (not $O(V)$) when every edge must be looked at.

**Representations.** A **standard adjacency list** is an array of linked lists, the list of $v$ holding its (out-)neighbors: $\Theta(V+E)$ space, an undirected edge stored twice, neighbors of $v$ listed in $O(1+\deg(v))$ time. An **adjacency matrix** is a $V\times V$ array of bits: adjacency tested in $O(1)$, but $\Theta(V^2)$ space and $\Theta(V)$ time to list the neighbors of any vertex. Unless a problem says otherwise, assume a standard adjacency list.

> [!recipe] Recipe — describing a graph in a solution
> 1. Say whether it is **directed** or undirected.
> 2. **Vertices:** an explicit set built from the input — "one vertex $(i,j)$ for every $1\le i\le m$ and $1\le j\le n$".
> 3. **Edges:** an explicit rule — "$(i,j)\to(i+1,j)$ whenever $A[i+1,j] > A[i,j]$" — and the **weights**, if any.
> 4. **Count** vertices and edges in the input's parameters; a brute-force construction takes $O(V+E)$ time from those counts.

> [!trap]
> - **Walk versus path.** Reachability does not care, but "longest path" (no repeats) and "longest walk" (possibly infinite) are different problems.
> - **Connected** is for undirected graphs; a directed graph is *strongly* connected if every vertex reaches every other.
> - **$O(E)$ is not $O(V+E)$**: isolated vertices make $E < V$ possible. And $E$ can be as large as $\Theta(V^2)$.
> - **Adjacency matrix by accident.** An algorithm that, for each vertex, loops over *all* vertices to find its neighbors takes $\Theta(V^2)$ time even on a sparse graph.

**Example — a configuration graph and the handshake lemma.** The 3-disk Tower of Hanoi has 27 configurations (each disk on one of 3 pegs). Joining two configurations by an edge when one legal move turns one into the other gives an undirected graph with 39 edges. In the three configurations with all disks on one peg only the smallest disk can move, to either other peg: degree 2. Everywhere else the smallest disk has two moves and exactly one other move is legal: degree 3. The handshake lemma checks the count: $3\cdot 2 + 24\cdot 3 = 78 = 2\cdot 39$. A shortest path between two of the degree-2 corners has $7 = 2^3 - 1$ edges — the Tower of Hanoi solution.

**Where it appears.** [[2-algorithms/05-basic-graph-algorithms#52-basic-definitions|§5.2]] (definitions), [[2-algorithms/05-basic-graph-algorithms#53-representations-and-examples|§5.3]] (drawings, intersection, dependency and configuration graphs, automata, implicit graphs), [[2-algorithms/05-basic-graph-algorithms#54-data-structures|§5.4]] (adjacency lists and matrices, the cost table); dags and strong connectivity in [[2-algorithms/06-depth-first-search|Chapter 6]].

Related: [[concepts/whatever-first-search]] · [[concepts/graph-reductions]] · [[concepts/depth-first-search]] · [[concepts/dfa]]
