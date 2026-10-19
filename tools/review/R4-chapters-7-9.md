# Review R4 — Chapters 7 and 9 and seven concept pages

Pages: `1-models-of-computation/07-undecidability`, `1-models-of-computation/09-nondeterministic-turing-machines`,
`concepts/{acceptable-and-decidable, diagonalization, halting-problem, undecidability-reductions, rices-theorem,
nondeterministic-turing-machines, cook-levin-theorem}`.
Sources used: Erickson Ch 6, 7, 9 PDFs (WebFetch, focused questions, including raw-text transcriptions of the
Cook–Levin constraints), `book-facts.md`, `moc-notes.tex`. Independent recomputation of the binary digits of π.

## Chapter 7 — 07-undecidability.md

**Checked (all against the book unless noted).** Definitions of Accept/Reject/Halt/Diverge(M) and the synonym list;
crash ⇒ Diverge (book Ch 6: a crashing machine neither accepts nor rejects). §7.2: Π = {w | 1^|w| in binary π}, the
book's (N+3)-state machine M_N, the counting-state description (state N reading a symbol rejects; blank accepts) is right;
π bits re-derived independently (run 1^6 at fraction bits 11–16; longest run in the first 4000 bits is 10, starting at
bit 645). Lemma 1 (book gives no construction; the page's swap / hang / reject→accept constructions are right, also
under the crash convention), Lemma 2, Corollary 3 (contrapositive, all four operations), Lemma 4 (serial ∩, parallel ∪,
the 1Σ*/Σ*0 example), Lemma 5 and its consequence. §7.4 encoding properties. Theorem 6 and the diagonal figure
(SR row = flipped diagonal, differs from row i at column i). Cantor (statement, sad set, f(w)=Accept(M) or ∅,
Y = Σ*∖SelfAccept). Theorems 7–9 proofs (SA^R, SHX, SDA as in the book). Theorems 10–11. Table of the four
self-referential languages. Theorem 12 (reduction SelfHalt → Halt) and the "Accept, Reject, Diverge undecidable;
Diverge not acceptable" paragraph. Direction box, reduction template ("does not accept" = rejects or diverges in the
⇐ case), traps, grading boxes (match book-facts rubrics). Theorem 13 proof (Accept → NeverAccept via M_w, opposite
answer); NeverReject/NeverHalt/NeverDiverge reductions (Diverge(M_w) = ∅ iff M halts on w); co-acceptability of
NeverAccept by dovetailing (original, correct). Theorem 14 (NeverDiverge → DivergeSame with Y accepting everything).
Rice: both forms as in the book; proof sketch incl. the ∅ ∈ 𝓛 case via the complementary property and Corollary 3
(AcceptIn(𝓛') = Enc ∖ AcceptIn(𝓛)). Corollary 15 (a)–(h) = book list; every witness pair in the added columns is
right (incl. (g) acceptor for SelfReject, (h) M_Reject or M_Accept when Accept(N) = ∅). Theorem 16 (𝓛_w, fix w).
Rejection/halting/divergence/decision variants = book statements; NeverDiverge = DivergeIn({∅}), NeverHalt =
HaltIn({∅}) witnesses right. ThisIsSparta (300 vs 301 steps), RevAccept (book: undecidable, no proof; the page's
reduction is right), trivial properties. RMMS: definitions (see change 4), theorem statement, Lemma 17 proof
(book's reduction from SelfDiverge, Accept(Y) ⊆ Accept(N)). Corollary 18 (a)–(h) = book list; every "condition that
fails" entry re-derived: (a) ∅→Σ*, (b) Σ* has no infinite finite subset, (c) ∅ ⊆ 0^n1^n, (d) 0^n1^n ⊆ Σ*,
(e) ∅ ⊆ SelfReject, (f) SelfReject ⊆ Σ*, (g) the property is monotone and compact, finitely acceptable would make
SelfDiverge acceptable, (h) monotone fails unless Accept(N) = Σ*, then compact fails. Theorem 19 (book: accept after
more than |Q| blanks; the page's |w| + |Q| step bound holds with "reads" = head on the cell, as the script checks),
Theorem 20 (book's construction: p1→q2, p2 right, p3 left; three right moves then three left before accepting; reduction
from Accept); LeftThree acceptable. Rules of thumb = book's lists (+ NeverLeft/LeftThree). Classification of every
named language (decidable / acceptable / co-acceptable) consistent across text, table, figure and concept pages.
Figures: four-languages, diagonal table, classes Venn (both "neither" languages: complements unacceptable by
Corollary 18 (b), (d)), reduction, NeverLeft run (start,start,p,p,q,r,q,r; first repeat q at cells 4, 6).
`tools/checks/ch07.py` checks the π bits, Lemma 1, Lemma 4/5 simulations, diagonal data, Cantor, Rice witnesses,
ThisIsSparta, the NeverLeft decider and bound, Theorem 20 — re-run: ALL OK (output unchanged).

**Changes.**
1. Abstract: "Running a supposed decider on its own encoding and doing the opposite — diagonalization — proves that
   SelfReject is undecidable" → "Running a machine built from a supposed decider on its own encoding — …". Why: for
   SelfReject no flip is used (SR itself is contradictory); flipping SR gives a consistent machine, exactly the trap
   that `concepts/diagonalization` warns about.
2. §7.2 intuition: "no single algorithm answers infinitely many questions" → "no single algorithm answers all of
   infinitely many questions correctly". Why: the old wording is literally false (deciders answer infinitely many
   questions).
3. Classes figure caption (`tools/figs_ch07.py`, regenerated, `assemble.py` on this page only; screenshot checked):
   "The self-referential languages and Accept, Halt sit in the left lune: acceptable, so their complements — …— are
   not." → "SelfReject, SelfAccept, SelfHalt, Accept, Halt and LeftThree sit in the left lune: acceptable but
   undecidable, so their complements (such as SelfDiverge and Diverge) are not acceptable." Why: SelfDiverge is
   self-referential but in the right lune, and "acceptable, so the complement is not" is a false inference
   (decidable languages are acceptable and co-acceptable).
4. Sources: added that *monotone* quantifies over acceptable supersets only, whereas the book says "every superset".
   Why: deviation from the book (needed: with "every superset" Lemma 17's machine N need not exist); REVIEW-SPEC asks
   that deviations be stated.

## Chapter 9 — 09-nondeterministic-turing-machines.md

**Checked.** NTM definition (book's δ has domain Q × Γ; the page excludes accept/reject, consistent with Ch 6 and
harmless since halting configurations are leaves); δ = ∅ → reject; computation tree; acceptance (some branch) /
rejection (every branch, so finite — König) / neither; N and N′ (tree on 011, 010 behavior, swapped N′ accepts
everything). TIME/NTIME/SPACE/NSPACE (book: "decided by multi-tape machines"; book leaves P, NP and the NTIME time
measure implicit — the page's "every branch" and P, NP definitions are standard and flagged as original); O(t log t) /
O(t²) tape simulations. Theorem 1 statement and bound O(t² r^{2t}); queue simulation; analysis (O(r^t) configurations
× O(t) cells; O(t) trips of length O(t r^t) per configuration; O(t r^t) with two tapes/heads) = book. DFS remark.
BFS order (accept dequeued 7th) and DFS path in the figure. Advice: Ω, δ_N = {δ_M(q,a,ω)}, example advice
121/122/221/222. **Book's rejection statement** ("N rejects w iff M rejects (w,x) for all x ∈ Ω*") is wrong whenever
the tree has an infinite branch and no accepting leaf, under any convention for exhausted advice (reject → all x
rejected; default option → a machine whose infinite branch needs the other option); with "diverge on exhaustion" the
⇒ direction fails instead. The page's form (some t, all x of length t reject within t steps) proved both ways.
Dovetail pseudocode = book; correctness argument; Σ s r^s ≤ 2 t r^t; O(t r^t) three tapes, O(t² r^t) one tape
(= book). NTIME(f) ⊆ ∪_c TIME(c^{f}) for f ≥ n: true (BFS or dovetailing run directly on the multi-tape machine;
see change 1). NP verifier definition = book (max{1,|w|^k}). **Cook–Levin:** the book's window is cells 0…N+1 with
sentinel N+1, advice n+2…N, transitions and acceptance for i ≤ N; a run that accepts at step N with a right move
puts the head on cell N+1, which the book's formula forces false — the page's window 0…N+2 (advice n+2…N+1,
transitions 1 ≤ i ≤ N+1) fixes it. Raw-text transcription of the book's constraints confirms index typos
(T_{t,i−1,a}, Q_{t−i,i+1,p}, T_{t,i+1,a} on the right of the Q constraint; boundary printed Q_{t,i,q} for Q_{t,0,q});
the page's formulas are correct (Q from i−1 with +1 or i+1 with −1 at time t−1; T written by the head or unchanged
when no head on cell i). Variable count (N+1)(N+3)(|Q|+|Γ|); O(N²) size; O(n^{2k}) + O(n^{2kc}). Intuition / trap boxes.

**Checks added to `tools/checks/ch09.py`** (old checks untouched; output saved, ALL OK, 24 checks):
- advice view, page's form ⇔ BFS rejection (N, N′ on |w| ≤ 6; 200 random NTMs);
- the book's form fails on 010 (N with "reject on exhausted advice"; N with a give-up option in *loop* with "take
  the last option");
- Φ_w with the page's window agrees with direct simulation for a second toy verifier that accepts with a final
  right move (and with the original evaluator on the first toy verifier);
- with the book's window 0…N+1 that verifier's accepting run (w = 0, N = 3, head on cell 4 at time 3) is lost;
- (for the concept-page change below) with w = 0, N = 4 the forced assignment accepts at time 3 and leaves the head's
  cell empty at time 4, so only the advice cells may be required to hold exactly one symbol.

**Changes.**
1. §9.3: "Theorem 1 gives one in the other direction" → "Theorem 1, whose simulation works the same way for multi-tape
   machines, gives one in the other direction". Why: Theorem 1 is stated for the one-tape machines of §9.1; going
   through a one-tape NTM first would give 2^{O(f²)}, not c^{f}.
2. Sources: added "we also correct a few index typos in the printed constraints (every variable on the right of a
   transition constraint refers to time t−1, and the left boundary is cell 0)"; and the check sentence now mentions
   the advice view and the two windows. Why: deviation from the book must be stated.

## Concept pages

- **acceptable-and-decidable**: definition, Lemma 5, recipe, table (all 10 rows re-derived; complement of NeverAccept
  acceptable by dovetailing — correct), traps. No change.
- **diagonalization**: Cantor, table argument, template, traps (the SelfReject "no flip" trap is right: SR^R is
  consistent), doubled-input example (unique parse of ⟨M⟩⟨M⟩). No change.
- **halting-problem**: Theorem 12, two-step proof, one-machine recipe, traps, HaltBlank example (Rice's halting theorem
  with 𝓛 = {L | ε ∈ L}). No change.
- **undecidability-reductions**: direction rule, template, traps, FiniteAccept example (|x| as step budget). No change.
- **rices-theorem**: statement, variants, proof idea, recipe, traps (wrong variant: HaltIn({Σ*}); non-empty is
  acceptable), example. No change.
- **nondeterministic-turing-machines**: definition, Theorem 1, recipe, traps, both examples. No change.
- **cook-levin-theorem**: change: "each cell holds exactly one symbol" → "each advice cell holds exactly one symbol".
  Why: in this formula a cell whose head has halted becomes empty (no transition from accept/reject), so a global
  exactly-one constraint would make Φ_w unsatisfiable whenever M halts before time N; the book and Ch 9 constrain only
  the advice cells at time 0. Rest (NP definition, sizes, SAT example: only a=T, b=F; adding ¬a∨b unsatisfiable)
  checked; `concepts_c.py` unchanged, ALL OK.

`tools/check.py --only <my pages>`: only "wikilink target not found" for 0-toolkit/05, 04-nondeterministic-automata,
2-algorithms/index.

## Remaining doubts

- §9.6 / concept page: the NP definition does not say over which alphabet advice strings range, while the tableau lets
  each advice cell hold any tape symbol (blanks included). The reduction is sound if "advice string" means any string of
  tape symbols; with the book's x ∈ Σ*, a satisfying assignment could use tape contents the definition says nothing
  about. The book has the same gap. Left as is.
- Crashing branches of a nondeterministic machine are covered neither by the book nor by the page (a crashed branch
  ends in no reject leaf, but the queue simulation would discard it and could reject). `ch09.py` treats a crash as
  rejection for its random machines. Left as is.
- Theorem 13's proof says M_w "runs forever (if M diverges on w)"; with crash ⊆ Diverge it may crash instead. The
  conclusion Accept(M_w) = ∅ is unaffected. Left as is.
