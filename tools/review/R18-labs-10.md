# Review R18 — Labs 10a and 10b, `content/3-homework-and-exams/lab-10a.md`, `lab-10b.md` (2026-10-28)

Method: rendered lab10a.pdf and lab10b.pdf (110 dpi; the looped-tree figure again at 300 dpi) and read every
statement and the figure. I read the loop edges off the figure myself: e→r 4, d→r 16, g→r 7, h→r 42, and the tree
r→a 5, r→b 8, a→c 17, a→d 0, c→e 23, b→f 1, f→g 9, f→h 14. They match the page. I solved every problem before
reading the pages, then compared. Rubric sources: algo-facts.md, toolkit §12–13, SPEC-labs.md. Related pages read:
Ch 8 §8.6 (Dijkstra, NonnegativeDijkstra, Lemmas 8.3/8.4, Shier–Witzgall), Ex 8.0, 8.1, 8.2, 8.5, 8.6, 8.14; Ch 9 §9.1
running example and §9.2 convention, Ex 9.3, 9.6, 9.8.

Independent brute force (own code, nothing shared with the check scripts) in `/tmp/r10/bf/r10a.py` and `r10b.py`:
- 10a P1: 5,000 random graphs with one negative edge (half of them adversarial: weights in {0,1,2,3}, w(u→v) = −δ_{G−uv}(v,u),
  the most negative weight allowed, so zero-weight cycles through u→v; 1,874 graphs with a zero cycle), all sources and
  targets. Truth from enumerating simple paths. Checked: the two-run formula; the rebuilt path (simple, correct length,
  ties go to d_s(t)); the two-layer one-run graph (2E − 1 edges); the re-inserting Dijkstra with an explicit
  Insert/DecreaseKey array queue and fixed or random tie-breaking: correct, ≤ 2 extractions per vertex, u at most once,
  at most one key drop and only from u to v, every extraction after u's final, ExtractMin ≤ 2V, relaxations ≤ 2E,
  predecessor paths simple and shortest. Early stopping and the book's NonnegativeDijkstra fail on some graphs, and
  "twice" is attained. The negative-cycle test d_v(u) + w ≥ 0 also holds. The example, the run log and the counts
  8/1/8 match, and so does the +5 trap. 0 failures.
- 10a P2: 2,500 random undirected or directed graphs. The two-Dijkstra answer, with the set of best cities, equals a
  time-expanded simulation with waiting (earliest common time). Both traps occur. Figure numbers match. 0 failures.
- 10a P3: 1,500 random looped trees, n = 1..11, all pairs, against Floyd–Warshall. Checked: the closed form; my
  recursive L equals the brute-force L (min over leaves below x of the path to the leaf plus its loop edge); the
  split-root formula with the u = v special case (u = r, v = r, u = v = r included); E ≤ (3n−1)/2. The handout tree's
  numbers match. 0 failures.
- 10b P1: 6,000 random graphs with negative edges (2,382 with a zero-length cycle), the weight of u→v lowered or
  raised without creating a negative cycle. Truth from simple-path enumeration under w′. Checked:
  - column u and row v are unchanged;
  - the in-place repair, in random order, is exact;
  - the O(1) test;
  - CheckAPSP on old, true and perturbed arrays;
  - the lemma "correct ⇔ δ′(u,v) = dist[u,v]";
  - the one-search test;
  - the shortcut;
  - my own criterion "correct after a raise ⇔ δ_{G−uv}(u,v) ≤ w(u→v)", which agrees.

  The out-neighbor test and the tight-incoming-edge test fail only on graphs with a zero-length cycle (232 and 277
  failures, none without one).
- 10b P1(d): 1,200 random H, half with negative edges reweighted by Johnson potentials. Checked: |E(G)| = m + 2n + 1,
  the old array is all zeros, and decoding (≥ M means unreachable, then un-reweighting) gives APSP of H. 0 failures.
- 10b P2: 3,000 random exact rational rate matrices, n = 1..6. Half of them contain zero rates, and the set of rates
  includes {1/6, 6, 1/2, 2, …}, so cycles of product exactly 1 occur. The page's ArbitrageCycle pseudocode, run
  verbatim, returns a simple cycle of positive rates with product > 1 exactly when brute-force cycle enumeration finds
  one. Max-product Floyd–Warshall and an explicit super-source Bellman–Ford agree. MaxCurrency equals the best
  simple-path product, and the −ln float version agrees to 1e−9. The figure trace returns € → $ → ¥ → €. The
  no-arbitrage example gives (1, 120, 1.2). The float remark gives −2.220446e−16. 0 failures.

Check scripts: read against the pages (same algorithms as stated, including the run table, the stale-copies heap,
CheckAPSP, the one-search test, and ArbitrageCycle as in the pseudocode). Both end with ALL OK, before and after my
edits; the .out files are saved. `check.py --only 3-homework-and-exams/lab-10`: OK. I previewed both pages in light mode
with every callout unfolded (temporary copy of content/ with `]-` removed). Math, tables, pseudocode and the five
figures render correctly.

## Lab 10a — per problem

- **P1** — agree.
  - Solution 1: G − (u→v), Dijkstra from s and from v, min{d_s(t), d_s(u) + w + d_v(t)}, correctness both ways. The
    path rule with ties going to d_s(t) gives a simple path, and the argument is correct. The cycle test
    d_v(u) + w ≥ 0 is right.
  - The one-run variant: two layers, crossing edge of weight 0, then + w. It is valid because every (s,0)→(t,1) path
    crosses that edge exactly once.
  - Solution 2 (re-inserting Dijkstra on G unchanged), claims 1–5 re-derived:
    - until u is extracted the run is Dijkstra in G − uv, so u is extracted with δ(s,u);
    - u is extracted at most once;
    - k_{i+1} < k_i only at the step from u to v;
    - each vertex is extracted at most twice;
    - every extraction after u's is final;
    - O(E log V);
    - stopping at t's first extraction is wrong.
  - Example graph, run table, trap numbers (17/25/21, real 7): all correct.
- **P2** — agree. The meeting time at t is max{δ(p,t), δ(q,t)}: Dijkstra ×2 plus a scan. The directed case needs no
  reversal. Both traps are real, the figure numbers are correct, and T(t) ≥ δ(p,q)/2 holds.
- **P3** — agree.
  - (a): ℓ = n₂ + 1 and E ≤ (3n−1)/2, so O(n log n).
  - (b): the split-root dag H with n + 1 vertices, the u′/v′ formula with u = v special-cased, and the proof.
  - The closed form, with L defined as the cheapest way down to a leaf of T_x plus that leaf's loop edge.
  - Corner cases: δ(r,v) = D(v), δ(u,r) = L(u) for u ≠ r, δ(u,u) = 0.
  - The Ω(n) adversary for one query, root detection from the bare graph, and all D/L numbers and distances on the
    handout tree.

## Lab 10b — per problem

- **1(a)** — agree. The lemma and its proof are right. Column u and row v never change, and in-place updating is safe
  because the bracket w′ + dist[v,u] is a cycle of nonnegative length. The Θ(V²) optimality remark holds. The Ch 9
  example (six changes, the rows as stated) is correct.
- **1(b)** — agree. The array is correct iff dist[u,v] ≤ w′(u→v); both directions of the proof are right, and so is
  the example (3→2 with 0, −2 or −3; 2→3 = 2).
- **1(c)** — agree.
  - CheckAPSP: three tests per source, with reachability along tight edges, which handles zero-length cycles. The
    proof is correct, and O(V(V+E)) is the asked O(VE) in the §9.2 convention.
  - The stronger claim "correct ⇔ δ′(u,v) = dist[u,v]" is true. Its proof is correct for both directions of change,
    and it agrees with my own criterion δ_{G−uv}(u,v) ≤ w(u→v).
  - The O(V+E) slack/tight-search test from u is correct, and so is the shortcut dist[u,v] < w ⇒ correct.
  - Example: raising 3→2 or 4→3 changes nothing, raising the other four edges breaks the array; the slack is 1.
  - Zero-cycle figure: the labels 0, 1, 0, 1 versus the true 0, 5, 0, 5 are correct, and both tempting tests are
    fooled as described. Each of them is right in graphs without zero cycles; I proved this for the out-neighbor test
    and confirmed both empirically.
- **1(d)** — agree.
  - G = H + u + v with 0-edges x→u and v→y; w(u→v) = 0, w′(u→v) = M = 1 + total weight.
  - The old array is all zeros, the new one is min{δ_H, M}, and the decoding is right; |V| = n + 2,
    |E| = m + 2n + 1.
  - It proves a reduction, not an unconditional bound, and the page says so correctly.
  - The Johnson remark is correct: one Bellman–Ford to reweight H, then O(n²) to convert back.
  - Figure numbers (M = 7; 2, 3, 1, 3; 7 for q, r → p) are correct.
- **2(a)** — agree. The −ln weights, MaxCurrency = e^{−dist(1,i)} (0 if unreachable, 1 for currency 1), Bellman–Ford
  from 1 in O(n³), and the log-free version all check out; the example gives (1, 120, 1.2).
- **2(b)** — agree. Bellman–Ford from a super-source with n rounds, and the reason for it: zero rates. Floyd–Warshall
  with a negative diagonal, or max-product with M[i,i] > 1, also works; everything is O(n³).
- **2(c)** — agree. The pseudocode is correct and so is its proof:
  - no false positives;
  - a tense edge exists when there is arbitrage;
  - the pointer walk cannot reach Null;
  - n steps land on the cycle;
  - pointer cycles are negative;
  - the reversed list is in trading order.

  The trace numbers and the returned € → $ → ¥ → € are correct. The diagonal and zero-rate conventions are stated,
  and the float remark is correct (left-to-right evaluation).

## Changes (before → after, why)

lab-10a.md:
1. Notation box: "Dijkstra is the version of the book and of the October 27 lecture" → "… the version of the book".
   Why: no source available to me confirms what the Oct 27 lecture presented (algo-facts only says shortest paths are
   lectured the week of Oct 26), so I removed the unverifiable claim.
2. Solution 2, time: "the lecture's bound with a factor 2" → "Dijkstra's usual bound with a factor 2". Same reason.
3. Abstract and P3(b) **Answer** line: "D(v) − D(u) if u is an ancestor of v, and L(u) + D(v) otherwise" → "… if u = v
   or u is an ancestor of v, …". Why: with the strict reading of "ancestor", u = v would fall into the second case and
   give L(u) + D(u) > 0 instead of 0. The displayed formula already had "(or u = v)", but the two cheat-sheet lines
   did not.
4. P3(b), O(1) query: "(u is an ancestor of v iff u comes before v in preorder and after it in postorder)" → "(u = v
   or u is an ancestor of v iff u comes no later than v in preorder and no earlier in postorder)". Why: the strict
   test misses u = v, which the formula needs. The check script already used ≤/≥ (consistent with Ex 8.1's text).

labs_10a.py: relabelled the O(1)-query check to state the non-strict test as now on the page, and added a check
that L(u) + D(u) > 0 = δ(u,u) for every u of the handout tree (the u = v case matters). Re-run: ALL OK.

lab-10b.md:
5. Frontmatter description: "(one search from u suffices)" → "(one search from u suffices, since the array was right
   for the old weight)". Why: next to "any array is checked", the parenthetical read as if it held for arbitrary arrays.
6. 1(d) "Why the two directions differ": "In the construction, every old shortest path between vertices of H uses
   u→v" → "… every old distance between vertices of H is 0, the length of the route through u→v". Why: false when H
   has 0-weight paths (allowed, since H has nonnegative weights); then an old shortest path can stay inside H.

labs_10b.py: unchanged (no checked claim changed). Re-run: ALL OK.

## Remaining doubts

- None on the mathematics.
- The handout's (c) asks for O(|E||V|). The page gives O(V(V+E)) and notes the §9.2 convention; when E < V an
  O(V²) term is unavoidable for reading the array. A grader should accept it. The page also gives the O(V+E) test.
- 10a Solution 2 relies on a "modified/unmodified algorithm" argument rather than a pure black box. That is what the
  handout's second hint asks for, and the page proves the bound, so I consider it full credit.
- Nothing fixed here appears verbatim on pages I was not assigned. Ex 8.1's Answer line uses the same "if u is an
  ancestor of v" shorthand without "or u = v". Its displayed claim and its ≤ test include u = v, so it is at most a
  wording nit for the coordinator.
