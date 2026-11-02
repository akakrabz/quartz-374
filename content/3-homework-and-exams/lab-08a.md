---
title: "Lab 8a — Dynamic programming: sledding ramps"
description: "Maximum air time down a hill of ramps: a one-index recurrence over the next ramp reached on the ground, then an extra parameter for a limit of k jumps, then two sledders who may not share a ramp — a four-parameter state that remembers where each sledder next touches the ground."
tags: [lab, algorithms, dynamic-programming, midterm-2]
---

*Lab 8a · October 14 · CS/ECE 374 A, Fall 2026 · [[concepts/dynamic-programming|dynamic programming]] · uses [[2-algorithms/03-dynamic-programming#34-the-pattern-smart-recursion|§3.4]], [[2-algorithms/04-greedy-algorithms#42-scheduling-classes|§4.2]] · rubric: [[0-toolkit/06-how-exams-are-graded#12-dynamic-programming|how exams are graded §12]] · solutions: explained from the official solutions*

> [!abstract] In one breath
> A sledder goes down a hill past ramps at sorted positions $\mathit{Ramp}[1\,..\,n]$; jumping at ramp $i$ means flying $\mathit{Length}[i]$ and skipping every ramp underneath. All three problems turn on one observation: **once a sledder is on the ground at a ramp, the past no longer matters** — only which ramp comes next. So Problem 1 is a one-index recurrence over suffixes (jump here and continue at $\textsf{Next}(i)$, the first ramp past the landing point, or sled on to ramp $i+1$), solved in $O(n\log n)$ time. Problem 2 adds the number of jumps left as a second parameter: $O(n\log n + nk)$. Problem 3 has two sledders who may not share a ramp: remember the next ramp each one reaches on the ground and the jumps each has left — four parameters, $O(n^2k^2)$ — and notice that the sledders only interact when both are on the ground at the same ramp.

## Problem 1 — Maximum air time

> [!question] Problem 1
> Amy and Banjin hold a sledding contest on a hill with $n$ snow ramps; each wants to spend as much distance in the air as possible. Whenever a sledder reaches a ramp *while on the ground*, she may use it to jump — possibly flying over one or more later ramps, which then cannot be used to extend the jump — or sled past it and stay on the ground. The input is a sorted array $\mathit{Ramp}[1\,..\,n]$, where $\mathit{Ramp}[i]$ is the distance from the top of the hill to ramp $i$, and an unsorted array $\mathit{Length}[1\,..\,n]$, where $\mathit{Length}[i]$ is the distance that a sledder who takes ramp $i$ travels through the air. Describe and analyze an algorithm that computes the maximum total distance a sledder can travel through the air.

The figure shows the small instance used on this page (ramps at 2, 4, 7, 12, 15, 19, 23 with lengths 3, 5, 4, 2, 6, 9, 1) and the answers to all three problems on it; look at it after you have tried them.

<!-- fig:lab-08a-ramps -->
<figure class="cs-fig"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 336" width="640" height="336" role="img" style="font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-size:13px"><title>four rows of ramps along a hill with jump arcs for the optimal solutions</title><defs><marker id="ARR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs><text x="147" y="14" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;font-weight:600;">1</text><line x1="147" y1="22" x2="147" y2="306" stroke="var(--muted)" stroke-width="0.6" stroke-linecap="round" stroke-dasharray="2 3" opacity="0.6"/><text x="182" y="14" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;font-weight:600;">2</text><line x1="182" y1="22" x2="182" y2="306" stroke="var(--muted)" stroke-width="0.6" stroke-linecap="round" stroke-dasharray="2 3" opacity="0.6"/><text x="234.5" y="14" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;font-weight:600;">3</text><line x1="234.5" y1="22" x2="234.5" y2="306" stroke="var(--muted)" stroke-width="0.6" stroke-linecap="round" stroke-dasharray="2 3" opacity="0.6"/><text x="322" y="14" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;font-weight:600;">4</text><line x1="322" y1="22" x2="322" y2="306" stroke="var(--muted)" stroke-width="0.6" stroke-linecap="round" stroke-dasharray="2 3" opacity="0.6"/><text x="374.5" y="14" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;font-weight:600;">5</text><line x1="374.5" y1="22" x2="374.5" y2="306" stroke="var(--muted)" stroke-width="0.6" stroke-linecap="round" stroke-dasharray="2 3" opacity="0.6"/><text x="444.5" y="14" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;font-weight:600;">6</text><line x1="444.5" y1="22" x2="444.5" y2="306" stroke="var(--muted)" stroke-width="0.6" stroke-linecap="round" stroke-dasharray="2 3" opacity="0.6"/><text x="514.5" y="14" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;font-weight:600;">7</text><line x1="514.5" y1="22" x2="514.5" y2="306" stroke="var(--muted)" stroke-width="0.6" stroke-linecap="round" stroke-dasharray="2 3" opacity="0.6"/><text x="112" y="322" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">0</text><text x="199.5" y="322" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">5</text><text x="287" y="322" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">10</text><text x="374.5" y="322" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">15</text><text x="462" y="322" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">20</text><text x="549.5" y="322" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">25</text><text x="14" y="14" text-anchor="start" dominant-baseline="central" fill="var(--muted)" style="font-size:11px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">ramp</text><text x="14" y="322" text-anchor="start" dominant-baseline="central" fill="var(--muted)" style="font-size:11px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">position</text><text x="14" y="58" text-anchor="start" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">one sledder</text><text x="14" y="73" text-anchor="start" dominant-baseline="central" fill="var(--muted)" style="font-size:11.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">best: 18</text><line x1="112" y1="80" x2="619.5" y2="80" stroke="currentColor" stroke-width="1.0" stroke-linecap="round" opacity="0.7"/><path d="M140.0,80.0 L149.0,80.0 L149.0,73.0 z" fill="var(--accent)" stroke="var(--accent)" stroke-width="1" opacity="1"/><path d="M175.0,80.0 L184.0,80.0 L184.0,73.0 z" fill="currentColor" stroke="currentColor" stroke-width="1" opacity="0.35"/><path d="M227.5,80.0 L236.5,80.0 L236.5,73.0 z" fill="var(--accent)" stroke="var(--accent)" stroke-width="1" opacity="1"/><path d="M315.0,80.0 L324.0,80.0 L324.0,73.0 z" fill="var(--accent)" stroke="var(--accent)" stroke-width="1" opacity="1"/><path d="M367.5,80.0 L376.5,80.0 L376.5,73.0 z" fill="currentColor" stroke="currentColor" stroke-width="1" opacity="0.75"/><path d="M437.5,80.0 L446.5,80.0 L446.5,73.0 z" fill="var(--accent)" stroke="var(--accent)" stroke-width="1" opacity="1"/><path d="M507.5,80.0 L516.5,80.0 L516.5,73.0 z" fill="currentColor" stroke="currentColor" stroke-width="1" opacity="0.35"/><path d="M149.0,73.0 Q174.2,37.4 199.5,79.0" fill="none" stroke="var(--accent)" stroke-width="2.0" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="174.2" y="49.2" text-anchor="middle" dominant-baseline="central" fill="var(--accent)" style="font-size:11.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">3</text><path d="M236.5,73.0 Q270.5,32.2 304.5,79.0" fill="none" stroke="var(--accent)" stroke-width="2.0" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="270.5" y="46.6" text-anchor="middle" dominant-baseline="central" fill="var(--accent)" style="font-size:11.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">4</text><path d="M324.0,73.0 Q340.5,42.6 357.0,79.0" fill="none" stroke="var(--accent)" stroke-width="2.0" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="340.5" y="51.8" text-anchor="middle" dominant-baseline="central" fill="var(--accent)" style="font-size:11.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">2</text><path d="M446.5,73.0 Q524.2,6.2 602.0,79.0" fill="none" stroke="var(--accent)" stroke-width="2.0" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="524.2" y="33.6" text-anchor="middle" dominant-baseline="central" fill="var(--accent)" style="font-size:11.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">9</text><text x="14" y="132" text-anchor="start" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">jump whenever</text><text x="14" y="147" text-anchor="start" dominant-baseline="central" fill="var(--muted)" style="font-size:11.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">you can: 16</text><line x1="112" y1="154" x2="619.5" y2="154" stroke="currentColor" stroke-width="1.0" stroke-linecap="round" opacity="0.7"/><path d="M140.0,154.0 L149.0,154.0 L149.0,147.0 z" fill="var(--muted)" stroke="var(--muted)" stroke-width="1" opacity="1"/><path d="M175.0,154.0 L184.0,154.0 L184.0,147.0 z" fill="currentColor" stroke="currentColor" stroke-width="1" opacity="0.35"/><path d="M227.5,154.0 L236.5,154.0 L236.5,147.0 z" fill="var(--muted)" stroke="var(--muted)" stroke-width="1" opacity="1"/><path d="M315.0,154.0 L324.0,154.0 L324.0,147.0 z" fill="var(--muted)" stroke="var(--muted)" stroke-width="1" opacity="1"/><path d="M367.5,154.0 L376.5,154.0 L376.5,147.0 z" fill="var(--muted)" stroke="var(--muted)" stroke-width="1" opacity="1"/><path d="M437.5,154.0 L446.5,154.0 L446.5,147.0 z" fill="currentColor" stroke="currentColor" stroke-width="1" opacity="0.35"/><path d="M507.5,154.0 L516.5,154.0 L516.5,147.0 z" fill="var(--muted)" stroke="var(--muted)" stroke-width="1" opacity="1"/><path d="M149.0,147.0 Q174.2,111.4 199.5,153.0" fill="none" stroke="var(--muted)" stroke-width="2.0" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="174.2" y="123.2" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:11.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">3</text><path d="M236.5,147.0 Q270.5,106.2 304.5,153.0" fill="none" stroke="var(--muted)" stroke-width="2.0" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="270.5" y="120.6" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:11.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">4</text><path d="M324.0,147.0 Q340.5,116.6 357.0,153.0" fill="none" stroke="var(--muted)" stroke-width="2.0" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="340.5" y="125.8" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:11.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">2</text><path d="M376.5,147.0 Q428.0,95.8 479.5,153.0" fill="none" stroke="var(--muted)" stroke-width="2.0" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="428" y="115.4" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:11.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">6</text><path d="M516.5,147.0 Q524.2,121.8 532.0,153.0" fill="none" stroke="var(--muted)" stroke-width="2.0" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="524.2" y="128.4" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:11.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">1</text><line x1="14" y1="176" x2="626" y2="176" stroke="var(--muted)" stroke-width="0.8" stroke-linecap="round" opacity="0.7"/><text x="14" y="206" text-anchor="start" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">Amy</text><text x="14" y="221" text-anchor="start" dominant-baseline="central" fill="var(--muted)" style="font-size:11.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">(k = 2)</text><line x1="112" y1="228" x2="619.5" y2="228" stroke="currentColor" stroke-width="1.0" stroke-linecap="round" opacity="0.7"/><path d="M140.0,228.0 L149.0,228.0 L149.0,221.0 z" fill="currentColor" stroke="currentColor" stroke-width="1" opacity="0.75"/><path d="M175.0,228.0 L184.0,228.0 L184.0,221.0 z" fill="var(--accent)" stroke="var(--accent)" stroke-width="1" opacity="1"/><path d="M227.5,228.0 L236.5,228.0 L236.5,221.0 z" fill="currentColor" stroke="currentColor" stroke-width="1" opacity="0.35"/><path d="M315.0,228.0 L324.0,228.0 L324.0,221.0 z" fill="currentColor" stroke="currentColor" stroke-width="1" opacity="0.75"/><path d="M367.5,228.0 L376.5,228.0 L376.5,221.0 z" fill="var(--accent)" stroke="var(--accent)" stroke-width="1" opacity="1"/><path d="M437.5,228.0 L446.5,228.0 L446.5,221.0 z" fill="currentColor" stroke="currentColor" stroke-width="1" opacity="0.35"/><path d="M507.5,228.0 L516.5,228.0 L516.5,221.0 z" fill="currentColor" stroke="currentColor" stroke-width="1" opacity="0.75"/><path d="M184.0,221.0 Q226.8,175.0 269.5,227.0" fill="none" stroke="var(--accent)" stroke-width="2.0" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="226.8" y="192" text-anchor="middle" dominant-baseline="central" fill="var(--accent)" style="font-size:11.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">5</text><path d="M376.5,221.0 Q428.0,169.8 479.5,227.0" fill="none" stroke="var(--accent)" stroke-width="2.0" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="428" y="189.4" text-anchor="middle" dominant-baseline="central" fill="var(--accent)" style="font-size:11.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">6</text><text x="14" y="280" text-anchor="start" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">Banjin</text><text x="14" y="295" text-anchor="start" dominant-baseline="central" fill="var(--muted)" style="font-size:11.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">(k = 2)</text><line x1="112" y1="302" x2="619.5" y2="302" stroke="currentColor" stroke-width="1.0" stroke-linecap="round" opacity="0.7"/><path d="M140.0,302.0 L149.0,302.0 L149.0,295.0 z" fill="currentColor" stroke="currentColor" stroke-width="1" opacity="0.75"/><path d="M175.0,302.0 L184.0,302.0 L184.0,295.0 z" fill="currentColor" stroke="currentColor" stroke-width="1" opacity="0.75"/><path d="M227.5,302.0 L236.5,302.0 L236.5,295.0 z" fill="var(--accent2)" stroke="var(--accent2)" stroke-width="1" opacity="1"/><path d="M315.0,302.0 L324.0,302.0 L324.0,295.0 z" fill="currentColor" stroke="currentColor" stroke-width="1" opacity="0.75"/><path d="M367.5,302.0 L376.5,302.0 L376.5,295.0 z" fill="currentColor" stroke="currentColor" stroke-width="1" opacity="0.75"/><path d="M437.5,302.0 L446.5,302.0 L446.5,295.0 z" fill="var(--accent2)" stroke="var(--accent2)" stroke-width="1" opacity="1"/><path d="M507.5,302.0 L516.5,302.0 L516.5,295.0 z" fill="currentColor" stroke="currentColor" stroke-width="1" opacity="0.35"/><path d="M236.5,295.0 Q270.5,254.2 304.5,301.0" fill="none" stroke="var(--accent2)" stroke-width="2.0" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="270.5" y="268.6" text-anchor="middle" dominant-baseline="central" fill="var(--accent2)" style="font-size:11.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">4</text><path d="M446.5,295.0 Q524.2,228.2 602.0,301.0" fill="none" stroke="var(--accent2)" stroke-width="2.0" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ARR)"/><text x="524.2" y="255.6" text-anchor="middle" dominant-baseline="central" fill="var(--accent2)" style="font-size:11.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">9</text></svg><figcaption><strong>The example: ramps at 2, 4, 7, 12, 15, 19, 23 with jump lengths 3, 5, 4, 2, 6, 9, 1.</strong> Faded ramps are flown over. Top: the best single run (ramps 1, 3, 4, 6; 18 in the air). Jumping at every ramp you reach gets only 16, because the jump at ramp 5 flies over the long jump at ramp 6. Bottom: two sledders with at most two jumps each and no shared ramp (Amy 2 and 5, Banjin 3 and 6; 24 in total). Alone, each could get 14 with ramps 2 and 6, but ramp 6 can be used only once.</figcaption></figure>

> [!hint]- Hint
> Suppose you are on the ground at ramp $i$. Jump or don't — either way, where are you next on the ground, and does anything about the past still matter?

> [!solution]- Solution
> **The idea.** Follow one sledder down the hill and make the decisions one ramp at a time. Standing on the ground at ramp $i$, there are two choices. Sled past it: then you are on the ground at ramp $i+1$. Jump: you land at $\mathit{Ramp}[i] + \mathit{Length}[i]$, every ramp up to that point is gone, and you are on the ground at the first ramp beyond the landing point. Either way you end up **on the ground at some later ramp, with nothing else to remember** — how you got there does not restrict what you can do next. So the subproblems are the suffixes "start on the ground at ramp $i$", and the recurrence tries both choices.
>
> Greed does not work here ([[2-algorithms/03-dynamic-programming#35-warning-greed-is-stupid|§3.5]]). On the example, jumping at every ramp you reach (ramps 1, 3, 4, 5, 7) gets 16, because the jump at ramp 5 flies over the long jump at ramp 6; taking the longest jumps first (ramps 6, 2, 4) also gets 16; the answer is 18 (ramps 1, 3, 4, 6). In fact this is the **weighted** version of class scheduling ([[2-algorithms/04-greedy-algorithms#42-scheduling-classes|§4.2]]): each jump is the interval $[\mathit{Ramp}[i],\ \mathit{Ramp}[i] + \mathit{Length}[i]]$, a set of jumps is possible exactly when its intervals are pairwise disjoint, and we maximize total length instead of the number of intervals. The greedy rule of [[concepts/interval-scheduling|interval scheduling]] (earliest landing first) maximizes the *number* of jumps — on the example it takes the same five jumps for 16.
>
> **Helper.** Add a sentinel $\mathit{Ramp}[n+1] = \infty$ (the bottom of the hill). For $1\le i\le n$ let
> $$
> \textsf{Next}(i) = \min\{\, j \mid \mathit{Ramp}[j] > \mathit{Ramp}[i] + \mathit{Length}[i] \,\},
> $$
> the first ramp past the landing point of a jump from ramp $i$. The handout does not say what happens when a jump ends exactly at a ramp; like the official solution, we count that ramp as flown over. Because $\mathit{Ramp}$ is sorted, binary search finds $\textsf{Next}(i)$ in $O(\log n)$ time, and $\textsf{Next}(i) > i$.
>
> **Function.** For $1\le i\le n+1$, let $\textsf{MaxAir}(i)$ be the **maximum total air distance of a sledder who reaches ramp $i$ on the ground and may use only ramps $i, \dots, n$** (0 when $i = n+1$). We need $\textsf{MaxAir}(1)$.
>
> **Recurrence.**
> $$
> \textsf{MaxAir}(i) = \begin{cases} 0 & \text{if } i > n\\ \max\big\{\textsf{MaxAir}(i+1),\ \ \mathit{Length}[i] + \textsf{MaxAir}(\textsf{Next}(i))\big\} & \text{otherwise}\end{cases}
> $$
> The first option sleds past ramp $i$; the second jumps, gains $\mathit{Length}[i]$, and lands before ramp $\textsf{Next}(i)$, which it then reaches on the ground. Every run from ramp $i$ does one of the two, so the maximum of the two optimal continuations is the optimum.
>
> - **Memoization:** a one-dimensional array $\mathit{MaxAir}[1\,..\,n+1]$.
> - **Evaluation order:** every entry reads only entries with a larger index, so fill $i$ from $n+1$ **down** to 1.
> - **Time:** $n$ binary searches, $O(n\log n)$, plus $n+1$ entries in $O(1)$ each: $O(n\log n)$ in total.
>
> ```text
> MaxAir(Ramp[1 .. n], Length[1 .. n]):
>     Ramp[n + 1] ← ∞                  ⟨⟨sentinel⟩⟩
>     MaxAir[n + 1] ← 0
>     for i ← n down to 1
>         next ← smallest j with Ramp[j] > Ramp[i] + Length[i]    ⟨⟨binary search⟩⟩
>         MaxAir[i] ← max{MaxAir[i + 1], Length[i] + MaxAir[next]}
>     return MaxAir[1]
> ```
>
> **On the example.** $\textsf{Next} = 3, 4, 4, 5, 7, 8, 8$ for $i = 1, \dots, 7$, and the table is
>
> | $i$ | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
> |---|---|---|---|---|---|---|---|---|
> | $\textsf{MaxAir}(i)$ | **18** | 16 | 15 | 11 | 9 | 9 | 1 | 0 |
>
> For instance $\textsf{MaxAir}(1) = \max\{\textsf{MaxAir}(2),\ 3 + \textsf{MaxAir}(3)\} = \max\{16, 18\} = 18$.
>
> **Answer.** $\textsf{MaxAir}(1)$, from an array filled right to left with $\textsf{MaxAir}(i) = \max\{\textsf{MaxAir}(i+1),\ \mathit{Length}[i] + \textsf{MaxAir}(\textsf{Next}(i))\}$, in $O(n\log n)$ time.

> [!trap] Where this loses points
> - **A description in terms of "the current position" or "where we last landed".** The parameter is the ramp $i$, and the description must say the sledder *reaches it on the ground* — that is what makes the value depend only on $i$.
> - **Recursing on $i+1$ after a jump.** The ramps under the jump are not available; the jump option must continue at $\textsf{Next}(i)$.
> - **A greedy rule** (jump whenever possible, longest first, earliest landing first) without proof: wrong here, and an unproved shortcut costs $1\tfrac12$ points even when it happens to be right.

## Problem 2 — At most k jumps

> [!question] Problem 2
> The university lawyers impose an upper bound on the number of jumps. Describe and analyze an algorithm that computes the maximum total distance a sledder can spend in the air **with at most $k$ jumps**, given $\mathit{Ramp}[1\,..\,n]$, $\mathit{Length}[1\,..\,n]$ and the integer $k$.

> [!hint]- Hint
> Same suffixes as in Problem 1. What else does a sledder standing at ramp $i$ need to know to decide whether she may jump?

> [!solution]- Solution
> **The idea.** Standing on the ground at ramp $i$, the past now matters in exactly one way: how many jumps are left. Make that a parameter. Jumping uses one; sledding past uses none; with no jumps left, nothing more can be gained.
>
> **Function.** With $\textsf{Next}$ as in Problem 1, for $1\le i\le n+1$ and $0\le\ell\le k$ let $\textsf{MaxAirK}(i, \ell)$ be the **maximum total air distance of a sledder who reaches ramp $i$ on the ground, may use only ramps $i, \dots, n$, and makes at most $\ell$ more jumps**. We need $\textsf{MaxAirK}(1, k)$.
>
> **Recurrence.** $\textsf{MaxAirK}(i, \ell) = 0$ if $i > n$ or $\ell = 0$; otherwise
> $$
> \textsf{MaxAirK}(i, \ell) = \max\big\{\textsf{MaxAirK}(i+1, \ell),\ \ \mathit{Length}[i] + \textsf{MaxAirK}(\textsf{Next}(i), \ell-1)\big\}.
> $$
>
> - **Memoization:** a two-dimensional array $\mathit{MaxAirK}[1\,..\,n+1,\ 0\,..\,k]$.
> - **Evaluation order:** entry $(i, \ell)$ reads entries with a larger first index, so the outer loop runs $i$ from $n+1$ **down** to 1, and the inner loop runs over $\ell$ in any order (say $0$ up to $k$).
> - **Time:** $n$ binary searches for $\textsf{Next}$ (once per $i$, outside the inner loop), plus $(n+1)(k+1)$ entries in $O(1)$ each: $O(n\log n + nk)$.
>
> ```text
> MaxAirK(Ramp[1 .. n], Length[1 .. n], k):
>     Ramp[n + 1] ← ∞
>     for ℓ ← 0 to k
>         MaxAirK[n + 1, ℓ] ← 0
>     for i ← n down to 1
>         next ← smallest j with Ramp[j] > Ramp[i] + Length[i]    ⟨⟨binary search⟩⟩
>         MaxAirK[i, 0] ← 0
>         for ℓ ← 1 to k
>             MaxAirK[i, ℓ] ← max{MaxAirK[i+1, ℓ], Length[i] + MaxAirK[next, ℓ−1]}
>     return MaxAirK[1, k]
> ```
>
> **On the example.** With $k = 2$:
>
> | $i$ | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
> |---|---|---|---|---|---|---|---|---|
> | $\textsf{MaxAirK}(i, 1)$ | 9 | 9 | 9 | 9 | 9 | 9 | 1 | 0 |
> | $\textsf{MaxAirK}(i, 2)$ | **14** | 14 | 13 | 11 | 9 | 9 | 1 | 0 |
>
> The best two jumps are ramps 2 and 6 ($5 + 9$). For $k = 1, 2, 3$ the answers are 9, 14, 16, and for every $k\ge 4$ the limit no longer binds and the answer is Problem 1's 18. In general, $k\ge n$ gives Problem 1.
>
> **Answer.** $\textsf{MaxAirK}(1, k)$, from an $(n+1)\times(k+1)$ array filled with $i$ decreasing, in $O(n\log n + nk)$ time.

## Problem 3 (harder) — Two sledders, each ramp used once

> [!question] Problem 3 (harder)
> The lawyers add one more rule: **no ramp may be used more than once**. Amy and Banjin cooperate to put on a good show. Describe and analyze an algorithm that computes the maximum total distance that Amy and Banjin together can spend in the air, **each taking at most $k$ jumps** (so at most $2k$ in total), with each ramp used at most once. The input is $\mathit{Ramp}[1\,..\,n]$, $\mathit{Length}[1\,..\,n]$ and $k$.

> [!hint]- Hint
> Run both sledders down the hill together. For each of them, remember the next ramp she will reach on the ground. Which ramp needs a decision next, and when can the two sledders get in each other's way?

> [!solution]- Solution
> **The idea.** By Problem 1's observation, everything about a single sledder's past is summed up by the **next ramp she reaches on the ground**, plus (as in Problem 2) her **jumps left**. With two sledders, keep both: Amy will next be on the ground at ramp $i$, Banjin at ramp $j$, with $a$ and $b$ jumps left. The ramps behind both of them are never touched again, so we never need to remember *which* ramps were used.
>
> Now look at the first ramp at which anybody can still decide something, ramp $\min(i, j)$:
>
> - **$i = j$: both are on the ground at ramp $i$.** This is the only place the one-use rule bites: at most one of them jumps. Three options — nobody jumps (both reach ramp $i+1$ on the ground), Amy jumps (she next touches ground at $\textsf{Next}(i)$, Banjin at $i+1$), or Banjin jumps.
> - **$i < j$: only Amy can use ramp $i$** (Banjin is in the air above it, or has already passed it). Amy sleds past or jumps; Banjin's state does not change.
> - **$i > j$:** the mirror image, Banjin decides at ramp $j$.
>
> When the sledders are at different ramps, they cannot conflict: a ramp $r$ with $i \le r < j$ is unusable for Banjin, so Amy is free to take it.
>
> **Function.** For $1\le i, j\le n+1$ and $0\le a, b\le k$, let $\textsf{MaxAirTwo}(i, j, a, b)$ be the **maximum total air distance of Amy and Banjin together, given that Amy reaches ramp $i$ on the ground and may use only ramps $i, \dots, n$ with at most $a$ more jumps, and Banjin reaches ramp $j$ on the ground and may use only ramps $j, \dots, n$ with at most $b$ more jumps, and no ramp is used by both.** (Distance flown before ramps $i$ and $j$ is not counted.) We need $\textsf{MaxAirTwo}(1, 1, k, k)$.
>
> **Recurrence.** With $\textsf{Next}$ and the sentinel as in Problem 1: $\textsf{MaxAirTwo}(i, j, a, b) = 0$ if $i > n$ and $j > n$ (nobody has a ramp left). Otherwise there are the three cases above. If $i = j \le n$ — nobody jumps, Amy jumps (needs $a\ge 1$), or Banjin jumps (needs $b\ge 1$):
> $$
> \textsf{MaxAirTwo}(i, i, a, b) = \max\left\{\begin{array}{l}
> \textsf{MaxAirTwo}(i+1, i+1, a, b)\\
> \mathit{Length}[i] + \textsf{MaxAirTwo}(\textsf{Next}(i), i+1, a-1, b)\\
> \mathit{Length}[i] + \textsf{MaxAirTwo}(i+1, \textsf{Next}(i), a, b-1)
> \end{array}\right\}
> $$
> If $i < j$ — Amy sleds past ramp $i$, or jumps (needs $a\ge 1$):
> $$
> \textsf{MaxAirTwo}(i, j, a, b) = \max\left\{\begin{array}{l}
> \textsf{MaxAirTwo}(i+1, j, a, b)\\
> \mathit{Length}[i] + \textsf{MaxAirTwo}(\textsf{Next}(i), j, a-1, b)
> \end{array}\right\}
> $$
> If $i > j$ — Banjin sleds past ramp $j$, or jumps (needs $b\ge 1$):
> $$
> \textsf{MaxAirTwo}(i, j, a, b) = \max\left\{\begin{array}{l}
> \textsf{MaxAirTwo}(i, j+1, a, b)\\
> \mathit{Length}[j] + \textsf{MaxAirTwo}(i, \textsf{Next}(j), a, b-1)
> \end{array}\right\}
> $$
> An option that needs a jump is left out when that sledder has none left. (The official solution instead lets $a$ and $b$ go down to $-1$ and sets $\textsf{MaxAirTwo} = -\infty$ there; same thing.) In the case $i < j$ we have $i\le n$, and in the case $i > j$ we have $j\le n$, so every $\mathit{Length}$ and $\textsf{Next}$ used exists.
>
> - **Memoization:** a four-dimensional array $\mathit{Air}[1\,..\,n+1,\ 1\,..\,n+1,\ 0\,..\,k,\ 0\,..\,k]$ holding the values of $\textsf{MaxAirTwo}$ — **all** pairs $(i, j)$, including $i > j$: Amy jumping from ramp $i = j$ immediately creates the state $(\textsf{Next}(i), i+1)$ with Amy ahead.
> - **Evaluation order:** an entry with $i \le j$ reads only entries with a larger first index; an entry with $i > j$ reads entries with the same first index $i$ and a larger second index. So the outer loop runs $i$ from $n+1$ **down** to 1, the next loop runs $j$ from $n+1$ **down** to 1 (all of them), and the two inner loops run over $a$ and $b$ in any order. Precompute $\textsf{Next}(1), \dots, \textsf{Next}(n)$ first.
> - **Time:** $(n+1)^2(k+1)^2$ entries, $O(1)$ each, plus $O(n\log n)$ for $\textsf{Next}$: $O(n^2k^2)$. (If $k > n$, replace $k$ by $n$ first: nobody makes more than $n$ jumps.)
>
> ```text
> MaxAirTwo(Ramp[1 .. n], Length[1 .. n], k):
>     Ramp[n + 1] ← ∞
>     for i ← 1 to n
>         Next[i] ← smallest j with Ramp[j] > Ramp[i] + Length[i]   ⟨⟨binary search⟩⟩
>     for i ← n + 1 down to 1
>         for j ← n + 1 down to 1               ⟨⟨all j, not only j ≥ i⟩⟩
>             for a ← 0 to k
>                 for b ← 0 to k
>                     Air[i, j, a, b] ← Best(i, j, a, b)
>     return Air[1, 1, k, k]
>
> Best(i, j, a, b):                     ⟨⟨reads only entries already filled⟩⟩
>     if i = n + 1 and j = n + 1
>         return 0
>     if i = j                            ⟨⟨both on the ground at ramp i⟩⟩
>         best ← Air[i + 1, i + 1, a, b]
>         if a ≥ 1
>             best ← max{best, Length[i] + Air[Next[i], i + 1, a − 1, b]}
>         if b ≥ 1
>             best ← max{best, Length[i] + Air[i + 1, Next[i], a, b − 1]}
>     else if i < j                       ⟨⟨Amy decides at ramp i⟩⟩
>         best ← Air[i + 1, j, a, b]
>         if a ≥ 1
>             best ← max{best, Length[i] + Air[Next[i], j, a − 1, b]}
>     else                                ⟨⟨Banjin decides at ramp j⟩⟩
>         best ← Air[i, j + 1, a, b]
>         if b ≥ 1
>             best ← max{best, Length[j] + Air[i, Next[j], a, b − 1]}
>     return best
> ```
>
> **On the example** (figure above). With $k = 1$ the best is 15: Amy takes ramp 5 and Banjin ramp 6 ($6 + 9$) — ramps 5 and 6 cannot both be used by one sledder, since the jump from ramp 5 flies over ramp 6. With $k = 2$ the best is **24** (Amy 2 and 5, Banjin 3 and 6, or Amy 2 and 6, Banjin 3 and 5), less than twice Problem 2's 14, because both would like ramp 6. With $k = 3$ it is 29 (every ramp but ramp 7), and with $k = 4$ it is 30: Amy takes ramps 1, 3, 5, 7 and Banjin 2, 4, 6, so every ramp is used.
>
> **Answer.** $\textsf{MaxAirTwo}(1, 1, k, k)$, from a four-dimensional array filled with $i$ decreasing, then $j$ decreasing over all of $1..n+1$, in $O(n^2k^2)$ time.

> [!warning] Misprints in the official solution to Problem 3
> The idea and the recurrence are right, but don't copy three details. (1) The first option of each maximum is written with $\ell, m$ where $a, b$ are meant. (2) The pseudocode's second loop runs `for j ← n + 1 down to i`, so the entries with $i > j$ are never filled, although the recurrence reads them (Amy's jump from ramp $i = j$ leads to the state $(\textsf{Next}(i), i+1)$); $j$ must run over all of $1..n+1$, and the dependency claim "$j' > i$" should read "$j' > j$". (3) In the case $i > j$ the pseudocode adds $\mathit{Length}[i]$; it must be $\mathit{Length}[j]$, Banjin's ramp. (Problem 2's recurrence similarly writes $\textsf{MaxAir}$ for $\textsf{MaxAir2}$ in one place.)

> [!tip] What to take from Problem 3
> When two "agents" move through the same input, give each one its own position parameter and always advance the one that is behind; they only need to be coordinated when they are at the same place. The cost is one more dimension per agent — here $n$ for the position and $k$ for the jumps, hence $n^2k^2$.

### Sources for this page

Problem statements: CS/ECE 374 A Fall 2026 Lab 8a handout (October 14); solutions explained from the official Lab 8a solutions, with the three misprints in Problem 3 corrected as described; the example instance and the class-scheduling connection are ours. `tools/checks/labs_08.py` implements every recurrence exactly as stated, in the stated evaluation order (with a memo that fails if an entry is read before it is written), and compares it with brute force: every sequence of jump decisions for one sledder (with and without a jump limit, up to 10 ramps, with ties and duplicate positions), every assignment of ramps to Amy, Banjin or nobody for two sledders (up to 7 ramps, $k\le 3$), and every set of pairwise compatible intervals; it reproduces every number in the example, confirms that the official Problem 3 pseudocode reads unfilled entries and that $\mathit{Length}[i]$ gives wrong answers, and counts the $(n+1)^2(k+1)^2$ entries.
