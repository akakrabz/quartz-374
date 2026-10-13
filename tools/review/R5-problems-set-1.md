# R5 — review of worked problems, set 1

Reviewer R5, 2026-10-13. Pages: `content/problems/{induction-on-a-recursive-string-function, regular-expression-and-dfa-for-one-language,
fooling-set-and-grammar-for-one-language, two-language-transformations, a-product-construction-written-formally,
subset-construction-by-hand}.md`; check script `tools/checks/problems_1.py`; figures `tools/figs_problems1.py`.

## Method (all pages)
- Re-solved every part from the statement before reading the solution; compared answers, proofs, tables, runs.
- Checked each model answer against the rubric paraphrase in `/home/claude/work/book-facts.md`.
- Checked each trap / wrong answer / wrong construction on its counterexample (by hand and in the script).
- Checked every inlined SVG edge by edge against the page's tables (all match `tools/figs_problems1.py`).
- Book (WebFetch): §1.1 notation (`a·x` pair vs `x•y` concatenation, |w| and • definitions, Lemma 1.2, hypothesis phrasing);
  §2.3 (examples only, no design recipe); §3.5 (brute-force DFA design method); §4.5 (s' = {s}, A' and δ' through
  ε-reach, table columns S | ε-reach | accepting? | δ' per symbol).
- Script: read in full; it checks the pages' own automata, grammar, regex, tables, runs, fooling sets and traps
  against predicates written from the statements. Before: 98 OK, ALL OK. After my additions: 102 OK, ALL OK
  (`problems_1.out` saved).
- `tools/check.py --only <6 pages>`: only the allowed "wikilink target not found" errors
  (`0-toolkit/06-how-exams-are-graded`, `1-models-of-computation/04-nondeterministic-automata`). All other anchors resolve.

## induction-on-a-recursive-string-function
Checked: sort examples and unfolding; (a), lemma and (b) line by line (each step's justification); strong hypothesis,
three exhaustive cases, base case; traps (sort(y•0) look-alike and non-distributivity counterexample); rubric box.
Changes:
1. "The lemma is applied to y = sort(x), which is *not* shorter than w in general" → "The lemma is applied with
   y = sort(x), to the string sort(x)•1, which is exactly as long as w — but the lemma holds for every string y …".
   Why: false — |sort(x)| = |x| = |w| − 1 by part (a); the string that is not shorter is sort(x)•1.
   New check: |sort(x)| = |w| − 1 and |sort(x)•1| = |w| for all w = 1x, |w| ≤ 12.
2. "the first symbol of sort(x)•1 is not the 1 just attached" → "… (unless x = ε)". Why: for x = ε it is.
   New check added.
3. Exam box: "results from lecture, the notes, labs …" → "… the course notes …". Why: unambiguous (course notes,
   not the site's sources).
Doubt (left): "the cases w = ε and w = 0x unfold with the definitions alone" — case 0x also uses the hypothesis;
the contrast intended is "no lemma needed". Not changed.

## regular-expression-and-dfa-for-one-language
Checked: examples; run decomposition; 7-state DFA (table, meanings, figure), runs on 1001101 / 010101 / ε;
minimality and the 7-string fooling set; regex 1*00*11*00*11*0* and its English parts; the four wrong expressions
(languages exact, witnesses, infinitely many errors); DFA and regex rubric numbers. All correct.
Change: Sources "The run-by-run design follows the recipes of Erickson … §2.3 and §3.5" → "The DFA follows the design
method of Erickson … §3.5 (one state for each combination of values of a left-to-right scan's variables) …; the
run-by-run regular expression is ours, in the style of the book's examples in §2.3." Why: the book's §2.3 has no
design recipe (only examples); the recipe on the site's §2.3 page is the site's own.

## fooling-set-and-grammar-for-one-language
Checked: examples; fooling set 0* with z = 1^m (counting argument covers the m = 0 case with n+1 decompositions);
closure alternative L ∩ 0*1* = {0^n1^n}; grammar S → AB, A → 0A1 | ε, B → 1B0 | ε, nonterminal languages, both
inclusions; parse-tree figure (leaves spell 001110); the three wrong grammars on their witnesses; rubric box. All correct.
Change: description "a three-rule context-free grammar" → "a context-free grammar with three nonterminals, every one
described,". Why: it has five rules (the site's §5.1 counts C → ε | 0C1 as two rules).
New check: the finite set {ε, 0, 00} in the "finite set" trap really is a fooling set.

## two-language-transformations
Checked: both constructions re-derived and proved by induction for an arbitrary DFA (invariants as stated);
formal description complete (states, start, accepting, every δ incl. ε for (b), "no ε-transitions" for (a));
English meanings of states and accepting states; edge-case table (∅, {ε}, 1*, 0*, Σ*) — correct for every DFA;
parity example and run on 0110; figure (guess edges (E,0)→(E,1), (O,0)→(O,1) on 1; ε-edges (E,0)→(O,1),
(O,0)→(E,1)); all seven wrong constructions on their counterexamples; Delete1(Insert1({01})) = {01, 10}. All correct.
No change.

## a-product-construction-written-formally
Checked: examples; M1, M2 and meanings; product tuple and 9-row table entry by entry; runs on 0111 / 1001;
reachability; only the three dead states merge (7-state minimum); fooling set F of size 7 and the three-case suffix
rule on all 21 pairs; union trap; the claims about ∪, \, ⊕ (9) and L2\L1, complement of ∩ (7). All correct.
Change: fooling-set proof "Let x and y be distinct strings in F" → "Let x and y be arbitrary distinct strings in F".
Why: rubric wording, and the site's fooling-set template.

## subset-construction-by-hand
Checked: L(N) = 0*(01)*1*; ε-reaches; the 7-row table recomputed by hand in BFS discovery order (matches, incl. ∅ row,
5 accepting); DFA figure edge by edge; runs; traps (acceptance without ε-reach rejects ε, 0, 00, 0101; transitions
without ε-reach send 1 and 01 to ∅); other convention gives 6 states; rows {p,t} and {p} equivalent; 6-element fooling
set and the 15-entry suffix table (each shortest). All correct; convention agrees with the book's §4.5.
Change: trap "Tabulating all 16 subsets" — added "(A table of all 16 still describes a correct DFA, with nine
unreachable states, but it is not what was asked and it wastes exam time.)". Why: the trap sat under "Where subset
constructions go wrong", but the full power-set DFA (the book's formal Q' = 2^Q) is correct, only wasteful.
New check: the 16-subset DFA is equivalent to 0*(01)*1* and has exactly 7 reachable states.

## Remaining doubts
- Rubric point values (e.g. exam regex deductions 2/4/8, transformation 2+2+6) follow book-facts.md's paraphrase;
  not re-verified against the course website.
- The book's §4.5 tables never show a ∅ row (its examples never reach ∅); the page's ∅ row follows the definition
  and the site's concept page — correct, just not illustrated in the book.
