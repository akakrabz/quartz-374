---
title: "Turing machines"
description: "A finite-state control with an unbounded read/write tape: the formal definition, the four outcomes of a run (accept, reject, crash, run forever), accepting versus deciding, and how to write a machine down — with a small verified decider for 0ⁿ1ⁿ."
tags: [concept, turing-machines]
aliases: ["Turing machine", "TM", "deterministic Turing machine"]
---

> [!definition] Definition — Turing machine
> A Turing machine $M$ has a finite **tape alphabet** $\Gamma$ with a **blank** $\square\in\Gamma$, an **input alphabet** $\Sigma\subseteq\Gamma\setminus\{\square\}$, a finite set of **states** $Q$ containing three distinct states $\textit{start}$, $\textit{accept}$, $\textit{reject}$, and a **transition function**
> $$
> \delta\colon \big(Q\setminus\{\textit{accept},\textit{reject}\}\big)\times\Gamma\to Q\times\Gamma\times\{-1,+1\}.
> $$
> $\delta(p,a) = (q,b,\Delta)$ means: in state $p$ reading $a$, write $b$, move the head by $\Delta$, and enter state $q$. A **configuration** $(q,x,i)$ records the state, the tape contents and the head position; on input $w$ the machine starts in $(\textit{start},w,0)$. It **accepts** $w$ if it reaches $\textit{accept}$, **rejects** $w$ if it reaches $\textit{reject}$, **crashes** if it moves left from cell 0, and otherwise **runs forever**.
>
> $M$ **accepts** a language $L$ if it accepts exactly the strings in $L$, and **decides** $L$ if it also rejects every string not in $L$ — so it halts on every input.

**Where it comes from.** Turing (1936) wanted a definition of computation simple enough for one proof to reason about every machine, yet strong enough to run any algorithm — including other Turing machines ([[concepts/universal-turing-machine]]). It is a poor model of *speed* and the standard model of *possibility*: every reasonable variant — stay-put moves, more tapes, heads or tracks, a two-way infinite tape, nondeterminism — accepts and decides exactly the same languages.

> [!recipe] Recipe — writing a machine down
> 1. Describe the algorithm in English as a few **passes**: scan for something, mark or erase it, walk back.
> 2. Keep unbounded information **on the tape**, never in the state, and make sure the head cannot fall off cell 0 (mark the left end, or keep a blank sentinel there).
> 3. Turn each pass into one or two states with mnemonic names, give the table, and say that missing transitions reject.
> 4. Trace $\varepsilon$, a short member of the language, and a few near-misses.
>
> In undecidability proofs, describe machines in pseudocode instead ([[concepts/church-turing-thesis]]); write a table only when one is asked for.

> [!trap]
> - **"Rejects" is not "does not accept."** A machine that does not accept $w$ may reject it, crash, or run forever.
> - **Accepting $L$ is not deciding $L$.** A decider halts on every input; an acceptor may run forever on strings outside $L$ ([[concepts/acceptable-and-decidable]]).
> - A machine that matches symbols without checking their **order** accepts near-misses — for $\{\mathtt{0}^n\mathtt{1}^n\}$, strings such as `0110`.

**Example — a decider for $\{\mathtt{0}^n\mathtt{1}^n \mid n\ge0\}$.** Erase the first `0` and the last `1`, walk back, repeat; accept when nothing is left. $\mathit{skip0}$ and $\mathit{skip1}$ check the form $\mathtt{0}^*\mathtt{1}^*$ on every pass; — means reject.

| state | $\mathtt{0}$ | $\mathtt{1}$ | $\square$ |
|---|---|---|---|
| $\textit{start}$: erase a `0` | $(\mathit{skip0},\square,+1)$ | — | $(\textit{accept},\square,+1)$ |
| $\mathit{skip0}$: scan the 0s | $(\mathit{skip0},\mathtt{0},+1)$ | $(\mathit{skip1},\mathtt{1},+1)$ | $(\mathit{erase1},\square,-1)$ |
| $\mathit{skip1}$: scan the 1s | — | $(\mathit{skip1},\mathtt{1},+1)$ | $(\mathit{erase1},\square,-1)$ |
| $\mathit{erase1}$: erase the last `1` | — | $(\mathit{back},\square,-1)$ | — |
| $\mathit{back}$: return left | $(\mathit{back},\mathtt{0},-1)$ | $(\mathit{back},\mathtt{1},-1)$ | $(\textit{start},\square,+1)$ |

Because erasing starts at the left end, a blank always sits just left of the remaining block, so $\mathit{back}$ never falls off the tape. On `0011` the machine accepts after 15 steps; on `0101` it rejects when $\mathit{skip1}$ meets a `0`. On $\mathtt{0}^k\mathtt{1}^k$ it makes $k$ passes of at most $4k+1$ steps each, so it runs in $O(n^2)$ time on inputs of length $n$.

**Where it appears.** [[1-models-of-computation/06-turing-machines#62-formal-definitions|§6.2]] (definitions), [[1-models-of-computation/06-turing-machines#63-a-first-example|§6.3]] (a decider for $\{\mathtt{0}^n\mathtt{1}^n\mathtt{0}^n\}$), [[1-models-of-computation/06-turing-machines#64-variations|§6.4]] and [[1-models-of-computation/06-turing-machines#66-tracks-heads-and-tapes|§6.6]] (variants, all equivalent), [[1-models-of-computation/06-turing-machines#65-computing-functions|§6.5]] (computing functions), [[1-models-of-computation/07-undecidability#71-acceptable-versus-decidable|§7.1]] (the four languages), [[1-models-of-computation/09-nondeterministic-turing-machines#91-definitions|§9.1]] (nondeterminism).

**Practice.** [[practice/topics#turing-machines-design-variants-simulation|Turing machines: design, variants, simulation]] (6 problems) — for example [[practice/06-turing-machines#61-deciding-crashing-and-variants|6.1 Deciding, crashing and variants]] (easy), [[practice/06-turing-machines#64-palindromes-by-peeling-both-ends|6.4 Palindromes by peeling both ends]] (medium), [[practice/06-turing-machines#66-a-machine-that-doubles-its-input|6.6 A machine that doubles its input]] (hard).

Related: [[concepts/acceptable-and-decidable]] · [[concepts/church-turing-thesis]] · [[concepts/universal-turing-machine]] · [[concepts/nondeterministic-turing-machines]] · [[concepts/dfa]]
