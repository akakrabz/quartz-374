---
title: "Splay trees"
description: "Self-adjusting binary search trees that move every accessed node to the root by zig, zig-zig (roller-coaster) and zig-zag rotations — O(log n) amortized per operation by the Access Lemma with potential Σ lg size(v) — and scapegoat trees, which rebuild unbalanced subtrees instead of rotating."
tags: [concept, algorithms, data-structures]
aliases: ["splay tree", "splaying", "Access Lemma", "scapegoat tree", "scapegoat trees", "tree rotation", "zig-zag", "zig-zig", "roller-coaster", "partial rebuilding", "global rebuilding"]
---

> [!key] Splay trees (Sleator and Tarjan)
> A binary search tree that, after every search, insertion or deletion, **splays** the node $x$ it touched to the root. While $x$ has a parent $y$:
> - $y$ is the root: rotate at $x$ (**zig**);
> - $x$ and $y$ are children on the same side: rotate at $y$, then at $x$ (**zig-zig**, or roller-coaster);
> - on opposite sides: rotate at $x$ twice (**zig-zag**).
>
> With the potential $\Phi = \sum_v\lg\text{size}(v)$, the **Access Lemma** bounds the amortized cost of splaying $x$ by $1 + 3\bigl(\lg n - \lg\text{size}(x)\bigr)\le 1 + 3\lg n$ rotations. Every operation takes $O(\log n)$ amortized time, and any $m$ operations starting from an empty tree take $O(m\log n)$ time.

**Why it works.** A double rotation lifts $x$ two levels; its two rotations are paid by three times the increase of $x$'s rank, $3(r'(x) - r(x))$, because the concavity of $\lg$ forces the potential to drop whenever $x$'s rank barely grows. Along a splay these increases telescope to $3(r(\text{root}) - r(x))$, plus 1 for a final single rotation. Long, expensive splays happen only in unbalanced trees with large potential, and they release it.

> [!recipe] Recipe — splaying by hand
> 1. Look at $x$, its parent and its grandparent.
> 2. Same side → rotate at the **parent first**, then at $x$. Opposite sides → rotate at $x$ twice. No grandparent → rotate at $x$ once.
> 3. Repeat until $x$ is the root: $\text{depth}(x)$ rotations in all.
> 4. Delete $x$: splay it, remove it, splay the largest key of the left subtree within that subtree, and hang the right subtree under it.

> [!trap]
> - **Not move-to-root.** Rotating $x$ up by single rotations alone has no such guarantee: its amortized cost can be $\Omega(n)$ per access (the note's Exercise 3).
> - **The zig-zig order matters:** parent first, then $x$.
> - **Amortized, not worst case:** after inserting $1, \ldots, n$ in increasing order, searching for 1 takes $n - 1$ rotations.
> - **Ranks are $\lg\text{size}(v)$, not $\lfloor\lg\text{size}(v)\rfloor$** (with floors the Access Lemma fails), and the amortized cost adds the *increase* of $\Phi$.
> - **Scapegoat trees are different:** no rotations; after an insertion they rebuild the lowest subtree with $\text{height}(v) > \alpha\lg\text{size}(v)$ perfectly balanced, and deletions only mark nodes until half are marked. They give $O(\log n)$ worst-case searches and $O(\log n)$ amortized updates.

**Example.** Inserting $1, 2, \ldots, 15$ in increasing order costs one rotation per insertion after the first — 14 in all — and leaves a path: 15 at the root, each key the left child of the next. Searching for 1 is then as expensive as an access can be: 14 rotations, seven zig-zigs. Afterwards the height is 8 instead of 14, and $\Phi$ has dropped from $\lg 15!\approx 40.25$ to $23.21$, so the amortized cost is $14 - 17.04\approx -3.04$, far below $1 + 3\lg 15\approx 12.72$: the cheap insertions prepaid the expensive search.

**Where it appears.** [[4-lecture-notes/10-scapegoat-and-splay-trees#105-rotations-double-rotations-and-splaying|note 10, §10.5]] (rotations and splaying), [[4-lecture-notes/10-scapegoat-and-splay-trees#106-splay-trees|§10.6]] (splay trees and the Access Lemma), [[4-lecture-notes/10-scapegoat-and-splay-trees#107-other-optimality-properties|§10.7]] (weights, static optimality, finger and working-set theorems), [[4-lecture-notes/10-scapegoat-and-splay-trees#103-insertions-partial-rebuilding|§10.3]] and [[4-lecture-notes/10-scapegoat-and-splay-trees#104-scapegoat-lazy-height-balanced-trees|§10.4]] (partial rebuilding, scapegoat trees); treaps, the randomized alternative, in [[4-lecture-notes/03-treaps-and-skip-lists|note 3]]; optimal static search trees in [[2-algorithms/03-dynamic-programming#39-optimal-binary-search-trees|§3.9]].

Related: [[concepts/amortized-analysis]] · [[concepts/optimal-binary-search-trees]] · [[concepts/treaps]] · [[concepts/union-find]]
