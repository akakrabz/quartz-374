---
title: "Practice — Chapter 4: Nondeterministic automata"
description: "10 practice problems (4 easy, 3 medium, 3 hard) on NFA design by guessing, running NFAs with ε-transitions, the subset construction, Thompson's algorithm, state elimination and two-part regular language transformations, each with a folded hint and a worked solution."
tags: [practice, regular, midterm-1]
chapter: 4
---

*Practice for [[1-models-of-computation/04-nondeterministic-automata|Chapter 4]] · concepts: [[concepts/nfa]] · [[concepts/subset-construction]] · [[concepts/state-elimination]] · [[concepts/language-transformations]] · all practice: [[practice/index|hub]] · by difficulty: [[practice/easy|easy]] · [[practice/medium|medium]] · [[practice/hard|hard]] · [[practice/topics|by topic]]*

Work each problem on paper first. Open the **hint** only when stuck, and the **solution** only after you have an answer you would hand in. Every automaton, expression and construction in the solutions has been checked by a script.

## Easy

### 4.1 Six quick NFA facts

> [!easy] Easy · true or false · NFA design · subset construction
> Decide whether each statement is true or false, and give a one-sentence reason (a counterexample when the answer is No). Throughout, $N$ is an NFA over $\Sigma = \{\mathtt{0},\mathtt{1}\}$, possibly with $\varepsilon$-transitions.
>
> (a) If $N$ has $n$ states, then some DFA with at most $2^n$ states accepts $L(N)$.
>
> (b) If $N = (\Sigma, Q, s, A, \delta)$ accepts $L$, then $(\Sigma, Q, s, Q\setminus A, \delta)$ accepts $\overline{L}$.
>
> (c) If $N$ has $n$ states and $L(N)\ne\varnothing$, then $N$ accepts some string of length at most $n-1$.
>
> (d) Every regular language is accepted by an NFA *without* $\varepsilon$-transitions that has exactly one accepting state.
>
> (e) Some language is accepted by an NFA with 4 states but by no DFA with fewer than 8 states.
>
> (f) If $L$ is regular, then so is $\{\textsf{sort}(w) \mid w\in L\}$, where $\textsf{sort}(w) = \mathtt{0}^{\#(\mathtt{0},w)}\mathtt{1}^{\#(\mathtt{1},w)}$ lists the 0s of $w$ before its 1s.
>
> *Source: original (statement (e) is a classic example).*

> [!hint]- Hint
> An NFA rejects a string when *no* path accepts it, and swapping the accepting states does not create new paths. For (d), try a language that contains $\varepsilon$ and one more short string. For (e), think of "the third symbol from the end".

> [!solution]- Solution
> **(a) Yes** — the subset construction ([[1-models-of-computation/04-nondeterministic-automata#45-nfa-to-dfa-the-subset-construction|§4.5]]) gives a DFA whose states are subsets of the $n$ states of $N$, and there are $2^n$ subsets.
>
> **(b) No** — an NFA can reject a string by having no path for it at all, and then the swapped machine has no path either. The one-state NFA with $A = \{s\}$ and no transitions accepts $\{\varepsilon\}$; swapping gives $A = \varnothing$, which accepts nothing, although $\mathtt{0}\in\overline{\{\varepsilon\}}$.
>
> **(c) Yes** — an accepting walk with the fewest transitions never visits a state twice (otherwise cut out the loop), so it has at most $n-1$ transitions and spells a string of length at most $n-1$.
>
> **(d) No** — for $L = \{\varepsilon,\mathtt{0}\}$, accepting $\varepsilon$ without $\varepsilon$-transitions forces $A = \{s\}$, and then a path for $\mathtt{0}$ is a $\mathtt{0}$-loop at $s$, which also accepts $\mathtt{00}\notin L$. With $\varepsilon$-transitions the statement is true ([[1-models-of-computation/04-nondeterministic-automata#46-regular-expression-to-nfa-thompsons-algorithm|Lemma 4.2]]); here $s\xrightarrow{\varepsilon}f$, $s\xrightarrow{\mathtt{0}}f$, $A = \{f\}$ works.
>
> **(e) Yes** — "the third symbol from the end is 1", $(\mathtt{0}+\mathtt{1})^*\mathtt{1}(\mathtt{0}+\mathtt{1})(\mathtt{0}+\mathtt{1})$, has a 4-state NFA (loop at $s$, guess the 1, read two more symbols), and the 8 strings of length 3 form a fooling set: if $x\ne y$ differ in position $i$, the suffix $\mathtt{0}^{i-1}$ moves that position to third from the end.
>
> **(f) No** — for $L = (\mathtt{01})^*$ the sorted strings form $\{\mathtt{0}^n\mathtt{1}^n \mid n\ge0\}$, which is not regular ([[1-models-of-computation/03-finite-state-machines#38-proving-a-language-is-not-regular|Lemma 3.6]]). The transformations of [[1-models-of-computation/04-nondeterministic-automata#49-regular-language-transformations|§4.9]] preserve regularity because a finite automaton can carry them out; sorting needs unbounded memory.
>
> **Watch out:** (b) is the classic trap. To complement an NFA, first convert it to a DFA with the subset construction, then swap.
>
> **Answer.** (a) Yes. (b) No. (c) Yes. (d) No. (e) Yes. (f) No.

### 4.2 Running an NFA with epsilon-moves

> [!easy] Easy · epsilon-transitions
> The NFA $N$ over $\{\mathtt{0},\mathtt{1}\}$ below has start state $s$ and one accepting state, $d$. Empty cells are $\varnothing$.
>
> | state | $\mathtt{0}$ | $\mathtt{1}$ | $\varepsilon$ |
> |---|---|---|---|
> | → $s$ | | | $\{a\}$ |
> | $a$ | $\{b\}$ | | $\{c\}$ |
> | $b$ | | $\{a\}$ | |
> | $c$ | $\{d\}$ | $\{b\}$ | |
> | $d$ \* | | | $\{a\}$ |
>
> (a) Compute $\varepsilon\text{-reach}(q)$ for every state $q$.
>
> (b) Track the set of states $N$ can be in after each prefix of `0110` and of `1010`. Which of $\varepsilon$, `0110` and `1010` does $N$ accept?
>
> *Source: original.*

> [!hint]- Hint
> $\varepsilon\text{-reach}(q)$ contains $q$ itself and every state reachable by $\varepsilon$-transitions alone, in any number of steps. To read a symbol, apply it to every state of the current set, then take the $\varepsilon$-reach of the result ([[1-models-of-computation/04-nondeterministic-automata#43-epsilon-transitions|§4.3]]).

> [!solution]- Solution
> **(a)** Follow $\varepsilon$-edges until nothing new appears; every state reaches itself.
>
> | $q$ | $s$ | $a$ | $b$ | $c$ | $d$ |
> |---|---|---|---|---|---|
> | $\varepsilon\text{-reach}(q)$ | $\{s,a,c\}$ | $\{a,c\}$ | $\{b\}$ | $\{c\}$ | $\{d,a,c\}$ |
>
> The reach of $s$ needs a chain of two edges, $s\xrightarrow{\varepsilon}a\xrightarrow{\varepsilon}c$; so does the reach of $d$.
>
> **(b)** Start with $C_0 = \varepsilon\text{-reach}(s)$, and after each symbol $x$ let $C_i = \varepsilon\text{-reach}\big(\delta(C_{i-1},x)\big)$.
>
> | $i$ | prefix of `0110` | $C_i$ | prefix of `1010` | $C_i$ |
> |---|---|---|---|---|
> | 0 | $\varepsilon$ | $\{s,a,c\}$ | $\varepsilon$ | $\{s,a,c\}$ |
> | 1 | `0` | $\{a,b,c,d\}$ | `1` | $\{b\}$ |
> | 2 | `01` | $\{a,b,c\}$ | `10` | $\varnothing$ |
> | 3 | `011` | $\{a,b,c\}$ | `101` | $\varnothing$ |
> | 4 | `0110` | $\{a,b,c,d\}$ | `1010` | $\varnothing$ |
>
> For example, the first `0` of `0110` uses $a\xrightarrow{\mathtt{0}}b$ and $c\xrightarrow{\mathtt{0}}d$; the $\varepsilon$-reach of $\{b,d\}$ adds $a$ and $c$. A `1` from $\{a,b,c,d\}$ uses $b\xrightarrow{\mathtt{1}}a$ and $c\xrightarrow{\mathtt{1}}b$, giving $\{a,b\}$ and then $\{a,b,c\}$. On `1010` the only $\mathtt{1}$-edge out of $\{s,a,c\}$ is $c\to b$, and $b$ has no $\mathtt{0}$-edge, so every thread dies.
>
> So $N$ **accepts `0110`** ($d\in C_4$) and **rejects $\varepsilon$** ($C_0$ contains no accepting state) and **`1010`** (the set is empty).
>
> **Check.** An accepting path for `0110`:
> $$
> s\xrightarrow{\varepsilon}a\xrightarrow{\varepsilon}c\xrightarrow{\mathtt{0}}d\xrightarrow{\varepsilon}a\xrightarrow{\varepsilon}c\xrightarrow{\mathtt{1}}b\xrightarrow{\mathtt{1}}a\xrightarrow{\varepsilon}c\xrightarrow{\mathtt{0}}d.
> $$
> The thread that starts with $a\xrightarrow{\mathtt{0}}b$ dies: after $b\xrightarrow{\mathtt{1}}a\xrightarrow{\varepsilon}c\xrightarrow{\mathtt{1}}b$ the final `0` has no edge out of $b$. In fact $N$ accepts exactly the strings that end in `0` and whose leading block of 1s has even length: $(\mathtt{11})^*\mathtt{0}+(\mathtt{11})^*\mathtt{0}(\mathtt{0}+\mathtt{1})^*\mathtt{0}$.
>
> **Watch out:** whether $\varepsilon$ is accepted depends on $\varepsilon\text{-reach}(s)$, not on $s$ alone; and a set that becomes $\varnothing$ stays $\varnothing$.
>
> **Answer.** $\varepsilon$-reach: $s\mapsto\{s,a,c\}$, $a\mapsto\{a,c\}$, $b\mapsto\{b\}$, $c\mapsto\{c\}$, $d\mapsto\{d,a,c\}$. On `0110` the sets are $\{s,a,c\}, \{a,b,c,d\}, \{a,b,c\}, \{a,b,c\}, \{a,b,c,d\}$ (accepted); on `1010` they are $\{s,a,c\}, \{b\}, \varnothing, \varnothing, \varnothing$ (rejected); $\varepsilon$ is rejected.

### 4.3 The last symbol appeared earlier

> [!easy] Easy · NFA design
> Let $\Sigma = \{\mathtt{0},\mathtt{1},\mathtt{2}\}$ and let $L$ be the set of strings whose last symbol also appears earlier in the string: $L = \{x\,a \mid a\in\Sigma,\ x\in\Sigma^*,\ \#(a,x)\ge1\}$. For example `0120` and `11` are in $L$; `012`, `1` and $\varepsilon$ are not. Give an NFA for $L$ with at most 5 states, as a transition table with a one-line meaning for each state. No proof required.
>
> *Source: textbook exercise style.*

> [!hint]- Hint
> Guess the moment you read the *earlier* copy of the final symbol $a$. Then skip anything, and guess that the next $a$ ends the string.

> [!solution]- Solution
> **Idea.** A DFA would have to remember which symbols it has seen. An NFA guesses the earlier occurrence of the final symbol, and then guesses where the string ends.
>
> | state | $\mathtt{0}$ | $\mathtt{1}$ | $\mathtt{2}$ | meaning |
> |---|---|---|---|---|
> | → $s$ | $\{s, p_0\}$ | $\{s, p_1\}$ | $\{s, p_2\}$ | before the earlier copy |
> | $p_0$ | $\{p_0, f\}$ | $\{p_0\}$ | $\{p_0\}$ | read a $\mathtt{0}$ that will reappear at the end |
> | $p_1$ | $\{p_1\}$ | $\{p_1, f\}$ | $\{p_1\}$ | the same for $\mathtt{1}$ |
> | $p_2$ | $\{p_2\}$ | $\{p_2\}$ | $\{p_2, f\}$ | the same for $\mathtt{2}$ |
> | $f$ \* | $\varnothing$ | $\varnothing$ | $\varnothing$ | read the repeat; the input must end here |
>
> **Why it works.** An accepting path ends with an $a$-transition from $p_a$ into $f$, and it entered $p_a$ on an earlier $a$; so every accepted string is in $L$. Conversely, if $w = x\,a\,y\,a$, the path stays in $s$ on $x$, moves $s\xrightarrow{a}p_a$, loops on $y$, and ends with $p_a\xrightarrow{a}f$.
>
> **Check.** `0120`: $s\xrightarrow{\mathtt{0}}p_0\xrightarrow{\mathtt{1}}p_0\xrightarrow{\mathtt{2}}p_0\xrightarrow{\mathtt{0}}f$, accepted. `012`: the final $\mathtt{2}$ would have to be read from $p_2$, which needs an earlier $\mathtt{2}$, so it is rejected. `1` and $\varepsilon$: every path to $f$ reads at least two symbols.
>
> **Compare.** The smallest DFA for $L$ has 15 states: it must remember the set of symbols seen so far (7 non-empty sets) and whether the current last symbol had appeared before it (2 choices), plus a start state.
>
> **Answer.** States $s, p_0, p_1, p_2, f$; $s$ loops on every symbol and $s\xrightarrow{a}p_a$; each $p_a$ loops on every symbol and $p_a\xrightarrow{a}f$; start $s$, accepting $\{f\}$.

### 4.4 Find the error, Kleene star

> [!easy] Easy · find the error · epsilon-transitions · closure properties
> Let $M = (\Sigma, Q, s, A, \delta)$ be a DFA for a language $L$. A student builds an NFA for $L^*$ as follows.
>
> *"Keep all the states and transitions of $M$. Make $s$ accepting, so that $\varepsilon$ is accepted, and add an $\varepsilon$-transition from every accepting state back to $s$, so that the machine can start a new piece after finishing one: $N = (\Sigma, Q, s, A\cup\{s\}, \delta_N)$ with $\delta_N(q,a) = \{\delta(q,a)\}$, and $\delta_N(q,\varepsilon) = \{s\}$ for every $q\in A$."*
>
> (a) Show that the construction is wrong: give a DFA $M$ and a string that $N$ accepts but that is not in $L^*$.
>
> (b) Fix the construction.
>
> *Source: classic.*

> [!hint]- Hint
> Making $s$ accepting accepts every string that leads $M$ from $s$ back to $s$, not only $\varepsilon$. Try a DFA with a loop at $s$.

> [!solution]- Solution
> **(a) The slip is "make $s$ accepting".** It accepts $\varepsilon$, but also every string $x$ with $\delta^*(s,x) = s$, whether or not $x\in L^*$. Take $L = \mathtt{0}^*\mathtt{1}$ with the DFA $s\xrightarrow{\mathtt{0}}s$, $s\xrightarrow{\mathtt{1}}a$, $a\xrightarrow{\mathtt{0},\mathtt{1}}d$, $d\xrightarrow{\mathtt{0},\mathtt{1}}d$ and $A = \{a\}$. Every non-empty string in $L^*$ ends in $\mathtt{1}$, so $\mathtt{0}\notin L^*$; but $N$ accepts $\mathtt{0}$ by looping once at the now-accepting state $s$. (Here $N$ accepts *every* string: after each $\mathtt{1}$ it can jump back to $s$ and stop there.)
>
> **(b) Add a fresh start state** for the empty string instead of reusing $s$:
> $$
> \begin{aligned}
> N' &= \big(\Sigma,\ Q\cup\{s'\},\ s',\ A\cup\{s'\},\ \delta'\big),\\
> \delta'(s',\varepsilon) &= \{s\}, \qquad \delta'(q,\varepsilon) = \{s\}\ \text{ for } q\in A,\\
> \delta'(q,a) &= \{\delta(q,a)\}\ \text{ for } q\in Q,\ a\in\Sigma.
> \end{aligned}
> $$
> No transition enters $s'$, so making it accepting adds only $\varepsilon$. Every other accepting walk goes from $s'$ to $s$, reads a string of $L$ to reach $A$, possibly jumps back to $s$ and repeats; it spells a concatenation of one or more strings of $L$, and every such concatenation has a walk.
>
> **Check.** With the DFA of (a), $N'$ accepts $\varepsilon$, `01` and `101` $=\mathtt{1}\cdot\mathtt{01}$, and rejects `0` and `10`.
>
> **Watch out:** the student's version happens to be correct whenever no transition of $M$ enters $s$, which is why it can survive a quick test. Thompson's star gadget avoids the problem the same way, with a fresh start state.
>
> **Answer.** (a) For $L = \mathtt{0}^*\mathtt{1}$ the student's NFA accepts $\mathtt{0}\notin L^*$ (in fact it accepts every string). (b) Add a new accepting start state $s'$ with $s'\xrightarrow{\varepsilon}s$, keep the $\varepsilon$-transitions from $A$ back to $s$, and do not make $s$ accepting (unless $s\in A$).

## Medium

### 4.5 Subset construction by hand

> [!medium] Medium · subset construction · epsilon-transitions
> The NFA $N$ below accepts $\mathtt{0}^*\mathtt{1}^* + \mathtt{1}^*\mathtt{0}^*$. Its start state is $s$, its accepting states are $b$ and $d$, and empty cells are $\varnothing$.
>
> | state | $\mathtt{0}$ | $\mathtt{1}$ | $\varepsilon$ |
> |---|---|---|---|
> | → $s$ | | | $\{a, c\}$ |
> | $a$ | $\{a\}$ | | $\{b\}$ |
> | $b$ \* | | $\{b\}$ | |
> | $c$ | | $\{c\}$ | $\{d\}$ |
> | $d$ \* | $\{d\}$ | | |
>
> (a) Convert $N$ to a DFA with the incremental subset construction: a table with columns $S$, $\varepsilon\text{-reach}(S)$, accepting?, $\delta'(S,\mathtt{0})$ and $\delta'(S,\mathtt{1})$, one row per reachable subset.
>
> (b) Describe in words the set of strings that leads to each DFA state, and decide whether the DFA is minimal.
>
> *Source: original.*

> [!hint]- Hint
> Begin with the row $S = \{s\}$. In each row first compute $R = \varepsilon\text{-reach}(S)$; then $\delta'(S,x)$ is the set of all $x$-successors of states in $R$. Every new set that appears in a transition column gets its own row, including $\varnothing$. A row is accepting when $R$ contains $b$ or $d$.

> [!solution]- Solution
> **(a)** In the book's version ([[1-models-of-computation/04-nondeterministic-automata#45-nfa-to-dfa-the-subset-construction|§4.5]]) the DFA states are sets $S$; $S$ is accepting iff $\varepsilon\text{-reach}(S)\cap A\ne\varnothing$, and $\delta'(S,x) = \bigcup_{r\in\varepsilon\text{-reach}(S)}\delta(r,x)$.
>
> | $S$ | $\varepsilon\text{-reach}(S)$ | accept? | $\delta'(S,\mathtt{0})$ | $\delta'(S,\mathtt{1})$ |
> |---|---|---|---|---|
> | → $\{s\}$ | $\{s,a,b,c,d\}$ | yes | $\{a,d\}$ | $\{b,c\}$ |
> | $\{a,d\}$ | $\{a,b,d\}$ | yes | $\{a,d\}$ | $\{b\}$ |
> | $\{b,c\}$ | $\{b,c,d\}$ | yes | $\{d\}$ | $\{b,c\}$ |
> | $\{b\}$ | $\{b\}$ | yes | $\varnothing$ | $\{b\}$ |
> | $\{d\}$ | $\{d\}$ | yes | $\{d\}$ | $\varnothing$ |
> | $\varnothing$ | $\varnothing$ | no | $\varnothing$ | $\varnothing$ |
>
> For example, the reach of $\{a,d\}$ is $\{a,b,d\}$ (because $a\xrightarrow{\varepsilon}b$); on $\mathtt{0}$ only $a\to a$ and $d\to d$ apply, giving $\{a,d\}$ again, and on $\mathtt{1}$ only $b\to b$ applies, giving $\{b\}$. Only 6 of the $2^5 = 32$ subsets are reachable.
>
> **(b) Meanings.**
>
> | DFA state | strings that lead to it |
> |---|---|
> | $\{s\}$ | only $\varepsilon$ |
> | $\{a,d\}$ | $\mathtt{0}^+$: only 0s, at least one |
> | $\{b,c\}$ | $\mathtt{1}^+$ |
> | $\{b\}$ | $\mathtt{0}^+\mathtt{1}^+$ |
> | $\{d\}$ | $\mathtt{1}^+\mathtt{0}^+$ |
> | $\varnothing$ | all strings outside $\mathtt{0}^*\mathtt{1}^*+\mathtt{1}^*\mathtt{0}^*$ |
>
> **Minimality.** Record which of the suffixes $\varepsilon, \mathtt{0}, \mathtt{1}, \mathtt{01}, \mathtt{10}$ lead from each state to acceptance:
>
> | state | $\varepsilon$ | $\mathtt{0}$ | $\mathtt{1}$ | $\mathtt{01}$ | $\mathtt{10}$ |
> |---|---|---|---|---|---|
> | $\{s\}$ | ✓ | ✓ | ✓ | ✓ | ✓ |
> | $\{a,d\}$ | ✓ | ✓ | ✓ | ✓ | — |
> | $\{b,c\}$ | ✓ | ✓ | ✓ | — | ✓ |
> | $\{b\}$ | ✓ | — | ✓ | — | — |
> | $\{d\}$ | ✓ | ✓ | — | — | — |
> | $\varnothing$ | — | — | — | — | — |
>
> The six rows are pairwise different, so any two states are distinguished by some suffix and no two can be merged: the DFA is minimal. Equivalently, $\{\varepsilon, \mathtt{0}, \mathtt{1}, \mathtt{01}, \mathtt{10}, \mathtt{010}\}$, one string per state, is a fooling set of size 6.
>
> **Check.** `0011` visits $\{s\},\{a,d\},\{a,d\},\{b\},\{b\}$ and is accepted; `010` visits $\{s\},\{a,d\},\{b\},\varnothing$ and is rejected — it is in neither $\mathtt{0}^*\mathtt{1}^*$ nor $\mathtt{1}^*\mathtt{0}^*$.
>
> **Watch out:** the $\varepsilon$-reach is taken *before* reading each symbol. Computing $\delta'(\{s\},\mathtt{0})$ from $s$ alone gives $\varnothing$, because $s$ has only $\varepsilon$-transitions, and loses the whole machine.
>
> **Answer.** Six states $\{s\}$ (start), $\{a,d\}$, $\{b,c\}$, $\{b\}$, $\{d\}$, $\varnothing$ with the transitions in the table, all accepting except $\varnothing$. They are reached by $\varepsilon$, $\mathtt{0}^+$, $\mathtt{1}^+$, $\mathtt{0}^+\mathtt{1}^+$, $\mathtt{1}^+\mathtt{0}^+$ and the rejected strings, and the DFA is minimal.

### 4.6 Thompson's NFA by the numbers

> [!medium] Medium · Thompson's algorithm · regex induction
> Thompson's algorithm ([[1-models-of-computation/04-nondeterministic-automata#46-regular-expression-to-nfa-thompsons-algorithm|§4.6]]) turns a leaf $\varnothing$, $\varepsilon$ or $a$ into two states joined by no transition, an $\varepsilon$-transition or an $a$-transition; it joins the machines for $S$ and $T$ in series by one $\varepsilon$-transition for $ST$; and for $S+T$ and for $S^*$ it adds a new start state, a new accepting state and four $\varepsilon$-transitions. A string such as $\mathtt{01}$ is a concatenation of one-symbol leaves.
>
> (a) For a regular expression $R$, let $\ell$ be its number of leaves (occurrences of $\varnothing$, $\varepsilon$ and symbols), of which $e$ are $\varepsilon$ and $\sigma$ are symbols, and let $u$, $k$, $c$ be its numbers of $+$, ${}^*$ and concatenation nodes. Show that Thompson's NFA for $R$ has exactly $2(\ell+u+k)$ states, $e+c+4u+4k$ $\varepsilon$-transitions and $\sigma$ symbol transitions.
>
> (b) Use (a) to count the states and transitions for $R = (\mathtt{1}+\mathtt{01})^*\mathtt{0}$, then build the NFA.
>
> (c) Compute the $\varepsilon$-reach of its start state and the set of states it can be in after reading `0` and after reading `01`. Which of the two strings does it accept?
>
> *Source: original.*

> [!hint]- Hint
> (a) is a structural induction: check the three leaves, then see what $ST$, $S+T$ and $S^*$ add to the counts for $S$ and $T$. In (b), $\mathtt{01}$ contributes two leaves and one concatenation node, and so does $(\cdots)^*\mathtt{0}$.

> [!solution]- Solution
> **(a) Structural induction on $R$.** Let $\#Q(R)$, $\#E(R)$, $\#S(R)$ be the numbers of states, $\varepsilon$-transitions and symbol transitions of Thompson's NFA for $R$, and assume the formulas for all proper subexpressions of $R$.
> - **Leaves.** $\varnothing$, $\varepsilon$ and $a$ each have 2 states; $\varepsilon$ has one $\varepsilon$-transition and $a$ one symbol transition. For a leaf $\ell = 1$, $u = k = c = 0$, and $e$ (resp. $\sigma$) is 1 exactly for $\varepsilon$ (resp. a symbol), so the formulas hold.
> - **$R = ST$.** The construction keeps both machines and adds one $\varepsilon$-transition: $\#Q(R) = \#Q(S)+\#Q(T)$, $\#E(R) = \#E(S)+\#E(T)+1$, $\#S(R) = \#S(S)+\#S(T)$. The counts $\ell, e, \sigma, u, k$ of $R$ are the sums of those of $S$ and $T$, and $c$ is one larger, so the induction hypothesis for $S$ and $T$ gives the formulas for $R$.
> - **$R = S+T$.** Two new states and four new $\varepsilon$-transitions; $u$ is one larger than the sum for $S$ and $T$, which adds exactly 2 to $2(\ell+u+k)$ and 4 to $e+c+4u+4k$.
> - **$R = S^*$.** Two new states and four new $\varepsilon$-transitions; $k$ is one larger than for $S$; the same arithmetic.
>
> **(b)** The leaves of $(\mathtt{1}+\mathtt{01})^*\mathtt{0}$ are $\mathtt{1},\mathtt{0},\mathtt{1},\mathtt{0}$, so $\ell = \sigma = 4$ and $e = 0$; there is one $+$, one ${}^*$ and two concatenations. Hence **12 states, $0+2+4+4 = 10$ $\varepsilon$-transitions and 4 symbol transitions.** Numbering the states in the order the recursion creates them:
>
> | states | gadget | its transitions |
> |---|---|---|
> | $0, 9$ | the star | $0\xrightarrow{\varepsilon}1$, $0\xrightarrow{\varepsilon}9$, $8\xrightarrow{\varepsilon}1$, $8\xrightarrow{\varepsilon}9$ |
> | $1, 8$ | the union | $1\xrightarrow{\varepsilon}2$, $1\xrightarrow{\varepsilon}4$, $3\xrightarrow{\varepsilon}8$, $7\xrightarrow{\varepsilon}8$ |
> | $2, 3$ | the leaf $\mathtt{1}$ | $2\xrightarrow{\mathtt{1}}3$ |
> | $4, 5, 6, 7$ | $\mathtt{0}$ then $\mathtt{1}$ in series | $4\xrightarrow{\mathtt{0}}5$, $5\xrightarrow{\varepsilon}6$, $6\xrightarrow{\mathtt{1}}7$ |
> | $10, 11$ | the final $\mathtt{0}$, in series after the star | $9\xrightarrow{\varepsilon}10$, $10\xrightarrow{\mathtt{0}}11$ |
>
> The start state is $0$ and the only accepting state is $11$.
>
> **(c)** $\varepsilon\text{-reach}(0) = \{0,1,2,4,9,10\}$: into the union ($1$, then $2$ and $4$) or past the star ($9$, then $10$). Reading `0` uses $4\xrightarrow{\mathtt{0}}5$ and $10\xrightarrow{\mathtt{0}}11$, and $\varepsilon\text{-reach}(\{5,11\}) = \{5,6,11\}$; it contains $11$, so **`0` is accepted**. Reading `1` next uses only $6\xrightarrow{\mathtt{1}}7$, and $\varepsilon\text{-reach}(\{7\}) = \{1,2,4,7,8,9,10\}$: back at the top of the loop, without $11$, so **`01` is rejected**.
>
> **Check.** $L(R)$ is the set of strings that end in `0` and contain no `00`: `0` is in it, `01` is not. For comparison, the incremental subset construction turns this 12-state NFA into a 5-state DFA, and the minimal DFA has 3 states.
>
> **Answer.** (a) $2(\ell+u+k)$ states, $e+c+4u+4k$ $\varepsilon$-transitions, one symbol transition per symbol leaf. (b) 12 states, 10 $\varepsilon$-transitions, 4 symbol transitions. (c) $\varepsilon\text{-reach}(0) = \{0,1,2,4,9,10\}$; after `0` the set is $\{5,6,11\}$ (accepted); after `01` it is $\{1,2,4,7,8,9,10\}$ (rejected).

### 4.7 Eliminating states, two parities

> [!medium] Medium · state elimination · regular expressions
> The DFA $M$ below tracks the parity of the number of 0s and of the number of 1s read so far ($\textsf{E}$ even, $\textsf{O}$ odd; $\textsf{OE}$ means "odd number of 0s, even number of 1s"). Its start state and only accepting state is $\textsf{EE}$, so $L(M)$ is the set of strings with an even number of 0s and an even number of 1s.
>
> | state | $\mathtt{0}$ | $\mathtt{1}$ |
> |---|---|---|
> | → $\textsf{EE}$ \* | $\textsf{OE}$ | $\textsf{EO}$ |
> | $\textsf{OE}$ | $\textsf{EE}$ | $\textsf{OO}$ |
> | $\textsf{EO}$ | $\textsf{OO}$ | $\textsf{EE}$ |
> | $\textsf{OO}$ | $\textsf{EO}$ | $\textsf{OE}$ |
>
> Use state elimination ([[1-models-of-computation/04-nondeterministic-automata#48-nfa-to-regular-expression-state-elimination|§4.8]]) to find a regular expression for $L(M)$: add a new start state and a new accepting state, then eliminate $\textsf{OE}$, $\textsf{EO}$, $\textsf{OO}$ and $\textsf{EE}$ in this order, giving the changed edge labels after each step.
>
> *Source: textbook exercise style.*

> [!hint]- Hint
> Eliminating $q$ replaces, for every predecessor $p$ and every successor $r$ of $q$ (including $p = r$), the label $R(p\to r)$ by $R(p\to r)+R(p\to q)\,R(q\to q)^*\,R(q\to r)$. Neither $\textsf{OE}$ nor $\textsf{EO}$ has a self-loop, and both sit between $\textsf{EE}$ and $\textsf{OO}$.

> [!solution]- Solution
> **Setup.** Add $s$ with $s\xrightarrow{\varepsilon}\textsf{EE}$ and $t$ with $\textsf{EE}\xrightarrow{\varepsilon}t$. All other labels are single symbols; missing edges are labeled $\varnothing$.
>
> **Eliminate $\textsf{OE}$.** No loop; it is entered from $\textsf{EE}$ on $\mathtt{0}$ and from $\textsf{OO}$ on $\mathtt{1}$, and left to $\textsf{EE}$ on $\mathtt{0}$ and to $\textsf{OO}$ on $\mathtt{1}$. One new label per predecessor–successor pair:
> $$
> \begin{aligned}
> R(\textsf{EE}\to\textsf{EE}) &= \mathtt{00}, &\qquad R(\textsf{EE}\to\textsf{OO}) &= \mathtt{01},\\
> R(\textsf{OO}\to\textsf{EE}) &= \mathtt{10}, & R(\textsf{OO}\to\textsf{OO}) &= \mathtt{11}.
> \end{aligned}
> $$
> **Eliminate $\textsf{EO}$.** No loop; entered from $\textsf{EE}$ on $\mathtt{1}$ and from $\textsf{OO}$ on $\mathtt{0}$, left to $\textsf{EE}$ on $\mathtt{1}$ and to $\textsf{OO}$ on $\mathtt{0}$. Each label gains one term:
> $$
> \begin{aligned}
> R(\textsf{EE}\to\textsf{EE}) &= \mathtt{00}+\mathtt{11}, &\qquad R(\textsf{EE}\to\textsf{OO}) &= \mathtt{01}+\mathtt{10},\\
> R(\textsf{OO}\to\textsf{EE}) &= \mathtt{10}+\mathtt{01}, & R(\textsf{OO}\to\textsf{OO}) &= \mathtt{11}+\mathtt{00}.
> \end{aligned}
> $$
> **Eliminate $\textsf{OO}$.** Its loop is $\mathtt{00}+\mathtt{11}$, and its only other neighbor is $\textsf{EE}$:
> $$
> R(\textsf{EE}\to\textsf{EE}) = \mathtt{00}+\mathtt{11}+(\mathtt{01}+\mathtt{10})(\mathtt{00}+\mathtt{11})^*(\mathtt{10}+\mathtt{01}) =: X.
> $$
> **Eliminate $\textsf{EE}$.** Its loop is $X$, entered from $s$ on $\varepsilon$ and left to $t$ on $\varepsilon$: $R(s\to t) = \varepsilon\,X^*\,\varepsilon = X^*$.
>
> **Reading the result.** Cut the string into pairs. A pair $\mathtt{00}$ or $\mathtt{11}$ keeps both parities; a mixed pair $\mathtt{01}$ or $\mathtt{10}$ flips both, so after one mixed pair the machine is in $\textsf{OO}$ and needs a second mixed pair, with only $\mathtt{00}$ and $\mathtt{11}$ pairs in between, to return to $\textsf{EE}$.
>
> **Check.** `0110` $=\mathtt{01}\cdot\mathtt{10}$ and `0101` $=\mathtt{01}\cdot\mathtt{01}$ each match $X$ once (a mixed pair, no unmixed pairs, a mixed pair); both have two 0s and two 1s. `011` has odd length, while every string matching $X^*$ has even length; indeed it has an odd number of 1s.
>
> **Watch out:** each elimination must update *every* predecessor–successor pair, including $p = r$ — here the new loops at $\textsf{EE}$ and $\textsf{OO}$ are exactly those pairs, and forgetting them is the most common slip.
>
> **Answer.** $\big(\mathtt{00}+\mathtt{11}+(\mathtt{01}+\mathtt{10})(\mathtt{00}+\mathtt{11})^*(\mathtt{10}+\mathtt{01})\big)^*$ (the order of the terms inside a union does not matter).

## Hard

### 4.8 Rotating the first symbol

> [!hard] Hard · language transformations · DFA design · NFA design
> For a string $w$, let $\textsf{rot}(w)$ move the first symbol of $w$ to the end: $\textsf{rot}(\varepsilon) = \varepsilon$ and $\textsf{rot}(a\,x) = x\,a$ for every symbol $a$ and string $x$. For example $\textsf{rot}(\mathtt{0110}) = \mathtt{1100}$ and $\textsf{rot}(\mathtt{1}) = \mathtt{1}$. Let $L$ be an arbitrary regular language over an alphabet $\Sigma$, and let $M = (\Sigma, Q, s, A, \delta)$ be a DFA for $L$.
>
> (a) Prove that $\textsf{RotPre}(L) := \{w \mid \textsf{rot}(w)\in L\}$ is regular: give a formal description of a DFA or NFA for it in terms of $M$, and explain in English what its states mean and why its accepting states are the right ones.
>
> (b) Do the same for $\textsf{RotImg}(L) := \{\textsf{rot}(w) \mid w\in L\}$.
>
> *Source: original.*

> [!hint]- Hint
> (a) Reading $w = a\,x$, the machine must feed $M$ the string $x\,a$. It can postpone the first symbol: remember $a$, simulate $M$ on $x$, and apply $a$ at the very end, in the accepting condition.
>
> (b) Now the input is $x\,a$ and $M$ must read $a\,x$. The symbol $a$ is needed first but arrives last: guess it at the start, and check the guess when the last symbol arrives.

> [!solution]- Solution
> **Idea.** Both parts move one symbol between the two ends of the string. A finite machine can remember one symbol (part a), or guess one symbol and verify it later (part b). See [[1-models-of-computation/04-nondeterministic-automata#49-regular-language-transformations|§4.9]] for the general pattern.
>
> **(a)** Let $M_1 = (\Sigma, Q_1, s_1, A_1, \delta_1)$ be the **DFA** with
> $$
> \begin{aligned}
> Q_1 &= \{s_1\}\cup(\Sigma\times Q), \qquad s_1 \text{ a new state},\\
> \delta_1(s_1, a) &= (a, s), \qquad \delta_1\big((a,q), b\big) = \big(a, \delta(q,b)\big),\\
> A_1 &= \{(a,q) \mid \delta(q,a)\in A\}\cup\{s_1 \mid s\in A\}.
> \end{aligned}
> $$
> *In English:* $s_1$ means "nothing read yet". The state $(a,q)$ means "the first symbol was $a$, and $M$, started at $s$ and fed everything *after* the first symbol, is in state $q$". After reading $w = a\,x$ the state is $(a, \delta^*(s,x))$, and $\textsf{rot}(w) = x\,a$ takes $M$ to $\delta(\delta^*(s,x), a)$; so $(a,q)$ must accept exactly when $\delta(q,a)\in A$. The empty input stays in $s_1$, and $\textsf{rot}(\varepsilon) = \varepsilon$, so $s_1$ accepts iff $\varepsilon\in L$, that is, iff $s\in A$.
>
> **(b)** A string $y$ is in $\textsf{RotImg}(L)$ iff $y = \varepsilon\in L$, or $y = x\,a$ for a symbol $a$ with $a\,x\in L$. Let $M_2 = (\Sigma, Q_2, s_2, A_2, \delta_2)$ be the **NFA** with
> $$
> \begin{aligned}
> Q_2 &= \{s_2, f\}\cup(\Sigma\times Q), \qquad s_2, f \text{ new states},\\
> \delta_2(s_2, \varepsilon) &= \{(a, \delta(s,a)) \mid a\in\Sigma\},\\
> \delta_2\big((a,q), b\big) &= \{(a, \delta(q,b))\}\cup\{f \mid b = a \text{ and } q\in A\},\\
> A_2 &= \{f\}\cup\{s_2 \mid s\in A\},
> \end{aligned}
> $$
> and no other transitions: none out of $f$, no symbol transitions out of $s_2$, and no other $\varepsilon$-transitions.
>
> *In English:* $M_2$ guesses the last symbol $a$ of its input before reading anything, and feeds it to $M$ first (the $\varepsilon$-move to $(a,\delta(s,a))$). The state $(a,q)$ means "the guess is $a$, and $M$ has read $a$ followed by the input so far and is in state $q$". When the input symbol $b$ equals $a$, the machine may also guess that it is the last symbol: it does not feed it to $M$, and moves to $f$ if $M$ is accepting. So $f$ means "the guessed symbol has arrived, and the preimage $a\,x$ is in $L$"; nothing may follow it. Finally, $s_2$ accepts only the empty input, which is in $\textsf{RotImg}(L)$ iff $\varepsilon\in L$.
>
> **Check.** For $L = \mathtt{1}(\mathtt{0}+\mathtt{1})^*$ (strings starting with 1), $\textsf{RotPre}(L) = \mathtt{1}+(\mathtt{0}+\mathtt{1})\mathtt{1}(\mathtt{0}+\mathtt{1})^*$ (the string `1`, or second symbol 1) and $\textsf{RotImg}(L) = (\mathtt{0}+\mathtt{1})^*\mathtt{1}$ (strings ending in 1), and these are exactly what $M_1$ and $M_2$ accept. The edge cases behave: $\varnothing$, $\{\varepsilon\}$ and $\Sigma^*$ are mapped to themselves by both constructions; for $\{\varepsilon\}$ the only reachable accepting state is $s_1$, resp. $s_2$.
>
> **Watch out:** leaving $s_1$ (or $s_2$) out of the accepting set loses $\varepsilon$ exactly when $\varepsilon\in L$. In (b), accepting in $(a,q)$ whenever $q\in A$, instead of moving to $f$, never checks that the input really ends with the guessed $a$.
>
> **Grading.** The course rubric for a transformation gives 2 points for a complete formal description (say whether it is a DFA or an NFA, and list the $\varepsilon$-transitions), 2 for the English explanation of the states and the accepting states, and 6 for correctness (1 for the states, 1 for the start state, 1 for the accepting states, 3 for the transitions). See [[0-toolkit/06-how-exams-are-graded|how exams are graded]].
>
> **Answer.** (a) DFA on $\{s_1\}\cup(\Sigma\times Q)$: remember the first symbol $a$, run $M$ on the rest, and accept $(a,q)$ iff $\delta(q,a)\in A$ (and $s_1$ iff $s\in A$). (b) NFA that guesses the last symbol $a$ and feeds it to $M$ first; on reading $a$ in a state $(a,q)$ with $q\in A$ it may move to the accepting dead end $f$ (and $s_2$ accepts iff $s\in A$).

### 4.9 Switching off the last 1

> [!hard] Hard · language transformations · DFA design · NFA design
> For a binary string $w$, let $\textsf{off}(w)$ be $w$ with its *last* $\mathtt{1}$ changed to $\mathtt{0}$; if $w$ has no $\mathtt{1}$, then $\textsf{off}(w) = w$. For example $\textsf{off}(\mathtt{0110}) = \mathtt{0100}$, $\textsf{off}(\mathtt{1011}) = \mathtt{1010}$ and $\textsf{off}(\mathtt{000}) = \mathtt{000}$. (Read as a binary number, $\textsf{off}$ clears the lowest set bit.) Let $L\subseteq\{\mathtt{0},\mathtt{1}\}^*$ be an arbitrary regular language with DFA $M = (\Sigma, Q, s, A, \delta)$.
>
> (a) Prove that $\textsf{OffPre}(L) := \{w \mid \textsf{off}(w)\in L\}$ is regular: a formal description of a DFA or NFA in terms of $M$, and an English explanation of its states and accepting states.
>
> (b) Do the same for $\textsf{OffImg}(L) := \{\textsf{off}(w) \mid w\in L\}$.
>
> *Source: original.*

> [!hint]- Hint
> (a) Check that $\textsf{off}(x\mathtt{0}) = \textsf{off}(x)\,\mathtt{0}$ and $\textsf{off}(x\mathtt{1}) = x\mathtt{0}$. A machine reading $w$ that knows where $M$ is after $w$ *and* after $\textsf{off}(w)$ can update both. (Alternatively: guess which $\mathtt{1}$ is the last one.)
>
> (b) Reading $y = \textsf{off}(w)$, guess which $\mathtt{0}$ of $y$ was the last $\mathtt{1}$ of $w$; after it only 0s may follow. Do not forget the strings $w$ with no $\mathtt{1}$ at all.

> [!solution]- Solution
> **Idea.** $\textsf{off}$ changes one symbol, but while reading $w$ we cannot tell which $\mathtt{1}$ is the last. A DFA can hedge by running $M$ on two strings at once; an NFA guesses the position and then checks the guess.
>
> **(a)** By definition, $\textsf{off}(\varepsilon) = \varepsilon$; $\textsf{off}(x\mathtt{0}) = \textsf{off}(x)\,\mathtt{0}$, because appending a $\mathtt{0}$ does not change which $\mathtt{1}$ is last; and $\textsf{off}(x\mathtt{1}) = x\mathtt{0}$, because the new $\mathtt{1}$ is the last one. Let $M_1 = (\Sigma, Q_1, s_1, A_1, \delta_1)$ be the **DFA** with
> $$
> \begin{aligned}
> Q_1 &= Q\times Q, \qquad s_1 = (s, s),\\
> \delta_1\big((p,q),\mathtt{0}\big) &= \big(\delta(p,\mathtt{0}),\ \delta(q,\mathtt{0})\big),\\
> \delta_1\big((p,q),\mathtt{1}\big) &= \big(\delta(p,\mathtt{1}),\ \delta(p,\mathtt{0})\big),\\
> A_1 &= \{(p,q) \mid q\in A\}.
> \end{aligned}
> $$
> *In English:* after reading $w$, the state is $(p,q)$ with $p = \delta^*(s,w)$ ("where $M$ is on $w$ itself") and $q = \delta^*(s,\textsf{off}(w))$ ("where $M$ is on $\textsf{off}(w)$"). The transitions are the three identities: a $\mathtt{0}$ extends both strings; a $\mathtt{1}$ extends $w$, while $\textsf{off}(w\mathtt{1}) = w\mathtt{0}$, so the new second component is $\delta(p,\mathtt{0})$, the state of $M$ on $w\mathtt{0}$. A string is accepted iff $\textsf{off}(w)\in L$, that is, iff $q\in A$. (A short induction on $w$ proves the invariant.)
>
> *Alternative (NFA).* Guess the last $\mathtt{1}$, with states $(q,\textsf{none})$ (no $\mathtt{1}$ read yet), $(q,\textsf{some})$ (a $\mathtt{1}$ read, the last one still to come) and $(q,\textsf{done})$ (the guessed last $\mathtt{1}$ was fed to $M$ as a $\mathtt{0}$; only 0s may follow). Accept $(q,\textsf{none})$ and $(q,\textsf{done})$ with $q\in A$, but never $(q,\textsf{some})$: there the input contained a $\mathtt{1}$ that was not switched off.
>
> **(b)** $y\in\textsf{OffImg}(L)$ iff either $y$ has no $\mathtt{1}$ and $y\in L$ (take $w = y$), or $y = x\,\mathtt{0}\,\mathtt{0}^k$ with $x\,\mathtt{1}\,\mathtt{0}^k\in L$. Let $M_2 = (\Sigma, Q_2, s_2, A_2, \delta_2)$ be the **NFA** with $Q_2 = Q\times\{\textsf{none},\textsf{some},\textsf{done}\}$, $s_2 = (s,\textsf{none})$, no $\varepsilon$-transitions, and for $\pi\in\{\textsf{none},\textsf{some}\}$:
> $$
> \begin{aligned}
> \delta_2\big((q,\pi),\mathtt{0}\big) &= \big\{(\delta(q,\mathtt{0}),\pi),\ (\delta(q,\mathtt{1}),\textsf{done})\big\},\\
> \delta_2\big((q,\pi),\mathtt{1}\big) &= \big\{(\delta(q,\mathtt{1}),\textsf{some})\big\},\\
> \delta_2\big((q,\textsf{done}),\mathtt{0}\big) &= \big\{(\delta(q,\mathtt{0}),\textsf{done})\big\},\\
> \delta_2\big((q,\textsf{done}),\mathtt{1}\big) &= \varnothing,\\
> A_2 &= \{(q,\textsf{none}) \mid q\in A\}\cup\{(q,\textsf{done}) \mid q\in A\}.
> \end{aligned}
> $$
> *In English:* in every state, $q$ is $M$'s state on the part of the guessed preimage $w$ read so far. $\textsf{none}$: no guess yet, and no $\mathtt{1}$ in the input yet. $\textsf{some}$: no guess yet, but the input has contained a $\mathtt{1}$. On a $\mathtt{0}$ the machine may guess "this $\mathtt{0}$ was the last $\mathtt{1}$ of $w$": it feeds $M$ a $\mathtt{1}$ and moves to $\textsf{done}$, where only 0s may follow (a later $\mathtt{1}$ would have been the last one). Accept in $\textsf{done}$ when $q\in A$: then $w\in L$ and $y = \textsf{off}(w)$. Accept in $\textsf{none}$ when $q\in A$: then $y$ has no $\mathtt{1}$, and $w = y\in L$ with $\textsf{off}(y) = y$. Never accept in $\textsf{some}$: there $w = y$ contains a $\mathtt{1}$, so $\textsf{off}(w)\ne y$.
>
> **Check.** $L = \Sigma^*$: $\textsf{OffPre}(L) = \Sigma^*$, and $\textsf{OffImg}(L) = \varepsilon+(\mathtt{0}+\mathtt{1})^*\mathtt{0}$, because $\textsf{off}(w)$ never ends in $\mathtt{1}$. $L = \mathtt{1}^*$: $\textsf{OffPre}(L) = \{\varepsilon\}$ and $\textsf{OffImg}(L) = \varepsilon+\mathtt{1}^*\mathtt{0}$. $\varnothing$ and $\{\varepsilon\}$ are mapped to themselves. $M_1$ and $M_2$ accept exactly these languages.
>
> **Watch out:** the tempting accepting set "every $(q,\pi)$ with $q\in A$" also accepts in $\textsf{some}$. For $L = \mathtt{1}^*$ it would accept `11`, which is not of the form $\textsf{off}(w)$ at all.
>
> **Answer.** (a) DFA on $Q\times Q$ that tracks $\big(\delta^*(s,w),\ \delta^*(s,\textsf{off}(w))\big)$: start $(s,s)$; on $\mathtt{0}$, $(p,q)\mapsto(\delta(p,\mathtt{0}),\delta(q,\mathtt{0}))$; on $\mathtt{1}$, $(p,q)\mapsto(\delta(p,\mathtt{1}),\delta(p,\mathtt{0}))$; accept iff $q\in A$. (b) NFA on $Q\times\{\textsf{none},\textsf{some},\textsf{done}\}$ that guesses which $\mathtt{0}$ was the last $\mathtt{1}$ (feeding $M$ a $\mathtt{1}$ there), then allows only 0s; it accepts $(q,\textsf{none})$ and $(q,\textsf{done})$ with $q\in A$.

### 4.10 Leading zeros to the back

> [!hard] Hard · language transformations · DFA design · NFA design
> Every binary string can be written uniquely as $w = \mathtt{0}^k x$, where $k\ge0$ and $x$ is empty or starts with $\mathtt{1}$. Let $\textsf{back}(w) := x\,\mathtt{0}^k$: the leading 0s move to the end. For example $\textsf{back}(\mathtt{00101}) = \mathtt{10100}$, $\textsf{back}(\mathtt{0011}) = \mathtt{1100}$, $\textsf{back}(\mathtt{000}) = \mathtt{000}$ and $\textsf{back}(\mathtt{110}) = \mathtt{110}$. Let $L\subseteq\{\mathtt{0},\mathtt{1}\}^*$ be an arbitrary regular language with DFA $M = (\Sigma, Q, s, A, \delta)$.
>
> (a) Prove that $\textsf{BackPre}(L) := \{w \mid \textsf{back}(w)\in L\}$ is regular: a formal description of a DFA or NFA, and an English explanation of its states and accepting states.
>
> (b) Do the same for $\textsf{BackImg}(L) := \{\textsf{back}(w) \mid w\in L\}$.
>
> *Source: original.*

> [!hint]- Hint
> (a) The leading 0s are read first but must be fed to $M$ last. Their number is unbounded, but their *effect* is not: store the function $q\mapsto\delta^*(q,\mathtt{0}^k)$ from $Q$ to $Q$. (Or guess the state $M$ will be in when they arrive, as in the proof that $\textsf{half}(L)$ is regular.)
>
> (b) Reading $y = x\,\mathtt{0}^k$, the machine must feed $M$ the final $\mathtt{0}^k$ first. Guess $p = \delta^*(s,\mathtt{0}^k)$ at the start, run $M$ from $p$ on $x$, and verify $p$ on the final 0s.

> [!solution]- Solution
> **Idea.** This is the block version of 4.8: an unbounded block of 0s moves from the front to the back. A finite machine cannot store the block, but it can store what the block does to $M$ (a function $Q\to Q$), or guess a state of $M$ and verify the guess later.
>
> **(a)** Write $Q^Q$ for the set of all functions $\tau\colon Q\to Q$, $\mathrm{id}$ for the identity function, and $\delta_{\mathtt{0}}(q) := \delta(q,\mathtt{0})$. Let $M_1 = (\Sigma, Q_1, s_1, A_1, \delta_1)$ be the **DFA** with
> $$
> \begin{aligned}
> Q_1 &= Q^Q\cup(Q^Q\times Q), \qquad s_1 = \mathrm{id},\\
> \delta_1(\tau,\mathtt{0}) &= \delta_{\mathtt{0}}\circ\tau, \qquad \delta_1(\tau,\mathtt{1}) = \big(\tau,\ \delta(s,\mathtt{1})\big),\\
> \delta_1\big((\tau,q),a\big) &= \big(\tau,\ \delta(q,a)\big)\quad\text{for } a\in\Sigma,\\
> A_1 &= \{\tau \mid \tau(s)\in A\}\cup\{(\tau,q) \mid \tau(q)\in A\}.
> \end{aligned}
> $$
> *In English:* a state $\tau$ means "so far only 0s, say $k$ of them, and $\tau(q) = \delta^*(q,\mathtt{0}^k)$ is where those 0s will take $M$ from any state $q$"; each further $\mathtt{0}$ composes one more $\delta_{\mathtt{0}}$. The first $\mathtt{1}$ starts $x$: a state $(\tau,q)$ means "the leading 0s act as $\tau$, and $M$, started at $s$ on the part of $x$ read so far, is in $q$". At the end, $\textsf{back}(w) = x\,\mathtt{0}^k$ takes $M$ to $\tau(\delta^*(s,x))$, so $(\tau,q)$ accepts iff $\tau(q)\in A$. If $w = \mathtt{0}^k$ has no $\mathtt{1}$, then $\textsf{back}(w) = w$ and $\tau$ accepts iff $\tau(s) = \delta^*(s,\mathtt{0}^k)\in A$. $Q_1$ is finite: at most $\lvert Q\rvert^{\lvert Q\rvert}(1+\lvert Q\rvert)$ states.
>
> *Alternative (NFA).* Guess $r = \delta^*(s,x)$ at the start; run $M$ from $r$ on the leading 0s; at the first $\mathtt{1}$ start a second copy of $M$ at $s$ on $x$. Accept iff the second copy ends at $r$ and the first one ended in $A$; if the input has no $\mathtt{1}$, the guess must be $r = s$.
>
> **(b)** $y\in\textsf{BackImg}(L)$ iff $y\in\mathtt{0}^*\cap L$ (take $w = y$), or $y = x\,\mathtt{0}^k$ with $x$ starting with $\mathtt{1}$ and $\mathtt{0}^k x\in L$. In particular every string in $\textsf{BackImg}(L)$ starts with $\mathtt{1}$ or has no $\mathtt{1}$. Let $M_2 = (\Sigma, Q_2, s_2, A_2, \delta_2)$ be the **NFA** with
> $$
> Q_2 = \{s_2\}\cup(\{\textsf{zeros}\}\times Q)\cup(\{\textsf{body}\}\times Q\times Q)\cup(\{\textsf{tail}\}\times Q\times Q),
> $$
> start state $s_2$, the following transitions for all $p, q, r\in Q$ and $a\in\Sigma$ (all others are $\varnothing$),
> $$
> \begin{aligned}
> \delta_2(s_2,\varepsilon) &= \{(\textsf{zeros}, s)\},\\
> \delta_2(s_2,\mathtt{1}) &= \{(\textsf{body}, p, \delta(p,\mathtt{1})) \mid p\in Q\},\\
> \delta_2\big((\textsf{zeros},q),\mathtt{0}\big) &= \{(\textsf{zeros},\delta(q,\mathtt{0}))\},\\
> \delta_2\big((\textsf{body},p,q),a\big) &= \{(\textsf{body},p,\delta(q,a))\},\\
> \delta_2\big((\textsf{body},p,q),\varepsilon\big) &= \{(\textsf{tail},p,s)\}\quad\text{if } q\in A,\\
> \delta_2\big((\textsf{tail},p,r),\mathtt{0}\big) &= \{(\textsf{tail},p,\delta(r,\mathtt{0}))\},
> \end{aligned}
> $$
> and accepting states $A_2 = \{(\textsf{zeros},q) \mid q\in A\}\cup\{(\textsf{tail},p,p) \mid p\in Q\}$.
>
> *In English:* $(\textsf{zeros},q)$: the input so far has no $\mathtt{1}$ and we bet it never will, so the preimage is the input itself; $q = \delta^*(s,y)$, and we accept iff $q\in A$. Alternatively, on a first symbol $\mathtt{1}$ the machine guesses $p$, the state of $M$ after the leading 0s of the preimage, and enters $(\textsf{body},p,q)$: "reading $x$; $M$, started at $p$ on the part of $x$ read so far, is in $q$". Whenever that copy of $M$ accepts, the machine may guess that $x$ is over (the $\varepsilon$-move). $(\textsf{tail},p,r)$: "reading the 0s that were the leading 0s of $w$; $M$, started at $s$ on them, is in $r$". Accept iff $r = p$: then the guess was right, and $\delta^*(s,\mathtt{0}^k x) = \delta^*(p,x)\in A$.
>
> **Check.** $L = \mathtt{1}\mathtt{0}^*$: $\textsf{BackPre}(L) = \mathtt{0}^*\mathtt{1}\mathtt{0}^*$ (exactly one 1) and $\textsf{BackImg}(L) = \mathtt{1}\mathtt{0}^*$. $L = \mathtt{0}^*\mathtt{1}$: $\textsf{BackPre}(L) = \{\mathtt{1}\}$ and $\textsf{BackImg}(L) = \mathtt{1}\mathtt{0}^*$. $L = \Sigma^*$: $\textsf{BackImg}(L) = \mathtt{0}^*+\mathtt{1}(\mathtt{0}+\mathtt{1})^*$. $\varnothing$, $\{\varepsilon\}$ and $\mathtt{1}^*$ are mapped to themselves by both. $M_1$ and $M_2$ accept exactly these languages.
>
> **Watch out:** the split point in (b) must be a guess. The 0s at the end of $y$ need not all be leading 0s of the preimage: $\textsf{back}(\mathtt{010}) = \mathtt{100}$, where $x = \mathtt{10}$ itself ends in a $\mathtt{0}$. And without the $\textsf{zeros}$ branch the machine misses $L\cap\mathtt{0}^*$: for $L = \mathtt{0}^*$ it would accept nothing, although $\textsf{BackImg}(\mathtt{0}^*) = \mathtt{0}^*$.
>
> **Answer.** (a) DFA on $Q^Q\cup(Q^Q\times Q)$: while reading the leading 0s keep $\tau = \delta^*(\cdot,\mathtt{0}^k)$; from the first $\mathtt{1}$ on keep $\tau$ and run $M$ from $s$ on $x$; accept $\tau$ iff $\tau(s)\in A$ and $(\tau,q)$ iff $\tau(q)\in A$. (b) NFA that either runs $M$ on an all-0 input (the $\textsf{zeros}$ branch), or guesses $p = \delta^*(s,\mathtt{0}^k)$, runs $M$ from $p$ on $x$, jumps by $\varepsilon$ to the tail when $M$ accepts, and accepts iff $M$ from $s$ on the remaining 0s ends exactly at $p$.

### Sources for this page
Problems 4.1, 4.2, 4.5, 4.6 and 4.8–4.10 are original; the transformations $\textsf{rot}$, $\textsf{off}$ and $\textsf{back}$ were made up for this page in the format of the exams' two-part transformation problem ([[1-models-of-computation/04-nondeterministic-automata#49-regular-language-transformations|§4.9]]). Classic textbook-style exercises, in our own words: the NFA for "the last symbol appeared earlier" (4.3), the third-symbol-from-the-end blow-up in 4.1(e), the Kleene-star slip of 4.4, and eliminating the two-parity DFA (4.7). None is taken from a course exam or homework. Every NFA, DFA, run, subset-construction table, Thompson count and regular expression, and every transformation (implemented for an arbitrary DFA and tested on 300 random DFAs with 2–4 states plus the edge cases $\varnothing$, $\{\varepsilon\}$, $\mathtt{1}^*$ and $\Sigma^*$), is checked by `tools/practice/checks/ch04.py`.

*Previous: [[practice/03-finite-state-machines|Chapter 3 practice]] · next: [[practice/05-context-free-languages|Chapter 5 practice]] · [[practice/index|all practice]]*
