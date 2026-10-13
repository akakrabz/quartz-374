---
title: "Worked problem — Induction on a recursive string function"
description: "A new recursive function sort moves every 1 of a binary string to the end. Part (a) proves that it keeps the length, with three cases that mirror the definition; part (b) proves that sorting twice changes nothing — a proof that gets stuck until a small lemma about sort(y•1) is proved first."
tags: [problem, strings, midterm-1]
---

*Problem · style of the Midterm 1 induction problem (a newly defined recursive string function) · uses [[1-models-of-computation/01-strings#13-induction-on-strings|§1.3]], [[1-models-of-computation/01-strings#more-recursive-functions|more recursive functions]] · concepts: [[concepts/induction-on-strings]], [[concepts/strings]]*

> [!question] Problem
> For every binary string $w$, define
> $$
> \textsf{sort}(w) := \begin{cases} \varepsilon & \text{if } w = \varepsilon\\ \mathtt{0}\cdot\textsf{sort}(x) & \text{if } w = \mathtt{0}x\\ \textsf{sort}(x)\bullet\mathtt{1} & \text{if } w = \mathtt{1}x\end{cases}
> $$
> for every string $x$. For example, $\textsf{sort}(\mathtt{0110}) = \textsf{sort}(\mathtt{1010}) = \mathtt{0011}$. You may use Lemmas 1.1–1.3 without proof.
>
> (a) Prove that $\lvert\textsf{sort}(w)\rvert = \lvert w\rvert$ for every binary string $w$.
>
> (b) Prove that $\textsf{sort}(\textsf{sort}(w)) = \textsf{sort}(w)$ for every binary string $w$.

**Unfold the definition before proving anything.** On a short string:
$$
\textsf{sort}(\mathtt{101}) = \textsf{sort}(\mathtt{01})\bullet\mathtt{1} = \big(\mathtt{0}\cdot\textsf{sort}(\mathtt{1})\big)\bullet\mathtt{1} = \Big(\mathtt{0}\cdot\big(\textsf{sort}(\varepsilon)\bullet\mathtt{1}\big)\Big)\bullet\mathtt{1} = (\mathtt{0}\cdot\mathtt{1})\bullet\mathtt{1} = \mathtt{011}.
$$
A 0 at the front stays in front (second case); a 1 at the front is taken off and re-attached at the very end, after the rest has been sorted (third case). So $\textsf{sort}(w)$ is $w$ with every 0 moved before every 1, $\textsf{sort}(w) = \mathtt{0}^{\#(\mathtt{0},w)}\mathtt{1}^{\#(\mathtt{1},w)}$, and both claims are believable. The job is to prove them from the definition. Notice the two different dots: the second case puts one *symbol* in front ($\cdot$, a pair), the third glues two *strings* ($\bullet$, concatenation) — that difference is what each proof has to handle.

## (a) Sorting keeps the length

**Idea.** The definition has three cases, so the proof has three cases. The cases $w = \varepsilon$ and $w = \mathtt{0}x$ unfold with the definitions alone. The case $w = \mathtt{1}x$ ends in a concatenation, and the definition of length peels the *first* symbol of a string, not the last — so it needs Lemma 1.2, $\lvert y\bullet z\rvert = \lvert y\rvert + \lvert z\rvert$.

> [!example] Proof of (a) — model answer
> Let $w$ be an arbitrary binary string. Assume that $\lvert\textsf{sort}(x)\rvert = \lvert x\rvert$ for every binary string $x$ with $\lvert x\rvert < \lvert w\rvert$. There are three cases.
>
> **Case $w = \varepsilon$.** $\textsf{sort}(\varepsilon) = \varepsilon$ by definition, so $\lvert\textsf{sort}(w)\rvert = \lvert\varepsilon\rvert = \lvert w\rvert$.
>
> **Case $w = \mathtt{0}x$** for some string $x$. Then $\lvert x\rvert = \lvert w\rvert - 1 < \lvert w\rvert$, so the induction hypothesis applies to $x$, and
> $$
> \begin{aligned}
> \lvert\textsf{sort}(\mathtt{0}x)\rvert &= \lvert\mathtt{0}\cdot\textsf{sort}(x)\rvert && \text{by definition of } \textsf{sort}\\
> &= 1 + \lvert\textsf{sort}(x)\rvert && \text{by definition of } \lvert\cdot\rvert\\
> &= 1 + \lvert x\rvert && \text{by the induction hypothesis}\\
> &= \lvert\mathtt{0}x\rvert && \text{by definition of } \lvert\cdot\rvert.
> \end{aligned}
> $$
> **Case $w = \mathtt{1}x$** for some string $x$. Again $\lvert x\rvert < \lvert w\rvert$, and
> $$
> \begin{aligned}
> \lvert\textsf{sort}(\mathtt{1}x)\rvert &= \lvert\textsf{sort}(x)\bullet\mathtt{1}\rvert && \text{by definition of } \textsf{sort}\\
> &= \lvert\textsf{sort}(x)\rvert + \lvert\mathtt{1}\rvert && \text{by Lemma 1.2}\\
> &= \lvert x\rvert + 1 && \text{by the induction hypothesis, and } \lvert\mathtt{1}\rvert = 1 + \lvert\varepsilon\rvert = 1\\
> &= \lvert\mathtt{1}x\rvert && \text{by definition of } \lvert\cdot\rvert.
> \end{aligned}
> $$
> The three cases cover every binary string, and in each case $\lvert\textsf{sort}(w)\rvert = \lvert w\rvert$. $\blacksquare$

> [!trap] Where (a) loses points
> - **Two cases where the definition has three.** Writing "case $w = ax$" is fine only if you then split on $a = \mathtt{0}$ and $a = \mathtt{1}$: $\textsf{sort}$ does different things in the two cases, and an argument that treats them together proves nothing about either.
> - **Treating $\bullet$ like $\cdot$.** "$\lvert\textsf{sort}(x)\bullet\mathtt{1}\rvert = 1 + \lvert\textsf{sort}(x)\rvert$ by definition of length" cites the wrong reason: the definition peels the first symbol, and this $\mathtt{1}$ is the last. Cite Lemma 1.2.
> - **A vague hypothesis.** "Assume it works for smaller strings" does not say *what* works. Write the claim out for every string shorter than $w$; that sentence is worth two rubric points by itself.

## (b) Sorting twice changes nothing

**Idea — and where the obvious attempt gets stuck.** Try the same three cases. The first two go through (they are written out in the proof below). The third does not:
$$
\textsf{sort}(\textsf{sort}(\mathtt{1}x)) = \textsf{sort}\big(\textsf{sort}(x)\bullet\mathtt{1}\big) = \ ?
$$
The definition of $\textsf{sort}$ looks at the *first* symbol of its argument, and the first symbol of $\textsf{sort}(x)\bullet\mathtt{1}$ is not the $\mathtt{1}$ just attached (unless $x = \varepsilon$). The induction hypothesis does not help either: it is about $\textsf{sort}(\textsf{sort}(y))$, not about $\textsf{sort}(y\bullet\mathtt{1})$, and the string $\textsf{sort}(x)\bullet\mathtt{1}$ has length $\lvert x\rvert + 1 = \lvert w\rvert$ (by part (a) and Lemma 1.2), so it is not even shorter than $w$. What is missing is a fact about sorting a string that *ends* in $\mathtt{1}$ — a final $\mathtt{1}$ is already where $\textsf{sort}$ would put it. State that fact as a lemma, prove it first, and the stuck case becomes one line.

> [!key] Lemma
> $\textsf{sort}(y\bullet\mathtt{1}) = \textsf{sort}(y)\bullet\mathtt{1}$ for every binary string $y$.

> [!example] Proof of the lemma
> Let $y$ be an arbitrary binary string. Assume that $\textsf{sort}(z\bullet\mathtt{1}) = \textsf{sort}(z)\bullet\mathtt{1}$ for every binary string $z$ with $\lvert z\rvert < \lvert y\rvert$. There are three cases.
>
> **Case $y = \varepsilon$.** By the definition of $\bullet$, $\varepsilon\bullet\mathtt{1} = \mathtt{1} = \mathtt{1}\cdot\varepsilon$, so the third case of the definition of $\textsf{sort}$ (with $x = \varepsilon$) gives $\textsf{sort}(\varepsilon\bullet\mathtt{1}) = \textsf{sort}(\varepsilon)\bullet\mathtt{1}$.
>
> **Case $y = \mathtt{0}z$** for some string $z$. Then $\lvert z\rvert < \lvert y\rvert$, and
> $$
> \begin{aligned}
> \textsf{sort}(\mathtt{0}z\bullet\mathtt{1}) &= \textsf{sort}\big(\mathtt{0}\cdot(z\bullet\mathtt{1})\big) && \text{by definition of } {\bullet}\\
> &= \mathtt{0}\cdot\textsf{sort}(z\bullet\mathtt{1}) && \text{by definition of } \textsf{sort}\\
> &= \mathtt{0}\cdot\big(\textsf{sort}(z)\bullet\mathtt{1}\big) && \text{by the induction hypothesis}\\
> &= \big(\mathtt{0}\cdot\textsf{sort}(z)\big)\bullet\mathtt{1} && \text{by definition of } {\bullet}\\
> &= \textsf{sort}(\mathtt{0}z)\bullet\mathtt{1} && \text{by definition of } \textsf{sort}.
> \end{aligned}
> $$
> **Case $y = \mathtt{1}z$** for some string $z$. Then $\lvert z\rvert < \lvert y\rvert$, and
> $$
> \begin{aligned}
> \textsf{sort}(\mathtt{1}z\bullet\mathtt{1}) &= \textsf{sort}\big(\mathtt{1}\cdot(z\bullet\mathtt{1})\big) && \text{by definition of } {\bullet}\\
> &= \textsf{sort}(z\bullet\mathtt{1})\bullet\mathtt{1} && \text{by definition of } \textsf{sort}\\
> &= \big(\textsf{sort}(z)\bullet\mathtt{1}\big)\bullet\mathtt{1} && \text{by the induction hypothesis}\\
> &= \textsf{sort}(\mathtt{1}z)\bullet\mathtt{1} && \text{by definition of } \textsf{sort}.
> \end{aligned}
> $$
> In all three cases, $\textsf{sort}(y\bullet\mathtt{1}) = \textsf{sort}(y)\bullet\mathtt{1}$. $\blacksquare$

> [!example] Proof of (b) — model answer
> Let $w$ be an arbitrary binary string. Assume that $\textsf{sort}(\textsf{sort}(x)) = \textsf{sort}(x)$ for every binary string $x$ with $\lvert x\rvert < \lvert w\rvert$. There are three cases.
>
> **Case $w = \varepsilon$.** $\textsf{sort}(\textsf{sort}(\varepsilon)) = \textsf{sort}(\varepsilon)$, because $\textsf{sort}(\varepsilon) = \varepsilon$.
>
> **Case $w = \mathtt{0}x$** for some string $x$. Then $\lvert x\rvert < \lvert w\rvert$, and
> $$
> \begin{aligned}
> \textsf{sort}(\textsf{sort}(\mathtt{0}x)) &= \textsf{sort}\big(\mathtt{0}\cdot\textsf{sort}(x)\big) && \text{by definition of } \textsf{sort}\\
> &= \mathtt{0}\cdot\textsf{sort}(\textsf{sort}(x)) && \text{by definition of } \textsf{sort}\\
> &= \mathtt{0}\cdot\textsf{sort}(x) && \text{by the induction hypothesis}\\
> &= \textsf{sort}(\mathtt{0}x) && \text{by definition of } \textsf{sort}.
> \end{aligned}
> $$
> **Case $w = \mathtt{1}x$** for some string $x$. Then $\lvert x\rvert < \lvert w\rvert$, and
> $$
> \begin{aligned}
> \textsf{sort}(\textsf{sort}(\mathtt{1}x)) &= \textsf{sort}\big(\textsf{sort}(x)\bullet\mathtt{1}\big) && \text{by definition of } \textsf{sort}\\
> &= \textsf{sort}(\textsf{sort}(x))\bullet\mathtt{1} && \text{by the lemma, with } y = \textsf{sort}(x)\\
> &= \textsf{sort}(x)\bullet\mathtt{1} && \text{by the induction hypothesis}\\
> &= \textsf{sort}(\mathtt{1}x) && \text{by definition of } \textsf{sort}.
> \end{aligned}
> $$
> In all three cases, $\textsf{sort}(\textsf{sort}(w)) = \textsf{sort}(w)$. $\blacksquare$

Look at how the two tools split the work. The induction hypothesis is applied only to $x$, which is shorter than $w$. The lemma is applied with $y = \textsf{sort}(x)$, to the string $\textsf{sort}(x)\bullet\mathtt{1}$, which is exactly as long as $w$ — but the lemma holds for every string $y$, so no length condition is needed.

> [!trap] Where (b) loses points
> - **Applying the hypothesis to $\textsf{sort}(x)\bullet\mathtt{1}$.** That string is as long as $w$, so the hypothesis does not cover it — and even for a shorter string the hypothesis would only give $\textsf{sort}(\textsf{sort}(y)) = \textsf{sort}(y)$, which is not the step needed. This is the rubric's "correct use of the hypothesis" item.
> - **Asserting the lemma.** "A 1 at the end is already in place" is the right intuition and not a proof. The lemma is not a result from lecture, so it needs its own induction; on an exam, prove it right before you use it.
> - **Proving a false lemma.** Test a lemma on a two-symbol example first. The look-alike $\textsf{sort}(y\bullet\mathtt{0}) = \textsf{sort}(y)\bullet\mathtt{0}$ fails at $y = \mathtt{1}$: $\textsf{sort}(\mathtt{10}) = \mathtt{01}$, but $\textsf{sort}(\mathtt{1})\bullet\mathtt{0} = \mathtt{10}$. The same example refutes $\textsf{sort}(x\bullet y) = \textsf{sort}(x)\bullet\textsf{sort}(y)$.

**Another route, and why it is not shorter.** You could first prove the closed form $\textsf{sort}(w) = \mathtt{0}^{\#(\mathtt{0},w)}\mathtt{1}^{\#(\mathtt{1},w)}$ and then $\textsf{sort}(\mathtt{0}^m\mathtt{1}^n) = \mathtt{0}^m\mathtt{1}^n$. That is two inductions as well, plus facts about powers such as $\mathtt{1}^n\bullet\mathtt{1} = \mathtt{1}^{n+1}$. When a direct induction gets stuck, ask: *what fact about the stuck expression would let me continue?* The answer is usually a lemma as small as the one above — and it is usually proved by the same kind of induction.

> [!exam] How this problem is graded
> Midterm-1-style exams devote a whole problem to a newly defined string function like $\textsf{sort}$. A proof is graded with the induction rubric, out of 10: **1** for starting from an arbitrary string; **2** for an explicitly stated strong hypothesis (weak induction is discouraged); **2** for cases that cover every string — three here, mirroring the definition; **1** for the base case; **2** for applying the hypothesis correctly — to $x$, never to $\textsf{sort}(x)\bullet\mathtt{1}$; **2** for the remaining details, with every line justified by a definition, a lemma or the hypothesis. A lemma you need is part of your proof and is graded with it; results from lecture, the course notes, labs or homework solutions (Lemmas 1.1–1.3, for instance) may be cited without proof. "Clearly" draws scrutiny. See [[0-toolkit/06-how-exams-are-graded|how exams are graded]].

### Sources for this page
An original problem in the style of the Midterm 1 induction problem; the function $\textsf{sort}$, both proofs, the lemma and the traps are ours (the course's practice exams use other functions). The proof template and Lemma 1.2 are from Erickson, *Models of Computation*, §1.3. Checked by `tools/checks/problems_1.py`: the examples and the unfolding, part (a), the lemma, part (b) and the closed form on every binary string of length at most 14, the length of $\textsf{sort}(x)\bullet\mathtt{1}$, and the counterexamples in the traps.
