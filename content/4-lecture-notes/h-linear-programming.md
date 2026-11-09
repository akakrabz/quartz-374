---
title: "Linear programming"
description: "Erickson's note H: linear programs, canonical and slack form, the geometry of feasible regions (infeasible, unbounded, optimal); shortest paths, single-source shortest paths, maximum flow and minimum cut as LPs; the dual and how to write it for any LP (Figure H.4); weak duality, the fundamental (strong duality) theorem and its proof for non-degenerate LPs, the dual as forces; complementary slackness — with worked examples checked by solver and the note's errors corrected."
tags: [lecture-notes, algorithms, linear-programming]
note: "H"
---

*Erickson, lecture notes · Extended Dance Remix H · 21 pp. · [PDF](https://jeffe.cs.illinois.edu/teaching/algorithms/notes/H-lp.pdf) · CC BY-NC-SA 4.0 · [[4-lecture-notes/index|all notes]] · status: text beta, needs figures*

> [!abstract] In one breath
> A **linear program** asks for a vector $x\in\mathbb{R}^d$ that maximizes or minimizes a linear function subject to finitely many linear inequalities and equations; every LP can be put in **canonical form** $\max\{c\cdot x : Ax\le b,\ x\ge 0\}$. Geometrically the feasible points form a convex **polyhedron**, and the LP is either **infeasible** (empty polyhedron), **unbounded** (the objective grows without limit), or it has an optimum. Shortest paths, maximum flows and minimum cuts are all LPs, and they come in pairs: every LP has a **dual** LP, obtained mechanically by swapping the roles of constraints and variables (one table, Figure H.4, covers every case). **Weak duality** — every feasible value of a maximization LP is at most every feasible value of its dual — is a two-line proof; the **fundamental theorem** (strong duality) says the two optima are equal whenever one exists, generalizing the maxflow-mincut theorem. **Complementary slackness** sharpens it: an optimal dual variable can be positive only on a tight primal constraint, and vice versa.

> [!note] Where this fits
> The note says "read F and G first": it builds on flows with balances ([[4-lecture-notes/f-balances-and-pseudoflows|note F]]) and minimum-cost flows ([[4-lecture-notes/g-minimum-cost-flows|note G]], [[concepts/minimum-cost-flow]]), and its examples are the textbook's shortest paths ([[2-algorithms/08-shortest-paths|Chapter 8]], [[concepts/shortest-paths]]) and maximum flows and minimum cuts ([[2-algorithms/10-maximum-flows-and-minimum-cuts|Chapter 10]], [[concepts/maximum-flow]]). Its sequel, [[4-lecture-notes/i-linear-programming-algorithms|note I]], solves LPs (the simplex method); [[4-lecture-notes/j-approximation-algorithms|note J]] uses LPs to approximate NP-hard problems. **Not assigned in CS/ECE 374 this semester** — linear programming is CS 473 material at Illinois. Concept page: [[concepts/linear-programming]].

## H.1 Introduction

The maximum flow and minimum cut problems are special cases of **linear programming**, and so are shortest paths, minimum spanning trees and many problems of scheduling, logistics and economics. (Briefly, the history the note tells: Kantorovich formalized LPs in the 1930s, Koopmans rediscovered them, Dantzig published the simplex method in 1947, and Kantorovich and Koopmans shared the 1975 economics Nobel prize.)

> [!definition] Definition — linear program
> A **linear program** asks for a vector $x\in\mathbb{R}^d$ that maximizes (or minimizes) $c\cdot x = \sum_j c_jx_j$ among all $x$ satisfying
> $$
> \begin{aligned}
> \textstyle\sum_{j=1}^d a_{ij}x_j &\le b_i &&\text{for } i = 1,\ldots,p,\\
> \textstyle\sum_{j=1}^d a_{ij}x_j &= b_i &&\text{for } i = p+1,\ldots,p+q,\\
> \textstyle\sum_{j=1}^d a_{ij}x_j &\ge b_i &&\text{for } i = p+q+1,\ldots,n.
> \end{aligned}
> $$
> The input is the **constraint matrix** $A = (a_{ij})\in\mathbb{R}^{n\times d}$, the **offset vector** $b\in\mathbb{R}^n$ and the **objective vector** $c\in\mathbb{R}^d$. The coordinates $x_j$ are the **variables**, each inequality or equation is a **constraint**, and $x\mapsto c\cdot x$ is the **objective function**.

> [!definition] Definition — canonical form and slack form
> An LP is in **canonical form** if it reads
> $$
> \max\ c\cdot x\quad\text{subject to}\quad Ax\le b,\quad x\ge 0,
> $$
> that is, $n$ **matrix constraints** $\sum_j a_{ij}x_j\le b_i$ plus $d$ **sign constraints** $x_j\ge 0$ ($x\ge y$ for vectors means $x_i\ge y_i$ for every $i$). It is determined by $A$, $b$ and $c$. An LP is in **slack form** if it reads $\max\ c\cdot x$ subject to $Ax = b$, $x\ge 0$: the only inequalities are sign constraints. (Some authors call either of these "standard form".)

**Every LP can be put in canonical form**, by three rewriting rules:

- replace each variable $x_j$ by $x_j^+ - x_j^-$ with two new variables $x_j^+, x_j^-\ge 0$;
- replace each equation $\sum_j a_{ij}x_j = b_i$ by the two inequalities $\sum_j a_{ij}x_j\le b_i$ and $\sum_j a_{ij}x_j\ge b_i$;
- replace each lower-bound constraint $\sum_j a_{ij}x_j\ge b_i$ by the upper bound $\sum_j(-a_{ij})x_j\le -b_i$.

(A minimization becomes a maximization by negating $c$.) This may double the numbers of variables and of constraints, and is rarely needed in practice. The note writes $Ax\ge b$ for the matrix constraints of a canonical LP (p. 2) and calls the $\ge$ constraint of the third rule an "upper bound" turned into a "lower bound" (p. 3); both are slips, corrected above. Slack form is reached from canonical form by giving each inequality its own non-negative **slack variable**, $\sum_j a_{ij}x_j + s_i = b_i$, $s_i\ge 0$ (the note leaves this as an exercise); slack form is the one the textbook simplex method works with.

> [!trap] Form traps
> - **"Standard form" is ambiguous** — some books mean canonical form, others slack form. Say which one you mean.
> - **Variables are not automatically non-negative.** A free variable must be split (or kept, if the format allows it); forgetting this silently changes the problem.
> - **Strict inequalities are not allowed** in an LP; "$<$" has no optimum in general.

Concept page: [[concepts/linear-programming]].

## H.2 The geometry of linear programming

A point $x$ is **feasible** if it satisfies all the constraints; the set of feasible points is the **feasible region**. A linear equation in $d$ variables defines a **hyperplane** in $\mathbb{R}^d$ (a line when $d = 2$), which splits $\mathbb{R}^d$ into two **halfspaces**, each the solution set of a linear inequality. So the feasible region is an intersection of finitely many hyperplanes and halfspaces — a **polyhedron** — and it is **convex**: with any two points it contains the segment between them, because every halfspace does. Rotating coordinates so that the objective vector points straight down turns every LP into one geometric question: **find the lowest point of a given polyhedron.**

<!-- fig:nh-geometry -->
<figure class="cs-fig"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 300" width="420" height="300" role="img" style="font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-size:14px"><title>a pentagon with vertices (0,0), (3,0), (3,1), (2,2), (0,3); objective values 0, 9, 11, 10, 6; the optimum (3,1) is highlighted</title><defs><marker id="ARR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs><path d="M52,250 L217,250 L217,195 L162,140 L52,85 Z" fill="var(--accent)" fill-opacity="0.13" stroke="none" stroke-width="0"/><line x1="35.5" y1="250" x2="349" y2="250" stroke="var(--muted)" stroke-width="1.1" stroke-linecap="round" marker-end="url(#ARR)"/><line x1="52" y1="266.5" x2="52" y2="19" stroke="var(--muted)" stroke-width="1.1" stroke-linecap="round" marker-end="url(#ARR)"/><text x="345" y="263" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:14px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">x</text><text x="41" y="24" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:14px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">y</text><line x1="107" y1="247" x2="107" y2="253" stroke="var(--muted)" stroke-width="1" stroke-linecap="round"/><line x1="162" y1="247" x2="162" y2="253" stroke="var(--muted)" stroke-width="1" stroke-linecap="round"/><line x1="217" y1="247" x2="217" y2="253" stroke="var(--muted)" stroke-width="1" stroke-linecap="round"/><line x1="272" y1="247" x2="272" y2="253" stroke="var(--muted)" stroke-width="1" stroke-linecap="round"/><line x1="49" y1="195" x2="55" y2="195" stroke="var(--muted)" stroke-width="1" stroke-linecap="round"/><line x1="49" y1="140" x2="55" y2="140" stroke="var(--muted)" stroke-width="1" stroke-linecap="round"/><line x1="49" y1="85" x2="55" y2="85" stroke="var(--muted)" stroke-width="1" stroke-linecap="round"/><line x1="54.8" y1="32.8" x2="285.8" y2="263.8" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" opacity="0.55"/><text x="127.2" y="63.2" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">x + y ≤ 4</text><line x1="38.2" y1="78.1" x2="335.2" y2="226.6" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" opacity="0.55"/><text x="293" y="184.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">x + 2y ≤ 6</text><line x1="217" y1="263.8" x2="217" y2="32.8" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" opacity="0.55"/><text x="217" y="57.8" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">x ≤ 3</text><path d="M52,250 L217,250 L217,195 L162,140 L52,85 Z" fill="none" fill-opacity="1" stroke="currentColor" stroke-width="1.8"/><line x1="181.2" y1="141.4" x2="261" y2="261" stroke="var(--hi)" stroke-width="1.4" stroke-linecap="round" stroke-dasharray="6 4"/><text x="285.8" y="286.2" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">3x + 2y = 11</text><line x1="82.2" y1="186.8" x2="118.9" y2="162.3" stroke="var(--accent2)" stroke-width="2.2" stroke-linecap="round" marker-end="url(#ARR)"/><text x="84.1" y="202.8" text-anchor="start" dominant-baseline="central" fill="var(--accent2)" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">c = (3, 2)</text><circle cx="52" cy="250" r="3.4" fill="currentColor" stroke="currentColor" stroke-width="1.2"/><text x="38" y="263" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">0</text><circle cx="217" cy="250" r="3.4" fill="currentColor" stroke="currentColor" stroke-width="1.2"/><text x="227" y="264" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">9</text><circle cx="217" cy="195" r="4.2" fill="var(--hi)" stroke="var(--hi)" stroke-width="1.2"/><text x="229" y="185" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">11</text><circle cx="162" cy="140" r="3.4" fill="currentColor" stroke="currentColor" stroke-width="1.2"/><text x="172" y="128" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">10</text><circle cx="52" cy="85" r="3.4" fill="currentColor" stroke="currentColor" stroke-width="1.2"/><text x="36" y="77" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">6</text><text x="251" y="201" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">(3, 1)</text></svg><figcaption><strong>The feasible region of a two-variable LP.</strong> Maximize 3<i>x</i> + 2<i>y</i> subject to <i>x</i> + <i>y</i> ≤ 4, <i>x</i> + 2<i>y</i> ≤ 6, <i>x</i> ≤ 3 and <i>x</i>, <i>y</i> ≥ 0: the shaded pentagon is the intersection of five halfplanes. The numbers at its vertices are the objective values; the objective grows in the direction <i>c</i>, and the dashed level line 3<i>x</i> + 2<i>y</i> = 11 touches the region only at the optimal vertex (3, 1).</figcaption></figure>

Two things can go wrong. The LP is **infeasible** if there is no feasible point at all, and **unbounded** if there are feasible points with arbitrarily large objective value (for a maximization). The same polyhedron can be unbounded for some objectives and bounded for others (an upward-opening wedge has no highest point but has a lowest one), or unbounded for every non-zero objective (all of $\mathbb{R}^d$). Otherwise the LP is feasible and bounded, and then — a standard fact the notes use throughout — the optimum is attained, at a vertex if the polyhedron has vertices (a canonical LP's always does).

> [!example] Example — an infeasible LP (the note's Figure H.2)
> Maximize $x - y$ subject to $2x + y\le 1$, $x + y\ge 2$, $x, y\ge 0$. With $y\ge 0$ the first constraint forces $x + y\le 2x + y\le 1 < 2$: no point satisfies both. As a certificate, add the first constraint to the second written as $-x - y\le -2$: the sum is $x\le -1$, which contradicts $x\ge 0$. (Such certificates always exist for infeasible LPs; that is Farkas's lemma, one of the theorems of the alternative of §H.5.)

<!-- fig:nh-infeasible -->
<figure class="cs-fig"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 360 290" width="360" height="290" role="img" style="font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-size:14px"><title>two disjoint shaded regions in the first quadrant: a small triangle under 2x + y = 1 and the region above x + y = 2</title><defs><marker id="ARR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs><path d="M40,250 L84,250 L40,162 Z" fill="var(--accent)" fill-opacity="0.3" stroke="none" stroke-width="0"/><path d="M216,250 L326,250 L326,25.6 L40,25.6 L40,74 Z" fill="var(--accent2)" fill-opacity="0.13" stroke="none" stroke-width="0"/><line x1="13.6" y1="250" x2="339.2" y2="250" stroke="var(--muted)" stroke-width="1.1" stroke-linecap="round" marker-end="url(#ARR)"/><line x1="40" y1="276.4" x2="40" y2="12.4" stroke="var(--muted)" stroke-width="1.1" stroke-linecap="round" marker-end="url(#ARR)"/><text x="335.2" y="263" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:14px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">x</text><text x="29" y="17.4" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:14px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">y</text><line x1="128" y1="247" x2="128" y2="253" stroke="var(--muted)" stroke-width="1" stroke-linecap="round"/><line x1="216" y1="247" x2="216" y2="253" stroke="var(--muted)" stroke-width="1" stroke-linecap="round"/><line x1="37" y1="162" x2="43" y2="162" stroke="var(--muted)" stroke-width="1" stroke-linecap="round"/><line x1="31.2" y1="144.4" x2="92.8" y2="267.6" stroke="var(--accent)" stroke-width="1.6" stroke-linecap="round"/><line x1="22.4" y1="56.4" x2="233.6" y2="267.6" stroke="var(--accent2)" stroke-width="1.6" stroke-linecap="round"/><text x="81.4" y="232.4" text-anchor="start" dominant-baseline="central" fill="var(--accent)" style="font-size:13.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">2x + y ≤ 1</text><text x="202.8" y="113.6" text-anchor="start" dominant-baseline="central" fill="var(--accent2)" style="font-size:13.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">x + y ≥ 2</text></svg><figcaption><strong>An infeasible LP (the note’s Figure H.2).</strong> In the quadrant <i>x</i>, <i>y</i> ≥ 0 the constraint 2<i>x</i> + <i>y</i> ≤ 1 leaves the small triangle, where <i>x</i> + <i>y</i> ≤ 1; the constraint <i>x</i> + <i>y</i> ≥ 2 leaves the region beyond the line <i>x</i> + <i>y</i> = 2. They do not meet, so no objective can be optimized.</figcaption></figure>

Concept page: [[concepts/linear-programming]].

## H.3 Examples

### One shortest path

Given a directed graph $G = (V,E)$ with edge lengths $\ell\colon E\to\mathbb{R}$ and two vertices $s$ and $t$, the shortest-path distance from $s$ to $t$ is the optimum of
$$
\begin{aligned}
\text{maximize}\quad & \mathit{dist}(t)\\
\text{subject to}\quad & \mathit{dist}(s) = 0,\\
& \mathit{dist}(v) - \mathit{dist}(u)\le\ell(u\to v)\quad\text{for every edge } u\to v,
\end{aligned}
$$
with one free variable $\mathit{dist}(v)$ per vertex. The constraints say that **no edge is tense** ([[2-algorithms/08-shortest-paths#83-the-only-sssp-algorithm|§8.3]]): along any path from $s$ to $v$ they add up to $\mathit{dist}(v)\le$ the length of the path, so every feasible solution *under*estimates every distance, and maximizing $\mathit{dist}(t)$ pushes it up to the true distance — a maximization that computes a shortest path.

- **Feasible if and only if $G$ has no negative cycle** — anywhere, not only on paths from $s$. Adding the constraints around a cycle gives $0\le$ its length. Conversely, without negative cycles the distances from a new vertex joined to every vertex by an edge of length 0 satisfy every constraint ([[2-algorithms/09-all-pairs-shortest-paths#93-reweighting|reweighting]]); subtracting the value at $s$ makes $\mathit{dist}(s) = 0$.
- **When feasible, bounded if and only if $t$ is reachable from $s$.** A path gives the upper bound. If $t$ is not reachable, take any feasible solution and add the same amount $M$ to $\mathit{dist}(v)$ for every vertex $v$ that $s$ cannot reach: no edge leaves the reachable set, so every constraint still holds, and $\mathit{dist}(t)\to\infty$. (The note's witness — $\mathit{dist} = 0$ on the reachable vertices and $\infty$ on the others, p. 5 — is not a feasible point when a reachable edge has negative length.)
- **The optimum need not be unique**: a vertex that cannot reach $t$ can be lowered freely. The note claims (p. 6) the optimum is unique if and only if (1) every vertex lies on a path from $s$ to $t$ and (2) all $s$–$t$ paths have the same length. The condition is sufficient but **not necessary**. With positive lengths the correct statement is: **the optimum is unique if and only if every vertex lies on a shortest path from $s$ to $t$** — then $\mathit{dist}(v)$ is squeezed between $\delta(s,v)$ from above and $\delta(s,t) - \delta(v,t) = \delta(s,v)$ from below. In the example below the paths have lengths 6, 8, 8, 9 and 11, yet the optimum is unique.

### One shortest path, take two

The same distance is the optimum of a minimization with one variable per **edge**, $x(u\to v)\ge 0$, which says how often $u\to v$ is used:
$$
\begin{aligned}
\text{minimize}\quad & \textstyle\sum_{u\to v}\ell(u\to v)\,x(u\to v)\\
\text{subject to}\quad & \textstyle\sum_u x(u\to t) - \sum_w x(t\to w) = 1,\\
& \textstyle\sum_u x(u\to v) - \sum_w x(v\to w) = 0\quad\text{for every vertex } v\ne s, t,\\
& x(u\to v)\ge 0\quad\text{for every edge } u\to v.
\end{aligned}
$$
Any $s$–$t$ path, or walk, is a feasible point (count the uses of each edge). This is a **minimum-cost flow** problem ([[4-lecture-notes/g-minimum-cost-flows|note G]]): edge costs $\ell$, no capacities, one unit of supply at $s$ (balance $-1$) and one unit of demand at $t$ (balance $+1$); the balance at $s$ is implied by the others. Since the balances are integers, there is an integral optimum, and by flow decomposition ([[2-algorithms/10-maximum-flows-and-minimum-cuts#105-combining-and-decomposing-flows|§10.5]]) an optimal one that is a simple path. Integrality is a feature of this LP, not of LPs with integer data in general.

- **Feasible iff $t$ is reachable from $s$**, since every flow of value 1 decomposes into paths and cycles.
- **When feasible, bounded iff there is no negative cycle**: push flow around a negative cycle and the cost falls without limit; otherwise cancel the cycles of any feasible flow (cost does not rise), and what is left carries at most one unit per edge, so the cost is at least the sum of the negative lengths.
- If two optimal solutions exist, so do infinitely many: every convex combination $\alpha x + (1-\alpha)x'$ of optimal solutions is optimal. This holds for every LP.

> [!example] Example — both shortest-path LPs on one graph
> Edges $s\to a$ 2, $s\to b$ 5, $a\to b$ 1, $a\to c$ 4, $b\to c$ 1, $b\to t$ 6, $c\to t$ 2. The first LP's optimum is $\mathit{dist} = (0, 2, 3, 4, 6)$ on $s, a, b, c, t$; it is **unique**, because every vertex lies on the shortest path $s\,a\,b\,c\,t$ — even though the five $s$–$t$ paths have lengths 6, 8, 8, 9, 11, so the note's condition (2) fails. The second LP's optimum puts $x = 1$ on the four edges of that path and 0 elsewhere, cost $2 + 1 + 1 + 2 = 6$. The two optima agree, as §H.5 promises, and the flow uses only **tight** edges, where $\mathit{dist}(v) - \mathit{dist}(u) = \ell(u\to v)$ (§H.8); the other three edges have slack 2, 2 and 3.

<!-- fig:nh-shortest-path -->
<figure class="cs-fig"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 510 290" width="510" height="290" role="img" style="font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-size:14px"><title>the shortest-path example graph with distances at the vertices and the shortest path highlighted</title><defs><marker id="ARR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs><path d="M62.5,131.1 L161.4,70.2" fill="none" stroke="var(--hi)" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M62.4,149.1 L161.5,211.6" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M178,77 L178,202.5" fill="none" stroke="var(--hi)" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M192.8,68.4 L301.1,130.3" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M192.7,213.4 L301.2,149.9" fill="none" stroke="var(--hi)" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M195,222.1 Q327.6,223.2 435.8,150.8" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M335,140 L432.5,140" fill="none" stroke="var(--hi)" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><circle cx="48" cy="140" r="17" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="48" y="141" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">s</text><circle cx="178" cy="60" r="17" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="178" y="61" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">a</text><circle cx="178" cy="222" r="17" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="178" y="223" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">b</text><circle cx="318" cy="140" r="17" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="318" y="141" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">c</text><circle cx="452" cy="140" r="17" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="452" y="141" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">t</text><text x="99" y="91" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">2</text><text x="77" y="193" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">5  (slack 2)</text><text x="167" y="141" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">1</text><text x="282" y="88" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">4  (slack 2)</text><text x="242" y="169" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">1</text><text x="355" y="219" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">6  (slack 3)</text><text x="385" y="128" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">2</text><text x="48" y="110" text-anchor="middle" dominant-baseline="central" fill="var(--accent2)" style="font-size:13.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">0</text><text x="178" y="30" text-anchor="middle" dominant-baseline="central" fill="var(--accent2)" style="font-size:13.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">2</text><text x="178" y="253" text-anchor="middle" dominant-baseline="central" fill="var(--accent2)" style="font-size:13.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">3</text><text x="318" y="110" text-anchor="middle" dominant-baseline="central" fill="var(--accent2)" style="font-size:13.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">4</text><text x="452" y="110" text-anchor="middle" dominant-baseline="central" fill="var(--accent2)" style="font-size:13.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">6</text></svg><figcaption><strong>Both shortest-path LPs on one graph.</strong> Numbers on edges are lengths; the bold numbers at the vertices are the optimal <i>dist</i> values of the maximization LP, 0, 2, 3, 4, 6 — the unique optimum. The highlighted edges are tight (<i>dist</i>(<i>v</i>) − <i>dist</i>(<i>u</i>) = ℓ(<i>u</i>→<i>v</i>)); the minimization LP puts one unit of flow on exactly these edges, the path <i>s</i> <i>a</i> <i>b</i> <i>c</i> <i>t</i> of length 6, and nothing on the three loose edges.</figcaption></figure>

### Single-source shortest paths

In the first LP only $\mathit{dist}(t)$ is pushed up; a vertex off the shortest path may stay below its distance. Maximizing $\sum_v\mathit{dist}(v)$ instead, with the same constraints, gives the true distance to **every** vertex at once (when all are reachable from $s$ and there is no negative cycle) — again a maximization. The corresponding minimization asks for one unit of demand at **every** vertex other than $s$:
$$
\begin{aligned}
\text{minimize}\quad & \textstyle\sum_{u\to v}\ell(u\to v)\,x(u\to v)\\
\text{subject to}\quad & \textstyle\sum_u x(u\to v) - \sum_w x(v\to w) = 1\quad\text{for every vertex } v\ne s,\\
& x\ge 0.
\end{aligned}
$$
If $T$ is a shortest-path tree rooted at $s$ and $D_v$ is the set of descendants of $v$ in $T$ (with $v$ itself, so $D_s = V$ and $D_v = \{v\}$ for a leaf — the note prints $\lvert v\rvert$), an optimal solution puts $x(u\to v) = \lvert D_v\rvert$ on every tree edge and 0 elsewhere: the tree edge into $v$ carries one unit for every vertex whose tree path passes through $v$. Its cost is $\sum_v\delta(s,v)$. This too is an uncapacitated minimum-cost flow problem.

### Maximum flows and minimum cuts

The maximum-flow problem ([[2-algorithms/10-maximum-flows-and-minimum-cuts#101-flows|§10.1]]) is an LP with one variable per edge:
$$
\begin{aligned}
\text{maximize}\quad & \textstyle\sum_w f(s\to w) - \sum_u f(u\to s)\\
\text{subject to}\quad & \textstyle\sum_w f(v\to w) - \sum_u f(u\to v) = 0\quad\text{for every vertex } v\ne s,t,\\
& 0\le f(u\to v)\le c(u\to v)\quad\text{for every edge } u\to v.
\end{aligned}
$$
The minimum cut gets "indicator" variables: $S(v)$ for each vertex (is $v$ on the source side?) and $x(u\to v)$ for each edge (does it cross from $S$ to $T$?):
$$
\begin{aligned}
\text{minimize}\quad & \textstyle\sum_{u\to v}c(u\to v)\,x(u\to v)\\
\text{subject to}\quad & x(u\to v) + S(v) - S(u)\ge 0\quad\text{and}\quad x(u\to v)\ge 0\quad\text{for every edge } u\to v,\\
& S(s) = 1,\quad S(t) = 0.
\end{aligned}
$$
The indicator vector of any cut is feasible with objective equal to the cut's capacity, so the optimum is at most the minimum cut; in fact it equals it, and some optimal solution is a 0/1 vector — an actual minimum cut. But fractional optimal solutions can exist too: in the network $s\to a\to t$ with both capacities 1, $S(a) = \tfrac12$, $x(s\to a) = x(a\to t) = \tfrac12$ is optimal (value 1), the average of the two minimum cuts.

> [!trap] Traps in the LP formulations
> - **Shortest paths by maximization.** Every feasible $\mathit{dist}$ is a lower bound on the distances; the LP *maximizes* to reach them. Minimizing $\mathit{dist}(t)$ computes something else: it is unbounded below unless $t$ can reach $s$, and then its minimum is $-\delta(t,s)$.
> - **Feasibility needs no negative cycle anywhere** in the graph, not just on $s$–$t$ paths: every edge contributes a constraint.
> - **Integrality is special.** Shortest-path, flow and cut LPs have integral optima (their constraint matrices are incidence matrices); a general LP with integer data need not have any integral optimum, and integer programming is NP-hard (the note's Exercise 8).

Concept page: [[concepts/linear-programming]].

## H.4 Linear programming duality

Each pair of LPs in §H.3 is an instance of **duality**: every LP has a **dual** LP, obtained mechanically by swapping the roles of the constraints and the variables. For canonical form the translation is
$$
\text{(P)}\quad \max\ c\cdot x\ \ \text{s.t.}\ \ Ax\le b,\ x\ge 0\qquad\Longleftrightarrow\qquad \text{(D)}\quad \min\ y\cdot b\ \ \text{s.t.}\ \ yA\ge c,\ y\ge 0,
$$
with one dual variable $y_i$ per primal constraint and one dual constraint per primal variable (here $x$ and $b$ are column vectors, $y$ and $c$ row vectors). Written in canonical form itself — negate both vectors and replace $A$ by $-A^\top$ — the dual is $\max\{-b^\top\cdot y^\top : -A^\top y^\top\le -c^\top,\ y^\top\ge 0\}$, and doing the same once more gives back (P): **the dual of the dual is the primal**. Which of the two is called "primal" is arbitrary (by habit, the maximization).

### Dualizing arbitrary LPs

Converting to canonical form, dualizing, and simplifying gives a direct rule for any LP — the note's Figure H.4:

| in the primal | dual of a **maximization** (minimizes $y\cdot b$) | dual of a **minimization** (maximizes $y\cdot b$) |
|---|---|---|
| constraint $\sum_j a_{ij}x_j\le b_i$ | $y_i\ge 0$ | $y_i\le 0$ |
| constraint $\sum_j a_{ij}x_j\ge b_i$ | $y_i\le 0$ | $y_i\ge 0$ |
| constraint $\sum_j a_{ij}x_j = b_i$ | $y_i$ free | $y_i$ free |
| variable $x_j\ge 0$ | $\sum_i y_ia_{ij}\ge c_j$ | $\sum_i y_ia_{ij}\le c_j$ |
| variable $x_j\le 0$ | $\sum_i y_ia_{ij}\le c_j$ | $\sum_i y_ia_{ij}\ge c_j$ |
| variable $x_j$ free | $\sum_i y_ia_{ij} = c_j$ | $\sum_i y_ia_{ij} = c_j$ |
| variable $x_j = 0$ | no constraint | no constraint |

The right-hand sides $b_i$ become the dual's objective coefficients and the objective coefficients $c_j$ become the dual's right-hand sides; the column of $x_j$ in $A$ becomes the row of the $j$th dual constraint. The apparent asymmetry — constraint directions flip into variable signs, variable signs keep their direction in the dual constraints — comes from switching between maximization and minimization.

> [!recipe] Recipe — writing the dual of any LP
> 1. Give every constraint (except sign constraints on single variables) a dual variable $y_i$; its sign comes from the table: in a maximization a **natural** $\le$ constraint gets a natural $y_i\ge 0$, an unnatural $\ge$ gets $y_i\le 0$, an equation gets a free $y_i$.
> 2. Write one dual constraint per primal variable $x_j$: $\sum_i y_ia_{ij}$ (the column of $x_j$) compared with $c_j$ — $\ge$ for a natural $x_j\ge 0$ in a maximization, $\le$ for $x_j\le 0$, $=$ for a free $x_j$; none for $x_j = 0$.
> 3. The dual objective is $\sum_i y_ib_i$, minimized if the primal maximizes and vice versa. For a minimization primal everything flips: natural is $\ge$ for constraints, $\ge 0$ for variables, and natural still maps to natural.
> 4. Check by weak duality on a pair of feasible points: the primal value must not beat the dual value.

### Shortest path example

The first shortest-path LP has a variable per vertex and a constraint per edge; its constraint matrix is the **signed incidence matrix** of $G$, with entry $-1$ in row $u\to v$, column $u$, and $+1$ in column $v$. So its dual has a variable $x(u\to v)$ per edge and a constraint per vertex. The variable $\mathit{dist}(s)$ is fixed at 0, so it gets no dual constraint; the others are free, so their dual constraints are equations; the primal constraints are $\le$, so $x\ge 0$; the objective coefficients ($+1$ for $t$, 0 elsewhere) become the right-hand sides and the edge lengths the objective. The result is exactly the second shortest-path LP. In the same way the single-source pair is a dual pair, and the minimum-cut LP is the dual of the maximum-flow LP (with $S(v)$ the negated dual variable of the conservation constraint at $v$, $S(s) = 1$ and $S(t) = 0$).

> [!trap] Dualizing traps
> - **Min or max first.** The table has two halves; using the max-half on a minimization flips every sign. Convert in your head ("natural to natural") or rewrite the primal as a maximization first.
> - **A fixed variable has no dual constraint**, and a free variable gives an *equation*.
> - **Transpose.** The $j$th dual constraint uses the $j$th *column* of $A$.

Concept page: [[concepts/linear-programming]].

## H.5 The fundamental theorem

> [!key] Fundamental theorem of linear programming
> A canonical linear program (P) has an optimal solution $x^*$ if and only if its dual (D) has an optimal solution $y^*$; and then $c\cdot x^* = y^*Ax^* = y^*\cdot b$.

This broad generalization of the [[2-algorithms/10-maximum-flows-and-minimum-cuts#103-the-maxflow-mincut-theorem|maxflow-mincut theorem]] was conjectured by von Neumann at his 1947 meeting with Dantzig, who had come to explain the simplex method; von Neumann saw it as a consequence of his 1928 min-max theorem for two-player zero-sum games. The first published proof is Gale, Kuhn and Tucker's (1951).

> [!key] Min-max theorem (von Neumann, 1928)
> For every matrix $A$, $\min_x\max_y\, xAy = \max_y\min_x\, xAy$, where $x$ and $y$ range over **probability vectors** (non-negative, summing to 1) — mixed strategies of the two players.

(The note omits the range of $x$ and $y$; over all real vectors the statement is empty — both sides are 0, since the inner optimum is infinite unless $xA = 0$, resp. $Ay = 0$.) The min-max theorem in turn follows from the **theorems of the alternative** proved by Gordan, Minkowski, Farkas, Stiemke, Motzkin and others around 1900. The earliest:

> [!key] Gordan's theorem of the alternative (1873)
> For every matrix $A$, exactly one of these holds: $Ax = 0$ for some non-zero $x\ge 0$; or $yA > 0$ (every entry positive) for some vector $y$.

(Both cannot hold: $yAx$ would be $0$ and $> 0$.) The easy half of the fundamental theorem needs none of this:

> [!key] Weak duality theorem
> If $x$ is feasible for the canonical LP (P) and $y$ is feasible for its dual (D), then $c\cdot x\le yAx\le y\cdot b$.

> [!proof]- Proof (click to expand)
> $x$ is feasible, so $Ax\le b$; multiplying by $y\ge 0$ keeps the inequality: $yAx\le y\cdot b$. $y$ is feasible, so $yA\ge c$; multiplying by $x\ge 0$: $yAx\ge c\cdot x$. $\square$

Two consequences:

- **Certificates.** If feasible $x$ and $y$ have $c\cdot x = y\cdot b$, both are optimal, exactly like a flow and a cut of equal value ([[2-algorithms/10-maximum-flows-and-minimum-cuts#102-cuts|Lemma 10.1]]).
- **Unbounded primal ⇒ infeasible dual**, and symmetrically, a feasible LP has a bounded dual.

The fundamental theorem turns the first consequence into an equivalence: feasible $x, y$ are optimal **if and only if** $c\cdot x = y\cdot b$. It does not do so for the second, as the note claims (p. 12): an LP and its dual can **both be infeasible** (the note says so in the same paragraph, adding that both are then degenerate), so an infeasible dual means the primal is unbounded **or infeasible**. The possible combinations:

| primal \ dual | optimal | infeasible | unbounded |
|---|---|---|---|
| optimal | yes, equal values | no | no |
| infeasible | no | possible (degenerate LPs) | yes |
| unbounded | no | yes | no |

Concept page: [[concepts/linear-programming]].

## H.6 Another duality example

Where does the dual come from? Take (an example from Vanderbei's textbook)
$$
\text{maximize } 4x_1 + x_2 + 3x_3\quad\text{subject to}\quad x_1 + 4x_2\le 2,\quad 3x_1 - x_2 + x_3\le 4,\quad x_1, x_2, x_3\ge 0,
$$
with optimum $\sigma^*$. Feasible points give lower bounds: $x = (1, 0, 0)$ gives $\sigma^*\ge 4$, and $x = (0, 0, 3)$ gives $\sigma^*\ge 9$. For an **upper** bound, multiply the constraints by non-negative numbers $y_1, y_2$ (non-negative, so the inequalities keep their direction) and add:
$$
(y_1 + 3y_2)x_1 + (4y_1 - y_2)x_2 + y_2x_3\le 2y_1 + 4y_2.
$$
If each coefficient on the left is at least the objective's — $y_1 + 3y_2\ge 4$, $4y_1 - y_2\ge 1$, $y_2\ge 3$ — then, because $x\ge 0$,
$$
4x_1 + x_2 + 3x_3\le(y_1 + 3y_2)x_1 + (4y_1 - y_2)x_2 + y_2x_3\le 2y_1 + 4y_2,\qquad(*)
$$
for every feasible $x$. The best such bound is the LP
$$
\text{minimize } 2y_1 + 4y_2\quad\text{subject to}\quad y_1 + 3y_2\ge 4,\quad 4y_1 - y_2\ge 1,\quad y_2\ge 3,\quad y_1, y_2\ge 0,
$$
which is precisely the dual, and $(*)$ is weak duality for this pair. **The dual variables are multipliers that combine the primal constraints into the best upper bound on the objective.**

> [!example] Example — the optimum (not in the note)
> $y = (1, 3)$ is dual feasible ($10\ge 4$, $1\ge 1$, $3\ge 3$) with value $2 + 12 = 14$, and $x^* = (0, 1/2, 9/2)$ is primal feasible — both constraints tight, $0 + 2 = 2$ and $0 - \tfrac12 + \tfrac92 = 4$ — with value $\tfrac12 + \tfrac{27}{2} = 14$. Equal values: both are optimal, and $\sigma^* = 14$. With $y = (1,3)$, $(*)$ reads $4x_1 + x_2 + 3x_3\le 10x_1 + x_2 + 3x_3\le 14$. Both optima are unique, and they satisfy complementary slackness strictly (§H.8): $y_1, y_2 > 0$ and both primal constraints are tight; $x_2, x_3 > 0$ and their dual constraints are tight ($1 = 1$, $3 = 3$); $x_1 = 0$ and its dual constraint is loose ($10 > 4$).

Concept page: [[concepts/linear-programming]].

## H.7 Strong duality

> [!key] Strong duality theorem
> If $x^*$ is an optimal solution of a canonical LP (P), then its dual (D) has an optimal solution $y^*$ with $c\cdot x^* = y^*Ax^* = y^*\cdot b$.

The note proves it only for **non-degenerate** LPs and $n\ge d$ (the general case needs more technical care, e.g. perturbation). Its non-degeneracy assumptions are (a) the objective vector is not normal to any constraint hyperplane, and (b) at most $d$ constraint hyperplanes pass through any point; it says (a) makes the optimum unique, hence a vertex. **For $d\ge 3$ it does not**: in the unit cube $0\le x_j\le 1$ with $c = (1, 1, 0)$, $c$ is normal to no facet and the cube satisfies (b), yet every point of the edge $x_1 = x_2 = 1$ is optimal. The assumption needed — the one note I states — is that $c$ is not a linear combination of fewer than $d$ constraint normals. Under it the optimum is a vertex where exactly $d$ of the $n + d$ constraints are tight.

> [!proof]- Proof sketch for non-degenerate LPs (click to expand)
> **Warm-up: $x^* = 0$.** Then the $d$ sign constraints are tight, and by (b) every other constraint is strict, $a_i\cdot x^* < b_i$. So for small $\delta > 0$ each point $\delta e_i$ is feasible, and since $x^*$ is the unique optimum, $\delta c_i = c\cdot(\delta e_i) < 0$: every $c_i < 0$. Then $y = 0$ satisfies $yA = 0\ge c$ and $y\ge 0$, and $y\cdot b = 0 = c\cdot x^*$: by weak duality $y$ is optimal.
>
> **General case.** Exactly $d$ constraints are tight at $x^*$; permuting constraints and changing coordinates, assume they are the first $d$ rows $a_1,\ldots,a_d$ of $A$: $a_i\cdot x^* = b_i$ for $i\le d$ and $a_i\cdot x^* < b_i$ for $i > d$. The $d\times d$ matrix $A_\bullet$ of these rows is invertible; let $v_j$ be the $j$th column of $V = A_\bullet^{-1}$, so $a_i\cdot v_j = [i = j]$. Define $y_j = c\cdot v_j$ for $j\le d$ and $y_j = 0$ for $j > d$. Then
> $$
> yA = y_\bullet A_\bullet = cVA_\bullet = c,\qquad y\cdot b = y_\bullet\cdot b_\bullet = cVA_\bullet x^* = c\cdot x^*.
> $$
> It remains to show $y\ge 0$. For small $\varepsilon > 0$ the point $\tilde x = x^* - \varepsilon v_j$ keeps the other $d - 1$ tight constraints tight, loosens the $j$th ($a_j\cdot\tilde x = b_j - \varepsilon$) and, being close to $x^*$, satisfies the strict ones: it is feasible. Since $x^*$ is the unique optimum, $c\cdot\tilde x = c\cdot x^* - \varepsilon y_j < c\cdot x^*$, so $y_j > 0$. Thus $y$ is dual feasible with $y\cdot b = c\cdot x^*$, and optimal by weak duality. $\square$

**The dual as forces.** The proof shows more: the non-zero dual variables are the coordinates of $c$ in the basis formed by the normals of the tight constraints, $c = \sum_{i\le d}y_ia_i$ with every $y_i > 0$. Physically, let the objective be gravity and drop a marble into the polyhedron: at the lowest point gravity still pulls, the marble does not move, so the constraint walls it touches push back, each along its own normal — and $y_i$ is the force of wall $i$. Walls it does not touch exert no force (§H.8).

<!-- fig:nh-dual-forces -->
<figure class="cs-fig"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 440 300" width="440" height="300" role="img" style="font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-size:14px"><title>the pentagon with the optimum (3,1); arrows 2 times (1,1) and 1 times (1,0) add up to the objective vector (3,2)</title><defs><marker id="ARR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs><path d="M52,250 L217,250 L217,195 L162,140 L52,85 Z" fill="var(--accent)" fill-opacity="0.13" stroke="none" stroke-width="0"/><line x1="35.5" y1="250" x2="349" y2="250" stroke="var(--muted)" stroke-width="1.1" stroke-linecap="round" marker-end="url(#ARR)"/><line x1="52" y1="266.5" x2="52" y2="19" stroke="var(--muted)" stroke-width="1.1" stroke-linecap="round" marker-end="url(#ARR)"/><text x="345" y="263" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:14px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">x</text><text x="41" y="24" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:14px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">y</text><line x1="107" y1="247" x2="107" y2="253" stroke="var(--muted)" stroke-width="1" stroke-linecap="round"/><line x1="162" y1="247" x2="162" y2="253" stroke="var(--muted)" stroke-width="1" stroke-linecap="round"/><line x1="217" y1="247" x2="217" y2="253" stroke="var(--muted)" stroke-width="1" stroke-linecap="round"/><line x1="272" y1="247" x2="272" y2="253" stroke="var(--muted)" stroke-width="1" stroke-linecap="round"/><line x1="49" y1="195" x2="55" y2="195" stroke="var(--muted)" stroke-width="1" stroke-linecap="round"/><line x1="49" y1="140" x2="55" y2="140" stroke="var(--muted)" stroke-width="1" stroke-linecap="round"/><line x1="49" y1="85" x2="55" y2="85" stroke="var(--muted)" stroke-width="1" stroke-linecap="round"/><line x1="54.8" y1="32.8" x2="285.8" y2="263.8" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" opacity="0.55"/><line x1="38.2" y1="78.1" x2="335.2" y2="226.6" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" opacity="0.55"/><line x1="217" y1="263.8" x2="217" y2="32.8" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" opacity="0.55"/><path d="M52,250 L217,250 L217,195 L162,140 L52,85 Z" fill="none" fill-opacity="1" stroke="currentColor" stroke-width="1.8"/><text x="127.2" y="63.2" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">x + y ≤ 4</text><text x="217" y="57.8" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">x ≤ 3</text><text x="317.2" y="229.9" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">x + 2y ≤ 6</text><line x1="277.5" y1="134.5" x2="307.8" y2="134.5" stroke="var(--muted)" stroke-width="1.1" stroke-linecap="round" stroke-dasharray="4 3"/><line x1="247.2" y1="195" x2="307.8" y2="134.5" stroke="var(--muted)" stroke-width="1.1" stroke-linecap="round" stroke-dasharray="4 3"/><line x1="217" y1="195" x2="277.5" y2="134.5" stroke="var(--accent)" stroke-width="2.2" stroke-linecap="round" marker-end="url(#ARR)"/><line x1="217" y1="195" x2="247.2" y2="195" stroke="var(--accent)" stroke-width="2.2" stroke-linecap="round" marker-end="url(#ARR)"/><line x1="217" y1="195" x2="307.8" y2="134.5" stroke="var(--accent2)" stroke-width="2.6" stroke-linecap="round" marker-end="url(#ARR)"/><circle cx="217" cy="195" r="4.2" fill="var(--hi)" stroke="var(--hi)" stroke-width="1.2"/><text x="243.5" y="124.5" text-anchor="middle" dominant-baseline="central" fill="var(--accent)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">2 · (1, 1)</text><text x="265.2" y="211" text-anchor="middle" dominant-baseline="central" fill="var(--accent)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">1 · (1, 0)</text><text x="347.8" y="132.5" text-anchor="middle" dominant-baseline="central" fill="var(--accent2)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">c = (3, 2)</text><text x="191" y="207" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">(3, 1)</text></svg><figcaption><strong>The dual solution as forces at the optimum.</strong> At (3, 1) the constraints <i>x</i> + <i>y</i> ≤ 4 and <i>x</i> ≤ 3 are tight; their outward normals (1, 1) and (1, 0) combine to the objective vector, <i>c</i> = (3, 2) = 2 · (1, 1) + 1 · (1, 0). The coefficients are the optimal dual variables, <i>y</i> = (2, 0, 1): the loose constraint <i>x</i> + 2<i>y</i> ≤ 6 gets 0, and the dual value 4 · 2 + 3 · 1 = 11 equals the primal optimum. (Arrows drawn at 0.55 scale.)</figcaption></figure>

> [!example] Example — reading the dual off the optimum
> In the figure's LP the optimum $(3, 1)$ (value 11) has $x + y\le 4$ and $x\le 3$ tight, and $c = (3,2) = 2\cdot(1,1) + 1\cdot(1,0)$: the dual solution is $(y_1, y_2, y_3) = (2, 0, 1)$ — zero for the loose $x + 2y\le 6$ — with value $4\cdot 2 + 3\cdot 1 = 11$.

Concept page: [[concepts/linear-programming]].

## H.8 Complementary slackness

Equal optimal values force more than equality. In the chain $c\cdot x^*\le y^*Ax^*\le y^*\cdot b$ both inequalities are equalities, and each is a sum of non-negative terms: $y^*\cdot b - y^*Ax^* = \sum_i y_i^*(b_i - a_i\cdot x^*)$ and $y^*Ax^* - c\cdot x^* = \sum_j x_j^*(y^*\cdot a^j - c_j)$, where $a_i$ is the $i$th row and $a^j$ the $j$th column of $A$. So every term is zero:

> [!definition] Complementary slackness conditions
> - for every row $i$: $y_i^* = 0$ or $a_i\cdot x^* = b_i$ (or both);
> - for every column $j$: $x_j^* = 0$ or $y^*\cdot a^j = c_j$ (or both).
>
> (The note prints the right-hand sides as $b$ and $c$, pp. 16–17.) Calling a constraint **tight** if it holds with equality and **loose** otherwise: a positive primal variable has a tight dual constraint, a loose dual constraint has a zero primal variable, a positive dual variable has a tight primal constraint, a loose primal constraint has a zero dual variable.

> [!key] Complementary slackness theorem (corrected)
> Let $x$ be feasible for a canonical LP and $y$ feasible for its dual. The following are equivalent:
> 1. $x$ and $y$ are both optimal;
> 2. $c\cdot x = y\cdot b$;
> 3. $c\cdot x = yAx$ **and** $yAx = y\cdot b$;
> 4. $x$ and $y$ satisfy all the complementary slackness conditions.

The note (p. 16) lists "$c\cdot x = yAx$" and "$yAx = y\cdot b$" as two **separate** conditions each equivalent to optimality. Each alone is only half of the slackness conditions — the first is exactly the column conditions, the second exactly the row conditions — and neither suffices. In the §H.6 example with $y = (1, 3)$: $x = 0$ has $c\cdot x = yAx = 0$ but value $0 < 14$; and $x = (1, \tfrac14, \tfrac54)$ is feasible with $yAx = y\cdot b = 14$ (both rows tight) but $c\cdot x = 8$.

> [!example] Example — complementary slackness on the shortest-path pair
> For the two shortest-path LPs of §H.3 the row conditions read: an edge with $x(u\to v) > 0$ is tight, $\mathit{dist}(v) - \mathit{dist}(u) = \ell(u\to v)$. (The column conditions say nothing here: the variables $\mathit{dist}(v)$ are free, so their dual constraints are equations, always tight.) That is the familiar fact that a shortest path uses only tight edges — in the example, the four edges of $s\,a\,b\,c\,t$, while $s\to b$, $a\to c$, $b\to t$ are loose and carry no flow. For maximum flow and minimum cut they say that an optimal flow saturates every edge crossing the minimum cut forward and avoids every edge crossing it backward ([[2-algorithms/10-maximum-flows-and-minimum-cuts#102-cuts|Lemma 10.1]]).

**Strict complementary slackness.** The conditions are not exclusive: a constraint can be tight while its dual variable is 0. Still, every feasible and bounded LP has *some* optimal pair $x^*, y^*$ with exactly one of $y_i^* > 0$ and $a_i\cdot x^* < b_i$ for every row, and exactly one of $x_j^* > 0$ and $y^*\cdot a^j > c_j$ for every column (a theorem of Goldman and Tucker, 1956). A non-degenerate LP has unique primal and dual optima, so they are that pair. For degenerate LPs a given optimal pair need not be strict: in the network $s\to a\to t$ with capacities 1, the maximum flow saturates both edges, but each of the two minimum cuts (as 0/1 solutions of the cut LP) has $x = 0$ on one of them; the strictly complementary partner is the fractional optimum $S(a) = \tfrac12$, $x = (\tfrac12, \tfrac12)$ of §H.3.

> [!trap] Duality traps
> - **Weak duality needs feasibility of both points.** An infeasible $y$ proves nothing.
> - **Complementary slackness characterizes optimality only for feasible pairs.** Points that satisfy all the slackness conditions but violate a constraint are not optimal (the simplex method of note I walks through such points).
> - **"Tight" is not "positive"**: a tight constraint may have dual variable 0.
> - **Both LPs can be infeasible.** "Dual infeasible" does not mean "primal unbounded".

Concept page: [[concepts/linear-programming]].

## Summary

- An LP optimizes $c\cdot x$ over $x\in\mathbb{R}^d$ subject to linear constraints; canonical form $\max\{c\cdot x : Ax\le b,\ x\ge 0\}$ (split free variables, double equations, negate $\ge$), slack form $Ax = b$, $x\ge 0$ (add slack variables).
- The feasible region is a convex polyhedron; an LP is infeasible, unbounded, or has an optimum (at a vertex when there are vertices).
- Shortest path: $\max\mathit{dist}(t)$ s.t. no tense edge (feasible iff no negative cycle, bounded iff $t$ reachable); its dual is the unit-flow minimum-cost LP. Single source: $\max\sum_v\mathit{dist}(v)$ and its dual with demand 1 everywhere, solved by $x = \lvert D_v\rvert$ on the tree. Max flow and min cut are a dual pair; the cut LP has a 0/1 optimum but may have fractional ones.
- Dual of $\max\{c\cdot x : Ax\le b, x\ge 0\}$ is $\min\{y\cdot b : yA\ge c, y\ge 0\}$; for any LP use the table (constraints ↔ variables, natural ↔ natural, equation ↔ free variable). The dual of the dual is the primal.
- Weak duality $c\cdot x\le yAx\le y\cdot b$; equal values certify optimality. Fundamental theorem: one optimum exists iff the other does, with equal values (proved for non-degenerate LPs by $y_\bullet = cA_\bullet^{-1}$, the coordinates of $c$ in the tight normals — the forces on the marble).
- Complementary slackness: for feasible $x, y$, optimal ⇔ $c\cdot x = y\cdot b$ ⇔ every positive variable has a tight dual constraint, on both sides. A strictly complementary optimal pair always exists.
- The note ends with 10 exercises (self-dual LPs; LPs for bipartite matching and minimum-cost circulation and their duals; largest square, rectangle and circle in a polygon; $L_1$ and $L_\infty$ line fitting; maximum-weight prefixes and intervals; equalizing path lengths; integer programming is NP-hard; Carathéodory's and Helly's theorems).

> [!exam] For CS 374
> **Not on the CS/ECE 374 exams**: linear programming is not taught in CS 374 this semester (it is CS 473 material at Illinois), and maximum flows, its main example here, are not examined either. What transfers: the shortest-path LP is a crisp restatement of [[2-algorithms/08-shortest-paths#83-the-only-sssp-algorithm|Ford's relaxation]] (feasible potentials are lower bounds, and a negative cycle means no feasible potentials), and the maxflow-mincut theorem is the best-known instance of the pattern "a max problem, a min problem, weak inequality by a two-line argument, equality by an algorithm". Integer programming, by contrast, is NP-hard — a standard target for reductions from [[2-algorithms/12-np-hardness|Chapter 12]] problems.

### Sources for this page
Erickson, *Linear Programming*, Extended Dance Remix H (21 pp., © 2018, CC BY-NC-SA 4.0; "Status: Text beta. Needs figures."), §§H.1–H.8 summarized in our own words; the 10 exercises (pp. 17–21) are listed, not solved. The definitions, the shortest-path, single-source, max-flow and min-cut LPs, the dualization table (Figure H.4), the theorems and the proof sketch, the infeasible example (Figure H.2) and Vanderbei's example (after Vanderbei and Clausen) are the note's; the note's Figures H.1–H.3 sketch polyhedra (H.2 is the infeasible example, redrawn here); the four figures here are ours; the optimum of Vanderbei's example, the 2D example LP, the shortest-path example graph, the fractional min-cut example and the cube are ours. Checked by `tools/checks/nh.py`: every example LP solved with `scipy.optimize.linprog` and its stated optimum certified exactly (a primal and a dual point with equal value); every dual on the page built by an implementation of Figure H.4 and solved; the table itself on 2,500 random LPs with mixed constraint types and variable signs (equal optima, unbounded ⇒ infeasible dual, dual of dual = primal); the canonical and slack conversions; weak duality, Gordan's theorem and the min-max theorem on random instances; the proof's construction $y_\bullet = cA_\bullet^{-1}$; the complementary slackness theorem and strict complementarity (also on degenerate LPs); the shortest-path LPs (and the minimization of $\mathit{dist}(t)$ in the trap) against Bellman–Ford and the max-flow/min-cut LPs against networkx and brute-force minimum cuts on hundreds of random graphs, including feasibility, boundedness, uniqueness and the duality between them.
**Errors in the note** (page, as printed → correct): p. 2, canonical constraints "$Ax\ge b$" → $Ax\le b$; p. 3, "$x_i^+$, $x_i^-$" → $x_j^+$, $x_j^-$, and "replace any upper bound constraint $\sum_j a_{ij}x_j\ge b_i$ with the equivalent lower bound" → a lower bound becomes an upper bound; p. 5, the unboundedness witness ($\mathit{dist} = 0$ on reachable vertices) can be infeasible with negative edges → add $M$ to the unreachable vertices of any feasible solution; p. 6, "unique optimum iff (1) every vertex on an $s$–$t$ path and (2) all $s$–$t$ paths of equal length" → sufficient but not necessary; with positive lengths unique iff every vertex lies on a shortest $s$–$t$ path (counterexample: the page's example graph, checked); p. 7, "$D_v = \lvert v\rvert$ if $v$ is a leaf" → $D_v = \{v\}$; p. 11, the min-max theorem without its range (over all real vectors it reads $0 = 0$) → $x, y$ probability vectors; p. 12, "all these implications are actually equivalences" → false for "unbounded ⇒ dual infeasible", since both LPs can be infeasible; p. 14, non-degeneracy (a) "objective not normal to any constraint hyperplane" does not make the optimum unique for $d\ge 3$ (unit cube, $c = (1,1,0)$) → $c$ not a combination of fewer than $d$ normals, as in note I; pp. 16–17, "$a_i\cdot x^* = b$", "$y^*\cdot a^j = c$" (and "$< b$", "$> c$" in the strict conditions) → $b_i$, $c_j$; p. 16, the complementary slackness theorem lists $c\cdot x = yAx$ and $yAx = y\cdot b$ as separately equivalent to optimality → only together (counterexamples above, checked). Minor: p. 8, "$f\in E^{\mathbb{R}}$" → $f\in\mathbb{R}^E$; p. 19, Exercise 7 colors edges red, white or blue but then speaks of black edges. Not machine-checked: the history, and the proof sketch itself (its construction is checked numerically). The strict-complementarity attribution (Goldman–Tucker) and the remark on attained optima are ours, not the note's.
