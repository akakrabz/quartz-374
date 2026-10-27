# Review R16 — Algorithms Chapter 8 (shortest paths), its concept pages and exercises (2026-10-25)

Method: read every page in full (SVG stripped for reading, figure captions kept); compared sections, definitions,
claims, lemmas, proofs, pseudocode and examples with the book (ch08.txt, and the relevant pages of ch08.pdf rendered
with pdftoppm, book p. = PDF p. + 272: pp. 275, 280, 283–287, 289, 294, 297, 299, 300, 302; Figs. 8.3, 8.6, 8.9/8.10,
8.14, 8.17, 8.18, the looped tree and the Ex. 8.16/8.17 graphs at high resolution); re-entered every book graph from
the rendered figures and compared it edge by edge with the check and figure scripts (Fig. 8.3: 6 edges; Fig. 8.6: 18
edges; Fig. 8.9 dag: 12 edges; Figs. 8.15/8.17: 12 edges; Fig. 8.14 family; looped tree: 8 tree + 4 loop edges with
loops e 4, d 16, g 7, h 42; Fig. 8.18: 17 edges; Ex. 8.16: 7 edges; Ex. 8.17: 6 red + 4 blue). Re-derived by hand:
the fan MST/SPT (14 / 26, distances 5 6 7 8); the BFS run of Fig. 8.6 phase by phase; the dag values 0 3 8 6 13 8 9 and
PushDagSSSP's 15→13, 10→9 (also 7→6 at c); the Dijkstra example table (6 Insert, 6 ExtractMin, 4 DecreaseKey); the
NonnegativeDijkstra counterexample (both variants, and the book version s a b a t); the book's Dijkstra on the Fig. 8.15
graph (d extracted six times with 5 4 3 2 1 0; e→d, f→e, f→d relaxed twice); the dist≤i table rows 0–6; both in-place
Bellman–Ford edge orders; Moore's run s ✠ a b c ✠ d f ✠ d e ✠ d; the layered-dag example (4, and 3 with 5 edges); all
concept-page examples; every exercise answer (re-solved before reading the solutions). Wrote an independent script
(scratchpad verify.py) for the errata: Moore's criterion on 3000 random graphs (book's version wrong on 297, "token
pulled a V-th time" on 0), Fig. 8.6/8.17 pull sequences, the dag identity with −∞ arithmetic (fails only at s, 428
times, never elsewhere), Shier–Witzgall relaxation counts 3(2^k − 1) for k ≤ 8 under both out-edge orders and both
tie-breaks, the 8.8(d) run, the 8.17 walk. Read both check scripts against the pages and ran them; ran tools/check.py.

## 2-algorithms/08-shortest-paths.md

Checked: §8.1 definitions (walk length, δ, SSSP, SPT), subpath optimality, uncrossing (Fig. 8.1), the existence proof
(fewest-edge shortest path, h(pred(v)) = h(v) − 1, cycle deletion uses only reachable cycles ≥ 0), SPT/MST table and
figure, "lightest edge at s is in both trees" (cut property + positive weights); §8.2 existence iff (book p. 275), the
three-case table, the NP-hard remark, Figs. 8.3/8.4 (2 − 8 + 1 + 4 = −1; triangle paths s v u and s u v, both 0),
undirected negative edges, O(VE + V² log V) matching remark, all four traps (constant-shift example 0 vs 3/4);
§8.3 InitSSSP/Relax/FordSSSP = book p. 276–277, the ∞ + w convention, relax figure (3 + 4 < 9), the four claims and
the page's proofs (Claim 2 via the first repeated vertex; Claim 3: the cycle edge leaving v becomes strict when the
last pointer is set; Claim 4), instance table, traps; §8.4 BFS and BFSWithToken = Fig. 8.5, Lemma 8.1 and proof, the
once-per-vertex/edge consequences, "dist(v) = ∞" test, Theorem 8.2 and proof, the example, traps; §8.5 recurrence,
dependency graph rev(G), evaluation order = postorder of rev(G) = topological order of G (consistent with the Ch 6
page's convention and warning box: dependency edges point to the needed subproblem), DagSSSP = Figs. 8.7/8.8,
PushDagSSSP, its induction, example, LLP comparison, traps; §8.6 Dijkstra = Fig. 8.11, the corrected invariant,
halting with negative edges (Claim 2), Lemmas 8.3/8.4 and proofs, Theorem 8.5 and proof (final value at the only
extraction uses Lemma 8.4), running-time table (heap, array O(V²), Fibonacci O(E + V log V); footnote 8), O(V + E log V)
remark, NonnegativeDijkstra = Fig. 8.13, the counterexample figure, Fig. 8.15 claims, Shier–Witzgall description
against Fig. 8.14 (j-th triangle from the right: 0, −2^j, base −2^{j−1}; V = 2k + 1; Θ(2^{V/2})), traps; §8.7
BellmanFord (both forms), Lemma 8.6 and proof, V − 1 rounds, the iff of negative-cycle detection (sum around C),
new-source trick, table, Moore = Fig. 8.16, per-phase facts, Lemma 8.7 (re-proved: a tense edge's tail is queued at
the start of a phase and is pulled in it), the V-th-token criterion (proof: with no reachable negative cycle all
labels are final after V − 1 phases, so phase V relaxes nothing and the loop stops before the V-th token pull), the
off-by-one example, BellmanFordDP = p. 295 and the three refinements, the layered-dag view, traps; "Which algorithm
when"; the three reductions in rubric format (graph with "directed", problem with from/to and why, black box, time in
input parameters; counts (k+1)n² / 8(k+1)n², 2V / 3E, (k+1)V / kE); Summary; exam box against algo-facts (HW8 allows
Dijkstra; rubric 3/3/2/2, −1 slower algorithm, −1 re-explaining). Consistency with 05 (BFS = WFS with a queue; best-
first "Dijkstra"; the book's Ch 5 says "positive", Ch 8 "non-negative" — no contradiction) and 06 §6.4 confirmed.
No "clearly/obviously/trivially"; history paraphrased.

Changes:
1. §8.4 history. Before: "Konrad Zuse had implemented it in 1945, to count components." After: "Konrad Zuse had
   already described it in 1945, as a program to count components." Why: the book says Zuse *described* an
   implementation (a Plankalkül program in his thesis, never run then; first Plankalkül compiler 1975).
2. §8.5. Before: "(In a general graph negating weights creates negative cycles, and longest paths are NP-hard.)"
   After: "(… negating weights turns every positive cycle into a negative one, and longest simple paths are NP-hard.)"
   Why: negation creates negative cycles only from positive cycles; "longest paths" in the walk sense are unbounded.
3. Sources, Dijkstra invariant. Before: "(p. 285)". After: "(pp. 284 and 286, a sentence split by the figure page
   285)". Why: rendered pages — the "if and only if" sentence starts at the bottom of p. 284 and ends at the top of
   p. 286; p. 285 holds only Figs. 8.10 and 8.11.
4. Sources, footnote 2. Before: "a shortest walk need not be a simple path, as footnote 2 (p. 275) says, when there
   are zero-weight cycles" (reads as if the book said so). After: "footnote 2 (p. 275) says that a shortest walk must be
   a simple path, but with a zero-weight cycle it need not be — some shortest walk always is."
5. Sources, captions and dag identity. Added the pages "(pp. 280, 294)" for Figs. 8.6/8.17 and "— it fails at s
   whenever δ(s) = −∞, for instance when s lies on a negative cycle" after the p. 282 correction. New check in a08.py:
   with −∞ arithmetic the identity holds at every v ≠ s and fails at s exactly when δ(s) = −∞ (400 random graphs).

## concepts/shortest-paths.md

Checked definition box, why-it-works, recipe table, traps, the example (every run of Ford: a2 b4 t5, pred(t) = b, 3 or
4 relaxations — the check enumerates all runs), anchors.
Change: trap. Before: "Dijkstra needs non-negative weights." After: "Dijkstra needs non-negative weights for its
O(E log V) bound (and the textbook version, NonnegativeDijkstra, to be correct at all)." Why: the chapter (and the
Dijkstra concept page) shows the book's Dijkstra is correct with negative edges if no negative cycle is reachable; the
old line contradicted that.

## concepts/breadth-first-search.md, dijkstras-algorithm.md, bellman-ford.md; whatever-first-search.md (alias edit)

Checked statements, pseudocode (= book), templates, traps (rubric −1 / −½ items), examples recomputed by hand (3×3
grid: labels i + j − 2, phases 1 2 3 2 1, 24 edge tests; undirected Dijkstra s0 b1 a3 t4 with a lowered from 4 and t
from 6; Bellman–Ford example +1 cycle → a2 b3 c0, −1 cycle → all three fall each round and the test pass reports).
whatever-first-search: aliases no longer contain "BFS"/"breadth-first search", Related links the new page; aliases
unique site-wide (checked). No changes.

## 2-algorithms/08-shortest-paths-exercises.md

Checked every statement against pp. 297–302 (♥ marks: 8.4(b), 8.6(c), 8.9, 8.10 — skipped correctly) and re-solved
every exercise: 8.0(a) three tests and both directions (passing labels ⇒ no reachable negative cycle), the tight-
cycle figure (labels 0 0 1, truth 0 1 2); 8.0(b) Null pointers, tree-path labels, reduction to (a); 8.1 E ≤ (3n − 1)/2,
the D/L formula and its proof (walk leaves T_u only by a loop edge), book-tree values 39, 32, 40, O(1) queries; 8.2(a)
negative-cycle test d_y(x) + w < 0 and the −∞ condition, the formula; 8.2(b) the (k + 2)-layer graph, edge count
(k + 2)E − k, both directions of the layer-(k + 1) test, the super-source trick per layer, O((k + 1)E log V), figure
values; 8.3(a)/(b); 8.4(a) the bypass claim (first A→B edge), lazy-deletion sweep, figure 12 10 10 10 11; 8.5;
8.6(a) (I1)/(I2), the chain cannot reach Null (contradiction with Lemma 8.6), V steps land on the cycle; 8.6(b) doomed
vertices both directions; 8.7; 8.8 (a) counterexample (s→a 0, a→b −1, b→a −1, a→s 100; 51 rounds, −102), corrected
claim; (b) run with the second cycle; (c) both directions including the non-halting lemma (σ argument re-checked
step by step); (d) counterexample (relax s→u, u→v, s→v, v→u, then halt) and the true half via P ⊆ R; 8.11 (SCC test
for "on a cycle", the dag U); 8.12 tight dag + BFS, the V·w + 1 packing; 8.13 NumPaths on Fig. 8.18 (s1 a1 b1 d1 M3
C4 E4 F7 t8 in my naming; 13 tight edges); 8.14 + trap; 8.15 (a)–(c); 8.16 (example 6); 8.17 state graph (4V + 1
vertices, ≤ 4E edges), walk RRBRBRR = 9, typo (the same walk is printed correctly, ending b→t, in the book's Ex. 5.15).
Reductions are in the four-part rubric format with "directed" stated. No changes.

## Check scripts

a08.py: implementations compared line by line with the page's pseudocode (InitSSSP, FordSSSP, BFS, BFSWithToken,
both DagSSSP forms, PushDagSSSP, Dijkstra with indexed heap, NonnegativeDijkstra, both BellmanFord forms, Moore,
BellmanFordDP 1–3, BellmanFordFinal); the graph data equal my re-entries; the printed table rows, traces and figure
labels are asserted against the page. Added one check (identity with −∞). 88 OK, ALL OK (a08.out saved).
a08x.py: implementations match the page's algorithms (one_negative, k_negative with the super-source layers,
replacement sweep, bf_cycle, bf_minus_inf, the Ford runs of 8.8, all_negative, best paths, NumPaths, the 8.14–8.17
reductions); data equal my re-entries. Unchanged; 67 OK, ALL OK (a08x.out re-saved, identical).
tools/check.py --only on the six prefixes: OK.

## Book errata (confirmed on the rendered pages and by code)

| page | as printed | should be |
|---|---|---|
| 275, fn. 2 | "if there is a shortest walk from s to t, that walk must be a simple path" | some shortest walk is a simple path (a zero-weight cycle gives non-simple shortest walks: s→a 1, a→s −1, a→t 2) |
| 280, Fig. 8.6 caption | pulled "s ✠ b d ✠ c a g ✠ f e ✠ h ✠ ✠" | "… ✠ h" (the loop stops when only the token is left) |
| 282 | the dag identity "holds for all directed graphs" | holds when no negative cycle is reachable from s (with −∞ values it holds at every v ≠ s, and fails at s whenever δ(s) = −∞) |
| 284/286 (sentence split by fig. page 285) | an edge u→v "is tense if and only if" u is in the queue or was most recently extracted | "only if" (a vertex in the queue may have no tense edge: s→a 1, s→b 1, a→b 5) |
| 287, Thm 8.5 proof | "Immediately after we Pull vertex v_{j−1} from the queue, either dist(v_i) ≤ … or we set dist(v_i) ← …" | "Extract", dist(v_j) |
| 293 | "Moore halts after at most V − 1 phases" | distances are final after V − 1 phases, but the vertices pushed in phase V − 1 are scanned in a V-th, partial phase; the token is pulled at most V − 1 times |
| 294 | negative cycle iff "the queue is non-empty immediately after the token is Pulled for the (V − 1)th time" | "… for the V-th time" (equivalently: iff the token is pulled a V-th time); path s→v1→…→v_{V−1} is a false positive |
| 294, Fig. 8.17 caption | "s ✠ a b c ✠ d f ✠ d e ✠ d ✠ ✠" | "… ✠ d" |
| 299, Ex. 8.8(a) | "contains a negative cycle through s" | s lies on a negative closed walk (a negative cycle reachable from s reaches s); counterexample s→a 0, a→s 100, a→b −1, b→a −1 |
| 299, Ex. 8.8(c) | "no negative cycles iff P ∪ X is always a dag" | "no negative cycle reachable from s" |
| 299, Ex. 8.8(d) | "no negative cycles if and only if R is always a dag" | only "R always a dag ⇒ no negative cycle reachable from s"; the converse fails (s→u 10, s→v 0, u→v 1, v→u 1) |
| 302, Ex. 8.17 | shortest walk "s→a→b⇒d→c⇒a→b→c" | "…→b→t" (no edge b→c; weight 9) |

Minor, not on the pages: p. 275 "well-defiend"; p. 281 stray character "s to‘v"; p. 283 "the distance of every in
O(V+E)" (missing "vertex"); p. 291 Lemma 8.6 proof "either dist(v) < dist(u) + w(u→v) already" (should be ≤);
p. 302 Ex. 8.16 "which is the length of the walk … has length 6" (garbled sentence).

## Remaining doubts / notes for the coordinator

- The task list cited "p. 279 Fig 8.6" and "p. 285" for the invariant: Fig. 8.6 is on p. 280, and the invariant
  sentence runs pp. 284/286 (p. 285 is a figure page). The pages now cite these.
- "Halts after at most V − 1 phases" (p. 293) is an imprecision (complete phases vs the final partial one), not a
  false statement in substance; the page words it as a precision.
- 8.15(c) uses Dijkstra on 0/1 weights (O(E log V)); a 0-1 BFS would be O(V + E) but is not one of the course's
  standard black boxes, so Dijkstra should be full credit. Left as is.
- Big-O for the jumps and k-edge reductions is written O(kn²), O(k(V + E)); for k = 0 read (k + 1). Left as is.
- Homework-style exercises (HW8 due Oct 27, shortest paths; no handout available): 8.15 (espresso/Starbucks), 8.16
  (walk length ≡ 0 mod 3), 8.17 (no three same-colored edges), 8.2(b) (k negative edges), 8.12 (best paths), 8.13
  (counting shortest paths), 8.14 (meeting point), 8.5 (reinserting an edge). If HW8 turns out to contain one of them,
  that section should be hidden until the deadline.
- Chapter 5 page (not mine): best-first "Dijkstra" says "If all weights are positive" — that is the book's Ch 5
  wording; Ch 8's "non-negative" is the sharper condition. No contradiction; no change suggested.
