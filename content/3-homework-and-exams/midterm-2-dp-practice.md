---
title: "Midterm 2 dynamic-programming practice — solutions"
description: "Four dynamic programs from the course's practice handout, each written up for the full rubric: a dance contest (a suffix with a jump), voting districts of size k to 2k (a suffix and the length of the first district, O(nk)), splitting an array into k intervals with the smallest maximum sum (a suffix and a count, O(n^2 k)), and the longest mostly odd increasing subsequence (fix the length, maximize odd minus even, O(n^3))."
tags: [exam, midterm-2, algorithms, dynamic-programming]
---

*Dynamic-programming practice · CS/ECE 374 A, Fall 2026 · four problems, each the dynamic-programming problem of a Midterm 2 · the practice tests: [[3-homework-and-exams/midterm-2-practice-1|test 1]], [[3-homework-and-exams/midterm-2-practice-2|test 2]], [[3-homework-and-exams/midterm-2-practice-3|test 3]] · how it is graded: [[0-toolkit/06-how-exams-are-graded#12-dynamic-programming|the DP rubric]] · on one page: [[0-toolkit/09-midterm-2-cheat-sheet|cheat sheet]]*

> [!abstract] In one breath
> All four are one-sequence problems, so every function starts from a **suffix** and adds what the rest of the computation needs. **Problem 1** (dancing): dance to song $k$ or not; dancing jumps to song $k + \mathit{Wait}[k] + 1$; $O(n)$ time. **Problem 2** (districts): the first district has between $k$ and $2k$ addresses; try each length, with prefix sums for the majority test; $O(nk)$ time. **Problem 3** (balanced partition): the function needs the number of intervals still to be made, and tries every end of the first interval; $O(n^2k)$ time. **Problem 4** (mostly odd increasing subsequence): "mostly odd" is a condition on the whole sequence, so fix its length and maximize the number of odd minus even elements; $O(n^3)$ time.

*All four: template [[0-toolkit/02-proof-templates#20-writing-up-a-dynamic-program|dynamic program]] · concepts [[concepts/dynamic-programming]], [[concepts/memoization]] · method [[2-algorithms/03-dynamic-programming#34-the-pattern-smart-recursion|§3.4]] · subproblem shapes [[0-toolkit/08-review-algorithms#4-chapter-3--dynamic-programming|review §4]]*

## Problem 1 — The dance contest

> [!question] Problem 1
> The judges will play $n$ songs, in a known order. If you dance to the $k$th song, you are awarded exactly $\mathit{Score}[k]$ points, but then you cannot dance to the next $\mathit{Wait}[k]$ songs (songs $k+1$ through $k + \mathit{Wait}[k]$). Describe an algorithm to compute the maximum total score you can achieve, given the arrays $\mathit{Score}[1\,..\,n]$ and $\mathit{Wait}[1\,..\,n]$.

The question to ask about an optimal plan: do you dance to the first song that is still available? If not, the rest is the same problem from the next song; if yes, it is the same problem from song $k + \mathit{Wait}[k] + 1$.

> [!key] Answer
> **Function.** For $1\le k\le n+1$, let $\textsf{MaxScore}(k)$ be the largest total score you can collect from songs $k$ through $n$, if you are free to dance to song $k$. We need $\textsf{MaxScore}(1)$.
>
> **Recurrence.** Write $k' = \min\{k + \mathit{Wait}[k] + 1,\ n + 1\}$ for the first song you can dance to after dancing to song $k$.
> $$
> \textsf{MaxScore}(k) = \begin{cases} 0 & \text{if } k > n\\ \max\big\{\textsf{MaxScore}(k+1),\ \mathit{Score}[k] + \textsf{MaxScore}(k')\big\} & \text{if } k\le n\end{cases}
> $$
> **Memoization.** An array $\textsf{MaxScore}[1\,..\,n+1]$.
>
> **Evaluation order.** $k$ from $n+1$ down to 1: both references have larger indices.
>
> **Time.** $n + 1$ entries, $O(1)$ each: **$O(n)$**.

The greedy idea "dance to the song with the highest score first" fails: with $\mathit{Score} = [3, 2, 2]$ and $\mathit{Wait} = [2, 0, 0]$, the 3 blocks both 2s, and $2 + 2 = 4$ is better.

> [!exam] How this is graded
> **3** for $\textsf{MaxScore}(k)$ as a function of the suffix of songs, with "free to dance to song $k$" — that condition is what makes the value depend only on $k$; **4** for the recurrence (the cap at $n + 1$ is the base-case detail); **3** for the array, the order and $O(n)$. [[0-toolkit/06-how-exams-are-graded#12-dynamic-programming|§12]].

## Problem 2 — Voting districts

> [!question] Problem 2
> $n$ people live at addresses $1, 2, \ldots, n$ of Purple Street, which must be partitioned into voting districts. Each district is a contiguous interval of addresses $i, i+1, \ldots, j$ for some $1\le i < j\le n$; every address lies in exactly one district, and every district contains between $k$ and $2k$ addresses, for a given positive integer $k$. A district is **good** if more than half of its residents voted for Oceania in the previous election. Given $k$ and a boolean array $\mathit{GoodVote}[1\,..\,n]$ ($\textsf{True}$ for a vote for Oceania), describe an algorithm to find the largest possible number of good districts in a legal partition, and analyze it in terms of $n$ and $k$. You may assume that a legal partition exists.
>
> In the handout's example, $k = 2$ and the 22 votes OXO XOXX OXO XXX OO OXO XXXX (O for Oceania, X for Eurasia) are partitioned as shown, into 4 good and 3 bad districts.

Ask about the first district of the rest of the street: it starts at address $i$, and its length $\ell$ is one of $k, \ldots, 2k$. The problem's "$i < j$" also forbids districts of a single address, which matters only when $k = 1$; so let $\ell_{\min} = \max\{k, 2\}$.

To test a district in $O(1)$ time, precompute the prefix counts $\mathit{Votes}[j] = \lvert\{m\le j \mid \mathit{GoodVote}[m]\}\rvert$ for $0\le j\le n$, in $O(n)$ time. Then $i\,..\,j$ is good exactly when $2\,(\mathit{Votes}[j] - \mathit{Votes}[i-1]) > j - i + 1$; write $\textsf{Good}(i, j)$ for 1 if it is and 0 otherwise.

> [!key] Answer
> **Function.** For $1\le i\le n+1$, let $\textsf{MaxGood}(i)$ be the largest number of good districts in a legal partition of the addresses $i, \ldots, n$ — every district an interval of $\ell_{\min}$ to $2k$ addresses — or $-\infty$ if no such partition exists. We need $\textsf{MaxGood}(1)$.
>
> **Recurrence.**
> $$
> \textsf{MaxGood}(i) = \begin{cases} 0 & \text{if } i = n + 1\\ \max\limits_{\ell_{\min}\le\ell\le\min\{2k,\, n-i+1\}}\big(\textsf{Good}(i, i + \ell - 1) + \textsf{MaxGood}(i + \ell)\big) & \text{if } i\le n\end{cases}
> $$
> with $\max\varnothing = -\infty$ (when $n - i + 1 < \ell_{\min}$).
>
> **Memoization.** An array $\textsf{MaxGood}[1\,..\,n+1]$, plus the prefix counts $\mathit{Votes}[0\,..\,n]$.
>
> **Evaluation order.** $i$ from $n+1$ down to 1: every reference is to a larger index.
>
> **Time.** $O(n)$ for the prefix counts; $n + 1$ entries with at most $k + 1$ candidates each, $O(1)$ per candidate: **$O(nk)$**.

The $-\infty$ matters: a non-empty suffix with fewer than $\ell_{\min}$ addresses cannot be partitioned, and without $-\infty$ the recurrence would happily end a partition there. On the handout's street the algorithm returns **4**: the partition in the figure is already optimal.

> [!exam] How this is graded
> **3** for $\textsf{MaxGood}(i)$ described as a function of the suffix of addresses, including what happens when no legal partition exists; **4** for the recurrence — the range of $\ell$ and the $-\infty$ are the details; **3** for the array, the order and $O(nk)$ — in terms of both parameters, as the problem asks. Recounting the votes of every district without prefix counts gives $O(nk^2)$, which is correct but slower. [[0-toolkit/06-how-exams-are-graded#12-dynamic-programming|§12]].

## Problem 3 — The most even partition into k intervals

> [!question] Problem 3
> Split an array $A[1\,..\,n]$ of integers into $k$ contiguous intervals so as to minimize the **cost**: the largest, over the $k$ intervals, of the sum of the values in the interval. Describe and analyze an algorithm to compute the minimum cost of a partition of $A$ into $k$ intervals, given $A$ and $k$. For example, for $A = [1, 6, -1, 8, 0, 3, 3, 9, 8, 8, 7, 4, 9, 8, 9, 4, 8, 4, 8, 2]$ and $k = 3$, the answer is 37, the cost of the partition into $A[1\,..\,9]$, $A[10\,..\,14]$ and $A[15\,..\,20]$, whose sums are 37, 36 and 35.

Ask where the first interval ends. The rest is a partition of a suffix into one fewer interval — so the function needs two parameters: where the suffix starts, and how many intervals it must be cut into.

Precompute prefix sums $\mathit{Pre}[j] = A[1] + \cdots + A[j]$ (with $\mathit{Pre}[0] = 0$) in $O(n)$ time, so that $\textsf{Sum}(i, j) = \mathit{Pre}[j] - \mathit{Pre}[i-1]$ costs $O(1)$.

> [!key] Answer
> **Function.** For $1\le i\le n$ and $1\le m\le k$, let $\textsf{MinCost}(i, m)$ be the smallest cost of a partition of the suffix $A[i\,..\,n]$ into $m$ non-empty contiguous intervals — the smallest possible maximum interval sum — or $\infty$ if the suffix has fewer than $m$ elements. We need $\textsf{MinCost}(1, k)$.
>
> **Recurrence.**
> $$
> \textsf{MinCost}(i, m) = \begin{cases} \textsf{Sum}(i, n) & \text{if } m = 1\\ \min\limits_{i\le j\le n - m + 1}\max\big\{\textsf{Sum}(i, j),\ \textsf{MinCost}(j+1, m-1)\big\} & \text{if } m\ge 2\end{cases}
> $$
> with $\min\varnothing = \infty$. The first interval is $A[i\,..\,j]$; it must leave at least $m - 1$ elements for the other intervals.
>
> **Memoization.** An array $\textsf{MinCost}[1\,..\,n, 1\,..\,k]$, plus the prefix sums $\mathit{Pre}[0\,..\,n]$.
>
> **Evaluation order.** $m$ from 1 up to $k$ in the outer loop; $i$ in any order in the inner loop (column $m$ reads only column $m - 1$).
>
> **Time.** $nk$ entries, each a minimum over $O(n)$ values of $j$: **$O(n^2k)$**.

The values may be negative, so a longer interval does not always have a larger sum; the recurrence does not care, because it tries every $j$. On the example it returns 37.

> [!exam] How this is graded
> **3** for $\textsf{MinCost}(i, m)$ with both parameters described — "the cost for the rest of the array" without the number of intervals is not usable; **4** for the recurrence, including the range of $j$ (or the $\infty$ that handles a suffix too short); **3** for the array, "$m$ outer" and $O(n^2k)$. [[0-toolkit/06-how-exams-are-graded#12-dynamic-programming|§12]].

## Problem 4 — The longest mostly odd increasing subsequence

> [!question] Problem 4
> A sequence of integers is **mostly odd** if strictly more than half of its elements are odd. Describe an algorithm that computes the length of the longest mostly odd increasing subsequence of an array $A[1\,..\,n]$ (assume that one exists). For example, for $A = [2, 4, 6, 8, 10, 1, 7, 12, 13, 14, 19, 25, 16, 18, 20, 22, 24]$ the answer is 7, the length of the mostly odd increasing subsequence $[4, 6, 7, 13, 14, 19, 25]$; the increasing subsequence $[2, 4, 6, 7, 12, 13, 14, 19, 20, 22, 24]$ is longer but not mostly odd.

*Related: [[2-algorithms/03-dynamic-programming#36-longest-increasing-subsequence|longest increasing subsequence, §3.6]], [[concepts/longest-increasing-subsequence]]*

"Mostly odd" is a property of the *whole* subsequence, so the usual $\textsf{LISfirst}(i)$ cannot check it. But for a fixed length it becomes an optimization: a sequence is mostly odd exactly when (number of odd elements) $-$ (number of even elements) $\ge 1$. So fix the length and maximize that **balance**. Write $p(i) = +1$ if $A[i]$ is odd and $p(i) = -1$ if it is even.

> [!key] Answer
> **Function.** For $1\le i\le n$ and $1\le\ell\le n$, let $\textsf{MaxBalance}(i, \ell)$ be the largest value of (number of odd elements) $-$ (number of even elements) over all increasing subsequences of $A[i\,..\,n]$ that start with $A[i]$ and have exactly $\ell$ elements, or $-\infty$ if there is none. The answer is the largest $\ell$ such that $\textsf{MaxBalance}(i, \ell)\ge 1$ for some $i$.
>
> **Recurrence.**
> $$
> \textsf{MaxBalance}(i, \ell) = \begin{cases} p(i) & \text{if } \ell = 1\\ p(i) + \max\limits_{\substack{i < j\le n\\ A[j] > A[i]}}\textsf{MaxBalance}(j, \ell - 1) & \text{if } \ell\ge 2\end{cases}
> $$
> with $\max\varnothing = -\infty$: after $A[i]$, the subsequence continues with some larger $A[j]$ further right.
>
> **Memoization.** An array $\textsf{MaxBalance}[1\,..\,n, 1\,..\,n]$.
>
> **Evaluation order.** $\ell$ from 1 up to $n$ in the outer loop; $i$ in any order in the inner loop (column $\ell$ reads only column $\ell - 1$). Then scan the table for the largest $\ell$ with an entry $\ge 1$.
>
> **Time.** $n^2$ entries, $O(n)$ each, and an $O(n^2)$ scan: **$O(n^3)$**.

Why a fixed length is needed: maximizing the balance alone finds the "most odd" subsequence, not the longest mostly odd one, and maximizing the length alone ignores the parity condition. With the length as a parameter, both are under control. On the example the algorithm returns **7**.

> [!trap] Two tempting shortcuts that fail
> Restricting to the odd elements finds an increasing subsequence that is all odd, but a longer mostly odd one may mix in some even elements: in the example the best all-odd one, $[1, 7, 13, 19, 25]$, has 5 elements, and the answer has 7, three of them even. And the longest increasing subsequence need not be mostly odd, nor contain the answer.

> [!exam] How this is graded
> **3** for $\textsf{MaxBalance}(i, \ell)$ with both parameters and the "starts with $A[i]$" condition described; **4** for the recurrence and the way the answer is read off the table; **3** for the array, "$\ell$ outer" and $O(n^3)$. A function such as "the longest mostly odd increasing subsequence starting at $A[i]$" cannot be computed from the same function on later starting points — how many even elements the tail may contain depends on how many odd ones came before — so it leads to no correct recurrence. [[0-toolkit/06-how-exams-are-graded#12-dynamic-programming|§12]].

### Sources for this page
Problems from the CS/ECE 374 A (Fall 2026) "Dynamic Programming Practice Questions" handout, paraphrased; no official solutions were posted, so the solutions are ours. Checked by `tools/checks/exams_mt2.py` (dynamic-programming practice section): every recurrence is run in the stated evaluation order with a table that fails on any read before write, and compared with exhaustive search — all subsets of songs, all legal partitions of the street, all ways to cut the array into $k$ non-empty intervals, all subsequences — on 300 random inputs each; the handout's partition (22 addresses, 4 good and 3 bad districts) and its optimality; the example cost 37 and its three sums; the example answer 7 and both of the handout's subsequences.
