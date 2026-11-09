---
title: "Hashing"
description: "Hash tables with a randomly chosen hash function: universal and k-uniform families, chaining with expected Θ(1 + α) search, multiplicative hashing, two-level perfect hashing with O(1) worst-case search, open addressing and linear or binary probing, cuckoo hashing — what each guarantees, and what is random."
tags: [concept, algorithms, hashing]
aliases: ["hash table", "hash function", "universal hashing", "universal hash family", "perfect hashing", "cuckoo hashing", "open addressing", "linear probing"]
---

> [!definition] Definition — hashing with a random hash function
> A **hash table** stores keys from a universe $\mathcal U$ in an array $T[0\,..\,m-1]$, key $x$ at (or near) slot $h(x)$. The **hash function** $h$ is drawn at random from a family $\mathcal H$ when the table is built; the keys are arbitrary, and **only $h$ is random**. The family is
> - **universal** if $\Pr_h[h(x) = h(y)]\le 1/m$ for all keys $x\ne y$ (**near-universal**: $\le 2/m$);
> - **$k$-uniform** if any $k$ distinct keys get independent, uniformly distributed hash values.
>
> Example: $h_{a,b}(x) = ((ax + b)\bmod p)\bmod m$, with a prime $p > \lvert\mathcal U\rvert$, $a\in\{1,\ldots,p-1\}$ and $b\in\{0,\ldots,p-1\}$ random, is universal. The **load factor** is $\alpha = n/m$.

**Why it works.** Every fixed $h$ sends at least $\lceil\lvert\mathcal U\rvert/m\rceil$ keys to one slot, so some input defeats it; a random $h$ has small expected cost on every fixed input. The analyses need only pairwise collision probabilities: the number of keys colliding with $x$ is a sum of $n$ indicators of mean at most $1/m$, so its expectation is at most $\alpha$.

> [!recipe] What each scheme guarantees (and what is random)
> | scheme | random | guarantee |
> |---|---|---|
> | chaining, (near-)universal $h$ | $h$ | search $\Theta(1+\alpha)$ **expected**; longest chain $\Theta(\log n/\log\log n)$ at $\alpha = 1$, even for ideal $h$ |
> | table of size $n^2$ (ideal) or $2n^2$ (near-universal) | $h$ | no collision at all with probability $> 1/2$ |
> | two-level (perfect) hashing: size $n$, then $2n_j^2$ per slot | all salts | $O(1)$ **worst-case** search; $O(n)$ expected space ($\operatorname{E}[\sum n_j^2]\le 3n-2$) |
> | open addressing, ideal random probe permutations | probe sequences | unsuccessful search $\le 1/(1-\alpha)$ expected probes |
> | linear probing, ideal $h$ | $h$ | about $\tfrac12(1 + 1/(1-\alpha)^2)$ probes (Knuth): clustering |
> | binary probing $h(x)\oplus i$, $\alpha\le 1/4$ | 5-uniform $h$ | $O(1)$ expected per search |
> | cuckoo hashing, two tables of size $(1+\varepsilon)n$ | $h_1, h_2$ | lookup in 2 probes, worst case; insertion $O(1)$ expected |

> [!trap]
> - **Expected is not worst case.** $O(1)$ per search is an average over $h$ for each fixed key set; the slowest search in a chained table with $\alpha = 1$ takes $\Theta(\log n/\log\log n)$. Only perfect hashing and cuckoo hashing bound the **lookup** time in the worst case.
> - **Uniform is not universal**: the constant functions are uniform and collide always. Universal is not uniform either (example below).
> - **$x\bmod m$ is not a random hash function**; keys that differ by a multiple of $m$ always collide.
> - **Quadratic probing is not a permutation**: $(h + i^2)\bmod m$ reaches only $(m+1)/2$ slots for odd prime $m$.
> - **In the CS 374 rubric a hash table earns nothing as a memoization structure**: its $O(1)$ is expected, an array's is worst-case.

**Example.** Take $p = 7$, $m = 3$ in $h_{a,b}$ (42 functions). Every pair of keys collides with probability exactly $\tfrac{5}{21} < \tfrac13$ — the note's formula $\frac{(p - p\bmod m)(p - (m - p\bmod m))}{mp(p-1)} = \frac{6\cdot 5}{3\cdot 7\cdot 6}$ — so the family is universal. But $\Pr[h(x) = 0] = \tfrac37$ and $\Pr[h(x) = 1] = \Pr[h(x) = 2] = \tfrac27$ for every key, because the values $0,\ldots,6$ of $(ax+b)\bmod 7$ fall three into residue 0 and two into each other residue: **universal but not uniform**.

**Cuckoo hashing** (standard material; the note's section is empty). Two tables of size $r\ge(1+\varepsilon)n$ and two hash functions: key $x$ lives in $T_1[h_1(x)]$ or $T_2[h_2(x)]$, so a lookup reads two cells. To insert $x$, put it in $T_1[h_1(x)]$; an evicted key moves to its cell in the other table, evicting the next, and so on; after about $3\log_{1+\varepsilon} r$ evictions, **rehash** with new functions. For sufficiently independent random $h_1, h_2$, insertions take $O(1)$ expected time and rehashes are rare (Pagh and Rodler, 2001). Simulated with $\varepsilon = 0.1$: about 0.6 evictions per insertion, a few percent of builds rehash, fewer as $n$ grows; above total load $1/2$ builds fail almost always.

**Where it appears.** [[4-lecture-notes/05-hashing#53-but-not-too-random|note 5, §5.3]] (the families), [[4-lecture-notes/05-hashing#54-chaining|§5.4]] (chaining), [[4-lecture-notes/05-hashing#55-multiplicative-hashing|§5.5]] (multiplicative hashing), [[4-lecture-notes/05-hashing#56-high-probability-bounds-balls-and-bins|§5.6]] (balls and bins), [[4-lecture-notes/05-hashing#57-perfect-hashing|§5.7]] (perfect hashing), [[4-lecture-notes/05-hashing#58-open-addressing|§5.8]]–[[4-lecture-notes/05-hashing#510-analysis-of-binary-probing|§5.10]] (open addressing, probing), [[4-lecture-notes/05-hashing#511-cuckoo-hashing|§5.11]] (cuckoo hashing); Bloom filters and count-min sketches in [[4-lecture-notes/06-filtering-and-streaming|note 6]]; fast adjacency lists in [[2-algorithms/05-basic-graph-algorithms#54-data-structures|§5.4 of the textbook]]; the rubric's rule in [[0-toolkit/06-how-exams-are-graded#12-dynamic-programming|how exams are graded]].

Related: [[concepts/bloom-filters]] · [[concepts/discrete-probability]] · [[concepts/tail-inequalities]] · [[concepts/memoization]] · [[concepts/dynamic-programming]]
