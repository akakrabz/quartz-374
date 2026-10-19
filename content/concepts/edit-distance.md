---
title: "Edit distance"
description: "The minimum number of letter insertions, deletions and substitutions that transform one string into another: alignments, the three-case recurrence on pairs of prefixes, the O(mn) table, and how to read an optimal alignment back out of it."
tags: [concept, algorithms, dynamic-programming, midterm-2]
aliases: ["Levenshtein distance", "string alignment", "EditDistance"]
---

> [!definition] Definition — edit distance
> The **edit distance** between $A[1\,..\,m]$ and $B[1\,..\,n]$ is the minimum number of single-letter **insertions, deletions and substitutions** that transform $A$ into $B$ — equivalently, the minimum cost of an **alignment** (columns letter/letter, letter/gap or gap/letter; the cost is the number of columns whose two entries differ). For $0\le i\le m$ and $0\le j\le n$ let $\textsf{Edit}(i,j)$ be the edit distance between the prefixes $A[1\,..\,i]$ and $B[1\,..\,j]$; we need $\textsf{Edit}(m,n)$.
> $$
> \textsf{Edit}(i,j) = \begin{cases} i & \text{if } j = 0\\ j & \text{if } i = 0\\ \min\left\{\begin{array}{l} \textsf{Edit}(i, j-1) + 1\\ \textsf{Edit}(i-1, j) + 1\\ \textsf{Edit}(i-1,j-1) + [A[i]\ne B[j]] \end{array}\right\} & \text{otherwise}\end{cases}
> $$
> Memoize in an array $\mathit{Edit}[0\,..\,m,\ 0\,..\,n]$, fill it row by row ($i$ increasing outer, $j$ increasing inner): $O(mn)$ time and space.

**Why it works.** The last column of an optimal alignment of $A[1\,..\,i]$ and $B[1\,..\,j]$ is an insertion of $B[j]$, a deletion of $A[i]$, or a substitution of $B[j]$ for $A[i]$ (free if the letters are equal). Removing it leaves an optimal alignment of shorter prefixes — a cheaper one, glued back to the last column, would beat the optimum — so trying the three cases is enough.

> [!recipe] Recipe — fill the table, then read it back
> 1. Row 0 is $0, 1, \ldots, n$ and column 0 is $0, 1, \ldots, m$.
> 2. Every other entry is $\min\{\text{left}+1,\ \text{above}+1,\ \text{diagonal} + [A[i]\ne B[j]]\}$. The answer is in the bottom right corner.
> 3. **Recovering an alignment:** from $(m,n)$, step to a neighbor that accounts for the current value — diagonal (match or substitution), left (insert $B[j]$), up (delete $A[i]$) — until $(0,0)$; then reverse. $O(m+n)$ extra time; no arrows need to be stored.

> [!trap]
> - The base cases are $i$ and $j$, not 0.
> - A match costs 0, not 1: the diagonal term is $[A[i]\ne B[j]]$.
> - The running time is $O(mn)$; write it in both lengths.
> - Optimal alignments need not be unique — read back *one*, unless asked for all.
> - Transposing the table (the book prints $A$ along the top) swaps which direction means insertion and which deletion; the distance is symmetric.

**Example — FOOD and MONEY.** Rows are prefixes of FOOD, columns prefixes of MONEY:

| | | M | O | N | E | Y |
|---|---|---|---|---|---|---|
| | **0** | 1 | 2 | 3 | 4 | 5 |
| F | 1 | **1** | 2 | 3 | 4 | 5 |
| O | 2 | 2 | **1** | **2** | 3 | 4 |
| O | 3 | 3 | 2 | 2 | **3** | 4 |
| D | 4 | 4 | 3 | 3 | 3 | **4** |

The edit distance is 4. Reading back with diagonal moves preferred (the bold entries): $(4,5)$ diagonal (D→Y), $(3,4)$ diagonal (O→E), $(2,3)$ left (insert N), $(2,2)$ diagonal (O = O, free), $(1,1)$ diagonal (F→M). Reversed, that is the alignment `F O _ O D` over `M O N E Y`, of cost 4. There are exactly three optimal alignments; the other two place the gap after the second O (`F O O _ D`, the book's) or at the end (`F O O D _`).

**Where it appears.** [[2-algorithms/03-dynamic-programming#37-edit-distance|§3.7]] (the recurrence, the pseudocode and the ALGORITHM/ALTRUISTIC table with its three optimal alignments), [[2-algorithms/03-dynamic-programming#34-the-pattern-smart-recursion|§3.4]] (its dependency picture and evaluation order).

Related: [[concepts/dynamic-programming]] · [[concepts/memoization]] · [[concepts/strings]] · [[concepts/longest-increasing-subsequence]]
