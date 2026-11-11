---
title: "HW8 — graph algorithms: putting the state into the vertices, worked through"
description: "Homework 8 (CS/ECE 374 A, Fall 2026) explained from the submitted solutions, each re-derived and checked: the recipe and rubric for a graph reduction in one page, then the cheapest tram trip with a card whose stickers can be peeled (three copies of the network joined by free one-way peel edges, and Dijkstra), a walk whose labels spell a string containing 374 (the graph times a four-state DFA, and reachability), and the same for any DFA (the graph times its states) — each built from the question 'what does a traveler have to remember?'"
tags: [homework, algorithms, graphs, midterm-2]
---

*Homework 8 · CS/ECE 374 A, Fall 2026 · due October 27 · graph algorithms · the method: [[2-algorithms/05-basic-graph-algorithms#57-graph-reductions-flood-fill|§5.7]], [[concepts/graph-reductions|graph reductions]] · the rubric: [[0-toolkit/06-how-exams-are-graded#13-graph-reductions|how exams are graded §13]] · the write-up template: [[0-toolkit/02-proof-templates#22-solving-a-problem-by-graph-reduction|proof templates §22]] · in class: [[5-lecture-log/2026-10-20|Oct 20]], [[5-lecture-log/2026-10-22|Oct 22]] · next: [[3-homework-and-exams/hw9-more-graph-algorithms|HW9]]*

> [!abstract] In one breath
> Both problems look like questions about paths in the given graph, and in both the given graph is not enough, because whether a step is allowed — or what it costs — depends on something besides where you are: which stickers are still on the card, or how much of 374 the walk has already spelled. The cure is always the same. Decide **what a traveler has to remember**, make a vertex of every pair (place, memory), draw an edge wherever one step leads from one pair to another, and hand the new graph, unchanged, to a standard algorithm: Dijkstra for the cheapest trip, whatever-first search for "is there a walk at all". Problem 1 needs three copies of the network. Problem 2(a) needs four, one per state of a small DFA; Problem 2(b) is the same construction with any DFA.

> [!note] Where these solutions come from
> This page writes up the solutions that were **submitted** for this homework. Every one of them was re-derived and checked by script, and the constructions agree with the posted official solutions. Where the submitted text had a slip or left a step out, the page gives the complete version, and a box titled "Changed from the submitted version" says exactly what differs.

## 0. Graph reductions, if you have only skimmed the notes

### What a reduction is

You are not asked to invent a graph algorithm. You are asked to **build a graph** from the input so that a question you care about becomes a question a standard algorithm already answers — reachability, shortest path — and then to call that algorithm as a black box ([[2-algorithms/05-basic-graph-algorithms#57-graph-reductions-flood-fill|§5.7]]; first shown in class on [[5-lecture-log/2026-10-20|October 20]]). The answer has four parts, and the rubric pays for each:

| part | what you write | points (of 10) |
|---|---|---|
| 1. the graph | the vertices and the edges as explicit functions of the input — tuples, not "a vertex for each situation" — directed or not, and the weights if there are any | 3 |
| 2. the problem | the standard problem you solve on that graph, from which vertex to which, and why its answer is the answer to the original question | 3 |
| 3. the algorithm | the standard algorithm, called by name, not re-explained; the least specific and fastest one that does the job | 2 |
| 4. the time | in the parameters of the **original input**, not the $V$ and $E$ of the graph you built | 2 |

### The one question: what does a traveler have to remember?

If the rule for the next step depends only on the current vertex, the given graph is enough. If it depends on anything else — a count, a mode, the last move, a budget — that extra information has to be **in the vertex**. Take all pairs (vertex, memory), and draw an edge from one pair to another whenever a single step leads from the first situation to the second. This is called **graph layering** when the memory is a small counter ([[5-lecture-log/2026-10-22|lecture of October 22]], [[2-algorithms/05-basic-graph-algorithms#state-in-the-vertices-walks-of-even-length|§5.7, state in the vertices]]), and it is the product construction for DFAs in other clothes ([[1-models-of-computation/03-finite-state-machines#36-the-product-construction|Models §3.6]]).

> [!trap] What loses the points
> - **Changing the algorithm instead of the graph** — "run Dijkstra, but also keep track of the stickers". Then you owe a proof that your modified Dijkstra is correct. Put the stickers into the vertices and run Dijkstra untouched.
> - **A slower or more specific algorithm than needed**: Dijkstra where a plain search answers the question, or "breadth-first search" where only reachability matters.
> - **A running time in terms of the new graph only.**

The handout's solved problem (three jars and the fewest pouring moves to measure $k$ gallons) is the model: the vertices are the triples of jar contents, the edges are the legal moves, and breadth-first search from $(0, 0, 0)$ finds the fewest moves.

## 1. The tram card with two stickers

> [!question] Problem 1 (10 points)
> A city's trams are run by three systems, A, B and C. The network is a directed graph $G = (V, E)$: vertices are stations, and each edge $e$ is a direct connection with a system $\textit{system}(e)\in\{A, B, C\}$ and a positive cost $\textit{cost}(e)$, the price for non-members. Members of a system pay **half** on that system's connections.
>
> You have a friend's System C card with two stickers stacked on it. With both stickers on, you appear to be a member of System A. Peeling off the top sticker makes you appear to be a member of System B; peeling off both makes you appear to be a member of System C. The bottom sticker cannot be removed before the top one, stickers cannot be put back, and you may peel one or both at any stop, including the start.
>
> Describe an algorithm that returns the minimum total cost of traveling from a station $s$ to a station $t$.
>
> In the handout's example the best plan costs 21.5: ride $s\to b\to e$ as a member of A, peel the top sticker, ride $e\to d\to c\to f$ as a member of B, peel the second sticker, and ride $f\to t$ as a member of C. The handout also states the fact to use: Dijkstra's algorithm computes all distances from one vertex in a directed graph with non-negative edge weights in $O(E\log V)$ time.

### What does a traveler have to remember?

The price of the next connection depends on the station you are at **and on what the card currently shows**. So a "situation" is a pair: a station and one of the three card states A, B, C. Two kinds of step change the situation: riding a connection (the station changes, the card does not) and peeling a sticker (the card changes, the station does not, and it costs nothing). The card only ever moves A → B → C.

> [!definition] The graph
> Build a directed graph $G' = (V', E')$ with non-negative edge weights.
> - **Vertices:** $V' = V\times\{A, B, C\}$. The vertex $(v, S)$ means "at station $v$, and the card shows system $S$".
> - **Travel edges:** for every connection $e = u\to v$ of $G$ and every $S\in\{A, B, C\}$, an edge $(u, S)\to(v, S)$ of weight $\tfrac12\,\textit{cost}(e)$ if $\textit{system}(e) = S$, and $\textit{cost}(e)$ otherwise.
> - **Peel edges:** for every station $v$, the edges $(v, A)\to(v, B)$ and $(v, B)\to(v, C)$, of weight 0. There are no edges back.

### The problem on this graph, and why it is the right one

**The answer is the shortest-path distance from $(s, A)$ to $(t, C)$ in $G'$** ($\infty$ if $t$ cannot be reached at all).

*Every plan is a path of the same cost.* A plan is a sequence of rides and peels that starts at $s$ with both stickers on. Follow it in $G'$ from $(s, A)$: each ride is a travel edge in the current layer, with exactly the price the plan pays, and each peel is a peel edge of cost 0. The plan ends at some $(t, S)$; append the remaining peel edges, for free, to reach $(t, C)$. So the plan's cost is the length of a walk from $(s, A)$ to $(t, C)$.

*Every path is a plan of the same cost.* Conversely, a path from $(s, A)$ to $(t, C)$ uses peel edges only in the order A → B → C, because there are no others — that is the rule that stickers come off top first and never go back — and each of its travel edges charges half price exactly when the card shows the connection's system.

So the cheapest plan and the shortest path have the same cost. The target is $(t, C)$ alone: arriving as $(t, A)$ or $(t, B)$ is never cheaper, since the free peel edges lead on to $(t, C)$.

### The algorithm and its running time

**Algorithm:** Dijkstra's algorithm on $G'$ from $(s, A)$; return $\mathit{dist}((t, C))$. The weights are non-negative (the peel edges weigh 0, everything else is positive), which is what Dijkstra's algorithm needs ([[2-algorithms/08-shortest-paths#86-best-first-dijkstras-algorithm|§8.6]], [[concepts/dijkstras-algorithm]]).

**Time:** $G'$ has $3\lvert V\rvert$ vertices and $3\lvert E\rvert + 2\lvert V\rvert$ edges, and is built in time proportional to its size. Dijkstra's algorithm takes $O(E'\log V') = O((V + E)\log V)$ time — which is $O(E\log V)$, the bound of the posted solution, when every station has at least one connection.

> [!example] The handout's route, recomputed
> The six connections of the route are $s\to b$ (system C, cost 1), $b\to e$ (A, 9), $e\to d$ (B, 10), $d\to c$ (A, 3), $c\to f$ (B, 8) and $f\to t$ (C, 8). As a member of A: $1 + 4.5 = 5.5$. Peel. As a member of B: $5 + 3 + 4 = 12$. Peel. As a member of C: $4$. Total $21.5$. On these six edges the algorithm returns 21.5; with one card state for the whole trip the cost would be 33 (never peel), 30 (peel once at $s$) or 34.5 (peel both at $s$). Where to peel is part of the optimization, which is why the layers are needed.

> [!trap] Where Problem 1 goes wrong
> - **Halving every edge.** Charging each connection its best-case price ignores that the card cannot go back. With $s\to x$ in system C and $x\to t$ in system A, cost 10 each, the answer is 15, not 10: you can have the first discount or the second, not both.
> - **Three separate Dijkstra runs, one per system, and the best of the three.** That finds the best trip with a single card state. The cheapest plan may change state twice along the way.
> - **Peel edges in both directions.** Then the graph would allow putting a sticker back.
> - **Running time $O(E'\log V')$ with no translation** into $\lvert V\rvert$ and $\lvert E\rvert$.

> [!note] Changed from the submitted version
> Nothing in the construction, the algorithm or the bound: the submitted answer is this one. Two small things were tidied. The submitted text called the peel edges "transition self-loop edges"; they are ordinary edges between two different vertices, $(v, A)$ and $(v, B)$ — a loop would join a vertex to itself — and their count, $2\lvert V\rvert$, was right. And the correctness paragraph argued only one direction in a sentence; both directions are written out above.

## 2(a). A walk that spells a string containing 374

> [!question] Problem 2(a) (3 points)
> Let $G = (V, E)$ be a directed graph in which every vertex $v$ has a label $\ell(v)$, a decimal digit. A walk $W = \langle v_0, v_1, \dots, v_{k-1}\rangle$ spells the string $\sigma(W) = \ell(v_1)\,\ell(v_2)\cdots\ell(v_{k-1})$: the labels of its vertices in order, **without the first one**. (A walk with a single vertex spells the empty string.) Given $G$, $\ell$ and two vertices $s$ and $t$, describe an algorithm that decides whether there is a walk $W$ from $s$ to $t$ such that $\sigma(W)$ contains **374** as a substring.

Because the first label is not read, walking along an edge $u\to v$ appends exactly one symbol, $\ell(v)$, to the string: the string of a walk is the labels of the heads of its edges.

### What does a walker have to remember?

A walk may wander for a long time before, between and after the three digits. What matters about the string spelled so far is only **how much progress it has made toward 374**: nothing useful yet, it ends in 3, it ends in 37, or 374 has already appeared. That is the memory of a four-state DFA $M$ — the pattern-matching automaton for 374.

> [!definition] The DFA
> States $\{0, 1, 2, 3\}$, start state 0, accepting state 3, and transition function $\textit{next}(j, d)$:
>
> | state $j$ | $d = 3$ | $d = 7$ | $d = 4$ | any other digit |
> |---|---|---|---|---|
> | 0 | 1 | 0 | 0 | 0 |
> | 1 | 1 | 2 | 0 | 0 |
> | 2 | 1 | 0 | 3 | 0 |
> | 3 | 3 | 3 | 3 | 3 |
>
> In a state $j < 3$, $j$ is the length of the longest suffix of the input that is a prefix of 374; state 3 means that 374 has appeared, and is never left. So $M$ ends in state 3 on input $x$ if and only if $x$ contains 374.

The entries that are easy to get wrong are in the first column: a 3 always leads to state 1, even from states 1 and 2, because that 3 may be the start of a new attempt (in 3374 or 37374).

### The product graph

> [!definition] The graph
> $G' = (V', E')$ is directed, with
> - **vertices** $V' = V\times\{0, 1, 2, 3\}$ — "the walk is at $v$, and $M$ is in state $j$";
> - **edges** $(u, j)\to(v, \textit{next}(j, \ell(v)))$ for every edge $u\to v$ of $G$ and every $j\in\{0, 1, 2, 3\}$.

**Problem:** is $(t, 3)$ **reachable** from $(s, 0)$ in $G'$?

**Algorithm:** whatever-first search in $G'$ from $(s, 0)$; return $\textsf{True}$ if and only if $(t, 3)$ is marked ([[2-algorithms/05-basic-graph-algorithms#55-whatever-first-search|§5.5]], [[concepts/whatever-first-search]]).

**Time:** $\lvert V'\rvert = 4\lvert V\rvert$ and $\lvert E'\rvert = 4\lvert E\rvert$; each edge of $G'$ is computed in $O(1)$ time from the table. Building $G'$ and searching it takes $O(V + E)$ time.

### Why it is correct

> [!key] Lemma
> For every vertex $v$ and state $j$: $(v, j)$ is reachable from $(s, 0)$ in $G'$ if and only if there is a walk $W$ from $s$ to $v$ in $G$ such that $M$ is in state $j$ after reading $\sigma(W)$.

> [!proof]- Proof (click to expand)
> A walk in $G'$ that starts at $(s, 0)$ is determined by its sequence of first coordinates, because the second coordinate is forced: the edge out of $(u, j)$ over $u\to v$ goes to $(v, \textit{next}(j, \ell(v)))$ and nowhere else. So walks of $G'$ from $(s, 0)$ correspond one to one to walks of $G$ from $s$. By induction on the number of edges, the second coordinate along the way is the state of $M$ on the string spelled so far: with no edges it is 0, the state on the empty string; and one more edge $u\to v$ appends $\ell(v)$ to the string and applies $\textit{next}(\cdot, \ell(v))$ to the state. A vertex is reachable exactly when some walk leads to it.

Whatever-first search marks exactly the vertices reachable from $(s, 0)$. By the lemma, $(t, 3)$ is marked if and only if some walk $W$ from $s$ to $t$ leaves $M$ in state 3 — that is, if and only if $\sigma(W)$ contains 374.

> [!example] A four-vertex check
> Vertices $s, a, b, c$ with labels 5, 3, 7, 4 and edges $s\to a\to b\to c\to a$. The walk $s, a, b, c$ spells 374, so $(c, 3)$ is marked — and so is $(a, 3)$, by going on along $c\to a$. But $(s, 3)$ is not: no edge enters $s$. Starting **at** $a$ instead, the walk $a, b, c$ spells only 74, since the first label is not read; yet the answer for $s = a$, $t = c$ is still $\textsf{True}$, because the walk $a, b, c, a, b, c$ spells 74374.

> [!tip] Another way: guess where 374 starts
> The posted solution also gives a version without an explicit DFA: layers $\varepsilon$, 3, 37 and 374, where a walk may stay in layer $\varepsilon$ as long as it likes, may move up one layer exactly when it reads the next digit of 374, and stays in the top layer once there. A walk "guesses" where the occurrence begins, the way an NFA would, so no fallback transitions are needed. It marks $(t, 374)$ in exactly the same cases.

> [!note] Changed from the submitted version
> - **The last sentence of the correctness argument.** As submitted it read that $(t, 3)$ is marked if and only if some walk from $s$ to $t$ "leaves $M$ in state $\textit{next}(i, L(v)) = j$", which does not say what is needed. The conclusion is: some walk from $s$ to $t$ leaves $M$ **in state 3**, that is, spells a string containing 374.
> - **The lemma was stated without a proof**; the induction above fills it in.
> - **Notation.** The submission wrote the label as both $L(v)$ and $\ell(v)$ and the transition function as both $\textit{next}$ and $\delta$; the page uses $\ell$ and $\textit{next}$ throughout.
>
> The DFA table, the product graph, the algorithm and the running time are as submitted.

## 2(b). The same for any DFA

> [!question] Problem 2(b) (7 points)
> Now you are also given a DFA $M = (Q, \delta, s', A)$ over the alphabet of the labels: states $Q$, transition function $\delta$, start state $s'$ and accepting states $A$. Describe an algorithm that decides whether there is a walk $W$ from $s$ to $t$ such that $\sigma(W)\in L(M)$. The running time should be expressed in terms of $\lvert V\rvert$, $\lvert E\rvert$ and $\lvert Q\rvert$.

### Nothing in (a) used 374

The construction in (a) used the automaton only as a table to look up: "in state $j$, reading $d$, go to $\textit{next}(j, d)$". Replace the table by $\delta$.

> [!definition] The graph
> $G' = (V', E')$ is directed, with
> - **vertices** $V' = V\times Q$ — "the walk is at $v$, and $M$ is in state $q$";
> - **edges** $(u, q)\to(v, \delta(q, \ell(v)))$ for every edge $u\to v$ of $G$ and every state $q\in Q$.

**Problem:** is some vertex $(t, q)$ with $q\in A$ **reachable** from $(s, s')$ in $G'$?

**Algorithm:** whatever-first search in $G'$ from $(s, s')$; return $\textsf{True}$ if and only if some $(t, q)$ with $q\in A$ is marked.

**Correctness:** the lemma of (a) and its proof hold word for word with $\delta$ in place of $\textit{next}$ and $s'$ in place of 0: $(v, q)$ is reachable from $(s, s')$ if and only if some walk $W$ from $s$ to $v$ has $\delta^*(s', \sigma(W)) = q$. So a marked $(t, q)$ with $q\in A$ exists exactly when some walk from $s$ to $t$ spells a string that $M$ accepts.

**Time:** $\lvert V'\rvert = \lvert V\rvert\cdot\lvert Q\rvert$ and $\lvert E'\rvert = \lvert E\rvert\cdot\lvert Q\rvert$, with $O(1)$ time per edge (one lookup of $\delta$): $O((V + E)\cdot\lvert Q\rvert)$ in all. Part (a) is the case $\lvert Q\rvert = 4$.

> [!example] The edge case that the construction gets right for free
> If $s = t$, the walk with the single vertex $s$ spells the empty string, which $M$ accepts exactly when its start state is accepting. The search marks $(s, s')$ before following any edge, so the algorithm answers $\textsf{True}$ in exactly that case — with no special treatment. In (a) the same walk is harmless: the empty string does not contain 374.

> [!trap] Where Problem 2 goes wrong
> - **Reading the first label.** $\sigma(W)$ starts with $\ell(v_1)$, not $\ell(v_0)$: the search starts at $(s, s')$, not at $(s, \delta(s', \ell(s)))$.
> - **Looking for a path.** The walk may repeat vertices and edges, and sometimes must (the example in (a)). Reachability in $G'$ handles this by itself; a vertex of $G$ may be visited in several states.
> - **Simulating $M$ on "the" path found by the search.** A search finds one walk to each vertex, not all of them, and the walk that spells an accepted string may not be the one it finds. The state has to be part of the vertex.
> - **A running time without $\lvert Q\rvert$.**

> [!note] Changed from the submitted version
> Nothing of substance. The submitted lemma spoke of "a path of length $k$" in $G'$ where "a walk" is meant (a path cannot repeat vertices; reachability is the same either way), and it named the DFA's parts $(Q, \Sigma, \delta, q_0, \textit{Accept})$ where the handout writes $(Q, \delta, s', A)$; the page follows the handout.

## What else was on the handout

Problem 3 (practice only, not submitted) asks whether a maze drawn as a planar straight-line graph can be walked from Start to Finish turning only straight on or by an acute angle — the memory is the edge you arrived by. Problem 4 is the solved three-jars problem described in §0. Neither is worked here. More problems of the same kind, solved on this site: [[2-algorithms/05-basic-graph-algorithms-exercises#exercise-514--walks-of-length-divisible-by-3|Exercise 5.14]] and [[2-algorithms/08-shortest-paths-exercises#exercise-816--shortest-walk-with-a-multiple-of-3-edges|Exercise 8.16]] (a counter in the vertex), [[3-homework-and-exams/lab-09a|Lab 9a]] (six variants of one maze) and [[3-homework-and-exams/lab-11|Lab 11]] (a reduction and a dynamic program for the same problem).

## Checklist for every graph reduction you write

1. The **vertices** are written as a set of tuples built from the input; say in words what a tuple means.
2. The **edges** are written as a set, with the condition for each family, the word "directed", and the weights.
3. The **problem**: reachability or shortest path, in which graph, from which vertex to which — and one or two sentences on why that answers the question.
4. The **algorithm** by name: whatever-first search for reachability, breadth-first search for fewest edges, Dijkstra for non-negative weights.
5. The **time** in the input's own parameters: count the vertices and edges of what you built.

### Sources for this page
The solutions are the ones submitted for Homework 8 (the PDF in the course folder's workspace), re-derived and corrected as noted in the three "Changed from the submitted version" boxes. The handout itself is not in the course folder: the problem statements are paraphrased from the handout on the course website as read through a text-extraction tool, so the wording is ours, and of the example figure of Problem 1 only the six edges that its text describes are known. The posted official solutions, read the same way, use the same constructions and give the point values quoted in the headings. Checked by `tools/checks/hw8.py`: Problem 1's state graph and Dijkstra against an independent three-phase formula on 1,500 random networks and against an exhaustive search over all walks and peeling decisions on 400 small ones, the graph's size, the handout's route (21.5) and the traps; Problem 2(a)'s DFA on every digit string of length at most 5 and 20,000 longer ones, the product graph against an enumeration of walks read as strings (420 small graphs) and against an independent search (1,500 graphs), the lemma's marked set, and the posted solution's variant; Problem 2(b) against an enumeration of walks with the DFA simulated on each string (900 random graphs and DFAs), including the empty walk.
