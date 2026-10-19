---
title: "Longest increasing subsequence"
description: "The length of a longest strictly increasing subsequence of A[1..n], two ways: LISbigger(i, j) (is the next element in?) and LISfirst(i) (what comes next?) — the exponential backtracking recurrences of Chapter 2 and their O(n^2) dynamic programs from Chapter 3."
tags: [concept, algorithms, backtracking, dynamic-programming, midterm-2]
aliases: ["LIS", "LISbigger", "LISfirst", "longest increasing subsequence problem"]
---

> [!definition] Problem and the two recurrences
> Given $A[1\,..\,n]$, find the length of a longest **strictly** increasing subsequence: the largest $\ell$ with indices $i_1<\dots<i_\ell$ and $A[i_1]<\dots<A[i_\ell]$. Add a sentinel $A[0] = -\infty$.
>
> **Take 1 — is the next element in?** For $0\le i<j\le n+1$, $\textsf{LISbigger}(i, j)$ is the length of a longest increasing subsequence of $A[j\,..\,n]$ in which every element is larger than $A[i]$. Answer: $\textsf{LISbigger}(0, 1)$.
> $$
> \textsf{LISbigger}(i, j) = \begin{cases}
> 0 & \text{if } j > n\\
> \textsf{LISbigger}(i, j+1) & \text{if } A[i] \ge A[j]\\
> \max\big\{\textsf{LISbigger}(i, j+1),\ 1 + \textsf{LISbigger}(j, j+1)\big\} & \text{otherwise}
> \end{cases}
> $$
> **Take 2 — what comes next?** For $0\le i\le n$, $\textsf{LISfirst}(i)$ is the length of a longest increasing subsequence of $A[i\,..\,n]$ that **begins with** $A[i]$. Answer: $\textsf{LISfirst}(0) - 1$, or $\max_{1\le i\le n}\textsf{LISfirst}(i)$.
> $$
> \textsf{LISfirst}(i) = 1 + \max\big\{\textsf{LISfirst}(j) \bigm| j > i \text{ and } A[j] > A[i]\big\}, \qquad \max\varnothing = 0.
> $$

**Why they work.** Both are backtracking over "what is the last element chosen?": an increasing subsequence can be extended by $x$ iff $x$ exceeds its last element, so that element — passed as the index $i$ — is all a call needs to know about the past. Take 1 decides about each *input* element in turn (skip or take); take 2 picks the next *output* element among the later, larger ones. As plain recursion both run in $O(2^n)$ time, and on an increasing array they really make $2^{n+1}-1$ and $2^n$ calls. Memoized:

> [!recipe] The dynamic programs (Chapter 3)
> | | take 1: $\textsf{LISbigger}(i, j)$ | take 2: $\textsf{LISfirst}(i)$ |
> |---|---|---|
> | memoization | 2D array $\textsf{LISbigger}[0\,..\,n,\ 1\,..\,n+1]$ (only $i<j$ is used) | 1D array $\textsf{LISfirst}[0\,..\,n]$ |
> | evaluation order | outer loop: column $j$ from $n+1$ down to 1; inner loop: $i<j$ in any order | $i$ from $n$ down to 0; inner loop over $j>i$ in any order |
> | time | $O(n^2)$ entries, $O(1)$ each: $O(n^2)$ | $O(n)$ entries, $O(n)$ each: $O(n^2)$ |
> | space | $O(n^2)$, or $O(n)$ keeping two columns | $O(n)$ |

```text
FastLIS2(A[1 .. n]):
  A[0] ← −∞                            ⟨⟨Add a sentinel⟩⟩
  for i ← n down to 0
    LISfirst[i] ← 1
    for j ← i + 1 to n
      if A[j] > A[i] and 1 + LISfirst[j] > LISfirst[i]
        LISfirst[i] ← 1 + LISfirst[j]
  return LISfirst[0] − 1                ⟨⟨Don't count the sentinel⟩⟩
```

> [!trap]
> - Dropping "that begins with $A[i]$" or "every element larger than $A[i]$": the described function changes, the recurrence no longer matches it, and the DP rubric gives nothing for the rest.
> - "The last element chosen so far" is hidden state; make it a parameter, the index $i$.
> - Increasing means **strictly**: the skip-only case is $A[i]\ge A[j]$, and equal elements never both count.
> - Computing only $\textsf{LISfirst}(1)$ (the LIS need not start at $A[1]$), or forgetting the $-1$ for the sentinel.
> - Entry $(i, j)$ of the take-1 table needs column $j+1$: fill columns right to left, not row by row from the top.

**Example (ours).** $A = 5, 2, 8, 6, 3, 6, 9, 7$. Then $\textsf{LISfirst}(1), \dots, \textsf{LISfirst}(8) = 3, 4, 2, 2, 3, 2, 1, 1$ and $\textsf{LISfirst}(0) = 5$, so the LIS has length 4 — for instance $2, 3, 6, 9$ or $2, 3, 6, 7$; the two 6s cannot both be used. In take 1, $\textsf{LISbigger}(1, 2) = 2$: after choosing $A[1] = 5$, the best continuations ($8, 9$ or $6, 9$ or $6, 7$) have two elements, so subsequences starting with 5 have length 3.

**Where it appears.** [[2-algorithms/02-backtracking#26-longest-increasing-subsequence|§2.6]] ($\textsf{LISbigger}$ and the digits-of-$\pi$ example), [[2-algorithms/02-backtracking#27-longest-increasing-subsequence-take-2|§2.7]] ($\textsf{LISfirst}$, with a full table for the example, and the comparison of the two), [[2-algorithms/03-dynamic-programming#36-longest-increasing-subsequence|§3.6]] (the dynamic programs $\textsf{FastLIS}$ and $\textsf{FastLIS2}$). Subsequences and substrings of strings: [[1-models-of-computation/01-strings#15-indices-substrings-and-subsequences|Models of Computation §1.5]].

Related: [[concepts/backtracking]] · [[concepts/dynamic-programming]] · [[concepts/memoization]] · [[concepts/edit-distance]] · [[concepts/strings]]
