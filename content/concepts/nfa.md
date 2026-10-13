---
title: "NFA (nondeterministic finite automaton)"
description: "A finite automaton that may have several transitions, none, or ε-transitions out of a state, and accepts if some sequence of choices ends in an accepting state: the definition with ε-reach, three intuitions, ε-removal, design tips and traps."
tags: [concept, regular, midterm-1]
aliases: ["NFA", "NFAs", "nondeterministic finite automaton", "nondeterministic finite-state automaton", "epsilon-transition", "epsilon-reach"]
---

> [!definition] Definition — NFA (with $\varepsilon$-transitions)
> An **NFA** $M = (\Sigma, Q, s, A, \delta)$ is like a [[concepts/dfa|DFA]], except that $\delta\colon Q\times(\Sigma\cup\{\varepsilon\})\to 2^Q$ returns a **set** of states, possibly empty. The **$\varepsilon$-reach** of $q$ is the set of states reachable from $q$ by zero or more $\varepsilon$-transitions. $M$ **accepts** $w$ iff some walk from $s$ to an accepting state spells $w$; formally, iff $\delta^*(s,w)\cap A\ne\varnothing$, where
> $$
> \delta^*(q,\varepsilon) := \varepsilon\text{-reach}(q),\qquad \delta^*(q,ax) := \bigcup_{r\in\varepsilon\text{-reach}(q)}\ \bigcup_{p\in\delta(r,a)}\delta^*(p,x).
> $$

**Intuition.** Three equivalent pictures: the machine **guesses**, always making a choice that leads to acceptance if one exists; it runs every choice as a **parallel thread**, a thread dying when it has no move, and accepts if any thread ends in $A$; or a prover supplies the choices and the machine only **verifies** them. Running an NFA by hand means tracking the *set* of current states — which is exactly the [[concepts/subset-construction|subset construction]], so NFAs accept only regular languages. Their value is convenience: "guess where the pattern starts" and "glue two machines together with $\varepsilon$-edges" each take one line.

**Removing $\varepsilon$-transitions** needs no new states: keep $Q$ and $s$, make $q$ accepting iff $\varepsilon\text{-reach}(q)$ meets $A$, and set $\delta'(q,a) := \bigcup_{r\in\varepsilon\text{-reach}(q)}\delta(r,a)$.

> [!recipe] Recipe — designing with nondeterminism
> 1. Decide **what to guess**: where a pattern starts, which of several cases holds, a symbol you never get to read.
> 2. Let **wrong guesses die** — only one thread has to accept.
> 3. Use **$\varepsilon$-transitions** to make a guess without reading anything, or to glue machines together.
> 4. Give $\delta(q,a)$ and $\delta(q,\varepsilon)$ as sets for every state, and say which transitions are $\varepsilon$-transitions.
> 5. Check both directions: every string in the language has an accepting walk, and no other string does.

> [!trap] Classic mistakes
> - **Swapping accepting states does not complement an NFA** (example below). Determinize first.
> - An NFA accepts if *some* walk accepts, not *all*; a string on which every thread dies is rejected.
> - $\varepsilon$-moves count before the first symbol and after the last one: always take the $\varepsilon$-reach.
> - Where a DFA is asked for, an NFA earns half credit.

**Example — strings that end in `01`.** States $s$, $a$, $b$: $s$ loops on `0` and `1`, $s\xrightarrow{\mathtt{0}}a$, $a\xrightarrow{\mathtt{1}}b$, and $A = \{b\}$. The machine guesses which `0` is the second-to-last symbol. On `1001` the set of current states is $\{s\},\{s\},\{s,a\},\{s,a\},\{s,b\}$; the last set meets $A$, so it accepts. Making $s$ and $a$ accepting instead does **not** give the complement: that machine accepts `01`, through the thread that stays in $s$.

**Where it appears.** [[1-models-of-computation/04-nondeterministic-automata#41-nondeterministic-state-machines|§4.1]] (definition), [[1-models-of-computation/04-nondeterministic-automata#42-intuition|§4.2]] (three intuitions), [[1-models-of-computation/04-nondeterministic-automata#43-epsilon-transitions|§4.3]] ($\varepsilon$-transitions and their removal), [[1-models-of-computation/04-nondeterministic-automata#45-nfa-to-dfa-the-subset-construction|§4.5]] (NFA to DFA), [[1-models-of-computation/04-nondeterministic-automata#46-regular-expression-to-nfa-thompsons-algorithm|§4.6]] (expression to NFA), [[1-models-of-computation/04-nondeterministic-automata#49-regular-language-transformations|§4.9]] (transformations: from a DFA to an NFA). Nondeterminism returns for Turing machines: [[concepts/nondeterministic-turing-machines]].

**Practice.** [[practice/topics#nfas-and-epsilon-transitions|NFAs and epsilon-transitions]] (8 problems) — for example [[practice/04-nondeterministic-automata#41-six-quick-nfa-facts|4.1 Six quick NFA facts]] (easy), [[practice/04-nondeterministic-automata#45-subset-construction-by-hand|4.5 Subset construction by hand]] (medium), [[practice/04-nondeterministic-automata#48-rotating-the-first-symbol|4.8 Rotating the first symbol]] (hard).

Related: [[concepts/dfa]] · [[concepts/subset-construction]] · [[concepts/thompsons-algorithm]] · [[concepts/kleenes-theorem]] · [[concepts/language-transformations]]
