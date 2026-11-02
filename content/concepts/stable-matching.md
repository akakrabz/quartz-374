---
title: "Stable matching"
description: "Matching n doctors with n hospitals so that no doctor and hospital prefer each other to their partners: the Gale–Shapley algorithm, its O(n^2) bound, why its output is stable, and why it is the best stable matching for the proposing side and the worst for the other."
tags: [concept, algorithms, greedy]
aliases: ["stable marriage", "Gale-Shapley algorithm", "Gale–Shapley", "unstable pair", "Boston Pool algorithm", "deferred acceptance"]
---

> [!definition] Definition — stable matching and Gale–Shapley
> $n$ doctors and $n$ hospitals each rank the whole other side, without ties. In a perfect matching, a doctor $\alpha$ and a hospital $B$ that are not matched with each other form an **unstable pair** if $\alpha$ prefers $B$ to her hospital and $B$ prefers $\alpha$ to its doctor; a matching is **stable** if no unstable pair exists. **Gale–Shapley (hospitals offer):** while some hospital is unmatched, it offers its position to the best doctor who has not yet rejected it; the doctor accepts if she is free or prefers this offer to her current one (dropping that one), and rejects it otherwise. At most $n^2$ offers, $O(n^2)$ time.

**Why it works.** A doctor, once offered, stays matched and only trades up, so the algorithm ends with a perfect matching. If $\alpha$ ends with $A$ but prefers $B$, then $B$ never offered to her (she would hold $B$ or better), so $B$ stopped at a doctor it likes more than $\alpha$: no unstable pair. Moreover hospitals are only ever rejected by doctors they cannot have in *any* stable matching (Lemma 4.7), so every hospital gets $\textsf{best}(A)$, its best partner over all stable matchings, and every doctor gets $\textsf{worst}(\alpha)$ — regardless of the order of offers.

> [!recipe] Recipe — running Gale–Shapley by hand
> 1. Keep, for every hospital, a pointer into its list; for every doctor, her current offer.
> 2. Pick any free hospital, advance its pointer, and let the doctor compare: keep the better of the two offers and free the other hospital.
> 3. Stop when no hospital is free. Check stability pair by pair: for each hospital, only the doctors it ranks above its partner can form an unstable pair.

> [!trap]
> - **Who proposes matters.** The proposing side gets its best stable partners, the other side its worst. Swapping roles can change the result.
> - **No second thoughts, no stability:** a protocol in which accepted offers are final can end unstable, and resolving unstable pairs one at a time can cycle.
> - **A doctor rejects only for a better offer** — she never trades down and is never unmatched after her first offer.
> - **Order does not matter** for the final matching, so do not argue about which free hospital goes next.

**Example.** Hospitals $A\colon q\succ r\succ s$, $B\colon r\succ s\succ q$, $C\colon s\succ q\succ r$; doctors $q\colon B\succ C\succ A$, $r\colon C\succ A\succ B$, $s\colon A\succ B\succ C$. With hospitals offering, each first offer is accepted: $\{Aq, Br, Cs\}$ after 3 offers — every hospital gets its first choice, every doctor her last. With doctors offering: $\{As, Bq, Cr\}$, the reverse. The third and only other stable matching, $\{Ar, Bs, Cq\}$, gives everyone a second choice.

**Where it appears.** [[2-algorithms/04-greedy-algorithms#45-stable-matching|§4.5]] (the bad ideas, the book's four-by-four run, the $O(n^2)$ implementation, correctness, Lemma 4.7 and Corollaries 4.8–4.9, why the NRMP lets doctors propose).

Related: [[concepts/greedy-algorithms]] · [[concepts/interval-scheduling]] · [[concepts/huffman-codes]]
