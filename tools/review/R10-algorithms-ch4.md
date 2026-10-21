# Review R10 — Algorithms Chapter 4 (greedy algorithms), its concept pages and exercises (2026-10-20)

Method: read every page in full (figure SVGs and captions included); compared sections, statements, pseudocode,
tables and examples with the book (ch04.txt, and ch04.pdf pages 161, 162, 167, 170, 173, 174, 178 rendered with
pdftoppm; the three p. 178 interval figures re-measured from the PDF's vector data with pdfplumber); re-derived every
lemma, exchange argument, counterexample, example number and exercise proof by hand; recomputed the delicate claims
with independent code (book figure geometry for 4.3–4.5; minimum largest frequency for 4.6(a), n ≤ 8, both tie
readings); read both check scripts against the pages and ran them; ran tools/check.py on all assigned prefixes.

## 2-algorithms/04-greedy-algorithms.md

Checked: both tape cost forms and the (n − i + 1) weights; Lemma 4.1 swap ((L[b] − L[a])/n) and the "all sorted
orders cost the same" step; Lemma 4.2 swap L[b]F[a] − L[a]F[b], strictness ⇒ every optimal order is ratio-sorted,
equal-ratio ties (adjacent swaps within a block, change 0); both tape examples (5, 7.5; 49 / 57 / 58). §4.2: problem
statement (⊆, distinct i, j, strict inequalities), the take-class-1-or-not recursion and the book's O(n³) remark;
GreedySchedule = book Fig. 4.3; the nine-class figure (SVG coordinates → a[1,3] … i[19,24], picks a c f i, a d h i
also maximum); Lemma 4.3 ("maximum-size", with the note that the book says "maximal"; compatible + later finish ⇒
starts after g ends); Theorem 4.4 both proofs (classes outside A are skipped because the last pick never finishes
before f; first-difference exchange keeps the finish-time order; the m > k step); trap table and the 11-class
fewest-conflicts example (unique minimum 2 conflicts, leftover groups pairwise overlapping). §4.3 recipe and template
against book pp. 164–165. §4.4: prefix-free / code-tree facts; cost = sum of internal weights; Sallows' sentence,
frequency and depth tables, codewords A = 101000, S = 111, the THISSE prefix, 649 and 850; the tree figure node by
node against book p. 167 (19 internal nodes summing to 649); Lemma 4.5 proof (full-tree reduction; swap formula;
all overlap cases of x, y with the two deepest positions — handled more carefully than the book); Theorem 4.6
(contraction cost(U) = cost(U′) + f1 + f2 for any U with 1, 2 siblings; optimal T′ ⇒ optimal T); BuildHuffman =
Fig. 4.4 with the loop fix; 2n − 1 Inserts / 2n − 2 ExtractMins; Encode/Decode = Fig. 4.5; Fano–Shannon 10,4,4,4,3
(splits, 57) vs Huffman 55. §4.5: definition; both "bad ideas" inputs as printed on pp. 171–172, Knuth's cycle, the
rounds protocol (stable on input 1, unstable via (s, A) on input 2); the GaleShapley pseudocode (invariants,
Next[A] ≤ n, O(1) per offer, O(n²)); the 4×4 lists against p. 173, the ten steps, the result, "only stable
matching", no first choices, County's last choice; the figure (offer numbers, struck/filled/dotted boxes);
n(n+1)/2 tightness; correctness proof (pigeonhole for perfect matching; stability); Lemma 4.7 induction;
Corollaries 4.8–4.9; same matching and same offer count (2 + 2 + 4 + 2) in every run; doctor-proposing run on the
example (9 offers, same matching); Dubins–Freedman / collusion / 1998 statements against p. 176. Roles are the
book's throughout: hospitals offer, hospital-optimal, doctor-pessimal. Summary table and Summary.

Changes:
1. §4.1, last paragraph. Before: "The book remarks that this problem resembles optimal binary search trees (§3.9)
   but needs no dynamic programming: here one swap of neighbors never affects any other file, which is exactly what
   makes the local choice safe." After: "… resembles optimal binary search trees (§3.9) in spirit, but the data
   structure and the cost function differ, so the algorithm differs too. Here no dynamic programming is needed:
   swapping two neighbors changes the cost of no other file, which is what makes the adjacent-swap argument work."
   Why: the book (p. 161) says only that structure and cost differ; "needs no DP" and the reason were attributed to
   the book.
2. "On the exams" callout. Before: "… and without one it earns no credit, even when it happens to be correct (the
   book's policy and the course's)." After: "…; the policy the book states in §3.5 gives no credit without one, even
   when the algorithm happens to be correct." Why: the no-credit policy is the book's (§3.5, p. 108, verified in
   ch03.txt); the course material available here (rubrics.txt, algo-facts.md) only has the DP rubric's −1½ for an
   unproved greedy step, which the next sentence of the callout already states.

## concepts/greedy-algorithms.md, concepts/huffman-codes.md, concepts/stable-matching.md

Checked: definitions, why-it-works, templates, recipes, traps; knapsack example (greedy 9 vs 10; fractional 13 =
LP optimum; exchange by density); ABRACADABRA (A5 B2 R2 C1 D1, both trees, 23 = 2 + 4 + 6 + 11, fixed 33);
stable-matching example (hospitals offering: first choices, 3 offers; doctors offering: {As, Bq, Cr}; third stable
matching {Ar, Bs, Cq} all second choices; exactly 3 stable matchings); anchors; aliases unique site-wide. No changes.

## concepts/interval-scheduling.md

Checked: definition (book's strict convention), why-it-works, recipe, traps (earliest start, shortest, endpoint
convention [1,3],[3,5],[5,7]), six-class example (greedy [2,3],[5,7],[8,10]; maximum 3).
Change: weighted trap. Before: "earliest finish fails — $[0,2]$ worth 1 beats $[1,10]$ worth 5 —". After: "earliest
finish fails — it takes $[0,2]$ worth 1 and loses $[1,10]$ worth 5 —". Why: "beats" read as if the 1-credit class
were the better one.

## 2-algorithms/04-greedy-algorithms-exercises.md

Checked every statement against pp. 176–179 (paraphrases faithful; 4.7 is ♥ and correctly skipped). Re-derived:
4.1 — all six counterexamples (first move forced, excludes every optimum; conflict counts in (e) 2/3/4 and (g)
4/2/3; every tie-break), the five-panel figure coordinates; (c) by reflection (compatibility preserved, conflicts
preserved, Lemma 4.3 for any first-finishing class); (h) all three cases including equal start times (y ⊆ x or
F[x] < F[y]); (i) containment discard, "ends last ⇒ starts strictly last" without containments, mirror of Lemma 4.3.
4.2 — [0,3]/2 vs [1,2]/1 against EF, (c), (h), (i); unit credits for the other six; MaxCredit: Prev(j) is a prefix
and < j, the compatibility argument, rubric parts (named function, prefix, base case, array, order, time).
4.3 — SmallestCover invariants (scanned intervals end ≤ reach; a gap is a real gap of the union; t = reach inside a
component), the stays-ahead claim and its closedness step, the component decomposition, k ≤ m; book figure: the
16 intervals re-measured from the PDF vectors give union = one interval, the shaded 7 form a cover, the minimum is 6
(4 different minimum covers), and the page's six picks are what the pseudocode returns. 4.4 — single test L[i] > p,
exchange to R1, induction, disjoint certificate (= GreedySchedule's picks); book figure: greedy 4 points, 4 disjoint
intervals, the book's points stab all. 4.5 — depth sweep (left before right), both bounds, the sweep coloring
(touching closed intervals), book coloring proper, depth 5. 4.6 — (a) caterpillar characterization, condition (∗)
under adversarial ties, the Lucas lower-bound induction and equality, Fibonacci S_k = F_{k+2} − 1, L_{n−2} =
F_{n−1} + F_{n−3} < F_n for n ≥ 5, favorable-tie variant F_{n−1}, (1,1,1,2) depths 2 and 3, the n = 6 figure;
independent exhaustive search (n ≤ 8): 1,1,3,4,7,11,18 and 1,1,2,3,5,8,13 for n = 2..8. (b) grandparent lemma and
d ≤ 2 log₂ N + 1. 4.8 — full-tree parity, the dummy-removal step (d2 cannot lie below x; third child moves up),
deepest-node exchange, contraction, (1,1,1,1) 7 vs 6. 4.9 — invariants, Next[A] ≤ n, O(n²), 10 offers on the book
example. 4.10 — unique stable matching for identical lists, exactly k offers by A_k in every run, n(n+1)/2, explicit
run for (a). No HW7 problem appears; 4.9/4.10 are book exercises, not course homework as far as algo-facts lists.

Change: before the 4.1 figure. Before: "The six counterexamples side by side:". After: "The counterexamples for the
six wrong rules, side by side:". Why: the figure has five panels ((a) and (b) share one input).

## Check scripts

a04.py: transcriptions of GreedySchedule, BuildHuffman (+ the printed loop), Encode/Decode, GaleShapley match the
page line by line; the examples are recomputed, but several page numbers were not tied to the page text. Added 3
checks: the page states 49 / 57 / 58 for the weighted tape example; the page lists exactly the 11 fewest-conflict
classes; the trap-table rows for earliest start and shortest duration. a04x.py tested hard-coded data only (it never
read the page). Added a "page text" section (10 checks): the intervals on the page in 4.1 (a)/(b), (d), (e), (f), (g)
and 4.2 are exactly the checked counterexamples; book-figure answers 6 / 4 / 5; the 4.6(a) answer; the 4.8 costs 7
and 6; n(n+1)/2 in 4.10. Both scripts end ALL OK (a04.out, a04x.out saved).

## Runs

a04.py ALL OK; a04x.py ALL OK; tools/check.py --only 2-algorithms/04,concepts/greedy-algorithms,
concepts/interval-scheduling,concepts/huffman-codes,concepts/stable-matching: OK. No figure changed, so no
assemble and no screenshots.

## Book errata (verified on the rendered pages)

Confirmed errors:
- p. 170, Fig. 4.4 BuildHuffman: as printed "for i ← n to 2n − 1"; should be "for i ← n + 1 to 2n − 1" (printed:
  n iterations, leaf n overwritten, the last ExtractMin on an empty queue; the text's own count of 2n − 1 Inserts and
  2n − 2 ExtractMins fits n + 1).
- p. 174: as printed "the matching {Ar, Bs, Cq, Dt} is also stable"; should be: it is unstable — Dr. Quincy (at
  County) and Bedlam (with Dr. Shephard) prefer each other, and (q, B) is its only unstable pair; {As, Bt, Cq, Dr} is
  the unique stable matching for the p. 173 lists (brute force over all 24 matchings, twice independently).
- p. 162: as printed "subset X ∈ {1, 2, …, n}"; should be X ⊆ {1, 2, …, n} (also "for any pair i, j ∈ X" needs
  i ≠ j).
- p. 161, proof of Lemma 4.2: as printed "L[π(i + 1)]/F[π(i + i)]"; should be F[π(i + 1)].
Probable slip (not reproduced on the site):
- p. 174: "the Boston Pool algorithm can execute each offer in constant time" — the paragraph analyzes Gale–Shapley
  (Exercise 4.9 refers back to it as Gale–Shapley's O(n²) claim), and the Boston Pool order (footnote 11, p. 173)
  depends on all lists, so "Gale–Shapley" is almost certainly meant.
Not an error:
- p. 178, Ex. 4.3 figure: the shaded cover of size 7 is not a smallest cover (6 suffice), but the caption only says
  "a cover (shaded) of size 7", so nothing false is claimed. The page says exactly this.
Typos (not on the site): p. 162 "shown in in Figure 4.3"; p. 171 "computes an matching"; p. 174 "Dpref/Hpref" vs
"HPref"; p. 178 "As usual, If"; p. 179 Ex. 4.6(b) "the any Huffman tree", Ex. 4.11 "has to a unique".
Notation remark: p. 169 writes depth(T) for the depth of leaves 1 and 2 in T; with ties these need not be deepest
(random search found f = (1,2,10,1,5,1,4,8,5,1), first pair at depth 5, tree depth 6). The algebra is unaffected;
the page's proof does not use it.

## Remaining doubts

- The Ch 3 page (§3.5 key box, not mine) still says "The book's policy (and the course's)" for "no credit for an
  unproved greedy algorithm". The book's policy is verified; the course part is not in rubrics.txt / algo-facts.md
  (only the DP rubric's −1½). Coordinator: confirm or align with the Ch 4 wording.
- 4.6(a) is read with adversarial ties (every Huffman tree must be deep → Lucas L_{n−2}); the page also gives the
  favorable-tie answer F_{n−1}. The book probably expects Fibonacci F_n; the page's statement that Fibonacci is not
  the smallest is right under both readings.
- §4.2 says the book "assumes all start and finish times are distinct"; the book only says (in its story) that every
  class has a different start and end time. Harmless; not changed.
- Lemma 4.5 proof fixes "of depth d" before "we may assume T is full"; read d as the depth of the full tree. Not
  changed.
