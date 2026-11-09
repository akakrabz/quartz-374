---
title: "Linear recurrences"
description: "Recurrences T(n) = c₁T(n−1) + ⋯ + c_kT(n−k) + g(n) with constant coefficients, solved with the shift operator E and annihilators: the characteristic polynomial, the solution forms for distinct and repeated roots, non-homogeneous terms and which constants the base cases fix, and the largest-root shortcut for Θ-bounds."
tags: [concept, algorithms, recursion]
aliases: ["linear recurrence", "annihilator", "annihilator method", "characteristic polynomial", "homogeneous recurrence"]
---

> [!key] Linear recurrences and their solutions
> A **linear recurrence with constant coefficients** has the form $T(n) = c_1T(n-1) + \cdots + c_kT(n-k) + g(n)$. With the **shift operator** $E$, $(ET)(n) = T(n+1)$, it reads $\chi(E)\,T = E^k g$, where
> $$
> \chi(x) = x^k - c_1x^{k-1} - \cdots - c_k
> $$
> is the **characteristic polynomial**. An **annihilator** of $f$ is a nonzero operator $X$ with $Xf = 0$; $(E - r)^m$ annihilates exactly the functions $p(n)\,r^n$ with $\deg p < m$.
> - **Homogeneous** ($g = 0$): if $\chi(x) = \prod_j (x - r_j)^{m_j}$, then $T(n) = \sum_j p_j(n)\,r_j^n$ with $\deg p_j < m_j$ — distinct roots give $\sum_j\alpha_j r_j^n$. The $k$ constants come from $k$ base cases.
> - **Non-homogeneous**: multiply $\chi(E)$ by an annihilator of $g$ — $E - 1$ for a constant, $(E-1)^{d+1}$ for a polynomial of degree $d$, $(E - s)^{d+1}$ for $n^d s^n$ — and read the form off the product. A root of $g$'s annihilator that is already a root of $\chi$ raises its multiplicity.
> - **Growth:** the term with the largest $\lvert r\rvert$ (and the highest power of $n$) whose coefficient is not zero.

**Why it works.** $(E - r)\,r^n = 0$, and $(E - r)\big(p(n)\,r^n\big) = \big(p(n+1) - p(n)\big)\,r^{n+1}$ lowers the degree of $p$ by one. Operators built from $E$ multiply like polynomials, so they commute and factor. A $k$-th order recurrence has a $k$-dimensional space of solutions ($k$ initial values determine the rest), spanned by the $k$ independent functions $n^i r_j^n$ ($i < m_j$). Plugging $T(n) = r^n$ into the homogeneous recurrence gives $\chi(r) = 0$: the same polynomial by the usual textbook route.

> [!recipe] Solving one
> 1. **Operator form**, shifted so every argument is $n$ or more: $T(n+k) - c_1T(n+k-1) - \cdots - c_kT(n) = g(n+k)$. Shift the residue too.
> 2. **Annihilator:** $\chi(E)$ times an annihilator of $g$. **Factor** it.
> 3. **Generic solution** from the roots and their multiplicities.
> 4. **Constants.** The terms coming from $g$ have *forced* coefficients: substitute them into the recurrence and match. The remaining $k$ constants come from the base cases (a small linear system).
> 5. **Check** the formula against $T(0), \ldots, T(k+2)$ computed from the recurrence.

> [!trap]
> - **Signs flip** in the operator form: $T(n) = 5T(n-1) - 8T(n-2) + 4T(n-3)$ is $(E^3 - 5E^2 + 8E - 4)T = 0$, which is $(E-2)^2(E-1)T = 0$. (Erickson's appendix misprints the 5 as 3; that recurrence has complex roots of modulus about 2.56.)
> - **Repeated roots need $n\,r^n$:** $T(n) = 4T(n-1) - 4T(n-2)$, $T(0) = 1$, $T(1) = 3$ is $(n+2)\,2^{n-1}$, not $\alpha 2^n$.
> - **A residue sharing a root multiplies by $n$:** $T(n) = 2T(n-1) + 2^n$, $T(0) = 0$ is $n\,2^n$, so $\Theta(n2^n)$, not $\Theta(2^n)$.
> - **Only $k$ constants are free;** the residue's coefficients are fixed (the appendix's p. 17 gets this wrong).
> - **Base cases can cancel the dominant root:** the Fibonacci recurrence with $T(0) = 1$, $T(1) = \hat\phi$ gives $\hat\phi^n\to 0$. Positive coefficients and positive base cases rule this out.
> - **Divide-and-conquer recurrences are not linear** in this sense; transform first: $t(k) = T(2^k)$.

**Example.** $T(n) = 2T(n-1) + n$ with $T(0) = 0$. In operator form $(E - 2)T(n) = n + 1$; the residue needs $(E-1)^2$, so $T(n) = \alpha 2^n + \beta n + \gamma$. The forced part: $\beta n + \gamma - 2\big(\beta(n-1) + \gamma\big) = n$ for all $n$ gives $\beta = -1$, $\gamma = -2$. Then $T(0) = 0$ gives $\alpha = 2$:
$$
T(n) = 2^{n+1} - n - 2 \qquad (0, 1, 4, 11, 26, \ldots) = \Theta(2^n).
$$

**Shortcut for $\Theta$.** If all $c_i\ge 0$ with $c_1 + \cdots + c_k > 1$, $g$ is a non-negative polynomial and the base cases are positive, then $T(n) = \Theta(r^n)$ for the unique positive root $r > 1$ of $\chi$: $T(n-1) + T(n-2) + 1$ grows like $\phi^n$, $T(n-1) + T(n-3) + 1$ like $1.4656^n$. If the $c_i$ add up to exactly 1, $r = 1$ and the growth is polynomial: unroll.

**Where it appears.** [[4-lecture-notes/99-solving-recurrences#5-linear-recurrences-annihilators|Appendix II, §5]] (the annihilator table, six worked examples, Binet's formula) and [[4-lecture-notes/99-solving-recurrences#6-transformations|§6]] (divide-and-conquer recurrences made linear by $t(k) = T(2^k)$). In the book: Hanoi's $2T(n-1) + 1$ ([[2-algorithms/01-recursion#13-tower-of-hanoi|§1.3]]), RecFibo's $2F_{n+1} - 1$ calls ([[2-algorithms/03-dynamic-programming#31-matravrtta-fibonacci-numbers|§3.1]]) and the matrix form of Fibonacci ([[2-algorithms/03-dynamic-programming#32-aside-even-faster-fibonacci-numbers|§3.2]]), and backtracking running times: $T(n-1) + T(n-2) + O(1)$ in [[2-algorithms/02-backtracking#22-game-trees|§2.2]], $2T(n-1) + \alpha$ and $3T(n-1) + \alpha$ in [[2-algorithms/02-backtracking#25-text-segmentation|§2.5]] and [[2-algorithms/02-backtracking#28-optimal-binary-search-trees|§2.8]].

Related: [[concepts/recursion-trees]] · [[concepts/master-theorem]] · [[concepts/backtracking]] · [[concepts/recursion]] · [[concepts/dynamic-programming]]
