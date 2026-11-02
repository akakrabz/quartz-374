# Review R23 — Algorithms Chapter 12 exercises and the concept pages independent-set, graph-coloring, hamiltonian-cycle (2026-10-30)

Method: read the four pages in full (callouts, figure captions); compared statements with the book (ch12.txt; PDF
pages of ch12.pdf rendered with pdftoppm, book p. = PDF p. + 378: pp. 396–397 for Figures 12.13–12.14, 399–402 for
Figures 12.17–12.20, 415–427 for the exercise statements and their ♥/♣/♠ markers); re-derived every proof and every
number; read both check scripts against the pages and ran them. Wrote an independent brute force (own Hamiltonian
cycle search, own encodings of the book's and the repaired 3SAT → DirectedHamCycle constructions) in the scratchpad.

## Book errors — verdicts

- **p. 400–401, §12.11 "From 3SAT": confirmed wrong as printed.** Read precisely: rows are doubly linked; the four
  connectors join both ends of row i to both ends of row i+1 (and n to 1), as the text and Figure 12.19 show; clause j
  uses positions 2j−1, 2j (Figure 12.20 draws 2k vertices per row; the text's (i,0)..(i,2k) is 2k+1). For the 8 clauses
  on a, b, c with (ā ∨ b ∨ c) last (unsatisfiable), my own DFS finds a Hamiltonian cycle in both readings (59 and 56
  vertices). Control: with (ā ∨ b ∨ c) first instead of last, the book's graph is still Hamiltonian (another cheating
  route), so the construction is broken more generally.
- p. 400: text says "a doubly-linked list of 2k vertices (i,0), (i,1), …, (i,2k)" — 2k+1 indices (the figures draw 2k).
  Already on both pages.
- Figure 12.17 (p. 399): the graph is u–v, u–w, u–x, v–x, w–x (five edges, 4-cycle u v x w plus diagonal ux), cover
  {u, x} highlighted in Figure 12.18. The chapter-page writer's report is right: a12c.py transcribed it as uv, uw, ux, vw.
- Figure 12.14 (p. 397) "all valid 3-colorings of a half-gadget, up to permutations of the colors" draws 5; up to
  permutation there are 4 (24 colorings / 6), the two top ones differ by swapping two colors. (Already a check line in
  a12c.py; not stated on my pages.)

## Repaired construction (spacers + hubs) — verified independently

All formulas with n ≤ 3, k ≤ 2 (1996, sampled where > 1500 per (n, k)), plus 300 random with k = 3, 4: H Hamiltonian ⇔ Φ
satisfiable, 0 errors; for k ≤ 2 the number of Hamiltonian cycles equals Σ over satisfying assignments of
Π_j (#true literals of c_j), 0 mismatches. The 8-clause counterexample gives an 86-vertex non-Hamiltonian H. Vertex and
edge counts n(3k+2)+k and 6kn+4n+6k re-derived. The chapter page's "⇐" case analysis (stranded spacer; j = 1 and j = k
end cases through the hubs) re-derived by hand and correct, including clauses with both x_i and x̄_i.

## content/concepts/hamiltonian-cycle.md

Checked: definition, both reductions, sizes, VertexCover isolated-vertex caveat (one edge + isolated vertex, k = 3:
cover exists, 3 cover vertices but 2 chains; "delete isolated vertices, YES if k ≥ vertices left" is right, the book's
H also works for k = n' exactly), variants (in/mid/out split), TSP, traps, example (6 satisfying assignments, 12 cycles,
26 vertices, 60 edges), the figure edge by edge (all 12 highlighted edges and the 12 clause edges match). Agrees with
the chapter page's construction.

- "Separator(s)" → "spacer(s)" (5 places in the text, 1 in the figure caption via tools/figs_a12c.py): the chapter page
  calls the same vertices spacers. Regenerated figures (ham-3sat differs only in caption and the draw order of a few
  non-overlapping lines), assembled the page, previewed in light mode.

## content/concepts/independent-set.md

Checked: definitions, complement relations and their proof, "exactly k" remark, rubric template (⇒, ⇐), traps, example
(9 vertices, 6 conflict edges listed correctly, 15 edges, {a₁, c₂, b̄₃}, 5 satisfying assignments, FFF/TTF/FTT, MVC 6,
complement 21 edges), figure (triangles, all 6 conflict edges, ringed set).

- Figure caption "one vertex per literal" → "one vertex per literal occurrence" (the page's own trap stresses
  occurrence, and a and b̄ each have two vertices in the drawing). tools/figs_a12c.py, regenerated, assembled, looked at
  the figure in light and dark.

## content/concepts/graph-coloring.md

Checked against Figure 12.13 (gadget: ℓ₁u, ℓ₂v, triangle uvw, wy, ℓ₃z, triangle yzT — 10 edges): sizes 3+2n+5k and
3+3n+10k, the ⇒ completion rule in every case, the ⇐ argument, majority-gate behavior, example (2 completions), 31/55 for
the book's formula, kColor padding, 2Color. No change. (Chapter page names the gadget vertices p, q, r, s, t; same
graph.)

## content/2-algorithms/12-np-hardness-exercises.md

Statements compared with pp. 415–427 (DNF example and the distributive example with their bars from the PDF). All
solutions re-derived: 12.1 DP and the n² -bit example; 12.2 Helly argument and candidate corners; 12.3 linear test and
the 3^k lower bound (minimal-assignment argument); 12.4 literal graph with complementary edges; 12.6(a)(b)(c) (2Sat
rule pos(x) > pos(x̄) and its contradiction chain); 12.7(b)(c) (edge count m+36+9n; padding, distinct-variable variant);
12.8(a)(b)(c); 12.10(a)(b); 12.16(a)–(f) (all inequalities in (d), (e)); 12.22(a)(b); 12.26; 12.34; 12.38. Skipped list:
markers verified on the PDF — ♥ 11(c), 11(d), 14, 15 (♠♥), 21, 22(c), 35(c); ♣ 5(f) (♣♥), 40, 41; no ◆. Accurate.

Special cases: 12.8(a) K₂ — right and necessary (directed 2-cycle counts by the page's convention). 12.10(a) n = 1 —
necessary (K₂ has no undirected Hamiltonian cycle). 12.10(b) n ≤ 2 — necessary for n = 2 (trap), harmless for n = 1.
12.26 isolated vertices — necessary. 12.38 triangle — needed (or the n < 3 special case). **12.22(b) n ≤ 2 — right but
not necessary**: without it, n ≤ 2 gives at most one domino, already a NO instance; and a12x.py's check line
"the special case matters" actually tested that K₂ maps to NO without it.

- 12.22(b): added one sentence saying the case only shortens the proof (for n ≤ 2 the plain construction is a NO
  instance anyway). Previewed (unfolded excerpt).
- tools/checks/a12x.py: replaced the misleading 12.22(b) check by one that runs the plain construction on all graphs
  with n ≤ 2 (all NO); added checks for 12.10(a)'s n = 1 case and for the 12.26 trap (keeping isolated vertices breaks
  the reduction on 361 (graph, k) pairs; keeping them and raising k by their number works on all graphs ≤ 5 vertices).

## Check scripts

- a12c.py: Figure 12.17 line fixed — edges uv, uw, ux, vx, wx; H has 22 vertices and 52 edges, exactly 2 Hamiltonian
  cycles; {u, x} the only cover of size 2 (matches the chapter page's statement). Otherwise the script implements the
  pages' constructions exactly (spot-checked sat_to_ham, book_sat_to_ham incl. both readings, vc_to_ham, sat_to_3color,
  sat_to_is, page phrases, alias uniqueness).
- a12x.py: implementations match the page (partition DP, 2Partition, 2Sat rule, 12.16(b)(c) with small constants,
  domino search). Both end ALL OK; .out saved. check.py on the four pages: OK. Aliases unique site-wide (case-folded grep).

## Doubts / notes for other pages

- Chapter page §12.10 (not mine): "With the two input colors fixed there are exactly five valid colorings (the book's
  Figure 12.14)" — with the inputs fixed there are 2 (equal inputs) or 3 (different inputs); five is the total over the
  two cases (and the book's five are not distinct up to permutation).
- Chapter page uses "spacers"; concept page now does too.
