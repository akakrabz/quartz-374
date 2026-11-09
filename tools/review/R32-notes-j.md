# R32 — review of Part 3, note J (Approximation Algorithms)

Source: `/home/claude/work/notes/J-approx.pdf` (25 pp., © 2018, "Status: Needs revision"), all 25 pages rendered
(110 dpi; pp. 18–19 at 200 dpi) and read; every formula, figure and pseudocode the page uses compared with the PDF.
Footnote 6 checked against Crossref (doi 10.1007/BF01185335). Checks: `tools/checks/nj.py` re-run before (ALL OK, same
output as the saved `.out`) and after my changes (110 OK, ALL OK, ~2 min; `.out` saved; the page's run counts and worst
ratios are unchanged because the new checks use their own random streams). Own brute force in a scratch script (32
checks): the set-cover family k = 2..10 with strict greedy choices, C5+chord / P5 tours with non-edges n+1 and n+2,
Filter survivor counts (3000 instances), double dual, strip triangles, 1−(1−x)^N < Nx, LP gap m = 6..12 by averaging,
greedy VC iteration bound on all graphs ≤ 6 vertices with random ties (OPT·lg|G| fails only on one-edge graphs).
`tools/check.py --only` the five pages: OK (no errors at all).

## content/4-lecture-notes/j-approximation-algorithms.md

Checked: all definitions, pseudocode (vs pp. 2, 3, 5, 6, 7, 9, 15, 17, 18), Theorems J.1–J.9 and proofs (re-derived),
ratios with hypotheses (load balancing 2, 3/2, exact 2−1/m and 4/3−1/(3m); greedy VC O(log n) and H(Δ); set cover
H(max|S|) ≤ 1+ln|X|, hitting set 1+ln|F|; DumbVertexCover 2; LP rounding 2; randomized rounding O(log n) in expectation;
TSP inapproximability with f poly-time computable; metric TSP 2 and 3/2 with the triangle inequality; Gonzalez 2 in
any metric; grid scheme 1+ε; FPTAS (1+ε) ⇔ r* ≥ s*/(1+ε) ≥ (1−ε)s*, O(n³ log n/ε)); PTAS/FPTAS examples; both tight
TSP families; C5 and K_n LP examples; pricing proof (correct, marked as not in the note); post-2018 remarks (KKO 2020
3/2 − 10^−36, marked; graphic TSP 7/5 Sebő–Vygen); all five figures (rendered light+dark: load balance, set-cover family,
tree doubling 4 shortcuts, Christofides ag/bd/ce + 1 shortcut, k-center √13 and √13/2); exam box vs algo-facts schedule
(no approximation lecture); 7-gram overlap with the note (only pseudocode, theorem statements and short phrases; Theorem
J.4 was a near-verbatim reordering → paraphrased); aliases unique site-wide (case-insensitive).

Writer's reported note errors — all confirmed (my own reading of the rendered pages):
p. 2 A[1..m]; p. 4 "maximization … as small as possible" (first of the two sentences) and "vertex color"; p. 5 "average
degree in G_i"; p. 6 OPT·lg|G| (0 iterations for one edge; only failure on all graphs ≤ 6 vertices); p. 6 set cover
O(log|F|) / hitting set O(log|X|) swapped — with the note's own naming (X ground set, F family, p. 6), greedy set cover
is H(max|S|) ≤ 1+ln|X| and the rows-and-blocks family has ratio k/2 with |F| = k+2, so O(log|F|) is false; hitting set is
the dual (ground set F), 1+ln|F|; p. 7 X* = {x* | x ∈ S}; p. 9 "x*(u) = x*(v) ≥ 1", "minimized" (max 1/4 at 1/2,
min 0), C ∪ {x}; p. 10 "exactly N·OPT~" (strictly less when some x* > 0); p. 10 swap again (standard analysis needs
O(log|X|) rounds; LP gap (m+2)/4 = Θ(|F|) rules out an LP-relative O(log|F|) — I did not find an instance where the
algorithm itself exceeds O(log|F|)·OPT, see doubts); p. 11 n+1 rules out only factors < 2 (C5+chord has a tour of 2n
= 10, P5 has OPT 10); p. 12 MST ≥ OPT; p. 12 figure middle panel labels 3/4 swapped (junction must be 3 in preorder,
right panel agrees); p. 12 "maximum-flow techniques" (the graph on O is not bipartite; blossom algorithm); p. 16
O(r*/δ²); p. 18 Filter's Y[j] ← Z[i], parameter k vs t, (1+εn/2)^i, "x ∈ S_{i−1}"; p. 18 case (2) middle step
(δ = 1/10, i = 2, x = 5, r = 20, r′ = 17: 23.7 > 23.15; final bound 24.2 still holds); p. 19 2 ln n/δ = 4n ln n/ε (note
n ln n/ε) and "=" for "≤"; p. 13 Christofides "best known" dated (and spelled "Christofedes"); p. 10 placeholder.
Refined: p. 19 ⌈log_{1+δ} i⌉ is wrong only at i = 1 (0 vs 1); for i ≥ 2 it is a valid count (by the ratio argument),
but the note's one-per-interval reason only gives ⌊log_{1+δ} i⌋ + 2.

Changes (before → after, why):
- Abstract: "not within any computable factor" → "not within any polynomial-time computable factor f(n)". Theorem J.4
  needs f poly-time computable; for f(n) = 2^(2^n) a trivial tour is a poly-time f(n)-approximation (positive integer
  lengths: input size ≥ 2^n allows Held–Karp, otherwise every length < 2^(2^n)), so "any computable" is false.
- TSP trap: "Theorem J.4 forbids every computable factor" → "unless P = NP, … every factor f(n) computable in
  polynomial time" (same reason). Summary TSP bullet: added "for any f computable in polynomial time".
- Theorem J.4 statement paraphrased (was a reordering of the note's sentence; CC BY-NC-SA); content unchanged.
- Theorem J.2 proof: "two — say k and ℓ — share a machine in every schedule" (a fixed pair) → two of the m+1 longest
  share a machine in every schedule; k, ℓ are the pair in the optimal schedule (quantifier).
- §J.4 duality: "the dual of the dual is the original system again" → "… up to renaming, provided no two elements lie in
  exactly the same sets (otherwise x* = y* and X* is smaller than X; the note claims it for every set system)". New note
  error p. 7 added to Sources (example X = {a,b}, F = {{a,b}}).
- §J.9 tight Christofides example: "strip of 2k triangles" → "2k−1" (k on bottom edges, k−1 on top edges; E−V+1 = 2k−1).
- §J.11: "so a scheme cannot run in polynomial time" → "so unless P = NP a scheme cannot …".
- Theorem J.9 proof: the survivor bound now follows from the ratio argument (p ≥ 2 survivors span a factor
  > (1+δ)^(p−1) inside [x_i, i·x_i]); the interval argument the page used only gives ⌊log_{1+δ} i⌋+2 (δ = 1, i = 3,
  x_i = 3: [3, 9] meets 3 intervals). Parenthetical on the note's count reworded accordingly ("0 for i = 1" instead of
  "one too few, already for i = 1", which suggested it is too small in general).
- Summary: greedy VC "precisely H(Δ)" → "more precisely at most H(Δ)·OPT" (an upper bound, not the exact ratio).
- Sources: p. 7 double-dual entry; p. 10 entry's evidence reworded (rounds O(log|X|); LP gap rules out an LP-relative
  O(log|F|)); new p. 16 footnote 6 "R. C. Chan" → R. C. Chang (Crossref); p. 19 entry reworded.
- nj.py: new checks — strip has 2k−1 triangles (k = 2..5); survivors: ratio > (1+δ)^(p−1), within [x_i, i x_i],
  p ≤ ⌊L⌋+1, and ≤ ⌈L⌉ for i ≥ 2 (1,500 instances, own RNG); the δ = 1, i = 3 interval example; double dual
  isomorphic iff the x* are distinct (400 systems, own RNG) and the {a,b} example; page/concept text states the TSP
  result for poly-time computable f and "strip of 2k−1". Docstring notes the additions.

## content/concepts/approximation-algorithms.md

Checked: definition (min/max forms, poly time, PTAS/FPTAS), recipe, table (every ratio and lower bound), traps,
Gonzalez example (r_1 = 2, OPT 1), Where-it-appears anchors (check.py), aliases.
Changes: table "no computable f(n) unless P = NP" → "no polynomial-time computable f(n) …"; trap "set cover only within
ln n, and general TSP within no factor at all" → "ln|X|" and "within no polynomial-time computable factor f(n) unless
P = NP" (n undefined there; overstatement as above).

## Link-line edits (np-hardness, independent-set, hamiltonian-cycle)

Only the "Where it appears" additions and the Related additions checked: anchors resolve (#j5-vertex-cover-redux,
#j8-traveling-salesman-the-bad-news), annotations correct. hamiltonian-cycle says "no approximation in general" without
"unless P = NP" — conventional shorthand, left as is. No changes.

## Doubts

- p. 10 (randomized rounding for weighted set cover): the page's correction O(log|X|) is right; that the note's
  O(log|F|) is false *for the algorithm itself* (not just for its LP-based analysis) is not shown by an explicit
  instance with a vertex LP solution. With a non-vertex optimal x* it fails (X = {0,1}^d, sets {x : x_j = a}, x* ≡ 1/d:
  rounding until covered takes about 1.8√d of the m = 2d sets against OPT 2 — simulated for d = 25 … 1600), but this x*
  is not a vertex, and I did not put it on the page.
- Graphic TSP 7/5 (Sebő–Vygen) is, to my knowledge, still the best general factor; not re-verified beyond a search.
- "Edmonds' blossom algorithm, in O(n³) time" — O(n³) is the Gabow/Lawler implementation; acceptable as stated.
