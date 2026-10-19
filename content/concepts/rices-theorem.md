---
title: "Rice's theorem"
description: "Every non-trivial property of the language a Turing machine accepts is undecidable: the statement and its variants, the three-step recipe with witness machines Y and N, and the cases where the theorem does not apply."
tags: [concept, undecidability]
aliases: ["Rice theorem", "AcceptIn", "non-trivial property of languages"]
---

> [!key] Rice's theorem
> Let $\mathcal{L}$ be a set of languages (a *property* of languages). If $\textsf{Accept}(Y)\in\mathcal{L}$ for some Turing machine $Y$ and $\textsf{Accept}(N)\notin\mathcal{L}$ for some Turing machine $N$, then
> $$
> \textsf{AcceptIn}(\mathcal{L}) := \{\langle M\rangle \mid \textsf{Accept}(M)\in\mathcal{L}\}
> $$
> is undecidable.
>
> **Variants** with the same proof: $\textsf{Reject}$, $\textsf{Halt}$ or $\textsf{Diverge}$ in place of $\textsf{Accept}$ throughout (Rice's rejection, halting and divergence theorems), and $\textsf{DecideIn}(\mathcal{L}) := \{\langle M\rangle \mid M \text{ decides a language in } \mathcal{L}\}$, with deciders $Y$ and $N$ (Rice's decision theorem).

**Why it works.** One reduction from $\textsf{Halt}$ handles every property at once. If $\varnothing\notin\mathcal{L}$, map $\langle M,w\rangle$ to the machine $\textsf{WTF}(x)$: "run $M$ on $w$ and ignore the result; then run $Y$ on $x$." If $M$ halts on $w$, then $\textsf{Accept}(\textsf{WTF}) = \textsf{Accept}(Y)\in\mathcal{L}$; otherwise $\textsf{Accept}(\textsf{WTF}) = \varnothing\notin\mathcal{L}$. So a decider for $\textsf{AcceptIn}(\mathcal{L})$ would decide $\textsf{Halt}$. If $\varnothing\in\mathcal{L}$, apply the same argument to the complementary property, with $N$ in the role of $Y$.

> [!recipe] Recipe — three steps (graded 4 + 4 + 2)
> 1. **Name the property.** Write the language as $\textsf{AcceptIn}(\mathcal{L})$ for an explicit set of languages $\mathcal{L}$, and check that membership of $\langle M\rangle$ depends **only on $\textsf{Accept}(M)$**: two machines with the same language are both in or both out. If it depends on $\textsf{Halt}(M)$ instead, use that variant.
> 2. **Give a machine $Y$** whose language is in $\mathcal{L}$, concretely (4 points).
> 3. **Give a machine $N$** whose language is not in $\mathcal{L}$ (4 points).
>
> Conclude "by Rice's theorem, $\textsf{AcceptIn}(\mathcal{L})$ is undecidable", naming the variant (2 points for these details). Handy witnesses: $M_{\textsf{Accept}}$ accepts every input ($\textsf{Accept} = \Sigma^*$); $M_{\textsf{Reject}}$ rejects every input ($\textsf{Accept} = \varnothing$, $\textsf{Halt} = \Sigma^*$); $M_{\textsf{Diverge}}$ moves right forever ($\textsf{Accept} = \textsf{Halt} = \varnothing$).

> [!trap] When Rice's theorem does not apply
> - **Behavior, not language.** "$M$ accepts $\mathtt{SPARTA}$ after exactly 300 steps" ($\textsf{ThisIsSparta}$) is decidable by simulation, and so is "$M$ never moves left on $w$" (Theorem 19); "$M$ moves left three times in a row on $w$" is undecidable (Theorem 20) — by a reduction.
> - **Self-reference.** $\textsf{RevAccept} := \{\langle M\rangle \mid M \text{ accepts } \langle M\rangle^R\}$ depends on $M$'s own encoding: undecidable, but by a [[concepts/undecidability-reductions|reduction]].
> - **Trivial properties** have no $Y$ or no $N$: $\{\langle M\rangle \mid \textsf{Accept}(M) \text{ is acceptable}\}$ is the set of all encodings — decidable.
> - **Wrong variant.** "$M$ halts on every input" is not a property of $\textsf{Accept}(M)$: $M_{\textsf{Reject}}$ and $M_{\textsf{Diverge}}$ accept the same language $\varnothing$, but only $M_{\textsf{Reject}}$ halts everywhere. Use Rice's halting theorem with $\mathcal{L} = \{\Sigma^*\}$, $Y = M_{\textsf{Accept}}$ and $N = M_{\textsf{Diverge}}$.
> - **Undecidable only.** Rice never proves "not acceptable" — $\textsf{AcceptIn}$ of "non-empty" is acceptable. For that, see Lemma 17.

**Example.** $\{\langle M\rangle \mid \textsf{Accept}(M) \text{ is infinite}\}$: the property is $\mathcal{L} = \{L \mid L \text{ is infinite}\}$; take $Y = M_{\textsf{Accept}}$, since $\Sigma^*$ is infinite, and $N = M_{\textsf{Reject}}$, since $\varnothing$ is finite. By Rice's theorem the language is undecidable. (By Corollary 18 neither it nor $\{\langle M\rangle \mid \textsf{Accept}(M) \text{ is finite}\}$ is even acceptable; a direct reduction for the finite case is on [[concepts/undecidability-reductions]].)

**Where it appears.** [[1-models-of-computation/07-undecidability#711-rices-theorem|§7.11]] (statement, proof, Corollary 15, the variants, $\textsf{ThisIsSparta}$ and $\textsf{RevAccept}$), [[1-models-of-computation/07-undecidability#712-the-ricemcnaughtonmyhillshapiro-theorem|§7.12]] (when $\textsf{AcceptIn}(\mathcal{L})$ is acceptable: Lemma 17, Corollary 18), [[1-models-of-computation/07-undecidability#713-turing-machine-behavior-its-complicated|§7.13]] (questions about behavior), [[0-toolkit/06-how-exams-are-graded|how exams are graded]].

**Practice.** [[practice/topics#rices-theorem-and-machine-behavior|Rice's theorem and machine behavior]] (4 problems) — for example [[practice/07-undecidability#72-decidable-acceptable-or-neither|7.2 Decidable, acceptable, or neither]] (easy), [[practice/07-undecidability#74-rice-with-the-right-variant|7.4 Rice with the right variant]] (medium), [[practice/07-undecidability#78-both-languages-infinite|7.8 Both languages infinite]] (hard).

Related: [[concepts/undecidability-reductions]] · [[concepts/halting-problem]] · [[concepts/acceptable-and-decidable]] · [[concepts/diagonalization]] · [[concepts/turing-machines]]
