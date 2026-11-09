# CS/ECE 374 site — writing spec for Part 3 (Erickson's other lecture notes)

Part 3 summarizes Jeff Erickson's lecture notes that are **not** in his two textbooks: the Director's Cut (1–13), the two
appendices (98 induction, 99 recurrences) and the Extended Dance Remix (A–J). **Read first:** `tools/SPEC.md` (everything
applies: frontmatter, notation, callouts, links, figures, verification, style), `tools/SPEC-algorithms.md` §4–§5 and §7
(meta line, how algorithms are written, verification), and `/home/claude/work/notes/notes-facts.md` (files, page counts,
licence, status lines, course relevance). Exemplar for tone and density: `content/2-algorithms/10-maximum-flows-and-minimum-cuts.md`
(a chapter the course does not test, written as a careful review) and `content/concepts/dijkstras-algorithm.md` (concept page).

## 0. Reader and purpose

An **info page** for a student who has the textbook chapters down and wants the rest of Erickson's material in reviewable
form: definitions, algorithms with running times, the key lemmas and their proof ideas, the examples that matter, and how
the note connects to the textbook chapters already on the site. Not a replacement for the note; no anecdotes.
**These notes are much less refined than the book** (several say "Status: Unfinished" or "Needs revision"): treat every
claim as unverified until your check script confirms it, fix what is wrong (say so on the page, briefly, as "the note
says … ; correct is …"), and report every error with its page number. Unfinished parts: summarize what is there, say it
is unfinished, never invent the missing parts.

## 1. Files

```
content/4-lecture-notes/index.md                 section page (written by the coordinator)
content/4-lecture-notes/<file from notes-facts>  one page per note (your files)
content/concepts/<slug>.md                       concept pages, only the slugs assigned to you (SPEC §12 format)
tools/figs_n<id>.py → tools/figs/n<id>-*.html     figures (id = 01 … 13, 98, 99, a … j)
tools/checks/n<id>.py (+ .out)                    checks for the note page and its concept pages
```
Existing pages to link (exact anchors; `tools/check.py` validates them): Part 2 chapters `content/2-algorithms/01…12-*.md`,
their exercises pages, Part 1 chapters `content/1-models-of-computation/0N-*.md`, concepts `content/concepts/*.md`
(e.g. `master-theorem`, `recursion-trees`, `union-find`, `minimum-spanning-trees`, `maximum-flow`, `ford-fulkerson`,
`np-hardness`, `polynomial-time-reductions`, `independent-set`, `subset-sum`, `dynamic-programming`, `dfa-minimization`,
`chomsky-normal-form`, `induction-on-strings`, `linear-time-selection`, `divide-and-conquer`), toolkit pages.
Do not edit existing pages, except: you may add one link to your page in the "Where it appears" line (and `Related:` line)
of an existing concept page that your note extends (e.g. `union-find` for note 11, `master-theorem` and `recursion-trees`
for 99, `induction-on-strings` for 98, `maximum-flow` for F/G, `np-hardness` for B/J) — nothing else on that page.

## 2. Page format

```yaml
---
title: "Discrete probability"                     # the note's title, sentence case
description: "…"                                  # one or two sentences; no straight double quotes inside (use “ ”)
tags: [lecture-notes, algorithms, probability]    # lecture-notes + algorithms + one or two topic tags
note: "1"                                         # 1 … 13, 98, 99, A … J
---
```
Meta line (first line of the body):
`*Erickson, lecture notes · Director's Cut 1 · 22 pp. · [PDF](https://jeffe.cs.illinois.edu/teaching/algorithms/notes/01-random.pdf) · CC BY-NC-SA 4.0 · [[4-lecture-notes/index|all notes]]*`
(Appendix I / Appendix II / Extended Dance Remix A … J as appropriate; add "· status: unfinished" etc. when the PDF has a
status line.) Then:
1. `> [!abstract] In one breath` — the whole note in 4–6 sentences.
2. `> [!note] Where this fits` — what in the textbook chapters on this site it builds on or continues (with links), and its
   CS 374 relevance from notes-facts.md (e.g. "not assigned in CS 374 this semester; CS 473 material at Illinois").
3. One `##` section per section of the note, titled with the note's own number and title in sentence case:
   `## 1.1 Discrete probability spaces`, `## A.4 Divide and conquer`. Unnumbered notes (98, 99): use their numbers
   (`## 2 The ultimate method: guess and confirm`). ♥ sections: keep, briefly, with "(♥ in the note)" in the first sentence.
   If the PDF's numbering is wrong or inconsistent (08 prints 13.x), use the note's id (8.1, 8.2 …) and say so in Sources.
   Extra material only in `###` subsections or an unnumbered `##` before Summary.
4. `## Summary` — a bullet list of what to remember (statements, running times, the one-line reasons).
5. `> [!exam] For CS 374` — one short paragraph: relevance to the course's exams (from notes-facts.md), honestly.
6. `### Sources for this page` — the note (with its status line), what was checked by which script, every error found in
   the note (page number, as printed → correct), anything not machine-checked, deviations.

Content rules: as SPEC-algorithms §5 — pseudocode in `text` blocks in the book's style; every algorithm with what it
computes, its running time (worst-case / expected / amortized — say which) and the one-line reason it is correct;
proofs folded (`> [!proof]-`) unless they are the point; key statements in `[!key]` or `[!definition]` boxes with the
note's numbering when it has one (Lemma 1.2, Theorem A.3). Probabilistic claims state exactly what is random. Keep a page
proportional to its note: roughly 250 words per PDF page, at most about 6,000 words. The notes' exercises are **not**
solved; Summary may end with one line "The note ends with N exercises (…)".

## 3. Concept pages

Only the slugs assigned to you, SPEC §12 format (definition/key box, why it works, recipe or template, traps, one checked
example, "Where it appears" with exact anchors, `Related:` last); tags `[concept, algorithms, <topic>]`; aliases unique
site-wide **case-insensitively** (`grep -rhi "^aliases" content`).

## 4. Verification (mandatory) — `tools/checks/n<id>.py`

As SPEC-algorithms §7: implement every algorithm exactly as the page states it and compare with brute force on many small
inputs; compute every probability and expectation exactly (fractions, by enumerating the sample space) or, where
enumeration is impossible, by simulation with a stated tolerance AND the closed form; check every recurrence solution
numerically; every number in every example and figure; every counterexample. scipy/numpy/networkx are available. Use
`check(name, cond, detail)` lines; end with `ALL OK`; save `.out` with tee. If the note's claim fails, investigate, fix the
page (never the check), and report it.

## 5. Before you finish

1. `python3 tools/assemble.py content/4-lecture-notes/<your page>.md` (and your concept pages, if they have figures).
2. `python3 tools/check.py content /opt/npm-tools/node_modules/katex/dist/katex.min.js --only 4-lecture-notes/<your files>,concepts/<your slugs>`
   — zero errors except "wikilink target not found" for `4-lecture-notes/index` and pages other agents are writing.
3. Preview each page once in light mode (`python3 /home/claude/work/preview/pageshot.py content/<page>.md /tmp/<you>/x.png light`,
   then `tiles.py`); figures in light and dark. Fix overflowing displays and broken callouts.
4. Final message (concise): files written; errors found in the note (page, as printed → correct, evidence); deviations;
   anything unverified. Do not commit or push.
