---
title: "Lab 11 — Solve it both ways"
description: "Two problems, each solved as a dynamic program and again as a graph reduction, to see that the two are one computation: the longest increasing subsequence with at most k icky numbers (a table indexed by position and budget; the same pairs as vertices of a layered dag whose longest path is the answer), and the longest palindrome that labels a path of a dag (a function of the two ends of the path, moving inward; the same pairs of vertices as a product dag)."
tags: [lab, algorithms, dynamic-programming, graphs, midterm-2]
---

*Lab 11 · November 4 · CS/ECE 374 A, Fall 2026 · one problem, two write-ups: [[concepts/dynamic-programming|dynamic programming]] and [[concepts/graph-reductions|graph reduction]] · uses [[2-algorithms/03-dynamic-programming#36-longest-increasing-subsequence|§3.6]], [[2-algorithms/06-depth-first-search#64-memoization-and-dynamic-programming|§6.4]] · rubrics: [[0-toolkit/06-how-exams-are-graded#12-dynamic-programming|how exams are graded §12]] and [[0-toolkit/06-how-exams-are-graded#13-graph-reductions|§13]] · in class: [[5-lecture-log/2026-10-29|Thu Oct 29]] · solutions: ours — no official solutions were posted*

> [!abstract] In one breath
> Each problem is to be solved twice, once "using dynamic programming" and once "by reducing it to a standard graph problem", and the lesson is that the two answers are the same computation written in two languages. In Problem 1 a longest increasing subsequence may contain at most $k$ marked ("icky") numbers: the extra thing to remember is how much of the budget is left, so the subproblems are pairs (position, budget) — a table with $n(k+1)$ entries, or a dag with one vertex per pair in which a longest path spells out the subsequence. In Problem 2 the longest palindrome that labels a path of a dag is found from the outside in: the subproblems are pairs of vertices $(u, v)$ with equal labels, the two ends of the palindrome, and one step moves both ends toward each other along an edge. Either way the running time is the number of subproblems times the work for each, or the size of the graph: $O(n^2k)$ for Problem 1, $O(V^2 + E^2)$ (or $O(VE)$ with one more idea) for Problem 2.

> [!key] The dictionary between the two write-ups
> | dynamic program | graph reduction |
> |---|---|
> | a subproblem: one choice of the function's parameters | a vertex |
> | "this subproblem's value uses that one's" | an edge |
> | the $+1$ (or $+2$) in the recurrence | the weight of that edge |
> | max over the choices | the **longest path** |
> | the evaluation order | a topological order — the graph is a dag because the recurrence terminates |
> | the call that gives the final answer | the source and target of the path |
>
> This is what the lecture of [[5-lecture-log/2026-10-29|October 29]] called memoization as a traversal of the dependency graph ([[2-algorithms/06-depth-first-search#64-memoization-and-dynamic-programming|§6.4]]). On an exam, write whichever form you find easier to get right; each has its own rubric.

## Problem 1 — The longest increasing subsequence with at most k icky numbers

> [!question] Problem 1
> You are given an array of numbers, some of which are marked as **icky**, and you want the length of the longest increasing subsequence that includes **at most $k$ icky numbers**. The input is the integer $k$, the number array $A[1\,..\,n]$ and a boolean array $\textit{Icky}[1\,..\,n]$.
>
> For example, for $k = 2$ and the array (icky numbers starred)
>
> $$
> 3^\star\ 1^\star\ 4\ 1^\star\ 5^\star\ 9\ 2^\star\ 6\ 5\ 3^\star\ 5\ 9\ 7\ 9^\star\ 3\ 2\ 3\ 8^\star\ 4\ 6^\star\ 2\ 6^\star
> $$
>
> the algorithm should return 5, the length of the increasing subsequence $4, 5^\star, 6, 7, 9^\star$.
>
> (a) Describe an algorithm for this problem using dynamic programming.
>
> (b) Describe an algorithm for this problem by reducing it to a standard graph problem.

Write $[\textit{Icky}[i]]$ for 1 if $A[i]$ is icky and 0 if not. "Increasing" is strict, as in the example.

### (a) As a dynamic program

> [!hint]- Hint
> Start from the recurrence for the ordinary longest increasing subsequence that *starts with* $A[i]$. What else does the rest of the subsequence need to know about the part already chosen?

> [!solution]- Solution
> **The idea.** For the ordinary problem ([[2-algorithms/03-dynamic-programming#36-longest-increasing-subsequence|§3.6]], [[concepts/longest-increasing-subsequence]]) the function "the longest increasing subsequence of $A[i\,..\,n]$ that starts with $A[i]$" works, because the first element is all that the rest needs to know. Here the rest also needs to know **how many icky numbers it may still use**. Whatever a subproblem needs to know becomes a parameter: add the remaining budget.
>
> **Function.** For $1\le i\le n$ and $0\le c\le k$, let $\textsf{IckyLIS}(i, c)$ be the length of the longest increasing subsequence of $A[i\,..\,n]$ that **starts with $A[i]$** and contains **at most $c$ icky numbers** (counting $A[i]$ itself), or $-\infty$ if there is none — which happens exactly when $A[i]$ is icky and $c = 0$. The answer to the problem is
>
> $$
> \max\Bigl\{0,\ \max_{1\le i\le n}\textsf{IckyLIS}(i, k)\Bigr\}.
> $$
>
> **Recurrence.** The subsequence starts with $A[i]$, which uses up $[\textit{Icky}[i]]$ of the budget; let $c' = c - [\textit{Icky}[i]]$. Then either $A[i]$ is the whole subsequence, or the second element is some $A[j]$ with $j > i$ and $A[j] > A[i]$, and the rest is the best subsequence starting at $A[j]$ with budget $c'$:
>
> $$
> \textsf{IckyLIS}(i, c) = \begin{cases} -\infty & \text{if } c' < 0,\\[2pt] 1 + \max\Bigl\{0,\ \max\bigl\{\textsf{IckyLIS}(j, c') \bigm\vert j > i,\ A[j] > A[i]\bigr\}\Bigr\} & \text{otherwise.}\end{cases}
> $$
>
> **Memoization.** A two-dimensional array $\textsf{IckyLIS}[1\,..\,n][0\,..\,k]$.
>
> **Evaluation order.** Every entry uses only entries with a larger first index: fill $i$ from $n$ down to $1$ (outer loop), $c$ in any order.
>
> **Time.** $n(k + 1)$ entries, $O(n)$ for each: $O(n^2k)$. A budget larger than $n$ is no different from $n$, so this is $O(n^2\min\{k, n\})$.
>
> **A small run.** $A = 2^\star, 5, 3^\star, 4, 6^\star$ and $k = 1$. Filling $i = 5, 4, \dots, 1$:
>
> | $i$ | $A[i]$ | $c = 0$ | $c = 1$ |
> |---|---|---|---|
> | 1 | $2^\star$ | $-\infty$ | 2 |
> | 2 | 5 | 1 | 2 |
> | 3 | $3^\star$ | $-\infty$ | 2 |
> | 4 | 4 | 1 | 2 |
> | 5 | $6^\star$ | $-\infty$ | 1 |
>
> The answer is 2. Entry $(1, 1)$: $2^\star$ spends the budget, so what follows comes from column $c = 0$, where the best larger element gives 1. For $k = 0, 1, 2, 3$ the answers are 1, 2, 3, 4: the full increasing subsequence $2^\star, 3^\star, 4, 6^\star$ needs all three icky numbers.
>
> **Answer.** $\textsf{IckyLIS}(i, c)$ as above, filled for $i = n$ down to 1; return the largest $\textsf{IckyLIS}(i, k)$, or 0. $O(n^2k)$ time.

### (b) As a graph reduction

> [!hint]- Hint
> Make a vertex of every pair (position, number of icky elements used so far). When does one such pair lead to another?

> [!solution]- Solution
> **The idea.** An increasing subsequence is a walk through the array from left to right, hopping from one chosen element to a later, larger one. Hopping is following an edge. To respect the budget, copy the array $k + 1$ times — one layer per number of icky elements used so far — and let an edge into an icky element climb one layer ([[concepts/graph-reductions|graph layering]]). A path can never climb above layer $k$.
>
> **Graph.** A directed graph $G$ with a source $s$, a target $t$ and a vertex $(i, c)$ for every $1\le i\le n$ and $0\le c\le k$, meaning "the subsequence so far ends with $A[i]$ and contains $c$ icky numbers". Its edges:
> - $s\to(i, [\textit{Icky}[i]])$ for every $i$ with $[\textit{Icky}[i]]\le k$, of weight 1 — the subsequence starts with $A[i]$;
> - $(i, c)\to(j, c + [\textit{Icky}[j]])$ whenever $i < j$, $A[i] < A[j]$ and $c + [\textit{Icky}[j]]\le k$, of weight 1 — the next element is $A[j]$;
> - $(i, c)\to t$ for every $i$ and $c$, of weight 0 — the subsequence ends here; and $s\to t$ of weight 0 for the empty subsequence.
>
> Every edge leads from a smaller index to a larger one (with $s$ before and $t$ after everything), so $G$ is a **dag**.
>
> **Problem.** Paths from $s$ to $t$ correspond exactly to increasing subsequences with at most $k$ icky numbers, and the weight of the path is the length of the subsequence. So the answer is the **length of the longest path from $s$ to $t$** in $G$.
>
> **Algorithm.** The longest-path algorithm for dags: dynamic programming over the vertices in topological order ([[2-algorithms/06-depth-first-search#dynamic-programming-in-dags|§6.4]]; equivalently, shortest paths in a dag with all weights negated, [[2-algorithms/08-shortest-paths#85-directed-acyclic-graphs-depth-first-search|§8.5]]), in time linear in the size of $G$.
>
> **Time.** $G$ has $n(k + 1) + 2$ vertices and at most $(k + 1)\binom n2 + n(k + 2) + 1$ edges, and is built by brute force in time proportional to its size: $O(n^2k)$ in all.
>
> **Answer.** The longest path from $s$ to $t$ in the layered dag on the vertices $(i, c)$; $O(n^2k)$ time.

> [!note] The same thing, twice
> The vertices of (b) are the subproblems of a dynamic program, and its edges are that program's recurrence — but not quite the one written in (a). The table of (a) looks forward ("starts with $A[i]$, may still use $c$"), while the vertex $(i, c)$ of (b) looks back ("ends with $A[i]$, has used $c$"). Either direction works in either write-up; the forward-looking graph is the reverse of the backward-looking one, with the budget counted down instead of up.

> [!trap] Two shortcuts that give wrong answers
> - **Forgetting the budget.** The ordinary longest increasing subsequence of the small example has length 4; with $k = 1$ the answer is 2.
> - **Deleting the icky numbers first.** That finds the best subsequence with *no* icky number (length 1 in the small example), not with at most $k$.

## Problem 2 — The longest palindrome along a path of a dag (harder)

> [!question] Problem 2 (to think about later)
> Let $G$ be a directed acyclic graph whose vertices have labels from some fixed alphabet. Every directed path in $G$ has a **label**: the string obtained by concatenating the labels of its vertices. A palindrome is a string that is equal to its reversal. Describe and analyze an algorithm that finds the **length of the longest palindrome that is the label of a path in $G$**.
>
> The handout's example is a dag with 14 vertices labeled S, H, A, N, E, O, N, T, T, O, N, H, D, A and 27 edges, in which the path H → A → N → N → A → H is highlighted: the algorithm should return 6, the length of HANNAH.
>
> (a) Describe an algorithm for this problem using dynamic programming.
>
> (b) Describe an algorithm for this problem by reducing it to a standard graph problem.

Write $\ell(v)$ for the label of $v$, and count the length of a path label in letters, that is, in vertices. A single vertex is a palindrome of length 1. In a dag every walk is a path, so nothing has to be said about repeated vertices.

### (a) As a dynamic program

> [!hint]- Hint
> A palindrome is determined from the outside in: its first and last letters agree, and what lies between them is a palindrome. So a subproblem should know both ends of the path.

> [!solution]- Solution
> **The idea.** For a palindromic subsequence of one string, the subproblem is an interval, and the two ends move inward together ([[3-homework-and-exams/hw7-dynamic-programming|HW7]], Problem 1(b)). On a path of a graph the two ends are two **vertices**: the first vertex $u$ and the last vertex $v$ of the path. If the label is a palindrome, then $\ell(u) = \ell(v)$, and the path continues from $u$ along some edge $u\to x$ and arrives at $v$ along some edge $y\to v$, with a palindromic path from $x$ to $y$ in between.
>
> **Function.** For vertices $u$ and $v$, let $\textsf{LongPal}(u, v)$ be the number of vertices of the longest path **from $u$ to $v$** whose label is a palindrome, or $-\infty$ if there is no such path. The answer to the problem is the largest $\textsf{LongPal}(u, v)$ over all pairs (it is at least 1 if $G$ has a vertex).
>
> **Recurrence.**
>
> $$
> \textsf{LongPal}(u, v) = \begin{cases} -\infty & \text{if } \ell(u)\ne\ell(v),\\[2pt] 1 & \text{if } u = v,\\[2pt] \max\Bigl\{\,2 \text{ if } u\to v\in E,\ \ 2 + \max\bigl\{\textsf{LongPal}(x, y) \bigm\vert u\to x\in E,\ y\to v\in E\bigr\}\Bigr\} & \text{otherwise,}\end{cases}
> $$
>
> where a maximum over nothing is $-\infty$. In the last case the path has at least two vertices: either it is the single edge $u\to v$ (the palindrome $\ell(u)\ell(v)$), or it has an inside, which runs from an out-neighbor $x$ of $u$ to an in-neighbor $y$ of $v$ and is itself a palindromic path — possibly a single vertex, $x = y$.
>
> **Memoization.** A two-dimensional array indexed by pairs of vertices.
>
> **Evaluation order.** $\textsf{LongPal}(u, v)$ uses pairs $(x, y)$ where $x$ comes after $u$ and $y$ comes before $v$ in a topological order. So take $u$ in **reverse** topological order (outer loop) and $v$ in topological order (inner loop).
>
> **Time.** $V^2$ entries. The entry $(u, v)$ looks at $\text{outdeg}(u)\cdot\text{indeg}(v)$ pairs, and $\sum_{u, v}\text{outdeg}(u)\,\text{indeg}(v) = E^2$: in all $O(V^2 + E^2)$.
>
> **Faster, with one more table.** Split the double maximum in two. Let $\textsf{Half}(x, v) = \max\{\textsf{LongPal}(x, y) \mid y\to v\in E\}$; then the last case is $\max\{2 \text{ if } u\to v\in E,\ 2 + \max\{\textsf{Half}(x, v) \mid u\to x\in E\}\}$. Now an entry $\textsf{LongPal}(u, v)$ costs $O(\text{outdeg}(u))$ and an entry $\textsf{Half}(x, v)$ costs $O(\text{indeg}(v))$, for $O(V^2 + VE)$ time in all. With the same order as before, $\textsf{Half}(u, \cdot)$ is computed as soon as the row $\textsf{LongPal}(u, \cdot)$ is complete.
>
> **The example.** In the handout's dag, $\textsf{LongPal}$ of the two inner N's is 2 (they are joined by an edge), of the two A's on the highlighted path 4, and of the two H's 6. Its only palindromic path labels with four or more letters are ANNA and HANNAH, so the answer is 6.
>
> **Answer.** $\textsf{LongPal}(u, v)$ for all pairs of vertices, $u$ in reverse topological order and $v$ in topological order; return the largest value. $O(V^2 + E^2)$ time, or $O(VE + V^2)$ with the table $\textsf{Half}$.

### (b) As a graph reduction

> [!hint]- Hint
> The vertices of the new graph are the subproblems of (a): pairs of vertices with the same label. One step of the new graph is two steps of $G$, one at each end.

> [!solution]- Solution
> **The idea.** Build the palindrome from the outside in, and let a vertex of the new graph remember where both ends currently are. A step commits the two current ends as a matching pair of letters (worth 2) and moves the front end forward along an edge and the back end backward along an edge. The construction stops when the two ends meet in one vertex (a middle letter, worth 1) or are joined by an edge (two middle letters, worth 2).
>
> **Graph.** A directed graph $G'$ with a source $s$, a target $t$ and a vertex $(u, v)$ for every pair of vertices of $G$ with $\ell(u) = \ell(v)$. Its edges:
> - $s\to(u, v)$ of weight 0, for every such pair — the outermost letters;
> - $(u, v)\to(x, y)$ of weight 2, whenever $u\ne v$, $u\to x\in E$, $y\to v\in E$ and $\ell(x) = \ell(y)$;
> - $(u, u)\to t$ of weight 1, for every vertex $u$;
> - $(u, v)\to t$ of weight 2, whenever $u\to v\in E$.
>
> The first coordinate moves forward along an edge of the dag $G$ in every step, so $G'$ is a **dag**.
>
> **Problem.** A path $s\to(u_1, v_1)\to(u_2, v_2)\to\cdots\to(u_r, v_r)\to t$ in $G'$ describes a path of $G$: follow $u_1, u_2, \dots, u_r$, then $v_r, \dots, v_2, v_1$ — with the edge $u_r\to v_r$ in between if the last step has weight 2, and with the middle vertex $u_r = v_r$ visited once if it has weight 1. Its label is a palindrome, and the weight of the path in $G'$ is the number of its vertices. Every palindromic path of $G$ arises this way. So the answer is the **length of the longest path from $s$ to $t$** in $G'$ (0 if $G$ has no vertices).
>
> **Algorithm.** The longest-path algorithm for dags ([[2-algorithms/06-depth-first-search#dynamic-programming-in-dags|§6.4]]), in time linear in the size of $G'$.
>
> **Time.** $G'$ has at most $V^2 + 2$ vertices and at most $E^2 + 2V^2$ edges: $O(V^2 + E^2)$, the bound of the plain dynamic program — necessarily, since this *is* that dynamic program: the vertex $(u, v)$ is the subproblem $\textsf{LongPal}(u, v)$, and its outgoing edges are the terms of the recurrence.
>
> **Answer.** The longest path from $s$ to $t$ in the dag of equal-label pairs; $O(V^2 + E^2)$ time.

> [!trap] Both ends, at once
> A function of one vertex ("the longest palindrome ending at $v$") cannot work: whether a path can be extended to a longer palindrome depends on its first letter as well as its last. And the first and last letters agreeing is not enough — in the handout's dag H → A → E → T → H is a path with label HAETH. The inside must be a palindrome too, which is what the recursion checks.

> [!exam] What this lab is for
> - **Choosing the form.** A problem that says "describe an algorithm" can be answered either way. The dynamic-programming rubric wants the function in English, the recurrence, the table, the order and the time ([[0-toolkit/02-proof-templates#20-writing-up-a-dynamic-program|template §20]]); the graph-reduction rubric wants the vertices and edges, the problem solved on the graph, the algorithm called and the time in the input's parameters ([[0-toolkit/02-proof-templates#22-solving-a-problem-by-graph-reduction|template §22]]).
> - **A dynamic program over a dag** may simply say "for all vertices in topological order" or "in postorder" ([[5-lecture-log/2026-10-29|lecture of October 29]]); here Problem 2(a) needs one of each.
> - **Longest path is a standard problem only in a dag.** In general graphs it is NP-hard ([[3-homework-and-exams/lab-12a|Lab 12a]], Problem 1); both reductions above make sure the graph they build is acyclic and say why.

### Sources for this page
CS/ECE 374 A (Fall 2026), Lab 11 handout, November 4; no official solutions are in the course folder, so the solutions are ours. Checked by `tools/checks/labs_11.py`: Problem 1's table algorithm and layered dag against an exhaustive search over all subsequences (1,428 inputs), the handout's example (22 numbers, 10 of them icky, answer 5 for $k = 2$; 3, 4, 6 and 6 for $k = 0, 1, 3$ and for no budget), the small table, the sizes of the table and of the graph, and the two traps; Problem 2's recurrence in the stated order, its two-step version and the pair graph against an enumeration of all paths of 1,200 random labeled dags, with the step counts; and the handout's figure, transcribed by hand as 14 vertices and 27 edges — on that graph all three methods and the enumeration of its 433 paths return 6, and the path found is the highlighted one. Handout slips: none ("with icky numbers are indicated by stars" is a typo for "with icky numbers indicated").
