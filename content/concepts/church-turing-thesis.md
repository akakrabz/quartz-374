---
title: "Church–Turing thesis"
description: "Every algorithm can be carried out by a Turing machine: why this is a thesis rather than a theorem, the evidence for it, the pseudocode it licenses in proofs, and what it does not say (anything about speed)."
tags: [concept, turing-machines]
aliases: ["Church-Turing thesis", "Church's thesis", "Turing's thesis"]
---

> [!key] The Church–Turing thesis
> Every function that can be computed by an algorithm — any finite, mechanical procedure — can be computed by a Turing machine.
>
> So "decidable" and "acceptable" mean the same thing for Turing machines, for Python programs, and for any other reasonable model of computation.

**Why it is a thesis, not a theorem.** "Algorithm" has no formal definition apart from the models themselves, so there is nothing to prove the claim against: it is a claim about the world. The evidence is that every reasonable model proposed since 1936 — Church's λ-calculus, the recursive functions of Gödel and Herbrand, multi-tape and nondeterministic Turing machines, random-access machines, two-stack and counter machines, combinator calculus — computes exactly the same functions. Each of *those* equivalences is a theorem, proved by simulating each model in the other; the thesis extrapolates to every model anyone will propose.

> [!recipe] Using the thesis in proofs
> 1. **Describe machines in pseudocode:** "on input $\langle M,w\rangle$: write $\langle M'\rangle$; run $\textsf{DecideL}$ on $\langle M'\rangle$; return its answer."
> 2. **Allowed steps:** parse and modify encodings; simulate a machine with the [[concepts/universal-turing-machine|universal machine]], for a fixed number of steps or without limit; run several simulations **in parallel**, one step each in turn; count; call a hypothetical decider as a subroutine.
> 3. **Not steps:** "if $M$ halts on $w$, …", "if $M$ accepts some string, …", "try every input, then answer" — unless a decider for exactly that question is the hypothesis you are about to refute.
>
> A simulation without a step limit may run forever: harmless in an acceptor, fatal in a decider.

> [!trap]
> - The thesis **cannot be proved**, and it is not what shows two given models equivalent: that takes a simulation, as in [[1-models-of-computation/06-turing-machines#66-tracks-heads-and-tapes|§6.6]] or [[1-models-of-computation/09-nondeterministic-turing-machines#94-deterministic-simulation-via-dovetailing|§9.4]].
> - It is about **what** can be computed, not **how fast**: one tape instead of two can cost a quadratic factor, and the known simulation of nondeterminism an exponential one.
> - It makes undecidability absolute: no program in any language decides $\textsf{Halt}$ — not just no Turing machine.

**Example — dovetailing.** $\{\langle M\rangle \mid \textsf{Accept}(M)\ne\varnothing\}$ is acceptable. In pseudocode:

```
for k ← 1, 2, 3, …
    for each of the first k strings x (in length-lexicographic order)
        simulate M on x for k steps
        if M accepted x: accept
```

If $M$ accepts the $j$-th string within $s$ steps, the loop accepts by round $\max\{j,s\}$ at the latest; if $\textsf{Accept}(M) = \varnothing$, it runs forever — allowed for an acceptor. By the thesis (or by hand, with the constructions of Chapter 6) this is a Turing machine. Running $M$ to completion on one string at a time would get stuck on the first string where $M$ runs forever.

**Where it appears.** [[1-models-of-computation/06-turing-machines|Chapter 6]] (the opening: Turing, Church and the thesis), [[1-models-of-computation/06-turing-machines#61-why-bother|§6.1]] (simple enough to reason about, powerful enough to simulate everything), [[1-models-of-computation/06-turing-machines#67-simulating-a-real-computer|§6.7]] (recursion and random-access memory), [[1-models-of-computation/08-universal-models|Chapter 8]] (two stacks, counters, FRACTRAN, tiles and combinators are all universal), [[0-toolkit/03-the-big-picture|the big picture]].

Related: [[concepts/turing-machines]] · [[concepts/universal-turing-machine]] · [[concepts/acceptable-and-decidable]] · [[concepts/nondeterministic-turing-machines]] · [[concepts/halting-problem]]
