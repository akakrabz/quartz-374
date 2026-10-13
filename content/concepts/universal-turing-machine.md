---
title: "Universal Turing machine"
description: "One fixed Turing machine U that runs any machine given to it as data: U accepts ⟨M, w⟩ iff M accepts w and rejects it iff M rejects w. The encoding, one simulated step, and how U proves languages acceptable — but never decidable."
tags: [concept, turing-machines]
aliases: ["universal machine", "UTM", "Turing machine interpreter"]
---

> [!definition] Definition — universal Turing machine
> A **universal Turing machine** $U$ takes the encoding $\langle M,w\rangle$ of a Turing machine $M$ and a string $w$, and simulates $M$ on $w$:
> $$
> U \text{ accepts } \langle M,w\rangle \iff M \text{ accepts } w, \qquad U \text{ rejects } \langle M,w\rangle \iff M \text{ rejects } w.
> $$
> If $M$ runs forever on $w$, so does $U$. $U$ is **one fixed machine**, with a fixed alphabet and a fixed number of states; $M$ is just data on its tape.

**How it works.** Everything about $M$ is written in binary: each symbol of $\Gamma$ as $\lceil\lg\lvert\Gamma\rvert\rceil$ bits and each state as $\lceil\lg\lvert Q\rvert\rceil$ bits, with $\textit{start}$ all 1s and $\textit{reject}$ all 0s ($U$ must also recognize $\textit{accept}$; the book leaves its code open, and this site uses $\mathtt{0}\cdots\mathtt{01}$). A string is $[\langle a_1\rangle{\bullet}\langle a_2\rangle{\bullet}\cdots]$. The machine is $\langle M\rangle = [\langle\textit{reject}\rangle{\bullet}\langle\square\rangle]$ followed by a bracketed list of blocks $[\langle p\rangle{\bullet}\langle a\rangle\,|\,\langle q\rangle{\bullet}\langle b\rangle{\bullet}\langle\Delta\rangle]$, one for each transition $\delta(p,a) = (q,b,\Delta)$ with $q\ne\textit{reject}$, where $\langle -1\rangle = \mathtt{0}$ and $\langle +1\rangle = \mathtt{1}$. $U$ keeps $M$'s tape as a list of cells $[\langle q\rangle{\bullet}\langle a\rangle]$, with $q = \textit{reject}$ everywhere except in the cell under the head. One simulated step: find that cell; look up the block whose left half matches it (none: **reject**); copy in the new state and symbol (new state $\textit{accept}$: **accept**); move the state code one cell left or right, appending an encoded blank at the right end when needed.

> [!recipe] Using $U$ in proofs
> - **"Run $M$ on $w$"** in pseudocode means "run $U$ on $\langle M,w\rangle$". This shows that $\textsf{Accept}$ is acceptable; for $\textsf{Halt}$, accept whenever the simulation halts; for $\textsf{SelfAccept}$, run $U$ on $\langle M,\langle M\rangle\rangle$ (Theorem 10).
> - **"Run $M$ on $w$ for $k$ steps"** — $U$ with a step counter — always halts, so a *decider* may use it.
> - **Run simulations in parallel**, one step each in turn, whenever one of them might run forever.

> [!trap]
> - $U$ **accepts** $\textsf{Accept}$ but does **not decide** it: on $\langle M,w\rangle$ with $M$ looping, $U$ loops. No machine decides $\textsf{Accept}$ ([[concepts/halting-problem]]).
> - A decider may call $U$ only with a step limit, or on machines known to halt.
> - $U$ does not grow with $M$; that is why states and symbols are encoded in binary.
> - $\langle M\rangle$ is a string, $M$ a machine: writing $\langle M'\rangle$ down is finite work even if $M'$ would run forever.

**Example.** Let $\Gamma = \{\square,\mathtt{0},\mathtt{1}\}$, $Q = \{\textit{start},\textit{accept},\textit{reject}\}$, and give $M$ a single transition $\delta(\textit{start},\mathtt{1}) = (\textit{accept},\mathtt{1},+1)$; all others reject, so $M$ accepts the strings that begin with `1`. With the 2-bit codes $\langle\square\rangle = \mathtt{00}$, $\langle\mathtt{0}\rangle = \mathtt{01}$, $\langle\mathtt{1}\rangle = \mathtt{10}$ and $\langle\textit{start}\rangle = \mathtt{11}$, $\langle\textit{accept}\rangle = \mathtt{01}$, $\langle\textit{reject}\rangle = \mathtt{00}$:
- $\langle M\rangle$ is `[00•00][[11•10|01•10•1]]`, and the input `10` is `[10•01]`;
- $U$'s initial configuration is `[[11•10][00•01]]`. The head cell `[11•10]` matches the left half of the only block, whose new state `01` is $\textit{accept}$, so $U$ accepts after one simulated step;
- on input `01` the configuration is `[[11•01][00•10]]`; no block begins `11•01`, so $U$ rejects.

**Where it appears.** [[1-models-of-computation/06-turing-machines#68-universal-turing-machines|§6.8]] (the encoding and the simulation), [[1-models-of-computation/07-undecidability#74-code-is-data-data-is-code|§7.4]] (encodings are unique, modifiable, executable), [[1-models-of-computation/07-undecidability#78-nevertheless-acceptable|§7.8]] (Theorems 10–11), [[1-models-of-computation/07-undecidability#79-the-halting-problem-via-reduction|§7.9]] ($\textsf{Accept}$, $\textsf{Reject}$ and $\textsf{Halt}$ are acceptable), [[1-models-of-computation/08-universal-models#81-universal-turing-machines|§8.1]] (and the much smaller universal systems of Chapter 8).

Related: [[concepts/turing-machines]] · [[concepts/church-turing-thesis]] · [[concepts/acceptable-and-decidable]] · [[concepts/halting-problem]] · [[concepts/diagonalization]]
