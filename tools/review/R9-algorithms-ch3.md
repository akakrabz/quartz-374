# Review R9 — Algorithms Chapter 3 (dynamic programming), its concept pages and exercises (2026-10-19)

Method: read every page in full (figure captions and the figure script included); re-derived every function
description, recurrence, base case, memoization structure, evaluation order (entries filled before they are read)
and running time; compared sections, pseudocode and examples with the book (PDF pages rendered with pdftoppm, book
p. = PDF p. − 18); re-solved each exercise from its statement before reading the solution, and recomputed the key
numbers with an independent script (greedy failures 416, 455; r = 1.44876; 97 palindrome decompositions; 3.10 → 7;
23 PPAP occurrences; Cut = 2; LPS 11; SPS 13; the four 3.8 examples); read the check scripts against the pages and ran
them; ran tools/check.py on all assigned pages.

## 2-algorithms/03-dynamic-programming.md

Checked: meters M(n) = F(n+1); RecFibo T(n) = 2F(n+1) − 1, leaves F(n) + F(n−1); RecFibo(n−k) called F(k+1) times
(0 ≤ k < n); MemFibo 2n − 1 calls and bottom-up fill; IterFibo, IterFibo2 (F(−1) = 1); matrix identity, F_n =
F_m F_{n−m−1} + F_{m+1} F_{n−m} and both substitutions; FastRecFibo (⌊log2 n⌋ + 1 calls); bit-cost table and M(n);
Splittable recurrence, FastSplittable (n(n+1)/2 IsWord calls), a^{n−1}b count 2^n − 1, THEMENTOR table; recipe and
rubric template against the course rubric text (rubrics.txt, incl. "at least 3/10" and labeled axes); greedy
counterexamples; LISbigger (range, column n+1, column-wise order; rows from the top fail, bottom-up rows work);
LISfirst (entry 0) and the [3,1,4,1,5,9,2,6] table; edit-distance recurrence, order, the ALGORITHM/ALTRUISTIC table
(= transpose of the book's p. 115 table, entry by entry), the three alignments (= book p. 116), FOOD/MONEY;
subset sum both recurrences, order, examples; OptCost, InitF, three orders, n(n+1)(n+2)/6, the f = [5,2,1,3,4]
table, unique tree, greedy 35; MIS / MISyes / MISno, TreeMIS(2) against p. 122, O(n) argument; summary table.
Every DP description would earn the 3 rubric points (named, explicit parameters, portion of input stated).

Changes:
1. §3.8 FastSubsetSum. Before: `for t ← 1 to X[i] − 1` (as printed on book p. 117). After:
   `for t ← 1 to min{X[i] − 1, T}   ⟨⟨the book prints X[i] − 1⟩⟩`, plus one sentence after the block: with the book's
   bound, an element X[i] > T + 1 makes the loop write past column T. Why: the table is S[1..n+1, 0..T]; the printed
   loop reads S[i+1, T+1] and writes S[i, T+1] when X[i] > T + 1. Sources' list of corrections extended.
   a03.py: FastSubsetSum gained a `book_bound` flag; two checks added (page shows the min bound; the printed bound
   raises an index error exactly when some X[i] > T + 1, and is otherwise correct). The old transcription had
   silently capped the loop at T.
2. Figure a03-fib-tree caption (tools/figs_a03.py, regenerated, assembled). Before: "and every second call is
   answered at once". After: "and the second recursive call of each of them is answered at once". Why: "every
   second call" reads as "every other call", which is not what happens (call order F6 F5 F4 F3 F2 F1 F0 F1 F2 F3 F4).
   Only that caption changed (other three figures byte-identical after regeneration).

## concepts/dynamic-programming.md, concepts/memoization.md, concepts/edit-distance.md

Checked: definitions, recipes, templates and traps against the rubric; MinCoins for (1,4,5) (table 0 1 2 3 1 1 2 3 2,
greedy 5+1+1+1); Choose call counts (2C(n,k) − 1; k(n−k) memoized subproblems; 503 / 25 / 51); FOOD/MONEY table,
bold read-back path, alignment F O _ O D, exactly three optimal alignments. No changes.

## concepts/optimal-binary-search-trees.md

Checked: recurrence, ranges, orders, f = (2,3,4) example (15 vs greedy 16), traps.
Change: recipe step 2. Before: "combine the two smaller intervals with a cost that depends only on (i,k)". After:
"… with a cost computed from i, k and r (here F[i,k], the same for every r)". Why: stated as the general interval
pattern, the old wording excludes split-dependent costs (e.g. matrix-chain-style recurrences); for optimal BSTs the
cost is F[i,k] either way.

## concepts/dynamic-programming-on-trees.md

Checked: pattern and O(n) bound; MISyes/MISno; naive path recursion F(n+2) − 1 calls; VCin/VCout; figure-tree cover
{r, d, e} of size 3 = 11 − 8.
Change: "in any graph, the complement of an independent set is a vertex cover" → "…, and the complement of a vertex
cover is an independent set". Why: "3 = 11 − 8, as it must be" needs both directions (min VC = n − max IS).

## 2-algorithms/03-dynamic-programming-exercises.md

Checked every statement against book pp. 123–130 (paraphrases faithful; the corrections to 3.6(b), 3.7(d), 3.7(f),
3.9(e), 3.10 verified on the rendered pages); re-solved 3.1–3.10 (all parts present) before reading the solutions:
3.1 (416 smallest greedy failure, next 455; r ≈ 1.449; O(k)); 3.2 (counts of IsWord calls); 3.3 Kadane and
max/min suffix products (traps [−2,3,−4], [3,¼,3]); 3.4 (wrap = total − min interval; LongEnd; block window minima;
successor queries O(n log n); two pointers); 3.5(a)–(h) (LCS, SCS proofs; bitonic with 1 < i < ℓ; OscDown/OscUp;
the O(n) shortest-oscillating-supersequence lemma — fillers max+1 / min−1, gaps of 0/1/2 fillers suffice, parity
DP; the O(n³) pair DP and the three third-element tests); 3.6 (Shuffle, SmoothX/SmoothY and their order; counting
argument; book picture is 8 + 11 X's); 3.7 (greedy key fact, Cut, MinCost with negative costs, NumOcc, bit bounds);
3.8 Mirror; 3.9 LPS, SPS (both directions of the proof), IsPal, MinPal, MaxMinLen, NumPal (97); 3.10 order by
decreasing value, answer 7, book sequence breaks the stated rule, swapped-rule answer 10.
HW7: 3.5(i) omitted; no longest common increasing/decreasing subsequence, palindromic common subsequence, rectangle
separability or tree broadcasting anywhere on the pages or in the check scripts.

Change: Exercise 3.4 preamble. Before: "… and allow the empty subarray (sum 0) as in Exercise 3.3." After: "… as in
Exercise 3.3 wherever its length is permitted (in (b) only when X = 0)." Why: in (b) a subarray of length ≥ X ≥ 1
cannot be empty; the solution (and the brute force in a03x.py) already excludes it.

## Runs

a03.py ALL OK (a03.out saved; 2 new checks); a03x.py ALL OK (a03x.out saved); tools/check.py --only on the six
prefixes: OK.

## Remaining doubts

- 3.7(f) says "part (d)"; the O(1)-addition assumption it relaxes is stated in (e), so (e) is almost certainly meant.
  The page answers both, which is safe.
- The book hints that one of 3.5(a)–(h) has an O(n) greedy solution; the page solves (d) by an O(n²) DP and (e) by an
  O(n) DP and does not say which one the hint means. Correct as is; an O(n) solution of (d) could be added later.
- 3.9(a) (longest palindromic subsequence) and 3.5(a) (LCS) are standard book exercises and not equivalent to HW7's
  longest palindromic *common* subsequence of two arrays, but they are its building blocks; left in.
- 3.1(b)/(c) use the input name k also as the function's parameter (MinBills(k)); acceptable, not changed.
