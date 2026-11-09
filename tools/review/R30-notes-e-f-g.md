# R30 — review of Part 3 notes E, F, G (+ concepts matroids, minimum-cost-flow; link lines)

Sources: E-matroids.pdf, F-pseudoflows.pdf, G-mincostflow.pdf rendered page by page (pdftoppm, 110–250 dpi) and read;
every formula and pseudocode checked on the image, not the .txt. Own brute force:
scratchpad `r30_indep.py` (fewest-edge negative cycle DP vs brute force, Theorem F.2 with Σb ≠ 0, two-interval
heaviest-first greedy). Goldberg–Tarjan abstract fetched from the Princeton tech-report page linked on the G page.

## content/4-lecture-notes/e-matroids.md
Checked: definitions, table of six matroids (bases/circuits), GreedyBasis and running time, Theorem E.1 proof
(first-difference argument, ties, heredity), Theorem E.2 proof (weights m+2/m+1/0), class-scheduling example,
traps, Lemma E.3/E.4 proofs, corrected GreedySchedule/Realistic?, six-task example (11 vs 17, 720 schedules), both
figures' data, exercises count. Counts 19/167 hereditary families and 16/68 matroids agree with known values.
Changes:
- "matroid iff GreedyBasis is optimal for every choice of weights" → "... of non-negative weights". With negative
  weights GreedyBasis is not a maximum-weight independent set even on a matroid (U(1,1), w = −1), and Theorem E.2
  (stated just above) is about max-weight sets. Check added to ne.py.
- "leaves the proofs that they are matroids as Exercises 1–4" → "that the last four are matroids": exercises cover
  graphic, cographic, matching, disjoint-path only.
Note errors confirmed: p. 1 "subsets of X" (→ S); p. 2 n×m matrix with columns 1..n (→ 1..m); p. 2 cographic
defined for every graph but has no independent set (not even ∅) when G is disconnected; graphic bases "spanning
tree" (→ spanning forests if disconnected); p. 3 Σ_{j=1}^ℓ w(h_i) (mixed index); p. 4 "Theorem ??" twice; p. 5
D[i] (→ D[i_t]); p. 6 |X(t)| < t (→ ≤); p. 6 "Lemma 9" (→ E.3); p. 6 GreedySchedule sorts P increasing (→
decreasing; example 17 vs 11 verified by hand); pp. 6–7 Realistic? reads X[0], uses "if" (→ while), and
GreedySchedule appends unsorted.
Ambiguous rather than wrong: p. 4 "easy counterexample with only two classes" — false for heaviest-first GreedyBasis
(verified exhaustively), true for Ch. 4's earliest-finish rule; the note's paragraph mixes the two algorithms. The
page's wording handles this correctly.

## content/concepts/matroids.md
Checked definition, why-it-works, recipe, traps, linear example (order, kept/rejected, weight 14, 8 bases, next 13,
circuit). Change: "greedy is optimal for all weights" → "for all non-negative weights" (same reason as above).
Description ("max-weight basis for every choice of weights") is correct as written and left.

## content/4-lecture-notes/f-balances-and-pseudoflows.md
Checked: F.1 definitions and figure (balances at all six vertices), reduction and Lemma F.1 proof, Theorem F.2 proof
(cut capacity algebra), pseudoflow/residual definitions, residual figure (15 residual capacities, path 15/7/4/10,
push 4, second push 11/5/6, final flow), infeasible-cut argument both sides, x→y→z example, FeasibleFlow, z
construction and counterexample s→t(10), t→v(20), b(v)=15, antisymmetric residual formulas, lower-bound recipe,
push-relabel pseudocode, Lemmas F.3–F.8 proofs, FIFO/highest-label/dynamic-tree bounds, two hand-traced runs.
Changes:
- REFUTED writer claim: the note prints B_ψ := Σ_v |b_ψ(v)| (p. 4, absolute-value bars visible at 250 dpi; lost in
  pdftotext), not Σ b_ψ ≡ 0. Real slip: missing /2 (twice the "total residual supply" it names; drops by 2R).
  Page parenthetical and Sources rewritten; nf.py check replaced (10 = 2·5, drop 8 = 2R).
- NEW: Theorem F.2 (and Lemma F.1's "equivalently every edge into t") need Σ_v b(v) = 0, which the note omits; a
  single vertex with b = −1 has neither a feasible flow nor an infeasible cut. Added "Assume Σb = 0" at the start of
  F.2, the hypothesis in the Theorem F.2 box, a remark in its proof, and Sources entry; nf.py checks the
  counterexample and 100 random Σb ≠ 0 networks (separate RNG, other counts unchanged).
- Sources: "the O(VE²) bound needs the globally shortest path" → "is Edmonds–Karp's in G′, proved for the globally
  shortest ... path" (whether the per-source version fails is not known to me).
Note errors confirmed: p. 4 infeasible-cut rules swapped; p. 5 ψ(e) ← ψ(e) − R on e ∉ E (→ reversed edge); p. 6
balance written out − in; p. 6 z with only t→z, z→s (fails when |f| or net inflow at t must be negative); p. 7
second cases ψ(u→v) (→ ψ(v→u)) in both ℓ_ψ and c_ψ, and c_ψ ≥ 0 (→ > 0); p. 9 "non-zero residual balance" (→ zero).
Precisions confirmed: F.5's b_ψ is the excess (sign opposite to F.3); Lemma F.8 "must equal" (→ at most; saturating
pushes can lower Φ). Not reported by writer, left alone (exercise): p. 11 Ex. 3 preflow condition printed with ">"
for "≥".

## content/4-lecture-notes/g-minimum-cost-flows.md
Checked: definition, max-flow reduction and sign, residual costs, augmentation formula, optimality proof via
decomposition, cycle-canceling analysis, two-stage method, running example (16; 18-flow, unique negative cycle −2),
SSP pseudocode, assumptions, extra-vertex counterexample, Lemma G.1 proof, max-flow special case, SSP table, Lemma
G.2/G.3 proofs, potentials table (all distances and reduced costs recomputed by hand), π ← dist counterexample
(b→s gets −2), Fulkerson reduction balances, transportation example, single-supply section.
Changes:
- NEW note error: p. 4 calls the negative cycle with the fewest edges NP-hard; it is polynomial (smallest k with a
  negative closed k-edge walk; DP O(V²E); verified against brute force on 400 digraphs). Page paragraph rewritten
  (most negative cycle kept as the NP-hard example, with the longest-cycle reason); Sources entry; ng.py checks.
- "almost-linear time with integer data" → "with polynomially bounded integer data" (the 2022 result's hypothesis).
- Sources: added "Disjktra" (p. 10) next to "Disjkstra" (p. 9).
Note errors confirmed: p. 2 value −f(t→s) (→ +); p. 3 "immediately conclude" (if-direction needs decomposition);
p. 5 Augment ψ(e) bug; p. 5 extra-vertex "report infeasible at once" wrong for arbitrary s, t; p. 7 "cycle canceling"
(→ SSP); p. 9 π(e) ← 0, "Disjkstra", π(v) ← dist(v) (→ π(v) + dist(v)), "Lemma 2"; p. 11 cost(f) + ℓ·$ (→ cost(f′));
p. 13 "f_t)" (→ f_T), "Lemma 1"; p. 10 "Kantorivich". Precisions confirmed: backward residual capacity f − ℓ with
lower bounds; finite capacity for t→s in the SSP max-flow case. Goldberg–Tarjan: abstract states
O(nm log n · min{log(nC), m log n}), i.e. O(VE² log² V) strongly polynomial — the note's O(VE² log V) misses a log;
confirmed from the linked Princeton tech-report page and my own recollection of the JACM 1989 abstract.

## content/concepts/minimum-cost-flow.md
Checked all bullets, why-it-works, recipe, traps, example (8 = 3 + 5; potentials (0,1,2,3); five reduced costs).
Change: "At most B iterations" → "... with integer capacities and balances" (false otherwise). ng.py page check added.

## Link lines (maximum-flow, greedy-algorithms, minimum-spanning-trees)
Only the added Where-it-appears/Related links checked: correct targets and anchors, accurate descriptions. No change.

## Other
Aliases: all 16 unique site-wide (case-insensitive). No sentence copied (6-gram scan outside code: only theorem
statements, section titles, status line). Checks: ne.py 77 OK, nf.py 57 OK, ng.py 57 OK, all ALL OK, .out saved.
check.py on the eight pages: OK. Light-mode previews of the changed F and G passages look fine.
Doubts: none blocking. The errata file /home/claude/work/notes/errata-notes.md still lists "B_ψ=Σb_ψ≡0" for F
(refuted) and lacks the F.2 hypothesis and the G p. 4 NP-hardness error.
