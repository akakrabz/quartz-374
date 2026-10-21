# R8 — review of Algorithms Chapter 1 (Recursion)

Reviewer R8, 2026-10-19. Pages: `content/2-algorithms/01-recursion.md`, `content/2-algorithms/01-recursion-exercises.md`,
`content/concepts/{recursion,divide-and-conquer,recursion-trees,linear-time-selection}.md`; checks `tools/checks/a01.py`,
`tools/checks/a01x.py`; figures `tools/figs_a01.py`.

## Method
- Book: `ch01.txt` read in full for §§1.1–1.10 and Exercises 1–13; PDF pages rendered and read for pp. 28, 29, 37, 43–51
  (Lemma 1.1 proof, Figures 1.7/1.8, MomSelect, SlowPower/PiṅgalaPower, every exercise statement and its ♥/◆/♣ marks,
  Figure 1.17 at 300 dpi). Recurrences appendix: Master Theorem and Akra–Bazzi statements.
- Re-derived every recurrence and solution, every count and every proof step by hand before reading the page's version;
  re-solved each exercise from the statement first (move counts ⌊2^{n+1}/3⌋, 2F_{n+1}−1, (3^n−1)/2, 3^n−1,
  (2n³+3n²−2n)/3; Ex 1.6–1.8; pancakes 2n−3 and 3n−2; StoogeSort; Cruel/Unusual; inversions).
- Independent spot checks (own code, not the site's scripts): Pisa BFS n ≤ 8 = 2F_{n+1}−1; restricted Hanoi BFS n ≤ 7
  (hub→end (3^n−1)/2, end→end 3^n−1); repeated-squaring count = ⌈lg n⌉ iff n has ≤ 2 one-bits.
- Scripts read in full: each implements the page's pseudocode as written and compares with brute force/BFS/exact
  closed forms. a01.py: 119 OK before, 125 OK after my additions, ALL OK. a01x.py: 104 OK, ALL OK (unchanged; .out re-saved).
- Figures: inlined SVG = generated files; MOM_GRID data checked cell by cell (medians 10,11,13,14,15,24,31,33,36,37;
  14 shaded < 15, 17 shaded > 15); three-cases and Hanoi figures viewed in light/dark — correct, unchanged.
- `tools/check.py --only 2-algorithms/01,concepts/…`: OK (before and after). Aliases unique site-wide.

## 01-recursion.md
Checked: all ten sections, every pseudocode block against the book (MergeSort/Merge, QuickSort/Partition, QuickSelect,
MomSelect, SplitMultiply, FastMultiply, PiṅgalaPower, PeasantPower), Lomuto partition trace of SORTINGEXAMPL (r = 9),
recursion-tree table (9 rows), domain transformation (α = 2), MomSelect counting incl. ∞-padding (both sides ≥ 3⌊m/2⌋−1,
second call ≤ n − 3⌊m/2⌋ ≤ 7n/10 + 3/2), block-size table (ratios 1, 9/10, 6/7), 16n comparison bound, Karatsuba
negative-split note, multiplication count ⌊lg n⌋ + β(n) − 1, a^15 chains, Hanoi optimality proof, exam box vs rubric text.
Changes:
1. Mergesort trap: "only a balanced split gives Θ(n log n)" → "a split into constant fractions (halves, or even n/3 and
   2n/3) gives Θ(n log n), while m = 1 gives T(n) = T(n−1) + O(n) = Θ(n²)". Why: an n/3 split is also Θ(n log n).
   New checks: m = 1, n−1, ⌊n/3⌋ splits sort; m = 1 Merge work n(n+1)/2 − 1; ⌊n/3⌋ split work/(n lg n) settles.
2. Linear-time selection key box: added "if the elements are distinct (as the analysis assumes; with repeated values use
   a three-way partition, see the traps below)". Why: with Lomuto's Partition an all-equal array gives a second call of
   n − 1 elements and superlinear time. New check: comparisons per element on all-equal arrays grow ~4× per doubling.
3. Summary: "⌈lg n⌉ is a lower bound, met exactly when n is a power of 2" → "…which both algorithms meet when n is a
   power of 2 (more generally, exactly when n has at most two 1 bits)". Why: false as an "iff" (n = 3, 5, 6, 12 meet it).
   New checks (n < 2^16, and the examples).
No other errors. The page already uses the corrected forms of the book slips (Lemma 1.1 indices, SlowPower n − 1,
MomSelect index, Lomuto's real partition row).

## 01-recursion-exercises.md
Checked: every statement against the PDF (faithful; markers right; skipped parts justified), every solution re-solved
and checked line by line — H1/H2 and all four 1.1 parts (incl. the (c) parity invariant with fixed pretend disks), Off/On
recursion and reducedness at the joints, Pisa algorithm and Figure 1.17 (first 7 moves for n = 7, 5th move carries disks
1–2 off the leaning needle), 1.4(a) lower-bound argument, Shift for k = n + 1 (spread/hop distances, sum), 1.6 table,
1.7(j–l) incl. ρ ≈ 0.6596 and the substitution with d = 1/(r−1), 1.8(m,n,p,q) exact forms and the n_k analysis, pancake
algorithms, worst-case families and the adjacency bound, P_n for 1.10(a), StoogeSort proof/counter-example/recurrence/
real-valued bounds/swaps = inversions, Cruel variants on 3 4 1 2 and comparison counts n^{lg3}/3 and n^{lg3} − n, CountInversions.
Each algorithmic solution has the five rubric parts.
Change: 1.11(d) "C(n)/n^α stays between 0.15 and 0.81 for all n ≤ 200,000" → "for all 2 ≤ n ≤ 200,000". Why: C(0) = C(1) = 0.
(The script already checks 2 ≤ n.)

## concepts/recursion.md
Checked: definition, template, traps, BinarySearch (subproblem sizes ≤ ⌊n/2⌋, ≤ ⌊lg n⌋ + 2 calls, the A[m..n] loop
on [4], x = 9), anchors. No change.

## concepts/divide-and-conquer.md
Checked: pattern, rubric template (3/1/2/2/2), table, MinMax (3n/2 − 2 at powers of 2, 1534 vs 2046, n = 6 takes 8).
Changes: "subproblems whose sizes add up to n … give about lg n levels" → "balanced subproblems …" (1 vs n−1 also adds
up to n and is Θ(n²)); trap "the recursion is exponential" → "can take exponential time" (overlap does not always give
exponential time).

## concepts/recursion-trees.md
Checked: three cases (Θ forms), n^d shortcut, traps, Strassen example T(2^k) = (7^{k+1} − 4^{k+1})/3. No change.

## concepts/linear-time-selection.md
Checked: statements, recipe, traps, the k-closest-to-median example (μ = 12, distances, d = 4, {12, 14, 9, 8}).
Change: key box "It leaves at most about 7n/10 elements" → "For distinct elements it leaves at most about 7n/10 elements
for the second call (repeated values: see the traps)". Why: same distinctness assumption as on the chapter page.

## Remaining doubts (not changed)
- Ex 1.3 asks for the smallest possible number of moves; optimality of 2F_{n+1} − 1 is only BFS-confirmed (n ≤ 9) and the
  page says a general proof is not given. A short proof is not obvious: the largest disk can finish with a block move from
  the leaning needle carrying smaller disks, and moving a stack onto the leaning needle costs more than across.
- Ex 1.11(a) handles repeated values with "read the k largest as a multiset; nothing changes" — correct, a little brief.
- Ex 1.10(a) fixes the middle position as ⌈n/2⌉ (the book does not say); the page notes other choices work the same way.

## Book errata confirmed (PDF)
- p. 28, Lemma 1.1 proof: "for all k from 0 to n, the last n − k − 1 iterations" → "for all k from 1 to n + 1, the last
  n − k + 1 iterations" (B[k..n] has n − k + 1 entries; the proof's own step uses n − k for B[k+1..n]).
- p. 29, Figure 1.7: Partition row A G O E I N L M P T X S R is not what the book's Lomuto Partition (Figure 1.8) produces
  with pivot P: O I N G E A M L P R T S X, r = 9 (inconsistency; the printed row is still a valid partition).
- p. 37, MomSelect: "r ← Partition(A[1 .. n], mom)" passes a value; Partition's second argument is an index (p. 29).
- p. 43, "This iterative algorithm requires n multiplications" → n − 1 (the loop runs for i = 2..n; p. 42 says n − 1).
- Ex 1.1(b), p. 44: after a move of a disk k ≥ 2, disk 1 has two legal moves, so "the only legal move" is ambiguous; needs
  "disk 1 never returns to the peg it just left".
- Ex 1.1(d), p. 45, RulerHanoi: "if n − i is even, move forward" → "if n − ρ(i) is odd, move forward (else backward)";
  as printed it fails for every n ≥ 1 (n = 1 moves disk 1 to peg 1).
- Ex 1.5(a), p. 48: "(This is exactly the same as problem 4(a).)" — not exactly: 4(a) starts on the hub peg, (3^n − 1)/2
  moves; 5(a) goes end to end, 3^n − 1 moves.
- Ex 1.10(a), p. 50: "preserves the existing order of all elements smaller than the pivot" appears twice; the second
  should say "larger".
- Unstated assumptions (not misprints): §1.8's 3n/10 bound needs distinct elements (or a three-way partition); the
  brute-force threshold "n ≤ 25 ⟨⟨or whatever⟩⟩" must be at least 5 so that ⌊m/2⌋ ≥ 1.
- Spelling only: p. 47 "Tower of Hanoi puzzle In each problem", p. 48 "Tower of Hanoi puzzle The puzzle" (missing
  periods); p. 49 fn 15 "is an long-standing".
