---
title: "Chapter 12 exercises — NP-hardness"
description: "Solutions to Exercises 12.1–12.4, 12.6, 12.7(b)(c), 12.8, 12.10, 12.16, 12.22(a)(b), 12.26, 12.34 and 12.38 of Erickson's Algorithms: why pseudo-polynomial time, a reduction in the wrong direction, an exponential conversion and an easy variant do not prove P = NP; polynomial algorithms for Partition with small numbers, BoxDepth, DNF-Sat, AllOrNothing3Sat, 2Partition, 2Color, 2Sat and domino lines; and NP-hardness proofs in the rubric's format for 12Color, 12Sat, undirected Hamiltonian cycle, Hamiltonian path versus cycle, six padded graph problems, domino cycles, dominating set, a stone puzzle and three-team splits."
tags: [exercises, algorithms, complexity]
---

*Solved exercises for [[2-algorithms/12-np-hardness|Chapter 12]] · book pp. 415–428 · statements paraphrased; see the book for the originals*

These are Exercises 12.1–12.4, 12.6, 12.7(b)(c), 12.8, 12.10, 12.16, 12.22(a)(b), 12.26, 12.34 and 12.38, chosen to cover the three kinds of question the final asks about this chapter: an NP-hardness proof by reduction, "polynomial or NP-hard?" for a variant of a hard problem, and the conceptual point behind a fake proof that P = NP. Skipped: the exercises marked ♥ (12.11(c)(d), 12.14, 12.15, 12.21, 12.22(c), 12.35(c)) and ♣ (12.5(f), 12.40, 12.41, which need outside material); 12.5, which turns decision algorithms into search algorithms, a different skill; 12.7(a), which needs 3Partition (not among the problems the lectures prove hard) and a padding argument to keep the numbers distinct; 12.9, a repeat of 12.8(a)(b); and the rest of the list, much of which reuses a gadget from this page — 12.25(c) is 12.16(d), and 12.39 (the longest line of acquaintances) falls to the Hamiltonian-path argument of 12.16(a). Every NP-hardness proof is written the way the [[0-toolkit/06-how-exams-are-graded#14-np-hardness|NP-hardness rubric]] grades it ([[concepts/polynomial-time-reductions]]): **the known NP-hard problem** $X$; **the reduction**, an algorithm that takes an arbitrary instance of $X$ and builds an instance of the new problem, with its size; **⇒**, a YES instance of $X$ becomes a YES instance; **⇐**, if the built instance is a YES instance, so was the instance of $X$; and the words **polynomial time**. Several reductions need a special case for tiny inputs; each is pointed out where it occurs. Write your own answer before opening a solution.

> [!tip] Known NP-hard problems and conventions used below
> - **Proved NP-hard in the chapter** ([[concepts/np-hardness]]): CircuitSat ([[concepts/cook-levin-theorem|Cook–Levin]]), Sat and 3Sat ([[2-algorithms/12-np-hardness#126-3sat-from-circuitsat|§12.6]], [[concepts/satisfiability]]); MaxIndSet ([[2-algorithms/12-np-hardness#127-maximum-independent-set-from-3sat|§12.7]]), MaxClique and VertexCover ([[2-algorithms/12-np-hardness#129-clique-and-vertex-cover-from-independent-set|§12.9]], [[concepts/independent-set]]); 3Color ([[2-algorithms/12-np-hardness#1210-graph-coloring-from-3sat|§12.10]], [[concepts/graph-coloring]]); directed HamiltonianCycle and HamiltonianPath ([[2-algorithms/12-np-hardness#1211-hamiltonian-cycle|§12.11]]) and their undirected versions (Exercises 12.8 and 12.10 below; [[concepts/hamiltonian-cycle]]); SubsetSum ([[2-algorithms/12-np-hardness#1212-subset-sum-from-vertex-cover|§12.12]]). Partition, 3Partition, Max2Sat and the others are listed as NP-hard, without proofs, in [[2-algorithms/12-np-hardness#1213-other-useful-np-hard-problems|§12.13]].
> - **Decision versions.** IndependentSet$(G, k)$: is there an independent set of size at least $k$? VertexCover$(G, k)$: is there a vertex cover of size at most $k$? An algorithm for an optimization problem ("what is the size of the largest …?") answers the decision question by one comparison, so proving the decision version hard proves the optimization version hard.
> - **Graphs** are simple (no loops, no parallel edges); $n = \lvert V\rvert$, and running times are written $O(V + E)$ as in the book. A Hamiltonian cycle in an undirected graph has at least 3 vertices; in a directed graph, at least 2 ($u\to v\to u$ counts). A literal is a variable $x$ or its negation $\bar x$.
> - **The direction rule** ([[2-algorithms/12-np-hardness#125-reductions-and-sat|§12.5]]): to prove $Y$ NP-hard, reduce a known NP-hard problem **to** $Y$.

## Exercise 12.1 — Partition in pseudo-polynomial time

> [!question] Exercise 12.1 (book p. 415)
> **Partition**: given a set $S$ of $n$ integers, can $S$ be split into two disjoint sets $A$ and $B$, $A\cup B = S$, with equal sums?
>
> (a) Describe and analyze an algorithm that solves Partition in $O(nM)$ time, where $M = \sum_{s\in S}\lvert s\rvert$.
>
> (b) Why doesn't this algorithm imply that P = NP?

### (a) An O(nM) dynamic program

> [!hint]- Hint
> It is subset sum ([[concepts/subset-sum]]) with target half the total. Negative elements are allowed, so the reachable sums lie anywhere in $[-M, M]$.

> [!solution]- Solution
> Number the elements $s_1, \dots, s_n$ and let $\Sigma = s_1 + \cdots + s_n$. If $\Sigma$ is odd, answer False. Otherwise $S$ can be split iff some subset sums to $\Sigma/2$: its complement then sums to $\Sigma/2$ too.
>
> **Function.** For $0\le i\le n$ and $-M\le t\le M$, let $\mathit{CanReach}(i, t)$ be True if and only if some subset of the prefix $\{s_1,\dots,s_i\}$ sums to exactly $t$. Every subset sum lies in $[-M, M]$. The answer is $\mathit{CanReach}(n, \Sigma/2)$.
>
> **Recurrence.** Either $s_i$ is left out or it is used:
>
> $$
> \mathit{CanReach}(i, t) = \begin{cases} [\,t = 0\,] & \text{if } i = 0,\\ \mathit{CanReach}(i-1, t)\ \lor\ \mathit{CanReach}(i-1, t - s_i) & \text{if } i\ge 1,\end{cases}
> $$
>
> where a term with $t - s_i$ outside $[-M, M]$ is False.
>
> **Memoization.** A boolean array $\mathit{CanReach}[0..n, -M..M]$ (shift the second index by $M$).
>
> **Evaluation order.** $i$ from $0$ to $n$ in the outer loop; $t$ in any order in the inner loop.
>
> **Time.** $(n+1)(2M+1)$ entries, $O(1)$ each: $O(nM)$.
>
> **Answer.** If $\Sigma$ is even, fill $\mathit{CanReach}(i, t)$ (some subset of the first $i$ elements sums to $t$) and return $\mathit{CanReach}(n, \Sigma/2)$; otherwise return False. $O(nM)$ time.

### (b) Why this does not prove P = NP

> [!hint]- Hint
> How many bits does the input take? How large can $M$ be in terms of that?

> [!solution]- Solution
> "Polynomial time" means polynomial in the **input size**, the number of bits needed to write the input. The $n$ numbers take about $\sum_i\log_2\lvert s_i\rvert\le n\log_2 M$ bits, so $M$ can be exponentially larger than the input. Example: the $n$ numbers $s_i = 2^{n-1} + i$ for $0\le i<n$ have $n$ bits each, so the input has $b = n^2$ bits, but $M\ge n\,2^{n-1}$, and the table has $(n+1)(2M+1) > 2^n = 2^{\sqrt b}$ entries — not polynomial in $b$.
>
> A running time that is polynomial in the numeric values but not in their lengths is **pseudo-polynomial**; the chapter's "Caveat reductor" in [[2-algorithms/12-np-hardness#1212-subset-sum-from-vertex-cover|§12.12]] makes the same point for subset sum. Partition is NP-hard only when its numbers are long — it is **weakly NP-hard** — and the reductions that prove it hard produce exponentially large numbers.
>
> **Answer.** $O(nM)$ is exponential in the input size, because $M$ can be exponential in the number of bits of the numbers: the algorithm is pseudo-polynomial, not polynomial.

## Exercise 12.2 — BoxDepth

> [!question] Exercise 12.2 (book p. 415)
> **BoxDepth**: given $n$ axis-aligned rectangles in the plane, what is the largest number of them that contain a common point?
>
> (a) Describe a polynomial-time reduction from BoxDepth to MaxClique.
>
> (b) Describe and analyze a polynomial-time algorithm for BoxDepth. (The book: $O(n^3)$ time should be easy; $O(n\log n)$ is possible.)
>
> (c) Why don't these two results imply that P = NP?

Take the rectangles closed: $R_i = [\ell_i, r_i]\times[b_i, t_i]$.

### (a) Reduction to MaxClique

> [!hint]- Hint
> One vertex per rectangle. When do pairwise intersecting intervals on a line share a point?

> [!solution]- Solution
> **Reduction.** Build the **intersection graph** $G$: one vertex per rectangle, and an edge $ij$ whenever $R_i\cap R_j\ne\varnothing$, that is, $\max(\ell_i,\ell_j)\le\min(r_i,r_j)$ and $\max(b_i,b_j)\le\min(t_i,t_j)$. This takes $O(n^2)$ time. Return the size of the largest clique of $G$, computed by the MaxClique black box.
>
> **Claim.** A set $K$ of rectangles has a common point if and only if $K$ is a clique of $G$.
>
> - *Only if.* Rectangles that share a point intersect pairwise.
> - *If.* Let $\ell^* = \max_{k\in K}\ell_k$, attained by $R_i$, and $r^* = \min_{k\in K} r_k$, attained by $R_j$. Since $R_i$ and $R_j$ intersect, $\ell_i\le r_j$, so $\ell^*\le r^*$, and $\ell_k\le\ell^*\le r^*\le r_k$ for every $k\in K$: the line $x = \ell^*$ meets every rectangle of $K$. The same argument in $y$ shows $b^* = \max_{k\in K} b_k$ lies in every $[b_k, t_k]$. So $(\ell^*, b^*)$ lies in every rectangle of $K$. (This is the Helly property of intervals, used once per coordinate.)
>
> So the largest clique of $G$ has exactly BoxDepth vertices.
>
> **Answer.** Build the intersection graph in $O(n^2)$ time; BoxDepth equals the size of its largest clique.

### (b) An O(n³) algorithm

> [!hint]- Hint
> The proof of (a) names a common point explicitly. Where can it lie?

> [!solution]- Solution
> By the proof of (a), if some rectangles share a point, they share the point $(\max\ell, \max b)$ taken over those rectangles: its $x$-coordinate is the left edge of one input rectangle and its $y$-coordinate the bottom edge of one. So it suffices to try the $n^2$ **candidate points** $(\ell_i, b_j)$ for all $i, j$, count for each the rectangles that contain it in $O(n)$ time, and return the largest count (0 if $n = 0$).
>
> **Time.** $n^2$ candidates $\times$ $O(n)$: $O(n^3)$. (The book's $O(n\log n)$ needs a sweep with a balanced tree, beyond what is needed here.)
>
> **Answer.** Maximize, over the $n^2$ points $(\ell_i, b_j)$, the number of rectangles containing the point: $O(n^3)$ time.

### (c) Why this does not prove P = NP

> [!hint]- Hint
> Which problem did (a) solve, and with which black box?

> [!solution]- Solution
> The reduction in (a) goes **from** BoxDepth **to** MaxClique: it shows that BoxDepth is no harder than MaxClique, since an algorithm for MaxClique would solve BoxDepth. Part (b) shows BoxDepth is easy. Neither says anything about solving MaxClique quickly. Intersection graphs of rectangles are very special graphs, and an arbitrary graph is not one of them, so a BoxDepth algorithm cannot be run on an arbitrary MaxClique instance. To conclude P = NP we would need a polynomial-time reduction in the other direction, from MaxClique (or any NP-hard problem) **to** BoxDepth.
>
> **Answer.** The reduction points the wrong way: "BoxDepth reduces to MaxClique" and "BoxDepth is in P" are both consistent with MaxClique being hard.

## Exercise 12.3 — DNF-Sat

> [!question] Exercise 12.3 (book p. 416)
> A formula is in **disjunctive normal form** (DNF) if it is an Or of **terms**, each the And of one or more literals, such as $(\bar x\wedge y\wedge\bar z)\vee(y\wedge z)\vee(x\wedge\bar y\wedge\bar z)$. **DNF-Sat** asks whether a given DNF formula is satisfiable.
>
> (a) Describe a polynomial-time algorithm for DNF-Sat.
>
> (b) What is wrong with this argument that P = NP? *"Given a CNF formula with at most three literals per clause, use the distributive law to build an equivalent DNF formula — for example $(x\vee y\vee\bar z)\wedge(\bar x\vee\bar y)\iff(x\wedge\bar y)\vee(y\wedge\bar x)\vee(\bar z\wedge\bar x)\vee(\bar z\wedge\bar y)$ — and run (a) on it. That solves 3Sat in polynomial time; 3Sat is NP-hard, so P = NP."*

### (a) A linear-time algorithm

> [!solution]- Solution
> A DNF formula is true if and only if one of its terms is true, and a term, an And of literals, can be made true if and only if it does not contain a variable together with its negation: set each of its literals True. So scan the terms one at a time, marking each variable's sign in an array as it appears; return True as soon as a term has no variable with both signs, and False if every term has one. Unmarking a term's variables after scanning it keeps the total time linear.
>
> **Answer.** Satisfiable if and only if some term contains no complementary pair $x$, $\bar x$: $O(\text{length of the formula})$ time.

### (b) The error

> [!hint]- Hint
> How many terms does the distributive law produce from $k$ clauses of three literals?

> [!solution]- Solution
> Distributing produces one term for every way of choosing one literal from each clause: $k$ clauses of three literals give up to $3^k$ terms. The conversion takes exponential time and produces an exponentially long formula, and an algorithm that is polynomial in the size of *that* formula is exponential in the size of the original. The step "construct an equivalent DNF formula" is not a polynomial-time reduction from 3Sat to DNF-Sat.
>
> This is not an artifact of the distributive law: some formulas have no short DNF at all. For $\Phi_k = (x_1\vee y_1\vee z_1)\wedge\cdots\wedge(x_k\vee y_k\vee z_k)$, every equivalent DNF formula has at least $3^k$ terms. Call an assignment **minimal** if it makes exactly one literal of each clause true; there are $3^k$ of them. Each must make some term true. If one term $T$ were true at two minimal assignments $\alpha\ne\beta$, it would also be true at the assignment $\alpha\wedge\beta$ (a variable is true iff it is true in both): a positive literal of $T$ is true in both, hence in $\alpha\wedge\beta$; a negated literal's variable is false in both, hence in $\alpha\wedge\beta$. But in a clause where $\alpha$ and $\beta$ chose different literals, $\alpha\wedge\beta$ makes all three false, so $T$ would be true where $\Phi_k$ is false. So distinct minimal assignments need distinct terms.
>
> **Answer.** The distributive law blows a CNF formula with $k$ clauses up to as many as $3^k$ terms (for $\Phi_k$, every equivalent DNF needs $3^k$), so the "reduction" takes exponential time.

## Exercise 12.4 — AllOrNothing3Sat

> [!question] Exercise 12.4 (book p. 416)
> **AllOrNothing3Sat**: given a 3CNF formula, is there an assignment under which every clause has either three True literals or three False literals?
>
> (a) Describe a polynomial-time algorithm for AllOrNothing3Sat.
>
> (b) But 3Sat is NP-hard! Why doesn't the existence of this algorithm prove that P = NP?

### (a) Equal literals and components

> [!hint]- Hint
> A clause is all-or-nothing exactly when its three literals are equal. Equalities between literals are a graph problem.

> [!solution]- Solution
> **Graph.** An undirected graph $H$ with one vertex per literal ($x_1, \bar x_1, \dots, x_N, \bar x_N$). For each clause $(\ell_1\vee\ell_2\vee\ell_3)$, add the edges $\ell_1\ell_2$ and $\ell_2\ell_3$ and also the **complementary edges** $\bar\ell_1\bar\ell_2$ and $\bar\ell_2\bar\ell_3$ (two literals are equal exactly when their negations are).
>
> **Algorithm.** Compute the components of $H$ by [[concepts/whatever-first-search|whatever-first search]]. Answer True if and only if no variable $x$ has $x$ and $\bar x$ in the same component.
>
> **Correctness.**
>
> - If a good assignment exists, every edge joins two literals with equal values, so every component is constant; $x$ and $\bar x$ have different values, so they lie in different components.
> - Conversely, suppose no component contains a pair $x$, $\bar x$. Negating every literal maps edges to edges (every edge was added together with its complement), so it maps each component $K$ onto a component $\bar K$; and $\bar K\ne K$, since otherwise $K$ would contain some $\ell$ and $\bar\ell$. For each pair $\{K,\bar K\}$, make the literals of $K$ True and those of $\bar K$ False. This is a consistent assignment ($x$ and $\bar x$ always lie in complementary components), and the three literals of each clause lie in one component, so they are equal.
>
> **Time.** $2N$ vertices and $4k$ edges for $N$ variables and $k$ clauses: $O(N + k)$.
>
> **Answer.** Join the literals each clause forces to be equal (and their negations); satisfiable if and only if no $x$, $\bar x$ share a component. $O(N + k)$ time.

### (b) Why this does not prove P = NP

> [!solution]- Solution
> AllOrNothing3Sat is a different problem on the same inputs, with different answers: $(x\vee\bar x\vee y)$ is satisfiable, but no assignment makes $x$ and $\bar x$ equal. An algorithm for one problem tells us nothing about another unless there is a polynomial-time reduction from the other to it. To get P = NP we would need a polynomial-time reduction **from** 3Sat **to** AllOrNothing3Sat — and since AllOrNothing3Sat is in P, finding one would itself prove P = NP.
>
> **Answer.** Solving a variant of 3Sat is not solving 3Sat; hardness transfers only through a reduction from the hard problem, and none is known here.

## Exercise 12.6 — Two is easy

> [!question] Exercise 12.6 (book p. 417)
> "There's something special about the number 3." Describe and analyze polynomial-time algorithms for:
>
> (a) **2Partition**: can a set $S$ of $2n$ positive integers be split into $n$ disjoint pairs whose sums are all equal?
>
> (b) **2Color**: does an undirected graph $G$ have a proper coloring with two colors?
>
> (c) **2Sat**: does a CNF formula $\Phi$ with exactly two literals per clause have a satisfying assignment? *(Hint: this problem is strongly connected to an earlier chapter.)*

The three-element versions are NP-hard: 3Partition ([[2-algorithms/12-np-hardness#1213-other-useful-np-hard-problems|§12.13]]), 3Color ([[2-algorithms/12-np-hardness#1210-graph-coloring-from-3sat|§12.10]]) and 3Sat ([[2-algorithms/12-np-hardness#126-3sat-from-circuitsat|§12.6]]).

### (a) 2Partition

> [!hint]- Hint
> Whom must the smallest number be paired with?

> [!solution]- Solution
> **Algorithm.** Sort: $a_1 < a_2 < \cdots < a_{2n}$. Answer True if and only if all $n$ sums $a_i + a_{2n+1-i}$, $1\le i\le n$, are equal. $O(n\log n)$ time.
>
> **Correctness.** If the sums are equal, these pairs are a solution. Conversely, take any solution, with common pair sum $t$. The smallest number $a_1$ is paired with $t - a_1$, and the largest $a_{2n}$ with $t - a_{2n}$. Since $t - a_{2n}\ge a_1$, we get $a_{2n}\le t - a_1\le a_{2n}$, so $t - a_1 = a_{2n}$: the solution pairs $a_1$ with $a_{2n}$. Removing these two numbers leaves a solution for the other $2n-2$, so by induction it pairs $a_2$ with $a_{2n-1}$, and so on. All the sums $a_i + a_{2n+1-i}$ equal $t$.
>
> **Answer.** Sort and pair the $i$th smallest with the $i$th largest; YES if and only if all pair sums are equal. $O(n\log n)$ time.

### (b) 2Color

> [!solution]- Solution
> **Algorithm.** In each component, run whatever-first search from any vertex, give the start color 0, and give each newly reached vertex the color opposite to its parent's. Then check every edge; answer True if and only if no edge has two equal colors. $O(V + E)$ time.
>
> **Correctness.** In a connected graph, once the start's color is fixed, every proper 2-coloring is forced along the search tree's paths, so it equals the search's coloring. If that coloring fails on some edge, no proper 2-coloring exists. (Equivalently, $G$ is 2-colorable iff it is bipartite iff it has no odd cycle: [[2-algorithms/05-basic-graph-algorithms-exercises#exercise-53--bipartite-graphs|Exercise 5.3]].)
>
> **Answer.** Color by alternating along a whatever-first search tree and check the edges: $O(V + E)$ time.

### (c) 2Sat

> [!hint]- Hint
> The clause $(a\vee b)$ says "if $a$ is false then $b$ is true" and "if $b$ is false then $a$ is true". Draw these implications as a directed graph and look at its strong components.

> [!solution]- Solution
> **Graph.** The **implication graph**, a **directed** graph with one vertex per literal ($2N$ vertices) and, for every clause $(a\vee b)$, the two edges $\bar a\to b$ and $\bar b\to a$.
>
> **Algorithm.** Compute the [[concepts/strongly-connected-components|strong components]] in $O(V+E)$ time ([[2-algorithms/06-depth-first-search#66-strong-components-in-linear-time|§6.6]]) and number them in a topological order of the component dag, $\mathit{pos}(\ell)$ being the number of $\ell$'s component. If some $x$ and $\bar x$ share a component, answer False. Otherwise answer True; a satisfying assignment sets $x$ True if and only if $\mathit{pos}(x) > \mathit{pos}(\bar x)$. With this rule, *every* literal $\ell$ (positive or negative) is True if and only if $\mathit{pos}(\ell) > \mathit{pos}(\bar\ell)$.
>
> **Correctness.**
>
> - *A shared component means unsatisfiable.* Every edge is an implication that holds in every satisfying assignment, and implications chain along paths. If $x$ and $\bar x$ share a component, then $x$ implies $\bar x$ and $\bar x$ implies $x$, which no value of $x$ satisfies.
> - *Otherwise the rule works.* Suppose a clause $(a\vee b)$ were false: $a$ and $b$ False, so $\mathit{pos}(a) < \mathit{pos}(\bar a)$ and $\mathit{pos}(b) < \mathit{pos}(\bar b)$. The edges $\bar a\to b$ and $\bar b\to a$ never go backward in the topological order: $\mathit{pos}(\bar a)\le\mathit{pos}(b)$ and $\mathit{pos}(\bar b)\le\mathit{pos}(a)$. Then $\mathit{pos}(a) < \mathit{pos}(\bar a)\le\mathit{pos}(b) < \mathit{pos}(\bar b)\le\mathit{pos}(a)$, a contradiction.
>
> **Time.** $2N$ vertices and $2k$ edges: $O(N + k)$.
>
> **Answer.** Satisfiable if and only if no variable shares a strong component of the implication graph with its negation; then set $x$ True iff its component comes after $\bar x$'s in topological order. $O(N + k)$ time.

## Exercise 12.7 — Twelve is as hard as three

> [!question] Exercise 12.7(b)(c) (book p. 418)
> "There's nothing special about the number 3."
>
> (b) **12Color**: can the vertices of a given graph be colored with twelve colors so that every edge has two different colors? Prove that 12Color is NP-hard. *(Hint: reduce from 3Color.)*
>
> (c) **12Sat**: given a CNF formula with exactly twelve literals per clause, is it satisfiable? Prove that 12Sat is NP-hard. *(Hint: reduce from 3Sat.)*

### (b) 12Color

> [!hint]- Hint
> Use up nine of the twelve colors on new vertices that every old vertex must avoid.

> [!solution]- Solution
> **Reduce from** 3Color ([[2-algorithms/12-np-hardness#1210-graph-coloring-from-3sat|§12.10]]).
>
> **Reduction.** Given an arbitrary graph $G = (V, E)$, build $G'$: $G$ plus nine new vertices $q_1,\dots,q_9$ that form a clique, each $q_i$ also adjacent to every vertex of $V$. $G'$ has $n + 9$ vertices and $\lvert E\rvert + 36 + 9n$ edges; it is built in $O(V + E)$ time.
>
> **⇒** Given a proper 3-coloring of $G$ with colors $1, 2, 3$, give $q_i$ color $3 + i$. The $q_i$ differ from each other and from colors $1$–$3$, so this is a proper 12-coloring of $G'$.
>
> **⇐** In a proper 12-coloring of $G'$, the clique $q_1,\dots,q_9$ uses nine distinct colors. Every vertex of $V$ is adjacent to all nine, so it gets one of the three remaining colors. Restricted to $G$, the coloring is proper and uses three colors.
>
> **Answer.** $G$ is 3-colorable if and only if $G$ plus a $K_9$ joined to every vertex is 12-colorable; the reduction runs in polynomial time, so 12Color is NP-hard.

### (c) 12Sat

> [!hint]- Hint
> Pad each clause with nine new variables, in every combination of signs, so that the padding can never help.

> [!solution]- Solution
> **Reduce from** 3Sat ([[2-algorithms/12-np-hardness#126-3sat-from-circuitsat|§12.6]]).
>
> **Reduction.** Given an arbitrary 3CNF formula $\Phi$ with $k$ clauses, add nine new variables $y_1,\dots,y_9$ and replace each clause $C$ by the $2^9 = 512$ clauses
>
> $$
> C\vee y_1^{\pm}\vee y_2^{\pm}\vee\cdots\vee y_9^{\pm},
> $$
>
> one for every choice of signs ($y^{+} = y$, $y^{-} = \bar y$). The new formula $\Phi'$ has $512k$ clauses of twelve literals: linear size, built in polynomial time.
>
> **⇒** A satisfying assignment of $\Phi$, extended by any values of the $y_i$, satisfies $\Phi'$: every clause of $\Phi'$ contains some clause $C$ of $\Phi$, which has a True literal.
>
> **⇐** Let $\alpha$ satisfy $\Phi'$. For a clause $C$ of $\Phi$, look at its copy whose padding literals are all False under $\alpha$ (take $y_i$ where $\alpha(y_i)$ is False and $\bar y_i$ where it is True). That copy is satisfied, so one of $C$'s own literals is True. So $\alpha$, restricted to the original variables, satisfies $\Phi$.
>
> If clauses must consist of twelve *distinct* variables: drop every clause of $\Phi$ containing some $x$ and $\bar x$ (it is always true), and pad a clause with only $d < 3$ distinct literals with $12 - d$ new variables in all $2^{12-d}$ sign patterns (eleven new variables suffice for every clause). The same proof works.
>
> **Answer.** Pad every clause with nine new variables in all 512 sign patterns; $\Phi$ is satisfiable iff the padded 12CNF formula is, and the reduction takes polynomial time, so 12Sat is NP-hard.

## Exercise 12.8 — Directed versus undirected Hamiltonian cycles

> [!question] Exercise 12.8 (book p. 418)
> The chapter proves twice that the Hamiltonian cycle problem in *directed* graphs is NP-hard.
>
> (a) Describe a polynomial-time reduction from undirected HamiltonianCycle to directed HamiltonianCycle, and prove it correct.
>
> (b) Describe a polynomial-time reduction from directed HamiltonianCycle to undirected HamiltonianCycle, and prove it correct.
>
> (c) Which of these two reductions implies that the undirected Hamiltonian cycle problem is NP-hard?
>
> (Exercise 12.9 asks (a) and (b) again.)

### (a) Undirected to directed

> [!solution]- Solution
> **Reduction.** Given an arbitrary undirected graph $G$: if $n\le 2$, $G$ has no Hamiltonian cycle, so output a fixed directed graph without one (two vertices, no edges). Otherwise output the directed graph $H$ on the same vertices with both edges $u\to v$ and $v\to u$ for every edge $uv$. $O(V + E)$ time.
>
> **⇒** Traverse a Hamiltonian cycle of $G$ in one direction; all its edges exist in $H$.
>
> **⇐** A Hamiltonian cycle $v_1\to v_2\to\cdots\to v_n\to v_1$ of $H$ uses edges that come from the edges $v_iv_{i+1}$ of $G$. Because $n\ge 3$, these $n$ edges of $G$ are distinct, so $v_1v_2\cdots v_nv_1$ is a Hamiltonian cycle of $G$.
>
> **Answer.** Replace each edge by two opposite directed edges (and send graphs with fewer than 3 vertices to a fixed NO instance): $O(V+E)$ time.

> [!trap]
> Without the special case the reduction is wrong: the graph with two vertices and one edge has no Hamiltonian cycle, but it would become the directed 2-cycle $u\to v\to u$, which is one.

### (b) Directed to undirected

> [!hint]- Hint
> Split every vertex into three in a row. A middle vertex of degree 2 forces the cycle to pass straight through.

> [!solution]- Solution
> **Reduction.** Given an arbitrary directed graph $G = (V, E)$, build the undirected graph $H$: for every vertex $v$, three vertices $v_{\mathrm{in}}, v_{\mathrm{mid}}, v_{\mathrm{out}}$ and the edges $v_{\mathrm{in}}v_{\mathrm{mid}}$ and $v_{\mathrm{mid}}v_{\mathrm{out}}$; for every directed edge $u\to v$, the edge $u_{\mathrm{out}}v_{\mathrm{in}}$. $H$ has $3n$ vertices and $2n + \lvert E\rvert$ edges; $O(V + E)$ time.
>
> **⇒** A directed Hamiltonian cycle $v_1\to v_2\to\cdots\to v_n\to v_1$ becomes the cycle $v_{1,\mathrm{in}}\,v_{1,\mathrm{mid}}\,v_{1,\mathrm{out}}\,v_{2,\mathrm{in}}\cdots v_{n,\mathrm{out}}\,v_{1,\mathrm{in}}$ through all $3n\ge 6$ vertices of $H$.
>
> **⇐** Let $C$ be a Hamiltonian cycle of $H$. Every $v_{\mathrm{mid}}$ has degree 2, so $C$ uses both its edges: $C$ contains the path $v_{\mathrm{in}}v_{\mathrm{mid}}v_{\mathrm{out}}$ for every $v$. The other edge of $C$ at $v_{\mathrm{out}}$ goes to an in-vertex, and the other edge at $v_{\mathrm{in}}$ comes from an out-vertex. Walk along $C$ from $v_{1,\mathrm{in}}$ toward $v_{1,\mathrm{mid}}$: it passes $v_{1,\mathrm{in}}, v_{1,\mathrm{mid}}, v_{1,\mathrm{out}}$, then some $u_{\mathrm{in}}$ (an edge $v_{1,\mathrm{out}}u_{\mathrm{in}}$, so $v_1\to u$ is an edge of $G$), then $u_{\mathrm{mid}}, u_{\mathrm{out}}$, and so on. $C$ visits the triples one at a time, each in the order in, mid, out, and consecutive triples are joined by edges of $G$. It visits every triple once and returns to $v_{1,\mathrm{in}}$, so the order of the triples is a directed Hamiltonian cycle of $G$.
>
> **Answer.** Split $v$ into the path $v_{\mathrm{in}}v_{\mathrm{mid}}v_{\mathrm{out}}$ and turn $u\to v$ into the edge $u_{\mathrm{out}}v_{\mathrm{in}}$: $3n$ vertices, built in polynomial ($O(V+E)$) time.

<!-- fig:a12x-split -->
<figure class="cs-fig"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 620 280" width="620" height="280" role="img" style="font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-size:14px"><title>a directed triangle a, b, c with an extra edge a to c, and the undirected graph of in, mid, out triples with the corresponding 9-vertex cycle in red</title><defs><marker id="ARR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs><line x1="117.3" y1="73.3" x2="167.6" y2="178.4" stroke="var(--hi)" stroke-width="2.8" stroke-linecap="round" marker-end="url(#ARR)"/><line x1="159" y1="196" x2="63.5" y2="196" stroke="var(--hi)" stroke-width="2.8" stroke-linecap="round" marker-end="url(#ARR)"/><line x1="51.3" y1="180.7" x2="101.6" y2="75.6" stroke="var(--hi)" stroke-width="2.8" stroke-linecap="round" marker-end="url(#ARR)"/><path d="M113.3,74.7 Q128,150 61.1,186.6" fill="none" stroke="var(--muted)" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)" stroke-dasharray="5 4"/><circle cx="110" cy="58" r="17" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="110" y="59" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">a</text><circle cx="176" cy="196" r="17" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="176" y="197" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">b</text><circle cx="44" cy="196" r="17" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="44" y="197" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">c</text><text x="110" y="250" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">directed G</text><line x1="232" y1="30" x2="232" y2="250" stroke="var(--muted)" stroke-width="0.8" stroke-linecap="round" stroke-dasharray="2 4"/><rect x="274" y="36" width="212" height="44" rx="22" fill="none" stroke="var(--muted)" stroke-width="1" stroke-dasharray="3 3"/><rect x="538" y="72" width="44" height="156" rx="22" fill="none" stroke="var(--muted)" stroke-width="1" stroke-dasharray="3 3"/><rect x="274" y="210" width="212" height="44" rx="22" fill="none" stroke="var(--muted)" stroke-width="1" stroke-dasharray="3 3"/><text x="380" y="22" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">a</text><text x="600" y="150" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">b</text><text x="380" y="270" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">c</text><line x1="316" y1="58" x2="364" y2="58" stroke="var(--hi)" stroke-width="2.8" stroke-linecap="round"/><line x1="560" y1="112" x2="560" y2="134" stroke="var(--hi)" stroke-width="2.8" stroke-linecap="round"/><line x1="444" y1="232" x2="396" y2="232" stroke="var(--hi)" stroke-width="2.8" stroke-linecap="round"/><line x1="396" y1="58" x2="444" y2="58" stroke="var(--hi)" stroke-width="2.8" stroke-linecap="round"/><line x1="560" y1="166" x2="560" y2="188" stroke="var(--hi)" stroke-width="2.8" stroke-linecap="round"/><line x1="364" y1="232" x2="316" y2="232" stroke="var(--hi)" stroke-width="2.8" stroke-linecap="round"/><line x1="475" y1="63.7" x2="545" y2="90.3" stroke="var(--hi)" stroke-width="2.8" stroke-linecap="round"/><line x1="544.6" y1="208.3" x2="475.4" y2="227.7" stroke="var(--hi)" stroke-width="2.8" stroke-linecap="round"/><line x1="300" y1="216" x2="300" y2="74" stroke="var(--hi)" stroke-width="2.8" stroke-linecap="round"/><line x1="460" y1="74" x2="460" y2="216" stroke="var(--muted)" stroke-width="1.3" stroke-linecap="round" stroke-dasharray="5 4"/><circle cx="300" cy="58" r="16" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="300" y="59" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:11px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">in</text><circle cx="380" cy="58" r="16" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="380" y="59" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:11px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">mid</text><circle cx="460" cy="58" r="16" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="460" y="59" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:11px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">out</text><circle cx="560" cy="96" r="16" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="560" y="97" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:11px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">in</text><circle cx="560" cy="150" r="16" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="560" y="151" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:11px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">mid</text><circle cx="560" cy="204" r="16" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="560" y="205" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:11px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">out</text><circle cx="460" cy="232" r="16" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="460" y="233" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:11px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">in</text><circle cx="380" cy="232" r="16" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="380" y="233" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:11px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">mid</text><circle cx="300" cy="232" r="16" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="300" y="233" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:11px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">out</text><text x="380" y="150" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">undirected H</text></svg><figcaption><strong>Splitting vertices (Exercise 12.8(b)).</strong> Each vertex <i>v</i> of the directed graph becomes a path <i>v</i><sub>in</sub> <i>v</i><sub>mid</sub> <i>v</i><sub>out</sub>, and each edge <i>u</i>→<i>v</i> becomes the undirected edge <i>u</i><sub>out</sub><i>v</i><sub>in</sub>. A middle vertex has degree 2, so a Hamiltonian cycle of <i>H</i> runs straight through every triple, in at an in-vertex and out at an out-vertex: red, the cycle for <i>a</i>→<i>b</i>→<i>c</i>→<i>a</i>. The edge <i>a</i>→<i>c</i> (dashed) is not used.</figcaption></figure>

### (c) Which one proves hardness

> [!solution]- Solution
> Reduction (b). It reduces the known NP-hard problem (directed HamiltonianCycle, [[2-algorithms/12-np-hardness#1211-hamiltonian-cycle|§12.11]]) **to** the undirected one, so a polynomial-time algorithm for undirected graphs would give one for directed graphs. Reduction (a) goes the other way: it shows only that the undirected problem is no harder than the directed one.
>
> **Answer.** (b), from directed to undirected.

## Exercise 12.10 — Hamiltonian path versus cycle

> [!question] Exercise 12.10 (book p. 418)
> (a) Describe a polynomial-time reduction from HamiltonianPath to HamiltonianCycle.
>
> (b) Describe a polynomial-time reduction from HamiltonianCycle to HamiltonianPath. *(Hint: a polynomial-time reduction may call the black-box subroutine more than once, but it doesn't have to.)*

Both for undirected graphs.

### (a) Path to cycle

> [!hint]- Hint
> Close the path through one new vertex.

> [!solution]- Solution
> **Reduction.** Given an arbitrary graph $G$: if $n = 1$, $G$ has a Hamiltonian path (its one vertex), so output a triangle. Otherwise output $G'$: $G$ plus a new vertex $z$ adjacent to every vertex of $G$. $n + 1$ vertices, $\lvert E\rvert + n$ edges, $O(V + E)$ time.
>
> **⇒** A Hamiltonian path $v_1v_2\cdots v_n$ of $G$ gives the cycle $z\,v_1v_2\cdots v_n\,z$ through all $n + 1\ge 3$ vertices.
>
> **⇐** A Hamiltonian cycle of $G'$ passes through $z$; deleting $z$ leaves a path through all $n$ vertices of $G$ that uses only edges of $G$.
>
> **Answer.** Add one vertex adjacent to everything: $G$ has a Hamiltonian path iff $G'$ has a Hamiltonian cycle, and $G'$ is built in polynomial time.

### (b) Cycle to path

> [!hint]- Hint
> Cut the cycle open at a vertex $v$ by making a copy $v'$ of it, and force the path to start at $v$ and end at $v'$ with two new pendant vertices.

> [!solution]- Solution
> **Reduction.** Given an arbitrary graph $G$: if $n\le 2$, $G$ has no Hamiltonian cycle, so output a fixed graph without a Hamiltonian path (two vertices, no edge). Otherwise pick any vertex $v$ and output $G'$: $G$ plus three new vertices, $v'$ adjacent to every neighbor of $v$, $s$ adjacent only to $v$, and $t$ adjacent only to $v'$. $n + 3$ vertices, $\lvert E\rvert + \deg(v) + 2$ edges, $O(V + E)$ time; one call to the black box.
>
> **⇒** A Hamiltonian cycle $v\,u_1u_2\cdots u_{n-1}\,v$ of $G$ gives the Hamiltonian path $s\,v\,u_1\cdots u_{n-1}\,v'\,t$ of $G'$: $u_{n-1}$ is a neighbor of $v$, hence of $v'$.
>
> **⇐** $s$ and $t$ have degree 1, so they are the two ends of every Hamiltonian path of $G'$ (an inner vertex of a path has two neighbors on it). Their only neighbors are $v$ and $v'$, so the path is $s\,v\,w_1\cdots w_{n-1}\,v'\,t$, where $w_1,\dots,w_{n-1}$ are the other vertices of $G$ in some order. Now $w_{n-1}$ is a neighbor of $v'$, hence of $v$, and $n - 1\ge 2$, so $v\,w_1\cdots w_{n-1}\,v$ is a Hamiltonian cycle of $G$.
>
> **Answer.** Copy one vertex $v$ to $v'$ and hang new leaves $s$ on $v$ and $t$ on $v'$: $G$ has a Hamiltonian cycle iff $G'$ has a Hamiltonian path, and $G'$ is built in polynomial time.

<!-- fig:a12x-cycle-to-path -->
<figure class="cs-fig"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 520 260" width="520" height="260" role="img" style="font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-size:14px"><title>a five-vertex graph with a copy v&#x27; of v and pendant vertices s and t; a Hamiltonian path from s to t highlighted</title><defs><marker id="ARR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs><line x1="165.6" y1="66.4" x2="264.4" y2="43.6" stroke="var(--hi)" stroke-width="2.8" stroke-linecap="round"/><line x1="295.7" y1="43.1" x2="414.3" y2="66.9" stroke="var(--hi)" stroke-width="2.8" stroke-linecap="round"/><line x1="430" y1="86" x2="430" y2="174" stroke="var(--hi)" stroke-width="2.8" stroke-linecap="round"/><line x1="414.4" y1="193.3" x2="295.6" y2="218.7" stroke="var(--hi)" stroke-width="2.8" stroke-linecap="round"/><line x1="269.6" y1="209.8" x2="160.4" y2="82.2" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/><line x1="291.3" y1="51.3" x2="418.7" y2="178.7" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/><line x1="160.1" y1="187.6" x2="269.9" y2="52.4" stroke="var(--accent)" stroke-width="1.3" stroke-linecap="round" stroke-dasharray="5 4"/><line x1="165.8" y1="202.7" x2="264.2" y2="219.3" stroke="var(--hi)" stroke-width="2.8" stroke-linecap="round"/><line x1="66" y1="70" x2="134" y2="70" stroke="var(--hi)" stroke-width="2.8" stroke-linecap="round"/><line x1="66" y1="200" x2="134" y2="200" stroke="var(--hi)" stroke-width="2.8" stroke-linecap="round"/><circle cx="50" cy="70" r="16" fill="var(--paper)" stroke="var(--accent)" stroke-width="1.5"/><text x="50" y="71" text-anchor="middle" dominant-baseline="central" fill="var(--accent)" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">s</text><circle cx="150" cy="70" r="16" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="150" y="71" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">v</text><circle cx="150" cy="200" r="16" fill="var(--paper)" stroke="var(--accent)" stroke-width="1.5"/><text x="150" y="201" text-anchor="middle" dominant-baseline="central" fill="var(--accent)" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">v&#x27;</text><circle cx="50" cy="200" r="16" fill="var(--paper)" stroke="var(--accent)" stroke-width="1.5"/><text x="50" y="201" text-anchor="middle" dominant-baseline="central" fill="var(--accent)" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">t</text><circle cx="280" cy="40" r="16" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="280" y="41" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">a</text><circle cx="430" cy="70" r="16" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="430" y="71" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">b</text><circle cx="430" cy="190" r="16" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="430" y="191" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">c</text><circle cx="280" cy="222" r="16" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="280" y="223" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">d</text></svg><figcaption><strong>Cutting a cycle open (Exercise 12.10(b)).</strong> The new vertex <i>v</i>′ (blue) copies the neighbors <i>a</i>, <i>d</i> of <i>v</i>, and the leaves <i>s</i> and <i>t</i> hang on <i>v</i> and <i>v</i>′. Leaves must be the ends of a Hamiltonian path, so every Hamiltonian path runs <i>s</i>, <i>v</i>, …, <i>v</i>′, <i>t</i>; its middle part is a Hamiltonian cycle of the original graph with its last edge redirected to <i>v</i>′. Red: the path <i>s v a b c d v</i>′ <i>t</i>, from the cycle <i>v a b c d v</i>.</figcaption></figure>

> [!trap]
> - The special case for $n\le 2$ is needed: for a single edge $uv$ (no Hamiltonian cycle), $G'$ has the Hamiltonian path $s\,v\,u\,v'\,t$.
> - Adding $t$ as a second leaf on $v$ itself does not work: $v$ would need three path neighbors.

## Exercise 12.16 — Six NP-hard graph problems

> [!question] Exercise 12.16 (book p. 420)
> Prove that the following problems are NP-hard.
>
> (a) Given an undirected graph $G$, does $G$ contain a simple path that visits all but 17 vertices?
>
> (b) Given an undirected graph $G$, does $G$ have a spanning tree in which every node has degree at most 23?
>
> (c) Given an undirected graph $G$, does $G$ have a spanning tree with at most 42 leaves?
>
> (d) Given an undirected graph $G = (V, E)$, what is the size of the largest set $S\subseteq V$ such that at most 374 edges of $E$ have both endpoints in $S$?
>
> (e) Given an undirected graph $G = (V, E)$, what is the size of the largest set $S\subseteq V$ in which each vertex has at most 473 neighbors in $S$?
>
> (f) Given an undirected graph $G$, can its vertices be colored with three colors so that at most 31337 edges have both endpoints the same color?

The constants are a disguise. Each reduction adds a gadget that uses up the allowance exactly, leaving the classic problem with no allowance at all: Hamiltonian path for (a)–(c), independent set for (d) and (e) — the chapter's rule of thumb for a large subset ([[2-algorithms/12-np-hardness#1214-choosing-the-right-problem|§12.14]]) — and 3Color for (f). Every construction adds a number of vertices and edges linear in $n$, so it runs in polynomial time, $O(V + E)$.

### (a) A path missing 17 vertices

> [!solution]- Solution
> **Reduce from** undirected HamiltonianPath, NP-hard by Exercises 12.8(b) and 12.10(b).
>
> **Reduction.** Given an arbitrary graph $G$, output $G'$: $G$ plus 17 new isolated vertices.
>
> **⇒** A Hamiltonian path of $G$ is a path of $G'$ that misses exactly the 17 new vertices.
>
> **⇐** Suppose $G'$ has a simple path $P$ through all but 17 of its $n + 17$ vertices, so through $n$ vertices. If $n = 1$, $G$ has a Hamiltonian path anyway. If $n\ge 2$, every vertex of $P$ has an edge of $P$, so $P$ avoids the isolated vertices: it is a path of $G$ through all $n$ vertices.
>
> (If "all but 17" means "all but at most 17", the same proof works: $P$ then has at least $n$ vertices.)
>
> **Answer.** $G$ has a Hamiltonian path iff $G$ plus 17 isolated vertices has a path missing 17 vertices.

### (b) Spanning tree of degree at most 23

> [!solution]- Solution
> **Reduce from** HamiltonianPath.
>
> **Reduction.** Given an arbitrary $G$, output $G'$: $G$ plus, for every vertex $v$, 21 new vertices adjacent only to $v$ (pendant leaves). $22n$ vertices, $\lvert E\rvert + 21n$ edges.
>
> **⇒** A Hamiltonian path of $G$ plus all the pendant edges is a spanning tree of $G'$; each $v\in V$ has degree at most $2 + 21 = 23$, each new vertex degree 1.
>
> **⇐** Let $T$ be a spanning tree of $G'$ with maximum degree at most 23. A pendant vertex has only one edge, so $T$ contains all $21n$ pendant edges, and every $v\in V$ has at most 2 edges of $T$ inside $G$. Deleting the pendant leaves from $T$ leaves a tree spanning $V$ with maximum degree at most 2 — a path through all of $V$, a Hamiltonian path of $G$.
>
> **Answer.** Hang 21 leaves on every vertex: $G$ has a Hamiltonian path iff $G'$ has a spanning tree of maximum degree 23.

### (c) Spanning tree with at most 42 leaves

> [!hint]- Hint
> A spanning tree with at most 2 leaves is a Hamiltonian path. Spend 41 leaves on a gadget — but you don't know where the path of $G$ will end, so attach the gadget to a new vertex adjacent to everything.

> [!solution]- Solution
> **Reduce from** HamiltonianPath.
>
> **Reduction.** Given an arbitrary $G$, output $G'$: $G$ plus a new vertex $z$ adjacent to every vertex of $G$, plus 41 new vertices $p_1,\dots,p_{41}$ adjacent only to $z$. $n + 42$ vertices, $\lvert E\rvert + n + 41$ edges.
>
> **⇒** For a Hamiltonian path $v_1\cdots v_n$ of $G$, take the path, the edge $zv_1$ and the 41 edges $zp_i$. Its leaves are $p_1,\dots,p_{41}$ and $v_n$: exactly 42 ($z$ has degree 42).
>
> **⇐** Let $T$ be a spanning tree of $G'$ with at most 42 leaves. The 41 vertices $p_i$ are leaves, so at most one leaf of $T$ lies in $V$. Deleting $z$ and the $p_i$ from $T$ leaves a forest $F$ spanning $V$, and each component of $F$ is joined to $z$ by exactly one edge of $T$ (at least one since $T$ is connected, at most one since it is acyclic). A one-vertex component is a leaf of $T$; a larger component is a tree with at least two leaves of its own, at most one of which gets the edge to $z$. So every component contains a leaf of $T$: $F$ has a single component. If $n = 1$, $G$ has a Hamiltonian path anyway; if $n\ge 2$, that tree has at most two leaves of its own (a third would give $T$ two leaves in $V$), so it is a path through all of $V$, a Hamiltonian path.
>
> **Answer.** Add $z$ adjacent to all of $V$ and 41 leaves on $z$: $G$ has a Hamiltonian path iff $G'$ has a spanning tree with at most 42 leaves.

### (d) At most 374 edges inside

> [!hint]- Hint
> Add 374 new disjoint edges. Each allowed edge is worth at most one extra vertex, wherever it is spent.

> [!solution]- Solution
> **Reduce from** IndependentSet, the decision version of MaxIndSet (§12.7). An algorithm that computes the largest such set answers the decision question below.
>
> **Reduction.** Given an arbitrary $(G, k)$, output $G'$: $G$ plus 374 new disjoint edges $a_ib_i$ (748 new vertices), with the threshold $k + 748$.
>
> **Claim.** $G$ has an independent set of size at least $k$ iff $G'$ has a set of at least $k + 748$ vertices with at most 374 edges inside.
>
> **⇒** An independent set $I$ of $G$ plus all 748 new vertices has exactly the 374 new edges inside.
>
> **⇐** Let $S$ be such a set, $A = S\cap V$, $B = S\setminus A$, and $e(X)$ the number of edges inside $X$. Each new edge $a_ib_i$ contributes at most $1 + [\text{both ends in } S]$ vertices to $B$, so $\lvert B\rvert\le 374 + e(B)$. Deleting one endpoint of every edge inside $A$ leaves an independent set of $G$ with at least
>
> $$
> \lvert A\rvert - e(A) = \lvert S\rvert - \lvert B\rvert - e(A)\ \ge\ \lvert S\rvert - 374 - e(B) - e(A)\ \ge\ \lvert S\rvert - 748\ \ge\ k
> $$
>
> vertices, using $e(A) + e(B) = e(S)\le 374$.
>
> **Answer.** The largest set of $G'$ with at most 374 inside edges has exactly $\alpha(G) + 748$ vertices, where $\alpha(G)$ is the size of the largest independent set of $G$; so the problem is NP-hard.

### (e) At most 473 neighbors inside

> [!hint]- Hint
> Give every vertex 473 private neighbors that form a clique. A vertex of $G$ can then afford no neighbor of $G$ in the set without giving up one of its private neighbors.

> [!solution]- Solution
> **Reduce from** IndependentSet.
>
> **Reduction.** Given an arbitrary $(G, k)$, output $G'$: $G$ plus, for every vertex $v$, a clique $Q_v$ of 473 new vertices, each adjacent to $v$; threshold $473n + k$. $474n$ vertices.
>
> **Claim.** $G$ has an independent set of size at least $k$ iff $G'$ has a set of at least $473n + k$ vertices in which every vertex has at most 473 neighbors in the set.
>
> **⇒** Take an independent set $I$ of $G$ and all the cliques: $S = I\cup\bigcup_v Q_v$. A vertex of $Q_v$ has 472 neighbors in $Q_v$, plus $v$ if $v\in I$: at most 473. A vertex $v\in I$ has its 473 neighbors in $Q_v$ and none in $I$.
>
> **⇐** Let $S$ be such a set, $A = S\cap V$, and $d_A(v)$ the number of neighbors of $v$ in $A$. A vertex $v\in A$ has $d_A(v) + \lvert S\cap Q_v\rvert\le 473$ neighbors in $S$, so $\lvert S\cap Q_v\rvert\le 473 - d_A(v)$; for $v\notin A$, $\lvert S\cap Q_v\rvert\le 473$. Adding up,
>
> $$
> \begin{aligned}
> \lvert S\rvert &\le \lvert A\rvert + 473n - \textstyle\sum_{v\in A} d_A(v) = 473n + \lvert A\rvert - 2e(A)\\
> &\le 473n + \bigl(\lvert A\rvert - e(A)\bigr) \le 473n + \alpha(G),
> \end{aligned}
> $$
>
> as in (d). So $\alpha(G)\ge\lvert S\rvert - 473n\ge k$.
>
> **Answer.** The largest such set of $G'$ has exactly $473n + \alpha(G)$ vertices; NP-hard.

### (f) Three colors with at most 31337 bad edges

> [!solution]- Solution
> **Reduce from** 3Color.
>
> **Reduction.** Given an arbitrary $G$, output $G'$: $G$ plus 31337 disjoint copies of $K_4$, the complete graph on four vertices.
>
> **⇒** Color $G$ properly and each $K_4$ with colors $1, 2, 3, 1$: the only monochromatic edges are the 31337 edges joining the two vertices of color 1 in each copy.
>
> **⇐** Four vertices with three colors: in every copy of $K_4$ two vertices share a color, and they are adjacent. So every 3-coloring has at least 31337 monochromatic edges inside the copies. If it has at most 31337 in total, none is an edge of $G$: the coloring restricted to $G$ is proper.
>
> **Answer.** $G$ is 3-colorable iff $G$ plus 31337 disjoint $K_4$'s has a 3-coloring with at most 31337 monochromatic edges.

## Exercise 12.22 — Dominos

> [!question] Exercise 12.22(a)(b) (book p. 421)
> A **domino** is a $1\times 2$ tile with an integer on each half. In a **legal arrangement**, dominos lie end to end so that touching ends carry the same number (a domino may be turned around). For each problem, describe a polynomial-time algorithm or prove it NP-hard.
>
> (a) Given a bag $D$ of dominos, is there a legal arrangement of *all* the dominos in $D$?
>
> (b) Given a bag $D$ of dominos and an integer $n$, is there a legal arrangement of some dominos from $D$ in which every integer between 1 and $n$ appears exactly twice?

### (a) All the dominos: an Euler trail

> [!hint]- Hint
> Numbers are vertices, dominos are edges.

> [!solution]- Solution
> **Graph.** An undirected multigraph $M$ with one vertex per number that occurs in $D$ and one edge per domino; a double $[a\,|\,a]$ is a loop, which adds 2 to the degree of $a$. A legal arrangement of all of $D$ is exactly a walk in $M$ that uses every edge once: an **Euler trail**, open or closed.
>
> **Algorithm.** Answer True if $D$ is empty, or if all the edges of $M$ lie in one component and $M$ has 0 or 2 vertices of odd degree; otherwise False. These are Euler's conditions: necessity because a walk enters and leaves every vertex other than its two ends equally often; sufficiency by [[2-algorithms/05-basic-graph-algorithms-exercises#exercise-55--euler-tours|Exercise 5.5]] (with two odd vertices, add an edge between them, take the closed Euler tour, and remove that edge). Building $M$ takes $O(m\log m)$ time for $m = \lvert D\rvert$ dominos (sort the numbers to name the vertices); degrees and one whatever-first search take $O(m)$.
>
> **Answer.** In P: all dominos connected and 0 or 2 numbers of odd degree. $O(m\log m)$ time.

### (b) Every number exactly twice: a Hamiltonian cycle

> [!hint]- Hint
> An arrangement in which every number appears twice must start and end with the same number. What does it trace in the graph of (a)?

> [!solution]- Solution
> NP-hard. **Reduce from** undirected HamiltonianCycle (NP-hard by Exercise 12.8(b)).
>
> **Reduction.** Given an arbitrary graph $G$: if $n\le 2$, it has no Hamiltonian cycle; output a fixed NO instance ($D$ empty, $n = 1$). (This case only keeps the proof short: for $n\le 2$ the construction below gives at most one domino, so no number appears twice and the answer is NO anyway.) Otherwise number the vertices $1,\dots,n$ and output the bag $D$ with one domino $[u\,|\,v]$ for every edge $uv$, and the same $n$. $\lvert E\rvert$ dominos; $O(V + E)$ time. All numbers on the dominos lie between 1 and $n$.
>
> **⇒** A Hamiltonian cycle $v_1v_2\cdots v_nv_1$ gives the arrangement $[v_1|v_2][v_2|v_3]\cdots[v_n|v_1]$ of $n$ distinct dominos ($n\ge 3$), in which every number appears twice.
>
> **⇐** Write an arrangement as $[p_1|p_2][p_2|p_3]\cdots[p_k|p_{k+1}]$. A number appears once for each end of the line it sits at and twice for each inner junction $p_2,\dots,p_k$ it sits at. If $p_1\ne p_{k+1}$, then $p_1$ appears an odd number of times; so $p_1 = p_{k+1}$, it appears twice at the ends and at no junction, and every other number appears at exactly one junction. Every number from 1 to $n$ appears, so $p_1,\dots,p_k$ are all $n$ numbers, each once, and $k = n$. Each domino is an edge of $G$, so $p_1p_2\cdots p_np_1$ is a Hamiltonian cycle.
>
> **Answer.** NP-hard: with one domino per edge, built in polynomial time, an arrangement using every number $1,\dots,n$ exactly twice is the same thing as a Hamiltonian cycle.

> [!intuition]
> The pair (a)/(b) is the chapter's Euler-versus-Hamilton contrast ([[2-algorithms/12-np-hardness#1211-hamiltonian-cycle|§12.11]]) in disguise: using every *domino* once is an Euler trail, easy; using every *number* twice — visiting every vertex once — is a Hamiltonian cycle, hard.

## Exercise 12.26 — Dominating set

> [!question] Exercise 12.26 (book pp. 422–423)
> A **dominating set** of a graph $G$ is a set $S$ of vertices such that every vertex of $G$ is in $S$ or adjacent to a vertex of $S$. DominatingSet asks, given $G$ and an integer $k$, whether $G$ has a dominating set of size $k$. Prove that DominatingSet is NP-hard. (The book's Figure 12.29: a dominating set of size 3 in the Petersen graph.)

> [!hint]- Hint
> A small set that must "touch" everything: reduce from VertexCover. Make every edge a vertex that only its two endpoints can dominate.

> [!solution]- Solution
> **Reduce from** VertexCover ([[2-algorithms/12-np-hardness#129-clique-and-vertex-cover-from-independent-set|§12.9]]). Read both questions as "of size at most $k$". (Adding vertices to a dominating set or a vertex cover keeps it one, so "exactly $k$" is the same question whenever $k$ is at most the number of vertices.)
>
> **Reduction.** Given an arbitrary $(G, k)$, delete the isolated vertices of $G$ (they touch no edge, so no vertex cover needs them); call the result $G_0 = (V_0, E)$. Output $(G', k)$, where $G'$ is $G_0$ plus, for every edge $uv$, a new vertex $w_{uv}$ adjacent to $u$ and $v$. $\lvert V_0\rvert + \lvert E\rvert$ vertices, $3\lvert E\rvert$ edges, $O(V + E)$ time.
>
> **⇒** Let $C$ be a vertex cover of $G$ with $\lvert C\rvert\le k$; drop its isolated vertices, so $C\subseteq V_0$. Every $w_{uv}$ is adjacent to $u$ or $v$, one of which is in $C$. A vertex $u\in V_0\setminus C$ is not isolated, so it has an edge $uv$, and $v\in C$ because $C$ covers $uv$. So $C$ dominates $G'$.
>
> **⇐** Let $D$ be a dominating set of $G'$ with $\lvert D\rvert\le k$. Replace every $w_{uv}\in D$ by $u$: the set stays dominating ($u$ dominates $w_{uv}$, $u$ and $v$, everything $w_{uv}$ dominated) and gets no larger. Now $D\subseteq V_0$, and it dominates every $w_{uv}$, whose only neighbors are $u$ and $v$: so $u\in D$ or $v\in D$ for every edge $uv$. $D$ is a vertex cover of $G$ of size at most $k$.
>
> **Answer.** Delete isolated vertices and give every edge $uv$ a new vertex adjacent to $u$ and $v$: $G$ has a vertex cover of size at most $k$ iff $G'$ has a dominating set of size at most $k$. The reduction runs in polynomial time, so DominatingSet is NP-hard.

<!-- fig:a12x-dominating -->
<figure class="cs-fig"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 520 260" width="520" height="260" role="img" style="font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-size:14px"><title>a triangle u v w with pendant x; every edge has an extra square vertex joined to its two ends; v and w highlighted</title><defs><marker id="ARR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs><line x1="110" y1="76" x2="110" y2="184" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/><line x1="45.7" y1="124.3" x2="98.7" y2="71.3" stroke="var(--accent)" stroke-width="1.3" stroke-linecap="round"/><line x1="45.7" y1="135.7" x2="98.7" y2="188.7" stroke="var(--accent)" stroke-width="1.3" stroke-linecap="round"/><line x1="124.8" y1="66.1" x2="265.2" y2="123.9" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/><line x1="207.1" y1="48.9" x2="125.9" y2="58.2" stroke="var(--accent)" stroke-width="1.3" stroke-linecap="round"/><line x1="220" y1="54.3" x2="270.1" y2="117.5" stroke="var(--accent)" stroke-width="1.3" stroke-linecap="round"/><line x1="124.8" y1="193.9" x2="265.2" y2="136.1" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/><line x1="207.1" y1="211.1" x2="125.9" y2="201.8" stroke="var(--accent)" stroke-width="1.3" stroke-linecap="round"/><line x1="220" y1="205.7" x2="270.1" y2="142.5" stroke="var(--accent)" stroke-width="1.3" stroke-linecap="round"/><line x1="296" y1="130" x2="434" y2="130" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/><line x1="358.4" y1="76.5" x2="293.2" y2="121" stroke="var(--accent)" stroke-width="1.3" stroke-linecap="round"/><line x1="371.6" y1="76.5" x2="436.8" y2="121" stroke="var(--accent)" stroke-width="1.3" stroke-linecap="round"/><rect x="32" y="122" width="16" height="16" rx="2" fill="var(--paper)" stroke="var(--accent)" stroke-width="1.5"/><text x="14" y="130" text-anchor="middle" dominant-baseline="central" fill="var(--accent)" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">w<tspan baseline-shift="sub" font-size="10">uv</tspan></text><rect x="207" y="40" width="16" height="16" rx="2" fill="var(--paper)" stroke="var(--accent)" stroke-width="1.5"/><text x="215" y="28" text-anchor="middle" dominant-baseline="central" fill="var(--accent)" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">w<tspan baseline-shift="sub" font-size="10">uw</tspan></text><rect x="207" y="204" width="16" height="16" rx="2" fill="var(--paper)" stroke="var(--accent)" stroke-width="1.5"/><text x="215" y="233" text-anchor="middle" dominant-baseline="central" fill="var(--accent)" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">w<tspan baseline-shift="sub" font-size="10">vw</tspan></text><rect x="357" y="64" width="16" height="16" rx="2" fill="var(--paper)" stroke="var(--accent)" stroke-width="1.5"/><text x="365" y="52" text-anchor="middle" dominant-baseline="central" fill="var(--accent)" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">w<tspan baseline-shift="sub" font-size="10">wx</tspan></text><circle cx="110" cy="60" r="16" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="110" y="61" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">u</text><circle cx="110" cy="200" r="16" fill="var(--hi)" stroke="var(--hi)" stroke-width="2"/><text x="110" y="201" text-anchor="middle" dominant-baseline="central" fill="var(--paper)" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">v</text><circle cx="280" cy="130" r="16" fill="var(--hi)" stroke="var(--hi)" stroke-width="2"/><text x="280" y="131" text-anchor="middle" dominant-baseline="central" fill="var(--paper)" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">w</text><circle cx="450" cy="130" r="16" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="450" y="131" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">x</text></svg><figcaption><strong>Dominating set from vertex cover (Exercise 12.26).</strong> Every edge <i>uv</i> of <i>G</i> gets a new vertex <i>w<sub>uv</sub></i> (blue square) adjacent to <i>u</i> and <i>v</i>. Only <i>u</i>, <i>v</i> and <i>w<sub>uv</sub></i> itself dominate <i>w<sub>uv</sub></i>, so a dominating set must touch every edge. Red: {<i>v</i>, <i>w</i>}, a smallest vertex cover of <i>G</i> and a smallest dominating set of the new graph, both of size 2.</figcaption></figure>

> [!trap]
> Without deleting them, isolated vertices break the reduction: each must be in every dominating set (nothing else can dominate it), while no vertex cover needs it. Keeping them and raising $k$ by their number works too.

## Exercise 12.34 — Red and blue stones

> [!question] Exercise 12.34 (book p. 425)
> A puzzle is an $n\times m$ grid in which every square is empty or holds a red or a blue stone. The goal is to remove some of the stones so that (1) every row still contains at least one stone and (2) no column contains stones of both colors. Prove that deciding whether a given puzzle can be solved is NP-hard.

> [!hint]- Hint
> Each column ends up red, blue or empty — a bit per column. Each row needs one surviving stone — an Or per row.

> [!solution]- Solution
> **Reduce from** 3Sat ([[2-algorithms/12-np-hardness#126-3sat-from-circuitsat|§12.6]]).
>
> **Reduction.** Given an arbitrary 3CNF formula with variables $x_1,\dots,x_N$, first drop the clauses that contain some $x$ together with $\bar x$ (they are always true). Build a grid with one row per remaining clause $C_i$ and one column per variable $x_j$: square $(i, j)$ holds a red stone if $x_j$ is a literal of $C_i$, a blue stone if $\bar x_j$ is, and nothing otherwise. $O(kN)$ time for $k$ clauses.
>
> **⇒** Given a satisfying assignment, remove the blue stones from column $j$ if $x_j$ is True and the red stones otherwise. No column keeps both colors. Each clause $C_i$ has a True literal: if it is $x_j$, then $x_j$ is True and the red stone at $(i, j)$ survived; if it is $\bar x_j$, then $x_j$ is False and the blue stone at $(i, j)$ survived. Every row keeps a stone.
>
> **⇐** Given a solution, set $x_j$ True if and only if column $j$ still contains a red stone. Row $i$ keeps some stone at $(i, j)$. If it is red, $x_j$ is a literal of $C_i$ and $x_j$ is True. If it is blue, $\bar x_j$ is a literal of $C_i$, and column $j$ keeps a blue stone, so it keeps no red one: $x_j$ is False and $\bar x_j$ is True. Every clause is satisfied.
>
> **Answer.** Rows are clauses, columns are variables, red and blue stones are positive and negative literals; the puzzle is solvable iff the formula is satisfiable, and it is built in polynomial time.

<!-- fig:a12x-stones -->
<figure class="cs-fig"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 236" width="600" height="236" role="img" style="font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-size:14px"><title>two 4 by 4 grids of red discs and blue squares, before and after removing the stones that disagree with the assignment</title><defs><marker id="ARR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs><text x="150" y="64" text-anchor="end" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">a ∨ b ∨ c</text><text x="150" y="100" text-anchor="end" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">b ∨ c̄ ∨ d̄</text><text x="150" y="136" text-anchor="end" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">ā ∨ c ∨ d</text><text x="150" y="172" text-anchor="end" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">a ∨ b̄ ∨ d̄</text><text x="188" y="32" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">a</text><text x="224" y="32" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">b</text><text x="260" y="32" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">c</text><text x="296" y="32" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">d</text><rect x="170" y="46" width="144" height="144" rx="0" fill="none" stroke="currentColor" stroke-width="1.2"/><line x1="206" y1="46" x2="206" y2="190" stroke="var(--muted)" stroke-width="0.6" stroke-linecap="round"/><line x1="170" y1="82" x2="314" y2="82" stroke="var(--muted)" stroke-width="0.6" stroke-linecap="round"/><line x1="242" y1="46" x2="242" y2="190" stroke="var(--muted)" stroke-width="0.6" stroke-linecap="round"/><line x1="170" y1="118" x2="314" y2="118" stroke="var(--muted)" stroke-width="0.6" stroke-linecap="round"/><line x1="278" y1="46" x2="278" y2="190" stroke="var(--muted)" stroke-width="0.6" stroke-linecap="round"/><line x1="170" y1="154" x2="314" y2="154" stroke="var(--muted)" stroke-width="0.6" stroke-linecap="round"/><circle cx="188" cy="64" r="11" fill="var(--hi)" stroke="var(--hi)" stroke-width="1.5"/><circle cx="224" cy="64" r="11" fill="var(--hi)" stroke="var(--hi)" stroke-width="1.5"/><circle cx="260" cy="64" r="11" fill="var(--hi)" stroke="var(--hi)" stroke-width="1.5"/><circle cx="224" cy="100" r="11" fill="var(--hi)" stroke="var(--hi)" stroke-width="1.5"/><rect x="250" y="90" width="20" height="20" rx="3" fill="var(--accent)" stroke="var(--accent)" stroke-width="1.5"/><rect x="286" y="90" width="20" height="20" rx="3" fill="var(--accent)" stroke="var(--accent)" stroke-width="1.5"/><rect x="178" y="126" width="20" height="20" rx="3" fill="var(--accent)" stroke="var(--accent)" stroke-width="1.5"/><circle cx="260" cy="136" r="11" fill="var(--hi)" stroke="var(--hi)" stroke-width="1.5"/><circle cx="296" cy="136" r="11" fill="var(--hi)" stroke="var(--hi)" stroke-width="1.5"/><circle cx="188" cy="172" r="11" fill="var(--hi)" stroke="var(--hi)" stroke-width="1.5"/><rect x="214" y="162" width="20" height="20" rx="3" fill="var(--accent)" stroke="var(--accent)" stroke-width="1.5"/><rect x="286" y="162" width="20" height="20" rx="3" fill="var(--accent)" stroke="var(--accent)" stroke-width="1.5"/><text x="438" y="32" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">a</text><text x="474" y="32" text-anchor="middle" dominant-baseline="central" fill="var(--accent)" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">b</text><text x="510" y="32" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">c</text><text x="546" y="32" text-anchor="middle" dominant-baseline="central" fill="var(--accent)" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">d</text><rect x="420" y="46" width="144" height="144" rx="0" fill="none" stroke="currentColor" stroke-width="1.2"/><line x1="456" y1="46" x2="456" y2="190" stroke="var(--muted)" stroke-width="0.6" stroke-linecap="round"/><line x1="420" y1="82" x2="564" y2="82" stroke="var(--muted)" stroke-width="0.6" stroke-linecap="round"/><line x1="492" y1="46" x2="492" y2="190" stroke="var(--muted)" stroke-width="0.6" stroke-linecap="round"/><line x1="420" y1="118" x2="564" y2="118" stroke="var(--muted)" stroke-width="0.6" stroke-linecap="round"/><line x1="528" y1="46" x2="528" y2="190" stroke="var(--muted)" stroke-width="0.6" stroke-linecap="round"/><line x1="420" y1="154" x2="564" y2="154" stroke="var(--muted)" stroke-width="0.6" stroke-linecap="round"/><circle cx="438" cy="64" r="11" fill="var(--hi)" stroke="var(--hi)" stroke-width="1.5"/><circle cx="474.0" cy="64.0" r="11" fill="none" stroke="var(--hi)" stroke-width="1.2" stroke-dasharray="3 3" opacity="0.6"/><circle cx="510" cy="64" r="11" fill="var(--hi)" stroke="var(--hi)" stroke-width="1.5"/><circle cx="474.0" cy="100.0" r="11" fill="none" stroke="var(--hi)" stroke-width="1.2" stroke-dasharray="3 3" opacity="0.6"/><rect x="500" y="90" width="20" height="20" rx="3" fill="none" stroke="var(--accent)" stroke-width="1.2" stroke-dasharray="3 3"/><rect x="536" y="90" width="20" height="20" rx="3" fill="var(--accent)" stroke="var(--accent)" stroke-width="1.5"/><rect x="428" y="126" width="20" height="20" rx="3" fill="none" stroke="var(--accent)" stroke-width="1.2" stroke-dasharray="3 3"/><circle cx="510" cy="136" r="11" fill="var(--hi)" stroke="var(--hi)" stroke-width="1.5"/><circle cx="546.0" cy="136.0" r="11" fill="none" stroke="var(--hi)" stroke-width="1.2" stroke-dasharray="3 3" opacity="0.6"/><circle cx="438" cy="172" r="11" fill="var(--hi)" stroke="var(--hi)" stroke-width="1.5"/><rect x="464" y="162" width="20" height="20" rx="3" fill="var(--accent)" stroke="var(--accent)" stroke-width="1.5"/><rect x="536" y="162" width="20" height="20" rx="3" fill="var(--accent)" stroke="var(--accent)" stroke-width="1.5"/><text x="242" y="212" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">the puzzle</text><text x="492" y="212" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">a = c = True, b = d = False</text><text x="380" y="118" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:22px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">→</text></svg><figcaption><strong>Stones from a formula (Exercise 12.34).</strong> The chapter's formula (<i>a</i> ∨ <i>b</i> ∨ <i>c</i>) ∧ (<i>b</i> ∨ <i>c̄</i> ∨ <i>d̄</i>) ∧ (<i>ā</i> ∨ <i>c</i> ∨ <i>d</i>) ∧ (<i>a</i> ∨ <i>b̄</i> ∨ <i>d̄</i>): one row per clause, one column per variable, a red disc for a positive literal and a blue square for a negative one. Right: the assignment <i>a</i> = <i>c</i> = True, <i>b</i> = <i>d</i> = False keeps the red stones of columns <i>a</i>, <i>c</i> and the blue stones of <i>b</i>, <i>d</i> (removed stones dashed). Every column is one color, and every row keeps a stone because every clause has a True literal.</figcaption></figure>

## Exercise 12.38 — Three-way teams

> [!question] Exercise 12.38 (book pp. 426–427)
> The party guests must be split into three teams so that (1) every team has at least one person, (2) any two people on the same team know each other, and (3) everyone is on a team. Given the list of pairs of guests who know each other, either describe a polynomial-time algorithm that decides whether such a split exists, or prove that the problem is NP-hard.

> [!hint]- Hint
> Look at the graph of strangers. What is a team there? And what do you do about rule (1)?

> [!solution]- Solution
> NP-hard. **Reduce from** 3Color ([[2-algorithms/12-np-hardness#1210-graph-coloring-from-3sat|§12.10]]) — the chapter's rule of thumb for splitting into a few groups. A team is a set of people who all know each other, an independent set in the graph of strangers, so a legal split is a proper 3-coloring of the strangers graph that uses all three colors.
>
> **Reduction.** Given an arbitrary graph $G$, let $G'$ be $G$ plus a separate triangle $t_1t_2t_3$. The party has one guest per vertex of $G'$, and two guests know each other if and only if they are **not** adjacent in $G'$ (the complement). $n + 3$ guests; $O(n^2)$ time to list the acquainted pairs.
>
> **⇒** Given a proper 3-coloring of $G$ with colors 1, 2, 3, give $t_i$ color $i$ and let the teams be the color classes. Each team contains some $t_i$, so it is nonempty. Two guests on the same team have the same color, so they are not adjacent in $G'$ ($G$ is properly colored, the $t_i$ have distinct colors, and no edge joins $G$ to the triangle): they know each other.
>
> **⇐** Given a legal split, color each guest by team. Two guests of the same color know each other, so they are not adjacent in $G'$: the coloring of $G'$ is proper, and its restriction to $G$ is a proper 3-coloring.
>
> **Answer.** NP-hard: the guests can be split iff the complement of the acquaintance graph is 3-colorable using all three colors, which the added triangle reduces to plain 3Color; the reduction takes polynomial time.

> [!trap]
> Rule (1) is why the triangle is there. Without it, the party would be the complement of $G$ itself, and the reduction would fail exactly on graphs with fewer than three vertices: the one-vertex graph is 3-colorable, but one guest cannot form three nonempty teams. (A 3-colorable graph with at least three vertices can always be recolored to use all three colors, so special-casing $n < 3$ would also work.)

## What the conceptual exercises teach

> [!exam] Four ways a "proof" that P = NP goes wrong
> - **Pseudo-polynomial time** (12.1): $O(nM)$ is polynomial in the *values* of the numbers but exponential in their *bit lengths*.
> - **The wrong direction** (12.2(c), 12.8(c)): reducing the new problem *to* a hard one says nothing about it being hard. To prove $Y$ hard, reduce a known NP-hard problem *to* $Y$.
> - **A reduction that is not polynomial** (12.3(b)): converting CNF to DNF can take exponential time and space, and the reduction's own running time counts.
> - **A different problem** (12.4(b)): an easy variant of a hard problem (all-or-nothing clauses, two literals per clause, two colors) says nothing about the hard problem without a reduction from it.
>
> And the constants matter in both directions: 2Partition, 2Color and 2Sat are easy (12.6), while 3, 12 or 31337 are as hard as 3 (12.7, 12.16).

### Sources for this page

Exercises 12.1–12.4, 12.6, 12.7(b)(c), 12.8, 12.10, 12.16, 12.22(a)(b), 12.26, 12.34 and 12.38 of Jeff Erickson, *Algorithms* (2019), pp. 415–428 (CC BY 4.0), paraphrased; the solutions are ours. The stone-puzzle figure uses the chapter's running example formula and its satisfying assignment (Figures 12.8 and 12.15); the other figure examples are original. The special cases for tiny inputs in 12.8(a), 12.10 and 12.22(b), the reading "at most $k$" in 12.26 and the two readings of 12.16(a) are our additions. Every algorithm on the page is compared with brute force, and every reduction is run on all graphs with up to five vertices (or many random formulas and graphs, and with small values of the constants 17, 23, 42, 374, 473 and 31337 as well) and its output solved by brute force, YES ↦ YES and NO ↦ NO — checked by `tools/checks/a12x.py`.
