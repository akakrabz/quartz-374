---
title: "Language transformations"
description: "How to prove that a transformed language is regular whenever L is: start from an arbitrary DFA for L and build an NFA — simulation for {w : f(w) ∈ L}, guessing for {f(w) : w ∈ L} — with the exam template, the rubric and the classic slips."
tags: [concept, regular, midterm-1]
aliases: ["regular language transformation", "language transformation"]
---

> [!definition] Definition — the two kinds of transformed language
> For a function $f$ from strings to strings and a language $L$:
> $$
> \{w \mid f(w)\in L\} \qquad\text{and}\qquad \{f(w) \mid w\in L\}.
> $$
> "Regular languages are closed under the transformation" means the new language is regular for **every** regular $L$. It is proved by a construction that starts from an **arbitrary** DFA $M = (\Sigma,Q,s,A,\delta)$ for $L$.

**Why it works.** The input side gets the most structure — a DFA, one state per prefix — and the output side the most freedom: an NFA with $\varepsilon$-transitions. For $\{w\mid f(w)\in L\}$, the new machine reads $w$ and **simulates $M$ on $f(w)$**, usually deterministically. For $\{f(w)\mid w\in L\}$, it reads the output and **guesses a preimage** $w$ while simulating $M$ on it: nondeterministic choices guess changed symbols, and $\varepsilon$-transitions guess deleted ones. The [[concepts/subset-construction|subset construction]] then turns the NFA into a DFA.

> [!template] Template — language transformation
> Let $M = (\Sigma,Q,s,A,\delta)$ be a DFA that accepts $L$. \
> We construct an NFA $M' = (\Sigma,Q',s',A',\delta')$ with $\varepsilon$-transitions that accepts *[the new language]*. \
> **In English:** $M'$ remembers *[each component of its state, and what it means]*, guesses *[what]*, and accepts when *[…]*. \
> **Formally:** $Q' = $ *[…]*, $s' = $ *[…]*, $A' = $ *[…]*, \
> $\delta'(q',a) = $ *[…]* for every state $q'$ and symbol $a$, and $\delta'(q',\varepsilon) = $ *[…]* ($\varnothing$ if there are none).

> [!trap]
> - Start from an **arbitrary** DFA for $L$, never from a machine for one example language.
> - Keep the directions apart: $\{w\mid f(w)\in L\}$ simulates $M$ on $f(w)$; $\{f(w)\mid w\in L\}$ guesses $w$.
> - Define $\delta'$ for **every** state and symbol, and $\varepsilon$; an unstated case is a missing transition.
> - Swapping the accepting states of an NFA does not complement its language — complement a DFA.
> - Test the edge cases $L = \varnothing$, $\{\varepsilon\}$, $\mathtt{1}^*$ and $\Sigma^*$.

**Example.** Let $\textsf{del0}(w)$ delete every `0` from $w$, so $\textsf{del0}(\mathtt{0110}) = \mathtt{11}$, and let $M$ be a DFA for $L$ over $\{\mathtt{0},\mathtt{1}\}$. Both constructions keep the states, start state and accepting states of $M$.
- $\{w\mid\textsf{del0}(w)\in L\}$: a DFA that **ignores** 0s, with $\delta'(q,\mathtt{0}) = q$ and $\delta'(q,\mathtt{1}) = \delta(q,\mathtt{1})$.
- $\{\textsf{del0}(w)\mid w\in L\}$: an NFA that **guesses** where the 0s were, with $\delta''(q,\varepsilon) = \{\delta(q,\mathtt{0})\}$, $\delta''(q,\mathtt{1}) = \{\delta(q,\mathtt{1})\}$ and $\delta''(q,\mathtt{0}) = \varnothing$.

> [!exam] How a transformation is graded
> 2 points for a formal, complete description of $M'$ built from an arbitrary DFA $M$ (say whether $M'$ is a DFA or an NFA, and whether it has $\varepsilon$-transitions); 2 for an English explanation of its states and accepting states; 6 for correctness — 1 for the states, 1 for the start state, 1 for the accepting states and 3 for the transitions. Midterm-1-style exams ask for two such constructions.

**Where it appears.** [[1-models-of-computation/04-nondeterministic-automata#49-regular-language-transformations|§4.9]] (the method; Lemma 4.4 reversal and Lemma 4.5 $\textsf{half}(L) = \{w\mid ww\in L\}$), [[1-models-of-computation/02-regular-languages#27-proofs-about-regular-languages|§2.7]] (the regular-expression route: reversal by structural recursion), [[1-models-of-computation/04-nondeterministic-automata#43-epsilon-transitions|§4.3]] ($\varepsilon$-transitions), [[1-models-of-computation/03-finite-state-machines#36-the-product-construction|§3.6]] (the product construction, the same idea with two machines).

**Practice.** [[practice/topics#regular-language-transformations|Regular language transformations]] (3 problems) — for example [[practice/04-nondeterministic-automata#48-rotating-the-first-symbol|4.8 Rotating the first symbol]] (hard).

Related: [[concepts/nfa]] · [[concepts/dfa]] · [[concepts/closure-properties]] · [[concepts/subset-construction]] · [[concepts/product-construction]]
