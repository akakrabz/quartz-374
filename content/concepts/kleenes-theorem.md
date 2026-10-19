---
title: "Kleene's theorem"
description: "Regular expressions, DFAs and NFAs (with or without ε-transitions) describe exactly the same languages, the regular languages. The cycle of conversions, the construction behind each arrow, and how big each one gets."
tags: [concept, regular, midterm-1]
aliases: ["Kleene theorem", "equivalence of regular expressions and automata"]
---

> [!key] Theorem 4.1 (Kleene)
> A language can be described by a regular expression if and only if it is accepted by a DFA. With the constructions below, regular expressions, DFAs, NFAs and NFAs with $\varepsilon$-transitions all describe exactly the same class of languages: the [[concepts/regular-languages|regular languages]]. (Stated as Theorem 3.3 in Chapter 3, proved in Chapter 4.)

**The cycle of conversions.** Each arrow is an algorithm, so from any one description you can reach all the others:
$$
\text{expression}\ \xrightarrow{\ \text{Thompson}\ }\ \varepsilon\text{-NFA}\ \xrightarrow{\ \text{subsets}\ }\ \text{DFA}\ \xrightarrow{\ \text{trivial}\ }\ \text{NFA}\ \xrightarrow{\ \text{elimination}\ }\ \text{expression}
$$

| arrow | construction | size of the result |
|---|---|---|
| expression → $\varepsilon$-NFA | [[concepts/thompsons-algorithm\|Thompson's algorithm]] (Lemma 4.2) | at most $2\times$ the length of the expression |
| $\varepsilon$-NFA → NFA (optional) | $\varepsilon$-removal | the same states |
| NFA → DFA | [[concepts/subset-construction\|subset construction]] | up to $2^n$ states, sometimes necessary |
| DFA → NFA | trivial: $\delta'(q,a) := \{\delta(q,a)\}$ | the same states |
| NFA → expression | [[concepts/state-elimination\|state elimination]] (Lemma 4.3) | length up to $\Theta(4^n)$ |

**Why it matters.** Each description is good at different things, and the theorem lets you switch freely. Expressions handle union, concatenation, star and reversal; DFAs handle complement and intersection ([[concepts/product-construction|products]]) and lower bounds ([[concepts/fooling-sets|fooling sets]]); NFAs handle guessing and [[concepts/language-transformations|transformations]]. Together they give Corollaries 3.4 and 3.5: regular languages are closed under every boolean operation, concatenation and star.

> [!recipe] Recipe — using the theorem
> - To prove that $L$ is regular, give **any one** description — whichever is easiest.
> - To prove a closure property, transform the description that makes it easy: a DFA for $L$ into an NFA for $f(L)$, or an expression by structural recursion.
> - For a "convert" question, follow the construction literally and show the work: the gadgets, the subset table, each elimination.

> [!trap] Classic mistakes
> - The conversions preserve the **language**, not the size: subsets can cost $2^n$ states, elimination $\Theta(4^n)$ symbols.
> - The theorem is about these models only. Regexen with back-references, grammars and Turing machines describe languages that are not regular.
> - It does not say that every language is regular; most languages are not.
> - No conversion is needed to treat a DFA as an NFA, and state elimination works on DFAs directly.

**Example — one full turn (the book's, plus the last arrow).** Start with $(\mathtt{0}+\mathtt{10}^*\mathtt{1})^*$, the strings with an even number of 1s. Thompson's algorithm gives a 14-state NFA. The incremental subset construction turns it into a 5-state DFA (instead of up to $2^{14} = 16384$ states). Minimization merges that DFA's three accepting states and its two rejecting states, leaving the 2-state parity DFA. State elimination on that DFA, removing the rejecting state first, gives back exactly $(\mathtt{0}+\mathtt{10}^*\mathtt{1})^*$. Section 4.7 repeats the exercise for $(\mathtt{0}+\mathtt{1})^*(\mathtt{00}+\mathtt{11})(\mathtt{0}+\mathtt{1})^*$: a 26-state Thompson NFA (the book's figure and table; its text says 18, the count you get by drawing each $\mathtt{0}+\mathtt{1}$ as one two-state gadget), a 9-state DFA, and a minimal DFA with 4 states.

**Where it appears.** [[1-models-of-computation/03-finite-state-machines#37-closure-properties|§3.7]] (stated as Theorem 3.3; its corollaries), [[1-models-of-computation/04-nondeterministic-automata#44-kleenes-theorem|§4.4]] (Theorem 4.1 and the plan of the proof), then the arrows: [[1-models-of-computation/04-nondeterministic-automata#43-epsilon-transitions|§4.3]] ($\varepsilon$-removal), [[1-models-of-computation/04-nondeterministic-automata#45-nfa-to-dfa-the-subset-construction|§4.5]], [[1-models-of-computation/04-nondeterministic-automata#46-regular-expression-to-nfa-thompsons-algorithm|§4.6]], [[1-models-of-computation/04-nondeterministic-automata#47-another-example|§4.7]], [[1-models-of-computation/04-nondeterministic-automata#48-nfa-to-regular-expression-state-elimination|§4.8]]. The context-free analogue: grammars and [[concepts/recursive-automata|recursive automata]] describe the same languages ([[1-models-of-computation/05-context-free-languages#57-recursive-automata|§5.7]]). All the classes at once: [[0-toolkit/03-the-big-picture|the big picture]].

**Practice.** [[practice/topics#conversions-subset-construction-thompson-state-elimination|Conversions: subset construction, Thompson, state elimination]] (4 problems) — for example [[practice/04-nondeterministic-automata#41-six-quick-nfa-facts|4.1 Six quick NFA facts]] (easy), [[practice/04-nondeterministic-automata#45-subset-construction-by-hand|4.5 Subset construction by hand]] (medium).

Related: [[concepts/regular-languages]] · [[concepts/regular-expressions]] · [[concepts/dfa]] · [[concepts/nfa]] · [[concepts/thompsons-algorithm]] · [[concepts/subset-construction]] · [[concepts/state-elimination]] · [[concepts/closure-properties]]
