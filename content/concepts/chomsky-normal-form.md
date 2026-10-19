---
title: "Chomsky normal form"
description: "Grammars whose rules are all A → BC or A → a (plus S → ε): every parse tree is a full binary tree, so a string of length n takes exactly 2n − 1 derivation steps. The definition, why it is useful, and the conversion algorithm step by step."
tags: [concept, context-free, midterm-1]
aliases: ["CNF grammar", "CNF conversion", "Chomsky form"]
---

> [!definition] Definition — Chomsky normal form (CNF)
> A grammar is in **Chomsky normal form** if the start symbol $S$ appears on no right side, the rule $S\to\varepsilon$ is allowed, and every other rule has one of two forms: $A\to BC$ (two nonterminals) or $A\to a$ (one terminal).

> [!key] Theorem 5.7, and the $2n-1$ fact
> Every context-free grammar of total length $L$ can be converted into an equivalent grammar in CNF of length $O(L^2)$, in $O(L^2)$ time. In a CNF grammar, every parse tree of a string of length $n\ge1$ has exactly $2n-1$ nonterminal nodes — $n-1$ using rules $A\to BC$ and $n$ using rules $A\to a$ — so every derivation of it has exactly $2n-1$ steps.

**Why it is useful.** In a general grammar, $\varepsilon$-rules and unit rules $A\to B$ add steps that produce nothing, so a short string can have arbitrarily long derivations. In CNF every step either splits a piece in two or produces one symbol. So membership can be decided by trying every derivation of $2n-1$ steps — or quickly by dynamic programming (standard: the CYK algorithm, $O(n^3)$ time for a fixed grammar) — and inductions over derivations get just two cases.

> [!recipe] Recipe — the conversion (§5.9), in order
> 0. Add a new start symbol $S'$ and the rule $S'\to S$.
> 1. **Split long rules:** replace $A\to X\alpha$, where $X$ is one symbol and $\lvert\alpha\rvert\ge2$, by $A\to XB$ and $B\to\alpha$ with a new $B$, until every right side has length at most 2.
> 2. **Find the nullable** nonterminals ($A\rightsquigarrow^*\varepsilon$) with a fixed-point loop.
> 3. **Remove $\varepsilon$-rules:** delete every $A\to\varepsilon$, and add every non-empty variant of each rule with nullable symbols left out; add $S'\to\varepsilon$ if $S'$ is nullable.
> 4. **Merge** nonterminals that derive each other through unit rules ($A\rightsquigarrow^*B\rightsquigarrow^*A$).
> 5. **Remove unit rules** $A\to B$ by copying $B$'s rules to $A$, in reverse topological order.
> 6. **Protect terminals:** in every right side of length 2, replace each terminal $a$ by a new nonterminal $T_a$ with the rule $T_a\to a$.

> [!trap]
> - Split long rules *before* removing $\varepsilon$-rules: a right side with $k$ nullable symbols has $2^k$ variants.
> - Removing $\varepsilon$-rules creates unit rules ($A\to BC$ with $B$ nullable gives the unit rule $A\to C$), so unit rules go after.
> - $A\to aB$, $A\to BCD$ and $A\to B$ are not CNF; only the start symbol may have an $\varepsilon$-rule, and only if $\varepsilon$ is in the language.

**Example.** Palindromes: $P\to\mathtt{0}P\mathtt{0}\mid\mathtt{1}P\mathtt{1}\mid\mathtt{0}\mid\mathtt{1}\mid\varepsilon$. Steps 0–1 give $S'\to P,$ $P\to\mathtt{0}X\mid\mathtt{1}Y\mid\mathtt{0}\mid\mathtt{1}\mid\varepsilon,$ $X\to P\mathtt{0}$ and $Y\to P\mathtt{1}$. The nullable nonterminals are $P$ and $S'$, so step 3 gives $X\to P\mathtt{0}\mid\mathtt{0},$ $Y\to P\mathtt{1}\mid\mathtt{1}$ and $S'\to P\mid\varepsilon$. Steps 5–6 then give
$$
\begin{aligned}
S' &\to T_{\mathtt{0}}X \mid T_{\mathtt{1}}Y \mid \mathtt{0} \mid \mathtt{1} \mid \varepsilon, &
P &\to T_{\mathtt{0}}X \mid T_{\mathtt{1}}Y \mid \mathtt{0} \mid \mathtt{1},\\
X &\to PT_{\mathtt{0}} \mid \mathtt{0}, &
Y &\to PT_{\mathtt{1}} \mid \mathtt{1},\\
T_{\mathtt{0}} &\to \mathtt{0}, &
T_{\mathtt{1}} &\to \mathtt{1}.
\end{aligned}
$$
For instance, `010` has one parse tree, with the $2\cdot3-1 = 5$ nonterminal nodes $S'$, $T_{\mathtt{0}}$, $X$, $P$, $T_{\mathtt{0}}$.

**Where it appears.** [[1-models-of-computation/05-context-free-languages#58-chomsky-normal-form|§5.8]] (definition, binary parse trees), [[1-models-of-computation/05-context-free-languages#59-the-cnf-conversion-algorithm|§5.9]] (Theorem 5.7; the algorithm on the book's running example), [[1-models-of-computation/05-context-free-languages#53-from-grammar-to-language|§5.3]] (why $\varepsilon$-rules complicate proofs), [[1-models-of-computation/05-context-free-languages#52-parse-trees-and-ambiguity|§5.2]] (parse trees).

**Practice.** [[practice/topics#parse-trees-ambiguity-and-chomsky-normal-form|Parse trees, ambiguity and Chomsky normal form]] (4 problems) — for example [[practice/05-context-free-languages#51-closure-and-ambiguity-true-or-false|5.1 Closure and ambiguity, true or false]] (easy), [[practice/05-context-free-languages#56-the-dangling-else|5.6 The dangling else]] (medium).

Related: [[concepts/context-free-grammars]] · [[concepts/parse-trees-and-ambiguity]] · [[concepts/recursive-automata]]
