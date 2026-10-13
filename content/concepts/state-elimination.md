---
title: "State elimination"
description: "NFA (or DFA) to regular expression: label the edges with expressions and remove states one at a time, replacing every detour through a state by an expression. The rule, a by-hand recipe, a tiny example, and the exponential blow-up."
tags: [concept, regular, midterm-1]
aliases: ["NFA to regular expression", "DFA to regular expression", "expression automaton", "McNaughton-Yamada algorithm"]
---

> [!definition] Definition — expression automaton and the elimination rule
> An **expression automaton** has a start state $s$ with no incoming edges, a target state $t\ne s$ with no outgoing edges, and a regular expression $R(p\to q)$ on each edge (a missing edge means $\varnothing$). It accepts $w$ if $w = x_1x_2\cdots x_\ell$ for some walk $s = q_0\to q_1\to\cdots\to q_\ell = t$ with each $x_i\in L(R(q_{i-1}\to q_i))$. To **eliminate** a state $q\notin\{s,t\}$, delete it and, for every pair of remaining states $p$, $r$ (including $p = r$), set
> $$
> R'(p\to r) := R(p\to r) + R(p\to q)\,R(q\to q)^*\,R(q\to r).
> $$
> When only $s$ and $t$ are left, $R(s\to t)$ is a regular expression for the language.

**Why it works.** A walk through $q$ arrives from some $p$, loops at $q$ zero or more times, and leaves to some $r$; the new term $R(p\to q)R(q\to q)^*R(q\to r)$ matches exactly those detours. So the language does not change and the automaton loses a state (Lemma 4.3, by induction on the number of states). Any NFA becomes an expression automaton by adding a new start and a new target with $\varepsilon$-edges, so every NFA language is regular — the last arrow of [[concepts/kleenes-theorem|Kleene's theorem]]. The book presents the method as McNaughton and Yamada's (1960), a modern form of Kleene's 1951 argument.

> [!recipe] Recipe — automaton to regular expression by hand
> 1. Add a new start $s$ with an $\varepsilon$-edge to the old start, and a new target $t$ with an $\varepsilon$-edge from every accepting state.
> 2. Merge parallel edges with $+$; a missing edge is $\varnothing$.
> 3. Eliminate the old states one at a time, in any order (states with few edges first keep things small): for every predecessor $p$ and successor $r$ of $q$, add $R(p\to q)R(q\to q)^*R(q\to r)$ to $R(p\to r)$.
> 4. Simplify as you go: $\varnothing$ terms vanish, $\varepsilon R = R$, and $\varnothing^* = \varepsilon$.
> 5. The answer is $R(s\to t)$. Test $\varepsilon$ and a few short strings.

> [!trap] Classic mistakes
> - Forgetting $p = r$: eliminating $q$ also changes the **self-loop** of every state with edges both to and from $q$.
> - Dropping the old direct term $R(p\to r)$.
> - Skipping the new $s$ and $t$ when the old start state has incoming edges or there are several accepting states.
> - Writing $R(q\to q)$ instead of $R(q\to q)^*$; with no loop at $q$ the factor is $\varnothing^* = \varepsilon$.
> - Different orders give different (equivalent) answers, and the expressions grow fast: by roughly a factor of 4 per elimination in the worst case, to length $\Theta(4^n)$ for $n$ states.

**Example.** The 2-state DFA for "an even number of 1s" has states $\textsf{E}$ (start, accepting) and $\textsf{O}$, a loop on `0` at each, and `1`-edges between them. Add $s\xrightarrow{\varepsilon}\textsf{E}$ and $\textsf{E}\xrightarrow{\varepsilon}t$. Eliminating $\textsf{O}$ (its only predecessor and successor is $\textsf{E}$) changes just the loop at $\textsf{E}$: $R'(\textsf{E}\to\textsf{E}) = \mathtt{0}+\mathtt{10}^*\mathtt{1}$. Eliminating $\textsf{E}$ then leaves $R(s\to t) = \varepsilon(\mathtt{0}+\mathtt{10}^*\mathtt{1})^*\varepsilon = (\mathtt{0}+\mathtt{10}^*\mathtt{1})^*$. The other order gives the longer, equivalent $\mathtt{0}^*+\mathtt{0}^*\mathtt{1}(\mathtt{0}+\mathtt{10}^*\mathtt{1})^*\mathtt{10}^*$.

**Where it appears.** [[1-models-of-computation/04-nondeterministic-automata#48-nfa-to-regular-expression-state-elimination|§4.8]] (expression automata, Lemma 4.3, the multiples-of-3 example), [[1-models-of-computation/04-nondeterministic-automata#44-kleenes-theorem|§4.4]] (Kleene's theorem). Arden's rule does the same job algebraically ([[1-models-of-computation/02-regular-languages#22-building-languages|§2.2]]), and the book derives its expression for the binary multiples of 3 ([[1-models-of-computation/02-regular-languages#23-regular-languages-and-regular-expressions|§2.3]]) by eliminating the states of the remainder-mod-3 DFA.

**Practice.** [[practice/topics#conversions-subset-construction-thompson-state-elimination|Conversions: subset construction, Thompson, state elimination]] (4 problems) — for example [[practice/04-nondeterministic-automata#41-six-quick-nfa-facts|4.1 Six quick NFA facts]] (easy), [[practice/04-nondeterministic-automata#45-subset-construction-by-hand|4.5 Subset construction by hand]] (medium).

Related: [[concepts/kleenes-theorem]] · [[concepts/regular-expressions]] · [[concepts/nfa]] · [[concepts/dfa]] · [[concepts/thompsons-algorithm]] · [[concepts/product-construction]]
