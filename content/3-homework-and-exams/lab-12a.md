---
title: "Lab 12a — From a yes-or-no box to the answer itself"
description: "Four problems with one idea: a polynomial-time black box that only answers yes or no is enough to find the optimum and then an optimal solution. The longest path: scan the length, then delete every edge the box says is avoidable. A largest independent set: scan the size, then delete every avoidable vertex. An optimal coloring from a box that takes only a graph: add every edge that keeps the chromatic number, and the color classes appear. A satisfying input for a circuit: And one literal at a time onto the output."
tags: [lab, algorithms, complexity]
---

*Lab 12a · November 11 · CS/ECE 374 A, Fall 2026 · decision, optimization and search problems · uses [[2-algorithms/12-np-hardness#122-p-versus-np|§12.2]], [[2-algorithms/12-np-hardness#123-np-hard-np-easy-and-np-complete|§12.3]] · concepts: [[concepts/polynomial-time-reductions|reductions]], [[concepts/independent-set|independent set]], [[concepts/graph-coloring|graph coloring]], [[concepts/satisfiability|satisfiability]] · in class: [[5-lecture-log/2026-11-10|Tue Nov 10]] · solutions: ours — no official solutions were posted*

> [!abstract] In one breath
> Each problem hands you a **magic black box** that answers a yes-or-no question in polynomial time — is there a path of length at least $L$, an independent set of size $k$, a coloring with $k$ colors, an input that satisfies this circuit — and asks for more than yes or no: the best value, or an actual best solution. The value comes from asking the box about every threshold and keeping the last yes. The solution comes from **shrinking the instance until it is the solution**: go through the pieces of the input one at a time, ask the box whether an optimal solution survives a change (delete this edge, delete this vertex, add this edge, fix this input), and keep the change whenever the answer is yes. Every answer is used to modify the instance **for good**, so the next question is about the modified instance. All four algorithms make polynomially many calls on instances no larger than the input, so they run in polynomial time if the box does. This is why the theory of NP-hardness can afford to talk about decision problems only ([[5-lecture-log/2026-11-10|lecture of Nov 10]]): a fast yes-or-no answer would give fast optimization and fast search as well.

> [!recipe] The pattern, used four times
> 1. **The optimum.** The box is monotone in its threshold (a path of length at least $L$ is a path of length at least $L - 1$; a subset of an independent set is independent; a coloring with $k$ colors is one with $k + 1$). Ask for every threshold; the answers are a run of yes followed by a run of no, and the last yes is the optimum $k^*$. Binary search needs fewer calls, but a plain scan is already polynomial when the threshold is at most the size of the graph.
> 2. **A solution.** For each piece of the input in turn, build a slightly more restricted instance and ask the box whether it still has a solution of value $k^*$. If yes, **keep the restriction**. Maintain the invariant: *the current instance has a solution of value $k^*$, and every solution of the current instance is a solution of the original.*
> 3. **Why the end result is a solution.** Every piece that survived was tested and could not be removed: every optimal solution of the current instance needs it. So an optimal solution of the final instance uses *all* that is left — what is left is the solution.
> 4. **Time.** Count the calls, note that every call is on an instance of polynomial size, and say **polynomial time**.

> [!trap] Use each answer before asking the next question
> The questions are not independent. "Is there a longest path that avoids $e$?" can be yes for $e_1$ and yes for $e_2$ although no longest path avoids both. Decide about one piece, change the instance, and only then ask about the next piece — the examples in Problems 1 and 2 show what goes wrong otherwise.

## Problem 1 — The longest path

> [!question] Problem 1
> You are given a magic black box that answers the following decision problem in polynomial time.
> - *Input:* a directed graph $G$ and a positive integer $L$. (The edges are not weighted, and $G$ is not necessarily a dag.)
> - *Output:* $\textsf{True}$ if $G$ contains a simple path of length at least $L$, and $\textsf{False}$ otherwise.
>
> (The handout's footnote: you already know how to solve this in polynomial time when $G$ is a dag, but the box works for every graph.)
>
> (a) Using the box as a subroutine, describe a polynomial-time algorithm for the optimization problem: given a directed graph $G$, compute the **length** of the longest path in $G$.
>
> (b) Using the box as a subroutine, describe a polynomial-time algorithm for the search problem: given a directed graph $G$, compute **the longest path** in $G$.
>
> *(Hint: you can use the magic box more than once.)*

Throughout, the length of a path is its number of edges, a path is simple (no repeated vertex), and $V$ and $E$ also stand for the numbers of vertices and edges. The footnote's dag case is the dynamic program of [[2-algorithms/06-depth-first-search#dynamic-programming-in-dags|§6.4]]; for general graphs the problem is NP-hard ([[2-algorithms/12-np-hardness#1213-other-useful-np-hard-problems|§12.13]]: it contains the Hamiltonian path problem), so nobody expects such a box to exist. The lab asks what would follow if it did.

### (a) The length of the longest path

> [!hint]- Hint
> How long can a simple path be? Ask the box about every possible length.

> [!solution]- Solution
> **The idea.** A simple path visits each vertex at most once, so it has at most $V - 1$ edges. There are only $V - 1$ lengths to ask about, and the answers are monotone: yes for $L = 1, \dots, L^*$ and no after that, where $L^*$ is the length we want.
>
> ```text
> LongestPathLength(G):
>     ℓ ← 0
>     for L ← 1 to V − 1
>         if Box(G, L)
>             ℓ ← L
>         else
>             return ℓ
>     return ℓ
> ```
>
> **Correctness.** If $G$ has a simple path of length at least $L\ge 2$, dropping its last edge leaves a simple path of length at least $L - 1$; so the box answers $\textsf{True}$ exactly for $L\le L^*$, and the loop returns the last $L$ with a $\textsf{True}$ answer. If even $\textsf{Box}(G, 1)$ is $\textsf{False}$, the graph has no edges and the longest path is a single vertex, of length 0 — a case the box cannot be asked about, since its $L$ must be positive.
>
> **Time.** At most $V - 1$ calls, all on $G$ itself, plus $O(V)$ work: polynomial time. Binary search over $L\in\{0, \dots, V - 1\}$ would need only $\lceil\log_2 V\rceil$ calls, but that is not required.
>
> **Answer.** The largest $L\in\{1, \dots, V - 1\}$ with $\textsf{Box}(G, L) = \textsf{True}$, or 0 if there is none; at most $V - 1$ calls.

> [!tip] When a scan is not enough
> Here the threshold is at most $V$, so trying every value is polynomial. If the edges had integer weights, the optimum could be as large as the sum of the weights, which is exponential in the number of *bits* of the input; then the scan must be replaced by binary search, whose number of calls is the number of bits of the largest possible value ([[2-algorithms/12-np-hardness#122-p-versus-np|input size means bits]]).

### (b) The longest path itself

> [!hint]- Hint
> Delete an edge and ask the box whether a path of length $L^*$ is still there. If it is, you never needed that edge.

> [!solution]- Solution
> **The idea.** We know the length $L^*$ from (a). An edge is *avoidable* if the graph without it still has a path of length $L^*$. Delete avoidable edges one at a time, each time from the graph as it currently is. When no edge is avoidable any more, the graph has been whittled down to a single longest path.
>
> ```text
> LongestPath(G):
>     L* ← LongestPathLength(G)
>     if L* = 0
>         return any single vertex
>     for every edge e of G                ⟨⟨in any order⟩⟩
>         if Box(G − e, L*)
>             G ← G − e                    ⟨⟨some longest path avoids e: delete e for good⟩⟩
>     return the edges that are left       ⟨⟨one path with L* edges⟩⟩
> ```
>
> **Correctness.** *Invariant:* the current graph is a subgraph of the input and contains a simple path of length $L^*$. It holds at the start, and an edge is deleted only after the box has confirmed that a path of length at least $L^*$ survives. Since the current graph is a subgraph of the input, it has no path longer than $L^*$, and each of its paths is a path of the input.
>
> Let $H$ be the final graph and $P$ a path of length $L^*$ in $H$. Take any edge $e$ of $H$. When $e$ was tested, the current graph $G_e$ contained $H$, and $\textsf{Box}(G_e - e, L^*)$ was $\textsf{False}$: every path of length $L^*$ in $G_e$ uses $e$. $P$ is such a path, so $P$ uses $e$. Hence every edge of $H$ lies on $P$, and $H$ has exactly the $L^*$ edges of $P$: what is left *is* a longest path of the input. To list its vertices in order, start at the one vertex with an outgoing but no incoming remaining edge and follow the edges.
>
> **Time.** At most $V - 1$ calls for the length and one call per edge: at most $V - 1 + E$ calls, each on a graph no larger than the input, plus $O(V + E)$ work per call to build $G - e$. Polynomial time.
>
> **Example.** Take the edges $a\to b$, $b\to c$, $c\to a$, $c\to d$, $d\to e$ and $b\to d$. Four calls give $L^* = 4$; there are two longest paths, $a\to b\to c\to d\to e$ and $c\to a\to b\to d\to e$. Testing the edges in the order listed: $a\to b$ is kept (both longest paths use it); $b\to c$ is deleted, because the second path avoids it; $c\to a$ is now kept; $c\to d$ is deleted; $d\to e$ and $b\to d$ are kept. What remains is $c\to a\to b\to d\to e$, after 10 calls. In the reverse order the algorithm returns the other path: which longest path you get depends on the order, and any of them is a correct answer.
>
> **Answer.** Compute $L^*$; for every edge $e$, delete $e$ if the box says that $G - e$ still has a path of length $L^*$; the surviving edges form a longest path. At most $V - 1 + E$ calls.

> [!trap] Do not test every edge against the original graph
> In the graph with the two edges $a\to b$ and $a\to c$, the longest path has one edge, and each edge alone is avoidable. Testing both against the original graph and then deleting both leaves nothing. The algorithm above deletes $a\to b$, and then finds that $a\to c$ is no longer avoidable.

## Problem 2 — A largest independent set

> [!question] Problem 2
> An **independent set** in a graph $G$ is a subset $S$ of the vertices such that no two vertices of $S$ are joined by an edge. You are given a magic black box that answers the following decision problem in polynomial time.
> - *Input:* an undirected graph $G$ and an integer $k$.
> - *Output:* $\textsf{True}$ if $G$ has an independent set of size $k$, and $\textsf{False}$ otherwise.
>
> (The handout's footnote: this is not hard to solve in polynomial time by dynamic programming when $G$ is a tree, but the box works for every graph.)
>
> (a) Using the box, describe a polynomial-time algorithm that computes the **size** of the largest independent set in a given undirected graph $G$.
>
> (b) Using the box, describe a polynomial-time algorithm that computes **an independent set of maximum size** in $G$.
>
> *(Hint: you can use the magic box more than once.)*

"Of size $k$" and "of size at least $k$" are the same question, because every subset of an independent set is independent. The tree case of the footnote is [[2-algorithms/03-dynamic-programming#310-dynamic-programming-on-trees|§3.10]]; the general problem is the NP-hard one of [[2-algorithms/12-np-hardness#127-maximum-independent-set-from-3sat|§12.7]] ([[concepts/independent-set]]).

### (a) The size of the largest independent set

> [!hint]- Hint
> The same scan as in Problem 1(a), over $k$.

> [!solution]- Solution
> **The idea.** The answers are monotone in $k$: $\textsf{True}$ for $k = 0, 1, \dots, k^*$ and $\textsf{False}$ for larger $k$, where $k^*$ is the size we want; and $k^*\le V$.
>
> ```text
> MaxIndSetSize(G):
>     k ← 0
>     while k < V and Box(G, k + 1)
>         k ← k + 1
>     return k
> ```
>
> **Correctness.** The empty set is independent, so the answer is at least 0. Removing a vertex from an independent set of size $k + 1$ leaves one of size $k$, so the loop stops at the first $\textsf{False}$, and no larger independent set exists.
>
> **Time.** At most $V$ calls on $G$: polynomial. (Binary search: $\lceil\log_2(V + 1)\rceil$ calls.)
>
> **Answer.** The largest $k\le V$ with $\textsf{Box}(G, k) = \textsf{True}$; at most $V$ calls.

### (b) A largest independent set itself

> [!hint]- Hint
> Delete a vertex — with its edges — and ask whether an independent set of size $k^*$ is still there.

> [!solution]- Solution
> **The idea.** Exactly Problem 1(b) with vertices in place of edges: a vertex is avoidable if the graph without it still has an independent set of size $k^*$. Delete avoidable vertices until none is left; the remaining vertices are the answer.
>
> ```text
> MaxIndSet(G):
>     k* ← MaxIndSetSize(G)
>     for every vertex v of G              ⟨⟨in any order⟩⟩
>         if Box(G − v, k*)
>             G ← G − v                    ⟨⟨some largest independent set avoids v⟩⟩
>     return the vertices that are left
> ```
>
> Here $G - v$ is $G$ without $v$ and without the edges at $v$.
>
> **Correctness.** *Invariant:* the current graph is an induced subgraph of the input and has an independent set of size $k^*$. So its independent sets are independent sets of the input, and none is larger than $k^*$. Let $H$ be the final graph and $S$ an independent set of size $k^*$ in $H$. For any vertex $v$ of $H$: when $v$ was tested, the current graph $G_v$ contained $H$, and $G_v - v$ had no independent set of size $k^*$, so every independent set of size $k^*$ in $G_v$ contains $v$. $S$ is one, so $v\in S$. Hence $S$ contains every vertex of $H$: the vertices that are left are exactly $S$, an independent set of maximum size.
>
> **Time.** At most $V$ calls for the size and $V$ for the deletions: at most $2V$ calls on graphs no larger than $G$. Polynomial time.
>
> **Another way.** Decide about each vertex positively instead: if $\textsf{Box}(G - N[v], k - 1)$, where $N[v]$ is $v$ together with its neighbors, put $v$ into the answer, delete $N[v]$ and lower $k$ by one; otherwise delete $v$ only. Same number of calls, same invariant (the current graph has an independent set of size $k$, and none of its vertices is adjacent to a chosen vertex).
>
> **Example.** Take the path $a - b - c - d - e$ with the extra edge $bd$. The box answers $\textsf{True}$ for $k = 1, 2, 3$ and $\textsf{False}$ for $k = 4$, so $k^* = 3$. Testing $a, b, c, d, e$ in order: without $a$ there is no independent set of size 3, so $a$ stays; $b$ is deleted; $c$ stays; $d$ is deleted; $e$ stays. The answer $\{a, c, e\}$ — the only independent set of size 3 — is found with 9 calls.
>
> **Answer.** Compute $k^*$; for every vertex $v$, delete $v$ if the box says that $G - v$ still has an independent set of size $k^*$; the surviving vertices are a largest independent set. At most $2V$ calls.

> [!trap] "In some largest independent set" is not enough
> In the graph with one edge $uv$, each of $u$ and $v$ lies in a largest independent set, but $\{u, v\}$ is not independent. Asking about every vertex separately and keeping all the yes answers fails; deleting (or committing) after each answer is what makes the answers consistent.

## Problem 3 — An optimal coloring (harder)

> [!question] Problem 3 (to think about later)
> A **proper coloring** of a graph $G = (V, E)$ is a function $c\colon V\to\{1, 2, \dots, k\}$, for some integer $k$, such that $c(u)\ne c(v)$ for every edge $uv$: every edge has endpoints of different colors. The **chromatic number** of $G$ is the minimum number of colors in a proper coloring of $G$. You are given a magic black box that answers the following decision problem in polynomial time.
> - *Input:* an undirected graph $G$ and an integer $k$.
> - *Output:* $\textsf{True}$ if $G$ has a proper coloring with $k$ colors, and $\textsf{False}$ otherwise.
>
> (The handout's footnote: for trees this is easy — the answer is $\textsf{True}$ except when $k = 1$ — but the box works for every graph.)
>
> Using the box, describe a polynomial-time algorithm for the search problem: given an undirected graph $G$, compute **a proper coloring of $G$ with the minimum possible number of colors**.
>
> *(Hint: you can use the magic box more than once. The input to the box is a graph and only a graph: vertices and edges.)*

> [!hint]- Hint
> You cannot tell the box "give $u$ color 1". But you can tell it "$u$ and $v$ must get different colors" — by adding the edge $uv$. Which pairs can be forced apart without needing another color?

> [!solution]- Solution
> **The idea.** The chromatic number $k^*$ comes from a scan, as before. For the coloring, the obstacle is the second half of the hint: the box accepts no partial coloring, only a graph. An edge is the one way to state a constraint in a graph, and it says "different colors". So take the non-adjacent pairs one at a time and **add the edge whenever the graph stays $k^*$-colorable**. At the end, every pair of vertices that is still non-adjacent *must* have the same color, and the color classes can be read off.
>
> ```text
> OptimalColoring(G):
>     k* ← 1
>     while not Box(G, k*)
>         k* ← k* + 1
>     for every pair u, v of vertices that are not adjacent in G
>         if Box(G + uv, k*)
>             G ← G + uv                   ⟨⟨u and v may differ: force them apart⟩⟩
>     ⟨⟨now "not adjacent" means "same color"⟩⟩
>     for every vertex v, in any order
>         if v is not adjacent to some vertex u that already has a color
>             c(v) ← c(u)
>         else
>             c(v) ← a new color
>     return c
> ```
>
> **Correctness.** A graph with at least one vertex needs at least one color, and $V$ colors always suffice, so the first loop stops with $k^*\le V$ equal to the chromatic number (with more colors allowed, a proper coloring stays proper).
>
> *Invariant of the second loop:* the current graph contains every edge of the input and has a proper coloring with $k^*$ colors. Any proper coloring of the current graph is therefore a proper coloring of the input.
>
> Let $H$ be the final graph and $c^*$ any proper coloring of $H$ with $k^*$ colors. Two adjacent vertices of $H$ get different colors. Two non-adjacent vertices $u, v$ of $H$ get the **same** color: the pair was tested when the current graph $G_{uv}$ was a subgraph of $H$, and $G_{uv} + uv$ was not $k^*$-colorable, so $H + uv$ is not either — but if $c^*(u)\ne c^*(v)$, then $c^*$ would be a proper $k^*$-coloring of $H + uv$. So in $H$, "not adjacent" is the same as "same color in $c^*$". In particular it is an equivalence relation, and its classes are the color classes of $c^*$: $H$ is a **complete multipartite graph**. The last loop recovers these classes without knowing $c^*$: a vertex joins the class of any earlier vertex it is not adjacent to. The result uses as many colors as $c^*$ has non-empty classes — at most $k^*$, hence exactly $k^*$, since the input has no proper coloring with fewer.
>
> **Time.** At most $V$ calls for $k^*$ and one per non-adjacent pair: at most $V + \binom{V}{2} - E$ calls, each on a graph with $V$ vertices; the last loop takes $O(V^2)$ time. Polynomial time.
>
> **Example.** The 5-cycle $a, b, c, d, e$: the box says $\textsf{False}$ for $k = 1, 2$ and $\textsf{True}$ for $k = 3$. The non-adjacent pairs in the order $ac, ad, bd, be, ce$: $ac$ is added; $ad$ is added; $bd$ is refused (with it, $a, b, c, d$ would be pairwise adjacent and need four colors); $be$ is added; $ce$ is refused ($a, c, d, e$ would be pairwise adjacent). The final graph is the complete 3-partite graph with parts $\{a\}$, $\{b, d\}$, $\{c, e\}$ — a proper 3-coloring of the cycle, found with 8 calls.
>
> **Another way.** The opposite constraint also fits into a graph: *merge* two non-adjacent vertices into one (the merged vertex inherits both neighborhoods) to say "same color". Merge whenever the box says the merged graph is still $k^*$-colorable, add the edge otherwise; when the graph has become a clique on $k^*$ vertices, each vertex of the clique stands for one color class.
>
> **Answer.** Find the chromatic number $k^*$ by a scan; add every missing edge that keeps the graph $k^*$-colorable; in the resulting graph, the classes of pairwise non-adjacent vertices are the color classes. At most $V + \binom{V}{2}$ calls.

The NP-hardness of deciding 3-colorability is [[2-algorithms/12-np-hardness#1210-graph-coloring-from-3sat|§12.10]] ([[concepts/graph-coloring]]).

## Problem 4 — A satisfying input for a circuit (harder)

> [!question] Problem 4 (to think about later)
> You are given a magic black box that answers the following decision problem in polynomial time.
> - *Input:* a boolean circuit $K$ with $n$ inputs and one output.
> - *Output:* $\textsf{True}$ if there are input values $x_1, x_2, \dots, x_n\in\{\textsf{True}, \textsf{False}\}$ that make $K$ output $\textsf{True}$, and $\textsf{False}$ otherwise.
>
> Using the box, describe a polynomial-time algorithm for the search problem: given a boolean circuit $K$ with $n$ inputs and one output, compute input values $x_1, \dots, x_n$ that make $K$ output $\textsf{True}$, or $\textsf{None}$ if there are none.
>
> *(Hint: you can use the magic box more than once.)*

> [!hint]- Hint
> Fix the inputs one at a time. How do you tell the box that $x_1$ must be $\textsf{True}$, when all it accepts is a circuit?

> [!solution]- Solution
> **The idea.** There is no optimum to find here, only a solution, and the "pieces" are the $n$ inputs. To force $x_i = \textsf{True}$ inside a circuit, feed the old output and the input $x_i$ into one new $\textsf{And}$ gate and call its output the new output; to force $x_i = \textsf{False}$, put a $\textsf{Not}$ gate between $x_i$ and the $\textsf{And}$. The new circuit still has the same $n$ inputs and one output, so the box accepts it, and it is satisfied exactly by the satisfying inputs of the old circuit that have the forced value.
>
> ```text
> SatisfyingInput(K):
>     if not Box(K)
>         return None
>     for i ← 1 to n
>         if Box(K ∧ x_i)
>             a_i ← True
>             K ← K ∧ x_i
>         else
>             a_i ← False
>             K ← K ∧ ¬x_i
>     return (a_1, a_2, …, a_n)
> ```
>
> **Correctness.** If the first call says $\textsf{False}$, there is nothing to find. Otherwise, *invariant:* before round $i$, the current circuit is satisfiable, and its satisfying inputs are exactly the satisfying inputs of the original $K$ that start with $a_1, \dots, a_{i-1}$. In round $i$, a satisfying input of the current circuit has $x_i = \textsf{True}$ or $x_i = \textsf{False}$. If the box says that $K\wedge x_i$ is satisfiable, we keep that; if not, every satisfying input has $x_i = \textsf{False}$, so $K\wedge\neg x_i$ is satisfiable. Either way the invariant holds for $i + 1$. After round $n$, the only input that can satisfy the current circuit is $(a_1, \dots, a_n)$, and the circuit is satisfiable; so $(a_1, \dots, a_n)$ satisfies it, and therefore the original $K$.
>
> **Time.** $n + 1$ calls. The circuit grows by at most two gates per round, so every call is on a circuit with at most $2n$ more gates than $K$. Polynomial time.
>
> **Example.** $K = (x_1\vee x_2)\wedge\neg(x_1\wedge x_3)$. The box says $\textsf{True}$ for $K$, for $K\wedge x_1$ and for $K\wedge x_1\wedge x_2$, and $\textsf{False}$ for $K\wedge x_1\wedge x_2\wedge x_3$. The output is $(\textsf{True}, \textsf{True}, \textsf{False})$, one of the four satisfying inputs — the first in the order that tries $\textsf{True}$ before $\textsf{False}$.
>
> **Answer.** One call to see whether a satisfying input exists; then for each input in turn, $\textsf{And}$ it onto the output, and keep it there if the circuit stays satisfiable, otherwise $\textsf{And}$ its negation: $n + 1$ calls.

CircuitSat is the first NP-hard problem of the chapter ([[2-algorithms/12-np-hardness#121-a-game-you-cant-win|§12.1]], [[concepts/satisfiability]]). The same algorithm, with clauses $(x_i)$ and $(\bar x_i)$ in place of the new gates, finds a satisfying assignment of a CNF formula from a box for Sat.

> [!exam] What this lab is for
> Nothing here is an NP-hardness proof: these are ordinary reductions *to* a problem you are given a subroutine for, the direction used all through the algorithms part of the course. What changes is the conclusion drawn from them. Since a decision box gives the optimum and a solution with polynomially many calls, a decision problem is "as hard as" its optimization and search versions, up to a polynomial factor — which is why P, NP and NP-hardness are defined for decision problems only, and why proving the decision version NP-hard is enough ([[concepts/np-hardness]]). Erickson's Exercise 12.5 is a list of further problems of this kind ([[2-algorithms/12-np-hardness-exercises|Chapter 12 exercises]] does not solve it).

### Sources for this page
CS/ECE 374 A (Fall 2026), Lab 12a handout, November 11; no official solutions were posted, so the solutions are ours. Checked by `tools/checks/labs_12a.py`, where every box is an exhaustive search that counts its calls: Problem 1 on all directed graphs with up to 4 vertices and random ones with 5–7 (the scan, binary search, monotonicity, the edge-deletion algorithm in several edge orders, the call counts, the example and the trap); Problem 2 on all graphs with up to 5 vertices, a sample with 6 and random ones with 7–9 (both algorithms, the call counts, the example and the trap); Problem 3 on all graphs with up to 5 vertices and random ones with 6–8 (the chromatic number, the complete multipartite structure of the final graph, the coloring, the example, and the merging variant); Problem 4 on every boolean function of up to 3 inputs and random circuits with 4–6 inputs, and the Sat version on random CNF formulas. The correctness arguments themselves are proofs in the text. Handout slips: none that affect a solution — "valid coloring" and "proper coloring" are used for the same thing in Problem 3, and the box of Problem 1 takes a *positive* $L$, so the edgeless graph (longest path of length 0) has to be recognized without asking it.
