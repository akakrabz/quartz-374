---
title: "HW7 — more dynamic programming, worked through"
description: "Homework 7 (CS/ECE 374 A, Fall 2026) explained for someone new to dynamic programming: the recipe and the rubric in one page, then the longest common decreasing subsequence (anchor on the last element), the longest common palindromic subsequence (shrink two intervals from both ends), the largest orthogonally separable set of rectangles (the subproblem is a box, not a set), and broadcasting in a binary tree (a function on subtrees) — each built from the question 'what is a subproblem?' to a recurrence, an array, an order and a running time."
tags: [algorithms, dynamic-programming, homework]
---

*Homework 7 · Erickson, Algorithms, Chapter 3 (Dynamic Programming) · private: homework solutions stay off the public site*

> [!abstract] In one breath
> Every problem on this homework is solved the same way: name a function of a few integers (or of a tree node) whose value is the answer to a *smaller version* of the problem, say in English what it returns, write a recurrence by asking one question about an optimal solution, store the values in an array, fill it in an order where everything you need is already there, and count entries × work per entry. The four problems differ only in what the smaller version is: **a pair of prefixes** and the last element taken (1a), **a pair of intervals** shrinking from both ends (1b), **a box** of the plane (2), and **a subtree** (3). If you can say what the subproblem is, the rest is routine.

## 0. Dynamic programming, if you have only skimmed the notes

### What it is

A recursive algorithm that tries every possibility for *one* decision and recurses on what is left is called backtracking; it is correct but usually exponential, because it solves the same smaller problems again and again. **Dynamic programming is the same recursion with the answers written down**: if each recursive call can be named by a few small integers ("the prefix $A[1..i]$", "the interval $A[i..j]$"), there are only polynomially many different calls, so store each answer in an array the first time and never compute it twice. The whole art is choosing *what the call is named by* — the parameters.

### The recipe, and what each step is worth

| step | what you write | points |
|---|---|---|
| 1. the function | a **named** function with explicit parameters and **one or two English sentences saying what it returns**, in terms of those parameters only; then which call gives the final answer | 3 — and 0 for everything else if this is missing |
| 2. the recurrence | base cases and recursive cases, each with its condition | 4 (1 base, 3 recursive) |
| 3. memoization | the array the values live in, with its index ranges | 1 |
| 4. evaluation order | which entries are filled first; for nested loops, which loop is outer | 1 |
| 5. running time | (number of entries) × (time per entry), in the problem's own variables | 1 |

> [!trap] The three ways to get zero for the description
> - **Describing the algorithm instead of the function.** "We scan both arrays and keep the best so far" is *how*. The rubric wants *what the value is*: "$\textsf{Dec}(i,j)$ is the length of the longest … of $A[1..i]$ and $B[1..j]$ that ends with $B[j]$."
> - **A value that depends on hidden state.** "The current index", "the last element we kept", "the best so far" are not parameters. If the value needs it, make it a parameter.
> - **A lazy name.** A single letter, $\textsf{OPT}$ or $\textsf{memo}$ costs a point. Use $\textsf{Dec}$, $\textsf{Pal}$, $\textsf{Sep}$, $\textsf{Rounds}$.

> [!tip] How to find a recurrence: ask one question about an optimal solution
> Picture a best solution and ask about **one** of its decisions — "is the last element used?", "are the two endpoints matched?", "where is the first cut?", "which child gets the message first?". Each possible answer leaves a strictly smaller problem *of the same kind*, whose value the function gives you by definition. The recurrence is the best over all answers. If the leftover is *not* of the same kind, your function needs another parameter: that is the question "what do I need to remember?".

### The two solved problems on the handout are the models for this homework

- **Longest balanced subsequence** (handout Problem 4): the function $\textsf{LBS}(i,k)$ lives on an **interval** $A[i..k]$. The one question: are the two endpoints $A[i]$ and $A[k]$ matched to each other? If so, $2 + \textsf{LBS}(i+1,k-1)$; otherwise some cut $j$ splits the subsequence. Problem 1(b) below is the same move with *two* intervals.
- **The party** (Problem 5): two functions $\textsf{MaxFunYes}(v)$, $\textsf{MaxFunNo}(v)$ on **subtrees**, computed from the children's values in a postorder traversal — "memoization" is a field in each node, the "order" is children before parent, and the time is $O(1)$ per node. Problem 3 below is a tree function too.

Keep both solutions open while you write; copying their *format* is exactly what the rubric rewards.

## 1(a). Longest common decreasing subsequence

### What is a subproblem?

A common subsequence of $A$ and $B$ is a sequence of matches $(i_1, j_1), (i_2, j_2), \dots$ with $A[i_t] = B[j_t]$, both index sequences increasing. Decreasing means $A[i_1] > A[i_2] > \cdots$. Walk through the arrays from the left. To decide whether we may append a new match, we need to know **the value of the last match** — so the function must remember it. The cheapest way to remember a value is to remember a *position* that holds it: say which element of $B$ the subsequence ends with. That is the same trick as $\textsf{LISfirst}$ in the notes (§3.6), where "ends with $B[j]$" replaces "starts with $A[i]$".

> [!definition] The function
> For $0 \le i \le m$ and $1 \le j \le n$, let $\textsf{Dec}(i, j)$ be the **length of the longest common subsequence of $A[1..i]$ and $B[1..j]$ that is strictly decreasing and whose last element is $B[j]$** — that is, $B[j]$ is matched to some $A[i']$ with $i' \le i$ — or $0$ if there is no such subsequence.
>
> The answer is $\max_{1 \le j \le n} \textsf{Dec}(m, j)$ (or $0$ if $n = 0$): the longest such subsequence ends *somewhere*.

### The one question: is $A[i]$ the element matched with $B[j]$?

- If $A[i] \ne B[j]$, it cannot be; $B[j]$ is matched to an earlier $A[i']$, so the subsequence is a common subsequence of $A[1..i-1]$ and $B[1..j]$ ending with $B[j]$.
- If $A[i] = B[j]$, either it is not (same as above), or it is. If it is, everything before the last match is a strictly decreasing common subsequence of $A[1..i-1]$ and $B[1..j-1]$ that ends with some $B[k]$, $k < j$, with $B[k] > B[j]$ — or is empty.

$$
\textsf{Dec}(i, j) =
\begin{cases}
0 & \text{if } i = 0\\[2pt]
\textsf{Dec}(i-1, j) & \text{if } i \ge 1 \text{ and } A[i] \ne B[j]\\[2pt]
\max\Big\{\textsf{Dec}(i-1, j),\ \ 1 + \max\big\{\textsf{Dec}(i-1, k) \;\big\vert\; 1 \le k < j,\ B[k] > B[j]\big\}\Big\} & \text{if } i \ge 1 \text{ and } A[i] = B[j]
\end{cases}
$$

where the maximum of an empty set is $0$ (the new match starts the subsequence). The recurrence never *checks* that $B[k]$'s match in $A$ comes before $A[i]$ — it does not have to, because $\textsf{Dec}(i-1, k)$ only uses $A[1..i-1]$.

> [!note] Why the "$B[k] > B[j]$" condition is enough
> The subsequence is decreasing if and only if every element is smaller than the one before it, and the one before $B[j]$ is $B[k]$. Everything earlier is handled inside $\textsf{Dec}(i-1,k)$, by definition. (For *non-increasing* instead of strictly decreasing, change $>$ to $\ge$; nothing else moves.)

**Memoization:** a two-dimensional array $\textsf{Dec}[0..m][1..n]$.
**Evaluation order:** every entry in row $i$ uses only row $i-1$, so fill $i$ from $0$ up to $m$ (outer loop); within a row, $j$ in any order (say increasing).
**Time:** $(m+1)\,n$ entries; the inner maximum scans $k < j$, so $O(n)$ per entry: $O(mn^2)$ total.

> [!example] A small run
> $A = [5, 3, 4, 1, 2]$, $B = [3, 5, 4, 2, 1]$. The table $\textsf{Dec}[i][j]$, rows $i = 1..5$, columns $j = 1..5$:
>
> | | $B[1]=3$ | $B[2]=5$ | $B[3]=4$ | $B[4]=2$ | $B[5]=1$ |
> |---|---|---|---|---|---|
> | $A[1]=5$ | 0 | 1 | 0 | 0 | 0 |
> | $A[2]=3$ | 1 | 1 | 0 | 0 | 0 |
> | $A[3]=4$ | 1 | 1 | 2 | 0 | 0 |
> | $A[4]=1$ | 1 | 1 | 2 | 0 | 3 |
> | $A[5]=2$ | 1 | 1 | 2 | 3 | 3 |
>
> The answer is $3$ ($5, 4, 1$ or $5, 4, 2$). Entry $[4][5] = 3$: $A[4] = B[5] = 1$, and the best earlier ending with a larger value of $B[1..4]$ is $\textsf{Dec}[3][3] = 2$ (the subsequence $5, 4$).

> [!tip] Bonus: $O(mn)$ with one running maximum
> In row $i$ the condition inside the maximum is $B[k] > B[j] = A[i]$ — it does not depend on $j$. So scan $j$ from $1$ to $n$ keeping $\textit{best} = \max\{\textsf{Dec}[i-1][k] : k < j,\ B[k] > A[i]\}$, updated after each $j$ in $O(1)$. The entry becomes $\max\{\textsf{Dec}[i-1][j],\ 1 + \textit{best}\}$ when $A[i] = B[j]$. This is the $O(mn)$ "longest common increasing subsequence" algorithm turned upside down; the $O(mn^2)$ version already earns full credit.

> [!trap] Where 1(a) loses points
> - **Dropping the "ends with $B[j]$" part.** Without it, $\textsf{Dec}(i,j)$ would be "the longest decreasing common subsequence of the two prefixes" — and then you cannot tell whether a new match is allowed, because you do not know the last value. The decreasing constraint is what forces the extra information into the definition.
> - **Remembering the last *value* as a parameter.** Correct, but values can be arbitrary integers; the table would have to be indexed by a value, which is a hash table (no credit) or a third index of size $n$ ($O(mn^2)$ entries). A *position* in $B$ is the clean way.
> - **Three nested quantifiers in the description.** "$\textsf{Dec}(i,j)$ is the length of the longest common subsequence of $A[1..i]$ and $B[1..j]$ that is strictly decreasing and ends with $B[j]$" is one sentence; it is enough.

## 1(b). Longest common palindromic subsequence

### Start from one string

The longest palindromic subsequence of a single string is a classic interval recurrence (book Exercise 3.9(a), notes §3.9): $\textsf{LPS}(i,j)$ for the substring $A[i..j]$; if $A[i] = A[j]$ the two ends are matched and the middle is $\textsf{LPS}(i+1, j-1)$; otherwise drop one end. A palindrome is built **from the outside in**, so the subproblem shrinks from both ends — an interval, not a prefix.

With two strings, a common palindromic subsequence has a first character that appears in both $A$ and $B$, and a last character equal to it. Shrinking from the outside in on both strings at once gives **a pair of intervals**.

> [!definition] The function
> For $1 \le i \le m+1$, $i-1 \le j \le m$, $1 \le k \le n+1$, $k-1 \le l \le n$, let $\textsf{Pal}(i, j, k, l)$ be the **length of the longest string that is a palindrome and a subsequence of both $A[i..j]$ and $B[k..l]$** (an interval of each string; empty intervals allowed).
>
> The answer is $\textsf{Pal}(1, m, 1, n)$.

### The one question: are all four endpoints used?

Suppose $P$ is a longest common palindromic subsequence of $A[i..j]$ and $B[k..l]$, with $|P| \ge 2$. Its first and last characters are equal (palindrome). Two facts:

1. **If $A[i] = A[j] = B[k] = B[l] = c$, we may assume $P$ starts and ends with $c$, using all four endpoints.** If $P$ did not start with $c$, then $P$ uses only characters strictly inside both intervals, and $cPc$ would be a longer common palindromic subsequence — a contradiction. And if $P$ starts and ends with $c$, we may slide its first $c$ to position $i$ and its last $c$ to position $j$ in $A$ (and likewise to $k$, $l$ in $B$), because those positions hold $c$ and lie outside the rest of $P$. The middle of $P$ is then a common palindromic subsequence of $A[i+1..j-1]$ and $B[k+1..l-1]$.
2. **Otherwise $P$ avoids at least one of the four endpoint positions.** Using $A[i]$ and $A[j]$ both would force $A[i] = A[j]$ (first = last), using $B[k]$ and $B[l]$ would force $B[k] = B[l]$, and the first character is the same in both strings — so using all four forces all four equal. Hence $P$ is a common palindromic subsequence of one of the four instances with one endpoint removed.

$$
\textsf{Pal}(i,j,k,l) =
\begin{cases}
0 & \text{if } i > j \text{ or } k > l\\[2pt]
1 & \text{if } A[i] = A[j] = B[k] = B[l] \text{ and } (i = j \text{ or } k = l)\\[2pt]
2 + \textsf{Pal}(i+1, j-1, k+1, l-1) & \text{if } A[i] = A[j] = B[k] = B[l],\ i < j,\ k < l\\[2pt]
\max\big\{\textsf{Pal}(i+1,j,k,l),\ \textsf{Pal}(i,j-1,k,l),\ \textsf{Pal}(i,j,k+1,l),\ \textsf{Pal}(i,j,k,l-1)\big\} & \text{otherwise}
\end{cases}
$$

The second line is the one-character case: if one interval is a single character $c$ that also begins and ends the other interval, the best is the one-letter palindrome $c$ (you cannot use the same position twice).

**Memoization:** a four-dimensional array $\textsf{Pal}[1..m+1][0..m][1..n+1][0..n]$ (only entries with $j \ge i-1$ and $l \ge k-1$ are used).
**Evaluation order:** every case uses entries with a larger $i$, a smaller $j$, a larger $k$ or a smaller $l$ (or all four at once). So: $i$ from $m+1$ **down** to $1$ (outermost), then $j$ from $i-1$ up to $m$, then $k$ from $n+1$ down to $1$, then $l$ from $k-1$ up to $n$ (innermost). Equivalently, by increasing total length $(j-i+1) + (l-k+1)$.
**Time:** $O(m^2 n^2)$ entries, $O(1)$ each: $O(m^2 n^2)$.

> [!example] Checks
> $\textsf{Pal}(\texttt{BANANA}, \texttt{ANANAS}) = 5$ (ANANA). $\textsf{Pal}(\texttt{ABCBA}, \texttt{ACBCA}) = 3$ (ABA or ACA — not ABCBA, since in the second string no B comes after the C's B; not BCB either). $\textsf{Pal}(\texttt{AB}, \texttt{BA}) = 1$.

> [!trap] Where 1(b) loses points
> - **Only two parameters.** "$\textsf{Pal}(i, k)$ for the suffixes $A[i..m]$ and $B[k..n]$" cannot express "and the last character must match the first": a palindrome needs both ends, so both intervals need both ends.
> - **Taking the four-way match without the one-character line.** With $A = B = \texttt{A}$, "$2 + \textsf{Pal}(\text{empty})$" would return $2$ for a single letter.
> - **Writing $O(n^4)$.** The sizes are $m$ and $n$; the rubric expects $O(m^2 n^2)$.
> - **Trying to be clever with LCS.** The longest common subsequence of $A$ and $B$ need not contain the longest common *palindromic* subsequence, and the LPS of the LCS is not the answer either. Keep the four indices.

## 2. The largest orthogonally separable subset

### Read the definition as a recursion

A set is separable if it is tiny ($\le 1$ rectangle), or some vertical or horizontal line splits it into two non-empty separable halves. That is already a recursive structure: a separable set is a **tree of cuts**, like a guillotine partition. The question "what is a subproblem?" is answered by asking what a half looks like after a cut: it is a separable set of rectangles that all lie **inside a box** of the plane — left of the cut, right of the previous cut, and so on. So:

> [!key] The subproblem is a box, not a subset
> The exponentially many *subsets* of $S$ are not the subproblems. The subproblems are the $O(n^4)$ **boxes** $[x_1, x_2] \times [y_1, y_2]$ whose sides are input coordinates, and the question for each box is "how large a separable subset can be chosen among the rectangles that lie inside it?"

**Only input coordinates matter.** Sort the $2n$ x-coordinates $A[1..n] \cup C[1..n]$ into $X[1..2n]$ and the $2n$ y-coordinates into $Y[1..2n]$ (all distinct, by assumption). A rectangle $r$ lies inside the box $[X[a], X[b]] \times [Y[c], Y[d]]$ if $X[a] \le A[r]$, $C[r] \le X[b]$, $Y[c] \le B[r]$ and $D[r] \le Y[d]$. If a vertical line $x = \ell$ separates $S_1$ (left) from $S_2$ (right), then so does the line through $\max_{r \in S_1} C[r]$, the right edge of the rightmost rectangle of $S_1$ — after nudging it by a hair to the right, which is harmless because no rectangle of $S_2$ starts there (the coordinates are distinct). So cuts can be restricted to the coordinates in $X$ and $Y$.

> [!definition] The function
> For $1 \le a < b \le 2n$ and $1 \le c < d \le 2n$, let $\textsf{Sep}(a, b, c, d)$ be the **maximum size of an orthogonally separable subset of the rectangles of $S$ that lie entirely inside the box $[X[a], X[b]] \times [Y[c], Y[d]]$**.
>
> The answer is $\textsf{Sep}(1, 2n, 1, 2n)$: every rectangle lies inside the box spanned by the extreme coordinates. (If $n = 0$ the answer is $0$.)

### The one question: what is the first cut?

A best separable subset $T$ of the rectangles in the box has size $0$, size $1$, or at least $2$. If at least $2$, by definition some vertical or horizontal line splits $T$ into non-empty separable $T_1$ and $T_2$; as shown above the line can be taken at a coordinate $X[e]$ with $a < e < b$ (or $Y[f]$, $c < f < d$), and then $T_1$ lies inside the left (lower) sub-box and $T_2$ inside the right (upper) one. Conversely, any separable subset of the left sub-box plus any separable subset of the right sub-box is a separable subset of the box — the two parts are disjoint (a rectangle cannot be on both sides of a line), and the line $x = X[e]$, nudged, separates them. So:

$$
\textsf{Sep}(a, b, c, d) = \max
\begin{cases}
1 & \text{if some rectangle lies inside the box, else } 0\\[2pt]
\textsf{Sep}(a, e, c, d) + \textsf{Sep}(e, b, c, d) & \text{for each } e \text{ with } a < e < b\\[2pt]
\textsf{Sep}(a, b, c, f) + \textsf{Sep}(a, b, f, d) & \text{for each } f \text{ with } c < f < d
\end{cases}
$$

No separate base case is needed: a box with no interior coordinate ($b = a+1$ and $d = c+1$) has no cuts to try, and it contains at most one rectangle (a rectangle inside it would have $A[r] = X[a]$ and $C[r] = X[b]$, which pins it down since coordinates are distinct), so the first line gives the right value. Allowing a cut with an empty side is harmless too: the sum is then the value of a smaller box, which is a legal separable subset of the big box.

**Memoization:** a four-dimensional array $\textsf{Sep}[1..2n][1..2n][1..2n][1..2n]$, of which the $O(n^4)$ entries with $a < b$, $c < d$ are used.
**Evaluation order:** each cut uses a box that is strictly narrower (same height) or strictly shorter (same width). So loop over the width $w = b - a$ from $1$ up to $2n-1$ (outer), the height $h = d - c$ from $1$ up (next), and inside, over all $a$ and $c$ — equivalently, by increasing $w + h$.
**Time:** $O(n^4)$ entries. Each tries $O(n)$ vertical and $O(n)$ horizontal cuts, and the "does the box contain a rectangle" test scans the $n$ rectangles: $O(n)$ per entry, so **$O(n^5)$** total.

> [!example] A check
> Rectangles $(1,1)$–$(3,3)$, $(4,2)$–$(6,5)$, $(2,4)$–$(5,7)$ and $(7,1)$–$(9,8)$: the first two are separated by $x = 3.5$, the fourth by $x = 6.5$, but the third overlaps the x-range *and* the y-range of each of the first two, so no line separates it from both. The answer is $3$. Two rectangles that cross each other (a plus sign) are not separable at all: the answer for a plus sign and one more rectangle is $2$.

> [!trap] Where Problem 2 loses points
> - **A function on subsets** ("$\textsf{Sep}(T)$ for a subset $T$ of $S$"). There are $2^n$ of them; the array does not exist. The box is what makes the number of subproblems polynomial.
> - **A function on one axis only** ("rectangles with $x$ between $X[a]$ and $X[b]$"). After a horizontal cut the two halves are constrained in $y$; without $c, d$ the two halves cannot be told apart.
> - **Forgetting that the box may hold at most one rectangle**, or forgetting the "$1$ if non-empty" option: a box with a single rectangle and no useful cut must still return $1$.
> - **Cuts at arbitrary real numbers.** Say explicitly that cuts are taken at input coordinates, and why (the nudging argument). It is one sentence and it is what makes the recurrence finite.
> - **Running time in $O(n^4)$.** Entries are $O(n^4)$; each costs $O(n)$. (Precomputing "box contains a rectangle" for all boxes does not help the bound, since the cuts already cost $O(n)$.)

## 3. Broadcasting in a binary tree (practice only)

### A function on subtrees

As in the party problem, the natural subproblem is a subtree: once a node $v$ knows the message, informing $v$'s subtree is a problem of the same kind, independent of the rest of the tree, because messages only travel downward.

> [!definition] The function
> For each node $v$ of $T$, let $\textsf{Rounds}(v)$ be the **minimum number of rounds needed to deliver the message to every node in the subtree of $v$, given that $v$ already knows it** at the start.
>
> The answer is $\textsf{Rounds}(\textit{root})$.

### The one question: which child does $v$ tell first?

Node $v$ can inform at most one child per round, so with two children it tells one of them in round 1 and the other in round 2 (there is no reason to wait). A child $w$ informed in round $t$ finishes its own subtree in round $t + \textsf{Rounds}(w)$, and all subtrees work in parallel.

$$
\textsf{Rounds}(v) =
\begin{cases}
0 & \text{if } v \text{ is a leaf}\\[2pt]
1 + \textsf{Rounds}(w) & \text{if } v \text{ has exactly one child } w\\[2pt]
\min\Big\{\max\{1 + \textsf{Rounds}(w_1),\ 2 + \textsf{Rounds}(w_2)\},\ \ \max\{1 + \textsf{Rounds}(w_2),\ 2 + \textsf{Rounds}(w_1)\}\Big\} & \text{if } v \text{ has children } w_1, w_2
\end{cases}
$$

The $\min$ is over the two orders; the $\max$ is the round in which the later of the two subtrees finishes. (Greedy intuition — "tell the child with the bigger subtree-time first" — is right, and the two-way $\min$ simplifies to $\max\{1 + \max(r_1, r_2),\ 2 + \min(r_1, r_2)\}$; but writing the $\min$ over both orders costs nothing and needs no proof, while an unproved greedy rule costs 1½ points.)

**Memoization:** a field $v.\textit{rounds}$ in each node.
**Evaluation order:** children before parents — a postorder traversal.
**Time:** $O(1)$ per node, $O(n)$ total.

> [!example] Checks
> The handout's tree takes $5$ rounds. A path of $7$ nodes takes $6$ (one new node per round); a complete binary tree with $7$ nodes takes $4$: round 1 and 2 inform the two children, rounds 2–3 and 3–4 their leaves.

> [!tip] If the tree were not binary
> With $k$ children, the question becomes "in what order?", and the greedy answer — decreasing $\textsf{Rounds}(w)$ — needs a short exchange argument: $\textsf{Rounds}(v) = \max_{t} \big(t + \textsf{Rounds}(w_{(t)})\big)$ where $w_{(1)}, w_{(2)}, \dots$ are the children sorted by decreasing $\textsf{Rounds}$. Sorting makes it $O(n \log n)$ overall. For a binary tree the $\min$ over two orders avoids the proof.

## Checklist before you submit

1. Every function has a **name**, explicit **parameters**, and an English sentence of the form "is the (length / size / number) of the (best thing) for (which part of the input)".
2. The **final answer** is stated as a call (or a max over calls) of that function.
3. The recurrence has its **base cases** and every recursive case has its **condition**; empty maxima are given a value.
4. The **array**, its **index ranges**, the **loop order** (which loop is outer and in which direction), and the **time** as entries × work per entry, in the problem's variables ($m, n$ for Problem 1; $n$ for Problems 2 and 3).

### Sources for this page

Problem statements, the standard dynamic programming rubric and the two solved problems are from the CS/ECE 374 A Fall 2026 Homework 7 handout; the method follows Erickson, *Algorithms*, Chapter 3. Every recurrence on this page was implemented exactly as written and compared with brute force on random small inputs: 1(a) and its $O(mn)$ variant against all subsequences (2,160 pairs of arrays), 1(b) in both memoized and nested-loop form against all subsequences (1,960 pairs of strings), Problem 2 against all subsets with the separability definition applied literally (108 random inputs with $n \le 5$), and Problem 3 against a breadth-first search over all broadcast schedules (300 random binary trees); every example answer above is reproduced by the checks.
