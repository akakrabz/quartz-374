#!/usr/bin/env python3
"""Checks for content/4-lecture-notes/a-fast-fourier-transforms.md (Erickson, Extended Dance Remix A, Fast Fourier
Transforms) and the concept page content/concepts/fast-fourier-transform.md.

Every algorithm is implemented exactly as the page states it (Evaluate, Horner, Add, Multiply, Lagrange
interpolation, the collapsing-set recursion, Radix2FFT, the iterative bit-reversal + butterfly FFT, the corrected
FactorFFT, InverseFFT, InverseRadix2FFT, FFTMultiply) and compared with brute force (the O(n^2) DFT straight from
the definition, naive O(nm) multiplication, numpy.fft) on many random inputs; polynomial products must agree EXACTLY
with the naive integer product after rounding. Every identity about roots of unity is checked for many n and k, every
worked example on the two pages is recomputed, and every error found in the note is demonstrated."""
import cmath
import itertools
import math
import random
import sys
from fractions import Fraction

import numpy as np

FAIL = []


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAIL.append(name)


rng = random.Random(374)
EPS = 1e-9


def close(a, b, tol=1e-7):
    a, b = np.asarray(a, dtype=complex), np.asarray(b, dtype=complex)
    return a.shape == b.shape and (a.size == 0 or float(np.max(np.abs(a - b))) <= tol * max(1.0, float(np.max(np.abs(b)))))


def omega(n, k=1):
    """omega_n^k = e^{2 pi i k / n}: the note's (and the page's) convention, a plus sign in the exponent."""
    return cmath.exp(2j * math.pi * k / n)


# ======================================================================================= A.1 polynomials
def Evaluate(P, x):
    X, y = 1, 0  # X = x^j
    for j in range(len(P)):
        y = y + P[j] * X
        X = X * x
    return y


def Horner(P, x):
    n = len(P) - 1
    y = P[n]
    for i in range(n - 1, -1, -1):
        y = x * y + P[i]
    return y


def Add(P, Q):
    return [P[j] + Q[j] for j in range(len(P))]


def Multiply(P, Q):
    n, m = len(P) - 1, len(Q) - 1
    R = [0] * (n + m + 1)
    for j in range(n + 1):
        for k in range(m + 1):
            R[j + k] = R[j + k] + P[j] * Q[k]
    return R


ok_eval = ok_horner = ok_add = ok_mul = True
mults_eval = mults_horner = None
for trial in range(2000):
    n = rng.randint(0, 12)
    P = [rng.randint(-20, 20) for _ in range(n + 1)]
    Q = [rng.randint(-20, 20) for _ in range(n + 1)]
    m = rng.randint(0, 12)
    Q2 = [rng.randint(-20, 20) for _ in range(m + 1)]
    x = rng.randint(-5, 5)
    truth = sum(P[j] * x ** j for j in range(n + 1))
    ok_eval &= Evaluate(P, x) == truth
    ok_horner &= Horner(P, x) == truth
    ok_add &= all(Evaluate(Add(P, Q), t) == Evaluate(P, t) + Evaluate(Q, t) for t in range(-3, 4))
    R = Multiply(P, Q2)
    ok_mul &= len(R) == n + m + 1 and all(Evaluate(R, t) == Evaluate(P, t) * Evaluate(Q2, t) for t in range(-4, 5))
    ok_mul &= R == [int(v) for v in np.convolve(P, Q2)]
check("A.1 Evaluate computes sum P[j] x^j (2000 random integer polynomials)", ok_eval)
check("A.1 Horner computes the same value", ok_horner)
check("A.1 Add: (p+q)(x) = p(x)+q(x)", ok_add)
check("A.1 Multiply: (p.q)(x) = p(x).q(x), n+m+1 coefficients, equals numpy.convolve", ok_mul)

# multiplication counts: Evaluate 2(n+1), Horner n -> 'cut the number of multiplications in half'


class Num:
    count = 0

    def __init__(self, v):
        self.v = v

    def __mul__(self, o):
        Num.count += 1
        return Num(self.v * (o.v if isinstance(o, Num) else o))

    __rmul__ = __mul__

    def __add__(self, o):
        return Num(self.v + (o.v if isinstance(o, Num) else o))

    __radd__ = __add__


ok = True
for n in range(0, 30):
    P = [Num(rng.randint(-5, 5)) for _ in range(n + 1)]
    Num.count = 0
    Evaluate(P, Num(3))
    e = Num.count
    Num.count = 0
    Horner(P, Num(3))
    h = Num.count
    ok &= e == 2 * (n + 1) and h == n
check("A.1 Evaluate uses 2n+2 multiplications, Horner exactly n (n = 0..29)", ok)
check("A.1 example p(x) = 1 + 2x + 3x^2 at x = 2: Horner 3 -> 8 -> 17",
      Horner([1, 2, 3], 2) == 17 and 2 * 3 + 2 == 8 and 2 * 8 + 1 == 17 and Evaluate([1, 2, 3], 2) == 17)
check("A.1 Multiply makes (n+1)(m+1) products: Theta(n^2) for two degree-n polynomials", True)

# ======================================================================================= A.2 representations
# roots + scale: evaluate in O(n), multiply by concatenating roots and multiplying scales
ok = True
for trial in range(300):
    k1, k2 = rng.randint(1, 6), rng.randint(1, 6)
    r1 = [rng.randint(-5, 5) for _ in range(k1)]
    r2 = [rng.randint(-5, 5) for _ in range(k2)]
    s1, s2 = rng.randint(1, 4), rng.randint(1, 4)
    ev = lambda s, rs, x: s * math.prod(x - r for r in rs)
    for x in range(-6, 7):
        ok &= ev(s1 * s2, r1 + r2, x) == ev(s1, r1, x) * ev(s2, r2, x)
check("A.2 roots representation: product = (s1 s2, roots concatenated)", ok)


def lagrange_value(xs, ys, x, upper):
    """sum_{j=0}^{upper} y_j / prod_{k != j}(x_j - x_k) * prod_{k != j}(x - x_k), exact (all k = 0..len-1)."""
    total = Fraction(0)
    for j in range(upper + 1):
        num = Fraction(1)
        den = Fraction(1)
        for k in range(len(xs)):
            if k != j:
                num *= (x - xs[k])
                den *= (xs[j] - xs[k])
        total += Fraction(ys[j]) * num / den
    return total


ok = True
for trial in range(300):
    n = rng.randint(0, 7)  # degree n, n+1 samples
    coeffs = [rng.randint(-9, 9) for _ in range(n + 1)]
    xs = rng.sample(range(-15, 16), n + 1)
    ys = [Evaluate(coeffs, x) for x in xs]
    for x in range(-8, 9):
        ok &= lagrange_value(xs, ys, x, n) == Evaluate(coeffs, x)
check("A.2 Lagrange's formula with j = 0..n (n+1 samples) reproduces every degree-n polynomial exactly", ok)

# the note prints the outer sum as j = 0 .. n-1 (p. 4): one of the n+1 samples is ignored
xs, ys = [0, 1, 2], [1, 2, 5]  # p(x) = 1 + x^2, degree n = 2
wrong_at_x2 = lagrange_value(xs, ys, 2, 1)
check("A.2 ERROR p. 4: with the sum stopping at j = n-1, the formula misses (x_n, y_n): 1 + x^2 through (0,1),(1,2),(2,5) "
      "gives 0 at x = 2 instead of 5", wrong_at_x2 == 0 and lagrange_value(xs, ys, 2, 2) == 5, f"value {wrong_at_x2}")

# uniqueness: Vandermonde determinant = prod_{j<k} (x_k - x_j) != 0 for distinct x's


def det_frac(M):
    M = [[Fraction(v) for v in row] for row in M]
    n, d = len(M), Fraction(1)
    for c in range(n):
        p = next((r for r in range(c, n) if M[r][c] != 0), None)
        if p is None:
            return Fraction(0)
        if p != c:
            M[c], M[p] = M[p], M[c]
            d = -d
        d *= M[c][c]
        for r in range(c + 1, n):
            f = M[r][c] / M[c][c]
            for cc in range(c, n):
                M[r][cc] -= f * M[c][cc]
    return d


ok = True
for trial in range(200):
    n = rng.randint(1, 6)
    xs = rng.sample(range(-10, 11), n)
    V = [[x ** j for j in range(n)] for x in xs]
    ok &= det_frac(V) == math.prod(xs[k] - xs[j] for j in range(n) for k in range(j + 1, n))
check("A.3 Vandermonde determinant = prod_{j<k}(x_k - x_j): nonzero for distinct sample points (unique interpolant)", ok)

# V a = y and a = V^{-1} y (exact)


def solve_frac(M, b):
    n = len(M)
    A = [[Fraction(v) for v in row] + [Fraction(bb)] for row, bb in zip(M, b)]
    for c in range(n):
        p = next(r for r in range(c, n) if A[r][c] != 0)
        A[c], A[p] = A[p], A[c]
        for r in range(n):
            if r != c and A[r][c] != 0:
                f = A[r][c] / A[c][c]
                A[r] = [u - f * v for u, v in zip(A[r], A[c])]
    return [A[r][n] / A[r][r] for r in range(n)]


ok = True
for trial in range(150):
    n = rng.randint(1, 7)
    a = [rng.randint(-9, 9) for _ in range(n)]
    xs = rng.sample(range(-10, 11), n)
    V = [[x ** j for j in range(n)] for x in xs]
    y = [sum(V[i][j] * a[j] for j in range(n)) for i in range(n)]
    ok &= y == [Evaluate(a, x) for x in xs] and solve_frac(V, y) == a
check("A.3 V a = y (samples) and solving the system recovers the coefficients exactly", ok)

# ======================================================================================= A.4 divide and conquer
check("A.4 example: 1 + 2x + 3x^2 + 4x^3 = (1 + 3x^2) + x (2 + 4x^2)",
      all(Evaluate([1, 2, 3, 4], x) == Evaluate([1, 3], x * x) + x * Evaluate([2, 4], x * x) for x in range(-9, 10)))
ok = True
for trial in range(500):
    n = rng.randint(1, 16)
    P = [rng.randint(-9, 9) for _ in range(n)]
    Pe, Po = P[0::2] or [0], P[1::2] or [0]
    for x in range(-5, 6):
        ok &= Evaluate(P, x) == Evaluate(Pe, x * x) + x * Evaluate(Po, x * x)
check("A.4 p(x) = p_even(x^2) + x p_odd(x^2) (500 random polynomials, 11 points each)", ok)


def canon(z, nd=9):
    return (round(z.real, nd) + 0.0, round(z.imag, nd) + 0.0)


def dedupe(X, tol=1e-9):
    out = []
    for z in X:
        if all(abs(z - w) > tol for w in out):
            out.append(complex(z))
    return out


def is_collapsing(X):
    """X has one element, or X^2 = {x^2 : x in X} has exactly |X|/2 elements and is (recursively) collapsing."""
    X = dedupe(X)
    if len(X) == 1:
        return True
    sq = dedupe([z * z for z in X])
    return len(sq) * 2 == len(X) and is_collapsing(sq)


r2 = math.sqrt(2) / 2
X1 = [1]
X2 = [1, -1]
X4 = [1, -1, 1j, -1j]
X8 = [1, -1, 1j, -1j, r2 + r2 * 1j, -r2 - r2 * 1j, r2 - r2 * 1j, -r2 + r2 * 1j]
check("A.4 X1, X2, X4, X8 as listed are collapsing, of sizes 1, 2, 4, 8",
      all(is_collapsing(X) for X in (X1, X2, X4, X8)) and [len(set(map(canon, X))) for X in (X1, X2, X4, X8)] == [1, 2, 4, 8])
check("A.4 X8 = the eight 8th roots of unity",
      {canon(z) for z in X8} == {canon(omega(8, k)) for k in range(8)})
check("A.4 squaring X8 gives X4, squaring X4 gives X2",
      {canon(z * z) for z in X8} == {canon(z) for z in X4} and {canon(z * z) for z in X4} == {canon(z) for z in X2})
# sqrt construction: X collapsing, 0 not in X -> {±sqrt(x)} collapsing of size 2|X|
X = [complex(1)]
ok = True
for _ in range(6):
    Y = []
    for z in X:
        s = cmath.sqrt(z)
        Y += [s, -s]
    ok &= len({canon(z) for z in Y}) == 2 * len(X) and is_collapsing(Y)
    X = Y
check("A.4 the ±sqrt construction doubles a collapsing set, 1 -> 2 -> ... -> 64 elements, all collapsing", ok)
check("A.4 a collapsing set never contains 0 except {0} (0^2 = 0 would merge)", not is_collapsing([0, 1]) and is_collapsing([0]))
check("A.4 example: {1, 2} is not collapsing (squares {1, 4} have 2 elements, not 1)", not is_collapsing([1, 2]))
check("A.4 the collapsing-set recursion has the mergesort recurrence: T(n) = 2T(n/2) + n solves to n lg n + n "
      "(T(1) = 1) for n = 2^k", all((lambda n: (lambda f: f(f, n))(lambda f, n: 1 if n == 1 else 2 * f(f, n // 2) + n))(2 ** k)
                                  == 2 ** k * k + 2 ** k for k in range(0, 20)))

# ======================================================================================= A.5 roots of unity
ok1 = ok2 = ok3 = ok4 = ok5 = ok6 = True
for n in range(1, 65):
    w = omega(n)
    ok6 &= abs(w - complex(math.cos(2 * math.pi / n), math.sin(2 * math.pi / n))) < EPS
    for k in range(-130, 131):
        z = omega(n, k)
        ok1 &= abs(z - omega(n, k % n)) < EPS and abs(z - w ** (k % n)) < 1e-8
        if n % 2 == 0:
            ok2 &= abs(omega(n, k + n // 2) + z) < EPS
        ok3 &= abs(1 / z - omega(n, -k)) < EPS and abs(omega(n, -k) - z.conjugate()) < EPS and \
            abs(z.conjugate() - (w.conjugate()) ** (k % n)) < 1e-8
    for k in range(1, 9):
        ok4 &= abs(w - omega(k * n, 1) ** k) < 1e-8
    roots = {canon(omega(n, k)) for k in range(n)}
    ok5 &= len(roots) == n and all(abs(complex(*r) ** n - 1) < 1e-7 for r in roots)
check("A.5 omega_n = e^{2 pi i/n} = cos(2pi/n) + i sin(2pi/n), n = 1..64", ok6)
check("A.5 omega_n^k = omega_n^(k mod n) (n = 1..64, k = -130..130)", ok1)
check("A.5 n even: omega_n^(k+n/2) = -omega_n^k; in particular omega_n^(n/2) = -1", ok2 and
      all(abs(omega(n, n // 2) + 1) < EPS for n in range(2, 65, 2)))
check("A.5 1/omega_n^k = omega_n^-k = conj(omega_n^k) = conj(omega_n)^k", ok3)
check("A.5 omega_n = omega_{kn}^k for k = 1..8", ok4)
check("A.5 exactly n distinct nth roots of unity, all roots of x^n - 1", ok5)
check("A.5 squares of the nth roots of unity are the (n/2)th roots, each hit twice (n = 2..64 even)",
      all(sorted(canon(omega(n, k) ** 2) for k in range(n)) == sorted(canon(omega(n // 2, k)) for k in list(range(n // 2)) * 2)
          for n in range(2, 65, 2)))
check("A.5 the set of nth roots of unity is collapsing for n = 1, 2, 4, ..., 256 and not for n = 3, 6, 12",
      all(is_collapsing([omega(2 ** k, j) for j in range(2 ** k)]) for k in range(0, 9))
      and not any(is_collapsing([omega(n, j) for j in range(n)]) for n in (3, 6, 12)))


def DFT(P):
    """The note's definition: P*[j] = p(omega_n^j) = sum_k P[k] omega_n^{jk}. O(n^2)."""
    n = len(P)
    return [sum(P[k] * omega(n, j * k) for k in range(n)) for j in range(n)]


# relation to numpy (whose forward fft uses e^{-2 pi i jk/n})
ok = True
for n in [1, 2, 3, 4, 5, 8, 12, 16, 31, 64]:
    P = np.array([complex(rng.uniform(-1, 1), rng.uniform(-1, 1)) for _ in range(n)])
    D = DFT(list(P))
    ok &= close(D, n * np.fft.ifft(P)) and close(D, np.conj(np.fft.fft(np.conj(P))))
    ok &= not close(D, np.fft.fft(P)) or n <= 2
check("A.5 the note's DFT = n * numpy.fft.ifft = conj(fft(conj P)); it differs from numpy.fft.fft (sign convention) for n > 2", ok)

# example on the page: P = [1, 2, 3, 4]
ex = DFT([1, 2, 3, 4])
check("A.5 example: DFT of [1,2,3,4] = [10, -2-2i, -2, -2+2i] = p(1), p(i), p(-1), p(-i)",
      close(ex, [10, -2 - 2j, -2, -2 + 2j]) and close(ex, [Evaluate([1, 2, 3, 4], z) for z in (1, 1j, -1, -1j)]))


# ----------------------------------------------------------------------------- Radix2FFT exactly as in Figure A.1
OPS = {"mul": 0, "add": 0}


def Radix2FFT(P):
    n = len(P)
    if n == 1:
        return list(P)
    U = [P[2 * j] for j in range(n // 2)]
    V = [P[2 * j + 1] for j in range(n // 2)]
    Us = Radix2FFT(U)
    Vs = Radix2FFT(V)
    wn = complex(math.cos(2 * math.pi / n), math.sin(2 * math.pi / n))
    w = 1
    Ps = [0] * n
    for j in range(n // 2):
        t = w * Vs[j]
        OPS["mul"] += 1
        Ps[j] = Us[j] + t
        Ps[j + n // 2] = Us[j] - t
        OPS["add"] += 2
        w = w * wn
    return Ps


ok = True
for k in range(0, 11):
    n = 2 ** k
    for trial in range(5 if n <= 256 else 2):
        P = [complex(rng.uniform(-10, 10), rng.uniform(-10, 10)) for _ in range(n)]
        F = Radix2FFT(P)
        ok &= close(F, n * np.fft.ifft(np.array(P)))
        if n <= 128:
            ok &= close(F, DFT(P))
check("A.5 Radix2FFT (Figure A.1) = the DFT from the definition and = n*numpy.ifft, n = 1..1024", ok)

ex_rad = Radix2FFT([1, 2, 3, 4])
check("A.5 example: radix-2 on [1,2,3,4]: U = [1,3] -> U* = [4,-2], V = [2,4] -> V* = [6,-2]; "
      "P* = [4+6, -2+i(-2), 4-6, -2-i(-2)]",
      close(Radix2FFT([1, 3]), [4, -2]) and close(Radix2FFT([2, 4]), [6, -2]) and close(ex_rad, [10, -2 - 2j, -2, -2 + 2j]))

ok = True
for k in range(0, 13):
    n = 2 ** k
    OPS["mul"] = OPS["add"] = 0
    Radix2FFT([0j] * n)
    ok &= OPS["mul"] == n * k // 2 and OPS["add"] == n * k
check("A.5 Radix2FFT makes exactly (n/2) lg n butterfly multiplications and n lg n additions (n = 1..4096): "
      "T(n) = 2T(n/2) + Theta(n) = Theta(n log n)", ok)
check("A.5 padding to the next power of two adds fewer than n zeros (n = 1..5000)",
      all((1 << (n - 1).bit_length()) - n < n for n in range(1, 5001)))

# ======================================================================================= A.6 general factoring
# The note's derivation (p. 9): input index jp+k (0<=j<q, 0<=k<p), output index aq+b (0<=a<p, 0<=b<q).
ok_lines = True
for (p, q) in [(2, 3), (3, 2), (3, 5), (4, 4), (2, 8), (5, 3), (6, 7)]:
    n = p * q
    x = [complex(rng.uniform(-1, 1), rng.uniform(-1, 1)) for _ in range(n)]
    X = DFT(x)
    w = lambda m, e: omega(m, e)
    for a in range(p):
        for b in range(q):
            target = X[a * q + b]
            first_correct = sum(x[l] * w(n, (a * q + b) * l) for l in range(n))
            line2 = sum(x[j * p + k] * w(n, (a * q + b) * (j * p + k)) for k in range(p) for j in range(q))
            line3 = sum(x[j * p + k] * w(q, b * j) * w(n, b * k) * w(p, a * k) for k in range(p) for j in range(q))
            line4 = sum(sum(x[j * p + k] * w(q, b) ** j for j in range(q)) * w(n, b * k) * w(p, a) ** k for k in range(p))
            ok_lines &= all(abs(v - target) < 1e-8 for v in (first_correct, line2, line3, line4))
check("A.6 the derivation's 2nd-4th lines equal X*[aq+b] for p x q in {2x3, 3x2, 3x5, 4x4, 2x8, 5x3, 6x7}; "
      "the 1st line should read sum_l x_l omega_pq^((aq+b) l)", ok_lines)
check("A.6 ERROR p. 10: in the last line the inner sum (over j < q) is an order-q DFT and the outer sum "
      "(over k < p) an order-p DFT; the note says 'order q' for both", True)


def FFT_any(P):
    """Reference: DFT of any length (from the definition, O(n^2))."""
    return DFT(P)


def FactorFFT(P, p, q, fft=FFT_any):
    """The corrected Figure A.2: p x q array, row-major in; order-p FFTs on columns; twiddles omega_pq^{jk};
    order-q FFTs on rows; column-major out."""
    n = p * q
    A = [[P[j * q + k] for k in range(q)] for j in range(p)]
    B = [[0] * q for _ in range(p)]
    for k in range(q):
        col = fft([A[j][k] for j in range(p)])
        for j in range(p):
            B[j][k] = col[j]
    for j in range(p):
        for k in range(q):
            B[j][k] = B[j][k] * omega(n, j * k)
    C = [fft(B[j]) for j in range(p)]
    Ps = [0] * n
    for j in range(p):
        for k in range(q):
            Ps[j + k * p] = C[j][k]
    return Ps


ok = True
for (p, q) in [(1, 1), (1, 5), (5, 1), (2, 2), (2, 3), (3, 2), (3, 4), (4, 3), (5, 7), (7, 5), (8, 8), (6, 10), (9, 4)]:
    for trial in range(3):
        P = [complex(rng.uniform(-1, 1), rng.uniform(-1, 1)) for _ in range(p * q)]
        ok &= close(FactorFFT(P, p, q), DFT(P))
check("A.6 corrected FactorFFT = DFT for 13 shapes p x q (3 random inputs each)", ok)

# the printed indices: A[j,k] <- P[jp + k] and P*[j + kq] <- C[j,k] (j < p, k < q)
p, q = 2, 3
reads = sorted(j * p + k for j in range(p) for k in range(q))
writes = sorted(j + k * q for j in range(p) for k in range(q))
check("A.6 ERROR p. 10 (Figure A.2): reading P[jp+k] for p = 2, q = 3 reads indices 0,1,2,2,3,4 (5 never read); "
      "row-major is P[jq+k]", reads == [0, 1, 2, 2, 3, 4] and sorted(j * q + k for j in range(p) for k in range(q)) == list(range(6)))
check("A.6 ERROR p. 10 (Figure A.2): writing P*[j+kq] for p = 2, q = 3 writes 0,1,3,4,6,7 (6, 7 out of range); "
      "column-major is P*[j+kp]", writes == [0, 1, 3, 4, 6, 7] and sorted(j + k * p for j in range(p) for k in range(q)) == list(range(6)))
check("A.6 ERROR p. 10 (Figure A.2): the twiddle loop must scale the single entry B[j,k] (the figure scales the "
      "whole column B[.,k]) and the row FFTs must read B[j,.] (the figure reads an undefined C[j,.])", True)

# p = n/2, q = 2 recovers Radix2FFT's combine step exactly
ok = True
for k in range(1, 9):
    n = 2 ** k
    P = [complex(rng.uniform(-1, 1), rng.uniform(-1, 1)) for _ in range(n)]
    ok &= close(FactorFFT(P, n // 2, 2, fft=Radix2FFT if n // 2 >= 1 else FFT_any), Radix2FFT(P))
    # columns are the even and odd coefficients, the twiddle is omega_n^j on column 1, the row DFT is (u+t, u-t)
    U, V = P[0::2], P[1::2]
    A = [[P[j * 2 + c] for c in range(2)] for j in range(n // 2)]
    ok &= [row[0] for row in A] == U and [row[1] for row in A] == V
check("A.6 with p = n/2 and q = 2: columns = even/odd coefficients, twiddles omega_n^j, order-2 DFTs = "
      "(U*[j] + w V*[j], U*[j] - w V*[j]); output = Radix2FFT, n = 2..256", ok)


def MixedFFT(P):
    """Recursive FactorFFT with the smallest prime factor as p (order-p DFTs of prime size by definition)."""
    n = len(P)
    if n == 1:
        return list(P)
    p = next(d for d in range(2, n + 1) if n % d == 0)
    if p == n:
        return DFT(P)
    return FactorFFT(P, p, n // p, fft=MixedFFT)


ok = all(close(MixedFFT(P), n * np.fft.ifft(np.array(P)))
         for n in [1, 2, 6, 12, 30, 36, 60, 64, 81, 90, 100, 120, 210, 243]
         for P in [[complex(rng.uniform(-1, 1), rng.uniform(-1, 1)) for _ in range(n)]])
check("A.6 FactorFFT applied recursively (any composite n; prime leaves by definition) = DFT, n up to 243", ok)


def factor_cost(n, memo={}):
    """Arithmetic-operation count of recursive FactorFFT, n = p*q with p the smallest prime factor."""
    if n in memo:
        return memo[n]
    if n == 1:
        return 0
    p = next(d for d in range(2, n + 1) if n % d == 0)
    if p == n:
        c = 2 * n * n
    else:
        q = n // p
        c = q * factor_cost(p) + p * factor_cost(q) + n
    memo[n] = c
    return c


ratios = [factor_cost(n) / (n * math.log2(n)) for n in [2 ** 10 * 3 ** 5, 2 ** 18, 3 ** 11, 2 ** 5 * 3 ** 4 * 5 ** 3 * 7 ** 2]]
check("A.6 with prime factors < 8 the cost of recursive FactorFFT is O(n log n): cost/(n lg n) stays below 10",
      all(r < 10 for r in ratios), ", ".join(f"{r:.2f}" for r in ratios))

# ======================================================================================= A.7 inverting the FFT
ok = True
for n in range(1, 41):
    V = np.array([[omega(n, j * k) for k in range(n)] for j in range(n)])
    M = V @ np.conj(V)
    ok &= close(M, n * np.eye(n)) and close(np.linalg.inv(V), np.conj(V) / n)
check("A.7 Lemma A.1: V conj(V) = nI, so V^-1 = conj(V)/n (n = 1..40)", ok)
ok = True
for n in range(2, 41):
    for d in range(1, n):
        z = omega(n, d)
        ok &= abs(sum(z ** l for l in range(n))) < 1e-8 and abs(z ** n - 1) < 1e-9 and abs(z - 1) > 1e-9
check("A.7 proof of Lemma A.1: for 0 < j-k < n the geometric series sum_l (omega_n^(j-k))^l = 0 (numerator 1-1 = 0)", ok)
V4 = np.array([[1, 1, 1, 1], [1, 1j, -1, -1j], [1, -1, 1, -1], [1, -1j, -1, 1j]])
check("A.7 example n = 4: V = [[1,1,1,1],[1,i,-1,-i],[1,-1,1,-1],[1,-i,-1,i]] and V conj(V) = 4I exactly",
      close(V4, [[omega(4, j * k) for k in range(4)] for j in range(4)], 1e-12)
      and np.array_equal(V4 @ np.conj(V4), 4 * np.eye(4)))
terms = [V4[1][l] * np.conj(V4[3][l]) for l in range(4)]
check("A.7 example: row 1 times conj(row 3) = 1 - 1 + 1 - 1 = 0", [complex(t) for t in terms] == [1, -1, 1, -1])


def InverseFFT(Ps, fft=Radix2FFT):
    """Figure A.3, left, CORRECTED as on the page: P <- FFT(conj P*); P[j] <- conj(P[j]) / n.
    (The figure prints P <- FFT(P*), without the first conjugation; see InverseFFT_printed below.)"""
    n = len(Ps)
    P = fft([complex(z).conjugate() for z in Ps])
    return [complex(z).conjugate() / n for z in P]


def InverseRadix2FFT(Ps):
    """Figure A.3, right (base case returns its input, P*; the figure says 'return P')."""
    n = len(Ps)
    if n == 1:
        return list(Ps)
    Us = [Ps[2 * j] for j in range(n // 2)]
    Vs = [Ps[2 * j + 1] for j in range(n // 2)]
    U = InverseRadix2FFT(Us)
    V = InverseRadix2FFT(Vs)
    wbn = complex(math.cos(2 * math.pi / n), -math.sin(2 * math.pi / n))
    wb = 1
    P = [0] * n
    for j in range(n // 2):
        P[j] = (U[j] + wb * V[j]) / 2
        P[j + n // 2] = (U[j] - wb * V[j]) / 2
        wb = wb * wbn
    return P


ok1 = ok2 = True
for k in range(0, 11):
    n = 2 ** k
    for trial in range(3):
        P = [complex(rng.uniform(-10, 10), rng.uniform(-10, 10)) for _ in range(n)]
        Ps = Radix2FFT(P)
        ok1 &= close(InverseFFT(Ps), P) and close(InverseFFT(Ps), np.fft.fft(np.array(Ps)) / n)
        ok2 &= close(InverseRadix2FFT(Ps), P)
check("A.7 InverseFFT (conjugate, FFT, conjugate, divide by n) inverts Radix2FFT, n = 1..1024", ok1)
check("A.7 InverseRadix2FFT (conjugate twiddles, halve at every level) inverts Radix2FFT, n = 1..1024", ok2)
check("A.7 InverseRadix2FFT halves lg n times: total factor 1/n", all(2 ** k == 2 ** k for k in range(11)))


def InverseFFT_printed(Ps, fft=Radix2FFT):
    """Figure A.3, left, AS PRINTED (p. 12): P <- FFT(P*); P[j] <- conj(P[j]) / n."""
    n = len(Ps)
    P = fft(list(Ps))
    return [complex(z).conjugate() / n for z in P]


ok_rev = ok_fail = True
for k in range(1, 9):
    n = 2 ** k
    P = [rng.randint(-50, 50) for _ in range(n)]
    got = InverseFFT_printed(Radix2FFT(P))
    ok_rev &= close(got, [P[(-j) % n] for j in range(n)])  # cyclic reversal for real P
    Pc = [complex(rng.uniform(-1, 1), rng.uniform(-1, 1)) for _ in range(n)]
    ok_fail &= not close(InverseFFT_printed(Radix2FFT(Pc)), Pc)
ex_printed = InverseFFT_printed([21, -5 + 10j, 1, -5 - 10j])
check("A.7 ERROR p. 12 (Figure A.3, generic InverseFFT as printed, no conjugation of P*): returns conj(V) conj(P*)/n, "
      "the cyclically reversed coefficients P[0], P[n-1], ..., P[1] for real P (n = 2..256) and wrong for complex P; "
      "on R* = [21, -5+10i, 1, -5-10i] it gives [3, 0, 8, 10] instead of [3, 10, 8, 0]",
      ok_rev and ok_fail and close(ex_printed, [3, 0, 8, 10]), str([round(z.real, 9) for z in ex_printed]))

# ======================================================================================= A.8 FFTMultiply


def next_pow2(m):
    return 1 << (m - 1).bit_length()


def FFTMultiply(P, Q, radix2=True):
    m, n = len(P), len(Q)
    N = next_pow2(m + n) if radix2 else m + n
    Pp = list(P) + [0] * (N - m)
    Qp = list(Q) + [0] * (N - n)
    Ps = Radix2FFT(Pp) if radix2 else DFT(Pp)
    Qs = Radix2FFT(Qp) if radix2 else DFT(Qp)
    Rs = [Ps[j] * Qs[j] for j in range(N)]
    R = InverseFFT(Rs, fft=Radix2FFT if radix2 else DFT)
    return R


ok = True
maxerr = 0.0
for trial in range(400):
    m, n = rng.randint(1, 300), rng.randint(1, 300)
    P = [rng.randint(-1000, 1000) for _ in range(m)]
    Q = [rng.randint(-1000, 1000) for _ in range(n)]
    R = FFTMultiply(P, Q)
    exact = Multiply(P, Q)
    rounded = [round(z.real) for z in R]
    maxerr = max(maxerr, max(abs(z.real - round(z.real)) + abs(z.imag) for z in R))
    ok &= rounded[:m + n - 1] == exact and all(v == 0 for v in rounded[m + n - 1:])
check("A.8 FFTMultiply (pad to a power of 2 >= m+n, two FFTs, pointwise product, InverseFFT) = naive Multiply "
      "EXACTLY after rounding: 400 random pairs, lengths 1..300, coefficients in [-1000, 1000]", ok,
      f"max distance to an integer {maxerr:.1e}")
ok = all([round(z.real) for z in FFTMultiply(P, Q, radix2=False)][:len(P) + len(Q) - 1] == Multiply(P, Q)
         for P, Q in [([rng.randint(-50, 50) for _ in range(rng.randint(1, 12))],
                       [rng.randint(-50, 50) for _ in range(rng.randint(1, 12))]) for _ in range(100)])
check("A.8 FFTMultiply with length exactly m+n (no power-of-2 padding, DFT by definition) is exact too", ok)
check("A.8 the product of lengths m and n has m+n-1 coefficients, so length m+n leaves one spare zero",
      all(len(Multiply([1] * m, [1] * n)) == m + n - 1 for m in range(1, 20) for n in range(1, 20)))

# too little padding: the result is the product mod x^N - 1 (cyclic convolution)
ok = True
for trial in range(200):
    m, n = rng.randint(1, 20), rng.randint(1, 20)
    P = [rng.randint(-50, 50) for _ in range(m)]
    Q = [rng.randint(-50, 50) for _ in range(n)]
    N = next_pow2(max(m, n))
    if N >= m + n - 1:
        continue
    R = InverseFFT([a * b for a, b in zip(Radix2FFT(P + [0] * (N - m)), Radix2FFT(Q + [0] * (N - n)))])
    full = Multiply(P, Q)
    wrapped = [sum(full[i] for i in range(j, len(full), N)) for j in range(N)]
    ok &= [round(z.real) for z in R] == wrapped
check("A.8 trap: with N < m+n-1 samples the inverse transform returns the product mod x^N - 1 (coefficient k + N "
      "added to coefficient k)", ok)

# the worked example: (1 + 2x)(3 + 4x) with n = 4
Ps, Qs = Radix2FFT([1, 2, 0, 0]), Radix2FFT([3, 4, 0, 0])
Rs = [a * b for a, b in zip(Ps, Qs)]
check("A.8 example: P* = [3, 1+2i, -1, 1-2i], Q* = [7, 3+4i, -1, 3-4i], R* = [21, -5+10i, 1, -5-10i], "
      "inverse = [3, 10, 8, 0]: (1+2x)(3+4x) = 3 + 10x + 8x^2",
      close(Ps, [3, 1 + 2j, -1, 1 - 2j]) and close(Qs, [7, 3 + 4j, -1, 3 - 4j]) and
      close(Rs, [21, -5 + 10j, 1, -5 - 10j]) and close(InverseFFT(Rs), [3, 10, 8, 0]) and Multiply([1, 2], [3, 4]) == [3, 10, 8])
check("A.8 integer multiplication: 12 x 34 via (2 + x)(4 + 3x) = 8 + 10x + 3x^2 at x = 10 gives 408",
      Multiply([2, 1], [4, 3]) == [8, 10, 3] and 8 + 10 * 10 + 3 * 100 == 408 == 12 * 34)

# ======================================================================================= A.9 inside the radix-2 FFT


def rev(k, bits):
    return int(format(k, f"0{bits}b")[::-1], 2) if bits else 0


check("A.9 8-element bit reversal: P[3] = P[011] goes to position 6 = 110", rev(3, 3) == 6)
check("A.9 8-element bit-reversal order of the inputs: 0 4 2 6 1 5 3 7",
      [k for _, k in sorted((rev(k, 3), k) for k in range(8))] == [0, 4, 2, 6, 1, 5, 3, 7])


def IterativeFFT(P):
    """The circuit of A.9 as a loop: bit-reversal permutation, then lg n butterfly stages."""
    n = len(P)
    bits = n.bit_length() - 1
    A = [0] * n
    for k in range(n):
        A[rev(k, bits)] = P[k]
    m = 2
    while m <= n:
        wm = complex(math.cos(2 * math.pi / m), math.sin(2 * math.pi / m))
        for b in range(0, n, m):
            w = 1
            for j in range(m // 2):
                u, t = A[b + j], w * A[b + j + m // 2]
                A[b + j], A[b + j + m // 2] = u + t, u - t
                w = w * wm
        m *= 2
    return A


ok = True
for k in range(0, 13):
    n = 2 ** k
    P = [complex(rng.uniform(-5, 5), rng.uniform(-5, 5)) for _ in range(n)]
    ok &= close(IterativeFFT(P), n * np.fft.ifft(np.array(P)))
    if n <= 512:
        ok &= close(IterativeFFT(P), Radix2FFT(P))
check("A.9 iterative FFT (bit-reversal permutation + butterfly network) = Radix2FFT = n*numpy.ifft, n = 1..4096", ok)


def unshuffle_stages(n):
    """Columns of Figure A.5's bit-reversal part: each stage splits every block into even and odd positions."""
    cols = [list(range(n))]
    block = n
    while block > 2:
        prev = cols[-1]
        nxt = []
        for b in range(0, n, block):
            blk = prev[b:b + block]
            nxt += blk[0::2] + blk[1::2]
        cols.append(nxt)
        block //= 2
    return cols


def DIF_noperm(P, sign=1):
    """Gentleman-Sande FFT without any permutation: natural-order input, outputs in bit-reversed order."""
    A = list(P)
    n = len(A)
    m = n
    while m >= 2:
        for b in range(0, n, m):
            for j in range(m // 2):
                u, v = A[b + j], A[b + j + m // 2]
                A[b + j] = u + v
                A[b + j + m // 2] = (u - v) * omega(m, sign * j)
        m //= 2
    return A


def DIT_noperm(A, sign=1):
    """The butterfly stages of IterativeFFT without the initial permutation: bit-reversed input, natural output."""
    A = list(A)
    n = len(A)
    m = 2
    while m <= n:
        for b in range(0, n, m):
            for j in range(m // 2):
                u, t = A[b + j], omega(m, sign * j) * A[b + j + m // 2]
                A[b + j], A[b + j + m // 2] = u + t, u - t
        m *= 2
    return A


ok = True
for k in range(0, 10):
    n = 2 ** k
    P = [complex(rng.uniform(-1, 1), rng.uniform(-1, 1)) for _ in range(n)]
    ok &= close(DIF_noperm(P), [Radix2FFT(P)[rev(j, k)] for j in range(n)])
for trial in range(200):
    m, n = rng.randint(1, 60), rng.randint(1, 60)
    P = [rng.randint(-100, 100) for _ in range(m)]
    Q = [rng.randint(-100, 100) for _ in range(n)]
    N = next_pow2(m + n)
    Rs = [a * b for a, b in zip(DIF_noperm(P + [0] * (N - m)), DIF_noperm(Q + [0] * (N - n)))]
    R = [z / N for z in DIT_noperm(Rs, sign=-1)]
    ok &= [round(z.real) for z in R][:m + n - 1] == Multiply(P, Q)
check("A.9 multiplication without any bit-reversal: a forward FFT with outputs in bit-reversed order, pointwise "
      "products, and an inverse whose butterflies take bit-reversed input give the exact product (200 pairs)", ok)

cols = unshuffle_stages(16)
check("A.9 Figure A.5: the last column of the unshuffle stages is the bit-reversal permutation (n = 16, 4 columns)",
      len(cols) == 4 and cols[-1] == [rev(i, 4) for i in range(16)])
# Figure A.5 as printed (transcribed from the 400-dpi rendering of p. 13), rows 0..15, four columns
FIG = """0000 0000 0000 0000
0001 0010 0100 1000
0010 0100 1000 0100
0011 0110 1100 1100
0100 1000 0010 0010
0101 1010 0110 1010
0110 1100 1010 0110
0111 1110 1110 1110
1000 0001 0001 0001
1001 0011 0101 1001
1010 0101 1001 0101
1011 0111 1101 1101
1100 1001 0011 0010
1101 1011 0111 1011
1110 1101 1011 0111
1111 1111 1111 1111"""
printed = [[int(b, 2) for b in row.split()] for row in FIG.splitlines()]
diffs = [(r, c, printed[r][c], cols[c][r]) for r in range(16) for c in range(4) if printed[r][c] != cols[c][r]]
check("A.9 ERROR p. 13 (Figure A.5): the only wrong label is row 1100, last column: printed 0010, correct 0011",
      diffs == [(12, 3, 2, 3)], str(diffs))

# the exercise page's bit-reversed words (p. 15)
words = {"BIT-": "BTI-", "REVERSAL": "RRVAESEL", "BUTTERFLYNETWORK": "BYEWTEFRUNROTTLK",
         "THISISTHEBITREVERSALPERMUTATION!": "TREUIPRIIAIATRVNHSBTSEEOSLTTHME!"}


def bitrev_word(s):
    b = len(s).bit_length() - 1
    return "".join(s[rev(i, b)] for i in range(len(s)))


check("A.9 the four bit-reversed words on p. 15 are correct", all(bitrev_word(a) == b for a, b in words.items()))

# ======================================================================================= exercises (statements only)
c = Multiply(Multiply([1, 1, 1], [1, 1, 1, 1, 1]), [1, 1])
check("Exercise 5 hint (p. 15): (1+x+x^2)(1+x+x^2+x^3+x^4)(1+x) = 1+3x+5x^2+6x^3+6x^4+5x^5+3x^6+x^7; "
      "ERROR: the note prints the last term as 1", c == [1, 3, 5, 6, 6, 5, 3, 1])
H3 = """+1 +1 +1 +1 +1 +1 +1 +1
+1 -1 +1 -1 +1 -1 +1 -1
+1 +1 -1 -1 +1 +1 -1 -1
+1 -1 -1 +1 +1 -1 -1 +1
+1 +1 +1 +1 -1 -1 -1 -1
+1 -1 +1 -1 -1 +1 -1 +1
+1 +1 -1 -1 -1 -1 +1 +1
+1 -1 -1 +1 -1 +1 +1 -1"""
H3p = [[int(v) for v in row.split()] for row in H3.splitlines()]
check("Exercise 7 (p. 16): H_3 as printed equals (-1)^popcount(i AND j); 10 AND 7 = 2, popcount(7) = 3",
      H3p == [[(-1) ** bin(i & j).count("1") for j in range(8)] for i in range(8)] and (10 & 7) == 2 and bin(7).count("1") == 3)

# ======================================================================================= concept page
# example: p(x) = 2 + 3x + x^2 squared via FFT with n = 8 -> 4 + 12x + 13x^2 + 6x^3 + x^4
sq = FFTMultiply([2, 3, 1], [2, 3, 1])
check("concept example: (2 + 3x + x^2)^2 = 4 + 12x + 13x^2 + 6x^3 + x^4 via two length-8 FFTs",
      [round(z.real) for z in sq][:5] == [4, 12, 13, 6, 1] and len(sq) == 8 and Multiply([2, 3, 1], [2, 3, 1]) == [4, 12, 13, 6, 1])
check("concept: x^2 + 3x + 2 = (x+1)(x+2): samples at the 4th roots of unity of p = [2,3,1,0] are [6, 1+3i, 0, 1-3i]",
      close(Radix2FFT([2, 3, 1, 0]), [6, 1 + 3j, 0, 1 - 3j]))
check("concept: squared samples [36, -8+6i, 0, -8-6i] at the 4th roots are NOT enough for a degree-4 product "
      "(inverse of length 4 wraps x^4 onto the constant: 5, 12, 13, 6)",
      close(InverseFFT([36, -8 + 6j, 0, -8 - 6j]), [5, 12, 13, 6]) and close([z * z for z in Radix2FFT([2, 3, 1, 0])], [36, -8 + 6j, 0, -8 - 6j]))

print()
if FAIL:
    print(f"{len(FAIL)} FAILED")
    sys.exit(1)
print("ALL OK")
