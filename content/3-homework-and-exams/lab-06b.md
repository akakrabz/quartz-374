---
title: "Lab 6b — Karatsuba at work: binary to decimal"
description: "Converting an n-bit binary number to decimal with fast multiplication: 2^n by Piṅgala's repeated squaring, a three-call divide and conquer that pays an extra log factor, the two-call version that costs no more than one multiplication, and an O(n log^2 n) algorithm on top of O(n log n) multiplication — four recursion-tree exercises."
tags: [lab, algorithms, divide-and-conquer, midterm-2]
---

*Lab 6b · October 1 · CS/ECE 374 A, Fall 2026 · [[concepts/divide-and-conquer|divide and conquer]] · uses [[2-algorithms/01-recursion#17-recursion-trees|§1.7]], [[2-algorithms/01-recursion#19-fast-multiplication|§1.9]], [[2-algorithms/01-recursion#110-exponentiation|§1.10]] · rubric: [[0-toolkit/06-how-exams-are-graded#11-recursive-algorithms|how exams are graded §11]] · solutions: explained from the official solutions*

> [!abstract] In one breath
> Given an integer $x$ as $n$ bits, compute its decimal digits. Peeling off one digit at a time ($x \bmod 10$, then $\lfloor x/10\rfloor$) takes $\Theta(n^2)$ time. Divide and conquer does better: write $x = a\cdot 2^{n/2} + b$, convert $a$ and $b$, and evaluate the formula in **decimal** arithmetic, multiplying with Karatsuba's algorithm ([[2-algorithms/01-recursion#19-fast-multiplication|§1.9]]) in $\Theta(L^{\lg 3})$ time for $L$-digit numbers. All four problems are recursion-tree questions in which a node's own work is one multiplication of numbers with $\Theta(\text{size})$ digits: halving the size divides that work by $2^{\lg 3} = 3$, so everything depends on the **number of children**. One child (Problem 1, $2^n$ by repeated squaring): $\Theta(n^{\lg 3})$. Three children (Problem 2, converting $2^{n/2}$ recursively like any other number): all levels cost the same, $\Theta(n^{\lg 3}\log n)$. Two children (Problem 3, $2^{n/2}$ by Problem 1): $\Theta(n^{\lg 3})$ — the whole conversion costs about as much as one multiplication. With an $O(n\log n)$ multiplication the same algorithm runs in $O(n\log^2 n)$ (Problem 4), because now two children no longer shrink the level sums.

> [!note] Costs used throughout
> - An $n$-bit number is less than $2^n$, which has exactly $\lfloor n\log_{10} 2\rfloor + 1 \approx 0.301\,n$ decimal digits: every number in this lab has $O(n)$ digits, and $2^n$ has $\Theta(n)$.
> - **DecimalAdd** and **DecimalDouble** make one pass over the digits: $O(L)$ single-digit operations on $L$-digit numbers.
> - **DecimalMultiply** with Karatsuba: $\Theta(L^{\lg 3})$ single-digit operations for two numbers of at most $L$ digits; **DecimalSquare** is the special case of equal factors.
> - The handout's baseline: computing one digit at a time divides an $n$-bit number by 10 about $0.3\,n$ times, at $\Theta(n)$ bit operations per division, for $\Theta(n^2)$ in total.

## Problem 1 — Powers of two in decimal

> [!question] Problem 1
> The Sanskrit prosodist Piṅgala (second century BCE) computed powers of two with the recurrence
> $$
> 2^n = \begin{cases} 1 & \text{if } n = 0,\\ \big(2^{n/2}\big)^2 & \text{if } n > 0 \text{ is even},\\ 2\cdot\big(2^{\lfloor n/2\rfloor}\big)^2 & \text{if } n \text{ is odd}. \end{cases}
> $$
> Use it to compute the decimal representation of $2^n$, storing all numbers as arrays of decimal digits and implementing squaring and doubling in decimal arithmetic, with Karatsuba's algorithm for the multiplications. What is the running time?

> [!hint]- Hint
> The answer has $\Theta(n)$ digits, so the last squaring alone costs $\Theta(n^{\lg 3})$. What do all the earlier squarings cost together?

> [!solution]- Solution
> **The idea.** [[2-algorithms/01-recursion#110-exponentiation|§1.10]] counts multiplications — $\Theta(\log n)$ of them — as if they all cost the same. Here they do not: the squaring at recursion depth $i$ acts on $2^{\lfloor n/2^{i+1}\rfloor}$, a number with about $1/2^i$ as many digits as the top-level one, and Karatsuba makes it cheaper by the factor
> $$
> \Big(\frac{1}{2^i}\Big)^{\lg 3} = \frac{1}{3^i}.
> $$
> The costs form a decreasing geometric series, so the **last squaring dominates**: all the others together cost at most half as much.
>
> **What the recursion computes.** $\textsf{DecimalTwoToThe}(n)$ returns the decimal digits of $2^n$.
> ```text
> DecimalTwoToThe(n):
>   if n = 0
>     return "1"
>   Z ← DecimalTwoToThe(⌊n/2⌋)        ⟨⟨Z = 2^⌊n/2⌋⟩⟩
>   Z ← DecimalSquare(Z)               ⟨⟨Karatsuba⟩⟩
>   if n is odd
>     Z ← DecimalDouble(Z)
>   return Z
> ```
> **Base case** $n = 0$: "1". **Recursive call** on $\lfloor n/2\rfloor$; squaring its result and doubling when $n$ is odd is Piṅgala's recurrence, so the output is $2^n$.
>
> **Time.** $Z$ has $\Theta(n)$ digits, so the squaring costs $O(n^{\lg 3})$ and the doubling $O(n)$:
> $$
> T(n) = T(\lfloor n/2\rfloor) + O(n^{\lg 3}).
> $$
> The recursion tree is a path; the node at depth $i$ costs $O((n/2^i)^{\lg 3}) = O(n^{\lg 3}/3^i)$. Decreasing level sums: the root dominates ([[2-algorithms/01-recursion#17-recursion-trees|§1.7]]), and
> $$
> T(n) = O\Big(n^{\lg 3}\big(1 + \tfrac13 + \tfrac19 + \cdots\big)\Big) = O(n^{\lg 3}).
> $$
> The bound is tight, since the last squaring alone multiplies two $\Theta(n)$-digit numbers. In an exact count of single-digit operations (with §1.9's $\textsf{FastMultiply}$), the last squaring is 67–70% of all the work, as the series predicts: $1/(1 + \frac13 + \frac19 + \cdots) = \frac23$.
>
> **Answer.** $\Theta(n^{\lg 3})$ — the cost of one Karatsuba multiplication of $\Theta(n)$-digit numbers.

## Problem 2 — Three recursive calls

> [!question] Problem 2
> To convert an arbitrary integer $x$, given as an array of $n$ bits, write $x = a\cdot 2^{n/2} + b$, where $a$ is given by the top $n/2$ bits of $x$ and $b$ by the bottom $n/2$ bits. Then convert $x$ to decimal as follows:
> 1. recursively convert $a$ to decimal;
> 2. recursively convert $2^{n/2}$ to decimal;
> 3. recursively convert $b$ to decimal;
> 4. compute $x = a\cdot 2^{n/2} + b$ with decimal multiplication and addition.
>
> With Karatsuba's algorithm for the decimal multiplication, what is the running time? (You may assume that $n$ is a power of 2.)

> [!hint]- Hint
> Three recursive calls on about $n/2$ bits, and $\Theta(n^{\lg 3})$ work outside them. How do the level sums of the recursion tree compare?

> [!solution]- Solution
> **The idea.** Each call does one multiplication of $\Theta(n)$-digit numbers, $\Theta(n^{\lg 3})$, plus an addition, and makes three calls of half the size. Halving the size divides the multiplication's cost by exactly 3, and there are exactly 3 times as many nodes on the next level: the factors cancel and **every level costs the same**. That is the "equal" case of the recursion tree — the answer is the root's cost times the number of levels.
>
> **What the recursion computes.** $\textsf{Decimal}(X[0\,..\,n-1])$ returns the decimal digits of $x = \sum_i X[i]\,2^i$ (bit $X[i]$ has weight $2^i$).
> ```text
> Decimal(X[0 .. n − 1]):
>   if n ≤ 3
>     return the one-digit number X[0] + 2X[1] + 4X[2]      ⟨⟨missing bits are 0⟩⟩
>   m ← ⌈n/2⌉
>   T[0 .. m] ← 0, …, 0, 1                ⟨⟨2^m in binary: m + 1 bits⟩⟩
>   M ← Decimal(T[0 .. m])
>   A ← Decimal(X[m .. n − 1])            ⟨⟨a = ⌊x / 2^m⌋⟩⟩
>   B ← Decimal(X[0 .. m − 1])            ⟨⟨b = x mod 2^m⟩⟩
>   return DecimalAdd(DecimalMultiply(A, M), B)
> ```
> **Base case.** $n \le 3$: $x \le 7$ is a single digit. (The call on $2^m$ uses $m + 1$ bits, which is fewer than $n$ only when $n \ge 4$ — so the base case must cover $n = 2, 3$. The official solution uses brute force below 100 bits.)
>
> **Recursive calls.** On $2^m$, $a$ and $b$, with $m + 1$, $n - m$ and $m$ bits, all fewer than $n$. **Combination.** $x = a\cdot 2^m + b$, evaluated in decimal.
>
> **Time.** $A$, $B$ and $M$ have $O(n)$ digits, and $M$ has $\Theta(n)$, so the multiplication costs $\Theta(n^{\lg 3})$ and the addition $O(n)$. Ignoring the $+1$ and the ceilings ([[2-algorithms/01-recursion#ignoring-floors-and-ceilings|§1.7]]),
> $$
> T(n) = 3\,T(n/2) + O(n^{\lg 3}).
> $$
> Depth $i$ has $3^i$ nodes of size $n/2^i$, each costing $O((n/2^i)^{\lg 3}) = O(n^{\lg 3}/3^i)$, so **every level sums to** $O(n^{\lg 3})$; with $\lg n + 1$ levels,
> $$
> T(n) = O(n^{\lg 3}\log n).
> $$
> This is tight, because every node really does multiply by its $\Theta(\text{size})$-digit power of 2. Counting single-digit operations exactly, the ratio $T(n)/n^{\lg 3}$ grows by a constant (about 1.5) with every doubling of $n$ — the signature of the extra $\log n$.
>
> **Answer.** $\Theta(n^{\lg 3}\log n)$ — a log factor worse than one multiplication.

## Problem 3 — Two recursive calls

> [!question] Problem 3
> Now convert $2^{n/2}$ to decimal with the specialized algorithm for powers of 2 from Problem 1 instead of the recursive call in step 2. What is the running time now (still with Karatsuba multiplication)?

> [!hint]- Hint
> The third recursive call becomes an $O(n^{\lg 3})$ subroutine call — the same cost as the multiplication. How many children does each node have now?

> [!solution]- Solution
> **The idea.** $2^{n/2}$ is not a general number: Problem 1 builds it in $O(n^{\lg 3})$ time, no more than the multiplication that follows anyway. So the work per node stays $\Theta(n^{\lg 3})$, but each node has only **two** children. Halving the size still divides the cost by 3, while the number of nodes only doubles: level sums shrink by the factor $2/3$, and the root dominates.
>
> ```text
> Decimal(X[0 .. n − 1]):
>   if n ≤ 3
>     return the one-digit number X[0] + 2X[1] + 4X[2]
>   m ← ⌈n/2⌉
>   M ← DecimalTwoToThe(m)                ⟨⟨Problem 1, not a recursive call⟩⟩
>   A ← Decimal(X[m .. n − 1])
>   B ← Decimal(X[0 .. m − 1])
>   return DecimalAdd(DecimalMultiply(A, M), B)
> ```
> Same description, base case and combination as in Problem 2; the recursive calls are only on $a$ and $b$.
>
> **Time.** $\textsf{DecimalTwoToThe}(m)$, the multiplication and the addition cost $O(n^{\lg 3})$ together:
> $$
> T(n) = 2\,T(n/2) + O(n^{\lg 3}).
> $$
> Depth $i$ has $2^i$ nodes costing $O(n^{\lg 3}/3^i)$ each, so the level sums are $O((2/3)^i\, n^{\lg 3})$ — decreasing geometrically — and
> $$
> T(n) = O(n^{\lg 3}).
> $$
> Counting single-digit operations, Problem 2's algorithm needs about 1.2 times as many as this one at $n = 32$ bits and about 3 times as many at $n = 65{,}536$ — the gap keeps growing like $\log n$.
>
> **Answer.** $\Theta(n^{\lg 3})$: converting to decimal costs only a constant factor more than a single multiplication.

The three recursion trees side by side:

<!-- fig:lab-06b-trees -->
<figure class="cs-fig"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 468" width="640" height="468" role="img" style="font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-size:13px"><title>three recursion trees: a path, a ternary tree and a binary tree, with level sums n^lg3 shrinking by 3, constant, and shrinking by 2/3</title><defs><marker id="ARR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs><text x="486" y="14" text-anchor="start" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">level sums</text><text x="14" y="40" text-anchor="start" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">Problem 1:  T(n) = T(n/2) + n<tspan dy="-6" style="font-size:10px">lg 3</tspan><tspan dy="6">  (Piṅgala)</tspan></text><text x="486" y="40" text-anchor="start" dominant-baseline="central" fill="var(--hi)" style="font-size:13.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:700;">Θ(n<tspan dy="-6" style="font-size:10px">lg 3</tspan><tspan dy="6">)</tspan></text><line x1="229" y1="79" x2="229" y2="92" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" opacity="0.5"/><line x1="229" y1="110" x2="229" y2="123" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" opacity="0.5"/><rect x="214" y="61" width="30" height="18" rx="4" fill="var(--paper)" stroke="currentColor" stroke-width="1.1"/><text x="229" y="70.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n</text><rect x="211" y="92" width="36" height="18" rx="4" fill="var(--paper)" stroke="currentColor" stroke-width="1.1"/><text x="229" y="101.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n/2</text><rect x="211" y="123" width="36" height="18" rx="4" fill="var(--paper)" stroke="currentColor" stroke-width="1.1"/><text x="229" y="132.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n/4</text><line x1="466" y1="58" x2="466" y2="144" stroke="var(--muted)" stroke-width="1" stroke-linecap="round" stroke-dasharray="3 3"/><text x="486" y="70.5" text-anchor="start" dominant-baseline="central" fill="var(--accent)" style="font-size:13px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n<tspan dy="-6" style="font-size:10px">lg 3</tspan><tspan dy="6"> </tspan></text><text x="486" y="101.5" text-anchor="start" dominant-baseline="central" fill="var(--accent)" style="font-size:13px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n<tspan dy="-6" style="font-size:10px">lg 3</tspan><tspan dy="6">/3</tspan></text><text x="486" y="132.5" text-anchor="start" dominant-baseline="central" fill="var(--accent)" style="font-size:13px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n<tspan dy="-6" style="font-size:10px">lg 3</tspan><tspan dy="6">/9</tspan></text><text x="486" y="156" text-anchor="start" dominant-baseline="central" fill="var(--accent)" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">root dominates</text><text x="14" y="186" text-anchor="start" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">Problem 2:  T(n) = 3T(n/2) + n<tspan dy="-6" style="font-size:10px">lg 3</tspan><tspan dy="6">  (three calls)</tspan></text><text x="486" y="186" text-anchor="start" dominant-baseline="central" fill="var(--hi)" style="font-size:13.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:700;">Θ(n<tspan dy="-6" style="font-size:10px">lg 3</tspan><tspan dy="6"> log n)</tspan></text><line x1="229" y1="225" x2="88.3" y2="238" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" opacity="0.5"/><line x1="229" y1="225" x2="229" y2="238" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" opacity="0.5"/><line x1="229" y1="225" x2="369.7" y2="238" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" opacity="0.5"/><line x1="88.3" y1="256" x2="41.4" y2="269" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" opacity="0.5"/><line x1="88.3" y1="256" x2="88.3" y2="269" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" opacity="0.5"/><line x1="88.3" y1="256" x2="135.2" y2="269" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" opacity="0.5"/><line x1="229" y1="256" x2="182.1" y2="269" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" opacity="0.5"/><line x1="229" y1="256" x2="229" y2="269" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" opacity="0.5"/><line x1="229" y1="256" x2="275.9" y2="269" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" opacity="0.5"/><line x1="369.7" y1="256" x2="322.8" y2="269" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" opacity="0.5"/><line x1="369.7" y1="256" x2="369.7" y2="269" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" opacity="0.5"/><line x1="369.7" y1="256" x2="416.6" y2="269" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" opacity="0.5"/><rect x="214" y="207" width="30" height="18" rx="4" fill="var(--paper)" stroke="currentColor" stroke-width="1.1"/><text x="229" y="216.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n</text><rect x="70.3" y="238" width="36" height="18" rx="4" fill="var(--paper)" stroke="currentColor" stroke-width="1.1"/><text x="88.3" y="247.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n/2</text><rect x="211" y="238" width="36" height="18" rx="4" fill="var(--paper)" stroke="currentColor" stroke-width="1.1"/><text x="229" y="247.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n/2</text><rect x="351.7" y="238" width="36" height="18" rx="4" fill="var(--paper)" stroke="currentColor" stroke-width="1.1"/><text x="369.7" y="247.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n/2</text><rect x="23.4" y="269" width="36" height="18" rx="4" fill="var(--paper)" stroke="currentColor" stroke-width="1.1"/><text x="41.4" y="278.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n/4</text><rect x="70.3" y="269" width="36" height="18" rx="4" fill="var(--paper)" stroke="currentColor" stroke-width="1.1"/><text x="88.3" y="278.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n/4</text><rect x="117.2" y="269" width="36" height="18" rx="4" fill="var(--paper)" stroke="currentColor" stroke-width="1.1"/><text x="135.2" y="278.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n/4</text><rect x="164.1" y="269" width="36" height="18" rx="4" fill="var(--paper)" stroke="currentColor" stroke-width="1.1"/><text x="182.1" y="278.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n/4</text><rect x="211" y="269" width="36" height="18" rx="4" fill="var(--paper)" stroke="currentColor" stroke-width="1.1"/><text x="229" y="278.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n/4</text><rect x="257.9" y="269" width="36" height="18" rx="4" fill="var(--paper)" stroke="currentColor" stroke-width="1.1"/><text x="275.9" y="278.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n/4</text><rect x="304.8" y="269" width="36" height="18" rx="4" fill="var(--paper)" stroke="currentColor" stroke-width="1.1"/><text x="322.8" y="278.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n/4</text><rect x="351.7" y="269" width="36" height="18" rx="4" fill="var(--paper)" stroke="currentColor" stroke-width="1.1"/><text x="369.7" y="278.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n/4</text><rect x="398.6" y="269" width="36" height="18" rx="4" fill="var(--paper)" stroke="currentColor" stroke-width="1.1"/><text x="416.6" y="278.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n/4</text><line x1="466" y1="204" x2="466" y2="290" stroke="var(--muted)" stroke-width="1" stroke-linecap="round" stroke-dasharray="3 3"/><text x="486" y="216.5" text-anchor="start" dominant-baseline="central" fill="var(--accent)" style="font-size:13px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n<tspan dy="-6" style="font-size:10px">lg 3</tspan><tspan dy="6"> </tspan></text><text x="486" y="247.5" text-anchor="start" dominant-baseline="central" fill="var(--accent)" style="font-size:13px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n<tspan dy="-6" style="font-size:10px">lg 3</tspan><tspan dy="6"> </tspan></text><text x="486" y="278.5" text-anchor="start" dominant-baseline="central" fill="var(--accent)" style="font-size:13px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n<tspan dy="-6" style="font-size:10px">lg 3</tspan><tspan dy="6"> </tspan></text><text x="486" y="302" text-anchor="start" dominant-baseline="central" fill="var(--accent)" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">× (lg n + 1) levels</text><text x="14" y="332" text-anchor="start" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">Problem 3:  T(n) = 2T(n/2) + n<tspan dy="-6" style="font-size:10px">lg 3</tspan><tspan dy="6">  (two calls)</tspan></text><text x="486" y="332" text-anchor="start" dominant-baseline="central" fill="var(--hi)" style="font-size:13.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:700;">Θ(n<tspan dy="-6" style="font-size:10px">lg 3</tspan><tspan dy="6">)</tspan></text><line x1="229" y1="371" x2="123.5" y2="384" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" opacity="0.5"/><line x1="229" y1="371" x2="334.5" y2="384" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" opacity="0.5"/><line x1="123.5" y1="402" x2="70.8" y2="415" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" opacity="0.5"/><line x1="123.5" y1="402" x2="176.2" y2="415" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" opacity="0.5"/><line x1="334.5" y1="402" x2="281.8" y2="415" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" opacity="0.5"/><line x1="334.5" y1="402" x2="387.2" y2="415" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" opacity="0.5"/><rect x="214" y="353" width="30" height="18" rx="4" fill="var(--paper)" stroke="currentColor" stroke-width="1.1"/><text x="229" y="362.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n</text><rect x="105.5" y="384" width="36" height="18" rx="4" fill="var(--paper)" stroke="currentColor" stroke-width="1.1"/><text x="123.5" y="393.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n/2</text><rect x="316.5" y="384" width="36" height="18" rx="4" fill="var(--paper)" stroke="currentColor" stroke-width="1.1"/><text x="334.5" y="393.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n/2</text><rect x="52.8" y="415" width="36" height="18" rx="4" fill="var(--paper)" stroke="currentColor" stroke-width="1.1"/><text x="70.8" y="424.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n/4</text><rect x="158.2" y="415" width="36" height="18" rx="4" fill="var(--paper)" stroke="currentColor" stroke-width="1.1"/><text x="176.2" y="424.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n/4</text><rect x="263.8" y="415" width="36" height="18" rx="4" fill="var(--paper)" stroke="currentColor" stroke-width="1.1"/><text x="281.8" y="424.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n/4</text><rect x="369.2" y="415" width="36" height="18" rx="4" fill="var(--paper)" stroke="currentColor" stroke-width="1.1"/><text x="387.2" y="424.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n/4</text><line x1="466" y1="350" x2="466" y2="436" stroke="var(--muted)" stroke-width="1" stroke-linecap="round" stroke-dasharray="3 3"/><text x="486" y="362.5" text-anchor="start" dominant-baseline="central" fill="var(--accent)" style="font-size:13px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n<tspan dy="-6" style="font-size:10px">lg 3</tspan><tspan dy="6"> </tspan></text><text x="486" y="393.5" text-anchor="start" dominant-baseline="central" fill="var(--accent)" style="font-size:13px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">(2/3) n<tspan dy="-6" style="font-size:10px">lg 3</tspan><tspan dy="6"> </tspan></text><text x="486" y="424.5" text-anchor="start" dominant-baseline="central" fill="var(--accent)" style="font-size:13px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">(4/9) n<tspan dy="-6" style="font-size:10px">lg 3</tspan><tspan dy="6"> </tspan></text><text x="486" y="448" text-anchor="start" dominant-baseline="central" fill="var(--accent)" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">root dominates</text></svg><figcaption><strong>Three recursion trees for Lab 6b.</strong> Every node is a call on the size shown (in bits); its own work is one Karatsuba multiplication of numbers with a proportional number of digits, (size)<sup>lg 3</sup>, and halving the size divides that by 2<sup>lg 3</sup> = 3. A path (Problem 1) and two children per node (Problem 3) make the level sums shrink, so the root's multiplication dominates; three children per node (Problem 2: <i>a</i>, 2<sup><i>n</i>/2</sup> and <i>b</i>) exactly cancel the factor 3, so all lg <i>n</i> + 1 levels cost the same.</figcaption></figure>

## Problem 4 — O(n log² n) with faster multiplication (harder)

> [!question] Problem 4
> Two $n$-digit decimal numbers can in fact be multiplied in $O(n\log n)$ time. Describe an algorithm that computes the decimal representation of an arbitrary $n$-bit binary number in $O(n\log^2 n)$ time.

> [!hint]- Hint
> Keep Problem 3's algorithm and swap in the faster multiplication — then redo both recursion trees: with $n\log n$ work per node, halving the size only halves the cost.

> [!solution]- Solution
> **The idea.** Use Problem 3's algorithm (and Problem 1's for the powers of 2) with the $O(n\log n)$ multiplication ([[2-algorithms/01-recursion#19-fast-multiplication|§1.9]] mentions the algorithm of Harvey and van der Hoeven). The algorithm does not change, but the analysis does: Karatsuba's cost dropped by a factor 3 when the size halved, an $n\log n$ cost drops only by about 2. So two children per node no longer make the level sums shrink — they stay about equal, and that costs one more $\log n$ factor.
>
> **Powers of 2.** With $T_2$ the time of $\textsf{DecimalTwoToThe}$,
> $$
> T_2(n) = T_2(n/2) + O(n\log n).
> $$
> The node at depth $i$ costs $O((n/2^i)\log(n/2^i)) \le O((n/2^i)\log n)$ — a decreasing geometric series times $\log n$ — so $T_2(n) = O(n\log n)$.
>
> **The conversion.** With $T_3$ the time of $\textsf{Decimal}$,
> $$
> T_3(n) = 2\,T_3(n/2) + T_2(n/2) + O(n\log n) = 2\,T_3(n/2) + O(n\log n).
> $$
> Depth $i$ has $2^i$ nodes costing $O((n/2^i)\log(n/2^i))$, so level $i$ sums to $O(n(\lg n - i)) \le O(n\log n)$; with $\lg n + 1$ levels, $T_3(n) = O(n\log^2 n)$. (Summing exactly, $2T(n/2) + n\lg n$ gives $\tfrac12\, n\lg n(\lg n + 1)$ at powers of 2 — the last row of the table in [[2-algorithms/01-recursion#17-recursion-trees|§1.7]].)
>
> **An alternative without the separate power computation.** Let every call return both $x$ and $2^n$ in decimal. The calls on the top $n - m$ bits and the bottom $m$ bits return $a, 2^{n-m}$ and $b, 2^m$; then $x = a\cdot 2^m + b$ and $2^n = 2^{n-m}\cdot 2^m$ — two multiplications and one addition per call, the same recurrence $T(n) = 2T(n/2) + O(n\log n) = O(n\log^2 n)$.
>
> **Why not Problem 2's algorithm?** With fast multiplication its recurrence is $T(n) = 3T(n/2) + O(n\log n)$, whose level sums $(3/2)^i\, n\lg(n/2^i)$ *grow*: the leaves dominate and $T(n) = \Theta(n^{\lg 3})$ — no better than Karatsuba. The third recursive call is now the bottleneck.
>
> **Answer.** Problem 3's algorithm with $O(n\log n)$ multiplication runs in $O(n\log^2 n)$ time.

> [!trap] Where the analysis goes wrong
> - **Counting multiplications instead of time.** Repeated squaring uses $\Theta(\log n)$ multiplications, but they are not unit-cost here: each has its own size, and the analysis must add their costs.
> - **Thinking $2^{n/2}$ is free.** In binary it is a 1 followed by zeros; in decimal it has to be computed. Converted recursively like any other number (Problem 2), it adds a third child to every node, and with $n^{\lg 3}$ work per node three children make every level cost the same.
> - **Reusing a recursion-tree verdict after changing the node cost.** Two children with $n^{\lg 3}$ work: the root dominates. Two children with $n\log n$ work: equal levels, an extra $\log n$. Recompute the level sums every time.

### Sources for this page

Lab 6b of CS/ECE 374 A, Fall 2026 (October 1), and its official solutions, explained in our own words; the recursion trees follow the official ones. Ours: the explicit base case $n \le 3$ (and why Problem 2 needs it), the tightness remarks, the "why not Problem 2's algorithm" remark in Problem 4, and the measurements. Everything is checked by `tools/checks/labs_06.py`: Karatsuba ($\textsf{FastMultiply}$ from [[2-algorithms/01-recursion#19-fast-multiplication|§1.9]]), $\textsf{DecimalTwoToThe}$ and both versions of $\textsf{Decimal}$ run on digit arrays with every single-digit operation counted, and their outputs match Python's conversion for $2^n$ with $n \le 400$, for all bit strings up to 12 bits and for random ones up to 300 bits. For larger $n$ the same algorithms run on machine integers and are charged exactly the digit operations of the digit-array version (the two counts agree on every input compared); then the counts for $n$ up to $2^{16}$–$2^{20}$ bits confirm $\Theta(n^{\lg 3})$ for Problems 1 and 3 (the ratio to $n^{\lg 3}$ settles), $\Theta(n^{\lg 3}\log n)$ for Problem 2 (the ratio grows by a constant per doubling), and — charging $L\lceil\lg L\rceil$ per multiplication of $L$-digit numbers as a stand-in for an $O(n\log n)$ algorithm — $O(n\log n)$ for powers of 2, $\Theta(n\log^2 n)$ for both versions in Problem 4 and $\Theta(n^{\lg 3})$ for the three-call algorithm. The $\Theta(n^2)$ cost of digit-by-digit conversion is counted too.
