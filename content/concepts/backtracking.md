---
title: "Backtracking"
description: "Recursive brute force over a sequence of decisions: each call makes one decision, tries every option consistent with the past, and passes on a minimal summary of the decisions made so far. How to find the recursive problem, the exam write-up, and the classic mistakes."
tags: [concept, algorithms, backtracking, midterm-2]
aliases: ["backtracking algorithm", "recursive brute force"]
---

> [!definition] Definition — backtracking
> A **backtracking** algorithm builds a solution as a **sequence of decisions**. Each recursive call makes exactly one decision: it tries *every* option consistent with the decisions already made, recurses on each, and combines the answers — $\lor$ to decide, $+$ to count, $\max$ or $\min$ to optimize. A call's parameters are the part of the input still to be processed and a **summary of the past decisions**, kept as small as possible: all earlier queens in $n$ queens, the remaining target in subset sum, the last chosen element in longest increasing subsequence, nothing at all in text segmentation.

**Why it works.** Every solution makes *some* choice for the next decision, and the call made for that choice finds the best way to complete it — induction on the number of decisions left. Trying every choice therefore finds the best solution. The price is time: the recursion tree branches at every decision, so backtracking is exponential — $T(n)\le 2T(n-1)+O(1) = O(2^n)$ for in/out decisions — until [[concepts/memoization|memoization]] collapses the repeated subproblems into a [[concepts/dynamic-programming|dynamic program]].

> [!recipe] Recipe — from problem to backtracking algorithm
> 1. Write a solution as a sequence of decisions; store a set in an array to fix an order.
> 2. Jump into the middle: what must you know about the past to make the next decision consistently? Shrink it to a number, an index or one element.
> 3. Define the recursive function in English with exactly those parameters, in index form (prefix, suffix, interval, plus values), and name the call that answers the original question.
> 4. Base cases: nothing is left to decide. Recursive case: every consistent option, recursively; combine.
> 5. Running time: a recurrence from the branching, solved.

> [!template] Template — exam write-up (recursive-algorithm rubric)
> $\textsf{Name}(\text{parameters})$ returns *[what, in terms of the parameters only]*; we need $\textsf{Name}(\text{initial values})$. \
> **Base cases:** *[…]*. **Recursive case:** *[the options for the next decision, the call for each, how the answers combine]*. \
> **Correct because** every solution makes some choice for the next decision, and the call for that choice handles the rest. \
> **Time:** *[recurrence]*, so *[closed form]*.

> [!trap]
> - Describing the steps ("include or exclude $X[i]$") instead of what the function *returns*: the 3 description points are for the latter.
> - Adding a parameter — a remaining target, a previous element, a bound — without describing the *generalized* problem it creates.
> - A summary that depends on hidden state ("the best so far", "the current index") instead of explicit parameters.
> - Pruning "obviously useless" options without proof: that is a greedy step, not backtracking.
> - Missing or misordered base cases (in subset sum, test $T = 0$ before $i = 0$).

**Example (ours).** *Does some subset of $X[1\,..\,n]$ with no two adjacent elements sum to $T$?* Decide "in or out" for $X[i]$ from right to left. Taking $X[i]$ forbids $X[i-1]$, so after taking it the recursion simply jumps to $X[i-2]$ — the summary of the past is absorbed into the index. Let $\textsf{NoAdj}(i, t)$ be True iff some subset of $X[1\,..\,i]$ containing no two adjacent indices sums to $t$; we need $\textsf{NoAdj}(n, T)$:
$$
\textsf{NoAdj}(i, t) = \begin{cases} \textsf{True} & \text{if } t = 0\\ \textsf{False} & \text{if } t<0 \text{ or } i\le 0\\ \textsf{NoAdj}(i-1, t) \lor \textsf{NoAdj}(i-2,\ t - X[i]) & \text{otherwise.}\end{cases}
$$
The running time satisfies $T(n) \le T(n-1) + T(n-2) + O(1)$, so $T(n) = O(\phi^n)$ with $\phi = (1+\sqrt5)/2$. For $X = [4, 1, 2, 7, 3]$, the target 9 is reachable ($4+2+3$), but 10 is not: every subset summing to 10 — $\{7, 3\}$, $\{1, 2, 7\}$, $\{4, 1, 2, 3\}$ — contains two neighbors.

**Where it appears.** The whole of [[2-algorithms/02-backtracking|Chapter 2]]: [[2-algorithms/02-backtracking#21-n-queens|§2.1]] ($n$ queens, recursion trees), [[2-algorithms/02-backtracking#22-game-trees|§2.2]] (game trees), [[2-algorithms/02-backtracking#23-subset-sum|§2.3]] (subset sum), [[2-algorithms/02-backtracking#24-the-general-pattern|§2.4]] (the general pattern, with a table of what each call must remember), [[2-algorithms/02-backtracking#25-text-segmentation|§2.5]] (text segmentation), [[2-algorithms/02-backtracking#26-longest-increasing-subsequence|§2.6]] and [[2-algorithms/02-backtracking#27-longest-increasing-subsequence-take-2|§2.7]] (two recursions for LIS), [[2-algorithms/02-backtracking#28-optimal-binary-search-trees|§2.8]] (optimal binary search trees). Every dynamic program starts as one: [[2-algorithms/03-dynamic-programming#34-the-pattern-smart-recursion|§3.4]]. Grading: [[0-toolkit/06-how-exams-are-graded#11-recursive-algorithms|the recursive-algorithm rubric]].

Related: [[concepts/recursion]] · [[concepts/divide-and-conquer]] · [[concepts/subset-sum]] · [[concepts/longest-increasing-subsequence]] · [[concepts/memoization]] · [[concepts/dynamic-programming]]
