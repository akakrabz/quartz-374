# Review R20 — Algorithms Chapter 11 (applications of flows and cuts), its exercises and concept pages (2026-10-30)

Method: read all four pages in full (figure captions included); compared sections, statements, networks, proofs and
running times with the book (ch11.txt; pp. 356, 360, 361, 364–369 and the figures of pp. 369–372 of ch11.pdf rendered
with pdftoppm, book p. = PDF p. + 352; ch10.txt for the black boxes); re-derived every reduction in both directions
(edge-disjoint paths and the walk argument, undirected cancellation, Menger, vertex splitting correspondence,
vertex-disjoint paths, matching and the cut ({s} ∪ L, R ∪ {t}), the residual graph = alternating paths, tuple
selection and multiplicity, exam scheduling, path cover both directions, faculty hiring with/without the triangle
inequality, baseball theorem, certificate cut and its proof, project selection identity), all numbers (Detroit
capacities 1/5/7/13, 27 games, 305 > 304 and that no 2- or 3-team Q works, the 8/8/0 example, the eight-project
example and its valid sets, reviewer and matching concept examples, the box example of Ex 11.10), and every exercise
solution (11.1 balance identity; 11.2 network and decomposition argument; 11.3 Lemmas A and B and the invariant;
11.4 both cut directions; 11.5(a); 11.6–11.10). Re-entered the Sodor graph, Figure 11.10 terminals and paths,
Figure 11.12 board and Figure 11.13 grid/tokens from 300–400 dpi renders: all match the check scripts. Read both check
scripts against the pages (they implement the page's networks and compare with exhaustive search) and ran them.

## Book errors reported by the writers — verdicts (against the PDF)

- p. 361, path-cover proof: confirmed. The claim is "k paths ⇔ matching of size V − k"; the bullet labeled ⇐ proves
  cover ⇒ matching and the bullet labeled ⇒ proves matching ⇒ cover; "We project M′ back" should be M; the bipartite
  graph is G′ = (V′, E′) in the text but "H" in both bullets of the construction.
- p. 356: confirmed — "enter any vertex in U or leave any vertex in W … edges from U to W" for L and R.
- p. 360: confirmed — input A[1..t, 1..p] with A[k, ℓ] = proctor ℓ free in slot k; the edge rule says A[ℓ, k].
- p. 365: confirmed — "let f be a feasible flow that saturates every edge out of s" then reads f(g_ij → t_i) as a
  number of games; needs an integral flow (theorem itself is right).
- pp. 364–365: confirmed — R[i] = Σ_j G[i, j] (p. 364), but the example uses R[n] = 27 for Detroit, whose division
  games are only 3 + 4 = 7.
- p. 367: confirmed — "a valid input to the maximum cut problem".
- p. 366: confirmed — "includes all its dependents; that is, … every project that x depends on" (prerequisites).
- p. 368, Ex 11.3: confirmed — "t₁, t₁, …, t_τ".
- New (minor): p. 365 says "\binom{n}{2} game nodes g_{i,j}, one for each pair 1 ≤ i < j < n"; that is \binom{n−1}{2}.

Precisions claimed by the writer, all correct: tuple selection counts with multiplicity (book says "set of tuples";
all capacities 2 on one tuple gives flow 2); faculty hiring's all-pairs condition equals the consecutive one under the
triangle inequality (check has a 1-vs-2 counterexample without it); vertex-disjoint paths need edge capacity 1 only
because of an edge s → t (every other edge touches a capacity-1 vertex) — the page's trap says exactly that.

Additions, all correct and marked: Menger ("not stated in the book's chapter"), certificate-cut theorem ("precision
added here"), Detroit Q = all four (305 > 304, unique), second baseball example (now marked "ours" in the text too).

## 2-algorithms/11-applications-of-flows-and-cuts.md

Changes:
- §11.2 trap "Do not cap s and t": before "If you split them as well (the book does, and uses s_out and t_in as source
  and target), their split edges must have capacity ∞" → after "… take s_out and t_in as source and target, as the
  book does: then their split edges never cross a cut forward, and their capacities do not matter. With s_in and
  t_out instead, those split edges need capacity ∞." Why: with s_out/t_in as terminals the split edges of s and t
  lie into the source / out of the target and are irrelevant; the old sentence said they must be ∞. Check added.
- §11.7 trap "Direction of the infinite edges": before "Reversed, they would let you take a prerequisite without its
  dependents but forbid taking a project without its prerequisite" → after "Reversed, they would let you take a
  project without its prerequisites but force you to take every project that needs a selected one". Why: the old
  text described the correct constraint as the reversed one's. Check added (u needs v, p = 5/−1: reversed cut picks
  {u}).
- §11.6: "(the book's footnote)" → "(the book's footnote; the following example is ours)" — the 8/8/0 example is an
  addition (Sources already said so).
- §11.6 trap: "trivially eliminated" → "already eliminated" (matches the formulation paragraph; avoids the word).
- Sources: added the \binom{n−1}{2} erratum (p. 365).

Checked and unchanged: black boxes against ch10 (integrality, decomposition ≤ E paths/cycles in O(VE), Orlin O(VE));
template; every reduction's network/claim/algorithm/time against the book (O(VE), O(N³), O(n³), O(n⁴), O(VE));
headings and anchors; table; summary; "On the exams" box (flows not taught, on no exam, link to the graph-reduction
rubric); Sources' list of errata.

## 2-algorithms/11-applications-of-flows-and-cuts-exercises.md

Change: Ex 11.4 trap "s and t must not get capacity-1 split edges, or the cut could 'close' them" → qualified: only
with source s_in or target t_out; with s_out/t_in (the page's network) their split edges never cross a cut forward.
Why: same error as the chapter trap; with the page's own terminals the statement was false. Check added to a11x.py
(300 random graphs; capacity 1 at s_in/t_out loses flow in 44).

Checked and unchanged: all statements against pp. 368–372 (paraphrased faithfully; skipped parts and ♥/♣ markers
right); all ten solutions re-proved; figure data re-read from the book.

## concepts/flow-reductions.md, concepts/bipartite-matching.md

No change. Definitions, template, traps, both examples (reviewer assignment 6 / 5 < 6; greedy {1A, 2C}, alternating
path 3 C 2 A 1 B, cut {s, 3, 4, C} of capacity 3) re-derived; aliases unique.

## Scripts and checks

- tools/checks/a11.py: two checks added (s/t split terminals; reversed infinite edges) using a local RNG / BFS so the
  other random streams are unchanged; two page-text checks added. ALL OK, a11.out saved.
- tools/checks/a11x.py: one check added (Sodor trap). ALL OK, a11x.out saved.
- tools/check.py on 2-algorithms/11-applications-of-flows-and-cuts, concepts/flow-reductions,
  concepts/bipartite-matching: only "wikilink target not found: [[concepts/polynomial-time-reductions]]" (Ch 12,
  being written).
- No display or figure changed, so no screenshots.

## Doubts

- None on correctness. Wording only: the §11.2 trap heading "Edges need capacity 1 too" is stronger than needed
  (only an edge s → t matters), but its explanation is accurate.
