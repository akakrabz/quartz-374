---
title: "Review: regular and context-free languages (Ch 1–5)"
description: "Exam review of Chapters 1–5, the Midterm 1 material that the final exam covers again: the five Midterm-1 problem types with how to attack and how they are graded, what to know cold in each chapter, every construction with its formula (product, subset construction with epsilon-reach, epsilon-removal, Thompson's gadgets, state elimination, reversal, half, Chomsky normal form), true/false practice, the traps that cost the most points, a cheat-sheet list and a study plan for the final."
tags: [toolkit, strings, regular, context-free, midterm-1]
aliases: ["Midterm 1 review", "Chapters 1–5 review"]
---

*Scope: Chapters 1–5, the material of Midterm 1 (Mon Sep 28), which the final exam (Fri Dec 11, 8–11 am) covers again. Each section links to the chapter page that proves its claims; this page only collects. How the classes fit together: [[0-toolkit/03-the-big-picture|the big picture]].*

> [!recipe] How to use this page
> Read one section, close the page, and rewrite its definitions and formulas from memory; then compare. Whatever you missed goes on your cheat sheet (§9) or into tomorrow's practice. Then work the five problem types of §1 on paper, under time.

## 1. The exam and how to attack each problem

The Midterm 1 practice exams have **five problems in 120 minutes**, one of each type below. Any result from lecture, the lecture notes, labs or homework solutions may be cited without proof. Words like "clearly", "trivial" and "obviously" draw scrutiny, and an ambiguous answer is read unfavorably. Full rubrics: [[0-toolkit/06-how-exams-are-graded|how exams are graded]].

> [!recipe] Type 1 — true or false, with a one-sentence justification (10 parts)
> - Test the claim on tiny cases before deciding: $\varnothing$, $\{\varepsilon\}$, $\Sigma^*$, $\mathtt{0}^*$, $\{\mathtt{0}^n\mathtt{1}^n\}$, strings of length 0, 1 and 2.
> - **True** needs a reason that covers every case: name the closure property, construction or theorem. **False** needs one concrete counterexample.
> - Practice: §7 below, the traps in §8, and the "On the exams" box at the end of each chapter page.

> [!recipe] Type 2 — regular language transformations (two parts)
> - **Which direction?** For $\{w \mid f(w)\in L\}$, read $w$ and simulate $M$ on $f(w)$ — often a DFA. For $\{f(w) \mid w\in L\}$, read the output and **guess** a preimage while simulating $M$ on it — an NFA, with $\varepsilon$-transitions for symbols that $f$ deletes.
> - Start from an **arbitrary** DFA $M = (\Sigma,Q,s,A,\delta)$ for $L$. Describe $M'$ in English (what each component of a state remembers, what it guesses, when it accepts) and formally: $Q'$, $s'$, $A'$, and $\delta'(q,a)$, $\delta'(q,\varepsilon)$ in every case.
> - Check the edge cases $L = \varnothing$, $\{\varepsilon\}$, $\mathtt{1}^*$, $\Sigma^*$.
> - **Graded:** 2 for a formal, complete description (say DFA or NFA, with or without $\varepsilon$-transitions) + 2 for the English explanation + 6 for correctness (1 states, 1 start, 1 accepting states, 3 transitions).
> - Templates: [[0-toolkit/02-proof-templates#9-language-transformation|language transformation]], [[1-models-of-computation/04-nondeterministic-automata#49-regular-language-transformations|§4.9]] · model answer: [[problems/two-language-transformations|Two language transformations]] · practice: [[practice/04-nondeterministic-automata|Chapter 4 practice]].

> [!recipe] Type 3 — induction on a recursively defined string function
> - Write the boilerplate first: an **arbitrary** string; a hypothesis for **every shorter string**, quantified over every other argument the proof changes; **one case per case of the definition**.
> - Induct on the argument the function takes apart, and peel what the definition peels (two symbols for a function defined on $w = abx$).
> - Justify every equation: a definition, the hypothesis (and why the string is shorter), a lemma, or arithmetic. If a case gets stuck, prove a small lemma first or strengthen the claim.
> - **Graded:** 1 arbitrary object + 2 explicit strong hypothesis + 2 exhaustive cases + 1 base cases + 2 correct use of the hypothesis + 2 other details.
> - Templates: [[0-toolkit/02-proof-templates#1-induction-on-strings|induction on strings]], [[1-models-of-computation/01-strings#13-induction-on-strings|§1.3]] · model answer: [[problems/induction-on-a-recursive-string-function|Induction on a recursive string function]] · practice: [[practice/01-strings|Chapter 1 practice]].

> [!recipe] Type 4 — not regular (fooling set), plus a grammar for the same language
> - **Fooling set:** choose $F$ from the unbounded quantity an algorithm would have to remember (usually $\mathtt{0}^*$ or $\mathtt{0}^*\mathtt{1}$). Write arbitrary distinct $x, y\in F$ with parameters $i\ne j$, build $z$ from $x$'s parameter, and prove $xz\in L$ and $yz\notin L$, each with a reason. Check the edge case $i = 0$.
> - **Grammar:** decompose a typical string — an outer matching pair, the first point where a count balances, or cases — give each piece a nonterminal, and describe its language in English. Test $\varepsilon$ and short strings that must be rejected.
> - **Graded:** fooling set 4 for an explicit infinite set that really is a fooling set (a finite set earns 0) + 6 for the proof (2 explicit suffix, 2 one string in, 2 the other out). Grammar 2 syntax + 8 correctness: $-2$ for one mistake (often $\varepsilon$), $-4$ for a few wrong strings, all 8 for infinitely many; $\varnothing$ or $\Sigma^*$ earns nothing; ambiguity costs nothing.
> - Templates: [[0-toolkit/02-proof-templates#7-fooling-set-proof|fooling-set proof]], [[0-toolkit/02-proof-templates#2-writing-up-a-regular-expression-or-a-grammar|writing up a grammar]], [[1-models-of-computation/05-context-free-languages#designing-a-grammar|designing a grammar]] · model answer: [[problems/fooling-set-and-grammar-for-one-language|A fooling set and a grammar for one language]] · practice: [[practice/03-finite-state-machines|Chapter 3 practice]], [[practice/05-context-free-languages|Chapter 5 practice]].

> [!recipe] Type 5 — a DFA and a regular expression for one language (mnemonic state names, no proof)
> - **DFA:** write the one-pass algorithm first; states = the values of its variables; name each state after what it remembers. Draw the start arrow and double circles, and if you omit the dump state, *say* that missing transitions go to it.
> - **Regular expression:** cut typical strings into blocks; explain each piece; test $\varepsilon$ and short strings in both directions. Only $+$, concatenation, $^*$, $\varepsilon$, $\varnothing$ and parentheses.
> - **Graded:** DFA 2 for a complete, unambiguous description + 6 correctness + 2 mnemonic names (an NFA where a DFA was asked earns half). Expression 2 syntax + 8 correctness, with the deductions of type 4.
> - Templates: [[0-toolkit/02-proof-templates#5-describing-a-dfa|describing a DFA]], [[0-toolkit/02-proof-templates#2-writing-up-a-regular-expression-or-a-grammar|writing up an expression]], [[1-models-of-computation/03-finite-state-machines#35-designing-dfas-dfas-are-algorithms|§3.5]] · model answer: [[problems/regular-expression-and-dfa-for-one-language|A regular expression and a DFA for one language]] · practice: [[practice/02-regular-languages|Chapter 2 practice]], [[practice/03-finite-state-machines|Chapter 3 practice]].

## 2. Chapter 1 — Strings

[[1-models-of-computation/01-strings|Chapter 1]] · concepts: [[concepts/strings]], [[concepts/induction-on-strings]]

| object | case $w = \varepsilon$ | case $w = ax$ |
|---|---|---|
| string | the empty string | a symbol $a$ followed by a string $x$ |
| length $\lvert w\rvert$ | $0$ | $1+\lvert x\rvert$ |
| concatenation $w\bullet z$ | $z$ | $a\cdot(x\bullet z)$ — recurses on the **left** argument |
| $\#(a,w)$ | $0$ | $[a = b] + \#(a,x)$ for $w = bx$ |
| reversal $w^R$ | $\varepsilon$ | $x^R\bullet a$ |
| complement $w^c$ | $\varepsilon$ | $\mathtt{1}\cdot x^c$ if $a = \mathtt{0}$, $\mathtt{0}\cdot x^c$ if $a = \mathtt{1}$ |

Powers: $w^0 = \varepsilon$, $w^n = w\bullet w^{n-1}$.

**Numbered results.** Lemma 1.1: $w\bullet\varepsilon = w$. Lemma 1.2: $\lvert w\bullet x\rvert = \lvert w\rvert+\lvert x\rvert$. Lemma 1.3: $(w\bullet x)\bullet y = w\bullet(x\bullet y)$. Each is an induction on the left argument.

**Standard facts**, each a short induction: $(w\bullet x)^R = x^R\bullet w^R$ (the order flips), $(w^R)^R = w$, $\#(a,xy) = \#(a,x)+\#(a,y)$, $\lvert w^R\rvert = \lvert w\rvert$, $w^mw^n = w^{m+n}$, and cancellation ($xz = yz$ implies $x = y$). Cite one on an exam only if it comes from lecture, the notes, labs or homework; otherwise prove it first.

**Pieces of a string.** A *substring* is contiguous; a *prefix* starts at the beginning, a *suffix* ends at the end; a *subsequence* deletes symbols anywhere; *proper* excludes $w$ itself. A string of length $n$ has $n+1$ prefixes and $n+1$ suffixes.

**Other splits** ([[1-models-of-computation/01-strings#14-more-than-one-path-up-the-mountain|§1.4]]): $w = a$ or $w = u\bullet v$ with $u, v$ non-empty (two base cases), or peel the last symbol, $w = xa$. Any split works if the cases cover every string and the hypothesis is applied only to shorter strings.

## 3. Chapter 2 — Regular languages and regular expressions

[[1-models-of-computation/02-regular-languages|Chapter 2]] · concepts: [[concepts/languages]], [[concepts/regular-languages]], [[concepts/regular-expressions]]

| notion | what to know cold |
|---|---|
| $\varnothing$, $\{\varepsilon\}$, $\varepsilon$ | no strings; exactly one string, the empty one; a string, not a language. $\varnothing\bullet L = \varnothing$, $\{\varepsilon\}\bullet L = L$, $\varnothing^* = \{\varepsilon\}^* = \{\varepsilon\}$ |
| $AB$, $L^*$, $L^+$ | $\{xy \mid x\in A, y\in B\}$; concatenations of zero or more, one or more strings of $L$; $L^+ = L^*$ iff $\varepsilon\in L$ (Lemma 2.2(c)) |
| algebra (Lemmas 2.1–2.2) | $\cup$ is commutative and associative; concatenation is associative, **not** commutative, distributes over $\cup$ but **not** over $\cap$; $L^* = L^*L^* = (L\cup\{\varepsilon\})^*$ |
| Arden's rule (Lemma 2.3) | if $\varepsilon\notin A$: $L = AL\cup B$ if and only if $L = A^*B$ |
| regular language | $\varnothing$; one string; $L\cup L'$, $LL'$ or $L^*$ of regular languages |
| regular expression | $\varnothing$, a string, $S+T$, $ST$, $S^*$; precedence $^*$ before concatenation before $+$: $\mathtt{10}^*$ is $\mathtt{1}(\mathtt{0}^*)$ |
| structural induction | five cases: $\varnothing$, a string, $S+T$, $ST$, $S^*$; the hypothesis covers the proper subexpressions |
| Lemmas 2.4–2.5 | an expression without $\varnothing$ denotes a non-empty language; every non-empty regular language has such an expression |
| counting (§2.8) | countably many regular languages, uncountably many languages |

To prove a property of **every regular language**, pick an expression for it and induct on the expression ([[1-models-of-computation/02-regular-languages#27-proofs-about-regular-languages|§2.7]]); the recursion $\textsf{rev}(ST) = \textsf{rev}(T)\,\textsf{rev}(S)$ (order swapped, every other case unchanged) proves that reversals of regular languages are regular.

## 4. Chapter 3 — Finite-state machines

[[1-models-of-computation/03-finite-state-machines|Chapter 3]] · concepts: [[concepts/dfa]], [[concepts/product-construction]], [[concepts/fooling-sets]], [[concepts/myhill-nerode-theorem]], [[concepts/dfa-minimization]]

> [!definition] DFA and the product construction
> $M = (\Sigma, Q, s, A, \delta)$ with $\delta\colon Q\times\Sigma\to Q$ **total**; $\delta^*(q,\varepsilon) = q$, $\delta^*(q,ax) = \delta^*(\delta(q,a),x)$; $L(M) = \{w \mid \delta^*(s,w)\in A\}$; and $\delta^*(q,xy) = \delta^*(\delta^*(q,x),y)$.
>
> **Product** of $M_1$, $M_2$: $Q = Q_1\times Q_2$, $s = (s_1,s_2)$, $\delta((p,q),a) = (\delta_1(p,a),\delta_2(q,a))$, and the accepting set picks the operation:
>
> | $L_1\cap L_2$ | $L_1\cup L_2$ | $L_1\setminus L_2$ | $L_1\oplus L_2$ | $\overline{L_1}$ (one machine) |
> |---|---|---|---|---|
> | $p\in A_1$ and $q\in A_2$ | $p\in A_1$ or $q\in A_2$ | $p\in A_1$ and $q\notin A_2$ | exactly one of the two | $Q_1\setminus A_1$ |

| result | statement |
|---|---|
| Lemma 3.1 | $\delta^*((p,q),w) = (\delta_1^*(p,w),\delta_2^*(q,w))$ |
| Theorem 3.2 | automatic languages are closed under complement, $\cup$, $\cap$, $\setminus$, $\oplus$ |
| Theorem 3.3 (Kleene) | regular expressions and DFAs describe the same languages (proved in Chapter 4) |
| Corollaries 3.4, 3.5 | regular languages are closed under complement, $\cap$, $\setminus$, $\oplus$; automatic ones under concatenation and $^*$ |
| Lemmas 3.6–3.9 | $\{\mathtt{0}^n\mathtt{1}^n\}$, $\{ww^R\}$, $\{\mathtt{0}^{2^n}\}$ and $\{\mathtt{0}^p \mid p\text{ prime}\}$ are not regular |
| Myhill–Nerode | fewest states of a DFA for $L$ = largest fooling set = number of classes of $\equiv_L$; so $L$ is regular iff every fooling set is finite |

**Designing and proving.** States are the values of the variables of a one-pass algorithm ([[1-models-of-computation/03-finite-state-machines#35-designing-dfas-dfas-are-algorithms|§3.5]]). A correctness proof gives every state a meaning and proves all the meanings at once by induction ([[1-models-of-computation/03-finite-state-machines#33-proving-a-dfa-correct|§3.3]]).

**Standard fooling sets** (for $x\ne y$ written with $i\ne j$):

| language | $F$ | suffix for $x$ |
|---|---|---|
| $\{\mathtt{0}^n\mathtt{1}^n\}$, $\#(\mathtt{0},w) = \#(\mathtt{1},w)$ | $\mathtt{0}^*$ | $x = \mathtt{0}^i$: $z = \mathtt{1}^i$ |
| $\{ww^R\}$, palindromes | $\mathtt{0}^*\mathtt{1}$ | $x = \mathtt{0}^i\mathtt{1}$: $z = \mathtt{1}\mathtt{0}^i$ |
| $\{\mathtt{0}^n\mathtt{1}^n\mathtt{0}^n\}$ | $\mathtt{0}^*$ | $x = \mathtt{0}^i$: $z = \mathtt{1}^i\mathtt{0}^i$ |
| balanced parentheses | $\mathtt{(}^*$ | $x = \mathtt{(}^i$: $z = \mathtt{)}^i$ |
| $\{\mathtt{0}^{2^n}\}$ | the language itself | $x = \mathtt{0}^{2^i}$: $z = \mathtt{0}^{2^i}$ |

**Minimization (Moore).** Mark every pair with exactly one accepting state; then mark $\{p,q\}$ whenever $\{\delta(p,a),\delta(q,a)\}$ is marked, until a pass marks nothing; merge the unmarked pairs. $O(\sigma n^3)$ time; Hopcroft's algorithm is $O(\sigma n\log n)$. Worked problem: [[problems/a-product-construction-written-formally|A product construction, written formally]].

## 5. Chapter 4 — Nondeterministic automata

[[1-models-of-computation/04-nondeterministic-automata|Chapter 4]] · concepts: [[concepts/nfa]], [[concepts/subset-construction]], [[concepts/thompsons-algorithm]], [[concepts/state-elimination]], [[concepts/kleenes-theorem]], [[concepts/language-transformations]]

> [!definition] NFA, epsilon-reach, epsilon-removal and the subset construction
> **NFA:** $\delta\colon Q\times(\Sigma\cup\{\varepsilon\})\to 2^Q$; $M$ accepts $w$ iff **some** walk from $s$ to an accepting state spells $w$. The $\varepsilon$-reach of $q$ is everything reachable from $q$ by zero or more $\varepsilon$-transitions, and
> $$
> \delta^*(q,\varepsilon) = \varepsilon\text{-reach}(q),\qquad \delta^*(q,ax) = \bigcup_{r\in\varepsilon\text{-reach}(q)}\ \bigcup_{p\in\delta(r,a)}\delta^*(p,x).
> $$
> **Removing $\varepsilon$-transitions** (same states and start): $A' = \{q \mid \varepsilon\text{-reach}(q)\cap A\ne\varnothing\}$ and $\delta'(q,a) = \bigcup_{r\in\varepsilon\text{-reach}(q)}\delta(r,a)$.
>
> **Subset construction** (NFA to DFA, [[1-models-of-computation/04-nondeterministic-automata#45-nfa-to-dfa-the-subset-construction|§4.5]]):
> $$
> \begin{gathered}
> Q' = 2^Q,\qquad s' = \{s\},\qquad A' = \{S \mid \varepsilon\text{-reach}(S)\cap A\ne\varnothing\},\\
> \delta'(S,a) = \bigcup_{p\in S}\ \bigcup_{r\in\varepsilon\text{-reach}(p)}\delta(r,a).
> \end{gathered}
> $$
> By hand, build only the reachable subsets, breadth-first from $\{s\}$, in a table with columns $S$, $\varepsilon$-reach$(S)$, accepting?, and $\delta'(S,a)$ for each $a$; $\varnothing$ gets a row if it appears.

> [!definition] Thompson's gadgets (expression to NFA, [[1-models-of-computation/04-nondeterministic-automata#46-regular-expression-to-nfa-thompsons-algorithm|§4.6]])
> Every gadget has one start state $s$ and one accepting state $t\ne s$ (Lemma 4.2).
>
> | expression | gadget |
> |---|---|
> | $\varnothing$, $\varepsilon$, a symbol $a$ | states $s$, $t$ with no transition, $s\xrightarrow{\varepsilon}t$, or $s\xrightarrow{a}t$ |
> | $ST$ | in series: $t_S\xrightarrow{\varepsilon}s_T$; start $s_S$, accept $t_T$ |
> | $S+T$ | new $s$, $t$: $s\xrightarrow{\varepsilon}s_S$, $s\xrightarrow{\varepsilon}s_T$, $t_S\xrightarrow{\varepsilon}t$, $t_T\xrightarrow{\varepsilon}t$ |
> | $S^*$ | new $s$, $t$: $s\xrightarrow{\varepsilon}s_S$, $t_S\xrightarrow{\varepsilon}t$, the bypass $s\xrightarrow{\varepsilon}t$, and a back edge for another copy — $t\xrightarrow{\varepsilon}s$ as the book draws it ($t_S\xrightarrow{\varepsilon}s_S$ works as well) |
>
> Two states per leaf, per $+$ and per $^*$, none per concatenation: $(\mathtt{0}+\mathtt{10}^*\mathtt{1})^*$ gets $2\times(4+1+2) = 14$.

> [!definition] State elimination (NFA to expression, [[1-models-of-computation/04-nondeterministic-automata#48-nfa-to-regular-expression-state-elimination|§4.8]])
> Add a new start $s$ with $s\xrightarrow{\varepsilon}$ (old start) and a new target $t$ with (every accepting state) $\xrightarrow{\varepsilon}t$; a missing edge is $\varnothing$. Remove the old states one at a time; removing $q$ sets, for **every** pair of remaining states $p$, $r$ — including $p = r$,
> $$
> R'(p\to r) = R(p\to r) + R(p\to q)\,R(q\to q)^*\,R(q\to r).
> $$
> At the end, $R(s\to t)$ is the expression (Lemma 4.3). $O(n^3)$ operations, but the expression can reach length $\Theta(4^n)$.

**Kleene's theorem (Theorem 4.1)** is the cycle expression $\to$ NFA (Thompson) $\to$ DFA (subsets) $\to$ NFA (a DFA already is one) $\to$ expression (elimination). Every arrow preserves the language, not the size: subsets can cost $2^{\lvert Q\rvert}$ states, elimination exponential length. The book's runs: $(\mathtt{0}+\mathtt{10}^*\mathtt{1})^*$ gives 14 NFA states, 5 DFA states, 2 after minimization; $(\mathtt{0}+\mathtt{1})^*(\mathtt{00}+\mathtt{11})(\mathtt{0}+\mathtt{1})^*$ gives 18 (26 if each $\mathtt{0}+\mathtt{1}$ is built literally), 9, and 4.

> [!definition] The two transformation lemmas ([[1-models-of-computation/04-nondeterministic-automata#49-regular-language-transformations|§4.9]])
> Let $M = (\Sigma,Q,s,A,\delta)$ be a DFA for $L$.
>
> **Lemma 4.4 — reversal** $L^R = \{w^R \mid w\in L\}$. Reverse every edge, add a new start $s^R$ with $\varepsilon$-edges to the old accepting states, and accept only at $s$:
> $$
> Q^R = Q\cup\{s^R\},\quad A^R = \{s\},\quad \delta^R(s^R,\varepsilon) = A,\quad \delta^R(q,a) = \{p \mid \delta(p,a) = q\}.
> $$
> (Or by expressions: reverse every string and swap the factors of every concatenation.)
>
> **Lemma 4.5 — half** $\textsf{half}(L) = \{w \mid ww\in L\}$. Guess the halfway state $h$, then run a left copy of $M$ from $s$ and a right copy from $h$ side by side:
> $$
> \begin{gathered}
> Q' = Q^3\cup\{s'\},\qquad \delta'(s',\varepsilon) = \{(s,h,h) \mid h\in Q\},\\
> \delta'((p,h,q),a) = \{(\delta(p,a),h,\delta(q,a))\},\qquad A' = \{(h,h,q) \mid h\in Q,\ q\in A\}.
> \end{gathered}
> $$

Worked problems: [[problems/subset-construction-by-hand|The subset construction by hand]], [[problems/state-elimination-by-hand|State elimination by hand]], [[problems/two-language-transformations|Two language transformations]].

## 6. Chapter 5 — Context-free languages

[[1-models-of-computation/05-context-free-languages|Chapter 5]] · concepts: [[concepts/context-free-grammars]], [[concepts/parse-trees-and-ambiguity]], [[concepts/recursive-automata]], [[concepts/chomsky-normal-form]]

| notion | what to know cold |
|---|---|
| grammar | $G = (\Sigma,\Gamma,R,S)$: terminals, nonterminals, rules $A\to\omega$ with $\omega\in(\Sigma\cup\Gamma)^*$, start symbol; $xAz\rightsquigarrow xyz$ for a rule $A\to y$; $L(G) = \{w\in\Sigma^* \mid S\rightsquigarrow^* w\}$ |
| parse trees, ambiguity | one parse tree = one **leftmost** derivation; a *grammar* is ambiguous if some string has two parse trees; a *language* is inherently ambiguous if every grammar for it is |
| $L(G) = L$ | two inductions: $L\subseteq L(G)$ builds derivations (Lemma 5.1), $L(G)\subseteq L$ takes them apart, one case per rule (Lemma 5.2); with $\varepsilon$-rules use a **shortest** derivation (Lemma 5.3); nonterminals that use each other need one **mutual** induction (Lemma 5.4) |
| regular ⊆ context-free | for an expression: $\varnothing$: $S\to S$; a string $w$: $S\to w$; $R_1+R_2$: $S\to S_1\mid S_2$; $R_1R_2$: $S\to S_1S_2$; $R_1^*$: $S\to\varepsilon\mid S_1S$ (§5.5) |
| closure | **yes** under $\cup$, concatenation, $^*$ and reversal (§5.5), and under $\cap$ with a regular language (a standard fact the book does not prove: [[concepts/closure-properties\|closure properties]]); **no** under $\cap$ and complement (§5.6) |
| recursive automata | NFAs that call each other; one module per nonterminal (Lemma 5.5); back to a grammar with one nonterminal per state, $[q]\to a[p]$, $[q]\to[p]$, $[q]\to[s_A][p]$, $[t_A]\to\varepsilon$ (Lemma 5.6) |
| Chomsky normal form | start symbol on no right side; $S\to\varepsilon$ allowed; otherwise only $A\to BC$ and $A\to a$. A string of length $n\ge1$ has parse trees with $2n-1$ nonterminal nodes and derivations of exactly $2n-1$ steps; membership in $O(n^3)$ time by dynamic programming (CYK); Theorem 5.7: size $O(L^2)$ in $O(L^2)$ time |

**Grammars to know by heart** ([[1-models-of-computation/05-context-free-languages#54-more-examples|§5.4]]):

| language | grammar |
|---|---|
| $\{\mathtt{0}^n\mathtt{1}^n\}$ | $C\to\varepsilon\mid\mathtt{0}C\mathtt{1}$ |
| $\{\mathtt{0}^m\mathtt{1}^n \mid m\ne n\}$ | $S\to A\mid B$, $A\to\mathtt{0}A\mid\mathtt{0}C$, $B\to B\mathtt{1}\mid C\mathtt{1}$, $C$ as above |
| palindromes | $S\to\mathtt{0}S\mathtt{0}\mid\mathtt{1}S\mathtt{1}\mid\mathtt{0}\mid\mathtt{1}\mid\varepsilon$ |
| $\#(\mathtt{0},w) = \#(\mathtt{1},w)$ | $S\to\mathtt{0}S\mathtt{1}S\mid\mathtt{1}S\mathtt{0}S\mid\varepsilon$ |
| $\#(\mathtt{0},w)\ge\#(\mathtt{1},w)$ | $S\to\mathtt{0}S\mathtt{1}\mid\mathtt{1}S\mathtt{0}\mid SS\mid\mathtt{0}\mid\varepsilon$ |
| balanced parentheses | $S\to\mathtt{(}S\mathtt{)}S\mid\varepsilon$ (unambiguous) |

> [!recipe] CNF conversion, steps 0–6 (§5.9)
> 0. Add a new start $S'\to S$ if $S$ is on a right side or derives $\varepsilon$.
> 1. Split long rules: $A\to X\alpha$ with $\lvert\alpha\rvert\ge2$ becomes $A\to XB$, $B\to\alpha$.
> 2. Find the nullable nonterminals, repeating until nothing changes.
> 3. Remove $\varepsilon$-rules: add every variant with **some** nullable occurrences deleted, delete every $A\to\varepsilon$, then **add** $S'\to\varepsilon$ if $S'$ is nullable.
> 4. Merge the nonterminals on a cycle of unit rules $A\to B$, and delete every rule $A\to A$.
> 5. Remove unit rules in reverse topological order, copying the target's rules **after** the target is processed.
> 6. Replace each terminal $a$ in a right side of length 2 by a new $T_a\to a$.

Worked problems: [[problems/proving-what-a-grammar-generates|Proving what a grammar generates]], [[problems/cnf-conversion-step-by-step|CNF conversion, step by step]], [[problems/fooling-set-and-grammar-for-one-language|A fooling set and a grammar for one language]].

## 7. True or false: twelve to practice

Cover the right-hand columns, answer, then check.

| statement | answer | one-sentence justification |
|---|---|---|
| $\varnothing^* = \varnothing$. | false | $\varnothing^* = \{\varepsilon\}$ (§2.2). |
| $L^+ = L^*$ for every language $L$. | false | only when $\varepsilon\in L$; for $L = \{\mathtt{0}\}$, $\varepsilon\in L^*\setminus L^+$ (Lemma 2.2). |
| If $L$ is regular, so is $\{w\in L \mid \lvert w\rvert \text{ is even}\}$. | true | it is $L$ intersected with the regular language $((\mathtt{0}+\mathtt{1})(\mathtt{0}+\mathtt{1}))^*$ (Corollary 3.4). |
| If $L_1\cup L_2$ is regular, then $L_1$ is regular. | false | $\{\mathtt{0}^n\mathtt{1}^n\}\cup\overline{\{\mathtt{0}^n\mathtt{1}^n\}} = \Sigma^*$. |
| If $L^*$ is regular, then $L$ is regular. | false | $L = \{\mathtt{0}^{2^n} \mid n\ge0\}$ is not regular (Lemma 3.8), but it contains `0`, so $L^* = \mathtt{0}^*$. |
| If $L$ is regular, so is $\{ww \mid w\in L\}$. | false | $L = \mathtt{0}^*\mathtt{1}$ gives $\{\mathtt{0}^n\mathtt{1}\mathtt{0}^n\mathtt{1}\}$, with fooling set $\mathtt{0}^*$ and suffix $\mathtt{1}\mathtt{0}^i\mathtt{1}$ for $\mathtt{0}^i$. |
| If $L$ is regular, so is $\{w \mid ww\in L\}$. | true | Lemma 4.5. |
| If $L$ has a fooling set of size 5, every DFA for $\overline{L}$ has at least 5 states. | true | a suffix that distinguishes two strings for $L$ also distinguishes them for $\overline{L}$. |
| Swapping the accepting and non-accepting states of an NFA for $L$ gives an NFA for $\overline{L}$. | false | a string can have an accepting and a rejecting walk at once; determinize first ([[concepts/nfa]]). |
| Every regular language is context-free. | true | §5.5 turns any regular expression into a grammar. |
| The intersection of two context-free languages is context-free. | false | $\{\mathtt{0}^i\mathtt{1}^i\mathtt{0}^j\}\cap\{\mathtt{0}^i\mathtt{1}^j\mathtt{0}^j\}$ (with $i\ge1$, resp. $j\ge1$) is $\{\mathtt{0}^n\mathtt{1}^n\mathtt{0}^n \mid n\ge1\}$ (§5.6). |
| If a grammar is ambiguous, its language is inherently ambiguous. | false | $S\to\mathtt{1}\mid S{+}S$ is ambiguous; $S\to\mathtt{1}\mid\mathtt{1}{+}S$ generates the same language unambiguously (§5.2). |

## 8. The traps that cost the most points

> [!trap] Across Chapters 1–5
> 1. **The induction hypothesis is too weak** — stated only for $x$, or not quantified over the other arguments the proof changes (§1.4). State it for every shorter string, for all values of the other arguments.
> 2. **Applying the hypothesis to a string that is not shorter**, or without saying why it is shorter.
> 3. **The missing or extra $\varepsilon$** in an expression or grammar: the typical one-mistake deduction. Test $\varepsilon$ every time.
> 4. **Precedence**: $\mathtt{10}^*\ne(\mathtt{10})^*$ and $\mathtt{0}+\mathtt{1}^*\ne(\mathtt{0}+\mathtt{1})^*$. Regex shorthand (`+` for "one or more", `?`, `[01]`) is not allowed.
> 5. **An incomplete DFA**: missing transitions without the sentence about the dump state, or an NFA where a DFA was asked (half credit).
> 6. **A fooling-set "proof" with one example pair**, a finite set, a suffix chosen for a specific $i$ and $j$, or only one of the two memberships checked. "Without loss of generality $i<j$" needs a symmetric argument.
> 7. **Closure in the wrong direction**: a regular intersection or union says nothing about $L$; a subset of a regular language need not be regular.
> 8. **The subset construction without $\varepsilon$-reach** on every row, accepting only if *all* states accept, or dropping the reachable $\varnothing$.
> 9. **Transformations built for an example** language instead of an arbitrary DFA, with $\delta'$ undefined in some case (in particular $\delta'(q,\varepsilon)$), and never tested on $\varnothing$, $\{\varepsilon\}$, $\mathtt{1}^*$, $\Sigma^*$.
> 10. **State elimination that forgets $p = r$** (the self-loops change) or the old direct term $R(p\to r)$.
> 11. **A grammar whose nonterminals are described by their role** ("the middle part") instead of their language — and two derivations offered as proof of ambiguity when they build the same parse tree.
> 12. **CNF step 3 or step 5 done carelessly**: every subset of the nullable occurrences, and the unit rules removed in the right order.

## 9. What to put on your cheat sheet

The final allows **two** double-sided, handwritten letter sheets for the whole course, and Chapters 6–9 and the algorithms half need room too. Writing them is part of the review. For Chapters 1–5:

- The string-induction boilerplate and the recursive definitions of $\lvert w\rvert$, $\bullet$, $\#(a,w)$, $w^R$; the fact $(wx)^R = x^R w^R$.
- $\varnothing$ versus $\{\varepsilon\}$, $L^+$ versus $L^*$, Arden's rule, regular-expression precedence.
- The DFA tuple, $\delta^*$, and the product table of accepting sets.
- The fooling-set template and the standard fooling-set table of §4; the Myhill–Nerode statement.
- NFA $\delta^*$ with $\varepsilon$-reach; the $\varepsilon$-removal and subset-construction formulas.
- Thompson's gadgets (four small sketches), the elimination rule, and the costs around Kleene's cycle.
- The transformation template, the reversal and half constructions, and the edge cases $\varnothing$, $\{\varepsilon\}$, $\mathtt{1}^*$, $\Sigma^*$.
- The grammars of §6, the regular-to-grammar table, and context-free closure (yes: $\cup$, concatenation, $^*$, reversal, $\cap$ regular; no: $\cap$, complement).
- The CNF definition and the conversion steps 0–6.
- The rubric numbers of §1 — they tell you what to write down first.

## 10. A study plan for the final

> [!tip] From now to Dec 11
> 1. **Until Midterm 2 (Mon Nov 9): keep it warm.** The algorithms half comes first. Once a week, do one exam-length problem from Chapters 1–5, rotating through the five types of §1 ([[practice/hard|hard practice problems]]).
> 2. **The first two weeks after Midterm 2: rebuild, chapter by chapter.** For each of Chapters 1–5, read the chapter page's definition, template and trap boxes, rewrite its section of this page from memory, then do the chapter's easy practice problems and one medium.
> 3. **Write the cheat sheets while you rebuild**, by hand, from §9 here and from the [[0-toolkit/02-proof-templates|proof templates]].
> 4. **The week after: timed.** Work a Midterm 1 practice exam in 120 minutes with only your cheat sheet, and grade it yourself with the rubrics of §1. Redo every lost point a day later, without looking.
> 5. **The last days: breadth.** The true/false table of §7, the traps of §8, and the [[0-toolkit/03-the-big-picture|big picture]] — then the same routine for [[0-toolkit/05-review-turing-machines-and-undecidability|Chapters 6–9]].

Related: [[0-toolkit/03-the-big-picture|the big picture]] · [[0-toolkit/05-review-turing-machines-and-undecidability|review of Chapters 6–9]] · [[0-toolkit/06-how-exams-are-graded|how exams are graded]] · [[practice/index|practice problems]]

### Sources for this page
Erickson, *Models of Computation*, Chapters 1–5, summarized in our own words, with the book's numbering; every definition, formula and result here follows the chapter page it links to. Exam format and rubrics: CS/ECE 374 A (Fall 2026) course website and Midterm 1 practice exams, paraphrased. The study plan, the cheat-sheet list and the true/false items are original. The construction formulas (product accepting sets, $\varepsilon$-removal, subset construction, both versions of Thompson's star gadget, the elimination rule, reversal and half) are checked on hundreds of random machines and on every small expression, and so are the true/false witnesses ($\{\mathtt{0}^{2^n}\}^* = \mathtt{0}^*$, the fooling set for $\{\mathtt{0}^n\mathtt{1}\mathtt{0}^n\mathtt{1}\}$) and the fooling-set table, by `tools/checks/toolkit_2.py`.
