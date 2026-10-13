---
title: "Practice — Chapter 2: Regular languages"
description: "8 practice problems (3 easy, 3 medium, 2 hard) on languages and regular expressions: ∅ versus {ε}, concatenation and star of small languages, reading and writing regular expressions with explanations, equivalence with witnesses, Arden's rule, and a structural induction on regular expressions, each with a folded hint and a worked solution."
tags: [practice, regular, midterm-1]
chapter: 2
---

*Practice for [[1-models-of-computation/02-regular-languages|Chapter 2]] · concepts: [[concepts/languages]] · [[concepts/regular-expressions]] · [[concepts/regular-languages]] · all practice: [[practice/index|hub]] · by difficulty: [[practice/easy|easy]] · [[practice/medium|medium]] · [[practice/hard|hard]] · [[practice/topics|by topic]]*

Work each problem on paper first. Open the **hint** only when stuck, and the **solution** only after you have an answer you would hand in. Every regular expression and every identity in the solutions has been checked by a script. All strings are over $\{\mathtt{0}, \mathtt{1}\}$, and, as in regular expressions, a single string may stand for the language that contains just that string.

## Easy

### 2.1 Empty things, products and stars

> [!easy] Easy · true or false · languages · Kleene star
> Answer each statement **Yes** (true for all languages involved) or **No**, with a one-sentence justification; for a No, give a counterexample.
>
> (a) $\varnothing\bullet\{\varepsilon\} = \{\varepsilon\}$.
>
> (b) $\{\mathtt{0},\mathtt{01}\}\bullet\{\mathtt{1},\mathtt{11}\}$ contains exactly four strings.
>
> (c) $(L^*)^* = L^*$ for every language $L$.
>
> (d) $(A\cup B)^* = A^*\cup B^*$ for all languages $A$ and $B$.
>
> (e) $\varnothing^+ = \varnothing$.
>
> (f) If $\varepsilon\in L$, then $L\bullet L = L$.
>
> *Source: original.*

> [!hint]- Hint
> Keep $\varnothing$ (no strings), $\{\varepsilon\}$ (one string) and $\varepsilon$ (a string) apart: a concatenation needs a string from *each* factor. For the "for all" statements, try one-string languages such as $\{\mathtt{0}\}$ and $\{\mathtt{1}\}$ first.

> [!solution]- Solution
> - **(a) No.** A concatenation needs a string from each factor and $\varnothing$ has none, so $\varnothing\bullet\{\varepsilon\} = \varnothing$ (Lemma 2.1(c)), which is not $\{\varepsilon\}$.
> - **(b) No.** It has three strings, $\mathtt{01}$, $\mathtt{011}$ and $\mathtt{0111}$, because two different pairs give the same string: $\mathtt{0}\bullet\mathtt{11} = \mathtt{01}\bullet\mathtt{1} = \mathtt{011}$.
> - **(c) Yes.** $L^*\subseteq(L^*)^*$ because every language is contained in its star, and $(L^*)^*\subseteq L^*$ because a concatenation of concatenations of strings of $L$ is itself a concatenation of strings of $L$.
> - **(d) No.** With $A = \{\mathtt{0}\}$ and $B = \{\mathtt{1}\}$, the string $\mathtt{01}$ is in $(A\cup B)^*$ but neither in $A^* = \mathtt{0}^*$ nor in $B^* = \mathtt{1}^*$. Only $A^*\cup B^*\subseteq(A\cup B)^*$ holds.
> - **(e) Yes.** $\varnothing^+ = \varnothing\bullet\varnothing^* = \varnothing\bullet\{\varepsilon\} = \varnothing$ by Lemma 2.1(c), even though $\varnothing^* = \{\varepsilon\}$ — as Lemma 2.2(c) predicts, $L^+\ne L^*$ when $\varepsilon\notin L$.
> - **(f) No.** $L = \{\varepsilon,\mathtt{0}\}$ contains $\varepsilon$, but $L\bullet L = \{\varepsilon,\mathtt{0},\mathtt{00}\}\ne L$. What does hold is $L\subseteq L\bullet L$, since $x = x\bullet\varepsilon$.
>
> **Answer.** (a) No. (b) No. (c) Yes. (d) No. (e) Yes. (f) No.

### 2.2 Read these expressions

> [!easy] Easy · regular expressions
> For each regular expression, describe its language in one English sentence, and list every string of length at most 2 that it matches.
>
> (a) $(\mathtt{1}+\mathtt{01})^*$
>
> (b) $(\mathtt{0}^*\mathtt{1}\mathtt{0}^*\mathtt{1}\mathtt{0}^*)^*$
>
> (c) $(\mathtt{00}+\mathtt{000})^*$
>
> (d) $(\mathtt{0}+\varnothing)^*\,\mathtt{1}\,\varnothing^*$
>
> *Source: original.*

> [!hint]- Hint
> Ask what each starred block contributes, and what the empty sequence of blocks gives. In (d), find $L(\mathtt{0}+\varnothing)$ and $L(\varnothing^*)$ first.

> [!solution]- Solution
> - **(a)** The blocks are $\mathtt{1}$ and $\mathtt{01}$, so every $\mathtt{0}$ is immediately followed by a $\mathtt{1}$ (equivalently: no $\mathtt{00}$, and no final $\mathtt{0}$). Conversely, a string with that property splits into such blocks by cutting after every $\mathtt{1}$. Length at most 2: $\varepsilon$, $\mathtt{1}$, $\mathtt{01}$, $\mathtt{11}$.
> - **(b)** Each block contains exactly two 1s, so every string matched has an even number of 1s; but each block contains at least one $\mathtt{1}$, so a non-empty string with no 1s is **not** matched. The language is $\varepsilon$ together with the strings that have an even, positive number of 1s. Length at most 2: $\varepsilon$, $\mathtt{11}$.
> - **(c)** Strings of 0s whose length is $2i+3j$ for some $i, j\ge0$ — every length except 1. So the language is $\{\mathtt{0}^n \mid n\ne1\}$, the same as $L(\varepsilon+\mathtt{000}^*)$. Length at most 2: $\varepsilon$, $\mathtt{00}$.
> - **(d)** $L(\mathtt{0}+\varnothing) = \{\mathtt{0}\}\cup\varnothing = \{\mathtt{0}\}$ and $L(\varnothing^*) = \{\varepsilon\}$, so the expression is equivalent to $\mathtt{0}^*\mathtt{1}$: any number of 0s followed by a single 1. Length at most 2: $\mathtt{1}$, $\mathtt{01}$.
>
> **Watch out:** (b) is *not* "an even number of 1s" — that language also contains $\mathtt{0}$, $\mathtt{00}$, $\mathtt{000}$, …, which have zero 1s. And in (d), $\varnothing^*$ is $\{\varepsilon\}$, not $\varnothing$, so the expression does not describe the empty language.
>
> **Answer.** (a) Every 0 is immediately followed by a 1: $\varepsilon$, $\mathtt{1}$, $\mathtt{01}$, $\mathtt{11}$. (b) $\varepsilon$ or an even, positive number of 1s: $\varepsilon$, $\mathtt{11}$. (c) $\mathtt{0}^n$ with $n\ne1$: $\varepsilon$, $\mathtt{00}$. (d) $\mathtt{0}^*\mathtt{1}$: $\mathtt{1}$, $\mathtt{01}$.

### 2.3 A missing empty string

> [!easy] Easy · find the error · regular expressions
> Let $L$ be the set of binary strings in which every $\mathtt{0}$ is followed, somewhere later in the string, by at least one $\mathtt{1}$. A student answers:
>
> *"$(\mathtt{0}+\mathtt{1})^*\mathtt{1}$. A string is in $L$ exactly when its last symbol is a 1, since that final 1 comes after every 0; $(\mathtt{0}+\mathtt{1})^*$ is everything before it."*
>
> Is the answer correct? If not, say exactly which strings it gets wrong, fix it, and say how the regular-expression rubric treats the slip.
>
> *Source: original.*

> [!solution]- Solution
> **The slip: $\varepsilon\in L$, but $\varepsilon$ does not match.** The empty string contains no 0 at all, so "every 0 is followed by a 1" holds for it vacuously. The rest of the explanation is right: a **non-empty** string is in $L$ if and only if it ends in $\mathtt{1}$ (if it ends in $\mathtt{0}$, that last 0 has nothing after it; if it ends in $\mathtt{1}$, that 1 comes after every 0). So $L = \{\varepsilon\}\cup L\big((\mathtt{0}+\mathtt{1})^*\mathtt{1}\big)$, and $\varepsilon$ is the **only** string the answer gets wrong.
>
> **Fix:** $\varepsilon+(\mathtt{0}+\mathtt{1})^*\mathtt{1}$, or equivalently $(\mathtt{0}^*\mathtt{1})^*$: blocks of 0s each closed by a 1, where the empty sequence of blocks gives $\varepsilon$.
>
> **Grading:** a single wrong string is the classic "one mistake" — typically a missing or extra $\varepsilon$ — and costs the smallest correctness deduction (2 of the 8 correctness points on an exam). An answer that is wrong on infinitely many strings would lose all 8.
>
> **Watch out:** test $\varepsilon$ explicitly, every time. Conditions of the form "every … is …" are true for strings that contain no "…" at all.
>
> **Answer.** Not correct: it misses exactly one string, $\varepsilon$. A correct answer is $\varepsilon+(\mathtt{0}+\mathtt{1})^*\mathtt{1}$ (or $(\mathtt{0}^*\mathtt{1})^*$).

## Medium

### 2.4 Three regular expressions

> [!medium] Medium · regular expressions
> Give a regular expression for each language, with a one-sentence explanation of each part. No proof is required.
>
> (a) Strings that contain both $\mathtt{00}$ and $\mathtt{11}$ as substrings.
>
> (b) Strings in which the number of 0s between any two consecutive 1s is even. (Two 1s are consecutive if no 1 lies between them; 0s before the first 1 or after the last 1 are unrestricted.)
>
> (c) Strings $w$ with $w_i = \mathtt{0}$ for every position $i$ that is a multiple of 3. (Positions are numbered from 1, so the condition is on $w_3$, $w_6$, $w_9$ and so on.)
>
> *Source: original.*

> [!hint]- Hint
> (a) "And" is hard for regular expressions, but here you can split by which of the two substrings occurs first. (b) Describe the first 1, then each later 1 together with the gap of 0s before it. (c) Cut the string into blocks of three symbols; the last block may be incomplete.

> [!solution]- Solution
> **(a) Idea.** An occurrence of $\mathtt{00}$ and an occurrence of $\mathtt{11}$ cannot overlap (they have no symbol in common), so one of them lies entirely before the other.
> $$
> (\mathtt{0}+\mathtt{1})^*\mathtt{00}(\mathtt{0}+\mathtt{1})^*\mathtt{11}(\mathtt{0}+\mathtt{1})^* + (\mathtt{0}+\mathtt{1})^*\mathtt{11}(\mathtt{0}+\mathtt{1})^*\mathtt{00}(\mathtt{0}+\mathtt{1})^*
> $$
> The first term is anything, then $\mathtt{00}$, then anything, then $\mathtt{11}$, then anything: an occurrence of $\mathtt{00}$ before an occurrence of $\mathtt{11}$. The second term is the same with the order reversed. Every string of the language has one of the two orders, and every string matched contains both substrings. **Check:** $\mathtt{0011}$, $\mathtt{1100}$ and $\mathtt{10011}$ match; $\mathtt{0110}$ (no $\mathtt{00}$), $\mathtt{0101}$ and $\varepsilon$ do not.
>
> **(b) Idea.** The 0s before the first 1 and after the last 1 are free; only the gaps between consecutive 1s are constrained.
> $$
> \mathtt{0}^* + \mathtt{0}^*\mathtt{1}\big((\mathtt{00})^*\mathtt{1}\big)^*\mathtt{0}^*
> $$
> The term $\mathtt{0}^*$ covers the strings with no 1, which have no gap to check. In the second term, $\mathtt{0}^*$ is the 0s before the first 1; $\mathtt{1}$ is the first 1; each $(\mathtt{00})^*\mathtt{1}$ is an even gap of 0s followed by the next 1; and the final $\mathtt{0}^*$ is the 0s after the last 1. **Check:** $\varepsilon$, $\mathtt{000}$, $\mathtt{0110}$, $\mathtt{1001}$ and $\mathtt{01001100}$ match; $\mathtt{101}$, $\mathtt{10001}$ and $\mathtt{11011}$ do not.
>
> **(c) Idea.** Positions $3k-2$, $3k-1$, $3k$ form the $k$th block of three, and only the third symbol of a *complete* block is constrained.
> $$
> \big((\mathtt{0}+\mathtt{1})(\mathtt{0}+\mathtt{1})\mathtt{0}\big)^*(\varepsilon+\mathtt{0}+\mathtt{1})(\varepsilon+\mathtt{0}+\mathtt{1})
> $$
> Each $(\mathtt{0}+\mathtt{1})(\mathtt{0}+\mathtt{1})\mathtt{0}$ is a complete block with a 0 in its third position, and the star allows any number of complete blocks; $(\varepsilon+\mathtt{0}+\mathtt{1})(\varepsilon+\mathtt{0}+\mathtt{1})$ is the incomplete last block, of length 0, 1 or 2, which contains no position divisible by 3. **Check:** $\varepsilon$, $\mathtt{11}$, $\mathtt{110}$ and $\mathtt{11011}$ match; $\mathtt{111}$ and $\mathtt{000001}$ do not.
>
> **Watch out:** in (b), $\mathtt{0}^*\big(\mathtt{1}(\mathtt{00})^*\big)^*$ looks plausible but forces an even number of 0s after the last 1, so it misses $\mathtt{10}$, $\mathtt{1000}$, …; in (c), leaving out the incomplete last block keeps only the strings whose length is divisible by 3. Each of these slips is wrong on infinitely many strings and loses all the correctness points.
>
> **Answer.** (a) $(\mathtt{0}+\mathtt{1})^*\mathtt{00}(\mathtt{0}+\mathtt{1})^*\mathtt{11}(\mathtt{0}+\mathtt{1})^* + (\mathtt{0}+\mathtt{1})^*\mathtt{11}(\mathtt{0}+\mathtt{1})^*\mathtt{00}(\mathtt{0}+\mathtt{1})^*$. (b) $\mathtt{0}^* + \mathtt{0}^*\mathtt{1}((\mathtt{00})^*\mathtt{1})^*\mathtt{0}^*$. (c) $((\mathtt{0}+\mathtt{1})(\mathtt{0}+\mathtt{1})\mathtt{0})^*(\varepsilon+\mathtt{0}+\mathtt{1})(\varepsilon+\mathtt{0}+\mathtt{1})$.

### 2.5 Equivalent or not

> [!medium] Medium · regular expressions · languages
> For each pair, decide whether the two regular expressions are equivalent. If they are, explain why; if not, give a shortest string that matches exactly one of them, and say whether one language contains the other.
>
> (a) $(\mathtt{0}+\mathtt{1})^*\mathtt{0}(\mathtt{0}+\mathtt{1})^*\mathtt{1}(\mathtt{0}+\mathtt{1})^*$ and $(\mathtt{0}+\mathtt{1})^*\mathtt{01}(\mathtt{0}+\mathtt{1})^*$
>
> (b) $\mathtt{1}(\mathtt{01})^*$ and $(\mathtt{10})^*\mathtt{1}$
>
> (c) $(\mathtt{01}+\mathtt{10})^*$ and $(\mathtt{01})^*(\mathtt{10})^*$
>
> (d) $(\mathtt{0}+\mathtt{01})^*$ and $\mathtt{0}^*(\mathtt{01})^*$
>
> *Source: original.*

> [!hint]- Hint
> List the short strings each side matches, in order of length, until the lists differ or a pattern appears. For an equivalence, argue both inclusions; in (a), look for a $\mathtt{0}$ that is *immediately* followed by a $\mathtt{1}$.

> [!solution]- Solution
> **Idea.** Equivalence needs an argument for both inclusions; non-equivalence needs one string, checked against both expressions.
>
> **(a) Equivalent.** Both describe the strings with a $\mathtt{0}$ somewhere before a $\mathtt{1}$. Right $\subseteq$ left: an occurrence of $\mathtt{01}$ is a 0 before a 1. Left $\subseteq$ right: if $w = x\mathtt{0}y\mathtt{1}z$, then the substring $\mathtt{0}y\mathtt{1}$ begins with 0 and contains a 1; the symbol just before its first 1 is a 0, so $w$ contains $\mathtt{01}$.
>
> **(b) Equivalent.** The languages are $\{\mathtt{1}(\mathtt{01})^n \mid n\ge0\}$ and $\{(\mathtt{10})^n\mathtt{1} \mid n\ge0\}$, and $\mathtt{1}(\mathtt{01})^n = (\mathtt{10})^n\mathtt{1}$ for every $n$: both are the alternating string $\mathtt{1010}\cdots\mathtt{01}$ of length $2n+1$ (by associativity, $\mathtt{1}\,\mathtt{01}\,\mathtt{01}\cdots\mathtt{01}$ regroups as $\mathtt{10}\,\mathtt{10}\cdots\mathtt{10}\,\mathtt{1}$). This is the "sliding" identity $x(yx)^* = (xy)^*x$.
>
> **(c) Not equivalent.** Shortest witness: $\mathtt{1001} = \mathtt{10}\bullet\mathtt{01}$ matches the left expression but not the right one, whose strings are some copies of $\mathtt{01}$ followed by some copies of $\mathtt{10}$. Every string matched by the right expression is a sequence of $\mathtt{01}$ and $\mathtt{10}$ blocks, so $L\big((\mathtt{01})^*(\mathtt{10})^*\big)\subsetneq L\big((\mathtt{01}+\mathtt{10})^*\big)$.
>
> **(d) Not equivalent.** Shortest witness: $\mathtt{010} = \mathtt{01}\bullet\mathtt{0}$ matches the left expression but not the right one, in which no $\mathtt{0}$ can come after a $\mathtt{01}$ block. Again $L\big(\mathtt{0}^*(\mathtt{01})^*\big)\subsetneq L\big((\mathtt{0}+\mathtt{01})^*\big)$: putting all the $\mathtt{0}$ blocks first is one particular order of the blocks.
>
> **Check:** in (c), both sides match exactly $\varepsilon$, $\mathtt{01}$, $\mathtt{10}$ among the strings of length at most 3; of length 4, the left side matches $\mathtt{0101}$, $\mathtt{0110}$, $\mathtt{1001}$, $\mathtt{1010}$ and the right side only $\mathtt{0101}$, $\mathtt{0110}$, $\mathtt{1010}$. In (d), the strings of length at most 2 agree ($\varepsilon$, $\mathtt{0}$, $\mathtt{00}$, $\mathtt{01}$), and $\mathtt{010}$ is the only difference of length 3.
>
> **Watch out:** "the two sides agree on every short string I tried" never proves equivalence — (c) agrees on everything shorter than 4.
>
> **Answer.** (a) Equivalent. (b) Equivalent. (c) Not equivalent: $\mathtt{1001}$; the right language is a proper subset of the left. (d) Not equivalent: $\mathtt{010}$; the right language is a proper subset of the left.

### 2.6 Solving three language equations

> [!medium] Medium · Arden's rule
> The languages $X$, $Y$, $Z$ satisfy
> $$
> X = \mathtt{0}X\cup\mathtt{1}Y\cup\{\varepsilon\},\qquad Y = \mathtt{0}X\cup\mathtt{1}Z\cup\{\varepsilon\},\qquad Z = \mathtt{1}Z\cup\{\varepsilon\}.
> $$
> (a) Use Arden's rule to find regular expressions for $Z$, $Y$ and $X$, and explain why the system has only one solution.
>
> (b) Describe $X$ in one English sentence.
>
> *Source: original.*

> [!hint]- Hint
> Solve the last equation first, substitute the result into the second, and then substitute the second into the first. Each time you apply Arden's rule, check that the language in front of the unknown does not contain $\varepsilon$.

> [!solution]- Solution
> **Idea.** Arden's rule (Lemma 2.3, [[1-models-of-computation/02-regular-languages#22-building-languages|§2.2]]): if $\varepsilon\notin A$, then $L = AL\cup B$ holds **if and only if** $L = A^*B$. Eliminate one unknown at a time, from the bottom up.
>
> **(a)** *$Z$.* The equation $Z = \mathtt{1}Z\cup\{\varepsilon\}$ has $A = \{\mathtt{1}\}$, and $\varepsilon\notin A$, so its only solution is $Z = \mathtt{1}^*\{\varepsilon\} = \mathtt{1}^*$.
>
> *$Y$ in terms of $X$.* Substituting, $Y = \mathtt{0}X\cup\mathtt{1}\mathtt{1}^*\cup\{\varepsilon\} = \mathtt{0}X\cup\mathtt{1}^*$, because $\mathtt{1}\mathtt{1}^*\cup\{\varepsilon\} = \mathtt{1}^+\cup\{\varepsilon\} = \mathtt{1}^*$ (Lemma 2.2(a)).
>
> *$X$.* Substituting into the first equation and distributing (Lemma 2.1(f)),
> $$
> X = \mathtt{0}X\cup\mathtt{1}(\mathtt{0}X\cup\mathtt{1}^*)\cup\{\varepsilon\} = (\mathtt{0}\cup\mathtt{10})X\cup(\mathtt{1}\mathtt{1}^*\cup\{\varepsilon\}) = (\mathtt{0}\cup\mathtt{10})X\cup\mathtt{1}^*.
> $$
> Here $A = \{\mathtt{0},\mathtt{10}\}$ does not contain $\varepsilon$, so Arden's rule gives $X = (\mathtt{0}+\mathtt{10})^*\mathtt{1}^*$, and then $Y = \mathtt{0}(\mathtt{0}+\mathtt{10})^*\mathtt{1}^* + \mathtt{1}^*$.
>
> *Only one solution.* If $(X, Y, Z)$ is any solution, then $Z$ must be $\mathtt{1}^*$, so $Y$ must be $\mathtt{0}X\cup\mathtt{1}^*$, so $X$ satisfies $X = (\mathtt{0}\cup\mathtt{10})X\cup\mathtt{1}^*$ and must be $(\mathtt{0}+\mathtt{10})^*\mathtt{1}^*$. Each "must" is the *only if* half of Arden's rule, which needs $\varepsilon\notin A$.
>
> **(b)** $X$ is the set of strings that do not contain $\mathtt{110}$. In a string of $(\mathtt{0}+\mathtt{10})^*$ every 1 is immediately followed by a 0, so it contains no $\mathtt{11}$; after it comes a final block of 1s, which has no 0 after it, so no $\mathtt{110}$ can appear. Conversely, cut a string without $\mathtt{110}$ just before its final block of 1s, so that the first part is empty or ends in $\mathtt{0}$. If some 1 in the first part were followed by another 1, the run of 1s containing them would be followed by a 0 (the first part ends in 0), and the last two 1s of that run together with this 0 would form $\mathtt{110}$. So every 1 of the first part is immediately followed by a 0, and the first part is in $(\mathtt{0}+\mathtt{10})^*$.
>
> **Check:** $\mathtt{0}$, $\mathtt{1011}$, $\mathtt{0101}$ and $\mathtt{111}$ are in $X$; $\mathtt{110}$ and $\mathtt{01101}$ are not. The other two unknowns have meanings too: $Y$ is the set of strings $y$ such that $\mathtt{1}y$ contains no $\mathtt{110}$, and $Z$ the set of strings $z$ such that $\mathtt{11}z$ contains none — which is why $Z = \mathtt{1}^*$.
>
> **Watch out:** Arden's rule gives the *only* solution only when $\varepsilon\notin A$; with $\varepsilon\in A$ it gives just the smallest one.
>
> **Answer.** $Z = \mathtt{1}^*$, $Y = \mathtt{0}(\mathtt{0}+\mathtt{10})^*\mathtt{1}^*+\mathtt{1}^*$, and $X = (\mathtt{0}+\mathtt{10})^*\mathtt{1}^*$: the strings with no substring $\mathtt{110}$. The solution is unique because neither coefficient, $\mathtt{1}$ or $\mathtt{0}+\mathtt{10}$, contains $\varepsilon$.

## Hard

### 2.7 Two careful regular expressions

> [!hard] Hard · regular expressions
> Give a regular expression for each language, with an English explanation of every part, and test it on all strings of length at most 3. No proof is required.
>
> (a) Strings that contain the substring $\mathtt{11}$ exactly once. (Occurrences may overlap: $\mathtt{111}$ contains $\mathtt{11}$ twice.)
>
> (b) Strings in which every $\mathtt{0}$ has a $\mathtt{1}$ as a neighbor: $w_{i-1} = \mathtt{1}$ or $w_{i+1} = \mathtt{1}$ for every position $i$ with $w_i = \mathtt{0}$.
>
> *Source: original.*

> [!hint]- Hint
> (a) Write the string as $x\,\mathtt{11}\,y$ around its one occurrence. What must $x$ and $y$ avoid, and how may $x$ end and $y$ begin? (b) View the string as blocks of 1s separated by blocks of 0s: which blocks of 0s are allowed between two blocks of 1s, and which at the two ends?

> [!solution]- Solution
> **(a) Idea.** Around its only occurrence the string is $x\,\mathtt{11}\,y$, where $x$ and $y$ contain no $\mathtt{11}$, $x$ does not end in $\mathtt{1}$, and $y$ does not begin with $\mathtt{1}$ — otherwise a second, overlapping occurrence appears. The strings with no $\mathtt{11}$ that are empty or end in $\mathtt{0}$ are exactly the sequences of blocks $\mathtt{0}$ and $\mathtt{10}$; symmetrically, those that are empty or begin with $\mathtt{0}$ are the sequences of blocks $\mathtt{0}$ and $\mathtt{01}$.
> $$
> (\mathtt{0}+\mathtt{10})^*\,\mathtt{11}\,(\mathtt{0}+\mathtt{01})^*
> $$
> - $(\mathtt{0}+\mathtt{10})^*$ is the part before the occurrence: every 1 in it is immediately followed by a 0, so it contains no $\mathtt{11}$ and is empty or ends in $\mathtt{0}$;
> - $\mathtt{11}$ is the one occurrence;
> - $(\mathtt{0}+\mathtt{01})^*$ is the part after it: every 1 in it is immediately preceded by a 0, so it contains no $\mathtt{11}$ and is empty or begins with $\mathtt{0}$.
>
> No other occurrence can straddle a boundary, because the symbol next to $\mathtt{11}$ on either side is a 0, if there is one. **Check:** of the 15 strings of length at most 3, the expression matches exactly $\mathtt{11}$, $\mathtt{011}$ and $\mathtt{110}$, which are exactly the ones with one occurrence ($\mathtt{111}$ has two).
>
> **(b) Idea.** A non-empty string with no 1 has a 0 without a 1 next to it, so $\varepsilon$ is the only string of the language without a 1. Otherwise cut the string into blocks of 1s separated by blocks of 0s. A block of 0s *between* two blocks of 1s may have length 1 or 2, because then each of its 0s is next to one of the two surrounding 1s, while a block of three or more 0s has a middle 0 with no 1 next to it. A block of 0s at the *beginning* or the *end* touches a 1 on one side only, so it has length at most 1.
> $$
> \varepsilon + (\varepsilon+\mathtt{0})\,\mathtt{1}\,(\mathtt{1}+\mathtt{01}+\mathtt{001})^*(\varepsilon+\mathtt{0})
> $$
> - $\varepsilon$: the string with no 1 (there is no 0 to check);
> - $(\varepsilon+\mathtt{0})$: at most one leading 0, which touches the first 1;
> - $\mathtt{1}$: the first 1;
> - $(\mathtt{1}+\mathtt{01}+\mathtt{001})^*$: each later 1, preceded by the zero, one or two 0s that separate it from the previous 1;
> - $(\varepsilon+\mathtt{0})$: at most one trailing 0, which touches the last 1.
>
> **Check:** of the strings of length at most 3, the expression matches $\varepsilon$, $\mathtt{1}$, $\mathtt{01}$, $\mathtt{10}$, $\mathtt{11}$, $\mathtt{010}$, $\mathtt{011}$, $\mathtt{101}$, $\mathtt{110}$ and $\mathtt{111}$, and rejects $\mathtt{0}$, $\mathtt{00}$, $\mathtt{000}$, $\mathtt{001}$ and $\mathtt{100}$ — each of which has a 0 with no 1 next to it. Longer: $\mathtt{1001}$ matches, and $\mathtt{10001}$ does not (its middle 0 is alone).
>
> **Grading notes.** The exam rubric gives 2 points for syntax and 8 for correctness ([[0-toolkit/06-how-exams-are-graded|how exams are graded]]). Typical losses here: in (a), $(\mathtt{0}+\mathtt{1})^*\mathtt{11}(\mathtt{0}+\mathtt{1})^*$ means "at least once" and matches $\mathtt{111}$, $\mathtt{1111}$, …; and $(\mathtt{0}+\mathtt{10})^*\mathtt{11}(\mathtt{0}+\mathtt{10})^*$ matches $\mathtt{1110}$ (two occurrences) while missing $\mathtt{1101}$, $\mathtt{110101}$ and many more. Both are wrong on infinitely many strings, so no correctness points. In (b), forgetting the term $\varepsilon$ is a single wrong string (the small deduction), but allowing $\mathtt{00}$ at either end matches $\mathtt{001}$, $\mathtt{0011}$, … and loses everything.
>
> **Answer.** (a) $(\mathtt{0}+\mathtt{10})^*\mathtt{11}(\mathtt{0}+\mathtt{01})^*$. (b) $\varepsilon+(\varepsilon+\mathtt{0})\mathtt{1}(\mathtt{1}+\mathtt{01}+\mathtt{001})^*(\varepsilon+\mathtt{0})$.

### 2.8 An expression for all prefixes

> [!hard] Hard · regex induction · regular expressions
> For a language $L$, let $\textsf{Pre}(L) := \{x \mid xy\in L \text{ for some string } y\}$ be the set of all prefixes of strings in $L$. For a regular expression $R$ that does **not** use the symbol $\varnothing$, define the expression $\textsf{pre}(R)$ by recursion on $R$:
> - $\textsf{pre}(w) := \varepsilon + w_1 + w_1w_2 + \cdots + w_1w_2\cdots w_n$ if $R$ is a string $w = w_1w_2\cdots w_n$ (so $\textsf{pre}(\varepsilon) = \varepsilon$);
> - $\textsf{pre}(S+T) := \textsf{pre}(S) + \textsf{pre}(T)$;
> - $\textsf{pre}(ST) := \textsf{pre}(S) + S\,\textsf{pre}(T)$;
> - $\textsf{pre}(S^*) := S^*\,\textsf{pre}(S)$.
>
> (a) Compute $\textsf{pre}\big((\mathtt{01})^*\mathtt{1}\big)$ and describe its language in English.
>
> (b) Prove that $L(\textsf{pre}(R)) = \textsf{Pre}(L(R))$ for every regular expression $R$ that does not use $\varnothing$.
>
> (c) Where does your proof use the assumption that $R$ does not use $\varnothing$? Extend the definition by $\textsf{pre}(\varnothing) := \varnothing$, and give an expression $R$ for which $L(\textsf{pre}(R))\ne\textsf{Pre}(L(R))$.
>
> *Source: original.*

> [!hint]- Hint
> Use the five-case template of [[1-models-of-computation/02-regular-languages#26-proofs-about-regular-expressions|§2.6]] and prove a set equality in each case. A prefix of $xy$ is either a prefix of $x$, or $x$ followed by a prefix of $y$; a prefix of $x_1x_2\cdots x_k$ is $x_1\cdots x_{i-1}$ followed by a prefix of $x_i$. To go back from a prefix of $x$ to a prefix of some $xy$, you need a string $y\in L(T)$ — Lemma 2.4 provides one.

> [!solution]- Solution
> **Idea.** Follow the cases of the definition and describe, in each case, the prefixes of the strings that case builds. Lemma 2.4 (an expression without $\varnothing$ has a non-empty language) is needed twice: to extend a prefix of $x\in L(S)$ to a string $xy\in L(S)L(T)$, and to get $\varepsilon\in\textsf{Pre}(L(S))$ in the star case.
>
> **(a)** With $S = (\mathtt{01})^*$ and $T = \mathtt{1}$:
> $$
> \textsf{pre}\big((\mathtt{01})^*\mathtt{1}\big) = \textsf{pre}\big((\mathtt{01})^*\big) + (\mathtt{01})^*\,\textsf{pre}(\mathtt{1}) = (\mathtt{01})^*(\varepsilon+\mathtt{0}+\mathtt{01}) + (\mathtt{01})^*(\varepsilon+\mathtt{1}),
> $$
> which is equivalent to $(\mathtt{01})^*(\varepsilon+\mathtt{0}+\mathtt{1})$, because $(\mathtt{01})^*\mathtt{01}$ adds nothing to $(\mathtt{01})^*$. In English: some copies of $\mathtt{01}$, followed by at most one more symbol. Indeed, $L\big((\mathtt{01})^*\mathtt{1}\big) = \{\mathtt{1}, \mathtt{011}, \mathtt{01011}, \dots\}$, and the prefixes of these strings are exactly the strings just described.
>
> **(b)** Let $R$ be an arbitrary regular expression that does not use $\varnothing$. Assume that $L(\textsf{pre}(R')) = \textsf{Pre}(L(R'))$ for every proper subexpression $R'$ of $R$; each of them is $\varnothing$-free too. There are five cases.
> - **$R = \varnothing$.** Impossible, because $R$ does not use $\varnothing$.
> - **$R$ is a string $w = w_1\cdots w_n$.** $\textsf{Pre}(\{w\})$ is the set of prefixes of $w$, which are exactly $w[1..j]$ for $0\le j\le n$ ([[1-models-of-computation/01-strings#15-indices-substrings-and-subsequences|§1.5]]): the strings of $L(\textsf{pre}(w))$.
> - **$R = S+T$.** A string is a prefix of a string in $L(S)\cup L(T)$ if and only if it is a prefix of a string in $L(S)$ or of a string in $L(T)$. So $\textsf{Pre}(L(R)) = \textsf{Pre}(L(S))\cup\textsf{Pre}(L(T)) = L(\textsf{pre}(S))\cup L(\textsf{pre}(T)) = L(\textsf{pre}(R))$, by the induction hypothesis for $S$ and $T$.
> - **$R = ST$.** We show $\textsf{Pre}(L(S)L(T)) = \textsf{Pre}(L(S))\cup L(S)\,\textsf{Pre}(L(T))$; the hypothesis for $S$ and $T$ turns the right side into $L(\textsf{pre}(S) + S\,\textsf{pre}(T))$.
>   - $\subseteq$: let $zu = xy$ with $x\in L(S)$ and $y\in L(T)$. If $\lvert z\rvert\le\lvert x\rvert$, then $z$ is the prefix of $x$ of length $\lvert z\rvert$, so $z\in\textsf{Pre}(L(S))$. Otherwise $z = xp$, where $p$ consists of the next $\lvert z\rvert-\lvert x\rvert$ symbols; then $xpu = xy$ gives $pu = y$ by cancellation, so $p\in\textsf{Pre}(L(T))$ and $z\in L(S)\,\textsf{Pre}(L(T))$.
>   - $\supseteq$: if $zu = x\in L(S)$, then $L(T)$ contains some string $y$, by Lemma 2.4 since $T$ does not use $\varnothing$; so $z(uy) = xy\in L(R)$ and $z\in\textsf{Pre}(L(R))$. If $z = xp$ with $x\in L(S)$ and $pu = y\in L(T)$, then $zu = xy\in L(R)$.
> - **$R = S^*$.** We show $\textsf{Pre}(L(S)^*) = L(S)^*\,\textsf{Pre}(L(S))$; the hypothesis for $S$ turns the right side into $L(S^*\,\textsf{pre}(S))$.
>   - $\subseteq$: let $zu = x_1x_2\cdots x_k$ with every $x_j\in L(S)$. If $z = \varepsilon$: $L(S)$ is not empty (Lemma 2.4), and $\varepsilon$ is a prefix of each of its strings, so $z = \varepsilon\bullet\varepsilon\in L(S)^*\,\textsf{Pre}(L(S))$. Otherwise let $i$ be the smallest index with $\lvert z\rvert\le\lvert x_1\cdots x_i\rvert$; then $z = x_1\cdots x_{i-1}\,p$, where $p$ is a prefix of $x_i$, so $z\in L(S)^*\,\textsf{Pre}(L(S))$.
>   - $\supseteq$: if $z = x_1\cdots x_{i-1}\,p$ with all $x_j\in L(S)$ and $pu = x_i\in L(S)$, then $zu = x_1\cdots x_i\in L(S)^*$.
>
> In all five cases, $L(\textsf{pre}(R)) = \textsf{Pre}(L(R))$. $\blacksquare$
>
> **(c)** The assumption is used through Lemma 2.4 in two places: in the case $ST$ ($\supseteq$), to find a string $y\in L(T)$, and in the case $S^*$ ($\subseteq$, $z = \varepsilon$), to get $\varepsilon\in\textsf{Pre}(L(S))$. Both fail when the language may be empty. For $R = \mathtt{0}\varnothing$: $L(R) = \varnothing$, so $\textsf{Pre}(L(R)) = \varnothing$, but $\textsf{pre}(\mathtt{0}\varnothing) = (\varepsilon+\mathtt{0}) + \mathtt{0}\varnothing$ denotes $\{\varepsilon,\mathtt{0}\}$. For $R = \varnothing^*$: $\textsf{Pre}(\{\varepsilon\}) = \{\varepsilon\}$, but $\textsf{pre}(\varnothing^*) = \varnothing^*\varnothing$ denotes $\varnothing$.
>
> **Check:** in (a), the strings of length at most 3 of $(\mathtt{01})^*(\varepsilon+\mathtt{0}+\mathtt{1})$ are $\varepsilon$, $\mathtt{0}$, $\mathtt{1}$, $\mathtt{01}$, $\mathtt{010}$ and $\mathtt{011}$ — exactly the prefixes of length at most 3 of the strings $\mathtt{1}$, $\mathtt{011}$ and $\mathtt{01011}$ of $L\big((\mathtt{01})^*\mathtt{1}\big)$ (longer strings of the language add no new short prefixes).
>
> **Watch out:** in the star case the hypothesis covers $S$, not $S^*$; the argument about $x_1x_2\cdots x_k$ is what handles the star. And since every non-empty regular language has a $\varnothing$-free expression (Lemma 2.5), the result shows that $\textsf{Pre}(L)$ is regular for every regular language $L$ ($\textsf{Pre}(\varnothing) = \varnothing$ is regular too).
>
> **Answer.** (a) $(\mathtt{01})^*(\varepsilon+\mathtt{0}+\mathtt{01}) + (\mathtt{01})^*(\varepsilon+\mathtt{1})\equiv(\mathtt{01})^*(\varepsilon+\mathtt{0}+\mathtt{1})$: some copies of $\mathtt{01}$, then at most one more symbol. (b) Structural induction with the set identities $\textsf{Pre}(A\cup B) = \textsf{Pre}(A)\cup\textsf{Pre}(B)$, $\textsf{Pre}(AB) = \textsf{Pre}(A)\cup A\,\textsf{Pre}(B)$ for $B\ne\varnothing$, and $\textsf{Pre}(A^*) = A^*\,\textsf{Pre}(A)$ for $A\ne\varnothing$. (c) Through Lemma 2.4, in the cases $ST$ and $S^*$; $R = \mathtt{0}\varnothing$ and $R = \varnothing^*$ break the extended definition.

### Sources for this page
The problems are original or classic exercise types restated in our own words: identities from Lemmas 2.1–2.2 on small languages (2.1); reading and writing regular expressions in the style of [[1-models-of-computation/02-regular-languages#23-regular-languages-and-regular-expressions|§2.3]] (2.2–2.4, 2.7); equivalence and non-equivalence with witnesses (2.5, where (b) is the classic sliding identity); a three-equation system solved with Arden's rule (2.6); and a structural recursion on expressions in the spirit of the book's reversal example and Lemmas 2.4–2.5 (2.8). None is taken from a course exam or homework. Every regular expression is compared exactly, by automaton equivalence, with an automaton built independently from the English description; every identity and counterexample is checked on all short strings; and the construction of 2.8 is verified on every $\varnothing$-free expression of size at most 6, all in `tools/practice/checks/ch02.py`.

*Previous: [[practice/01-strings|Chapter 1 practice]] · next: [[practice/03-finite-state-machines|Chapter 3 practice]] · [[practice/index|all practice]]*
