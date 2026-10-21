---
title: "HW6 — dynamic programming, worked through"
description: "Homework 6 (CS/ECE 374 A, Fall 2026) explained for someone who has only skimmed the dynamic programming notes: the method and the grading rubric in one page, then days off with a sliding-window rule, maximum flatness of a subsequence, and the two palindrome practice problems — each built up from the question 'what do I need to remember?' to a recurrence, an evaluation order and a running time."
tags: [algorithms, dynamic-programming, homework]
---

*Homework 6 · Erickson, Algorithms, Chapter 3 (Dynamic Programming) · private: homework solutions stay off the public site*

> [!abstract] In one breath
> Dynamic programming is recursion that writes its answers down. You describe, in plain English, a function of a few integer parameters whose value is the answer to a smaller version of the problem; you write a recurrence for it; and you fill an array with its values in an order where every entry you need is already there. The grading rubric gives 3 points for the English description, 4 for the recurrence and 3 for the array, the order and the running time — and **0 points for everything else if the description is missing**. Problem 1 is about choosing *what to remember* (how long ago the last few days off were); Problem 2 is about finding the right *structure* first (cut the array into pieces and keep the most common letter of each); Problem 3 is two classic string recurrences.

## 0. Dynamic programming in one page

### The idea

A recursive algorithm for an optimization problem usually tries every possibility for the *first* (or last) decision and recurses on what is left. Written naively it takes exponential time, because the same smaller problems are solved again and again. But if every recursive call is identified by a few integers — "the suffix starting at day $i$", "the prefix of length $i$", "the interval from $i$ to $j$" — there are only polynomially many different calls. Store each answer in an array the first time it is computed and the exponential blow-up disappears. That is all dynamic programming is; the art is in choosing the parameters.

### The recipe — and what each step is worth

| step | what you write | rubric |
|---|---|---|
| 1. the function | a **named** function with explicit parameters, and **one or two English sentences saying what it returns** in terms of those parameters; then say which call gives the final answer | 3 points (1 for saying which part of the input a subproblem looks at, 2 all-or-nothing for a description that is explicit, self-contained and usable) |
| 2. the recurrence | base cases and recursive cases, in math or as recursive pseudocode | 4 points (1 base, 3 recursive; −1 per minor bug; −1½ for an unproved "greedy" shortcut) |
| 3. memoization | the array the values live in, with its index ranges | 1 point |
| 4. evaluation order | which entries are filled first; for nested loops, which loop is outside | 1 point |
| 5. running time | (number of entries) × (time per entry) | 1 point |

Three rules from the rubric that cost the most points:

> [!trap] What makes a description worth zero
> - **It describes the algorithm, not the function.** "We loop over the days and keep the best score so far" says how you compute; the rubric wants *what the function's value is*: "$\textsf{MaxJoy}(i, p, q)$ is the largest total joy from days $i$ through $n$, given that …".
> - **It refers to the algorithm's state.** "the current index", "the best score so far", "the last character we kept" are not parameters. The value must depend only on the parameters you name (and the fixed input).
> - **It has no name, or a lazy one.** A single letter, `OPT` or `memo` costs a point. Use names like $\textsf{MaxJoy}$, $\textsf{MaxFlat}$, $\textsf{MinPal}$.
>
> Without a usable description, the recurrence and the iterative details earn nothing — even if they are perfect.

> [!tip] How to find the recurrence
> Imagine an optimal solution and ask about **one decision** in it — the first day: is it taken off or not? the last piece: where does it start? Each answer leaves a smaller problem of the *same kind*, which the function solves by definition. The recurrence is the best over all possible answers to that one question. If the smaller problem is not of the same kind, the function needs another parameter: that is the question "what do I need to remember?".

### The solved problem in this format

The handout's shuffle problem is the model. The function is $\textsf{Shuf}(i, j)$ = "True if and only if $C[1..i+j]$ is a shuffle of $A[1..i]$ and $B[1..j]$" — a **pair of prefixes**. The one decision: the last character $C[i+j]$ came either from $A$ (then $A[i] = C[i+j]$ and $C[1..i+j-1]$ must be a shuffle of $A[1..i-1]$ and $B[1..j]$) or from $B$. The array is $\textsf{Shuf}[0..m][0..n]$, each entry looks up and left, so row-major order works, in $O(mn)$ time. Notice the answer reports $O(mn)$, not $O(n^2)$: the rubric deducts for the sloppier bound.

> [!warning] Three typos in the handout's solved problem
> In the pseudocode for (a), the first column should test $A[i] = C[i]$, not $A[i] = B[i]$ (the recurrence above it is right). In (b), the last line of the recurrence should test $B[j] = C[i+j]$, not $B[j] = C[j]$; the pseudocode's first column again tests $A[i] = B[i]$; and it should return $\#\textsf{Shuf}[m,n]$. Don't copy these into your own solutions.

## 1. Days off in a sliding window

### Reading the rule

"At most 2 days off in any 28 consecutive workdays." Write the days you take off in increasing order, $d_1 < d_2 < d_3 < \cdots$. Then

$$
\text{at most 2 days off in every window of 28 days} \iff d_{t+2} - d_t \ge 28 \text{ for every } t.
$$

If $d_{t+2} - d_t \le 27$, the 28 days starting at $d_t$ contain three days off. Conversely, three days off in one window of 28 days are within 27 days of each other, and so are the first and third of any three *consecutive* days off among them. The handout's example fits: after days 2 and 20, day 30 is the first allowed day, since $30 - 2 = 28$; after day 30, the next is $20 + 28 = 48$. In general, with at most $\ell$ days in any $k$ consecutive days, the rule is $d_{t+\ell} - d_t \ge k$.

### What do we need to remember?

Go through the days in order and decide, for each day $i$, take it off or not. Whether day $i$ *may* be taken off depends only on the **second most recent** day off: it must be at least 28 days before day $i$. And after we take day $i$, the old most recent day off becomes the second most recent. So the only things we must remember about the past are **how many days ago the two most recent days off were** — and a day off 28 or more days ago no longer restricts anything, so "28 or more" (or "never") can be one value.

That is the whole design: the subproblem is a **suffix of the days** plus **two small numbers**.

> [!definition] The function for part (a)
> For $1 \le i \le n+1$ and $1 \le p \le 28$, $1 \le q \le 28$, let $\textsf{MaxJoy}(i, p, q)$ be the **maximum total joy from the days off we choose among workdays $i, i+1, \dots, n$**, given that the most recent day off before day $i$ was $p$ days before day $i$ and the second most recent was $q$ days before day $i$ — where the value 28 means "28 or more days before day $i$, or there was no such day off" — and the chosen days, together with those earlier days off, must obey the 2-in-28 rule. (Choosing no days at all gives 0.)
>
> The answer is $\textsf{MaxJoy}(1, 28, 28)$: before day 1 there are no days off.

Write $x^{+} = \min(x + 1, 28)$ for "one day further back, capped at 28". The base case is $\textsf{MaxJoy}(n+1, p, q) = 0$: no days are left. For $i \le n$ we either work day $i$ or take it off, and taking it off is allowed exactly when $q = 28$:

$$
\textsf{MaxJoy}(i, p, q) =
\begin{cases}
\max\{\,\text{work},\ \text{off}\,\} & \text{if } q = 28\\[2pt]
\text{work} & \text{if } q < 28
\end{cases}
\qquad
\begin{aligned}
\text{work} &= \textsf{MaxJoy}(i+1,\ p^{+},\ q^{+})\\
\text{off} &= J[i] + \textsf{MaxJoy}(i+1,\ 1,\ p^{+})
\end{aligned}
$$

In the "take it off" branch, day $i$ becomes the most recent day off (1 day before day $i+1$) and the old most recent one becomes the second most recent ($p^{+}$ days before day $i+1$).

> [!note] Why negative joys need no special treatment
> Working a day is always allowed, so a day with negative joy is simply never worth taking off — the $\max$ takes care of it. Zero-joy days are harmless either way. The answer is never negative, because taking no days off is always an option.

**Memoization:** a three-dimensional array $\textsf{MaxJoy}[1..n+1][1..28][1..28]$.
**Evaluation order:** entry $i$ only uses entries $i+1$, so fill $i$ from $n+1$ **down** to 1; for each $i$, the 784 pairs $(p, q)$ in any order.
**Time:** $28 \cdot 28 \cdot (n+1)$ entries, each in $O(1)$ time, so $O(n)$. (Only the 379 pairs with $p < q$ or $p = q = 28$ ever occur, but the bound is the same.)

### Part (b): at most ℓ days in any k consecutive days

Exactly the same idea with longer memory: remember how many days ago the **$\ell$ most recent** days off were, each capped at $k$. Day $i$ may be taken off exactly when the $\ell$-th most recent day off is at least $k$ days back.

> [!definition] The function for part (b)
> For $1 \le i \le n+1$ and $g_1, \dots, g_\ell \in \{1, \dots, k\}$, let $\textsf{MaxJoy}(i, g_1, \dots, g_\ell)$ be the **maximum total joy from the days off we choose among workdays $i, \dots, n$**, given that for each $t$, the $t$-th most recent day off before day $i$ was $g_t$ days before day $i$ — where $k$ means "$k$ or more days before day $i$, or no such day off" — and the chosen days, together with those earlier days off, must obey the $\ell$-in-$k$ rule.
>
> The answer is $\textsf{MaxJoy}(1, k, k, \dots, k)$.

With $x^{+} = \min(x+1, k)$: the base case is $\textsf{MaxJoy}(n+1, g_1, \dots, g_\ell) = 0$, and for $i \le n$

$$
\textsf{MaxJoy}(i, g_1, \dots, g_\ell) =
\begin{cases}
\max\{\,\text{work},\ \text{off}\,\} & \text{if } g_\ell = k\\[2pt]
\text{work} & \text{if } g_\ell < k
\end{cases}
$$

$$
\begin{aligned}
\text{work} &= \textsf{MaxJoy}(i+1,\ g_1^{+}, \dots, g_\ell^{+})\\
\text{off} &= J[i] + \textsf{MaxJoy}(i+1,\ 1,\ g_1^{+}, \dots, g_{\ell-1}^{+})
\end{aligned}
$$

Taking day $i$ off pushes every remembered day one place back and drops the oldest, $g_\ell$, which no longer matters.

**Memoization:** an $(\ell+1)$-dimensional array indexed by $i \in [1..n+1]$ and $g_1, \dots, g_\ell \in [1..k]$ — an ordinary multidimensional array, not a hash table (the rubric gives no credit for hash tables).
**Evaluation order:** $i$ from $n+1$ down to 1; for each $i$, the gap tuples in any order.
**Time:** $(n+1)\,k^\ell$ entries; each takes $O(\ell)$ time to form the shifted tuple, so $O(\ell\, n\, k^\ell) = O(n k^\ell)$ because $\ell$ is a constant. Part (a) is $\ell = 2$, $k = 28$, where this is $O(n)$.

> [!example] A small run
> $\ell = 2$, $k = 4$, $J = [5, -1, 3, 4, 2, 6, 1]$. The best total is **15**, reached by taking days $\{1, 4, 6\}$ ($5 + 4 + 6$) or $\{1, 3, 6, 7\}$ ($5 + 3 + 6 + 1$; check the windows $[1..4]$, $[3..6]$, $[4..7]$: two days off each). Taking $\{1, 3, 4\}$ fails: days 1 and 4 are only 3 apart with day 3 between them.

> [!trap] Where Problem 1 loses points
> - **A description that says "the last two days off" without saying *relative to what*.** "Days ago, measured from day $i$" is what makes the value depend only on the parameters.
> - **Forgetting the cap.** Without it, $p$ and $q$ range up to $n$ and the table has $n^3$ entries — still correct, but $O(n^3)$ instead of $O(n)$, which a rubric usually scores as a slower algorithm.
> - **Remembering only a count** ("how many days off in the last 27 days"). That is not enough: when the window slides, you must know *which* day drops out of it.
> - **Running time in the wrong variables.** Part (b) asks for $n$, $\ell$ and $k$; say $O(n k^\ell)$ (or $O(\ell\, n\, k^\ell)$), not $O(n^3)$.

## 2. Maximum flatness of a subsequence

### Find the structure first

A subsequence's flatness is the sum of the squares of its run lengths, and squares reward long runs: $(a+b)^2 > a^2 + b^2$. Two observations:

- **Adding a character can hurt.** In `ABA`, the subsequence `AA` has flatness 4, but `ABA` itself has only 3: the `B` splits the run.
- **Within a stretch of the array, keep every copy of one letter.** If a run of `A`s comes from some stretch of $A[\cdot]$, taking *every* `A` in that stretch can only lengthen the run.

This suggests a cleaner way to see every subsequence: **cut the array into contiguous pieces, and from each piece keep all copies of its most frequent letter.**

> [!key] Lemma (cut into pieces)
> For any array $A[1..n]$, the maximum flatness of a subsequence of $A$ equals the maximum, over all ways of cutting $A$ into contiguous pieces, of $\sum_{\text{pieces } P} \textsf{Most}(P)^2$, where $\textsf{Most}(P)$ is the largest number of copies of a single letter in $P$.

> [!proof]- Proof (click to expand)
> **Every subsequence is matched by some cut.** Let a subsequence have runs $R_1, \dots, R_m$ (in order). Each run's characters sit at increasing positions of $A$, and all of run $R_t$ comes before run $R_{t+1}$. Cut $A$ between the last position of $R_t$ and the first position of $R_{t+1}$, for each $t$ (anywhere in between). Then piece $t$ contains all of run $R_t$, whose characters are all the same letter, so $\lvert R_t\rvert \le \textsf{Most}(\text{piece } t)$. Summing squares, the flatness of the subsequence is at most the cut's sum.
>
> **Every cut is matched by some subsequence.** Given a cut, keep, in each piece, all copies of its most frequent letter. Adjacent pieces may keep the same letter; then their copies merge into one longer run, and since $(a+b)^2 \ge a^2+b^2$, the flatness of this subsequence is at least the cut's sum.
>
> So the two maxima are equal. $\blacksquare$

This lemma is the "structure" step: it is not a greedy shortcut, but the rubric deducts for structural claims used without proof, so **write the proof** (both directions, as above).

### The recurrence

The last piece of a cut of $A[1..i]$ is some $A[j+1..i]$, and what remains is a cut of the prefix $A[1..j]$. So the subproblems are **prefixes**:

> [!definition] The function
> For $0 \le i \le n$, let $\textsf{MaxFlat}(i)$ be the **maximum flatness of any subsequence of the prefix $A[1..i]$**. The answer is $\textsf{MaxFlat}(n)$.

By the lemma (applied to the prefix), with $\textsf{Most}(j+1, i)$ = the largest number of copies of one letter in $A[j+1..i]$:

$$
\textsf{MaxFlat}(i) =
\begin{cases}
0 & \text{if } i = 0\\[4pt]
\displaystyle\max_{0 \le j < i}\ \Big(\textsf{MaxFlat}(j) + \textsf{Most}(j+1, i)^2\Big) & \text{if } i \ge 1
\end{cases}
$$

**Memoization:** a one-dimensional array $\textsf{MaxFlat}[0..n]$.
**Evaluation order:** $i$ from 0 up to $n$. For each $i$, run $j$ from $i-1$ **down** to 0, so the piece $A[j+1..i]$ grows one character at a time; keep a count for each letter of $\Sigma$ and the largest count so far, so each $\textsf{Most}(j+1,i)$ costs $O(1)$.
**Time:** $O(n)$ values of $j$ for each of $n$ values of $i$, plus $O(\lvert\Sigma\rvert)$ to reset the counts for each $i$: $O(n^2)$, since the alphabet is fixed.

> [!example] The handout's example
> $A = $ `ABALCCLDLGOODAO`. The table is
>
> | $i$ | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
> |---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
> | $\textsf{MaxFlat}(i)$ | 0 | 1 | 2 | 4 | 5 | 6 | 9 | 10 | 11 | 13 | 14 | 15 | 18 | 19 | 20 | **23** |
>
> One optimal cut is `ABA` · `L` · `CC` · `LDL` · `G` · `OODAO`, worth $2^2 + 1^2 + 2^2 + 2^2 + 1^2 + 3^2 = 23$, from the subsequence `AA L CC LL G OOO` (runs 2, 1, 2, 2, 1, 3). The handout's `AALLLGOOO` (runs 2, 3, 1, 3) is another one with 23.

> [!trap] Where Problem 2 loses points
> - **A state that remembers "the last character kept" without making it a parameter.** If you go the direct way — process $A$ left to right, remembering the last kept letter and the current run length — both must be parameters, for example $\textsf{MaxFlat}(i, c, r)$ over suffixes; that works too, but it is bigger and easy to get wrong.
> - **Assuming you should keep as many characters as possible.** `ABA` shows it is false.
> - **Using the lemma without proof.** It is exactly the kind of structural claim the rubric's −1½ is about.

## 3. Palindrome decompositions (practice only)

Both parts use one helper table.

> [!definition] Helper
> For $1 \le i \le n+1$ and $i - 1 \le j \le n$, let $\textsf{IsPal}(i, j)$ be True if and only if the substring $A[i..j]$ is a palindrome (the empty substring, $j = i - 1$, counts as one):
> $$
> \textsf{IsPal}(i, j) = \begin{cases} \text{True} & \text{if } j \le i\\ \big(A[i] = A[j]\big) \wedge \textsf{IsPal}(i+1, j-1) & \text{otherwise} \end{cases}
> $$
> A two-dimensional array, filled with $i$ decreasing (outer loop) and $j$ increasing (inner loop), in $O(n^2)$ time.

### (a) Fewest palindromes

The last piece of a decomposition of $A[1..i]$ is some palindrome $A[j+1..i]$; the rest is a decomposition of the prefix $A[1..j]$.

> [!definition] The function
> For $0 \le i \le n$, let $\textsf{MinPal}(i)$ be the **smallest number of palindromes into which the prefix $A[1..i]$ can be decomposed**. The answer is $\textsf{MinPal}(n)$.
> $$
> \textsf{MinPal}(i) = \begin{cases} 0 & \text{if } i = 0\\ 1 + \min\big\{\textsf{MinPal}(j) \;\big\vert\; 0 \le j < i \text{ and } \textsf{IsPal}(j+1, i)\big\} & \text{if } i \ge 1 \end{cases}
> $$
> The set is never empty, because a single character ($j = i-1$) is a palindrome.

A one-dimensional array $\textsf{MinPal}[0..n]$, filled with $i$ increasing; $O(n)$ per entry, so $O(n^2)$ time including the helper table. On `BUBBASEESABANANA` it returns 3 (`BUB` · `BASEESAB` · `ANANA`).

### (b) Fewest palindromes in a metapalindrome

**The key observation.** If a metapalindrome has at least two pieces, its first and last pieces have the **same length** $L$ (the length sequence is a palindrome), and the pieces in between form a metapalindrome of what is left in the middle. Because the same length comes off both ends, what is left is always **centered**: after removing pieces of total length $s$ from each end, the middle is $A[s+1 .. n-s]$. So a single index describes every subproblem.

> [!definition] The function
> For $1 \le i \le \lfloor n/2\rfloor + 1$, let $\textsf{MinMeta}(i)$ be the **smallest number of palindromes in a metapalindrome of the centered substring $A[i .. n+1-i]$** (empty when $i > n+1-i$). The answer is $\textsf{MinMeta}(1)$.

With $j = n+1-i$ (the right end of the middle): if $i > j$, the middle is empty and $\textsf{MinMeta}(i) = 0$. Otherwise $\textsf{MinMeta}(i)$ is the smallest of

- $1$, if $\textsf{IsPal}(i, j)$ — the whole middle is one palindrome;
- $2 + \textsf{MinMeta}(i + L)$, for each $L \ge 1$ with $i + 2L - 1 \le j$ such that $\textsf{IsPal}(i, i+L-1)$ and $\textsf{IsPal}(j-L+1, j)$ — a palindrome of length $L$ at each end.

The second kind of option always exists when the middle has two or more characters ($L = 1$ works), and a single character is a palindrome, so the minimum is always finite.

A one-dimensional array $\textsf{MinMeta}[1..\lfloor n/2\rfloor + 1]$, filled with $i$ **decreasing** (each entry uses a larger index); $O(n)$ per entry, so $O(n^2)$ time including the helper table. On `BOBSMAMASEESAUKULELE` it returns 7 (`BOB` · `S` · `MAM` · `ASEESA` · `UKU` · `L` · `ELE`, lengths 3, 1, 3, 6, 3, 1, 3).

> [!trap] The tempting wrong turn in (b)
> Using a two-parameter interval $\textsf{MinMeta}(i, j)$ for an arbitrary substring is correct but wasteful ($O(n^2)$ entries, $O(n^3)$ time): only centered substrings ever occur. And computing the best ordinary decomposition first, then checking whether its lengths happen to be a palindrome, is wrong — the best metapalindrome can need more pieces than the best decomposition. For `AAB` the best decomposition is `AA` · `B` (lengths 2, 1 — not a palindrome), while the best metapalindrome is `A` · `A` · `B` (3 pieces).

### Sources for this page

Problem statements, the standard dynamic programming rubric and the solved shuffle problem are from the CS/ECE 374 A Fall 2026 Homework 6 handout; the method follows Erickson, *Algorithms*, Chapter 3. Every recurrence on this page was implemented exactly as written and compared with brute force on thousands of random small inputs: Problem 1 against all subsets of days (also with $\ell = 2$, $k = 28$ for $n$ up to 60, and the window rule against its $d_{t+\ell} - d_t \ge k$ form), Problem 2 against all subsequences, and Problem 3 against all palindrome decompositions; the three example answers (23, 3 and 7) and the small Problem 1 example are reproduced.
