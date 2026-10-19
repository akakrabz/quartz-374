---
title: "Closure properties"
description: "Which operations keep a language regular, context-free, decidable or acceptable: one table with the construction or counterexample behind every cell, and how to use closure to prove that a language is, or is not, in a class."
tags: [concept, regular, context-free, undecidability, midterm-1]
aliases: ["closure property", "closed under"]
---

> [!definition] Definition — closed under an operation
> A class of languages is **closed under** an operation if applying the operation to languages in the class always gives a language in the class. A "yes" is a construction that works for an *arbitrary* input; a "no" needs only *one* counterexample.

**Where it comes from.** The constructions are expressions, [[concepts/product-construction|product DFAs]] and NFAs for regular languages; new grammar rules for context-free ones; and for decidable and acceptable ones, Turing machines that run the given machines as subroutines — in parallel when one of them might run forever.

Below, $R, R'$ are regular expressions and $S_1, S_2$ start symbols of grammars for $L, L'$; a **homomorphism** $h$ replaces every symbol $a$ by a fixed string $h(a)$; $\textsf{half}(L) = \{w \mid ww\in L\}$; † marks a standard fact that the book does not prove.

| operation | regular | context-free | decidable | acceptable |
|---|---|---|---|---|
| $L\cup L'$ | yes: $R+R'$ | yes: ${S\to S_1\mid S_2}$ | yes: run both | yes: run both in parallel |
| $L\cap L'$ | yes: product DFA | **no**† (below) | yes: run both | yes: run one, then the other |
| $\overline{L}$ | yes: accept ${Q\setminus A}$ | **no**†: else De Morgan gives $\cap$ | yes: swap accept and reject | **no**: not for $\textsf{Halt}$ |
| $L\setminus L'$ | yes: product DFA | **no**†: ${\Sigma^*\setminus L}$ | yes: run both | **no**: ${\Sigma^*\setminus\textsf{Halt}}$ |
| $LL'$ | yes: $RR'$ | yes: ${S\to S_1S_2}$ | yes†: try every split | yes†: all splits in parallel |
| $L^*$ | yes: $R^*$ | yes: ${S\to\varepsilon\mid S_1S}$ | yes†: try every cutting | yes†: all cuttings in parallel |
| $L^R$ | yes: Lemma 4.4 | yes†: reverse every right side | yes†: reverse the input | yes†: reverse the input |
| $h(L)$ | yes†: $h(a)$ for $a$ in $R$ | yes†: $h(a)$ for $a$ in the rules | **no**† (below) | yes†: dovetail over preimages |
| $h^{-1}(L)$ | yes†: ${\delta'(q,a) = \delta^*(q,h(a))}$ | yes† | yes†: compute $h(w)$ first | yes†: compute $h(w)$ first |
| $L\cap R$, $R$ regular | yes: product DFA | yes†: product with a DFA | yes | yes |
| $\textsf{half}(L)$ | yes: Lemma 4.5 | **no**† (below) | yes†: decide $ww$ | yes†: run on $ww$ |

**The witnesses.** $\{\mathtt{0}^n\mathtt{1}^n\mathtt{2}^m\}$ ($S\to AC$, $A\to\mathtt{0}A\mathtt{1}\mid\varepsilon$, $C\to\mathtt{2}C\mid\varepsilon$) and, symmetrically, $\{\mathtt{0}^m\mathtt{1}^n\mathtt{2}^n\}$ are context-free, but their intersection $\{\mathtt{0}^n\mathtt{1}^n\mathtt{2}^n\}$ is not (the proof is beyond this course). $L = \{\mathtt{0}^n\mathtt{1}^n\}\,\mathtt{2}^*\mathtt{0}^*\,\{\mathtt{1}^n\mathtt{2}^n\}$ is context-free, but $\textsf{half}(L)\cap\mathtt{0}^+\mathtt{1}^+\mathtt{2}^+ = \{\mathtt{0}^n\mathtt{1}^n\mathtt{2}^n \mid n\ge1\}$ is not, so neither is $\textsf{half}(L)$. And $\{\langle M,w\rangle\#^t \mid M \text{ halts on } w \text{ within } t \text{ steps}\}$ is decidable, but erasing its $\#$s leaves $\textsf{Halt}$.

> [!recipe] Recipe — closure on an exam
> - **$L$ is regular:** build it from known regular languages with closed operations — "contains `11`, has even length, does not end in `0`" is an intersection of three.
> - **$L$ is not regular:** assume it is, combine it with *regular* languages by closed operations, and reach a known non-regular language — a contradiction.
> - **A new closure property:** give a construction that starts from an *arbitrary* DFA, grammar or machine ([[concepts/language-transformations|language transformations]]).

> [!trap]
> - Closure runs one way. If $L\cap R$ is not regular (with $R$ regular), then $L$ is not regular; if $L\cap R$ is regular, nothing follows. A regular union proves nothing either: ${\{\mathtt{0}^n\mathtt{1}^n\}\cup\overline{\{\mathtt{0}^n\mathtt{1}^n\}} = \Sigma^*}$.
> - Subsets and infinite unions are not closed operations: every language is a subset of $\Sigma^*$ and a union of one-string languages.
> - Context-free ∩ context-free can fail; context-free ∩ *regular* (and so context-free minus regular, $L\cap\overline{R}$) cannot.
> - Acceptable languages are not closed under complement — which is why "decidable" means acceptable *and* co-acceptable (Lemma 5).

**Example.** $L = \{\mathtt{0}^m\mathtt{1}^n \mid m\ne n\}$ is not regular. If it were, $\overline{L}\cap\mathtt{0}^*\mathtt{1}^*$ would be regular too (complement, then intersection with a regular language). But that language is $\{\mathtt{0}^n\mathtt{1}^n \mid n\ge0\}$, which is not regular (Lemma 3.6).

**Where it appears.** [[1-models-of-computation/03-finite-state-machines#36-the-product-construction|§3.6]] and [[1-models-of-computation/03-finite-state-machines#37-closure-properties|§3.7]] (boolean operations; Theorem 3.2, Corollaries 3.4–3.5), [[1-models-of-computation/04-nondeterministic-automata#49-regular-language-transformations|§4.9]] (Lemmas 4.4–4.5), [[1-models-of-computation/05-context-free-languages#55-regular-languages-are-context-free|§5.5]] (grammars for $\cup$, $\bullet$, $^*$), [[1-models-of-computation/07-undecidability#73-useful-properties|§7.3]] (Lemmas 2, 4 and 5); all classes at once in [[0-toolkit/03-the-big-picture|the big picture]].

**Practice.** [[practice/topics#product-construction-and-closure-properties|Product construction and closure properties]] (4 problems) — for example [[practice/03-finite-state-machines#31-closure-and-fooling-set-verdicts|3.1 Closure and fooling-set verdicts]] (easy), [[practice/03-finite-state-machines#36-a-product-written-formally|3.6 A product, written formally]] (medium), [[practice/03-finite-state-machines#39-three-look-alike-counting-languages|3.9 Three look-alike counting languages]] (hard).

Related: [[concepts/product-construction]] · [[concepts/language-transformations]] · [[concepts/regular-languages]] · [[concepts/context-free-grammars]] · [[concepts/acceptable-and-decidable]] · [[concepts/fooling-sets]]
