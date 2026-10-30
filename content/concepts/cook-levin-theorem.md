---
title: "Cook–Levin theorem"
description: "If SAT can be decided in polynomial time, then P = NP — exactly what the book proves, the verifier definition of NP it uses, the formula Φ_w behind the proof, and how the algorithms half turns it into NP-hardness."
tags: [concept, complexity]
aliases: ["Cook-Levin theorem", "Cook's theorem"]
---

> [!key] The Cook–Levin theorem (as stated in §9.6)
> If $\textsf{SAT}\in\textsf{P}$, then $\textsf{P} = \textsf{NP}$.
>
> $\textsf{SAT}$ is the set of satisfiable boolean formulas, and $\textsf{P}$ is the set of languages decided by deterministic Turing machines in polynomial time. $L\in\textsf{NP}$ if there are an integer $k$ and a deterministic **verifier** $M$ that halts within $\max\{1,\lvert w\rvert^k\}$ steps on every input $(w,x)$, such that $M$ accepts $(w,x)$ for **some** advice string $x$ when $w\in L$, and rejects $(w,x)$ for **every** $x$ when $w\notin L$.

**Where it comes from.** Fix $L\in\textsf{NP}$ with verifier $M$, and let $N = \max\{1, n^k\}$ for an input $w$ of length $n$. A run of $M$ is a table with $N+1$ rows (times) and $O(N)$ columns (cells). Boolean variables $Q_{t,i,q}$ ("after $t$ steps, $M$ is in state $q$ with its head on cell $i$") and $T_{t,i,a}$ ("after $t$ steps, cell $i$ holds $a$") describe the table, and a formula $\Phi_w$ says: row 0 is the start configuration on $w$ followed by an *unknown* advice string, each advice cell holds exactly one symbol, each row follows from the previous one by $\delta$, and $M$ reaches $\textit{accept}$. So $\Phi_w$ is satisfiable iff some advice makes $M$ accept iff $w\in L$. $\Phi_w$ has size $O(N^2)$ and is built in $O(N^2) = O(n^{2k})$ time, so a $\textsf{SAT}$ algorithm running in $O(m^c)$ time on formulas of size $m$ would decide $L$ in $O(n^{2kc})$ time.

> [!recipe] Recipe — the theorem as the algorithms half uses it
> - **The proof is a reduction:** $w\mapsto\Phi_w$ is computable in polynomial time, and $w\in L\iff\Phi_w\in\textsf{SAT}$. In the vocabulary of [[2-algorithms/index|the algorithms half]], every language in $\textsf{NP}$ reduces to $\textsf{SAT}$, so $\textsf{SAT}$ is **NP-hard**; with $\textsf{SAT}\in\textsf{NP}$ (example below) it is **NP-complete**. Chapter 9 itself states only the implication above.
> - **Hardness proofs start from $\textsf{SAT}$:** to show that a problem $X$ is NP-hard, reduce $\textsf{SAT}$ (or another NP-hard problem) **to** $X$ in polynomial time — the same direction rule as for [[concepts/undecidability-reductions|undecidability]].

> [!trap]
> - The theorem does **not** say that $\textsf{SAT}\notin\textsf{P}$ or that $\textsf{P}\ne\textsf{NP}$; both questions are open.
> - $\textsf{NP}$ means *nondeterministic polynomial time*, not "not polynomial": $\textsf{P}\subseteq\textsf{NP}$.
> - The time bound depends on $\lvert w\rvert$ only, so the verifier reads at most polynomially many advice symbols: certificates are short.
> - **Direction:** every $\textsf{NP}$ problem reduces *to* $\textsf{SAT}$. Reducing a new problem *to* $\textsf{SAT}$ shows that it is no harder than $\textsf{SAT}$, not that it is hard.
> - The polynomial size of $\Phi_w$ is essential; an exponentially long formula would prove nothing.

**Example — $\textsf{SAT}\in\textsf{NP}$.** The advice is an assignment, and the verifier evaluates the formula, in polynomial time. The formula $(a\lor b)\land(\lnot a\lor\lnot b)\land(a\lor\lnot b)$ is satisfiable, with certificate $a = \textsf{True}$, $b = \textsf{False}$ (the only one). Add the clause $(\lnot a\lor b)$ and each of the four assignments falsifies some clause, so the verifier rejects every advice string: the new formula is not in $\textsf{SAT}$.

**Where it appears.** [[1-models-of-computation/09-nondeterministic-turing-machines#96-the-cooklevin-theorem|§9.6]] (statement and proof), [[1-models-of-computation/09-nondeterministic-turing-machines#93-time-and-space-complexity|§9.3]] ($\textsf{P}$ and $\textsf{NP}$), [[1-models-of-computation/09-nondeterministic-turing-machines#95-nondeterminism-as-advice|§9.5]] (advice strings), [[2-algorithms/index|the algorithms half]] (NP-hardness and NP-completeness), [[2-algorithms/12-np-hardness#123-np-hard-np-easy-and-np-complete|§12.3]] (the book's statement, for circuit satisfiability) and [[2-algorithms/12-np-hardness#125-reductions-and-sat|§12.5]]–[[2-algorithms/12-np-hardness#126-3sat-from-circuitsat|§12.6]] (the first reductions, CircuitSat → Sat and → 3Sat).

Related: [[concepts/nondeterministic-turing-machines]] · [[concepts/undecidability-reductions]] · [[concepts/turing-machines]] · [[concepts/church-turing-thesis]] · [[concepts/np-hardness]]
