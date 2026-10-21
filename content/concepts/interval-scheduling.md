---
title: "Interval scheduling"
description: "Choosing the largest set of pairwise non-overlapping intervals (the book's class scheduling problem): take the interval that finishes first and recurse — O(n log n), proved by an exchange argument — and the natural rules that fail."
tags: [concept, algorithms, greedy, midterm-2]
aliases: ["class scheduling", "activity selection", "GreedySchedule", "earliest finish time first"]
---

> [!definition] Definition — interval scheduling
> Given $n$ classes (intervals) with start and finish times $S[i] < F[i]$, find a largest set $X$ of pairwise **compatible** classes: for distinct $i, j\in X$, $S[i] > F[j]$ or $S[j] > F[i]$ (in the book's convention, classes sharing an endpoint conflict). **Greedy solution:** sort by finish time; scan, and take every class that starts after the last class taken finishes. Time $O(n\log n)$ for the sort plus $O(n)$ for the scan.

**Why it works.** Let $f$ finish first. In any optimal schedule, replace its first-finishing class $g$ by $f$: every other class of the schedule starts after $g$ finishes, so after $f$ finishes — the swap keeps the schedule conflict-free and its size unchanged (Lemma 4.3). The classes compatible with $f$ are exactly those that start after $f$ ends, so the rest is the same problem on fewer classes, and induction finishes the proof (Theorem 4.4). Intuition: finishing first leaves the most room for everything else.

> [!recipe] Recipe — greedy on intervals
> 1. Ask which endpoint to sort by. For "most disjoint intervals", sort by **right** endpoint.
> 2. Before proving anything, test the rival rules (earliest start, shortest, fewest overlaps) on three-interval inputs.
> 3. Prove with the exchange: "Let $g$ be the first interval of an optimal solution to finish; replace it by the greedy one, which finishes no later."
> 4. Watch the endpoint convention: closed intervals that touch conflict; half-open ones do not.

> [!trap]
> - **Earliest start** fails: $[0,10]$, $[1,2]$, $[3,4]$ (greedy 1, optimum 2).
> - **Shortest first** fails: $[0,4]$, $[3,6]$, $[5,9]$ (greedy 1, optimum 2).
> - **Fewest conflicts first** fails on an 11-interval example (greedy 3, optimum 4; see §4.2).
> - **Weighted** intervals (maximize total credit hours): earliest finish fails — it takes $[0,2]$ worth 1 and loses $[1,10]$ worth 5 — and so do the other rules; use dynamic programming over the intervals sorted by finish time (the book's Exercise 4.2).
> - **Endpoints:** with the strict convention, $[1,3]$, $[3,5]$, $[5,7]$ allow only 2 classes; if touching were allowed, all 3.

**Example.** Six classes $[2,3]$, $[1,4]$, $[3,6]$, $[5,7]$, $[6,9]$, $[8,10]$, already sorted by finish time. Greedy takes $[2,3]$; skips $[1,4]$ and $[3,6]$ (both start at or before 3); takes $[5,7]$; skips $[6,9]$; takes $[8,10]$. Three classes — and checking all 64 subsets confirms that 3 is the maximum.

**Where it appears.** [[2-algorithms/04-greedy-algorithms#42-scheduling-classes|§4.2]] (GreedySchedule, Lemma 4.3, Theorem 4.4 in both forms, the failing rules), [[2-algorithms/04-greedy-algorithms#43-the-general-pattern|§4.3]] (the exchange-argument template); variants are the book's Exercises 4.1–4.5 ([[2-algorithms/04-greedy-algorithms-exercises|solved exercises]]).

Related: [[concepts/greedy-algorithms]] · [[concepts/dynamic-programming]] · [[concepts/backtracking]]
