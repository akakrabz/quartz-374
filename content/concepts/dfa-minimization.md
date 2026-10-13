---
title: "DFA minimization"
description: "Moore's table-filling algorithm: mark the distinguishable pairs of states, pass after pass, until nothing changes, then merge what is left — the result is the unique smallest DFA for the language."
tags: [concept, regular, midterm-1]
aliases: ["Moore's algorithm", "table-filling algorithm", "minimal DFA"]
---

> [!definition] Definition — distinguishable and equivalent states
> States $p$ and $q$ of a DFA are **distinguishable** if some string $z$ leads exactly one of them to an accepting state: exactly one of $\delta^*(p,z)$ and $\delta^*(q,z)$ is in $A$. Otherwise they are **equivalent**. Recursively, $p$ and $q$ are distinguishable if exactly one of them is accepting, or if $\delta(p,a)$ and $\delta(q,a)$ are distinguishable for some symbol $a$.

**Why it works.** Moore's algorithm is dynamic programming on the length of a distinguishing string: after the initial marking and $k$ passes, every pair distinguished by a string of length at most $k$ is marked, and only distinguishable pairs are ever marked. Once a pass marks nothing, no later pass would either, so the unmarked pairs are equivalent. Equivalent states have equivalent successors, so merging them gives a well-defined DFA for the same language; by the [[concepts/myhill-nerode-theorem|Myhill–Nerode theorem]] its states are the classes of $\equiv_L$, so it is the smallest DFA, unique up to renaming.

> [!recipe] Moore's algorithm (table filling)
> 1. Delete the states that are unreachable from $s$.
> 2. Mark every pair $\{p,q\}$ with exactly one accepting state.
> 3. In passes, mark $\{p,q\}$ whenever $\{\delta(p,a),\delta(q,a)\}$ is already marked for some symbol $a$. Stop after a pass that marks nothing (at most $n$ passes, $O(\sigma n^3)$ time for $n$ states and $\sigma$ symbols; Hopcroft's algorithm needs only $O(\sigma n\log n)$).
> 4. Merge each group of mutually unmarked states; the merged state inherits the transitions and acceptance of its members.

> [!trap]
> - Step 1 matters: table filling never deletes a state, so unreachable states can survive as extra states. The brute-force design for "contains `11`" in §3.5 has 14 possible states, 4 of them unreachable.
> - Start from the accepting/non-accepting split, not from "edges that look different".
> - Keep making passes until one changes nothing; one pass is rarely enough.
> - The algorithm needs a real DFA: every transition present (keep the dump state) and no nondeterminism.
> - On exams, minimize only when asked: a larger DFA with clear state names earns full credit.

**Example.** Remembering a flag "seen `11`" and the last symbol gives a 5-state DFA for "contains `11`", with states $(\textsf{F},\varepsilon)$, $(\textsf{F},\mathtt{0})$, $(\textsf{F},\mathtt{1})$, $(\textsf{T},\mathtt{0})$, $(\textsf{T},\mathtt{1})$; the two $\textsf{T}$ states accept. Step 2 marks the 6 pairs between the groups. Pass 1 marks $\{(\textsf{F},\varepsilon),(\textsf{F},\mathtt{1})\}$ and $\{(\textsf{F},\mathtt{0}),(\textsf{F},\mathtt{1})\}$: reading `1` sends both to the marked pair $\{(\textsf{F},\mathtt{1}),(\textsf{T},\mathtt{1})\}$. Pass 2 marks nothing, because $(\textsf{F},\varepsilon), (\textsf{F},\mathtt{0})$ have identical successors, and so do $(\textsf{T},\mathtt{0}), (\textsf{T},\mathtt{1})$. Merging leaves the minimal 3-state DFA: "no `11`, last symbol not `1`", "no `11`, last symbol `1`" and "seen `11`".

**Where it appears.** [[1-models-of-computation/03-finite-state-machines#310-minimal-automata-moores-algorithm|§3.10]] (the algorithm and its running time), [[1-models-of-computation/03-finite-state-machines#39-the-myhillnerode-theorem|§3.9]] (why the result is the smallest), [[1-models-of-computation/03-finite-state-machines#35-designing-dfas-dfas-are-algorithms|§3.5]] (brute-force designs, and why clarity beats minimality), [[1-models-of-computation/04-nondeterministic-automata#47-another-example|§4.7]] (a 9-state subset-construction DFA that minimizes to 4 states).

**Practice.** [[practice/topics#myhillnerode-and-minimal-dfas|Myhill–Nerode and minimal DFAs]] (2 problems) — for example [[practice/03-finite-state-machines#33-prefixes-of-a-pattern|3.3 Prefixes of a pattern]] (easy), [[practice/03-finite-state-machines#310-shrink-it-then-prove-it-minimal|3.10 Shrink it, then prove it minimal]] (hard).

Related: [[concepts/myhill-nerode-theorem]] · [[concepts/dfa]] · [[concepts/fooling-sets]] · [[concepts/subset-construction]] · [[concepts/product-construction]]
