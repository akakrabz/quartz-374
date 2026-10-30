---
title: "Chapter 4 exercises — Greedy Algorithms"
description: "Solutions to Exercises 4.1–4.6 and 4.8–4.10 of Erickson's Algorithms: nine greedy rules for class scheduling (three proved correct, six refuted), weighted scheduling by dynamic programming, smallest interval covers, stabbing points, interval coloring, the deepest Huffman trees and why Fibonacci frequencies are not the smallest, ternary Huffman codes, and implementing and stress-testing Gale–Shapley."
tags: [exercises, algorithms, greedy]
---

*Solved exercises for [[2-algorithms/04-greedy-algorithms|Chapter 4]] · book pp. 176–179 · statements paraphrased; see the book for the originals*

These are Exercises 4.1–4.10, the scheduling, interval, Huffman and stable-matching problems that open the chapter's exercises. Skipped: 4.7 (α-heavy frequency arrays), which is marked ♥ (particularly challenging); 4.11–4.25 lie beyond the first ten. As the book's caveat demands, every [[concepts/greedy-algorithms|greedy algorithm]] here comes with a proof — usually an exchange argument as in [[2-algorithms/04-greedy-algorithms#43-the-general-pattern|§4.3]] — and every wrong greedy rule with a counterexample that defeats it **however its ties are broken**; the one problem that needs a [[concepts/dynamic-programming|dynamic program]], 4.2(c), is written in the DP rubric's format. Intervals and classes are **closed**, as in [[2-algorithms/04-greedy-algorithms#42-scheduling-classes|§4.2]]: two of them conflict (overlap) when they share a point, even an endpoint. Two remarks on the book: the cover shaded in its figure for Exercise 4.3 is a cover but not a smallest one, and in the four-hospital example of §4.5 the second matching called stable is not (see Exercise 4.9). Write your own answer before opening a solution.

## Exercise 4.1 — Nine greedy rules for class scheduling

> [!question] Exercise 4.1 (book pp. 176–177)
> The [[concepts/interval-scheduling|class scheduling]] problem of §4.2 asks for a largest set of pairwise non-conflicting classes, and GreedySchedule repeatedly takes the class that finishes first. For each greedy rule below, either prove that it always produces an optimal schedule, or give a small input on which it does not. Ties are broken arbitrarily — in a way you do not control. (The book's hint: **three** of the rules are correct.)
>
> (a) Choose the class $x$ that ends last, discard the classes that conflict with $x$, and recurse.
>
> (b) Choose the class $x$ that starts first, discard the classes that conflict with $x$, and recurse.
>
> (c) Choose the class $x$ that starts last, discard the classes that conflict with $x$, and recurse.
>
> (d) Choose the class $x$ with the shortest duration, discard the classes that conflict with $x$, and recurse.
>
> (e) Choose a class $x$ that conflicts with the fewest other classes, discard the classes that conflict with $x$, and recurse.
>
> (f) If no two classes conflict, take them all. Otherwise discard the class with the longest duration and recurse.
>
> (g) If no two classes conflict, take them all. Otherwise discard a class that conflicts with the most other classes and recurse.
>
> (h) Let $x$ be the class with the earliest start time and $y$ the class with the second earliest start time. If $x$ and $y$ are disjoint, choose $x$ and recurse on the other classes. If $x$ completely contains $y$, discard $x$ and recurse. Otherwise discard $y$ and recurse.
>
> (i) If some class $x$ completely contains another class, discard $x$ and recurse. Otherwise choose the class $y$ that ends last, discard the classes that conflict with $y$, and recurse.

A class is written as its interval $[S, F]$. Since ties are out of your control, a counterexample must defeat the rule on **every** run; in each one below the rule's first move is forced and already rules out every optimal schedule. Conflict counts in (e) and (g) are taken among the classes still present.

### (a) Ends last and (b) starts first

> [!hint]- Hint
> One long class can end last and start first at the same time.

> [!solution]- Solution
> Take the classes $[0,5]$, $[1,2]$ and $[3,4]$. The class $[0,5]$ is the only one that ends last and also the only one that starts first, so both rules choose it — and it conflicts with the other two, so both rules end with one class. But $[1,2]$ and $[3,4]$ are disjoint: two classes.
>
> **Answer.** Both rules are wrong: on $[0,5], [1,2], [3,4]$ they take 1 class, the optimum is 2.

### (c) Starts last

> [!hint]- Hint
> Run time backwards.

> [!solution]- Solution
> **Correct.** Reflect the time axis: replace every class $[S, F]$ by $[-F, -S]$. Two classes are compatible before the reflection if and only if they are compatible after it ($S[i] > F[j]$ is the same as $-F[j] > -S[i]$), so the schedules of the two inputs correspond one to one, with the same sizes. A class that starts last becomes a class that finishes first, and the classes that conflict with it stay the classes that conflict with it. So rule (c) on the input makes exactly the choices that "choose a class that finishes first, discard its conflicts, recurse" makes on the reflected input — and that algorithm is optimal for every tie-breaking: Lemma 4.3 holds for *any* class that finishes first, and the induction of Theorem 4.4 then goes through unchanged.
>
> **Answer.** Correct: it is the earliest-finish greedy algorithm with time running backwards.

### (d) Shortest duration

> [!hint]- Hint
> A short class can straddle the gap between two longer classes that fit together.

> [!solution]- Solution
> Take $[0,4]$, $[5,9]$ and $[3,6]$. The shortest class is $[3,6]$ (duration 3; the others have 4), and it overlaps both others, so the rule ends with one class. But $[0,4]$ and $[5,9]$ are disjoint.
>
> **Answer.** Wrong: 1 class instead of 2.

### (e) Fewest conflicts

> [!hint]- Hint
> Put the class with the fewest conflicts in the middle, overlapping two classes of an optimal schedule of size 4. To make every other class conflict with more classes, stack three mutually overlapping classes over each of the two outer gaps.

> [!solution]- Solution
> Take eleven classes:
> - $[0,4]$, $[6,10]$, $[12,16]$, $[18,22]$: four disjoint classes, an optimal schedule;
> - $[9,13]$, which overlaps only $[6,10]$ and $[12,16]$;
> - $[2,7]$, $[3,7]$, $[3,8]$ over the first gap, each overlapping $[0,4]$, $[6,10]$ and the other two; and symmetrically $[14,19]$, $[15,19]$, $[15,20]$ over the last gap.
>
> The class $[9,13]$ has 2 conflicts, $[0,4]$ and $[18,22]$ have 3, and every other class has 4. So the rule must choose $[9,13]$, which discards $[6,10]$ and $[12,16]$. What remains are the groups $\{[0,4], [2,7], [3,7], [3,8]\}$ and $\{[14,19], [15,19], [15,20], [18,22]\}$, each pairwise conflicting, so the rule takes at most one more class from each: 3 classes in all.
>
> **Answer.** Wrong: on these eleven classes the rule takes 3, the optimum is 4.

### (f) Discard the longest

> [!hint]- Hint
> The longest class may conflict with nothing at all.

> [!solution]- Solution
> Take $[0,6]$, $[7,9]$ and $[8,10]$. The last two conflict, so the rule discards the longest class, $[0,6]$ (duration 6; the others have 2); then $[7,9]$ and $[8,10]$ still conflict, one of them is discarded, and one class is left. But $[0,6]$ and $[7,9]$ are disjoint.
>
> **Answer.** Wrong: 1 class instead of 2.

### (g) Discard the most conflicted

> [!hint]- Hint
> The class with the most conflicts can be the bridge of the only largest schedule. Hang a triangle of three mutually overlapping classes on each side of it.

> [!solution]- Solution
> Take seven classes: two triangles of pairwise overlapping classes, $\{[0,3], [2,7], [1,8]\}$ and $\{[12,19], [13,18], [17,20]\}$, and a bridge $[6,14]$ that overlaps $[2,7]$, $[1,8]$, $[12,19]$ and $[13,18]$ but neither $[0,3]$ nor $[17,20]$. The bridge has 4 conflicts, $[0,3]$ and $[17,20]$ have 2, and the other four classes have 3, so the rule first discards the bridge. After that, no class conflicts with a class of the other triangle, and the classes of a triangle all conflict with each other, so the rule keeps at most one class per triangle: 2 classes. But $[0,3]$, $[6,14]$, $[17,20]$ form a schedule of size 3.
>
> **Answer.** Wrong: 2 classes instead of 3.

### (h) The two earliest starts

> [!hint]- Hint
> Every class other than $x$ and $y$ starts no earlier than $y$. In each of the three cases, show that the rule's action keeps the size of a largest schedule unchanged.

> [!solution]- Solution
> **Correct.** Write $\textit{opt}(X)$ for the size of a largest schedule within a set $X$ of classes. Each step of the rule removes one class, so by induction on $\lvert X\rvert$ it suffices to show that each step preserves the optimum (with a single class, the rule takes it). Every class $z$ other than $x$ and $y$ has $S[z]\ge S[y]\ge S[x]$.
> - **$x$ and $y$ are disjoint.** Then $F[x] < S[y]\le S[z]$ for every other class $z$, so $x$ conflicts with no class at all, and $\textit{opt}(X) = 1 + \textit{opt}(X\setminus\{x\})$: choosing $x$ and recursing on the rest loses nothing.
> - **$x$ contains $y$.** In a largest schedule that contains $x$, replace $x$ by $y$: every class disjoint from $x$ is disjoint from $y\subseteq x$ (and $y$ itself was not in the schedule, since it overlaps $x$). So $\textit{opt}(X\setminus\{x\}) = \textit{opt}(X)$.
> - **Otherwise** $x$ and $y$ overlap and $x$ does not contain $y$; as $S[x]\le S[y]$, this means $F[x] < F[y]$. Let $K$ be a largest schedule that contains $y$ (if there is none, discarding $y$ costs nothing). Then $x\notin K$, and every other class $z\in K$ starts at or after $S[y]$ and is disjoint from $y$, so $S[z] > F[y] > F[x]$. Hence $K\setminus\{y\}\cup\{x\}$ is a schedule of the same size without $y$, and $\textit{opt}(X\setminus\{y\}) = \textit{opt}(X)$.
>
> The argument never used *which* classes were picked as $x$ and $y$ among classes with equal start times, so every tie-breaking is fine.
>
> **Answer.** Correct.

### (i) Discard containers, then the latest finish

> [!hint]- Hint
> When no class contains another, sorting by start time and sorting by finish time give the same order.

> [!solution]- Solution
> **Correct**, by induction on the number of classes, with $\textit{opt}$ as in (h).
> - **Discarding a class $x$ that contains another class $y$** keeps the optimum: in a largest schedule that contains $x$, replace $x$ by $y$, as in the second case of (h).
> - **No class contains another.** Let $y$ be a class that ends last. Every other class $z$ has $F[z]\le F[y]$; if also $S[z]\ge S[y]$, then $y$ would contain $z$. So $S[z] < S[y]$: $y$ is also the class that starts last. Some largest schedule contains $y$: if a largest schedule $K$ does not, let $g$ be the class of $K$ that starts last; every other class of $K$ ends before $g$ starts, hence before $y$ starts, so $K\setminus\{g\}\cup\{y\}$ is a schedule of the same size (the mirror image of Lemma 4.3). A largest schedule containing $y$ consists of $y$ and a largest schedule of the classes compatible with $y$ — which is what the recursion computes, by induction.
>
> **Answer.** Correct.

The counterexamples for the six wrong rules, side by side:

<!-- fig:a04x-ex1 -->
<figure class="cs-fig"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 258" width="640" height="258" role="img" style="font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-size:13px"><title>five small sets of intervals, each with an optimal schedule and the first move of a wrong greedy rule</title><defs><marker id="ARR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs><text x="10" y="13" text-anchor="start" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">(a) ends last, (b) starts first</text><text x="310" y="13" text-anchor="end" dominant-baseline="central" fill="var(--muted)" style="font-size:11.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">rule 1 · optimum 2</text><rect x="71.2" y="26" width="59.2" height="16" rx="3" fill="var(--accent)" fill-opacity="0.25" stroke="var(--accent)" stroke-width="1.6"/><text x="100.8" y="34.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">[1,2]</text><rect x="189.6" y="26" width="59.2" height="16" rx="3" fill="var(--accent)" fill-opacity="0.25" stroke="var(--accent)" stroke-width="1.6"/><text x="219.2" y="34.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">[3,4]</text><rect x="12" y="48" width="296" height="16" rx="3" fill="var(--hi)" fill-opacity="0.2" stroke="var(--hi)" stroke-width="1.8"/><text x="160" y="56.5" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">[0,5]</text><line x1="12" y1="71" x2="308" y2="71" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="12" y1="71" x2="12" y2="74" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="71.2" y1="71" x2="71.2" y2="74" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="130.4" y1="71" x2="130.4" y2="74" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="189.6" y1="71" x2="189.6" y2="74" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="248.8" y1="71" x2="248.8" y2="74" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="308" y1="71" x2="308" y2="74" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><text x="10" y="99" text-anchor="start" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">(d) shortest duration</text><text x="310" y="99" text-anchor="end" dominant-baseline="central" fill="var(--muted)" style="font-size:11.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">rule 1 · optimum 2</text><rect x="12" y="112" width="131.6" height="16" rx="3" fill="var(--accent)" fill-opacity="0.25" stroke="var(--accent)" stroke-width="1.6"/><text x="77.8" y="120.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">[0,4]</text><rect x="176.4" y="112" width="131.6" height="16" rx="3" fill="var(--accent)" fill-opacity="0.25" stroke="var(--accent)" stroke-width="1.6"/><text x="242.2" y="120.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">[5,9]</text><rect x="110.7" y="134" width="98.7" height="16" rx="3" fill="var(--hi)" fill-opacity="0.2" stroke="var(--hi)" stroke-width="1.8"/><text x="160" y="142.5" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">[3,6]</text><line x1="12" y1="157" x2="308" y2="157" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="12" y1="157" x2="12" y2="160" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="44.9" y1="157" x2="44.9" y2="160" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="77.8" y1="157" x2="77.8" y2="160" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="110.7" y1="157" x2="110.7" y2="160" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="143.6" y1="157" x2="143.6" y2="160" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="176.4" y1="157" x2="176.4" y2="160" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="209.3" y1="157" x2="209.3" y2="160" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="242.2" y1="157" x2="242.2" y2="160" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="275.1" y1="157" x2="275.1" y2="160" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="308" y1="157" x2="308" y2="160" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><text x="10" y="185" text-anchor="start" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">(f) discard the longest</text><text x="310" y="185" text-anchor="end" dominant-baseline="central" fill="var(--muted)" style="font-size:11.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">rule 1 · optimum 2</text><rect x="12" y="198" width="177.6" height="16" rx="3" fill="none" stroke="var(--hi)" stroke-width="1.6" stroke-dasharray="4 3"/><text x="100.8" y="206.5" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">[0,6]</text><rect x="219.2" y="198" width="59.2" height="16" rx="3" fill="var(--accent)" fill-opacity="0.25" stroke="var(--accent)" stroke-width="1.6"/><text x="248.8" y="206.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">[7,9]</text><rect x="248.8" y="220" width="59.2" height="16" rx="3" fill="none" stroke="currentColor" stroke-width="1.1"/><text x="278.4" y="228.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">[8,10]</text><line x1="12" y1="243" x2="308" y2="243" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="12" y1="243" x2="12" y2="246" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="41.6" y1="243" x2="41.6" y2="246" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="71.2" y1="243" x2="71.2" y2="246" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="100.8" y1="243" x2="100.8" y2="246" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="130.4" y1="243" x2="130.4" y2="246" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="160" y1="243" x2="160" y2="246" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="189.6" y1="243" x2="189.6" y2="246" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="219.2" y1="243" x2="219.2" y2="246" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="248.8" y1="243" x2="248.8" y2="246" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="278.4" y1="243" x2="278.4" y2="246" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="308" y1="243" x2="308" y2="246" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><text x="330" y="13" text-anchor="start" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">(e) fewest conflicts</text><text x="630" y="13" text-anchor="end" dominant-baseline="central" fill="var(--muted)" style="font-size:11.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">rule 3 · optimum 4</text><rect x="332" y="26" width="53.8" height="16" rx="3" fill="var(--accent)" fill-opacity="0.25" stroke="var(--accent)" stroke-width="1.6"/><text x="358.9" y="34.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">[0,4]</text><rect x="412.7" y="26" width="53.8" height="16" rx="3" fill="var(--accent)" fill-opacity="0.25" stroke="var(--accent)" stroke-width="1.6"/><text x="439.6" y="34.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">[6,10]</text><rect x="493.5" y="26" width="53.8" height="16" rx="3" fill="var(--accent)" fill-opacity="0.25" stroke="var(--accent)" stroke-width="1.6"/><text x="520.4" y="34.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">[12,16]</text><rect x="574.2" y="26" width="53.8" height="16" rx="3" fill="var(--accent)" fill-opacity="0.25" stroke="var(--accent)" stroke-width="1.6"/><text x="601.1" y="34.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">[18,22]</text><rect x="358.9" y="48" width="67.3" height="16" rx="3" fill="none" stroke="currentColor" stroke-width="1.1"/><text x="392.5" y="56.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">[2,7]</text><rect x="453.1" y="48" width="53.8" height="16" rx="3" fill="var(--hi)" fill-opacity="0.2" stroke="var(--hi)" stroke-width="1.8"/><text x="480" y="56.5" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">[9,13]</text><rect x="520.4" y="48" width="67.3" height="16" rx="3" fill="none" stroke="currentColor" stroke-width="1.1"/><text x="554" y="56.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">[14,19]</text><rect x="372.4" y="70" width="53.8" height="16" rx="3" fill="none" stroke="currentColor" stroke-width="1.1"/><text x="399.3" y="78.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">[3,7]</text><rect x="533.8" y="70" width="53.8" height="16" rx="3" fill="none" stroke="currentColor" stroke-width="1.1"/><text x="560.7" y="78.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">[15,19]</text><rect x="372.4" y="92" width="67.3" height="16" rx="3" fill="none" stroke="currentColor" stroke-width="1.1"/><text x="406" y="100.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">[3,8]</text><rect x="533.8" y="92" width="67.3" height="16" rx="3" fill="none" stroke="currentColor" stroke-width="1.1"/><text x="567.5" y="100.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">[15,20]</text><line x1="332" y1="115" x2="628" y2="115" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="332" y1="115" x2="332" y2="118" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="345.5" y1="115" x2="345.5" y2="118" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="358.9" y1="115" x2="358.9" y2="118" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="372.4" y1="115" x2="372.4" y2="118" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="385.8" y1="115" x2="385.8" y2="118" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="399.3" y1="115" x2="399.3" y2="118" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="412.7" y1="115" x2="412.7" y2="118" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="426.2" y1="115" x2="426.2" y2="118" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="439.6" y1="115" x2="439.6" y2="118" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="453.1" y1="115" x2="453.1" y2="118" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="466.5" y1="115" x2="466.5" y2="118" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="480" y1="115" x2="480" y2="118" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="493.5" y1="115" x2="493.5" y2="118" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="506.9" y1="115" x2="506.9" y2="118" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="520.4" y1="115" x2="520.4" y2="118" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="533.8" y1="115" x2="533.8" y2="118" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="547.3" y1="115" x2="547.3" y2="118" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="560.7" y1="115" x2="560.7" y2="118" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="574.2" y1="115" x2="574.2" y2="118" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="587.6" y1="115" x2="587.6" y2="118" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="601.1" y1="115" x2="601.1" y2="118" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="614.5" y1="115" x2="614.5" y2="118" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="628" y1="115" x2="628" y2="118" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><text x="330" y="143" text-anchor="start" dominant-baseline="central" fill="currentColor" style="font-size:13px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">(g) discard most conflicts</text><text x="630" y="143" text-anchor="end" dominant-baseline="central" fill="var(--muted)" style="font-size:11.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">rule 2 · optimum 3</text><rect x="332" y="156" width="44.4" height="16" rx="3" fill="var(--accent)" fill-opacity="0.25" stroke="var(--accent)" stroke-width="1.6"/><text x="354.2" y="164.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">[0,3]</text><rect x="420.8" y="156" width="118.4" height="16" rx="3" fill="none" stroke="var(--hi)" stroke-width="1.6" stroke-dasharray="4 3"/><text x="480" y="164.5" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">[6,14]</text><rect x="583.6" y="156" width="44.4" height="16" rx="3" fill="var(--accent)" fill-opacity="0.25" stroke="var(--accent)" stroke-width="1.6"/><text x="605.8" y="164.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">[17,20]</text><rect x="361.6" y="178" width="74" height="16" rx="3" fill="none" stroke="currentColor" stroke-width="1.1"/><text x="398.6" y="186.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">[2,7]</text><rect x="509.6" y="178" width="103.6" height="16" rx="3" fill="none" stroke="currentColor" stroke-width="1.1"/><text x="561.4" y="186.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">[12,19]</text><rect x="346.8" y="200" width="103.6" height="16" rx="3" fill="none" stroke="currentColor" stroke-width="1.1"/><text x="398.6" y="208.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">[1,8]</text><rect x="524.4" y="200" width="74" height="16" rx="3" fill="none" stroke="currentColor" stroke-width="1.1"/><text x="561.4" y="208.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:10.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">[13,18]</text><line x1="332" y1="223" x2="628" y2="223" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="332" y1="223" x2="332" y2="226" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="346.8" y1="223" x2="346.8" y2="226" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="361.6" y1="223" x2="361.6" y2="226" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="376.4" y1="223" x2="376.4" y2="226" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="391.2" y1="223" x2="391.2" y2="226" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="406" y1="223" x2="406" y2="226" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="420.8" y1="223" x2="420.8" y2="226" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="435.6" y1="223" x2="435.6" y2="226" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="450.4" y1="223" x2="450.4" y2="226" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="465.2" y1="223" x2="465.2" y2="226" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="480" y1="223" x2="480" y2="226" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="494.8" y1="223" x2="494.8" y2="226" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="509.6" y1="223" x2="509.6" y2="226" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="524.4" y1="223" x2="524.4" y2="226" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="539.2" y1="223" x2="539.2" y2="226" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="554" y1="223" x2="554" y2="226" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="568.8" y1="223" x2="568.8" y2="226" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="583.6" y1="223" x2="583.6" y2="226" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="598.4" y1="223" x2="598.4" y2="226" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="613.2" y1="223" x2="613.2" y2="226" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/><line x1="628" y1="223" x2="628" y2="226" stroke="var(--muted)" stroke-width="0.9" stroke-linecap="round"/></svg><figcaption><strong>Counterexamples for Exercise 4.1.</strong> Classes are closed intervals [start, finish]; the top row of each panel (filled) is a largest schedule. Red marks the rule's first move: the class it <em>chooses</em> in (a), (b), (d), (e), or the class it <em>discards</em> (dashed) in (f), (g). After that move every run of the rule, however ties are broken, ends with fewer classes than the optimum.</figcaption></figure>

## Exercise 4.2 — Weighted class scheduling

> [!question] Exercise 4.2 (book pp. 177–178)
> Now every class also earns a number of credit hours, unrelated to its duration, and the goal is a conflict-free set of classes with the largest total credit. The input is the arrays of start times, finish times and credits.
>
> (a) Prove that the greedy algorithm of §4.2 — choose the class that ends first and recurse — does not always find an optimal schedule.
>
> (b) Prove that **none** of the greedy rules of Exercise 4.1 always finds an optimal schedule. (The book's hint: the rules that fail there fail here too.)
>
> (c) Describe and analyze an algorithm that always finds an optimal schedule. (The book's hint: it is not greedy.)

### (a) and (b) Every greedy rule fails

> [!hint]- Hint
> A long class worth many credits that contains a short class worth few.

> [!solution]- Solution
> Take two classes: $[0,3]$ worth 2 credits and $[1,2]$ worth 1 credit. They overlap, so the optimum is 2 credits.
> - **(a)** $[1,2]$ ends first; the greedy algorithm takes it and discards $[0,3]$: 1 credit.
> - **(b)** The three rules that are correct in Exercise 4.1 also end with $[1,2]$: it starts last, so (c) takes it; it is the second earliest start $y$ and lies inside $x = [0,3]$, so (h) discards $x$; and $[0,3]$ contains another class, so (i) discards it. Each earns 1 credit. The other six rules, (a), (b), (d), (e), (f) and (g), already fail with **one credit per class** — then the credit of a schedule is its size — on the counterexamples of Exercise 4.1.
>
> **Answer.** $[0,3]$ (2 credits) with $[1,2]$ (1 credit) defeats earliest finish and rules (c), (h), (i); Exercise 4.1's counterexamples with unit credits defeat the other six.

### (c) Dynamic programming

> [!hint]- Hint
> Sort the classes by finish time. The last class is in the schedule or not; if it is, every other class of the schedule finishes before it starts, and those classes form a prefix of the sorted order.

> [!solution]- Solution
> Sort the classes so that $F[1]\le F[2]\le\cdots\le F[n]$, permuting $S$ and the credits $C$ to match. For $1\le j\le n$ let $\textsf{Prev}(j)$ be the number of classes $i$ with $F[i] < S[j]$. Because $F$ is sorted, these are exactly the classes $1, \ldots, \textsf{Prev}(j)$, and $\textsf{Prev}(j) < j$ because $F[j] > S[j]$.
>
> **Function.** For $0\le j\le n$, let $\textsf{MaxCredit}(j)$ be the largest total credit of a conflict-free subset of the classes $1, \ldots, j$ (the prefix of the sorted order). We need $\textsf{MaxCredit}(n)$.
>
> **Recurrence.**
> $$
> \textsf{MaxCredit}(j) = \begin{cases} 0 & \text{if } j = 0\\ \max\big\{\textsf{MaxCredit}(j-1),\ C[j] + \textsf{MaxCredit}(\textsf{Prev}(j))\big\} & \text{if } j\ge 1\end{cases}
> $$
> A best subset of the classes $1, \ldots, j$ either avoids class $j$ — then it is a subset of $1, \ldots, j-1$ — or contains it. In the second case every other class $i$ of the subset has $i < j$, so $F[i]\le F[j]$, and is compatible with $j$; since $S[i] < F[i]\le F[j]$, compatibility means $F[i] < S[j]$, that is, $i\le\textsf{Prev}(j)$. Conversely, class $j$ together with any conflict-free subset of $1, \ldots, \textsf{Prev}(j)$ is conflict-free.
>
> - **Memoization:** an array $\mathit{MaxCredit}[0\,..\,n]$, and an array $\mathit{Prev}[1\,..\,n]$ computed beforehand by binary search for $S[j]$ in the sorted array $F$.
> - **Evaluation order:** $j$ from $0$ up to $n$.
> - **Time:** $O(n\log n)$ for sorting and the $n$ binary searches, then $O(1)$ per entry: $O(n\log n)$ in all.
>
> Recording which term wins at each $j$ recovers the schedule itself.
>
> **Answer.** $\textsf{MaxCredit}(n)$, in $O(n\log n)$ time.

## Exercise 4.3 — Smallest cover

> [!question] Exercise 4.3 (book p. 178)
> Let $X$ be a set of $n$ intervals on the real line, given by arrays $L[1\,..\,n]$ and $R[1\,..\,n]$ of left and right endpoints. A subset $Y\subseteq X$ **covers** $X$ if the union of the intervals in $Y$ equals the union of all intervals in $X$; the size of a cover is its number of intervals. Describe and analyze an efficient algorithm that computes a smallest cover of $X$; if it is greedy, prove it correct. (The book's figure shows 16 intervals and a shaded cover of size 7.)

> [!hint]- Hint
> Sweep from left to right. An interval that covers the leftmost point not yet covered must start at or before that point. Among all such intervals, which one would you rather have?

> [!solution]- Solution
> **Algorithm.** Sort the intervals by left endpoint and sweep. The variable $\mathit{reach}$ is the right end of the part covered so far. When the next interval sticks out to the right of $\mathit{reach}$, take — among all intervals that start at or before $t = \max\{\mathit{reach}, L[i]\}$ — one that reaches farthest to the right. Inside a component of the union, $t = \mathit{reach}$; after a gap in the union, $t = L[i]$ is the first point of a new component.
>
> ```text
> SmallestCover(L[1 .. n], R[1 .. n]):
>     sort the intervals so that L[1] ≤ L[2] ≤ ··· ≤ L[n]
>     count ← 0;  reach ← −∞;  i ← 1
>     while i ≤ n
>         if R[i] ≤ reach                       ⟨⟨interval i is already covered⟩⟩
>             i ← i + 1
>         else
>             t ← max{reach, L[i]}              ⟨⟨extend the cover from t⟩⟩
>             best ← R[i]
>             while i ≤ n and L[i] ≤ t          ⟨⟨scan the candidates⟩⟩
>                 best ← max{best, R[i]};  i ← i + 1
>             count ← count + 1;  reach ← best  ⟨⟨take a candidate reaching farthest⟩⟩
>     return count
> ```
>
> To output the cover itself, remember an interval that attains $\mathit{best}$. Intervals before position $i$ all end at or before $\mathit{reach}$, so they are never better candidates than the ones scanned.
>
> **Running time.** The sort takes $O(n\log n)$ time; after it, every iteration of either loop increases $i$, so the sweep takes $O(n)$: $O(n\log n)$ in all.
>
> **Components.** The union $U$ of $X$ splits into maximal intervals, its components. Every interval of $X$ lies inside one component, so $Y$ covers $X$ if and only if, for every component, the intervals of $Y$ inside it cover it: the components can be treated separately. Fix a component $[a, b]$. The algorithm's picks inside it are intervals $g_1, \ldots, g_k$ with right ends $r_1 < r_2 < \cdots < r_k = b$: $g_1$ reaches farthest among the intervals that start at $a$, and $g_j$, for $j\ge 2$, farthest among those that start at or before $r_{j-1}$. Each pick makes progress while $r_{j-1} < b$: if every interval meeting $(r_{j-1}, b]$ started after $r_{j-1}$, the points between $r_{j-1}$ and the smallest of their left endpoints would lie in $[a, b]$ but not in $U$.
>
> **Greedy stays ahead.** *Claim:* if some $j$ intervals of $X$ cover $[a, t]$, where $a\le t\le b$, then $r_j\ge t$ (set $r_j = b$ for $j > k$). Induction on $j$. Let $q = [L_q, R_q]$ be one of the $j$ intervals that contains $t$.
> - If $L_q\le a$, then $L_q = a$ (no interval inside the component starts before $a$), so $q$ was a candidate for the first pick, and $r_j\ge r_1\ge R_q\ge t$.
> - Otherwise the points of $[a, L_q)$ are covered by the other $j-1$ intervals (so $j\ge 2$), and since a finite union of closed intervals is closed, those $j-1$ intervals cover $[a, L_q]$. By induction $r_{j-1}\ge L_q$. If $j\le k$, then $q$ starts at or before $r_{j-1}$, so it was a candidate for the $j$th pick, and $r_j\ge R_q\ge t$; if $j > k$, then $r_j = b\ge t$ anyway.
>
> A cover of $X$ contains some number $m$ of intervals inside $[a, b]$ that cover it, so $r_m\ge b$ by the claim, and therefore $k\le m$. Adding over the components, no cover is smaller than the algorithm's.
>
> **The book's example.** The 16 intervals of the book's figure have a single interval as their union, and the algorithm covers it with **6** of them (figure below). So the shaded cover of size 7 in the book is a cover, but not a smallest one.
>
> **Answer.** SmallestCover returns the size of a smallest cover, in $O(n\log n)$ time.

<!-- fig:a04x-cover -->
<figure class="cs-fig"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 174" width="640" height="174" role="img" style="font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-size:13px"><title>sixteen intervals in five rows; six of them, numbered 1 to 6, form a cover of the union</title><defs><marker id="ARR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs><rect x="14" y="8" width="147.5" height="18" rx="3" fill="var(--accent)" fill-opacity="0.25" stroke="var(--accent)" stroke-width="1.6"/><text x="87.7" y="17.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">1</text><rect x="240.7" y="8" width="136" height="18" rx="3" fill="none" stroke="currentColor" stroke-width="1.1"/><rect x="388.2" y="8" width="147.2" height="18" rx="3" fill="none" stroke="currentColor" stroke-width="1.1"/><rect x="558" y="8" width="39.9" height="18" rx="3" fill="none" stroke="currentColor" stroke-width="1.1"/><rect x="36.7" y="34" width="101.8" height="18" rx="3" fill="none" stroke="currentColor" stroke-width="1.1"/><rect x="183.8" y="34" width="136" height="18" rx="3" fill="none" stroke="currentColor" stroke-width="1.1"/><rect x="427.4" y="34" width="119.1" height="18" rx="3" fill="none" stroke="currentColor" stroke-width="1.1"/><rect x="87.7" y="60" width="249" height="18" rx="3" fill="var(--accent)" fill-opacity="0.25" stroke="var(--accent)" stroke-width="1.6"/><text x="212.3" y="69.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">2</text><rect x="354" y="60" width="136" height="18" rx="3" fill="var(--accent)" fill-opacity="0.25" stroke="var(--accent)" stroke-width="1.6"/><text x="422" y="69.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">4</text><rect x="569.5" y="60" width="56.5" height="18" rx="3" fill="var(--accent)" fill-opacity="0.25" stroke="var(--accent)" stroke-width="1.6"/><text x="597.7" y="69.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">6</text><rect x="64.8" y="86" width="90.7" height="18" rx="3" fill="none" stroke="currentColor" stroke-width="1.1"/><rect x="269.1" y="86" width="113" height="18" rx="3" fill="var(--accent)" fill-opacity="0.25" stroke="var(--accent)" stroke-width="1.6"/><text x="325.6" y="95.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">3</text><rect x="450.4" y="86" width="136" height="18" rx="3" fill="none" stroke="currentColor" stroke-width="1.1"/><rect x="53.9" y="112" width="181.3" height="18" rx="3" fill="none" stroke="currentColor" stroke-width="1.1"/><rect x="257.6" y="112" width="45.3" height="18" rx="3" fill="none" stroke="currentColor" stroke-width="1.1"/><rect x="405.1" y="112" width="203.7" height="18" rx="3" fill="var(--accent)" fill-opacity="0.25" stroke="var(--accent)" stroke-width="1.6"/><text x="506.9" y="121.5" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">5</text><line x1="14" y1="142" x2="626" y2="142" stroke="var(--accent)" stroke-width="2.2" stroke-linecap="round"/><text x="14" y="156" text-anchor="start" dominant-baseline="central" fill="var(--muted)" style="font-size:11.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">union: one interval</text><line x1="161.5" y1="139" x2="161.5" y2="145" stroke="var(--accent)" stroke-width="1.4" stroke-linecap="round"/><line x1="336.8" y1="139" x2="336.8" y2="145" stroke="var(--accent)" stroke-width="1.4" stroke-linecap="round"/><line x1="382.1" y1="139" x2="382.1" y2="145" stroke="var(--accent)" stroke-width="1.4" stroke-linecap="round"/><line x1="490" y1="139" x2="490" y2="145" stroke="var(--accent)" stroke-width="1.4" stroke-linecap="round"/><line x1="608.8" y1="139" x2="608.8" y2="145" stroke="var(--accent)" stroke-width="1.4" stroke-linecap="round"/><line x1="626" y1="139" x2="626" y2="145" stroke="var(--accent)" stroke-width="1.4" stroke-linecap="round"/></svg><figcaption><strong>SmallestCover on the book's example (Exercise 4.3).</strong> The 16 intervals of the book's figure, in the same rows. Sweeping left to right, the algorithm takes the filled intervals in the order numbered: each one starts inside the part already covered and reaches farthest to the right (ticks on the axis). Six intervals suffice; the cover shaded in the book has seven, so it is not a smallest one.</figcaption></figure>

## Exercise 4.4 — Stabbing intervals

> [!question] Exercise 4.4 (book p. 178)
> A set $P$ of points **stabs** a set $X$ of intervals if every interval of $X$ contains at least one point of $P$. Given $L[1\,..\,n]$ and $R[1\,..\,n]$, describe and analyze an efficient algorithm to compute a smallest set of points that stabs $X$; if it is greedy, prove it correct. (The book's figure stabs 16 intervals with four points.)

> [!hint]- Hint
> Some point has to lie in the interval that ends first. How far to the right can you move that point without losing anything?

> [!solution]- Solution
> **Algorithm.** Scan the intervals by right endpoint; whenever an interval is not stabbed yet, put a point at its right end.
>
> ```text
> StabIntervals(L[1 .. n], R[1 .. n]):
>     sort the intervals so that R[1] ≤ R[2] ≤ ··· ≤ R[n]
>     count ← 0;  p ← −∞
>     for i ← 1 to n
>         if L[i] > p                  ⟨⟨interval i is not stabbed yet⟩⟩
>             count ← count + 1
>             p ← R[i];  P[count] ← p
>     return P[1 .. count]
> ```
>
> The single test $L[i] > p$ suffices: every point placed so far is at most $p$, and $p$ is the right end of an earlier interval in the sorted order, so $p\le R[i]$. Interval $i$ is stabbed if and only if it contains $p$, that is, $L[i]\le p$.
>
> **Exchange.** Let $I = [L_1, R_1]$ be an interval with the smallest right endpoint. *Some smallest stabbing set contains $R_1$:* a smallest stabbing set $P$ has a point $p\in I$, so $p\le R_1$; every interval $J = [L_J, R_J]$ that contains $p$ satisfies $L_J\le p\le R_1\le R_J$, so it contains $R_1$ as well. Hence $P\setminus\{p\}\cup\{R_1\}$ also stabs $X$, with the same size.
>
> **Induction.** Since every right endpoint is at least $R_1$, the intervals that contain $R_1$ are exactly those with $L\le R_1$; let $X'$ be the others. A smallest stabbing set $P\ni R_1$ of $X$ gives the stabbing set $P\setminus\{R_1\}$ of $X'$, and conversely $R_1$ together with a stabbing set of $X'$ stabs $X$; so the minimum for $X$ is 1 plus the minimum for $X'$. The algorithm places its first point at $R_1$, skips exactly the intervals with $L\le R_1$, and then treats $X'$ as it would on its own — by induction, with the minimum number of points.
>
> **Running time.** $O(n\log n)$ for the sort, then $O(n)$.
>
> **A certificate.** The intervals that receive a point are pairwise disjoint: each one starts after the previous point, which is the right end of the previous such interval. A stabbing set needs a separate point for each of them — so the smallest number of stabbing points equals the largest number of pairwise disjoint intervals. (The intervals that receive points are exactly the classes GreedySchedule takes in §4.2.) In the book's example the algorithm also uses four points, at the right ends of four pairwise disjoint intervals (figure below), so the book's four points are optimal.
>
> **Answer.** StabIntervals, in $O(n\log n)$ time.

<!-- fig:a04x-stab -->
<figure class="cs-fig"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 178" width="640" height="178" role="img" style="font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-size:13px"><title>sixteen intervals in five rows, four vertical lines through them at the greedy points</title><defs><marker id="ARR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs><line x1="138.5" y1="2" x2="138.5" y2="140" stroke="var(--hi)" stroke-width="2.2" stroke-linecap="round"/><text x="138.5" y="154" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">p1</text><line x1="302.9" y1="2" x2="302.9" y2="140" stroke="var(--hi)" stroke-width="2.2" stroke-linecap="round"/><text x="302.9" y="154" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">p2</text><line x1="490" y1="2" x2="490" y2="140" stroke="var(--hi)" stroke-width="2.2" stroke-linecap="round"/><text x="490" y="154" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">p3</text><line x1="597.9" y1="2" x2="597.9" y2="140" stroke="var(--hi)" stroke-width="2.2" stroke-linecap="round"/><text x="597.9" y="154" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">p4</text><rect x="14" y="8" width="147.5" height="18" rx="3" fill="none" stroke="currentColor" stroke-width="1.1"/><rect x="240.7" y="8" width="124.5" height="18" rx="3" fill="none" stroke="currentColor" stroke-width="1.1"/><rect x="388.2" y="8" width="147.2" height="18" rx="3" fill="none" stroke="currentColor" stroke-width="1.1"/><rect x="552.6" y="8" width="45.3" height="18" rx="3" fill="var(--accent)" fill-opacity="0.25" stroke="var(--accent)" stroke-width="1.6"/><rect x="36.7" y="34" width="101.8" height="18" rx="3" fill="var(--accent)" fill-opacity="0.25" stroke="var(--accent)" stroke-width="1.6"/><rect x="183.8" y="34" width="147.5" height="18" rx="3" fill="none" stroke="currentColor" stroke-width="1.1"/><rect x="427.4" y="34" width="113.6" height="18" rx="3" fill="none" stroke="currentColor" stroke-width="1.1"/><rect x="87.7" y="60" width="249" height="18" rx="3" fill="none" stroke="currentColor" stroke-width="1.1"/><rect x="365.2" y="60" width="124.8" height="18" rx="3" fill="var(--accent)" fill-opacity="0.25" stroke="var(--accent)" stroke-width="1.6"/><rect x="569.5" y="60" width="56.2" height="18" rx="3" fill="none" stroke="currentColor" stroke-width="1.1"/><rect x="64.8" y="86" width="90.7" height="18" rx="3" fill="none" stroke="currentColor" stroke-width="1.1"/><rect x="269.1" y="86" width="113" height="18" rx="3" fill="none" stroke="currentColor" stroke-width="1.1"/><rect x="450.4" y="86" width="136" height="18" rx="3" fill="none" stroke="currentColor" stroke-width="1.1"/><rect x="53.9" y="112" width="181.3" height="18" rx="3" fill="none" stroke="currentColor" stroke-width="1.1"/><rect x="257.6" y="112" width="45.3" height="18" rx="3" fill="var(--accent)" fill-opacity="0.25" stroke="var(--accent)" stroke-width="1.6"/><rect x="405.1" y="112" width="203.7" height="18" rx="3" fill="none" stroke="currentColor" stroke-width="1.1"/><text x="146.5" y="168" text-anchor="start" dominant-baseline="central" fill="var(--muted)" style="font-size:11.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">p1 lies in 5 intervals</text></svg><figcaption><strong>StabIntervals on the book's example (Exercise 4.4).</strong> Scanning by right endpoint, each point p<sub>k</sub> is the right end of the first interval not yet stabbed (filled). The four filled intervals are pairwise disjoint, so no three points can stab them all: four is optimal. The point p<sub>1</sub> lies in five intervals, so the book's five-color coloring in Exercise 4.5 is optimal too.</figcaption></figure>

## Exercise 4.5 — Coloring intervals

> [!question] Exercise 4.5 (book p. 178)
> A **proper coloring** of a set $X$ of intervals assigns a color to every interval so that any two overlapping intervals get different colors. Given $L[1\,..\,n]$ and $R[1\,..\,n]$, describe and analyze an efficient algorithm to compute the minimum number of colors in a proper coloring of $X$; if it is greedy, prove it correct. (The book's figure colors 16 intervals with five colors.)

> [!hint]- Hint
> Intervals that share a common point need different colors. Is that the only obstacle? Color the intervals in order of their left endpoints.

> [!solution]- Solution
> **The answer is the depth** of $X$: the largest number of intervals that contain a common point. Compute it by sweeping over the endpoints.
>
> ```text
> MinColors(L[1 .. n], R[1 .. n]):
>     sort the 2n endpoints by coordinate,
>         with left endpoints before right endpoints at equal coordinates
>     d ← 0;  best ← 0
>     for each endpoint, in sorted order
>         if it is a left endpoint
>             d ← d + 1;  best ← max{best, d}
>         else
>             d ← d − 1
>     return best
> ```
>
> After all left endpoints at a coordinate $x$ have been processed, $d$ is the number of intervals that contain $x$. A deepest point can be moved left to the largest left endpoint among the intervals containing it without leaving any of them, so $\mathit{best}$ is the depth. Processing left endpoints first at equal coordinates counts two intervals that share only an endpoint as overlapping, as closed intervals do. (For open intervals, process right endpoints first.)
>
> **At least depth-many colors.** If $d$ intervals contain a common point, they pairwise overlap, so they need $d$ different colors.
>
> **Depth-many colors suffice.** Color during the same sweep: at a left endpoint, give the interval any color that is currently free, or a new color if none is free; at a right endpoint, free the interval's color. Two overlapping intervals get different colors: when the later-starting one begins, the other has started and has not yet ended (its right endpoint is not smaller, and ties go to left endpoints), so its color is not free. A new color is created only when all existing colors are held by intervals that have started but not ended; all of them, and the new interval, contain the current left endpoint, so the number of colors never exceeds the depth.
>
> **Running time.** $O(n\log n)$ for the sort, $O(n)$ for the sweep (keep the free colors on a stack).
>
> **The book's example** has depth 5 — five intervals share the first stabbing point in the figure of Exercise 4.4 — so the book's coloring with five colors is optimal.
>
> **Answer.** The minimum number of colors is the depth of $X$, computed by MinColors in $O(n\log n)$ time.

## Exercise 4.6 — Deep Huffman trees

> [!question] Exercise 4.6 (book p. 179)
> (a) For every integer $n$, find a frequency array $f[1\,..\,n]$ whose [[concepts/huffman-codes|Huffman]] code tree has depth $n-1$, such that the largest frequency is as small as possible.
>
> (b) Suppose the total length $N = \sum_i f[i]$ of the unencoded message is bounded by a polynomial in the alphabet size $n$. Prove that every Huffman tree for $f[1\,..\,n]$ has depth $O(\log n)$.

### (a) The deepest trees with the smallest frequencies

> [!hint]- Hint
> Depth $n-1$ means that every merge after the first one combines the tree built so far with a single leaf. When is that tree guaranteed to be one of the two least frequent items — whatever the tie-breaking?

> [!solution]- Solution
> Frequencies are positive integers (how often each symbol occurs), and Huffman's algorithm breaks ties arbitrarily ([[2-algorithms/04-greedy-algorithms#44-huffman-codes|§4.4]]), so the tree should have depth $n-1$ for **every** tie-breaking.
>
> **The answer.** Let $L_0 = 2$, $L_1 = 1$ and $L_k = L_{k-1} + L_{k-2}$ be the Lucas numbers $2, 1, 3, 4, 7, 11, 18, 29, \ldots$. Take
> $$
> f = (1, 1, 1, 3, 4, 7, 11, 18, \ldots),\qquad f[1] = f[2] = 1,\quad f[j] = L_{j-2}\ \text{ for } j\ge 3.
> $$
> Its largest frequency is $L_{n-2}$ for $n\ge 3$ (and 1 for $n\le 2$).
>
> **When is the depth $n-1$?** A binary tree with $n$ leaves has depth $n-1$ exactly when it is a caterpillar, in which only the deepest internal node has two leaf children. Every merge of two leaves creates an internal node with two leaf children, so a Huffman tree has depth $n-1$ exactly when only its first merge combines two leaves and every later merge combines the one tree built so far with a leaf.
>
> Sort $f[1]\le\cdots\le f[n]$ and let $S_k = f[1] + \cdots + f[k]$. The first merge creates a tree of weight $S_2$. Suppose that before some later merge the items are a tree of weight $S_k$ and the leaves $f[k+1]\le\cdots\le f[n]$, for some $2\le k\le n-2$. If $S_k\ge f[k+2]$, then the leaves $f[k+1]$ and $f[k+2]$ are two least frequent items, and some tie-breaking merges them. If $S_k < f[k+2]$, every pair of least frequent items consists of the tree and a leaf of frequency $f[k+1]$, and the next state has the same form with $k+1$. So **every** Huffman tree has depth $n-1$ if and only if
> $$
> f[k+2] > S_k = f[1] + \cdots + f[k]\qquad\text{for all } 2\le k\le n-2. \tag{$\ast$}
> $$
>
> **Nothing smaller works.** Let $f$ satisfy $(\ast)$. We show $S_k\ge L_k - 1$ for $k\ge 2$ and $f[j]\ge L_{j-2}$ for $j\ge 3$. To start, $S_2\ge 2 = L_2 - 1$ and $f[3]\ge 1 = L_1$. If $S_k\ge L_k - 1$, then $f[k+2]\ge S_k + 1\ge L_k$ by $(\ast)$, and $S_{k+1} = S_k + f[k+1]\ge (L_k - 1) + L_{k-1} = L_{k+1} - 1$, using $f[k+1]\ge L_{k-1}$ from the previous step. In particular $f[n]\ge L_{n-2}$.
>
> **The bound is reached.** For the array above every inequality is an equality: $S_k = L_k - 1$ and $f[k+2] = L_k = S_k + 1 > S_k$, so $(\ast)$ holds (figure below for $n = 6$).
>
> **Two near misses.**
> - The **Fibonacci** frequencies $1, 1, 2, 3, 5, \ldots, F_n$ satisfy $(\ast)$ too, because $S_k = F_{k+2} - 1$; they are the classic example of a deepest Huffman tree. But their largest frequency is $F_n = F_{n-1} + F_{n-2}$, while $L_{n-2} = F_{n-1} + F_{n-3}$, which is smaller for $n\ge 5$ (for $n = 5$: 4 instead of 5).
> - If ties may be broken **in your favor**, $(\ast)$ relaxes to $f[k+2]\ge S_k$, and the same argument gives $(1, 1, 1, 2, 3, 5, 8, \ldots)$, that is, $f[j] = F_{j-1}$ for $j\ge 2$, with largest frequency $F_{n-1}$. For example, $(1, 1, 1, 2)$ has a Huffman tree of depth 3, but another tie-breaking gives depth 2.
>
> **Answer.** $f = (1, 1, 1, 3, 4, 7, 11, \ldots)$ with $f[j] = L_{j-2}$ for $j\ge 3$; the smallest possible largest frequency is the Lucas number $L_{n-2}$ for $n\ge 3$.

<!-- fig:a04x-huffman -->
<figure class="cs-fig"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 236" width="300" height="236" role="img" style="font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-size:14px"><title>a caterpillar binary tree with leaves 1,1,1,3,4,7 and internal weights 2,3,6,10,17</title><defs><marker id="ARR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs><line x1="203.9" y1="30.9" x2="180.2" y2="53.1" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" opacity="0.55"/><line x1="161.4" y1="71" x2="138.8" y2="93" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" opacity="0.55"/><line x1="120.5" y1="111.4" x2="100" y2="132.6" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" opacity="0.55"/><line x1="82.7" y1="152" x2="66.3" y2="172" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" opacity="0.55"/><line x1="51.7" y1="193.4" x2="40.3" y2="214.1" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" opacity="0.55"/><line x1="64.3" y1="193.4" x2="75.7" y2="214.1" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" opacity="0.55"/><line x1="99.3" y1="152" x2="118.3" y2="175.1" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" opacity="0.55"/><line x1="138.5" y1="111.4" x2="161.8" y2="135.5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" opacity="0.55"/><line x1="180.1" y1="71" x2="205.5" y2="95.7" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" opacity="0.55"/><line x1="222.9" y1="30.9" x2="249.4" y2="55.8" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" opacity="0.55"/><text x="36" y="222" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">1</text><text x="80" y="222" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">1</text><circle cx="58" cy="182" r="12" fill="var(--paper)" stroke="currentColor" stroke-width="1.2"/><text x="58" y="182" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">2</text><text x="124" y="182" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">1</text><circle cx="91" cy="142" r="12" fill="var(--paper)" stroke="currentColor" stroke-width="1.2"/><text x="91" y="142" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">3</text><text x="168" y="142" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">3</text><circle cx="129.5" cy="102" r="12" fill="var(--paper)" stroke="currentColor" stroke-width="1.2"/><text x="129.5" y="102" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">6</text><text x="212" y="102" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">4</text><circle cx="170.8" cy="62" r="12" fill="var(--paper)" stroke="currentColor" stroke-width="1.2"/><text x="170.8" y="62" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">10</text><text x="256" y="62" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">7</text><circle cx="213.4" cy="22" r="12" fill="var(--paper)" stroke="currentColor" stroke-width="1.2"/><text x="213.4" y="22" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;">17</text><text x="296" y="22" text-anchor="end" dominant-baseline="central" fill="var(--muted)" style="font-size:12px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">depth 5</text></svg><figcaption><strong>The deepest Huffman tree with the smallest frequencies, n = 6.</strong> Leaves 1, 1, 1, 3, 4, 7; each internal node shows its weight. Every subtree weighs less than the leaf two places further in sorted order (2 &lt; 3, 3 &lt; 4, 6 &lt; 7), so no tie-breaking lets Huffman merge two leaves instead, and every Huffman tree is this caterpillar of depth n &minus; 1 = 5.</figcaption></figure>

### (b) Polynomial length means logarithmic depth

> [!hint]- Hint
> Walk up from a deep leaf. Show that the weight of a node's grandparent is at least twice the node's own weight.

> [!solution]- Solution
> Every node of a Huffman tree has a **weight**: the total frequency of the leaves below it; the root weighs $N$, and every leaf at least 1.
>
> **Lemma.** If $v$ has a grandparent $g$, then $w(g)\ge 2\,w(v)$.
>
> *Proof.* Let $p$ be the parent of $v$, let $s$ be the sibling of $v$ and $t$ the sibling of $p$. When $v$ and $s$ were merged, they were two least frequent items, so every other item present then weighed at least $w(v)$; so did the new item $p$. Every item created afterwards is the sum of two items that weigh at least $w(v)$, so from that moment on every item weighs at least $w(v)$. The item $t$ was present when $p$ and $t$ were merged, which happened later, so $w(t)\ge w(v)$, and $w(g) = w(v) + w(s) + w(t)\ge 2\,w(v)$.
>
> **The bound.** Let a leaf have depth $d$. Going up from it, the weight at least doubles every two levels, so $N\ge 2^{\lfloor d/2\rfloor}$ and $d\le 2\log_2 N + 1$. If $N\le n^c$ for a constant $c$, then $d\le 2c\log_2 n + 1 = O(\log n)$.
>
> The Fibonacci frequencies of part (a) have depth $n-1$, and indeed their total $N = F_{n+2} - 1$ is exponential in $n$.
>
> **Answer.** Every Huffman tree has depth at most $2\log_2 N + 1$, which is $O(\log n)$ when $N$ is polynomial in $n$.

## Exercise 4.8 — Ternary Huffman codes

> [!question] Exercise 4.8 (book p. 179)
> Describe and analyze an algorithm that computes an optimal **ternary** prefix-free code for frequencies $f[1\,..\,n]$: codewords over the alphabet $\{\mathtt{0}, \mathtt{1}, \mathtt{2}\}$, minimizing $\sum_i f[i]\cdot\lvert\text{codeword of } i\rvert$. Prove that your algorithm is correct for **all** $n$.

> [!hint]- Hint
> Merging three least frequent symbols at a time works when every merge can take exactly three items. For which $n$ is that true? What can you add to the alphabet when it is not?

> [!solution]- Solution
> A ternary code is a tree in which every internal node has at most three children, and a symbol's codeword length is the depth of its leaf; the cost is $\sum_i f[i]\cdot\textsf{depth}(i)$. A tree is **full** if every internal node has exactly three children; a full tree with $m$ internal nodes has $2m+1$ leaves, an odd number.
>
> **Algorithm.** If $n$ is even, add a dummy symbol of frequency 0. Then merge three least frequent items until one item is left.
>
> ```text
> TernaryHuffman(f[1 .. n]):
>     m ← n
>     if n is even                                 ⟨⟨add a dummy symbol⟩⟩
>         m ← n + 1;  f[m] ← 0
>     insert the symbols 1, …, m into a priority queue keyed by frequency
>     for i ← m + 1 to m + (m − 1)/2               ⟨⟨(m − 1)/2 merges⟩⟩
>         x ← ExtractMin();  y ← ExtractMin();  z ← ExtractMin()
>         f[i] ← f[x] + f[y] + f[z];  make x, y, z the children of node i
>         insert i into the priority queue
>     delete the dummy leaf, if any; return the tree rooted at node m + (m − 1)/2
> ```
>
> The queue starts with an odd number $m$ of items and each merge removes three and inserts one, so a merge always finds three items. The dummy has frequency 0, so it is merged in the first round: for even $n$ the first merge effectively combines only the **two** least frequent symbols. For $n = 1$ there is no merge and the single codeword is empty.
>
> **Running time.** $O(n)$ priority-queue operations: $O(n\log n)$ time.
>
> **Correctness.** Let $f'$ be $f$ if $n$ is odd, and $f$ plus a symbol of frequency 0 if $n$ is even; $f'$ has an odd number $n'$ of symbols.
>
> 1. **Reduction to full trees: the cheapest code for $f$ costs as much as the cheapest full tree for $f'$.** Deleting the dummy leaf from a full tree for $f'$ leaves a code for $f$ of the same cost. Conversely, take an optimal code tree for $f$ and give every internal node with fewer than three children extra dummy leaves of frequency 0: a full tree of the same cost, with some number $D$ of dummies, where $n + D$ is odd. While $D\ge 2$, remove two dummies without increasing the cost: let $d_1$ be a deepest dummy, with parent $u$, and $d_2$ another dummy, a sibling of $d_1$ if possible. If $d_2$ is not a sibling of $d_1$, swap it with a sibling $x$ of $d_1$ ($d_2$ is not below $x$, because $d_1$ is a deepest dummy); the subtree of $x$ moves to the depth of $d_2$, which is at most the depth of $d_1$, so the cost does not increase. Now delete $d_1$ and $d_2$ and let the third child of $u$ take $u$'s place, moving its subtree up one level. The tree stays full and $D$ drops by 2. We end with $D = 1$ for even $n$ and $D = 0$ for odd $n$: a full tree for $f'$, no more expensive than the optimal code.
> 2. **Greedy choice: if $n'\ge 3$, some optimal full tree for $f'$ has three least frequent symbols $x, y, z$ as siblings.** In an optimal full tree let $v$ be an internal node of maximum depth; its three children are leaves at the maximum depth. Swap each of $x, y, z$ that is not yet a child of $v$ with a child of $v$ outside $\{x, y, z\}$. Each swap exchanges a leaf at some depth $\delta$ with a leaf at the maximum depth $\Delta\ge\delta$ whose frequency is at least as large (it is not among the three least frequent), and changes the cost by $(f[\text{small}] - f[\text{large}])(\Delta - \delta)\le 0$ — the argument of Lemma 4.5.
> 3. **Recursion.** Replacing the sibling leaves $x, y, z$ by one leaf of frequency $f[x] + f[y] + f[z]$ turns full trees for $f'$ in which $x, y, z$ are siblings into full trees for the smaller instance ($n'-2$ symbols, still an odd number), and back; the cost changes by exactly $f[x] + f[y] + f[z]$ either way. The algorithm merges $x, y, z$ and then, by induction on $n'$, builds an optimal full tree for the smaller instance; with step 2 its tree is optimal for $f'$, and with step 1 the code is optimal for $f$. The base case $n' = 1$ is a single leaf.
>
> **Trap.** "Always merge three; if two items are left at the end, merge two" is wrong. For $f = (1, 1, 1, 1)$ it merges three 1s and then the result with the last 1: codeword lengths $1, 2, 2, 2$, cost 7. The algorithm above merges two 1s first (with the dummy) and then everything: lengths $1, 1, 2, 2$, cost 6. The level that has room for an extra child must be the deepest one, not the root.
>
> **Answer.** Add a 0-frequency dummy if $n$ is even, then repeatedly merge the three least frequent items: an optimal ternary code in $O(n\log n)$ time.

## Exercise 4.9 — Implementing Gale–Shapley

> [!question] Exercise 4.9 (book p. 179)
> Describe in detail how to implement the Gale–Shapley [[concepts/stable-matching|stable matching]] algorithm so that its worst-case running time is $O(n^2)$, as claimed in [[2-algorithms/04-greedy-algorithms#45-stable-matching|§4.5]].

> [!hint]- Hint
> There are at most $n^2$ offers, so make each offer take $O(1)$ time. What does a hospital need to know to make its next offer, and what does a doctor need to know to compare two hospitals?

> [!solution]- Solution
> **Representation**, as the book suggests: doctors and hospitals are the integers $1, \ldots, n$; $\mathit{HPref}[A, r]$ is the $r$th doctor on hospital $A$'s list and $\mathit{DPref}[\alpha, r]$ the $r$th hospital on doctor $\alpha$'s list. Add four structures:
> - $\mathit{Rank}[\alpha, A]$, the position of hospital $A$ on doctor $\alpha$'s list — the inverse of $\mathit{DPref}$, so a doctor compares two hospitals in $O(1)$ time;
> - $\mathit{Next}[A]$, the position on $A$'s list of the next doctor $A$ will offer to;
> - $\mathit{Match}[\alpha]$, the hospital that doctor $\alpha$ currently holds, or 0;
> - a stack $\mathit{Free}$ of the unmatched hospitals (an array with a top index).
>
> ```text
> GaleShapley(HPref[1 .. n, 1 .. n], DPref[1 .. n, 1 .. n]):
>     for α ← 1 to n
>         for r ← 1 to n
>             Rank[α, DPref[α, r]] ← r
>         Match[α] ← 0
>     for A ← 1 to n
>         Next[A] ← 1;  Push(Free, A)
>     while Free is not empty
>         A ← Pop(Free)
>         α ← HPref[A, Next[A]];  Next[A] ← Next[A] + 1      ⟨⟨A offers to α⟩⟩
>         if Match[α] = 0
>             Match[α] ← A
>         else if Rank[α, A] < Rank[α, Match[α]]
>             Push(Free, Match[α]);  Match[α] ← A           ⟨⟨α drops her hospital⟩⟩
>         else
>             Push(Free, A)                                 ⟨⟨α rejects A⟩⟩
>     return Match[1 .. n]
> ```
>
> **It is the Gale–Shapley algorithm.** Two invariants hold before every iteration: $\mathit{Free}$ holds exactly the unmatched hospitals, and every doctor before position $\mathit{Next}[A]$ on $A$'s list has received an offer from $A$ and has rejected it (at once or by dropping $A$ later), except $A$'s current doctor if $A$ is matched. So a popped hospital $A$ is unmatched, and $\mathit{HPref}[A, \mathit{Next}[A]]$ is the best doctor who has not rejected $A$ — each iteration is one round of the algorithm. As shown in §4.5, an unmatched hospital has never been rejected by all $n$ doctors, so $\mathit{Next}[A]\le n$ whenever $A$ is popped.
>
> **Running time.** Building $\mathit{Rank}$ and the initialization take $O(n^2)$ time. Each iteration takes $O(1)$ time and makes one offer; $\mathit{Next}[A]$ only increases, so $A$ offers to each doctor at most once, and there are at most $n^2$ iterations. Total: $O(n^2)$, linear in the size of the two $n\times n$ input tables.
>
> On the book's four-hospital example the implementation makes 10 offers and returns $\{As, Bt, Cq, Dr\}$, the same matching as the book's run. It is in fact the only stable matching for those lists: the book also calls $\{Ar, Bs, Cq, Dt\}$ stable, but there Dr. Quincy (at County) and Bedlam (with Dr. Shephard) prefer each other.
>
> **Answer.** Rank table, next-offer pointers, current matches and a stack of free hospitals: $O(1)$ per offer, $O(n^2)$ in all.

## Exercise 4.10 — Gale–Shapley can take quadratic time

> [!question] Exercise 4.10 (book p. 179)
> (a) Prove that the Gale–Shapley algorithm can make $\Omega(n^2)$ offers before it halts: describe an input and a sequence of $\Omega(n^2)$ valid offers.
>
> (b) For every $n$, describe preferences for $n$ doctors and $n$ hospitals that force the algorithm to run $\Omega(n^2)$ rounds, **no matter which valid offer** is made in each round. (The book's hint: (b) implies (a).)

> [!hint]- Hint
> Let everyone agree: all hospitals rank the doctors in the same order, and all doctors rank the hospitals in the same order. Who ends up with whom, and how far down its list must each hospital go?

> [!solution]- Solution
> **The input.** Every hospital ranks the doctors $\alpha_1\succ\alpha_2\succ\cdots\succ\alpha_n$, and every doctor ranks the hospitals $A_1\succ A_2\succ\cdots\succ A_n$.
>
> **(b)** *The only stable matching pairs $A_k$ with $\alpha_k$ for every $k$.* $A_1$ and $\alpha_1$ rank each other first, so a matching that separates them has the unstable pair $(\alpha_1, A_1)$; with them matched, the same argument applies to $A_2$ and $\alpha_2$ among the rest, and so on. Every run of Gale–Shapley returns a stable matching, so it pairs $A_k$ with $\alpha_k$. A hospital offers down its list in order, and its final doctor is the last one it offered to (a hospital makes no offers while matched, and its last offer was never rejected). So in **every** run $A_k$ offers exactly to $\alpha_1, \ldots, \alpha_k$: $k$ offers. Every round makes one offer, so every run takes
> $$
> \sum_{k=1}^{n} k = \frac{n(n+1)}{2} = \Omega(n^2)
> $$
> rounds.
>
> **(a)** follows from (b): any run will do. An explicit one: let $A_1, A_2, \ldots, A_n$ take turns, each offering until it is accepted. $A_k$ offers to $\alpha_1, \ldots, \alpha_{k-1}$, who each hold a hospital they prefer and reject it, and then to $\alpha_k$, who is still unmatched and accepts. Nobody is ever dropped, and there are $n(n+1)/2$ offers.
>
> **Answer.** Identical preference lists on both sides force exactly $n(n+1)/2$ offers in every run.

### Sources for this page

Exercises 4.1–4.6 and 4.8–4.10 of Jeff Erickson, *Algorithms* (2019), pp. 176–179 (CC BY 4.0), paraphrased; the solutions are ours. All counterexamples, the Lucas-number answer to 4.6(a) and its comparison with the Fibonacci frequencies, and the pseudocode are original; the 16-interval examples of Exercises 4.3–4.5 are the book's figures, measured from the PDF. The book's shaded cover in Exercise 4.3 is not a smallest one (6 intervals suffice), and §4.5's claim that $\{Ar, Bs, Cq, Dt\}$ is stable is false. Every rule of Exercise 4.1 is simulated under every tie-breaking on all small inputs, and every algorithm, counterexample, number and book example on this page is checked against brute force by `tools/checks/a04x.py`.
