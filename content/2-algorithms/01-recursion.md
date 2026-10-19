---
title: "Chapter 1 — Recursion"
description: "Reductions and the Recursion Fairy; the Tower of Hanoi; mergesort and quicksort with their correctness proofs and recurrences; the divide-and-conquer pattern; recursion trees and their three cases; linear-time selection with the median-of-medians pivot; Karatsuba multiplication; exponentiation by repeated squaring."
tags: [chapter, algorithms, recursion, midterm-2]
chapter: 1
---

*Algorithms, Chapter 1 · book pp. 21–70 · [chapter PDF](https://jeffe.cs.illinois.edu/teaching/algorithms/book/01-recursion.pdf) · next: [[2-algorithms/02-backtracking|Chapter 2]] · exercises: [[2-algorithms/01-recursion-exercises|solved exercises]]*

> [!abstract] In one breath
> A **reduction** solves a problem by calling an algorithm for another problem as a black box; **recursion** is a reduction to *smaller instances of the same problem*, with the smallest instances solved directly. The Recursion Fairy who solves the smaller instances is the induction hypothesis, so a recursive algorithm is proved correct by induction — and never by unrolling it. **Divide and conquer** splits an instance into independent smaller instances, solves them recursively and combines the answers: mergesort and quicksort, selection, Karatsuba multiplication, repeated squaring. Running times come from recurrences, and **recursion trees** solve almost all of them: add the work level by level and see whether the level sums shrink (the root dominates), stay equal (multiply by the depth) or grow (the leaves dominate). Headline results: mergesort runs in $\Theta(n\log n)$, the median-of-medians pivot selects the $k$-th smallest element in $\Theta(n)$ worst-case time, Karatsuba multiplies $n$-digit numbers in $\Theta(n^{\lg 3})$, and $a^n$ takes $O(\log n)$ multiplications.

## 1.1 Reductions

> [!definition] Definition — reduction
> **Reducing** problem $X$ to problem $Y$ means writing an algorithm for $X$ that uses an algorithm for $Y$ as a **black box** (a subroutine). The algorithm for $X$ may assume only that the black box solves $Y$ correctly; its correctness must not depend on *how* $Y$ is solved. Its running time does depend on the black box's running time, but that is a separate question.

Two examples from the book. Peasant multiplication (Chapter 0) reduces multiplying positive integers to three simpler operations — addition, halving ("mediation") and parity testing — so it is correct for *any* representation of integers that supports them, and it gets faster just by switching to a representation where those operations are faster (place-value digits instead of tally marks). The Huntington–Hill apportionment algorithm reduces to a priority queue with Insert and ExtractMax; any priority-queue data structure plugs in, and its designer never needs to know about Congress.

The habit to build: even when you know how a component works, reason as if you don't. The black box is somebody else's problem.

> [!note] The same word in Part 1
> Undecidability proofs also used reductions ([[1-models-of-computation/07-undecidability#79-the-halting-problem-via-reduction|§7.9]]), with a *hypothetical* decider as the black box. Here the black box is a real algorithm and the reduction is the algorithm we want. The direction rule is the same: an algorithm for $X$ that calls $Y$ shows that $X$ is no harder than $Y$.

## 1.2 Simplify and delegate

> [!definition] Definition — recursion
> **Recursion** is a reduction from a problem to smaller instances of itself:
> - if the instance can be solved directly (a **base case**), solve it directly;
> - otherwise, reduce it to one or more **simpler instances of the same problem**, and build the answer from theirs.
>
> Think of the simpler instances as solved by the **Recursion Fairy**, by methods that are none of your business. The Recursion Fairy's formal name is the **induction hypothesis**.

One technical condition: there must be no infinite sequence of reductions. The standard way to guarantee it is to make every recursive call **strictly smaller** in some nonnegative integer measure — array length, number of disks, the value of an integer — so that every chain of calls reaches a base case, which must then be solved by some other method.

**Example: peasant multiplication.** The identity
$$
x\cdot y = \begin{cases} 0 & \text{if } x = 0,\\ \lfloor x/2\rfloor\cdot(y+y) & \text{if } x \text{ is even},\\ \lfloor x/2\rfloor\cdot(y+y) + y & \text{if } x \text{ is odd}\end{cases}
$$
is already a recursive algorithm:

```text
PeasantMultiply(x, y):
  if x = 0
    return 0
  else
    x′ ← ⌊x/2⌋
    y′ ← y + y
    prod ← PeasantMultiply(x′, y′)      ⟨⟨Recurse!⟩⟩
    if x is odd
      prod ← prod + y
    return prod
```

The recursive instance is simpler because $x' < x$ whenever $x \ge 1$, and a nonnegative integer cannot decrease forever (here the recursion depth is the number of bits of $x$). A senior scribe computes $x'$ and $y'$, hands $x'\cdot y'$ to a junior scribe, and possibly adds $y$; how the junior scribe does it is none of the senior scribe's business.

> [!template] Template — proving a recursive algorithm correct
> Write the proof as a strong induction that mirrors the algorithm: \
> *Let $I$ be an arbitrary instance of size $n$, and assume the algorithm is correct on every instance of size less than $n$.* \
> **Base cases:** for the instances solved directly, check the direct answer. \
> **Recursive case:** every recursive call is on a smaller instance, so by the induction hypothesis it returns the correct answer; show that the way the algorithm *combines* those answers is correct. \
> Nothing else: never trace what the recursive calls do inside.

> [!trap] Don't unroll the recursion
> Following the calls two or three levels down feels like understanding, but it is exactly the work the induction hypothesis does for you — and it is where proofs go wrong. Your only job at each level is to simplify the instance, or to solve it directly when it cannot be simplified.

Concept page: [[concepts/recursion]].

## 1.3 Tower of Hanoi

Move a tower of $n$ disks from peg src to peg dst, one disk at a time, never placing a disk on a smaller one, using the third peg tmp as a spare.

Concentrate on the **largest disk**. It cannot move until the $n-1$ smaller disks are out of the way — all on tmp. Then it moves to dst in one step, and finally the $n-1$ smaller disks move from tmp onto it. Both transfers are $(n-1)$-disk instances of the same puzzle: hand them to the Recursion Fairy. The reduction assumes there *is* a largest disk, so $n = 0$ is the base case, solved by doing nothing.

<!-- fig:a01-hanoi -->
<figure class="cs-fig"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 660 196" width="660" height="196" role="img" style="font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-size:13px"><title>four snapshots of a 4-disk Tower of Hanoi: start, after moving 3 disks to the middle peg, after moving the largest disk, finished</title><defs><marker id="ARR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs><line x1="12" y1="112" x2="154" y2="112" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><line x1="37" y1="46" x2="37" y2="112" stroke="var(--muted)" stroke-width="2.4" stroke-linecap="round"/><text x="37" y="125" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:11.5px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">src</text><line x1="83" y1="46" x2="83" y2="112" stroke="var(--muted)" stroke-width="2.4" stroke-linecap="round"/><text x="83" y="125" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:11.5px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">tmp</text><line x1="129" y1="46" x2="129" y2="112" stroke="var(--muted)" stroke-width="2.4" stroke-linecap="round"/><text x="129" y="125" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:11.5px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">dst</text><rect x="14" y="99" width="46" height="10.5" rx="3" fill="var(--accent)" fill-opacity="0.35" stroke="var(--accent)" stroke-width="1.3"/><rect x="19" y="87" width="36" height="10.5" rx="3" fill="currentColor" fill-opacity="0.1" stroke="currentColor" stroke-width="1.3"/><rect x="23.5" y="75" width="27" height="10.5" rx="3" fill="currentColor" fill-opacity="0.1" stroke="currentColor" stroke-width="1.3"/><rect x="28" y="63" width="18" height="10.5" rx="3" fill="currentColor" fill-opacity="0.1" stroke="currentColor" stroke-width="1.3"/><text x="83" y="150" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">start</text><text x="83" y="168" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">n = 4 disks on src</text><line x1="158" y1="62" x2="172" y2="62" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" marker-end="url(#ARR)"/><line x1="176" y1="112" x2="318" y2="112" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><line x1="201" y1="46" x2="201" y2="112" stroke="var(--muted)" stroke-width="2.4" stroke-linecap="round"/><text x="201" y="125" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:11.5px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">src</text><line x1="247" y1="46" x2="247" y2="112" stroke="var(--muted)" stroke-width="2.4" stroke-linecap="round"/><text x="247" y="125" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:11.5px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">tmp</text><line x1="293" y1="46" x2="293" y2="112" stroke="var(--muted)" stroke-width="2.4" stroke-linecap="round"/><text x="293" y="125" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:11.5px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">dst</text><rect x="178" y="99" width="46" height="10.5" rx="3" fill="var(--accent)" fill-opacity="0.35" stroke="var(--accent)" stroke-width="1.3"/><rect x="229" y="99" width="36" height="10.5" rx="3" fill="currentColor" fill-opacity="0.1" stroke="currentColor" stroke-width="1.3"/><rect x="233.5" y="87" width="27" height="10.5" rx="3" fill="currentColor" fill-opacity="0.1" stroke="currentColor" stroke-width="1.3"/><rect x="238" y="75" width="18" height="10.5" rx="3" fill="currentColor" fill-opacity="0.1" stroke="currentColor" stroke-width="1.3"/><text x="247" y="150" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">Hanoi(n−1, src, tmp, dst)</text><text x="247" y="168" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">recursion: 7 moves</text><line x1="322" y1="62" x2="336" y2="62" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" marker-end="url(#ARR)"/><circle cx="186" cy="22" r="9" fill="var(--paper)" stroke="var(--hi)" stroke-width="1.3"/><text x="186" y="22.5" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:11.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:700;">1</text><line x1="340" y1="112" x2="482" y2="112" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><line x1="365" y1="46" x2="365" y2="112" stroke="var(--muted)" stroke-width="2.4" stroke-linecap="round"/><text x="365" y="125" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:11.5px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">src</text><line x1="411" y1="46" x2="411" y2="112" stroke="var(--muted)" stroke-width="2.4" stroke-linecap="round"/><text x="411" y="125" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:11.5px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">tmp</text><line x1="457" y1="46" x2="457" y2="112" stroke="var(--muted)" stroke-width="2.4" stroke-linecap="round"/><text x="457" y="125" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:11.5px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">dst</text><rect x="393" y="99" width="36" height="10.5" rx="3" fill="currentColor" fill-opacity="0.1" stroke="currentColor" stroke-width="1.3"/><rect x="397.5" y="87" width="27" height="10.5" rx="3" fill="currentColor" fill-opacity="0.1" stroke="currentColor" stroke-width="1.3"/><rect x="402" y="75" width="18" height="10.5" rx="3" fill="currentColor" fill-opacity="0.1" stroke="currentColor" stroke-width="1.3"/><rect x="434" y="99" width="46" height="10.5" rx="3" fill="var(--accent)" fill-opacity="0.35" stroke="var(--accent)" stroke-width="1.3"/><text x="411" y="150" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">move disk n: src → dst</text><text x="411" y="168" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">1 move</text><line x1="486" y1="62" x2="500" y2="62" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" marker-end="url(#ARR)"/><circle cx="350" cy="22" r="9" fill="var(--paper)" stroke="var(--hi)" stroke-width="1.3"/><text x="350" y="22.5" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:11.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:700;">2</text><line x1="504" y1="112" x2="646" y2="112" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><line x1="529" y1="46" x2="529" y2="112" stroke="var(--muted)" stroke-width="2.4" stroke-linecap="round"/><text x="529" y="125" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:11.5px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">src</text><line x1="575" y1="46" x2="575" y2="112" stroke="var(--muted)" stroke-width="2.4" stroke-linecap="round"/><text x="575" y="125" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:11.5px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">tmp</text><line x1="621" y1="46" x2="621" y2="112" stroke="var(--muted)" stroke-width="2.4" stroke-linecap="round"/><text x="621" y="125" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:11.5px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">dst</text><rect x="598" y="99" width="46" height="10.5" rx="3" fill="var(--accent)" fill-opacity="0.35" stroke="var(--accent)" stroke-width="1.3"/><rect x="603" y="87" width="36" height="10.5" rx="3" fill="currentColor" fill-opacity="0.1" stroke="currentColor" stroke-width="1.3"/><rect x="607.5" y="75" width="27" height="10.5" rx="3" fill="currentColor" fill-opacity="0.1" stroke="currentColor" stroke-width="1.3"/><rect x="612" y="63" width="18" height="10.5" rx="3" fill="currentColor" fill-opacity="0.1" stroke="currentColor" stroke-width="1.3"/><text x="575" y="150" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">Hanoi(n−1, tmp, dst, src)</text><text x="575" y="168" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">recursion: 7 moves</text><circle cx="514" cy="22" r="9" fill="var(--paper)" stroke="var(--hi)" stroke-width="1.3"/><text x="514" y="22.5" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:11.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:700;">3</text><text x="330" y="184" text-anchor="middle" dominant-baseline="central" fill="var(--accent)" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">n = 4:  7 + 1 + 7 = 15 = 2⁴ − 1 moves</text></svg><figcaption><strong>The Tower of Hanoi recursion.</strong> To move <i>n</i> disks from src to dst: (1) recursively move the <i>n</i> − 1 smaller disks out of the way to tmp, (2) move the largest disk (shaded) to dst, (3) recursively move the <i>n</i> − 1 smaller disks from tmp onto it. Only the largest disk matters at this level; the Recursion Fairy handles the rest. Moves: <i>T</i>(<i>n</i>) = 2<i>T</i>(<i>n</i> − 1) + 1 = 2<sup><i>n</i></sup> − 1.</figcaption></figure>

```text
Hanoi(n, src, dst, tmp):
  if n > 0
    Hanoi(n − 1, src, tmp, dst)     ⟨⟨Recurse!⟩⟩
    move disk n from src to dst
    Hanoi(n − 1, tmp, dst, src)     ⟨⟨Recurse!⟩⟩
```

> [!key] Tower of Hanoi
> $\textsf{Hanoi}(n, \textit{src}, \textit{dst}, \textit{tmp})$ solves the puzzle with exactly $T(n) = 2^n - 1$ moves, the solution of
> $$
> T(0) = 0, \qquad T(n) = 2T(n-1) + 1 \quad (n\ge 1).
> $$
> For the legendary 64 disks that is $2^{64}-1 = 18{,}446{,}744{,}073{,}709{,}551{,}615$ moves — about 585 billion years at one move per second.

> [!proof]- Proof (click to expand) — correctness, move count, and why no solution is shorter
> **Correctness.** The claim that survives the induction is slightly stronger than "it solves the puzzle": *if disks $1,\dots,n$ are the top $n$ disks on src and every other disk on every peg is larger than disk $n$, then $\textsf{Hanoi}(n,\textit{src},\textit{dst},\textit{tmp})$ moves disks $1,\dots,n$ to dst by legal moves without touching any other disk.* For $n=0$ there is nothing to move. For $n\ge1$, the first call satisfies the hypothesis (disks $1..n-1$ are on top of src, everything else is larger than $n-1$) and parks them on tmp; then disk $n$ is alone on top of src, and every disk on dst is larger than $n$, so the move is legal; the second call again satisfies the hypothesis and moves disks $1..n-1$ from tmp onto disk $n$.
>
> **Count.** $T(0)=0$, and for $n\ge1$, $2T(n-1)+1 = 2(2^{n-1}-1)+1 = 2^n-1$.
>
> **Optimality** (not in the book's text). Let $L(n)$ be the fewest moves for $n$ disks. The largest disk must move at least once. Just before its first move, the other $n-1$ disks must all sit on the third peg (neither its source nor its target), which takes at least $L(n-1)$ moves. Just before its last move (onto dst) they must again all sit on the third peg, and afterwards they still have to get onto dst: at least $L(n-1)$ more moves, disjoint from the first ones. So $L(n)\ge 2L(n-1)+1$, and $L(n) \ge 2^n-1$ by induction. $\blacksquare$

It may be tempting to follow how the small disks wander around; don't. The book's correctness argument is exactly the induction above, phrased as "the Recursion Fairy correctly moves the top $n-1$ disks".

## 1.4 Mergesort

1. **Divide** the array into two halves.
2. **Recursively** mergesort each half.
3. **Merge** the two sorted halves into one sorted array.

```text
Input:          S O R T I N G E X A M P L
Divide:         S O R T I N | G E X A M P L
Recurse left:   I N O R S T | G E X A M P L
Recurse right:  I N O R S T | A E G L M P X
Merge:          A E G I L M N O P R S T X
```

Dividing is trivial and the recursion is delegated; all the real work is in Merge, which repeatedly copies the smaller of the two front elements into a buffer $B$:

```text
MergeSort(A[1 .. n]):
  if n > 1
    m ← ⌊n/2⌋
    MergeSort(A[1 .. m])           ⟨⟨Recurse!⟩⟩
    MergeSort(A[m + 1 .. n])       ⟨⟨Recurse!⟩⟩
    Merge(A[1 .. n], m)

Merge(A[1 .. n], m):
  i ← 1; j ← m + 1
  for k ← 1 to n
    if j > n
      B[k] ← A[i]; i ← i + 1
    else if i > m
      B[k] ← A[j]; j ← j + 1
    else if A[i] < A[j]
      B[k] ← A[i]; i ← i + 1
    else
      B[k] ← A[j]; j ← j + 1
  for k ← 1 to n
    A[k] ← B[k]
```

### Correctness of mergesort

Two inductions: one for the subroutine, one for the algorithm.

> [!key] Lemma 1.1
> If the subarrays $A[1..m]$ and $A[m+1..n]$ are sorted, then $\textsf{Merge}(A[1..n], m)$ correctly merges them: afterwards $A[1..n]$ is sorted.

> [!proof]- Proof (click to expand)
> Induct on $n-k+1$, the number of elements still to be merged. Claim: when iteration $k$ starts with indices $i$ and $j$, the remaining iterations fill $B[k..n]$ with the elements of $A[i..m]\cup A[j..n]$ in sorted order. If $k>n$, both subarrays are empty and there is nothing to do (base case). Otherwise iteration $k$ puts the smallest element of $A[i..m]\cup A[j..n]$ into $B[k]$, in each of the four cases:
> - $j>n$: $A[j..n]$ is empty, so the smallest element is $A[i]$;
> - $i>m$: $A[i..m]$ is empty, so it is $A[j]$;
> - otherwise, if $A[i] < A[j]$, it is $A[i]$ (both subarrays are sorted, so their minima are their first elements);
> - otherwise $A[i]\ge A[j]$, and it is $A[j]$.
>
> The iteration then advances $i$ or $j$ past the element it copied, and by the induction hypothesis the last $n-k$ iterations merge what remains into $B[k+1..n]$. Starting from $k=1$, $i=1$, $j=m+1$, the buffer ends up as the sorted merge, and the final loop copies it back. $\blacksquare$

> [!key] Theorem 1.2
> $\textsf{MergeSort}$ correctly sorts any input array $A[1..n]$.

> [!proof]- Proof (click to expand)
> Strong induction on $n$. If $n\le1$, the array is already sorted and the algorithm correctly does nothing. Otherwise $1\le m<n$, so both halves are smaller than $A$; by the induction hypothesis the two recursive calls sort $A[1..m]$ and $A[m+1..n]$, and then Lemma 1.1 says Merge combines them into a sorted array. $\blacksquare$

### Analysis of mergesort

Merge is a single loop with constant work per iteration — $O(n)$ time, at most $n-1$ comparisons. So
$$
T(n) = T(\lceil n/2\rceil) + T(\lfloor n/2\rfloor) + O(n).
$$
Floors and ceilings can safely be dropped ([[#ignoring-floors-and-ceilings|below]]), leaving $T(n) = 2T(n/2) + O(n)$; every level of its recursion tree costs $n$ ([[#17-recursion-trees|§1.7]]), so
$$
T(n) = \Theta(n\log n).
$$
With exactly $n$ units of work per call and $T(1) = 0$, the recurrence gives $T(2^k) = k\,2^k = n\lg n$ on the nose.

> [!trap] Mergesort details that get asked
> - Any split point $1\le m<n$ gives a correct algorithm, but not the same running time: a split into constant fractions (halves, or even $n/3$ and $2n/3$) gives $\Theta(n\log n)$, while $m = 1$ gives $T(n) = T(n-1) + O(n) = \Theta(n^2)$.
> - The book's Merge takes the right-hand element on a tie (the test $A[i] < A[j]$ is strict), so this MergeSort is **not stable**; with $\le$ instead it would be.
> - Merge needs the extra array $B$ of size $n$: this mergesort does not sort in place.

## 1.5 Quicksort

Hoare's quicksort does the hard work *before* recursing, so that combining is trivial:

1. Choose a **pivot** element.
2. **Partition** the array into the elements smaller than the pivot, the pivot, and the elements larger than it.
3. Recursively quicksort the first and last parts.

```text
QuickSort(A[1 .. n]):
  if n > 1
    Choose a pivot element A[p]
    r ← Partition(A, p)
    QuickSort(A[1 .. r − 1])       ⟨⟨Recurse!⟩⟩
    QuickSort(A[r + 1 .. n])       ⟨⟨Recurse!⟩⟩

Partition(A[1 .. n], p):
  swap A[p] ↔ A[n]
  ℓ ← 0                            ⟨⟨#items < pivot⟩⟩
  for i ← 1 to n − 1
    if A[i] < A[n]
      ℓ ← ℓ + 1
      swap A[ℓ] ↔ A[i]
  swap A[n] ↔ A[ℓ + 1]
  return ℓ + 1
```

This Partition (Lomuto's) parks the pivot at the end, sweeps once while $\ell$ counts the elements found to be smaller, and swaps the pivot into position $\ell+1$, which it returns: $r$ is the pivot's **rank**. On the book's example, with pivot `P`:

```text
Input:               S O R T I N G E X A M P L
Partition (r = 9):   O I N G E A M L P R T S X
Recurse left:        A E G I L M N O P R T S X
Recurse right:       A E G I L M N O P R S T X
```

(The book's figure shows the two sides arranged differently; any arrangement is a valid partition, and the one above is the one this Partition produces.)

**Correctness.** Again two inductions. Partition maintains a loop invariant: after each iteration, everything in $A[1..\ell]$ is less than the pivot $A[n]$, and nothing in $A[\ell+1..i]$ is. At the end, the final swap leaves smaller elements, then the pivot at position $r = \ell+1$, then elements that are not smaller. QuickSort is then correct by strong induction on $n$: both recursive calls are on fewer than $n$ elements, so they sort their parts, and a sorted left part, the pivot and a sorted right part form a sorted array.

**Analysis.** Partition is a single loop: $O(n)$ time ($n-1$ comparisons). With a pivot of rank $r$,
$$
T(n) = T(r-1) + T(n-r) + O(n).
$$
- **Median pivot** ($r = \lceil n/2\rceil$): $T(n) = T(\lceil n/2\rceil - 1) + T(\lfloor n/2\rfloor) + O(n) \le 2T(n/2) + O(n)$, so $T(n) = O(n\log n)$ — the mergesort recurrence again. The median can be found in linear time ([[#18-linear-time-selection|§1.8]]), but with such a large constant that the resulting sort is impractical.
- **First or last element** (what most programmers do): $r$ can be anything, so $T(n) = \max_{1\le r\le n}\big(T(r-1) + T(n-r)\big) + O(n)$. In the worst case $r = 1$ or $r = n$ every time — for instance on an already sorted array — and $T(n) = T(n-1) + O(n) = \Theta(n^2)$: exactly $n(n-1)/2$ comparisons.
- **Median of three** (median of the first, middle and last elements): somewhat faster in practice, especially on nearly sorted arrays, but the pivot can still have rank $2$ or $n-1$ at every level, so $T(n)\le T(1) + T(n-2) + O(n) = \Theta(n^2)$ in the worst case.

> [!note] "Average case" and random pivots
> Intuitively the pivot "usually" lands with rank between $n/10$ and $9n/10$, and then $T(n)\le T(n/10) + T(9n/10) + O(n) = O(n\log n)$ (an unbalanced recursion tree, [[#17-recursion-trees|§1.7]]). The usual formalization assumes all $n!$ input orders are equally likely — an unrealistic assumption about real data. What does work: choose the pivot index **uniformly at random**. Then quicksort runs in $O(n\log n)$ time with high probability *for every input*, because the randomness belongs to the algorithm, not to an adversary who has read the code (the analysis is outside the book). The "best case" running time the book pointedly does not consider.

## 1.6 The pattern

Mergesort and quicksort are both instances of **divide and conquer**:

> [!recipe] The divide-and-conquer pattern
> 1. **Divide** the given instance into several *independent* smaller instances of *exactly the same* problem.
> 2. **Delegate** each smaller instance to the Recursion Fairy.
> 3. **Combine** the solutions of the smaller instances into the solution of the given instance.
>
> Below a constant size threshold, stop recursing and solve the instance directly (brute force, constant time). **Correctness** is almost always an induction; the **running time** is a recurrence, usually (not always) solved with a recursion tree.

| algorithm | non-recursive work | recurrence | solution |
|---|---|---|---|
| MergeSort | Merge, $O(n)$ | $T(n) = 2T(n/2) + O(n)$ | $\Theta(n\log n)$ |
| QuickSort | Partition, $O(n)$ | $T(n) = T(r-1) + T(n-r) + O(n)$ | $\Theta(n^2)$ worst case |
| QuickSelect | Partition, $O(n)$ | $T(n) \le \max_{\ell<n} T(\ell) + O(n)$ | $\Theta(n^2)$ worst case |
| MomSelect | block medians and Partition, $O(n)$ | $T(n)\le T(n/5) + T(7n/10) + O(n)$ | $\Theta(n)$ |
| SplitMultiply | split, shift and add, $O(n)$ | $T(n) = 4T(n/2) + O(n)$ | $\Theta(n^2)$ |
| FastMultiply | split, shift and add, $O(n)$ | $T(n) = 3T(n/2) + O(n)$ | $\Theta(n^{\lg 3})$ |
| PiṅgalaPower | 1 or 2 multiplications | $T(n)\le T(n/2) + 2$ | $O(\log n)$ multiplications |

> [!template] Template — writing up a divide-and-conquer algorithm (the recursive-algorithm rubric)
> 1. **What the recursive algorithm computes** — what it *returns*, in terms of its parameters, in a sentence or two. Essential when you solve a more general problem than the one asked (QuickSelect returns the $k$-th smallest element for *any* $k$, not just the median) or need extra assumptions. An explanation of *how* it works does not count here.
> 2. **Base case(s)** and their answers.
> 3. **Divide:** the recursive subproblems, exactly (index ranges, parameters).
> 4. **Conquer:** how the results of the recursive calls give the answer.
> 5. **Time:** the recurrence, and its closed-form solution (e.g. from a recursion tree).

Concept page: [[concepts/divide-and-conquer]].

## 1.7 Recursion trees

> [!definition] Definition — recursion tree
> The **recursion tree** of a recursive algorithm (or of its recurrence) has one node for each recursive subproblem; a node's children are the subproblems it calls, and its **value** is the time spent on that subproblem *excluding* the recursive calls. The total running time is the **sum of all the values** in the tree.

Take an algorithm that does $f(n)$ non-recursive work and makes $r$ recursive calls on instances of size $n/c$: $T(n) = r\,T(n/c) + f(n)$. Its recursion tree is a complete $r$-ary tree in which each node at depth $i$ has value $f(n/c^i)$, and there are $r^i$ of them. The base case doesn't matter asymptotically, so take $T(n) = 1$ for $n\le 1$; then the depth is $L = \log_c n$, the number of leaves is $r^L = r^{\log_c n} = n^{\log_c r}$, and adding level by level,
$$
T(n) = \sum_{i=0}^{L} r^i\, f(n/c^i). \qquad (\Sigma)
$$

> [!key] The three easy cases
> Draw two or three levels of the tree and compute each level's total:
> - **Decreasing** — each level sum is a constant factor *smaller* than the one above (a decreasing geometric series): the **root dominates**, $T(n) = \Theta(f(n))$. The depth is irrelevant; the bound would hold even for an infinite tree.
> - **Equal** — all level sums are equal: $T(n) = \Theta(f(n)\cdot L) = \Theta(f(n)\log n)$.
> - **Increasing** — each level sum is a constant factor *larger* than the one above: the **leaves dominate**, $T(n) = \Theta(n^{\log_c r})$, the number of leaves.
>
> For $f(n) = n^d$ consecutive level sums differ by the factor $r/c^d$: if $r < c^d$, $T(n) = \Theta(n^d)$; if $r = c^d$, $T(n) = \Theta(n^d\log n)$; if $r > c^d$, $T(n) = \Theta(n^{\log_c r})$. (This is the "Master Theorem" of the book's appendix on recurrences; for a recurrence with $\le$, the same reasoning gives the corresponding $O$-bound.)

<!-- fig:a01-three-cases -->
<figure class="cs-fig"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 468" width="640" height="468" role="img" style="font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-size:13px"><title>three recursion trees with three levels each and their level sums: decreasing, equal and increasing</title><defs><marker id="ARR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs><text x="470" y="14" text-anchor="start" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">level sums</text><text x="14" y="40" text-anchor="start" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">Decreasing:  T(n) = T(n/5) + T(7n/10) + n</text><text x="305.1" y="40" text-anchor="start" dominant-baseline="central" fill="var(--muted)" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">  (MomSelect)</text><text x="470" y="40" text-anchor="start" dominant-baseline="central" fill="var(--hi)" style="font-size:13.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:700;">Θ(n)</text><line x1="224" y1="79" x2="121" y2="92" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" opacity="0.5"/><line x1="224" y1="79" x2="327" y2="92" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" opacity="0.5"/><line x1="121" y1="110" x2="69.5" y2="123" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" opacity="0.5"/><line x1="121" y1="110" x2="172.5" y2="123" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" opacity="0.5"/><line x1="327" y1="110" x2="275.5" y2="123" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" opacity="0.5"/><line x1="327" y1="110" x2="378.5" y2="123" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" opacity="0.5"/><rect x="209" y="61" width="30" height="18" rx="4" fill="var(--paper)" stroke="currentColor" stroke-width="1.1"/><text x="224" y="70.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n</text><rect x="97" y="92" width="48" height="18" rx="4" fill="var(--paper)" stroke="currentColor" stroke-width="1.1"/><text x="121" y="101.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n/5</text><rect x="303" y="92" width="48" height="18" rx="4" fill="var(--paper)" stroke="currentColor" stroke-width="1.1"/><text x="327" y="101.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">7n/10</text><rect x="40.5" y="123" width="58" height="18" rx="4" fill="var(--paper)" stroke="currentColor" stroke-width="1.1"/><text x="69.5" y="132.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n/25</text><rect x="143.5" y="123" width="58" height="18" rx="4" fill="var(--paper)" stroke="currentColor" stroke-width="1.1"/><text x="172.5" y="132.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">7n/50</text><rect x="246.5" y="123" width="58" height="18" rx="4" fill="var(--paper)" stroke="currentColor" stroke-width="1.1"/><text x="275.5" y="132.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">7n/50</text><rect x="349.5" y="123" width="58" height="18" rx="4" fill="var(--paper)" stroke="currentColor" stroke-width="1.1"/><text x="378.5" y="132.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">49n/100</text><line x1="452" y1="58" x2="452" y2="144" stroke="var(--muted)" stroke-width="1" stroke-linecap="round" stroke-dasharray="3 3"/><text x="470" y="70.5" text-anchor="start" dominant-baseline="central" fill="var(--accent)" style="font-size:13px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n</text><text x="470" y="101.5" text-anchor="start" dominant-baseline="central" fill="var(--accent)" style="font-size:13px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">9n/10</text><text x="470" y="132.5" text-anchor="start" dominant-baseline="central" fill="var(--accent)" style="font-size:13px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">81n/100</text><text x="470" y="156" text-anchor="start" dominant-baseline="central" fill="var(--accent)" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">root dominates</text><text x="14" y="186" text-anchor="start" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">Equal:  T(n) = 2T(n/2) + n</text><text x="198.6" y="186" text-anchor="start" dominant-baseline="central" fill="var(--muted)" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">  (MergeSort)</text><text x="470" y="186" text-anchor="start" dominant-baseline="central" fill="var(--hi)" style="font-size:13.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:700;">Θ(n log n)</text><line x1="224" y1="225" x2="121" y2="238" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" opacity="0.5"/><line x1="224" y1="225" x2="327" y2="238" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" opacity="0.5"/><line x1="121" y1="256" x2="69.5" y2="269" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" opacity="0.5"/><line x1="121" y1="256" x2="172.5" y2="269" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" opacity="0.5"/><line x1="327" y1="256" x2="275.5" y2="269" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" opacity="0.5"/><line x1="327" y1="256" x2="378.5" y2="269" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" opacity="0.5"/><rect x="209" y="207" width="30" height="18" rx="4" fill="var(--paper)" stroke="currentColor" stroke-width="1.1"/><text x="224" y="216.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n</text><rect x="103" y="238" width="36" height="18" rx="4" fill="var(--paper)" stroke="currentColor" stroke-width="1.1"/><text x="121" y="247.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n/2</text><rect x="309" y="238" width="36" height="18" rx="4" fill="var(--paper)" stroke="currentColor" stroke-width="1.1"/><text x="327" y="247.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n/2</text><rect x="51.5" y="269" width="36" height="18" rx="4" fill="var(--paper)" stroke="currentColor" stroke-width="1.1"/><text x="69.5" y="278.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n/4</text><rect x="154.5" y="269" width="36" height="18" rx="4" fill="var(--paper)" stroke="currentColor" stroke-width="1.1"/><text x="172.5" y="278.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n/4</text><rect x="257.5" y="269" width="36" height="18" rx="4" fill="var(--paper)" stroke="currentColor" stroke-width="1.1"/><text x="275.5" y="278.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n/4</text><rect x="360.5" y="269" width="36" height="18" rx="4" fill="var(--paper)" stroke="currentColor" stroke-width="1.1"/><text x="378.5" y="278.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n/4</text><line x1="452" y1="204" x2="452" y2="290" stroke="var(--muted)" stroke-width="1" stroke-linecap="round" stroke-dasharray="3 3"/><text x="470" y="216.5" text-anchor="start" dominant-baseline="central" fill="var(--accent)" style="font-size:13px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n</text><text x="470" y="247.5" text-anchor="start" dominant-baseline="central" fill="var(--accent)" style="font-size:13px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n</text><text x="470" y="278.5" text-anchor="start" dominant-baseline="central" fill="var(--accent)" style="font-size:13px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n</text><text x="470" y="302" text-anchor="start" dominant-baseline="central" fill="var(--accent)" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">× (lg n + 1) levels</text><text x="14" y="332" text-anchor="start" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">Increasing:  T(n) = 3T(n/2) + n</text><text x="234.1" y="332" text-anchor="start" dominant-baseline="central" fill="var(--muted)" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">  (Karatsuba)</text><text x="470" y="332" text-anchor="start" dominant-baseline="central" fill="var(--hi)" style="font-size:13.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:700;">Θ(n<tspan dy="-6" style="font-size:10.5px">lg 3</tspan><tspan dy="6">)</tspan></text><line x1="224" y1="371" x2="86.7" y2="384" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" opacity="0.5"/><line x1="224" y1="371" x2="224" y2="384" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" opacity="0.5"/><line x1="224" y1="371" x2="361.3" y2="384" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" opacity="0.5"/><line x1="86.7" y1="402" x2="40.9" y2="415" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" opacity="0.5"/><line x1="86.7" y1="402" x2="86.7" y2="415" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" opacity="0.5"/><line x1="86.7" y1="402" x2="132.4" y2="415" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" opacity="0.5"/><line x1="224" y1="402" x2="178.2" y2="415" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" opacity="0.5"/><line x1="224" y1="402" x2="224" y2="415" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" opacity="0.5"/><line x1="224" y1="402" x2="269.8" y2="415" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" opacity="0.5"/><line x1="361.3" y1="402" x2="315.6" y2="415" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" opacity="0.5"/><line x1="361.3" y1="402" x2="361.3" y2="415" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" opacity="0.5"/><line x1="361.3" y1="402" x2="407.1" y2="415" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" opacity="0.5"/><rect x="209" y="353" width="30" height="18" rx="4" fill="var(--paper)" stroke="currentColor" stroke-width="1.1"/><text x="224" y="362.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n</text><rect x="68.7" y="384" width="36" height="18" rx="4" fill="var(--paper)" stroke="currentColor" stroke-width="1.1"/><text x="86.7" y="393.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n/2</text><rect x="206" y="384" width="36" height="18" rx="4" fill="var(--paper)" stroke="currentColor" stroke-width="1.1"/><text x="224" y="393.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n/2</text><rect x="343.3" y="384" width="36" height="18" rx="4" fill="var(--paper)" stroke="currentColor" stroke-width="1.1"/><text x="361.3" y="393.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n/2</text><rect x="22.9" y="415" width="36" height="18" rx="4" fill="var(--paper)" stroke="currentColor" stroke-width="1.1"/><text x="40.9" y="424.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n/4</text><rect x="68.7" y="415" width="36" height="18" rx="4" fill="var(--paper)" stroke="currentColor" stroke-width="1.1"/><text x="86.7" y="424.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n/4</text><rect x="114.4" y="415" width="36" height="18" rx="4" fill="var(--paper)" stroke="currentColor" stroke-width="1.1"/><text x="132.4" y="424.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n/4</text><rect x="160.2" y="415" width="36" height="18" rx="4" fill="var(--paper)" stroke="currentColor" stroke-width="1.1"/><text x="178.2" y="424.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n/4</text><rect x="206" y="415" width="36" height="18" rx="4" fill="var(--paper)" stroke="currentColor" stroke-width="1.1"/><text x="224" y="424.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n/4</text><rect x="251.8" y="415" width="36" height="18" rx="4" fill="var(--paper)" stroke="currentColor" stroke-width="1.1"/><text x="269.8" y="424.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n/4</text><rect x="297.6" y="415" width="36" height="18" rx="4" fill="var(--paper)" stroke="currentColor" stroke-width="1.1"/><text x="315.6" y="424.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n/4</text><rect x="343.3" y="415" width="36" height="18" rx="4" fill="var(--paper)" stroke="currentColor" stroke-width="1.1"/><text x="361.3" y="424.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n/4</text><rect x="389.1" y="415" width="36" height="18" rx="4" fill="var(--paper)" stroke="currentColor" stroke-width="1.1"/><text x="407.1" y="424.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n/4</text><line x1="452" y1="350" x2="452" y2="436" stroke="var(--muted)" stroke-width="1" stroke-linecap="round" stroke-dasharray="3 3"/><text x="470" y="362.5" text-anchor="start" dominant-baseline="central" fill="var(--accent)" style="font-size:13px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">n</text><text x="470" y="393.5" text-anchor="start" dominant-baseline="central" fill="var(--accent)" style="font-size:13px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">3n/2</text><text x="470" y="424.5" text-anchor="start" dominant-baseline="central" fill="var(--accent)" style="font-size:13px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">9n/4</text><text x="470" y="448" text-anchor="start" dominant-baseline="central" fill="var(--accent)" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">leaves dominate</text></svg><figcaption><strong>The three easy cases of a recursion tree.</strong> Each node holds the non-recursive work of one subproblem; the running time is the sum over all nodes, added level by level (right). If the level sums shrink geometrically, the root's term dominates; if they are all equal, multiply by the number of levels; if they grow geometrically, the leaves dominate — and there are <i>n</i><sup>lg 3</sup> of them for Karatsuba. Unbalanced trees (top) need no special treatment.</figcaption></figure>

The method works just as well when the subproblems have **different sizes**, because only the level sums matter:

| recurrence | level-$i$ sum | case | solution |
|---|---|---|---|
| $T(n) = 2T(n/2) + n$ (mergesort) | $n$ | equal, $\lg n$ levels | $\Theta(n\log n)$ |
| $T(n) = 3T(n/2) + n$ (Karatsuba) | $(3/2)^i\,n$ | increasing | $\Theta(n^{\lg 3}) \approx \Theta(n^{1.585})$ |
| $T(n) = 4T(n/2) + n$ (SplitMultiply) | $2^i\,n$ | increasing | $\Theta(n^2)$ |
| $T(n) = 2T(n/2) + n^2$ | $n^2/2^i$ | decreasing | $\Theta(n^2)$ |
| $T(n) = T(n/2) + O(1)$ (repeated squaring) | constant | equal | $\Theta(\log n)$ |
| $T(n) = T(n/5) + T(7n/10) + n$ (MomSelect) | $(9/10)^i\,n$ | decreasing | $\Theta(n)$ |
| $T(n) = T(n/3) + T(2n/3) + n$ | at most $n$ | none (unbalanced) | $\Theta(n\log n)$ |
| $T(n) = T(n-1) + n$ (bad quicksort) | a path: $n, n-1, \dots$ | none | $\Theta(n^2)$ |
| $T(n) = 2T(n/2) + n\lg n$ | $n(\lg n - i)$ | none | $\Theta(n\log^2 n)$ |

**The unbalanced rows.** If quicksort's pivot always landed in the middle third, $T(n)\le T(n/3) + T(2n/3) + O(n)$. Every level of that tree sums to *at most* $n$ (deeper levels are missing nodes), and the depth is $\log_{3/2} n = O(\log n)$, so $T(n) = O(n\log n)$; the first $\log_3 n$ levels are complete, so the bound is tight. The worst-case quicksort recurrence $T(n) = T(n-1) + T(1) + O(n)$ fits none of the three cases (one child of every node is a leaf), but every level is at most $n$ and there are at most $n$ levels: $O(n^2)$, and tight because $n/2$ levels each have value at least $n/2$. For $2T(n/2) + n\lg n$ the level sums shrink by an *additive* amount, so no case applies; summing directly gives $n\lg n(\lg n+1)/2$ at powers of two (with $T(1) = 0$).

### Ignoring floors and ceilings

The true mergesort recurrence is $T(n) = T(\lceil n/2\rceil) + T(\lfloor n/2\rfloor) + O(n)$; an induction with the floors and ceilings in place works but is ugly. A **domain transformation** removes them:

**Step 1.** We want an upper bound, so we may overestimate (treating $T$ as a nondecreasing function on the reals): pretend both halves are the larger one, then drop the ceiling,
$$
T(n) \le 2T(\lceil n/2\rceil) + n \le 2T(n/2 + 1) + n.
$$
**Step 2.** Define $S(n) = T(n + \alpha)$ and choose the constant $\alpha$ to make $S$'s recurrence clean:
$$
S(n) = T(n+\alpha) \le 2T\Big(\frac{n}{2} + \frac{\alpha}{2} + 1\Big) + n + \alpha = 2S\Big(\frac{n}{2} - \frac{\alpha}{2} + 1\Big) + n + \alpha.
$$
With $\alpha = 2$ this is $S(n)\le 2S(n/2) + n + 2$.

**Step 3.** The recursion tree gives $S(n) = O(n\log n)$, so $T(n) = S(n-2) = O((n-2)\log(n-2)) = O(n\log n)$.

The same trick removes floors, ceilings and lower-order terms from any divide-and-conquer recurrence. Having seen it once, the book (and this site) silently drops them from now on.

Concept page: [[concepts/recursion-trees]].

## 1.8 Linear-time selection

**Selection:** given an unsorted array $A[1..n]$ and an integer $k$ with $1\le k\le n$, return the $k$-th smallest element. The median is the case $k \approx n/2$. Sorting solves it in $O(n\log n)$ time; Blum, Floyd, Pratt, Rivest and Tarjan showed how to do it in $O(n)$.

### Quickselect

Hoare's **quickselect** ("one-armed quicksort") partitions around a pivot and then recurses into *only* the side that contains the answer:

```text
QuickSelect(A[1 .. n], k):
  if n = 1
    return A[1]
  else
    Choose a pivot element A[p]
    r ← Partition(A[1 .. n], p)
    if k < r
      return QuickSelect(A[1 .. r − 1], k)
    else if k > r
      return QuickSelect(A[r + 1 .. n], k − r)
    else
      return A[r]
```

Two features matter. Quickselect is **correct for every pivot choice**: after Partition the pivot has rank $r$; if $k<r$ the answer is the $k$-th smallest element of the left part, if $k>r$ it is the $(k-r)$-th smallest of the right part, and if $k = r$ it is the pivot. And the **general problem is necessary**: even if you only want medians, the recursion needs arbitrary $k$, because the median of $A$ is almost never the median of either side.

**Worst case.** We know neither $r$ nor which side we recurse into, so assume the worst; writing $\ell$ for the size of the recursive subproblem,
$$
T(n) \le \max_{1\le r\le n}\max\{T(r-1),\, T(n-r)\} + O(n) = \max_{0\le \ell\le n-1} T(\ell) + O(n).
$$
If the pivot is always the smallest or largest element, $T(n) = T(n-1) + O(n) = \Theta(n^2)$ (the recursion tree is a path).

**Good pivots suffice.** If the pivot always guarantees $\ell\le \alpha n$ for a constant $\alpha<1$, then $T(n)\le T(\alpha n) + O(n)$ — a decreasing geometric series — so $T(n) = O(n)$, with a constant depending on $\alpha$. An element merely *close* to the median, found in linear time, gives the exact median in linear time.

### Good pivots: the median of medians

The **Approximate Median Fairy** is the Recursion Fairy in disguise: compute the median of a well-chosen subset recursively. Split $A$ into $m = \lceil n/5\rceil$ blocks of 5 consecutive elements (pad the last block with $\infty$s), find each block's median by brute force, and recursively take the median of those $m$ medians — **mom** — as the pivot:

```text
MomSelect(A[1 .. n], k):
  if n ≤ 25                                    ⟨⟨or whatever⟩⟩
    use brute force
  else
    m ← ⌈n/5⌉
    for i ← 1 to m
      M[i] ← MedianOfFive(A[5i − 4 .. 5i])      ⟨⟨Brute force!⟩⟩
    mom ← MomSelect(M[1 .. m], ⌊m/2⌋)           ⟨⟨Recursion!⟩⟩
    r ← Partition(A[1 .. n], p)                 ⟨⟨where A[p] = mom⟩⟩
    if k < r
      return MomSelect(A[1 .. r − 1], k)        ⟨⟨Recursion!⟩⟩
    else if k > r
      return MomSelect(A[r + 1 .. n], k − r)    ⟨⟨Recursion!⟩⟩
    else
      return mom
```

MomSelect recurses for two different purposes: once on the $m$ medians, to choose the pivot, and once on one side of the partition, to search.

### Analysis of MomSelect

**First insight: mom is a good pivot.** Mom is the $\lfloor m/2\rfloor$-th smallest block median, so $\lfloor m/2\rfloor - 1 \approx n/10$ other medians are smaller than mom, and each of them is larger than two more elements of its own block; mom is also larger than two elements of its own block. So at least $3\lfloor m/2\rfloor - 1 \approx 3n/10$ elements are smaller than mom, and symmetrically at least about $3n/10$ are larger. Whichever side the second recursive call searches, it has thrown away about $3n/10$ elements: it gets **at most about $7n/10$** of them (precisely, for distinct elements, at most $n - 3\lfloor m/2\rfloor \le 7n/10 + 3/2$).

<!-- fig:a01-mom-grid -->
<figure class="cs-fig"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 232" width="640" height="232" role="img" style="font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-size:13px"><title>5 by 10 grid of the numbers 1 to 50 with mom = 15 in the center row; shaded regions show values certainly smaller and certainly larger than mom</title><defs><marker id="ARR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs><rect x="92" y="34" width="34" height="28" rx="0" fill="var(--accent)" fill-opacity="0.22" stroke="none" stroke-width="0"/><rect x="92" y="34" width="34" height="28" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="109" y="48.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">5</text><rect x="92" y="62" width="34" height="28" rx="0" fill="var(--accent)" fill-opacity="0.22" stroke="none" stroke-width="0"/><rect x="92" y="62" width="34" height="28" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="109" y="76.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">8</text><rect x="92" y="90" width="34" height="28" rx="0" fill="var(--accent)" fill-opacity="0.22" stroke="none" stroke-width="0"/><rect x="92" y="90" width="34" height="28" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="109" y="104.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">10</text><rect x="92" y="118" width="34" height="28" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="109" y="132.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">21</text><rect x="92" y="146" width="34" height="28" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="109" y="160.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">40</text><rect x="126" y="34" width="34" height="28" rx="0" fill="var(--accent)" fill-opacity="0.22" stroke="none" stroke-width="0"/><rect x="126" y="34" width="34" height="28" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="143" y="48.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">1</text><rect x="126" y="62" width="34" height="28" rx="0" fill="var(--accent)" fill-opacity="0.22" stroke="none" stroke-width="0"/><rect x="126" y="62" width="34" height="28" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="143" y="76.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">7</text><rect x="126" y="90" width="34" height="28" rx="0" fill="var(--accent)" fill-opacity="0.22" stroke="none" stroke-width="0"/><rect x="126" y="90" width="34" height="28" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="143" y="104.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">11</text><rect x="126" y="118" width="34" height="28" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="143" y="132.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">30</text><rect x="126" y="146" width="34" height="28" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="143" y="160.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">47</text><rect x="160" y="34" width="34" height="28" rx="0" fill="var(--accent)" fill-opacity="0.22" stroke="none" stroke-width="0"/><rect x="160" y="34" width="34" height="28" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="177" y="48.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">2</text><rect x="160" y="62" width="34" height="28" rx="0" fill="var(--accent)" fill-opacity="0.22" stroke="none" stroke-width="0"/><rect x="160" y="62" width="34" height="28" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="177" y="76.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">9</text><rect x="160" y="90" width="34" height="28" rx="0" fill="var(--accent)" fill-opacity="0.22" stroke="none" stroke-width="0"/><rect x="160" y="90" width="34" height="28" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="177" y="104.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">13</text><rect x="160" y="118" width="34" height="28" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="177" y="132.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">25</text><rect x="160" y="146" width="34" height="28" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="177" y="160.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">26</text><rect x="194" y="34" width="34" height="28" rx="0" fill="var(--accent)" fill-opacity="0.22" stroke="none" stroke-width="0"/><rect x="194" y="34" width="34" height="28" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="211" y="48.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">4</text><rect x="194" y="62" width="34" height="28" rx="0" fill="var(--accent)" fill-opacity="0.22" stroke="none" stroke-width="0"/><rect x="194" y="62" width="34" height="28" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="211" y="76.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">12</text><rect x="194" y="90" width="34" height="28" rx="0" fill="var(--accent)" fill-opacity="0.22" stroke="none" stroke-width="0"/><rect x="194" y="90" width="34" height="28" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="211" y="104.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">14</text><rect x="194" y="118" width="34" height="28" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="211" y="132.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">27</text><rect x="194" y="146" width="34" height="28" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="211" y="160.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">32</text><rect x="228" y="34" width="34" height="28" rx="0" fill="var(--accent)" fill-opacity="0.22" stroke="none" stroke-width="0"/><rect x="228" y="34" width="34" height="28" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="245" y="48.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">3</text><rect x="228" y="62" width="34" height="28" rx="0" fill="var(--accent)" fill-opacity="0.22" stroke="none" stroke-width="0"/><rect x="228" y="62" width="34" height="28" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="245" y="76.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">6</text><rect x="228" y="90" width="34" height="28" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="245" y="104.5" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;font-weight:700;">15</text><rect x="228" y="118" width="34" height="28" rx="0" fill="var(--accent2)" fill-opacity="0.22" stroke="none" stroke-width="0"/><rect x="228" y="118" width="34" height="28" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="245" y="132.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">44</text><rect x="228" y="146" width="34" height="28" rx="0" fill="var(--accent2)" fill-opacity="0.22" stroke="none" stroke-width="0"/><rect x="228" y="146" width="34" height="28" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="245" y="160.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">45</text><rect x="262" y="34" width="34" height="28" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="279" y="48.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">16</text><rect x="262" y="62" width="34" height="28" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="279" y="76.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">22</text><rect x="262" y="90" width="34" height="28" rx="0" fill="var(--accent2)" fill-opacity="0.22" stroke="none" stroke-width="0"/><rect x="262" y="90" width="34" height="28" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="279" y="104.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">24</text><rect x="262" y="118" width="34" height="28" rx="0" fill="var(--accent2)" fill-opacity="0.22" stroke="none" stroke-width="0"/><rect x="262" y="118" width="34" height="28" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="279" y="132.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">46</text><rect x="262" y="146" width="34" height="28" rx="0" fill="var(--accent2)" fill-opacity="0.22" stroke="none" stroke-width="0"/><rect x="262" y="146" width="34" height="28" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="279" y="160.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">48</text><rect x="296" y="34" width="34" height="28" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="313" y="48.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">18</text><rect x="296" y="62" width="34" height="28" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="313" y="76.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">20</text><rect x="296" y="90" width="34" height="28" rx="0" fill="var(--accent2)" fill-opacity="0.22" stroke="none" stroke-width="0"/><rect x="296" y="90" width="34" height="28" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="313" y="104.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">31</text><rect x="296" y="118" width="34" height="28" rx="0" fill="var(--accent2)" fill-opacity="0.22" stroke="none" stroke-width="0"/><rect x="296" y="118" width="34" height="28" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="313" y="132.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">42</text><rect x="296" y="146" width="34" height="28" rx="0" fill="var(--accent2)" fill-opacity="0.22" stroke="none" stroke-width="0"/><rect x="296" y="146" width="34" height="28" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="313" y="160.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">43</text><rect x="330" y="34" width="34" height="28" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="347" y="48.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">17</text><rect x="330" y="62" width="34" height="28" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="347" y="76.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">29</text><rect x="330" y="90" width="34" height="28" rx="0" fill="var(--accent2)" fill-opacity="0.22" stroke="none" stroke-width="0"/><rect x="330" y="90" width="34" height="28" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="347" y="104.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">33</text><rect x="330" y="118" width="34" height="28" rx="0" fill="var(--accent2)" fill-opacity="0.22" stroke="none" stroke-width="0"/><rect x="330" y="118" width="34" height="28" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="347" y="132.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">34</text><rect x="330" y="146" width="34" height="28" rx="0" fill="var(--accent2)" fill-opacity="0.22" stroke="none" stroke-width="0"/><rect x="330" y="146" width="34" height="28" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="347" y="160.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">49</text><rect x="364" y="34" width="34" height="28" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="381" y="48.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">19</text><rect x="364" y="62" width="34" height="28" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="381" y="76.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">23</text><rect x="364" y="90" width="34" height="28" rx="0" fill="var(--accent2)" fill-opacity="0.22" stroke="none" stroke-width="0"/><rect x="364" y="90" width="34" height="28" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="381" y="104.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">36</text><rect x="364" y="118" width="34" height="28" rx="0" fill="var(--accent2)" fill-opacity="0.22" stroke="none" stroke-width="0"/><rect x="364" y="118" width="34" height="28" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="381" y="132.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">38</text><rect x="364" y="146" width="34" height="28" rx="0" fill="var(--accent2)" fill-opacity="0.22" stroke="none" stroke-width="0"/><rect x="364" y="146" width="34" height="28" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="381" y="160.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">41</text><rect x="398" y="34" width="34" height="28" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="415" y="48.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">28</text><rect x="398" y="62" width="34" height="28" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="415" y="76.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">35</text><rect x="398" y="90" width="34" height="28" rx="0" fill="var(--accent2)" fill-opacity="0.22" stroke="none" stroke-width="0"/><rect x="398" y="90" width="34" height="28" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="415" y="104.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">37</text><rect x="398" y="118" width="34" height="28" rx="0" fill="var(--accent2)" fill-opacity="0.22" stroke="none" stroke-width="0"/><rect x="398" y="118" width="34" height="28" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="415" y="132.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">39</text><rect x="398" y="146" width="34" height="28" rx="0" fill="var(--accent2)" fill-opacity="0.22" stroke="none" stroke-width="0"/><rect x="398" y="146" width="34" height="28" rx="0" fill="none" stroke="currentColor" stroke-width="0.8"/><text x="415" y="160.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">50</text><rect x="92" y="90" width="340" height="28" rx="0" fill="none" stroke="currentColor" stroke-width="2.2"/><rect x="229.5" y="91.5" width="31" height="25" rx="0" fill="none" stroke="var(--hi)" stroke-width="2.4"/><text x="82" y="104" text-anchor="end" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">medians</text><line x1="22" y1="38" x2="22" y2="170" stroke="var(--muted)" stroke-width="1.3" stroke-linecap="round" marker-end="url(#ARR)"/><text x="22" y="26" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:11px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">small</text><text x="22" y="184" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:11px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">large</text><text x="262" y="18" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">10 blocks of 5, each drawn sorted; blocks ordered by their medians →</text><text x="245" y="190" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:700;">mom = 15</text><rect x="454" y="42" width="16" height="14" rx="0" fill="var(--accent)" fill-opacity="0.35" stroke="currentColor" stroke-width="0.8"/><text x="478" y="49" text-anchor="start" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">14 values surely &lt; mom</text><rect x="454" y="70" width="16" height="14" rx="0" fill="var(--accent2)" fill-opacity="0.35" stroke="currentColor" stroke-width="0.8"/><text x="478" y="77" text-anchor="start" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">17 values surely &gt; mom</text><text x="454" y="112" text-anchor="start" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">k &gt; 15: recurse on the</text><text x="454" y="129" text-anchor="start" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">35 = 7n/10 values &gt; mom</text><text x="454" y="152" text-anchor="start" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">k &lt; 15: recurse on at most</text><text x="454" y="169" text-anchor="start" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">50 − 17 − 1 = 32 values</text></svg><figcaption><strong>Why the median of medians is a good pivot</strong> (<i>n</i> = 50, <i>m</i> = 10 blocks). Picture each block as a column sorted top to bottom and the columns ordered by their medians — the algorithm never does this sorting. Mom, the 5th smallest median, is above the top-left block of shaded cells and below the bottom-right block, so at least 3⌊<i>m</i>/2⌋ − 1 ≈ 3<i>n</i>/10 values lie on each side. In this input the bound is tight: exactly 14 values are smaller than mom.</figcaption></figure>

**Second insight: the two recursive calls are small *together*.** Their sizes add up to at most $n/5 + 7n/10 = 9n/10 < n$:
$$
T(n) \le T(n/5) + T(7n/10) + O(n).
$$
In the recursion tree each level sums to at most $9/10$ of the level above ($n$, $9n/10$, $81n/100$, …): decreasing, so the root dominates — and that the tree is unbalanced is irrelevant.

> [!key] Linear-time selection (Blum–Floyd–Pratt–Rivest–Tarjan)
> $\textsf{MomSelect}(A[1..n], k)$ returns the $k$-th smallest element of $A$ in $\Theta(n)$ worst-case time, if the elements are distinct (as the analysis assumes; with repeated values use a three-way partition, see the traps below). In particular the median of an unsorted array can be found in linear time, and quicksort with the median as pivot runs in $\Theta(n\log n)$ worst-case time.

### Sanity checking: why blocks of 5

With blocks of odd size $g$, mom beats about $(g+1)/2$ elements in each of about $n/(2g)$ blocks, so about $(g+1)n/(4g)$ elements are discarded and the second call gets about $(3g-1)n/(4g)$:

| block size $g$ | recurrence | level-sum ratio | solution |
|---|---|---|---|
| 3 | $T(n) \le T(n/3) + T(2n/3) + O(n)$ | $1$ | $\Theta(n\log n)$ |
| 5 | $T(n) \le T(n/5) + T(7n/10) + O(n)$ | $9/10$ | $\Theta(n)$ |
| 7 | $T(n) \le T(n/7) + T(5n/7) + O(n)$ | $6/7$ | $\Theta(n)$ |

The book's point: **5 is the smallest odd block size that gives exponential decay.** With blocks of 3 every level sums to at most $n$ over $\log_{3/2}n$ levels, and $\log_3 n$ levels are complete, so the bound $\Theta(n\log n)$ is tight — no faster than sorting. (Even block sizes add complications. The book stops at blocks of 3; the row for 7 uses the same count.)

**The hidden constant is large.** The median of 5 elements can be found with 6 comparisons, so the block medians cost $6n/5$ comparisons; after the recursive call about $3n/10$ elements are already known to lie on each side of mom, so partitioning needs only about $2n/5$ more instead of $n-1$. For the worst-case number of comparisons,
$$
T(n) \le T(n/5) + T(7n/10) + \frac{8n}{5} \quad\Longrightarrow\quad T(n) \le \frac{8n}{5}\sum_{i\ge0}\Big(\frac{9}{10}\Big)^i = 16n.
$$
In practice median of medians beats this worst case, but it is still slower than sorting for moderately large arrays. The practical choice is a **uniformly random pivot**: the expected number of comparisons to find the median is then at most $4n$.

> [!trap] Selection traps
> - **The general $k$.** Describe the recursive problem as "the $k$-th smallest element of $A[1..n]$", not "the median" — the recursion needs it, and the rubric's description points are for exactly this.
> - **The base case must be large enough.** $\lfloor m/2\rfloor$ must be a valid rank: with $n\le 5$ there is a single block and "the 0th smallest median" is meaningless. Any threshold of at least 5 works; 25 is arbitrary.
> - **Distinct elements.** The $7n/10$ bound counts elements *strictly* smaller or larger than mom. With many copies of the pivot, Lomuto's Partition sends them all to the right (on an all-equal array the second call gets $n-1$ elements); use a three-way partition ($<$, $=$, $>$) or break ties consistently.
> - **Blocks of 3** give $T(n)\le T(n/3) + T(2n/3) + O(n) = \Theta(n\log n)$, not $O(n)$: the subproblem sizes add up to $n$.

Concept page: [[concepts/linear-time-selection]].

## 1.9 Fast multiplication

To multiply two $n$-digit numbers $x$ and $y$, split each at $m = \lceil n/2\rceil$ digits, $x = 10^m a + b$ and $y = 10^m c + d$, and use
$$
(10^m a + b)(10^m c + d) = 10^{2m}ac + 10^m(bc + ad) + bd.
$$
Multiplying by a power of 10 is a shift, so everything except the four products takes $O(n)$ time:

```text
SplitMultiply(x, y, n):
  if n = 1
    return x · y
  else
    m ← ⌈n/2⌉
    a ← ⌊x/10^m⌋; b ← x mod 10^m      ⟨⟨x = 10^m a + b⟩⟩
    c ← ⌊y/10^m⌋; d ← y mod 10^m      ⟨⟨y = 10^m c + d⟩⟩
    e ← SplitMultiply(a, c, m)
    f ← SplitMultiply(b, d, m)
    g ← SplitMultiply(b, c, m)
    h ← SplitMultiply(a, d, m)
    return 10^(2m) e + 10^m (g + h) + f
```

Correctness is an induction using the identity. The recurrence $T(n) = 4T(\lceil n/2\rceil) + O(n)$ has level sums $n, 2n, 4n, \dots$ — increasing — so $T(n) = \Theta(n^{\log_2 4}) = \Theta(n^2)$: no better than the grade-school algorithm, and in fact it multiplies every digit of $x$ by every digit of $y$.

Kolmogorov conjectured that $\Theta(n^2)$ time is necessary; in 1960 the student Anatolii Karatsuba refuted the conjecture by noticing that the middle coefficient needs only **one** more product:
$$
bc + ad = ac + bd - (a-b)(c-d).
$$

```text
FastMultiply(x, y, n):
  if n = 1
    return x · y
  else
    m ← ⌈n/2⌉
    a ← ⌊x/10^m⌋; b ← x mod 10^m      ⟨⟨x = 10^m a + b⟩⟩
    c ← ⌊y/10^m⌋; d ← y mod 10^m      ⟨⟨y = 10^m c + d⟩⟩
    e ← FastMultiply(a, c, m)
    f ← FastMultiply(b, d, m)
    g ← FastMultiply(a − b, c − d, m)
    return 10^(2m) e + 10^m (e + f − g) + f
```

> [!key] Karatsuba's algorithm
> $\textsf{FastMultiply}$ multiplies two $n$-digit numbers in time
> $$
> T(n) \le 3T(\lceil n/2\rceil) + O(n) \quad\Longrightarrow\quad T(n) = \Theta(n^{\lg 3}) = O(n^{1.585}).
> $$
> The level sums $(3/2)^i n$ increase, so the leaves dominate: $3^{\lg n} = n^{\lg 3}$ of them, $\lg 3 = 1.58496\ldots$

For $n = 2^k$ digits the two algorithms perform $4^k = n^2$ and $3^k = n^{\lg 3}$ one-digit multiplications respectively — for $n = 1024$, $1{,}048{,}576$ versus $59{,}049$.

> [!note] Negative halves
> $a-b$ and $c-d$ may be negative, but they still have at most $m$ digits — provided a negative number is split by its absolute value ($x = 10^m a + b$ with $a$, $b$ both $\le 0$), so that $a$ and $b$ always have the same sign and $\lvert a - b\rvert < 10^m$. Karatsuba's original version used $(a+b)(c+d) - ac - bd = bc + ad$ instead; it also runs in $O(n^{\lg 3})$ time, but $a+b$ and $c+d$ can have $m+1$ digits, which makes the recurrence messier. The $a-b$ variant is due to Knuth.

Splitting into more pieces goes further. Toom–Cook splits each number into $k$ parts and uses $2k-1$ recursive multiplications, for $O(n^{1 + 1/\lg k})$ time; FFT-based algorithms reach $O(n\log n\log\log n)$ (Schönhage–Strassen, 1971) and finally $O(n\log n)$ (Harvey and van der Hoeven, 2019).

## 1.10 Exponentiation

Compute $a^n$ for a positive integer $n$. The base $a$ can be anything we know how to multiply — an integer, a real number, a number modulo $N$ (cryptography), a matrix (evaluating recurrences, shortest paths) — so we cannot know what one multiplication costs, and we **count multiplications**. The naive loop, $x\leftarrow a$ and then $x\leftarrow x\cdot a$ for $i\leftarrow 2$ to $n$ ($\textsf{SlowPower}$), performs $n-1$ of them.

Piṅgala (2nd century BCE) used the recursive formula
$$
a^n = \begin{cases} 1 & \text{if } n = 0,\\ (a^{n/2})^2 & \text{if } n>0 \text{ is even},\\ (a^{\lfloor n/2\rfloor})^2\cdot a & \text{otherwise}.\end{cases}
$$
As pseudocode:

```text
PiṅgalaPower(a, n):
  if n = 1
    return a
  else
    x ← PiṅgalaPower(a, ⌊n/2⌋)
    if n is even
      return x · x
    else
      return x · x · a
```

The number of multiplications satisfies $T(n)\le T(n/2) + 2$, so $T(n) = O(\log n)$. Replacing addition by multiplication in peasant multiplication — "squaring and mediation" — gives an almost identical algorithm based on $a^n = (a^2)^{n/2}$ for even $n$ and $(a^2)^{\lfloor n/2\rfloor}\cdot a$ for odd $n$:

```text
PeasantPower(a, n):
  if n = 1
    return a
  else if n is even
    return PeasantPower(a², n/2)
  else
    return PeasantPower(a², ⌊n/2⌋) · a
```

> [!key] Repeated squaring
> PiṅgalaPower and PeasantPower each compute $a^n$ with exactly $\lfloor\lg n\rfloor + \beta(n) - 1$ multiplications, where $\beta(n)$ is the number of 1s in the binary representation of $n$ — so between $\lceil\lg n\rceil$ and $2\lfloor\lg n\rfloor$, i.e. $\Theta(\log n)$. That is asymptotically optimal: each multiplication at most doubles the largest power computed so far, so **every** algorithm needs at least $\lceil\lg n\rceil$ multiplications. For $n = 2^k$ both use exactly $\lg n$, which is optimal.

Not optimal for every $n$, though: both compute $a^{15}$ with six multiplications, while five suffice.

| method | powers computed | multiplications |
|---|---|---|
| Piṅgala | $a \to a^2\to a^3\to a^6\to a^7\to a^{14}\to a^{15}$ | 6 |
| Peasant | $a\to a^2\to a^4\to a^8\to a^{12}\to a^{14}\to a^{15}$ | 6 |
| optimal | $a\to a^2\to a^3\to a^5\to a^{10}\to a^{15}$ | 5 |

Whether the minimum number of multiplications for a given $n$ can be computed efficiently is a long-standing open question. Matrix powers computed this way give "even faster" Fibonacci numbers in [[2-algorithms/03-dynamic-programming#32-aside-even-faster-fibonacci-numbers|§3.2]].

## Summary

- **Reduction:** solve $X$ with an algorithm for $Y$ as a black box; correctness may not depend on how $Y$ is solved. **Recursion:** reduce to strictly smaller instances of the same problem, plus base cases. The Recursion Fairy is the induction hypothesis — prove correctness by strong induction, never by unrolling.
- **Tower of Hanoi:** move $n-1$, move the largest, move $n-1$; $T(n) = 2T(n-1)+1 = 2^n - 1$ moves, and no solution is shorter.
- **Mergesort:** split, recurse, Merge in $O(n)$; correct by Lemma 1.1 and Theorem 1.2; $T(n) = 2T(n/2) + O(n) = \Theta(n\log n)$. **Quicksort:** Partition in $O(n)$, recurse on both sides; $\Theta(n^2)$ worst case for first/last/median-of-three pivots, $O(n\log n)$ with a median pivot (or w.h.p. with a random one).
- **Divide and conquer:** divide into independent smaller instances, delegate, combine; write it up as *what it computes*, base case, divide, conquer, recurrence + solution.
- **Recursion trees:** sum level by level. Decreasing sums → $\Theta(f(n))$; equal → $\Theta(f(n)\log n)$; increasing → $\Theta(n^{\log_c r})$ leaves. Unbalanced trees are fine; floors and ceilings can be ignored (domain transformation).
- **Selection:** quickselect recurses into one side; the median of medians of blocks of 5 guarantees $\le 7n/10$, so $T(n)\le T(n/5)+T(7n/10)+O(n) = \Theta(n)$. Blocks of 3 give only $\Theta(n\log n)$.
- **Karatsuba:** $bc + ad = ac + bd - (a-b)(c-d)$ turns four half-size products into three: $\Theta(n^{\lg 3})\approx\Theta(n^{1.585})$ instead of $\Theta(n^2)$.
- **Repeated squaring:** $a^n$ with $\Theta(\log n)$ multiplications; $\lceil \lg n\rceil$ is a lower bound, which both algorithms meet when $n$ is a power of 2 (more generally, exactly when $n$ has at most two 1 bits).

> [!exam] On the exams
> Midterm 2 (Mon Nov 9) is the algorithms exam, and this chapter is its divide-and-conquer material (Homework 5). A divide-and-conquer answer is graded with the **recursive-algorithm rubric**, 10 points: **3** for a clear English description of the problem your recursive algorithm solves — what it returns in terms of its parameters, required whenever you generalize the problem (the $k$-th smallest instead of the median, extra output such as both the minimum and the maximum) or add assumptions; describing *how* it works earns none of these points; **1** for the base case(s); **2** for correctly identifying the recursive subproblems ("divide"); **2** for correctly using the results of the recursive calls ("conquer"); **2** for the time analysis — **1** for the recurrence and **1** for its closed-form solution. So a full answer has five visible parts: description, base case, subproblems, combination, recurrence with solution (say which recursion-tree case applies). Algorithms from the book and lecture — MergeSort, linear-time selection, Karatsuba — can be used as black boxes with their running times. Words like "clearly", "simply" and "just" draw extra scrutiny, and ambiguity is read unfavorably. More in [[0-toolkit/06-how-exams-are-graded|how exams are graded]].

### Sources for this page
Erickson, *Algorithms*, Chapter 1 (§§1.1–1.10, pp. 21–43), summarized in our own words, with the $n^d$ form of the three recursion-tree cases from the book's appendix on solving recurrences. Pseudocode follows the book's figures; in MomSelect the Partition call is written with the index of mom (the book passes mom itself), and the note on splitting negative numbers in FastMultiply is ours. The `SORTINGEXAMPL` examples are the book's; the partition row is the actual output of Lomuto's Partition, which differs from the book's Figure 1.7. Original to this page: the strengthened Hanoi invariant and the optimality argument, the stability remark, the tight median-of-medians grid, the exact bound $n - 3\lfloor m/2\rfloor$, the row for blocks of 7, and the exact multiplication count of repeated squaring. Grading notes paraphrase the CS/ECE 374 A (Fall 2026) standard rubrics. Every algorithm (implemented exactly as written and compared with brute force), example, count, table entry and recurrence solution on this page is checked by `tools/checks/a01.py`.
