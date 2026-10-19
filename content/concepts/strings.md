---
title: "Strings"
description: "A string is either empty or a symbol followed by a string. That recursive definition gives Σ*, length and concatenation, the pieces of a string (prefixes, suffixes, substrings, subsequences), and the shape of every proof about strings."
tags: [concept, strings, midterm-1]
aliases: ["string", "alphabet", "empty string", "substring", "subsequence"]
---

> [!definition] Definition — alphabet, string, $\Sigma^*$
> An **alphabet** $\Sigma$ is a finite set of **symbols**. A **string** over $\Sigma$ is either the **empty string** $\varepsilon$, or a pair $a\cdot x$ (written $ax$) of a symbol $a\in\Sigma$ and a string $x$. $\Sigma^*$ is the set of all strings over $\Sigma$: an infinite set (if $\Sigma\ne\varnothing$), but every string in it is finite. Length and concatenation follow the same two cases:
> $$
> \lvert w\rvert := \begin{cases} 0 & \text{if } w = \varepsilon\\ 1 + \lvert x\rvert & \text{if } w = ax\end{cases}
> \qquad\qquad
> w\bullet z := \begin{cases} z & \text{if } w = \varepsilon\\ a\cdot(x\bullet z) & \text{if } w = ax.\end{cases}
> $$

**Where it comes from.** A string is built like a linked list: a first symbol and the rest. So every function on strings has a case for $\varepsilon$ and a case for $ax$ that recurses on the shorter string $x$, and every proof about strings is an [[concepts/induction-on-strings|induction on strings]] with the same two cases. Concatenation takes apart only its **left** argument, which is why proofs about $w\bullet z$ induct on $w$. Lemmas 1.1–1.3 say $w\bullet\varepsilon = w$, $\lvert w\bullet x\rvert = \lvert w\rvert + \lvert x\rvert$, and $(w\bullet x)\bullet y = w\bullet(x\bullet y)$: concatenation is associative (so dots and parentheses are dropped) but not commutative.

> [!definition] The pieces of a string $w$ of length $n$
> | piece of $w$ | definition | how many |
> |---|---|---|
> | prefix | $w = px$ for some string $x$ | exactly $n+1$ |
> | suffix | $w = xs$ for some string $x$ | exactly $n+1$ |
> | substring | $w = xyz$ for some strings $x$, $z$ (contiguous) | at most $n(n+1)/2$ non-empty ones |
> | subsequence | delete zero or more symbols, anywhere | at most $2^n$ |
>
> A **proper** prefix, suffix, substring or subsequence is one other than $w$ itself. Every substring is a subsequence, but not conversely.

> [!recipe] Recipe — a newly defined string function (an exam problem type)
> 1. **Unfold it** on two or three tiny inputs, case by case, exactly as the definition says (as in the example below).
> 2. **Test the claim** you are asked to prove on those inputs; a false "identity" usually fails on a two-symbol string.
> 3. **Find the argument the definition takes apart** — for ${\bullet}$, the left one. The induction goes on that argument.
> 4. Write the [[concepts/induction-on-strings|string-induction template]], with a definition, the hypothesis, or one of Lemmas 1.1–1.3 cited on every line.

> [!trap] Classic mistakes
> - $\varepsilon$ is a string; $\{\varepsilon\}$ is a language with one string; $\varnothing$ is the empty language ([[concepts/languages|languages]]).
> - $\Sigma^*$ contains no infinite strings: "$\mathtt{000}\cdots$" is not an element of $\{\mathtt{0}\}^*$.
> - Reversal flips the order: $(wx)^R = x^Rw^R$, not $w^Rx^R$ (try $w = \mathtt{0}$, $x = \mathtt{1}$).
> - Substring is not subsequence: `0110` contains `00` as a subsequence but not as a substring. "Contains `00`" means substring unless the problem says otherwise.
> - Formally the symbol $a$ and the one-symbol string $a\cdot\varepsilon$ differ; $a\bullet z = a\cdot z$ uses both cases of the definition of ${\bullet}$.

**Example.** Unfolding the definition, $\mathtt{ba}\bullet\mathtt{na} = \mathtt{b}\cdot(\mathtt{a}\bullet\mathtt{na}) = \mathtt{b}\cdot\big(\mathtt{a}\cdot(\varepsilon\bullet\mathtt{na})\big) = \mathtt{bana}$. The string $w = \mathtt{banana}$ has length 6, so it has 7 prefixes and 7 suffixes (counting $\varepsilon$ and $w$). It has only 15 distinct non-empty substrings, not $6\cdot7/2 = 21$, because some repeat — `ana` starts at positions 2 and 4 — and only 40 distinct subsequences, not $2^6 = 64$. `bnn` is a subsequence of `banana` but not a substring.

**Where it appears.** [[1-models-of-computation/01-strings#11-strings|§1.1]] (definition), [[1-models-of-computation/01-strings#12-two-recursive-functions|§1.2]] (length and concatenation), [[1-models-of-computation/01-strings#15-indices-substrings-and-subsequences|§1.5]] (indices and pieces), [[1-models-of-computation/01-strings#more-recursive-functions|more recursive functions]] ($\#(a,w)$, reversal, powers, complement). Later definitions recurse the same way, for example a DFA's $\delta^*$ ([[1-models-of-computation/03-finite-state-machines#32-formal-definitions|§3.2]]).

**Practice.** [[practice/topics#induction-on-strings-and-recursive-functions|Induction on strings and recursive functions]] (9 problems) — for example [[practice/01-strings#11-unfold-an-accumulator|1.1 Unfold an accumulator]] (easy), [[practice/01-strings#14-reversal-with-an-accumulator|1.4 Reversal with an accumulator]] (medium), [[practice/01-strings#17-complementing-every-other-symbol|1.7 Complementing every other symbol]] (hard).

Related: [[concepts/induction-on-strings]] · [[concepts/languages]] · [[concepts/dfa]] · [[concepts/regular-expressions]]
