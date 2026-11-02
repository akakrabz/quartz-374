---
title: "Strongly connected components"
description: "The classes of mutual reachability in a directed graph; contracting them gives the strong component graph scc(G), which is always a dag; all of them in O(V + E) time by the Kosaraju–Sharir algorithm (or Tarjan's)."
tags: [concept, algorithms, graphs, midterm-2]
aliases: ["strong components", "SCC", "strong component graph", "condensation", "Kosaraju-Sharir algorithm", "Tarjan's algorithm"]
---

> [!definition] Definition
> Vertices $u$ and $v$ are **strongly connected** if each can reach the other. This is an equivalence relation; its classes are the **strong components** of $G$. Contracting each component to a vertex and collapsing parallel edges gives the **strong component graph** $\textsf{scc}(G)$. Facts:
> - $\textsf{scc}(G)$ is a **dag**, for every directed graph $G$;
> - $u$ reaches $v$ in $G$ if and only if the component of $u$ reaches the component of $v$ in $\textsf{scc}(G)$;
> - $G$ is strongly connected if and only if it has one component; a graph without loops is a dag if and only if every component is a single vertex.
>
> All the components, and $\textsf{scc}(G)$, can be computed in $O(V+E)$ time.

**Why it works.** A cycle of components would merge them into one, so $\textsf{scc}(G)$ is acyclic. **Kosaraju–Sharir:** the last vertex to finish in a depth-first search lies in a source component; $G$ and $\textsf{rev}(G)$ have the same components with every component edge reversed, so the last vertex to finish in a search of $\textsf{rev}(G)$ lies in a **sink** component of $G$, and a search of $G$ from it finds exactly its component. Phase 1 searches $\textsf{rev}(G)$ and stacks the vertices as they finish; phase 2 pops them and, from each unlabeled one, searches $G$, ignoring labeled vertices — each such search labels one component, sinks first. **Tarjan** does the same in one search, with $\textsf{low}$ values and a second stack.

> [!recipe] Recipe — strong components on an exam
> 1. "Compute the strong components of $G$ and the strong component graph $\textsf{scc}(G)$ in $O(V+E)$ time (Kosaraju–Sharir)" — cite it, do not re-derive it.
> 2. Solve the problem on the **dag** $\textsf{scc}(G)$, usually by dynamic programming in topological order, after giving each component vertex the data of its members (its size, the largest value in it, …): inside a component, every vertex can reach every other.
> 3. Translate back, and state the time in the input's parameters.
>
> One component only (is $G$ strongly connected?): search $G$ and $\textsf{rev}(G)$ from any one vertex; strongly connected if and only if both searches reach everything — $O(V+E)$.

> [!trap]
> - **Phase 1 must run on the other graph.** The *first* vertex to finish in a search of $G$ need not lie in a sink component (in $a\to b$, $b\to a$, $a\to c$, searched from $a$ trying $b$ first, $b$ finishes first but $\{a, b\}$ has the edge $a\to c$ leaving it).
> - Computing $\textsf{reach}(v)\cap\textsf{reach}^{-1}(v)$ separately for every vertex takes $O(VE)$ time, not linear.
> - A path through $\textsf{scc}(G)$ stands for a **walk** in $G$ that may wander through each component; that is why component weights are sums or maxima over the whole component.

**Example.** The graph with edges $a\to b$, $b\to c$, $c\to a$, $b\to d$, $d\to e$, $e\to f$, $f\to d$, $g\to f$, $g\to h$, $h\to g$ has the components $\{a, b, c\}$, $\{d, e, f\}$, $\{g, h\}$, and $\textsf{scc}(G)$ has the two edges $\{a, b, c\}\to\{d, e, f\}$ and $\{g, h\}\to\{d, e, f\}$. Kosaraju–Sharir with every choice in alphabetical order: the search of $\textsf{rev}(G)$ finishes the vertices in the order $b\,c\,a\,e\,h\,g\,f\,d$; popping from $d$, the second phase starts searches of $G$ at $d$, $g$ and $a$, and labels $\{d, e, f\}$, $\{g, h\}$, $\{a, b, c\}$, in that order — the sink first.

**Where it appears.** [[2-algorithms/06-depth-first-search#65-strong-connectivity|§6.5]] (definitions, $\textsf{scc}(G)$ is a dag, one component in linear time, the figure), [[2-algorithms/06-depth-first-search#66-strong-components-in-linear-time|§6.6]] (Lemma 6.2, Kosaraju–Sharir with the book's example run, Tarjan's algorithm with $\textsf{low}$ values).

Related: [[concepts/depth-first-search]] · [[concepts/topological-sort]] · [[concepts/dynamic-programming-on-dags]] · [[concepts/graphs]] · [[concepts/graph-reductions]]
