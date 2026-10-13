# Review R1 — Chapters 1–3 and their concept pages (2026-10-13)

Method: read every page in full (figures through captions, SVG labels and the figure scripts); re-derived each
definition, proof step, example, table entry and trap; compared numbered results, section titles and examples with the
chapter PDFs (WebFetch); read the check scripts against the page text and ran them; ran `tools/check.py --only` on all
assigned pages.

## 1-models-of-computation/01-strings.md

Checked: definitions of string, |·|, •, w_i, w[i..j], prefix/suffix/subsequence/proper (book §§1.1–1.5); Lemmas 1.1–1.3
and all three proofs line by line (every line justified, hypothesis applied only to strictly shorter strings); §1.4
three-case proof with the hypothesis quantified over x', y' (as in the book) and the four (z, x', y') triples; the
recursive-function table (#, ^R, powers, complement, swap: book exercises 5–8, 10) and every listed identity; the model
proof of (wx)^R = x^R w^R; examples (STRING, NOWHERE, HEADACHE, MEATBALL/METAL are the book's); counts n+1, n(n+1)/2, 2^n;
rubric numbers. ch01.py checks these literally; ALL OK.

Change:
- §1.4 trap. Before: "each step below applies the claim … to a shorter z, but with *other* second and third arguments".
  After: "… to a shorter z, and three of the four steps use *other* second and third arguments". Why: step 3 uses
  (v, x, y), i.e. the fixed x and y; the trap's own last sentence (and ch01.py) say exactly that.

Doubt: the §1.3 template follows the book's boilerplate closely (on purpose: exam boilerplate). Left.

## 1-models-of-computation/02-regular-languages.md

Checked: §2.1–2.2 definitions and examples ({0,00}{0,00}, {0,11}*); Lemmas 2.1–2.3 against the book (statements match);
Arden proof (uniqueness is the direction that needs ε ∉ A; A*B is a solution for every A; citations 2.1(a,d,e,g),
2.2(a,b) correct) and both examples; the DFA-solving derivation; the table (all 11 expressions and descriptions are the
book's; ε-membership of each description consistent); design examples, tests and wrong answers; rubric numbers;
regexen and the {ww} fooling set; tree sizes 10 and 29; subexpression examples; Lemma 2.4 proof; Lemma 2.5 construction
and examples; rev(R) example; counting argument (digits 1–7 in base 8; L_α; same as the book); parentheses fooling set.

Changes:
1. §2.3, after the table. Before: "Chapter 4 shows how to derive such an expression from the three-state DFA that tracks
   the remainder mod 3." After: "Chapter 4 derives it by state elimination from a DFA that tracks the remainder mod 3,
   with a separate non-accepting start state (the three remainder states alone would also accept ε, which the expression
   does not match)." Why: the expression excludes ε; the book's §4.8 DFA has a start state s with no incoming edges,
   separate from the accepting remainder-0 state (unsimplified result 00*+(00*1+1)(10*1+01*0)*10*). Two checks added
   to ch02.py (4-state DFA ≡ expression, minimal 4 states, book's unsimplified form equivalent; 3-state DFA = ε + expression).
2. Lemma 2.4 and Lemma 2.5 statements were word-for-word copies of the book's sentences. Paraphrased, same meaning:
   "If a regular expression does not use the symbol ∅, then its language is not empty." / "Every regular language other
   than ∅ is the language of some regular expression that does not use the symbol ∅."
3. Lemma 2.5 proof, first sentences. Before: "A direct induction fails: in the case R = S+T, one of L(S), L(T) may be
   empty, and then the hypothesis says nothing about it. So prove a **stronger** claim about every regular expression R:
   …". After: "A structural induction proves a claim about *every* regular expression, and the subexpressions of an
   expression with a non-empty language can have empty languages (the ∅ in 0+∅). So state the claim in a form that holds
   for all of them: for every regular expression R, …". Why: the disjunction "L(R) = ∅ or R has a ∅-free equivalent" is
   logically equivalent to "if L(R) ≠ ∅ then R has a ∅-free equivalent", and induction on that implication goes through
   directly (case S+T with L(T) = ∅: L(S) = L(R) ≠ ∅, so the hypothesis applies to S). The book uses the disjunction and
   claims neither failure nor strengthening. Consequential edits: the sentence after the proof ("Strengthening the claim
   so that the induction goes through is the same move as …" → "Stating the claim so that it covers every object the
   hypothesis will be applied to — here every subexpression, even one with an empty language — is the same move as …")
   and the Summary bullet ("strengthen the claim when a case gets stuck (Lemma 2.5)" → "the claim must hold for every
   subexpression, even one with an empty language (Lemma 2.5)"). One check added (0+∅ non-empty, subexpression ∅ empty).

ch02.py: 3 checks added; ALL OK; ch02.out saved.

## 1-models-of-computation/03-finite-state-machines.md

Checked: mod-5 DFA (all 10 drawn edges = (2q+a) mod 5) and the run on 00101110110 (0,0,0,1,2,0,1,3,1,3,2,4; 374 = 5·74+4);
DFA definition and δ* identities; parity claim, proof and template; §3.4 numbers against the book (Swiss railway clock,
720 states; Rubik's cube 519,024,039,293,878,272,000 ≈ 5.2·10^20, 12 quarter turns); contains-11 counts (14 possible,
10 reachable — the book's §3.10 figure; 5 with the last symbol only; minimal 3); product accepting sets for ∩ ∪ \ ⊕ and
the complement; Lemma 3.1 and proof; Theorems 3.2, 3.3 and Corollaries 3.4, 3.5 against the book; every fooling-set table
row for arbitrary i ≠ j (Lemma 3.9 uses 0* in the book, as stated); closure alternative; Myhill–Nerode statement (matches
the book, including "regular iff every fooling set is finite") and sketch; Moore's algorithm, O(σn^3), O(σn^2), Hopcroft
O(σ n log n); mod-6 passes. ch03.py ALL OK.

Change:
- §3.1. Before: "The empty string … is accepted: the book reads ε as the number 0." After: "… is accepted, so the machine
  treats ε as a numeral for 0." Why: the book never says this; it only follows from A = {0}.

Doubts: headings 3.1, 3.3, 3.5, 3.6, 3.7, 3.10 are descriptive rather than the book's titles (Intuition; Another Example;
A Brute-Force Design Example; Combining DFAs: The Product Construction; Automatic Languages and Closure Properties; Minimal
Automata). SPEC fixes them as site-wide anchors and the numbers agree, so left unchanged. The Myhill–Nerode sketch does
not say why {[w] | w ∈ L} is well defined (take z = ε); same level of detail as the book; left.

## Concept pages

strings, induction-on-strings, languages, regular-expressions, regular-languages, dfa, product-construction,
closure-properties, fooling-sets, myhill-nerode-theorem, dfa-minimization, counting-arguments.

Checked: definitions agree with the chapter pages; every example re-derived by hand (banana: 15 substrings, 40
subsequences; A = {0,01}: |AB| = 3, A* = "every 1 preceded by 0"; no-00 expressions and wrong answer; ends-in-01 DFA,
run on 1001 and fooling set; product example: 6 reachable pairs, the 4 accepting sets, run on 1101; #0 > #1 with
z = 1^min(i,j), naive z = 1^i fails exactly when j < i; {0} has 3 classes; L3 needs 8 states, NFA 4; 5-state contains-11
Moore passes; diagonal example). Closure table: all 44 cells checked, including the decidable and acceptable columns;
the book's half(L) = {w | ww ∈ L} confirmed (Lemma 4.5); half(·) witness verified: for p, q, r ≥ 1, ww = 0^p1^q2^r0^p1^q2^r
has six runs, so matching 0^a1^a2^b0^c1^d2^d forces a = p = q, b = r, c = p, d = q = r, i.e. p = q = r; CF ∩ witness and
decidable h(L) witness correct. Traps are real traps. "Where it appears" anchors resolve and point at sections with the
stated content (ch05 §5.5/§5.6, ch07 §7.3/§7.5/§7.6; book §4.7: 9-state DFA → 4). concepts_a.py / concepts_b.py check
these examples as stated; both ALL OK (not modified). No changes.

Doubt: a few †-marks ("the book does not prove") in the closure table could be covered by book exercises (e.g. CF
reversal); harmless.

## Site check

`tools/check.py --only` on all assigned pages: only "wikilink target not found" for 0-toolkit/* and
1-models-of-computation/04-nondeterministic-automata (pages still being written).
