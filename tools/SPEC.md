# CS/ECE 374 notes site — writing spec (Models of Computation)

You are writing pages for a Quartz 5 study site for UIUC **CS/ECE 374 A (Fall 2026)**, in the same style as the
student's ECE 329 site. Read this whole file, then read the exemplar page
`content/1-models-of-computation/03-finite-state-machines.md` **completely** before writing anything: match its
structure, tone, density and conventions.

## 0. Purpose, audience, standards

- The reader is a student reviewing for exams: Midterm 1 (Models of computation, Ch 1–5) was on Sep 28;
  Midterm 2 (Algorithms) is Nov 9; the Final (everything, incl. Ch 6–9) is Dec 11. Exams allow one (midterm) or two
  (final) **handwritten** double-sided cheat sheets.
- The site is a **reference and review**, explicitly *not* a replacement for Jeff Erickson's textbook. Every chapter
  page links its chapter PDF; definitions, theorems, templates, worked examples and traps are the core; long
  narrative is not. Aim for precise, compact, exam-useful.
- **Correctness is the top priority.** Every concrete automaton, regular expression, grammar, Turing machine,
  run trace, state count and fooling-set claim must be machine-checked (§9). A wrong example does more harm than none.
- Write in your own words. The book is CC BY-NC-SA: summarize and paraphrase, never copy sentences. Standard
  examples (0^n1^n, mod-5 DFA, …) are fine to use.

## 1. Sources (read them)

- `/home/claude/work/moc-notes.tex` — chapter notes written earlier for this student (primary source; same theorem
  numbering as the book).
- `/home/claude/work/book-facts.md` — **verified** section titles, theorem numbers, page ranges, PDF URLs, course and
  exam facts, and a paraphrase of the grading rubrics. Prefer it over memory.
- The chapter PDFs (URLs in book-facts.md) may be read with WebFetch to double-check a specific detail.
- Do not invent course facts (dates, policies) beyond book-facts.md.

## 2. Site layout and link targets (use these exact paths)

```
content/index.md                                   home
content/0-toolkit/index.md                         Toolkit
content/0-toolkit/01-notation-and-conventions.md
content/0-toolkit/02-proof-templates.md
content/0-toolkit/03-the-big-picture.md            classes of languages, closure table, how to prove in/out
content/0-toolkit/04-review-regular-and-context-free.md        exam review Ch 1–5
content/0-toolkit/05-review-turing-machines-and-undecidability.md   exam review Ch 6–9
content/0-toolkit/06-how-exams-are-graded.md
content/1-models-of-computation/index.md           unit page
content/1-models-of-computation/01-strings.md
content/1-models-of-computation/02-regular-languages.md
content/1-models-of-computation/03-finite-state-machines.md
content/1-models-of-computation/04-nondeterministic-automata.md
content/1-models-of-computation/05-context-free-languages.md
content/1-models-of-computation/06-turing-machines.md
content/1-models-of-computation/07-undecidability.md
content/1-models-of-computation/08-universal-models.md
content/1-models-of-computation/09-nondeterministic-turing-machines.md
content/2-algorithms/index.md                      planned
content/concepts/<slug>.md                         glossary (slugs below)
content/problems/<slug>.md                         worked exam-style problems
content/practice/0N-<chapter-slug>.md              practice bank (01-strings … 07-undecidability)
```

**Concept slugs** (link as `[[concepts/<slug>]]` or `[[concepts/<slug>|text]]`):
`strings` · `induction-on-strings` · `languages` · `regular-expressions` · `regular-languages` · `dfa` · `nfa` ·
`product-construction` · `subset-construction` · `thompsons-algorithm` · `state-elimination` · `kleenes-theorem` ·
`closure-properties` · `fooling-sets` · `myhill-nerode-theorem` · `dfa-minimization` · `language-transformations` ·
`context-free-grammars` · `parse-trees-and-ambiguity` · `chomsky-normal-form` · `recursive-automata` ·
`counting-arguments` · `turing-machines` · `church-turing-thesis` · `universal-turing-machine` ·
`acceptable-and-decidable` · `diagonalization` · `halting-problem` · `undecidability-reductions` · `rices-theorem` ·
`nondeterministic-turing-machines` · `cook-levin-theorem`

**Chapter headings are fixed** — use exactly these `##` headings (they are the anchors other pages link to). Extra
material goes in `###` subsections or in an unnumbered `##` section placed before `## Summary`.

```
Ch1: 1.1 Strings | 1.2 Two recursive functions | 1.3 Induction on strings | 1.4 More than one path up the mountain |
     1.5 Indices, substrings, and subsequences | More recursive functions | Summary
Ch2: 2.1 Languages | 2.2 Building languages | 2.3 Regular languages and regular expressions |
     2.4 Things that aren't regular expressions | 2.5 Regular expression trees | 2.6 Proofs about regular expressions |
     2.7 Proofs about regular languages | 2.8 Not every language is regular | Summary
Ch3: (see the exemplar)
Ch4: 4.1 Nondeterministic state machines | 4.2 Intuition | 4.3 Epsilon-transitions | 4.4 Kleene's theorem |
     4.5 NFA to DFA: the subset construction | 4.6 Regular expression to NFA: Thompson's algorithm | 4.7 Another example |
     4.8 NFA to regular expression: state elimination | 4.9 Regular language transformations | Summary
Ch5: 5.1 Definitions | 5.2 Parse trees and ambiguity | 5.3 From grammar to language | 5.4 More examples |
     5.5 Regular languages are context-free | 5.6 Not every language is context-free | 5.7 Recursive automata |
     5.8 Chomsky normal form | 5.9 The CNF conversion algorithm | Summary
Ch6: 6.1 Why bother? | 6.2 Formal definitions | 6.3 A first example | 6.4 Variations | 6.5 Computing functions |
     6.6 Tracks, heads, and tapes | 6.7 Simulating a real computer | 6.8 Universal Turing machines | Summary
Ch7: 7.1 Acceptable versus decidable | 7.2 Decidable without knowing the algorithm | 7.3 Useful properties |
     7.4 Code is data; data is code | 7.5 Self-haters gonna self-hate | 7.6 Aside: uncountable barbers |
     7.7 More self-referential languages | 7.8 Nevertheless, acceptable | 7.9 The halting problem via reduction |
     7.10 More undecidable languages | 7.11 Rice's theorem | 7.12 The Rice–McNaughton–Myhill–Shapiro theorem |
     7.13 Turing machine behavior: it's complicated | Summary
Ch8: 8.1 Universal Turing machines | 8.2 Two-stack machines | 8.3 Counter machines | 8.4 FRACTRAN |
     8.5 Post's correspondence problem | 8.6 Matrix mortality | 8.7 Dynamical systems | 8.8 Wang tiles |
     8.9 Combinator calculus | Summary
Ch9: 9.1 Definitions | 9.2 Acceptance and rejection | 9.3 Time and space complexity |
     9.4 Deterministic simulation via dovetailing | 9.5 Nondeterminism as advice | 9.6 The Cook–Levin theorem | Summary
```

Anchors are github-slugger slugs of the heading: lowercase, spaces → `-`, punctuation (`.`, `:`, `'`, `?`, `;`, `,`,
en dash) dropped. Examples: `#45-nfa-to-dfa-the-subset-construction`, `#39-the-myhillnerode-theorem`,
`#711-rices-theorem`, `#61-why-bother`. `tools/check.py` verifies every anchor.

## 3. Frontmatter

Chapter page:
```yaml
---
title: "Chapter 4 — Nondeterministic Automata"
description: "One or two sentences listing what the page covers (shown in link previews and search)."
tags: [chapter, regular, midterm-1]
chapter: 4
---
```
Tags: structural tag first (`chapter`, `concept`, `problem`, `practice`, `toolkit`), then topic tags from
`strings`, `regular`, `context-free`, `turing-machines`, `undecidability`, `complexity`, then `midterm-1` for
Ch 1–5 material. Concept pages may add `aliases: [...]` (alternative names; do not reuse an alias of another page).

## 4. Chapter page skeleton (copy the exemplar's)

1. Meta line (italic, one line):
   `*Chapter N · book pp. a–b · [chapter PDF](URL) · prev: [[…|Chapter N−1]] · next: [[…|Chapter N+1]]*`
   (no prev on Ch 1, no next on Ch 9; the practice link is added later by a script — do not add it yourself).
2. `> [!abstract] In one breath` — 4–6 sentences: the chapter's main idea and results.
3. The fixed `##` sections. In each: definitions in `[!definition]`, numbered results in `[!key]` titled exactly as
   the book numbers them ("Lemma 4.2", "Theorem 4.1 (Kleene)", "Theorem 12", "Rice's theorem"), proofs folded in
   `[!proof]-`, procedures in `[!recipe]`, exam boilerplate in `[!template]`, mistakes in `[!trap]`, worked examples in
   `[!example]`, grading/exam notes in `[!exam]`, intuition in `[!intuition]`. Close a section with
   "Concept page: [[concepts/…]]." when one exists.
4. `## Summary` — 5–8 bullets.
5. `> [!exam] On the exams` — how this chapter is examined (use book-facts.md: MT1 problem types, rubric points;
   Ch 6–9 are on the final only). Link `[[0-toolkit/06-how-exams-are-graded|how exams are graded]]` where useful.
6. `### Sources for this page` — one paragraph: which book sections, which examples are the book's and which are
   original, and "checked by `tools/checks/chNN.py`".

Length: like the exemplar (roughly 2,500–4,500 words of prose plus math). Ch 8 is shorter (the book's chapter is a
sketch).

## 5. Notation (KaTeX, strict mode, no macros — the vault must also render in Obsidian)

- Inline math `$…$`, display math `$$…$$` on its own lines. Inside a callout every line, including the `$$` lines,
  starts with `> `.
- **Explicit symbols and strings in math use `\mathtt`**: `$\mathtt{0}^n\mathtt{1}^n$`,
  `$(\mathtt{0}+\mathtt{1})^*\mathtt{00}$`, `$\#(\mathtt{1},w)$`. A literal string in running text may be written
  in backticks: `` `0110` ``. Variables are italic as usual: $a, b, c$ symbols; $w, x, y, z$ strings.
- Empty string `\varepsilon`; empty language `\varnothing`; concatenation by juxtaposition or `\bullet`;
  length `\lvert w\rvert` (always `\lvert … \rvert` inside tables; plain `|w|` is fine elsewhere);
  set-builder `\{ w \mid … \}` (never a bare `|` inside a table); reversal $w^R$; complement `\overline{L}`;
  symmetric difference `\oplus`; derivation step `\rightsquigarrow`, many steps `\rightsquigarrow^*`.
- Named languages and functions in sans-serif inside math: `$\textsf{Halt}$`, `$\textsf{Accept}(M)$`,
  `$\textsf{SelfReject}$`, `$\textsf{half}(L)$`. Encodings `\langle M\rangle`, `\langle M, w\rangle`.
  True/false values `\textsf{True}`, `\textsf{False}`. TM blank `\square`. States of a TM in math:
  `\textit{accept}` or `\mathit{seek1}`.
- No `\textsc` (KaTeX does not support it), no `\newcommand`, no `\color` for meaning.
- In headings: no math, no `ε` (write "epsilon"), no inline code.
- Regular-expression conventions as in the book: `+` for union, juxtaposition, `*`; precedence star > concat > union.

## 6. Callouts

Allowed types: `definition`, `key`, `template`, `recipe`, `trap`, `exam`, `intuition`, `proof` (fold with `-`),
`derivation` (fold with `-`), `example`, `abstract`, `tip`, `note`, `question`, `warning`.
- Title after the type: `> [!definition] Definition — NFA`, `> [!key] Lemma 4.4`, `> [!template] Template — …`,
  `> [!proof]- Proof (click to expand)`.
- Inside a callout a paragraph break is a line containing only `>`. Never put a blank line inside a callout (it ends
  the callout). Separate consecutive callouts with one blank line. Never nest callouts.
- In `[!template]` callouts, end every line but the last with ` \` (a hard line break) so the boilerplate keeps its
  line structure, or use a list.
- Tables inside callouts work (prefix every row with `> `).

## 7. Links

- Always full paths: `[[1-models-of-computation/04-nondeterministic-automata#45-nfa-to-dfa-the-subset-construction|§4.5]]`,
  `[[concepts/subset-construction]]`. Inside tables escape the pipe: `[[concepts/dfa\|DFA]]`.
- Link generously but meaningfully: first mention of a concept on a page → concept page; cross-references between
  chapters → the exact section anchor.
- External links (book PDF, course site) as plain Markdown links.

## 8. Figures

Inline SVG generated by Python, theme-aware (strokes/text `currentColor`; accents `var(--accent)`,
`var(--accent2)`, `var(--hi)`, `var(--muted)`; label halos `var(--paper)`).
- Library: `tools/figlib.py` (`Automaton` for DFAs/NFAs/TM diagrams, `Tree` for expression and parse trees, `Tape`
  for Turing-machine tapes, `SVG` for anything else). Read it, and read `tools/figs_ch03.py` as the model.
- Put your figure code in `tools/figs_chNN.py` (your chapter number); it writes `tools/figs/chNN-<name>.html`.
  Figure names start with `chNN-`.
- In the page, a figure is the marker line `<!-- fig:chNN-name -->`; then run
  `python3 tools/assemble.py content/<your page>.md` (always pass your page paths — never run it without arguments,
  other writers are editing other pages) to inline the figure on the next line.
- Every figure has a caption: `<strong>Short title.</strong>` + one or two sentences that make the figure readable
  on its own.
- **Look at every figure** before finishing: `python3 /home/claude/work/preview/shot.py out.png tools/figs/chNN-x.html …`
  renders light and dark side by side; then view the PNG with the Read tool. Fix overlaps, clipped arrows, wasted
  space, unreadable labels. Typical canvas: 400–640 px wide.
- 3–6 figures per chapter page where they help (automata, trees, tapes, construction gadgets). Do not draw what a
  table says better.

## 9. Verification (mandatory)

- Library: `tools/automata` (`DFA`, `NFA`, `Regex`, `thompson`, `eliminate_states`, `CFG`, `TM`, `strings`,
  `first_difference`). Read `tools/automata/*.py` and `tools/checks/ch03.py` (the model). **Do not edit the library**;
  if you find a bug or need a helper, write the helper in your own check script and mention the bug in your report.
- Write `tools/checks/chNN.py`: one `check(name, condition, detail)` line per concrete claim on your page (every
  automaton correct against a brute-force predicate up to length ≥ 10–14, every regex equivalence exact via
  `Regex(...).equivalent(...)`, every grammar against a predicate up to length ≥ 10, every run trace, every state
  count, every fooling-set suffix for many i ≠ j, every TM on all inputs up to length ≥ 8). Run it and save the output:
  `python3 tools/checks/chNN.py | tee tools/checks/chNN.out`. It must end with `ALL OK`.
- If a claim from the notes or the book fails a check, investigate; fix the page (never the check) and mention the
  discrepancy in your final report.

## 10. Before you finish

1. `python3 tools/assemble.py content/<your pages>`
2. `python3 tools/check.py content /opt/npm-tools/node_modules/katex/dist/katex.min.js --only <your page prefixes>`
   — zero errors on your pages, **except** "wikilink target not found" for pages listed in §2 that do not exist yet
   (concept pages, other chapters, toolkit pages). Anchors into existing pages must resolve.
3. Render your page: `python3 /home/claude/work/preview/pageshot.py content/<page>.md /tmp/x.png light` (and `dark`),
   split long screenshots with `python3 /home/claude/work/preview/tiles.py /tmp/x.png /tmp/x_ 1700`, and look at
   every tile with Read. Fix anything ugly (broken math, run-on callouts, figures too large).
4. Final report (your last message): files written, every place you deviated from the notes or the book and why,
   any library bug, and anything you could not verify.

## 11. Style

- American spelling. Short paragraphs. Bold the defined term at its definition. Second person is fine.
- Prefer a worked example over an abstract sentence. Prefer one precise sentence over three vague ones.
- Never write "clearly", "obviously", "trivially" in a proof — the graders penalize them, and so should we.
- Do not mention this spec, the checks, or "the notes" in page text; the "Sources for this page" paragraph is the only
  place to mention verification.

## 12. Concept pages (`content/concepts/<slug>.md`)

One page per idea, 250–600 words, self-contained, consulted out of order. Model: the ECE 329 site's concept pages.
```markdown
---
title: "Fooling sets"
description: "One sentence: what it is and what it is for."
tags: [concept, regular, midterm-1]
aliases: ["fooling set", "distinguishing suffix"]
---

> [!definition] Definition            (or [!key] for a theorem-type concept)
> The precise definition / statement, with the key formula.

**Why it works / where it comes from.** 2–4 sentences.

> [!recipe] or [!template]   — how to use it on an exam (copy the chapter's template if there is one)

> [!trap]
> - the 2–5 classic mistakes

**Example.** One short, verified example (different from the chapter's main one where possible).

**Where it appears.** Links to the chapter sections that develop it (exact anchors), and to other concept pages.

Related: [[concepts/…]] · [[concepts/…]] · …
```
The build script later inserts a "**Practice.**" line right before the "Related:" line — keep "Related:" as the last line.
Concept pages need no figures. Examples on concept pages are verified in `tools/checks/concepts_<group>.py`.

## 13. Worked problems (`content/problems/<slug>.md`)

Exam-style problems worked in full, the way a strong student writes them on the exam, with the trap at each step
called out. Model: the ECE 329 site's worked problems.
```markdown
---
title: "Worked problem — Two language transformations"
description: "What the problem asks and what the solution shows, in one or two sentences."
tags: [problem, regular, midterm-1]
---

*Problem · style of a Midterm 1 language-transformation problem · uses [[1-models-of-computation/04-nondeterministic-automata#49-regular-language-transformations|§4.9]] · concepts: [[concepts/language-transformations]], [[concepts/nfa]]*

> [!question] Problem
> The full statement, parts (a), (b), …

## (a) …
Idea → construction/proof → check, with [!key] boxes for the final answers, [!trap] boxes for the classic errors,
and an [!exam] box saying how the rubric would grade it.

### Sources for this page
```
All problems are original (or classic textbook-style in our own words); none copies a course exam or homework.
Every automaton/grammar/TM is verified in `tools/checks/problems_<n>.py`.
