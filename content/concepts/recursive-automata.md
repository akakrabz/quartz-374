---
title: "Recursive automata"
description: "NFAs that can call each other, and themselves, with a stack of return states: the machine model for context-free languages, and the two conversions between recursive automata and grammars (Lemmas 5.5 and 5.6)."
tags: [concept, context-free, midterm-1]
aliases: ["recursive automaton", "recursive state machine"]
---

> [!definition] Definition — recursive automaton
> A **recursive automaton** has an input alphabet $\Sigma$, a finite set $N$ of **module names** disjoint from $\Sigma$ with a main name $S$, and for each $A\in N$ an NFA **module** $M_A$ over $\Sigma\cup N$ with start state $s_A$ and a single accepting state $t_A$. A configuration is (remaining input, current state, stack of states). Besides reading symbols and following $\varepsilon$-edges, the automaton can
> - **call** $A$ along an edge $q\xrightarrow{A}q'$: push $q'$ and jump to $s_A$, reading nothing;
> - **return** from $t_A$: pop a state and continue there.
>
> It accepts $w$ if it can go from ($w$, $s_S$, empty stack) to ($\varepsilon$, $t_S$, empty stack).

**Where it comes from.** It is a grammar drawn as flowcharts: an edge labeled $A$ means "read some string that $M_A$ accepts here", exactly like a nonterminal on a right side, and the stack remembers where to resume. An NFA is the special case with one module and no calls; the unbounded stack is what lets it match $\mathtt{0}^n$ with $\mathtt{1}^n$. (Other textbooks use the equivalent pushdown automata.)

> [!key] Lemmas 5.5 and 5.6
> A language is context-free if and only if some recursive automaton accepts it.
> - **Grammar → automaton:** one module per nonterminal $A$, with a path from $s_A$ to $t_A$ for each rule $A\to\omega$ that reads the terminals of $\omega$ and calls its nonterminals, in order.
> - **Automaton → grammar:** one nonterminal $[q]$ per state, generating the strings that lead from $q$ to the accepting state of its module: $[q]\to a[p]$ for $p\in\delta(q,a)$, $[q]\to[p]$ for $p\in\delta(q,\varepsilon)$, $[q]\to[s_B][p]$ for $p\in\delta(q,B)$, and $[t_A]\to\varepsilon$; the start symbol is $[s_S]$.

> [!trap]
> - A call reads no input; the called module does. Acceptance needs the whole input read **and** an empty stack, in $t_S$.
> - The stack holds return *states*, not input symbols, and has no fixed bound; with a bounded stack the machine is just an NFA.
> - Each module has exactly one accepting state.
> - One stack gives exactly the context-free languages; two stacks already simulate a Turing machine.

**Example.** Balanced parentheses, $S\to\mathtt{(}S\mathtt{)}S\mid\varepsilon$, need one module with states $s, a, b, c, t$: a path $s\xrightarrow{\mathtt{(}}a\xrightarrow{S}b\xrightarrow{\mathtt{)}}c\xrightarrow{S}t$ and an edge $s\xrightarrow{\varepsilon}t$. On `()` it reads `(`, calls $S$ (pushing $b$), returns at once along $s\xrightarrow{\varepsilon}t$, reads `)`, calls $S$ again (pushing $t$), returns, and stops in $t$ with an empty stack: accepted. Lemma 5.6 turns the module back into a grammar:
$$
[s]\to\mathtt{(}[a]\mid[t] \qquad [a]\to[s][b] \qquad [b]\to\mathtt{)}[c] \qquad [c]\to[s][t] \qquad [t]\to\varepsilon
$$

**Where it appears.** [[1-models-of-computation/05-context-free-languages#57-recursive-automata|§5.7]] (definition, Lemmas 5.5–5.6, and a two-module automaton for ${\{\mathtt{0}^m\mathtt{1}^n \mid m\ne n\}}$), [[1-models-of-computation/04-nondeterministic-automata#41-nondeterministic-state-machines|§4.1]] (NFAs, the building blocks), [[1-models-of-computation/05-context-free-languages#55-regular-languages-are-context-free|§5.5]] (regular languages are context-free), [[1-models-of-computation/08-universal-models#82-two-stack-machines|§8.2]] (two stacks are as powerful as a Turing machine).

Related: [[concepts/context-free-grammars]] · [[concepts/nfa]] · [[concepts/chomsky-normal-form]] · [[concepts/turing-machines]]
