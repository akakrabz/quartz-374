# CS/ECE 374 site — writing spec for the lab pages (`content/3-homework-and-exams/lab-*.md`)

Read `tools/SPEC.md` (frontmatter, KaTeX strict without macros, callouts, links, figures, verification, style) and
`tools/SPEC-algorithms.md` (§5: pseudocode style; the rubric write-up formats for recursive algorithms, dynamic programs,
greedy algorithms and graph reductions) first; everything there applies. The whole site is private: no "private" notes.

## Sources

Handouts and official solutions (PDF + `pdftotext -layout` text) in `/home/claude/work/labs/`:
`lab6a.pdf`/`.txt` + `lab6a-sol.*`, … `lab8b` + `lab8b-sol`; `lab9a` and `lab9b` have **no official solutions** —
those pages are our own solutions and must say so in the meta line. Render a page to check figures/pseudocode:
`pdftoppm -f P -l P -r 110 -png /home/claude/work/labs/<file>.pdf /tmp/<you>/p` and Read the PNG.
Rubrics: `/home/claude/work/algo/algo-facts.md`. Book: `/home/claude/work/algo/` (`ch0N.txt`, PDF page = book page + 18).

## Files

```
content/3-homework-and-exams/lab-06a.md … lab-09b.md   one page per lab handout
tools/checks/labs_0N.py (+ .out)                       checks for lab N (a and b together), ending ALL OK
tools/figs_labs.py → tools/figs/lab-*.html             figures (only if they help), via tools/figlib.py; if the file
                                                        exists, append your own clearly marked section, never edit others'
```

## Page format

```markdown
---
title: "Lab 6a — Faster than brute force: binary search"
description: "One or two sentences: the problems and the idea each turns on."
tags: [lab, algorithms, divide-and-conquer, midterm-2]
---

*Lab 6a · September 30 · CS/ECE 374 A, Fall 2026 · [divide and conquer] · uses [[2-algorithms/01-recursion#…|§1.x]] ·
solutions: explained from the official solutions | ours — no official solutions were posted*

> [!abstract] In one breath
> The problems in one paragraph and the one idea each turns on.

## Problem 1 — Short title

> [!question] Problem 1
> The full statement, paraphrased faithfully and completely (every part, every example and its expected answer).

### (a) …

> [!hint]- Hint
> One or two sentences.

> [!solution]- Solution
> **The idea.** How to think about it — the observation that makes it work, in plain words (the student asked for an
> *explanation* of the answer, not only the answer).
>
> Then the answer in the rubric's format for its type (recursive algorithm / dynamic program / graph reduction), with
> pseudocode only where it clarifies, the running time, and why it is correct.
>
> **Answer.** The final algorithm and bound in one line.
```

- One `##` per problem (`## Problem 3 — …`); `###` per part. Mark the handout's "harder problems to think about later"
  with "(harder)" in the heading and solve them too.
- When the official solutions give several approaches, explain the most natural one fully and mention the others in a
  sentence or two (what changes). Do not copy the official text; explain in our own words. If an official solution has
  an error, fix it on the page, say so in one line, and report it.
- Link the site's chapter, concept and exercise pages where the same idea appears (grep headings for exact anchors), e.g.
  `[[2-algorithms/03-dynamic-programming#36-longest-increasing-subsequence|§3.6]]`, `[[concepts/graph-reductions]]`,
  `[[2-algorithms/05-basic-graph-algorithms-exercises#exercise-511--number-maze|Ex. 5.11]]`. Stay consistent with them.
- End with `### Sources for this page` (the lab handout and date; official solutions or "ours"; what the checks cover).

## Verification (mandatory)

Implement every algorithm exactly as the page states it and compare it with brute force on all small inputs plus random
ones; reproduce every example answer in the handout (e.g. 9 for the median example, 17 for the alternating subsequence,
8 for the number maze). For graph reductions, build the graph from random small inputs and compare the answer with an
exhaustive search over move sequences. Check every claimed running time at least by counting operations on growing inputs
where feasible. End with `ALL OK`; save the output (`python3 tools/checks/labs_0N.py | tee tools/checks/labs_0N.out`).
Then `python3 tools/check.py content /opt/npm-tools/node_modules/katex/dist/katex.min.js --only 3-homework-and-exams/lab-0N`
and one light-mode preview per page (`python3 /home/claude/work/preview/pageshot.py content/<page>.md /tmp/<you>/x.png light`,
then `tiles.py`), with the folded callouts expanded at least once to see the solutions render.

Do NOT git commit or push. Touch only your own files. Final message: files written, deviations from the official
solutions and why (errors found), anything unverified.
