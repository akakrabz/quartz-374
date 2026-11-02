---
title: "Chapter 6 exercises — Depth-First Search"
description: "Solutions to Exercises 6.0–6.13 of Erickson's Algorithms: reversal and the strong component graph, semi-connected graphs, one-way streets, (s,t)-cut vertices in a dag, cut vertices and bridges by low numbers, transitive closure and reduction, Tarry's maze-walking algorithm and a variant that is not depth-first search, keys locked in boxes, recognizing depth-first and breadth-first trees, parallel assignment, and dynamic programming on dags (job scheduling, constrained best paths, counting paths)."
tags: [exercises, algorithms, graphs, midterm-2]
---

*Solved exercises for [[2-algorithms/06-depth-first-search|Chapter 6]] · book pp. 244–251 · statements paraphrased; see the book for the originals*

These are Exercises 6.0–6.13: the depth-first-search exercises that open the list, plus the first two dynamic-programming ones, so that [[concepts/dynamic-programming-on-dags|dynamic programming on dags]] is represented. Skipped: 6.11(b), which would take an unreasonable amount of thought (a temporary variable can be reused, and the book's own example for it is wrong), and 6.14–6.25, beyond the first ten-odd (none of 6.0–6.13 is marked ♥ or ◆). Algorithms built on [[concepts/depth-first-search|depth-first search]] come with the algorithm, its $O(V+E)$ analysis and a correctness proof; modeling problems are written in the graph-reduction rubric's format ([[concepts/graph-reductions]]: graph, problem on the graph, black-box algorithm, time in the input's parameters); dynamic programs in the format of the [[0-toolkit/06-how-exams-are-graded#12-dynamic-programming|DP rubric]]. Three statements are wrong as printed — 6.4(b)ii is inverted, the "only if" half of 6.6(b) is false, and 6.11 claims that a swap-like assignment needs two temporaries when one suffices — and each is pointed out where it occurs. Write your own answer before opening a solution.

> [!tip] Black boxes from the chapter, used below without re-explanation
> - **DFS with clock** ([[2-algorithms/06-depth-first-search#61-preorder-and-postorder|§6.1]]): $O(V+E)$; $u$ is an ancestor of $v$ in the depth-first forest iff $u.\mathit{pre}\le v.\mathit{pre} < v.\mathit{post}\le u.\mathit{post}$ (Lemma 6.1). In a directed graph every edge $u\to v$ is a tree or forward edge ($v$ a descendant of $u$), a back edge ($v$ an ancestor of $u$), or a cross edge with $v.\mathit{post} < u.\mathit{pre}$.
> - **Undirected DFS has no cross edges:** every edge of an undirected graph that is not in the depth-first tree joins an ancestor and a descendant. (If $u.\mathit{pre} < v.\mathit{pre}$, then $v$ is new when $\textsf{DFS}(u)$ starts and the edge $uv$ is a path of new vertices, so $v$ is a descendant of $u$ by Lemma 6.1(d).)
> - **Cycle detection and [[concepts/topological-sort|topological sort]]** ([[2-algorithms/06-depth-first-search#62-detecting-cycles|§6.2]], [[2-algorithms/06-depth-first-search#63-topological-sort|§6.3]]): $\textsf{IsAcyclic}$ and reverse postorder, $O(V+E)$.
> - **[[concepts/strongly-connected-components|Strong components]]** and the strong component graph $\textsf{scc}(G)$ by Kosaraju–Sharir ([[2-algorithms/06-depth-first-search#66-strong-components-in-linear-time|§6.6]]), $O(V+E)$.
> - **Reachability** by [[concepts/whatever-first-search|whatever-first search]] ([[2-algorithms/05-basic-graph-algorithms#55-whatever-first-search|§5.5]]), $O(V+E)$.

## Exercise 6.0 — Reversal and the strong component graph

> [!question] Exercise 6.0 (book p. 244)
> (a) Describe an algorithm that computes the reversal $\textsf{rev}(G)$ of a directed graph $G$ (every edge $u\to v$ replaced by $v\to u$) in $O(V+E)$ time.
>
> (b) Prove that the strong component graph $\textsf{scc}(G)$ is acyclic for every directed graph $G$.
>
> (c) Prove that $\textsf{scc}(\textsf{rev}(G)) = \textsf{rev}(\textsf{scc}(G))$ for every directed graph $G$.
>
> (d) Let $S(v)$ be the strong component of $G$ that contains $v$. Prove that $u$ can reach $v$ in $G$ if and only if $S(u)$ can reach $S(v)$ in $\textsf{scc}(G)$.

### (a) Reversal

> [!hint]- Hint
> One pass over the adjacency lists: the edge $u\to v$, found in $u$'s list, belongs in $v$'s new list.

> [!solution]- Solution
> ```text
> Reverse(G):
>     for each vertex v
>         Radj[v] ← an empty list
>     for each vertex u
>         for each edge u→v
>             append u to Radj[v]
>     return Radj
> ```
>
> Every edge $u\to v$ of $G$ produces exactly the edge $v\to u$, so $\mathit{Radj}$ is the adjacency list of $\textsf{rev}(G)$. Creating the $V$ lists takes $O(V)$ time and each of the $E$ edges costs one $O(1)$ append: $O(V+E)$.
>
> **Answer.** Copy each edge $u\to v$ into $v$'s new list, in $O(V+E)$ time.

### (b), (c), (d) Three facts about the strong component graph

> [!hint]- Hint
> Recall that $\textsf{scc}(G)$ has an edge $C\to C'$ exactly when $C\ne C'$ and $G$ has an edge from a vertex of $C$ to a vertex of $C'$. Prove (d) first by mapping paths back and forth; a cycle of components in (b) would make all their vertices strongly connected.

> [!solution]- Solution
> **(d)** ($\Rightarrow$) Let $u = x_0\to x_1\to\dots\to x_k = v$ be a path in $G$. For each $i$, either $S(x_{i}) = S(x_{i+1})$ or $S(x_i)\to S(x_{i+1})$ is an edge of $\textsf{scc}(G)$; dropping consecutive repetitions from $S(x_0), \dots, S(x_k)$ leaves a walk from $S(u)$ to $S(v)$ in $\textsf{scc}(G)$. ($\Leftarrow$) Let $S(u) = C_0\to C_1\to\dots\to C_k = S(v)$ be a path in $\textsf{scc}(G)$. Each edge $C_{i-1}\to C_i$ comes from an edge $y_i\to z_i$ of $G$ with $y_i\in C_{i-1}$ and $z_i\in C_i$. Inside each component every vertex reaches every other, so $G$ contains walks $u\leadsto y_1$, $z_1\leadsto y_2$, …, $z_{k-1}\leadsto y_k$ and $z_k\leadsto v$; joined by the edges $y_i\to z_i$ they form a walk from $u$ to $v$, which contains a path.
>
> **(b)** Suppose $\textsf{scc}(G)$ had a directed cycle through two different components $C\ne C'$. Pick $u\in C$ and $v\in C'$. Along the cycle $C$ reaches $C'$ and $C'$ reaches $C$, so by (d) $u$ reaches $v$ and $v$ reaches $u$: they are strongly connected and lie in the same component — a contradiction. ($\textsf{scc}(G)$ has no loops, by definition.)
>
> **(c)** A path from $x$ to $y$ in $\textsf{rev}(G)$ is a path from $y$ to $x$ in $G$, read backwards. So "$x$ and $y$ reach each other" means the same in both graphs, and $G$ and $\textsf{rev}(G)$ have the same strong components. For components $C\ne C'$: $\textsf{scc}(\textsf{rev}(G))$ has the edge $C\to C'$ $\iff$ $\textsf{rev}(G)$ has an edge $x\to y$ with $x\in C$, $y\in C'$ $\iff$ $G$ has the edge $y\to x$ $\iff$ $\textsf{scc}(G)$ has $C'\to C$ $\iff$ $\textsf{rev}(\textsf{scc}(G))$ has $C\to C'$.
>
> **Answer.** (d) map paths component by component in both directions; (b) and (c) follow from (d) and from "reversal reverses reachability".

## Exercise 6.1 — Semi-connected graphs

> [!question] Exercise 6.1 (book pp. 244–245)
> A directed graph is **semi-connected** if, for every pair of vertices $u$ and $v$, $u$ can reach $v$ or $v$ can reach $u$ (or both).
>
> (a) Give a dag with a unique source that is not semi-connected.
>
> (b) Describe and analyze an algorithm that decides whether a given dag is semi-connected.
>
> (c) Describe and analyze an algorithm that decides whether an arbitrary directed graph is semi-connected.

### (a) A counterexample

> [!hint]- Hint
> Three vertices suffice.

> [!solution]- Solution
> Vertices $s, a, b$ and edges $s\to a$, $s\to b$. The only source is $s$, but neither of $a$ and $b$ reaches the other.
>
> **Answer.** $s\to a$, $s\to b$.

### (b) Dags

> [!hint]- Hint
> Look at two consecutive vertices of a topological order. Which of them could reach the other, and by which path?

> [!solution]- Solution
> **Algorithm.** Compute a topological order $S[1\,..\,V]$ (reverse postorder) and check that $G$ contains every edge $S[i]\to S[i+1]$:
>
> ```text
> SemiConnectedDag(G):
>     S[1 .. V] ← a topological order of G
>     for i ← 1 to V − 1
>         if S[i]→S[i+1] is not an edge of G
>             return False
>     return True
> ```
>
> **Correctness.** If all these edges exist, the path $S[1]\to S[2]\to\dots\to S[V]$ lets $S[i]$ reach $S[j]$ whenever $i < j$. Conversely, suppose $G$ is semi-connected and fix $i$. Every edge goes forward in the topological order, so everything $S[i+1]$ reaches comes after it; in particular $S[i+1]$ cannot reach $S[i]$, so $S[i]$ reaches $S[i+1]$. The positions increase along that path, from $i$ to $i+1$, so the path is the single edge $S[i]\to S[i+1]$. In other words: **a dag is semi-connected iff it has a Hamiltonian path.**
>
> **Time.** $O(V+E)$ for the topological sort; the edge tests scan each adjacency list once, $O(E)$ in all. (Any topological order works — a semi-connected dag has only one.)
>
> **Answer.** $G$ is semi-connected iff consecutive vertices of a topological order are joined by edges; $O(V+E)$ time.

### (c) Arbitrary directed graphs

> [!hint]- Hint
> Exercise 6.0(d).

> [!solution]- Solution
> Compute $\textsf{scc}(G)$ with Kosaraju–Sharir in $O(V+E)$ time and run $\textsf{SemiConnectedDag}$ on it — it is a dag by Exercise 6.0(b) and has at most $V$ vertices and $E$ edges, so this takes $O(V+E)$ time as well.
>
> **Correctness.** Two vertices of the same component reach each other; for vertices in different components, $u$ reaches $v$ iff $S(u)$ reaches $S(v)$ in $\textsf{scc}(G)$ (Exercise 6.0(d)). So $G$ is semi-connected iff $\textsf{scc}(G)$ is.
>
> **Answer.** Run (b) on $\textsf{scc}(G)$: $O(V+E)$ time.

## Exercise 6.2 — One-way streets

> [!question] Exercise 6.2 (book p. 245)
> Every street of a city is one-way. The mayor claims that one can legally drive from any intersection to any other.
>
> (a) Formalize this problem with graphs, and describe and analyze an algorithm that verifies or refutes the claim.
>
> (b) Call an intersection $x$ **good** if from every intersection $y$ that can be reached legally from $x$, one can legally drive back to $x$. The mayor now claims that over 95% of the intersections are good. Describe and analyze an efficient algorithm that verifies or refutes this claim.
>
> Both algorithms should run in linear time.

### (a) Can everybody get everywhere?

> [!hint]- Hint
> If every intersection can reach one fixed intersection and be reached from it, every intersection can reach every other one.

> [!solution]- Solution
> Let the city have $n$ intersections and $m$ one-way street segments.
>
> **Graph.** $G = (V, E)$, **directed**: one vertex per intersection, and an edge $u\to v$ for each street segment that leads directly from intersection $u$ to intersection $v$ in its legal direction. $V = n$, $E = m$.
>
> **Problem.** The claim says that $G$ is **strongly connected**: every vertex can reach every other vertex.
>
> **Algorithm.** Pick any vertex $s$. Run whatever-first search from $s$ in $G$ and from $s$ in $\textsf{rev}(G)$ (Exercise 6.0(a)). The claim is true iff both searches mark all $n$ vertices. Correctness: if every vertex is reachable from $s$ and every vertex can reach $s$ (searching $\textsf{rev}(G)$ finds exactly the vertices that reach $s$ in $G$), then any $x$ reaches any $y$ through $s$; if some vertex is missed, it is not reachable from $s$ or cannot reach $s$, and the claim fails for that pair.
>
> **Time.** Building $G$ and its reversal and two searches: $O(n+m)$.
>
> **Answer.** Strong connectivity, decided by two whatever-first searches from one vertex, in $G$ and in $\textsf{rev}(G)$: $O(n+m)$ time.

### (b) Good intersections

> [!hint]- Hint
> Where can a good vertex's strong component sit in $\textsf{scc}(G)$?

> [!solution]- Solution
> **Claim.** $x$ is good iff its strong component $S(x)$ is a **sink component**, a sink of $\textsf{scc}(G)$. If $S(x)$ has an edge to another component $C'$, then $x$ reaches the vertices of $C'$ (Exercise 6.0(d)), and they cannot reach $x$ — otherwise they would be strongly connected to $x$ and lie in $S(x)$. If $S(x)$ is a sink, everything $x$ reaches lies in $S(x)$ (again by 6.0(d)) and can reach $x$.
>
> **Algorithm.** With $G$ as in (a): compute the strong components and $\textsf{scc}(G)$ with Kosaraju–Sharir, mark the components with no outgoing edge in $\textsf{scc}(G)$, and let $g$ be the total number of vertices in them. The claim holds iff $g > 0.95\,n$, that is, iff $20g > 19n$.
>
> **Time.** $O(n+m)$.
>
> **Answer.** The good intersections are exactly those in sink components of $\textsf{scc}(G)$; count them in $O(n+m)$ time.

## Exercise 6.3 — (s,t)-cut vertices in a dag

> [!question] Exercise 6.3 (book p. 245)
> $G$ is a dag with a unique source $s$ and a unique sink $t$. A vertex $v\notin\{s, t\}$ is an **$(s,t)$-cut vertex** if every path from $s$ to $t$ passes through $v$ — equivalently, if deleting $v$ makes $t$ unreachable from $s$. Describe and analyze an algorithm that finds every $(s,t)$-cut vertex of $G$. (The book's Figure 6.20 shows a dag with three of them.)

> [!hint]- Hint
> Lay the vertices out in topological order. An edge from position $i$ to position $j$ "jumps over" every vertex strictly between them.

> [!solution]- Solution
> **Setup.** Fix a topological order $S[1\,..\,V]$ and write $\mathit{pos}(v)$ for the position of $v$. Every vertex except $s$ has an incoming edge and every vertex except $t$ an outgoing one, so $S[1] = s$, $S[V] = t$, every vertex is reachable from $s$ (walk backwards along incoming edges until you reach the only source) and every vertex reaches $t$. Say that the edge $u\to w$ **jumps over** $v$ if $\mathit{pos}(u) < \mathit{pos}(v) < \mathit{pos}(w)$.
>
> **Claim.** A vertex $v\notin\{s,t\}$ is an $(s,t)$-cut vertex iff no edge jumps over it.
>
> - If $u\to w$ jumps over $v$, the path $s\leadsto u\to w\leadsto t$ avoids $v$: positions increase along every path, so the vertices of $s\leadsto u$ sit at positions $\le\mathit{pos}(u) < \mathit{pos}(v)$ and those of $w\leadsto t$ at positions $\ge\mathit{pos}(w) > \mathit{pos}(v)$.
> - If no edge jumps over $v$, take any path from $s$ to $t$ and its first edge $x\to y$ with $\mathit{pos}(y)\ge\mathit{pos}(v)$ (it exists because $\mathit{pos}(t) > \mathit{pos}(v) > \mathit{pos}(s)$). Then $\mathit{pos}(x) < \mathit{pos}(v)\le\mathit{pos}(y)$, and since $x\to y$ does not jump over $v$, $y = v$. Every path passes through $v$.
>
> **Algorithm.** Sweep the order once, remembering the farthest position reached so far by an edge:
>
> ```text
> STCutVertices(G):
>     S[1 .. V] ← a topological order of G
>     for i ← 1 to V
>         pos(S[i]) ← i
>     far ← 1
>     for i ← 1 to V
>         if 1 < i < V and far ≤ i
>             report S[i]              ⟨⟨no edge jumps over S[i]⟩⟩
>         for each edge S[i]→w
>             far ← max{far, pos(w)}
> ```
>
> At the test, $\mathit{far}$ is the largest position of an edge's head among the edges leaving $S[1\,..\,i-1]$, so some edge jumps over $S[i]$ iff $\mathit{far} > i$.
>
> **Time.** $O(V+E)$: one topological sort and one pass over all adjacency lists.
>
> **Answer.** The cut vertices are the vertices that no edge jumps over in a topological order; one sweep, $O(V+E)$ time.

<!-- fig:a06x-cut-dag -->
<figure class="cs-fig"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 636 160" width="636" height="160" role="img" style="font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-size:14px"><title>twelve vertices on a line with eleven arcs above; three vertices are not covered by any arc</title><defs><marker id="ARR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs><line x1="38" y1="104" x2="64.5" y2="104" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" marker-end="url(#ARR)"/><path d="M31.6,93.4 C47.2,49.4 110.8,49.4 125.2,91.2" fill="none" stroke="var(--accent)" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><line x1="91" y1="104" x2="117.5" y2="104" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" marker-end="url(#ARR)"/><line x1="144" y1="104" x2="170.5" y2="104" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" marker-end="url(#ARR)"/><path d="M137.6,93.4 C153.2,49.4 216.8,49.4 231.2,91.2" fill="none" stroke="var(--accent)" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M137.6,93.4 C163.8,20.8 259.2,20.8 284.2,91.2" fill="none" stroke="var(--accent)" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M137.6,93.4 C174.4,-7.8 301.6,-7.8 337.2,91.2" fill="none" stroke="var(--accent)" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><line x1="197" y1="104" x2="223.5" y2="104" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" marker-end="url(#ARR)"/><path d="M190.6,93.4 C216.8,20.8 312.2,20.8 337.2,91.2" fill="none" stroke="var(--accent)" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M190.6,93.4 C206.2,49.4 269.8,49.4 284.2,91.2" fill="none" stroke="var(--accent)" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><line x1="250" y1="104" x2="276.5" y2="104" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" marker-end="url(#ARR)"/><path d="M243.6,93.4 C259.2,49.4 322.8,49.4 337.2,91.2" fill="none" stroke="var(--accent)" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><line x1="303" y1="104" x2="329.5" y2="104" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" marker-end="url(#ARR)"/><line x1="356" y1="104" x2="382.5" y2="104" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" marker-end="url(#ARR)"/><path d="M349.6,93.4 C365.2,49.4 428.8,49.4 443.2,91.2" fill="none" stroke="var(--accent)" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M349.6,93.4 C375.8,20.8 471.2,20.8 496.2,91.2" fill="none" stroke="var(--accent)" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><line x1="409" y1="104" x2="435.5" y2="104" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" marker-end="url(#ARR)"/><path d="M402.6,93.4 C418.2,49.4 481.8,49.4 496.2,91.2" fill="none" stroke="var(--accent)" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><line x1="462" y1="104" x2="488.5" y2="104" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" marker-end="url(#ARR)"/><line x1="515" y1="104" x2="541.5" y2="104" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" marker-end="url(#ARR)"/><path d="M508.6,93.4 C524.2,49.4 587.8,49.4 602.2,91.2" fill="none" stroke="var(--accent)" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><line x1="568" y1="104" x2="594.5" y2="104" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" marker-end="url(#ARR)"/><circle cx="26" cy="104" r="12" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="26" y="105" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">s</text><text x="26" y="130" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">1</text><circle cx="79" cy="104" r="12" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="79" y="105" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">f</text><text x="79" y="130" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">2</text><circle cx="132" cy="104" r="12" fill="var(--hi)" fill-opacity="0.28" stroke="var(--hi)" stroke-width="2.2"/><text x="132" y="105" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">g</text><text x="132" y="130" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">3</text><circle cx="185" cy="104" r="12" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="185" y="105" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">a</text><text x="185" y="130" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">4</text><circle cx="238" cy="104" r="12" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="238" y="105" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">b</text><text x="238" y="130" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">5</text><circle cx="291" cy="104" r="12" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="291" y="105" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">h</text><text x="291" y="130" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">6</text><circle cx="344" cy="104" r="12" fill="var(--hi)" fill-opacity="0.28" stroke="var(--hi)" stroke-width="2.2"/><text x="344" y="105" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">c</text><text x="344" y="130" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">7</text><circle cx="397" cy="104" r="12" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="397" y="105" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">d</text><text x="397" y="130" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">8</text><circle cx="450" cy="104" r="12" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="450" y="105" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">i</text><text x="450" y="130" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">9</text><circle cx="503" cy="104" r="12" fill="var(--hi)" fill-opacity="0.28" stroke="var(--hi)" stroke-width="2.2"/><text x="503" y="105" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">j</text><text x="503" y="130" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">10</text><circle cx="556" cy="104" r="12" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="556" y="105" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">e</text><text x="556" y="130" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">11</text><circle cx="609" cy="104" r="12" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="609" y="105" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">t</text><text x="609" y="130" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">12</text><text x="317.5" y="150" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">position in the topological order</text></svg><figcaption><strong>Cut vertices are the ones no edge jumps over.</strong> The dag of the book's Figure 6.20, drawn in the topological order <i>s f g a b h c d i j e t</i>. Eleven edges join consecutive vertices (black); the other eleven (blue arcs) jump over every vertex strictly between their endpoints. Only <i>g</i>, <i>c</i> and <i>j</i> lie under no arc, so they are the (<i>s</i>, <i>t</i>)-cut vertices, as in the book.</figcaption></figure>

## Exercise 6.4 — Cut vertices

> [!question] Exercise 6.4 (book pp. 245–246)
> A vertex $v$ of a connected undirected graph $G$ is a **cut vertex** if $G - v$ (delete $v$ and its edges) is disconnected. (The book's Figure 6.21 shows a graph with four of them.)
>
> (a) Describe a linear-time algorithm that decides, given $G$ and a vertex $v$, whether $v$ is a cut vertex. How long does it take to find all cut vertices by running it for each vertex?
>
> (b) Let $T$ be a depth-first spanning tree of $G$.
> - i. Prove that the root of $T$ is a cut vertex iff it has more than one child in $T$.
> - ii. Prove that a non-root vertex $v$ is a cut vertex iff **some child $c$ of $v$ has no descendant (in $T$, including $c$) that is a neighbor (in $G$) of a proper ancestor of $v$**.
>
>
> (The book's hint: both claims fail if $T$ is not a depth-first tree, or if $G$ is directed.)
>
> (c) Describe an algorithm that finds every cut vertex in $O(V+E)$ time.
>
> **Correction.** The book's part ii reads "…iff at least one descendant of *each* child of $v$ is a neighbor of some proper ancestor of $v$". That is exactly the condition for $v$ **not** to be a cut vertex — a leaf of $T$ satisfies it vacuously and is never a cut vertex. Part ii above is the corrected statement.

### (a) One vertex at a time

> [!hint]- Hint
> Search $G - v$ without building it.

> [!solution]- Solution
> Start a whatever-first search at any vertex other than $v$, treating $v$ as already marked (so its edges are never followed), and count the marked vertices: $v$ is a cut vertex iff fewer than $V - 1$ are marked. This is one search of $G - v$, $O(V+E)$ time. Repeating it for all $V$ vertices takes $O(V(V+E)) = O(VE)$ time, since $E\ge V-1$ in a connected graph.
>
> **Answer.** One search of $G - v$, $O(V+E)$; all vertices this way, $O(VE)$.

### (b) Cut vertices and depth-first trees

> [!hint]- Hint
> Undirected DFS has no cross edges. So an edge that leaves the subtree $T_c$ of a vertex $c$ goes either to the parent of $c$ or to a proper ancestor of $c$.

> [!solution]- Solution
> Let $T_c$ be the subtree of $T$ rooted at $c$ and $r$ the root. **Key fact:** every edge of $G$ with exactly one endpoint in $T_c$ is the tree edge from $c$ to its parent or joins a vertex of $T_c$ to a proper ancestor of $c$. Indeed, a non-tree edge $xy$ with $x\in T_c$ joins an ancestor and a descendant of $x$ (black box); descendants of $x$ lie in $T_c$, and the ancestors of $x$ outside $T_c$ are the proper ancestors of $c$.
>
> **i.** If $r$ has two children $c_1\ne c_2$, every edge leaving $T_{c_1}$ goes to $r$, the only proper ancestor of $c_1$ (key fact). So in $G - r$ no edge leaves $T_{c_1}$, while $T_{c_2}$ lies outside it: $G - r$ is disconnected. If $r$ has exactly one child $c$, then $T_c = T - r$ is a spanning tree of $G - r$, so $G - r$ is connected. (If $r$ has no child, $G$ is a single vertex and $G - r$ is empty, which does not count as disconnected.)
>
> **ii.** ($\Leftarrow$) Suppose no vertex of $T_c$ is adjacent to a proper ancestor of $v$. By the key fact every edge leaving $T_c$ goes to $v$ or to a proper ancestor of $c$ — that is, to $v$ or a proper ancestor of $v$ — and only $v$ remains. So in $G - v$ no edge leaves $T_c$, while $r\notin T_c\cup\{v\}$: $G - v$ is disconnected. ($\Rightarrow$, contrapositive) Suppose every child $c$ of $v$ has a vertex of $T_c$ adjacent to a proper ancestor of $v$. In $G - v$, the vertices outside $T_v$ form a subtree of $T$ (containing $r$), hence a connected set $A$; each $T_c$ is connected, and an edge joins it to a proper ancestor of $v$, which lies in $A$. Every vertex of $G - v$ is in $A$ or in some $T_c$, so $G - v$ is connected.
>
> **Why "depth-first" matters.** In the 4-cycle $1\,2\,3\,4$, a breadth-first tree from $1$ has two children at the root, $2$ and $4$, yet $G - 1$ is the path $2\,3\,4$: claim i fails because the non-tree edge at $3$ joins the two subtrees.
>
> **Answer.** i: two children of the root share no edge, one child spans $G - r$. ii: $v$ is a cut vertex iff some child's subtree has no edge to a proper ancestor of $v$ — not "each child's subtree has such an edge", as printed.

### (c) All cut vertices in linear time

> [!hint]- Hint
> Part ii in numbers: let $v.\mathit{low}$ be the smallest starting time reachable from the subtree of $v$ by one non-tree edge. Compute it in postorder.

> [!solution]- Solution
> **Low numbers.** For the depth-first tree $T$ of one DFS, define $v.\mathit{low}$ as the smallest of $v.\mathit{pre}$ and the starting times $y.\mathit{pre}$ of all vertices $y$ joined by a **non-tree** edge to some vertex of $T_v$. It satisfies
> $$
> v.\mathit{low} = \min\Big(\{v.\mathit{pre}\}\cup\{w.\mathit{pre}\mid vw \text{ a non-tree edge}\}\cup\{c.\mathit{low}\mid c \text{ a child of } v\}\Big).
> $$
>
> **Test.** A non-root vertex $v$ is a cut vertex iff some child $c$ has $c.\mathit{low}\ge v.\mathit{pre}$. By part ii it suffices that $c.\mathit{low} < v.\mathit{pre}$ iff some vertex of $T_c$ is adjacent to a proper ancestor of $v$. The non-tree edges from $x\in T_c$ go to ancestors or descendants of $x$, that is, into $T_c$ or to $v$ (starting times $\ge v.\mathit{pre}$) or to proper ancestors of $v$ (starting times $< v.\mathit{pre}$). The root is handled by part i.
>
> ```text
> CutVertices(G):
>     clock ← 0; unmark every vertex
>     r ← any vertex
>     CutDFS(r, None)
>     if r has at least two children
>         report r
>
> CutDFS(v, p):                        ⟨⟨p = parent of v⟩⟩
>     mark v
>     clock ← clock + 1; v.pre ← clock; v.low ← v.pre
>     for each edge vw
>         if w is unmarked                     ⟨⟨tree edge: w is a child⟩⟩
>             CutDFS(w, v)
>             v.low ← min{v.low, w.low}
>             if p ≠ None and w.low ≥ v.pre
>                 report v                     ⟨⟨w's subtree hangs on v⟩⟩
>         else if w ≠ p                        ⟨⟨non-tree edge⟩⟩
>             v.low ← min{v.low, w.pre}
> ```
>
> (A vertex may be reported once per child that hangs on it; report it only the first time.) The test `w ≠ p` skips the tree edge to the parent; the graph is simple, so no other edge goes to $p$. This is ordinary DFS with $O(1)$ extra work per edge: **$O(V+E)$ time.**
>
> **Answer.** One DFS computing $v.\mathit{low}$; report the root if it has two children and a non-root $v$ if some child $c$ has $c.\mathit{low}\ge v.\mathit{pre}$; $O(V+E)$ time.

<!-- fig:a06x-low -->
<figure class="cs-fig"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 650 272" width="650" height="272" role="img" style="font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-size:14px"><title>a thirteen-vertex undirected graph with a depth-first tree, pre and low labels, four cut vertices and one bridge</title><defs><marker id="ARR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs><line x1="40" y1="82" x2="40" y2="168" stroke="var(--accent)" stroke-width="3.0" stroke-linecap="round"/><line x1="48.3" y1="78.7" x2="136.7" y2="171.3" stroke="var(--muted)" stroke-width="1.2" stroke-linecap="round" stroke-dasharray="4 3"/><line x1="52" y1="180" x2="133" y2="180" stroke="var(--accent)" stroke-width="3.0" stroke-linecap="round"/><line x1="157" y1="70" x2="238" y2="70" stroke="var(--accent)" stroke-width="3.0" stroke-linecap="round"/><line x1="145" y1="82" x2="145" y2="168" stroke="var(--accent)" stroke-width="3.0" stroke-linecap="round"/><line x1="153.3" y1="78.7" x2="241.7" y2="171.3" stroke="var(--muted)" stroke-width="1.2" stroke-linecap="round" stroke-dasharray="4 3"/><line x1="156.6" y1="73" x2="343.4" y2="122" stroke="var(--muted)" stroke-width="1.2" stroke-linecap="round" stroke-dasharray="4 3"/><line x1="241.7" y1="78.7" x2="153.3" y2="171.3" stroke="var(--muted)" stroke-width="1.2" stroke-linecap="round" stroke-dasharray="4 3"/><line x1="250" y1="82" x2="250" y2="168" stroke="var(--accent)" stroke-width="3.0" stroke-linecap="round"/><line x1="260.6" y1="75.6" x2="344.4" y2="119.4" stroke="var(--muted)" stroke-width="1.2" stroke-linecap="round" stroke-dasharray="4 3"/><line x1="157" y1="180" x2="238" y2="180" stroke="var(--muted)" stroke-width="1.2" stroke-linecap="round" stroke-dasharray="4 3"/><line x1="156.6" y1="177" x2="343.4" y2="128" stroke="var(--muted)" stroke-width="1.2" stroke-linecap="round" stroke-dasharray="4 3"/><line x1="260.6" y1="174.4" x2="344.4" y2="130.6" stroke="var(--accent)" stroke-width="3.0" stroke-linecap="round"/><line x1="260.5" y1="185.8" x2="344.5" y2="232.2" stroke="var(--hi)" stroke-width="3.4" stroke-linecap="round"/><line x1="364.4" y1="117.6" x2="430.6" y2="65.4" stroke="var(--accent)" stroke-width="3.0" stroke-linecap="round"/><line x1="364.4" y1="132.4" x2="430.6" y2="184.6" stroke="var(--muted)" stroke-width="1.2" stroke-linecap="round" stroke-dasharray="4 3"/><line x1="367" y1="125" x2="508" y2="125" stroke="var(--muted)" stroke-width="1.2" stroke-linecap="round" stroke-dasharray="4 3"/><line x1="440" y1="70" x2="440" y2="180" stroke="var(--accent)" stroke-width="3.0" stroke-linecap="round"/><line x1="449.2" y1="65.7" x2="510.8" y2="117.3" stroke="var(--muted)" stroke-width="1.2" stroke-linecap="round" stroke-dasharray="4 3"/><line x1="449.2" y1="184.3" x2="510.8" y2="132.7" stroke="var(--accent)" stroke-width="3.0" stroke-linecap="round"/><line x1="529.2" y1="117.3" x2="590.8" y2="65.7" stroke="var(--accent)" stroke-width="3.0" stroke-linecap="round"/><line x1="529.2" y1="132.7" x2="590.8" y2="184.3" stroke="var(--muted)" stroke-width="1.2" stroke-linecap="round" stroke-dasharray="4 3"/><line x1="600" y1="70" x2="600" y2="180" stroke="var(--accent)" stroke-width="3.0" stroke-linecap="round"/><circle cx="40" cy="70" r="12" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="40" y="71" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">a</text><text x="40" y="46" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">1/1</text><circle cx="40" cy="180" r="12" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="40" y="181" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">b</text><text x="40" y="204" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">2/1</text><circle cx="145" cy="70" r="12" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="145" y="71" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">c</text><text x="145" y="46" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">4/3</text><circle cx="145" cy="180" r="12" fill="var(--hi)" fill-opacity="0.28" stroke="var(--hi)" stroke-width="2.2"/><text x="145" y="181" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">d</text><text x="145" y="204" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">3/1</text><circle cx="250" cy="70" r="12" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="250" y="71" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">e</text><text x="250" y="46" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">5/3</text><circle cx="250" cy="180" r="12" fill="var(--hi)" fill-opacity="0.28" stroke="var(--hi)" stroke-width="2.2"/><text x="250" y="181" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">f</text><text x="242" y="205" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">6/3</text><circle cx="355" cy="125" r="12" fill="var(--hi)" fill-opacity="0.28" stroke="var(--hi)" stroke-width="2.2"/><text x="355" y="126" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">g</text><text x="347" y="100" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">7/3</text><circle cx="355" cy="238" r="12" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="355" y="239" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">h</text><text x="389" y="238" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">13/13</text><circle cx="440" cy="58" r="12" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="440" y="59" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">i</text><text x="440" y="34" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">8/7</text><circle cx="440" cy="192" r="12" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="440" y="193" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">j</text><text x="440" y="216" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">9/7</text><circle cx="520" cy="125" r="12" fill="var(--hi)" fill-opacity="0.28" stroke="var(--hi)" stroke-width="2.2"/><text x="520" y="126" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">k</text><text x="528" y="100" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">10/7</text><circle cx="600" cy="58" r="12" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="600" y="59" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">l</text><text x="600" y="34" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">11/10</text><circle cx="600" cy="192" r="12" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="600" y="193" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">m</text><text x="600" y="216" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">12/10</text><text x="325" y="264" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">label: pre/low · thick: DFS tree from a · dashed: non-tree edges</text></svg><figcaption><strong>Low numbers find cut vertices and bridges.</strong> The graph of the book's Figure 6.21 (our labels), searched from <i>a</i> with alphabetical adjacency lists; each vertex shows <i>v.pre</i>/<i>v.low</i>. A non-root vertex is a cut vertex when some child has low ≥ its own pre: <i>d</i> (child <i>c</i>, low 3), <i>f</i> (child <i>h</i>, low 13), <i>g</i> (child <i>i</i>, low 7) and <i>k</i> (child <i>l</i>, low 10). The root <i>a</i> has one child, so it is not. The only tree edge with <i>v.low</i> = <i>v.pre</i> is <i>fh</i>, the only bridge.</figcaption></figure>

## Exercise 6.5 — Bridges

> [!question] Exercise 6.5 (book p. 246)
> An edge $e$ of a connected undirected graph $G$ is a **bridge** (or **cut edge**) if $G - e$ is disconnected.
>
> (a) Describe a linear-time algorithm that decides whether a given edge $e$ is a bridge. How long does finding all bridges this way take?
>
> (b) Let $T$ be any spanning tree of $G$. Prove that every bridge of $G$ is an edge of $T$, so $G$ has at most $V-1$ bridges. How does this improve the algorithm of (a)?
>
> (c) Root $T$ at any vertex, and let $T_v$ be the subtree rooted at $v$. Let $uv$ be an edge of $T$, $u$ the parent of $v$. Prove that $uv$ is a bridge iff it is the only edge of $G$ with exactly one endpoint in $T_v$.
>
> (d) Describe a linear-time algorithm that finds every bridge. (Hint: let $T$ be a depth-first tree.)

### (a), (b) and (c) Bridges and spanning trees

> [!hint]- Hint
> (a) $G - uv$ is disconnected iff $u$ can no longer reach $v$. (b) A spanning tree that avoids $e$ keeps $G - e$ connected. (c) $T_v$ and the rest of $T$ are both connected.

> [!solution]- Solution
> **(a)** Let $e = uv$. Every vertex reaches $u$ or $v$ in $G - e$ (cut a path to $u$ in $G$ just before it first uses $e$), so $G - e$ is disconnected iff $v$ is unreachable from $u$ in $G - e$. Run whatever-first search from $u$, skipping the edge $e$: $O(V+E)$ time. For all $E$ edges: $O(E(V+E)) = O(E^2)$ time, as $V\le E+1$.
>
> **(b)** If a bridge $e$ were not in $T$, then $T$ would be a connected spanning subgraph of $G - e$, and $G - e$ would be connected — a contradiction. So the bridges are among the $V-1$ edges of $T$. Find one spanning tree with one search, then test only its edges with (a): $O(V(V+E)) = O(VE)$ time instead of $O(E^2)$.
>
> **(c)** ($\Leftarrow$) If $uv$ is the only edge with exactly one endpoint in $T_v$, then $G - uv$ has no edge between $T_v$ and the other vertices, a non-empty set that contains $u$: disconnected. ($\Rightarrow$, contrapositive) Suppose another edge $xy$ has $x\in T_v$ and $y\notin T_v$. In $G - uv$, $T_v$ is connected (a subtree), the vertices outside $T_v$ are connected ($T$ minus the subtree $T_v$ is still a tree), and $xy$ joins the two parts: $G - uv$ is connected.
>
> **Answer.** (a) one search of $G - e$, $O(V+E)$; all edges $O(E^2)$. (b) only tree edges can be bridges, so $O(VE)$. (c) as proved.

### (d) All bridges in linear time

> [!hint]- Hint
> With a depth-first tree, the only edges that can leave $T_v$ besides the tree edge are back edges to proper ancestors of $v$ — the low numbers of Exercise 6.4(c) see them.

> [!solution]- Solution
> Run $\textsf{CutDFS}$ of Exercise 6.4(c) (same $v.\mathit{low}$, with the tree edge to the parent excluded), and after each recursive call $\textsf{CutDFS}(w, v)$ add the test
>
> ```text
>             if w.low = w.pre
>                 report the bridge vw
> ```
>
> **Correctness.** Let $vw$ be a tree edge, $v$ the parent of $w$. By the key fact of 6.4(b), the edges other than $vw$ with exactly one endpoint in $T_w$ are non-tree edges from $T_w$ to proper ancestors of $w$ — vertices with starting time $< w.\mathit{pre}$. Such an edge exists iff $w.\mathit{low} < w.\mathit{pre}$. By (c), $vw$ is a bridge iff $w.\mathit{low} = w.\mathit{pre}$. Non-tree edges are never bridges, by (b).
>
> **Time.** One DFS: $O(V+E)$.
>
> **Trap.** The tree edge to the parent must not count in $v.\mathit{low}$. If it did (as when Figure 6.18's $\textsf{FindLowDFS}$ is run on an undirected graph), then $w.\mathit{low}\le v.\mathit{pre} < w.\mathit{pre}$ always and no bridge is ever reported; the cut-vertex test of 6.4(c) happens to survive that change.
>
> **Answer.** The tree edge $vw$ ($v$ the parent) is a bridge iff $w.\mathit{low} = w.\mathit{pre}$; one DFS, $O(V+E)$ time. In the graph of Figure 6.21 the only bridge is the edge to the pendant vertex $h$.

## Exercise 6.6 — Transitive closure and reduction

> [!question] Exercise 6.6 (book pp. 246–247)
> The **transitive closure** $G^T$ of a directed graph $G$ has the same vertices and an edge $u\to v$ iff $G$ has a directed path from $u$ to $v$ (we consider $u\ne v$ only). A **transitive reduction** of $G$ is a graph with as few edges as possible whose transitive closure is $G^T$; it need not be a subgraph of $G$, and a graph can have several.
>
> (a) Describe an efficient algorithm that computes the transitive closure of a directed graph.
>
> (b) Prove that $G$ has a unique transitive reduction iff $G$ is acyclic. **As printed, the "only if" half is false** — see the solution.
>
> (c) Describe an efficient algorithm that computes a transitive reduction of a directed graph.

### (a) Closure

> [!hint]- Hint
> The closure's edges out of $u$ are exactly $\textsf{reach}(u)$.

> [!solution]- Solution
> For every vertex $u$, run whatever-first search from $u$ and add $u\to v$ for every marked $v\ne u$. Each search finds exactly $\textsf{reach}(u)$. Time: $V$ searches, $O(V(V+E))$. (The closure itself can have $\Theta(V^2)$ edges, so $O(V^2)$ is unavoidable when $E$ is small.)
>
> **Answer.** One search from every vertex: $O(V(V+E))$ time.

### (b) When is the reduction unique?

> [!hint]- Hint
> In a dag, call an edge $u\to v$ **essential** if it is the only path from $u$ to $v$. Show that every graph with the same closure contains every essential edge, and that the essential edges alone already have the right closure. For the converse, try the smallest cyclic graphs.

> [!solution]- Solution
> **If $G$ is a dag, its transitive reduction is unique.** Call an edge $u\to v$ of $G$ *essential* if $G$ has no other path from $u$ to $v$, and let $R$ be the set of essential edges.
>
> - *Every graph $H$ with $H^T = G^T$ contains $R$.* Let $u\to v\in R$. $H$ has a path from $u$ to $v$. If it had an intermediate vertex $w$, then $G$ would have paths $u\leadsto w$ and $w\leadsto v$ (same closure), and their concatenation would be a second path from $u$ to $v$ in $G$ (in a dag a walk cannot repeat a vertex) — so $u\to v$ would not be essential. Hence the path in $H$ is the edge $u\to v$ itself.
> - *$R^T = G^T$.* Since $R\subseteq G$, $R^T\subseteq G^T$; conversely it suffices that every edge $u\to v$ of $G$ is in $R^T$. Take a **longest** path $P$ from $u$ to $v$ in $G$. Each edge $x\to y$ of $P$ is essential: another path from $x$ to $y$ would be longer than one edge and would lengthen $P$. So $P\subseteq R$.
>
> So the minimum number of edges is $\lvert R\rvert$, and the only graph with that many edges and closure $G^T$ is $R$.
>
> **The converse is false as printed.** The 2-cycle $u\to v\to u$ is not acyclic, yet it is its own unique transitive reduction: any graph on $\{u, v\}$ in which $u$ reaches $v$ and $v$ reaches $u$ contains both edges. What *is* true: if some strong component $C$ has $k\ge 3$ vertices, the reduction is not unique — inside $C$ any of the $(k-1)!$ directed Hamiltonian cycles of $C$ can be used (for example $a\to b\to c\to a$ and $a\to c\to b\to a$ have the same closure). Part (c) yields the exact statement: **the transitive reduction is unique iff every strong component has at most two vertices and every two-vertex component has no edge to or from the rest of $G$.**
>
> **Answer.** Dags: the essential edges are the unique reduction. The "only if" fails for $u\to v\to u$; it holds as soon as a strong component has three or more vertices.

### (c) Computing a reduction

> [!hint]- Hint
> Inside a strong component, a cycle is the cheapest way to connect everything. Between components, use the essential edges of the dag $\textsf{scc}(G)$, each realized by one edge.

> [!solution]- Solution
> **Algorithm.**
> 1. Compute the strong components and $\textsf{scc}(G)$ with Kosaraju–Sharir: $O(V+E)$.
> 2. Compute the closure of the dag $\textsf{scc}(G)$ with (a) and keep the edges $C\to C'$ of $\textsf{scc}(G)$ such that no **other** out-neighbor of $C$ reaches $C'$ — the essential edges; call them $R$. Time $O(V(V+E))$ for the closure plus $\sum_C \deg^+(C)^2\le VE$ lookups.
> 3. Output $H$: for each component $C = \{c_1, \dots, c_k\}$ with $k\ge 2$ the cycle $c_1\to c_2\to\dots\to c_k\to c_1$, and for each $C\to C'$ in $R$ one edge from an arbitrary vertex of $C$ to an arbitrary vertex of $C'$.
>
> Total time $O(V(V+E))$. For a dag, steps 1 and 3 do nothing: the answer is $R$, as in (b).
>
> **Same closure.** The strong components of $H$ are those of $G$ (each is a cycle or a single vertex, and $R$ is acyclic), and $C$ reaches $C'$ through $R$ iff it does in $\textsf{scc}(G)$, by (b) applied to the dag $\textsf{scc}(G)$. By Exercise 6.0(d), applied to both $H$ and $G$, $u$ reaches $v$ in $H$ iff $S(u)$ reaches $S(v)$ iff $u$ reaches $v$ in $G$.
>
> **Fewest edges.** Let $H'$ be any graph with $H'^T = G^T$.
> - For each component $C$ with $k\ge 2$ vertices, $H'$ has at least $k$ edges inside $C$: every vertex on an $H'$-path between two vertices of $C$ is reachable from $C$ and reaches $C$, so it lies in $C$; hence $H'$ restricted to $C$ is strongly connected, and then every vertex of $C$ needs an outgoing edge inside $C$.
> - For each $C\to C'$ in $R$, $H'$ has an edge from $C$ to $C'$: an $H'$-path from $C$ to $C'$ leaves $C$ along an edge into some component $D$; then $C$ reaches $D$ and $D$ reaches $C'$ in $G$, and $D\ne C'$ would give a second path $C\leadsto D\leadsto C'$ in $\textsf{scc}(G)$.
>
> These edge sets are disjoint, so $\lvert H'\rvert\ge\sum_{\lvert C\rvert\ge 2}\lvert C\rvert + \lvert R\rvert = \lvert H\rvert$.
>
> **Counting reductions.** Equality forces exactly a Hamiltonian cycle inside each component and exactly one edge for each edge of $R$, with free endpoints. So $G$ has exactly $\prod_C (\lvert C\rvert-1)!\cdot\prod_{C\to C'\in R}\lvert C\rvert\,\lvert C'\rvert$ transitive reductions. This is 1 iff no component has three or more vertices and every edge of $R$ joins two single vertices; a component with any edge in or out of it in $\textsf{scc}(G)$ is an endpoint of some edge of $R$ (its out-neighbor that comes first in topological order is reached by no other path, and symmetrically for in-neighbors). That is the characterization stated in (b).
>
> **Answer.** A cycle through each strong component plus one edge per essential edge of $\textsf{scc}(G)$, in $O(V(V+E))$ time; for a dag, the essential edges.

## Exercise 6.7 — Tarry's algorithm

> [!question] Exercise 6.7 (book pp. 247–248)
> Tarry's maze-walking algorithm (1895) runs on a connected undirected graph $G$ in which each edge $uv$ is split into two **arcs** $u\to v$ and $v\to u$, so each vertex has $\deg(v)$ arcs out and $\deg(v)$ arcs in. All vertices start unmarked and all arcs white.
>
> ```text
> Tarry(G):
>     s ← any vertex; RecTarry(s)
>
> RecTarry(v):
>     mark v                                 ⟨⟨"visit v"⟩⟩
>     if some arc v→w is white
>         if w is unmarked
>             color w→v green
>         color v→w red; RecTarry(w)         ⟨⟨"traverse v→w"⟩⟩
>     else if some arc v→w is green
>         color v→w red; RecTarry(w)         ⟨⟨"traverse v→w"⟩⟩
> ```
>
> A vertex can be visited (marked) several times.
>
> - (a) Describe how to implement Tarry's algorithm in $O(V+E)$ time.
> - (b) Prove that no arc is traversed more than once.
> - (c) When $v$ is visited for the $k$th time, exactly how many arcs into $v$ and out of $v$ are red? (Treat the start vertex $s$ separately.)
> - (d) Prove that $v$ is visited at most $\deg(v)$ times, except $s$, which is visited at most $\deg(s)+1$ times. So $\textsf{Tarry}$ halts.
> - (e) Prove that the last vertex visited is $s$.
> - (f) Prove that all arcs into and out of every visited vertex are red when $\textsf{Tarry}$ halts. (Induct over the vertices in the order they are first marked.)
> - (g) Prove that every vertex is visited, so $\textsf{Tarry}$ traverses every arc exactly once.

Two observations are used throughout. Colors only change from white to green, from white to red, or from green to red, so red is permanent. And the only arc that ever turns green is, for each $w\ne s$, the arc $w\to v$ back to the vertex $v$ from which $w$ was first reached; call $v$ the **parent** of $w$. The start vertex $s$ never gets a green arc.

### (a) Linear-time implementation

> [!hint]- Hint
> Arcs never become white again, so the search for a white arc out of $v$ can resume where it last stopped.

> [!solution]- Solution
> Store each arc in its tail's adjacency list with its color and a pointer to its **twin** (the reverse arc in the other list), so "color $w\to v$ green" takes $O(1)$ time. Each vertex $v$ keeps a pointer into its list, the position of the first arc not yet known to be non-white, and a pointer to its parent arc. To look for a white arc out of $v$, advance the pointer past non-white arcs; since an arc never becomes white again, every arc is passed over at most once in the whole run, $O(E)$ in all. The green branch follows the parent arc in $O(1)$ time. The recursion is a tail call, so it becomes a loop (the walk can be $2E$ steps long; no stack is needed).
>
> Each visit does $O(1)$ work besides the pointer advances, and every visit but the last traverses an arc, which by (b) happens at most $2E$ times. Total: $O(V+E)$.
>
> **Answer.** Twin pointers, a resumable pointer per adjacency list and a loop instead of recursion: $O(V+E)$.

### (b), (c), (d) Counting red arcs

> [!hint]- Hint
> Every arc into $v$ that turns red is immediately followed by a visit to $v$; every visit except the very last one leaves $v$ along exactly one arc, which turns red.

> [!solution]- Solution
> **(b)** Traversing an arc colors it red, only white or green arcs are traversed, and red is permanent. So each arc is traversed at most once.
>
> **(c)** At the $k$th visit of $v$ (just after marking it):
>
> | vertex | red arcs into $v$ | red arcs out of $v$ |
> |---|---|---|
> | $v\ne s$ | $k$ | $k-1$ |
> | $v = s$ | $k-1$ | $k-1$ |
>
> An arc into $v$ turns red exactly when it is traversed, and each traversal into $v$ is followed at once by a visit to $v$; every visit is of this form except the first visit of $s$. Each of the previous $k-1$ visits of $v$ ended by traversing exactly one arc out of $v$ (a visit that traverses nothing ends the algorithm), and nothing else colors an arc out of $v$ red.
>
> **(d)** For $v\ne s$, the $k$th visit has $k$ red arcs into $v$ among $\deg(v)$, so $k\le\deg(v)$. For $s$, $k-1\le\deg(s)$. With finitely many visits, each doing finite work, the algorithm halts.
>
> **Answer.** (c) $k$ in and $k-1$ out for $v\ne s$; $k-1$ in and $k-1$ out for $s$. (d) follows by comparing with $\deg(v)$.

### (e), (f), (g) Tarry's walk ends at home and covers everything

> [!hint]- Hint
> (e) If the walk stopped at $v\ne s$, all $\deg(v)$ arcs out of $v$ would be red; compare with (c). (f) The parent arc of $v$ is traversed last, and only when no white arc leaves $v$.

> [!solution]- Solution
> **(e)** Suppose the algorithm halts during the $k$th visit of some $v\ne s$. No arc out of $v$ is white or green. The arc to $v$'s parent turned green when $v$ was first reached, so it is now red, and all other arcs out of $v$ are red as well (they never turn green). So all $\deg(v)$ arcs out of $v$ are red, and by (c) $\deg(v) = k-1$. But by (c) $k$ arcs into $v$ are red, so $k\le\deg(v) = k-1$ — a contradiction. The last vertex visited is $s$.
>
> **(f)** Induction over the vertices in the order in which they are first marked. *Base, $s$:* by (e) the algorithm halts during some visit $k$ of $s$, when no arc out of $s$ is white or green; so all $\deg(s)$ arcs out of $s$ are red, and by (c) $\deg(s) = k - 1$, which is also the number of red arcs into $s$: all of them. *Step, $v\ne s$ with parent $p$* (marked earlier): by induction all arcs at $p$ are red at the end, including $v\to p$. That arc was green, so it was traversed by the green branch during some visit $k$ of $v$, when no arc out of $v$ was white — all others were red. After this traversal all $\deg(v)$ arcs out of $v$ are red, and by (c) $k$ of them, so $\deg(v) = k$, which is the number of red arcs into $v$ at that visit: all of them. Red is permanent.
>
> **(g)** If some vertex were never visited, connectivity would give an edge $uv$ with $u$ visited and $v$ not. By (f) the arc $u\to v$ is red at the end, so it was traversed and $v$ was visited — a contradiction. So every vertex is visited, all $2E$ arcs are red by (f), and each was traversed exactly once by (b): the walk crosses every edge exactly once in each direction.
>
> **Answer.** (e) a stop at $v\ne s$ contradicts the counts of (c); (f) induction in order of first marking, via the parent arc; (g) an unvisited neighbor of a visited vertex contradicts (f).

## Exercise 6.8 — Tarry2 is not depth-first search

> [!question] Exercise 6.8 (book p. 248)
> A variant of Tarry's algorithm traverses green arcs without recoloring them and assigns two labels:
>
> ```text
> RecTarry2(v, clock):
>     if v is unmarked
>         v.pre ← clock; clock ← clock + 1; mark v
>     if some arc v→w is white
>         if w is unmarked
>             color w→v green
>         color v→w red; RecTarry2(w, clock)
>     else if some arc v→w is green
>         v.post ← clock; clock ← clock + 1; RecTarry2(w, clock)
> ```
>
> started as $\textsf{RecTarry2}(s, 1)$ with all vertices unmarked and all arcs white. Prove or disprove: when it halts, the green edges form a spanning tree, and the labels $v.\mathit{pre}$ and $v.\mathit{post}$ are a preorder and a postorder labeling, all consistent with one depth-first search of $G$.

> [!hint]- Hint
> When Tarry2 crosses a non-tree edge $v\to w$ to an already marked vertex, it continues from $w$ — depth-first search would stay at $v$. Can $w$ then discover a new vertex while $v$'s subtree is unfinished?

> [!solution]- Solution
> **The claim is false.** (A minor symptom first: $s$ never receives a $\mathit{post}$ label, since labels are only assigned when leaving along a green arc and $s$ has none. That could be patched; the tree cannot.)
>
> **Counterexample.** Vertices $s, a, b, x$, edges $sa$, $ab$, $bs$, $sx$, $xb$, adjacency lists $s{:}\ a, x, b$; $a{:}\ s, b$; $b{:}\ a, s, x$; $x{:}\ s, b$, white arcs taken in list order. The walk is
>
> | step | at | action |
> |---|---|---|
> | 1 | $s$ | $s.\mathit{pre} = 1$; $a$ is new: $a\to s$ green, go to $a$ |
> | 2 | $a$ | $a.\mathit{pre} = 2$; $b$ is new: $b\to a$ green, go to $b$ |
> | 3 | $b$ | $b.\mathit{pre} = 3$; white arc $b\to s$, go to $s$ (already marked) |
> | 4 | $s$ | white arc $s\to x$, $x$ is new: $x\to s$ green, go to $x$ |
> | 5 | $x$ | $x.\mathit{pre} = 4$; white arc $x\to b$, go to $b$ |
> | 6 | $b$ | white arc $b\to x$, go to $x$ |
> | 7 | $x$ | no white arc; $x.\mathit{post} = 5$, follow green $x\to s$ |
> | 8 | $s$ | white arc $s\to b$, go to $b$ |
> | 9 | $b$ | no white arc; $b.\mathit{post} = 6$, follow green $b\to a$ |
> | 10 | $a$ | no white arc; $a.\mathit{post} = 7$, follow green $a\to s$ |
> | 11 | $s$ | no white and no green arc: halt |
>
> The green edges $sa$, $ab$, $sx$ do form a spanning tree, but it is **not a depth-first tree for any adjacency order**: in a DFS of an undirected graph every non-tree edge joins an ancestor and a descendant, and the non-tree edge $xb$ joins two different subtrees of $s$. The labels fail too: $[x.\mathit{pre}, x.\mathit{post}] = [4, 5]$ is nested in $[b.\mathit{pre}, b.\mathit{post}] = [3, 6]$, which by Lemma 6.1 would make $x$ a descendant of $b$.
>
> What went wrong is step 3: crossing the non-tree edge $b\to s$ moved the walk back to $s$, which then discovered $x$ while $b$ was still unfinished. (On connected graphs with at most three vertices the green tree is always a depth-first tree, so four vertices is the smallest counterexample.)
>
> **Answer.** Disproved: on the graph above Tarry2 produces the tree $\{sa, ab, sx\}$, which no depth-first search produces, and nested intervals for unrelated vertices.

<!-- fig:a06x-tarry2 -->
<figure class="cs-fig"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 250" width="600" height="250" role="img" style="font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-size:14px"><title>a four-vertex graph with a spanning tree and nested intervals that no depth-first search can produce</title><defs><marker id="ARR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs><line x1="83" y1="50" x2="177" y2="50" stroke="var(--accent)" stroke-width="3.0" stroke-linecap="round"/><line x1="190" y1="63" x2="190" y2="147" stroke="var(--accent)" stroke-width="3.0" stroke-linecap="round"/><line x1="79.6" y1="58.8" x2="180.4" y2="151.2" stroke="var(--muted)" stroke-width="1.3" stroke-linecap="round" stroke-dasharray="5 3"/><line x1="70" y1="63" x2="70" y2="147" stroke="var(--accent)" stroke-width="3.0" stroke-linecap="round"/><line x1="83" y1="160" x2="177" y2="160" stroke="var(--hi)" stroke-width="1.3" stroke-linecap="round" stroke-dasharray="5 3"/><circle cx="70" cy="50" r="13" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="70" y="51" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">s</text><circle cx="190" cy="50" r="13" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="190" y="51" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">a</text><circle cx="190" cy="160" r="13" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="190" y="161" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">b</text><circle cx="70" cy="160" r="13" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="70" y="161" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">x</text><text x="36" y="50" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">1/–</text><text x="224" y="50" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">2/7</text><text x="224" y="160" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">3/6</text><text x="36" y="160" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">4/5</text><text x="46" y="198" text-anchor="start" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">s: a x b</text><text x="146" y="198" text-anchor="start" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">a: s b</text><text x="46" y="216" text-anchor="start" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">b: a s x</text><text x="146" y="216" text-anchor="start" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">x: s b</text><text x="130" y="240" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">walk: s a b s x b x s b a s</text><text x="319" y="200" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">1</text><line x1="319" y1="38" x2="319" y2="188" stroke="var(--muted)" stroke-width="0.5" stroke-linecap="round" stroke-dasharray="2 3"/><text x="357" y="200" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">2</text><line x1="357" y1="38" x2="357" y2="188" stroke="var(--muted)" stroke-width="0.5" stroke-linecap="round" stroke-dasharray="2 3"/><text x="395" y="200" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">3</text><line x1="395" y1="38" x2="395" y2="188" stroke="var(--muted)" stroke-width="0.5" stroke-linecap="round" stroke-dasharray="2 3"/><text x="433" y="200" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">4</text><line x1="433" y1="38" x2="433" y2="188" stroke="var(--muted)" stroke-width="0.5" stroke-linecap="round" stroke-dasharray="2 3"/><text x="471" y="200" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">5</text><line x1="471" y1="38" x2="471" y2="188" stroke="var(--muted)" stroke-width="0.5" stroke-linecap="round" stroke-dasharray="2 3"/><text x="509" y="200" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">6</text><line x1="509" y1="38" x2="509" y2="188" stroke="var(--muted)" stroke-width="0.5" stroke-linecap="round" stroke-dasharray="2 3"/><text x="547" y="200" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">7</text><line x1="547" y1="38" x2="547" y2="188" stroke="var(--muted)" stroke-width="0.5" stroke-linecap="round" stroke-dasharray="2 3"/><rect x="313" y="51" width="262.8" height="18" rx="9" fill="var(--accent)" fill-opacity="0.15" stroke="currentColor" stroke-width="1.3" stroke-dasharray="4 3"/><text x="284" y="60" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">s</text><rect x="351" y="85" width="202" height="18" rx="9" fill="var(--accent)" fill-opacity="0.15" stroke="currentColor" stroke-width="1.3"/><text x="284" y="94" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">a</text><rect x="389" y="119" width="126" height="18" rx="9" fill="var(--accent)" fill-opacity="0.15" stroke="currentColor" stroke-width="1.3"/><text x="284" y="128" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">b</text><rect x="427" y="153" width="50" height="18" rx="9" fill="var(--accent)" fill-opacity="0.15" stroke="var(--hi)" stroke-width="1.3"/><text x="284" y="162" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">x</text><text x="433" y="22" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">intervals [pre, post]</text></svg><figcaption><strong>Tarry2 is not depth-first search.</strong> Left: the green edges (thick) that Tarry2 leaves on this graph, with <i>pre</i>/<i>post</i> labels. Right: the intervals [<i>pre</i>, <i>post</i>]; <i>s</i> never gets a <i>post</i> label. The interval of <i>x</i> is nested in that of <i>b</i>, yet <i>x</i> is not a descendant of <i>b</i>, and the non-tree edge <i>xb</i> (red, dashed) joins two different subtrees of <i>s</i>. Neither can happen in a depth-first search of an undirected graph.</figcaption></figure>

## Exercise 6.9 — Keys locked in boxes

> [!question] Exercise 6.9 (book pp. 248–249)
> There are $n$ lock-boxes and $m$ gold keys. Each key unlocks at most one box; a box may be unlocked by one key, several keys or none. A box can be opened by unlocking it with a matching key in hand, or by smashing it. All keys are locked inside the boxes, and you know which keys are in which box. You must get all the keys out.
>
> (a) Your brother is about to smash one particular box. Describe and analyze an algorithm that decides whether all the keys can be retrieved without smashing any other box.
>
> (b) Describe and analyze an algorithm that computes the minimum number of boxes that must be smashed to retrieve all the keys.

### (a) One smashed box

> [!hint]- Hint
> Draw an edge from box $i$ to box $j$ when box $i$ holds a key to box $j$.

> [!solution]- Solution
> **Graph.** $G$, **directed**: one vertex per box ($n$ vertices), and an edge $i\to j$ for every key that lies in box $i$ and unlocks box $j$ (at most $m$ edges; keys that unlock nothing give no edge).
>
> **Problem.** Reachability from the chosen box $b$. After smashing $b$, the boxes you can open are exactly $\textsf{reach}(b)$: along a path $b\to j_1\to\dots\to j_k$ each box holds a key to the next, and conversely every box you open is unlocked by a key taken from a box opened earlier. All keys come out iff **every box that contains at least one key lies in $\textsf{reach}(b)$** (boxes without keys need not be opened).
>
> **Algorithm.** Whatever-first search from $b$, then check the box of each of the $m$ keys.
>
> **Time.** $O(n+m)$ to build $G$, search and check.
>
> **Answer.** Yes iff every box holding a key is reachable from $b$ in the box graph: $O(n+m)$ time.

### (b) Fewest smashed boxes

> [!hint]- Hint
> Smashing one box of a strong component opens the whole component. Which components can nothing else open?

> [!solution]- Solution
> **Graph** as in (a). Smashing a set $X$ of boxes opens exactly the boxes reachable from $X$.
>
> **Problem.** Count the **source components** of $\textsf{scc}(G)$ (strong components with no incoming edge in $\textsf{scc}(G)$) that contain at least one box with a key. That count is the answer.
>
> - *At least.* Let $C$ be such a source component. No box outside $C$ reaches a box of $C$ (Exercise 6.0(d)), so some box of $C$ must be smashed, and different components need different boxes.
> - *Enough.* Smash one box in each such component. Take any box $y$ that holds a key. Walking backwards in the dag $\textsf{scc}(G)$ from $S(y)$ ends at some source component $C$ that reaches $S(y)$. If $C\ne S(y)$, the first edge of that path out of $C$ means some box of $C$ holds a key; if $C = S(y)$, then $C$ contains $y$. Either way a box of $C$ was smashed, and it reaches $y$ (6.0(d)).
>
> A box with no key and no key to it is a source component of its own, but it never needs opening — which is why such components are not counted.
>
> **Algorithm.** Build $G$, compute $\textsf{scc}(G)$ with Kosaraju–Sharir, mark the components with an incoming edge, and count the unmarked components that contain a box with a key. **Time:** $O(n+m)$.
>
> **Answer.** The number of source components of $\textsf{scc}(G)$ that contain a key: $O(n+m)$ time.

## Exercise 6.10 — Is T a depth-first or breadth-first tree?

> [!question] Exercise 6.10 (book p. 249)
> You are given a connected graph $G$, a start vertex $s$ and a spanning tree $T$ of $G$ (rooted at $s$; when $G$ is directed, every edge of $T$ points away from $s$). Describe and analyze algorithms that decide whether
>
> - (a) $T$ is a depth-first spanning tree rooted at $s$, for undirected $G$;
> - (b) $T$ is a breadth-first spanning tree rooted at $s$, for undirected $G$ (hint: it is not enough for $T$ to be a shortest-path tree, and this is the right chapter for the problem);
> - (c) $T$ is a breadth-first spanning tree rooted at $s$, for directed $G$;
> - (d) $T$ is a depth-first spanning tree rooted at $s$, for directed $G$.
>
> "Is a depth-first tree" means: some ordering of the adjacency lists makes $\textsf{DFS}(s)$ produce exactly $T$; likewise for breadth-first search (whatever-first search with a queue).

In all parts, one traversal of $T$ from $s$ computes the parent $p(v)$, the depth $d(v)$ and pre/post numbers of every vertex in $T$, so ancestry in $T$ is an $O(1)$ interval test. Write $T_v$ for the subtree of $v$.

### (a) Undirected, depth-first

> [!hint]- Hint
> No cross edges.

> [!solution]- Solution
> **Claim.** $T$ is a depth-first tree from $s$ iff every edge of $G$ not in $T$ joins an ancestor and a descendant in $T$.
>
> **Algorithm.** Check every non-tree edge $uv$ with the interval test: $[u.\mathit{pre}, u.\mathit{post}]$ and $[v.\mathit{pre}, v.\mathit{post}]$ must be nested. **Time:** $O(V+E)$.
>
> **Proof.** ($\Rightarrow$) Undirected DFS has no cross edges. ($\Leftarrow$) Order each adjacency list with the $T$-children of the vertex first. By induction on the size of $T_x$: if $\textsf{DFS}(x)$ is called while all of $T_x$ is unmarked, it marks exactly $T_x$ and follows the edges of $T$. Indeed, $\textsf{DFS}(x)$ first examines its children $c_1, c_2, \dots$; when it reaches $c_i$, only $T_{c_1}, \dots, T_{c_{i-1}}$ have been marked inside $T_x$ (induction), so $c_i$ is unmarked and $\textsf{DFS}(c_i)$ marks exactly $T_{c_i}$. Every other edge $xy$ then leads to an ancestor of $x$ (marked: it is active) or to a descendant (marked: all of $T_x$ is), so it starts no call.
>
> **Answer.** $T$ is a DFS tree iff all non-tree edges join ancestor–descendant pairs: $O(V+E)$ time.

### (b) and (c) Breadth-first

> [!hint]- Hint
> Breadth-first search processes the vertices level by level, each level in the order of the parents, and the parent of $v$ is its neighbor that came first. So a non-tree edge from $u$ to a vertex $v$ one level down forces $p(v)$ before $u$. Translate each such constraint into "this child of the lowest common ancestor before that child", and ask whether the constraints have a cycle.

> [!solution]- Solution
> **Facts about BFS** (the book's queue version, Chapter 5). BFS marks the vertices in an order $\pi$ by levels, $d(v)$ being the distance from $s$; within a level, by the $\pi$-order of the parents, and a vertex's children consecutively, in the order of its adjacency list. The parent of each $v\ne s$ is the first vertex of $\pi$ with an edge to $v$. So for two different vertices $x, y$ at the same depth, with $x', y'$ their ancestors that are children of the same vertex (the lowest common ancestor), $x$ precedes $y$ in $\pi$ iff $x'$ precedes $y'$.
>
> **Algorithm** (written for directed edges; for undirected $G$ in part (b), use both directions of every edge):
>
> ```text
> IsBFSTree(G, s, T):
>     compute p(v) and d(v) for every vertex (T rooted at s)
>     H ← a graph on the vertices of G with no edges
>     for each edge u→v of G
>         if d(v) > d(u) + 1
>             return False                     ⟨⟨T is not a shortest-path tree⟩⟩
>         if d(v) = d(u) + 1 and p(v) ≠ u
>             (x, y) ← Lift(p(v), u)
>             add x→y to H                     ⟨⟨x's branch before y's⟩⟩
>     return IsAcyclic(H)
>
> Lift(x, y):                                  ⟨⟨x ≠ y⟩⟩
>     while d(x) > d(y): x ← p(x)
>     while d(y) > d(x): y ← p(y)
>     while p(x) ≠ p(y): x ← p(x); y ← p(y)
>     return (x, y)                            ⟨⟨siblings below the LCA⟩⟩
> ```
>
> Every edge of $H$ joins two siblings, so $H$ is acyclic iff for every vertex the constraints on its children can be met by one order — a topological order of $H$.
>
> **Correctness.** ($\Rightarrow$) Let BFS produce $T$ and order $\pi$. Its tree is a shortest-path tree, so $d(v)\le d(u)+1$ for every edge $u\to v$. For a non-tree edge $u\to v$ with $d(v) = d(u)+1$, $p(v)$ precedes $u$ in $\pi$ (the parent comes first), so by the facts the lifted pair satisfies $x$ before $y$: every edge of $H$ goes forward in $\pi$, and $H$ is acyclic. ($\Leftarrow$) Order the children of every vertex by a topological order of $H$, and give every vertex an adjacency list that starts with its $T$-children in that order. Let $\pi$ list $T$ level by level, each level by parents, siblings in the chosen order. By induction along $\pi$, BFS marks the vertices in the order $\pi$ and gives each $v$ the parent $p(v)$: among the vertices with an edge to $v$, $p(v)$ is marked first, because any other in-neighbor $u$ of $v$ is at depth $\ge d(v) > d(p(v))$, or at depth $d(v)-1$ and then after $p(v)$ in $\pi$ by the edge $x\to y$ of $H$ it produced.
>
> **Time.** $\textsf{Lift}$ walks up the tree, $O(V)$ per edge; $H$ has at most $E$ edges and $\textsf{IsAcyclic}$ takes $O(V+E)$. Total $O(VE)$. (Faster lowest-common-ancestor methods exist but are beyond this course.)
>
> **Example (the book's hint).** Let $G$ have edges $sa, sb, ac, ad, bc, bd$ and $T = \{sa, sb, ac, bd\}$. Every edge of $G$ joins adjacent levels, so $T$ is a shortest-path tree. But $c$'s parent $a$ must come before its other neighbor $b$, and $d$'s parent $b$ before $a$: $H$ has the cycle $a\to b\to a$, and indeed neither order of $a, b$ produces $T$.
>
> **Answer.** Check $d(v)\le d(u)+1$ for every edge, turn every non-tree edge between adjacent levels into a sibling constraint at the lowest common ancestor, and accept iff the constraints are acyclic: $O(VE)$ time, for both (b) and (c).

### (d) Directed, depth-first

> [!hint]- Hint
> Edge classification: in a DFS, a non-tree edge between unrelated vertices is a cross edge into a subtree that is already finished — the branch of its head was explored first.

> [!solution]- Solution
> **Algorithm.**
>
> ```text
> IsDFSTreeDirected(G, s, T):
>     compute p(v), d(v), v.pre, v.post in T
>     H ← a graph on the vertices of G with no edges
>     for each edge u→v of G not in T
>         if neither of u, v is an ancestor of the other
>             (x, y) ← Lift(u, v)
>             add y→x to H                     ⟨⟨v's branch before u's⟩⟩
>     return IsAcyclic(H)
> ```
>
> **Correctness.** ($\Rightarrow$) In a DFS producing $T$, every non-tree edge $u\to v$ is a forward edge, a back edge, or a cross edge with $v.\mathit{post} < u.\mathit{pre}$ (§6.1). In the last case $v$'s branch below the lowest common ancestor was called before $u$'s, so every edge of $H$ goes from an earlier to a later call: $H$ is acyclic. ($\Leftarrow$) Order the children of each vertex by a topological order of $H$, $T$-children first in each adjacency list. The induction of part (a) goes through: when $\textsf{DFS}(x)$ examines a non-tree edge $x\to v$, $v$ is an ancestor of $x$ (active), a descendant (in the already explored $T_x$), or lies in a branch that comes earlier at the lowest common ancestor (finished) — marked in every case.
>
> **Time.** $O(VE)$, as in (b).
>
> Part (a) is the special case in which every edge goes both ways: an undirected non-tree edge between unrelated vertices produces both $x\to y$ and $y\to x$, a cycle in $H$.
>
> **Answer.** Turn every cross edge into "the head's branch before the tail's branch" at the lowest common ancestor; $T$ is a DFS tree iff these constraints are acyclic: $O(VE)$ time.

## Exercise 6.11 — Parallel assignment

> [!question] Exercise 6.11(a) (book pp. 249–250)
> A **parallel assignment** $x_1, \dots, x_k \leftarrow e_1, \dots, e_k$ evaluates all right sides with the *old* values and then assigns them; for example `a,b = b,a` swaps. An interpreter must turn it into a sequence of single assignments. `x,y = x+1,x+y` can only be serialized as `y=x+y; x=x+1`; serializing `a,b = b,a` needs one temporary variable. The variables are simple, no variable appears twice on the left, and right sides have no side effects.
>
> (a) Describe an algorithm that decides whether a given parallel assignment can be serialized without temporary variables. (Describe the graph representation you assume.)
>
> Part (b), exactly one temporary variable, is skipped. Two slips in the book's text: `a,b = 0,1` can be serialized "either `a=0; b=1` or `a=0; b=1`" (the second should be `b=1; a=0`); and `x,y = x+y,x-y` is said to need **two** temporaries, but one suffices: `t=x; x=x+y; y=t-y`.

> [!hint]- Hint
> If $e_i$ reads $x_j$, the assignment to $x_i$ must happen before $x_j$ is overwritten.

> [!solution]- Solution
> Let $r$ be the total length of the right sides.
>
> **Graph.** $D$, **directed**: one vertex per assignment $x_i\leftarrow e_i$ ($k$ vertices), and an edge $x_i\to x_j$ whenever $i\ne j$ and $e_i$ mentions $x_j$. Assume each variable occurrence in an expression points to its variable's record, so $D$ is built in one scan, $O(k+r)$ time, with at most $r$ edges.
>
> **Problem.** A serialization without temporaries executes the $k$ assignments once each, in some order. It is correct iff $x_i\leftarrow e_i$ runs before $x_j\leftarrow e_j$ for every edge $x_i\to x_j$: $e_i$ needs the old value of $x_j$, which disappears exactly when $x_j$ is assigned; and $e_i$ may read $x_i$ itself, still unassigned when $e_i$ is evaluated (no loops needed). So the correct serializations are exactly the **topological orders** of $D$, and one exists iff $D$ is **acyclic**.
>
> **Algorithm.** $\textsf{IsAcyclic}(D)$; if acyclic, output the assignments in a topological order (reverse postorder). **Time:** $O(k+r)$, linear in the size of the statement.
>
> **Examples.** For `x,y = x+1,x+y` the only edge is $y\to x$, so $y$ goes first. `a,b = b,a` and `x,y = x+y,x-y` both give the 2-cycle $a\rightleftarrows b$ (resp. $x\rightleftarrows y$) and need a temporary.
>
> **Answer.** Serializable without temporaries iff the "reads" graph $D$ is acyclic; a topological order of $D$ is the serialization: $O(k+r)$ time.

## Exercise 6.12 — Scheduling jobs in a dag

> [!question] Exercise 6.12 (book p. 250)
> The vertices of a dag $G$ are jobs; an edge $u\to v$ means that job $u$ must be completed before job $v$ begins; job $v$ takes time $T(v)\ge 0$. Any number of jobs may run at the same time (the book leaves this implicit).
>
> (a) Describe an algorithm that computes the shortest time interval in which all jobs can be executed.
>
> (b) The first job starts at time 0. Describe an algorithm that computes, for every vertex $v$, the earliest time at which job $v$ can begin.
>
> (c) Describe an algorithm that computes, for every vertex $v$, the latest time at which job $v$ can begin without violating a precedence constraint or increasing the overall completion time of (a), assuming every other job starts at its earliest start time of (b).

### (a) and (b) Earliest start times

> [!hint]- Hint
> Job $v$ can start as soon as all its predecessors have finished.

> [!solution]- Solution
> **Function.** For every vertex $v$, let $\textsf{EarliestStart}(v)$ be the earliest time at which job $v$ can begin if every job starts as early as the constraints allow and the first jobs start at time 0. Part (b) asks for all of them; part (a) is $\mathit{CT} = \max_v\big(\textsf{EarliestStart}(v) + T(v)\big)$.
>
> **Recurrence.** Job $v$ can begin once every predecessor $u$ has finished, at time $\textsf{EarliestStart}(u) + T(u)$ at the earliest:
> $$
> \textsf{EarliestStart}(v) = \max\Big(\{0\}\cup\big\{\textsf{EarliestStart}(u) + T(u) \bigm| u\to v\in E\big\}\Big).
> $$
> Starting every job at this time respects all constraints and finishes at $\mathit{CT}$; no schedule finishes earlier, because the jobs along any path must run one after another, and $\mathit{CT}$ is the total time of the heaviest path.
>
> - **Memoization:** a field $v.\mathit{es}$ in every vertex (an array indexed by vertices).
> - **Evaluation order:** a topological order of $G$ — each entry reads only its in-neighbors. (Equivalently, postorder of $\textsf{rev}(G)$.)
> - **Time:** $O(V+E)$: the topological sort, plus $O(1)$ per edge.
>
> **Answer.** $\textsf{EarliestStart}$ in topological order, and $\mathit{CT} = \max_v(\textsf{EarliestStart}(v) + T(v))$: $O(V+E)$ time.

### (c) Latest start times

> [!hint]- Hint
> With every other job pinned to its earliest start, job $v$ only has to finish before each of its successors starts and before $\mathit{CT}$.

> [!solution]- Solution
> If every other job starts at its earliest time, job $v$'s predecessors finish by $\textsf{EarliestStart}(v)$, so $v$ may start at any time $t\ge\textsf{EarliestStart}(v)$ with $t + T(v)\le\textsf{EarliestStart}(w)$ for every edge $v\to w$ and $t + T(v)\le\mathit{CT}$. The latest such $t$ is
> $$
> \textsf{LatestStart}(v) = \min\Big(\{\mathit{CT}\}\cup\{\textsf{EarliestStart}(w)\mid v\to w\in E\}\Big) - T(v),
> $$
> which is at least $\textsf{EarliestStart}(v)$ by the recurrence of (a). This needs no recursion: after (a) and (b), one pass over the out-edges, $O(V+E)$ time.
>
> **Variant.** If the other jobs may be delayed as well (the "latest start time" of the critical-path method), the deadline of $v$ depends on how late its successors may start, which gives a recurrence evaluated in **reverse** topological order (postorder):
> $$
> \textsf{LatestStart}^*(v) = \min\Big(\{\mathit{CT}\}\cup\{\textsf{LatestStart}^*(w)\mid v\to w\in E\}\Big) - T(v).
> $$
> It equals $\mathit{CT}$ minus the heaviest path that starts at $v$, and it is never earlier than $\textsf{LatestStart}(v)$; the jobs with $\textsf{LatestStart}^*(v) = \textsf{EarliestStart}(v)$ are the critical ones.
>
> **Answer.** $\textsf{LatestStart}(v) = \min(\{\mathit{CT}\}\cup\{\textsf{EarliestStart}(w) : v\to w\}) - T(v)$, in $O(V+E)$ time.

## Exercise 6.13 — Paths in a dag with one source and one sink

> [!question] Exercise 6.13 (book pp. 250–251)
> $G$ is a dag with a unique source $s$ and a unique sink $t$.
>
> (a) A Hamiltonian path is a directed path that contains every vertex. Describe an algorithm that decides whether $G$ has one.
>
> (b) The vertices have weights. Describe an efficient algorithm that finds the path from $s$ to $t$ with maximum total weight.
>
> (c) Given also an integer $\ell$, find the maximum-weight path from $s$ to $t$ with at most $\ell$ edges (assume one exists).
>
> (d) Some vertices are **important**; given an integer $k$, find the maximum-weight path from $s$ to $t$ that visits at least $k$ important vertices (assume one exists).
>
> (e) Compute the number of paths from $s$ to $t$ (adding large integers takes $O(1)$ time).

All five are [[concepts/dynamic-programming-on-dags|dynamic programs on the dag itself]] ([[2-algorithms/06-depth-first-search#64-memoization-and-dynamic-programming|§6.4]]): a function of a vertex $v$ (and possibly a counter) that describes paths **from $v$ to $t$**, whose value at $v$ depends on its out-neighbors. Since $t$ is the only sink, every vertex other than $t$ has an outgoing edge and every path can be continued to $t$. Every vertex is reachable from $s$, so the evaluation order **postorder of $\textsf{DFS}(s)$** (reverse topological order) computes every entry after the entries it reads. Write $w(v)$ for the weight of $v$.

### (a) and (b) Longest and heaviest paths

> [!hint]- Hint
> A Hamiltonian path has to start at $s$ and end at $t$. Count vertices on the longest path from $s$.

> [!solution]- Solution
> **(a) Function.** For every vertex $v$, let $\textsf{Len}(v)$ be the largest number of vertices on a path from $v$ to $t$. A Hamiltonian path must begin at $s$ (no edge enters it) and end at $t$ (no edge leaves it), so $G$ has one iff $\textsf{Len}(s) = V$.
>
> **Recurrence.** $\textsf{Len}(t) = 1$, and $\textsf{Len}(v) = 1 + \max\{\textsf{Len}(x)\mid v\to x\in E\}$ for $v\ne t$ (the path continues along some edge $v\to x$).
>
> **(b) Function.** For every vertex $v$, let $\textsf{MaxPath}(v)$ be the maximum total weight of a path from $v$ to $t$. We need $\textsf{MaxPath}(s)$.
>
> **Recurrence.**
> $$
> \textsf{MaxPath}(v) = \begin{cases} w(t) & \text{if } v = t\\ w(v) + \max\{\textsf{MaxPath}(x)\mid v\to x\in E\} & \text{otherwise}\end{cases}
> $$
> To output the path, record a maximizing $x$ at each $v$ and follow these choices from $s$.
>
> - **Memoization:** a field in every vertex.
> - **Evaluation order:** postorder of $\textsf{DFS}(s)$.
> - **Time:** $O(V+E)$ — each entry scans the out-edges of its vertex once.
>
> (a) is also Exercise 6.1(b) in disguise: a dag has a Hamiltonian path iff it is semi-connected.
>
> **Answer.** (a) $\textsf{Len}(s) = V$; (b) $\textsf{MaxPath}(s)$; each $O(V+E)$ time.

### (c) and (d) Paths with a budget

> [!hint]- Hint
> Add the remaining budget to the subproblem: the number of edges still allowed, or the number of important vertices still needed.

> [!solution]- Solution
> **(c) Function.** For every vertex $v$ and $0\le j\le\ell$, let $\textsf{MaxPathL}(v, j)$ be the maximum weight of a path from $v$ to $t$ with at most $j$ edges ($-\infty$ if there is none). We need $\textsf{MaxPathL}(s, \ell)$.
>
> **Recurrence.**
> $$
> \textsf{MaxPathL}(v, j) = \begin{cases}
> w(t) & \text{if } v = t\\
> -\infty & \text{if } v\ne t \text{ and } j = 0\\
> w(v) + \max\{\textsf{MaxPathL}(x, j-1)\mid v\to x\in E\} & \text{otherwise}
> \end{cases}
> $$
>
> - **Memoization:** an array $\mathit{MaxPathL}[1\,..\,V, 0\,..\,\ell]$.
> - **Evaluation order:** $j$ from $0$ up to $\ell$ in the outer loop, the vertices in any order in the inner loop (entry $(v, j)$ reads only column $j-1$).
> - **Time:** $\ell+1$ columns, each $O(V+E)$: $O(\ell(V+E))$.
>
> **(d) Function.** Let $\mathit{imp}(v) = 1$ if $v$ is important and $0$ otherwise. For every vertex $v$ and $0\le j\le k$, let $\textsf{MaxImp}(v, j)$ be the maximum weight of a path from $v$ to $t$ that visits at least $j$ important vertices ($-\infty$ if there is none). We need $\textsf{MaxImp}(s, k)$.
>
> **Recurrence.** At the sink, $\textsf{MaxImp}(t, j) = w(t)$ if $\mathit{imp}(t)\ge j$ and $-\infty$ otherwise. For $v\ne t$, visiting $v$ uses up one requirement if $v$ is important, so with $j' = \max\{0, j - \mathit{imp}(v)\}$:
> $$
> \textsf{MaxImp}(v, j) = w(v) + \max\{\textsf{MaxImp}(x, j')\mid v\to x\in E\}.
> $$
>
> - **Memoization:** an array $\mathit{MaxImp}[1\,..\,V, 0\,..\,k]$.
> - **Evaluation order:** vertices in postorder of $\textsf{DFS}(s)$ in the outer loop, $j$ in any order in the inner loop (entry $(v, j)$ reads only out-neighbors of $v$).
> - **Time:** $(k+1)$ entries per vertex, each scanning the out-edges: $O(k(V+E))$.
>
> **Answer.** (c) $\textsf{MaxPathL}(s, \ell)$ in $O(\ell(V+E))$ time; (d) $\textsf{MaxImp}(s, k)$ in $O(k(V+E))$ time.

### (e) Counting paths

> [!hint]- Hint
> Every path from $v$ to $t$ starts with exactly one edge.

> [!solution]- Solution
> **Function.** For every vertex $v$, let $\textsf{NumPaths}(v)$ be the number of paths from $v$ to $t$. We need $\textsf{NumPaths}(s)$.
>
> **Recurrence.** Paths from $v\ne t$ are classified by their first edge:
> $$
> \textsf{NumPaths}(v) = \begin{cases} 1 & \text{if } v = t\\ \sum_{v\to x\in E}\textsf{NumPaths}(x) & \text{otherwise}\end{cases}
> $$
>
> - **Memoization:** a field in every vertex.
> - **Evaluation order:** postorder of $\textsf{DFS}(s)$.
> - **Time:** $O(V+E)$ additions.
>
> **Example.** The dag of Figure 6.20 (Exercise 6.3) has $128 = 2\cdot 8\cdot 4\cdot 2$ paths from $s$ to $t$: every path passes through the cut vertices $g$, $c$, $j$, and there are 2, 8, 4 and 2 paths from $s$ to $g$, $g$ to $c$, $c$ to $j$ and $j$ to $t$.
>
> **Answer.** $\textsf{NumPaths}(s)$, in $O(V+E)$ time.

### Sources for this page

Exercises 6.0–6.11(a), 6.12 and 6.13 of Jeff Erickson, *Algorithms* (2019), pp. 244–251 (CC BY 4.0), paraphrased; the solutions are ours. The graphs of Figures 6.20 and 6.21 are re-entered from the book (our vertex names) and their claims — three $(s,t)$-cut vertices, four cut vertices — are reproduced; the Tarry2 counterexample, the shortest-path tree that is not a breadth-first tree, and the remaining examples are original. Three statements are wrong as printed: 6.4(b)ii describes the vertices that are *not* cut vertices, the "only if" half of 6.6(b) fails for the 2-cycle, and 6.11 says that `x,y = x+y,x-y` needs two temporaries (one suffices). Every algorithm on this page is checked by `tools/checks/a06x.py` against brute force on random small graphs — vertex and edge deletion for cut vertices and bridges, all graphs on at most four vertices for transitive reductions, every adjacency order for the depth-first and breadth-first tree tests, all subsets of boxes, all paths, all start times and all serialization orders — and every number in the examples is recomputed there.
