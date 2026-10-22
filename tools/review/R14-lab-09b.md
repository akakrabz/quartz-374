# Review R14 — Lab 9b (3-homework-and-exams/lab-09b.md; no official solutions) (2026-10-22)

Method: read the handout (lab9b.txt and both pages of lab9b.pdf rendered) and the book's Exercise 6.22 (ch06.txt,
ch06.pdf p. 30 = book p. 254, (b) marked ♥); rubrics from algo-facts.md and toolkit/06 §12–13; DFS page §6.3–6.4.
Solved all four problems myself before reading the page (scratch /tmp/r9b/mine.py: own brute force over all walks,
own topological sort, own layered dag, own three-token sweep that remembers chain *starts* and moves the min-D token
by index on ties). Then re-implemented the page's algorithms from the page text only (/tmp/r9b/page_impl.py: H + s',
3-copy dag, tuples (p0,p1,p2,t0,t1) with σ/τ, rank leader, finish/climb/start/end edges, A0/A1/A2) and compared with
my brute force: 1500 random graphs n ≤ 8 (disconnected allowed; D with ties in {1..3}, distinct ints, BFS hops,
reals; random rank tie-break), k = 1, 2, both readings of paid-into-home, and the extra variant "level teleports may be
paid"; plus 1200 graphs n = 6–9 with heavy ties (/tmp/r9b/stress.py). All agree. Brute force is finite: away steps
raise D and at most k steps are paid, so a tour has ≤ (k+1)(n−1)+k+1 teleports.

## Problem 1 — consistent ranking: agree
Edges a→b, b→c per game suffice (a→c follows in any linear order; with a→c added the cycle question is unchanged since
a→b→c replaces a→c). Topological sort with active-vertex cycle detection, O(n+m). Example (FABDEC, cycle with EFC)
re-derived by hand. No change.

## Problem 2 — Judy's tour: agree
Reading D as given distances with D[s] = 0 < D[v] is right: the input supplies D, "away" = D increases along the edge,
and with BFS hop distances the last stop has D = 1, so every tour is s→v→s (the page's argument is correct). Ties:
level teleport-ways are neither away nor toward and are excluded — consistent with "away at every step", and needed
for acyclicity. Dag H + s', edges v→s' from N(s) (final teleport is a teleport-way into s), home counted once,
answer max{1, LLP(s)}, O(n+m) without sorting by D. Example (answer 4) re-derived. 
Change: "the answer would always be 2" → "… always be 2 (1 if s has no neighbor)". Why: precision.

## Problem 3 — two paid teleports, multiplicity: agree
Readings listed on the page all verified against brute force: paid = strictly toward and landing ≠ s (main); paid may
land at home (edges (v,j)→(s,j+1)); "two including the last" = k = 1. 3n+1 vertices, ≤ 8m edges, (j, D)
lexicographic ⇒ dag. Example 14 (k=2) and 9 (k=1) re-checked.
Change: "(k+1)n+1 vertices and O(km) edges: O(k(n+m)) time" → "O((k+1)m) edges: O((k+1)(n+m))". Why: the old bound
is 0 for k = 0.

## Problem 4 — distinct galaxies (book ♥ 6.22(b)): agree, algorithm and proof correct
Checked the lemma line by line. Ties in D are harmless: the leader is chosen by rank (a total order refining D, any
tie-break), chains strictly increase in rank. Two tokens can share a galaxy (example: all three at h). A galaxy on two
chains is always occupied by both tokens at some moment: when the first arrives the other is strictly lower, and the
first can neither climb nor finish (finishing is also a leader move) until the other arrives; the invariant "seen but
unoccupied ⇒ below every occupied galaxy" gives exactly-once counting, regardless of the real-time order of the
chains. Junctions: start edges enumerate both paid teleports (x1⇢y1, x2⇢y2), tokens 0/1 can finish only at t0 = x1 /
t1 = x2 and may not climb past them, token 2 finishes at a neighbor of s (final teleport). Fewer paid teleports are
needed separately (A2 = −∞ is possible, e.g. G = {s–v}) and the page takes max{1, A0, A1, A2}. Bound: (n+1)³n²+2
tuples, ≤ 3n²(n+1)²m climb edges, ≤ m² start edges ⇒ O(n⁵ + n⁴m); O(n⁴m) after discarding galaxies outside s's
component (≤ m+1 galaxies; m = 0 gives answer 1). Example 8 / 7 and the sweep table re-derived by hand.
Change: added after the Time bullet "If a paid teleport may also land at home (the variant at the end of Problem 3),
let y1 and y2 be s as well in the start edges; nothing else changes." Why: the Sources say Problem 4's variant is
checked, but the page never said how; verified by my tests and by the script.

## Check script (tools/checks/labs_09b.py)
Read it against the page: it implements the page's constructions as stated and compares with exhaustive search (all
graphs n ≤ 4 × D ∈ {1,2,3}, 900 random connected graphs). Added: (1) Problem 4 with three random tie-breaks of the
ranks on every instance with ties (591 runs) = brute force; (2) climb edges summed over all (n+1)³n² tuples ≤
3n²(n+1)²m; (3) the "highest token" trap now must fail on most instances (> 150/300; 264), as the page says "most".
Docstring and the page's Sources line mention (1). Re-ran: ALL OK (30 checks), saved to labs_09b.out.
tools/check.py --only 3-homework-and-exams/lab-09b: OK. No figure change (figure data = checked instance).

## Remaining doubts
- Whether O(n⁴m) can be improved for Problem 4 (the page says it does not know; I found no better construction either).
  The book's intended solution for the ♥ part is unknown.
- Level (equal-D) teleport-ways are never used on the page. Letting them be paid teleports (another possible reading)
  only adds paid edges; I verified that variant too but did not add it to the page.
- Problem 2's "Algorithm" bullet restates the LLP recurrence in one line; I judge it an invocation, not a
  re-explanation (−1 under the rubric), so left it.
