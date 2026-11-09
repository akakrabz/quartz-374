---
title: "Randomized minimum cut"
description: "Global minimum cuts of an undirected multigraph by random edge contraction: GuessMinCut (Karger) finds any fixed minimum cut with probability at least 2/(n(n−1)), so a multigraph has at most n(n−1)/2 minimum cuts; amplification gives O(n⁴ log n) with high probability; Karger–Stein's recursive BetterGuess succeeds with probability Ω(1/log n) in O(n² log n) time, O(n² log³ n) overall. The note's sections are numbered 13.x and its errors are corrected."
tags: [lecture-notes, algorithms, randomized, graphs]
note: "8"
---

*Erickson, lecture notes · Director's Cut 8 · 7 pp. · [PDF](https://jeffe.cs.illinois.edu/teaching/algorithms/notes/08-mincut.pdf) · CC BY-NC-SA 4.0 · [[4-lecture-notes/index|all notes]]*

> [!abstract] In one breath
> A **cut** of a connected undirected multigraph splits its vertices into two nonempty sets; its size is the number of edges between them, and a **minimum cut** has the fewest. **Contracting** an edge merges its endpoints; every cut of the contracted graph is a cut of the original with the same edges, so contraction never lowers the minimum cut, and it raises it only by contracting an edge that lies in every minimum cut. Karger's **GuessMinCut** contracts uniformly random edges until two vertices remain: because every vertex has degree at least the cut size $k$, there are at least $kn/2$ edges, and a fixed minimum cut survives with probability at least $2/(n(n-1))$ — so there are at most $\binom n2$ minimum cuts. Repeating $O(n^2\log n)$ times finds a minimum cut with high probability in $O(n^4\log n)$ time. **Karger and Stein** observe that the early contractions are safe and the late ones dangerous: contract to about $n/2$ vertices once, then recurse four times on the result; this succeeds with probability $\Omega(1/\log n)$ in $O(n^2\log n)$ time, and $O(\log^2 n)$ repetitions give $O(n^2\log^3 n)$.

> [!note] Where this fits
> The **global** minimum cut is not the $(s,t)$-cut of [[2-algorithms/10-maximum-flows-and-minimum-cuts#102-cuts|§10.2]]: the graph is undirected, edges count by number (or multiplicity) rather than capacity, and there is no source or target — both sides only need to be nonempty. The flow-based route therefore needs many flows: fix any vertex $s$, replace each edge by two opposite directed edges of capacity 1 (per copy), and take the smallest of the $n-1$ minimum $(s,t)$-cuts over all $t\ne s$ — some $t$ lies on the other side of a global minimum cut ([[concepts/maximum-flow]]). The analysis uses [[4-lecture-notes/01-discrete-probability|discrete probability]] (independence, the bound $1 + x\le e^x$), and Karger–Stein's running time is a [[concepts/recursion-trees|recursion tree]] with equal levels. Not assigned in CS 374 this semester; CS 473 material at Illinois.

The PDF is an older lecture numbered 13 (header "Lecture 13: Randomized Minimum Cut [Sp'15]"); its sections 13.1–13.5 are 8.1–8.5 here.

## 8.1 Setting up the problem

The setting is a connected **multigraph** $G$ with $n$ vertices — parallel edges allowed, no self-loops. (Everything works for non-negative edge weights too, with more notation.) An enemy wants to split the network by cutting as few edges as possible.

> [!definition] Definition — cut, size, minimum cut
> A **cut** partitions the vertices into two **nonempty** subsets. Its **size** is the number of **crossing** edges, those with one endpoint in each subset. A **minimum cut** is a cut of smallest size; a graph may have several.

<!-- fig:n08-multigraph -->
<figure class="cs-fig"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 470 215" width="470" height="215" role="img" style="font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-size:14px"><title>eight vertices a to h; a left cluster a c d g and a right cluster b e f h joined by three edges</title><defs><marker id="ARR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs><line x1="110" y1="40" x2="30" y2="110" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><line x1="110" y1="40" x2="110" y2="180" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><line x1="110" y1="40" x2="190" y2="110" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><line x1="30" y1="110" x2="190" y2="110" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><path d="M30.0,110.0 Q77.2,136.7 110.0,180.0" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/><path d="M30.0,110.0 Q62.8,153.3 110.0,180.0" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/><line x1="110" y1="180" x2="190" y2="110" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><line x1="110" y1="40" x2="340" y2="40" stroke="var(--hi)" stroke-width="2.6" stroke-linecap="round"/><line x1="190" y1="110" x2="260" y2="110" stroke="var(--hi)" stroke-width="2.6" stroke-linecap="round"/><line x1="110" y1="180" x2="340" y2="180" stroke="var(--hi)" stroke-width="2.6" stroke-linecap="round"/><line x1="340" y1="40" x2="260" y2="110" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><line x1="340" y1="40" x2="340" y2="180" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><path d="M340.0,40.0 Q387.2,66.7 420.0,110.0" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/><path d="M340.0,40.0 Q372.8,83.3 420.0,110.0" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/><line x1="260" y1="110" x2="340" y2="180" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><line x1="340" y1="180" x2="420" y2="110" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><circle cx="110" cy="40" r="7" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="96" y="30" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">a</text><circle cx="340" cy="40" r="7" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="354" y="30" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">b</text><circle cx="30" cy="110" r="7" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="16" y="110" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">c</text><circle cx="190" cy="110" r="7" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="194" y="128" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">d</text><circle cx="260" cy="110" r="7" fill="var(--paper)" stroke="var(--hi)" stroke-width="1.6"/><text x="256" y="128" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">e</text><circle cx="420" cy="110" r="7" fill="var(--paper)" stroke="var(--hi)" stroke-width="1.6"/><text x="435" y="110" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">f</text><circle cx="110" cy="180" r="7" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="96" y="190" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">g</text><circle cx="340" cy="180" r="7" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="354" y="190" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">h</text><text x="70" y="206" text-anchor="middle" dominant-baseline="central" fill="var(--accent)" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">S = {a, c, d, g}</text><text x="390" y="206" text-anchor="middle" dominant-baseline="central" fill="var(--accent2)" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">{b, e, f, h}</text></svg><figcaption><strong>A multigraph whose minimum cut has three edges (the note’s first figure, recomputed).</strong> It has 8 vertices and 16 edges (two pairs are parallel). The thick edges <i>ab</i>, <i>de</i>, <i>gh</i> cross the cut ({<i>a</i>, <i>c</i>, <i>d</i>, <i>g</i>}, {<i>b</i>, <i>e</i>, <i>f</i>, <i>h</i>}). No cut has fewer than 3 crossing edges, and exactly two other cuts have 3: separating <i>e</i> alone or <i>f</i> alone (both have degree 3). A minimum cut need not be unique.</figcaption></figure>

**Edge contraction.** For an edge $uv$, the **contracted graph** $G/\{u,v\}$ replaces $u$ and $v$ by one new vertex $uv$: every edge $uw$ or $vw$ becomes an edge $(uv)w$, and all the edges between $u$ and $v$ disappear (they would be self-loops). Parallel edges are kept — they matter for the probabilities. With adjacency lists one contraction takes $O(n)$ time (the note leaves the details as an exercise).

<!-- fig:n08-contraction -->
<figure class="cs-fig"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 560 190" width="560" height="190" role="img" style="font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-size:14px"><title>a five-vertex multigraph with a double edge uv, and the four-vertex multigraph after contracting uv</title><defs><marker id="ARR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs><path d="M40.0,60.0 Q51.0,100.0 40.0,140.0" fill="none" stroke="var(--hi)" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/><path d="M40.0,60.0 Q29.0,100.0 40.0,140.0" fill="none" stroke="var(--hi)" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/><line x1="40" y1="60" x2="130" y2="100" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><line x1="40" y1="140" x2="130" y2="100" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><line x1="40" y1="140" x2="200" y2="150" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><line x1="130" y1="100" x2="200" y2="150" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><line x1="130" y1="100" x2="230" y2="60" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><path d="M200.0,150.0 Q204.6,101.5 230.0,60.0" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/><path d="M200.0,150.0 Q225.4,108.5 230.0,60.0" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/><path d="M350.0,100.0 Q390.0,89.0 430.0,100.0" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/><path d="M350.0,100.0 Q390.0,111.0 430.0,100.0" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/><line x1="350" y1="100" x2="500" y2="150" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><line x1="430" y1="100" x2="500" y2="150" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><line x1="430" y1="100" x2="530" y2="60" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><path d="M500.0,150.0 Q504.6,101.5 530.0,60.0" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/><path d="M500.0,150.0 Q525.4,108.5 530.0,60.0" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/><circle cx="40" cy="60" r="7" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="26" y="54" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">u</text><circle cx="40" cy="140" r="7" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="26" y="146" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">v</text><circle cx="130" cy="100" r="7" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="130" y="83" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">w</text><circle cx="200" cy="150" r="7" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="200" y="169" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">x</text><circle cx="230" cy="60" r="7" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="242" y="50" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">y</text><circle cx="350" cy="100" r="7" fill="var(--paper)" stroke="var(--hi)" stroke-width="1.6"/><text x="348" y="120" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">uv</text><circle cx="430" cy="100" r="7" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="430" y="83" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">w</text><circle cx="500" cy="150" r="7" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="500" y="169" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">x</text><circle cx="530" cy="60" r="7" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="542" y="50" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">y</text><line x1="262" y1="100" x2="322" y2="100" stroke="var(--muted)" stroke-width="1.6" stroke-linecap="round" marker-end="url(#ARR)"/><text x="292" y="86" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:11.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">contract uv</text><text x="130" y="178" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">G: 9 edges</text><text x="440" y="178" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">G/{u,v}: 7 edges</text></svg><figcaption><strong>Contracting an edge of a multigraph.</strong> Contracting (either copy of) <i>uv</i> merges <i>u</i> and <i>v</i>, deletes <em>both</em> <i>uv</i> edges (no self-loops) and keeps every other edge: <i>uw</i> and <i>vw</i> become two parallel edges. <i>G</i> has minimum cut 3, attained by four cuts — {<i>u</i>}, {<i>u</i>, <i>v</i>}, {<i>y</i>} and {<i>x</i>, <i>y</i>} against the rest. In <i>G</i>/{<i>u</i>, <i>v</i>} the minimum cut is still 3: the cut {<i>u</i>}, which the thick edges cross, is gone; the other three survive with the same three crossing edges each.</figcaption></figure>

> [!key] The contraction lemma
> The cuts of $G/\{u,v\}$ are exactly the cuts of $G$ that put $u$ and $v$ on the same side, with the same crossing edges. Hence (1) contracting an edge never decreases the minimum cut size, and (2) contracting $uv$ increases it **if and only if** $uv$ crosses **every** minimum cut of $G$.

Concept page: [[concepts/randomized-minimum-cut]].

## 8.2 Blindly guessing

```text
GuessMinCut(G):
    for i ← n downto 3
        pick a uniformly random edge e of G
        G ← G/e
    return the only cut in G
```

(The note's loop runs "downto 2", which performs $n-1$ contractions and leaves a single vertex; $n-2$ contractions leave the two vertices whose cut is returned.) **Time $O(n^2)$:** $n-2$ contractions of $O(n)$ each. By the contraction lemma, the answer is a minimum cut as long as no contracted edge crosses some fixed minimum cut.

> [!key] Karger's bound
> Fix any minimum cut $C$ of size $k$. GuessMinCut returns $C$ with probability at least
> $$
> \prod_{i=3}^{n}\frac{i-2}{i} = \frac{2}{n(n-1)} = \binom n2^{-1}.
> $$

> [!proof]- Proof (click to expand)
> Every vertex has degree at least $k$ — otherwise the cut around that vertex alone would be smaller than $C$ — so $G$ has at least $kn/2$ edges, and a uniformly random edge crosses $C$ with probability at most $k/(kn/2) = 2/n$. If it does not, $C$ is still a minimum cut of the contracted graph (the contraction lemma; its size is still $k$), which has $n-1$ vertices, and the rest of the run is GuessMinCut on that graph with independent choices. So $P(n)\ge\frac{n-2}{n}P(n-1)$ with $P(2) = 1$, and the product telescopes: $\prod_{i=3}^{n}(i-2)/\prod_{i=3}^{n} i = (n-2)!\big/\tfrac{n!}{2} = 2/(n(n-1))$. $\square$

The bound is tight: in the cycle $C_n$ every pair of edges is a minimum cut, every contraction of a cycle is a cycle, and each of the $\binom n2$ minimum cuts is returned with probability exactly $2/(n(n-1))$.

> [!example] The multigraph above, exactly
> Enumerating every contraction sequence of the 8-vertex multigraph of §8.1: GuessMinCut returns $\{a,c,d,g\}$, $\{e\}$, $\{f\}$ with probabilities about 0.117, 0.123 and 0.142 — each well above the guarantee $2/56\approx 0.036$ — and some minimum cut with probability about 0.382.

### A corollary: at most n(n−1)/2 minimum cuts

Not in the note, but immediate: the events "GuessMinCut returns $C$" for different minimum cuts $C$ are disjoint, each has probability at least $1/\binom n2$, and probabilities add up to at most 1. So **every connected multigraph has at most $\binom n2 = n(n-1)/2$ minimum cuts**, and the cycle shows that this is tight. (In contrast, a graph has $2^{n-1}-1$ cuts in all.)

## 8.3 Blindly guessing over and over

One guess is unlikely to succeed, but independent guesses can be repeated — **amplification**:

```text
KargerMinCut(G):
    mink ← ∞
    for i ← 1 to N
        X ← GuessMinCut(G)
        if |X| < mink
            mink ← |X|;  minX ← X
    return minX
```

It fails only if all $N$ independent guesses miss, so by $1 + x\le e^x$ it succeeds with probability
$$
1 - \Big(1 - \frac{2}{n(n-1)}\Big)^{N} \;\ge\; 1 - e^{-2N/(n(n-1))}.
$$
(The note prints $\le$ here; the inequality runs the other way, which is the direction a lower bound needs.) With $N = c\binom n2\ln n$ the success probability is at least $1 - e^{-c\ln n} = 1 - 1/n^c$: the algorithm is correct **with high probability** (failure probability polynomially small), in $O(n^2\log n)\cdot O(n^2) = O(n^4\log n)$ time. With $N = n^2(n-1)/2$ the failure probability is at most $e^{-n}$ — **very high probability** — which is usually overkill.

## 8.4 Not-so-blindly guessing

The danger grows as the graph shrinks: a fixed minimum cut is hit with probability at most $2/n$ by the first contraction but up to $2/3$ by the last. Contracting from $n$ down to $t$ vertices preserves a fixed minimum cut with probability at least
$$
\prod_{i=t+1}^{n}\frac{i-2}{i} = \frac{t(t-1)}{n(n-1)}, \qquad\text{which for } t = \tfrac n2 \text{ is } \frac{n-2}{4(n-1)}\approx\frac14 .
$$
David Karger and Cliff Stein's idea: do the **safe** phase once and the **dangerous** phase several times, recursively.

```text
Contract(G, t):
    for i ← n downto t + 1
        pick a uniformly random edge e of G
        G ← G/e
    return G

BetterGuess(G):
    if n is small
        return a minimum cut, by brute force
    H ← Contract(G, n/2)
    X_1 ← BetterGuess(H);  X_2 ← BetterGuess(H)
    X_3 ← BetterGuess(H);  X_4 ← BetterGuess(H)
    return the smallest of X_1, X_2, X_3, X_4
```

(Corrected from the note, whose Contract runs "downto $m$" — one contraction too many — and whose BetterGuess already has the parameter $\alpha$ of Exercise 4, `Contract(G, n/α)` and `BetterGuess(H, α)`; here $\alpha = 2$.) The four calls share $H$ but make independent random choices, so they almost always return four different cuts. Four calls balance speed against success probability: more calls succeed more often but cost more.

**Success probability.** BetterGuess returns a minimum cut if the top-level Contract preserves some minimum cut and at least one of the four calls finds a minimum cut of $H$. With $P(n)$ the success probability on $n$ vertices and independence of the calls, the note writes
$$
P(n)\;\ge\;\frac14\Big(1 - \big(1 - P(\tfrac n2)\big)^4\Big),
$$
and §8.5 shows that this forces $P(n) = \Omega(1/\log n)$. The factor $\tfrac14$ is a deliberate simplification: contracting to exactly $n/2$ vertices preserves the cut with probability $(n-2)/(4(n-1))$, slightly less than $\tfrac14$ — exactly that for cycles. Contracting to $n/2 + 1$ vertices instead gives $(n+2)/(4(n-1)) > \tfrac14$, and nothing else changes. (The note's footnote 4 claims that contracting to $\lceil n/2\rceil + 1$ vertices gives probability above $\tfrac12$; it gives about $\tfrac14$, and above $\tfrac12$ only for $n = 5$ (and trivially for $n\le 3$, where nothing is contracted). Karger and Stein's own algorithm contracts to $\lceil 1 + n/\sqrt2\,\rceil$ vertices, which does preserve the cut with probability above $\tfrac12$, and recurses twice.)

**Running time.** Contracting $n/2$ edges takes $O(n^2)$, so
$$
T(n) = O(n^2) + 4\,T(n/2) = O(n^2\log n):
$$
level $i$ of the recursion tree has $4^i$ subproblems of size $n/2^i$, costing $4^i(n/2^i)^2 = n^2$ — all $\lg n$ levels are equal.

**Amplified.** Write $P(n)\ge\alpha/\ln n$. Running BetterGuess $N = c\ln^2 n$ times fails with probability at most $(1 - \alpha/\ln n)^{c\ln^2 n}\le e^{-c\alpha\ln n} = n^{-c\alpha}$, so a minimum cut is found **with high probability in $O(n^2\log^3 n)$ time**. (The note writes the exponent as $c/\alpha$ and claims $\alpha > 2$. The proof of §8.5 gives only $\alpha = \tfrac13\ln 2\approx 0.23$ — the exact solution has $P(n)\ln n\to\tfrac23\ln 2\approx 0.46$ — and with $\alpha < 1$ the note's $1 - n^{-c/\alpha}$ does not follow; $1 - n^{-c\alpha}$ does, and the conclusion stands.)

> [!example] Exact success probabilities on a small graph
> The 8-cycle with edge multiplicities $3, 4, 4, 4, 3, 4, 4, 4$ has a unique minimum cut, the two edges of multiplicity 3 (size 6). Enumerating all contraction sequences: GuessMinCut finds it with probability about 0.068 (guarantee $2/56\approx 0.036$); BetterGuess, contracting $8\to 4\to 2$ with four calls at each level, with probability about 0.193.

Concept page: [[concepts/randomized-minimum-cut]].

## 8.5 Solving the Karger–Stein recurrence

This section is starred (optional) in the note. Let $\overline P$ satisfy the recurrence with equality, so $P(n)\ge\overline P(n)$, and let $p(k) = \overline P(2^k)$ and $d(k) = 1/p(k)$:
$$
p(k) = \frac14 - \frac14\big(1 - p(k-1)\big)^4, \qquad d(k) = \frac{4}{1 - \big(1 - \frac{1}{d(k-1)}\big)^4} = \frac{4\,d(k-1)^4}{d(k-1)^4 - \big(d(k-1)-1\big)^4}.
$$

> [!key] The inequality and the solution
> For all $x\ge 1$,
> $$
> x \;<\; \frac{4x^4}{x^4 - (x-1)^4} \;\le\; x + 3,
> $$
> so $d(k-1) < d(k)\le d(k-1) + 3$. From $P(2) = 1$, i.e. $d(1) = 1$, induction gives $d(k)\le 3k - 2$, and
> $$
> P(n)\;\ge\;\overline P(n) = \frac{1}{d(\lg n)}\;\ge\;\frac{1}{3\lg n - 2} = \Omega\Big(\frac{1}{\log n}\Big).
> $$

> [!proof]- The inequality by hand (click to expand)
> The note credits the "straightforward algebraic manipulation" to Wolfram Alpha. With $x^4 - (x-1)^4 = 4x^3 - 6x^2 + 4x - 1 > 0$ for $x\ge 1$: the right inequality is $(x+3)\big(x^4 - (x-1)^4\big) - 4x^4 = 6x^3 - 14x^2 + 11x - 3 = (x-1)(6x^2 - 8x + 3)\ge 0$, and $6x^2 - 8x + 3 > 0$ always (discriminant $-8$). The left one is $4x^4 - x\big(x^4 - (x-1)^4\big) = x(6x^2 - 4x + 1) > 0$ (discriminant $-8$ again). $\square$

The bound is not tight: the increments $d(k) - d(k-1)$ tend to $\tfrac32$, so in fact $\overline P(n)\approx 2/(3\lg n)$. The base cases in the note vary — brute force below 1000 vertices in the pseudocode, $P(n) = 1$ for $n\le 8$ in §8.4, $P(2) = 1$ here — none of which affects the asymptotics. The section ends with an unanswered to-do ("Galton–Watson process?").

## Summary

- **Global minimum cut:** a partition of the vertices of an undirected multigraph into two nonempty sides crossed by the fewest edges; no source or target, unlike the $(s,t)$-cuts of flows ($n-1$ flow computations recover it).
- **Contraction** merges two adjacent vertices, deletes the edges between them and keeps parallel edges; cuts of $G/e$ are the cuts of $G$ not crossed by $e$, so the minimum cut never decreases, and it increases only if $e$ crosses every minimum cut.
- **GuessMinCut** (contract random edges down to 2 vertices, $O(n^2)$): every vertex has degree $\ge k$, so $\ge kn/2$ edges and a fixed minimum cut survives a step with probability $\ge 1 - 2/n$; overall $\ge 2/(n(n-1))$, tight for cycles. Corollary: at most $\binom n2$ minimum cuts.
- **Amplification:** $N$ independent guesses all fail with probability $\le e^{-2N/(n(n-1))}$; $N = c\binom n2\ln n$ gives $1 - n^{-c}$, $O(n^4\log n)$ time.
- **Karger–Stein:** contract to $\approx n/2$ vertices (survival $\approx\tfrac14$), recurse four times, keep the best: $P(n)\ge\tfrac14\big(1 - (1 - P(n/2))^4\big)$, so $P(n)\ge 1/(3\lg n - 2)$; $T(n) = O(n^2) + 4T(n/2) = O(n^2\log n)$; $O(\log^2 n)$ repetitions: $O(n^2\log^3 n)$ with high probability.
- The note ends with 4 exercises (a faster GuessMinCut via minimum spanning trees, weighted cuts, the probability of finding the second-smallest cut, and BetterGuess with a general shrinking factor $\alpha$ and branching factor).

> [!exam] For CS 374
> Not assigned reading in CS/ECE 374 A this semester; randomized minimum cut is CS 473 material at Illinois. The parts that use course skills are the recursion-tree solution of $T(n) = O(n^2) + 4T(n/2)$ (the "all levels equal" case, as in Midterm 2's recurrence questions) and the contrast with the $(s,t)$-cuts of Chapter 10, which CS 374 does not examine either.

### Sources for this page
Erickson, lecture note "Randomized Minimum Cut" (Director's Cut 8; the PDF is headed "Lecture 13: Randomized Minimum Cut [Sp'15]" and numbers its sections 13.1–13.5, renumbered 8.1–8.5 here; 7 pp., no status line; © 2018, CC BY-NC-SA 4.0), summarized in our own words; the 4 exercises are not solved. The definitions, algorithms, analyses and the first figure are the note's; the at-most-$\binom n2$ corollary, the flow-based comparison, the exact probabilities, the contraction figure, the proof of the §8.5 inequality and the remarks on $\alpha$ and on $3k/2$ are additions, and the parameters of Karger and Stein's original algorithm come from outside the note. **Errors in the note, corrected on the page:** p. 2, GuessMinCut's loop "for $i\leftarrow n$ downto 2" contracts $n - 1$ edges and leaves one vertex (should stop at 3); p. 2, the contraction figure is a weighted graph from the minimum-spanning-tree chapter: it shows a single contraction followed by deleting the heavier of each pair of parallel edges (Karger's contraction keeps them), its caption names $G/\{b,e\}$ and $G/\{c,d\}$ for unlabeled vertices, and the pictured $G$ has minimum cut 2 (a vertex of degree 2), not the "cut of size 1" the text mentions — not reproduced; p. 3, "$1 - (1 - \frac{2}{n(n-1)})^N\le 1 - e^{-2N/n(n-1)}$" should be $\ge$; p. 4, Contract's loop "downto $m$" contracts one edge too many; p. 4, BetterGuess calls Contract$(G, n/\alpha)$ and BetterGuess$(H,\alpha)$ with an undefined $\alpha$ (the parameter of Exercise 4); p. 4, footnote 4 ("contract to $\lceil n/2\rceil + 1$ nodes … strictly greater than 1/2") is false for $n = 4$ and every $n\ge 6$ (the probability tends to 1/4); p. 4, the safe-phase probability $(n-2)/(4(n-1))$ is below 1/4, so the recurrence's factor 1/4 needs contraction to $n/2 + 1$ vertices; p. 5, "correctly returns the minimum cut unless (1) none of the edges … are contracted and (2) all four recursive calls return the incorrect cut" garbles the condition (it fails only if a cut edge is contracted or all four calls fail); p. 5, "$\ge 1 - e^{-(c/\alpha)\ln n}$" should be $e^{-c\alpha\ln n}$, and "Karger and Stein's proof implies $\alpha > 2$" is false ($\alpha = \frac13\ln 2$ from the proof, limit $\frac23\ln 2$); pp. 4–6, inconsistent base cases. Checked by `tools/checks/n08.py`: contraction implemented on multigraphs and the contraction lemma tested edge by edge on 300 random multigraphs; the exact output distribution of GuessMinCut, by enumerating contraction sequences with exact fractions, against $2/(n(n-1))$ for every minimum cut of all 787 connected simple graphs on 3–5 vertices and 60 random multigraphs on 5–7 vertices, with equality on the cycles $C_3,\ldots,C_8$; the number of minimum cuts on all connected simple graphs with up to 6 vertices and 300 random multigraphs on 7; the first figure's graph (reconstructed from the PDF; three minimum cuts) and the second figure's; BetterGuess exactly on the 8-vertex examples; the telescoping products, footnote 4, the amplification inequalities, the recurrence and its reciprocal form for $k\le 2000$ with 60-digit arithmetic, the polynomial identities behind the §8.5 inequality, $T(n)$ exactly, and the flow-based formula against brute force on 200 random multigraphs.
