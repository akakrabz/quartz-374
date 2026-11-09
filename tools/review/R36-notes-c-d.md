# Review R36 — lecture notes C (DP for formal languages and automata) and D (Advanced dynamic programming), concept page cyk-algorithm, link lines in dfa-minimization and chomsky-normal-form (2026-11-08)

Method: read the three pages in full (callouts, captions, Sources) and the two link lines; read both note texts in full
and rendered the pages where symbols matter (C pp. 1, 3–6; D pp. 3, 4 (Figure D.1 at 200 dpi), 5, 9, 10, 12, 13);
re-derived every recurrence, table, count and bound; read nc.py and nd.py against the pages and ran them (ALL OK
before and after). Own brute force in /tmp/r36/py (not in the repo): Hirschberg worst-case recurrence (T(5,40),
max T/mn, the 2mn + (m+n)log2 m bound), Figure D.1 recomputed, the Edit/Half tables, Knuth's example f = [5,2,1,3,4]
(roots, cost 31, 24 vs 30 root trials), the f = [1,1,1,1,1] ties, even–odd vs divide-and-conquer examined entries for
m = 3, 7, 15, 31 (200 random monotone arrays each: odd-row version never equal, even-row version always equal), the 11
violating 2×2 subarrays of the first 5×5 array (second: 0), Reduce on rows (1,1),(0,5) printed vs corrected. By hand:
the NFA table for 0110, the CYK tables for (())() and 0011/0101, the (n³ − n)/6 split count, the corner-block Monge
proofs, the characterization coefficient (slack of U_{a,b} is the indicator of (a, b−1)), FindMatches on A = B = AB.
7-word overlap scan page ↔ note: only pseudocode, quoted placeholders/status line, titles, the lemma list (a)–(g) and
short phrases — no copied prose. Aliases of cyk-algorithm unique site-wide, case-insensitive (own scan).

## Note errors claimed by the writer — verdicts

C (Dynamic Programming for Formal Languages and Automata)
- p. 1 "a directed graph, whose edges are called states" (vertices): **confirmed.**
- p. 3 "δ[p,a,q] = True iff p ∈ δ(q,a)": **confirmed** (rendered). Pseudocode uses δ[q,w[i],r] as r ∈ δ(q,w[i]).
- p. 3 recurrence's ⋁ over r ∈ δ(q,a) with a unbound (correct δ(q,w[i])): **confirmed** (rendered).
- p. 5 parenthesis grammar generates only ε (author's "This is incorrect."): **confirmed** — every right side of A, B,
  C contains A or B, so none of them derives a terminal string.
- Grammar length = number of rules makes the O(L²) bound false: **confirmed**, but the definition is on **p. 4** and
  the bound on p. 5 (page said p. 5; fixed to pp. 4–5). The counting argument (one-rule grammars S → w vs finitely
  many CNF grammars with O(1) rules) is right.
- p. 6 "Gen?(A, 1, n) = True" (correct S): **confirmed** (rendered).
- p. 6 CYKParse "for i ← n down to j + 1" (correct j − 1 down to 1): **confirmed** (rendered); the split loop is
  empty for i > j and Gen[S,1,n] is never written for n ≥ 2.
- Typos "it it not hard" (p. 4), "an equivalent CFG grammar" (p. 5): **confirmed.** Added: "an equivalent grammar
  Chomsky normal form" (missing "in", p. 5), "the production rules of the CFL" (p. 4).

D (Advanced Dynamic Programming)
- T ≤ 2αmn induction: **confirmed as a gap** (base cases T(m/2, 0) = Θ(m) and ⌈m/2⌉ rounding ignored; worst case of
  the recurrence T(5,40) = 442 > 400, max T/mn = 2.588 for m,n ≤ 40). It is on **p. 3**, not p. 2 (page fixed).
  O(mn) is right: T ≤ 4mn + m + n survives the induction (step ≤ 3mn + 3n + m for m ≥ 2).
- p. 4 A[1..n], B[1..m] vs A[1..m], B[1..n] elsewhere: **confirmed** (rendered).
- p. 4 Figure D.1 column O, rows U..», printed 3, correct 2: **confirmed** (200 dpi render; own table; every other
  entry correct).
- p. 5 FindMatches: "i < m and j < n", "ii ← i + 1", unbounded run loops: **confirmed** (rendered; A = B = AB finds
  only (1,1); a run of length 2 loops forever).
- p. 5 SparseLCS: "to K" (correct K + 1), "min" (correct max), "Sort M": **confirmed** (rendered).
- p. 6 FasterOptimalSearchTree: "for i ← 1 downto n" (empty for n ≥ 2), missing base cases, OptRoot[i,i−1] = i lets
  d = 0 try r = j + 1, "d ← 0 to n" / "i ← 1 to n" run j past n: **confirmed.**
- p. 6 Knuth's inequality needs a fixed tie rule: **confirmed** (imprecision rather than a false statement: the note
  speaks of "the" optimal root). f = [1,1,1,1,1]: roots {2,3} for [1..4], {2,3,4} for [1..5].
- p. 8 "morally identical … same subset of array entries and the same comparisons": **confirmed** for the printed
  odd-row version (never equal for m = 2^k − 1); the even-row variant matches divide and conquer exactly.
- p. 10 q_i in the distance formula (correct q_j): **confirmed** (rendered).
- p. 11 upper-right / lower-left blocks must contain the corner: **confirmed as an ambiguity** (single middle 1 and an
  upper-left block are not Monge; corner blocks are, by (x − x′)(y′ − y) ≥ 0).
- p. 12 Reduce "k ← 1" and "≥": **confirmed** (rendered); rows (1,1),(0,5): printed keeps only column 2, LM = (1,1).
  With > the start must be k = 2 (else column 1 is pushed twice).
- p. 13 "t = n" (correct t = m) and "t < m columns" (correct t ≤ m): **confirmed** (rendered).
- Typos (pp. 1, 2, 6, 7, 11, 12, 15; Burdyok; "A new algorithms"): **confirmed.** Added: "hilighted" (p. 7), "the
  exactly the same" (p. 8), "an lower-left" (p. 11).
- **New:** p. 14 "Reduce the input array to at most m rows" — Reduce removes columns (correct: at most m columns).
  The page's own text was already right; added to Sources.

## Other checks (no change needed)

- Rubric format: Dist(k,p,q), Accepts?(q,i), Gen?(A,i,j), Half(i,j), LCS(i,j), LCS[k], dist_k(v) all have a named
  function with English description, recurrence with base cases, memo structure, evaluation order (outer loop named),
  time. OptCost on D lacked the English description (fixed, one clause).
- Bounds: NFA O(n|Q|²) (exactly n|Q|² innermost tests), backtracking 1 + |Q| + … + |Q|ⁿ calls; CYK O(n³L), exact
  r(n³ − n)/6; Hirschberg O(mn) time, O(m + n) space; sparse LCS O(m log m + n log n + K²), K(K+1)/2 inner steps;
  Knuth O(n²) via the telescoping sum ≤ 2n per diagonal; monotone row minima O(m + n log m); SMAWK O(m + n); Bellman–
  Ford O(n²) on the bipartite Euclidean graph: all correct.
- C.1 subsection: labelled "(not in the note)", is §3.10 in DP form, correct; in-place passes ≤ layered rounds is
  right (in-place marks ⊇ layer k after pass k). C.3 and D.8: nothing invented.
- Figures (rendered nd-*; nc-* read from the SVG): NFA table for 0110, CYK table for (())(), Hirschberg grid (path
  AL-TRUISTIC / ALGOR-I-THM, cost 6, h = 5), sparse LCS chain, the two 5×5 arrays, Monge crossing: all correct.
- Check scripts: nc.py checks ~45 claims, nd.py ~70, each as stated on the page; both ALL OK.
- Link lines: dfa-minimization → #c1-dfa-minimization, chomsky-normal-form → #c4-cfg-parsing (anchors resolve; texts
  accurate).

## Changes

c-dynamic-programming-for-automata.md
- Abstract: backtracking "takes Θ(|Q|ⁿ)" → "… in the worst case" (it is the worst case only).
- C.1: "This happens after at most n − 2 rounds" → "The layers stop changing after at most n − 2 rounds (so the stop
  comes by layer n − 1)". The old wording read as "the first repeated layer appears within n − 2 rounds", off by one
  (chain DFA 0→1→2, accepting 2: first repeated layer is layer 2 = n − 1). nc.py: new check that the n − 2 bound is
  attained by chain DFAs, n = 3..8.
- Sources: grammar-length error "p. 5" → "pp. 4–5 (definition p. 4, bound p. 5)"; two typos added.

d-advanced-dynamic-programming.md
- "How tight" box: "stays below 2mn + (m+n)log2 m for all 2 ≤ m,n ≤ 40, so T = O(mn) holds" inferred an asymptotic
  bound from a finite computation → states the valid induction (guess T ≤ 4mn + m + n). nd.py: two new checks (the
  bound for 0 ≤ m,n ≤ 40, and the induction step inequality for 2 ≤ m ≤ 40, 0 ≤ h ≤ n ≤ 40).
- D.3: added the English description of OptCost(i,j) (rubric).
- Sources: induction error p. 2 → p. 3; new note error p. 14 (rows → columns); three typos added.

nc.out and nd.out re-saved (ALL OK). check.py on the five pages: OK.

## Doubts

- The 2.05–2.36 cell ratio and SMAWK's 2.2(m + n) are seed-dependent measurements (reproduced by nd.py as is).
- "Knuth needs a tie rule" and "corner blocks" are imprecisions of the note rather than false statements; listed under
  errors by the writer, kept.
- History, dates and attributions (Kasami/Younger/Cocke, Hirschberg 1975, Hu–Tucker, Garsia–Wachs, SMAWK 1987, Monge
  1781, Burdyuk–Trofimov) not checked.
