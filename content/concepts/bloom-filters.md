---
title: "Bloom filters and sketches"
description: "Bloom filters (approximate set membership: no false negatives, false-positive rate about (1 − e^{−kn/m})^k, optimal k = (m/n) ln 2), the count-min sketch for item frequencies in a data stream, and the minimum-hash idea for counting distinct items — what is random, and what is guaranteed."
tags: [concept, algorithms, streaming]
aliases: ["Bloom filter", "count-min sketch", "streaming algorithm", "data stream", "false-positive rate", "distinct-element estimation"]
---

> [!definition] Definition — Bloom filter
> A **Bloom filter** for a set $X$ of $n$ items is an array of $m$ bits and $k$ hash functions $h_1,\ldots,h_k$ (assumed independent and ideal random). Inserting $x$ sets the bits $h_1(x),\ldots,h_k(x)$; a query $y$ answers **no** if one of its $k$ bits is 0 and **maybe** otherwise. Members always get "maybe" (**no false negatives**); a non-member gets "maybe" with probability about
> $$
> \big(1 - e^{-kn/m}\big)^k ,
> $$
> minimized by $k = (m/n)\ln 2$ to about $0.6185^{m/n}$. A rate $\delta$ needs about $1.44\,n\lg(1/\delta)$ bits and $\lg(1/\delta)$ hash functions.

**Why it works.** Each bit stays 0 with probability $(1-1/m)^{kn}\approx e^{-kn/m}$, and a non-member is fooled only if all $k$ of its random bits were set by other items. The estimate treats those $k$ bits as independent; they are not, and the true rate is slightly higher. The **count-min sketch** applies the same idea to counting: $d$ rows of $w$ counters, one hash function per row; an arrival of $x$ increments its counter in every row, and the estimate of $x$'s count $f_x$ is the **minimum** of its $d$ counters. Other items only ever add to a counter, so the estimate is never too low; in each row the excess has expectation at most $N/w$ (universality), so by Markov's inequality it exceeds $\varepsilon N$ with probability at most $1/(w\varepsilon)\le 1/e$ when $w = \lceil e/\varepsilon\rceil$, and all $d = \lceil\ln(1/\delta)\rceil$ independent rows fail together with probability at most $\delta$.

> [!recipe] Sizing
> | bits per item $m/n$ | best integer $k$ | false-positive estimate |
> |---|---|---|
> | 4 | 3 | 14.7% |
> | 8 | 6 | 2.16% |
> | 10 | 7 | 0.82% |
> | 16 | 11 | 0.046% |
>
> **Count-min:** for additive error $\varepsilon N$ with failure probability $\delta$, use $w = \lceil e/\varepsilon\rceil$ columns and $d = \lceil\ln(1/\delta)\rceil$ rows: $O(\frac1\varepsilon\log\frac1\delta)$ counters, $O(\log\frac1\delta)$ time per update and query, independent of the stream's length and the universe's size.

> [!trap]
> - **The errors are one-sided.** A Bloom filter's "no" and a count-min estimate's lower bound $\hat f_x\ge f_x$ are certain; only "maybe" and the overestimate are probabilistic.
> - **The probability is over the hash functions, for a fixed set or stream and one fixed query** — not over random queries, and not for all queries at once (multiply $\delta$ by the number of queries).
> - **More hash functions is not better**: past $(m/n)\ln 2$ the filter fills with 1s and the rate rises.
> - **Count-min error is additive** ($\varepsilon N$): useless for items much rarer than $\varepsilon N$.
> - **A plain Bloom filter cannot delete** — clearing a shared bit would create false negatives.

**Example.** A filter for $n = 10^6$ items with a 1% false-positive rate needs $m\approx 1.44\cdot 10^6\cdot\lg 100\approx 9.6\cdot 10^6$ bits — about 1.2 MB, whatever the size of the items — and 7 hash functions. With exactly $10^7$ bits (10 per item) and 7 functions the estimate is 0.82%.

**Distinct items.** To estimate the number $n$ of distinct items in a stream, hash every item to $[m]$ with a 2-uniform function and keep only the minimum hash value $\bar h$; repeats do not change it, and $n$ random points in $[m]$ have minimum about $m/n$, so $m/\bar h$ estimates $n$. One minimum is a crude estimate (within a constant factor, with constant probability); keeping the $k$ smallest values and taking the median of independent copies sharpens it. In the note this is an exercise and an unfinished section.

**Where it appears.** [[4-lecture-notes/06-filtering-and-streaming#61-bloom-filters|note 6, §6.1]] (Bloom filters), [[4-lecture-notes/06-filtering-and-streaming#62-false-positive-rate|§6.2]] (the false-positive rate and the optimal $k$), [[4-lecture-notes/06-filtering-and-streaming#63-streaming-algorithms|§6.3]] (data streams), [[4-lecture-notes/06-filtering-and-streaming#64-the-count-min-sketch|§6.4]] (count-min), [[4-lecture-notes/06-filtering-and-streaming#65-estimating-distinct-items|§6.5]] (distinct items); the hash families in [[4-lecture-notes/05-hashing#53-but-not-too-random|note 5, §5.3]].

Related: [[concepts/hashing]] · [[concepts/tail-inequalities]] · [[concepts/discrete-probability]] · [[concepts/dfa]]
