# Review R12 — Algorithms Chapter 6 (depth-first search), its concept pages and exercises (2026-10-20)

Method: read every page in full (figure captions and both figure scripts included); compared sections, pseudocode,
lemmas and examples with the book (ch06.txt, and every relevant page of ch06.pdf rendered with pdftoppm, book p. =
PDF p. + 224; Figure 5.7 from ch05.pdf); re-entered the book's graphs from the rendered figures (Fig. 6.4/6.13 graph,
24 edges; Fig. 6.6 dag, 23 edges; Fig. 6.20, 22 edges; Fig. 6.21, 23 edges) and compared them edge by edge with the
check and figure scripts; re-derived by hand the alphabetical traversal of the 16-vertex graph (all 32 times, edge
classes 14/2/5/3), phase 1 of Kosaraju–Sharir (b e f g a m i n j l o k h d c p), the Tarjan low table, the weighted-dag
LLP values (13, 11, −∞, 7, 6, 4, 0; shortest 10; greedy 11), the concept-page examples, the CutDFS run of the 6.21
figure, the Tarry2 walk, the 128 paths of Fig. 6.20 and the 36-edge LIS dag; re-solved every exercise before reading
its solution; read both check scripts against the pages and ran them; ran tools/check.py on the five prefixes.

## 2-algorithms/06-depth-first-search.md

Checked: DFS/DFSAll and the added-source wrapper; Figure 6.3 pseudocode; definitions of pre/post, active interval,
new/active/finished; the classification table (both readings: state of v when DFS(u) begins, and the interval
order), the on-the-fly tip, loops as back edges; Lemma 6.1 statement and all four implications of the proof;
dag/source/sink; cycle ⇔ back edge ⇔ some u.post < v.post in both directions (proof by the first-starting vertex of
the cycle and Lemma 6.1(d)); IsAcyclic = Fig. 6.7; the two traps; topological order theorem, its proof and the
converse (every topological order is a reverse postorder); TopologicalSort/TopSortDFS, PostProcess, PostProcessDag
and the idiom against Fig. 6.9 and p. 233; rev(G); traps incl. the preorder counterexample; Memoize / DynamicProgramming
= Figs. 6.10–6.11; edit-distance and OBST dependency remarks; the edge-direction warning against book pp. 193–194 and
234–235 and against the Chapter 5 page; LLP recurrence, both LongestPath versions against p. 236–237, the diamond
example; "paths in dags" box and recipe; §6.5 definitions, scc(G) is a dag, one component, O(VE); Lemma 6.2 and proof;
StrongComponents = Fig. 6.15; Lemma 6.3 and proof; the "more is true" lemma behind phase 2; KosarajuSharir = Fig.
6.16 and the Fig. 6.17 run; the phase-ordering trap; low, Lemma 6.4 and proof; FindLowDFS = Fig. 6.18; Tarjan =
Fig. 6.19 and the table; the at-a-glance table, Summary and exam box against the graph-reduction rubric. All claimed
book errors verified on the rendered pages (list below).

Changes:
1. §6.0. Before: "the number of trees depends on the order of the wrapper's loop, and can be anything from 1 to V".
   After: "depends on the graph and on the order of the wrapper's loop, and can be anything from 1 to V, even for a
   graph that looks "connected"". Why: as written it suggests every graph can give any count (a strongly connected
   graph always gives one tree); the book says "depending on the structure of the graph and the order".
2. §6.2. Before: "(The book proves (3) ⇒ (1) here and gets the converse from the topological-sort argument of §6.3.)"
   After: "(The book proves only (3) ⇒ (1) here. The converse also follows from §6.3: if every edge had
   u.post > v.post, reverse postorder would be a topological order, which a graph with a cycle cannot have.)"
   Why: the book never states the converse; the old sentence attributed an argument to it.
3. §6.4 warning box: added "(The book's own Figure 6.12, the edit-distance dag of this chapter, reuses the picture of
   Figure 5.7 unchanged, so its arrows still point Chapter 5's way.)" Why: Fig. 6.12 (p. 236) is the same
   picture as Fig. 5.7 (p. 194), whose edges are (i−1,j)→(i,j) etc. by the Chapter 5 text; a student reading Chapter 6
   sees a figure that contradicts the chapter's stated convention (p. 235 also describes the OBST graph with
   Chapter 5's "rightward and upward" edges). Sources sentence extended accordingly.
4. Lemma 6.3 proof. Before: "y is a descendant of v, so v.pre < y.pre". After: "y is a descendant of v (possibly v
   itself), so v.pre ≤ y.pre". Why: y = v is allowed (an edge into the root of C); the conclusion x.post > v.pre is
   unchanged. (The book has the same slip.)
5. §6.6 FindLow. Before: "(the book's FindLow; here the clock counts …)". After: "(the book's FindLow, whose wrapper
   is DFSAll with the clock set to 0 — the book prints its second loop indented inside the first; here the clock
   counts …)". Why: new book error found (p. 243, Fig. 6.18: the second "for all vertices v" is nested in the first).
   As printed, on vertices a, b, c with b→c, c→b the sink component {b, c} ends with low < pre for both vertices, so
   Lemma 6.4 finds no root. Sources' list of corrections extended. New check in a06.py (find_low_printed).
6. Abstract and Summary. Before: "Kosaraju–Sharir (search rev(G), then search G in reverse postorder)". After: "… then
   search G in the reverse of that postorder". Why: "reverse postorder" alone reads as reverse postorder of G, which is
   exactly the mistake the page's own trap warns against.

## concepts/depth-first-search.md, topological-sort.md, strongly-connected-components.md

Checked: definitions, why-it-works arguments (incl. "v.pre < u.post always, so u.post < v.post only for back edges"),
recipes against the rubric (−½ for DFS when WFS suffices), traps, examples recomputed by hand (a 1/8 … e 9/10 and its
edge classes; a 1/10 … f 11/12, postorder e d b c a f, preorder traps; components abc/def/gh, phase 1 b c a e h g f d,
searches from d, g, a). No changes.

## concepts/dynamic-programming-on-dags.md

Checked: the pattern box, LLP, why-it-works, traps (incl. the convention trap), the LIS-as-longest-path example
(10 vertices, 36 edges counted by hand, LLP(0) = 5, answer 4).
Change: recipe step 3. Before: "longest (shortest) path in a dag by dynamic programming in topological order". After:
"… by dynamic programming (LLP above, evaluated in postorder)". Why: LLP(v) is defined toward t and must be evaluated
in reverse topological order; the old wording contradicts the page's own definition box and convention trap.

## 2-algorithms/06-depth-first-search-exercises.md

Checked every statement against book pp. 244–251 (paraphrases faithful; the 6.6 "u ≠ v" convention is stated) and
every solution: 6.0 (a)–(d); 6.1 (a), (b) incl. uniqueness of the order, (c); 6.2 (a), (b) in rubric format, 20g > 19n;
6.3 jump-over characterization, both directions, the sweep invariant (far ≥ i always, so far ≤ i ⇔ far = i), the
Fig. 6.20 data and the 11/11 split of its edges; 6.4 (a), key fact, i, ii both directions, the corrected statement,
the 4-cycle BFS example, low recurrence and CutDFS (parent test, simple graph); the Fig. 6.21 run (pre/low values in
the caption recomputed by hand); 6.5 (a)–(d) and the "parent edge counted" trap (cut test survives because added
values are ≥ v.pre); 6.6 closure, the essential-edge proof for dags, the 2-cycle counterexample, the (c) algorithm,
its minimality argument and the counting formula ∏(|C|−1)!·∏|C||C'| with the uniqueness characterization; 6.7 the
literal pseudocode, (a)–(g) with the red-arc counts; 6.8 the 11-step walk, green tree, labels, why it is no DFS tree;
6.9 (a), (b) both bounds; 6.10 BFS facts for the book's lazy queue version, IsBFSTree/Lift, both directions,
the example; (a) and (d) both directions; 6.11(a) graph, topological orders, examples, the one-temporary
serialization; 6.12 ES/CT/LS and the critical-path variant (LS* = CT − heaviest path from v ≥ LS); 6.13 (a)–(e), the
DP-rubric items, evaluation orders, 128 = 2·8·4·2 counted by hand. Rubric format respected (graph/problem/black box/
time in input parameters for 6.2, 6.9, 6.11; named function + recurrence + memo + order + time for 6.12, 6.13).
No changes.

## Check scripts

a06.py: transcriptions compared line by line with the page's pseudocode (DFS with clock, IsAcyclic, TopologicalSort
with as_printed flag, PostProcess, PostProcessDag, both LongestPath versions with as_printed flag, KosarajuSharir,
FindLow, Tarjan); the example data (G16, D16, WD/W, T6, D5, S8, LIS array) equal my re-entry from the figures; the
page strings it asserts are the ones on the page. Added one check (FindLow with the book's nested loops). 94 OK,
ALL OK (a06.out saved).
a06x.py: implementations match the page (STCutVertices, CutDFS/BridgeDFS, TransitiveReduction, Tarry, TarryFast,
Tarry2, OnlyThisBox, MinSmash, IsDFSTreeUndirected, IsBFSTree, IsDFSTreeDirected, Serialize, ES/LS, the 6.13 DPs);
F20_E and F21_E equal the book figures edge for edge. Unchanged; 80 OK, ALL OK (a06x.out re-saved, identical).
tools/check.py --only on the five prefixes: OK.

## Book errata (confirmed on the rendered pages)

| page | as printed | should be |
|---|---|---|
| 233, Fig. 6.9 | TopSortDFS: `clock ← TopSortDFS(v, clock)` in the loop | `TopSortDFS(w, clock)` |
| 233 | PostProcess: `if v is unmarked` | `if v.status = New` |
| 233 | PostProcessDag: `PostProcessDagDFS(s)` | `PostProcessDagDFS(v)` |
| 236 | memoized LongestPath: `return v.LLP` indented inside `if v.LLP is undefined` | at the outer level |
| 238 | "every back edge joins two edges in the same strong component" | "two vertices" |
| 242 | Tarjan's algorithm "identifies a source component of G" first | a sink component |
| 243, Fig. 6.18 | FindLow: second `for all vertices v` nested inside the first | the two loops consecutive (new) |
| 246, Ex. 6.4(b)ii | "…iff at least one descendant of each child of v is a neighbor of some proper ancestor of v" | iff some child of v has no descendant adjacent to a proper ancestor of v (printed text = condition for NOT a cut vertex) |
| 247, Ex. 6.6(b) | unique transitive reduction "if and only if" G is acyclic | "if" only; the 2-cycle u⇄v is cyclic with a unique reduction |
| 250, Ex. 6.11 | "either a=0; b=1 or a=0; b=1" | "a=0; b=1 or b=1; a=0" |
| 250, Ex. 6.11 | x,y = x+y,x-y "requires two temporary variables" | one: t=x; x=x+y; y=t-y |
| 252, Ex. 6.16 | "union of all directed paths in G from u to v" | "from u to w" |
| 252, Ex. 6.16 | "v ∈ reach(u) and w ∈ reach(x)" | "w ∈ reach(v)" |

Minor (not on the pages): p. 235 Fig. 6.10 DFS(v) calls PreVisit(x)/PostVisit(x) (should be v); p. 236 Fig. 6.12 is
Fig. 5.7 reused (Chapter 5 edge direction), and p. 235 describes the OBST dependency graph with Chapter 5's
"rightward and upward" edges; p. 240 Lemma 6.3 proof "v.pre < y.pre" (≤ when y = v); typos p. 228 "assigns assigns",
p. 231 "no incoming vertices", p. 234 "each each", p. 236 "easy to if the input graph".

## Remaining doubts / notes for the coordinator

- Chapter 5 page (content/2-algorithms/05-basic-graph-algorithms.md, line 67, not mine, not edited): "A dynamic
  programming evaluation order is an order in which every subproblem comes after its predecessors (…; Chapter 6 calls
  it a topological order)". With Chapter 5's edge direction the evaluation order is indeed a topological order, but
  Chapter 6 points the edges the other way and calls it a *reverse* topological order (p. 235: "We previously called
  the reverse topological order an evaluation order"); the Chapter 6 page says so. Suggested: "(it is a topological
  order of this graph; Chapter 6, whose dependency edges point the other way, calls it a reverse topological order)".
- Exercise 6.11(a) assumes a serialization without temporaries runs each assignment exactly once (no algebraic
  tricks such as a=a+b; b=a−b; a=a−b); standard reading, left as is.
- 6.10(b)–(d) are O(VE); faster methods exist (the page says so). Correct as is.
- 6.2, 6.9 and 6.13 are classic homework-style problems; no HW8 handout exists yet (algo-facts), so left in.
