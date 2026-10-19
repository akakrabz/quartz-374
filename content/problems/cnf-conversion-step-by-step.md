---
title: "Worked problem — CNF conversion, step by step"
description: "A grammar for balanced strings with an ε-rule, a unit rule and a long rule, converted to Chomsky normal form with steps 0–6 of the textbook algorithm: every intermediate grammar, the step that creates a new unit rule, the right order for removing unit rules, and a check of the result."
tags: [problem, context-free, midterm-1]
---

*Problem · a conversion exercise on Chomsky normal form · uses [[1-models-of-computation/05-context-free-languages#58-chomsky-normal-form|§5.8]], [[1-models-of-computation/05-context-free-languages#59-the-cnf-conversion-algorithm|§5.9]] · concepts: [[concepts/chomsky-normal-form]], [[concepts/context-free-grammars]]*

> [!question] Problem
> The grammar
> $$
> S\to SS\mid P\mid\varepsilon\qquad\qquad P\to\mathtt{0}S\mathtt{1}
> $$
> generates the **balanced strings**: read `0` as "(" and `1` as ")"; a string $w$ is balanced if $\#(\mathtt{0},w) = \#(\mathtt{1},w)$ and every prefix of $w$ has at least as many 0s as 1s. $S$ generates all balanced strings, and $P$ those of the form $\mathtt{0}x\mathtt{1}$ with $x$ balanced. The grammar has an $\varepsilon$-rule ($S\to\varepsilon$), a unit rule ($S\to P$) and a long rule ($P\to\mathtt{0}S\mathtt{1}$).
>
> (a) Convert the grammar to Chomsky normal form with the algorithm of §5.9, showing the grammar after every step.
>
> (b) Check the result.

**The target.** A grammar is in [[concepts/chomsky-normal-form|Chomsky normal form]] if its start symbol appears on no right side, the only allowed $\varepsilon$-rule is (start symbol) $\to\varepsilon$, and every other rule is $A\to BC$ (two nonterminals) or $A\to a$ (one terminal). Each step of the algorithm removes one kind of violation without changing the language; the order of the steps matters.

## (a) The conversion

**Step 0 — new start symbol.** $S$ appears on right sides ($S\to SS$, $P\to\mathtt{0}S\mathtt{1}$) and the language contains $\varepsilon$, so $S$ cannot be the start symbol of a CNF grammar. Add $S'\to S$:
$$
S'\to S\qquad S\to SS\mid P\mid\varepsilon\qquad P\to\mathtt{0}S\mathtt{1}
$$

**Step 1 — split long rules.** Only $P\to\mathtt{0}S\mathtt{1}$ has a right side longer than 2. Keep its first symbol and hand the rest to a new nonterminal $B$:
$$
S'\to S\qquad S\to SS\mid P\mid\varepsilon\qquad P\to\mathtt{0}B\qquad B\to S\mathtt{1}
$$
$B$ generates the strings $x\mathtt{1}$ with $x$ balanced. (A rule of length $k$ becomes $k-1$ rules of length 2.)

**Step 2 — find the nullable nonterminals.** $S$ is nullable ($S\to\varepsilon$), and therefore so is $S'$ ($S'\to S$). $P$ and $B$ are not: each of their rules contains a terminal. Nullable: $\{S, S'\}$. Because $S'$ is nullable, the final grammar will keep $S'\to\varepsilon$.

**Step 3 — remove $\varepsilon$-rules.** For each rule, add every variant with some nullable occurrences deleted (never an empty right side); then delete $S\to\varepsilon$ and add $S'\to\varepsilon$.
- $S\to SS$: deleting one $S$ gives $S\to S$; deleting both would give $\varepsilon$, which is not added.
- $B\to S\mathtt{1}$: deleting $S$ gives $B\to\mathtt{1}$.
- $S'\to S$: deleting $S$ would leave $\varepsilon$; instead $S'\to\varepsilon$ is added, since $S'$ is nullable.
$$
S'\to S\mid\varepsilon\qquad S\to SS\mid S\mid P\qquad P\to\mathtt{0}B\qquad B\to S\mathtt{1}\mid\mathtt{1}
$$
From now on $S$ generates the **non-empty** balanced strings; only $S'$ still generates $\varepsilon$.

> [!trap] Step 3
> - **$B\to\mathtt{1}$ is easy to miss, and fatal.** Without it every $P$ needs a $B$, every $B$ needs a non-empty $S$, and every non-empty $S$ needs a $P$: the grammar generates nothing but $\varepsilon$.
> - **Do not put $S\to\varepsilon$ back** "because $S$ is nullable". Only the start symbol may keep an $\varepsilon$-rule; the variants now do the work of the deleted rule.
> - **Removing $\varepsilon$-rules creates unit rules** — here $S\to S$, from $S\to SS$. That is why unit rules are removed *after* $\varepsilon$-rules.

**Step 4 — merge equivalent nonterminals.** The unit rules are $S'\to S$, $S\to S$ and $S\to P$. The only cycle among them is the self-loop $S\to S$, which says nothing: delete it. No two different nonterminals derive each other by unit rules, so nothing is merged.
$$
S'\to S\mid\varepsilon\qquad S\to SS\mid P\qquad P\to\mathtt{0}B\qquad B\to S\mathtt{1}\mid\mathtt{1}
$$

**Step 5 — remove unit rules.** The unit rules form the chain $S'\to S\to P$. Work from its end backward (reverse topological order): $P$ has no unit rule; replace $S\to P$ by $P$'s rule, giving $S\to SS\mid\mathtt{0}B$; then replace $S'\to S$ by $S$'s rules *as they are now*:
$$
S'\to SS\mid\mathtt{0}B\mid\varepsilon\qquad S\to SS\mid\mathtt{0}B\qquad P\to\mathtt{0}B\qquad B\to S\mathtt{1}\mid\mathtt{1}
$$
$P$ is no longer reachable from $S'$, so delete it. (CNF does not forbid useless nonterminals, but there is no reason to keep one.)

> [!trap] Step 5
> The order matters. Processing $S'$ before $S$ copies $S$'s rules while $S\to P$ is still among them: $S'\to SS\mid P\mid\varepsilon$, and the unit rule $S'\to P$ survives into the "final" grammar — same language, but not in CNF.

**Step 6 — protect terminals.** In each right side of length 2, replace a terminal $a$ by a new nonterminal $T_a$ with the rule $T_a\to a$. Rules $A\to a$ stay as they are ($B\to\mathtt{1}$).

> [!key] Answer (a) — the grammar in Chomsky normal form, start symbol $S'$
> $$
> \begin{aligned}
> S'&\to SS\mid T_{\mathtt{0}}B\mid\varepsilon & S&\to SS\mid T_{\mathtt{0}}B & B&\to ST_{\mathtt{1}}\mid\mathtt{1}\\
> T_{\mathtt{0}}&\to\mathtt{0} & T_{\mathtt{1}}&\to\mathtt{1}
> \end{aligned}
> $$
> $S'$ generates the balanced strings, $S$ the non-empty balanced strings, and $B$ the strings $x\mathtt{1}$ with $x$ balanced.

| step | what changed | grammar afterwards |
|---|---|---|
| 0 | new start symbol | $S'\to S$; $\ S\to SS\mid P\mid\varepsilon$; $\ P\to\mathtt{0}S\mathtt{1}$ |
| 1 | $P\to\mathtt{0}S\mathtt{1}$ split | $S'\to S$; $\ S\to SS\mid P\mid\varepsilon$; $\ P\to\mathtt{0}B$; $\ B\to S\mathtt{1}$ |
| 2 | nullable: $S$, $S'$ | unchanged |
| 3 | $\varepsilon$-rules removed | $S'\to S\mid\varepsilon$; $\ S\to SS\mid S\mid P$; $\ P\to\mathtt{0}B$; $\ B\to S\mathtt{1}\mid\mathtt{1}$ |
| 4 | self-loop $S\to S$ deleted | $S'\to S\mid\varepsilon$; $\ S\to SS\mid P$; $\ P\to\mathtt{0}B$; $\ B\to S\mathtt{1}\mid\mathtt{1}$ |
| 5 | unit rules removed, $P$ deleted | $S'\to SS\mid\mathtt{0}B\mid\varepsilon$; $\ S\to SS\mid\mathtt{0}B$; $\ B\to S\mathtt{1}\mid\mathtt{1}$ |
| 6 | terminals protected | the answer above |

## (b) Checking the result

**Syntax.** $S'$ appears on no right side; $S'\to\varepsilon$ is the only $\varepsilon$-rule; every other rule is two nonterminals or one terminal. ✓

**Language.** $S'\to\varepsilon$ gives $\varepsilon$; $S'\to T_{\mathtt{0}}B$ gives $\mathtt{0}x\mathtt{1}$ with $x$ balanced; $S'\to SS$ gives the concatenations of two non-empty balanced strings. These are all the balanced strings: cut a non-empty balanced string after its *shortest* non-empty balanced prefix; if that prefix is the whole string, the string is $\mathtt{0}x\mathtt{1}$ with $x$ balanced, and otherwise it is a concatenation of two non-empty balanced strings. The same argument shows that $S$ generates the non-empty ones. ✓

**Short strings.** Test a few strings in each intermediate grammar as you go: $\varepsilon$, `01`, `0011`, `0101` must be generated, `0`, `10`, `0110` must not. A step that changes the language usually fails one of them at once — forgetting $B\to\mathtt{1}$ fails `01`.

**A derivation.** In CNF, every derivation of a string of length $n\ge1$ has exactly $2n-1$ steps. For `0011`:
$$
S'\rightsquigarrow T_{\mathtt{0}}B\rightsquigarrow\mathtt{0}B\rightsquigarrow\mathtt{0}ST_{\mathtt{1}}\rightsquigarrow\mathtt{0}T_{\mathtt{0}}BT_{\mathtt{1}}\rightsquigarrow\mathtt{00}BT_{\mathtt{1}}\rightsquigarrow\mathtt{001}T_{\mathtt{1}}\rightsquigarrow\mathtt{0011},
$$
seven steps, $2\cdot4-1$. ✓

> [!exam] How a conversion is checked
> No standard rubric targets CNF conversions. A conversion goes wrong in one of two visible ways: the result is **not in CNF** (a leftover unit rule, an $\varepsilon$-rule for a nonterminal other than the start symbol, a terminal in a rule of length 2), or it generates a **different language** — and a forgotten variant in step 3 usually changes infinitely many strings, as $B\to\mathtt{1}$ does here. On the grammar rubric's scale (2 for syntax, 8 for correctness), infinitely many wrong strings cost all the correctness points. Writing down every intermediate grammar is what lets you test each step on short strings.

### Sources for this page
The grammar is a variant, with an explicit unit rule, of the balanced-parentheses grammar of Erickson, *Models of Computation*, §5.4, and the algorithm is the book's §5.9, in our own words; the problem, the intermediate grammars, the traps and their consequences are ours. Checked by `tools/checks/problems_2.py`: every intermediate grammar generates exactly the balanced strings of length at most 12, the nullable set, the CNF test for the final grammar, the languages of $S$ and $B$, the decomposition of balanced strings, the derivation of `0011`, and both trap scenarios (no $B\to\mathtt{1}$; the wrong order in step 5).
