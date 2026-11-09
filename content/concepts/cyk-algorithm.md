---
title: "CYK algorithm"
description: "Deciding whether a context-free grammar in Chomsky normal form generates a string, by dynamic programming over substrings: Gen?(A, i, j) for every nonterminal and substring, filled by increasing length, O(n³·L) time for L rules."
tags: [concept, algorithms, dynamic-programming, context-free]
aliases: ["CYK", "CKY", "CYK parsing", "Cocke–Younger–Kasami algorithm", "CYKParse"]
---

> [!definition] The CYK algorithm (Cocke–Younger–Kasami)
> Input: a grammar $G$ in [[concepts/chomsky-normal-form|Chomsky normal form]] with start symbol $S$, and a string $w[1\,..\,n]$, $n\ge1$. For every nonterminal $A$ and $1\le i\le j\le n$, let $\textsf{Gen?}(A,i,j)$ be $\textsf{True}$ iff $A\rightsquigarrow^* w[i\,..\,j]$. Then
> $$
> \textsf{Gen?}(A,i,j) = \begin{cases} [\,A\to w[i] \text{ is a rule}\,] & \text{if } i = j\\[2pt] \displaystyle\bigvee_{A\to BC}\ \bigvee_{k=i}^{j-1}\Big(\textsf{Gen?}(B,i,k)\wedge\textsf{Gen?}(C,k+1,j)\Big) & \text{if } i<j\end{cases}
> $$
> and $w\in L(G)$ iff $\textsf{Gen?}(S,1,n)$; $\varepsilon\in L(G)$ iff $S\to\varepsilon$ is a rule. Filled in a table by increasing length $j-i$, it takes $O(n^3L)$ time for a grammar with $L$ rules — $O(n^3)$ for a fixed grammar — and $O(n^2\lvert\Gamma\rvert)$ space.

**Why it works.** In Chomsky normal form, a parse tree of a string of length at least 2 has a root rule $A\to BC$ whose subtrees derive a **non-empty** prefix and a **non-empty** suffix. So the recurrence tries exactly the possible root rules and split points, and every call is on a shorter substring. That is why CNF is needed: with $\varepsilon$-rules ($S\to SS$, $S\rightsquigarrow\varepsilon$) or cycles of unit rules ($S\to A\to B\to S$) the recursion would call itself on the same substring forever.

> [!recipe] Recipe — writing it up in the dynamic-programming rubric
> 1. **Function:** $\textsf{Gen?}(A,i,j)$ is $\textsf{True}$ iff nonterminal $A$ derives the substring $w[i\,..\,j]$; we need $\textsf{Gen?}(S,1,n)$ (and the rule $S\to\varepsilon$ when $w = \varepsilon$).
> 2. **Recurrence** as above: base case $i = j$, recursive case over rules $A\to BC$ and splits $i\le k<j$.
> 3. **Memoization:** a boolean array $\textit{Gen}[1\,..\,\lvert\Gamma\rvert,\ 1\,..\,n,\ 1\,..\,n]$ (or one set of nonterminals per substring).
> 4. **Evaluation order:** by increasing length $j-i$; equivalently $j$ from 1 to $n$ (outer) and $i$ from $j-1$ down to 1 (inner).
> 5. **Time:** $O(n^2)$ substrings $\times$ $O(n)$ splits $\times$ $L$ rules $= O(n^3L)$.
>
> For a parse tree, remember one rule and split that made each entry true and walk down from $(S,1,n)$; to count parse trees, replace $\vee,\wedge$ by $+,\times$.

> [!trap]
> - **Not in CNF?** Convert first ([[1-models-of-computation/05-context-free-languages#59-the-cnf-conversion-algorithm|§5.9]]); with $\varepsilon$-rules or unit rules the recurrence is wrong or never stops.
> - **Splits are non-empty:** $k$ from $i$ to $j-1$. The empty string is handled by $S\to\varepsilon$ alone.
> - **Start symbol only:** the answer is $\textsf{Gen?}(S,1,n)$, not "some nonterminal derives $w$".
> - **Order:** rows with $i$ increasing read cells not yet computed. Erickson's note prints the inner loop as "$i\leftarrow n$ down to $j+1$"; it must be $j-1$ down to 1.
> - **Size of the grammar:** $O(n^3)$ only for a fixed grammar; CNF conversion can square a grammar's size.

**Example.** $L = \{\mathtt{0}^n\mathtt{1}^n\mid n\ge1\}$ in CNF: $S\to ZO\mid ZT$, $T\to XO$, $X\to ZO\mid ZT$, $Z\to\mathtt{0}$, $O\to\mathtt{1}$ ($X$ is a copy of $S$, because the start symbol may not appear on a right side). For $w = $ `0011`: the single symbols give $Z, Z, O, O$; among the substrings of length 2 only `01` $= w[2\,..\,3]$ is derivable, by $S$ and $X$ (rule $ZO$); of length 3 only `011` $= w[2\,..\,4]$, by $T$ ($X$ on `01`, then $O$); and $w[1\,..\,4]$ by $S$ and $X$ ($Z$ on `0`, then $T$ on `011`). $S$ is in the top cell, so `0011` $\in L$. For `0101`, both halves `01` contain $S$ and $X$, but no rule has a right side $XX$ or $SX$, and the top cell has no $S$.

**Where it appears.** [[4-lecture-notes/c-dynamic-programming-for-automata#c4-cfg-parsing|Lecture note C, §C.4]] (the recurrence, the algorithm, the corrected pseudocode and a full table), [[1-models-of-computation/05-context-free-languages#58-chomsky-normal-form|§5.8]] (the algorithm in one paragraph, as the payoff of Chomsky normal form), [[2-algorithms/03-dynamic-programming#34-the-pattern-smart-recursion|§3.4]] (the dynamic-programming pattern it follows).

Related: [[concepts/chomsky-normal-form]] · [[concepts/context-free-grammars]] · [[concepts/parse-trees-and-ambiguity]] · [[concepts/dynamic-programming]] · [[concepts/edit-distance]]
