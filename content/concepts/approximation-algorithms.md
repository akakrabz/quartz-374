---
title: "Approximation algorithms"
description: "A polynomial-time algorithm that is always within a factor α of the optimum: the ratio for minimization and maximization, how to prove one by bounding the optimum, tight examples, and the classic results — load balancing, vertex cover by greed, matching and LP rounding, set cover's logarithm, metric TSP within 2 and 3/2, general TSP not at all, k-center, PTAS and FPTAS."
tags: [concept, algorithms, complexity]
aliases: ["approximation algorithm", "approximation ratio", "approximation factor", "alpha-approximation", "PTAS", "FPTAS", "approximation scheme", "LP rounding", "metric TSP", "Christofides"]
---

> [!definition] Definition (§J.2)
> Let $\mathrm{OPT}(X)$ be the optimal value for input $X$ and $A(X)$ the value of the solution algorithm $A$ returns. $A$ is an **$\alpha$-approximation algorithm** ($\alpha\ge 1$, possibly a function of the input size $n$) if it runs in **polynomial time** and, for **every** input $X$,
> $$
> A(X)\le\alpha\cdot\mathrm{OPT}(X)\ \ \text{(minimization)}, \qquad A(X)\ge\mathrm{OPT}(X)/\alpha\ \ \text{(maximization)}.
> $$
> $\alpha$ is the **approximation ratio** (or factor); $\alpha = 1$ means exact. An **approximation scheme** takes $\varepsilon > 0$ as a second input and is a $(1+\varepsilon)$-approximation; it is a **PTAS** if its time is polynomial in $n$ for each fixed $\varepsilon$, and an **FPTAS** if it is polynomial in $n$ and $1/\varepsilon$. (For maximization some authors write the ratio as a number below 1, such as $1-\varepsilon$.)

**Why it works.** For an NP-hard problem the optimum cannot be computed, so a proof never mentions what the optimal solution looks like. It compares the algorithm with a quantity $L(X)$ that **every** solution must respect — a lower bound $L(X)\le\mathrm{OPT}(X)$ for a minimization problem — and then shows $A(X)\le\alpha\,L(X)$ from the algorithm's steps. The art is choosing $L$: strong enough to be close to $\mathrm{OPT}$, simple enough to compare with the algorithm.

> [!recipe] Recipe — proving an $\alpha$-approximation (minimization)
> 1. **Lower bound.** Name $L(X)$ and prove $L(X)\le\mathrm{OPT}(X)$ for every input. Standard choices: the largest job and the average load; a matching (each edge needs its own cover vertex); a linear-programming relaxation (more feasible solutions, so a smaller minimum); a minimum spanning tree (a tour minus an edge is a spanning tree); $k+1$ points pairwise far apart (two share one of $k$ clusters).
> 2. **Upper bound.** Follow the algorithm to show $A(X)\le\alpha\,L(X)$.
> 3. **Conclude** $A(X)\le\alpha\,\mathrm{OPT}(X)$, and give the (polynomial) running time.
> 4. **Tight example** (optional): an input with $A = \alpha\cdot\mathrm{OPT}$, or a family with ratio tending to $\alpha$, shows that this analysis of this algorithm cannot be improved.

| problem | algorithm | ratio | the lower bound on OPT |
|---|---|---|---|
| load balancing, $m$ machines | greedy; sorted greedy | 2 (exactly $2-\frac1m$); $\frac32$ (exactly $\frac43-\frac1{3m}$) | largest job; average load; two of the $m+1$ largest jobs share a machine |
| vertex cover | largest degree first | $H(\Delta) = O(\log n)$ | the optimal cover covers every remaining graph |
| vertex cover | both ends of a maximal matching | 2 | the matching |
| weighted vertex cover | **LP rounding**: take $v$ iff $x^*(v)\ge\frac12$ | 2 | the LP optimum |
| set cover; hitting set | greedy | $H(\max\lvert S\rvert)\le 1+\ln\lvert X\rvert$; $1+\ln\lvert\mathcal F\rvert$ | pricing argument |
| **metric TSP** | tree doubling; **Christofides** | 2; $\frac32$ | MST $\le$ OPT; odd-vertex matching $\le$ OPT/2 |
| general TSP | none possible | no polynomial-time computable $f(n)$ unless P = NP | — |
| $k$-center | Gonzalez (farthest point) | 2 | $k+1$ centers pairwise $\ge r_k$ apart |
| max subset sum $\le t$ | trimmed lists of sums | FPTAS, $O(n^3\log n/\varepsilon)$ | — |

> [!trap]
> - **NP-hard problems approximate very differently**: subset sum has an FPTAS, metric TSP is within $\frac32$, set cover only within $\ln\lvert X\rvert$, and general TSP within no polynomial-time computable factor $f(n)$ unless P = NP (Theorem J.4: a gap reduction from Hamiltonian cycle, non-edges of length $n f(n) + 1$). NP-hardness alone says nothing about approximability.
> - **The triangle inequality** is what makes shortcuts in TSP tours safe; without it, tree doubling can exceed $2\cdot\mathrm{OPT}$.
> - **A tight example is about the analysis**, not the problem: it shows this algorithm can be off by $\alpha$, not that no algorithm does better.
> - **The lower bound limits the proof.** The vertex-cover LP has value $n/2$ on $K_n$ while $\mathrm{OPT} = n-1$, so no analysis against the LP can prove a ratio below 2.
> - **Set cover is logarithmic in the ground set** $\lvert X\rvert$, not in the number of sets (Erickson's note J has these swapped).

**Example.** Gonzalez's algorithm on the three points $-1, 0, 1$ of a line, $k = 1$, starting from $p_1 = -1$: the single center is $-1$, the farthest point is $1$, so $r_1 = 2$; the optimal center $0$ gives radius 1. The ratio is exactly 2, and the lower bound in the proof is exactly what is attained: $c_1 = -1$ and $c_2 = 1$ are 2 apart, so any one disk containing both has radius at least 1.

**Where it appears.** Erickson's note J: [[4-lecture-notes/j-approximation-algorithms#j1-load-balancing|§J.1]] (load balancing), [[4-lecture-notes/j-approximation-algorithms#j2-generalities|§J.2]] (the definition), [[4-lecture-notes/j-approximation-algorithms#j3-greedy-vertex-cover|§J.3]]–[[4-lecture-notes/j-approximation-algorithms#j5-vertex-cover-redux|§J.5]] (vertex cover, set cover and hitting set), [[4-lecture-notes/j-approximation-algorithms#j6-lightest-vertex-cover-lp-rounding|§J.6]]–[[4-lecture-notes/j-approximation-algorithms#j7-randomized-lp-rounding|§J.7]] (LP rounding), [[4-lecture-notes/j-approximation-algorithms#j8-traveling-salesman-the-bad-news|§J.8]]–[[4-lecture-notes/j-approximation-algorithms#j9-traveling-salesman-the-good-news|§J.9]] (TSP), [[4-lecture-notes/j-approximation-algorithms#j10-k-center-clustering|§J.10]] ($k$-center), [[4-lecture-notes/j-approximation-algorithms#j11-approximation-schemes|§J.11]]–[[4-lecture-notes/j-approximation-algorithms#j12-an-fptas-for-subset-sum|§J.12]] (PTAS and FPTAS). The NP-hard problems themselves: [[2-algorithms/12-np-hardness#129-clique-and-vertex-cover-from-independent-set|§12.9]] (vertex cover), [[2-algorithms/12-np-hardness#1211-hamiltonian-cycle|§12.11]] (TSP), [[2-algorithms/12-np-hardness#caveat-reductor|§12.12]] (subset sum's pseudo-polynomial algorithm).

Related: [[concepts/np-hardness]] · [[concepts/polynomial-time-reductions]] · [[concepts/independent-set]] · [[concepts/hamiltonian-cycle]] · [[concepts/subset-sum]] · [[concepts/minimum-spanning-trees]] · [[concepts/linear-programming]] · [[concepts/greedy-algorithms]]
