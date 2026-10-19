---
title: "Errata in the books"
description: "Slips in Erickson's two textbooks found while writing this site — in Models of Computation a wrong move in a printed Turing machine, a too-weak CNF rule and an off-by-one in the Cook–Levin tableau; in Algorithms wrong summation limits, a wrong growth rate, array ranges and loop bounds that do not fit their tables, a broken non-recursive Hanoi rule and three wrong counts in exercise examples — each with the correction and the section here that has it right."
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

## Not errors, but easy to trip over

- **State elimination's name.** Some summaries call §4.8's method "Han and Wood's algorithm"; the current book credits the idea to McNaughton and Yamada (1960), with Lee (1960) and Kleene (1951) before them. Same algorithm — [[concepts/state-elimination]].
- **Thompson's star gadget.** The book closes the loop of $S^*$ from the new accepting state back to the new start state; many other sources loop from $t_S$ back to $s_S$. Both are correct and have the same size; only some $\varepsilon$-reaches differ — [[concepts/thompsons-algorithm]].
- **"Recognizable" and "acceptable".** Chapter 6 says *recognizable*, Chapter 7 says *acceptable*; they mean the same — [[0-toolkit/01-notation-and-conventions]].

### Sources for this page

Each item was found by the writer or the independent reviewer of the page linked in its row, read against Erickson, *Models of Computation*, chapter PDFs of December 28, 2018. The concrete ones are checked by scripts: the §4.7 state counts by `tools/checks/ch04.py`; the CNF counterexample by `tools/checks/ch05.py`; the §6.3 machine (with both moves) and the §6.8 encodings by `tools/checks/ch06.py`; the PCP string by `tools/checks/ch08.py`; the advice-view counterexample and the Cook–Levin tableau (with both cell ranges) by `tools/checks/ch09.py`. The *Algorithms* items were read against the first edition (June 2019) and are checked by `tools/checks/a01.py`, `a01x.py`, `a02.py`, `a03.py` and `a03x.py` — in particular the printed and corrected loop bounds of FastSubsetSum and OptimalBST3, the Fibonacci call counts, the 97 palindrome decompositions and the back-and-forth answers 7 and 10.
