---
title: "Master theorem"
description: "The three cases of T(n) = a T(n/b) + f(n) as a formula: Erickson's ratio form and the textbook n^(log_b a) form with the log^k extension and the regularity condition, why both are the recursion-tree level sums, a table of solved recurrences, the recurrences it cannot solve, and Akra–Bazzi for unequal splits."
tags: [concept, algorithms, recursion, midterm-2]
aliases: ["master method", "Akra–Bazzi", "Akra–Bazzi theorem", "divide-and-conquer recurrence"]
---

> [!key] The Master Theorem (ratio form, Erickson's appendix)
> Let $T(n) = a\,T(n/b) + f(n)$ with constants $a \ge 1$ and $b > 1$. Compare $a\,f(n/b)$, the work one level down, with $f(n)$:
> - if $a\,f(n/b) = \kappa\, f(n)$ for a constant $\kappa < 1$, then $T(n) = \Theta(f(n))$ — the **root** dominates;
> - if $a\,f(n/b) = f(n)$, then $T(n) = \Theta(f(n)\log n)$ — all levels are **equal**;
> - if $a\,f(n/b) = K f(n)$ for a constant $K > 1$, then $T(n) = \Theta(n^{\log_b a})$ — the **leaves** dominate;
> - otherwise the theorem says nothing.
>
> In the first and last cases an inequality is enough: $a\,f(n/b) \le \kappa f(n)$, respectively $\ge K f(n)$, for all large $n$.

This is the form Erickson's appendix [*Solving Recurrences*](https://jeffe.cs.illinois.edu/teaching/algorithms/notes/99-recurrences.pdf) calls the Master Theorem. The book's chapters never state it — the index entry reads "Master Theorem, *see* recursion trees" — and use the same three cases as recursion-tree level sums in [[2-algorithms/01-recursion#17-recursion-trees|§1.7]], where the recurrence is written $r\,T(n/c) + f(n)$ and $f(n) = n^d$.

> [!key] The textbook form
> Most textbooks (CLRS, for one) compare $f$ with $n^{\log_b a}$, the number of leaves:
> 1. $f(n) = O(n^{\log_b a - \varepsilon})$ for a constant $\varepsilon > 0$ (polynomially smaller): $T(n) = \Theta(n^{\log_b a})$.
> 2. $f(n) = \Theta(n^{\log_b a}\log^k n)$ for a constant $k \ge 0$: $T(n) = \Theta(n^{\log_b a}\log^{k+1} n)$. Many statements give only $k = 0$.
> 3. $f(n) = \Omega(n^{\log_b a + \varepsilon})$ for a constant $\varepsilon > 0$ (polynomially larger) **and** the **regularity condition** holds: $a\,f(n/b) \le \kappa f(n)$ for a constant $\kappa < 1$ and all large $n$. Then $T(n) = \Theta(f(n))$.
>
> For $f(n) = \Theta(n^c)$ it is a comparison of exponents: $c < \log_b a$ gives $\Theta(n^{\log_b a})$, $c = \log_b a$ gives $\Theta(n^c\log n)$, $c > \log_b a$ gives $\Theta(n^c)$. Since $a(n/b)^c = (a/b^c)\,n^c$, this is the ratio form with $\kappa$ or $K$ equal to $a/b^c$.

Beyond the usual statement, case 2 with $k = -1$ gives $\Theta(n^{\log_b a}\log\log n)$ and with $k < -1$ gives $\Theta(n^{\log_b a})$.

**Regularity.** Case 3 needs more than "$f$ is bigger": the level sums must shrink geometrically, and $a\,f(n/b) \le \kappa f(n)$ says exactly that each level costs at most $\kappa$ times the one above. For $f = n^c\log^k n$ with $c > \log_b a$ it always holds. The ratio form needs no separate condition because its first case *is* the regularity condition, and that hypothesis already makes $f$ polynomially larger: $f(n) = (a/\kappa)\,f(n/b)$ gives $f(n) = f(1)\,n^{\log_b a + \log_b(1/\kappa)}$ at powers of $b$.

**Why it works.** Level $i$ of the [[concepts/recursion-trees|recursion tree]] has $a^i$ nodes of size $n/b^i$, so
$$
T(n) = \sum_{i=0}^{\log_b n} a^i f(n/b^i),
$$
and consecutive terms differ by the factor $a\,f(n/b^{i+1})/f(n/b^i)$ — the ratio in the theorem. When it is a constant, the level sums form a geometric series, which is within a constant factor of its largest term: the root's $f(n)$ when $\kappa < 1$; the bottom level, $a^{\log_b n} = n^{\log_b a}$ leaves of constant cost, when $K > 1$; and when the ratio is 1, all $\log_b n + 1$ levels count. The method and pictures are in [[2-algorithms/01-recursion#17-recursion-trees|§1.7]].

> [!recipe] Using it on an exam
> 1. **Check the shape:** exactly $T(n) = a\,T(n/b) + f(n)$ — a single subproblem size, constants $a \ge 1$ and $b > 1$, where $b$ is the factor by which the *size* shrinks. Floors, ceilings and $\pm$ constants in the argument do not matter.
> 2. **Compute $\log_b a$**: the leaves number $n^{\log_b a}$. For $f = n^c$ also compute the level ratio $a/b^c$.
> 3. **Compare** $f$ with $n^{\log_b a}$: polynomially smaller → leaves; equal up to a $\log^k n$ factor → equal, one more log; polynomially larger → root.
> 4. **Write** the recurrence, the solution, and the case in words: "$T(n) = 3T(n/2) + O(n)$; the level sums grow by the factor $3/2$, so the leaves dominate and $T(n) = O(n^{\lg 3})$."

**Worked examples.** The "from" column links to where each recurrence comes from.

| recurrence | from | $n^{\log_b a}$ | $a\,f(n/b)/f(n)$ | case: solution |
|---|---|---|---|---|
| $2T(n/2) + n$ | MergeSort ([[2-algorithms/01-recursion#14-mergesort\|§1.4]]) | $n$ | $1$ | equal: $\Theta(n\log n)$ |
| $T(n/2) + O(1)$ | BinarySearch ([[concepts/recursion\|recursion]]), PiṅgalaPower ([[2-algorithms/01-recursion#110-exponentiation\|§1.10]]) | $1$ | $1$ | equal: $\Theta(\log n)$ |
| $T(n/2) + n$ | QuickSelect, median pivots ([[2-algorithms/01-recursion#quickselect\|§1.8]]) | $1$ | $1/2$ | root: $\Theta(n)$ |
| $2T(n/2) + n^{\lg 3}$ | Cruel ([[2-algorithms/01-recursion-exercises#exercise-112--cruel-and-unusual\|Ex. 1.12]]) | $n$ | $2/3$ | root: $\Theta(n^{\lg 3})$ |
| $2T(n/2) + 2$ | MinMax ([[concepts/divide-and-conquer\|D&C]]) | $n$ | $2$ | leaves: $\Theta(n)$ |
| $4T(n/2) + n$ | SplitMultiply ([[2-algorithms/01-recursion#19-fast-multiplication\|§1.9]]) | $n^2$ | $2$ | leaves: $\Theta(n^2)$ |
| $3T(n/2) + n$ | Karatsuba ([[2-algorithms/01-recursion#19-fast-multiplication\|§1.9]]) | $n^{\lg 3}\approx n^{1.585}$ | $3/2$ | leaves: $\Theta(n^{\lg 3})$ |
| $7T(n/2) + n^2$ | Strassen ([[concepts/recursion-trees\|trees]]) | $n^{\lg 7}\approx n^{2.807}$ | $7/4$ | leaves: $\Theta(n^{\lg 7})$ |
| $3T(2n/3) + 1$ | StoogeSort ([[2-algorithms/01-recursion-exercises#exercise-111--stoogesort\|Ex. 1.11]]) | $n^{\log_{3/2} 3}\approx n^{2.71}$ | $3$ | leaves: $\Theta(n^{\log_{3/2} 3})$ |
| $2T(n/4) + \sqrt n$ | $A(n)$ of [[2-algorithms/01-recursion-exercises#exercise-16--nine-recurrences\|Ex. 1.6]] | $\sqrt n$ | $1$ | equal: $\Theta(\sqrt n\log n)$ |
| $2T(n/2) + n\lg n$ | [[2-algorithms/01-recursion-exercises#exercise-18--logarithms-and-square-roots\|Ex. 1.8]](m) | $n$ | $\to 1$, not $= 1$ | equal, $k = 1$: $\Theta(n\log^2 n)$ |
| $4T(n/2) + n\lg n$ | appendix | $n^2$ | $\to 2$ | leaves: $\Theta(n^2)$ |

In the last two rows the ratio $(a/2)(\lg n - 1)/\lg n$ is not a constant. The ratio form's equal case misses $n\lg n$, and the textbook form's $k = 1$ catches it; for $4T(n/2) + n\lg n$ the ratio is at least $3/2$ once $n \ge 16$, which is enough for the leaves case (and $n\lg n = O(n^{1.5})$ is polynomially smaller than $n^2$).

**When it does not apply.** Then go back to the recursion tree, or to one of the tools below.

| recurrence | why not | instead | solution |
|---|---|---|---|
| $T(n-1) + n$ (quicksort's worst case) | subtracts: the size drops by 1, not by a factor $b$ | the tree is a path: $n + (n-1) + \dots + 1$ | $\Theta(n^2)$ |
| $2T(n-1) + 1$ (Hanoi) | subtracts | induction: $2^n - 1$ | $\Theta(2^n)$ |
| $T(n/5) + T(7n/10) + n$ (MomSelect) | two different sizes | tree: level sums $(9/10)^i n$; or Akra–Bazzi | $\Theta(n)$ |
| $T(n/3) + T(2n/3) + n$ | two different sizes | tree: levels at most $n$, depth $\Theta(\log n)$ | $\Theta(n\log n)$ |
| $2T(n/2) + n/\lg n$ | $f$ is below the leaves' $n$ only by a log factor: a gap between the cases | tree: level $i$ sums to $n/(\lg n - i)$, a harmonic sum | $\Theta(n\log\log n)$ |
| $\sqrt n\,T(\sqrt n) + n$ | $a = \sqrt n$ is not a constant | tree: every level sums to $n$, $\lg\lg n$ levels | $\Theta(n\log\log n)$ |
| $2T(\sqrt n) + \lg n$ | $n \mapsto \sqrt n$ is not $n \mapsto n/b$ | domain transformation: $S(m) = T(2^m)$ satisfies $S(m) = 2S(m/2) + m$ | $\Theta(\log n\log\log n)$ |

The gap row is [[2-algorithms/01-recursion-exercises#n-n-over-log-n-per-node|Ex. 1.8(n)]]: exactly $T(n) = n(1 + H_{\lg n})$ at powers of 2 with $T(1) = 1$, where $H_k = \ln k + O(1)$ is the $k$-th harmonic number.

> [!note] Akra–Bazzi (what the appendix calls the nuclear bomb)
> For $T(n) = \sum_{i=1}^{k} a_i\,T(n/b_i) + f(n)$ with constants $k$, $a_i > 0$, $b_i > 1$, and $f$ polynomially bounded (any $\Theta(n^c\log^j n)$, including constants), let $\rho$ be the unique real number with $\sum_i a_i/b_i^{\rho} = 1$. Then
> $$
> T(n) = \Theta\Big(n^\rho\Big(1 + \int_1^n \frac{f(u)}{u^{\rho+1}}\,du\Big)\Big).
> $$
> - **MomSelect**, $T(n/5) + T(7n/10) + n$: the left side of $(1/5)^\rho + (7/10)^\rho = 1$ decreases in $\rho$ and is $2$ at $\rho = 0$ and $9/10$ at $\rho = 1$, so $0 < \rho < 1$ ($\rho \approx 0.8398$). Then $\int_1^n u^{-\rho}\,du = (n^{1-\rho} - 1)/(1 - \rho) = \Theta(n^{1-\rho})$ and $T(n) = \Theta(n^\rho\cdot n^{1-\rho}) = \Theta(n)$.
> - **Ham-sandwich trees**, $T(n/2) + T(n/4) + 1$: with $x = 2^\rho$ the equation is $1/x + 1/x^2 = 1$, so $x = \phi = (1+\sqrt5)/2$ and $\rho = \lg\phi \approx 0.6942$. The integral $\int_1^n u^{-\rho-1}\,du < 1/\rho$ is bounded, so $T(n) = \Theta(n^{\lg\phi})$ — recursion trees alone only bracket it between $\sqrt n$ and $n$.
>
> With one term, $\rho = \log_b a$ and the formula gives back the Master Theorem. For $2T(n/2) + n/\lg n$, $\rho = 1$, and the integral $\int_2^n du/(u\lg u) = \Theta(\log\log n)$ (started at 2, where $\lg u > 0$) gives the gap row's $\Theta(n\log\log n)$.

> [!trap]
> - **$\log_b a$, not $\log_a b$.** The leaves number $a^{\log_b n} = n^{\log_b a}$. For $3T(n/2) + n$, $\log_2 3 \approx 1.585$ gives the right $\Theta(n^{\lg 3})$; $\log_3 2 \approx 0.63$ would make $f = n$ win and give the wrong $\Theta(n)$. And $b$ is how much the *size* shrinks, not the number of pieces: StoogeSort's $3T(2n/3) + 1$ has $b = 3/2$.
> - **The equal case multiplies by $\log n$.** $2T(n/2) + n$ is $\Theta(n\log n)$, not $\Theta(n)$; and $2T(n/2) + n\lg n$ is $\Theta(n\log^2 n)$, one log more than $f$.
> - **Subtractive recurrences are out.** $T(n) = T(n-1) + n$ has no $b$; it is $\Theta(n^2)$, not $\Theta(n)$ or $\Theta(n\log n)$.
> - **Polynomially larger, not merely larger.** $n\lg n$ beats $n$ only by a log, so $2T(n/2) + n\lg n$ is not in the root case ($\Theta(n\log n)$ is wrong); $n/\lg n$ is below $n$ only by a log, so $2T(n/2) + n/\lg n$ is not in the leaves case ($\Theta(n)$ is wrong).
> - **The rubric wants both** the recurrence and its closed-form solution, one point each ([[0-toolkit/06-how-exams-are-graded#11-recursive-algorithms|recursive-algorithm rubric]]). "$O(n^{\lg 3})$ by the Master Theorem" without $T(n) = 3T(n/2) + O(n)$ loses a point; naming the case is the justification.

**Where it appears.** [[2-algorithms/01-recursion#17-recursion-trees|§1.7]] (the three cases and their $n^d$ form, which is this theorem), [[2-algorithms/01-recursion#14-mergesort|§1.4]] mergesort, [[2-algorithms/01-recursion#18-linear-time-selection|§1.8]] selection (MomSelect's two sizes are outside the theorem), [[2-algorithms/01-recursion#19-fast-multiplication|§1.9]] multiplication, [[2-algorithms/01-recursion#110-exponentiation|§1.10]] repeated squaring. Exercises: [[2-algorithms/01-recursion-exercises#exercise-16--nine-recurrences|1.6]] (nine direct applications), [[2-algorithms/01-recursion-exercises#exercise-17--unbalanced-recursion-trees|1.7]] (unequal splits; part (l) uses the Akra–Bazzi exponent), [[2-algorithms/01-recursion-exercises#exercise-18--logarithms-and-square-roots|1.8]] (the gaps and the square roots), [[2-algorithms/01-recursion-exercises#exercise-111--stoogesort|1.11]], [[2-algorithms/01-recursion-exercises#exercise-112--cruel-and-unusual|1.12]]. The ratio form and the Akra–Bazzi examples are from the appendix *Solving Recurrences* of Erickson's lecture notes.

Related: [[concepts/recursion-trees]] · [[concepts/divide-and-conquer]] · [[concepts/linear-time-selection]] · [[concepts/recursion]]
