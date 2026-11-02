---
title: "Review: Turing machines and undecidability (Ch 6–9)"
description: "Exam review of Chapters 6–9, which only the final exam tests: the Turing-machine definition and its conventions, variants and their simulation costs, the universal machine, the four languages of a machine, the self-referential languages, Halt, Accept and NeverAccept with the direction of reductions, Rice's theorem and its variants, the RMMS theorem, questions about behavior, the universal models of Chapter 8, nondeterministic machines and dovetailing, the Cook–Levin theorem; true/false practice, traps, a cheat-sheet list and a study plan."
tags: [toolkit, turing-machines, undecidability, complexity]
aliases: ["Chapters 6–9 review", "final review: computability"]
---

*Scope: Chapters 6–9, tested on the final exam only (Fri Dec 11, 8–11 am; two handwritten double-sided cheat sheets). Each section links to the chapter page that proves its claims; this page only collects. How the classes fit together: [[0-toolkit/03-the-big-picture|the big picture]]; Chapters 1–5: [[0-toolkit/04-review-regular-and-context-free|the other review]].*

> [!recipe] How to use this page
> Read one section, close the page, and rewrite its definitions and statements from memory; then compare. The heart of this half is Chapter 7: be able to write a diagonal argument, a reduction and a proof by Rice's theorem from a blank page, about ten minutes each, with every machine named.

## 1. How this material is graded

An undecidability proof is graded out of 10 with one of three rubrics; choose the tool first (§6 below), then write to its rubric. Full rubrics: [[0-toolkit/06-how-exams-are-graded|how exams are graded]].

| proof | graded | template | model answer |
|---|---|---|---|
| diagonalization | 4 for the wrapper machine built from the hypothetical decider + 6 for the contradiction (3 per case) | [[0-toolkit/02-proof-templates#12-undecidability-by-diagonalization\|diagonalization]], [[1-models-of-computation/07-undecidability#77-more-self-referential-languages\|§7.7]] | Theorem 6 ([[1-models-of-computation/07-undecidability#75-self-haters-gonna-self-hate\|§7.5]]) |
| reduction | 4 for the reduction (the new decider and $M'$, in the right direction) + 3 for yes-instances + 3 for no-instances | [[0-toolkit/02-proof-templates#13-undecidability-by-reduction\|reduction]], [[1-models-of-computation/07-undecidability#79-the-halting-problem-via-reduction\|§7.9]] | [[problems/undecidability-by-reduction-and-by-rice#a-a-reduction-from-accept\|AtLeastTwo by reduction]] |
| Rice's theorem | 4 for a machine whose language has the property + 4 for one whose language does not + 2 for the details, including the right variant | [[0-toolkit/02-proof-templates#14-undecidability-by-rices-theorem\|Rice]], [[1-models-of-computation/07-undecidability#711-rices-theorem\|§7.11]] | [[problems/undecidability-by-reduction-and-by-rice#b-the-same-result-by-rices-theorem\|AtLeastTwo by Rice]] |

If a machine has to be designed, give a transition table or diagram **plus** an English description of every state, use mnemonic state names, and say that missing transitions reject ([[0-toolkit/02-proof-templates#11-describing-a-turing-machine|template]]; [[1-models-of-computation/06-turing-machines#63-a-first-example|§6.3]]; [[problems/designing-a-turing-machine|worked problem]]). The Midterm 1 format also had a true/false problem; §7 collects true/false statements about this material for practice. Practice: [[practice/06-turing-machines|Chapter 6 practice]], [[practice/07-undecidability|Chapter 7 practice]].

## 2. Chapter 6 — Turing machines

[[1-models-of-computation/06-turing-machines|Chapter 6]] · concepts: [[concepts/turing-machines]], [[concepts/acceptable-and-decidable]], [[concepts/universal-turing-machine]], [[concepts/church-turing-thesis]]

> [!definition] Turing machine
> A tape alphabet $\Gamma$ with a blank $\square$; an input alphabet $\Sigma\subseteq\Gamma\setminus\{\square\}$; a finite set of states $Q$ with $\textit{start}$, $\textit{accept}$, $\textit{reject}$; and
> $$
> \delta\colon (Q\setminus\{\textit{accept},\textit{reject}\})\times\Gamma\to Q\times\Gamma\times\{-1,+1\}.
> $$
> A configuration is $(q, x, i)$: state, tape contents, head position; the run on $w$ starts at $(\textit{start}, w, 0)$, and a move left from cell 0 **crashes**. On each input the machine **accepts**, **rejects**, **crashes** or **runs forever**. $M$ **accepts** $L$ if $\textsf{Accept}(M) = L$; $M$ **decides** $L$ if it also halts — rejecting — on every string outside $L$.

| convention | what it means |
|---|---|
| missing transitions | go to $\textit{reject}$ — say so on an exam |
| the left end | mark it before the machine ever walks left; otherwise it may crash |
| a crash | neither accept nor reject: Chapter 7 counts the input as diverging |
| computing a function | one halting state; the output is the tape at that moment without trailing blanks; $M(w)\uparrow$ if $M$ never halts |
| names | acceptable = recognizable = semi-decidable = recursively enumerable; decidable = computable = recursive |

**Variants and what simulating them costs** ([[1-models-of-computation/06-turing-machines#64-variations|§6.4]], [[1-models-of-computation/06-turing-machines#66-tracks-heads-and-tapes|§6.6]], [[1-models-of-computation/06-turing-machines#67-simulating-a-real-computer|§6.7]], [[1-models-of-computation/09-nondeterministic-turing-machines#94-deterministic-simulation-via-dovetailing|§9.4]]). None of them changes which languages are accepted or decided; they change only the running time.

| variant | how a standard machine simulates it | cost of $t$ steps |
|---|---|---|
| stay-put moves | states $Q\times\{0,1\}$: move right, then step back | at most $2t$ |
| $k$ tracks | one track over $\Gamma_1\times\cdots\times\Gamma_k$ | $t$ |
| tape infinite both ways | fold it at cell 0 onto two tracks | $O(t)$ |
| $k$ heads, or $k$ tapes | extra tracks mark the heads; every step sweeps across them | $\Theta(t^2)$, unavoidable in general |
| $k$ tapes on a **two**-tape machine | a cleverer simulation | $O(t\log t)$ |
| recursion; random-access memory | a call stack on an extra tape; a list of $[\textit{address}\bullet\textit{data}]$ pairs | polynomial |
| nondeterminism ($r$ options per step) | breadth-first search of the computation tree | $O(t^2r^{2t})$ on one tape, $O(t\,r^t)$ with two |

The quadratic loss is real: marked palindromes $\{w\mathtt{\#}w^R\}$ take $O(n)$ steps with two heads but $\Omega(n^2)$ with one.

**The universal machine** ([[1-models-of-computation/06-turing-machines#68-universal-turing-machines|§6.8]]). $U$ accepts $\langle M,w\rangle$ iff $M$ accepts $w$, and rejects it iff $M$ rejects $w$. Symbols and states are fixed-length bit strings ($\langle\textit{start}\rangle = \mathtt{1}\cdots\mathtt{1}$, $\langle\textit{reject}\rangle = \mathtt{0}\cdots\mathtt{0}$, and on this site $\langle\textit{accept}\rangle = \mathtt{0}\cdots\mathtt{01}$, a code the book leaves open); a transition $\delta(p,a) = (q,b,\Delta)$ is the block $[\langle p\rangle{\bullet}\langle a\rangle\,|\,\langle q\rangle{\bullet}\langle b\rangle{\bullet}\langle\Delta\rangle]$, and transitions into $\textit{reject}$ are left out; a configuration is a list of cells $[\langle q\rangle{\bullet}\langle a\rangle]$ in which only the head's cell carries a state other than $\textit{reject}$. One step: find the head's cell, look up its block (none: reject), rewrite the cell, pass the state to the neighbor.

**The Church–Turing thesis** — every algorithm can be carried out by a Turing machine — is a claim about the world, not a theorem. It is what lets proofs describe machines in pseudocode.

## 3. Chapter 7 — Undecidability

[[1-models-of-computation/07-undecidability|Chapter 7]] · concepts: [[concepts/diagonalization]], [[concepts/halting-problem]], [[concepts/undecidability-reductions]], [[concepts/rices-theorem]]

**The four languages of a machine.** $\textsf{Accept}(M)$, $\textsf{Reject}(M)$ and $\textsf{Diverge}(M)$ split $\Sigma^*$; $\textsf{Halt}(M) = \textsf{Accept}(M)\cup\textsf{Reject}(M)$. $M$ decides $\textsf{Accept}(M)$ exactly when $\textsf{Diverge}(M) = \varnothing$. "$M$ does not accept $w$" means $M$ rejects **or** diverges.

| result | statement |
|---|---|
| Lemma 1 | from any $M$ build $M^R$ (swap accept and reject), $M^A$ (rejections become endless loops: $\textsf{Reject}(M^A) = \varnothing$) and $M^H$ (rejections become acceptances: $\textsf{Accept}(M^H) = \textsf{Halt}(M)$) |
| Lemma 2 | decidable languages are closed under $\cup$, $\cap$, $\setminus$ — and complement, by Lemma 1(a) |
| Corollary 3 | if $L'$ is decidable and $L\cap L'$, $L\cup L'$, $L\setminus L'$ or $L'\setminus L$ is undecidable, then $L$ is undecidable |
| Lemma 4 | acceptable languages are closed under $\cup$ (run both **in parallel**) and $\cap$ |
| Lemma 5 | an acceptable $L$ is decidable iff $\overline{L}$ is acceptable; so if $L$ is acceptable but undecidable, $\overline{L}$ is **not** acceptable |
| Cantor's theorem | no $f\colon X\to 2^X$ is onto; so some language is not acceptable |

**The named languages** (complements taken among valid encodings):

| language | decidable? | acceptable? | complement acceptable? |
|---|---|---|---|
| $\textsf{SelfReject} = \{\langle M\rangle \mid M \text{ rejects } \langle M\rangle\}$ | no — Theorem 6 | yes — Theorem 11 | no |
| $\textsf{SelfAccept}$, $\textsf{SelfHalt}$ | no — Theorems 7, 8 | yes — Theorem 10, Lemma 4 | no |
| $\textsf{SelfDiverge} = \{\langle M\rangle \mid M \text{ diverges on } \langle M\rangle\}$ | no | no — Theorem 9 | yes |
| $\textsf{Accept}$, $\textsf{Reject}$, $\textsf{Halt}$ (pairs $\langle M,w\rangle$) | no — Theorem 12 for $\textsf{Halt}$ | yes — run $U$, $U^R$, $U^H$ | no |
| $\textsf{Diverge}$ | no | no | yes |
| $\textsf{NeverAccept} = \{\langle M\rangle \mid \textsf{Accept}(M) = \varnothing\}$ | no — Theorem 13 | no | yes — dovetail $M$ over all inputs |
| $\textsf{LeftThree}$ (three left moves in a row on $w$) | no — Theorem 20 | yes — simulate and wait | no |
| $\textsf{NeverLeft}$, $\textsf{ThisIsSparta}$ | yes — Theorem 19; simulate 300 steps | yes | yes |

Also undecidable: $\textsf{NeverReject}$, $\textsf{NeverHalt}$, $\textsf{NeverDiverge}$ (the same reduction with the other languages of $M_w$), $\textsf{DivergeSame}$ (Theorem 14), and $\{\langle M,w\rangle \mid M \text{ accepts } w^k \text{ for every } k\ge0\}$ (Theorem 16).

<!-- fig:ch07-classes -->
<figure class="cs-fig"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 620 316" width="620" height="316" role="img" style="font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-size:14px"><title>Venn diagram of acceptable and co-acceptable languages; their intersection is the decidable languages; example languages in each region</title><defs><marker id="ARR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs><rect x="8" y="8" width="604" height="300" rx="10" fill="none" stroke="var(--muted)" stroke-width="1.2"/><text x="22" y="24" text-anchor="start" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">all languages</text><ellipse cx="235" cy="160" rx="185" ry="108" fill="var(--accent)" fill-opacity="0.07" stroke="var(--accent)" stroke-width="1.6"/><ellipse cx="385" cy="160" rx="185" ry="108" fill="var(--accent2)" fill-opacity="0.07" stroke="var(--accent2)" stroke-width="1.6"/><text x="120" y="40" text-anchor="middle" dominant-baseline="central" fill="var(--accent)" style="font-size:15px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:700;">acceptable</text><text x="500" y="34" text-anchor="middle" dominant-baseline="central" fill="var(--accent2)" style="font-size:15px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:700;">co-acceptable</text><text x="500" y="50" text-anchor="middle" dominant-baseline="central" fill="var(--accent2)" style="font-size:11px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">(complement acceptable)</text><text x="310" y="92" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:700;">decidable</text><text x="310" y="109" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:11px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">= both (Lemma 5)</text><text x="130" y="114" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">SelfReject</text><text x="130" y="136" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">SelfAccept</text><text x="130" y="158" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">SelfHalt</text><text x="130" y="180" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">Accept, Halt</text><text x="130" y="202" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">LeftThree</text><text x="490" y="134" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">SelfDiverge</text><text x="490" y="160" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">Diverge</text><text x="490" y="186" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">NeverAccept</text><text x="310" y="134" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;"><tspan style="font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif">regular languages</tspan></text><text x="310" y="157" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;"><tspan style="font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif">{</tspan><tspan style="font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;font-size:14px">0</tspan><tspan style="font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;font-size:11px" baseline-shift="super">n</tspan><tspan style="font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;font-size:14px">1</tspan><tspan style="font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;font-size:11px" baseline-shift="super">n</tspan><tspan style="font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;font-size:14px">0</tspan><tspan style="font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;font-size:11px" baseline-shift="super">n</tspan><tspan style="font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif">}</tspan></text><text x="310" y="180" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">NeverLeft</text><text x="310" y="203" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">ThisIsSparta</text><text x="310" y="290" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;"><tspan style="font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif">neither: </tspan><tspan style="font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif">{⟨</tspan><tspan style="font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic">M</tspan><tspan style="font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif">⟩ : </tspan><tspan style="font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif">Accept</tspan><tspan style="font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif">(</tspan><tspan style="font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic">M</tspan><tspan style="font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif">)</tspan><tspan style="font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif"> is finite}, </tspan><tspan style="font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif">{⟨</tspan><tspan style="font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic">M</tspan><tspan style="font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif">⟩ : </tspan><tspan style="font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif">Accept</tspan><tspan style="font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif">(</tspan><tspan style="font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic">M</tspan><tspan style="font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif">)</tspan><tspan style="font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif"> is regular}</tspan></text></svg><figcaption><strong>Acceptable, co-acceptable, decidable.</strong> A language is decidable exactly when both it and its complement are acceptable (Lemma 5). SelfReject, SelfAccept, SelfHalt, Accept, Halt and LeftThree sit in the left lune: acceptable but undecidable, so their complements (such as SelfDiverge and Diverge) are not acceptable. NeverAccept is co-acceptable but not acceptable. Some languages are neither, such as the two at the bottom (Corollary 18).</figcaption></figure>

> [!key] The direction of a reduction
> To prove $L$ undecidable, **reduce a known undecidable language to $L$**: assume a decider $\textsf{DecideL}$, and build from it a decider for $\textsf{Accept}$ (or $\textsf{Halt}$, …) that writes down the encoding of a new machine $M'$ and asks $\textsf{DecideL}$ about it. The new decider never *runs* $M'$. The workhorse is
> $$
> M_w(x)\colon\ \text{erase } x;\ \text{write } w;\ \text{run } M \text{ on } w,\qquad \textsf{Accept}(M_w) = \begin{cases}\Sigma^* & \text{if } M \text{ accepts } w,\\ \varnothing & \text{otherwise.}\end{cases}
> $$
> Deciding $L$ with the help of a decider for $\textsf{Halt}$ proves nothing: every decidable language reduces to $\textsf{Halt}$.

> [!template] Template — the three proofs in skeleton form
> **Diagonalization.** Suppose $\textsf{Dec}$ decides $L$. Build $\textsf{Wrap}$ from $\textsf{Dec}$ (swap its answers, or redirect them to a loop) so that for every $M$, $\textsf{Wrap}$ accepts (or halts on) $\langle M\rangle$ iff $M$ does not … $\langle M\rangle$. Take $M = \textsf{Wrap}$; both cases contradict. \
> **Reduction.** Suppose $\textsf{DecideL}$ decides $L$. $\textsf{DecideAccept}$: given $\langle M,w\rangle$, write $\langle M'\rangle$, run $\textsf{DecideL}$ on it, return its answer (or the opposite). If $M$ accepts $w$, then … so $\langle M'\rangle\in L$; if $M$ rejects **or diverges**, then … so $\langle M'\rangle\notin L$. So $\textsf{DecideAccept}$ decides $\textsf{Accept}$ — impossible. \
> **Rice.** $L = \textsf{AcceptIn}(\mathcal{L})$ for $\mathcal{L} = \{\ldots\}$; membership depends only on $\textsf{Accept}(M)$; $\textsf{Accept}(Y)\in\mathcal{L}$ for $Y = \ldots$; $\textsf{Accept}(N)\notin\mathcal{L}$ for $N = \ldots$; so $L$ is undecidable by Rice's theorem.

> [!key] Rice's theorem and its variants
> If $\textsf{Accept}(Y)\in\mathcal{L}$ for some machine $Y$ and $\textsf{Accept}(N)\notin\mathcal{L}$ for some machine $N$, then $\textsf{AcceptIn}(\mathcal{L}) = \{\langle M\rangle \mid \textsf{Accept}(M)\in\mathcal{L}\}$ is undecidable. (The proof, when $\varnothing\notin\mathcal{L}$: a reduction from $\textsf{Halt}$ with $\textsf{WTF}(x)$ = "run $M$ on $w$, then $Y$ on $x$"; otherwise apply it to the complementary property.) The same holds with $\textsf{Reject}$, $\textsf{Halt}$ or $\textsf{Diverge}$ in place of $\textsf{Accept}$, and for $\textsf{DecideIn}(\mathcal{L})$ with deciders $Y$ and $N$. Use the variant that matches the definition.
>
> Witnesses: $M_{\textsf{Accept}}$ accepts everything ($\textsf{Accept} = \Sigma^*$); $M_{\textsf{Reject}}$ rejects everything ($\textsf{Accept} = \varnothing$, $\textsf{Halt} = \Sigma^*$); $M_{\textsf{Diverge}}$ moves right forever ($\textsf{Accept} = \textsf{Halt} = \varnothing$). Corollary 15: "accepts $\varepsilon$", "accepts $\mathtt{UIUC}$", "accepts exactly three strings", "accepts every palindrome", "$\textsf{Accept}(M)$ is regular / not regular / undecidable", "$\textsf{Accept}(M) = \textsf{Accept}(N)$" are all undecidable.

**When Rice's theorem does not apply** ([[1-models-of-computation/07-undecidability#711-rices-theorem|§7.11]]): a property of the machine's **behavior** or **text** ($\textsf{ThisIsSparta}$, "$M$ has 374 states": decidable); **self-reference** ($\textsf{RevAccept} = \{\langle M\rangle \mid M \text{ accepts } \langle M\rangle^R\}$: undecidable, but by a reduction); a **trivial** property (no $Y$ or no $N$: decidable); and **unacceptability**, which Rice never proves.

> [!key] The Rice–McNaughton–Myhill–Shapiro theorem ([[1-models-of-computation/07-undecidability#712-the-ricemcnaughtonmyhillshapiro-theorem|§7.12]])
> For a set $\mathcal{L}$ of acceptable languages, $\textsf{AcceptIn}(\mathcal{L})$ is acceptable **iff** $\mathcal{L}$ is **monotone** (acceptable supersets of its members are members), **compact** (every member has a finite subset that is a member) and **finitely acceptable** (its finite members, listed out, form an acceptable language). **Lemma 17:** not monotone ⇒ not acceptable. **Corollary 18:** "$\textsf{Accept}(M)$ is finite / infinite / regular / not regular / decidable / undecidable", "$M$ accepts some string of $\textsf{SelfDiverge}$" and "$\textsf{Accept}(M) = \textsf{Accept}(N)$" are not acceptable.
>
> Sanity check: "$\textsf{Accept}(M)\ne\varnothing$" is monotone, compact (a single string suffices) and finitely acceptable — and indeed dovetailing accepts that language.

**Behavior** ([[1-models-of-computation/07-undecidability#713-turing-machine-behavior-its-complicated|§7.13]]). $\textsf{NeverLeft}$ is decidable: a machine that only moves right and has read more than $\lvert Q\rvert$ blanks has repeated a state on a blank and will run right forever. $\textsf{LeftThree}$ is undecidable: a simulation can be padded so that it never makes three left moves in a row until it would accept. Rules of thumb, not theorems: a behavior is **probably undecidable** if a machine could simulate an arbitrary machine while avoiding it and show it only on acceptance; **probably decidable** if it confines the machine to finitely many configurations or forces an endless loop after finitely many steps.

## 4. Chapter 8 — Universal models

[[1-models-of-computation/08-universal-models|Chapter 8]] — a sketch in the book; treat it as background. A model that can simulate every Turing machine inherits both its power and its undecidability: a decider for "does this run stop?" would decide $\textsf{Halt}$.

| model | the trick that simulates a Turing machine | what becomes undecidable |
|---|---|---|
| two-stack machine | the tape cut at the head: one stack holds the left part, the other the head cell and the right part | halting (one stack and one pass over the input give only context-free languages) |
| counter machines | three counters: the halves of the tape as base-$\lvert\Gamma\rvert$ numbers; two counters: $(a,b,c)$ stored as $2^a3^b5^c$ | whether a two-counter machine started at $(0,0)$ halts; universal only for suitably encoded inputs |
| FRACTRAN | the prime exponents of $N$ are counters; a fraction $f$ applies only if $Nf$ is an integer — a built-in zero test | whether the program halts |
| Post's correspondence problem | dominoes whose solutions spell a halting computation, the bottom row one configuration ahead | PCP: undecidable but acceptable, so its complement is not acceptable |
| matrix mortality | strings as integer matrices, built from a PCP instance | is some product zero? (already for two $15\times15$ or six $3\times3$ matrices) |
| mirrors, Wang tiles | a ray's position or a row of tiles encodes a configuration | does the ray reach a region? can the plane be tiled? |
| combinator calculus | $\mathsf{I}x\to x$, $\mathsf{K}xy\to x$, $\mathsf{S}xyz\to xz(yz)$; equivalent to the λ-calculus | does a term have a normal form? |

## 5. Chapter 9 — Nondeterministic Turing machines

[[1-models-of-computation/09-nondeterministic-turing-machines|Chapter 9]] · concepts: [[concepts/nondeterministic-turing-machines]], [[concepts/cook-levin-theorem]]

| notion | what to know cold |
|---|---|
| definition | $\delta\colon (Q\setminus\{\textit{accept},\textit{reject}\})\times\Gamma\to 2^{Q\times\Gamma\times\{-1,+1\}}$; the runs on $w$ form a **computation tree** |
| accept / reject | accepts $w$ if **some** branch accepts (others may run forever); rejects $w$ if **every** branch rejects — then the whole tree is finite; otherwise neither |
| Theorem 1 | a deterministic machine accepts and rejects exactly the same strings: breadth-first search of the tree, $O(t^2r^{2t})$ steps on one tape, $O(t\,r^t)$ with two; depth-first search can get stuck in an infinite branch |
| advice and dovetailing | number the options $1,\dots,r$; $N$ accepts $w$ iff some advice string makes the deterministic $M$ accept $(w,x)$. Dovetailing tries all advice strings of length $t$ for $t$ steps, $t = 1, 2, \ldots$: $O(t\,r^t)$ with three tapes, $O(t^2r^t)$ with one |
| complexity classes | $\textsf{TIME}$, $\textsf{NTIME}$, $\textsf{SPACE}$, $\textsf{NSPACE}$ on multi-tape machines; $\textsf{P} = \bigcup_k\textsf{TIME}(n^k)$, $\textsf{NP} = \bigcup_k\textsf{NTIME}(n^k)$; $\textsf{P}\subseteq\textsf{NP}\subseteq$ exponential time; $\textsf{NP}$ = languages with polynomial-time verifiers |
| Cook–Levin | if $\textsf{SAT}\in\textsf{P}$ then $\textsf{P} = \textsf{NP}$. For $L\in\textsf{NP}$ with a verifier running $N = \max\{1, n^k\}$ steps, the formula $\Phi_w$ has variables $Q_{t,i,q}$ (state $q$, head on cell $i$, time $t$) and $T_{t,i,a}$ (cell $i$ holds $a$), five kinds of constraints (boundaries, initialization, advice, transitions, acceptance), size $O(N^2) = O(n^{2k})$, and is satisfiable iff $w\in L$ |

So $\textsf{SAT}$ is NP-hard — every $L\in\textsf{NP}$ reduces **to** it — and, being in $\textsf{NP}$, NP-complete. To prove another problem NP-hard, reduce $\textsf{SAT}$ to it: the same direction rule as for undecidability ([[1-models-of-computation/09-nondeterministic-turing-machines#96-the-cooklevin-theorem|§9.6]]; the reductions themselves are in [[2-algorithms/12-np-hardness|Algorithms, Chapter 12]]).

## 6. Which tool for which question

| the language or question | first try | example |
|---|---|---|
| $\{\langle M\rangle \mid \textsf{Accept}(M) \text{ has a property}\}$, non-trivial | Rice's theorem: undecidable | "$M$ accepts at least two strings" ([[problems/undecidability-by-reduction-and-by-rice\|worked problem]]) |
| the condition is about $\textsf{Halt}(M)$, $\textsf{Reject}(M)$ or $\textsf{Diverge}(M)$ | the matching variant of Rice | "$M$ halts on every input": $\textsf{HaltIn}(\{\Sigma^*\})$ with $Y = M_{\textsf{Accept}}$, $N = M_{\textsf{Diverge}}$ |
| a bounded run, or a behavior with finitely many configurations | simulate: decidable | $\textsf{ThisIsSparta}$, $\textsf{NeverLeft}$ |
| an unbounded behavior | a reduction from $\textsf{Accept}$ with a padded simulation | $\textsf{LeftThree}$ |
| the machine's own encoding appears in the condition | a diagonal argument, or a reduction with $M_w$ | $\textsf{SelfReject}$; $\textsf{RevAccept}$ |
| "is $L$ acceptable?" | describe the search: run $U$, dovetail over inputs and step counts, or guess ([[0-toolkit/02-proof-templates#15-acceptable-by-dovetailing\|template]]) | $\textsf{Accept}(M)\ne\varnothing$; $\textsf{Halt}$ |
| "is $L$ not acceptable?" | $L$ undecidable with an acceptable complement (Lemma 5, [[0-toolkit/02-proof-templates#16-not-acceptable-by-lemma-5\|template]]); a non-monotone property (Lemma 17); a diagonal argument | $\textsf{NeverAccept}$; "$\textsf{Accept}(M)$ is finite"; $\textsf{SelfDiverge}$ |

## 7. True or false: twelve to practice

| statement | answer | one-sentence justification |
|---|---|---|
| Every decidable language is acceptable. | true | a decider accepts its language (§6.2). |
| If $M$ does not accept $w$, then $M$ rejects $w$. | false | $M$ may run forever, or crash. |
| If $L$ and $\overline{L}$ are both acceptable, then $L$ is decidable. | true | run both acceptors in parallel (Lemma 5). |
| The complement of every acceptable language is acceptable. | false | $\textsf{Halt}$ is acceptable, but by Lemma 5 its complement is not. |
| $\textsf{Halt}$ is undecidable, so it is not acceptable. | false | the universal machine accepts it. |
| "$M$ has 374 states" is undecidable by Rice's theorem. | false | it is decidable — a property of the machine's text, not of its language. |
| Rice's theorem shows that $\{\langle M\rangle \mid \textsf{Accept}(M)\ne\varnothing\}$ is not acceptable. | false | Rice proves only undecidability; dovetailing accepts this language. |
| Deciding $L$ with a subroutine that decides $\textsf{Halt}$ proves that $L$ is undecidable. | false | wrong direction: every decidable language reduces to $\textsf{Halt}$. |
| A nondeterministic machine rejects $w$ if some branch rejects $w$. | false | every branch must reject (§9.2). |
| Every language accepted by a nondeterministic Turing machine is acceptable. | true | Theorem 1 of Chapter 9. |
| Some language decided by a two-tape machine is decided by no one-tape machine. | false | one tape simulates two with a quadratic slowdown; only time changes. |
| A finite-state machine with two stacks is as powerful as a Turing machine. | true | the tape is two stacks cut at the head (§8.2). |

## 8. The traps that cost the most points

> [!trap] Across Chapters 6–9
> 1. **"Does not accept" is not "rejects".** Every second case of a reduction must handle rejection **and** divergence.
> 2. **A decider halts on every input**, including strings that encode nothing; the decider you build in a reduction must halt even when $M'$ would not.
> 3. **Wrong direction.** The hypothetical decider for the *new* language is the subroutine; the language you end up deciding is the known undecidable one.
> 4. **Running $M'$ instead of writing it down.** $\textsf{DecideAccept}$ only computes $\langle M'\rangle$; say what $M'$ does on *every* input $x$.
> 5. **Unnamed machines.** "It accepts" is ambiguous with four machines around: name $\textsf{DecideL}$, $\textsf{DecideAccept}$, $M$ and $M'$.
> 6. **Diagonalization on the wrong machine.** The contradiction comes from running the wrapper on **its own** encoding; say why that run halts.
> 7. **Rice misapplied:** to behavior or to the machine's text, without the property written as a set of languages, without concrete $Y$ and $N$, with the wrong variant, or to conclude "not acceptable".
> 8. **The union of acceptable languages run in series.** The first acceptor may run forever; simulate in parallel (Lemma 4).
> 9. **Swapping accept and reject** complements only a deterministic decider — not a machine that may diverge, not a nondeterministic machine.
> 10. **Machine design without the conventions:** say that missing transitions reject, mark the left end, and trace $\varepsilon$ and near-misses.
> 11. **Confusing time with power.** Tapes, heads and nondeterminism change running times, never which languages are decidable or acceptable.

## 9. What to put on your cheat sheet

The final allows two double-sided, handwritten letter sheets for the whole course. For Chapters 6–9:

- The Turing-machine tuple, $\delta$'s type, configurations, the four outcomes, and accepts versus decides.
- The variants table with its costs ($2t$, $\Theta(t^2)$, $O(t\log t)$, $O(t^2r^{2t})$, $O(t\,r^t)$).
- Lemmas 1–5 in one line each, and Corollary 3.
- The table of named languages: decidable, acceptable, complement acceptable.
- The three proof skeletons with their rubrics (4+6, 4+3+3, 4+4+2), and $M_w$.
- Rice's statement, its variants, the witnesses $M_{\textsf{Accept}}$, $M_{\textsf{Reject}}$, $M_{\textsf{Diverge}}$, and the four cases where it does not apply.
- RMMS: monotone, compact, finitely acceptable; Lemma 17.
- The rules of thumb for behavior, with $\textsf{NeverLeft}$ and $\textsf{LeftThree}$.
- Nondeterministic acceptance versus rejection; Theorem 1 and dovetailing; the definitions of P and NP; the Cook–Levin statement and its variables.

## 10. A study plan for the final

> [!tip] Chapters 6–9 between Midterm 2 (Nov 9) and the final (Dec 11)
> 1. **Read first, once.** Chapter 6 for the definitions and conventions; Chapter 7 slowly, section by section, rewriting each template from memory; Chapters 8 and 9 for the statements in §4 and §5 above.
> 2. **Drill the three proofs.** Work the [[problems/undecidability-by-reduction-and-by-rice|worked problem]] without looking, then the [[practice/07-undecidability|Chapter 7 practice]] problems: one diagonal argument, two reductions and two Rice proofs a day for a week, each graded against its rubric.
> 3. **Classify languages fast.** Go down the table of §3 and the zoo of [[0-toolkit/03-the-big-picture#3-the-language-zoo|the big picture]] covering the answers: decidable? acceptable? complement acceptable? which tool?
> 4. **Design one machine** end to end ([[practice/06-turing-machines|Chapter 6 practice]]): passes in English, table, meanings, traces.
> 5. **Write the cheat sheets** by hand from §9 here and §9 of [[0-toolkit/04-review-regular-and-context-free|the Chapters 1–5 review]], then finish with the true/false tables of both reviews and the traps.

Related: [[0-toolkit/03-the-big-picture|the big picture]] · [[0-toolkit/04-review-regular-and-context-free|review of Chapters 1–5]] · [[0-toolkit/06-how-exams-are-graded|how exams are graded]] · [[practice/index|practice problems]]

### Sources for this page
Erickson, *Models of Computation*, Chapters 6–9, summarized in our own words, with the book's numbering (Chapter 7's results are numbered without a chapter prefix); every statement here follows the chapter page it links to, and the figure is the one from [[1-models-of-computation/07-undecidability#78-nevertheless-acceptable|§7.8]]. Rubrics: CS/ECE 374 A (Fall 2026) undecidability rubrics, paraphrased. The tables, the true/false items, the cheat-sheet list and the study plan are original. Every machine, bound and example behind these statements is checked on the chapter pages by `tools/checks/ch06.py` to `ch09.py`.
