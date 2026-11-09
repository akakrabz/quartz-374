# Review R31 — Part 3, Appendix I (Proof by induction) + concept strong-induction (2026-11-08)

Pages: `content/4-lecture-notes/98-proof-by-induction.md`, `content/concepts/strong-induction.md`, and the link-line
edit in `content/concepts/induction-on-strings.md` (checked only); check `tools/checks/n98.py`; figures
`tools/figs_n98.py`.

Method: read both pages in full (figure captions included) and the whole note text; rendered 98-induction.pdf with
pdftoppm (110 dpi; pp. 8 and 29 also at 200/300 dpi) and compared every theorem, proof, pseudocode, figure caption and
exercise example on pp. 1–30 with the page. Re-derived by hand: all ten theorems' proofs (logical shape, quantifiers,
which cases use the hypothesis), the stamp threshold, the baby-step loop indices (n = 8 trace), Theorem 9's odd case,
the three tree proofs and the leaf walk, the build-up counterexample (base K2, step keeps connectivity and min degree,
2K2 not buildable), Ex 5/6/7/19 sums, α-power table, Ex 21 first terms, Ex 22 counterexample (x^(2 lg π), exponent
3.303; f free on (1/√2, 1] so even Θ(x^(2 lg π)) needs bounds there), Ex 23's proof. Ran n98.py (ALL OK before and
after; 134 → 136 checks); it checks far more than 8–12 key claims, each as stated on the page (same algorithms, same
numbers). License: 6/7-gram overlap scan against the note text finds theorem statements, definitions, the boilerplate
itself and quoted note errors; one 6-word clause ("the case analysis is obviously exhaustive") reworded.
Aliases of concepts/strong-induction: none collides case-insensitively with any alias site-wide.

## Note errors reported by the writer — verdicts (against the PDF)

- p. 9, Theorem 3 proof cites "Theorem 2" for the prime divisor: **confirmed** (Theorem 1).
- pp. 13–14, captions "Top-down inductive proof of Theorem 4" / "Second proof of Theorem 4": **confirmed** (Theorem 5).
- p. 17, baby-step invariant proofs assume "for any j ≤ i": **confirmed** (circular; j < i). The i-th iteration
  "replaces two copies of 2^i with 2^(i+1)": **confirmed** off by one with the note's own numbering (after the i-th
  iteration, i = 0 = before the loop): iteration i merges 2^(i−1); second proof likewise says "two copies of 2^i"
  just before iteration i.
- p. 18, Theorem 8 hypothesis "F_k is even iff n is divisible by 3": **confirmed** (k).
- p. 19, "a proper subtree is any tree except T itself": **confirmed** (any subtree of T other than T; as printed the
  "smaller" relation is not well-founded).
- p. 20, "Thus, T has at least two connected components": **confirmed** (T \ e); "proper subtree of G": **confirmed**
  (of T; for d = 1, G_1 = G is not a proper subtree of G).
- p. 22, Ex 6: (−2)^6+(−2)^5+(−2)^4+(−2)^0 = 49: **confirmed**; 42 = (−2)^6+…+(−2)^1 (negabinary 1111110).
- p. 23, Ex 7(d): F−9+F−7+F−5+F−3+F−1 = 55: **confirmed**; 54 = F−9+F−7+F−5+F−3.
- p. 29, Ex 22 false as printed: **confirmed** (f(x) = x^(2 lg π) meets both conditions, not O(x)).
- p. 29, Ex 23: open interval defined as {t | a ≤ t < z}: **confirmed**; [a, b] → [a, z]: **confirmed**;
  [a, u] ∈ S → ⊆: **confirmed**. "S̄ is bounded" → T: **not an error** — S̄ (undefined, but used consistently)
  is the complement of S in [a, z], i.e. T. Third case "ℓ ∈ S" → ℓ ∉ S: **refuted** — the PDF prints ℓ ∈ S̄
  (bar visible at 300 dpi; the .txt drops it), which is correct.
- Typos: p. 3 "than", p. 6 snark sentence and "An all cases", p. 10 "In both cases" after three cases and "which
  empty space", p. 14 "triomono", p. 8 Scheme lists unquoted: **confirmed**. p. 8 C program: **confirmed**, but it is
  literal LaTeX source `$n$` in the code, not a "LaTeX-typeset variable" (reworded).

## New note error found

- p. 4 (terse proof of Theorem 1: "n has a proper divisor; call it d … d has a prime divisor") and p. 10 (Theorem 3,
  second proof: "Let d be any proper divisor of n … both d and m are … smaller than n"): by the note's own definition
  (p. 1) 1 is a proper divisor, and d = 1 breaks both (1 has no prime divisor / is outside 1 < k < n; m = n). Must be
  a proper divisor d > 1. The page already used d > 1 silently; now says so in §4 and in Sources; 2 checks added.

## Changes — 98-proof-by-induction.md

1. §1, last paragraph: "provided the induction hypothesis is written out and the case analysis is obviously
   exhaustive" → "as long as the hypothesis is stated explicitly and the cases visibly cover every n" (near-copy of
   the note's sentence).
2. §4, "Split anywhere": added "(the note says "any proper divisor", but by its own definition 1 is one, and d = 1
   gives m = n)".
3. §6, Tile pseudocode: returned ∅ in the base case but nothing in the recursive case (T was computed and dropped).
   Now a procedure that places tiles: "return ∅" → "return ⟨⟨nothing left to cover⟩⟩", "T ← a triomino on …" →
   "place a triomino T on …". Recurrence and call count unchanged.
4. §11 trap: "The same pattern "proves" false claims" + "(this one is not in the note)" — marks the addition.
5. Sources: "unnumbered sections 1–11" → "sections numbered 1–11 without a chapter prefix" (the PDF numbers them);
   triomino count added to the "Original here" list; p. 4/p. 10 proper-divisor error added; Ex 23 entry corrected
   (removed the refuted third-case claim; S̄ described as undefined notation for T, not an error); p. 8 C typo
   reworded (no dollar signs in the page: inside backticks they were rendered as math and garbled the sentence).
6. Figure n98-triomino-topdown caption (figs_n98.py): "minus the black square" → "minus the solid square" (the hole
   is currentColor, white in dark mode). Regenerated; the other two figures byte-identical; assembled this page only.

## Changes — strong-induction.md

- Where it appears: added the link [[0-toolkit/02-proof-templates#3-induction-on-regular-expressions|structural
  induction on regular expressions]] (five cases). Reason: the page claims the alias "structural induction", which
  in Part 1 means the five-case induction on regular expressions; with the link the alias leads there. All eight
  aliases kept: unique site-wide (case-insensitive), and each term is defined/explained on the page.

## Checked, no change

- Exam box: rubric 1/2/2/1/2/2 matches 06-how-exams-are-graded §4, book-facts and 02-proof-templates §1; each
  boilerplate line mapped to the right rubric line; consistent with the induction-on-strings template (arbitrary
  string, hypothesis for every shorter string, cases covering all strings). Midterm 2 "proofs only when asked" matches
  0-toolkit/08.
- Concept page: key box, well-ordering, weak/structural induction, template, five traps (incl. the integers-are-not-
  well-founded trap), MergeSort example f(n) = n − 1 and "for n ≥ 4 neither half is n − 1" — all correct and checked.
- induction-on-strings.md: only the Where-it-appears sentence and the Related line changed (allowed by SPEC-notes §1);
  Practice line still directly before Related.
- All three figures: tilings valid (checked by the script), captions match drawings.
- `python3 tools/check.py … --only 4-lecture-notes/98-proof-by-induction,concepts/strong-induction,concepts/induction-on-strings`: OK.
- Preview (light) of every changed part: fine; Tile header comment kept short to avoid horizontal scroll.

## Doubts

- Inline additions inside the note's sections (Postage/Tile pseudocode, n = 8 trace, threshold remark, triomino count
  in the Theorem 5 box) are marked only in Sources, as on earlier Part 3 pages.
- The italic "quote" of the non-proof in the §11 trap is a paraphrase, not the note's wording.
