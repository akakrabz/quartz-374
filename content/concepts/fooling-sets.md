---
title: "Fooling sets"
description: "Strings that must all reach different states of any DFA for L: a finite fooling set is a lower bound on the number of states, an infinite one proves L is not regular. The exam proof template, how to choose the set, and how the proof is graded."
tags: [concept, regular, midterm-1]
aliases: ["fooling set", "distinguishing suffix", "non-regularity proof"]
---

> [!definition] Definition — distinguishing suffix, fooling set
> A **distinguishing suffix** for strings $x$ and $y$ (with respect to $L$) is a string $z$ such that **exactly one** of $xz$ and $yz$ is in $L$. A **fooling set** for $L$ is a set $F$ of strings in which every pair of distinct strings has a distinguishing suffix.
>
> **Fact.** If $F$ is a fooling set for $L$, every DFA for $L$ has at least $\lvert F\rvert$ states. So if $L$ has an **infinite** fooling set, $L$ is **not regular**.

**Why it works.** A DFA remembers nothing but its state. If distinct $x, y\in F$ reached the same state, then $xz$ and $yz$ would reach the same state for every $z$, and the DFA would accept both or neither — but a distinguishing suffix puts exactly one of them in $L$. The [[concepts/myhill-nerode-theorem|Myhill–Nerode theorem]] adds the converse: every non-regular language has an infinite fooling set, so the method always works in principle.

> [!template] Template — fooling-set proof
> Let $F = $ *[an explicit infinite set]*. \
> Let $x$ and $y$ be arbitrary distinct strings in $F$. \
> The definition of $F$ implies $x = $ *[…]* and $y = $ *[…]* for some integers $i\ne j$. \
> Let $z = $ *[a suffix that may depend on $i$ and $j$]*. \
> Then $xz = $ *[…]* $\in L$, because *[…]*. \
> And $yz = $ *[…]* $\notin L$, because *[…]*. \
> So $F$ is a fooling set for $L$. Because $F$ is infinite, $L$ cannot be regular. $\blacksquare$

**Choosing $F$.** Ask what any algorithm for $L$ must remember without bound — a count, a prefix, a position — and let $F$ list its values: $\mathtt{0}^*$ for a count of 0s, $\mathtt{0}^*\mathtt{1}$ or all of $\Sigma^*$ for a remembered prefix, sometimes $L$ itself. Keep the strings simple; they need not belong to $L$. **Finite fooling sets** give lower bounds: $\{\varepsilon,\mathtt{1},\mathtt{11}\}$ is one for "contains `11`" ($z = \mathtt{1}$ separates $\varepsilon$ from `1`, and $z = \varepsilon$ separates `11` from both), so the 3-state DFA for that language is minimal.

> [!trap]
> - One example pair is not a proof: argue for *arbitrary* distinct $x, y\in F$.
> - Prove both halves, each with a reason: one of $xz, yz$ is in $L$, the other is not.
> - "Assume $i<j$" needs "without loss of generality" *and* a symmetric argument; a suffix built from $x$ alone is usually not symmetric.
> - $F$ must be infinite and explicit; a finite set proves only a lower bound.
> - $z$ may depend on $x$ and $y$, never on a hypothetical DFA.

**Example.** $L = \{w\in\{\mathtt{0},\mathtt{1}\}^* \mid \#(\mathtt{0},w) > \#(\mathtt{1},w)\}$ is not regular. Let $F = \mathtt{0}^*$, so distinct $x, y\in F$ are $x = \mathtt{0}^i$ and $y = \mathtt{0}^j$ with $i\ne j$, and let $z = \mathtt{1}^{\min(i,j)}$. Whichever of $xz, yz$ has $\min(i,j)$ zeros has equally many 0s and 1s, so it is not in $L$; the other has $\max(i,j) > \min(i,j)$ zeros, so it is in $L$. The naive $z = \mathtt{1}^i$ fails when $j<i$: then neither $xz$ nor $yz$ is in $L$.

> [!exam] How a fooling-set proof is graded
> 4 points for an explicit infinite set that really is a fooling set (a finite set earns nothing); 6 for the argument with arbitrary distinct $x, y$ — 2 for an explicit suffix $z$, 2 for showing one of $xz, yz$ is in $L$, 2 for showing the other is not. Midterm-1-style exams pair this proof with a [[concepts/context-free-grammars|grammar]] for the same language.

**Where it appears.** [[1-models-of-computation/03-finite-state-machines#38-proving-a-language-is-not-regular|§3.8]] (definitions, Lemmas 3.6–3.9, a table of standard fooling sets, the closure alternative), [[1-models-of-computation/03-finite-state-machines#39-the-myhillnerode-theorem|§3.9]] (why an infinite fooling set always exists), [[1-models-of-computation/02-regular-languages#24-things-that-arent-regular-expressions|§2.4]] ($\{ww\}$ is not regular), [[1-models-of-computation/05-context-free-languages#55-regular-languages-are-context-free|§5.5]] (the language $\{\mathtt{0}^n\mathtt{1}^n\}$ separates regular from context-free).

**Practice.** [[practice/topics#fooling-sets-and-non-regularity|Fooling sets and non-regularity]] (8 problems) — for example [[practice/03-finite-state-machines#31-closure-and-fooling-set-verdicts|3.1 Closure and fooling-set verdicts]] (easy), [[practice/03-finite-state-machines#37-squares-need-a-marker|3.7 Squares need a marker]] (medium), [[practice/03-finite-state-machines#39-three-look-alike-counting-languages|3.9 Three look-alike counting languages]] (hard).

Related: [[concepts/myhill-nerode-theorem]] · [[concepts/dfa-minimization]] · [[concepts/closure-properties]] · [[concepts/regular-languages]] · [[concepts/dfa]] · [[concepts/context-free-grammars]]
