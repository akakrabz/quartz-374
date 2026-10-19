---
title: "The halting problem"
description: "Halt = {⟨M, w⟩ | M halts on w} is acceptable but undecidable (Theorem 12): where it comes from, a one-machine proof, the classic confusions, and how it seeds other undecidability proofs."
tags: [concept, undecidability]
aliases: ["Halt", "halting problem"]
---

> [!key] Theorem 12 (the halting problem)
> $$
> \textsf{Halt} := \{\langle M, w\rangle \mid M \text{ halts on } w\}
> $$
> is **undecidable**. It is **acceptable** — run the [[concepts/universal-turing-machine|universal machine]] and accept as soon as the simulation halts — so its complement $\textsf{Diverge}$ is **not** acceptable (Lemma 5).

**Where it comes from.** Turing proved it in 1936, and it is why Hilbert's *Entscheidungsproblem* has no algorithmic solution. The book proves it in two steps. A diagonal argument shows that $\textsf{SelfHalt} := \{\langle M\rangle \mid M \text{ halts on } \langle M\rangle\}$ is undecidable (Theorem 8); then a decider $\textsf{H}$ for $\textsf{Halt}$ would decide $\textsf{SelfHalt}$ — on input $\langle M\rangle$, run $\textsf{H}$ on $\langle M,\langle M\rangle\rangle$. The same argument makes $\textsf{Accept}$, $\textsf{Reject}$ and $\textsf{Diverge}$ undecidable.

> [!recipe] Recipe — proving Theorem 12 from scratch, with one machine
> Suppose $\textsf{H}$ decides $\textsf{Halt}$. Build $\textsf{Wrap}$: on input $\langle M\rangle$, run $\textsf{H}$ on $\langle M,\langle M\rangle\rangle$; if $\textsf{H}$ accepts, loop forever; if $\textsf{H}$ rejects, accept. (On strings that encode no machine, reject.) Since $\textsf{H}$ always halts, $\textsf{Wrap}$ halts on $\langle M\rangle$ exactly when $\textsf{H}$ rejects $\langle M,\langle M\rangle\rangle$.
> - If $\textsf{Wrap}$ halts on $\langle\textsf{Wrap}\rangle$, then $\textsf{H}$ rejects $\langle\textsf{Wrap},\langle\textsf{Wrap}\rangle\rangle$, so $\textsf{Wrap}$ does not halt on $\langle\textsf{Wrap}\rangle$.
> - If $\textsf{Wrap}$ does not halt on $\langle\textsf{Wrap}\rangle$, then $\textsf{H}$ accepts $\langle\textsf{Wrap},\langle\textsf{Wrap}\rangle\rangle$, so $\textsf{Wrap}$ halts on $\langle\textsf{Wrap}\rangle$.
>
> Both cases are contradictions, so $\textsf{H}$ does not exist. $\blacksquare$

> [!trap]
> - **Undecidable is not unacceptable.** $\textsf{Halt}$ is acceptable; $\textsf{Diverge}$ is not.
> - **"Simulate $M$ on $w$ and see" is not a decider:** if $M$ runs forever, so does the simulation, and no computable time limit is correct for every $\langle M,w\rangle$ — such a limit would decide $\textsf{Halt}$.
> - **Mind the quantifier.** Halting on a given $w$, on the blank tape, and on every input are three different languages (all undecidable).
> - **Fixed versus given machine.** For one fixed $M$ the question may be easy — if $M$ always halts, $\textsf{Halt}(M) = \Sigma^*$. The theorem says that no single machine answers it for **every** $\langle M,w\rangle$.
> - In a reduction, decide $\textsf{Halt}$ *using* the decider for the new language — never the other way around.

**Example — halting on the blank tape.** $\textsf{HaltBlank} := \{\langle M\rangle \mid M \text{ halts on } \varepsilon\}$ is undecidable. Given $\langle M,w\rangle$, write $\langle M_w\rangle$, where $M_w$ erases its input, writes $w$, and runs $M$. Then $M_w$ halts on $\varepsilon$ — indeed on every input — if and only if $M$ halts on $w$. So a decider for $\textsf{HaltBlank}$, run on $\langle M_w\rangle$, would decide $\textsf{Halt}$, which is impossible. ([[concepts/rices-theorem|Rice's halting theorem]] gives the same result, with $Y = M_{\textsf{Accept}}$ and $N = M_{\textsf{Diverge}}$.)

**Where it appears.** [[1-models-of-computation/06-turing-machines|Chapter 6]] (Turing's 1936 paper), [[1-models-of-computation/07-undecidability#77-more-self-referential-languages|§7.7]] (Theorem 8: $\textsf{SelfHalt}$), [[1-models-of-computation/07-undecidability#79-the-halting-problem-via-reduction|§7.9]] (Theorem 12 and the direction of reductions), [[1-models-of-computation/07-undecidability#711-rices-theorem|§7.11]] (Rice's theorem is proved by a reduction from $\textsf{Halt}$), [[1-models-of-computation/08-universal-models#85-posts-correspondence-problem|§8.5]] (undecidable problems far from Turing machines).

**Practice.** [[practice/topics#undecidability-by-reduction|Undecidability by reduction]] (4 problems) — for example [[practice/07-undecidability#73-a-reduction-that-proves-nothing|7.3 A reduction that proves nothing]] (easy), [[practice/07-undecidability#75-two-behaviors-two-answers|7.5 Two behaviors, two answers]] (medium), [[practice/07-undecidability#78-both-languages-infinite|7.8 Both languages infinite]] (hard).

Related: [[concepts/diagonalization]] · [[concepts/undecidability-reductions]] · [[concepts/acceptable-and-decidable]] · [[concepts/universal-turing-machine]] · [[concepts/rices-theorem]]
