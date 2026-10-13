---
title: "Induction on strings"
description: "The proof pattern behind every claim about strings: an arbitrary string, a hypothesis for every shorter string, and cases that mirror the recursive definition — the graded template, its variations, and a worked example."
tags: [concept, strings, midterm-1]
aliases: ["string induction", "strong induction on strings"]
---

> [!key] The pattern
> To prove a claim $P(w)$ for every string $w$: let $w$ be an **arbitrary** string; assume $P(x)$ for **every** string $x$ with $\lvert x\rvert < \lvert w\rvert$; and prove $P(w)$ in **cases that cover every string** — usually $w = \varepsilon$ and $w = ax$. In the second case $\lvert x\rvert = \lvert w\rvert - 1 < \lvert w\rvert$, so the hypothesis applies to $x$.

**Why it works.** If the claim failed for some string, it would fail for a *shortest* one, $w$. The hypothesis says that nothing shorter than $w$ fails, and the cases show that $w$ cannot fail either. The cases mirror the recursive definition of [[concepts/strings|strings]] because that is how every function on strings unfolds. The hypothesis covers *all* shorter strings because that costs nothing, the graders expect it, and it still works when a proof needs a string two symbols shorter, or half as long.

> [!template] Template — induction on strings
> Let $w$ be an arbitrary string. \
> Assume, for every string $x$ with $\lvert x\rvert < \lvert w\rvert$, that *[the claim holds for $x$]*. \
> There are two cases to consider. \
> **Case $w = \varepsilon$.** … Therefore *[the claim holds for $w$]*. \
> **Case $w = ax$** for some symbol $a$ and string $x$. The induction hypothesis implies that *[the claim holds for $x$]*. … Therefore *[the claim holds for $w$]*. \
> In both cases, *[the claim holds for $w$]*. $\blacksquare$

**Variations.** Induct on the argument that the definitions take apart (the left argument of ${\bullet}$) and keep the others fixed — or, if the proof applies the hypothesis with *other* values of them, quantify over them: "for all strings $y$, and every $x$ with $\lvert x\rvert < \lvert w\rvert$". Any other split works if it covers every string and only shrinks it: the last symbol ($w = xa$, natural for DFAs); $w = a$ or $w = uv$ with $u$, $v$ non-empty (two base cases); or $w = abx$ for a function defined two symbols at a time.

> [!trap] Where induction proofs lose points
> - A **weak** hypothesis ("assume it for $x$, prove it for $ax$"): state it for every shorter string.
> - Applying the hypothesis to a string that is not shorter than $w$, or not saying why it is shorter.
> - Cases that miss strings: a definition with a case $w = abx$ needs base cases $\varepsilon$ *and* every single symbol.
> - Inducting on the wrong argument: the right argument of ${\bullet}$ never gets smaller.
> - Steps justified by "clearly": cite a definition, the hypothesis, or a lemma on every line.

> [!example] Example — $\lvert w^R\rvert = \lvert w\rvert$ for every string $w$
> Recall $\varepsilon^R := \varepsilon$ and $(ax)^R := x^R\bullet a$. Let $w$ be an arbitrary string, and assume that $\lvert x^R\rvert = \lvert x\rvert$ for every string $x$ with $\lvert x\rvert < \lvert w\rvert$. There are two cases.
>
> **Case $w = \varepsilon$.** $\lvert\varepsilon^R\rvert = \lvert\varepsilon\rvert$, because $\varepsilon^R = \varepsilon$ by the definition of ${}^R$.
>
> **Case $w = ax$** for some symbol $a$ and string $x$. Then $\lvert x\rvert < \lvert w\rvert$, so the induction hypothesis applies to $x$, and
> $$
> \begin{aligned}
> \lvert (ax)^R\rvert &= \lvert x^R\bullet a\rvert && \text{by definition of } {}^R\\
> &= \lvert x^R\rvert + \lvert a\rvert && \text{by Lemma 1.2}\\
> &= \lvert x\rvert + 1 && \text{by the induction hypothesis, and } \lvert a\rvert = 1\\
> &= \lvert ax\rvert && \text{by definition of } \lvert\cdot\rvert.
> \end{aligned}
> $$
> In both cases, $\lvert w^R\rvert = \lvert w\rvert$. $\blacksquare$

**Where it appears.** [[1-models-of-computation/01-strings#13-induction-on-strings|§1.3]] (the template and Lemmas 1.1–1.3), [[1-models-of-computation/01-strings#14-more-than-one-path-up-the-mountain|§1.4]] (other splits; quantifying the hypothesis), [[1-models-of-computation/01-strings#more-recursive-functions|more recursive functions]] (a model exam answer and its rubric). The same pattern proves DFAs correct ([[1-models-of-computation/03-finite-state-machines#33-proving-a-dfa-correct|§3.3]]) and the product lemma ([[1-models-of-computation/03-finite-state-machines#36-the-product-construction|§3.6]]); its cousin, structural induction, handles regular expressions ([[1-models-of-computation/02-regular-languages#26-proofs-about-regular-expressions|§2.6]]) and grammars ([[1-models-of-computation/05-context-free-languages#53-from-grammar-to-language|§5.3]]). Grading: [[0-toolkit/06-how-exams-are-graded|how exams are graded]].

**Practice.** [[practice/topics#induction-on-strings-and-recursive-functions|Induction on strings and recursive functions]] (9 problems) — for example [[practice/01-strings#11-unfold-an-accumulator|1.1 Unfold an accumulator]] (easy), [[practice/01-strings#14-reversal-with-an-accumulator|1.4 Reversal with an accumulator]] (medium), [[practice/01-strings#17-complementing-every-other-symbol|1.7 Complementing every other symbol]] (hard).

Related: [[concepts/strings]] · [[concepts/regular-expressions]] · [[concepts/dfa]] · [[concepts/context-free-grammars]]
