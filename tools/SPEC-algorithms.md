# CS/ECE 374 site — writing spec for Part 2 (Algorithms)

Part 2 summarizes Jeff Erickson's *Algorithms* the way Part 1 summarizes *Models of Computation*. **Read `tools/SPEC.md`
first** — everything in it applies (frontmatter, notation, callouts, links, figures, verification, style) except where this
file says otherwise. Then read `/home/claude/work/algo/algo-facts.md` (book, page offsets, sections, course and rubric facts),
and the exemplar `content/1-models-of-computation/03-finite-state-machines.md` for structure, tone and density.

## 0. Reader and purpose

The reader **has already read the textbook** and wants a good summary and review before Midterm 2 (algorithms, Nov 9) and the
final: the definitions, the algorithms with their recurrences and running times, the proof ideas, the patterns to reuse, the exam
write-up format and the traps. Not a replacement for the book: don't retell anecdotes; do keep every algorithm, recurrence,
analysis and key example. **Correctness is the top priority** — every algorithm, recurrence, table and number is checked by code.

## 1. Files and links

```
content/2-algorithms/index.md                     unit page (written by the coordinator)
content/2-algorithms/01-recursion.md               chapter pages
content/2-algorithms/02-backtracking.md
content/2-algorithms/03-dynamic-programming.md
content/2-algorithms/01-recursion-exercises.md     solved book exercises (see §6)
content/2-algorithms/02-backtracking-exercises.md
content/2-algorithms/03-dynamic-programming-exercises.md
content/2-algorithms/04-greedy-algorithms.md          (build 3)
content/2-algorithms/05-basic-graph-algorithms.md
content/2-algorithms/06-depth-first-search.md
content/2-algorithms/04-greedy-algorithms-exercises.md
content/2-algorithms/05-basic-graph-algorithms-exercises.md
content/2-algorithms/06-depth-first-search-exercises.md
content/2-algorithms/07-minimum-spanning-trees.md    (build 4) + 07-minimum-spanning-trees-exercises.md
content/2-algorithms/08-shortest-paths.md                       + 08-shortest-paths-exercises.md
content/2-algorithms/09-all-pairs-shortest-paths.md             + 09-all-pairs-shortest-paths-exercises.md
content/2-algorithms/10-maximum-flows-and-minimum-cuts.md (build 5) + 10-maximum-flows-and-minimum-cuts-exercises.md
content/2-algorithms/11-applications-of-flows-and-cuts.md           + 11-applications-of-flows-and-cuts-exercises.md
content/2-algorithms/12-np-hardness.md                              + 12-np-hardness-exercises.md
content/concepts/<slug>.md                         concept pages (see §3)
tools/figs_a0N.py → tools/figs/a0N-*.html          figures (chapter N; exercises use a0Nx-*)
tools/checks/a0N.py (+ .out)                       checks for chapter page N and its concept pages
tools/checks/a0Nx.py (+ .out)                      checks for the exercises page of chapter N
Graph figures: `tools/figlib.py` has `Automaton` (circles/rounded boxes + straight, curved or looped edges; works for any
graph — pass `start=None`, `accepting=False`) and `Tree`. Use them; colors only through the CSS variables (SPEC §8).
```

Existing pages you may link: everything in Part 1, e.g. `[[0-toolkit/06-how-exams-are-graded]]`,
`[[0-toolkit/02-proof-templates]]`, `[[concepts/induction-on-strings]]`, `[[1-models-of-computation/07-undecidability#79-the-halting-problem-via-reduction|reductions]]`.

## 2. Fixed chapter headings (anchors other pages link to)

```
Ch1: 1.1 Reductions | 1.2 Simplify and delegate | 1.3 Tower of Hanoi | 1.4 Mergesort | 1.5 Quicksort | 1.6 The pattern |
     1.7 Recursion trees | 1.8 Linear-time selection | 1.9 Fast multiplication | 1.10 Exponentiation | Summary
Ch2: 2.1 N queens | 2.2 Game trees | 2.3 Subset sum | 2.4 The general pattern | 2.5 Text segmentation |
     2.6 Longest increasing subsequence | 2.7 Longest increasing subsequence, take 2 | 2.8 Optimal binary search trees | Summary
Ch3: 3.1 Matravrtta: Fibonacci numbers | 3.2 Aside: even faster Fibonacci numbers | 3.3 Interpunctio verborum redux |
     3.4 The pattern: smart recursion | 3.5 Warning: greed is stupid | 3.6 Longest increasing subsequence | 3.7 Edit distance |
     3.8 Subset sum | 3.9 Optimal binary search trees | 3.10 Dynamic programming on trees | Summary
Ch4: 4.1 Storing files on tape | 4.2 Scheduling classes | 4.3 The general pattern | 4.4 Huffman codes | 4.5 Stable matching |
     Summary
Ch5: 5.1 Introduction and history | 5.2 Basic definitions | 5.3 Representations and examples | 5.4 Data structures |
     5.5 Whatever-first search | 5.6 Important variants | 5.7 Graph reductions: flood fill | Summary
Ch6: 6.0 Depth-first search, recursively (the chapter's unnumbered introduction) | 6.1 Preorder and postorder |
     6.2 Detecting cycles | 6.3 Topological sort | 6.4 Memoization and dynamic programming | 6.5 Strong connectivity |
     6.6 Strong components in linear time | Summary
Ch7: 7.1 Distinct edge weights | 7.2 The only minimum spanning tree algorithm | 7.3 Borůvka's algorithm |
     7.4 Jarník's (Prim's) algorithm | 7.5 Kruskal's algorithm | Summary
Ch8: 8.1 Shortest path trees | 8.2 Negative edges | 8.3 The only SSSP algorithm | 8.4 Unweighted graphs: breadth-first search |
     8.5 Directed acyclic graphs: depth-first search | 8.6 Best-first: Dijkstra's algorithm |
     8.7 Relax all the edges: Bellman–Ford | Summary
Ch9: 9.1 Introduction | 9.2 Lots of single sources | 9.3 Reweighting | 9.4 Johnson's algorithm | 9.5 Dynamic programming |
     9.6 Divide and conquer | 9.7 Funny matrix multiplication | 9.8 Floyd–Warshall | Summary
Ch10: 10.1 Flows | 10.2 Cuts | 10.3 The maxflow-mincut theorem | 10.4 Ford and Fulkerson's augmenting-path algorithm |
     10.5 Combining and decomposing flows | 10.6 Edmonds and Karp's algorithms | 10.7 Further progress | Summary
Ch11: 11.1 Edge-disjoint paths | 11.2 Vertex capacities and vertex-disjoint paths | 11.3 Bipartite matching |
     11.4 Tuple selection | 11.5 Disjoint-path covers | 11.6 Baseball elimination | 11.7 Project selection | Summary
Ch12: 12.1 A game you can't win | 12.2 P versus NP | 12.3 NP-hard, NP-easy and NP-complete | 12.4 Formal definitions |
     12.5 Reductions and SAT | 12.6 3SAT (from CircuitSat) | 12.7 Maximum independent set (from 3SAT) |
     12.8 The general pattern | 12.9 Clique and vertex cover (from independent set) | 12.10 Graph coloring (from 3SAT) |
     12.11 Hamiltonian cycle | 12.12 Subset sum (from vertex cover) | 12.13 Other useful NP-hard problems |
     12.14 Choosing the right problem | 12.15 A frivolous real-world example | 12.16 On beyond zebra | Summary
```
Build-5 anchors (github-slugger: lowercase, punctuation dropped, spaces → hyphens, Unicode kept): `#103-the-maxflow-mincut-theorem`,
`#104-ford-and-fulkersons-augmenting-path-algorithm`, `#106-edmonds-and-karps-algorithms`, `#113-bipartite-matching`,
`#121-a-game-you-cant-win`, `#123-np-hard-np-easy-and-np-complete`, `#126-3sat-from-circuitsat`,
`#127-maximum-independent-set-from-3sat`, `#128-the-general-pattern`, `#129-clique-and-vertex-cover-from-independent-set`,
`#1210-graph-coloring-from-3sat`, `#1211-hamiltonian-cycle`, `#1212-subset-sum-from-vertex-cover`,
`#1213-other-useful-np-hard-problems`, `#1214-choosing-the-right-problem`. `tools/check.py` validates every anchor.
The ♥ sections (12.4, 12.16) are kept, briefly, with "(♥ in the book)" in the first sentence, not in the heading.

Anchors are github-slugger slugs: `#17-recursion-trees`, `#18-linear-time-selection`, `#24-the-general-pattern`,
`#27-longest-increasing-subsequence-take-2`, `#31-matravrtta-fibonacci-numbers`, `#34-the-pattern-smart-recursion`,
`#310-dynamic-programming-on-trees`, `#43-the-general-pattern`, `#45-stable-matching`, `#55-whatever-first-search`,
`#57-graph-reductions-flood-fill`, `#63-topological-sort`, `#64-memoization-and-dynamic-programming`,
`#66-strong-components-in-linear-time`. (Ch 5 has several short history sections in the book; 5.1 may be brief.) Extra material goes in `###` subsections or an unnumbered `##` before `## Summary`.
In text, write the Sanskrit name as Mātrāvṛtta.

## 3. Concept slugs for Part 2 (link as `[[concepts/<slug>]]`)

Ch 1: `recursion` · `divide-and-conquer` · `recursion-trees` · `linear-time-selection`
Ch 2: `backtracking` · `subset-sum` · `longest-increasing-subsequence`
Ch 3: `dynamic-programming` · `memoization` · `edit-distance` · `optimal-binary-search-trees` · `dynamic-programming-on-trees`
Ch 4: `greedy-algorithms` (the pattern and the exchange argument) · `interval-scheduling` · `huffman-codes` · `stable-matching`
Ch 5: `graphs` (definitions, representations, the V/E vocabulary) · `whatever-first-search` (incl. the stack/queue/priority-queue
      variants and their running times) · `graph-reductions` (modeling a problem as a graph; the rubric's write-up)
Ch 6: `depth-first-search` (pre/postorder, edge classification) · `topological-sort` · `dynamic-programming-on-dags` ·
      `strongly-connected-components`
Ch 7: `minimum-spanning-trees` (safe/useless edges, the generic algorithm; Borůvka, Jarník/Prim and Kruskal compared;
      aliases for the three names) · `union-find` (disjoint sets, as used by Kruskal)
Ch 8: `shortest-paths` (SSSP, shortest-path trees, tense edges and relaxation, Ford's generic algorithm, negative cycles) ·
      `breadth-first-search` (the Ch 8 writer moves the aliases "BFS" and "breadth-first search" here from
      concepts/whatever-first-search.md, editing only that page's aliases line and adding a link) · `dijkstras-algorithm` ·
      `bellman-ford`
Ch 9: `all-pairs-shortest-paths` (the problem, lots of single sources, DP, divide and conquer, funny matrix
      multiplication) · `johnsons-algorithm` (reweighting) · `floyd-warshall`

Ch 10: `maximum-flow` (flows, cuts, residual graphs, the maxflow-mincut theorem, integrality; aliases such as "maxflow",
      "minimum cut", "maxflow-mincut theorem") · `ford-fulkerson` (augmenting paths, running times, Edmonds–Karp's two
      rules; aliases "Ford–Fulkerson", "augmenting path", "Edmonds–Karp")
Ch 11: `flow-reductions` (modeling a problem as a flow network: edge- and vertex-disjoint paths, vertex capacities,
      the two-direction proof, integrality) · `bipartite-matching`
Ch 12: `np-hardness` (P, NP, co-NP, NP-hard, NP-easy, NP-complete, P versus NP; aliases "NP-hard", "NP-complete",
      "P versus NP") · `polynomial-time-reductions` (Karp reductions, the direction rule, the write-up and its rubric;
      aliases "Karp reduction", "many-one reduction", "NP-hardness proof") · `satisfiability` (SAT, CircuitSat, 3SAT,
      CNF, the CircuitSat → SAT/3SAT reductions; aliases "SAT", "3SAT", "CircuitSat") · `independent-set` (with clique
      and vertex cover: the 3SAT reduction and the complement relations; aliases "IndependentSet", "maximum independent
      set", "clique", "vertex cover") · `graph-coloring` (3Color from 3SAT) · `hamiltonian-cycle` (the book's reduction).
      Already on the site and to be linked, not rewritten: `cook-levin-theorem` (Part 1 §9.6) and `subset-sum` (Ch 2–3;
      the Ch 12 writer adds §12.12 to its "Where it appears" line and nothing else).

Concept pages follow SPEC §12 (definition/key box, why it works, recipe/template, traps, one checked example, "Where it appears"
with exact anchors, `Related:` last). Tags: `concept` plus `algorithms` and a topic tag. Check aliases are unique site-wide
(`grep -rh "^aliases" content`).

## 4. Frontmatter and meta line

```yaml
---
title: "Chapter 1 — Recursion"
description: "…"
tags: [chapter, algorithms, recursion, midterm-2]      # topic tags: recursion, backtracking, dynamic-programming
chapter: 1
---
```
Meta line: `*Algorithms, Chapter 1 · book pp. 21–70 · [chapter PDF](https://jeffe.cs.illinois.edu/teaching/algorithms/book/01-recursion.pdf) · next: [[2-algorithms/02-backtracking|Chapter 2]] · exercises: [[2-algorithms/01-recursion-exercises|solved exercises]]*`
(Chapter PDFs: `01-recursion.pdf`, `02-backtracking.pdf`, `03-dynprog.pdf`, `04-greedy.pdf`, `05-graphs.pdf`, `06-dfs.pdf`,
`07-mst.pdf`, `08-sssp.pdf`, `09-apsp.pdf`, `10-maxflow.pdf`, `11-maxflowapps.pdf`, `12-nphard.pdf`.) Then `> [!abstract] In one breath`, the fixed
sections, `## Summary`, `> [!exam] On the exams`, `### Sources for this page` — as in Part 1.

## 5. Algorithms on the page

- **Pseudocode** goes in fenced blocks marked `text`, in the book's style: CamelCase procedure names with array parameters
  (`MergeSort(A[1 .. n])`), `←` for assignment, `for i ← 1 to n`, `if … else`, `return`, comments as `⟨⟨…⟩⟩`. Keep it short and
  exactly as correct as the book's; when you shorten or change the book's version, say so.
- Mention algorithm names in running text as plain text or `\textsf{MergeSort}` in math — consistently on a page.
- Every algorithm gets: what it computes (the recursive-algorithm rubric's "English description"), its recurrence, the solved
  running time, and the one-line reason it is correct. Recurrences in display math; solutions with `\Theta`.
- **Dynamic programming** solutions are written in the rubric's format, every time: (1) a *named* function with explicit
  parameters and an English sentence saying what it returns, plus which call answers the problem; (2) the recurrence with base
  cases; (3) the memoization structure; (4) the evaluation order (for nested loops, which is outer); (5) time = entries × work
  per entry. Use `[!definition]` for (1) and a display for (2).
- **Backtracking / divide and conquer** solutions are written in the recursive-algorithm rubric's format: the problem the
  recursive algorithm solves (in English, including any generalization), base case, the recursive calls, how results combine,
  recurrence + solution.
- **Greedy algorithms** are written as: the algorithm (pseudocode or one precise sentence), its running time, and a proof
  of correctness — normally the book's exchange argument (an optimal solution that agrees with the greedy choice exists;
  then induct). State the greedy choice precisely, and give a counterexample for each tempting wrong rule the book discusses.
- **Graph problems** solved by reduction are written in the graph-reduction rubric's format (algo-facts.md): (1) the graph —
  vertices and edges (and weights) as explicit functions of the input, directed or not; (2) the problem on that graph —
  "reachability from … to …", "shortest path from … to any vertex of the form …" — and why it answers the original question;
  (3) the standard algorithm invoked as a black box (whatever-first search when reachability is all that is needed);
  (4) time in the INPUT's parameters. Notation: $G = (V, E)$, $n = \lvert V\rvert$ (the book writes $V$ for both — use $V$
  and $E$ in running times like the book: $O(V + E)$), directed edges $u\to v$, undirected edges $uv$.
- **Flow reductions** (Ch 10–11) are written like graph reductions, plus Erickson's two-direction proof: (1) the flow
  network — vertices, directed edges, capacities, source and sink — as explicit functions of the input; (2) the claim
  "the input has a solution of size $k$ if and only if the network has an $(s,t)$-flow of value $k$", proved in both
  directions (solution → flow; integral flow → solution, by the integrality theorem); (3) the maximum-flow algorithm
  as a black box (Ford–Fulkerson in $O(E\lvert f^*\rvert)$ when the flow value is small, otherwise Orlin's $O(VE)$ as
  the book allows); (4) time in the input's parameters. Flows are **not taught in CS 374** (the book's own page says the
  course covers everything except flows) and appear on no exam: say so once in the "On the exams" box, without a rubric.
- **NP-hardness proofs** (Ch 12) are written in the course NP-hardness rubric's format (algo-facts.md): name the known
  NP-hard problem $X$; the reduction as an algorithm that takes an **arbitrary instance of $X$** and builds an instance
  of $Y$ in polynomial time (gadgets described exactly, sizes counted); the "⇒" proof (a YES instance of $X$ gives a YES
  instance of $Y$) and the "⇐" proof (if the built instance of $Y$ is YES, the instance of $X$ was YES); the words
  "polynomial time". The direction rule is the top trap: reduce **from** the known hard problem **to** the new one.
  Every reduction on a page is checked by brute force on all (or many random) small instances: YES ↦ YES and NO ↦ NO.
- Recursion trees: show the level sums and say which of the three cases applies (decreasing geometric → root dominates,
  equal → levels × level sum, increasing → leaves dominate).

## 6. Solved exercises pages (`0N-…-exercises.md`)

The student asked for solutions to **some of the easier book exercises — roughly the first 10 of each chapter**. Skip, and say
in one line at the top which you skipped and why: exercises marked ♥ (book's "particularly challenging", extracted as `ª`),
◆ (needs later chapters), anything that would take an unreasonable amount of thought, and anything equivalent to an open
course homework problem (list in algo-facts.md). It is fine to solve only some parts of a multi-part exercise.

```markdown
---
title: "Chapter 1 exercises — Recursion"
description: "Solutions to selected exercises from Chapter 1 of Erickson's Algorithms: …"
tags: [exercises, algorithms, recursion, midterm-2]
---

*Solved exercises for [[2-algorithms/01-recursion|Chapter 1]] · book pp. 44–70 · statements paraphrased; see the book for the originals*

(one short paragraph: which exercises are here, which were skipped and why)

## Exercise 1.6 — Recursion trees

> [!question] Exercise 1.6 (book p. 48)
> The statement, paraphrased faithfully and completely (all parts you solve), with the book's examples.

### (a) …

> [!hint]- Hint
> One or two sentences.

> [!solution]- Solution
> The solution in the rubric's format (§5): description → recurrence/algorithm → analysis → why it is correct.
>
> **Answer.** The final algorithm / bound / number in one line.
```

Rules: one `##` per exercise (`## Exercise 1.6 — Short title`), `###` per part you solve; hint and solution folded; every
solution ends with `> **Answer.** …`; every claimed answer (move counts, closed forms, recurrence solutions, algorithm outputs on
examples) is checked in `tools/checks/a0Nx.py` against brute force or direct simulation; mark anything not machine-checkable as a
proof in the text. Difficulty is not tagged. A worked solution should look like a full-credit exam answer: correct, complete,
concise.

## 7. Verification (mandatory)

Write Python checks (no special library needed; `tools/automata` is irrelevant here): implement every algorithm exactly as the
page's pseudocode/recurrence states it, and compare with brute force on many random small inputs (e.g. all inputs up to size 8,
plus random ones); check every number on the page (move counts, table entries, recurrence values, the book's examples such as
edit distance tables) and every claimed asymptotic solution numerically (compute T(n) for growing n and check the ratio to the
claimed bound settles, or check an exact closed form). Use `check(name, cond, detail)` lines and end with `ALL OK`; save the
output (`python3 tools/checks/a0N.py | tee tools/checks/a0N.out`). If the book's claim fails a check, investigate, fix the page
(never the check), and report it.

## 8. Before you finish

1. `python3 tools/assemble.py content/2-algorithms/<your page>.md` (only your pages).
2. `python3 tools/check.py content /opt/npm-tools/node_modules/katex/dist/katex.min.js --only 2-algorithms/0N,concepts/<yours>`
   — zero errors except "wikilink target not found" for pages that other agents are still writing (the other chapter pages,
   exercises pages and Part 2 concept pages listed above).
3. Preview each page once in light mode (`python3 /home/claude/work/preview/pageshot.py content/<page>.md /tmp/x.png light`,
   then `tiles.py`), figures in light and dark. Fix overflowing displays (split long `cases` into named branches) and broken
   callouts. Budget: don't screenshot more than needed.
4. Final message: files written, deviations from the book and why, book errors found, anything unverified.
