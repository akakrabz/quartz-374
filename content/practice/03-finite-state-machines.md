---
title: "Practice — Chapter 3: Finite-state machines"
description: "10 practice problems (4 easy, 3 medium, 3 hard) on DFA design and correctness, the product construction, fooling sets and minimization, each with a folded hint and a worked solution."
tags: [practice, regular, midterm-1]
chapter: 3
---

*Practice for [[1-models-of-computation/03-finite-state-machines|Chapter 3]] · concepts: [[concepts/dfa]] · [[concepts/product-construction]] · [[concepts/fooling-sets]] · [[concepts/dfa-minimization]] · all practice: [[practice/index|hub]] · by difficulty: [[practice/easy|easy]] · [[practice/medium|medium]] · [[practice/hard|hard]] · [[practice/topics|by topic]]*

Work each problem on paper first. Open the **hint** only when stuck, and the **solution** only after you have an answer you would hand in. Every automaton, regular expression and fooling set in the solutions has been checked by a script. All strings are over $\{\mathtt{0},\mathtt{1}\}$; in transition tables, → marks the start state and \* the accepting states.

## Easy

### 3.1 Closure and fooling-set verdicts

> [!easy] Easy · true or false · closure properties · fooling sets
> Let $L$, $L'$, $L_1$, $L_2$ be languages over $\Sigma = \{\mathtt{0},\mathtt{1}\}$. Answer each statement **Yes** (always true) or **No**, with a one-sentence reason; for a No, give a counterexample.
>
> (a) If $L\oplus L'$ is regular, then $L$ and $L'$ are both regular.
>
> (b) If $L_1$ is regular and $L_2$ is not, then $L_1\oplus L_2$ is not regular.
>
> (c) If neither $L$ nor $L'$ is regular, then $L\cap L'$ is not regular.
>
> (d) Every DFA that accepts $\{w\in\Sigma^* \mid \lvert w\rvert = 5\}$ has at least 7 states.
>
> (e) If $L$ is not regular, then $L^*$ is not regular.
>
> (f) If a DFA with $n$ states accepts at least one string, then it accepts some string of length less than $n$.
>
> *Source: original.*

> [!hint]- Hint
> Closure properties say nothing about non-regular inputs, so for a No look for a counterexample built from $\{\mathtt{0}^n\mathtt{1}^n \mid n\ge0\}$, its complement, or $\varnothing$. For (b), write $L_2$ in terms of $L_1$ and $L_1\oplus L_2$.

> [!solution]- Solution
> **(a) No.** Take $L = L' = \{\mathtt{0}^n\mathtt{1}^n \mid n\ge0\}$, which is not regular (Lemma 3.6); then $L\oplus L' = \varnothing$, which is regular.
>
> **(b) Yes.** $L_2 = L_1\oplus(L_1\oplus L_2)$, so if $L_1\oplus L_2$ were regular, $L_2$ would be regular by closure under $\oplus$ (Corollary 3.4).
>
> **(c) No.** $L = \{\mathtt{0}^n\mathtt{1}^n \mid n\ge0\}$ and $L' = \overline{L}$ are both non-regular (if $\overline{L}$ were regular, so would be its complement $L$), but $L\cap L' = \varnothing$.
>
> **(d) Yes.** The seven strings $\varepsilon,\mathtt{0},\mathtt{0}^2,\dots,\mathtt{0}^6$ form a fooling set: for $0\le i<j\le6$ the suffix $z = \mathtt{0}^{5-i}$ makes $\mathtt{0}^iz$ exactly 5 symbols long and $\mathtt{0}^jz$ longer. (Seven states also suffice: count the symbols up to 5, plus a dump state for longer strings.)
>
> **(e) No.** $L = \{\mathtt{0}^{2^n} \mid n\ge0\}$ is not regular (Lemma 3.8), but $\mathtt{0} = \mathtt{0}^{2^0}\in L$ and $L\subseteq\mathtt{0}^*$, so $L^* = \mathtt{0}^*$, which is regular.
>
> **(f) Yes.** The walk of a *shortest* accepted string never repeats a state (otherwise cutting out the loop between the two visits would leave a shorter accepted string), so it visits at most $n$ states and reads at most $n-1$ symbols.
>
> **Watch out:** in (a), (c) and (e) the closure theorems do not apply — they promise regular outputs only from regular inputs. The useful move is the one in (b): undo the operation with a language you know is regular.
>
> **Answer.** (a) No (b) Yes (c) No (d) Yes (e) No (f) Yes.

### 3.2 A bounded counter

> [!easy] Easy · DFA design
> Let $L$ be the set of strings $w$ such that every prefix $p$ of $w$ (including $\varepsilon$ and $w$ itself) satisfies $\lvert\#(\mathtt{0},p)-\#(\mathtt{1},p)\rvert\le2$. For example, `0101` and `001101` are in $L$, but `0001` is not: its prefix `000` has three more 0s than 1s.
>
> (a) Give a DFA for $L$ with mnemonic state names, as a transition table with a column for the meaning of each state. No proof is required.
>
> (b) In one sentence: why does the same idea not give a DFA for $\{w \mid \#(\mathtt{0},w) = \#(\mathtt{1},w)\}$?
>
> *Source: textbook exercise style.*

> [!hint]- Hint
> Write the algorithm first: one variable $d = \#(\mathtt{0},p)-\#(\mathtt{1},p)$ for the prefix $p$ read so far. Which values of $d$ matter before the answer is certainly No?

> [!solution]- Solution
> **Idea.** Scan once, keeping $d$, the number of 0s minus the number of 1s read so far: a `0` adds 1 and a `1` subtracts 1. The first time $\lvert d\rvert$ reaches 3, some prefix has failed and nothing later can repair that, so from then on the machine only needs to remember "failed". That is five values of $d$ plus a dump state.
>
> **(a)**
>
> | | state | meaning (input read so far) | $\mathtt{0}$ | $\mathtt{1}$ |
> |---|---|---|---|---|
> | \* | $d_{-2}$ | no prefix has failed; two more 1s than 0s | $d_{-1}$ | $\mathit{dead}$ |
> | \* | $d_{-1}$ | no prefix has failed; one more 1 than 0s | $d_{0}$ | $d_{-2}$ |
> | → \* | $d_{0}$ | no prefix has failed; as many 0s as 1s | $d_{1}$ | $d_{-1}$ |
> | \* | $d_{1}$ | no prefix has failed; one more 0 than 1s | $d_{2}$ | $d_{0}$ |
> | \* | $d_{2}$ | no prefix has failed; two more 0s than 1s | $\mathit{dead}$ | $d_{1}$ |
> | | $\mathit{dead}$ | some prefix has failed (dump state) | $\mathit{dead}$ | $\mathit{dead}$ |
>
> **Check.** `001101` visits $d_0, d_1, d_2, d_1, d_0, d_1, d_0$ and is accepted; `0001` visits $d_0, d_1, d_2, \mathit{dead}, \mathit{dead}$ and is rejected. The empty string stays in $d_0$ and is accepted, as it should be: its only prefix is $\varepsilon$, with difference 0.
>
> **(b)** There the difference is unbounded, so the counter would need a state for every integer; in fact $\mathtt{0}^*$ is an infinite fooling set for that language (the suffix $\mathtt{1}^i$ separates $\mathtt{0}^i$ from $\mathtt{0}^j$).
>
> **Answer.** Six states: $d_{-2},\dots,d_{2}$ (no prefix has failed, and the subscript is the current value of $d$; all accepting; start $d_0$) and a dump state $\mathit{dead}$. Reading `0` moves $d_k$ to $d_{k+1}$, reading `1` moves it to $d_{k-1}$, and stepping outside $[-2,2]$ goes to $\mathit{dead}$.

### 3.3 Prefixes of a pattern

> [!easy] Easy · fooling sets · Myhill–Nerode
> Let $L = \{w \mid w \text{ contains the substring } \mathtt{0110}\}$.
>
> (a) Prove that every DFA that accepts $L$ has at least 5 states.
>
> (b) A student adds `01101` to your five strings, hoping to prove that 6 states are needed. Why must this fail?
>
> *Source: original.*

> [!hint]- Hint
> A DFA hunting for `0110` must remember how much of the pattern it has just seen. Try the prefixes of `0110`, and a suffix that completes the longer of the two strings.

> [!solution]- Solution
> **(a)** Let $F = \{\varepsilon,\mathtt{0},\mathtt{01},\mathtt{011},\mathtt{0110}\}$, the five prefixes of the pattern $P = \mathtt{0110}$. Let $x$ and $y$ be distinct strings in $F$, named so that $\lvert x\rvert = i < j = \lvert y\rvert$ (a distinguishing suffix works for the pair in either order, so this loses nothing). Let $z$ be the last $4-j$ symbols of $P$. Then $yz = P\in L$. And $xz\notin L$, because $\lvert xz\rvert = i+4-j < 4$ is too short to contain `0110`. So $F$ is a fooling set of size 5, and every DFA for $L$ has at least 5 states.
>
> For instance, $z = \mathtt{10}$ distinguishes `0` and `01`: `010` $\notin L$ but `0110` $\in L$.
>
> **(b)** `0110` and `01101` both contain the pattern, so $\mathtt{0110}z$ and $\mathtt{01101}z$ are both in $L$ for *every* $z$: no suffix distinguishes them. In fact no fooling set for $L$ has 6 strings, because the 5-state DFA below accepts $L$, and by the [[1-models-of-computation/03-finite-state-machines#39-the-myhillnerode-theorem|Myhill–Nerode theorem]] the largest fooling set is exactly as large as the smallest DFA. State $q_u$ means "no `0110` yet, and $u$ is the longest suffix of the input that is a prefix of `0110`":
>
> | | state | $\mathtt{0}$ | $\mathtt{1}$ |
> |---|---|---|---|
> | → | $q_\varepsilon$ | $q_{\mathtt{0}}$ | $q_\varepsilon$ |
> | | $q_{\mathtt{0}}$ | $q_{\mathtt{0}}$ | $q_{\mathtt{01}}$ |
> | | $q_{\mathtt{01}}$ | $q_{\mathtt{0}}$ | $q_{\mathtt{011}}$ |
> | | $q_{\mathtt{011}}$ | $\mathit{found}$ | $q_\varepsilon$ |
> | \* | $\mathit{found}$ | $\mathit{found}$ | $\mathit{found}$ |
>
> **Answer.** (a) $F = \{\varepsilon,\mathtt{0},\mathtt{01},\mathtt{011},\mathtt{0110}\}$: for $\lvert x\rvert<\lvert y\rvert$, the suffix that completes $y$ to `0110` leaves $xz$ shorter than 4. (b) `0110` and `01101` stay in $L$ under every extension, so nothing distinguishes them; a 5-state DFA exists, so 5 is the exact minimum.

### 3.4 The forgotten second branch

> [!easy] Easy · find the error · fooling sets · non-regularity
> Let $L = \{\mathtt{0}^a\mathtt{1}^b \mid a,b\ge0 \text{ and } (b = a \text{ or } b = 2a)\}$. A student writes:
>
> *"Let $F = \mathtt{0}^*$. Let $x$ and $y$ be arbitrary distinct strings in $F$; then $x = \mathtt{0}^i$ and $y = \mathtt{0}^j$ for some integers $i\ne j$. Let $z = \mathtt{1}^i$. Then $xz = \mathtt{0}^i\mathtt{1}^i\in L$, because $b = a$. And $yz = \mathtt{0}^j\mathtt{1}^i\notin L$, because $j\ne i$. So $F$ is a fooling set for $L$, and since $F$ is infinite, $L$ is not regular."*
>
> (a) Which sentence is wrong? Give a concrete pair $x, y\in F$ that this $z$ does not distinguish.
>
> (b) Repair the proof. (Its conclusion is true.)
>
> *Source: original.*

> [!hint]- Hint
> Read the definition of $L$ again: in how many ways can $\mathtt{0}^j\mathtt{1}^i$ belong to $L$?

> [!solution]- Solution
> **(a) The slip is "$yz\notin L$, because $j\ne i$".** That rules out only the branch $b = a$. The string $yz = \mathtt{0}^j\mathtt{1}^i$ is also in $L$ when $i = 2j$. For example, $x = \mathtt{00}$ and $y = \mathtt{0}$ ($i = 2$, $j = 1$) get $z = \mathtt{11}$, and both $xz = \mathtt{0011}$ and $yz = \mathtt{011}$ are in $L$. (The pair is still distinguishable — by $z = \mathtt{1}$, for instance: `001` $\notin L$ but `01` $\in L$ — but not by the suffix the proof chose.)
>
> **(b) Fix: shrink $F$ so that the bad case cannot happen.** Let $F = \mathtt{0}(\mathtt{00})^*$, the strings of 0s of odd length. Let $x$ and $y$ be arbitrary distinct strings in $F$; then $x = \mathtt{0}^i$ and $y = \mathtt{0}^j$ for some odd integers $i\ne j$. Let $z = \mathtt{1}^i$. Then $xz = \mathtt{0}^i\mathtt{1}^i\in L$, because $b = a$. And $yz = \mathtt{0}^j\mathtt{1}^i\notin L$: the branch $b = a$ would need $i = j$, and the branch $b = 2a$ would need $i = 2j$, which is even, while $i$ is odd. So $F$ is a fooling set for $L$, and since $F$ is infinite, $L$ is not regular.
>
> **Another fix: keep $F = \mathtt{0}^*$ and split cases.** If $i\ne 2j$, the student's $z = \mathtt{1}^i$ works. If $i = 2j$, then $j\ge1$ (otherwise $i = j = 0$), and $z = \mathtt{1}^j$ works: $yz = \mathtt{0}^j\mathtt{1}^j\in L$, while $xz = \mathtt{0}^{2j}\mathtt{1}^j\notin L$, because $j = 2j$ and $j = 4j$ are both false for $j\ge1$.
>
> **Watch out:** "$yz\notin L$" must rule out *every* way of being in $L$. When the definition contains an "or", check each branch — a proof that skips one looks complete and still loses the points for that half.
>
> **Answer.** (a) "$yz\notin L$, because $j\ne i$" ignores the branch $b = 2a$: for $x = \mathtt{00}$, $y = \mathtt{0}$, $z = \mathtt{11}$, both `0011` and `011` are in $L$. (b) Use $F = \mathtt{0}(\mathtt{00})^*$ with $z = \mathtt{1}^i$, where $i = 2j$ is impossible because $i$ is odd; or keep $\mathtt{0}^*$ and use $z = \mathtt{1}^j$ when $i = 2j$.

## Medium

### 3.5 Read a DFA, then prove it

> [!medium] Medium · DFA proof · string induction
> For a string $w$, let $\#(\mathtt{01},w)$ be the number of occurrences of `01` in $w$ as a substring. The DFA $M$ has start state $A$, accepting states $\{A,B\}$ and this transition function:
>
> | $\delta$ | $\mathtt{0}$ | $\mathtt{1}$ |
> |---|---|---|
> | $A$ | $B$ | $A$ |
> | $B$ | $B$ | $C$ |
> | $C$ | $D$ | $C$ |
> | $D$ | $D$ | $A$ |
>
> Prove that $L(M) = \{w \mid \#(\mathtt{01},w)\text{ is even}\}$:
>
> (a) give each state $q$ a meaning — a property $P_q$ of the input read so far — such that $\delta^*(A,w) = q$ exactly when $w$ has $P_q$;
>
> (b) prove your claim by induction on $w$, and conclude.
>
> *Source: original.*

> [!hint]- Hint
> Two things matter: the parity of $\#(\mathtt{01},\cdot)$ so far, and whether the last symbol read is a `0` (half of a possible new `01`). Peel off the *last* symbol, $w = xa$, so that you need the claim only from the start state.

> [!solution]- Solution
> **Idea.** The four states record two bits: the parity of $\#(\mathtt{01},w)$, and whether $w$ ends in `0`. A new `01` appears exactly when a `1` is read right after a `0`. The proof follows the template of [[1-models-of-computation/03-finite-state-machines#33-proving-a-dfa-correct|§3.3]].
>
> **(a) Meanings.**
>
> | state | $P_q$: the input $w$ read so far … | accepting |
> |---|---|---|
> | $A$ | has an even $\#(\mathtt{01},w)$ and does not end in `0` (it is empty or ends in `1`) | yes |
> | $B$ | has an even $\#(\mathtt{01},w)$ and ends in `0` | yes |
> | $C$ | has an odd $\#(\mathtt{01},w)$ and does not end in `0` | no |
> | $D$ | has an odd $\#(\mathtt{01},w)$ and ends in `0` | no |
>
> Every string has exactly one of the four properties, so it is enough to prove: **for every string $w$, $\delta^*(A,w)$ is the state whose property $w$ has.**
>
> **(b) A fact first.** For every string $x$ and symbol $a$: $\#(\mathtt{01},xa) = \#(\mathtt{01},x)+1$ if $x$ ends in `0` and $a = \mathtt{1}$, and $\#(\mathtt{01},xa) = \#(\mathtt{01},x)$ otherwise. Indeed, an occurrence of `01` in $xa$ either lies inside $x$ or uses the last two symbols, and those two symbols are `01` exactly when $x$ ends in `0` and $a = \mathtt{1}$.
>
> **Proof.** Let $w$ be an arbitrary string, and assume that for every string $x$ shorter than $w$, $\delta^*(A,x)$ is the state whose property $x$ has. There are two cases.
> - **$w = \varepsilon$.** $\delta^*(A,\varepsilon) = A$ by the definition of $\delta^*$, and $\varepsilon$ has $P_A$: $\#(\mathtt{01},\varepsilon) = 0$ is even, and $\varepsilon$ does not end in `0`.
> - **$w = xa$** for some string $x$ and symbol $a$. Then $\delta^*(A,w) = \delta(\delta^*(A,x),a)$, and by the induction hypothesis $\delta^*(A,x) = q$, where $x$ has $P_q$. The fact gives the property of $xa$ in each of the eight combinations of $q$ and $a$, and in each one $\delta(q,a)$ is the matching state:
>
> | $x$ has | $a$ | so $xa$ has | $\delta(q,a)$ |
> |---|---|---|---|
> | $P_A$ | `0` | even, ends in `0`: $P_B$ | $B$ ✓ |
> | $P_A$ | `1` | even (no new `01`: $x$ does not end in `0`), ends in `1`: $P_A$ | $A$ ✓ |
> | $P_B$ | `0` | even, ends in `0`: $P_B$ | $B$ ✓ |
> | $P_B$ | `1` | odd (one new `01`), ends in `1`: $P_C$ | $C$ ✓ |
> | $P_C$ | `0` | odd, ends in `0`: $P_D$ | $D$ ✓ |
> | $P_C$ | `1` | odd (no new `01`), ends in `1`: $P_C$ | $C$ ✓ |
> | $P_D$ | `0` | odd, ends in `0`: $P_D$ | $D$ ✓ |
> | $P_D$ | `1` | even (one new `01`), ends in `1`: $P_A$ | $A$ ✓ |
>
> In both cases $\delta^*(A,w)$ is the state whose property $w$ has. $\blacksquare$
>
> **Conclusion.** $w\in L(M)\iff\delta^*(A,w)\in\{A,B\}\iff w$ has $P_A$ or $P_B\iff\#(\mathtt{01},w)$ is even.
>
> **Check.** `00110` contains one `01`: $M$ visits $A,B,B,C,C,D$ and rejects. `0101` contains two: $M$ visits $A,B,C,D,A$ and accepts.
>
> **Watch out:** peeling the *first* symbol ($w = ax$) would need the claim from every state, because $\delta^*(A,ax) = \delta^*(\delta(A,a),x)$ runs $x$ from $\delta(A,a)$. And $\#(\mathtt{01},\cdot)$ is not additive: $\#(\mathtt{01},xy)$ is one more than $\#(\mathtt{01},x)+\#(\mathtt{01},y)$ when the seam is a `01` — that is exactly what the fact keeps track of.
>
> **Answer.** $A$: even and not ending in `0`; $B$: even and ending in `0`; $C$: odd and not ending in `0`; $D$: odd and ending in `0` (parity of $\#(\mathtt{01},w)$). Induction on $w = xa$, using that reading $a$ adds a `01` exactly when $x$ ends in `0` and $a = \mathtt{1}$, proves these meanings; since $A$ and $B$ are the accepting states, $L(M) = \{w \mid \#(\mathtt{01},w)\text{ is even}\}$.

### 3.6 A product, written formally

> [!medium] Medium · product construction · closure properties · DFA design
> Let $L_1$ be the set of strings that start with `1`, let $L_2 = \{w \mid \#(\mathtt{1},w)\text{ is even}\}$, and let $L = L_1\cap L_2$.
>
> (a) Give DFAs $M_1$ for $L_1$ and $M_2$ for $L_2$ with mnemonic state names.
>
> (b) Describe the product DFA $M = (\Sigma,Q,s,A,\delta)$ for $L$ formally. Then give the transition table of its reachable states, and run it on `1001` and on `0110`.
>
> (c) Changing only the accepting set, give DFAs for $L_1\cup L_2$ and for $L_1\setminus L_2$.
>
> (d) Two reachable states of $M$ can be merged without changing $L(M)$. Which two, and why?
>
> *Source: original.*

> [!hint]- Hint
> A product state is a pair (state of $M_1$, state of $M_2$), and $M$ runs both machines in lockstep. Only the accepting set depends on whether you want $\cap$, $\cup$ or $\setminus$. For (d), look for states from which no accepting state can be reached.

> [!solution]- Solution
> **Idea.** $M_1$ remembers what the first symbol was, $M_2$ the parity of the number of 1s. Run both at once ([[1-models-of-computation/03-finite-state-machines#36-the-product-construction|§3.6]]) and accept when both accept.
>
> **(a)** $M_1 = (\Sigma,\{\mathit{new},\mathit{good},\mathit{bad}\},\mathit{new},\{\mathit{good}\},\delta_1)$ and $M_2 = (\Sigma,\{\mathit{even},\mathit{odd}\},\mathit{even},\{\mathit{even}\},\delta_2)$:
>
> | | $M_1$ | meaning | $\mathtt{0}$ | $\mathtt{1}$ |
> |---|---|---|---|---|
> | → | $\mathit{new}$ | nothing read yet | $\mathit{bad}$ | $\mathit{good}$ |
> | \* | $\mathit{good}$ | the first symbol was `1` | $\mathit{good}$ | $\mathit{good}$ |
> | | $\mathit{bad}$ | the first symbol was `0` | $\mathit{bad}$ | $\mathit{bad}$ |
>
> | | $M_2$ | meaning | $\mathtt{0}$ | $\mathtt{1}$ |
> |---|---|---|---|---|
> | → \* | $\mathit{even}$ | an even number of 1s so far | $\mathit{even}$ | $\mathit{odd}$ |
> | | $\mathit{odd}$ | an odd number of 1s so far | $\mathit{odd}$ | $\mathit{even}$ |
>
> **(b) The product.**
> $$
> Q := \{\mathit{new},\mathit{good},\mathit{bad}\}\times\{\mathit{even},\mathit{odd}\},\qquad s := (\mathit{new},\mathit{even}),\qquad A := \{(\mathit{good},\mathit{even})\},
> $$
> $$
> \delta\big((p,q),a\big) := \big(\delta_1(p,a),\,\delta_2(q,a)\big)\quad\text{for every } (p,q)\in Q \text{ and } a\in\Sigma.
> $$
> $Q$ has six states, but $(\mathit{new},\mathit{odd})$ is unreachable: $M_1$ is in $\mathit{new}$ only before anything is read, when the number of 1s is 0. The other five:
>
> | | state | meaning | $\mathtt{0}$ | $\mathtt{1}$ |
> |---|---|---|---|---|
> | → | $(\mathit{new},\mathit{even})$ | nothing read yet | $(\mathit{bad},\mathit{even})$ | $(\mathit{good},\mathit{odd})$ |
> | \* | $(\mathit{good},\mathit{even})$ | starts with `1`, even number of 1s | $(\mathit{good},\mathit{even})$ | $(\mathit{good},\mathit{odd})$ |
> | | $(\mathit{good},\mathit{odd})$ | starts with `1`, odd number of 1s | $(\mathit{good},\mathit{odd})$ | $(\mathit{good},\mathit{even})$ |
> | | $(\mathit{bad},\mathit{even})$ | starts with `0`, even number of 1s | $(\mathit{bad},\mathit{even})$ | $(\mathit{bad},\mathit{odd})$ |
> | | $(\mathit{bad},\mathit{odd})$ | starts with `0`, odd number of 1s | $(\mathit{bad},\mathit{odd})$ | $(\mathit{bad},\mathit{even})$ |
>
> **Check.** On `1001`, $M$ visits $(\mathit{new},\mathit{even})$, $(\mathit{good},\mathit{odd})$ three times, then $(\mathit{good},\mathit{even})$ and accepts: the string starts with `1` and has two 1s. On `0110` it visits $(\mathit{new},\mathit{even})$, $(\mathit{bad},\mathit{even})$, $(\mathit{bad},\mathit{odd})$, $(\mathit{bad},\mathit{even})$, $(\mathit{bad},\mathit{even})$ and rejects: two 1s, but it starts with `0`. The empty string stays in $(\mathit{new},\mathit{even})$ and is rejected, correctly, since it does not start with `1`.
>
> **(c)** Keep $Q$, $s$ and $\delta$, and change $A$:
> - $L_1\cup L_2$: $A := \{(p,q) \mid p = \mathit{good} \text{ or } q = \mathit{even}\} = \{(\mathit{new},\mathit{even}),(\mathit{good},\mathit{even}),(\mathit{good},\mathit{odd}),(\mathit{bad},\mathit{even})\}$;
> - $L_1\setminus L_2$: $A := \{(p,q) \mid p = \mathit{good} \text{ and } q = \mathit{odd}\} = \{(\mathit{good},\mathit{odd})\}$.
>
> **(d)** $(\mathit{bad},\mathit{even})$ and $(\mathit{bad},\mathit{odd})$. Neither is accepting, and every transition out of them stays between the two, so from either one no string leads to an accepting state: both accept the same set of continuations, namely none. Merging them into a single dump state leaves a 4-state DFA for $L$, which Moore's algorithm confirms is minimal. (For $L_1\cup L_2$ the two must stay apart, because there $(\mathit{bad},\mathit{even})$ accepts.)
>
> **Watch out:** the product construction gives a correct DFA, not a minimal one. Define $Q$ as the whole product $Q_1\times Q_2$ with $\delta$ on every pair; tabulating only the reachable states is fine, but the formal definition must not leave transitions undefined.
>
> **Grading notes.** A product construction earns its description points only if each factor is described completely (states, start, accepting states, transitions) and the product's accepting set is given explicitly; "run both machines in parallel" alone earns little ([[0-toolkit/06-how-exams-are-graded|how exams are graded]]).
>
> **Answer.** $Q = \{\mathit{new},\mathit{good},\mathit{bad}\}\times\{\mathit{even},\mathit{odd}\}$, $s = (\mathit{new},\mathit{even})$, $\delta((p,q),a) = (\delta_1(p,a),\delta_2(q,a))$, $A = \{(\mathit{good},\mathit{even})\}$; five states are reachable. For $L_1\cup L_2$: $A = \{(\mathit{new},\mathit{even}),(\mathit{good},\mathit{even}),(\mathit{good},\mathit{odd}),(\mathit{bad},\mathit{even})\}$; for $L_1\setminus L_2$: $A = \{(\mathit{good},\mathit{odd})\}$. The two $\mathit{bad}$ states merge into one dump state.

### 3.7 Squares need a marker

> [!medium] Medium · fooling sets · non-regularity
> Prove that $L = \{ww \mid w\in\{\mathtt{0},\mathtt{1}\}^*\}$, the set of strings that consist of two copies of the same string, is not regular. Use a fooling set, and write the proof in full.
>
> *Source: classic.*

> [!hint]- Hint
> Let every string of $F$ end with a marker `1`, and try the suffix $z = x$. To show $yz\notin L$, count the 1s: how many does each half of a string in $L$ get?

> [!solution]- Solution
> **Idea.** A DFA reading the first half must remember all of it. The suffix $z = x$ copies $x$, so $xz = xx\in L$ for free; a single `1` at the end of each string of $F$ marks where the copy starts, which makes $yz$ easy to rule out.
>
> **Proof.** Let $F = \mathtt{0}^*\mathtt{1} = \{\mathtt{0}^i\mathtt{1} \mid i\ge0\}$. Let $x$ and $y$ be arbitrary distinct strings in $F$; then $x = \mathtt{0}^i\mathtt{1}$ and $y = \mathtt{0}^j\mathtt{1}$ for some integers $i\ne j$. Let $z = \mathtt{0}^i\mathtt{1}$.
>
> Then $xz = \mathtt{0}^i\mathtt{1}\,\mathtt{0}^i\mathtt{1} = ww$ for $w = \mathtt{0}^i\mathtt{1}$, so $xz\in L$.
>
> And $yz = \mathtt{0}^j\mathtt{1}\,\mathtt{0}^i\mathtt{1}\notin L$. Suppose instead that $yz = uu$ for some string $u$. The two copies of $u$ contain the same number of 1s, and $yz$ contains exactly two, so $u$ contains exactly one `1`. The string $yz$ ends in `1`, so $u$ ends in `1`; therefore $u = \mathtt{0}^k\mathtt{1}$ for some $k$, and $yz = \mathtt{0}^k\mathtt{1}\,\mathtt{0}^k\mathtt{1}$. Comparing the numbers of 0s before the first `1` and between the two 1s gives $j = k$ and $i = k$, so $i = j$, a contradiction.
>
> So $z$ distinguishes $x$ and $y$, and $F$ is a fooling set for $L$. Because $F$ is infinite, $L$ is not regular. $\blacksquare$
>
> **Check.** For $i = 1$, $j = 2$: $xz = \mathtt{0101}\in L$, and $yz = \mathtt{00101}$ has odd length, so it is not in $L$. For $i = 1$, $j = 3$: $yz = \mathtt{000101}$ has halves `000` and `101`.
>
> **Watch out:** with $F = \mathtt{0}^*$ the suffix $z = x$ fails: then $yz = \mathtt{0}^{i+j}$, which is in $L$ whenever $i+j$ is even. ($\mathtt{0}^*$ can still be made to work, with $z = \mathtt{1}\mathtt{0}^i\mathtt{1}$ and the same counting argument.)
>
> **Grading notes.** 4 points for an explicit infinite set that really is a fooling set, then 2 each for an explicit $z$, for $xz\in L$ and for $yz\notin L$ — and $yz\notin L$ needs an argument for *arbitrary* $i\ne j$, not an example.
>
> **Answer.** $F = \mathtt{0}^*\mathtt{1}$ with $z = x$: for $x = \mathtt{0}^i\mathtt{1}$ and $y = \mathtt{0}^j\mathtt{1}$, $xz = (\mathtt{0}^i\mathtt{1})(\mathtt{0}^i\mathtt{1})\in L$, while $yz = \mathtt{0}^j\mathtt{1}\mathtt{0}^i\mathtt{1}$ would have to be $\mathtt{0}^k\mathtt{1}\mathtt{0}^k\mathtt{1}$, forcing $i = j$.

## Hard

### 3.8 No 00 after an 11

> [!hard] Hard · DFA design · regular expressions
> Let $L$ be the set of strings $w$ that have no substring of the form $\mathtt{11}x\mathtt{00}$ with $x\in\{\mathtt{0},\mathtt{1}\}^*$. In words: once `11` has appeared, `00` never appears afterwards. For example, `0010110` and `110101` are in $L$, but `0110100` is not.
>
> (a) Give a DFA for $L$ with mnemonic state names. No proof is required.
>
> (b) Give a regular expression for $L$, with a one-sentence explanation of each part.
>
> *Source: original.*

> [!hint]- Hint
> (a) Before the first `11`, remember whether the last symbol was `1`; after it, whether the last symbol was `0`. (b) Cut $w$ just before the first `11`. What can the part before the cut look like, and the part after it?

> [!solution]- Solution
> **Idea.** The scan has two phases. Before the first `11`, a `00` is harmless and the machine watches for `11`; from then on it watches for `00`, which is fatal. Note that `00` *before* the first `11` is allowed, as in `0010110`.
>
> **(a)**
>
> | | state | meaning: the input read so far … | $\mathtt{0}$ | $\mathtt{1}$ |
> |---|---|---|---|---|
> | → \* | $\mathit{before}$ | has no `11`, and is empty or ends in `0` | $\mathit{before}$ | $\mathit{before1}$ |
> | \* | $\mathit{before1}$ | has no `11`, and ends in `1` | $\mathit{before}$ | $\mathit{after1}$ |
> | \* | $\mathit{after1}$ | has a `11` and no `00` after it, and ends in `1` | $\mathit{after0}$ | $\mathit{after1}$ |
> | \* | $\mathit{after0}$ | has a `11` and no `00` after it, and ends in `0` | $\mathit{dead}$ | $\mathit{after1}$ |
> | | $\mathit{dead}$ | has a `00` after a `11` (dump state) | $\mathit{dead}$ | $\mathit{dead}$ |
>
> **(b)**
> $$
> (\mathtt{0}+\mathtt{10})^*\,(\mathtt{1}+\mathtt{01})^*\,(\varepsilon+\mathtt{0})
> $$
> - $(\mathtt{0}+\mathtt{10})^*$ is the part before the first `11`: every `1` in it is followed by a `0`, so it contains no `11` and does not end in `1` (a `1` just before the first `11` would make an earlier `11`).
> - $(\mathtt{1}+\mathtt{01})^*$ is the part from the first `11` on: every `0` in it is followed by a `1`, so it contains no `00`. (If $w$ has no `11` at all, this part is empty or a single final `1`.)
> - $(\varepsilon+\mathtt{0})$ allows one final `0` — the only `0` after the first `11` that need not be followed by a `1`.
>
> **Check.** `0010110` splits as `0010` · `11` · `0`, and the DFA visits $\mathit{before},\mathit{before},\mathit{before},\mathit{before1},\mathit{before},\mathit{before1},\mathit{after1},\mathit{after0}$ and accepts. `110101` is $\varepsilon$ · `110101` · $\varepsilon$, since `110101` $=$ `1`·`1`·`01`·`01`. On `0110100` the DFA reaches $\mathit{after1}$ after `011` and falls into $\mathit{dead}$ at the final `00`; the expression cannot match it either, because after the first `11` every `0` but a final one must be followed by a `1`.
>
> **Watch out:** $(\mathtt{0}+\mathtt{10})^*(\mathtt{1}+\mathtt{01})^*$ without the final $(\varepsilon+\mathtt{0})$ looks right but misses `110`, `1110`, … — infinitely many strings, which on an exam costs all of the correctness points. And "no `00` and no `11` anywhere" describes a much smaller language: `00` is fine before the first `11`.
>
> **Grading notes.** For the DFA: a start arrow, marked accepting states and a sentence about the dump state if you omit it from a drawing (2 points), correctness (6), mnemonic state names (2). For the expression: syntax (2) and correctness (8) ([[0-toolkit/06-how-exams-are-graded|how exams are graded]]).
>
> **Answer.** (a) Five states: $\mathit{before}$ (start), $\mathit{before1}$, $\mathit{after1}$, $\mathit{after0}$, all accepting, and the dump state $\mathit{dead}$, as in the table. (b) $(\mathtt{0}+\mathtt{10})^*(\mathtt{1}+\mathtt{01})^*(\varepsilon+\mathtt{0})$.

### 3.9 Three look-alike counting languages

> [!hard] Hard · non-regularity · closure properties · fooling sets
> For strings $u$ and $w$, let $\#(u,w)$ be the number of occurrences of $u$ in $w$ as a substring; overlapping occurrences count, so $\#(\mathtt{00},\mathtt{000}) = 2$. For each language below, decide whether it is regular, and prove your answer: a regular expression with a short justification if it is regular, a proof if it is not.
>
> (a) $L_a = \{w \mid \#(\mathtt{00},w) = \#(\mathtt{11},w)\}$
>
> (b) $L_b = \{w \mid \#(\mathtt{01},w) = \#(\mathtt{10},w)\}$
>
> (c) $L_c = \{w \mid \#(\mathtt{01},w) = \#(\mathtt{11},w)\}$
>
> *Source: original; part (b) is a classic exercise.*

> [!hint]- Hint
> (a) Intersect with $\mathtt{0}^*\mathtt{1}^*$ and count `00` and `11` in $\mathtt{0}^a\mathtt{1}^b$. (b) Cut $w$ into maximal runs of equal symbols; where can `01` and `10` occur? (c) Extra 0s at the front of a string change neither count — so build the fooling set from 1s.

> [!solution]- Solution
> **Idea.** All three definitions compare two substring counts, but only some comparisons need an unbounded counter. Before trying to prove anything, ask what a one-pass algorithm would have to remember — and test the definition on short strings.
>
> **(a) Not regular — by closure.** Suppose $L_a$ were regular. Since $\mathtt{0}^*\mathtt{1}^*$ is regular, $L_a\cap\mathtt{0}^*\mathtt{1}^*$ would be regular too (Corollary 3.4). The string $\mathtt{0}^a\mathtt{1}^b$ contains $\max(a-1,0)$ copies of `00` and $\max(b-1,0)$ copies of `11`; these are equal when $a = b$, and otherwise only when $a\le1$ and $b\le1$. So
> $$
> L_a\cap\mathtt{0}^*\mathtt{1}^* = \{\mathtt{0}^n\mathtt{1}^n \mid n\ge0\}\cup\{\mathtt{0},\mathtt{1}\}.
> $$
> The finite language $\{\mathtt{0},\mathtt{1}\}$ is regular, so $(L_a\cap\mathtt{0}^*\mathtt{1}^*)\setminus\{\mathtt{0},\mathtt{1}\} = \{\mathtt{0}^n\mathtt{1}^n \mid n\ge0\}$ would be regular as well, contradicting Lemma 3.6. So $L_a$ is not regular.
>
> (A fooling set works too, but not $\mathtt{0}^*$ with $z = \mathtt{1}^i$: that suffix fails for the pair $\varepsilon$, `0`, which are both in $L_a$. With $F = \{\mathtt{0}^i \mid i\ge1\}$ and $z = \mathtt{1}^i$, the string $yz = \mathtt{0}^j\mathtt{1}^i$ has $j-1$ copies of `00` but $i-1$ copies of `11`.)
>
> **(b) Regular.** $L_b$ is the language of the expression
> $$
> \varepsilon+\mathtt{0}+\mathtt{1}+\mathtt{0}(\mathtt{0}+\mathtt{1})^*\mathtt{0}+\mathtt{1}(\mathtt{0}+\mathtt{1})^*\mathtt{1},
> $$
> the strings that are empty or start and end with the same symbol: $\varepsilon$, `0` and `1` are the strings of length at most 1, and the last two terms are the longer strings that start and end with `0`, respectively `1`. *Why this is $L_b$:* cut a non-empty $w$ into its maximal runs of equal symbols, $w = r_1r_2\cdots r_k$ (for example `0110` $=$ `0`·`11`·`0`). Inside a run adjacent symbols are equal, so the occurrences of `01` and `10` are exactly the $k-1$ seams between consecutive runs. The runs alternate between 0s and 1s, so the seams alternate between `01` and `10`. Hence $\#(\mathtt{01},w) = \#(\mathtt{10},w)$ exactly when $k-1$ is even, that is, when $r_1$ and $r_k$ consist of the same symbol — when $w$ starts and ends with the same symbol. And $\varepsilon\in L_b$, since $0 = 0$.
>
> **(c) Not regular — by a fooling set.** First, $\mathtt{0}^*$ is useless here: for $i,j\ge1$ and every $z$, the strings $\mathtt{0}^iz$ and $\mathtt{0}^jz$ have the same numbers of `01` and `11`, because the extra 0s create only copies of `00`. So no suffix distinguishes $\mathtt{0}^i$ and $\mathtt{0}^j$. The quantity a DFA would have to count is the number of `11`s, so use 1s.
>
> Let $F = \{\mathtt{1}^i \mid i\ge1\}$. Let $x$ and $y$ be arbitrary distinct strings in $F$; then $x = \mathtt{1}^i$ and $y = \mathtt{1}^j$ for some integers $i,j\ge1$ with $i\ne j$. Let $z = (\mathtt{01})^{i-1}$. For any $m\ge1$, in $\mathtt{1}^mz$ the copies of `11` are the $m-1$ inside $\mathtt{1}^m$ ($z$ alternates and starts with `0`), and the copies of `01` are the $i-1$ inside $z$ (there are none inside $\mathtt{1}^m$, and the seam is `10`). So:
> - $xz = \mathtt{1}^i(\mathtt{01})^{i-1}$ has $i-1$ copies of each, so $xz\in L_c$;
> - $yz = \mathtt{1}^j(\mathtt{01})^{i-1}$ has $j-1$ copies of `11` but $i-1\ne j-1$ copies of `01`, so $yz\notin L_c$.
>
> So $F$ is a fooling set for $L_c$, and since it is infinite, $L_c$ is not regular. $\blacksquare$
>
> **Check.** (b): `0110` has one `01` and one `10`; `011` has one `01` and no `10`. (c) with $i = 2$, $j = 3$: $xz = \mathtt{1101}$ has one `11` and one `01`; $yz = \mathtt{11101}$ has two `11`s and one `01`.
>
> **Watch out:** three definitions that look alike, three different arguments — never decide "not regular" from the shape of a definition. In (a) the closure argument must run in the right direction (assume $L_a$ regular and derive a known non-regular language; a *regular* intersection would prove nothing), and the intersection must be computed exactly: forgetting `0` and `1` is a real error. More on this trick in [[1-models-of-computation/03-finite-state-machines#38-proving-a-language-is-not-regular|§3.8]].
>
> **Answer.** (a) Not regular: $(L_a\cap\mathtt{0}^*\mathtt{1}^*)\setminus\{\mathtt{0},\mathtt{1}\} = \{\mathtt{0}^n\mathtt{1}^n \mid n\ge0\}$. (b) Regular: $\varepsilon+\mathtt{0}+\mathtt{1}+\mathtt{0}(\mathtt{0}+\mathtt{1})^*\mathtt{0}+\mathtt{1}(\mathtt{0}+\mathtt{1})^*\mathtt{1}$. (c) Not regular: $F = \{\mathtt{1}^i \mid i\ge1\}$ with $z = (\mathtt{01})^{i-1}$.

### 3.10 Shrink it, then prove it minimal

> [!hard] Hard · minimization · Myhill–Nerode · fooling sets
> The DFA $M$ has start state $A$, accepting states $\{E,G\}$ and this transition function:
>
> | $\delta$ | $\mathtt{0}$ | $\mathtt{1}$ |
> |---|---|---|
> | $A$ | $D$ | $B$ |
> | $B$ | $C$ | $B$ |
> | $C$ | $D$ | $E$ |
> | $D$ | $A$ | $B$ |
> | $E$ | $G$ | $E$ |
> | $G$ | $G$ | $E$ |
> | $H$ | $A$ | $C$ |
>
> (a) Which states are unreachable from $A$?
>
> (b) Run Moore's algorithm on the reachable states: list the pairs marked initially and in each pass. (In pass $k$, mark $\{p,q\}$ if, for some symbol $a$, the pair $\{\delta(p,a),\delta(q,a)\}$ was marked *before* pass $k$ began; stop after a pass that marks nothing.)
>
> (c) Give the minimal DFA with mnemonic state names, and describe $L(M)$ in one sentence.
>
> (d) Prove with a fooling set that no DFA with fewer states accepts $L(M)$.
>
> *Source: original.*

> [!hint]- Hint
> Pass $k$ marks exactly the pairs whose shortest distinguishing string has length $k$ (the initial marks are the length-0 pairs). For (d), take one string that leads to each state of your minimal DFA.

> [!solution]- Solution
> **Idea.** Moore's algorithm ([[1-models-of-computation/03-finite-state-machines#310-minimal-automata-moores-algorithm|§3.10]]) is dynamic programming on "some string of length at most $k$ distinguishes $p$ and $q$". Whatever is never marked can be merged; a fooling set then certifies that the result cannot be shrunk further.
>
> **(a)** From $A$ we reach $D$ and $B$, then $C$, then $E$, then $G$; no transition enters $H$. So $H$ is unreachable, and we delete it.
>
> **(b)** Six states give 15 pairs.
> - **Initially:** the 8 pairs with exactly one accepting state, $\{X,Y\}$ for $X\in\{A,B,C,D\}$ and $Y\in\{E,G\}$.
> - **Pass 1:** $\{A,C\}$, $\{B,C\}$, $\{C,D\}$. In each, reading `1` leads to the marked pair $\{B,E\}$, because $\delta(A,\mathtt{1}) = \delta(B,\mathtt{1}) = \delta(D,\mathtt{1}) = B$ and $\delta(C,\mathtt{1}) = E$.
> - **Pass 2:** $\{A,B\}$ (reading `0` gives $\{D,C\}$, marked in pass 1) and $\{B,D\}$ (reading `0` gives $\{C,A\}$, marked in pass 1).
> - **Pass 3:** nothing. The remaining pairs only lead to themselves or to a single state: $\{A,D\}$ goes to $\{D,A\}$ on `0` and to $B$ on `1`; $\{E,G\}$ goes to $G$ on `0` and to $E$ on `1`. Stop.
>
> The pass that marked each pair (0 = initially, – = never):
>
> | | $A$ | $B$ | $C$ | $D$ | $E$ |
> |---|---|---|---|---|---|
> | $B$ | 2 | | | | |
> | $C$ | 1 | 1 | | | |
> | $D$ | – | 2 | 1 | | |
> | $E$ | 0 | 0 | 0 | 0 | |
> | $G$ | 0 | 0 | 0 | 0 | – |
>
> **(c)** Merge $A$ with $D$, and $E$ with $G$:
>
> | | state | meaning: the input read so far … | $\mathtt{0}$ | $\mathtt{1}$ |
> |---|---|---|---|---|
> | → | $AD$ | has no `101`, and does not end in `1` or `10` | $AD$ | $B$ |
> | | $B$ | has no `101`, and ends in `1` | $C$ | $B$ |
> | | $C$ | has no `101`, and ends in `10` | $AD$ | $EG$ |
> | \* | $EG$ | contains `101` | $EG$ | $EG$ |
>
> So $L(M)$ is the set of strings that contain `101` as a substring.
>
> **(d)** Let $S = \{\varepsilon,\mathtt{1},\mathtt{10},\mathtt{101}\}$, one string for each state of the minimal DFA. Every pair has a distinguishing suffix $z$ (shown with the string of the pair that $z$ puts into $L(M)$):
>
> | pair | $z$ | in $L(M)$ | not in $L(M)$ |
> |---|---|---|---|
> | $\varepsilon$, `1` | `01` | `101` | `01` |
> | $\varepsilon$, `10` | `1` | `101` | `1` |
> | `1`, `10` | `1` | `101` | `11` |
> | $\varepsilon$, `101` | $\varepsilon$ | `101` | $\varepsilon$ |
> | `1`, `101` | $\varepsilon$ | `101` | `1` |
> | `10`, `101` | $\varepsilon$ | `101` | `10` |
>
> So $S$ is a fooling set of size 4: every DFA for $L(M)$ has at least 4 states, and the DFA in (c) is minimal.
>
> **Check.** The pass numbers agree with shortest distinguishing strings: `1` distinguishes $A$ and $C$ ($\delta^*(A,\mathtt{1}) = B$ rejects, $\delta^*(C,\mathtt{1}) = E$ accepts), while $A$ and $B$ need two symbols: `01` takes $A$ to $B$ (reject) and $B$ to $E$ (accept), and no single symbol separates them.
>
> **Watch out:** if marks made earlier *in the same pass* are allowed to count, the pass numbers can change (checking pairs in alphabetical order, $\{B,D\}$ is then marked in pass 1, because $\{A,C\}$ was marked earlier in that pass), but the final partition cannot. And do not skip step 1: $H$ is equivalent to no other state, so leaving it in the table produces a 5-state "minimal" DFA.
>
> **Answer.** (a) $H$. (b) Initially the 8 pairs between $\{A,B,C,D\}$ and $\{E,G\}$; pass 1: $\{A,C\},\{B,C\},\{C,D\}$; pass 2: $\{A,B\},\{B,D\}$; pass 3: nothing. (c) Four states $AD$, $B$, $C$, $EG$; $L(M)$ is the set of strings containing `101`. (d) $S = \{\varepsilon,\mathtt{1},\mathtt{10},\mathtt{101}\}$ is a fooling set of size 4.

### Sources for this page
All ten problems were written for this page in the style of the course's exams; none is taken from a course exam or homework. Problem 3.7 (the squares $\{ww\}$ are not regular) and part (b) of 3.9 (equally many `01`s and `10`s is a regular condition) are classic textbook exercises, and 3.2 is a standard bounded-counter design, all in our own words; the rest are original. The methods are those of the book's Chapter 3: the correctness template (§3.3), DFAs as algorithms (§3.5), the product construction and closure properties (§§3.6–3.7), fooling sets and the closure trick (§3.8), the Myhill–Nerode theorem (§3.9) and Moore's algorithm (§3.10). Every DFA, regular expression, fooling-set suffix and Moore pass on this page is checked by `tools/practice/checks/ch03.py`.

*Previous: [[practice/02-regular-languages|Chapter 2 practice]] · next: [[practice/04-nondeterministic-automata|Chapter 4 practice]] · [[practice/index|all practice]]*
