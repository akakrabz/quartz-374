---
title: "Midterm 1 practice test 2 — solutions"
description: "Five problems in the Midterm 1 format: two transformations built on compress0s (halving every run of 0s), a regular expression, DFA and 375-state lower bound for 'at least 374 consecutive 1s', two inductions on the run-doubling function Bond, a fooling set and a grammar for 0^a 1^b 0^c with two equal exponents, and ten true/false statements."
tags: [exam, midterm-1, regular, context-free]
---

*Midterm 1 practice test 2 · CS/ECE 374 A, Fall 2026 · five problems in the exam's format · the other tests: [[3-homework-and-exams/midterm-1-practice-1|test 1]], [[3-homework-and-exams/midterm-1-practice-3|test 3]] · how it is graded: [[0-toolkit/06-how-exams-are-graded|rubrics]]*

> [!abstract] In one breath
> **Problem 1** transforms a regular language through $\textsf{compress0s}$, which halves every run of 0s: $\textsf{Decompressed}(L)$ is a DFA that *simulates* $M$ on the compressed input (one bit of memory: the parity of the current run), and $\textsf{Compressed}(L)$ is an NFA that *guesses* the original run lengths by feeding $M$ one or two 0s per input 0. **Problem 2** asks for a regular expression, a DFA and a lower bound for "at least 374 consecutive 1s": the DFA counts the current run up to 374, and the fooling set $\{\mathtt{1}^i \mid 0\le i\le 374\}$ shows that its 375 states are necessary. **Problem 3** is two inductions on $\textsf{Bond}$, which doubles every 0: a length inequality and the fact that $\textsf{Bond}$ respects concatenation. **Problem 4** proves $\{\mathtt{0}^a\mathtt{1}^b\mathtt{0}^c \mid a = b \text{ or } a = c \text{ or } b = c\}$ non-regular with the fooling set $\mathtt{0}^+$ and writes it as a union of three grammars. **Problem 5** is ten true/false statements on implications, fooling sets, grammars, one-accepting-state DFAs, $\varepsilon$-transitions, bitwise complements and closure.

## Problem 1 — Language transformations: compress0s

> [!question] Problem 1
> Let $\textsf{compress0s}(w)$ be the string formed by compressing every run of 0s in $w$ by half: every run of $2n$ 0s becomes $n$ 0s, and every run of $2n+1$ 0s becomes $n+1$ 0s. (For example, $\textsf{compress0s}(\mathtt{00000110001}) = \mathtt{00011001}$.) Let $L$ be an arbitrary regular language. *Prove* that the following languages are regular.
>
> Throughout, $M = (Q, s, A, \delta)$ is a DFA that accepts $L$. In other words, $\textsf{compress0s}$ replaces each run of $k$ 0s by $\lceil k/2\rceil$ 0s and leaves every 1 alone.
>
> (a) $\textsf{Decompressed}(L) := \{w\in\Sigma^* \mid \textsf{compress0s}(w)\in L\}$
>
> (b) $\textsf{Compressed}(L) := \{\textsf{compress0s}(w) \mid w\in L\}$

*Template: [[0-toolkit/02-proof-templates#9-language-transformation|language transformation]] · concepts: [[concepts/language-transformations]], [[concepts/nfa]] · the two kinds of transformation: [[1-models-of-computation/04-nondeterministic-automata#49-regular-language-transformations|§4.9]]*

### (a) Decompressed(L): simulate M on the compressed input

The input to $M'$ is an arbitrary string $w$, and $M'$ simulates $M$ on $\textsf{compress0s}(w)$. To turn each run of $k$ 0s into $\lceil k/2\rceil$ 0s, $M'$ passes the 1st, 3rd, 5th, … 0 of each run to $M$ and skips the 2nd, 4th, 6th, … one.

> [!key] Answer (a)
> We construct a DFA $M' = (Q', s', A', \delta')$ as follows:
> $$
> \begin{aligned}
> Q' &= Q\times\{0, 1\} &\qquad \delta'\big((q, 0), \mathtt{0}\big) &= \big(\delta(q, \mathtt{0}), 1\big)\\
> s' &= (s, 0) &\qquad \delta'\big((q, 1), \mathtt{0}\big) &= (q, 0)\\
> A' &= A\times\{0, 1\} &\qquad \delta'\big((q, p), \mathtt{1}\big) &= \big(\delta(q, \mathtt{1}), 0\big)
> \end{aligned}
> $$
> State $(q, p)$ means that $M$ is in state $q$ after reading $\textsf{compress0s}(x)$, where $x$ is the input read so far, and $p$ is the parity of the length of the run of 0s at the end of $x$ ($p = 0$ if $x$ is empty or ends with 1).

Reading a 0 when $p = 0$ lengthens $\textsf{compress0s}(x)$ by one 0; reading a 0 when $p = 1$ does not change it; every 1 is copied to $M$. So $M'$ accepts $w$ if and only if $M$ accepts $\textsf{compress0s}(w)$.

### (b) Compressed(L): guess the original run lengths

The input to $M'$ is a string $u = \textsf{compress0s}(w)$, and $M'$ must decide whether some such $w$ is in $L$. A run of $m$ 0s in $u$ came from a run of either $2m-1$ or $2m$ 0s in $w$ (these are the only $k$ with $\lceil k/2\rceil = m$), and $w$ and $u$ have the same 1s. So $M'$ *guesses* $w$: for the first 0 of each run of 0s in $u$ it feeds either `0` or `00` to $M$, and for every later 0 of the same run it feeds `00`. This turns a run of $m$ 0s into exactly $2m-1$ or $2m$ 0s.

> [!key] Answer (b)
> We construct an NFA without $\varepsilon$-transitions $M' = (Q', s', A', \delta')$ as follows:
> $$
> \begin{aligned}
> Q' &= Q\times\{\textsf{False}, \textsf{True}\}\\
> s' &= (s, \textsf{False})\\
> A' &= A\times\{\textsf{False}, \textsf{True}\}\\[0.5ex]
> \delta'\big((q, \textsf{False}), \mathtt{0}\big) &= \Big\{\big(\delta(q, \mathtt{0}), \textsf{True}\big),\ \big(\delta(\delta(q, \mathtt{0}), \mathtt{0}), \textsf{True}\big)\Big\}\\
> \delta'\big((q, \textsf{True}), \mathtt{0}\big) &= \Big\{\big(\delta(\delta(q, \mathtt{0}), \mathtt{0}), \textsf{True}\big)\Big\}\\
> \delta'\big((q, b), \mathtt{1}\big) &= \Big\{\big(\delta(q, \mathtt{1}), \textsf{False}\big)\Big\}\qquad\text{for } b\in\{\textsf{False}, \textsf{True}\}
> \end{aligned}
> $$
> State $(q, b)$ means that $M$ is in state $q$ after reading the guessed prefix of $w$, and $b = \textsf{True}$ if and only if the last input symbol was 0 (so the next 0 is not the first of its run).

So $M'$ accepts $u$ if and only if $M$ accepts some $w$ with $\textsf{compress0s}(w) = u$.

> [!exam] How this is graded
> Each part out of 10: **2** for a formal, complete description built from an *arbitrary* DFA $M$ (say DFA or NFA, and list the $\varepsilon$-transitions — here there are none), **2** for the English meaning of the states and of the accepting states, **6** for correctness (states, start, accepting states, transitions). The two parts are the two kinds of transformation: (a) *simulates* $M$ on $f(w)$, (b) *guesses* $w$ — mixing them up is the classic deduction. Rubric: [[0-toolkit/06-how-exams-are-graded#8-language-transformations|§8]]; a worked problem of the same type: [[problems/two-language-transformations|insert and delete a 1]].

## Problem 2 — Regex, DFA, and a lower bound: 374 consecutive 1s

> [!question] Problem 2
> Let $L$ be the language of all strings over $\{\mathtt{0}, \mathtt{1}\}$ that contain at least 374 consecutive 1s.
>
> (a) Give a regular expression that matches $L$.
>
> (b) Describe a DFA whose language is $L$.
>
> (c) *Prove* that any DFA whose language is $L$ must have at least 375 states.

*Templates: [[0-toolkit/02-proof-templates#2-writing-up-a-regular-expression-or-a-grammar|regular expression]], [[0-toolkit/02-proof-templates#5-describing-a-dfa|describing a DFA]], [[0-toolkit/02-proof-templates#7-fooling-set-proof|fooling set]] · concepts: [[concepts/regular-expressions]], [[concepts/dfa]], [[concepts/fooling-sets]]*

### (a) A regular expression

> [!key] Answer (a)
> $(\mathtt{0} + \mathtt{1})^*\,\mathtt{1}^{374}\,(\mathtt{0} + \mathtt{1})^*$: anything, then 374 consecutive 1s, then anything.

($\mathtt{1}^{374}$ is shorthand for 374 copies of $\mathtt{1}$ written out — exponents are not part of the regular-expression syntax, so say so.)

### (b) A DFA

> [!key] Answer (b)
> Let $M = (Q, s, A, \delta)$, where
> $$
> \begin{aligned}
> Q &= \{0, 1, 2, \dots, 374\} &\qquad \delta(i, \mathtt{1}) &= i + 1 &&\quad\text{for all } i < 374\\
> s &= 0 &\qquad \delta(i, \mathtt{0}) &= 0 &&\quad\text{for all } i < 374\\
> A &= \{374\} &\qquad \delta(374, a) &= 374 &&\quad\text{for all } a\in\Sigma
> \end{aligned}
> $$
> State $i < 374$ means the input does not contain $\mathtt{1}^{374}$ yet and ends with exactly $i$ consecutive 1s. State $374$ means the input contains $\mathtt{1}^{374}$.

<!-- fig:exam-mt1p2-run-of-ones -->
<figure class="cs-fig"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 180" width="640" height="180" role="img" style="font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-size:14px"><title>a chain of states 0, 1, 2, ..., 373, 374 joined by 1-edges, with 0-edges back to state 0 and an absorbing accepting state 374</title><defs><marker id="ARR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs><path d="M286,68 L316,68" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="4 4"/><text x="340" y="69" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:18px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">⋯</text><path d="M364,68 L393.5,68" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)" stroke-dasharray="4 4"/><text x="340" y="48" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">1</text><path d="M51.1,51.2 C25.4,13 94.6,13 70.1,49" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="60" y="6.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">0</text><path d="M84,68 L133.5,68" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="110" y="57" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">1</text><path d="M184,68 L233.5,68" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="210" y="57" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">1</text><path d="M444,68 L510.5,68" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="478.5" y="57" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">1</text><path d="M531.1,51.2 C505.4,13 574.6,13 550.1,49" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="540" y="6.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">0,1</text><path d="M136.2,87 Q110,108 85.7,88.6" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="110" y="107.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">0</text><path d="M236,83.4 Q160,132 86.1,84.7" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="160" y="117.7" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">0</text><path d="M396,80.3 Q240,160 86.2,81.4" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="240" y="130.1" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">0</text><line x1="10" y1="68" x2="33.5" y2="68" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" marker-end="url(#ARR)"/><rect x="36" y="49" width="48" height="38" rx="19" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="60" y="69" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">0</text><rect x="136" y="49" width="48" height="38" rx="19" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="160" y="69" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">1</text><rect x="236" y="49" width="48" height="38" rx="19" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="260" y="69" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">2</text><rect x="396" y="49" width="48" height="38" rx="19" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="420" y="69" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">373</text><rect x="512" y="45" width="56" height="46" rx="23" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><rect x="516" y="49" width="48" height="38" rx="19" fill="var(--accent)" fill-opacity="0.1" stroke="currentColor" stroke-width="1.6"/><text x="540" y="69" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">374</text></svg><figcaption><strong>At least 374 consecutive 1s.</strong> State <i>i</i> &lt; 374 means the input has no run of 374 1s yet and ends with exactly <i>i</i> consecutive 1s; a 1 moves one step right, a 0 resets to state 0. State 374 means a run of 374 1s has been seen, and it absorbs everything. 375 states, and Problem 2(c) shows no DFA does better.</figcaption></figure>

### (c) Every DFA for L has at least 375 states

> [!key] Lemma
> *If $L$ has a fooling set $F$ of size $\ell$, then every DFA that accepts $L$ has at least $\ell$ states.*
>
> **Proof.** Let $M = (Q, s, A, \delta)$ be a DFA that accepts $L$, and suppose $|Q| < \ell$. By the pigeonhole principle, there are distinct strings $x, y\in F$ with $\delta^*(s, x) = \delta^*(s, y)$. Because $F$ is a fooling set, some suffix $z$ has exactly one of $xz$ and $yz$ in $L$. But $\delta^*(s, xz) = \delta^*(\delta^*(s, x), z) = \delta^*(\delta^*(s, y), z) = \delta^*(s, yz)$, so $M$ accepts both $xz$ and $yz$ or neither; this contradicts $L(M) = L$. $\square$

This is the finite version of the fooling-set argument of [[1-models-of-computation/03-finite-state-machines#38-proving-a-language-is-not-regular|§3.8]]; the same pigeonhole step, with an infinite $F$, is what makes a language non-regular.

Now consider the set $F = \{\mathtt{1}^i \mid 0\le i\le 374\}$, which contains 375 strings. Let $x$ and $y$ be arbitrary distinct strings in $F$. Then $x = \mathtt{1}^i$ and $y = \mathtt{1}^j$ for some integers $0\le i < j\le 374$, without loss of generality. Let $z = \mathtt{1}^{374-j}$.

- $yz = \mathtt{1}^{374}\in L$.
- $xz = \mathtt{1}^{374-(j-i)}\notin L$, because it has fewer than 374 symbols.

Thus, $z$ distinguishes $x$ and $y$, so $F$ is a fooling set for $L$ of size 375. By the lemma, every DFA for $L$ has at least 375 states.

> [!exam] How this is graded
> (a) **2** for syntax, **8** for correctness — one missing or extra string costs 2, infinitely many cost all 8 ([[0-toolkit/06-how-exams-are-graded#5-regular-expressions-and-grammars|§5]]). (b) **2** for a complete, unambiguous description, **2** for mnemonic state names (here each state *is* its meaning: the current run length), **6** for correctness; an NFA where a DFA was asked earns half ([[0-toolkit/06-how-exams-are-graded#6-dfas-and-nfas|§6]]). (c) is a fooling-set proof with a *finite* set: the four-point structure of [[0-toolkit/06-how-exams-are-graded#7-fooling-sets|§7]] applies (explicit set, explicit suffix for arbitrary distinct $x$, $y$, one half in, one half out), and the lemma must be stated or cited, since the course's fooling-set lemma is usually quoted only for infinite sets.

## Problem 3 — Induction: Bond doubles every 0

> [!question] Problem 3
> Consider the following recursive function, which doubles the length of every run of 0s:
> $$
> \textsf{Bond}(w) := \begin{cases}
> \varepsilon & \text{if } w = \varepsilon\\
> \mathtt{00}\cdot\textsf{Bond}(x) & \text{if } w = \mathtt{0}\cdot x \text{ for some string } x\\
> \mathtt{1}\cdot\textsf{Bond}(x) & \text{if } w = \mathtt{1}\cdot x \text{ for some string } x
> \end{cases}
> $$
> (a) *Prove* that $|\textsf{Bond}(w)|\ge|w|$ for all strings $w$.
>
> (b) *Prove* that $\textsf{Bond}(x\bullet y) = \textsf{Bond}(x)\bullet\textsf{Bond}(y)$ for all strings $x$ and $y$.

*Template: [[0-toolkit/02-proof-templates#1-induction-on-strings|induction on strings]] · concepts: [[concepts/induction-on-strings]], [[concepts/strings]] · the model proofs: [[1-models-of-computation/01-strings#13-induction-on-strings|§1.3]]*

### (a) Bond never shortens a string

Let $w$ be an arbitrary string. Assume that $|\textsf{Bond}(x)|\ge|x|$ for every string $x$ such that $|x| < |w|$. There are three cases to consider.

- If $w = \varepsilon$, then $|\textsf{Bond}(w)| = |\varepsilon| = 0 = |w|$.
- If $w = \mathtt{0}x$ for some string $x$, then
  $$
  \begin{aligned}
  |\textsf{Bond}(w)| &= \big|\mathtt{0}\cdot(\mathtt{0}\cdot\textsf{Bond}(x))\big| && \text{by definition of } \textsf{Bond}\\
  &= 2 + |\textsf{Bond}(x)| && \text{by definition of } |\cdot| \text{ (twice)}\\
  &\ge 2 + |x| && \text{by the induction hypothesis}\\
  &> 1 + |x| = |w| && \text{by definition of } |\cdot|
  \end{aligned}
  $$
- If $w = \mathtt{1}x$ for some string $x$, then
  $$
  \begin{aligned}
  |\textsf{Bond}(w)| &= |\mathtt{1}\cdot\textsf{Bond}(x)| && \text{by definition of } \textsf{Bond}\\
  &= 1 + |\textsf{Bond}(x)| && \text{by definition of } |\cdot|\\
  &\ge 1 + |x| = |w| && \text{by the induction hypothesis}
  \end{aligned}
  $$

The induction hypothesis applies because $|x| = |w| - 1 < |w|$. In every case, $|\textsf{Bond}(w)|\ge|w|$. $\blacksquare$

### (b) Bond respects concatenation

Induct on the **left** argument $x$, because $\bullet$ takes its left argument apart; $y$ stays fixed throughout.

Let $x$ and $y$ be arbitrary strings. Assume that $\textsf{Bond}(z\bullet y) = \textsf{Bond}(z)\bullet\textsf{Bond}(y)$ for every string $z$ such that $|z| < |x|$. There are three cases to consider.

- If $x = \varepsilon$, then
  $$
  \begin{aligned}
  \textsf{Bond}(x\bullet y) &= \textsf{Bond}(y) && \text{because } \varepsilon\bullet y = y\\
  &= \varepsilon\bullet\textsf{Bond}(y) && \text{by definition of } {\bullet}\\
  &= \textsf{Bond}(x)\bullet\textsf{Bond}(y) && \text{because } \textsf{Bond}(\varepsilon) = \varepsilon
  \end{aligned}
  $$
- If $x = \mathtt{0}z$ for some string $z$, then
  $$
  \begin{aligned}
  \textsf{Bond}(x\bullet y) &= \textsf{Bond}\big(\mathtt{0}\cdot(z\bullet y)\big) && \text{by definition of } {\bullet}\\
  &= \mathtt{00}\cdot\textsf{Bond}(z\bullet y) && \text{by definition of } \textsf{Bond}\\
  &= \mathtt{00}\cdot\big(\textsf{Bond}(z)\bullet\textsf{Bond}(y)\big) && \text{by the induction hypothesis}\\
  &= \big(\mathtt{00}\cdot\textsf{Bond}(z)\big)\bullet\textsf{Bond}(y) && \text{by definition of } {\bullet} \text{ (twice)}\\
  &= \textsf{Bond}(x)\bullet\textsf{Bond}(y) && \text{by definition of } \textsf{Bond}
  \end{aligned}
  $$
- If $x = \mathtt{1}z$ for some string $z$, then
  $$
  \begin{aligned}
  \textsf{Bond}(x\bullet y) &= \textsf{Bond}\big(\mathtt{1}\cdot(z\bullet y)\big) && \text{by definition of } {\bullet}\\
  &= \mathtt{1}\cdot\textsf{Bond}(z\bullet y) && \text{by definition of } \textsf{Bond}\\
  &= \mathtt{1}\cdot\big(\textsf{Bond}(z)\bullet\textsf{Bond}(y)\big) && \text{by the induction hypothesis}\\
  &= \big(\mathtt{1}\cdot\textsf{Bond}(z)\big)\bullet\textsf{Bond}(y) && \text{by definition of } {\bullet}\\
  &= \textsf{Bond}(x)\bullet\textsf{Bond}(y) && \text{by definition of } \textsf{Bond}
  \end{aligned}
  $$

The induction hypothesis applies because $|z| = |x| - 1 < |x|$. In every case, $\textsf{Bond}(x\bullet y) = \textsf{Bond}(x)\bullet\textsf{Bond}(y)$. $\blacksquare$

> [!exam] How this is graded
> Out of 10 per part: **1** for starting from an arbitrary string, **2** for an explicit *strong* hypothesis, **2** for exhaustive cases ($\varepsilon$, $\mathtt{0}x$, $\mathtt{1}x$ — the three cases of the definition), **1** for the base case, **2** for using the hypothesis correctly (on something shorter, and saying why it is shorter), **2** for the rest. Every line of the chains above carries its reason; "by definition of $\bullet$ (twice)" is the kind of detail the graders look for. Rubric: [[0-toolkit/06-how-exams-are-graded#4-induction|§4]]; worked problem of the same type: [[problems/induction-on-a-recursive-string-function|sorting a string]].

## Problem 4 — Not regular, but context-free: two equal exponents

> [!question] Problem 4
> Let $L$ be the language $\{\mathtt{0}^a\mathtt{1}^b\mathtt{0}^c \mid a = b \text{ or } a = c \text{ or } b = c\}$.
>
> (a) *Prove* that $L$ is not a regular language.
>
> (b) Describe a context-free grammar for $L$.

*Templates: [[0-toolkit/02-proof-templates#7-fooling-set-proof|fooling set]], [[0-toolkit/02-proof-templates#2-writing-up-a-regular-expression-or-a-grammar|writing up a grammar]] · concepts: [[concepts/fooling-sets]], [[concepts/context-free-grammars]] · worked problem of the same type: [[problems/fooling-set-and-grammar-for-one-language|fooling set and grammar]]*

### (a) A fooling set

> [!key] Answer (a)
> Consider the set $F = \mathtt{0}^+ = \{\mathtt{0}^n \mid n\ge1\}$. Let $x$ and $y$ be arbitrary distinct strings in $F$. Then $x = \mathtt{0}^i$ and $y = \mathtt{0}^j$ for some positive integers $i\ne j$. Let $z = \mathtt{1}^i$.
> - $xz = \mathtt{0}^i\mathtt{1}^i\in L$, with $a = b = i$ and $c = 0$.
> - $yz = \mathtt{0}^j\mathtt{1}^i\notin L$. Because $i\ge1$, the only way to write $yz$ as $\mathtt{0}^a\mathtt{1}^b\mathtt{0}^c$ is with $a = j$, $b = i$, and $c = 0$. But $a\ne b$ because $j\ne i$, $a\ne c$ because $j\ge1$, and $b\ne c$ because $i\ge1$.
>
> Thus, $z$ is a distinguishing suffix for $x$ and $y$. We conclude that $F$ is a fooling set for $L$. Because $F$ is infinite, $L$ cannot be regular. $\blacksquare$

**Why $F$ starts at $n = 1$.** With $x = \varepsilon$ (that is, $i = 0$) the suffix $z = \mathtt{1}^0 = \varepsilon$ gives $yz = \mathtt{0}^j$, which **is** in $L$ (with $b = c = 0$), so $\varepsilon$ cannot be distinguished this way. That is why $F = \mathtt{0}^+$ rather than $\mathtt{0}^*$, and why the "not in $L$" half uses both $i\ge1$ and $j\ge1$: a three-way "or" leaves three ways for $yz$ to sneak into $L$, and each must be ruled out.

### (b) A grammar: a union of three languages

$L$ is the union of three simpler languages, one for each equality.

> [!key] Answer (b)
> $$
> \begin{aligned}
> S &\to EZ \mid M \mid ZF &&\qquad L\\
> E &\to \varepsilon \mid \mathtt{0}E\mathtt{1} &&\qquad \{\mathtt{0}^n\mathtt{1}^n \mid n\ge0\}\\
> F &\to \varepsilon \mid \mathtt{1}F\mathtt{0} &&\qquad \{\mathtt{1}^n\mathtt{0}^n \mid n\ge0\}\\
> M &\to \mathtt{0}M\mathtt{0} \mid U &&\qquad \{\mathtt{0}^n\mathtt{1}^m\mathtt{0}^n \mid m, n\ge0\}\\
> U &\to \varepsilon \mid \mathtt{1}U &&\qquad \mathtt{1}^*\\
> Z &\to \varepsilon \mid \mathtt{0}Z &&\qquad \mathtt{0}^*
> \end{aligned}
> $$
> $EZ$ generates the strings with $a = b$, $M$ those with $a = c$, and $ZF$ those with $b = c$.

The third column is the self-contained description of each nonterminal's language that a homework write-up needs. The grammar is ambiguous — $\varepsilon$ is generated through $EZ$, through $M$ and through $ZF$, and `0` through $EZ$ (as $\mathtt{0}^0\mathtt{1}^0\mathtt{0}^1$, so $a = b$) and through $ZF$ (as $\mathtt{0}^1\mathtt{1}^0\mathtt{0}^0$, so $b = c$) — but ambiguity is not penalized.

> [!exam] How this is graded
> (a) **4** for an explicit infinite set that really is a fooling set, **2** for an explicit suffix for arbitrary distinct $x, y$, **2** for the half in $L$, **2** for the half out of $L$ — the last one is where this problem bites, because "$\mathtt{0}^j\mathtt{1}^i\notin L$" needs all three inequalities ([[0-toolkit/06-how-exams-are-graded#7-fooling-sets|§7]]). (b) **2** for syntax, **8** for correctness; a union with a forgotten case loses infinitely many strings and all 8 ([[0-toolkit/06-how-exams-are-graded#5-regular-expressions-and-grammars|§5]]).

## Problem 5 — True or false

> [!question] Problem 5
> For each statement below, check "True" if the statement is always true and check "False" otherwise, and give a brief (one short sentence) explanation of your answer. For any string $w\in(\mathtt{0}+\mathtt{1})^*$, let $w^c$ denote the *bitwise complement* of $w$, obtained by flipping every 0 in $w$ to a 1, and vice versa.

*Concepts touched: [[concepts/fooling-sets]], [[concepts/context-free-grammars]], [[concepts/dfa]], [[concepts/subset-construction]], [[concepts/closure-properties]] · the closure table: [[0-toolkit/03-the-big-picture|the big picture]]*

**(a)** *If $2 + 2 = 5$, then zero is odd.* \
**True.** The hypothesis is false, so the implication is (vacuously) true.

**(b)** *$\{\mathtt{0}^n\mathtt{1} \mid n > 0\}$ is the only infinite fooling set for the language $\{\mathtt{0}^n\mathtt{1}\mathtt{0}^n \mid n > 0\}$.* \
**False.** For example, $\{\mathtt{0}^n \mid n > 0\}$ is another infinite fooling set: the suffix $\mathtt{1}\mathtt{0}^i$ distinguishes $\mathtt{0}^i$ from $\mathtt{0}^j$.

**(c)** *$\{\mathtt{0}^n\mathtt{1}\mathtt{0}^n \mid n > 0\}$ is a context-free language.* \
**True.** It is generated by the grammar $S\to\mathtt{010}\mid\mathtt{0}S\mathtt{0}$.

**(d)** *The context-free grammar $S\to\mathtt{00}S\mid S\mathtt{11}\mid\mathtt{01}$ generates the language $\{\mathtt{0}^n\mathtt{1}^n \mid n\ge0\}$.* \
**False.** It generates $\mathtt{0001}$ (via $S\rightsquigarrow\mathtt{00}S\rightsquigarrow\mathtt{0001}$), which is not in that language; it also cannot generate $\varepsilon$.

**(e)** *Every regular language is recognized by a DFA with exactly one accepting state.* \
**False.** No such DFA accepts $\{\varepsilon, \mathtt{0}\}$: accepting $\varepsilon$ forces the start state $s$ to be the accepting state, and then accepting `0` forces $\delta(s, \mathtt{0}) = s$, so `00` would be accepted too.

**(f)** *Any language that can be decided by an NFA with $\varepsilon$-transitions can also be decided by an NFA without $\varepsilon$-transitions.* \
**True.** The subset construction turns the NFA into an equivalent DFA, which is an NFA without $\varepsilon$-transitions.

**(g)** *If $L$ is a regular language over $\{\mathtt{0}, \mathtt{1}\}$, then $\{xy^c \mid x, y\in L\}$ is also regular.* \
**True.** Swapping the 0- and 1-transitions of a DFA for $L$ gives a DFA for $\{y^c \mid y\in L\}$, and the given language is the concatenation of $L$ with that regular language.

**(h)** *If $L$ is a regular language over $\{\mathtt{0}, \mathtt{1}\}$, then $\{ww^c \mid w\in L\}$ is also regular.* \
**False.** For the regular language $L = \mathtt{0}^*$, we get $\{\mathtt{0}^n\mathtt{1}^n \mid n\ge0\}$, which is not regular.

**(i)** *The regular expression $(\mathtt{00} + \mathtt{11})^*$ represents the language of all strings over $\{\mathtt{0}, \mathtt{1}\}$ of even length.* \
**False.** The string `01` has even length, but it is not in $(\mathtt{00} + \mathtt{11})^*$.

**(j)** *Let $L_1$ and $L_2$ be two regular languages. The language $(L_1\cup L_2)^*$ is also regular.* \
**True.** Regular languages are closed under union and Kleene star.

> [!exam] How this is graded
> One sentence per item is the expected justification; a "False" needs a concrete counterexample (as in (b), (d), (e), (h), (i)) and a "True" needs the name of the result it rests on. The pattern in (g) versus (h) recurs on every exam: a transformation that treats $x$ and $y$ independently stays regular, one that forces the two halves to match ($w$ and $w^c$) does not. See [[0-toolkit/06-how-exams-are-graded#3-the-midterm-1-format|the Midterm 1 format]].

### Sources for this page
A conversion of "Midterm 1 Practice Tests 1, 2 and 3: Solutions", practice test 2, written earlier for this course; the problem statements are the paraphrased statements from that document, and the solutions are the same, lightly reworded for the page. Checked by `tools/checks/exams_mt1.py` (practice test 2 section): both $\textsf{compress0s}$ constructions implemented as functions of an arbitrary DFA and compared with the definitions of $\textsf{Decompressed}$ and $\textsf{Compressed}$ on random DFAs with 2–4 states, exactly on every string of length at most 8; the worked example $\textsf{compress0s}(\mathtt{00000110001})$; the regular expression, DFA and fooling set of Problem 2 for every run length $k\le 6$ (regex, DFA and brute force agree on all strings of length at most 12, the minimal DFA has exactly $k+1$ states, and the suffix $\mathtt{1}^{k-j}$ distinguishes every pair), plus the state count and sample runs of the 375-state DFA itself; the length inequality for $\textsf{Bond}$ on all strings of length at most 10 and the concatenation identity for all $x$, $y$ of length at most 6; the fooling set of Problem 4 for all $1\le i\ne j\le 12$ and the grammar (and each nonterminal's language) on all strings of length at most 12; and every concrete claim of Problem 5 — the alternative fooling set, both grammars, the one-accepting-state DFAs (exhaustively, up to 3 states), the complement DFA, $\{ww^c\}$ for $\mathtt{0}^*$, and `01`.
