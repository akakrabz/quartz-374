---
title: "Chapter 6 — Depth-First Search"
description: "Recursive depth-first search and the DFSAll wrapper; starting and finishing times and the nesting of active intervals; new, active and finished vertices and tree, forward, back and cross edges; cycle detection; topological sort by reverse postorder, explicit and implicit; memoization as depth-first search of the dependency dag and longest paths in dags; strong components, the strong component graph, and the linear-time algorithms of Kosaraju–Sharir and Tarjan."
tags: [chapter, algorithms, graphs, midterm-2]
chapter: 6
---

*Algorithms, Chapter 6 · book pp. 225–256 · [chapter PDF](https://jeffe.cs.illinois.edu/teaching/algorithms/book/06-dfs.pdf) · prev: [[2-algorithms/05-basic-graph-algorithms|Chapter 5]] · next: [[2-algorithms/07-minimum-spanning-trees|Chapter 7]] · exercises: [[2-algorithms/06-depth-first-search-exercises|solved exercises]]*

> [!abstract] In one breath
> Depth-first search is whatever-first search with a stack, written as a recursion: DFS$(v)$ marks $v$ and recurses on every unmarked out-neighbor, and the wrapper DFSAll restarts it until every vertex is marked, in $O(V+E)$ time. Stamping every vertex with a **starting time** $v.\mathit{pre}$ and a **finishing time** $v.\mathit{post}$ makes the recursion visible: the active intervals $[v.\mathit{pre}, v.\mathit{post}]$ are nested or disjoint, nested exactly for ancestors and descendants, and how the two intervals of an edge $u\to v$ sit determines whether it is a tree, forward, back or cross edge. A directed graph has a cycle if and only if depth-first search finds a back edge, so in a dag every edge $u\to v$ has $u.\mathit{post} > v.\mathit{post}$, and **reverse postorder is a topological order**. Memoized recursion is depth-first search of the dependency dag and dynamic programming evaluates it in postorder; the model problem, longest paths in a dag, takes $O(V+E)$ time although it is NP-hard in general graphs. Finally, the **strong components** of any directed graph contract to a dag, $\textsf{scc}(G)$, and two depth-first algorithms find them all in $O(V+E)$ time: Kosaraju–Sharir (search $\textsf{rev}(G)$, then search $G$ in the reverse of that postorder) and Tarjan (one search with $\textsf{low}$ values and a stack).

## 6.0 Depth-first search, recursively

Depth-first search is the stack version of whatever-first search ([[2-algorithms/05-basic-graph-algorithms#56-important-variants|§5.6]]), but it is almost always written recursively, with the recursion stack as the stack:

```text
DFS(v):
    if v is unmarked
        mark v
        for each edge v→w
            DFS(w)
```

Testing the mark **before** recursing calls DFS once per vertex. Two black-box hooks, PreVisit and PostVisit, let the same skeleton compute everything in this chapter, and parent pointers record the search:

```text
DFS(v):
    mark v
    PreVisit(v)
    for each edge v→w
        if w is unmarked
            parent(w) ← v
            DFS(w)
    PostVisit(v)
```

Write $\textsf{reach}(v)$ for the set of vertices that $v$ can reach, $v$ itself included. If all vertices start unmarked, DFS$(v)$ marks **exactly** $\textsf{reach}(v)$, and the parent pointers form a tree rooted at $v$ whose vertices are $\textsf{reach}(v)$. In an undirected graph, $\textsf{reach}(v)$ is the component of $v$, so the tree spans the component. In a directed graph, different start vertices reach different, overlapping sets, and the tree need not span the graph even when the graph looks "connected" (the book's Figure 6.1).

**The wrapper.** To search the whole graph, restart from every vertex that is still unmarked; Preprocess is a third hook, for initialization:

```text
DFSAll(G):
    Preprocess(G)
    for all vertices v
        unmark v
    for all vertices v
        if v is unmarked
            DFS(v)
```

Equivalently, add a new vertex $s$ with an edge $s\to v$ to every vertex and call DFS$(s)$ once: if $s$'s edges are listed in the wrapper's order, the traversal is the same and the trees of DFSAll are the subtrees of $s$'s children. (This equivalence is special to depth-first search: breadth-first search from an added source is not breadth-first search wrapped in a loop.) In an undirected graph the parent pointers of DFSAll form a spanning forest, one tree per component. In a directed graph the number of trees depends on the graph and on the order of the wrapper's loop, and can be anything from 1 to $V$, even for a graph that looks "connected": on the path $0\to1\to2\to3\to4$, the order $0, 1, 2, 3, 4$ gives one tree and the order $4, 3, 2, 1, 0$ gives five.

> [!key] Running time
> With adjacency lists, DFSAll calls DFS exactly once per vertex and examines every edge exactly once, from its tail: $O(V+E)$ time, plus the time spent in the hooks.

Concept page: [[concepts/depth-first-search]].

## 6.1 Preorder and postorder

Passing a counter through the recursion stamps every vertex twice (the book's Figure 6.3):

```text
DFSAll(G):
    clock ← 0
    for all vertices v
        unmark v
    for all vertices v
        if v is unmarked
            clock ← DFS(v, clock)

DFS(v, clock):
    mark v
    clock ← clock + 1;  v.pre ← clock
    for each edge v→w
        if w is unmarked
            w.parent ← v
            clock ← DFS(w, clock)
    clock ← clock + 1;  v.post ← clock
    return clock
```

The same thing in hook form: Preprocess sets a global $\mathit{clock} \leftarrow 0$, PreVisit and PostVisit each advance it and record it in $v.\mathit{pre}$, respectively $v.\mathit{post}$.

> [!definition] Definition — starting time, finishing time, active interval
> $v.\mathit{pre}$, the **starting time** of $v$, is assigned just after $v$ is pushed on the recursion stack; $v.\mathit{post}$, its **finishing time**, just before $v$ is popped. The clock takes each of the values $1, 2, \ldots, 2V$ exactly once. Sorting the vertices by $\mathit{pre}$ gives a **preordering**, by $\mathit{post}$ a **postordering**, and $[v.\mathit{pre}, v.\mathit{post}]$ is the **active interval** of $v$. Both orders depend on the order in which DFSAll considers the vertices and DFS considers the edges out of each vertex; most graphs have many. (Neither should be called "the depth-first order".)

> [!key] Nesting of active intervals
> For any two vertices $u$ and $v$, the active intervals $[u.\mathit{pre}, u.\mathit{post}]$ and $[v.\mathit{pre}, v.\mathit{post}]$ are either **disjoint or nested**, and $[u.\mathit{pre}, u.\mathit{post}]$ contains $[v.\mathit{pre}, v.\mathit{post}]$ if and only if DFS$(v)$ is called during DFS$(u)$, that is, if and only if $u$ is an ancestor of $v$ in the depth-first forest.

The reason is that pushes and pops on a stack nest like parentheses. The book's running example, a directed graph on the 16 vertices $a, \ldots, p$, with every choice made in alphabetical order:

<!-- fig:a06-dfs-forest -->
<figure class="cs-fig"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 560 452" width="560" height="452" role="img" style="font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-size:14px"><title>directed graph on a four by four grid with its depth-first forest, edge classes and pre/post times</title><defs><marker id="ARR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs><line x1="30" y1="432" x2="64" y2="432" stroke="var(--accent)" stroke-width="2.4" stroke-linecap="round"/><text x="72" y="432" text-anchor="start" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">tree (14)</text><line x1="162" y1="432" x2="196" y2="432" stroke="var(--accent2)" stroke-width="1.7" stroke-linecap="round" stroke-dasharray="7 4"/><text x="204" y="432" text-anchor="start" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">forward (2)</text><line x1="294" y1="432" x2="328" y2="432" stroke="var(--hi)" stroke-width="1.7" stroke-linecap="round" stroke-dasharray="7 3 2 3"/><text x="336" y="432" text-anchor="start" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">back (5)</text><line x1="426" y1="432" x2="460" y2="432" stroke="var(--muted)" stroke-width="1.7" stroke-linecap="round" stroke-dasharray="2 3"/><text x="468" y="432" text-anchor="start" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">cross (3)</text><path d="M77,52 L180.5,52" fill="none" stroke="var(--accent)" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M200,69 L200,132.5" fill="none" stroke="var(--accent)" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M353.8,61.9 L464.1,140.7" fill="none" stroke="var(--accent)" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M463,52 L359.5,52" fill="none" stroke="var(--hi)" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)" stroke-dasharray="7 3 2 3"/><path d="M77,152 L180.5,152" fill="none" stroke="var(--muted)" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)" stroke-dasharray="2 3"/><path d="M60,169 L60,232.5" fill="none" stroke="var(--accent)" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M217,152 L320.5,152" fill="none" stroke="var(--accent)" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M216,157.7 L461.6,245.4" fill="none" stroke="var(--accent2)" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)" stroke-dasharray="7 4"/><path d="M324.7,144.6 Q205.4,86.9 79,56.6" fill="none" stroke="var(--hi)" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)" stroke-dasharray="7 3 2 3"/><path d="M340,135 L340,71.5" fill="none" stroke="var(--accent)" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M340,169 L340,232.5" fill="none" stroke="var(--accent2)" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)" stroke-dasharray="7 4"/><path d="M480,135 L480,71.5" fill="none" stroke="var(--accent)" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M480,169 L480,232.5" fill="none" stroke="var(--accent)" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M73.8,261.9 L184.1,340.7" fill="none" stroke="var(--accent)" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M217,252 L320.5,252" fill="none" stroke="var(--muted)" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)" stroke-dasharray="2 3"/><path d="M186.2,261.9 L75.9,340.7" fill="none" stroke="var(--accent)" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M353.8,242.1 L464.1,163.3" fill="none" stroke="var(--hi)" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)" stroke-dasharray="7 3 2 3"/><path d="M357,252 L460.5,252" fill="none" stroke="var(--hi)" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)" stroke-dasharray="7 3 2 3"/><path d="M466.2,261.9 L355.9,340.7" fill="none" stroke="var(--accent)" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M480,269 L480,332.5" fill="none" stroke="var(--accent)" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M60,335 L60,271.5" fill="none" stroke="var(--hi)" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)" stroke-dasharray="7 3 2 3"/><path d="M200,335 L200,271.5" fill="none" stroke="var(--accent)" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M217,352 L320.5,352" fill="none" stroke="var(--muted)" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)" stroke-dasharray="2 3"/><path d="M340,335 L340,271.5" fill="none" stroke="var(--accent)" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><line x1="17" y1="52" x2="40.5" y2="52" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" marker-end="url(#ARR)"/><circle cx="60" cy="52" r="17" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="60" y="53" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">a</text><circle cx="200" cy="52" r="17" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="200" y="53" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">b</text><circle cx="340" cy="52" r="17" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="340" y="53" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">c</text><circle cx="480" cy="52" r="17" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="480" y="53" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">d</text><line x1="17" y1="152" x2="40.5" y2="152" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" marker-end="url(#ARR)"/><circle cx="60" cy="152" r="17" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="60" y="153" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">e</text><circle cx="200" cy="152" r="17" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="200" y="153" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">f</text><circle cx="340" cy="152" r="17" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="340" y="153" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">g</text><circle cx="480" cy="152" r="17" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="480" y="153" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">h</text><circle cx="60" cy="252" r="17" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="60" y="253" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">i</text><circle cx="200" cy="252" r="17" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="200" y="253" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">j</text><circle cx="340" cy="252" r="17" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="340" y="253" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">k</text><circle cx="480" cy="252" r="17" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="480" y="253" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">l</text><circle cx="60" cy="352" r="17" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="60" y="353" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">m</text><circle cx="200" cy="352" r="17" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="200" y="353" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n</text><circle cx="340" cy="352" r="17" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="340" y="353" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">o</text><circle cx="480" cy="352" r="17" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="480" y="353" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">p</text><text x="60" y="23" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">1/22</text><text x="200" y="23" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">2/21</text><text x="340" y="23" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">5/18</text><text x="480" y="23" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">7/8</text><text x="60" y="123" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">23/32</text><text x="200" y="182" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">3/20</text><text x="377" y="140" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">4/19</text><text x="517" y="152" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">6/17</text><text x="23" y="252" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">24/31</text><text x="200" y="223" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">26/29</text><text x="306" y="276" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">11/12</text><text x="517" y="252" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">9/16</text><text x="60" y="382" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">27/28</text><text x="200" y="382" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">25/30</text><text x="340" y="382" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">10/13</text><text x="480" y="382" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">14/15</text></svg><figcaption><strong>A depth-first forest of the book’s example graph.</strong> DFSAll considers the vertices, and every vertex its edges, in alphabetical order; the two roots <i>a</i> and <i>e</i> have entry arrows, and each vertex is labeled <i>pre</i>/<i>post</i>. Preorder <i>abfgchdlokpeinjm</i>, postorder <i>dkoplhcgfbamjnie</i>. Of the 24 edges, 14 are tree edges (16 vertices minus 2 roots), 2 forward, 5 back and 3 cross. The back edges <i>g</i>→<i>a</i>, <i>d</i>→<i>c</i>, <i>k</i>→<i>h</i>, <i>k</i>→<i>l</i> and <i>m</i>→<i>i</i> are exactly the edges <i>u</i>→<i>v</i> with <i>u.post</i> &lt; <i>v.post</i>.</figcaption></figure>

<!-- fig:a06-intervals -->
<figure class="cs-fig"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 250" width="600" height="250" role="img" style="font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-size:14px"><title>active intervals of the sixteen vertices drawn as nested bars over a time axis from 1 to 32</title><defs><marker id="ARR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs><rect x="28" y="14" width="361.2" height="18" rx="3" fill="var(--accent)" fill-opacity="0.14" stroke="currentColor" stroke-width="1.1"/><text x="208.6" y="23.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">a</text><rect x="45.2" y="36" width="326.8" height="18" rx="3" fill="var(--accent)" fill-opacity="0.14" stroke="currentColor" stroke-width="1.1"/><text x="208.6" y="45.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">b</text><rect x="96.8" y="102" width="223.6" height="18" rx="3" fill="var(--accent)" fill-opacity="0.14" stroke="currentColor" stroke-width="1.1"/><text x="208.6" y="111.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">c</text><rect x="131.2" y="146" width="17.2" height="18" rx="3" fill="var(--accent)" fill-opacity="0.14" stroke="currentColor" stroke-width="1.1"/><text x="139.8" y="155.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">d</text><rect x="406.4" y="14" width="154.8" height="18" rx="3" fill="var(--accent)" fill-opacity="0.14" stroke="currentColor" stroke-width="1.1"/><text x="483.8" y="23.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">e</text><rect x="62.4" y="58" width="292.4" height="18" rx="3" fill="var(--accent)" fill-opacity="0.14" stroke="currentColor" stroke-width="1.1"/><text x="208.6" y="67.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">f</text><rect x="79.6" y="80" width="258" height="18" rx="3" fill="var(--accent)" fill-opacity="0.14" stroke="currentColor" stroke-width="1.1"/><text x="208.6" y="89.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">g</text><rect x="114" y="124" width="189.2" height="18" rx="3" fill="var(--accent)" fill-opacity="0.14" stroke="currentColor" stroke-width="1.1"/><text x="208.6" y="133.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">h</text><rect x="423.6" y="36" width="120.4" height="18" rx="3" fill="var(--accent)" fill-opacity="0.14" stroke="currentColor" stroke-width="1.1"/><text x="483.8" y="45.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">i</text><rect x="458" y="80" width="51.6" height="18" rx="3" fill="var(--accent)" fill-opacity="0.14" stroke="currentColor" stroke-width="1.1"/><text x="483.8" y="89.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">j</text><rect x="200" y="190" width="17.2" height="18" rx="3" fill="var(--accent)" fill-opacity="0.14" stroke="currentColor" stroke-width="1.1"/><text x="208.6" y="199.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">k</text><rect x="165.6" y="146" width="120.4" height="18" rx="3" fill="var(--accent)" fill-opacity="0.14" stroke="currentColor" stroke-width="1.1"/><text x="225.8" y="155.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">l</text><rect x="475.2" y="102" width="17.2" height="18" rx="3" fill="var(--accent)" fill-opacity="0.14" stroke="currentColor" stroke-width="1.1"/><text x="483.8" y="111.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">m</text><rect x="440.8" y="58" width="86" height="18" rx="3" fill="var(--accent)" fill-opacity="0.14" stroke="currentColor" stroke-width="1.1"/><text x="483.8" y="67.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n</text><rect x="182.8" y="168" width="51.6" height="18" rx="3" fill="var(--accent)" fill-opacity="0.14" stroke="currentColor" stroke-width="1.1"/><text x="208.6" y="177.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">o</text><rect x="251.6" y="168" width="17.2" height="18" rx="3" fill="var(--accent)" fill-opacity="0.14" stroke="currentColor" stroke-width="1.1"/><text x="260.2" y="177.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">p</text><line x1="18" y1="220" x2="575.2" y2="220" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" marker-end="url(#ARR)"/><line x1="28" y1="216" x2="28" y2="224" stroke="currentColor" stroke-width="1" stroke-linecap="round"/><line x1="28" y1="14" x2="28" y2="216" stroke="currentColor" stroke-width="0.6" stroke-linecap="round" stroke-dasharray="2 3" opacity="0.35"/><text x="28" y="234" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">1</text><line x1="45.2" y1="216" x2="45.2" y2="224" stroke="currentColor" stroke-width="1" stroke-linecap="round"/><line x1="45.2" y1="14" x2="45.2" y2="216" stroke="currentColor" stroke-width="0.6" stroke-linecap="round" stroke-dasharray="2 3" opacity="0.35"/><text x="45.2" y="234" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">2</text><line x1="62.4" y1="216" x2="62.4" y2="224" stroke="currentColor" stroke-width="1" stroke-linecap="round"/><line x1="62.4" y1="14" x2="62.4" y2="216" stroke="currentColor" stroke-width="0.6" stroke-linecap="round" stroke-dasharray="2 3" opacity="0.35"/><text x="62.4" y="234" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">3</text><line x1="79.6" y1="216" x2="79.6" y2="224" stroke="currentColor" stroke-width="1" stroke-linecap="round"/><line x1="79.6" y1="14" x2="79.6" y2="216" stroke="currentColor" stroke-width="0.6" stroke-linecap="round" stroke-dasharray="2 3" opacity="0.35"/><text x="79.6" y="234" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">4</text><line x1="96.8" y1="216" x2="96.8" y2="224" stroke="currentColor" stroke-width="1" stroke-linecap="round"/><line x1="96.8" y1="14" x2="96.8" y2="216" stroke="currentColor" stroke-width="0.6" stroke-linecap="round" stroke-dasharray="2 3" opacity="0.35"/><text x="96.8" y="234" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">5</text><line x1="114" y1="216" x2="114" y2="224" stroke="currentColor" stroke-width="1" stroke-linecap="round"/><line x1="114" y1="14" x2="114" y2="216" stroke="currentColor" stroke-width="0.6" stroke-linecap="round" stroke-dasharray="2 3" opacity="0.35"/><text x="114" y="234" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">6</text><line x1="131.2" y1="216" x2="131.2" y2="224" stroke="currentColor" stroke-width="1" stroke-linecap="round"/><line x1="131.2" y1="14" x2="131.2" y2="216" stroke="currentColor" stroke-width="0.6" stroke-linecap="round" stroke-dasharray="2 3" opacity="0.35"/><text x="131.2" y="234" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">7</text><line x1="148.4" y1="216" x2="148.4" y2="224" stroke="currentColor" stroke-width="1" stroke-linecap="round"/><line x1="148.4" y1="14" x2="148.4" y2="216" stroke="currentColor" stroke-width="0.6" stroke-linecap="round" stroke-dasharray="2 3" opacity="0.35"/><text x="148.4" y="234" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">8</text><line x1="165.6" y1="216" x2="165.6" y2="224" stroke="currentColor" stroke-width="1" stroke-linecap="round"/><line x1="165.6" y1="14" x2="165.6" y2="216" stroke="currentColor" stroke-width="0.6" stroke-linecap="round" stroke-dasharray="2 3" opacity="0.35"/><text x="165.6" y="234" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">9</text><line x1="182.8" y1="216" x2="182.8" y2="224" stroke="currentColor" stroke-width="1" stroke-linecap="round"/><line x1="182.8" y1="14" x2="182.8" y2="216" stroke="currentColor" stroke-width="0.6" stroke-linecap="round" stroke-dasharray="2 3" opacity="0.35"/><text x="182.8" y="234" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">10</text><line x1="200" y1="216" x2="200" y2="224" stroke="currentColor" stroke-width="1" stroke-linecap="round"/><line x1="200" y1="14" x2="200" y2="216" stroke="currentColor" stroke-width="0.6" stroke-linecap="round" stroke-dasharray="2 3" opacity="0.35"/><text x="200" y="234" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">11</text><line x1="217.2" y1="216" x2="217.2" y2="224" stroke="currentColor" stroke-width="1" stroke-linecap="round"/><line x1="217.2" y1="14" x2="217.2" y2="216" stroke="currentColor" stroke-width="0.6" stroke-linecap="round" stroke-dasharray="2 3" opacity="0.35"/><text x="217.2" y="234" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">12</text><line x1="234.4" y1="216" x2="234.4" y2="224" stroke="currentColor" stroke-width="1" stroke-linecap="round"/><line x1="234.4" y1="14" x2="234.4" y2="216" stroke="currentColor" stroke-width="0.6" stroke-linecap="round" stroke-dasharray="2 3" opacity="0.35"/><text x="234.4" y="234" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">13</text><line x1="251.6" y1="216" x2="251.6" y2="224" stroke="currentColor" stroke-width="1" stroke-linecap="round"/><line x1="251.6" y1="14" x2="251.6" y2="216" stroke="currentColor" stroke-width="0.6" stroke-linecap="round" stroke-dasharray="2 3" opacity="0.35"/><text x="251.6" y="234" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">14</text><line x1="268.8" y1="216" x2="268.8" y2="224" stroke="currentColor" stroke-width="1" stroke-linecap="round"/><line x1="268.8" y1="14" x2="268.8" y2="216" stroke="currentColor" stroke-width="0.6" stroke-linecap="round" stroke-dasharray="2 3" opacity="0.35"/><text x="268.8" y="234" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">15</text><line x1="286" y1="216" x2="286" y2="224" stroke="currentColor" stroke-width="1" stroke-linecap="round"/><line x1="286" y1="14" x2="286" y2="216" stroke="currentColor" stroke-width="0.6" stroke-linecap="round" stroke-dasharray="2 3" opacity="0.35"/><text x="286" y="234" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">16</text><line x1="303.2" y1="216" x2="303.2" y2="224" stroke="currentColor" stroke-width="1" stroke-linecap="round"/><line x1="303.2" y1="14" x2="303.2" y2="216" stroke="currentColor" stroke-width="0.6" stroke-linecap="round" stroke-dasharray="2 3" opacity="0.35"/><text x="303.2" y="234" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">17</text><line x1="320.4" y1="216" x2="320.4" y2="224" stroke="currentColor" stroke-width="1" stroke-linecap="round"/><line x1="320.4" y1="14" x2="320.4" y2="216" stroke="currentColor" stroke-width="0.6" stroke-linecap="round" stroke-dasharray="2 3" opacity="0.35"/><text x="320.4" y="234" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">18</text><line x1="337.6" y1="216" x2="337.6" y2="224" stroke="currentColor" stroke-width="1" stroke-linecap="round"/><line x1="337.6" y1="14" x2="337.6" y2="216" stroke="currentColor" stroke-width="0.6" stroke-linecap="round" stroke-dasharray="2 3" opacity="0.35"/><text x="337.6" y="234" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">19</text><line x1="354.8" y1="216" x2="354.8" y2="224" stroke="currentColor" stroke-width="1" stroke-linecap="round"/><line x1="354.8" y1="14" x2="354.8" y2="216" stroke="currentColor" stroke-width="0.6" stroke-linecap="round" stroke-dasharray="2 3" opacity="0.35"/><text x="354.8" y="234" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">20</text><line x1="372" y1="216" x2="372" y2="224" stroke="currentColor" stroke-width="1" stroke-linecap="round"/><line x1="372" y1="14" x2="372" y2="216" stroke="currentColor" stroke-width="0.6" stroke-linecap="round" stroke-dasharray="2 3" opacity="0.35"/><text x="372" y="234" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">21</text><line x1="389.2" y1="216" x2="389.2" y2="224" stroke="currentColor" stroke-width="1" stroke-linecap="round"/><line x1="389.2" y1="14" x2="389.2" y2="216" stroke="currentColor" stroke-width="0.6" stroke-linecap="round" stroke-dasharray="2 3" opacity="0.35"/><text x="389.2" y="234" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">22</text><line x1="406.4" y1="216" x2="406.4" y2="224" stroke="currentColor" stroke-width="1" stroke-linecap="round"/><line x1="406.4" y1="14" x2="406.4" y2="216" stroke="currentColor" stroke-width="0.6" stroke-linecap="round" stroke-dasharray="2 3" opacity="0.35"/><text x="406.4" y="234" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">23</text><line x1="423.6" y1="216" x2="423.6" y2="224" stroke="currentColor" stroke-width="1" stroke-linecap="round"/><line x1="423.6" y1="14" x2="423.6" y2="216" stroke="currentColor" stroke-width="0.6" stroke-linecap="round" stroke-dasharray="2 3" opacity="0.35"/><text x="423.6" y="234" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">24</text><line x1="440.8" y1="216" x2="440.8" y2="224" stroke="currentColor" stroke-width="1" stroke-linecap="round"/><line x1="440.8" y1="14" x2="440.8" y2="216" stroke="currentColor" stroke-width="0.6" stroke-linecap="round" stroke-dasharray="2 3" opacity="0.35"/><text x="440.8" y="234" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">25</text><line x1="458" y1="216" x2="458" y2="224" stroke="currentColor" stroke-width="1" stroke-linecap="round"/><line x1="458" y1="14" x2="458" y2="216" stroke="currentColor" stroke-width="0.6" stroke-linecap="round" stroke-dasharray="2 3" opacity="0.35"/><text x="458" y="234" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">26</text><line x1="475.2" y1="216" x2="475.2" y2="224" stroke="currentColor" stroke-width="1" stroke-linecap="round"/><line x1="475.2" y1="14" x2="475.2" y2="216" stroke="currentColor" stroke-width="0.6" stroke-linecap="round" stroke-dasharray="2 3" opacity="0.35"/><text x="475.2" y="234" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">27</text><line x1="492.4" y1="216" x2="492.4" y2="224" stroke="currentColor" stroke-width="1" stroke-linecap="round"/><line x1="492.4" y1="14" x2="492.4" y2="216" stroke="currentColor" stroke-width="0.6" stroke-linecap="round" stroke-dasharray="2 3" opacity="0.35"/><text x="492.4" y="234" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">28</text><line x1="509.6" y1="216" x2="509.6" y2="224" stroke="currentColor" stroke-width="1" stroke-linecap="round"/><line x1="509.6" y1="14" x2="509.6" y2="216" stroke="currentColor" stroke-width="0.6" stroke-linecap="round" stroke-dasharray="2 3" opacity="0.35"/><text x="509.6" y="234" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">29</text><line x1="526.8" y1="216" x2="526.8" y2="224" stroke="currentColor" stroke-width="1" stroke-linecap="round"/><line x1="526.8" y1="14" x2="526.8" y2="216" stroke="currentColor" stroke-width="0.6" stroke-linecap="round" stroke-dasharray="2 3" opacity="0.35"/><text x="526.8" y="234" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">30</text><line x1="544" y1="216" x2="544" y2="224" stroke="currentColor" stroke-width="1" stroke-linecap="round"/><line x1="544" y1="14" x2="544" y2="216" stroke="currentColor" stroke-width="0.6" stroke-linecap="round" stroke-dasharray="2 3" opacity="0.35"/><text x="544" y="234" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">31</text><line x1="561.2" y1="216" x2="561.2" y2="224" stroke="currentColor" stroke-width="1" stroke-linecap="round"/><line x1="561.2" y1="14" x2="561.2" y2="216" stroke="currentColor" stroke-width="0.6" stroke-linecap="round" stroke-dasharray="2 3" opacity="0.35"/><text x="561.2" y="234" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">32</text><text x="14" y="234" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:10px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;"></text></svg><figcaption><strong>The active intervals of the same traversal.</strong> Vertex <i>v</i> occupies [<i>v.pre</i>, <i>v.post</i>], drawn one row below its parent. Any two intervals are nested or disjoint, and nested exactly when one vertex is an ancestor of the other; reading the left ends gives the preorder, the right ends the postorder. The active vertices at any moment are the intervals stacked above that time: a path of tree edges.</figcaption></figure>

### Classifying vertices and edges

> [!definition] Definition — new, active, finished
> At any moment during DFSAll, a vertex $v$ is
> - **new** if DFS$(v)$ has not been called: $\mathit{clock} < v.\mathit{pre}$;
> - **active** if DFS$(v)$ has been called but has not returned: $v.\mathit{pre} \le \mathit{clock} < v.\mathit{post}$;
> - **finished** if DFS$(v)$ has returned: $v.\mathit{post} \le \mathit{clock}$.
>
> The active vertices are exactly the vertices on the recursion stack, so at every moment they form a directed path of tree edges, ending at the vertex being explored.

Every edge $u\to v$ falls into one of four classes, decided by the state of $v$ when DFS$(u)$ begins — equivalently, by how the two active intervals sit:

| state of $v$ when DFS$(u)$ begins | order of the times | class of $u\to v$ |
|---|---|---|
| new | $u.\mathit{pre} < v.\mathit{pre} < v.\mathit{post} < u.\mathit{post}$ | **tree edge** if DFS$(u)$ calls DFS$(v)$ itself ($u = v.\mathit{parent}$); otherwise **forward edge** |
| active | $v.\mathit{pre} < u.\mathit{pre} < u.\mathit{post} < v.\mathit{post}$ | **back edge** — and $G$ has a path from $v$ to $u$ |
| finished | $v.\mathit{post} < u.\mathit{pre}$ | **cross edge** |
| — | $u.\mathit{post} < v.\mathit{pre}$ | impossible |

Why: if $v$ is new, DFS$(u)$ examines $u\to v$ before it returns, so DFS$(v)$ is called during DFS$(u)$ — directly (tree edge) or from a deeper call (forward edge). If $v$ is active, it is on the recursion stack below $u$, so it is an ancestor of $u$ and the tree path from $v$ down to $u$ is a path in $G$. If $v$ is finished, $v.\mathit{post}$ is already smaller than $u.\mathit{pre}$. And $u.\mathit{post} < v.\mathit{pre}$ cannot happen, because $v$ is marked before DFS$(u)$ is done examining $u\to v$. (A loop $u\to u$ counts as a back edge: $u$ is active when its own call begins.)

> [!tip] Classifying while the search runs
> An implementation sees the state of $v$ when it **examines** the edge $u\to v$: new means tree edge, active means back edge, and finished means forward edge if $v.\mathit{pre} > u.\mathit{pre}$, cross edge otherwise.

> [!example] Example — the edges of the figure
> The 24 edges split into 14 **tree** edges (16 vertices minus 2 roots), 2 **forward** edges, $f\to l$ ($[9, 16]$ inside $[3, 20]$) and $g\to k$, 5 **back** edges, $g\to a$, $d\to c$, $k\to h$, $k\to l$ and $m\to i$, and 3 **cross** edges, $e\to f$ ($f.\mathit{post} = 20 < 23 = e.\mathit{pre}$), $j\to k$ and $n\to o$. The classes change if the vertices or the edges are considered in a different order.

The key lemma characterizes the depth-first forest by the states of the vertices during the search.

> [!key] Lemma 6.1
> Fix any depth-first traversal of any directed graph $G$. For all vertices $u$ and $v$ of $G$, the following are equivalent:
> - (a) $u$ is an ancestor of $v$ in the depth-first forest ($u = v$ allowed);
> - (b) $u.\mathit{pre} \le v.\mathit{pre} < v.\mathit{post} \le u.\mathit{post}$;
> - (c) just after DFS$(v)$ is called, $u$ is active;
> - (d) just before DFS$(u)$ is called, there is a path from $u$ to $v$ on which every vertex, $u$ and $v$ included, is new.

> [!proof]- Proof (click to expand)
> **(a) ⇒ (b), (c), (d).** Along the path of tree edges from $u$ down to $v$, every vertex's active interval lies inside its parent's, so (b) holds; hence $u$ is active during all of DFS$(v)$, which is (c); and every vertex of the tree path starts after $u$ does, so all of them are new just before DFS$(u)$ is called, which is (d).
>
> **(b) ⇒ (a)** because intervals nest only along recursive calls, and **(c) ⇒ (b)** because $v.\mathit{pre}$ then lies in the active interval of $u$, and intervals are nested or disjoint.
>
> **(d) ⇒ (a)**, by contraposition. Suppose $v$ is not a descendant of $u$, and fix any path $P$ from $u$ to $v$. Let $x$ be the first vertex of $P$ that is not a descendant of $u$, and $w$ its predecessor on $P$, a descendant of $u$. When DFS$(w)$ examines $w\to x$, either $x$ is unmarked and becomes a child of $w$ — impossible, it would be a descendant of $u$ — or it is already marked, so $x.\mathit{pre} < w.\mathit{post} \le u.\mathit{post}$. A vertex that starts while $u$ is active is a descendant of $u$, so in fact $x.\mathit{pre} < u.\mathit{pre}$: $x$ is already active or finished when DFS$(u)$ is called, and $P$ is not a path of new vertices.

Form (d) is the one the rest of the chapter uses: **everything that $u$ can reach through new vertices when DFS$(u)$ is called becomes a descendant of $u$.**

Concept page: [[concepts/depth-first-search]].

## 6.2 Detecting cycles

> [!definition] Definition — dag, source, sink
> A **directed acyclic graph**, or **dag**, is a directed graph with no directed cycle. A **source** is a vertex with no incoming edges, a **sink** a vertex with no outgoing edges; an isolated vertex is both. Every dag has at least one source and at least one sink: walking forward along edges from any vertex can never repeat a vertex, so the walk stops, and only at a sink (backward, at a source). In the edgeless graph every vertex is both. The book's dag of Figure 6.6 has the sources $e, f, j$ and the sinks $b, c, p$.

> [!key] Back edges are cycles
> For any depth-first traversal of a directed graph $G$ without loops, the following are equivalent:
> 1. $G$ has a directed cycle;
> 2. the traversal finds a back edge;
> 3. some edge $u\to v$ has $u.\mathit{post} < v.\mathit{post}$.

> [!proof]- Proof (click to expand)
> **(2) ⇔ (3)** by the classification table: back edges have $u.\mathit{post} < v.\mathit{post}$; tree, forward and cross edges have $v.\mathit{post} < u.\mathit{post}$.
>
> **(2) ⇒ (1).** A back edge $u\to v$, followed by the tree path from $v$ down to $u$, is a directed cycle.
>
> **(1) ⇒ (2).** Let $v$ be the vertex of the cycle that starts first. Just before DFS$(v)$ is called, every vertex of the cycle is new, so by Lemma 6.1(d) every vertex of the cycle becomes a descendant of $v$. The cycle's edge $u\to v$ into $v$ then goes from a descendant $u$ to its ancestor $v$, which is active when DFS$(u)$ begins: a back edge.

(The book proves only (3) ⇒ (1) here. The converse also follows from §6.3: if every edge had $u.\mathit{post} > v.\mathit{post}$, reverse postorder would be a topological order, which a graph with a cycle cannot have.) So acyclicity takes $O(V+E)$ time in two ways: compute a postordering and test every edge for $u.\mathit{post} < v.\mathit{post}$; or keep each vertex's state and stop at the first edge into an **active** vertex:

```text
IsAcyclic(G):
    for all vertices v
        v.status ← New
    for all vertices v
        if v.status = New
            if IsAcyclicDFS(v) = False
                return False
    return True

IsAcyclicDFS(v):
    v.status ← Active
    for each edge v→w
        if w.status = Active
            return False
        else if w.status = New
            if IsAcyclicDFS(w) = False
                return False
    v.status ← Finished
    return True
```

> [!trap] Cycle-detection traps
> - **"An edge to a visited vertex closes a cycle" is false** in a directed graph: forward and cross edges also lead to visited (finished) vertices. In the dag $a\to b$, $b\to c$, $a\to c$, the search from $a$ meets $c$ a second time along the forward edge $a\to c$. Only an edge into an **active** vertex closes a cycle — so a directed search needs three states (or the clock), not two.
> - The test $u.\mathit{post} < v.\mathit{post}$ uses the times of **one** complete traversal. With loops allowed, a loop $u\to u$ is a cycle of length 1, a back edge with $u.\mathit{post} = v.\mathit{post}$, so the test becomes $u.\mathit{post} \le v.\mathit{post}$.

Concept page: [[concepts/depth-first-search]].

## 6.3 Topological sort

> [!definition] Definition — topological ordering
> A **topological ordering** of a directed graph $G$ is a total order $\prec$ of its vertices with $u \prec v$ for every edge $u\to v$: drawn on a horizontal line in that order, every edge points to the right. A graph with a directed cycle has none — the rightmost vertex of the cycle would have an edge pointing left.

> [!key] Theorem — reverse postorder is a topological order
> If $G$ is a dag, then $u.\mathit{post} > v.\mathit{post}$ for every edge $u\to v$, in every depth-first traversal of $G$. So the reversal of any postordering of a dag is a topological ordering, and a directed graph has a topological ordering if and only if it is acyclic.

Proof: $u.\mathit{post} < v.\mathit{post}$ only for back edges, a back edge closes a cycle, and $u.\mathit{post} = v.\mathit{post}$ only for $u = v$. Conversely, **every** topological order of a dag is the reversal of some postordering: let the wrapper visit the vertices in the reversed topological order; then every vertex is visited after all its out-neighbors, every call returns at once, and the postorder is exactly that sequence.

> [!example] Examples
> - The book's dag of Figure 6.6, with DFSAll and every adjacency list in alphabetical order: postorder $b\,a\,c\,d\,h\,p\,l\,k\,o\,n\,i\,e\,g\,f\,m\,j$, hence the topological order $j\,m\,f\,g\,e\,i\,n\,o\,k\,l\,p\,h\,d\,c\,a\,b$ (the book's Figure 6.8).
> - The weighted dag in the figure of §6.4: postorder $t\,d\,c\,b\,x\,a\,s$, topological order $s\,a\,x\,b\,c\,d\,t$.

To store the order, write each vertex into an array when it finishes, filling from the right (the book's Figure 6.9):

```text
TopologicalSort(G):
    for all vertices v
        v.status ← New
    clock ← V
    for all vertices v
        if v.status = New
            clock ← TopSortDFS(v, clock)
    return S[1 .. V]

TopSortDFS(v, clock):
    v.status ← Active
    for each edge v→w
        if w.status = New
            clock ← TopSortDFS(w, clock)    ⟨⟨the book prints v here⟩⟩
        else if w.status = Active
            fail gracefully                  ⟨⟨G has a cycle⟩⟩
    v.status ← Finished
    S[clock] ← v
    clock ← clock − 1
    return clock
```

Here the clock counts **down** from $V$, so the first vertex to finish lands in $S[V]$ and the last in $S[1]$. The running time is $O(V+E)$. As printed, the recursive call TopSortDFS$(v, \mathit{clock})$ would call itself on $v$ forever as soon as $v$ has an edge to a new vertex.

### Implicit topological sort

Usually the list itself is not the goal: we want to do some work at every vertex, in topological or in reverse topological order. Reverse topological order is postorder, so it suffices to do the work at the end of each recursive call:

```text
PostProcess(G):
    for all vertices v
        v.status ← New
    for all vertices v
        if v.status = New                ⟨⟨the book prints "v is unmarked"⟩⟩
            PostProcessDFS(v)

PostProcessDFS(v):
    v.status ← Active
    for each edge v→w
        if w.status = New
            PostProcessDFS(w)
        else if w.status = Active
            fail gracefully
    v.status ← Finished
    Process(v)
```

If $G$ is known to be a dag, plain marks suffice, and this is just DFSAll with PostVisit renamed Process (the book's PostProcessDag, whose wrapper should call PostProcessDagDFS$(v)$, not $(s)$). The book abbreviates it as an idiom:

```text
PostProcessDag(G):
    for all vertices v in postorder
        Process(v)
```

For example, TopologicalSort becomes: $\mathit{clock} \leftarrow V$; for all vertices $v$ in postorder, $S[\mathit{clock}] \leftarrow v$ and $\mathit{clock} \leftarrow \mathit{clock} - 1$; return $S[1\,..\,V]$.

To process a dag in **forward** topological order, record the order in an array and loop over it, or run the postorder idiom on the **reversal** $\textsf{rev}(G)$, which replaces every edge $v\to w$ by $w\to v$ and can be built in $O(V+E)$ time. Reversing a dag gives a dag, its sources are $G$'s sinks and vice versa, and its topological orders are exactly the reversals of $G$'s.

> [!trap] Topological-sort traps
> - **Preorder is not a topological order**, read forward or backward. For the dag $a\to b$, $a\to c$, $b\to d$, $c\to d$, $d\to e$, $f\to c$ searched in alphabetical order, the preorder $a\,b\,d\,e\,c\,f$ puts $c$ before $f$ although $f\to c$, and its reversal puts $e$ before $d$ although $d\to e$. Only **decreasing finishing time** works.
> - Increasing postorder is the **reverse** topological order: sinks first. That is the order in which a dynamic program evaluates (§6.4).
> - A graph with a cycle has no topological order; an algorithm that sorts must notice (the "fail gracefully" line).

Concept page: [[concepts/topological-sort]].

## 6.4 Memoization and dynamic programming

Recall the **dependency graph** of a recurrence ([[2-algorithms/05-basic-graph-algorithms#53-representations-and-examples|§5.3]]; the dependencies of [[2-algorithms/03-dynamic-programming#34-the-pattern-smart-recursion|§3.4]]): one vertex per subproblem, and in this chapter an edge $x\to y$ when evaluating $x$ needs the value of $y$. It must be a dag, or the plain recursion would never halt.

> [!key] Memoization is depth-first search; dynamic programming is postorder
> Evaluating a recurrence with memoization **is** a depth-first search of its dependency dag: a subproblem is "marked" once its value is stored, the first recursive call into it is a tree edge, a later look-up is an edge to a finished vertex, and a value is finalized exactly when its call finishes. Dynamic programming evaluates the subproblems in **postorder** of the dependency dag — a **reverse topological order**, every subproblem after all the subproblems it depends on. An evaluation order in the sense of Chapter 3 is exactly a reverse topological order of the dependency dag.

The book's side-by-side versions (its Figures 6.10 and 6.11):

```text
Memoize(x):
    if value[x] is undefined
        initialize value[x]
        for all subproblems y of x
            Memoize(y)
            update value[x] based on value[y]
        finalize value[x]

DynamicProgramming(G):
    for all subproblems x in postorder
        initialize value[x]
        for all subproblems y of x
            update value[x] based on value[y]
        finalize value[x]
```

Two differences from topological sort, both minor. The dependency graph is **implicit** — encoded by the recurrence rather than stored — which is harmless as long as the subproblems a subproblem depends on can be listed in $O(1)$ time each. And it is usually **highly structured**, so nested loops can hard-wire a reverse topological order instead of computing one at run time. For edit distance ([[2-algorithms/03-dynamic-programming#37-edit-distance|§3.7]]) the dependency dag is a grid with diagonals, $(i,j)\to(i,j-1), (i-1,j), (i-1,j-1)$, and row-major order is a reverse topological order; a memoized $\textsf{Edit}(m,n)$ that recurses in the order $(i,j-1), (i-1,j), (i-1,j-1)$ finalizes the entries in exactly the postorder of a depth-first search of that grid from $(m,n)$. For optimal binary search trees ([[2-algorithms/03-dynamic-programming#39-optimal-binary-search-trees|§3.9]]) every entry depends on entries to its left in its row and below it in its column.

> [!warning] Which way do the dependency edges point?
> Chapter 6 points the edge from a subproblem to the subproblems it **needs**, so the evaluation order is a **reverse** topological order (postorder). Chapter 5 of the book (its Figures 5.6 and 5.7) draws the same graph with every edge reversed, from the needed subproblem to the one that needs it; with that convention the evaluation order is a topological order. (The book's own Figure 6.12, the edit-distance dag of this chapter, reuses the picture of Figure 5.7 unchanged, so its arrows still point Chapter 5's way.) Either is fine on an exam, as long as you say which one you use.

### Dynamic programming in dags

Conversely, depth-first search turns a recursion over an *unstructured* dag into a dynamic program. The model problem: given a dag $G$ with edge weights $\ell(u\to v)$, of any sign, and two vertices $s$ and $t$, find the largest total weight of a path from $s$ to $t$. In general directed graphs this **longest path problem** is NP-hard (by a reduction from the traveling salesman problem, Chapter 12 of the book); in a dag it takes linear time.

> [!definition] Function — $\textsf{LLP}(v)$
> For every vertex $v$, $\textsf{LLP}(v)$ is the Length of the Longest Path from $v$ to $t$ in $G$, and $-\infty$ if $v$ cannot reach $t$. We need $\textsf{LLP}(s)$.

$$
\textsf{LLP}(v) = \begin{cases} 0 & \text{if } v = t\\ \max\{\ell(v\to w) + \textsf{LLP}(w) \mid v\to w \in E\} & \text{otherwise}\end{cases}\qquad\text{with } \max\varnothing = -\infty
$$
so a sink other than $t$ gets $-\infty$.

- **Memoization:** a field $v.\mathit{LLP}$ in every vertex (or an array indexed by the vertices).
- **Dependencies:** $\textsf{LLP}(v)$ reads $\textsf{LLP}(w)$ exactly for the edges $v\to w$ — the dependency graph **is $G$ itself**.
- **Evaluation order:** postorder of a depth-first search of $G$ (reverse topological order), or memoized recursion from $s$, which performs that search.
- **Time:** $O(1 + \text{out-degree of } v)$ for each vertex $v$, so $O(V+E)$ in all.

```text
LongestPath(v, t):
    if v = t
        return 0
    if v.LLP is undefined
        v.LLP ← −∞
        for each edge v→w
            v.LLP ← max{v.LLP, ℓ(v→w) + LongestPath(w, t)}
    return v.LLP                    ⟨⟨outside the if⟩⟩
```

```text
LongestPath(s, t):
    for each node v in postorder
        if v = t
            v.LLP ← 0
        else
            v.LLP ← −∞
            for each edge v→w
                v.LLP ← max{v.LLP, ℓ(v→w) + w.LLP}
    return s.LLP
```

The two are the same depth-first search — the recursion in the first and the loop in the second — and choosing one is a matter of convenience. (The book indents the last line of the memoized version into the `if`, so a second call on an already evaluated vertex would return nothing — for example the second call on $c$ in the diamond $s\to a\to c$, $s\to b\to c$, $c\to t$.)

<!-- fig:a06-longest-path -->
<figure class="cs-fig"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 610 212" width="610" height="212" role="img" style="font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-size:14px"><title>seven-vertex weighted dag drawn on a line in topological order with longest-path values</title><defs><marker id="ARR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs><rect x="47" y="176" width="38" height="22" rx="4" fill="var(--accent)" fill-opacity="0.1" stroke="currentColor" stroke-width="1.1"/><text x="66" y="187.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">13</text><rect x="131" y="176" width="38" height="22" rx="4" fill="var(--accent)" fill-opacity="0.1" stroke="currentColor" stroke-width="1.1"/><text x="150" y="187.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">11</text><rect x="215" y="176" width="38" height="22" rx="4" fill="var(--accent)" fill-opacity="0.1" stroke="currentColor" stroke-width="1.1"/><text x="234" y="187.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">−∞</text><rect x="299" y="176" width="38" height="22" rx="4" fill="var(--accent)" fill-opacity="0.1" stroke="currentColor" stroke-width="1.1"/><text x="318" y="187.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">7</text><rect x="383" y="176" width="38" height="22" rx="4" fill="var(--accent)" fill-opacity="0.1" stroke="currentColor" stroke-width="1.1"/><text x="402" y="187.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">6</text><rect x="467" y="176" width="38" height="22" rx="4" fill="var(--accent)" fill-opacity="0.1" stroke="currentColor" stroke-width="1.1"/><text x="486" y="187.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">4</text><rect x="551" y="176" width="38" height="22" rx="4" fill="var(--accent)" fill-opacity="0.1" stroke="currentColor" stroke-width="1.1"/><text x="570" y="187.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">0</text><text x="4" y="187.5" text-anchor="start" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">LLP</text><path d="M83,100 L130.5,100" fill="none" stroke="var(--accent)" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="108" y="90" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">2</text><path d="M80.4,109.1 Q192,180 301.5,110.5" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="192" y="154.6" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">5</text><path d="M164.1,90.6 Q234,44 301.8,89.2" fill="none" stroke="var(--accent)" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="234" y="57.3" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">4</text><path d="M163.5,89.7 Q276,4 386.5,88.2" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="276" y="36.8" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">3</text><path d="M167,100 L214.5,100" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="192" y="110" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">7</text><path d="M335,100 L382.5,100" fill="none" stroke="var(--accent)" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="360" y="90" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">1</text><path d="M332.1,109.4 Q402,156 469.8,110.8" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="402" y="142.7" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">2</text><path d="M419,100 L466.5,100" fill="none" stroke="var(--accent)" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="444" y="90" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">2</text><path d="M416.1,90.6 Q486,44 553.8,89.2" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="486" y="57.3" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">5</text><path d="M503,100 L550.5,100" fill="none" stroke="var(--accent)" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="528" y="90" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">4</text><circle cx="66" cy="100" r="17" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="66" y="101" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">s</text><circle cx="150" cy="100" r="17" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="150" y="101" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">a</text><circle cx="234" cy="100" r="17" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="234" y="101" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">x</text><circle cx="318" cy="100" r="17" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="318" y="101" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">b</text><circle cx="402" cy="100" r="17" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="402" y="101" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">c</text><circle cx="486" cy="100" r="17" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="486" y="101" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">d</text><circle cx="570" cy="100" r="17" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="570" y="101" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">t</text></svg><figcaption><strong>A weighted dag in topological order, with LLP(<i>v</i>) = length of the longest path from <i>v</i> to <i>t</i>.</strong> The order <i>s a x b c d t</i> is the reverse of the postorder <i>t d c b x a s</i> of DFS(<i>s</i>) with the edges taken in the order <i>s</i>: <i>a, b</i>; <i>a</i>: <i>b, c, x</i>; <i>b</i>: <i>c, d</i>; <i>c</i>: <i>d, t</i>, so every edge points right. The values are computed right to left (postorder); <i>x</i> cannot reach <i>t</i>, so LLP(<i>x</i>) = −∞. The longest path, in color, is <i>s a b c d t</i> of length 13; always taking the heaviest edge gives <i>s b d t</i> of length 11.</figcaption></figure>

> [!example] Example — the dag in the figure
> In postorder: $\textsf{LLP}(t) = 0$, $\textsf{LLP}(d) = 4 + 0 = 4$, $\textsf{LLP}(c) = \max\{2 + 4,\ 5 + 0\} = 6$, $\textsf{LLP}(b) = \max\{1 + 6,\ 2 + 4\} = 7$, $\textsf{LLP}(x) = -\infty$ ($x$ is a sink other than $t$), $\textsf{LLP}(a) = \max\{4 + 7,\ 3 + 6,\ 7 - \infty\} = 11$ and $\textsf{LLP}(s) = \max\{2 + 11,\ 5 + 7\} = 13$. The same dynamic program with $\min$ (and $\min\varnothing = +\infty$) finds the **shortest** path, $s\to a\to c\to t$ of length 10.

> [!key] Paths in dags are dynamic programs
> Almost every dynamic program that chooses an optimal **sequence** of decisions is a longest or shortest path in the dependency dag of its recurrence, possibly with weights on vertices or edges: text segmentation, subset sum, longest increasing subsequence, edit distance. For example, the edit distance of $A[1\,..\,m]$ and $B[1\,..\,n]$ is the length of the shortest path from $(m, n)$ to $(0, 0)$ in the grid dag with edges $(i,j)\to(i,j-1)$ and $(i,j)\to(i-1,j)$ of weight 1 and diagonal edges $(i,j)\to(i-1,j-1)$ of weight $[A[i] \ne B[j]]$. "Tree-shaped" dynamic programs — optimal binary search trees, independent sets in trees — combine several subproblems at once and are **not** paths in a dag.

> [!recipe] Recipe — a problem that is a path in a dag
> 1. **Build the graph** from the input: its vertices, its directed edges and their weights, as explicit functions of the input, and say why it is acyclic (typically, every edge goes from a smaller to a larger index).
> 2. **Name the path problem**: "the answer is the length of the longest (shortest) path from … to … in this dag", and say why paths correspond to the objects being optimized.
> 3. **Solve it** by the dynamic program above: $\textsf{LLP}$ in postorder, $O(V+E)$ time — a standard algorithm that can be cited.
> 4. **State the time in the input's parameters**: the dag for an array of length $n$ may have $\Theta(n^2)$ edges.

Concept pages: [[concepts/dynamic-programming-on-dags]], [[concepts/dynamic-programming]], [[concepts/memoization]].

## 6.5 Strong connectivity

> [!definition] Definition — strong components
> Vertices $u$ and $v$ of a directed graph are **strongly connected** if $u$ can reach $v$ and $v$ can reach $u$. This is an equivalence relation (reflexive because $v\in\textsf{reach}(v)$, symmetric by definition, transitive by concatenating paths), and its equivalence classes are the **strong components** (strongly connected components) of $G$ — equivalently, its maximal strongly connected subgraphs. $G$ is **strongly connected** if it has exactly one strong component; at the other extreme, a graph without loops is a dag if and only if every strong component is a single vertex.

> [!definition] Definition — the strong component graph
> $\textsf{scc}(G)$ is obtained from $G$ by contracting each strong component to a single vertex and collapsing parallel edges; edges inside a component disappear. It is also called the meta-graph or the condensation of $G$.

> [!key] The strong component graph is a dag
> $\textsf{scc}(G)$ is acyclic for every directed graph $G$. Moreover, $u$ can reach $v$ in $G$ if and only if the component of $u$ can reach the component of $v$ in $\textsf{scc}(G)$.

A directed cycle $C_1\to C_2\to\cdots\to C_k\to C_1$ of components would let every vertex of every $C_i$ reach every other one, so they would all be a single component. Every directed graph is therefore a dag of strongly connected pieces, and a dag can be ordered topologically: the vertices of $G$ can be ordered so that every edge pointing backward joins two vertices of the same strong component. (The book writes "two edges".)

<!-- fig:a06-scc -->
<figure class="cs-fig"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 372" width="640" height="372" role="img" style="font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-size:14px"><title>the sixteen-vertex graph with its five strong components shaded, and the five-vertex component dag</title><defs><marker id="ARR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs><g opacity="0.16"><path d="M44,44 L136,44 M136,44 L136,136 M136,136 L228,136" fill="var(--accent)" stroke="var(--accent)" stroke-width="54" stroke-linecap="round" stroke-linejoin="round"/></g><g opacity="0.16"><path d="M228,44 L320,44 M320,44 L320,136 M320,136 L320,228 M228,228 L320,228 M228,228 L228,320" fill="var(--accent2)" stroke="var(--accent2)" stroke-width="54" stroke-linecap="round" stroke-linejoin="round"/></g><circle cx="44" cy="136" r="27" fill="var(--muted)" fill-opacity="0.16" stroke="none"/><g opacity="0.16"><path d="M44,228 L136,228 M44,228 L44,320 M136,228 L136,320 M44,320 L136,320 M44,228 h92 v92 h-92 z" fill="var(--hi)" stroke="var(--hi)" stroke-width="54" stroke-linecap="round" stroke-linejoin="round"/></g><circle cx="320" cy="320" r="27" fill="var(--muted)" fill-opacity="0.16" stroke="none"/><rect x="385.0" y="164" width="46" height="44" rx="21" fill="var(--muted)" fill-opacity="0.16" stroke="none"/><rect x="452.0" y="70" width="84" height="44" rx="21" fill="var(--accent)" fill-opacity="0.16" stroke="none"/><rect x="452.0" y="258" width="84" height="44" rx="21" fill="var(--hi)" fill-opacity="0.16" stroke="none"/><rect x="539.0" y="164" width="102" height="44" rx="21" fill="var(--accent2)" fill-opacity="0.16" stroke="none"/><rect x="567.0" y="296" width="46" height="44" rx="21" fill="var(--muted)" fill-opacity="0.16" stroke="none"/><text x="500" y="18" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">scc(G)</text><path d="M60,44 L117.5,44" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M136,60 L136,117.5" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M239.3,55.3 L306.9,122.9" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M304,44 L246.5,44" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M60,136 L117.5,136" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)" stroke-dasharray="5 3"/><path d="M44,152 L44,209.5" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)" stroke-dasharray="5 3"/><path d="M152,136 L209.5,136" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M150.3,143.2 L303.5,219.7" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)" stroke-dasharray="5 3"/><path d="M214.6,127.2 Q141.4,79.3 61.4,50.3" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M228,120 L228,62.5" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)" stroke-dasharray="5 3"/><path d="M228,152 L228,209.5" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)" stroke-dasharray="5 3"/><path d="M320,120 L320,62.5" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M320,152 L320,209.5" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M55.3,239.3 L122.9,306.9" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M152,228 L209.5,228" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)" stroke-dasharray="5 3"/><path d="M124.7,239.3 L57.1,306.9" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M239.3,216.7 L306.9,149.1" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M244,228 L301.5,228" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M308.7,239.3 L241.1,306.9" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M320,244 L320,301.5" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)" stroke-dasharray="5 3"/><path d="M44,304 L44,246.5" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M136,304 L136,246.5" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M152,320 L209.5,320" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)" stroke-dasharray="5 3"/><path d="M228,304 L228,246.5" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M419.5,173.5 L476.8,110.8" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M419.5,198.5 L476.8,261.2" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M511.4,109 L570.9,167.3" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M511.4,263 L570.9,204.7" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M590,203 L590,298.5" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><circle cx="44" cy="44" r="16" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="44" y="45" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">a</text><circle cx="136" cy="44" r="16" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="136" y="45" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">b</text><circle cx="228" cy="44" r="16" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="228" y="45" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">c</text><circle cx="320" cy="44" r="16" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="320" y="45" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">d</text><circle cx="44" cy="136" r="16" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="44" y="137" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">e</text><circle cx="136" cy="136" r="16" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="136" y="137" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">f</text><circle cx="228" cy="136" r="16" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="228" y="137" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">g</text><circle cx="320" cy="136" r="16" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="320" y="137" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">h</text><circle cx="44" cy="228" r="16" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="44" y="229" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">i</text><circle cx="136" cy="228" r="16" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="136" y="229" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">j</text><circle cx="228" cy="228" r="16" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="228" y="229" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">k</text><circle cx="320" cy="228" r="16" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="320" y="229" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">l</text><circle cx="44" cy="320" r="16" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="44" y="321" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">m</text><circle cx="136" cy="320" r="16" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="136" y="321" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n</text><circle cx="228" cy="320" r="16" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="228" y="321" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">o</text><circle cx="320" cy="320" r="16" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="320" y="321" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">p</text><circle cx="408" cy="186" r="17" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="408" y="187" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">e</text><rect x="457" y="75" width="74" height="34" rx="17" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="494" y="93" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">a b f g</text><rect x="457" y="263" width="74" height="34" rx="17" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="494" y="281" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">i j m n</text><rect x="544" y="169" width="92" height="34" rx="17" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="590" y="187" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">c d h k l o</text><circle cx="590" cy="318" r="17" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="590" y="319" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">p</text></svg><figcaption><strong>The strong components of the book’s example graph, and its strong component graph.</strong> Left: the five components {<i>a, b, f, g</i>}, {<i>c, d, h, k, l, o</i>}, {<i>e</i>}, {<i>i, j, m, n</i>} and {<i>p</i>}; dashed edges join different components. Right: contracting each component to a vertex and collapsing parallel edges gives scc(<i>G</i>), a dag with source {<i>e</i>} and sink {<i>p</i>}.</figcaption></figure>

**One component.** The strong component of a single vertex $v$ is $\textsf{reach}(v) \cap \textsf{reach}^{-1}(v)$, where $\textsf{reach}^{-1}(v) = \{u \mid v\in\textsf{reach}(u)\}$ is computed by a whatever-first search of $\textsf{rev}(G)$: $O(V+E)$ time. In particular, $G$ is strongly connected if and only if one search of $G$ and one search of $\textsf{rev}(G)$, from the same arbitrary vertex, both reach every vertex — $O(V+E)$ time.

**All components.** Repeating this from every vertex not yet in a component takes $O(VE)$ time: there can be $V$ components, and each costs $O(E)$ to find, even when the graph is a dag. Yet deciding whether **every** component is a single vertex — whether $G$ is a dag — takes only $O(V+E)$. The next section closes the gap.

Concept page: [[concepts/strongly-connected-components]].

## 6.6 Strong components in linear time

Every linear-time algorithm rests on one observation about an arbitrary depth-first traversal.

> [!key] Lemma 6.2
> Fix any depth-first traversal of any directed graph $G$. Each strong component $C$ of $G$ contains exactly one vertex that does not have a parent in $C$ (its parent lies in another component, or it has no parent).

> [!proof]- Proof (click to expand)
> First, any path between two vertices of $C$ stays inside $C$: every vertex on it can reach the path's end, hence all of $C$, and can be reached from its start, hence from all of $C$.
>
> Let $v$ be the vertex of $C$ that starts first. If $v$ has a parent, the parent started even earlier, so it is not in $C$. For any other $w\in C$: just before DFS$(v)$ is called, every vertex of $C$ is new, and a path from $v$ to $w$ inside $C$ is a path of new vertices, so by Lemma 6.1(d) $w$ is a descendant of $v$. The tree path from $v$ to $w$ is a path between two vertices of $C$, so it lies in $C$; in particular $\mathit{parent}(w)\in C$.

So every strong component is a **connected subtree** of the depth-first forest. Its top vertex, the one that starts first — also the lowest common ancestor of the component — is called the **root** of the component. In the traversal of the first figure the roots are $a$, $c$, $p$, $e$ and $i$.

All the algorithms follow one outline. Call $C$ a **sink component** if it is a sink of $\textsf{scc}(G)$; equivalently, $\textsf{reach}(v) = C$ for every $v \in C$. A search from any vertex of a sink component finds exactly that component; deleting it leaves a graph with the same other components; repeat:

```text
StrongComponents(G):
    count ← 0
    while G is non-empty
        C ← ∅
        count ← count + 1
        v ← any vertex in a sink component of G       ⟨⟨Magic!⟩⟩
        for all vertices w in reach(v)
            w.label ← count
            add w to C
        remove C and its incoming edges from G
```

The whole difficulty is the magic line: finding a vertex of a sink component.

### Kosaraju and Sharir's algorithm

Finding a vertex of a **source** component is easy.

> [!key] Lemma 6.3
> The last vertex in any postordering of $G$ lies in a source component of $G$.

> [!proof]- Proof (click to expand)
> Let $v$ finish last. Then DFS$(v)$ is the last call made by the wrapper, $v$ is a root of the forest, and $v$ is the root of its component $C$. Every vertex $x$ with $x.\mathit{post} > v.\mathit{pre}$ is a descendant of $v$: it cannot have been active when DFS$(v)$ was called (it would be an ancestor of the root $v$), so it started after $v$, during the last top-level call. Suppose some edge $x\to y$ has $x\notin C$ and $y\in C$. By Lemma 6.2, $y$ is a descendant of $v$ (possibly $v$ itself), so $v.\mathit{pre} \le y.\mathit{pre}$; the edge $x\to y$ gives $y.\mathit{pre} < x.\mathit{post}$; so $x.\mathit{post} > v.\mathit{pre}$ and $x$ is a descendant of $v$. Then $v$ reaches $x$ along tree edges, and $x$ reaches $v$ through $y$ — so $x\in C$, a contradiction.

The graphs $G$ and $\textsf{rev}(G)$ have the same strong components, and $\textsf{rev}(\textsf{scc}(G)) = \textsf{scc}(\textsf{rev}(G))$. So the last vertex in a postordering of $\textsf{rev}(G)$ lies in a source component of $\textsf{rev}(G)$ — a **sink component of $G$**, which is exactly what the magic line needs. More is true: if $G$ has an edge from a component $C$ to a component $C'$, then in the search of $\textsf{rev}(G)$ some vertex of $C'$ finishes after every vertex of $C$. Hence, if the vertices are taken in **reverse postorder of $\textsf{rev}(G)$**, the first vertex not yet labeled always lies in a sink component of the graph of unlabeled vertices, and a search of $G$ from it that ignores labeled vertices labels exactly its component.

The **Kosaraju–Sharir algorithm** (Kosaraju 1978, unpublished; Sharir 1981) has two phases: a depth-first search of $\textsf{rev}(G)$ that pushes each vertex on a stack when it finishes, then searches of $G$ from the vertices in the order they are popped. It labels each vertex with the root of its component — the vertex from which the second phase found it.

```text
KosarajuSharir(G):
    S ← new empty stack
    for all vertices v
        unmark v
        v.root ← None
    ⟨⟨Phase 1: push in postorder in rev(G)⟩⟩
    for all vertices v
        if v is unmarked
            PushPostRevDFS(v, S)
    ⟨⟨Phase 2: DFS again in stack order⟩⟩
    while S is non-empty
        v ← Pop(S)
        if v.root = None
            LabelOneDFS(v, v)

PushPostRevDFS(v, S):
    mark v
    for each edge u→v                 ⟨⟨Reversed!⟩⟩
        if u is unmarked
            PushPostRevDFS(u, S)
    Push(v, S)

LabelOneDFS(v, r):
    v.root ← r
    for each edge v→w
        if w.root = None
            LabelOneDFS(w, r)
```

Each phase is one traversal, so the algorithm runs in $O(V+E)$ time; with minor changes it also builds $\textsf{scc}(G)$ in $O(V+E)$ time. (The second phase only needs reachability, so it can be any whatever-first search.)

> [!example] Example — the book's graph (its Figure 6.17)
> Phase 1, a depth-first search of $\textsf{rev}(G)$ with every choice in alphabetical order, finishes the vertices in the order $b\,e\,f\,g\,a\,m\,i\,n\,j\,l\,o\,k\,h\,d\,c\,p$. Phase 2 pops them in the reverse order $p\,c\,d\,h\,k\,o\,l\,j\,n\,i\,m\,a\,g\,f\,e\,b$; the vertices still unlabeled when popped are $p, c, j, a, e$, and the searches from them label
>
> | root | $p$ | $c$ | $j$ | $a$ | $e$ |
> |---|---|---|---|---|---|
> | component | $\{p\}$ | $\{c, d, h, k, l, o\}$ | $\{i, j, m, n\}$ | $\{a, b, f, g\}$ | $\{e\}$ |
>
> The components come out **sinks first** — a reverse topological order of $\textsf{scc}(G)$, as always with this algorithm.

> [!trap] Postorder of $G$ is not reverse postorder of $\textsf{rev}(G)$
> The first vertex to finish in a search of $G$ need not lie in a sink component. In $G$: $a\to b$, $b\to a$, $a\to c$, a search from $a$ that tries $b$ first finishes $b$ first, but $b$'s component $\{a, b\}$ has the edge $a\to c$ leaving it. Only the **last** vertex to finish is guaranteed (Lemma 6.3), and it is in a **source** component. So the two phases must run on different graphs: phase 1 on $\textsf{rev}(G)$ and phase 2 on $G$ — or, symmetrically, phase 1 on $G$ and phase 2 on $\textsf{rev}(G)$.

### Tarjan's algorithm

An earlier algorithm (Tarjan, 1972), subtler, and marked ♥ (advanced) in the book, does everything in a **single** depth-first search. For each vertex $v$ let $\textsf{low}(v)$ be the smallest starting time among the vertices reachable from $v$ by a path of tree edges followed by **at most one** non-tree edge; so $\textsf{low}(v) \le v.\mathit{pre}$.

> [!key] Lemma 6.4
> A vertex $v$ is the root of a sink component of $G$ if and only if $\textsf{low}(v) = v.\mathit{pre}$ and $\textsf{low}(w) < w.\mathit{pre}$ for every proper descendant $w$ of $v$.

> [!proof]- Proof (click to expand)
> If $\textsf{low}(v) = v.\mathit{pre}$, no edge leads from a descendant of $v$ to a vertex that started before $v$; and no edge can lead from a descendant to a non-descendant that starts after $v$ (it would be marked before the descendant finished, so it would start while $v$ is active, making it a descendant). So $v$ reaches only its descendants, and $v$ is the root of its component. If moreover every proper descendant $w$ has $\textsf{low}(w) < w.\mathit{pre}$, then $w$ can reach a descendant of $v$ that started earlier than $w$; by induction on starting times every descendant reaches $v$. So the descendants of $v$ form its component $C$, and $C$ is a sink because $v$ reaches nothing outside it.
>
> Conversely, if $v$ is the root of a sink component $C$, then $v$ reaches exactly $C$, which consists of descendants of $v$ (Lemma 6.2), so the descendants of $v$ are exactly $C$ and $\textsf{low}(v) = v.\mathit{pre}$. A proper descendant $w$ with $\textsf{low}(w) = w.\mathit{pre}$ would be another root of $C$, by the first part — impossible.

Computing $\textsf{low}$ is one depth-first search (the book's FindLow, whose wrapper is DFSAll with the clock set to 0 — the book prints its second loop indented inside the first; here the clock counts starting times only, $1, \ldots, V$, which is all the comparisons need):

```text
FindLowDFS(v):
    mark v
    clock ← clock + 1
    v.pre ← clock
    v.low ← v.pre
    for each edge v→w
        if w is unmarked
            FindLowDFS(w)
            v.low ← min{v.low, w.low}
        else
            v.low ← min{v.low, w.pre}
```

Finding a sink component this way and deleting it, then repeating, could take $V$ rounds and $O(VE)$ time. Tarjan's algorithm avoids the repetition with an **auxiliary stack** of vertices, separate from the recursion stack: push every vertex when it starts; when a vertex $v$ finishes with $v.\mathit{low} = v.\mathit{pre}$, then $v$ is the root of a sink component $C$ of the graph that remains, the vertices of $C$ are on top of the auxiliary stack, and $v$ is the deepest of them — so pop down to $v$ and label what was popped. Instead of deleting $C$ and starting over, the algorithm simply **ignores labeled vertices** from then on, which makes it behave exactly as if they had been deleted:

```text
Tarjan(G):
    clock ← 0
    S ← new empty stack
    for all vertices v
        unmark v
        v.root ← None
    for all vertices v
        if v is unmarked
            TarjanDFS(v)

TarjanDFS(v):
    mark v
    clock ← clock + 1
    v.pre ← clock
    v.low ← v.pre
    Push(S, v)
    for each edge v→w
        if w is unmarked
            TarjanDFS(w)
            v.low ← min{v.low, w.low}
        else if w.root = None
            v.low ← min{v.low, w.pre}
    if v.low = v.pre
        repeat
            w ← Pop(S)
            w.root ← v
        until w = v
```

Each vertex is pushed and popped once, and the rest is one depth-first search: $O(V+E)$ time. Like Kosaraju–Sharir, Tarjan's algorithm finds the components **sinks first**. (The book's introduction to the algorithm says it finds a *source* component first; Lemma 6.4 and the algorithm find sink components.)

> [!example] Example — Tarjan on the traversal of the first figure
> With the starting times of the figure (only comparisons matter), the values of $\textsf{low}$ computed by TarjanDFS are
>
> | $v$ | $a$ | $b$ | $f$ | $g$ | $c$ | $h$ | $d$ | $l$ | $o$ | $k$ | $p$ | $e$ | $i$ | $n$ | $j$ | $m$ |
> |---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
> | $v.\mathit{pre}$ | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 9 | 10 | 11 | 14 | 23 | 24 | 25 | 26 | 27 |
> | $v.\mathit{low}$ | 1 | 1 | 1 | 1 | 5 | 5 | 5 | 6 | 6 | 6 | 14 | 23 | 24 | 24 | 24 | 24 |
>
> The roots, where $\mathit{low} = \mathit{pre}$, are $a, c, p, e, i$; the components are popped in the order $\{p\}$, $\{c, d, h, k, l, o\}$, $\{a, b, f, g\}$, $\{i, j, m, n\}$, $\{e\}$. The test "$w.\mathit{root} = \textsf{None}$" matters: without it the cross edge $e\to f$ into the already labeled component of $a$ would give $e$ the value $\textsf{low}(e) = 3$, and $e$ would never be recognized as a root.

Concept page: [[concepts/strongly-connected-components]].

## The chapter's algorithms at a glance

| question | algorithm | time | section |
|---|---|---|---|
| which vertices can $s$ reach? | DFS$(s)$, or any whatever-first search | $O({V+E})$ | 6.0 |
| preorder, postorder, depth-first forest, edge classes | DFSAll with a clock | $O({V+E})$ | 6.1 |
| does $G$ have a directed cycle? | IsAcyclic: look for an edge into an active vertex | $O({V+E})$ | 6.2 |
| a topological order of a dag | reverse postorder (TopologicalSort) | $O({V+E})$ | 6.3 |
| longest or shortest path in a dag, any weights | dynamic programming in postorder ($\textsf{LLP}$) | $O({V+E})$ | 6.4 |
| longest path in a general directed graph | — (NP-hard) | | 6.4 |
| strong component of one vertex; is $G$ strongly connected? | $\textsf{reach}(v)\cap\textsf{reach}^{-1}(v)$ | $O({V+E})$ | 6.5 |
| all strong components, $\textsf{scc}(G)$ | Kosaraju–Sharir, or Tarjan | $O({V+E})$ | 6.6 |

## Summary

- DFS$(v)$ marks exactly $\textsf{reach}(v)$; DFSAll covers the whole graph in $O(V+E)$ time; with a clock it assigns starting and finishing times $1, \ldots, 2V$.
- Active intervals are nested or disjoint, nested exactly for ancestor and descendant. Lemma 6.1: $v$ becomes a descendant of $u$ if and only if, when DFS$(u)$ is called, $u$ reaches $v$ through new vertices.
- Edge $u\to v$: tree or forward if $u.\mathit{pre} < v.\mathit{pre} < v.\mathit{post} < u.\mathit{post}$, back if $v.\mathit{pre} < u.\mathit{pre} < u.\mathit{post} < v.\mathit{post}$, cross if $v.\mathit{post} < u.\mathit{pre}$; never $u.\mathit{post} < v.\mathit{pre}$.
- Cycle $\iff$ back edge $\iff$ some edge with $u.\mathit{post} < v.\mathit{post}$; IsAcyclic stops at the first edge into an active vertex.
- In a dag every edge has $u.\mathit{post} > v.\mathit{post}$, so reverse postorder is a topological order; postorder itself is the evaluation order of dynamic programming.
- Memoization is depth-first search of the dependency dag; longest (or shortest) paths in a dag take $O(V+E)$ time by $\textsf{LLP}(v) = \max_{v\to w}\{\ell(v\to w) + \textsf{LLP}(w)\}$ in postorder; longest paths in general graphs are NP-hard.
- Strong components contract to a dag $\textsf{scc}(G)$; each component is a subtree of any depth-first forest (Lemma 6.2); Kosaraju–Sharir (search $\textsf{rev}(G)$, then search $G$ in the reverse of that postorder) and Tarjan (one search, $\textsf{low}$ values, a stack) find them all in $O(V+E)$ time, sink components first.

> [!exam] On the exams
> Graph algorithms are part of the algorithms half of the course (Midterm 2 on November 9, and the final); the course website says which chapters each exam covers. Graph problems are graded by the course's **graph-reduction rubric** (10 points): 3 for **constructing the graph** — vertices, edges (−½ for forgetting to say "directed") and weights, all as explicit functions of the input; 3 for **relating the problem to a specific problem on that graph** — which problem (reachability, longest path in a dag, strong components…), from where to where, and why it answers the question; 2 for **applying the right algorithm as a black box** — −1 for a slower algorithm than necessary, −½ for a more specific one than necessary (such as DFS when any whatever-first search would do), −1 for re-explaining a standard algorithm instead of citing it; and 2 for the **time in the input's parameters**, not just the $V$ and $E$ of the constructed graph. Everything in the table above is a standard algorithm you may cite: DFSAll with pre/post times, cycle detection, topological sort, longest and shortest paths in a dag, strong components and $\textsf{scc}(G)$, each in $O(V+E)$ time. The classic mistakes: modifying a standard algorithm instead of modifying the graph; "try all paths with DFS and keep the best" (exponentially many paths); and applying the dag dynamic program to a graph that may have cycles — which is where $\textsf{scc}(G)$ comes in, to turn any directed graph into a dag. A dynamic program written out in full is still graded by the [[0-toolkit/06-how-exams-are-graded#12-dynamic-programming|dynamic programming rubric]]; see also [[0-toolkit/06-how-exams-are-graded|how exams are graded]].

### Sources for this page
Erickson, *Algorithms*, Chapter 6 (pp. 225–243; the exercises, pp. 244–256, are on the [[2-algorithms/06-depth-first-search-exercises|exercises page]]), summarized in our own words. The algorithms and lemmas follow the book, as does the pseudocode, with these corrections: the recursive call in TopSortDFS is on $w$, not $v$; the memoized LongestPath returns $v.\mathit{LLP}$ outside the `if`; PostProcess tests the status, and PostProcessDag calls PostProcessDagDFS$(v)$, not $(s)$; Tarjan's algorithm finds sink, not source, components first; a backward edge "joins two vertices", not "two edges"; the two loops of FindLow's wrapper are consecutive, not nested. The warning about the direction of dependency edges points out that Chapters 5 and 6 of the book use opposite conventions (and that the book's Figure 6.12 keeps Chapter 5's). The 16-vertex graph and dag, with all their pre/post times, orders and components, are the book's (Figures 6.4, 6.6, 6.8, 6.13, 6.17), reconstructed from its figures and recomputed; the proof of the cycle lemma in both directions, the weighted dag, the Tarjan table, the counterexamples in the traps, the edit-distance-as-shortest-path statement and the remark that every topological order is a reverse postorder are additions. CS/ECE 374 A (Fall 2026) standard rubrics for the grading notes. Every pseudocode block on this page is implemented and compared with brute force on random graphs, and every example, order and table is recomputed, by `tools/checks/a06.py`.
