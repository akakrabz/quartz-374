# Review R17 — Algorithms Chapter 9 (all-pairs shortest paths), its concept pages and exercises (2026-10-25)

Method: read every page in full (figure captions and both figure scripts included); compared sections, pseudocode,
recurrences and claims with the book (ch09.txt, and pp. 312–316, 318–319 and 324 of ch09.pdf rendered with pdftoppm,
book p. = PDF p. + 308); re-derived by hand the running example (all 16 distances and predecessors, its three simple
cycles), Johnson's prices −3, −5, −1, 0 and the six reduced weights, Dijkstra from 3 on w′ and the conversion back,
W² and W⁴, all four Floyd–Warshall phases (the improved entries of each), the wrong-loop-order run (entry (2, 1)
stays ∞), the negative-cycle and shortest-cycle runs of the concept example, both concept examples, the Leyzorek
pointer-cycle trace, the zero-cycle figure (prices −2, 0, −3, −4, −2, −2, nine reduced weights, the four simple
cycles), the elimination figure and the dag-blocks figure; re-proved every lemma and solution before reading it
(reweighting telescoping, nonnegativity, the new vertex, the in-place safety arguments for AllPairsBellmanFord,
Leyzorek and Floyd–Warshall, the negative-cycle detection lemma also with negative cycles present, 9.1(a) pair
tie-break and its no-pointer-cycle argument, 9.1(b) invariants (i)/(ii), 9.2 lemma and both constructions, 9.3(a)
pointer-walk argument with V+1 rounds, 9.3(c) pre-phase test, 9.4–9.10). Independent code of my own (not the check
scripts): Exercise 9.11 printed vs fixed code on 400 random graphs with n up to 16 (printed code wrong on all 400;
printed call order alone wrong on 165; the Park–Penner–Prasanna order right on all), the 2→4→3→1 counterexample,
the Leyzorek pointer cycle, the u-v-r loop-order counterexample. Read both check scripts against the pages and ran
them; ran tools/check.py on the four prefixes. Screenshotted all seven figures (light and dark) to confirm the drawn
edges, directions and colors match the captions; no figure changed, so no page screenshot.

## 2-algorithms/09-all-pairs-shortest-paths.md

Checked: definition box (the "otherwise" for dist(u, u) correctly resolves the book's overlap between "u on a
negative cycle" and "u reaches a negative cycle that reaches u"); §9.2 table, the O(VE) = O(V² + VE) convention,
array/Fibonacci-heap Dijkstra bounds; Figure 9.1 numbers (8/7 → 12/13) and the +3 example (7 vs 4); prices
definition, telescoping key box and proof; "distances are good prices" (tight edges = edges on shortest paths from
s); the new vertex (no distance changes, π(v) = min{0, minᵤ dist(u, v)}); JohnsonAPSP = Fig. 9.2; time bullets;
Johnson example and figure; traps (consistent with §8.6 on NonnegativeDijkstra/Dijkstra); Shimbel function,
recurrence, memo/order/time in the DP-rubric format, pseudocode with the v ≠ u fix; AllPairsBellmanFord = p. 314 and
its in-place invariant; Fischer–Meyer function (powers of 2, 2^⌈lg V⌉ ∈ [V−1, 2V)), recurrence, memo O(V² log V),
order, time, FischerMeyerAPSP and LeyzorekAPSP = pp. 315–316, the in-place argument for Leyzorek; min-plus
definition, associativity/identity, the operation table, W^⊗ℓ = dist(·, ·, ℓ), exact-ℓ variant, Shimbel = iterated
products, Fischer–Meyer = repeated squaring, the Strassen/Seidel/subcubic paragraph against p. 317; §9.8 definitions,
recurrence and its proof (both directions), KleeneAPSP and FloydWarshall = p. 319, the in-place key box, the phase
figure, history, the loop-order trap, the negative-cycle lemma and proof (the "dist ≤ every simple path, cycles
included" induction holds with negative cycles present), predecessors, Warshall, shortest-cycle tip, the
at-a-glance table, Summary, exam box against the graph-reduction and DP rubrics; all anchors into Chapters 1, 4
(Part 1), 6 and 8 point at the right sections and agree with those pages.

Change:
1. §9.5, after ShimbelAPSP. Before: "As printed in the book, the middle loop skips $v = u$". After: "… the loop over
   $v$ skips $v = u$". Why: with the loops ℓ, u, v the "middle" loop reads as the loop over u; the faulty loop is the
   one over v (the page's own comment marks it).

## concepts/all-pairs-shortest-paths.md

Checked: definition and table, why-these-bounds, recipe, traps, example (rows (0, 2, 1), (∞, 0, −1), (∞, 3, 0);
W^⊗2 = distances), anchors.
Change:
2. Trap 2. Before: "…without that assumption their output is meaningless (except Floyd–Warshall's diagonal)."
   After: "… (except the diagonal of Floyd–Warshall or of the repeated-squaring algorithms: some entry is negative
   iff there is a negative cycle)." Why: the old wording implies Leyzorek's diagonal is meaningless, but it detects
   negative cycles exactly like Floyd–Warshall's (every simple cycle has ≤ V ≤ 2^⌈lg V⌉ edges), and the exercises
   page relies on that in 9.2(b) and 9.3(b). New check `sq_detect` in a09.py (Fischer–Meyer and Leyzorek diagonal on
   the 1500 mixed graphs) and a page-text check.

## concepts/johnsons-algorithm.md, concepts/floyd-warshall.md

Checked: key boxes, why-it-works, recipes, templates (DP rubric), traps ("r must be outer … paths of three or more
edges": two-edge paths are always found in one u-v-r pass, so "three" is right), both examples recomputed by hand
(Johnson: prices 0, −2, −1, reduced 0, 0, 4, 1, dist(a, c) = −1, dist(c, b) = 0; Floyd–Warshall: the three phases,
final rows, the w(3→1) = −3 run with diagonal −1, −1, −2 and (3, 1) = −4, the ∞-diagonal run 4, 4, 4); aliases
unique site-wide. No changes.

## 2-algorithms/09-all-pairs-shortest-paths-exercises.md

Checked every statement against pp. 320–325 (paraphrases faithful; the added "no negative cycles" in 9.5 and 9.8 is
labelled) and every solution: 9.1(a) counterexample trace, the pair fix and its three-step proof; 9.1(b) both
invariants in all four cases; 9.2 lemma, (a) components/Bellman–Ford/two searches per source, (b)/(c) marking pass
and the in-place remark; 9.3(a) invariant, negative pointer cycles, the walk never reaching s; 9.3(b)/(c) and the
Floyd–Warshall-only variant (diagonal stays 0 until the first successful test; simple cycle by the shared-vertex
split; converse); 9.4 (a), (b) and the example; 9.5 construction (z_i→x weight −π(x)), formula, Fibonacci-heap bound
O(VE + kV log V), the trap; 9.6 graph, (a)–(c), the multiplicative form; 9.7 s = p by the triangle inequality, the
2·min(|P|, |F|) Dijkstras; 9.8 (a)–(c) and the Floyd–Warshall/state-elimination remark; 9.9; 9.10 (a)–(d), the
recursion tree for T(n) = 2T(n/2) + O(n^ω); the 9.11 note.
Change:
3. 9.2(a) step 1. Before: "Each $x\in B$ lies on a negative closed walk (go from $x$ to the negative cycle, around it,
   and back inside $C$)". After: "… around it often enough, and back inside $C$". Why: one turn around the cycle need
   not make the closed walk negative (the detour to and from the cycle can be longer than the cycle is negative).

## Check scripts

a09.py: transcriptions match the page's pseudocode (Johnson, Shimbel with as_printed flag, AllPairsBellmanFord,
Fischer–Meyer, Leyzorek, min-plus, Kleene, FloydWarshall with order/pred/diag options, wrong order, Warshall); the
running example and concept examples equal my re-derivations; figure parsing covers edges, weights, matrices and
highlights. Added `sq_detect` and the concept-trap text check. 93 OK (91 before), ALL OK (a09.out saved).
a09x.py: implementations match the page (Leyzorek/FW with pred, pair versions, JohnsonNeg, marking pass,
Bellman–Ford cycle extraction, FW pre-phase test, zero subgraphs, class distances and the wrong variant, exact
arbitrage, Morty over all s, elimination, boolean products, the closures, RecursiveAPSP as printed and fixed). It did
not read the page at all; added a final block that asserts the page states the checked numbers (9.1(a) trace, 9.2(a)
wording, 9.4 example, 9.5 construction, 9.6 example, 9.11 counterexample) and that the zero, pointer-cycle and
elimination figures carry the computed labels. 56 OK (52 before), ALL OK (a09x.out saved; about 5 minutes).
tools/check.py --only on the four prefixes: OK.

## Book errata (confirmed on the rendered pages and by code)

| page | as printed | should be |
|---|---|---|
| 312 | Johnson: "O(V + E) time doing other bookkeeping" | the final conversion loop is Θ(V²) (total O(VE log V) unaffected when E ≥ V) |
| 314 | ShimbelAPSP: "for all vertices v ≠ u" | all v (else dist[u, u, ℓ] is never assigned for ℓ ≥ 1, yet read at level ℓ + 1 for every edge u→v) |
| 315 | Fischer–Meyer recurrence: base case "if i = 1" | "if ℓ = 1" |
| 316 | dropping the third index "reduces the space from O(V³) to O(V²)" | the 3-D table has V²(⌈lg V⌉ + 1) = O(V² log V) entries (O(V³) true but loose) |
| 324, Ex. 9.11 | init: "if i = j: D ← 0; if i→j ∈ E: D ← w else D ← ∞" | the else overwrites the diagonal with ∞; needs "else if" |
| 324, Ex. 9.11 | base case D[i, j] ← min{D[i, j], D[i, k] + D[j, k]} | D[i, k] + D[k, j] |
| 324, Ex. 9.11 | calls (i,j,k), (i,j,k+m), (i,j+m,k), (i,j+m,k+m), (i+m,j,k), (i+m,j,k+m), (i+m,j+m,k), (i+m,j+m,k+m) | k-half first: (i,j,k), (i,j+m,k), (i+m,j,k), (i+m,j+m,k), then (i+m,j+m,k+m), (i+m,j,k+m), (i,j+m,k+m), (i,j,k+m); printed order misses D[2, 1] on unit-weight 2→4→3→1 |

Not errata but worth knowing: p. 310's third boundary case ("if u does not lie on a negative cycle … dist(u, u) =
0") overlaps the second when u reaches a negative cycle that reaches u without lying on it; the page's "otherwise"
reading is the right one. p. 312 "the original weight of of the path" (typo).

## Remaining doubts / notes for the coordinator

- Exam box: "All of this chapter's algorithms are standard algorithms you may cite" is course policy I cannot verify
  from the sources here (the course's general rule — anything from lecture or the textbook may be used as a black
  box — supports it). Left as is.
- §9.5 writes O(V²(V + E)) = O(V²E) and §9.4 "Bellman–Ford on V+1 vertices and E+V edges, O(VE)": both rely on the
  page's stated convention (O(VE) stands for O(V² + VE)); correct under it, left as is.
- 9.7 assumes, like the book's formal statement, that the 137-flink constraint is dist(p, f) ≤ 137; with that reading
  s = p is optimal (checked against all s by brute force).
- Nothing fixed here appears on pages I was not assigned.
