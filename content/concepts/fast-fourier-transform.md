---
title: "Fast Fourier transform"
description: "The discrete Fourier transform evaluates a polynomial at the n-th roots of unity; the radix-2 FFT computes it by divide and conquer in O(n log n) time, the inverse transform is the same algorithm with conjugated roots divided by n, and together they multiply polynomials in O(n log n) time."
tags: [concept, algorithms, polynomials]
aliases: ["FFT", "DFT", "discrete Fourier transform", "radix-2 FFT", "Cooley–Tukey FFT", "inverse FFT"]
---

> [!definition] Definition — DFT and radix-2 FFT
> A polynomial $p(x) = \sum_{k=0}^{n-1} P[k]\,x^k$ is given either by its **coefficients** $P[0\,..\,n-1]$ or by its **samples**, its values at $n$ fixed distinct points. With $\omega_n = e^{2\pi i/n}$, the **discrete Fourier transform** samples $p$ at the $n$th roots of unity:
> $$
> P^*[j] = p(\omega_n^j) = \sum_{k=0}^{n-1} P[k]\,\omega_n^{jk}\qquad(0\le j<n).
> $$
> For $n$ a power of 2 the **radix-2 FFT** splits $P$ into its even coefficients $U$ and odd coefficients $V$, transforms both recursively, and combines, for $0\le j<n/2$,
> $$
> P^*[j] = U^*[j] + \omega_n^j V^*[j],\qquad P^*[j+n/2] = U^*[j] - \omega_n^j V^*[j],
> $$
> in $T(n) = 2T(n/2) + \Theta(n) = \Theta(n\log n)$ time. The **inverse** DFT is $P = \overline{V}P^*/n$ (Lemma A.1): conjugate, FFT, conjugate, divide by $n$ — also $\Theta(n\log n)$.

**Why it works.** $p(x) = p_{\text{even}}(x^2) + x\,p_{\text{odd}}(x^2)$, so evaluating $p$ at a set of points costs two evaluations of half-size polynomials at the *squares* of the points. For the $n$th roots of unity the squares are only the $n/2$ roots of order $n/2$, because $\omega_n^{j+n/2} = -\omega_n^j$: both subproblems are half the size, the mergesort recurrence follows, and the minus sign is why one product $\omega_n^jV^*[j]$ serves two outputs. Lemma A.1 holds because distinct rows of the matrix $(\omega_n^{jk})$ are orthogonal: $\sum_\ell \omega_n^{(j-k)\ell} = 0$ for $j\ne k$, a geometric series over a full circle.

> [!recipe] Recipe — multiply two polynomials (or convolve two sequences)
> 1. Pad the coefficient vectors (lengths $m$ and $n$) with zeros to a power of 2, $N\ge m+n-1$.
> 2. FFT both: $O(N\log N)$.
> 3. Multiply the samples pointwise: $R^*[j] = P^*[j]\cdot Q^*[j]$, $O(N)$.
> 4. Inverse FFT of $R^*$; with integer inputs, round to the nearest integers.
>
> Total $\Theta((m+n)\log(m+n))$ arithmetic operations, against $\Theta(mn)$ for the school method and $O(n^{\lg 3})$ for Karatsuba.

> [!trap]
> - **Too little padding** computes the product modulo $x^N-1$: coefficients of degree $\ge N$ wrap around onto the low ones (example below).
> - **Sign conventions differ.** Algorithms texts use $e^{+2\pi i/n}$; `numpy.fft.fft` and most signal-processing texts use $e^{-2\pi i/n}$ for the forward transform.
> - **The sample points matter.** At arbitrary points, coefficients → samples is a Vandermonde matrix–vector product, $\Theta(n^2)$; the speed comes from the roots of unity being a *collapsing* set.
> - **$O(n\log n)$ counts arithmetic operations** on complex numbers, in floating point: exact integer results need rounding and enough precision.

**Example.** Square $p(x) = 2 + 3x + x^2$. With $N = 4$ the samples at $1, i, -1, -i$ are $[6,\ 1+3i,\ 0,\ 1-3i]$, their squares $[36,\ -8+6i,\ 0,\ -8-6i]$, and the inverse transform gives $[5, 12, 13, 6]$ — wrong, because the square has degree 4 and needs 5 coefficients: the $x^4$ coefficient 1 has wrapped onto the constant 4. With $N = 8$ the same steps give $4 + 12x + 13x^2 + 6x^3 + x^4$, which is $p(x)^2$.

**Where it appears.** [[4-lecture-notes/a-fast-fourier-transforms#a2-alternate-representations|§A.2]] (coefficient, root and sample representations), [[4-lecture-notes/a-fast-fourier-transforms#a4-divide-and-conquer|§A.4]] (collapsing sets), [[4-lecture-notes/a-fast-fourier-transforms#a5-the-discrete-fourier-transform|§A.5]] (roots of unity, the DFT, Radix2FFT), [[4-lecture-notes/a-fast-fourier-transforms#a6-more-general-factoring|§A.6]] (any composite $n$), [[4-lecture-notes/a-fast-fourier-transforms#a7-inverting-the-fft|§A.7]] (Lemma A.1, inverse FFT), [[4-lecture-notes/a-fast-fourier-transforms#a8-fast-polynomial-multiplication|§A.8]] (FFTMultiply), [[4-lecture-notes/a-fast-fourier-transforms#a9-inside-the-radix-2-fft|§A.9]] (bit reversal, butterflies); Karatsuba's slower divide and conquer for the same problem in [[2-algorithms/01-recursion#19-fast-multiplication|§1.9]].

Related: [[concepts/divide-and-conquer]] · [[concepts/master-theorem]] · [[concepts/recursion-trees]] · [[concepts/recursion]]
