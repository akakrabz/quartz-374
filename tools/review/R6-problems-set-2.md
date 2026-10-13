# R6 — review of worked problems, set 2

Reviewer log (2026-10-13). Pages: `content/problems/{state-elimination-by-hand, proving-what-a-grammar-generates,
cnf-conversion-step-by-step, designing-a-turing-machine, undecidability-by-reduction-and-by-rice}.md`.
Check script `tools/checks/problems_2.py` (re-run after edits: ALL OK, saved to `problems_2.out`).
`tools/check.py --only <these pages>`: only the expected "wikilink target not found" for
`1-models-of-computation/04-nondeterministic-automata` (page still being written).

Book claims verified with WebFetch on the chapter PDFs: §4.8 normal form (s with no incoming, t ≠ s with no outgoing
edges, added with ε-edges), update rule, "factor of 4 / Θ(4^n)", Lemma 4.3; §5.3.1 (Lemma 5.3 uses a minimum-length
derivation; induction on derivation length offered as an alternative); §5.8 CNF definition; §5.9 steps 0–6 in the
order the CNF page uses, S' → ε added when S' is nullable; §6.2 "the machine crashes" when the head position becomes
negative, crash = neither accept nor reject; §6.3 "unspecified transitions lead to the reject state"; §6.6 marked
palindromes O(n) with two heads, Ω(n²) with one; §7.11 Rice (both forms; proof reduces from Halt via WTF; names
M_Accept, M_Reject, M_Diverge); §7.12 RMMS for sets of acceptable languages, Lemma 17; Lemma 5; Corollary 15(c);
Accept undecidable ("nearly identical arguments" after Theorem 12).

## state-elimination-by-hand

Checked: the problem, DFA and its meanings; step 0; every new label of steps 1–3 (re-derived by hand, all four pairs
of step 1 including p = r); both figures against the text (every edge, direction and label); answer (b) by the
first-return argument; trap expression ((1+00)(0+11))* (subset of L, misses (01)^k); sanity checks (length 2, 3, 4
lists complete, block differences mod 3); order q0, q1, q2: all nine labels of step 1, four of step 2, final
expression; symbol counts 10/28 by hand, 22 by hand for q1, q0, q2, the remaining orders by the 0↔1, q1↔q2 symmetry
(script confirms all six with the library); mirror expression; exam box against the rubric. Script checks the same
automata and expressions as printed.

Changes: none.

Doubts: none. (Counts are of 0/1 occurrences; ε is not counted — consistent with the page.)

## proving-what-a-grammar-generates

Checked: list of generated strings of length ≤ 6 (12 strings) and the two non-examples; (a) all three cases,
legality of (m−1, n−1) and (m−1, 0), exhaustiveness, the m = 3, n = 1 derivation; (b) all three cases, |x| = |w|−3
and |w|−1, x = ε; the ε paragraph against §5.3.1 (shortest derivation / derivation length — matches the book and the
Ch 5 page); S → SS counterexample 0110; the 0011 two-derivation trap; C(m, n) parse trees; unambiguous grammar;
rubric points.

Changes:
- Trap in (b): "Not justifying |x|<|w| — harmless here, fatal …" → "— true here, but it is the reason the hypothesis
  applies, so say it; fatal …". Why: in a box titled "Where (b) loses points", "harmless" contradicted the page's own
  exam box (the 2 points for using the hypothesis correctly are earned exactly by this check).
- Exam box: "Midterm-1-style exams ask for a grammar with a description of each nonterminal and no proof" → "… ask for
  a grammar without a proof (homework also asks for a description of each nonterminal)". Why: book-facts and every
  other page (Ch 5, concepts/context-free-grammars, fooling-set-and-grammar) state the nonterminal descriptions as a
  homework requirement; exam grammars are graded on syntax and correctness only.

Doubts: none.

## cnf-conversion-step-by-step

Checked against the Ch 5 page's §5.9 recipe (and the book): every intermediate grammar re-derived by hand (step 0
new start; step 1 P → 0B, B → S1; nullable {S, S'}; step 3 variants S → S, B → 1, S' → ε; step 4 self-loop deleted;
step 5 reverse topological order, P unreachable; step 6 T0, T1); final grammar in CNF; languages of S', S, B; both
traps (no B → 1 ⇒ only ε; S' processed first ⇒ S' → P survives); the 7-step leftmost derivation of 0011; summary
table rows equal the text.

Changes:
- Frontmatter description: "with the six steps of the textbook algorithm" → "with steps 0–6 of the textbook
  algorithm". Why: the book's algorithm (and the page) has seven steps, numbered 0–6.

Doubts: none.

## designing-a-turing-machine

Checked: table vs English recipe vs state meanings vs figure (all 17 drawn edges; 20 transitions); every row of the
01#01 trace re-simulated by hand (18 steps); the 01#00 rejection (seek1 reads 0 in cell 4 at step 10, reject at step
11); the list of missing transitions that occur (the never-occurring ones, e.g. start on x, are rightly omitted);
halting argument; the 2n²+3n+2 bound (a round is ≤ 2n−1 steps, so the bound is loose but valid); exact count per
phase (k−i+2, i, i, k−i+1 ⇒ 2k+3 per round, k+2 at the end, 2(k+1)²); left-end trap against §6.2 ("crashes");
book's §6.6 remark; the table re-transcribed independently and simulated on all inputs of length ≤ 10.

Changes:
- (c): added after "rounds of 7 steps end at steps 7 and 14": "Even lengths have no string w#w, but w#w0
  (n = 2k+2) runs the same k rounds and is rejected when check reads the final 0: again 2(k+1)² = n²/2 steps."
  Answer (c): added "(for even n, w#w0 takes n²/2)". Sources: added "and as many on every w#w0". Why: the Θ(n²)
  claim needs a lower bound for every large n, but the page gave one only for odd n (w#w has odd length).
- `problems_2.py`: new check "even lengths: on w#w0 (n = 2k + 2) it rejects after 2(k+1)^2 = n^2/2 steps, for every w
  with k <= 7". (Independent simulation: the true worst case for even n ≤ 10 is a little larger, e.g. 11 for n = 4,
  which is consistent with the stated lower and upper bounds.)

Doubts: none. Rendered the changed part (light mode): fine.

## undecidability-by-reduction-and-by-rice

Checked: reduction direction (Accept → AtLeastTwo, decider built for Accept); M' (same as the Ch 7 page's M_w);
⇒ (Accept(M') = Σ*) and ⇐ covering reject and diverge (Accept(M') = ∅); DecideAccept halts; the three reduction
traps; Rice: property as a set of languages, Y = M_Accept and N = M_Reject with transitions and languages, AcceptIn
variant, the RejectIn remark (witnesses swapped correctly), "book's proof uses Halt" (true); Quick374 decider and the
two same-language machines; the bounded look-alike (in 374 steps the head reads only cells 0–373; length-374
argument; 2^375 − 1 strings); dovetailing acceptor and the one-at-a-time counterexample; complement not acceptable by
Lemma 5; RMMS cross-check (monotone, compact, finitely acceptable; "at most one string" not monotone ⇒ Lemma 17;
non-encodings form a decidable set, so they change nothing); rubric points.

Changes: none.

Doubts: the parenthetical in (c) "count it [a crash] as halting or not, as your definition of 'halts' says" is
correct but could simply say that, by the page's definition, a crash is not halting (so the decider rejects). Left
as is (not an error).

## Noticed on pages not assigned to me (not edited)

- `concepts/chomsky-normal-form.md`, trap 2: "Removing ε-rules creates unit rules (X → P0 with P nullable gives
  X → 0, but S' → P stays a unit rule)". The parenthetical does not illustrate the claim: X → 0 is a terminal rule,
  and S' → P existed before step 3. A real instance is A → BC with C nullable giving A → B (or S → SS giving S → S).
