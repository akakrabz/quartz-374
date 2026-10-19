---
title: "Parse trees and ambiguity"
description: "A parse tree records how a grammar builds a string; a grammar is ambiguous when some string has two parse trees. How to show ambiguity, how to remove it, and why it matters for meaning but not for the language."
tags: [concept, context-free, midterm-1]
aliases: ["parse tree", "ambiguous grammar", "inherently ambiguous", "leftmost derivation"]
---

> [!definition] Definition — parse tree, ambiguity
> A **parse tree** for a string $w$ in a grammar $G$ is a rooted ordered tree whose root is the start symbol, whose internal nodes are nonterminals, whose leaves are terminals or $\varepsilon$ and spell $w$ from left to right, and in which the children of every node $A$ spell the right side of some rule $A\to\omega$. A string is **ambiguous** if it has more than one parse tree, and a grammar is **ambiguous** if some string is. A context-free language is **inherently ambiguous** if every grammar for it is ambiguous.

**Where it comes from.** A derivation fixes an order of rule applications; a parse tree keeps only which rule built which piece. Each parse tree corresponds to exactly one **leftmost derivation** (always expand the leftmost nonterminal), so "two parse trees" and "two leftmost derivations" mean the same thing. Ambiguity never changes $L(G)$, but compilers read meaning off the tree: $\mathtt{1}-\mathtt{1}-\mathtt{1}$ is $-1$ or $1$ depending on the grouping.

> [!recipe] Recipe — showing and removing ambiguity
> 1. **Ambiguous:** exhibit one string and two different parse trees, or two different leftmost derivations.
> 2. **Remove it:** choose one canonical way to build each string and let the grammar allow only that one — produce optional pieces in a fixed order, use one nonterminal per precedence level ($E\to E+T\mid T$, $T\to T\times F\mid F$), and recurse on one side only to fix associativity.
> 3. **Unambiguous:** show by induction that at every step the string splits in only one way.

> [!trap]
> - Two different derivations are not enough — they may build the same tree. Compare trees, or leftmost derivations.
> - Ambiguity belongs to the grammar, not the language: the example below has both kinds of grammar. Inherently ambiguous languages do exist (a standard fact; for example $\{\mathtt{0}^i\mathtt{1}^j\mathtt{2}^k \mid i=j \text{ or } j=k\}$).
> - The grading rubric does not penalize an ambiguous grammar.

**Example.** $S\to\mathtt{0}S\mathtt{1}\mid\mathtt{0}S\mid\varepsilon$ generates $\{\mathtt{0}^m\mathtt{1}^n \mid m\ge n\}$, ambiguously: `001` has two leftmost derivations,
$$
S\rightsquigarrow\mathtt{0}S\mathtt{1}\rightsquigarrow\mathtt{00}S\mathtt{1}\rightsquigarrow\mathtt{001}
\qquad\text{and}\qquad
S\rightsquigarrow\mathtt{0}S\rightsquigarrow\mathtt{00}S\mathtt{1}\rightsquigarrow\mathtt{001},
$$
depending on which `0` is matched with the `1`. (In general $\mathtt{0}^m\mathtt{1}^n$ has $\binom{m}{n}$ parse trees.) Producing the unmatched 0s first removes the choice: $S\to\mathtt{0}S\mid T$, $T\to\mathtt{0}T\mathtt{1}\mid\varepsilon$ generates the same language with exactly one parse tree per string.

**Where it appears.** [[1-models-of-computation/05-context-free-languages#52-parse-trees-and-ambiguity|§5.2]] (definitions; $S\to\mathtt{1}\mid S+S$ versus $S\to\mathtt{1}\mid\mathtt{1}+S$), [[1-models-of-computation/05-context-free-languages#54-more-examples|§5.4]] (balanced parentheses both ways; precedence in the expression grammar), [[1-models-of-computation/05-context-free-languages#58-chomsky-normal-form|§5.8]] (parse trees of CNF grammars are full binary trees), [[1-models-of-computation/02-regular-languages#25-regular-expression-trees|§2.5]] (expression trees).

**Practice.** [[practice/topics#parse-trees-ambiguity-and-chomsky-normal-form|Parse trees, ambiguity and Chomsky normal form]] (4 problems) — for example [[practice/05-context-free-languages#51-closure-and-ambiguity-true-or-false|5.1 Closure and ambiguity, true or false]] (easy), [[practice/05-context-free-languages#56-the-dangling-else|5.6 The dangling else]] (medium).

Related: [[concepts/context-free-grammars]] · [[concepts/chomsky-normal-form]] · [[concepts/regular-expressions]] · [[concepts/recursive-automata]]
