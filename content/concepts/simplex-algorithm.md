---
title: "Simplex algorithm"
description: "Dantzig's method for linear programs: walk between neighboring vertices (bases), keeping feasibility (primal simplex) or local optimality (dual simplex), until both hold; initial bases, pivot rules and their exponential worst case, network simplex on spanning trees, and Seidel's randomized algorithm for fixed dimension."
tags: [concept, algorithms, linear-programming]
aliases: ["simplex", "simplex method", "pivoting", "pivot rule", "network simplex", "dual simplex", "Seidel's algorithm"]
---

> [!definition] Definition — bases and pivots (Erickson's geometric view)
> For a canonical LP $\max\{c\cdot x : Ax\le b,\ x\ge 0\}$ with $d$ variables and $n + d$ constraints, a **basis** is a set of $d$ constraints; its **location** is the point where all $d$ are tight. It is **feasible** if the location satisfies every constraint, and **locally optimal** if $c$ is a non-negative combination of the $d$ normals (equivalently, the complementary dual basis is feasible). Two bases are **neighbors** if they share $d - 1$ constraints; a **pivot** moves to a neighbor. The optimum (non-degenerate LP) is the unique basis that is feasible *and* locally optimal.
> - **Primal simplex**: from a feasible basis, pivot to a feasible neighbor of larger value until locally optimal; if none exists first, the LP is **unbounded**.
> - **Dual simplex**: from a locally optimal basis, pivot to a locally optimal neighbor of smaller value until feasible; if none exists first, the LP is **infeasible**.
>
> At most $\binom{n+d}{d}$ pivots, since the value moves strictly monotonically.

**Why it works.** Every feasible value is at most every locally optimal value (weak duality), so primal pivots climb towards the optimum from below and dual pivots descend to it from above; running one on an LP is running the other on its dual. To **start**, make an arbitrary basis locally optimal by replacing $c$ with a positive combination of its normals (their sum) and run the dual simplex — feasibility does not depend on $c$; or make it feasible by translating the constraints and run the primal simplex. (Textbooks use an auxiliary "phase I" LP instead.) **Network simplex**: for an uncapacitated minimum-cost flow (transshipment) problem the bases are spanning trees; the tree's flow on an edge is the total balance on its head side, a non-tree edge's slack is the cost of the cycle it closes (its reduced cost), primal pivots cancel such cycles and dual pivots shift potentials across a tree cut. **Seidel's algorithm** (fixed dimension $d$): drop a random constraint $h$, solve recursively, and if the answer violates $h$, solve again on the hyperplane $\partial h$ — one dimension less; $O(d!\cdot n)$ expected time.

> [!recipe] Recipe — one dictionary pivot (textbook form)
> 1. Write each basic variable (initially the slacks $w_i = b_i - a_i\cdot x$) and the objective in terms of the non-basic ones, which are 0.
> 2. **Entering** variable: one with a positive objective coefficient (Dantzig: the largest; Bland: the smallest index). None: optimal.
> 3. **Ratio test**: raise it until the first basic variable hits 0 — that one **leaves**. Nothing limits it: unbounded.
> 4. Solve the leaving row for the entering variable and substitute everywhere.

> [!trap]
> - **Erickson's basis = the $d$ tight constraints = the textbook's *non*-basic variables** (a tight $x_j\ge 0$ is a non-basic $x_j$, a tight row a non-basic slack).
> - **Positive inner products with the normals do not make a vertex locally optimal**; a positive *combination* does ($c = (1,2)$ against normals $(1,0), (1,1)$ is a counterexample).
> - **Exponential worst case**: Dantzig's rule takes $2^d - 1$ pivots on the Klee–Minty cube; no pivot rule is known to be polynomial (LPs are polynomial by ellipsoid or interior-point methods).
> - **Degenerate LPs** allow pivots that do not change the value, and careless rules can cycle; Bland's rule cannot.

**Example.** $\max 4x_1 + x_2 + 3x_3$ s.t. $x_1 + 4x_2\le 2$, $3x_1 - x_2 + x_3\le 4$, $x\ge 0$, Dantzig's rule from the origin. Pivot 1: $x_1$ enters; the ratio test allows $x_1\le 2$ in row 1 and $x_1\le 4/3$ in row 2, so $w_2$ leaves: vertex $(4/3, 0, 0)$, value $16/3$, objective $16/3 + \tfrac73x_2 + \tfrac53x_3 - \tfrac43w_2$. Pivot 2: $x_2$ enters, $w_1$ leaves: $(18/13, 2/13, 0)$, value $74/13$. Pivot 3: $x_3$ enters, $x_1$ leaves: $(0, 1/2, 9/2)$, value 14, where every objective coefficient is negative — optimal. In Erickson's terms the tight sets are $\{x_1, x_2, x_3\ge 0\}\to\{\text{row }2, x_2, x_3\ge 0\}\to\{\text{rows }1, 2, x_3\ge 0\}\to\{\text{rows }1, 2, x_1\ge 0\}$: one constraint swapped per pivot.

**Where it appears.** [[4-lecture-notes/i-linear-programming-algorithms#i1-bases-feasibility-and-local-optimality|§I.1]] (bases), [[4-lecture-notes/i-linear-programming-algorithms#i2-the-simplex-algorithm|§I.2]] (primal and dual simplex), [[4-lecture-notes/i-linear-programming-algorithms#i3-computing-the-initial-basis|§I.3]] (initial bases), [[4-lecture-notes/i-linear-programming-algorithms#i4-network-simplex|§I.4]] (network simplex), [[4-lecture-notes/i-linear-programming-algorithms#i5-linear-expected-time-for-fixed-dimensions|§I.5]] (Seidel); duality in [[4-lecture-notes/h-linear-programming#h7-strong-duality|§H.7]]; cycle canceling in [[4-lecture-notes/g-minimum-cost-flows#g1-minimum-cost-circulations|§G.1]].

Related: [[concepts/linear-programming]] · [[concepts/minimum-cost-flow]] · [[concepts/maximum-flow]] · [[concepts/minimum-spanning-trees]] · [[concepts/ford-fulkerson]]
