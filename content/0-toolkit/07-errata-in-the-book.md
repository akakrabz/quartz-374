---
title: "Errata in the book"
description: "Slips in Erickson's Models of Computation (December 2018 edition) found while writing this site: a wrong move in a printed Turing machine, a misprinted string, a CNF rule that is too weak, an off-by-one in the Cook–Levin tableau, and a few more — each with the correction and the section here that has it right."
tags: [toolkit, regular, context-free, turing-machines, undecidability, complexity]
aliases: ["errata", "book errata", "typos in the book"]
---

The book is careful, and every item below is small. They are listed because each one can cost points if it is copied onto a cheat sheet or used to check an answer. Every item was confirmed against the chapter PDF (cover date December 28, 2018), and every concrete one is also checked by the site's scripts. Only items that would change an answer are listed — no spelling.

> [!tip] How to read this page
> "As printed" is what the PDF says; "should be" is what this site uses. The last column links the section here that has the corrected version and explains it. If the book is updated, some items may disappear: the [chapter PDFs](https://jeffe.cs.illinois.edu/teaching/algorithms/#models) are the reference.

## Chapter 4 · Nondeterministic automata

| where | as printed | should be | why it matters |
|---|---|---|---|
| §4.7, Thompson's NFA for $(\mathtt{0}+\mathtt{1})^*(\mathtt{00}+\mathtt{11})(\mathtt{0}+\mathtt{1})^*$ | the text calls it an "18-state" NFA | the figure and the subset-construction table use the literal 26-state construction (states $a$ to $z$); 18 is the count if each $\mathtt{0}+\mathtt{1}$ is drawn as one two-state gadget | Thompson's algorithm makes 2 states per symbol, union and star — [[1-models-of-computation/04-nondeterministic-automata#47-another-example\|§4.7]] |

## Chapter 5 · Context-free languages

| where | as printed | should be | why it matters |
|---|---|---|---|
| §5.9, CNF conversion step 0 | the new start symbol $S'\to S$ is needed only when $S\rightsquigarrow^*\varepsilon$, and is dropped again otherwise | also needed whenever $S$ appears on a right side | for $S\to\mathtt{0}S\mid\mathtt{1}$, dropping $S'$ leaves the start symbol on a right side, which CNF forbids — [[1-models-of-computation/05-context-free-languages#59-the-cnf-conversion-algorithm\|§5.9]] |

## Chapter 6 · Turing machines

| where | as printed | should be | why it matters |
|---|---|---|---|
| §6.3, transition table of the $\mathtt{0}^n\mathtt{1}^n\mathtt{0}^n$ machine | after marking a 0, state *seek0* moves right ($+1$) | moves left ($-1$), as the text and its traces do | with $+1$ the machine rejects `010`, which is in the language — [[1-models-of-computation/06-turing-machines#63-a-first-example\|§6.3]] |
| §6.3, the same machine | presented as a machine for $\{\mathtt{0}^n\mathtt{1}^n\mathtt{0}^n\}$ | even with the left move, it accepts strings outside the language — `001010` and 17 others of length at most 12 — because it never checks that the input has the form $\mathtt{0}^*\mathtt{1}^*\mathtt{0}^*$; and it rejects $\varepsilon$, which is in the language | a decider needs a format check first; the site's 12-state machine has one — [[1-models-of-computation/06-turing-machines#63-a-first-example\|§6.3]] |
| §6.8, encoding example | lists $\langle\textit{start}\rangle = \mathtt{111}$, but writes *start* as `001` inside the encoded transitions | `111` everywhere (the start state is coded by all 1s) | reading or writing $\langle M\rangle$ — [[1-models-of-computation/06-turing-machines#68-universal-turing-machines\|§6.8]] |
| §6.8, the universal machine | fixes codes for *start* (all 1s) and *reject* (all 0s) only | $U$ must also recognize *accept*; this site uses $\langle\textit{accept}\rangle = \mathtt{0}\cdots\mathtt{01}$ | a gap rather than an error — [[1-models-of-computation/06-turing-machines#68-universal-turing-machines\|§6.8]] |

## Chapter 7 · Undecidability

| where | as printed | should be | why it matters |
|---|---|---|---|
| §7.12, the Rice–McNaughton–Myhill–Shapiro theorem | $\mathcal{L}$ is monotone if every superset of a language in $\mathcal{L}$ is in $\mathcal{L}$ | every **acceptable** superset | $\mathcal{L}$ contains only acceptable languages, so read literally no non-empty $\mathcal{L}$ would be monotone; Lemma 17's proof uses the acceptable version — [[1-models-of-computation/07-undecidability#712-the-ricemcnaughtonmyhillshapiro-theorem\|§7.12]] |

## Chapter 8 · Universal models

| where | as printed | should be | why it matters |
|---|---|---|---|
| §8.5, Post's correspondence problem | both rows of the solution $c, b, c, a$ spell `110110100` | `110011100` | checking a PCP solution by hand — [[1-models-of-computation/08-universal-models#85-posts-correspondence-problem\|§8.5]] |

## Chapter 9 · Nondeterministic Turing machines

| where | as printed | should be | why it matters |
|---|---|---|---|
| §9.5, nondeterminism as advice | $N$ rejects $w$ if and only if $M$ rejects $(w, x)$ for **every** advice string $x$ | $N$ rejects $w$ if and only if, for some length $t$, $M$ rejects $(w, x)$ within $t$ steps for every advice string $x$ of length $t$ | the printed version fails when the computation tree has an infinite branch, whatever $M$ does when the advice runs out — [[1-models-of-computation/09-nondeterministic-turing-machines#95-nondeterminism-as-advice\|§9.5]] |
| §9.6, the Cook–Levin tableau | cells $0, \dots, N+1$ | cells $0, \dots, N+2$: the head starts on cell 1 and can reach cell $N+1$ at time $N$, and cells $0$ and $N+2$ are empty sentinels | with the printed range, a run whose head ends on cell $N+1$ is not represented — [[1-models-of-computation/09-nondeterministic-turing-machines#96-the-cooklevin-theorem\|§9.6]] |
| §9.6, the transition constraints | a few right-hand sides refer to time $t$ (for example $T_{t,i-1,a}$), and the left boundary is written with cell $i$ | every variable on the right of a transition constraint refers to time $t-1$; the left boundary is cell $0$ | a constraint at time $t$ must be determined by the configuration at time $t-1$ — [[1-models-of-computation/09-nondeterministic-turing-machines#96-the-cooklevin-theorem\|§9.6]] |

## Not errors, but easy to trip over

- **State elimination's name.** Some summaries call §4.8's method "Han and Wood's algorithm"; the current book credits the idea to McNaughton and Yamada (1960), with Lee (1960) and Kleene (1951) before them. Same algorithm — [[concepts/state-elimination]].
- **Thompson's star gadget.** The book closes the loop of $S^*$ from the new accepting state back to the new start state; many other sources loop from $t_S$ back to $s_S$. Both are correct and have the same size; only some $\varepsilon$-reaches differ — [[concepts/thompsons-algorithm]].
- **"Recognizable" and "acceptable".** Chapter 6 says *recognizable*, Chapter 7 says *acceptable*; they mean the same — [[0-toolkit/01-notation-and-conventions]].

### Sources for this page

Each item was found by the writer or the independent reviewer of the page linked in its row, read against Erickson, *Models of Computation*, chapter PDFs of December 28, 2018. The concrete ones are checked by scripts: the §4.7 state counts by `tools/checks/ch04.py`; the CNF counterexample by `tools/checks/ch05.py`; the §6.3 machine (with both moves) and the §6.8 encodings by `tools/checks/ch06.py`; the PCP string by `tools/checks/ch08.py`; the advice-view counterexample and the Cook–Levin tableau (with both cell ranges) by `tools/checks/ch09.py`.
