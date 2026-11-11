---
title: "Homework and exams"
description: "The course's own problems worked out: the three Midterm 1 and the Midterm 2 practice tests solved in the exam's format, the labs from 6a on with every problem explained, the homework write-ups for HW6 to HW9 that teach the method while solving the problems, and a study guide for the open Homework 10 — every automaton, grammar, recurrence and reduction checked by script."
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

## Midterm 2 practice tests

Five problems each in the Midterm 2 format (short answers, dynamic programming, divide and conquer, graph reductions), plus the course's four dynamic-programming practice problems. Every solution is ours — none were posted — and every algorithm is checked against brute force:

| test | problems | page |
|---|---|---|
| 1 | recurrences and two memoization plans · quadhopper (greedy fails; a suffix DP) · the highest point of a short walk (Dijkstra from both ends) · the longest verbal subsequence · the closest pair of points around a black box | [[3-homework-and-exams/midterm-2-practice-1\|solutions]] |
| 2 | depth-first, breadth-first and shortest-path trees and a topological order on one dag · rainbow walks · square-depth · merging $k$ sorted arrays · the fewest terms to finish a degree | [[3-homework-and-exams/midterm-2-practice-2\|solutions]] |
| 3 | recurrences, two small graphs and a memoization plan · cards against greedy Elmo · the least remote vertex · the one even adjacent pair · shortest zigzag walks | [[3-homework-and-exams/midterm-2-practice-3\|solutions]] |
| DP | a dance contest · voting districts · $k$ intervals with the smallest maximum sum · the longest mostly odd increasing subsequence | [[3-homework-and-exams/midterm-2-dp-practice\|solutions]] |

The material is reviewed in [[0-toolkit/08-review-algorithms|the Midterm 2 review]], and condensed for the handwritten sheet in [[0-toolkit/09-midterm-2-cheat-sheet|the Midterm 2 cheat sheet]].

## Labs

Each page states every problem (including the "harder problems to think about later"), with a folded hint and a folded solution that explains the idea before the details. Labs 6–8 are explained from the official solutions — every error found in them is fixed and noted on the page; labs 9a–10b had no posted solutions, so those solutions are ours, each checked against brute force and reviewed independently. Labs 11, 12a and 12b are ours as well and checked against exhaustive search, but not yet reviewed independently.

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
| 11 | Nov 4 | solve it both ways: an increasing subsequence with at most $k$ icky numbers, and the longest palindrome along a path of a dag, each as a dynamic program and as a graph reduction | [[3-homework-and-exams/lab-11\|Lab 11]] |
| 12a | Nov 11 | from a yes-or-no black box to the optimum and to a solution: longest path, independent set, coloring, circuit satisfiability | [[3-homework-and-exams/lab-12a\|Lab 12a]] |
| 12b | Nov 13 | NP-hardness of five variants of Sat (4Sat, BalancedSat, Exact3Sat, bounded occurrences), and why XorSat is easy | [[3-homework-and-exams/lab-12b\|Lab 12b]] |

## Homework write-ups

| homework | topic | page |
|---|---|---|
| 6 | dynamic programming: days off in a sliding window, maximum flatness, palindrome decompositions | [[3-homework-and-exams/hw6-dynamic-programming\|HW6, worked through]] |
| 7 | more dynamic programming: longest common decreasing and palindromic subsequences, orthogonally separable rectangles, broadcasting in a binary tree | [[3-homework-and-exams/hw7-dynamic-programming\|HW7, worked through]] |
| 8 | graph algorithms: the cheapest tram trip with a two-sticker card (three layers and Dijkstra), a walk whose labels spell 374 and then any regular language (the graph times a DFA) | [[3-homework-and-exams/hw8-graph-algorithms\|HW8, worked through]] |
| 9 | more graph algorithms: equal path lengths and the most relics in a game map (dynamic programming on a dag), energetic cycles (a negative-cycle test, a proof, and layers by balance) | [[3-homework-and-exams/hw9-more-graph-algorithms\|HW9, worked through]] |
| 10 | NP and reductions: perfect matching is in NP and reduces to Sat, StringMatch is NP-hard, and the handout's solved stone puzzle — **open until Nov 17, so a study guide without solutions** | [[3-homework-and-exams/hw10-np-hardness\|HW10, study guide]] |

The method behind HW6 and HW7 is [[2-algorithms/03-dynamic-programming|Chapter 3]] and its [[0-toolkit/02-proof-templates#20-writing-up-a-dynamic-program|write-up template]]; behind HW8 and HW9, [[2-algorithms/05-basic-graph-algorithms#57-graph-reductions-flood-fill|graph reductions]] and their [[0-toolkit/02-proof-templates#22-solving-a-problem-by-graph-reduction|template]]. The HW8 and HW9 pages are written from the solutions that were submitted: each solution was re-derived and checked, and a box at the end of every part says what, if anything, was changed from the submitted version. Behind HW10, [[2-algorithms/12-np-hardness|Chapter 12]] and the [[0-toolkit/02-proof-templates#23-proving-a-problem-np-hard|NP-hardness template]]. A homework that is still open gets a study guide — what each problem practices, its rubric, and where the same kind of problem is worked on this site — and no solutions. For Midterm 2 (Mon Nov 9), start from [[0-toolkit/08-review-algorithms|the algorithms review]]. What each lecture covered is in [[5-lecture-log/index|the lecture log]].

### Sources for this page
Problems from the CS/ECE 374 A (Fall 2026) practice tests and homework handouts; the solutions are ours, and every automaton, regular expression, grammar, fooling set, recurrence, algorithm and reduction on these pages is checked against brute force by `tools/checks/exams_mt1.py`, `tools/checks/exams_mt2.py`, the lab scripts `tools/checks/labs_*.py` and the homework check scripts.
