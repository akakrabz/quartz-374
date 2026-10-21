# Review R11 — Algorithms Chapter 5 (basic graph algorithms), its concept pages and exercises (2026-10-20)

Method: read every page in full (figure captions and figure scripts included); compared every section, definition,
pseudocode block, lemma, table and example with the book (ch05.txt, and ch05.pdf pages rendered with pdftoppm, PDF
p. = book p. − 186, at 110–500 dpi for pseudocode, figures and proofs); re-derived every proof, count, running time
and exercise solution before reading the page's version; recomputed the key numbers with an independent script
(scratch, not the writers' code): S&L k = 1..8 (None 10 7 5 5 5 4 3), maze 8, Vidrach 5, Seashells as drawn
unsolvable / repaired 4, K4 Eager vs DFS trees, Hierholzer parity claim, coupon readings, bag sizes on K_n, 7 × 7
DFS tree a Hamiltonian path; read both check scripts against the pages and ran them; ran tools/check.py.
Graph-reduction rubric paraphrase compared line by line with rubrics.txt ("Standard graph-reduction rubric").

## 2-algorithms/05-basic-graph-algorithms.md

Checked: §5.1 history (dates, Euler/Hierholzer, Cayley/Sylvester/Kőnig); §5.2 definition, V/E convention and bounds,
vocabulary table (cycle on ≥ 3 vertices is a correct precision of "no subgraph is a cycle"), subgraphs/components/
trees, handshake; §5.3 Fibonacci and edit-distance dependency graphs ((m+1)(n+1) vertices, 3mn edges), 4-disk Hanoi
(81 vertices, 120 = 3(3^4 − 1)/2 edges, 15), DFA emptiness O(|Q||Σ|), subset-construction edges; §5.4 example graph,
figure (list, matrix, 8 edges), adjacency array (offsets 1 3 6 9 12 14 15 16), Table 5.1 = book; §5.5 RecursiveDFS /
IterativeDFS / pair version = book; reverse-push claim (IterativeDFS with each list pushed reversed marks in
RecursiveDFS's order and builds its tree — true, simulation argument + a05.py); Lemma 5.1 statement and both proof
parts (parent edges distinct because parent(v) is marked before v); analysis († ≤ V, ⋆⋆ = Σ deg over marked = 2E(comp),
⋆ ≤ 2E + 1, directed E + 1, matrix O(V² + ET)); stack and queue traces on G (15 pairs, b in 3 times, trees, BFS
distances 1 1 2 3 4); §5.6 table, 7 × 7 grid figure (169 = 2·84 + 1, depths 48/6/8), BFS intuition, best-first
O(V + E log E), the three priority rules and what they compute, WFSAll, CountComponents, CountAndLabel (returns 2 on G;
book's literal LabelOne returns V), directed reachability and the a→b, c→b example, directed "Prim" counterexample
(5 vs 4); §5.7 flood-fill write-up (n² vertices, ≤ 2n(n − 1) edges, O(n²)), 8 × 8 figure (57 edges, region 9),
template = rubric (3 = 1+1+1 with −½ for "directed"; 3 = 1+2; 2 with −1 slower, −½ more specific, −1 re-explaining;
2 for time in input parameters; the two named common mistakes), parity reduction H (2V vertices, 2E edges) and its
figure; summary; exam box.

Changes:
1. §5.2 trap. Before: "$O(E)$ is not $O(V+E)$: a graph may have isolated vertices, and then $E < V$." After: "…:
   isolated vertices make $E < V$ possible (a graph with no edges has $E = 0$)." Why: the implication as written is
   false (K5 plus one isolated vertex has E = 10 > V = 6); wording now matches concepts/graphs.
2. §5.3 dependency graphs (also requested by the coordinator from the Ch 6 review). Before: "… after its predecessors
   (§3.4; Chapter 6 calls it a topological order)." After: "… (§3.4). With the edges pointing this way — from a
   subproblem to the ones that need it — that is a topological order; Chapter 6 points every edge the other way, from
   a subproblem to the ones it needs, and so calls the same order a *reverse* topological order." Why: book pp. 234–235
   (Ch 6) draw the edges from a subproblem to the ones it needs and say "reverse topological order" ("We previously
   called the reverse topological order an evaluation order"); the site's Ch 6 page says the same. a05.py edit-distance
   check extended: row-major order is a topological order of the Ch 5-direction dag, and the page text says so.
3. §5.5 trap (EagerWFS). Before: "On a triangle abc searched from a, EagerWFS always builds the star ab, ac, while every
   depth-first tree is a path." After: "… EagerWFS always makes a the parent of both b and c (tree ab, ac), while every
   depth-first tree from a gives a a single child (tree ab, bc or ac, cb)." Why: on three vertices the star ab, ac is
   itself a path (b–a–c), so the stated contrast was empty; the real difference is the rooted shape. a05.py check
   rewritten to test exactly the two tree sets and a's child count, plus the page text.
4. §5.7 flood-fill write-up, "The algorithm". Before: "Run whatever-first search in G from (i,j), and give each vertex
   the new color when it is marked." After: "Run whatever-first search in G from (i,j), then give every marked vertex
   the new color. (The book recolors each vertex the moment it is marked, which comes to the same; recoloring
   afterwards keeps the search a black box.)" Why: this is the page's model rubric answer, and the template and trap
   right below it say not to modify the standard algorithm. a05.py: the black-box variant (random bag) is compared with
   the brute-force region on the 1500 random maps.
5. Summary. Before: "Each vertex enters the bag up to $\deg(v)$ times, …". After: "… ($s$ once more), …". Why: s can
   enter deg(s) + 1 times (the analysis section says so).
6. Sources, list of corrections: added "in a directed graph the parent edges are parent(v)→v (p. 205 prints
   parent(v)→p)" — a typo seen on the rendered page that the text had silently corrected.

Not changed (noted): "The bag … can hold up to 2E + 1 pairs" — correct as an upper bound (at most 2E + 1 ever go in;
after the first take at most 2E are in it at once); K_n with a queue does hold Θ(E) at once (K12: 121 pairs, E = 66),
so the point of the trap stands.

## concepts/graphs.md, concepts/whatever-first-search.md

Checked: definitions and bounds (directed bound labeled "no loops"), handshake, recipe, traps; 3-disk Hanoi (27, 39,
degrees 3·2 + 24·3 = 78, corner distance 7); WFS key box, table, "why it works", template, traps; K5 example
(21 pairs, 4 + 1 entries, stack → Hamiltonian path, queue → star). No changes.

## concepts/graph-reductions.md

Checked: definition, the undecidability analogy (direction of both reductions), template = rubric, traps, knight
example (undirected, ≤ 4n² edges, BFS, O(n²); 8 × 8 corner to corner 6; 3 × 3 center isolated).
Change: "On a 3 × 3 board the center square has no knight moves at all, so from a corner it is impossible." → "…, so it
cannot be reached from a corner: the answer is "impossible"." Why: "it" had no clear referent.

## 2-algorithms/05-basic-graph-algorithms-exercises.md

Checked every statement against book pp. 207–216 (rendered figures 5.14–5.17); the skip list (♥ = 5.10(e,f), 22(c),
24, 26(b), 27, 28; confirmed by the extracted markers). Re-solved each exercise before reading the solution:
5.1 (Lemmas A and B, all six links); 5.2; 5.3(a–c) incl. Lemma C; 5.4 (insertion rule, O(n²) linear in a tournament,
shortest-cycle argument, position = 1 + out-degree); 5.5(a,b) (longest trail); 5.5(c) Hierholzer (see change 7);
5.6 (Gray code, d = 3 list, Euler iff d even, Q_0); 5.7 (bridges, (★), DFS orientation proof, O(V + E));
5.8; 5.9(a–c); 5.10(a–d) (stack invariant, push order, K4 queue counterexample for both push orders);
reductions 5.11–5.19 against the rubric — each has an explicit vertex set, edge rule, direction stated (directed for
5.11, 5.12, 5.13, 5.14, 5.15, 5.16, 5.17; undirected for 5.18, 5.19 with the reason), the problem with source and
target(s) and why it answers the question, the cheapest adequate black box (BFS only where move counts matter, WFS for
5.14, 5.16, 5.18, 5.19(c)), and time in n, k, n + m, V + E as appropriate. All are full-credit answers.
Interpretations: Fig 5.15 read on a 500-dpi render — snakes 98→6, 95→71, 79→40, 67→10, 27→17; ladders 3→42, 8→54,
24→86, 50→93, 58→65, 59→81 = the page; the two snakes crossing near 15/26 were read by smooth continuation, and the
other pairing (98→17, 27→6) gives the same answers for k = 1..8, so the numbers do not depend on it. Fig 5.14 maze,
Fig 5.16 five moves (red D2, blue U3, red R3, blue L3, red D1), Ex 5.14 graph (s→w, w→t, w→y, y→x, x→s, y→z, z→t),
Ex 5.15 graph (red cycle s a b t d c, blue c→a, d→s, b→d, t→a), Fig 5.17 graph (ab, bc, ap, bq, pq, qr, qx, qy, rz):
all match the page and the check script.

Changes:
7. 5.5(c), "Parity" paragraph. Before: "… All counts are even at the start, so this holds for every edge the algorithm
   takes: **the first entry appended inside a call made from Walk(v) is v** …". This is false: on a triangle s, a, b
   with Walk(s) taking sa first, Walk(b) called from Walk(a) appends s first, not a. After: defines an *even* moment,
   proves (induction on the number of unused edges) that loops resume only at even moments and that an edge taken at
   an even moment makes the caller's vertex the first entry inside the call, notes the triangle as the reason for the
   condition; the next paragraph now says the loop "resuming at an even moment" calls Walk(w'). The conclusion (a
   valid tour) was right and is unchanged. a05x.py: instrumented Walk checks both properties on 1414 random Eulerian
   graphs, and the triangle counterexample.
8. 5.8, "Depth-first". Before: "… builds exactly the trees that RecursiveDFS builds (it scans each adjacency list in
   reverse order; §5.6)." After: "…, over all orders of the adjacency lists: on the same lists it tries each vertex's
   neighbors in reverse order, so it builds RecursiveDFS's tree for the reversed lists (§5.5)." Why: link pointed to
   the wrong section; wording now agrees with the chapter page's §5.5 statement (same trees only with reversed push
   order / as sets over all orders), which a05.py and a05x.py both check.
9. 5.9(c). Answer before: "On a triangle, EagerWFS always builds a star at s; depth-first search always builds a path."
   After: "On a triangle searched from s, EagerWFS always makes s the parent of both other vertices; depth-first search
   always gives s a single child." Added after the proof: both searches start at s, as in (b) — as unrooted trees all
   spanning trees of a triangle are paths and RecursiveDFS from a can build {as, sb}; on K4 the conclusion holds for
   any start vertices (EagerWFS: star at the start; RecursiveDFS: Hamiltonian path). Same reason as change 3.
   a05x.py: two new checks (triangle from other starts contains the star; K4 any start/order/bag: 4 stars vs 12 paths,
   none common).
10. 5.12. Before: "With k = 1 square 100 is unreachable: every route lands on the snake at 98." After: "… the route is
    forced, and from 93 it lands on 94, 95 (down to 71), 72, …, 79 (down to 40), 41, …, 50 (up to 93) and around again
    forever, never beyond 95." Why: with k = 1 the token never reaches 98. Also added to "Problem": "if n² is not
    reachable from 1, no number of moves suffices". a05x.py k = 1 check now tests the landing set (max 95, no 98).
11. 5.17(b) statement. Before: "… a coupon that lets her use one teleport-way once for free." After: "… a coupon that
    lets her use exactly one teleport-way for free — read here, as the natural meaning of a coupon, as one free use of
    one teleport-way." Why: the paraphrase silently fixed an interpretation. The other reading (every use of one chosen
    teleport-way free) gives different answers on some inputs (found: ways 3–0 cost 4, 1–3 cost 7, 0–2 cost 9, s = 2,
    t = 3: 4 teleports vs 6), so the reading is now stated.

## Book errata (Chapter 5) — final list, each confirmed on the rendered page and by reasoning/code

| page | as printed | should be | status |
|---|---|---|---|
| 191 | "in any directed graph we have 0 ≤ E ≤ V(V − 1)" | ≤ V² (the definition allows u→u; p. 197 says directed matrices may have nonzero diagonals), or "without loops" | confirmed (imprecision) |
| 193 | "an m × n grid of vertices (i, j)" (edit-distance dependency graph) | (m + 1) × (n + 1) grid, 0 ≤ i ≤ m, 0 ≤ j ≤ n (Fig 5.7 is unlabeled) | confirmed (imprecision) |
| 200 | Lemma 5.1 proof: "The prefix path s→⋯→u is shorter than the shortest path from s to u" | "is a shortest path from s to u, shorter than the shortest path from s to v" | confirmed |
| 201 | "adding one more parent edge s→parent(s)" | "v→parent(v)" | confirmed |
| 202 | "Because the priority queue stores at most one copy of each edge" | an undirected edge can be in it once per direction ((b,c) and (c,b) together: triangle ab 1, ac 2, bc 9); ≤ 2E + 1 items, O(log E) unchanged; true for directed graphs | confirmed |
| 204 | LabelOne: body starts "while the bag is not empty" | first line "put v into the bag" (as printed nothing is labeled and CountAndLabel returns V) | confirmed |
| 204 | "WFSAll … puts every edge into the bag once, and takes every edge out of the bag once" | each undirected edge twice (as p. 201 itself says), each directed edge once, plus one start item per component; O(V + ET) unchanged | confirmed |
| 205 | "the directed edges parent(v)→p define a rooted tree" | parent(v)→v | new (typo) |
| 205 | "… we can obtain … a minimum-weight directed spanning tree …" | false: s→a 2, s→b 3, b→a 1 gives 5, optimum 4; min arborescences need Chu–Liu/Edmonds | confirmed |
| 215 | Fig 5.17 caption "the first two turns of a solution" | no solution exists as drawn: x and y are both leaves of the center vertex q, so two tokens would have to leave q in the last turn; with x hung from p instead, 4 turns starting with the book's two | confirmed (argument + exhaustive search) |
| 216 | Ex 5.19(b) "a configuration where both coins are on the same vertex" (three coins) | "all three coins" | confirmed |

## Runs

a05.py ALL OK (73 checks; 3 rewritten/extended, a05.out saved); a05x.py ALL OK (85 checks, 4 new + 1 strengthened;
a05x.out saved); tools/check.py --only 2-algorithms/05,concepts/graphs,concepts/whatever-first-search,
concepts/graph-reductions: OK. No figure changed, so no reassembly or screenshots.

## Remaining doubts

- p. 191: the book writes "(simple) graph" and calls graphs without loops simple, so one can argue directed loops were
  meant to be excluded; listed as an imprecision, not a hard error.
- 5.17(b): the "one free use" reading is the usual one (coupon), but the book's wording allows the other; the page now
  says which it uses.
- 5.10(c): the page's "same trees" argument matches list orders to the run's choices; correct and exhaustively checked
  on small graphs, but terse.
- Ex 5.12–5.19 look like typical course homework/lab problems (number maze, Snakes and Ladders, Vidrach Itky Leda,
  mod-3 walks, red/blue walks, French flag, Judy's teleports, Three Seashells, coins); they are book exercises, which the
  student asked for — flag for the coordinator in case HW8 (graphs, not yet released) reuses one of them.
