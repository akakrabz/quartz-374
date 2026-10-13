---
title: "Product construction"
description: "Run two DFAs in parallel on pairs of states; the choice of accepting pairs gives intersection, union, difference or symmetric difference — the proof that regular languages are closed under every boolean operation."
tags: [concept, regular, midterm-1]
aliases: ["product automaton", "product DFA", "cross-product construction"]
---

> [!definition] Definition — product of two DFAs
> Given DFAs $M_1 = (\Sigma, Q_1, s_1, A_1, \delta_1)$ and $M_2 = (\Sigma, Q_2, s_2, A_2, \delta_2)$ over the same alphabet, the product has
> $$
> Q := Q_1\times Q_2,\qquad s := (s_1,s_2),\qquad \delta\big((p,q),a\big) := \big(\delta_1(p,a),\,\delta_2(q,a)\big).
> $$
> Only the accepting set depends on the operation:
>
> | language | accepting states $A$ |
> |---|---|
> | $L_1\cap L_2$ | $\{(p,q) \mid p\in A_1 \text{ and } q\in A_2\}$ |
> | $L_1\cup L_2$ | $\{(p,q) \mid p\in A_1 \text{ or } q\in A_2\}$ |
> | $L_1\setminus L_2$ | $\{(p,q) \mid p\in A_1 \text{ and } q\notin A_2\}$ |
> | $L_1\oplus L_2$ | $\{(p,q) \mid p\in A_1 \text{ xor } q\in A_2\}$ |
> | $\overline{L_1}$ | no product needed: $M_1$ with accepting set $Q_1\setminus A_1$ |

**Why it works.** Lemma 3.1, a string induction: $\delta^*((p,q),w) = (\delta_1^*(p,w),\delta_2^*(q,w))$ for every string $w$. After reading $w$ the product sits on the pair of states that the two machines reach separately, so it can accept on any boolean combination of "$M_1$ accepts" and "$M_2$ accepts". Hence regular languages are closed under all boolean operations (Theorem 3.2, Corollary 3.4). The product has $\lvert Q_1\rvert\cdot\lvert Q_2\rvert$ states, and products of products handle any finite number of machines.

> [!template] Template — writing up a product construction
> Let $M_1 = (\Sigma, Q_1, s_1, A_1, \delta_1)$ be a DFA for $L_1$: *[its states and what each means, start, accepting states, transitions — or a drawing]*. \
> Let $M_2 = (\Sigma, Q_2, s_2, A_2, \delta_2)$ be a DFA for $L_2$: *[likewise]*. \
> Define $M := (\Sigma,\ Q_1\times Q_2,\ (s_1,s_2),\ A,\ \delta)$ with $\delta((p,q),a) := (\delta_1(p,a),\delta_2(q,a))$, \
> and with $A$ := *[the accepting pairs from the table]*. \
> By Lemma 3.1, $M$ accepts $w$ iff *[the boolean combination]*, so $L(M) =$ *[the target language]*.

> [!trap] Classic mistakes
> - $A_1\times A_2$ gives only $\cap$. For $\cup$ a pair accepts when **either** component does, including pairs where the other component rejects.
> - Both factors must be **complete DFAs** over the same alphabet: if one factor has no move, the pair has none, and $\cup$, $\setminus$ and $\oplus$ lose strings.
> - "Run both machines in parallel" alone earns little: describe each factor completely, then the product's states, start, transitions and accepting set.
> - A drawing may leave out unreachable pairs (say so), but every reachable pair needs all of its transitions.

**Example.** Let $M_1$ accept the strings that end in `01` (states $\varepsilon$, `0`, `01`, as on the [[concepts/dfa|DFA page]]) and let $M_2$ track the parity of the length (states $\textsf{E}$, $\textsf{O}$, start $\textsf{E}$). All six pairs are reachable, and the accepting sets are

- $\cap$ (ends in `01` and has even length): $\{(\mathtt{01},\textsf{E})\}$;
- $\cup$: $\{(\varepsilon,\textsf{E}),(\mathtt{0},\textsf{E}),(\mathtt{01},\textsf{E}),(\mathtt{01},\textsf{O})\}$;
- $\setminus$ (ends in `01` and has odd length): $\{(\mathtt{01},\textsf{O})\}$;
- $\oplus$: $\{(\varepsilon,\textsf{E}),(\mathtt{0},\textsf{E}),(\mathtt{01},\textsf{O})\}$.

On `1101` the product visits $(\varepsilon,\textsf{E}),(\varepsilon,\textsf{O}),(\varepsilon,\textsf{E}),(\mathtt{0},\textsf{O}),(\mathtt{01},\textsf{E})$: the input ends in `01` and has even length, so the $\cap$ machine accepts.

**Where it appears.** [[1-models-of-computation/03-finite-state-machines#36-the-product-construction|§3.6]] (definition, Lemma 3.1, a parity example, grading), [[1-models-of-computation/03-finite-state-machines#37-closure-properties|§3.7]] (Theorem 3.2, Corollary 3.4), [[1-models-of-computation/03-finite-state-machines#38-proving-a-language-is-not-regular|§3.8]] (closure as a tool for non-regularity); "and" conditions in [[1-models-of-computation/02-regular-languages#designing-a-regular-expression|regular-expression design]]; machines that run several copies of a DFA at once, such as the one for $\textsf{half}(L)$ ([[1-models-of-computation/04-nondeterministic-automata#49-regular-language-transformations|§4.9]]).

**Practice.** [[practice/topics#product-construction-and-closure-properties|Product construction and closure properties]] (4 problems) — for example [[practice/03-finite-state-machines#31-closure-and-fooling-set-verdicts|3.1 Closure and fooling-set verdicts]] (easy), [[practice/03-finite-state-machines#36-a-product-written-formally|3.6 A product, written formally]] (medium), [[practice/03-finite-state-machines#39-three-look-alike-counting-languages|3.9 Three look-alike counting languages]] (hard).

Related: [[concepts/dfa]] · [[concepts/closure-properties]] · [[concepts/regular-languages]] · [[concepts/language-transformations]] · [[concepts/state-elimination]]
