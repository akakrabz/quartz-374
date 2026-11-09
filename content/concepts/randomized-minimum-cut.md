---
title: "Randomized minimum cut"
description: "Karger's contraction algorithm for the global minimum cut of an undirected multigraph — a fixed minimum cut survives random contractions with probability at least 2/(n(n−1)), so there are at most n(n−1)/2 minimum cuts — and Karger and Stein's recursive version, O(n² log³ n) with high probability."
tags: [concept, algorithms, randomized]
aliases: ["Karger's algorithm", "Karger–Stein", "Karger-Stein", "global minimum cut", "global min cut", "edge contraction", "contraction algorithm", "GuessMinCut"]
---

> [!key] Karger's bound and the Karger–Stein algorithm (Director's Cut 8)
> A **cut** of a connected undirected multigraph $G$ splits the vertices into two nonempty sets; its size is the number of crossing edges. **Contracting** an edge $uv$ merges $u$ and $v$, deletes the edges between them and keeps all other edges, parallel ones included.
> - **GuessMinCut:** contract uniformly random edges until 2 vertices remain ($O(n^2)$ time). Every fixed minimum cut is returned with probability $\ge 2/(n(n-1))$; hence **$G$ has at most $\binom n2$ minimum cuts** (tight for the cycle $C_n$).
> - **Repeated** $c\binom n2\ln n$ times: correct with probability $\ge 1 - n^{-c}$, $O(n^4\log n)$ time.
> - **Karger–Stein:** contract to about $n/2$ vertices, recurse four times on the result, keep the best: success $\Omega(1/\log n)$, time $T(n) = O(n^2) + 4T(n/2) = O(n^2\log n)$; repeated $O(\log^2 n)$ times, $O(n^2\log^3 n)$ with high probability.

**Why it works.** The cuts of $G/\{u,v\}$ are exactly the cuts of $G$ with $u$ and $v$ on the same side, crossed by the same edges — so a run returns a fixed minimum cut $C$ unless it contracts an edge of $C$. If $C$ has $k$ edges, every vertex has degree $\ge k$ (or that vertex alone would be a smaller cut), so there are $\ge kn/2$ edges and a random one lies in $C$ with probability $\le 2/n$. Multiplying over the shrinking graph, $\prod_{i=3}^{n}(1 - 2/i) = 2/(n(n-1))$. The early contractions are almost always safe and the late ones risky; Karger–Stein repeats only the risky part.

> [!recipe] Recipe — analyzing a contraction run
> 1. Fix one minimum cut $C$ of size $k$; the run succeeds if no edge of $C$ is contracted.
> 2. With $i$ vertices left, at least $ki/2$ edges remain, so the next contraction avoids $C$ with probability $\ge (i-2)/i$.
> 3. Contracting from $n$ to $t$ vertices preserves $C$ with probability $\ge\prod_{i=t+1}^{n}\frac{i-2}{i} = \frac{t(t-1)}{n(n-1)}$.
> 4. For $N$ independent repetitions use $(1 - p)^N\le e^{-pN}$.

> [!trap]
> - **Not the $(s,t)$-cut of maximum flows**: no source or target, undirected, edges counted by multiplicity; the flow route needs $n - 1$ minimum $(s,t)$-cuts (fix $s$, try every $t$).
> - **Keep parallel edges** when contracting (only the edges between the merged vertices disappear); deleting them changes the probabilities.
> - **$n - 2$ contractions**, not $n - 1$: stop at two vertices.
> - **Randomness is in the algorithm**: the bounds hold for every input graph, as probabilities over the algorithm's choices. One run is usually wrong; the guarantee comes from repetition.
> - **Karger–Stein's $\tfrac14$** is approximate: contracting to exactly $n/2$ vertices gives $(n-2)/(4(n-1))$; contracting to $n/2 + 1$ makes $\tfrac14$ a true bound.

**Example.** $K_4$ has minimum cut 3, attained by its four single vertices. The first contraction is the same up to symmetry, leaving a vertex $x = \{a,b\}$ joined to $c$ and to $d$ by two edges each, and the edge $cd$. The second contraction picks $xc$ (probability $2/5$, leaving the cut $\{d\}$), $xd$ ($2/5$, cut $\{c\}$) or $cd$ ($1/5$, the cut $\{a,b\}\mid\{c,d\}$ of size 4). So GuessMinCut succeeds with probability $4/5$, and each of the four minimum cuts is returned with probability $1/5\ge 2/(4\cdot 3) = 1/6$. On the 4-cycle each of its six minimum cuts comes out with probability exactly $1/6$.

**Where it appears.** [[4-lecture-notes/08-randomized-minimum-cut#81-setting-up-the-problem|note 8, §8.1]] (cuts, contraction, the contraction lemma), [[4-lecture-notes/08-randomized-minimum-cut#82-blindly-guessing|§8.2]] (GuessMinCut, the bound, the number of minimum cuts), [[4-lecture-notes/08-randomized-minimum-cut#83-blindly-guessing-over-and-over|§8.3]] (amplification), [[4-lecture-notes/08-randomized-minimum-cut#84-not-so-blindly-guessing|§8.4]] (Karger–Stein), [[4-lecture-notes/08-randomized-minimum-cut#85-solving-the-kargerstein-recurrence|§8.5]] (the recurrence); compare the $(s,t)$-cuts of [[2-algorithms/10-maximum-flows-and-minimum-cuts#102-cuts|§10.2]].

Related: [[concepts/maximum-flow]] · [[concepts/graphs]] · [[concepts/recursion-trees]] · [[concepts/master-theorem]] · [[concepts/discrete-probability]] · [[concepts/minimum-spanning-trees]]
