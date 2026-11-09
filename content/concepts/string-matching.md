---
title: "String matching"
description: "Finding a pattern P[1..m] in a text T[1..n]: brute force in O(nm), Karp–Rabin fingerprints in O(n) expected time, Knuth–Morris–Pratt in O(n + m) worst-case time with the failure function — which is a compressed DFA for “contains P”."
tags: [concept, algorithms, string-matching]
aliases: ["KMP", "Knuth–Morris–Pratt", "Knuth-Morris-Pratt", "Karp–Rabin", "Karp-Rabin", "Rabin–Karp", "failure function", "pattern matching", "fingerprinting"]
---

> [!key] String matching (Director's Cut 7)
> Given a text $T[1..n]$ and a pattern $P[1..m]$, find the smallest shift $s$ with $T[s..s+m-1] = P$.
>
> | algorithm | idea | time |
> |---|---|---|
> | brute force | compare $P$ at every shift, stop at the first mismatch | $O(nm)$ worst case |
> | Karp–Rabin | compare fingerprints $p\bmod q$ and $t_s\bmod q$, updated in $O(1)$ per shift; check each hit | $O(n)$ expected |
> | Knuth–Morris–Pratt | never re-read a matched character: after $T[i]\ne P[j]$, continue with $j\leftarrow\mathit{fail}[j]$ | $O(m) + O(n)$ worst case |
>
> **Failure function:** $\mathit{fail}[1] = 0$, and $\mathit{fail}[j] - 1$ is the length of the longest **border** — proper prefix that is also a suffix — of $P[1..j-1]$.

**Why it works.** Karp–Rabin's randomness is in the algorithm, not the input: with $q$ a random prime up to $m^2\lg m$, a window that differs from $P$ has a fingerprint collision only if $q$ divides a number below $10^m$, which has at most $m\lg 10$ prime factors among $\Theta(m^2)$ candidates; with a fixed prime $q > m^2$ and a random radix $b$, a collision is a root of a nonzero polynomial of degree $< m$, probability $< 1/m$. Either way the expected number of false hits is $O(n/m)$, each costing $O(m)$. KMP is correct because, after $P[1..j-1]$ has matched, the next shift that could succeed aligns the longest border of $P[1..j-1]$ with the text; it is fast because every comparison advances the text or slides the pattern, at most $n$ of each.

> [!recipe] Recipe — failure function and DFA by hand
> 1. $\mathit{fail}[1] = 0$, $\mathit{fail}[2] = 1$; for $j\ge 3$ find the longest border of $P[1..j-1]$ and add 1.
> 2. **Optimized** (left to right): if $P[\mathit{fail}[j]] = P[j]$, replace $\mathit{fail}[j]$ by the optimized $\mathit{fail}[\mathit{fail}[j]]$.
> 3. **DFA for "contains $P$":** states $0..m$ (characters matched); $\delta(k,a) = k+1$ if $P[k+1] = a$; else $\delta(0,a) = 0$ and $\delta(k,a) = \delta(\mathit{fail}[k+1]-1, a)$; state $m$ absorbs. It is minimal: the $m+1$ prefixes of $P$ are a fooling set.

> [!trap]
> - **Index conventions differ.** Here $\mathit{fail}[j]$ is a node to resume at (border length + 1, for the border of $P[1..j-1]$); the common "prefix function" $\pi[j]$ is the border length of $P[1..j]$, so $\pi[j] = \mathit{fail}[j+1] - 1$.
> - **Karp–Rabin's $O(n)$ is expected**, over the random modulus or radix, for every input; a fixed public modulus can be defeated, and skipping the check of each hit gives wrong answers.
> - **Polynomial hashing needs characters smaller than $q$**, or distinct characters may collide for every radix.
> - **Failure edges read no input**: the KMP machine becomes a DFA only after unfolding $\delta$ as above.
> - **The $O(n)$ bound is for the whole search.** One text character can trigger several failure steps; the total is at most $2n - 1$ comparisons.

**Example.** $P = \mathtt{AABA}$: the borders of `A`, `AA`, `AAB` have lengths 0, 1, 0, so $\mathit{fail} = 0, 1, 2, 1$; optimized, $0, 0, 2, 0$ ($P[2] = P[1]$ and $P[4] = P[1]$). On $T = \mathtt{AABBAABA}$, KMP matches `AAB`, fails at $T[4] = \mathtt{B}$ against $P[4]$, then tries $P[\mathit{fail}[4]] = P[1] = \mathtt{A}$, which fails too — the optimized table jumps straight to 0 — and then reads $T[5..8] = \mathtt{AABA}$: a match at shift 5 after 9 comparisons (8 with the optimized table).

**Where it appears.** [[4-lecture-notes/07-string-matching#71-brute-force|note 7, §7.1]] (brute force), [[4-lecture-notes/07-string-matching#73-karprabin-fingerprinting|§7.3]] (Karp–Rabin, random primes, polynomial hashing), [[4-lecture-notes/07-string-matching#75-finite-state-machines|§7.5]] (the KMP machine and search, [[4-lecture-notes/07-string-matching#the-machine-as-a-dfa|as a DFA]]), [[4-lecture-notes/07-string-matching#76-computing-the-failure-function|§7.6]] (ComputeFailure), [[4-lecture-notes/07-string-matching#77-optimizing-the-failure-function|§7.7]] (the optimized failure function); the "contains `11`" DFA of [[1-models-of-computation/03-finite-state-machines#35-designing-dfas-dfas-are-algorithms|§3.5]] is the KMP DFA for $P = \mathtt{11}$.

Related: [[concepts/dfa]] · [[concepts/fooling-sets]] · [[concepts/subset-construction]] · [[concepts/strings]] · [[concepts/hashing]] · [[concepts/dynamic-programming]]
