---
title: "Subset construction"
description: "NFA to DFA: the DFA's states are sets of NFA states. The book's version with ε-transitions, the incremental table you build by hand, and why the result can have exponentially many states."
tags: [concept, regular, midterm-1]
aliases: ["powerset construction", "NFA to DFA", "determinization"]
---

> [!definition] Definition — subset construction (with $\varepsilon$-transitions)
> For an NFA $M = (\Sigma, Q, s, A, \delta)$, possibly with $\varepsilon$-transitions, the DFA $M' = (\Sigma, Q', s', A', \delta')$ has
> $$
> Q' := 2^Q,\qquad s' := \{s\},\qquad A' := \{S\subseteq Q \mid \varepsilon\text{-reach}(S)\cap A\ne\varnothing\},
> $$
> $$
> \delta'(S,a) := \bigcup_{p\in S}\ \bigcup_{r\in\varepsilon\text{-reach}(p)}\delta(r,a).
> $$
> Without $\varepsilon$-transitions this is just $A' = \{S \mid S\cap A\ne\varnothing\}$ and $\delta'(S,a) = \bigcup_{p\in S}\delta(p,a)$.

**Why it works.** A DFA cannot guess, but it can remember every state the [[concepts/nfa|NFA]] might be in: all the parallel threads at once. By induction on $w$, $\varepsilon\text{-reach}\big((\delta')^*(\{s\},w)\big)$ is exactly the set of states the NFA can be in after reading $w$, so $M'$ accepts $w$ iff some thread of $M$ does. A set of NFA states is a finite amount of memory — one of $2^{\lvert Q\rvert}$ possibilities — so NFAs accept only regular languages.

> [!recipe] Recipe — the incremental subset construction (by hand)
> Build only the subsets that are reachable, breadth-first from $\{s\}$, in a table with one row per DFA state and the columns $S$, $\varepsilon\text{-reach}(S)$, "accepting?", and $\delta'(S,a)$ for each symbol.
> 1. Start with the row $\{s\}$.
> 2. In each row compute $\varepsilon\text{-reach}(S)$; the row is accepting if that set meets $A$; for each symbol $a$, collect every $\delta(r,a)$ with $r\in\varepsilon\text{-reach}(S)$.
> 3. A subset that appears in a transition column for the first time gets a row of its own — $\varnothing$ included (it is a dump state).
> 4. Stop when no new subset appears. The rows are the DFA's states.

> [!key] The worst case is exponential — and sometimes necessary
> $M'$ has at most $2^{\lvert Q\rvert}$ states, and exponentially many can be needed. "The $k$th symbol from the end is `1`" has an NFA with $k+1$ states (loop at the start, guess the position, then read $k-1$ more symbols), but every DFA for it has at least $2^k$ states: the $2^k$ strings of length $k$ form a [[concepts/fooling-sets|fooling set]], because if $x\ne y$ first differ at position $i$, the suffix $\mathtt{0}^{i-1}$ makes that position the $k$th from the end.

> [!trap] Classic mistakes
> - Taking the $\varepsilon$-reach only at the start: every row needs it, both for the moves and for the acceptance test.
> - Accepting a subset only if **all** its states accept: one accepting state in its $\varepsilon$-reach is enough.
> - Dropping $\varnothing$: if it is reachable, it is a state, with a loop on every symbol.
> - Listing all $2^{\lvert Q\rvert}$ subsets: build the reachable ones only. The result is correct but often not minimal ([[concepts/dfa-minimization|minimize]] it if asked).
> - To complement an NFA, determinize it first, then swap the accepting states.

**Example (with an $\varepsilon$-transition).** The NFA with states $p$ (start, loop on `0`) and $q$ (accepting, loop on `1`) and an $\varepsilon$-transition from $p$ to $q$ accepts $\mathtt{0}^*\mathtt{1}^*$. The construction finds three DFA states:

| $S$ | $\varepsilon\text{-reach}(S)$ | accepting? | on `0` | on `1` |
|---|---|---|---|---|
| $\{p\}$ (start) | $\{p,q\}$ | yes | $\{p\}$ | $\{q\}$ |
| $\{q\}$ | $\{q\}$ | yes | $\varnothing$ | $\{q\}$ |
| $\varnothing$ | $\varnothing$ | no | $\varnothing$ | $\varnothing$ |

On the "ends in `01`" NFA of the [[concepts/nfa|NFA page]] it finds the subsets $\{s\}$, $\{s,a\}$, $\{s,b\}$ — 3 of the $2^3 = 8$ — which form the 3-state [[concepts/dfa|DFA]] for that language. On [[concepts/thompsons-algorithm|Thompson's]] 14-state NFA for $(\mathtt{0}+\mathtt{10}^*\mathtt{1})^*$ it builds 5 states, not $2^{14} = 16384$.

**Where it appears.** [[1-models-of-computation/04-nondeterministic-automata#45-nfa-to-dfa-the-subset-construction|§4.5]] (definition and the incremental version), [[1-models-of-computation/04-nondeterministic-automata#43-epsilon-transitions|§4.3]] ($\varepsilon$-reach), [[1-models-of-computation/04-nondeterministic-automata#46-regular-expression-to-nfa-thompsons-algorithm|§4.6]] and [[1-models-of-computation/04-nondeterministic-automata#47-another-example|§4.7]] (applied to Thompson's NFAs), [[1-models-of-computation/04-nondeterministic-automata#44-kleenes-theorem|§4.4]] (its arrow in Kleene's theorem). The same idea — simulate every choice — gives deterministic simulations of nondeterministic Turing machines ([[1-models-of-computation/09-nondeterministic-turing-machines#94-deterministic-simulation-via-dovetailing|§9.4]]).

**Practice.** [[practice/topics#conversions-subset-construction-thompson-state-elimination|Conversions: subset construction, Thompson, state elimination]] (4 problems) — for example [[practice/04-nondeterministic-automata#41-six-quick-nfa-facts|4.1 Six quick NFA facts]] (easy), [[practice/04-nondeterministic-automata#45-subset-construction-by-hand|4.5 Subset construction by hand]] (medium).

Related: [[concepts/nfa]] · [[concepts/dfa]] · [[concepts/kleenes-theorem]] · [[concepts/thompsons-algorithm]] · [[concepts/fooling-sets]] · [[concepts/dfa-minimization]]
