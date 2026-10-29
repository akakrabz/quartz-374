---
title: "Homework and exams"
description: "The course's own problems worked out: the three Midterm 1 practice tests solved in the exam's format, the labs from 6a on with every problem explained, and homework write-ups that teach the method while solving the problems — every automaton, grammar and recurrence checked by script."
tags: [exam, homework, lab]
---

The rest of the site uses original problems and the books' exercises; this section is where the **course's own** problems are worked out. The practice-test pages are written the way a full-credit exam answer looks, with the rubric for each problem type linked. The lab pages give each problem's statement, a hint and an explained solution. The homework write-ups go slower: they start from the method and build each solution from the question "what is a subproblem?", for a reader who has only skimmed the notes.

## Midterm 1 practice tests

Five problems each, in the Midterm 1 format. The problem types repeat across the tests, in different orders:

| test | problems | page |
|---|---|---|
| 1 | true or false · language transformations (Delete1st) · induction (squish) · fooling set and grammar · DFA and regular expression | [[3-homework-and-exams/midterm-1-practice-1\|solutions]] |
| 2 | language transformations (compress0s) · regular expression, DFA and a lower bound (374 consecutive 1s) · induction · fooling set and grammar · true or false | [[3-homework-and-exams/midterm-1-practice-2\|solutions]] |
| 3 | true or false · parity: recursive definition, product construction, closure · fooling set and grammar · language transformations (take2skip2) · DFA and regular expression | [[3-homework-and-exams/midterm-1-practice-3\|solutions]] |

Before working them, read [[0-toolkit/06-how-exams-are-graded|how exams are graded]] and keep [[0-toolkit/02-proof-templates|proof templates]] open; the review of the material is [[0-toolkit/04-review-regular-and-context-free|Review: Chapters 1–5]].

## Labs

Each page states every problem (including the "harder problems to think about later"), with a folded hint and a folded solution that explains the idea before the details. Labs 6–8 are explained from the official solutions — every error found in them is fixed and noted on the page; labs 9a–10b had no posted solutions, so those solutions are ours, each checked against brute force and reviewed independently.

| lab | date | topic | page |
|---|---|---|---|
| 6a | Sep 30 | binary search: fixed point, local minimum, median and k-th smallest of two sorted arrays | [[3-homework-and-exams/lab-06a\|Lab 6a]] |
| 6b | Oct 1 | Karatsuba at work: powers of 2 and binary-to-decimal conversion | [[3-homework-and-exams/lab-06b\|Lab 6b]] |
| 7a | Oct 7 | backtracking: longest decreasing, alternating and convex subsequences; palindromes | [[3-homework-and-exams/lab-07a\|Lab 7a]] |
| 7b | Oct 9 | the same five problems as dynamic programs | [[3-homework-and-exams/lab-07b\|Lab 7b]] |
| 8a | Oct 14 | dynamic programming: sledding ramps, with at most $k$ jumps, two sledders | [[3-homework-and-exams/lab-08a\|Lab 8a]] |
| 8b | Oct 16 | dynamic programming: fewest 1s in an arithmetic expression; parenthesizing $+$ and $-$ | [[3-homework-and-exams/lab-08b\|Lab 8b]] |
| 9a | Oct 21 | graph reductions: a number maze and five variants | [[3-homework-and-exams/lab-09a\|Lab 9a]] |
| 9b | Oct 23 | graph reductions to dags: a consistent ranking, Judy's tour of the galaxies | [[3-homework-and-exams/lab-09b\|Lab 9b]] |
| 10a | Oct 28 | shortest paths: one negative edge, where to meet, looped trees | [[3-homework-and-exams/lab-10a\|Lab 10a]] |
| 10b | Oct 30 | all-pairs shortest paths: repairing a distance array after one wrong weight; arbitrage | [[3-homework-and-exams/lab-10b\|Lab 10b]] |

## Homework write-ups

| homework | topic | page |
|---|---|---|
| 6 | dynamic programming: days off in a sliding window, maximum flatness, palindrome decompositions | [[3-homework-and-exams/hw6-dynamic-programming\|HW6, worked through]] |

The method behind them is [[2-algorithms/03-dynamic-programming|Chapter 3]] and its [[0-toolkit/02-proof-templates#20-writing-up-a-dynamic-program|write-up template]].

### Sources for this page
Problems from the CS/ECE 374 A (Fall 2026) practice tests and homework handouts; the solutions are ours, and every automaton, regular expression, grammar, fooling set and recurrence on these pages is checked against brute force by `tools/checks/exams_mt1.py` and the homework check scripts.
