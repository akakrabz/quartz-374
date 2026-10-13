---
title: "Languages"
description: "A language is any set of strings — a yes/no problem. Union, concatenation and Kleene star build new languages; their algebra (Lemmas 2.1–2.3, Arden's rule), and why ∅, {ε} and ε are three different things."
tags: [concept, regular, midterm-1]
aliases: ["language", "formal language", "Kleene star", "Kleene plus", "concatenation of languages"]
---

> [!definition] Definition — language, concatenation, Kleene star
> A **language** over $\Sigma$ is any set $L\subseteq\Sigma^*$ of strings, finite or infinite. Besides the set operations ($\cup$, $\cap$, $\setminus$, $\oplus$, and the complement $\overline{L} := \Sigma^*\setminus L$), two operations use the fact that the elements are strings:
> - **concatenation** $A\bullet B := \{xy \mid x\in A \text{ and } y\in B\}$, usually written $AB$;
> - **Kleene star** $L^*$: $w\in L^*$ iff $w = \varepsilon$, or $w = xy$ for some $x\in L$ and $y\in L^*$ — the concatenations of zero or more strings from $L$. The **Kleene plus** $L^+ := L\bullet L^*$ allows one or more.

**Why it matters.** A language is a decision problem: given $w$, is $w\in L$? Every model in the course — [[concepts/regular-expressions|regular expressions]], [[concepts/dfa|DFAs]], [[concepts/nfa|NFAs]], [[concepts/context-free-grammars|grammars]], [[concepts/turing-machines|Turing machines]] — is a *finite* description of a possibly infinite language, and the course asks which languages each kind of description can reach.

**The algebra** (Lemmas 2.1–2.3). $\varnothing L = L\varnothing = \varnothing$ and $\{\varepsilon\}L = L\{\varepsilon\} = L$; concatenation is associative and distributes over $\cup$; $L^* = \{\varepsilon\}\cup L^+ = L^*L^*$; $L^+ = L^*$ iff $\varepsilon\in L$; $\varnothing^* = \{\varepsilon\}^* = \{\varepsilon\}$, and every other $L^*$ is infinite. **Arden's rule:** if $\varepsilon\notin A$, then $L = AL\cup B$ holds if and only if $L = A^*B$.

> [!recipe] Recipe — testing a claimed identity (true/false questions)
> 1. Try the extreme languages $\varnothing$, $\{\varepsilon\}$ and $\Sigma^*$, then a one-string language such as $\{\mathtt{0}\}$.
> 2. List the short strings on each side; a counterexample, if there is one, usually has length at most 2.
> 3. If none turns up, prove both inclusions: an arbitrary $w$ on the left is on the right, and conversely.

> [!trap] Classic mistakes
> - $\varnothing$ (no strings), $\{\varepsilon\}$ (one string) and $\varepsilon$ (a string, not a language) are three different things: $\varnothing\bullet L = \varnothing$ but $\{\varepsilon\}\bullet L = L$.
> - Concatenation is not commutative, and it does not distribute over $\cap$.
> - $L^2 = LL$ is all concatenations of *two* strings of $L$, not $\{ww \mid w\in L\}$: for $L = \{\mathtt{0},\mathtt{1}\}$, $LL$ has four strings, but $\{ww \mid w\in L\} = \{\mathtt{00},\mathtt{11}\}$.
> - $AB$ can have fewer than $\lvert A\rvert\cdot\lvert B\rvert$ strings: different pairs can glue to the same string.
> - The complement depends on the alphabet: $\overline{L} = \Sigma^*\setminus L$.

**Example.** Let $A = \{\mathtt{0},\mathtt{01}\}$ and $B = \{\mathtt{1},\mathtt{11}\}$. Then $AB = \{\mathtt{01},\mathtt{011},\mathtt{0111}\}$ has only three strings, because $\mathtt{0}\bullet\mathtt{11} = \mathtt{01}\bullet\mathtt{1}$, while $BA = \{\mathtt{10},\mathtt{101},\mathtt{110},\mathtt{1101}\}$; so $AB\ne BA$. The star $A^* = \{\varepsilon,\mathtt{0},\mathtt{00},\mathtt{01},\mathtt{000},\mathtt{001},\mathtt{010},\dots\}$ is exactly the set of binary strings in which every `1` is immediately preceded by a `0`.

**Where it appears.** [[1-models-of-computation/02-regular-languages#21-languages|§2.1]] (definition; the three "empty" things), [[1-models-of-computation/02-regular-languages#22-building-languages|§2.2]] (operations, Lemmas 2.1–2.3, solving a DFA with Arden's rule), [[1-models-of-computation/02-regular-languages#28-not-every-language-is-regular|§2.8]] (uncountably many languages, only countably many descriptions). How the classes of languages fit together: [[0-toolkit/03-the-big-picture|the big picture]].

**Practice.** [[practice/topics#languages-and-their-operations|Languages and their operations]] (3 problems) — for example [[practice/02-regular-languages#21-empty-things-products-and-stars|2.1 Empty things, products and stars]] (easy), [[practice/02-regular-languages#25-equivalent-or-not|2.5 Equivalent or not]] (medium).

Related: [[concepts/strings]] · [[concepts/regular-languages]] · [[concepts/regular-expressions]] · [[concepts/closure-properties]] · [[concepts/counting-arguments]]
