---
title: "Midterm 1 practice test 3 — solutions"
description: "Ten true/false statements on regular and context-free languages; a recursive parity function with the product and closure proofs for OddParity(L) and AddParity(L); a fooling set and a grammar for {w 0^n w^R : n > 0}; the two take2skip2 transformations (simulate M on the taken symbols, or guess the skipped ones); and a DFA plus a regular expression for 'runs of 1s even, runs of 0s odd' and for '0*10* with length a multiple of 3'."
tags: [exam, midterm-1, regular, context-free]
---

*Midterm 1 practice test 3 · CS/ECE 374 A, Fall 2026 · five problems in the exam's format · the other tests: [[3-homework-and-exams/midterm-1-practice-1|test 1]], [[3-homework-and-exams/midterm-1-practice-2|test 2]] · how it is graded: [[0-toolkit/06-how-exams-are-graded|rubrics]]*

> [!abstract] In one breath
> Problem 1 is the usual ten true/false statements, most of them settled by one closure fact or one example ($\varnothing^* = \{\varepsilon\}$, a finite language is regular, a fooling set for a language with a $k$-state DFA has at most $k$ strings). Problem 2 defines *parity* recursively and then proves $\textsf{OddParity}(L)$ regular by a product construction and $\textsf{AddParity}(L)$ regular by closure under concatenation and union. Problem 3 is the fooling-set-plus-grammar pair for $\{w\mathtt{0}^nw^R \mid n > 0\}$: the fooling set is $\mathtt{1}^*$ with suffix $\mathtt{0}\mathtt{1}^i$, and the grammar builds $w$ and $w^R$ from the inside out. Problem 4 is the transformation pair for $\textsf{take2skip2}$: when the input is the *original* string, a DFA counts positions mod 4 and feeds every taken symbol to $M$; when the input is the *subsequence*, an NFA guesses the skipped symbols with $\varepsilon$-transitions. Problem 5 asks for a DFA and a regular expression for two languages, each one state per "what I need to remember".

## Problem 1 — True or false

> [!question] Problem 1
> For each statement below, check "Yes" if the statement is always true and check "No" otherwise, and give a brief (one short sentence) explanation of your answer.

- **(a)** *Every integer in the empty set is prime.* \
  **Yes.** The statement is vacuously true, because the empty set contains no integers.
- **(b)** *The language $\{\mathtt{0}^m\mathtt{1}^n \mid m + n \le 374\}$ is regular.* \
  **Yes.** The language is finite, and every finite language is regular.
- **(c)** *The language $\{\mathtt{0}^m\mathtt{1}^n \mid m - n \le 374\}$ is regular.* \
  **No.** $\mathtt{0}^*$ is an infinite [[concepts/fooling-sets|fooling set]]: for $i < j$, the suffix $\mathtt{0}^{374}\mathtt{1}^i$ distinguishes $\mathtt{0}^i$ from $\mathtt{0}^j$, because $\mathtt{0}^{374+i}\mathtt{1}^i$ is in the language but $\mathtt{0}^{374+j}\mathtt{1}^i$ is not.
- **(d)** *For all languages $L$, the language $L^*$ is regular.* \
  **No.** The irregular language $L = \{w \mid \#(\mathtt{0}, w) = \#(\mathtt{1}, w)\}$ contains $\varepsilon$ and is closed under concatenation, so $L^* = L$.
- **(e)** *For all languages $L$, the language $L^*$ is infinite.* \
  **No.** $\varnothing^* = \{\varepsilon\}$, which is finite.
- **(f)** *For all languages $L \subseteq \Sigma^*$, if $L$ can be represented by a regular expression, then $\Sigma^* \setminus L$ is recognized by a DFA.* \
  **Yes.** $L$ is regular, so some DFA accepts $L$; swapping its accepting and non-accepting states gives a DFA for $\Sigma^* \setminus L$.
- **(g)** *For all languages $L$ and $L'$, if $L \cap L' = \varnothing$ and $L'$ is not regular, then $L$ is regular.* \
  **No.** For $L' = \{\mathtt{0}^n\mathtt{1}^n \mid n \ge 0\}$ and $L = \Sigma^* \setminus L'$, the two languages are disjoint, but $L$ is not regular (otherwise its complement $L'$ would be).
- **(h)** *Every regular language is recognized by a DFA with at least 374 accepting states.* \
  **Yes.** Adding 374 new accepting states (each with self-loops on both symbols) that are unreachable from the start state does not change the language.
- **(i)** *Every regular language is recognized by an NFA with at most 374 accepting states.* \
  **Yes.** One suffices: add a new accepting state with $\varepsilon$-transitions into it from every old accepting state, and make the old accepting states non-accepting.
- **(j)** *Every context-free language has an infinite fooling set.* \
  **No.** Every regular language is context-free, but if a DFA with $k$ states accepts $L$, then every fooling set for $L$ has at most $k$ strings.

> [!exam] How this is graded
> One short sentence per item is what the format asks for: a closure fact ([[0-toolkit/03-the-big-picture#4-closure-at-a-glance|closure table]]), an explicit example or a one-line construction. The three "No" answers that rest on an example — (d), (e), (g) — name the example; (c) names the fooling set *and* the suffix, as the [[0-toolkit/06-how-exams-are-graded#7-fooling-sets|fooling-set rubric]] wants; (j) is the [[concepts/myhill-nerode-theorem|Myhill–Nerode]] bound. Review: [[0-toolkit/04-review-regular-and-context-free#7-true-or-false-twelve-to-practice|twelve more true/false items]].

## Problem 2 — Parity: a recursive definition, a product, and closure

> [!question] Problem 2
> The *parity* of a bit-string $w$ is `0` if $w$ has an even number of `1`s, and `1` if $w$ has an odd number of `1`s.
>
> (a) Give a self-contained, formal, recursive definition of the *parity* function.
>
> (b) *Prove* that for every regular language $L$, the language $\textsf{OddParity}(L) := \{w \in L \mid \mathit{parity}(w) = \mathtt{1}\}$ is also regular.
>
> (c) *Prove* that for every regular language $L$, the language $\textsf{AddParity}(L) := \{\mathit{parity}(w) \cdot w \mid w \in L\}$ is also regular.

### (a) The recursive definition

> [!key] Answer (a)
> $$
> \mathit{parity}(w) :=
> \begin{cases}
> \mathtt{0} & \text{if } w = \varepsilon\\
> \mathit{parity}(x) & \text{if } w = \mathtt{0}x \text{ for some string } x\\
> \mathtt{1} & \text{if } w = \mathtt{1}x \text{ and } \mathit{parity}(x) = \mathtt{0} \text{ for some string } x\\
> \mathtt{0} & \text{if } w = \mathtt{1}x \text{ and } \mathit{parity}(x) = \mathtt{1} \text{ for some string } x
> \end{cases}
> $$
> That is, a leading `0` does not change the parity, and a leading `1` flips it.

The definition peels one symbol off the front, like the recursive functions of [[1-models-of-computation/01-strings#12-two-recursive-functions|§1.2]], and its cases are exhaustive: $w$ is empty, or starts with `0`, or starts with `1` (and then $\mathit{parity}(x)$ is one of the two symbols).

### (b) OddParity(L) is regular

Let $M = (Q, s, A, \delta)$ be a DFA that accepts $L$. We construct a DFA $M' = (Q', s', A', \delta')$ that runs $M$ while keeping track of the parity of the input read so far — this is the [[concepts/product-construction|product]] of $M$ with the two-state parity DFA.

> [!key] Answer (b)
> $$
> \begin{aligned}
> Q' &= Q \times \{\mathtt{0}, \mathtt{1}\} & \delta'\big((q, p), \mathtt{0}\big) &= \big(\delta(q, \mathtt{0}),\ p\big)\\
> s' &= (s, \mathtt{0}) & \delta'\big((q, \mathtt{0}), \mathtt{1}\big) &= \big(\delta(q, \mathtt{1}),\ \mathtt{1}\big)\\
> A' &= A \times \{\mathtt{1}\} & \delta'\big((q, \mathtt{1}), \mathtt{1}\big) &= \big(\delta(q, \mathtt{1}),\ \mathtt{0}\big)
> \end{aligned}
> $$
> State $(q, p)$ means that $M$ is in state $q$ after reading the input $x$ read so far, and $p = \mathit{parity}(x)$. So $M'$ accepts $w$ if and only if $w \in L$ and $\mathit{parity}(w) = \mathtt{1}$.

### (c) AddParity(L) is regular

Let $\textsf{EvenParity}(L) := \{w \in L \mid \mathit{parity}(w) = \mathtt{0}\}$. This language is regular: it is accepted by the DFA $M'$ from part (b) with accepting states $A \times \{\mathtt{0}\}$ instead.

> [!key] Answer (c)
> Every string $w \in L$ becomes $\mathtt{0}w$ if $\mathit{parity}(w) = \mathtt{0}$ and $\mathtt{1}w$ if $\mathit{parity}(w) = \mathtt{1}$, so
> $$
> \textsf{AddParity}(L) = \big(\{\mathtt{0}\} \bullet \textsf{EvenParity}(L)\big) \cup \big(\{\mathtt{1}\} \bullet \textsf{OddParity}(L)\big).
> $$
> The languages $\{\mathtt{0}\}$ and $\{\mathtt{1}\}$ are regular, and regular languages are closed under concatenation and union, so $\textsf{AddParity}(L)$ is regular.

> [!exam] How this is graded
> (b) is a [[0-toolkit/02-proof-templates#6-writing-up-a-product-construction|product construction]] written formally: the [[0-toolkit/06-how-exams-are-graded#6-dfas-and-nfas|DFA rubric]] wants the pairs, the start pair, the accepting pairs and a sentence saying what a pair means — all four are in the box. (c) earns its points by *naming* the closure properties it uses ([[1-models-of-computation/03-finite-state-machines#37-closure-properties|§3.7]], [[concepts/closure-properties|closure properties]]) and by saying why $\textsf{EvenParity}(L)$ is regular; a construction of a third automaton is not needed, because results from the notes may be used without proof.

## Problem 3 — Fooling set and grammar: a string, a block of 0s, the string reversed

> [!question] Problem 3
> Let $L = \{w\mathtt{0}^nw^R \mid w \in \{\mathtt{0},\mathtt{1}\}^* \text{ and } n > 0\}$, where $w^R$ denotes the reversal of string $w$.
>
> (a) *Prove* that $L$ is not a regular language.
>
> (b) Describe a context-free grammar for $L$.

### (a) A fooling set

Consider the set $F = \mathtt{1}^* = \{\mathtt{1}^n \mid n \ge 0\}$. Let $x$ and $y$ be arbitrary distinct strings in $F$. Then $x = \mathtt{1}^i$ and $y = \mathtt{1}^j$ for some non-negative integers $i \ne j$. Let $z = \mathtt{0}\mathtt{1}^i$.

- $xz = \mathtt{1}^i\mathtt{0}\mathtt{1}^i \in L$, taking $w = \mathtt{1}^i$ and $n = 1$.
- $yz = \mathtt{1}^j\mathtt{0}\mathtt{1}^i \notin L$. Suppose $yz = w\mathtt{0}^nw^R$ for some string $w$ and some $n > 0$. Because $\#(\mathtt{0}, w^R) = \#(\mathtt{0}, w)$, the string $w\mathtt{0}^nw^R$ contains $2\cdot\#(\mathtt{0}, w) + n$ copies of `0`. But $yz$ contains exactly one `0`, so $n = 1$ and $w$ contains no `0`s; that is, $w = \mathtt{1}^k$ for some $k$. Then $\mathtt{1}^k\mathtt{0}\mathtt{1}^k = \mathtt{1}^j\mathtt{0}\mathtt{1}^i$ implies $k = j$ and $k = i$, contradicting $i \ne j$.

Thus, $z$ is a distinguishing suffix for $x$ and $y$. We conclude that $F$ is a fooling set for $L$. Because $F$ is infinite, $L$ cannot be regular.

> [!key] Answer (a)
> $F = \mathtt{1}^*$ is an infinite fooling set for $L$: for $x = \mathtt{1}^i$ and $y = \mathtt{1}^j$ with $i \ne j$, the suffix $z = \mathtt{0}\mathtt{1}^i$ gives $xz \in L$ and $yz \notin L$.

### (b) A context-free grammar

> [!key] Answer (b)
> $$
> \begin{aligned}
> S &\to \mathtt{0}S\mathtt{0} \mid \mathtt{1}S\mathtt{1} \mid Z & &L\\
> Z &\to \mathtt{0} \mid \mathtt{0}Z & &\mathtt{0}^+ = \{\mathtt{0}^n \mid n \ge 1\}
> \end{aligned}
> $$
> $Z$ generates the non-empty block $\mathtt{0}^n$ in the middle. Each production $S \to aSa$ turns a string $w\mathtt{0}^nw^R$ into $aw\mathtt{0}^nw^Ra = (aw)\mathtt{0}^n(aw)^R$, because $(aw)^R = w^Ra$; so $S$ builds $w$ and $w^R$ from the inside out.

> [!exam] How this is graded
> (a) follows the [[0-toolkit/02-proof-templates#7-fooling-set-proof|fooling-set template]] line by line, and the [[0-toolkit/06-how-exams-are-graded#7-fooling-sets|rubric]] pays for each line: the explicit infinite set, the explicit suffix, $xz \in L$ with a witness, $yz \notin L$ with an argument — here a counting argument on the number of `0`s, since "it does not look like $w\mathtt{0}^nw^R$" is not a proof. (b) is graded as a [[0-toolkit/06-how-exams-are-graded#5-regular-expressions-and-grammars|grammar]]: each nonterminal comes with the language it generates. Template: [[0-toolkit/02-proof-templates#2-writing-up-a-regular-expression-or-a-grammar|writing up a grammar]]; the same pair of tasks is worked in [[problems/fooling-set-and-grammar-for-one-language|fooling set and grammar for one language]].

## Problem 4 — Language transformations: take2skip2

> [!question] Problem 4
> For any string $w \in \{\mathtt{0},\mathtt{1}\}^*$, let $\textsf{take2skip2}(w)$ denote the subsequence of $w$ containing the symbols at positions $1, 2, 5, 6, 9, 10, \dots, 4i+1, 4i+2, \dots$. (For example, $\textsf{take2skip2}(\mathtt{0100111100011}) = \mathtt{0111001}$.) Let $L$ be an arbitrary regular language over $\{\mathtt{0},\mathtt{1}\}$.
>
> (a) *Prove* that $\textsf{Took2Added2}(L) := \{w \in \Sigma^* \mid \textsf{take2skip2}(w) \in L\}$ is regular.
>
> (b) *Prove* that $\textsf{Took2Skipped2}(L) := \{\textsf{take2skip2}(w) \mid w \in L\}$ is regular.

Throughout, $M = (Q, s, A, \delta)$ is a DFA that accepts $L$. Numbering positions from $1$, the symbol at position $p$ is *taken* if $(p-1) \bmod 4 \in \{0, 1\}$ and *skipped* otherwise. The two parts are the two kinds of [[concepts/language-transformations|transformation]] of [[1-models-of-computation/04-nondeterministic-automata#49-regular-language-transformations|§4.9]]: in (a) the input is the original string and the machine applies $\textsf{take2skip2}$ itself; in (b) the input is the result, and the machine must guess what was thrown away.

### (a) Took2Added2(L): simulate M on the taken symbols

The input to $M'$ is an arbitrary string $w$, and $M'$ simulates $M$ on $\textsf{take2skip2}(w)$ by counting positions mod 4. We construct a DFA $M' = (Q', s', A', \delta')$ as follows.

> [!key] Answer (a)
> $$
> \begin{aligned}
> Q' &= Q \times \{0, 1, 2, 3\}\\
> s' &= (s, 0)\\
> A' &= A \times \{0, 1, 2, 3\}\\
> \delta'\big((q, i), a\big) &= \big(\delta(q, a),\ i + 1\big) && \text{for } i \in \{0, 1\} \text{ and } a \in \Sigma\\
> \delta'\big((q, i), a\big) &= \big(q,\ (i + 1) \bmod 4\big) && \text{for } i \in \{2, 3\} \text{ and } a \in \Sigma
> \end{aligned}
> $$
> State $(q, i)$ means that $M'$ has read a string $x$ with $|x| \bmod 4 = i$, and $q = \delta^*(s, \textsf{take2skip2}(x))$. The next symbol is at position $|x| + 1$, so it is taken (passed to $M$) if $i \in \{0, 1\}$ and skipped if $i \in \{2, 3\}$. So $M'$ accepts $w$ if and only if $M$ accepts $\textsf{take2skip2}(w)$.

### (b) Took2Skipped2(L): guess the skipped symbols

The input to $M'$ is a string $u = \textsf{take2skip2}(w)$, and $M'$ must decide whether some such $w$ is in $L$. $M'$ rebuilds $w$ one symbol at a time while simulating $M$ on it: the taken symbols of $w$ are read from the input, and the skipped symbols are *guessed* with $\varepsilon$-transitions. We construct an [[concepts/nfa|NFA]] with $\varepsilon$-transitions $M' = (Q', s', A', \delta')$ as follows.

> [!key] Answer (b)
> $$
> \begin{aligned}
> Q' &= Q \times \{0, 1, 2, 3\}\\
> s' &= (s, 0)\\
> A' &= A \times \{0, 1, 2, 3\}\\
> \delta'\big((q, i), a\big) &= \big\{\big(\delta(q, a),\ i + 1\big)\big\} && \text{for } i \in \{0, 1\} \text{ and } a \in \Sigma\\
> \delta'\big((q, i), \varepsilon\big) &= \big\{\big(\delta(q, b),\ (i + 1) \bmod 4\big) \mid b \in \Sigma\big\} && \text{for } i \in \{2, 3\}
> \end{aligned}
> $$
> All other transitions lead to $\varnothing$: there are no input transitions out of states $(q, 2)$ and $(q, 3)$, and no $\varepsilon$-transitions out of states $(q, 0)$ and $(q, 1)$.
>
> State $(q, i)$ means that $M'$ has rebuilt a prefix $x$ of $w$ with $|x| \bmod 4 = i$ and $q = \delta^*(s, x)$, where $\textsf{take2skip2}(x)$ is the input read so far. The next symbol of $w$ is taken if $i \in \{0, 1\}$, so it must be the next input symbol; otherwise it is skipped, so $M'$ guesses it. Every state $(q, i)$ with $q \in A$ accepts, because $w$ may end at any position. So $M'$ accepts $u$ if and only if $M$ accepts some $w$ with $\textsf{take2skip2}(w) = u$.

> [!exam] How this is graded
> The [[0-toolkit/06-how-exams-are-graded#8-language-transformations|transformation rubric]]: 2 points for a formal description built from an *arbitrary* DFA $M$ — saying "DFA" in (a) and "NFA with $\varepsilon$-transitions" in (b), and listing exactly which $\varepsilon$-transitions exist; 2 for the English meaning of a state and of the accepting states; 6 for correctness (states, start, accepting, transitions). The accepting set $A \times \{0,1,2,3\}$ is the detail most worth a second look: in both parts $w$ may end at any position, so the counter's value at the end does not matter. Template: [[0-toolkit/02-proof-templates#9-language-transformation|language transformation]]; a worked pair of the same two kinds: [[problems/two-language-transformations|insert and delete a 1]].

## Problem 5 — A DFA and a regular expression for each language

> [!question] Problem 5
> For each of the following languages $L$ over the alphabet $\{\mathtt{0},\mathtt{1}\}$, describe a DFA that accepts $L$ **and** give a regular expression that represents $L$.
>
> (a) All strings in which every run of `1`s has even length and every run of `0`s has odd length.
>
> (b) All strings in $\mathtt{0}^*\mathtt{1}\mathtt{0}^*$ whose length is a multiple of 3.

### (a) Runs of 1s even, runs of 0s odd

Each state records the symbol and the parity of the length (so far) of the last run; every earlier run has the correct parity.

<!-- fig:exam-mt1p3-runs-dfa -->
<figure class="cs-fig"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 276" width="640" height="276" role="img" style="font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-size:14px"><title>four-state DFA: E,1 (start, accepting) and O,1 exchange on 1; E,1 goes to O,0 on 0; O,0 (accepting) goes to O,1 on 1 and exchanges with E,0 on 0</title><defs><marker id="ARR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs><path d="M103.8,59 Q240,42 376.7,59.1" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="240.7" y="39.6" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">1</text><path d="M379.2,64.6 Q240,82 106.3,65.3" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="240.7" y="84.4" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">1</text><path d="M97,79 L221.3,203.3" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="152.2" y="149.8" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">0</text><path d="M257,205 L383.4,78.6" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="328.8" y="148.7" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">1</text><path d="M263.8,219 Q400,202 536.7,219.1" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="400.7" y="199.6" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">0</text><path d="M539.2,224.6 Q400,242 266.3,225.3" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="400.7" y="244.4" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">0</text><line x1="30" y1="62" x2="53.5" y2="62" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" marker-end="url(#ARR)"/><circle cx="80" cy="62" r="25" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><circle cx="80" cy="62" r="21" fill="var(--accent)" fill-opacity="0.1" stroke="currentColor" stroke-width="1.6"/><text x="80" y="63" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">E,1</text><circle cx="400" cy="62" r="21" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="400" y="63" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">O,1</text><circle cx="240" cy="222" r="25" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><circle cx="240" cy="222" r="21" fill="var(--accent)" fill-opacity="0.1" stroke="currentColor" stroke-width="1.6"/><text x="240" y="223" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">O,0</text><circle cx="560" cy="222" r="21" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="560" y="223" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">E,0</text></svg><figcaption><strong>Every run of 1s even, every run of 0s odd.</strong> A state names the symbol of the current run and the parity (E/O) of its length so far; every earlier run already has the right parity. E,1 is also the start state (the empty input has no runs). The two missing transitions — a 0 in O,1 and a 1 in E,0 — end a run of the wrong parity and lead to a hidden dump state.</figcaption></figure>

- E,`1` — the input is empty or ends with a run of `1`s of even length.
- O,`1` — the input ends with a run of `1`s of odd length.
- O,`0` — the input ends with a run of `0`s of odd length.
- E,`0` — the input ends with a run of `0`s of even length.

The missing transitions (reading `0` in state O,`1` or `1` in state E,`0`) end a run of the wrong parity, so they lead to a hidden dump state.

> [!key] Regular expression (a)
> $$
> (\mathtt{11})^*\,\big(\mathtt{0}(\mathtt{00})^*\,\mathtt{11}(\mathtt{11})^*\big)^*\,\big(\varepsilon + \mathtt{0}(\mathtt{00})^*\big)
> $$
> Runs of `0`s and `1`s alternate: an optional even-length run of `1`s, then any number of pairs (odd-length run of `0`s, even-length run of `1`s), then an optional final odd-length run of `0`s.

### (b) One 1, and length a multiple of 3

The DFA counts the length mod 3 and remembers whether it has seen the `1`.

<!-- fig:exam-mt1p3-mod3-dfa -->
<figure class="cs-fig"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 300" width="500" height="300" role="img" style="font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-size:14px"><title>six-state DFA in two rows of three: N0, N1, N2 cycle on 0; Y1, Y2, Y0 cycle on 0; vertical 1-edges from N0 to Y1, N1 to Y2 and N2 to Y0; Y0 is accepting</title><defs><marker id="ARR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs><path d="M100,92 L227.5,92" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="165" y="81" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">0</text><path d="M270,92 L397.5,92" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="335" y="81" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">0</text><path d="M402.1,83.1 Q250,8 100.2,82" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="250" y="35.6" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">0</text><path d="M100,212 L227.5,212" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="165" y="201" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">0</text><path d="M270,212 L394.5,212" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="333.5" y="201" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">0</text><path d="M399.4,222.2 Q250,296 100.2,222" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="249.3" y="268.8" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">0</text><path d="M80,112 L80,189.5" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="69" y="152" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">1</text><path d="M250,112 L250,189.5" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="239" y="152" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">1</text><path d="M420,112 L420,186.5" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="409" y="150.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">1</text><line x1="34" y1="92" x2="57.5" y2="92" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" marker-end="url(#ARR)"/><circle cx="80" cy="92" r="20" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="80" y="93" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">N<tspan dy="4" style="font-size:10px">0</tspan></text><circle cx="80" cy="212" r="20" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="80" y="213" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">Y<tspan dy="4" style="font-size:10px">1</tspan></text><circle cx="250" cy="92" r="20" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="250" y="93" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">N<tspan dy="4" style="font-size:10px">1</tspan></text><circle cx="250" cy="212" r="20" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="250" y="213" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">Y<tspan dy="4" style="font-size:10px">2</tspan></text><circle cx="420" cy="92" r="20" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="420" y="93" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">N<tspan dy="4" style="font-size:10px">2</tspan></text><circle cx="420" cy="212" r="24" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><circle cx="420" cy="212" r="20" fill="var(--accent)" fill-opacity="0.1" stroke="currentColor" stroke-width="1.6"/><text x="420" y="213" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">Y<tspan dy="4" style="font-size:10px">0</tspan></text></svg><figcaption><strong>One 1, and length a multiple of 3.</strong> The subscript is the length of the input so far, mod 3. Top row N: no 1 read yet; bottom row Y: exactly one 1 read. Each 0 moves one step along its row (and wraps around after 2); the 1 drops from N<sub><i>i</i></sub> to Y<sub><i>i</i>+1</sub>. Only Y<sub>0</sub> accepts. A second 1 (missing transitions out of the Y row) leads to a hidden dump state.</figcaption></figure>

- $N_i$ — no `1` has been read yet, and the length of the input so far is $i \bmod 3$.
- $Y_i$ — exactly one `1` has been read, and the length of the input so far is $i \bmod 3$.

The missing transitions (reading `1` in any state $Y_i$) lead to a hidden dump state, because the input then contains two `1`s.

> [!key] Regular expression (b)
> $$
> (\mathtt{000})^*\,(\mathtt{100} + \mathtt{010} + \mathtt{001})\,(\mathtt{000})^*
> $$
> A string $\mathtt{0}^a\mathtt{1}\mathtt{0}^b$ has length $a + b + 1$, which is a multiple of 3 if and only if $(a \bmod 3, b \bmod 3)$ is $(0, 2)$, $(1, 1)$, or $(2, 0)$; the middle term covers these three cases, and each $(\mathtt{000})^*$ adds the remaining multiples of 3 on its side.

> [!exam] How this is graded
> No proof is asked for, but the [[0-toolkit/06-how-exams-are-graded#6-dfas-and-nfas|DFA rubric]] still wants a complete description: a start arrow, double circles, **mnemonic state names with a sentence each**, and a sentence about the dump state when it is left out of the drawing — leaving it out silently makes the machine an NFA, worth half credit. The [[0-toolkit/06-how-exams-are-graded#5-regular-expressions-and-grammars|regular-expression rubric]] takes 2 points for one wrong string (test $\varepsilon$: it belongs to (a) and not to (b)) and 8 for infinitely many. Templates: [[0-toolkit/02-proof-templates#5-describing-a-dfa|describing a DFA]], [[0-toolkit/02-proof-templates#2-writing-up-a-regular-expression-or-a-grammar|writing up a regular expression]]; method: [[1-models-of-computation/03-finite-state-machines#35-designing-dfas-dfas-are-algorithms|§3.5]], [[1-models-of-computation/02-regular-languages#designing-a-regular-expression|§2.3]]; the same task worked in [[problems/regular-expression-and-dfa-for-one-language|01 exactly twice]].

### Sources for this page
The problems are paraphrased from Midterm 1 practice test 3 of CS/ECE 374 A (Fall 2026); the solutions are the student's own, converted from the earlier write-up with the same constructions and wording. Checked by `tools/checks/exams_mt1.py` (section "practice test 3"): every true/false answer that rests on an example (the fooling set in 1(c), $L^* = L$ in 1(d), $\varnothing^* = \{\varepsilon\}$, the complement DFA, the unreachable accepting states, the one-accepting-state NFA, the Myhill–Nerode bound in 1(j)); the recursive parity function against the count of `1`s; the constructions of 2(b), 2(c), 4(a) and 4(b) as functions of an arbitrary DFA, compared with the definitions of $\textsf{OddParity}$, $\textsf{AddParity}$, $\textsf{Took2Added2}$ and $\textsf{Took2Skipped2}$ on random DFAs with 1–4 states; the fooling set of 3(a) for all $i \ne j \le 8$; the grammar of 3(b) against the definition of $L$ up to length 10; and both DFAs and both regular expressions of Problem 5 against the languages' definitions, by exact equivalence.
