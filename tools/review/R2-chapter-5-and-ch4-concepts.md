# Review R2 — Chapter 5 and the Chapter 4/5 concept pages

Reviewer R2, 2026-10-13. Sources: Ch 4 and Ch 5 PDFs (WebFetch, focused questions), `moc-notes.tex`, `book-facts.md`.
Scripts run: `ch05.py` (ALL OK, 157 checks), `concepts_a.py` (ALL OK, unchanged), `concepts_b.py` (ALL OK, 68 checks).
`check.py --only <my pages>`: only "wikilink target not found" for `04-nondeterministic-automata` (27×) and
`0-toolkit/06-how-exams-are-graded` (1×), both still being written. All 36 anchors into the Ch 4 page match the
SPEC's fixed Ch 4 headings (slugs computed by hand).

## content/1-models-of-computation/05-context-free-languages.md

Checked: every definition, lemma and proof (5.1–5.4, incl. the shortest-derivation argument and the mutual
induction), the running example and its nonterminal languages, all grammars of the §5.4 table against the book
(WebFetch list of §5.4 grammars) and against their languages incl. ε, design examples and grading variants, the
§5.5 construction (book: ∅ → S → S etc.), the intersection/complement argument, the inherent-ambiguity claim
(standard; the book defines inherent ambiguity but gives no example — page lists it as original), recursive-automaton
definition and moves (match the book's (w, q, σ) semantics, stack top first), the trace on 001, Lemma 5.5 (book only
says "one module per nonterminal") and Lemma 5.6 rules (match the book), CNF definition, 2n − 1, CYK paragraph
(original; correct), the CNF algorithm and every row of the running-example table (match the book's step results and
final grammar), figure data (imported by ch05.py) and all five captions, cross-links into Ch 2/3 (multiples-of-4
tree, parity DFA s/t of §3.3).
Script: confirmed ~40 key claims are checked as stated (running example, Lemmas 5.1–5.4, §5.4 grammars, CNF grammar
and every conversion step, recursive automaton and trace, Lemma 5.6 grammar, closure languages).

Changes:
1. §5.9 step 3: "then delete every rule A→ε, except S'→ε if S' is nullable" → "then delete every rule A→ε, and add
   S'→ε if S' is nullable (the only ε-rule of the result)". S'→ε does not exist before step 3 (variants are
   non-empty), so the old wording loses ε; the book says *add*.
2. §5.9 step 0: added that S'→S is dropped again after step 2 when not needed, and that the book's rule (drop S'
   whenever it is not nullable; "necessary only when S ⇒* ε") fails when S is on a right side, e.g. S → 0S | 1.
   The page's condition was already right but was an unflagged deviation from the book.
3. §5.9 step 4: added "and delete every rule A→A (merging creates them, and so does step 3, e.g. S→S from S→SS)"
   (book removes A→A; without it step 5's "the unit-rule graph is now acyclic" is false).
4. Theorem 5.7 callout moved from the end of §5.8 to the start of §5.9 (the book states it in §5.9).
5. Figure ch05-regex-trees caption (tools/figs_ch05.py): "generates exactly the regular expressions over 0 and 1"
   → "... that use neither ∅ nor ε" (the grammar has no ∅/ε rules; the trap text above already says so).
   Regenerated (only this figure changed), assembled, screenshot checked light/dark.
6. Sources paragraph: verification bounds made accurate (not "up to 12" for the 3- and 6-symbol grammars); noted
   that the book's regex grammar is used without its ∅/ε rules and the corrected S' condition.
ch05.py: `cnf_convert` got an optional `book_drop` flag; 4 new checks (page's step-0 rule on S → 0S | 1 gives CNF and
0*1; the book's rule leaves S on a right side; step 3's only ε-rule is S'→ε on S → ε | SS | 0S1 | 1S0; step 4 drops
the S→S created by step 3). Re-run, `.out` saved.

Doubts (not changed): Lemma 5.4 on the page states L(S) = (01)* *and* L(A) = (10)*; the book's lemma states only
L(S), proving both. "G = (Σ, Γ, R, S)": the book lists the components without a tuple. "Chapter 6 opens with one
for exactly this language": §6.3 is the book's first TM example, whose printed version is flawed (book-facts).

## Concept pages

- **context-free-grammars**: definition, template (shortest-derivation induction is valid), traps, example
  0^a1^b0^c with b = a + c and its fooling set, rubric. Change: "Regular expressions are the special case without
  recursion — … S → ε | S1S for star" → "… that recurses only through the star" (the star rule is recursive).
- **parse-trees-and-ambiguity**: definition, leftmost-derivation correspondence, inherent-ambiguity example,
  S → 0S1 | 0S | ε with C(m, n) trees, unambiguous fix. No change.
- **chomsky-normal-form**: definition, Theorem 5.7, 2n − 1, recipe (steps 0–6 incl. "add S'→ε"), palindrome example
  step by step. Changes: trap "Removing ε-rules creates unit rules (X→P0 with P nullable gives X→0, but S'→P stays
  a unit rule)" → "(A→BC with B nullable gives the unit rule A→C)" — X→0 is not a unit rule and S'→P was not
  created by the step. "§5.8 (definition, Theorem 5.7)" → "§5.8 (definition, binary parse trees)", "§5.9 (Theorem
  5.7; …)". concepts_b.py: 1 new check for the new trap example; re-run, `.out` saved.
- **recursive-automata**: definition vs book (single accepting state, ε allowed, disjoint states, moves,
  acceptance), Lemma 5.5/5.6 constructions, the balanced-parentheses module, its run on () and its grammar. No change.
- **nfa**: definition and δ* with ε-reach (identical to the book's §4.3), ε-removal (Q' = Q, s' = s,
  A' = {q : ε-reach(q) ∩ A ≠ ∅}, δ'(q,a) = δ(ε-reach(q), a) — the book's), ends-in-01 example and trace. No change.
- **subset-construction**: definition with ε exactly as the book (s' = {s}, A' via ε-reach(S), δ' via ε-reach of
  each p), table for the p/q example, 3/5-state claims, k-th symbol from the end (NFA k+1 states, fooling set of
  size 2^k, suffix 0^(i−1) correct). Change: "at most 2^|Q| states, and that many can be needed" → "and
  exponentially many can be needed" — the example shows 2^k = 2^(|Q|−1), not 2^|Q|.
- **thompsons-algorithm**: gadgets (book text gives only the figures; notes and library agree on the 4 ε-edges of
  the star), invariant, state counts 14 and 6/5/2, 4 → 3 for 0*1, shortcut-star counterexample. Change: trap
  "then ε ∉ L(S*) unless ε ∈ L(S)" → "then the NFA for S* rejects ε unless ε ∈ L(S)" (L(S*) always contains ε).
- **state-elimination**: expression automaton vs book (R(q→s) = R(t→q) = ∅), rule for all pairs incl. p = r,
  factor 4 / Θ(4^n) (book), parity example both orders. Attribution: the current §4.8 PDF credits McNaughton and
  Yamada (1960), mentions C. Y. Lee (earlier the same year) and Kleene (1951); "Han"/"Wood" appear nowhere in the
  Ch 4 PDF text — the notes' "Han and Wood" is outdated. The page is right. No change.
- **kleenes-theorem**: Theorem 4.1 statement (matches the book's), conversion table, 14 → 5 (3
  accepting) → 2, 18 drawn / 26 literal → 9 (6 accepting) → 4 (book: "18-state monster", 9, 6, 4). Change:
  "Example — one full turn (the book's)" → "(the book's, plus the last arrow)" — the elimination step back to the
  expression is not in the book. Doubt: "up to 2^n states, sometimes necessary" is true (tight bound) but not shown
  on the site; left.
- **language-transformations**: both del0 constructions are correct for an arbitrary DFA (ε-moves, start,
  accepting sets; δ''(q,0) = ∅), template, traps, rubric (book-facts). §4.9's Lemma 4.4/4.5 constructions
  checked against the PDF for cross-reference. No change.
