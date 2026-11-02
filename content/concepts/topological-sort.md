---
title: "Topological sort"
description: "An order of the vertices of a dag in which every edge points forward: one exists exactly when the graph is acyclic, and the reverse of any depth-first postorder is one, computed in O(V + E) time — explicitly into an array, or implicitly by doing the work as each vertex finishes."
tags: [concept, algorithms, graphs, midterm-2]
aliases: ["topological order", "topological ordering", "reverse postorder", "TopologicalSort"]
---

> [!key] Theorem
> A **topological ordering** of a directed graph lists its vertices so that $u$ comes before $v$ for every edge $u\to v$. A directed graph has one **if and only if it is a dag**. In every depth-first search of a dag, $u.\mathit{post} > v.\mathit{post}$ for every edge $u\to v$, so listing the vertices by **decreasing finishing time** — reverse postorder — is a topological ordering, computed in $O(V+E)$ time.

**Why it works.** A cycle has no such order: its rightmost vertex would have an edge pointing left. In a depth-first search, an edge $u\to v$ with $u.\mathit{post} < v.\mathit{post}$ is a back edge, and a back edge plus the tree path from $v$ down to $u$ is a cycle; so in a dag every edge goes from a later-finishing to an earlier-finishing vertex. Conversely, every topological order of a dag is a reverse postorder: let the wrapper start the vertices in the reversed order.

> [!recipe] Recipe
> 1. Run DFSAll with three states per vertex; an edge into an **active** vertex means a cycle, and no topological order exists.
> 2. Write each vertex into an array **as it finishes**, from the right end: $S[V]$ first, $S[1]$ last.
> 3. Often no array is needed. To process the vertices in **reverse** topological order (sinks first — the evaluation order of a dynamic program on a dag), do the work in PostVisit: "for all vertices $v$ in postorder". For forward order, loop over the array, or take the postorder of the reversed graph $\textsf{rev}(G)$.
> 4. On an exam, cite "topological sort, $O(V+E)$" as a black box.

> [!trap]
> - **Preorder is not a topological order**, forward or backward (example below). Only finishing times work.
> - **Increasing** postorder is the **reverse** of a topological order.
> - Topological orders are rarely unique: say "a topological order", and any order with every edge pointing forward is correct.
> - A graph with a cycle has none; an algorithm that sorts an arbitrary directed graph must detect the cycle.

**Example.** The dag with edges $a\to b$, $a\to c$, $b\to d$, $c\to d$, $d\to e$, $f\to c$, searched in alphabetical order: the times are $a$ 1/10, $b$ 2/7, $d$ 3/6, $e$ 4/5, $c$ 8/9, $f$ 11/12, so the postorder is $e\,d\,b\,c\,a\,f$ and the topological order is $f\,a\,c\,b\,d\,e$ — check: every one of the six edges points right. The preorder $a\,b\,d\,e\,c\,f$ puts $c$ before $f$ although $f\to c$, and the reversed preorder $f\,c\,e\,d\,b\,a$ puts $e$ before $d$ although $d\to e$.

**Where it appears.** [[2-algorithms/06-depth-first-search#63-topological-sort|§6.3]] (the theorem, TopologicalSort, the implicit version, the reversal), [[2-algorithms/06-depth-first-search#62-detecting-cycles|§6.2]] (cycles and back edges), [[2-algorithms/06-depth-first-search#64-memoization-and-dynamic-programming|§6.4]] (evaluation order = reverse topological order), [[2-algorithms/06-depth-first-search#65-strong-connectivity|§6.5]] (ordering the strong components); evaluation orders in [[2-algorithms/03-dynamic-programming#34-the-pattern-smart-recursion|§3.4]].

Related: [[concepts/depth-first-search]] · [[concepts/dynamic-programming-on-dags]] · [[concepts/strongly-connected-components]] · [[concepts/dynamic-programming]]
