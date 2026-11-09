---
title: "Linear programming"
description: "Optimize a linear function subject to linear inequalities: canonical and slack form, infeasible / unbounded / optimal, the dual LP and how to write it, weak and strong duality, complementary slackness, and shortest paths and maximum flow as LPs."
tags: [concept, algorithms, linear-programming]
aliases: ["LP", "linear program", "linear programs", "LP duality", "strong duality", "weak duality", "complementary slackness"]
---

> [!definition] Definition — linear program, duality
> A **linear program** maximizes or minimizes $c\cdot x$ over $x\in\mathbb{R}^d$ subject to finitely many linear inequalities and equations. **Canonical form**: $\max\{c\cdot x : Ax\le b,\ x\ge 0\}$; **slack form**: $Ax = b$, $x\ge 0$ (either may be called "standard"). The feasible set is a convex polyhedron, and the LP is **infeasible**, **unbounded**, or has an **optimum** (attained at a vertex if there is one). The **dual** of the canonical LP is
> $$
> \min\{\,y\cdot b : yA\ge c,\ y\ge 0\,\},
> $$
> one variable per primal constraint, one constraint per primal variable; the dual of the dual is the primal.
> - **Weak duality**: for feasible $x, y$, $c\cdot x\le yAx\le y\cdot b$.
> - **Strong duality** (fundamental theorem): one LP has an optimum iff the other does, and the optimal values are equal.
> - **Complementary slackness**: feasible $x, y$ are both optimal iff $y_i > 0$ only on tight rows ($a_i\cdot x = b_i$) and $x_j > 0$ only where the dual constraint is tight ($y\cdot a^j = c_j$).

**Why it works.** Dual variables are multipliers: adding $y_i\ge 0$ times each primal row gives $(yA)\cdot x\le y\cdot b$, and if $yA\ge c$ this bounds $c\cdot x$ for every feasible $x\ge 0$. The dual asks for the best such bound, and strong duality says it is exact; at the optimum $c$ is a non-negative combination of the normals of the tight constraints, with the dual variables as coefficients. Shortest paths ($\max\mathit{dist}(t)$ s.t. no tense edge, dual: a minimum-cost unit $s$–$t$ flow) and maximum flow (dual: the minimum-cut LP) are dual pairs; maxflow = mincut is strong duality plus the fact that the cut LP has a 0/1 optimal solution.

> [!recipe] Recipe — the dual of any LP
> 1. One dual variable per constraint. In a **max** LP: $\le$ row → $y_i\ge 0$; $\ge$ row → $y_i\le 0$; $=$ row → $y_i$ free.
> 2. One dual constraint per variable, using its column: $x_j\ge 0$ → $\sum_i y_ia_{ij}\ge c_j$; $x_j\le 0$ → $\le c_j$; $x_j$ free → $= c_j$; $x_j$ fixed at 0 → none.
> 3. Objective $\min\sum_i y_ib_i$. For a **min** LP every sign flips (natural $\ge$ rows and $x\ge 0$ map to natural $y\ge 0$ and $\le$ dual rows in a max LP).
> 4. Sanity check with weak duality on any feasible pair.

> [!trap]
> - **Both LPs can be infeasible**: an infeasible dual means "unbounded *or* infeasible".
> - **Equal objective values certify optimality only for feasible pairs**, and "$c\cdot x = yAx$" alone (or "$yAx = y\cdot b$" alone) is only half of complementary slackness — not enough.
> - **Integrality is not automatic**: an LP with integer data can have only fractional optima; integer programming is NP-hard. Flow, cut and shortest-path LPs are the lucky exceptions.
> - **Mixing up the two halves of the dualization table** (max vs min) flips every sign.

**Example.** $\max 3x + 2y$ s.t. $x + y\le 4$, $x + 2y\le 6$, $x\le 3$, $x, y\ge 0$. Its vertices $(0,0), (3,0), (3,1), (2,2), (0,3)$ have values $0, 9, 11, 10, 6$, so the optimum is $(3, 1)$ with value 11. The dual is $\min 4a + 6b + 3c$ s.t. $a + b + c\ge 3$, $a + 2b\ge 2$, $a, b, c\ge 0$. Complementary slackness finds it: $x + 2y = 5 < 6$ is loose, so $b = 0$; $x, y > 0$, so both dual rows are tight: $a + c = 3$, $a = 2$. Thus $(a, b, c) = (2, 0, 1)$, value $8 + 3 = 11$ — equal, so both are optimal, and $(3, 2) = 2\cdot(1,1) + 1\cdot(1,0)$.

**Where it appears.** [[4-lecture-notes/h-linear-programming#h1-introduction|§H.1]] (forms), [[4-lecture-notes/h-linear-programming#h2-the-geometry-of-linear-programming|§H.2]] (geometry), [[4-lecture-notes/h-linear-programming#h3-examples|§H.3]] (shortest paths, max flow, min cut as LPs), [[4-lecture-notes/h-linear-programming#h4-linear-programming-duality|§H.4]] (the dual and its table), [[4-lecture-notes/h-linear-programming#h5-the-fundamental-theorem|§H.5]]–[[4-lecture-notes/h-linear-programming#h7-strong-duality|§H.7]] (weak and strong duality), [[4-lecture-notes/h-linear-programming#h8-complementary-slackness|§H.8]] (complementary slackness); algorithms in [[4-lecture-notes/i-linear-programming-algorithms|note I]]; LP rounding in [[4-lecture-notes/j-approximation-algorithms#j6-lightest-vertex-cover-lp-rounding|§J.6]]; the textbook's instances in [[2-algorithms/08-shortest-paths#83-the-only-sssp-algorithm|§8.3]] and [[2-algorithms/10-maximum-flows-and-minimum-cuts#103-the-maxflow-mincut-theorem|§10.3]].

Related: [[concepts/simplex-algorithm]] · [[concepts/maximum-flow]] · [[concepts/shortest-paths]] · [[concepts/minimum-cost-flow]] · [[concepts/approximation-algorithms]] · [[concepts/np-hardness]]
