---
title: "Practice — Chapter 6: Turing machines"
description: "6 practice problems (3 easy, 2 medium, 1 hard) on Turing machines: true or false on deciding, crashing and the equivalent variants, tracing configurations to the four possible outcomes, a would-be decider that only accepts, designing a decider for palindromes and a linear-time two-tape decider for 0^n1^n0^n, and a machine that computes w ↦ ww, each with a folded hint and a worked solution."
tags: [practice, turing-machines]
chapter: 6
---

*Practice for [[1-models-of-computation/06-turing-machines|Chapter 6]] · concepts: [[concepts/turing-machines]] · [[concepts/acceptable-and-decidable]] · all practice: [[practice/index|hub]] · by difficulty: [[practice/easy|easy]] · [[practice/medium|medium]] · [[practice/hard|hard]] · [[practice/topics|by topic]]*

Work each problem on paper first. Open the **hint** only when stuck, and the **solution** only after you have an answer you would hand in. Every Turing machine in the solutions has been checked by a script. Machines follow [[1-models-of-computation/06-turing-machines#62-formal-definitions|§6.2]] unless a problem says otherwise: one tape, infinite to the right; every step moves the head one cell left ($-1$) or right ($+1$); a move left from cell 0 **crashes**; and missing transitions go to $\textit{reject}$. A table entry $(q, b, \Delta)$ in row $p$ and column $a$ means $\delta(p,a) = (q,b,\Delta)$.

## Easy

### 6.1 Deciding, crashing and variants

> [!easy] Easy · true or false · TM variants
> Answer each statement **Yes** (always true) or **No**, with a one-sentence reason; for a No, give a counterexample. "Standard" means the model of §6.2.
>
> (a) A Turing machine that never moves its head to the left can accept a language that is not regular.
>
> (b) If a Turing machine $M$ halts on every input and accepts every string in $L$, then $M$ decides $L$.
>
> (c) If a Turing machine $M$ crashes on at least one input, then $M$ decides no language at all.
>
> (d) Every Turing machine that may also stay put ($\Delta = 0$) can be simulated by a standard Turing machine that takes at most twice as many steps.
>
> (e) Every Turing machine whose tape is infinite in both directions can be simulated by a standard Turing machine with only a constant-factor slowdown.
>
> (f) If a two-tape Turing machine decides $L$ in $O(n)$ time, then some standard Turing machine decides $L$ in $O(n)$ time.
>
> *Source: original.*

> [!hint]- Hint
> For (a): can the machine ever look again at a cell it has left? For (b) and (c), go back to the exact definitions of *accepts $L$* and *decides $L$*. For (f), §6.6 names a language with a quadratic gap.

> [!solution]- Solution
> **(a) No.** Such a machine reads each input symbol exactly once, left to right, and after the input it reads only blanks, so its state at the end of the input determines everything that follows: it is a DFA in disguise, and $\textsf{Accept}(M)$ is regular. (Concretely: a DFA with states $Q\cup\{\textit{ACC},\textit{REJ}\}$ follows $M$'s state symbol by symbol, and accepts in $\textit{ACC}$ and in every state from which $M$'s walk over blanks reaches $\textit{accept}$ — a walk that depends on the state alone.)
>
> **(b) No.** "Accepts every string in $L$" still allows accepting more. The machine $M_{\textsf{Accept}}$ that accepts at once halts on every input and accepts every string in $L = \{\varepsilon\}$, but it also accepts `0`; it decides $\Sigma^*$, not $\{\varepsilon\}$. With "$\textsf{Accept}(M) = L$" instead, the statement would be true.
>
> **(c) Yes.** A decider must accept or reject every input, and on an input where $M$ crashes it does neither: a crash is not a rejection.
>
> **(d) Yes.** The construction of [[1-models-of-computation/06-turing-machines#64-variations|§6.4]] with states $Q\times\{0,1\}$ replaces each stay-put step by a step right and a step back, and every other step by one step, so $t$ steps become at most $2t$.
>
> **(e) Yes.** Fold the tape at cell 0 onto two tracks — the upper track of cell $i\ge0$ holds cell $i$, the lower track holds cell $-i-1$ — mark cell 0, and keep the current track in the state; each simulated step costs one step, or two when the head crosses between cells $0$ and $-1$ (plus two steps at the start to mark cell 0).
>
> **(f) No.** The marked palindromes $\{w\,\mathtt{\#}\,w^R \mid w\in\{\mathtt{0},\mathtt{1}\}^*\}$: two tapes decide them in $O(n)$ steps — copy $w$ onto tape 2, then compare it backwards with the part after the $\mathtt{\#}$ — but every standard one-tape machine needs $\Omega(n^2)$ time ([[1-models-of-computation/06-turing-machines#66-tracks-heads-and-tapes|§6.6]]). What is true is the simulation bound: one tape can always do it in $O(n^2)$ steps.
>
> **Watch out:** (b) and (c) are pure definitions, and that is where exam points go. *$M$ accepts $L$* means $M$ accepts exactly the strings of $L$; *$M$ decides $L$* means, in addition, that $M$ halts — accepts or rejects, never crashes or runs forever — on every input.
>
> **Answer.** (a) No (b) No (c) Yes (d) Yes (e) Yes (f) No.

### 6.2 Four ways a run ends

> [!easy] Easy · TM simulation
> The machine $M$ below has input alphabet $\{\mathtt{0},\mathtt{1}\}$, tape alphabet $\{\mathtt{0},\mathtt{1},\square\}$ and states $\textit{start}$, $\mathit{look}$, $\textit{accept}$, $\textit{reject}$; the blank entry is a missing transition.
>
> | | $\mathtt{0}$ | $\mathtt{1}$ | $\square$ |
> |---|---|---|---|
> | $\textit{start}$ | $(\mathit{look},\mathtt{1},+1)$ | $(\mathit{look},\mathtt{1},-1)$ | |
> | $\mathit{look}$ | $(\mathit{look},\mathtt{0},-1)$ | $(\textit{start},\mathtt{1},+1)$ | $(\textit{accept},\mathtt{1},-1)$ |
>
> (a) Write the run of $M$ on input `000` as a sequence of configurations $(q, x, i)$, and say how it ends.
>
> (b) On each of the inputs $\varepsilon$, `1`, `01` and `011`, does $M$ accept, reject, crash, or run forever? Justify each answer.
>
> (c) Does $M$ decide any language?
>
> *Source: original.*

> [!hint]- Hint
> A configuration $(q,x,i)$ lists the state, the tape without trailing blanks, and the head position. On `011`, write configurations until one of them comes back.

> [!solution]- Solution
> **(a)** The run on `000`:
>
> | step | configuration | step | configuration |
> |---|---|---|---|
> | 0 | $(\textit{start},\mathtt{000},0)$ | 5 | $(\mathit{look},\mathtt{110},1)$ |
> | 1 | $(\mathit{look},\mathtt{100},1)$ | 6 | $(\textit{start},\mathtt{110},2)$ |
> | 2 | $(\mathit{look},\mathtt{100},0)$ | 7 | $(\mathit{look},\mathtt{111},3)$ |
> | 3 | $(\textit{start},\mathtt{100},1)$ | 8 | $(\textit{accept},\mathtt{1111},2)$ |
> | 4 | $(\mathit{look},\mathtt{110},2)$ | | |
>
> $M$ **accepts** after 8 steps. In state $\textit{start}$ it overwrites a `0` with `1` and steps right; $\mathit{look}$ sees another `0`, steps back onto the `1` it just wrote, and steps forward again in state $\textit{start}$ — three steps per cell. After the last `0`, $\mathit{look}$ reads the blank, writes `1` and accepts.
>
> **(b)**
> - $\varepsilon$: **reject.** $\textit{start}$ reads $\square$ and has no transition for it, so $(\textit{start},\varepsilon,0)\Rightarrow(\textit{reject},\varepsilon,0)$.
> - `1`: **crash.** $\textit{start}$ reads `1` on cell 0 and moves left; there is no next configuration.
> - `01`: **reject.** $(\textit{start},\mathtt{01},0)\Rightarrow(\mathit{look},\mathtt{11},1)\Rightarrow(\textit{start},\mathtt{11},2)$, and $\textit{start}$ reads $\square$.
> - `011`: **runs forever.** $(\textit{start},\mathtt{011},0)\Rightarrow(\mathit{look},\mathtt{111},1)\Rightarrow(\textit{start},\mathtt{111},2)\Rightarrow(\mathit{look},\mathtt{111},1)$. The configuration of step 1 has come back at step 3. A Turing machine is deterministic, so from then on it alternates between these two configurations forever.
>
> **(c) No.** A machine that decides a language halts on every input, and $M$ crashes on `1` and runs forever on `011`.
>
> **Going further.** Following the head on every input gives the complete picture. In state $\textit{start}$ on a `0`, the machine uses up that `0` if the next symbol is `0`, and the block `01` if it is `1` ($\mathit{look}$ steps over the `1`). So it reads the input as a sequence of blocks `0` and `01`: it accepts if a lone `0` ends the input, rejects if a block `01` ends it, and loops as soon as a block `01` is followed by a `1`:
> $$
> \begin{aligned}
> \textsf{Accept}(M) &= (\mathtt{0}+\mathtt{01})^*\mathtt{0}, & \textsf{Reject}(M) &= \varepsilon+(\mathtt{0}+\mathtt{01})^*\mathtt{01},\\
> \text{crashes on } &\mathtt{1}(\mathtt{0}+\mathtt{1})^*, & \text{runs forever on } &(\mathtt{0}+\mathtt{01})^*\mathtt{011}(\mathtt{0}+\mathtt{1})^*.
> \end{aligned}
> $$
> $\textsf{Accept}(M)$ is regular, so it is decidable — just not by $M$. *Decidable* describes a language; *decides* relates one machine to one language.
>
> **Answer.** (a) Accepts after 8 steps, ending in $(\textit{accept},\mathtt{1111},2)$. (b) $\varepsilon$: reject; `1`: crash; `01`: reject; `011`: runs forever (a configuration repeats). (c) No: it crashes on `1` and runs forever on `011`.

### 6.3 A decider that only accepts

> [!easy] Easy · find the error · Turing machine design
> Let $E = \{w\in\{\mathtt{0},\mathtt{1}\}^* \mid \#(\mathtt{0},w) = \#(\mathtt{1},w)\}$. A student designs a Turing machine for $E$ and writes:
>
> *"The first symbol is overwritten with ${\vdash}$, which marks the left end and remembers one symbol still waiting for a partner. Then repeat: find an unmarked partner of the opposite kind to the right and mark it $\mathtt{x}$; walk back to the ${\vdash}$; find the first unmarked symbol, mark it $\mathtt{x}$, and look for its partner. When no unmarked symbol is left, accept. In the table, — means 'write back the symbol read', and missing transitions reject. My machine decides $E$."*
>
> | state | read | write | move | next state |
> |---|---|---|---|---|
> | $\textit{start}$ | $\mathtt{0}$ | ${\vdash}$ | $+1$ | $\mathit{seek1}$ |
> | | $\mathtt{1}$ | ${\vdash}$ | $+1$ | $\mathit{seek0}$ |
> | | $\square$ | — | $+1$ | $\textit{accept}$ |
> | $\mathit{seek1}$ | $\mathtt{0}$, $\mathtt{x}$ | — | $+1$ | $\mathit{seek1}$ |
> | | $\mathtt{1}$ | $\mathtt{x}$ | $-1$ | $\mathit{rewind}$ |
> | | $\square$ | — | $+1$ | $\mathit{seek1}$ |
> | $\mathit{seek0}$ | $\mathtt{1}$, $\mathtt{x}$ | — | $+1$ | $\mathit{seek0}$ |
> | | $\mathtt{0}$ | $\mathtt{x}$ | $-1$ | $\mathit{rewind}$ |
> | $\mathit{rewind}$ | $\mathtt{0}$, $\mathtt{1}$, $\mathtt{x}$ | — | $-1$ | $\mathit{rewind}$ |
> | | ${\vdash}$ | — | $+1$ | $\mathit{next}$ |
> | $\mathit{next}$ | $\mathtt{x}$ | — | $+1$ | $\mathit{next}$ |
> | | $\mathtt{0}$ | $\mathtt{x}$ | $+1$ | $\mathit{seek1}$ |
> | | $\mathtt{1}$ | $\mathtt{x}$ | $+1$ | $\mathit{seek0}$ |
> | | $\square$ | — | $+1$ | $\textit{accept}$ |
>
> (a) Run the machine on `100`. (b) What is wrong with the claim "my machine decides $E$", and which entry causes it? Fix the machine. (c) Does the student's machine *accept* $E$?
>
> *Source: original.*

> [!hint]- Hint
> On `100`, the first `1` finds its partner. What happens to the second `0`?

> [!solution]- Solution
> **(a)** The first `1` is matched with the first `0`; then the second `0` looks for a partner that does not exist:
> $$
> \begin{aligned}
> &(\textit{start},\mathtt{100},0)\Rightarrow(\mathit{seek0},{\vdash}\mathtt{00},1)\Rightarrow(\mathit{rewind},{\vdash}\mathtt{x0},0)\Rightarrow(\mathit{next},{\vdash}\mathtt{x0},1)\\
> &\Rightarrow(\mathit{next},{\vdash}\mathtt{x0},2)\Rightarrow(\mathit{seek1},{\vdash}\mathtt{xx},3)\Rightarrow(\mathit{seek1},{\vdash}\mathtt{xx},4)\Rightarrow(\mathit{seek1},{\vdash}\mathtt{xx},5)\Rightarrow\cdots
> \end{aligned}
> $$
> From step 5 on, $\mathit{seek1}$ reads a blank, moves right, and reads another blank: the machine **runs forever**.
>
> **(b) The slip is the entry $\delta(\mathit{seek1},\square) = (\mathit{seek1},\square,+1)$** — "keep looking for a `1`" after the input has ended. Every cell past the input is blank, so once $\mathit{seek1}$ reaches the end it never halts. That happens on every string with more `0`s than `1`s (each round marks one `0` and one `1`, so eventually a `0` is left without a partner), and a decider must halt on every input. **Fix:** delete that entry. Reaching the blank in $\mathit{seek1}$ means "this `0` has no partner", so $w\notin E$, and the missing transition rejects — exactly what $\mathit{seek0}$ already does when it reaches a blank. With this change the machine decides $E$.
>
> **(c) Yes.** The bad entry is used only when $\mathit{seek1}$ reaches the blank; on every other input the student's machine and the fixed one behave identically. So the student's machine accepts exactly $E$, rejects the strings with more `1`s than `0`s, and runs forever on the strings with more `0`s than `1`s: it **accepts** $E$ but does not **decide** it.
>
> **Watch out:** every "scan for something" state needs an answer to *what if I reach the blank?* "Skip every symbol that is not a `1`" is exactly the thought that produces this bug.
>
> **Answer.** (a) It runs forever: after matching the `1`, $\mathit{seek1}$ walks right over blanks forever. (b) $\delta(\mathit{seek1},\square) = (\mathit{seek1},\square,+1)$ makes it loop on every string with more `0`s than `1`s; delete it, so that the blank rejects. (c) Yes: $\textsf{Accept}(M) = E$, but $M$ is not a decider.

## Medium

### 6.4 Palindromes by peeling both ends

> [!medium] Medium · Turing machine design
> Design a Turing machine that **decides** $\textsf{Pal} = \{w\in\{\mathtt{0},\mathtt{1}\}^* \mid w = w^R\}$. Give
>
> (a) the algorithm in English, as passes over the tape;
>
> (b) a transition table with a one-line meaning for every state;
>
> (c) an argument that your machine never crashes and halts on every input of length $n$ within $O(n^2)$ steps.
>
> *Source: classic.*

> [!hint]- Hint
> A string of length at least 2 is a palindrome exactly when its first and last symbols agree and the part between them is a palindrome. Remember the first symbol in the state, and **erase** symbols as you use them: the blank left behind at the front also tells the machine where to stop when it walks back.

> [!solution]- Solution
> **Idea.** Peel off the two ends: erase the first remaining symbol, remembering it in the state; walk to the end; compare and erase the last remaining symbol; walk back. Nothing left, or a lone middle symbol, means accept.
>
> **(a) Algorithm.** Repeat:
> 1. If the current cell is blank, nothing is left: accept. Otherwise erase the current symbol $a$ and remember it.
> 2. Walk right to the first blank, and step back onto the last remaining symbol.
> 3. If that cell is blank, the erased $a$ was the middle symbol: accept. If it holds the other symbol, reject. If it holds $a$, erase it.
> 4. Walk left to the first blank, step right, and start over.
>
> **(b) Transition table** ("—" means "write back the symbol read"; missing transitions reject):
>
> | state | read | write | move | next state | meaning |
> |---|---|---|---|---|---|
> | $\textit{start}$ | $\mathtt{0}$ | $\square$ | $+1$ | $\mathit{have0}$ | erase the first remaining symbol, a 0 … |
> | | $\mathtt{1}$ | $\square$ | $+1$ | $\mathit{have1}$ | … or a 1 |
> | | $\square$ | — | $+1$ | $\textit{accept}$ | nothing left: every pair matched |
> | $\mathit{have0}$ | $\mathtt{0}$, $\mathtt{1}$ | — | $+1$ | $\mathit{have0}$ | the first symbol was 0; walk to the end |
> | | $\square$ | — | $-1$ | $\mathit{last0}$ | step back onto the last remaining symbol |
> | $\mathit{have1}$ | $\mathtt{0}$, $\mathtt{1}$ | — | $+1$ | $\mathit{have1}$ | the first symbol was 1; walk to the end |
> | | $\square$ | — | $-1$ | $\mathit{last1}$ | |
> | $\mathit{last0}$ | $\mathtt{0}$ | $\square$ | $-1$ | $\mathit{back}$ | the ends agree: erase the last symbol |
> | | $\square$ | — | $+1$ | $\textit{accept}$ | nothing after the erased 0: it was the middle |
> | $\mathit{last1}$ | $\mathtt{1}$ | $\square$ | $-1$ | $\mathit{back}$ | the ends agree |
> | | $\square$ | — | $+1$ | $\textit{accept}$ | the erased 1 was the middle |
> | $\mathit{back}$ | $\mathtt{0}$, $\mathtt{1}$ | — | $-1$ | $\mathit{back}$ | walk left over the remaining symbols |
> | | $\square$ | — | $+1$ | $\textit{start}$ | the blank in front of them: next round |
>
> The rejections are the missing transitions $\delta(\mathit{last0},\mathtt{1})$ and $\delta(\mathit{last1},\mathtt{0})$: the ends differ.
>
> **(c) No crash.** The first step erases cell 0, so from then on cell 0 is blank and $\mathit{back}$ stops there at the latest, moving right. The other left moves step from a blank onto the last remaining symbol, or from the last remaining symbol (which lies to the right of the erased first one) one cell left, never past cell 0. **Running time.** Each round erases two symbols (one in the final round of an odd-length input), so there are at most $n/2+1$ rounds, and each round walks across the remaining symbols and back, at most $2n+1$ steps: $O(n^2)$ in all. Exactly, on a palindrome of length $n$ the machine takes $(n+1)(n+2)/2$ steps (a round on $m\ge2$ remaining symbols costs $2m+1$ steps); on other inputs it rejects sooner.
>
> **Check.** On `0110`: round 1 erases both `0`s and walks back to cell 0; round 2 erases both `1`s; then $\textit{start}$ reads $\square$ and accepts — 15 steps $= 5\cdot6/2$. On `0100`: round 1 erases the outer `0`s, then $\mathit{last1}$ reads `0` and rejects (13 steps). On `010`: after round 1, $\textit{start}$ erases the `1`, $\mathit{have1}$ reads $\square$ at once, and $\mathit{last1}$ reads the blank where the `1` was: accept. On $\varepsilon$: accept in one step.
>
> **Answer.** The six-state machine above (erase the first symbol, remember it, compare with the last, erase, walk back); it never crashes and takes $(n+1)(n+2)/2 = O(n^2)$ steps on palindromes of length $n$.

### 6.5 Two tapes, linear time

> [!medium] Medium · TM variants · Turing machine design
> A **two-tape** Turing machine has one finite control and two tapes, each with its own head. Its transition function has the form $\delta(p,(a_1,a_2)) = (q,(b_1,b_2),(\Delta_1,\Delta_2))$: it reads the symbols $a_1, a_2$ under the two heads, writes $b_1$ and $b_2$, and moves each head by $\Delta_k\in\{-1,0,+1\}$ (in this problem a head may also stay put). The input is on tape 1, tape 2 is blank, both heads start on cell 0, and a head moving left from cell 0 crashes the machine.
>
> (a) Design a two-tape machine that decides $Z = \{\mathtt{0}^n\mathtt{1}^n\mathtt{0}^n \mid n\ge0\}$ within $O(\lvert w\rvert)$ steps on every input $w$. Describe it in English and give its transition table with a meaning for every state.
>
> (b) Exactly how many steps does your machine take on $\mathtt{0}^k\mathtt{1}^k\mathtt{0}^k$? Compare with the one-tape machine of [[1-models-of-computation/06-turing-machines#63-a-first-example|§6.3]], which takes $4k^2+9k+1$ steps.
>
> (c) What running time does the simulation of [[1-models-of-computation/06-turing-machines#66-tracks-heads-and-tapes|§6.6]] give for a one-tape machine built from yours? Does your machine show that two tapes can decide languages that one tape cannot?
>
> *Source: original.*

> [!hint]- Hint
> Use tape 2 as a unary counter: one mark per `0` of the first block. Then walk tape 2's head back over the marks while tape 1 reads the `1`s, and forward again while tape 1 reads the last block. Make the mark in tape 2's cell 0 special, so that its head knows where to stop.

> [!solution]- Solution
> **Idea.** One left-to-right pass over the input, with tape 2 counting: write one mark per `0` of the first block (the first one is ${\vdash}$, so that cell 0 of tape 2 is recognizable); match the `1`s against the marks walking tape 2 *left*, then match the last block against the marks walking tape 2 *right*.
>
> **Construction.** Missing transitions reject; "—" means "write back the symbols read".
>
> | state | read $(a_1,a_2)$ | write | move | next state | meaning |
> |---|---|---|---|---|---|
> | $\textit{start}$ | $(\mathtt{0},\square)$ | $(\mathtt{0},{\vdash})$ | $(+1,+1)$ | $\mathit{copy}$ | first 0: mark tape 2's cell 0 with ${\vdash}$ |
> | | $(\square,\square)$ | — | $(+1,+1)$ | $\textit{accept}$ | $\varepsilon\in Z$ |
> | $\mathit{copy}$ | $(\mathtt{0},\square)$ | $(\mathtt{0},\mathtt{x})$ | $(+1,+1)$ | $\mathit{copy}$ | one mark per further 0 of block 1 |
> | | $(\mathtt{1},\square)$ | — | $(0,-1)$ | $\mathit{match1}$ | block 1 is over: tape 2 steps back onto the last mark |
> | $\mathit{match1}$ | $(\mathtt{1},\mathtt{x})$ | — | $(+1,-1)$ | $\mathit{match1}$ | pair a 1 with a mark, walking tape 2 left |
> | | $(\mathtt{1},{\vdash})$ | — | $(+1,0)$ | $\mathit{match0}$ | this 1 pairs with ${\vdash}$; tape 2 stays put |
> | $\mathit{match0}$ | $(\mathtt{0},{\vdash})$, $(\mathtt{0},\mathtt{x})$ | — | $(+1,+1)$ | $\mathit{match0}$ | pair a 0 of block 3 with a mark, walking tape 2 right |
> | | $(\square,\square)$ | — | $(+1,+1)$ | $\textit{accept}$ | input and marks run out together |
>
> Every way to fail is a missing transition: $\textit{start}$ reading a `1` (no first block), $\mathit{copy}$ reading $(\square,\square)$ (no `1`s), $\mathit{match1}$ reading a `0` or $\square$ on tape 1 (too few `1`s), and $\mathit{match0}$ reading a `1` (too many `1`s, or a fourth block), $(\mathtt{0},\square)$ (block 3 too long), or $(\square,\mathtt{x})$ or $(\square,{\vdash})$ (block 3 too short). The tape-2 head moves left only from a cell holding $\mathtt{x}$, which is never cell 0, so the machine never crashes. Tape 1's head moves right in every step but one, so the machine halts within $\lvert w\rvert+2$ steps.
>
> **(b)** For $k\ge1$: 1 step in $\textit{start}$, $k-1$ in $\mathit{copy}$ on the remaining `0`s, 1 more when $\mathit{copy}$ meets the first `1`, $k$ in $\mathit{match1}$, $k$ in $\mathit{match0}$, and 1 to accept — **$3k+2$ steps** (and 1 step for $k=0$). Against $4k^2+9k+1$: for $k = 100$, 302 steps instead of 40,901.
>
> **(c)** One tape simulates $t$ steps of a two-tape machine in $O(t^2)$ steps when $t\ge n$ (two tracks per tape — contents and head mark — and one sweep over the used cells per simulated step). Here $t = O(n)$, so the simulation decides $Z$ in $O(n^2)$ steps on one tape, the same order as the machine of §6.3. **No:** every two-tape machine can be simulated by a one-tape machine, so both models decide exactly the same languages; the second tape saves time, not power.
>
> **Check.** On `010`: $\textit{start}$ writes ${\vdash}$; $\mathit{copy}$ meets the `1` and backs tape 2 onto ${\vdash}$; $\mathit{match1}$ pairs the `1` with ${\vdash}$; $\mathit{match0}$ pairs the last `0` with ${\vdash}$, then reads $(\square,\square)$: accept after 5 steps $= 3\cdot1+2$. On `0110`, $\mathit{match0}$ reads $(\mathtt{1},{\vdash})$ and rejects; on `00110`, $\mathit{match0}$ reads $(\square,\mathtt{x})$ and rejects.
>
> **Answer.** (a) The four-state machine above: count block 1 on tape 2, match block 2 walking tape 2 left, block 3 walking it right. (b) $3k+2$ steps, against $4k^2+9k+1$ with one tape. (c) $O(n^2)$ by simulation; two tapes decide no new languages, they only run faster.

## Hard

### 6.6 A machine that doubles its input

> [!hard] Hard · Turing machine design · TM simulation
> A Turing machine **computes** a function as in [[1-models-of-computation/06-turing-machines#65-computing-functions|§6.5]]: it has a single halting state $\textit{halt}$, and its output is the tape contents when it halts, without trailing blanks. Design a one-tape Turing machine that computes the **doubling** function $D(w) = ww$ for $w\in\{\mathtt{0},\mathtt{1}\}^*$; for example $D(\mathtt{10}) = \mathtt{1010}$ and $D(\varepsilon) = \varepsilon$.
>
> (a) Describe your algorithm in English as passes over the tape. You may add tape symbols.
>
> (b) Give the transition table, with a one-line meaning for every state, and explain why your machine never moves left from cell 0.
>
> (c) Trace your machine on input `10` (every configuration).
>
> (d) Find the exact number of steps your machine takes on an input of length $n$, and conclude that it runs in $\Theta(n^2)$ time.
>
> *Source: textbook exercise style.*

> [!hint]- Hint
> Copy one symbol per round, left to right: mark it, carry it to the end in the state, write it there, and walk back. Write the copies as new symbols until the very end (what goes wrong otherwise?). And mark only the symbol you are copying *right now*: then the walk back always stops at that mark, and the machine never needs to find cell 0.

> [!solution]- Solution
> **Idea.** Round $i$ copies the $i$th symbol: the state carries it to the right end. Two kinds of temporary symbols: copies are written as $\mathtt{a}$ (a copy of 0) and $\mathtt{b}$ (a copy of 1), so the machine can see where the original ends; and the one symbol being copied is written as $\hat{\mathtt{0}}$ or $\hat{\mathtt{1}}$, which is where the walk back stops.
>
> **(a) Algorithm.**
> 1. ($\mathit{next}$) If the current cell holds an original symbol $c$, overwrite it with $\hat{c}$ and carry $c$ to the right. If it holds a copy, every symbol has been copied: go to step 4. If it is blank (only when $w = \varepsilon$), halt.
> 2. ($\mathit{carry0}$, $\mathit{carry1}$) Move right over originals and copies to the first blank, write the copy of $c$ there, and step left.
> 3. ($\mathit{back}$) Move left to the hatted cell, restore it to $c$, step right, and go to step 1.
> 4. ($\mathit{clean}$) Walk right turning $\mathtt{a}$ into `0` and $\mathtt{b}$ into `1`; halt at the blank.
>
> **(b) Transition table** (tape alphabet $\{\mathtt{0},\mathtt{1},\hat{\mathtt{0}},\hat{\mathtt{1}},\mathtt{a},\mathtt{b},\square\}$; "—" means "write back the symbol read"):
>
> | state | read | write | move | next state | meaning |
> |---|---|---|---|---|---|
> | $\mathit{next}$ (start) | $\mathtt{0}$ | $\hat{\mathtt{0}}$ | $+1$ | $\mathit{carry0}$ | mark the symbol to copy, a 0 … |
> | | $\mathtt{1}$ | $\hat{\mathtt{1}}$ | $+1$ | $\mathit{carry1}$ | … or a 1 |
> | | $\mathtt{a}$ | $\mathtt{0}$ | $+1$ | $\mathit{clean}$ | the first copy: every original is copied |
> | | $\mathtt{b}$ | $\mathtt{1}$ | $+1$ | $\mathit{clean}$ | |
> | | $\square$ | — | $+1$ | $\textit{halt}$ | empty input: $D(\varepsilon) = \varepsilon$ |
> | $\mathit{carry0}$ | $\mathtt{0}$, $\mathtt{1}$, $\mathtt{a}$, $\mathtt{b}$ | — | $+1$ | $\mathit{carry0}$ | carrying a 0 to the end … |
> | | $\square$ | $\mathtt{a}$ | $-1$ | $\mathit{back}$ | … append its copy |
> | $\mathit{carry1}$ | $\mathtt{0}$, $\mathtt{1}$, $\mathtt{a}$, $\mathtt{b}$ | — | $+1$ | $\mathit{carry1}$ | carrying a 1 to the end … |
> | | $\square$ | $\mathtt{b}$ | $-1$ | $\mathit{back}$ | … append its copy |
> | $\mathit{back}$ | $\mathtt{0}$, $\mathtt{1}$, $\mathtt{a}$, $\mathtt{b}$ | — | $-1$ | $\mathit{back}$ | walk left to the hatted cell |
> | | $\hat{\mathtt{0}}$ | $\mathtt{0}$ | $+1$ | $\mathit{next}$ | restore it; the next cell is the next to copy |
> | | $\hat{\mathtt{1}}$ | $\mathtt{1}$ | $+1$ | $\mathit{next}$ | |
> | $\mathit{clean}$ | $\mathtt{a}$ | $\mathtt{0}$ | $+1$ | $\mathit{clean}$ | turn the copies into ordinary symbols |
> | | $\mathtt{b}$ | $\mathtt{1}$ | $+1$ | $\mathit{clean}$ | |
> | | $\square$ | — | $+1$ | $\textit{halt}$ | done: the tape holds $ww$ |
>
> The pairs not listed never occur. **No crash:** there are two kinds of left moves. $\mathit{carry}$ steps left from the blank it has just filled, which lies to the right of the hatted cell; $\mathit{back}$ walks left only until it reads the hatted cell, and exactly one cell — the one being copied — is hatted whenever $\mathit{back}$ runs, so it turns right there, at cell 0 at the earliest.
>
> **(c) Trace on `10`** (hats and copies as they stand on the tape):
>
> | step | configuration | step | configuration |
> |---|---|---|---|
> | 0 | $(\mathit{next},\mathtt{10},0)$ | 7 | $(\mathit{carry0},\mathtt{1}\hat{\mathtt{0}}\mathtt{b},3)$ |
> | 1 | $(\mathit{carry1},\hat{\mathtt{1}}\mathtt{0},1)$ | 8 | $(\mathit{back},\mathtt{1}\hat{\mathtt{0}}\mathtt{ba},2)$ |
> | 2 | $(\mathit{carry1},\hat{\mathtt{1}}\mathtt{0},2)$ | 9 | $(\mathit{back},\mathtt{1}\hat{\mathtt{0}}\mathtt{ba},1)$ |
> | 3 | $(\mathit{back},\hat{\mathtt{1}}\mathtt{0b},1)$ | 10 | $(\mathit{next},\mathtt{10ba},2)$ |
> | 4 | $(\mathit{back},\hat{\mathtt{1}}\mathtt{0b},0)$ | 11 | $(\mathit{clean},\mathtt{101a},3)$ |
> | 5 | $(\mathit{next},\mathtt{10b},1)$ | 12 | $(\mathit{clean},\mathtt{1010},4)$ |
> | 6 | $(\mathit{carry0},\mathtt{1}\hat{\mathtt{0}}\mathtt{b},2)$ | 13 | $(\textit{halt},\mathtt{1010},5)$ |
>
> It halts after 13 steps with output `1010`.
>
> **(d) Step count.** Let $n = \lvert w\rvert$. The round that copies the symbol in cell $i$ takes: 1 step in $\mathit{next}$; $n-1$ steps of $\mathit{carry}$ over cells $i+1,\dots,n+i-1$ (the $n-1-i$ remaining originals and the $i$ copies so far); 1 step writing the copy in cell $n+i$; $n-1$ steps of $\mathit{back}$ over cells $n+i-1,\dots,i+1$; and 1 step restoring cell $i$. That is $2n+1$ steps per round, $n(2n+1)$ for all $n$ rounds. The finish takes 1 step in $\mathit{next}$ on the first copy, $n-1$ steps of $\mathit{clean}$ and 1 step at the blank: $n+1$ more. In total
> $$
> T(n) = n(2n+1) + n + 1 = 2n^2+2n+1,
> $$
> which is also right for $n = 0$ (one step). Since $2n^2\le T(n)\le 5n^2$ for $n\ge1$, the machine runs in $\Theta(n^2)$ time. Check: $T(2) = 13$, as in (c).
>
> **Watch out:**
> - Writing each copy as a plain `0` or `1` breaks termination: after the last original, $\mathit{next}$ sees the first copy, copies *it*, and the machine keeps copying its own copies forever.
> - Keeping *every* copied original hatted, and planning to unhat them all at the end while walking left, crashes: walking left over hatted symbols, the machine cannot tell when it has reached cell 0. Either hat only the current symbol (as here) or give cell 0 a mark of its own.
> - The final head position does not matter: the output is the tape contents.
>
> **Answer.** (a)–(b) The five-state machine above (mark the current symbol, carry it to the end, append a temporary copy, walk back to the mark; finally clean up the copies). (c) 13 steps, ending in $(\textit{halt},\mathtt{1010},5)$. (d) Exactly $2n^2+2n+1$ steps, so $\Theta(n^2)$.

### Sources for this page
Problems 6.1, 6.2, 6.3 and 6.5 are original; 6.4 (palindromes, decided by peeling off both ends) and 6.6 (the doubling function, computed by copying one symbol per round) are classic textbook exercises, written here in our own words. The facts behind 6.1 and 6.5 — removing stay-put moves, folding a two-way infinite tape onto two tracks, the quadratic one-tape simulation of several tapes, and the marked palindromes — are from §§6.4 and 6.6 of the book, and 6.5 revisits the language $\{\mathtt{0}^n\mathtt{1}^n\mathtt{0}^n\}$ of §6.3. None is taken from a course exam or homework. Every machine, trace and step count on this page is checked by `tools/practice/checks/ch06.py`: the one- and two-tape machines on all inputs of length up to 12–14, the four outcomes of 6.2 on every input up to length 12, and the constructions behind 6.1 (right-moving machines are DFAs, stay-put removal, two-track folding) on hundreds of random machines.

*Previous: [[practice/05-context-free-languages|Chapter 5 practice]] · next: [[practice/07-undecidability|Chapter 7 practice]] · [[practice/index|all practice]]*
