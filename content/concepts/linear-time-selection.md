---
title: "Linear-time selection"
description: "Find the k-th smallest of n unsorted elements in O(n) worst-case time: quickselect with the median-of-medians pivot (blocks of 5), the recurrence T(n) ≤ T(n/5) + T(7n/10) + O(n), why blocks of 3 fail, and how to use selection as a black box."
tags: [concept, algorithms, recursion, midterm-2]
aliases: ["selection", "median of medians", "MomSelect", "quickselect", "BFPRT", "k-th smallest element", "median finding"]
---

> [!key] Linear-time selection (Blum, Floyd, Pratt, Rivest, Tarjan)
> Given an unsorted array $A[1..n]$ and $1\le k\le n$, the $k$-th smallest element can be found in $\Theta(n)$ worst-case time.
> - **Quickselect:** partition around a pivot of rank $r$; if $k<r$ recurse on the left part with $k$, if $k>r$ on the right part with $k-r$, otherwise return the pivot. Correct for every pivot.
> - **MomSelect:** the pivot is the median of the $\lceil n/5\rceil$ medians of blocks of 5, computed recursively. For distinct elements it leaves at most about $7n/10$ elements for the second call (repeated values: see the traps).
>
> Hence MomSelect's running time satisfies
> $$
> T(n) \le T(n/5) + T(7n/10) + O(n) = \Theta(n).
> $$

**Why it works.** Mom is larger than about half of the $m = \lceil n/5\rceil$ block medians, and each of those is larger than two more elements of its block, so at least $3\lfloor m/2\rfloor - 1\approx 3n/10$ elements are smaller than mom; symmetrically about $3n/10$ are larger. Whichever side quickselect searches, it discards about $3n/10$ elements. The two recursive calls together see at most $(1/5 + 7/10)n = 9n/10$ elements, so the level sums of the [[concepts/recursion-trees|recursion tree]] decay geometrically and the root's $O(n)$ dominates.

> [!recipe] Using selection on an exam
> Cite it as a black box: "find the $k$-th smallest element (e.g. the median) of the array in $O(n)$ time by linear-time selection." Typical uses: a perfect pivot (quicksort with median pivots is $\Theta(n\log n)$ in the worst case); splitting an array into its lower and upper halves in $O(n)$; finding all elements of rank at most $k$ (select the $k$-th, then scan).

> [!trap]
> - Quickselect needs the general $k$ — the median of $A$ is not the median of either side — so describe the recursive problem with $k$.
> - First-element or random pivots: $\Theta(n^2)$ worst case (random pivots are fast in *expectation*).
> - Blocks of 3 give $T(n)\le T(n/3) + T(2n/3) + O(n) = \Theta(n\log n)$; 5 is the smallest odd block size whose level sums decay.
> - The $7n/10$ bound needs distinct elements, or a three-way partition ($<$, $=$, $>$).
> - Linear is not fast: up to $16n$ comparisons in the worst case; in practice a random pivot wins.

**Example: the $k$ elements closest to the median.** Given $n$ distinct numbers and $k$, return the $k$ numbers whose distance to the median is smallest, in $O(n)$ time: (1) select the median $\mu$; (2) compute $D[i] = \lvert A[i] - \mu\rvert$; (3) select the $k$-th smallest distance $d$; (4) output every $A[i]$ with $D[i] < d$, then elements with $D[i] = d$ until there are $k$. Two selections and two scans: $O(n)$. For $A = 12, 3, 17, 8, 25, 1, 14, 9, 30$ and $k = 4$: $\mu = 12$, the distances are $0, 9, 5, 4, 13, 11, 2, 3, 18$, the 4th smallest is $d = 4$, and the answer is $\{12, 14, 9, 8\}$.

**Where it appears.** [[2-algorithms/01-recursion#18-linear-time-selection|§1.8]] (quickselect, MomSelect, the grid picture, block sizes, the comparison count), [[2-algorithms/01-recursion#15-quicksort|§1.5]] (the median as a quicksort pivot), [[2-algorithms/01-recursion#17-recursion-trees|§1.7]] (the decreasing case of recursion trees).

Related: [[concepts/divide-and-conquer]] · [[concepts/recursion-trees]] · [[concepts/recursion]]
