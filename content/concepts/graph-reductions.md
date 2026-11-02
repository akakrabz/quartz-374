---
title: "Graph reductions"
description: "Solving a problem by building a graph from its input and calling a standard graph algorithm as a black box — the four-part write-up the course's graph-reduction rubric grades, its common mistakes, and the trick of putting extra state into the vertices."
tags: [concept, algorithms, graphs, midterm-2]
aliases: ["graph reduction", "graph-reduction rubric", "flood fill", "reduction to reachability"]
---

> [!definition] Definition — graph reduction
> A **graph reduction** solves a problem by (1) constructing a graph whose vertices, edges and weights are explicit functions of the input, (2) showing that the answer is the answer to a standard problem on that graph — reachability, shortest path, … — (3) solving that problem with a standard algorithm used as a **black box**, and (4) analyzing the running time in the parameters of the **original input**.

**Why it works.** A black box needs only its specification: "whatever-first search from $s$ marks exactly the vertices reachable from $s$, in $O(V+E)$ time". All the creativity goes into the graph — choosing vertices that remember everything the question depends on, and edges that are exactly the allowed steps — and the proof is the equivalence in step (2). It is the same notion of reduction as in undecidability proofs — solve one problem with an algorithm for another as a black box — put to the opposite use: there, reducing a known undecidable problem to a new one shows that the new one is undecidable; here, reducing a new problem to a solved one solves it.

> [!template] Template — the four parts (rubric: 3 + 3 + 2 + 2 points)
> 1. **Graph (3):** "Let $G$ be the [directed / undirected] graph with vertices [explicit set] and edges [explicit rule], weighted by …". Saying "directed" when it is matters ($-\tfrac12$).
> 2. **Problem (3):** "The answer is yes iff $t$ is reachable from $s$ in $G$" / "the answer is the length of a shortest path in $G$ from … to …", and why. Naming an algorithm is not naming a problem.
> 3. **Algorithm (2):** the standard one, as a black box — whatever-first search for reachability, breadth-first search for fewest edges. Slower than necessary: $-1$; more specific than necessary: $-\tfrac12$; re-explained: $-1$.
> 4. **Time (2):** in the input's parameters, through the sizes of $V$ and $E$.

> [!trap]
> - **Modifying the algorithm instead of the graph.** Put the extra state into the vertices — pairs (vertex, state) — and run the algorithm unchanged.
> - **"Try all paths and keep the best."** A search finds one path per vertex; there can be exponentially many simple paths.
> - **Time stated only as $O(V+E)$.**
> - **Vertices or edges described vaguely**, or the direction of edges left unsaid.

**Example — knight moves.** *Fewest knight moves from square $(a,b)$ to square $(c,d)$ of an $n\times n$ board, or report that it is impossible.*
- **Graph:** the undirected graph $G$ with the $n^2$ squares $(i,j)$, $1\le i,j\le n$, as vertices, and an edge between two squares whenever their rows differ by 1 and their columns by 2, or the other way around. No weights.
- **Problem:** the answer is the number of edges of a shortest path from $(a,b)$ to $(c,d)$ in $G$, because a sequence of moves is exactly a walk in $G$; if $(c,d)$ is not reachable from $(a,b)$, it is impossible.
- **Algorithm:** breadth-first search in $G$ from $(a,b)$ (unweighted, so no Dijkstra).
- **Time:** each square has at most 8 neighbors, so $G$ has at most $4n^2$ edges: $O(n^2)$ time.

On an $8\times 8$ board, a knight needs 6 moves from one corner to the opposite corner. On a $3\times 3$ board the center square has no knight moves at all, so it cannot be reached from a corner: the answer is "impossible".

**Where it appears.** [[2-algorithms/05-basic-graph-algorithms#57-graph-reductions-flood-fill|§5.7]] (flood fill as reachability, the template, and walks of even length with a parity bit in the vertices), [[2-algorithms/05-basic-graph-algorithms#53-representations-and-examples|§5.3]] (configuration graphs; DFA emptiness as reachability); [[0-toolkit/06-how-exams-are-graded|how exams are graded]].

Related: [[concepts/whatever-first-search]] · [[concepts/graphs]] · [[concepts/undecidability-reductions]] · [[concepts/depth-first-search]]
