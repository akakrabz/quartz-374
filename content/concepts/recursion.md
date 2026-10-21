---
title: "Recursion"
description: "Reduce a problem to strictly smaller instances of itself plus directly solved base cases; the Recursion Fairy is the induction hypothesis. How to specify, prove and analyze a recursive algorithm, and the classic mistakes."
tags: [concept, algorithms, recursion, midterm-2]
aliases: ["recursive algorithm", "Recursion Fairy", "simplify and delegate", "base case"]
---

> [!definition] Definition — reduction, recursion
> A **reduction** from problem $X$ to problem $Y$ is an algorithm for $X$ that calls an algorithm for $Y$ as a **black box**; its correctness may assume only that the black box solves $Y$, never how. **Recursion** is a reduction to *strictly smaller instances of the same problem*:
> - if the instance is small enough (a **base case**), solve it directly;
> - otherwise reduce it to one or more smaller instances, and build the answer from theirs.
>
> The smaller instances are solved by the **Recursion Fairy** — formally, the **induction hypothesis**.

**Why it works.** Correctness of a recursive algorithm is a strong induction on the size of the instance: the base cases are checked directly, and in the recursive case the induction hypothesis guarantees that the calls on smaller instances return correct answers, so only the combination step needs an argument. Termination needs every call to be strictly smaller in some nonnegative integer measure (length, value, number of disks); then every chain of calls reaches a base case.

> [!template] Template — specifying and proving a recursive algorithm
> 1. **Specify** what $\textsf{Alg}(\text{parameters})$ returns, in terms of its parameters. Generalize if the recursion needs it (the $k$-th smallest element rather than the median).
> 2. **Base cases:** which instances are solved directly, and how.
> 3. **Recursive case:** the smaller instances, and how their answers combine.
> 4. **Proof:** "Let $I$ be an arbitrary instance of size $n$; assume $\textsf{Alg}$ is correct on all smaller instances." Then argue only the base cases and the combination.
> 5. **Time:** a recurrence — the calls plus the non-recursive work — solved with a [[concepts/recursion-trees|recursion tree]].

> [!trap]
> - A "smaller" instance that is not strictly smaller: infinite recursion (example below).
> - Missing base cases, e.g. size 0 *and* size 1 when a call can produce either.
> - Unrolling the recursion instead of trusting the induction hypothesis.
> - Describing *how* the algorithm works instead of *what* it returns — the rubric's description points are for the latter.
> - A recursion that only works for a more general problem than the one asked: state and prove the general version.

**Example: binary search.** $\textsf{BinarySearch}(A[1..n], x)$ returns $\textsf{True}$ if and only if $x$ occurs in the sorted array $A[1..n]$.

```text
BinarySearch(A[1 .. n], x):
  if n = 0
    return False
  m ← ⌈n/2⌉
  if x = A[m]
    return True
  else if x < A[m]
    return BinarySearch(A[1 .. m − 1], x)
  else
    return BinarySearch(A[m + 1 .. n], x)
```

*Correct* by induction on $n$: the empty array contains nothing; if $x < A[m]$, sortedness puts every possible copy of $x$ in $A[1..m-1]$, and symmetrically for $x > A[m]$; both recursive instances have at most $\lfloor n/2\rfloor < n$ elements, so the induction hypothesis applies. *Time:* $T(n) = T(\lfloor n/2\rfloor) + O(1) = O(\log n)$ — at most $\lfloor\lg n\rfloor + 2$ calls. *The trap:* recursing on $A[m..n]$ instead of $A[m+1..n]$ looks harmless, but for $A = [4]$ and $x = 9$ we get $m = 1$, and the "smaller" instance is the same instance, forever.

**Where it appears.** [[2-algorithms/01-recursion#11-reductions|§1.1]] (reductions as black boxes), [[2-algorithms/01-recursion#12-simplify-and-delegate|§1.2]] (the definition, PeasantMultiply, the proof template), [[2-algorithms/01-recursion#13-tower-of-hanoi|§1.3]] (Tower of Hanoi), and every algorithm after it: [[concepts/divide-and-conquer|divide and conquer]] in the rest of Chapter 1, [[concepts/backtracking|backtracking]] in Chapter 2, recursion plus [[concepts/memoization|memoization]] in Chapter 3. The proof style is Part 1's [[concepts/induction-on-strings|strong induction]].

Related: [[concepts/divide-and-conquer]] · [[concepts/recursion-trees]] · [[concepts/backtracking]] · [[concepts/dynamic-programming]] · [[concepts/induction-on-strings]]
