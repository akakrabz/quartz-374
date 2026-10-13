---
title: "Practice — Chapter 1: Strings"
description: "8 practice problems (3 easy, 3 medium, 2 hard) on strings and string induction: unfolding recursive definitions, substrings versus subsequences, a proof with a missing case, reversal with an accumulator, rotation, and two exam-length proofs about newly defined functions, each with a folded hint and a worked solution."
tags: [practice, strings, midterm-1]
chapter: 1
---

*Practice for [[1-models-of-computation/01-strings|Chapter 1]] · concepts: [[concepts/strings]] · [[concepts/induction-on-strings]] · all practice: [[practice/index|hub]] · by difficulty: [[practice/easy|easy]] · [[practice/medium|medium]] · [[practice/hard|hard]] · [[practice/topics|by topic]]*

Work each problem on paper first. Open the **hint** only when stuck, and the **solution** only after you have an answer you would hand in. Every identity and every step of every proof in the solutions has been checked by a script on all short strings. In proofs you may cite Lemmas 1.1–1.3 and the facts listed under [[1-models-of-computation/01-strings#more-recursive-functions|More recursive functions]], as the exams allow.

## Easy

### 1.1 Unfold an accumulator

> [!easy] Easy · recursive functions
> The function $\textsf{rcat}$ takes two strings and recurses on its first argument:
> $$
> \textsf{rcat}(x, y) := \begin{cases} y & \text{if } x = \varepsilon\\ \textsf{rcat}(z,\ a\cdot y) & \text{if } x = a\cdot z.\end{cases}
> $$
> (a) Compute $\textsf{rcat}(\mathtt{011}, \varepsilon)$ by unfolding the definition one step at a time, and name the case used at each step.
>
> (b) Compute $\textsf{rcat}(\mathtt{10}, \mathtt{01})$.
>
> (c) Guess a formula for $\textsf{rcat}(x, y)$ in terms of $x$, $y$ and the functions of Chapter 1, and a formula for $\lvert\textsf{rcat}(x, y)\rvert$. No proof is needed here; Problem 1.4 asks for one.
>
> *Source: classic.*

> [!solution]- Solution
> **(a)** Each step peels the first symbol off the first argument and puts it in front of the second argument with the small dot:
> $$
> \begin{aligned}
> \textsf{rcat}(\mathtt{011}, \varepsilon) &= \textsf{rcat}(\mathtt{11}, \mathtt{0}\cdot\varepsilon) = \textsf{rcat}(\mathtt{11}, \mathtt{0}) && \text{second case: } a = \mathtt{0},\ z = \mathtt{11}\\
> &= \textsf{rcat}(\mathtt{1}, \mathtt{1}\cdot\mathtt{0}) = \textsf{rcat}(\mathtt{1}, \mathtt{10}) && \text{second case: } a = \mathtt{1},\ z = \mathtt{1}\\
> &= \textsf{rcat}(\varepsilon, \mathtt{1}\cdot\mathtt{10}) = \textsf{rcat}(\varepsilon, \mathtt{110}) && \text{second case: } a = \mathtt{1},\ z = \varepsilon\\
> &= \mathtt{110} && \text{first case.}
> \end{aligned}
> $$
> **(b)** $\textsf{rcat}(\mathtt{10}, \mathtt{01}) = \textsf{rcat}(\mathtt{0}, \mathtt{101}) = \textsf{rcat}(\varepsilon, \mathtt{0101}) = \mathtt{0101}$.
>
> **(c)** The symbols of $x$ arrive at the front of the second argument one at a time, so they end up in reverse order, in front of the untouched $y$: in (a), $\mathtt{110} = (\mathtt{011})^R$, and in (b), $\mathtt{0101} = (\mathtt{10})^R\bullet\mathtt{01}$. The guess is
> $$
> \textsf{rcat}(x, y) = x^R\bullet y, \qquad \lvert\textsf{rcat}(x, y)\rvert = \lvert x\rvert + \lvert y\rvert.
> $$
> **Check:** for $x = \varepsilon$ the guess gives $\varepsilon^R\bullet y = y$, which is the first case of the definition.
>
> **Watch out:** the recursive call changes *both* arguments — the first gets shorter, the second longer. A proof by induction on $x$ must therefore allow any second argument in its hypothesis (Problem 1.4).
>
> **Answer.** (a) $\mathtt{110}$. (b) $\mathtt{0101}$. (c) $\textsf{rcat}(x, y) = x^R\bullet y$, of length $\lvert x\rvert + \lvert y\rvert$.

### 1.2 Substrings, subsequences and prefixes

> [!easy] Easy · true or false · substrings and subsequences
> All strings are over $\{\mathtt{0}, \mathtt{1}\}$. Answer each statement **Yes** (always true) or **No** (not always true), with a one-sentence justification; for a No, give a counterexample.
>
> (a) If $x$ is a substring of $y\bullet z$, then $x$ is a substring of $y$ or a substring of $z$.
>
> (b) If $x$ is a subsequence of $y\bullet z$, then $x = u\bullet v$ for some subsequence $u$ of $y$ and some subsequence $v$ of $z$.
>
> (c) If $p$ is a prefix of $w$, then $p^R$ is a suffix of $w^R$.
>
> (d) If $x\bullet y = y\bullet x$, then $x = y$.
>
> (e) Every string of length $n$ has at least $n+1$ distinct subsequences.
>
> (f) The string $\mathtt{0101}$ has exactly 11 distinct substrings, counting $\varepsilon$.
>
> *Source: original.*

> [!hint]- Hint
> Every counterexample here needs at most three symbols. For (e), look for $n+1$ subsequences that are different for an obvious reason.

> [!solution]- Solution
> - **(a) No.** A substring can straddle the boundary: $x = \mathtt{01}$ is a substring of $\mathtt{0}\bullet\mathtt{1} = \mathtt{01}$, but not of $y = \mathtt{0}$ or of $z = \mathtt{1}$.
> - **(b) Yes.** A subsequence keeps some symbols of $yz$ in order; the kept symbols that come from $y$ form a subsequence $u$ of $y$, those from $z$ a subsequence $v$ of $z$, and $x = uv$ because every symbol of $y$ comes before every symbol of $z$.
> - **(c) Yes.** If $w = p\bullet x$, then $w^R = x^R\bullet p^R$ by the reversal fact $(p\bullet x)^R = x^R\bullet p^R$, so $p^R$ is a suffix of $w^R$.
> - **(d) No.** $x = \mathtt{0}$ and $y = \mathtt{00}$ commute ($\mathtt{0}\bullet\mathtt{00} = \mathtt{000} = \mathtt{00}\bullet\mathtt{0}$) but are different; so do $x = \varepsilon$ and any non-empty $y$.
> - **(e) Yes.** The $n+1$ prefixes $w[1..0], w[1..1], \dots, w[1..n]$ are subsequences (a prefix is a substring, and a substring is a subsequence), and they are distinct because their lengths differ. The bound is reached: $\mathtt{0}^n$ has exactly the $n+1$ subsequences $\varepsilon, \mathtt{0}, \dots, \mathtt{0}^n$.
> - **(f) No.** It has 8: $\varepsilon$, $\mathtt{0}$, $\mathtt{1}$, $\mathtt{01}$, $\mathtt{10}$, $\mathtt{010}$, $\mathtt{101}$, $\mathtt{0101}$. Eleven — $n(n+1)/2$ non-empty substrings plus $\varepsilon$ — is only an upper bound; here different positions give equal substrings ($\mathtt{01}$ starts at positions 1 and 3).
>
> **Watch out:** a Yes needs a reason that covers every case — one example proves nothing. A No needs one concrete counterexample, and a tiny one is best.
>
> **Answer.** (a) No. (b) Yes. (c) Yes. (d) No. (e) Yes. (f) No: it has 8.

### 1.3 A proof with a missing case

> [!easy] Easy · find the error · string induction
> For a binary string $w$, $w^c$ is its complement (every $\mathtt{0}$ becomes $\mathtt{1}$ and vice versa) and $w^R$ its reversal. A student proves $(w^R)^c = (w^c)^R$, citing the facts $(x\bullet y)^R = y^R\bullet x^R$ and $(x\bullet y)^c = x^c\bullet y^c$:
>
> *Let $w$ be an arbitrary binary string, and assume that $(x^R)^c = (x^c)^R$ for every string $x$ with $\lvert x\rvert<\lvert w\rvert$. Case $w = \varepsilon$: $(\varepsilon^R)^c = \varepsilon^c = \varepsilon = \varepsilon^R = (\varepsilon^c)^R$. Case $w = u\bullet v$ for non-empty strings $u$ and $v$: then $\lvert u\rvert, \lvert v\rvert<\lvert w\rvert$, so*
> $$
> \big((uv)^R\big)^c = (v^Ru^R)^c = (v^R)^c(u^R)^c = (v^c)^R(u^c)^R = (u^cv^c)^R = \big((uv)^c\big)^R.
> $$
> *In both cases, $(w^R)^c = (w^c)^R$.* $\blacksquare$
>
> What is wrong with this proof? Repair it.
>
> *Source: original.*

> [!hint]- Hint
> Which strings fall into neither case? Can such a string be written as $u\bullet v$ with both pieces non-empty?

> [!solution]- Solution
> **The slip: the cases do not cover every string.** A string of length 1 is neither $\varepsilon$ nor a concatenation of two *non-empty* strings, so the proof says nothing about $w = \mathtt{0}$ or $w = \mathtt{1}$. The $u\bullet v$ step itself is correct: its five equalities use the reversal fact, the complement fact, the hypothesis for $v$ and for $u$ (both shorter than $w$), the reversal fact, and the complement fact.
>
> **The repair: add the case $w = a$** for a single symbol $a$. By the definition of reversal, $a^R = (a\cdot\varepsilon)^R = \varepsilon^R\bullet a = \varepsilon\bullet a = a$: a one-symbol string is its own reversal. The complement $a^c$ is again a single symbol, so $(a^c)^R = a^c$, and therefore $(a^R)^c = a^c = (a^c)^R$. With the three cases $w = \varepsilon$, $w = a$, and $w = u\bullet v$ with $u$, $v$ non-empty, every string is covered and the proof is complete.
>
> **Why the missing case matters.** The same two cases "prove" the false claim $\#(\mathtt{0}, w) = \#(\mathtt{1}, w)$: it holds for $\varepsilon$, and if it holds for $u$ and $v$, then $\#(\mathtt{0}, uv) = \#(\mathtt{0},u) + \#(\mathtt{0},v) = \#(\mathtt{1},u) + \#(\mathtt{1},v) = \#(\mathtt{1},uv)$. The claim fails exactly in the missing case: $\#(\mathtt{0},\mathtt{0}) = 1\ne0 = \#(\mathtt{1},\mathtt{0})$.
>
> **Watch out:** the split $w = u\bullet v$ always needs *two* base cases, $\varepsilon$ and a single symbol ([[1-models-of-computation/01-strings#14-more-than-one-path-up-the-mountain|§1.4]]). On the exams, cases that miss some strings cost the 2 points for exhaustive cases.
>
> **Answer.** Strings of length 1 are in neither case. Add the case $w = a$, where $(a^R)^c = a^c = (a^c)^R$ because a one-symbol string is its own reversal.

## Medium

### 1.4 Reversal with an accumulator

> [!medium] Medium · string induction · recursive functions
> Let $\textsf{rcat}$ be the function of Problem 1.1: $\textsf{rcat}(\varepsilon, y) := y$ and $\textsf{rcat}(a\cdot z, y) := \textsf{rcat}(z, a\cdot y)$.
>
> (a) Prove that $\textsf{rcat}(x, y) = x^R\bullet y$ for all strings $x$ and $y$.
>
> (b) Conclude that $\textsf{rcat}(x, \varepsilon) = x^R$ and $\lvert\textsf{rcat}(x, y)\rvert = \lvert x\rvert + \lvert y\rvert$.
>
> Reversal is defined by $\varepsilon^R := \varepsilon$ and $(a\cdot z)^R := z^R\bullet a$; you may also use $\lvert w^R\rvert = \lvert w\rvert$.
>
> *Source: classic.*

> [!hint]- Hint
> Induct on $x$, the argument that shrinks. In the recursive case the *second* argument changes from $y$ to $a\cdot y$, so the induction hypothesis must hold for every second argument, not only for $y$.

> [!solution]- Solution
> **Idea.** $\textsf{rcat}$ recurses on $x$, so induct on $x$. The recursive call has second argument $a\cdot y$ instead of $y$; a hypothesis about the fixed $y$ could not be applied to it, so the hypothesis quantifies over all second arguments.
>
> **(a)** Let $x$ be an arbitrary string. Assume that $\textsf{rcat}(z, y') = z^R\bullet y'$ for every string $z$ with $\lvert z\rvert<\lvert x\rvert$ and **every** string $y'$. Let $y$ be an arbitrary string. There are two cases.
>
> **Case $x = \varepsilon$.** By the definitions of $\textsf{rcat}$, ${\bullet}$ and ${}^R$: $\textsf{rcat}(\varepsilon, y) = y = \varepsilon\bullet y = \varepsilon^R\bullet y$.
>
> **Case $x = a\cdot z$** for some symbol $a$ and string $z$. Then $\lvert z\rvert<\lvert x\rvert$, so the induction hypothesis applies to $z$, with $y' = a\cdot y$:
> $$
> \begin{aligned}
> \textsf{rcat}(a\cdot z, y) &= \textsf{rcat}(z, a\cdot y) && \text{by definition of } \textsf{rcat}\\
> &= z^R\bullet(a\cdot y) && \text{by the induction hypothesis, with } y' = a\cdot y\\
> &= z^R\bullet(a\bullet y) && \text{because } a\bullet y = a\cdot y\\
> &= (z^R\bullet a)\bullet y && \text{by Lemma 1.3}\\
> &= (a\cdot z)^R\bullet y && \text{by definition of } {}^R.
> \end{aligned}
> $$
> In both cases, $\textsf{rcat}(x, y) = x^R\bullet y$. $\blacksquare$
>
> **(b)** With $y = \varepsilon$, part (a) and Lemma 1.1 give $\textsf{rcat}(x, \varepsilon) = x^R\bullet\varepsilon = x^R$. By part (a), Lemma 1.2 and $\lvert x^R\rvert = \lvert x\rvert$: $\lvert\textsf{rcat}(x, y)\rvert = \lvert x^R\rvert + \lvert y\rvert = \lvert x\rvert + \lvert y\rvert$.
>
> **Check:** $\textsf{rcat}(\mathtt{011}, \varepsilon) = \mathtt{110} = (\mathtt{011})^R$ and $\textsf{rcat}(\mathtt{10}, \mathtt{01}) = \mathtt{0101} = \mathtt{01}\bullet\mathtt{01}$, as computed in Problem 1.1.
>
> **Watch out:** with the weaker hypothesis "$\textsf{rcat}(z, y) = z^R\bullet y$ for every shorter $z$" (the same $y$), the second line is not justified, because the call is $\textsf{rcat}(z, a\cdot y)$. Graders count that as applying the hypothesis with the wrong value of the other argument (2 points on the induction rubric). Proving only the special case $\textsf{rcat}(x, \varepsilon) = x^R$ by induction fails for the same reason — $\textsf{rcat}(a\cdot z, \varepsilon)$ calls $\textsf{rcat}(z, a)$, which is not of the form $\textsf{rcat}(z', \varepsilon)$. Here the general statement is *easier* to prove than the special case.
>
> **Answer.** (a) Induction on $x$, with the hypothesis for every second argument: $\textsf{rcat}(az, y) = \textsf{rcat}(z, ay) = z^R\bullet(ay) = (z^Ra)\bullet y = (az)^R\bullet y$. (b) $\textsf{rcat}(x,\varepsilon) = x^R\bullet\varepsilon = x^R$, and $\lvert\textsf{rcat}(x,y)\rvert = \lvert x\rvert+\lvert y\rvert$.

### 1.5 When subsequences are substrings

> [!medium] Medium · substrings and subsequences
> All strings are over $\{\mathtt{0}, \mathtt{1}\}$.
>
> (a) For integers $a, b\ge1$, how many distinct substrings and how many distinct subsequences does $\mathtt{0}^a\mathtt{1}^b$ have? Count $\varepsilon$.
>
> (b) Prove that every subsequence of $w$ is a substring of $w$ if and only if $w = \mathtt{0}^i\mathtt{1}^j$ or $w = \mathtt{1}^i\mathtt{0}^j$ for some $i, j\ge0$.
>
> *Source: original.*

> [!hint]- Hint
> (a) Deleting symbols from $\mathtt{0}^a\mathtt{1}^b$ never puts a $\mathtt{1}$ before a $\mathtt{0}$. (b) For "only if", find a symbol whose copies are not all next to each other, and look at its longest block of consecutive copies.

> [!solution]- Solution
> **Idea.** A subsequence of $\mathtt{0}^a\mathtt{1}^b$ is a few 0s followed by a few 1s, and such a string sits around the boundary of $\mathtt{0}^a\mathtt{1}^b$ as a substring. A string of any other shape has a symbol that occurs in two separate blocks, and gluing copies from both blocks gives a subsequence that is too long to be a substring.
>
> **(a)** A subsequence of $\mathtt{0}^a\mathtt{1}^b$ keeps some of the 0s and some of the 1s, in order, so it is $\mathtt{0}^p\mathtt{1}^q$ with $0\le p\le a$ and $0\le q\le b$; conversely each such string is a subsequence. Each of them is also a substring — the last $p$ zeros and the first $q$ ones, $w[a-p+1\,..\,a+q]$ — and every substring is a subsequence. So the substrings and the subsequences are the same set $\{\mathtt{0}^p\mathtt{1}^q \mid 0\le p\le a,\ 0\le q\le b\}$, with $(a+1)(b+1)$ elements (different pairs $(p, q)$ give different strings).
>
> **(b) "If."** For $w = \mathtt{0}^i\mathtt{1}^j$ this is the argument of (a), which also works when $i = 0$ or $j = 0$. For $w = \mathtt{1}^i\mathtt{0}^j$, exchange the roles of the two symbols.
>
> **"Only if"**, by the contrapositive. Suppose $w$ has neither form. Since $w$ is not $\mathtt{0}^i\mathtt{1}^j$, some $\mathtt{1}$ of $w$ comes before some $\mathtt{0}$ (otherwise all 0s precede all 1s); since $w$ is not $\mathtt{1}^i\mathtt{0}^j$, some $\mathtt{0}$ comes before some $\mathtt{1}$. Let $c$ be the first symbol of $w$ and $\bar c$ the other one. By one of the two facts (the first if $c = \mathtt{0}$, the second if $c = \mathtt{1}$), some $\bar c$ comes before a later $c$; with the first symbol, $w$ contains $c$, then $\bar c$, then $c$ again, in that order. So the copies of $c$ form at least two separate **blocks** (maximal runs of consecutive $c$'s). Let $m$ be the length of the longest block. The other block has at least one $c$, so $\#(c, w)\ge m+1$, and $c^{m+1}$ is a subsequence of $w$. But it is not a substring: a substring made of $m+1$ copies of $c$ would lie inside a single block, and every block has length at most $m$. $\blacksquare$
>
> **Check:** $\mathtt{0110}$ has neither form, and indeed $\mathtt{00}$ is a subsequence but not a substring of it. $\mathtt{0011}$ has $(2+1)(2+1) = 9$ substrings and 9 subsequences.
>
> **Answer.** (a) $(a+1)(b+1)$ substrings and $(a+1)(b+1)$ subsequences — the two sets are equal. (b) "If": every subsequence $\mathtt{0}^p\mathtt{1}^q$ of $\mathtt{0}^i\mathtt{1}^j$ is a substring. "Only if": otherwise some symbol $c$ occurs in two blocks, and if its longest block has length $m$, then $c^{m+1}$ is a subsequence but not a substring.

### 1.6 Rotating a string

> [!medium] Medium · string induction · recursive functions
> For symbols $a$, $b$ and a string $x$, define
> $$
> \textsf{rot}(w) := \begin{cases} w & \text{if } \lvert w\rvert\le1\\ b\cdot\textsf{rot}(a\cdot x) & \text{if } w = a\cdot b\cdot x.\end{cases}
> $$
> (a) Compute $\textsf{rot}(\mathtt{STAR})$ by unfolding the definition.
>
> (b) Prove directly from the definition, by induction on $w$, that $\lvert\textsf{rot}(w)\rvert = \lvert w\rvert$ for every string $w$.
>
> (c) Prove that $\textsf{rot}(a\cdot x) = x\bullet a$ for every symbol $a$ and every string $x$.
>
> *Source: original.*

> [!hint]- Hint
> (b) The definition has two cases, $\lvert w\rvert\le1$ and $w = a\cdot b\cdot x$, so the proof does too. The recursive call is on $a\cdot x$: is that string shorter than $w$, and does it matter that it is not the tail $b\cdot x$? (c) Here it is easier to induct on $x$ and keep $a$ fixed.

> [!solution]- Solution
> **Idea.** Each call moves the second symbol out to the front and keeps the first symbol inside the call, so the first symbol travels to the end: $\textsf{rot}$ rotates the string by one position. For (b), the strong hypothesis ("every shorter string") covers the call on $a\cdot x$; for (c), inducting on $x$ makes the call an ordinary call on a shorter tail.
>
> **(a)**
> $$
> \textsf{rot}(\mathtt{STAR}) = \mathtt{T}\cdot\textsf{rot}(\mathtt{SAR}) = \mathtt{T}\cdot\mathtt{A}\cdot\textsf{rot}(\mathtt{SR}) = \mathtt{T}\cdot\mathtt{A}\cdot\mathtt{R}\cdot\textsf{rot}(\mathtt{S}) = \mathtt{TARS}.
> $$
> **(b)** Let $w$ be an arbitrary string, and assume that $\lvert\textsf{rot}(y)\rvert = \lvert y\rvert$ for every string $y$ with $\lvert y\rvert<\lvert w\rvert$. There are two cases.
>
> **Case $\lvert w\rvert\le1$.** Then $\textsf{rot}(w) = w$, so $\lvert\textsf{rot}(w)\rvert = \lvert w\rvert$.
>
> **Case $w = a\cdot b\cdot x$.** The string $a\cdot x$ has length $\lvert x\rvert+1<\lvert x\rvert+2 = \lvert w\rvert$, so the induction hypothesis applies to it:
> $$
> \lvert\textsf{rot}(w)\rvert = \lvert b\cdot\textsf{rot}(a\cdot x)\rvert = 1 + \lvert\textsf{rot}(a\cdot x)\rvert = 1 + \lvert a\cdot x\rvert = 2 + \lvert x\rvert = \lvert w\rvert,
> $$
> by the definition of $\textsf{rot}$, the definition of $\lvert\cdot\rvert$, the induction hypothesis, and the definition of $\lvert\cdot\rvert$ twice more.
>
> In both cases, $\lvert\textsf{rot}(w)\rvert = \lvert w\rvert$. $\blacksquare$
>
> The string $a\cdot x$ is in general not a suffix of $w$ — for $w = \mathtt{STAR}$ it is $\mathtt{SAR}$. That does not matter: the hypothesis covers *every* string shorter than $w$.
>
> **(c)** Let $a$ be a symbol and $x$ an arbitrary string. Assume that $\textsf{rot}(a\cdot y) = y\bullet a$ for every string $y$ with $\lvert y\rvert<\lvert x\rvert$. There are two cases.
>
> **Case $x = \varepsilon$.** $\textsf{rot}(a\cdot\varepsilon) = a = \varepsilon\bullet a$, by the first case of $\textsf{rot}$ and the definition of ${\bullet}$.
>
> **Case $x = b\cdot y$.** Then $\lvert y\rvert<\lvert x\rvert$, and
> $$
> \textsf{rot}(a\cdot b\cdot y) = b\cdot\textsf{rot}(a\cdot y) = b\cdot(y\bullet a) = (b\cdot y)\bullet a = x\bullet a,
> $$
> by the definition of $\textsf{rot}$, the induction hypothesis for $y$, and the definition of ${\bullet}$.
>
> In both cases, $\textsf{rot}(a\cdot x) = x\bullet a$. $\blacksquare$
>
> **Check:** $\textsf{rot}(\mathtt{STAR}) = \mathtt{TARS} = \mathtt{TAR}\bullet\mathtt{S}$, as (c) predicts. And (b) also follows from (c): $\lvert x\bullet a\rvert = \lvert x\rvert + 1$ by Lemma 1.2.
>
> **Watch out:** choosing *what* to induct on is part of the proof. Inducting on $w$ in (c) works too, but then the hypothesis must be applied to $a\cdot y$, which is not a tail of $w$, and the bookkeeping is heavier.
>
> **Answer.** (a) $\mathtt{TARS}$. (b) Two cases; for $w = abx$, the hypothesis applies to the shorter string $a\cdot x$, and $\lvert b\cdot\textsf{rot}(ax)\rvert = 1 + \lvert ax\rvert = \lvert w\rvert$. (c) Induction on $x$: $\textsf{rot}(a\cdot b\cdot y) = b\cdot\textsf{rot}(a\cdot y) = b\cdot(y\bullet a) = (by)\bullet a$.

## Hard

### 1.7 Complementing every other symbol

> [!hard] Hard · string induction · recursive functions
> For a binary string $w$, the complement $w^c$ is defined by $\varepsilon^c := \varepsilon$ and $(a\cdot x)^c := \bar a\cdot x^c$, where $\bar{\mathtt{0}} = \mathtt{1}$ and $\bar{\mathtt{1}} = \mathtt{0}$. Define
> $$
> \textsf{zig}(w) := \begin{cases} \varepsilon & \text{if } w = \varepsilon\\ a\cdot\big(\textsf{zig}(x)\big)^c & \text{if } w = a\cdot x.\end{cases}
> $$
> For example, $\textsf{zig}(\mathtt{0000}) = \mathtt{0101}$ and $\textsf{zig}(\mathtt{0110}) = \mathtt{0011}$.
>
> (a) Prove that $\textsf{zig}(w^c) = \big(\textsf{zig}(w)\big)^c$ for every binary string $w$.
>
> (b) Prove that $\textsf{zig}(\textsf{zig}(w)) = w$ for every binary string $w$.
>
> You may use $(y^c)^c = y$ for every binary string $y$, and in (b) you may use (a).
>
> *Source: original.*

> [!hint]- Hint
> Write the boilerplate for both parts first. In (a), the case $w = a\cdot x$ starts from $w^c = \bar a\cdot x^c$. In (b), unfolding $\textsf{zig}(\textsf{zig}(a\cdot x))$ twice produces $\textsf{zig}\big(\textsf{zig}(x)^c\big)$: that is where (a) comes in, applied to the string $\textsf{zig}(x)$.

> [!solution]- Solution
> **Idea.** $\textsf{zig}$ keeps the first symbol and complements the result of the recursive call, so the second symbol is complemented once, the third twice, and so on: $\textsf{zig}$ complements exactly the symbols in even positions, and doing that twice changes nothing. In the proof, a complement must be moved past $\textsf{zig}$; that is what (a) does.
>
> **(a)** Let $w$ be an arbitrary binary string. Assume that $\textsf{zig}(y^c) = \textsf{zig}(y)^c$ for every binary string $y$ with $\lvert y\rvert<\lvert w\rvert$. There are two cases.
>
> **Case $w = \varepsilon$.** $\textsf{zig}(\varepsilon^c) = \textsf{zig}(\varepsilon) = \varepsilon = \varepsilon^c = \textsf{zig}(\varepsilon)^c$, by the definitions of ${}^c$ and $\textsf{zig}$.
>
> **Case $w = a\cdot x$** for a symbol $a$ and a string $x$. Then $\lvert x\rvert<\lvert w\rvert$, so the induction hypothesis applies to $x$, and
> $$
> \begin{aligned}
> \textsf{zig}(w^c) &= \textsf{zig}(\bar a\cdot x^c) && \text{by definition of } {}^c\\
> &= \bar a\cdot\big(\textsf{zig}(x^c)\big)^c && \text{by definition of } \textsf{zig}\\
> &= \bar a\cdot\big(\textsf{zig}(x)^c\big)^c && \text{by the induction hypothesis for } x\\
> &= \big(a\cdot\textsf{zig}(x)^c\big)^c && \text{by definition of } {}^c\\
> &= \textsf{zig}(a\cdot x)^c && \text{by definition of } \textsf{zig}.
> \end{aligned}
> $$
> In both cases, $\textsf{zig}(w^c) = \textsf{zig}(w)^c$. $\blacksquare$
>
> **(b)** Let $w$ be an arbitrary binary string. Assume that $\textsf{zig}(\textsf{zig}(y)) = y$ for every binary string $y$ with $\lvert y\rvert<\lvert w\rvert$. There are two cases.
>
> **Case $w = \varepsilon$.** $\textsf{zig}(\textsf{zig}(\varepsilon)) = \textsf{zig}(\varepsilon) = \varepsilon$, by the definition of $\textsf{zig}$ (twice).
>
> **Case $w = a\cdot x$** for a symbol $a$ and a string $x$. Then $\lvert x\rvert<\lvert w\rvert$, and
> $$
> \begin{aligned}
> \textsf{zig}(\textsf{zig}(a\cdot x)) &= \textsf{zig}\big(a\cdot\textsf{zig}(x)^c\big) && \text{by definition of } \textsf{zig}\\
> &= a\cdot\Big(\textsf{zig}\big(\textsf{zig}(x)^c\big)\Big)^c && \text{by definition of } \textsf{zig}\\
> &= a\cdot\Big(\big(\textsf{zig}(\textsf{zig}(x))\big)^c\Big)^c && \text{by (a), applied to the string } \textsf{zig}(x)\\
> &= a\cdot\textsf{zig}(\textsf{zig}(x)) && \text{because } (y^c)^c = y\\
> &= a\cdot x && \text{by the induction hypothesis for } x.
> \end{aligned}
> $$
> In both cases, $\textsf{zig}(\textsf{zig}(w)) = w$. $\blacksquare$
>
> **Check:** $\textsf{zig}(\mathtt{0110}) = \mathtt{0011}$ and $\textsf{zig}(\mathtt{0011}) = \mathtt{0110}$, as (b) says. For $w = \mathtt{01}$, (a) reads $\textsf{zig}(\mathtt{10}) = \mathtt{11} = (\mathtt{00})^c = \textsf{zig}(\mathtt{01})^c$.
>
> **Watch out:** in the third line of (b) the induction hypothesis is of no use: it is about $\textsf{zig}(\textsf{zig}(y))$, not $\textsf{zig}(y^c)$. Part (a) moves the complement out, and because (a) has been proved for *every* string, it may be applied to $\textsf{zig}(x)$ with no question of length. The hypothesis of (b) is used once, for $x$, in the last line.
>
> **Answer.** (a) Induction on $w$; for $w = ax$: $\textsf{zig}(\bar ax^c) = \bar a\cdot\textsf{zig}(x^c)^c = \bar a\cdot(\textsf{zig}(x)^c)^c = (a\cdot\textsf{zig}(x)^c)^c = \textsf{zig}(ax)^c$. (b) Induction on $w$, using (a) for $\textsf{zig}(x)$ and the hypothesis for $x$: $\textsf{zig}(\textsf{zig}(ax)) = a\cdot\textsf{zig}(\textsf{zig}(x)^c)^c = a\cdot\textsf{zig}(\textsf{zig}(x)) = ax$.

### 1.8 Binary increment, low bit first

> [!hard] Hard · string induction · recursive functions
> Read a binary string as a number with its **least** significant bit first:
> $$
> \textsf{val}(w) := \begin{cases} 0 & \text{if } w = \varepsilon\\ a + 2\cdot\textsf{val}(x) & \text{if } w = a\cdot x,\end{cases}
> $$
> where the symbols $\mathtt{0}$ and $\mathtt{1}$ count as the numbers 0 and 1; for example, $\textsf{val}(\mathtt{011}) = 0 + 2\big(1 + 2(1 + 2\cdot0)\big) = 6$. The function
> $$
> \textsf{inc}(w) := \begin{cases} \mathtt{1} & \text{if } w = \varepsilon\\ \mathtt{1}\cdot x & \text{if } w = \mathtt{0}\cdot x\\ \mathtt{0}\cdot\textsf{inc}(x) & \text{if } w = \mathtt{1}\cdot x\end{cases}
> $$
> adds one, the way you add one by hand: for example, $\textsf{inc}(\mathtt{1101}) = \mathtt{0011}$, that is, $11 + 1 = 12$.
>
> (a) Prove that $\textsf{val}(\textsf{inc}(w)) = \textsf{val}(w) + 1$ for every binary string $w$.
>
> (b) Prove that $\lvert\textsf{inc}(w)\rvert = \lvert w\rvert + 1$ if $w = \mathtt{1}^n$ for some $n\ge0$, and $\lvert\textsf{inc}(w)\rvert = \lvert w\rvert$ otherwise.
>
> *Source: original.*

> [!hint]- Hint
> The definition of $\textsf{inc}$ has three cases — $\varepsilon$, $\mathtt{0}\cdot x$, $\mathtt{1}\cdot x$ — so both proofs do, and only the case $\mathtt{1}\cdot x$ needs the induction hypothesis. In (b), split that case according to whether $x$ is all 1s.

> [!solution]- Solution
> **Idea.** Adding one turns the leading block of 1s (the low-order bits) into 0s and the first 0 into a 1; the string gets longer only when there is no 0 to absorb the carry. Both proofs follow the three cases of the definition of $\textsf{inc}$.
>
> **(a)** Let $w$ be an arbitrary binary string, and assume that $\textsf{val}(\textsf{inc}(x)) = \textsf{val}(x) + 1$ for every binary string $x$ with $\lvert x\rvert<\lvert w\rvert$. There are three cases.
>
> **Case $w = \varepsilon$.** $\textsf{val}(\textsf{inc}(\varepsilon)) = \textsf{val}(\mathtt{1}\cdot\varepsilon) = 1 + 2\cdot\textsf{val}(\varepsilon) = 1 = \textsf{val}(\varepsilon) + 1$, by the definitions of $\textsf{inc}$ and $\textsf{val}$.
>
> **Case $w = \mathtt{0}\cdot x$.** $\textsf{val}(\textsf{inc}(w)) = \textsf{val}(\mathtt{1}\cdot x) = 1 + 2\,\textsf{val}(x) = \big(0 + 2\,\textsf{val}(x)\big) + 1 = \textsf{val}(\mathtt{0}\cdot x) + 1$, by the definitions of $\textsf{inc}$ and $\textsf{val}$.
>
> **Case $w = \mathtt{1}\cdot x$.** Then $\lvert x\rvert<\lvert w\rvert$, so the induction hypothesis applies to $x$:
> $$
> \begin{aligned}
> \textsf{val}(\textsf{inc}(\mathtt{1}\cdot x)) &= \textsf{val}(\mathtt{0}\cdot\textsf{inc}(x)) && \text{by definition of } \textsf{inc}\\
> &= 0 + 2\,\textsf{val}(\textsf{inc}(x)) && \text{by definition of } \textsf{val}\\
> &= 2\big(\textsf{val}(x) + 1\big) && \text{by the induction hypothesis}\\
> &= \big(1 + 2\,\textsf{val}(x)\big) + 1 && \text{by arithmetic}\\
> &= \textsf{val}(\mathtt{1}\cdot x) + 1 && \text{by definition of } \textsf{val}.
> \end{aligned}
> $$
> In all three cases, $\textsf{val}(\textsf{inc}(w)) = \textsf{val}(w) + 1$. $\blacksquare$
>
> **(b)** A small fact first: $\mathtt{1}\cdot x$ is of the form $\mathtt{1}^n$ if and only if $x$ is. Indeed, $\mathtt{1}\cdot\mathtt{1}^m = \mathtt{1}^{m+1}$; conversely, if $\mathtt{1}\cdot x = \mathtt{1}^n$, then $n\ge1$ (the string is not empty), so $\mathtt{1}\cdot x = \mathtt{1}\cdot\mathtt{1}^{n-1}$ by the definition of powers, and $x = \mathtt{1}^{n-1}$ because equal pairs have equal second parts.
>
> Let $w$ be an arbitrary binary string. Assume, for every binary string $x$ with $\lvert x\rvert<\lvert w\rvert$, that $\lvert\textsf{inc}(x)\rvert = \lvert x\rvert + 1$ if $x$ is of the form $\mathtt{1}^m$, and $\lvert\textsf{inc}(x)\rvert = \lvert x\rvert$ otherwise. There are three cases.
>
> **Case $w = \varepsilon$.** Here $w = \mathtt{1}^0$, and $\lvert\textsf{inc}(\varepsilon)\rvert = \lvert\mathtt{1}\rvert = 1 = \lvert\varepsilon\rvert + 1$.
>
> **Case $w = \mathtt{0}\cdot x$.** Here $w$ is not of the form $\mathtt{1}^n$, because such a string is empty or starts with $\mathtt{1}$; and $\lvert\textsf{inc}(w)\rvert = \lvert\mathtt{1}\cdot x\rvert = 1 + \lvert x\rvert = \lvert\mathtt{0}\cdot x\rvert = \lvert w\rvert$.
>
> **Case $w = \mathtt{1}\cdot x$.** By the definitions, $\lvert\textsf{inc}(w)\rvert = \lvert\mathtt{0}\cdot\textsf{inc}(x)\rvert = 1 + \lvert\textsf{inc}(x)\rvert$, and $\lvert x\rvert<\lvert w\rvert$, so the hypothesis applies to $x$.
> - If $x = \mathtt{1}^m$, then $w = \mathtt{1}^{m+1}$, and $\lvert\textsf{inc}(w)\rvert = 1 + \lvert x\rvert + 1 = \lvert w\rvert + 1$.
> - Otherwise, by the small fact, $w$ is not of the form $\mathtt{1}^n$ either, and $\lvert\textsf{inc}(w)\rvert = 1 + \lvert x\rvert = \lvert w\rvert$.
>
> In all cases, the claim holds for $w$. $\blacksquare$
>
> **Check:** $\textsf{inc}(\mathtt{111}) = \mathtt{0001}$: the value goes from 7 to 8, and the length from 3 to 4. $\textsf{inc}(\mathtt{011}) = \mathtt{111}$: the value goes from 6 to 7, and the length stays 3.
>
> **Grading notes.** Each part is an induction proof of the exam type, graded out of 10: an arbitrary $w$ (1), an explicit hypothesis for every shorter string (2), cases that cover every string — here the three of the definition (2), the base case (1), the hypothesis applied only to the shorter $x$ (2), and justified details (2). See [[0-toolkit/06-how-exams-are-graded|how exams are graded]].
>
> **Watch out:** the claim in (b) has two alternatives, so the hypothesis must state both: in the case $w = \mathtt{1}\cdot x$ you do not know in advance which one applies to $x$.
>
> **Answer.** (a) Three cases; only $w = \mathtt{1}x$ uses the hypothesis: $\textsf{val}(\mathtt{0}\cdot\textsf{inc}(x)) = 2(\textsf{val}(x)+1) = \textsf{val}(\mathtt{1}x) + 1$. (b) Three cases; for $w = \mathtt{1}x$, $\lvert\textsf{inc}(w)\rvert = 1 + \lvert\textsf{inc}(x)\rvert$, and $w$ is all 1s exactly when $x$ is.

### Sources for this page
The problems are original or classic exercise types restated in our own words. Problems 1.1 and 1.4 use the classic accumulator version of reversal; 1.2 and 1.5 test the definitions of [[1-models-of-computation/01-strings#15-indices-substrings-and-subsequences|§1.5]]; 1.3 is built on the three-case split of [[1-models-of-computation/01-strings#14-more-than-one-path-up-the-mountain|§1.4]]; and the functions $\textsf{rot}$, $\textsf{zig}$ and $\textsf{inc}$ (1.6–1.8) are new, in the style of the book's Chapter 1 exercises and of the exams' induction problem. None is taken from a course exam or homework. Every identity, every line of every proof and every example is checked by brute force over all short strings (lengths up to 8–12) in `tools/practice/checks/ch01.py`.

*Next: [[practice/02-regular-languages|Chapter 2 practice]] · [[practice/index|all practice]]*
