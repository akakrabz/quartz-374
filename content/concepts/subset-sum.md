---
title: "Subset sum"
description: "Does some subset of X[1..n] sum to T? The include/exclude backtracking recursion (O(2^n)), constructing the subset, the O(nT) dynamic program, and the base-case and description traps."
tags: [concept, algorithms, backtracking, dynamic-programming, midterm-2]
aliases: ["SubsetSum", "subset-sum problem"]
---

> [!definition] Problem and backtracking recurrence
> **SubsetSum:** given positive integers $X[1\,..\,n]$ and an integer $T$, does some subset of $X$ sum to $T$? Let $\textsf{SubsetSum}(X, i, T)$ be True iff some subset of the prefix $X[1\,..\,i]$ sums to $T$; we need $\textsf{SubsetSum}(X, n, T)$.
> - **Base cases.** True if $T = 0$; False if $T < 0$, or if $i = 0$ and $T\ne 0$.
> - **Recursive case** (otherwise): with $X[i]$, or without it,
> $$
> \textsf{SubsetSum}(X, i, T) = \textsf{SubsetSum}(X, i-1,\ T - X[i]) \lor \textsf{SubsetSum}(X, i-1,\ T).
> $$

**Why it works.** A subset of $X[1\,..\,i]$ either contains $X[i]$ — and then the rest of it sums to $T - X[i]$ — or it does not. The decisions already made are summarized by one number, the *remaining target*; which elements were chosen does not matter. Evaluated by plain recursion, the time satisfies $T(n)\le 2T(n-1)+O(1)$, so it is $O(2^n)$, and that is tight: when the target exceeds the sum of all elements there are exactly $2^{n+1}-1$ calls. To return a subset instead of True, return $\varnothing$ at $T = 0$, None at failure, and add $X[i]$ on the way back up from a successful "with" call (the book's $\textsf{ConstructSubset}$).

> [!definition] The dynamic program (Chapter 3, in rubric form)
> 1. **Function.** $\textsf{SS}(i, t)$ is True iff some subset of the *suffix* $X[i\,..\,n]$ sums to $t$, for $1\le i\le n+1$ and $0\le t\le T$. We need $\textsf{SS}(1, T)$.
> 2. **Recurrence** (the case $t < X[i]$ avoids negative targets):
> $$
> \textsf{SS}(i, t) = \begin{cases} \textsf{True} & \text{if } t = 0\\ \textsf{False} & \text{if } i > n \text{ (and } t > 0)\\ \textsf{SS}(i+1, t) & \text{if } t < X[i]\\ \textsf{SS}(i+1, t) \lor \textsf{SS}(i+1, t - X[i]) & \text{otherwise.}\end{cases}
> $$
> 3. **Memoization:** a boolean array $S[1\,..\,n+1,\ 0\,..\,T]$.
> 4. **Evaluation order:** $i$ from $n+1$ down to 1 in the outer loop; $t$ in any order in the inner loop (row $i$ reads only row $i+1$).
> 5. **Time:** $O(nT)$ entries, $O(1)$ each: $O(nT)$.

$O(nT)$ is polynomial in the *value* $T$ but not in the input size, since $T$ takes only $O(\log T)$ bits to write down; when $T$ is much larger than $2^n$, the table is slower than plain backtracking. Subset sum is NP-hard (§12.12 of the book), so no truly polynomial algorithm is known.

> [!trap]
> - Test $T = 0$ **before** $i = 0$: reaching the target exactly with the last element must return True.
> - "$T<0$ means False" relies on **positive** elements.
> - Describe *which* elements a subproblem may use (a prefix $X[1\,..\,i]$ or a suffix $X[i\,..\,n]$) and *which* target; "can we reach $t$ with the current elements" is not a usable description.
> - A hash table of reachable sums earns no memoization credit on exams; use the array.
> - Prefix (Chapter 2) and suffix (Chapter 3) versions are both fine — but don't mix them in one answer.

**Example.** $X = [3, 5, 6, 8]$ and $T = 14$: exactly two subsets work, $\{6, 8\}$ and $\{3, 5, 6\}$. $\textsf{SubsetSum}$ tries "with $X[4] = 8$" first and succeeds through $\{6, 8\}$; $\textsf{ConstructSubset}$, which tries "without" first, returns $\{3, 5, 6\}$. Row $i = 1$ of the dynamic program marks the reachable sums $0, 3, 5, 6, 8, 9, 11, 13, 14$ in the range $0..14$; for instance 12 is not reachable.

**Where it appears.** [[2-algorithms/02-backtracking#23-subset-sum|§2.3]] (the recursion, its analysis, $\textsf{ConstructSubset}$ and other variants), [[2-algorithms/02-backtracking#24-the-general-pattern|§2.4]] (why a *set* problem becomes a sequence of decisions), [[2-algorithms/03-dynamic-programming#38-subset-sum|§3.8]] (the dynamic program). A variant with a constraint between neighbors is the example on [[concepts/backtracking]].

Related: [[concepts/backtracking]] · [[concepts/dynamic-programming]] · [[concepts/memoization]] · [[concepts/recursion]]
