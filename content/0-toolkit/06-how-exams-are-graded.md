---
title: "How exams are graded"
description: "Exam dates, scope and cheat-sheet rules; the Midterm 1 format; and a paraphrase of every standard rubric — induction, regular expressions and grammars, DFAs and NFAs, fooling sets, language transformations, diagonalization, reductions and Rice's theorem — with what loses points, the matching template and a worked problem for each."
tags: [toolkit, strings, regular, context-free, undecidability, midterm-1]
aliases: ["rubrics", "grading rubrics", "exam rubrics", "exam format"]
---

*Toolkit · reference page · the course's standard rubrics, paraphrased — the course website is authoritative.*

> [!warning] A paraphrase, not the rubrics themselves
> Everything on this page paraphrases the CS/ECE 374 A (Fall 2026) course website: its exam schedule, the Midterm 1 practice exams and the standard grading rubrics. The course website is authoritative. Where this page disagrees with it, or with the instructions printed on an exam, they win.

## 1. All rubrics at a glance

Each standard rubric is out of 10 points.

| rubric | where the 10 points go | template | worked problem |
|---|---|---|---|
| [[#4-induction\|induction]] | 1 arbitrary object · 2 explicit strong hypothesis · 2 exhaustive cases · 1 base cases · 2 correct use of the hypothesis · 2 other details | [[0-toolkit/02-proof-templates#1-induction-on-strings\|string induction]] | [[problems/induction-on-a-recursive-string-function\|sorting a string]] |
| [[#5-regular-expressions-and-grammars\|regular expression or grammar]] | 2 syntax · 8 correctness on exams: −2 for one mistake, −4 for a few wrong strings, −8 for infinitely many | [[0-toolkit/02-proof-templates#2-writing-up-a-regular-expression-or-a-grammar\|write-up]] | [[problems/regular-expression-and-dfa-for-one-language\|01 exactly twice]] (b) |
| [[#6-dfas-and-nfas\|DFA or NFA]] | 2 unambiguous, complete description · 6 correctness on exams · 2 mnemonic state names | [[0-toolkit/02-proof-templates#5-describing-a-dfa\|describing a DFA]] | [[problems/regular-expression-and-dfa-for-one-language\|01 exactly twice]] (a) |
| [[#7-fooling-sets\|fooling set]] | 4 explicit infinite fooling set · 2 explicit suffix $z$ · 2 one of $xz$, $yz$ in $L$ · 2 the other not | [[0-toolkit/02-proof-templates#7-fooling-set-proof\|fooling set]] | [[problems/fooling-set-and-grammar-for-one-language\|fooling set and grammar]] (a) |
| [[#8-language-transformations\|language transformation]] | 2 formal description of $M'$ from an arbitrary DFA · 2 English explanation · 6 correctness: 1 states, 1 start, 1 accepting, 3 transitions | [[0-toolkit/02-proof-templates#9-language-transformation\|transformation]] | [[problems/two-language-transformations\|insert and delete a 1]] |
| [[#diagonalization\|diagonalization]] | 4 wrapper machine · 6 contradiction, 3 per case | [[0-toolkit/02-proof-templates#12-undecidability-by-diagonalization\|diagonalization]] | Theorem 6, [[1-models-of-computation/07-undecidability#75-self-haters-gonna-self-hate\|§7.5]] |
| [[#reduction\|reduction]] | 4 the reduction · 3 "if" · 3 "only if" | [[0-toolkit/02-proof-templates#13-undecidability-by-reduction\|reduction]] | [[problems/undecidability-by-reduction-and-by-rice\|AtLeastTwo]] (a) |
| [[#rices-theorem\|Rice's theorem]] | 4 a machine whose language has the property · 4 one whose language does not · 2 details, including the right variant | [[0-toolkit/02-proof-templates#14-undecidability-by-rices-theorem\|Rice]] | [[problems/undecidability-by-reduction-and-by-rice\|AtLeastTwo]] (b) |

**On every problem** ([[#10-general-rules|§10]]): "clearly", "trivial" and "obviously" draw scrutiny; ambiguity is read unfavorably; an NFA where a DFA was asked earns half credit; $\varnothing$ or $\Sigma^*$ as a regular expression or grammar earns nothing; and any result from lecture, the lecture notes, labs or homework solutions may be used without proof.

## 2. Exams and cheat sheets

| exam | when | covers | cheat sheet |
|---|---|---|---|
| Midterm 1, "Models of computation" | Mon Sep 28, 2026 (done) | induction on strings and languages, regular languages and regular expressions, DFAs, NFAs, fooling sets, regular language transformations, context-free languages and grammars (Chapters 1–5); no Turing machines | one sheet |
| Midterm 2, "Algorithms" | Mon Nov 9, 2026, 7–9 pm | the [[2-algorithms/index\|algorithms]] half of the course | one sheet |
| Final exam, "Everything" | Fri Dec 11, 2026, 8–11 am | everything, including Chapters 6–9, which are tested only here | two sheets |

A cheat sheet is a double-sided letter-size sheet, and it must be **handwritten**. The formats of Midterm 2 and of the final exam are not described here; check the course website.

## 3. The Midterm 1 format

Midterm 1's practice exams have **5 problems in 120 minutes**, one of each type below. Students may use **any result from lecture, the lecture notes, labs or homework solutions without proof** — cite it by name: "by Lemma 3.6", "by the product construction".

| problem type | what to hand in | template | rubric | worked problem |
|---|---|---|---|---|
| true/false, 10 parts | each answer with a one-sentence justification | — | — | sample items close every chapter page: [[1-models-of-computation/01-strings#summary\|Ch 1]], [[1-models-of-computation/02-regular-languages#summary\|2]], [[1-models-of-computation/03-finite-state-machines#summary\|3]], [[1-models-of-computation/04-nondeterministic-automata#summary\|4]], [[1-models-of-computation/05-context-free-languages#summary\|5]] |
| regular language transformations, two parts | for each, an automaton built from an arbitrary DFA for $L$ | [[0-toolkit/02-proof-templates#9-language-transformation\|transformation]] | [[#8-language-transformations\|§8]] | [[problems/two-language-transformations\|insert and delete a 1]] |
| induction on a recursively defined string function | a complete induction proof | [[0-toolkit/02-proof-templates#1-induction-on-strings\|string induction]] | [[#4-induction\|§4]] | [[problems/induction-on-a-recursive-string-function\|sorting a string]] |
| non-regularity plus a grammar for the same language | a fooling-set proof and a context-free grammar | [[0-toolkit/02-proof-templates#7-fooling-set-proof\|fooling set]], [[0-toolkit/02-proof-templates#2-writing-up-a-regular-expression-or-a-grammar\|write-up]] | [[#7-fooling-sets\|§7]], [[#5-regular-expressions-and-grammars\|§5]] | [[problems/fooling-set-and-grammar-for-one-language\|fooling set and grammar]] |
| a DFA plus a regular expression for the same language | both, with mnemonic state names; no proof needed | [[0-toolkit/02-proof-templates#5-describing-a-dfa\|describing a DFA]], [[0-toolkit/02-proof-templates#2-writing-up-a-regular-expression-or-a-grammar\|write-up]] | [[#6-dfas-and-nfas\|§6]], [[#5-regular-expressions-and-grammars\|§5]] | [[problems/regular-expression-and-dfa-for-one-language\|01 exactly twice]] |

## 4. Induction

| points | for |
|---|---|
| 1 | starting from an **arbitrary** object: "let $w$ be an arbitrary string" |
| 2 | an **explicit, strong** induction hypothesis — weak induction is discouraged |
| 2 | **exhaustive** cases: together they cover every object |
| 1 | the **base cases** |
| 2 | **correct use** of the induction hypothesis |
| 2 | the other details |

The wording ("an arbitrary object") fits every induction in the course — over strings, regular expressions, numbers or derivations. A proof that a grammar generates a language is two of them.

> [!trap] What loses points
> - A hypothesis that is never written down, or a weak one ("assume the claim for $x$; prove it for $ax$"). State it for **every** smaller object.
> - Applying the hypothesis to something that is not smaller than $w$ — or not saying why it is smaller.
> - Cases that miss strings: a definition with a case $w = abx$ needs base cases for $\varepsilon$ **and** for every single symbol.
> - Inducting on the wrong argument: concatenation takes its left argument apart, so the right one never gets smaller.
> - A step justified by "clearly" instead of by a definition, the hypothesis or a lemma.

**Templates:** [[0-toolkit/02-proof-templates#1-induction-on-strings|string induction]], [[0-toolkit/02-proof-templates#3-induction-on-regular-expressions|structural induction]], [[0-toolkit/02-proof-templates#10-proving-what-a-grammar-generates|what a grammar generates]] · **worked:** [[problems/induction-on-a-recursive-string-function|sorting a string]], [[problems/proving-what-a-grammar-generates|a grammar proof]] · **traps in context:** [[1-models-of-computation/01-strings#14-more-than-one-path-up-the-mountain|§1.4]], [[concepts/induction-on-strings|induction on strings]]

## 5. Regular expressions and grammars

| points | for |
|---|---|
| 2 | syntax |
| 8 | correctness (on exams) |

Exam deductions are twice the homework ones:

| mistake | homework | exam |
|---|---|---|
| one mistake — often a missing or extra $\varepsilon$ | −1 | −2 |
| a few wrong strings | −2 | −4 |
| infinitely many wrong strings | no correctness credit | no correctness credit: −8 |
| the answer $\varnothing$ or $\Sigma^*$ | no credit | no credit |

Homework answers must also explain each piece in English, and for a grammar, **every nonterminal** needs a self-contained description of its language. **Ambiguity is not penalized**: an ambiguous grammar that generates the right language earns full credit.

> [!trap] What loses points
> - $\varepsilon$, forgotten or let in by accident. Test it first.
> - Precedence: $\mathtt{1}\mathtt{0}^*$ is not $(\mathtt{10})^*$, and a misplaced star usually changes infinitely many strings.
> - Syntax that regular expressions do not have: $\cap$, complement, $\mathtt{0}^n$, a "plus" that means "one or more".
> - A union with a forgotten case, like a grammar for "not of the form $\mathtt{0}^n\mathtt{1}^n$" that misses every string containing `10` ([[1-models-of-computation/05-context-free-languages#designing-a-grammar|§5.4]], Example 2).
> - A nonterminal described by its role ("the middle part") instead of by its language.

**Template:** [[0-toolkit/02-proof-templates#2-writing-up-a-regular-expression-or-a-grammar|write-up]] · **worked:** [[problems/regular-expression-and-dfa-for-one-language|01 exactly twice]] (b), [[problems/fooling-set-and-grammar-for-one-language|fooling set and grammar]] (b), [[problems/state-elimination-by-hand|state elimination by hand]] · **traps in context:** [[1-models-of-computation/02-regular-languages#designing-a-regular-expression|§2.3]], [[1-models-of-computation/05-context-free-languages#designing-a-grammar|§5.4]]

## 6. DFAs and NFAs

| points | for |
|---|---|
| 2 | an **unambiguous, complete description**: a start arrow and double circles; say so if you leave out a trash (dump) state; a description in text gives the whole transition function; an NFA states its $\varepsilon$-transitions; a product construction describes each factor and the accepting states |
| 6 | correctness (on exams) |
| 2 | **mnemonic** state names |

**An NFA where a DFA was asked earns half credit.** The rubric has no line for minimality; a clear machine with a few extra states is better than a minimal one you cannot explain ([[1-models-of-computation/03-finite-state-machines#35-designing-dfas-dfas-are-algorithms|§3.5]]).

> [!trap] What loses points
> - Missing transitions and no sentence about a dump state: the machine is incomplete — or an NFA, which earns half credit.
> - States named $q_0, q_1, \dots$ with no meaning attached.
> - "Run both machines in parallel" with no description of the factors, the pairs and the accepting pairs.
> - Factors of a product that are not complete DFAs over the same alphabet: the union and the difference then lose strings.

**Templates:** [[0-toolkit/02-proof-templates#5-describing-a-dfa|describing a DFA]], [[0-toolkit/02-proof-templates#6-writing-up-a-product-construction|product construction]] · **worked:** [[problems/regular-expression-and-dfa-for-one-language|01 exactly twice]] (a), [[problems/a-product-construction-written-formally|a product, written formally]], [[problems/subset-construction-by-hand|subset construction by hand]] · **traps in context:** [[1-models-of-computation/03-finite-state-machines#32-formal-definitions|§3.2]], [[1-models-of-computation/03-finite-state-machines#36-the-product-construction|§3.6]]

## 7. Fooling sets

| points | for |
|---|---|
| 4 | an explicit **infinite** set that really is a fooling set — a finite set earns nothing |
| 2 | for arbitrary distinct $x, y\in F$: an explicit suffix $z$ |
| 2 | showing that one of $xz$ and $yz$ is in $L$ |
| 2 | showing that the other is not |

> [!trap] What loses points
> - One example pair instead of arbitrary distinct $x$ and $y$, written with parameters $i\ne j$.
> - "Assume $i<j$" without "without loss of generality" — or when the argument is not symmetric, because $z$ was built from $x$.
> - Only one half shown, or a half with no reason.
> - A set described by what it should do ("all the prefixes we need") instead of explicitly.
> - A suffix that depends on a DFA you are trying to rule out.

**Template:** [[0-toolkit/02-proof-templates#7-fooling-set-proof|fooling set]] · **worked:** [[problems/fooling-set-and-grammar-for-one-language|fooling set and grammar]] (a) · **traps in context:** [[1-models-of-computation/03-finite-state-machines#38-proving-a-language-is-not-regular|§3.8]], [[concepts/fooling-sets|fooling sets]]

## 8. Language transformations

| points | for |
|---|---|
| 2 | a **formal, complete description** of the new machine $M'$, built from an **arbitrary** DFA $M$ — say whether $M'$ is a DFA or an NFA, and give its $\varepsilon$-transitions |
| 2 | an **English explanation** of the states and of the accepting states |
| 6 | correctness: 1 for the states, 1 for the start state, 1 for the accepting states, 3 for the transitions |

Before handing in, run the construction on the edge cases the rubric names: $L = \varnothing$, $\{\varepsilon\}$, $\mathtt{1}^*$ and $\Sigma^*$.

> [!trap] What loses points
> - A construction for one particular DFA or language: the claim is about **every** regular $L$.
> - $\delta'$ left undefined for some state and symbol, or for $\varepsilon$.
> - The two kinds mixed up: $\{w \mid f(w)\in L\}$ simulates $M$ on $f(w)$; $\{f(w) \mid w\in L\}$ guesses $w$.
> - Complementing an NFA by swapping its accepting states.

**Template:** [[0-toolkit/02-proof-templates#9-language-transformation|transformation]] · **worked:** [[problems/two-language-transformations|insert and delete a 1]] · **traps in context:** [[1-models-of-computation/04-nondeterministic-automata#49-regular-language-transformations|§4.9]], [[concepts/language-transformations|language transformations]]

## 9. Undecidability

Chapters 6–9 are tested on the final exam only. An undecidability proof is graded with the rubric of its method.

### Diagonalization

| points | for |
|---|---|
| 4 | the wrapper machine, built from the hypothetical decider |
| 6 | the contradiction: 3 for each of the two cases |

### Reduction

| points | for |
|---|---|
| 4 | the reduction: the new decider and the machine $M'$ it writes down |
| 3 | "if": a yes-instance ($M$ accepts $w$) makes the new decider accept |
| 3 | "only if": a no-instance ($M$ rejects **or diverges**) makes it reject |

### Rice's theorem

| points | for |
|---|---|
| 4 | a machine whose language has the property |
| 4 | a machine whose language does not |
| 2 | the details, including the right variant of the theorem |

> [!trap] What loses points
> - **The wrong direction.** Deciding $L$ with the help of a decider for $\textsf{Halt}$ proves nothing; the hypothetical decider for $L$ must be the subroutine.
> - **Running $M'$.** The new decider only writes $\langle M'\rangle$ down; it must halt on every input.
> - **"Does not accept" read as "rejects".** It also means "diverges", and the "only if" case must cover both.
> - **Unnamed machines.** Name the hypothetical decider, the decider you build, $M$ and $M'$, and never write "it".
> - **Rice where it does not apply:** a behavior ($\textsf{ThisIsSparta}$), self-reference ($\textsf{RevAccept}$), a trivial property — or the wrong variant, such as a property of $\textsf{Halt}(M)$ treated as one of $\textsf{Accept}(M)$.
> - **Diagonalizing against the wrong machine.** The contradiction comes from running the machine built from the decider on its own encoding.

**Templates:** [[0-toolkit/02-proof-templates#12-undecidability-by-diagonalization|diagonalization]], [[0-toolkit/02-proof-templates#13-undecidability-by-reduction|reduction]], [[0-toolkit/02-proof-templates#14-undecidability-by-rices-theorem|Rice]] · **worked:** [[problems/undecidability-by-reduction-and-by-rice|AtLeastTwo]]; Theorem 6 in [[1-models-of-computation/07-undecidability#75-self-haters-gonna-self-hate|§7.5]] · **traps in context:** [[1-models-of-computation/07-undecidability#79-the-halting-problem-via-reduction|§7.9]], [[1-models-of-computation/07-undecidability#711-rices-theorem|§7.11]]

## 10. General rules

- **"Clearly", "trivial" and "obviously" draw scrutiny.** A grader reads the step they introduce more closely. Write the reason instead: a definition, the hypothesis, a lemma.
- **Ambiguity is read unfavorably.** When an answer can be read two ways, expect the reading that earns less: define every symbol, name every machine, label every edge. (An *ambiguous grammar* is a different thing, and costs nothing.)
- **An NFA where a DFA was asked earns half credit.**
- **$\varnothing$ or $\Sigma^*$ as a regular expression or grammar earns no credit.**
- **Cite instead of reproving.** Any result from lecture, the lecture notes, labs or homework solutions may be used without proof.
- **Cheat sheets are handwritten:** one double-sided letter sheet for a midterm, two for the final.

Related: [[0-toolkit/02-proof-templates|proof templates]] · [[0-toolkit/01-notation-and-conventions|notation and conventions]] · [[0-toolkit/03-the-big-picture|the big picture]]

### Sources for this page
Exam dates and scope, the cheat-sheet rules, the Midterm 1 format (from its practice exams) and the standard rubrics come from the CS/ECE 374 A (Fall 2026) course website and are paraphrased here; the website is authoritative. The "what loses points" lists collect the traps of the chapter and concept pages linked from each section.
