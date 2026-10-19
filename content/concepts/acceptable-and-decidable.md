---
title: "Acceptable and decidable languages"
description: "A machine accepts L if it accepts exactly the strings in L, and decides L if it also halts on every input. Lemma 5 (decidable = acceptable and co-acceptable), how to classify a language, and a table of the standard languages."
tags: [concept, turing-machines, undecidability]
aliases: ["acceptable language", "decidable language", "recognizable language", "semi-decidable", "recursively enumerable", "co-acceptable"]
---

> [!definition] Definition — acceptable, decidable
> Every input lands in exactly one of $\textsf{Accept}(M)$, $\textsf{Reject}(M)$ and $\textsf{Diverge}(M)$ (crashing counts as diverging), and $\textsf{Halt}(M) := \textsf{Accept}(M)\cup\textsf{Reject}(M)$.
> - $L$ is **acceptable** (recognizable, semi-decidable, recursively enumerable) if $L = \textsf{Accept}(M)$ for some Turing machine $M$.
> - $L$ is **decidable** (computable, recursive) if $L = \textsf{Accept}(M)$ and $\textsf{Diverge}(M) = \varnothing$ for some $M$: a machine that halts on every input, accepting the strings in $L$ and rejecting the rest.

> [!key] Lemma 5
> An acceptable language $L$ is decidable if and only if its complement $\overline{L} = \Sigma^*\setminus L$ is acceptable. So if $L$ is acceptable but undecidable, then $\overline{L}$ is **not** acceptable.

**Why it works.** A decider with its answers swapped decides $\overline{L}$. Conversely, run an acceptor for $L$ and one for $\overline{L}$ **in parallel**, one step each in turn: every string is accepted by exactly one of them, so the combination always halts with the right answer. Hence decidable = acceptable and co-acceptable, and the classes are strictly nested: decidable $\subsetneq$ acceptable $\subsetneq$ all languages.

> [!recipe] Recipe — classifying a language
> - **Acceptable:** describe a machine that accepts exactly $L$ — simulation with $U$, dovetailing, or nondeterministic guessing. Running forever on strings outside $L$ is allowed.
> - **Decidable:** a machine that halts on every input; or show that $L$ and $\overline{L}$ are both acceptable; or combine decidable languages with $\cup$, $\cap$, $\setminus$ (Lemma 2).
> - **Undecidable:** [[concepts/diagonalization]], a [[concepts/undecidability-reductions|reduction]], or [[concepts/rices-theorem|Rice's theorem]].
> - **Not acceptable:** $\overline{L}$ is acceptable and $L$ is undecidable (Lemma 5); a diagonal argument (Theorem 9); or Lemma 17 for properties that are not monotone (§7.12).

**Example — the standard languages.** Complements are taken among valid encodings; the strings that encode nothing form a decidable set and change none of the answers.

| language | acceptable? | decidable? | reason |
|---|---|---|---|
| $\textsf{Accept} = \{\langle M,w\rangle \mid M \text{ accepts } w\}$ | yes | no | run $U$; a decider would decide $\textsf{SelfAccept}$ |
| $\textsf{Halt} = \{\langle M,w\rangle \mid M \text{ halts on } w\}$ | yes | no | run $U$, accept if it halts; Theorem 12 |
| $\overline{\textsf{Accept}}$; $\textsf{Diverge} = \overline{\textsf{Halt}}$ | no | no | Lemma 5 |
| $\textsf{SelfAccept}$; $\textsf{SelfReject}$ | yes | no | acceptable: Theorems 10, 11; undecidable: Theorems 7, 6 |
| $\textsf{SelfHalt}$ | yes | no | union of those two (Lemma 4); Theorem 8 |
| $\overline{\textsf{SelfAccept}}$; $\overline{\textsf{SelfReject}}$ | no | no | Lemma 5 |
| $\textsf{SelfDiverge} = \overline{\textsf{SelfHalt}}$ | no | no | Theorem 9 (diagonalization) |
| $\textsf{NeverAccept} = \{\langle M\rangle \mid \textsf{Accept}(M) = \varnothing\}$ | no | no | Theorem 13; Lemma 5, since its complement is acceptable |
| $\overline{\textsf{NeverAccept}}$ | yes | no | [[1-models-of-computation/09-nondeterministic-turing-machines#94-deterministic-simulation-via-dovetailing\|dovetail]] $M$ over all inputs |
| $\textsf{ThisIsSparta}$: $M$ accepts $\mathtt{SPARTA}$ after exactly 300 steps | yes | yes | simulate 300 steps |

> [!trap]
> - **Undecidable is not unacceptable:** $\textsf{Halt}$ is acceptable.
> - Acceptable languages are **not** closed under complement ($\textsf{Halt}$ versus $\textsf{Diverge}$). They are closed under $\cup$ and $\cap$ (Lemma 4), but the union needs a parallel simulation, because the first acceptor may run forever.
> - "Decidable" is about **existence**: the language built from the binary digits of $\pi$ in §7.2 is decidable though nobody knows its decider.

**Where it appears.** [[1-models-of-computation/06-turing-machines#62-formal-definitions|§6.2]] (accepting versus deciding), [[1-models-of-computation/07-undecidability#71-acceptable-versus-decidable|§7.1]] (the four languages of a machine), [[1-models-of-computation/07-undecidability#72-decidable-without-knowing-the-algorithm|§7.2]] (the $\pi$ example), [[1-models-of-computation/07-undecidability#73-useful-properties|§7.3]] (Lemmas 1–5), [[1-models-of-computation/07-undecidability#78-nevertheless-acceptable|§7.8]] (Theorems 10–11), [[1-models-of-computation/07-undecidability#712-the-ricemcnaughtonmyhillshapiro-theorem|§7.12]] (which properties give acceptable languages), [[0-toolkit/03-the-big-picture|the big picture]].

**Practice.** [[practice/topics#acceptable-and-decidable-languages|Acceptable and decidable languages]] (4 problems) — for example [[practice/07-undecidability#71-closure-facts-true-or-false|7.1 Closure facts, true or false]] (easy), [[practice/07-undecidability#76-do-two-machines-share-a-string|7.6 Do two machines share a string]] (medium), [[practice/07-undecidability#77-accepts-epsilon-rejects-itself|7.7 Accepts epsilon, rejects itself]] (hard).

Related: [[concepts/turing-machines]] · [[concepts/halting-problem]] · [[concepts/diagonalization]] · [[concepts/undecidability-reductions]] · [[concepts/rices-theorem]] · [[concepts/counting-arguments]]
