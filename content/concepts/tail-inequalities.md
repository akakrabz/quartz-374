---
title: "Tail inequalities"
description: "Bounds on the probability that a random variable is far from its mean — Markov, Chebyshev, higher moments and Chernoff — and what “with high probability” means; the tools behind every high-probability running time."
tags: [concept, algorithms, probability]
aliases: ["tail inequality", "tail bound", "Markov's inequality", "Chebyshev's inequality", "Chernoff bound", "Chernoff bounds", "with high probability", "w.h.p."]
---

> [!key] The bounds (X a sum of indicator variables with mean μ)
> - **Markov** (any $Z\ge 0$): $\Pr[Z\ge z]\le\mathrm{E}[Z]/z$.
> - **Chebyshev** (pairwise independent): variance $\sigma^2 = \sum_i p_i(1-p_i)\le\mu$, so $\Pr[\lvert X-\mu\rvert\ge\Delta]\le\sigma^2/\Delta^2$ and $\Pr[X\ge(1+\delta)\mu] < 1/(\delta^2\mu)$.
> - **$2k$-th moment** ($2k$-wise independent, $\mu\ge1$): $\Pr[X\ge(1+\delta)\mu] = O\big((1/(\delta^2\mu))^k\big)$.
> - **Chernoff** (mutually independent): $\Pr[X\ge x]\le e^{x-\mu}(\mu/x)^x$ for $x\ge\mu$, the same bound for $\Pr[X\le x]$ when $0<x\le\mu$; for $0<\delta<1$,
> $$
> \Pr[X\ge(1+\delta)\mu]\le e^{-\delta^2\mu/3},\qquad \Pr[X\le(1-\delta)\mu]\le e^{-\delta^2\mu/2}.
> $$
> An event happens **with high probability** if its probability is at least $1 - 1/n^c$ for a constant $c\ge 1$.

**Why it works.** Each bound is Markov's inequality applied to a cleverly chosen non-negative variable: $(X-\mu)^2$ for Chebyshev, $(X-\mu)^{2k}$ for higher moments, $\alpha^X$ for Chernoff. More independence makes the expectation of that variable computable — cross terms vanish, or the expectation of a product factors as $\mathrm{E}[\alpha^X] = \prod_i(1 + (\alpha-1)p_i)\le e^{(\alpha-1)\mu}$ — and the tail bound sharpens from $\Theta(1)$ to polynomial to exponential.

> [!recipe] Recipe — a "with high probability" bound
> 1. Write the bad quantity for **one** object (a node's depth, a bin's load) as a sum of indicators; find $\mu$ (or an upper bound on it — the absolute Chernoff bound increases with $\mu$, so an upper bound may be plugged in).
> 2. Check **mutual independence** of those indicators; if only some groups are independent, split the sum.
> 3. Apply Chernoff to get probability $\le 1/n^{c+1}$ for one object.
> 4. **Union bound** over the $n$ objects: all are fine with probability $\ge 1 - 1/n^c$.

> [!trap]
> - **Wrong independence:** Chernoff needs mutual independence; Chebyshev only pairwise. Dependent indicators (the $n-1$ ancestor indicators of a treap node) do not qualify.
> - **The simple forms need $0<\delta<1$**; for large deviations use $e^{x-\mu}(\mu/x)^x$.
> - **Monotonicity mistakes:** $a^\mu < a^{\ln n}$ for $\mu < \ln n$ only if $a > 1$ — a slip Erickson's note itself makes.
> - **Markov needs $Z\ge 0$**; it says nothing useful when $z\le\mathrm{E}[Z]$.

**Example.** $N = 1000$ fair coins, at least 600 heads ($\mu = 500$, $\delta = 0.2$). Markov: $\le 5/6$. Chebyshev with the variance 250: $\le 250/100^2 = 1/40$. Simple Chernoff: $\le e^{-20/3}\approx 1.3\cdot10^{-3}$. Multiplicative Chernoff: $\le(e^{0.2}/1.2^{1.2})^{500}\approx 8.3\cdot10^{-5}$. The fair-coin bound $(2\cdot0.6^{0.6}0.4^{0.4})^{-1000} = e^{-20.14}\approx 1.8\cdot10^{-9}$. Exact: $\approx 1.36\cdot10^{-10}$.

**Where it appears.** Erickson's note 4: [[4-lecture-notes/04-tail-inequalities#41-markovs-inequality|§4.1]] (Markov), [[4-lecture-notes/04-tail-inequalities#43-chebyshevs-inequality|§4.3]] (Chebyshev), [[4-lecture-notes/04-tail-inequalities#45-chernoff-bounds|§4.5]] (Chernoff), [[4-lecture-notes/04-tail-inequalities#46-coin-flips|§4.6]] (coin flips), [[4-lecture-notes/04-tail-inequalities#48-back-to-treaps-take-2|§4.8]] (treap depth); skip-list levels by the union bound in [[4-lecture-notes/03-treaps-and-skip-lists#322-number-of-levels|note 3, §3.2.2]]; the random-pivot remark in [[2-algorithms/01-recursion#15-quicksort|§1.5]]; hashing in [[4-lecture-notes/05-hashing|note 5]].

Related: [[concepts/discrete-probability]] · [[concepts/treaps]] · [[concepts/hashing]]
