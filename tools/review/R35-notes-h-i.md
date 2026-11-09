# R35 — review of Part 3, notes H (Linear Programming) and I (Linear Programming Algorithms)

Sources: `/home/claude/work/notes/H-lp.pdf` (21 pp., © 2018, "Status: Text beta. Needs figures.") and `I-simplex.pdf`
(15 pp., © 2018, "Status: Half-finished."; §I.4 "needs revision", §I.5 "needs careful revision"); both .txt read in
full; pages rendered (110 dpi; H p. 10 at 160 dpi) and every reported note error confirmed on the PNG: H pp. 2, 3, 5,
7, 8, 11, 12, 14, 16, 17, 19; I pp. 5, 7, 8, 9, 10, 11. Own derivations: the Figure H.4 table (both halves, from
min c·x s.t. Ax ≥ b, x ≥ 0 ↔ max y·b s.t. yA ≤ c, y ≥ 0), the max-flow dual (S(v) = −p_v with conservation written
out − in), the shortest-path uniqueness criterion (two optimal potentials δ(s,·) and δ(s,t) − δ(·,t) differ exactly
off shortest s–t paths), the network-simplex slack updates via potentials (primal: shift V∖S by slack(e_in); dual:
e_in must go V∖S → S, shift by −slack(e_in), cost change |flow(e_out)|·slack(e_in)), the Seidel recurrences
(T(n,1) = H_n, all calls n + H_n − 1, a_δ = Σ δ!/k! bound), the Vanderbei dictionary run (16/3, 74/13, 14), the
network-pivot figure (21 → 19 → 17, slacks −2/+1, +2/−1, +2/+1) and the simplex-paths figure (0→6→13→15, 35→20→15).
Checks: `nh.py` and `ni.py` re-run before changes (identical to the saved `.out`), `nh.py` after (78 OK, ALL OK,
earlier checks byte-identical; `.out` saved), `ni.py` after (unchanged, ALL OK). 7-gram overlap with the note texts:
only pseudocode, quoted erroneous phrases and short definitional phrases; one near-paraphrase reworded (below).
Aliases unique site-wide (case-insensitive). `tools/check.py --only` the six pages: OK (no errors).

## content/4-lecture-notes/h-linear-programming.md

Checked: definitions and forms (canonical, slack, conversion rules), geometry, Figure H.2 example and Farkas
certificate, all four LPs of §H.3 and their claims (feasibility, boundedness, uniqueness, integrality, |D_v| solution),
the fractional min-cut example, the canonical dual and negative-transpose form, Figure H.4 table vs own derivation,
recipe, shortest-path and max-flow dualizations, fundamental/weak/strong duality statements, Gordan, the outcome table,
Vanderbei example and its optimum, proof sketch (warm-up and general case), the cube counterexample, forces figure,
complementary slackness definition/theorem/counterexamples (x = 0 and (1, 1/4, 5/4) with y = (1, 3)), strict CS and the
s→a→t example, traps, summary, exam box (notes-facts: not assigned, CS 473), all four figures' numbers.

Writer's note errors — confirmed: p. 2 Ax ≥ b; p. 3 x_i^± and "upper bound … ≥ / lower bound … ≤" swapped; p. 5 witness
(dist = 0 on reachable vertices violates a negative reachable edge; ∞ is no value anyway); p. 6 uniqueness condition
sufficient, not necessary (page's graph: paths 6, 8, 8, 9, 11, unique optimum); p. 7 D_v = |v|; p. 11 min-max without
range (refined: over real vectors it is not false but empty, both sides 0); p. 12 "all these implications are
equivalences" (fails for unbounded ⇐ dual infeasible); p. 14 (a) does not give uniqueness for d ≥ 3 (unit cube,
c = (1,1,0)); p. 16 b, c for b_i, c_j (also p. 17 in the strict conditions); p. 16 CS theorem lists c·x = yAx and
yAx = y·b as separately equivalent; p. 8 f ∈ E^ℝ; p. 19 black edges.

Changes (before → after, why):
- H.3 trap: "Minimizing dist(t) would be unbounded below." → unbounded below unless t can reach s, then the minimum is
  −δ(t,s). False as stated: constraints along a t→s path give dist(t) ≥ −δ(t,s) (s↔t with length 1: min −1).
- H.5: "(…over all real vectors both sides are infinite.)" → both sides are 0 (inner optimum infinite unless xA = 0,
  resp. Ay = 0), so the statement is empty. Wrong as written (x = 0 gives max_y 0 = 0).
- H.8 definition box: "(… b and c, p. 16.)" → "pp. 16–17"; Sources entry extended to the strict conditions.
- Sources: p. 8 "f ∈ E ℝ" (pdftotext artifact) → as printed "f ∈ E^ℝ"; p. 11 entry notes it reads 0 = 0 over real
  vectors; checked-by sentence mentions the min dist(t) check.
- nh.py: new checks (own random streams): min dist(t) = −δ(t,s) or unbounded (400 graphs + the s↔t example); min-max
  over real vectors is 0 = 0 (100 matrices); page/concept text for the three edits. Docstring notes the additions.

Doubts (not changed): p. 12 "both infeasible … only if both LPs are degenerate" is true under note I's non-degeneracy
(every d normals independent; proof: y ≥ 0, yA ≥ 0, yb < 0 and x ≥ 0, Ax ≤ 0, cx > 0 force a singular square minor of
A on supp(y) × supp(x)), but false under note H's own (a)+(b) (max 2x1 − x2 s.t. x1 − x2 ≤ 1, −x1 + x2 ≤ −2: parallel
rows, satisfies (a) and (b), primal and dual infeasible). The page's table says "possible (degenerate LPs)" without
fixing the definition — acceptable. Page is ~6,300 words without figures (cap "about 6,000"); not shortened.

## content/4-lecture-notes/i-linear-programming-algorithms.md

Checked: non-degeneracy, bases/location/neighbors (C(n+d,d), dn), local optimality = complementary dual basis
feasible (own proof via labels), basis facts, both simplex pseudocodes vs the note, correctness and pivot bounds,
initial-basis observations and the p. 5 counterexample (c = (1,2), normals (1,0), (1,1)), Figures I.4/I.5 code,
transshipment LP and incidence matrix, non-degeneracy, Lemma I.1 and proof sketch, slack = fundamental-cycle cost =
reduced cost (G.3 convention cost + π(u) − π(v)), feasibility/local-optimality criteria, both pivots (direction of
e_in, slack updates, cost changes), Seidel code vs p. 11, correctness, boundedness caveat, recurrence and induction,
base-case-call reading, history (Hirsch/Santos 43-dim, 86 facets, 44), Beyond the note (marked; Klee–Minty in
Chvátal's form, 2^d − 1 with Dantzig's rule), §I.4/§I.5 only summarized and marked, both figures rendered.

Writer's note errors — confirmed: p. 5 positive inner products; p. 7 "maximize"; p. 8 incidence matrix rows/columns;
p. 8 "non-negative on every free edge"; p. 10 cost decreases "by" a negative product (sign slip); p. 10 dual pivot
needs e_in from V∖S into S, slack update reversed; p. 10 single bounding halfspace can be sampled (bounding constraints
must be kept out of the random choices; confirmed as an insufficient remedy rather than a false formula); p. 11
SeidelLP(H, B ∪ h) → SeidelLP(H∖h, B ∪ ∂h); p. 11 T counts base-case calls (d = 1: H_n vs n + H_n − 1); p. 12
Exercise 1(a) false for unbounded regions ({x ≥ 0, x1 − x2 ≤ 1}, c generic: (0,0) has one feasible neighbor); typos
Fransisco, feasbile, initializzation. Refuted as an error: p. 10 "saturated" — in residual terms the reversed edge
of e_out is saturated; the note's own bullet says "empty"; wording only.

Changes:
- I.2 pivot-rules sentence reworded (was a near-paraphrase of the note's sentence, CC BY-NC-SA); content unchanged.
- Sources: "saturated" entry moved from error to wording remark (reason above).
- ni.py: no change needed (no checked claim changed); re-run, output identical.

Doubts: footnote 1's "in 2010" for Friedmann–Hansen–Zwick (the RandomFacet lower bound appeared at STOC 2011) is copied
from the note; listed as not machine-checked.

## content/concepts/linear-programming.md

Checked: definition box, recipe (both halves), traps, example (vertices, dual, CS solve), anchors, aliases.
Change: "maxflow = mincut is strong duality" → "… strong duality plus the fact that the cut LP has a 0/1 optimal
solution" (strong duality alone only equates max flow with the LP minimum of the cut LP). nh.py text check added.

## content/concepts/simplex-algorithm.md

Checked: definition, why it works, dictionary recipe (Dantzig/Bland), traps (basis ↔ non-basic variables,
counterexample, Klee–Minty, Bland), the worked dictionary example (every ratio, coefficient and tight set), anchors,
aliases. No changes.

## Link-line edits (maximum-flow, shortest-paths)

Only the added "Where it appears" note-H links and the `Related: … [[concepts/linear-programming]]` additions checked:
anchors resolve (#h3-examples), annotations correct. No changes.
