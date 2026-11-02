---
title: "NP-hardness"
description: "P, NP and co-NP; NP-hard, NP-easy and NP-complete; P versus NP; what an NP-hardness result does and does not say, how to prove one, and how to show membership in NP with a certificate."
tags: [concept, algorithms, complexity]
aliases: ["NP-hard", "NP-complete", "NP-completeness", "P versus NP", "P vs NP", "co-NP", "NP-easy"]
---

> [!definition] Definition (§12.2–12.3)
> For **decision problems** (answer YES or NO), with time measured in the number of **bits** of the input:
> - **P**: solvable in polynomial time.
> - **NP**: every YES instance has a **certificate** — a proof of YES — that can be checked in polynomial time.
> - **co-NP**: every NO instance has a certificate checkable in polynomial time.
>
> A problem $\Pi$ (decision or not) is **NP-hard** if a polynomial-time algorithm for $\Pi$ would imply $\textsf{P} = \textsf{NP}$ — formally (§12.4), every problem in NP reduces to $\Pi$ in polynomial time. It is **NP-complete** if it is NP-hard **and in NP** (the book also calls the second condition "NP-easy").
> $$
> \textsf{P}\subseteq\textsf{NP}\cap\textsf{co-NP},\qquad \textsf{P}\overset{?}{=}\textsf{NP},\qquad \textsf{NP}\overset{?}{=}\textsf{co-NP}.
> $$

**Why it matters.** Nobody has proved that any problem in NP needs super-polynomial time, but thousands of NP-complete problems are known, and a polynomial-time algorithm for any one of them would solve all of them. So "NP-hard" is the standard evidence that no efficient exact algorithm exists — evidence, not proof. The first NP-hard problem comes from the **Cook–Levin theorem** (circuit satisfiability, or formula satisfiability: [[concepts/cook-levin-theorem]]); every later one is proved NP-hard by a reduction *from* a problem already known to be NP-hard ([[concepts/polynomial-time-reductions]]).

> [!recipe] Recipe — classifying a new problem $Y$
> - **In P?** Give an algorithm, polynomial in the input *size* (an $O(nT)$ table is not polynomial when $T$ is a binary number).
> - **NP-hard?** Reduce a known NP-hard problem $X$ **to** $Y$: from an arbitrary instance of $X$, build an instance of $Y$ in polynomial time, YES ⟺ YES. Use the template of [[2-algorithms/12-np-hardness#128-the-general-pattern|§12.8]].
> - **In NP?** Describe the certificate (a satisfying assignment, a coloring, a tour, a subset) and say why it has polynomial size and is checked in polynomial time.
> - **NP-complete** = the last two together; on exams, +1 point for the membership part.

> [!trap]
> - **NP means nondeterministic polynomial**, not "not polynomial": every problem in P is in NP.
> - **NP-hard is not "in NP and hard".** Optimization problems and even undecidable problems are NP-hard without being in NP; the co-NP problem UnSat is NP-hard but in NP only if $\textsf{NP} = \textsf{co-NP}$.
> - **NP-hard does not mean "exponential time is proved"** — it means "polynomial time would prove $\textsf{P} = \textsf{NP}$".
> - **Special cases can be easy.** Independent set is NP-hard in general but linear-time in trees; 2Sat and 2Color are in P; subset sum is easy when the numbers are small (pseudo-polynomial).
> - **Membership needs a polynomial-size certificate**: "the list of all subsets" is not one.

**Example.** **3Color** is NP-complete. *In NP:* a coloring is the certificate; checking that the two ends of every edge differ takes $O(V+E)$ time. On the 5-cycle $0\,1\,2\,3\,4$, the coloring $0, 1, 0, 1, 2$ is proper, while no 2-coloring is (an odd cycle). *NP-hard:* by the reduction from 3Sat of [[2-algorithms/12-np-hardness#1210-graph-coloring-from-3sat|§12.10]]. So the general problem "what is the fewest colors?" is NP-hard too, although it is not a decision problem.

**Where it appears.** [[2-algorithms/12-np-hardness#122-p-versus-np|§12.2]] (P, NP, co-NP), [[2-algorithms/12-np-hardness#123-np-hard-np-easy-and-np-complete|§12.3]] (NP-hard, NP-complete, Cook–Levin), [[2-algorithms/12-np-hardness#124-formal-definitions|§12.4]] (languages, Cook and Karp reductions), [[2-algorithms/12-np-hardness#1212-subset-sum-from-vertex-cover|§12.12]] (weak and strong NP-hardness), [[2-algorithms/12-np-hardness#1216-on-beyond-zebra|§12.16]] (PSPACE, EXP and beyond); Part 1: [[1-models-of-computation/09-nondeterministic-turing-machines#93-time-and-space-complexity|§9.3]] and [[1-models-of-computation/09-nondeterministic-turing-machines#96-the-cooklevin-theorem|§9.6]].

Related: [[concepts/polynomial-time-reductions]] · [[concepts/cook-levin-theorem]] · [[concepts/satisfiability]] · [[concepts/independent-set]] · [[concepts/graph-coloring]] · [[concepts/hamiltonian-cycle]] · [[concepts/subset-sum]] · [[concepts/nondeterministic-turing-machines]]
