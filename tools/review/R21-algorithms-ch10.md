# Review R21 — Algorithms Chapter 10 (maximum flows and minimum cuts), its exercises and concept pages (2026-10-30)

Method: read all four pages in full (figure captions included) and both figure scripts' captions; compared every
section, definition, theorem, proof and number with the book (ch10.txt, and book pp. 329, 330, 334–338, 342, 343,
345, 346 rendered from ch10.pdf, PDF p. = book p. − 326; Figures 10.2, 10.3, 10.7, 10.8 incl. paths A/B/C, 10.9,
10.10, 10.11 zoomed). Re-derived by hand: the Figure 10.2 flow, the four-row cut table, the residual graph (13
edges), the augmentation s c a b d t (F = 5) and the resulting flow and cut; Zwick's four steps from
(φ^(k−1), 0, φ^k), the count after 4n + 1 augmentations, the limit and the flows on the X edges (≤ 2); the
Figure 10.9 flow and both decompositions; Lemma 10.1, the maxflow-mincut proof (feasibility, conservation, value),
integrality, the decomposition proof, Lemmas 10.2/10.3, the fattest-path averaging (incl. why ≤ E pieces in G_f);
every exercise solution (10.0–10.9) before reading it, incl. the 10.4 counterexample's cut capacities, 10.5(a)'s
bidirected-tree test, 10.6(a)'s MakeAcyclic invariants and time bound, 10.6(b)'s set H, 10.7's level cuts, 10.9's
cyclomatic-number induction. Read both check scripts against the pages and ran them; ran tools/check.py.

## Writers' claimed book errors — verdicts

- p. 329, ∂f(v) := Σ_u f(u→v) − Σ_w f(v→w) while the text says "net flow out" and concludes |f| = ∂f(s) = −∂f(t):
  **confirmed** (formula has the sign flipped; Lemma 10.1's proof on p. 330 uses out − in). Also typo "or every
  vertex" for "for every vertex" (same page).
- p. 336, Zwick: after 4n + 1 augmentations k = 2n + 1, so residuals φ^(2n), 0, φ^(2n+1); the book's
  φ^(2n−2), 0, φ^(2n−1) fails already at n = 0. Limit 1 + 2Σ_{i≥1}φ^i = 1 + 2φ/(1−φ) = 2 + √5; the book writes
  Σ_{i≥1}φ^i = 1/(1−φ), giving 4 + √5. **Confirmed**; conclusion "< 7" stands. (Also "non-negative integer k" should
  be k ≥ 1; k = 0 would start from φ^(−1).)
- p. 337, path/cycle flows with −1 on reversed edges: **confirmed, but narrowed**. §10.5 says "arbitrary graph G";
  with antiparallel edges the clause breaks conservation/value (edges s→t, t→s, path s→t: value 2). For a path of a
  reduced G the clause is vacuous; it is meaningful (and correct) for a path that uses edges backward, i.e. an
  augmenting path, where f + F·P is the augmented flow. Page note made fairer (see below).
- p. 337, decomposition theorem "every non-negative flow": **confirmed** — one unit on t→s is a non-negative
  (s,t)-flow of value −1 (the book's value definition subtracts flow into s, so such edges are allowed); positive
  combinations of paths (value 1) and cycles (value 0) have value ≥ 0. The proof covers only |f| = 0 and |f| > 0.
- p. 339, decomposition algorithm walking from s and stopping at t: **confirmed** — circulation s→a→t→b→s:
  removes s a t, leaves t→b→s, every walk stalls at s. It works whenever no flow enters s (then the remainder is
  a circulation once s has no outflow), e.g. on all Ford–Fulkerson flows; page now says so.
- p. 342, "at most EV/2 iterations": **confirmed as a counting slip** — Lemma 10.3 bounds each *residual* edge,
  and a residual graph of a reduced network has up to 2E possible edges, so the argument gives EV; O(VE²) unchanged.
  The page does not claim EV/2 is false, only that the argument gives VE (correct).
- Exercise 10.4(a),(b): **confirmed false** with s→u (1), u→v (7), v→u (10), v→t (1): max flow 1 → 0, min cuts
  {s},{s,u,v} → {s,u}. (c) true.
- Exercise 10.2: **confirmed** (degenerate): §10.1 allows c = 0; with c(u→v) = 0 all placements can be minimum.
- Exercise 10.9(a),(b): **confirmed** — bounds are E − V + c; two disjoint triangles break (a). Also found: the
  book says "an arbitrary (s,t)-flow", but the pieces may use only edges with f(e) > 0, so f ≥ 0 is required
  (−1 around a directed triangle is a counterexample); the page had silently assumed f ≥ 0.

Additional book slips found (not on the pages, nothing to change): p. 338 "subwalk v_j→v_{j−1}→⋯→v_k" should be
v_j→v_{j+1}→⋯→v_k; p. 342 Lemma 10.3 proof calls the paths "ith"/"jth augmenting path" although, by Lemma 10.2's
convention (the ith path lies in G_{i−1}), they are the (i+1)st and (j+1)st (the level equations are right);
p. 340 "f′ can be decomposed into at most E paths and cycles" — G_f can have 2E edges; true for a maximum flow of
G_f without 2-cycles (the page already adds this justification).

## 2-algorithms/10-maximum-flows-and-minimum-cuts.md

Checked: headings = fixed list; all definitions and Lemma/Theorem names and statements vs pp. 328–343; figures
10.2/10.3/10.5–10.9 data vs the book's figures; residual-graph figure (13 edges, directions); Lemma 10.1 proof and
equality conditions; equivalence box and proof; smallest-min-cut remark; pseudocode (reduced network); integrality
proof; |f*| ≤ V−1 for unit capacities without parallel edges; rational/irrational paragraph; Zwick table and
max flow 2X + 1 (cut {s,a,b}); traps (diamond, fractional flow); §10.5 linearity, theorem, proof (incl. #f ≥ 2),
cancelling cycles, the O(VE) algorithm with t→s, "dropping cycles is not enough"; second decomposition sums;
fattest path (Dijkstra variant and the Prim-like book version are both correct for directed graphs), the
(1−1/E) bound; Lemma 10.2/10.3 proofs (indices consistent); EK example (BFS tie-break: "finds" is one valid run);
§10.7 table vs Figure 10.10 (two rows omitted, said "abridged"); Orlin/Karzanov/Mądry/2022 facts; black-box
section and template; Summary; exam box (says flows are not taught and on no exam — required wording present).

Changes:
- §10.5 path-flow note: "…in a reduced network those are never edges, and with antiparallel edges they would break
  conservation, so that clause is omitted here." → "For a path of G in a reduced network those reversals are never
  edges, and with antiparallel edges the −1 breaks conservation, so that clause is omitted here. The clause does fit
  a path that may use edges of a reduced network backward, such as an augmenting path: then P is a flow of value 1,
  and augmenting gives f + F·P." Why: fairness — the clause is not meaningless; it is exactly the augmentation.
- §10.5 O(VE) algorithm note: appended "The book's version does work whenever no edge into s carries flow — for
  instance on every flow Ford–Fulkerson computes, because an augmenting path never enters s." Why: fairness; the
  counterexample needs flow into s.
- Sources: "…the book's walk that stops at t (p. 339) can get stuck" → "… can get stuck when flow enters s".
- Zwick figure caption (tools/figs_a10.py, regenerated, assembled): "…repeated in the order B, C, B, A forever, each
  time pushing a smaller power of φ" → "…each round of four pushing smaller powers of φ than the round before".
  Why: B and C push the same amount φ^k, so "each time … smaller" was wrong per augmentation.
- tools/checks/a10.py: three checks added — the book's −1 path flow of every augmenting path of every intermediate
  flow (400 dense reduced networks, 54 backward edges used) is a flow of value 1 and f + F·P equals the augmented
  flow; Ford–Fulkerson flows (any/shortest/fattest) carry no flow into s and the book's walk decomposition never gets
  stuck on them or on 300 random flows without flow into s (pieces add up to f, ≤ #f, positive); the two new page
  sentences are present. Re-ran: ALL OK (a10.out saved).

## 2-algorithms/10-maximum-flows-and-minimum-cuts-exercises.md

Checked: statements vs pp. 344–346 (10.0 uses c: E → R⁺; Figure 10.11 direction); skip list and markers (10.10 ♣,
10.13(c) and 10.19 ♥); every solution re-derived (see above); the three figures' numbers are asserted in
figs_a10x.py; a10x.py checks the same networks as the page (10.4 example, 10.5(c)/(d), 10.5 trap, 10.6 trap,
10.7 tightness, 10.9 counterexample and tightness families).

Changes:
- Tip box: "every flow f ≥ 0 is a positive combination…" → "every flow f ≥ 0 with |f| ≥ 0 is …". Why: false without
  |f| ≥ 0 and contradicted the chapter page.
- 10.9 question: added "(The book says "an arbitrary (s,t)-flow"; since the paths and cycles may use only edges with
  f(e) > 0, the claims can hold only for f ≥ 0.)" Why: the page silently strengthened the hypothesis.
- Intro and Sources: 10.9 also needs "a non-negative flow, which the book leaves implicit".
- tools/checks/a10x.py: added the −1-around-a-triangle check (nonzero flow, value 0, no positive edge). ALL OK
  (a10x.out saved).

## concepts/maximum-flow.md, concepts/ford-fulkerson.md

Checked: definitions, key boxes, tables (VE iterations consistent with chapter), recipe (smallest min cut), traps,
both examples by hand (unique max flow 3,2,1,2,3; min cuts {s}, {s,a}, {s,a,b}; diamond runs), aliases unique
(a10.py), "not on the exams" line. No change.

## Site checks

tools/check.py on the three prefixes: OK. Previewed (light) only the changed parts: Zwick caption and §10.5
(chapter page), tip box and Exercise 10.9 (exercises page).

## Other pages (not assigned)

- content/2-algorithms/11-applications-of-flows-and-cuts.md line 18: "every flow is a positive combination of at
  most E path flows and cycle flows" — needs "every non-negative flow with |f| ≥ 0" (true for the maximum flows used
  there).

## Doubts

- Exercise 10.2's failure is degenerate (zero-capacity edge); listing it as an erratum is defensible under §10.1's
  c: E → R≥0 but minor.
- The book's "EV/2" bound might still hold by a finer argument; only the argument's count is wrong. No example with
  more than EV/2 Edmonds–Karp iterations is known to me; the page does not claim one.
