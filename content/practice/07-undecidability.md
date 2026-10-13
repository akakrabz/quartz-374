---
title: "Practice — Chapter 7: Undecidability"
description: "8 practice problems (3 easy, 3 medium, 2 hard) on undecidability: closure facts and Lemma 5, classifying languages as decidable, acceptable but undecidable, or not acceptable, a reduction in the wrong direction, Rice's theorem with the right variant, one decidable and one undecidable machine behavior, dovetailing, a diagonalization proof and a full reduction proof, each with a folded hint and a worked solution."
tags: [practice, undecidability]
chapter: 7
---

*Practice for [[1-models-of-computation/07-undecidability|Chapter 7]] · concepts: [[concepts/acceptable-and-decidable]] · [[concepts/diagonalization]] · [[concepts/undecidability-reductions]] · [[concepts/rices-theorem]] · all practice: [[practice/index|hub]] · by difficulty: [[practice/easy|easy]] · [[practice/medium|medium]] · [[practice/hard|hard]] · [[practice/topics|by topic]]*

Work each problem on paper first. Open the **hint** only when stuck, and the **solution** only after you have an answer you would hand in. Every concrete machine in the solutions has been checked by a script. Conventions as in [[1-models-of-computation/07-undecidability#71-acceptable-versus-decidable|§7.1]]: "$M$ does not accept $w$" means that $M$ rejects $w$ or diverges on it (a crash counts as diverging), and $\overline{L} = \Sigma^*\setminus L$. $M_{\textsf{Accept}}$, $M_{\textsf{Reject}}$ and $M_{\textsf{Diverge}}$ are the machines of [[1-models-of-computation/07-undecidability#711-rices-theorem|§7.11]] that accept at once, reject at once, and move right forever.

## Easy

### 7.1 Closure facts, true or false

> [!easy] Easy · true or false · closure of decidable languages · acceptable vs decidable
> All languages are over a fixed alphabet $\Sigma$. Answer each statement **Yes** (always true) or **No**, with a one-sentence reason; for a No, give a counterexample.
>
> (a) If $L$ is decidable, then $\overline{L}$ is decidable.
>
> (b) If $L$ is acceptable, then every subset of $L$ is acceptable.
>
> (c) If $L_1$ and $L_2$ are decidable, then their concatenation $L_1\bullet L_2$ is decidable.
>
> (d) If $L_1\cup L_2$ is decidable, then $L_1$ and $L_2$ are both decidable.
>
> (e) If $L$ and $\overline{L}$ are both acceptable, then $L$ is decidable.
>
> (f) If $L$ is undecidable and $L'$ is decidable, then $L\setminus L'$ is undecidable.
>
> *Source: original.*

> [!hint]- Hint
> $\Sigma^*$ and $\varnothing$ are decidable, $\textsf{Halt}$ is acceptable but undecidable, and $\textsf{SelfDiverge}$ is not even acceptable. Most of the No's need nothing more.

> [!solution]- Solution
> **(a) Yes.** Swap the accept and reject states of a decider for $L$ (Lemma 1(a)); the new machine still halts on every input, and it decides $\overline{L}$.
>
> **(b) No.** $\Sigma^*$ is acceptable (even decidable), but its subset $\textsf{SelfDiverge}$ is not acceptable (Theorem 9).
>
> **(c) Yes.** Given $w$, try all $\lvert w\rvert+1$ ways to write $w = xy$, running the decider for $L_1$ on $x$ and the decider for $L_2$ on $y$, and accept if some split passes both tests; there are finitely many splits and every test halts, so this machine halts on every input.
>
> **(d) No.** $\textsf{Halt}\cup\overline{\textsf{Halt}} = \Sigma^*$ is decidable, but $\textsf{Halt}$ is not (Theorem 12).
>
> **(e) Yes.** This is Lemma 5: run an acceptor for $L$ and one for $\overline{L}$ in parallel on $w$; exactly one of them eventually accepts, and which one tells you whether $w\in L$.
>
> **(f) No.** Take $L' = \Sigma^*$: then $L\setminus L' = \varnothing$, which is decidable whatever $L$ is. (Corollary 3 runs the other way: if $L'$ is decidable and $L\setminus L'$ is undecidable, then $L$ is undecidable.)
>
> **Watch out:** "try every split" in (c) works because each test halts. For two *acceptable* languages the concatenation is still acceptable, but the splits must be tested **in parallel**, one step at a time — a test that runs forever would block the rest.
>
> **Answer.** (a) Yes (b) No (c) Yes (d) No (e) Yes (f) No.

### 7.2 Decidable, acceptable, or neither

> [!easy] Easy · true or false · acceptable vs decidable · Rice's theorem
> Answer each statement **Yes** or **No**, with a one-sentence reason. Then put each language in one of three classes: **decidable**, **acceptable but undecidable**, or **not acceptable**.
>
> (a) $\{\langle M\rangle \mid M \text{ accepts at least one string}\}$ is acceptable.
>
> (b) $\{\langle M\rangle \mid M \text{ accepts no string}\}$ is acceptable.
>
> (c) By Rice's theorem, $\{\langle M\rangle \mid \text{some transition of } M \text{ writes the symbol } \mathtt{\#}\}$ is undecidable.
>
> (d) $\{\langle M, w\rangle \mid M \text{ halts on } w \text{ within } \lvert w\rvert^2 \text{ steps}\}$ is decidable.
>
> (e) $\{\langle M\rangle \mid M \text{ halts on every input of length } 3\}$ is decidable.
>
> (f) $\{\langle M\rangle \mid \textsf{Accept}(M) \text{ is finite}\}$ is undecidable.
>
> *Source: original.*

> [!hint]- Hint
> An acceptor only has to say yes on the yes-instances; it may run forever on the others. So "acceptable" asks: is there a search that succeeds exactly when the answer is yes? For a language that is not acceptable, use Lemma 5 or Corollary 18.

> [!solution]- Solution
> **(a) Yes.** Dovetail: in round $t = 1, 2, 3, \dots$, run $M$ for $t$ steps on each of the first $t$ strings of $\Sigma^*$, and accept as soon as one of these runs accepts; if $M$ accepts the $i$th string within $s$ steps, this happens by round $\max(i,s)$. *Acceptable but undecidable* — undecidable by Rice's theorem with $Y = M_{\textsf{Accept}}$ and $N = M_{\textsf{Reject}}$.
>
> **(b) No.** This is $\textsf{NeverAccept}$. Its complement — the language of (a) together with the strings that encode no machine — is acceptable (Lemma 4), so if $\textsf{NeverAccept}$ were acceptable as well, Lemma 5 would make it decidable, contradicting Theorem 13. *Not acceptable.*
>
> **(c) No.** Whether some transition writes $\mathtt{\#}$ can be read off the encoding $\langle M\rangle$ by scanning its list of transitions, so the language is *decidable*. Rice's theorem does not apply because this is a property of the transition table, not of $\textsf{Accept}(M)$: adding a new state that is never entered, with a transition that writes $\mathtt{\#}$, changes membership but not the language.
>
> **(d) Yes.** Simulate $M$ on $w$ for $\lvert w\rvert^2$ steps with the universal machine, counting steps; accept if $M$ has halted, otherwise reject. *Decidable.*
>
> **(e) No.** Run $M$ on each of the finitely many inputs of length 3, one after another, and accept if every run halts: this accepts the language, but it runs forever when some run does. The language is undecidable by **Rice's halting theorem**, with $\mathcal{L} = \{L \mid L \text{ contains every string of length } 3\}$, $Y = M_{\textsf{Accept}}$ ($\textsf{Halt}(Y) = \Sigma^*\in\mathcal{L}$) and $N = M_{\textsf{Diverge}}$ ($\textsf{Halt}(N) = \varnothing\notin\mathcal{L}$). *Acceptable but undecidable.*
>
> **(f) Yes.** Rice's theorem with $\mathcal{L} = \{L \mid L \text{ is finite}\}$, $Y = M_{\textsf{Reject}}$ (it accepts $\varnothing$, which is finite) and $N = M_{\textsf{Accept}}$ (it accepts $\Sigma^*$, which is not). In fact this language is *not acceptable* (Corollary 18(a)), and neither is $\{\langle M\rangle \mid \textsf{Accept}(M) \text{ is infinite}\}$ (Corollary 18(b)).
>
> | | the language: $\{\langle M\rangle \mid \ldots\}$ | class |
> |---|---|---|
> | (a) | $M$ accepts at least one string | acceptable but undecidable |
> | (b) | $M$ accepts no string | not acceptable |
> | (c) | some transition of $M$ writes $\mathtt{\#}$ | decidable |
> | (d) | $M$ halts on $w$ within $\lvert w\rvert^2$ steps (pairs $\langle M,w\rangle$) | decidable |
> | (e) | $M$ halts on every input of length 3 | acceptable but undecidable |
> | (f) | $\textsf{Accept}(M)$ is finite | not acceptable |
>
> **Watch out:** in (b), "the complement of $\textsf{NeverAccept}$ is acceptable" is not a contradiction by itself — Lemma 5 needs *both* a language and its complement to be acceptable before it says anything. The argument is: the complement is acceptable and $\textsf{NeverAccept}$ is undecidable, so $\textsf{NeverAccept}$ cannot be acceptable.
>
> **Answer.** (a) Yes (b) No (c) No (d) Yes (e) No (f) Yes; classes as in the table.

### 7.3 A reduction that proves nothing

> [!easy] Easy · find the error · reductions
> Let $\textsf{EvenAccept} := \{\langle M\rangle \mid M \text{ accepts at least one string of even length}\}$. A student writes:
>
> *"Claim: $\textsf{EvenAccept}$ is undecidable. Proof: Suppose some machine $\textsf{DecideAccept}$ decides $\textsf{Accept}$. Given $\langle M\rangle$, build the machine $M'$ that ignores its own input and runs $M$ on all strings of even length in parallel (dovetailing), accepting as soon as $M$ accepts one of them. Then $M'$ accepts $\varepsilon$ if and only if $\langle M\rangle\in\textsf{EvenAccept}$. So the machine that writes $\langle M', \varepsilon\rangle$ and runs $\textsf{DecideAccept}$ on it decides $\textsf{EvenAccept}$. Since $\textsf{Accept}$ is undecidable, $\textsf{EvenAccept}$ is undecidable."*
>
> Every step of the construction is correct. What is wrong with the proof? Fix it.
>
> *Source: original.*

> [!hint]- Hint
> Which language does the student's argument assume can be decided, and which one does it then decide? Compare with the boxed rule in [[1-models-of-computation/07-undecidability#79-the-halting-problem-via-reduction|§7.9]].

> [!solution]- Solution
> **The slip: the reduction goes in the wrong direction.** The student decides $\textsf{EvenAccept}$ *using* a decider for $\textsf{Accept}$ — a reduction from $\textsf{EvenAccept}$ to $\textsf{Accept}$. That proves only "if $\textsf{Accept}$ were decidable, $\textsf{EvenAccept}$ would be decidable too", which says nothing, because $\textsf{Accept}$ is not decidable. The same kind of argument "reduces" decidable languages to $\textsf{Accept}$ — for example $\{\langle M\rangle \mid M \text{ has three states}\}$ — so it cannot prove undecidability.
>
> **The fix: reduce $\textsf{Accept}$ to $\textsf{EvenAccept}$.** Suppose for the sake of argument that $\textsf{DecideEven}$ decides $\textsf{EvenAccept}$. Build $\textsf{DecideAccept}$: given $\langle M, w\rangle$, write the encoding of the machine
> $$
> M_w(x)\colon\ \text{ignore } x;\ \text{run } M \text{ on } w;\ \text{accept if } M \text{ accepts},
> $$
> then run $\textsf{DecideEven}$ on $\langle M_w\rangle$ and return its answer.
> - If $M$ accepts $w$, then $M_w$ accepts every string, in particular $\varepsilon$, which has even length; so $\langle M_w\rangle\in\textsf{EvenAccept}$, $\textsf{DecideEven}$ accepts, and $\textsf{DecideAccept}$ accepts.
> - If $M$ does not accept $w$ (it rejects or runs forever), then $M_w$ accepts no string at all; so $\langle M_w\rangle\notin\textsf{EvenAccept}$, $\textsf{DecideEven}$ rejects, and $\textsf{DecideAccept}$ rejects.
>
> So $\textsf{DecideAccept}$ decides $\textsf{Accept}$, which is impossible; hence $\textsf{DecideEven}$ does not exist. (Rice's theorem gives the same in one line: $\mathcal{L} = \{L \mid L \text{ contains a string of even length}\}$, $Y = M_{\textsf{Accept}}$, $N = M_{\textsf{Reject}}$.)
>
> **What the student did prove.** Running the universal machine on $\langle M', \varepsilon\rangle$ *accepts* $\textsf{EvenAccept}$. So $\textsf{EvenAccept}$ is acceptable — and, by the fix, undecidable.
>
> **Answer.** The reduction goes from $\textsf{EvenAccept}$ to $\textsf{Accept}$, which proves nothing; reduce $\textsf{Accept}$ to $\textsf{EvenAccept}$ instead, with $M_w$ ("ignore the input, run $M$ on $w$").

## Medium

### 7.4 Rice with the right variant

> [!medium] Medium · Rice's theorem
> Prove that each language is undecidable, using Rice's theorem or one of its variants for rejection, halting, divergence or deciding ([[1-models-of-computation/07-undecidability#711-rices-theorem|§7.11]]). For each, write the language as $\textsf{AcceptIn}(\mathcal{L})$, $\textsf{RejectIn}(\mathcal{L})$, $\textsf{HaltIn}(\mathcal{L})$, … with an explicit property $\mathcal{L}$, and give concrete machines $Y$ and $N$. Machines have input alphabet $\{\mathtt{0},\mathtt{1}\}$.
>
> (a) $\textsf{RevClosed} := \{\langle M\rangle \mid \text{for every string } w, \text{ if } M \text{ accepts } w \text{ then } M \text{ accepts } w^R\}$.
>
> (b) $\textsf{RejectOne} := \{\langle M\rangle \mid M \text{ rejects exactly one string}\}$.
>
> (c) $\textsf{AcceptEqualsReject} := \{\langle M\rangle \mid \textsf{Accept}(M) = \textsf{Reject}(M)\}$.
>
> *Source: original.*

> [!hint]- Hint
> (a) needs a machine whose language contains some string but not its reversal. In (b), whether $\langle M\rangle$ belongs depends on $\textsf{Reject}(M)$: two machines with the same $\textsf{Accept}(M)$ can disagree. In (c), what is $\textsf{Accept}(M)\cap\textsf{Reject}(M)$?

> [!solution]- Solution
> **Idea.** Rice's theorem applies to a property of *one* of the four languages of a machine. First find which one decides membership, then exhibit one machine whose language has the property and one whose language does not.
>
> **(a) Rice's theorem.** $\textsf{RevClosed} = \textsf{AcceptIn}(\mathcal{L}_a)$ with $\mathcal{L}_a = \{L \mid w^R\in L \text{ for every } w\in L\}$: membership depends only on $\textsf{Accept}(M)$.
> - $Y = M_{\textsf{Accept}}$: $\textsf{Accept}(Y) = \Sigma^*$ contains every reversal, so it is in $\mathcal{L}_a$.
> - $N$ accepts exactly $\{\mathtt{01}\}$: $\delta(\textit{start},\mathtt{0}) = (\mathit{saw0},\mathtt{0},+1)$, $\delta(\mathit{saw0},\mathtt{1}) = (\mathit{saw01},\mathtt{1},+1)$, $\delta(\mathit{saw01},\square) = (\textit{accept},\square,+1)$, all other transitions reject. $\mathtt{01}\in\textsf{Accept}(N)$ but $\mathtt{10}\notin\textsf{Accept}(N)$, so $\textsf{Accept}(N)\notin\mathcal{L}_a$.
>
> By Rice's theorem, $\textsf{RevClosed}$ is undecidable.
>
> **(b) Rice's rejection theorem.** $\textsf{RejectOne} = \textsf{RejectIn}(\mathcal{L}_b)$ with $\mathcal{L}_b = \{L \mid L \text{ has exactly one element}\}$.
> - $Y$: $\delta(\textit{start},\square) = (\textit{reject},\square,+1)$ and $\delta(\textit{start},a) = (\textit{accept},a,+1)$ for $a\in\{\mathtt{0},\mathtt{1}\}$. It rejects $\varepsilon$ and accepts everything else: $\textsf{Reject}(Y) = \{\varepsilon\}\in\mathcal{L}_b$.
> - $N = M_{\textsf{Accept}}$: $\textsf{Reject}(N) = \varnothing$, which has no element, so it is not in $\mathcal{L}_b$.
>
> By Rice's rejection theorem, $\textsf{RejectOne}$ is undecidable. The plain (accepting) version does not fit: change $Y$ to move right forever on $\square$ instead of rejecting. The new machine accepts the same strings as $Y$, but rejects none, so it is not in $\textsf{RejectOne}$ — membership is not determined by $\textsf{Accept}(M)$.
>
> **(c) Rice's halting theorem.** No machine both accepts and rejects the same string, so $\textsf{Accept}(M)\cap\textsf{Reject}(M) = \varnothing$, and the two sets can be equal only if both are empty — that is, if $M$ halts on no input. So $\textsf{AcceptEqualsReject} = \textsf{HaltIn}(\{\varnothing\})$.
> - $Y = M_{\textsf{Diverge}}$: $\textsf{Halt}(Y) = \varnothing$.
> - $N = M_{\textsf{Accept}}$: $\textsf{Halt}(N) = \Sigma^*\ne\varnothing$.
>
> By Rice's halting theorem, $\textsf{AcceptEqualsReject}$ is undecidable.
>
> **Check.** $N$ on `01` goes $\textit{start}\to\mathit{saw0}\to\mathit{saw01}$ and accepts at the blank; on `10`, $\textit{start}$ reads `1` and has no transition, so it rejects; on `011`, $\mathit{saw01}$ reads `1` and rejects. $Y$ in (b) reads $\square$ at once on $\varepsilon$ and rejects, and accepts every other input in one step. In (c), $M_{\textsf{Diverge}}$ accepts and rejects nothing ($\varnothing = \varnothing$), while $M_{\textsf{Accept}}$ accepts $\Sigma^*\ne\varnothing$.
>
> **Watch out:** the rubric gives 2 of the 10 points for the details, including the *right variant*. Citing the plain theorem in (b) or (c) — and describing $Y$ and $N$ by the strings they accept — proves nothing there, because membership is not decided by $\textsf{Accept}(M)$.
>
> **Answer.** (a) $\textsf{AcceptIn}(\mathcal{L}_a)$, $Y = M_{\textsf{Accept}}$, $N$ accepts exactly $\{\mathtt{01}\}$. (b) $\textsf{RejectIn}(\{L : \lvert L\rvert = 1\})$, $Y$ rejects exactly $\varepsilon$, $N = M_{\textsf{Accept}}$. (c) $\textsf{HaltIn}(\{\varnothing\})$, $Y = M_{\textsf{Diverge}}$, $N = M_{\textsf{Accept}}$.

### 7.5 Two behaviors, two answers

> [!medium] Medium · TM behavior · reductions
> Decide whether each language is decidable, and prove your answer. Machines have input alphabet $\{\mathtt{0},\mathtt{1}\}$ and any finite tape alphabet; $\mathtt{\#}$ is a fixed symbol that may or may not belong to a machine's tape alphabet.
>
> (a) $\textsf{Reach374} := \{\langle M, w\rangle \mid M, \text{ run on input } w, \text{ at some time has its head on cell } 374\}$.
>
> (b) $\textsf{WritesHash} := \{\langle M, w\rangle \mid M, \text{ run on input } w, \text{ writes the symbol } \mathtt{\#} \text{ in some step}\}$.
>
> Why does Rice's theorem settle neither question?
>
> *Source: original.*

> [!hint]- Hint
> (a) A run that never reaches cell 374 lives inside a box of 374 cells. How many different configurations fit in that box? (b) Modify $M$ so that it writes $\mathtt{\#}$ exactly when it is about to accept — and think about what happens if $M$'s step into $\textit{accept}$ moves left from cell 0.

> [!solution]- Solution
> **Idea.** A behavior that confines the machine to finitely many configurations is decidable by bounded simulation; a behavior that a simulation can avoid, and then perform on purpose, is undecidable by reduction ([[1-models-of-computation/07-undecidability#713-turing-machine-behavior-its-complicated|§7.13]]).
>
> **(a) Decidable.** Let $Q$ and $\Gamma$ be $M$'s states and tape alphabet. As long as the head stays among cells $0,\dots,373$, the cells from 374 on are never read or written, so they keep their initial contents, and the configuration is determined by the state, the head position, and the contents of cells $0,\dots,373$: at most
> $$
> N := \lvert Q\rvert\cdot374\cdot\lvert\Gamma\rvert^{374}
> $$
> possibilities. The decider simulates $M$ on $w$ for up to $N$ steps. It **accepts** as soon as the head is on cell 374, and **rejects** if $M$ halts or crashes first. If $N$ steps pass with neither, it **rejects**: two of the $N+1$ configurations seen so far are equal (pigeonhole), and since $M$ is deterministic, the run cycles through the same configurations forever and never reaches cell 374. The decider halts after at most $N$ simulated steps and is right in all three cases.
>
> **(b) Undecidable,** by a reduction from $\textsf{Accept}$. Suppose for the sake of argument that $\textsf{DecideHash}$ decides $\textsf{WritesHash}$. Build $\textsf{DecideAccept}$: given $\langle M, w\rangle$, it modifies $M$'s transition table into a machine $M'$:
> 1. if $\mathtt{\#}$ is in $M$'s tape alphabet, rename it to a new symbol everywhere in the table;
> 2. add a new state $\mathit{fin}$, and redirect every transition into $\textit{accept}$ to $\mathit{fin}$ instead (same symbol written, same move);
> 3. for every tape symbol $c$, let $\delta'(\mathit{fin}, c) = (\textit{accept}, \mathtt{\#}, +1)$.
>
> Then it runs $\textsf{DecideHash}$ on $\langle M', w\rangle$ and returns its answer. Editing a finite table always terminates, and $\textsf{DecideHash}$ halts, so $\textsf{DecideAccept}$ halts on every input.
> - Suppose $M$ accepts $w$. $M'$ makes exactly the same steps as $M$ until $M$ would enter $\textit{accept}$; it enters $\mathit{fin}$ instead and then writes $\mathtt{\#}$. So $\langle M',w\rangle\in\textsf{WritesHash}$, $\textsf{DecideHash}$ accepts, and $\textsf{DecideAccept}$ accepts.
> - Suppose $M$ does not accept $w$: it rejects, crashes or runs forever. $M'$ does the same and never enters $\mathit{fin}$, and step 1 guarantees that it writes no $\mathtt{\#}$ along the way. So $\langle M',w\rangle\notin\textsf{WritesHash}$, $\textsf{DecideHash}$ rejects, and $\textsf{DecideAccept}$ rejects.
>
> So $\textsf{DecideAccept}$ decides $\textsf{Accept}$, which is impossible; $\textsf{WritesHash}$ is undecidable. (It is acceptable: simulate and wait for a $\mathtt{\#}$.)
>
> **Rice does not apply** to either language, because both are about behavior, not about $\textsf{Accept}(M)$. $M_{\textsf{Accept}}$ accepts every input after one step, never reaching cell 374 and never writing $\mathtt{\#}$; a machine that first walks 374 cells to the right, writing $\mathtt{\#}$ as it goes, and then accepts, has the same language and belongs to both.
>
> **Check.** Try the decider of (a) on three machines. $M_{\textsf{Accept}}$ moves to cell 1 and accepts: reject. A machine that moves right forever in one state is on cell 374 after 374 steps: accept. A machine that, on the empty input, steps right onto a blank and back left forever repeats its first configuration after two steps: reject, since it will never get further. In (b), if $M$ accepts $w$ after $t$ steps, $M'$ writes $\mathtt{\#}$ in step $t+1$; if $M$ rejects $w$ after $t$ steps, so does $M'$, without writing $\mathtt{\#}$.
>
> **Watch out:** it is tempting to write $\mathtt{\#}$ in the step into $\textit{accept}$ itself. If that step moves left from cell 0, $M$ crashes instead of accepting — yet the $\mathtt{\#}$ has been written. The extra state $\mathit{fin}$, which always moves right, avoids this (the same trick is behind Theorem 20).
>
> **Answer.** (a) Decidable: simulate $\lvert Q\rvert\cdot374\cdot\lvert\Gamma\rvert^{374}$ steps; a run that has not reached cell 374 by then has repeated a configuration and never will. (b) Undecidable: from $M$ build $M'$ that writes $\mathtt{\#}$ (in one extra step) exactly when $M$ accepts $w$. Rice's theorem is about $\textsf{Accept}(M)$, and these are properties of the run.

### 7.6 Do two machines share a string

> [!medium] Medium · acceptable vs decidable · reductions
> Let $\textsf{Overlap} := \{\langle M_1\rangle\langle M_2\rangle \mid \textsf{Accept}(M_1)\cap\textsf{Accept}(M_2)\ne\varnothing\}$: some string is accepted by both machines.
>
> (a) Show that $\textsf{Overlap}$ is acceptable: describe an acceptor, and explain why "for each string $x$ in turn, run $M_1$ on $x$ and then $M_2$ on $x$" does not work.
>
> (b) Show that $\textsf{Overlap}$ is undecidable.
>
> (c) Is $\textsf{Disjoint} := \{\langle M_1\rangle\langle M_2\rangle \mid \textsf{Accept}(M_1)\cap\textsf{Accept}(M_2) = \varnothing\}$ acceptable? Is it decidable?
>
> *Source: original.*

> [!hint]- Hint
> (a) Interleave both the strings and the step counts. (b) Fix one of the two machines so that $\textsf{Overlap}$ turns into a language you already know. (c) Lemma 5.

> [!solution]- Solution
> **Idea.** A yes-instance has a finite certificate — a string $x$ and two accepting runs — so a patient search finds it; that makes $\textsf{Overlap}$ acceptable. Fixing $M_2 = M_{\textsf{Accept}}$ turns it into "$M_1$ accepts something", which is undecidable, and then Lemma 5 rules out the complement.
>
> **(a) An acceptor (dovetailing).** On input $\langle M_1\rangle\langle M_2\rangle$ (reject anything else): for $t = 1, 2, 3, \dots$, for each of the first $t$ strings $x$ of $\Sigma^*$, run $M_1$ on $x$ for $t$ steps and $M_2$ on $x$ for $t$ steps; if both accept, accept. If the $i$th string is accepted by $M_1$ within $s_1$ steps and by $M_2$ within $s_2$ steps, the acceptor accepts by round $\max(i, s_1, s_2)$. If no string is accepted by both, it runs forever — which an acceptor may do. So it accepts exactly $\textsf{Overlap}$.
>
> The serial search gets stuck on the first string on which $M_1$ or $M_2$ runs forever. Let $M_1$ accept `0`, reject `1`, and run forever on $\varepsilon$, and let $M_2 = M_{\textsf{Accept}}$. The pair is in $\textsf{Overlap}$, because both machines accept `0`, but the serial search runs $M_1$ on $\varepsilon$ forever and never gets to `0`. Dovetailing accepts in round 2.
>
> **(b) Undecidable,** by a reduction from $\textsf{NeverAccept}$ (Theorem 13). Suppose for the sake of argument that $\textsf{DecideOverlap}$ decides $\textsf{Overlap}$. Build $\textsf{DecideNA}$: given a string, reject it if it is not an encoding $\langle M\rangle$; otherwise run $\textsf{DecideOverlap}$ on $\langle M\rangle\langle M_{\textsf{Accept}}\rangle$ and return the **opposite** answer. Since $\textsf{Accept}(M)\cap\Sigma^* = \textsf{Accept}(M)$:
> - If $\textsf{Accept}(M) = \varnothing$, the intersection is empty, $\textsf{DecideOverlap}$ rejects, and $\textsf{DecideNA}$ accepts $\langle M\rangle$.
> - If $M$ accepts some string $x$, then $M_{\textsf{Accept}}$ accepts $x$ too, $\textsf{DecideOverlap}$ accepts, and $\textsf{DecideNA}$ rejects $\langle M\rangle$.
>
> So $\textsf{DecideNA}$ decides $\textsf{NeverAccept}$, which is impossible; $\textsf{Overlap}$ is undecidable.
>
> **(c) Not acceptable, so not decidable.** The complement of $\textsf{Overlap}$ is $\textsf{Disjoint}$ together with the strings that do not have the form $\langle M_1\rangle\langle M_2\rangle$, which form a decidable set. If $\textsf{Disjoint}$ were acceptable, then so would be this union (Lemma 4), so both $\textsf{Overlap}$ (by (a)) and its complement would be acceptable, and Lemma 5 would make $\textsf{Overlap}$ decidable — contradicting (b).
>
> **Check.** On the pair in (a), round 1 runs both machines on $\varepsilon$ for one step ($M_1$ is still running); round 2 runs them on $\varepsilon$ and `0` for two steps each, and both accept `0` in their first step: accept. The serial search, in contrast, never gets past $\varepsilon$.
>
> **Answer.** (a) Dovetail over strings and step counts; the serial search hangs on a string where $M_1$ or $M_2$ runs forever. (b) Undecidable: $\langle M\rangle\langle M_{\textsf{Accept}}\rangle\in\textsf{Overlap}$ exactly when $\textsf{Accept}(M)\ne\varnothing$. (c) $\textsf{Disjoint}$ is not acceptable (Lemma 5), hence not decidable.

## Hard

### 7.7 Accepts epsilon, rejects itself

> [!hard] Hard · diagonalization · acceptable vs decidable
> Let $\textsf{EpsSelfReject} := \{\langle M\rangle \mid M \text{ accepts } \varepsilon \text{ and } M \text{ rejects } \langle M\rangle\}$.
>
> (a) Prove that $\textsf{EpsSelfReject}$ is undecidable **by diagonalization** (not by a reduction).
>
> (b) Prove that $\textsf{EpsSelfReject}$ is acceptable.
>
> (c) Is the complement of $\textsf{EpsSelfReject}$ acceptable?
>
> (d) Explain why Rice's theorem cannot be used here: give two machines that accept the same language, exactly one of them in $\textsf{EpsSelfReject}$, and two machines that reject the same language, exactly one of them in $\textsf{EpsSelfReject}$.
>
> *Source: original.*

> [!hint]- Hint
> Build the wrapper so that it certainly accepts $\varepsilon$. On encodings, should it copy the decider's answer or flip it? Try both on the wrapper's own encoding, and keep the one that gives a contradiction in *both* cases.

> [!solution]- Solution
> **Idea.** Run a wrapper built from the hypothetical decider on its own encoding. The wrapper must make the side condition "accepts $\varepsilon$" true for itself, and on encodings it must **copy** the decider's answer — the language is about *rejecting*, as in Theorem 6.
>
> **(a)** Suppose for the sake of argument that some Turing machine $\textsf{Dec}$ decides $\textsf{EpsSelfReject}$. Build the machine $\textsf{Wrap}$: on input $x$,
> - if $x = \varepsilon$, accept;
> - if $x = \langle M\rangle$ for some machine $M$, run $\textsf{Dec}$ on $x$ and return its answer (accept if $\textsf{Dec}$ accepts, reject if $\textsf{Dec}$ rejects);
> - otherwise reject.
>
> $\textsf{Wrap}$ halts on every input, because $\textsf{Dec}$ does, and it accepts $\varepsilon$. So $\langle\textsf{Wrap}\rangle\in\textsf{EpsSelfReject}$ if and only if $\textsf{Wrap}$ rejects $\langle\textsf{Wrap}\rangle$. Run $\textsf{Dec}$ on $\langle\textsf{Wrap}\rangle$; it halts, so there are two cases.
> - If $\textsf{Dec}$ accepts $\langle\textsf{Wrap}\rangle$, then $\textsf{Wrap}$ accepts $\langle\textsf{Wrap}\rangle$, so $\textsf{Wrap}$ does not reject $\langle\textsf{Wrap}\rangle$, so $\langle\textsf{Wrap}\rangle\notin\textsf{EpsSelfReject}$ — yet $\textsf{Dec}$ accepted it. Contradiction.
> - If $\textsf{Dec}$ rejects $\langle\textsf{Wrap}\rangle$, then $\textsf{Wrap}$ rejects $\langle\textsf{Wrap}\rangle$, and it accepts $\varepsilon$, so $\langle\textsf{Wrap}\rangle\in\textsf{EpsSelfReject}$ — yet $\textsf{Dec}$ rejected it. Contradiction.
>
> Both cases are impossible, so $\textsf{Dec}$ does not exist: $\textsf{EpsSelfReject}$ is undecidable. $\blacksquare$
>
> **(b)** $\textsf{EpsSelfReject} = \textsf{AccEps}\cap\textsf{SelfReject}$, where $\textsf{AccEps} := \{\langle M\rangle \mid M \text{ accepts } \varepsilon\}$. $\textsf{AccEps}$ is acceptable (on $\langle M\rangle$, run $M$ on $\varepsilon$ with the universal machine), $\textsf{SelfReject}$ is acceptable (Theorem 11), and the intersection of two acceptable languages is acceptable (Lemma 4). Concretely: reject non-encodings; run $M$ on $\varepsilon$; if it accepts, run $M$ on $\langle M\rangle$ and accept if that run rejects. If $M$ runs forever on $\varepsilon$, so does this acceptor — which is fine, since then $\langle M\rangle\notin\textsf{EpsSelfReject}$.
>
> **(c) No.** $\textsf{EpsSelfReject}$ is acceptable by (b) and undecidable by (a), so by Lemma 5 its complement is not acceptable.
>
> **(d)** Let $M_1$ accept if its input is empty and reject otherwise, and $M_2$ accept if its input is empty and run forever otherwise. Both accept exactly $\{\varepsilon\}$. But $M_1$ rejects every non-empty string — its own encoding included — so $\langle M_1\rangle\in\textsf{EpsSelfReject}$, while $M_2$ rejects nothing, so $\langle M_2\rangle\notin\textsf{EpsSelfReject}$. Next, let $M_3$ run forever if its input is empty and reject otherwise: it rejects the same strings as $M_1$, but it does not accept $\varepsilon$, so $\langle M_3\rangle\notin\textsf{EpsSelfReject}$. Membership is decided neither by $\textsf{Accept}(M)$ nor by $\textsf{Reject}(M)$, so neither Rice's theorem nor its rejection version applies. (The pair $M_1$, $M_{\textsf{Accept}}$ — both halt on every input, but $M_{\textsf{Accept}}$ rejects nothing — rules out the halting and divergence versions too.)
>
> **Watch out:**
> - **Flipping is the wrong reflex here.** If $\textsf{Wrap}$ returned the *opposite* of $\textsf{Dec}$'s answer, both cases would be consistent: $\textsf{Dec}$ accepts $\langle\textsf{Wrap}\rangle$, so $\textsf{Wrap}$ rejects it and $\langle\textsf{Wrap}\rangle\in\textsf{EpsSelfReject}$ — no contradiction; similarly for rejection. Work out both cases before committing to a wrapper.
> - **Forgetting the $\varepsilon$ clause** breaks the proof too: a wrapper that does not accept $\varepsilon$ is never in the language, so "$\textsf{Dec}$ rejects $\langle\textsf{Wrap}\rangle$" is perfectly consistent.
> - Say why the run of $\textsf{Dec}$ on $\langle\textsf{Wrap}\rangle$ halts; otherwise there is a third case.
>
> **Grading.** Out of 10: 4 for the wrapper (built from $\textsf{Dec}$, with its behavior on $\varepsilon$ and on encodings stated) and 6 for the contradiction, 3 for each case.
>
> **Answer.** (a) $\textsf{Wrap}$ accepts $\varepsilon$ and copies $\textsf{Dec}$'s answer on encodings; on $\langle\textsf{Wrap}\rangle$ both answers of $\textsf{Dec}$ are wrong. (b) $\textsf{AccEps}\cap\textsf{SelfReject}$ is acceptable by Lemma 4. (c) No, by Lemma 5. (d) $M_1$ and $M_2$ accept $\{\varepsilon\}$, but only $M_1$ is in the language; $M_1$ and $M_3$ reject every non-empty string, but only $M_1$ is in the language.

### 7.8 Both languages infinite

> [!hard] Hard · reductions · Rice's theorem
> Let $\textsf{BothInfinite} := \{\langle M\rangle \mid \textsf{Accept}(M) \text{ and } \textsf{Reject}(M) \text{ are both infinite}\}$, for machines with input alphabet $\{\mathtt{0},\mathtt{1}\}$.
>
> (a) Show that neither Rice's theorem nor Rice's rejection theorem applies directly: give two machines that accept the same language, exactly one of them in $\textsf{BothInfinite}$, and two machines that reject the same language, exactly one of them in $\textsf{BothInfinite}$.
>
> (b) Prove that $\textsf{BothInfinite}$ is undecidable by a reduction, written out in full with both directions.
>
> *Source: original.*

> [!hint]- Hint
> (a) Accept the strings of even length; decide what happens to the odd ones. (b) Build $M'$ that first runs $M$ on $w$ and then, only if $M$ accepted, behaves like your machine from (a) that is in $\textsf{BothInfinite}$.

> [!solution]- Solution
> **Idea.** Membership depends on $\textsf{Accept}(M)$ and $\textsf{Reject}(M)$ *together*, so no single-language version of Rice fits; but the reduction behind Rice still works, with a target machine that both accepts and rejects infinitely many strings.
>
> **(a)** Three parity machines, with start state $\mathit{even}$: on `0` or `1`, $\mathit{even}$ and $\mathit{odd}$ swap and move right; on the blank they do this:
>
> | machine | $\mathit{even}$ reads $\square$ | $\mathit{odd}$ reads $\square$ | $\textsf{Accept}$ | $\textsf{Reject}$ | in $\textsf{BothInfinite}$? |
> |---|---|---|---|---|---|
> | $P$ | accept | reject | even-length strings | odd-length strings | yes |
> | $P'$ | accept | move right, stay in $\mathit{odd}$ | even-length strings | $\varnothing$ | no |
> | $P''$ | move right, stay in $\mathit{even}$ | reject | $\varnothing$ | odd-length strings | no |
>
> ($P'$ runs forever on odd-length inputs, walking right over blanks; $P''$ does the same on even-length ones.) $\textsf{Accept}(P) = \textsf{Accept}(P')$ but only $P$ is in $\textsf{BothInfinite}$, so it is not $\textsf{AcceptIn}(\mathcal{L})$ for any $\mathcal{L}$; $\textsf{Reject}(P) = \textsf{Reject}(P'')$ but only $P$ is in it, so it is not $\textsf{RejectIn}(\mathcal{L})$ either.
>
> **(b)** Suppose for the sake of argument that some Turing machine $\textsf{DecideBI}$ decides $\textsf{BothInfinite}$. Consider the machine $\textsf{DecideAccept}$ that, given $\langle M, w\rangle$, writes the encoding $\langle M'\rangle$ of the machine
> $$
> M'(x)\colon\ \text{run } M \text{ on } w;\ \text{if } M \text{ accepts } w\text{: accept } x \text{ if } \lvert x\rvert \text{ is even, reject } x \text{ if } \lvert x\rvert \text{ is odd}
> $$
> (if $M$ rejects $w$, $M'$ runs forever; if $M$ runs forever or crashes on $w$, so does $M'$), and then runs $\textsf{DecideBI}$ on $\langle M'\rangle$ and returns its answer. Writing $\langle M'\rangle$ always terminates and $\textsf{DecideBI}$ always halts, so $\textsf{DecideAccept}$ halts on every input.
> - **Suppose $M$ accepts $w$.** Then on every input $x$, $M'$ finishes running $M$ on $w$ and accepts $x$ if $\lvert x\rvert$ is even and rejects it if $\lvert x\rvert$ is odd. So $\textsf{Accept}(M')$ is the set of even-length strings and $\textsf{Reject}(M')$ the set of odd-length strings, both infinite: $\langle M'\rangle\in\textsf{BothInfinite}$. So $\textsf{DecideBI}$ accepts $\langle M'\rangle$, and $\textsf{DecideAccept}$ accepts $\langle M, w\rangle$.
> - **Suppose $M$ does not accept $w$.** If $M$ rejects $w$, then $M'$ runs forever on every input by construction; if $M$ runs forever on $w$, then $M'$ never finishes its first phase. Either way $M'$ halts on no input, so $\textsf{Accept}(M') = \textsf{Reject}(M') = \varnothing$: $\langle M'\rangle\notin\textsf{BothInfinite}$. So $\textsf{DecideBI}$ rejects $\langle M'\rangle$, and $\textsf{DecideAccept}$ rejects $\langle M, w\rangle$.
>
> In both cases $\textsf{DecideAccept}$ is correct, so it decides $\textsf{Accept}$ — which is impossible. Hence $\textsf{DecideBI}$ does not exist, and $\textsf{BothInfinite}$ is undecidable. $\blacksquare$
>
> **Check.** $P$ is what $M'$ turns into when $M$ accepts $w$. On `01` it goes $\mathit{even}\to\mathit{odd}\to\mathit{even}$ and accepts at the blank; on `0`, $\mathit{odd}$ reads the blank and rejects; on $\varepsilon$ it accepts at once. $P'$ on `0` walks right over blanks in state $\mathit{odd}$ forever.
>
> **Watch out:** the clause "if $M$ rejects $w$, $M'$ runs forever" matters. If $M'$ went on to the parity phase whenever $M$ *halts* on $w$, then a rejection of $w$ would put $\langle M'\rangle$ in $\textsf{BothInfinite}$, and the second direction would fail. That version is a correct reduction from $\textsf{Halt}$ instead; what breaks the proof is mixing the two.
>
> **Grading.** Out of 10: 4 for the reduction ($\textsf{DecideAccept}$ and $M'$ described, in the right direction), 3 for "$M$ accepts $w$ ⇒ accept", 3 for "$M$ rejects or diverges ⇒ reject".
>
> **Answer.** (a) $P$ (accept even, reject odd) and $P'$ (accept even, run forever on odd) accept the same language; $P$ and $P''$ (reject odd, run forever on even) reject the same language; only $P$ is in $\textsf{BothInfinite}$. (b) Reduce $\textsf{Accept}$: $M'$ runs $M$ on $w$ and, if $M$ accepts, accepts even-length and rejects odd-length inputs.

### Sources for this page
All eight problems are original, written in the formats of the course's true-or-false and undecidability problems; none is taken from a course exam or homework. They use the results of the book's Chapter 7: the closure lemmas and Lemma 5 (§7.3), diagonalization (§§7.5–7.7), the halting problem and reductions (§§7.9–7.10), Rice's theorem with its rejection and halting variants (§7.11), Corollary 18 (§7.12), and the two principles of §7.13 — bounded simulation, as in Theorem 19, and the extra-steps construction behind Theorem 20. The grading notes paraphrase the course's undecidability rubrics. Undecidability itself cannot be tested by a program, but everything concrete around the proofs is checked by `tools/practice/checks/ch07.py`: every witness machine on all short inputs, the bounded-simulation decider of 7.5(a) against long simulations of 400 random machines, the construction of 7.5(b) on 400 random machines, the dovetailing acceptor of 7.6 against the serial search on 300 random pairs, the case analysis of the diagonal argument in 7.7 (including the failure of the flipping wrapper), and the parity machines of 7.8.

*Previous: [[practice/06-turing-machines|Chapter 6 practice]] · [[practice/index|all practice]]*
