---
title: "Homework and exams"
description: "The course's own problems worked out: the three Midterm 1 practice tests solved in the exam's format, and homework write-ups that teach the method while solving the problems — every automaton, grammar and recurrence checked by script."
tags: [exam, homework]
---

The rest of the site uses original problems and the books' exercises; this section is where the **course's own** problems are worked out. The practice-test pages are written the way a full-credit exam answer looks, with the rubric for each problem type linked. The homework write-ups go slower: they start from the method and build each solution from the question "what is a subproblem?", for a reader who has only skimmed the notes.

## Midterm 1 practice tests

Five problems each, in the Midterm 1 format. The problem types repeat across the tests, in different orders:

| test | problems | page |
|---|---|---|
| 1 | true or false · language transformations (Delete1st) · induction (squish) · fooling set and grammar · DFA and regular expression | [[3-homework-and-exams/midterm-1-practice-1\|solutions]] |
| 2 | language transformations (compress0s) · regular expression, DFA and a lower bound (374 consecutive 1s) · induction · fooling set and grammar · true or false | [[3-homework-and-exams/midterm-1-practice-2\|solutions]] |
| 3 | true or false · parity: recursive definition, product construction, closure · fooling set and grammar · language transformations (take2skip2) · DFA and regular expression | [[3-homework-and-exams/midterm-1-practice-3\|solutions]] |

Before working them, read [[0-toolkit/06-how-exams-are-graded|how exams are graded]] and keep [[0-toolkit/02-proof-templates|proof templates]] open; the review of the material is [[0-toolkit/04-review-regular-and-context-free|Review: Chapters 1–5]].

## Homework write-ups

| homework | topic | page |
|---|---|---|
| 6 | dynamic programming: days off in a sliding window, maximum flatness, palindrome decompositions | [[3-homework-and-exams/hw6-dynamic-programming\|HW6, worked through]] |

The method behind them is [[2-algorithms/03-dynamic-programming|Chapter 3]] and its [[0-toolkit/02-proof-templates#20-writing-up-a-dynamic-program|write-up template]].

### Sources for this page
Problems from the CS/ECE 374 A (Fall 2026) practice tests and homework handouts; the solutions are ours, and every automaton, regular expression, grammar, fooling set and recurrence on these pages is checked against brute force by `tools/checks/exams_mt1.py` and the homework check scripts.
