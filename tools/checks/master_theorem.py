#!/usr/bin/env python3
"""Checks for content/concepts/master-theorem.md.

For every recurrence on the page (worked-examples table, the "does not apply" table, the traps, the
log-factor extension and the Akra-Bazzi examples):
  * T is computed exactly from the recurrence (Python ints / Fractions) at powers of b, n = b^k, with T(1) = 1;
    the ratio T(n)/g(n) to the claimed bound g must stay bounded over k in [K/8, K] (max/min <= 1.5) and must
    not drift (relative change between k = K/2 and k = K below 2%).  The same test is run against g*lg n and
    g/lg n and must FAIL there, so a missing or extra log factor would be caught.
  * For several rows the recurrence is also evaluated with floors/ceilings at random integers n up to 1e18
    (memoized); the ratio must stay in a bounded band whose mean does not drift between scales.
  * The case of every table row is computed from (a, b, f) by the textbook form (with the n^c log^k n
    extension) and by Erickson's ratio form, and compared with the case printed on the page.
  * Akra-Bazzi exponents are found by bisection and compared with the values on the page.
The two log log n examples converge too slowly for a ratio test alone; they get exact closed forms as well."""
import math
import random
import sys
from fractions import Fraction
from functools import lru_cache

sys.setrecursionlimit(100000)
FAIL = []


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAIL.append(name)


rng = random.Random(374)
lg = math.log2
LN2 = math.log(2)
PHI = (1 + math.sqrt(5)) / 2


def ln_exact(x):
    """Natural log of a positive int or Fraction of any size."""
    x = Fraction(x)
    return math.log(x.numerator) - math.log(x.denominator)


# ------------------------------------------------------------------------------------------ helpers
def T_powers(a, b, fk, K, t0=1):
    """Exact T(b^k) for k = 0..K from T(n) = a T(n/b) + f(n), T(1) = t0; fk(k) = f(b^k) exactly."""
    t = [Fraction(t0)]
    for k in range(1, K + 1):
        t.append(a * t[-1] + Fraction(fk(k)))
    return t


def ratio_test(lnT, lng, K, spread=1.5, drift=0.02):
    """lnT[k] = ln T(b^k); lng(k) = ln g(b^k).  Bounded on [K/8, K] and not drifting between K/2 and K."""
    ks = range(K // 8, K + 1)
    rs = {k: math.exp(lnT[k] - lng(k)) for k in ks}
    lo, hi = min(rs.values()), max(rs.values())
    d = abs(rs[K] - rs[K // 2]) / rs[K]
    return (hi / lo <= spread and d <= drift), rs[K // 8], rs[K // 2], rs[K], d


def theta_powers(name, a, b, fk, lng, lnb, K=1024, t0=1):
    """Claim T = Theta(g).  Passes the ratio test for g, fails it for g*lg n and for g/lg n."""
    t = T_powers(a, b, fk, K, t0)
    lnT = [ln_exact(x) for x in t]
    ok, r0, r1, r2, d = ratio_test(lnT, lng, K)
    lglog = lambda k: math.log(k * lnb / LN2)                     # ln(lg n) at n = b^k
    up, *_ = ratio_test(lnT, lambda k: lng(k) + lglog(k), K)       # g * lg n
    dn, *_ = ratio_test(lnT, lambda k: lng(k) - lglog(k), K)       # g / lg n
    check(name, ok and not up and not dn,
          f"T/g at n=b^{K//8}, b^{K//2}, b^{K}: {r0:.4f}, {r1:.4f}, {r2:.4f}; drift {d:.2%}; "
          f"g*lg n rejected: {not up}; g/lg n rejected: {not dn}")
    return t


def ln_pow_log(e, m, lnb):
    """ln of n^e * (lg n)^m at n = b^k, as a function of k."""
    return lambda k: e * k * lnb + (m * math.log(k * lnb / LN2) if m else 0.0)


def theta_floors(name, T, g, b=2.0, x_lo=20, x_hi=60, width=8, per=400, spread=3.0, drift=0.10):
    """T evaluated with floors/ceilings at random n, log-uniform in buckets n in [b^x, b^(x+width)) for
    x = x_lo, x_lo + width, ..., x_hi - width.  Each bucket spans a whole number of periods of the
    floor/ceiling oscillation (whose period is a factor b in n), so bucket means are comparable.
    The ratio T/g stays in a bounded band, and the means of the last two buckets agree within `drift`."""
    means, allr = [], []
    for x in range(x_lo, x_hi, width):
        rs = []
        for _ in range(per):
            n = max(2, int(b ** (x + width * rng.random())))
            rs.append(T(n) / g(n))
        means.append(sum(rs) / len(rs))
        allr += rs
    band = max(allr) / min(allr)
    d = abs(means[-1] - means[-2]) / means[-1]
    check(name, band <= spread and d <= drift,
          f"ratio band {min(allr):.3f}..{max(allr):.3f} for n in [{b}^{x_lo}, {b}^{x_hi}); "
          f"bucket means " + ", ".join(f"{m:.3f}" for m in means))


# ------------------------------------------------------------------------------------------ constants on the page
check("lg 3 = 1.585 (to 3 places)", round(lg(3), 3) == 1.585, f"{lg(3):.6f}")
check("lg 7 = 2.807 (to 3 places)", round(lg(7), 3) == 2.807, f"{lg(7):.6f}")
check("log_{3/2} 3 = 2.71 (to 2 places)", round(math.log(3) / math.log(1.5), 2) == 2.71, f"{math.log(3)/math.log(1.5):.6f}")
check("log_3 2 = 0.63 (to 2 places)", round(math.log(2) / math.log(3), 2) == 0.63, f"{math.log(2)/math.log(3):.6f}")
check("log_4 2 = 1/2", abs(math.log(2) / math.log(4) - 0.5) < 1e-12)
check("number of leaves a^(log_b n) = n^(log_b a)",
      all(abs(math.log(a) * math.log(n) / math.log(b) - math.log(n) * math.log(a) / math.log(b)) < 1e-9
          and abs(a ** (math.log(n) / math.log(b)) / n ** (math.log(a) / math.log(b)) - 1) < 1e-9
          for a in (1, 2, 3, 4, 7) for b in (1.5, 2, 3, 4, 5) for n in (10, 1000, 10 ** 6)))


# ------------------------------------------------------------------------------------------ case classification
def classify(a, b, c, k):
    """Textbook form with the log extension, f(n) = n^c lg^k n.  Returns (case, (e, m)) with solution n^e lg^m n,
    or ('equal', 'loglog') for k = -1."""
    e = math.log(a) / math.log(b)
    if c < e - 1e-9:
        return "leaves", (e, 0)
    if c > e + 1e-9:
        return "root", (c, k)
    if k > -1:
        return "equal", (e, k + 1)
    if k == -1:
        return "equal", "loglog"
    return "leaves", (e, 0)


def ratio_form(a, b, c, k):
    """Erickson's ratio form: a f(n/b) / f(n).  Constant only when k = 0; returns (case, ratio)."""
    rs = []
    for n in (2.0 ** 40, 2.0 ** 80, 2.0 ** 160):
        f = lambda x: x ** c * (lg(x) ** k if k else 1.0)
        rs.append(a * f(n / b) / f(n))
    if max(rs) - min(rs) > 1e-9:
        return "none", rs[-1]
    r = rs[0]
    if abs(r - 1) < 1e-9:
        return "equal", 1.0
    return ("root" if r < 1 else "leaves"), r


# rows of the worked-examples table: (label, a, b, c, k, case on page, ratio-form case on page, ratio on page,
#                                     solution on page as (e, m) meaning n^e lg^m n)
L3, L7, LS = lg(3), lg(7), math.log(3) / math.log(1.5)
ROWS = [
    ("MergeSort 2T(n/2)+n",          2, 2,   1,   0, "equal",  "equal",  1,   (1, 1)),
    ("BinarySearch T(n/2)+1",        1, 2,   0,   0, "equal",  "equal",  1,   (0, 1)),
    ("PingalaPower T(n/2)+2",        1, 2,   0,   0, "equal",  "equal",  1,   (0, 1)),
    ("QuickSelect median T(n/2)+n",  1, 2,   1,   0, "root",   "root",   0.5, (1, 0)),
    ("MinMax 2T(n/2)+2",             2, 2,   0,   0, "leaves", "leaves", 2,   (1, 0)),
    ("Cruel 2T(n/2)+n^lg3",          2, 2,   L3,  0, "root",   "root",   2 / 3, (L3, 0)),
    ("SplitMultiply 4T(n/2)+n",      4, 2,   1,   0, "leaves", "leaves", 2,   (2, 0)),
    ("Karatsuba 3T(n/2)+n",          3, 2,   1,   0, "leaves", "leaves", 1.5, (L3, 0)),
    ("Strassen 7T(n/2)+n^2",         7, 2,   2,   0, "leaves", "leaves", 1.75, (L7, 0)),
    ("StoogeSort 3T(2n/3)+1",        3, 1.5, 0,   0, "leaves", "leaves", 3,   (LS, 0)),
    ("Ex 1.6 A: 2T(n/4)+sqrt n",     2, 4,   0.5, 0, "equal",  "equal",  1,   (0.5, 1)),
    ("2T(n/2)+n lg n",               2, 2,   1,   1, "equal",  "none",   None, (1, 2)),
    ("4T(n/2)+n lg n",               4, 2,   1,   1, "leaves", "none",   None, (2, 0)),
]
for label, a, b, c, k, case, rcase, rpage, sol in ROWS:
    got, gsol = classify(a, b, c, k)
    rgot, r = ratio_form(a, b, c, k)
    ok = got == case and rgot == rcase and abs(gsol[0] - sol[0]) < 1e-9 and gsol[1] == sol[1]
    if rpage is not None:
        ok &= abs(r - rpage) < 1e-9
    check(f"case of row {label}: textbook form '{got}', ratio form '{rgot}' (ratio {r:.4f}), solution n^{gsol[0]:.3f} lg^{gsol[1]} n",
          ok)

# the n lg n rows: ratio (a/2)(lg n - 1)/lg n; for a = 4 it is >= 3/2 exactly when n >= 16
ok = all((4 * (n / 2) * lg(n / 2) / (n * lg(n)) >= 1.5) == (n >= 16) for n in [x / 4 for x in range(9, 4000)])
ok &= all(abs(a * (n / 2) * lg(n / 2) / (n * lg(n)) - (a / 2) * (lg(n) - 1) / lg(n)) < 1e-12 for a in (2, 4) for n in (3.0, 10.0, 1e6))
check("n lg n rows: a f(n/2)/f(n) = (a/2)(lg n - 1)/lg n, and for a = 4 it is >= 3/2 iff n >= 16", ok)
check("n lg n = O(n^1.5): n lg n / n^1.5 = lg n / sqrt n <= 1.5 for all n >= 1, -> 0",
      all(lg(n) / math.sqrt(n) <= 1.5 for n in range(1, 10 ** 5)) and lg(1e12) / 1e6 < 1e-4)
# regularity in the root rows: a f(n/b) <= kappa f(n) with kappa < 1 (here with equality)
for label, a, b, c, k, case, *_ in ROWS:
    if case == "root":
        kap = a / b ** c
        check(f"regularity holds in root row {label}: a f(n/b) = {kap:.4f} f(n), kappa < 1", kap < 1)
# regularity with a log factor: 2T(n/2) + n^2 lg n has a f(n/b)/f(n) = (1/2)(lg n - 1)/lg n <= 1/2
check("regularity for f = n^2 lg n, a = b = 2: ratio (1/2)(lg n - 1)/lg n <= 1/2 for all n >= 2",
      all(2 * (n / 2) ** 2 * lg(n / 2) <= 0.5 * n * n * lg(n) + 1e-9 for n in [2 ** j for j in range(1, 60)]))
# the ratio form's decreasing hypothesis forces f to be polynomially larger: f(b^k) = (a/kappa)^k f(1)
a_, b_, kap = 2, 2, Fraction(1, 2)
f = [Fraction(1)]
for _ in range(30):
    f.append(f[-1] * a_ / kap)         # a f(n/b) = kappa f(n)  =>  f(n) = (a/kappa) f(n/b)
check("a f(n/b) = kappa f(n) forces f(b^k) = f(1) n^(log_b a + log_b(1/kappa)): a=b=2, kappa=1/2 gives f = n^2",
      all(f[k] == Fraction(4) ** k for k in range(31)))


# ------------------------------------------------------------------------------------------ worked examples (powers)
LN = math.log
theta_powers("MergeSort 2T(n/2) + n = Theta(n log n)", 2, 2, lambda k: 2 ** k, ln_pow_log(1, 1, LN(2)), LN(2))
t = T_powers(2, 2, lambda k: 2 ** k, 40)
check("MergeSort exact: T(2^k) = 2^k (k + 1) with T(1) = 1", all(t[k] == 2 ** k * (k + 1) for k in range(41)))
theta_powers("BinarySearch T(n/2) + 1 = Theta(log n)", 1, 2, lambda k: 1, ln_pow_log(0, 1, LN(2)), LN(2))
theta_powers("PingalaPower T(n/2) + 2 = Theta(log n)", 1, 2, lambda k: 2, ln_pow_log(0, 1, LN(2)), LN(2))
theta_powers("QuickSelect, median pivot: T(n/2) + n = Theta(n)", 1, 2, lambda k: 2 ** k, ln_pow_log(1, 0, LN(2)), LN(2))
theta_powers("MinMax 2T(n/2) + 2 = Theta(n)", 2, 2, lambda k: 2, ln_pow_log(1, 0, LN(2)), LN(2))
t = [None, Fraction(1)]                       # T(2) = 1, T(n) = 2T(n/2) + 2
for k in range(2, 40):
    t.append(2 * t[-1] + 2)
check("MinMax exact: T(2) = 1, T(n) = 2T(n/2) + 2 gives 3n/2 - 2 at powers of 2",
      all(t[k] == Fraction(3 * 2 ** k, 2) - 2 for k in range(1, 40)))
theta_powers("Cruel 2T(n/2) + n^lg3 = Theta(n^lg3)", 2, 2, lambda k: 3 ** k, ln_pow_log(L3, 0, LN(2)), LN(2))
theta_powers("SplitMultiply 4T(n/2) + n = Theta(n^2)", 4, 2, lambda k: 2 ** k, ln_pow_log(2, 0, LN(2)), LN(2))
theta_powers("Karatsuba 3T(n/2) + n = Theta(n^lg3)", 3, 2, lambda k: 2 ** k, ln_pow_log(L3, 0, LN(2)), LN(2))
theta_powers("Strassen 7T(n/2) + n^2 = Theta(n^lg7)", 7, 2, lambda k: 4 ** k, ln_pow_log(L7, 0, LN(2)), LN(2))
theta_powers("StoogeSort 3T(2n/3) + 1 = Theta(n^log_{3/2} 3)", 3, Fraction(3, 2), lambda k: 1,
             ln_pow_log(LS, 0, LN(1.5)), LN(1.5))
theta_powers("Ex 1.6 A: 2T(n/4) + sqrt n = Theta(sqrt n log n)", 2, 4, lambda k: 2 ** k, ln_pow_log(0.5, 1, LN(4)), LN(4))
theta_powers("2T(n/2) + n lg n = Theta(n log^2 n)", 2, 2, lambda k: k * 2 ** k, ln_pow_log(1, 2, LN(2)), LN(2))
theta_powers("4T(n/2) + n lg n = Theta(n^2)", 4, 2, lambda k: k * 2 ** k, ln_pow_log(2, 0, LN(2)), LN(2))

# ------------------------------------------------------------------------------------------ worked examples (floors)
@lru_cache(maxsize=None)
def T_ms(n):
    return 1 if n <= 1 else T_ms((n + 1) // 2) + T_ms(n // 2) + n


theta_floors("MergeSort with floors and ceilings T(ceil n/2) + T(floor n/2) + n = Theta(n log n)", T_ms, lambda n: n * lg(n))


@lru_cache(maxsize=None)
def T_bs(n):
    return 1 if n <= 1 else T_bs(n // 2) + 1


theta_floors("BinarySearch with floors T(floor n/2) + 1 = Theta(log n)", T_bs, lambda n: lg(n))


@lru_cache(maxsize=None)
def T_ka(n):
    return 1 if n <= 1 else 3 * T_ka((n + 1) // 2) + n


theta_floors("Karatsuba with ceilings 3T(ceil n/2) + n = Theta(n^lg3)", T_ka, lambda n: n ** L3, spread=4.0)


@lru_cache(maxsize=None)
def T_st(n):
    return 1 if n <= 1 else 7 * T_st((n + 1) // 2) + n * n


theta_floors("Strassen with ceilings 7T(ceil n/2) + n^2 = Theta(n^lg7)", T_st, lambda n: n ** L7, spread=8.0)


@lru_cache(maxsize=None)
def T_sg(n):           # StoogeSort comparisons, as on the exercises page
    if n <= 1:
        return 0
    if n == 2:
        return 1
    return 3 * T_sg(-(-2 * n // 3))


theta_floors("StoogeSort with ceilings 3T(ceil 2n/3) = Theta(n^log_{3/2} 3)", T_sg, lambda n: n ** LS, b=1.5, x_lo=24, x_hi=64,
             spread=4.0)


@lru_cache(maxsize=None)
def T_qs(n):
    return 1 if n <= 1 else T_qs(n // 2) + n


theta_floors("QuickSelect median pivot with floors T(floor n/2) + n = Theta(n)", T_qs, lambda n: n)


# ------------------------------------------------------------------------------------------ the log-factor extension
for a, b, kk in [(2, 2, 0), (2, 2, 1), (2, 2, 2), (4, 2, 0), (4, 2, 1), (4, 2, 2), (1, 2, 1), (1, 2, 2)]:
    e = round(math.log(a) / math.log(b))
    theta_powers(f"extension, equal case: {a}T(n/{b}) + n^{e} lg^{kk} n = Theta(n^{e} log^{kk+1} n)", a, b,
                 lambda k, e=e, kk=kk: (b ** e) ** k * k ** kk, ln_pow_log(e, kk + 1, LN(b)), LN(b))
theta_powers("extension, k = -2: 2T(n/2) + n/lg^2 n = Theta(n)", 2, 2, lambda k: Fraction(2 ** k, k * k),
             ln_pow_log(1, 0, LN(2)), LN(2))
t = T_powers(2, 2, lambda k: Fraction(2 ** k, k * k), 400)
check("extension, k = -2: T(2^k)/2^k = 1 + sum 1/j^2 -> 1 + pi^2/6",
      abs(t[400] / 2 ** 400 - (1 + math.pi ** 2 / 6)) < 1 / 300, f"{float(t[400] / 2 ** 400):.5f} vs {1 + math.pi**2/6:.5f}")
theta_powers("extension, root case with a log: 2T(n/2) + n^2 lg n = Theta(n^2 log n)", 2, 2,
             lambda k: 4 ** k * k, ln_pow_log(2, 1, LN(2)), LN(2))
theta_powers("extension, leaves case with a log: 3T(n/2) + n lg^2 n = Theta(n^lg3)", 3, 2,
             lambda k: 2 ** k * k * k, ln_pow_log(L3, 0, LN(2)), LN(2))

# ------------------------------------------------------------------------------------------ does not apply
# T(n) = T(n-1) + n
T = [0]
for n in range(1, 5001):
    T.append(T[-1] + n)
check("T(n) = T(n-1) + n, T(0) = 0: exactly n(n+1)/2", all(T[n] == n * (n + 1) // 2 for n in range(5001)))
rs = [T[n] / n ** 2 for n in (500, 1000, 2000, 4000, 5000)]
check("T(n) = T(n-1) + n = Theta(n^2): T/n^2 settles at 1/2", max(rs) / min(rs) < 1.01 and abs(rs[-1] - 0.5) < 0.001,
      " ".join(f"{r:.4f}" for r in rs))
check("T(n) = T(n-1) + n is not Theta(n log n): T/(n lg n) grows", T[5000] / (5000 * lg(5000)) > 2 * T[500] / (500 * lg(500)))
# Hanoi
H = [0]
for n in range(1, 200):
    H.append(2 * H[-1] + 1)
check("Hanoi T(n) = 2T(n-1) + 1, T(0) = 0: exactly 2^n - 1", all(H[n] == 2 ** n - 1 for n in range(200)))


# MomSelect, real sizes (memo on exponents) and with floors
@lru_cache(maxsize=None)
def mom_real(i, j, n):
    x = n * 0.2 ** i * 0.7 ** j
    return 1.0 if x < 1 else x + mom_real(i + 1, j, n) + mom_real(i, j + 1, n)


rs = [mom_real(0, 0, 10.0 ** e) / 10.0 ** e for e in (6, 8, 10, 12)]
check("MomSelect T(n/5) + T(7n/10) + n = Theta(n) (real sizes): T/n settles below 10",
      max(rs) <= 10 and abs(rs[-1] - rs[-2]) / rs[-1] < 0.02, " ".join(f"{r:.4f}" for r in rs))


@lru_cache(maxsize=None)
def T_mom(n):
    return 1 if n <= 1 else T_mom(n // 5) + T_mom(7 * n // 10) + n


theta_floors("MomSelect with floors T(floor n/5) + T(floor 7n/10) + n = Theta(n)", T_mom, lambda n: n, x_hi=44)


@lru_cache(maxsize=None)
def T_13(n):
    return 1 if n <= 2 else T_13(n // 3) + T_13(n - n // 3) + n


theta_floors("T(n/3) + T(2n/3) + n = Theta(n log n) (floors)", T_13, lambda n: n * lg(n), x_hi=44)

# the gap: 2T(n/2) + n/lg n.  Exact: T(2^k) = 2^k (1 + H_k).
t = T_powers(2, 2, lambda k: Fraction(2 ** k, k), 300)
Hk = [Fraction(0)]
for j in range(1, 301):
    Hk.append(Hk[-1] + Fraction(1, j))
check("gap 2T(n/2) + n/lg n: exactly T(2^k) = 2^k (1 + H_k) with T(1) = 1", all(t[k] == 2 ** k * (1 + Hk[k]) for k in range(301)))
# normalized recurrence u_k = T(2^k)/2^k = u_{k-1} + 1/k, far out
u, K = 1.0, 10 ** 6
us = {}
for k in range(1, K + 1):
    u += 1.0 / k
    if k in (1000, K // 8, K // 4, K // 2, K):
        us[k] = u
gamma = 0.5772156649015329
check("gap: T(n)/n - ln lg n -> 1 + gamma (so T(n) = n ln lg n + O(n) = Theta(n log log n))",
      all(abs(us[k] - math.log(k) - (1 + gamma)) < 1e-3 for k in us), f"at lg n = 1e6: {us[K] - math.log(K):.6f}")
r = {k: us[k] / math.log(k) for k in us}          # T / (n ln lg n)
check("gap: T/(n ln lg n) bounded on lg n in [1e6/8, 1e6] and not drifting (< 2%)",
      max(r[k] for k in (K // 8, K // 4, K // 2, K)) / min(r[k] for k in (K // 8, K // 4, K // 2, K)) < 1.5
      and abs(r[K] - r[K // 2]) / r[K] < 0.02, " ".join(f"{r[k]:.4f}" for k in sorted(r)))
check("gap: Theta(n) is wrong: T/n = 1 + H_lg n grows without bound (drift > 2% from lg n = 5e5 to 1e6)",
      abs(us[K] - us[K // 2]) / us[K] > 0.02, f"{us[K//2]:.4f} -> {us[K]:.4f}")
check("gap: Theta(n log n) is wrong: T/(n lg n) -> 0", us[K] / K < 1e-4)
check("gap: ratio form a f(n/b)/f(n) = lg n/(lg n - 1) is never exactly 1 (none of Erickson's cases)",
      all(Fraction(k, k - 1) != 1 for k in range(2, 1000)))


@lru_cache(maxsize=None)
def T_gap(n):
    return 1 if n <= 1 else 2 * T_gap(n // 2) + n / lg(n)


theta_floors("gap with floors 2T(floor n/2) + n/lg n: T/(n ln lg n) stays in a band", T_gap, lambda n: n * math.log(lg(n)),
             spread=2.0)

# sqrt(n) T(sqrt n) + n: Theta(n log log n).  Exact at n = 2^(2^j) with T(2) = 1: T(n) = n (lg lg n + 1/2).
ok = True
for j in range(0, 7):
    def P(m_exp):    # n = 2^m_exp, m_exp a power of 2; sqrt n = 2^(m_exp/2) children
        if m_exp == 1:
            return Fraction(1)
        return 2 ** (m_exp // 2) * P(m_exp // 2) + 2 ** m_exp
    m_exp = 2 ** j
    ok &= P(m_exp) == 2 ** m_exp * (Fraction(j) + Fraction(1, 2))
check("sqrt(n) T(sqrt n) + n with T(2) = 1: exactly n (lg lg n + 1/2) at n = 2^(2^j), j = 0..6", ok)


@lru_cache(maxsize=None)
def T_sq(n):
    if n <= 2:
        return 1
    s = math.isqrt(n)
    return s * T_sq(s) + n


theta_floors("sqrt(n) T(sqrt n) + n with floors: T/(n lg lg n) stays in a band", T_sq, lambda n: n * lg(lg(n)),
             x_lo=24, x_hi=60, width=12, spread=2.0)

# 2T(sqrt n) + lg n: S(m) = T(2^m) = 2S(m/2) + m, Theta(m log m).  Exact at n = 2^(2^j), T(2) = 1: lg n (lg lg n + 1).
@lru_cache(maxsize=None)
def T_dt(n):
    if n <= 2:
        return 1
    return 2 * T_dt(math.isqrt(n)) + (n.bit_length() - 1)


ok = all(T_dt(2 ** (2 ** j)) == 2 ** j * (j + 1) for j in range(0, 21))
check("2T(sqrt n) + lg n (floors), T(n) = 1 for n <= 2: exactly lg n (lg lg n + 1) at n = 2^(2^j), j = 0..20", ok)
check("domain transformation: S(m) = T(2^m) satisfies S(m) = 2S(m/2) + m at m = 2^j (checked on the original recurrence)",
      all(T_dt(2 ** (2 ** j)) == 2 * T_dt(2 ** (2 ** (j - 1))) + 2 ** j for j in range(1, 21)))
rs = []
for _ in range(300):
    m = rng.randint(2 ** 6, 2 ** 18)
    n = 2 ** m + rng.getrandbits(m)
    rs.append(T_dt(n) / (lg(n) * lg(lg(n))))
check("2T(sqrt n) + lg n with floors at random n with lg n in [64, 2^18]: T/(lg n lg lg n) in a band (max/min < 1.5)",
      max(rs) / min(rs) < 1.5, f"{min(rs):.3f}..{max(rs):.3f}")
check("2T(sqrt n) + lg n is not Theta(log n): T/lg n = lg lg n + 1 grows (11 at lg n = 2^10, 21 at 2^20)",
      T_dt(2 ** (2 ** 10)) / 2 ** 10 == 11 and T_dt(2 ** (2 ** 20)) / 2 ** 20 == 21)


# ------------------------------------------------------------------------------------------ Akra-Bazzi
def rho(terms, lo=-5.0, hi=5.0):
    """Unique real root of sum a_i / b_i^rho = 1 (the left side decreases in rho)."""
    g = lambda p: sum(a / b ** p for a, b in terms) - 1
    for _ in range(200):
        mid = (lo + hi) / 2
        if g(mid) > 0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


r_mom = rho([(1, 5), (1, 10 / 7)])
check("Akra-Bazzi, MomSelect (1/5)^rho + (7/10)^rho = 1: rho = 0.83978 (to 5 places), so 0 < rho < 1",
      round(r_mom, 5) == 0.83978 and 0 < r_mom < 1, f"{r_mom:.8f}")
check("Akra-Bazzi, MomSelect: (1/5)^rho + (7/10)^rho is 2 at rho = 0 and 9/10 at rho = 1, decreasing",
      Fraction(1, 5) ** 0 + Fraction(7, 10) ** 0 == 2 and Fraction(1, 5) + Fraction(7, 10) == Fraction(9, 10)
      and all((0.2 ** (x / 100) + 0.7 ** (x / 100)) > (0.2 ** ((x + 1) / 100) + 0.7 ** ((x + 1) / 100)) for x in range(100)))
r_ham = rho([(1, 2), (1, 4)])
check("Akra-Bazzi, ham-sandwich (1/2)^rho + (1/4)^rho = 1: rho = lg phi = 0.69424 (to 5 places)",
      abs(r_ham - lg(PHI)) < 1e-12 and round(r_ham, 5) == 0.69424, f"{r_ham:.8f}")
check("Akra-Bazzi, T(n/3) + T(2n/3) + n: rho = 1", abs(rho([(1, 3), (1, 1.5)]) - 1) < 1e-12)
check("Akra-Bazzi, T(3n/4) + T(n/4) + n: rho = 1", abs(rho([(1, 4 / 3), (1, 4)]) - 1) < 1e-12)
check("Akra-Bazzi, (1/4)T(n/4) + (3/4)T(3n/4) + 1: rho = 0", abs(rho([(0.25, 4), (0.75, 4 / 3)])) < 1e-12)
check("Akra-Bazzi, single term a T(n/b): rho = log_b a",
      all(abs(rho([(a, b)]) - math.log(a) / math.log(b)) < 1e-9 for a in (1, 2, 3, 4, 7) for b in (1.5, 2, 4)))
# MomSelect: integral of u^(1-rho-1) = u^(-rho) from 1 to n is (n^(1-rho) - 1)/(1 - rho) -> T = Theta(n)
for n in (1e6, 1e12):
    steps = 200000
    lo_, hi_ = 0.0, math.log(n)
    h = (hi_ - lo_) / steps
    integral = sum(math.exp((1 - r_mom) * (lo_ + (i + 0.5) * h)) * h for i in range(steps))   # u = e^t: u^(-rho) du = u^(1-rho) dt
    closed = (n ** (1 - r_mom) - 1) / (1 - r_mom)
    check(f"Akra-Bazzi, MomSelect integral at n = {n:.0e} equals (n^(1-rho) - 1)/(1 - rho)", abs(integral / closed - 1) < 1e-6)
check("Akra-Bazzi, ham-sandwich: x = 2^rho solves 1/x + 1/x^2 = 1, so x = phi",
      abs(2 ** r_ham - PHI) < 1e-12 and abs(1 / PHI + 1 / PHI ** 2 - 1) < 1e-12)
check("Akra-Bazzi, ham-sandwich: integral_1^n u^(-rho-1) du = (1 - n^-rho)/rho < 1/rho",
      all((1 - n ** -r_ham) / r_ham < 1 / r_ham for n in (10.0, 1e3, 1e6, 1e12)))
# one term: n^rho (1 + integral_1^n u^(c - rho - 1) du) reproduces the three cases
for a, b, c in [(3, 2, 1), (4, 2, 1), (2, 2, 1), (2, 4, 0.5), (1, 2, 1), (2, 2, 2), (7, 2, 2), (1, 2, 0)]:
    r1 = rho([(a, b)])
    def AB(n, r1=r1, c=c):
        e = c - r1
        integral = math.log(n) if abs(e) < 1e-12 else (n ** e - 1) / e
        return n ** r1 * (1 + integral)
    case, sol = classify(a, b, c, 0)
    g = lambda n, sol=sol: n ** sol[0] * (math.log(n) if sol[1] else 1)
    rs = [AB(n) / g(n) for n in (1e20, 1e40, 1e60, 1e80)]
    check(f"Akra-Bazzi with one term reproduces the Master Theorem: {a}T(n/{b}) + n^{c}: {case}",
          max(rs) / min(rs) < 1.05, " ".join(f"{x:.4f}" for x in rs))
# ham-sandwich: t(k) = T(2^k) = t(k-1) + t(k-2) + 1 grows like phi^k = n^(lg phi)
t = [1, 3]
for k in range(2, 400):
    t.append(t[-1] + t[-2] + 1)
rs = [t[k] / PHI ** k for k in (100, 200, 300, 399)]
check("ham-sandwich T(n/2) + T(n/4) + 1 at n = 2^k: T/n^(lg phi) settles", max(rs) / min(rs) < 1 + 1e-9, f"{rs[-1]:.6f}")
# gap via Akra-Bazzi: rho = 1, integral_2^n du/(u lg u) = ln 2 (ln ln n - ln ln 2)
for n in (2.0 ** 64, 2.0 ** 1000):
    steps = 200000
    lo_, hi_ = math.log(2), math.log(n)
    h = (hi_ - lo_) / steps
    integral = sum(LN2 / (lo_ + (i + 0.5) * h) * h for i in range(steps))        # u = e^t: du/(u lg u) = ln2 dt / t
    closed = LN2 * (math.log(math.log(n)) - math.log(math.log(2)))
    check(f"Akra-Bazzi on the gap: integral_2^n du/(u lg u) = ln2 (ln ln n - ln ln 2) at n = 2^{round(lg(n))}",
          abs(integral / closed - 1) < 1e-6)

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: {FAIL}")
