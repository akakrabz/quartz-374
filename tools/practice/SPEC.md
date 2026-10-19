# Practice bank — authoring spec (CS/ECE 374, Models of Computation, Chapters 1–7)

You are writing practice-problem pages for the CS/ECE 374 study site. Read `tools/SPEC.md` (site-wide notation, links,
callouts) first; this file adds the practice-specific rules. The student uses the bank to prepare for exams, so the
bank must (1) start easy, (2) reach real exam difficulty in the exams' own formats, and (3) be **correct in every
answer** — a wrong answer key does more harm than no answer key.

## 1. Files

- Write only your assigned page(s): `content/practice/0N-<slug>.md` (§9).
- Write a verification script per page, `tools/practice/checks/chNN.py`, run it, save its output as
  `tools/practice/checks/chNN.out`; it must end with `ALL OK`. Use `tools/automata` (see `tools/checks/ch03.py` for the
  style). Never edit the library or anyone else's files.
- Validate with `python3 tools/practice/build_practice.py` (no `--write`; it only parses and prints errors for every
  page — fix all errors on yours). Then `python3 tools/check.py content /opt/npm-tools/node_modules/katex/dist/katex.min.js --only practice/0N`
  (ignore only "wikilink target not found" for pages that do not exist yet). Render the page with
  `python3 /home/claude/work/preview/pageshot.py content/practice/0N-….md /tmp/p.png light` and look at it.
  (The previewer leaves folded callouts empty; to proofread solutions, render a temporary copy with `]-` replaced by `]`.)

## 2. Counts and difficulty

| chapter | file | problems (easy, medium, hard) |
|---|---|---|
| 1 Strings | `practice/01-strings.md` | 8 (3, 3, 2) |
| 2 Regular languages | `practice/02-regular-languages.md` | 8 (3, 3, 2) |
| 3 Finite-state machines | `practice/03-finite-state-machines.md` | 10 (4, 3, 3) |
| 4 Nondeterministic automata | `practice/04-nondeterministic-automata.md` | 10 (4, 3, 3) |
| 5 Context-free languages | `practice/05-context-free-languages.md` | 10 (4, 3, 3) |
| 6 Turing machines | `practice/06-turing-machines.md` | 6 (3, 2, 1) |
| 7 Undecidability | `practice/07-undecidability.md` | 8 (3, 3, 2) |

Number problems `C.1 … C.n` (C = chapter) in order easy → medium → hard, under `## Easy`, `## Medium`, `## Hard`.

| level | what it means | time | hint? |
|---|---|---|---|
| easy | one definition or one idea: a true-or-false item with one-sentence reasons, a short regular expression or DFA, a single induction step, spotting one error | 2–5 min | optional |
| medium | a standard exam part: a DFA or grammar with state/nonterminal meanings, a full fooling-set proof, a short induction proof, one construction by hand | 10–15 min | required |
| hard | a full exam problem: a two-part language transformation with formal constructions, a regular-and-context-free pair (fooling set + grammar), a complete proof about a recursive function, an undecidability proof | 20–30 min | required |

**Variety on every page:** at least one **true-or-false** item (easy, 4–6 statements, each answered Yes/No *with a
one-sentence reason* — the exams' first problem has exactly this format), at least one **find-the-error** item (a short
student answer with one classic slip), and hard problems in the exams' formats (book-facts.md lists the five Midterm 1
problem types). **Scope rule:** a Chapter C problem may use only Chapters 1…C.

**Originality:** every problem is original or a classic textbook-style exercise in your own words. Do **not** use the
course's practice-exam problems, which are: squish (pairs of symbols → 0/1); Bond (doubling runs of 0s); compress0s;
take2skip2 / Took2Added2 / Took2Skipped2; OddParity / AddParity; "every run of 0s is followed by a shorter run of 1s";
{0^a 1^b 0^c : a=b or a=c or b=c}; {w 0^n w^R : n > 0}; no subsequence 010; at least two even-length runs of 1s;
every run of 1s even and every run of 0s odd; strings in 0*10* of length divisible by 3; 374 consecutive 1s; and the
true/false statements of those exams. Do not duplicate the site's worked problems (`content/problems/`) or the examples
worked on the chapter pages; variations with a genuinely different language are fine.

## 3. Page template (copy exactly, then fill)

```markdown
---
title: "Practice — Chapter 3: Finite-state machines"
description: "10 practice problems (4 easy, 3 medium, 3 hard) on DFA design and correctness, the product construction, fooling sets and minimization, each with a folded hint and a worked solution."
tags: [practice, regular, midterm-1]
chapter: 3
---

*Practice for [[1-models-of-computation/03-finite-state-machines|Chapter 3]] · concepts: [[concepts/dfa]] · [[concepts/fooling-sets]] · all practice: [[practice/index|hub]] · by difficulty: [[practice/easy|easy]] · [[practice/medium|medium]] · [[practice/hard|hard]]*

Work each problem on paper first. Open the **hint** only when stuck, and the **solution** only after you have an answer you would hand in. Every automaton, expression and grammar in the solutions has been checked by a script.

## Easy

### 3.1 Short title here

> [!easy] Easy · true or false · fooling sets
> (statement)
>
> *Source: original.*

> [!solution]- Solution
> (worked solution)
>
> **Answer.** (the final result in one or two lines)

## Medium

### 3.5 …

> [!medium] Medium · DFA design
> …
>
> *Source: original.*

> [!hint]- Hint
> …

> [!solution]- Solution
> …
>
> **Answer.** …

## Hard
…

### Sources for this page
One short paragraph: what kinds of problems these are and where the ideas come from (book sections, classic exercise
types); say that none is taken from a course exam or homework.
```

Tags in frontmatter: `[practice, strings, midterm-1]` (Ch 1), `[practice, regular, midterm-1]` (Ch 2–4),
`[practice, context-free, midterm-1]` (Ch 5), `[practice, turing-machines]` (Ch 6), `[practice, undecidability]` (Ch 7).
`chapter:` = the chapter number. The description must contain "N practice problems (a easy, b medium, c hard)".
The concept links in the header line: 2–4 pages from the concept slug list in tools/SPEC.md §2.

## 4. The problem block — exact rules (a parser builds the indexes from these)

1. Heading `### C.N Short title` — title ≤ 6 words, letters/digits/commas/hyphens/apostrophes only, no math.
2. The next non-blank line is the difficulty callout `> [!easy] Easy · tag · tag` (or medium/hard), with 1–3 tags
   from the **tag vocabulary** below, separated by ` · `.
3. The statement is inside that callout; its last line is `> *Source: ….*` (`original`, `classic`, or `textbook
   exercise style`).
4. Then a folded hint `> [!hint]- Hint` (required for medium and hard, optional for easy).
5. Then always a folded solution `> [!solution]- Solution` ending with a line `> **Answer.** …`.
6. One blank line between callouts; inside a callout a paragraph break is a line containing only `>`; never a blank
   line inside a callout; never nested callouts. Tables inside callouts are fine (every row prefixed `> `).

**Tag vocabulary** (use only these; the build script rejects anything else):
`true or false` · `multiple choice` · `find the error` · `string induction` · `recursive functions` ·
`substrings and subsequences` · `languages` · `Kleene star` · `Arden's rule` · `regular expressions` ·
`regex induction` · `DFA design` · `DFA proof` · `product construction` · `closure properties` · `fooling sets` ·
`non-regularity` · `Myhill–Nerode` · `minimization` · `NFA design` · `epsilon-transitions` · `subset construction` ·
`Thompson's algorithm` · `state elimination` · `language transformations` · `grammar design` · `grammar proof` ·
`parse trees` · `ambiguity` · `Chomsky normal form` · `recursive automata` · `context-free closure` ·
`Turing machine design` · `TM variants` · `TM simulation` · `acceptable vs decidable` ·
`closure of decidable languages` · `diagonalization` · `reductions` · `Rice's theorem` · `TM behavior`

## 5. Writing the statement

- Self-contained and unambiguous: state the alphabet; define every language precisely (set-builder plus a sentence);
  say exactly what to produce ("a DFA with mnemonic state names; no proof required", "a regular expression and a
  one-sentence explanation of each part", "a fooling-set proof", "a formal description of an NFA $M'$ in terms of an
  arbitrary DFA $M = (\Sigma, Q, s, A, \delta)$").
- True-or-false items: 4–6 statements labelled (a), (b), …; ask for Yes/No and a one-sentence justification each.
- Find-the-error items: show the student's answer inside the statement (indented or as a quote-free paragraph),
  then ask what is wrong and for a fix.

## 6. Writing the solution (the most important part)

- Medium/hard solutions: **Idea** (what to remember / guess / induct on, in one or two sentences) → **Construction or
  proof**, written the way a full-credit exam answer is written (state meanings for every DFA/NFA state, a description
  of every nonterminal's language, the full proof template for inductions and fooling sets, the formal tuple for
  transformations) → **Check** (run the machine on a few short strings, try $\varepsilon$, compare with the language
  definition) → `**Answer.**`.
- Automata in solutions: give them as transition tables (rows = states, columns = symbols, a column "meaning",
  mark start with → and accepting with \*) or as formal tuples; for transformations always the formal definition of
  $Q'$, $s'$, $A'$, $\delta'$.
- Proofs: complete, in exam style; the induction hypothesis stated explicitly; every step justified by a definition,
  the hypothesis or arithmetic. Never "clearly".
- True/false: one line per statement: **Yes/No** — reason. If "No", give a concrete counterexample when there is one.
- Find-the-error: name the slip, fix it, give the corrected result.
- Add "**Watch out:** …" for the classic trap when there is one, and grading notes from the rubrics where useful.

## 7. Verification (mandatory, scripted)

Every automaton, regular expression, grammar and Turing machine that appears in a statement or a solution is checked
against a brute-force predicate over all strings up to length ≥ 10 (exactly, via DFA equivalence, whenever the
language is regular); every "this string is / is not in L" claim; every fooling-set suffix for many pairs i ≠ j; every
counterexample in a true-or-false answer; every language transformation construction implemented as a function of an
arbitrary DFA and tested on at least 200 random small DFAs (2–4 states) against the definition of the transformed
language; every induction claim tested on all strings up to length ≥ 8. Write the brute-force predicates
independently of the answers (from the problem statement).

## 8. Notation

Exactly as tools/SPEC.md §5 (`\mathtt{0}`, `\varepsilon`, `\textsf{…}` for named languages, `\lvert w\rvert` in
tables, no macros, KaTeX strict).

## 9. Assignments

| C | file | chapter page |
|---|---|---|
| 1 | `practice/01-strings.md` | `1-models-of-computation/01-strings` |
| 2 | `practice/02-regular-languages.md` | `1-models-of-computation/02-regular-languages` |
| 3 | `practice/03-finite-state-machines.md` | `1-models-of-computation/03-finite-state-machines` |
| 4 | `practice/04-nondeterministic-automata.md` | `1-models-of-computation/04-nondeterministic-automata` |
| 5 | `practice/05-context-free-languages.md` | `1-models-of-computation/05-context-free-languages` |
| 6 | `practice/06-turing-machines.md` | `1-models-of-computation/06-turing-machines` |
| 7 | `practice/07-undecidability.md` | `1-models-of-computation/07-undecidability` |

## 10. Coverage checklists (cover every bullet at least once)

**Ch 1.** Unfolding recursive definitions on examples; length/concatenation facts; a full string induction with the
template; the three-case decomposition; substrings vs subsequences vs prefixes; reversal or counting facts; a new
recursive function defined in the problem with two properties to prove (hard).
**Ch 2.** ∅ vs {ε} vs ε; concatenation and star of small languages; L* facts (Lemma 2.2); Arden's rule; writing regular
expressions for described languages (several, with explanations); reading an expression (describe its language);
equivalence or non-equivalence of two expressions with a witness; structural induction on regular expressions (a new
recursive function on expressions, e.g. an expression for every string's prefixes, or "does L(R) contain ε").
**Ch 3.** DFA design with mnemonic names (several); proving a DFA correct; product construction written formally;
closure arguments; fooling-set proofs (several, including one where F ≠ 0*); the closure trick (∩ with a regular
language); finite fooling sets as lower bounds; Moore's algorithm on a small DFA.
**Ch 4.** NFA design (guessing); running an NFA on a string (sets of states); ε-reach; incremental subset construction
by hand (table); Thompson on a small expression (state count, structure); state elimination on a small DFA; language
transformations of both kinds ({w : f(w) ∈ L} with a DFA, {f(w) : w ∈ L} with an NFA guessing), formal tuples.
**Ch 5.** Grammar design (several, each nonterminal described); proving L(G) = L (both inclusions, a short one);
ambiguity (two parse trees; an unambiguous grammar); CNF conversion of a small grammar; regular-language → grammar;
a language that is context-free but not regular (fooling set + grammar, hard); recursive automaton ↔ grammar.
**Ch 6.** Tracing a TM on an input (configurations); designing a small TM (transition table, verified by simulation);
accept vs reject vs diverge; variants (stay-put, doubly infinite tape, k tapes) and slowdowns; computing a function.
**Ch 7.** Acceptable vs decidable facts (closure, complements, Lemma 5); a diagonalization proof; a reduction proof
(template, both directions); Rice's theorem applications with explicit Y and N machines; a behavior question where
Rice does not apply (decidable by simulation, or undecidable by reduction); true/false on classification of languages.
