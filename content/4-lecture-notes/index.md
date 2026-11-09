---
title: "Part 3 · Beyond the book"
description: "Jeff Erickson's lecture notes that are not in his two textbooks — randomized algorithms, hashing, amortized analysis, lower bounds, the induction and recurrences appendices, FFT, faster dynamic programming, matroids, min-cost flows, linear programming and approximation algorithms — one checked info page per note, with errors in the notes corrected."
tags: [lecture-notes, algorithms]
---

Erickson's [course page](https://jeffe.cs.illinois.edu/teaching/algorithms/) has more than the two books: thirteen **Director's Cut** notes on topics the *Algorithms* book leaves out (mostly randomized algorithms and data structures), two **appendices** on proof by induction and solving recurrences, and ten **Extended Dance Remix** notes on more advanced material. This part summarizes each of them on one page, the way Parts 1 and 2 summarize the chapters: definitions, algorithms with running times, the key lemmas with their proof ideas, and links back to the chapters they build on.

> [!warning] Rougher sources
> Erickson says these notes are much less polished than the textbook, and several carry a status line (“Beta”, “Unfinished”, “Needs significant revision or deletion”). Every algorithm, formula and example on these pages was checked by script (results the notes only cite from the literature are marked as such); where a note is wrong, the page says so and gives the correction, and every error is listed in the page's sources. Unfinished parts are summarized as unfinished, never completed by guesswork.

> [!exam] For CS 374
> None of these notes is assigned reading in CS/ECE 374 A this semester; most are CS 473 material at Illinois. Worth reading anyway: **[[4-lecture-notes/99-solving-recurrences|Solving recurrences]]** (Midterm 2 always opens with recurrences) and **[[4-lecture-notes/98-proof-by-induction|Proof by induction]]** (every induction proof in the course); **[[4-lecture-notes/c-dynamic-programming-for-automata|C]]**, which joins the two halves of the course (NFA acceptance and CFG parsing as dynamic programs); **[[4-lecture-notes/12-lower-bounds|Lower bounds]]** (why sorting needs $\Omega(n\log n)$ comparisons); and **[[4-lecture-notes/j-approximation-algorithms|J]]**, what to do after proving a problem NP-hard.

## Appendices

| note | page | about | pp. |
|---|---|---|---|
| I | [[4-lecture-notes/98-proof-by-induction\|Proof by induction]] | smallest counterexamples, strong induction and its boilerplate, induction on everything | 30 |
| II | [[4-lecture-notes/99-solving-recurrences\|Solving recurrences]] | guess and confirm, recursion trees, annihilators, transformations | 22 |

## Director's Cut

| # | page | about | pp. |
|---|---|---|---|
| 1 | [[4-lecture-notes/01-discrete-probability\|Discrete probability]] | probability spaces, random variables, expectation, coin flips, coupon collecting, random permutations | 22 |
| 2 | [[4-lecture-notes/02-nuts-and-bolts\|Nuts and bolts]] | randomized matching of nuts and bolts — quicksort in disguise — and three ways to analyze it | 13 |
| 3 | [[4-lecture-notes/03-treaps-and-skip-lists\|Treaps and skip lists]] | randomized balanced search trees and their expected costs | 14 |
| 4 | [[4-lecture-notes/04-tail-inequalities\|Tail inequalities]] | Markov, Chebyshev and Chernoff; treap depth with high probability | 10 |
| 5 | [[4-lecture-notes/05-hashing\|Hash tables]] | universal hashing, chaining, multiplicative hashing, balls and bins, perfect hashing, linear and binary probing (cuckoo hashing is only a placeholder in the note) | 19 |
| 6 | [[4-lecture-notes/06-filtering-and-streaming\|Filtering and streaming]] | Bloom filters, the count-min sketch, counting distinct items | 6 |
| 7 | [[4-lecture-notes/07-string-matching\|String matching]] | Karp–Rabin fingerprints and Knuth–Morris–Pratt's automaton | 14 |
| 8 | [[4-lecture-notes/08-randomized-minimum-cut\|Randomized minimum cut]] | edge contraction, Karger and Karger–Stein | 7 |
| 9 | [[4-lecture-notes/09-amortized-analysis\|Amortized analysis]] | aggregate, accounting and potential arguments: counters and Gray codes | 14 |
| 10 | [[4-lecture-notes/10-scapegoat-and-splay-trees\|Scapegoat and splay trees]] | balance by rebuilding and by splaying, with amortized bounds | 15 |
| 11 | [[4-lecture-notes/11-disjoint-sets\|Disjoint sets]] | union-find: union by rank, path compression, $\log^*$ and inverse Ackermann | 14 |
| 12 | [[4-lecture-notes/12-lower-bounds\|Lower bounds]] | decision trees and the information-theoretic bound | 6 |
| 13 | [[4-lecture-notes/13-adversary-arguments\|Adversary arguments]] | adversaries, evasive graph properties, minimum and maximum, the median | 8 |

## Extended Dance Remix

| note | page | about | pp. |
|---|---|---|---|
| A | [[4-lecture-notes/a-fast-fourier-transforms\|Fast Fourier transforms]] | polynomial representations, the DFT and the FFT, fast polynomial multiplication | 17 |
| B | [[4-lecture-notes/b-fast-exponential-algorithms\|Faster exponential algorithms]] | faster-than-brute-force exact algorithms for 3SAT and maximum independent set | 14 |
| C | [[4-lecture-notes/c-dynamic-programming-for-automata\|Dynamic programming for formal languages and automata]] | NFA acceptance and CFG parsing (CYK) as dynamic programs; its DFA-minimization and regular-expression sections are unwritten | 7 |
| D | [[4-lecture-notes/d-advanced-dynamic-programming\|Advanced dynamic programming]] | saving space by divide and conquer; saving time by sparseness, monotonicity, SMAWK, Four Russians | 18 |
| E | [[4-lecture-notes/e-matroids\|Matroids]] | the structures on which the greedy algorithm is always optimal | 8 |
| F | [[4-lecture-notes/f-balances-and-pseudoflows\|Balances and pseudoflows]] | flows with supplies and demands, pseudoflows, push-relabel | 12 |
| G | [[4-lecture-notes/g-minimum-cost-flows\|Minimum-cost flows]] | cycle cancelling, successive shortest paths, potentials, transportation | 15 |
| H | [[4-lecture-notes/h-linear-programming\|Linear programming]] | geometry, examples, duality, complementary slackness | 21 |
| I | [[4-lecture-notes/i-linear-programming-algorithms\|Linear programming algorithms]] | the simplex method, initial bases, network simplex, Seidel's algorithm | 15 |
| J | [[4-lecture-notes/j-approximation-algorithms\|Approximation algorithms]] | load balancing, vertex cover, set cover, TSP, approximation schemes | 25 |

**Concepts for this part:** [[concepts/discrete-probability]] · [[concepts/treaps]] · [[concepts/tail-inequalities]] · [[concepts/hashing]] · [[concepts/bloom-filters]] · [[concepts/string-matching]] · [[concepts/randomized-minimum-cut]] · [[concepts/amortized-analysis]] · [[concepts/splay-trees]] · [[concepts/comparison-lower-bounds]] · [[concepts/adversary-arguments]] · [[concepts/strong-induction]] · [[concepts/linear-recurrences]] · [[concepts/fast-fourier-transform]] · [[concepts/cyk-algorithm]] · [[concepts/matroids]] · [[concepts/minimum-cost-flow]] · [[concepts/linear-programming]] · [[concepts/simplex-algorithm]] · [[concepts/approximation-algorithms]] — and, from Part 2, [[concepts/union-find]], [[concepts/master-theorem]] and [[concepts/recursion-trees]].

### Sources for this page
Jeff Erickson's lecture notes, [jeffe.cs.illinois.edu/teaching/algorithms](https://jeffe.cs.illinois.edu/teaching/algorithms/), © 2018 Jeff Erickson, licensed CC BY-NC-SA 4.0 — summarized in our own words; each page links its PDF and lists the errors found in it. Page counts are those of the PDFs.
