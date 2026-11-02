# Review R19 — Midterm 2 review page (0-toolkit/08-review-algorithms.md), 2026-10-30

Method: read the page in full; re-derived every recurrence, table entry, DFS interval rule, the Bellman–Ford and
Floyd–Warshall recurrences/orders/negative-cycle tests, and all 13 drill answers by hand (D11–D13 traced on the
figure's edge list; figure SVG checked edge by edge against the caption and tools/figs_review_mt2.py). Compared names,
notation, anchors and numbers with the chapter pages 01, 02, 03, 05, 06, 08, 09 (and their "at a glance" tables), the
lab/HW pages and 0-toolkit/06; course facts against algo-facts.md ("Course schedule and exam facts", rubrics);
rubric wording against rubrics.txt; Erickson ch08.txt for Bellman's equation and BellmanFordDP. Verified with
WebFetch: the Fall 2025 and Fall 2026 exams pages (both URLs and the PrairieLearn link are real; Fall 2026 practice
exams are placeholders), and the problem mix of f25-mt2 and its practice exams 1–3.

## 1. Mathematics

Verified correct: key box (level ratio a·f(n/b)/f(n), a/b^d; three cases; unequal pieces Σα_i^d with Θ(n^ρ) above 1
— Akra–Bazzi); subtractive rows; all 14 standard recurrences (lg 3 < 1.585, lg 7 < 2.808); backtracking table and
2^n/3^n derivations; DP shape table (orders incl. LISbigger j-outer, interval i-down/j-up or by length, BF i-outer,
FW r-outer); the 8 standard DPs; adjacency list/matrix table; bag table; DFS edge table (tree/forward, back, cross,
never u.post < v.pre); cycle ⇔ back edge ⇔ u.post < v.post; reverse postorder; Kosaraju–Sharir as stated;
which-algorithm table; BF interface, recurrence (= Erickson p. 295), row-V test; FW recurrence, r outer, diagonal
test; graph-reduction size counts (2nm / m² token edges); traps 1–15 (all genuine traps); drills A1–A5, B6–B7,
C8–C10, D11–D13.

Changes:
- Type 1: "Square roots and logs in f are fine: the ratio still decides" → square roots fine (ratio constant); "A log
  factor in f makes the ratio drift towards 1, so no case applies: sum the levels directly (drill A5)". Why: for
  f = n lg n the ratio is (lg n−1)/lg n, not a constant; ch01 page lists 2T(n/2)+n lg n under "none"; the page's own
  A5 says the same. (Rule "ratio → 1 ⇒ ×log n" fails e.g. for n/lg n.)
- Type 1: "1/2+1/3+1/6 = 1 means every level sums to n" → "every level sums to at most n (the first log_6 n levels to
  exactly n)". Why: the tree is unbalanced; matches ch01 ("at most n", deeper levels missing nodes).
- §3: "subtract the same inequality for n−1: T(n) ≤ 2T(n−1)+O(1)" → "take it with equality and subtract the same
  equation for n−1: T(n) = 2T(n−1)+O(1)". Why: subtracting two ≤ inequalities is not valid.
- §4: "a max over nothing is 0" (stated for the whole table) → "0 in LISfirst but −∞ in LLP (a vertex other than t
  without outgoing edges cannot reach t)". Why: wrong for LLP; ch06 page defines max ∅ = −∞.
- §7: shortest-path tree "stores all shortest paths from s" → "stores a shortest path from s to every vertex".
- §7: "every algorithm below relaxes tense edges … (Ford's generic algorithm)" → "every single-source algorithm
  below" (Floyd–Warshall is in the table and is not an instance of Ford's algorithm).
- §7 table, all pairs/any weights: added "(in a dag: DagSSSP from every vertex, O(VE))". Why: "take the first row
  that applies" + "−1 for slower" would otherwise send an all-pairs dag problem to O(V³); matches ch09 "at a glance".

## 2. Agreement with chapter pages

Names/notation agree (SubsetSum, Splittable, LISbigger, LISfirst, SS, Edit, OptCost, MISyes/MISno, LLP, WFSAll,
DagSSSP, NonnegativeDijkstra, dist_{≤i}(v) with memo dist[0..V−1, V], dist(u, v, r), rev(G), scc(G), reach(s)). All
anchors resolve (check.py). Exercise ranges 3.5–3.10, 5.11–5.19, 8.13–8.17 and all named exercises/lab problems
exist and match. Only notational difference: this page writes T(n) = a T(n/b) + f(n) and log_b a; ch01 uses Erickson's
r T(n/c), log_c r. Left as is (self-contained, defined in the key box). The max-∅ fix above was a contradiction
with ch06 and is now resolved.

## 3. Course facts

Verified: Mon Nov 9 7–9 pm, conflict Tue Nov 10, one double-sided handwritten sheet, HW5–9 + Nov 3 interfaces,
not-on-it list (greedy as topic, MST, flows, NP-hardness; "tested on the final" is backed by Final "Everything"),
policies, HW9 open until Nov 3, lab dates (Lab 10b = Oct 30), optional reviews Nov 5/6. No HW8/HW9 content or
anything resembling a solution; no past problem copied (one-line paraphrases only).

Changes:
- Scope line: "plus Bellman–Ford and Floyd–Warshall as black boxes" → "plus the interfaces of Bellman–Ford's dynamic
  program and of Floyd–Warshall" (Bellman–Ford itself is Ch 8 material, lectured Oct 29, not only a black box).
- §1: the gloss "what each takes, returns and costs" was attached to the announcement with a colon → "— read
  'interface' as …" (interpretation, not the announcement's words).
- §1 table: HW column "HW8" / "HW8, HW9" / "HW8, HW9" → "HW8–9" in all three graph rows (which topic was in which
  homework is unknown; the student has neither handout). Strong components → "strong components (in Ch 6 with
  depth-first search, but not named in the announcement)"; also not in the lecture list.
- §1 rules: "Any algorithm from lecture, the notes, labs or homework is a black box" → "… labs or homework
  solutions …" (the course statement in book-facts.md, "any result from lecture, the notes, labs or homework
  solutions without proof", recorded with the MT1 format; the graph rubric's −1 names lecture, textbook,
  prerequisite class). I first narrowed it to the rubric's wording, then restored it once I found that source.
  Doubt: the statement was recorded for Midterm 1; assumed to be the general exam policy.
- §1 Format: "short answers, a DP that opens with a greedy counterexample, a second DP, a D&C problem, and one or two
  graph reductions" (adds up to 5–6 and is wrong for 3 of 4 exams) → "short answers, one D&C problem, and three
  problems shared between DP and graph reductions — one DP and two graph problems in three of the four exams, two
  DPs and one graph problem in the fourth. In three of the four, a DP opens with a greedy counterexample." Verified
  by WebFetch of f25-mt2 and practice 1–3 (P1: SA, greedy+DP, graph, D&C, graph; P2: SA, graph, DP, D&C, graph;
  P3: SA, greedy+DP, graph, DP, D&C; real: SA, graph, D&C, graph, greedy+DP) and consistent with the problem lists
  in algo-facts (7 graph, 5 DP, 4 D&C).
- Type 3 heading "a second dynamic program" → "a dynamic program without a greedy part" (follows from the above).
- Type 1: "Graded part by part, with no standard rubric" → "Grading: no standard rubric covers this problem"
  (how Problem 1 is graded is not in the sources).
- BF box: "(the Nov 3 lecture's view)" → "(the book's formulation, scheduled for the Nov 3 lecture, whose notation
  may differ)" — the lecture has not happened.
- Plan, Wed Nov 4: "Lab 11 ('Solve it both ways')" → "the Nov 4 lab" (no source for the name or number).
- Plan footer: "Keep the Fall 2025 exams unseen" contradicted "Practice: Problem 1 of every Fall 2025 practice exam"
  → "Apart from their Problem 1 (drill material), keep the Fall 2025 exams unseen …".

## 4. Check script

tools/checks/review_mt2.py implements the page's statements as printed (recurrences numerically/exactly; every DP
of the table vs brute force; evaluation orders by simulated fill; DFS classification, cycles, topological order,
Kosaraju–Sharir; BFS, DagSSSP, Dijkstra, BF rounds + DP + row-V test + super-source; FW r-outer, = 3-index
recurrence, diagonal test, r-inner fails; all drills; page strings). Added: level sums of T(n/2)+T(n/3)+T(n/6)+n
(≤ n, = n exactly for the first ⌊log_6 n⌋ levels); the log-factor ratio (k−1)/k; all-pairs in a dag by
DagSSSP from every vertex = FW; page strings for the BF and FW recurrences, the three DFS table rows, the Θ(n^ρ)
rule, the level-sum wording, the max-∅ convention, the dag all-pairs entry and the row-V test. 143 OK, ALL OK
(review_mt2.out saved). check.py on 0-toolkit/08-review-algorithms: OK.

## 5. Length and redundancy

8,148 → 8,221 words (the hedges add ~110, the cuts remove ~60). Cuts:
- §2 D&C box: the binary-search bullet repeated Type 4's method → pointer "(the method: §1, type 4; Lab 6a: …)".
- §4 greedy box: first sentence repeated Type 2 (a) word for word → "What the answer contains: §1, type 2."
- §4 "Trees and dags": "the parameter is a node, the memo is a field in the node, the order is postorder" repeated
  the shape table → "(shape table above)".
- §5: rubric parenthetical (½ for BFS/DFS where WFS suffices), stated also in Type 5 and trap 8 → "(trap 8 of §9)".
No restructuring. Further candidates left alone: trap 4's second sentence (= Type 2 (a)), §7 Johnson paragraph vs
§1 "Not on it".

## Remaining doubts

- The "HW8–9" attribution of graph topics and the lab ↔ topic map rest on lab pages only.
- "the Spring 2026 practice exams … have the same problems" comes from algo-facts; not re-verified.
- Bag table "stack → starting and finishing times": strictly those come from recursive DFS (§6), not from the
  stack-based WFS; harmless, left.
- Floors/ceilings "never change the answer": true for the recurrences on the exam, not literally for all.
- Light-mode screenshot of §1 and §7 tables looked fine (no figure changed).
