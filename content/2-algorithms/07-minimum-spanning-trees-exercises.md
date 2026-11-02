---
title: "Chapter 7 exercises — Minimum Spanning Trees"
description: "Solutions to Exercises 7.1–7.10 of Erickson's Algorithms: the cycle property, when the minimum spanning tree is unique (the book's characterization corrected), dangerous and useful edges and reverse-delete, maximum spanning trees and feedback edge sets, updating an MST, the second smallest spanning tree, Jarník's algorithm in O(V²) time, Borůvka's algorithm by contraction, bottleneck distances, and Borůvka's algorithm with union-find (one claim corrected)."
tags: [exercises, algorithms, graphs]
---

*Solved exercises for [[2-algorithms/07-minimum-spanning-trees|Chapter 7]] · book pp. 268–272 · statements paraphrased; see the book for the originals*

These are all ten of the chapter's exercises on [[concepts/minimum-spanning-trees|minimum spanning trees]], 7.1–7.10, except the two parts marked ♥ (particularly challenging): 7.6(b), the $k$ lightest spanning trees, and 7.9(d), a widest path in linear time. None is marked ◆. Minimum spanning trees were not lectured this semester, so treat the page as practice with [[concepts/greedy-algorithms|exchange arguments]] and graph algorithms. As in the chapter, $G$ is connected and its edge weights are distinct, so "the" minimum spanning tree $T$ is well defined — except in Exercise 7.2, which is about ties. Proofs use the chapter's tools: safe and useless edges, and swapping one edge of a spanning tree for another. Two statements are wrong as printed — the "only if" half of 7.2(b), and the claim in 7.10 that $\textsf{AddSafeEdges}$ runs in $O(E)$ time — and each is pointed out where it occurs. Write your own answer before opening a solution.

> [!tip] Tools from the chapter, used below without re-proof
> - **Safe edges** ([[2-algorithms/07-minimum-spanning-trees#72-the-only-minimum-spanning-tree-algorithm|Lemma 7.2]], in the strong form the book proves): for every vertex set $S$ with $\varnothing\ne S\ne V$, the lightest edge with exactly one endpoint in $S$ is in the MST. **Useless edges** (Lemma 7.3): an edge whose endpoints lie in one component of the intermediate forest $F$ is not.
> - **Swap.** If $T$ is a spanning tree, $g = uv\notin T$, and $f$ is an edge of the path from $u$ to $v$ in $T$ (the **tree path** of $g$), then $T - f + g$ is a spanning tree: $T + g$ has exactly one cycle, the tree path plus $g$, and deleting any edge of that cycle leaves a connected graph with $V - 1$ edges.
> - **Optimality conditions** (by the swap): if $T$ is a minimum spanning tree, every edge $g\notin T$ is at least as heavy as every edge on its tree path, and every edge $f\in T$ is at most as heavy as every edge with one endpoint in each component of $T - f$. Otherwise a swap gives a lighter spanning tree. With distinct weights, "at least" and "at most" become strict.
> - **Running times:** [[2-algorithms/07-minimum-spanning-trees#75-kruskals-algorithm|Kruskal's algorithm]] $O(E\log V)$ — on a disconnected graph it returns a minimum spanning tree of every component; [[2-algorithms/07-minimum-spanning-trees#74-jarníks-prims-algorithm|Jarník's algorithm]] with a Fibonacci heap $O(E + V\log V)$; [[2-algorithms/07-minimum-spanning-trees#73-borůvkas-algorithm|Borůvka's algorithm]] $O(E\log V)$; [[concepts/whatever-first-search|whatever-first search]] $O(V+E)$.

## Exercise 7.1 — The heaviest and the lightest edge of a cycle

> [!question] Exercise 7.1 (book p. 268)
> Let $G$ be a connected graph with distinct edge weights.
>
> (a) Prove that, for every cycle of $G$, the minimum spanning tree of $G$ excludes the heaviest edge of that cycle.
>
> (b) Prove or disprove: the minimum spanning tree of $G$ contains the lightest edge of every cycle of $G$.

### (a) The cycle property

> [!hint]- Hint
> Copy the proof of Lemma 7.2: cut the tree at the heaviest edge and look where the rest of the cycle crosses the cut.

> [!solution]- Solution
> Let $C$ be a cycle, let $e = uv$ be its heaviest edge, and let $T$ be any spanning tree that contains $e$; we show that $T$ is not minimum. Deleting $e$ splits $T$ into two trees; let $S$ be the vertex set of the one that contains $u$, so $v\notin S$. The path $C - e$ leads from $u\in S$ to $v\notin S$, so it contains an edge $e'$ with exactly one endpoint in $S$. Then $e'\ne e$, so $w(e') < w(e)$, and $e'$ joins the two trees: $T' = T - e + e'$ is a spanning tree with $w(T') < w(T)$.
>
> The proof needs distinctness only once: $e$ must be *strictly* heavier than the other edges of $C$. So it shows more: **an edge that is the unique heaviest edge of some cycle lies in no minimum spanning tree**, whatever the other weights. (Without that, the claim fails: in a triangle with three equal weights, every minimum spanning tree contains a heaviest edge of the cycle.)
>
> **In the chapter's language.** Kruskal's algorithm examines $e$ after every other edge of $C$. Each of those was then added to $F$ or found useless; either way its endpoints lay in one component of $F$, and following $C - e$ so do $u$ and $v$. Hence $e$ is useless when Kruskal's algorithm reaches it, and the MST omits it.
>
> **Answer.** Swapping the heaviest edge of a cycle for another edge of the cycle that crosses the same cut gives a lighter spanning tree; equivalently, Kruskal's algorithm finds that edge useless.

### (b) The lightest edge of a cycle

> [!hint]- Hint
> The lightest edge of one cycle can be the heaviest edge of another.

> [!solution]- Solution
> **False.** Take vertices $u, v, x, y$ and edges $ux$, $xv$, $uv$, $uy$, $vy$ of weights $1, 2, 3, 4, 5$ (figure below). The edge $uv$ is the heaviest edge of the cycle $u\,x\,v$, so the MST excludes it by (a) — yet it is the lightest edge of the cycle $u\,v\,y$. Kruskal's algorithm confirms it: it adds $1$ and $2$, rejects $3$ ($u$ and $v$ are already joined through $x$), adds $4$ and rejects $5$, so $T = \{ux, xv, uy\}$, of weight $7$.
>
> What is true: Lemma 7.2 with $S = \{v\}$ puts the lightest edge *at every vertex* into the MST. The lightest edge of a cycle need not be the lightest edge at either of its endpoints.
>
> **Answer.** False: in the graph below, $uv$ is the lightest edge of the cycle $u\,v\,y$ but not in the MST.

<!-- fig:a07x-diamond -->
<figure class="cs-fig"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 520 215" width="520" height="215" role="img" style="font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-size:14px"><title>a four-vertex graph with two triangles sharing the edge uv; the minimum spanning tree avoids uv</title><defs><marker id="ARR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs><path d="M60,105 L160,40 L260,105 Z" fill="var(--accent2)" stroke="none" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" opacity="0.13"/><path d="M60,105 L160,175 L260,105 Z" fill="var(--hi)" stroke="none" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" opacity="0.1"/><line x1="70.1" y1="98.5" x2="149.9" y2="46.5" stroke="var(--accent)" stroke-width="3.4" stroke-linecap="round"/><line x1="170.1" y1="46.5" x2="249.9" y2="98.5" stroke="var(--accent)" stroke-width="3.4" stroke-linecap="round"/><line x1="72" y1="105" x2="248" y2="105" stroke="var(--hi)" stroke-width="2.2" stroke-linecap="round" stroke-dasharray="6 4"/><line x1="69.8" y1="111.9" x2="150.2" y2="168.1" stroke="var(--accent)" stroke-width="3.4" stroke-linecap="round"/><line x1="250.2" y1="111.9" x2="169.8" y2="168.1" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/><text x="104" y="63.3" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">1</text><text x="216" y="63.3" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">2</text><text x="160" y="94" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">3</text><text x="103.7" y="149" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">4</text><text x="203.7" y="131" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">5</text><circle cx="60" cy="105" r="12" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="60" y="106" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">u</text><circle cx="260" cy="105" r="12" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="260" y="106" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">v</text><circle cx="160" cy="40" r="12" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="160" y="41" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">x</text><circle cx="160" cy="175" r="12" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="160" y="176" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">y</text><text x="300" y="62" text-anchor="start" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">cycle u x v: uv is the heaviest edge</text><text x="300" y="80" text-anchor="start" dominant-baseline="central" fill="var(--muted)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">→ not in the MST, by part (a)</text><text x="300" y="140" text-anchor="start" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">cycle u v y: uv is the lightest edge</text><text x="300" y="158" text-anchor="start" dominant-baseline="central" fill="var(--muted)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">→ still not in the MST</text><text x="160" y="205" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">thick: the MST {ux, xv, uy}, weight 7</text></svg><figcaption><strong>The lightest edge of a cycle can be left out.</strong> The edge <i>uv</i> (weight 3, red dashed) lies on two cycles. It is the heaviest edge of the cycle <i>u x v</i> (blue tint), so by part (a) the MST excludes it — yet it is the lightest edge of the cycle <i>u v y</i> (red tint). The MST (thick) is {<i>ux</i>, <i>xv</i>, <i>uy</i>}.</figcaption></figure>

## Exercise 7.2 — When is the minimum spanning tree unique?

> [!question] Exercise 7.2 (book p. 268)
> Distinct weights imply a unique minimum spanning tree (Lemma 7.1), but a weaker condition already does.
>
> (a) Describe an edge-weighted graph with a unique minimum spanning tree in which two edges have the same weight.
>
> (b) Prove that $G$ has a unique minimum spanning tree if and only if both of the following hold:
> - for every partition of the vertices into two nonempty sets, the lightest edge with one endpoint in each set is unique (call this the **cut condition**);
> - every cycle of $G$ has a unique heaviest edge (the **cycle condition**).
>
> (c) Describe and analyze an algorithm that decides whether $G$ has a unique minimum spanning tree.
>
> **Correction.** The "if" half of (b) is true — each condition alone already implies uniqueness — but the "only if" half is false: the two graphs in the figure below have unique minimum spanning trees, yet the first violates the cut condition and the second the cycle condition. The solution proves what is true and gives a correct characterization.

### (a) A tie that does no harm

> [!hint]- Hint
> The book's footnote to Lemma 7.1 has a one-word answer. Find one that contains a cycle.

> [!solution]- Solution
> The triangle $a, b, c$ with $w(ab) = w(bc) = 1$ and $w(ca) = 2$. Its three spanning trees weigh $2$, $3$ and $3$, so $\{ab, bc\}$ is the only minimum spanning tree. (Any tree works too: its only spanning tree is itself.)
>
> **Answer.** A triangle with weights $1, 1, 2$.

### (b) What the two conditions do and do not say

> [!hint]- Hint
> Reread the proofs of Lemma 7.2 and Exercise 7.1(a): each needs distinct weights only on one cut or one cycle. For the converse, look again at your answer to (a).

> [!solution]- Solution
> **Two sharper lemmas.** The exchange proofs of Lemma 7.2 and Exercise 7.1(a) compare only the edges of one cut or one cycle, so with no assumption on the other weights they prove:
> - **strict cut lemma:** if $e$ is the *unique* lightest edge with exactly one endpoint in some set $S$, then every minimum spanning tree contains $e$;
> - **strict cycle lemma:** if $e$ is the *unique* heaviest edge of some cycle, then no minimum spanning tree contains $e$.
>
> **The cut condition implies uniqueness.** Let $T$ and $T'$ be minimum spanning trees and $e\in T$. Let $S$ be the vertex set of one component of $T - e$. By the cut condition the lightest edge across $S$ is unique; by the strict cut lemma it lies in $T$, and the only edge of $T$ across $S$ is $e$. So that edge is $e$, and the same lemma puts $e$ into $T'$. Hence $T\subseteq T'$, and $T = T'$ because both have $V - 1$ edges.
>
> **The cycle condition implies uniqueness.** Let $T$ and $T'$ be minimum spanning trees and $g\notin T$. By the cycle condition the cycle formed by $g$ and its tree path in $T$ has a unique heaviest edge; by the strict cycle lemma that edge is not in $T$, so it is $g$, and the same lemma keeps $g$ out of $T'$. Hence $T'\subseteq T$, so $T' = T$.
>
> **Neither condition is necessary.** The triangle of (a) has a unique minimum spanning tree, but the partition $\{b\}$, $\{a, c\}$ has two lightest crossing edges, $ab$ and $bc$. The graph $H$ with edges $ac, ax, bx, ab, bc$ of weights $1, 2, 3, 4, 4$ has the unique minimum spanning tree $\{ac, ax, bx\}$ (weight $6$; uniqueness follows from the criterion below), but its cycle $a\,b\,c$ has two heaviest edges, $ab$ and $bc$. ($H$ does satisfy the cut condition, and the triangle the cycle condition.)
>
> **A correct characterization.** Let $T$ be any minimum spanning tree of $G$. Then $T$ is the only one if and only if every edge $g\notin T$ is *strictly* heavier than every edge on its tree path.
> - ($\Leftarrow$) Then $g$ is the unique heaviest edge of the cycle it closes with $T$, so by the strict cycle lemma no minimum spanning tree contains $g$. Every minimum spanning tree is a subset of $T$, hence equal to $T$.
> - ($\Rightarrow$) If some $g\notin T$ has $w(g)\le w(f)$ for an edge $f$ on its tree path, the swap $T - f + g$ is a spanning tree of weight at most $w(T)$, hence a second minimum spanning tree.
>
> In the triangle, the non-tree edge $ca$ (weight 2) is heavier than $ab$ and $bc$; in $H$, $ab$ (4) is heavier than its tree path $2, 3$, and $bc$ (4) than $3, 2, 1$.
>
> **Answer.** Each condition alone implies a unique minimum spanning tree, but neither is necessary. Correct version: an MST $T$ is unique iff every non-tree edge is strictly the heaviest edge of the cycle it closes with $T$.

<!-- fig:a07x-unique -->
<figure class="cs-fig"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 250" width="600" height="250" role="img" style="font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-size:14px"><title>two small weighted graphs, each with a unique minimum spanning tree, one violating the cut condition and one violating the cycle condition</title><defs><marker id="ARR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs><path d="M140,14 C196,14 196,98 140,98 C84,98 84,14 140,14 Z" fill="none" stroke="var(--hi)" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="4 3"/><text x="203" y="30" text-anchor="start" dominant-baseline="central" fill="var(--hi)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">S = {b}</text><line x1="57" y1="165.3" x2="133" y2="59.7" stroke="var(--accent)" stroke-width="3.4" stroke-linecap="round"/><line x1="147" y1="59.7" x2="223" y2="165.3" stroke="var(--accent)" stroke-width="3.4" stroke-linecap="round"/><line x1="218" y1="175" x2="62" y2="175" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/><text x="86.1" y="106.1" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">1</text><text x="193.9" y="106.1" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">1</text><text x="140" y="186" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">2</text><circle cx="50" cy="175" r="12" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="50" y="176" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">a</text><circle cx="140" cy="50" r="12" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="140" y="51" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">b</text><circle cx="230" cy="175" r="12" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="230" y="176" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">c</text><text x="140" y="212" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">unique MST {ab, bc}; the cut S has</text><text x="140" y="228" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">two lightest edges (cut condition fails)</text><path d="M330,115 L540,115 L435,185 Z" fill="var(--hi)" stroke="none" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" opacity="0.1"/><line x1="340" y1="121.7" x2="425" y2="178.3" stroke="var(--accent)" stroke-width="3.4" stroke-linecap="round"/><line x1="339.8" y1="108" x2="425.2" y2="47" stroke="var(--accent)" stroke-width="3.4" stroke-linecap="round"/><line x1="530.2" y1="108" x2="444.8" y2="47" stroke="var(--accent)" stroke-width="3.4" stroke-linecap="round"/><line x1="342" y1="115" x2="528" y2="115" stroke="var(--hi)" stroke-width="2.2" stroke-linecap="round" stroke-dasharray="6 4"/><line x1="530" y1="121.7" x2="445" y2="178.3" stroke="var(--hi)" stroke-width="2.2" stroke-linecap="round" stroke-dasharray="6 4"/><text x="376.4" y="159.2" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">1</text><text x="388.9" y="86.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">2</text><text x="481.1" y="86.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">3</text><text x="435" y="104" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">4</text><text x="493.6" y="159.2" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">4</text><circle cx="330" cy="115" r="12" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="330" y="116" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">a</text><circle cx="540" cy="115" r="12" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="540" y="116" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">b</text><circle cx="435" cy="40" r="12" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="435" y="41" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">x</text><circle cx="435" cy="185" r="12" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="435" y="186" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">c</text><text x="435" y="212" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">unique MST {ac, ax, bx}; the cycle a b c has</text><text x="435" y="228" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">two heaviest edges (cycle condition fails)</text><line x1="282" y1="20" x2="282" y2="235" stroke="var(--muted)" stroke-width="0.8" stroke-linecap="round" stroke-dasharray="2 4"/></svg><figcaption><strong>Unique minimum spanning trees that break the book's conditions.</strong> Left: the triangle of part (a). Its MST {<i>ab</i>, <i>bc</i>} is unique, but the cut around <i>S</i> = {<i>b</i>} has two lightest edges. Right: the graph <i>H</i>. Its MST (thick) is unique, but the cycle <i>a b c</i> (tinted) has two heaviest edges, <i>ab</i> and <i>bc</i>. Each of them is the strictly heaviest edge of another cycle (<i>a x b</i>, and <i>b c a x</i>), so no MST uses it.</figcaption></figure>

### (c) Testing uniqueness

> [!hint]- Hint
> Run Kruskal's algorithm a second time, breaking ties *against* the tree it found the first time.

> [!solution]- Solution
> ```text
> UniqueMST(V, E):
>     T ← Kruskal(V, E)                       ⟨⟨ties broken arbitrarily⟩⟩
>     sort E by weight, placing edges not in T before edges in T of equal weight
>     T′ ← the forest built by Kruskal's loop over E in this order
>     return (T′ = T)
> ```
>
> **Correctness.** Kruskal's algorithm returns a minimum spanning tree however ties are broken ([[2-algorithms/07-minimum-spanning-trees#71-distinct-edge-weights|§7.1]]), so $T$ and $T'$ are both minimum. If the minimum spanning tree is unique, $T' = T$. Otherwise, by (b), some edge $g = uv\notin T$ has $w(g)\le w(f)$ for an edge $f$ on its tree path $P$ — in fact $w(g) = w(f)$, since $w(g) < w(f)$ would make $T - f + g$ lighter than $T$. In the second run $g$ is therefore examined before $f$. Suppose $T' = T$. Then $g$ was rejected, so when it was examined, $u$ and $v$ were already joined in the current forest $F'\subseteq T' = T$; the only path between them in $T$ is $P$, so $f\in F'$ — impossible, because $f$ comes after $g$. Hence $T'\ne T$.
>
> **Time.** Two sorts and two runs of Kruskal's loop, $O(E\log V)$; marking the edges of $T$ and comparing, $O(V+E)$.
>
> **Answer.** The MST is unique iff Kruskal's algorithm, rerun with ties broken against its first tree, returns the same tree; $O(E\log V)$ time.

## Exercise 7.3 — Dangerous and useful edges

> [!question] Exercise 7.3 (book p. 268)
> Edge weights are distinct. An edge is **dangerous** if it is the heaviest edge of some cycle of $G$, and **useful** if it lies on no cycle of $G$.
>
> (a) Prove that the minimum spanning tree contains every useful edge.
>
> (b) Prove that the minimum spanning tree contains no dangerous edge.
>
> (c) Describe and analyze an efficient implementation of the other algorithm in Kruskal's 1956 paper: examine the edges in *decreasing* order of weight, and delete each edge that is dangerous (in the current graph). The book's hint: it will not be as fast as Kruskal's usual algorithm.

### (a) and (b) Which edges are certain

> [!hint]- Hint
> (a) A useful edge is the only edge across some cut. (b) You have proved this already.

> [!solution]- Solution
> **(a)** Let $e = uv$ be useful. Then $G - e$ has no path from $u$ to $v$ — with $e$ it would close a cycle. Let $S$ be the set of vertices that $u$ reaches in $G - e$. Every edge other than $e$ has both endpoints or neither in $S$, so $e$ is the only, hence the lightest, edge with exactly one endpoint in $S$, and Lemma 7.2 puts it into the MST. (In fact every spanning tree contains $e$.)
>
> **(b)** This is Exercise 7.1(a).
>
> **More is true.** Every edge $g\notin T$ is dangerous: by the optimality condition it is heavier than every edge on its tree path, so it is the heaviest edge of the cycle it closes with $T$. So the dangerous edges are *exactly* the edges outside the MST.
>
> **Answer.** (a) A useful edge is the only edge leaving the vertices on one side of it, so it is safe. (b) A dangerous edge is the heaviest edge of a cycle, so Exercise 7.1(a) applies.

### (c) Reverse-delete

> [!hint]- Hint
> Every heavier edge that survived its own test lies on no cycle. So when is the current edge the heaviest edge of a cycle of the current graph?

> [!solution]- Solution
> ```text
> ReverseDelete(V, E):
>     sort E by decreasing weight
>     H ← (V, E)
>     for each edge uv in this order
>         remove uv from H
>         if whatever-first search from u in H does not reach v
>             put uv back into H              ⟨⟨uv lies on no cycle of H⟩⟩
>     return H
> ```
>
> **The test is right.** When $uv$ is examined, every heavier edge still in $H$ was put back when it was examined, because it lay on no cycle of the graph at that time; that graph contained the current $H$, so the edge lies on no cycle of $H$ either. Every cycle of $H$ through $uv$ therefore consists of $uv$ and lighter edges, so $uv$ is dangerous in $H$ iff it lies on a cycle of $H$ — iff $u$ still reaches $v$ once $uv$ is removed.
>
> **Correctness.** Invariant: $H$ is connected, and its minimum spanning tree is $T$, the MST of $G$. Deleting a dangerous edge keeps $H$ connected (the rest of its cycle joins its endpoints), and $T$, which avoids that edge by (b), is still a spanning tree of the smaller graph — still minimum, because the spanning trees of the smaller graph are spanning trees of $H$. At the end every remaining edge was put back, so it lies on no cycle: $H$ is connected and acyclic, a spanning tree, and its only spanning tree is $T$. So $H = T$. (If "dangerous" is read in the original $G$ instead, nothing changes: those are exactly the edges outside $T$ by the remark after (b), and the algorithm deletes exactly those.)
>
> **Time.** Sorting takes $O(E\log V)$, and each of the $E$ searches takes $O(V+E)$: $O(E(V+E)) = O(E^2)$ in total, since $V\le E+1$ in a connected graph.
>
> **Answer.** One whatever-first search per edge, in decreasing order of weight: $O(E^2)$ time, against $O(E\log V)$ for Kruskal's algorithm.

## Exercise 7.4 — Maximum spanning trees and feedback edge sets

> [!question] Exercise 7.4 (book pp. 268–269)
> (a) Describe and analyze an algorithm that computes the maximum-weight spanning tree of an edge-weighted graph.
>
> (b) A **feedback edge set** of an undirected graph $G$ is a set $F$ of edges such that every cycle of $G$ contains an edge of $F$; equivalently, removing $F$ makes $G$ acyclic. Describe and analyze a fast algorithm that computes a minimum-weight feedback edge set of an edge-weighted graph.

### (a) Maximum spanning trees

> [!hint]- Hint
> Negate.

> [!solution]- Solution
> Run any MST algorithm with the weights $w'(e) = -w(e)$ — for example Kruskal's loop over the edges in *decreasing* order of weight. Distinct weights stay distinct, and $w'(T) = -w(T)$ for every spanning tree $T$, so a tree minimizes $w'$ iff it maximizes $w$. Time $O(E\log V)$.
>
> **Answer.** The minimum spanning tree for $-w$; $O(E\log V)$ time.

### (b) Minimum feedback edge sets

> [!hint]- Hint
> Removing $F$ leaves a forest, and $F$ is light exactly when that forest is heavy. Watch out for negative weights.

> [!solution]- Solution
> **Reformulation.** $F$ is a feedback edge set iff the remaining edges $E\setminus F$ form a forest, and $w(F) = w(E) - w(E\setminus F)$. So we want a **maximum-weight forest** $K$, and we output $F = E\setminus K$.
>
> **Algorithm.** Let $G^+$ be the graph with all the vertices and only the edges of positive weight. Compute a maximum spanning forest $K$ of $G^+$ with Kruskal's loop over the positive edges in decreasing order of weight, and return $F = E\setminus K$. Every edge of weight $\le 0$ ends up in $F$. If all weights are positive, $F$ is everything outside a maximum spanning tree (forest, if $G$ is disconnected).
>
> **Correctness.** $K$ is a forest, so $F$ is a feedback edge set. Let $K'$ be any forest of $G$. Dropping its edges of weight $\le 0$ gives a forest $K''$ of $G^+$ with $w(K'')\ge w(K')$. Now add edges of $G^+$ that join different trees of $K''$ for as long as possible: the result is a spanning forest of $G^+$ (it has the same components as $G^+$), and since the added edges are positive its weight is at least $w(K'')$. The maximum spanning forest $K$ weighs at least as much, so $w(K)\ge w(K')$, and $w(F)$ is minimum.
>
> **Time.** $O(E\log V)$ for Kruskal's algorithm, $O(E)$ for the rest.
>
> **Answer.** Output every edge outside a maximum spanning forest of the positive-weight edges; $O(E\log V)$ time.

## Exercise 7.5 — Updating a minimum spanning tree

> [!question] Exercise 7.5 (book p. 269)
> We are given an undirected graph $G$ with weighted edges and a minimum spanning tree $T$ of $G$. Describe algorithms that update $T$ when the weight of a single edge $e$ (a) decreases, (b) increases. The input is $e$ and its new weight; the algorithms must modify $T$ so that it is again a minimum spanning tree. The book's hint: treat $e\in T$ and $e\notin T$ separately.

Below, $w$ is the old weight function and $w'$ the new one, and the new weights are still distinct.

### (a) The weight decreases

> [!hint]- Hint
> If $e\notin T$, the new minimum spanning tree lies inside $T + e$.

> [!solution]- Solution
> - **$e\in T$: do nothing.** Let $\delta = w(e) - w'(e) > 0$. Every spanning tree $T'$ gets lighter by at most $\delta$, and $T$ by exactly $\delta$: $w'(T')\ge w(T') - \delta\ge w(T) - \delta = w'(T)$.
> - **$e = uv\notin T$:** find the tree path $P$ from $u$ to $v$ by whatever-first search in $T$, and its heaviest edge $f$. If $w'(e) < w(f)$, set $T\leftarrow T - f + e$; otherwise do nothing. Time $O(V)$, since $T$ has $V - 1$ edges.
>
> **Correctness when $e\notin T$.** Every edge $g\notin T + e$ is, under $w$, the heaviest edge of the cycle it closes with $T$ (optimality condition). That cycle consists of $g$ and tree edges, so none of its weights changed, and by Exercise 7.1(a) the new minimum spanning tree $T^*$ avoids $g$. Hence $T^*\subseteq T + e$. The graph $T + e$ has exactly one cycle, $P + e$, so $T^*$ is $T + e$ minus one edge of it, and by Exercise 7.1(a) that edge is the heaviest one under $w'$: $f$ if $w'(e) < w(f)$, and $e$ otherwise.
>
> **Answer.** If $e\in T$, nothing changes; otherwise swap $e$ in for the heaviest edge on its tree path if $e$ is now lighter than that edge. $O(V)$ time.

### (b) The weight increases

> [!hint]- Hint
> If $e\in T$, every other tree edge stays. What reconnects the two halves?

> [!solution]- Solution
> - **$e\notin T$: do nothing.** $w'(T')\ge w(T')\ge w(T) = w'(T)$ for every spanning tree $T'$.
> - **$e = uv\in T$:** delete $e$ from $T$, label the two components of $T - e$ by whatever-first search ($O(V)$), scan all edges for the lightest edge $g$ under $w'$ with one endpoint in each component ($O(E)$; $e$ itself is a candidate), and set $T\leftarrow T - e + g$. Time $O(V+E) = O(E)$.
>
> **Correctness when $e\in T$.** Let $h\in T - e$. By the optimality condition, $h$ is the lightest edge (under $w$) with one endpoint in each component of $T - h$. The edge $e$ is not among these crossing edges — it is a tree edge other than $h$, so it lies inside one of the two components — so their weights did not change, and Lemma 7.2 puts $h$ into the new minimum spanning tree $T^*$. Thus $T - e\subseteq T^*$, and the last edge of $T^*$ must join the two components of $T - e$; by Lemma 7.2 (with $S$ the component of $u$) it is the lightest such edge, $g$.
>
> **Answer.** If $e\notin T$, nothing changes; otherwise replace $e$ by the lightest edge across the cut that $T - e$ defines (possibly $e$ again). $O(E)$ time.

## Exercise 7.6 — The second smallest spanning tree

> [!question] Exercise 7.6 (book p. 269)
> (a) Describe and analyze an algorithm that finds the **second smallest spanning tree** of $G$: the spanning tree of smallest weight other than the minimum spanning tree.
>
> (Part (b), the $k$ lightest spanning trees, is marked ♥ and skipped.)

> [!hint]- Hint
> Some second smallest spanning tree is one swap $T - f + g$ away from $T$. For a fixed $g$, which $f$ is best?

> [!solution]- Solution
> **Claim.** Every second smallest spanning tree $T_2$ equals $T - f + g$ for some edge $g\notin T$ and some edge $f$ on the tree path of $g$.
>
> *Proof.* Suppose $T$ and $T_2$ differ in at least two edges, and let $g$ be the lightest edge of the symmetric difference $T\oplus T_2$.
> - If $g\in T_2\setminus T$: the cycle that $g$ closes with $T$ contains an edge $h\notin T_2$, because $T_2$ is acyclic. Then $h\in T\setminus T_2$, and $h$ is lighter than $g$ by the optimality condition — contradicting the choice of $g$.
> - If $g\in T\setminus T_2$: the cycle that $g$ closes with $T_2$ contains an edge $h\notin T$, so $h\in T_2\setminus T$ and $w(h) > w(g)$. The swap $T_2 - h + g$ is a spanning tree lighter than $T_2$, and it still differs from $T$: $T_2$ lacked at least two edges of $T$, and the swap restores only one. This contradicts the choice of $T_2$.
>
> So $T_2$ differs from $T$ in exactly one edge: $T_2 = T - f + g$, and since this is a spanning tree, $f$ lies on the tree path of $g$. $\square$
>
> **Algorithm.** The swap costs $w(g) - w(f)$ extra; for a fixed $g$ the best $f$ is the heaviest edge on its tree path. Precompute that edge for every pair of vertices, then try every non-tree edge:
>
> ```text
> SecondMST(V, E):
>     T ← the minimum spanning tree of G
>     for each vertex s                        ⟨⟨one search of T per vertex⟩⟩
>         Heavy[s, s] ← Null
>         search T from s; whenever v is marked from its parent p:
>             Heavy[s, v] ← heavier of Heavy[s, p] and pv     ⟨⟨Null loses⟩⟩
>     best ← ∞
>     for each edge uv ∉ T
>         if w(uv) − w(Heavy[u, v]) < best
>             best ← w(uv) − w(Heavy[u, v])
>             g ← uv;  f ← Heavy[u, v]
>     return T − f + g
> ```
>
> **Time.** The MST takes $O(E + V\log V)$ with Jarník's algorithm and a Fibonacci heap; the $V$ searches of $T$ take $O(V)$ each, $O(V^2)$ in all; the final loop takes $O(E)$. Total $O(V^2)$. (If $G$ is itself a tree, there is no second spanning tree.)
>
> **Example.** On the book's Figure 7.1 the MST weighs $42$ (figure below). Its six non-tree edges:
>
> | non-tree edge $g$ | 8 | 10 | 14 | 18 | 26 | 30 |
> |---|---|---|---|---|---|---|
> | heaviest edge $f$ on its tree path | 5 | 3 | 12 | 12 | 16 | 16 |
> | extra weight $w(g) - w(f)$ | 3 | 7 | **2** | 6 | 10 | 14 |
>
> The best swap trades $12$ for $14$: the second smallest spanning tree weighs $44$.
>
> **Answer.** Try every non-tree edge against the heaviest edge of its tree path and take the cheapest swap; $O(V^2)$ time.

<!-- fig:a07x-second -->
<figure class="cs-fig"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 480 265" width="480" height="265" role="img" style="font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-size:14px"><title>the book&#x27;s seven-vertex example graph with its minimum spanning tree and one swap marked</title><defs><marker id="ARR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs><line x1="119.6" y1="33.9" x2="48.4" y2="74.1" stroke="var(--muted)" stroke-width="1.2" stroke-linecap="round"/><line x1="140.4" y1="33.9" x2="211.6" y2="74.1" stroke="var(--accent)" stroke-width="3.4" stroke-linecap="round"/><line x1="50" y1="80" x2="210" y2="80" stroke="var(--muted)" stroke-width="1.2" stroke-linecap="round"/><line x1="48.4" y1="85.9" x2="119.6" y2="126.1" stroke="var(--accent)" stroke-width="3.4" stroke-linecap="round"/><line x1="140.4" y1="126.1" x2="211.6" y2="85.9" stroke="var(--accent)" stroke-width="3.4" stroke-linecap="round"/><line x1="38" y1="92" x2="38" y2="172" stroke="var(--muted)" stroke-width="1.2" stroke-linecap="round"/><line x1="222" y1="92" x2="222" y2="172" stroke="var(--accent)" stroke-width="3.4" stroke-linecap="round"/><line x1="119.6" y1="137.9" x2="48.4" y2="178.1" stroke="var(--accent)" stroke-width="3.4" stroke-linecap="round" opacity="0.35"/><line x1="140.4" y1="137.9" x2="211.6" y2="178.1" stroke="var(--muted)" stroke-width="1.2" stroke-linecap="round"/><line x1="130" y1="144" x2="130" y2="224" stroke="var(--hi)" stroke-width="2.2" stroke-linecap="round" stroke-dasharray="6 4"/><line x1="48.4" y1="189.9" x2="119.6" y2="230.1" stroke="var(--accent)" stroke-width="3.4" stroke-linecap="round"/><line x1="140.4" y1="230.1" x2="211.6" y2="189.9" stroke="var(--muted)" stroke-width="1.2" stroke-linecap="round"/><text x="74" y="44" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">8</text><text x="186" y="44" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">5</text><text x="130" y="70" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">10</text><text x="78" y="117" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">2</text><text x="182" y="117" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">3</text><text x="25" y="132" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">18</text><text x="235" y="132" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">16</text><text x="76" y="147" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">12</text><text x="184" y="147" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">30</text><text x="119" y="184" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">14</text><text x="74" y="220" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">4</text><text x="186" y="220" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">26</text><circle cx="130" cy="28" r="12" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><circle cx="38" cy="80" r="12" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><circle cx="222" cy="80" r="12" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><circle cx="130" cy="132" r="12" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><circle cx="38" cy="184" r="12" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><circle cx="222" cy="184" r="12" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><circle cx="130" cy="236" r="12" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><line x1="60.4" y1="160.4" x2="74.4" y2="174.4" stroke="var(--hi)" stroke-width="2.4" stroke-linecap="round"/><line x1="60.4" y1="174.4" x2="74.4" y2="160.4" stroke="var(--hi)" stroke-width="2.4" stroke-linecap="round"/><text x="262" y="70" text-anchor="start" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">MST T (thick): weight 42</text><text x="262" y="98" text-anchor="start" dominant-baseline="central" fill="var(--hi)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">g = 14 (dashed) closes a cycle</text><text x="262" y="116" text-anchor="start" dominant-baseline="central" fill="var(--hi)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">whose heaviest tree edge is</text><text x="262" y="134" text-anchor="start" dominant-baseline="central" fill="var(--hi)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">f = 12 (crossed out)</text><text x="262" y="162" text-anchor="start" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">T − f + g: weight 44,</text><text x="262" y="180" text-anchor="start" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">the second smallest</text></svg><figcaption><strong>The second smallest spanning tree is one swap away.</strong> The graph of the book's Figure 7.1 with its MST (thick, weight 42). Of the six non-tree edges, 14 is the cheapest to swap in: it closes the cycle through 12 and 4, and removing 12 costs only 14 − 12 = 2 extra. The result, weight 44, is the second smallest spanning tree.</figcaption></figure>

## Exercise 7.7 — Jarník's algorithm in O(V²) time

> [!question] Exercise 7.7 (book p. 269)
> A graph is **dense** if $E = \Theta(V^2)$. Describe a modification of Jarník's algorithm that runs in $O(V^2)$ time, whatever $E$ is, using only elementary data structures — in particular, no Fibonacci heap. (Dijkstra described this variant in 1958.)

> [!hint]- Hint
> With $V^2$ time to spend, each of the $V - 1$ iterations can afford a linear scan for the minimum.

> [!solution]- Solution
> Keep the priorities of the book's Figure 7.5 in a plain array and replace $\textsf{ExtractMin}$ by a scan. With the weights in an adjacency matrix ($w(u, v) = \infty$ if $uv\notin E$):
>
> ```text
> DenseJarník(V, w, s):
>     for each vertex u
>         inT(u) ← False;  priority(u) ← w(s, u);  edge(u) ← su
>     inT(s) ← True;  T ← ∅
>     for i ← 1 to V − 1
>         ⟨⟨linear scan over all vertices:⟩⟩
>         v ← the vertex with inT(v) = False and the smallest priority(v)
>         inT(v) ← True;  add edge(v) to T
>         for each vertex u with inT(u) = False
>             if w(v, u) < priority(u)
>                 priority(u) ← w(v, u);  edge(u) ← vu
>     return T
> ```
>
> **Correctness.** Invariant: for every vertex $u$ outside $T$, $\mathit{priority}(u)$ is the weight of the lightest edge between $u$ and $T$, and $\mathit{edge}(u)$ is that edge ($\infty$ if there is none). It holds when $T = \{s\}$, and when $v$ joins $T$ the only new candidates for $u$ are the edges $vu$, which the inner loop examines. So the scan returns the endpoint of $T$'s safe edge — the lightest edge with exactly one endpoint in $T$ — which is the edge Jarník's algorithm adds ([[2-algorithms/07-minimum-spanning-trees#74-jarníks-prims-algorithm|§7.4]]). As $G$ is connected, the chosen priority is finite, so $\mathit{edge}(v)$ is a real edge.
>
> **Time.** $V - 1$ iterations, each with two loops over the $V$ vertices: $O(V^2)$, independent of $E$. With adjacency lists instead of a matrix, the inner loop scans $v$'s list, for $O(V^2 + E) = O(V^2)$ in all. For a dense graph this is optimal, since reading the input already takes $\Theta(V^2)$ time.
>
> **Answer.** Keep the priorities in an array and find the minimum by a linear scan: $O(V^2)$ time.

## Exercise 7.8 — Borůvka's algorithm by contraction

> [!question] Exercise 7.8 (book pp. 269–270)
> To **contract** an edge $uv$, replace $u$ and $v$ by one new node, redirect every other edge at $u$ or $v$ to the new node, and of any parallel edges this creates keep only the lightest. (The book's Figure 7.7 contracts one edge of its example graph.) All three classical algorithms can be phrased as "copy $G$ to $G'$, repeatedly contract safe edges of $G'$; the contracted edges form the MST":
> - **Borůvka:** mark the lightest edge at each vertex, contract all marked edges, and recurse;
> - **Jarník:** repeatedly contract the lightest edge at a fixed root vertex;
> - **Kruskal:** repeatedly contract the lightest edge in the graph.
>
> (a) Describe how to execute one pass of Borůvka's contraction algorithm in $O(V+E)$ time; the graph is given by adjacency lists.
>
> (b) A hybrid algorithm performs $k$ passes of Borůvka's contraction algorithm and then runs Jarník's algorithm with a Fibonacci heap on the contracted graph. i. What is its running time, as a function of $V$, $E$ and $k$? ii. Which $k$ minimizes it, and what is the resulting running time?
>
> (c) A family of graphs is **nice** if contracting an edge of a nice graph yields a nice graph, and every nice graph with $V$ vertices has $O(V)$ edges. (Planar graphs are nice: contraction keeps a graph planar, and a planar graph has at most $3V - 6$ edges.) Prove that Borůvka's contraction algorithm computes the minimum spanning tree of any nice graph in $O(V)$ time.

### (a) One pass in linear time

> [!hint]- Hint
> Label the components of the marked edges. What is left is to remove duplicates from a list of pairs of labels — a job for radix sort.

> [!solution]- Solution
> 1. **Mark.** For every vertex $v$, scan its adjacency list and mark its lightest edge: $O(V+E)$.
> 2. **Label.** Run $\textsf{CountAndLabel}$ (the chapter's subroutine from Chapter 5) on the graph whose edges are the marked edges; every vertex gets a label $\mathit{comp}(v)\in\{1, \dots, V'\}$: $O(V)$.
> 3. **Relabel.** For every edge $uv$ with $\mathit{comp}(u)\ne\mathit{comp}(v)$, append the record $\big(\min\{\mathit{comp}(u), \mathit{comp}(v)\}, \max\{\mathit{comp}(u), \mathit{comp}(v)\}, w(uv), uv\big)$ to a list $L$; edges inside a component are dropped: $O(E)$.
> 4. **Deduplicate.** Radix-sort $L$ by its pair of labels: a counting sort on the second label, then a stable counting sort on the first, each with $V'$ buckets, $O(V+E)$. Records with the same pair are now consecutive; keep the lightest record of each run: $O(E)$.
> 5. **Build** the adjacency lists of the new graph on $V'$ vertices from the surviving records, and output the marked edges: $O(V+E)$. Each record remembers its original edge, so the output can be given in terms of $G$.
>
> **Why it is a Borůvka step.** The nodes of the current graph are the components of the forest of edges contracted so far, and the edge kept between two nodes is the lightest edge of $G$ between the two components. So the lightest edge at a node $A$ is the lightest edge of $G$ with exactly one endpoint in $A$ — the safe edge of $A$ — and a pass adds exactly the safe edges of all components, as one iteration of [[2-algorithms/07-minimum-spanning-trees#73-borůvkas-algorithm|Borůvka's algorithm]] does. All marked edges are in the MST (Lemma 7.2), so they form a forest. Every node has a marked edge, so every component of marked edges has at least two nodes: $V'\le V/2$.
>
> **Answer.** Mark, label the components, relabel the edges, radix-sort and deduplicate: $O(V+E)$ per pass, and the number of vertices at least halves.

### (b) A hybrid with Jarník's algorithm

> [!hint]- Hint
> Each pass costs $O(E)$ and halves $V$; Jarník's algorithm costs $O(E' + V'\log V')$ on a graph with $V'$ vertices and $E'$ edges.

> [!solution]- Solution
> **i.** By (a), each pass costs $O(V+E) = O(E)$ (connected graph) and at least halves the number of vertices, while the number of edges never grows. After $k$ passes at most $V/2^k$ vertices and $E$ edges are left, and Jarník's algorithm with a Fibonacci heap takes $O(E + (V/2^k)\log V)$ on them. In total:
> $$
> O\Big(kE + E + \frac{V\log V}{2^k}\Big).
> $$
>
> **ii.** The term $kE$ grows with $k$ and $V\log V/2^k$ shrinks; balance them by choosing
> $$
> k = \max\Big\{0,\ \Big\lceil\log_2\frac{V\log_2 V}{E}\Big\rceil\Big\}.
> $$
> Then $2^k\ge V\log_2 V/E$, so the last term is at most $E$, and the running time is
> $$
> O\Big(E\cdot\max\Big\{1,\ \log\frac{V\log V}{E}\Big\}\Big).
> $$
> No $k$ does better by more than a constant factor: with $L = \log_2(V\log_2 V/E)$, every $k\ge L/2$ pays $kE\ge EL/2$, and every $k < L/2$ pays $V\log_2 V/2^k > E\cdot 2^{L/2}\ge EL/2$. Because $E\ge V - 1$, the ratio $V\log V/E$ is $O(\log V)$: the worst case, for sparse graphs, is $O(E\log\log V)$, and once $E\ge V\log_2 V$ we get $k = 0$ and plain Jarník's algorithm already takes $O(E)$. The simpler choice $k = \lceil\log_2\log_2 V\rceil$ always gives $O(E\log\log V)$.
>
> **Answer.** $O(kE + E + V\log V/2^k)$; the best $k$ is about $\log_2(V\log V/E)$, for $O(E\cdot\max\{1, \log(V\log V/E)\}) = O(E\log\log V)$ time.

### (c) Nice graphs in linear time

> [!hint]- Hint
> A geometric series.

> [!solution]- Solution
> Let $V_i$ and $E_i$ be the numbers of vertices and edges before pass $i$, with $V_0 = V$. Contracting the marked edges of a pass one at a time, keeping the lightest of parallel edges each time, produces the same graph as the pass, so by the first property every graph the algorithm creates is nice. By the second property there is a constant $c$ with $E_i\le cV_i$ for all $i$. By (a), $V_i\le V/2^i$, and pass $i$ takes $O(V_i + E_i) = O((1+c)V_i)$ time. In total:
> $$
> \sum_{i\ge 0} O\Big((1+c)\frac{V}{2^i}\Big) = O(V).
> $$
> Correctness is that of Borůvka's algorithm: by (a), each pass adds exactly the safe edges.
>
> **Answer.** Pass $i$ costs $O(V_i)$ because nice graphs stay nice and sparse, and $V_i\le V/2^i$, so the total is $O(V)$.

## Exercise 7.9 — Bottleneck distance

> [!question] Exercise 7.9 (book pp. 270–271)
> The **width** of a path in an undirected weighted graph is the minimum weight of its edges. The **bottleneck distance** between $s$ and $t$ is the width of the widest path from $s$ to $t$; it is $-\infty$ if there is no such path, and $\infty$ if $s = t$. (In the book's figure, reproduced below, the bottleneck distance between $s$ and $t$ is $9$.)
>
> (a) Prove that the *maximum* spanning tree of $G$ contains a widest path between *every* pair of vertices.
>
> (b) Describe an algorithm for the following problem that runs in $O(V+E)$ time: given $G$, vertices $s$ and $t$, and a weight $W$, is the bottleneck distance between $s$ and $t$ at most $W$?
>
> (c) Let $B$ be the bottleneck distance between $s$ and $t$. i. Prove that deleting any edge of weight less than $B$ does not change the bottleneck distance between $s$ and $t$. ii. Prove that contracting any edge of weight greater than $B$ does not change it either (where contraction keeps the *heaviest* of any parallel edges).
>
> (Part (d), a minimum-bottleneck path in $O(V+E)$ time, is marked ♥ and skipped.)

### (a) Widest paths live in the maximum spanning tree

> [!hint]- Hint
> Cut the maximum spanning tree at the lightest edge of its $s$–$t$ path, and look where a wider path crosses that cut.

> [!solution]- Solution
> Let $T$ be a maximum spanning tree, $s\ne t$ two vertices, $P$ the path from $s$ to $t$ in $T$, and $e$ its lightest edge, so $P$ has width $w(e)$. Suppose some path $Q$ from $s$ to $t$ is wider: all its edges are heavier than $e$. Deleting $e$ splits $T$ into two trees, one containing $s$ and the other $t$. The path $Q$ crosses from one to the other along some edge $f$, with $w(f) > w(e)$, so $T - e + f$ is a spanning tree heavier than $T$ — a contradiction. So $P$ is a widest path. (For $s = t$ the empty path has width $\infty$.) The proof never uses distinct weights, so every maximum spanning tree has this property.
>
> **Answer.** A wider path would cross the cut at the tree path's lightest edge with a heavier edge, and swapping it in would give a heavier spanning tree.

<!-- fig:a07x-bottleneck -->
<figure class="cs-fig"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 265" width="420" height="265" role="img" style="font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-size:14px"><title>the seven-vertex example graph with its maximum spanning tree and the widest s-t path</title><defs><marker id="ARR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs><line x1="119.6" y1="33.9" x2="48.4" y2="74.1" stroke="var(--muted)" stroke-width="1.2" stroke-linecap="round"/><line x1="140.4" y1="33.9" x2="211.6" y2="74.1" stroke="var(--hi)" stroke-width="3.6" stroke-linecap="round"/><line x1="50" y1="80" x2="210" y2="80" stroke="var(--accent)" stroke-width="3.4" stroke-linecap="round"/><line x1="48.4" y1="85.9" x2="119.6" y2="126.1" stroke="var(--muted)" stroke-width="1.2" stroke-linecap="round"/><line x1="140.4" y1="126.1" x2="211.6" y2="85.9" stroke="var(--muted)" stroke-width="1.2" stroke-linecap="round"/><line x1="38" y1="92" x2="38" y2="172" stroke="var(--muted)" stroke-width="1.2" stroke-linecap="round"/><line x1="222" y1="92" x2="222" y2="172" stroke="var(--hi)" stroke-width="3.6" stroke-linecap="round"/><line x1="119.6" y1="137.9" x2="48.4" y2="178.1" stroke="var(--hi)" stroke-width="3.6" stroke-linecap="round"/><line x1="140.4" y1="137.9" x2="211.6" y2="178.1" stroke="var(--hi)" stroke-width="3.6" stroke-linecap="round"/><line x1="130" y1="144" x2="130" y2="224" stroke="var(--muted)" stroke-width="1.2" stroke-linecap="round"/><line x1="48.4" y1="189.9" x2="119.6" y2="230.1" stroke="var(--accent)" stroke-width="3.4" stroke-linecap="round"/><line x1="140.4" y1="230.1" x2="211.6" y2="189.9" stroke="var(--muted)" stroke-width="1.2" stroke-linecap="round"/><text x="74" y="44" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">1</text><text x="186" y="44" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">11</text><text x="130" y="70" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">6</text><text x="78" y="117" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">4</text><text x="182" y="117" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">3</text><text x="25" y="132" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">5</text><text x="235" y="132" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">9</text><text x="76" y="147" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">10</text><text x="184" y="147" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">12</text><text x="119" y="184" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">7</text><text x="74" y="220" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">8</text><text x="186" y="220" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">2</text><circle cx="130" cy="28" r="12" fill="var(--hi)" fill-opacity="0.18" stroke="var(--hi)" stroke-width="1.8"/><text x="130" y="29" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">t</text><circle cx="38" cy="80" r="12" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><circle cx="222" cy="80" r="12" fill="var(--hi)" fill-opacity="0.18" stroke="var(--hi)" stroke-width="1.8"/><circle cx="130" cy="132" r="12" fill="var(--hi)" fill-opacity="0.18" stroke="var(--hi)" stroke-width="1.8"/><circle cx="38" cy="184" r="12" fill="var(--hi)" fill-opacity="0.18" stroke="var(--hi)" stroke-width="1.8"/><text x="38" y="185" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">s</text><circle cx="222" cy="184" r="12" fill="var(--hi)" fill-opacity="0.18" stroke="var(--hi)" stroke-width="1.8"/><circle cx="130" cy="236" r="12" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="262" y="80" text-anchor="start" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">thick: the maximum</text><text x="262" y="98" text-anchor="start" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">spanning tree</text><text x="262" y="130" text-anchor="start" dominant-baseline="central" fill="var(--hi)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">red: its s–t path</text><text x="262" y="148" text-anchor="start" dominant-baseline="central" fill="var(--hi)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">10, 12, 9, 11 — width 9</text><text x="262" y="180" text-anchor="start" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">no s–t path is wider:</text><text x="262" y="198" text-anchor="start" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">bottleneck distance 9</text></svg><figcaption><strong>The maximum spanning tree contains a widest path.</strong> The graph of the book's figure for Exercise 7.9. Its maximum spanning tree (thick) uses the edges 12, 11, 10, 9, 8 and 6; the path from <i>s</i> to <i>t</i> inside it (red) has width 9, the bottleneck distance the book states. Every other <i>s</i>–<i>t</i> path uses an edge of weight at most 8.</figcaption></figure>

### (b) Is the bottleneck distance at most W?

> [!hint]- Hint
> A path wider than $W$ uses only edges heavier than $W$.

> [!solution]- Solution
> In the [[concepts/graph-reductions|graph-reduction]] format:
>
> **Graph.** $H = (V, \{e\in E\mid w(e) > W\})$, undirected: the same vertices, and only the edges heavier than $W$. Building it takes $O(V+E)$ time.
>
> **Problem.** Reachability: the answer is "yes" iff $t$ is *not* reachable from $s$ in $H$. Indeed, the bottleneck distance exceeds $W$ iff some $s$–$t$ path has width greater than $W$, iff some $s$–$t$ path uses only edges heavier than $W$, iff $H$ contains a path from $s$ to $t$. This covers the special cases: if $s = t$, then $t$ is reachable and the answer is "no", correctly, as $\infty > W$; if $G$ has no $s$–$t$ path, then neither has $H$ and the answer is "yes", correctly, as $-\infty\le W$.
>
> **Algorithm.** Whatever-first search from $s$ in $H$, $O(V+E)$ time.
>
> **Answer.** Delete every edge of weight at most $W$ and answer "yes" iff $s$ can no longer reach $t$; $O(V+E)$ time.

### (c) Edges that do not matter

> [!hint]- Hint
> i: a widest path never uses such an edge. ii: map paths from $G$ to the contracted graph and back; on the way back, re-insert the contracted edge where needed.

> [!solution]- Solution
> **i.** Let $w(e) < B$. A widest path $P$ has width $B$, so all its edges weigh at least $B$, and $e\notin P$. After deleting $e$ the path $P$ is still there, so the bottleneck distance is still at least $B$; deleting an edge creates no new path, so it is not larger either.
>
> **ii.** Let $e = xy$ with $w(e) > B$; contraction merges $x$ and $y$ into a node $z$, and $s'$, $t'$ denote the nodes that $s$ and $t$ become.
> - *Not smaller.* Map a widest path $P$ of $G$ to $G/e$: drop $e$ if $P$ uses it, and replace every other edge by the edge kept between the images of its endpoints, which is at least as heavy. The result is a walk from $s'$ to $t'$ whose edges all weigh at least $B$ (it may pass through $z$ twice); it contains an $s'$–$t'$ path of width at least $B$.
> - *Not larger.* Suppose $G/e$ has an $s'$–$t'$ path $Q$ of width greater than $B$. Each edge of $Q$ is an edge of $G$ with the same weight. Consecutive edges of $Q$ meet at a common vertex of $G$, except possibly at $z$, where one may end at $x$ and the next start at $y$ (or the reverse); insert $e$ there, and likewise at the two ends of $Q$ if needed. The result is a walk from $s$ to $t$ in $G$ whose edges all weigh more than $B$, and it contains an $s$–$t$ path of width greater than $B$ — a contradiction.
>
> **Answer.** i: a widest path survives the deletion and no path is created. ii: widest paths map to $G/e$, and any path of $G/e$ lifts back to $G$ by re-inserting $e$, which is heavier than $B$.

## Exercise 7.10 — Borůvka's algorithm with union-find

> [!question] Exercise 7.10 (book pp. 271–272)
> Borůvka's algorithm can find its safe edges with a disjoint-set ([[concepts/union-find|union-find]]) structure, as Kruskal's algorithm does, instead of counting and labeling the components of $F$ in every iteration. Each component of $F$ is an **up-tree**: every vertex $v$ stores a pointer $\mathit{parent}(v)$, and $v$ is a root iff $\mathit{parent}(v) = v$. $\textsf{Find}(v)$ returns the root of $v$'s up-tree and applies **path compression**: every vertex on the path from $v$ to the root is made to point directly at the root. $\textsf{Union}(u, v)$ finds the two roots and makes either one the parent of the other. When $\textsf{FindSafeEdges}$ ends, each root $r$ stores $\mathit{safe}(r)$, the lightest edge with exactly one endpoint in its component.
>
> ```text
> FindSafeEdges(V, E):
>     for each vertex v
>         safe(v) ← Null
>     found ← False
>     for each edge uv ∈ E
>         ū ← Find(u);  v̄ ← Find(v)
>         if ū ≠ v̄
>             if safe(ū) = Null or w(uv) < w(safe(ū))
>                 safe(ū) ← uv
>             if safe(v̄) = Null or w(uv) < w(safe(v̄))
>                 safe(v̄) ← uv
>             found ← True
>     return found
>
> AddSafeEdges(V, E, F):
>     for each vertex v ∈ V
>         if safe(v) ≠ Null
>             xy ← safe(v)
>             if Find(x) ≠ Find(y)
>                 Union(x, y)
>                 add xy to F
>
> Borůvka(V, E):
>     F ← ∅
>     for each vertex v
>         parent(v) ← v
>     while FindSafeEdges(V, E)
>         AddSafeEdges(V, E, F)
>     return F
> ```
>
> Prove that each call to $\textsf{FindSafeEdges}$ and $\textsf{AddSafeEdges}$ takes only $O(E)$ time. [Hint: what is the depth of the up-trees when $\textsf{FindSafeEdges}$ ends?] It follows that this variant of Borůvka's algorithm also runs in $O(E\log V)$ time.
>
> **Correction.** The bound for $\textsf{AddSafeEdges}$ is false when $\textsf{Union}$ may link either way, as the book allows: there are trees with $V$ vertices on which a single call takes $\Theta(V\log V)$ time. The bound for $\textsf{FindSafeEdges}$ and the $O(E\log V)$ total are true; the total is easy to prove when $\textsf{Union}$ links by size, which the book's footnote calls the normal implementation.

### FindSafeEdges, and the hint

> [!hint]- Hint
> Charge each step of a $\textsf{Find}$ to a parent pointer that path compression changes. How often can one pointer change if no $\textsf{Union}$ happens in between?

> [!solution]- Solution
> **Cost of one Find.** If $v$ has depth $L$, $\textsf{Find}(v)$ makes $L + 1$ calls, $O(L+1)$ time, and redirects to the root every vertex on the path whose parent was not already the root: $L - 1$ of them when $L\ge 1$. So a $\textsf{Find}$ costs $O(2 + \text{the number of pointers it changes})$.
>
> **FindSafeEdges takes $O(E)$ time.** It calls $\textsf{Find}$ $2E$ times and never calls $\textsf{Union}$, so roots stay roots during the call, and a pointer, once redirected to a root, keeps pointing there: each of the $V$ pointers changes at most once. The total is $O(2\cdot 2E + V) = O(E)$, as $V\le E+1$.
>
> **The hint.** Because $G$ is connected, every vertex is an endpoint of some edge, gets a $\textsf{Find}$, and afterwards points at its root. So when $\textsf{FindSafeEdges}$ ends, every up-tree has depth at most $1$.
>
> **Answer.** Every $\textsf{Find}$ step beyond the second changes a pointer, and each pointer changes at most once per call: $O(E)$. At the end all up-trees have depth at most $1$.

### AddSafeEdges, and the total

> [!hint]- Hint
> The unions inside $\textsf{AddSafeEdges}$ make the trees deep again. How deep, if $\textsf{Union}$ always picks the worse direction?

> [!solution]- Solution
> **What it costs.** Only roots carry safe edges, so with $c$ components $\textsf{AddSafeEdges}$ makes at most $4c$ calls to $\textsf{Find}$ (two in the test, two inside $\textsf{Union}$) plus $O(V)$ other work, and each $\textsf{Find}$ costs $O(1 + \text{depth})$. All depths are at most $1$ when the call starts, but every $\textsf{Union}$ hangs one root below another, so the trees grow during the call.
>
> **The $O(E)$ claim is false.** Let $\textsf{Union}$ pick its direction adversarially. In the first iteration every vertex is its own component, and its safe edge is its lightest edge. Build a tree $G$ (so $E = V - 1$) on $V = 2^{k+1}$ vertices from two halves, handled by $\textsf{AddSafeEdges}$ in this order:
> - $2^k$ vertices forming a binomial tree of depth $k$ whose edge weights increase with depth, so that every vertex's safe edge goes to its parent. In a suitable vertex order, $\textsf{AddSafeEdges}$ links them into an up-tree of the same shape: each $\textsf{Union}$ joins two equal trees root to root, and every $\textsf{Find}$ costs $O(1)$.
> - $2^k$ further vertices $u_1, u_2, \dots$, where $u_i$ is joined, by an edge heavier than all earlier ones, to the vertex that is deepest in the up-tree when $u_i$ is handled. The $\textsf{Find}$ on that vertex walks at least $k$ pointers, and $\textsf{Union}$ then hangs the whole up-tree below the single vertex $u_i$.
>
> This is the classic worst case of path compression with arbitrary linking, which Tarjan and van Leeuwen (1984) showed can cost $\Theta(n\log n)$ for $n$ links and $n$ $\textsf{Find}$s. Here the compressed tree keeps a vertex at depth $k$ or more (a simulation of the book's pseudocode confirms this for every $V$ up to $2^{13}$; we give no proof for general $k$), so every one of these $2^k$ $\textsf{Find}$s makes at least $k + 1$ calls, and the call to $\textsf{AddSafeEdges}$ takes $\Omega(k\,2^k) = \Omega(V\log V)$ time on a graph with $E = V - 1$ edges. For $V = 2^{13}$ it makes $90{,}099$ calls of $\textsf{Find}$ (recursive calls included), about $11E$, and each doubling of $V$ adds another $0.5E$; with $\textsf{Union}$ by size, the same input costs $5.5E$.
>
> **What is true.** With $\textsf{Union}$ *by size* (the root of the larger tree stays a root), a vertex gets deeper only when the size of its tree at least doubles, and path compression only decreases depths; so every depth is at most $\log_2 V$ and every $\textsf{Find}$ costs $O(\log V)$. A call to $\textsf{AddSafeEdges}$ with $c$ components then takes $O(V + c\log V)$ time. The number of components at least halves in every iteration, so all the calls to $\textsf{AddSafeEdges}$ together cost $O(V\log V + \log V\cdot(V + V/2 + V/4 + \cdots)) = O(V\log V)$, and the at most $\lfloor\log_2 V\rfloor + 1$ calls to $\textsf{FindSafeEdges}$ cost $O(E\log V)$. Total: $O(E\log V)$, as the book concludes. (With arbitrary linking the total is still $O(E\log V)$, by a theorem we cite rather than prove. When a call starts, every non-root vertex is a leaf at depth $1$, and only roots are ever linked, so each $\textsf{Find}$ costs one step plus a $\textsf{Find}$ in the forest formed by the $c$ roots. Tarjan and van Leeuwen (1984) proved that path compression with arbitrary linking performs any $m$ $\textsf{Find}$s and at most $n - 1$ links on $n$ elements in $O(n + m\log_{2+m/n} n)$ time; with $n = c$ and $m\le 4c$ this is $O(c\log c)$, so every call to $\textsf{AddSafeEdges}$ still takes $O(V + c\log V)$ time, and the sum above applies.)
>
> **Answer.** $\textsf{AddSafeEdges}$ takes $O(V + c\log V)$ time with union by size, but can take $\Theta(V\log V)$ time on a tree with arbitrary linking, so "$O(E)$ per call" is false; the $O(E\log V)$ total holds.

### Sources for this page

Exercises 7.1–7.6(a), 7.7, 7.8, 7.9(a)–(c) and 7.10 of Jeff Erickson, *Algorithms* (2019), pp. 268–272 (CC BY 4.0), paraphrased; the pseudocode of Exercise 7.10 is re-typed from the book, and the solutions are ours. The graphs of the book's Figure 7.1 and of its figure for Exercise 7.9 are re-entered (our vertex names); their claims — an MST of weight 42, a bottleneck distance of 9 — are reproduced. The diamond of 7.1(b), the graphs of 7.2, the second smallest spanning tree of Figure 7.1 and the union-find input of 7.10 are original. Two statements are wrong as printed: the "only if" half of 7.2(b), and the $O(E)$ bound for $\textsf{AddSafeEdges}$ in 7.10 when $\textsf{Union}$ may link either way. The bound for path compression with arbitrary linking used in 7.10 is Theorem 4 of R. E. Tarjan and J. van Leeuwen, "Worst-case analysis of set union algorithms", *J. ACM* 31(2), 1984, which also shows that it is tight. Every algorithm on this page is checked by `tools/checks/a07x.py` against brute force — all spanning trees (minimum, uniqueness, second smallest), all cycles and cuts, all edge subsets (feedback edge sets) and all simple paths (bottleneck distances) — on every weighted graph with at most four vertices and weights in $\{1, 2, 3\}$ (for 7.2) and on hundreds of random graphs; the book's pseudocode for 7.10 is run literally, counting $\textsf{Find}$ calls, and every number in the examples is recomputed there.
