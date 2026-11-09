---
title: "Faster exponential algorithms"
description: "Exact algorithms for NP-hard problems that beat brute force: branching on clauses for 3SAT (1.8393ⁿ, then 1.7693ⁿ with pure literals), deterministic local search (√3ⁿ) and random restarts ((3/2)ⁿ); characteristic polynomials of backtracking recurrences; maximum independent set by case analysis on degrees (1.3803ⁿ); and the unfinished section on dynamic programming over subsets (3-coloring, Lawler's chromatic number). Errors in the note are corrected."
tags: [lecture-notes, algorithms, np-hardness, backtracking]
note: "B"
---

*Erickson, lecture notes · Extended Dance Remix B · 14 pp. · [PDF](https://jeffe.cs.illinois.edu/teaching/algorithms/notes/B-fastexpo.pdf) · CC BY-NC-SA 4.0 · status: unfinished · [[4-lecture-notes/index|all notes]]*

> [!abstract] In one breath
> NP-hard problems still have to be solved, and among exponential algorithms the base matters: for $n = 100$, $2^n\approx 1.3\times10^{30}$ but $1.25^n\approx 4.9\times10^{9}$. The tool is backtracking whose branches are chosen so that each one removes several variables or vertices. Such an algorithm's running time satisfies $T(n)\le \text{poly}(n) + \sum_i T(n-a_i)$, which solves to $O(\lambda^n\,\text{poly}(n))$ for $\lambda$ the largest root of a **characteristic polynomial**. For **3Sat**, branching on one clause gives $1.8393^n$, adding **pure-literal** elimination and a second clause $1.7693^n$, **local search** from the all-true and all-false assignments $\sqrt3^{\,n}\approx 1.7321^n$, and local search from random starts $(3/2)^n$ with failure probability at most $e^{-n}$. For **maximum independent set**, taking every vertex of degree at most 1, branching on vertices of degree at least 3 and solving unions of cycles directly gives $1.3803^n$. The last section, on **dynamic programming over subsets** (3-coloring in $O(2^n\,\text{poly}(n))$, Lawler's algorithms through maximal independent sets), is an unfinished draft.

> [!note] Where this fits
> The note asks you to read Chapters 2, 3 and 12 first. Its two problems are the first NP-hard problems of [[2-algorithms/12-np-hardness|Chapter 12]] — 3Sat ([[2-algorithms/12-np-hardness#126-3sat-from-circuitsat|§12.6]], [[concepts/satisfiability]]) and maximum independent set ([[2-algorithms/12-np-hardness#127-maximum-independent-set-from-3sat|§12.7]], [[concepts/independent-set]]) — and its algorithms are the recursive backtracking of [[2-algorithms/02-backtracking|Chapter 2]] with better branching, plus memoization over subsets ([[concepts/dynamic-programming]]). The recurrences are linear recurrences, solved by the characteristic-polynomial method of [[4-lecture-notes/99-solving-recurrences#5-linear-recurrences-annihilators|Appendix II, §5]] ([[concepts/linear-recurrences]]). **Not assigned in CS/ECE 374 this semester** (most of these notes are CS 473 material at Illinois); what this note adds to Chapter 12 is what to do *after* proving a problem NP-hard.

**Which exponential?** The obvious exact algorithm for an NP-hard problem generates every candidate solution — every assignment, coloring, subset or permutation — by recursive backtracking. Most NP-hard problems have structure that lets an algorithm prune most of that recursion tree: an algorithm in $O(1.5^n)$ or $O(1.25^n)$ time, while still unusable for huge inputs, handles instances far beyond an $O(2^n)$ one, and that in turn beats $O(4^n)$.

## B.1 3SAT

The input is a boolean formula in conjunctive normal form with at most three literals per clause, $n$ variables and $m$ clauses; the question is whether some assignment satisfies it. Trying all $2^n$ assignments, each checked in $O(m)$ time, takes $O(2^n m)$ time; after removing repeated clauses (easy in polynomial time) $m = O(n^3)$, so $O(2^n n^3)$. Polynomial factors are noise next to an exponential, so the note writes $\text{poly}(n) := n^{O(1)}$ for "some polynomial" and calls this $O(2^n\,\text{poly}(n))$.

### One clause

A 3CNF formula is either empty or (a clause) ∧ (a 3CNF formula). For a formula $\Psi$ and a literal $x$, write $\Psi|x$ for the formula obtained by setting $x$ to True and simplifying: clauses containing $x$ disappear and $\bar x$ is deleted from the others. $\Psi|x$ has at least one variable fewer, and $x\wedge\Psi = x\wedge(\Psi|x)$ (an induction on the formula). So for $\Phi = (x\vee y\vee z)\wedge\Phi'$,
$$
\Phi = \bigl(x\wedge(\Phi'|x)\bigr)\vee\bigl(y\wedge(\Phi'|y)\bigr)\vee\bigl(z\wedge(\Phi'|z)\bigr),
$$
and $\Phi$ is satisfiable exactly when one of the three smaller formulas is. Checking all three recursively gives $T(n)\le 3T(n-1) + \text{poly}(n) = O(3^n\,\text{poly}(n))$ — worse than brute force. But the cases are not exclusive: if $\Phi'|x$ is unsatisfiable, then $x$ is false in every satisfying assignment, so the second branch may also set $x$ false, and the third may set $x$ and $y$ false.

```text
3Sat(Φ):
  if Φ = ∅
      return True
  if Φ contains an empty clause          ⟨⟨missing in the note⟩⟩
      return False
  (x ∨ y ∨ z) ∧ Φ′ ← Φ
  if 3Sat(Φ′|x)
      return True
  if 3Sat(Φ′|x̄y)
      return True
  return 3Sat(Φ′|x̄ȳz)
```

The three branches fix one, two and three variables (a shorter clause gives fewer branches), so
$$
T(n) = T(n-1) + T(n-2) + T(n-3) + \text{poly}(n).
$$
Correctness: a satisfying assignment makes $x$ true, or $x$ false and $y$ true, or $x$, $y$ false and $z$ true, and the matching branch inherits it; every branch only restricts $\Phi$. (The note's pseudocode has no `return False` at all, so it can never report an unsatisfiable formula; the recursion reaches a formula with an empty clause — a clause whose literals have all been made false — and must return False there.)

<!-- fig:nb-3sat -->
<figure class="cs-fig"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 268" width="640" height="268" role="img" style="font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-size:14px"><title>two recursion trees: 3Sat with three children losing 1, 2, 3 variables; Faster3Sat with four children losing 2, 3, 2, 3</title><defs><marker id="ARR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs><text x="160" y="18" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">3Sat</text><text x="160" y="40" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">(x ∨ y ∨ z) ∧ Φ′</text><rect x="137" y="61" width="46" height="30" rx="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.4"/><text x="160" y="77" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">Φ</text><text x="190" y="76" text-anchor="start" dominant-baseline="central" fill="var(--muted)" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">n variables</text><line x1="160" y1="91" x2="58" y2="157" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/><rect x="29" y="157" width="58" height="30" rx="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.4"/><text x="58" y="173" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">Φ′|x</text><text x="58" y="202" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">≤ n − 1</text><line x1="160" y1="91" x2="160" y2="157" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/><rect x="125.5" y="157" width="69" height="30" rx="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.4"/><text x="160" y="173" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">Φ′|x̅y</text><text x="160" y="202" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">≤ n − 2</text><line x1="160" y1="91" x2="262" y2="157" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/><rect x="222" y="157" width="80" height="30" rx="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.4"/><text x="262" y="173" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">Φ′|x̅y̅z</text><text x="262" y="202" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">≤ n − 3</text><text x="160" y="236" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">T(n) = T(n−1) + T(n−2) + T(n−3)</text><text x="160" y="256" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">λ = 1.8393</text><text x="480" y="18" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">Faster3Sat (no pure literal)</text><text x="480" y="40" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:14px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">(x ∨ y ∨ z) ∧ (x̅ ∨ u ∨ v) ∧ Φ′</text><rect x="457" y="61" width="46" height="30" rx="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.4"/><text x="480" y="77" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">Φ</text><text x="510" y="76" text-anchor="start" dominant-baseline="central" fill="var(--muted)" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">n variables</text><line x1="480" y1="91" x2="366" y2="157" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/><rect x="337" y="157" width="58" height="30" rx="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.4"/><text x="366" y="173" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">Φ|xu</text><text x="366" y="202" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">≤ n − 2</text><line x1="480" y1="91" x2="442" y2="157" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/><rect x="407.5" y="157" width="69" height="30" rx="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.4"/><text x="442" y="173" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">Φ|xu̅v</text><text x="442" y="202" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">≤ n − 3</text><line x1="480" y1="91" x2="518" y2="157" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/><rect x="489" y="157" width="58" height="30" rx="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.4"/><text x="518" y="173" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">Φ|x̅y</text><text x="518" y="202" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">≤ n − 2</text><line x1="480" y1="91" x2="598" y2="157" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/><rect x="563.5" y="157" width="69" height="30" rx="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.4"/><text x="598" y="173" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">Φ|x̅y̅z</text><text x="598" y="202" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">≤ n − 3</text><text x="480" y="236" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13.5px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">T(n) = 2T(n−2) + 2T(n−3)</text><text x="480" y="256" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">λ = 1.7693</text></svg><figcaption><strong>Two branching rules for 3Sat.</strong> Left: the first clause (<i>x</i> ∨ <i>y</i> ∨ <i>z</i>) must be satisfied by <i>x</i>, or else by <i>y</i> with <i>x</i> false, or else by <i>z</i> with both false; the three branches fix 1, 2 and 3 variables. Right: when <i>x</i> is not pure, a second clause contains <i>x̅</i>; if <i>x</i> is true that clause needs <i>u</i> or (<i>u̅</i> and <i>v</i>), so every branch fixes at least 2 variables. λ is the largest root of the characteristic polynomial, and the running time is <i>O</i>(λ<sup><i>n</i></sup> poly(<i>n</i>)).</figcaption></figure>

> [!key] Solving backtracking recurrences
> Let $T(n)\le \text{poly}(n) + \sum_{i=1}^{k} T(n - a_i)$ for constants $1\le a_1\le a_2\le\cdots\le a_k$ (repetitions allowed). The **characteristic polynomial**
> $$
> r^{a_k} - \sum_{i=1}^{k} r^{a_k - a_i}
> $$
> has degree $a_k$, exactly one positive root $\lambda\ge1$, and no root of larger modulus. Then $T(n) = O(\lambda^n\,\text{poly}(n))$, which is $O(c^n)$ for every $c>\lambda$ — rounding the base up absorbs the polynomial. For a recurrence with several cases, $T(n)\le\text{poly}(n) + \max\{\dots\}$, solve each case and take the largest $\lambda$: $\lambda^n$ satisfies every case at once.

For 3Sat the polynomial is $r^3 - r^2 - r - 1$, with roots $1.83928676$ and $-0.41964338\pm0.60629073\,i$ (modulus $0.737$), so $T(n) = O(1.83929^n)$. (The note orders the $a_i$ "in non-increasing order" while writing $a_1\le\dots\le a_k$, which is non-decreasing; it says the polynomial has $k$ roots, but it has $a_k$ — $T(n-1)+T(n-4)$ has $k = 2$ terms and four roots; and it prints the real part of the complex roots as $-0.419643337$, where $(1 - 1.8392867552)/2 = -0.4196433776$. Exact closed forms, from all the roots and the base cases, are the subject of Appendix II.)

### Pure literals

A literal $x$ is **pure** in $\Phi$ if $x$ occurs and $\bar x$ does not. If $\Phi$ is satisfiable, it has a satisfying assignment in which every pure literal is true (making a pure literal true can only satisfy more clauses), so a pure literal can be set without branching. If $\Phi = (x\vee y\vee z)\wedge\Phi'$ has no pure literal, some clause contains $\bar x$: $\Phi = (x\vee y\vee z)\wedge(\bar x\vee u\vee v)\wedge\Phi'$, where $u$, $v$ may involve $y$ or $z$. Then $\Phi|x$ contains the clause $(u\vee v)$, so the branch "$x$ true" splits again exactly as before: $\Phi|x = (u\wedge\Phi'|xu)\vee(v\wedge\Phi'|x\bar uv)$.

```text
Faster3Sat(Φ):
  if Φ = ∅
      return True
  if Φ contains an empty clause          ⟨⟨missing in the note⟩⟩
      return False
  if Φ has a pure literal x
      return Faster3Sat(Φ|x)
  (x ∨ y ∨ z) ∧ (x̄ ∨ u ∨ v) ∧ Φ′ ← Φ
  if Faster3Sat(Φ|xu)
      return True
  if Faster3Sat(Φ|xūv)
      return True
  if Faster3Sat(Φ|x̄y)
      return True
  return Faster3Sat(Φ|x̄ȳz)
```

Every branch now fixes at least two variables:
$$
T(n) = \text{poly}(n) + \max\begin{cases} T(n-1) & \text{(pure literal)}\\ 2T(n-2) + 2T(n-3) & \text{(four branches)}\end{cases}
$$
The first case alone is polynomial; the second has characteristic polynomial $r^3 - 2r - 2$ with largest root $\lambda\approx 1.76929235$, so $T(n) = O(1.76930^n)$.

### Local search

Instead of building an assignment variable by variable, **local search** walks from a starting assignment toward a satisfying one. The **Hamming distance** between two assignments is the number of variables on which they differ. If $A$ is not satisfying, pick a clause $C$ that $A$ falsifies: every satisfying assignment $A^*$ disagrees with $A$ on at least one of $C$'s (at most three) variables, so flipping the right one brings $A$ one step closer to $A^*$. We don't know which one, so try all three.

```text
Local3Sat(Φ, A, r):                          ⟨⟨A is passed by value⟩⟩
  if A satisfies Φ
      return True
  if r = 0
      return False
  C ← any clause of Φ that A does not satisfy
  for each variable x of C
      if Local3Sat(Φ, A with x flipped, r − 1)
          return True
  return False
```

> [!key] Local search
> Local3Sat$(\Phi, A, r)$ returns True if and only if some satisfying assignment lies within Hamming distance $r$ of $A$. It makes at most $1 + 3 + \dots + 3^r$ calls: **$O(3^r\,\text{poly}(n))$ time**. It does not look at every assignment within distance $r$, only along falsified clauses.

The note's Figure B.2 unrolls the loop into three branches, flipping $A[x]$, $A[y]$, $A[z]$ in place and passing $A$, $A_y$, $A_z$; it is correct when each call gets its own copy of the assignment. Read with one shared array it is not: the third branch returns without undoing its flip, the caller's later branches start from the wrong assignment, and in the check of this page that version missed satisfying assignments within distance $r$ and gave wrong answers on several small formulas.

Every assignment has at least $n/2$ true or at least $n/2$ false variables, so every satisfying assignment is within distance $\lfloor n/2\rfloor$ of the all-True or the all-False assignment. Two calls of Local3Sat with $r = \lfloor n/2\rfloor$ therefore decide 3Sat in $O(3^{n/2}\,\text{poly}(n)) = O(1.73206^n)$ time.

### Random starting assignments

(♥ in the note.) Start instead from random assignments with a smaller radius, accepting a small probability of a false "unsatisfiable". Let $V(r) = \sum_{i=0}^{r}\binom ni$, the number of assignments within distance $r$ of a fixed one, and $P(r)$ the probability that local search with radius $r$ from a **uniformly random** assignment succeeds, for a satisfiable $\Phi$. The random start lands within distance $r$ of a fixed satisfying assignment with probability $V(r)/2^n$, so $P(r)\ge V(r)/2^n$.

- **Repetitions.** With $N(r) = n2^n/V(r)$ independent random starts, the probability that all fail is at most $(1 - V(r)/2^n)^{n2^n/V(r)}\le e^{-n}$. An answer True is always right; only "unsatisfiable" can be wrong.
- **Time.** $O(N(r)\,3^r\,\text{poly}(n)) = O\bigl(2^n3^r/V(r)\cdot\text{poly}(n)\bigr)$.
- **Volume.** For a constant $0<\alpha<1$, Stirling's formula gives $V(\alpha n)\ge\binom{n}{\alpha n} = \Omega\bigl(H(\alpha)^n/\sqrt n\bigr)$ with $H(\alpha) = (1/\alpha)^\alpha(1/(1-\alpha))^{1-\alpha}$, which is 2 raised to the binary entropy of $\alpha$ ($H(1/4)\approx1.7548$, $H(1/2) = 2$).
- **Optimizing.** With $r = \alpha n$ the time is $O\bigl((2(3\alpha)^\alpha(1-\alpha)^{1-\alpha})^n\,\text{poly}(n)\bigr)$. The derivative of $\alpha\ln(3\alpha) + (1-\alpha)\ln(1-\alpha)$ is $\ln(3\alpha) - \ln(1-\alpha)$, zero at $3\alpha = 1-\alpha$, $\alpha = 1/4$, where the base is $2\cdot(3/4)^{1/4}(3/4)^{3/4} = 3/2$.

> [!key] Randomized local search
> Local search with radius $n/4$ from $n2^n/V(n/4)$ uniformly random starting assignments decides 3Sat in $O((3/2)^n\,\text{poly}(n))$ time; it never accepts an unsatisfiable formula and rejects a satisfiable one with probability at most $e^{-n}$.

### Further extensions

Fifteen or more improved 3Sat algorithms have appeared since 1998, most based on local search. Schöning (1999) replaced the backtracking by a random walk of length $3n$ and reached $O((4/3)^n\,\text{poly}(n))$ with exponentially small error. As of 2016, per the note, the fastest deterministic algorithm runs in $O(1.3303^n)$ time (Makino, Tamaki and Yamamoto) and the fastest randomized one in $O(1.30704^n)$ expected time (Hertli's analysis of PPSZ). Practical SAT solvers combine backtracking, local search, random restarts and heuristics and routinely solve industrial instances with millions of variables — the exponential worst case is simply rare in practice.

## B.2 Maximum independent set

Now the input is an undirected graph $G$ and the output the size of its largest independent set. Write $N(v)$ for the **closed** neighborhood: $v$ and all its neighbors. The obvious backtracking either takes $v$ (and then none of its neighbors) or leaves it out:

```text
MaximumIndSetSize(G):
  if G = ∅
      return 0
  else
      v ← any node in G
      withv ← 1 + MaximumIndSetSize(G \ N(v))
      withoutv ← MaximumIndSetSize(G \ {v})
      return max{withv, withoutv}
```

If $v$ has no neighbors both calls get $n-1$ vertices, so $T(n) = 2T(n-1) + \text{poly}(n) = O(2^n\,\text{poly}(n))$. The same branching bounds the number $M(n)$ of **maximal** independent sets (independent sets to which no vertex can be added): each one contains $v$ or not, so $M(n)\le 2M(n-1)$ with $M(1) = 1$, which solves to $M(n)\le2^{n-1}$. (The note states the weaker $2^n - 1$. The truth is $3^{n/3}$, the note's Exercise 1; by brute force the maxima for $n = 1,\dots,6$ are $1, 2, 3, 4, 6, 9$.)

### Smarter case analysis

Each refinement removes the current worst case of the recurrence.

- **Degree 0.** An isolated vertex is in every maximal independent set, so take it: one call on $n-1$ vertices. Otherwise $v$ has a neighbor and $G\setminus N(v)$ has at most $n-2$ vertices. $T(n)\le\text{poly}(n) + \max\{T(n-1),\ T(n-1) + T(n-2)\} = O(1.61804^n)$, the Fibonacci recurrence ($\varphi = 1.6180340$).
- **Degree 1.** If $v$ has exactly one neighbor $w$, some *maximum* independent set contains $v$: in one that contains $w$, replace $w$ by $v$. So take $v$ — one call on at most $n-2$ vertices. Otherwise every vertex has degree at least 2 and taking $v$ deletes at least 3. $T(n)\le\text{poly}(n) + \max\{T(n-1),\ T(n-2),\ T(n-1)+T(n-3)\} = O(1.46558^n)$, from $r^3 - r^2 - 1$ ($\lambda = 1.4655712$).
- **Degree ≥ 3.** Branch on a vertex of degree at least 3: taking it deletes at least 4 vertices. If there is none, every vertex has degree exactly 2; on a path $u, v, w$ (with possibly $u$ adjacent to $w$) every maximal independent set contains $v$, or $u$, or $w$ (if $v$ is out, a neighbor of $v$ is in), and each choice deletes 3 vertices. $T(n)\le\text{poly}(n)+\max\{T(n-1),\ T(n-2),\ T(n-1)+T(n-4),\ 3T(n-3)\} = O(3^{n/3}\,\text{poly}(n)) = O(1.44225^n)$; the case $3T(n-3)$ is the worst, while $T(n-1)+T(n-4)$ alone would give $1.38028^n$ ($r^4 - r^3 - 1$).
- **Degree 2.** If every vertex has degree 2, every component is a cycle, and a cycle of length $k$ has a maximum independent set of size $\lfloor k/2\rfloor$ — no recursion needed. The worst case left is $T(n-1) + T(n-4)$: **$O(1.38028^n)$**.

```text
MaximumIndSetSize(G):
  if G = ∅
      return 0
  else if G has a node v with degree 0 or 1
      return 1 + MaximumIndSetSize(G \ N(v))           ⟨⟨≤ n − 1⟩⟩
  else if G has a node v with degree greater than 2
      withv ← 1 + MaximumIndSetSize(G \ N(v))          ⟨⟨≤ n − 4⟩⟩
      withoutv ← MaximumIndSetSize(G \ {v})            ⟨⟨≤ n − 1⟩⟩
      return max{withv, withoutv}
  else                                                 ⟨⟨every node has degree 2⟩⟩
      total ← 0
      for each component of G
          k ← number of vertices in the component
          total ← total + ⌊k/2⌋
      return total
```

<!-- fig:nb-mis -->
<figure class="cs-fig"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 250" width="640" height="250" role="img" style="font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-size:14px"><title>three small graphs: a degree-one vertex taken greedily, a degree-three vertex branched on, and a 5-cycle plus a 4-cycle</title><defs><marker id="ARR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs><rect x="20" y="86" width="96" height="48" rx="24" fill="none" stroke="var(--accent)" stroke-width="1.2" stroke-dasharray="4 3"/><line x1="40" y1="110" x2="92" y2="110" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/><line x1="92" y1="110" x2="150" y2="70" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/><line x1="92" y1="110" x2="160" y2="140" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/><line x1="150" y1="70" x2="160" y2="140" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/><line x1="160" y1="140" x2="104" y2="168" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/><circle cx="40" cy="110" r="11" fill="var(--paper)" stroke="var(--hi)" stroke-width="2.2"/><circle cx="92" cy="110" r="11" fill="var(--accent)" fill-opacity="0.35" stroke="var(--accent)" stroke-width="1.4"/><circle cx="150" cy="70" r="11" fill="var(--paper)" stroke="currentColor" stroke-width="1.4"/><circle cx="160" cy="140" r="11" fill="var(--paper)" stroke="currentColor" stroke-width="1.4"/><circle cx="104" cy="168" r="11" fill="var(--paper)" stroke="currentColor" stroke-width="1.4"/><text x="40" y="74" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">v</text><text x="92" y="74" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;">w</text><text x="100" y="18" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">deg v ≤ 1: take v</text><text x="100" y="206" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">one call on G ∖ N(v)</text><text x="100" y="224" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">(at most n − 1 vertices)</text><line x1="322" y1="108" x2="276" y2="66" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/><line x1="322" y1="108" x2="368" y2="66" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/><line x1="322" y1="108" x2="322" y2="160" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/><line x1="276" y1="66" x2="368" y2="66" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/><line x1="368" y1="66" x2="400" y2="140" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/><line x1="322" y1="160" x2="400" y2="140" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/><line x1="322" y1="160" x2="252" y2="150" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/><line x1="276" y1="66" x2="252" y2="150" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/><circle cx="322" cy="108" r="11" fill="var(--paper)" stroke="var(--hi)" stroke-width="2.2"/><circle cx="276" cy="66" r="11" fill="var(--accent)" fill-opacity="0.35" stroke="var(--accent)" stroke-width="1.4"/><circle cx="368" cy="66" r="11" fill="var(--accent)" fill-opacity="0.35" stroke="var(--accent)" stroke-width="1.4"/><circle cx="322" cy="160" r="11" fill="var(--accent)" fill-opacity="0.35" stroke="var(--accent)" stroke-width="1.4"/><circle cx="400" cy="140" r="11" fill="var(--paper)" stroke="currentColor" stroke-width="1.4"/><circle cx="252" cy="150" r="11" fill="var(--paper)" stroke="currentColor" stroke-width="1.4"/><text x="340" y="124" text-anchor="middle" dominant-baseline="central" fill="var(--hi)" style="font-size:15px;font-family:'STIX Two Math','Latin Modern Math','Cambria Math','Times New Roman',serif;font-style:italic;paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">v</text><text x="326" y="18" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">deg v ≥ 3: branch</text><text x="326" y="206" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">with v: G ∖ N(v), ≤ n − 4 vertices</text><text x="326" y="224" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">without v: G − v, n − 1 vertices</text><line x1="480" y1="70" x2="447.7" y2="93.5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/><line x1="447.7" y1="93.5" x2="460" y2="131.5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/><line x1="460" y1="131.5" x2="500" y2="131.5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/><line x1="500" y1="131.5" x2="512.3" y2="93.5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/><line x1="512.3" y1="93.5" x2="480" y2="70" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/><line x1="596.2" y1="86.8" x2="553.8" y2="86.8" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/><line x1="553.8" y1="86.8" x2="553.8" y2="129.2" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/><line x1="553.8" y1="129.2" x2="596.2" y2="129.2" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/><line x1="596.2" y1="129.2" x2="596.2" y2="86.8" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/><circle cx="480" cy="70" r="11" fill="var(--paper)" stroke="currentColor" stroke-width="1.4"/><circle cx="447.7" cy="93.5" r="11" fill="var(--hi)" stroke="var(--hi)" stroke-width="1.4"/><circle cx="460" cy="131.5" r="11" fill="var(--paper)" stroke="currentColor" stroke-width="1.4"/><circle cx="500" cy="131.5" r="11" fill="var(--hi)" stroke="var(--hi)" stroke-width="1.4"/><circle cx="512.3" cy="93.5" r="11" fill="var(--paper)" stroke="currentColor" stroke-width="1.4"/><circle cx="596.2" cy="86.8" r="11" fill="var(--hi)" stroke="var(--hi)" stroke-width="1.4"/><circle cx="553.8" cy="86.8" r="11" fill="var(--paper)" stroke="currentColor" stroke-width="1.4"/><circle cx="553.8" cy="129.2" r="11" fill="var(--hi)" stroke="var(--hi)" stroke-width="1.4"/><circle cx="596.2" cy="129.2" r="11" fill="var(--paper)" stroke="currentColor" stroke-width="1.4"/><text x="530" y="18" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:13.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;font-weight:600;">every degree 2: cycles</text><text x="530" y="206" text-anchor="middle" dominant-baseline="central" fill="currentColor" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">⌊5/2⌋ + ⌊4/2⌋ = 4</text><text x="530" y="224" text-anchor="middle" dominant-baseline="central" fill="var(--muted)" style="font-size:12.5px;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif;">no recursion at all</text><line x1="212" y1="30" x2="212" y2="230" stroke="var(--muted)" stroke-width="0.8" stroke-linecap="round" stroke-dasharray="2 4"/><line x1="436" y1="30" x2="436" y2="230" stroke="var(--muted)" stroke-width="0.8" stroke-linecap="round" stroke-dasharray="2 4"/></svg><figcaption><strong>The cases of the final MaximumIndSetSize (Figure B.3).</strong> Left: a vertex <i>v</i> of degree 0 or 1 can always be taken (some maximum independent set contains it), and <i>v</i> and its neighbor <i>w</i> (shaded) disappear. Middle: a vertex of degree at least 3 is branched on; taking it deletes its closed neighborhood of at least 4 vertices. Right: if neither applies every vertex has degree 2, the graph is a union of cycles, and a cycle of length <i>k</i> contributes ⌊<i>k</i>/2⌋ (one optimal choice filled). Worst case: <i>T</i>(<i>n</i>) = <i>T</i>(<i>n</i>−1) + <i>T</i>(<i>n</i>−4) + poly(<i>n</i>) = <i>O</i>(1.3803<sup><i>n</i></sup>).</figcaption></figure>

> [!example] The bases, checked
> | rule added | worst case | characteristic polynomial | $\lambda$ |
> |---|---|---|---|
> | none | $2T(n-1)$ | $r - 2$ | $2$ |
> | degree 0 | $T(n-1)+T(n-2)$ | $r^2 - r - 1$ | $1.6180340$ |
> | degree 1 | $T(n-1)+T(n-3)$ | $r^3 - r^2 - 1$ | $1.4655712$ |
> | degree ≥ 3 | $3T(n-3)$ | $r^3 - 3$ | $1.4422496$ |
> | degree 2 (cycles) | $T(n-1)+T(n-4)$ | $r^4 - r^3 - 1$ | $1.3802776$ |
>
> Each $\lambda$ is a little below the note's rounded-up base ($1.61804$, $1.46558$, $1.44225$, $1.38028$). Iterating each multi-case recurrence numerically gives the same growth rates.

### Further improvements

Tarjan and Trojanowski (1977) published a backtracking algorithm with several dozen cases, each with its own recurrence. Many cases are dominated by others without solving anything — $T(n-4) + T(n-5)$ grows more slowly than $T(n-3) + T(n-5)$ (bases $1.1673$ and $1.1939$) — and after discarding those, twelve remain (the note's Figure B.4). The worst is $T(n-2) + T(n-8) + 2T(n-10)$, with characteristic polynomial $r^{10} - r^8 - r^2 - 2$ and $\lambda = 1.256020$, so $T(n) = O(1.25603^n) = O(2^{n/3})$, since $2^{1/3} = 1.259921$. (The note prints $O(1.25603^2)$.) As of 2016 the fastest published algorithm runs in $O(1.2114^n)$ time (Bourgeois, Escoffier, Paschos and van Rooij), and an unpublished, computer-generated algorithm of Robson runs in $O(1.1889^n)$ time — which is inside $O(2^{n/4})$, since $2^{1/4} = 1.18921$; the note's "$O(2^{n/4}\,\text{poly}(n)) = O(1.1889^n)$" has the inclusion the wrong way round.

## B.3 Dynamic programming

**This section is unfinished:** a heading, three draft boxes and a list of topics to add. What is there:

- **Planned warm-up:** the Bellman–Held–Karp dynamic program for the traveling salesman problem in $O(2^n\,\text{poly}(n))$ time — one line, marked "leave as exercise?".
- **3-coloring in $O(2^n\,\text{poly}(n))$ time.** Let $\textit{OPT}(X)$ be True if $G$ has a 3-coloring in which every vertex of $X$ is red. Then
$$
\textit{OPT}(X) = \begin{cases}\textsf{False} & \text{if $X$ is not independent}\\ \textsf{True} & \text{if $G\setminus X$ is bipartite}\\ \bigvee_{v\in V\setminus X}\textit{OPT}(X\cup\{v\}) & \text{otherwise,}\end{cases}
$$
and $G$ is 3-colorable iff $\textit{OPT}(\varnothing)$. Correct because the red vertices of a 3-coloring form an independent set $R$ with $G\setminus R$ bipartite; if $G\setminus X$ is not bipartite, $R$ must contain another vertex. Memoized over the $2^n$ subsets, each entry in polynomial time.
- **Lawler's improvement to $O(3^{n/3}\,\text{poly}(n)) = O(1.4423^n)$.** Only *maximal* independent sets $X$ matter: $G$ is 3-colorable iff $G\setminus I$ is bipartite for some maximal independent set $I$ (extend the red class of a coloring to a maximal one). An $n$-vertex graph has at most $3^{n/3}$ maximal independent sets (Moon and Moser), and they can be listed in $O(3^{n/3}\,\text{poly}(n))$ time.
- **Backtracking alternative.** Color the vertices in a fixed whatever-first order; each vertex must differ from its parent, and without loss of generality the first two are red and green, so only $2^{n-2}$ colorings of a connected graph are candidates — $O(2^n\,\text{poly}(n))$, and memoization does not help.
- **Lawler's chromatic number in $O((1+3^{1/3})^n\,\text{poly}(n)) = O(2.4423^n)$.** With $\textit{OPT}(X)$ the chromatic number of the induced subgraph $G[X]$: $\textit{OPT}(\varnothing) = 0$ and $\textit{OPT}(X) = 1 + \min\{\textit{OPT}(X\setminus I) \mid I \text{ a maximal independent set of } G[X]\}$ (some color class of an optimal coloring extends to a maximal independent set). A subset of size $k$ has at most $3^{k/3}$ maximal independent sets, and $\sum_k\binom nk3^{k/3} = (1+3^{1/3})^n$. (The draft says "$O(3^{k/3})$ maximal independent sets *of size $k$*"; the bound is for a graph *with $k$ vertices* — $K_{10}$ alone has ten maximal independent sets of size 1.)
- **Listed but not written:** Horowitz–Sahni splitting for subset sum in $O(2^{n/2}\,\text{poly}(n))$ time (and 3SUM), and deciding by counting with inclusion–exclusion. The page does not fill these in.

All of the drafted algorithms were checked against brute force (see Sources); the planned topics are not covered here.

## Summary

- Backtracking recurrences $T(n)\le\text{poly}(n)+\sum_i T(n-a_i)$ solve to $O(\lambda^n\,\text{poly}(n))$, $\lambda$ = the positive root of $r^{a_k} - \sum_i r^{a_k-a_i}$; with several cases, take the largest $\lambda$.
- 3Sat: branch on a clause ($x$; $\bar xy$; $\bar x\bar yz$) — $1.8393^n$; set pure literals and branch on two clauses — $1.7693^n$. Both need a base case returning False on an empty clause.
- Local search: Local3Sat$(\Phi,A,r)$ is True iff a satisfying assignment lies within distance $r$ of $A$, $O(3^r\,\text{poly}(n))$; from all-True and all-False with $r = n/2$: $\sqrt3^{\,n}\approx1.7321^n$; from $n2^n/V(n/4)$ random starts with $r = n/4$: $(3/2)^n$, one-sided error $\le e^{-n}$.
- Maximum independent set: take vertices of degree $\le1$, branch on degree $\ge3$ ($n-1$ and $\le n-4$), solve cycles directly ($\lfloor k/2\rfloor$ each): $1.3803^n$. Tarjan–Trojanowski $2^{n/3}$; best known about $1.19^n$–$1.21^n$.
- Unfinished: 3-coloring by a DP over subsets in $O(2^n\,\text{poly}(n))$, via maximal independent sets in $O(3^{n/3}\,\text{poly}(n))$; chromatic number in $O(2.4423^n)$.
- The note ends with 5 exercises (at most $3^{n/3}$ maximal independent sets, $k$Sat recurrences, 3Sat in $O(\varphi^n\,\text{poly}(n))$, 4-coloring in $O(2^n\,\text{poly}(n))$, bounds on binomial sums), plus a note that more are needed.

> [!exam] For CS 374
> Not on the CS/ECE 374 exams; the course stops at proving NP-hardness ([[2-algorithms/12-np-hardness#128-the-general-pattern|§12.8]]). Two things carry over. First, the correct reading of "NP-hard": it rules out a polynomial-time algorithm unless P = NP, not a faster exponential one, and an answer such as "use brute force, $O(2^n)$" is a choice, not a theorem. Second, the analysis: the recurrences here are backtracking recurrences like those of [[2-algorithms/02-backtracking|Chapter 2]], and $T(n) = T(n-1) + T(n-2) + \Theta(1)$ — the Fibonacci recurrence, $\Theta(\varphi^n)$ — is solved by the same characteristic-polynomial method as every recurrence on this page ([[4-lecture-notes/99-solving-recurrences|Appendix II]]).

### Sources for this page
Erickson, "Faster Exponential Algorithms", Extended Dance Remix note B (14 pp., © 2018, CC BY-NC-SA 4.0; status line "Unfinished"; "Read Chapters 2, 3, and 12 first"), summarized in our own words; the site's file name and the index row say "Fast", the PDF's title says "Faster". The algorithms, recurrences, bases, the random-restart analysis, the case analysis for independent sets, the Tarjan–Trojanowski recurrence and the B.3 drafts are the note's; the "iff" form of the local-search lemma, the loop form of Local3Sat, the precise characteristic-polynomial statement, the table of bases, the $n = 100$ comparison and both figures are ours. Checked by `tools/checks/nb.py`: 3Sat and Faster3Sat (with the added base case) against brute force on 2500 random formulas with up to 9 variables, and their call counts against the recurrences; Local3Sat's "iff" for every start and radius on formulas with up to 6 variables, its call bound, the deterministic and randomized wrappers' probability claims by exact enumeration; all five stages of the independent-set algorithm against brute force on all 33,868 labelled graphs with at most 6 vertices and 320 random larger ones, with call counts against $T(n-1)+T(n-4)$; every characteristic root and base on the page, by `numpy.roots` and by iterating the recurrences; the twelve Tarjan–Trojanowski cases; the B.3 drafts (3-coloring DP, Lawler's 3-coloring and chromatic number, whatever-first backtracking with exactly $2^{n-2}$ candidates) against brute force; maximal-independent-set counts. **Errors in the note:** pp. 3 and 5, 3Sat and Faster3Sat (Figure B.1) never return False (add: an empty clause returns False); p. 4, "non-increasing order: $a_1\le\dots\le a_k$" (correct: non-decreasing); p. 4, the characteristic polynomial "has exactly $k$ complex roots" (correct: $a_k$); p. 4, complex roots $-0.419643337\pm\dots$ (correct: $-0.41964338\pm0.60629073i$); p. 6, Figure B.2 is wrong with a shared array (its third branch never undoes its flip; the check found missed solutions and wrong answers) and uses undefined $A_y$, $A_z$ (correct: pass copies); p. 7, $H(\alpha) = (1/\alpha)^\alpha(1/(1-\alpha))^{1-\alpha}$ is called "the binary entropy function" (it is 2 raised to the binary entropy); p. 8, "Uwe Schöning the running time" (a verb is missing: improved); p. 11, "$O(1.25603^2)$" (correct: $O(1.25603^n)$; the root is $1.2560202$); p. 11, "$O(2^{n/4}\,\text{poly}(n)) = O(1.1889^n)$" (false since $2^{1/4} = 1.18921$; correct: $O(1.1889^n)\subseteq O(2^{n/4})$); p. 11, footnote 5 "can Rooij" (van Rooij); p. 12, "Lawlar" (Lawler), "is parent", "first tow nodes", and "$O(3^{k/3})$ maximal independent sets of size $k$" (correct: in a graph with $k$ vertices); p. 13, Exercise 5(a) claims $\sum_{i\le\alpha n}\binom ni<H(\alpha)^n$ for all $0<\alpha<1$, false for $\alpha>1/2$ ($\alpha = 3/4$, $n = 40$: $1.1\times10^{12}$ versus $5.9\times10^{9}$); "Figure ??" for Figures B.1–B.4 on pp. 4, 6, 10 and 11. Loose but not wrong: p. 9 confirms $M(n)\le2^n-1$ from $M(n)\le2M(n-1)$, $M(1)=1$, which is true (the induction goes through) but weaker than the $2^{n-1}$ the recurrence gives. Not machine-checked: the literature claims (Schöning, Makino–Tamaki–Yamamoto, Hertli, Tarjan–Trojanowski's full case analysis, Bourgeois et al., Robson, Moon–Moser in general, Lawler's listing time) and the remarks on practical SAT solvers.
