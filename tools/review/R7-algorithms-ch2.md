# R7 — review of Algorithms Chapter 2 (Backtracking)

Reviewer log (2026-10-19). Pages: `content/2-algorithms/02-backtracking.md`, `content/2-algorithms/02-backtracking-exercises.md`,
`content/concepts/{backtracking,subset-sum,longest-increasing-subsequence}.md`. Sources: `/home/claude/work/algo/ch02.txt` and
the PDF (book pp. 71–96 = PDF pp. 89–114; pp. 79, 86, 92, 93 rendered and read). Scripts: `tools/checks/a02.py` (118 checks,
ALL OK, saved to `a02.out`), `tools/checks/a02x.py` (67 checks, ALL OK, saved to `a02x.out`). `tools/check.py --only
2-algorithms/02,concepts/backtracking,concepts/subset-sum,concepts/longest-increasing-subsequence`: OK, no errors.

## Book errata confirmed against the PDF

- p. 79, Figure 2.6 (ConstructSubset): base case printed `if T < 0 or n = 0`; must be `i = 0` (with `n` fixed the recursion
  indexes X[0], X[−1], …). Page and check (`ConstructSubsetLiteral`) agree.
- p. 92, OptCost recurrence: printed `Σ_{j=i}^{k} f[i]`; the summand must be `f[j]` (the text before it says Σ f[i] over the
  interval, and the cost recurrence one display earlier sums f over all keys).
- p. 93, number of BSTs: printed `N(n) = Σ_{r=1}^{n−1} N(r−1)·N(n−r)`; the upper limit must be n (otherwise N(1) = 0 and all
  N(n) = 0). Printed closed form `Θ(4^n/√n)` is the growth of C(2n, n); the Catalan numbers are C(2n,n)/(n+1) = Θ(4^n/n^{3/2}).
- Minor (not on the page's errata list): p. 73 says the root of the recursion tree is the empty board "(with r = 0)", but the
  empty-board call is PlaceQueens(Q, 1) (the page says r = 1, consistent with the pseudocode); p. 88 LISbigger array version
  prints `A[2 .. n)` (bracket typo); p. 95 Ex. 5(b) "removing removing".

## 02-backtracking.md

Checked: every section against the book (2.1–2.8 headings, Figure 2.2, PlayAnyGame, both SubsetSum versions, Figure 2.6,
both Splittable versions and the recurrence, MaxScore, LISbigger array/index/recurrence, LIS wrapper, LISfirst recurrence and
both LIS wrappers, Cost and OptCost recurrences, both ♥ analyses); every rubric box (description of the generalized problem,
base cases, calls, combine, recurrence + solution, correctness line) — each would earn full credit; every recurrence re-derived
by hand: PlaceQueens T(m) ≤ mT(m−1)+O(n²) → O(n²·n!); game tree N(n) = 1+N(n−1)+N(n−2) = F_{n+3}−1; SubsetSum and LISbigger
2T(n−1)+O(1) with exact worst-case call counts 2^{n+1}−1; Splittable/LISfirst full-history recurrence → 2T(n−1)+α; a^{n−1}b
worst case W(m) = m + Σ_{k<m} W(k) = 2^m−1; LISfirst calls 2^{n−i} on increasing input; OptCost calls C(n) = 1+2ΣC(k) = 3^n;
3^n vs Catalan crossover at n = 17 (N(16) = 35357670 < 3^16, N(17) = 129644790 > 3^17); the halving-frequencies path claim via
the rotation argument; the 7-key example (both trees' costs by hand, 49 and 56). Figures: Gauss board (all eight columns from
SVG coordinates), 4-queens tree (every node's queens from coordinates; 1,4,6,4,2; four dead ends), game tree (labels, faded
subtree = the 4-node subtree of 2, call order 4,3,2,1,0,0,1,0), LIS pictures (chosen 1,4,5,6 match the book's highlighting on
p. 86; take-2 candidates 12,13,14,15,19), OBST trees. Check script implements each algorithm as printed and compares with brute
force; the key numeric claims (solution/call tables, subset-sum instances, LISfirst table, OptCost table, 3^n calls, Catalan
asymptotics) are checked as stated.

Changes:
- Abstract: "the same recurrences become the polynomial-time dynamic programs of Chapter 3" → "… become the dynamic programs of
  Chapter 3 — polynomial-time for segmentation, LIS and optimal search trees, pseudo-polynomial O(nT) for subset sum". Why:
  subset sum's DP is not polynomial-time (NP-hard; the concept page says so); the old sentence implied otherwise.
- §2.2 definition box: added "(This assumes that every finished game has a winner — no draws — as in both games on this
  page.)"; PlayAnyGame rubric "Problem": added "(in a game without draws)". Why: with a drawn terminal state the recursion
  returns Good from a state that can only draw, so "Good iff the player to move can force a win" is false in general. New check
  in a02.py (`play_generic` on a two-state draw game).

Doubts: none on the mathematics. PlayAnyGame's "Time" bullet gives no closed form in general (game-dependent) — acceptable.

## 02-backtracking-exercises.md

Re-solved every exercise from the statement before reading the solutions (2.1(a,b), 2.2(a–c), 2.3(a), 2.4(a–f), 2.5(a,b),
2.6(a–c)); the page's solutions match mine. Checked statements against pp. 93–96 (♥ parts 3(b), 5(c) correctly skipped; no
other parts marked). Verified by hand: 2.1(b) example weights 3/8/7/5; ARTISTOIL = 0+1+1; BOTHEARTH/PINSTART cuts 3,8,12,15,19;
ShortestChain generalization, base case, candidate X[k]+1, depth ≤ n−1; l(15) = 5 vs binary 6; binary chain for 374 = 8+6−1 =
13; lcs proof including "match wins"; scs proof and m+n−lcs = 14; bitonic split at the peak and the "≥ 2" conditions;
oscillation direction (X1 > X2 < …); sos case analysis (t = 0/1/2 costs, SDown ≤ 1+SUp, collapse to the scan) and the witness
3,1,4,1,5,0,9,2,6,5,10,3 position by position; convex LXS recurrence and 3,1,1,2,6; MinDel base cases and the greedy lemma; PPAP
copies at 1,4,8,14 and 9,10,13,18; AVL height pairs and h ≤ 0 base cases; red-black Black/Red/Any with null = black-height 0;
AA left-child rule. a02x.py brute-forces each recurrence (all small inputs), l(374) = 11 by exhaustive iterative deepening over
all (not only star) chains, and RB/AA/AVL optima by enumerating all BSTs and all colorings. Rubric format: every algorithm part
has description (with generalization), base cases, calls, combine and (where asked) recurrence + solution. HW7: nothing
equivalent (LCS of 2.4(a) is the plain book exercise; no LCIS/LDCS, palindromic common subsequence, rectangles or broadcasting).

Changes:
- Ex 2.5 statement (b): "after removing the two copies of A …" → "after removing two symbols from PENPINEAPPLEAPPLEPEN (for
  instance its two copies of A) …". Why: faithful to the book's wording; the specific pair is the page's own example.

Doubts: 2.4(c) returns 0 when no bitonic subsequence exists — a convention (the book leaves it open); the page states it.

## concepts/backtracking.md, subset-sum.md, longest-increasing-subsequence.md

Checked: definitions and recurrences against §§2.3, 2.6, 2.7, 3.6, 3.8 (DP versions: suffix SS(i,t) with the t < X[i] case,
S[1..n+1, 0..T], rows from n+1 down; LISbigger table columns right to left; FastLIS2 as in the book); NP-hardness reference
§12.12 (TOC: "Subset Sum (from Vertex Cover)", p. 402); examples NoAdj on [4,1,2,7,3] (9 yes, 10 no, the three 10-subsets),
[3,5,6,8]/14 (with-first finds {6,8}, ConstructSubset finds {3,5,6}; reachable sums), 5 2 8 6 3 6 9 7 (LISfirst 3 4 2 2 3 2 1 1,
LISfirst(0) = 5, LISbigger(1,2) = 2) — by hand and in a02.py. Traps are real traps (hash table memo is penalized by the rubric).

Changes: none.

Doubts: none.
