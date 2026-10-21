---
title: "Depth-first search"
description: "Recursive depth-first search and the DFSAll wrapper; starting and finishing times, the nesting of active intervals, and the classification of edges as tree, forward, back or cross — the facts that cycle detection, topological sort and strong components rest on."
tags: [concept, algorithms, graphs, midterm-2]
aliases: ["DFS", "DFSAll", "preorder and postorder", "edge classification", "back edge", "depth-first forest"]
---

> [!definition] Definition
> DFS$(v)$ marks $v$ and then calls DFS$(w)$ for every out-neighbor $w$ that is still unmarked; started with everything unmarked, it marks exactly $\textsf{reach}(v)$. The wrapper **DFSAll** calls DFS$(v)$ for every vertex still unmarked, in $O(V+E)$ time. A clock advanced at the start and at the end of every call gives each vertex a **starting time** $v.\mathit{pre}$ and a **finishing time** $v.\mathit{post}$. An edge $u\to v$ is
> - a **tree** or **forward** edge if $u.\mathit{pre} < v.\mathit{pre} < v.\mathit{post} < u.\mathit{post}$ (tree if $u$ is the parent of $v$);
> - a **back** edge if $v.\mathit{pre} < u.\mathit{pre} < u.\mathit{post} < v.\mathit{post}$;
> - a **cross** edge if $v.\mathit{post} < u.\mathit{pre}$;
>
> and $u.\mathit{post} < v.\mathit{pre}$ never happens.

**Why it works.** The recursion is a stack, and pushes and pops nest like parentheses, so two active intervals $[v.\mathit{pre}, v.\mathit{post}]$ are nested or disjoint, nested exactly when one vertex is an ancestor of the other. When DFS$(u)$ is called, every vertex that $u$ can reach through **new** (not yet marked) vertices becomes a descendant of $u$ (Lemma 6.1). An edge $u\to v$ is examined before $u$ finishes, so $v.\mathit{pre} < u.\mathit{post}$ always; hence $u.\mathit{post} < v.\mathit{post}$ only when $v$ is an ancestor of $u$ — a back edge, which closes a cycle.

> [!recipe] Recipe — using depth-first search on an exam
> - **Reachability only?** Cite whatever-first search: the graph-reduction rubric takes half a point for a more specific algorithm (such as DFS) than the problem needs.
> - **Need an order or edge classes** (cycles, topological order, strong components)? Cite DFSAll with pre/post times, $O(V+E)$, and use the facts above; do not re-explain the search.
> - **Classifying on the fly**, when examining $u\to v$: $v$ new means tree edge; $v$ active (on the recursion stack) means back edge; $v$ finished means forward edge if $v.\mathit{pre} > u.\mathit{pre}$, cross edge otherwise.
> - Put extra work in the PreVisit and PostVisit hooks instead of writing a new search.

> [!trap]
> - **Visited is not the same as on the stack.** An edge to a finished vertex (forward or cross) does not close a cycle; only an edge to an active vertex does.
> - The times and the classes depend on the order of the vertices and of each adjacency list; a claim must hold for **every** depth-first search.
> - Depth-first search does not find shortest paths (breadth-first search does), and it does not "try all paths": it finds one path to each vertex, while a graph may have exponentially many.
> - In a directed graph one call DFS$(v)$ finds only $\textsf{reach}(v)$; the number of trees of DFSAll depends on the wrapper's order.

**Example.** Search the graph with edges $a\to b$, $a\to d$, $b\to c$, $c\to a$, $c\to d$, $e\to b$, $e\to d$, everything in alphabetical order. The times are $a$ 1/8, $b$ 2/7, $c$ 3/6, $d$ 4/5, $e$ 9/10 (preorder $a\,b\,c\,d\,e$, postorder $d\,c\,b\,a\,e$). The tree edges are $a\to b$, $b\to c$, $c\to d$; $a\to d$ is a forward edge ($d$ finished inside $a$'s interval before $a$ examined it); $c\to a$ is a back edge, closing the cycle $a\to b\to c\to a$ (and $c.\mathit{post} = 6 < 8 = a.\mathit{post}$); $e\to b$ and $e\to d$ are cross edges.

**Where it appears.** [[2-algorithms/06-depth-first-search#60-depth-first-search-recursively|§6.0]] (DFS and DFSAll), [[2-algorithms/06-depth-first-search#61-preorder-and-postorder|§6.1]] (times, edge classes, Lemma 6.1, the figures), [[2-algorithms/06-depth-first-search#62-detecting-cycles|§6.2]] (back edges are cycles), [[2-algorithms/06-depth-first-search#66-strong-components-in-linear-time|§6.6]] (components are subtrees of the depth-first forest); depth-first search as the stack version of whatever-first search in [[2-algorithms/05-basic-graph-algorithms#56-important-variants|§5.6]].

Related: [[concepts/whatever-first-search]] · [[concepts/graphs]] · [[concepts/topological-sort]] · [[concepts/strongly-connected-components]] · [[concepts/dynamic-programming-on-dags]]
