---
title: "Chapter 2 exercises — Backtracking"
description: "Solutions to selected exercises from Chapter 2 of Erickson's Algorithms: counting and weighted subset sums, text segmentation of one string and of two strings at the same indices, shortest addition chains, recursive definitions for longest common subsequence, shortest common supersequence and longest bitonic, oscillating and convex subsequences, subsequence testing and destruction, and optimal AVL, red-black and AA trees."
tags: [exercises, algorithms, backtracking, midterm-2]
---

*Solved exercises for [[2-algorithms/02-backtracking|Chapter 2]] · book pp. 93–96 · statements paraphrased; see the book for the originals*

Chapter 2 has six exercises, each in several parts; all six are here. Two parts are skipped because the book marks them ♥ (particularly challenging): 2.3(b), a sub-exponential addition-chain algorithm, and 2.5(c), two disjoint copies of a subsequence. Every algorithm is written to the [[0-toolkit/06-how-exams-are-graded#11-recursive-algorithms|recursive-algorithm rubric]]: what the recursive function computes (including any generalization), base cases, the recursive calls, how their results combine, and the running time where the exercise asks for it. A recursive definition is a backtracking algorithm in disguise ([[concepts/backtracking]]): each one below translates line by line into code, and memoizing it gives the dynamic programs of [[2-algorithms/03-dynamic-programming|Chapter 3]].

## Exercise 2.1 — Counting and weighing subset sums

> [!question] Exercise 2.1 (book p. 93)
> Describe recursive algorithms for these generalizations of SubsetSum ([[2-algorithms/02-backtracking#23-subset-sum|§2.3]]).
>
> **(a)** Given an array $X[1..n]$ of positive integers and an integer $T$, compute the **number** of subsets of $X$ whose elements sum to $T$.
>
> **(b)** Given arrays $X[1..n]$ and $W[1..n]$ of positive integers and an integer $T$, where $W[i]$ is the **weight** of $X[i]$, compute the maximum-weight subset of $X$ whose elements sum to $T$. If no subset sums to $T$, return $-\infty$.

### (a) Number of subsets with sum T

> [!hint]- Hint
> Same recursion as SubsetSum: a subset either contains the last element or it does not. The two kinds of subsets are disjoint, so add the two counts instead of OR-ing two booleans.

> [!solution]- Solution
> **What the recursion computes.** For $0\le i\le n$ and any integer $t$, let $\textsf{NumSubsets}(i,t)$ be the number of subsets of $X[1..i]$ whose elements sum to $t$. Subsets are sets of *positions*, so equal values at different positions give different subsets. We need $\textsf{NumSubsets}(n, T)$.
>
> ```text
> ⟨⟨Number of subsets of X[1 .. i] that sum to t⟩⟩
> NumSubsets(i, t):
>     if t = 0
>         return 1
>     else if t < 0 or i = 0
>         return 0
>     else
>         with ← NumSubsets(i − 1, t − X[i])
>         wout ← NumSubsets(i − 1, t)
>         return with + wout
> ```
>
> **Base cases.** Every $X[j]$ is positive, so the empty set is the *only* subset with sum $0$: the answer for $t=0$ is $1$, not "true". If $t<0$, or no elements are left and $t\ne 0$, no subset works.
>
> **Recursive case.** The subsets of $X[1..i]$ with sum $t$ that contain $X[i]$ are exactly the subsets of $X[1..i-1]$ with sum $t - X[i]$, each plus $X[i]$; those that do not contain $X[i]$ are the subsets of $X[1..i-1]$ with sum $t$. No subset is in both groups, so the counts add.
>
> **Time.** Two calls on $i-1$ plus constant work:
> $$
> \mathrm{Time}(n) \le 2\,\mathrm{Time}(n-1) + O(1) \quad\Longrightarrow\quad \mathrm{Time}(n) = O(2^n).
> $$
> The bound is tight: if $T$ exceeds the sum of all elements, the recursion tree is complete, with $2^{n+1}-1$ calls. Memoized over $(i,t)$ it takes $O(nT)$ time ([[2-algorithms/03-dynamic-programming#38-subset-sum|§3.8]]).
>
> **Example.** For the book's $X = \{8, 6, 7, 5, 3, 10, 9\}$ and $T = 15$ the answer is $4$: $\{8,7\}$, $\{7,5,3\}$, $\{6,9\}$, $\{5,10\}$. For $X = \{11, 6, 5, 1, 7, 13, 12\}$ and $T = 15$ it is $0$.
>
> **Watch out:** the base case uses positivity. With zeros allowed, "$t = 0 \Rightarrow 1$" undercounts: $X = (0, 1)$ has two subsets with sum $1$.
>
> **Answer.** $\textsf{NumSubsets}(n, T)$, computed by the recursion above in $O(2^n)$ time.

### (b) Maximum-weight subset with sum T

> [!hint]- Hint
> Replace the sum of (a) by a maximum, and give the "impossible" base case the value $-\infty$: it is the identity for $\max$, and $-\infty + W[i] = -\infty$ carries the failure upward.

> [!solution]- Solution
> **What the recursion computes.** $\textsf{MaxWeight}(i, t)$ is the largest total weight of a subset of $X[1..i]$ whose elements sum to $t$, or $-\infty$ if there is none. We need $\textsf{MaxWeight}(n, T)$.
>
> ```text
> ⟨⟨Maximum weight of a subset of X[1 .. i] that sums to t, or −∞⟩⟩
> MaxWeight(i, t):
>     if t = 0
>         return 0
>     else if t < 0 or i = 0
>         return −∞
>     else
>         with ← W[i] + MaxWeight(i − 1, t − X[i])
>         wout ← MaxWeight(i − 1, t)
>         return max{with, wout}
> ```
>
> **Base cases.** For $t=0$ the only subset is the empty set, of weight $0$. For $t<0$, or no elements left and $t\ne0$, there is no subset: $-\infty$.
>
> **Recursive case.** The best subset either contains $X[i]$ — then the rest is a best subset of $X[1..i-1]$ with sum $t - X[i]$, worth $W[i]$ more — or it does not, and then it is a best subset of $X[1..i-1]$ with sum $t$. The answer is the larger of the two; if both are $-\infty$, so is the maximum.
>
> **Time.** Again $\mathrm{Time}(n)\le 2\,\mathrm{Time}(n-1)+O(1)$, so $O(2^n)$.
>
> **The subset itself.** Return the subset along with its weight, as ConstructSubset does in §2.3: whichever branch wins, return that call's subset, with $X[i]$ added if *with* won.
>
> **Example.** $X = (8, 6, 7, 5, 3, 10, 9)$, $W = (2, 5, 1, 4, 3, 1, 2)$, $T = 15$: the four subsets with sum $15$ weigh $3$ ($\{8,7\}$), $8$ ($\{7,5,3\}$), $7$ ($\{6,9\}$) and $5$ ($\{5,10\}$), so the answer is $8$. With $T = 4$ the answer is $-\infty$.
>
> **Answer.** $\textsf{MaxWeight}(n, T)$, in $O(2^n)$ time.

Concept page: [[concepts/subset-sum]].

## Exercise 2.2 — Text segmentation variants

> [!question] Exercise 2.2 (book pp. 93–94)
> A subroutine IsWord takes an array of characters and returns True if and only if that string is a "word". Describe recursive algorithms for these variants of text segmentation ([[2-algorithms/02-backtracking#25-text-segmentation|§2.5]]).
>
> **(a)** Given $A[1..n]$, compute the number of partitions of $A$ into words. For example, `ARTISTOIL` has 2: `ARTIST·OIL` and `ART·IS·TOIL`.
>
> **(b)** Given $A[1..n]$ and $B[1..n]$, decide whether $A$ and $B$ can be partitioned into words **at the same indices**. For example, `BOTHEARTHANDSATURNSPIN` and `PINSTARTRAPSANDRAGSLAP` can: `BOT·HEART·HAND·SAT·URNS·PIN` and `PIN·START·RAPS·AND·RAGS·LAP`.
>
> **(c)** Given $A[1..n]$ and $B[1..n]$, compute the number of different ways to partition $A$ and $B$ into words at the same indices.

### (a) Counting segmentations

> [!hint]- Hint
> Use Splittable's recursion: the first word is $A[i..j]$ for some $j$. Different first words give different partitions, so OR becomes a sum.

> [!solution]- Solution
> **What the recursion computes.** With $A$ global, $\textsf{NumSplits}(i)$ is the number of ways to partition the suffix $A[i..n]$ into words. We need $\textsf{NumSplits}(1)$.
>
> ```text
> ⟨⟨Number of partitions of the suffix A[i .. n] into words⟩⟩
> NumSplits(i):
>     if i > n
>         return 1
>     total ← 0
>     for j ← i to n
>         if IsWord(A[i .. j])
>             total ← total + NumSplits(j + 1)
>     return total
> ```
>
> **Base case.** The empty suffix has exactly **one** partition, into zero words. Returning $0$ here would make every count $0$.
>
> **Recursive case.** Group the partitions of $A[i..n]$ by their first word $A[i..j]$. For a fixed $j$, the partitions in the group correspond one-to-one to the partitions of $A[j+1..n]$, and different $j$ give disjoint groups, so the total is the sum over all $j$ for which $A[i..j]$ is a word.
>
> **Time** (counted in calls to IsWord, as for Splittable). Every prefix is tested, and there is a recursive call for every suffix:
> $$
> \mathrm{Time}(n) \le \sum_{m=0}^{n-1}\mathrm{Time}(m) + O(n) \quad\Longrightarrow\quad \mathrm{Time}(n) = O(2^n).
> $$
> A counting algorithm cannot stop early, so the bound is reached: if every substring is a word there are $2^{n-1}$ partitions and NumSplits calls IsWord exactly $2^n - 1$ times. Memoized, it makes $O(n^2)$ calls ([[2-algorithms/03-dynamic-programming#33-interpunctio-verborum-redux|§3.3]]).
>
> **Example.** With the words A, ART, ARTIST, I, IS, IT, OIL, TO, TOIL, the input `ARTISTOIL` gives $\textsf{NumSplits}(1) = 0 + 1 + 1 = 2$: the first word A leaves `RTISTOIL`, which has no partition; ART leaves `ISTOIL` = IS·TOIL; ARTIST leaves `OIL`.
>
> **Answer.** $\textsf{NumSplits}(1)$, in $O(2^n)$ time.

### (b) Two strings, same indices

> [!hint]- Hint
> A common segmentation is one list of cut positions that works for both strings. Choose the end $j$ of the next word once, and test $A[i..j]$ *and* $B[i..j]$.

> [!solution]- Solution
> **What the recursion computes.** $\textsf{BothSplittable}(i)$ is True if and only if the suffixes $A[i..n]$ and $B[i..n]$ can be partitioned into words at the same indices. We need $\textsf{BothSplittable}(1)$.
>
> ```text
> ⟨⟨Can A[i .. n] and B[i .. n] be split into words at the same indices?⟩⟩
> BothSplittable(i):
>     if i > n
>         return True
>     for j ← i to n
>         if IsWord(A[i .. j]) and IsWord(B[i .. j])
>             if BothSplittable(j + 1)
>                 return True
>     return False
> ```
>
> **Base case.** Two empty suffixes are both split into zero words: True.
>
> **Recursive case.** In a common segmentation of the suffixes, the first words of both are $A[i..j]$ and $B[i..j]$ for the *same* $j$; both must be words, and the rest is a common segmentation of $A[j+1..n]$ and $B[j+1..n]$. Conversely, any such $j$ with BothSplittable$(j+1)$ true gives a common segmentation. The loop tries every $j$.
>
> **Time.** The same recurrence as in (a), with two IsWord calls per $j$: $O(2^n)$.
>
> **Watch out:** running Splittable on $A$ and on $B$ separately is wrong. With the words A, BC, XY, Z, both `ABC` = A·BC and `XYZ` = XY·Z can be split, but not at the same index.
>
> **Example.** In the book's pair, the cuts after positions 3, 8, 12, 15 and 19 split both strings into words.
>
> **Answer.** $\textsf{BothSplittable}(1)$, in $O(2^n)$ time.

### (c) Counting common segmentations

> [!hint]- Hint
> Combine (a) and (b): the loop of (b), the sum and the base case $1$ of (a).

> [!solution]- Solution
> **What the recursion computes.** $\textsf{NumBothSplits}(i)$ is the number of ways to partition $A[i..n]$ and $B[i..n]$ into words at the same indices. We need $\textsf{NumBothSplits}(1)$.
>
> ```text
> ⟨⟨Number of common segmentations of A[i .. n] and B[i .. n]⟩⟩
> NumBothSplits(i):
>     if i > n
>         return 1
>     total ← 0
>     for j ← i to n
>         if IsWord(A[i .. j]) and IsWord(B[i .. j])
>             total ← total + NumBothSplits(j + 1)
>     return total
> ```
>
> **Correctness.** Group the common segmentations by the shared end $j$ of their first words, as in (a); the base case counts the one empty segmentation.
>
> **Time.** $O(2^n)$, as in (a) and (b).
>
> **Example.** If the dictionary holds the eleven words of the book's segmentation plus URN, SPIN, RAG and SLAP, the book's pair has exactly $2$ common segmentations; the second is `BOT·HEART·HAND·SAT·URN·SPIN` and `PIN·START·RAPS·AND·RAG·SLAP`.
>
> **Answer.** $\textsf{NumBothSplits}(1)$, in $O(2^n)$ time.

## Exercise 2.3 — Shortest addition chains

> [!question] Exercise 2.3 (book p. 94)
> An **addition chain** for $n$ is an increasing sequence of integers $1 = x_0 < x_1 < \cdots < x_\ell = n$ in which every entry after the first is the sum of two earlier entries: for every $k > 0$ there are indices $i \le j < k$ with $x_k = x_i + x_j$. Its **length** is $\ell$, the number of entries minus one. For example, $\langle 1, 2, 3, 5, 10, 20, 23, 46, 92, 184, 187, 374\rangle$ is an addition chain for $374$ of length $11$.
>
> **(a)** Describe a recursive backtracking algorithm that computes a minimum-length addition chain for a given positive integer $n$. Running time exponential in $n$ is fine; don't analyze it. (The book's hint: this is more like $n$ queens than text segmentation.)
>
> **(b)** ♥ The same in time sub-exponential in $n$. *(Skipped.)*

### (a) Exhaustive search over chains

> [!hint]- Hint
> Build the chain one entry at a time, as $n$ queens places one queen per row ([[2-algorithms/02-backtracking#21-n-queens|§2.1]]). A later entry may use *any* earlier entry, so — unlike a suffix in text segmentation — the whole chain built so far must be passed to the recursive call.

> [!solution]- Solution
> **What the recursion computes.** Given an addition chain $X[0..k]$ (so $X[0] = 1$) with $X[k]\le n$, $\textsf{ShortestChain}(X[0..k])$ returns a shortest addition chain for $n$ whose first $k+1$ entries are $X[0..k]$; $n$ is global. We need $\textsf{ShortestChain}(\langle 1\rangle)$.
>
> ```text
> ⟨⟨Shortest addition chain for n that begins with the chain X[0 .. k]⟩⟩
> ShortestChain(X[0 .. k]):
>     if X[k] = n
>         return X[0 .. k]
>     best ← None
>     for i ← 0 to k
>         for j ← i to k
>             if X[k] < X[i] + X[j] ≤ n
>                 C ← ShortestChain(X[0 .. k] • ⟨X[i] + X[j]⟩)
>                 if best = None or C is shorter than best
>                     best ← C
>     return best
> ```
>
> **Base case.** If $X[k] = n$, the prefix is already a chain for $n$, and it is the only one that begins with this prefix: entries increase, so nothing can follow $n$.
>
> **Recursive case.** If $X[k] < n$, every chain for $n$ that extends the prefix has a next entry $X[i] + X[j]$ with $i\le j\le k$ and $X[k] < X[i] + X[j] \le n$ (increasing, and nothing larger than $n$ can be followed by $n$). The two loops try every such entry, the Recursion Fairy returns a shortest completion of each, and the shortest of those is the answer. At least one candidate exists, $X[0] + X[k] = X[k] + 1$, so the result is never None.
>
> **Termination.** Every call increases the last entry, which stays at most $n$, so the recursion depth is at most $n-1$. The running time is exponential in $n$ (not analyzed, as the exercise allows). A sum reachable from several pairs $(i,j)$ is tried more than once; skipping repeats is a safe speedup.
>
> **Example.** For $n = 15$ the shortest chains have length $5$, for instance $1, 2, 3, 5, 10, 15$. Square-and-multiply ([[2-algorithms/01-recursion#110-exponentiation|§1.10]]) gives $1, 2, 3, 6, 7, 14, 15$, of length $6$; $15$ is the smallest $n$ for which it is not optimal. The book's chain for $374$ is optimal: there is no addition chain for $374$ of length $10$, while square-and-multiply needs $13$.
>
> **Answer.** $\textsf{ShortestChain}(\langle1\rangle)$: try every legal next entry, recursively, and keep the shortest completed chain.

## Exercise 2.4 — Recursive definitions for subsequence problems

> [!question] Exercise 2.4 (book pp. 94–95)
> Give a simple recursive definition for each function.
>
> **(a)** $\textsf{lcs}(A,B)$: the length of a longest **common subsequence** of $A[1..m]$ and $B[1..n]$ (a subsequence of both).
>
> **(b)** $\textsf{scs}(A,B)$: the length of a shortest **common supersequence** of $A[1..m]$ and $B[1..n]$ (a sequence that contains both as subsequences).
>
> **(c)** $X[1..n]$ is **bitonic** if there is an index $i$ with $1 < i < n$ such that $X[1..i]$ is increasing and $X[i..n]$ is decreasing. $\textsf{lbs}(A)$: the length of a longest bitonic subsequence of an integer array $A$.
>
> **(d)** $X[1..n]$ is **oscillating** if $X[i] < X[i+1]$ for every even $i$ and $X[i] > X[i+1]$ for every odd $i$. $\textsf{los}(A)$: the length of a longest oscillating subsequence of $A$.
>
> **(e)** $\textsf{sos}(A)$: the length of a shortest oscillating supersequence of $A$.
>
> **(f)** $X[1..n]$ is **convex** if $2\cdot X[i] < X[i-1] + X[i+1]$ for all $i$. $\textsf{lxs}(A)$: the length of a longest convex subsequence of $A$.

Conventions below: "increasing" and "decreasing" are strict, as in [[2-algorithms/02-backtracking#26-longest-increasing-subsequence|§2.6]]; $\max\varnothing = 0$, as in [[2-algorithms/02-backtracking#27-longest-increasing-subsequence-take-2|§2.7]]; the arrays are global and each function's parameters are indices. The single-array parts (c), (d), (f) reuse the "what's next?" recursion of $\textsf{LISfirst}$ ([[concepts/longest-increasing-subsequence]]). The examples use $A = 3, 1, 4, 1, 5, 9, 2, 6, 5, 3$.

### (a) Longest common subsequence

> [!hint]- Hint
> Look at the first elements $A[i]$ and $B[j]$ of the two suffixes. In a common subsequence, either $A[i]$ is unused, or $B[j]$ is unused, or the two are matched to each other.

> [!solution]- Solution
> **Definition.** $\textsf{lcs}(i,j)$ is the length of a longest common subsequence of the suffixes $A[i..m]$ and $B[j..n]$; the answer is $\textsf{lcs}(1,1)$.
> $$
> \textsf{lcs}(i,j) = \begin{cases}
> 0 & \text{if } i > m \text{ or } j > n\\
> 1 + \textsf{lcs}(i+1, j+1) & \text{if } A[i] = B[j]\\
> \max\{\textsf{lcs}(i+1, j),\ \textsf{lcs}(i, j+1)\} & \text{otherwise}
> \end{cases}
> $$
>
> **Why.** Write a common subsequence as a list of matched pairs $(p,q)$ with $A[p] = B[q]$, increasing in both coordinates. If $A[i]$ is in no pair, the pairs form a common subsequence of $A[i+1..m]$ and $B[j..n]$; likewise if $B[j]$ is in no pair. Otherwise $A[i]$ is in the first pair (it is the earliest element of $A[i..m]$) and so is $B[j]$ — so they are matched to each other, $A[i] = B[j]$, and the other pairs form a common subsequence of $A[i+1..m]$ and $B[j+1..n]$. So $\textsf{lcs}(i,j)$ is the largest of $\textsf{lcs}(i+1,j)$, $\textsf{lcs}(i,j+1)$ and, if $A[i] = B[j]$, $1 + \textsf{lcs}(i+1,j+1)$; each option is achievable.
>
> **Why matching wins when $A[i] = B[j]$** (the rubric wants this proved, not assumed). Deleting $B[j]$ from a common subsequence of $A[i+1..m]$ and $B[j..n]$ loses at most one pair, so $\textsf{lcs}(i+1,j)\le 1+\textsf{lcs}(i+1,j+1)$; symmetrically $\textsf{lcs}(i,j+1)\le 1+\textsf{lcs}(i+1,j+1)$. Hence, when $A[i] = B[j]$, the match is the largest option, as in the recurrence.
>
> **Example.** $\textsf{lcs}(\texttt{ALGORITHM}, \texttt{ALTRUISTIC}) = 5$, for instance `ALRIT`. Memoized: $mn$ subproblems, $O(mn)$ time — a close cousin of edit distance ([[2-algorithms/03-dynamic-programming#37-edit-distance|§3.7]]).
>
> **Answer.** $\textsf{lcs}(A,B) = \textsf{lcs}(1,1)$ with the recurrence above.

### (b) Shortest common supersequence

> [!hint]- Hint
> The first symbol of a shortest common supersequence is $A[i]$ or $B[j]$ — otherwise delete it. After it, what is left to cover?

> [!solution]- Solution
> **Definition.** $\textsf{scs}(i,j)$ is the length of a shortest common supersequence of $A[i..m]$ and $B[j..n]$; the answer is $\textsf{scs}(1,1)$.
> $$
> \textsf{scs}(i,j) = \begin{cases}
> n - j + 1 & \text{if } i > m\\
> m - i + 1 & \text{if } j > n\\
> 1 + \textsf{scs}(i+1, j+1) & \text{if } A[i] = B[j]\\
> 1 + \min\{\textsf{scs}(i+1, j),\ \textsf{scs}(i, j+1)\} & \text{otherwise}
> \end{cases}
> $$
>
> **Base cases.** If one suffix is empty, the shortest supersequence is the other suffix.
>
> **Why.** Let $Z$ be a shortest common supersequence and fix embeddings of $A[i..m]$ and $B[j..n]$ in it. $Z[1]$ is used by at least one embedding, or deleting it would leave a shorter one. If $A$'s embedding uses it, $Z[1] = A[i]$ and $Z[2..]$ contains $A[i+1..m]$; $Z[2..]$ also contains $B[j..n]$, or $B[j+1..n]$ if $B[j]$ is embedded at $Z[1]$ too, which needs $A[i] = B[j]$. The case where $B$'s embedding uses $Z[1]$ is symmetric. So $|Z|$ is $1$ plus the smallest of $\textsf{scs}(i+1,j)$, $\textsf{scs}(i,j+1)$ and (only if $A[i]=B[j]$) $\textsf{scs}(i+1,j+1)$, and putting the symbol in front of an optimal solution of the subproblem achieves each option. When $A[i] = B[j]$, the last option is the smallest: a supersequence of $A[i+1..m]$ and $B[j..n]$ also contains $B[j+1..n]$, so $\textsf{scs}(i+1,j+1)\le\textsf{scs}(i+1,j)$, and symmetrically.
>
> **Example.** $\textsf{scs}(\texttt{ALGORITHM}, \texttt{ALTRUISTIC}) = 14$. In general $\textsf{scs}(A,B) = m + n - \textsf{lcs}(A,B)$: the matched pairs of a common subsequence are the symbols the two strings can share.
>
> **Answer.** $\textsf{scs}(A,B) = \textsf{scs}(1,1)$ with the recurrence above.

### (c) Longest bitonic subsequence

> [!hint]- Hint
> Split a bitonic subsequence at its peak: an increasing subsequence that **ends** at the peak, then a decreasing one that **starts** there. Both halves depend only on the peak's index. The book's definition ($1 < i < n$) needs at least two elements in each half.

> [!solution]- Solution
> **Definition.** For $1\le i\le n$, let $\textsf{LISlast}(i)$ be the length of a longest increasing subsequence of $A[1..i]$ that ends with $A[i]$, and $\textsf{LDSfirst}(i)$ the length of a longest decreasing subsequence of $A[i..n]$ that begins with $A[i]$:
> $$
> \textsf{LISlast}(i) = 1 + \max\{\textsf{LISlast}(h) \mid h < i,\ A[h] < A[i]\}
> $$
> $$
> \textsf{LDSfirst}(i) = 1 + \max\{\textsf{LDSfirst}(j) \mid j > i,\ A[j] < A[i]\}
> $$
> With $\max\varnothing = 0$, the base cases come for free: for example $\textsf{LISlast}(1) = \textsf{LDSfirst}(n) = 1$. Then
> $$
> \textsf{lbs}(A) = \max\{\textsf{LISlast}(i) + \textsf{LDSfirst}(i) - 1 \mid 1\le i\le n,\ \textsf{LISlast}(i)\ge 2,\ \textsf{LDSfirst}(i)\ge 2\},
> $$
> which is $0$ if no index qualifies.
>
> **Why.** Let $X[1..\ell]$ be bitonic with turning index $p$, $1<p<\ell$, and let its peak $X[p]$ be $A[i]$. Then $X[1..p]$ is an increasing subsequence of $A[1..i]$ ending with $A[i]$, of length $p\ge2$, and $X[p..\ell]$ is a decreasing subsequence of $A[i..n]$ beginning with $A[i]$, of length $\ell-p+1\ge2$; they share only $A[i]$. The two halves live on opposite sides of $i$, so they can be chosen independently: the best bitonic subsequence with peak $A[i]$ has length $\textsf{LISlast}(i)+\textsf{LDSfirst}(i)-1$, provided both are at least $2$. The recurrences for $\textsf{LISlast}$ and $\textsf{LDSfirst}$ are $\textsf{LISfirst}$'s from §2.7, run backward and with the inequality flipped.
>
> **Watch out:** some sources also call increasing or decreasing sequences bitonic. Under the book's definition they are not — $\textsf{lbs}(1,2,3) = 0$ — and the two "$\ge 2$" conditions enforce that; drop them for the other convention.
>
> **Example.** For $A = 3,1,4,1,5,9,2,6,5,3$ the peak $9$ has $\textsf{LISlast} = 4$ ($1,4,5,9$) and $\textsf{LDSfirst} = 4$ ($9,6,5,3$), so $\textsf{lbs}(A) = 7$, for instance $1,4,5,9,6,5,3$. Memoized: $O(n)$ subproblems with $O(n)$ work each, $O(n^2)$ time.
>
> **Answer.** $\textsf{lbs}(A) = \max_i\{\textsf{LISlast}(i) + \textsf{LDSfirst}(i) - 1\}$ over the indices where both are at least $2$ (and $0$ if there are none).

### (d) Longest oscillating subsequence

> [!hint]- Hint
> An oscillating sequence goes down, up, down, … from its first element. Remember the last element chosen and the direction of the next step: two mutually recursive versions of $\textsf{LISfirst}$.

> [!solution]- Solution
> **Definition.** For $1\le i\le n$, let $\textsf{Down}(i)$ be the length of a longest subsequence of $A[i..n]$ that begins with $A[i]$ and alternates $X_1 > X_2 < X_3 > \cdots$ (an oscillating subsequence starting at $A[i]$), and $\textsf{Up}(i)$ the same for $X_1 < X_2 > X_3 < \cdots$:
> $$
> \textsf{Down}(i) = 1 + \max\{\textsf{Up}(j) \mid j > i,\ A[j] < A[i]\}
> $$
> $$
> \textsf{Up}(i) = 1 + \max\{\textsf{Down}(j) \mid j > i,\ A[j] > A[i]\}
> $$
> $$
> \textsf{los}(A) = \max\{\textsf{Down}(i) \mid 1 \le i \le n\}\qquad(\text{and } 0 \text{ if } n = 0).
> $$
> Equivalently, add a sentinel $A[0] = -\infty$ and return $\textsf{Up}(0) - 1$.
>
> **Why.** The definition makes position 1 (odd) a down-step, position 2 an up-step, and so on. If $X_1 > X_2 < X_3 > \cdots$ starts at $A[i]$, then either it is $A[i]$ alone, or it continues with some $A[j]$, $j>i$, $A[j]<A[i]$, and $X_2, X_3, \ldots$ alternates *up* first. So the longest choice is $1$ plus the best $\textsf{Up}(j)$, and symmetrically for $\textsf{Up}$. With $\max\varnothing = 0$ the base case $\textsf{Down}(n) = \textsf{Up}(n) = 1$ is built in.
>
> **Example.** $\textsf{los}(3,1,4,1,5,9,2,6,5,3) = 8$, for instance $3,1,4,1,5,2,6,5$. Memoized: $2n$ subproblems, $O(n^2)$ time.
>
> **Answer.** $\textsf{los}(A) = \max_i \textsf{Down}(i)$ with the mutual recursion above.

### (e) Shortest oscillating supersequence

> [!hint]- Hint
> The inserted elements can be any integers, so pick them very large or very small. Between consecutive elements of $A$, inserting $0$ elements requires the right comparison and flips the direction of the next step; inserting $1$ always works and keeps it; inserting $2$ always works and flips it. More is never needed.

> [!solution]- Solution
> **Definition.** For $1\le i\le n$, let $\textsf{SDown}(i)$ be the length of a shortest sequence that begins with $A[i]$, contains $A[i..n]$ as a subsequence, and alternates $X_1 > X_2 < X_3 > \cdots$; let $\textsf{SUp}(i)$ be the same with $X_1 < X_2 > X_3 < \cdots$. Then $\textsf{SDown}(n) = \textsf{SUp}(n) = 1$, and for $i < n$
> $$
> \textsf{SDown}(i) = \min\{\,d_i + \textsf{SUp}(i+1),\ 2 + \textsf{SDown}(i+1)\,\},\qquad d_i = \begin{cases}1 & \text{if } A[i] > A[i+1]\\ 3 & \text{otherwise}\end{cases}
> $$
> $$
> \textsf{SUp}(i) = \min\{\,u_i + \textsf{SDown}(i+1),\ 2 + \textsf{SUp}(i+1)\,\},\qquad u_i = \begin{cases}1 & \text{if } A[i] < A[i+1]\\ 3 & \text{otherwise}\end{cases}
> $$
> $$
> \textsf{sos}(A) = \min\{\textsf{SDown}(1),\ 1 + \textsf{SUp}(1)\}\qquad(\text{and } 0 \text{ if } n = 0).
> $$
>
> **Why.** Fix an embedding of $A$ in a shortest oscillating supersequence $X$; the other elements of $X$ are *inserted*. Nothing is inserted after $A[n]$ (cutting off a tail keeps a sequence oscillating). Suppose $t$ elements are inserted between $A[i]$ and $A[i+1]$, and the step after $A[i]$ must go down. For $t = 0$ we need $A[i] > A[i+1]$, and the step after $A[i+1]$ goes up. Every $t\ge1$ is possible — insert alternately a value below everything and a value above everything, starting with a small one — and $A[i+1]$'s next step goes down for odd $t$ and up for even $t$. The cheapest options are therefore $t = 1$ (cost $2 + \textsf{SDown}(i+1)$), and $t = 0$ or else $t = 2$ (cost $d_i + \textsf{SUp}(i+1)$); any larger $t$ costs more than $t-2$ with the same parity. $\textsf{SUp}$ is symmetric. At the start, $A[1]$ is either the first element (down-step next) or comes after one inserted large element (then it sits at position 2, and its next step goes up); more elements in front never help, by the same parity argument.
>
> **A simpler rule (proved, not assumed).** Inserting one extreme element right after $A[i]$ flips its direction, so $\textsf{SDown}(i)\le 1+\textsf{SUp}(i)$ and $\textsf{SUp}(i)\le 1+\textsf{SDown}(i)$. Plugging this in, each minimum above is attained by the comparison option when the comparison holds and by the $t=1$ option when it fails, and $\textsf{sos}(A) = \textsf{SDown}(1)$. In words: scan $A$ and insert one extreme element exactly where the required comparison fails.
>
> **Example.** For $A = 3,1,4,1,5,9,2,6,5,3$ the required pattern $>,<,>,<,\ldots$ fails at $5 > 9$ and, later, at $5 < 3$. Inserting $0$ and $10$ gives $3,1,4,1,5,0,9,2,6,5,10,3$, so $\textsf{sos}(A) = 12$.
>
> **Answer.** $\textsf{sos}(A) = \min\{\textsf{SDown}(1), 1 + \textsf{SUp}(1)\}$ with the recurrences above, which collapse to the linear scan.

### (f) Longest convex subsequence

> [!hint]- Hint
> Convexity constrains three consecutive elements, so remembering only the last element chosen is not enough. Remember the last *two*: a function of two indices.

> [!solution]- Solution
> **Convention.** The condition applies to the interior indices $1 < i < n$, so every sequence of length at most $2$ is convex.
>
> **Definition.** For $1\le i<j\le n$, let $\textsf{LXS}(i,j)$ be the length of a longest convex subsequence of $A[i..n]$ whose first two elements are $A[i]$ and $A[j]$:
> $$
> \textsf{LXS}(i,j) = \max\big(\{2\} \cup \{\,1 + \textsf{LXS}(j,k) \mid k > j,\ 2A[j] < A[i] + A[k]\,\}\big)
> $$
> $$
> \textsf{lxs}(A) = \max\big(\{\min(n,2)\}\cup\{\textsf{LXS}(i,j) \mid 1\le i<j\le n\}\big).
> $$
>
> **Why.** A convex subsequence that starts with $A[i], A[j]$ either stops there (length $2$) or continues with some $A[k]$, $k>j$. In the second case the sequence after $A[i]$ is convex and starts with $A[j], A[k]$, and the only condition involving $A[i]$ is the one at $A[j]$: $2A[j] < A[i] + A[k]$. Conversely, putting $A[i]$ in front of a convex sequence that starts with $A[j], A[k]$ keeps it convex when that inequality holds. There is no separate base case: when no $k$ qualifies, the value is $2$.
>
> **Example.** $\textsf{lxs}(3,1,4,1,5,9,2,6,5,3) = 5$, for instance $3,1,1,2,6$: $2\cdot1 < 3+1$, $2\cdot1 < 1+2$, $2\cdot2 < 1+6$. Memoized: $\binom n2$ subproblems with $O(n)$ work each, $O(n^3)$ time.
>
> **Answer.** $\textsf{lxs}(A) = \max_{i<j}\textsf{LXS}(i,j)$ (at least $\min(n,2)$) with the recurrence above.

## Exercise 2.5 — Subsequences of a second array

> [!question] Exercise 2.5 (book p. 95)
> The input is two arrays $X[1..k]$ and $Y[1..n]$ with $k\le n$. Don't analyze the running times.
>
> **(a)** Describe a recursive backtracking algorithm to decide whether $X$ is a subsequence of $Y$. For example, `PPAP` is a subsequence of `PENPINEAPPLEAPPLEPEN`.
>
> **(b)** Describe a recursive backtracking algorithm to find the smallest number of symbols that can be removed from $Y$ so that $X$ is no longer a subsequence — equivalently, the longest subsequence of $Y$ that is not a supersequence of $X$. For example, after removing two symbols from `PENPINEAPPLEAPPLEPEN` (for instance its two copies of `A`), `PPAP` is no longer a subsequence.
>
> **(c)** ♥ Decide whether $X$ occurs as two *disjoint* subsequences of $Y$. *(Skipped.)*

### (a) Is X a subsequence of Y?

> [!hint]- Hint
> Decide the fate of $Y[j]$: if it equals $X[i]$, it can be used for $X[i]$ or skipped; otherwise it must be skipped.

> [!solution]- Solution
> **What the recursion computes.** $\textsf{IsSubseq}(i,j)$ is True if and only if $X[i..k]$ is a subsequence of $Y[j..n]$. We need $\textsf{IsSubseq}(1,1)$.
>
> ```text
> ⟨⟨Is X[i .. k] a subsequence of Y[j .. n]?⟩⟩
> IsSubseq(i, j):
>     if i > k
>         return True
>     else if j > n
>         return False
>     else if X[i] = Y[j]
>         return IsSubseq(i + 1, j + 1) ∨ IsSubseq(i, j + 1)
>     else
>         return IsSubseq(i, j + 1)
> ```
>
> **Base cases.** The empty sequence is a subsequence of everything. A nonempty sequence is not a subsequence of the empty one.
>
> **Recursive cases.** An embedding of $X[i..k]$ in $Y[j..n]$ either uses $Y[j]$ — then $Y[j]$ is matched to $X[i]$, so $X[i] = Y[j]$, and the rest embeds $X[i+1..k]$ in $Y[j+1..n]$ — or it does not, and then it embeds $X[i..k]$ in $Y[j+1..n]$. The algorithm tries exactly these options.
>
> **Greedy is safe here (with proof).** When $X[i] = Y[j]$, the second call is unnecessary: if $X[i..k]$ is a subsequence of $Y[j+1..n]$, then so is $X[i+1..k]$, so the first call already returns True. Dropping it leaves one call per level, $O(n)$ time.
>
> **Answer.** $\textsf{IsSubseq}(1,1)$.

### (b) Fewest deletions that destroy X

> [!hint]- Hint
> Walk through $Y$ and decide, for each symbol, delete or keep. Keeping a symbol different from $X[i]$ changes nothing. Keeping $Y[j] = X[i]$ means the rest of $Y$ must not contain $X[i+1..k]$.

> [!solution]- Solution
> **What the recursion computes.** $\textsf{MinDel}(i,j)$ is the smallest number of symbols to delete from $Y[j..n]$ so that $X[i..k]$ is not a subsequence of what remains, or $\infty$ if no deletions achieve that. We need $\textsf{MinDel}(1,1)$; the longest subsequence of $Y$ that is not a supersequence of $X$ has length $n - \textsf{MinDel}(1,1)$.
> $$
> \textsf{MinDel}(i,j) = \begin{cases}
> \infty & \text{if } i > k\\
> 0 & \text{if } i\le k \text{ and } j > n\\
> \textsf{MinDel}(i, j+1) & \text{if } X[i] \ne Y[j]\\
> \min\{1 + \textsf{MinDel}(i, j+1),\ \textsf{MinDel}(i+1, j+1)\} & \text{if } X[i] = Y[j]
> \end{cases}
> $$
>
> **Base cases.** An empty $X[i..k]$ is a subsequence of everything, so it cannot be destroyed. A nonempty one is not a subsequence of the empty remainder of $Y$, so nothing more needs deleting.
>
> **Recursive cases.** Let $y$ be a symbol and $Z$ a sequence. By the greedy argument of (a): if $y = X[i]$, then $X[i..k]$ is a subsequence of $yZ$ if and only if $X[i+1..k]$ is a subsequence of $Z$; if $y \ne X[i]$, it is a subsequence of $yZ$ if and only if it is a subsequence of $Z$. Now decide $Y[j]$. Deleting it costs $1$ and leaves the subproblem $(i, j+1)$. Keeping it costs nothing and leaves $(i, j+1)$ if $Y[j]\ne X[i]$ — at least as good as deleting, so that branch is dropped — or $(i+1, j+1)$ if $Y[j] = X[i]$.
>
> **Example.** For `PPAP` in `PENPINEAPPLEAPPLEPEN` the answer is $2$. Deleting both copies of `A` works. One deletion is not enough: `PPAP` occurs at positions $1,4,8,14$ and, disjointly, at $9,10,13,18$, and one deletion hits at most one of the two copies.
>
> **Answer.** $\textsf{MinDel}(1,1)$ with the recurrence above.

## Exercise 2.6 — Optimal balanced binary search trees

> [!question] Exercise 2.6 (book p. 96)
> The input is a sorted array $A[1..n]$ of keys and an array $f[1..n]$ of frequencies, with the cost function of §2.8: $\sum_i f[i]\cdot(\text{number of ancestors of the node holding } A[i])$. Describe recursive backtracking algorithms that construct an optimal tree among those satisfying extra constraints. Don't analyze the running times.
>
> **(a)** **AVL trees:** at every node, the heights of the left and right subtrees differ by at most one.
>
> **(b)** **Red-black trees:** every node is red or black; every red node has a black parent; every root-to-leaf path contains the same number of black nodes.
>
> **(c)** **AA trees:** red-black trees in which no left child is red.

**The common idea.** Extend $\textsf{OptCost}(i,k)$ ([[2-algorithms/02-backtracking#28-optimal-binary-search-trees|§2.8]], [[concepts/optimal-binary-search-trees]]) with exactly the information the balance rule needs about a subtree: its height for AVL trees; its root color and black-height for red-black and AA trees. All three rules are local — they relate a node only to its children's heights or colors and black-heights — and the cost splits as in §2.8 into $F(i,k) := \sum_{t=i}^{k} f[t]$ plus the costs of the two subtrees. So once the root and the children's parameters are fixed, each subtree should be an optimal one for its keys and parameters. Computing the optimal cost is enough; to construct the tree, record the minimizing choice in each call and rebuild from the top. Conventions: the empty tree has height $0$ and black-height $0$ and counts as black; a "root-to-leaf path" ends at an empty subtree (a null pointer), as usual for red-black trees. (If a leaf meant a childless node, a path of black nodes would qualify.)

### (a) Optimal AVL tree

> [!hint]- Hint
> The subtrees of an AVL tree of height $h$ have heights $(h-1, h-1)$, $(h-1, h-2)$ or $(h-2, h-1)$, and both are AVL trees. Make the exact height a parameter.

> [!solution]- Solution
> **What the recursion computes.** $\textsf{OptAVL}(i,k,h)$ is the minimum cost of an AVL tree on the keys $A[i..k]$ with height exactly $h$, or $\infty$ if there is none. The answer is $\min_{0\le h\le n}\textsf{OptAVL}(1,n,h)$.
>
> **Base cases.** For the empty range ($i > k$): $0$ if $h = 0$, and $\infty$ otherwise. For a nonempty range and $h\le 0$: $\infty$.
>
> **Recursive case** ($i\le k$, $h\ge1$): try every root $r$ and every allowed pair of subtree heights,
> $$
> \textsf{OptAVL}(i,k,h) = F(i,k) + \min_{i\le r\le k}\ \min_{(h_L,h_R)}\big(\textsf{OptAVL}(i,r-1,h_L) + \textsf{OptAVL}(r+1,k,h_R)\big),
> $$
> where $(h_L,h_R)$ ranges over $(h-1,h-1)$, $(h-1,h-2)$, $(h-2,h-1)$.
>
> **Why.** A tree with root $A[r]$ and height $h$ is an AVL tree if and only if both subtrees are AVL trees, the taller one has height $h-1$, and the heights differ by at most one — exactly the three pairs. For fixed $r$, $h_L$ and $h_R$ the subtrees are independent, so each should be optimal for its keys and height. Every call has fewer keys than its caller, so the recursion ends.
>
> **Answer.** $\min_h \textsf{OptAVL}(1,n,h)$; memoizing the $O(n^3)$ triples $(i,k,h)$, with $O(n)$ work each, gives an $O(n^4)$-time dynamic program.

### (b) Optimal red-black tree

> [!hint]- Hint
> A red node's children must be black (or empty); a black node's children may have either color. The **black-height** — black nodes on each path from a node down to an empty subtree — must match in the two children. Use two functions, one per root color, with the black-height as a parameter.

> [!solution]- Solution
> **What the recursion computes.** For $b\ge 0$: $\textsf{Black}(i,k,b)$ is the minimum cost of a tree on $A[i..k]$ that is empty or has a black root, in which every red node has a black parent and every path from the root to an empty subtree contains exactly $b$ black nodes ($\infty$ if none exists). $\textsf{Red}(i,k,b)$ is the same with a red root (the root's own parent is checked by the caller), and $\textsf{Any}(i,k,b) = \min\{\textsf{Black}(i,k,b), \textsf{Red}(i,k,b)\}$.
>
> **Base cases.** Empty range: $\textsf{Black} = 0$ if $b = 0$ and $\infty$ otherwise; $\textsf{Red} = \infty$. Nonempty range with $b = 0$: $\textsf{Black} = \infty$.
>
> **Recursive cases** ($i\le k$):
> $$
> \textsf{Black}(i,k,b) = F(i,k) + \min_{i\le r\le k}\big(\textsf{Any}(i,r-1,b-1) + \textsf{Any}(r+1,k,b-1)\big)\qquad(b\ge1)
> $$
> $$
> \textsf{Red}(i,k,b) = F(i,k) + \min_{i\le r\le k}\big(\textsf{Black}(i,r-1,b) + \textsf{Black}(r+1,k,b)\big)
> $$
>
> **Answer of the whole problem.** $\min_{0\le b\le n}\textsf{Black}(1,n,b)$. The root must be black, because a red root has no black parent; allowing a red root would not change the optimum anyway, since recoloring the root black keeps every rule.
>
> **Why.** A subtree whose root has color $c$ satisfies both rules with black-height $b$ if and only if both child subtrees satisfy them with black-height $b-1$ (if $c$ is black) or $b$ (if $c$ is red), and, if $c$ is red, both children are black or empty. Given $r$, $c$ and $b$, the two children are independent, so each should be optimal. Every call that loops over roots works on fewer keys than its caller, so the recursion ends.
>
> **Answer.** $\min_b \textsf{Black}(1,n,b)$ with the two recurrences above.

### (c) Optimal AA tree

> [!hint]- Hint
> Same as (b), with one change: the left child of a black node must be black too. (The children of a red node are black already.)

> [!solution]- Solution
> **What the recursion computes.** $\textsf{Black}$, $\textsf{Red}$ and $\textsf{Any}$ as in (b), with "no left child is red" added to the rules. Base cases and $\textsf{Red}$ are unchanged; for a black root the left subtree must be empty or have a black root:
> $$
> \textsf{Black}(i,k,b) = F(i,k) + \min_{i\le r\le k}\big(\textsf{Black}(i,r-1,b-1) + \textsf{Any}(r+1,k,b-1)\big)\qquad(b\ge1)
> $$
> **Why.** The new rule only restricts the color of each left child, which is the root of the left subtree; the argument of (b) goes through unchanged.
>
> **Example.** For $f = (1,1,1,1,2,6)$ the four optima all differ: unconstrained $25$, red-black $26$, AVL $27$, AA $31$. The red-black optimum is never above the AVL optimum, because every AVL tree can be colored as a red-black tree (a standard fact), and never above the AA optimum, because every AA tree is a red-black tree. The AA rule is not symmetric: for $f = (8,4,2,1)$ the red-black and AA optima are both $27$, but for the mirror image $f = (1,2,4,8)$ they are $27$ and $28$.
>
> **Answer.** $\min_b \textsf{Black}(1,n,b)$ with the modified recurrence for $\textsf{Black}$.

### Sources for this page

Statements paraphrased from the Chapter 2 exercises of Jeff Erickson's *Algorithms* (pp. 93–96; CC BY 4.0), including the book's examples (ARTISTOIL, the BOTHEARTH/PINSTART pair, the chain for 374, PPAP). The solutions, the extra examples (dictionaries, the arrays and frequency vectors) and the remarks on greedy shortcuts are original. Every algorithm and recursive definition on this page is implemented as written and compared with brute force on all small inputs, and every number on the page is recomputed, by `tools/checks/a02x.py`.
