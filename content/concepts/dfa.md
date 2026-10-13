---
title: "DFA (deterministic finite automaton)"
description: "A one-pass, constant-memory algorithm: the tuple (Σ, Q, s, A, δ) with a total transition function, the extended transition function δ*, how to design a DFA with mnemonic state names, and what loses points."
tags: [concept, regular, midterm-1]
aliases: ["DFA", "DFAs", "deterministic finite automaton", "deterministic finite-state automaton", "finite-state machine"]
---

> [!definition] Definition — DFA
> A **DFA** is a tuple $M = (\Sigma, Q, s, A, \delta)$: a finite alphabet $\Sigma$, a finite set $Q$ of **states**, a **start state** $s\in Q$, a set $A\subseteq Q$ of **accepting states**, and a **total** transition function $\delta\colon Q\times\Sigma\to Q$. The extended transition function follows the recursive definition of strings:
> $$
> \delta^*(q,\varepsilon) := q,\qquad \delta^*(q,ax) := \delta^*\big(\delta(q,a),\,x\big).
> $$
> $M$ **accepts** $w$ iff $\delta^*(s,w)\in A$, and its language is $L(M) := \{w\in\Sigma^* \mid \delta^*(s,w)\in A\}$.

**Why it works.** A DFA is an algorithm that reads its input once, left to right, and remembers only its current state: the states are the possible values of its memory, $\delta$ is one iteration of the loop, and $A$ is the final test. As a graph, every state has exactly one outgoing edge per symbol, so every string traces exactly one walk from $s$. Two identities, each a short [[concepts/induction-on-strings|string induction]], do most of the work in proofs: $\delta^*(q,xy) = \delta^*(\delta^*(q,x),y)$ and $\delta^*(q,xa) = \delta(\delta^*(q,x),a)$. DFAs accept exactly the [[concepts/regular-languages|regular languages]].

> [!recipe] Recipe — designing a DFA (the exam problem)
> 1. Write a one-pass loop whose variables take a fixed, finite set of values.
> 2. **States** = combinations of values; **start** = the initial values; $\delta$ = one iteration; $A$ = the final test.
> 3. **Name each state after what it remembers** ("last symbol was `0`", "seen `11`", "remainder 3").
> 4. **Complete $\delta$:** one edge per state and symbol. Omitting the dump state is fine only if you say so.
> 5. **Test** $\varepsilon$, every short string, and one long string.

> [!trap] Classic mistakes
> - Missing transitions without a sentence about a dump state: an incomplete DFA. (An NFA where a DFA was asked for earns half credit.)
> - No start arrow, no double circles, or state names that say nothing — the names are graded.
> - "Remember how many 0s" is not a finite set of states, unless you count mod $k$ or up to a cap.
> - Forgetting $\varepsilon$: the start state is accepting exactly when $\varepsilon\in L$.
> - Swapping accepting and non-accepting states complements a DFA, but not an [[concepts/nfa|NFA]].

**Example — strings that end in `01`.** Remember the longest suffix of the input so far that is a prefix of `01`:

| state (what it remembers) | on `0` | on `1` |
|---|---|---|
| $\varepsilon$ — no progress (start) | `0` | $\varepsilon$ |
| `0` — the input ends in `0` | `0` | `01` |
| `01` — the input ends in `01` (accepting) | `0` | $\varepsilon$ |

On `1001` it visits $\varepsilon,\varepsilon,\mathtt{0},\mathtt{0},\mathtt{01}$ and accepts. No DFA for this language has fewer states: $\{\varepsilon,\mathtt{0},\mathtt{01}\}$ is a [[concepts/fooling-sets|fooling set]] — the suffix `1` distinguishes $\varepsilon$ from `0`, and the suffix $\varepsilon$ distinguishes `01` from each of the other two.

**Where it appears.** [[1-models-of-computation/03-finite-state-machines#31-intuition-a-dfa-is-a-loop-with-constant-memory|§3.1]] (the multiples-of-5 machine), [[1-models-of-computation/03-finite-state-machines#32-formal-definitions|§3.2]] (definition), [[1-models-of-computation/03-finite-state-machines#33-proving-a-dfa-correct|§3.3]] (correctness proofs), [[1-models-of-computation/03-finite-state-machines#35-designing-dfas-dfas-are-algorithms|§3.5]] (design), [[1-models-of-computation/03-finite-state-machines#36-the-product-construction|§3.6]] (products), [[1-models-of-computation/03-finite-state-machines#310-minimal-automata-moores-algorithm|§3.10]] (minimization). Every DFA is an NFA ([[1-models-of-computation/04-nondeterministic-automata#41-nondeterministic-state-machines|§4.1]]), and language transformations start from a DFA ([[1-models-of-computation/04-nondeterministic-automata#49-regular-language-transformations|§4.9]]). Grading: [[0-toolkit/06-how-exams-are-graded|how exams are graded]].

**Practice.** [[practice/topics#designing-and-proving-dfas|Designing and proving DFAs]] (7 problems) — for example [[practice/03-finite-state-machines#32-a-bounded-counter|3.2 A bounded counter]] (easy), [[practice/03-finite-state-machines#35-read-a-dfa-then-prove-it|3.5 Read a DFA, then prove it]] (medium), [[practice/03-finite-state-machines#38-no-00-after-an-11|3.8 No 00 after an 11]] (hard).

Related: [[concepts/nfa]] · [[concepts/product-construction]] · [[concepts/fooling-sets]] · [[concepts/dfa-minimization]] · [[concepts/myhill-nerode-theorem]] · [[concepts/kleenes-theorem]]
