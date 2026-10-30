# Review R22 — Algorithms Chapter 12 (NP-hardness) and its concept pages (2026-10-30)

Method: read the chapter page (figure captions and SVGs), np-hardness, polynomial-time-reductions, satisfiability, and
the link lines of cook-levin-theorem and subset-sum in full; compared every section with ch12.txt and with ch12.pdf
pages rendered by pdftoppm (book pp. 385, 394 incl. a 300 dpi crop of Fig. 12.10, 396–403 incl. 250 dpi crops of
Figs 12.19–12.20); re-derived every proof by hand; wrote an independent brute-force script (scratchpad
`r22_indep.py`, own Hamiltonian-cycle search, own builders from the book's text) for the six reported book errors;
read a12.py against the page and ran it; rendered all seven figures (light/dark) and the changed parts of the page.

## 2-algorithms/12-np-hardness.md

Checked: definitions of P, NP, co-NP, NP-hard (book's ⇔ form), NP-complete, NP-easy against pp. 381–383; Cook–Levin
statement; §12.4 (TM definitions, O(T(n)^4) RAM simulation, Cook/Turing/oracle and Karp reductions, closure of NP,
UnSat, log-space remark); direction rule; CircuitSat → Sat (Fig. 12.5 gate list, 01100 wire values); the Tseitin
stages, gate CNFs, padding, the 46-clause/34-variable count of p. 390, NAND example (13 clauses, 3·2^6); 3Sat →
MaxIndSet (Fig. 12.8: 12 + 8 edges, circled set); §12.8 (three parts, asymmetry, certificate table, template, rubric
points); §12.9 relations and both reductions; 3Color gadgets against Figs 12.12–12.15 (10 edges, majority gate 2 + 3
colorings, extension rule, 31/55); VC → HC gadget (6 edges, three crossings, Fig. 12.16), chains, 4E + k vertices,
6E + (2E − V) + 2kV edges, Fig. 12.17 example (22, 52, unique cover {u, x}, 2 cycles); 3Sat → HC as printed and the
repair; §12.12 numbers, base-4 table, ⇒/⇐, k = 1 target 1706; Caveat reductor; §12.13–12.16 against pp. 404–415;
"On the exams" against algo-facts (Nov 10–19, labs 12a–13b, HW10 Nov 17, HW11 Dec 1, final only, rubric 1/2/2/2/2/1,
≤ 5, wrong direction ≤ 1, NP-completeness +1 and 1½).

Changes (before → after, why):
- §12.3 NP-easy note: added "In that broader sense, NP-hard and NP-easy together do not make a problem NP-complete:
  UnSat is both, but it is in NP only if NP = co-NP." Why: the general definition makes "NP-hard + NP-easy" broader
  than NP-complete; the old text invited the wrong identification.
- §12.9 "the final box is labeled" → "the output is labeled" (Fig. 12.10's label sits under the output arrow).
- §12.10 "With the two input colors fixed there are exactly five valid colorings (Fig. 12.14)" → "Once the two input
  colors are fixed, only two or three valid colorings remain — five in all, drawn in Fig. 12.14". Why: for fixed
  inputs there are 2 (equal) or 3 (different); 5 is the total of the two cases.
- §12.11 repaired theorem: "6kn + 4n + 6k edges" → "at most … (exactly that many when no clause repeats a literal)".
  Why: (a ∨ a ∨ b) gives coinciding clause edges (24 < 26). Check updated and one added.
- §12.12 ⇒ "In digit E the sum is k" → "The k vertex numbers contribute k·4^E"; ⇐ "digit E of the sum is |V′| =
  ⌊T/4^E⌋ = k" → "the low parts … add up to less than 4^E, so the sum divided by 4^E, rounded down, is |V′| =
  ⌊T/4^E⌋ = k". Why: k (and |V′|) can exceed 3, so "digit E" is not a base-4 digit.
- Caveat reductor: "a T larger than 4^E" → "a T of at least 4^E (whenever k ≥ 1)". Why: false for k = 0, and T = 4^E
  for E = 0, k = 1 (found by the new check).
- §12.14 and exam box: "any problem the lecture notes prove NP-hard" → "any NP-hard problem in the lecture notes"
  (algo-facts: "any in the lecture notes"; the old wording contradicted "every problem of this chapter qualifies",
  since §12.13's problems are listed without proof).
- Sources: added the p. 398 reduction diagram's "in O(V+E) time" (H has 2kV cover edges; the text's O(V²) is right).

## concepts/np-hardness.md
- "would imply P = NP — equivalently, every problem in NP reduces to Π" → "— formally (§12.4), every problem …".
  Why: not literally equivalent (if P ≠ NP the implication form holds vacuously for every problem outside P).
- Trap: "co-NP problems such as UnSat … are NP-hard without being in NP" → "the co-NP problem UnSat is NP-hard but
  in NP only if NP = co-NP" (not known to be outside NP).

## concepts/polynomial-time-reductions.md, concepts/satisfiability.md
No changes. Definitions, template, traps, 5-cycle complement 0 2 4 1 3, Tseitin display, 9 clauses / 7 variables /
48 of 128 all correct.

## concepts/cook-levin-theorem.md, concepts/subset-sum.md (link lines only)
- cook-levin: "§12.5 (the first reductions, CircuitSat → Sat and → 3Sat)" → "§12.5–§12.6 (…)" with a link to
  #126-3sat-from-circuitsat (→ 3Sat is §12.6). subset-sum link line correct.

## tools/checks/a12.py
Read: the reductions are implemented as on the page and tested by brute force (YES ↦ YES, NO ↦ NO, certificates both
ways); page-text checks match. Added: repeated-literal edge count; the page's VC → HC handling (isolated vertices
removed, k ≥ n′ answered by a fixed Hamiltonian graph) correct on 1026 random (G, k); set reading of SubsetSum fails
(edge uv, k = 2); T ≥ 4^E for k ≥ 1. Re-run: ALL OK, saved to a12.out. check.py on all six prefixes: OK.

## Book errors (verified independently)
1. CONFIRMED, pp. 400–401: 3Sat → DirectedHamCycle is wrong. Rows are joined end-to-end by (i,0|2k) → (i+1,0|2k)
   (read in the PDF, directed, cyclic). For the 8 sign patterns on a, b, c with (ā ∨ b ∨ c) last (unsatisfiable),
   the cycle of a = T, b = c = F with (1,2k) → [8] → (2,2k) replacing the connector is Hamiltonian — explicit check in
   both readings (59 and 56 vertices). Also smaller non-3CNF examples exist, e.g. (ā ∨ b̄)(b)(b̄ ∨ a). Text says "2k
   vertices (i,0),…,(i,2k)" (2k+1 labels); Figs 12.19–12.20 draw 8 = 2k per row, ends at clause positions.
   Repair verified: proof re-derived step by step (incl. clauses containing x and x̄, j = 1 and j = k, n = 1);
   exhaustive over every CNF with ≤ 2 variables, ≤ 2 clauses of 1–3 literals (repeats allowed): 1280 formulas, 0
   errors; the 8-clause formula's repaired graph (86 vertices) has no Hamiltonian cycle.
2. CONFIRMED, pp. 398–400: VC → HC fails exactly when k > #non-isolated vertices (and for E = ∅); all 331 failures
   in an exhaustive run (n ≤ 5, ≤ 4 edges) are YES ↦ no cycle in those cases. "O(V+E)" is in the unnumbered
   reduction diagram on p. 398 (not Fig. 12.17); wrong, since H has 2kV cover edges (Θ(V²) for a matching with
   k = V/2); text on p. 400 says O(V²).
3. CONFIRMED, p. 394: Fig. 12.10's output label reads "size of largest independent set in Ḡ"; should be "in G".
4. CONFIRMED, p. 403: the ⇐ proof writes t (twice: "= t", "the ith digit of t is 2") for T.
5. CONFIRMED as an overstatement, p. 385: "NP-hard with respect to Karp reductions only if P=NP … UnSat". In fact
   UnSat is Karp-NP-hard iff NP = co-NP; "only if P = NP" would need NP = co-NP ⇒ P = NP, which is open. Not
   provably false, just not known (the book's own previous sentence names the right condition).
6. CONFIRMED, p. 402: "Given a set X"; the reduction can output equal numbers (endpoints of an isolated edge;
   isolated vertices), and read as a set it answers wrongly (28 of the exhaustive cases n ≤ 4; e.g. edge uv, k = 2).

## Coordinator note (other Ch 12 reviewer): §12.10 "exactly five valid colorings"
Agreed and already fixed (see §12.10 change above). Also verified their Fig. 12.14 remark: the 24 half-gadget colorings
form 4 classes up to permuting colors; the book draws 5 because its two equal-input drawings differ only by swapping
the two other colors (caption "up to permutations of the colors" is loose; minor). The page's "five in all" means
2 + 3 with one equal and one different input pair fixed, which is what the figure draws — correct. Check added to
a12.py. Clause-gadget vertex names (u, v, w, y, z on concepts/graph-coloring vs p, q, r, s, t here): left as is.

## Doubts
- The rubric's exact wording ("in the lecture notes" vs "proved in the lecture notes") is not available locally;
  the page now follows algo-facts. The toolkit page (06-how-exams-are-graded §14) says "any problem the lecture notes
  prove NP-hard" — not my page.
- "the book also calls membership in NP being NP-easy" is the book's parenthetical usage on p. 383; kept.
