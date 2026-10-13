---
title: "Regular languages"
description: "The languages built from ∅ and single strings by finitely many unions, concatenations and stars — exactly the languages of DFAs and NFAs. The recursive definition, three ways to prove a language regular, and the operations that preserve regularity."
tags: [concept, regular, midterm-1]
aliases: ["regular language", "automatic language"]
---

> [!definition] Definition — regular language
> A language $L$ is **regular** if and only if
> - $L$ is empty;
> - $L$ contains exactly one string (which may be $\varepsilon$);
> - $L$ is the union of two regular languages;
> - $L$ is the concatenation of two regular languages; or
> - $L$ is the Kleene star of a regular language.
>
> [[concepts/regular-expressions|Regular expressions]] are the notation for this definition. By [[concepts/kleenes-theorem|Kleene's theorem]], $L$ is regular if and only if some [[concepts/dfa|DFA]] accepts it (the book calls such languages **automatic**), if and only if some [[concepts/nfa|NFA]] accepts it.

**Why it matters.** The regular languages are exactly the problems that a one-pass, constant-memory algorithm can solve. Every finite language is regular (a finite union of one-string languages), and so is $\Sigma^*$. But there are only countably many regular languages and uncountably many languages, and specific ones such as $\{\mathtt{0}^n\mathtt{1}^n \mid n\ge0\}$ are not regular — [[concepts/fooling-sets|fooling sets]] prove it.

> [!recipe] Recipe — three ways to prove that a language is regular
> 1. Give a **regular expression** for it.
> 2. Give a **DFA** or an **NFA** for it ($\varepsilon$-transitions allowed).
> 3. Build it from languages already known to be regular with **closure properties** — finitely many operations.
>
> To prove something about *every* regular language, choose an expression $R$ with $L(R) = L$ and induct on $R$, or start from a DFA for $L$ and build an NFA ([[concepts/language-transformations|language transformations]]). To prove that $L$ is *not* regular, give an infinite fooling set, or use closure backwards: if $L\cap R$ is not regular for some regular $R$, then $L$ is not regular.

**Closed under** (with the construction that proves it): complement, $\cup$, $\cap$, $\setminus$ and $\oplus$ ([[concepts/product-construction|product construction]]); concatenation, ${}^*$ and ${}^+$ (expressions, or NFAs glued with $\varepsilon$-edges); reversal (Lemma 4.4); $\textsf{half}(L) = \{w \mid ww\in L\}$ (Lemma 4.5); and many other [[concepts/language-transformations|transformations]]. Full table: [[concepts/closure-properties]].

> [!trap] Classic mistakes
> - A **subset** of a regular language need not be regular: $\{\mathtt{0}^n\mathtt{1}^n \mid n\ge0\}\subseteq(\mathtt{0}+\mathtt{1})^*$.
> - Closure covers **finitely many** operations. Every language is the union of its one-string subsets, so an infinite union of regular languages can be anything.
> - Closure arguments run one way: "$L\cap R$ is regular" or "$L\cup L'$ is regular" says nothing about $L$.
> - Regularity is a property of the **language**, not of how it is written: $\{\mathtt{0}^n\mathtt{1}^n \mid n\le 374\}$ is finite, hence regular.
> - A language has no recursive structure to induct on — induct on an expression for it.

**Example.** $L = \{\mathtt{0}^m\mathtt{1}^n \mid m\ne n\}$ is not regular. If it were, then $\overline{L}\cap\mathtt{0}^*\mathtt{1}^*$ would be regular too, by closure under complement and intersection; but that language is $\{\mathtt{0}^n\mathtt{1}^n \mid n\ge0\}$, which is not regular (Lemma 3.6). In the other direction, the binary numerals of the multiples of 5 written least-significant bit first form a regular language, with no new design needed: they are the reversals of the usual numerals, which the 5-state DFA of [[1-models-of-computation/03-finite-state-machines#31-intuition-a-dfa-is-a-loop-with-constant-memory|§3.1]] accepts, and regular languages are closed under reversal.

**Where it appears.** [[1-models-of-computation/02-regular-languages#23-regular-languages-and-regular-expressions|§2.3]] (definition), [[1-models-of-computation/02-regular-languages#27-proofs-about-regular-languages|§2.7]] (proofs through an expression), [[1-models-of-computation/02-regular-languages#28-not-every-language-is-regular|§2.8]] (counting), [[1-models-of-computation/03-finite-state-machines#37-closure-properties|§3.7]] (closure; the three ways), [[1-models-of-computation/03-finite-state-machines#38-proving-a-language-is-not-regular|§3.8]] (non-regularity), [[1-models-of-computation/04-nondeterministic-automata#44-kleenes-theorem|§4.4]] (Kleene's theorem), [[1-models-of-computation/04-nondeterministic-automata#49-regular-language-transformations|§4.9]] (transformations), [[1-models-of-computation/05-context-free-languages#55-regular-languages-are-context-free|§5.5]] (every regular language is context-free). The hierarchy of classes: [[0-toolkit/03-the-big-picture|the big picture]].

**Practice.** [[practice/topics#structural-induction-on-regular-expressions|Structural induction on regular expressions]] (2 problems) · [[practice/topics#regular-expressions|Regular expressions]] (9 problems) — for example [[practice/02-regular-languages#22-read-these-expressions|2.2 Read these expressions]] (easy), [[practice/02-regular-languages#24-three-regular-expressions|2.4 Three regular expressions]] (medium), [[practice/02-regular-languages#27-two-careful-regular-expressions|2.7 Two careful regular expressions]] (hard).

Related: [[concepts/regular-expressions]] · [[concepts/kleenes-theorem]] · [[concepts/closure-properties]] · [[concepts/fooling-sets]] · [[concepts/language-transformations]] · [[concepts/myhill-nerode-theorem]]
