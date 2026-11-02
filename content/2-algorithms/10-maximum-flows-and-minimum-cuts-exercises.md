---
title: "Chapter 10 exercises — Maximum flows and minimum cuts"
description: "Solutions to Exercises 10.0–10.9 of Erickson's Algorithms: checking a maximum flow, the difference of two flows in the residual network, how minimum cuts cross an edge and why they are closed under union and intersection, simplifying opposing edges (two parts false as printed), unique maximum flows and unique minimum cuts, acyclic maximum flows, unit-capacity networks with long shortest paths, deleting k edges, and tight bounds for flow decompositions."
tags: [exercises, algorithms, flows]
---

*Solved exercises for [[2-algorithms/10-maximum-flows-and-minimum-cuts|Chapter 10]] · book pp. 344–346 · statements paraphrased; see the book for the originals*

These are the chapter's first ten exercises, 10.0–10.9; none of them carries a marker. Skipped: 10.10, marked ♣ (it needs linear algebra from outside the book: flow spaces and their bases), and 10.11–10.20, beyond the first batch (10.13(c) and 10.19 are marked ♥). Flows are not taught in CS/ECE 374 this semester and are on no exam, so treat the page as practice with residual graphs, cuts and the proofs behind [[concepts/maximum-flow|maximum flows]] and [[concepts/ford-fulkerson|Ford–Fulkerson]]. Three statements need repair: 10.2 holds only for an edge of positive capacity; parts (a) and (b) of 10.4 are false as printed (part (c) is true); and the bounds of 10.9 need a connected graph (and a non-negative flow, which the book leaves implicit). Each is pointed out where it occurs. Write your own answer before opening a solution.

> [!tip] Notation and facts from the chapter, used below without re-proof
> - A **flow network** is a directed graph $G = (V, E)$ with a source $s$, a target $t$ and capacities $c(e)\ge 0$. A **flow** $f$ satisfies conservation at every vertex other than $s$ and $t$; it is **feasible** if $0\le f(e)\le c(e)$ for every edge; its **value** $\lvert f\rvert$ is the net flow out of $s$. $f$ **saturates** $e$ if $f(e) = c(e)$ and **avoids** $e$ if $f(e) = 0$. A **cut** $(S, T)$ partitions $V$ with $s\in S$, $t\in T$; its capacity $\lVert S, T\rVert$ is the total capacity of the edges from $S$ to $T$.
> - **Lemma 10.1** ([[2-algorithms/10-maximum-flows-and-minimum-cuts#102-cuts|§10.2]]): $\lvert f\rvert\le\lVert S, T\rVert$ for every feasible flow and every cut, with equality if and only if $f$ saturates every edge from $S$ to $T$ and avoids every edge from $T$ to $S$. With the **maxflow–mincut theorem** ([[2-algorithms/10-maximum-flows-and-minimum-cuts#103-the-maxflow-mincut-theorem|§10.3]]): *every* maximum flow saturates every edge leaving *every* minimum cut and avoids every edge entering it.
> - The **residual graph** $G_f$ has, for every edge $u\to v$, a residual edge $u\to v$ of capacity $c(u\to v) - f(u\to v)$ if that is positive, and a residual edge $v\to u$ of capacity $f(u\to v)$ if that is positive. (The book's $c_f$ assumes $G$ is **reduced** — at most one edge between any two vertices — and so do Exercises 10.1, 10.5 and 10.6 below. Subdividing every edge $u\to v$ into $u\to x\to v$ makes any network reduced without changing its flows in any essential way.)
> - **Augmenting.** Pushing $F\le$ (smallest residual capacity) along an $s\to t$ path of $G_f$ gives a feasible flow of value $\lvert f\rvert + F$; along a directed cycle of $G_f$ it gives a feasible flow of the *same* value — the same three-case proof. A feasible $f$ is maximum if and only if $G_f$ has no $s\to t$ path, and then the vertices reachable from $s$ in $G_f$ form the $S$ side of a minimum cut.
> - **Integrality theorem** ([[2-algorithms/10-maximum-flows-and-minimum-cuts#104-ford-and-fulkersons-augmenting-path-algorithm|§10.4]]) and **flow decomposition theorem** ([[2-algorithms/10-maximum-flows-and-minimum-cuts#105-combining-and-decomposing-flows|§10.5]]): every flow $f\ge 0$ with $\lvert f\rvert\ge 0$ is a positive combination of directed $s\to t$ paths and directed cycles that use only edges with $f > 0$; a **circulation** (value 0, conserved everywhere) needs only cycles.
> - **Times.** Ford–Fulkerson $O(E\lvert f^*\rvert)$ with integer capacities; Edmonds–Karp's shortest augmenting paths $O(VE^2)$ ([[2-algorithms/10-maximum-flows-and-minimum-cuts#106-edmonds-and-karps-algorithms|§10.6]]); in general, "maximum flows can be computed in $O(VE)$ time" (Orlin, [[2-algorithms/10-maximum-flows-and-minimum-cuts#107-further-progress|§10.7]]). [[concepts/whatever-first-search|Whatever-first search]] and [[concepts/strongly-connected-components|strong components]] take $O(V+E)$.

## Exercise 10.0 — Is this a maximum flow?

> [!question] Exercise 10.0 (book p. 344)
> You are given a directed graph $G = (V, E)$, two vertices $s$ and $t$, capacities $c\colon E\to\mathbb{R}^+$ and an arbitrary function $f\colon E\to\mathbb{R}$. Describe an algorithm that decides whether $f$ is a maximum $(s,t)$-flow in $G$.

> [!hint]- Hint
> $f$ is an arbitrary function: first make sure it is a feasible flow at all. Then reuse the proof of the maxflow–mincut theorem.

> [!solution]- Solution
> ```text
> IsMaxFlow(G, c, s, t, f):
>     for every edge e
>         if f(e) < 0 or f(e) > c(e)
>             return False                        ⟨⟨not feasible⟩⟩
>     for every vertex v other than s and t
>         if the flow into v ≠ the flow out of v
>             return False                        ⟨⟨not a flow⟩⟩
>     build the residual graph G_f
>     if t is reachable from s in G_f              ⟨⟨whatever-first search⟩⟩
>         return False
>     return True
> ```
>
> **Correctness.** A function that fails one of the first two tests is not a feasible flow. Suppose $f$ passes them. If $G_f$ has an $s\to t$ path, augmenting along it gives a feasible flow of larger value, so $f$ is not maximum. If it has none, let $S$ be the set of vertices reachable from $s$ in $G_f$ and $T = V\setminus S$: no residual edge leaves $S$, so $f$ saturates every edge from $S$ to $T$ and avoids every edge from $T$ to $S$, and Lemma 10.1 gives $\lvert f\rvert = \lVert S, T\rVert$, which no feasible flow exceeds. The argument never uses $\lvert f\rvert\ge 0$, so feasible flows of negative value (flow pushed from $t$ back to $s$) are handled too.
>
> **Time.** Two passes over the edges, a residual graph with at most $2E$ edges, one search: $O(V + E)$. The test also works with parallel and opposite edges, with one residual edge per edge and direction.
>
> **Answer.** Check $0\le f\le c$ and conservation, then check that $t$ is not reachable from $s$ in $G_f$: $O(V+E)$ time.

> [!trap]
> - Computing a maximum flow yourself and comparing values also works, but costs $O(VE)$ instead of $O(V + E)$.
> - "No augmenting path" alone is not enough: an infeasible or non-conserving $f$ can pass that test.

## Exercise 10.1 — Two flows differ by a flow in the residual network

> [!question] Exercise 10.1 (book p. 344)
> Let $f$ and $f'$ be feasible $(s,t)$-flows in a flow network $G$ with $\lvert f'\rvert > \lvert f\rvert$. Prove that the residual network $G_f$ has a feasible $(s,t)$-flow of value $\lvert f'\rvert - \lvert f\rvert$.

> [!hint]- Hint
> Compare $f'$ with $f$ edge by edge. Where $f'$ is larger it uses spare capacity; where it is smaller it undoes flow of $f$, which is residual capacity in the opposite direction.

> [!solution]- Solution
> As in the chapter's definition of $G_f$, $G$ is reduced. For every edge $u\to v$ of $G$ let $\Delta(u\to v) = f'(u\to v) - f(u\to v)$, and define $g$ on ordered pairs of vertices by
> $$
> g(u\to v) = \Delta(u\to v)\ \text{ if } \Delta(u\to v) > 0, \qquad g(v\to u) = -\Delta(u\to v)\ \text{ if } \Delta(u\to v) < 0,
> $$
> and $g = 0$ everywhere else. Because $G$ is reduced, each ordered pair receives a value from at most one edge.
>
> **$g$ fits in $G_f$.** If $\Delta(u\to v) > 0$, then $g(u\to v) = f'(u\to v) - f(u\to v)\le c(u\to v) - f(u\to v) = c_f(u\to v)$, because $f'\le c$. If $\Delta(u\to v) < 0$, then $g(v\to u) = f(u\to v) - f'(u\to v)\le f(u\to v) = c_f(v\to u)$, because $f'\ge 0$. So $0\le g\le c_f$, and $g$ is positive only on edges of $G_f$.
>
> **$g$ is a flow of the right value.** Whichever direction it is placed in, the contribution of the edge $u\to v$ to $g$ adds $\Delta(u\to v)$ to the net flow out of $u$ and subtracts it from the net flow out of $v$ — exactly what $f' - f$ does. So at every vertex the net flow out under $g$ is the net flow out under $f'$ minus that under $f$: zero at every $v\ne s, t$, and $\lvert f'\rvert - \lvert f\rvert$ at $s$.
>
> (Conversely, adding a feasible flow of $G_f$ to $f$ gives a feasible flow of $G$. Together with the case $f' = f^*$: the maximum flow value of $G_f$ is exactly $\lvert f^*\rvert - \lvert f\rvert$, the fact the analysis of fattest augmenting paths in §10.6 uses.)
>
> **Answer.** Put the positive part of $f' - f$ on forward residual edges and its negative part on backward residual edges: a feasible flow in $G_f$ of value $\lvert f'\rvert - \lvert f\rvert$.

## Exercise 10.2 — An edge never crosses minimum cuts both ways

> [!question] Exercise 10.2 (book p. 344)
> Let $u\to v$ be an edge of a flow network $G$. Prove: if some minimum $(s,t)$-cut $(S, T)$ has $u\in S$ and $v\in T$, then no minimum cut $(S', T')$ has $u\in T'$ and $v\in S'$.

> [!hint]- Hint
> Fix one maximum flow $f^*$. What does Lemma 10.1 say about $f^*(u\to v)$ for each of the two cuts?

> [!solution]- Solution
> Let $f^*$ be a maximum flow. It saturates every edge leaving a minimum cut and avoids every edge entering one. The first cut has $u\to v$ leaving $S$, so $f^*(u\to v) = c(u\to v)$; the second would have $u\to v$ entering $S'$, so $f^*(u\to v) = 0$. Both together force $c(u\to v) = 0$. Hence the claim holds for every edge of positive capacity — in particular whenever all capacities are positive, as in Exercise 10.0.
>
> **The hypothesis is needed.** The chapter allows capacity 0. In the network with edges $s\to t$ (capacity 1) and $u\to v$ (capacity 0), every cut has capacity 1, so all four placements of $u$ and $v$ give minimum cuts, including $u\in S, v\in T$ and $u\in T', v\in S'$.
>
> **Answer.** One maximum flow would need $f^*(u\to v) = c(u\to v)$ and $f^*(u\to v) = 0$, so $c(u\to v) = 0$ — impossible if the edge has positive capacity, which the statement must assume.

## Exercise 10.3 — Union and intersection of minimum cuts

> [!question] Exercise 10.3 (book p. 344)
> Let $(S, T)$ and $(S', T')$ be minimum $(s,t)$-cuts in a flow network $G$. Prove that $(S\cap S', T\cup T')$ and $(S\cup S', T\cap T')$ are minimum $(s,t)$-cuts too.

> [!hint]- Hint
> Use one maximum flow again: check that it saturates every edge leaving $S\cap S'$ and avoids every edge entering it.

> [!solution]- Solution
> Both pairs are cuts: $s\in S\cap S'\subseteq S\cup S'$, $t\notin S\cup S'$, and $T\cup T' = V\setminus(S\cap S')$, $T\cap T' = V\setminus(S\cup S')$. Let $f^*$ be a maximum flow; it saturates every edge leaving $S$ or $S'$ and avoids every edge entering $S$ or $S'$.
>
> - **$A = S\cap S'$.** An edge $x\to y$ leaving $A$ has $x$ in both sets and $y$ outside at least one of them, so it leaves $S$ or leaves $S'$: saturated. An edge entering $A$ has $y$ in both sets and $x$ outside one of them, so it enters $S$ or $S'$: avoided.
> - **$B = S\cup S'$.** An edge leaving $B$ starts in $S$ or in $S'$ and ends outside both, so it leaves that set: saturated. An edge entering $B$ ends in $S$ or in $S'$ and starts outside both, so it enters that set: avoided.
>
> By Lemma 10.1, $\lvert f^*\rvert = \lVert A, V\setminus A\rVert = \lVert B, V\setminus B\rVert$, so both are minimum cuts. (Equivalently: cut capacity is submodular, $\lVert S\cap S'\rVert + \lVert S\cup S'\rVert\le\lVert S\rVert + \lVert S'\rVert$, writing $\lVert X\rVert$ for $\lVert X, V\setminus X\rVert$, and neither term on the left can be below the minimum.)
>
> So the minimum cuts have a smallest $S$ side (the intersection of all of them) and a largest one (their union) — Exercise 10.5(b) finds both.
>
> **Answer.** A maximum flow saturates every edge leaving, and avoids every edge entering, both $S\cap S'$ and $S\cup S'$; Lemma 10.1 makes both minimum cuts.

## Exercise 10.4 — Simplifying opposing edges (false as printed)

> [!question] Exercise 10.4 (book pp. 344–345)
> $G$ contains an opposing pair of edges $u\to v$ and $v\to u$, both with positive capacity. $G'$ is obtained by decreasing both capacities by $m = \min\{c(u\to v), c(v\to u)\}$ and deleting the edges whose capacity becomes 0. (The book's Figure 10.11: capacities 10 and 7 become a single edge of capacity 3 in the direction of the 10; capacities 5 and 5 disappear.)
>
> (a) Prove that every maximum $(s,t)$-flow in $G'$ is also a maximum $(s,t)$-flow in $G$. (So simplifying every opposing pair would give a reduced network with the same maximum flow value.)
>
> (b) Prove that every minimum $(s,t)$-cut in $G$ is also a minimum $(s,t)$-cut in $G'$, and vice versa.
>
> (c) Prove that some maximum $(s,t)$-flow in $G$ is *not* a maximum $(s,t)$-flow in $G'$.

### (a) and (b) — false as printed

> [!hint]- Hint
> Compute the capacity of a cut that separates $u$ from $v$, before and after. In $G$, how much net flow can go from $v$ to $u$? In $G'$?

> [!solution]- Solution
> **What the simplification does to cuts.** A cut with $u\in S$, $v\in T$ pays $c(u\to v)$ in $G$ and $c(u\to v) - m$ in $G'$; a cut with $v\in S$, $u\in T$ pays $c(v\to u)$, then $c(v\to u) - m$; a cut with $u, v$ on the same side pays for neither edge. So
> $$
> \lVert S, T\rVert_{G'} = \begin{cases}\lVert S, T\rVert_G - m & \text{if the cut separates } u \text{ and } v,\\ \lVert S, T\rVert_G & \text{otherwise.}\end{cases}
> $$
> The cuts that separate $u$ and $v$ all get cheaper, so the minimum can move and drop. In flow terms: in $G$ the net flow from $u$ to $v$ can be anything from $-c(v\to u)$ to $c(u\to v)$, but in $G'$ only one direction survives, with capacity reduced by $m$.
>
> **Counterexample (figure).** Edges $s\to u$ (1), $u\to v$ (7), $v\to u$ (10), $v\to t$ (1); here $m = 7$, and $G'$ has $s\to u$ (1), $v\to u$ (3), $v\to t$ (1).
>
> | $S$ | $\{s\}$ | $\{s, u\}$ | $\{s, v\}$ | $\{s, u, v\}$ |
> |---|---|---|---|---|
> | $\lVert S, T\rVert$ in $G$ | **1** | 7 | 12 | **1** |
> | $\lVert S, T\rVert$ in $G'$ | 1 | **0** | 5 | 1 |
>
> - (a) fails: $G'$ has no path from $s$ to $t$, so the zero flow is a maximum flow in $G'$; it is not one in $G$, whose maximum flow is 1 (along $s\to u\to v\to t$).
> - (b) fails in both directions: $G$'s minimum cuts are $\{s\}$ and $\{s, u, v\}$, and $G'$'s only minimum cut is $\{s, u\}$.
>
> The correct ways to get a reduced network are the subdivision of §10.3 (replace $u\to v$ by $u\to x\to v$), or, for a given flow, cancelling: subtracting $\min\{f(u\to v), f(v\to u)\}$ from both edges keeps the flow feasible with the same value.
>
> **Answer.** False: on $s\to u$ (1), $u\to v$ (7), $v\to u$ (10), $v\to t$ (1), the maximum flow drops from 1 to 0 and the minimum cuts change from $\{s\}, \{s,u,v\}$ to $\{s,u\}$, because every cut separating $u$ and $v$ loses $m$.

<!-- fig:a10x-opposing -->
<figure class="cs-fig"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 580 262" width="580" height="262" role="img" style="font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-size:14px"><title>two four-vertex networks s, u, v, t; top with an opposing pair 7 and 10, bottom with a single edge v to u of capacity 3; dashed minimum cuts</title><defs><marker id="ARR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs><text x="22" y="74" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:17px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">G</text><text x="22" y="196" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:17px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">G′</text><line x1="174" y1="28" x2="174" y2="114" stroke="var(--hi)" stroke-width="1.6" stroke-linecap="round" stroke-dasharray="5 4"/><text x="174" y="18" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">{s}: 1</text><line x1="474" y1="28" x2="474" y2="114" stroke="var(--hi)" stroke-width="1.6" stroke-linecap="round" stroke-dasharray="5 4"/><text x="474" y="18" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">{s, u, v}: 1</text><line x1="252" y1="156" x2="252" y2="236" stroke="var(--hi)" stroke-width="1.6" stroke-linecap="round" stroke-dasharray="5 4"/><text x="252" y="248" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">{s, u}: 0</text><text x="92" y="116" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">max flow 1</text><text x="92" y="238" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">max flow 0</text><path d="M87,74 L190.5,74" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="140" y="62" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">1</text><path d="M225.5,67 Q290,38 352.2,66" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="290" y="41.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">7</text><path d="M354.5,81 Q290,110 227.8,82" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="290" y="106.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">10</text><path d="M387,74 L490.5,74" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="440" y="62" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">1</text><path d="M87,196 L190.5,196" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="140" y="184" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">1</text><path d="M353,196 L229.5,196" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="290" y="208" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">3</text><path d="M387,196 L490.5,196" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="440" y="184" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">1</text><circle cx="70" cy="74" r="17" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="70" y="75" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">s</text><circle cx="70" cy="196" r="17" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="70" y="197" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">s</text><circle cx="210" cy="74" r="17" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="210" y="75" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">u</text><circle cx="210" cy="196" r="17" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="210" y="197" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">u</text><circle cx="370" cy="74" r="17" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="370" y="75" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">v</text><circle cx="370" cy="196" r="17" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="370" y="197" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">v</text><circle cx="510" cy="74" r="17" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="510" y="75" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">t</text><circle cx="510" cy="196" r="17" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="510" y="197" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">t</text></svg><figcaption><strong>Exercise 10.4 is false as printed.</strong> Top: <i>G</i>, with the opposing pair <i>u</i>→<i>v</i> (7) and <i>v</i>→<i>u</i> (10). Its maximum flow is 1, and its minimum cuts (dashed, labeled <i>S</i>: capacity) are {<i>s</i>} and {<i>s</i>, <i>u</i>, <i>v</i>}. Bottom: <i>G</i>′, where both capacities drop by 7, so only <i>v</i>→<i>u</i> survives, with capacity 3. Now <i>t</i> is unreachable, the maximum flow is 0, and the only minimum cut is {<i>s</i>, <i>u</i>}, which costs 7 in <i>G</i>. Every cut that separates <i>u</i> from <i>v</i> gets 7 cheaper; the others keep their capacity.</figcaption></figure>

### (c) A maximum flow that the simplified network cannot carry

> [!hint]- Hint
> The 2-cycle $u\to v\to u$ can carry flow without changing the value or anything else.

> [!solution]- Solution
> Take any maximum flow $f$ of $G$, and say $c(u\to v)\ge c(v\to u) = m$ (the other case is symmetric). Then $G'$ has no edge $v\to u$, and $u\to v$ has capacity $c(u\to v) - m$ (it is deleted if that is 0). If $f(v\to u) > 0$ or $f(u\to v) > c(u\to v) - m$, then $f$ does not even fit in $G'$. Otherwise push $m$ units around the 2-cycle $u\to v\to u$: the new flow has $f(u\to v) + m\le c(u\to v)$ and $f(v\to u) = m\le c(v\to u)$, so it is feasible; conservation and value are unchanged (a cycle enters and leaves each of its vertices once). It is a maximum flow of $G$ with $f(v\to u) = m > 0$ on an edge that $G'$ does not have.
>
> **Answer.** If necessary push $m$ around $u\to v\to u$: the result is a maximum flow of $G$ that uses capacity $G'$ no longer has, so it is not a flow in $G'$ at all.

## Exercise 10.5 — Unique maximum flows and unique minimum cuts

> [!question] Exercise 10.5 (book p. 345)
> (a) Describe an efficient algorithm to decide whether a given flow network has a *unique* maximum $(s,t)$-flow.
>
> (b) Describe an efficient algorithm to decide whether a given flow network has a *unique* minimum $(s,t)$-cut.
>
> (c) Describe a flow network with a unique maximum flow but more than one minimum cut.
>
> (d) Describe a flow network with a unique minimum cut but more than one maximum flow.

### (a) A unique maximum flow

> [!hint]- Hint
> Two maximum flows differ by a circulation in the residual graph (Exercise 10.1 with equal values). But careful: every edge carrying flow strictly between 0 and its capacity puts a harmless two-vertex cycle into $G_f$.

> [!solution]- Solution
> $G$ is reduced. Compute a maximum flow $f$ and its residual graph $G_f$.
>
> **Claim.** $f$ is the only maximum flow if and only if $G_f$ has no directed cycle through three or more vertices.
>
> - *A long cycle gives a second flow.* Push $\varepsilon$ = (smallest residual capacity) around a cycle $C$ of $G_f$ with at least three vertices. The result is feasible with the same value. The vertices of $C$ are distinct, so consecutive pairs of $C$ are different pairs of vertices, and since $G$ is reduced they belong to different edges of $G$, each of which changes by $\pm\varepsilon$. A second maximum flow.
> - *A second flow gives a long cycle.* If $f'\ne f$ is another maximum flow, the flow $g$ built in Exercise 10.1 (the construction never uses $\lvert f'\rvert > \lvert f\rvert$) has value $\lvert f'\rvert - \lvert f\rvert = 0$, so it is a nonzero circulation in $G_f$, and it is never positive on both $x\to y$ and $y\to x$. By flow decomposition it is a positive combination of directed cycles of $G_f$ on which $g > 0$, and none of them has only two vertices.
>
> **Testing for a long cycle.** Every cycle lies inside one strong component of $G_f$. A strong component $K$ contains no cycle through three or more vertices if and only if it is a **bidirected tree**: every residual edge inside $K$ comes with its reversal, and the vertex pairs joined inside $K$ form a tree, so $K$ contains exactly $2(\lvert K\rvert - 1)$ residual edges. (If $x\to y$ is inside $K$ but $y\to x$ is not an edge, a shortest path from $y$ back to $x$ closes a cycle with at least three vertices. If all edges are paired and the pairs contain an undirected cycle, it can be traversed in one direction: a long directed cycle. A bidirected tree has only two-vertex cycles.)
>
> **Algorithm.** Maximum flow; residual graph; strong components; for each component check that every inner edge has its reversal and that there are $2(\lvert K\rvert - 1)$ inner edges. The flow is unique if and only if every component passes.
>
> **Time.** $O(VE)$ for the maximum flow, $O(V + E)$ for the rest.
>
> **Answer.** The maximum flow $f^*$ is unique if and only if every strong component of $G_{f^*}$ is a bidirected tree (no residual cycle through three or more vertices): $O(VE)$ time.

> [!trap]
> "Unique if and only if $G_{f^*}$ is acyclic" is wrong: in $s\to a$ (capacity 1), $a\to t$ (capacity 2) the maximum flow is unique, but $a\to t$ is half full, so $G_{f^*}$ contains the 2-cycle $a\to t\to a$. Pushing flow around it changes nothing.

<!-- fig:a10x-residual -->
<figure class="cs-fig"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 620 205" width="620" height="205" role="img" style="font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-size:14px"><title>left: four-vertex network with flow labels; right: its residual graph with a red three-vertex cycle</title><defs><marker id="ARR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs><text x="165" y="190" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">a maximum flow (flow/capacity)</text><text x="475" y="190" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">residual graph</text><path d="M56,130 L131.5,130" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="95" y="117" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">1/1</text><path d="M160.5,118 L207.8,63.9" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="194.8" y="98.6" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">0/2</text><path d="M230.5,62 L277.8,116.1" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="264.8" y="81.4" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">0/2</text><path d="M166,130 L271.5,130" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="220" y="117" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">1/2</text><path d="M444,130 L368.5,130" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="405" y="141" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">1</text><path d="M470.5,118 L517.8,63.9" fill="none" stroke="var(--hi)" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="503.3" y="97.2" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">2</text><path d="M540.5,62 L587.8,116.1" fill="none" stroke="var(--hi)" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="573.3" y="82.8" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">2</text><path d="M474.9,124.1 Q530,102 582.8,123.1" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="530" y="102" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">1</text><path d="M585.1,135.9 Q530,158 477.2,136.9" fill="none" stroke="var(--hi)" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="530" y="158" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">1</text><circle cx="40" cy="130" r="16" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="40" y="131" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">s</text><circle cx="350" cy="130" r="16" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="350" y="131" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">s</text><circle cx="150" cy="130" r="16" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="150" y="131" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">a</text><circle cx="460" cy="130" r="16" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="460" y="131" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">a</text><circle cx="220" cy="50" r="16" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="220" y="51" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">b</text><circle cx="530" cy="50" r="16" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="530" y="51" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">b</text><circle cx="290" cy="130" r="16" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="290" y="131" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">t</text><circle cx="600" cy="130" r="16" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="600" y="131" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">t</text></svg><figcaption><strong>The uniqueness test of Exercise 10.5(a) on the network of 10.5(d).</strong> Left: a maximum flow of value 1. Right: its residual graph. The edge <i>a</i>→<i>t</i> is half full, so the residual graph contains both <i>a</i>→<i>t</i> and <i>t</i>→<i>a</i>; such two-vertex cycles come from a single edge and do not count. The red cycle <i>a</i>→<i>b</i>→<i>t</i>→<i>a</i> has three vertices: pushing 1 unit around it gives a second maximum flow, along <i>s</i>→<i>a</i>→<i>b</i>→<i>t</i>. The minimum cut is unique, as 10.5(b) predicts: <i>s</i> reaches nothing, and every other vertex reaches <i>t</i>.</figcaption></figure>

### (b) A unique minimum cut

> [!hint]- Hint
> By Exercise 10.3 the minimum cuts lie between a smallest and a largest one. Find both with two searches in $G_{f^*}$.

> [!solution]- Solution
> Compute a maximum flow $f$. Let $R_s$ be the set of vertices reachable from $s$ in $G_f$, and $R^t$ the set of vertices that can reach $t$ in $G_f$ (whatever-first search from $t$ in the reversal of $G_f$). The two sets are disjoint, since $G_f$ has no $s\to t$ path.
>
> - *Every minimum cut $(S, T)$ has $R_s\subseteq S$ and $R^t\subseteq T$.* The flow $f$ saturates every edge from $S$ to $T$ and avoids every edge from $T$ to $S$, so no residual edge leaves $S$: a residual edge $x\to y$ with $x\in S$, $y\in T$ would come from an unsaturated edge $x\to y$ or from flow on an edge $y\to x$. Hence nothing reachable from $s$ lies in $T$, and nothing in $S$ reaches $t$.
> - *Both extremes are minimum cuts.* $(R_s, V\setminus R_s)$ is the cut of the maxflow–mincut proof. Symmetrically, no residual edge enters $R^t$ from outside (its tail would reach $t$), so $f$ saturates every edge into $R^t$ and avoids every edge out of it, and Lemma 10.1 makes $(V\setminus R^t, R^t)$ a minimum cut.
>
> So the minimum cut is unique if and only if $R_s = V\setminus R^t$, that is, $R_s\cup R^t = V$.
>
> **Time.** $O(VE)$ for the maximum flow plus two searches.
>
> **Answer.** Unique if and only if every vertex is reachable from $s$ or can reach $t$ in $G_{f^*}$: $O(VE)$ time.

### (c) and (d) Examples

> [!solution]- Solution
> **(c)** The path $s\to a\to t$ with capacities 1 and 1. Conservation at $a$ forces $f(s\to a) = f(a\to t)$, so the only maximum flow sends 1 along the path; but $(\{s\}, \{a, t\})$ and $(\{s, a\}, \{t\})$ both have capacity 1. In (b)'s terms, $a$ is neither reachable from $s$ nor able to reach $t$ in $G_{f^*}$.
>
> **(d)** Edges $s\to a$ (1), $a\to b$ (2), $b\to t$ (2), $a\to t$ (2) — the figure above. The cuts $\{s\}$, $\{s, a\}$, $\{s, b\}$, $\{s, a, b\}$ have capacities 1, 4, 3, 4, so $(\{s\}, \{a, b, t\})$ is the only minimum cut. The one unit can go directly $a\to t$, or through $b$, or be split between the two: infinitely many maximum flows.
>
> **Answer.** (c) $s\to a\to t$ with capacities 1, 1. (d) $s\to a$ (1), $a\to b$ (2), $b\to t$ (2), $a\to t$ (2).

## Exercise 10.6 — Acyclic maximum flows

> [!question] Exercise 10.6 (book p. 345)
> A flow is **acyclic** if the edges with positive flow form a dag.
>
> (a) Describe and analyze an algorithm that computes an acyclic maximum $(s,t)$-flow, in the same asymptotic time as Ford–Fulkerson.
>
> (b) Describe and analyze an algorithm that decides whether *every* maximum $(s,t)$-flow in a given network is acyclic.

### (a) Cancelling flow cycles

> [!hint]- Hint
> Compute any maximum flow, then cancel flow cycles with one depth-first search through the edges that carry flow. Never re-explore a vertex from which no flow cycle remains.

> [!solution]- Solution
> Run Ford–Fulkerson to get a maximum flow $f$ (integer capacities), then cancel its cycles with a depth-first search of the edges that carry flow. Each vertex is *new*, *active* (on the stack) or *done*, and keeps a pointer into its list of outgoing edges.
>
> ```text
> MakeAcyclic(G, f):
>     mark every vertex new; point each vertex at its first outgoing edge
>     for every vertex r
>         if r is new
>             push r onto an empty stack; mark r active
>             while the stack is not empty
>                 v ← the top of the stack
>                 advance v's pointer past every edge v→w with f(v→w) = 0 or w done
>                 if v's pointer has passed its last edge
>                     pop v; mark v done
>                 else
>                     v→w ← the edge at v's pointer
>                     if w is new
>                         push w; mark w active
>                     else                                  ⟨⟨w is on the stack⟩⟩
>                         C ← the pointer edges from w up to v, then v→w
>                         F ← min over e in C of f(e)
>                         f(e) ← f(e) − F for every edge e in C
>                         pop every vertex above w; mark them new
>     return f
> ```
>
> **Correctness.** The pointer of each stacked vertex is the edge to the next stacked vertex, and it carries flow; so when $v\to w$ reaches an active $w$, $C$ is a directed cycle of positive edges. Subtracting its minimum keeps $0\le f\le c$, conservation, and the value (a cycle leaves and enters each of its vertices once). Popping back to $w$ restores this, because only the pointer edges of $w$ and of the vertices above it changed. *Invariant: no flow cycle passes through a done vertex.* When $v$ is marked done, each of its edges carries no flow or ends at a done vertex; flow only decreases and done is permanent, so this stays true, and a flow cycle through $v$ would continue into a done vertex. At the end every vertex is done: the flow is acyclic, feasible, and has the same value — an acyclic maximum flow.
>
> **Time.** Pointers only move forward: $O(V + E)$ for all pointer moves and first pushes. A cancellation along $C$ costs $O(\lvert C\rvert)$ and pops fewer than $\lvert C\rvert$ vertices, and each such pop allows at most one later push. Total: $O(V + E + \sum\lvert C\rvert)$. With integer flows $F\ge 1$, so each cancellation lowers $\sum_e f(e)$ by $F\lvert C\rvert\ge\lvert C\rvert$, and $\sum\lvert C\rvert\le\sum_e f(e)$. Ford–Fulkerson's output has $\sum_e f(e)\le (V-1)\lvert f^*\rvert$: an augmentation along a path of at most $V - 1$ residual edges raises at most $V - 1$ edge values, each by $F$, and the $F$'s add up to $\lvert f^*\rvert$. So the cancelling costs $O(E + V\lvert f^*\rvert)$, within Ford–Fulkerson's $O(E\lvert f^*\rvert)$ (every vertex lies on an edge, so $V = O(E)$). With arbitrary real capacities each cancellation empties an edge, so there are at most $E$ of them: $O(VE)$, the cost of a flow decomposition (§10.5).
>
> **Answer.** Ford–Fulkerson, then a depth-first search over the positive edges that cancels each flow cycle it closes: $O(E + \sum_e f(e)) = O(E\lvert f^*\rvert)$ extra time.

> [!trap]
> Extracting $s\to t$ paths one at a time does not make the flow acyclic: the paths $s\to a\to b\to t$ and $s\to b\to a\to t$ are both simple, but their sum has the flow cycle $a\to b\to a$.

### (b) Is every maximum flow acyclic?

> [!hint]- Hint
> Find the set $H$ of edges that carry flow in *some* maximum flow. If every edge of a cycle carries flow in some maximum flow, the average of those flows is a maximum flow.

> [!solution]- Solution
> $G$ is reduced. Compute a maximum flow $f$, its residual graph and the strong components of $G_f$. Let $H$ be the set of edges $u\to v$ of $G$ with $f(u\to v) > 0$, or with $c(u\to v) > 0$ and both endpoints in one strong component of $G_f$.
>
> **Claim 1: $H$ is the set of edges that are positive in some maximum flow.** If $f(u\to v) = 0 < c(u\to v)$, then $u\to v$ is a residual edge, so $u$ and $v$ share a strong component exactly when $v$ can reach $u$ in $G_f$. If it can, a path from $v$ to $u$ plus $u\to v$ is a residual cycle with at least three vertices (the two-vertex cycle $u\to v\to u$ would need $f(u\to v) > 0$); pushing $\varepsilon$ around it gives a maximum flow with flow $\varepsilon$ on $u\to v$. Conversely, if a maximum flow $f'$ has $f'(u\to v) > 0 = f(u\to v)$, the flow $g$ of Exercise 10.1 is a circulation in $G_f$ with $g(u\to v) > 0$, and its decomposition puts $u\to v$ on a residual cycle, so $v$ reaches $u$.
>
> **Claim 2: some maximum flow has a flow cycle iff $H$ has a directed cycle.** A flow cycle of a maximum flow consists of edges of $H$. Conversely, for each edge $e$ of a cycle $C$ in $H$ pick a maximum flow $f_e$ with $f_e(e) > 0$. Their average satisfies the capacity and conservation constraints and has value $\lvert f^*\rvert$, so it is a maximum flow, and it is positive on every edge of $C$.
>
> **Algorithm.** Maximum flow, strong components of $G_f$, build $H$, and test whether $H$ is a dag (depth-first search). Every maximum flow is acyclic if and only if $H$ is a dag.
>
> **Time.** $O(VE)$ for the maximum flow plus $O(V + E)$.
>
> **Answer.** Let $H$ be the edges with positive flow in $f^*$ or with both endpoints in one strong component of $G_{f^*}$; every maximum flow is acyclic if and only if $H$ is a dag: $O(VE)$ time.

## Exercise 10.7 — Unit capacities and long shortest paths

> [!question] Exercise 10.7 (book pp. 345–346)
> Every edge of $G = (V, E)$ has capacity 1, and the shortest-path distance from $s$ to $t$ is at least $d$.
>
> (a) Prove that the maximum $(s,t)$-flow has value at most $E/d$.
>
> (b) Now $G$ is **simple**: for all $u$ and $v$ there is at most one edge from $u$ to $v$. (Flow networks may have parallel edges.) Prove that the maximum flow has value $O(V^2/d^2)$. *(The book's hint: how many vertices are in the average level of a breadth-first search tree rooted at $s$?)*

> [!hint]- Hint
> Cut between consecutive breadth-first levels. Which edges can cross such a cut forward?

> [!solution]- Solution
> **Level cuts.** Let $L_i$ be the set of vertices at distance exactly $i$ from $s$, and for $0\le i\le d - 1$ let $S_i = L_0\cup\cdots\cup L_i$. Since $\mathit{dist}(s, t)\ge d > i$, each $(S_i, V\setminus S_i)$ is an $(s,t)$-cut. If an edge $x\to y$ leaves $S_i$, then $\mathit{dist}(x)\le i < \mathit{dist}(y)\le\mathit{dist}(x) + 1$, so $x\in L_i$ and $y\in L_{i+1}$: **the edges leaving $S_i$ all run from $L_i$ to $L_{i+1}$**, and the $d$ cuts have pairwise disjoint sets of crossing edges (figure).
>
> **(a)** The $d$ cut capacities add up to at most $E$, so the smallest is at most $E/d$, and the maximum flow is at most every cut's capacity. (Or by flow decomposition: every flow path has at least $d$ edges, so $d\,\lvert f\rvert\le\sum_e f(e)\le E$.) The bound is tight: $k$ edge-disjoint $s\to t$ paths of length $d$ have $E = kd$ and maximum flow $k$.
>
> **(b)** In a simple graph at most $\lvert L_i\rvert\cdot\lvert L_{i+1}\rvert$ edges run from $L_i$ to $L_{i+1}$. Since $\sum_{i=0}^{d-1}(\lvert L_i\rvert + \lvert L_{i+1}\rvert)\le 2V$, some $i$ has $\lvert L_i\rvert + \lvert L_{i+1}\rvert\le 2V/d$, and then
> $$
> \lvert L_i\rvert\cdot\lvert L_{i+1}\rvert\le\left(\frac{\lvert L_i\rvert + \lvert L_{i+1}\rvert}{2}\right)^2\le\frac{V^2}{d^2}.
> $$
> So the maximum flow is at most $V^2/d^2$.
>
> **Answer.** (a) The $d$ level cuts have disjoint edge sets, so one has at most $E/d$ edges. (b) In a simple graph the thinnest pair of consecutive levels gives a cut with at most $V^2/d^2$ edges.

<!-- fig:a10x-levels -->
<figure class="cs-fig"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 560 250" width="560" height="250" role="img" style="font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-size:14px"><title>nine vertices in five BFS levels with four dashed vertical cuts between consecutive levels</title><defs><marker id="ARR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs><line x1="100" y1="22" x2="100" y2="212" stroke="var(--hi)" stroke-width="1.5" stroke-linecap="round" stroke-dasharray="5 4"/><text x="100" y="12" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">2 edges</text><line x1="210" y1="22" x2="210" y2="212" stroke="var(--hi)" stroke-width="1.5" stroke-linecap="round" stroke-dasharray="5 4"/><text x="210" y="12" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">4 edges</text><line x1="320" y1="22" x2="320" y2="212" stroke="var(--hi)" stroke-width="1.5" stroke-linecap="round" stroke-dasharray="5 4"/><text x="320" y="12" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">3 edges</text><line x1="430" y1="22" x2="430" y2="212" stroke="var(--hi)" stroke-width="1.5" stroke-linecap="round" stroke-dasharray="5 4"/><text x="430" y="12" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">2 edges</text><text x="45" y="234" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">level 0</text><text x="155" y="234" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">level 1</text><text x="265" y="234" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">level 2</text><text x="375" y="234" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">level 3</text><text x="485" y="234" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">level 4</text><path d="M58.7,108.8 L139.1,72.2" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M58.7,121.2 L139.1,157.8" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M169.6,61.7 L247.9,43.9" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M168.7,71.2 L249.1,107.8" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M168.7,158.8 L249.1,122.2" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M169.6,168.3 L247.9,186.1" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M279.3,44.5 L358.3,69.7" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M279.1,109.9 L358.6,81" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M279.6,186.7 L357.9,168.9" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M389.1,80.1 L468.6,109" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M388.7,158.8 L469.1,122.2" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M250,115.1 Q198.4,115.5 166.4,78.3" fill="none" stroke="var(--muted)" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)" stroke-dasharray="4 3"/><path d="M265,55 L265,97.5" fill="none" stroke="var(--muted)" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)" stroke-dasharray="4 3"/><path d="M363.4,174.5 Q326.2,204.8 282,194.1" fill="none" stroke="var(--muted)" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)" stroke-dasharray="4 3"/><circle cx="45" cy="115" r="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="45" y="116" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">s</text><circle cx="155" cy="65" r="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="155" y="66" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">a</text><circle cx="155" cy="165" r="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="155" y="166" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">b</text><circle cx="265" cy="40" r="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="265" y="41" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">c</text><circle cx="265" cy="115" r="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="265" y="116" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">d</text><circle cx="265" cy="190" r="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="265" y="191" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">e</text><circle cx="375" cy="75" r="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="375" y="76" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">f</text><circle cx="375" cy="165" r="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="375" y="166" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">g</text><circle cx="485" cy="115" r="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="485" y="116" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">t</text></svg><figcaption><strong>Level cuts in Exercise 10.7.</strong> Breadth-first levels from <i>s</i>, here with dist(<i>s</i>, <i>t</i>) = 4. An edge climbs at most one level, so the only edges leaving <i>S<sub>i</sub></i> = level 0 ∪ ⋯ ∪ level <i>i</i> run from level <i>i</i> to level <i>i</i> + 1 (black); edges inside a level or back down (dashed gray) never cross a cut forward. The four dashed (<i>s</i>, <i>t</i>)-cuts therefore have disjoint sets of crossing edges, of sizes 2, 4, 3, 2 — at most <i>E</i> in total, so one of the <i>d</i> cuts has at most <i>E</i>/<i>d</i> edges. With unit capacities the maximum flow is 2.</figcaption></figure>

## Exercise 10.8 — Deleting k edges

> [!question] Exercise 10.8 (book p. 346)
> Every edge of $G = (V, E)$ has capacity 1, and $k$ is an integer. Describe and analyze an algorithm that finds $k$ edges whose deletion makes the maximum $(s,t)$-flow of the remaining graph as small as possible.

> [!hint]- Hint
> Deleting one unit-capacity edge lowers every cut's capacity by at most 1.

> [!solution]- Solution
> Let $\lambda$ be the maximum flow value. With unit capacities, a minimum cut $(S, T)$ has exactly $\lambda$ edges from $S$ to $T$.
>
> **Algorithm.** Compute a maximum flow and let $S$ be the set of vertices reachable from $s$ in its residual graph. Delete $\min\{k, \lambda\}$ edges from $S$ to $T$; if $k > \lambda$, delete $k - \lambda$ arbitrary other edges as well.
>
> **Correctness.** After the deletions the cut $(S, T)$ has $\max\{\lambda - k, 0\}$ edges, so the maximum flow is at most that. No choice does better: deleting $k$ edges lowers every cut's capacity by at most $k$, so every cut keeps capacity at least $\lambda - k$, and by the maxflow–mincut theorem the maximum flow stays at least $\lambda - k$ (and at least 0).
>
> **Time.** $O(VE)$ for the maximum flow (or Ford–Fulkerson in $O(E\lambda)$), plus $O(V + E)$.
>
> **Answer.** Delete $k$ edges of a minimum cut (all of them if $k\ge\lambda$): the maximum flow becomes $\max\{\lambda - k, 0\}$, which is optimal; $O(VE)$ time.

## Exercise 10.9 — Tight bounds for flow decompositions

> [!question] Exercise 10.9 (book p. 346)
> Let $f\ge 0$ be an $(s,t)$-flow in a flow network $G = (V, E)$. (The book says "an arbitrary $(s,t)$-flow"; since the paths and cycles may use only edges with $f(e) > 0$, the claims can hold only for $f\ge 0$.)
>
> (a) Prove that if $\lvert f\rvert = 0$, then $f$ is a weighted sum of at most $E - V + 1$ directed cycles, each using only edges with $f(e) > 0$.
>
> (b) Prove that if $\lvert f\rvert > 0$, then $f$ is a weighted sum of at most $E - V + 2$ directed paths and cycles, each using only edges with $f(e) > 0$.
>
> (c) Show that both bounds are tight. *(The book's hint: this is easy.)*

### (a) and (b) — for connected networks

> [!hint]- Hint
> $E - V + 1$ is the number of edges outside a spanning tree. Each cancelled cycle destroys at least one independent cycle of the support.

> [!solution]- Solution
> **The statement needs $G$ connected** (directions ignored), which "an arbitrary flow network" does not guarantee: two disjoint directed triangles with flow 1 on all six edges have $E - V + 1 = 1$ but need two cycles. For a graph with $c$ connected components, the proof below gives $E - V + c$ in (a) and $E - V + c + 1$ in (b).
>
> **The cyclomatic number.** For a set $X$ of edges let $\mu(X) = \lvert X\rvert - V + c(X)$, where $c(X)$ is the number of connected components of $(V, X)$, directions ignored — the number of edges of $X$ outside a spanning forest. Deleting an edge that lies on a cycle of $X$ (directions ignored) leaves $c(X)$ unchanged and lowers $\mu$ by 1; deleting any other edge raises $c(X)$ by 1 and leaves $\mu$ unchanged. So $\mu$ never increases when edges are deleted, and $\mu(X)\le\mu(E) = E - V + 1$ for connected $G$.
>
> **(a)** *Claim: a circulation $f\ge 0$ whose support is $X$ is a positive combination of at most $\mu(X)$ directed cycles in $X$.* Induction on $\lvert X\rvert$. If $X = \varnothing$, no cycles are needed. Otherwise follow positive edges from any vertex of $X$; conservation never lets the walk stop, so it closes a directed cycle $C\subseteq X$. Subtract $F = \min_C f$ along $C$: the result $f'\ge 0$ is a circulation, and some edge $e$ of $C$ drops to 0, so its support $X'$ lies in $X - e$. Because $e$ lies on the cycle $C$, $\mu(X - e) = \mu(X) - 1$, so $\mu(X')\le\mu(X) - 1$. By induction $f'$ needs at most $\mu(X) - 1$ cycles; add $C$.
>
> **(b)** Add a new edge $t\to s$ carrying $\lvert f\rvert$. The result is a circulation on a connected graph with $E + 1$ edges and $V$ vertices, so by (a) it uses at most $E - V + 2$ cycles; deleting $t\to s$ turns the cycles through it into $s\to t$ paths.
>
> **Answer.** Every cancelled cycle lowers the cyclomatic number of the support by at least 1, so for connected $G$ a circulation needs at most $E - V + 1$ cycles and, with the extra edge $t\to s$, a flow at most $E - V + 2$ paths and cycles.

### (c) Tightness

> [!solution]- Solution
> **Circulations.** A chain of $k$ directed triangles, consecutive ones sharing a vertex: $V = 2k + 1$, $E = 3k$, $E - V + 1 = k$. Its only directed cycles are the $k$ triangles, which are edge-disjoint, so the circulation with flow 1 on every edge needs all $k$ of them.
>
> **Flows.** $k$ paths $s\to a_i\to t$: $V = k + 2$, $E = 2k$, $E - V + 2 = k$. The graph has no cycles, and each $s\to t$ path passes through only one $a_i$, so the flow with value 1 on every edge needs $k$ paths.
>
> **Answer.** A chain of $k$ triangles needs $k = E - V + 1$ cycles; $k$ parallel paths $s\to a_i\to t$ need $k = E - V + 2$ paths.

### Sources for this page

Exercises 10.0–10.9 of Jeff Erickson, *Algorithms* (2019), pp. 344–346 (CC BY 4.0), paraphrased; the solutions, the counterexamples and the three figures are ours. Three statements needed repair: 10.2 is false for an edge of capacity 0, which the chapter allows; 10.4(a) and (b) are false as printed — simplifying an opposing pair makes every cut separating its endpoints cheaper, and the four-vertex network built from the book's capacities 7 and 10 breaks both parts — while 10.4(c) is true; and 10.9(a)–(b) need a connected network and, left implicit in the book, a non-negative flow. Every algorithm on this page is implemented in `tools/checks/a10x.py` and compared on thousands of random small networks (with parallel and opposite edges where the solution allows them) against brute force: minimum cuts by enumerating all vertex partitions, uniqueness and "some maximum flow has a cycle" by enumerating all integral flows and by linear programming, deletions by trying every $k$-subset of edges; the decomposition bounds, the level-cut argument and every number in the examples and figures are recomputed there.
