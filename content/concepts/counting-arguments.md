---
title: "Counting arguments"
description: "There are only countably many regular expressions, grammars and Turing machines but uncountably many languages, so almost every language is not regular, not context-free and not even acceptable — and what this argument can and cannot prove."
tags: [concept, regular, context-free, undecidability, midterm-1]
aliases: ["counting argument", "countability argument", "uncountably many languages"]
---

> [!key] Countably many descriptions, uncountably many languages
> Every regular expression, context-free grammar and Turing machine is a **finite string** over a finite alphabet, so there are only **countably** many of each. But the languages over a non-empty alphabet $\Sigma$ — all subsets of $\Sigma^*$ — form an **uncountable** set. So all but countably many languages are not regular, not context-free, and not even acceptable.

**Why it works.** *Countable:* list strings by length, and alphabetically within each length; every string gets a position, and so does every description (§2.8 instead reads a regular expression as a base-8 numeral). *Uncountable:* given any list $L_1, L_2, \dots$ of languages and the list $w_1, w_2, \dots$ of all strings, the **diagonal** language $D = \{w_i \mid w_i\notin L_i\}$ differs from each $L_i$ on the string $w_i$, so no list contains every language (Cantor). §2.8 instead pairs languages over $\{\mathtt{1}\}$ with the real numbers in $[0,1)$.

> [!recipe] Recipe — the argument in three lines
> 1. Each *[regular expression / grammar / Turing machine]* is a finite string over a finite alphabet, so there are countably many of them, and countably many languages that they describe.
> 2. There are uncountably many languages over $\Sigma$ (Cantor's diagonal argument).
> 3. So some language over $\Sigma$ — in fact almost every one — has no such description.

**What it does not tell you.** It proves that non-regular, non-context-free and unacceptable languages *exist*, but it never names one, and it never shows that a *given* language is outside a class. For that you need a [[concepts/fooling-sets|fooling set]] (not regular) or [[concepts/diagonalization]] and [[concepts/undecidability-reductions|reductions]] (undecidable, unacceptable). Nor can it separate two countable classes, such as regular from context-free or decidable from acceptable.

> [!trap]
> - "Infinite" is not "uncountable": $\Sigma^*$ is infinite but countable; the set of all languages over $\Sigma$ is uncountable.
> - Every string and every description is finite, even when the language it describes is infinite.
> - A counting argument never proves that a specific language is not regular.

**Example.** Over $\{\mathtt{0},\mathtt{1}\}$ the list of strings begins $w_1 = \varepsilon$, $w_2 = \mathtt{0}$, $w_3 = \mathtt{1}$, $w_4 = \mathtt{00}$, $w_5 = \mathtt{01}$, $w_6 = \mathtt{10}$; in general $w_i$ is the binary numeral of $i$ with its leading 1 deleted ($6$ is `110`, so $w_6 = \mathtt{10}$). Against the list $L_1 = \varnothing$, $L_2 = \mathtt{0}^*$, $L_3 = (\mathtt{0}+\mathtt{1})^*$, $L_4 = \{\mathtt{0}^n\mathtt{1}^n \mid n\ge0\}$, the diagonal language contains $\varepsilon$ and $\mathtt{00}$ but not $\mathtt{0}$ or $\mathtt{1}$, so it differs from each $L_i$ at $w_i$.

**Where it appears.** [[1-models-of-computation/02-regular-languages#28-not-every-language-is-regular|§2.8]] (regular expressions as base-8 numerals; languages $L_\alpha$ from real numbers), [[1-models-of-computation/05-context-free-languages#56-not-every-language-is-context-free|§5.6]] (grammars as integers), [[1-models-of-computation/07-undecidability#76-aside-uncountable-barbers|§7.6]] (Cantor's theorem; not every language is acceptable), [[1-models-of-computation/07-undecidability#75-self-haters-gonna-self-hate|§7.5]] (the same diagonal argument, aimed at Turing machines).

Related: [[concepts/diagonalization]] · [[concepts/acceptable-and-decidable]] · [[concepts/regular-languages]] · [[concepts/fooling-sets]] · [[concepts/halting-problem]]
