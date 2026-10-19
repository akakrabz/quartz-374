---
title: "Divide and conquer"
description: "Split an instance into independent smaller instances of the same problem, solve them recursively, combine the answers: the pattern behind mergesort, quicksort, linear-time selection, Karatsuba multiplication and repeated squaring, with the rubric's write-up format and their recurrences."
tags: [concept, algorithms, recursion, midterm-2]
aliases: ["divide-and-conquer algorithm", "D&C", "recursive-algorithm rubric"]
---

> [!definition] Definition — divide and conquer
> 1. **Divide** the given instance into several *independent* smaller instances of *exactly the same* problem.
> 2. **Delegate** each smaller instance to the Recursion Fairy (recursive calls).
> 3. **Combine** their solutions into the solution of the given instance.
>
> Below a constant size, solve directly. Correctness is an induction; the running time is a recurrence $T(n) = \sum_i T(n_i) + (\text{divide and combine work})$.

**Why it works — and why it is fast.** Correctness is that of any [[concepts/recursion|recursion]]: assume the recursive calls are right and check the combination. Speed comes from the recurrence: balanced subproblems whose sizes add up to $n$ with linear extra work give about $\lg n$ levels of $n$ work each ($\Theta(n\log n)$, mergesort); *fewer* subproblems than the naive split (Karatsuba's 3 instead of 4) or subproblems whose sizes add up to *less* than $n$ (selection's $n/5 + 7n/10$) push the solution down. [[concepts/recursion-trees|Recursion trees]] make this precise.

> [!template] Template — a divide-and-conquer answer (recursive-algorithm rubric, 10 points)
> 1. **What the recursive algorithm computes** (3): what it returns, in terms of its parameters; required whenever you generalize the problem or add assumptions. Not how it works.
> 2. **Base case(s)** (1).
> 3. **Divide** (2): the exact recursive subproblems.
> 4. **Conquer** (2): how the recursive results combine into the answer.
> 5. **Time** (2): the recurrence (1) and its closed-form solution (1).

| algorithm | recurrence | solution |
|---|---|---|
| MergeSort | $T(n) = 2T(n/2) + O(n)$ | $\Theta(n\log n)$ |
| QuickSort, worst-case pivots | $T(n) = T(n-1) + O(n)$ | $\Theta(n^2)$ |
| MomSelect | $T(n)\le T(n/5) + T(7n/10) + O(n)$ | $\Theta(n)$ |
| SplitMultiply | $T(n) = 4T(n/2) + O(n)$ | $\Theta(n^2)$ |
| FastMultiply (Karatsuba) | $T(n) = 3T(n/2) + O(n)$ | $\Theta(n^{\lg 3})$ |
| PiṅgalaPower | $T(n)\le T(n/2) + 2$ | $O(\log n)$ multiplications |
| BinarySearch | $T(n) = T(n/2) + O(1)$ | $\Theta(\log n)$ |

> [!trap]
> - The subproblems must be *independent* instances of the *same* problem. If the same subproblems recur over and over, the recursion can take exponential time — that is the cue for [[concepts/dynamic-programming|dynamic programming]].
> - Dividing and combining are not free: Partition and Merge cost $\Theta(n)$ and belong in the recurrence.
> - A split that can be $1$ versus $n-1$ gives $\Theta(n^2)$ (worst-case quicksort); balance matters.
> - A recurrence without its solution, or a solution without its recurrence, each lose a time point.

**Example: minimum and maximum together.** $\textsf{MinMax}(A[1..n])$, for $n\ge1$, returns the pair (smallest, largest) of $A[1..n]$. Base cases: $n = 1$ returns $(A[1], A[1])$ with no comparisons; $n = 2$ uses one comparison. Otherwise let $m = \lfloor n/2\rfloor$, recursively compute $(a_1, b_1) = \textsf{MinMax}(A[1..m])$ and $(a_2, b_2) = \textsf{MinMax}(A[m+1..n])$, and return $(\min(a_1,a_2), \max(b_1,b_2))$ — two more comparisons. The comparison count satisfies $T(2) = 1$, $T(n) = 2T(n/2) + 2$, so $T(n) = 3n/2 - 2$ when $n$ is a power of 2 (induction: $2(3n/4 - 2) + 2 = 3n/2 - 2$), against $2n - 2$ for two separate scans: 1534 instead of 2046 comparisons for 1024 elements. (For other $n$ this particular split can cost slightly more; $n = 6$ takes 8.)

**Where it appears.** [[2-algorithms/01-recursion#16-the-pattern|§1.6]] (the pattern, the rubric template, a table of the chapter's algorithms), with the instances [[2-algorithms/01-recursion#14-mergesort|§1.4]] mergesort, [[2-algorithms/01-recursion#15-quicksort|§1.5]] quicksort, [[2-algorithms/01-recursion#18-linear-time-selection|§1.8]] selection, [[2-algorithms/01-recursion#19-fast-multiplication|§1.9]] multiplication and [[2-algorithms/01-recursion#110-exponentiation|§1.10]] exponentiation. The same rubric grades [[concepts/backtracking|backtracking]] algorithms.

Related: [[concepts/recursion]] · [[concepts/recursion-trees]] · [[concepts/linear-time-selection]] · [[concepts/backtracking]] · [[concepts/dynamic-programming]]
