---
title: "Minimum-cost flows"
description: "The cheapest feasible flow when every edge has a cost per unit: optimal exactly when the residual graph has no negative cycle; solved by cycle canceling or by successive shortest paths, which node potentials (reduced costs) speed up from Bellman–Ford to Dijkstra; transshipment, transportation and assignment are special cases."
tags: [concept, algorithms, flows]
aliases: ["min-cost flow", "minimum-cost flow", "minimum-cost circulation", "cycle canceling", "successive shortest paths", "reduced costs", "node potentials", "transportation problem", "transshipment problem"]
---

> [!key] Minimum-cost flow (note G)
> Edges have capacities $c$, lower bounds $\ell$ and a **cost** per unit (any sign); vertices have balances $b$ (inflow − outflow, summing to 0). Find a feasible flow minimizing $\textsf{cost}(f) = \sum_e\textsf{cost}(e)\,f(e)$. In the residual graph a forward edge keeps its cost and a backward edge costs minus its edge's cost.
> - **Optimality:** a feasible flow is optimal $\iff$ its residual graph has **no negative cycle**.
> - **Cycle canceling** (Klein): from a feasible flow, push around negative residual cycles (Bellman–Ford, $O(VE)$ each) — $O(VE^2CK)$ with integer capacities $\le C$ and costs $\le K$ in absolute value.
> - **Successive shortest paths:** from a pseudoflow without negative residual cycles, push along a cheapest path from an excess to a deficit; no negative cycle ever appears. At most $B = \sum_v\lvert b(v)\rvert/2$ iterations with integer capacities and balances.
> - **Reduced costs:** $\textsf{cost}_\pi(u\to v) = \pi(u) + \textsf{cost}(u\to v) - \pi(v)$. With $\pi\leftarrow\pi + \textsf{dist}$ after each shortest-path computation, all residual reduced costs stay $\ge 0$, so Dijkstra suffices: $O(BE\log V)$.

**Why it works.** Two feasible flows differ by a circulation in the residual graph of the first, which decomposes into residual cycles; if none of them is negative, nothing is cheaper. Pushing along a *shortest* path keeps negative cycles away, because a negative cycle through the new backward edges, combined with the path, would contain a cheaper path. Potentials change every path between two fixed vertices by the same amount and every cycle by nothing, so they never change which path is shortest — they only make the edge costs non-negative, which is what Dijkstra needs. This is the reweighting of Johnson's algorithm, invented here first.

> [!recipe] Recipe — choosing the tool
> 1. **Maximum flow** is the minimum-cost circulation with one extra edge $t\to s$ of cost $-1$; a **shortest path** is a single-supply transshipment.
> 2. **Is a given flow optimal?** Look for a negative cycle in its residual graph (Bellman–Ford); one is a certificate of improvement, none a certificate of optimality.
> 3. **To compute one:** make lower bounds 0 and costs non-negative with an initial pseudoflow, then run successive shortest paths with potentials (Dijkstra). For big numbers, cite a strongly polynomial algorithm (Orlin, $O(E^2\log^2 V)$).
> 4. **Uncapacitated, bipartite** supply-to-demand problems are transportation problems; with unit supplies and demands, assignment (minimum-cost perfect matching, Hungarian method, $O(V^3)$).

> [!trap]
> - **Backward residual edges have negative costs**, so the residual graph usually has negative edges even when the network has none — plain Dijkstra fails without potentials.
> - **Update the potentials by adding the distances**, $\pi\leftarrow\pi + \textsf{dist}$; replacing them, $\pi\leftarrow\textsf{dist}$, can create negative reduced costs.
> - **With lower bounds, a backward edge cancels only $f - \ell$**, not all of $f$.
> - **"Reduced cost" is not "cost":** compare reduced lengths only between paths with the same endpoints; convert back with $-\pi(\text{start}) + \pi(\text{end})$.

**Example.** Send 2 units from $s$ to $t$ through edges $s\to a$, $s\to b$, $a\to b$, $a\to t$, $b\to t$, all of capacity 1, with costs 1, 3, 1, 3, 1. The cheapest path $s\to a\to b\to t$ (cost 3) fills $a\to b$, $s\to a$ and $b\to t$; along forward edges $s$ can now reach only $b$, a dead end. The residual graph still has $s\to b\to a\to t$ through the backward edge $b\to a$, of cost $3 - 1 + 3 = 5$; pushing along it cancels the flow on $a\to b$ and leaves $s\to a\to t$ plus $s\to b\to t$, total $3 + 5 = 8$, the minimum. After the first path the potentials $\pi = (0, 1, 2, 3)$ (the first Dijkstra's distances) give reduced costs 1 to $s\to b$ and $a\to t$ and 0 to $b\to a$, $a\to s$, $t\to b$ — all non-negative.

**Where it appears.** [[4-lecture-notes/g-minimum-cost-flows#g1-minimum-cost-circulations|Note G §G.1]] (circulations, cycle canceling, the two-stage general algorithm), [[4-lecture-notes/g-minimum-cost-flows#g2-successive-shortest-paths|§G.2]] (successive shortest paths, Lemma G.1), [[4-lecture-notes/g-minimum-cost-flows#g3-node-potentials-and-reduced-costs|§G.3]] (potentials, Lemmas G.2 and G.3), [[4-lecture-notes/g-minimum-cost-flows#g4-transshipment-and-transportation|§G.4]] (transshipment, transportation, assignment, shortest paths); built on [[4-lecture-notes/f-balances-and-pseudoflows|note F]] (balances, pseudoflows) and [[2-algorithms/10-maximum-flows-and-minimum-cuts#103-the-maxflow-mincut-theorem|§10.3]] (residual graphs); reweighting in [[2-algorithms/09-all-pairs-shortest-paths#93-reweighting|§9.3]].

Related: [[concepts/maximum-flow]] · [[concepts/ford-fulkerson]] · [[concepts/flow-reductions]] · [[concepts/bellman-ford]] · [[concepts/johnsons-algorithm]] · [[concepts/dijkstras-algorithm]] · [[concepts/bipartite-matching]]
