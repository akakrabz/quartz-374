# Review R24 — Lecture note 99 (Appendix II, Solving Recurrences) and concepts/linear-recurrences (2026-11-08)

Method: read both pages in full (callouts, tables, figure caption) and the link lines added to concepts/master-theorem
and concepts/recursion-trees; read 99-recurrences.txt in full and rendered every page with a formula I checked
(pdftoppm, pp. 3, 4, 8–14, 16, 17, 19); re-derived every solution, level sum, fitted constant and proof step by hand;
compared with master-theorem, recursion-trees, 0-toolkit/08-review-algorithms, 09-midterm-2-cheat-sheet,
06-how-exams-are-graded, 01-recursion-exercises §1.8(p), 02-backtracking §2.2/2.5/2.8, 03-dynamic-programming §3.1;
read n99.py against the page and ran it (116 checks, ALL OK before my changes).

## Note errors claimed by the writer — verdicts

- p. 12 / p. 17, coefficient 3 → 5 and annihilator E³−3E²+8E−4 → E³−5E²+8E−4: **confirmed**. Printed recurrence gives
  T(3..6) = 4, 12, 4, −68 vs (n−3)2ⁿ+4 = 4, 20, 68, 196; x³−3x²+8x−4 has roots ≈ 0.612 and a complex pair of modulus
  ≈ 2.557; the note's own factorization (E−2)²(E−1) expands to E³−5E²+8E−4. The p. 12 check's brackets evaluate to
  0, −1, −8 (its constant bracket (2−8+4) is a second misprint, 3 under the printed recurrence, 5 corrected).
- p. 17, 2ⁿ−n² example: **confirmed**. α = 2/3 forced ((E²−E−2)(αn2ⁿ) = 6α2ⁿ = E²2ⁿ = 4·2ⁿ), γ, δ, ε = 1/2, 5/2, 4
  forced; only β, η depend on T(0), T(1). Footnote 2's family leaves residue n² − 8, not 2ⁿ − n²: not a solution.
  "E²(2ⁿ+n²)" for E²(2ⁿ−n²): typo, confirmed.
- p. 14 row (αn+β)a^b: **confirmed** (rendered page).
- p. 13 "2f(n−1)" for 2f(n+1): **confirmed**.
- p. 16 −γ/φ̂ → +γ/φ̂: **confirmed** (α/φ − 1 + γ/φ̂ = 0; with −γ/φ̂ it is 0.342); the stated solution is right.
- p. 8 lower limit j = i → j = 1 (three sums): **confirmed**. p. 9 Σ_{i=1}^∞ j/2^j index: **confirmed**.
- p. 9 "overestimate" for the lower bound: **confirmed**.
- p. 9 missing +n / +1 in n log_{4/3} n, log_{4/3} n: **confirmed only as an off-by-one in the argument** (extending to
  the deepest leaf counts log_{4/3} n + 1 levels). With T = 0 below size 1 the printed bounds are false only for some
  n < 2 (e.g. n = 1) and hold for all n ≥ 2 (checked exactly at the breakpoints in [2, 8], induction with margin
  −0.955 beyond). Page and Sources reworded to say so.
- p. 10 a·f(b/n) for a·f(n/b), three times: **confirmed**.
- p. 10 Akra–Bazzi 0 < c: **confirmed as an inconsistency** — the hypothesis is sufficient but excludes the note's own
  f = 1 examples (randomized search trees, ham-sandwich); constant f is fine for the theorem.
- p. 11 O(n log n): **refuted as an error** — true, just weaker than the Θ the formula gives. Moved in Sources to
  "Not an error"; the in-text remark already said only that the formula gives Θ.
- p. 19 footnote 3 t(n) → t(k): **confirmed**. Footnote's math (λ = log_{3/2} 3 = 2.709511, double root 3/2, no other
  positive root) is right.
- Typos p. 3 "a > 0" (also "the coefficient a", same page), p. 4 "conforming", p. 9 "modes", p. 16 "when i is an
  integer": **confirmed**.
- Not reported by the writer, added to Sources: p. 19 quicksort derivation Σ_{k=0} T(j) (index k, summand j), twice.

## Writer's additions — verified

Exact forms (§3 table rows 1–6, n(lg lg n + 1), nH_{lg n}, 2n² − n lg n − 2n, 4n − 3, 3n^{lg 3} − 2n,
2(n+1)Hₙ − 3n, T(2^k) = F_{k+3} − 1, H(n) = F(n+3) − 1) re-derived by hand and in n99.py. Largest-root shortcut: true
(Descartes → one positive root r > 1; lower bound by induction from positive base cases; all roots of modulus r are
simple, so O(rⁿ); the sketch's A rⁿ − q(n) works with q = C(n+M)^d). "Choosing a method" rows and answers correct and
marked "Not in the note"; Sources lists the additions. Master Theorem box matches the note and concepts/master-theorem;
Akra–Bazzi statement matches master-theorem; exam advice consistent with 08-review-algorithms (Θ only unless
prove/justify; write the case).

## Changes

1. §5.2 definition: "An annihilator of a function f is any nonzero operator that transforms f into the zero function"
   (near-verbatim copy of the note) and "Every function built from polynomials and exponentials has a unique minimal
   annihilator" (imprecise: 2^{n²} is built from them and has none) → "An operator X annihilates f if Xf is the zero
   function; a nonzero such X is an annihilator of f. Every sum Σ p_i(n) a_iⁿ (distinct a_i, nonzero p_i) has a
   unique minimal annihilator up to a constant factor, Π (E − a_i)^{deg p_i + 1}." New check line.
2. §3, 4T(n/2) + n lg n: "Not quite a geometric series, but still dominated by its largest term" (near-copy) →
   "The sum is not geometric, yet it is within a constant factor of its largest term."
3. §3, quicksort split: "It also drops the +1 in the upper bound." → adds that the printed bound is false only for
   some n < 2 and holds for n ≥ 2. New check line.
4. "Where this fits" and the exam box: "three recurrences" stated as fact about the Nov 9 exam → "recurrences to
   solve (three in each Fall 2025 version)", as 06/08 support.
5. Sources: p. 9 +n/+1 and p. 10 0 < c reworded as above; p. 11 moved to "Not an error"; p. 3 second "a" and the
   p. 19 Σ index typo added; the "Checked by" sentence no longer claims every listed error is machine-checked.
6. tools/checks/n99.py: +2 checks (printed p. 9 bounds hold for all n ≥ 2; minimal annihilator). 118 checks, ALL OK;
   n99.out saved. check.py on the four pages: OK. Previewed the changed parts in light mode.

No change to concepts/linear-recurrences (all claims verified: trap examples, worked example, shortcut, links to
§2.2/2.5/2.8/3.1/3.2) or to the link lines in master-theorem / recursion-trees (anchors resolve, statements right).

## Doubts

- concepts/linear-recurrences "Growth: the term with the largest |r|…" is only an upper-bound rule when several roots
  share the largest modulus (2ⁿ + (−2)ⁿ); the shortcut's hypotheses avoid this. Left as is.
- "three in each Fall 2025 version" rests on 06/08's description of the Fall 2025 exams, not on book-facts.md.
