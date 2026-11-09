---
title: "Amortized analysis"
description: "Bounding the total cost of every sequence of operations and charging each operation its share: the aggregate (summation), accounting (taxation and charging) and potential methods, an odometer example, and the traps — no probability, no bound on a single operation, mind the starting state."
tags: [concept, algorithms, data-structures]
aliases: ["amortized time", "amortized cost", "amortization", "potential method", "potential function", "accounting method", "aggregate method", "taxation method", "charging method"]
---

> [!definition] Definition — amortized cost
> Operations on a data structure have **amortized costs** $a(\cdot)$ if **every** sequence of operations $o_1, \ldots, o_n$ from the initial state has total actual cost $\sum_i c_i\le\sum_i a(o_i)$. Three ways to prove it:
> - **Aggregate (summation) method:** bound the worst-case total $T(n)$ of $n$ operations; each costs $T(n)/n$.
> - **Accounting method:** *taxation* — charge each operation a fixed tax and show the saved credit never goes negative; or *charging* — bill expensive steps to earlier operations, each of which receives $O(1)$ charge.
> - **Potential method:** pick $\Phi$ on the states with $\Phi_i\ge\Phi_0$ for all $i$, and set
> $$
> a_i = c_i + \Phi_i - \Phi_{i-1}.
> $$

**Why it works.** The amortized costs telescope: $\sum a_i = \sum c_i + \Phi_n - \Phi_0\ge\sum c_i$. The potential is prepaid work stored in the structure: cheap operations raise it a little, and an expensive operation is paid for by a large drop. Taxation is the special case where the potential is a sum of credits on individual parts.

> [!recipe] Recipe — a potential-function proof
> 1. Define $\Phi$ as a function of the current structure; check $\Phi_0 = 0$ and $\Phi\ge 0$ (or just $\Phi\ge\Phi_0$).
> 2. For each operation, write its actual cost $c$ and the change $\Delta\Phi$ in the same terms (bits set and cleared, items moved, …).
> 3. Show $c + \Delta\Phi\le$ the claimed bound; the expensive part of $c$ must be cancelled by a drop of $\Phi$.
> 4. Conclude: any $n$ operations cost at most the sum of the bounds.
>
> Typical potentials: the number of 1 bits (binary counters, cost 2 per Increment); $2\cdot\text{size} - \text{capacity}$ (an array that doubles when full, cost 3 per append); $\sum_v\lg\text{size}(v)$ (splay trees, [[concepts/splay-trees]]).

> [!trap]
> - **Amortized is not average-case or expected.** No probability: it is a worst-case bound on the total of every sequence.
> - **It does not bound one operation.** An Increment is $O(1)$ amortized but $\Theta(\log n)$ in the worst case.
> - **Mind the starting state.** From an arbitrary state the total is $\sum a_i + \Phi_0 - \Phi_n$; a counter starting at $v$ can cost $\#_1(v)$ more than $2n$.
> - **Every operation must be covered.** A binary counter that also decrements is not $O(1)$ amortized: alternating between $2^k - 1$ and $2^k$ costs $k + 1$ every time.
> - **Amortized bounds are not unique**: different potentials can split the same total differently among the operations.

**Example.** A decimal odometer counts from 0 to $n$. Digit $i$ changes $\lfloor n/10^i\rfloor$ times, so the total is $(10n - s(n))/9 < 10n/9$, where $s(n)$ is the digit sum of $n$. With the potential $\Phi$ = (digit sum)/9, an increment that turns $t$ trailing 9s into 0s and raises one digit costs $t + 1$ and changes $\Phi$ by $(1 - 9t)/9$: amortized exactly $10/9$. Counting to 1000 changes $1000 + 100 + 10 + 1 = 1111$ digits, although the single step $999\to 1000$ changes 4.

**Where it appears.** [[4-lecture-notes/09-amortized-analysis#92-counting-from-0-to-n|note 9, §9.2]] (the four methods on the binary counter), [[4-lecture-notes/09-amortized-analysis#93-incrementing-and-decrementing|§9.3]] (the double counter), [[4-lecture-notes/10-scapegoat-and-splay-trees|note 10]] (rebuilding and splaying), [[4-lecture-notes/11-disjoint-sets|note 11]] (union-find); quoted bounds in the textbook: Fibonacci heaps in [[2-algorithms/08-shortest-paths#86-best-first-dijkstras-algorithm|§8.6]] and [[2-algorithms/07-minimum-spanning-trees#74-jarníks-prims-algorithm|§7.4]], union-find in [[2-algorithms/07-minimum-spanning-trees#75-kruskals-algorithm|§7.5]].

Related: [[concepts/splay-trees]] · [[concepts/union-find]] · [[concepts/dijkstras-algorithm]] · [[concepts/minimum-spanning-trees]]
