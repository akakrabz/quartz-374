---
title: "Practice problems"
description: "60 practice problems for Chapters 1–7 of Models of Computation — 24 easy, 20 medium, 16 hard — each with a folded hint and a worked solution, and every automaton, expression and grammar machine-checked. Browse by chapter, by difficulty or by topic."
tags: [practice]
---

Knowing the definitions and being able to *produce* a DFA, a fooling set or a reduction under time pressure are different skills, and only the second one is tested. This bank has **60 problems for Chapters 1–7**: quick true-or-false checks, standard exam parts, and full exam-length problems in the formats of the course's exams. None of them is copied from a course exam or homework.

> [!recipe] How to use the bank
> 1. Pick a chapter you have read and do its **easy** problems first — a few minutes each, one idea per problem.
> 2. Work on paper, the way you will on the exam. Open the **hint** only after you have been stuck for a few minutes, and the **solution** only once you have an answer you would hand in.
> 3. Compare with the **Answer.** line, then read the solution's *Check*: it shows how to test your own answer (run the DFA on a few strings, try $\varepsilon$, try the shortest strings in and out of the language).
> 4. Move on to **medium** (one exam part), then **hard** (a whole exam problem, about 20 minutes).
> 5. A day later, redo every problem you got wrong, without looking.

> [!tip] Before the final
> Go chapter by chapter: read the chapter's *definition*, *template* and *trap* boxes, then do its easy problems and one medium. Leave the hard problems for a second pass, and write your handwritten cheat sheet from the [[0-toolkit/02-proof-templates|proof templates]] and the [[0-toolkit/04-review-regular-and-context-free|exam review]] pages.

## The tag system

Every problem's title bar carries one **difficulty tag** and one to three **topic tags**, for example

> [!easy] Easy · fooling sets · true or false
> The problem statement sits in this box; the folded *Hint* and *Solution* boxes below it open with a click.

| difficulty | what it means | time |
|---|---|---|
| <span class="diff easy">easy</span> | one definition or one idea: a true-or-false item with a one-sentence reason, a short regular expression or DFA, a single induction step, or spotting one error | 2–5 min |
| <span class="diff medium">medium</span> | a standard exam part: a DFA or grammar with state or nonterminal meanings, a full fooling-set proof, a short induction proof, or one construction carried out by hand | 10–15 min |
| <span class="diff hard">hard</span> | a full exam problem: a language transformation with a formal construction, a two-part regular-and-context-free problem, a complete proof about a recursive function, or an undecidability proof | 20–30 min |

Browse: [[practice/easy|all 24 easy]] · [[practice/medium|all 20 medium]] · [[practice/hard|all 16 hard]] · [[practice/topics|by topic]] — 19 topics that cut across chapters, plus the true-or-false checks and the find-the-error items.

## By chapter

| ch | chapter | practice | easy | medium | hard |
|---|---|---|---|---|---|
| 1 | [[1-models-of-computation/01-strings\|Strings]] | [[practice/01-strings\|8 problems]] | [[practice/easy#chapter-1--strings\|3]] | [[practice/medium#chapter-1--strings\|3]] | [[practice/hard#chapter-1--strings\|2]] |
| 2 | [[1-models-of-computation/02-regular-languages\|Regular languages]] | [[practice/02-regular-languages\|8 problems]] | [[practice/easy#chapter-2--regular-languages\|3]] | [[practice/medium#chapter-2--regular-languages\|3]] | [[practice/hard#chapter-2--regular-languages\|2]] |
| 3 | [[1-models-of-computation/03-finite-state-machines\|Finite-state machines]] | [[practice/03-finite-state-machines\|10 problems]] | [[practice/easy#chapter-3--finite-state-machines\|4]] | [[practice/medium#chapter-3--finite-state-machines\|3]] | [[practice/hard#chapter-3--finite-state-machines\|3]] |
| 4 | [[1-models-of-computation/04-nondeterministic-automata\|Nondeterministic automata]] | [[practice/04-nondeterministic-automata\|10 problems]] | [[practice/easy#chapter-4--nondeterministic-automata\|4]] | [[practice/medium#chapter-4--nondeterministic-automata\|3]] | [[practice/hard#chapter-4--nondeterministic-automata\|3]] |
| 5 | [[1-models-of-computation/05-context-free-languages\|Context-free languages]] | [[practice/05-context-free-languages\|10 problems]] | [[practice/easy#chapter-5--context-free-languages\|4]] | [[practice/medium#chapter-5--context-free-languages\|3]] | [[practice/hard#chapter-5--context-free-languages\|3]] |
| 6 | [[1-models-of-computation/06-turing-machines\|Turing machines]] | [[practice/06-turing-machines\|6 problems]] | [[practice/easy#chapter-6--turing-machines\|3]] | [[practice/medium#chapter-6--turing-machines\|2]] | [[practice/hard#chapter-6--turing-machines\|1]] |
| 7 | [[1-models-of-computation/07-undecidability\|Undecidability]] | [[practice/07-undecidability\|8 problems]] | [[practice/easy#chapter-7--undecidability\|3]] | [[practice/medium#chapter-7--undecidability\|3]] | [[practice/hard#chapter-7--undecidability\|2]] |
| | **total** | **60** | **24** | **20** | **16** |

Chapters 1–5 were the scope of Midterm 1; Chapters 6–7 (Turing machines and undecidability) are on the final. Chapters 8 and 9 have no practice pages: their material is mostly conceptual and is exercised by the true-or-false items of Chapters 6–7.

## How the answers were checked

Every regular expression, DFA, NFA, grammar and Turing machine in a solution is checked by a script against a brute-force definition of the language, over all strings up to length 10–14 (and exactly, by DFA equivalence, wherever the language is regular). Constructions such as language transformations are checked on many random DFAs. Induction proofs were checked step by step, and every claim they prove was tested on all short strings. Every solution was also proofread in the rendered page with its hint and solution unfolded. The scripts are in `tools/practice/checks/`.
