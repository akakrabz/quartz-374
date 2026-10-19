# Review R3 — Chapters 6 and 8 and the concept pages turing-machines, church-turing-thesis, universal-turing-machine

Reviewer R3, 2026-10-13. Sources: Ch 6, Ch 7 (§7.1 only) and Ch 8 PDFs via WebFetch (focused questions, several
asked twice for exact strings), `moc-notes.tex`, `book-facts.md`. Scripts: `ch06.py` (ALL OK, 45 checks),
`ch08.py` (ALL OK, 26 checks), `concepts_c.py` (ALL OK, 36 checks); `.out` files saved. `check.py --only` on the five
pages: OK (no errors at all). Figures: all six rendered (light + dark) and compared with the tables/captions; no
figure changed. Page re-rendered in light mode around the edited §6.2 and §6.8 callouts.

## 1-models-of-computation/06-turing-machines.md

Checked: formal definition against the book's §6.2 (Γ, □, Σ, Q, δ on Q∖{accept,reject}, ±1 moves, configurations
(q,x,i) ∈ Q×Γ*×ℕ, the step relation with |x| = i, crash at position −1, accept/reject via ⇒*, "rejects" ≠ "does not
accept", recognize/decide and the synonyms); history paragraph and Church–Turing box against the chapter opening and
footnote 1 (age 23 = "a few months before his 24th birthday", Church first, "appeals to intuition"); §6.1 reversal
O(n)/Ω(n²). The 12-state 0^n1^n0^n machine: English description, table and figure (all 20 rows/edges) agree; traced
010 by hand (14 steps, all 15 configurations), 0010, 0110, 0101; derived 4k²+9k+1 by hand (6k+1 for phase 1,
k(4k+1) for the rounds, 2k for verify); no-crash argument; rejection list. Book's §6.3 machine: table obtained from
the PDF (seek0/0 printed with +1; the text's trace moves left), traced 001010 by hand (accepted), ε rejected.
§6.4 variant list and the stay-put construction against the book (book leaves the start/accept/reject states of M′
implicit; the page's (start,0), (accept,0), (reject,0) is a correct completion). §6.5 output/divergence definitions
and the shift machine against the book; increment table by hand. §6.6 costs against the book (k heads and k tapes
Θ(t²) on one tape, O(t log t) on two; doubly infinite O(t); marked palindromes O(n)/Ω(n²)). §6.7 bounds: book states
O(t)/O(t²) for recursion and O(kℓ), O(t²ℓ), O(t³ℓ²) for memory — match. §6.8 encodings against the book; the
example's codes, block, ⟨010⟩ and encoded configuration by hand. ch06.py checks the machine (all inputs ≤ 14),
trace, step formula, rejection points, book machine, stay-put (+300 random machines), shift, increment, encodings and
a string-level U — as stated on the page.

Changes:
1. §6.2 configuration: "(followed by infinitely many blanks, which are not written)" → "(followed by infinitely many
   blanks; trailing blanks may be written or left out, so (q,x,i) and (q,x□,i) are the same configuration)". Why:
   with blanks never written, the step rule (p,xay,i) ⇒ … cannot fire when the head is on a blank past x (e.g. step
   3→4 of the 010 trace); the book says trailing blanks are ignored.
2. §6.2 four outcomes: "M runs forever (diverges) on w" + "M halts on w if it accepts or rejects w" → "M runs forever
   on w" + "M halts on w if it accepts or rejects w; otherwise — if it crashes or runs forever — M diverges on w.
   (Chapter 7's set Diverge(M) therefore contains the inputs on which M crashes.)". Why: the book uses "diverges" for
   "does not halt" (§6.5 M(w)↑; §7.1 Diverge(M) := Σ*∖Halt(M)), and so do the Ch 7 page, the notation page and
   acceptable-and-decidable; the old wording made crash and divergence disjoint, contradicting §6.5 of the same page.
3. Synonym table: "recognizable" → "recognizable (the book's word in §6.2)". Why: the book's §6.2 uses recognizable;
   "acceptable" only from Ch 7.
4. Missing-transitions trap: "tables and diagrams always leave most transitions out" → "usually leave many". Why:
   overstatement (the shift machine on this page is complete).
5. §6.4: "(and so also run forever on the same strings)" → "(so they also diverge on the same strings, although one
   may crash where the other runs forever)". Why: false with four outcomes; the book only requires same accepted
   and same rejected strings.
6. §6.4 example: "many textbooks let the final transition into accept stay put" → "some definitions let …". Why:
   unverifiable generalization.
7. §6.3 book-machine trap: added "the printed table says +1 there, a typo". Why: the page fixed a book typo without
   saying so (SPEC: say so); the check already shows the printed +1 rejects 010.
8. §6.7: removed "(and any arguments)" from the call-stack record. Why: the O(t) bound (book's) is for records that
   only name a state; arguments of unbounded size break it.
9. §6.8 States bullet: added "The book fixes no code for accept, but U has to recognize it, so fix one as well; this
   site uses ⟨accept⟩ = 0⋯01." Example: added ⟨accept⟩ = 0001 (the value ch06.py already used). Why: step 3 of U
   ("if q = accept, accept") needs a known accept code; ⟨M⟩ carries only reject and blank codes, and a state whose
   transitions all reject is indistinguishable from accept in ⟨δ⟩. The concept page's example already uses 01.
10. §6.8 example: added a note that the book's own example lists ⟨start⟩ = 111 (and uses it in the initial
    configuration) but writes start as 001 inside its encoded transitions — a typo. Verified twice by WebFetch
    (blocks [001•001|010•011•1], [001•100|101•011•1], [100•011|001•011•1]; 001 is assigned to no state).
11. §6.8 recipe step 4: added "(If the head would move left from the first cell, M crashes; then U must not answer
    either — it can simply loop forever.)" Why: the key box claims U rejects iff M rejects; the recipe was silent on
    crashes (so is the book).
12. Sources paragraph: mentions the accept-code convention and the 001 remark.
ch06.py: U now derives start = 1…1 and accept = 0…01 from the reject code instead of reading STATE["accept"];
added checks: accept = 0001 = 0…01; U gives no answer when M crashes (crashing machine, all inputs ≤ 6); the book's
three printed blocks differ from the correct ones exactly in the start code 001 (unassigned) vs 111.

Doubts (left as is):
- "Chapter 8 replaces U by much smaller universal systems" — loose (Ch 8 presents other universal models, not
  smaller U's); not wrong enough to edit.
- Figure caption "one round in" for (reset, #0x1x0, 3): the configuration is in the middle of round 1.
- §6.4 list item "halting by moving off the left end" is not in the book's list (the book has "declare such a move
  invalid" and crash-as-rejection); harmless, all variants are equivalent.
- The exam box's "Turing machines appear there mostly through undecidability" is a forecast, not a course fact.

## 1-models-of-computation/08-universal-models.md

Checked against the book's Ch 8 (§8.1 U; §8.2 two-stack via two restricted tapes; §8.3 counter-machine definition
δ: Q×{0,+}^k → Q×{−1,0,+1}^k, three counters via binary halves + scratch (page generalizes to base |Γ|, correct),
2^a3^b5^c, the (n,0,0)→(2^n,0,0) recipe, the HARD exercise with [Barzhdin 1963, Yao 1971, Schröpel 1972]; §8.4
Conway 1987, 2^(n+1) ↦ 3^(f(n)+1), "started on 1 outputs 1 or loops" (both are exercises in the book); §8.5 PCP
definition, a/b/c dominoes, tag-machine remark, three long-solution instances (75; 4 pairs "total length 451"; 528);
§8.6 mortality, 15×15 / 3×3, CHHN 2014; §8.7 Reif–Tygar–Yoshida 1994, (x,y) = left/right tape halves, quadratic
mirrors or refraction; §8.8 is only a placeholder in the book (no Wang/Berger); §8.9 term definition, SKK(IS)
example, R reduction and the six-step SII(S(KI)(SII)) sequence — identical to the page's, and the book does not fix
an order). Re-derived: two-stack step, counter encodings, FRACTRAN start-at-1 argument, PCP solution and minimality,
matrix products, single-matrix nilpotency, every combinator step under both stated orders, and the
leftmost-outermost cycle SII(I^kT) → SII(I^(k+1)T) in k+5 steps. Figures (two stacks, PCP) agree with ch08.py data.

Changes:
1. §8.2: "one step of a Turing machine is a pop, a state change, and one or two pushes" → "a pop, a state change and
   a push — plus, for a move left, moving the top symbol of the left stack over to the right stack". Why: a left
   move needs two pops and two pushes (the page's own figure caption says so). ch08.py: two_stack_run records the
   operations; new check: right moves (1 pop, 1 push), left moves (2, 2).
2. §8.4: "Conway's [455/33, …, 1/3]" → "[455/33, …, 1/3]". Why: no source found attributing this program to Conway
   (it circulates as an example without attribution; the book gives no example program). Check name and Sources
   adjusted.
3. §8.5 example: added "(the book prints 110110100 here, a typo)". Verified by WebFetch twice (the extracted line
   reads "gives us 110110100 for both concatenations"); cbca spells 110011100. ch08.py: report check added.
4. §8.5 long solutions: "The book lists three-domino instances whose shortest solutions need 75 dominoes, and others
   that need hundreds. Searching harder does not help in general — that is what undecidability means." → names the
   instance (0/001), (001/1), (1/0) (75 dominoes), "others whose shortest solutions use hundreds", and "No computable
   function of the instance bounds the length of its shortest solution: with such a bound, searching up to it would
   decide PCP." Why: the old last sentence was vague and not what undecidability means. ch08.py: new complete
   breadth-first search (overhangs pruned only when they cannot be cancelled in the remaining steps): no solution
   with ≤ 74 dominoes, a verified one with 75 (2 s).
5. Sources paragraph: misprinted string, Wang section is a placeholder in the book, 75 now checked, longer solutions
   and matrix sizes cited.

Doubts: the 528-domino instance (0/00010, 010/01, 100/0) could not be confirmed (search runs out of memory); the
count constraint #a = #c = k, #b = 2k (4k = 528) is consistent with "528 dominoes". The 451 instance's unit is unclear
in the book ("total length"); the page does not quote it. PCP-figure caption "which is what makes the problem hard"
is loose intuition; left.

## concepts/turing-machines.md

Checked: definition, outcomes, accept/decide, the 0^n1^n decider table (11 transitions), no-crash argument, 0011 in
15 steps (by hand), 0101 rejection at skip1, pass lengths 4m+1 (total 2k²+3k+1), O(n²), trap examples, anchors.
concepts_c.py checks these as stated. No change.

## concepts/church-turing-thesis.md

Checked: statement, thesis-vs-theorem, recipe (allowed/not allowed steps), traps, dovetailing pseudocode and the
max{j,s} bound. Change: "every model proposed since 1936" → "every reasonable model …". Why: overstatement (finite
automata, primitive recursion, … compute less); the chapter page already says "reasonable".

## concepts/universal-turing-machine.md

Checked: definition, encoding summary, recipe, traps, example (⟨M⟩ = [00•00][[11•10|01•10•1]], ⟨10⟩, both initial
configurations, accept after one step, reject on 01). Change: added "(U must also recognize accept; the book leaves
its code open, and this site uses 0⋯01)" to the encoding summary — same reason as Ch 6 change 9; the example's
accept = 01 fits. concepts_c.py: added a check that the example's codes follow start = 1…1, reject = 0…0,
accept = 0…01.

## Statements also on pages not assigned to R3

- 0-toolkit/05-review-turing-machines-and-undecidability.md (§6.8 summary) lists ⟨start⟩ = 1⋯1, ⟨reject⟩ = 0⋯0 and
  "if q = accept" logic without an accept code; could add "⟨accept⟩ = 0⋯01 (site convention)".
- 1-models-of-computation/07-undecidability.md line 15: "can do three things with an input: accept it, reject it, or
  run forever — diverge" (crash handled two paragraphs later); consistent with the new Ch 6 definition, but "run
  forever — diverge" equates the two words.
