#!/usr/bin/env python3
"""Checks for content/4-lecture-notes/99-solving-recurrences.md (Erickson, Appendix II "Solving Recurrences")
and the concept page content/concepts/linear-recurrences.md.

Every recurrence on the pages is computed directly and compared with its stated solution:
  * exact closed forms with exact arithmetic (int, Fraction, and an exact field Q(sqrt 5) for Fibonacci-type
    formulas) for n up to large values;
  * Theta-claims by ratios T(n)/g(n) that must settle (relative spread of the last ratios below a stated
    tolerance) and stay inside the stated bounds;
  * recursion-tree level sums by building the levels;
  * annihilator / characteristic-polynomial solutions by fitting the constants to the base cases with exact
    linear algebra and checking the result for every n in range;
  * domain / range / difference transformations by computing both sides;
  * Akra-Bazzi exponents by bisection and the predicted growth by ratios.
Claims of the note that are wrong are checked to BE wrong (so the page's corrections are justified)."""
import math
import random
from decimal import Decimal, getcontext
from fractions import Fraction as Fr
from functools import lru_cache

import numpy as np
from scipy import integrate

FAIL = []


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAIL.append(name)


rng = random.Random(99)
lg = math.log2


def settles(vals, tol):
    """vals: ratios for growing n. Positive, finite, and the last four within relative spread tol."""
    tail = vals[-4:]
    ok = all(v > 0 and math.isfinite(v) for v in vals) and (max(tail) - min(tail)) / max(tail) < tol
    return ok, [round(v, 5) for v in tail]


def fib(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def H(n):
    return sum(Fr(1, i) for i in range(1, n + 1))


# ---------------------------------------------------------------- exact arithmetic in Q(sqrt 5)
class Q5:
    """p + q*sqrt(5) with rational p, q."""

    def __init__(self, p, q=0):
        self.p, self.q = Fr(p), Fr(q)

    def __add__(s, o):
        o = o if isinstance(o, Q5) else Q5(o)
        return Q5(s.p + o.p, s.q + o.q)

    __radd__ = __add__

    def __neg__(s):
        return Q5(-s.p, -s.q)

    def __sub__(s, o):
        return s + (-(o if isinstance(o, Q5) else Q5(o)))

    def __rsub__(s, o):
        return Q5(o) - s

    def __mul__(s, o):
        o = o if isinstance(o, Q5) else Q5(o)
        return Q5(s.p * o.p + 5 * s.q * o.q, s.p * o.q + s.q * o.p)

    __rmul__ = __mul__

    def inv(s):
        d = s.p * s.p - 5 * s.q * s.q
        return Q5(s.p / d, -s.q / d)

    def __truediv__(s, o):
        o = o if isinstance(o, Q5) else Q5(o)
        return s * o.inv()

    def __pow__(s, k):
        if k < 0:
            return s.inv() ** (-k)
        r, b = Q5(1), s
        while k:
            if k & 1:
                r = r * b
            b = b * b
            k >>= 1
        return r

    def __eq__(s, o):
        o = o if isinstance(o, Q5) else Q5(o)
        return s.p == o.p and s.q == o.q

    def __float__(s):
        return float(s.p) + float(s.q) * math.sqrt(5)


SQ5 = Q5(0, 1)
PHI = Q5(Fr(1, 2), Fr(1, 2))
PHIH = Q5(Fr(1, 2), Fr(-1, 2))
phi = (1 + math.sqrt(5)) / 2

# =====================================================================================================
# 1  Introduction: three recurrences for the identity function
# =====================================================================================================
N = 5000
f1 = [0] * (N + 1)
for n in range(1, N + 1):
    f1[n] = f1[n - 1] + 1
f2 = [0, 1] + [0] * (N - 1)
for n in range(2, N + 1):
    f2[n] = f2[n // 2] + f2[(n + 1) // 2]
f3 = [0] * (N + 1)
for n in range(1, N + 1):
    f3[n] = 2 * f3[n // 2] if n % 2 == 0 else f3[n - 1] + 1
check("§1 f(n)=f(n-1)+1, f(floor(n/2))+f(ceil(n/2)) and the even/odd recurrence all give f(n) = n, n <= 5000",
      f1 == f2 == f3 == list(range(N + 1)))

# =====================================================================================================
# 2.1 Tower of Hanoi
# =====================================================================================================
T = [0]
for n in range(1, 301):
    T.append(2 * T[-1] + 1)
check("§2.1 Hanoi values T(0..6) = 0,1,3,7,15,31,63", T[:7] == [0, 1, 3, 7, 15, 31, 63])
check("§2.1 Hanoi T(n) = 2^n - 1 for n <= 300", all(T[n] == 2 ** n - 1 for n in range(301)))
check("§2.1 unrolled k times: T(n) = 2^k T(n-k) + 2^k - 1 for all 0 <= k <= n <= 80",
      all(T[n] == 2 ** k * T[n - k] + 2 ** k - 1 for n in range(81) for k in range(n + 1)))

# =====================================================================================================
# 2.2 Fibonacci numbers: guess alpha*c^n
# =====================================================================================================
getcontext().prec = 500
PHI_D = (1 + Decimal(5).sqrt()) / 2
check("§2.2 c^2 - c - 1 >= 0 for c >= 1 exactly when c >= phi = 1.618034 (the larger root)",
      abs(phi - 1.618034) < 5e-7 and abs(phi * phi - phi - 1) < 1e-12
      and all((c * c - c - 1 >= 0) == (c >= phi) for c in np.linspace(1, 3, 2001)))
check("§2.2 the other root (1-sqrt5)/2 has smaller absolute value", abs((1 - math.sqrt(5)) / 2) < phi)
check("§2.2 F0/phi^0 = 0, F1/phi = 0.618034, F2/phi^2 = 0.381966",
      abs(1 / phi - 0.618034) < 5e-7 and abs(1 / phi ** 2 - 0.381966) < 5e-7)
check("§2.2 upper bound F_n <= phi^(n-1) for 0 <= n <= 1000",
      all(Decimal(fib(n)) <= PHI_D ** (n - 1) for n in range(1001)))
check("§2.2 lower bound F_n >= phi^(n-2) for 1 <= n <= 1000 (fails at n = 0)",
      all(Decimal(fib(n)) >= PHI_D ** (n - 2) for n in range(1, 1001)) and not (0 >= PHI_D ** -2))
r = [float(Decimal(fib(n)) / PHI_D ** n) for n in range(10, 1001, 30)]
ok, tl = settles(r, 1e-9)
check("§2.2 F_n = Theta(phi^n): F_n/phi^n settles (tol 1e-9) at 1/sqrt5", ok and abs(r[-1] - 1 / math.sqrt(5)) < 1e-12,
      str(tl))

# =====================================================================================================
# 2.3 Mergesort (powers of 2)
# =====================================================================================================
@lru_cache(None)
def ms(n):
    return 1 if n == 1 else 2 * ms(n // 2) + n


check("§2.3 T(n) = 2T(n/2) + n, T(1) = 1: T(n) = n lg n + n for n = 2^k, k <= 200",
      all(ms(2 ** k) == 2 ** k * k + 2 ** k for k in range(201)))
check("§2.3 unrolled: T(n) = 2^j T(n/2^j) + j n for all 0 <= j <= k <= 60",
      all(ms(2 ** k) == 2 ** j * ms(2 ** (k - j)) + j * 2 ** k for k in range(61) for j in range(k + 1)))

# =====================================================================================================
# 2.4 T(n) = sqrt(n) T(sqrt(n)) + n, n = 2^(2^k)
# =====================================================================================================
@lru_cache(None)
def ugly(k):      # T(2^(2^k)), base T(2) = 2
    if k == 0:
        return 2
    n, rt = 2 ** (2 ** k), 2 ** (2 ** (k - 1))
    return rt * ugly(k - 1) + n


check("§2.4 T(n) = sqrt(n) T(sqrt n) + n with T(2) = 2: T(n) = n(lg lg n + 1) at n = 2^(2^k), k <= 12",
      all(ugly(k) == 2 ** (2 ** k) * (k + 1) for k in range(13)))
# the four guesses: the algebra of each inductive step, at random n and constants
ok = True
for _ in range(2000):
    n = 2 ** rng.uniform(4, 200)
    a = rng.uniform(0.01, 10)
    s = math.sqrt(n)
    ok &= math.isclose(s * a * s * lg(s) + n, (a / 2) * n * lg(n) + n, rel_tol=1e-9)
    ok &= math.isclose(s * a * s * math.sqrt(lg(s)) + n, (a / math.sqrt(2)) * n * math.sqrt(lg(n)) + n, rel_tol=1e-9)
    ok &= math.isclose(s * a * s * lg(lg(s)) + n, a * n * lg(lg(n)) - a * n + n, rel_tol=1e-9)
    ok &= ((a / 2) * n * lg(n) + n <= a * n * lg(n) * (1 + 1e-12)) == (n >= 2 ** (2 / a) * (1 - 1e-9))
check("§2.4 inductive-step algebra of the guesses n lg n, n sqrt(lg n), n lg lg n; the n lg n step works iff n >= 2^(2/a)", ok)
ok = all((a * n * lg(lg(n)) - a * n + n <= a * n * lg(lg(n))) == (a >= 1)
         for a in (0.5, 0.99, 1, 1.5, 3) for n in (2 ** 4, 2 ** 64))
check("§2.4 upper step for n lg lg n works iff a >= 1; lower step (same algebra) iff b <= 1", ok)
ks = list(range(3, 13))
check("§2.4 T/(n lg n) -> 0, T/n -> infinity, T/(n sqrt(lg n)) -> 0 (decreasing / increasing on n = 2^2^k, k = 3..12)",
      all(ugly(k + 1) / (2 ** 2 ** (k + 1) * 2 ** (k + 1)) < ugly(k) / (2 ** 2 ** k * 2 ** k) for k in ks[:-1])
      and all(ugly(k + 1) / 2 ** 2 ** (k + 1) > ugly(k) / 2 ** 2 ** k for k in ks[:-1])
      and all((k + 2) / math.sqrt(2 ** (k + 1)) < (k + 1) / math.sqrt(2 ** k) for k in ks[:-1]))
# the recursion tree for n = 2^16: level i has n^(1 - 2^-i) nodes of size n^(2^-i)
n = 2 ** 16
lev = []
cnt, size = 1, n
while size >= 2:
    lev.append((cnt, size))
    if size == 2:
        break
    s = math.isqrt(size)
    cnt, size = cnt * s, s
check("§2.4/§3 tree of sqrt(n) T(sqrt n) + n at n = 65536: levels (1, 65536), (256, 256), (4096, 16), (16384, 4), "
      "(32768, 2), every level sums to n, lg lg n = 4 levels below the root",
      lev == [(1, 65536), (256, 256), (4096, 16), (16384, 4), (32768, 2)] and all(c * s == n for c, s in lev)
      and len(lev) - 1 == int(lg(lg(n))), str(lev))

# =====================================================================================================
# 3 Recursion trees
# =====================================================================================================
def tree_sum(a, b, f, k):
    """Sum over levels of a^i f(b^(k-i)) for n = b^k with T(1) = f(1)."""
    return sum(a ** i * f(b ** (k - i)) for i in range(k + 1))


def rec(a, b, f, k):
    t = f(1)
    for j in range(1, k + 1):
        t = a * t + f(b ** j)
    return t


ok = all(tree_sum(a, b, f, k) == rec(a, b, f, k)
         for a in (1, 2, 3, 4, 7) for b in (2, 3, 4) for f in (lambda m: m, lambda m: m * m, lambda m: 1)
         for k in range(0, 25))
check("§3 (Sigma): T(n) = sum_i a^i f(n/b^i) equals the recurrence at n = b^k (a in 1,2,3,4,7; b in 2,3,4; f = n, n^2, 1)", ok)
check("§3 a^(log_b n) = n^(log_b a) (leaves), random a, b, n",
      all(math.isclose(a ** math.log(n, b), n ** math.log(a, b), rel_tol=1e-9)
          for a, b, n in ((rng.uniform(1, 9), rng.uniform(1.1, 9), rng.uniform(2, 1e6)) for _ in range(500))))

# Randomized selection T(n) = T(3n/4) + n, n = (4/3)^k, T(1) = 1: exactly 4n - 3
ok = True
for k in range(0, 60):
    nn = Fr(4, 3) ** k
    t = Fr(1)
    for j in range(1, k + 1):
        t = t + Fr(4, 3) ** j
    ok &= t == 4 * nn - 3
check("§3 T(n) = T(3n/4) + n, T(1) = 1, n = (4/3)^k: level sums (3/4)^i n, T(n) = 4n - 3 exactly, Theta(n)", ok)
# Karatsuba
check("§3 T(n) = 3T(n/2) + n, T(1) = 1: level sums (3/2)^i n; T(n) = 3 n^(lg 3) - 2n exactly (n = 2^k, k <= 100)",
      all(rec(3, 2, lambda m: m, k) == 3 * 3 ** k - 2 * 2 ** k for k in range(101))
      and all(3 ** i * Fr(2 ** k, 2 ** i) == Fr(3, 2) ** i * 2 ** k for k in range(20) for i in range(k + 1)))


# 2T(n/2) + n / lg n, base T(2) = 2: exactly n H_{lg n}
@lru_cache(None)
def nlg(k):
    return Fr(2) if k == 1 else 2 * nlg(k - 1) + Fr(2 ** k, k)


check("§3 T(n) = 2T(n/2) + n/lg n, T(2) = 2: level i sums to n/(lg n - i) (i <= lg n - 1); T(n) = n H_(lg n) exactly, k <= 150",
      all(nlg(k) == 2 ** k * H(k) for k in range(1, 151))
      and all(2 ** i * Fr(2 ** (k - i), k - i) == Fr(2 ** k, k - i) for k in range(1, 30) for i in range(k)))
check("§3 ln(n+1) <= H_n <= ln n + 1 for 1 <= n <= 20000",
      all(math.log(n + 1) <= h <= math.log(n) + 1 for n, h in
          zip(range(1, 20001), np.cumsum([1 / i for i in range(1, 20001)]))))
hk = np.cumsum([1 / i for i in range(1, 2 ** 20 + 1)])
vals = [hk[2 ** j - 1] / lg(2 ** j) for j in range(8, 21)]
ok, tl = settles(vals, 0.02)
check("§3 so n H_(lg n) = Theta(n log log n): H_k / lg k settles (tol 2%) toward ln 2 for k up to 2^20", ok, str(tl))


# 4T(n/2) + n lg n, T(1) = 0
@lru_cache(None)
def f4(k):
    return 0 if k == 0 else 4 * f4(k - 1) + 2 ** k * k


check("§3 T(n) = 4T(n/2) + n lg n, T(1) = 0: level sums n 2^i (lg n - i); T(n) = 2n^2 - n lg n - 2n exactly, k <= 200",
      all(f4(k) == 2 * 4 ** k - 2 ** k * k - 2 * 2 ** k for k in range(201))
      and all(f4(k) == sum(2 ** k * 2 ** i * (k - i) for i in range(k)) for k in range(60)))
check("§3 sum_(j=1..k) j/2^j = 2 - (k+2)/2^k, so the infinite sum is 2 (and sum_(j=1..lg n) n^2 j/2^j is the tree sum)",
      all(sum(Fr(j, 2 ** j) for j in range(1, k + 1)) == 2 - Fr(k + 2, 2 ** k) for k in range(0, 80))
      and all(f4(k) == 4 ** k * sum(Fr(j, 2 ** j) for j in range(1, k + 1)) for k in range(60)))
vals = [f4(k) / 4 ** k for k in range(20, 200, 10)]
ok, tl = settles(vals, 1e-6)
check("§3 4T(n/2) + n lg n = Theta(n^2): T/n^2 -> 2 (tol 1e-6)", ok and abs(vals[-1] - 2) < 1e-6, str(tl))


# ---- real-valued recurrences on a lopsided tree: T(x) = 0 for x < 1. Memo by the exponents (a, b) of the
#      node size n * p^a * q^b, so the tree is computed exactly as a tree (no rounding of sizes).
def lopsided(n, p, q, cp, cq, fn):
    """T(x) = cp T(p x) + cq T(q x) + fn(x) for x >= 1, T(x) = 0 for x < 1."""
    memo = {}

    def t(a, b):
        x = n * p ** a * q ** b
        if x < 1:
            return 0.0
        if (a, b) not in memo:
            memo[(a, b)] = cp * t(a + 1, b) + cq * t(a, b + 1) + fn(x)
        return memo[(a, b)]

    return t(0, 0)


# randomized quicksort split
ns = [4.0 ** k for k in range(3, 16)]
Tq = [lopsided(n, 0.25, 0.75, 1, 1, lambda x: x) for n in ns]
rnd = [rng.uniform(1, 1e7) for _ in range(150)]
check("§3 T(n) = T(n/4) + T(3n/4) + n (T = 0 below 1): n log_4 n <= T(n) <= n (log_(4/3) n + 1), n = 4^3 .. 4^15 "
      "and 150 random real n in [1, 10^7]",
      all(n * math.log(n, 4) <= t <= n * (math.log(n, 4 / 3) + 1) for n, t in zip(ns, Tq))
      and all(n * math.log(n, 4) <= lopsided(n, 0.25, 0.75, 1, 1, lambda x: x) <= n * (math.log(n, 4 / 3) + 1)
              for n in rnd))
ent = 0.25 * lg(4) + 0.75 * lg(4 / 3)
vals = [t / (n * lg(n)) for n, t in zip(ns, Tq)]
ok, tl = settles(vals, 0.03)
check("§3 ... and T(n)/(n lg n) settles (tol 3%) near 1/H(1/4) = 1.233, inside [1/lg 4, 1/lg(4/3)] = [0.5, 2.41]",
      ok and all(0.5 < v < 2.41 for v in vals) and abs(vals[-1] - 1 / ent) < 0.06, f"{tl}, 1/H = {1 / ent:.4f}")
check("§3 ERROR p.9: without the +n / +1 the upper bounds fail for small n: T(1) = 1 > 1*log_(4/3) 1 = 0 for both "
      "T(3n/4) + T(n/4) + n and the weighted recurrence",
      lopsided(1.0, 0.25, 0.75, 1, 1, lambda x: x) == 1 > 0 and lopsided(1.0, 0.25, 0.75, 0.25, 0.75, lambda x: 1.0) == 1 > 0)
# ... but the printed bounds hold for every real n >= 2. T(n)/n (quicksort split) and T(n) (weighted) are
# piecewise constant, jumping only at n = 4^a (4/3)^b, while log_(4/3) n increases: checking n = 2 and every such
# breakpoint in [2, 8] (exact fractions) covers [2, 8]; for n >= 8 both children are >= 2 and induction works
# with margin 1 - (1/4)log_(4/3) 4 - 3/4 = -0.955 < 0 (same algebra for n log and for log).
def lop_exact(n, cp, cq, unit):
    memo = {}

    def t(a, b):
        x = n * Fr(1, 4) ** a * Fr(3, 4) ** b
        if x < 1:
            return Fr(0)
        if (a, b) not in memo:
            memo[(a, b)] = cp * t(a + 1, b) + cq * t(a, b + 1) + (x if unit == "n" else Fr(1))
        return memo[(a, b)]

    return t(0, 0)


bps = sorted({Fr(2)} | {Fr(4) ** a * Fr(4, 3) ** b for a in range(3) for b in range(10)
                        if 2 <= Fr(4) ** a * Fr(4, 3) ** b <= 8})
ok = all(float(lop_exact(x, 1, 1, "n")) <= float(x) * math.log(x, 4 / 3)
         and float(lop_exact(x, Fr(1, 4), Fr(3, 4), "1")) <= math.log(x, 4 / 3) for x in bps)
margin = 1 - 0.25 * math.log(4, 4 / 3) - 0.75
ok &= margin < -0.95
ok &= all(lopsided(n, 0.25, 0.75, 1, 1, lambda x: x) <= n * math.log(n, 4 / 3)
          and lopsided(n, 0.25, 0.75, 0.25, 0.75, lambda x: 1.0) <= math.log(n, 4 / 3)
          for n in [2 + i / 100 for i in range(1000)] + [r for r in rnd if r >= 2])
check("§3 p.9 bounds as printed (n log_(4/3) n, log_(4/3) n) do hold for all n >= 2: breakpoints in [2, 8] exactly, "
      "inductive margin -0.955, dense and random samples", ok, f"{len(bps)} breakpoints, margin {margin:.3f}")
# complete levels: every node at depth i <= log_4 n has size >= 1; level sums of complete levels are n
n = 4.0 ** 6
ok = True
for i in range(0, 7):
    sizes = [n * 0.25 ** a * 0.75 ** (i - a) for a in range(i + 1)]
    mult = [math.comb(i, a) for a in range(i + 1)]
    ok &= all(s >= 1 - 1e-9 for s in sizes) and math.isclose(sum(m * s for m, s in zip(mult, sizes)), n)
check("§3 at n = 4^6 the first log_4 n + 1 = 7 levels are complete and each sums to n; deepest leaf <= log_(4/3) n",
      ok and n * 0.75 ** math.floor(math.log(n, 4 / 3)) >= 1 and n * 0.75 ** (math.floor(math.log(n, 4 / 3)) + 1) < 1)

# deterministic selection
ns = [10.0 ** k for k in range(2, 13)]
Tm = [lopsided(n, 0.2, 0.7, 1, 1, lambda x: x) for n in ns]
vals = [t / n for n, t in zip(ns, Tm)]
ok, tl = settles(vals, 0.03)
check("§3 T(n) = T(n/5) + T(7n/10) + n: level sums n, 9n/10, 81n/100; n <= T(n) <= 10n and T/n settles (tol 3%)",
      ok and all(n <= t <= 10 * n for n, t in zip(ns, Tm)) and math.isclose(0.2 + 0.7, 0.9)
      and all(n <= lopsided(n, 0.2, 0.7, 1, 1, lambda x: x) <= 10 * n for n in rnd), str(tl))

# randomized search trees, weighted
ns = [4.0 ** k for k in range(3, 18)]
Tw = [lopsided(n, 0.25, 0.75, 0.25, 0.75, lambda x: 1.0) for n in ns]
check("§3 T(n) = T(n/4)/4 + 3T(3n/4)/4 + 1: log_4 n <= T(n) <= log_(4/3) n + 1, n = 4^3 .. 4^17 and 150 random n",
      all(math.log(n, 4) <= t <= math.log(n, 4 / 3) + 1 for n, t in zip(ns, Tw))
      and all(math.log(n, 4) <= lopsided(n, 0.25, 0.75, 0.25, 0.75, lambda x: 1.0) <= math.log(n, 4 / 3) + 1
              for n in rnd))
vals = [t / lg(n) for n, t in zip(ns, Tw)]
ok, tl = settles(vals, 0.03)
check("§3 ... T(n)/lg n settles (tol 3%) near 1/H(1/4) = 1.233: Theta(log n)", ok and abs(vals[-1] - 1 / ent) < 0.06, str(tl))


def two_param(n, alpha):
    memo = {}

    def t(a, b):
        x = n * 0.25 ** a * 0.75 ** b
        if x < 1:
            return 0.0
        if (a, b) not in memo:
            memo[(a, b)] = t(a + 1, b) + t(a, b + 1) + alpha * 0.25 ** a * 0.75 ** b
        return memo[(a, b)]

    return t(0, 0)


check("§3 the two-parameter form T(n, alpha) = T(n/4, alpha/4) + T(3n/4, 3alpha/4) + alpha gives T(n, 1) = T(n)",
      all(math.isclose(two_param(n, 1.0), t, rel_tol=1e-12) for n, t in zip(ns[:8], Tw[:8])))

# ham-sandwich trees
ns = [2.0 ** k for k in range(4, 61)]
Th = [lopsided(n, 0.5, 0.25, 1, 1, lambda x: 1.0) for n in ns]
check("§3 T(n) = T(n/2) + T(n/4) + 1 (T = 0 below 1): T(2^k) = F_(k+3) - 1 exactly, k = 4..60",
      all(t == fib(k + 3) - 1 for k, t in zip(range(4, 61), Th)))
check("§3 crude bounds: sqrt(n) <= T(n) <= 2n at n = 2^k, k = 4..60, and at 150 random real n in [1, 10^7]",
      all(math.sqrt(n) <= t <= 2 * n for n, t in zip(ns, Th))
      and all(math.sqrt(n) <= lopsided(n, 0.5, 0.25, 1, 1, lambda x: 1.0) <= 2 * n for n in rnd))
vals = [t / n ** lg(phi) for n, t in zip(ns, Th)]
ok, tl = settles(vals, 1e-6)
check("§3/§4/§6 ham-sandwich T(n)/n^(lg phi) settles (tol 1e-6) at phi^3/sqrt5 = 1.894", ok
      and abs(vals[-1] - phi ** 3 / math.sqrt(5)) < 1e-6, str(tl))

# master theorem ratio form on the note's examples
for a, b, fexp, kind, expect in ((2, 2, 1, "equal", 1), (1, 4 / 3, 1, "decreasing", 3 / 4), (3, 2, 1, "increasing", 1.5)):
    rr = a * (1 / b) ** fexp
    check(f"§3 Master Theorem ratio a f(n/b)/f(n) for {a}T(n/{b:g}) + n is {expect} ({kind})", math.isclose(rr, expect))


# =====================================================================================================
# 4 Akra-Bazzi
# =====================================================================================================
def rho_of(terms):
    g = lambda r: sum(a / b ** r for a, b in terms) - 1
    lo, hi = -20.0, 20.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if g(mid) > 0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


r_q = rho_of([(1, 4 / 3), (1, 4)])
r_m = rho_of([(1, 5), (1, 10 / 7)])
r_w = rho_of([(0.25, 4), (0.75, 4 / 3)])
r_h = rho_of([(1, 2), (1, 4)])
check("§4 rho: (3/4)^rho + (1/4)^rho = 1 gives rho = 1", abs(r_q - 1) < 1e-12)
check("§4 rho: (1/5)^rho + (7/10)^rho = 1 gives rho = 0.83978 (between 0 and 1)", abs(r_m - 0.83978) < 5e-6 and 0 < r_m < 1,
      f"{r_m:.6f}")
check("§4 rho: (1/4)(1/4)^rho + (3/4)(3/4)^rho = 1 gives rho = 0", abs(r_w) < 1e-12)
check("§4 rho: (1/2)^rho + (1/4)^rho = 1 gives rho = lg phi = 0.69424 (x = 2^rho solves 1/x + 1/x^2 = 1)",
      abs(r_h - lg(phi)) < 1e-12 and abs(r_h - 0.69424) < 5e-6 and abs(1 / phi + 1 / phi ** 2 - 1) < 1e-12, f"{r_h:.6f}")
xs = np.linspace(-3, 3, 601)
check("§4 sum a_i / b_i^x is strictly decreasing in x (so rho is unique) for all four examples",
      all(np.all(np.diff([sum(a / b ** x for a, b in t) for x in xs]) < 0)
          for t in ([(1, 4 / 3), (1, 4)], [(1, 5), (1, 10 / 7)], [(0.25, 4), (0.75, 4 / 3)], [(1, 2), (1, 4)])))
ok = True
for n in (10.0, 1e3, 1e6):
    I1 = integrate.quad(lambda u: u ** (-r_m), 1, n, limit=200)[0]
    I2 = integrate.quad(lambda u: u ** (-r_h - 1), 1, n, limit=200)[0]
    ok &= math.isclose(I1, (n ** (1 - r_m) - 1) / (1 - r_m), rel_tol=1e-6)
    ok &= math.isclose(I2, (1 - n ** (-r_h)) / r_h, rel_tol=1e-6)
check("§4 the two integrals: int_1^n u^-rho du = (n^(1-rho) - 1)/(1-rho), int_1^n u^(-rho-1) du = (1 - n^-rho)/rho", ok)


def ab_pred(n, rho, f):
    # substitute u = e^s: int_1^n f(u) u^(-rho-1) du = int_0^(ln n) f(e^s) e^(-rho s) ds (smooth integrand)
    return n ** rho * (1 + integrate.quad(lambda s: f(math.exp(s)) * math.exp(-rho * s), 0, math.log(n), limit=500)[0])


tests = [("quicksort split", [4.0 ** k for k in range(4, 15)], Tq_ := [lopsided(4.0 ** k, 0.25, 0.75, 1, 1, lambda x: x)
                                                                      for k in range(4, 15)], r_q, lambda u: u),
         ("deterministic selection", [10.0 ** k for k in range(3, 13)], [lopsided(10.0 ** k, 0.2, 0.7, 1, 1, lambda x: x)
                                                                         for k in range(3, 13)], r_m, lambda u: u),
         ("random search trees", [4.0 ** k for k in range(4, 18)], [lopsided(4.0 ** k, 0.25, 0.75, 0.25, 0.75, lambda x: 1.0)
                                                                    for k in range(4, 18)], r_w, lambda u: 1.0),
         ("ham-sandwich", [2.0 ** k for k in range(10, 61, 5)], [lopsided(2.0 ** k, 0.5, 0.25, 1, 1, lambda x: 1.0)
                                                                for k in range(10, 61, 5)], r_h, lambda u: 1.0)]
for name, ns_, ts_, rho, f in tests:
    vals = [t / ab_pred(n, rho, f) for n, t in zip(ns_, ts_)]
    ok, tl = settles(vals, 0.05)
    check(f"§4 Akra-Bazzi prediction n^rho (1 + int f/u^(rho+1)) matches T for {name} (ratio settles, tol 5%)", ok, str(tl))

for a, b, c, g in ((4, 2, 1, lambda n: n ** 2), (4, 2, 2, lambda n: n ** 2 * lg(n)), (4, 2, 3, lambda n: n ** 3)):
    vals = [rec(a, b, lambda m: m ** c, k) / g(2 ** k) for k in range(20, 80, 6)]
    ok, tl = settles(vals, 0.05)
    check(f"§4 Master Theorem from Akra-Bazzi: {a}T(n/{b}) + n^{c} = Theta(" +
          ("n^(log_b a)" if c < 2 else "n^c log n" if c == 2 else "n^c") + ") (tol 5%)", ok, str(tl))

# =====================================================================================================
# 5 Linear recurrences
# =====================================================================================================
def run_lin(coefs, base, nmax, g=lambda n: 0):
    """T(n) = sum_i coefs[i] T(n-1-i) + g(n) for n >= len(base)."""
    t = list(base)
    for n in range(len(base), nmax + 1):
        t.append(sum(c * t[n - 1 - i] for i, c in enumerate(coefs)) + g(n))
    return t


closed = lambda n: (n - 3) * 2 ** n + 4
note_ver = run_lin([3, -8, 4], [1, 0, 0], 40)
fixed = run_lin([5, -8, 4], [1, 0, 0], 300)
check("§5 ERROR p.12/p.17: the printed recurrence 3T(n-1) - 8T(n-2) + 4T(n-3) gives T(4) = 12, not (4-3)2^4 + 4 = 20",
      note_ver[3] == closed(3) and note_ver[4] == 12 and closed(4) == 20, str(note_ver[:7]))
check("§5 corrected: T(n) = 5T(n-1) - 8T(n-2) + 4T(n-3), T(0..2) = 1, 0, 0 gives (n-3)2^n + 4 for n <= 300",
      all(fixed[n] == closed(n) for n in range(301)), str(fixed[:7]))
check("§5 x^3 - 5x^2 + 8x - 4 = (x-2)^2 (x-1); x^3 - 3x^2 + 8x - 4 is not",
      list(np.polymul(np.polymul([1, -2], [1, -2]), [1, -1])) == [1, -5, 8, -4])
roots = sorted(np.roots([1, -3, 8, -4]), key=abs)
check("§5 the printed polynomial x^3 - 3x^2 + 8x - 4 has one real root 0.612 and two complex roots of modulus 2.557",
      abs(roots[0].imag) < 1e-12 and abs(roots[0].real - 0.6115) < 5e-4 and abs(abs(roots[1]) - 2.557) < 5e-4
      and abs(roots[1].imag) > 1, str(roots))
# the verification line of p.12
ok = True
for n in range(3, 60):
    lhs = 5 * Fr((n - 4) * 2 ** (n - 1) + 4) - 8 * Fr((n - 5) * 2 ** (n - 2) + 4) + 4 * Fr((n - 6) * 2 ** (n - 3) + 4)
    mid = (Fr(5, 2) - Fr(8, 4) + Fr(4, 8)) * n * 2 ** n - (Fr(20, 2) - Fr(40, 4) + Fr(24, 8)) * 2 ** n + (5 - 8 + 4) * 4
    ok &= lhs == mid == closed(n)
check("§5 corrected verification: (5/2 - 8/4 + 4/8) n 2^n - (20/2 - 40/4 + 24/8) 2^n + (5 - 8 + 4) 4 = (n-3)2^n + 4", ok)
check("§5 ERROR p.12: the printed brackets evaluate to 3/2-8/4+4/8 = 0, 12/2-40/4+24/8 = -1, (2-8+4)4 = -8, not 1, 3, 4",
      Fr(3, 2) - 2 + Fr(1, 2) == 0 and 6 - 10 + 3 == -1 and (2 - 8 + 4) * 4 == -8)

# 5.1 operators, on sequences n = 0..M
M = 40


def E(f, k=1):
    return lambda n: f(n + k)


def lin(*pairs):        # sum of c * f
    return lambda n: sum(c * f(n) for c, f in pairs)


def poly_op(coefs, f):
    """(sum_i coefs[i] E^(deg-i)) f, coefs highest first."""
    d = len(coefs) - 1
    return lambda n: sum(c * f(n + d - i) for i, c in enumerate(coefs))


def seq(f, m=M):
    return [f(n) for n in range(m)]


two = lambda n: Fr(2) ** n
check("§5.1 on f = 2^n: 2f = 2^(n+1), Ef = 2^(n+1), E^2 f = 2^(n+2), (E-2)f = 0, (E^2-1)f = 3*2^n",
      seq(lin((2, two))) == seq(lambda n: Fr(2) ** (n + 1)) == seq(E(two))
      and seq(E(two, 2)) == seq(lambda n: Fr(2) ** (n + 2))
      and seq(poly_op([1, -2], two)) == [0] * M and seq(poly_op([1, 0, -1], two)) == seq(lambda n: 3 * Fr(2) ** n))
ok = True
for _ in range(50):
    fv = [Fr(rng.randint(-50, 50)) for _ in range(M + 10)]
    gv = [Fr(rng.randint(-50, 50)) for _ in range(M + 10)]
    hv = [Fr(rng.randint(-50, 50)) for _ in range(M + 10)]
    f_, g_, h_ = (lambda v: (lambda n: v[n]))(fv), (lambda v: (lambda n: v[n]))(gv), (lambda v: (lambda n: v[n]))(hv)
    # E(f - 3(g - h)) = Ef - 3Eg + 3Eh
    ok &= seq(E(lambda n: f_(n) - 3 * (g_(n) - h_(n)))) == seq(lambda n: f_(n + 1) - 3 * g_(n + 1) + 3 * h_(n + 1))
    # (E-1)(E-2) = E^2 - 3E + 2 = (E-2)(E-1)
    a1 = poly_op([1, -1], poly_op([1, -2], f_))
    a2 = poly_op([1, -3, 2], f_)
    a3 = poly_op([1, -2], poly_op([1, -1], f_))
    ok &= seq(a1, M - 5) == seq(a2, M - 5) == seq(a3, M - 5)
check("§5.1 operator algebra on random sequences: E(f - 3(g-h)) = Ef - 3Eg + 3Eh; (E-1)(E-2) = E^2-3E+2 = (E-2)(E-1)", ok)
check("§5.1 ERROR p.13: with the printed middle line f(n+2) - 2f(n-1) - f(n+1) + 2f(n), the identity fails (2f(n+1) is meant)",
      any(fv[n + 2] - 2 * fv[n - 1] - (fv[n + 1] - 2 * fv[n]) != fv[n + 2] - 3 * fv[n + 1] + 2 * fv[n] for n in range(1, 30)))


# 5.2 annihilator table
def annihilates(coefs, f, m=30):
    return all(v == 0 for v in seq(poly_op(coefs, f), m))


def pmul(*ps):
    out = [Fr(1)]
    for p in ps:
        out = list(np.polymul(out, p))
    return [Fr(x) for x in out]


ok = True
for _ in range(40):
    al, be, ga = (Fr(rng.randint(-9, 9), rng.randint(1, 5)) for _ in range(3))
    a, b, c = Fr(rng.randint(-7, 7), rng.randint(1, 3)), Fr(rng.randint(-7, 7), rng.randint(1, 3)), Fr(rng.randint(2, 9))
    if a == b or b == c or a == c:
        continue
    ok &= annihilates([1, -1], lambda n: al)
    ok &= annihilates([1, -a], lambda n: al * a ** n)
    ok &= annihilates(pmul([1, -a], [1, -b]), lambda n: al * a ** n + be * b ** n)
    ok &= annihilates(pmul([1, -a], [1, -b], [1, -c]), lambda n: al * a ** n + be * b ** n + ga * c ** n)
    ok &= annihilates(pmul([1, -1], [1, -1]), lambda n: al * n + be)
    ok &= annihilates(pmul([1, -a], [1, -a]), lambda n: (al * n + be) * a ** n)
    ok &= annihilates(pmul([1, -a], [1, -a], [1, -b]), lambda n: (al * n + be) * a ** n + ga * b ** n)
    d = rng.randint(1, 5)
    cs = [Fr(rng.randint(-5, 5)) for _ in range(d)]
    ok &= annihilates(pmul(*([[1, -a]] * d)), lambda n: sum(cs[i] * n ** i for i in range(d)) * a ** n)
    ok &= annihilates(pmul([1, -1], [1, -1], [1, -1]), lambda n: al * n * n + be * n + ga)
check("§5.2 annihilator table (corrected row (E-a)^2(E-b): (alpha n + beta) a^n + gamma b^n) on random constants", ok)
# minimal annihilator of sum_i p_i(n) a_i^n (distinct a_i, p_i != 0) is prod (E - a_i)^(deg p_i + 1):
# it annihilates, and lowering any one exponent by 1 does not
ok, cnt = True, 0
for _ in range(60):
    bases = rng.sample([Fr(x) for x in (-3, -2, -1, 1, 2, 3, 5)] + [Fr(1, 2), Fr(-2, 3)], rng.randint(1, 3))
    polys = []
    for _a in bases:
        dgr = rng.randint(0, 2)
        cs = [Fr(rng.randint(-5, 5)) for _ in range(dgr)] + [Fr(rng.choice([-3, -2, -1, 1, 2, 3]))]
        polys.append(cs)
    fsum = (lambda bs, ps: (lambda n: sum(sum(c * n ** i for i, c in enumerate(p)) * a ** n for a, p in zip(bs, ps))))(
        bases, polys)
    exps = [len(p) for p in polys]
    ok &= annihilates(pmul(*[[1, -a] for a, e in zip(bases, exps) for _ in range(e)]), fsum, 40)
    for j in range(len(bases)):
        low = [e - (1 if i == j else 0) for i, e in enumerate(exps)]
        facs = [[1, -a] for a, e in zip(bases, low) for _ in range(e)]
        ok &= not annihilates(pmul(*facs) if facs else [Fr(1)], fsum, 40)
    cnt += 1
check("§5.2 minimal annihilator of sum p_i(n) a_i^n is prod (E - a_i)^(deg p_i + 1): annihilates, and lowering any "
      "exponent fails (random examples)", ok, f"{cnt} examples")
check("§5.2 ERROR p.14: the printed row (alpha n + beta) a^b + gamma b^n is not annihilated by (E-a)^2(E-b) (a=2, b=3)",
      not annihilates(pmul([1, -2], [1, -2], [1, -3]), lambda n: (n + 1) * Fr(2) ** 3 + Fr(3) ** n))
check("§5.2 (E-c)a^n = (a-c)a^n; (E-3)2^n = -2^n; (E-2)(2^n + 3^n) = 3^n; (E-a)((alpha n + beta)a^n) = alpha a^(n+1)",
      all(seq(poly_op([1, -c], lambda n: Fr(a) ** n), 15) == seq(lambda n: (a - c) * Fr(a) ** n, 15)
          for a in range(-3, 6) for c in range(-3, 6))
      and seq(poly_op([1, -3], two)) == seq(lambda n: -two(n))
      and seq(poly_op([1, -2], lambda n: two(n) + Fr(3) ** n)) == seq(lambda n: Fr(3) ** n)
      and seq(poly_op([1, -5], lambda n: (7 * n + 2) * Fr(5) ** n)) == seq(lambda n: 7 * Fr(5) ** (n + 1)))
# rules: X kills f -> kills Ef, alpha f; X kills f, g -> kills f +- g; X kills f, Y kills g -> XY kills f +- g
f_ = lambda n: (3 * n + 1) * two(n)
g_ = lambda n: Fr(-1) ** n
X, Y = pmul([1, -2], [1, -2]), [1, 1]
check("§5.2 the four rules (shift, sum, scalar multiple, product of annihilators) on (3n+1)2^n and (-1)^n",
      annihilates(X, E(f_)) and annihilates(X, lambda n: 7 * f_(n)) and annihilates(X, lambda n: f_(n) - 2 * two(n))
      and annihilates(pmul(X, Y), lambda n: f_(n) + g_(n)) and annihilates(pmul(Y, X), lambda n: f_(n) - g_(n)))
# "nothing else": any sequence killed by (E-a)(E-b) is alpha a^n + beta b^n (fit from two values)
ok = True
for _ in range(30):
    a, b = rng.randint(-5, 5), rng.randint(-5, 5)
    if a == b or a == 0 or b == 0:
        continue
    x0, x1 = Fr(rng.randint(-20, 20)), Fr(rng.randint(-20, 20))
    s = run_lin([a + b, -a * b], [x0, x1], 25)
    beta = (x1 - a * x0) / (b - a)
    alpha = x0 - beta
    ok &= all(s[n] == alpha * Fr(a) ** n + beta * Fr(b) ** n for n in range(26))
check("§5.2 every solution of (E-a)(E-b)T = 0 is alpha a^n + beta b^n (two free constants), random a != b", ok)

# 5.3 examples
check("§5.3 r(n) = 5r(n-1), r(0) = 3: r(n) = 3*5^n (n <= 200)", run_lin([5], [3], 200) == [3 * 5 ** n for n in range(201)])
check("§5.3 phi, phi-hat are the roots of x^2 - x - 1; phi-hat = 1 - phi = -1/phi = -0.618034; 2phi - 1 = sqrt5",
      PHI * PHI - PHI - 1 == 0 and PHIH * PHIH - PHIH - 1 == 0 and PHIH == 1 - PHI and PHIH == -(PHI.inv())
      and abs(float(PHIH) + 0.618034) < 5e-7 and 2 * PHI - 1 == SQ5)
check("§5.3 Fibonacci: alpha = 1/sqrt5, alpha-hat = -1/sqrt5 solve F(0) = 0, F(1) = 1; F(n) = (phi^n - phihat^n)/sqrt5 "
      "exactly (all sqrt5 parts cancel), n <= 300",
      (SQ5.inv() - SQ5.inv()) == 0 and SQ5.inv() * PHI - SQ5.inv() * PHIH == 1
      and all((PHI ** n - PHIH ** n) / SQ5 == fib(n) for n in range(301)))
check("§5.3 |phihat^n/sqrt5| < 1/2, so F(n) = phi^n/sqrt5 rounded to the nearest integer, n <= 300",
      all(abs(Decimal(fib(n)) - PHI_D ** n / Decimal(5).sqrt()) < Decimal("0.5") for n in range(301))
      and abs(float(PHIH)) < 1)
check("§5.3 Hanoi: (E-2)T = 1 (T(n+1) - 2T(n) = 1); generic alpha 2^n + beta; alpha = 1, beta = -1",
      all(T[n + 1] - 2 * T[n] == 1 for n in range(100)) and all(T[n] == 1 * 2 ** n - 1 for n in range(100)))
# height-balanced trees
Hs = {-1: Q5(0), 0: Q5(1)}
for n in range(1, 301):
    Hs[n] = Hs[n - 1] + Hs[n - 2] + 1
al, be, ga = (SQ5 + 2) / SQ5, Q5(-1), (SQ5 - 2) / SQ5
check("§5.3 H(n) = H(n-1) + H(n-2) + 1, H(-1) = 0, H(0) = 1: H(1) = 2 and H(n) = alpha phi^n - 1 + gamma phihat^n with "
      "alpha = (sqrt5+2)/sqrt5, gamma = (sqrt5-2)/sqrt5, exactly for -1 <= n <= 300",
      Hs[1] == 2 and all(al * PHI ** n + be + ga * PHIH ** n == Hs[n] for n in range(-1, 301)))
check("§5.3 ... equivalently H(n) = F(n+3) - 1 (alpha = phi^3/sqrt5, gamma = -phihat^3/sqrt5)",
      all(Hs[n] == fib(n + 3) - 1 for n in range(0, 301)) and al == PHI ** 3 / SQ5 and ga == -(PHIH ** 3) / SQ5)
check("§5.3 ERROR p.16: the H(-1) equation needs + gamma/phihat (= -gamma phi); with the printed - gamma/phihat it fails",
      al / PHI + be + ga / PHIH == 0 and not (al / PHI + be - ga / PHIH == 0))
# the corrected cubic: solve the 3x3 system


def solve(A, b):
    """Gauss-Jordan over Fractions."""
    m = len(A)
    Mx = [[Fr(x) for x in row] + [Fr(y)] for row, y in zip(A, b)]
    for c in range(m):
        p = next(r for r in range(c, m) if Mx[r][c] != 0)
        Mx[c], Mx[p] = Mx[p], Mx[c]
        Mx[c] = [x / Mx[c][c] for x in Mx[c]]
        for r in range(m):
            if r != c and Mx[r][c] != 0:
                Mx[r] = [x - Mx[r][c] * y for x, y in zip(Mx[r], Mx[c])]
    return [row[-1] for row in Mx]


sol = solve([[0, 1, 1], [2, 2, 1], [8, 4, 1]], [1, 0, 0])
check("§5.3 corrected cubic: generic alpha n 2^n + beta 2^n + gamma; base cases give alpha = 1, beta = -3, gamma = 4",
      sol == [1, -3, 4])

# T(n) = T(n-1) + 2T(n-2) + 2^n - n^2
g = lambda n: Fr(2) ** n - n * n
check("§5.3 (E^2 - E - 2) = (E-2)(E+1); shifted form T(n+2) - T(n+1) - 2T(n) = 2^(n+2) - (n+2)^2",
      [int(x) for x in np.polymul([1, -2], [1, 1])] == [1, -1, -2])
check("§5.3 (E-2)(E-1)^3 annihilates 2^n - n^2 and 2^n + n^2",
      annihilates(pmul([1, -2], [1, -1], [1, -1], [1, -1]), g)
      and annihilates(pmul([1, -2], [1, -1], [1, -1], [1, -1]), lambda n: Fr(2) ** n + n * n))
basis = [lambda n: n * Fr(2) ** n, lambda n: Fr(2) ** n, lambda n: Fr(n * n), lambda n: Fr(n), lambda n: Fr(1),
         lambda n: Fr(-1) ** n]
alphas, ok_all, ok_forced = [], True, True
for trial in range(60):
    t0, t1 = Fr(rng.randint(-100, 100), rng.randint(1, 9)), Fr(rng.randint(-100, 100), rng.randint(1, 9))
    if trial == 0:
        t0, t1 = Fr(0), Fr(0)
    s = run_lin([1, 2], [t0, t1], 60, g)
    co = solve([[b(n) for b in basis] for n in range(6)], s[:6])
    alphas.append(co[0])
    ok_all &= all(sum(c * b(n) for c, b in zip(co, basis)) == s[n] for n in range(61))
    ok_forced &= co[0] == Fr(2, 3) and co[2] == Fr(1, 2) and co[3] == Fr(5, 2) and co[4] == 4
check("§5.3 T(n) = T(n-1) + 2T(n-2) + 2^n - n^2: the six-term generic solution fitted to T(0..5) matches T(n) for n <= 60 "
      "(60 random base cases)", ok_all)
check("§5.3 ERROR p.17: alpha = 2/3 for EVERY choice of T(0), T(1) (never 0), and gamma, delta, epsilon = 1/2, 5/2, 4 are forced "
      "too; T(n) = (2/3) n 2^n + beta 2^n + n^2/2 + 5n/2 + 4 + eta (-1)^n", ok_forced and set(alphas) == {Fr(2, 3)})
bad = [lambda n, eta=eta: -Fr(2) ** n / 2 - Fr(n * n, 2) - Fr(5 * n, 2) + eta * Fr(-1) ** n for eta in (0, 1, -3)]
check("§5.3 ERROR p.17 footnote 2: -2^(n-1) - n^2/2 - 5n/2 + eta(-1)^n does not satisfy the recurrence (eta = 0, 1, -3)",
      all(any(b(n) != b(n - 1) + 2 * b(n - 2) + g(n) for n in range(2, 10)) for b in bad))
s = run_lin([1, 2], [0, 0], 3000, lambda n: 2 ** n - n * n)
vals = [s[n] / (n * 2 ** n) for n in range(300, 3001, 300)]
ok, tl = settles(vals, 5e-3)
check("§5.3 ... so T(n) = Theta(n 2^n) for every base case: T(n)/(n 2^n) -> 2/3 (T(0) = T(1) = 0; tol 0.5%)",
      ok and abs(vals[-1] - 2 / 3) < 5e-3, str(tl))

# =====================================================================================================
# 6 Transformations
# =====================================================================================================
Nm = 1 << 17
ms_exact = [0, 1] + [0] * (Nm - 1)
for n in range(2, Nm + 1):
    ms_exact[n] = ms_exact[(n + 1) // 2] + ms_exact[n // 2] + n
check("§6 exact mergesort T(n) = T(ceil(n/2)) + T(floor(n/2)) + n, T(1) = 1 is nondecreasing (n <= 2^17)",
      all(ms_exact[n] <= ms_exact[n + 1] for n in range(1, Nm)))
check("§6 T(n) <= 2T(ceil(n/2)) + n and ceil(n/2) <= n/2 + 1; alpha = 2 solves n/2 + alpha = (n + alpha)/2 + 1",
      all(ms_exact[n] <= 2 * ms_exact[(n + 1) // 2] + n for n in range(2, Nm + 1))
      and all(Fr(n, 2) + 2 == Fr(n + 2, 2) + 1 for n in range(100)))
S = lambda n: ms_exact[n + 2]
check("§6 S(n) = T(n+2) satisfies S(n) <= 2S(n/2) + n + 2 for even n (n <= 2^17 - 2)",
      all(S(n) <= 2 * S(n // 2) + n + 2 for n in range(2, Nm - 1, 2)))
vals = [ms_exact[n] / (n * lg(n)) for n in (2 ** 10 + 1, 3 * 2 ** 10, 5 * 2 ** 11 + 7, 2 ** 14 - 3, 3 * 2 ** 14 + 1,
                                            2 ** 16 + 5, 99999, 2 ** 17)]
check("§6 exact mergesort = Theta(n log n): 1 <= T(n)/(n lg n) <= 1.2 for odd and non-power-of-2 n in [2^10, 2^17]",
      all(1 <= v <= 1.2 for v in vals), str([round(v, 3) for v in vals]))
# ham-sandwich via t(k) = T(2^k)
tk = [lopsided(2.0 ** k, 0.5, 0.25, 1, 1, lambda x: 1.0) for k in range(0, 50)]
check("§6 ham-sandwich: t(k) = T(2^k) satisfies t(k) = t(k-1) + t(k-2) + 1 (the H recurrence), so t(k) = F_(k+3) - 1",
      all(tk[k] == tk[k - 1] + tk[k - 2] + 1 for k in range(2, 50)) and all(tk[k] == fib(k + 3) - 1 for k in range(50)))
check("§6 phi^(lg n) = n^(lg phi), lg phi = 0.69424",
      all(math.isclose(phi ** lg(n), n ** lg(phi)) for n in (3.0, 1e3, 1e9)) and abs(lg(phi) - 0.69424) < 5e-6)
check("§6 mergesort: t(k) = T(2^k) satisfies t(k) = 2t(k-1) + 2^k and equals (k+1)2^k (annihilator (E-2)^2)",
      all(ms(2 ** k) == 2 * ms(2 ** (k - 1)) + 2 ** k == (k + 1) * 2 ** k for k in range(1, 100))
      and annihilates(pmul([1, -2], [1, -2]), lambda k: (k + 1) * Fr(2) ** k))
# footnote 3
lam = math.log(3) / math.log(1.5)
gfun = lambda r: r ** lam - r ** (lam - 1) - 1
rs = np.linspace(1.0001, 10, 20000)
check("§6 footnote 3: lambda = log_(3/2) 3 = 2.709511; r = 3/2 is the only positive root of r^lambda - r^(lambda-1) - 1",
      abs(lam - 2.709511) < 5e-7 and abs(gfun(1.5)) < 1e-12 and np.all(np.diff(gfun(rs)) > 0)
      and all(gfun(x) < 0 for x in np.linspace(0.001, 1, 500)))
ks = [k for k in range(8, 60, 4)]
tt = {k: lopsided(1.5 ** k, 1 / 3, 2 / 3, 1, 1, lambda x: x) for k in range(0, 61)}
check("§6 footnote 3: t(k) = T((3/2)^k) satisfies t(k) = t(k-1) + t(k-lambda) + (3/2)^k (T(n/3) = t(k - lambda))",
      all(math.isclose(1.5 ** k / 3, 1.5 ** (k - lam)) for k in range(1, 60)))
vals = [tt[k] / (1.5 ** k * k) for k in ks]
ok, tl = settles(vals, 0.04)
check("§6 T(n) = T(n/3) + T(2n/3) + n = Theta(n log n): t(k)/(k (3/2)^k) settles (tol 4%)", ok, str(tl))
# random BSTs: U(n) = n T(n)
ok = True
for n in (5.0, 37.0, 1000.0, 4.0 ** 9):
    Tn = lambda x: lopsided(x, 0.25, 0.75, 0.25, 0.75, lambda y: 1.0)
    U = lambda x: x * Tn(x)
    ok &= math.isclose(U(n), U(n / 4) + U(3 * n / 4) + n, rel_tol=1e-12)
check("§6 range transformation: U(n) = n T(n) satisfies U(n) = U(n/4) + U(3n/4) + n", ok)
# randomized quicksort, full history, T(0) = 0
NQ = 600
TQ = [Fr(0)]
for n in range(1, NQ + 1):
    TQ.append(Fr(2, n) * sum(TQ) + n)
check("§6 T(n) = (2/n) sum_(k<n) T(k) + n, T(0) = 0: limited-history form T(n) = (n+1)/n T(n-1) + 2 - 1/n (n <= 600)",
      all(TQ[n] == Fr(n + 1, n) * TQ[n - 1] + 2 - Fr(1, n) for n in range(1, NQ + 1))
      and all(n * TQ[n] - (n - 1) * TQ[n - 1] == 2 * TQ[n - 1] + 2 * n - 1 for n in range(1, NQ + 1)))
tq = [TQ[n] / (n + 1) for n in range(NQ + 1)]
check("§6 t(n) = T(n)/(n+1) satisfies t(n) = t(n-1) + 2/(n+1) - 1/(n(n+1))",
      all(tq[n] == tq[n - 1] + Fr(2, n + 1) - Fr(1, n * (n + 1)) for n in range(1, NQ + 1)))
Hn = [Fr(0)]
for n in range(1, NQ + 1):
    Hn.append(Hn[-1] + Fr(1, n))
check("§6 closed form T(n) = 2(n+1)H_n - 3n exactly (n <= 600)", all(TQ[n] == 2 * (n + 1) * Hn[n] - 3 * n for n in range(NQ + 1)))
vals = [2 * (n + 1) * sum(1 / i for i in range(1, n + 1)) - 3 * n for n in (10 ** 4, 10 ** 5, 10 ** 6, 2 * 10 ** 6)]
vals = [v / (n * math.log(n)) for v, n in zip(vals, (10 ** 4, 10 ** 5, 10 ** 6, 2 * 10 ** 6))]
ok, tl = settles(vals, 0.05)
check("§6 ... = Theta(n log n): T(n)/(n ln n) increases slowly toward 2 (1.6 < ratio < 2, tol 5%)",
      ok and all(1.6 < v < 2 for v in vals) and all(x < y for x, y in zip(vals, vals[1:])), str(tl))

# =====================================================================================================
# "Choosing a method" table and the exam box: every example
# =====================================================================================================
vals = [rec(3, 2, lambda m: m * m, k) / 4 ** k for k in range(20, 80, 6)]
ok, tl = settles(vals, 1e-6)
check("table: 3T(n/2) + n^2 = Theta(n^2) (level ratio 3/4)", ok, str(tl))
vals = [lopsided(2.0 ** k, 0.5, 0.25, 1, 1, lambda x: x) / 2.0 ** k for k in range(10, 60, 5)]
ok, tl = settles(vals, 0.02)
check("table: T(n/2) + T(n/4) + n = Theta(n) (fractions add to 3/4)", ok, str(tl))
vals = [rec(2, 2, lambda m: m * (m.bit_length() - 1), k) / (2 ** k * k * k) for k in range(100, 2001, 300)]
ok, tl = settles(vals, 0.01)
check("table: 2T(n/2) + n lg n = Theta(n log^2 n) (T(1) = 0; ratio (k+1)/(2k) -> 1/2, tol 1%)", ok, str(tl))


def sub(coefs, base, g, nmax):
    return run_lin(coefs, base, nmax, g)


t1 = sub([1], [0], lambda n: n, 3000)
check("table: T(n-1) + n = n(n+1)/2 = Theta(n^2)", all(t1[n] == n * (n + 1) // 2 for n in range(3001)))
t2 = sub([1, 1], [1, 1], lambda n: 1, 400)
vals = [t2[n] / phi ** n for n in range(100, 401, 30)]
ok, tl = settles(vals, 1e-9)
check("table: T(n-1) + T(n-2) + 1 = Theta(phi^n) (= 2F_(n+1) - 1 with T(0) = T(1) = 1)",
      ok and all(t2[n] == 2 * fib(n + 1) - 1 for n in range(401)), str(tl))
# root rule for constant-coefficient recurrences with non-negative coefficients
for coefs, base, gg, root, label in (([1, 1], [1, 1], lambda n: 1, phi, "T(n-1) + T(n-2) + 1"),
                                     ([3], [1], lambda n: 5, 3.0, "3T(n-1) + 5"),
                                     ([1, 2], [1, 1], lambda n: n, 2.0, "T(n-1) + 2T(n-2) + n"),
                                     ([1, 0, 1], [1, 1, 1], lambda n: 1, None, "T(n-1) + T(n-3) + 1")):
    if root is None:
        root = max(np.roots([1, -1, 0, -1]).real)
    s = sub(coefs, base, gg, 600)
    vals = [s[n] / root ** n for n in range(300, 601, 30)]
    ok, tl = settles(vals, 1e-6)
    check(f"rule: {label} = Theta(r^n), r = {root:.4f} the largest root of the characteristic polynomial", ok, str(tl))
check("rule: x^3 = x^2 + 1 has the real root 1.4656", abs(max(np.roots([1, -1, 0, -1]).real) - 1.4656) < 5e-5)


# T(sqrt n) + 1 and 2T(sqrt n) + lg n at n = 2^(2^k)
@lru_cache(None)
def sq1(k):
    return 1 if k == 0 else sq1(k - 1) + 1


@lru_cache(None)
def sq2(k):
    return 1 if k == 0 else 2 * sq2(k - 1) + 2 ** k


check("table: T(sqrt n) + 1 = lg lg n + 1 at n = 2^(2^k): Theta(log log n)", all(sq1(k) == k + 1 for k in range(60)))
check("table: 2T(sqrt n) + lg n = lg n (lg lg n + 1) at n = 2^(2^k), T(2) = 1: S(m) = T(2^m) = 2S(m/2) + m",
      all(sq2(k) == 2 ** k * (k + 1) for k in range(60)))

# =====================================================================================================
# concept page: linear recurrences
# =====================================================================================================
c1 = run_lin([2], [0], 300, lambda n: n)
check("concept: T(n) = 2T(n-1) + n, T(0) = 0: T(n) = 2^(n+1) - n - 2 (n <= 300)",
      all(c1[n] == 2 ** (n + 1) - n - 2 for n in range(301)))
check("concept: annihilator (E-2)(E-1)^2; forced beta = -1, gamma = -2 from plugging beta n + gamma in; alpha = 2 from T(0)",
      annihilates(pmul([1, -2], [1, -1], [1, -1]), lambda n: Fr(c1[n]))
      and all((-(n) - 2) == 2 * (-(n - 1) - 2) + n for n in range(1, 50)))
c2 = run_lin([2], [0], 200, lambda n: 2 ** n)
check("concept trap: T(n) = 2T(n-1) + 2^n, T(0) = 0 gives n 2^n (the residue's root 2 doubles), not Theta(2^n)",
      all(c2[n] == n * 2 ** n for n in range(201)))
c3 = run_lin([1, 2], [0, 1], 200)
check("concept: T(n) = T(n-1) + 2T(n-2), T(0) = 0, T(1) = 1: x^2 - x - 2 = (x-2)(x+1), T(n) = (2^n - (-1)^n)/3",
      all(3 * c3[n] == 2 ** n - (-1) ** n for n in range(201)))
c4 = run_lin([1, 1], [1, PHIH], 60)
check("concept trap: base cases can kill the dominant root: F-recurrence with T(0) = 1, T(1) = phihat gives phihat^n -> 0",
      all(c4[n] == PHIH ** n for n in range(61)) and abs(float(c4[60])) < 1e-12)
c5 = run_lin([4, -4], [1, 3], 200)
check("concept: T(n) = 4T(n-1) - 4T(n-2), T(0) = 1, T(1) = 3: double root 2, T(n) = (n/2 + 1) 2^n = (n+2)2^(n-1)",
      all(c5[n] == (n + 2) * 2 ** n // 2 for n in range(201)))

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: {FAIL}")
