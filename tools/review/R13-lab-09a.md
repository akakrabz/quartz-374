# Review R13 — Lab 9a (number-maze variants), `content/3-homework-and-exams/lab-09a.md` (2026-10-22)

Method: rendered lab9a.pdf (both pages; maze figure at 400 dpi) and read every statement and the drawn 8-move path
(R3 D4 L2 R1 U3 L1 R3 D3; goal drawn as ★ without a label). Solved all six problems myself before reading the page,
wrote independent code in /tmp/r9a/mine.py (own move generator, own reductions; Problem 5 deliberately via the
O(n³) (square, last length) graph, not the page's) and a brute force over explicit move sequences, then compared:
- own reductions vs brute force (all walks ≤ 12 moves): 3,300 random mazes n = 1..4, 0 mismatches;
- own reductions vs the page's graphs (writer's builders, imported only for this cross-check): 34,968 comparisons on
  random mazes n = 2..6, both readings (pass through the goal / game ends on arrival), 0 differences;
- "game ends on arrival" reading: own brute force over walks that stop at the goal vs own reductions with M[n,n] = n,
  1,500 mazes, 0 mismatches (confirms the page's "give (n,n) the label n, every reduction works unchanged");
- handout example, own code only: 8, none, 10, none, none, none for every goal label 1..7; brute force up to 16 moves
  agrees; the 8-move solution is the only one with 8 moves; the only 10-move solution not passing through the goal is
  R3 D4 L2 R1 U3 L1 R3 L3 R3 D3 (= page). Re-derived by hand the four "facts" (moves into the goal, into (2,5), into
  (2,2), out of (1,1)) and the deductions for Problems 2, 4, 5, 6.
Then read the page line by line against the rubric (algo-facts.md, toolkit §13) and the handout's six bullets, read
the check script against the page (same graphs, same sources/targets, n = 1 handling, both readings), ran it.

## Per problem

- **P1** — agree. Squares, directed move edges, BFS from (1,1), dist(n,n); E ≤ 4n²; O(n²); BFS vs WFS/Dijkstra correct.
- **P2** — agree. Separate start s with edges for both kinds of first move; (i,j,axis of last move); targets
  (n,n,horiz)/(n,n,vert); E ≤ 4n² + 2; n = 1 returns 0 directly (s ≠ target). Walks from s ↔ alternating sequences
  (both directions hold by induction). Trap text had a false detail (fixed, below).
- **P3** — agree. 5 layers, (r+1) mod 5, BFS (1,1,0) → (n,n,0); n = 1 gives 0; rounding-up trap correct (all-1 2×2:
  2 vs 10, parity); "may not exist even when solvable" true (e.g. 3×3 [[1,2,2],[3,2,3],[3,1,3]]). Shortest valid
  solution may pass through the goal here — page states its reading and the alternative.
- **P4** — agree. Start s, (i,j,direction of last move), edges skip opp(d); targets the four (n,n,d); E ≤ 12n² + 3.
- **P5** — agree with the O(n²) reduction. A move from p has length M[p], so "next move longer" is the edge-local
  condition M[q] > M[p] on p→q whenever q is left again; the last move (into the goal, any labels) goes to t; first
  move unconstrained (no condition into (1,1)); n = 1 returns 0 directly (t unreachable). Walks (1,1) ⇝ t with m
  edges ↔ valid solutions with m moves. Dag; lengths strictly increase in 1..n−1 ⇒ ≤ n−1 moves. E ≤ 4n² + 2n. Direct
  O(n³) version correct. Agrees with my independent O(n³) version everywhere.
- **P6** — agree. Pair (f,b); edge needs move f→f′ and move b′→b with M[b′] = M[f] (back step reversed correctly);
  even: (f,f) → 2d; odd: move f→b → 2d+1; min over both after one BFS; n = 1 gives 0 via (f,f) at d = 0. Out-degree
  ≤ 16 because b′ ∈ {b ∓ M[f]·dir} (not all O(n) predecessors of b); O(n⁴).
- Example table and "four facts" paragraph — agree (also hold for every goal label; with label 3, U3 out of the goal
  also enters (2,5), which the paragraph says).

## Changes (before → after, why)

1. P2 trap: "from there only vertical moves are allowed, and they lead nowhere new, so it reports 'no solution'" →
   "…: up returns to the marked square (1,2), and down reaches (3,2), whose label 2 allows no horizontal move. The
   search stops without reaching the goal and reports 'no solution'". Why: false detail — down from the center
   reaches the unmarked (3,2) (traced by hand and in code); the conclusion was right. Check added (marked squares and
   arrival directions of the modified search; (3,2) has no horizontal move).
2. P2 idea, start vertex: "(It cannot be one of the two copies of (1,1): the token may come back to (1,1) later, and
   then the rule applies.)" → explains why one copy cannot serve (each allows one kind of move; giving one all moves
   breaks the rule on a return to (1,1)) and adds "Running BFS from each of the two copies and keeping the smaller
   distance works too." Why: the old wording could be read as ruling out the (correct, full-credit) two-source
   approach. Check added (two BFS runs = page answer, n = 1 included).
3. P5 algorithm remark: "dynamic programming over the squares in increasing order of label, which is a topological
   order — but that also takes O(V+E) time" → adds "(with t last; capping the labels at n, which changes no edge,
   counting sort finds it in O(n²) time)". Why: a comparison sort of the labels would cost O(n² log n), so the
   "also O(V+E)" needed the counting-sort justification. Check added (capping changes no edge; the order is
   topological).
4. Figure lab-09a-example caption (tools/figs_labs.py, Lab 9a section): "It ends with right 3 from (2,2) and down 3
   into the goal (red): those are the only moves into the goal and into (2,5)." → "It ends with down 3 from (2,5) into
   the goal and first reaches (2,5) by right 3 from (2,2) (red): those are the only moves into the goal and into
   (2,5), apart from up 3 out of the goal if the goal were labeled 3." Why: under the page's default (pass-through)
   reading with goal label 3, a solution can end U3 D3 (e.g. R3 D4 L2 R1 U3 L1 R3 D3 U3 D3); the conclusions are
   unchanged. Regenerated only the Lab 9a figures (palindrome figure byte-identical) and ran assemble.py on this page.

Check script: tools/checks/labs_09a.py now 92 OK lines, ends ALL OK (output saved to labs_09a.out).
tools/check.py --only 3-homework-and-exams/lab-09a: OK. Light-mode preview looked at (example figure and caption).

## Remaining doubts

- Reading of "solution" when the token passes through the goal: the handout does not say. The page takes the
  pass-through reading as default and gives the stop-on-arrival variant; only Problems 3 and 6 can differ, and the
  example's answers are the same under both. A grader expecting one specific reading should accept either as stated.
- No official solutions exist; all six answers rest on my independent derivation and the computational checks above.
