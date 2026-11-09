---
title: "Solving recurrences"
description: "Erickson's Appendix II, checked: guess and confirm by induction (Hanoi, Fibonacci, mergesort, √n·T(√n) + n), recursion trees and the ratio-form Master Theorem, lopsided and weighted trees, the Akra–Bazzi formula, linear recurrences by annihilators (operators, the annihilator table, homogeneous and non-homogeneous examples), and domain, range and difference transformations — with a table of which method fits which shape, and the note's errors corrected (the cubic example's coefficient, a row of the annihilator table, the forced coefficient on p. 17)."
tags: [lecture-notes, algorithms, recursion, midterm-2]
note: "99"
---

*Erickson, lecture notes · Appendix II · 22 pp. · [PDF](https://jeffe.cs.illinois.edu/teaching/algorithms/notes/99-recurrences.pdf) · CC BY-NC-SA 4.0 · [[4-lecture-notes/index|all notes]]*

> [!abstract] In one breath
> A **recurrence** describes a function by its values on smaller arguments; solving it means finding a closed form, exact or up to $\Theta$. The one method that always works is **guess and confirm**: guess, by unrolling or by tabulating small values, then prove the guess by induction — and when the proof fails, the way it fails tells you how to change the guess. For divide-and-conquer recurrences the **recursion tree** turns $T(n)$ into a sum of level sums; when they form a geometric series the largest term decides (the **Master Theorem**), and lopsided or weighted trees still give bounds. **Akra–Bazzi** solves almost any $\sum_i a_i T(n/b_i) + f(n)$ with one exponent and one integral. **Linear recurrences** with constant coefficients fall to **annihilators**: write the recurrence with the shift operator $E$, factor the polynomial in $E$, read off a sum of terms $n^j r^n$, and fit the constants. **Transformations** of the domain ($n = 2^k$), the range ($U = nT$) or by subtracting shifted copies turn most other recurrences into one of these forms.

> [!note] Where this fits
> The three cases of a recursion tree are [[2-algorithms/01-recursion#17-recursion-trees|§1.7]] of the book and the concept pages [[concepts/recursion-trees]] and [[concepts/master-theorem]] (which already state the Master Theorem in this appendix's ratio form, the textbook form and Akra–Bazzi); this page links to them instead of repeating them. The appendix's running examples are the book's: [[2-algorithms/01-recursion#13-tower-of-hanoi|Tower of Hanoi]], [[2-algorithms/01-recursion#14-mergesort|mergesort]], [[2-algorithms/01-recursion#18-linear-time-selection|selection]], [[2-algorithms/01-recursion#19-fast-multiplication|Karatsuba]] and [[2-algorithms/03-dynamic-programming#31-matravrtta-fibonacci-numbers|Fibonacci numbers]]. What is new here is guess and confirm as a method, the annihilator method for linear recurrences ([[concepts/linear-recurrences]]) and transformations. **CS 374:** not assigned reading this semester, but its subject is examined: Midterm 2 (Mon Nov 9) opens with recurrences to solve (three in each Fall 2025 version), and the final (Fri Dec 11) covers everything again. Sections 4 and 5 are marked ★ (optional) in the note.

## 1 Introduction

> [!definition] Definition — recurrence, solution, closed form
> A **recurrence** describes a function in terms of itself: one or more **base cases** give explicit values for a few (usually small) arguments, and one or more **recursive cases** relate $f(n)$ to values $f(k)$ with $k < n$. Each case is an equation or an inequality. A function **satisfies** (is a **solution** of) the recurrence if every case is true for it. When every case is an equation the solution is unique — it is the function computed by reading the recurrence as a recursive algorithm.
>
> A **closed-form solution** is a non-recursive description of that function, either exact or asymptotic, $\Theta(g(n))$ for an explicit $g$. For a recursive *inequality* the goal is a **tight** bound: one that would still hold if every inequality were an equation.

The same function satisfies many recurrences. The identity $f(n) = n$ satisfies $f(0) = 0$, $f(n) = f(n-1) + 1$; also $f(0) = 0$, $f(1) = 1$, $f(n) = f(\lfloor n/2\rfloor) + f(\lceil n/2\rceil)$; and also $f(0) = 0$, $f(n) = 2f(n/2)$ for even $n > 0$, $f(n) = f(n-1) + 1$ for odd $n$. Recurrences describe running times of recursive algorithms (one recursive case per recursive branch of the algorithm) and answer counting questions, and a recurrence alone is not a satisfying answer to either: we want its closed form.

## 2 The ultimate method: guess and confirm

> [!key] Guess and confirm
> **Guess** a closed form, then **prove it by induction**. It does not matter where the guess comes from — unrolling, a table of small values, a similar recurrence, a recursion tree. If the proof succeeds you are done; if it fails, the failure shows whether the guess was too big or too small.

### 2.1 Tower of Hanoi

The book's [[2-algorithms/01-recursion#13-tower-of-hanoi|Hanoi]] recurrence is $T(0) = 0$, $T(n) = 2T(n-1) + 1$. Its first values $0, 1, 3, 7, 15, 31, 63$ are each one less than a power of two, so guess $T(n) = 2^n - 1$: the base case is $2^0 - 1 = 0$, and $2T(n-1) + 1 = 2(2^{n-1} - 1) + 1 = 2^n - 1$.

A second way to guess is to **unroll** the recurrence into itself: $T(n) = 2T(n-1) + 1 = 4T(n-2) + 3 = 8T(n-3) + 7 = \cdots$, which suggests
$$
T(n) = 2^k\,T(n-k) + (2^k - 1)\qquad\text{for every } 0\le k\le n.
$$
This is itself proved by induction on $k$ (substitute the recurrence for $T(n-k+1)$), and $k = n$ gives $T(n) = 2^n T(0) + 2^n - 1 = 2^n - 1$.

### 2.2 Fibonacci numbers

For $F_0 = 0$, $F_1 = 1$, $F_n = F_{n-1} + F_{n-2}$ there is no visible pattern, but exponential growth is a safe guess. Try to prove $F_n \le \alpha c^n$ and see what the proof needs:
$$
F_n = F_{n-1} + F_{n-2} \le \alpha c^{n-1} + \alpha c^{n-2} \overset{?}{\le} \alpha c^n
\quad\Longleftrightarrow\quad c^2 - c - 1 \ge 0 .
$$
The smallest such $c$ is the larger root of $c^2 = c + 1$, the golden ratio $\phi = (1+\sqrt5)/2 \approx 1.618034$ (the other root has smaller absolute value). The base cases decide $\alpha$: $F_0/\phi^0 = 0$ and $F_1/\phi = 1/\phi \approx 0.618034$, so $\alpha = 1/\phi$ works and
$$
F_n \le \phi^{n-1}\qquad\text{for all } n\ge 0.
$$
The same step proves $F_n \ge \beta\phi^n$, but with $F_0 = 0$ as a base case only $\beta = 0$ works. An $\Omega$-bound only needs large $n$, so start the induction at the base cases $F_1$ and $F_2$ instead: $F_2/\phi^2 \approx 0.381966$ is the smaller ratio, so $\beta = 1/\phi^2$ and $F_n \ge \phi^{n-2}$ for all $n\ge 1$. Together, $F_n = \Theta(\phi^n)$. The exact formula needs annihilators (§5.3).

### 2.3 Mergesort

[[2-algorithms/01-recursion#14-mergesort|Mergesort]] has worst-case time $T(n) = T(\lceil n/2\rceil) + T(\lfloor n/2\rfloor) + \Theta(n)$ with $T(1) = \Theta(1)$. Two simplifications before solving: take $n$ a power of 2, which removes the floors and ceilings (§6 shows they do not matter), and **remove the $\Theta$s**, solving $T(1) = 1$, $T(n) = 2T(n/2) + n$; any asymptotic solution of the simplified recurrence is one of the original. Unrolling suggests $T(n) = 2^k T(n/2^k) + kn$, which induction on $k$ confirms, and at $k = \lg n$,
$$
T(n) = n\,T(1) + n\lg n = n\lg n + n = \Theta(n\log n).
$$

> [!trap] Why the $\Theta$s go first
> Kept inside an induction, asymptotic notation hides a constant that changes at every step. The classic bogus proof: “assume $T(n/2) = O(n/2)$; then $T(n) = 2\,O(n/2) + O(n) = O(n)$.” Each level of the induction silently enlarges the constant, and after $\lg n$ levels it is no longer a constant — the true answer is $\Theta(n\log n)$. Prove $T(n)\le a\cdot g(n)$ with one explicit constant $a$, the same in the hypothesis and the conclusion.

### 2.4 An uglier divide-and-conquer example

$T(n) = \sqrt n\,T(\sqrt n) + n$ has a non-constant number of subproblems, so no Master Theorem; but the subproblems have total size $n$, like mergesort's. Try guesses, proving an upper bound $T(n)\le a\,g(n)$ and a lower bound $T(n)\ge b\,g(n)$ for large $n$ by induction:

| guess $g(n)$ | upper bound: $\sqrt n\cdot a\,g(\sqrt n) + n \le a\,g(n)$? | lower bound: $\ldots\ge b\,g(n)$? | verdict |
|---|---|---|---|
| $n\lg n$ | $\tfrac a2\,n\lg n + n \le a\,n\lg n$ once $n\ge 2^{2/a}$: works for **every** $a > 0$ | $\tfrac b2\,n\lg n + n\ge b\,n\lg n$ fails for large $n$ | too big |
| $n$ | $(a+1)\,n\le a\,n$ fails | $T(n)\ge n$ directly | too small |
| $n\sqrt{\lg n}$ | $\tfrac{a}{\sqrt2}\,n\sqrt{\lg n} + n\le a\,n\sqrt{\lg n}$ for large $n$ | $\tfrac{b}{\sqrt2}\,n\sqrt{\lg n} + n \ge b\,n\sqrt{\lg n}$ fails | too big |
| $n\lg\lg n$ | $a\,n\lg\lg n - a\,n + n\le a\,n\lg\lg n$ **iff $a\ge 1$** | $b\,n\lg\lg n - b\,n + n\ge b\,n\lg\lg n$ **iff $b\le 1$** | right |

(The algebra uses $\lg\sqrt n = \tfrac12\lg n$ and $\lg\lg\sqrt n = \lg\lg n - 1$.) Two lessons. An upper-bound proof that works for every constant, however small, signals a bound that is not tight. A proof that forces a condition on the constant ($a\ge 1$) signals the right answer. So $T(n) = \Theta(n\log\log n)$; the base cases still have to be checked. Exactly: at $n = 2^{2^k}$, dividing by $n$ gives $T(n)/n = T(\sqrt n)/\sqrt n + 1$, so $T(n) = n(\lg\lg n + 1)$ with $T(2) = 2$. The same recurrence is solved with a recursion tree in [[2-algorithms/01-recursion-exercises#p-square-root-branching|Exercise 1.8(p)]] and in §3 below.

> [!template] Template — confirming a guess $T(n)\le a\,g(n)$
> - **Claim.** $T(n)\le a\,g(n)$ for all $n\ge n_0$, for a constant $a$ chosen at the end.
> - **Base cases.** Every $n\ge n_0$ whose recursive calls fall below $n_0$; check each directly (this fixes how large $a$ must be).
> - **Inductive step.** Assume $T(m)\le a\,g(m)$ for all $n_0\le m < n$. Substitute into the recurrence and simplify until you reach $a\,g(n)$, noting every condition used (such as $n\ge 2^{2/a}$ or $a\ge 1$).
> - **Conclusion.** Choose $a$ (and $n_0$) to meet the base cases and all conditions. The lower bound $T(n)\ge b\,g(n)$ is the same with $\ge$.

## 3 Divide and conquer recurrences (recursion trees)

For $T(n) = a\,T(n/b) + f(n)$ the **recursion tree** is a complete $a$-ary tree whose nodes at depth $i$ hold $f(n/b^i)$; there are $a^i$ of them, the depth is $L = \log_b n$, and
$$
T(n) = \sum_{i=0}^{L} a^i f(n/b^i), \qquad (\Sigma)
$$
whose last term is $\Theta(a^L) = \Theta(n^{\log_b a})$, one unit per leaf. The exact base case does not matter — $T(n) = \Theta(1)$ for all $n\le 10^{100}$ would do — and $n$ is taken to be a power of $b$. When the level sums form a geometric series only the largest term matters. The method, its pictures and the three cases are on [[2-algorithms/01-recursion#17-recursion-trees|§1.7]] and [[concepts/recursion-trees]]; here are the appendix's examples, with exact values added for the stated base cases.

| recurrence | level $i$ sum | case | solution | exactly |
|---|---|---|---|---|
| $2T(n/2) + n$ | $n$ | equal | $\Theta(n\log n)$ | $n\lg n + n$ |
| $T(3n/4) + n$ | $(3/4)^i\,n$ | decreasing | $\Theta(n)$ | $4n - 3$ |
| $3T(n/2) + n$ | $(3/2)^i\,n$ | increasing | $\Theta(n^{\lg 3})$ | $3n^{\lg 3} - 2n$ |
| $2T(n/2) + n/\lg n$ | $n/(\lg n - i)$ | none: harmonic | $\Theta(n\log\log n)$ | $n\,H_{\lg n}$ |
| $4T(n/2) + n\lg n$ | $n\,2^i(\lg n - i)$ | none; leaves win | $\Theta(n^2)$ | $2n^2 - n\lg n - 2n$ |
| $\sqrt n\,T(\sqrt n) + n$ | $n$ | equal, $\lg\lg n$ levels | $\Theta(n\log\log n)$ | $n(\lg\lg n + 1)$ |

The first three are mergesort, randomized selection and Karatsuba. The exact values hold at powers of 2 with $T(1) = 1$ (rows 1 and 3), at $n = (4/3)^k$ with $T(1) = 1$ (row 2), at powers of 2 with $T(2) = 2$ and $T(1) = 0$ (rows 4 and 5), and at $n = 2^{2^k}$ with $T(2) = 2$ (row 6).

- **Randomized selection** is a path, not a tree; its depth $\log_{4/3} n$ is irrelevant because the series decreases. **Karatsuba**'s last level is $(3/2)^L n = 3^{\lg n} = n^{\lg 3}$, the number of leaves.
- **$n/\lg n$ per node.** The tree stops at size 2 (depth $\lg n - 1$), and the level sums are neither constant nor geometric, so add them: $\sum_{i=0}^{\lg n - 1} n/(\lg n - i) = n\sum_{j=1}^{\lg n} 1/j = n H_{\lg n}$, where the **harmonic number** $H_m = \sum_{j=1}^{m} 1/j$ satisfies $\ln(m+1)\le H_m\le\ln m + 1$. So $T(n) = \Theta(n\log\log n)$.
- **$n\lg n$ per node with four children.** Substituting $j = \lg n - i$ turns the level sums into $n^2\sum_{j=1}^{\lg n} j/2^j$, and $\sum_{j=1}^{m} j/2^j = 2 - (m+2)/2^m < 2$. The sum is not geometric, yet it is within a constant factor of its largest term. (The note prints the lower limit as $j = i$, p. 8; it is $j = 1$.)
- **$\sqrt n$ children.** Level $i$ has $n^{1-2^{-i}}$ nodes of size $n^{2^{-i}}$, so every level sums to $n$; square roots never reach 1, so the tree stops at size 2, at depth $L$ with $n^{2^{-L}} = 2$, that is $L = \lg\lg n$. For $n = 65536$: 1 node of size 65536, then 256 of size 256, 4096 of size 16, 16384 of size 4 and 32768 of size 2 — five levels of 65536 each.

**Lopsided trees.** When the subproblems have different sizes, nodes on the same level differ and leaves sit at different depths; only the **complete** levels (above the shallowest leaf) have predictable sums. Count only the complete levels for a lower bound; ignore the base cases and extend every level down to the deepest leaf (or to infinity) for an upper bound.

<!-- fig:n99-lopsided -->
<figure class="cs-fig"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 328" width="640" height="328" role="img" style="font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-size:13px"><title>two recursion trees drawn three levels deep, each continuing as a shaded region whose left side stops at depth log base 4 of n and whose right side reaches the deepest leaf; level sums shown at the right</title><defs><marker id="ARR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs><text x="10" y="16" text-anchor="start" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">T(n) = T(n/4) + T(3n/4) + n</text><text x="246" y="38" text-anchor="start" dominant-baseline="central" fill="var(--muted)" style="font-size:11px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">level sum</text><path d="M26,134 L12,196 L214.8,196 L208,134 Z" fill="var(--accent)" fill-opacity="0.16" stroke="none"/><path d="M12,196 L192,262 L222,262 L214.8,196 Z" fill="var(--muted)" fill-opacity="0.13" stroke="none"/><path d="M26,134 L12,196 L192,262 L222,262 L208,134" fill="none" stroke="var(--accent)" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/><line x1="8" y1="196" x2="304" y2="196" stroke="var(--hi)" stroke-width="1.2" stroke-linecap="round" stroke-dasharray="4 3"/><line x1="222" y1="262" x2="304" y2="262" stroke="var(--muted)" stroke-width="1.0" stroke-linecap="round" stroke-dasharray="2 3"/><text x="117" y="158" text-anchor="middle" dominant-baseline="central" fill="var(--accent)" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">complete levels</text><text x="169" y="236" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">ragged levels</text><text x="121" y="185" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:11.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">depth log<tspan dy="4" style="font-size:9.5px">4</tspan><tspan dy="-4"> n: shallowest leaf</tspan></text><text x="222" y="276" text-anchor="end" dominant-baseline="central" fill="var(--muted)" style="font-size:11.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">depth log<tspan dy="4" style="font-size:9.5px">4/3</tspan><tspan dy="-4"> n: deepest</tspan></text><line x1="117" y1="65" x2="61.5" y2="79" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" opacity="0.55"/><line x1="117" y1="65" x2="172.5" y2="79" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" opacity="0.55"/><line x1="61.5" y1="97" x2="33.8" y2="111" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" opacity="0.55"/><line x1="61.5" y1="97" x2="89.2" y2="111" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" opacity="0.55"/><line x1="172.5" y1="97" x2="144.8" y2="111" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" opacity="0.55"/><line x1="172.5" y1="97" x2="200.2" y2="111" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" opacity="0.55"/><line x1="33.8" y1="129" x2="26.8" y2="135" stroke="currentColor" stroke-width="1.0" stroke-linecap="round" opacity="0.35"/><line x1="33.8" y1="129" x2="40.8" y2="135" stroke="currentColor" stroke-width="1.0" stroke-linecap="round" opacity="0.35"/><line x1="89.2" y1="129" x2="82.2" y2="135" stroke="currentColor" stroke-width="1.0" stroke-linecap="round" opacity="0.35"/><line x1="89.2" y1="129" x2="96.2" y2="135" stroke="currentColor" stroke-width="1.0" stroke-linecap="round" opacity="0.35"/><line x1="144.8" y1="129" x2="137.8" y2="135" stroke="currentColor" stroke-width="1.0" stroke-linecap="round" opacity="0.35"/><line x1="144.8" y1="129" x2="151.8" y2="135" stroke="currentColor" stroke-width="1.0" stroke-linecap="round" opacity="0.35"/><line x1="200.2" y1="129" x2="193.2" y2="135" stroke="currentColor" stroke-width="1.0" stroke-linecap="round" opacity="0.35"/><line x1="200.2" y1="129" x2="207.2" y2="135" stroke="currentColor" stroke-width="1.0" stroke-linecap="round" opacity="0.35"/><rect x="103" y="47" width="28" height="18" rx="4" fill="var(--paper)" stroke="currentColor" stroke-width="1.1"/><text x="117" y="56.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n</text><rect x="41.5" y="79" width="40" height="18" rx="4" fill="var(--paper)" stroke="currentColor" stroke-width="1.1"/><text x="61.5" y="88.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n/4</text><rect x="152.5" y="79" width="40" height="18" rx="4" fill="var(--paper)" stroke="currentColor" stroke-width="1.1"/><text x="172.5" y="88.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">3n/4</text><rect x="11.8" y="111" width="44" height="18" rx="4" fill="var(--paper)" stroke="currentColor" stroke-width="1.1"/><text x="33.8" y="120.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n/16</text><rect x="67.2" y="111" width="44" height="18" rx="4" fill="var(--paper)" stroke="currentColor" stroke-width="1.1"/><text x="89.2" y="120.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">3n/16</text><rect x="122.8" y="111" width="44" height="18" rx="4" fill="var(--paper)" stroke="currentColor" stroke-width="1.1"/><text x="144.8" y="120.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">3n/16</text><rect x="178.2" y="111" width="44" height="18" rx="4" fill="var(--paper)" stroke="currentColor" stroke-width="1.1"/><text x="200.2" y="120.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">9n/16</text><text x="246" y="56.5" text-anchor="start" dominant-baseline="central" fill="var(--accent)" style="font-size:12.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n</text><text x="246" y="88.5" text-anchor="start" dominant-baseline="central" fill="var(--accent)" style="font-size:12.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n</text><text x="246" y="120.5" text-anchor="start" dominant-baseline="central" fill="var(--accent)" style="font-size:12.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n</text><text x="246" y="162" text-anchor="start" dominant-baseline="central" fill="var(--accent)" style="font-size:12.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n each</text><text x="246" y="232" text-anchor="start" dominant-baseline="central" fill="var(--muted)" style="font-size:12.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">&lt; n each</text><text x="10" y="298" text-anchor="start" dominant-baseline="central" fill="currentColor" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">n log<tspan dy="4" style="font-size:9.5px">4</tspan><tspan dy="-4"> n</tspan> ≤ T(n) ≤ n(log<tspan dy="4" style="font-size:9.5px">4/3</tspan><tspan dy="-4"> n</tspan> + 1)</text><text x="10" y="317" text-anchor="start" dominant-baseline="central" fill="var(--hi)" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">so T(n) = Θ(n log n)</text><line x1="321" y1="30" x2="321" y2="256" stroke="var(--muted)" stroke-width="0.8" stroke-linecap="round" stroke-dasharray="2 4"/><text x="334" y="16" text-anchor="start" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">T(n) = T(n/2) + T(n/4) + 1</text><text x="570" y="38" text-anchor="start" dominant-baseline="central" fill="var(--muted)" style="font-size:11px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">level sum</text><path d="M350,134 L336,196 L538.8,196 L532,134 Z" fill="var(--accent)" fill-opacity="0.16" stroke="none"/><path d="M336,196 L516,262 L546,262 L538.8,196 Z" fill="var(--muted)" fill-opacity="0.13" stroke="none"/><path d="M350,134 L336,196 L516,262 L546,262 L532,134" fill="none" stroke="var(--accent)" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/><line x1="332" y1="196" x2="628" y2="196" stroke="var(--hi)" stroke-width="1.2" stroke-linecap="round" stroke-dasharray="4 3"/><line x1="546" y1="262" x2="628" y2="262" stroke="var(--muted)" stroke-width="1.0" stroke-linecap="round" stroke-dasharray="2 3"/><text x="441" y="158" text-anchor="middle" dominant-baseline="central" fill="var(--accent)" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">complete levels</text><text x="493" y="236" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">ragged levels</text><text x="445" y="185" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:11.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">depth log<tspan dy="4" style="font-size:9.5px">4</tspan><tspan dy="-4"> n: shallowest leaf</tspan></text><text x="546" y="276" text-anchor="end" dominant-baseline="central" fill="var(--muted)" style="font-size:11.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">depth log<tspan dy="4" style="font-size:9.5px">2</tspan><tspan dy="-4"> n: deepest</tspan></text><line x1="441" y1="65" x2="385.5" y2="79" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" opacity="0.55"/><line x1="441" y1="65" x2="496.5" y2="79" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" opacity="0.55"/><line x1="385.5" y1="97" x2="357.8" y2="111" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" opacity="0.55"/><line x1="385.5" y1="97" x2="413.2" y2="111" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" opacity="0.55"/><line x1="496.5" y1="97" x2="468.8" y2="111" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" opacity="0.55"/><line x1="496.5" y1="97" x2="524.2" y2="111" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" opacity="0.55"/><line x1="357.8" y1="129" x2="350.8" y2="135" stroke="currentColor" stroke-width="1.0" stroke-linecap="round" opacity="0.35"/><line x1="357.8" y1="129" x2="364.8" y2="135" stroke="currentColor" stroke-width="1.0" stroke-linecap="round" opacity="0.35"/><line x1="413.2" y1="129" x2="406.2" y2="135" stroke="currentColor" stroke-width="1.0" stroke-linecap="round" opacity="0.35"/><line x1="413.2" y1="129" x2="420.2" y2="135" stroke="currentColor" stroke-width="1.0" stroke-linecap="round" opacity="0.35"/><line x1="468.8" y1="129" x2="461.8" y2="135" stroke="currentColor" stroke-width="1.0" stroke-linecap="round" opacity="0.35"/><line x1="468.8" y1="129" x2="475.8" y2="135" stroke="currentColor" stroke-width="1.0" stroke-linecap="round" opacity="0.35"/><line x1="524.2" y1="129" x2="517.2" y2="135" stroke="currentColor" stroke-width="1.0" stroke-linecap="round" opacity="0.35"/><line x1="524.2" y1="129" x2="531.2" y2="135" stroke="currentColor" stroke-width="1.0" stroke-linecap="round" opacity="0.35"/><rect x="427" y="47" width="28" height="18" rx="4" fill="var(--paper)" stroke="currentColor" stroke-width="1.1"/><text x="441" y="56.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n</text><rect x="365.5" y="79" width="40" height="18" rx="4" fill="var(--paper)" stroke="currentColor" stroke-width="1.1"/><text x="385.5" y="88.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n/2</text><rect x="476.5" y="79" width="40" height="18" rx="4" fill="var(--paper)" stroke="currentColor" stroke-width="1.1"/><text x="496.5" y="88.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n/4</text><rect x="335.8" y="111" width="44" height="18" rx="4" fill="var(--paper)" stroke="currentColor" stroke-width="1.1"/><text x="357.8" y="120.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n/4</text><rect x="391.2" y="111" width="44" height="18" rx="4" fill="var(--paper)" stroke="currentColor" stroke-width="1.1"/><text x="413.2" y="120.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n/8</text><rect x="446.8" y="111" width="44" height="18" rx="4" fill="var(--paper)" stroke="currentColor" stroke-width="1.1"/><text x="468.8" y="120.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n/8</text><rect x="502.2" y="111" width="44" height="18" rx="4" fill="var(--paper)" stroke="currentColor" stroke-width="1.1"/><text x="524.2" y="120.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n/16</text><text x="570" y="56.5" text-anchor="start" dominant-baseline="central" fill="var(--accent)" style="font-size:12.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">1</text><text x="570" y="88.5" text-anchor="start" dominant-baseline="central" fill="var(--accent)" style="font-size:12.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">2</text><text x="570" y="120.5" text-anchor="start" dominant-baseline="central" fill="var(--accent)" style="font-size:12.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">4</text><text x="570" y="162" text-anchor="start" dominant-baseline="central" fill="var(--accent)" style="font-size:12.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">2<tspan dy="-5" style="font-size:9.5px">i</tspan><tspan dy="5"> each</tspan></text><text x="570" y="232" text-anchor="start" dominant-baseline="central" fill="var(--muted)" style="font-size:12.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">&lt; 2<tspan dy="-5" style="font-size:9.5px">i</tspan><tspan dy="5"> each</tspan></text><text x="334" y="298" text-anchor="start" dominant-baseline="central" fill="currentColor" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">√n ≤ T(n) ≤ 2n: the levels alone do not decide</text><text x="334" y="317" text-anchor="start" dominant-baseline="central" fill="var(--hi)" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">T(n) = Θ(n<tspan dy="-5" style="font-size:9.5px">lg φ</tspan><tspan dy="5">) by §4 or §6</tspan></text></svg><figcaption><strong>Lopsided recursion trees.</strong> With unequal pieces the leaves sit at different depths: the all-left path is the shortest, the all-right path the longest. Every level above the shallowest leaf is <em>complete</em>, and below it the levels thin out. Left (randomized quicksort’s split): complete levels sum to exactly <i>n</i> and no level exceeds <i>n</i>, so counting the complete levels gives the lower bound and extending every level to the deepest leaf gives the upper bound — both Θ(<i>n</i> log <i>n</i>). Right (ham-sandwich trees): complete levels double, so the leaves dominate, but the number of leaves is only pinned between 2<sup>log<sub>4</sub> <i>n</i></sup> = √<i>n</i> and <i>n</i>; Akra–Bazzi or the domain transformation <i>t</i>(<i>k</i>) = <i>T</i>(2<sup><i>k</i></sup>) settles it.</figcaption></figure>

- **$T(3n/4) + T(n/4) + n$** (the split of randomized quicksort): complete levels sum to $n$, no level exceeds $n$, and the leaves lie between depths $\log_4 n$ and $\log_{4/3} n$. With $T(n) = 0$ below size 1, $n\log_4 n\le T(n)\le n(\log_{4/3} n + 1)$, so $T(n) = \Theta(n\log n)$. (The note calls the lower-bound step an “overestimate”, p. 9; counting fewer levels underestimates. It also drops the $+1$ that the level count gives; without it the upper bound is false for some $n < 2$, such as $n = 1$, though it holds for all $n\ge 2$.)
- **$T(n/5) + T(7n/10) + n$** (deterministic selection): complete levels sum to $n, \tfrac{9}{10}n, \tfrac{81}{100}n, \ldots$; the whole infinite series is $10n$, so $n\le T(n)\le 10n$ and $T(n) = \Theta(n)$.
- **$\tfrac14T(n/4) + \tfrac34T(3n/4) + 1$** (randomized search trees): a quarter of a child makes sense as a **weight**. Equivalently add a second parameter, $T(n) = T(n, 1)$ with $T(n,\alpha) = T(n/4, \alpha/4) + T(3n/4, 3\alpha/4) + \alpha$: an ordinary tree whose complete levels each sum to exactly 1. Leaves again lie between depths $\log_4 n$ and $\log_{4/3} n$, so $\log_4 n\le T(n)\le\log_{4/3} n + 1$ and $T(n) = \Theta(\log n)$.
- **$T(n/2) + T(n/4) + 1$** (ham-sandwich trees): complete levels sum to $1, 2, 4, \ldots$, so the leaves dominate — but the number of leaves is only pinned between $2^{\log_4 n} = \sqrt n$ and $2^{\log_2 n} = n$. Trees alone cannot decide; §4 and §6 both give $\Theta(n^{\lg\phi})$.

> [!key] The Master Theorem (the appendix's form)
> For $T(n) = a\,T(n/b) + f(n)$: if $a\,f(n/b) = \kappa f(n)$ with a constant $\kappa < 1$, then $T(n) = \Theta(f(n))$; if $a\,f(n/b) = K f(n)$ with a constant $K > 1$, then $T(n) = \Theta(n^{\log_b a})$; if $a\,f(n/b) = f(n)$, then $T(n) = \Theta(f(n)\log n)$; otherwise you are on your own.

It is the recursion tree with the ratio between consecutive level sums written out: by induction the level sums of $(\Sigma)$ form a geometric series with ratio $\kappa$, $K$ or 1, and a geometric series is a constant times its largest term — the first, the last ($\Theta(n^{\log_b a})$), or all $L + 1$ equal terms. (The note's proof writes $a\,f(b/n)$ for $a\,f(n/b)$ three times, p. 10.) Erickson himself finds the recursion tree easier to remember than the theorem. The textbook $n^{\log_b a}$ form, the inequality versions, the regularity condition and a table of solved recurrences are on [[concepts/master-theorem]].

## 4 The nuclear bomb

(★ in the note: optional.) A generalization of recursion trees by Akra and Bazzi (1998), stated without proof.

> [!key] The Akra–Bazzi theorem
> Let $T(n) = \sum_{i=1}^{k} a_i\,T(n/b_i) + f(n)$ with constants $k$, $a_i > 0$ and $b_i > 1$, base case $T(\Theta(1)) = \Theta(1)$, and $f$ of polynomial growth — for example any $\Theta(n^c\log^j n)$ with $c\ge 0$, constants included. Let $\rho$ be the unique real number with $\sum_i a_i/b_i^{\rho} = 1$ (the left side decreases strictly in $\rho$). Then
> $$
> T(n) = \Theta\Big(n^{\rho}\Big(1 + \int_1^n \frac{f(u)}{u^{\rho+1}}\,du\Big)\Big).
> $$

The note states the growth condition as $f(n) = \Omega(n^c)$ and $O(n^d)$ with $0 < c\le d$ (p. 10), which would exclude $f(n) = 1$ — yet two of its four examples have $f = 1$; constant $f$ is fine. The $a_i$ and $b_i$ need not be integers, and the equation for $\rho$ may have no closed-form solution. With one term, $\rho = \log_b a$ and the formula is the Master Theorem for $a\,T(n/b) + n^c$: $\Theta(n^{\log_b a})$ if $c < \log_b a$, $\Theta(n^c\log n)$ if $c = \log_b a$, $\Theta(n^c)$ if $c > \log_b a$.

| recurrence | $\rho$ | $\int_1^n f(u)\,u^{-\rho-1}\,du$ | $T(n)$ |
|---|---|---|---|
| $T(3n/4) + T(n/4) + n$ | $1$ | $\ln n$ | $\Theta(n\log n)$ |
| $T(n/5) + T(7n/10) + n$ | $\approx 0.83978$ | $\frac{n^{1-\rho} - 1}{1-\rho}$ | $\Theta(n)$ |
| $\tfrac14T(n/4) + \tfrac34T(3n/4) + 1$ | $0$ | $\ln n$ | $\Theta(\log n)$ |
| $T(n/2) + T(n/4) + 1$ | $\lg\phi\approx 0.69424$ | $\frac{1 - n^{-\rho}}{\rho} < \frac1\rho$ | $\Theta(n^{\lg\phi})$ |

Row by row, the exponents solve $(\tfrac34)^\rho + (\tfrac14)^\rho = 1$, $(\tfrac15)^\rho + (\tfrac{7}{10})^\rho = 1$, $\tfrac14(\tfrac14)^\rho + \tfrac34(\tfrac34)^\rho = 1$ and $(\tfrac12)^\rho + (\tfrac14)^\rho = 1$, in that order.

For deterministic selection it is enough to see that $(1/5)^x + (7/10)^x$ decreases from 2 at $x = 0$ to $9/10$ at $x = 1$, so $0 < \rho < 1$ and the integral is $\Theta(n^{1-\rho})$. For ham-sandwich trees, $x = 2^\rho$ solves $1/x + 1/x^2 = 1$, so $x = \phi$. (For the first row the note writes $O(n\log n)$, p. 11; the formula gives $\Theta(n\log n)$.) The method solves almost any divide-and-conquer recurrence in a few lines, but $\sqrt n\,T(\sqrt n) + n$ is outside it (the number of terms is not constant), the steps look like magic, and for most recurrences in practice simpler tools suffice.

## 5 Linear recurrences (annihilators)

(★ in the note: optional.) A **linear recurrence** expresses $f(n)$ as a linear combination of a few nearby values $f(n-1), f(n-2), \ldots$, plus possibly a non-recursive term; they arise from backtracking algorithms and counting problems. Fibonacci is the standard example. Their solutions are always sums of polynomials times exponentials.

> [!warning] Correction — the note's opening example
> The note's example is $T(0) = 1$, $T(1) = T(2) = 0$, $T(n) = 3T(n-1) - 8T(n-2) + 4T(n-3)$, with claimed solution $(n-3)2^n + 4$ (p. 12, repeated on p. 17). The coefficient 3 is a misprint for **5**. As printed, the recurrence gives $T(3), \ldots, T(6) = 4, 12, 4, -68$, while $(n-3)2^n + 4$ gives $4, 20, 68, 196$; its polynomial $x^3 - 3x^2 + 8x - 4$ has one real root $\approx 0.612$ and two complex roots of modulus $\approx 2.557$, not the factorization $(x-2)^2(x-1)$ the note uses. The printed induction check fails too: its brackets $\tfrac32 - \tfrac84 + \tfrac48$, $\tfrac{12}{2} - \tfrac{40}{4} + \tfrac{24}{8}$ and $(2 - 8 + 4)\cdot 4$ evaluate to $0$, $-1$, $-8$. With the corrected recurrence,
> $$
> \begin{aligned}
> &5\big((n-4)2^{n-1} + 4\big) - 8\big((n-5)2^{n-2} + 4\big) + 4\big((n-6)2^{n-3} + 4\big)\\
> &\quad = \big(\tfrac52 - \tfrac84 + \tfrac48\big)\,n2^n - \big(\tfrac{20}{2} - \tfrac{40}{4} + \tfrac{24}{8}\big)\,2^n + (5 - 8 + 4)\cdot 4 = n2^n - 3\cdot 2^n + 4 .
> \end{aligned}
> $$
> Everything below uses $T(n) = 5T(n-1) - 8T(n-2) + 4T(n-3)$.

### 5.1 Operators

**Operators** are functions on functions. Three building blocks suffice: **sum** $(f + g)(n) = f(n) + g(n)$, **scale** $(\alpha f)(n) = \alpha\,f(n)$, and **shift** $(Ef)(n) = f(n+1)$, with $E^k f(n) = f(n+k)$. Shift and scale are **linear**: $E(f - 3(g - h)) = Ef - 3Eg + 3Eh$. Combining them gives **compound operators** such as $E - 2$ (meaning $Ef - 2f$) and $(E-2)^2 = (E-2)(E-2)$. On $f(n) = 2^n$: $Ef = 2^{n+1}$, $E^2 f = 2^{n+2}$, $(E - 2)f = 2^{n+1} - 2\cdot 2^n = 0$, and $(E^2 - 1)f = 2^{n+2} - 2^n = 3\cdot 2^n$.

Compound operators behave exactly like **polynomials in $E$**: they add, multiply (compose), commute and factor. For example, with $g = (E - 2)f$,
$$
\begin{aligned}
(E-1)(E-2)f(n) &= g(n+1) - g(n) = \big(f(n+2) - 2f(n+1)\big) - \big(f(n+1) - 2f(n)\big)\\
&= f(n+2) - 3f(n+1) + 2f(n) = (E^2 - 3E + 2)f(n),
\end{aligned}
$$
and $(E - 2)(E - 1)$ is the same operator. (The note's middle line has $2f(n-1)$ for $2f(n+1)$, p. 13.)

### 5.2 Annihilators

> [!definition] Definition — annihilator
> An operator $X$ **annihilates** $f$ if $Xf$ is the zero function; a nonzero such $X$ is an **annihilator** of $f$. Every sum of polynomials times exponentials, $\sum_i p_i(n)\,a_i^n$ with distinct $a_i$ and nonzero $p_i$, has a unique minimal annihilator up to a constant factor, $\prod_i (E - a_i)^{\deg p_i + 1}$.

Since $(E - c)\,a^n = a^{n+1} - c\,a^n = (a - c)\,a^n$, the operator $E - c$ annihilates $\alpha a^n$ exactly when $c = a$: $E - 2$ annihilates $2^n$ but leaves $3^n$ unchanged, and $E - 3$ annihilates $3^n$ but negates $2^n$. Products annihilate sums: $(E-2)(2^n + 3^n) = 3^n$, so $(E-3)(E-2)(2^n + 3^n) = 0$. For a repeated factor, $(E - a)\big((\alpha n + \beta)a^n\big) = \alpha a^{n+1}$, so $(E-a)^2$ annihilates $(\alpha n + \beta)a^n$. In general:

| operator | annihilates exactly the functions |
|---|---|
| $E - 1$ | $\alpha$ |
| $E - a$ | $\alpha a^n$ |
| $(E - a)(E - b)$, $a\ne b$ | $\alpha a^n + \beta b^n$ |
| $(E - a_0)(E - a_1)\cdots(E - a_k)$, $a_i$ distinct | $\sum_{i=0}^{k}\alpha_i a_i^n$ |
| $(E - 1)^2$ | $\alpha n + \beta$ |
| $(E - a)^2$ | $(\alpha n + \beta)\,a^n$ |
| $(E - a)^2(E - b)$, $a\ne b$ | $(\alpha n + \beta)\,a^n + \gamma\,b^n$ |
| $(E - a)^d$ | $\big(\sum_{i=0}^{d-1}\alpha_i n^i\big)\,a^n$ — a polynomial of degree $< d$ times $a^n$ |

(The note prints the $(E-a)^2(E-b)$ row as $(\alpha n+\beta)a^b + \gamma b^n$, p. 14; the exponent is $n$. The note also says “for any integers $a\ne b$”; any constants work.) The rules for combining them: if $X$ annihilates $f$, it annihilates $Ef$ and $\alpha f$; if $X$ annihilates $f$ and $g$, it annihilates $f\pm g$; if $X$ annihilates $f$ and $Y$ annihilates $g$, then $XY$ annihilates $f\pm g$.

Concept page: [[concepts/linear-recurrences]].

### 5.3 Annihilating recurrences

> [!recipe] The annihilator method
> 1. Write the recurrence in operator form, shifted so that every argument is $n$ or larger.
> 2. Extract an annihilator: the operator on the left, times an annihilator of whatever non-recursive **residue** is left on the right.
> 3. Factor it into operators $E - c$.
> 4. Read the generic solution off the table.
> 5. Solve for the coefficients, using the base cases (a small linear system). Without base cases the generic solution usually still gives the $\Theta$-bound.

**$r(n) = 5r(n-1)$, $r(0) = 3$.** $(E - 5)r = 0$, so $r(n) = \alpha 5^n$, and $r(0) = 3$ gives $r(n) = 3\cdot 5^n$.

**Fibonacci.** $(E^2 - E - 1)F = 0$, and $E^2 - E - 1 = (E - \phi)(E - \hat\phi)$ with $\phi = (1+\sqrt5)/2$ and $\hat\phi = (1-\sqrt5)/2 = 1 - \phi = -1/\phi\approx -0.618034$. So $F(n) = \alpha\phi^n + \hat\alpha\hat\phi^n$; $F(0) = 0$ and $F(1) = 1$ give $\alpha = 1/(2\phi - 1) = 1/\sqrt5 = -\hat\alpha$:
$$
F(n) = \frac{\phi^n - \hat\phi^n}{\sqrt5} = \frac{1}{\sqrt5}\Big(\frac{1+\sqrt5}{2}\Big)^{n} - \frac{1}{\sqrt5}\Big(\frac{1-\sqrt5}{2}\Big)^{n}.
$$
All the square roots cancel for integer $n$ (expand by the binomial theorem). Since $\lvert\hat\phi^n/\sqrt5\rvert < 1/2$, $F(n)$ is $\phi^n/\sqrt5$ rounded to the nearest integer.

**Tower of Hanoi** — the first **non-homogeneous** recurrence (it has a non-recursive term). $(E - 2)T = 1$: $E - 2$ leaves the residue 1, which $E - 1$ annihilates, so $(E-1)(E-2)$ annihilates $T$ and $T(n) = \alpha 2^n + \beta$. From $T(0) = 0$ and $T(1) = 1$: $\alpha = 1$, $\beta = -1$, so $T(n) = 2^n - 1$.

**Height-balanced trees:** $H(n) = H(n-1) + H(n-2) + 1$ with $H(-1) = 0$, $H(0) = 1$ (starting at $-1$ is fine). $(E^2 - E - 1)H = 1$, annihilator $(E-1)(E-\phi)(E-\hat\phi)$, generic solution $\alpha\phi^n + \beta + \gamma\hat\phi^n$; the values $H(-1) = 0$, $H(0) = 1$, $H(1) = 2$ give $\alpha = (\sqrt5 + 2)/\sqrt5$, $\beta = -1$, $\gamma = (\sqrt5 - 2)/\sqrt5$. (In the equation for $H(-1)$ the last term is $+\gamma/\hat\phi$, not $-\gamma/\hat\phi$ as printed on p. 16; the solution is right.) Shorter: $H + 1$ satisfies the Fibonacci recurrence with values $1, 2$ at $-1, 0$, so $H(n) = F(n+3) - 1$ — the same thing, since $\phi^3 = 2 + \sqrt5$.

**The corrected cubic.** $(E^3 - 5E^2 + 8E - 4)T = 0$ and $E^3 - 5E^2 + 8E - 4 = (E - 2)^2(E - 1)$, so $T(n) = \alpha n2^n + \beta 2^n + \gamma$. The base cases give $\beta + \gamma = 1$, $2\alpha + 2\beta + \gamma = 0$, $8\alpha + 4\beta + \gamma = 0$, hence $\alpha = 1$, $\beta = -3$, $\gamma = 4$: $T(n) = (n-3)2^n + 4$.

**$T(n) = T(n-1) + 2T(n-2) + 2^n - n^2$.** Shifting up, $(E^2 - E - 2)T(n) = E^2(2^n - n^2)$ — the residue must be shifted too. $(E-2)(E-1)^3$ annihilates $2^n - n^2$ and so its shift, and $E^2 - E - 2 = (E-2)(E+1)$, so the annihilator is $(E-2)^2(E-1)^3(E+1)$ and
$$
T(n) = \alpha\,n2^n + \beta\,2^n + \gamma n^2 + \delta n + \varepsilon + \eta\,(-1)^n .
$$
The note fits all six constants to $T(0), \ldots, T(5)$ and says that $\alpha\ne 0$ “for almost every set of base cases”, with a footnote describing the solutions with $\alpha = 0$ (p. 17). In fact **only $\beta$ and $\eta$ depend on the base cases** — two base cases, two free constants. The others are forced by the recurrence: substituting $\alpha n2^n$ into $E^2 - E - 2$ gives $6\alpha\cdot 2^n$, which must equal the residue's $4\cdot 2^n$, so $\alpha = 2/3$; matching the polynomial part the same way gives $\gamma = \tfrac12$, $\delta = \tfrac52$, $\varepsilon = 4$. So
$$
T(n) = \tfrac23\,n2^n + \beta\,2^n + \tfrac12 n^2 + \tfrac52 n + 4 + \eta\,(-1)^n = \Theta(n2^n)
$$
for every choice of $T(0)$ and $T(1)$; no solution has $\alpha = 0$, and the footnote's family $-2^{n-1} - n^2/2 - 5n/2 + \eta(-1)^n$ does not satisfy the recurrence at all.

For a fuller treatment the note points to G. Lueker, “Some techniques for solving recurrences”, *ACM Computing Surveys* 12(4), 1980. The polynomial in $E$ is the **characteristic polynomial** of the recurrence; the usual textbook route — try $T(n) = r^n$ — reaches the same polynomial ([[concepts/linear-recurrences]]).

## 6 Transformations

When a recurrence fits none of these forms, define a new function with a simpler recurrence:
- **domain transformation:** $S(n) = T(f(n))$ for a simple $f$;
- **range transformation:** $S(n) = f(T(n))$;
- **difference transformation:** look at $\Delta T(n) = T(n) - T(n-1)$, or more generally subtract a shifted copy of the recurrence.

**Unsimplified mergesort (domain).** For $T(n) = T(\lceil n/2\rceil) + T(\lfloor n/2\rfloor) + \Theta(n)$ there is no exact solution worth having, and for $n$ not a power of 2 the simplified $2T(n/2) + n$ never reaches its base case. Overestimate twice, $T(n)\le 2T(\lceil n/2\rceil) + n\le 2T(n/2 + 1) + n$, and set $S(n) = T(n + \alpha)$ for a constant $\alpha$ chosen so that $S(n)\le 2S(n/2) + O(n)$: comparing arguments, $n/2 + \alpha = (n + \alpha)/2 + 1$ gives $\alpha = 2$. Then $S(n) = O(n\log n)$ and $T(n) = S(n-2) = O(n\log n)$; the lower bound is symmetric. This is exactly [[2-algorithms/01-recursion#ignoring-floors-and-ceilings|“Ignoring floors and ceilings”]] in §1.7: floors, ceilings and lower-order terms in the argument never matter for such recurrences, so stop worrying about them.

**Ham-sandwich trees (domain, to a linear recurrence).** For $T(n) = T(n/2) + T(n/4) + 1$, the function $t(k) = T(2^k)$ satisfies $t(k) = t(k-1) + t(k-2) + 1$ — the height-balanced-tree recurrence of §5.3. So $t(k) = \Theta(\phi^k)$ and
$$
T(n) = t(\lg n) = \Theta(\phi^{\lg n}) = \Theta(n^{\lg\phi})\approx\Theta(n^{0.69424}),
$$
in a few lines, where the original authors needed a long induction. (With $T(n) = 0$ below size 1, exactly $T(2^k) = F_{k+3} - 1$.) The same trick turns mergesort's $2T(n/2) + n$ into $t(k) = 2t(k-1) + 2^k$, annihilated by $(E-2)^2$: $t(k) = \Theta(k2^k)$, $T(n) = \Theta(n\log n)$. Not every recurrence transforms this way: for $T(n/3) + T(2n/3) + n$ the substitution $t(k) = T((3/2)^k)$ gives $t(k) = t(k-1) + t(k-\lambda) + (3/2)^k$ with the non-integer shift $\lambda = \log_{3/2} 3\approx 2.709511$; its characteristic function $(r^\lambda - r^{\lambda-1} - 1)(r - 3/2)$ has a double root at $r = 3/2$ and no other positive root, which again gives $t(k) = \Theta(k(3/2)^k)$ and $T(n) = \Theta(n\log n)$ — the idea behind Akra–Bazzi (footnote 3; its left side reads $t(n)$ for $t(k)$, p. 19).

**Random binary search trees (range).** For $T(n) = \tfrac14T(n/4) + \tfrac34T(3n/4) + 1$, the function $U(n) = n\,T(n)$ satisfies $U(n) = U(n/4) + U(3n/4) + n$, an ordinary lopsided tree with $U(n) = \Theta(n\log n)$ (§3), so $T(n) = \Theta(\log n)$ — no weighted tree needed.

**Randomized quicksort (difference).** The **full-history** recurrence
$$
T(n) = \frac2n\sum_{k=0}^{n-1} T(k) + n
$$
defines $T(n)$ through *all* earlier values. Convert it to a **limited-history** recurrence: multiply by $n$, write the same equation for $n-1$, and subtract.
$$
\begin{aligned}
nT(n) &= 2\textstyle\sum_{k=0}^{n-1} T(k) + n^2\\
(n-1)T(n-1) &= 2\textstyle\sum_{k=0}^{n-2} T(k) + (n-1)^2\\
nT(n) - (n-1)T(n-1) &= 2T(n-1) + 2n - 1,
\end{aligned}
$$
so $T(n) = \frac{n+1}{n}\,T(n-1) + 2 - \frac1n$.
Now divide by $n + 1$: $t(n) = T(n)/(n+1)$ satisfies $t(n) = t(n-1) + \frac{2}{n+1} - \frac{1}{n(n+1)} = t(n-1) + \Theta(1/n)$, which unrolls to $\Theta(H_n) = \Theta(\log n)$. So $T(n) = (n+1)\,t(n) = \Theta(n\log n)$; with $T(0) = 0$, exactly $T(n) = 2(n+1)H_n - 3n$. The book's backtracking chapter uses the same subtraction for text segmentation and optimal binary search trees ([[2-algorithms/02-backtracking#25-text-segmentation|§2.5]], [[2-algorithms/02-backtracking#28-optimal-binary-search-trees|§2.8]]), reducing $\sum_{i<n} T(i) + \alpha n$ to the Hanoi-like $2T(n-1) + \alpha$, and the optimal-tree sum to $3T(n-1) + \alpha$.

## Choosing a method

Not in the note: a summary of which tool fits which shape, with each example solved as on this page.

| shape | first try | example | answer |
|---|---|---|---|
| $a\,T(n/b) + f(n)$, constant level ratio | recursion tree / Master Theorem | $3T(n/2) + n^2$: ratio $3/4$ | $\Theta(n^2)$ |
| pieces of different sizes, $f(n) = n^d$ | compare $\sum_i\alpha_i^{\,d}$ with 1 | $T(n/2) + T(n/4) + n$: $\tfrac34 < 1$ | $\Theta(n)$ |
| … and the sum exceeds 1 | Akra–Bazzi exponent $\sum_i\alpha_i^{\rho} = 1$ | $T(n/2) + T(n/4) + 1$ | $\Theta(n^{\lg\phi})$ |
| log factor in $f$ (ratio drifts towards 1) | add up the levels | $2T(n/2) + n\lg n$ | $\Theta(n\log^2 n)$ |
| $T(n-1) + f(n)$ | unroll | $T(n-1) + n$ | $\Theta(n^2)$ |
| several $T(n-i)$, constant coefficients | largest characteristic root | $T(n-1) + T(n-2) + 1$ | $\Theta(\phi^n)$ |
| $\sqrt n$ in the argument | substitute $n = 2^m$ | $2T(\sqrt n) + \lg n$: $S(m) = 2S(m/2) + m$ | $\Theta(\log n\log\log n)$ |
| non-constant number of children | level sums | $\sqrt n\,T(\sqrt n) + n$ | $\Theta(n\log\log n)$ |
| full history $\sum_{k<n} T(k)$ | subtract the shifted copy | $\tfrac2n\sum_{k<n} T(k) + n$ | $\Theta(n\log n)$ |
| anything else, or the problem says *prove* | guess and confirm | $\sqrt n\,T(\sqrt n) + n$ again | $\Theta(n\log\log n)$ |

> [!key] The largest-root shortcut
> If $T(n) = c_1T(n-1) + \cdots + c_kT(n-k) + p(n)$ with constants $c_i\ge 0$, $c_1 + \cdots + c_k > 1$, a non-negative polynomial $p$ and positive base cases, then $T(n) = \Theta(r^n)$, where $r > 1$ is the unique positive root of $x^k = c_1x^{k-1} + \cdots + c_k$. Examples: $T(n-1) + T(n-2) + 1$ gives $\phi$; $3T(n-1) + 5$ gives 3; $T(n-1) + 2T(n-2) + n$ gives 2; $T(n-1) + T(n-3) + 1$ gives $r\approx 1.4656$. (If the $c_i$ add up to exactly 1 the root is 1 and growth is polynomial: unroll instead.)

Why: the polynomial $x^k - c_1x^{k-1} - \cdots - c_k$ has one sign change, hence one positive root, and it is negative at $x = 1$, so $r > 1$; induction gives $T(n)\ge a\,r^n$ directly, and $T(n)\le A\,r^n - q(n)$ for a suitable polynomial $q$ absorbs $p$.

## Summary

- A recurrence = base cases + recursive cases; with equations it has exactly one solution. Want a closed form, exact or $\Theta$.
- **Guess and confirm:** guess (unroll, tabulate, analogy), prove by induction with one explicit constant. A proof that works for every constant means the bound is loose; one that forces a condition on the constant means it is likely tight. Strip the $\Theta$s first. $\sqrt n\,T(\sqrt n) + n = \Theta(n\log\log n)$.
- **Recursion trees:** $T(n) = \sum_i a^i f(n/b^i)$; geometric level sums → largest term (root, every level, or the $n^{\log_b a}$ leaves); otherwise add the levels ($n/\lg n$ per node: harmonic, $\Theta(n\log\log n)$). Lopsided trees: complete levels for the lower bound, extend to the deepest leaf for the upper bound; quarter children become weights.
- **Master Theorem** (ratio form): $a\,f(n/b) = \kappa f(n)$, $f(n)$ or $K f(n)$ gives $\Theta(f(n))$, $\Theta(f(n)\log n)$, $\Theta(n^{\log_b a})$.
- **Akra–Bazzi:** $\sum a_i b_i^{-\rho} = 1$, $T(n) = \Theta\big(n^\rho(1 + \int_1^n f(u)u^{-\rho-1}du)\big)$; ham-sandwich trees $\Theta(n^{\lg\phi})$, MomSelect $\Theta(n)$ with $\rho\approx 0.83978$.
- **Annihilators:** $E - a$ kills $a^n$, $(E-a)^d$ kills (polynomial of degree $< d$)$\cdot a^n$; operator form → annihilate the residue too → factor → generic solution → constants. Only as many constants as base cases are free; the residue's are forced. $F(n) = (\phi^n - \hat\phi^n)/\sqrt5$.
- **Transformations:** domain ($t(k) = T(2^k)$, $S(n) = T(n + 2)$ for ceilings), range ($U = nT$), difference (subtract a shifted copy to turn full history into limited history).
- The note ends with 4 exercises (21 recurrences to solve exactly, 19 to solve with recursion trees or Akra–Bazzi, “make up your own” linear recurrences, and one with a sum of $\lg n$ terms; its last part reads “More to come…”).

> [!exam] For CS 374
> The appendix is not assigned reading, but Problem 1 of Midterm 2 (Mon Nov 9) asks for the solutions of recurrences (three in each Fall 2025 version) — $\Theta$-bounds, with no proof unless the problem says *prove* or *justify* — and the final (Fri Dec 11) may do so again. **Worth it under time pressure:** the level ratio of the recursion tree (Master Theorem) for $a\,T(n/b) + f(n)$; $\sum_i\alpha_i^{\,d}$ against 1 for pieces of different sizes; unrolling for $T(n-1) + f(n)$; the substitution $n = 2^m$ (or $2^{2^k}$) for square roots; and for a backtracking-style $T(n-1) + T(n-2) + O(1)$, the largest root of the characteristic polynomial. Write the case you used (“level sums grow by $3/2$: leaves dominate, $\Theta(n^{\lg 3})$”). **Guess and confirm** is the fallback for anything odd and the method when a proof is required; test the guess on $n = 2, 4, 8, 16$ first. **Overkill:** fitting annihilator constants (an exam wants $\Theta$), the Akra–Bazzi integral (only its exponent equation is quick), and domain transformations for floors and ceilings (drop them). Practice: the [[0-toolkit/08-review-algorithms#10-short-answer-drill|short-answer drill]], [[0-toolkit/09-midterm-2-cheat-sheet#2-recurrences|the cheat sheet's recurrence table]] and [[2-algorithms/01-recursion-exercises#exercise-16--nine-recurrences|Exercises 1.6–1.8]].

### Sources for this page
Jeff Erickson, *Solving Recurrences*, Appendix II of the lecture notes for *Algorithms* (PDF header “[Fa’13]”, © 2018, CC BY-NC-SA 4.0, no status line; 22 pp.), summarized in our own words; section numbers are the note's, and the ★ on §4 and §5 is the note's mark for optional material. The exercises (pp. 20–22) are not solved; the last one is unfinished (“(b) More to come…”). Original here: the exact closed forms in the §3 table and for $\sqrt n\,T(\sqrt n) + n$ and the full-history quicksort recurrence, the bounds with $+1$ for the lopsided trees, $H(n) = F(n+3) - 1$ and $T(2^k) = F_{k+3} - 1$, the rounding form of Binet's formula, the guess-and-confirm template and the bogus $O(n)$ proof, the figure, the method table and the largest-root shortcut. **Errors in the note:** p. 12 and p. 17, the linear-recurrence example $3T(n-1) - 8T(n-2) + 4T(n-3)$ and its annihilator $E^3 - 3E^2 + 8E - 4$ → coefficient 5, and the p. 12 induction check's brackets ($\tfrac32 - \tfrac84 + \tfrac48$, $\tfrac{12}2 - \tfrac{40}4 + \tfrac{24}8$, $(2-8+4)\cdot4$ → $\tfrac52 - \ldots$, $\tfrac{20}2 - \ldots$, $(5-8+4)\cdot 4$); p. 13, $2f(n-1)$ → $2f(n+1)$; p. 14, annihilator-table row $(\alpha n+\beta)a^b$ → $(\alpha n+\beta)a^n$; p. 16, $-\gamma/\hat\phi$ → $+\gamma/\hat\phi$ in the equation for $H(-1)$; p. 17, “for almost every set of base cases, $\alpha\ne 0$” → $\alpha = 2/3$ for every set of base cases, footnote 2's $\alpha = 0$ solutions do not exist (its formula is not a solution), and “$E^2(2^n + n^2)$” → $E^2(2^n - n^2)$; p. 8, lower summation limit $j = i$ → $j = 1$ (and p. 9, $\sum_{i=1}^\infty j/2^j$ → $\sum_{j=1}^\infty$); p. 9, the lower bound “overestimate” → underestimate, and the upper bounds $n\log_{4/3} n$, $\log_{4/3} n$ omit the $+n$, $+1$ that the level count gives (an off-by-one in the argument: with $T = 0$ below size 1 the printed bounds are false only for some $n < 2$, such as $n = 1$); p. 10, $a\,f(b/n)$ → $a\,f(n/b)$ (three times) and the Akra–Bazzi hypothesis $0 < c$ → $0\le c$ (as printed it excludes the note's own examples with $f = 1$); p. 19, footnote 3's $t(n)$ → $t(k)$, and in the quicksort derivation $\sum_{k=0} T(j)$ → $\sum_{j=0} T(j)$ (twice); typos “constants $a > 0$” and “the coefficient $a$” → $\alpha$ (p. 3), “conforming” → confirming (p. 4), “modes” → nodes (p. 9), “when $i$ is an integer” → $n$ (p. 16). Not an error: p. 11 writes $O(n\log n)$ for the first Akra–Bazzi example, which is true but weaker than the $\Theta(n\log n)$ the formula gives. **Checked by `tools/checks/n99.py`:** every recurrence on the page computed directly — exact closed forms in exact arithmetic (integers, fractions, and $\mathbb{Q}(\sqrt5)$ for the Fibonacci-type formulas) for every $n$ up to 300–600, or up to $2^{100}$–$2^{200}$ at powers of two; every $\Theta$-claim by ratios $T(n)/g(n)$ whose last four values agree within a stated tolerance (from $10^{-9}$ for exact exponentials to 5% for the slowly converging $n\log n$ and Akra–Bazzi ratios); every level sum; the four lopsided trees computed as trees with $T = 0$ below size 1, against their stated bounds; every guess-and-confirm inductive step; every annihilator-table row and rule on random constants; every fitted solution of §5.3, including 60 random base cases for the $2^n - n^2$ example; the Akra–Bazzi exponents (bisection) and integrals (numerical quadrature), with the predicted growth compared to the computed $T(n)$; every transformation (both sides computed); the method-table examples and the largest-root shortcut on four recurrences; and each error above that changes a value (pp. 9, 12–14, 16, 17), by showing that the printed version fails; misprinted letters and indices are only noted. The Akra–Bazzi theorem itself and the shortcut's proof sketch are not machine-checked.
