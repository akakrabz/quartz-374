---
title: "Chapter 5 exercises — Basic Graph Algorithms"
description: "Solutions to Exercises 5.1–5.19 of Erickson's Algorithms: seven definitions of a tree, bipartite graphs, pecking orders, Euler tours, hypercubes, strong orientations, variants of whatever-first search, and nine puzzle and walk problems solved by graph reductions in the rubric's format."
tags: [exercises, algorithms, graphs, midterm-2]
---

*Solved exercises for [[2-algorithms/05-basic-graph-algorithms|Chapter 5]] · book pp. 207–216 · statements paraphrased; see the book for the originals*

These are Exercises 5.1–5.19: the graph-theory warm-ups (5.1–5.6), the traversal exercises (5.7–5.10) and the first nine reductions (5.11–5.19). Skipped: 5.10(e–f), which are marked ♥ (particularly challenging), and Exercises 5.20 onward (5.22(c), 5.24, 5.26(b), 5.27 and 5.28 are ♥ as well). Every reduction is written the way the graph-reduction rubric grades it ([[concepts/graph-reductions]], [[2-algorithms/05-basic-graph-algorithms#57-graph-reductions-flood-fill|§5.7]]): **the graph**, with its vertices and edges as explicit functions of the input and whether it is directed; **the problem** on that graph, from where to where, and why it answers the question; **the algorithm**, a standard one called as a black box — [[concepts/whatever-first-search|whatever-first search]] when reachability is enough, breadth-first search when the number of moves matters; and **the time**, in the input's parameters. As in the book, $V$ and $E$ denote both the vertex and edge sets and their sizes, $u\to v$ is a directed edge and $uv$ an undirected one ([[concepts/graphs]]). The puzzle of Exercise 5.18 has no solution as printed, and 5.19(b) says "both coins" where it means all three; both are pointed out where they occur. Write your own answer before opening a solution.

## Exercise 5.1 — Seven definitions of a tree

> [!question] Exercise 5.1 (book p. 207)
> Prove that the following definitions of a **tree** are equivalent, for a graph with $V$ vertices:
>
> 1. a connected acyclic graph;
> 2. one component of a forest (an acyclic graph);
> 3. a connected graph with at most $V-1$ edges;
> 4. a minimally connected graph: removing any edge disconnects it;
> 5. an acyclic graph with at least $V-1$ edges;
> 6. a maximally acyclic graph: adding an edge between any two (non-adjacent) vertices creates a cycle;
> 7. a graph with a unique path between each pair of vertices.

> [!hint]- Hint
> Add the edges one at a time to the graph with no edges and watch the number of components. Separately, ask when deleting a single edge disconnects its endpoints.

> [!solution]- Solution
> Two lemmas about an arbitrary graph $G$ with $V$ vertices, $E$ edges and $c$ components do all the work.
>
> **Lemma A.** An edge $uv$ lies on a cycle if and only if $u$ and $v$ are connected in $G - uv$. Consequently, deleting $uv$ splits a component exactly when $uv$ lies on no cycle.
>
> *Proof.* The rest of a cycle through $uv$ is a $u$–$v$ path that avoids $uv$; conversely, a $u$–$v$ path in $G - uv$ has at least two edges, and together with $uv$ it is a cycle. If $u$ and $v$ stay connected, every walk that used $uv$ can detour along such a path, so the components do not change; otherwise $u$ and $v$ end up in different components.
>
> **Lemma B.** $E\ge V - c$, with equality if and only if $G$ is acyclic.
>
> *Proof.* Insert the edges one at a time into the graph on the same vertices with no edges, which has $V$ components. An edge between two different components merges them; an edge inside one component changes nothing. Hence $c\ge V - E$, with equality exactly when every edge merges two components. An edge $uv$ inserted inside a component closes a cycle with the $u$–$v$ path that already exists; conversely, if $G$ has a cycle, the last of its edges to be inserted joins two vertices that the rest of the cycle already connects.
>
> **The equivalences.** Each definition is shown equivalent to (1).
>
> - **(1)⇔(2).** A component of an acyclic graph is connected and acyclic; a connected acyclic graph is a forest with one component.
> - **(1)⇔(3).** Connected means $c = 1$. If $G$ is also acyclic, Lemma B gives $E = V - 1$. Conversely, $E\le V - 1 = V - c$ forces equality in Lemma B, so $G$ is acyclic.
> - **(1)⇔(5).** Acyclic means $E = V - c$ (Lemma B). If $G$ is also connected, $E = V - 1$. Conversely, $E\ge V-1$ gives $V - c\ge V - 1$, so $c\le 1$: $G$ is connected.
> - **(1)⇔(4).** By Lemma A, removing an edge from a connected graph disconnects it if and only if the edge lies on no cycle. So (4) says: connected, and no edge lies on a cycle — that is, connected and acyclic.
> - **(1)⇔(6).** Lemma A applied to $G + uv$: adding a new edge $uv$ creates a cycle if and only if $u$ and $v$ are already connected. So (6) says: acyclic, and any two non-adjacent vertices are connected — that is, acyclic and connected.
> - **(1)⇔(7).** Unique paths imply connected, and acyclic: an edge $uv$ on a cycle gives two $u$–$v$ paths, the edge itself and the rest of the cycle. Conversely, let $G$ be connected and acyclic, and suppose $P\ne Q$ are two $u$–$v$ paths. Some edge $xy$ of $P$ is not on $Q$ (if every edge of $P$ were on the path $Q$, then $P$ would be the one $u$–$v$ path inside $Q$, namely $Q$). Say $P$ visits $x$ before $y$. Walking from $x$ back along $P$ to $u$, then along $Q$ to $v$, then back along $P$ to $y$ never uses the edge $xy$; so $x$ and $y$ are connected in $G - xy$, and $xy$ lies on a cycle by Lemma A — a contradiction.
>
> **Answer.** All seven are equivalent; Lemma A (an edge is on a cycle iff its endpoints stay connected without it) and Lemma B ($E\ge V - c$, with equality iff acyclic) prove every link.

## Exercise 5.2 — Two vertices of degree 1

> [!question] Exercise 5.2 (book p. 207)
> Prove that every connected acyclic graph with $n\ge 2$ vertices has at least two vertices of degree 1, using only the definitions of "connected" and "acyclic" — no properties of trees or leaves.

> [!hint]- Hint
> Look at the two ends of a longest path.

> [!solution]- Solution
> The graph is connected and has two vertices, so it has an edge, and there are paths with at least one edge. A finite graph has finitely many paths; let $P = v_0v_1\cdots v_k$ be one with the largest number of edges. Then $k\ge 1$, so $v_0\ne v_k$.
>
> $v_0$ is adjacent to $v_1$. Suppose $v_0$ had another neighbor $w\ne v_1$. If $w = v_i$ for some $i\ge 2$, then $v_0v_1\cdots v_iv_0$ is a cycle, contradicting acyclicity. Otherwise $w$ is not on $P$, and $wv_0v_1\cdots v_k$ is a path with $k+1$ edges, contradicting the choice of $P$. So $\deg(v_0) = 1$, and by the same argument $\deg(v_k) = 1$.
>
> **Answer.** Both ends of a longest path have degree 1.

## Exercise 5.3 — Bipartite graphs

> [!question] Exercise 5.3 (book p. 207)
> A graph is **bipartite** if its vertices can be split into two sets $L$ and $R$ so that every edge has one endpoint in $L$ and the other in $R$.
>
> (a) Prove that every tree is bipartite.
>
> (b) Prove that a graph is bipartite if and only if every cycle in it has an even number of edges.
>
> (c) Describe and analyze an efficient algorithm that decides whether a given undirected graph is bipartite.

### (a) Trees

> [!hint]- Hint
> Hang the tree from a root and color by depth.

> [!solution]- Solution
> Run whatever-first search from any vertex $r$ of the tree. Its parent edges form a spanning tree ([[2-algorithms/05-basic-graph-algorithms#55-whatever-first-search|Lemma 5.1]]), which has $V - 1$ edges, like the tree itself (Exercise 5.1); so every edge of the tree is a parent edge. Let $L$ be the vertices at even depth (number of parent edges up to $r$) and $R$ those at odd depth. A parent edge joins depths $d$ and $d+1$, so it has one endpoint on each side. (Part (b) also gives (a): a tree has no cycles at all.)
>
> **Answer.** Even depths on one side, odd depths on the other.

### (b) Bipartite means no odd cycles

> [!hint]- Hint
> For "if": color each vertex by the parity of its distance from a fixed vertex. An edge between two vertices of the same color produces a closed walk of odd length — and an odd closed walk contains an odd cycle.

> [!solution]- Solution
> **Only if.** Walking along a cycle $v_0v_1\cdots v_k$ with $v_k = v_0$, consecutive vertices lie on opposite sides; we return to the side we started on, so $k$ is even.
>
> **If.** It suffices to split each component, so assume $G$ is connected. Fix a vertex $r$, let $d(v)$ be the number of edges of a shortest path from $r$ to $v$, and put $L = \{v \mid d(v) \text{ even}\}$, $R = \{v \mid d(v)\text{ odd}\}$. Suppose an edge $uv$ had $d(u)\equiv d(v)\pmod 2$. A shortest $r$–$u$ path, the edge $uv$ and a shortest $v$–$r$ path form a closed walk of odd length $d(u) + 1 + d(v)$. That contradicts the assumption, by this lemma:
>
> **Lemma C.** Every closed walk of odd length contains a cycle of odd length.
>
> *Proof,* by induction on the length $\ell$ of the closed walk $w_0w_1\cdots w_\ell$, $w_\ell = w_0$. If no vertex repeats (other than $w_\ell = w_0$), the walk is a cycle: $\ell\ne 1$ because there are no loops, so $\ell\ge 3$. Otherwise $w_i = w_j$ for some $0\le i < j<\ell$ other than $i = 0, j = \ell$; cutting there gives two closed walks, of lengths $j - i$ and $\ell - (j - i)$, both shorter and positive. Their lengths add up to the odd number $\ell$, so one of them is odd and contains an odd cycle by induction.
>
> **Answer.** Bipartite $\iff$ no odd cycle; for "if", color by the parity of the distance from a fixed vertex in each component.

### (c) Testing bipartiteness

> [!hint]- Hint
> Any whatever-first search tree will do; you do not need shortest paths.

> [!solution]- Solution
> Run whatever-first search from every unmarked vertex in turn (the wrapper WFSAll of [[2-algorithms/05-basic-graph-algorithms#56-important-variants|§5.6]]), recording depths: the root of each search gets depth 0, and when a vertex $v$ is marked with parent $p$, set $\mathit{depth}(v) \leftarrow \mathit{depth}(p) + 1$. Then check every edge: if some edge $uv$ has $\mathit{depth}(u)\equiv\mathit{depth}(v)\pmod 2$, report "not bipartite"; otherwise report "bipartite", with $L$ and $R$ the vertices of even and odd depth.
>
> **Correctness.** If every edge passes, $L$ and $R$ are a valid split. If an edge $uv$ fails, the tree path from $u$ up to its root $r$ (length $\mathit{depth}(u)$), the tree path down from $r$ to $v$ (length $\mathit{depth}(v)$) and the edge $vu$ form a closed walk of odd length, which contains an odd cycle by Lemma C; by (b) the graph is not bipartite.
>
> **Time.** $O(V+E)$ for the searches plus $O(E)$ for the edge test.
>
> **Answer.** Two-color by depth parity in a whatever-first search forest and test every edge, in $O(V + E)$ time.

## Exercise 5.4 — Pecking orders

> [!question] Exercise 5.4 (book p. 208)
> In any pair of pigeons, exactly one pecks the other, always the same one; the pecking relation may contain cycles.
>
> (a) Prove that any finite set of pigeons can be lined up in a procession in which every pigeon pecks the pigeon just ahead of it.
>
> (b) The input is a directed graph with one vertex per pigeon and an edge $i\to j$ whenever pigeon $i$ pecks pigeon $j$. Describe and analyze an algorithm that computes such a procession.
>
> (c) Prove that for at least three pigeons, either the procession of (a) is unique, or there are three pigeons $i, j, k$ such that $i$ pecks $j$, $j$ pecks $k$ and $k$ pecks $i$.

In graph terms the pecking graph is a **tournament** (exactly one directed edge between any two vertices), and a procession $p_1, p_2, \dots, p_n$ with $p_{i+1}\to p_i$ for all $i$ is a directed Hamiltonian path $p_n\to p_{n-1}\to\cdots\to p_1$.

### (a) and (b) Building a procession

> [!hint]- Hint
> Add the pigeons one at a time. Where can a new pigeon squeeze into an existing procession?

> [!solution]- Solution
> **Insertion rule.** Given a procession $p_1, \dots, p_k$ of some of the pigeons and a new pigeon $x$, insert $x$ **just before the first $p_i$ that pecks $x$**, or at the end if no $p_i$ pecks $x$.
>
> This gives a procession. If $x$ goes before $p_i$, then $p_i$ pecks $x$; and if $i > 1$, then $p_{i-1}$ does not peck $x$ (it comes before the first one that does), so $x$ pecks $p_{i-1}$. If $x$ goes at the end, $p_k$ does not peck $x$, so $x$ pecks $p_k$. All other neighbors in the line are unchanged. Starting from the empty procession and inserting every pigeon proves (a) by induction.
>
> **Algorithm (b).** Keep the procession in a linked list and the pecking relation in an adjacency matrix (build one from adjacency lists in $O(n^2)$ time if necessary), so that "does $p$ peck $x$?" takes $O(1)$ time. Insert the pigeons one at a time with the rule; each insertion scans the list once, in $O(n)$ time.
>
> **Time.** $O(n^2)$, which is linear in the size of the input: a tournament has $n(n-1)/2$ edges.
>
> **Answer.** Insert each pigeon before the first pigeon that pecks it (or at the end): $O(n^2)$ time.

### (c) Unique, or a 3-cycle

> [!hint]- Hint
> First show that a tournament with a directed cycle has a directed cycle of length 3. Without cycles, where must the pigeon that pecks everybody stand?

> [!solution]- Solution
> Suppose no three pigeons peck each other in a cycle.
>
> **No cycles at all.** Suppose the pecking graph had a directed cycle, and take a shortest one, $v_1\to v_2\to\cdots\to v_k\to v_1$. Then $k\ge 3$ (two pigeons never peck each other mutually), and $k\ne 3$ by assumption, so $k\ge 4$. Look at $v_1$ and $v_3$. If $v_3$ pecks $v_1$, then $v_1\to v_2\to v_3\to v_1$ is a 3-cycle; if $v_1$ pecks $v_3$, then $v_1\to v_3\to\cdots\to v_k\to v_1$ is a shorter cycle. Both are impossible, so the graph is acyclic.
>
> **Every procession is the same.** Let $p_1, \dots, p_n$ be a procession. For $i < j$, pigeon $p_j$ pecks $p_i$: otherwise $p_i\to p_j$ and $p_j\to p_{j-1}\to\cdots\to p_i$ would close a cycle. So $p_i$ pecks exactly the $i - 1$ pigeons ahead of it, and its position is $1 + (\text{the number of pigeons it pecks})$ — a number that does not depend on the procession. Hence the procession is unique.
>
> **Answer.** Without a 3-cycle the pecking graph is acyclic, and every pigeon's place is forced: one plus the number of pigeons it pecks.

## Exercise 5.5 — Euler tours

> [!question] Exercise 5.5 (book p. 208)
> An **Euler tour** of a graph is a closed walk that traverses every edge exactly once.
>
> (a) Prove that if a connected graph has an Euler tour, every vertex has even degree.
>
> (b) Prove that if every vertex of a connected graph has even degree, the graph has an Euler tour.
>
> (c) Describe and analyze an algorithm that computes an Euler tour of a given graph, or correctly reports that none exists.

### (a) Necessity

> [!hint]- Hint
> Every time the tour passes through a vertex, it uses two of its edges.

> [!solution]- Solution
> Write the tour as $v_0e_1v_1e_2\cdots e_mv_m$ with $v_m = v_0$, and read it cyclically, so that each occurrence of a vertex among $v_1, \dots, v_m$ is entered by one edge $e_i$ and left by the next, $e_{i+1}$ (with $e_{m+1} = e_1$). These two edge ends are different (no loops), and since every edge appears exactly once on the tour, every end of an edge at $v$ is counted exactly once. So $\deg(v)$ is twice the number of times the tour passes through $v$. (In a connected graph with at least one edge every vertex lies on the tour; a graph with no edges has all degrees 0.)
>
> **Answer.** $\deg(v) = 2\cdot(\text{number of visits to } v)$, which is even.

### (b) Sufficiency

> [!hint]- Hint
> Take a longest walk that repeats no edge. If it is not closed, its last vertex has an unused edge; if it misses an edge, splice one in.

> [!solution]- Solution
> If the graph has no edges, the walk consisting of one vertex is an Euler tour. Otherwise, call a walk that repeats no edge a **trail**, and let $W$ be a trail with as many edges as possible (trails have at most $E$ edges).
>
> **$W$ is closed.** Suppose $W$ runs from $u$ to $v\ne u$. Each pass of $W$ through $v$ uses two edges at $v$ and the final arrival uses one, so $W$ uses an odd number of the edges at $v$. Since $\deg(v)$ is even, some edge $vw$ is unused, and $W$ followed by $vw$ is a longer trail — a contradiction.
>
> **$W$ uses every edge.** Suppose some edge is unused. Then some unused edge has an endpoint $u$ on $W$: either an endpoint of the unused edge is on $W$, or a path from a vertex of $W$ to that edge (the graph is connected) leaves the vertex set of $W$ along an edge that cannot belong to $W$. Rotate the closed trail $W$ so that it starts and ends at $u$, and append the unused edge at $u$: a longer trail — a contradiction.
>
> So $W$ is a closed walk through every edge exactly once.
>
> **Answer.** A longest trail is closed (even degrees) and uses every edge (connectivity), so it is an Euler tour.

### (c) Computing a tour

> [!hint]- Hint
> Turn the proof of (b) into an algorithm: walk along unused edges until you get stuck — which can only happen where you started — and splice in more closed walks from the vertices you have passed. Recursion does the splicing for you.

> [!solution]- Solution
> By (a) and (b), a tour exists exactly when every vertex has even degree and all edges lie in one component. The algorithm (Hierholzer's) checks the first condition directly and detects the second at the end.
>
> ```text
> EulerTour(G):
>     if some vertex has odd degree
>         return None
>     if G has no edges
>         return the one-vertex walk ⟨v⟩ for any vertex v
>     Tour ← the empty list
>     Walk(s) for any vertex s with an edge
>     if Tour has fewer than E + 1 entries     ⟨⟨edges in several components⟩⟩
>         return None
>     return Tour
>
> Walk(v):
>     while some edge vw is unused
>         mark vw used
>         Walk(w)
>     append v to Tour
> ```
>
> **Which edges get used.** A call $\textsf{Walk}(v)$ returns only when every edge at $v$ is used, and an edge is used only by a call at one endpoint that then calls the other. So every vertex of $s$'s component gets a call and every edge of that component gets used, and nothing else. Each call appends one entry, and there is one call for $s$ plus one per used edge; so $\mathit{Tour}$ has $E + 1$ entries exactly when all edges lie in $s$'s component.
>
> **Parity.** Call a moment *even* if every vertex has an even number of unused edges; the start is even. Suppose that at an even moment a call $\textsf{Walk}(v)$ marks an edge $vw$ and calls $\textsf{Walk}(w)$. The nested calls then follow unused edges along a walk $v\to w\to\cdots$; whenever its current end $x$ is not $v$, an odd number of the walk's edges touch $x$, so $x$ still has an odd — hence nonzero — number of unused edges. The first call that finds no unused edge is therefore at $v$, and it appends $v$; at that moment the walk is closed and the moment is even again. From then on, each call on the walk resumes its loop at an even moment, and any edge it takes starts the same argument over (induction on the number of unused edges), ending at an even moment again; so $\textsf{Walk}(w)$ also returns at an even moment. Hence **loops resume only at even moments, and if $\textsf{Walk}(v)$ takes an edge $vw$ at an even moment, the first entry appended inside $\textsf{Walk}(w)$ is $v$**; in particular the first entry of $\mathit{Tour}$ is $s$. (The condition matters: on a triangle $s, a, b$ where $\textsf{Walk}(s)$ takes $sa$ first, the call $\textsf{Walk}(b)$ made from $\textsf{Walk}(a)$ appends $s$ first, not $a$.)
>
> **The output is a closed walk through every edge once.** Consider the entry appended by $\textsf{Walk}(w)$, called from $\textsf{Walk}(v)$ through the edge $vw$. The next entry is $v$: either $v$'s loop ends and $\textsf{Walk}(v)$ appends $v$, or the loop, resuming at an even moment, calls $\textsf{Walk}(w')$, whose first entry is $v$. So consecutive entries are joined by the edge of the earlier entry's call; these edges are distinct and are all the used edges. The first entry is $s$, and the last is $s$ too ($\textsf{Walk}(s)$ returns last).
>
> **Time.** Keep a pointer into each adjacency list, and let the two records of an undirected edge share one "used" bit. The test "some edge $vw$ is unused" advances $v$'s pointer past used records, so every record is passed once: $O(V + E)$ time. (The recursion can be $E$ deep; an explicit stack avoids that in practice.)
>
> **Answer.** Check the degrees, run $\textsf{Walk}(s)$, and check that the tour has $E+1$ entries: $O(V + E)$ time.

## Exercise 5.6 — Hypercubes

> [!question] Exercise 5.6 (book p. 208)
> The **$d$-dimensional hypercube** $Q_d$ has the $2^d$ strings of $d$ bits as its vertices, two of them adjacent when they differ in exactly one bit.
>
> (a) A **Hamiltonian cycle** is a cycle that visits every vertex exactly once. Prove that $Q_d$ has a Hamiltonian cycle for every $d\ge 2$.
>
> (b) Which hypercubes have an Euler tour?

> [!hint]- Hint
> (a) Two copies of $Q_d$, one prefixed with 0 and one with 1, make $Q_{d+1}$: run through the first copy, cross over, and come back through the second copy in reverse. (b) What is the degree of every vertex?

> [!solution]- Solution
> **(a)** Induction on $d$. For $d = 2$: $00, 01, 11, 10$. If $c_1, c_2, \dots, c_N$ ($N = 2^d$) is a Hamiltonian cycle of $Q_d$, then
> $$
> 0c_1,\ 0c_2,\ \dots,\ 0c_N,\ 1c_N,\ 1c_{N-1},\ \dots,\ 1c_1
> $$
> is one of $Q_{d+1}$: it lists every $(d+1)$-bit string exactly once, consecutive strings within each half differ in one bit by assumption, and the two crossings $0c_N$–$1c_N$ and $1c_1$–$0c_1$ change only the first bit. (This is the **reflected Gray code**; for $d = 3$ it is $000, 001, 011, 010, 110, 111, 101, 100$.) The bound $d\ge 2$ is needed because $Q_1$, a single edge, has no cycle.
>
> **(b)** $Q_d$ is connected (change the bits one at a time) and every vertex has degree $d$. By Exercise 5.5, $Q_d$ has an Euler tour if and only if $d$ is even. ($Q_0$, a single vertex, has the empty tour.)
>
> **Answer.** (a) The reflected Gray code. (b) Exactly the hypercubes of even dimension.

## Exercise 5.7 — Strongly connected orientations

> [!question] Exercise 5.7 (book p. 209)
> Describe an algorithm that decides, given an undirected graph $G$, whether its edges can be directed so that the resulting directed graph is **strongly connected** (every vertex reachable from every other).

> [!hint]- Hint
> An edge whose removal disconnects the graph is hopeless. Otherwise, try depth-first search: point the tree edges down and every other edge up.

> [!solution]- Solution
> **Necessary: connected, and every edge on a cycle.** A disconnected graph has no strongly connected orientation. If an edge $uv$ lies on no cycle, then $u$ and $v$ are in different components of $G - uv$ (Exercise 5.1, Lemma A); orient it $u\to v$, say. A directed path from $v$ to $u$ would have to cross from $v$'s side to $u$'s side, and the only edge between them points the other way.
>
> **A property of depth-first search.** Run the book's RecursiveDFS with parent pointers:
>
> ```text
> RecursiveDFS(v):
>     mark v
>     for each edge vw
>         if w is unmarked
>             parent(w) ← v
>             RecursiveDFS(w)
> ```
>
> (★) *If $uv$ is an edge and $u$ is marked before $v$, then $v$ is a descendant of $u$ in the depth-first tree.* Indeed, $\textsf{RecursiveDFS}(u)$ scans the edge $uv$ before it returns, so $v$ is marked while that call is active; every vertex marked during the call is marked by a call made from it, directly or through other calls, so its chain of parents leads to $u$.
>
> So every edge joins an ancestor and a descendant. The **DFS orientation** directs every tree edge from parent to child and every other edge from its descendant endpoint to its ancestor endpoint.
>
> **Sufficient: the DFS orientation works.** Let $G$ be connected with every edge on a cycle, and run $\textsf{RecursiveDFS}(s)$. Every vertex is reachable from $s$ along tree edges. Every vertex $v$ reaches $s$, by induction on its depth: for $v\ne s$, the tree edge between $v$ and its parent lies on a cycle, so deleting it leaves the subtree $D(v)$ of $v$ connected to the rest of the graph by some other edge $xy$, $x\in D(v)$, $y\notin D(v)$. This edge is not a tree edge (the only tree edge leaving $D(v)$ is the deleted one), and by (★) $y$ is an ancestor of $x$ — a descendant of $x$ would lie in $D(v)$ — so $y$ is a proper ancestor of $v$, and the edge is directed $x\to y$. Thus $v$ reaches $x$ down the tree, then $y$, which has smaller depth and reaches $s$ by induction. So the orientation is strongly connected.
>
> **Algorithm.** Compute the DFS orientation from any vertex $s$; run whatever-first search from $s$ in the oriented graph and in its reversal; answer True if and only if both searches mark every vertex. If they do, every vertex is reachable from $s$ and reaches $s$, so the orientation is strongly connected. If some strongly connected orientation exists, $G$ is connected with every edge on a cycle, so the DFS orientation is strongly connected and both searches succeed.
>
> **Time.** One depth-first search and two whatever-first searches: $O(V + E)$. (Testing every edge separately — is $G - e$ still connected? — gives a simpler $O(E(V+E))$ algorithm.)
>
> **Answer.** Possible exactly when $G$ is connected and no edge is a bridge; decide it, and find the orientation, in $O(V + E)$ time by orienting a depth-first search tree.

## Exercise 5.8 — Depth-first and breadth-first at once

> [!question] Exercise 5.8 (book p. 209)
> Let $T$ be a depth-first spanning tree of a connected graph $G$, rooted at a vertex $v$. Prove that if $T$ is also a breadth-first spanning tree of $G$ rooted at $v$, then $G = T$.

> [!hint]- Hint
> In a depth-first tree every edge of $G$ joins an ancestor and a descendant; in a breadth-first tree the depths of adjacent vertices differ by at most 1.

> [!solution]- Solution
> **Depth-first.** Whatever-first search with a stack builds exactly the trees that RecursiveDFS builds, over all orders of the adjacency lists: on the same lists it tries each vertex's neighbors in reverse order, so it builds RecursiveDFS's tree for the reversed lists ([[2-algorithms/05-basic-graph-algorithms#55-whatever-first-search|§5.5]]). By (★) of Exercise 5.7, every edge $xy$ of $G$ joins an ancestor and a descendant in $T$.
>
> **Breadth-first.** A breadth-first spanning tree contains shortest paths from its root ([[2-algorithms/05-basic-graph-algorithms#56-important-variants|§5.6]]): the depth of every vertex $x$ in $T$ is its distance $\textsf{dist}(v, x)$ in $G$. For any edge $xy$, a shortest path to $x$ followed by $xy$ is a walk to $y$, so $\textsf{dist}(v, y)\le\textsf{dist}(v, x) + 1$, and symmetrically: the depths of adjacent vertices differ by at most 1.
>
> **Together.** Let $xy$ be any edge of $G$, with $x$ an ancestor of $y$. Then $y$ is deeper than $x$, but by at most 1, so $x$ is the parent of $y$ and $xy$ is the tree edge between them (a simple graph has only one edge $xy$). So every edge of $G$ is in $T$, and $G = T$.
>
> **Answer.** Ancestor–descendant edges whose depths differ by at most 1 are parent–child edges, so $G$ has no edge outside $T$.

## Exercise 5.9 — Eager whatever-first search

> [!question] Exercise 5.9 (book p. 209)
> Professors Epprich and Goodstein mark vertices when they enter the bag instead of when they leave it, so that each vertex enters the bag at most once:
>
> ```text
> EagerWFS(s):
>     mark s
>     put s into the bag
>     while the bag is not empty
>         take v from the bag
>         for each edge vw
>             if w is unmarked
>                 mark w
>                 parent(w) ← v
>                 put w into the bag
> ```
>
> (a) Prove that $\textsf{EagerWFS}(s)$ marks every vertex reachable from $s$ and nothing else, and that its parent edges form a spanning tree of the component of $s$.
>
> (b) Prove that with a queue as the bag, EagerWFS is equivalent to breadth-first search: both mark the same vertices in the same order and build the same spanning tree.
>
> (c) Prove that EagerWFS is never equivalent to depth-first search, whatever the bag: exhibit a graph $G$ such that no spanning tree that RecursiveDFS can build (for any order of the edges at each vertex) can be built by EagerWFS (with any bag), or vice versa.

### (a) Correctness

> [!hint]- Hint
> Every marked vertex goes through the bag exactly once. For reachability, look at the first unmarked vertex on a path from $s$.

> [!solution]- Solution
> A vertex enters the bag exactly when it is marked, so every marked vertex passes through the bag exactly once and the loop runs at most $V$ times.
>
> **Marked ⇒ reachable, with parents leading to $s$.** By induction on the marking order: $s$ is reachable. Any other vertex $w$ is marked while the edge $vw$ of a vertex $v$ taken from the bag is scanned; $v$ was marked earlier, and $\mathit{parent}(w) = v$. By induction the parent chain from $v$ leads to $s$, so the one from $w$ does too.
>
> **Reachable ⇒ marked.** Suppose $x$ is reachable but unmarked at the end. On a path from $s$ to $x$, some edge $yz$ has $y$ marked and $z$ unmarked. But $y$ entered the bag when it was marked, left it before the bag became empty, and at that time the loop scanned $yz$ and marked $z$ if it was still unmarked — a contradiction.
>
> **Spanning tree.** Every marked vertex other than $s$ has exactly one parent, so $k$ marked vertices have $k - 1$ parent edges, and they connect everything to $s$: a spanning tree of the component of $s$ (Exercise 5.1, definition 3). With $O(1)$ bag operations the running time is $O(V + E)$.
>
> **Answer.** EagerWFS marks exactly the vertices reachable from $s$, and its parent edges are a spanning tree of their component.

### (b) With a queue it is breadth-first search

> [!hint]- Hint
> A queue releases items in the order they went in. In both algorithms, which vertex is processed next, and which vertex becomes its parent?

> [!solution]- Solution
> Compare EagerWFS with a queue and the book's breadth-first search (whatever-first search with pairs $(p, v)$ in a queue, marking a vertex when its first pair comes out), using the same adjacency lists. In both algorithms **scanning** a vertex $v$ means running through its edges $vw$ in list order, and each step is a **sighting** of $w$ by $v$.
>
> - **EagerWFS** marks $w$, gives it the parent $v$ and appends it to the queue at its **first** sighting; later sightings find $w$ marked. The queue releases vertices in the order they were appended, so the vertices are scanned in the order of their first sightings, $s$ first.
> - **BFS** appends a pair $(v, w)$ at **every** sighting, and the queue releases the pairs in sighting order. The first pair $(\cdot, w)$ to come out is the one from $w$'s first sighting, and $w$ is still unmarked then (only a pair $(\cdot, w)$ can mark $w$; $s$ is marked first of all). So $w$ is marked, with the parent $v$ of its first sighting, and scanned; its later pairs are discarded. Again the vertices are marked and scanned in the order of their first sightings, $s$ first.
>
> So both algorithms obey the same rule: the next vertex to be scanned is the earliest first-sighted vertex not yet scanned, and its parent is the vertex that sighted it first. The sightings, in turn, are determined by the order of the scans. By induction on $k$: if both algorithms scan the same first $k$ vertices, they make the same sightings during those scans, so they scan the same $(k+1)$-st vertex with the same parent. Hence they mark the same vertices in the same order and build the same tree.
>
> **Answer.** Both scan vertices in order of first sighting and take the first sighter as parent, so they coincide.

### (c) Never depth-first search

> [!hint]- Hint
> Try a triangle. What does EagerWFS do with both neighbors of $s$ in its very first iteration?

> [!solution]- Solution
> Let $G$ be the triangle on $s, a, b$.
>
> **EagerWFS(s), any bag, any edge order.** The first iteration takes $s$, the only vertex in the bag, and scans its edges $sa$ and $sb$ while $a$ and $b$ are both unmarked, so $\mathit{parent}(a) = \mathit{parent}(b) = s$. The tree is always the star $\{sa, sb\}$.
>
> **RecursiveDFS(s), any edge order.** The call at $s$ recurses into its first neighbor, say $a$, before it looks at the second; the call at $a$ finds $b$ unmarked and makes it a child of $a$. The tree is the path $\{sa, ab\}$ or $\{sb, ba\}$, never the star.
>
> So no tree of RecursiveDFS on the triangle can be built by EagerWFS. (Both searches start at $s$, as in (b): as unrooted trees all three spanning trees of a triangle are paths, and RecursiveDFS from $a$ can build $\{as, sb\}$. The complete graph $K_4$ needs no such proviso: from any start, EagerWFS makes the start the parent of all three other vertices, while every RecursiveDFS tree of $K_4$ is a path through all four.)
>
> **Answer.** On a triangle searched from $s$, EagerWFS always makes $s$ the parent of both other vertices; depth-first search always gives $s$ a single child.

## Exercise 5.10 — Three-color search

> [!question] Exercise 5.10 (book pp. 210–211), parts (a)–(d)
> Dijkstra, Lamport, Martin, Scholten and Steffens (1975) color vertices white, gray or black instead of marking them:
>
> ```text
> ThreeColorSearch(s):              ThreeColorStep():
>     color all vertices white          v ← any gray vertex
>     color s gray                      if v has no white neighbors
>     while some vertex is gray             color v black
>         ThreeColorStep()              else
>                                           w ← any white neighbor of v
>                                           parent(w) ← v
>                                           color w gray
> ```
>
> (a) Prove the invariant: no black vertex is ever adjacent to a white vertex.
>
> (b) Prove that when $\textsf{ThreeColorSearch}(s)$ terminates, the vertices reachable from $s$ are black, the others white, and the parent edges form a spanning tree of the component of $s$.
>
> (c) The stack variant keeps the gray vertices in a stack: it starts with $s$ on the stack, and each step **pops** $v$; if $v$ has no white neighbors it colors $v$ black, and otherwise it picks a white neighbor $w$, sets $\mathit{parent}(w)\leftarrow v$, colors $w$ gray, and **pushes $v$, then $w$**. Prove that it is equivalent to depth-first search. (The book's hint: the order of the two pushes matters.)
>
> (d) The queue variant is the same with a queue (pull $v$; push $v$, then $w$). Prove that it is **not** equivalent to breadth-first search. (Hint: here the order of the two pushes does not matter.)
>
> Parts (e) and (f), on concurrent garbage collection (♥), are skipped.

### (a) and (b) The invariant and correctness

> [!hint]- Hint
> Colors only get darker. For (b), black and white vertices cannot meet along a path from $s$.

> [!solution]- Solution
> **(a)** Initially no vertex is black. A step either colors $v$ black when $v$ has no white neighbor, which creates no black–white pair, or colors a white vertex gray, which creates no black vertex. So the invariant holds after every step.
>
> **(b) Termination.** Every step changes one vertex from white to gray or from gray to black, and colors never get lighter, so there are at most $2V$ steps. At the end no vertex is gray.
>
> **Non-white vertices are reachable.** $s$ is reachable; another vertex $w$ turns gray only as a white neighbor of a gray vertex $v$, which turned non-white earlier, and then $\mathit{parent}(w) = v$. By induction every non-white vertex has a parent chain to $s$. So vertices not reachable from $s$ stay white.
>
> **Reachable vertices are black.** $s$ is never white. If a reachable vertex $x$ were white at the end, some edge of a path from $s$ to $x$ would join a non-white vertex — black, since none is gray — to a white one, contradicting (a).
>
> **Spanning tree.** Each non-white vertex other than $s$ received exactly one parent, so the $k$ vertices of the component of $s$ carry $k - 1$ parent edges that connect them all to $s$: a spanning tree, rooted at $s$.
>
> **Answer.** Colors only darken (termination within $2V$ steps), and the invariant keeps black and white apart, so at the end black = reachable and white = unreachable.

### (c) The stack variant is depth-first search

> [!hint]- Hint
> Match the stack with the recursion stack of RecursiveDFS: gray = active call, black = finished call, white = unmarked.

> [!solution]- Solution
> Compare with RecursiveDFS with parent pointers (Exercise 5.7). **Invariant:** the stack holds exactly the gray vertices, each once, from bottom to top $s = g_0, g_1, \dots, g_k$ with $\mathit{parent}(g_i) = g_{i-1}$ — exactly the vertices whose calls $\textsf{RecursiveDFS}(g_i)$ are active, innermost on top. Black vertices are those whose calls have returned, white vertices are unmarked.
>
> A step pops the top $g_k$, the innermost active call, and then:
>
> - if $g_k$ has no white neighbor, it turns black and stays off the stack — the call's loop has met only marked neighbors, so it returns, and $g_{k-1}$ is on top again;
> - otherwise it picks a white neighbor $w$, makes $g_k$ its parent and pushes $g_k$ back, then $w$ on top — the call at $g_k$ has reached an unmarked neighbor $w$ in its loop and calls $\textsf{RecursiveDFS}(w)$, which runs to completion before the loop at $g_k$ continues.
>
> Both cases preserve the invariant. Pushing $w$ **after** $g_k$ is essential: in the other order $g_k$ would be popped again first and could adopt more white neighbors before $w$ is explored.
>
> So a run of ThreeColorStackSearch does exactly what RecursiveDFS does when every adjacency list begins with the vertex's children in the order the run chose them (by the time the run blackens a vertex, all its neighbors are non-white, so the rest of the list holds only marked vertices); conversely, choosing in every step the first white neighbor in list order reproduces RecursiveDFS with those lists. The two algorithms mark (turn gray) the same vertices in the same order and build the same trees.
>
> **Answer.** The stack is the recursion stack; each step is one iteration of an active call's loop or its return.

### (d) The queue variant is not breadth-first search

> [!hint]- Hint
> Breadth-first search makes every neighbor of $s$ a child of $s$. Find a graph where the queue variant cannot.

> [!solution]- Solution
> Take the complete graph $K_4$ on $s, a, b, c$. Every breadth-first spanning tree from $s$ is the star at $s$, since every other vertex is at distance 1 ([[2-algorithms/05-basic-graph-algorithms#56-important-variants|§5.6]]).
>
> Every run of ThreeColorQueueSearch: step 1 pulls $s$ and picks some white neighbor $x$ (parent $s$); the queue is $(s, x)$. Step 2 pulls $s$ and picks a white $y$ (parent $s$); the queue is $(x, s, y)$. Step 3 pulls $x$, whose neighbor $z$ — the fourth vertex — is still white, so $\mathit{parent}(z) = x$. The tree has $z$ at depth 2, so it is not a breadth-first tree.
>
> With the pushes in the other order ($w$, then $v$), step 2 already pulls $x$, which adopts a white vertex at once — the same failure.
>
> **Answer.** On $K_4$ the queue variant always gives some neighbor of $s$ a parent other than $s$; breadth-first search never does.

## Exercise 5.11 — Number maze

> [!question] Exercise 5.11 (book p. 212)
> A **number maze** is an $n\times n$ grid of positive integers. A token starts in the top-left square; each move takes it up, down, left or right by exactly the number on its current square, without leaving the board. Describe and analyze an efficient algorithm that returns the minimum number of moves from the top-left to the bottom-right square, or reports that there is no solution. For the maze of Figure 5.14 (reproduced below), the answer is 8.

> [!hint]- Hint
> One vertex per square, one edge per legal move. Are the edges symmetric?

> [!solution]- Solution
> Let $M[1\,..\,n, 1\,..\,n]$ be the grid, row 1 at the top.
>
> **Graph.** A **directed** graph $G$ with one vertex $(i, j)$ for each square, $1\le i, j\le n$, and for each square, with $k = M[i, j]$, the edges
> $$
> (i, j)\to(i - k, j),\quad (i, j)\to(i + k, j),\quad (i, j)\to(i, j - k),\quad (i, j)\to(i, j + k)
> $$
> for those targets that lie on the grid. The edges are directed because the length of a move depends on the square it starts from. $G$ has $n^2$ vertices and at most $4n^2$ edges and is built in $O(n^2)$ time.
>
> **Problem.** Moves of the token correspond one-to-one to edges of $G$, so a solution with $m$ moves is a walk with $m$ edges from $(1, 1)$ to $(n, n)$. The answer is the **shortest-path distance** (number of edges) from $(1, 1)$ to $(n, n)$, and the maze has no solution if $(n, n)$ is not reachable.
>
> **Algorithm.** Breadth-first search in $G$ from $(1, 1)$; return the distance of $(n, n)$, or "no solution" if BFS does not reach it.
>
> **Time.** $O(V + E) = O(n^2)$.
>
> On Figure 5.14 the search returns 8, with the solution right 3, down 4, left 2, right 1, up 3, left 1, right 3, down 3.
>
> **Answer.** BFS distance from $(1,1)$ to $(n,n)$ in the directed move graph: $O(n^2)$ time.

<!-- fig:a05x-number-maze -->
<figure class="cs-fig"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 626 320" width="626" height="320" role="img" style="font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-size:14px"><title>a five by five number maze with an eight-move solution, and a grid of BFS distances</title><defs><marker id="ARR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs><text x="148" y="13" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">the maze and a shortest solution</text><rect x="8" y="30" width="56" height="56" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="20" y="43" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">3</text><rect x="64" y="30" width="56" height="56" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="76" y="43" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">5</text><rect x="120" y="30" width="56" height="56" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="132" y="43" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">7</text><rect x="176" y="30" width="56" height="56" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="188" y="43" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">4</text><rect x="232" y="30" width="56" height="56" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="244" y="43" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">6</text><rect x="8" y="86" width="56" height="56" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="20" y="99" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">5</text><rect x="64" y="86" width="56" height="56" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="76" y="99" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">3</text><rect x="120" y="86" width="56" height="56" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="132" y="99" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">1</text><rect x="176" y="86" width="56" height="56" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="188" y="99" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">5</text><rect x="232" y="86" width="56" height="56" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="244" y="99" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">3</text><rect x="8" y="142" width="56" height="56" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="20" y="155" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">2</text><rect x="64" y="142" width="56" height="56" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="76" y="155" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">8</text><rect x="120" y="142" width="56" height="56" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="132" y="155" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">3</text><rect x="176" y="142" width="56" height="56" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="188" y="155" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">1</text><rect x="232" y="142" width="56" height="56" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="244" y="155" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">4</text><rect x="8" y="198" width="56" height="56" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="20" y="211" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">4</text><rect x="64" y="198" width="56" height="56" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="76" y="211" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">5</text><rect x="120" y="198" width="56" height="56" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="132" y="211" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">7</text><rect x="176" y="198" width="56" height="56" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="188" y="211" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">2</text><rect x="232" y="198" width="56" height="56" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="244" y="211" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">3</text><rect x="8" y="254" width="56" height="56" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="20" y="267" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">3</text><rect x="64" y="254" width="56" height="56" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="76" y="267" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">1</text><rect x="120" y="254" width="56" height="56" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="132" y="267" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">3</text><rect x="176" y="254" width="56" height="56" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="188" y="267" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">2</text><rect x="232" y="254" width="56" height="56" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="260" y="283" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:22px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">★</text><rect x="8" y="30" width="280" height="280" rx="0" fill="none" stroke="currentColor" stroke-width="1.6"/><rect x="10" y="32" width="52" height="52" rx="0" fill="none" stroke="var(--hi)" stroke-width="2"/><path d="M43.0,61.5 Q120.0,68.0 197.0,61.5" fill="none" stroke="var(--hi)" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><circle cx="120" cy="64.8" r="8" fill="var(--paper)" stroke="var(--hi)" stroke-width="1.2"/><text x="120" y="65.2" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:11px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">1</text><path d="M201.2,65.0 Q196.0,170.0 201.2,275.0" fill="none" stroke="var(--hi)" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><circle cx="198.6" cy="170" r="8" fill="var(--paper)" stroke="var(--hi)" stroke-width="1.2"/><text x="198.6" y="170.5" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:11px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">2</text><path d="M197.0,286.2 Q148.0,294.0 99.0,286.2" fill="none" stroke="var(--hi)" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><circle cx="148" cy="290.1" r="8" fill="var(--paper)" stroke="var(--hi)" stroke-width="1.2"/><text x="148" y="290.6" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:11px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">3</text><path d="M99.0,280.9 Q120.0,279.0 141.0,280.9" fill="none" stroke="var(--hi)" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><circle cx="120" cy="280" r="8" fill="var(--paper)" stroke="var(--hi)" stroke-width="1.2"/><text x="120" y="280.5" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:11px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">4</text><path d="M145.2,275.0 Q140.0,198.0 145.2,121.0" fill="none" stroke="var(--hi)" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><circle cx="142.6" cy="198" r="8" fill="var(--paper)" stroke="var(--hi)" stroke-width="1.2"/><text x="142.6" y="198.5" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:11px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">5</text><path d="M141.0,118.2 Q120.0,126.0 99.0,118.2" fill="none" stroke="var(--hi)" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><circle cx="120" cy="122.1" r="8" fill="var(--paper)" stroke="var(--hi)" stroke-width="1.2"/><text x="120" y="122.6" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:11px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">6</text><path d="M99.0,112.6 Q176.0,110.0 253.0,112.6" fill="none" stroke="var(--hi)" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><circle cx="176" cy="111.3" r="8" fill="var(--paper)" stroke="var(--hi)" stroke-width="1.2"/><text x="176" y="111.8" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:11px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">7</text><path d="M257.2,121.0 Q252.0,198.0 257.2,275.0" fill="none" stroke="var(--hi)" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><circle cx="254.6" cy="198" r="8" fill="var(--paper)" stroke="var(--hi)" stroke-width="1.2"/><text x="254.6" y="198.5" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:11px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">8</text><text x="478" y="13" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">BFS distance from the start</text><rect x="338" y="30" width="56" height="56" rx="0" fill="var(--accent)" fill-opacity="0.13" stroke="none" stroke-width="0"/><rect x="338" y="30" width="56" height="56" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="366" y="59" text-anchor="middle" dominant-baseline="central" fill="var(--accent)" style="font-size:17px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">0</text><rect x="394" y="30" width="56" height="56" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="422" y="59" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:17px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">–</text><rect x="450" y="30" width="56" height="56" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="478" y="59" text-anchor="middle" dominant-baseline="central" fill="var(--accent)" style="font-size:17px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">6</text><rect x="506" y="30" width="56" height="56" rx="0" fill="var(--accent)" fill-opacity="0.13" stroke="none" stroke-width="0"/><rect x="506" y="30" width="56" height="56" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="534" y="59" text-anchor="middle" dominant-baseline="central" fill="var(--accent)" style="font-size:17px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">1</text><rect x="562" y="30" width="56" height="56" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="590" y="59" text-anchor="middle" dominant-baseline="central" fill="var(--accent)" style="font-size:17px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">3</text><rect x="338" y="86" width="56" height="56" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="366" y="115" text-anchor="middle" dominant-baseline="central" fill="var(--accent)" style="font-size:17px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">5</text><rect x="394" y="86" width="56" height="56" rx="0" fill="var(--accent)" fill-opacity="0.13" stroke="none" stroke-width="0"/><rect x="394" y="86" width="56" height="56" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="422" y="115" text-anchor="middle" dominant-baseline="central" fill="var(--accent)" style="font-size:17px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">6</text><rect x="450" y="86" width="56" height="56" rx="0" fill="var(--accent)" fill-opacity="0.13" stroke="none" stroke-width="0"/><rect x="450" y="86" width="56" height="56" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="478" y="115" text-anchor="middle" dominant-baseline="central" fill="var(--accent)" style="font-size:17px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">5</text><rect x="506" y="86" width="56" height="56" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="534" y="115" text-anchor="middle" dominant-baseline="central" fill="var(--accent)" style="font-size:17px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">4</text><rect x="562" y="86" width="56" height="56" rx="0" fill="var(--accent)" fill-opacity="0.13" stroke="none" stroke-width="0"/><rect x="562" y="86" width="56" height="56" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="590" y="115" text-anchor="middle" dominant-baseline="central" fill="var(--accent)" style="font-size:17px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">7</text><rect x="338" y="142" width="56" height="56" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="366" y="171" text-anchor="middle" dominant-baseline="central" fill="var(--accent)" style="font-size:17px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">5</text><rect x="394" y="142" width="56" height="56" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="422" y="171" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:17px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">–</text><rect x="450" y="142" width="56" height="56" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="478" y="171" text-anchor="middle" dominant-baseline="central" fill="var(--accent)" style="font-size:17px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">4</text><rect x="506" y="142" width="56" height="56" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="534" y="171" text-anchor="middle" dominant-baseline="central" fill="var(--accent)" style="font-size:17px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">3</text><rect x="562" y="142" width="56" height="56" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="590" y="171" text-anchor="middle" dominant-baseline="central" fill="var(--accent)" style="font-size:17px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">4</text><rect x="338" y="198" width="56" height="56" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="366" y="227" text-anchor="middle" dominant-baseline="central" fill="var(--accent)" style="font-size:17px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">1</text><rect x="394" y="198" width="56" height="56" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="422" y="227" text-anchor="middle" dominant-baseline="central" fill="var(--accent)" style="font-size:17px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">3</text><rect x="450" y="198" width="56" height="56" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="478" y="227" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:17px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">–</text><rect x="506" y="198" width="56" height="56" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="534" y="227" text-anchor="middle" dominant-baseline="central" fill="var(--accent)" style="font-size:17px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">4</text><rect x="562" y="198" width="56" height="56" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="590" y="227" text-anchor="middle" dominant-baseline="central" fill="var(--accent)" style="font-size:17px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">2</text><rect x="338" y="254" width="56" height="56" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="366" y="283" text-anchor="middle" dominant-baseline="central" fill="var(--accent)" style="font-size:17px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">4</text><rect x="394" y="254" width="56" height="56" rx="0" fill="var(--accent)" fill-opacity="0.13" stroke="none" stroke-width="0"/><rect x="394" y="254" width="56" height="56" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="422" y="283" text-anchor="middle" dominant-baseline="central" fill="var(--accent)" style="font-size:17px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">3</text><rect x="450" y="254" width="56" height="56" rx="0" fill="var(--accent)" fill-opacity="0.13" stroke="none" stroke-width="0"/><rect x="450" y="254" width="56" height="56" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="478" y="283" text-anchor="middle" dominant-baseline="central" fill="var(--accent)" style="font-size:17px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">4</text><rect x="506" y="254" width="56" height="56" rx="0" fill="var(--accent)" fill-opacity="0.13" stroke="none" stroke-width="0"/><rect x="506" y="254" width="56" height="56" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="534" y="283" text-anchor="middle" dominant-baseline="central" fill="var(--accent)" style="font-size:17px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">2</text><rect x="562" y="254" width="56" height="56" rx="0" fill="var(--accent)" fill-opacity="0.13" stroke="none" stroke-width="0"/><rect x="562" y="254" width="56" height="56" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="590" y="283" text-anchor="middle" dominant-baseline="central" fill="var(--accent)" style="font-size:17px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">8</text><rect x="338" y="30" width="280" height="280" rx="0" fill="none" stroke="currentColor" stroke-width="1.6"/></svg><figcaption><strong>Exercise 5.11: the maze of Figure 5.14.</strong> Left: the book's number maze (labels in the corners; start framed, goal ★) with a shortest solution found by BFS (moves numbered 1–8: right 3, down 4, left 2, right 1, up 3, left 1, right 3, down 3). Right: the BFS distance of every square from the top-left one in the move graph; the shaded squares are the solution's. 3 squares (–) cannot be reached at all.</figcaption></figure>

## Exercise 5.12 — Snakes and Ladders

> [!question] Exercise 5.12 (book pp. 212–213)
> A Snakes and Ladders board is an $n\times n$ grid whose squares are numbered $1$ to $n^2$ in a zigzag from the bottom-left corner. Some pairs of squares in different rows are joined by a **snake** (leading down) or a **ladder** (leading up); every square is an endpoint of at most one snake or ladder. A token starts on square 1. In each move it advances by $1, 2, \dots,$ or $k$ squares, for a fixed constant $k$; if it lands on the top of a snake it slides down to the snake's bottom, and if it lands on the bottom of a ladder it climbs to the ladder's top. Describe and analyze an algorithm that computes the smallest number of moves needed to reach square $n^2$.

> [!hint]- Hint
> Put the snake or ladder into the edge: a move from $i$ that lands on $j$ really ends at $j$'s other end.

> [!solution]- Solution
> The input is $n$, $k$ and the list of snakes and ladders as pairs of squares. Assume, as on the book's board, that squares 1 and $n^2$ are not endpoints, and that a move cannot overshoot square $n^2$.
>
> **Destination array.** For $1\le j\le n^2$, let $\mathit{dest}(j)$ be the other end of the snake or ladder at $j$ if $j$ is the top of a snake or the bottom of a ladder, and $j$ itself otherwise. Filling the array from the list takes $O(n^2)$ time.
>
> **Graph.** A **directed** graph with vertices $1, \dots, n^2$ and an edge $i\to\mathit{dest}(j)$ for every $i$ and every $j$ with $i < j\le\min\{i + k, n^2\}$. It has $n^2$ vertices and at most $kn^2$ edges.
>
> **Problem.** A move from a resting square $i$ ends on $\mathit{dest}(j)$, where $j$ is the square it lands on, so the moves are exactly the edges, and a game of $m$ moves is a walk of $m$ edges from 1. The answer is the **shortest-path distance** from vertex 1 to vertex $n^2$; if $n^2$ is not reachable from 1, no number of moves suffices.
>
> **Algorithm.** Breadth-first search from vertex 1.
>
> **Time.** $O(V + E) = O(kn^2)$, which is $O(n^2)$ for constant $k$.
>
> The book gives no number for its board (Figure 5.15). Reading its snakes as 27→17, 67→10, 79→40, 95→71, 98→6 and its ladders as 3→42, 8→54, 24→86, 50→93, 58→65, 59→81, BFS finds that with $k = 6$ the token needs **5** moves — compared with 17 on an empty board — for example advancing 2 (to 3, up the ladder to 42), 2 (to 44), 6 (to 50, up the ladder to 93), 1 (to 94) and 6 (to 100). With $k = 1$ square 100 is unreachable: the route is forced, and from 93 it lands on 94, 95 (down to 71), 72, …, 79 (down to 40), 41, …, 50 (up to 93) and around again forever, never beyond 95.
>
> **Answer.** BFS distance from 1 to $n^2$ in the graph with edges $i\to\mathit{dest}(j)$, $i<j\le i+k$: $O(n^2)$ time.

## Exercise 5.13 — Vidrach Itky Leda

> [!question] Exercise 5.13 (book pp. 213–214)
> An $n\times n$ grid of positive integers carries a red and a blue token on distinct squares, starting in the top-left and bottom-right corners; the goal is to swap them. In one turn you move **one** token up, down, left or right by the number on the square of the **other** token, without leaving the grid and without landing on the other token. Describe and analyze an efficient algorithm that returns the minimum number of moves, or reports that the puzzle has no solution. For the puzzle
> $$
> \begin{matrix} 1 & 2 & 4 & 3\\ 3 & 4 & 1 & 2\\ 3 & 1 & 2 & 3\\ 2 & 3 & 1 & 2 \end{matrix}
> $$
> of Figure 5.16 the answer is 5.

> [!hint]- Hint
> A single token's position is not enough to describe the state of the puzzle.

> [!solution]- Solution
> Let $M[1\,..\,n, 1\,..\,n]$ be the grid, and write $M[p]$ for the label of square $p$.
>
> **Graph.** A **directed** graph whose vertices are the ordered pairs $(r, b)$ of distinct squares — the positions of the red and the blue token: $n^2(n^2 - 1)$ vertices. From $(r, b)$ there is an edge
>
> - to $(r', b)$ for each square $r'\ne b$ on the grid that lies $M[b]$ steps up, down, left or right of $r$ (red moves), and
> - to $(r, b')$ for each square $b'\ne r$ on the grid that lies $M[r]$ steps up, down, left or right of $b$ (blue moves).
>
> At most 8 edges leave each vertex: $E\le 8n^4$. (Every move can in fact be undone, so the edges come in opposite pairs; the algorithm does not need this.)
>
> **Problem.** Configurations are vertices and legal moves are edges, so the answer is the **shortest-path distance** from $\big((1,1),(n,n)\big)$ to $\big((n,n),(1,1)\big)$, and "no solution" if the latter is unreachable.
>
> **Algorithm.** Breadth-first search from $\big((1,1),(n,n)\big)$.
>
> **Time.** $O(V + E) = O(n^4)$, including building the graph.
>
> On Figure 5.16 BFS returns 5; one solution is the book's: red down 2, blue up 3, red right 3, blue left 3, red down 1.
>
> **Answer.** BFS distance between the two swapped configurations in the graph of token pairs: $O(n^4)$ time.

## Exercise 5.14 — Walks of length divisible by 3

> [!question] Exercise 5.14 (book p. 214)
> Given a directed graph $G = (V, E)$ and vertices $s$ and $t$, describe and analyze an algorithm that decides whether $G$ has a walk from $s$ to $t$ (repeating vertices and edges allowed) whose length is divisible by 3. In the book's example, with edges $s\to w$, $w\to t$, $w\to y$, $y\to x$, $x\to s$, $y\to z$ and $z\to t$, the answer is True, because of the walk $s\to w\to y\to x\to s\to w\to t$ of length 6.

> [!hint]- Hint
> Make three copies of every vertex, one for each possible length mod 3.

> [!solution]- Solution
> **Graph.** A **directed** graph $G'$ with vertices $V\times\{0, 1, 2\}$ and, for every edge $u\to v$ of $G$ and every $i\in\{0,1,2\}$, the edge
> $$
> (u, i)\to\big(v, (i + 1) \bmod 3\big).
> $$
> It has $3V$ vertices and $3E$ edges.
>
> **Problem.** A walk $s = v_0\to v_1\to\cdots\to v_\ell$ in $G$ corresponds to the walk $(v_0, 0)\to(v_1, 1\bmod 3)\to\cdots\to(v_\ell, \ell\bmod 3)$ in $G'$, and every walk in $G'$ from $(s, 0)$ arises this way: the second coordinate counts the edges mod 3. So $G$ has a walk from $s$ to $t$ of length divisible by 3 if and only if $(t, 0)$ is **reachable** from $(s, 0)$ in $G'$. (If $s = t$, the empty walk has length 0 and the answer is True.)
>
> **Algorithm.** Whatever-first search in $G'$ from $(s, 0)$; answer whether $(t, 0)$ is marked.
>
> **Time.** $O(V + E)$.
>
> In the example, $(s,0)\to(w,1)\to(y,2)\to(x,0)\to(s,1)\to(w,2)\to(t,0)$; 6 is also the shortest such length. This is the even-walk reduction of [[2-algorithms/05-basic-graph-algorithms#57-graph-reductions-flood-fill|§5.7]] with three layers instead of two.
>
> **Answer.** Reachability of $(t, 0)$ from $(s, 0)$ in $V\times\{0,1,2\}$: $O(V + E)$ time.

## Exercise 5.15 — No three edges of one color in a row

> [!question] Exercise 5.15 (book p. 214)
> Each edge of a directed graph $G$ is red or blue. Describe an algorithm that finds the shortest walk from $s$ to $t$ in which no three consecutive edges have the same color. In the book's example (drawn below) the answer is 7, for the walk $s\to a\to b\Rightarrow d\to c\Rightarrow a\to b\to t$ (blue edges as $\Rightarrow$).

> [!hint]- Hint
> What do you need to remember about the walk so far to know which edges may come next?

> [!solution]- Solution
> **Graph.** A **directed** graph $G'$ whose vertices are a start vertex $\textit{start}$ and the triples $(v, c, k)$ with $v\in V$, $c\in\{\textsf{red}, \textsf{blue}\}$ and $k\in\{1, 2\}$, meaning "at $v$, and the walk so far ends with exactly $k$ edges of color $c$". For every edge $u\to v$ of $G$ with color $c'$:
>
> - $\textit{start}\to(v, c', 1)$ if $u = s$;
> - $(u, c, k)\to(v, c', 1)$ for $c\ne c'$ and $k\in\{1,2\}$ (the color changes);
> - $(u, c', 1)\to(v, c', 2)$ (a second edge of the same color; there is no edge out of $(u, c', 2)$ in color $c'$).
>
> $G'$ has $4V + 1$ vertices and at most $4E$ edges.
>
> **Problem.** By induction on the length, the legal walks from $s$ correspond one-to-one to the walks in $G'$ from $\textit{start}$, with the same number of edges: the triple records exactly what decides whether the next edge is allowed. So the answer is the **shortest-path distance** from $\textit{start}$ to the nearest of the four vertices $(t, c, k)$ (and 0 if $s = t$); if none is reachable, there is no legal walk.
>
> **Algorithm.** Breadth-first search in $G'$ from $\textit{start}$, then the minimum of four distances.
>
> **Time.** $O(V + E)$.
>
> In the example the four distances to $t$ give 7: the colors along the walk are red, red, blue, red, blue, red, red.
>
> **Answer.** BFS in the graph of (vertex, last color, run length) triples: $O(V + E)$ time.

<!-- fig:a05x-red-blue -->
<figure class="cs-fig"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 236" width="600" height="236" role="img" style="font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-size:14px"><title>a six-vertex directed graph with red and blue edges and the seven-step walk from s to t</title><defs><marker id="ARR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs><line x1="77" y1="52" x2="170.5" y2="52" stroke="var(--hi)" stroke-width="1.8" stroke-linecap="round" marker-end="url(#ARR)"/><line x1="207" y1="52" x2="300.5" y2="52" stroke="var(--hi)" stroke-width="1.8" stroke-linecap="round" marker-end="url(#ARR)"/><line x1="320" y1="69" x2="320" y2="162.5" stroke="var(--hi)" stroke-width="1.8" stroke-linecap="round" marker-end="url(#ARR)"/><line x1="303" y1="182" x2="209.5" y2="182" stroke="var(--hi)" stroke-width="1.8" stroke-linecap="round" marker-end="url(#ARR)"/><line x1="173" y1="182" x2="79.5" y2="182" stroke="var(--hi)" stroke-width="1.8" stroke-linecap="round" marker-end="url(#ARR)"/><line x1="60" y1="165" x2="60" y2="71.5" stroke="var(--hi)" stroke-width="1.8" stroke-linecap="round" marker-end="url(#ARR)"/><line x1="72" y1="170" x2="176.2" y2="65.8" stroke="var(--accent)" stroke-width="1.8" stroke-linecap="round" marker-end="url(#ARR)" stroke-dasharray="6 4"/><line x1="178" y1="170" x2="73.8" y2="65.8" stroke="var(--accent)" stroke-width="1.8" stroke-linecap="round" marker-end="url(#ARR)" stroke-dasharray="6 4"/><line x1="308" y1="64" x2="203.8" y2="168.2" stroke="var(--accent)" stroke-width="1.8" stroke-linecap="round" marker-end="url(#ARR)" stroke-dasharray="6 4"/><line x1="308" y1="170" x2="203.8" y2="65.8" stroke="var(--accent)" stroke-width="1.8" stroke-linecap="round" marker-end="url(#ARR)" stroke-dasharray="6 4"/><circle cx="60" cy="52" r="17" fill="var(--paper)" stroke="var(--hi)" stroke-width="1.6"/><text x="60" y="53" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:17px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">s</text><circle cx="190" cy="52" r="17" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="190" y="53" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:17px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">a</text><circle cx="320" cy="52" r="17" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="320" y="53" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:17px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">b</text><circle cx="60" cy="182" r="17" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="60" y="183" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:17px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">c</text><circle cx="190" cy="182" r="17" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="190" y="183" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:17px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">d</text><circle cx="320" cy="182" r="17" fill="var(--paper)" stroke="var(--hi)" stroke-width="1.6"/><text x="320" y="183" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:17px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">t</text><line x1="32" y1="222" x2="62" y2="222" stroke="var(--hi)" stroke-width="1.8" stroke-linecap="round"/><text x="68" y="222" text-anchor="start" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">red</text><line x1="112" y1="222" x2="142" y2="222" stroke="var(--accent)" stroke-width="1.8" stroke-linecap="round" stroke-dasharray="6 4"/><text x="148" y="222" text-anchor="start" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">blue</text><text x="395" y="28" text-anchor="start" dominant-baseline="central" fill="var(--muted)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">the shortest legal walk</text><text x="400" y="54" text-anchor="start" dominant-baseline="central" fill="var(--muted)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">1.</text><text x="424" y="54" text-anchor="start" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">s</text><line x1="438" y1="54" x2="470" y2="54" stroke="var(--hi)" stroke-width="1.8" stroke-linecap="round" marker-end="url(#ARR)"/><text x="478" y="54" text-anchor="start" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">a</text><text x="500" y="54" text-anchor="start" dominant-baseline="central" fill="var(--hi)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">red</text><text x="400" y="76" text-anchor="start" dominant-baseline="central" fill="var(--muted)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">2.</text><text x="424" y="76" text-anchor="start" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">a</text><line x1="438" y1="76" x2="470" y2="76" stroke="var(--hi)" stroke-width="1.8" stroke-linecap="round" marker-end="url(#ARR)"/><text x="478" y="76" text-anchor="start" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">b</text><text x="500" y="76" text-anchor="start" dominant-baseline="central" fill="var(--hi)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">red</text><text x="400" y="98" text-anchor="start" dominant-baseline="central" fill="var(--muted)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">3.</text><text x="424" y="98" text-anchor="start" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">b</text><line x1="438" y1="98" x2="470" y2="98" stroke="var(--accent)" stroke-width="1.8" stroke-linecap="round" marker-end="url(#ARR)" stroke-dasharray="6 4"/><text x="478" y="98" text-anchor="start" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">d</text><text x="500" y="98" text-anchor="start" dominant-baseline="central" fill="var(--accent)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">blue</text><text x="400" y="120" text-anchor="start" dominant-baseline="central" fill="var(--muted)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">4.</text><text x="424" y="120" text-anchor="start" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">d</text><line x1="438" y1="120" x2="470" y2="120" stroke="var(--hi)" stroke-width="1.8" stroke-linecap="round" marker-end="url(#ARR)"/><text x="478" y="120" text-anchor="start" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">c</text><text x="500" y="120" text-anchor="start" dominant-baseline="central" fill="var(--hi)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">red</text><text x="400" y="142" text-anchor="start" dominant-baseline="central" fill="var(--muted)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">5.</text><text x="424" y="142" text-anchor="start" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">c</text><line x1="438" y1="142" x2="470" y2="142" stroke="var(--accent)" stroke-width="1.8" stroke-linecap="round" marker-end="url(#ARR)" stroke-dasharray="6 4"/><text x="478" y="142" text-anchor="start" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">a</text><text x="500" y="142" text-anchor="start" dominant-baseline="central" fill="var(--accent)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">blue</text><text x="400" y="164" text-anchor="start" dominant-baseline="central" fill="var(--muted)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">6.</text><text x="424" y="164" text-anchor="start" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">a</text><line x1="438" y1="164" x2="470" y2="164" stroke="var(--hi)" stroke-width="1.8" stroke-linecap="round" marker-end="url(#ARR)"/><text x="478" y="164" text-anchor="start" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">b</text><text x="500" y="164" text-anchor="start" dominant-baseline="central" fill="var(--hi)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">red</text><text x="400" y="186" text-anchor="start" dominant-baseline="central" fill="var(--muted)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">7.</text><text x="424" y="186" text-anchor="start" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">b</text><line x1="438" y1="186" x2="470" y2="186" stroke="var(--hi)" stroke-width="1.8" stroke-linecap="round" marker-end="url(#ARR)"/><text x="478" y="186" text-anchor="start" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">t</text><text x="500" y="186" text-anchor="start" dominant-baseline="central" fill="var(--hi)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">red</text></svg><figcaption><strong>Exercise 5.15: the book's example.</strong> The red edges (solid) form the directed cycle <i>s</i>→<i>a</i>→<i>b</i>→<i>t</i>→<i>d</i>→<i>c</i>→<i>s</i>; the blue edges (dashed) are <i>c</i>→<i>a</i>, <i>d</i>→<i>s</i>, <i>b</i>→<i>d</i> and <i>t</i>→<i>a</i>. The obvious walk <i>s</i>→<i>a</i>→<i>b</i>→<i>t</i> uses three reds in a row; the shortest legal walk (right) has 7 edges, colored red, red, blue, red, blue, red, red.</figcaption></figure>

## Exercise 5.16 — French flag walks

> [!question] Exercise 5.16 (book p. 215)
> Every edge of a directed graph $G$ is red, white or blue. A walk $v_0\to v_1\to\cdots\to v_k$ is a **French flag walk** if its edge $v_i\to v_{i+1}$ is red when $i\bmod 3 = 0$, white when $i\bmod 3 = 1$ and blue when $i\bmod 3 = 2$. Describe an algorithm that finds all vertices reachable from a given vertex $v$ by a French flag walk.

> [!hint]- Hint
> As in Exercise 5.14, remember the position in the pattern — but keep only the edges of the right color in each layer.

> [!solution]- Solution
> **Graph.** A **directed** graph $G'$ with vertices $V\times\{0, 1, 2\}$ and, for every edge $u\to w$ of $G$, the single edge
> $$
> (u, i)\to\big(w, (i+1)\bmod 3\big)\quad\text{where } i = 0, 1, 2 \text{ if } u\to w \text{ is red, white, blue.}
> $$
> It has $3V$ vertices and exactly $E$ edges.
>
> **Problem.** French flag walks from $v$ of length $\ell$ correspond one-to-one to walks in $G'$ from $(v, 0)$ of length $\ell$, ending in layer $\ell\bmod 3$: the layer says which color the next edge must have. So $w$ is reachable by a French flag walk if and only if **some** $(w, i)$ is **reachable** from $(v, 0)$. ($v$ itself always is, by the empty walk.)
>
> **Algorithm.** Whatever-first search in $G'$ from $(v, 0)$; output every $w$ such that at least one of $(w, 0), (w, 1), (w, 2)$ is marked.
>
> **Time.** $O(V + E)$.
>
> **Answer.** Reachability from $(v, 0)$ in the three-layer graph, projected back to $V$: $O(V + E)$ time.

## Exercise 5.17 — Teleport tolls divisible by five

> [!question] Exercise 5.17 (book p. 215)
> $n$ galaxies are joined by $m$ two-way teleport-ways; teleport-way $e$ costs $c(e)$ dollars, a positive integer, every time it is used. Judy travels from galaxy $s$ to galaxy $t$ with as few teleports as possible, but the total cost must be a multiple of 5 dollars.
>
> (a) Describe and analyze an algorithm that computes the smallest number of teleports for such a trip.
>
> (b) Solve (a) again, assuming Judy has a coupon that lets her use exactly one teleport-way for free — read here, as the natural meaning of a coupon, as one free use of one teleport-way.

> [!hint]- Hint
> Only the total cost mod 5 matters. For (b), also remember whether the coupon has been spent.

> [!solution]- Solution
> **(a) Graph.** A **directed** graph $G_a$ with a vertex $(g, r)$ for each galaxy $g$ and residue $r\in\{0, \dots, 4\}$ (the total cost so far, mod 5), and for every teleport-way $e$ between $g$ and $h$ and every $r$ the two edges
> $$
> (g, r)\to\big(h, (r + c(e))\bmod 5\big),\qquad (h, r)\to\big(g, (r + c(e))\bmod 5\big).
> $$
> Directed, because traversing an edge backward would subtract the toll. $5n$ vertices, $10m$ edges.
>
> **Problem.** Trips from $s$ with $\ell$ teleports and total cost $C$ correspond to walks from $(s, 0)$ with $\ell$ edges that end at a vertex $(\cdot, C\bmod 5)$. The answer is the **shortest-path distance** from $(s, 0)$ to $(t, 0)$, or "impossible" if $(t, 0)$ is unreachable.
>
> **Algorithm.** Breadth-first search from $(s, 0)$.
>
> **Time.** $O(n + m)$.
>
> **(b) Graph.** A **directed** graph $G_b$ with vertices $(g, r, f)$, where $f\in\{0, 1\}$ records whether the coupon has been used: $10n$ vertices. For every teleport-way $e$ between $g$ and $h$ and every $r$: the paying edges $(g, r, f)\to(h, (r + c(e))\bmod 5, f)$ and $(h, r, f)\to(g, (r + c(e))\bmod 5, f)$ for $f = 0, 1$, and the free edges $(g, r, 0)\to(h, r, 1)$ and $(h, r, 0)\to(g, r, 1)$. That is $30m$ edges.
>
> **Problem.** The answer is the smaller of the **shortest-path distances** from $(s, 0, 0)$ to $(t, 0, 0)$ and to $(t, 0, 1)$ — using the coupon is optional. (If the coupon must be used, only $(t, 0, 1)$ counts.)
>
> **Algorithm.** Breadth-first search from $(s, 0, 0)$.
>
> **Time.** $O(n + m)$.
>
> **Answer.** (a) BFS distance from $(s,0)$ to $(t,0)$ over (galaxy, cost mod 5); (b) the same with a coupon bit, minimum over $(t,0,0)$ and $(t,0,1)$. Both $O(n + m)$.

## Exercise 5.18 — Three Seashells

> [!question] Exercise 5.18 (book p. 215)
> Three tokens sit on distinct vertices $a, b, c$ of a connected undirected graph $G$. In each turn **all three** tokens must move, each along an edge to an adjacent vertex, and after the turn they must again be on three different vertices. The goal is to get the tokens onto the vertices $x, y, z$, in any order. Describe and analyze an algorithm that decides whether a given puzzle is solvable.

> [!hint]- Hint
> A configuration is the triple of token positions. How many configurations, and how many ways to leave each one?

> [!solution]- Solution
> **Graph.** A graph $G'$ whose vertices are the ordered triples $(p, q, r)$ of distinct vertices of $G$ — at most $V^3$ — with an edge from $(p, q, r)$ to $(p', q', r')$ whenever $pp'$, $qq'$ and $rr'$ are edges of $G$ and $p', q', r'$ are distinct. Every turn can be undone by moving each token back along its edge, so $G'$ is undirected. The number of edges is
> $$
> \sum_{(p, q, r)}\deg(p)\deg(q)\deg(r)\ \le\ \Big(\sum_{p}\deg(p)\Big)^3 = (2E)^3,
> $$
> and the graph is built by trying, for each triple, every combination of three incident edges: $O(V^3 + E^3)$ time.
>
> **Problem.** Turns are edges, so the puzzle is solvable if and only if one of the six triples $(x, y, z), (x, z, y), \dots, (z, y, x)$ is **reachable** from $(a, b, c)$.
>
> **Algorithm.** Whatever-first search in $G'$ from $(a, b, c)$; check the six goal triples.
>
> **Time.** $O(V^3 + E^3) = O(E^3)$, because $G$ is connected and so $V\le E + 1$.
>
> **The book's example has no solution.** In Figure 5.17 the goal vertices $x$ and $y$ both hang from the same vertex (called $q$ below) and have no other neighbor. A token that ends a turn on $x$ arrived from $q$, and so did a token that ends it on $y$ — two tokens leaving one vertex. So the goal can never be reached, although the book calls the two turns it draws "the first two turns of a solution". If $x$ hung from the left middle vertex $p$ instead, the puzzle would be solvable in 4 turns, starting with the book's two.
>
> **Answer.** Reachability from $(a,b,c)$ to a permutation of $(x,y,z)$ in the graph of token triples: $O(E^3)$ time.

<!-- fig:a05x-seashells -->
<figure class="cs-fig"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 520 222" width="520" height="222" role="img" style="font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-size:14px"><title>the Three Seashells graph as printed and with one edge moved</title><defs><marker id="ARR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs><text x="125" y="16" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">as drawn: no solution</text><line x1="70" y1="46" x2="110" y2="46" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><line x1="140" y1="46" x2="180" y2="46" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><line x1="55" y1="61" x2="55" y2="101" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><line x1="125" y1="61" x2="125" y2="101" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><line x1="70" y1="116" x2="110" y2="116" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><line x1="140" y1="116" x2="180" y2="116" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><line x1="114.4" y1="126.6" x2="65.6" y2="175.4" stroke="var(--hi)" stroke-width="2.6" stroke-linecap="round"/><line x1="125" y1="131" x2="125" y2="171" stroke="var(--hi)" stroke-width="2.6" stroke-linecap="round"/><line x1="195" y1="131" x2="195" y2="171" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><circle cx="55" cy="46" r="15" fill="var(--accent)" fill-opacity="0.18" stroke="currentColor" stroke-width="1.5"/><text x="55" y="47" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:16px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">a</text><circle cx="125" cy="46" r="15" fill="var(--accent)" fill-opacity="0.18" stroke="currentColor" stroke-width="1.5"/><text x="125" y="47" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:16px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">b</text><circle cx="195" cy="46" r="15" fill="var(--accent)" fill-opacity="0.18" stroke="currentColor" stroke-width="1.5"/><text x="195" y="47" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:16px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">c</text><circle cx="55" cy="116" r="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="55" y="117" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:16px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">p</text><circle cx="125" cy="116" r="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="125" y="117" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:16px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">q</text><circle cx="195" cy="116" r="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="195" y="117" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:16px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">r</text><circle cx="55" cy="186" r="19" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><circle cx="55" cy="186" r="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="55" y="187" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:16px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">x</text><circle cx="125" cy="186" r="19" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><circle cx="125" cy="186" r="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="125" y="187" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:16px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">y</text><circle cx="195" cy="186" r="19" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><circle cx="195" cy="186" r="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="195" y="187" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:16px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">z</text><text x="395" y="16" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">x moved to p: 4 turns</text><line x1="340" y1="46" x2="380" y2="46" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><line x1="410" y1="46" x2="450" y2="46" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><line x1="325" y1="61" x2="325" y2="101" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><line x1="395" y1="61" x2="395" y2="101" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><line x1="340" y1="116" x2="380" y2="116" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><line x1="410" y1="116" x2="450" y2="116" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><line x1="395" y1="131" x2="395" y2="171" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><line x1="465" y1="131" x2="465" y2="171" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><line x1="325" y1="131" x2="325" y2="171" stroke="var(--accent)" stroke-width="2.6" stroke-linecap="round" stroke-dasharray="5 4"/><circle cx="325" cy="46" r="15" fill="var(--accent)" fill-opacity="0.18" stroke="currentColor" stroke-width="1.5"/><text x="325" y="47" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:16px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">a</text><circle cx="395" cy="46" r="15" fill="var(--accent)" fill-opacity="0.18" stroke="currentColor" stroke-width="1.5"/><text x="395" y="47" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:16px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">b</text><circle cx="465" cy="46" r="15" fill="var(--accent)" fill-opacity="0.18" stroke="currentColor" stroke-width="1.5"/><text x="465" y="47" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:16px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">c</text><circle cx="325" cy="116" r="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="325" y="117" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:16px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">p</text><circle cx="395" cy="116" r="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="395" y="117" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:16px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">q</text><circle cx="465" cy="116" r="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="465" y="117" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:16px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">r</text><circle cx="325" cy="186" r="19" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><circle cx="325" cy="186" r="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="325" y="187" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:16px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">x</text><circle cx="395" cy="186" r="19" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><circle cx="395" cy="186" r="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="395" y="187" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:16px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">y</text><circle cx="465" cy="186" r="19" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><circle cx="465" cy="186" r="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="465" y="187" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:16px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">z</text></svg><figcaption><strong>Exercise 5.18: the puzzle of Figure 5.17.</strong> Tokens start on the shaded vertices <i>a</i>, <i>b</i>, <i>c</i> and must end on the double circles <i>x</i>, <i>y</i>, <i>z</i> (the book leaves the middle row unnamed; here <i>p</i>, <i>q</i>, <i>r</i>). Left, as printed: <i>x</i> and <i>y</i> are leaves of the same vertex <i>q</i>, so in the last turn two tokens would have to arrive from <i>q</i> at once — there is no solution, although the book shows "the first two turns of a solution". Right: with the edge <i>qx</i> replaced by <i>px</i>, the shortest solution has 4 turns and begins with the book's two.</figcaption></figure>

## Exercise 5.19 — Coins that must keep moving

> [!question] Exercise 5.19 (book p. 216)
> Coins sit on vertices of a connected undirected graph $G = (V, E)$; in every step **every** coin must move to an adjacent vertex.
>
> (a) Given two vertices $u$ and $v$ (possibly equal) holding the two coins, describe and analyze an algorithm that computes the minimum number of steps until both coins are on the same vertex, or reports that this never happens.
>
> (b) The same for three coins (the book says "both coins" here; it means all three).
>
> (c) With 42 coins, describe an algorithm that decides whether all of them can be brought to the same vertex, in $O(V + E)$ time.

> [!hint]- Hint
> The obvious reduction runs BFS on pairs of positions. There is a faster one: a coin can stand on $x$ after exactly $t$ steps if and only if $t$ is at least the length of the shortest walk to $x$ **with the same parity as $t$** — it can always waste two steps by stepping back and forth.

> [!solution]- Solution
> If $V = 1$, all coins are already together: the answer is 0. Assume $V\ge 2$, so every vertex has an edge.
>
> **Graph.** The **bipartite double cover** $H$ — the parity graph of [[2-algorithms/05-basic-graph-algorithms#57-graph-reductions-flood-fill|§5.7]]: an undirected graph with vertices $V\times\{0, 1\}$ and edges $(x, i)(y, 1 - i)$ for every edge $xy$ of $G$ and $i\in\{0, 1\}$. It has $2V$ vertices and $2E$ edges. A walk in $G$ from $u$ to $x$ of length $\ell$ corresponds to a walk in $H$ from $(u, 0)$ to $(x, \ell\bmod 2)$ of the same length. So the BFS distance $d_u(x, i)$ from $(u, 0)$ to $(x, i)$ in $H$ is the length of a shortest walk from $u$ to $x$ of parity $i$ ($\infty$ if there is none).
>
> **Lemma.** There is a walk with exactly $t$ edges from $u$ to $x$ if and only if $t\ge d_u(x, t\bmod 2)$. *Proof.* "Only if" is the definition of $d_u$. "If": take a shortest walk of parity $t\bmod 2$, and append the steps $x\to y\to x$ along any edge $xy$ until the length is $t$; each round adds 2.
>
> **Problem (a).** Both coins are on $x$ after exactly $t$ steps if and only if each has a walk of length exactly $t$ to $x$, that is, $t\ge\max\{d_u(x, i), d_v(x, i)\}$ with $i = t\bmod 2$. Both distances have parity $i$, so the smallest such $t$ is that maximum. Hence
> $$
> \text{answer} = \min_{x\in V,\ i\in\{0,1\}} \max\{d_u(x, i),\ d_v(x, i)\},
> $$
> and the coins never meet if this is $\infty$ (no $(x, i)$ is reachable from both $(u, 0)$ and $(v, 0)$).
>
> **Algorithm (a).** Breadth-first search in $H$ from $(u, 0)$ and from $(v, 0)$, then one scan over the $2V$ vertices of $H$.
>
> **Time (a).** $O(V + E)$.
>
> **(b)** Same graph and argument with three breadth-first searches, from $(u, 0)$, $(v, 0)$ and $(w, 0)$, and the maximum of three distances: $O(V + E)$.
>
> **(c)** All 42 coins can meet on $x$ after some $t\equiv i\pmod 2$ steps if and only if $(x, i)$ is **reachable** in $H$ from all 42 vertices $(u_j, 0)$ (then $t$ equal to the largest of the 42 distances works). So run whatever-first search in $H$ from each $(u_j, 0)$ and answer whether some vertex of $H$ is marked by all 42 searches: $42\cdot O(V + E) = O(V + E)$. (Equivalently: the answer is yes if $G$ is not bipartite, and otherwise yes exactly when all coins start on the same side.)
>
> **Alternative.** BFS on the configuration graph of pairs $(x, y)$, with an edge for every simultaneous move, also solves (a) — from $(u, v)$ to any $(x, x)$ — but it has $V^2$ vertices and $\sum\deg(x)\deg(y) = 4E^2$ edges: $O(V^2 + E^2)$ time, and $O(V^3 + E^3)$ for (b).
>
> **Answer.** Distances in the double cover $G\times\{0,1\}$: (a) and (b) $\min_{x, i}$ of the largest coin distance to $(x, i)$, (c) a common reachable $(x, i)$; all in $O(V + E)$ time.

### Sources for this page

Exercises 5.1–5.19 of Jeff Erickson, *Algorithms* (2019), pp. 207–216 (CC BY 4.0), paraphrased; the solutions are ours. The book's examples are kept and reproduced (the maze of Figure 5.14, the Vidrach Itky Leda puzzle of Figure 5.16, the walks of Exercises 5.14 and 5.15); the Snakes and Ladders numbers are computed from our reading of Figure 5.15. Two statements needed repair: the Three Seashells puzzle of Figure 5.17 has no solution as printed, and 5.19(b) says "both coins" for three coins. Every claim on this page is checked by `tools/checks/a05x.py`: the graph-theory statements on every graph with up to five or six vertices and on random larger ones; the traversal algorithms under every adjacency order or every choice they allow on small graphs; and every reduction by building the page's graph from random small inputs and comparing its answer with an exhaustive search over move sequences or walks.
