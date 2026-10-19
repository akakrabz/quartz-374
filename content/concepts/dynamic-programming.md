---
title: "Dynamic programming"
description: "Recursion without repetition: specify a recursive function in English, write its recurrence, and evaluate it once per subproblem in an order that respects the dependencies — with the rubric's write-up format and a worked example."
tags: [concept, algorithms, dynamic-programming, midterm-2]
aliases: ["DP", "dynamic program", "smart recursion", "dynamic programming rubric"]
---

> [!definition] Definition — dynamic programming
> A **dynamic programming** algorithm evaluates a recursive formulation of a problem — a function of a few parameters, defined by a recurrence — so that each **distinct subproblem is solved once**: its value is stored in a memoization structure, usually an array indexed by the parameters, and every later use is a look-up. The entries are filled in an **evaluation order** in which every entry comes after the entries it reads. Then
> $$
> \begin{aligned} \text{space} &= \text{number of subproblems},\\ \text{time} &= \sum_{\text{subproblems}} \text{work not counting recursive calls}. \end{aligned}
> $$

**Why it works.** A backtracking algorithm's running time counts *calls*, and the calls can be exponentially many even when only polynomially many *distinct* subproblems exist: RecFibo makes $2F_{n+1}-1$ calls to compute $F_n$, but there are only $n+1$ different arguments. Correctness comes from the recurrence alone, proved by induction like any recursive algorithm; the table and the loops only change *when* each value is computed. So **dynamic programming is about smart recursion, not about filling in tables** — get the recurrence right first.

> [!recipe] Recipe — from a problem to a dynamic program
> 1. **Find the recursion.** Think backtracking: what is the first (or last) decision — the first word, the last column of an alignment, the root of a tree? Try every option and recurse on what is left.
> 2. **Specify the function** in English: what it returns, as a function of its parameters only.
> 3. **Write the recurrence**, base cases first.
> 4. **Turn the crank:** subproblems → memoization array → dependencies → evaluation order → time → pseudocode (optional).

> [!template] Template — the rubric's write-up (3 + 4 + 3 points)
> 1. **Function (3).** "For [ranges of the parameters], let $\textsf{Name}(i,t)$ denote [the value] for [the portion of the input: prefix $A[1\,..\,i]$, suffix $A[i\,..\,n]$, interval $A[i\,..\,k]$, pair of prefixes, subtree of $v$] [and the extra parameter $t$]. We need $\textsf{Name}(\ldots)$."
> 2. **Recurrence (4)** — base cases (1), recursive cases (3), each with its condition.
> 3. **Memoization (1)** — "an array $\textsf{Name}[1\,..\,n+1,\ 0\,..\,T]$".
> 4. **Evaluation order (1)** — "outer loop $i$ from $n+1$ down to $1$, inner loop $t$ from $0$ to $T$".
> 5. **Time (1)** — "$(n+1)(T+1)$ entries, $O(1)$ each: $O(nT)$".
>
> Without a usable function description the rest earns nothing; pseudocode is optional; the optimal *value* suffices unless the structure is asked for.

> [!trap]
> - **Describing how, not what** ("we scan the table…"), or a function that depends on hidden state ("the best so far", "the current index").
> - **Undescriptive names** ($\textsf{OPT}$, $\textsf{memo}$, a single letter) cost a point; a **hash table** as memoization structure earns nothing.
> - **An evaluation order that reads unfilled entries**; nested loops without saying which is outer.
> - **Time = entries only**, forgetting the work per entry ($O(n^3)$ for optimal BSTs, not $O(n^2)$); or the wrong variables ($O(n^2)$ for an $m\times n$ table).
> - **A greedy shortcut without a proof** costs $1\tfrac12$ points; and **$O(nT)$ is not polynomial** when $T$ is a number in the input.

**Example — making change.** Coin values $D[1\,..\,k]$ with $D$ containing 1, unlimited supply, target $T$: use as few coins as possible. Greedy (largest coin first) fails for $D = (1, 4, 5)$ and $T = 8$: it takes $5+1+1+1$, four coins, but $4+4$ uses two.
- **Function.** For $0\le t\le T$, $\textsf{MinCoins}(t)$ is the minimum number of coins with values in $D$ that sum to exactly $t$. We need $\textsf{MinCoins}(T)$.
- **Recurrence.** $\textsf{MinCoins}(0) = 0$, and for $t > 0$, $\textsf{MinCoins}(t) = 1 + \min\{\textsf{MinCoins}(t - D[i]) \mid D[i]\le t\}$ (the last coin is some $D[i]\le t$).
- **Memoization** $\mathit{MinCoins}[0\,..\,T]$; **order** $t$ from $0$ up to $T$; **time** $T+1$ entries $\times$ $O(k)$ $= O(kT)$ — pseudo-polynomial.

For $D = (1,4,5)$ the table $\mathit{MinCoins}[0\,..\,8]$ is $0, 1, 2, 3, 1, 1, 2, 3, 2$.

**Where it appears.** [[2-algorithms/03-dynamic-programming#34-the-pattern-smart-recursion|§3.4]] (the recipe, the template and the dependency pictures), [[2-algorithms/03-dynamic-programming#31-matravrtta-fibonacci-numbers|§3.1]] (Fibonacci: backtracking, memoization, table), [[2-algorithms/03-dynamic-programming#35-warning-greed-is-stupid|§3.5]] (why not greedy), [[2-algorithms/03-dynamic-programming#the-chapters-dynamic-programs-at-a-glance|all the chapter's dynamic programs at a glance]], [[0-toolkit/06-how-exams-are-graded#12-dynamic-programming|how dynamic programs are graded]]; the recursions come from [[2-algorithms/02-backtracking#24-the-general-pattern|backtracking (§2.4)]].

Related: [[concepts/memoization]] · [[concepts/backtracking]] · [[concepts/edit-distance]] · [[concepts/subset-sum]] · [[concepts/longest-increasing-subsequence]] · [[concepts/optimal-binary-search-trees]] · [[concepts/dynamic-programming-on-trees]]
