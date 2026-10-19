---
title: "Part 2 · Algorithms"
description: "Jeff Erickson's Algorithms, chapter by chapter, for review after reading the book: recursion and divide and conquer, backtracking, and dynamic programming so far — each with its algorithms, recurrences, running times, the rubric's write-up format, and solved book exercises. Later chapters to follow."
tags: [algorithms, recursion, backtracking, dynamic-programming, midterm-2]
---

A review of Jeff Erickson's [*Algorithms*](https://jeffe.cs.illinois.edu/teaching/algorithms/) for someone who has **already read it**: the algorithms with their recurrences and running times, the proof ideas, the patterns to reuse, the exam write-up format, and the traps. The first three chapters build one idea in three steps. **Recursion** solves a problem by trusting the recursive call on smaller instances (Ch 1), and recursion trees turn its running time into a sum. **Backtracking** is recursion over a sequence of decisions — try every choice for the next one (Ch 2) — and it is exponential because the same subproblems come back again and again. **Dynamic programming** keeps the backtracking recurrence and stores each subproblem's answer in an array (Ch 3), which turns exponential into polynomial time.

Midterm 2 (algorithms) is on Monday, November 9, 7–9 pm; the final (everything) on Friday, December 11. Every chapter page follows the book's sections, links the chapter PDF, writes each algorithm in the format its rubric grades, and ends with a summary and an "On the exams" box. Each chapter has a page of **solved book exercises** — the easier ones, roughly the first ten; hard (♥) problems are skipped.

| # | page | one line | exercises |
|---|---|---|---|
| 1 | [[2-algorithms/01-recursion\|Recursion]] | reductions and the Recursion Fairy; Tower of Hanoi; mergesort and quicksort; the divide-and-conquer pattern; recursion trees and their three cases; median-of-medians selection; Karatsuba multiplication; repeated squaring | [[2-algorithms/01-recursion-exercises\|13 solved]] |
| 2 | [[2-algorithms/02-backtracking\|Backtracking]] | n queens; game trees; subset sum; the general pattern (what a call must remember); text segmentation; two recursions for the longest increasing subsequence; optimal binary search trees | [[2-algorithms/02-backtracking-exercises\|6 solved]] |
| 3 | [[2-algorithms/03-dynamic-programming\|Dynamic programming]] | Fibonacci from exponential to linear; memoization and deliberate table filling; the smart-recursion recipe and write-up format; greed is stupid; LIS, edit distance, subset sum, optimal BSTs, independent sets in trees | [[2-algorithms/03-dynamic-programming-exercises\|10 solved]] |

**How each kind of answer is graded:** [[0-toolkit/06-how-exams-are-graded#11-recursive-algorithms|recursive algorithms]] (divide and conquer and backtracking) · [[0-toolkit/06-how-exams-are-graded#12-dynamic-programming|dynamic programming]] · the write-up templates: [[0-toolkit/02-proof-templates#18-writing-up-a-divide-and-conquer-algorithm|divide and conquer]], [[0-toolkit/02-proof-templates#19-writing-up-a-backtracking-algorithm|backtracking]], [[0-toolkit/02-proof-templates#20-writing-up-a-dynamic-program|dynamic programming]].

**Concepts for this part:** [[concepts/recursion]] · [[concepts/divide-and-conquer]] · [[concepts/recursion-trees]] · [[concepts/linear-time-selection]] · [[concepts/backtracking]] · [[concepts/subset-sum]] · [[concepts/longest-increasing-subsequence]] · [[concepts/dynamic-programming]] · [[concepts/memoization]] · [[concepts/edit-distance]] · [[concepts/optimal-binary-search-trees]] · [[concepts/dynamic-programming-on-trees]]

### Still to come

<span class="cs-chip">planned</span> The rest of the book, in order: 4 Greedy algorithms · 5 Basic graph algorithms · 6 Depth-first search · 7 Minimum spanning trees · 8 Shortest paths · 9 All-pairs shortest paths · 10 Maximum flows and minimum cuts · 11 Applications of flows and cuts · 12 NP-hardness. Which of them the course covers, and in what order, is on the course website. Already on this site and used again later: the [[concepts/cook-levin-theorem|Cook–Levin theorem]] and P versus NP in [[1-models-of-computation/09-nondeterministic-turing-machines#96-the-cooklevin-theorem|§9.6]], the starting point for NP-hardness, and [[concepts/undecidability-reductions|reductions]], whose direction rule is the same for NP-hardness.

**The book:** Jeff Erickson, *Algorithms*, 1st edition (2019), free under CC BY 4.0 — [whole book (PDF)](https://jeffe.cs.illinois.edu/teaching/algorithms/book/Algorithms-JeffE.pdf) · [chapter PDFs](https://jeffe.cs.illinois.edu/teaching/algorithms/). Each chapter page links its own PDF in its first line.
