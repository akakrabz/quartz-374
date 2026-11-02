---
title: "Satisfiability (SAT, CircuitSat, 3SAT)"
description: "Circuit and formula satisfiability, CNF and 3CNF, and the reductions CircuitSat → Sat and CircuitSat → 3Sat (Tseitin: one variable per wire, one small CNF per gate, padding to three literals) that make 3SAT the standard starting point for NP-hardness proofs."
tags: [concept, algorithms, complexity]
aliases: ["SAT", "3SAT", "CircuitSat", "circuit satisfiability", "CNF", "3CNF", "conjunctive normal form"]
---

> [!definition] Definitions (§12.1, §12.5, §12.6)
> - **CircuitSat:** given a boolean circuit of And, Or and Not gates, is there an input that makes the output True?
> - **Sat:** given a boolean formula, is there an assignment of True/False to its variables that makes it True?
> - A **CNF** formula is an And of **clauses**, each an Or of **literals** (variables or negated variables); in a **3CNF** formula every clause has exactly three literals. **3Sat:** is a given 3CNF formula satisfiable?
>
> All three are **NP-complete**: a satisfying input or assignment is a certificate, and CircuitSat is NP-hard by the Cook–Levin theorem.

**Why they are hard, in a chain.** **CircuitSat → Sat:** name every interior wire $y_j$ and the output $z$, and write one equation per gate, "$y_j$ = the gate applied to its inputs", joined by And, plus $\land\, z$; the formula is satisfiable iff the circuit is. **CircuitSat → 3Sat** (Tseitin): make every gate binary, then replace each equation by its CNF and pad short clauses with new variables:
$$
\begin{aligned}
a = b\land c &\mapsto (a\lor\bar b\lor\bar c)(\bar a\lor b)(\bar a\lor c), & (a\lor b) &\mapsto (a\lor b\lor x)(a\lor b\lor\bar x),\\
a = b\lor c &\mapsto (\bar a\lor b\lor c)(a\lor\bar b)(a\lor\bar c), & (z) &\mapsto (z\lor x\lor y)(z\lor\bar x\lor y)\\
a = \bar b &\mapsto (a\lor b)(\bar a\lor\bar b), & &\quad\ (z\lor x\lor\bar y)(z\lor\bar x\lor\bar y).
\end{aligned}
$$
At most 5 clauses per binary gate: linear size. The new variables are what keep it small — distributing $\lor$ over $\land$ can be exponential.

> [!recipe] Recipe — reducing from 3Sat
> 3Sat is the default source problem ([[2-algorithms/12-np-hardness#1214-choosing-the-right-problem|§12.14]]). Given an arbitrary 3CNF formula with $n$ variables and $k$ clauses, build a **variable gadget** for each variable — something with exactly two "states", True and False — and a **clause gadget** for each clause that can be completed exactly when one of its three literals is True; wire them consistently. Then prove ⇒ (satisfying assignment ↦ solution) and ⇐ (solution of the *built* instance ↦ satisfying assignment). Models: [[concepts/independent-set|independent set]] (triangles), [[concepts/graph-coloring|3-coloring]] (majority gates), [[concepts/hamiltonian-cycle|Hamiltonian cycle]] (rows and detours).

> [!trap]
> - **Direction:** reducing a new problem *to* Sat (encoding it as a formula) shows only that it is no harder than Sat, not that it is hard.
> - **3CNF means exactly three literals per clause**; pad with new variables.
> - **2Sat is in P**: hardness needs clauses of size 3 (or the optimization version, Max2Sat).
> - **Equisatisfiable, not equivalent:** the Tseitin formula has extra variables; what is preserved is satisfiability, with certificates translated both ways.

**Example.** The one-gate circuit $z = x_1\lor x_2$ gives $\Phi_2 = (\bar z\lor x_1\lor x_2)(z\lor\bar x_1)(z\lor\bar x_2)(z)$ and, after padding, a 3CNF formula with $1 + 2 + 2 + 4 = 9$ clauses on 7 variables. Exactly 48 of its 128 assignments satisfy it: $z$ must be True and $(x_1, x_2)$ one of the 3 satisfying inputs, while the 4 padding variables are free ($3\cdot 2^4 = 48$). By contrast, $(x\lor y)(\bar x\lor y)(x\lor\bar y)(\bar x\lor\bar y)$ is unsatisfiable, and dropping any one clause makes it satisfiable.

**Where it appears.** [[2-algorithms/12-np-hardness#121-a-game-you-cant-win|§12.1]] (CircuitSat), [[2-algorithms/12-np-hardness#125-reductions-and-sat|§12.5]] (Sat from CircuitSat), [[2-algorithms/12-np-hardness#126-3sat-from-circuitsat|§12.6]] (3Sat from CircuitSat, the book's 46-clause example), [[2-algorithms/12-np-hardness#1213-other-useful-np-hard-problems|§12.13]] (1-in-3Sat, NotAllEqual3Sat, Planar3Sat, Max2Sat); Part 1: [[1-models-of-computation/09-nondeterministic-turing-machines#96-the-cooklevin-theorem|§9.6]] (the formula $\Phi_w$ of Cook–Levin).

Related: [[concepts/cook-levin-theorem]] · [[concepts/np-hardness]] · [[concepts/polynomial-time-reductions]] · [[concepts/independent-set]] · [[concepts/graph-coloring]] · [[concepts/hamiltonian-cycle]]
