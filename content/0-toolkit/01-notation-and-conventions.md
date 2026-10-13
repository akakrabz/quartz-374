---
title: "Notation and conventions"
description: "Every symbol the site uses — strings, languages, regular expressions, automata, grammars, Turing machines, encodings, named languages and complexity classes — with where each is developed, how to write it by hand on an exam, the other names you will meet for the same thing, and the few places where this site departs from the book."
tags: [toolkit, strings, regular, context-free, turing-machines, undecidability, complexity, midterm-1]
aliases: ["notation", "symbol table", "terminology"]
---

*Toolkit · reference page · every row links to the section that develops the notation; this page only collects.*

The site writes everything the way Erickson's *Models of Computation* ([whole book PDF](https://jeffe.cs.illinois.edu/teaching/algorithms/models/all-models.pdf)) does, except for the handful of changes listed in [[#11-where-this-site-departs-from-the-book|§11]]. Section and result numbers are the book's: "§3.8" is section 3.8 of both the book and the chapter page. Results in Chapters 1–5 carry the chapter number (Lemma 3.6, Theorem 5.7); in Chapters 7 and 9 they do not, so "Lemma 5" and "Theorem 12" live in Chapter 7 and "Theorem 1" in Chapter 9.

## 1. Strings

| notation | meaning | where |
|---|---|---|
| $\Sigma$ | an **alphabet**: a finite set of **symbols** | [[1-models-of-computation/01-strings#11-strings\|§1.1]] |
| $a, b, c$ | variables for symbols | §1.1 |
| $w, x, y, z$ | variables for strings | §1.1 |
| $\mathtt{0}$, $\mathtt{1}$, `0110` | explicit symbols and strings, set in monospace | §1.1 |
| $\varepsilon$ | the **empty string**, of length 0 | §1.1 |
| $a\cdot x$ | the string with first symbol $a$ and rest $x$ — the **small dot** puts one symbol in front; usually written $ax$ | §1.1 |
| $w\bullet z$ | **concatenation** of two strings — the **big dot**; usually written $wz$ | [[1-models-of-computation/01-strings#12-two-recursive-functions\|§1.2]] |
| $\Sigma^*$ | all strings over $\Sigma$: an infinite set, but every string in it is finite | §1.1 |
| $\lvert w\rvert$ | the **length** of $w$ | §1.2 |
| $\#(a,w)$ | the number of $a$'s in $w$: $\#(\mathtt{0},\mathtt{0110}) = 2$ | [[1-models-of-computation/01-strings#more-recursive-functions\|more functions]] |
| $w^R$ | **reversal**: $(\mathtt{001})^R = \mathtt{100}$ | ″ |
| $w^n$ | $n$ copies of $w$: $w^0 = \varepsilon$, $(\mathtt{01})^3 = \mathtt{010101}$ | ″ |
| $w^c$ | **binary complement**, every bit flipped: $(\mathtt{001})^c = \mathtt{110}$ — not the complement of a language | ″ |
| $w_i$ | the $i$th symbol of $w$, counting from $w_1$ | [[1-models-of-computation/01-strings#15-indices-substrings-and-subsequences\|§1.5]] |
| $w[i..j]$ | the substring $w_iw_{i+1}\cdots w_j$; it is $\varepsilon$ if $j<i$ | §1.5 |
| $w[1..n]$, $w_1w_2\cdots w_n$ | $w$ spelled out, with $n = \lvert w\rvert$ — which may be 1, or even 0 | §1.5 |
| prefix; suffix; substring; subsequence | $w = px$; $w = xs$; $w = xyz$ (always contiguous); delete symbols anywhere. **Proper** means "not $w$ itself": `HE` is a proper prefix and a proper suffix of `HEADACHE` | §1.5 |

## 2. Languages

| notation | meaning | where |
|---|---|---|
| $L$, $A$, $B$, $C$ | **languages**: sets of strings, $L\subseteq\Sigma^*$ | [[1-models-of-computation/02-regular-languages#21-languages\|§2.1]] |
| $\varnothing$ | the **empty language**: no strings at all | §2.1 |
| $\{\varepsilon\}$ | the language whose one string is $\varepsilon$ — not empty | §2.1 |
| $\{w \mid \ldots\}$ | set-builder: all strings $w$ such that … | §2.1 |
| $\{\mathtt{0}^n\mathtt{1}^n \mid n\ge0\}$ | exponents count copies: $n$ 0s followed by $n$ 1s | §2.1 |
| $A\cup B$, $A\cap B$, $A\setminus B$ | union, intersection, difference | [[1-models-of-computation/02-regular-languages#22-building-languages\|§2.2]] |
| $A\oplus B$ | **symmetric difference**: the strings in exactly one of $A$ and $B$ | §2.2 |
| $\overline{L}$ | **complement**, always relative to $\Sigma^*$: $\overline{L} = \Sigma^*\setminus L$ | §2.2 |
| $A\bullet B$, $AB$ | **concatenation**: $\{xy \mid x\in A \text{ and } y\in B\}$ | §2.2 |
| $L^*$ | **Kleene star**: concatenations of zero or more strings of $L$; $\varnothing^* = \{\varepsilon\}^* = \{\varepsilon\}$ | §2.2 |
| $L^+$ | **Kleene plus**: $L\bullet L^*$, one or more; $L^+ = L^*$ if and only if $\varepsilon\in L$ | §2.2 |
| $A^n$ | $A^0 = \{\varepsilon\}$ and $A^n = A\bullet A^{n-1}$ (the proof of Arden's rule) | §2.2 |
| $L^R$ | $\{w^R \mid w\in L\}$ (Lemma 4.4) | [[1-models-of-computation/04-nondeterministic-automata#49-regular-language-transformations\|§4.9]] |
| $\textsf{half}(L)$ | $\{w \mid ww\in L\}$ (Lemma 4.5) | §4.9 |

> [!trap] Three different "empty" things
> $\varnothing$ has no strings, $\{\varepsilon\}$ has one string, and $\varepsilon$ is a string, not a language. In a regular expression, $\varepsilon$ stands for $\{\varepsilon\}$. They behave differently: $\varnothing\bullet L = \varnothing$ but $\{\varepsilon\}\bullet L = L$.

## 3. Regular expressions

| notation | meaning | where |
|---|---|---|
| $\varnothing$ | the expression for the empty language | [[1-models-of-computation/02-regular-languages#23-regular-languages-and-regular-expressions\|§2.3]] |
| $w$, any string (also $\varepsilon$) | the expression for $\{w\}$ | §2.3 |
| $S+T$ | **union** — never "one or more" | §2.3 |
| $ST$ | concatenation | §2.3 |
| $S^*$ | Kleene star | §2.3 |
| precedence | the star first, then concatenation, then $+$: $\mathtt{1}\mathtt{0}^*$ is $\mathtt{1}(\mathtt{0}^*)$, not $(\mathtt{10})^*$, and $\mathtt{0}+\mathtt{1}^*$ is $\mathtt{0}+(\mathtt{1}^*)$ | §2.3 |
| $L(R)$ | the language of $R$; $w$ **matches** $R$ if $w\in L(R)$; $R$ and $R'$ are **equivalent** if $L(R) = L(R')$ | §2.3 |
| $RR^*$ | one or more copies of $R$ — the course's expressions have no other "plus" | [[1-models-of-computation/02-regular-languages#24-things-that-arent-regular-expressions\|§2.4]] |
| subexpression, size | a subtree of the expression tree; the number of its nodes, invisible concatenations included | [[1-models-of-computation/02-regular-languages#25-regular-expression-trees\|§2.5]] |

Not part of the syntax: $\cap$, complement, counters such as $\mathtt{0}^n$, and the conveniences of programming "regexen" — alternation bars, `?`, `{2,3}`, back-references ([[1-models-of-computation/02-regular-languages#24-things-that-arent-regular-expressions|§2.4]]).

## 4. Finite automata

| notation | meaning | where |
|---|---|---|
| $(\Sigma, Q, s, A, \delta)$ | a **DFA** $M$: input alphabet, states, start state, accepting states, transition function — in this order everywhere on this site | [[1-models-of-computation/03-finite-state-machines#32-formal-definitions\|§3.2]] |
| $\delta\colon Q\times\Sigma\to Q$ | DFA transitions — **total**: exactly one edge per state and symbol | §3.2 |
| $\delta^*(q,w)$ | the state reached from $q$ by reading $w$: $\delta^*(q,\varepsilon) = q$ and $\delta^*(q,ax) = \delta^*(\delta(q,a),x)$ | §3.2 |
| $L(M)$ | $\{w \mid \delta^*(s,w)\in A\}$; a language is **automatic** if it is $L(M)$ for some DFA $M$ | §3.2 |
| drawings | states are circles; an arrow from nowhere marks the start state; **double circles** mark accepting states; an edge labeled $\mathtt{0},\mathtt{1}$ stands for two edges | §3.2 |
| dump state | a non-accepting state that loops to itself on every symbol; a drawing may leave it out only if it says so | §3.2 |
| $(p,q)\in Q_1\times Q_2$ | a state of a product DFA: $M_1$ is in $p$ and $M_2$ is in $q$ | [[1-models-of-computation/03-finite-state-machines#36-the-product-construction\|§3.6]] |
| $F$, $z$ | a **fooling set**; a **distinguishing suffix** — this $F$ is not the "final states" of other textbooks | [[1-models-of-computation/03-finite-state-machines#38-proving-a-language-is-not-regular\|§3.8]] |
| $x\equiv_L y$, $[w]$ | no suffix distinguishes $x$ and $y$; the equivalence class of $w$ | [[1-models-of-computation/03-finite-state-machines#39-the-myhillnerode-theorem\|§3.9]] |
| $\delta\colon Q\times(\Sigma\cup\{\varepsilon\})\to 2^Q$ | **NFA** transitions: a set of states, possibly empty | [[1-models-of-computation/04-nondeterministic-automata#43-epsilon-transitions\|§4.3]] |
| $2^Q$ | the **power set** of $Q$: all $2^{\lvert Q\rvert}$ subsets | [[1-models-of-computation/04-nondeterministic-automata#41-nondeterministic-state-machines\|§4.1]] |
| $\varepsilon\text{-reach}(q)$ | the states reachable from $q$ by zero or more $\varepsilon$-transitions, $q$ included | §4.3 |
| NFA acceptance | $\delta^*(s,w)\cap A\ne\varnothing$: some walk from $s$ to an accepting state spells $w$ | §4.1 |
| a set $S\subseteq Q$ as a state | a state of the subset construction; its start state is $\{s\}$ | [[1-models-of-computation/04-nondeterministic-automata#45-nfa-to-dfa-the-subset-construction\|§4.5]] |
| $R(p\to q)$ | the regular expression on the edge from $p$ to $q$ in an expression automaton; $\varnothing$ if there is no edge | [[1-models-of-computation/04-nondeterministic-automata#48-nfa-to-regular-expression-state-elimination\|§4.8]] |

## 5. Context-free grammars

| notation | meaning | where |
|---|---|---|
| $G = (\Sigma, \Gamma, R, S)$ | terminals, nonterminals, production rules, start symbol | [[1-models-of-computation/05-context-free-languages#51-definitions\|§5.1]] |
| $a, b, c$; $A, B, C, S$; $w, x, y, z$ | terminals; nonterminals; strings over $\Sigma\cup\Gamma$ | §5.1 |
| $A\to\omega$ | a rule; $C\to\varepsilon\mid\mathtt{0}C\mathtt{1}$ is two rules | §5.1 |
| $xAz\rightsquigarrow x\omega z$ | one **derivation step**, applying the rule $A\to\omega$ | §5.1 |
| $x\rightsquigarrow^* z$ | $z$ **derives** from $x$ in zero or more steps | §5.1 |
| $L(A)$, $L(G)$ | $\{x\in\Sigma^* \mid A\rightsquigarrow^* x\}$, and $L(G) = L(S)$ | §5.1 |
| parse tree, leftmost derivation | the tree of rule applications; the derivation that always expands the leftmost nonterminal — exactly one per tree | [[1-models-of-computation/05-context-free-languages#52-parse-trees-and-ambiguity\|§5.2]] |
| ambiguous | some string has two parse trees — a property of the grammar; **inherently ambiguous**: every grammar for the language is ambiguous | §5.2 |
| nullable, unit rule | $A\rightsquigarrow^*\varepsilon$; a rule $A\to B$ | [[1-models-of-computation/05-context-free-languages#careful-with-those-epsilons\|§5.3]], [[1-models-of-computation/05-context-free-languages#59-the-cnf-conversion-algorithm\|§5.9]] |
| CNF | the start symbol on no right side; every rule $A\to BC$ or $A\to a$, except possibly $S\to\varepsilon$. In the conversion, $S'$ is the new start symbol and $T_a\to a$ protects the terminal $a$ | [[1-models-of-computation/05-context-free-languages#58-chomsky-normal-form\|§5.8]], §5.9 |
| $M_A$, $s_A$, $t_A$ | the module of a recursive automaton for $A$, its start state, its single accepting state | [[1-models-of-computation/05-context-free-languages#57-recursive-automata\|§5.7]] |
| $(x, q, \sigma)$ | a recursive automaton's configuration: unread input, current state, stack of return states (top first) | §5.7 |
| $[q]$ | the nonterminal for state $q$ when a recursive automaton is turned into a grammar (Lemma 5.6) | §5.7 |

## 6. Turing machines

| notation | meaning | where |
|---|---|---|
| $\Gamma$, $\square$ | the **tape alphabet**, which contains the **blank** $\square$ | [[1-models-of-computation/06-turing-machines#62-formal-definitions\|§6.2]] |
| $\Sigma\subseteq\Gamma\setminus\{\square\}$ | the input alphabet | §6.2 |
| $\textit{start}$, $\textit{accept}$, $\textit{reject}$ | the three special states; other states are italic words that say what they do, such as $\mathit{seek1}$ | §6.2 |
| $\delta(p,a) = (q,b,\Delta)$ | in state $p$ reading $a$: write $b$, move by $\Delta$, enter $q$; $\Delta = -1$ is left, $\Delta = +1$ is right | §6.2 |
| $(q, x, i)$ | a **configuration**: state, tape contents (trailing blanks not written), head position $i\ge0$; cell 0 is the left end | §6.2 |
| $\Rightarrow$, $\Rightarrow^*$ | one step; zero or more steps. Every run starts at $(\textit{start}, w, 0)$ | §6.2 |
| accepts; rejects; crashes; runs forever | reaches $\textit{accept}$; reaches $\textit{reject}$; moves left from cell 0; none of these, ever. **Halts** means accepts or rejects | §6.2 |
| missing transitions | go to $\textit{reject}$ — say so on an exam | §6.2 |
| — in a transition table's write column | write back the symbol that was read | [[1-models-of-computation/06-turing-machines#63-a-first-example\|§6.3]] |
| $\mathtt{x}$, $\mathtt{\#}$ | this site's marks: a matched symbol; the left end of the tape | §6.3 |
| $\textit{halt}$, $M(w)$, $M(w)\uparrow$ | the single halting state of a machine that computes a function; its output; $M$ diverges on $w$ | [[1-models-of-computation/06-turing-machines#65-computing-functions\|§6.5]] |
| $\Delta = 0$ | a stay-put move — a variant, removed with states $Q\times\{0,1\}$ | [[1-models-of-computation/06-turing-machines#64-variations\|§6.4]] |
| $\delta(p,a)\subseteq Q\times\Gamma\times\{-1,+1\}$ | a nondeterministic machine's options in state $p$ reading $a$ | [[1-models-of-computation/09-nondeterministic-turing-machines#91-definitions\|§9.1]] |
| $\Omega = \{1,\dots,r\}$, $x\in\Omega^*$ | advice symbols and an **advice string**, one choice per step; $r$ is the largest number of options in any $\delta(p,a)$ | [[1-models-of-computation/09-nondeterministic-turing-machines#95-nondeterminism-as-advice\|§9.5]] |

## 7. Encodings and named languages

Named languages, functions and the machines in proofs are set in sans-serif. The font carries no meaning; the definition does.

| notation | meaning | where |
|---|---|---|
| $\langle M\rangle$ | the **encoding** of the machine $M$, a string | [[1-models-of-computation/06-turing-machines#68-universal-turing-machines\|§6.8]], [[1-models-of-computation/07-undecidability#74-code-is-data-data-is-code\|§7.4]] |
| $\langle M, w\rangle$ | the encoding of $M$ together with an input string $w$ | §6.8 |
| $\langle M_1\rangle\langle M_2\rangle$ | two encodings, one after the other (Theorem 14) | [[1-models-of-computation/07-undecidability#710-more-undecidable-languages\|§7.10]] |
| $U$ | the **universal machine**: accepts $\langle M,w\rangle$ iff $M$ accepts $w$, rejects it iff $M$ rejects $w$ | §6.8 |
| $M^R$, $M^A$, $M^H$ | $M$ with accept and reject swapped; with every rejection turned into an endless loop; with every rejection turned into acceptance (Lemma 1) | [[1-models-of-computation/07-undecidability#73-useful-properties\|§7.3]] |
| $\textsf{Accept}(M)$, $\textsf{Reject}(M)$ | the strings $M$ accepts; the strings it rejects | [[1-models-of-computation/07-undecidability#71-acceptable-versus-decidable\|§7.1]] |
| $\textsf{Halt}(M)$, $\textsf{Diverge}(M)$ | $\textsf{Accept}(M)\cup\textsf{Reject}(M)$; everything else, $\Sigma^*\setminus\textsf{Halt}(M)$ — crashes included | §7.1 |
| $\textsf{Accept}$, $\textsf{Reject}$, $\textsf{Halt}$, $\textsf{Diverge}$ | with no argument: languages of **pairs**, such as $\textsf{Halt} = \{\langle M,w\rangle \mid M \text{ halts on } w\}$ | [[1-models-of-computation/07-undecidability#79-the-halting-problem-via-reduction\|§7.9]] |
| $\textsf{SelfAccept}$, $\textsf{SelfReject}$, $\textsf{SelfHalt}$, $\textsf{SelfDiverge}$ | $\{\langle M\rangle \mid M \text{ accepts } \langle M\rangle\}$, and likewise with rejects, halts on, diverges on | [[1-models-of-computation/07-undecidability#75-self-haters-gonna-self-hate\|§7.5]], [[1-models-of-computation/07-undecidability#77-more-self-referential-languages\|§7.7]] |
| $\textsf{NeverAccept}$, $\textsf{NeverReject}$, $\textsf{NeverHalt}$, $\textsf{NeverDiverge}$ | $\{\langle M\rangle \mid \textsf{Accept}(M) = \varnothing\}$, and likewise | §7.10 |
| $\textsf{DivergeSame}$ | $\{\langle M_1\rangle\langle M_2\rangle \mid \textsf{Diverge}(M_1) = \textsf{Diverge}(M_2)\}$ | §7.10 |
| $\mathcal{L}$, $\textsf{AcceptIn}(\mathcal{L})$ | a **property**, that is, a set of languages; $\{\langle M\rangle \mid \textsf{Accept}(M)\in\mathcal{L}\}$. Also $\textsf{RejectIn}$, $\textsf{HaltIn}$, $\textsf{DivergeIn}$, $\textsf{DecideIn}$ | [[1-models-of-computation/07-undecidability#711-rices-theorem\|§7.11]] |
| $\textsf{ThisIsSparta}$, $\textsf{RevAccept}$ | where Rice's theorem does not apply: a behavior (decidable); self-reference (undecidable, by a reduction) | §7.11 |
| $\textsf{NeverLeft}$, $\textsf{LeftThree}$ | behaviors: never moves left (decidable); moves left three times in a row (undecidable) | [[1-models-of-computation/07-undecidability#713-turing-machine-behavior-its-complicated\|§7.13]] |
| $M_w$ | ignores its input and runs $M$ on $w$, so $\textsf{Accept}(M_w)$ is $\Sigma^*$ or $\varnothing$ | §7.10 |
| $M_{\textsf{Accept}}$, $M_{\textsf{Reject}}$, $M_{\textsf{Diverge}}$ | accepts every input at once; rejects every input at once; moves right forever | §7.11 |
| $\textsf{SR}$, $\textsf{DecideL}$, $\textsf{Wrap}$, $\textsf{WTF}$, … | machines in proofs; every machine in a reduction gets its own name | §7.5–§7.11 |
| $\textsf{half}$, $\textsf{swap}$, $\textsf{rev}$ | functions on strings and on expressions | Chapters 1, 2, 4 |
| $\textsf{True}$, $\textsf{False}$ | truth values | |

> [!trap] $\textsf{Accept}(M)$ is not $\textsf{Accept}$
> $\textsf{Accept}(M)$ is a set of strings — the inputs that one machine $M$ accepts. $\textsf{Accept}$ is a set of encodings $\langle M, w\rangle$ — every machine paired with every input it accepts. The first can be any acceptable language; the second is one particular undecidable language.

## 8. Complexity classes

| notation | meaning | where |
|---|---|---|
| $O$, $\Omega$, $\Theta$ | upper, lower and tight asymptotic bounds | |
| $\textsf{TIME}(f(n))$, $\textsf{NTIME}(f(n))$ | the languages decided in $O(f(n))$ time by a deterministic, resp. nondeterministic, multi-tape Turing machine | [[1-models-of-computation/09-nondeterministic-turing-machines#93-time-and-space-complexity\|§9.3]] |
| $\textsf{SPACE}(f(n))$, $\textsf{NSPACE}(f(n))$ | the same, counting tape cells instead of steps | §9.3 |
| $\textsf{P}$, $\textsf{NP}$ | $\bigcup_k\textsf{TIME}(n^k)$ and $\bigcup_k\textsf{NTIME}(n^k)$ | §9.3 |
| verifier, certificate | the deterministic machine and the advice string in the definition of $\textsf{NP}$ | [[1-models-of-computation/09-nondeterministic-turing-machines#96-the-cooklevin-theorem\|§9.6]] |
| $\textsf{SAT}$ | the satisfiable boolean formulas | §9.6 |
| NP-hard, NP-complete | every language in $\textsf{NP}$ reduces to it in polynomial time; NP-hard and in $\textsf{NP}$ | §9.6 |
| $Q_{t,i,q}$, $T_{t,i,a}$, $\Phi_w$ | the Cook–Levin variables ("after $t$ steps, state $q$ with the head on cell $i$"; "cell $i$ holds $a$") and the formula built from them | §9.6 |

## 9. Writing it by hand

| printed | by hand | why |
|---|---|---|
| $\varepsilon$ | a clear epsilon — never $\in$, never $e$ | a missing or extra $\varepsilon$ is the typical one-mistake deduction |
| $\varnothing$ and $\{\varepsilon\}$ | a slashed circle for the empty language; braces around $\varepsilon$ for the one-string language | they are different languages ([[#2-languages\|§2]]) |
| $\mathtt{0}$, `0110` | plain symbols; keep $a, b, c$ and $w, x, y, z$ for variables | a reader must tell explicit strings from variables |
| $\mathtt{0}+\mathtt{1}$ | $+$ on the line, and parentheses whenever in doubt | a raised $^+$ reads as Kleene plus; redundant parentheses are never wrong |
| $\rightsquigarrow$ | a wavy arrow, or anything visibly different from $\to$ | $\to$ writes a rule, $\rightsquigarrow$ a derivation step |
| a DFA | an arrow into the start state, double circles, every edge labeled, and the sentence "missing transitions go to a dump state" if any are missing | these are the "complete description" points of the DFA rubric |
| state names | short words for what the state remembers: $\mathit{last1}$, $\mathit{even}$, $(\mathit{even},\mathit{last1})$ | mnemonic names are 2 of the 10 points |
| $\square$ | a small square | an empty cell in a transition table looks like a missing transition |
| $\langle M\rangle$, $\langle M, w\rangle$ | angle brackets | $M$ is a machine; $\langle M\rangle$ is a string |
| $\textsf{Halt}$, $\textsf{SelfReject}$ | the capitalized name; define a new one in set-builder form | the definition is what a grader checks |
| $\mathcal{L}$ | a script L, or any letter, explicitly defined as a set of languages | Rice's theorem is about a set of languages: say which |
| $\overline{L}$ | a bar over the letter — or $\Sigma^*\setminus L$, which cannot be misread | |

General rules for the write-up itself — no "clearly", every machine named, any result from lecture cited by name — are on [[0-toolkit/06-how-exams-are-graded#10-general-rules|how exams are graded]].

## 10. Same thing, different names

| this site | also called | note |
|---|---|---|
| acceptable | recognizable, semi-decidable, semi-computable, listable, recursively enumerable (r.e.) | the book says *recognizable* in Chapter 6 and *acceptable* from Chapter 7 on |
| decidable | computable, recursive | [[1-models-of-computation/07-undecidability#71-acceptable-versus-decidable\|§7.1]] |
| $M$ accepts $L$ | $M$ recognizes $L$ | [[1-models-of-computation/06-turing-machines#62-formal-definitions\|§6.2]] |
| $M$ decides $L$ | $M$ is a decider for $L$ | §6.2 |
| co-acceptable | "its complement is acceptable" | this site's word, not the book's ([[1-models-of-computation/07-undecidability#73-useful-properties\|§7.3]]) |
| automatic | regular | the same class, by Kleene's theorem; the book uses both words ([[1-models-of-computation/03-finite-state-machines#37-closure-properties\|§3.7]]) |
| DFA | deterministic finite(-state) automaton, finite-state machine | |
| accepting states $A$, start state $s$ | final states $F$, initial state $q_0$ | other textbooks, which also order the tuple differently |
| dump state | trash state (the course rubrics), dead state, sink | |
| $\varepsilon$ | $\lambda$ or $\Lambda$ | some other textbooks |
| $\varepsilon$-transition | $\varepsilon$-move; "epsilon-transition" in this site's headings | |
| $\varepsilon\text{-reach}(q)$ | $\varepsilon$-closure of $q$ | other textbooks |
| subset construction | powerset construction, determinization | [[1-models-of-computation/04-nondeterministic-automata#45-nfa-to-dfa-the-subset-construction\|§4.5]] |
| Thompson's algorithm | Thompson's construction | [[1-models-of-computation/04-nondeterministic-automata#46-regular-expression-to-nfa-thompsons-algorithm\|§4.6]] |
| state elimination | McNaughton and Yamada's algorithm | the book's attribution ([[1-models-of-computation/04-nondeterministic-automata#48-nfa-to-regular-expression-state-elimination\|§4.8]]) |
| Moore's algorithm | table-filling algorithm | [[1-models-of-computation/03-finite-state-machines#310-minimal-automata-moores-algorithm\|§3.10]] |
| $x\equiv_L y$ | Myhill–Nerode (or Nerode) equivalence | §3.9 |
| Kleene star | Kleene closure | |
| nonterminal | non-terminal (the book's usual spelling), variable | [[1-models-of-computation/05-context-free-languages#51-definitions\|§5.1]] |
| production rule | rule, production | §5.1 |
| recursive automaton | — | most other textbooks use pushdown automata instead: a different machine for the same languages ([[1-models-of-computation/05-context-free-languages#57-recursive-automata\|§5.7]]) |
| runs forever | diverges, loops; $M(w)\uparrow$ | a crash also puts the input in $\textsf{Diverge}(M)$ |
| advice string | certificate | for the verifier in the definition of $\textsf{NP}$ (§9.6) |
| $\textsf{Halt}$ | the halting problem | [[concepts/halting-problem\|concept page]] |

## 11. Where this site departs from the book

The changes are small, but each one shows up when you put a chapter page next to the book.

- **The left-end marker.** The Turing machine for $\{\mathtt{0}^n\mathtt{1}^n\mathtt{0}^n \mid n\ge0\}$ marks the left end of the tape with $\mathtt{\#}$; the book's machine writes a dollar sign. The site's machine also checks the format of the input first (extra states $\mathit{block1}$, $\mathit{block2}$, $\mathit{block3}$, $\mathit{rewind}$, $\mathit{mark0}$), because the book's machine, which starts matching at once, also accepts strings such as `001010` (see the trap in [[1-models-of-computation/06-turing-machines#63-a-first-example|§6.3]]).
- **The shift machine's states** are $\mathit{hold0}$ and $\mathit{hold1}$; the book calls them 0 and 1 ([[1-models-of-computation/06-turing-machines#65-computing-functions|§6.5]]).
- **Chomsky normal form.** The nonterminals that protect terminals are $T_a\to a$; the book calls them $A_a$. The final grammar of the running example keeps the book's names $E\to\mathtt{0}$ and $F\to\mathtt{1}$ ([[1-models-of-computation/05-context-free-languages#59-the-cnf-conversion-algorithm|§5.9]]).
- **Grammars as tuples.** $G = (\Sigma,\Gamma,R,S)$ is this site's shorthand; the book lists the four parts without a tuple ([[1-models-of-computation/05-context-free-languages#51-definitions|§5.1]]).
- **The DFA tuple** is always $(\Sigma, Q, s, A, \delta)$ here; the book's order varies from section to section. On an exam, name each component ("start state $s$, accepting states $A$") and the order stops mattering.
- **One word for acceptable.** The site says *acceptable* throughout, where the book's Chapter 6 says *recognizable*, and it adds the word *co-acceptable* ([[1-models-of-computation/07-undecidability#73-useful-properties|§7.3]]).
- **Plainer section titles.** Numbers always match the book, but some titles are descriptive where the book's are jokes or generic: §7.2 "Lo, I Have Become Death, Stealer of Pie" is [[1-models-of-computation/07-undecidability#72-decidable-without-knowing-the-algorithm|"Decidable without knowing the algorithm"]], and §3.3 "Another Example" is [[1-models-of-computation/03-finite-state-machines#33-proving-a-dfa-correct|"Proving a DFA correct"]].
- **Chapter 9.** The site defines $\textsf{P}$ and $\textsf{NP}$ explicitly (the book leaves them implicit), states the rejection half of the advice view with an explicit length $t$, and numbers the Cook–Levin tableau's cells $0,\dots,N+2$, with the input starting at cell 1 between two empty sentinel cells — unlike a Turing machine's tape in Chapter 6, which starts at cell 0 ([[1-models-of-computation/09-nondeterministic-turing-machines#96-the-cooklevin-theorem|§9.6]]).

Related: [[0-toolkit/02-proof-templates|proof templates]] · [[0-toolkit/03-the-big-picture|the big picture]] · [[0-toolkit/06-how-exams-are-graded|how exams are graded]] · [[concepts/strings|strings]] · [[concepts/languages|languages]] · [[concepts/turing-machines|Turing machines]]

### Sources for this page
Erickson, *Models of Computation*, Chapters 1–9, as summarized on the chapter pages of this site, which every row links. The book's own wording — *recognizable* in Chapter 6 and *acceptable* in Chapter 7, its synonym lists, the order of the DFA tuple, the names $A_a$, the dollar sign, 0 and 1, the attribution of state elimination, and the section titles — was checked against the chapter PDFs. The examples are the chapter pages' own, checked there.
