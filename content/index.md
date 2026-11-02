---
title: "CS/ECE 374 · Algorithms & Models of Computation"
description: "Review and reference notes for CS/ECE 374 A (Fall 2026, Illinois): Jeff Erickson's Models of Computation chapter by chapter, a concept glossary, proof templates, exam reviews, worked exam-style problems and a practice bank with folded hints and solutions — every automaton, grammar and Turing machine machine-checked. The Algorithms half covers all of Erickson's Algorithms (recursion, backtracking, dynamic programming, greedy algorithms, graph search, depth-first search, minimum spanning trees, shortest paths, maximum flows and NP-hardness) with solved book exercises, plus a Midterm 2 review."
---

Notes for **CS/ECE 374 A — Algorithms and Models of Computation** (University of Illinois, Fall 2026), written for *review*: the week before an exam, or when a homework problem needs the exact definition. They follow Jeff Erickson's two textbooks section by section — *Models of Computation* for Part 1 and *Algorithms* for Part 2 — with the books' theorem numbers. They are **not a replacement for the books** — [read them](https://jeffe.cs.illinois.edu/teaching/algorithms/); come here to look things up, to review, and to practice.

> [!tip] How this site is organized
> - **Chapters** (the spine, in book order) — one page per chapter with the book's section numbers: definitions, numbered results, the exam templates, worked examples, traps, and an "On the exams" box. Each links its chapter PDF.
> - **Concepts** are the glossary: one short page per idea (fooling sets, the subset construction, Rice's theorem, …) with the precise statement, how to use it, the traps, and links to every section that develops it.
> - **Toolkit** pages collect what is spread over the chapters: notation, every proof template on one page, the big picture of language classes, three exam reviews (including Midterm 2), how exams are graded, and errata in the book.
> - **Worked problems** are exam-style problems solved in full as model answers; the **practice bank** is where you do the work yourself — 60 problems tagged easy, medium or hard, each with a folded hint and a worked solution. In Part 2, each chapter instead has a page of **solved book exercises**.
> - **Homework and exams** holds the course's own material worked out: the Midterm 1 practice tests, the labs and the homework write-ups.
>
> Hover a link for a preview, and use the **graph view** at the top right of any page to see what connects to what.

## Course map

### [[0-toolkit/index|Toolkit]] — reference pages
[[0-toolkit/01-notation-and-conventions|Notation and conventions]] · **[[0-toolkit/02-proof-templates|Proof templates]]** · [[0-toolkit/03-the-big-picture|The big picture]] · **[[0-toolkit/04-review-regular-and-context-free|Review: Ch 1–5]]** · **[[0-toolkit/05-review-turing-machines-and-undecidability|Review: Ch 6–9]]** · **[[0-toolkit/08-review-algorithms|Review: Midterm 2 (algorithms)]]** · [[0-toolkit/06-how-exams-are-graded|How exams are graded]] · [[0-toolkit/07-errata-in-the-book|Errata in the books]]

### [[1-models-of-computation/index|Part 1 · Models of Computation]] — Chapters 1–9 <span class="cs-chip done">complete</span>
Midterm 1 (Sep 28) covered Chapters 1–5; the final covers all nine.

1. [[1-models-of-computation/01-strings|Strings]] — recursive definitions and induction on strings
2. [[1-models-of-computation/02-regular-languages|Regular languages]] — language operations, regular expressions, structural induction
3. [[1-models-of-computation/03-finite-state-machines|Finite-state machines]] — DFAs, the product construction, fooling sets, Myhill–Nerode, minimization
4. [[1-models-of-computation/04-nondeterministic-automata|Nondeterministic automata]] — NFAs, the subset construction, Thompson, state elimination, Kleene's theorem, transformations
5. [[1-models-of-computation/05-context-free-languages|Context-free languages]] — grammars, ambiguity, proving $L(G) = L$, recursive automata, Chomsky normal form
6. [[1-models-of-computation/06-turing-machines|Turing machines]] — the formal model, variants and their costs, the universal machine
7. [[1-models-of-computation/07-undecidability|Undecidability]] — diagonalization, the halting problem, reductions, Rice's theorem
8. [[1-models-of-computation/08-universal-models|Universal models]] — two stacks, counters, FRACTRAN, Post's correspondence problem, tiles, combinators
9. [[1-models-of-computation/09-nondeterministic-turing-machines|Nondeterministic Turing machines]] — computation trees, dovetailing, P and NP, Cook–Levin

### [[2-algorithms/index|Part 2 · Algorithms]] — Chapters 1–12 <span class="cs-chip done">complete</span>
**Midterm 2 (Mon Nov 9, 7–9 pm)** covers Homeworks 5–9: recursion, divide and conquer, backtracking, dynamic programming, graph search, depth-first search, topological sort and shortest paths (Chapters 1–3, 5, 6, 8, plus Floyd–Warshall's interface from 9) — start from **[[0-toolkit/08-review-algorithms|the Midterm 2 review]]**. The final covers both parts. Each chapter has a page of solved book exercises.

1. [[2-algorithms/01-recursion|Recursion]] — Hanoi, mergesort, quicksort, recursion trees, median-of-medians, Karatsuba · [[2-algorithms/01-recursion-exercises|exercises]]
2. [[2-algorithms/02-backtracking|Backtracking]] — n queens, game trees, subset sum, text segmentation, LIS, optimal BSTs · [[2-algorithms/02-backtracking-exercises|exercises]]
3. [[2-algorithms/03-dynamic-programming|Dynamic programming]] — memoization, the write-up format, LIS, edit distance, subset sum, optimal BSTs, trees · [[2-algorithms/03-dynamic-programming-exercises|exercises]]
4. [[2-algorithms/04-greedy-algorithms|Greedy algorithms]] — exchange arguments, class scheduling, Huffman codes, stable matching · [[2-algorithms/04-greedy-algorithms-exercises|exercises]]
5. [[2-algorithms/05-basic-graph-algorithms|Basic graph algorithms]] — representations, whatever-first search, BFS and DFS as variants, graph reductions · [[2-algorithms/05-basic-graph-algorithms-exercises|exercises]]
6. [[2-algorithms/06-depth-first-search|Depth-first search]] — pre/postorder, edge classification, topological sort, DP on dags, strong components · [[2-algorithms/06-depth-first-search-exercises|exercises]]
7. [[2-algorithms/07-minimum-spanning-trees|Minimum spanning trees]] — safe edges, Borůvka, Jarník (Prim), Kruskal, union-find · [[2-algorithms/07-minimum-spanning-trees-exercises|exercises]]
8. [[2-algorithms/08-shortest-paths|Shortest paths]] — relaxation, BFS, dags, Dijkstra, Bellman–Ford, which algorithm when · [[2-algorithms/08-shortest-paths-exercises|exercises]]
9. [[2-algorithms/09-all-pairs-shortest-paths|All-pairs shortest paths]] — Johnson, min-plus products, Floyd–Warshall · [[2-algorithms/09-all-pairs-shortest-paths-exercises|exercises]]

10. [[2-algorithms/10-maximum-flows-and-minimum-cuts|Maximum flows and minimum cuts]] — cuts, residual graphs, maxflow-mincut, Ford–Fulkerson, Edmonds–Karp (not part of CS 374 this semester) · [[2-algorithms/10-maximum-flows-and-minimum-cuts-exercises|exercises]]
11. [[2-algorithms/11-applications-of-flows-and-cuts|Applications of flows and cuts]] — disjoint paths, bipartite matching, scheduling, baseball elimination, project selection (not part of CS 374 this semester) · [[2-algorithms/11-applications-of-flows-and-cuts-exercises|exercises]]
12. [[2-algorithms/12-np-hardness|NP-hardness]] — P vs NP, reductions, SAT and 3SAT, independent set, coloring, Hamiltonian cycle, subset sum (on the final) · [[2-algorithms/12-np-hardness-exercises|exercises]]

Solving recurrences: [[concepts/recursion-trees|recursion trees]] and the [[concepts/master-theorem|master theorem]].

### [[3-homework-and-exams/index|Homework and exams]] — worked solutions
The three Midterm 1 practice tests solved in full in the exam's format — [[3-homework-and-exams/midterm-1-practice-1|test 1]] · [[3-homework-and-exams/midterm-1-practice-2|test 2]] · [[3-homework-and-exams/midterm-1-practice-3|test 3]] — the labs from 6a on, each problem explained — [[3-homework-and-exams/lab-06a|6a]] · [[3-homework-and-exams/lab-06b|6b]] · [[3-homework-and-exams/lab-07a|7a]] · [[3-homework-and-exams/lab-07b|7b]] · [[3-homework-and-exams/lab-08a|8a]] · [[3-homework-and-exams/lab-08b|8b]] · [[3-homework-and-exams/lab-09a|9a]] · [[3-homework-and-exams/lab-09b|9b]] · [[3-homework-and-exams/lab-10a|10a]] · [[3-homework-and-exams/lab-10b|10b]] — and homework write-ups that explain the method as they solve the problems: [[3-homework-and-exams/hw6-dynamic-programming|HW6, dynamic programming]] · [[3-homework-and-exams/hw7-dynamic-programming|HW7, more dynamic programming]].

### [[practice/index|Practice problems]] — Models of Computation, Chapters 1–7
Sixty problems, from two-minute true-or-false checks to full exam problems, each with a folded hint and a worked solution: by difficulty — [[practice/easy|easy]] · [[practice/medium|medium]] · [[practice/hard|hard]] — or [[practice/topics|by topic]] across chapters. Every chapter page links its own set.

### Cross-cutting
[[concepts/index|Concept glossary]] · [[problems/index|Worked problems]] · [[practice/index|Practice problems]] · [[3-homework-and-exams/index|Homework and exams]]

## Conventions used throughout

| | this site writes | for example |
|---|---|---|
| explicit symbols and strings | typewriter: $\mathtt{0}$, $\mathtt{1}$, `0110` | $\mathtt{0}^n\mathtt{1}^n$, $(\mathtt{0}+\mathtt{1})^*\mathtt{00}$ |
| variables | $a, b, c$ for symbols; $w, x, y, z$ for strings | $w = ax$ |
| empty string, empty language | $\varepsilon$ (a string), $\varnothing$ (a language) — and $\{\varepsilon\}$ is a third, different object | $\varnothing^* = \{\varepsilon\}$ |
| regular expressions | $+$ for union, juxtaposition, $^*$; star binds tightest | $\mathtt{10}^* = \mathtt{1}(\mathtt{0}^*)$ |
| automata | $M = (\Sigma, Q, s, A, \delta)$, extended to strings as $\delta^*$ | $M$ accepts $w$ iff $\delta^*(s,w)\in A$ |
| grammars | $A\to w$, one step $\rightsquigarrow$, many steps $\rightsquigarrow^*$ | $S\rightsquigarrow\mathtt{0}S\mathtt{1}\rightsquigarrow\mathtt{01}$ |
| machines as input | encodings $\langle M\rangle$, $\langle M, w\rangle$ | $\textsf{Halt} = \{\langle M,w\rangle \mid M \text{ halts on } w\}$ |
| named languages | sans-serif | $\textsf{SelfReject}$, $\textsf{Accept}(M)$, $\textsf{half}(L)$ |

The full list, with the book's notation and the other names you will meet (acceptable = recognizable = semi-decidable = recursively enumerable, …), is on [[0-toolkit/01-notation-and-conventions|notation and conventions]].

## Callouts

The pages use a few recurring boxes, so you can skim for what you need:

> [!definition] Definition
> A formal definition — DFA, grammar, Turing machine, fooling set.

> [!key] Lemma or theorem
> A result, numbered as in the book: Lemma 3.6, Theorem 4.1 (Kleene), Rice's theorem.

> [!template] Template
> Proof boilerplate to copy onto the exam, word for word, then fill in.

> [!recipe] Recipe
> A construction or algorithm, step by step.

> [!trap] Trap
> A mistake that costs points, and how to avoid it.

> [!exam] On the exams
> How the idea shows up on exams and how the rubric grades it.

> [!intuition] Intuition
> The picture behind the formalism.

> [!proof]- Proof (click to expand)
> Proofs are folded so the page stays readable. Expand when you want the details.

The [[practice/index|practice pages]] add their own five: the problem statement sits in an **easy**, **medium** or **hard** box (the difficulty, followed by topic tags), and the **hint** and **solution** below it stay folded until you click them.

## How the examples were checked

Every concrete example on the site — each regular expression, DFA, NFA, grammar, Turing machine, run trace, state count and fooling-set suffix — is checked by a script against a brute-force definition of its language (all strings up to length 10–14, and exactly by automaton equivalence wherever the language is regular); constructions such as language transformations are tested on hundreds of random DFAs. In Part 2, every algorithm and recurrence is implemented exactly as the page states it and compared with brute force on all small inputs, and every running-time claim is checked numerically. Each chapter page, concept page and worked problem was then reviewed independently against the book. The scripts are in the repository's `tools/` folder, and the slips found in the book along the way are on [[0-toolkit/07-errata-in-the-book|errata in the book]].

*Status: Part 1 (Models of Computation) is complete — 9 chapter pages, 32 concept pages, 11 worked problems and 60 practice problems. Part 2 (Algorithms) is complete — 12 chapter pages, 43 concept pages and 140 solved book exercises — with a Midterm 2 review among the 8 toolkit pages, and the course's Midterm 1 practice tests, labs 6a–10b and HW6–7 worked out. Sources: Jeff Erickson, [Models of Computation](https://jeffe.cs.illinois.edu/teaching/algorithms/models/all-models.pdf) (December 2018), licensed CC BY-NC-SA 4.0, and [Algorithms](https://jeffe.cs.illinois.edu/teaching/algorithms/book/Algorithms-JeffE.pdf) (1st edition, 2019), licensed CC BY 4.0 — summarized here in our own words.*
