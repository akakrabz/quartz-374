---
title: "Proof templates"
description: "Every exam boilerplate on one page, in course order — string induction, write-ups for regular expressions, grammars and DFAs, structural induction, DFA correctness, product constructions, fooling sets, closure, language transformations, grammar proofs, Turing machines, diagonalization, reductions, Rice's theorem, dovetailing and Lemma 5 — each with its source section, its rubric line and a worked problem."
tags: [toolkit, strings, regular, context-free, turing-machines, undecidability, midterm-1]
aliases: ["templates", "proof template", "exam boilerplate"]
---

*Toolkit · reference page · each template is copied from the section linked below it; the rubric lines paraphrase the course's standard rubrics ([[0-toolkit/06-how-exams-are-graded|how exams are graded]]).*

> [!recipe] How to use a template on the exam
> 1. **Recognize the problem type.** The [[#17-which-template-for-which-problem|table at the end]] maps each type to its template, its rubric and a worked problem.
> 2. **Write the boilerplate first**, word for word, with several blank lines in every case.
> 3. **Fill in the claim and the hypothesis** — or the set $F$, the names of the machines, the states of $M'$ — in full, with variable names that do not clash.
> 4. **Only then think** about the real work (the inductive step, the suffix $z$, the machine $M'$), and write it into the gaps.
> 5. **Reread every line for its reason:** a definition, the hypothesis, a lemma, arithmetic. Never "clearly".
>
> The frame alone earns points: on the induction rubric, an arbitrary string, an explicit strong hypothesis and cases that cover every string are 5 of the 10 points, before any algebra. Templates marked *assembled here* have no boilerplate on their chapter page; they are built from that section's recipe and worked examples, in its words where possible.

**Chapter 1** [[#1-induction-on-strings|string induction]] · **Chapter 2** [[#2-writing-up-a-regular-expression-or-a-grammar|expression or grammar write-up]], [[#3-induction-on-regular-expressions|structural induction]] · **Chapter 3** [[#4-proving-a-dfa-correct|DFA correctness]], [[#5-describing-a-dfa|describing a DFA]], [[#6-writing-up-a-product-construction|product construction]], [[#7-fooling-set-proof|fooling set]], [[#8-non-regularity-by-closure|closure]] · **Chapter 4** [[#9-language-transformation|language transformation]] · **Chapter 5** [[#10-proving-what-a-grammar-generates|what a grammar generates]] · **Chapter 6** [[#11-describing-a-turing-machine|Turing machine]] · **Chapter 7** [[#12-undecidability-by-diagonalization|diagonalization]], [[#13-undecidability-by-reduction|reduction]], [[#14-undecidability-by-rices-theorem|Rice]], [[#15-acceptable-by-dovetailing|dovetailing]], [[#16-not-acceptable-by-lemma-5|Lemma 5]]

## 1. Induction on strings

**Use it for** any claim about every string — the Midterm 1 problem on a newly defined recursive string function, and identities such as $(w\bullet x)^R = x^R\bullet w^R$.

> [!template] Template — induction on strings
> Let $w$ be an arbitrary string. \
> Assume, for every string $x$ with $\lvert x\rvert < \lvert w\rvert$, that *[the claim holds for $x$]*. \
> There are two cases to consider. \
> **Case $w = \varepsilon$.** … Therefore *[the claim holds for $w$]*. \
> **Case $w = ax$** for some symbol $a$ and string $x$. The induction hypothesis implies that *[the claim holds for $x$]*. … Therefore *[the claim holds for $w$]*. \
> In both cases, *[the claim holds for $w$]*. $\blacksquare$

**Variants** ([[1-models-of-computation/01-strings#14-more-than-one-path-up-the-mountain|§1.4]]): peel the last symbol, $w = xa$; split $w = a$ or $w = u\bullet v$ with $u$, $v$ non-empty (two base cases); or follow a definition with more cases, such as $w = abx$ (base cases $\varepsilon$ and every single symbol). If the hypothesis is applied with other values of the other arguments, it must say "for all" of them.

**Source** [[1-models-of-computation/01-strings#13-induction-on-strings|§1.3]] · **rubric** induction, out of 10: 1 arbitrary object · 2 explicit strong hypothesis · 2 exhaustive cases · 1 base cases · 2 correct use of the hypothesis · 2 other details ([[0-toolkit/06-how-exams-are-graded#4-induction|details]]) · **worked** [[problems/induction-on-a-recursive-string-function|sorting a string]]

## 2. Writing up a regular expression or a grammar

**Use it for** "give a regular expression for $L$" (half of the Midterm 1 DFA problem) and "give a context-free grammar for $L$" (half of the non-regularity problem). *Assembled here* from the worked examples of §2.3 and §5.4, which all have this shape.

> [!template] Template — writing up a regular expression or a grammar
> **Idea.** *[how a typical string of $L$ decomposes: into blocks that a star can repeat; by nesting; at the first point where a count balances; or by cases]* \
> **Answer:** *[the expression — or the rules, one line per nonterminal]* \
> **In English:** *[what each piece of the expression stands for — or, for a grammar, a description of the language of every nonterminal that makes sense on its own]* \
> **Test:** *[$\varepsilon$ and the shortest strings of $L$]* are generated; *[short strings outside $L$]* are not.

**Source** [[1-models-of-computation/02-regular-languages#designing-a-regular-expression|§2.3]] (Examples 1 and 2), [[1-models-of-computation/05-context-free-languages#designing-a-grammar|§5.4]] (Examples 1 and 2) · **rubric** regular expressions and grammars: 2 syntax · 8 correctness on exams, with deductions twice the homework ones — 2 for one mistake (often $\varepsilon$), 4 for a few wrong strings, all 8 for infinitely many; $\varnothing$ or $\Sigma^*$ earns nothing; ambiguity costs nothing; homework also needs the English ([[0-toolkit/06-how-exams-are-graded#5-regular-expressions-and-grammars|details]]) · **worked** [[problems/regular-expression-and-dfa-for-one-language|01 exactly twice]] (b), [[problems/fooling-set-and-grammar-for-one-language|fooling set and grammar]] (b)

## 3. Induction on regular expressions

**Use it for** any claim about every regular expression — and, through an expression that represents it, about every regular language ([[1-models-of-computation/02-regular-languages#27-proofs-about-regular-languages|§2.7]]).

> [!template] Template — induction on regular expressions
> Let $R$ be an arbitrary regular expression. \
> Assume that every proper subexpression of $R$ *[has the property]*. \
> There are five cases to consider. \
> **Case $R = \varnothing$.** … Therefore $R$ *[has the property]*. \
> **Case $R$ is a single string** $w$ (possibly $\varepsilon$). … Therefore $R$ *[has the property]*. \
> **Case $R = S+T$** for some regular expressions $S$ and $T$. The induction hypothesis implies that $S$ and $T$ *[have the property]*. … \
> **Case $R = ST$** for some regular expressions $S$ and $T$. The induction hypothesis implies that $S$ and $T$ *[have the property]*. … \
> **Case $R = S^*$** for some regular expression $S$. The induction hypothesis implies that $S$ *[has the property]*. … \
> In all five cases, $R$ *[has the property]*. $\blacksquare$

**Notes.** Inducting on the size of $R$ gives the same five cases. In the case $R = S^*$ the hypothesis covers $S$, not $S^*$. If a case gets stuck, strengthen the claim, as in Lemma 2.5.

**Source** [[1-models-of-computation/02-regular-languages#26-proofs-about-regular-expressions|§2.6]] · **rubric** induction ([[0-toolkit/06-how-exams-are-graded#4-induction|details]]) · **worked** the proof of Lemma 2.4 in [[1-models-of-computation/02-regular-languages#26-proofs-about-regular-expressions|§2.6]]

## 4. Proving a DFA correct

**Use it for** "prove that your DFA accepts exactly $L$". Midterm-1-style DFA problems need no proof, but the meanings of step 1 are exactly what mnemonic state names should convey.

> [!template] Template — proving $L(M) = L$ for a DFA
> 1. **Give each state $q$ a meaning** $P_q$, and claim: "$\delta^*(s,w) = q$ if and only if $w$ has property $P_q$."
> 2. **Induct on $w$.** Either peel the *first* symbol ($w = ax$) — then state the claim for every possible start state, as in §3.3 — or peel the *last* symbol ($w = xa$) and use $\delta^*(s,xa) = \delta(\delta^*(s,x),a)$, which needs the claim only from $s$.
> 3. **Conclude:** $w\in L(M) \iff \delta^*(s,w)\in A \iff w$ has one of the accepting properties $\iff w\in L$.

**Source** [[1-models-of-computation/03-finite-state-machines#33-proving-a-dfa-correct|§3.3]] · **rubric** induction ([[0-toolkit/06-how-exams-are-graded#4-induction|details]]) · **worked** the odd-number-of-1s proof in [[1-models-of-computation/03-finite-state-machines#33-proving-a-dfa-correct|§3.3]]; state meanings in [[problems/regular-expression-and-dfa-for-one-language|01 exactly twice]] (a)

## 5. Describing a DFA

**Use it for** "give a DFA for $L$; no proof required" — with a regular expression for the same language, one of the five Midterm 1 problems. *Assembled here* from §3.2, §3.5 and the DFA rubric.

> [!template] Template — describing a DFA
> *[A drawing: an arrow from nowhere into the start state, double circles on the accepting states, a label on every edge — or, in text, the start state, the accepting states and the complete transition table.]* \
> *"All missing transitions go to a dump state."* *[Only if some are missing.]* \
> **States:** *[for each state, a mnemonic name and what it remembers about the input read so far — e.g. "$\mathit{last1}$: no `11` yet, and the last symbol read was `1`"]*.

**Source** [[1-models-of-computation/03-finite-state-machines#32-formal-definitions|§3.2]] (a total transition function; the dump state), [[1-models-of-computation/03-finite-state-machines#35-designing-dfas-dfas-are-algorithms|§3.5]] (name each state after what it remembers) · **rubric** DFAs: 2 unambiguous, complete description · 6 correctness (on exams) · 2 mnemonic state names; an NFA where a DFA was asked earns half credit ([[0-toolkit/06-how-exams-are-graded#6-dfas-and-nfas|details]]) · **worked** [[problems/regular-expression-and-dfa-for-one-language|01 exactly twice]] (a)

## 6. Writing up a product construction

**Use it for** a DFA for "$L_1$ and $L_2$", "$L_1$ or $L_2$", "$L_1$ but not $L_2$" — any boolean combination of languages that have simple DFAs.

> [!template] Template — writing up a product construction
> Let $M_1 = (\Sigma, Q_1, s_1, A_1, \delta_1)$ be a DFA for $L_1$: *[its states and what each means, start, accepting states, transitions — or a drawing]*. \
> Let $M_2 = (\Sigma, Q_2, s_2, A_2, \delta_2)$ be a DFA for $L_2$: *[likewise]*. \
> Define $M := (\Sigma,\ Q_1\times Q_2,\ (s_1,s_2),\ A,\ \delta)$ with $\delta((p,q),a) := (\delta_1(p,a),\delta_2(q,a))$, \
> and with $A$ := *[the accepting pairs from the table]*. \
> By Lemma 3.1, $M$ accepts $w$ iff *[the boolean combination]*, so $L(M) =$ *[the target language]*.

**Source** [[1-models-of-computation/03-finite-state-machines#36-the-product-construction|§3.6]] (the definition, the table of accepting sets, Lemma 3.1, how it is graded); the template is the one on [[concepts/product-construction|product construction]] · **rubric** DFAs — for a product, the complete description defines each factor completely, then the product's states, start state, transitions and accepting states ([[0-toolkit/06-how-exams-are-graded#6-dfas-and-nfas|details]]) · **worked** [[problems/a-product-construction-written-formally|a product, written formally]]

## 7. Fooling-set proof

**Use it for** "prove that $L$ is not regular" — on Midterm 1, paired with a grammar for the same language.

> [!template] Template — fooling-set proof (as in Lemma 3.6)
> Let $F = $ *[an explicit infinite set, e.g. $\mathtt{0}^*$]*. \
> Let $x$ and $y$ be arbitrary distinct strings in $F$. \
> The definition of $F$ implies $x = $ *[…]* and $y = $ *[…]* for some integers $i\ne j$. \
> Let $z = $ *[a suffix that may depend on $i$ and $j$]*. \
> Then $xz = $ *[…]* $\in L$, because *[…]*. \
> And $yz = $ *[…]* $\notin L$, because *[…]*. \
> So $z$ distinguishes $x$ and $y$. We conclude that $F$ is a fooling set for $L$. \
> Because $F$ is infinite, $L$ cannot be regular. $\blacksquare$

**Choosing $F$.** A simple language with one star and no union — $\mathtt{0}^*$, $\mathtt{1}\mathtt{0}^*\mathtt{1}$, $(\mathtt{01})^*$ — or $L$ itself; the standard cases are tabulated in §3.8. Keep $i\ne j$: "$i<j$" needs "without loss of generality" *and* a symmetric argument.

**Source** [[1-models-of-computation/03-finite-state-machines#38-proving-a-language-is-not-regular|§3.8]] · **rubric** fooling sets: 4 an explicit infinite set that really is a fooling set (a finite set earns nothing) · 2 explicit suffix $z$ · 2 one of $xz$, $yz$ in $L$ · 2 the other not ([[0-toolkit/06-how-exams-are-graded#7-fooling-sets|details]]) · **worked** [[problems/fooling-set-and-grammar-for-one-language|fooling set and grammar]] (a)

## 8. Non-regularity by closure

**Use it for** a short non-regularity proof when the problem does not prescribe a method, and for true/false justifications. *Assembled here* from "the closure alternative" in §3.8.

> [!template] Template — non-regularity by closure
> Suppose for the sake of argument that $L$ is regular. \
> The language $R = $ *[e.g. $\mathtt{0}^*\mathtt{1}^*$]* is regular, because *[it is described by a regular expression]*. \
> Regular languages are closed under *[intersection, complement, …]*, so $L' = $ *[e.g. $L\cap R$]* is regular too. \
> But $L' = $ *[a language known to be non-regular, e.g. $\{\mathtt{0}^n\mathtt{1}^n \mid n\ge0\}$]*, which is not regular by *[Lemma 3.6, or a fooling set]*. \
> This contradiction shows that $L$ is not regular. $\blacksquare$

**Only in this direction:** if $L\cap R$ turns out to be regular, nothing follows about $L$.

**Source** [[1-models-of-computation/03-finite-state-machines#38-proving-a-language-is-not-regular|§3.8]], [[concepts/closure-properties|closure properties]] · **rubric** none of its own — a problem that asks for a fooling set wants a fooling set · **worked** the closure alternative in [[problems/fooling-set-and-grammar-for-one-language|fooling set and grammar]]

## 9. Language transformation

**Use it for** "prove that $f(L)$ is regular for every regular language $L$" — the two-part Midterm 1 problem.

> [!template] Template — regular language transformation
> Let $M = (\Sigma, Q, s, A, \delta)$ be a DFA that accepts $L$. \
> We construct an NFA $M' = (\Sigma, Q', s', A', \delta')$ with $\varepsilon$-transitions that accepts *[the new language]*. \
> **In English:** $M'$ remembers *[each component of its state, and what it means]*, guesses *[what, and when]*, and accepts when *[…]*. \
> **Formally:** $Q' = $ *[…]*, $s' = $ *[…]*, $A' = $ *[…]*, \
> $\delta'(q', a) = $ *[…]* for every state $q'$ and every symbol $a$, \
> $\delta'(q', \varepsilon) = $ *[…]* for every state $q'$ (write $\varnothing$ where there are none). \
> **Why:** $M'$ can be in state *[…]* after reading $x$ if and only if *[…]*; so it accepts exactly *[the new language]*.

**Which kind of language?** For "strings whose transform is in $L$", $\{w \mid f(w)\in L\}$, usually a DFA that simulates $M$ on $f(w)$ while reading $w$. For "transforms of strings in $L$", $\{f(w) \mid w\in L\}$, usually an NFA that simulates $M$ on a guessed preimage, with $\varepsilon$-transitions guessing the symbols that $f$ deleted.

**Source** [[1-models-of-computation/04-nondeterministic-automata#49-regular-language-transformations|§4.9]] (Lemmas 4.4 and 4.5), where this template is copied from; a shorter version is on [[concepts/language-transformations|language transformations]] · **rubric** transformations: 2 formal, complete description of $M'$ built from an arbitrary DFA $M$ (say DFA or NFA; list the $\varepsilon$-transitions) · 2 English explanation of the states and accepting states · 6 correctness — 1 states, 1 start state, 1 accepting states, 3 transitions; test $L = \varnothing$, $\{\varepsilon\}$, $\mathtt{1}^*$, $\Sigma^*$ ([[0-toolkit/06-how-exams-are-graded#8-language-transformations|details]]) · **worked** [[problems/two-language-transformations|insert and delete a 1]]

## 10. Proving what a grammar generates

**Use it for** "prove that $G$ generates exactly $L$" — and for convincing yourself that a grammar you designed is right.

> [!template] Template — proving $L(G) = L$
> 1. **State the language of every nonterminal.** If nonterminals use each other, the claims must be proved together, in one induction (mutual induction, §5.3).
> 2. **$L\subseteq L(G)$.** Let $w\in L$ be arbitrary; assume every shorter string of $L$ is generated (or induct on a parameter, like $n$ in Lemma 5.1). Split $w$ into pieces that match the right side of one rule, apply the hypothesis to the pieces, and assemble a derivation $S\rightsquigarrow\omega\rightsquigarrow^* w$.
> 3. **$L(G)\subseteq L$.** Let $w\in L(G)$ be arbitrary and fix a derivation of $w$; assume every shorter generated string is in $L$. Write one case per rule the derivation can start with; in each case $w$ splits into pieces derived from the symbols of the right side, the hypothesis applies to each piece, and the pieces together satisfy the definition of $L$.
> 4. **If the grammar has $\varepsilon$-rules,** fix a *shortest* derivation of $w$ (§5.3, "Careful with those epsilons"), or induct on the length of the derivation instead of the string.

**Source** [[1-models-of-computation/05-context-free-languages#53-from-grammar-to-language|§5.3]] (Lemmas 5.1–5.4; [[1-models-of-computation/05-context-free-languages#careful-with-those-epsilons|careful with those epsilons]]; [[1-models-of-computation/05-context-free-languages#mutual-induction|mutual induction]]) · **rubric** two inductions, each graded like an induction ([[0-toolkit/06-how-exams-are-graded#4-induction|details]]) · **worked** [[problems/proving-what-a-grammar-generates|a grammar proof]]

## 11. Describing a Turing machine

Chapter 6 gives a recipe rather than a boilerplate. A design answer should contain:

1. the algorithm in English, phase by phase — scan, mark, walk back;
2. a transition table or diagram that implements exactly that description, with mnemonic state names and a one-line meaning for every state;
3. the sentence "missing transitions reject";
4. a trace on $\varepsilon$, on a short string in the language, and on a near-miss.

**Source** [[1-models-of-computation/06-turing-machines#63-a-first-example|§6.3]] (the design recipe and "Writing a Turing machine on an exam") · **rubric** none of its own; the DFA rubric's demands — a complete, unambiguous description and mnemonic names — are the guide · **worked** [[problems/designing-a-turing-machine|the copy language]]

## 12. Undecidability by diagonalization

**Use it for** self-referential languages — defined by what a machine does with its own encoding — when no known undecidable language is easier to reduce from.

> [!template] Template — undecidability by diagonalization
> Suppose for the sake of argument that some Turing machine $\textsf{Dec}$ decides $L$. \
> Build a new machine $\textsf{Wrap}$ from $\textsf{Dec}$: *[swap $\textsf{Dec}$'s accept and reject states / redirect its accepting transitions to a looping state / …]*. \
> Then for every Turing machine $M$: $\textsf{Wrap}$ *[accepts, or halts on]* $\langle M\rangle$ if and only if $M$ *[does not …]* $\langle M\rangle$. \
> In particular, take $M = \textsf{Wrap}$. \
> If $\textsf{Wrap}$ *[accepts]* $\langle\textsf{Wrap}\rangle$, then by the line above $\textsf{Wrap}$ does not *[accept]* $\langle\textsf{Wrap}\rangle$ — a contradiction. \
> If $\textsf{Wrap}$ does not *[accept]* $\langle\textsf{Wrap}\rangle$, then by the line above $\textsf{Wrap}$ *[accepts]* $\langle\textsf{Wrap}\rangle$ — a contradiction. \
> So $\textsf{Dec}$ does not exist, and $L$ is undecidable. $\blacksquare$

**Against an acceptor** (to prove $L$ not acceptable, as in Theorem 9): assume only that $\textsf{Dec}$ accepts $L$, turn its rejections into endless loops (Lemma 1), and derive "$\textsf{Wrap}$ halts on $\langle\textsf{Wrap}\rangle$ if and only if it diverges on $\langle\textsf{Wrap}\rangle$".

**Source** [[1-models-of-computation/07-undecidability#77-more-self-referential-languages|§7.7]] (the template, Theorems 7–9), [[1-models-of-computation/07-undecidability#75-self-haters-gonna-self-hate|§7.5]] (Theorem 6, the model argument) · **rubric** diagonalization: 4 wrapper machine · 6 contradiction, 3 per case ([[0-toolkit/06-how-exams-are-graded#diagonalization|details]]) · **worked** the proof of Theorem 6 in [[1-models-of-computation/07-undecidability#75-self-haters-gonna-self-hate|§7.5]]; a doubled input on [[concepts/diagonalization|diagonalization]]

## 13. Undecidability by reduction

**Use it for** "prove that $L$ is undecidable" when $L$ is not self-referential: reduce from $\textsf{Accept}$, $\textsf{Halt}$, or any language already known to be undecidable.

> [!template] Template — undecidability by reduction from $\textsf{Accept}$
> Suppose for the sake of argument that some Turing machine $\textsf{DecideL}$ decides $L$. \
> Consider the following machine $\textsf{DecideAccept}$. Given $\langle M, w\rangle$, it writes the encoding $\langle M'\rangle$ of the machine \
> $\quad M'(x)$: *[for example: ignore $x$; run $M$ on $w$; then …]* \
> and then runs $\textsf{DecideL}$ on $\langle M'\rangle$ and returns its answer. \
> $\Rightarrow$ Suppose $M$ accepts $w$. Then $M'$ *[…]*, so $\langle M'\rangle\in L$. So $\textsf{DecideL}$ accepts $\langle M'\rangle$, and $\textsf{DecideAccept}$ accepts $\langle M, w\rangle$. \
> $\Leftarrow$ Suppose $M$ does not accept $w$ — it rejects or diverges. Then $M'$ *[…]*, so $\langle M'\rangle\notin L$. So $\textsf{DecideL}$ rejects $\langle M'\rangle$, and $\textsf{DecideAccept}$ rejects $\langle M, w\rangle$. \
> In both cases $\textsf{DecideAccept}$ is correct, and it always halts. So $\textsf{DecideAccept}$ decides $\textsf{Accept}$, which is impossible. \
> We conclude that $\textsf{DecideL}$ does not exist: $L$ is undecidable. $\blacksquare$

**Opposite answers.** If $\langle M'\rangle\in L$ exactly when $M$ does *not* accept $w$, let $\textsf{DecideAccept}$ return the opposite of $\textsf{DecideL}$'s answer, as in the proof of Theorem 13 ([[1-models-of-computation/07-undecidability#710-more-undecidable-languages|§7.10]]).

**Source** [[1-models-of-computation/07-undecidability#79-the-halting-problem-via-reduction|§7.9]] · **rubric** reduction: 4 the reduction (the new decider and $M'$, in the right direction) · 3 for each direction ([[0-toolkit/06-how-exams-are-graded#reduction|details]]) · **worked** [[problems/undecidability-by-reduction-and-by-rice|AtLeastTwo]] (a); Theorem 13 in [[1-models-of-computation/07-undecidability#710-more-undecidable-languages|§7.10]]

## 14. Undecidability by Rice's theorem

**Use it for** $\{\langle M\rangle \mid \textsf{Accept}(M) \text{ has some property}\}$ — a property of the language $M$ accepts, not of $M$ or of its behavior. *Assembled here* from the recipe "Using Rice's theorem" in §7.11.

> [!template] Template — undecidability by Rice's theorem
> Let $\mathcal{L} := $ *[an explicit set of languages]*, so that the language in question is $\textsf{AcceptIn}(\mathcal{L}) = \{\langle M\rangle \mid \textsf{Accept}(M)\in\mathcal{L}\}$. *[Check: two machines with the same language are both in it or both out.]* \
> Let $Y := $ *[a concrete machine, e.g. $M_{\textsf{Accept}}$]*. Then $\textsf{Accept}(Y) = $ *[…]* $\in\mathcal{L}$, because *[…]*. \
> Let $N := $ *[a concrete machine, e.g. $M_{\textsf{Reject}}$]*. Then $\textsf{Accept}(N) = $ *[…]* $\notin\mathcal{L}$, because *[…]*. \
> By Rice's theorem, $\textsf{AcceptIn}(\mathcal{L})$ is undecidable. $\blacksquare$

**Variants.** If membership depends on $\textsf{Reject}(M)$, $\textsf{Halt}(M)$ or $\textsf{Diverge}(M)$, or on the language $M$ decides, use $\textsf{RejectIn}$, $\textsf{HaltIn}$, $\textsf{DivergeIn}$ or $\textsf{DecideIn}$ throughout, and describe $Y$ and $N$ by that language. **Not for** behavior ($\textsf{ThisIsSparta}$ is decidable), self-reference ($\textsf{RevAccept}$ needs a reduction) or trivial properties — and Rice's theorem never proves "not acceptable".

**Source** [[1-models-of-computation/07-undecidability#711-rices-theorem|§7.11]] (the recipe, Corollary 15, the variants) · **rubric** Rice: 4 a machine whose language has the property · 4 a machine whose language does not · 2 details, including the right variant of the theorem ([[0-toolkit/06-how-exams-are-graded#rices-theorem|details]]) · **worked** [[problems/undecidability-by-reduction-and-by-rice|AtLeastTwo]] (b); the witnesses of Corollary 15 in [[1-models-of-computation/07-undecidability#711-rices-theorem|§7.11]]

## 15. Acceptable by dovetailing

**Use it for** "prove that $L$ is acceptable" when membership of $\langle M\rangle$ is witnessed by finitely many accepting runs of $M$ — "$\textsf{Accept}(M)\ne\varnothing$", "$M$ accepts at least two strings". *Assembled here* from §7.10 and §9.5.

> [!template] Template — acceptable by dovetailing
> The following machine accepts $L$. Given $\langle M\rangle$ *[if the input encodes no machine, reject]*: \
> for $t = 1, 2, 3, \ldots$, run $M$ for $t$ steps on each of the first $t$ strings of $\Sigma^*$ *[in shortlex order]*, and accept as soon as *[the runs so far show membership, e.g. two different strings have been accepted]*. \
> If $\langle M\rangle\in L$: *[the witnesses $x_1,\dots,x_k$]* are each accepted within some $s$ steps, so in round $t = $ *[the largest of $s$ and the positions of $x_1,\dots,x_k$]* all of them run long enough, and the machine accepts. \
> If $\langle M\rangle\notin L$: no round ever *[shows membership]*, so the machine never accepts — it runs forever, which an acceptor may do. $\blacksquare$

**Why not one string at a time?** If $M$ runs forever on the first string tried, the search never reaches the others. **Simpler cases** need no dovetailing: $\textsf{SelfAccept}$ is accepted by running $U$ on $\langle M, \langle M\rangle\rangle$ (Theorem 10).

**Source** [[1-models-of-computation/07-undecidability#710-more-undecidable-languages|§7.10]] (an acceptor for the complement of $\textsf{NeverAccept}$), [[1-models-of-computation/09-nondeterministic-turing-machines#95-nondeterminism-as-advice|§9.5]] (dovetailing) · **rubric** none of its own · **worked** [[problems/undecidability-by-reduction-and-by-rice|AtLeastTwo]] (d)

## 16. Not acceptable, by Lemma 5

**Use it for** "prove that $L$ is not acceptable" when its complement is acceptable but undecidable — $\textsf{NeverAccept}$, $\textsf{Diverge}$, the complement of $\textsf{SelfAccept}$. *Assembled here* from Lemma 5 and its consequence in §7.3.

> [!template] Template — not acceptable, by Lemma 5
> The complement $\overline{L} = \Sigma^*\setminus L$ is acceptable: *[a machine that accepts it — run $U$, or dovetail]*. \
> $\overline{L}$ is undecidable: *[by diagonalization, a reduction or Rice's theorem — or because $L$ is undecidable, and decidable languages are closed under complement]*. \
> If $L$ were acceptable too, the acceptable language $\overline{L}$ would have an acceptable complement, so it would be decidable by Lemma 5 — a contradiction. \
> So $L$ is not acceptable. $\blacksquare$

Strings that encode no machine form a decidable set; counting them in $L$ or in $\overline{L}$ changes nothing. **Other routes:** diagonalization against an acceptor (Theorem 9), or Lemma 17 for a property that is not monotone ([[1-models-of-computation/07-undecidability#712-the-ricemcnaughtonmyhillshapiro-theorem|§7.12]]).

**Source** [[1-models-of-computation/07-undecidability#73-useful-properties|§7.3]] · **rubric** none of its own · **worked** [[problems/undecidability-by-reduction-and-by-rice|AtLeastTwo]] (d); $\textsf{NeverAccept}$ in [[1-models-of-computation/07-undecidability#710-more-undecidable-languages|§7.10]]

## 17. Which template for which problem

| problem | template | rubric, out of 10 | worked problem |
|---|---|---|---|
| a new recursive string function: prove a property (Midterm 1) | [[#1-induction-on-strings\|string induction]] | induction: 1 + 2 + 2 + 1 + 2 + 2 | [[problems/induction-on-a-recursive-string-function\|sorting a string]] |
| a claim about every regular expression or regular language | [[#3-induction-on-regular-expressions\|structural induction]] | induction | Lemma 2.4, [[1-models-of-computation/02-regular-languages#26-proofs-about-regular-expressions\|§2.6]] |
| a DFA for a described language, no proof (Midterm 1) | [[#5-describing-a-dfa\|describing a DFA]] | DFA: 2 + 6 + 2 | [[problems/regular-expression-and-dfa-for-one-language\|01 exactly twice]] (a) |
| a regular expression for the same language (Midterm 1) | [[#2-writing-up-a-regular-expression-or-a-grammar\|write-up]] | expression: 2 + 8 | [[problems/regular-expression-and-dfa-for-one-language\|01 exactly twice]] (b) |
| prove a DFA correct | [[#4-proving-a-dfa-correct\|DFA correctness]] | induction | [[1-models-of-computation/03-finite-state-machines#33-proving-a-dfa-correct\|§3.3]] |
| a DFA for an "and", "or" or "but not" condition | [[#6-writing-up-a-product-construction\|product construction]] | DFA: 2 + 6 + 2 | [[problems/a-product-construction-written-formally\|product, written formally]] |
| an NFA turned into a DFA | recipe in [[1-models-of-computation/04-nondeterministic-automata#45-nfa-to-dfa-the-subset-construction\|§4.5]] | DFA, when the answer is a DFA | [[problems/subset-construction-by-hand\|subset construction]] |
| a DFA or NFA turned into a regular expression | recipe in [[1-models-of-computation/04-nondeterministic-automata#48-nfa-to-regular-expression-state-elimination\|§4.8]] | expression: 2 + 8 | [[problems/state-elimination-by-hand\|state elimination]] |
| $L$ is not regular (Midterm 1) | [[#7-fooling-set-proof\|fooling set]]; [[#8-non-regularity-by-closure\|closure]] if the method is free | fooling set: 4 + 2 + 2 + 2 | [[problems/fooling-set-and-grammar-for-one-language\|fooling set and grammar]] (a) |
| $f(L)$ is regular whenever $L$ is (Midterm 1, two parts) | [[#9-language-transformation\|transformation]] | transformation: 2 + 2 + 6 | [[problems/two-language-transformations\|insert and delete a 1]] |
| a grammar for a described language (Midterm 1) | [[#2-writing-up-a-regular-expression-or-a-grammar\|write-up]] | grammar: 2 + 8 | [[problems/fooling-set-and-grammar-for-one-language\|fooling set and grammar]] (b) |
| prove $L(G) = L$ | [[#10-proving-what-a-grammar-generates\|two inclusions]] | two inductions | [[problems/proving-what-a-grammar-generates\|a grammar proof]] |
| convert a grammar to Chomsky normal form | recipe in [[1-models-of-computation/05-context-free-languages#59-the-cnf-conversion-algorithm\|§5.9]] | none of its own | [[problems/cnf-conversion-step-by-step\|CNF, step by step]] |
| design a Turing machine | [[#11-describing-a-turing-machine\|description]] | none of its own | [[problems/designing-a-turing-machine\|the copy language]] |
| undecidable, self-referential | [[#12-undecidability-by-diagonalization\|diagonalization]] | diagonalization: 4 + 3 + 3 | Theorem 6, [[1-models-of-computation/07-undecidability#75-self-haters-gonna-self-hate\|§7.5]] |
| undecidable, by reduction | [[#13-undecidability-by-reduction\|reduction]] | reduction: 4 + 3 + 3 | [[problems/undecidability-by-reduction-and-by-rice\|AtLeastTwo]] (a) |
| undecidable, a property of $\textsf{Accept}(M)$ | [[#14-undecidability-by-rices-theorem\|Rice]] | Rice: 4 + 4 + 2 | [[problems/undecidability-by-reduction-and-by-rice\|AtLeastTwo]] (b) |
| acceptable | [[#15-acceptable-by-dovetailing\|dovetailing]] | none of its own | [[problems/undecidability-by-reduction-and-by-rice\|AtLeastTwo]] (d) |
| not acceptable | [[#16-not-acceptable-by-lemma-5\|Lemma 5]] | none of its own | [[problems/undecidability-by-reduction-and-by-rice\|AtLeastTwo]] (d) |

The point splits are explained, with what loses points, on [[0-toolkit/06-how-exams-are-graded|how exams are graded]]; the symbols are on [[0-toolkit/01-notation-and-conventions|notation and conventions]].

### Sources for this page
The templates for string induction, structural induction, DFA correctness, fooling sets, grammar proofs, diagonalization and reduction are copied from the chapter sections linked under them; the product-construction and language-transformation templates from [[concepts/product-construction|product construction]] and [[concepts/language-transformations|language transformations]] (the second follows the method of §4.9). Context words that pointed elsewhere on their page ("as above", "below", "next subsection") were replaced by section numbers; nothing else changed. The templates marked *assembled here* are built from the recipes and worked examples of the sections they cite. Rubric lines paraphrase the CS/ECE 374 A (Fall 2026) standard rubrics.
