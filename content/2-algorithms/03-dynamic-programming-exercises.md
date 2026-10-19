---
title: "Chapter 3 exercises — Dynamic Programming"
description: "Solutions to Exercises 3.1–3.10 of Erickson's Algorithms in the dynamic-programming rubric's format: change-making where greedy fails, text-segmentation variants, maximum subarray sums and products and five variants, optimal subsequences and supersequences, shuffles, counting and costing subsequence occurrences, forward-and-backward substrings, palindromes, and back-and-forth subsequences."
tags: [exercises, algorithms, dynamic-programming, midterm-2]
---

*Solved exercises for [[2-algorithms/03-dynamic-programming|Chapter 3]] · book pp. 123–130 · statements paraphrased; see the book for the originals*

These are Exercises 3.1–3.10, the sequence and array problems that open the chapter's exercises, with most of their parts. Skipped: 3.7(c) and 3.9(f), which are marked ♥ (particularly challenging); 3.5(i), the longest common increasing subsequence, is omitted until the related homework is due. Every [[concepts/dynamic-programming|dynamic program]] is written the way the rubric of [[2-algorithms/03-dynamic-programming#34-the-pattern-smart-recursion|§3.4]] grades it: a named function with an English description of its value and the call that answers the problem, the recurrence with its base cases, the [[concepts/memoization|memoization]] structure, the evaluation order, and the running time. Three of the book's examples are wrong as printed (in 3.6(b), 3.9(e) and 3.10) and 3.7(d) has its indices swapped; each is pointed out where it occurs. Write your own answer before opening a solution.

## Exercise 3.1 — Making change in Nadiria

> [!question] Exercise 3.1 (book p. 123)
> The bills of Nadiria are worth 1, 4, 7, 13, 28, 52, 91 and 365 Dream-Dollars, and a cashier must give change with as few bills as possible.
>
> (a) The **greedy** algorithm repeatedly hands over the largest bill that does not exceed the amount still owed; for 122 it pays $91 + 28 + 1 + 1 + 1$. Find an amount for which greedy uses more bills than necessary. (The book suggests writing a small program.)
>
> (b) Describe and analyze a recursive algorithm that computes, given an integer $k$, the minimum number of bills worth $k$ in total. It only has to be correct, not fast.
>
> (c) Describe a dynamic programming algorithm for the same problem. This one has to be fast.

### (a) A counterexample to greed

> [!hint]- Hint
> Greedy is optimal for every amount below 365, so a counterexample uses the 365 bill. Try sums of a few 91s and 52s just above 365.

> [!solution]- Solution
> For 416, greedy takes 365 and then pays the remaining 51 as $28 + 13 + 7 + 1 + 1 + 1$: seven bills. But $416 = 91 + 91 + 91 + 91 + 52$ takes five. Comparing greedy with the dynamic program of part (c) on every amount shows that 416 is the *smallest* amount where greedy fails; the next is $455 = 5\cdot 91$, which greedy also pays with seven bills ($365 + 52 + 28 + 7 + 1 + 1 + 1$). This is the warning of [[2-algorithms/03-dynamic-programming#35-warning-greed-is-stupid|§3.5]] in miniature.
>
> **Answer.** 416: greedy uses 7 bills ($365+28+13+7+1+1+1$), the optimum is 5 ($4\cdot 91 + 52$).

### (b) A recursive algorithm

> [!hint]- Hint
> Some bill is handed over first. Try each of the eight denominations and recurse on what is left.

> [!solution]- Solution
> Let $D = \{1, 4, 7, 13, 28, 52, 91, 365\}$.
>
> **Function.** For every integer $k\ge 0$, let $\textsf{MinBills}(k)$ be the minimum number of bills from $D$ whose values add up to exactly $k$. We need $\textsf{MinBills}(k)$.
>
> **Recurrence.**
> $$
> \textsf{MinBills}(k) = \begin{cases} 0 & \text{if } k = 0\\ 1 + \min\{\textsf{MinBills}(k-d) \mid d\in D,\ d\le k\} & \text{if } k\ge 1\end{cases}
> $$
> The minimum is over a non-empty set because $1\in D$. An optimal payment of $k\ge 1$ contains some bill $d\le k$, and its other bills pay $k-d$, so there are at least $\textsf{MinBills}(k-d)$ of them; conversely, adding a bill $d$ to an optimal payment of $k-d$ pays $k$.
>
> **Running time.** Evaluated by plain recursion, the number of calls satisfies $T(0) = 1$ and $T(k) = 1 + \sum_{d\in D,\, d\le k} T(k-d)$. $T$ is non-decreasing, so $T(k)\ge T(k-1) + T(k-4)\ge 2\,T(k-4)$ for $k\ge 4$, and $T(k)\ge 2^{\lfloor k/4\rfloor}$: exponential. More precisely, $T(k) = \Theta(r^k)$ where $r\approx 1.449$ is the root of the characteristic equation $\sum_{d\in D} r^{-d} = 1$. Each call does $O(1)$ work besides its recursive calls.
>
> **Answer.** The recursion for $\textsf{MinBills}(k)$ is correct but takes $\Theta(r^k)$ time, $r\approx 1.449$.

### (c) Dynamic programming

> [!hint]- Hint
> $\textsf{MinBills}(k)$ depends only on smaller amounts.

> [!solution]- Solution
> Memoize the recurrence of part (b).
>
> - **Memoization:** an array $\mathit{MinBills}[0\,..\,k]$.
> - **Evaluation order:** entry $t$ reads only entries $t-d < t$, so fill $t$ from $0$ up to $k$.
> - **Time:** $k+1$ entries, each a minimum of at most $\lvert D\rvert = 8$ terms: $O(k)$ time. (Only the last 365 entries are ever read again, so constant space suffices; for an arbitrary set of denominations the time is $O(k\lvert D\rvert)$.)
>
> ```text
> FastMinBills(k):
>     MinBills[0] ← 0
>     for t ← 1 to k
>         MinBills[t] ← ∞
>         for each d ∈ {1, 4, 7, 13, 28, 52, 91, 365}
>             if d ≤ t and 1 + MinBills[t − d] < MinBills[t]
>                 MinBills[t] ← 1 + MinBills[t − d]
>     return MinBills[k]
> ```
>
> $O(k)$ is linear in the *value* $k$ and exponential in its number of digits — a pseudo-polynomial bound, like the $O(nT)$ of subset sum in [[2-algorithms/03-dynamic-programming#38-subset-sum|§3.8]].
>
> **Answer.** $\textsf{MinBills}(k)$ from an array filled left to right, in $O(k)$ time.

## Exercise 3.2 — Text segmentation variants

> [!question] Exercise 3.2 (book p. 124)
> A subroutine $\textsf{IsWord}$ takes an array of characters and returns True if and only if that string is a "word". Describe efficient algorithms for the following problems, and bound the number of calls to $\textsf{IsWord}$.
>
> (a) Given $A[1\,..\,n]$, compute the number of partitions of $A$ into words. For `ARTISTOIL` the answer is 2: ARTIST·OIL and ART·IS·TOIL.
>
> (b) Given $A[1\,..\,n]$ and $B[1\,..\,n]$, decide whether $A$ and $B$ can be partitioned into words **at the same indices**. For example, `BOTHEARTHANDSATURNSPIN` and `PINSTARTRAPSANDRAGSLAP` can: BOT·HEART·HAND·SAT·URNS·PIN and PIN·START·RAPS·AND·RAGS·LAP.
>
> (c) Given $A[1\,..\,n]$ and $B[1\,..\,n]$, compute the number of ways to partition $A$ and $B$ into words at the same indices.

### (a) Counting segmentations

> [!hint]- Hint
> Reuse the suffix formulation $\textsf{Splittable}(i)$ of [[2-algorithms/03-dynamic-programming#33-interpunctio-verborum-redux|§3.3]]: the first word is $A[i\,..\,j]$ for some $j$. To count, add instead of "or".

> [!solution]- Solution
> **Function.** For $1\le i\le n+1$, let $\textsf{NumSplits}(i)$ be the number of partitions of the suffix $A[i\,..\,n]$ into words (the empty suffix has exactly one, the empty partition). We need $\textsf{NumSplits}(1)$.
>
> **Recurrence.** A partition of $A[i\,..\,n]$ is a first word $A[i\,..\,j]$ followed by a partition of $A[j+1\,..\,n]$, and different first words give different partitions. So $\textsf{NumSplits}(n+1) = 1$ and, for $i\le n$,
> $$
> \textsf{NumSplits}(i) = \sum_{\substack{i\le j\le n\\ \textsf{IsWord}(A[i\,..\,j])}} \textsf{NumSplits}(j+1).
> $$
>
> - **Memoization:** an array $\mathit{NumSplits}[1\,..\,n+1]$.
> - **Evaluation order:** $i$ from $n+1$ down to $1$ (entry $i$ reads only entries $j+1 > i$).
> - **Time:** entry $i$ calls $\textsf{IsWord}$ once on each of the $n-i+1$ prefixes of $A[i\,..\,n]$: exactly $n(n+1)/2 = O(n^2)$ calls, and $O(n^2)$ other work.
>
> **Answer.** $\textsf{NumSplits}(1)$, with $n(n+1)/2$ calls to $\textsf{IsWord}$.

### (b) and (c) Two strings cut at the same places

> [!hint]- Hint
> Cut both strings after the same index $j$: the first words are $A[i\,..\,j]$ and $B[i\,..\,j]$, and the rest must again be cut at the same places.

> [!solution]- Solution
> **(b) Function.** For $1\le i\le n+1$, let $\textsf{SameSplit}(i)$ be True if and only if the suffixes $A[i\,..\,n]$ and $B[i\,..\,n]$ can be partitioned into words at the same indices. We need $\textsf{SameSplit}(1)$.
>
> **Recurrence.** $\textsf{SameSplit}(n+1) = \textsf{True}$ and, for $i\le n$,
> $$
> \textsf{SameSplit}(i) = \bigvee_{j=i}^{n}\Big(\textsf{IsWord}(A[i\,..\,j]) \land \textsf{IsWord}(B[i\,..\,j]) \land \textsf{SameSplit}(j+1)\Big).
> $$
>
> **(c) Function.** For $1\le i\le n+1$, let $\textsf{NumSameSplits}(i)$ be the number of ways to partition $A[i\,..\,n]$ and $B[i\,..\,n]$ into words at the same indices. We need $\textsf{NumSameSplits}(1)$.
>
> **Recurrence.** $\textsf{NumSameSplits}(n+1) = 1$ and, for $i\le n$,
> $$
> \textsf{NumSameSplits}(i) = \sum_{\substack{i\le j\le n\\ \textsf{IsWord}(A[i\,..\,j])\,\land\,\textsf{IsWord}(B[i\,..\,j])}} \textsf{NumSameSplits}(j+1).
> $$
>
> - **Memoization:** arrays $\mathit{SameSplit}[1\,..\,n+1]$ and $\mathit{NumSameSplits}[1\,..\,n+1]$.
> - **Evaluation order:** $i$ from $n+1$ down to $1$.
> - **Time:** at most two calls to $\textsf{IsWord}$ per pair $i\le j$, so at most $n(n+1) = O(n^2)$ calls, and $O(n^2)$ other work.
>
> **Answer.** (b) $\textsf{SameSplit}(1)$ and (c) $\textsf{NumSameSplits}(1)$, each with $O(n^2)$ calls to $\textsf{IsWord}$.

## Exercise 3.3 — Maximum subarray sum and product

> [!question] Exercise 3.3 (book p. 124)
> The array $A[1\,..\,n]$ holds numbers that may be positive, negative or zero, and are not necessarily integers. Comparing, adding or multiplying two numbers takes $O(1)$ time.
>
> (a) Describe and analyze an algorithm that finds the largest sum of a contiguous subarray $A[i\,..\,j]$.
>
> (b) Describe and analyze an algorithm that finds the largest product of a contiguous subarray $A[i\,..\,j]$.
>
> For $[-6, 12, -7, 0, 14, -7, 5]$ the answers are $19 = 12 - 7 + 0 + 14$ and $504 = (-6)\cdot 12\cdot(-7)$. For $[-374]$ they are 0 and 1: the empty subarray counts, with sum 0 and product 1.

### (a) Largest sum

> [!hint]- Hint
> Every subarray is a suffix of some prefix $A[1\,..\,j]$. Get the best suffix of $A[1\,..\,j]$ from the best suffix of $A[1\,..\,j-1]$.

> [!solution]- Solution
> **Function.** For $0\le j\le n$, let $\textsf{MaxSuffixSum}(j)$ be the largest sum of a possibly empty suffix $A[i\,..\,j]$, $1\le i\le j+1$, of the prefix $A[1\,..\,j]$. Every subarray is such a suffix for some $j$, so we need $\max_{0\le j\le n}\textsf{MaxSuffixSum}(j)$.
>
> **Recurrence.** A suffix of $A[1\,..\,j]$ is either empty or a suffix of $A[1\,..\,j-1]$ followed by $A[j]$:
> $$
> \textsf{MaxSuffixSum}(j) = \begin{cases} 0 & \text{if } j = 0\\ \max\{0,\ \textsf{MaxSuffixSum}(j-1) + A[j]\} & \text{if } j\ge 1\end{cases}
> $$
>
> - **Memoization:** an array $\mathit{MaxSuffixSum}[0\,..\,n]$ (or one variable: entry $j$ reads only entry $j-1$).
> - **Evaluation order:** $j$ from $0$ up to $n$, keeping a running maximum.
> - **Time:** $n+1$ entries, $O(1)$ each: $O(n)$.
>
> This is Kadane's algorithm. On the example, $\textsf{MaxSuffixSum}(1), \dots, \textsf{MaxSuffixSum}(7)$ are $0, 12, 5, 5, 19, 12, 17$, with maximum 19.
>
> **Answer.** $\max_j \textsf{MaxSuffixSum}(j)$, in $O(n)$ time.

### (b) Largest product

> [!hint]- Hint
> Multiplying by a negative number turns the smallest product into the largest. Keep both the largest and the smallest suffix product.

> [!solution]- Solution
> **Functions.** For $0\le j\le n$, let $\textsf{MaxSuffixProd}(j)$ and $\textsf{MinSuffixProd}(j)$ be the largest and the smallest product of a possibly empty suffix $A[i\,..\,j]$ of $A[1\,..\,j]$ (the empty product is 1). We need $\max_{0\le j\le n}\textsf{MaxSuffixProd}(j)$.
>
> **Recurrence.** $\textsf{MaxSuffixProd}(0) = \textsf{MinSuffixProd}(0) = 1$ and, for $j\ge 1$,
> $$
> \begin{aligned}
> \textsf{MaxSuffixProd}(j) &= \max\{1,\ A[j]\cdot\textsf{MaxSuffixProd}(j-1),\ A[j]\cdot\textsf{MinSuffixProd}(j-1)\}\\
> \textsf{MinSuffixProd}(j) &= \min\{1,\ A[j]\cdot\textsf{MaxSuffixProd}(j-1),\ A[j]\cdot\textsf{MinSuffixProd}(j-1)\}
> \end{aligned}
> $$
> The non-empty suffix products of $A[1\,..\,j]$ are the numbers $A[j]\cdot p$, where $p$ ranges over the suffix products of $A[1\,..\,j-1]$. Multiplying by $A[j]\ge 0$ preserves order and multiplying by $A[j] < 0$ reverses it, so the extremes of $A[j]\cdot p$ come from the extremes of $p$.
>
> - **Memoization:** two arrays indexed $0\,..\,n$ (or two variables).
> - **Evaluation order:** $j$ from $0$ up to $n$, both functions at each $j$.
> - **Time:** $O(n)$.
>
> **Traps.** Keeping only the maximum fails on $[-2, 3, -4]$: it reports 3, but the answer is 24. Integer intuition ("multiply the whole zero-free stretch, then drop a negative end") fails for fractions: for $[3, \tfrac14, 3]$ the whole array has product $\tfrac94$, but the answer is 3.
>
> **Answer.** $\max_j\textsf{MaxSuffixProd}(j)$, in $O(n)$ time.

## Exercise 3.4 — Maximum subarray variants

> [!question] Exercise 3.4 (book p. 125)
> The input is an array $A[1\,..\,n]$ of real numbers (of any sign) and possibly an integer $X\ge 0$. Describe and analyze algorithms that find a contiguous subarray with the largest sum, where:
>
> (a) **wrapping around:** $A$ is circular, so a contiguous subarray is an interval $A[i\,..\,j]$ or a suffix followed by a prefix, $A[i\,..\,n]\cdot A[1\,..\,j]$;
>
> (b) **long subarrays only:** the subarray must have length at least $X$ (assume $X\le n$);
>
> (c) **short subarrays only:** the subarray must have length at most $X$;
>
> (d) **The Price Is Right:** the sum must be at most $X$;
>
> (e) the same as (d), but faster, when every entry of $A$ is non-negative.

All five solutions use the prefix sums $P[0] = 0$ and $P[j] = P[j-1] + A[j]$, so that $A[i\,..\,j]$ has sum $P[j] - P[i-1]$, and allow the empty subarray (sum 0) as in Exercise 3.3 wherever its length is permitted (in (b) only when $X = 0$). They compute the largest sum; recording where the maximum is attained gives the subarray itself.

### (a) Wrapping around

> [!hint]- Hint
> A wrap-around subarray is everything except an ordinary interval.

> [!solution]- Solution
> A wrap-around subarray $A[i\,..\,n]\cdot A[1\,..\,j]$ (with $j < i$) is the complement of the interval $A[j+1\,..\,i-1]$, and every interval, empty or not, arises this way. So the best wrap-around sum is the total minus the *smallest* interval sum, and the smallest interval sum of $A$ is minus the largest interval sum of $-A$. With $\textsf{MaxSubarray}$ the algorithm of Exercise 3.3(a):
> $$
> \text{answer} = \max\Big\{\textsf{MaxSubarray}(A),\ \ \sum_{t=1}^{n} A[t] + \textsf{MaxSubarray}(-A)\Big\}.
> $$
> Two runs of Kadane's algorithm and one sum: $O(n)$ time.
>
> **Answer.** $\max\{\textsf{MaxSubarray}(A),\ \sum_t A[t] + \textsf{MaxSubarray}(-A)\}$, in $O(n)$ time.

### (b) Long subarrays only

> [!hint]- Hint
> A subarray of length at least $X$ that ends at $A[j]$ is the block of the last $X$ entries, $A[j-X+1\,..\,j]$, preceded by a possibly empty suffix of $A[1\,..\,j-X]$.

> [!solution]- Solution
> **Function.** For $X\le j\le n$, let $\textsf{LongEnd}(j)$ be the largest sum of a subarray of length at least $X$ that ends at index $j$. We need $\max_{X\le j\le n}\textsf{LongEnd}(j)$.
>
> **Recurrence.** By the hint, with $\textsf{MaxSuffixSum}$ from Exercise 3.3(a),
> $$
> \textsf{LongEnd}(j) = \big(P[j] - P[j-X]\big) + \textsf{MaxSuffixSum}(j-X).
> $$
>
> - **Memoization:** arrays $P[0\,..\,n]$ and $\mathit{MaxSuffixSum}[0\,..\,n]$; $\textsf{LongEnd}(j)$ is then a lookup.
> - **Evaluation order:** both arrays left to right, then $j$ from $X$ up to $n$.
> - **Time:** $O(n)$.
>
> (For $X = 0$ this is Exercise 3.3(a) again.)
>
> **Answer.** $\max_{X\le j\le n}\big(P[j]-P[j-X] + \textsf{MaxSuffixSum}(j-X)\big)$, in $O(n)$ time.

### (c) Short subarrays only

> [!hint]- Hint
> The best subarray of length at most $X$ ending at $j$ has sum $P[j]$ minus the smallest of $P[j-X], \dots, P[j]$. So you need the minimum of every window of $X+1$ consecutive prefix sums — in $O(n)$ total time, cut the indices into blocks of $X+1$.

> [!solution]- Solution
> For each $j$, the subarrays of length at most $X$ that end at $j$ are $A[t+1\,..\,j]$ for $\max(0, j-X)\le t\le j$ (with $t = j$ the empty one), and their sums are $P[j] - P[t]$. So
> $$
> \text{answer} = \max_{0\le j\le n}\big(P[j] - \textsf{WinMin}(j)\big),
> $$
> where $\textsf{WinMin}(j) = \min\{P[t] \mid \max(0, j-X)\le t\le j\}$ is the minimum of a window of at most $X+1$ consecutive prefix sums.
>
> **All window minima in $O(n)$ time.** Cut the indices $0, 1, \dots, n$ into consecutive blocks of $w = X+1$ indices: $\{0, \dots, X\}$, $\{X+1, \dots, 2X+1\}$, and so on. For each index $t$ define
> - $\textsf{PreMin}(t)$, the minimum of $P$ from the first index of $t$'s block up to $t$: it is $P[t]$ if $t$ starts its block, and $\min\{\textsf{PreMin}(t-1), P[t]\}$ otherwise;
> - $\textsf{SufMin}(t)$, the minimum of $P$ from $t$ up to the last index of $t$'s block: it is $P[t]$ if $t$ ends its block or $t = n$, and $\min\{\textsf{SufMin}(t+1), P[t]\}$ otherwise.
>
> For $j\ge X$ the window $\{j-X, \dots, j\}$ has exactly $w$ indices, so it is either a whole block or the end of one block followed by the beginning of the next; either way $\textsf{WinMin}(j) = \min\{\textsf{SufMin}(j-X), \textsf{PreMin}(j)\}$. For $j < X$ the window $\{0, \dots, j\}$ is the beginning of the first block, and $\textsf{WinMin}(j) = \textsf{PreMin}(j)$.
>
> - **Memoization:** arrays $P$, $\mathit{PreMin}$ and $\mathit{SufMin}$, each indexed $0\,..\,n$.
> - **Evaluation order:** $P$ and $\mathit{PreMin}$ left to right, $\mathit{SufMin}$ right to left, then one pass over $j$.
> - **Time:** $O(n)$, independent of $X$. (A monotone deque also gives $O(n)$; trying every length up to $X$ for every $j$ gives a simpler $O(nX)$ algorithm.)
>
> **Answer.** $\max_j \big(P[j] - \textsf{WinMin}(j)\big)$, in $O(n)$ time.

### (d) The Price Is Right

> [!hint]- Hint
> For a fixed end $j$ you want the smallest prefix sum $P[t]$, $t\le j$, that is still at least $P[j]-X$: a successor query in a balanced search tree.

> [!solution]- Solution
> The sum of $A[t+1\,..\,j]$ is $P[j] - P[t]$, which is at most $X$ if and only if $P[t]\ge P[j] - X$. For a fixed $j$ the best start therefore has the **smallest** $P[t]$ with $t\le j$ and $P[t]\ge P[j]-X$ — the successor of $P[j]-X$ among $P[0], \dots, P[j]$. Scan $j$ from left to right, keeping the prefix sums seen so far in a balanced binary search tree:
>
> ```text
> PriceIsRight(A[1 .. n], X):
>     best ← 0; P ← 0
>     T ← a balanced binary search tree containing only 0
>     for j ← 1 to n
>         P ← P + A[j]
>         insert P into T
>         q ← the smallest key in T that is ≥ P − X     ⟨⟨exists: P itself, as X ≥ 0⟩⟩
>         best ← max{best, P − q}
>     return best
> ```
>
> Each of the $n$ iterations does one insertion and one successor query, $O(\log n)$ time each: $O(n\log n)$ in all.
>
> **Answer.** Prefix sums in a balanced search tree with one successor query per $j$, in $O(n\log n)$ time.

### (e) Non-negative entries

> [!hint]- Hint
> With non-negative entries the prefix sums are sorted, so the best start for $j$ never moves left as $j$ grows.

> [!solution]- Solution
> If every $A[t]\ge 0$, then $P$ is non-decreasing, so the starts $t\le j$ with $P[j]-P[t]\le X$ form an interval $\{t_j, \dots, j\}$, and the best of them is the smallest, $t_j$. As $j$ grows, $P[j]-X$ grows, so $t_j$ never decreases: two pointers suffice.
>
> ```text
> PriceIsRightNonneg(A[1 .. n], X):
>     compute the prefix sums P[0 .. n]
>     t ← 0; best ← 0
>     for j ← 0 to n
>         while P[j] − P[t] > X
>             t ← t + 1
>         best ← max{best, P[j] − P[t]}
>     return best
> ```
>
> The inner loop stops at the latest when $t = j$ (difference $0\le X$), and $t$ increases at most $n$ times in total: $O(n)$ time.
>
> **Answer.** Two pointers over the prefix sums, in $O(n)$ time.

## Exercise 3.5 — Optimal subsequences

> [!question] Exercise 3.5 (book pp. 125–126)
> A **subsequence** keeps some elements of a sequence in their original order, not necessarily contiguous. Describe efficient algorithms to compute:
>
> (a) the length of a longest **common subsequence** of two arrays $A[1\,..\,m]$ and $B[1\,..\,n]$;
>
> (b) the length of a shortest **common supersequence** of $A[1\,..\,m]$ and $B[1\,..\,n]$ — a sequence that contains both as subsequences;
>
> (c) the length of a longest **bitonic** subsequence of an integer array $A[1\,..\,n]$, where $X[1\,..\,\ell]$ is bitonic if, for some $1 < i < \ell$, the prefix $X[1\,..\,i]$ is increasing and the suffix $X[i\,..\,\ell]$ is decreasing;
>
> (d) the length of a longest **oscillating** subsequence, where $X$ is oscillating if $X[i] < X[i+1]$ for every even $i$ and $X[i] > X[i+1]$ for every odd $i$ — that is, $X[1] > X[2] < X[3] > X[4] < \cdots$;
>
> (e) the length of a shortest oscillating **supersequence** of $A$;
>
> (f) the length of a longest **convex** subsequence: $2X[i] < X[i-1] + X[i+1]$ for all $1 < i < \ell$;
>
> (g) the length of a longest **weakly increasing** subsequence: $2X[i] > X[i-1] + X[i-2]$ for all $i > 2$;
>
> (h) the length of a longest **double-increasing** subsequence: $X[i] > X[i-2]$ for all $i > 2$ (a perfect shuffle of two increasing sequences).
>
> The book's hint: exactly one of these problems can be solved in $O(n)$ time by a greedy algorithm. Part (i), the longest common increasing subsequence of two arrays, is omitted until the related homework is due.

### (a) Longest common subsequence

> [!hint]- Hint
> Look at the first elements of the two suffixes: one of them is unused, or they are matched to each other.

> [!solution]- Solution
> **Function.** For $1\le i\le m+1$ and $1\le j\le n+1$, let $\textsf{LCS}(i, j)$ be the length of a longest common subsequence of the suffixes $A[i\,..\,m]$ and $B[j\,..\,n]$. We need $\textsf{LCS}(1, 1)$.
>
> **Recurrence.** $\textsf{LCS}(i, j) = 0$ if $i > m$ or $j > n$; otherwise
> $$
> \textsf{LCS}(i, j) = \max\begin{cases}
> \textsf{LCS}(i+1, j)\\
> \textsf{LCS}(i, j+1)\\
> 1 + \textsf{LCS}(i+1, j+1) & \text{only if } A[i] = B[j]
> \end{cases}
> $$
> A longest common subsequence of the two suffixes does not use $A[i]$, or does not use $B[j]$, or uses both — and then both are matched to its first element, so $A[i] = B[j]$, and the rest is a common subsequence of $A[i+1\,..\,m]$ and $B[j+1\,..\,n]$.
>
> - **Memoization:** an array $\mathit{LCS}[1\,..\,m+1, 1\,..\,n+1]$.
> - **Evaluation order:** $i$ from $m+1$ down to $1$ in the outer loop, $j$ from $n+1$ down to $1$ in the inner loop.
> - **Time:** $O(mn)$ entries, $O(1)$ each: $O(mn)$.
>
> The table and the evaluation order are those of [[concepts/edit-distance|edit distance]] ([[2-algorithms/03-dynamic-programming#37-edit-distance|§3.7]]).
>
> **Answer.** $\textsf{LCS}(1,1)$, in $O(mn)$ time.

### (b) Shortest common supersequence

> [!hint]- Hint
> The first symbol of a shortest common supersequence is used by $A$, by $B$, or by both — otherwise it could be deleted.

> [!solution]- Solution
> **Function.** For $1\le i\le m+1$ and $1\le j\le n+1$, let $\textsf{SCS}(i, j)$ be the length of a shortest common supersequence of $A[i\,..\,m]$ and $B[j\,..\,n]$. We need $\textsf{SCS}(1,1)$.
>
> **Recurrence.** $\textsf{SCS}(i, j) = n-j+1$ if $i > m$, and $m-i+1$ if $j > n$ (copy the other suffix); otherwise
> $$
> \textsf{SCS}(i, j) = 1 + \min\begin{cases}
> \textsf{SCS}(i+1, j)\\
> \textsf{SCS}(i, j+1)\\
> \textsf{SCS}(i+1, j+1) & \text{only if } A[i] = B[j]
> \end{cases}
> $$
> Fix embeddings of both suffixes in a shortest common supersequence $Z$. Its first symbol is used by at least one of them (otherwise delete it). If only $A$'s embedding uses it, it is $A[i]$, and the rest of $Z$ contains $A[i+1\,..\,m]$ and $B[j\,..\,n]$; symmetrically for $B$; if both use it, $A[i] = B[j]$ and the rest contains $A[i+1\,..\,m]$ and $B[j+1\,..\,n]$. Conversely, each option with the right first symbol prepended is a common supersequence.
>
> Memoization, evaluation order and time are as in (a): $O(mn)$.
>
> **Answer.** $\textsf{SCS}(1,1)$, in $O(mn)$ time.

### (c) Longest bitonic subsequence

> [!hint]- Hint
> Guess the peak $A[i]$. The increasing half ends at $A[i]$ and uses only indices before $i$; the decreasing half starts at $A[i]$ and uses only indices after $i$ — so the two halves can be optimized separately, as in [[2-algorithms/03-dynamic-programming#36-longest-increasing-subsequence|§3.6]].

> [!solution]- Solution
> **Functions.** For $1\le i\le n$, let $\textsf{IncEnd}(i)$ be the length of a longest increasing subsequence of $A[1\,..\,i]$ that ends with $A[i]$, and $\textsf{DecStart}(i)$ the length of a longest decreasing subsequence of $A[i\,..\,n]$ that starts with $A[i]$.
>
> **Recurrences** (a maximum over the empty set is 0). The element before $A[i]$ in the increasing subsequence is some smaller $A[h]$, $h < i$; the element after $A[i]$ in the decreasing one is some smaller $A[j]$, $j > i$:
> $$
> \begin{aligned}
> \textsf{IncEnd}(i) &= 1 + \max\{\textsf{IncEnd}(h) \mid h < i,\ A[h] < A[i]\}\\
> \textsf{DecStart}(i) &= 1 + \max\{\textsf{DecStart}(j) \mid j > i,\ A[j] < A[i]\}
> \end{aligned}
> $$
> **Combining.** A bitonic subsequence with peak $A[i]$ has at least two elements on each side, counting the peak, so we need
> $$
> \max\{\textsf{IncEnd}(i) + \textsf{DecStart}(i) - 1 \mid 1\le i\le n,\ \textsf{IncEnd}(i)\ge 2,\ \textsf{DecStart}(i)\ge 2\},
> $$
> or 0 if no $i$ qualifies. (The condition $1 < i < \ell$ in the definition rules out monotone sequences; if you allow them, drop the two conditions $\ge 2$.)
>
> - **Memoization:** arrays $\mathit{IncEnd}[1\,..\,n]$ and $\mathit{DecStart}[1\,..\,n]$.
> - **Evaluation order:** $\mathit{IncEnd}$ for $i$ from $1$ up to $n$; $\mathit{DecStart}$ for $i$ from $n$ down to $1$.
> - **Time:** $2n$ entries, $O(n)$ each: $O(n^2)$.
>
> **Answer.** The maximum above, in $O(n^2)$ time.

### (d) Longest oscillating subsequence

> [!hint]- Hint
> After its first element, an oscillating sequence oscillates "the other way round". Use two functions: one for sequences whose first step goes down, one for sequences whose first step goes up.

> [!solution]- Solution
> **Functions.** For $1\le i\le n$, let $\textsf{OscDown}(i)$ be the length of a longest subsequence of $A[i\,..\,n]$ that starts with $A[i]$ and whose steps go down, up, down, … (first step down), and let $\textsf{OscUp}(i)$ be the same with the first step up. The oscillating sequences are exactly those whose steps go down, up, down, …, so we need $\max_{1\le i\le n}\textsf{OscDown}(i)$ (and 0 if $n = 0$).
>
> **Recurrences** (a maximum over the empty set is 0). After $A[i]$ comes some $A[j]$, $j > i$, that is smaller (for $\textsf{OscDown}$) or larger (for $\textsf{OscUp}$), and from $A[j]$ on the steps start the other way:
> $$
> \begin{aligned}
> \textsf{OscDown}(i) &= 1 + \max\{\textsf{OscUp}(j) \mid j > i,\ A[j] < A[i]\}\\
> \textsf{OscUp}(i) &= 1 + \max\{\textsf{OscDown}(j) \mid j > i,\ A[j] > A[i]\}
> \end{aligned}
> $$
>
> - **Memoization:** arrays $\mathit{OscDown}[1\,..\,n]$ and $\mathit{OscUp}[1\,..\,n]$.
> - **Evaluation order:** $i$ from $n$ down to $1$, both entries at each $i$.
> - **Time:** $2n$ entries, $O(n)$ each: $O(n^2)$.
>
> **Answer.** $\max_i\textsf{OscDown}(i)$, in $O(n^2)$ time.

### (e) Shortest oscillating supersequence

> [!hint]- Hint
> In an oscillating sequence, odd positions are local maxima and even positions local minima. Fill every inserted position with something huge (odd) or tiny (even); then only elements of $A$ that end up next to each other can conflict, and only the parity of each element's position matters.

> [!solution]- Solution
> **Where $A$ can go.** In an oscillating sequence every odd position holds a larger value than its neighbors and every even position a smaller one. Place $A[1], \dots, A[n]$ at positions $p_1 < p_2 < \dots < p_n$, and fill every other position with $\max A + 1$ if it is odd and $\min A - 1$ if it is even. Every inequality involving a filler then holds, so the result is oscillating if and only if each pair of elements of $A$ in **adjacent** positions $p_{h+1} = p_h + 1$ steps the right way. Let $\textsf{Step}(h, \pi)$ be the condition for $A[h]$, at a position of parity $\pi$, to be followed directly by $A[h+1]$: $A[h] > A[h+1]$ if $\pi$ is odd, and $A[h] < A[h+1]$ if $\pi$ is even. Conversely, every oscillating supersequence puts $A$ at positions with this property, and cutting it off after $A[n]$ leaves an oscillating supersequence.
>
> So we want valid positions with $p_n$ as small as possible, and only parities matter. Between $A[h]$ and $A[h+1]$ we insert 0 fillers (parity flips; needs $\textsf{Step}$), 1 filler (parity stays) or 2 fillers (parity flips, always allowed); a gap of 3 or more fillers can be shortened by 2 without changing any parity.
>
> **Function.** For $1\le i\le n$ and $\pi\in\{\text{odd}, \text{even}\}$, let $\textsf{OscSuper}(i, \pi)$ be the length of a shortest oscillating supersequence of $A[1\,..\,i]$ that ends with $A[i]$, at a position of parity $\pi$. We need $\min_\pi \textsf{OscSuper}(n, \pi)$ (and 0 if $n = 0$).
>
> **Recurrence.** $\textsf{OscSuper}(1, \text{odd}) = 1$ and $\textsf{OscSuper}(1, \text{even}) = 2$. For $i\ge 2$, write $\bar\pi$ for the other parity and let $c = 1$ if $\textsf{Step}(i-1, \bar\pi)$ holds and $c = 3$ otherwise; then
> $$
> \textsf{OscSuper}(i, \pi) = \min\{\textsf{OscSuper}(i-1, \pi) + 2,\ \ \textsf{OscSuper}(i-1, \bar\pi) + c\}.
> $$
> Keeping only the shortest length for each parity loses nothing, because what may follow $A[i]$ depends only on the parity of its position.
>
> - **Memoization:** an array $\mathit{OscSuper}[1\,..\,n, \{\text{odd}, \text{even}\}]$.
> - **Evaluation order:** $i$ from $1$ up to $n$.
> - **Time:** $2n$ entries, $O(1)$ each: $O(n)$.
>
> For example, $[1, 1]$ needs three elements, such as $1, 0, 1$.
>
> **Answer.** $\min_\pi\textsf{OscSuper}(n, \pi)$, in $O(n)$ time.

### (f), (g), (h) Convex, weakly increasing and double-increasing

> [!hint]- Hint
> Each condition involves three consecutive elements, so a subproblem must remember **two** elements: the first two of the rest of the sequence.

> [!solution]- Solution
> **(h) Function.** For $1\le i < j\le n$, let $\textsf{DoubleInc}(i, j)$ be the length of a longest double-increasing subsequence of $A$ whose first two elements are $A[i]$ and $A[j]$ (so the rest comes from $A[j+1\,..\,n]$). We need $n$ if $n\le 2$, and $\max_{i<j}\textsf{DoubleInc}(i, j)$ otherwise.
>
> **Recurrence.** The third element, if any, is some $A[k]$ with $k > j$ and $A[k] > A[i]$, and from $A[j], A[k]$ on the sequence must again be double-increasing:
> $$
> \textsf{DoubleInc}(i, j) = 1 + \max\big(\{1\} \cup \{\textsf{DoubleInc}(j, k) \mid k > j,\ A[k] > A[i]\}\big).
> $$
> The $\{1\}$ accounts for the sequence $A[i], A[j]$ with nothing after it.
>
> - **Memoization:** an array $\mathit{DoubleInc}[1\,..\,n, 1\,..\,n]$ (entries with $i < j$).
> - **Evaluation order:** $i$ from $n$ down to $1$ in the outer loop, $j$ in any order in the inner loop (entry $(i, j)$ reads only row $j > i$).
> - **Time:** $O(n^2)$ entries, $O(n)$ each: $O(n^3)$.
>
> **(f) and (g)** are the same algorithm with another test for the third element. $\textsf{Convex}(i, j)$, the length of a longest convex subsequence whose first two elements are $A[i]$ and $A[j]$, allows $A[k]$ when $2A[j] < A[i] + A[k]$; $\textsf{WeakInc}(i, j)$, the same for weakly increasing subsequences, allows $A[k]$ when $2A[k] > A[i] + A[j]$. Same table, order and time.
>
> **Trap.** A one-index function like $\textsf{IncEnd}(i)$ does not work here: whether $A[k]$ may come next depends on the two previous elements, not only on the last one.
>
> **Answer.** The maximum of the pair function over $i < j$, in $O(n^3)$ time, for each of (f), (g) and (h).

## Exercise 3.6 — Shuffles

> [!question] Exercise 3.6 (book pp. 126–127)
> A **shuffle** of two strings $X$ and $Y$ intersperses their characters while keeping the characters of each string in order. `BANANAANANAS` is a shuffle of `BANANA` and `ANANAS` in several ways, and `PRODGYRNAMAMMIINCG` and `DYPRONGARMAMMICING` are both shuffles of `DYNAMIC` and `PROGRAMMING`.
>
> (a) Given $A[1\,..\,m]$, $B[1\,..\,n]$ and $C[1\,..\,m+n]$, describe and analyze an algorithm to decide whether $C$ is a shuffle of $A$ and $B$.
>
> (b) A **smooth** shuffle never uses more than two consecutive symbols of either string. `PRDOYGNARAMMMIICNG` is a smooth shuffle of `DYNAMIC` and `PROGRAMMING`; `DYPRNOGRAAMMMICING` is a shuffle of the same strings but not a smooth one (it takes OGR and ING from PROGRAMMING in one piece); a string of 19 X's is a smooth shuffle of 8 X's and 11 X's; and 4 X's and 12 X's have no smooth shuffle at all. Describe and analyze an algorithm to decide whether $Z$ is a smooth shuffle of $X$ and $Y$.
>
> (The book prints the first unary string with 7 X's, but its colored picture uses 8 of them, and $7 + 11\ne 19$.)

### (a) Shuffles

> [!hint]- Hint
> After $i-1$ characters of $A$ and $j-1$ of $B$ have been used, the next character of $C$ is $C[i+j-1]$, and it must come from $A$ or from $B$.

> [!solution]- Solution
> **Function.** For $1\le i\le m+1$ and $1\le j\le n+1$, let $\textsf{Shuffle}(i, j)$ be True if and only if $C[i+j-1\,..\,m+n]$ is a shuffle of $A[i\,..\,m]$ and $B[j\,..\,n]$. We need $\textsf{Shuffle}(1,1)$. (If $C$ does not have length $m+n$, the answer is False.)
>
> **Recurrence.** $\textsf{Shuffle}(m+1, n+1) = \textsf{True}$; otherwise the character $C[i+j-1]$ comes from $A$ or from $B$:
> $$
> \begin{aligned}
> \textsf{Shuffle}(i, j) = {}& \big(i\le m \,\land\, A[i] = C[i+j-1] \,\land\, \textsf{Shuffle}(i+1, j)\big)\\
> {}\lor{}& \big(j\le n \,\land\, B[j] = C[i+j-1] \,\land\, \textsf{Shuffle}(i, j+1)\big)
> \end{aligned}
> $$
>
> - **Memoization:** a boolean array $\mathit{Shuffle}[1\,..\,m+1, 1\,..\,n+1]$.
> - **Evaluation order:** $i$ from $m+1$ down to $1$ in the outer loop, $j$ from $n+1$ down to $1$ in the inner loop.
> - **Time:** $O(mn)$ entries, $O(1)$ each: $O(mn)$.
>
> **Trap.** Taking the character from $A$ whenever it matches is wrong: `acab` is a shuffle of $A = $ `ab` and $B = $ `ac` (it is $B$ followed by $A$), but that greedy rule takes the first `a` from $A$ and then gets stuck at `c`.
>
> **Answer.** $\textsf{Shuffle}(1,1)$, in $O(mn)$ time.

### (b) Smooth shuffles

> [!hint]- Hint
> Cut $Z$ into maximal runs of characters that come from the same string. $Z$ is a smooth shuffle exactly when the runs have length 1 or 2; consecutive runs come from different strings. Remember which string the next run comes from.

> [!solution]- Solution
> Let $X = X[1\,..\,m]$ and $Y = Y[1\,..\,n]$, and assume that $Z$ has length $m+n$ (otherwise the answer is False). Split a shuffle into maximal runs of consecutive characters taken from the same string; the runs alternate between $X$ and $Y$, and the shuffle is smooth if and only if every run has length 1 or 2.
>
> **Functions.** For $1\le i\le m+1$ and $1\le j\le n+1$, let $\textsf{SmoothX}(i, j)$ be True if and only if $Z[i+j-1\,..\,m+n]$ is a smooth shuffle of $X[i\,..\,m]$ and $Y[j\,..\,n]$ whose first run comes from $X$, or both suffixes are empty; let $\textsf{SmoothY}(i, j)$ be the same with the first run from $Y$. We need $\textsf{SmoothX}(1,1)\lor\textsf{SmoothY}(1,1)$.
>
> **Recurrence.** $\textsf{SmoothX}(m+1, n+1) = \textsf{SmoothY}(m+1, n+1) = \textsf{True}$. Otherwise the first run is $X[i]$ or $X[i\,..\,i+1]$, and the next run, if any, comes from $Y$:
> $$
> \begin{aligned}
> \textsf{SmoothX}(i, j) = {}& \big(X[i] = Z[i+j-1] \,\land\, \textsf{SmoothY}(i+1, j)\big)\\
> {}\lor{}& \big(X[i\,..\,i+1] = Z[i+j-1\,..\,i+j] \,\land\, \textsf{SmoothY}(i+2, j)\big)
> \end{aligned}
> $$
> $\textsf{SmoothY}(i, j)$ is the same with the roles of $X, i$ and $Y, j$ exchanged: $Y[j] = Z[i+j-1]$ and $\textsf{SmoothX}(i, j+1)$, or $Y[j\,..\,j+1] = Z[i+j-1\,..\,i+j]$ and $\textsf{SmoothX}(i, j+2)$. A term that needs characters past the end of $X$ or $Y$ is False. In particular $\textsf{SmoothY}(i, n+1)$ is False for $i\le m$: a run from $X$ can be followed only by a run from $Y$ or by the end of $Z$.
>
> - **Memoization:** two boolean arrays indexed $[1\,..\,m+1, 1\,..\,n+1]$.
> - **Evaluation order:** $i$ from $m+1$ down to $1$ in the outer loop, $j$ from $n+1$ down to $1$ in the inner loop, computing $\textsf{SmoothX}(i, j)$ and $\textsf{SmoothY}(i, j)$ together. ($\textsf{SmoothX}(i, j)$ reads rows $i+1$ and $i+2$; $\textsf{SmoothY}(i, j)$ reads entries $j+1$ and $j+2$ of row $i$, already computed.)
> - **Time:** $O(mn)$.
>
> The book's last example is a counting argument: the 12 X's of the second string need at least 6 runs, with a run of the first string between any two of them — at least 5 runs, but the first string has only 4 characters.
>
> **Answer.** $\textsf{SmoothX}(1,1)\lor\textsf{SmoothY}(1,1)$, in $O(mn)$ time.

## Exercise 3.7 — Subsequences of a longer string

> [!question] Exercise 3.7 (book p. 127)
> The input is two arrays $X[1\,..\,k]$ and $Y[1\,..\,n]$ with $k\le n$.
>
> (a) Decide whether $X$ is a subsequence of $Y$. For example, `PPAP` is a subsequence of `PENPINEAPPLEAPPLEPEN`.
>
> (b) Find the smallest number of symbols that can be removed from $Y$ so that $X$ is no longer a subsequence (equivalently, the longest subsequence of $Y$ that is not a supersequence of $X$). For `PPAP` and `PENPINEAPPLEAPPLEPEN` the answer is 2.
>
> (d) Each $Y[j]$ also has a cost $C[j]$, which may be positive, negative or zero. Compute the minimum cost of an occurrence of $X$ as a subsequence of $Y$: indices $I[1] < I[2] < \dots < I[k]$ with $Y[I[j]] = X[j]$ for every $j$, minimizing $\sum_{j=1}^{k} C[I[j]]$. (The book writes $X[I[j]] = Y[j]$ and $\sum_j C[j]$, with the indices swapped.)
>
> (e) Count the occurrences of $X$ as a subsequence of $Y$ (the index arrays $I$ of part (d)), assuming two integers can be added in $O(1)$ time. `PPAP` occurs exactly 23 times in `PENPINEAPPLEAPPLEPEN`; if all characters are equal, the answer is $\binom{n}{k}$.
>
> (f) What is the running time of your algorithm for part (e) if adding two $\ell$-bit integers takes $O(\ell)$ time? (The book says "part (d)"; both are answered below.)
>
> Part (c), two disjoint occurrences (♥), is skipped.

### (a) Is X a subsequence of Y?

> [!hint]- Hint
> Match each $X[i]$ to the earliest possible position. An exchange argument shows that this never hurts.

> [!solution]- Solution
> Scan $Y$ once, matching $X$ greedily:
>
> ```text
> IsSubsequence(X[1 .. k], Y[1 .. n]):
>     i ← 1
>     for j ← 1 to n
>         if i ≤ k and X[i] = Y[j]
>             i ← i + 1
>     return (i = k + 1)
> ```
>
> **Why greedy is correct.** *Key fact* (used again in (b)): if $X[i] = Y[j]$, then $X[i\,..\,k]$ is a subsequence of $Y[j\,..\,n]$ if and only if $X[i+1\,..\,k]$ is a subsequence of $Y[j+1\,..\,n]$; if $X[i]\ne Y[j]$, then if and only if $X[i\,..\,k]$ is a subsequence of $Y[j+1\,..\,n]$. The "if" directions hold because an occurrence in a shorter suffix, extended by $Y[j]$ where needed, is an occurrence in the longer one. For "only if" when $X[i] = Y[j]$: an occurrence matches $X[i]$ to some position $j'\ge j$ holding the same symbol; moving that match to $j$ keeps the positions increasing, and the matches of $X[i+1\,..\,k]$ lie in $Y[j+1\,..\,n]$. When $X[i]\ne Y[j]$, no occurrence can use position $j$, since $X[i]$ is matched first. Each iteration of the loop applies the key fact once, so by induction the loop answers correctly.
>
> **Time:** $O(n)$.
>
> **Answer.** The greedy scan, in $O(n)$ time.

### (b) Destroying every occurrence

> [!hint]- Hint
> Decide for each $Y[j]$, from left to right, whether to delete it, and test what remains with the greedy algorithm of (a). Deleting a symbol that the greedy scan would skip anyway is wasted.

> [!solution]- Solution
> **Function.** For $1\le i\le k+1$ and $1\le j\le n+1$, let $\textsf{Cut}(i, j)$ be the smallest number of symbols that must be deleted from $Y[j\,..\,n]$ so that $X[i\,..\,k]$ is not a subsequence of what remains, or $\infty$ if that is impossible (which happens exactly when $i = k+1$: the empty string is a subsequence of everything). We need $\textsf{Cut}(1, 1)$.
>
> **Recurrence.**
> $$
> \textsf{Cut}(i, j) = \begin{cases}
> \infty & \text{if } i = k+1\\
> 0 & \text{if } i\le k \text{ and } j = n+1\\
> \textsf{Cut}(i, j+1) & \text{if } i\le k,\ j\le n,\ Y[j]\ne X[i]\\
> \min\{1 + \textsf{Cut}(i, j+1),\ \textsf{Cut}(i+1, j+1)\} & \text{if } i\le k,\ j\le n,\ Y[j] = X[i]
> \end{cases}
> $$
> By the key fact of (a), whether $X[i\,..\,k]$ survives in what remains of $Y[j\,..\,n]$ is decided by the first remaining symbol. If $Y[j]\ne X[i]$, keeping $Y[j]$ does not change the answer, so deleting it would waste a deletion. If $Y[j] = X[i]$, either delete it (cost 1, same $i$), or keep it — then $X[i]$ is matched to it, and $X[i+1\,..\,k]$ must be destroyed in $Y[j+1\,..\,n]$.
>
> - **Memoization:** an array $\mathit{Cut}[1\,..\,k+1, 1\,..\,n+1]$.
> - **Evaluation order:** $j$ from $n+1$ down to $1$ in the outer loop, $i$ in any order in the inner loop (entry $(i, j)$ reads only column $j+1$).
> - **Time:** $O(kn)$.
>
> In the example, deleting the two A's of `PENPINEAPPLEAPPLEPEN` (positions 8 and 13) leaves no A at all, and no single deletion destroys every `PPAP`.
>
> **Answer.** $\textsf{Cut}(1,1)$, in $O(kn)$ time.

### (d) Cheapest occurrence

> [!hint]- Hint
> Same subproblems as in (b): an occurrence of $X[i\,..\,k]$ in $Y[j\,..\,n]$ either uses $Y[j]$ for $X[i]$ or avoids position $j$.

> [!solution]- Solution
> **Function.** For $1\le i\le k+1$ and $1\le j\le n+1$, let $\textsf{MinCost}(i, j)$ be the minimum total cost of an occurrence of $X[i\,..\,k]$ as a subsequence of $Y[j\,..\,n]$, or $\infty$ if there is none. We need $\textsf{MinCost}(1, 1)$.
>
> **Recurrence.** $\textsf{MinCost}(k+1, j) = 0$ (the empty occurrence) and $\textsf{MinCost}(i, n+1) = \infty$ for $i\le k$; otherwise
> $$
> \textsf{MinCost}(i, j) = \min\begin{cases}
> \textsf{MinCost}(i, j+1)\\
> C[j] + \textsf{MinCost}(i+1, j+1) & \text{only if } X[i] = Y[j]
> \end{cases}
> $$
> Negative costs cause no trouble: every occurrence of $X[i\,..\,k]$ uses exactly $k-i+1$ positions.
>
> - **Memoization:** an array $\mathit{MinCost}[1\,..\,k+1, 1\,..\,n+1]$.
> - **Evaluation order:** $j$ from $n+1$ down to $1$ in the outer loop, $i$ in any order in the inner loop.
> - **Time:** $O(kn)$.
>
> **Answer.** $\textsf{MinCost}(1,1)$, in $O(kn)$ time ($\infty$ means that $X$ is not a subsequence of $Y$).

### (e) and (f) Counting occurrences

> [!hint]- Hint
> The same subproblems once more: add the two cases instead of minimizing. For (f), bound the size of a count.

> [!solution]- Solution
> **Function.** For $1\le i\le k+1$ and $1\le j\le n+1$, let $\textsf{NumOcc}(i, j)$ be the number of occurrences of $X[i\,..\,k]$ as a subsequence of $Y[j\,..\,n]$ (index sequences, as in (d)). We need $\textsf{NumOcc}(1,1)$.
>
> **Recurrence.** $\textsf{NumOcc}(k+1, j) = 1$ and $\textsf{NumOcc}(i, n+1) = 0$ for $i\le k$; otherwise count the occurrences that avoid position $j$ and those that use it for $X[i]$:
> $$
> \textsf{NumOcc}(i, j) = \textsf{NumOcc}(i, j+1) + \begin{cases}\textsf{NumOcc}(i+1, j+1) & \text{if } X[i] = Y[j]\\ 0 & \text{otherwise}\end{cases}
> $$
> Same array and evaluation order as in (b) and (d): $O(kn)$ additions, so $O(kn)$ time. When all characters are equal, the recurrence is Pascal's rule and $\textsf{NumOcc}(1,1) = \binom{n}{k}$.
>
> **(f)** Every entry counts sets of positions in $Y$, so it is at most $2^n$ and has at most $n+1$ bits. Each of the $O(kn)$ additions then takes $O(n)$ time: $O(kn^2)$ in all. The size bound is tight: for $k = n/2$ and equal characters the answer $\binom{n}{n/2}$ has $n - O(\log n)$ bits. For part (d) with $\ell$-bit integer costs, every partial sum of at most $k$ costs has $\ell + O(\log k)$ bits, so that algorithm takes $O(kn(\ell + \log k))$ time.
>
> **Answer.** (e) $\textsf{NumOcc}(1,1)$ in $O(kn)$ time; (f) $O(kn^2)$ time when an $\ell$-bit addition costs $O(\ell)$.

## Exercise 3.8 — Forward and backward

> [!question] Exercise 3.8 (book p. 128)
> Describe and analyze an algorithm to find the length of the longest substring of $T[1\,..\,n]$ that appears both forward and backward in $T$, where the forward and the backward copy must not overlap. For `ALGORITHM` the answer is 0; for `RECURSION` it is 1 (R); for `REDIVIDE` it is 3 (EDI, whose reversal IDE ends the string — the palindrome DIVID does not count, because its two copies overlap); for `DYNAMICPROGRAMMINGMANYTIMES` it is 4 (YNAM and MANY — not 6, since YNAMIR is only a subsequence).

> [!hint]- Hint
> Pair the first character of the forward copy with the last character of the backward copy, and walk inward from both ends.

> [!solution]- Solution
> If $S$ occurs at $T[i\,..\,i+\ell-1]$ and its reversal at $T[j-\ell+1\,..\,j]$, then $T[i+t] = T[j-t]$ for $0\le t < \ell$. Exchanging the roles of the two copies (the reversal of $S$ is read forward at the other place), we may assume that the forward copy is on the left; then "no overlap" means $i+\ell-1 < j-\ell+1$, that is, $2\ell\le j-i+1$.
>
> **Function.** For $1\le i, j\le n$, let $\textsf{Mirror}(i, j)$ be the largest $\ell\ge 0$ such that $2\ell\le j-i+1$ and $T[i+t] = T[j-t]$ for all $0\le t<\ell$ — the length of the longest substring that starts at $i$ and whose reversal ends at $j$, without overlap. We need $\max_{1\le i<j\le n}\textsf{Mirror}(i, j)$ (and 0 if $n\le 1$).
>
> **Recurrence.**
> $$
> \textsf{Mirror}(i, j) = \begin{cases} 0 & \text{if } i\ge j \text{ or } T[i]\ne T[j]\\ 1 + \textsf{Mirror}(i+1, j-1) & \text{otherwise}\end{cases}
> $$
> If $i<j$ and $T[i] = T[j]$, then $\ell = 1$ fits, and a longer match is $T[i] = T[j]$ followed by a match for $(i+1, j-1)$, whose non-overlap condition $2(\ell-1)\le (j-1)-(i+1)+1$ is the same as $2\ell\le j-i+1$.
>
> - **Memoization:** an array $\mathit{Mirror}[1\,..\,n, 1\,..\,n]$.
> - **Evaluation order:** $i$ from $n$ down to $1$ in the outer loop, $j$ in any order in the inner loop (entry $(i, j)$ reads row $i+1$).
> - **Time:** $O(n^2)$ entries, $O(1)$ each: $O(n^2)$.
>
> Example: for `REDIVIDE`, $\textsf{Mirror}(2, 8) = 3$ — E = E, D = D, I = I, and then $(5, 5)$ has $i\ge j$.
>
> **Answer.** $\max_{i<j}\textsf{Mirror}(i,j)$, in $O(n^2)$ time.

## Exercise 3.9 — Palindromes

> [!question] Exercise 3.9 (book pp. 128–129)
> A **palindrome** is a string equal to its reversal, like `I`, `DEED` or `RACECAR`. Given a string $T[1\,..\,n]$, describe and analyze algorithms to find:
>
> (a) the length of a longest subsequence of $T$ that is a palindrome — for `MAHDYNAMICPROGRAMZLETMESHOWYOUTHEM` it is 11 (`MHYMRORMYHM`);
>
> (b) the length of a shortest supersequence of $T$ that is a palindrome — for `TWENTYONE` it is 13 (`TWENTOYOTNEWT`);
>
> (c) the smallest number of palindromes into which $T$ can be cut — for `BUBBASEESABANANA` it is 3 (BUB·BASEESAB·ANANA; other decompositions include B·U·BB·ASEESA·B·ANANA and BUB·B·A·SEES·ABA·N·ANA);
>
> (d) the largest $k$ such that $T$ can be cut into palindromes of length at least $k$ — 1 for `PALINDROME`, 3 for `BUBBASEESABANANA`, and $n$ for a string of $n$ identical symbols;
>
> (e) the number of ways to cut $T$ into palindromes — 1 for `PALINDROME` and $2^{n-1}$ for $n$ identical symbols. For `BUBBASEESABANANA` the book says 70 (five decompositions shown "and 65 others"); the correct count is **97**.
>
> Part (f), metapalindromes (♥), is skipped.

### (a) Longest palindromic subsequence

> [!hint]- Hint
> Use intervals $T[i\,..\,j]$: either an end is unused, or both ends are used and matched to each other.

> [!solution]- Solution
> **Function.** For $1\le i\le n+1$ and $i-1\le j\le n$, let $\textsf{LPS}(i, j)$ be the length of a longest palindromic subsequence of $T[i\,..\,j]$. We need $\textsf{LPS}(1, n)$.
>
> **Recurrence.** $\textsf{LPS}(i, i-1) = 0$ (empty interval) and $\textsf{LPS}(i, i) = 1$; for $i < j$,
> $$
> \textsf{LPS}(i, j) = \max\begin{cases}
> \textsf{LPS}(i+1, j)\\
> \textsf{LPS}(i, j-1)\\
> 2 + \textsf{LPS}(i+1, j-1) & \text{only if } T[i] = T[j]
> \end{cases}
> $$
> A longest palindromic subsequence of $T[i\,..\,j]$ avoids $T[i]$, or avoids $T[j]$, or uses both; in the last case $T[i]$ is its first and $T[j]$ its last symbol, so they are equal, and the middle is a palindromic subsequence of $T[i+1\,..\,j-1]$.
>
> - **Memoization:** an array $\mathit{LPS}[1\,..\,n+1, 0\,..\,n]$.
> - **Evaluation order:** $i$ from $n$ down to $1$ in the outer loop, $j$ from $i$ up to $n$ in the inner loop (the base entries $(i, i-1)$ and $(n+1, n)$ first).
> - **Time:** $O(n^2)$ entries, $O(1)$ each: $O(n^2)$.
>
> Always taking $2 + \textsf{LPS}(i+1, j-1)$ when $T[i] = T[j]$ is also correct, but that shortcut needs an exchange argument; the three-way maximum needs none.
>
> **Answer.** $\textsf{LPS}(1, n)$, in $O(n^2)$ time.

### (b) Shortest palindromic supersequence

> [!hint]- Hint
> A palindrome starts and ends with the same symbol. Wrap a shortest answer for a smaller interval in a pair of equal symbols.

> [!solution]- Solution
> **Function.** For $1\le i\le n+1$ and $i-1\le j\le n$, let $\textsf{SPS}(i, j)$ be the length of a shortest palindrome that contains $T[i\,..\,j]$ as a subsequence. We need $\textsf{SPS}(1, n)$.
>
> **Recurrence.** $\textsf{SPS}(i, i-1) = 0$ and $\textsf{SPS}(i, i) = 1$; for $i < j$,
> $$
> \textsf{SPS}(i, j) = 2 + \min\begin{cases}
> \textsf{SPS}(i+1, j)\\
> \textsf{SPS}(i, j-1)\\
> \textsf{SPS}(i+1, j-1) & \text{only if } T[i] = T[j]
> \end{cases}
> $$
> **Each option is achievable:** $T[i]\cdot P\cdot T[i]$ for a shortest palindromic supersequence $P$ of $T[i+1\,..\,j]$; symmetrically with $T[j]$ for $T[i\,..\,j-1]$; and $T[i]\cdot P\cdot T[j]$ for $T[i+1\,..\,j-1]$ when $T[i] = T[j]$. **Nothing is shorter:** a shortest palindromic supersequence of $T[i\,..\,j]$ has the form $c\,P'\,c$ with $P'$ a palindrome; fix an embedding of $T[i\,..\,j]$ in it. If neither $T[i]$ is matched to the first $c$ nor $T[j]$ to the last, all of $T[i\,..\,j]$ embeds in $P'$, which is shorter — impossible. If only $T[i]$ is matched to the first $c$, then $T[i+1\,..\,j]$ embeds in $P'$, so the length is at least $2 + \textsf{SPS}(i+1, j)$; symmetrically $2 + \textsf{SPS}(i, j-1)$; if both are, then $T[i] = c = T[j]$ and the length is at least $2 + \textsf{SPS}(i+1, j-1)$.
>
> Memoization, evaluation order and time are as in (a): $O(n^2)$.
>
> **Answer.** $\textsf{SPS}(1, n)$, in $O(n^2)$ time.

### (c), (d), (e) Decompositions into palindromes

> [!hint]- Hint
> First tabulate which substrings are palindromes (an interval recurrence). Then use the suffix recurrence of text segmentation with $\textsf{IsWord}$ replaced by that table — minimizing the number of pieces, maximizing the shortest piece, or adding.

> [!solution]- Solution
> **Palindrome table.** For $1\le i\le n+1$ and $i-1\le j\le n$, let $\textsf{IsPal}(i, j)$ be True if and only if $T[i\,..\,j]$ is a palindrome: $\textsf{IsPal}(i, j) = \textsf{True}$ if $j\le i$, and $\textsf{IsPal}(i, j) = \big(T[i] = T[j]\big)\land\textsf{IsPal}(i+1, j-1)$ otherwise. Array $\mathit{IsPal}[1\,..\,n+1, 0\,..\,n]$, filled for $i$ from $n+1$ down to $1$, $j$ from $i-1$ up to $n$: $O(n^2)$ time. In each recurrence below, the first piece of a decomposition of $T[i\,..\,n]$ is a palindrome $T[i\,..\,j]$ and the rest is a decomposition of $T[j+1\,..\,n]$.
>
> **(c) Function.** For $1\le i\le n+1$, let $\textsf{MinPal}(i)$ be the smallest number of palindromes into which the suffix $T[i\,..\,n]$ can be cut. We need $\textsf{MinPal}(1)$. $\textsf{MinPal}(n+1) = 0$ and, for $i\le n$ (single characters are palindromes, so the set is not empty),
> $$
> \textsf{MinPal}(i) = 1 + \min\{\textsf{MinPal}(j+1) \mid i\le j\le n,\ \textsf{IsPal}(i, j)\}.
> $$
>
> **(d) Function.** For $1\le i\le n+1$, let $\textsf{MaxMinLen}(i)$ be the largest $m$ such that $T[i\,..\,n]$ can be cut into palindromes of length at least $m$ — the maximum, over all decompositions, of the length of the shortest piece ($\infty$ for the empty suffix). We need $\textsf{MaxMinLen}(1)$. $\textsf{MaxMinLen}(n+1) = \infty$ and, for $i\le n$,
> $$
> \textsf{MaxMinLen}(i) = \max\big\{\min\{j-i+1,\ \textsf{MaxMinLen}(j+1)\} \bigm| i\le j\le n,\ \textsf{IsPal}(i, j)\big\}.
> $$
>
> **(e) Function.** For $1\le i\le n+1$, let $\textsf{NumPal}(i)$ be the number of decompositions of $T[i\,..\,n]$ into palindromes. We need $\textsf{NumPal}(1)$. $\textsf{NumPal}(n+1) = 1$ and, for $i\le n$,
> $$
> \textsf{NumPal}(i) = \sum_{\substack{i\le j\le n\\ \textsf{IsPal}(i, j)}} \textsf{NumPal}(j+1).
> $$
>
> - **Memoization:** the table $\mathit{IsPal}$, plus one array indexed $1\,..\,n+1$ for each part.
> - **Evaluation order:** $\mathit{IsPal}$ first; then $i$ from $n+1$ down to $1$.
> - **Time:** $O(n^2)$ for the table, then $n+1$ entries at $O(n)$ each: $O(n^2)$ in all.
>
> **The book's count is off.** `BUBBASEESABANANA` has eleven palindromic substrings of length at least 2 (BUB, BB, BASEESAB, ASEESA, SEES, EE, ABA, ANA twice, NAN, ANANA). The recurrence gives $\textsf{NumPal}(1) = 97$, and so does a direct enumeration of all $2^{15}$ ways to cut the string — not 70. For $n$ identical symbols every way of cutting works, and the recurrence gives $2^{n-1}$.
>
> **Answer.** (c) $\textsf{MinPal}(1)$, (d) $\textsf{MaxMinLen}(1)$, (e) $\textsf{NumPal}(1)$, each in $O(n^2)$ time.

## Exercise 3.10 — Increasing back-and-forth subsequences

> [!question] Exercise 3.10 (book pp. 129–130)
> Let $A[1\,..\,n]$ be an array of positive integers. An **increasing back-and-forth subsequence** is a sequence of indices $I[1\,..\,\ell]$ with $A[I[j]] < A[I[j+1]]$ for all $j < \ell$, where the next index $I[j+1]$ is larger than $I[j]$ if $I[j]$ is even and smaller if $I[j]$ is odd. Picture a token on a row of numbered squares that moves left from odd squares and right from even squares, always to a larger number. Describe an algorithm to compute the length of a longest increasing back-and-forth subsequence.
>
> The book's example is $A = [1, 1, 8, 7, 5, 6, 3, 6, 4, 4, 8, 3, 9, 1, 2, 2, 3, 9, 4, 0]$ with claimed answer 9; under the rule as stated, the answer is 7 (see the solution).

> [!hint]- Hint
> Where the token may go next depends only on the square it is on. The values strictly increase along the way, so the dependencies have no cycles: process the squares from the largest value down.

> [!solution]- Solution
> **Function.** For $1\le i\le n$, let $\textsf{BackForth}(i)$ be the length of a longest increasing back-and-forth subsequence that starts at index $i$. We need $\max_{1\le i\le n}\textsf{BackForth}(i)$ (and 0 if $n = 0$).
>
> **Recurrence** (a maximum over the empty set is 0). The next index $j$, if any, holds a larger value and lies on the correct side of $i$:
> $$
> \textsf{BackForth}(i) = 1 + \begin{cases}
> \max\{\textsf{BackForth}(j) \mid j > i,\ A[j] > A[i]\} & \text{if } i \text{ is even}\\
> \max\{\textsf{BackForth}(j) \mid j < i,\ A[j] > A[i]\} & \text{if } i \text{ is odd}
> \end{cases}
> $$
>
> - **Memoization:** an array $\mathit{BackForth}[1\,..\,n]$.
> - **Evaluation order:** entry $i$ reads only entries $j$ with $A[j] > A[i]$, so sort the indices by value and fill the entries in **decreasing** order of $A[i]$, ties in any order. Neither left to right nor right to left works, because the token moves both ways.
> - **Time:** $O(n\log n)$ to sort, then $n$ entries at $O(n)$ each: $O(n^2)$.
>
> **The book's example.** On the array above the algorithm returns **7**, for instance with indices $14, 15, 12, 19, 5, 4, 11$ and values $1, 2, 3, 4, 5, 7, 8$: from square 14 (even) right to 15, from 15 (odd) left to 12, from 12 (even) right to 19, and so on. The book's sequence of length 9, with indices $20, 1, 15, 18, 10, 6, 4, 3, 13$, moves *right* from odd squares and *left* from even ones — the opposite of the rule — and $A[18] = 9$ breaks the increasing order (its values are $0, 1, 2, 9, 4, \ldots$). With the directions swapped, the longest sequence would have length 10 (indices $20, 1, 16, 7, 10, 5, 6, 4, 3, 13$, values $0$ to $9$).
>
> **Answer.** $\max_i\textsf{BackForth}(i)$, in $O(n^2)$ time; on the book's example, 7.

### Sources for this page

Exercises 3.1–3.10 of Jeff Erickson, *Algorithms* (2019), pp. 123–130 (CC BY 4.0), paraphrased; the solutions are ours. The book's examples are kept wherever they test an algorithm. Three of them are wrong as printed — the length of the first unary string in 3.6(b), the palindrome count in 3.9(e), and the answer and sample sequence in 3.10 — and 3.7(d) states the occurrence condition with $X$ and $Y$ exchanged. Every recurrence on this page, in its stated evaluation order, and every number is checked by `tools/checks/a03x.py` against brute force on all small inputs and on random ones.
