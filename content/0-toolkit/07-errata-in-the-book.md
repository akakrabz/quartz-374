---
title: "Errata in the books"
description: "Slips in Erickson's two textbooks found while writing this site — in Models of Computation a wrong move in a printed Turing machine, a too-weak CNF rule and an off-by-one in the Cook–Levin tableau; in Algorithms wrong summation limits, a wrong growth rate, array ranges and loop bounds that do not fit their tables, a broken non-recursive Hanoi rule, wrong counts in exercise examples, a Huffman loop off by one, an unstable “stable” matching, and graph-search pseudocode that recurses forever or labels nothing — each with the correction and the section here that has it right."
tags: [toolkit, regular, context-free, turing-machines, undecidability, complexity, algorithms]
aliases: ["errata", "book errata", "typos in the book"]
---

The book is careful, and every item below is small. They are listed because each one can cost points if it is copied onto a cheat sheet or used to check an answer. Every item was confirmed against the book — the *Models of Computation* chapter PDFs (cover date December 28, 2018) and the first edition of *Algorithms* (June 2019), whose page numbers are given — and every concrete one is also checked by the site's scripts. Only items that would change an answer are listed — no spelling.

> [!tip] How to read this page
> "As printed" is what the PDF says; "should be" is what this site uses. The last column links the section here that has the corrected version and explains it. If the book is updated, some items may disappear: the [chapter PDFs](https://jeffe.cs.illinois.edu/teaching/algorithms/#models) are the reference.

## Chapter 4 · Nondeterministic automata

| where | as printed | should be | why it matters |
|---|---|---|---|
| §4.7, Thompson's NFA for $(\mathtt{0}+\mathtt{1})^*(\mathtt{00}+\mathtt{11})(\mathtt{0}+\mathtt{1})^*$ | the text calls it an "18-state" NFA | the figure and the subset-construction table use the literal 26-state construction (states $a$ to $z$); 18 is the count if each $\mathtt{0}+\mathtt{1}$ is drawn as one two-state gadget | Thompson's algorithm makes 2 states per symbol, union and star — [[1-models-of-computation/04-nondeterministic-automata#47-another-example\|§4.7]] |

## Chapter 5 · Context-free languages

| where | as printed | should be | why it matters |
|---|---|---|---|
| §5.9, CNF conversion step 0 | the new start symbol $S'\to S$ is needed only when $S\rightsquigarrow^*\varepsilon$, and is dropped again otherwise | also needed whenever $S$ appears on a right side | for $S\to\mathtt{0}S\mid\mathtt{1}$, dropping $S'$ leaves the start symbol on a right side, which CNF forbids — [[1-models-of-computation/05-context-free-languages#59-the-cnf-conversion-algorithm\|§5.9]] |

## Chapter 6 · Turing machines

| where | as printed | should be | why it matters |
|---|---|---|---|
| §6.3, transition table of the $\mathtt{0}^n\mathtt{1}^n\mathtt{0}^n$ machine | after marking a 0, state *seek0* moves right ($+1$) | moves left ($-1$), as the text and its traces do | with $+1$ the machine rejects `010`, which is in the language — [[1-models-of-computation/06-turing-machines#63-a-first-example\|§6.3]] |
| §6.3, the same machine | presented as a machine for $\{\mathtt{0}^n\mathtt{1}^n\mathtt{0}^n\}$ | even with the left move, it accepts strings outside the language — `001010` and 17 others of length at most 12 — because it never checks that the input has the form $\mathtt{0}^*\mathtt{1}^*\mathtt{0}^*$; and it rejects $\varepsilon$, which is in the language | a decider needs a format check first; the site's 12-state machine has one — [[1-models-of-computation/06-turing-machines#63-a-first-example\|§6.3]] |
| §6.8, encoding example | lists $\langle\textit{start}\rangle = \mathtt{111}$, but writes *start* as `001` inside the encoded transitions | `111` everywhere (the start state is coded by all 1s) | reading or writing $\langle M\rangle$ — [[1-models-of-computation/06-turing-machines#68-universal-turing-machines\|§6.8]] |
| §6.8, the universal machine | fixes codes for *start* (all 1s) and *reject* (all 0s) only | $U$ must also recognize *accept*; this site uses $\langle\textit{accept}\rangle = \mathtt{0}\cdots\mathtt{01}$ | a gap rather than an error — [[1-models-of-computation/06-turing-machines#68-universal-turing-machines\|§6.8]] |

## Chapter 7 · Undecidability

| where | as printed | should be | why it matters |
|---|---|---|---|
| §7.12, the Rice–McNaughton–Myhill–Shapiro theorem | $\mathcal{L}$ is monotone if every superset of a language in $\mathcal{L}$ is in $\mathcal{L}$ | every **acceptable** superset | $\mathcal{L}$ contains only acceptable languages, so read literally no non-empty $\mathcal{L}$ would be monotone; Lemma 17's proof uses the acceptable version — [[1-models-of-computation/07-undecidability#712-the-ricemcnaughtonmyhillshapiro-theorem\|§7.12]] |

## Chapter 8 · Universal models

| where | as printed | should be | why it matters |
|---|---|---|---|
| §8.5, Post's correspondence problem | both rows of the solution $c, b, c, a$ spell `110110100` | `110011100` | checking a PCP solution by hand — [[1-models-of-computation/08-universal-models#85-posts-correspondence-problem\|§8.5]] |

## Chapter 9 · Nondeterministic Turing machines

| where | as printed | should be | why it matters |
|---|---|---|---|
| §9.5, nondeterminism as advice | $N$ rejects $w$ if and only if $M$ rejects $(w, x)$ for **every** advice string $x$ | $N$ rejects $w$ if and only if, for some length $t$, $M$ rejects $(w, x)$ within $t$ steps for every advice string $x$ of length $t$ | the printed version fails when the computation tree has an infinite branch, whatever $M$ does when the advice runs out — [[1-models-of-computation/09-nondeterministic-turing-machines#95-nondeterminism-as-advice\|§9.5]] |
| §9.6, the Cook–Levin tableau | cells $0, \dots, N+1$ | cells $0, \dots, N+2$: the head starts on cell 1 and can reach cell $N+1$ at time $N$, and cells $0$ and $N+2$ are empty sentinels | with the printed range, a run whose head ends on cell $N+1$ is not represented — [[1-models-of-computation/09-nondeterministic-turing-machines#96-the-cooklevin-theorem\|§9.6]] |
| §9.6, the transition constraints | a few right-hand sides refer to time $t$ (for example $T_{t,i-1,a}$), and the left boundary is written with cell $i$ | every variable on the right of a transition constraint refers to time $t-1$; the left boundary is cell $0$ | a constraint at time $t$ must be determined by the configuration at time $t-1$ — [[1-models-of-computation/09-nondeterministic-turing-machines#96-the-cooklevin-theorem\|§9.6]] |

## Algorithms, Chapter 1 · Recursion

*Erickson, Algorithms, 1st edition (June 2019).*

| where | as printed | should be | why it matters |
|---|---|---|---|
| p. 28, proof of Lemma 1.1 (Merge) | "for all $k$ from 0 to $n$, the last $n-k-1$ iterations …" | $k$ from 1 to $n+1$, the last $n-k+1$ iterations — $B[k..n]$ has $n-k+1$ entries | an off-by-one in a loop-invariant proof — [[2-algorithms/01-recursion#14-mergesort\|§1.4]] |
| p. 29, Figure 1.7 | the partitioned row `AGOEINLMPTXSR` | the book's own Partition (Figure 1.8) produces `OINGEAMLPRTSX`, with the pivot at index 9 | the printed row is a valid partition, but not the one the algorithm produces — tracing by hand will disagree — [[2-algorithms/01-recursion#15-quicksort\|§1.5]] |
| p. 37, MomSelect | `Partition(A[1 .. n], mom)` passes the median's value | Partition takes an index: pass $p$ with $A[p] = \textit{mom}$ | — [[2-algorithms/01-recursion#18-linear-time-selection\|§1.8]] |
| pp. 37–38, the analysis of MomSelect | the $7n/10$ bound, stated without conditions | it assumes distinct elements (with repeated values, use a three-way partition); the brute-force threshold must be at least 5 | with the book's two-way Partition, an all-equal array is not linear — [[2-algorithms/01-recursion#18-linear-time-selection\|§1.8]] |
| p. 43 | SlowPower "requires $n$ multiplications" | $n-1$ (the loop runs for $i = 2, \dots, n$; p. 42 says $n-1$) | — [[2-algorithms/01-recursion#110-exponentiation\|§1.10]] |
| Ex. 1.1(b), p. 44 | "the only legal move that involves a different disk from the previous move" | ambiguous: after a move of a larger disk, disk 1 has two legal moves; add "disk 1 never returns to the peg it just left" | — [[2-algorithms/01-recursion-exercises#exercise-11--tower-of-hanoi-without-recursion\|Ex. 1.1]] |
| Ex. 1.1(d), p. 45, RulerHanoi | "if $n - i$ is even, move disk $\rho(i)$ forward" | forward if $n - \rho(i)$ is odd, backward if it is even; as printed it is wrong for every $n$ (for $n = 1$ it moves disk 1 to peg 1) | — [[2-algorithms/01-recursion-exercises#exercise-11--tower-of-hanoi-without-recursion\|Ex. 1.1]] |
| Ex. 1.5(a), p. 48 | "This is exactly the same as problem 4(a)" | not the same: 4(a) starts on the middle peg, $(3^n-1)/2$ moves; 5(a) goes end to end, $3^n - 1$ moves | — [[2-algorithms/01-recursion-exercises\|exercises]] |
| Ex. 1.10(a), p. 50 | "smaller than the pivot" twice | the second should be "larger" | — |

## Algorithms, Chapter 2 · Backtracking

| where | as printed | should be | why it matters |
|---|---|---|---|
| p. 79, Figure 2.6 (ConstructSubset) | `if T < 0 or n = 0` | `i = 0` — as printed the recursion indexes $X[0], X[-1], \dots$ | — [[2-algorithms/02-backtracking#23-subset-sum\|§2.3]] |
| p. 92, the OptCost recurrence | summand $\sum_{j=i}^{k} f[i]$ | $\sum_{j=i}^{k} f[j]$ | the cost of a subtree is the total frequency of *its* keys — [[2-algorithms/02-backtracking#28-optimal-binary-search-trees\|§2.8]] |
| p. 93, the number of binary search trees | $N(n) = \sum_{r=1}^{n-1} N(r-1)\,N(n-r)$ | the sum runs to $r = n$ (as printed, $N(1) = 0$) | — [[2-algorithms/02-backtracking#28-optimal-binary-search-trees\|§2.8]] |
| p. 93, the same passage | $N(n) = \Theta(4^n/\sqrt n)$ | $N(n) = \binom{2n}{n}/(n+1) = \Theta(4^n/n^{3/2})$; $4^n/\sqrt n$ is the growth of $\binom{2n}{n}$ | — [[2-algorithms/02-backtracking#28-optimal-binary-search-trees\|§2.8]] |
| p. 73 | the root of the n-queens recursion tree has "$r = 0$" | the empty-board call is $\textsf{PlaceQueens}(Q, 1)$ | — [[2-algorithms/02-backtracking#21-n-queens\|§2.1]] |

## Algorithms, Chapter 3 · Dynamic programming

| where | as printed | should be | why it matters |
|---|---|---|---|
| p. 99, memoization of Fibonacci | "$F_{k-1}$ recursive calls to RecFibo$(n-k)$" | $F_{k+1}$ — the same sentence lists 1, 2, 3, 5 calls for $k = 1, 2, 3, 4$ | — [[2-algorithms/03-dynamic-programming#31-matravrtta-fibonacci-numbers\|§3.1]] |
| p. 105, text segmentation | "only $n$ different ways to call Splittable$(i)$ — one for each value of $i$ between 1 and $n+1$" | $n+1$ ways | counting subproblems — [[2-algorithms/03-dynamic-programming#33-interpunctio-verborum-redux\|§3.3]] |
| p. 109, FastLIS | the array $\mathit{LISbigger}$ has columns $1\,..\,n$ | columns $1\,..\,n+1$: the base cases are stored in column $n+1$ | a memo structure must hold every entry the loops write — [[2-algorithms/03-dynamic-programming#36-longest-increasing-subsequence\|§3.6]] |
| p. 110, FastLIS2 | the array $\mathit{LISfirst}[1\,..\,n]$ | $\mathit{LISfirst}[0\,..\,n]$: the answer is read from entry 0 | the same — [[2-algorithms/03-dynamic-programming#36-longest-increasing-subsequence\|§3.6]] |
| p. 117, FastSubsetSum | first inner loop `for t ← 1 to X[i] − 1` | `for t ← 1 to min{X[i] − 1, T}` | when $X[i] > T+1$ the printed loop writes $S[i, T+1]$, outside the table $S[1\,..\,n+1, 0\,..\,T]$ — [[2-algorithms/03-dynamic-programming#38-subset-sum\|§3.8]] |
| p. 120, OptimalBST3 | outer loop `for j ← 0 to n + 1` | `for j ← 0 to n` | the last iteration would write $\mathit{OptCost}[n+2, n+1]$, outside the table — [[2-algorithms/03-dynamic-programming#39-optimal-binary-search-trees\|§3.9]] |
| Ex. 3.6(b), p. 127 | a string of 19 X's is a smooth shuffle of 7 X's and 11 X's | 8 X's and 11 X's, as the book's colored picture shows ($7 + 11 \ne 19$) | — [[2-algorithms/03-dynamic-programming-exercises#exercise-36--shuffles\|Ex. 3.6]] |
| Ex. 3.7(d), p. 127 | an occurrence has $X[I[j]] = Y[j]$, with cost $\sum_j C[j]$ | $Y[I[j]] = X[j]$, with cost $\sum_j C[I[j]]$: the indices $I[j]$ are positions in $Y$ | as printed, the indices would point into $X$, which has only $k$ entries — [[2-algorithms/03-dynamic-programming-exercises#exercise-37--subsequences-of-a-longer-string\|Ex. 3.7]] |
| Ex. 3.7(f), p. 127 | the running time "of your algorithm for part (d)" | almost certainly part (e): (f) drops the $O(1)$-addition assumption that (e) makes | the page answers both — [[2-algorithms/03-dynamic-programming-exercises#exercise-37--subsequences-of-a-longer-string\|Ex. 3.7]] |
| Ex. 3.9(e), p. 128 | `BUBBASEESABANANA` has 5 palindrome decompositions shown "and 65 others" (70) | 97, by the recurrence and by trying all $2^{15}$ ways to cut | — [[2-algorithms/03-dynamic-programming-exercises#exercise-39--palindromes\|Ex. 3.9]] |
| Ex. 3.10, pp. 129–130 | the example array's longest increasing back-and-forth subsequence has length 9 | 7 under the rule as stated; the printed sequence moves the opposite way (right from odd squares) and is not increasing ($A[18] = 9$ comes before $4$); with the directions swapped the answer would be 10 | also, the problem says positive integers but the array contains a 0 — [[2-algorithms/03-dynamic-programming-exercises#exercise-310--increasing-back-and-forth-subsequences\|Ex. 3.10]] |

## Algorithms, Chapter 4 · Greedy algorithms

| where | as printed | should be | why it matters |
|---|---|---|---|
| p. 161, proof of Lemma 4.2 | $F[\pi(i+i)]$ | $F[\pi(i+1)]$ | — [[2-algorithms/04-greedy-algorithms#41-storing-files-on-tape\|§4.1]] |
| p. 162 | "$X \in \{1, 2, \dots, n\}$" | $X \subseteq \{1, 2, \dots, n\}$, and "for any pair $i \ne j$ in $X$" | — [[2-algorithms/04-greedy-algorithms#42-scheduling-classes\|§4.2]] |
| p. 170, Figure 4.4 (BuildHuffman) | "for $i \leftarrow n$ to $2n-1$" | for $i \leftarrow n+1$ to $2n-1$ | as printed, leaf $n$ is overwritten and the last ExtractMin runs on an empty queue; the book's own count of $2n-1$ Inserts and $2n-2$ ExtractMins fits $n+1$ — [[2-algorithms/04-greedy-algorithms#44-huffman-codes\|§4.4]] |
| p. 174, stable matching example | "the matching $\{Ar, Bs, Cq, Dt\}$ is also stable" | it is **unstable** ($q$ and $B$ prefer each other); $\{As, Bt, Cq, Dr\}$ is the only stable matching for those lists | checking stability by hand against the book gives the wrong answer — [[2-algorithms/04-greedy-algorithms#45-stable-matching\|§4.5]] |
| p. 174 | "the Boston Pool algorithm can execute each offer in constant time" | almost certainly Gale–Shapley: the paragraph analyzes it, and Exercise 4.9 cites it that way | — [[2-algorithms/04-greedy-algorithms#45-stable-matching\|§4.5]] |

## Algorithms, Chapter 5 · Basic graph algorithms

| where | as printed | should be | why it matters |
|---|---|---|---|
| p. 191, the number of edges | a directed graph has $0 \le E \le V(V-1)$ edges | true without loops; the book's definition allows loops (p. 197 uses them), and then $E \le V^2$ | an imprecision rather than an error — [[2-algorithms/05-basic-graph-algorithms#52-basic-definitions\|§5.2]] |
| p. 193, dependency graphs | the edit-distance dependency graph is an $m\times n$ grid | an $(m+1)\times(n+1)$ grid: the table includes row 0 and column 0 | — [[2-algorithms/05-basic-graph-algorithms#53-representations-and-examples\|§5.3]] |
| p. 200, proof of Lemma 5.1 | the prefix of the path ending at $u$ "is shorter than the shortest path from $s$ to $u$" | the prefix **is** a shortest path to $u$ (and shorter than the shortest path to $v$) | as printed the sentence contradicts itself — [[2-algorithms/05-basic-graph-algorithms#55-whatever-first-search\|§5.5]] |
| p. 201, the same proof | "adding one more parent edge $s\to\textit{parent}(s)$" | $v\to\textit{parent}(v)$ | — [[2-algorithms/05-basic-graph-algorithms#55-whatever-first-search\|§5.5]] |
| p. 202, best-first search | the priority queue holds "at most one copy of each edge" | in an undirected graph an edge can be there once in each direction; the $O(\log E)$ time per operation is unaffected | — [[2-algorithms/05-basic-graph-algorithms#56-important-variants\|§5.6]] |
| p. 204, LabelOne | starts with "while the bag is not empty" | first put $v$ into the bag; as printed nothing is labeled and CountAndLabel returns $V$ | copying the pseudocode gives a broken component counter — [[2-algorithms/05-basic-graph-algorithms#56-important-variants\|§5.6]] |
| p. 204, WFSAll | "puts every edge into the bag once" | each undirected edge twice, plus one start item per component; the $O(V+E)$ bound is unaffected | — [[2-algorithms/05-basic-graph-algorithms#56-important-variants\|§5.6]] |
| p. 205 | "$\textit{parent}(v)\to p$" | $\textit{parent}(v)\to v$ | — [[2-algorithms/05-basic-graph-algorithms#56-important-variants\|§5.6]] |
| p. 205, directed graphs | best-first search by edge weight gives a "minimum-weight directed spanning tree" | false: with $s\to a$ (2), $s\to b$ (3), $b\to a$ (1), best-first search keeps weight 5 but the optimum is 4; this needs a different algorithm (Chu–Liu/Edmonds) | do not use it as a black box for directed spanning trees — [[2-algorithms/05-basic-graph-algorithms#56-important-variants\|§5.6]] |
| p. 215, Figure 5.17 (Three Seashells) | "the first two turns of a solution" | as drawn the puzzle has **no** solution: the goals $x$ and $y$ are both leaves of the center vertex; with $x$ on the left middle vertex it is solvable in 4 turns | — [[2-algorithms/05-basic-graph-algorithms-exercises#exercise-518--three-seashells\|Ex. 5.18]] |
| Ex. 5.19(b), p. 216 | "where both coins are on the same vertex" | all three coins | — [[2-algorithms/05-basic-graph-algorithms-exercises#exercise-519--coins-that-must-keep-moving\|Ex. 5.19]] |

## Algorithms, Chapter 6 · Depth-first search

| where | as printed | should be | why it matters |
|---|---|---|---|
| p. 233, Figure 6.9 (TopSortDFS) | the recursive call is $\textsf{TopSortDFS}(v, \textit{clock})$ | $\textsf{TopSortDFS}(w, \textit{clock})$ | as printed it recurses forever as soon as a vertex has an edge to a new vertex — [[2-algorithms/06-depth-first-search#63-topological-sort\|§6.3]] |
| p. 233, PostProcess | "if $v$ is unmarked" | "if $v.\textit{status} = \textsf{New}$" (the algorithm never marks) | — [[2-algorithms/06-depth-first-search#63-topological-sort\|§6.3]] |
| p. 233, PostProcessDag | calls $\textsf{PostProcessDagDFS}(s)$ | $\textsf{PostProcessDagDFS}(v)$ | — [[2-algorithms/06-depth-first-search#63-topological-sort\|§6.3]] |
| p. 236, memoized LongestPath | "return $v.\textit{LLP}$" indented inside the "if" | at the outer level | as printed a second call on the same vertex returns nothing — [[2-algorithms/06-depth-first-search#64-memoization-and-dynamic-programming\|§6.4]] |
| p. 238 | "every back edge joins two edges in the same strong component" | two **vertices** | — [[2-algorithms/06-depth-first-search#65-strong-connectivity\|§6.5]] |
| p. 242, Tarjan's algorithm | it "identifies a source component" first | a **sink** component (the first one finished) | the same source/sink mix-up is the classic Kosaraju–Sharir trap — [[2-algorithms/06-depth-first-search#66-strong-components-in-linear-time\|§6.6]] |
| p. 243, Figure 6.18 (FindLow) | the second "for all vertices $v$" loop is printed inside the first | the two loops are consecutive | as printed, Lemma 6.4 finds no root on a two-vertex cycle — [[2-algorithms/06-depth-first-search#66-strong-components-in-linear-time\|§6.6]] |
| Ex. 6.4(b)ii, p. 246 | a non-root $v$ is a cut vertex iff "at least one descendant of each child of $v$ is a neighbor of a proper ancestor of $v$" | iff **some** child of $v$ has **no** descendant (itself included) adjacent to a proper ancestor of $v$ — the printed condition is the one for *not* being a cut vertex | — [[2-algorithms/06-depth-first-search-exercises#exercise-64--cut-vertices\|Ex. 6.4]] |
| Ex. 6.6(b), p. 247 | a transitive reduction is unique "if and only if" $G$ is acyclic | only the "if" half holds: the 2-cycle $u\to v\to u$ is its own unique reduction | — [[2-algorithms/06-depth-first-search-exercises#exercise-66--transitive-closure-and-reduction\|Ex. 6.6]] |
| Ex. 6.11, p. 250 | $x, y \leftarrow x+y, x-y$ "requires two temporary variables"; "either a=0; b=1 or a=0; b=1" | one temporary suffices ($t \leftarrow x$; $x \leftarrow x+y$; $y \leftarrow t-y$); the second order is b=1; a=0 | — [[2-algorithms/06-depth-first-search-exercises#exercise-611--parallel-assignment\|Ex. 6.11]] |

## Not errors, but easy to trip over

- **State elimination's name.** Some summaries call §4.8's method "Han and Wood's algorithm"; the current book credits the idea to McNaughton and Yamada (1960), with Lee (1960) and Kleene (1951) before them. Same algorithm — [[concepts/state-elimination]].
- **Thompson's star gadget.** The book closes the loop of $S^*$ from the new accepting state back to the new start state; many other sources loop from $t_S$ back to $s_S$. Both are correct and have the same size; only some $\varepsilon$-reaches differ — [[concepts/thompsons-algorithm]].
- **The cover in the figure of Exercise 4.3** (p. 178) has 7 intervals, but 6 suffice; the caption only calls it "a cover", so nothing is wrong — just don't take it as the answer to the exercise — [[2-algorithms/04-greedy-algorithms-exercises#exercise-43--smallest-cover|Ex. 4.3]].
- **Which way dependency edges point.** Chapter 5 draws an edge from each subproblem to the subproblems that *use* it, so an evaluation order is a topological order; Chapter 6 points them the other way and calls the same order a *reverse* topological order — and its Figure 6.12 reuses Chapter 5's picture. Both are fine; mixing them is not — [[2-algorithms/06-depth-first-search#64-memoization-and-dynamic-programming|§6.4]].
- **"Recognizable" and "acceptable".** Chapter 6 says *recognizable*, Chapter 7 says *acceptable*; they mean the same — [[0-toolkit/01-notation-and-conventions]].

### Sources for this page

Each item was found by the writer or the independent reviewer of the page linked in its row, read against Erickson, *Models of Computation*, chapter PDFs of December 28, 2018. The concrete ones are checked by scripts: the §4.7 state counts by `tools/checks/ch04.py`; the CNF counterexample by `tools/checks/ch05.py`; the §6.3 machine (with both moves) and the §6.8 encodings by `tools/checks/ch06.py`; the PCP string by `tools/checks/ch08.py`; the advice-view counterexample and the Cook–Levin tableau (with both cell ranges) by `tools/checks/ch09.py`. The *Algorithms* items were read against the first edition (June 2019) and are checked by `tools/checks/a01.py`, `a01x.py`, `a02.py`, `a03.py`, `a03x.py` and, for Chapters 4–6, `a04.py` through `a06x.py` — in particular the printed and corrected loop bounds of FastSubsetSum and OptimalBST3, the Fibonacci call counts, the 97 palindrome decompositions and the back-and-forth answers 7 and 10.
