---
title: "Adversary arguments"
description: "Lower bounds by an adversary that answers queries consistently but unhelpfully: any-ones and the pattern 01 in bit strings (evasive exactly for even n), evasive graph properties (emptiness, connectedness via a reverse-Kruskal adversary), the Aanderaa–Karp–Rosenberg conjecture, min-and-max in exactly ⌈3n/2⌉ − 2 comparisons, and a 3n/2 − O(log n) lower bound for the median. Errors in the note corrected."
tags: [lecture-notes, algorithms, lower-bounds]
note: "13"
---

*Erickson, lecture notes · Director's Cut 13 · 8 pp. · [PDF](https://jeffe.cs.illinois.edu/teaching/algorithms/notes/13-adversary.pdf) · CC BY-NC-SA 4.0 · [[4-lecture-notes/index|all notes]]*

> [!abstract] In one breath
> An **adversary argument** proves a lower bound by playing against the algorithm: the adversary pretends to hold an input and answers every query so as to keep the algorithm in the dark, always consistently with some input. If the algorithm stops too early, two inputs agree with every answer but need different outputs, so it is wrong on one of them. With bit queries this shows that "is any bit 1?" needs all $n$ bits, and "does the string contain 01?" needs all $n$ bits exactly when $n$ is even — the property is **evasive**. With adjacency-matrix queries, emptiness and **connectedness** are evasive (the connectedness adversary is Kruskal run backwards), and the Aanderaa–Karp–Rosenberg conjecture says every nontrivial monotone graph property is. With comparisons, finding the **minimum and maximum** together takes exactly $\lceil 3n/2\rceil - 2$ comparisons, and the **median** needs $3n/2 - O(\log n)$, by combining an adversary with leaf counting.

> [!note] Where this fits
> It continues [[4-lecture-notes/12-lower-bounds|note 12]], whose maximum adversary ([[4-lecture-notes/12-lower-bounds#126-finding-the-maximum-and-adversaries|§12.6]]) is the model; the median bound complements linear-time selection ([[2-algorithms/01-recursion#18-linear-time-selection|§1.8]]), and the connectedness adversary uses minimum (here maximum) spanning trees ([[2-algorithms/07-minimum-spanning-trees#75-kruskals-algorithm|§7.5]]). Fooling sets ([[concepts/fooling-sets]]) are a cousin: two inputs the machine cannot tell apart. **Not assigned in CS 374 this semester** (CS 473 material at Illinois). Concept page: [[concepts/adversary-arguments]].

## 13.1 Three-card monte

The street game is the metaphor: the dealer "shuffles" three cards and the tourist bets on the queen, but the queen is up the dealer's sleeve, and whichever card the tourist picks is black. As long as the dealer never has to reveal all the cards, the tourist cannot prove he cheated — he can always slide the queen under some unturned card afterwards.

## 13.2 n-card monte

Now the tourist is an algorithm and the cards are bits: given $n$ bits, is any of them 1? The **adversary** (the dealer) pretends to have chosen an input; whenever the algorithm looks at a bit, it chooses the value that makes the algorithm work hardest. Here it answers 0 every time. If the algorithm stops with a bit unexamined: if it says "no 1", the adversary sets that bit to 1; if it says "there is a 1", the adversary reveals all zeros. Either way the algorithm is wrong, and it cannot tell the adversary from an honest user who fixed the input in advance.

> [!key] Any ones: all $n$ bits are needed
> Every algorithm that decides whether $n$ bits contain a 1 examines all $n$ bits in the worst case.

The crucial feature: the adversary makes **no assumption** about the algorithm — not the order in which it examines bits, nor what it does in between. Any algorithm that skips a bit falls to it.

## 13.3 Finding patterns in bit strings

Does an array $B[1..n]$ of bits contain the substring 01?

**Odd $n$: $n - 1$ bits suffice.** Look first at the even positions $B[2], B[4], \ldots, B[n-1]$. If some 0 among them comes before some 1, the string contains 01 (starting at the last 0 before that 1). Otherwise they read $1\cdots 1 0\cdots 0$, and an odd position can complete a 01 only if the even bit to its left is 0 or the even bit to its right is 1; look at those odd positions. Exactly one odd position is never needed — $B[1]$ if $B[2] = 0$, $B[n]$ if $B[n-1] = 1$, otherwise the one between the last 1 and the first 0, where both $1\,0\,0$ and $1\,1\,0$ avoid 01 — so at most $n - 1$ bits are examined.

**Even $n$: all $n$ bits are needed.** The adversary aims at an input without 01; those are exactly the strings $1\cdots 1 0\cdots 0$. It keeps two indices: it pretends $B[1..\ell]$ is all 1s and $B[r..n]$ all 0s, with $\ell = 0$ and $r = n + 1$ at the start, and keeps the number of undecided positions strictly between, $r - \ell - 1$, **even**.

```text
Hide01(i):                       ⟨⟨the algorithm examines B[i]⟩⟩
    if i ≤ ℓ
        B[i] ← 1
    else if i ≥ r
        B[i] ← 0
    else if i − ℓ is odd
        B[i] ← 0;  r ← i          ⟨⟨i − ℓ − 1 undecided bits remain: even⟩⟩
    else
        B[i] ← 1;  ℓ ← i          ⟨⟨r − i − 1 = (r − ℓ − 1) − (i − ℓ): even⟩⟩
```

(The note's version has the two middle branches the other way round — 0 when $i - \ell$ is even — and states the invariant as "$r - \ell$ is even", which is false at the start, where $r - \ell = n + 1$. As printed it fails already for $n = 2$: probing $B[1]$ gets a 1, after which neither completion, 10 or 11, contains 01.)

<!-- fig:n13-hide01 -->
<figure class="cs-fig"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 520 132" width="520" height="132" role="img" style="font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-size:14px"><title>ten cells: 1 1 1 1 ? ? ? ? 0 0, with cells 1, 4, 9, 10 shaded and pointers l = 4 and r = 9</title><defs><marker id="ARR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs><rect x="60" y="34" width="40" height="40" rx="0" fill="var(--accent)" fill-opacity="0.16" stroke="currentColor" stroke-width="1.2"/><text x="80" y="22" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:11.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">1</text><text x="80" y="55" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:17px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;font-weight:600;">1</text><rect x="100" y="34" width="40" height="40" rx="0" fill="none" stroke="currentColor" stroke-width="1.2"/><text x="120" y="22" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:11.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">2</text><text x="120" y="55" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:17px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">1</text><rect x="140" y="34" width="40" height="40" rx="0" fill="none" stroke="currentColor" stroke-width="1.2"/><text x="160" y="22" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:11.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">3</text><text x="160" y="55" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:17px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">1</text><rect x="180" y="34" width="40" height="40" rx="0" fill="var(--accent)" fill-opacity="0.16" stroke="currentColor" stroke-width="1.2"/><text x="200" y="22" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:11.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">4</text><text x="200" y="55" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:17px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;font-weight:600;">1</text><rect x="220" y="34" width="40" height="40" rx="0" fill="none" stroke="currentColor" stroke-width="1.2"/><text x="240" y="22" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:11.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">5</text><text x="240" y="55" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:17px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">?</text><rect x="260" y="34" width="40" height="40" rx="0" fill="none" stroke="currentColor" stroke-width="1.2"/><text x="280" y="22" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:11.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">6</text><text x="280" y="55" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:17px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">?</text><rect x="300" y="34" width="40" height="40" rx="0" fill="none" stroke="currentColor" stroke-width="1.2"/><text x="320" y="22" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:11.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">7</text><text x="320" y="55" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:17px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">?</text><rect x="340" y="34" width="40" height="40" rx="0" fill="none" stroke="currentColor" stroke-width="1.2"/><text x="360" y="22" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:11.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">8</text><text x="360" y="55" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:17px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">?</text><rect x="380" y="34" width="40" height="40" rx="0" fill="var(--accent)" fill-opacity="0.16" stroke="currentColor" stroke-width="1.2"/><text x="400" y="22" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:11.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">9</text><text x="400" y="55" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:17px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;font-weight:600;">0</text><rect x="420" y="34" width="40" height="40" rx="0" fill="var(--accent)" fill-opacity="0.16" stroke="currentColor" stroke-width="1.2"/><text x="440" y="22" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:11.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">10</text><text x="440" y="55" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:17px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;font-weight:600;">0</text><line x1="200" y1="104" x2="200" y2="79" stroke="var(--hi)" stroke-width="1.8" stroke-linecap="round" marker-end="url(#ARR)"/><text x="200" y="116" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">ℓ = 4</text><line x1="400" y1="104" x2="400" y2="79" stroke="var(--hi)" stroke-width="1.8" stroke-linecap="round" marker-end="url(#ARR)"/><text x="400" y="116" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">r = 9</text><text x="50" y="54" text-anchor="end" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">B</text></svg><figcaption><strong>What the Hide01 adversary is thinking</strong> (<i>n</i> = 10, after the algorithm has probed positions 4, 9, 1, 10 and seen 1, 0, 1, 0). Shaded cells have been examined. The adversary pretends the input is 1s up to ℓ = 4 and 0s from <i>r</i> = 9 on; the 4 bits strictly between are undecided, and their number <i>r</i> − ℓ − 1 is kept even. Until every bit is probed, a 01 can still be planted (in the gap, or by turning an unexamined 1 into 0 or an unexamined 0 into 1) or avoided.</figcaption></figure>

If the algorithm stops with a bit unexamined, the adversary can produce an input with 01 consistent with every answer: an unexamined bit left of $\ell$ can be 0 (followed by the 1 at $\ell$); one right of $r$ can be 1 (after the 0 at $r$); and if bits strictly between $\ell$ and $r$ remain, there are at least two of them, room for a 01. It can equally produce $1\cdots 1 0\cdots 0$, which has none. So the algorithm cannot know the answer.

> [!definition] Definition — evasive
> A bit pattern is **evasive** (for a given $n$) if every algorithm that decides whether an $n$-bit string contains it must examine all $n$ bits in the worst case. The pattern 1 is evasive for every $n$; the pattern 01 is evasive if and only if $n$ is even. The only patterns evasive for **all** $n$ are 0 and 1.

## 13.4 Evasive graph properties

Adversaries also give lower bounds for graph problems when the graph is given by its **adjacency matrix**: a query asks whether one pair $ij$ is an edge. A graph property (connected? acyclic? planar? complete? a tree?) is **evasive** if deciding it requires looking at all $\binom n2$ entries.

**Emptiness is evasive.** The adversary keeps the empty graph $E$ and a graph $G$, initially complete; for each queried pair it deletes the pair from $G$ and answers "no". If the algorithm stops before querying every pair, $G$ still has an edge, so $G$ is not empty while $E$ is, and both agree with every answer.

## 13.5 Connectedness is evasive

The adversary keeps two graphs on the $n$ vertices: $Y$ ("yes"), the edges it has confirmed, initially empty, and $M$ ("maybe"), the confirmed edges plus all unexamined pairs, initially complete. Each pair is assumed to be queried at most once.

```text
HideConnectedness(e):
    if M ∖ {e} is connected
        M ← M ∖ {e};  return 0       ⟨⟨"not an edge"⟩⟩
    else
        Y ← Y ∪ {e};  return 1       ⟨⟨"edge"⟩⟩
```

Both $Y$ and $M$ are consistent with all answers at all times. Invariants:
1. $Y\subseteq M$, and $M$ is connected.
2. No edge of $Y$ lies on a cycle of $M$ — an edge on a cycle could be deleted without disconnecting $M$, so it would have been answered 0.
3. $Y$ is acyclic (by 2).
4. If $Y\ne M$, then $Y$ is disconnected: otherwise $Y$ would be a spanning tree, and any edge of $M\setminus Y$ would close a cycle of $M$ through edges of $Y$, contradicting 2.

<!-- fig:n13-connectedness -->
<figure class="cs-fig"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 330 250" width="330" height="250" role="img" style="font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-size:14px"><title>five vertices on a pentagon; edges 15 and 25 thick, 34 35 45 thin, the other five dashed</title><defs><marker id="ARR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs><line x1="165" y1="36" x2="252.5" y2="99.6" stroke="var(--muted)" stroke-width="1.2" stroke-linecap="round" stroke-dasharray="4 4"/><line x1="165" y1="36" x2="219.1" y2="202.4" stroke="var(--muted)" stroke-width="1.2" stroke-linecap="round" stroke-dasharray="4 4"/><line x1="165" y1="36" x2="110.9" y2="202.4" stroke="var(--muted)" stroke-width="1.2" stroke-linecap="round" stroke-dasharray="4 4"/><line x1="165" y1="36" x2="77.5" y2="99.6" stroke="var(--hi)" stroke-width="3.4" stroke-linecap="round"/><line x1="252.5" y1="99.6" x2="219.1" y2="202.4" stroke="var(--muted)" stroke-width="1.2" stroke-linecap="round" stroke-dasharray="4 4"/><line x1="252.5" y1="99.6" x2="110.9" y2="202.4" stroke="var(--muted)" stroke-width="1.2" stroke-linecap="round" stroke-dasharray="4 4"/><line x1="252.5" y1="99.6" x2="77.5" y2="99.6" stroke="var(--hi)" stroke-width="3.4" stroke-linecap="round"/><line x1="219.1" y1="202.4" x2="110.9" y2="202.4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><line x1="219.1" y1="202.4" x2="77.5" y2="99.6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><line x1="110.9" y1="202.4" x2="77.5" y2="99.6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><circle cx="165" cy="36" r="14" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="165" y="37" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">1</text><circle cx="252.5" cy="99.6" r="14" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="252.5" y="100.6" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">2</text><circle cx="219.1" cy="202.4" r="14" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="219.1" y="203.4" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">3</text><circle cx="110.9" cy="202.4" r="14" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="110.9" y="203.4" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">4</text><circle cx="77.5" cy="99.6" r="14" fill="var(--paper)" stroke="currentColor" stroke-width="1.5"/><text x="77.5" y="100.6" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">5</text></svg><figcaption><strong>HideConnectedness on five vertices</strong>, after the algorithm has asked about the edges 12, 13, 14, 15, 23, 24, 25 in that order. The adversary said “no” to 12, 13, 14, 23, 24 (dashed: deleted from <i>M</i>, which stayed connected) and “yes” to 15 and 25 (thick: the graph <i>Y</i>), because deleting either would have cut vertex 1 or 2 off. Thin edges are unexamined. <i>M</i> = <i>Y</i> plus the thin edges is connected, <i>Y</i> is not, and both agree with every answer so far.</figcaption></figure>

> [!key] Connectedness is evasive
> Every algorithm that decides whether an $n$-vertex graph, given by its adjacency matrix, is connected must examine all $\binom n2$ entries in the worst case.

> [!proof]- Proof (click to expand)
> While some pair is unexamined, it is in $M$ but not in $Y$, so $Y\ne M$; by the invariants $M$ is connected and $Y$ is not. Both are consistent with every answer, so an algorithm that stops now is wrong on one of them. $\square$

**In spanning-tree terms.** The adversary is "anti-Kruskal" (reverse delete): it considers the edges in the order queried and deletes each one whose removal leaves the graph connected. If every pair is queried, $Y$ and $M$ both end as the **maximum** spanning tree of $K_n$ when each edge is weighted by the time it was queried (in the figure's order, the star at vertex 5).

## 13.6 An evasive conjecture

A graph property is **nontrivial** if some $n$-vertex graph has it and some does not, and **monotone** if it is closed under taking subgraphs (deleting edges). Emptiness, planarity, acyclicity and disconnectedness are monotone; being a tree and having a vertex of degree 3 are not.

> [!key] Conjecture (Aanderaa, Karp and Rosenberg)
> Every nontrivial monotone property of $n$-vertex graphs is evasive.

It has been proved when $n$ is a prime power $p^e$ (by Kahn, Saks and Sturtevant, with algebraic topology) and is open in general. There are nontrivial properties that are **not** evasive, but all known ones are non-monotone — for example "is a scorpion", one of the note's exercises.

## 13.7 Finding the minimum and maximum

*Given distinct $x_1, \ldots, x_n$, find the indices of the smallest and the largest.* Finding the minimum ($n - 1$ comparisons) and then the maximum of the rest ($n - 2$) gives $2n - 3$; finding the maximum alone already needs $n - 1$. Both bounds improve to the same value.

**Algorithm.** Compare the $\lfloor n/2\rfloor$ disjoint pairs $x_1{:}x_2$, $x_3{:}x_4$, …; put each smaller element into a set $S$ and each larger one into $L$ (for odd $n$, put $x_n$ into both). The minimum is the minimum of $S$, the maximum the maximum of $L$:
$$
\underbrace{\lfloor n/2\rfloor}_{\text{pairs}} + \underbrace{\lceil n/2\rceil - 1}_{\min S} + \underbrace{\lceil n/2\rceil - 1}_{\max L} = \lceil 3n/2\rceil - 2 \text{ comparisons.}
$$

**Lower bound.** The adversary puts a **+** mark on every element that might still be the maximum and a **−** mark on every element that might still be the minimum: initially both marks on all $n$ elements, $2n$ marks. A correct algorithm must end with exactly one + and one − (on different elements when $n\ge 2$), since the adversary could make any +-marked element the maximum and any −-marked one the minimum. Call an element N (new: both marks), W (only +: it has won every comparison), L (only −: it has lost every comparison) or O (no marks). The adversary answers as follows, keeping actual values so that its answers stay consistent — it raises a W above everything when it must win and lowers an L below everything when it must lose, which contradicts no earlier answer:

| comparison | answer | marks removed |
|---|---|---|
| N vs N | either; the winner becomes W, the loser L | 2 |
| N vs W | W wins (N becomes L) | 1 |
| N vs L or O | N wins (becomes W) | 1 |
| W vs W | either; the loser becomes O | 1 |
| L vs L | either; the winner becomes O | 1 |
| W vs L, and anything vs O otherwise | W wins, L loses, O vs O by value | 0 |

Only N-vs-N comparisons remove two marks, and each uses up two N elements, so there are at most $\lfloor n/2\rfloor$ of them. The algorithm must remove $2n - 2$ marks, so it needs at least $(2n - 2) - \lfloor n/2\rfloor = \lceil 3n/2\rceil - 2$ comparisons.

> [!key] Minimum and maximum
> Finding both the minimum and the maximum of $n$ distinct numbers takes exactly $\lceil 3n/2\rceil - 2$ comparisons in the worst case.

## 13.8 Finding the median

*Given distinct $x_1, \ldots, x_n$, $n$ even, find the index of the $n/2$-th largest.* The lower bound combines two adversary arguments with leaf counting.

> [!key] Lemma 1
> Any comparison tree that finds the median also determines which elements are larger and which are smaller than the median.

> [!proof]- Proof (click to expand)
> Suppose a leaf outputs $x_m$ while some $x_i$ is not known to be larger or smaller than $x_m$. Then no element is known to lie between them, so some input consistent with all comparisons made has $x_i$ and $x_m$ adjacent in sorted order. Swapping their values changes no comparison result on the path, but makes $x_i$ the median: the tree is wrong on that input. $\square$

So a median-finding tree also finds the set $L$ of the $n/2 - 1$ elements larger than the median. Suppose a "little birdie" reveals $L$. That fixes the outcome of every comparison between $L$ and $X\setminus L$, so those nodes can be pruned. The pruned tree finds the largest element of $X\setminus L$ — the median — and $X\setminus L$ has $n/2 + 1$ elements, so by the maximum adversary every leaf of the pruned tree has depth at least $n/2$, and the pruned tree has at least $2^{n/2}$ leaves. Every leaf of the original tree is a leaf of exactly one of the $\binom{n}{n/2-1}$ pruned trees (it determines $L$), so the original tree has at least $\binom{n}{n/2-1}2^{n/2}$ leaves and depth
$$
\frac n2 + \lg\binom{n}{n/2 - 1} = \frac{3n}{2} - O(\log n),
$$
using $\binom{n}{n/2-1}\approx 2^n\sqrt{2/(\pi n)}$. (The note says the pruned tree has depth at least $n/2 - 1$ and gets $n/2 - 1 + \lg\binom{n}{n/2-1}$ — one less; it also drops the constant $\sqrt\pi$ in the estimate. Neither changes $3n/2 - O(\log n)$.)

> [!example] Example — exact values for small $n$
> Exhaustive search over comparison trees gives the true worst-case cost of the median: $1, 4, 8$ comparisons for $n = 2, 4, 6$. The bound $\lceil n/2 + \lg\binom{n}{n/2-1}\rceil$ gives $1, 4, 7$ — exact for $n = 2, 4$.

A more complicated argument raises the median bound to $2n - o(n)$. The same reasoning shows that finding the $k$-th largest of $n$ elements needs at least $n - k + \lceil\lg\binom{n}{k-1}\rceil = \Omega((n - k) + k\log(n/k))$ comparisons; this is tight up to constant factors for all $k\le n/2$, and **exactly** tight for $k = 1$ ($n - 1$) and $k = 2$ ($n - 2 + \lceil\lg n\rceil$). According to the note, these are the only $k\le n/2$ whose exact complexity is known; even $k = 3$ is open.

## Summary

- **Adversary argument**: answer every query consistently but as unhelpfully as possible; if the algorithm stops early, exhibit two consistent inputs with different answers. It must work against **every** query order.
- **Evasive** = all $n$ bits (all $\binom n2$ adjacency entries) must be examined. "Any 1?" is evasive; 01 is evasive iff $n$ is even (Hide01 keeps the undecided gap $r - \ell - 1$ even); only 0 and 1 are evasive for all $n$.
- **Emptiness** and **connectedness** are evasive; the connectedness adversary deletes an edge unless that disconnects the "maybe" graph (reverse Kruskal) and ends with the maximum spanning tree by query time. **AKR conjecture**: every nontrivial monotone graph property is evasive (proved for prime-power $n$).
- **Min and max**: exactly $\lceil 3n/2\rceil - 2$ — pair up, then min of the losers and max of the winners; lower bound by $\pm$ marks: $2n - 2$ marks to remove, at most $\lfloor n/2\rfloor$ comparisons remove two.
- **Median**: knows its partition (Lemma 1); little birdie + maximum adversary + leaf counting: $n/2 + \lg\binom{n}{n/2-1} = 3n/2 - O(\log n)$; $k$-th largest $\ge n - k + \lceil\lg\binom{n}{k-1}\rceil$.
- The note ends with 7 exercises (more evasive patterns, sinks with $O(n)$ probes, scorpions, acyclicity, the second largest, ternary majority trees, egg dropping).

> [!exam] For CS 374
> Not assigned reading this semester (CS 473 material at Illinois). The closest relatives in the course are fooling-set proofs (Midterm 1, Ch 3): two inputs that a machine with too few states cannot tell apart, just as two inputs consistent with all of the adversary's answers cannot be told apart by an algorithm that stopped too early.

### Sources for this page
Erickson, lecture note "Adversary Arguments" (Director's Cut 13, Fall 2013 revision, 8 pp., no status line), §§13.1–13.8, summarized in our own words; the exercises (pp. 6–8) are not solved. The adversaries, the odd-$n$ algorithm, the invariants, the conjecture, the min-and-max algorithm and bound, Lemma 1 and the median argument are the note's; the answer table for the min-and-max adversary is ours (the note describes it in words), as are the figures' concrete states and the small-$n$ example; the names Kahn, Saks and Sturtevant are added (the note cites the prime-power theorem without them). Checked by `tools/checks/n13.py`: decision-tree complexities by exhaustive minimax search — any-ones for $n\le 10$, 01 for $n\le 10$ ($n$ for even $n$, $n-1$ for odd $n\ge 3$), all patterns of length $\le 3$ for $|p|\le n\le 10$, emptiness and connectedness for $n\le 5$, all 22 nontrivial monotone properties of 4-vertex graphs (evasive), min-and-max for $n\le 6$, median for $n = 2, 4, 6$, $k$-th largest for $n\le 6$; the odd-$n$ algorithm on all inputs for odd $n\le 15$; Hide01 (corrected and as printed) against every probe order for even $n\le 8$; HideConnectedness against every query order for $n\le 4$ and random orders for $n\le 8$ (invariants after every step, maximum spanning tree at the end); the min-and-max algorithm on all permutations for $n\le 9$; the mark adversary against 127,226 comparison sequences (all of length $\lceil 3n/2\rceil - 3$ for $n\le 5$, random up to $n = 14$); Lemma 1 on every state of the median search; the binomial estimate numerically. Not checked: the prime-power theorem, the $2n - o(n)$ median bound, the upper bound $O(n + k\log(n/k))$ and the openness of $k = 3$. **Errors in the note:** p. 2, "before looking at all three bits" → all $n$ bits; p. 2, odd $n$: the bit that need not be examined when the even bits read $1\cdots 1 0\cdots 0$ lies "between the last 0 and the first 1" → between the last 1 and the first 0; p. 2, invariant "$r - \ell$ is even" → $r - \ell - 1$ is even; p. 3, Hide01 has the two middle branches swapped (0 when $i - \ell$ is even) — as printed it fails for $n = 2$; p. 4, HideConnectedness removes "$(i, j)$" → $e$; p. 4, "Aanderraa" → Aanderaa; p. 6, the pruned tree has depth at least $n/2 - 1$ → $n/2$ ($X\setminus L$ has $n/2 + 1$ elements; the printed bound is valid, just one weaker than the argument gives), bound $n/2 - 1 + \lg\binom{n}{n/2-1}$ → $n/2 + \lg\binom{n}{n/2-1}$, and $\binom{n}{n/2-1}\approx 2^n/\sqrt{n/2}$ → $2^n\sqrt{2/(\pi n)}$; p. 7, Exercise 1(c) says 11 is evasive iff $n\bmod 3 = 1$ — the search finds the opposite for $n\le 10$: evasive iff $n\bmod 3\ne 1$ (for $n = 4$, three probes suffice). Exercise 1(d) agrees with the search for $n\le 10$.
