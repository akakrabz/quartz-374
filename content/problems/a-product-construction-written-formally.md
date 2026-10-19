---
title: "Worked problem — A product construction, written formally"
description: "Strings whose number of 1s is divisible by 3 and that contain no 00: the two factor DFAs, the product written as a formal tuple with its full transition table, why its 9 states shrink to 7, and a 7-string fooling set proving that 7 is the minimum."
tags: [problem, regular, midterm-1]
---

*Problem · a DFA built by the product construction, as in a Midterm 1 DFA problem, plus a minimality question · uses [[1-models-of-computation/03-finite-state-machines#36-the-product-construction|§3.6]], [[1-models-of-computation/03-finite-state-machines#310-minimal-automata-moores-algorithm|§3.10]] · concepts: [[concepts/product-construction]], [[concepts/fooling-sets]], [[concepts/dfa-minimization]]*

> [!question] Problem
> Let $L$ be the set of binary strings $w$ such that $\#(\mathtt{1},w)$, the number of 1s in $w$, is divisible by 3, **and** $w$ does not contain the substring `00`. For example, $\varepsilon$, `0`, `111`, `0111` and `10101` are in $L$; `1`, `11`, `00` and `1001` are not.
>
> (a) Give DFAs $M_1$ and $M_2$, with mnemonic state names, for the two conditions separately.
>
> (b) Describe a DFA for $L$ formally by the product construction: its states, start state, transition function and accepting states.
>
> (c) How many states does your product DFA have? Is it minimal? Find the number of states of a minimal DFA for $L$, and prove that no DFA with fewer states accepts $L$.

## (a) The two factors

**Idea.** One condition is a counter, the other a pattern. $M_1$ remembers the number of 1s mod 3. $M_2$ remembers just enough about the end of the input to notice `00`: whether the last symbol was a 0 — and, once `00` has appeared, that it has.

> [!key] Answer (a)
> **$M_1$:** $Q_1 = \{0, 1, 2\}$, $s_1 = 0$, $A_1 = \{0\}$, $\delta_1(r,\mathtt{0}) = r$ and $\delta_1(r,\mathtt{1}) = (r+1)\bmod 3$. State $r$ means: the number of 1s read so far is $\equiv r\pmod 3$.
>
> **$M_2$:** $Q_2 = \{\textsf{safe},\textsf{zero},\textsf{dead}\}$, $s_2 = \textsf{safe}$, $A_2 = \{\textsf{safe},\textsf{zero}\}$, and
>
> | state | meaning: the input read so far … | on $\mathtt{0}$ | on $\mathtt{1}$ |
> |---|---|---|---|
> | → $\textsf{safe}$ \* | contains no `00`, and is empty or ends in 1 | $\textsf{zero}$ | $\textsf{safe}$ |
> | $\textsf{zero}$ \* | contains no `00`, and ends in 0 | $\textsf{dead}$ | $\textsf{safe}$ |
> | $\textsf{dead}$ | contains `00` | $\textsf{dead}$ | $\textsf{dead}$ |

<!-- fig:prob1-product-factors -->
<figure class="cs-fig"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 178" width="640" height="178" role="img" style="font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-size:14px"><title>left: three-state cycle counting 1s mod 3; right: three-state DFA safe, zero, dead</title><defs><marker id="ARR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs><text x="160" y="14" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">M₁: number of 1s mod 3</text><text x="490" y="14" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">M₂: no 00</text><path d="M55.7,72.6 C29.8,34.5 102.2,34.5 77.5,70.4" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="66" y="27.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">0</text><path d="M157.1,75.2 C131.4,37 200.6,37 176.1,73" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="166" y="30.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">0</text><path d="M257.1,75.2 C231.4,37 300.6,37 276.1,73" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="266" y="30.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">0</text><path d="M88,92 L144.5,92" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="117.5" y="81" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">1</text><path d="M185,92 L244.5,92" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="216" y="81" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">1</text><path d="M248.6,99.7 Q166,136 88.4,101.9" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="166.7" y="128.1" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">1</text><path d="M371.1,75.2 C345.4,37 414.6,37 390.1,73" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="380" y="30.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">1</text><path d="M408,82.8 Q435,74 459.6,82.1" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="435" y="67.4" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">0</text><path d="M462,101.2 Q435,110 410.4,101.9" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="435" y="116.6" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">1</text><path d="M518,92 L564.5,92" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="542.5" y="81" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">0</text><path d="M583.1,75.2 C557.4,37 626.6,37 602.1,73" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="592" y="30.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">0,1</text><line x1="18" y1="92" x2="41.5" y2="92" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" marker-end="url(#ARR)"/><circle cx="66" cy="92" r="23" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><circle cx="66" cy="92" r="19" fill="var(--accent)" fill-opacity="0.1" stroke="currentColor" stroke-width="1.6"/><text x="66" y="93" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">0</text><circle cx="166" cy="92" r="19" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="166" y="93" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">1</text><circle cx="266" cy="92" r="19" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="266" y="93" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">2</text><line x1="380" y1="140" x2="380" y2="116.5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" marker-end="url(#ARR)"/><rect x="351" y="69" width="58" height="46" rx="23" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><rect x="355" y="73" width="50" height="38" rx="19" fill="var(--accent)" fill-opacity="0.1" stroke="currentColor" stroke-width="1.6"/><text x="380" y="93" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">safe</text><rect x="461" y="69" width="58" height="46" rx="23" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><rect x="465" y="73" width="50" height="38" rx="19" fill="var(--accent)" fill-opacity="0.1" stroke="currentColor" stroke-width="1.6"/><text x="490" y="93" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">zero</text><rect x="567" y="73" width="50" height="38" rx="19" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/><text x="592" y="93" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">dead</text></svg><figcaption><strong>The two factors.</strong> <i>M</i>₁ keeps the number of 1s mod 3 and accepts 0. <i>M</i>₂ keeps <i>safe</i> (no 00 yet, and the input is empty or ends in 1), <i>zero</i> (no 00 yet, ends in 0) or <i>dead</i> (00 has appeared, a dump state); it accepts <i>safe</i> and <i>zero</i>. The product's states are the nine pairs (<i>r</i>, <i>p</i>).</figcaption></figure>

Both factors are minimal on their own: three remainders need three states, and $\textsf{safe}$ and $\textsf{zero}$ differ on the suffix `0`.

## (b) The product, formally

**Idea.** Run both machines in parallel on the same input. A state of the product is a pair — one state of each machine — and by Lemma 3.1 the product is in state $(\delta_1^*(s_1,w), \delta_2^*(s_2,w))$ after reading $w$. For $\cap$, accept when *both* components accept.

> [!key] Answer (b)
> $M = (\Sigma, Q, s, A, \delta)$ with
> $$
> Q = Q_1\times Q_2 = \{0,1,2\}\times\{\textsf{safe},\textsf{zero},\textsf{dead}\},\qquad s = (s_1, s_2) = (0,\textsf{safe}),
> $$
> $$
> \delta\big((r,p),a\big) = \big(\delta_1(r,a),\ \delta_2(p,a)\big),\qquad A = A_1\times A_2 = \{(0,\textsf{safe}),\ (0,\textsf{zero})\}.
> $$
> State $(r,p)$ means: the number of 1s read so far is $\equiv r\pmod 3$, *and* the input so far is in situation $p$ of $M_2$. Written out:
>
> | state | on $\mathtt{0}$ | on $\mathtt{1}$ |
> |---|---|---|
> | → $(0,\textsf{safe})$ \* | $(0,\textsf{zero})$ | $(1,\textsf{safe})$ |
> | $(1,\textsf{safe})$ | $(1,\textsf{zero})$ | $(2,\textsf{safe})$ |
> | $(2,\textsf{safe})$ | $(2,\textsf{zero})$ | $(0,\textsf{safe})$ |
> | $(0,\textsf{zero})$ \* | $(0,\textsf{dead})$ | $(1,\textsf{safe})$ |
> | $(1,\textsf{zero})$ | $(1,\textsf{dead})$ | $(2,\textsf{safe})$ |
> | $(2,\textsf{zero})$ | $(2,\textsf{dead})$ | $(0,\textsf{safe})$ |
> | $(0,\textsf{dead})$ | $(0,\textsf{dead})$ | $(1,\textsf{dead})$ |
> | $(1,\textsf{dead})$ | $(1,\textsf{dead})$ | $(2,\textsf{dead})$ |
> | $(2,\textsf{dead})$ | $(2,\textsf{dead})$ | $(0,\textsf{dead})$ |

**Check.** On `0111`: $(0,\textsf{safe})\xrightarrow{\mathtt{0}}(0,\textsf{zero})\xrightarrow{\mathtt{1}}(1,\textsf{safe})\xrightarrow{\mathtt{1}}(2,\textsf{safe})\xrightarrow{\mathtt{1}}(0,\textsf{safe})$: accept. On `1001`: $(0,\textsf{safe})\to(1,\textsf{safe})\to(1,\textsf{zero})\to(1,\textsf{dead})\to(2,\textsf{dead})$: reject — and once the second component is $\textsf{dead}$, no continuation can make the product accept.

> [!trap] Where product answers lose points
> - **"Run $M_1$ and $M_2$ in parallel" and nothing else.** The rubric wants each factor completely and then the product's states, start state, transitions and accepting set. The accepting set is the only part that knows whether you mean $\cap$, $\cup$ or $\setminus$.
> - **The wrong accepting set.** $\{(r,p) \mid r = 0 \text{ or } p\ne\textsf{dead}\}$ is the union: it accepts `1`, which has no `00` but one 1.
> - **Pairs without meanings.** $(2,\textsf{zero})$ is a mnemonic name because each component is; names like $q_7$ are not.

## (c) Nine states, but seven are enough

**The count.** The product has $3\times3 = 9$ states, and all 9 are reachable: $\mathtt{1}^r$ reaches $(r,\textsf{safe})$, $\mathtt{1}^r\mathtt{0}$ reaches $(r,\textsf{zero})$, and $\mathtt{1}^r\mathtt{00}$ reaches $(r,\textsf{dead})$. Reachable does not mean necessary, though. The three states $(0,\textsf{dead})$, $(1,\textsf{dead})$, $(2,\textsf{dead})$ are non-accepting and lead only to each other, so from none of them does any suffix lead to acceptance. No suffix distinguishes them: they are equivalent, and merging them into one dump state gives a 7-state DFA for $L$. Moore's algorithm agrees — it marks every pair of states except the pairs of dead states.

**The lower bound.** Seven states are also necessary. Take one string for each state of the merged DFA,
$$
F = \{\varepsilon,\ \mathtt{1},\ \mathtt{11},\ \mathtt{0},\ \mathtt{10},\ \mathtt{110},\ \mathtt{00}\},
$$
which reach $(0,\textsf{safe})$, $(1,\textsf{safe})$, $(2,\textsf{safe})$, $(0,\textsf{zero})$, $(1,\textsf{zero})$, $(2,\textsf{zero})$ and the dump state. For a string $x$ without `00`, let $t_x\in\{0,1,2\}$ be the number of 1s that $x$ lacks to a multiple of 3: $t_x = (3-\#(\mathtt{1},x))\bmod 3$.

> [!example] Proof that $F$ is a fooling set
> Let $x$ and $y$ be arbitrary distinct strings in $F$. Whether a suffix distinguishes $x$ and $y$ does not depend on which of the two is called $x$, so it suffices to consider three cases.
> - **One of them is `00`; call it $y$.** Let $z = \mathtt{1}^{t_x}$. Then $xz$ contains no `00` ($x$ contains none, and appending 1s creates none), and its number of 1s is $\#(\mathtt{1},x)+t_x\equiv0\pmod 3$, so $xz\in L$. But $yz$ contains `00`, so $yz\notin L$.
> - **Neither is `00`, and they contain different numbers of 1s.** In $F$ these numbers are among 0, 1, 2, so they differ mod 3. Let $z = \mathtt{1}^{t_x}$. As before, $xz\in L$. And $yz$ contains no `00`, but $\#(\mathtt{1},yz) = \#(\mathtt{1},y)+t_x\not\equiv\#(\mathtt{1},x)+t_x\equiv0\pmod 3$, so $yz\notin L$.
> - **Neither is `00`, and they contain equally many 1s.** These are the pairs $\varepsilon/\mathtt{0}$, $\mathtt{1}/\mathtt{10}$ and $\mathtt{11}/\mathtt{110}$; call $x$ the one that is empty or ends in 1, and $y$ the one that ends in 0. Let $z = \mathtt{0}\mathtt{1}^{t_x}$. Then $x\mathtt{0}$ contains no `00`, because $x$ does not end in 0, and neither does $xz$; its number of 1s, $\#(\mathtt{1},x)+t_x$, is divisible by 3; so $xz\in L$. But in $yz$ the last 0 of $y$ is followed by the first 0 of $z$, so $yz\notin L$.
>
> Every two distinct strings of $F$ have a distinguishing suffix, so $F$ is a fooling set of size 7, and every DFA for $L$ has at least 7 states. $\blacksquare$

> [!key] Answer (c)
> The product DFA has **9** states, all reachable, but it is **not minimal**: $(0,\textsf{dead})$, $(1,\textsf{dead})$ and $(2,\textsf{dead})$ are equivalent. Merging them gives a 7-state DFA, and the 7-element fooling set $F$ shows that **7 is the minimum**.

**Which operations let the dead states merge.** After a `00`, the fate of a string under $\cap$ no longer depends on its number of 1s: it is out of $L$ whatever follows. That is why the three dead states merge. The same happens for every combination whose answer, once `00` has appeared, ignores the count — $L_2\setminus L_1$, or the complement of $L_1\cap L_2$, also need only 7 states. For $L_1\cup L_2$, $L_1\setminus L_2$ or $L_1\oplus L_2$ the count still matters after a `00`, and the 9-state product is already minimal. So the product of two minimal DFAs need not be minimal, and whether it is depends on the boolean operation: $mn$ states always suffice, and sometimes fewer do.

> [!exam] How a product construction is graded
> On a DFA problem, a product construction is graded with the DFA rubric (out of 10): **2** for an unambiguous, complete description — which for a product means each factor completely, then the product's states, start state, transitions and **accepting states**; **6** for correctness; **2** for mnemonic state names (pairs named by their components, like $(2,\textsf{zero})$, qualify). Minimality is not required: the 9-state product earns full credit. Statements like "the product of two minimal DFAs is minimal" (false, as (c) shows) are natural true/false items. See [[0-toolkit/06-how-exams-are-graded|how exams are graded]].

### Sources for this page
An original problem. The product construction, Lemma 3.1, fooling sets and Moore's algorithm are from Erickson, *Models of Computation*, §§3.6–3.10, described in our own words. Checked by `tools/checks/problems_1.py`: both factors and their state meanings, the product against the definition of $L$ on all strings of length at most 14, the 9-row table entry by entry, reachability, the equivalent states (only the three dead states merge), the 7-state minimum, the fooling-set suffix rule on all 21 pairs, the example strings and runs, the union trap, and the minimal state counts for the other boolean combinations (9 for $\cup$, $L_1\setminus L_2$ and $\oplus$; 7 for $L_2\setminus L_1$ and the complement of $\cap$).
