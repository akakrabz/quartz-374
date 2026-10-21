---
title: "Midterm 1 practice test 1 — solutions"
description: "Five problems in the Midterm 1 format, solved in full: ten true/false statements with one-line reasons; the transformations Inserted1st and Deleted1st built from an arbitrary DFA; an induction proof about a recursive function squish; a fooling set and a grammar for the language where every run of 0s is followed by a shorter run of 1s; and a DFA plus a regular expression for two languages (no subsequence 010; at least two even-length runs of 1s)."
tags: [exam, midterm-1, regular, context-free]
---

*Midterm 1 practice test 1 · CS/ECE 374 A, Fall 2026 · five problems in the exam's format · the other tests: [[3-homework-and-exams/midterm-1-practice-2|test 2]], [[3-homework-and-exams/midterm-1-practice-3|test 3]] · how it is graded: [[0-toolkit/06-how-exams-are-graded|rubrics]]*

> [!abstract] In one breath
> Problem 1 is ten true/false statements, each settled by one example or one closure fact. Problem 2 builds machines for $\textsf{Inserted1st}(L)$ and $\textsf{Deleted1st}(L)$ from an arbitrary DFA for $L$: the first is a DFA that skips the first run of its input, the second an NFA that guesses the deleted run and feeds it to $M$ with $\varepsilon$-transitions. Problem 3 is an induction on strings about a recursively defined function $\textsf{squish}$, with cases that follow the definition two symbols at a time. Problem 4 proves that "every run of 0s is followed by a shorter run of 1s" is not regular, with the fooling set $\mathtt{0}^+$, and gives a four-nonterminal grammar for it. Problem 5 asks for a DFA and a regular expression for two languages: "no subsequence 010" (three states, $\mathtt{1}^*\mathtt{0}^*\mathtt{1}^*$) and "at least two even-length runs of 1s" (seven states, and a regular expression that forces each $\mathtt{11}(\mathtt{11})^*$ to be a whole run).

## Problem 1 — True or false

> [!question] Problem 1
> For each statement below, check "Yes" if the statement is always true and check "No" otherwise, and give a brief (one short sentence) explanation of your answer.

**(a)** *Every infinite language is regular.* \
**No.** $\{\mathtt{0}^n\mathtt{1}^n \mid n\ge0\}$ is infinite but not regular.

**(b)** *The language $(\mathtt{0} + \mathtt{1}(\mathtt{01}^*\mathtt{0})^*\mathtt{1})^*$ is not context-free.* \
**No.** It is described by a regular expression, so it is regular, and every regular language is context-free.

**(c)** *Every subset of an irregular language is irregular.* \
**No.** $\varnothing$ is a subset of the irregular language $\{\mathtt{0}^n\mathtt{1}^n \mid n\ge0\}$, but $\varnothing$ is regular.

**(d)** *The language $\{\mathtt{0}^a\mathtt{1}^b \mid a-b \text{ is divisible by } 374\}$ is regular.* \
**Yes.** It equals $\bigcup_{r=0}^{373} (\mathtt{0}^{374})^*\,\mathtt{0}^r\mathtt{1}^r\,(\mathtt{1}^{374})^*$, because $374$ divides $a-b$ exactly when $a$ and $b$ have the same remainder $r$ mod $374$.

**(e)** *If language $L$ is not regular, then $L$ has a finite fooling set.* \
**Yes.** Every language has finite fooling sets; for example, any set containing just one string is (vacuously) a fooling set.

**(f)** *If there is a DFA that rejects every string in language $L$, then $L$ is regular.* \
**No.** The DFA with no accepting states rejects every string in *every* language, including the irregular language $\{\mathtt{0}^n\mathtt{1}^n \mid n\ge0\}$.

**(g)** *If language $L$ is accepted by a DFA with $n$ states, then $\Sigma^*\setminus L$ is also accepted by a DFA with $n$ states.* \
**Yes.** Swap the accepting and non-accepting states of the DFA for $L$.

**(h)** *$\mathtt{1}^*\mathtt{0}^*$ is a fooling set for the language $\{\mathtt{1}^i\mathtt{0}^{i+j}\mathtt{1}^j \mid i, j\ge0\}$.* \
**No.** The strings `10` and `1100` are both in $\mathtt{1}^*\mathtt{0}^*$, but for every string $z$, $\mathtt{10}z$ is in the language $\iff$ $z = \mathtt{0}^j\mathtt{1}^j$ for some $j\ge0$ $\iff$ $\mathtt{1100}z$ is in the language; so no suffix distinguishes them.

**(i)** *Every regular language is accepted by a DFA with an odd number of accepting states.* \
**Yes.** If a DFA for $L$ has an even number of accepting states, add one more accepting state (with self-loops on both symbols) that is unreachable from the start state; the language does not change.

**(j)** *The context-free grammar $S\to\varepsilon\mid\mathtt{0}A\mid\mathtt{1}S$, $A\to\mathtt{0}S\mid\mathtt{1}A$ generates all binary strings with an even number of 0s.* \
**Yes.** By induction on length, $S$ generates exactly the strings with an even number of 0s and $A$ exactly those with an odd number: each 0 switches between $S$ and $A$, and each 1 does not.

> [!exam] How this is graded
> Each item is the answer plus one sentence. A "No" needs a concrete counterexample (one string, one language, one DFA); a "Yes" needs the fact it rests on — a closure property ([[1-models-of-computation/03-finite-state-machines#37-closure-properties|§3.7]]), a definition ([[concepts/fooling-sets|fooling set]]: (e) and (h) both turn on the definition, not on Lemma 3.6), or a one-line construction ((g), (i)). The classes and their closure facts are collected on [[0-toolkit/03-the-big-picture|the big picture]]; sample items close every chapter page ([[1-models-of-computation/02-regular-languages#summary|Ch 2]], [[1-models-of-computation/03-finite-state-machines#summary|Ch 3]], [[1-models-of-computation/05-context-free-languages#summary|Ch 5]]).

## Problem 2 — Language transformations: Delete1st

> [!question] Problem 2
> For any non-empty string $w\in\{\mathtt{0},\mathtt{1}\}^*$, let $\textsf{Delete1st}(w)$ denote the string obtained by deleting the first run in $w$. (For example, $\textsf{Delete1st}(\mathtt{100110}) = \mathtt{00110}$.) Let $L$ be an arbitrary regular language over $\Sigma = \{\mathtt{0},\mathtt{1}\}$. Prove that the following languages are also regular.
>
> (a) $\textsf{Inserted1st}(L) = \{w\in\Sigma^* \mid w\ne\varepsilon \text{ and } \textsf{Delete1st}(w)\in L\}$
>
> (b) $\textsf{Deleted1st}(L) = \{\textsf{Delete1st}(w) \mid w\ne\varepsilon \text{ and } w\in L\}$

Throughout, $M = (Q, s, A, \delta)$ is a DFA that accepts $L$, and for each symbol $a\in\Sigma$, $\bar a$ denotes the *other* symbol. Every non-empty string $w$ can be written uniquely as $w = a^k u$, where $a\in\Sigma$, $k\ge1$, and $u$ is either empty or begins with $\bar a$; then $\textsf{Delete1st}(w) = u$. The two parts are the two kinds of [[concepts/language-transformations|transformation]] ([[1-models-of-computation/04-nondeterministic-automata#49-regular-language-transformations|§4.9]]): in (a) the input is $w$ and the machine simulates $M$ on $\textsf{Delete1st}(w)$; in (b) the input is the *result* $u$, and the machine must guess the string of $L$ that produced it.

### (a) Inserted1st

The input to $M'$ is an arbitrary string $w$; $M'$ skips the first run of $w$ and then simulates $M$ on the rest. No guessing is needed, so $M'$ is a DFA.

> [!key] Answer (a)
> We construct a DFA $M' = (Q', s', A', \delta')$, where $s'$, $f_{\mathtt{0}}$, and $f_{\mathtt{1}}$ are three new states:
> $$
> \begin{aligned}
> Q' &= \{s', f_{\mathtt{0}}, f_{\mathtt{1}}\}\cup Q
> &
> A' &= \begin{cases} A\cup\{f_{\mathtt{0}}, f_{\mathtt{1}}\} & \text{if } s\in A\\ A & \text{if } s\notin A \end{cases}
> \\[0.5ex]
> \delta'(s', a) &= f_a
> &
> \delta'(f_a, a) &= f_a
> \\
> \delta'(f_a, \bar a) &= \delta(s, \bar a)
> &
> \delta'(q, a) &= \delta(q, a)\quad\text{for all } q\in Q
> \end{aligned}
> $$
> for every symbol $a\in\Sigma$.
> - $s'$: Nothing has been read yet. It is not accepting, because $w$ must be non-empty.
> - $f_a$: The input so far is $a^k$ for some $k\ge1$, so it is still inside the first run, and deleting that run leaves $\varepsilon$. So $M'$ accepts here if and only if $M$ accepts $\varepsilon$, that is, if and only if $s\in A$.
> - $q\in Q$: The first run is over; if the input so far is $a^k u$, where $u$ starts with $\bar a$, then $q = \delta^*(s, u)$.
>
> So $M'$ accepts $w$ if and only if $w\ne\varepsilon$ and $M$ accepts $\textsf{Delete1st}(w)$.

### (b) Deleted1st

The input to $M'$ is a string $u$, and $M'$ must decide whether $a^k u\in L$ for some $a\in\Sigma$ and $k\ge1$ such that $u$ is empty or starts with $\bar a$. $M'$ *guesses* the deleted run $a^k$, feeding it to $M$ with $\varepsilon$-transitions, and then simulates $M$ on the actual input, checking that the first input symbol is not $a$.

> [!key] Answer (b)
> We construct an NFA with $\varepsilon$-transitions $M' = (Q', s', A', \delta')$, where $s'$ is a new state:
> $$
> \begin{aligned}
> Q' &= \{s'\}\cup(Q\times\Sigma)\cup Q
> &
> \delta'(s', \varepsilon) &= \{(\delta(s, a), a) \mid a\in\Sigma\}
> \\
> A' &= (A\times\Sigma)\cup A
> &
> \delta'\big((q, a), \varepsilon\big) &= \{(\delta(q, a), a)\}
> \\
> &&
> \delta'\big((q, a), \bar a\big) &= \{\delta(q, \bar a)\}
> \\
> &&
> \delta'(q, a) &= \{\delta(q, a)\}\quad\text{for all } q\in Q
> \end{aligned}
> $$
> for every symbol $a\in\Sigma$. All other transitions lead to $\varnothing$; in particular, $\delta'((q, a), a) = \varnothing$, and $s'$ has no transitions on input symbols.
> - $(q, a)$: $M'$ has guessed that the deleted first run consists of $a$s and has fed $a^k$ to $M$ for some $k\ge1$, so $q = \delta^*(s, a^k)$; no input has been read yet. Each $\varepsilon$-transition adds one more $a$ to the run. The first input symbol must be $\bar a$, because otherwise it would belong to the deleted run. If the input ends here, then $u = \varepsilon$, so $M'$ accepts if and only if $a^k\in L$, that is, $q\in A$.
> - $q\in Q$: $M'$ has read a non-empty prefix $v$ of its input, and $q = \delta^*(s, a^k v)$.
>
> So $M'$ accepts $u$ if and only if $a^k u\in L$ for some $a\in\Sigma$ and $k\ge1$ such that $u$ is empty or starts with $\bar a$, that is, if and only if $u\in\textsf{Deleted1st}(L)$.

> [!exam] How this is graded
> Out of 10 per part: 2 for a formal, complete description built from an *arbitrary* DFA (say DFA or NFA, and list the $\varepsilon$-transitions — (b) states explicitly that $\delta'((q,a),a) = \varnothing$), 2 for the English meaning of the states and of the accepting states, 6 for correctness ([[0-toolkit/06-how-exams-are-graded#8-language-transformations|§8 of the rubrics]]). Before handing in, run both machines on $L = \varnothing$, $\{\varepsilon\}$, $\mathtt{1}^*$ and $\Sigma^*$: for $L = \{\varepsilon\}$, (a) accepts $\mathtt{0}^+ + \mathtt{1}^+$ (the $f_a$ states accept because $s\in A$) and (b) accepts nothing (no $a^k$ with $k\ge1$ is in $L$). Template: [[0-toolkit/02-proof-templates#9-language-transformation|language transformation]]; the same two kinds, worked with traps: [[problems/two-language-transformations|insert and delete a 1]].

## Problem 3 — Induction: squish

> [!question] Problem 3
> For any string $w\in\{\mathtt{0},\mathtt{1}\}^*$, let $\textsf{squish}(w)$ be defined recursively as follows:
> $$
> \textsf{squish}(w) :=
> \begin{cases}
> w & \text{if } w = \varepsilon \text{ or } w = \mathtt{0} \text{ or } w = \mathtt{1}\\
> \mathtt{0}\cdot\textsf{squish}(x) & \text{if } w = \mathtt{00}x \text{ or } w = \mathtt{11}x \text{ for some string } x\\
> \mathtt{1}\cdot\textsf{squish}(x) & \text{if } w = \mathtt{01}x \text{ or } w = \mathtt{10}x \text{ for some string } x
> \end{cases}
> $$
> You may use the fact that $\#(\mathtt{1}, xy) = \#(\mathtt{1}, x) + \#(\mathtt{1}, y)$ for all strings $x$ and $y$.
>
> (a) *Prove* that $\#(\mathtt{1}, \textsf{squish}(w))\le\#(\mathtt{1}, w)$ for every string $w$.
>
> (b) *Prove* that $\#(\mathtt{1}, \textsf{squish}(w)) \bmod 2 = \#(\mathtt{1}, w) \bmod 2$ for every string $w$.

The definition consumes two symbols at a time, so the induction follows it: three base cases ($\varepsilon$, `0`, `1`) and two recursive cases, $w = aax$ and $w = abx$ with $a\ne b$. The induction hypothesis is applied to $x$, which is shorter than $w$ by two ([[0-toolkit/02-proof-templates#1-induction-on-strings|template]], [[1-models-of-computation/01-strings#14-more-than-one-path-up-the-mountain|§1.4]] on following a definition with more cases).

### (a) Squishing never adds 1s

Let $w$ be an arbitrary string. Assume that $\#(\mathtt{1}, \textsf{squish}(x))\le\#(\mathtt{1}, x)$ for every string $x$ such that $|x| < |w|$. There are three cases to consider, mirroring the definition of $\textsf{squish}$.

- If $w = \varepsilon$ or $w = \mathtt{0}$ or $w = \mathtt{1}$, then $\textsf{squish}(w) = w$, so $\#(\mathtt{1}, \textsf{squish}(w)) = \#(\mathtt{1}, w)$.
- If $w = aax$ for some symbol $a$ and some string $x$ (that is, $w = \mathtt{00}x$ or $w = \mathtt{11}x$), then
  $$
  \begin{aligned}
  \#(\mathtt{1}, \textsf{squish}(w))
  &= \#(\mathtt{1}, \mathtt{0}\cdot\textsf{squish}(x)) && \text{by definition of } \textsf{squish}\\
  &= \#(\mathtt{1}, \textsf{squish}(x)) && \text{because } \#(\mathtt{1}, \mathtt{0}) = 0\\
  &\le \#(\mathtt{1}, x) && \text{by the induction hypothesis}\\
  &\le \#(\mathtt{1}, aa) + \#(\mathtt{1}, x) && \text{because } \#(\mathtt{1}, aa)\ge0\\
  &= \#(\mathtt{1}, w) && \text{because } w = aa\cdot x
  \end{aligned}
  $$
- If $w = abx$ for some symbols $a\ne b$ and some string $x$ (that is, $w = \mathtt{01}x$ or $w = \mathtt{10}x$), then
  $$
  \begin{aligned}
  \#(\mathtt{1}, \textsf{squish}(w))
  &= \#(\mathtt{1}, \mathtt{1}\cdot\textsf{squish}(x)) && \text{by definition of } \textsf{squish}\\
  &= 1 + \#(\mathtt{1}, \textsf{squish}(x)) && \text{because } \#(\mathtt{1}, \mathtt{1}) = 1\\
  &\le 1 + \#(\mathtt{1}, x) && \text{by the induction hypothesis}\\
  &= \#(\mathtt{1}, ab) + \#(\mathtt{1}, x) && \text{because } \#(\mathtt{1}, ab) = 1\\
  &= \#(\mathtt{1}, w) && \text{because } w = ab\cdot x
  \end{aligned}
  $$

The induction hypothesis applies because $|x| = |w| - 2 < |w|$. In every case, $\#(\mathtt{1}, \textsf{squish}(w))\le\#(\mathtt{1}, w)$. $\blacksquare$

### (b) Squishing preserves the parity of the number of 1s

Write $m\equiv n$ to mean $m \bmod 2 = n \bmod 2$. Let $w$ be an arbitrary string. Assume that $\#(\mathtt{1}, \textsf{squish}(x))\equiv\#(\mathtt{1}, x)$ for every string $x$ such that $|x| < |w|$. There are three cases to consider.

- If $w = \varepsilon$ or $w = \mathtt{0}$ or $w = \mathtt{1}$, then $\textsf{squish}(w) = w$, so the claim is immediate.
- If $w = aax$ for some symbol $a$ and some string $x$, then
  $$
  \begin{aligned}
  \#(\mathtt{1}, \textsf{squish}(w))
  &= \#(\mathtt{1}, \textsf{squish}(x)) && \text{as in part (a)}\\
  &\equiv \#(\mathtt{1}, x) && \text{by the induction hypothesis}\\
  &\equiv \#(\mathtt{1}, aa) + \#(\mathtt{1}, x) && \text{because } \#(\mathtt{1}, aa) \text{ is } 0 \text{ or } 2\\
  &= \#(\mathtt{1}, w)
  \end{aligned}
  $$
- If $w = abx$ for some symbols $a\ne b$ and some string $x$, then
  $$
  \begin{aligned}
  \#(\mathtt{1}, \textsf{squish}(w))
  &= 1 + \#(\mathtt{1}, \textsf{squish}(x)) && \text{as in part (a)}\\
  &\equiv 1 + \#(\mathtt{1}, x) && \text{by the induction hypothesis}\\
  &= \#(\mathtt{1}, ab) + \#(\mathtt{1}, x) && \text{because } \#(\mathtt{1}, ab) = 1\\
  &= \#(\mathtt{1}, w)
  \end{aligned}
  $$

Again, the induction hypothesis applies because $|x| < |w|$. In every case, $\#(\mathtt{1}, \textsf{squish}(w))\equiv\#(\mathtt{1}, w)$. $\blacksquare$

> [!exam] How this is graded
> Out of 10: 1 for starting from an arbitrary $w$, 2 for an explicit strong hypothesis (quantified over all shorter $x$ — here it must cover $|x| = |w|-2$, which a "for $|x| = |w|-1$" hypothesis does not), 2 for exhaustive cases (the three base cases *and* both recursive cases), 1 for the base cases, 2 for using the hypothesis correctly, 2 for the rest ([[0-toolkit/06-how-exams-are-graded#4-induction|§4 of the rubrics]]). Each line of the chains above carries its reason; the given fact about $\#(\mathtt{1}, xy)$ is what turns $\#(\mathtt{1}, aa\cdot x)$ into a sum. Worked in the same style: [[problems/induction-on-a-recursive-string-function|sorting a string]].

## Problem 4 — Not regular, and a grammar

> [!question] Problem 4
> Let $L$ be the set of all strings in $\{\mathtt{0},\mathtt{1}\}^*$ in which every run of 0s is followed immediately by a *shorter* run of 1s.
>
> (a) *Prove* that $L$ is not a regular language.
>
> (b) Describe a context-free grammar for $L$.

### (a) A fooling set

A machine reading $\mathtt{0}^n$ must remember $n$, because the next run of 1s is allowed to have any length below $n$ and no other: that unbounded count is what the fooling set exploits ([[concepts/fooling-sets|fooling sets]], [[1-models-of-computation/03-finite-state-machines#38-proving-a-language-is-not-regular|§3.8]], [[0-toolkit/02-proof-templates#7-fooling-set-proof|template]]).

> [!key] Answer (a)
> Fooling set $F = \mathtt{0}^+ = \{\mathtt{0}^n \mid n\ge1\}$; for $x = \mathtt{0}^i$ and $y = \mathtt{0}^j$ with $i < j$, the distinguishing suffix is $z = \mathtt{1}^i$.

Consider the set $F = \mathtt{0}^+ = \{\mathtt{0}^n \mid n\ge1\}$. Let $x$ and $y$ be arbitrary distinct strings in $F$. Then $x = \mathtt{0}^i$ and $y = \mathtt{0}^j$ for some positive integers $i\ne j$; without loss of generality, $i < j$. Let $z = \mathtt{1}^i$.

- $xz = \mathtt{0}^i\mathtt{1}^i\notin L$, because its only run of 0s has length $i$ and is followed by a run of 1s of length $i$, which is not shorter.
- $yz = \mathtt{0}^j\mathtt{1}^i\in L$, because its only run of 0s has length $j$ and is followed immediately by a run of 1s of length $i$, where $1\le i < j$.

Thus, $z$ is a distinguishing suffix for $x$ and $y$. We conclude that $F$ is a fooling set for $L$. Because $F$ is infinite, $L$ cannot be regular. $\blacksquare$

### (b) A grammar

A string is in $L$ if and only if it consists of a (possibly empty) string of 1s followed by zero or more *blocks* $\mathtt{0}^a\mathtt{1}^b$ with $1\le b < a$; each block is a run of 0s together with the shorter run of 1s that must follow it. (Each block starts with 0 and ends with 1, so adjacent blocks never merge runs: every run of 0s is the 0-part of exactly one block, followed immediately by that block's 1-part.)

> [!key] Answer (b)
> $$
> \begin{array}{rcll}
> S & \to & \mathtt{1}S \mid T & \qquad L\\
> T & \to & \varepsilon \mid RT & \qquad \{\mathtt{0}^a\mathtt{1}^b \mid 1\le b < a\}^* \quad\text{(zero or more blocks)}\\
> R & \to & \mathtt{0}R\mathtt{1} \mid \mathtt{0}Z\mathtt{1} & \qquad \{\mathtt{0}^a\mathtt{1}^b \mid 1\le b < a\} \quad\text{(one block)}\\
> Z & \to & \mathtt{0} \mid \mathtt{0}Z & \qquad \mathtt{0}^+ = \{\mathtt{0}^c \mid c\ge1\}
> \end{array}
> $$
> The production $R\to\mathtt{0}Z\mathtt{1}$ generates the blocks $\mathtt{0}^{c+1}\mathtt{1}$ with $c\ge1$, and each use of $R\to\mathtt{0}R\mathtt{1}$ adds one 0 and one 1, which keeps $1\le b < a$. Every block $\mathtt{0}^a\mathtt{1}^b$ with $1\le b < a$ is obtained by wrapping $\mathtt{0}^{a-b+1}\mathtt{1}$ in $b-1$ such pairs.

> [!exam] How this is graded
> (a), out of 10: 4 for an explicit infinite set that really is a fooling set, 2 for the suffix, 2 for each half of "$xz\in L$, $yz\notin L$" — both halves need a reason, as above ([[0-toolkit/06-how-exams-are-graded#7-fooling-sets|§7 of the rubrics]]). Note that $F = \mathtt{0}^*$ would also work but needs care at $i = 0$ (then $z = \varepsilon$ and $xz = \varepsilon\in L$ while $yz = \mathtt{0}^j\notin L$); $\mathtt{0}^+$ avoids the special case. (b), out of 10: 2 for syntax and 8 for correctness, with every nonterminal's language stated, as in the right-hand column ([[0-toolkit/06-how-exams-are-graded#5-regular-expressions-and-grammars|§5]], [[0-toolkit/02-proof-templates#2-writing-up-a-regular-expression-or-a-grammar|template]]). The first thing a grader tries is $\varepsilon$ and the strings of $\mathtt{1}^*$: $S\rightsquigarrow^*\mathtt{1}^nT\rightsquigarrow\mathtt{1}^n$, good. A worked problem of the same type: [[problems/fooling-set-and-grammar-for-one-language|fooling set and grammar]].

## Problem 5 — A DFA and a regular expression

> [!question] Problem 5
> For each of the following languages over $\Sigma = \{\mathtt{0},\mathtt{1}\}$, describe a DFA that accepts $L$ **and** give a regular expression that represents $L$.
>
> (a) Strings that do not contain the subsequence `010`.
>
> (b) Strings that contain at least two even-length runs of 1s.

### (a) No subsequence 010

Each state is labeled with the longest prefix of `010` that appears in the input so far as a subsequence ([[0-toolkit/02-proof-templates#5-describing-a-dfa|template]], [[1-models-of-computation/03-finite-state-machines#35-designing-dfas-dfas-are-algorithms|§3.5]]).

<!-- fig:exam-mt1p1-no-010-subsequence -->
<figure class="cs-fig"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 128" width="400" height="128" role="img" style="font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-size:14px"><title>three accepting states in a row, named epsilon, 0 and 01, with loops 1, 0, 1 and edges 0 then 1</title><defs><marker id="ARR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs><path d="M59.7,60.6 C33.8,22.5 106.2,22.5 81.5,58.4" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="70" y="15.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">1</text><path d="M189.7,60.6 C163.8,22.5 236.2,22.5 211.5,58.4" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="200" y="15.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">0</text><path d="M319.7,60.6 C293.8,22.5 366.2,22.5 341.5,58.4" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="330" y="15.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">1</text><path d="M92,80 L175.5,80" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="135" y="69" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">0</text><path d="M222,80 L305.5,80" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="265" y="69" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">1</text><line x1="22" y1="80" x2="45.5" y2="80" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" marker-end="url(#ARR)"/><circle cx="70" cy="80" r="23" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><circle cx="70" cy="80" r="19" fill="var(--accent)" fill-opacity="0.1" stroke="currentColor" stroke-width="1.6"/><text x="70" y="81" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">ε</text><circle cx="200" cy="80" r="23" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><circle cx="200" cy="80" r="19" fill="var(--accent)" fill-opacity="0.1" stroke="currentColor" stroke-width="1.6"/><text x="200" y="81" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">0</text><circle cx="330" cy="80" r="23" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><circle cx="330" cy="80" r="19" fill="var(--accent)" fill-opacity="0.1" stroke="currentColor" stroke-width="1.6"/><text x="330" y="81" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">01</text></svg><figcaption><strong>No subsequence 010.</strong> Each state is named after the longest prefix of 010 that occurs in the input so far as a subsequence: ε (no 0 yet), 0 (a 0, but no 1 after it), 01 (a 0 followed later by a 1). All three accept. The missing transition, a 0 read in state 01, leads to a hidden dump state: the input contains 010.</figcaption></figure>

- $\varepsilon$ — no 0 has been read yet.
- `0` — some 0 has been read, but no 1 after it.
- `01` — some 0 has been read, followed later by a 1.

The missing transition (reading 0 in state `01`) leads to a hidden dump state: the input contains `010`.

> [!key] Regular expression (a)
> $$
> \mathtt{1}^*\mathtt{0}^*\mathtt{1}^*
> $$
> A string avoids the subsequence `010` if and only if no 0 appears after a 1 that itself comes after a 0; that is, if and only if it consists of some 1s, then some 0s, then some 1s.

### (b) At least two even-length runs of 1s

Call a run of 1s *finished* once a 0 has been read after it. In states $N_k$, $O_k$, and $E_k$, exactly $k$ finished runs of 1s have even length.

<!-- fig:exam-mt1p1-two-even-runs -->
<figure class="cs-fig"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 262" width="640" height="262" role="img" style="font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-size:14px"><title>seven-state DFA: top row N0, O0, E0; bottom row done, E1, O1, N1; a 0 from E0 drops to N1 and a 0 from E1 leads to done</title><defs><marker id="ARR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs><path d="M180.6,60.3 C154.8,22.2 225.2,22.2 200.6,58.1" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="190" y="15.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">0</text><path d="M209,71.9 Q265,54 318.6,71.1" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="265" y="52" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">1</text><path d="M321,84.1 Q265,102 211.4,84.9" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="265" y="104" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">0</text><path d="M359,71.9 Q415,54 468.6,71.1" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="415" y="52" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">1</text><path d="M471,84.1 Q415,102 361.4,84.9" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="415" y="104" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">1</text><path d="M490,98 L490,183.5" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="479" y="142" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">0</text><path d="M507.7,196.6 C545.8,170.8 545.8,241.2 509.9,216.6" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="552.5" y="206" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">0</text><path d="M471,212.1 Q415,230 361.4,212.9" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="415" y="232" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">1</text><path d="M359,199.9 Q415,182 468.6,199.1" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="415" y="180" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">0</text><path d="M321,212.1 Q265,230 214.3,213.8" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="265.7" y="232.3" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">1</text><path d="M211.9,199 Q265,182 318.6,199.1" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="265.7" y="179.7" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">1</text><path d="M167,206 L95.5,206" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="130" y="217" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">0</text><path d="M52.6,188.3 C26.8,150.2 97.2,150.2 72.6,186.1" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="62" y="143.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">0,1</text><line x1="144" y1="78" x2="167.5" y2="78" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" marker-end="url(#ARR)"/><circle cx="190" cy="78" r="20" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="190" y="79" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">N<tspan dy="4" style="font-size:10px">0</tspan></text><circle cx="340" cy="78" r="20" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="340" y="79" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">O<tspan dy="4" style="font-size:10px">0</tspan></text><circle cx="490" cy="78" r="20" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="490" y="79" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">E<tspan dy="4" style="font-size:10px">0</tspan></text><circle cx="490" cy="206" r="20" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="490" y="207" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">N<tspan dy="4" style="font-size:10px">1</tspan></text><circle cx="340" cy="206" r="20" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="340" y="207" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">O<tspan dy="4" style="font-size:10px">1</tspan></text><circle cx="190" cy="206" r="24" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><circle cx="190" cy="206" r="20" fill="var(--accent)" fill-opacity="0.1" stroke="currentColor" stroke-width="1.6"/><text x="190" y="207" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">E<tspan dy="4" style="font-size:10px">1</tspan></text><rect x="30" y="182" width="64" height="48" rx="24" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><rect x="34" y="186" width="56" height="40" rx="20" fill="var(--accent)" fill-opacity="0.1" stroke="currentColor" stroke-width="1.6"/><text x="62" y="207" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">done</text></svg><figcaption><strong>At least two even-length runs of 1s.</strong> The subscript <i>k</i> counts the <em>finished</em> runs of 1s (a 0 has been read after them) that have even length. <i>N</i>: the input is empty or ends with 0; <i>O</i>, <i>E</i>: it ends with a run of 1s of odd, even length so far. A 0 read in <i>E</i> finishes an even run, and <i>E</i>₁ accepts because an input that ends there ends with a second even run. <i>done</i> is a permanent accepting state.</figcaption></figure>

- $N_k$ — the input does not end with 1 (it is empty or ends with 0).
- $O_k$ — the input ends with a run of 1s whose length so far is odd.
- $E_k$ — the input ends with a run of 1s whose length so far is even.
- $\textsf{done}$ — at least two finished runs of 1s have even length.

State $E_1$ accepts because, if the input ends there, its last run is a second even-length run of 1s.

> [!key] Regular expression (b)
> $$
> (\varepsilon + (\mathtt{0}+\mathtt{1})^*\mathtt{0})\;\mathtt{11}(\mathtt{11})^*\;\mathtt{0}\;(\varepsilon + (\mathtt{0}+\mathtt{1})^*\mathtt{0})\;\mathtt{11}(\mathtt{11})^*\;(\varepsilon + \mathtt{0}(\mathtt{0}+\mathtt{1})^*)
> $$
> The two copies of $\mathtt{11}(\mathtt{11})^*$ are two even-length runs of 1s. The pieces around them force each copy to be a *whole* run: each one is preceded by the start of the string or a 0, and followed by a 0 or the end of the string.

> [!exam] How this is graded
> No proof is asked for. DFA, out of 10: 2 for a complete, unambiguous description — a start arrow, double circles, and a sentence about the dump state whenever a transition is missing, as in (a); 6 for correctness; 2 for mnemonic state names, which is why the states above are named after what they remember and not $q_0, q_1, \dots$ ([[0-toolkit/06-how-exams-are-graded#6-dfas-and-nfas|§6 of the rubrics]]). An NFA where a DFA was asked earns half credit. Regular expression, out of 10: 2 for syntax, 8 for correctness, and a missing or extra $\varepsilon$ costs 2 ([[0-toolkit/06-how-exams-are-graded#5-regular-expressions-and-grammars|§5]]) — in (b), the $\varepsilon$ alternatives are what let an even run sit at the very start or the very end. Same type, worked with traps: [[problems/regular-expression-and-dfa-for-one-language|01 exactly twice]].

### Sources for this page

Converted from the Midterm 1 Practice Test 1 solutions written earlier for this student (problem statements paraphrased there); the solutions, the constructions and the wording are the same, reorganized into the page format with rubric notes and links added. Checked by `tools/checks/exams_mt1.py` (section "Practice test 1"): the two DFAs and the two regular expressions of Problem 5 against brute-force definitions of their languages on every string of length at most 10 and against each other by exact DFA equivalence; the constructions of Problem 2 implemented as functions of an arbitrary DFA and compared with the definitions of $\textsf{Inserted1st}$ and $\textsf{Deleted1st}$ on 300 random DFAs, on every string of length at most 8; the two inequalities of Problem 3 on every string of length at most 12; the fooling set of Problem 4 for all $1\le i < j\le 9$ and its grammar against the definition of $L$ up to length 12; and the concrete claims of Problem 1 (the equality in (d) for several moduli, the undistinguishable pair `10`, `1100` in (h) on every suffix up to length 10, the grammar in (j) up to length 12).
