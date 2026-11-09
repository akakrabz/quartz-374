---
title: "Strong induction"
description: "Induction with the hypothesis for every smaller object — the same proof as a smallest counterexample, justified by the well-ordering principle: the boilerplate, why weak induction is a special case, structural induction on recursively defined objects, the classic mistakes, and a checked example."
tags: [concept, algorithms, induction, midterm-1]
aliases: ["strong induction", "proof by smallest counterexample", "smallest counterexample", "minimal counterexample", "well-ordering principle", "structural induction", "weak induction", "induction hypothesis"]
---

> [!key] The principle
> To prove $P(x)$ for every object $x$ — integers, strings, trees, expressions — under a notion of "smaller" with no infinite descending chains: let $x$ be **arbitrary**, **assume $P(y)$ for every $y$ smaller than $x$** (the **induction hypothesis**), and prove $P(x)$ by cases that together cover every $x$. Cases that use the hypothesis are **inductive cases**; the others are **base cases**. Equivalently, as a **proof by smallest counterexample**: if $P$ failed somewhere, it would fail at a smallest (minimal) $x$; show that no $x$ can be one.

**Why it works.** The **well-ordering principle** — every non-empty set of positive integers has a smallest element — turns any counterexample into a smallest one, and the proof shows that "nothing smaller fails" forces $P(x)$. The two write-ups are contrapositives: they differ only in how the argument is written down. **Weak induction** ("assume $P(n-1)$") is the special case of a proof that happens to need only $n-1$: the strong hypothesis contains it, so writing the strong one never costs anything. **Structural induction** is the same principle with "smaller" meaning "a proper part" — a shorter string, a subexpression, a subtree, a shorter derivation — and then the cases mirror the recursive definition of the objects.

> [!template] Template — strong induction
> Let $x$ be an arbitrary *[object]*. \
> Assume that *[the claim]* holds for every *[object]* $y$ smaller than $x$. \
> There are *[k]* cases to consider. \
> **Case** *[$x$ is small or special]*. … Therefore *[the claim holds for $x$]*. \
> **Case** *[everything else]*. *[$y_1, y_2, \dots$]* are smaller than $x$ because …, so the induction hypothesis implies that … Therefore *[the claim holds for $x$]*. \
> In every case, *[the claim holds for $x$]*. $\blacksquare$

> [!trap]
> - **A weak or unwritten hypothesis.** Write it out in full, for every smaller object: 2 of the rubric's 10 points.
> - **Base cases that don't reach.** The base cases are whatever the inductive case cannot handle: a step from $n$ to $n-5$ needs five consecutive base cases; a recurrence on $n-1$ and $n-2$ needs two.
> - **Building up.** "Assume it for $T$, add a leaf, get it for the bigger tree" covers only the objects that can be built that way. Start from an arbitrary object and take it apart.
> - **Circular or illegal uses.** A hypothesis "for every $j\le i$" assumes what is being proved. Apply the hypothesis only to objects that are smaller and in the set (not $F_{-1}$), and say why they are smaller.
> - **No smallest element.** Over all the integers, the claim "$n\ge 0$" satisfies "if every $k < n$ has it, so does $n$" for every $n$ — vacuously, since some $k < n$ is always negative — yet ${n = -1}$ fails it. "Smaller" must be well-founded.

**Example.** Let $f(1) = 0$ and $f(n) = f(\lfloor n/2\rfloor) + f(\lceil n/2\rceil) + 1$ for $n\ge 2$ — the number of merges MergeSort performs on $n$ items. *Claim:* $f(n) = n - 1$ for every $n\ge 1$. Let $n\ge 1$ be arbitrary, and assume $f(k) = k - 1$ for every integer $k$ with $1\le k < n$. If $n = 1$, then $f(1) = 0 = n - 1$. If $n\ge 2$, then $1\le\lfloor n/2\rfloor\le\lceil n/2\rceil < n$, so the hypothesis applies to both halves, and
$$
f(n) = \big(\lfloor n/2\rfloor - 1\big) + \big(\lceil n/2\rceil - 1\big) + 1 = n - 1,
$$
because $\lfloor n/2\rfloor + \lceil n/2\rceil = n$. In both cases $f(n) = n-1$. $\blacksquare$ (For $n\ge 4$ neither half is $n-1$: a weak hypothesis would not reach them.)

**Where it appears.** Erickson's Appendix I: [[4-lecture-notes/98-proof-by-induction#1-prime-divisors-proof-by-smallest-counterexample|§1]] (from smallest counterexample to induction), [[4-lecture-notes/98-proof-by-induction#2-the-axiom-of-induction|§2]] (well-ordering, the axiom of induction, the boilerplate), [[4-lecture-notes/98-proof-by-induction#7-binary-numbers-exist|§7]] (four proofs; weak induction), [[4-lecture-notes/98-proof-by-induction#11-trees|§11]] (structural induction on trees; building up). In the course: strings in [[1-models-of-computation/01-strings#13-induction-on-strings|Models §1.3]] and [[1-models-of-computation/01-strings#14-more-than-one-path-up-the-mountain|§1.4]], regular expressions in [[1-models-of-computation/02-regular-languages#26-proofs-about-regular-expressions|§2.6]], grammars in [[1-models-of-computation/05-context-free-languages#53-from-grammar-to-language|§5.3]], recursive algorithms in [[2-algorithms/01-recursion#12-simplify-and-delegate|Algorithms §1.2]]; templates for [[0-toolkit/02-proof-templates#1-induction-on-strings|string induction]], [[0-toolkit/02-proof-templates#3-induction-on-regular-expressions|structural induction on regular expressions]] (five cases) and [[0-toolkit/02-proof-templates#17-proving-a-recursive-algorithm-correct|recursive correctness]]; the [[0-toolkit/06-how-exams-are-graded#4-induction|induction rubric]].

Related: [[concepts/induction-on-strings]] · [[concepts/recursion]] · [[concepts/regular-expressions]] · [[concepts/context-free-grammars]] · [[concepts/divide-and-conquer]]
