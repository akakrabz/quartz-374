---
title: "Chapter 9 exercises — All-Pairs Shortest Paths"
description: "Solutions to Exercises 9.1–9.10 of Erickson's Algorithms: predecessor pointers for LeyzorekAPSP and Floyd–Warshall (and why the obvious update fails for Leyzorek), correct distances and explicit negative cycles in graphs with negative cycles, zero-length cycles by reweighting, distances between vertex classes, currency arbitrage, Morty's labyrinth, deleting a vertex, and boolean matrix products versus min-plus products and transitive closure."
tags: [exercises, algorithms, graphs, dynamic-programming, midterm-2]
---

*Solved exercises for [[2-algorithms/09-all-pairs-shortest-paths|Chapter 9]] · book pp. 320–325 · statements paraphrased; see the book for the originals*

These are Exercises 9.1–9.10, all parts; none of them is marked ♥ or ◆. Skipped: 9.11, a correctness proof for a cache-friendly recursive reordering of Floyd–Warshall (an unreasonable amount of thought, and its printed code is faulty — see the note below), 9.12 (♥, Seidel's algorithm) and 9.13 (Yuval's reduction), past the first ten. Modifications of the chapter's algorithms come with the change, its running time and a correctness proof; modeling problems are written in the graph-reduction rubric's format ([[concepts/graph-reductions]]: graph, problem on the graph, black-box algorithm, time in the input's parameters); recursive algorithms in the [[0-toolkit/06-how-exams-are-graded#11-recursive-algorithms|recursive-algorithm rubric]]'s. One finding is worth knowing before an exam: the "minor modification" that adds predecessor pointers works for Floyd–Warshall but **not** for LeyzorekAPSP when the graph has a cycle of length zero (Exercise 9.1). Write your own answer before opening a solution.

> [!tip] Black boxes from Chapters 6–9, used below without re-explanation
> - **[[concepts/bellman-ford|Bellman–Ford]]** ([[2-algorithms/08-shortest-paths#87-relax-all-the-edges-bellmanford|§8.7]]): $O(VE)$; after $i$ rounds every $\mathit{dist}(v)$ is at most the length of every walk from $s$ to $v$ with at most $i$ edges; an edge is still tense after $V-1$ rounds iff a negative cycle is reachable from $s$.
> - **[[concepts/dijkstras-algorithm|Dijkstra]]** ([[2-algorithms/08-shortest-paths#86-best-first-dijkstras-algorithm|§8.6]]), nonnegative weights only: $O(E\log V)$ with a binary heap, $O(E + V\log V)$ with a Fibonacci heap.
> - **Reweighting** ([[2-algorithms/09-all-pairs-shortest-paths#93-reweighting|§9.3]]): with prices $\pi$, $w'(u\to v) = \pi(u) + w(u\to v) - \pi(v)$ changes every path from $u$ to $v$ by $\pi(u) - \pi(v)$ and every cycle by 0. With $\pi(v) = \textsf{dist}(s, v)$ from a new vertex $s$ with 0-weight edges to all vertices, every $w'\ge 0$ and every $\pi(v)\le 0$ ([[concepts/johnsons-algorithm|Johnson]], [[2-algorithms/09-all-pairs-shortest-paths#94-johnsons-algorithm|§9.4]]).
> - **LeyzorekAPSP** ([[2-algorithms/09-all-pairs-shortest-paths#96-divide-and-conquer|§9.6]], $O(V^3\log V)$) and **FloydWarshall** ([[2-algorithms/09-all-pairs-shortest-paths#98-floydwarshall|§9.8]], $O(V^3)$), with $\mathit{dist}[v, v] = 0$ and $\infty$ for non-edges initially. Even with negative cycles: every stored $\mathit{dist}[u, v]$ is the length of some walk from $u$ to $v$; at the end it is at most the length of every path from $u$ to $v$ (a simple cycle through $u$ if $u = v$).
> - **Strong components** and $\textsf{scc}(G)$, **cycle detection**, **topological sort**: $O(V+E)$ ([[2-algorithms/06-depth-first-search#66-strong-components-in-linear-time|§6.6]], [[2-algorithms/06-depth-first-search#62-detecting-cycles|§6.2]], [[2-algorithms/06-depth-first-search#63-topological-sort|§6.3]]). **Reachability** by [[concepts/whatever-first-search|whatever-first search]], $O(V+E)$, also from several sources at once.

> [!note] Exercise 9.11 as printed
> The book's $\textsf{RecursiveAPSP}$ (p. 324) does not work as printed: its initialization overwrites $D[i, i] \leftarrow 0$ with $\infty$ (the "else" belongs to the edge test), the base case reads $D[j, k]$ where $D[k, j]$ is meant, and even with both fixed, the eight recursive calls in the printed order miss paths — with unit weights on $2\to4\to3\to1$ it leaves $D[2, 1] = \infty$. An order that works: the blocks $(i, j)$, $(i, j{+}m)$, $(i{+}m, j)$, $(i{+}m, j{+}m)$ with $k$, then $(i{+}m, j{+}m)$, $(i{+}m, j)$, $(i, j{+}m)$, $(i, j)$ with $k{+}m$.

## Exercise 9.1 — Predecessor pointers

> [!question] Exercise 9.1 (book p. 320)
> (a) Describe a modification of LeyzorekAPSP that returns the array of predecessor pointers in addition to the distances, still in $O(V^3\log V)$ time.
>
> (b) Describe a modification of FloydWarshall that returns the array of predecessor pointers in addition to the distances, still in $O(V^3)$ time.
>
> As in the chapter, $G$ has no negative cycles, and $\mathit{pred}[u, v]$ is the second-to-last vertex of a shortest path from $u$ to $v$ ($\textsf{Null}$ if $u = v$ or $v$ is unreachable), so that following the pointers back from $v$ traces a shortest path.

**The obvious modification**, for both algorithms: initialize $\mathit{pred}[u, v]\leftarrow u$ for every edge $u\to v$ and $\textsf{Null}$ otherwise; whenever $\mathit{dist}[u, v]$ improves through a middle vertex $x$ (or $r$), set $\mathit{pred}[u, v]\leftarrow\mathit{pred}[x, v]$, because the new path ends with the stored path from $x$ to $v$.

### (a) LeyzorekAPSP

> [!hint]- Hint
> Try the obvious modification on a graph with a cycle of length 0. Then break ties between equally short walks by their number of edges.

> [!solution]- Solution
> **The obvious modification fails.** In the figure below, the loops run over the vertices in the order $a, b, c, d$. In the first pass, $\mathit{dist}[c, a]$ improves through $b$ (so $\mathit{pred}[c, a] = b$), then $\mathit{dist}[d, a] = 3$ through $c$ (so $\mathit{pred}[d, a] = \mathit{pred}[c, a] = b$), then $\mathit{dist}[d, b]$ is set to $\mathit{dist}[d, a] + \mathit{dist}[a, b] = 3 - 1 = 2$ through $a$ (so $\mathit{pred}[d, b] = \mathit{pred}[a, b] = a$); the candidate through $c$ also has length 2 and does not replace it. All distances are right, but the pointers from $a$ lead $a, b, a, b, \ldots$ and never reach $d$. The culprit is the zero-length cycle $a\to b\to a$: a walk around it ties with the shortest path.
>
> **The fix: tie-break by the number of edges.** Run the algorithm with the pairs $(\text{length}, \text{number of edges})$ in place of lengths: an edge $u\to v$ has $(w(u\to v), 1)$, the diagonal starts at $(0, 0)$, non-edges at $(\infty, \infty)$; pairs are added coordinatewise and compared lexicographically. Output the first coordinates.
>
> ```text
> LeyzorekAPSPWithPred(V, E, w):
>     for all vertices u
>         for all vertices v
>             if u = v:        dist[u, v] ← (0, 0);         pred[u, v] ← Null
>             else if u→v ∈ E: dist[u, v] ← (w(u→v), 1);    pred[u, v] ← u
>             else:            dist[u, v] ← (∞, ∞);         pred[u, v] ← Null
>     for i ← 1 to ⌈lg V⌉
>         for all vertices u
>             for all vertices v
>                 for all vertices x
>                     if dist[u, v] > dist[u, x] + dist[x, v]      ⟨⟨lexicographic⟩⟩
>                         dist[u, v] ← dist[u, x] + dist[x, v]
>                         pred[u, v] ← pred[x, v]
> ```
>
> **Time.** Each step costs $O(1)$ more than before: $O(V^3\log V)$.
>
> **Correctness.** Write $D(u, v)$ for the smallest pair-length of a walk from $u$ to $v$.
> 1. *Every cycle has positive pair-length*: its length is positive, or it is 0 and the cycle has at least one edge. The correctness proof of §9.6 only adds and compares lengths, so it holds for pairs: the algorithm ends with $\mathit{dist}[u, v] = D(u, v)$, whose first coordinate is $\textsf{dist}(u, v)$ (the lexicographic minimum minimizes the length first).
> 2. *Walk invariant.* By induction on the updates, every finite $\mathit{dist}[u, v]$ with $u\ne v$ is the pair-length of a walk from $u$ to $v$ whose last edge is $\mathit{pred}[u, v]\to v$: an update glues the walks stored for $(u, x)$ and $(x, v)$, and the last edge comes from the second. With $p = \mathit{pred}[u, v]$, the part of that walk before $v$ is a walk from $u$ to $p$, so at the end $D(u, v) = \mathit{dist}[u, v] \ge D(u, p) + (w(p\to v), 1) \ge D(u, v)$: every pointer edge is **tight**, $D(u, v) = D(u, p) + (w(p\to v), 1)$.
> 3. *No pointer cycles.* If the pointers of row $u$ formed a cycle, adding the tight equations around it would give the cycle pair-length $(0, 0)$, contradicting step 1. So following the pointers from any reachable $v$ never repeats a vertex and can only stop at $u$ (every other reachable vertex has a pointer); adding the tight equations along the way shows that the path has length $\textsf{dist}(u, v)$.
>
> If every cycle of $G$ has positive length, step 1 holds for plain lengths, and the obvious modification is already correct.
>
> **Answer.** Update $\mathit{pred}[u, v] \leftarrow \mathit{pred}[x, v]$ with each improvement, but compare (length, number of edges) pairs lexicographically; $O(V^3\log V)$ time. Without the tie-break, zero-length cycles can produce pointer cycles.

<!-- fig:a09x-pointer-cycle -->
<figure class="cs-fig"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 236" width="600" height="236" role="img" style="font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-size:14px"><title>two copies of a four-vertex path graph with a two-cycle; the top copy has a cycle of red pointer edges</title><defs><marker id="ARR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs><text x="70" y="100" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">0</text><text x="190" y="100" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">1</text><text x="310" y="100" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">2</text><text x="430" y="100" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">3</text><text x="70" y="210" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">0</text><text x="190" y="210" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">1</text><text x="310" y="210" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">2</text><text x="430" y="210" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">3</text><text x="500" y="180" text-anchor="start" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;"></text><text x="500" y="180" text-anchor="start" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">FloydWarshall</text><text x="500" y="197" text-anchor="start" dominant-baseline="central" fill="var(--muted)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">(or Leyzorek</text><text x="500" y="214" text-anchor="start" dominant-baseline="central" fill="var(--muted)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">with pairs)</text><text x="500" y="62" text-anchor="start" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">LeyzorekAPSP,</text><text x="500" y="79" text-anchor="start" dominant-baseline="central" fill="var(--muted)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">plain update</text><path d="M85,70 L172.5,70" fill="none" stroke="var(--hi)" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="130" y="59" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">1</text><path d="M205,70 L292.5,70" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="250" y="59" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">1</text><path d="M323.6,63.7 Q370,42 414.1,62.6" fill="none" stroke="var(--hi)" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="370" y="41.8" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">1</text><path d="M416.4,76.3 Q370,98 325.9,77.4" fill="none" stroke="var(--hi)" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="370" y="98.2" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">−1</text><path d="M85,180 L172.5,180" fill="none" stroke="var(--hi)" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="130" y="169" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">1</text><path d="M205,180 L292.5,180" fill="none" stroke="var(--hi)" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="250" y="169" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">1</text><path d="M323.6,173.7 Q370,152 414.1,172.6" fill="none" stroke="var(--hi)" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="370" y="151.8" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">1</text><path d="M416.4,186.3 Q370,208 325.9,187.4" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="370" y="208.2" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">−1</text><circle cx="70" cy="70" r="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="70" y="71" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">d</text><circle cx="190" cy="70" r="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="190" y="71" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">c</text><circle cx="310" cy="70" r="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="310" y="71" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">b</text><circle cx="430" cy="70" r="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="430" y="71" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">a</text><circle cx="70" cy="180" r="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="70" y="181" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">d</text><circle cx="190" cy="180" r="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="190" y="181" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">c</text><circle cx="310" cy="180" r="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="310" y="181" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">b</text><circle cx="430" cy="180" r="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="430" y="181" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">a</text></svg><figcaption><strong>The plain predecessor update can close a zero-length pointer cycle.</strong> Edges <i>d</i>→<i>c</i>→<i>b</i>→<i>a</i> of weight 1 and <i>a</i>→<i>b</i> of weight −1; the cycle <i>a</i>→<i>b</i>→<i>a</i> has length 0. The grey numbers are the (correct) distances from <i>d</i>; red edges are the pointer edges <i>pred</i>[<i>d</i>, <i>x</i>]→<i>x</i>. Top: LeyzorekAPSP sets <i>pred</i>[<i>d</i>, <i>a</i>] = <i>b</i>, then reaches <i>b</i> through <i>a</i> (length 2, a tie with the path through <i>c</i>, which therefore never replaces it) and sets <i>pred</i>[<i>d</i>, <i>b</i>] = <i>a</i>: following the pointers from <i>a</i> never gets back to <i>d</i>. Bottom: the correct pointers.</figcaption></figure>

### (b) Floyd–Warshall

> [!hint]- Hint
> Floyd–Warshall computes the layered values $\textsf{dist}(u, v, r)$ exactly. Show that the paths behind them are consistent: the path stored for $(u, v)$, minus its last edge, is the path stored for $(u, \mathit{pred}[u, v])$.

> [!solution]- Solution
> **Modification.** The obvious one, with no tie-breaking: $\mathit{pred}[u, v] \leftarrow u$ for every edge, $\textsf{Null}$ otherwise; inside the test,
>
> ```text
>                 if dist[u, v] > dist[u, r] + dist[r, v]
>                     dist[u, v] ← dist[u, r] + dist[r, v]
>                     pred[u, v] ← pred[r, v]
> ```
>
> **Time.** $O(1)$ extra per step: $O(V^3)$.
>
> **Correctness, zero-length cycles included.** Phase $r$ changes neither row $r$ nor column $r$, so the array holds $\textsf{dist}(\cdot, \cdot, r)$ after phase $r$, and the pointers can be followed phase by phase. Let $P_r(u, v)$ be the path the recurrence chooses: the edge $u\to v$ for $r = 0$; for $r\ge 1$, $P_{r-1}(u, v)$ if the test fails and $P_{r-1}(u, r)\cdot P_{r-1}(r, v)$ if it succeeds. By induction on $r$:
> - (i) $P_r(u, v)$ is a path of length $\textsf{dist}(u, v, r)$ whose second-to-last vertex is $\mathit{pred}[u, v]$. When the test succeeds, $r$ occurs once in the concatenation; a repeated vertex would lie on a closed subwalk through $r$, of length $\ge 0$, and deleting that subwalk would leave a walk from $u$ to $v$ with intermediate vertices $< r$ and length $< \textsf{dist}(u, v, r-1)$ — impossible.
> - (ii) If $p = \mathit{pred}[u, v]\ne u$, then $P_r(u, v)$ minus its last edge is exactly $P_r(u, p)$. *Test succeeded at $(u, v)$:* if $p = r$ the prefix is $P_{r-1}(u, r) = P_r(u, r)$. Otherwise the prefix is $P_{r-1}(u, r)\cdot P_{r-1}(r, p)$ by (ii) for $r-1$, and the test also succeeded at $(u, p)$: otherwise $\textsf{dist}(u, p, r-1) + w(p\to v)$, the length of a walk from $u$ to $v$ with intermediate vertices $< r$, would be at most $\textsf{dist}(u, r, r-1) + \textsf{dist}(r, v, r-1) < \textsf{dist}(u, v, r-1)$. *Test failed at $(u, v)$:* the prefix is $P_{r-1}(u, p)$, and the test also failed at $(u, p)$: otherwise $\textsf{dist}(u, r, r-1) + \textsf{dist}(r, p, r-1) + w(p\to v)$ — at least $\textsf{dist}(u, r, r-1) + \textsf{dist}(r, v, r-1)$, as $p < r$ — would be smaller than $\textsf{dist}(u, v, r-1)$, and the test at $(u, v)$ would have succeeded.
>
> By (i) and (ii), following the pointers from $v$ walks $P_V(u, v)$ backwards, a shortest path. (The pair trick of (a) would also work here.)
>
> **Answer.** Set $\mathit{pred}[u, v]\leftarrow\mathit{pred}[r, v]$ whenever the test succeeds; $O(V^3)$ time, correct even with zero-length cycles.

## Exercise 9.2 — Correct distances despite negative cycles

> [!question] Exercise 9.2 (book p. 320)
> Modify each algorithm so that it returns the correct distances even when $G$ has negative cycles: for all $u, v$, $\mathit{dist}[u, v] = \infty$ if $u$ cannot reach $v$; $-\infty$ if $u$ can reach a negative cycle that can reach $v$; otherwise the length of a shortest path from $u$ to $v$.
>
> (a) Johnson's algorithm. (b) LeyzorekAPSP. (c) Floyd–Warshall.

> [!hint]- Hint
> Find a set $B$ of "bad" vertices, each on a negative closed walk, that contains every vertex of every negative cycle. Then $\textsf{dist}(u, v) = -\infty$ iff $u$ reaches some $x\in B$ that reaches $v$, and every other pair can be handled as if $B$ did not exist.

> [!solution]- Solution
> **Lemma.** Let $B$ contain every vertex of every negative cycle, and let every $x\in B$ lie on some closed walk of negative length.
> 1. $\textsf{dist}(u, v) = -\infty$ iff some $x\in B$ has $u\leadsto x\leadsto v$.
> 2. Otherwise no walk from $u$ to $v$ touches $B$, every cycle on such a walk has length $\ge 0$, and $\textsf{dist}(u, v)$ is the length of a shortest path from $u$ to $v$ — which lies in $G - B$.
>
> *Proof.* (1) A negative closed walk through $x$ contains a negative cycle $C$ whose vertices it visits, so $u\leadsto x\leadsto C\leadsto x\leadsto v$. Conversely, if $u$ reaches a negative cycle that reaches $v$, any vertex of it is in $B$. (2) A walk from $u$ to $v$ through $x\in B$, or containing a negative cycle (whose vertices are in $B$), would give (1). A walk whose cycles are all nonnegative is no shorter than the path left after cutting them out.
>
> **(a) Johnson.**
> 1. Compute the strong components. For each component $C$, run Bellman–Ford in $G[C]$ from any vertex of $C$; every cycle of $G$ lies inside one component, so $C$ contains a negative cycle iff this reports one. Let $B$ be the union of these bad components. Each $x\in B$ lies on a negative closed walk (go from $x$ to the negative cycle, around it often enough, and back inside $C$). Time $\sum_C O(\lvert C\rvert\cdot E(C)) = O(VE)$.
> 2. Run Johnson's algorithm on $G - B$, which has no negative cycle: $O(VE\log V)$.
> 3. For every $u$: search from $u$; then search once from all the vertices of $B$ it found; set $\mathit{dist}[u, v] = -\infty$ for every $v$ found by the second search. $O(V+E)$ per $u$.
> 4. Every other entry is Johnson's value from step 2 if $u, v\notin B$, and $\infty$ otherwise.
>
> By the lemma, step 3 finds exactly the $-\infty$ pairs. For an unmarked pair with $u\in B$ or $v\in B$, $v$ is unreachable (a reachable $v$ would have been marked, through $x = u$ or $x = v$); for $u, v\notin B$, part 2 of the lemma says $G - B$ has the right distance. **Time** $O(VE\log V + V^2)$, as for Johnson.
>
> **(b) and (c) LeyzorekAPSP and Floyd–Warshall.** Run the unmodified algorithm, then:
>
> ```text
> for all vertices x
>     if dist[x, x] < 0
>         for all vertices u
>             for all vertices v
>                 if dist[u, x] < ∞ and dist[x, v] < ∞
>                     dist[u, v] ← −∞
> ```
>
> Take $B = \{x : \mathit{dist}[x, x] < 0\}$ after the main loops. Each stored value is the length of a walk, so $x\in B$ lies on a negative closed walk, and $\mathit{dist}[u, x] < \infty$ iff $u$ reaches $x$ (a finite value is a walk; a path bounds the value from above). A vertex $x$ on a negative cycle has $\mathit{dist}[x, x]\le$ the length of that cycle $< 0$, so $x\in B$. By the lemma the loop marks exactly the $-\infty$ pairs. (Marking changes no finite-versus-$\infty$ status, and it can only lower a diagonal entry of a vertex that already lies on a negative closed walk, so updating in place is safe.) For every other reachable pair, the stored value is at most the length of a shortest path and is the length of a walk, which by part 2 of the lemma is at least $\textsf{dist}(u, v)$: it is exact.
>
> **Time.** One extra $O(V^3)$ pass: (b) $O(V^3\log V)$, (c) $O(V^3)$.
>
> **Answer.** (a) Bad strong components by Bellman–Ford, Johnson on the rest, and two searches per source for the $-\infty$ pairs, $O(VE\log V + V^2)$. (b), (c) Run the algorithm, then set $\mathit{dist}[u, v] = -\infty$ whenever some $x$ with $\mathit{dist}[x, x] < 0$ has $\mathit{dist}[u, x] < \infty$ and $\mathit{dist}[x, v] < \infty$; $O(V^3)$ extra.

## Exercise 9.3 — Returning a negative cycle

> [!question] Exercise 9.3 (book pp. 320–321)
> Modify each algorithm to return either the array of all distances or an explicit negative cycle of $G$ (any one, if there are several).
>
> (a) Johnson's algorithm. (b) LeyzorekAPSP. (c) Floyd–Warshall.

### (a) Johnson

> [!hint]- Hint
> Bellman–Ford maintains predecessor pointers. After it finds a tense edge $u\to v$, relax it and walk back from $v$ along the pointers.

> [!solution]- Solution
> **Modification.** Johnson's Bellman–Ford runs on $V+1$ vertices (the artificial source $s$ included). If an edge $u\to v$ is still tense after the $V$ rounds, relax it, follow $V+1$ predecessor pointers back from $v$ to some vertex $y$, and return the cycle $y\to\dots\to\mathit{pred}(\mathit{pred}(y))\to\mathit{pred}(y)\to y$, read off by following pointers from $y$ until $y$ reappears (and reversed). Otherwise continue as usual. Extra time $O(V)$; total $O(VE\log V)$.
>
> **Correctness.**
> - *Invariant:* for every pointer $p = \mathit{pred}(x)$, $\mathit{dist}(x)\ge\mathit{dist}(p) + w(p\to x)$ — equality when the pointer is set, after which $\mathit{dist}(p)$ only decreases and $\mathit{dist}(x)$ changes only together with $\mathit{pred}(x)$.
> - *Every cycle of pointers is negative.* Look at the relaxation that set the last pointer of the cycle, $\mathit{pred}(x_1)\leftarrow x_k$. Just before it, $x_k\to x_1$ was tense, $\mathit{dist}(x_1) > \mathit{dist}(x_k) + w(x_k\to x_1)$, and the other pointer edges of the cycle satisfied the invariant. Adding the $k$ inequalities around the cycle, the $\mathit{dist}$ terms cancel: $0 > $ the cycle's length.
> - *The walk from $v$ does not reach the source.* Otherwise the pointers from $v$ trace a path $P$ from $s$ to $v$ with at most $V$ edges, and the invariant summed along it gives $\mathit{dist}(v)\ge\mathit{dist}(s) + w(P) = w(P)$ ($s$ has no incoming edge, so $\mathit{dist}(s) = 0$). But after $V$ rounds $\mathit{dist}(v)$ was already at most $w(P)$, and the last relaxation lowered it. So the pointer walk never stops, and after $V+1$ steps it has entered a cycle of pointers, which avoids $s$.
>
> **Answer.** On a tense edge $u\to v$ after the last round, relax it, walk $V+1$ pointers back from $v$, and return the pointer cycle reached: a negative cycle, $O(V)$ extra time.

### (b) and (c) LeyzorekAPSP and Floyd–Warshall

> [!hint]- Hint
> A negative diagonal entry tells you where to look. Part (a)'s method works from any source.

> [!solution]- Solution
> **Modification.** Run the algorithm unchanged. If every $\mathit{dist}[x, x]$ is 0, return the array. Otherwise pick $x$ with $\mathit{dist}[x, x] < 0$, run Bellman–Ford from $x$ in $G$ with the cycle extraction of (a), and return its cycle.
>
> **Correctness.** If $G$ has a negative cycle, each of its vertices ends with a negative diagonal entry (Exercise 9.2); if not, no diagonal entry can become negative (it is the length of a closed walk), and the array is correct. A negative $\mathit{dist}[x, x]$ is a closed walk of negative length through $x$, so a negative cycle is reachable from $x$, and Bellman–Ford from $x$ ends with a tense edge. The argument of (a) works from any source $x$: the pointer walk could only stop at $x$ while $\mathit{pred}(x) = \textsf{Null}$, that is, while $\mathit{dist}(x) = 0$, and then the same contradiction applies.
>
> **Time.** $O(VE)\subseteq O(V^3)$ extra: (b) $O(V^3\log V)$, (c) $O(V^3)$.
>
> **Floyd–Warshall without Bellman–Ford.** Keep the predecessor pointers of 9.1(b), and before phase $r$ test every $u\ne r$: if $\mathit{dist}[u, r] + \mathit{dist}[r, u] < 0$, return the pointer path from $u$ to $r$ (row $u$) followed by the pointer path from $r$ to $u$ (row $r$). This is a simple negative cycle. At the first test that succeeds, every diagonal entry is still 0, so every cycle whose vertices, except perhaps one, come before $r$ has length $\ge 0$ — all that the proof of 9.1(b) uses — and the two pointer paths are paths with intermediate vertices before $r$ and lengths $\mathit{dist}[u, r]$ and $\mathit{dist}[r, u]$. A vertex $y$ shared by both would split the negative closed walk into the closed walks $u\leadsto y\leadsto u$ and $y\leadsto r\leadsto y$, both of length $\ge 0$. Conversely, a negative cycle whose last vertex in the loop order is $r$ makes the test succeed at phase $r$ or earlier. Extra time $O(V)$ per phase.
>
> **Answer.** Find $x$ with $\mathit{dist}[x, x] < 0$ and extract a cycle by Bellman–Ford from $x$, $O(V^3)$ extra; Floyd–Warshall can instead test $\mathit{dist}[u, r] + \mathit{dist}[r, u] < 0$ before each phase and return its two pointer paths.

## Exercise 9.4 — Zero-length cycles

> [!question] Exercise 9.4 (book p. 321)
> $G$ is a directed graph whose edge weights may be positive, negative or zero, without negative cycles.
>
> (a) Describe an efficient algorithm that finds a cycle of length 0 in $G$ or correctly reports that none exists.
>
> (b) Describe an efficient algorithm that constructs a subgraph $H$ of $G$ such that every vertex of $G$ is a vertex of $H$, every directed cycle of $H$ has length 0, and every directed cycle of length 0 in $G$ is a cycle of $H$. (So if $G$ has no zero cycle, $H$ has no edges.)

> [!hint]- Hint
> Johnson's reweighting does not change the length of any cycle, and afterwards all weights are $\ge 0$. When does a sum of nonnegative numbers vanish?

<!-- fig:a09x-zero -->
<figure class="cs-fig"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 238" width="640" height="238" role="img" style="font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-size:14px"><title>the same six-vertex graph twice: original weights with prices, and reduced weights with the zero cycles in red</title><defs><marker id="ARR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs><text x="36" y="36" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">π=−2</text><text x="150" y="36" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">π=0</text><text x="95" y="188" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">π=−3</text><text x="262" y="36" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">π=−4</text><text x="262" y="188" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">π=−2</text><text x="178" y="188" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">π=−2</text><text x="150" y="222" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">weights w and prices π = dist(s, ·)</text><text x="480" y="222" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">reduced weights w′ ≥ 0</text><path d="M55,62 L132.5,62" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="95" y="51" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">2</text><path d="M142.7,75.1 L103.6,144.7" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="132.1" y="116.4" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">−3</text><path d="M87.7,146.9 L48.6,77.3" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="57.9" y="116.4" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">1</text><path d="M165,62 L244.5,62" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="206" y="51" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">−1</text><path d="M268.6,75.5 Q286,111 269.7,144.3" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="288.3" y="111" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">2</text><path d="M255.4,146.5 Q238,111 254.3,77.7" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="235.7" y="111" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">−2</text><path d="M110,160 L160.5,160" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="136.5" y="149" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">1</text><path d="M193,160 L244.5,160" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="220" y="149" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">0</text><path d="M250.7,150.1 L163.2,73.5" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="198.8" y="119.3" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">3</text><path d="M385,62 L462.5,62" fill="none" stroke="var(--hi)" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="425" y="51" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">0</text><path d="M472.7,75.1 L433.6,144.7" fill="none" stroke="var(--hi)" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="462.1" y="116.4" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">0</text><path d="M417.7,146.9 L378.6,77.3" fill="none" stroke="var(--hi)" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="387.9" y="116.4" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">0</text><path d="M495,62 L574.5,62" fill="none" stroke="var(--muted)" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)" stroke-dasharray="4 3"/><text x="536" y="51" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">3</text><path d="M598.6,75.5 Q616,111 599.7,144.3" fill="none" stroke="var(--hi)" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="618.3" y="111" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">0</text><path d="M585.4,146.5 Q568,111 584.3,77.7" fill="none" stroke="var(--hi)" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="565.7" y="111" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">0</text><path d="M440,160 L490.5,160" fill="none" stroke="var(--accent)" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="466.5" y="149" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">0</text><path d="M523,160 L574.5,160" fill="none" stroke="var(--accent)" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="550" y="149" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">0</text><path d="M580.7,150.1 L493.2,73.5" fill="none" stroke="var(--muted)" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)" stroke-dasharray="4 3"/><text x="528.8" y="119.3" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">1</text><circle cx="40" cy="62" r="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="40" y="63" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">a</text><circle cx="150" cy="62" r="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="150" y="63" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">b</text><circle cx="95" cy="160" r="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="95" y="161" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">c</text><circle cx="262" cy="62" r="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="262" y="63" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">d</text><circle cx="262" cy="160" r="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="262" y="161" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">e</text><circle cx="178" cy="160" r="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="178" y="161" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">f</text><circle cx="370" cy="62" r="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="370" y="63" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">a</text><circle cx="480" cy="62" r="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="480" y="63" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">b</text><circle cx="425" cy="160" r="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="425" y="161" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">c</text><circle cx="592" cy="62" r="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="592" y="63" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">d</text><circle cx="592" cy="160" r="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="592" y="161" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">e</text><circle cx="508" cy="160" r="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="508" y="161" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">f</text></svg><figcaption><strong>Zero cycles become cycles of zero-weight edges.</strong> Left: a graph with negative edges but no negative cycle, with Bellman–Ford prices π(<i>v</i>) from an artificial source. Right: the reduced weights <i>w</i>′(<i>u</i>→<i>v</i>) = π(<i>u</i>) + <i>w</i>(<i>u</i>→<i>v</i>) − π(<i>v</i>). The zero-weight edges form <i>Z</i> (solid); <i>H</i> keeps the ones inside a strong component of <i>Z</i> (red): exactly the two zero cycles <i>a</i>→<i>b</i>→<i>c</i>→<i>a</i> and <i>d</i>→<i>e</i>→<i>d</i>. The blue edges <i>c</i>→<i>f</i>→<i>e</i> have reduced weight 0 but lie on no cycle of <i>Z</i>.</figcaption></figure>

### (a) Finding a zero cycle

> [!solution]- Solution
> **Algorithm.**
> 1. Add a vertex $s$ with 0-weight edges to all vertices and run Bellman–Ford from $s$; let $\pi(v) = \textsf{dist}(s, v)$ and $w'(u\to v) = \pi(u) + w(u\to v) - \pi(v)\ge 0$. $O(VE)$.
> 2. Let $Z$ be the subgraph of edges with $w'(e) = 0$, on all vertices. Run DFS cycle detection on $Z$ ([[2-algorithms/06-depth-first-search#62-detecting-cycles|§6.2]]); if it finds a back edge $x\to y$, return the cycle formed by the tree path from $y$ to $x$ and the edge $x\to y$; otherwise report that there is no zero cycle. $O(V+E)$.
>
> **Correctness.** Around a cycle the prices cancel, so its length under $w'$ equals its length under $w$. Since all $w'\ge 0$, a cycle has length 0 iff every edge on it has $w' = 0$, that is, iff it is a cycle of $Z$.
>
> **Time.** $O(VE)$.
>
> **Answer.** Reweight with Bellman–Ford prices; the zero cycles of $G$ are exactly the cycles of the zero-weight subgraph $Z$, so find one by DFS: $O(VE)$ time.

### (b) The zero-cycle subgraph

> [!solution]- Solution
> **Algorithm.** Compute $Z$ as in (a), then its strong components; let $H$ consist of all vertices of $G$ and the edges of $Z$ whose two endpoints lie in the same strong component of $Z$. Time $O(VE)$ for the prices plus $O(V+E)$.
>
> **Correctness.**
> - Every cycle of $H$ is a cycle of $Z$, so it has length 0 by (a).
> - A zero cycle of $G$ is a cycle of $Z$; its vertices reach each other along it, so they lie in one strong component of $Z$, and all its edges are in $H$.
> - Every edge $x\to y$ of $H$ lies on a zero cycle: $y$ reaches $x$ in $Z$ by a path, which with $x\to y$ forms a cycle of $Z$. So $H$ is exactly the union of all zero cycles of $G$, and it has no edges when there are none.
>
> **Example.** In the figure, the zero cycles are $a\to b\to c\to a$ and $d\to e\to d$; the other cycles, $b\to d\to e\to b$ and $b\to c\to f\to e\to b$, have lengths 4 and 1. The edges $c\to f$ and $f\to e$ have $w' = 0$ but join different strong components of $Z$, so $H$ drops them.
>
> **Answer.** $H$ = the zero-reduced-weight edges inside strong components of $Z$; $O(VE)$ time.

## Exercise 9.5 — Distances between vertex classes

> [!question] Exercise 9.5 (book p. 321)
> The vertices of a directed graph $G$ with arbitrary edge weights are partitioned into $k$ classes $V_1, \ldots, V_k$. For all $i$ and $j$ let
> $$
> \delta(i, j) = \min\{\textsf{dist}(v_i, v_j) \mid v_i\in V_i,\ v_j\in V_j\}.
> $$
> Describe an algorithm that computes $\delta(i, j)$ for all $i$ and $j$ in $O(VE + kV\log V)$ time.

> [!hint]- Hint
> Reweight once. Then each class needs one Dijkstra from a new super-source — but with which weights on the super-source's edges?

> [!solution]- Solution
> Assume $G$ has no negative cycle (otherwise the distances are not all defined, and the Bellman–Ford in step 1 reports it).
>
> **Graph.**
> 1. Prices: add a vertex $s$ with 0-weight edges $s\to v$, run Bellman–Ford, $\pi(v) = \textsf{dist}(s, v)\le 0$. Reduced weights $w'(u\to v) = \pi(u) + w(u\to v) - \pi(v)\ge 0$.
> 2. For each class $i$, the **directed** graph $G_i$: the vertices of $G$ plus a new vertex $z_i$; the edges of $G$ with weights $w'$, plus an edge $z_i\to x$ of weight $-\pi(x)\ge 0$ for every $x\in V_i$.
>
> **Problem.** Single-source shortest paths from $z_i$ in $G_i$. No edge enters $z_i$, so a path from $z_i$ to $v$ is an edge $z_i\to x$ with $x\in V_i$ followed by a path from $x$ to $v$ in $G$, and reweighting changes the latter by $\pi(x) - \pi(v)$:
> $$
> \textsf{dist}_{G_i}(z_i, v) = \min_{x\in V_i}\big(-\pi(x) + \textsf{dist}(x, v) + \pi(x) - \pi(v)\big) = \min_{x\in V_i}\textsf{dist}(x, v) - \pi(v).
> $$
> Hence $\delta(i, j) = \min_{v\in V_j}\big(\textsf{dist}_{G_i}(z_i, v) + \pi(v)\big)$.
>
> **Algorithm.** One Bellman–Ford; then for each $i$, Dijkstra from $z_i$ in $G_i$ (all weights $\ge 0$) with a Fibonacci heap, followed by one scan of the vertices that updates $\delta(i, \cdot)$.
>
> **Time.** $O(VE)$ for Bellman–Ford; $k$ Dijkstras on $V+1$ vertices and at most $E+V$ edges, $O(k(E + V\log V))$; the scans $O(kV)$. Since $k\le V$, $kE\le VE$, so the total is $O(VE + kV\log V)$. (With a binary heap: $O(VE + kE\log V)$.)
>
> **Trap.** Edges $z_i\to x$ of weight 0 in the reweighted graph compute $\min_{x}\big(\pi(x) + \textsf{dist}(x, v)\big) - \pi(v)$: the prices of different $x\in V_i$ differ, so the shift does not cancel.
>
> **Answer.** Reweight once; for each class, Dijkstra from a super-source with edges $z_i\to x$ of weight $-\pi(x)$, then $\delta(i, j) = \min_{v\in V_j}(\textsf{dist}(z_i, v) + \pi(v))$; $O(VE + kV\log V)$ time.

## Exercise 9.6 — Arbitrage

> [!question] Exercise 9.6 (book pp. 321–322)
> $n$ currencies are traded; one unit of currency $i$ buys $\mathit{Exch}[i, j]$ units of currency $j$ (not necessarily $\mathit{Exch}[i, j]\cdot\mathit{Exch}[j, i] = 1$). An **arbitrage cycle** is a cycle of trades that ends with more than it started with; the book's example: 1 dollar buys 120 yen, 1 yen buys 0.01 euro, 1 euro buys 1.2 dollars, so the cycle dollar → yen → euro → dollar turns 1 dollar into 1.44 dollars.
>
> (a) Assuming there is no arbitrage cycle, compute $\mathit{MaxAmt}[1\,..\,n]$, where $\mathit{MaxAmt}[i]$ is the most of currency $i$ one can obtain by trading, starting with one unit of currency 1.
>
> (b) Decide whether the rates admit an arbitrage cycle.
>
> (c) Return an arbitrage cycle if one exists.

> [!hint]- Hint
> Logarithms turn products into sums, and a maximum into a minimum if you negate them.

> [!solution]- Solution
> **Graph.** **Directed**, one vertex per currency; an edge $i\to j$ for all $i\ne j$ with $\mathit{Exch}[i, j] > 0$, of weight
> $$
> w(i\to j) = -\ln\mathit{Exch}[i, j].
> $$
> $n$ vertices and at most $n(n-1)$ edges. A sequence of trades along a walk $W$ multiplies the amount by $\prod\mathit{Exch} = e^{-w(W)}$: more money means a shorter walk, and an **arbitrage cycle is exactly a negative cycle**. In the example, $w = -\ln 120 - \ln 0.01 - \ln 1.2 = -\ln 1.44 < 0$.
>
> **(a)** With no arbitrage there is no negative cycle, so the best trade sequences are shortest paths: $\mathit{MaxAmt}[i] = e^{-\textsf{dist}(1, i)}$ (0 if $i$ is unreachable; $\mathit{MaxAmt}[1] = 1$). Weights can be negative (rates above 1), so use Bellman–Ford from vertex 1: $O(VE) = O(n^3)$. The same algorithm works on the amounts directly, with no logarithms: start with $\mathit{amt}[1] = 1$ and 0 elsewhere, and relax with "if $\mathit{amt}[i]\cdot\mathit{Exch}[i, j] > \mathit{amt}[j]$, set $\mathit{amt}[j]\leftarrow\mathit{amt}[i]\cdot\mathit{Exch}[i, j]$" — it is Bellman–Ford seen through the order-reversing map $d\mapsto e^{-d}$.
>
> **(b)** Arbitrage anywhere, not only through currency 1, is a negative cycle anywhere: add a source with 0-weight edges to every currency and run Bellman–Ford, $O(n^3)$. (Floyd–Warshall and a negative diagonal entry also work in $O(n^3)$.)
>
> **(c)** Extract the negative cycle with the predecessor walk of Exercise 9.3(a): still $O(n^3)$.
>
> **Trap.** Floating-point logarithms can misjudge a cycle whose product is extremely close to 1; the multiplicative version with exact rational arithmetic avoids that.
>
> **Answer.** Weights $-\ln\mathit{Exch}[i, j]$ turn the problem into shortest paths: (a) Bellman–Ford from currency 1, $\mathit{MaxAmt}[i] = e^{-\textsf{dist}(1, i)}$; (b) negative-cycle detection; (c) the negative cycle itself — each $O(n^3)$ time.

## Exercise 9.7 — Morty and the plumbus

> [!question] Exercise 9.7 (book p. 322)
> Morty gets a directed graph $G = (V, E)$ with nonnegative edge weights (in flinks) and disjoint vertex sets $P$ (plumbus storage units) and $F$ (fleebholes). He must choose a start vertex $s$ (his portal), a plumbus $p\in P$ and a fleebhole $f\in F$ such that $\textsf{dist}(p, f)\le 137$ (an unstabilized plumbus explodes after 137 flinks), minimizing the length of the shortest walk $s\leadsto p\leadsto f\leadsto s$. Describe and analyze an algorithm; assume a solution exists.

> [!hint]- Hint
> Morty chooses $s$ himself. For a fixed pair $(p, f)$, which $s$ is best?

> [!solution]- Solution
> **Observation.** The walk has length $\textsf{dist}(s, p) + \textsf{dist}(p, f) + \textsf{dist}(f, s)$. For fixed $p$ and $f$, the triangle inequality gives $\textsf{dist}(f, s) + \textsf{dist}(s, p)\ge\textsf{dist}(f, p)$ for every $s$, with equality for $s = p$. So the best choice is $s = p$ — open the portal at the plumbus — and the problem is to minimize
> $$
> \textsf{dist}(p, f) + \textsf{dist}(f, p)\quad\text{over } p\in P,\ f\in F \text{ with } \textsf{dist}(p, f)\le 137.
> $$
>
> **Graph.** $G$ itself (**directed**, weights $\ge 0$) and its reversal $\textsf{rev}(G)$, in which $\textsf{dist}_{\textsf{rev}(G)}(f, p) = \textsf{dist}_G(p, f)$.
>
> **Problem.** For every $f\in F$, single-source shortest paths from $f$ in $G$ (giving $\textsf{dist}(f, p)$ for all $p$) and from $f$ in $\textsf{rev}(G)$ (giving $\textsf{dist}(p, f)$). Then, over all pairs with $\textsf{dist}(p, f)\le 137$, take the smallest $\textsf{dist}(p, f) + \textsf{dist}(f, p)$, and output $s = p$, $p$, $f$. If $\lvert P\rvert < \lvert F\rvert$, run the searches from the plumbuses instead.
>
> **Algorithm.** Dijkstra (weights are nonnegative), $2\min(\lvert P\rvert, \lvert F\rvert)$ times; then a scan of all $\lvert P\rvert\cdot\lvert F\rvert$ pairs.
>
> **Time.** $O(\min(\lvert P\rvert, \lvert F\rvert)\cdot E\log V + \lvert P\rvert\lvert F\rvert)$, at most $O(VE\log V + V^2)$.
>
> **Answer.** Take $s = p$ and minimize $\textsf{dist}(p, f) + \textsf{dist}(f, p)$ subject to $\textsf{dist}(p, f)\le 137$, with Dijkstra in $G$ and $\textsf{rev}(G)$ from the smaller of $P$ and $F$.

## Exercise 9.8 — Deleting a vertex

> [!question] Exercise 9.8 (book pp. 322–323)
> $G = (V, E)$ is a directed graph with arbitrary edge weights (and, as in the chapter, no negative cycles).
>
> (a) Describe an $O(V^2)$-time algorithm that builds a weighted directed graph $G' = (V\setminus\{v\}, E')$ in which the distance between any two vertices equals their distance in $G$.
>
> (b) Given all distances in $G'$, compute all distances in $G$ from $v$ and to $v$ in $O(V^2)$ time.
>
> (c) Combine (a) and (b) into an all-pairs shortest-path algorithm that runs in $O(V^3)$ time. (It is almost Floyd–Warshall.)

### (a) Deleting $v$

> [!hint]- Hint
> A shortest path through $v$ uses two consecutive edges $u\to v\to x$. Give $G'$ a shortcut for each such pair.

> [!solution]- Solution
> **Algorithm.** With an adjacency matrix ($w = \infty$ for non-edges):
>
> ```text
> DeleteVertex(G, v):
>     for all vertices u ≠ v
>         for all vertices x ∉ {u, v}
>             w′(u→x) ← min{ w(u→x), w(u→v) + w(v→x) }
>     return G′ = (V ∖ {v}, the pairs with w′ < ∞)
> ```
>
> Loops $u\to v\to u$ are left out: their weight is $\ge 0$, so they never shorten anything. **Time** $O(V^2)$.
>
> **Correctness.** Let $a, b\ne v$. ($\textsf{dist}'\le\textsf{dist}$) A shortest path in $G$ from $a$ to $b$ either avoids $v$, so all its edges are in $G'$ with $w'\le w$, or passes through $v$ once, as $u\to v\to x$ with $u\ne x$, which the edge $u\to x$ of $G'$ replaces with $w'(u\to x)\le w(u\to v) + w(v\to x)$. ($\textsf{dist}'\ge\textsf{dist}$) Every edge of $G'$ stands for a path of $G$ of the same weight ($u\to x$ or $u\to v\to x$), so every path of $G'$ becomes a walk of $G$ of the same length, and with no negative cycles no walk is shorter than $\textsf{dist}$. The same translation shows that $G'$ has no negative cycle.
>
> **Answer.** Give every in-neighbor $u$ and out-neighbor $x$ of $v$ the edge $u\to x$ of weight $\min\{w(u\to x), w(u\to v) + w(v\to x)\}$; $O(V^2)$ time.

<!-- fig:a09x-eliminate -->
<figure class="cs-fig"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 620 236" width="620" height="236" role="img" style="font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-size:14px"><title>a five-vertex graph and the four-vertex graph obtained by deleting its middle vertex</title><defs><marker id="ARR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs><text x="150" y="222" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">G</text><text x="480" y="222" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">G′ on V ∖ {v}</text><path d="M53.2,59.2 L134.6,103.6" fill="none" stroke="var(--hi)" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="100.3" y="72.3" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">2</text><path d="M53.2,164.8 L134.6,120.4" fill="none" stroke="var(--hi)" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="89.7" y="132.3" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">−1</text><path d="M163.2,104.8 L244.6,60.4" fill="none" stroke="var(--hi)" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="199.7" y="72.3" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">3</text><path d="M163.2,119.2 L244.6,163.6" fill="none" stroke="var(--hi)" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="210.3" y="132.3" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">1</text><path d="M54.5,48.3 Q150,24 243,47.7" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="150" y="25.1" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">4</text><path d="M245.5,168.3 Q150,144 57,167.7" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="150" y="145.1" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">2</text><path d="M384.5,48.3 Q480,24 573,47.7" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="480" y="25.1" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">4</text><path d="M383.2,59.2 L574.6,163.6" fill="none" stroke="var(--accent)" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="436.9" y="75.9" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">3</text><path d="M383.2,164.8 L574.6,60.4" fill="none" stroke="var(--accent)" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="426.3" y="128.8" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">2</text><path d="M384.5,175.7 Q480,200 573,176.3" fill="none" stroke="var(--accent)" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="480" y="198.9" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">0</text><path d="M575.5,168.3 Q480,144 387,167.7" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="480" y="145.1" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">2</text><circle cx="40" cy="52" r="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="40" y="53" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">u₁</text><circle cx="40" cy="172" r="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="40" y="173" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">u₂</text><circle cx="150" cy="112" r="15" fill="var(--paper)" stroke="var(--hi)" stroke-width="1.6"/><text x="150" y="113" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">v</text><circle cx="260" cy="52" r="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="260" y="53" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">x₁</text><circle cx="260" cy="172" r="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="260" y="173" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">x₂</text><circle cx="370" cy="52" r="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="370" y="53" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">u₁</text><circle cx="370" cy="172" r="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="370" y="173" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">u₂</text><circle cx="590" cy="52" r="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="590" y="53" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">x₁</text><circle cx="590" cy="172" r="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="590" y="173" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">x₂</text></svg><figcaption><strong>Deleting a vertex without changing distances.</strong> Left: the four edges at <i>v</i> (red) and two other edges. Right: <i>G</i>′ on the remaining vertices; every in-neighbor <i>u</i> and out-neighbor <i>x</i> of <i>v</i> get an edge <i>u</i>→<i>x</i> of weight min{<i>w</i>(<i>u</i>→<i>x</i>), <i>w</i>(<i>u</i>→<i>v</i>) + <i>w</i>(<i>v</i>→<i>x</i>)}. Three new edges (blue) replace detours through <i>v</i>; <i>u</i>₁→<i>x</i>₁ keeps its weight 4 &lt; 2 + 3, and <i>x</i>₂→<i>u</i>₂ is unchanged.</figcaption></figure>

### (b) Putting $v$ back

> [!hint]- Hint
> A shortest path from $v$ leaves $v$ along one edge and never comes back.

> [!solution]- Solution
> **Formulas.** $\textsf{dist}(v, v) = 0$, and for every $x\ne v$
> $$
> \textsf{dist}(v, x) = \min_{v\to y\in E,\ y\ne v}\big(w(v\to y) + \textsf{dist}'(y, x)\big),
> $$
> $$
> \textsf{dist}(x, v) = \min_{y\to v\in E,\ y\ne v}\big(\textsf{dist}'(x, y) + w(y\to v)\big),
> $$
> with $\textsf{dist}'(x, x) = 0$ and $\min\varnothing = \infty$.
>
> **Correctness.** By (a), $\textsf{dist}' = \textsf{dist}$ on $V\setminus\{v\}$, so each term is the length of a walk from $v$ to $x$, hence $\ge\textsf{dist}(v, x)$. Conversely, a shortest path from $v$ to $x$ starts with some edge $v\to y$ and does not return to $v$, so its remainder is a path from $y$ to $x$, of length at least $\textsf{dist}(y, x) = \textsf{dist}'(y, x)$. Paths into $v$ are symmetric (last edge $y\to v$).
>
> **Time.** $O(V)$ per value, $2(V-1)$ values: $O(V^2)$.
>
> **Answer.** Minimize over the first edge out of $v$ (or the last edge into $v$), using the distances of $G'$; $O(V^2)$ time.

### (c) All pairs by elimination

> [!hint]- Hint
> Delete a vertex, recurse, put it back.

> [!solution]- Solution
> **Problem solved.** $\textsf{ElimAPSP}(G)$ returns all distances of a weighted directed graph $G$ with no negative cycle. (By (a), $G'$ is again such a graph, so the recursion is legitimate.)
>
> ```text
> ElimAPSP(G):
>     if G has one vertex v
>         return dist[v, v] = 0
>     v ← any vertex of G
>     G′ ← DeleteVertex(G, v)            ⟨⟨(a), O(V²)⟩⟩
>     dist ← ElimAPSP(G′)                ⟨⟨distances among V ∖ {v}⟩⟩
>     fill row v and column v by (b)     ⟨⟨O(V²)⟩⟩
>     return dist
> ```
>
> - **Base case:** one vertex, distance 0.
> - **Recursive call:** on $G'$, one vertex fewer; its distances are those of $G$ by (a).
> - **Combine:** (b) adds the distances from and to $v$.
> - **Time:** $T(V) = T(V-1) + O(V^2)$, so $T(V) = O(\sum_{i\le V} i^2) = O(V^3)$.
>
> **Why it is almost Floyd–Warshall.** Unrolled, the deletions perform $\mathit{dist}[u, x] \leftarrow \min\{\mathit{dist}[u, x], \mathit{dist}[u, v] + \mathit{dist}[v, x]\}$ for the deleted vertex $v$ over the vertices not yet deleted — Floyd–Warshall's phase for $v$, restricted to fewer pairs; the back-substitutions (b) fill in the rows and columns of the deleted vertices. It is Gaussian elimination in the min-plus world, and the state elimination of [[1-models-of-computation/04-nondeterministic-automata#48-nfa-to-regular-expression-state-elimination|§4.8]] in the regular-expression world.
>
> **Answer.** Delete $v$ by (a), recurse, restore $v$ by (b): $T(V) = T(V-1) + O(V^2) = O(V^3)$.

## Exercise 9.9 — Boolean matrix multiplication

> [!question] Exercise 9.9 (book p. 323)
> For boolean $n\times n$ matrices $A$ and $B$, the boolean product is $C[i, j] = \bigvee_k \big(A[i, k]\land B[k, j]\big)$.
>
> (a) Given a subroutine $\textsf{MinPlusMultiply}$ that computes min-plus products of $n\times n$ matrices in $T(n)$ time, multiply two boolean matrices in $O(T(n))$ time.
>
> (b) The same with a subroutine $\textsf{MatrixMultiply}$ for ordinary products.

> [!hint]- Hint
> Encode $\textsf{True}$ so that "and" becomes $+$ and "or" becomes $\min$ — or so that "and" becomes $\cdot$ and "or" becomes "the sum is positive".

> [!solution]- Solution
> **(a)** Let $A'[i, k] = 0$ if $A[i, k]$ and $1$ otherwise, and $B'$ likewise. Compute $C' = \textsf{MinPlusMultiply}(A', B')$ and set $C[i, j] = \textsf{True}$ iff $C'[i, j] = 0$. A term $A'[i, k] + B'[k, j]$ is 0 iff both entries are $\textsf{True}$, and the minimum over $k$ is 0 iff some term is.
>
> **(b)** Read $A$ and $B$ as 0/1 integer matrices and compute $C' = \textsf{MatrixMultiply}(A, B)$. Then $C'[i, j] = \sum_k A[i, k]B[k, j]$ counts the $k$ with $A[i, k]\land B[k, j]$, so $C[i, j] = \textsf{True}$ iff $C'[i, j] > 0$. The entries are at most $n$, so they are small integers.
>
> **Time.** One call plus $O(n^2)$ for the conversions, and $T(n) = \Omega(n^2)$ (the subroutine writes $n^2$ outputs): $O(T(n))$ in both cases.
>
> **Answer.** (a) $\textsf{True}\mapsto 0$, $\textsf{False}\mapsto 1$, min-plus product, test $= 0$. (b) 0/1 integers, ordinary product, test $> 0$. Both $O(T(n))$.

## Exercise 9.10 — Transitive closure by matrix multiplication

> [!question] Exercise 9.10 (book p. 323)
> The transitive closure of a directed graph $G$ has an edge $u\to v$ iff $G$ has a path from $u$ to $v$. Assume two $n\times n$ boolean matrices can be multiplied in $O(n^\omega)$ time for a constant $2\le\omega < 3$.
>
> (a) Compute the transitive closure of an $n$-vertex directed graph in $O(n^\omega\log n)$ time.
>
> (b) Do it in $O(n^\omega)$ time when $G$ is a dag. (The book's hint: do what you always do with dags, then divide and conquer; use $\omega\ge 2$.)
>
> (c) Do it in $O(n^\omega)$ time for an arbitrary directed graph. (Hint: turn it into a dag.)
>
> (d) Conversely, given a subroutine $\textsf{TransitiveClosure}$ that runs in $O(n^\alpha)$ time for a constant $2\le\alpha < 3$, multiply two boolean $n\times n$ matrices in $O(n^\alpha)$ time.

Below, $A$ is the adjacency matrix and $R^*$ the **reflexive** closure ($R^*[u, u] = 1$; paths of length 0 count). If the closure must contain $u\to u$ only when $u$ lies on a cycle, one more product gives it: $R^+ = A\cdot R^*$ ("a first edge, then any path").

### (a) Repeated squaring

> [!hint]- Hint
> Funny matrix multiplication with booleans.

> [!solution]- Solution
> **Algorithm.** $R\leftarrow A\lor I$; then $\lceil\lg n\rceil$ times $R\leftarrow R\cdot R$ (boolean product). Return $R = R^*$.
>
> **Correctness.** By induction, after $i$ squarings $R[u, v] = 1$ iff $G$ has a walk from $u$ to $v$ with at most $2^i$ edges: such a walk splits at its middle vertex into two walks of at most $2^{i-1}$ edges each (a walk with fewer edges uses the 1s on the diagonal). Every path has at most $n - 1\le 2^{\lceil\lg n\rceil}$ edges.
>
> **Time.** $\lceil\lg n\rceil$ products: $O(n^\omega\log n)$.
>
> **Answer.** Square $A\lor I$ $\lceil\lg n\rceil$ times: $O(n^\omega\log n)$ time.

### (b) Dags

> [!hint]- Hint
> Sort topologically and split the vertices into a first and a second half. Which of the four blocks of $R^*$ is zero, and how does a path get from the first half to the second?

> [!solution]- Solution
> **Setup.** Sort topologically ($O(n^2)$ with an adjacency matrix) and number the vertices in that order, so every edge goes from a smaller to a larger number. Split them into the first half $X$ and the second half $Y$. In block form,
> $$
> A = \begin{pmatrix} A_X & A_{XY}\\ 0 & A_Y\end{pmatrix}, \qquad R^* = \begin{pmatrix} R^*_X & R^*_X\, A_{XY}\, R^*_Y\\ 0 & R^*_Y\end{pmatrix},
> $$
> where $R^*_X$ and $R^*_Y$ are the reflexive closures of the induced subgraphs $G[X]$ and $G[Y]$.
>
> **Why.** No edge goes from $Y$ to $X$, so a path never returns to $X$ once it has left: paths between vertices of $X$ stay in $X$, paths between vertices of $Y$ stay in $Y$, nothing goes from $Y$ to $X$, and a path from $x\in X$ to $y\in Y$ is a path in $G[X]$ from $x$ to some $x'$, then one edge $x'\to y'$ with $y'\in Y$, then a path in $G[Y]$ from $y'$ to $y$ — exactly the boolean product $R^*_X A_{XY} R^*_Y$.
>
> **Recursive algorithm.** $\textsf{DagClosure}(A)$ returns $R^*$ for a dag whose vertices are numbered in topological order. *Base case:* one vertex, $R^* = (1)$. *Recursive calls:* on $G[X]$ and $G[Y]$, which are again topologically numbered dags. *Combine:* two boolean products of matrices of size at most $\lceil n/2\rceil$ (pad to square), and copy the blocks. *Time:*
> $$
> T(n) = 2T(n/2) + O(n^\omega).
> $$
> In the [[concepts/recursion-trees|recursion tree]], level $\ell$ costs $2^\ell (n/2^\ell)^\omega = n^\omega/2^{\ell(\omega-1)}$, a decreasing geometric series because $\omega > 1$: the root dominates, $T(n) = O(n^\omega)$. With the topological sort, $O(n^2 + n^\omega) = O(n^\omega)$ — here $\omega\ge 2$ is used.
>
> **Answer.** Sort topologically, recurse on both halves, and fill the off-diagonal block with $R^*_X A_{XY} R^*_Y$: $T(n) = 2T(n/2) + O(n^\omega) = O(n^\omega)$.

<!-- fig:a09x-dag-blocks -->
<figure class="cs-fig"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 236" width="640" height="236" role="img" style="font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-size:14px"><title>a dag drawn on a line split into two halves, and its 8 by 8 reachability matrix split into four blocks</title><defs><marker id="ARR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs><line x1="33" y1="140" x2="44.5" y2="140" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" marker-end="url(#ARR)"/><path d="M27.5,130.5 C36.4,98.4 79.6,98.4 87.2,128.3" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M63.5,130.5 C72.4,98.4 115.6,98.4 123.2,128.3" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><line x1="105" y1="140" x2="116.5" y2="140" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" marker-end="url(#ARR)"/><line x1="141" y1="140" x2="152.5" y2="140" stroke="var(--hi)" stroke-width="2.2" stroke-linecap="round" marker-end="url(#ARR)"/><path d="M99.5,130.5 C115.6,77.6 180.4,77.6 195.2,128.3" fill="none" stroke="var(--hi)" stroke-width="2.0" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M171.5,130.5 C180.4,98.4 223.6,98.4 231.2,128.3" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><line x1="213" y1="140" x2="224.5" y2="140" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" marker-end="url(#ARR)"/><line x1="249" y1="140" x2="260.5" y2="140" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" marker-end="url(#ARR)"/><path d="M63.5,130.5 C94.0,36.0 202.0,36.0 231.2,128.3" fill="none" stroke="var(--hi)" stroke-width="2.0" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><circle cx="22" cy="140" r="11" fill="var(--paper)" stroke="currentColor" stroke-width="1.4"/><text x="22" y="141" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">1</text><circle cx="58" cy="140" r="11" fill="var(--paper)" stroke="currentColor" stroke-width="1.4"/><text x="58" y="141" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">2</text><circle cx="94" cy="140" r="11" fill="var(--paper)" stroke="currentColor" stroke-width="1.4"/><text x="94" y="141" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">3</text><circle cx="130" cy="140" r="11" fill="var(--paper)" stroke="currentColor" stroke-width="1.4"/><text x="130" y="141" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">4</text><circle cx="166" cy="140" r="11" fill="var(--paper)" stroke="currentColor" stroke-width="1.4"/><text x="166" y="141" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">5</text><circle cx="202" cy="140" r="11" fill="var(--paper)" stroke="currentColor" stroke-width="1.4"/><text x="202" y="141" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">6</text><circle cx="238" cy="140" r="11" fill="var(--paper)" stroke="currentColor" stroke-width="1.4"/><text x="238" y="141" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">7</text><circle cx="274" cy="140" r="11" fill="var(--paper)" stroke="currentColor" stroke-width="1.4"/><text x="274" y="141" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">8</text><line x1="148" y1="30" x2="148" y2="176" stroke="var(--muted)" stroke-width="1.2" stroke-linecap="round" stroke-dasharray="4 3"/><text x="76" y="174" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">X</text><text x="220" y="174" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">Y</text><text x="148" y="206" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">vertices in topological order</text><text x="307" y="43.5" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:10px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">1</text><text x="325.5" y="25" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:10px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">1</text><text x="307" y="62.5" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:10px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">2</text><text x="344.5" y="25" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:10px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">2</text><text x="307" y="81.5" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:10px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">3</text><text x="363.5" y="25" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:10px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">3</text><text x="307" y="100.5" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:10px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">4</text><text x="382.5" y="25" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:10px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">4</text><text x="307" y="119.5" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:10px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">5</text><text x="401.5" y="25" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:10px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">5</text><text x="307" y="138.5" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:10px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">6</text><text x="420.5" y="25" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:10px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">6</text><text x="307" y="157.5" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:10px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">7</text><text x="439.5" y="25" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:10px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">7</text><text x="307" y="176.5" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:10px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">8</text><text x="458.5" y="25" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:10px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">8</text><rect x="319" y="37" width="13" height="13" rx="2" fill="var(--accent)" fill-opacity="0.55" stroke="none" stroke-width="0"/><rect x="338" y="37" width="13" height="13" rx="2" fill="var(--accent)" fill-opacity="0.55" stroke="none" stroke-width="0"/><rect x="357" y="37" width="13" height="13" rx="2" fill="var(--accent)" fill-opacity="0.55" stroke="none" stroke-width="0"/><rect x="376" y="37" width="13" height="13" rx="2" fill="var(--accent)" fill-opacity="0.55" stroke="none" stroke-width="0"/><rect x="395" y="37" width="13" height="13" rx="2" fill="var(--hi)" fill-opacity="0.75" stroke="none" stroke-width="0"/><rect x="414" y="37" width="13" height="13" rx="2" fill="var(--hi)" fill-opacity="0.75" stroke="none" stroke-width="0"/><rect x="433" y="37" width="13" height="13" rx="2" fill="var(--hi)" fill-opacity="0.75" stroke="none" stroke-width="0"/><rect x="452" y="37" width="13" height="13" rx="2" fill="var(--hi)" fill-opacity="0.75" stroke="none" stroke-width="0"/><rect x="338" y="56" width="13" height="13" rx="2" fill="var(--accent)" fill-opacity="0.55" stroke="none" stroke-width="0"/><rect x="376" y="56" width="13" height="13" rx="2" fill="var(--accent)" fill-opacity="0.55" stroke="none" stroke-width="0"/><rect x="395" y="56" width="13" height="13" rx="2" fill="var(--hi)" fill-opacity="0.75" stroke="none" stroke-width="0"/><rect x="433" y="56" width="13" height="13" rx="2" fill="var(--hi)" fill-opacity="0.75" stroke="none" stroke-width="0"/><rect x="452" y="56" width="13" height="13" rx="2" fill="var(--hi)" fill-opacity="0.75" stroke="none" stroke-width="0"/><rect x="357" y="75" width="13" height="13" rx="2" fill="var(--accent)" fill-opacity="0.55" stroke="none" stroke-width="0"/><rect x="376" y="75" width="13" height="13" rx="2" fill="var(--accent)" fill-opacity="0.55" stroke="none" stroke-width="0"/><rect x="395" y="75" width="13" height="13" rx="2" fill="var(--hi)" fill-opacity="0.75" stroke="none" stroke-width="0"/><rect x="414" y="75" width="13" height="13" rx="2" fill="var(--hi)" fill-opacity="0.75" stroke="none" stroke-width="0"/><rect x="433" y="75" width="13" height="13" rx="2" fill="var(--hi)" fill-opacity="0.75" stroke="none" stroke-width="0"/><rect x="452" y="75" width="13" height="13" rx="2" fill="var(--hi)" fill-opacity="0.75" stroke="none" stroke-width="0"/><rect x="376" y="94" width="13" height="13" rx="2" fill="var(--accent)" fill-opacity="0.55" stroke="none" stroke-width="0"/><rect x="395" y="94" width="13" height="13" rx="2" fill="var(--hi)" fill-opacity="0.75" stroke="none" stroke-width="0"/><rect x="433" y="94" width="13" height="13" rx="2" fill="var(--hi)" fill-opacity="0.75" stroke="none" stroke-width="0"/><rect x="452" y="94" width="13" height="13" rx="2" fill="var(--hi)" fill-opacity="0.75" stroke="none" stroke-width="0"/><rect x="395" y="113" width="13" height="13" rx="2" fill="var(--accent)" fill-opacity="0.55" stroke="none" stroke-width="0"/><rect x="433" y="113" width="13" height="13" rx="2" fill="var(--accent)" fill-opacity="0.55" stroke="none" stroke-width="0"/><rect x="452" y="113" width="13" height="13" rx="2" fill="var(--accent)" fill-opacity="0.55" stroke="none" stroke-width="0"/><rect x="414" y="132" width="13" height="13" rx="2" fill="var(--accent)" fill-opacity="0.55" stroke="none" stroke-width="0"/><rect x="433" y="132" width="13" height="13" rx="2" fill="var(--accent)" fill-opacity="0.55" stroke="none" stroke-width="0"/><rect x="452" y="132" width="13" height="13" rx="2" fill="var(--accent)" fill-opacity="0.55" stroke="none" stroke-width="0"/><rect x="433" y="151" width="13" height="13" rx="2" fill="var(--accent)" fill-opacity="0.55" stroke="none" stroke-width="0"/><rect x="452" y="151" width="13" height="13" rx="2" fill="var(--accent)" fill-opacity="0.55" stroke="none" stroke-width="0"/><rect x="452" y="170" width="13" height="13" rx="2" fill="var(--accent)" fill-opacity="0.55" stroke="none" stroke-width="0"/><rect x="316" y="34" width="152" height="152" rx="0" fill="none" stroke="currentColor" stroke-width="1.4"/><line x1="392" y1="34" x2="392" y2="186" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/><line x1="316" y1="110" x2="468" y2="110" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/><text x="354" y="148" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:22px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">0</text><text x="482" y="62" text-anchor="start" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">rows of X:</text><text x="490" y="83" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;"><tspan font-family="'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif" font-style="italic">R</tspan><tspan font-family="'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif" font-style="italic" font-size="10" dy="4">X</tspan><tspan dy="-4"> </tspan></text><text x="512" y="83" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:15px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">|</text><text x="524" y="83" text-anchor="start" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;"><tspan font-family="'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif" font-style="italic">R</tspan><tspan font-family="'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif" font-style="italic" font-size="10" dy="4">X</tspan><tspan dy="-4"> </tspan>·<tspan font-family="'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif" font-style="italic">A</tspan><tspan font-family="'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif" font-style="italic" font-size="10" dy="4">XY</tspan><tspan dy="-4"> </tspan>·<tspan font-family="'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif" font-style="italic">R</tspan><tspan font-family="'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif" font-style="italic" font-size="10" dy="4">Y</tspan><tspan dy="-4"> </tspan></text><text x="490" y="159" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">0</text><text x="512" y="159" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:15px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">|</text><text x="524" y="159" text-anchor="start" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;"><tspan font-family="'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif" font-style="italic">R</tspan><tspan font-family="'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif" font-style="italic" font-size="10" dy="4">Y</tspan><tspan dy="-4"> </tspan></text><text x="482" y="138" text-anchor="start" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">rows of Y:</text><text x="392" y="206" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">R*[i, j] = 1 iff i reaches j</text></svg><figcaption><strong>The closure of a topologically sorted dag, by blocks.</strong> Left: an 8-vertex dag; every edge goes right, and the three red edges cross from the first half <i>X</i> to the second half <i>Y</i>. Right: its reflexive reachability matrix. No path goes from <i>Y</i> back to <i>X</i> (zero block); paths inside <i>X</i> or inside <i>Y</i> stay there (two recursive closures); and every path from <i>X</i> to <i>Y</i> crosses exactly one red edge, so the red block is the boolean product <i>R<sub>X</sub></i> · <i>A<sub>XY</sub></i> · <i>R<sub>Y</sub></i>.</figcaption></figure>

### (c) Arbitrary directed graphs

> [!hint]- Hint
> Strong components.

> [!solution]- Solution
> **Algorithm.** Compute the strong components and the component graph $\textsf{scc}(G)$, a dag with $k\le n$ vertices: $O(n^2)$ time from the adjacency matrix ([[concepts/strongly-connected-components]]). Compute the reflexive closure $R^*_{\textsf{scc}}$ of $\textsf{scc}(G)$ by (b) in $O(k^\omega)\subseteq O(n^\omega)$ time. Set $R^*[u, v] = R^*_{\textsf{scc}}[S(u), S(v)]$, where $S(u)$ is the component of $u$: $O(n^2)$.
>
> **Correctness.** $u$ reaches $v$ in $G$ iff $S(u)$ reaches $S(v)$ in $\textsf{scc}(G)$ ([[2-algorithms/06-depth-first-search-exercises#exercise-60--reversal-and-the-strong-component-graph|Exercise 6.0(d)]]).
>
> **Time.** $O(n^2 + n^\omega) = O(n^\omega)$.
>
> **Answer.** Close the component dag by (b) and copy each entry to all pairs of vertices of the two components: $O(n^\omega)$ time.

### (d) Multiplication from closure

> [!hint]- Hint
> Build a graph in which a path of length 2 is exactly a witness $k$ for $A[i, k]\land B[k, j]$.

> [!solution]- Solution
> **Graph.** **Directed**, $3n$ vertices $a_1, \ldots, a_n$, $b_1, \ldots, b_n$, $c_1, \ldots, c_n$; an edge $a_i\to b_k$ iff $A[i, k]$, and an edge $b_k\to c_j$ iff $B[k, j]$. Built in $O(n^2)$ time.
>
> **Problem.** Reachability from each $a_i$ to each $c_j$. Edges only go from the $a$'s to the $b$'s and from the $b$'s to the $c$'s, so every path from $a_i$ to $c_j$ is $a_i\to b_k\to c_j$ for some $k$, which exists iff $A[i, k]\land B[k, j]$. So $C[i, j] = 1$ iff the closure contains $a_i\to c_j$.
>
> **Algorithm.** One call to $\textsf{TransitiveClosure}$ on the $3n$-vertex graph; read off the $(a_i, c_j)$ block.
>
> **Time.** $O((3n)^\alpha) = O(3^\alpha n^\alpha) = O(n^\alpha)$, plus $O(n^2)\subseteq O(n^\alpha)$ for building and reading.
>
> **Answer.** Three layers $a\to b\to c$ encoding $A$ and $B$; $C$ is the $(a, c)$ block of the closure; $O(n^\alpha)$ time.

### Sources for this page

Exercises 9.1–9.10 of Jeff Erickson, *Algorithms* (2019), pp. 320–323 (CC BY 4.0), paraphrased, with the book's arbitrage example; the solutions, the counterexample for LeyzorekAPSP's predecessor pointers, the zero-cycle example, the elimination example and the dag in the last figure are ours. Exercise 9.11's code (p. 324) is wrong as printed in three places, as noted at the top; none of 9.1–9.10 is wrong as printed, but the obvious predecessor update for LeyzorekAPSP (9.1(a)) needs a tie-break. Every algorithm on this page is checked by `tools/checks/a09x.py` against exhaustive enumeration of simple paths and simple cycles on thousands of random small digraphs with negative and zero edges: predecessor pointers traced back to shortest paths, distances with $\pm\infty$, returned negative and zero cycles, class distances, exact rational arbitrage, Morty's walks over all start vertices, vertex elimination, boolean products and closures; every number in the examples and figures is recomputed there, and so are the three defects of 9.11.
