---
title: "Midterm 2 practice test 3 — solutions"
description: "Five problems in the Midterm 2 format: three recurrences of the form aT(n/2) + n^2, two small graphs with stated properties and a memoization plan; a card game against a greedy opponent, where greedy loses and an interval dynamic program wins; the vertex of minimum remoteness by three breadth-first searches from color super-sources; the one even adjacent pair by binary search on a parity invariant; and shortest zigzag walks by Dijkstra in a forward/backward copy of the graph."
tags: [exam, midterm-2, algorithms]
---

*Midterm 2 practice test 3 · CS/ECE 374 A, Fall 2026 · five problems in the exam's format · the other tests: [[3-homework-and-exams/midterm-2-practice-1|test 1]], [[3-homework-and-exams/midterm-2-practice-2|test 2]], [[3-homework-and-exams/midterm-2-dp-practice|DP practice]] · how it is graded: [[0-toolkit/06-how-exams-are-graded|rubrics]] · on one page: [[0-toolkit/09-midterm-2-cheat-sheet|cheat sheet]]*

> [!abstract] In one breath
> **Problem 1** is short answers: $aT(n/2) + n^2$ with $a = 3, 7, 4$ lands in each of the three cases ($n^2$, $n^{\lg 7}$, $n^2\log n$); a diamond $s\to a, b\to t$ is a dag with one source, one sink and two topological orders; the same diamond with weights 1, 4 and 2, 3 has two shortest paths of length 5; and $\textsf{Huh}$ only ever increases $i$, so filling $i$ downwards is enough, $O(n^2)$. **Problem 2** is a card game against greedy Elmo: on $4, 3, 7, 1, 2$ greedy play loses $5$ to $12$ but taking the 2 first wins $9$ to $8$; because Elmo's replies are forced, $\textsf{Best}(i, j)$ — your best total from the row $C[i\,..\,j]$ when it is your turn — is an interval recurrence, $O(n^2)$. **Problem 3** finds the least remote vertex with one super-source per color and three breadth-first searches, $O(V+E)$. **Problem 4** finds the one even adjacent pair by binary search: $A[1\,..\,m]$ alternates exactly when $A[m] - A[1] - (m-1)$ is even, and that holds for $m\le i$ and fails for $m > i$, $O(\log n)$. **Problem 5** finds a shortest zigzag walk with Dijkstra in a graph with two copies of every vertex, "next edge forward" and "next edge backward", $O(E\log V)$.

## Problem 1 — Short answers

> [!question] Problem 1
> (a) Solve the recurrences $A(n) = 3A(n/2) + O(n^2)$, $\ B(n) = 7B(n/2) + O(n^2)$, $\ C(n) = 4C(n/2) + O(n^2)$.
>
> (b) Draw a directed acyclic graph with at most ten vertices, exactly one source, exactly one sink, and more than one topological order.
>
> (c) Draw a directed graph with at most ten vertices, with distinct positive edge weights, that has more than one shortest path from some vertex $s$ to some other vertex $t$.
>
> (d) Describe an appropriate memoization structure and evaluation order for the following (meaningless) recurrence, and give the running time of the resulting iterative algorithm to compute $\textsf{Huh}(1, n)$.
> $$
> \textsf{Huh}(i, k) = \begin{cases} 0 & \text{if } i > n \text{ or } k < 0\\ \min\big\{\textsf{Huh}(i+1, k-2),\ \textsf{Huh}(i+2, k-1)\big\} + A[i, k] & \text{if } A[i, k] \text{ is even}\\ \max\big\{\textsf{Huh}(i+1, k-2),\ \textsf{Huh}(i+2, k-1)\big\} - A[i, k] & \text{if } A[i, k] \text{ is odd}\end{cases}
> $$

*Method: [[concepts/recursion-trees]], [[2-algorithms/01-recursion#17-recursion-trees|§1.7]] · concepts: [[concepts/topological-sort]], [[concepts/shortest-paths]], [[concepts/memoization]]*

### (a) Three recurrences

All three have the form $a\,T(n/2) + n^2$, so the level sums of the recursion tree change by the factor $a/2^2 = a/4$.

> [!key] Answer (a)
> - $A(n) = O(n^2)$: level ratio $3/4 < 1$, the root dominates.
> - $B(n) = O(n^{\lg 7})\approx O(n^{2.81})$: level ratio $7/4 > 1$, the $7^{\lg n} = n^{\lg 7}$ leaves dominate.
> - $C(n) = O(n^2\log n)$: level ratio $4/4 = 1$, all $\lg n$ levels cost $n^2$.

### (b) and (c) Two small graphs

<!-- fig:exam-mt2p3-small-graphs -->
<figure class="cs-fig"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 560 150" width="560" height="150" role="img" style="font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-size:14px"><title>two four-vertex graphs: a diamond-shaped dag, and the same diamond with weights 1, 4 on top and 2, 3 below</title><defs><marker id="ARR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs><text x="14" y="14" text-anchor="start" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">(b)</text><text x="300" y="14" text-anchor="start" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">(c)</text><path d="M75.5,73.1 L132.2,47.9" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M75.5,86.9 L132.2,112.1" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M165.5,46.9 L222.2,72.1" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M165.5,113.1 L222.2,87.9" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M355.5,73.1 L412.2,47.9" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="380.5" y="49.9" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">1</text><path d="M445.5,46.9 L502.2,72.1" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="479.5" y="49.9" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">4</text><path d="M355.5,86.9 L412.2,112.1" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="380.5" y="110.1" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">2</text><path d="M445.5,113.1 L502.2,87.9" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="479.5" y="110.1" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">3</text><circle cx="60" cy="80" r="17" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="60" y="81" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">s</text><circle cx="150" cy="40" r="17" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="150" y="41" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">a</text><circle cx="150" cy="120" r="17" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="150" y="121" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">b</text><circle cx="240" cy="80" r="17" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="240" y="81" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">t</text><circle cx="340" cy="80" r="17" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="340" y="81" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">s</text><circle cx="430" cy="40" r="17" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="430" y="41" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">a</text><circle cx="430" cy="120" r="17" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="430" y="121" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">b</text><circle cx="520" cy="80" r="17" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="520" y="81" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">t</text></svg><figcaption><strong>Practice test 3, Problem 1(b) and (c).</strong> (b) One source <i>s</i>, one sink <i>t</i>, and two topological orders, <i>s, a, b, t</i> and <i>s, b, a, t</i>. (c) Distinct positive weights 1, 2, 3, 4, and two shortest paths from <i>s</i> to <i>t</i>, both of length 5.</figcaption></figure>

> [!key] Answer (b)
> Vertices $s, a, b, t$ and edges $s\to a$, $s\to b$, $a\to t$, $b\to t$. It is acyclic; $s$ is the only source and $t$ the only sink; $s, a, b, t$ and $s, b, a, t$ are both topological orders, because no edge joins $a$ and $b$.

> [!key] Answer (c)
> The same four vertices with $w(s\to a) = 1$, $w(a\to t) = 4$, $w(s\to b) = 2$, $w(b\to t) = 3$. The weights are distinct and positive, and the only two paths from $s$ to $t$, $s\to a\to t$ and $s\to b\to t$, both have length 5.

Distinct weights do not make shortest paths unique — only the *sums* along whole paths matter.

### (d) A memoization plan

Every reference in $\textsf{Huh}(i, k)$ goes to a strictly **larger** $i$ (by 1 or by 2); $k$ goes down, but that does not matter once $i$ has been taken care of. The first argument ranges over $1\,..\,n+2$ and the second over $-2\,..\,n$, with the base case covering $i > n$ and $k < 0$.

> [!key] Answer (d)
> **Memoization:** an array $\textsf{Huh}[1\,..\,n+2, -2\,..\,n]$ (shift the second index by 2 if negative indices are not available). **Evaluation order:** $i$ from $n+2$ down to 1 in the outer loop; $k$ in any order in the inner loop, say from $-2$ up to $n$. **Time:** $O(n^2)$ entries, $O(1)$ each: **$O(n^2)$**.

> [!exam] How this is graded
> No standard rubric covers Problem 1. For (a), the level ratio and the case; for (b) and (c), the drawing with every property checked (one source, one sink, two orders; distinct positive weights, two paths of equal length); for (d), the array with its index ranges, which loop is outer and in which direction, and the time. More practice: [[0-toolkit/08-review-algorithms#10-short-answer-drill|review §10]].

## Problem 2 — Beating Elmo at cards

> [!question] Problem 2
> The cards of a game are dealt face up in a row; each is worth a different number of points (positive, negative or zero). You and Elmo take turns removing either the leftmost or the rightmost card, until all cards are gone; whoever has collected the most points wins. Elmo always takes the card with the higher point value.
>
> (a) Prove that you should not also use the greedy strategy: show that there is a game you can win, but only if you do not follow the same greedy strategy as Elmo. Assume Elmo plays first.
>
> (b) Describe and analyze an algorithm to determine, given the initial sequence of cards, the maximum number of points that you can collect playing against Elmo.

*Template: [[0-toolkit/02-proof-templates#20-writing-up-a-dynamic-program|dynamic program]] · concept: [[concepts/dynamic-programming]] · greedy counterexamples: [[2-algorithms/03-dynamic-programming#35-warning-greed-is-stupid|§3.5]]*

### (a) Greedy loses

> [!key] Answer (a)
> Take the row $4, 3, 7, 1, 2$ (17 points), Elmo first.
>
> - **If you play greedily:** Elmo takes 4 (4 > 2); you take 3 (3 > 2); Elmo takes 7; you take 2; Elmo takes 1. You have $3 + 2 = 5$, Elmo $12$: you lose.
> - **If you do not:** Elmo takes 4; you take **2**; Elmo takes 3 (3 > 1); you take 7; Elmo takes 1. You have $2 + 7 = 9$, Elmo $8$: you win.

Taking the 3 hands Elmo the 7; taking the 2 instead leaves him a choice between 3 and 1, and the 7 comes to you.

### (b) A dynamic program

Elmo's moves are forced, so after each of your moves the next state is determined. Write $\textsf{Elmo}(a, b)$ for the interval that remains after Elmo moves on the row $C[a\,..\,b]$: $(a+1, b)$ if $C[a] > C[b]$, and $(a, b-1)$ otherwise (in particular when $a = b$); if $a > b$ the row is empty and $\textsf{Elmo}(a, b) = (a, b)$.

> [!key] Answer (b)
> **Function.** For $1\le i\le n+1$ and $i - 1\le j\le n$, let $\textsf{Best}(i, j)$ be the largest number of points you can collect from the row $C[i\,..\,j]$ when it is your turn to move and Elmo plays greedily from then on. Elmo moves first, so we need $\textsf{Best}(\textsf{Elmo}(1, n))$.
>
> **Recurrence.**
> $$
> \textsf{Best}(i, j) = \begin{cases} 0 & \text{if } i > j\\ \max\Big\{C[i] + \textsf{Best}\big(\textsf{Elmo}(i+1, j)\big),\ \ C[j] + \textsf{Best}\big(\textsf{Elmo}(i, j-1)\big)\Big\} & \text{if } i\le j\end{cases}
> $$
> The first option takes the left card, the second the right one; either way Elmo answers with his forced move.
>
> **Memoization.** An array $\textsf{Best}[1\,..\,n+1, 0\,..\,n]$, using the entries with $j\ge i - 1$.
>
> **Evaluation order.** Each reference is to $(i+2, j)$, $(i+1, j-1)$ or $(i, j-2)$: a later row, or the same row further left. So $i$ from $n+1$ down to 1 in the outer loop, $j$ from $i - 1$ up to $n$ in the inner loop.
>
> **Time.** $O(n^2)$ entries, $O(1)$ each (computing $\textsf{Elmo}$ is one comparison): **$O(n^2)$**.

You can beat Elmo exactly when $2\,\textsf{Best}(\textsf{Elmo}(1, n))$ exceeds the total of all cards. On the row $4, 3, 7, 1, 2$ the algorithm returns 9.

> [!exam] How this is graded
> (a) as a counterexample: a concrete row, both plays, both scores. (b) by the dynamic-programming rubric ([[0-toolkit/06-how-exams-are-graded#12-dynamic-programming|§12]]): **3** for describing $\textsf{Best}(i, j)$ — whose turn it is and that Elmo is greedy are part of the description; **4** for the recurrence, where Elmo's move must be built in (a minimax recurrence that lets Elmo play optimally answers a different question); **3** for the array, the order and $O(n^2)$.

## Problem 3 — The least remote vertex

> [!question] Problem 3
> The vertices of a directed graph $G = (V, E)$ are colored red, green or blue; the edges have no weights, and $G$ is not necessarily a dag. The **remoteness** of a vertex $v$ is the largest of three numbers: the length of a shortest path to $v$ from the closest red vertex, from the closest green vertex, and from the closest blue vertex. (If $v$ is not reachable from vertices of all three colors, it is infinitely remote.) Describe and analyze an algorithm to find a vertex of $G$ with minimum remoteness.

*Template: [[0-toolkit/02-proof-templates#22-solving-a-problem-by-graph-reduction|graph reduction]] · concepts: [[concepts/breadth-first-search]], [[concepts/graph-reductions]] · the trick: [[0-toolkit/08-review-algorithms#8-graph-reduction-tricks|a super-source]]*

"From the closest red vertex" is a shortest path with many possible starts. One new vertex in front of all of them turns it into a single-source problem.

> [!key] Answer
> - **The graph.** For each color $c\in\{\text{red}, \text{green}, \text{blue}\}$, the **directed** graph $G_c$: the vertices and edges of $G$, plus a new vertex $s_c$ with an edge $s_c\to u$ for every vertex $u$ of color $c$. No weights.
> - **The problem on it.** Single-source shortest paths (fewest edges) from $s_c$ in $G_c$, for each of the three colors. A path from $s_c$ to $v$ is an edge $s_c\to u$ followed by a path from $u$ to $v$ in $G$, so $d_c(v) = \mathit{dist}_{G_c}(s_c, v) - 1$ is the length of a shortest path to $v$ from the closest vertex of color $c$ ($\infty$ if there is none). The remoteness of $v$ is $\max\{d_{\text{red}}(v), d_{\text{green}}(v), d_{\text{blue}}(v)\}$; return a vertex where it is smallest.
> - **The algorithm.** Breadth-first search from $s_c$ in $G_c$, once for each color, then one scan over the vertices.
> - **The time.** Each $G_c$ has $V + 1$ vertices and at most $V + E$ edges, and is built in $O(V + E)$ time; each search takes $O(V + E)$; the scan $O(V)$: **$O(V + E)$** in all.

A vertex of color $c$ gets $d_c(v) = 0$, as it should: it is its own closest vertex of that color. If some color does not occur at all, every vertex is infinitely remote and any vertex is an answer.

> [!trap] Running a search from every vertex
> Breadth-first search from every red vertex separately, keeping the minimum, is correct but takes $O(V(V+E))$ time — and the rubric deducts for a slower algorithm than necessary. Reversing the graph does not help either: the paths must run *from* the colored vertices *to* $v$, which is the direction a search from $s_c$ already follows.

> [!exam] How this is graded
> Graph-reduction rubric ([[0-toolkit/06-how-exams-are-graded#13-graph-reductions|§13]]): **3** for the graph ($s_c$ and its edges, "directed"); **3** for the problem — distances from $s_c$, the "$-1$", and the max over colors and min over vertices; **2** for breadth-first search (Dijkstra would cost a point: the graph is unweighted); **2** for $O(V + E)$.

## Problem 4 — The one even pair

> [!question] Problem 4
> An array $A[1\,..\,n]$ of integers has the property that $A[i] + A[i+1]$ is even for exactly one index $i$: the elements alternate between even and odd, except for exactly one adjacent pair that are both even or both odd. Describe and analyze an efficient algorithm to find that index $i$. For example, given $A = [17, 40, 23, 72, 39, 88, 62, 13, 40, 53, 92, 21, 10, 73, 68]$, the algorithm should return 6, because $A[6] + A[7] = 88 + 62$ is even.

*Template: [[0-toolkit/02-proof-templates#18-writing-up-a-divide-and-conquer-algorithm|divide and conquer]] · concept: [[concepts/divide-and-conquer]] · more binary searches on an invariant: [[3-homework-and-exams/lab-06a|Lab 6a]]*

A scan finds $i$ in $O(n)$ time; "efficient" asks for a binary search. The test at a middle index $m$ must say on which side of $m$ the pair is. Before the pair, the parities alternate perfectly, so $A[m]$ has the parity of $A[1] + (m - 1)$; after it, they are shifted by one.

> [!key] Lemma
> *Call an index $m$ **good** if $A[m] - A[1] - (m - 1)$ is even. Then $m$ is good if and only if $m\le i$.*
>
> **Proof.** For $m\le i$, the elements $A[1], \ldots, A[m]$ alternate, so the parity changes $m - 1$ times between $A[1]$ and $A[m]$: $A[m]\equiv A[1] + (m - 1)$ modulo 2. For $m > i$, the parity changes at every step from $A[1]$ to $A[m]$ except the one from $A[i]$ to $A[i+1]$: $m - 2$ changes, so $A[m]\equiv A[1] + (m - 2)\not\equiv A[1] + (m - 1)$. $\square$

So $i$ is the **largest good index**; index 1 is good and index $n$ is not ($i\le n - 1$).

> [!key] Answer
> **What the recursive algorithm returns.** For indices $lo < hi$ with $lo$ good and $hi$ not good, $\textsf{EvenPair}(lo, hi)$ returns the index $i$ — which, by the lemma, satisfies $lo\le i < hi$. We call $\textsf{EvenPair}(1, n)$.
>
> **Base case.** If $hi = lo + 1$, return $lo$ (the lemma: $lo\le i < lo + 1$).
>
> **Divide and conquer.** Otherwise let $m = \lfloor(lo + hi)/2\rfloor$, so $lo < m < hi$. If $m$ is good, return $\textsf{EvenPair}(m, hi)$; otherwise return $\textsf{EvenPair}(lo, m)$. Either way the call's precondition holds.
>
> **Time.** $O(1)$ work per call, and $hi - lo$ halves: $T(n) = T(n/2) + O(1)$, so **$T(n) = O(\log n)$**.

On the example, $A[1] = 17$ and $m$ is good exactly when $A[m] + m$ is even; the search narrows $(1, 15)\to(1, 8)\to(4, 8)\to(6, 8)\to(6, 7)$ and returns **6**.

> [!exam] How this is graded
> Recursive-algorithm rubric ([[0-toolkit/06-how-exams-are-graded#11-recursive-algorithms|§11]]): **3** for what $\textsf{EvenPair}(lo, hi)$ returns *and its precondition* — the invariant "$lo$ good, $hi$ not good" is the description; **1** for the base case; **2** for the test at $m$ (the lemma); **2** for recursing on the correct half; **2** for $T(n) = T(n/2) + O(1) = O(\log n)$. A test that only compares $A[m]$ with $A[m+1]$ cannot tell on which side the pair lies.

## Problem 5 — Shortest zigzag walks

> [!question] Problem 5
> A **zigzag walk** in a directed graph $G$ is a sequence of vertices connected by edges of $G$, where the edges alternately point forward and backward along the sequence: the first edge points forward, the second backward, and so on. Its length is the sum of the weights of its edges, forward and backward. For example, in the handout's graph $a\to b\leftarrow d\to f\leftarrow c\to e$ is a zigzag walk of length 5 if every edge has weight 1. Given a directed graph $G$ with non-negative edge weights and two vertices $s$ and $t$, describe and analyze an algorithm to find the shortest zigzag walk from $s$ to $t$.

*Template: [[0-toolkit/02-proof-templates#22-solving-a-problem-by-graph-reduction|graph reduction]] · concepts: [[concepts/dijkstras-algorithm]], [[concepts/graph-reductions]] · the trick: [[2-algorithms/05-basic-graph-algorithms#state-in-the-vertices-walks-of-even-length|state in the vertices]]*

What the walk must remember is the direction of its **next** edge. Two copies of every vertex record it, and each edge of $G$ becomes two edges, one in each direction of travel.

> [!key] Answer
> - **The graph.** A **directed** graph $H$ with two vertices $(v, \mathrm{F})$ and $(v, \mathrm{B})$ for every vertex $v$ of $G$ — "the walk is at $v$ and its next edge must be followed forward" (F) or "backward" (B). For every edge $u\to v$ of $G$ with weight $w(u\to v)$, $H$ has the edge $(u, \mathrm{F})\to(v, \mathrm{B})$ (follow $u\to v$ forward) and the edge $(v, \mathrm{B})\to(u, \mathrm{F})$ (follow $u\to v$ backward, from $v$ to $u$), both with weight $w(u\to v)$.
> - **The problem on it.** Shortest paths from $(s, \mathrm{F})$ in $H$; the answer is $\min\{\mathit{dist}_H((s, \mathrm{F}), (t, \mathrm{F})),\ \mathit{dist}_H((s, \mathrm{F}), (t, \mathrm{B}))\}$, since a zigzag walk may end after a forward or after a backward edge. The walk itself is the predecessor path, with the second components dropped.
> - **The algorithm.** Dijkstra's algorithm from $(s, \mathrm{F})$ (all weights are non-negative).
> - **The time.** $H$ has $2V$ vertices and $2E$ edges and is built in $O(V + E)$ time; Dijkstra takes $O(E\log V)$: **$O(E\log V)$**.

**Why it is correct.** Walks in $H$ from $(s, \mathrm{F})$ correspond one-to-one to zigzag walks in $G$ from $s$, with the same length: from an F-vertex the only edges follow an edge of $G$ forward and lead to a B-vertex, and from a B-vertex the only edges follow an edge of $G$ backward and lead to an F-vertex.

<!-- fig:exam-mt2p3-zigzag -->
<figure class="cs-fig"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 620 230" width="620" height="230" role="img" style="font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-size:13px"><title>the six-vertex example graph with a zigzag walk highlighted, and the two directed edges that replace one edge in the reduction</title><defs><marker id="ARR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs><text x="10" y="14" text-anchor="start" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">the handout&#x27;s graph</text><text x="130" y="214" text-anchor="middle" dominant-baseline="central" fill="var(--accent)" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">a → b ← d → f ← c → e</text><text x="330" y="14" text-anchor="start" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">one edge u → v of weight w becomes two edges</text><text x="470" y="214" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:11.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">F: next edge forward · B: next edge backward</text><path d="M55,70 L112.5,70" fill="none" stroke="var(--accent)" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M145,70 L202.5,70" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M206.8,77.1 Q130,118 55.4,78.2" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M130,85 L130,152.5" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M140,81.1 L208.3,157" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M210,81.1 L141.7,157" fill="none" stroke="var(--accent)" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M220,85 L220,152.5" fill="none" stroke="var(--accent)" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M50,158.9 L118.3,83" fill="none" stroke="var(--accent)" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M115,170 L57.5,170" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M53,177.5 Q130,222 204.8,178.8" fill="none" stroke="var(--accent)" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><path d="M402,77.2 Q479.7,102.5 540.2,153.4" fill="none" stroke="var(--accent)" stroke-width="2.0" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="459.9" y="88.6" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">w</text><path d="M538,162.8 Q460.3,137.5 399.8,86.6" fill="none" stroke="var(--accent2)" stroke-width="2.0" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="480.1" y="151.4" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">w</text><circle cx="40" cy="70" r="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="40" y="71" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">a</text><circle cx="130" cy="70" r="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="130" y="71" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">b</text><circle cx="220" cy="70" r="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="220" y="71" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">c</text><circle cx="40" cy="170" r="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="40" y="171" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">d</text><circle cx="130" cy="170" r="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="130" y="171" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">e</text><circle cx="220" cy="170" r="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="220" y="171" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">f</text><rect x="358" y="55" width="44" height="30" rx="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="380" y="71" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">u,F</text><rect x="538" y="55" width="44" height="30" rx="15" fill="var(--paper)" stroke="var(--muted)" stroke-width="1.6"/><text x="560" y="71" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">v,F</text><rect x="358" y="155" width="44" height="30" rx="15" fill="var(--paper)" stroke="var(--muted)" stroke-width="1.6"/><text x="380" y="171" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">u,B</text><rect x="538" y="155" width="44" height="30" rx="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="560" y="171" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">v,B</text></svg><figcaption><strong>Zigzag walks.</strong> Left: the handout's example, every edge of weight 1; the highlighted walk <i>a → b ← d → f ← c → e</i> has length 5, and no zigzag walk from <i>a</i> to <i>e</i> is shorter. Right: the reduction. A vertex remembers whether the next edge must be followed forward (F) or backward (B); the edge <i>u → v</i> is followed forward from (<i>u</i>, F) to (<i>v</i>, B), and backward from (<i>v</i>, B) to (<i>u</i>, F).</figcaption></figure>

On the handout's graph with unit weights, the shortest zigzag walk from $a$ to $e$ has length 5, so the handout's example is a shortest one.

> [!exam] How this is graded
> Graph-reduction rubric ([[0-toolkit/06-how-exams-are-graded#13-graph-reductions|§13]]): **3** for $H$ — both copies, both edges per edge of $G$, "directed", the weights; **3** for the problem — shortest paths from $(s, \mathrm{F})$, and the minimum over the two copies of $t$; **2** for Dijkstra; **2** for $O(E\log V)$. A "modified Dijkstra that remembers the direction" earns full credit only if it is unmistakably correct; the two-copy graph is the safe answer.

### Sources for this page
Problems from the CS/ECE 374 A (Fall 2026) "Midterm 2 Practice 3" handout, paraphrased (the zigzag example graph is transcribed from the handout's figure); no official solutions were posted, so the solutions are ours. Checked by `tools/checks/exams_mt2.py` (practice test 3 section): the three recurrences numerically; both small graphs (sources, sinks, all topological orders; weights and shortest paths); the $\textsf{Huh}$ plan with a table that fails on any read before write, against the plain recursion on 300 random arrays; the card game — the recurrence against game-tree search with greedy Elmo on 400 random rows, and the counterexample's scores; remoteness by the three super-source searches against breadth-first search from every vertex on 300 random graphs; the binary search on 2000 random arrays (the right index in at most $\lceil\lg n\rceil$ steps) and on the handout's array; the two-copy graph against exhaustive search over zigzag walks on 250 random graphs, and the handout's walk and its optimality.
