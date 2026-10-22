---
title: "Lab 6a — Faster than brute force: binary search"
description: "Four problems a linear scan solves, done in logarithmic time: an index with A[i] = i in a sorted array, a local minimum, the median of two sorted arrays, and the k-th smallest element of two sorted arrays — each by finding a constant-time test that throws away half of the candidates while keeping an answer."
tags: [lab, algorithms, divide-and-conquer, midterm-2]
---

*Lab 6a · September 30 · CS/ECE 374 A, Fall 2026 · [[concepts/divide-and-conquer|divide and conquer]] · uses [[2-algorithms/01-recursion#16-the-pattern|§1.6]], [[2-algorithms/01-recursion#17-recursion-trees|§1.7]], [[2-algorithms/01-recursion#18-linear-time-selection|§1.8]] · rubric: [[0-toolkit/06-how-exams-are-graded#11-recursive-algorithms|how exams are graded §11]] · solutions: explained from the official solutions*

> [!abstract] In one breath
> Each problem has an obvious $O(n)$ scan, and each can be done in $O(\log n)$ time by binary search — once you find the right **one-comparison test** that tells you which half of the candidates can be thrown away. Problem 1 (an index with $A[i] = i$) becomes an ordinary binary search after one observation: for distinct *integers*, the differences $A[i] - i$ are sorted, so you are searching for a $0$. Problem 2 (a local minimum) keeps the invariant "the subarray goes down at its left end and up at its right end", which forces a local minimum inside; one look at the middle pair restores the invariant on half the array. Problem 3 (the median of two sorted arrays of length $n$) compares the two middle elements: the larger one's tail lies above the median and the smaller one's head lies below it, so dropping the same number from each side leaves the median where it was. Problem 4 (the $k$-th smallest of two sorted arrays) reduces to Problem 3 by keeping only the first $k$ elements of each array and padding with $\infty$.

> [!intuition] What all four have in common
> Binary search is not really about looking up a value. It is any recursion that keeps an **invariant** — "an answer lies in $A[lo\,..\,hi]$" — and spends $O(1)$ time to shrink the range to about half while keeping the invariant. The running time is always $T(n) = T(n/2) + O(1) = O(\log n)$ (the "equal level sums" case of [[2-algorithms/01-recursion#17-recursion-trees|§1.7]]), and the proof of correctness is always the same: show that the half you throw away contains no answer you need. The whole difficulty is finding the test.

## Problem 1 — An index with A[i] = i

> [!question] Problem 1
> You are given an array $A[1\,..\,n]$ of $n$ distinct integers — positive, negative or zero — sorted in increasing order, $A[1] < A[2] < \cdots < A[n]$.
>
> **(a)** Describe a fast algorithm that either computes an index $i$ with $A[i] = i$ or correctly reports that there is no such index.
>
> **(b)** Suppose you know in advance that $A[1] > 0$. Describe an even faster algorithm for the same task. (The handout's hint: this is really easy.)

### (a) Any sorted array

> [!hint]- Hint
> Look at the differences $A[i] - i$. Since the entries are distinct integers, how do consecutive differences compare?

> [!solution]- Solution
> **The idea.** We are not looking for a given *value* in $A$, but for a position where value and index agree. Turn it into a value search: let $\Delta[i] = A[i] - i$. The entries are distinct integers in increasing order, so each step to the right raises $A$ by **at least** 1 while it raises the index by exactly 1:
> $$
> \Delta[i+1] = A[i+1] - (i+1) \;\ge\; (A[i] + 1) - (i+1) = \Delta[i].
> $$
> So $\Delta[1\,..\,n]$ is sorted, and $A[i] = i$ exactly when $\Delta[i] = 0$: binary search for $0$ in $\Delta$. There is no need to build $\Delta$ — whenever the search wants $\Delta[mid]$, compute $A[mid] - mid$. In words: if $A[mid] < mid$, then $\Delta[i] \le \Delta[mid] < 0$ for every $i \le mid$, so nothing in $A[lo\,..\,mid]$ can match and the search moves right; if $A[mid] > mid$, nothing in $A[mid\,..\,hi]$ can match and it moves left.
>
> **What the recursion computes.** $\textsf{FindMatch}(A, lo, hi)$ returns an index $i$ with $lo \le i \le hi$ and $A[i] = i$, or None if there is no such index. The answer is $\textsf{FindMatch}(A, 1, n)$.
> ```text
> FindMatch(A, lo, hi):
>   if lo > hi
>     return None
>   mid ← ⌊(lo + hi)/2⌋
>   if A[mid] = mid
>     return mid
>   else if A[mid] < mid          ⟨⟨Δ[mid] < 0: no match in A[lo .. mid]⟩⟩
>     return FindMatch(A, mid + 1, hi)
>   else                          ⟨⟨Δ[mid] > 0: no match in A[mid .. hi]⟩⟩
>     return FindMatch(A, lo, mid − 1)
> ```
> **Base case.** An empty range ($lo > hi$) contains no match. **Divide and conquer.** One recursive call, on the half that may still contain a match (the argument above); its answer is returned unchanged. The official solution also gives the same algorithm as a `while` loop that updates $lo$ and $hi$.
>
> **Time.** $T(n) = T(\lfloor n/2\rfloor) + O(1) = O(\log n)$: at most $\lfloor \lg n\rfloor + 1$ probes, attained when there is no match and every probe moves right.
>
> **Why "distinct integers" matters.** Both words are used in the inequality above. With $A = [1.5, 2]$ (not integers) the differences $0.5, 0$ are not sorted; the search probes $A[1] = 1.5 > 1$, moves left, and misses $A[2] = 2$. With $A = [1, 1, 1]$ (not distinct) the differences $0, -1, -2$ decrease, and the search misses $A[1] = 1$.
>
> **Answer.** Binary search for $0$ in $A[i] - i$, computed on the fly: $O(\log n)$ time.

### (b) When A[1] > 0

> [!hint]- Hint
> What does $A[1] > 0$ say about $\Delta[1]$? Then use that $\Delta$ is sorted.

> [!solution]- Solution
> **The idea.** $A[1]$ is a positive integer, so $\Delta[1] = A[1] - 1 \ge 0$, and since $\Delta$ is sorted, $\Delta[i] \ge \Delta[1]$ for every $i$. Two cases:
> - $A[1] = 1$: index 1 is a match. (There may be others, as in $A = [1, 2, 3, 7]$; any one will do.)
> - $A[1] > 1$: then $\Delta[i] \ge \Delta[1] > 0$, that is $A[i] > i$, for **every** $i$ — no match anywhere.
>
> ```text
> FindMatchPos(A[1 .. n]):
>   if A[1] = 1
>     return 1
>   else
>     return None
> ```
> **Answer.** Check whether $A[1] = 1$: $O(1)$ time.

## Problem 2 — A local minimum

> [!question] Problem 2
> You are given an array $A[1\,..\,n]$ with $A[1] \ge A[2]$ and $A[n-1] \le A[n]$. An entry $A[x]$ is a **local minimum** if $A[x-1] \ge A[x]$ and $A[x] \le A[x+1]$ (so $2 \le x \le n-1$, and implicitly $n \ge 3$). For example, this array has exactly six local minima, marked ▲:
>
> | $x$ | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
> |---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
> | $A[x]$ | 9 | 7 | 7 | 2 | 1 | 3 | 7 | 5 | 4 | 7 | 3 | 3 | 4 | 8 | 6 | 9 |
> | | | ▲ | | | ▲ | | | | ▲ | | ▲ | ▲ | | | ▲ | |
>
> Describe and analyze a fast algorithm that returns the index of one local minimum. On the array above it could return $9$, since $A[9]$ is a local minimum. (The handout's hint: with these boundary conditions, every array has at least one local minimum. Why?)

> [!hint]- Hint
> Why must a local minimum exist? Consider the smallest of $A[2\,..\,n-1]$. Then look at a middle pair $A[mid], A[mid+1]$: which half of the array satisfies the same boundary conditions as the whole?

> [!solution]- Solution
> **Why a local minimum exists.** Let $x$ be the index of a smallest value among $A[2\,..\,n-1]$. Each neighbor of $x$ is either inside that range, so not smaller, or is an end: $A[1] \ge A[2]$ and $A[n] \ge A[n-1]$ by the boundary conditions. Either way $A[x-1] \ge A[x] \le A[x+1]$.
>
> **The idea.** That argument used nothing but the shape at the two ends: the array **goes down at its left end** ($A[1] \ge A[2]$) and **goes up at its right end** ($A[n-1] \le A[n]$). So *any* subarray $A[lo\,..\,hi]$ with at least three entries, $A[lo] \ge A[lo+1]$ and $A[hi-1] \le A[hi]$ contains a local minimum strictly inside it — and an index strictly inside the subarray has the same two neighbors in $A$, so it is a local minimum of $A$ too. Now look at one pair in the middle:
> - if $A[mid] < A[mid+1]$, the array goes up at $mid$, so $A[lo\,..\,mid+1]$ goes down at its left end (as before) and up at its right end;
> - otherwise $A[mid] \ge A[mid+1]$, the array goes down at $mid$, so $A[mid\,..\,hi]$ goes down at its left end and up at its right end (as before).
>
> Either way, about half the array still has the shape that guarantees an answer.
>
> **What the recursion computes.** Given $hi - lo \ge 2$, $A[lo] \ge A[lo+1]$ and $A[hi-1] \le A[hi]$, $\textsf{LocalMin}(A, lo, hi)$ returns an index $x$ with $lo < x < hi$ that is a local minimum of $A$. The boundary conditions of the problem are exactly these assumptions for $\textsf{LocalMin}(A, 1, n)$.
> ```text
> LocalMin(A, lo, hi):         ⟨⟨needs hi − lo ≥ 2, A[lo] ≥ A[lo+1], A[hi−1] ≤ A[hi]⟩⟩
>   if hi − lo = 2
>     return lo + 1
>   mid ← ⌊(lo + hi)/2⌋
>   if A[mid] < A[mid + 1]
>     return LocalMin(A, lo, mid + 1)
>   else
>     return LocalMin(A, mid, hi)
> ```
> **Base case.** With three entries the only inside index is $lo+1$, and the assumptions say exactly $A[lo] \ge A[lo+1] \le A[hi]$.
>
> **Divide.** If $hi - lo \ge 3$, then $lo < mid$ and $mid + 1 < hi$, so both possible calls are on shorter subarrays with at least three entries, and they satisfy the assumptions by the two bullets above.
>
> **Conquer.** The returned index lies strictly inside the smaller subarray, hence strictly inside $A[lo\,..\,hi]$, and is a local minimum of $A$ — return it.
>
> **Time.** Count the inside positions, $k = hi - lo - 1$: the left call keeps $\lceil k/2\rceil$ of them and the right call $\lfloor k/2\rfloor$, and the recursion stops at $k = 1$. So there are at most $\lceil \lg(n-2)\rceil$ comparisons; as a recurrence, $T(n) \le T(\lceil n/2\rceil + 1) + O(1) = O(\log n)$ (the $+1$ is removed by the domain transformation of [[2-algorithms/01-recursion#ignoring-floors-and-ceilings|§1.7]]).
>
> **On the example.**
>
> | range | $mid$ | $A[mid]$ vs $A[mid+1]$ | next range |
> |---|---|---|---|
> | $1..16$ | 8 | $5 \ge 4$ | $8..16$ |
> | $8..16$ | 12 | $3 < 4$ | $8..13$ |
> | $8..13$ | 10 | $7 \ge 3$ | $10..13$ |
> | $10..13$ | 11 | $3 \ge 3$ | $11..13$ |
> | $11..13$ | — | base case | return 12 |
>
> It returns $12$ ($A[11] = 3 \ge A[12] = 3 \le A[13] = 4$) after $\lceil\lg 14\rceil = 4$ comparisons — a different local minimum than the handout's $9$, which is fine.
>
> **About the official version.** It stops when $hi - lo < 100$ and returns "the minimum of $A[lo\,..\,hi]$ by brute force". With ties that minimum can sit at the end $lo$ — on $[1, 1, 2]$ it is index $1$, which has no left neighbor — so take the minimum of the inside part $A[lo+1\,..\,hi-1]$ instead, as in the existence argument. (Its comment also asks for $A[lo] > A[lo+1]$, which the else-branch does not guarantee; the non-strict version above is what the recursion maintains.)
>
> **Answer.** Binary search that keeps "down at the left end, up at the right end": $O(\log n)$ time, at most $\lceil\lg(n-2)\rceil$ comparisons.

## Problem 3 — The median of two sorted arrays

> [!question] Problem 3
> You are given two sorted arrays $A[1\,..\,n]$ and $B[1\,..\,n]$ of distinct integers. Describe a fast algorithm that finds the median of $A \cup B$, meaning its $n$-th smallest element. For example, for
> $$
> A[1\,..\,8] = [0, 1, 6, 9, 12, 13, 18, 20], \qquad B[1\,..\,8] = [2, 4, 5, 8, 17, 19, 21, 23]
> $$
> the algorithm should return $9$. (The handout's hint: what can you learn by comparing one element of $A$ with one element of $B$?)

> [!hint]- Hint
> Compare the middle elements $A[m]$ and $B[m]$, $m = \lceil n/2\rceil$. Count how many elements are certainly smaller than the larger of the two, and how many are certainly larger than the beginning of the other array.

> [!solution]- Solution
> **The idea.** Let $m = \lceil n/2\rceil$ and suppose $A[m] > B[m]$ (the other case is symmetric). This one comparison places a lot of elements relative to the median, the $n$-th smallest of the $2n$:
> - **$A[m]$ is at or above the median.** It is larger than $A[1\,..\,m-1]$ and, since $A[m] > B[m]$, larger than $B[1\,..\,m]$: at least $2m - 1 \ge n - 1$ smaller elements. So everything in $A[m+1\,..\,n]$ is **above** the median.
> - **$B[1\,..\,n-m]$ is below the median.** Take $j \le n - m$. Larger than $B[j]$ are $B[j+1\,..\,n]$ (at least $m$ elements) and $A[m\,..\,n]$ ($n - m + 1$ elements, all greater than $B[m] \ge B[j]$): at least $n + 1$ larger elements, so $B[j]$ is at most the $(n-1)$-st smallest — strictly **below** the median.
>
> Now drop $A[m+1\,..\,n]$ and $B[1\,..\,n-m]$ — the same number, $n - m = \lfloor n/2\rfloor$, from above and from below the median. The median keeps its place in the middle: it is the $m$-th smallest of the $2m$ elements that remain, which form two sorted arrays $A[1\,..\,m]$ and $B[n-m+1\,..\,n]$ of length $m$. That is the same problem, half the size.
>
> **What the recursion computes.** For sorted arrays of the same length $n \ge 1$ with distinct elements, $\textsf{Median}(A[1\,..\,n], B[1\,..\,n])$ returns the $n$-th smallest element of $A \cup B$.
> ```text
> Median(A[1 .. n], B[1 .. n]):
>   if n = 1
>     return min{A[1], B[1]}
>   m ← ⌈n/2⌉
>   if A[m] > B[m]
>     return Median(A[1 .. m], B[n − m + 1 .. n])
>   else
>     return Median(A[n − m + 1 .. n], B[1 .. m])
> ```
> **Base case.** $n = 1$: the smaller of the two. It is needed — for $n = 1$, $m = 1$ and the recursive call would be on the same two arrays. (The official solution uses brute force below a huge constant; any constant works.)
>
> **Divide and conquer.** One call on two arrays of length $\lceil n/2\rceil$ (pass index ranges, not copies); by the argument above its answer is the answer.
>
> **Time.** $T(n) = T(\lceil n/2\rceil) + O(1) = O(\log n)$: exactly $\lceil\lg n\rceil$ comparisons $A[m]$ vs $B[m]$, plus one at the base.
>
> **On the example.**
>
> | $n$ | $m$ | $A[m]$ vs $B[m]$ | keep |
> |---|---|---|---|
> | 8 | 4 | $9 > 8$ | $A$: 0 1 6 9 · $B$: 17 19 21 23 |
> | 4 | 2 | $1 < 19$ | $A$: 6 9 · $B$: 17 19 |
> | 2 | 1 | $6 < 17$ | $A$: 9 · $B$: 17 |
> | 1 | — | base case | $\min\{9, 17\} = 9$ |
>
> **A correction.** The official write-up's counts are slightly off: it lists $A[1\,..\,m] \cup B[1\,..\,m-1]$ as the elements below $A[m]$ (it is $A[1\,..\,m-1] \cup B[1\,..\,m]$), and for $B[n-m]$ it counts $B[m+1\,..\,n]$, which for odd $n$ gives only $n$ larger elements — enough for "$\le$ the median", not for "below"; counting $B[n-m+1\,..\,n]$ as above gives $n + 1$.
>
> **Answer.** Compare $A[\lceil n/2\rceil]$ with $B[\lceil n/2\rceil]$, drop the $\lfloor n/2\rfloor$ elements after the larger and before the smaller, recurse: $O(\log n)$ time.

The first step of Problem 3's example, drawn out (it gives the idea away):

<!-- fig:lab-06a-median-step -->
<figure class="cs-fig"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 620 228" width="620" height="228" role="img" style="font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-size:14px"><title>two sorted arrays of eight numbers; the compared middle pair 9 and 8 is highlighted, the last four of A and the first four of B are greyed out as dropped</title><defs><marker id="ARR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs><text x="62" y="74" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:16px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">A</text><text x="62" y="154" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:16px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">B</text><text x="115" y="46" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:11.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">1</text><text x="161" y="46" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:11.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">2</text><text x="207" y="46" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:11.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">3</text><text x="253" y="46" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:11.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">4</text><text x="299" y="46" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:11.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">5</text><text x="345" y="46" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:11.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">6</text><text x="391" y="46" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:11.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">7</text><text x="437" y="46" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:11.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">8</text><rect x="92" y="58" width="46" height="32" rx="0" fill="var(--paper)" stroke="currentColor" stroke-width="1.2"/><text x="115" y="74.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">0</text><rect x="138" y="58" width="46" height="32" rx="0" fill="var(--paper)" stroke="currentColor" stroke-width="1.2"/><text x="161" y="74.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">1</text><rect x="184" y="58" width="46" height="32" rx="0" fill="var(--paper)" stroke="currentColor" stroke-width="1.2"/><text x="207" y="74.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">6</text><rect x="230" y="58" width="46" height="32" rx="0" fill="var(--paper)" stroke="currentColor" stroke-width="1.2"/><text x="253" y="74.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">9</text><rect x="276" y="58" width="46" height="32" rx="0" fill="var(--muted)" fill-opacity="0.16" stroke="var(--muted)" stroke-width="1.1"/><text x="299" y="74.5" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:14px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">12</text><rect x="322" y="58" width="46" height="32" rx="0" fill="var(--muted)" fill-opacity="0.16" stroke="var(--muted)" stroke-width="1.1"/><text x="345" y="74.5" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:14px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">13</text><rect x="368" y="58" width="46" height="32" rx="0" fill="var(--muted)" fill-opacity="0.16" stroke="var(--muted)" stroke-width="1.1"/><text x="391" y="74.5" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:14px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">18</text><rect x="414" y="58" width="46" height="32" rx="0" fill="var(--muted)" fill-opacity="0.16" stroke="var(--muted)" stroke-width="1.1"/><text x="437" y="74.5" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:14px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">20</text><rect x="92" y="138" width="46" height="32" rx="0" fill="var(--muted)" fill-opacity="0.16" stroke="var(--muted)" stroke-width="1.1"/><text x="115" y="154.5" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:14px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">2</text><rect x="138" y="138" width="46" height="32" rx="0" fill="var(--muted)" fill-opacity="0.16" stroke="var(--muted)" stroke-width="1.1"/><text x="161" y="154.5" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:14px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">4</text><rect x="184" y="138" width="46" height="32" rx="0" fill="var(--muted)" fill-opacity="0.16" stroke="var(--muted)" stroke-width="1.1"/><text x="207" y="154.5" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:14px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">5</text><rect x="230" y="138" width="46" height="32" rx="0" fill="var(--muted)" fill-opacity="0.16" stroke="var(--muted)" stroke-width="1.1"/><text x="253" y="154.5" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:14px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">8</text><rect x="276" y="138" width="46" height="32" rx="0" fill="var(--paper)" stroke="currentColor" stroke-width="1.2"/><text x="299" y="154.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">17</text><rect x="322" y="138" width="46" height="32" rx="0" fill="var(--paper)" stroke="currentColor" stroke-width="1.2"/><text x="345" y="154.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">19</text><rect x="368" y="138" width="46" height="32" rx="0" fill="var(--paper)" stroke="currentColor" stroke-width="1.2"/><text x="391" y="154.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">21</text><rect x="414" y="138" width="46" height="32" rx="0" fill="var(--paper)" stroke="currentColor" stroke-width="1.2"/><text x="437" y="154.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">23</text><rect x="231.5" y="59.5" width="43" height="29" rx="0" fill="none" stroke="var(--accent)" stroke-width="2.4"/><rect x="231.5" y="139.5" width="43" height="29" rx="0" fill="none" stroke="var(--accent)" stroke-width="2.4"/><text x="253" y="114" text-anchor="middle" dominant-baseline="central" fill="var(--accent)" style="font-size:13.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:700;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">9 &gt; 8</text><path d="M279,36 L279,31 L457,31 L457,36" fill="none" stroke="var(--hi)" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/><text x="368" y="21" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">all above the median: drop</text><path d="M95,176 L95,181 L273,181 L273,176" fill="none" stroke="var(--hi)" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/><text x="184" y="194" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">all below the median: drop</text><text x="474" y="74" text-anchor="start" dominant-baseline="central" fill="var(--accent2)" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">keep A[1..4]</text><text x="474" y="154" text-anchor="start" dominant-baseline="central" fill="var(--accent2)" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">keep B[5..8]</text></svg><figcaption><strong>One step of the two-array median.</strong> With <i>n</i> = 8 compare the middle entries <i>A</i>[4] = 9 and <i>B</i>[4] = 8. Since 9 &gt; 8, seven elements (<i>A</i>[1..3] and <i>B</i>[1..4]) are smaller than <i>A</i>[4], so it is at least the 8th smallest and everything after it in <i>A</i> is above the median; every element of <i>B</i>[1..4] has at least nine larger elements, so all four are below it. Dropping four from each side leaves two sorted arrays of length 4 whose median (4th smallest) is still 9.</figcaption></figure>

## Problem 4 — The k-th smallest of two sorted arrays (harder)

> [!question] Problem 4
> Now you are given two sorted arrays $A[1\,..\,m]$ and $B[1\,..\,n]$ (distinct elements, lengths possibly different) and an integer $k$. Describe a fast algorithm that finds the $k$-th smallest element of $A \cup B$. For example, for
> $$
> A[1\,..\,8] = [0, 1, 6, 9, 12, 13, 18, 20], \qquad B[1\,..\,5] = [2, 5, 7, 17, 19], \qquad k = 6
> $$
> the algorithm should return $7$.

> [!hint]- Hint
> The $k$-th smallest element of $A \cup B$ is among $A[1\,..\,k]$ and $B[1\,..\,k]$. Which problem asks for the $k$-th smallest of two arrays of length $k$? (And what if an array is shorter than $k$?)

> [!solution]- Solution
> **The idea: reduce to Problem 3.** If $A[i]$ is among the $k$ smallest elements of $A \cup B$, then so are $A[1\,..\,i-1]$, so $i \le k$; the same holds in $B$. Hence the $k$ smallest elements of $A \cup B$ all lie in $A[1\,..\,k] \cup B[1\,..\,k]$, and the $k$-th smallest of $A \cup B$ is the $k$-th smallest of $A[1\,..\,k] \cup B[1\,..\,k]$ — exactly what $\textsf{Median}$ computes for two arrays of length $k$.
>
> **Short arrays.** If $k > m$, the array $A[1\,..\,k]$ does not exist. Pretend that $A[i] = \infty$ for $i > m$ (and $B[i] = \infty$ for $i > n$): whenever $\textsf{Median}$ reads such an entry, use $\infty$ instead of failing. Padding sits above every real element, so it does not change which element is $k$-th smallest — there are at least $k$ real ones, because $k \le m + n$.
>
> **Large $k$.** For $k$ near $m + n$ the arrays of length $k$ are wasteful. Turn the problem upside down: the $k$-th smallest is the $\ell$-th **largest**, $\ell = m + n - k + 1$, and by the same argument it is the $\ell$-th largest of the last $\ell$ entries of each array, $A[k-n\,..\,m]$ and $B[k-m\,..\,n]$, where indices below $1$ read as $-\infty$. The $\ell$-th largest of two sorted arrays of length $\ell$ is Problem 3 upside down: negate every element and read the arrays backward (so they are sorted again), take the $\ell$-th smallest with $\textsf{Median}$, and negate the result.
> ```text
> Select(A[1 .. m], B[1 .. n], k):
>   if k < (m + n)/2
>     ⟨⟨read A[i] = ∞ for i > m and B[i] = ∞ for i > n⟩⟩
>     return Median(A[1 .. k], B[1 .. k])
>   else
>     ⟨⟨read A[i] = −∞ and B[i] = −∞ for i < 1⟩⟩
>     return UpperMedian(A[k − n .. m], B[k − m .. n])
>
> UpperMedian(X[1 .. ℓ], Y[1 .. ℓ]):       ⟨⟨the ℓ-th largest of X ∪ Y⟩⟩
>   return −Median(X′, Y′)  where X′[i] = −X[ℓ + 1 − i] and Y′[i] = −Y[ℓ + 1 − i]
> ```
> The padded and negated arrays are never built — that would take linear time. Every entry is computed in $O(1)$ time when $\textsf{Median}$ asks for it, as with $\Delta$ in Problem 1.
>
> **Equal padding values.** $\textsf{Median}$ assumed distinct elements, and padding repeats $\infty$. It does no harm: its comparison "is the entry of $A$ larger than the entry of $B$?" answers no for two padding entries, exactly as if each of $A$'s padding values were slightly smaller than each of $B$'s — a consistent way to make all values distinct and keep both arrays sorted — and the answer is a real element anyway.
>
> **Time.** $O(\log \ell)$ for the length $\ell$ of the arrays handed to $\textsf{Median}$, and $\textsf{Select}$ picks the smaller option: $O(\log\min\{k, m+n-k+1\}) = O(\log(m+n))$. Either option alone would also be correct and $O(\log(m+n))$.
>
> **On the example.** $k = 6 < 13/2$, so $\textsf{Median}([0, 1, 6, 9, 12, 13], [2, 5, 7, 17, 19, \infty])$:
>
> | $\ell$ | $h = \lceil \ell/2\rceil$ | $A[h]$ vs $B[h]$ | keep |
> |---|---|---|---|
> | 6 | 3 | $6 < 7$ | $A$: 9 12 13 · $B$: 2 5 7 |
> | 3 | 2 | $12 > 5$ | $A$: 9 12 · $B$: 5 7 |
> | 2 | 1 | $9 > 5$ | $A$: 9 · $B$: 7 |
> | 1 | — | base case | $\min\{9, 7\} = 7$ |
>
> **A direct alternative.** Without padding: compare $A[i]$ with $B[j]$ for $i = \min\{m, \lfloor k/2\rfloor\}$ and $j = \min\{n, \lfloor k/2\rfloor\}$. If $A[i] < B[j]$, at most $i + j - 2 \le k - 2$ elements are smaller than $A[i]$, so all of $A[1\,..\,i]$ lie below the $k$-th smallest: drop them and look for the $(k-i)$-th smallest of what is left (symmetrically for $B$; when an array is empty, index into the other; for $k = 1$ take the smaller first element). Each step halves $k$ or empties an array: $O(\log k)$.
>
> **Answer.** Hand the first $k$ entries of each array (or, for large $k$, the last $m+n-k+1$, upside down) to Problem 3's algorithm, reading missing entries as $\pm\infty$: $O(\log\min\{k, m+n-k+1\}) = O(\log(m+n))$ time.

> [!exam] Writing these up
> On Midterm 2 each of these is a full recursive-algorithm answer ([[0-toolkit/02-proof-templates#18-writing-up-a-divide-and-conquer-algorithm|template]]): the 3 description points go to *what the call returns in terms of its parameters* — for $\textsf{LocalMin}$ including its assumptions on the ends of the range, for $\textsf{Median}$ "the $n$-th smallest of two sorted length-$n$ arrays" — then the base case, the exact subarrays of the recursive call, why its answer is the answer (the discarding argument is the heart of the solution), and $T(n) = T(n/2) + O(1) = O(\log n)$.

### Sources for this page

Lab 6a of CS/ECE 374 A, Fall 2026 (September 30), and its official solutions; the solutions here are explained in our own words. Changes from the official solutions: the local-minimum recursion stops at three entries and its brute-force base case is replaced (the official one can return an end of the range when there are ties); the counting argument for the two-array median is corrected; the remark on why distinct *integers* matter, the exact comparison counts, the traces and the direct alternative for Problem 4 are ours. Everything is checked by `tools/checks/labs_06.py`: each algorithm, implemented as written here, agrees with brute force on all small inputs (all sorted arrays of distinct integers from $-4..10$ up to length 8; all arrays over $\{1, 2, 3\}$ up to length 10 with the boundary conditions; all interleavings of two arrays up to length 8; all $m, n \le 6$ and every $k$) and on thousands of random ones; the handout's examples (the six local minima, index 9, the median 9, the answer 7 for $k = 6$) and the traces are reproduced; the comparison counts $\lfloor\lg n\rfloor + 1$, $\lceil\lg(n-2)\rceil$ and $\lceil\lg n\rceil + 1$ are confirmed, and the failure of the official base case on $[1, 1, 2]$ is exhibited.
