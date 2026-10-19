---
title: "Nondeterministic Turing machines"
description: "Turing machines that may choose among several transitions: they accept if some branch accepts and reject only if every branch rejects. Same power as deterministic machines (breadth-first search, dovetailing), but the known simulation is exponentially slower."
tags: [concept, turing-machines, complexity]
aliases: ["NTM", "nondeterministic Turing machine", "computation tree"]
---

> [!definition] Definition — nondeterministic Turing machine
> Like a [[concepts/turing-machines|Turing machine]], except that each $\delta(p,a)\subseteq Q\times\Gamma\times\{-1,+1\}$ is a **set** of options: in state $p$ reading $a$, the machine may perform any one of them, and if $\delta(p,a) = \varnothing$ it rejects. Its possible runs on $w$ form the **computation tree**, rooted at $(\textit{start}, w, 0)$.
> - $N$ **accepts** $w$ if **some** branch reaches $\textit{accept}$ — other branches may reject or run forever.
> - $N$ **rejects** $w$ if **every** branch reaches $\textit{reject}$; then the whole tree is finite.
> - Otherwise $N$ neither accepts nor rejects $w$. $N$ **decides** $L$ if it accepts every string in $L$ and rejects every other string.

> [!key] Theorem 1 (§9.4)
> For every nondeterministic machine $N$ there is a deterministic machine $M$ that accepts exactly the strings $N$ accepts and rejects exactly the strings $N$ rejects. If every branch of $N$ on $w$ halts within $t$ steps, then $M$ halts within $O(t^2r^{2t})$ steps, where $r$ is the size of the largest set $\delta(p,a)$.

So nondeterministic machines accept exactly the acceptable languages and decide exactly the decidable ones.

**Why it works.** $M$ explores the computation tree **breadth-first**, keeping a queue of encoded configurations on its tape; every level of the tree is finite, so an accepting leaf at depth $d$ is found after finitely many steps. Depth-first search could follow one infinite branch forever. Equivalently (§9.5), the choices can be written in advance as an **advice string**, and **dovetailing** runs every advice string of length $t$ for $t$ steps, for $t = 1, 2, 3, \ldots$ — $O(t\,r^t)$ time with three tapes. Either way the simulation is exponential in $t$; whether polynomial-time nondeterminism can always be simulated in deterministic polynomial time is the $\textsf{P}$ versus $\textsf{NP}$ question.

> [!recipe] Recipe — guess, then verify
> 1. **Guess** a certificate one symbol per step — a divisor, an input string, a satisfying assignment — and write it on the tape.
> 2. **Verify** it deterministically; accept if the check succeeds.
> 3. **For a decider, bound the guess** (say, by the input length), so that every branch halts and the strings outside $L$ are rejected.

> [!trap]
> - **One rejecting branch is not rejection.** Every branch must reject; a single branch that runs forever means $N$ does not reject.
> - **Swapping accept and reject does not complement** a nondeterministic machine: the swapped machine accepts whenever *some* branch rejects.
> - **Simulate breadth-first, or by dovetailing** — never depth-first.
> - **Nondeterminism never decides an undecidable language:** by Theorem 1 the decider could be made deterministic.

**Example.** The machine "guess a string $x$ symbol by symbol, stopping whenever it likes; then run $M$ on $x$ and accept if $M$ accepts" accepts $\{\langle M\rangle \mid \textsf{Accept}(M)\ne\varnothing\}$. It rejects nothing — a branch that never stops guessing runs forever — which is fine for an acceptor; Theorem 1 turns it into a deterministic acceptor, much like the dovetailing loop on [[concepts/church-turing-thesis]]. By contrast, on input $\mathtt{1}^n$, the machine "guess $d$ with $2\le d\le n-1$ by marking one of the input cells; accept if $d$ divides $n$, otherwise reject" halts on every branch, so it **decides** $\{\mathtt{1}^n \mid n \text{ is composite}\}$.

**Where it appears.** [[1-models-of-computation/09-nondeterministic-turing-machines#91-definitions|§9.1]] (definition, computation tree), [[1-models-of-computation/09-nondeterministic-turing-machines#92-acceptance-and-rejection|§9.2]] (the asymmetry), [[1-models-of-computation/09-nondeterministic-turing-machines#93-time-and-space-complexity|§9.3]] ($\textsf{NTIME}$, $\textsf{NP}$), [[1-models-of-computation/09-nondeterministic-turing-machines#94-deterministic-simulation-via-dovetailing|§9.4]] (Theorem 1), [[1-models-of-computation/09-nondeterministic-turing-machines#95-nondeterminism-as-advice|§9.5]] (advice and dovetailing); for finite automata, [[1-models-of-computation/04-nondeterministic-automata#41-nondeterministic-state-machines|§4.1]], where the [[concepts/subset-construction|subset construction]] plays the role of Theorem 1.

Related: [[concepts/turing-machines]] · [[concepts/nfa]] · [[concepts/subset-construction]] · [[concepts/cook-levin-theorem]] · [[concepts/church-turing-thesis]]
