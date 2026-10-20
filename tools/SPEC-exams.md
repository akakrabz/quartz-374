# CS/ECE 374 site — writing spec for `content/3-homework-and-exams/` (practice-exam and homework write-ups)

These pages carry the student's own worked solutions to the course's practice exams and homework. **Read `tools/SPEC.md`
first** (frontmatter, KaTeX rules, callouts, links, figures, verification, style); everything there applies.
The whole site is private, so nothing here needs a "private" or "do not publish" note.

## Files

```
content/3-homework-and-exams/index.md                      unit page (coordinator)
content/3-homework-and-exams/midterm-1-practice-1.md       one page per practice test (5 problems each)
content/3-homework-and-exams/midterm-1-practice-2.md
content/3-homework-and-exams/midterm-1-practice-3.md
content/3-homework-and-exams/hw6-dynamic-programming.md    (coordinator)
tools/figs_exams.py -> tools/figs/exam-*.html               figures (DFA drawings), via tools/figlib.py (class Automaton)
tools/checks/exams_mt1.py (+ .out)                          checks: every DFA, NFA, regex, grammar, fooling set on the pages
```

## Source

`/home/claude/work/exams/mt1-practice-solutions.tex` (+ `.pdf`, 16 pages, same folder) — "Midterm 1 Practice Tests 1, 2 and 3:
Solutions", written earlier for this student. Test N starts at `\PracticeHeader{N}`; problems are the `\item`s of the
`Problems` environment (five per test), parts are `\item`s of `enumerate[(a)]`; `\begin{Solution}` … holds the solution.
Convert faithfully — **same solutions, same wording where it reads well in markdown**; fix only what is wrong (report it).
The problem statements in the .tex are the paraphrased statements; keep them (do not fetch the course PDFs).

Macros to translate (KaTeX strict, no macros): `\Sym{0}` → `\mathtt{0}` (in text outside math: `` `0` `` or $\mathtt{0}$);
`\fn{X}` → `\textsf{X}`; `\Lang{X}` → `\textsf{X}` (no `\textsc`); `\set{…}` → `\{…\}`; `\Setbar{a}{b}` → `\{a \mid b\}`;
`\e` → `\varepsilon`; `\AnsYes`/`\AnsNo`/`\AnsTrue`/`\AnsFalse` → `**Yes.**` etc.; `\T`/`\F` → `\textsf{True}`/`\textsf{False}`;
`\emptyset` → `\varnothing`; `\cramped` itemize → plain list; `align*` → `$$\begin{aligned}…\end{aligned}$$`; `\xrightarrow` ok;
`\mbox{}` drop. Inside tables, `\lvert…\rvert` and `\mid`, never a bare `|`. TikZ `dfa` pictures → `tools/figlib.Automaton`
figures (see `tools/figs_problems1.py` for the idiom: rounded states with mnemonic names, `save(...)`, `<!-- fig:NAME -->`
marker on the page, then `python3 tools/assemble.py content/<page>.md`). Look at the PDF page (`pdftoppm -f P -l P -r 110 -png`)
to reproduce each drawing's layout.

## Page format

```markdown
---
title: "Midterm 1 practice test 1 — solutions"
description: "…one or two sentences: the five problems and what each exercises…"
tags: [exam, midterm-1, regular, context-free]
---

*Midterm 1 practice test 1 · CS/ECE 374 A, Fall 2026 · five problems in the exam's format · the other tests: [[3-homework-and-exams/midterm-1-practice-2|test 2]], [[3-homework-and-exams/midterm-1-practice-3|test 3]] · how it is graded: [[0-toolkit/06-how-exams-are-graded|rubrics]]*

> [!abstract] In one breath
> What the five problems are and the one idea each turns on.

## Problem 1 — True or false

> [!question] Problem 1
> The statement, paraphrased as in the .tex.

### (a) …

**Yes.** … (one line each, as in the source; use a list or `###` per part, whichever reads better for the ten statements)

## Problem 2 — Language transformations: Delete1st
…
> [!key] Answer (a)
> the formal construction, as in the source
…
> [!exam] How this is graded
> one or two lines tying the answer to the rubric (links: [[0-toolkit/06-how-exams-are-graded#8-language-transformations|…]] etc.)

### Sources for this page
```

Link every problem to the matching template on [[0-toolkit/02-proof-templates]] and the matching concept page(s), with
exact anchors (grep the headings). Keep the `\NextProblem` structure as `## Problem k — short title`; parts as `### (a) …`.
Use `[!key]` for final answers (the DFA, the regex, the fooling set, the grammar), `[!proof]-`? no — proofs stay visible on
these pages; `[!trap]` only where the source already warns of a mistake.

## Verification (mandatory)

`tools/checks/exams_mt1.py` (one shared script; each writer appends a clearly marked section for their test — use
`check(name, cond, detail)` lines and keep the shared header; run the whole script, it must end `ALL OK`). Use
`tools/automata` (see any `tools/checks/ch0N.py` for the API: DFA, NFA, regex equivalence, grammars with Earley parsing):
every DFA/NFA/regex/grammar on the page is compared with a brute-force definition of its language on all strings up to
length 8–10; every fooling-set claim is checked (the distinguishing suffixes); every "Yes/No" that rests on a concrete
example is checked. Then `python3 tools/check.py content /opt/npm-tools/node_modules/katex/dist/katex.min.js --only
3-homework-and-exams/midterm-1-practice-N` must pass (ignore "wikilink target not found" for the other agents' pages and
the index), and preview the page once in light mode (`python3 /home/claude/work/preview/pageshot.py content/<page>.md
/tmp/<you>/x.png light`, then `tiles.py`) to catch overflowing displays and broken callouts.

Final message: files written, anything you changed from the .tex and why, anything unverified.
