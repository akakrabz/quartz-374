---
title: "Discrete probability"
description: "Sample spaces, events, conditional probability and independence; random variables and expectation; linearity of expectation and the indicator method, which turn the expected value of any count into a sum of probabilities; the common distributions. The toolkit behind every randomized-algorithm analysis."
tags: [concept, algorithms, probability]
aliases: ["linearity of expectation", "indicator random variable", "indicator variable", "expected value", "expectation", "random variable", "sample space", "coupon collector"]
---

> [!definition] Definition
> A **discrete probability space** is a countable **sample space** $\Omega$ with weights $\Pr[\omega]\ge 0$ that sum to 1. An **event** is a set $A\subseteq\Omega$, with $\Pr[A] = \sum_{\omega\in A}\Pr[\omega]$; $\Pr[A\mid B] = \Pr[A\wedge B]/\Pr[B]$; $A$ and $B$ are **independent** if $\Pr[A\wedge B] = \Pr[A]\Pr[B]$. A **random variable** is a function $X\colon\Omega\to\mathbb{R}$, and its **expectation** is $\operatorname{E}[X] = \sum_x x\Pr[X = x]$. The **indicator** $[A]$ of an event is 1 on $A$ and 0 elsewhere, and $\operatorname{E}\big[[A]\big] = \Pr[A]$.
>
> **Linearity of expectation:** $\operatorname{E}\big[\sum_i\alpha_iX_i\big] = \sum_i\alpha_i\operatorname{E}[X_i]$ for **any** random variables — independent or not.
>
> | distribution | models | mean |
> |---|---|---|
> | uniform on $[1..n]$ | fair die | $(n+1)/2$ |
> | Bernoulli($p$) | one coin flip, any indicator | $p$ |
> | binomial($n,p$) | successes in $n$ independent flips | $np$ |
> | geometric($p$) | trials up to and including the first success | $1/p$ |

**Why it works.** Linearity is nothing but exchanging two sums over $\Omega$, so it cannot depend on how the variables interact. Combined with $\operatorname{E}[\text{indicator}] = \text{probability}$, it says that **the expected value of a count is the sum of the probabilities of the things counted** — and probabilities of single events are usually easy, often by symmetry. Products are different: $\operatorname{E}[XY] = \operatorname{E}[X]\operatorname{E}[Y]$ needs independence.

> [!recipe] Recipe — the expected value of a count
> 1. **Say what is random**: the algorithm's own random choices (for a randomized algorithm the input is fixed and arbitrary).
> 2. **Write the quantity as a sum of indicators**, $X = \sum_i X_i$ — one per comparison, collision, fixed point, new card, …
> 3. **Find each $p_i = \Pr[X_i = 1]$**, typically by a symmetry argument ("each of these $k$ elements is equally likely to be chosen first").
> 4. **Add**: $\operatorname{E}[X] = \sum_i p_i$. Harmonic sums $H_n = \sum_{k=1}^n 1/k$, with $\ln(n+1)\le H_n\le\ln n + 1$, are common.
>
> For "repeat until success": a trial that succeeds with probability $p$ takes $1/p$ attempts on average; split a longer process into phases and add the phase expectations (coupon collector: $nH_n$).

> [!trap]
> - **Independence is needed for products, not for sums.** $\operatorname{E}[R + R'] = 7$ for the top and bottom faces of one die, but $\operatorname{E}[RR'] = 28/3\ne\operatorname{E}[R]\operatorname{E}[R'] = 49/4$.
> - **$\operatorname{E}[f(X)]\ne f(\operatorname{E}[X])$** in general: not for $X^2$, $1/X$, $\max$ or $\log$.
> - **Expected time is not average-case time.** "$O(n\log n)$ expected" means: for every input, averaged over the algorithm's coins — no assumption about the inputs.
> - **Two geometric conventions**: failures before the first success have mean $(1-p)/p$; trials including it, $1/p$.
> - **Disjoint is not independent**: disjoint events of positive probability are dependent.

**Example.** The expected number of **fixed points** of a uniformly random permutation $\pi$ of $[1..n]$ is 1, for every $n$. Let $X_i = [\pi(i) = i]$; position $i$ receives each value with probability $1/n$, so $\Pr[X_i = 1] = 1/n$ and $\operatorname{E}[\sum_i X_i] = n\cdot\tfrac1n = 1$ — even though the $X_i$ are dependent (if $n-1$ points are fixed, so is the last). Check for $n = 3$: the permutations 123, 132, 213, 231, 312, 321 have 3, 1, 1, 0, 0, 1 fixed points, 6 in total, average 1.

**Where it appears.** Erickson's note 1: [[4-lecture-notes/01-discrete-probability#11-discrete-probability-spaces|§1.1]] (spaces, events, independence, identities), [[4-lecture-notes/01-discrete-probability#122-expectation|§1.2.2]] (expectation, linearity), [[4-lecture-notes/01-discrete-probability#13-common-probability-distributions|§1.3]] (distributions), [[4-lecture-notes/01-discrete-probability#15-pokémon-collecting|§1.5]] (the indicator method and the coupon collector), [[4-lecture-notes/01-discrete-probability#17-properties-of-random-permutations|§1.7]] (fixed points and cycles); note 2: [[4-lecture-notes/02-nuts-and-bolts#27-iterative-analysis|§2.7]] (randomized quicksort's comparisons as indicators); in the textbook, random pivots for quicksort and quickselect ([[2-algorithms/01-recursion#15-quicksort|§1.5]], [[2-algorithms/01-recursion#18-linear-time-selection|§1.8]]); and the later randomized notes on [[4-lecture-notes/03-treaps-and-skip-lists|treaps]], [[4-lecture-notes/04-tail-inequalities|tail inequalities]] and [[4-lecture-notes/05-hashing|hashing]].

Related: [[concepts/linear-time-selection]] · [[concepts/divide-and-conquer]] · [[concepts/recursion-trees]] · [[concepts/counting-arguments]] · [[concepts/tail-inequalities]] · [[concepts/hashing]] · [[concepts/treaps]]
