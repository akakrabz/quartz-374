---
title: "Diagonalization"
description: "Self-reference as a proof technique: Cantor's theorem, and the argument that runs a machine built from a hypothetical decider on its own encoding — the template, the traps, and an example where the input is doubled."
tags: [concept, undecidability]
aliases: ["diagonal argument", "diagonal language", "self-reference argument"]
---

> [!key] The diagonal argument
> **Cantor's theorem:** no function $f\colon X\to 2^X$ is onto, because the set $Y = \{x\in X \mid x\notin f(x)\}$ differs from every $f(y)$ — at $y$ itself: $y\in Y \iff y\notin f(y)$.
>
> **For Turing machines,** take $X = \Sigma^*$ and $f(\langle M\rangle) = \textsf{Accept}(M)$ (and $f(w) = \varnothing$ for strings that encode no machine): then $Y$ is a language that no Turing machine accepts. The same twist — run a machine on its own encoding and make it contradict itself — proves $\textsf{SelfReject}$, $\textsf{SelfAccept}$ and $\textsf{SelfHalt}$ undecidable (Theorems 6–8) and $\textsf{SelfDiverge}$ unacceptable (Theorem 9).

**Why "diagonal".** Write the machines $M_1, M_2, \ldots$ as the rows of a table and their encodings $\langle M_1\rangle, \langle M_2\rangle, \ldots$ as the columns; entry $(i,j)$ says what $M_i$ does on $\langle M_j\rangle$. A language defined by **flipping the diagonal** — $\langle M_i\rangle$ belongs to it exactly when $M_i$ does *not* accept $\langle M_i\rangle$ — disagrees with row $i$ in column $i$, so it is no machine's language. Theorem 6 runs the same argument against a hypothetical decider $\textsf{SR}$ for $\textsf{SelfReject}$: on its own encoding, $\textsf{SR}$ would accept if and only if it rejects.

> [!template] Template — undecidability by diagonalization (graded 4 + 3 + 3)
> Suppose for the sake of argument that some Turing machine $\textsf{Dec}$ decides $L$. \
> Build a new machine $\textsf{Wrap}$ from $\textsf{Dec}$: *[swap its accept and reject states / redirect its accepting transitions to a looping state / …]*. \
> Then for every Turing machine $M$: $\textsf{Wrap}$ *[accepts, or halts on]* $\langle M\rangle$ if and only if $M$ *[does not …]* $\langle M\rangle$. \
> In particular, take $M = \textsf{Wrap}$. \
> If $\textsf{Wrap}$ *[accepts]* $\langle\textsf{Wrap}\rangle$, then by the line above $\textsf{Wrap}$ does not *[accept]* $\langle\textsf{Wrap}\rangle$ — a contradiction. \
> If $\textsf{Wrap}$ does not *[accept]* $\langle\textsf{Wrap}\rangle$, then by the line above $\textsf{Wrap}$ *[accepts]* $\langle\textsf{Wrap}\rangle$ — a contradiction. \
> So $\textsf{Dec}$ does not exist, and $L$ is undecidable. $\blacksquare$
>
> 4 points for the wrapper machine and its behavior on $\langle M\rangle$, 3 for each of the two cases.

> [!trap]
> - Run the machine **built from the decider** on **its own** encoding; plugging in any other machine proves nothing.
> - Say why there are only two cases: $\textsf{Wrap}$ halts because $\textsf{Dec}$ does. With a mere acceptor there is a third case — running forever — and the contradiction must be "halts if and only if it diverges" (Theorem 9).
> - Check that the flip contradicts the definition of $L$. For $\textsf{SelfReject}$ no flip is needed — $\textsf{Dec}$ itself is the contradiction — and swapping its answers yields a consistent machine.
> - Diagonalization handles self-referential languages; for other languages, [[concepts/undecidability-reductions|reduce]] from one of them.

**Example — a doubled input.** $L := \{\langle M\rangle \mid M \text{ accepts } \langle M\rangle\langle M\rangle\}$ is undecidable. Suppose $\textsf{Dec}$ decides $L$. Let $\textsf{Wrap}$, on input $x$, reject unless $x = \langle M\rangle\langle M\rangle$ for some machine $M$; in that case run $\textsf{Dec}$ on $\langle M\rangle$ and do the opposite — accept if $\textsf{Dec}$ rejects, and reject if $\textsf{Dec}$ accepts. $\textsf{Wrap}$ halts on every input, and
$$
\langle\textsf{Wrap}\rangle\in L \iff \textsf{Wrap} \text{ accepts } \langle\textsf{Wrap}\rangle\langle\textsf{Wrap}\rangle \iff \textsf{Dec} \text{ rejects } \langle\textsf{Wrap}\rangle \iff \langle\textsf{Wrap}\rangle\notin L,
$$
a contradiction. The wrapper must contradict $\textsf{Dec}$ on the input that the definition of $L$ looks at — here $\langle\textsf{Wrap}\rangle\langle\textsf{Wrap}\rangle$, not $\langle\textsf{Wrap}\rangle$.

**Where it appears.** [[1-models-of-computation/07-undecidability#75-self-haters-gonna-self-hate|§7.5]] (Theorem 6 and the diagonal table), [[1-models-of-computation/07-undecidability#76-aside-uncountable-barbers|§7.6]] (Cantor's theorem and the barber), [[1-models-of-computation/07-undecidability#77-more-self-referential-languages|§7.7]] (Theorems 7–9 and the template), [[1-models-of-computation/02-regular-languages#28-not-every-language-is-regular|§2.8]] and [[concepts/counting-arguments]] (the counting version: uncountably many languages).

**Practice.** [[practice/topics#diagonalization|Diagonalization]] (1 problems) — for example [[practice/07-undecidability#77-accepts-epsilon-rejects-itself|7.7 Accepts epsilon, rejects itself]] (hard).

Related: [[concepts/halting-problem]] · [[concepts/undecidability-reductions]] · [[concepts/acceptable-and-decidable]] · [[concepts/counting-arguments]] · [[concepts/universal-turing-machine]]
