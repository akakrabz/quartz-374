---
title: "Midterm 2 cheat sheet"
description: "Everything worth copying onto the one handwritten sheet for Midterm 2, in compact form: the three rubrics as write-up skeletons, recurrences and their solutions, dynamic-programming shapes, evaluation orders and standard programs, greedy counterexamples, search and depth-first facts, which shortest-path algorithm when, the Bellman–Ford and Floyd–Warshall interfaces, graph-reduction tricks, the patterns of the Fall 2026 practice tests, and the traps that cost the most."
tags: [toolkit, algorithms, midterm-2]
aliases: ["Midterm 2 cheat sheet", "MT2 cheat sheet", "algorithms cheat sheet"]
---

*Toolkit · Midterm 2, Mon Nov 9, 7–9 pm · one double-sided letter sheet, **handwritten** — this page is the material, not the sheet: copy what you would not reproduce under pressure. The explanations behind every line are in [[0-toolkit/08-review-algorithms|the Midterm 2 review]]; the rubrics in full are in [[0-toolkit/06-how-exams-are-graded#11-recursive-algorithms|how exams are graded §11–13]]; worked exams: [[3-homework-and-exams/midterm-2-practice-1|practice 1]], [[3-homework-and-exams/midterm-2-practice-2|2]], [[3-homework-and-exams/midterm-2-practice-3|3]], [[3-homework-and-exams/midterm-2-dp-practice|DP practice]].*

> [!abstract] The exam
> **5 problems, 120 minutes**, about 20 minutes each: short answers (three recurrences; a memoization plan for a meaningless recurrence; draw a small graph or mark a search tree), a dynamic program (often after "show that the obvious greedy fails"), divide and conquer, graph reductions. **Every algorithm needs a running time.** Correct and slow beats fast and wrong. Cite standard algorithms as black boxes, never re-explain them. A greedy algorithm without a proof earns nothing. English, not code. Proofs only where it says *prove* or *justify*.

## 1. The three write-ups

| problem | points (out of 10) | the answer must contain |
|---|---|---|
| divide and conquer, backtracking | 3 what it returns · 1 base · 2 subproblems · 2 combine · 2 time | what the function returns **in terms of its parameters** (not how it works); base case; recursive calls; how their results combine; recurrence **and** its solution |
| dynamic programming | 3 function · 4 recurrence (1 base + 3 recursive) · 3 iterative (1 memo + 1 order + 1 time) | named function with explicit parameters, an English sentence saying what it returns, and the call that answers the problem; the recurrence with base cases; an **array** with index ranges; which loop is outer and which way each index runs; entries × work per entry |
| graph reduction | 3 graph · 3 problem · 2 algorithm · 2 time | vertices as explicit tuples, edges as functions of the input, "**directed**", weights; the problem (reachability, shortest path, longest path in a dag…) from which vertex to which, and how it gives the answer; the fastest correct black box; the time in the **input's** parameters |

**Without a usable DP description, the recurrence and the iterative details earn nothing.** A hash table as memo structure earns nothing. In a graph reduction, −1 for a slower algorithm than necessary, −½ for a more specific one (breadth-first where whatever-first suffices), −1 for re-explaining one.

> [!template] Dynamic program
> **Function.** For $1\le i\le n+1$ [and …], let $\textsf{Name}(i, \ldots)$ be [the largest / smallest / number of … ] for [the suffix $A[i\,..\,n]$ / the interval $A[i\,..\,j]$ / the subtree of $v$] [given …]. We need $\textsf{Name}(1, \ldots)$. \
> **Recurrence.** $\textsf{Name}(i, \ldots) = $ base cases; recursive case trying every answer to *one* question about the first choice. \
> **Memoization.** An array $\textsf{Name}[1\,..\,n+1, \ldots]$. \
> **Evaluation order.** $i$ from $n+1$ down to 1 (outer), … (inner). \
> **Time.** [entries] × [work per entry] $= O(\ldots)$.

> [!template] Graph reduction
> **The graph.** A directed graph $H$ with a vertex $(v, q)$ for every vertex $v$ and state $q$ …; an edge $(u, q)\to(v, q')$ for every edge $u\to v$ of $G$ with …; weight …. \
> **The problem.** [Reachability / shortest paths / longest path] in $H$ from $(s, q_0)$; the answer is … at $(t, \cdot)$. \
> **The algorithm.** [whatever-first search / breadth-first search / DagSSSP / Dijkstra / Bellman–Ford] from $(s, q_0)$. \
> **The time.** $H$ has [$\ldots V$] vertices and [$\ldots E$] edges, so $O(\ldots)$.

## 2. Recurrences

**Level ratio.** For $T(n) = a\,T(n/b) + f(n)$, consecutive levels of the recursion tree sum to values in the ratio $r = a\,f(n/b)/f(n)$; for $f(n) = n^d$, $r = a/b^d$.

| $r$ | dominated by | $T(n)$ |
|---|---|---|
| $< 1$ | the root | $\Theta(f(n))$ |
| $= 1$ | every level equally | $\Theta(f(n)\log n)$ |
| $> 1$ | the leaves | $\Theta(n^{\log_b a})$ |

**Unequal pieces** $T(n) = \sum_i T(\alpha_i n) + n^d$: compare $\sum_i\alpha_i^{\,d}$ with 1 (for $d = 1$, the sum of the fractions). **Subtractive** recurrences: unroll. **A log factor** in $f$ (the ratio drifts towards 1): sum the levels directly. Floors, ceilings and $\pm$ constants inside $T(\cdot)$ never matter.

| recurrence | solution | | recurrence | solution |
|---|---|---|---|---|
| $T(n/2) + 1$ | $\log n$ | | $T(n-1) + 1$ | $n$ |
| $T(n/2) + n$ | $n$ | | $T(n-1) + n$ | $n^2$ |
| $2T(n/2) + 1$ | $n$ | | $2T(n-1) + 1$ | $2^n$ |
| $2T(n/2) + n$ | $n\log n$ | | $T(n/5) + T(7n/10) + n$ | $n$ |
| $2T(n/2) + n^2$ | $n^2$ | | $T(n/2) + T(n/3) + n$ | $n$ |
| $3T(n/2) + n$ | $n^{\lg 3}\approx n^{1.585}$ | | $T(n/3) + T(2n/3) + n$ | $n\log n$ |
| $4T(n/2) + n$ | $n^2$ | | $T(n/2) + T(n/3) + T(n/6) + n$ | $n\log n$ |
| $3T(n/2) + n^2$ | $n^2$ | | $T(5n/11) + \sqrt n$ | $\sqrt n$ |
| $4T(n/2) + n^2$ | $n^2\log n$ | | $4T(n/16) + \sqrt n$ | $\sqrt n\log n$ |
| $7T(n/2) + n^2$ | $n^{\lg 7}\approx n^{2.807}$ | | $T(n/2) + \lg n$ | $\log^2 n$ |
| $8T(n/2) + n^2$ | $n^3$ | | $T(\sqrt n) + 1$ | $\log\log n$ |

All solutions are $\Theta(\cdot)$. Useful facts: $a^{\log_b n} = n^{\log_b a}$; $\lg 3\approx 1.585$, $\lg 5\approx 2.32$, $\lg 7\approx 2.807$; $\sum_{i\le j}(j - i + 1)^2 = \Theta(n^4)$ (all intervals, quadratic work each).

## 3. Dynamic programming

**Recipe.** (1) One question about an optimal solution: is $A[i]$ used? where does the first piece end? which end is taken? which edge leaves $v$? (2) The function: explicit parameters (an index into the input plus whatever the rest of the computation needs) and an English sentence. (3) The recurrence: try every answer. (4) Array, order, time. Test on an input of size 2 or 3.

| shape | memo | evaluation order | seen in |
|---|---|---|---|
| suffix $i$ | $[1\,..\,n+1]$ | $i$ decreasing | quadhopper, words with skips, dance, districts |
| suffix + value or counter $(i, t)$ | $[1\,..\,n+1, 0\,..\,T]$ | $i$ decreasing (outer) | subset sum, $k$ jumps |
| suffix + count of pieces $(i, m)$ | $[1\,..\,n, 1\,..\,k]$ | $m$ increasing (outer) | $k$ intervals of smallest max sum |
| start + exact length $(i, \ell)$ | $[1\,..\,n, 1\,..\,n]$ | $\ell$ increasing (outer) | mostly odd increasing subsequence |
| two prefixes $(i, j)$ | $[0\,..\,m, 0\,..\,n]$ | $i$ increasing (outer), $j$ increasing | edit distance, LCS |
| interval $(i, j)$ | $[1\,..\,n+1, 0\,..\,n]$, $j\ge i-1$ | $i$ decreasing (outer), $j$ increasing | square-depth, card game, optimal BST |
| subtree $v$ | a field per node | postorder | independent set in a tree |
| dag vertex $v$ | a field per vertex | reverse topological (postorder) for edges out of $v$; topological for edges into $v$ | longest path, earliest term |

**A memoization plan for a given recurrence.** (1) Index ranges: from the call and the base cases; store only values that occur (if $s$ only doubles from 1, index by $e$ with $s = 2^e$, $0\le e\le\lfloor\lg n\rfloor$). (2) For each reference, which index moves which way. (3) Outer loop: an index that **every** reference either keeps or moves the same way, run so that referenced entries come first (references to larger $i$: $i$ decreasing); inner loop: whatever the references that keep the outer index need ("any order" if every reference strictly moves the outer index). (4) Time: entries × work per entry, where a $\max$ or $\sum$ over $j$ costs $O(n)$.

| standard DP | function | time |
|---|---|---|
| text segmentation | $\textsf{Splittable}(i)$: $A[i\,..\,n]$ splits into words | $O(n^2)$ calls of $\textsf{IsWord}$ |
| longest increasing subsequence | $\textsf{LISfirst}(i)$: longest in $A[i\,..\,n]$ starting with $A[i]$ | $O(n^2)$ |
| edit distance | $\textsf{Edit}(i, j)$ of $A[1\,..\,i]$, $B[1\,..\,j]$ | $O(mn)$ |
| subset sum | $\textsf{SS}(i, t)$: a subset of $X[i\,..\,n]$ sums to $t$ | $O(nT)$, pseudo-polynomial |
| optimal BST | $\textsf{OptCost}(i, k)$: keys $i$ to $k$ | $O(n^3)$: $n^2$ entries, $O(n)$ each |
| independent set in a tree | $\textsf{MISyes}(v)$, $\textsf{MISno}(v)$ | $O(n)$ |
| longest path in a dag | $\textsf{LLP}(v) = \max_{v\to w}\{\ell(v\to w) + \textsf{LLP}(w)\}$ | $O(V + E)$ |

**Tricks from the practice handouts.** A *skip* option when not every element must be used ($\textsf{MaxWords}(i)$ either skips $T[i]$ or starts a word there). A *jump* when a choice blocks what follows ($\textsf{MaxScore}(k + \mathit{Wait}[k] + 1)$). A *count* parameter when the number of pieces is fixed. **Fix the length** when the condition is on the whole sequence ("mostly odd": maximize odd minus even for each length). A **forced opponent** is not a parameter: build their move into the recurrence ($\textsf{Best}(\textsf{Elmo}(i+1, j))$). $-\infty$ / $\infty$ for "impossible", and $\max\varnothing$ stated.

> [!recipe] "Show that the obvious greedy strategy fails"
> State the rule; give one small concrete input; give greedy's value and a better value. No optimality proof needed. Try sizes 2–3 first; look for a locally best choice that blocks two good later ones. Stock examples: coins $\{1, 3, 4\}$ paying 6 (greedy $4+1+1$, best $3+3$); quadhopper $(1,2,2,2), (4,4,4,4), (1,1,1,1), (1,1,1,1)$ (greedy 2 moves, best 3); cards $4, 3, 7, 1, 2$ against greedy Elmo (greedy you 5 to 12, best 9 to 8); dancing with $\mathit{Score} = [3, 2, 2]$, $\mathit{Wait} = [2, 0, 0]$ (greedy 3, best 4).

## 4. Divide and conquer

- **Binary search on an invariant.** Find a test $\textsf{good}(m)$ that is true up to the answer and false after it; keep $\textsf{good}(lo)$, $\lnot\textsf{good}(hi)$; $T(n) = T(n/2) + O(1) = O(\log n)$. Example: the one even adjacent pair — $A[1\,..\,m]$ alternates iff $A[m] - A[1] - (m-1)$ is even.
- **Split, recurse on both halves, combine in linear time:** $2T(n/2) + O(n) = O(n\log n)$ — mergesort, counting inversions, closest pair (split at the median $x$; a black box finds the best pair across the line).
- **Merge $k$ sorted arrays of length $n$:** pair them up recursively, $T(k) = 2T(k/2) + O(nk) = O(nk\log k)$; merging one at a time is $\Theta(nk^2)$.
- **Generalize** when the recursion needs it (the $k$-th smallest, not the median) and describe the general problem. Black boxes: mergesort $O(n\log n)$, selection $O(n)$, binary search $O(\log n)$, merge $O(n)$, Karatsuba $O(n^{\lg 3})$.

## 5. Graphs

| search (bag) | time | gives |
|---|---|---|
| whatever-first | $O(V+E)$ | $\textsf{reach}(s)$, a spanning tree of it; in a loop, the components |
| depth-first (stack / recursion) | $O(V+E)$ | pre/post times, cycles, topological order, strong components |
| breadth-first (queue) | $O(V+E)$ | fewest-edge distances, a breadth-first tree |
| best-first (priority queue) | $O(E\log V)$ | Dijkstra: shortest paths with weights $\ge 0$ |

**Depth-first search.** Edge $u\to v$: tree/forward if $u.\mathit{pre} < v.\mathit{pre} < v.\mathit{post} < u.\mathit{post}$; back if $v.\mathit{pre} < u.\mathit{pre} < u.\mathit{post} < v.\mathit{post}$; cross if $v.\mathit{post} < u.\mathit{pre}$. Cycle $\iff$ back edge. **Decreasing $\mathit{post}$ = topological order** (preorder is not one). Postorder = DP order for edges out of $v$. Strong components (Kosaraju–Sharir): DFSAll on $\textsf{rev}(G)$, then search $G$ from unmarked vertices in decreasing $\mathit{post}$; the condensation is a dag. **A dag has exactly one topological order iff consecutive vertices of the order are joined by edges** (a path through all vertices).

**Marking trees on a given graph.** A search tree contains only vertices its root reaches (check in-degrees: a source is reached from nowhere). Breadth-first tree edges go from level $d$ to level $d+1$; ties are legitimate alternatives. A shortest-path tree with negative edges in a dag: relax in topological order. Follow the stated tie-breaking (usually alphabetical).

| the graph you built | algorithm | time |
|---|---|---|
| unweighted | breadth-first search | $O(V+E)$ |
| a dag, any weights | DagSSSP: relax edges in topological order | $O(V+E)$ |
| weights $\ge 0$ | Dijkstra | $O(E\log V)$ |
| negative edges, no negative cycle | Bellman–Ford | $O(VE)$ |
| all pairs, any weights | Floyd–Warshall | $O(V^3)$ |
| longest path | only in a dag: negate, DagSSSP (or $\textsf{LLP}$) | $O(V+E)$ |

**Bellman–Ford.** $\mathit{dist}_{\le i}(v) = \min\big\{\mathit{dist}_{\le i-1}(v),\ \min_{u\to v}\{\mathit{dist}_{\le i-1}(u) + w(u\to v)\}\big\}$, $\mathit{dist}_{\le 0}(s) = 0$, else $\infty$; $i$ outer, $1\le i\le V-1$; a negative cycle is reachable from $s$ iff round $V$ still improves something. **Floyd–Warshall.** $\textsf{dist}(u, v, r) = \min\{\textsf{dist}(u, v, r-1),\ \textsf{dist}(u, r, r-1) + \textsf{dist}(r, v, r-1)\}$, $\textsf{dist}(u, v, 0) = w(u\to v)$; **$r$ outer**; negative cycle iff some $\mathit{dist}[v, v] < 0$. Dijkstra that never re-extracts a vertex is wrong with negative edges; never add a constant to all weights.

## 6. Graph-reduction tricks

| the question says… | the new graph | example |
|---|---|---|
| the next move depends on the last one (color, direction, parity, turn) | vertices $(v, q)$; edges update $q$ | rainbow walks: $(v, c)$, $3V+1$ vertices; zigzag walks: $(v, \mathrm{F})\to(w, \mathrm{B})$ for $v\to w$ and $(w, \mathrm{B})\to(v, \mathrm{F})$ |
| at most $k$ of something | layers $(v, c)$, $0\le c\le k$ | $k$ jumps, $k$ negative edges: $O(k(V+E))$ |
| from the closest vertex of a set | super-source $s'$ with edges to the whole set; subtract the extra edge | remoteness: one BFS per color, $\mathit{dist}(s_c, v) - 1$ |
| to a target, from everywhere | reverse the graph | distances to $t$ |
| through some vertex $v$ | run from $s$ and from $t$; combine $d_s(v) + d_t(v)$ | highest point of a walk of length $\le L$: $\max\{h(v) \mid d_s(v) + d_t(v)\le L\}$ |
| costs on vertices | split $v$ into $v_{\mathrm{in}}\to v_{\mathrm{out}}$ | vertex weights |
| two tokens | vertices are pairs of positions | $O(V^2)$ vertices |
| every move increases something | the graph is a dag: DP or longest path | quadhopper (squares), prerequisites: $\textsf{Term}(v) = 1 + \max_{u\to v}\textsf{Term}(u)$ |
| cycles but a dag algorithm is needed | contract strong components | condensation |

Cost of a trick: $s$ states per vertex gives $sV$ vertices and about $sE$ edges. State graphs are **directed**, even for an undirected input.

## 7. Traps

1. A DP function without parameters or an English description ("$\textsf{OPT}(i)$", "the best so far"): the next 7 points are gone too.
2. A hash table as memo; no evaluation order; an order that reads entries before they are written.
3. Time = number of entries (forgetting the work per entry, or the cost of a black box such as $O(\lvert w\rvert)$ for $\textsf{IsWord}$ or $O(k^2)$ for $\textsf{IsSquare}$).
4. Greedy without proof; "obviously optimal".
5. Describing *how* instead of *what* a recursive function returns.
6. $\log_b a$ upside down; forgetting the $\log n$ factor when $r = 1$; a recurrence without its solution.
7. Modifying the algorithm (a "smart DFS that remembers the color") instead of the graph.
8. Dijkstra on an unweighted graph or a dag (−1); BFS on a weighted graph (wrong); Dijkstra with negative edges (wrong).
9. Time in $V$ and $E$ of the built graph instead of the input's parameters.
10. "Try all paths with DFS": exponential.
11. Forgetting "directed" (−½).
12. Longest path in a graph that is not a dag (NP-hard); preorder as a topological order.

## 8. The practice tests at a glance

| problem | pattern | time | page |
|---|---|---|---|
| quadhopper | suffix DP; greedy fails | $O(n)$ | [[3-homework-and-exams/midterm-2-practice-1#problem-2--quadhopper\|P1.2]] |
| highest walk of length $\le L$ | Dijkstra from $s$ and $t$, $d_s(v) + d_t(v)\le L$ | $O(E\log V)$ | [[3-homework-and-exams/midterm-2-practice-1#problem-3--the-highest-point-of-a-short-walk\|P1.3]] |
| verbal subsequence | suffix DP with a skip option | $O(n^3)$ | [[3-homework-and-exams/midterm-2-practice-1#problem-4--the-longest-verbal-subsequence\|P1.4]] |
| closest pair | split at median $x$, black box across the line | $O(n\log n)$ | [[3-homework-and-exams/midterm-2-practice-1#problem-5--the-closest-pair-of-points\|P1.5]] |
| rainbow walks | state = last color | $O(V+E)$ | [[3-homework-and-exams/midterm-2-practice-2#problem-2--rainbow-walks\|P2.2]] |
| square-depth | interval DP | $O(n^4)$ | [[3-homework-and-exams/midterm-2-practice-2#problem-3--square-depth\|P2.3]] |
| merge $k$ sorted arrays | pairwise merging | $O(nk\log k)$ | [[3-homework-and-exams/midterm-2-practice-2#problem-4--merging-k-sorted-arrays\|P2.4]] |
| fewest terms | longest path ending at $v$ in a dag; then count | $O(V+E)$ | [[3-homework-and-exams/midterm-2-practice-2#problem-5--speed-running-a-degree\|P2.5]] |
| cards against greedy Elmo | interval DP with a forced reply | $O(n^2)$ | [[3-homework-and-exams/midterm-2-practice-3#problem-2--beating-elmo-at-cards\|P3.2]] |
| minimum remoteness | super-source per color, 3 BFS | $O(V+E)$ | [[3-homework-and-exams/midterm-2-practice-3#problem-3--the-least-remote-vertex\|P3.3]] |
| the one even pair | binary search on a parity invariant | $O(\log n)$ | [[3-homework-and-exams/midterm-2-practice-3#problem-4--the-one-even-pair\|P3.4]] |
| zigzag walks | two copies, F and B; Dijkstra | $O(E\log V)$ | [[3-homework-and-exams/midterm-2-practice-3#problem-5--shortest-zigzag-walks\|P3.5]] |
| dance contest | suffix DP with a jump | $O(n)$ | [[3-homework-and-exams/midterm-2-dp-practice#problem-1--the-dance-contest\|DP.1]] |
| districts of size $k$ to $2k$ | suffix DP over the first district's length; prefix sums | $O(nk)$ | [[3-homework-and-exams/midterm-2-dp-practice#problem-2--voting-districts\|DP.2]] |
| $k$ intervals, smallest max sum | suffix + count of intervals | $O(n^2k)$ | [[3-homework-and-exams/midterm-2-dp-practice#problem-3--the-most-even-partition-into-k-intervals\|DP.3]] |
| mostly odd increasing subsequence | fix the length, maximize odd − even | $O(n^3)$ | [[3-homework-and-exams/midterm-2-dp-practice#problem-4--the-longest-mostly-odd-increasing-subsequence\|DP.4]] |

Related: [[0-toolkit/08-review-algorithms|Midterm 2 review]] · [[0-toolkit/06-how-exams-are-graded|how exams are graded]] · [[0-toolkit/02-proof-templates|proof templates]] · [[3-homework-and-exams/index|homework and exams]]

### Sources for this page
A condensation of [[0-toolkit/08-review-algorithms|the Midterm 2 review]] and [[0-toolkit/06-how-exams-are-graded|how exams are graded]] (themselves based on Erickson's *Algorithms* and the CS/ECE 374 A, Fall 2026, course website), plus the patterns of the Fall 2026 Midterm 2 practice handouts as solved on the four practice pages. Checked by `tools/checks/exams_mt2.py` (cheat-sheet section): every recurrence in the table of §2 numerically (the ratio to the stated solution settles for growing $n$; $2T(n-1) + 1$ exactly), and every greedy counterexample of §3 by brute force; the other facts are checked on the pages they come from.
