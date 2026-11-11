---
title: "HW9 — more graph algorithms: dags, negative cycles and layers, worked through"
description: "Homework 9 (CS/ECE 374 A, Fall 2026) explained from the submitted solutions, each re-derived and checked: whether all start-to-boss paths of a game map have the same length (shortest and longest path in a dag), the most relics a character can collect without dying (a table indexed by vertex and health, filled in reverse topological order), whether a two-colored graph has an energetic cycle (weights +2 and −1, and Bellman–Ford's negative-cycle test), a proof that the shortest energetic closed walk is a simple cycle, and its length (layers indexed by the running balance, and Dijkstra from every vertex)."
tags: [homework, algorithms, graphs, midterm-2]
---

*Homework 9 · CS/ECE 374 A, Fall 2026 · due November 3 · more graph algorithms · the method: [[2-algorithms/06-depth-first-search#64-memoization-and-dynamic-programming|§6.4]], [[2-algorithms/08-shortest-paths|Chapter 8]], [[concepts/dynamic-programming-on-dags|dynamic programming on dags]], [[concepts/bellman-ford|Bellman–Ford]], [[concepts/graph-reductions|graph reductions]] · the rubrics: [[0-toolkit/06-how-exams-are-graded#12-dynamic-programming|how exams are graded §12]] and [[0-toolkit/06-how-exams-are-graded#13-graph-reductions|§13]] · in class: [[5-lecture-log/2026-10-27|Oct 27]], [[5-lecture-log/2026-10-29|Oct 29]] · previous: [[3-homework-and-exams/hw8-graph-algorithms|HW8]]*

> [!abstract] In one breath
> Two problems, five parts, and three tools from the two lectures before it. **A dag lets you do dynamic programming over its vertices**: Problem 1 computes the shortest and the longest path to every vertex in topological order, and then a table indexed by (vertex, health) in *reverse* topological order, because that recurrence looks at where you can go next. **A condition on counts becomes a condition on a sum** once every edge gets the right weight: in Problem 2, "fewer than a third of the edges are red" is "the weights $+2$ for red and $-1$ for blue add up to less than 0", so an energetic cycle is a negative cycle and Bellman–Ford finds it. And **what a walk has to remember goes into the vertices**: to find the *shortest* energetic cycle, layer the graph by the running balance and run Dijkstra — after proving that the shortest energetic closed walk is a simple cycle, which is what bounds the number of layers.

> [!note] Where these solutions come from
> This page writes up the solutions that were **submitted** for this homework. Every one of them was re-derived and checked by script, and the approaches agree with the posted official solutions. Where the submitted text had a slip or left a step out, the page gives the complete version, and a box titled "Changed from the submitted version" says exactly what differs.

## 0. The three tools, if you have only skimmed the notes

- **Dynamic programming on a dag.** If a function of a vertex is defined from its values at the vertex's *in*-neighbors, evaluate the vertices in **topological order**; if from its *out*-neighbors, in **reverse topological order** (postorder). You may write "for all vertices in topological order" without saying how the order is computed; it takes $O(V + E)$ time. The total work is one step per edge, not (vertices) × (largest degree). → [[5-lecture-log/2026-10-29|lecture of October 29]], [[2-algorithms/06-depth-first-search#dynamic-programming-in-dags|§6.4]]
- **Bellman–Ford as a black box.** Given a directed graph with arbitrary real edge weights and a source, it computes shortest-path distances or reports that the source can reach a **negative cycle**, in $O(VE)$ time. → [[2-algorithms/08-shortest-paths#87-relax-all-the-edges-bellmanford|§8.7]]
- **Layers.** When what is allowed next depends on a running quantity, make one copy of the graph for each of its values. The art is to bound how many values can matter. → [[concepts/graph-reductions]], [[3-homework-and-exams/hw8-graph-algorithms|HW8]]

Each part below is graded by the rubric of its form: a dynamic program by [[0-toolkit/06-how-exams-are-graded#12-dynamic-programming|§12]] (the function in English, the recurrence, the table, the order, the time), a reduction by [[0-toolkit/06-how-exams-are-graded#13-graph-reductions|§13]] (the graph, the problem on it, the algorithm, the time in the input's terms).

## 1(a). Do all paths to the boss have the same length?

> [!question] Problem 1 (setting) and part (a) (4 points)
> A game generates its maps as directed acyclic graphs $G = (V, E)$ with exactly one source, the start space $s$, and exactly one sink, the boss space $b$. The player's character (the PC) moves along edges from $s$ to $b$.
>
> (a) Describe an algorithm that decides whether **all paths from $s$ to $b$ have the same length**.

The length of a path is its number of edges.

### One number would do, if we had two

All paths from $s$ to $b$ have the same length exactly when the **shortest** one and the **longest** one have the same length. Both are easy in a dag: a path to $v$ is a path to some in-neighbor $u$ followed by the edge $u\to v$.

> [!definition] The functions
> For every vertex $v$, let $\textit{lo}(v)$ be the length of the **shortest** path from $s$ to $v$ and $\textit{hi}(v)$ the length of the **longest** path from $s$ to $v$, both in edges. The algorithm returns $\textsf{True}$ if and only if $\textit{lo}(b) = \textit{hi}(b)$.

$$
\textit{lo}(v) = \begin{cases} 0 & \text{if } v = s,\\ 1 + \min\{\textit{lo}(u) \mid u\to v\in E\} & \text{otherwise,}\end{cases}\qquad
\textit{hi}(v) = \begin{cases} 0 & \text{if } v = s,\\ 1 + \max\{\textit{hi}(u) \mid u\to v\in E\} & \text{otherwise.}\end{cases}
$$

**Why the recurrences are well defined.** $s$ is the only source, so every other vertex has an incoming edge: the minimum and the maximum are never over nothing. And every vertex is reachable from $s$: follow incoming edges backward from any vertex; in a dag this must stop, and it can only stop at the source.

**Why they are right.** The only path from $s$ to itself has no edges (a longer one would be a cycle). A path from $s$ to $v\ne s$ ends with some edge $u\to v$, and what comes before is a path from $s$ to $u$; so a shortest (longest) path to $v$ is a shortest (longest) path to some in-neighbor, plus one edge.

**Memoization:** two numbers stored at each vertex, $v.\textit{lo}$ and $v.\textit{hi}$.
**Evaluation order:** each value depends on in-neighbors, so take the vertices **in topological order**.
**Time:** a topological order takes $O(V + E)$ time; then each vertex and each edge is looked at once: $O(V + E)$ in all.

> [!example] Two small maps
> The diamond $s\to a\to b$, $s\to c\to b$: $\textit{lo}(b) = \textit{hi}(b) = 2$, so the answer is $\textsf{True}$. Replace $a\to b$ by $a\to c$ (edges $s\to a$, $s\to c$, $a\to c$, $c\to b$): now $\textit{lo}(b) = 2$ along $s, c, b$ and $\textit{hi}(b) = 3$ along $s, a, c, b$: $\textsf{False}$.

The same two computations are the dag shortest-path and longest-path algorithms of the lecture ([[2-algorithms/08-shortest-paths#85-directed-acyclic-graphs-depth-first-search|§8.5]]) with every weight 1, so the answer may also be written as a reduction: "compute the shortest and the longest $s$–$b$ distance in the dag and compare"; the posted solution gives both forms.

> [!note] Changed from the submitted version
> The submitted answer defined $\textit{lo}$ and $\textit{hi}$ and proved the recurrences, but the last step — **return whether $\textit{lo}(b) = \textit{hi}(b)$** — appeared only in the opening sentence, not as the algorithm's output; it is stated in the definition box above. Everything else is as submitted.

## 1(b). The most relics without dying

> [!question] Problem 1(b) (6 points)
> Now every space has two attributes: $\textit{Relic}(v)\in\{\textsf{False}, \textsf{True}\}$ says whether the PC acquires a relic on entering $v$, and $\textit{Damage}(v)$, a non-negative integer, is the health the PC loses on entering $v$. The PC starts at $s$ with health $k\ge 1$, an integer, and dies when its health reaches 0 or less. You may assume $\textit{Damage}(s) = 0$ and $\textit{Relic}(s) = \textsf{False}$.
>
> Describe an algorithm that computes the **maximum number of relics the PC can acquire on a path from $s$ to $b$ that it survives**, or $-\infty$ if it cannot survive any path. The running time should be a function of $\lvert V\rvert$, $\lvert E\rvert$ and $k$.

### What does the rest of the trip need to know?

The best way on from a space depends on more than the space: with a lot of health left the PC can afford a damaging detour to a relic; with little, it must take the safe way, or cannot reach the boss at all. What the rest of the trip needs to know is the current space **and the current health**. Relics already collected do not matter for what can still be collected. So the subproblems are pairs (space, health).

> [!definition] The function
> For every vertex $v$ and every integer $1\le h\le k$, let $R(v, h)$ be the **maximum number of relics the PC can still collect after $v$**, on a path from $v$ to $b$ that it survives, given that it is standing on $v$ with health $h$ (the damage and the relic of $v$ itself already taken); $R(v, h) = -\infty$ if it cannot reach $b$ alive from there. The algorithm returns $R(s, k)$.

$$
R(v, h) = \begin{cases} 0 & \text{if } v = b,\\[2pt] \max\bigl\{[\textit{Relic}(w)] + R(w,\ h - \textit{Damage}(w)) \bigm\vert v\to w\in E,\ \ h - \textit{Damage}(w)\ge 1\bigr\} & \text{otherwise,}\end{cases}
$$

where $[\textit{Relic}(w)]$ is 1 if $w$ holds a relic and 0 if not, a maximum over nothing is $-\infty$, and $-\infty + 1 = -\infty$.

**Why it is right.** At $b$ the trip is over: nothing more can be collected, so 0, for every $h\ge 1$. From any other space the PC must step along some edge $v\to w$. The step is survivable only if $h - \textit{Damage}(w)\ge 1$; it collects $[\textit{Relic}(w)]$ relics; and then the PC stands on $w$ with health $h - \textit{Damage}(w)$, from where the best continuation collects $R(w, h - \textit{Damage}(w))$ by definition. If no step is survivable, or none leads on to the boss alive, the value is $-\infty$. Entering the boss space is a step like any other: its damage and its relic count.

**Memoization:** an array $R[v][1\,..\,k]$ at every vertex — $k\lvert V\rvert$ numbers.
**Evaluation order:** $R(v, \cdot)$ uses $R(w, \cdot)$ for the **out**-neighbors $w$ of $v$, so take the vertices in **reverse topological order** (postorder) as the outer loop; $h$ in any order inside.
**Time:** a topological order in $O(V + E)$; then, for each of the $k$ values of $h$, every vertex and every edge is looked at once: $O(k(V + E))$.

> [!example] One relic, one detour
> Spaces $s, a, c, b$ with edges $s\to a\to b$ and $s\to c\to b$; $a$ holds a relic and deals 2 damage, $c$ is empty and harmless, and the boss space deals 1.
>
> | $k$ | best surviving path | answer |
> |---|---|---|
> | 1 | none: even $s, c, b$ arrives with health 0 | $-\infty$ |
> | 2 | $s, c, b$ | 0 |
> | 3 | $s, c, b$ — the path through $a$ would arrive with $3 - 2 - 1 = 0$ | 0 |
> | 4 | $s, a, b$ | 1 |
>
> In the table for $k = 4$: $R(a, 2) = 0$ but $R(a, 1) = -\infty$, since the boss still deals 1; so $R(s, 4) = 1 + R(a, 2) = 1$, while $R(s, 3) = \max\{1 + R(a, 1),\ 0 + R(c, 3)\} = 0$.

> [!trap] Where 1(b) goes wrong
> - **A function of the vertex only** — "the most relics from $v$ to $b$". It cannot say whether the PC survives; health must be a parameter.
> - **The most relics first, survival second.** For $k = 3$ above, the relic-richest path dies. The answer is 0, not 1 and not $-\infty$.
> - **Forgetting the boss's damage**, or letting health reach exactly 0: the PC must arrive with health at least 1.
> - **Filling the table in topological order.** This recurrence looks forward along edges, so the *later* vertices must be done first.

> [!note] Changed from the submitted version
> - **The evaluation order.** The submitted answer mentioned a topological sort but did not say in which direction the table is filled, nor name the table. Since $R(v, h)$ depends on the out-neighbors of $v$, the order must be **reverse** topological (postorder); with the vertices in topological order the entries needed would not be there yet. The rubric gives a point each for the memoization structure and the evaluation order.
> - The function, the recurrence, the returned value $R(s, k)$ and the time $O(k(V + E))$ are as submitted. (The submitted recurrence was typeset as a code block; it is the display above.)

## 2(a). Is there an energetic cycle?

> [!question] Problem 2 (setting) and part (a) (3 points)
> $G = (V, E)$ is a directed graph in which every edge is colored **red** or **blue** and has a positive weight $w(e)$. A path, cycle or walk is **energetic** if fewer than a third of its edges are red — with $r$ red and $b$ blue edges, if $2r < b$.
>
> (a) Describe an algorithm that determines whether $G$ contains an energetic cycle.

### Turn the count into a sum

"$2r < b$" is "$2r - b < 0$". Give every edge a **balance**: $+2$ if it is red, $-1$ if it is blue. A walk with $r$ red and $b$ blue edges has total balance $2r - b$. So:

> [!key] The observation
> A walk is energetic if and only if its total balance is negative. In particular, $G$ has an energetic cycle if and only if $G$, with the balances as edge weights, has a **negative cycle**.

**Algorithm.**
1. Add a new vertex $x$ with an edge of weight 0 to every vertex of $G$.
2. Run Bellman–Ford from $x$, with the balances as edge weights (the given weights $w$ play no role in this part).
3. Answer $\textsf{True}$ if and only if Bellman–Ford reports a negative cycle.

**Why.** Bellman–Ford detects a negative cycle exactly when one is reachable from its source ([[2-algorithms/08-shortest-paths#87-relax-all-the-edges-bellmanford|§8.7]], [[concepts/bellman-ford]]). Every vertex is reachable from $x$, so every cycle of $G$ is. And $x$ has no incoming edge, so adding it creates no new cycle.

**Time.** The new graph has $V + 1$ vertices and $E + V$ edges: $O(VE)$ (for a graph with at least as many edges as vertices; $O(V(V + E))$ in general).

A blue loop is an energetic cycle of one edge ($0 < 1$); a red loop is not.

> [!note] Changed from the submitted version
> Nothing. The weights, the extra source and the argument are as submitted.

## 2(b). The shortest energetic closed walk is a simple cycle

> [!question] Problem 2(b) (2 points)
> Prove: if $G$ contains an energetic closed walk (which may repeat vertices), then the shortest energetic closed walk is a simple cycle (no repeated vertices).

"Shortest" is by total weight $w$. A closed walk is $W = v_0\to v_1\to\cdots\to v_k$ with $v_k = v_0$ and $k\ge 1$; it **repeats a vertex** if $v_i = v_j$ for some $0\le i < j < k$, and it is a simple cycle if it does not.

### The idea: cut a closed walk at a repeated vertex

A closed walk that passes twice through the same vertex falls apart there into two closed walks. Their edges are the edges of the original, so their balances add up to the original balance — and if a sum of two numbers is negative, one of the numbers is. That one is a smaller energetic closed walk.

> [!key] Splitting lemma
> Every energetic closed walk that repeats a vertex contains an energetic closed walk that is strictly shorter and has fewer edges.

> [!proof] Proof
> Let $W = v_0\to v_1\to\cdots\to v_k = v_0$ be energetic with $v_i = v_j$ for some $0\le i < j < k$. Split it into
> $$
> W_2 = v_i\to v_{i+1}\to\cdots\to v_j\qquad\text{and}\qquad W_1 = v_0\to\cdots\to v_i = v_j\to v_{j+1}\to\cdots\to v_k .
> $$
> Both are closed walks: $W_2$ because $v_i = v_j$, and $W_1$ because it starts and ends at $v_0$ and is connected at $v_i = v_j$. $W_2$ has $j - i\ge 1$ edges and $W_1$ has $k - (j - i)\ge 1$ edges, and together they use each edge of $W$ exactly once. Hence
> $$
> \sigma(W_1) + \sigma(W_2) = \sigma(W) < 0 ,
> $$
> where $\sigma$ is the total balance of 2(a), so at least one of $\sigma(W_1)$, $\sigma(W_2)$ is negative: that walk is energetic. It has fewer edges than $W$, and since **every weight is positive** and the other part has at least one edge, its weight is strictly smaller than $w(W)$. $\blacksquare$

> [!proof] Proof of the claim
> *A shortest energetic closed walk exists.* There are infinitely many closed walks, so this needs an argument. Let $W$ be any energetic closed walk. Apply the splitting lemma as long as the current walk repeats a vertex; the number of edges drops each time, so this stops, and it stops at an energetic **simple cycle** $C$ with $w(C)\le w(W)$. So every energetic closed walk is at least as long as some energetic simple cycle. $G$ has only finitely many simple cycles; let $C^*$ be a shortest energetic one. Then no energetic closed walk is shorter than $C^*$: a shortest energetic closed walk exists, and its weight is $w(C^*)$.
>
> *Every shortest energetic closed walk is a simple cycle.* Suppose a shortest energetic closed walk repeated a vertex. By the splitting lemma it would contain a strictly shorter energetic closed walk — a contradiction. $\blacksquare$

The positive weights are used in exactly one place — "strictly shorter". With weights that may be zero or negative the claim can fail: a zero-weight detour makes a non-simple walk just as short, and a negative closed walk can be repeated to get below any length.

> [!example] A walk that is not the answer
> Vertices $a, b, c, d, e$; a red edge $a\to b$ and blue edges $b\to c$, $c\to a$ of weight 1 each; blue edges $c\to d$, $d\to e$, $e\to a$ of weight 4 each. The cycle $a, b, c$ has balance $2 - 2 = 0$: not energetic. The cycle $a, b, c, d, e$ has balance $2 - 4 = -2$: energetic, weight 14. The closed walk that goes round the short cycle and then the long one has balance $-2$ too and weight 17. Splitting it at $a$ gives back the two cycles, and the energetic one of them is shorter than the walk.

> [!note] Changed from the submitted version
> The proof's structure is as submitted: the splitting claim, an existence step, and the contradiction. Four slips were corrected.
> - **"Suppose a shortest energetic closed walk is represented by one vertex"** should read "**repeats a vertex**". As written the final step did not make sense.
> - **Where positivity is used.** The submitted text said "all edge weights are positive, so $w(W) = w(W_1) + w(W_2)$". The weights add up whatever their signs; positivity is what makes each part *strictly* lighter than the whole.
> - **References.** The balance was cited as "(1.a)" and the splitting claim as "(1.b)"; they are part 2(a) and the splitting lemma of this part.
> - The existence step spoke of "the path $W$"; $W$ is a walk.

## 2(c). The length of the shortest energetic cycle

> [!question] Problem 2(c) (5 points)
> Describe and analyze an algorithm that computes the length of the shortest energetic cycle. *(Hint: layer the graph, and use part (b) to bound the number of layers you need.)*

### What does a walk have to remember?

Whether a closed walk is energetic depends on its balance, so a walk under construction has to remember its **current balance**. Balances can be any integers, which would make infinitely many layers — and this is where part (b) pays off: we only need to find the shortest energetic closed walk, and it is a **simple cycle**, with at most $\lvert V\rvert$ edges. Every prefix of it has at most $\lvert V\rvert$ edges too, so every prefix has a balance between $-\lvert V\rvert$ (all blue) and $2\lvert V\rvert$ (all red). Layers $-\lvert V\rvert, \dots, 2\lvert V\rvert$ are enough: $3\lvert V\rvert + 1$ of them.

> [!definition] The graph
> $G' = (V', E')$ is directed, with positive edge weights.
> - **Vertices:** $(v, t)$ for every $v\in V$ and every integer $-\lvert V\rvert\le t\le 2\lvert V\rvert$ — "the walk is at $v$, and its balance so far is $t$".
> - **Edges:** for every edge $u\to v$ of $G$ and every $t$: if the edge is **red**, $(u, t)\to(v, t + 2)$; if it is **blue**, $(u, t)\to(v, t - 1)$ — whenever the new balance is still in the range. Each of these edges has the weight $w(u\to v)$.

$G'$ can have cycles (the balance goes up and down), so this is not a dag computation; but its weights are positive, so Dijkstra's algorithm applies.

**Algorithm.**
1. For every vertex $s\in V$, run Dijkstra's algorithm in $G'$ from $(s, 0)$.
2. Return the smallest $\mathit{dist}((s, 0), (s, t))$ over all $s\in V$ and all $t < 0$ — or report that there is no energetic cycle if all of these are $\infty$.

**Why it is correct.**

*What it returns is the weight of an energetic closed walk.* A path in $G'$ from $(s, 0)$ to $(s, t)$ follows a closed walk of $G$ from $s$ back to $s$, of the same weight, whose balance is $t$. If $t < 0$ that closed walk is energetic. By part (b) its weight is at least that of the shortest energetic cycle.

*It does not miss the shortest energetic cycle.* Let $C$ be a shortest energetic cycle and $s$ any vertex on it. $C$ has at most $\lvert V\rvert$ edges, so all its prefix balances lie in the range, and $C$ is a path in $G'$ from $(s, 0)$ to $(s, \sigma(C))$ of weight $w(C)$, with $\sigma(C) < 0$. The algorithm looks at this endpoint.

So the minimum is exactly the weight of the shortest energetic cycle.

**Time.** $G'$ has $(3\lvert V\rvert + 1)\lvert V\rvert = O(V^2)$ vertices and at most $(3\lvert V\rvert + 1)\lvert E\rvert = O(VE)$ edges. One run of Dijkstra's algorithm takes $O(E'\log V') = O(VE\log V)$ time; $\lvert V\rvert$ runs take

$$
O(V^2E\log V) .
$$

> [!example] The same graph as in (b)
> There the only energetic cycle is $a, b, c, d, e$, of weight 14, and the algorithm returns 14: from $(a, 0)$ the balances along it are $2, 1, 0, -1, -2$, ending at $(a, -2)$. The short cycle ends at $(a, 0)$, which is not a target.

> [!trap] Where 2(c) goes wrong
> - **Too few layers.** A simple cycle can have $\lvert V\rvert$ edges — one through every vertex — not just $\lvert V\rvert - 1$. An all-blue triangle is an energetic cycle whose balance reaches $-3 = -\lvert V\rvert$; with layers starting at $-\lvert V\rvert + 1$ it is not found.
> - **Bellman–Ford with the balances, then "the cycle it found".** That detects *an* energetic cycle (part (a)); it says nothing about the *shortest* one, which is measured in the other weights $w$.
> - **One Dijkstra run from a new source joined to every $(s, 0)$.** A path could then start at $(s, 0)$ and end at $(s', t)$ for a different vertex $s'$ — not a closed walk. Each start vertex needs its own run (or its own copy).
> - **Skipping part (b).** Without it nothing bounds the balance, and nothing says that the closed walks the search finds cannot beat every cycle.

The upper layers are more generous than necessary: a prefix with balance above $\lvert V\rvert$ could not get back below 0 within $\lvert V\rvert$ edges, so layers up to $\lvert V\rvert$ would do. The range above is the simple, safe one.

> [!note] Changed from the submitted version
> - **The edges of $G'$ were missing.** The submitted text said "each edge of $G$ becomes one edge in each layer where both endpoints exist:" and then nothing; the two rules above (red: up 2, blue: down 1, same weight) are what the sentence was leading to.
> - **The running time.** The submitted bound was $O(V^2E + V^3\log V)$ "using a binary heap". With a binary heap, one run of Dijkstra's algorithm on $G'$ costs $O(E'\log V') = O(VE\log V)$, so the total is $O(V^2E\log V)$ — the bound above and the one in the posted solution. The submitted expression is what a Fibonacci heap would give ($O(E' + V'\log V')$ per run); it is not wrong as a bound for that data structure, but it does not match the heap named, and the course's stated bound for Dijkstra's algorithm is $O(E\log V)$.
> - **Step 1 of the submitted algorithm** (first run part (a), and stop if there is no energetic cycle) is harmless but unnecessary: in that case every distance in step 2 is $\infty$.
> - The layered graph was called both $G'$ and $H$; it is $G'$ here.
>
> The layer range $-\lvert V\rvert\,..\,2\lvert V\rvert$, the choice of Dijkstra, the per-vertex runs and the correctness argument are as submitted.

## What else was on the handout

Problem 3 (practice only, not submitted) is a bus-transfer problem: the earliest arrival, then the least waiting. Problems 4 and 5 are solved on the handout: counting shortest paths (Dijkstra, then count paths in the dag of tight edges — on this site as [[2-algorithms/08-shortest-paths-exercises#exercise-813--counting-shortest-paths|Exercise 8.13]]) and shortest walks that go uphill and then downhill (two layers, "up" and "down"). None of these is worked here. More of the same kind on this site: [[3-homework-and-exams/lab-09b|Lab 9b]] (dynamic programming on dags), [[3-homework-and-exams/lab-10b|Lab 10b]], Problem 2 (arbitrage: another condition turned into a negative cycle), [[3-homework-and-exams/lab-11|Lab 11]] (a table and a layered graph for the same problem), and [[2-algorithms/08-shortest-paths-exercises#exercise-88--detecting-negative-cycles-in-fords-algorithm|Exercise 8.8]].

## Checklist

1. A function on the vertices of a dag: say **in or out** — which neighbors it depends on — and so **which order**.
2. A table with a second index (health, budget, count): its range, and the time as (values of the index) × $(V + E)$.
3. A condition on counts: can it be a **sum of edge weights**? Then negative cycles and shortest paths apply.
4. Layers: **which quantity**, **which range**, and **why that range is enough** — the step that usually needs a lemma.
5. Dijkstra's algorithm: non-negative weights, and $O(E\log V)$ on the graph you built, translated back.

### Sources for this page
The solutions are the ones submitted for Homework 9 (the PDF in the course folder's workspace), re-derived and corrected as noted in the five "Changed from the submitted version" boxes. The handout itself is not in the course folder: the problem statements are paraphrased from the handout on the course website as read through a text-extraction tool, so the wording is ours; the handout defines neither the length of a path in Problem 1 (taken as its number of edges, as in both the submitted and the posted solution) nor "shortest" in Problem 2 (taken as total weight). The posted official solutions, read the same way, take the same approach in every part and give the point values quoted. Checked by `tools/checks/hw9.py`: 1(a) against an enumeration of all start-to-boss paths of 900 random maps; 1(b) against a simulation of every path for 1,800 inputs (462 with no surviving path), with the step count; 2(a) against an enumeration of all simple cycles of 1,300 random two-colored graphs (713 with an energetic cycle); the splitting step of 2(b) on 1,360 random energetic closed walks, and the claim itself by searching closed walks with a much wider balance range; 2(c) against the enumeration of simple cycles, with the size of the layered graph, the all-blue triangle and the narrower ranges; and every example.
