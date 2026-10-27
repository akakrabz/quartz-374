# Review R15 — Algorithms Chapter 7 (minimum spanning trees), its concept pages and exercises (2026-10-25)

Method: read every page in full (figure captions included; SVG stripped for reading, all nine figures rendered with
shot.py and looked at); compared sections, lemmas, proofs, pseudocode and examples with the book (ch07.txt, and every
page of ch07.pdf rendered with pdftoppm, book p. = PDF p. + 256; Figs. 7.1, 7.3, 7.4, 7.5, 7.6 and the Ex. 7.9 figure
at high resolution); re-entered the Fig. 7.1 graph (12 edges) and the Ex. 7.9 graph from the rendered figures and
compared them edge by edge with both check scripts and the figure data; re-derived by hand the MST (42), the partial
forest's safe/useless/undecided edges, the cut exchange 61 → 57 → 52 → 42 (each step is a cut exchange: S = {a,b,c,d},
{a,c}, {f}), Borůvka's two phases and picks, JarníkBestFirst's 12 extractions from g, the vertex-version priority table
(7 DecreaseKeys), the Kruskal label table (24 Finds, 7 relabelings), the 8-vertex path (3 phases), the concept-page
square and union-find examples; re-solved every exercise before reading its solution; read both check scripts against
the pages and ran them; ran an independent simulation of the Ex. 7.10 construction (book pseudocode, recursive Find).

## 2-algorithms/07-minimum-spanning-trees.md

Checked: definition; Lemma 7.1 and proof (e'' ≠ e, w(e'') ≥ w(e') ≥ w(e), equality from minimality); converse
remark; ShorterEdge = lexicographic key (book p. 259 line by line); the perturbation note (ordering preserved for
ε < gap/E, w(T*) − w(T) < εVE); generic algorithm, invariant, safe/useless/undecided definitions; Lemma 7.2 statement
and proof (strong form, ∅ ≠ S ≠ V); Lemma 7.3 and the "useless but in the MST" example F = {ab, bc}; generic
correctness box; cut-exchange template; Borůvka and AddAllSafeEdges = book p. 262; running-time box; the triangle
tie-breaking trap (with keys x<y<z: xy, xy, xz); JarníkBestFirst (each edge inserted exactly once, queue invariant);
Fig. 7.5 transcription; DecreaseKey count (at most one per edge, none at s — the book's "at most twice" is loose, not
wrong; confirmed); the queue table; Fibonacci-heap footnote; Jarník ≠ Dijkstra trap; Kruskal's test and proof
(edge is the lightest safe edge of all); Kruskal = book p. 267; labeling union-find analysis; α-footnote; traps;
at-a-glance table; Summary; exam box (anchor 0-toolkit/06#13-graph-reductions exists). History paraphrased, no
copied sentences.

Changes:
1. §7.3 running-time box. Before: "Starting from V components, there are at most ⌈log₂ V⌉ phases." After: "… at most
   ⌊V/2^i⌋ are left after i phases, so there are at most ⌊log₂ V⌋ phases. (The book says ⌈log₂ V⌉, which is also an
   upper bound but is never reached unless V is a power of 2.)" Why: c → ⌊c/2⌋ per phase gives ⌊log₂ V⌋; the exact
   worst case for V = 2..8 is ⌊log₂ V⌋ (new check).
2. §7.3 example. Before: "On the example, two phases suffice, fewer than ⌈log₂ 7⌉ = 3". After: "On the example the
   algorithm takes two phases, the most that any seven-vertex graph can need (⌊log₂ 7⌋ = 2; at worst 7→3→1)". Why: no
   7-vertex graph can take 3 phases; the old sentence presented the worst case as a lucky case.
3. §7.3 "MST algorithm you want": "far fewer than ⌈log₂ V⌉ phases" → "⌊log₂ V⌋" (consistency).
4. §7.2 Ties trap. Before: Lemma 7.2 weakens to "**some** MST contains each safe edge". After: "each safe edge lies in
   **some** MST" — not necessarily all of them in the same one. Why: the old wording also reads as "one MST contains all
   safe edges", which is false (the page's own Borůvka triangle).
5. §7.2 Disconnected-graphs trap. Before: "Jarník spans only the component of its start vertex." After: "Jarník's
   best-first version spans only the component of its start vertex; the vertex version (§7.4) instead extracts a vertex
   of priority ∞, whose edge is Null, whenever a component is finished, and grows the next tree from it." Why: Fig. 7.5's
   loop runs |V| − 1 times regardless; on a disconnected graph its non-Null edges form the minimum spanning forest
   (new check).
6. §7.4 table row "unsorted array of vertex priorities (not in the book)" → "(the book's Exercise 7.7)"; and "The plain
   array wins for dense graphs, E = Θ(V²)." → "For dense graphs, E = Θ(V²), the plain array of the last row reaches the
   same O(V²) with no special data structure, and beats a binary heap's O(V² log V)." Why: it is the book's Ex. 7.7;
   "wins" was unclear (it ties the Fibonacci heap asymptotically).
7. Sources: lists the ⌊log₂ V⌋ correction (book p. 263), the disconnected-graph remark and Ex. 7.7 as the array's source.

## concepts/minimum-spanning-trees.md

Checked: key box, table, why-it-works, template, traps, the square example (Kruskal pq, rs, pr; Jarník from s rs, pr,
pq; Borůvka pq/rs then pr), anchors (check.py), aliases unique site-wide.
Change: table "≤⌈log₂ V⌉ phases" → "≤⌊log₂ V⌋ phases" (consistency with the chapter page).

## concepts/union-find.md

Checked: definition; labels analysis (≤ log₂ n relabelings per element); forest pseudocode (path compression, union by
rank); height ≤ log₂ n under union by rank; Kruskal costs; traps; the 8-element example (12 relabelings, 8 → 7 → 5 → 1,
forest rank 3, recomputed by hand with the page's linking rule).
Change: "Each operation takes O(α(n)) amortized time" → "… (Tarjan, 1975)". Why: the bound was unattributed (Tarjan,
J. ACM 22, 1975). Nothing overclaimed otherwise (the forest is presented as the book's footnote; "at most 4" as a
practical statement).

## 2-algorithms/07-minimum-spanning-trees-exercises.md

Re-solved first, then checked: 7.1(a) (cut at the heaviest edge; Kruskal view; strict version), 7.1(b) diamond
(ux 1, xv 2, uv 3, uy 4, vy 5; MST weight 7); 7.2(a) triangle 1,1,2; 7.2(b): strict cut/cycle lemmas, each condition
alone ⇒ uniqueness (both proofs), counterexamples to "only if" (triangle violates the cut condition at S = {b}; H = ac 1,
ax 2, bx 3, ab 4, bc 4 has unique MST {ac, ax, bx} of weight 6 — every tree with ab or bc weighs ≥ 7 — and cycle abc
has two heaviest edges; H satisfies the cut condition since a cut avoiding ac, ax, bx is trivial), the corrected
characterization (both directions) and its examples; 7.2(c) two Kruskal runs (the contradiction f ∈ F' before f is
examined); 7.3(a)–(c) (reverse-delete invariant, O(E²)); 7.4(a)(b) (negative weights handled; the extension argument);
7.5(a)(b) all four cases; 7.6(a) one-swap claim (both cases of the symmetric-difference argument), Heavy table, the
Fig. 7.1 table 8/5/3, 10/3/7, 14/12/2, 18/12/6, 26/16/10, 30/16/14 → 44; 7.7; 7.8(a) radix-sort pass, V' ≤ V/2;
7.8(b) bound, k*, the lower-bound argument (2^{L/2} ≥ L/2), E log log V; 7.8(c); 7.9 figure (re-entered: max spanning
tree 12, 11, 10, 9, 8, 6; path 10, 12, 9, 11; width 9; edges ≥ 9 form exactly that path), (a), (b) in rubric format,
(c)i, (c)ii both directions; 7.10: pseudocode = book p. 272, Find cost accounting, FindSafeEdges O(E), the hint
(depth ≤ 1), the counterexample, union-by-size analysis.

7.10 counterexample: re-implemented independently (scratchpad sim710.py: book's recursive Find, adversarial Union,
attach u_i to the deepest vertex, ties by smallest index). Results: V = 2^13: 90,099 Find calls = 11.0E (matches the
page); V = 2^14: 11.5E; V = 2^15: 12.0E; the deepest vertex when u_i is handled has depth exactly k for i = 2^j − 1 and
k + 1 otherwise (k ≤ 14), so the "depth ≥ k" claim holds in every simulated case. I found no general proof for the
"deepest vertex" adversary; the general statement (some tree forces Θ(V log V)) is still true by Tarjan–van Leeuwen's
tight lower bound for path compression with naive linking (attach u_i to the deepest vertex of the embedded binomial
tree, the classic sequence).

Changes:
1. 7.10, counterexample paragraph. Before: "This is the classic worst case of path compression without balanced
   linking: the compressed tree keeps a vertex at depth k or more, so …". After: "This is the classic worst case of path
   compression with arbitrary linking, which Tarjan and van Leeuwen (1984) showed can cost Θ(n log n) for n links and
   n Finds. Here the compressed tree keeps a vertex at depth k or more (a simulation of the book's pseudocode confirms
   this for every V up to 2^13; we give no proof for general k), so …". Why: the depth claim was asserted without proof
   or source; now attributed and its status stated.
2. 7.10, "What is true". Before: "(With arbitrary linking the total is still O(E log V), but the proof needs the general
   amortized analysis of path compression, which we omit.)" After: the reduction (at a call's start every non-root is a
   depth-1 leaf and only roots are linked, so each Find = 1 step + a Find in the forest of the c roots) plus Tarjan and van
   Leeuwen's Theorem 4, O(n + m log_{2+m/n} n) for m Finds and ≤ n − 1 links with arbitrary linking; n = c, m ≤ 4c gives
   O(c log c), so each call is O(V + c log V) and the union-by-size sum applies. Why: the claim was true but neither
   proved nor cited (the task asked to check this). Bound confirmed from the paper (J. ACM 31(2), 1984, Thm. 4).
3. 7.10: "at most ⌈log₂ V⌉ + 1 calls to FindSafeEdges" → "⌊log₂ V⌋ + 1" (consistency; new check).
4. Sources: full reference to Tarjan–van Leeuwen.
No other changes: 7.1–7.9 are correct as written; the two claimed book errors are confirmed (table below).

## Check scripts

a07.py: transcriptions compared with the page (ShorterEdge, CountAndLabel/AddAllSafeEdges, JarníkBestFirst,
JarníkInit/Loop, Kruskal with labels and forest, the generic algorithm); EX graph = Fig. 7.1; the page strings it
asserts are on the page; figure roles parsed from the figure HTML. Changed: phase bound ceil → floor (and ⌊V/2^i⌋ after
i phases); new exhaustive worst-case check for V = 2..8 (= ⌊log₂ V⌋, all path weightings); page-string checks for the
new bound, the 7-vertex sentence, the Ex. 7.7 row and the disconnected-graph sentence; new check that the vertex
version on disconnected graphs extracts one ∞-priority vertex per further component and returns the minimum spanning
forest. 67 OK, ALL OK (a07.out saved).
a07x.py: implementations match the page; E71/E9 equal the book figures; did not read the page at all — added five
page-string checks (7.1(b), 7.2 graphs, the 7.6 table and 44, the 7.10 numbers, the TvL citation and the 2^13 hedge)
and a check of ≤ ⌊log₂ V⌋ + 1 FindSafeEdges calls. 72 OK, ALL OK (a07x.out saved).
tools/check.py --only 2-algorithms/07,concepts/minimum-spanning-trees,concepts/union-find: OK. Figures unchanged (no
assemble needed).

## Book errata (confirmed on the rendered pages)

| page | as printed | should be |
|---|---|---|
| 268, Ex. 7.2(b) | unique MST "if and only if" (every cut has a unique lightest crossing edge) and (every cycle has a unique heaviest edge) | "if" only — each condition alone suffices. Not "only if": triangle ab 1, bc 1, ca 2 (cut {b} fails) and ac 1, ax 2, bx 3, ab 4, bc 4 (cycle abc fails) have unique MSTs. Correct: an MST T is unique iff every non-tree edge is strictly heavier than every edge on its T-path |
| 272, Ex. 7.10 (with fn. 8, p. 271, "those details don't matter here") | "each call to FindSafeEdges and AddSafeEdges requires only O(E) time" | true for FindSafeEdges; false for AddSafeEdges when Union links either way (Θ(V log V) on a tree, E = V − 1). With union by size O(V + c log V) per call; the O(E log V) total holds with either linking (arbitrary: Tarjan–van Leeuwen 1984) |
| 263 | "below the worst-case ⌈log₂ V⌉" iterations | ⌊log₂ V⌋ (⌈·⌉ is an upper bound, not attained unless V is a power of 2) — new, minor |
| 265 | DecreaseKey "at most twice for each edge" | at most once per edge (none for edges at s) — loose, not wrong |

Minor (not errors, or typos): p. 262 Borůvka's `while count > 1` never ends on a disconnected graph (the chapter assumes
connected graphs; on the page as a trap); p. 265 "called O(V) times once for each vertex except s" (missing colon);
p. 259 "Because the input graph undirected" (missing "is"); p. 261 "Łukaziewicz" (spelled Łukaszewicz earlier on the
same page); p. 263 "Lobermand" (Loberman); p. 267 fn. 6 "Ackerman" (Ackermann); p. 265 "Jarnik's" (no accent);
pp. 270–271 Ex. 7.9 "a undirected" twice.

## Remaining doubts / notes for the coordinator

- 7.10: the "deepest vertex" construction's depth ≥ k property is verified by simulation (check script to V = 2^13,
  my independent run to V = 2^15) but not proved in general; the page now says so. The correction itself (the book's
  O(E) per call is false) does not depend on it: Tarjan–van Leeuwen's lower bound gives such trees.
- Whether AddSafeEdges is O(E) per call with union by size + path compression is not settled here (O(V + c log V) is
  proved; the page claims nothing more).
- Trap "an algorithm must break all ties with one consistent rule" is the book's prescription; strictly only
  algorithms that add several edges at once (Borůvka) need it — Kruskal and Jarník return an MST with any tie-breaking.
  Left as is.
- 7.3(c): O(E²) is the straightforward bound; faster reverse-delete implementations exist (dynamic connectivity), not
  mentioned. Fine for the exercise.
- /home/claude/work/algo/errata-notes.md (not edited): the Ch 7 entries are confirmed; add the new p. 263 ⌈log₂ V⌉ item
  and the trivial typos above; the 7.10 entry can cite Tarjan–van Leeuwen for the O(E log V) total.
- No statement fixed here appears on another page (2-algorithms/05 §5.6 "Prim" row is consistent; index pages only
  list topics).
