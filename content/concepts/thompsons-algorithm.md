---
title: "Thompson's algorithm"
description: "Regular expression to NFA by structural recursion: two-state gadgets for ∅, ε and single symbols, glued with ε-transitions for union, concatenation and star. Every gadget has one start and one accepting state, and the NFA has linear size."
tags: [concept, regular, midterm-1]
aliases: ["Thompson's construction", "regular expression to NFA"]
---

> [!definition] Definition — Thompson's algorithm (Lemma 4.2)
> By recursion on the expression tree, build an NFA with **exactly one accepting state $t$, different from its start state $s$**:
> - $\varnothing$: states $s$ and $t$, no transitions. $\varepsilon$: $s\xrightarrow{\varepsilon}t$. A symbol $a$: $s\xrightarrow{a}t$. (A longer string is a concatenation of symbols.)
> - $ST$, in **series**: add $t_S\xrightarrow{\varepsilon}s_T$; the start is $s_S$ and the accepting state is $t_T$.
> - $S+T$, in **parallel**: new $s$ and $t$, with $s\xrightarrow{\varepsilon}s_S$, $s\xrightarrow{\varepsilon}s_T$, $t_S\xrightarrow{\varepsilon}t$ and $t_T\xrightarrow{\varepsilon}t$.
> - $S^*$: new $s$ and $t$, with $s\xrightarrow{\varepsilon}s_S$, $t_S\xrightarrow{\varepsilon}s_S$ (another copy), $t_S\xrightarrow{\varepsilon}t$ (stop), and $s\xrightarrow{\varepsilon}t$ (zero copies).
>
> The book closes the loop from the new $t$ back to the new $s$ instead of from $t_S$ to $s_S$ ([[1-models-of-computation/04-nondeterministic-automata#46-regular-expression-to-nfa-thompsons-algorithm|§4.6]]). Both versions are correct and have the same number of states and edges; only some $\varepsilon$-reaches differ.

**Why it works.** Structural induction on the expression: in the finished NFA, every gadget is entered only at its start state and left only from its accepting state, so a walk through a gadget spells exactly a string of that gadget's language. The single accepting state is what makes the gluing easy. The algorithm adds 2 states for each $\varnothing$, $\varepsilon$ or symbol leaf and for each $+$ and $^*$, and none for a concatenation — at most twice the length of the expression. The NFAs are full of redundant states and $\varepsilon$-transitions; that is fine, because the next step is $\varepsilon$-removal or the [[concepts/subset-construction|subset construction]].

> [!recipe] Recipe — Thompson's algorithm by hand
> 1. Parse the expression into its tree: $^*$ binds before concatenation, which binds before $+$.
> 2. Build bottom-up: a two-state gadget for each leaf, then glue at each internal node exactly as above.
> 3. Keep every sub-NFA's start and accepting state labeled; new edges touch only those two states.
> 4. Count the states as a check: $2\times(\text{leaves} + \text{unions} + \text{stars})$.

> [!trap] Classic mistakes
> - Dropping the bypass $s\xrightarrow{\varepsilon}t$ of the star gadget: then the NFA for $S^*$ rejects $\varepsilon$ unless $\varepsilon\in L(S)$.
> - In $ST$, the accepting state of $S$ stops being accepting; only $t_T$ accepts.
> - **The "shortcut" star** — no new states, just make the old start state accepting and add an $\varepsilon$-edge back to it from the accepting state — fails when the start state has incoming edges. On the two-state NFA for $\mathtt{0}^*\mathtt{1}$ (the start loops on `0`; a `1` leads to the accepting state) it accepts `0`, which is not in $(\mathtt{0}^*\mathtt{1})^*$.
> - Expecting a small NFA: Thompson's output is correct, not compact.

**Example.** For $\mathtt{0}^*\mathtt{1}$: the star gadget around the `0` gadget has 4 states, the `1` gadget 2 more, and the concatenation adds only an $\varepsilon$-edge — 6 states, 5 $\varepsilon$-transitions and 2 symbol transitions. The subset construction turns it into a 4-state DFA (one of them the dump state $\varnothing$), and minimization into 3 states. For the book's $(\mathtt{0}+\mathtt{10}^*\mathtt{1})^*$ the count is $2\times(4+1+2) = 14$ states, the number in §4.6.

**Where it appears.** [[1-models-of-computation/04-nondeterministic-automata#46-regular-expression-to-nfa-thompsons-algorithm|§4.6]] (Lemma 4.2 and the 14-state example), [[1-models-of-computation/04-nondeterministic-automata#47-another-example|§4.7]] (a second example), [[1-models-of-computation/04-nondeterministic-automata#44-kleenes-theorem|§4.4]] (its arrow in Kleene's theorem), [[1-models-of-computation/04-nondeterministic-automata#43-epsilon-transitions|§4.3]] (removing the $\varepsilon$-transitions afterwards). The same structural recursion turns an expression into a context-free grammar ([[1-models-of-computation/05-context-free-languages#55-regular-languages-are-context-free|§5.5]]).

**Practice.** [[practice/topics#conversions-subset-construction-thompson-state-elimination|Conversions: subset construction, Thompson, state elimination]] (4 problems) — for example [[practice/04-nondeterministic-automata#41-six-quick-nfa-facts|4.1 Six quick NFA facts]] (easy), [[practice/04-nondeterministic-automata#45-subset-construction-by-hand|4.5 Subset construction by hand]] (medium).

Related: [[concepts/regular-expressions]] · [[concepts/nfa]] · [[concepts/subset-construction]] · [[concepts/kleenes-theorem]] · [[concepts/state-elimination]]
