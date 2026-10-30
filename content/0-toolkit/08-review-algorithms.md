---
title: "Review: algorithms for Midterm 2 (Ch 1–9)"
description: "Exam review for Midterm 2 (Mon Nov 9): what is on it and what is not, the five problem types with how to attack and how they are graded, what to know cold in each chapter — recurrences and their solutions, backtracking, dynamic-programming shapes and evaluation orders, whatever-first and depth-first search, topological sort, strong components, which shortest-path algorithm when, the Bellman–Ford and Floyd–Warshall interfaces — a catalog of graph-reduction tricks, the traps that cost the most points, a short-answer drill, a cheat-sheet list and a day-by-day study plan."
tags: [toolkit, algorithms, midterm-2]
aliases: ["Midterm 2 review", "algorithms review"]
---

*Scope: Erickson's* Algorithms, *Chapters 1–3, 5, 6 and 8, plus the interfaces of Bellman–Ford's dynamic program and of Floyd–Warshall (§8.7, §9.8) — the material of Homeworks 5–9 and of Midterm 2, Mon Nov 9, 7–9 pm. Greedy algorithms (Ch 4) and minimum spanning trees (Ch 7) are not on it. Each section links the chapter page that proves its claims; this page only collects. Unit page: [[2-algorithms/index|Part 2 · Algorithms]].*

> [!recipe] How to use this page
> Read §1 first: it says what each exam problem asks and what the answer must contain. Then take one topic section at a time (the plan is in §12): read it, close the page, and rewrite its tables from memory. Whatever you missed goes on your cheat sheet (§11). Do the drill of §10 without looking, and work each problem type of §1 on paper in 20 minutes.

## 1. The exam and how to attack each problem

**When and what.** Monday, November 9, 7–9 pm; the conflict exam is Tuesday, November 10. You may bring **one double-sided 8½″ × 11″ handwritten cheat sheet** and nothing else. The official announcement (Oct 30) says the exam focuses on the material of **Homeworks 5–9**, plus the **interface** of the algorithms introduced in the lecture of Tue Nov 3 (Bellman–Ford as direct dynamic programming, and Floyd–Warshall) — read "interface" as what each takes, returns and costs, so that you can call it as a black box.

| topic | book | homework and labs |
|---|---|---|
| recursion, divide and conquer, recurrences | [[2-algorithms/01-recursion\|Ch 1]] | HW5; Labs 6a, 6b |
| backtracking | [[2-algorithms/02-backtracking\|Ch 2]] | Lab 7a |
| dynamic programming, including tree-shaped DP | [[2-algorithms/03-dynamic-programming\|Ch 3]] | HW6, HW7; Labs 7b, 8a, 8b |
| graphs; reachability and connectivity by whatever-first search; graph reductions | [[2-algorithms/05-basic-graph-algorithms\|Ch 5]] | HW8–9; Lab 9a |
| depth-first search, cycles, topological sort, DP on dags; strong components (in Ch 6 with depth-first search, but not named in the announcement) | [[2-algorithms/06-depth-first-search\|Ch 6]] | HW8–9; Lab 9b |
| shortest paths: breadth-first search, dags, Dijkstra, Bellman–Ford | [[2-algorithms/08-shortest-paths\|Ch 8]] | HW8–9; Lab 10a |
| Bellman–Ford as a dynamic program, Floyd–Warshall — interfaces only | [[2-algorithms/08-shortest-paths#dynamic-programming-formulation\|§8.7]], [[2-algorithms/09-all-pairs-shortest-paths#98-floydwarshall\|§9.8]] | Lab 10b |

**Not on it:** greedy algorithms as a topic (Ch 4) — but a dynamic-programming problem often opens with "show that the obvious greedy strategy fails", and any greedy *algorithm* you hand in needs a formal proof or earns nothing; minimum spanning trees (Ch 7, not lectured this semester); flows (Ch 10–11, not taught in this course); NP-hardness (Ch 12, lectured from Nov 10 and tested on the final); Johnson's algorithm ([[2-algorithms/09-all-pairs-shortest-paths#94-johnsons-algorithm|§9.4]] is in the book but not on the lecture schedule — know only that it exists, §7).

**The rules of the game** (course policies):
- About **20 minutes per problem**, and the problems are "much closer in difficulty to lab problems than homework" — so the labs are the best practice.
- **Every algorithm needs a running time.** A faster correct algorithm beats a slower correct one, which beats a faster incorrect one: write the simple correct solution first.
- **Proofs only where the problem says *prove* or *justify*.** Everywhere else, a precise algorithm and its time.
- **English specifications, no code** — above all, an English description of every recursive function.
- **Cite, don't re-explain.** Any algorithm from lecture, the notes, labs or homework solutions is a black box with a known running time: "breadth-first search from $s$, $O(V+E)$ time". Words like "clearly", "simply" and "just" draw scrutiny, and an ambiguous answer is read unfavorably.

**Format.** The Fall 2025 Midterm 2 and its three practice exams (public, with solutions, on the [Fall 2025 exams page](https://courses.grainger.illinois.edu/CS374AL1/fa2025/exams.html)) — several of whose problems the Spring 2026 practice exams reuse — all have **5 problems in 120 minutes**: short answers, one divide-and-conquer problem, and three problems shared between dynamic programming and graph reductions — one dynamic program and two graph problems in three of the four exams, two dynamic programs and one graph problem in the fourth. In three of the four, a dynamic program opens with a greedy counterexample. The Fall 2026 practice exams will appear on the [Fall 2026 exams page](https://courses.grainger.illinois.edu/cs374al1/fa2026/exams.html), and the course has [practice problems on PrairieLearn](https://us.prairielearn.com/pl/course_instance/223826/assessment/2711985). The full rubrics: [[0-toolkit/06-how-exams-are-graded#11-recursive-algorithms|how exams are graded §11–13]].

> [!recipe] Type 1 — short answers: recurrences, a memoization plan, small graphs
> - **Three recurrences to solve.** For each, write the ratio between consecutive level sums of the recursion tree and name the case: decreasing → root, equal → times $\log n$, increasing → leaves. With unequal pieces, add up $\alpha_i^{\,d}$ (for $f = n$, the fractions themselves): $\tfrac12+\tfrac13+\tfrac16 = 1$ means every level sums to at most $n$ (the first $\log_6 n$ levels to exactly $n$), so $\Theta(n\log n)$. Square roots in $f$ are fine: the ratio $a\,f(n/b)/f(n)$ is still a constant and decides (§2). A log factor in $f$ makes the ratio drift towards 1, so no case applies: sum the levels directly (drill A5).
> - **Memoization structure, evaluation order and time for a given recurrence** (deliberately meaningless): an array with the index ranges the base cases imply; an order read off from which entries each entry reads — which loop is outer, and which way each index runs; time = entries × work per entry, where a $\min$ over $k$ costs $O(n)$ (§4).
> - **Draw a small graph with stated properties** (for example a dag with one source, one sink and several topological orders): the smallest example that works, 3–5 vertices, then check every property, edge directions included.
> - **Mark a depth-first tree, breadth-first tree, shortest-path tree or topological order** on a given graph: follow the stated tie-breaking (usually alphabetical) and write the starting and finishing times next to each vertex as you go (§6).
> - **Grading:** no standard rubric covers this problem; give each answer with its one-line reason (the ratio and the case, the dependency that fixes the order).
> - Practice: the drill of §10; Problem 1 of every Fall 2025 practice exam; PrairieLearn; [[2-algorithms/01-recursion-exercises#exercise-16--nine-recurrences|Exercise 1.6]] (nine recurrences); [[2-algorithms/06-depth-first-search-exercises#exercise-610--is-t-a-depth-first-or-breadth-first-tree|Exercise 6.10]] (which trees are depth-first or breadth-first trees).

> [!recipe] Type 2 — a dynamic program whose part (a) is "the obvious greedy strategy fails"
> - **(a)** State the greedy rule precisely, then give **one concrete input**, the greedy solution with its value, and a better solution with its value. That is the whole answer: no proof that the better solution is optimal. Find it by trying the rule on inputs of size 2 and 3 (§4).
> - **(b)** Backtracking first: the one question about an optimal solution (first element? last element? where to cut? the root?) and what a recursive call must remember. Then the five parts of the template: function with English description, recurrence with base cases, memoization structure, evaluation order, time.
> - **Graded** (b) by the dynamic-programming rubric: 3 for the English description of the function (without a usable one, the rest earns nothing) + 4 for the recurrence (1 base cases, 3 recursive cases; −1½ for an unproved greedy shortcut) + 3 for memoization structure, evaluation order and time, 1 each.
> - Template: [[0-toolkit/02-proof-templates#20-writing-up-a-dynamic-program|dynamic program]] · model answers: [[2-algorithms/03-dynamic-programming-exercises#exercise-31--making-change-in-nadiria|making change]] (counterexample, then the DP), [[2-algorithms/04-greedy-algorithms-exercises#exercise-42--weighted-class-scheduling|weighted class scheduling]] (every greedy rule fails, then the DP) · practice: [[3-homework-and-exams/lab-08a|Lab 8a]], [[3-homework-and-exams/hw6-dynamic-programming|HW6]].

> [!recipe] Type 3 — a dynamic program without a greedy part: sequences, intervals, trees
> - **Read the shape off the input** (§4): one sequence → a prefix or suffix, plus the last element taken if the future depends on it; two sequences → a pair of prefixes; "split", "parenthesize", "cut", or work from both ends → an interval; a tree → a subtree; a dag → a vertex.
> - **Test the recurrence by hand** on an input of size 2 or 3 before you analyze it, and check the base cases against the empty input.
> - **Graded** by the dynamic-programming rubric, as type 2.
> - Model answers: [[2-algorithms/03-dynamic-programming#37-edit-distance|edit distance]], [[2-algorithms/03-dynamic-programming#39-optimal-binary-search-trees|optimal binary search trees]], [[2-algorithms/03-dynamic-programming#310-dynamic-programming-on-trees|independent sets in trees]], [[3-homework-and-exams/hw7-dynamic-programming|HW7]] (two prefixes, two intervals, a box, a subtree), [[3-homework-and-exams/lab-07b|Lab 7b]], [[3-homework-and-exams/lab-08b|Lab 8b]] · practice: [[2-algorithms/03-dynamic-programming-exercises|Chapter 3 exercises]] 3.5–3.10.

> [!recipe] Type 4 — divide and conquer: binary search or a black-box subroutine
> - **Binary search:** find a constant-time test at the middle that tells which half still contains an answer, state that as an invariant ("$A[lo\,..\,hi]$ contains a …"), and check arrays of one and two elements. $T(n) = T(n/2) + O(1) = O(\log n)$. (A past example: the missing term of an arithmetic progression.)
> - **A black-box subroutine** (one the problem gives you, or linear-time selection, or merging): call it, and charge its cost to the node's own work in the recursion tree.
> - **Graded** by the recursive-algorithm rubric: 3 for what the recursive algorithm *returns*, in terms of its parameters — essential when you generalize (the $k$-th smallest, not the median) — + 1 base case + 2 subproblems + 2 combining the results + 2 time (1 recurrence, 1 solution).
> - Template: [[0-toolkit/02-proof-templates#18-writing-up-a-divide-and-conquer-algorithm|divide and conquer]] · model answers: [[3-homework-and-exams/lab-06a|Lab 6a]] (four binary searches), [[2-algorithms/01-recursion-exercises#exercise-113--counting-inversions|counting inversions]], [[2-algorithms/01-recursion#18-linear-time-selection|selection]] · practice: [[3-homework-and-exams/lab-06b|Lab 6b]], [[2-algorithms/01-recursion-exercises|Chapter 1 exercises]].

> [!recipe] Type 5 — one or two graph reductions
> - **Ask what a walk must remember** besides its current vertex — a parity, a counter, the last color, a second token — and put it into the vertices (§8). If every edge increases something (time, height, a counter), the graph is a dag: say so.
> - **Write the four parts in order:** the **graph** (vertices and edges as explicit functions of the input, "directed", weights); the **problem** on it (reachability, shortest path, longest path in a dag, strong components — from which vertex to which, and why that answers the question); the **algorithm**, the fastest correct black box (§7's table); the **time** in the input's parameters.
> - **Graded** by the graph-reduction rubric: 3 for the graph (1 vertices, 1 edges, −½ without "directed", 1 weights) + 3 for the problem (1 which problem, 2 the details) + 2 for the algorithm (−1 slower than necessary, −½ more specific than necessary, −1 re-explained) + 2 for the time in the input's parameters.
> - Template: [[0-toolkit/02-proof-templates#22-solving-a-problem-by-graph-reduction|graph reduction]] · model answers: [[2-algorithms/08-shortest-paths#shortest-paths-by-graph-reduction|three layered reductions]] (Ch 8), [[3-homework-and-exams/lab-09a|Lab 9a]], [[3-homework-and-exams/lab-09b|Lab 9b]] · practice: [[2-algorithms/05-basic-graph-algorithms-exercises|Chapter 5 exercises]] 5.11–5.19, [[2-algorithms/08-shortest-paths-exercises|Chapter 8 exercises]] 8.13–8.17, [[3-homework-and-exams/lab-10a|Lab 10a]], [[3-homework-and-exams/lab-10b|Lab 10b]].

## 2. Chapter 1 — Recursion and divide and conquer

[[2-algorithms/01-recursion|Chapter 1]] · concepts: [[concepts/recursion]], [[concepts/divide-and-conquer]], [[concepts/recursion-trees]], [[concepts/master-theorem]], [[concepts/linear-time-selection]]

> [!key] Solving recurrences: the three cases of a recursion tree
> For $T(n) = a\,T(n/b) + f(n)$, level $i$ of the recursion tree has $a^i$ nodes of size $n/b^i$, and consecutive level sums differ by the factor $a\,f(n/b)/f(n)$ — for $f(n) = n^d$, by $a/b^d$.
>
> | level ratio | the sum is dominated by | $T(n)$ |
> |---|---|---|
> | $<1$, decreasing | the root | $\Theta(f(n))$ |
> | $=1$, equal | all $\log_b n$ levels | $\Theta(f(n)\log n)$ |
> | $>1$, increasing | the $n^{\log_b a}$ leaves | $\Theta(n^{\log_b a})$ |
>
> **Pieces of different sizes**, $T(n) = \sum_i T(\alpha_i n) + n^d$: the level ratio is $\sum_i\alpha_i^{\,d}$ — for $d = 1$, the sum of the fractions. Below 1: $\Theta(n^d)$; equal to 1: $\Theta(n^d\log n)$; above 1: $\Theta(n^\rho)$, where $\sum_i\alpha_i^{\,\rho} = 1$.
>
> **Subtractive recurrences** have no ratio; unroll them: $T(n-1) + \Theta(1) = \Theta(n)$, $T(n-1) + \Theta(n) = \Theta(n^2)$, $2T(n-1) + \Theta(1) = \Theta(2^n)$.

The standard recurrences — know every row, and why:

| algorithm | recurrence | case | solution |
|---|---|---|---|
| Tower of Hanoi, moves | $T(n) = 2T(n-1) + 1$ | subtractive | $2^n - 1$ exactly |
| mergesort | $2T(n/2) + \Theta(n)$ | equal | $\Theta(n\log n)$ |
| quicksort, worst case | $T(n-1) + \Theta(n)$ | subtractive | $\Theta(n^2)$ |
| quicksort, random pivot (expected) | $\frac1n\sum_{k=1}^{n}\big(T(k-1) + T(n-k)\big) + \Theta(n)$ | average of splits | $\Theta(n\log n)$ |
| binary search | $T(n/2) + O(1)$ | equal | $\Theta(\log n)$ |
| quickselect, worst case | $T(n-1) + \Theta(n)$ | subtractive | $\Theta(n^2)$ |
| quickselect, median pivot | $T(n/2) + \Theta(n)$ | root | $\Theta(n)$ |
| median of medians (blocks of 5) | $T(n/5) + T(7n/10) + \Theta(n)$ | root: $\tfrac15 + \tfrac7{10} = \tfrac9{10}$ | $\Theta(n)$ |
| median of medians, blocks of 3 | $T(n/3) + T(2n/3) + \Theta(n)$ | equal: $\tfrac13 + \tfrac23 = 1$ | $\Theta(n\log n)$ |
| three pieces adding up to $n$ | $T(n/2) + T(n/3) + T(n/6) + \Theta(n)$ | equal: $\tfrac12 + \tfrac13 + \tfrac16 = 1$ | $\Theta(n\log n)$ |
| splitting multiplication | $4T(n/2) + \Theta(n)$ | leaves, ratio 2 | $\Theta(n^2)$ |
| Karatsuba | $3T(n/2) + \Theta(n)$ | leaves, ratio $3/2$ | $\Theta(n^{\lg 3}) = O(n^{1.585})$ |
| Strassen-like | $7T(n/2) + \Theta(n^2)$ | leaves, ratio $7/4$ | $\Theta(n^{\lg 7}) = O(n^{2.808})$ |
| exponentiation by repeated squaring | $T(n/2) + O(1)$ | equal | $\Theta(\log n)$ multiplications |

Floors, ceilings and additive constants inside $T(\cdot)$ never change the answer ([[2-algorithms/01-recursion#ignoring-floors-and-ceilings|domain transformation]]); the rubric wants the recurrence **and** its solution, a point each.

> [!recipe] Divide and conquer on the exam
> - **Binary search on an invariant** (the method: §1, type 4; [[3-homework-and-exams/lab-06a|Lab 6a]]: $A[i] = i$, a local minimum, medians of two sorted arrays).
> - **Throw away a constant fraction with linear work:** $T(n) = T(n/2) + O(n) = O(n)$. **Recurse on both halves with linear combining:** $2T(n/2) + O(n) = O(n\log n)$ (mergesort, [[2-algorithms/01-recursion-exercises#exercise-113--counting-inversions|counting inversions]]).
> - **Generalize** when the recursion needs it, and describe the general problem: the $k$-th smallest instead of the median; return extra values (a count *and* a sorted copy, the minimum *and* the maximum).
> - **Black boxes you may cite:** MergeSort, $O(n\log n)$; linear-time selection of the $k$-th smallest, $O(n)$; binary search, $O(\log n)$; Karatsuba, $O(n^{\lg 3})$; repeated squaring, $O(\log n)$ multiplications.
> - **Correctness** (only if asked): strong induction on the size — the recursive calls are correct by hypothesis; prove only that combining them is ([[0-toolkit/02-proof-templates#17-proving-a-recursive-algorithm-correct|template]]). Never unroll the recursion.

## 3. Chapter 2 — Backtracking

[[2-algorithms/02-backtracking|Chapter 2]] · concepts: [[concepts/backtracking]], [[concepts/subset-sum]], [[concepts/longest-increasing-subsequence]]

A backtracking algorithm makes **one decision per call** and tries every option consistent with the decisions already made, combining the answers with $\lor$, $+$, $\max$ or $\min$. The design step is the recursive problem: **the input still to be processed plus the smallest summary of the past** a call needs ([[2-algorithms/02-backtracking#24-the-general-pattern|§2.4]]). A nontrivial summary means you solve a more general problem — describe *that* problem, and say which call answers the original question. Pass indices, not copies of subarrays.

| problem | recursive function: what it returns | the call remembers | backtracking | as a DP |
|---|---|---|---|---|
| subset sum | $\textsf{SubsetSum}(X, i, T)$: does some subset of $X[1\,..\,i]$ sum to $T$? | the remaining target | $O(2^n)$ | $O(nT)$ |
| text segmentation | $\textsf{Splittable}(i)$: can $A[i\,..\,n]$ be split into words? | where the rest starts | $O(2^n)$ | $O(n^2)$ |
| LIS, take 1 | $\textsf{LISbigger}(i, j)$: longest increasing subsequence of $A[j\,..\,n]$ above $A[i]$ | the last element taken | $O(2^n)$ | $O(n^2)$ |
| LIS, take 2 | $\textsf{LISfirst}(i)$: longest increasing subsequence of $A[i\,..\,n]$ that starts with $A[i]$ | the element just taken | $O(2^n)$ | $O(n^2)$ |
| optimal BST | $\textsf{OptCost}(i, k)$: cost of an optimal search tree for keys $i$ to $k$ | the interval | $\Theta(3^n)$ | $O(n^3)$ |

The exponential bounds come from $T(n)\le 2T(n-1) + O(1)$ (two choices per element), from $T(n)\le\sum_{i<n}T(i) + O(n)$ (take it with equality and subtract the same equation for $n-1$: $T(n) = 2T(n-1) + O(1)$), and, for $\textsf{OptCost}$, from $T(n) = 2\sum_{k<n}T(k) + O(n)$, which gives $T(n) = 3T(n-1) + O(1)$. Writing a backtracking answer: [[0-toolkit/02-proof-templates#19-writing-up-a-backtracking-algorithm|template]], same rubric as divide and conquer. Backtracking itself is rarely the final answer on Midterm 2, but every dynamic program starts as one.

## 4. Chapter 3 — Dynamic programming

[[2-algorithms/03-dynamic-programming|Chapter 3]], [[2-algorithms/06-depth-first-search#64-memoization-and-dynamic-programming|§6.4]] · concepts: [[concepts/dynamic-programming]], [[concepts/memoization]], [[concepts/edit-distance]], [[concepts/optimal-binary-search-trees]], [[concepts/dynamic-programming-on-trees]], [[concepts/dynamic-programming-on-dags]]

> [!recipe] From backtracking to a dynamic program
> 1. **One question** about an optimal solution whose possible answers split it into smaller instances of the same problem: is $A[i]$ used? what comes first or last? which key is the root? where is the first cut? which edge leaves $v$?
> 2. **The function:** a name, explicit integer parameters (indices into the input, plus any value the rest depends on), and an English sentence saying what it returns for which part of the input — and which call answers the problem.
> 3. **The recurrence**, trying every answer to the question, with base cases.
> 4. **Memoization structure** (an array with index ranges; a field in each node for trees), **evaluation order** (every entry after the entries it reads; say which loop is outer), **time** (entries × work per entry, in the input's parameters).
>
> Write-up: [[0-toolkit/02-proof-templates#20-writing-up-a-dynamic-program|template]] · rubric 3 + 4 + 3 · the method spelled out slowly: [[3-homework-and-exams/hw6-dynamic-programming#0-dynamic-programming-in-one-page|HW6 §0]].

**Subproblem shapes.** The parameters decide the array, and the direction of the references decides the order:

| shape | parameters | memoization | evaluation order | examples |
|---|---|---|---|---|
| prefix or suffix | $i$ | 1-D array | $i$ increasing for prefixes, decreasing for suffixes | Fibonacci, $\textsf{Splittable}(i)$, $\textsf{LISfirst}(i)$ |
| suffix plus a value | $(i, t)$ | 2-D array | suffix index decreasing in the outer loop; the value in any order when it refers only to the next suffix | $\textsf{SS}(i, t)$; $\textsf{LISbigger}(i, j)$, where the suffix index is $j$ |
| prefix or suffix plus a counter | $(i, c)$ | 2-D array | as for the plain prefix or suffix, outer; the counter inner | at most $k$ jumps ([[3-homework-and-exams/lab-08a\|Lab 8a]]) |
| two prefixes | $(i, j)$ | $(m+1)\times(n+1)$ array | $i$ increasing (outer), $j$ increasing (inner) | $\textsf{Edit}(i, j)$, longest common subsequence |
| interval | $(i, j)$ | $n\times n$ array, upper triangle $i\le j$ | $i$ decreasing (outer), $j$ increasing (inner) — or by increasing length $j - i$ | $\textsf{OptCost}(i, k)$, palindromes ([[3-homework-and-exams/lab-07b\|Lab 7b]]), [[3-homework-and-exams/lab-08b\|Lab 8b]] |
| subtree | a node $v$ | a field in each node | postorder: children first | $\textsf{MISyes}(v)$, $\textsf{MISno}(v)$; [[3-homework-and-exams/hw7-dynamic-programming\|HW7]] problem 3 |
| dag vertex | a vertex $v$ | a field in each vertex | postorder of a depth-first search = reverse topological order | $\textsf{LLP}(v)$ |
| number of edges, vertex | $(i, v)$ | $V\times V$ array | $i$ increasing (outer) | Bellman–Ford's $\mathit{dist}_{\le i}(v)$ (§7) |
| two vertices and a bound | $(u, v, r)$ | $V\times V$ array, in place | $r$ increasing (outer) | Floyd–Warshall (§7) |

**The standard dynamic programs** (base cases and proofs on the chapter page; the full table with evaluation orders: [[2-algorithms/03-dynamic-programming#the-chapters-dynamic-programs-at-a-glance|at a glance]]):

| problem | function | recursive case | time |
|---|---|---|---|
| Fibonacci | $\textsf{Fib}(i)$ | $\textsf{Fib}(i-1) + \textsf{Fib}(i-2)$ | $O(n)$ |
| text segmentation | $\textsf{Splittable}(i)$: $A[i\,..\,n]$ splits into words | $\bigvee_{j = i}^{n}\big(\textsf{IsWord}(i, j)\land\textsf{Splittable}(j+1)\big)$ | $O(n^2)$ |
| longest increasing subsequence | $\textsf{LISfirst}(i)$: longest in $A[i\,..\,n]$ starting with $A[i]$ | $1 + \max\{\textsf{LISfirst}(j) \mid j > i,\ A[j] > A[i]\}$ | $O(n^2)$ |
| edit distance | $\textsf{Edit}(i, j)$ of $A[1\,..\,i]$ and $B[1\,..\,j]$ | $\min\{\textsf{Edit}(i-1, j) + 1,\ \textsf{Edit}(i, j-1) + 1,\ \textsf{Edit}(i-1, j-1) + [A[i]\ne B[j]]\}$ | $O(mn)$ |
| subset sum | $\textsf{SS}(i, t)$: some subset of $X[i\,..\,n]$ sums to $t$ | $\textsf{SS}(i+1, t)\lor\textsf{SS}(i+1, t - X[i])$ | $O(nT)$ |
| optimal BST | $\textsf{OptCost}(i, k)$ for keys $i$ to $k$ | $\sum_{j=i}^{k}f[j] + \min_{i\le r\le k}\{\textsf{OptCost}(i, r-1) + \textsf{OptCost}(r+1, k)\}$ | $O(n^3)$ |
| independent set in a tree | $\textsf{MISyes}(v)$, $\textsf{MISno}(v)$ in the subtree of $v$ | $1 + \sum_{w}\textsf{MISno}(w)$ and $\sum_{w}\max\{\textsf{MISyes}(w), \textsf{MISno}(w)\}$, over children $w$ | $O(n)$ |
| longest path in a dag | $\textsf{LLP}(v)$: longest path from $v$ to $t$ | $\max_{v\to w}\{\ell(v\to w) + \textsf{LLP}(w)\}$ | $O(V+E)$ |

$[A[i]\ne B[j]]$ is 1 if the symbols differ and 0 otherwise; a $\max$ over nothing is 0 in $\textsf{LISfirst}$ but $-\infty$ in $\textsf{LLP}$ (a vertex other than $t$ without outgoing edges cannot reach $t$). Subset sum's $O(nT)$ is **pseudo-polynomial**: polynomial in the value $T$, exponential in its number of bits. Optimal BST has $O(n^2)$ entries but $O(n)$ work each.

**Trees and dags.** In a tree-shaped DP (shape table above) the time is the sum over all nodes — $O(n)$ when a node's work is $O(1 + \text{children})$. Every DP's dependency graph is a dag, and every recursion over a dag is a DP evaluated in postorder of a depth-first search; that is why "longest path" is easy in dags and NP-hard in general.

> [!recipe] Part (a): the obvious greedy strategy fails
> What the answer contains: §1, type 2. Look for an input where the locally best first choice blocks two good later ones. **Example:** paying 6 with coins of values 1, 3 and 4, "largest coin first" pays $4 + 1 + 1$, three coins; $3 + 3$ uses two. More counterexamples: [[2-algorithms/03-dynamic-programming#35-warning-greed-is-stupid|§3.5]], the four failing rules for class scheduling in [[2-algorithms/04-greedy-algorithms#42-scheduling-classes|§4.2]], and [[2-algorithms/04-greedy-algorithms-exercises#exercise-41--nine-greedy-rules-for-class-scheduling|Exercise 4.1]]. A greedy *algorithm* is never the answer to part (b) unless you also prove it ([[0-toolkit/02-proof-templates#21-proving-a-greedy-algorithm-correct|exchange argument]]).

## 5. Chapter 5 — Graphs and whatever-first search

[[2-algorithms/05-basic-graph-algorithms|Chapter 5]] · concepts: [[concepts/graphs]], [[concepts/whatever-first-search]], [[concepts/graph-reductions]]

| notion | what to know cold |
|---|---|
| graph | $G = (V, E)$; edges $uv$ (undirected) or $u\to v$ (directed); $V$ and $E$ also denote the numbers of vertices and edges; $\sum_v\deg(v) = 2E$ |
| walk, path | a walk may repeat vertices, a path may not; a shortest walk is a path, a longest walk need not exist |
| components | undirected: maximal connected subgraphs; directed: $\textsf{reach}(s)$, and strong components (§6) |
| default input | a **standard adjacency list**: every time bound assumes it unless the problem says otherwise |

| operation | adjacency list | adjacency matrix |
|---|---|---|
| space | $\Theta(V+E)$ | $\Theta(V^2)$ |
| is $u\to v$ an edge? | $O(1+\deg(u))$ | $O(1)$ |
| list the neighbors of $v$ | $O(1+\deg(v))$ | $\Theta(V)$ |
| a whole search | $O(V+E)$ | $O(V^2)$ |

**Whatever-first search** ([[2-algorithms/05-basic-graph-algorithms#55-whatever-first-search|§5.5]]) puts edges into a bag, marks a vertex the first time it comes out, and marks **exactly the vertices reachable from $s$**; the parent edges form a spanning tree of them. With bag operations of cost $T$ it runs in $O(V + ET)$:

| bag | search | time | gives you |
|---|---|---|---|
| anything with $O(1)$ operations | whatever-first | $O(V+E)$ | $\textsf{reach}(s)$ and a spanning tree of it |
| stack | depth-first | $O(V+E)$ | a depth-first tree; starting and finishing times (§6) |
| queue | breadth-first | $O(V+E)$ | fewest-edge paths from $s$: a breadth-first tree |
| priority queue | best-first | $O(V + E\log E)$ | shortest paths with non-negative weights (Dijkstra), widest paths |

**Wrapped in a loop over all vertices** (WFSAll) the same search counts and labels the components of an undirected graph in $O(V+E)$ ([[2-algorithms/05-basic-graph-algorithms#disconnected-graphs|disconnected graphs]]). In a directed graph a search from $s$ marks $\textsf{reach}(s)$; a search from $t$ in the reversed graph marks every vertex that can reach $t$. On an exam, name the **problem** — "reachability from $s$" — and the most general search that solves it: "whatever-first search" (trap 8 of §9).

## 6. Chapter 6 — Depth-first search

[[2-algorithms/06-depth-first-search|Chapter 6]] · concepts: [[concepts/depth-first-search]], [[concepts/topological-sort]], [[concepts/dynamic-programming-on-dags]], [[concepts/strongly-connected-components]]

DFS$(v)$ marks $v$, then calls itself on every unmarked out-neighbor; DFSAll restarts it from every unmarked vertex, in $O(V+E)$ time. A clock that ticks when a vertex is first visited (its **starting time** $v.\mathit{pre}$) and when its call returns (its **finishing time** $v.\mathit{post}$) numbers the events $1, \ldots, 2V$; the intervals $[v.\mathit{pre}, v.\mathit{post}]$ are nested (exactly for ancestor and descendant) or disjoint.

| edge $u\to v$ | intervals | finishing times |
|---|---|---|
| tree or forward ($v$ a descendant of $u$) | $u.\mathit{pre} < v.\mathit{pre} < v.\mathit{post} < u.\mathit{post}$ | $u.\mathit{post} > v.\mathit{post}$ |
| back ($v$ an ancestor of $u$, still active) | $v.\mathit{pre} < u.\mathit{pre} < u.\mathit{post} < v.\mathit{post}$ | $u.\mathit{post} < v.\mathit{post}$ |
| cross ($v$ finished, unrelated) | $v.\mathit{pre} < v.\mathit{post} < u.\mathit{pre} < u.\mathit{post}$ | $u.\mathit{post} > v.\mathit{post}$ |

$u.\mathit{post} < v.\mathit{pre}$ never happens for an edge $u\to v$. In an undirected graph every non-tree edge joins an ancestor and a descendant.

> [!key] The facts depth-first search gives you, each in $O(V+E)$
> - **Cycles:** a directed graph has a cycle $\iff$ DFSAll finds a back edge $\iff$ some edge $u\to v$ has $u.\mathit{post} < v.\mathit{post}$ ([[2-algorithms/06-depth-first-search#62-detecting-cycles|§6.2]]).
> - **Topological sort:** in a dag every edge has $u.\mathit{post} > v.\mathit{post}$, so **decreasing finishing time** is a topological order. Preorder is not one, read either way ([[2-algorithms/06-depth-first-search#63-topological-sort|§6.3]]).
> - **Dynamic programming on a dag:** evaluate in **postorder** (increasing finishing time = reverse topological order), so every vertex comes after the vertices its edges point to — or recurse with memoization, which performs that search ([[2-algorithms/06-depth-first-search#dynamic-programming-in-dags|§6.4]]).
> - **Strong components:** $u$ and $v$ are strongly connected if each can reach the other. Contracting every strong component gives the **condensation** $\textsf{scc}(G)$, which is always a dag. **Kosaraju–Sharir:** DFSAll on the reversed graph $\textsf{rev}(G)$, recording the postorder; then, in **decreasing** order of those finishing times, a whatever-first search in $G$ from every still-unmarked vertex marks exactly one strong component — sink components first ([[2-algorithms/06-depth-first-search#66-strong-components-in-linear-time|§6.6]]).

## 7. Chapters 8–9 — Shortest paths

[[2-algorithms/08-shortest-paths|Chapter 8]], [[2-algorithms/09-all-pairs-shortest-paths|Chapter 9]] · concepts: [[concepts/shortest-paths]], [[concepts/breadth-first-search]], [[concepts/dijkstras-algorithm]], [[concepts/bellman-ford]], [[concepts/all-pairs-shortest-paths]], [[concepts/floyd-warshall]]

- **Shortest-path tree:** subpaths of shortest paths are shortest, so one predecessor pointer per vertex stores a shortest path from $s$ to every vertex. It is not a minimum spanning tree.
- **Negative cycles:** if a walk from $s$ to $t$ can touch a negative cycle, there is no shortest walk. Otherwise a shortest walk can be taken to be a path, with at most $V-1$ edges.
- **Relaxing:** an edge $u\to v$ is **tense** if $\mathit{dist}(u) + w(u\to v) < \mathit{dist}(v)$; every single-source algorithm below relaxes tense edges in some order until none is left (Ford's generic algorithm).
- **Never "fix" negative weights by adding a constant** to every edge: a path with $k$ edges grows by $k$ times the constant, which favors paths with few edges.

**Which algorithm when.** Take the first row that applies — to the graph *you built*. The rubric deducts a point for a slower algorithm than necessary.

| the graph | algorithm | time |
|---|---|---|
| unweighted, or all weights equal | breadth-first search | $O(V+E)$ |
| a dag, any weights | DagSSSP: relax the edges in topological order | $O(V+E)$ |
| non-negative weights | Dijkstra (binary heap) | $O(E\log V)$ |
| negative edges, no negative cycle | Bellman–Ford | $O(VE)$ |
| is a negative cycle reachable from $s$? | Bellman–Ford: is an edge still tense after $V-1$ rounds? | $O(VE)$ |
| at most $k$ edges, any weights | DagSSSP in the layered dag of $k+1$ copies (§8) | $O(k(V+E))$ |
| all pairs, unweighted | breadth-first search from every vertex | $O(VE)$ |
| all pairs, non-negative weights | Dijkstra from every vertex | $O(VE\log V)$ |
| all pairs, any weights | Floyd–Warshall (in a dag: DagSSSP from every vertex, $O(VE)$) | $O(V^3)$ |
| longest path | in a dag: DagSSSP with negated weights (or $\textsf{LLP}$); in general graphs NP-hard | $O(V+E)$ |

(The all-pairs bounds assume $E\ge V$, as the book does.) For distances **to** one vertex $t$, run the single-source algorithm from $t$ in the reversed graph; for distances from a few fixed vertices, run it a few times — computing all pairs then costs a point.

> [!key] Bellman–Ford — the interface ([[2-algorithms/08-shortest-paths#87-relax-all-the-edges-bellmanford|§8.7]])
> **Input:** a directed graph $G = (V, E)$, edge weights $w(u\to v)$ of any sign, a source $s$. **Output:** if no negative cycle is reachable from $s$, the distance $\mathit{dist}(v)$ from $s$ to every vertex ($\infty$ if unreachable) and a shortest-path tree; otherwise the report that a negative cycle is reachable from $s$ (an edge still tense after $V-1$ rounds). **Time:** $O(VE)$. Only negative cycles **reachable from $s$** are detected; to detect any, add a new source with weight-0 edges to every vertex.
>
> **As a dynamic program** (the book's formulation, scheduled for the Nov 3 lecture, whose notation may differ): $\mathit{dist}_{\le i}(v)$ is the length of the shortest walk from $s$ to $v$ with **at most $i$ edges**, $\infty$ if none.
> $$
> \mathit{dist}_{\le i}(v) = \begin{cases} 0 & \text{if } i = 0 \text{ and } v = s\\ \infty & \text{if } i = 0 \text{ and } v\ne s\\ \min\big\{\mathit{dist}_{\le i-1}(v),\ \min_{u\to v}\{\mathit{dist}_{\le i-1}(u) + w(u\to v)\}\big\} & \text{if } i\ge 1\end{cases}
> $$
> Memoize in an array $\mathit{dist}[0\,..\,V-1, V]$; evaluate $i$ increasing in the outer loop, the vertices in any order inside; $O(V + E)$ per row, $O(VE)$ in all. Without negative cycles the answer is row $V-1$; a negative cycle is reachable from $s$ exactly when row $V$ would still improve some entry. The table is a layered dag, and Bellman–Ford is DagSSSP on it.

> [!key] Floyd–Warshall — the interface ([[2-algorithms/09-all-pairs-shortest-paths#98-floydwarshall|§9.8]])
> **Input:** a directed graph with edge weights of any sign, as a $V\times V$ matrix ($0$ on the diagonal, $\infty$ for non-edges). **Output:** if $G$ has no negative cycle, $\mathit{dist}[u, v]$, the distance from $u$ to $v$, for **all pairs** (and predecessors, if you keep them). **Time** $O(V^3)$, space $O(V^2)$. **Negative cycles:** $G$ has one if and only if $\mathit{dist}[v, v] < 0$ for some $v$ at the end.
>
> **Recurrence:** number the vertices $1, \ldots, V$; $\textsf{dist}(u, v, r)$ is the length of the shortest path from $u$ to $v$ whose **intermediate** vertices are all at most $r$:
> $$
> \textsf{dist}(u, v, r) = \begin{cases} w(u\to v) & \text{if } r = 0\\ \min\{\textsf{dist}(u, v, r-1),\ \textsf{dist}(u, r, r-1) + \textsf{dist}(r, v, r-1)\} & \text{if } r\ge 1\end{cases}
> $$
> **$r$ is the outer loop**, $u$ and $v$ inside in any order, one $V\times V$ array updated in place. Use it when the answer needs many pairs; for one source or one target a single-source algorithm is faster.

**Johnson's algorithm** ([[2-algorithms/09-all-pairs-shortest-paths#94-johnsons-algorithm|§9.4]]) — Bellman–Ford once from a new vertex, then reweighting so that every weight is non-negative, then $V$ runs of Dijkstra, $O(VE\log V)$ with any weights — is in Chapter 9 but not on the lecture schedule, and the announcement names only Bellman–Ford and Floyd–Warshall. Know that it exists; for all pairs with negative edges on this exam, Floyd–Warshall is the black box to reach for.

## 8. Graph-reduction tricks

When a question depends on more than the current vertex, change the **graph**, not the algorithm. Every trick below builds a new graph and then calls an unchanged search or shortest-path algorithm; the time is that algorithm's time on the new graph, translated into the input's parameters.

| trick | when the question says… | the new graph | on this site |
|---|---|---|---|
| state in the vertices | parity, length mod $k$, the last color or direction, whose turn | vertices $(v, q)$ for every vertex $v$ and state $q$; an edge for every allowed move, updating $q$ | [[2-algorithms/05-basic-graph-algorithms#state-in-the-vertices-walks-of-even-length\|walks of even length]]; [[2-algorithms/05-basic-graph-algorithms-exercises#exercise-514--walks-of-length-divisible-by-3\|Ex. 5.14]]–5.16; [[3-homework-and-exams/lab-09a\|Lab 9a]] |
| layering by a counter $\le k$ | at most $k$ jumps, coupons, negative edges, edges | vertices $(v, c)$ with $0\le c\le k$; a counted move goes from layer $c$ to layer $c+1$; if every edge does, the graph is a dag | [[2-algorithms/08-shortest-paths#shortest-paths-by-graph-reduction\|layered reductions]]; [[3-homework-and-exams/lab-09b#problem-3--two-paid-teleports-every-visit-counts-harder\|Lab 9b, Problem 3]]; [[2-algorithms/08-shortest-paths-exercises#exercise-82--a-few-negative-edges\|Ex. 8.2]] |
| reverse the graph | distances or reachability **to** a target, from every vertex | $\textsf{rev}(G)$: every edge flipped; one search from $t$ | [[2-algorithms/08-shortest-paths-exercises#exercise-85--reinserting-one-edge\|Ex. 8.5]]; [[3-homework-and-exams/lab-10a\|Lab 10a]]; Kosaraju–Sharir |
| a super-source or super-sink | several starts or several targets | a new vertex with weight-0 edges to every start (or from every target) | [[2-algorithms/09-all-pairs-shortest-paths-exercises#exercise-95--distances-between-vertex-classes\|Ex. 9.5]]; Bellman–Ford above; Johnson |
| split a vertex | weights, costs or limits on vertices | $v_{\mathrm{in}}\to v_{\mathrm{out}}$ carrying the vertex's weight; edges enter $v_{\mathrm{in}}$ and leave $v_{\mathrm{out}}$ | [[2-algorithms/08-shortest-paths-exercises#exercise-83--vertex-weights\|Ex. 8.3]]; [[3-homework-and-exams/lab-10a#problem-3--looped-trees-harder\|Lab 10a, Problem 3]] |
| tokens as tuples | two or three things move, one at a time or together | vertices are pairs (or triples) of positions; edges move one or all tokens | [[2-algorithms/05-basic-graph-algorithms-exercises#exercise-513--vidrach-itky-leda\|Ex. 5.13]], 5.18, 5.19; [[3-homework-and-exams/lab-09b#problem-4--counting-distinct-galaxies-harder-starred\|Lab 9b, Problem 4]] |
| contract strong components | a dag algorithm (DP, topological order) on a graph with cycles, when a cycle can be toured freely | $\textsf{scc}(G)$, each component's data combined | [[2-algorithms/06-depth-first-search-exercises#exercise-61--semi-connected-graphs\|Ex. 6.1]], [[2-algorithms/06-depth-first-search-exercises#exercise-69--keys-locked-in-boxes\|Ex. 6.9]] |
| a dag by construction | time, height, index or a counter grows along every move | edges only go "up", so sorting by that quantity is a topological order | [[3-homework-and-exams/lab-09b#problem-2--judys-tour\|Lab 9b, Problem 2]]; [[2-algorithms/06-depth-first-search-exercises#exercise-612--scheduling-jobs-in-a-dag\|Ex. 6.12]] |
| negate the weights | longest or most valuable path | weights $-\ell$, then shortest paths — **only in a dag** | [[2-algorithms/08-shortest-paths#85-directed-acyclic-graphs-depth-first-search\|§8.5]], [[2-algorithms/06-depth-first-search-exercises#exercise-613--paths-in-a-dag-with-one-source-and-one-sink\|Ex. 6.13]] |

**The cost of a trick.** With $s$ states per vertex, an input graph with $n$ vertices and $m$ edges becomes one with $sn$ vertices and, when each move updates the state in one way, $sm$ edges: a search takes $O(s(n+m))$ time. So $k+1$ layers multiply the time by $k+1$; pairs of positions give $n^2$ vertices and $O(nm)$ edges when one token moves at a time, $O(m^2)$ edges when both move together. Say "directed": a state graph is directed even when the input graph is not.

## 9. The traps that cost the most points

> [!trap] Across Chapters 1–9
> 1. **A DP function without explicit parameters or an English description** — "$\textsf{OPT}(i)$", "dp[i][j] is the answer for $i$ and $j$", "the best so far". Without a usable description the recurrence and the iterative details earn nothing — 7 points gone before the description's own 3 are counted.
> 2. **Memoizing in a hash table, or giving no evaluation order.** An array with index ranges (a field per node for trees); say which loop is outer and which way each index runs — and check that every entry is filled before it is read.
> 3. **Time = number of subproblems.** Multiply by the work per entry (optimal BST: $n^2$ entries, $O(n^3)$), and use the right variables ($O(mn)$, not $O(n^2)$, for strings of lengths $m$ and $n$).
> 4. **A greedy algorithm without a proof** earns nothing; an unproved greedy shortcut inside a DP costs 1½. For "show that greedy fails", one concrete counterexample with both values beats any argument.
> 5. **Describing how instead of what** in a recursive algorithm, or generalizing silently: the 3 description points are for what the function returns, in terms of its parameters.
> 6. **A recurrence solved with the wrong case:** $\log_b a$, not $\log_a b$; the equal case multiplies by $\log n$; pieces adding up to exactly $n$ give $\Theta(n\log n)$, not $\Theta(n)$; $T(n-1) + n$ is $\Theta(n^2)$; and a recurrence without its solution (or the reverse) loses a point.
> 7. **Re-explaining a standard algorithm** instead of invoking it ($-1$), or **modifying** it instead of the graph (full credit only if unmistakably correct).
> 8. **A slower algorithm than necessary** ($-1$): Dijkstra on an unweighted graph or a dag, Bellman–Ford with non-negative weights, all pairs when one source is enough. A more specific search than necessary, such as breadth-first search for plain reachability, costs ½.
> 9. **Dijkstra with negative edges** — its $O(E\log V)$ bound and proof need non-negative weights (NonnegativeDijkstra can return wrong distances, §10 item 10); breadth-first search on a weighted graph is simply wrong.
> 10. **Time in $V$ and $E$ of the graph you built.** Translate: "$H$ has $(k+1)n$ vertices and $(k+1)m$ edges, so breadth-first search takes $O(k(n+m))$ time."
> 11. **"Try all paths with depth-first search and keep the best."** Every search finds one path per vertex; a graph can have exponentially many paths.
> 12. **Forgetting "directed"** ($-\tfrac12$) — layered and state graphs are directed even for an undirected input.
> 13. **A dag algorithm on a graph that may have cycles.** Prove that your graph is a dag (every edge increases a quantity), or contract strong components first; longest paths in general graphs are NP-hard.
> 14. **Preorder as a topological order**, or postorder instead of *reverse* postorder.
> 15. **Bellman–Ford "until nothing changes"** (it never stops on a negative cycle), or its DP without the edge count $i$; **Floyd–Warshall with $r$ inside** the other loops (one pass is then not enough).

## 10. Short-answer drill

Thirteen original items in the style of Problem 1. Cover the answers, write yours on paper, then unfold.

> [!question] A. Solve each recurrence, and name the case
> 1. $T(n) = 4T(n/2) + n^2$
> 2. $T(n) = 5T(n/2) + n^2$
> 3. $T(n) = T(n/2) + T(n/3) + n$
> 4. $T(n) = 4T(n/16) + \sqrt n$
> 5. $T(n) = T(n/2) + \lg n$

> [!solution]- Answers A
> 1. Level ratio $4/2^2 = 1$: equal, $\Theta(n^2\log n)$.
> 2. Level ratio $5/2^2 = 5/4 > 1$: leaves, $\Theta(n^{\lg 5})\approx\Theta(n^{2.32})$.
> 3. The pieces add up to $\tfrac12 + \tfrac13 = \tfrac56 < 1$, so level $i$ sums to at most $(5/6)^i n$: root, $\Theta(n)$.
> 4. Level ratio $4\sqrt{n/16}/\sqrt n = 4/4 = 1$: equal, $\Theta(\sqrt n\log n)$.
> 5. One node per level, with values $\lg n, \lg n - 1, \ldots, 1$; the ratio tends to 1 but is not a constant, so sum directly: $\Theta(\log^2 n)$.

> [!question] B. Memoization structure, evaluation order, running time
> Both recurrences are meaningless on purpose; $A[1\,..\,n]$ is an array of numbers.
>
> 6. For $0\le i\le n$ and $0\le j\le k$: $\textsf{Huh}(i, j) = 0$ if $i = 0$ or $j = 0$, and otherwise $\textsf{Huh}(i, j) = \max\{\textsf{Huh}(i-1, j),\ \textsf{Huh}(i, j-1) + A[i],\ 2\,\textsf{Huh}(i-1, j-1)\}$.
> 7. For $1\le i\le j\le n$: $\textsf{Meh}(i, j) = 0$ if $j\le i+1$, and otherwise $\textsf{Meh}(i, j) = A[i]\,A[j] + \min_{i<m<j}\{\textsf{Meh}(i, m) + \textsf{Meh}(m, j)\}$.

> [!solution]- Answers B
> 6. An array $\textsf{Huh}[0\,..\,n, 0\,..\,k]$. Every reference lowers $i$ or $j$ and raises neither, so row by row works: $i$ from 0 up to $n$ in the outer loop, $j$ from 0 up to $k$ in the inner loop (swapping the loops works too). $O(1)$ per entry: $O(nk)$ time.
> 7. An array $\textsf{Meh}[1\,..\,n, 1\,..\,n]$, of which only $i\le j$ is used. Entry $(i, j)$ reads $(i, m)$ with $m < j$ (same row, to the left) and $(m, j)$ with $m > i$ (a lower row): $i$ from $n$ down to 1 in the outer loop, $j$ from $i$ up to $n$ in the inner loop — or all intervals by increasing $j - i$. $O(n^2)$ entries and $O(n)$ work each for the $\min$: $O(n^3)$ time.

> [!question] C. Draw a graph
> 8. A dag with 4 vertices and exactly **one** topological order. Why must every such dag contain a path through all of its vertices?
> 9. A directed graph with 4 vertices and a depth-first search of it (say the start vertices and the order of the adjacency lists) that produces a tree edge, a forward edge, a back edge and a cross edge.
> 10. A directed graph with one negative edge and no negative cycle on which the version of Dijkstra's algorithm that never re-extracts a vertex (NonnegativeDijkstra) returns a wrong distance.

> [!solution]- Answers C
> 8. $a\to b\to c\to d$. In a dag with a unique topological order, two vertices $x, y$ that are consecutive in it must be joined by the edge $x\to y$: otherwise no edge forces $x$ before $y$, and swapping them gives a second topological order. So consecutive vertices form a path through all vertices — and conversely such a path forces the order.
> 9. Edges $a\to b$, $b\to c$, $a\to c$, $c\to a$, $d\to b$; DFSAll in alphabetical order, adjacency lists alphabetical. Times: $a$ $[1, 6]$, $b$ $[2, 5]$, $c$ $[3, 4]$, $d$ $[7, 8]$. Tree edges $a\to b$ and $b\to c$; $c\to a$ is a back edge ($a$ is still active); $a\to c$ is a forward edge ($c$ is a finished descendant of $a$); $d\to b$ is a cross edge ($b$ finished before $d$ started).
> 10. $s\to a$ (weight 1), $s\to b$ (2), $b\to a$ ($-2$), $a\to c$ (2). NonnegativeDijkstra extracts $s$ (0), then $a$ (1), which sets $\mathit{dist}(c) = 3$; then $b$ (2) — the edge $b\to a$ is tense, but $a$ has already been extracted and never is again, so $c$ is extracted with 3. The path $s\to b\to a\to c$ has length 2. Bellman–Ford (or the book's re-inserting Dijkstra, at the risk of exponential time) gets 2.

<!-- fig:rmt2-drill-dag -->
<figure class="cs-fig"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 530 240" width="530" height="240" role="img" style="font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-size:14px"><title>a directed acyclic graph on the vertices a to g</title><defs><marker id="ARR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs><path d="M75.6,111 L172.2,55.2" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M75.6,129 L172.2,184.8" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M78,120 L319.5,120" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M208,45 L319.5,45" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M206.1,53 L321.7,110.8" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M355.6,54 L452.2,109.8" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M206.1,187 L321.7,129.2" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M358,120 L449.5,120" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M78,195 L169.5,195" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><circle cx="60" cy="120" r="18" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="60" y="121" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">a</text><circle cx="190" cy="45" r="18" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="190" y="46" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">b</text><circle cx="340" cy="45" r="18" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="340" y="46" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">c</text><circle cx="340" cy="120" r="18" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="340" y="121" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">e</text><circle cx="470" cy="120" r="18" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="470" y="121" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">f</text><circle cx="190" cy="195" r="18" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="190" y="196" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">d</text><circle cx="60" cy="195" r="18" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="60" y="196" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">g</text></svg><figcaption><strong>The drill graph.</strong> A dag with 7 vertices and 9 edges: a→b, a→d, a→e, b→c, b→e, c→f, d→e, e→f, g→d. Every adjacency list is in alphabetical order, and DFSAll tries the start vertices in alphabetical order.</figcaption></figure>

> [!question] D. On the drill graph above (adjacency lists alphabetical; DFSAll tries $a, b, \ldots, g$ in order)
> 11. Give every vertex's starting and finishing times, and classify every edge that is not a tree edge.
> 12. Give the topological order that this search yields, and one other topological order. Which vertices can come first?
> 13. By dynamic programming over the dag, count the paths from $a$ to $f$ and find the most edges on a path from $a$; say in which order you evaluate. Then give the breadth-first tree from $a$.

> [!solution]- Answers D
> 11. $a$ $[1, 12]$, $b$ $[2, 9]$, $c$ $[3, 6]$, $f$ $[4, 5]$, $e$ $[7, 8]$, $d$ $[10, 11]$, $g$ $[13, 14]$. Tree edges: $a\to b$, $b\to c$, $c\to f$, $b\to e$, $a\to d$. Non-tree edges: $a\to e$ is forward ($e$'s interval lies inside $a$'s); $e\to f$, $d\to e$ and $g\to d$ are cross edges (the head finished before the tail started). No back edge: the graph is a dag.
> 12. Decreasing finishing time: $g, a, d, b, e, c, f$. Another: $a, g, b, c, d, e, f$. Only the two sources, $a$ and $g$, can come first; the graph has 14 topological orders in all.
> 13. Evaluate in postorder, $f, c, e, b, d, a$ (then $g$, not needed) — every vertex after the heads of its edges. Paths to $f$: $N(f) = 1$, $N(c) = N(e) = 1$, $N(b) = N(c) + N(e) = 2$, $N(d) = N(e) = 1$, $N(a) = N(b) + N(d) + N(e) = 4$. The longest path from $a$ has 3 edges, for example $a\to b\to c\to f$. Breadth-first tree from $a$: $a\to b$, $a\to d$, $a\to e$, $b\to c$, $e\to f$; $g$ is not reachable.

More: Problem 1 of the Fall 2025 practice exams, [[2-algorithms/01-recursion-exercises#exercise-16--nine-recurrences|Exercise 1.6]], and the [[2-algorithms/06-depth-first-search-exercises|Chapter 6 exercises]].

## 11. What to put on your cheat sheet

One double-sided letter sheet, handwritten — writing it is half the review. A layout that fits:

**Side 1 — write-ups, recurrences, dynamic programming**
- The three rubrics as checklists: recursive algorithm 3 + 1 + 2 + 2 + 2; dynamic programming 3 + 4 + 3; graph reduction 3 + 3 + 2 + 2 — and the policies of §1 (time for every algorithm; cite, don't re-explain; greedy needs a proof).
- The recursion-tree table, the rule for pieces of different sizes, and the standard recurrences of §2.
- Backtracking: what a call remembers; the two LIS recursions.
- The subproblem-shape table of §4 (shape → array → order) and the eight standard DPs, one line each with their times.
- The greedy-counterexample checklist and the coin example.

**Side 2 — graphs**
- Adjacency list versus matrix; the bag table of §5; WFSAll for components.
- Depth-first search: the edge-classification table, back edge $\iff$ cycle, reverse postorder = topological order, postorder = DP order, $\textsf{LLP}$, Kosaraju–Sharir in two lines, $\textsf{scc}(G)$ is a dag.
- The which-algorithm table of §7, with times.
- Bellman–Ford: interface, $\mathit{dist}_{\le i}(v)$ recurrence, negative-cycle test. Floyd–Warshall: interface, recurrence, "$r$ outer", $\mathit{dist}[v, v] < 0$.
- The graph-reduction tricks of §8, one line each, and the four-part template.
- Your own top five traps from §9.

## 12. A study plan, Oct 30 to Nov 9

> [!tip] Day by day
> | day | topic | do |
> |---|---|---|
> | Fri Oct 30 | the exam, the rubrics | Lab 10b; read §1 and [[0-toolkit/06-how-exams-are-graded#11-recursive-algorithms\|how exams are graded §11–13]]; start the cheat sheet with the three rubrics |
> | Sat Oct 31 | graphs, whatever-first search, reductions | §5 and §8 alongside HW9 (graph algorithms, open until Tue Nov 3); Lab 9a |
> | Sun Nov 1 | recursion, divide and conquer | §2; Labs 6a, 6b; redo one HW5 problem in 20 minutes with the template; drill A |
> | Mon Nov 2 | backtracking, dynamic programming | §3–4; Labs 7a, 7b, 8a, 8b; the [[3-homework-and-exams/hw6-dynamic-programming\|HW6]] and [[3-homework-and-exams/hw7-dynamic-programming\|HW7]] write-ups; drill B; check whether the Fall 2026 practice exams are up |
> | Tue Nov 3 | lecture: Bellman–Ford as DP, Floyd–Warshall | HW9 due; after the lecture, §7 and its two interface boxes; Lab 10a |
> | Wed Nov 4 | depth-first search, topological sort, strong components | Lab 11, “Solve it both ways” (Nov 4, per the course calendar); §6; Lab 9b; drills C and D |
> | Thu Nov 5 | review session (optional) | write the whole cheat sheet (§11); first timed practice exam, 120 minutes, only the sheet |
> | Fri Nov 6 | review session (optional) | grade yesterday's exam with the rubrics; redo every lost point without looking |
> | Sat Nov 7 | timed exam 2 | another practice exam; fix the cheat sheet where it failed you |
> | Sun Nov 8 | timed exam 3 | the Fall 2025 Midterm 2 (or a third practice exam); then §9 once more |
> | Mon Nov 9 | **exam, 7–9 pm** | no new material: reread your sheet and the traps of §9 |
>
> Apart from their Problem 1 (drill material), keep the Fall 2025 exams unseen until you take them timed; the labs and the solved exercises are the material for learning, the practice exams for testing.

Related: [[2-algorithms/index|Part 2 · Algorithms]] · [[0-toolkit/06-how-exams-are-graded|how exams are graded]] · [[0-toolkit/02-proof-templates|proof templates]] · [[3-homework-and-exams/index|homework and exams]] · [[concepts/graph-reductions|graph reductions]] · [[0-toolkit/04-review-regular-and-context-free|review of Chapters 1–5 of Models of Computation]]

### Sources for this page
Erickson, *Algorithms*, Chapters 1–3, 5, 6, 8 and 9 (§9.4 and §9.8), summarized in our own words; every definition, recurrence and running time follows the chapter page it links to. Exam date, scope, policies and format: the CS/ECE 374 A (Fall 2026) course website and the official Midterm 2 announcement of Oct 30, paraphrased, and the public Fall 2025 Midterm 2 exams, whose problem types are described here without copying their problems. The study plan, the cheat-sheet layout, the trick catalog, the coin counterexample and all thirteen drill items are original. Checked by `tools/checks/review_mt2.py`: every recurrence solution numerically (exact closed forms where they exist, otherwise ratios to the claimed bound for growing $n$), the backtracking call counts, every dynamic program in the tables against brute force on random inputs, the depth-first search facts (edge classification, cycles, topological order, Kosaraju–Sharir) on random graphs, breadth-first search, DagSSSP, Dijkstra, Bellman–Ford and Floyd–Warshall — as the boxes state them, including negative-cycle detection — against brute force, and every drill answer by brute force.
