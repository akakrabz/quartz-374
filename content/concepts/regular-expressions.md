---
title: "Regular expressions"
description: "The notation for regular languages — ∅, strings, + (union), concatenation and * — with precedence, equivalence, a design recipe, expression trees, and the five-case structural induction."
tags: [concept, regular, midterm-1]
aliases: ["regular expression", "regex", "expression tree", "regular expression tree"]
---

> [!definition] Definition — regular expression and its language
> A **regular expression** is $\varnothing$, a string $w$ (possibly $\varepsilon$), or $S+T$, $ST$ or $S^*$ for regular expressions $S$ and $T$, with parentheses for grouping. Its **language** is
> $$
> L(\varnothing) = \varnothing,\quad L(w) = \{w\},\quad L(S+T) = L(S)\cup L(T),\quad L(ST) = L(S)\bullet L(T),\quad L(S^*) = L(S)^*.
> $$
> **Precedence:** $^*$ binds tightest, then concatenation, then $+$. Two expressions are **equivalent** if they have the same language.

**Where it comes from.** It is the recursive definition of [[concepts/regular-languages|regular languages]], written compactly. Every expression is really a **tree** whose root is the operation applied last; its subtrees are the **subexpressions**. So a proof about all regular expressions is a **structural induction** with five cases — $\varnothing$, a string, $S+T$, $ST$, $S^*$ — whose hypothesis covers the proper subexpressions $S$ and $T$ ([[1-models-of-computation/02-regular-languages#26-proofs-about-regular-expressions|template]]). By [[concepts/kleenes-theorem|Kleene's theorem]], expressions describe exactly the languages of DFAs.

> [!recipe] Recipe — designing a regular expression
> 1. **List short examples** in and out of the language, including $\varepsilon$ and every string of length 1 and 2.
> 2. **Cut a typical string into blocks** that a star can repeat; handle the beginning and the end separately.
> 3. **Write the expression piece by piece**, and say in English what each piece does.
> 4. **Test both directions:** nothing extra is generated and nothing is missed; check $\varepsilon$ explicitly.
> 5. **"And" conditions are hard:** refine the blocks, or build a [[concepts/product-construction|product DFA]] and convert it by [[concepts/state-elimination|state elimination]].

> [!trap] Classic mistakes
> - **Precedence:** $\mathtt{10}^*$ is $\mathtt{1}(\mathtt{0}^*)$, not $(\mathtt{10})^*$; and $\mathtt{0}+\mathtt{1}^*$ is not $(\mathtt{0}+\mathtt{1})^*$.
> - **Only the real syntax:** no $\cap$, no complement, no counters like $\mathtt{0}^n$, no regex shortcuts (`?`, `[01]`, `+` for "one or more", back-references). Write $RR^*$ for "one or more copies of $R$".
> - **$\varepsilon$ versus $\varnothing$:** $L(\varnothing^*) = \{\varepsilon\}$. A missing or extra $\varepsilon$ is the typical one-mistake deduction.
> - A well-formed substring of $R$ need not be a subexpression: induct on the tree, not on the characters.
> - In the $S^*$ case of a structural induction, the hypothesis covers $S$, not $S^*$.

> [!example] Example — binary strings with no `00`
> **Idea.** Every `0` except possibly the last symbol is followed by a `1`, so the string splits into blocks `1` and `01`, followed by at most one final `0`.
>
> **Answer:** $(\mathtt{1}+\mathtt{01})^*(\varepsilon+\mathtt{0})$. Cutting from the other end — every `0` except possibly the first symbol is preceded by a `1` — gives the equivalent $(\varepsilon+\mathtt{0})(\mathtt{1}+\mathtt{10})^*$.
>
> **Test:** $\varepsilon$, `0`, `10`, `0101` and `0110` match; `00`, `100` and `1001` do not.
>
> **A wrong answer:** $(\mathtt{1}+\mathtt{01})^*$ misses every string of the language that ends in `0` — `0`, `10`, `110`, … — infinitely many, so it earns no correctness credit.

**Where it appears.** [[1-models-of-computation/02-regular-languages#23-regular-languages-and-regular-expressions|§2.3]] (definition and the book's table of examples), [[1-models-of-computation/02-regular-languages#designing-a-regular-expression|designing an expression]] (two worked examples; grading), [[1-models-of-computation/02-regular-languages#24-things-that-arent-regular-expressions|§2.4]] (regexen), [[1-models-of-computation/02-regular-languages#25-regular-expression-trees|§2.5]] (trees), [[1-models-of-computation/02-regular-languages#26-proofs-about-regular-expressions|§2.6]] (structural induction). Expressions become NFAs by [[concepts/thompsons-algorithm|Thompson's algorithm]] ([[1-models-of-computation/04-nondeterministic-automata#46-regular-expression-to-nfa-thompsons-algorithm|§4.6]]), and automata become expressions by [[concepts/state-elimination|state elimination]] ([[1-models-of-computation/04-nondeterministic-automata#48-nfa-to-regular-expression-state-elimination|§4.8]]).

**Practice.** [[practice/topics#regular-expressions|Regular expressions]] (9 problems) — for example [[practice/02-regular-languages#22-read-these-expressions|2.2 Read these expressions]] (easy), [[practice/02-regular-languages#24-three-regular-expressions|2.4 Three regular expressions]] (medium), [[practice/02-regular-languages#27-two-careful-regular-expressions|2.7 Two careful regular expressions]] (hard).

Related: [[concepts/regular-languages]] · [[concepts/languages]] · [[concepts/kleenes-theorem]] · [[concepts/thompsons-algorithm]] · [[concepts/state-elimination]]
