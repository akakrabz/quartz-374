---
title: "Lab 7a — Backtracking for longest subsequences"
description: "Recursive backtracking for five subsequence problems: longest decreasing, alternating and convex subsequences (scan the array and remember the last one or two elements chosen) and longest palindrome subsequence and shortest palindrome supersequence (recurse on intervals, from both ends inward)."
tags: [lab, algorithms, backtracking, midterm-2]
---

*Lab 7a · October 7 · CS/ECE 374 A, Fall 2026 · [[concepts/backtracking|backtracking]] · uses [[2-algorithms/02-backtracking#26-longest-increasing-subsequence|§2.6]], [[2-algorithms/02-backtracking#27-longest-increasing-subsequence-take-2|§2.7]] · rubric: [[0-toolkit/06-how-exams-are-graded#11-recursive-algorithms|how exams are graded §11]] · as dynamic programs: [[3-homework-and-exams/lab-07b|Lab 7b]] · solutions: explained from the official solutions*

> [!abstract] In one breath
> All five problems are solved the same way: make one decision, recurse on what is left, and pass the recursion exactly the information about earlier decisions that the next decision needs. For a **decreasing** subsequence that is the last element chosen — the longest-increasing-subsequence recursion of [[2-algorithms/02-backtracking#26-longest-increasing-subsequence|§2.6]] with the comparison flipped. For an **alternating** subsequence it is the last element *and* the direction of the next step, so there are two functions that call each other. For a **convex** subsequence it is the last *two* elements, because convexity compares three consecutive elements. A **palindrome** is built from the outside in, so the last two problems recurse on intervals $A[i\,..\,j]$ and decide what happens to the two end elements. Two warnings: the official convex recurrence is one too small (a pair of elements has length 2, not 1), and the longest palindrome subsequence of the handout's example has length 9, not 7.

## Designing a backtracking algorithm

A **subsequence** keeps some of the elements of a sequence, in their original order; a **substring** (or interval) keeps a contiguous block. `SBSQNC`, `SQUEE` and `EEE` are subsequences of `SUBSEQUENCE` but not substrings; `UBSEQU` is both; `QUEUE`, `EQUUS` and `DIMAGGIO` are neither (more in [[2-algorithms/02-backtracking#26-longest-increasing-subsequence|§2.6]]). "Decreasing" is strict throughout.

The handout's questions for designing a backtracking algorithm, in short:

1. **Solve it by hand first.** What sequence of decisions builds a solution, and what are the options for each one? Here: "is this element in the subsequence?" or "which element comes next?".
2. **What is left after some decisions?** The *shape* of the remaining subproblem — a prefix, a suffix, an interval — and **what you still need to know about the earlier decisions** to make the later ones consistent.
3. **Name the subproblem with a few integers**, usually indices into the array.
4. **State the precise recursive problem**: after some decisions, what question are you asking about the remaining input? The handout calls this the most important step; it is also the first thing the rubric grades.
5. **Write the recursion**: try every option for exactly *one* decision, and solve each resulting subproblem recursively.

The write-up format is [[0-toolkit/02-proof-templates#19-writing-up-a-backtracking-algorithm|template §19]]. For the five problems the answers to questions 1–3 are:

| problem | the one decision | what the recursion must remember | subproblem | function |
|---|---|---|---|---|
| 1. decreasing | is $A[j]$ in? | the last element chosen | suffix $A[j\,..\,n]$ and an earlier index $i$ | $\textsf{LDSsmaller}(i, j)$ |
| 2. alternating | is $A[j]$ in? | the last element chosen and the direction of the next step | the same, one function per direction | $\textsf{LASabove}(i, j)$, $\textsf{LASbelow}(i, j)$ |
| 3. convex | which element comes next? | the last two elements chosen | two indices $i < j$ | $\textsf{LXS}(i, j)$ |
| 4. palindrome subsequence | what happens to the two ends? | nothing | interval $A[i\,..\,j]$ | $\textsf{LPS}(i, j)$ |
| 5. palindrome supersequence | which ends form the outer pair? | nothing | interval $A[i\,..\,j]$ | $\textsf{SPS}(i, j)$ |

Conventions on this page: the array $A$ is global and the functions' parameters are indices; a maximum over the empty set is 0 unless stated otherwise. All examples use the handout's array

$$
A = 3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5, 8, 9, 7, 9, 3, 2, 3, 8, 4, 6, 2, 7 \qquad (n = 23).
$$

## Problem 1 — Longest decreasing subsequence

> [!question] Problem 1
> Given an array $A[1\,..\,n]$ of integers, compute the length of a longest **decreasing** subsequence; a sequence $B[1\,..\,\ell]$ is decreasing if $B[i] < B[i-1]$ for every $i \ge 2$. For the array above the answer is 5, because $9, 6, 5, 4, 2$ is a longest decreasing subsequence (one of many). Describe a recursive backtracking algorithm; don't worry about the running time.

> [!hint]- Hint
> This is the longest *increasing* subsequence problem upside down. Scan the array left to right and decide about one element at a time: what do you need to know about the elements already chosen to decide whether $A[j]$ can be added?

> [!solution]- Solution
> **The idea.** Go through the array from left to right and decide, for each element, whether it is in the subsequence. Adding $A[j]$ keeps the subsequence decreasing exactly when $A[j]$ is smaller than the **last element chosen** — nothing else about the past matters. So a recursive call needs to know where the scan is ($j$) and which element was chosen last (an earlier index $i$). To start with "nothing chosen yet", pretend the last chosen element is a sentinel $A[0] = +\infty$, which every element is below. This is [[2-algorithms/02-backtracking#26-longest-increasing-subsequence|§2.6]]'s $\textsf{LISbigger}$ with the comparison flipped.
>
> **The recursive problem.** For $0 \le i < j \le n+1$, let $\textsf{LDSsmaller}(i, j)$ be the length of a longest decreasing subsequence of the suffix $A[j\,..\,n]$ **in which every element is smaller than $A[i]$**. With the sentinel $A[0] = +\infty$, the answer is $\textsf{LDSsmaller}(0, 1)$.
> $$
> \textsf{LDSsmaller}(i, j) = \begin{cases}
> 0 & \text{if } j > n\\
> \mathit{skip} & \text{if } A[j] \ge A[i]\\
> \max\{\mathit{skip},\ 1 + \mathit{take}\} & \text{otherwise}
> \end{cases}
> $$
> where $\mathit{skip} = \textsf{LDSsmaller}(i, j+1)$ and $\mathit{take} = \textsf{LDSsmaller}(j, j+1)$.
>
> - **Base case.** $j > n$: the suffix is empty, and so is its only subsequence — length 0.
> - **Recursive calls.** If $A[j] \ge A[i]$, then $A[j]$ cannot be used, and we skip it. Otherwise we try both: skip $A[j]$, which is $\textsf{LDSsmaller}(i, j+1)$; or take it, after which every later element must be smaller than $A[j]$, which is $\textsf{LDSsmaller}(j, j+1)$.
> - **Combine.** The larger of the skip value and $1 +$ the take value.
> - **Correct because** a decreasing subsequence of $A[j\,..\,n]$ below $A[i]$ either avoids $A[j]$, or starts with $A[j] < A[i]$ and continues with a decreasing subsequence of $A[j+1\,..\,n]$ below $A[j]$ (induction on $n - j$).
> - **Time.** Each call makes at most two calls on a suffix one element shorter: $T(m) \le 2T(m-1) + O(1)$, so $T(n) = O(2^n)$. On a strictly decreasing array every call branches and $\textsf{LDSsmaller}(0, 1)$ makes exactly $2^{n+1} - 1$ calls.
>
> **Other ways.** *What comes next?* (as in [[2-algorithms/02-backtracking#27-longest-increasing-subsequence-take-2|§2.7]]): let $\textsf{LDSfirst}(i)$ be the length of a longest decreasing subsequence of $A[i\,..\,n]$ that **begins with** $A[i]$; then $\textsf{LDSfirst}(i) = 1 + \max\{\textsf{LDSfirst}(j) \mid j > i,\ A[j] < A[i]\}$, and the answer is $\max_i \textsf{LDSfirst}(i)$, or $\textsf{LDSfirst}(0) - 1$ with $A[0] = +\infty$. Scanning from *right to left* and remembering the *next* chosen element (a prefix plus a later index, with a sentinel $A[n+1] = -\infty$) works just as well. And with no new recursion at all: a longest decreasing subsequence of $A$ is a longest increasing subsequence of $-A$ (negation flips every comparison), or of $A$ reversed.
>
> **Answer.** $\textsf{LDSsmaller}(0, 1)$ with $A[0] = +\infty$; it returns 5 on the example. As a dynamic program: [[3-homework-and-exams/lab-07b#problem-1--longest-decreasing-subsequence|Lab 7b, Problem 1]].

## Problem 2 — Longest alternating subsequence

> [!question] Problem 2
> Given an array $A[1\,..\,n]$ of integers, compute the length of a longest **alternating** subsequence. A sequence $B[1\,..\,\ell]$ is alternating if $B[i] < B[i-1]$ for every even index $i \ge 2$ and $B[i] > B[i-1]$ for every odd index $i \ge 3$: its steps go down, up, down, up, …, starting with a step **down**. For the array above the answer is 17, because $3, 1, 4, 1, 5, 2, 6, 5, 8, 7, 9, 3, 8, 4, 6, 2, 7$ is a longest alternating subsequence (one of many).

> [!hint]- Hint
> The same scan as in Problem 1. Whether $A[j]$ may come next now depends on the last element chosen *and* on whether the next step must go up or down. Use two functions, one for each direction.

> [!solution]- Solution
> **The idea.** Scan as in Problem 1. Whether $A[j]$ can be added depends on the last element chosen, $A[i]$, and on the direction of the next step: up (then we need $A[j] > A[i]$) or down ($A[j] < A[i]$). Once $A[j]$ is added, the direction flips. The direction is one bit of memory, so instead of a third parameter we use **two functions**, one per direction, that call each other. The alternating sequences of the problem start with a step down; to start the recursion with "nothing chosen yet", let a sentinel $A[0] = -\infty$ be the last element chosen, with the next step going **up**: every first element is above $-\infty$, and after it the steps go down, up, … as required.
>
> **The recursive problems.** For $0 \le i < j \le n+1$:
> - $\textsf{LASabove}(i, j)$ is the length of a longest subsequence of $A[j\,..\,n]$ whose first element (if any) is **larger than $A[i]$** and whose steps go down, up, down, … — an alternating subsequence that starts above $A[i]$;
> - $\textsf{LASbelow}(i, j)$ is the length of a longest subsequence of $A[j\,..\,n]$ whose first element (if any) is **smaller than $A[i]$** and whose steps go up, down, up, … — an "inverted" alternating subsequence that starts below $A[i]$.
>
> In words: the longest way to continue after choosing $A[i]$ when the next step must go up, respectively down. With $A[0] = -\infty$ the answer is $\textsf{LASabove}(0, 1)$.
> $$
> \textsf{LASabove}(i, j) = \begin{cases}
> 0 & \text{if } j > n\\
> \textsf{LASabove}(i, j+1) & \text{if } A[j] \le A[i]\\
> \max\big\{\textsf{LASabove}(i, j+1),\ 1 + \textsf{LASbelow}(j, j+1)\big\} & \text{otherwise}
> \end{cases}
> $$
> $$
> \textsf{LASbelow}(i, j) = \begin{cases}
> 0 & \text{if } j > n\\
> \textsf{LASbelow}(i, j+1) & \text{if } A[j] \ge A[i]\\
> \max\big\{\textsf{LASbelow}(i, j+1),\ 1 + \textsf{LASabove}(j, j+1)\big\} & \text{otherwise}
> \end{cases}
> $$
>
> - **Base case.** $j > n$: only the empty subsequence, length 0.
> - **Recursive calls.** Skip $A[j]$: the same function at $(i, j+1)$. If $A[j]$ lies on the required side of $A[i]$, also take it: the step after $A[j]$ goes the other way, so the rest is the *other* function at $(j, j+1)$.
> - **Combine.** The larger of the skip value and $1 +$ the take value.
> - **Correct because** an alternating subsequence of $A[j\,..\,n]$ that starts above $A[i]$ either avoids $A[j]$, or starts with $A[j] > A[i]$, and then its other elements form a subsequence of $A[j+1\,..\,n]$ that starts below $A[j]$ and goes up, down, …; the other function is symmetric.
> - **Time.** At most two calls on a shorter suffix: $O(2^n)$, as in Problem 1.
>
> **Other way.** *What comes next?*: let $\textsf{Down}(i)$ be the length of a longest alternating subsequence of $A[i\,..\,n]$ that begins with $A[i]$ (first step down), and $\textsf{Up}(i)$ the same with the first step up. Then $\textsf{Down}(i) = 1 + \max\{\textsf{Up}(j) \mid j > i,\ A[j] < A[i]\}$, $\textsf{Up}(i) = 1 + \max\{\textsf{Down}(j) \mid j > i,\ A[j] > A[i]\}$, and the answer is $\max_i \textsf{Down}(i)$. The book calls these sequences *oscillating*: [[2-algorithms/02-backtracking-exercises#d-longest-oscillating-subsequence|Exercise 2.4(d)]]. Lab 7b adds an $O(n)$ greedy algorithm, with its proof.
>
> **Answer.** $\textsf{LASabove}(0, 1)$ with $A[0] = -\infty$; 17 on the example. As a dynamic program: [[3-homework-and-exams/lab-07b#problem-2--longest-alternating-subsequence|Lab 7b, Problem 2]].

## Problem 3 — Longest convex subsequence

> [!question] Problem 3
> Given an array $A[1\,..\,n]$ of integers, compute the length of a longest **convex** subsequence. A sequence $B[1\,..\,\ell]$ is convex if $B[i] - B[i-1] > B[i-1] - B[i-2]$ for every $i \ge 3$: every step is strictly larger than the step before. For the array above the answer is 6, because $3, 1, 1, 2, 5, 9$ (steps $-2, 0, 1, 3, 4$) is a longest convex subsequence (one of many).

> [!hint]- Hint
> Whether an element may follow depends on the last *two* elements chosen. Make them the parameters, and choose the next element.

> [!solution]- Solution
> **The idea.** The convexity condition involves three consecutive elements: $x$ may follow $\ldots, y, z$ if and only if $x - z > z - y$, that is, $y + x > 2z$. So the recursion must remember the last **two** elements chosen. A scan that decides about one element at a time would then need three indices (the two remembered elements and the scan position). It is simpler to ask *which element comes next?*, as in [[2-algorithms/02-backtracking#27-longest-increasing-subsequence-take-2|§2.7]], with the two parameters naming the first two elements of the rest of the subsequence.
>
> **The recursive problem.** For $1 \le i < j \le n$, let $\textsf{LXS}(i, j)$ be the length of a longest convex subsequence of $A[i\,..\,n]$ **whose first two elements are $A[i]$ and $A[j]$**. (The official solutions call it LCS; on this site LCS is the longest *common* subsequence.)
> $$
> \textsf{LXS}(i, j) = \max\Big(\{2\} \cup \big\{1 + \textsf{LXS}(j, k) \bigm| j < k \le n,\ A[i] + A[k] > 2A[j]\big\}\Big)
> $$
> The answer is $\max_{1 \le i < j \le n} \textsf{LXS}(i, j)$ if $n \ge 2$, and $n$ if $n \le 1$ (every sequence of length at most 2 is convex).
>
> - **Base case.** No $k$ qualifies (for instance $j = n$): the subsequence is just $A[i], A[j]$, of length 2.
> - **Recursive calls.** $\textsf{LXS}(j, k)$ for every $k > j$ with $A[i] + A[k] > 2A[j]$ — every possible third element.
> - **Combine.** One (for $A[i]$) plus the best of them, or 2 if there is none.
> - **Correct because** a convex subsequence that starts $A[i], A[j]$ either stops there or continues with some $A[k]$, $k > j$. In the second case everything from $A[j]$ on is a convex subsequence that starts $A[j], A[k]$, and the only condition that involves $A[i]$ is the one at $A[j]$: $A[i] + A[k] > 2A[j]$. Conversely, putting $A[i]$ in front of a convex subsequence that starts $A[j], A[k]$ keeps it convex when that inequality holds.
> - **Time.** The calls below $\textsf{LXS}(i, j)$ correspond to distinct chains of indices $j < k_1 < k_2 < \cdots$, so there are at most $2^{n-j}$ of them (exactly that many if every subsequence is convex, as for $A[k] = 2^k$), each with $O(n)$ work of its own. With the outer maximum over all pairs: $O(n^3 2^n)$.
>
> **A correction.** The official solutions write the recurrence as $1 + \max\{\ldots\}$ with $\max\varnothing = 0$. That makes $\textsf{LXS}(i, j) = 1$ for a pair with no possible third element, although the pair itself has length 2 — so every value comes out one too small, and on the example the answer comes out 5 instead of 6. The base value must be 2, as above (the same fix applies to their sentinel version and to their Lab 7b pseudocode, which initializes each entry to 1).
>
> **Other way: sentinels.** To avoid the maximum over all pairs, shift $A$ so that its smallest element is 0, let $M$ be its largest element, and put $A[-1] = 4M + 3$ and $A[0] = 2M + 1$ in front. Both new triples are convex whatever the first two elements $A[k], A[l]$ of the rest are: $A[-1] + A[k] - 2A[0] = A[k] + 1 > 0$ and $A[0] + A[l] - 2A[k] \ge 2M + 1 - 2M > 0$. So the answer is $\textsf{LXS}(-1, 0) - 2$. (The official proof checks only the first of the two triples.)
>
> **Answer.** $\max_{i < j} \textsf{LXS}(i, j)$ with base value 2 (or $n$ if $n \le 1$); 6 on the example. As a dynamic program: [[3-homework-and-exams/lab-07b#problem-3--longest-convex-subsequence|Lab 7b, Problem 3]]. The book's version of the problem: [[2-algorithms/02-backtracking-exercises#f-longest-convex-subsequence|Exercise 2.4(f)]].

## Problem 4 — Longest palindrome subsequence (harder)

> [!question] Problem 4 (harder)
> Given an array $A[1\,..\,n]$, compute the length of a longest **palindrome** subsequence of $A$; a sequence $B[1\,..\,\ell]$ is a palindrome if $B[i] = B[\ell - i + 1]$ for every index $i$. For the array above the handout's answer is 7, because $4, 9, 5, 3, 5, 9, 4$ is a palindrome subsequence.

> [!warning] The handout's example is wrong
> $4, 9, 5, 3, 5, 9, 4$ is a palindrome subsequence of the array, but not a longest one. The correct answer is **9**: for instance $2, 6, 8, 9, 7, 9, 8, 6, 2$ (positions 7, 8, 12, 13, 14, 15, 19, 21, 22) or $3, 2, 3, 9, 7, 9, 3, 2, 3$. A correct algorithm returns 9.

> [!hint]- Hint
> A palindrome is built from the outside in: its first and last elements are equal. Recurse on an interval $A[i\,..\,j]$ and decide what happens to its two end elements.

> [!solution]- Solution
> **The idea.** Prefixes and suffixes are the wrong shape here: a palindrome pairs its first element with its last, so the natural decisions are about **both ends** of the input. Look at $A[i]$ and $A[j]$. A palindrome subsequence of $A[i\,..\,j]$ may leave out $A[i]$, or leave out $A[j]$, or use both — and then they are its first and last elements, hence equal, with a palindrome subsequence of $A[i+1\,..\,j-1]$ in between. Every option leaves a smaller **interval**, and nothing about earlier decisions needs remembering: the outer pairs already chosen do not restrict what happens inside.
>
> **The recursive problem.** For $1 \le i \le n+1$ and $i - 1 \le j \le n$, let $\textsf{LPS}(i, j)$ be the length of a longest palindrome subsequence of the interval $A[i\,..\,j]$. The answer is $\textsf{LPS}(1, n)$. The base cases are $\textsf{LPS}(i, i-1) = 0$ and $\textsf{LPS}(i, i) = 1$; for $i < j$,
> $$
> \textsf{LPS}(i, j) = \max\begin{cases}
> \textsf{LPS}(i+1, j)\\
> \textsf{LPS}(i, j-1)\\
> 2 + \textsf{LPS}(i+1, j-1) & \text{only if } A[i] = A[j]
> \end{cases}
> $$
>
> - **Base cases.** An empty interval has only the empty palindrome; a single element is a palindrome of length 1.
> - **Recursive calls and combine.** The best of the two or three options above.
> - **Correct because** a longest palindrome subsequence of $A[i\,..\,j]$, $i < j$, avoids $A[i]$, avoids $A[j]$, or uses both as its outer pair, as explained above; and each option is achievable.
> - **Time.** On an interval of length $m$, $T(m) \le 2T(m-1) + T(m-2) + O(1)$, so $T(n) = O(3^n)$.
>
> **A shortcut, with its proof.** When $A[i] = A[j]$, the third option always wins, so the recursion may return $2 + \textsf{LPS}(i+1, j-1)$ right away. A shortcut like this needs a proof, and here is one: $\textsf{LPS}(i+1, j) \le 2 + \textsf{LPS}(i+1, j-1)$, because a longest palindrome subsequence of $A[i+1\,..\,j]$ either avoids $A[j]$ (then it lies in $A[i+1\,..\,j-1]$), or is $A[j]$ alone (length 1), or ends with $A[j]$ (then removing its first and last elements leaves a palindrome subsequence of $A[i+1\,..\,j-1]$ that is two shorter). Symmetrically, $\textsf{LPS}(i, j-1) \le 2 + \textsf{LPS}(i+1, j-1)$. With the shortcut every call makes at most two calls, so the recursion takes $O(2^n)$ time. (The official solutions prove the same claim with an exchange argument: in a longest palindrome subsequence, replace the outer elements by $A[i]$ and $A[j]$.)
>
> **Answer.** $\textsf{LPS}(1, n)$; **9** on the example (not the handout's 7). As a dynamic program: [[3-homework-and-exams/lab-07b#problem-4--longest-palindrome-subsequence|Lab 7b, Problem 4]]. The same recurrence for strings: [[2-algorithms/03-dynamic-programming-exercises#a-longest-palindromic-subsequence|Exercise 3.9(a)]].

## Problem 5 — Shortest palindrome supersequence (harder)

> [!question] Problem 5 (harder)
> Given an array $A[1\,..\,n]$, compute the length of a shortest **palindrome supersequence** of $A$ — a palindrome that contains $A$ as a subsequence ($B$ is a supersequence of $C$ if and only if $C$ is a subsequence of $B$). For $A = 3, 1, 4, 1, 5, 9, 2, 6, 5, 3$ the answer is 15, because $3, 5, 6, 2, 9, 5, 1, 4, 1, 5, 9, 2, 6, 5, 3$ is a shortest palindrome supersequence.

> [!hint]- Hint
> Look at the outer pair of a shortest answer: two equal symbols. At least one of them must be an element of $A$ (otherwise delete both). Which elements can they be?

> [!solution]- Solution
> **The idea.** Intervals again, from the outside in. Take a shortest palindrome $P$ that contains $A[i\,..\,j]$, and fix where the elements of $A[i\,..\,j]$ sit in it. The first and last symbols of $P$ are equal. If neither of them is one of those elements, deleting both leaves a shorter palindrome that still contains $A[i\,..\,j]$ — impossible. So the outer pair is used by $A[i]$ (at the front), by $A[j]$ (at the back), or by both:
> - only $A[i]$: then $P = A[i] \cdot P' \cdot A[i]$, where the last symbol is an inserted copy, and the palindrome $P'$ must contain $A[i+1\,..\,j]$;
> - only $A[j]$: symmetrically, $P'$ must contain $A[i\,..\,j-1]$;
> - both: then $A[i] = A[j]$, and $P'$ must contain $A[i+1\,..\,j-1]$.
>
> Conversely, every option can be realized by wrapping a shortest palindrome supersequence of the smaller interval in two copies of $A[i]$ (or of $A[j]$).
>
> **The recursive problem.** For $1 \le i \le n+1$ and $i - 1 \le j \le n$, let $\textsf{SPS}(i, j)$ be the length of a shortest palindrome supersequence of the interval $A[i\,..\,j]$. The answer is $\textsf{SPS}(1, n)$. The base cases are $\textsf{SPS}(i, i-1) = 0$ and $\textsf{SPS}(i, i) = 1$; for $i < j$,
> $$
> \textsf{SPS}(i, j) = 2 + \min\begin{cases}
> \textsf{SPS}(i+1, j)\\
> \textsf{SPS}(i, j-1)\\
> \textsf{SPS}(i+1, j-1) & \text{only if } A[i] = A[j]
> \end{cases}
> $$
>
> - **Base cases.** The empty interval needs nothing (the empty sequence is a palindrome); a single element is its own palindrome.
> - **Correct because** of the three cases above; **time** as for $\textsf{LPS}$, $O(3^n)$.
>
> **Shortcut.** Here the shortcut for equal ends is easy to justify: a palindrome that contains $A[i+1\,..\,j]$ also contains $A[i+1\,..\,j-1]$, so $\textsf{SPS}(i+1, j-1) \le \textsf{SPS}(i+1, j)$, and likewise $\textsf{SPS}(i+1, j-1) \le \textsf{SPS}(i, j-1)$. So when $A[i] = A[j]$ the answer is $2 + \textsf{SPS}(i+1, j-1)$.
>
> **The two problems are one.** With both shortcuts, the $\textsf{SPS}$ and $\textsf{LPS}$ recurrences have the same shape, and induction on $j - i$ gives
> $$
> \textsf{SPS}(i, j) = 2(j - i + 1) - \textsf{LPS}(i, j).
> $$
> (Equal ends add 2 to the length of the interval and 2 to both values; otherwise, for an interval of length $m$, $2 + \min\{2(m-1) - \textsf{LPS}(i+1, j),\ 2(m-1) - \textsf{LPS}(i, j-1)\} = 2m - \textsf{LPS}(i, j)$.) In words: the elements of $A$ that a shortest palindrome pairs with each other form a longest palindrome subsequence, and every other element gets an inserted partner. In the handout's answer the outer 3s, the two 1s and the middle 4 come from $A$ — the palindrome subsequence $3, 1, 4, 1, 3$ of length 5 — and the other five elements $5, 9, 2, 6, 5$ each get a partner: $10 + 5 = 15$.
>
> **Answer.** $\textsf{SPS}(1, n)$; 15 on the example. As a dynamic program: [[3-homework-and-exams/lab-07b#problem-5--shortest-palindrome-supersequence|Lab 7b, Problem 5]]. For strings: [[2-algorithms/03-dynamic-programming-exercises#b-shortest-palindromic-supersequence|Exercise 3.9(b)]].

### Sources for this page

Lab 7a handout (CS/ECE 374 A, Fall 2026, October 7) and its official solutions, explained in our own words; the function names ($\textsf{LDSsmaller}$, $\textsf{LASabove}$, $\textsf{LXS}$, …) follow the site's LIS pages rather than the solutions. Two corrections: the official convex recurrence needs base value 2 (it returns 5 instead of 6 on the example), and the handout's palindrome example has answer 9, not 7. Every recurrence on this page is implemented as plain recursion and compared with brute force over all subsequences (for supersequences, over all palindromes of each length) on all arrays of length at most 7 over $\{1, 2, 3, 4\}$, all permutations of length at most 7 and random arrays of length up to 12; the handout's examples (also by exhaustive search), every witness subsequence, the two corrections, the shortcut lemmas, the identity $\textsf{SPS} = 2m - \textsf{LPS}$ and the call counts behind the running times are checked by `tools/checks/labs_07.py`.
