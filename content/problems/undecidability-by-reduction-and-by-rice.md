---
title: "Worked problem — Undecidability by reduction and by Rice's theorem"
description: "AtLeastTwo = {⟨M⟩ : M accepts at least two different strings} is undecidable, proved twice: by a reduction from Accept with every machine named, and by Rice's theorem with explicit witnesses. A look-alike time-bounded property is decidable, and AtLeastTwo is acceptable by dovetailing while its complement is not."
tags: [problem, undecidability]
---

*Problem · style of an undecidability problem (Chapter 7 material, on the final exam) · uses [[1-models-of-computation/07-undecidability#79-the-halting-problem-via-reduction|§7.9]], [[1-models-of-computation/07-undecidability#711-rices-theorem|§7.11]], [[1-models-of-computation/07-undecidability#712-the-ricemcnaughtonmyhillshapiro-theorem|§7.12]] · concepts: [[concepts/undecidability-reductions]], [[concepts/rices-theorem]], [[concepts/acceptable-and-decidable]]*

> [!question] Problem
> Let $\textsf{AtLeastTwo} := \{\langle M\rangle \mid M \text{ accepts at least two different strings}\}$, that is, the encodings of Turing machines $M$ with $\lvert\textsf{Accept}(M)\rvert\ge2$.
>
> (a) Prove that $\textsf{AtLeastTwo}$ is undecidable by a reduction from $\textsf{Accept} = \{\langle M, w\rangle \mid M \text{ accepts } w\}$.
>
> (b) Prove it again with Rice's theorem.
>
> (c) Show that $\textsf{Quick374} := \{\langle M\rangle \mid M \text{ halts on input } \varepsilon \text{ within 374 steps}\}$ is decidable, and explain why Rice's theorem does not apply to it.
>
> (d) Is $\textsf{AtLeastTwo}$ acceptable? Is its complement?

Machines have input alphabet $\Sigma = \{\mathtt{0},\mathtt{1}\}$, and "halts" means "reaches $\textit{accept}$ or $\textit{reject}$".

## (a) A reduction from Accept

**Idea.** Given $\langle M, w\rangle$, build a machine $M'$ whose language is huge — all of $\Sigma^*$, so certainly two strings — if $M$ accepts $w$, and empty otherwise. $M'$ ignores its own input: the only thing that decides what it does is whether $M$ accepts $w$. This is the standard shape of a [[concepts/undecidability-reductions|reduction]] ([[1-models-of-computation/07-undecidability#79-the-halting-problem-via-reduction|§7.9]]).

> [!example] Proof of (a) — model answer
> Suppose for the sake of argument that some Turing machine $\textsf{DecideAtLeastTwo}$ decides $\textsf{AtLeastTwo}$.
>
> Consider the following machine $\textsf{DecideAccept}$. Given $\langle M, w\rangle$, it writes the encoding $\langle M'\rangle$ of the machine
> $$
> M'(x)\colon\ \text{erase } x;\ \text{write } w;\ \text{run } M \text{ on } w;\ \text{if } M \text{ accepts, accept; if } M \text{ rejects, reject},
> $$
> then runs $\textsf{DecideAtLeastTwo}$ on $\langle M'\rangle$ and returns its answer.
>
> $\Rightarrow$ Suppose $M$ accepts $w$. Whatever the input $x$ is, $M'$ erases it and then does exactly what $M$ does on $w$, so $M'$ accepts every input: $\textsf{Accept}(M') = \Sigma^*$, which contains the two different strings `0` and `1`. So $\langle M'\rangle\in\textsf{AtLeastTwo}$, $\textsf{DecideAtLeastTwo}$ accepts $\langle M'\rangle$, and $\textsf{DecideAccept}$ accepts $\langle M, w\rangle$.
>
> $\Leftarrow$ Suppose $M$ does not accept $w$: it rejects $w$ or diverges on $w$. In the first case $M'$ rejects every input; in the second, $M'$ diverges on every input. Either way $\textsf{Accept}(M') = \varnothing$, which has fewer than two strings. So $\langle M'\rangle\notin\textsf{AtLeastTwo}$, $\textsf{DecideAtLeastTwo}$ rejects $\langle M'\rangle$, and $\textsf{DecideAccept}$ rejects $\langle M, w\rangle$.
>
> In both cases $\textsf{DecideAccept}$ answers correctly, and it always halts: writing $\langle M'\rangle$ is a finite edit of $\langle M\rangle$ and $w$, and $\textsf{DecideAtLeastTwo}$ always halts. So $\textsf{DecideAccept}$ decides $\textsf{Accept}$, which is impossible, because $\textsf{Accept}$ is undecidable. Therefore $\textsf{DecideAtLeastTwo}$ does not exist: $\textsf{AtLeastTwo}$ is undecidable. $\blacksquare$

Four machines, four names: the hypothetical decider $\textsf{DecideAtLeastTwo}$; the decider we build from it, $\textsf{DecideAccept}$; its input machine $M$; and $M'$, whose encoding $\textsf{DecideAccept}$ writes down but never runs.

> [!trap] Where reductions go wrong
> - **An $M'$ that does not land in the property.** "$M'(x)$: run $M$ on $x$" gives $\textsf{Accept}(M') = \textsf{Accept}(M)$, which has nothing to do with $w$. "$M'(x)$: if $x = \varepsilon$, run $M$ on $w$; otherwise reject" gives $\textsf{Accept}(M')\subseteq\{\varepsilon\}$ — never two strings — so the $\Rightarrow$ direction fails. In the yes-case the language must have the property; $\Sigma^*$ has two strings to spare.
> - **Running $M'$ (or $M$).** $\textsf{DecideAccept}$ only *writes* $\langle M'\rangle$. If it ran $M$ on $w$ itself, it could run forever, and a decider must halt.
> - **Forgetting divergence.** "Does not accept" includes running forever. Then $M'$ runs forever on every input, so $\textsf{Accept}(M') = \varnothing$ — do not write "$M'$ rejects".
> - **The wrong direction.** Deciding $\textsf{AtLeastTwo}$ with the help of a decider for $\textsf{Accept}$ proves nothing.

## (b) The same result by Rice's theorem

> [!example] Proof of (b) — model answer
> Let $\mathcal{L} := \{L\subseteq\Sigma^* \mid \lvert L\rvert\ge2\}$, the set of languages with at least two strings. Then $\textsf{AtLeastTwo} = \textsf{AcceptIn}(\mathcal{L}) = \{\langle M\rangle \mid \textsf{Accept}(M)\in\mathcal{L}\}$: whether $\langle M\rangle$ belongs depends only on the language $\textsf{Accept}(M)$.
> - $Y := M_{\textsf{Accept}}$, with $\delta(\textit{start}, a) = (\textit{accept}, a, +1)$ for every $a\in\Gamma$. It accepts every input, so $\textsf{Accept}(Y) = \Sigma^*\in\mathcal{L}$.
> - $N := M_{\textsf{Reject}}$, with $\delta(\textit{start}, a) = (\textit{reject}, a, +1)$ for every $a\in\Gamma$. It accepts nothing, so $\textsf{Accept}(N) = \varnothing\notin\mathcal{L}$.
>
> By [[concepts/rices-theorem|Rice's theorem]], $\textsf{AcceptIn}(\mathcal{L}) = \textsf{AtLeastTwo}$ is undecidable. $\blacksquare$

The property speaks about the strings $M$ **accepts**, so the $\textsf{AcceptIn}$ form of the theorem is the right one. For "$M$ *rejects* at least two strings" you would use the rejection version, $\textsf{RejectIn}(\mathcal{L})$, and describe the witnesses by their $\textsf{Reject}$ languages: then $M_{\textsf{Reject}}$ ($\textsf{Reject} = \Sigma^*$) is the $Y$ and $M_{\textsf{Accept}}$ ($\textsf{Reject} = \varnothing$) the $N$. Part (a) is the proof of Rice's theorem specialized to this property, with $Y = M_{\textsf{Accept}}$ — except that it reduces from $\textsf{Accept}$, where the book's proof uses $\textsf{Halt}$.

> [!trap] Rice traps
> - **Vague witnesses.** "A machine that accepts two strings" is not a witness; give the machine (its transitions, or an unmistakable description) *and* its language.
> - **Swapped witnesses.** $Y$'s language must have the property ($\ge2$ strings) and $N$'s must not. Both are judged by $\textsf{Accept}(\cdot)$ alone — not by how fast or whether the machines halt.
> - **Applying Rice to behavior** — the next part.

## (c) A look-alike that is decidable

> [!example] Proof of (c)
> **A decider.** Given $\langle M\rangle$, simulate $M$ on the empty input for at most 374 steps, using the universal machine with a step counter. If $M$ accepts or rejects within those steps, accept; if it is still running after 374 steps, reject. Only 374 steps of $M$ are ever simulated, so this machine halts on every input, and it accepts exactly the encodings in $\textsf{Quick374}$. (A crash within the 374 steps is detected the same way; count it as halting or not, as your definition of "halts" says.)
>
> **Why Rice's theorem does not apply.** $\textsf{Quick374}$ is not $\textsf{AcceptIn}(\mathcal{L})$ for any set of languages $\mathcal{L}$, because membership does not depend on the language alone. $M_{\textsf{Accept}}$ halts on $\varepsilon$ after one step, so $\langle M_{\textsf{Accept}}\rangle\in\textsf{Quick374}$. The machine $M_{\textsf{slow}}$ that walks right for 400 steps and then accepts has the same language, $\Sigma^*$, but halts on $\varepsilon$ only after 400 steps, so $\langle M_{\textsf{slow}}\rangle\notin\textsf{Quick374}$. Two machines with the same language, one in and one out: this is a property of machines, not of languages.

Rice's theorem is silent about such behavioral properties: some are decidable, like this one and the book's $\textsf{ThisIsSparta}$, and some are not ([[1-models-of-computation/07-undecidability#713-turing-machine-behavior-its-complicated|§7.13]]). What makes this one decidable is the step bound: the question is about a finite piece of one computation.

**An even closer look-alike.** "$M$ accepts at least two different strings, each within 374 steps" is decidable too. In 374 steps the head reads only cells $0,\dots,373$, so whether $M$ accepts $x$ within 374 steps depends only on the first 374 symbols of $x$. Simulate $M$ for 374 steps on every string of length at most 374. If some string of length exactly 374 is accepted within those steps, so are all of its infinitely many extensions: answer yes. Otherwise no longer string is accepted within 374 steps either, and you just count. That is $2^{375}-1$ simulations — absurd, but finite, and decidability asks for nothing more. The step bound, not the "two strings", is what changes the answer.

## (d) Acceptable, but its complement is not

> [!key] Answer (d)
> $\textsf{AtLeastTwo}$ is **acceptable**: dovetail — for $t = 1, 2, 3, \dots$, run $M$ for $t$ steps on each of the first $t$ strings in shortlex order, and accept as soon as two different strings have been accepted. Its **complement is not acceptable**: $\textsf{AtLeastTwo}$ is acceptable but undecidable, so by [[1-models-of-computation/07-undecidability#73-useful-properties|Lemma 5]] its complement cannot be acceptable as well.

**Why dovetail?** Running $M$ on $\varepsilon$, `0`, `1`, `00`, … one after the other fails when $M$ runs forever on one of them: a machine that diverges on $\varepsilon$ but accepts every other string is in $\textsf{AtLeastTwo}$, yet the one-at-a-time search never gets past $\varepsilon$. Dovetailing gives every string an ever-growing time budget, so if $M$ accepts $x\ne y$, some round runs both long enough. (The same idea simulates nondeterminism in [[1-models-of-computation/09-nondeterministic-turing-machines#94-deterministic-simulation-via-dovetailing|§9.4]].) If $M$ accepts at most one string, the acceptor runs forever — allowed for an acceptor.

**The same answer from §7.12.** "At least two strings" is monotone (a superset still has two strings), compact (any two of the strings form a finite subset with the property) and finitely acceptable (count the strings in a finite list), as the Rice–McNaughton–Myhill–Shapiro theorem requires of an acceptable $\textsf{AcceptIn}(\mathcal{L})$. The complementary property "at most one string" is not monotone — $\varnothing$ has it, $\Sigma^*\supseteq\varnothing$ does not — so Lemma 17 gives unacceptability again. (The complement also contains every string that encodes no machine; those form a decidable set and change nothing.)

> [!exam] How these proofs are graded
> Chapter 7 is tested on the final exam only. A **reduction** is graded out of 10: **4** for the reduction itself — a correct description of the new decider and of $M'$, in the right direction — **3** for the yes-direction and **3** for the no-direction, which must cover both rejecting and diverging. A proof by **Rice's theorem**: **4** for a machine whose language has the property, **4** for one whose language does not, and **2** for the details, including stating the property as a set of languages and using the right variant of the theorem. Rubric details: [[0-toolkit/06-how-exams-are-graded|how exams are graded]].

### Sources for this page
The language is a classic textbook-style exercise (compare Corollary 15(c), "accepts exactly three strings"), worked in our own words with the templates of Erickson, *Models of Computation*, §§7.9–7.12; the contrast in (c) follows the book's $\textsf{ThisIsSparta}$ example, and dovetailing is the technique of §9.4. The bounded look-alike and the dovetailing acceptor are ours. Checked by `tools/checks/problems_2.py`: the witnesses $Y$ and $N$; the machine $M'$, built as an actual Turing machine from five toy machines and eight strings $w$ (on every input $x$ of length at most 5 it accepts, rejects or runs on exactly as $M$ does on $w$); the $\textsf{Quick374}$ decider on machines that halt after 1, 374, 375 or 400 steps or never; the fact behind the bounded look-alike, on 400 random small machines; and the dovetailing acceptor on five machines.
