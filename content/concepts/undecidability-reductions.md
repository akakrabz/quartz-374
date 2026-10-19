---
title: "Undecidability by reduction"
description: "To prove L undecidable, assume a decider for L and use it as a subroutine to decide a language already known to be undecidable: the direction rule, the template, the traps, and an example that uses the input as a step budget."
tags: [concept, undecidability]
aliases: ["reduction proof", "undecidability by reduction", "reducing Halt to L"]
---

> [!key] The direction rule
> To prove that $L$ is undecidable, **reduce a known undecidable language to $L$**: assume that some machine $\textsf{DecideL}$ decides $L$, and use it as a black-box subroutine in a machine that decides $\textsf{Accept}$, $\textsf{Halt}$, or another language already known to be undecidable. That is impossible, so $\textsf{DecideL}$ does not exist.
>
> Reducing $L$ *to* $\textsf{Halt}$ — deciding $L$ with the help of a decider for $\textsf{Halt}$ — proves nothing: every decidable language reduces to $\textsf{Halt}$ too.

**Why it works.** A reduction from $X$ to $L$ proves "if $L$ is decidable, so is $X$"; read backwards, if $X$ is undecidable, so is $L$. Its heart is a translation: from $\langle M,w\rangle$, compute the encoding of a machine $M'$ with $\langle M'\rangle\in L$ exactly when $\langle M,w\rangle\in X$. Writing $\langle M'\rangle$ down always halts, even if $M'$ would run forever.

> [!template] Template — undecidability by reduction from $\textsf{Accept}$ (graded 4 + 3 + 3)
> Suppose for the sake of argument that some Turing machine $\textsf{DecideL}$ decides $L$. \
> Consider the following machine $\textsf{DecideAccept}$. Given $\langle M, w\rangle$, it writes the encoding $\langle M'\rangle$ of the machine \
> $\quad M'(x)$: *[for example: ignore $x$; run $M$ on $w$; then …]* \
> and then runs $\textsf{DecideL}$ on $\langle M'\rangle$ and returns its answer. \
> $\Rightarrow$ Suppose $M$ accepts $w$. Then $M'$ *[…]*, so $\langle M'\rangle\in L$. So $\textsf{DecideL}$ accepts $\langle M'\rangle$, and $\textsf{DecideAccept}$ accepts $\langle M, w\rangle$. \
> $\Leftarrow$ Suppose $M$ does not accept $w$ — it rejects or diverges. Then $M'$ *[…]*, so $\langle M'\rangle\notin L$. So $\textsf{DecideL}$ rejects $\langle M'\rangle$, and $\textsf{DecideAccept}$ rejects $\langle M, w\rangle$. \
> In both cases $\textsf{DecideAccept}$ is correct, and it always halts. So $\textsf{DecideAccept}$ decides $\textsf{Accept}$, which is impossible. \
> We conclude that $\textsf{DecideL}$ does not exist: $L$ is undecidable. $\blacksquare$
>
> 4 points for the reduction, 3 for each case. If $\langle M'\rangle\in L$ exactly when $M$ does **not** accept $w$, return the opposite of $\textsf{DecideL}$'s answer.

> [!trap]
> - **Direction.** The *new* language's decider is the subroutine; the known undecidable language is the one you end up deciding.
> - **Never run $M'$.** $\textsf{DecideAccept}$ only writes $\langle M'\rangle$ down; it must halt on every input, so it cannot run $M$ on $w$ itself.
> - **"Does not accept" means rejects *or* diverges**, and the second case must handle both.
> - **Say what $M'$ does with its own input $x$**, for every $x$: that is what determines $\textsf{Accept}(M')$.
> - **Name every machine** — $\textsf{DecideL}$, $\textsf{DecideAccept}$, $M$, $M'$ — and never write "it".

**Example — the input as a step budget.** $\textsf{FiniteAccept} := \{\langle M\rangle \mid \textsf{Accept}(M) \text{ is finite}\}$ is undecidable, by a reduction from $\textsf{Halt}$. Suppose $\textsf{DecideFinite}$ decides it. Given $\langle M,w\rangle$, the machine $\textsf{DecideHalt}$ writes the encoding of
$$
M'(x)\colon\ \text{simulate } M \text{ on } w \text{ for } \lvert x\rvert \text{ steps; accept if } M \text{ has halted, otherwise reject},
$$
runs $\textsf{DecideFinite}$ on $\langle M'\rangle$, and returns the **opposite** answer. If $M$ halts on $w$ after $s$ steps, then $M'$ accepts every $x$ with $\lvert x\rvert\ge s$ — infinitely many strings — so $\textsf{DecideFinite}$ rejects and $\textsf{DecideHalt}$ accepts. If $M$ never halts on $w$, then $\textsf{Accept}(M') = \varnothing$ is finite, so $\textsf{DecideFinite}$ accepts and $\textsf{DecideHalt}$ rejects. ([[concepts/rices-theorem|Rice's theorem]] also gives this result.)

**Where it appears.** [[1-models-of-computation/07-undecidability#79-the-halting-problem-via-reduction|§7.9]] (Theorem 12, the direction rule and the template), [[1-models-of-computation/07-undecidability#710-more-undecidable-languages|§7.10]] (Theorems 13–14: $\textsf{NeverAccept}$, $\textsf{DivergeSame}$), [[1-models-of-computation/07-undecidability#711-rices-theorem|§7.11]] (one reduction for every property; $\textsf{RevAccept}$), [[1-models-of-computation/07-undecidability#713-turing-machine-behavior-its-complicated|§7.13]] (Theorem 20), [[1-models-of-computation/08-universal-models#86-matrix-mortality|§8.6]] (matrix mortality), [[0-toolkit/02-proof-templates|proof templates]].

**Practice.** [[practice/topics#undecidability-by-reduction|Undecidability by reduction]] (4 problems) — for example [[practice/07-undecidability#73-a-reduction-that-proves-nothing|7.3 A reduction that proves nothing]] (easy), [[practice/07-undecidability#75-two-behaviors-two-answers|7.5 Two behaviors, two answers]] (medium), [[practice/07-undecidability#78-both-languages-infinite|7.8 Both languages infinite]] (hard).

Related: [[concepts/halting-problem]] · [[concepts/rices-theorem]] · [[concepts/diagonalization]] · [[concepts/acceptable-and-decidable]] · [[concepts/cook-levin-theorem]]
