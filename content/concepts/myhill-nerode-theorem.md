---
title: "Myhill–Nerode theorem"
description: "The minimum number of states of a DFA for L equals the size of the largest fooling set for L and the number of classes of the equivalence relation ≡_L — which is why fooling-set proofs always exist and why the minimal DFA is unique."
tags: [concept, regular, midterm-1]
aliases: ["Myhill-Nerode", "Nerode equivalence", "equivalence classes of a language"]
---

> [!definition] Definition — the relation $\equiv_L$
> For a language $L$, write $x\equiv_L y$ if **no** suffix distinguishes $x$ and $y$: $xz\in L\iff yz\in L$ for every string $z$. This is an equivalence relation; its classes $[x]$ group the strings that have the same possible futures.

> [!key] The Myhill–Nerode theorem
> For every language $L$, these three numbers are equal (possibly all infinite):
> 1. the minimum number of states of a DFA for $L$;
> 2. the maximum size of a [[concepts/fooling-sets|fooling set]] for $L$;
> 3. the number of equivalence classes of $\equiv_L$.
>
> So **$L$ is regular if and only if $\equiv_L$ has finitely many classes**, if and only if every fooling set for $L$ is finite.

**Why it works.** (1) ≥ (2): two strings of a fooling set cannot share a state. (2) = (3): a fooling set is exactly a set with at most one string from each class. (1) ≤ (3): the classes themselves are the states of a DFA, with start state $[\varepsilon]$, accepting states $\{[w] \mid w\in L\}$ and $\delta([w],a) = [wa]$ — well defined because $x\equiv_L y$ implies $xa\equiv_L ya$.

**What it justifies.** *Fooling sets are complete:* a non-regular language has infinitely many classes, and one string from each is an infinite fooling set, so a non-regularity proof by fooling set always exists. *Minimization is canonical:* in a DFA without unreachable states, two states are equivalent exactly when the strings reaching them lie in the same class, so merging equivalent states ([[concepts/dfa-minimization|Moore's algorithm]]) yields the class DFA. The minimal DFA is unique up to renaming its states.

> [!recipe] Recipe — the exact number of states
> 1. Guess the classes: what must an algorithm for $L$ remember? Pick one representative string per class.
> 2. **Lower bound:** show the representatives are pairwise distinguishable — a fooling set.
> 3. **Upper bound:** give a DFA with one state per class.
>
> Either bound alone proves nothing exact.

> [!trap]
> - The count includes the dump state: $\{\mathtt{0}\}$ over $\{\mathtt{0},\mathtt{1}\}$ has three classes, $[\varepsilon]$, $[\mathtt{0}]$ and $[\mathtt{1}]$ (every string that is not a prefix of `0`), so its minimal DFA has three states.
> - Classes are sets of *strings*; a non-minimal DFA may split one class over several states.
> - The theorem is about DFAs; an NFA can be exponentially smaller (example below).

**Example.** Let $L_3$ be the binary strings whose third symbol from the end is `1`. Pad every string on the left with 0s to length 3; then $x\equiv_{L_3} y$ exactly when $x$ and $y$ end in the same three padded symbols, so there are $2^3 = 8$ classes. If two windows $u\ne v$ first differ in position $k$, the suffix $z = \mathtt{0}^{k-1}$ moves that position to third from the end, so exactly one of $uz, vz$ is in $L_3$. The minimal DFA therefore has 8 states — but an NFA needs only 4: loop at the start, guess the `1`, then read exactly two more symbols.

**Where it appears.** [[1-models-of-computation/03-finite-state-machines#39-the-myhillnerode-theorem|§3.9]] (statement and proof), [[1-models-of-computation/03-finite-state-machines#38-proving-a-language-is-not-regular|§3.8]] (fooling sets), [[1-models-of-computation/03-finite-state-machines#310-minimal-automata-moores-algorithm|§3.10]] (minimal automata), [[1-models-of-computation/04-nondeterministic-automata#45-nfa-to-dfa-the-subset-construction|§4.5]] (the subset construction, whose output can be exponentially larger).

**Practice.** [[practice/topics#myhillnerode-and-minimal-dfas|Myhill–Nerode and minimal DFAs]] (2 problems) — for example [[practice/03-finite-state-machines#33-prefixes-of-a-pattern|3.3 Prefixes of a pattern]] (easy), [[practice/03-finite-state-machines#310-shrink-it-then-prove-it-minimal|3.10 Shrink it, then prove it minimal]] (hard).

Related: [[concepts/fooling-sets]] · [[concepts/dfa-minimization]] · [[concepts/dfa]] · [[concepts/nfa]] · [[concepts/subset-construction]] · [[concepts/regular-languages]]
