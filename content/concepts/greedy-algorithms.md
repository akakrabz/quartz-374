---
title: "Greedy algorithms"
description: "Algorithms that commit to one locally best choice and recurse on what is left: fast, usually wrong, and correct only with a proof — normally an inductive exchange argument, whose write-up template and classic pitfalls are collected here."
tags: [concept, algorithms, greedy, midterm-2]
aliases: ["greedy algorithm", "exchange argument", "inductive exchange argument", "greedy choice"]
---

> [!definition] Definition — greedy algorithm, exchange argument
> A **greedy algorithm** builds a solution by a sequence of choices, making each one by a fixed local rule (shortest first, earliest finish first, two least frequent first, …) **without** solving subproblems to compare the alternatives, and never revisiting it. It is correct only if it comes with a proof, usually an **inductive exchange argument**:
> 1. **Exchange lemma:** some optimal solution makes the greedy first choice $g$ — take any optimal solution, replace the element that plays $g$'s role by $g$, and show that the result is still feasible and no worse;
> 2. **Same problem, smaller:** after choosing $g$, what is left is a smaller instance of the same problem, and $g$ plus an optimal solution of it is optimal;
> 3. **Induction** (plus, if needed, a check that no optimal solution has more elements than the greedy one).

**Why it works.** Backtracking tries every option for the first decision and recurses on each. The exchange lemma proves that one particular option — the greedy one — always leads to an optimal solution, so the other branches can be skipped and the recursion tree collapses to a single path. That is why greedy algorithms are fast (typically a sort or a priority queue, $O(n\log n)$), and why skipping the proof is never safe: without the lemma, the discarded branches may hold the only optimal solutions.

> [!template] Template — proving a greedy algorithm correct
> **Greedy choice.** "Let $g$ be [the precise rule, with ties]." \
> **Exchange lemma.** "Let $\mathit{OPT}$ be an optimal solution without $g$, and $o$ the element of $\mathit{OPT}$ in $g$'s role. $\mathit{OPT} - o + g$ is feasible because [...] and no worse because [...]." \
> **Same problem, smaller.** "After $g$, the remaining instance is [...]; an optimal solution containing $g$ is $g$ plus an optimal solution of it." \
> **Induction.** "The algorithm chooses $g$ and then, by the induction hypothesis, solves the rest optimally." \
> **Running time.** Sorting or a heap: $O(n\log n)$.

> [!trap]
> - **No proof, no credit** — and inside a dynamic program an unproved greedy shortcut costs $1\tfrac12$ points.
> - **Testing the rule on examples is not a proof**; one counterexample is a disproof. Try the obvious rivals (earliest start vs earliest finish, shortest vs longest) on three or four items before trusting a rule.
> - **Exchanges must keep the solution feasible**: check the swapped-in element against everything that stays.
> - **Start from an arbitrary optimal solution**, not from the greedy one, and finish by ruling out an optimum with *more* elements.

**Example — knapsack by value per weight.** Capacity 10; items $a$ (weight 6, value 9), $b$ (5, 5), $c$ (5, 5). Greedy by value/weight takes $a$ (ratio 1.5) and then nothing fits: value 9, but $b + c$ is worth 10 — the rule fails for the 0/1 knapsack. If items may be taken **fractionally**, the same rule is optimal: $a$ plus $4/5$ of $b$ is worth 13, the maximum. Exchange argument: if an optimal load carries less of a denser item than it could while carrying some of a less dense one, moving weight $\varepsilon$ from the less dense item to the denser one changes the value by $\varepsilon$ times the difference of the ratios, which is $\ge 0$.

**Where it appears.** [[2-algorithms/03-dynamic-programming#35-warning-greed-is-stupid|§3.5]] (greed is stupid: segmentation and LIS counterexamples), [[2-algorithms/04-greedy-algorithms#41-storing-files-on-tape|§4.1]] (tape sorting, adjacent swaps), [[2-algorithms/04-greedy-algorithms#42-scheduling-classes|§4.2]] (earliest finish, rules that fail), [[2-algorithms/04-greedy-algorithms#43-the-general-pattern|§4.3]] (the pattern and the template), [[2-algorithms/04-greedy-algorithms#44-huffman-codes|§4.4]], [[2-algorithms/04-greedy-algorithms#45-stable-matching|§4.5]]; later in the book, minimum spanning trees (Chapter 7).

Related: [[concepts/interval-scheduling]] · [[concepts/huffman-codes]] · [[concepts/stable-matching]] · [[concepts/dynamic-programming]] · [[concepts/backtracking]]
