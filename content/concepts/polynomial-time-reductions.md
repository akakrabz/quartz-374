---
title: "Polynomial-time reductions"
description: "Karp (many-one) reductions and how they prove NP-hardness: the direction rule, the three algorithms behind every reduction, the exam write-up and its 10-point rubric, the classic mistakes, and a complete small example."
tags: [concept, algorithms, complexity]
aliases: ["Karp reduction", "many-one reduction", "NP-hardness proof", "polynomial-time reduction", "Cook reduction"]
---

> [!key] Definition and the direction rule (§12.4–12.5, §12.8)
> A **polynomial-time (Karp, many-one) reduction** from problem $X$ to problem $Y$ is an algorithm that transforms **any** instance $x$ of $X$ into an instance $y$ of $Y$ in polynomial time, so that
> $$
> x \text{ is a YES instance of } X \iff y \text{ is a YES instance of } Y .
> $$
> Then a polynomial-time algorithm for $Y$ gives one for $X$: transform, then ask $Y$. So **to prove $Y$ NP-hard, reduce a known NP-hard problem $X$ to $Y$** — never $Y$ to $X$. (A **Cook reduction** may call the algorithm for $Y$ many times and post-process its answers; the course's reductions are all Karp reductions.)

**Why it works.** The reduction is a proof by contradiction: if $Y$ were easy, then $X$ would be easy, and $X$ is NP-hard. The proof of correctness runs both ways but is not symmetric: "⇒" must handle **every** instance of $X$, while "⇐" only has to handle the special instances $y$ the reduction builds — whose structure (the gadgets) forces every solution of $y$ to come from a solution of $x$. Think of it as three algorithms: instance $x\mapsto y$ (polynomial time), certificate for $x$ $\mapsto$ certificate for $y$, and certificate for $y$ $\mapsto$ certificate for $x$. It is the same direction rule as for undecidability ([[concepts/undecidability-reductions]]), plus a time bound.

> [!template] Template — $Y$ is NP-hard (rubric: 1 problem + 2 sound + 2 correct + 2 "only if" + 2 "if" + 1 "polynomial time")
> We reduce from $X$, which is NP-hard. \
> **Reduction.** Given an arbitrary instance $x$ of $X$, build $y$: [every part of $y$ as an explicit function of $x$]. It has [size], so it is built in **polynomial time**. \
> **⇒.** If $x$ is YES with certificate [$c$], then [certificate for $y$], so $y$ is YES. \
> **⇐.** If the $y$ built above is YES with certificate [$c'$], then [certificate for $x$], so $x$ is YES. \
> Hence $Y$ is NP-hard. $\blacksquare$

> [!trap]
> - **Wrong direction:** at most 1 point of 10. "I can solve $Y$ with a SAT solver" proves nothing.
> - **Not an arbitrary instance:** the reduction gets $x$ and nothing else — no satisfying assignment, no knowledge of the answer — and must work for every $x$, including degenerate ones (isolated vertices, repeated literals, $k$ larger than $n$).
> - **Only "⇒" proved:** the "⇐" direction, about the built instance, is worth as much and catches most wrong constructions.
> - **Exponential blow-up:** distributing a CNF formula into DNF, or listing all subsets, is not polynomial time. Numbers count by their bits.

**Example — IndependentSet → Clique.** *Reduction:* given an arbitrary graph $G = (V,E)$ and integer $k$, output the complement $\overline G$ (same vertices, exactly the non-edges of $G$) and the same $k$; $O(V^2)$ time. *⇒:* an independent set $S$ of $G$ has no edges of $G$ inside, so every pair in $S$ is an edge of $\overline G$: $S$ is a clique of $\overline G$. *⇐:* a clique of $\overline G$ has no edge of $G$ inside, so it is independent in $G$. On the 5-cycle $C = 0\,1\,2\,3\,4$, the complement is the 5-cycle $0\,2\,4\,1\,3$; $\{0, 2\}$ is independent in $C$ and a clique in $\overline C$, and both maxima are 2.

**Where it appears.** [[2-algorithms/12-np-hardness#124-formal-definitions|§12.4]] (Cook versus Karp), [[2-algorithms/12-np-hardness#125-reductions-and-sat|§12.5]] (the direction rule, CircuitSat → Sat), [[2-algorithms/12-np-hardness#128-the-general-pattern|§12.8]] (the general pattern and template), [[2-algorithms/12-np-hardness#1214-choosing-the-right-problem|§12.14]] (choosing $X$), [[0-toolkit/06-how-exams-are-graded#14-np-hardness|the NP-hardness rubric]]; every reduction of [[2-algorithms/12-np-hardness|Chapter 12]] is an instance.

Related: [[concepts/np-hardness]] · [[concepts/satisfiability]] · [[concepts/independent-set]] · [[concepts/graph-coloring]] · [[concepts/hamiltonian-cycle]] · [[concepts/undecidability-reductions]] · [[concepts/graph-reductions]]
