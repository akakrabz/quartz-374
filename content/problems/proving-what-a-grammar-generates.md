---
title: "Worked problem — Proving what a grammar generates"
description: "The grammar S → 0S11 | 0S | ε generates exactly the strings 0^m 1^(2n) with m ≥ n ≥ 0: both inclusions proved in full as a model answer, with the base cases, the role of the ε-rule, why the induction hypothesis applies, and a note on ambiguity."
tags: [problem, context-free, midterm-1]
---

*Problem · a grammar-correctness proof: two inductions, graded with the induction rubric · uses [[1-models-of-computation/05-context-free-languages#53-from-grammar-to-language|§5.3]] · concepts: [[concepts/context-free-grammars]], [[concepts/induction-on-strings]], [[concepts/parse-trees-and-ambiguity]]*

> [!question] Problem
> Let $G$ be the grammar with one nonterminal $S$ and the rules
> $$
> S\to\mathtt{0}S\mathtt{11}\mid\mathtt{0}S\mid\varepsilon ,
> $$
> and let $L = \{\mathtt{0}^m\mathtt{1}^{2n} \mid m\ge n\ge 0\}$: a block of 0s followed by an even number of 1s, with at least one 0 for every two 1s.
>
> (a) Prove that $L\subseteq L(G)$.
>
> (b) Prove that $L(G)\subseteq L$.
>
> (c) Is $G$ ambiguous? Does that matter for (a) and (b)?

**Test the claim before proving it.** The strings of length at most 6 that $G$ generates are $\varepsilon$, `0`, `00`, `011`, `000`, `0000`, `0011`, `00000`, `00011`, `000000`, `000011`, `001111` — exactly the strings $\mathtt{0}^m\mathtt{1}^{2n}$ with $m\ge n$ of that length. `0111` (an odd number of 1s) and `01111` (too few 0s) are correctly missing. Reading the rules explains why: $S\to\mathtt{0}S\mathtt{11}$ adds one 0 and two 1s, and $S\to\mathtt{0}S$ adds an extra 0, always on the outside.

## (a) Everything in L is generated

**Idea.** Build a derivation from the outside in. If the string has 1s, peel off a `0` in front and `11` at the back (rule $S\to\mathtt{0}S\mathtt{11}$); if it has none, peel off one `0` (rule $S\to\mathtt{0}S$). Induct on $m$, the number of 0s.

> [!example] Proof of (a) — model answer
> **Claim.** $S\rightsquigarrow^*\mathtt{0}^m\mathtt{1}^{2n}$ for all integers $m\ge n\ge 0$.
>
> Let $m$ and $n$ be arbitrary integers with $m\ge n\ge 0$, and assume that $S\rightsquigarrow^*\mathtt{0}^{m'}\mathtt{1}^{2n'}$ for all integers $m'\ge n'\ge 0$ with $m'<m$. There are three cases.
>
> **Case $m = 0$.** Then $n = 0$, because $0\le n\le m$. So $\mathtt{0}^m\mathtt{1}^{2n} = \varepsilon$, and $S\rightsquigarrow\varepsilon$ by the rule $S\to\varepsilon$.
>
> **Case $m\ge1$ and $n = 0$.** The pair $(m-1, 0)$ satisfies $m-1\ge0$ and $m-1<m$, so the induction hypothesis gives $S\rightsquigarrow^*\mathtt{0}^{m-1}$. Hence
> $$
> S\rightsquigarrow\mathtt{0}S\rightsquigarrow^*\mathtt{0}\bullet\mathtt{0}^{m-1} = \mathtt{0}^m\mathtt{1}^{2n},
> $$
> by the rule $S\to\mathtt{0}S$ and then the hypothesis, applied inside the context $\mathtt{0}\,\underline{\ \ }$.
>
> **Case $m\ge1$ and $n\ge1$.** The pair $(m-1, n-1)$ satisfies $m-1\ge n-1\ge0$ and $m-1<m$, so the hypothesis gives $S\rightsquigarrow^*\mathtt{0}^{m-1}\mathtt{1}^{2n-2}$. Hence
> $$
> S\rightsquigarrow\mathtt{0}S\mathtt{11}\rightsquigarrow^*\mathtt{0}\bullet\mathtt{0}^{m-1}\mathtt{1}^{2n-2}\bullet\mathtt{11} = \mathtt{0}^m\mathtt{1}^{2n},
> $$
> by the rule $S\to\mathtt{0}S\mathtt{11}$ and then the hypothesis inside the context $\mathtt{0}\,\underline{\ \ }\,\mathtt{11}$.
>
> The three cases cover every pair with $m\ge n\ge0$, and in each case $S\rightsquigarrow^*\mathtt{0}^m\mathtt{1}^{2n}$. $\blacksquare$

For $m = 3$, $n = 1$ the proof builds $S\rightsquigarrow\mathtt{0}S\mathtt{11}\rightsquigarrow\mathtt{00}S\mathtt{11}\rightsquigarrow\mathtt{000}S\mathtt{11}\rightsquigarrow\mathtt{00011}$: one $\mathtt{0}\ldots\mathtt{11}$ layer, then the two extra 0s, then $S\to\varepsilon$.

> [!trap] Where (a) loses points
> - **Missing the case $n = 0$.** The rule $S\to\mathtt{0}S\mathtt{11}$ cannot produce a string without 1s, so $\mathtt{0}^m$ needs its own case and its own rule. Inducting on $n$ alone has the same hole: its base case $n = 0$ is the whole family $\mathtt{0}^m$, which needs a second induction.
> - **Using the hypothesis without checking that it applies.** Say why $(m-1, n-1)$ is a legal pair: $m-1\ge n-1$ because $m\ge n$, $n-1\ge0$ because $n\ge1$, and $m-1<m$.
> - **Only describing the derivation.** "Use $S\to\mathtt{0}S\mathtt{11}$ $n$ times, then $S\to\mathtt{0}S$ $m-n$ times, then $S\to\varepsilon$" is the right idea; the induction is what turns it into a proof.

## (b) Everything generated is in L

**Idea.** Take an arbitrary derivation apart at its **first step** — one case per rule. The string derived from the inner $S$ is shorter than $w$, so the hypothesis applies to it.

> [!example] Proof of (b) — model answer
> **Claim.** Every string $w\in L(G)$ equals $\mathtt{0}^m\mathtt{1}^{2n}$ for some integers $m\ge n\ge0$.
>
> Let $w$ be an arbitrary string in $L(G)$, and fix a derivation $S\rightsquigarrow^* w$. Assume that every string $x\in L(G)$ with $\lvert x\rvert<\lvert w\rvert$ is in $L$. The derivation starts with one of the three rules for $S$.
>
> **Case $S\to\varepsilon$.** Then the derivation is $S\rightsquigarrow\varepsilon$, so $w = \varepsilon = \mathtt{0}^0\mathtt{1}^0$, with $m = n = 0$.
>
> **Case $S\to\mathtt{0}S\mathtt{11}$.** Then the derivation is $S\rightsquigarrow\mathtt{0}S\mathtt{11}\rightsquigarrow^* w$. The `0` and the `11` are terminals, so every later step rewrites the middle $S$ or a symbol derived from it; hence $w = \mathtt{0}x\mathtt{11}$ for some string $x$ with $S\rightsquigarrow^* x$. So $x\in L(G)$ and $\lvert x\rvert = \lvert w\rvert-3<\lvert w\rvert$, and the induction hypothesis gives $x = \mathtt{0}^m\mathtt{1}^{2n}$ for some $m\ge n\ge0$. Then $w = \mathtt{0}^{m+1}\mathtt{1}^{2(n+1)}$ with $m+1\ge n+1\ge0$, so $w\in L$.
>
> **Case $S\to\mathtt{0}S$.** In the same way $w = \mathtt{0}x$ with $S\rightsquigarrow^* x$ and $\lvert x\rvert = \lvert w\rvert-1<\lvert w\rvert$, so $x = \mathtt{0}^m\mathtt{1}^{2n}$ with $m\ge n\ge0$ by the hypothesis. Then $w = \mathtt{0}^{m+1}\mathtt{1}^{2n}$ with $m+1>m\ge n$, so $w\in L$.
>
> In all three cases, $w\in L$. $\blacksquare$

**Where the $\varepsilon$-rule needs care.** Two details make this induction work, and both concern $\varepsilon$.

- **The inner string may be empty.** `011` has the derivation $S\rightsquigarrow\mathtt{0}S\mathtt{11}\rightsquigarrow\mathtt{011}$, with $x = \varepsilon$. The hypothesis covers $x = \varepsilon$ because it is about *every* shorter string, $\varepsilon$ included; the base case is not a separate assumption but the case $S\to\varepsilon$ of the same argument.
- **The inner string is strictly shorter** — because every rule except $S\to\varepsilon$ puts at least one terminal next to $S$. This is exactly what fails for a rule whose right side has only nonterminals: with $S\to SS$, one of the two halves can derive $\varepsilon$, the other is then all of $w$, and the hypothesis says nothing about it. For such grammars, fix a **shortest** derivation (a half that derives $\varepsilon$ could then be cut out) or induct on the **length of the derivation** — see [[1-models-of-computation/05-context-free-languages#careful-with-those-epsilons|Careful with those epsilons]] and Lemma 5.3. (Here, adding $S\to SS$ would also break the claim itself: $S\rightsquigarrow SS\rightsquigarrow^*\mathtt{011}\bullet\mathtt{0} = \mathtt{0110}\notin L$.)

> [!trap] Where (b) loses points
> - **Reading the rule off the string.** "$w$ ends in `11`, so its derivation starts with $S\to\mathtt{0}S\mathtt{11}$" is false: `0011` also has the derivation $S\rightsquigarrow\mathtt{0}S\rightsquigarrow\mathtt{00}S\mathtt{11}\rightsquigarrow\mathtt{0011}$. Split into cases on the derivation you fixed, not on what $w$ looks like.
> - **Weak induction.** A hypothesis only for strings of length $\lvert w\rvert-1$ does not cover the case $S\to\mathtt{0}S\mathtt{11}$, where $x$ is three symbols shorter. Assume the claim for *every* shorter string.
> - **Not justifying $\lvert x\rvert<\lvert w\rvert$** — true here, but it is the reason the hypothesis applies, so say it; fatal in grammars with rules like $S\to SS$.
> - **Checking only half of the definition of $L$.** Membership of $w = \mathtt{0}^{m+1}\mathtt{1}^{2(n+1)}$ needs both the shape (0s, then an even number of 1s) and the inequality $m+1\ge n+1$.

## (c) Ambiguity

$G$ is **ambiguous**: `0011` has two parse trees. In one, the root uses $S\to\mathtt{0}S\mathtt{11}$ and the inner $S$ uses $S\to\mathtt{0}S$ and then $S\to\varepsilon$; in the other, the root uses $S\to\mathtt{0}S$ and the inner $S$ uses $S\to\mathtt{0}S\mathtt{11}$ and then $S\to\varepsilon$. In general $\mathtt{0}^m\mathtt{1}^{2n}$ has exactly $\binom{m}{n}$ parse trees: a parse tree is a chain of $m$ rules that each add one 0, followed by $S\to\varepsilon$, and any $n$ of those $m$ rules can be the ones that also add `11`.

It does not matter. $L(G)$ is a set of strings; (a) needs *some* derivation of each string of $L$, and (b) works for *any* derivation of each generated string. The grading rubrics do not penalize ambiguity either. If you want an [[concepts/parse-trees-and-ambiguity|unambiguous]] grammar anyway, produce the extra 0s first:
$$
S\to\mathtt{0}S\mid T\qquad T\to\mathtt{0}T\mathtt{11}\mid\varepsilon .
$$
Here $T$ generates $\{\mathtt{0}^n\mathtt{1}^{2n}\mid n\ge0\}$ and $S$ puts the $m-n$ extra 0s in front; every string of $L$ has exactly one parse tree.

> [!exam] How a proof like this is graded
> Midterm-1-style exams ask for a grammar without a proof (homework also asks for a description of each nonterminal). A correctness proof like this one consists of two inductions, each graded with the standard induction rubric, out of 10: **1** for starting from an arbitrary object (an arbitrary pair $m\ge n\ge0$; an arbitrary string with a fixed derivation), **2** for an explicitly stated strong induction hypothesis, **2** for cases that cover everything (three in each direction here), **1** for the base case, **2** for using the hypothesis correctly — only on legal, smaller objects, which is what the checks $m-1\ge n-1$ and $\lvert x\rvert<\lvert w\rvert$ are for — and **2** for the remaining details. "Clearly" draws scrutiny. See [[0-toolkit/06-how-exams-are-graded|how exams are graded]].

### Sources for this page
A classic textbook-style exercise, written in our own words; the problem statement, both proofs, the traps, the parse-tree count and the unambiguous grammar are ours, and the proof pattern follows Lemmas 5.1–5.3 of Erickson, *Models of Computation*, §5.3. Checked by `tools/checks/problems_2.py`: $L(G) = L$ on all strings of length at most 14, the derivation built in (a) for every $m\ge n$ with $m+2n\le16$, the facts used in each case of (b), the alternative derivation of `0011`, the $S\to SS$ counterexample, the count $\binom{m}{n}$ of parse trees, and the language and unambiguity of the second grammar.
