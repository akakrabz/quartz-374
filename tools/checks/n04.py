#!/usr/bin/env python3
"""Checks for content/4-lecture-notes/04-tail-inequalities.md (Erickson, Director's Cut 4) and the concept page
content/concepts/tail-inequalities.md.

Every tail bound the page states — Markov, Chebyshev (and its four corollaries), the fourth-moment bound, the
exponential moment inequality, the absolute, alpha-, traditional and simple multiplicative Chernoff forms, and the
fair-coin bound — is evaluated against exact tails (Fractions for small n, scipy/log-space floats for larger n) of
binomial and Poisson-binomial variables over grids of parameters, and against exhaustively enumerated pairwise-,
3-wise- and 4-wise-independent families. Every number in §4.6 is recomputed. For the treap sections, Lemma 1's
independence and the distributions of depth_< and depth_> are checked exactly by enumerating all priority orders
(n <= 7); Lemma 2 is checked against the exact distribution of Z; Theorem 3 and its generalization are checked against
the exact distribution of the height of a random treap (a dynamic program over subtree sizes, itself checked against
enumeration and simulation). Where the note's argument or formula fails, the failure is exhibited."""
import itertools
import math
import os
import random
import sys
from fractions import Fraction as Fr

import numpy as np
from scipy.stats import binom

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
FIGS = os.path.join(HERE, "..", "figs")
PAGE = os.path.join(ROOT, "content", "4-lecture-notes", "04-tail-inequalities.md")
CONCEPT = os.path.join(ROOT, "content", "concepts", "tail-inequalities.md")
FAIL = []
rng = random.Random(40374)
E = math.e
LN43 = math.log(4 / 3)


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAIL.append(name)


def H(m):
    return sum((Fr(1, i) for i in range(1, m + 1)), Fr(0))


def pmf_pb(ps):
    """Exact pmf (list of Fractions) of a sum of independent indicators with probabilities ps (Fractions)."""
    d = [Fr(1)]
    for p in ps:
        nd = [Fr(0)] * (len(d) + 1)
        for i, q in enumerate(d):
            nd[i] += q * (1 - p)
            nd[i + 1] += q * p
        d = nd
    return d


def pmf_pb_float(ps):
    d = np.zeros(len(ps) + 1)
    d[0] = 1.0
    for j, p in enumerate(ps):
        d[1:j + 2] = d[1:j + 2] * (1 - p) + d[0:j + 1] * p
        d[0] *= (1 - p)
    return d


def upper(d, x):
    return sum((q for i, q in enumerate(d) if i >= x), Fr(0) if isinstance(d[0], Fr) else 0.0)


def lower(d, x):
    return sum((q for i, q in enumerate(d) if i <= x), Fr(0) if isinstance(d[0], Fr) else 0.0)


def mean(d):
    return sum(i * q for i, q in enumerate(d))


TOL = 1 + 1e-12

# exact test distributions: binomials and Poisson-binomials
DISTS = []
for N in (1, 2, 3, 5, 8, 13, 20, 30, 40):
    for p in (Fr(1, 10), Fr(1, 3), Fr(1, 2), Fr(9, 10)):
        DISTS.append((f"Bin({N},{p})", [p] * N))
for n in (5, 10, 20, 40):
    DISTS.append((f"Z_2..Z_{n} (Pr 1/j)", [Fr(1, j) for j in range(2, n + 1)]))
for t in range(12):
    m = rng.randint(1, 25)
    DISTS.append((f"random PB #{t}", [Fr(rng.randint(1, 19), 20) for _ in range(m)]))
PMFS = [(name, ps, pmf_pb(ps)) for name, ps in DISTS]

# =====================================================================================================
# 4.1 Markov
ok_area = ok_markov = ok_mult = True
for name, ps, d in PMFS:
    mu = mean(d)
    ok_area &= sum(upper(d, z) for z in range(1, len(d))) == mu
    for z2 in range(1, 4 * len(d) + 2):
        z = Fr(z2, 2)
        ok_markov &= upper(d, z) <= mu / z
    if mu > 0:
        for dl in (Fr(1, 4), Fr(1, 2), Fr(1), Fr(3)):
            ok_mult &= upper(d, (1 + dl) * mu) <= 1 / (1 + dl)
check("Markov's proof: the area under the staircase z -> Pr[Z >= z] is sum_z Pr[Z >= z] = E[Z] (exact)", ok_area)
check("Markov: Pr[Z >= z] <= E[Z]/z for z = 1/2, 1, 3/2, ... on all test distributions (exact)", ok_markov)
check("Markov, multiplicative: Pr[X >= (1+delta)E[X]] <= 1/(1+delta)", ok_mult)
ok = True
for _ in range(2000):
    vals = [rng.uniform(0, 10) for _ in range(rng.randint(1, 6))]
    w = [rng.random() for _ in vals]
    s = sum(w)
    w = [x / s for x in w]
    mu = sum(v * q for v, q in zip(vals, w))
    for z in np.linspace(0.1, 12, 40):
        ok &= sum(q for v, q in zip(vals, w) if v >= z) <= mu / z + 1e-12
check("Markov also holds for non-negative real-valued variables (2000 random finite distributions)", ok)
d6 = pmf_pb([Fr(1, 2)] * 6)
stair = [upper(d6, z) for z in range(1, 7)]
check("figure: 6 fair coins, Pr[Z >= z] = 63/64, 57/64, 42/64, 22/64, 7/64, 1/64 (z = 1..6); total area 3 = E[Z]",
      stair == [Fr(63, 64), Fr(57, 64), Fr(42, 64), Fr(22, 64), Fr(7, 64), Fr(1, 64)] and sum(stair) == 3)
check("figure: the rectangle at z = 4 has area 4 * 22/64 = 11/8 <= 3", 4 * stair[3] == Fr(11, 8) <= 3)
check("Markov for treaps: Pr[some node has depth >= 2n^2 ln n] <= n (2 ln n)/(2 n^2 ln n) = 1/n",
      all(abs(n * (2 * math.log(n)) / (2 * n * n * math.log(n)) - 1 / n) < 1e-15 for n in range(2, 1000)))

# =====================================================================================================
# 4.2 Independence
outcomes = []
for x, y, z in itertools.product((0, 1), repeat=3):
    outcomes.append(((x + y + z) % 2, x, y, z))


def mutually_independent(outs, idx):
    """outs: equally likely tuples; idx: tuple of coordinates."""
    N = len(outs)
    for vals in itertools.product((0, 1), repeat=len(idx)):
        joint = Fr(sum(1 for o in outs if all(o[i] == v for i, v in zip(idx, vals))), N)
        prod = Fr(1)
        for i, v in zip(idx, vals):
            prod *= Fr(sum(1 for o in outs if o[i] == v), N)
        if joint != prod:
            return False
    return True


check("W = (X+Y+Z) mod 2: every 3 of {W, X, Y, Z} are mutually independent (so also pairwise)",
      all(mutually_independent(outcomes, c) for r in (2, 3) for c in itertools.combinations(range(4), r)))
check("... but {W, X, Y, Z} is not 4-wise independent: Pr[W=X=Y=Z=1] = 0, not 1/16",
      not mutually_independent(outcomes, (0, 1, 2, 3)))
xs = [-1, 0, 1]
check("dependent but uncorrelated: X uniform on {-1,0,1}, Y = X^2: E[XY] = 0 = E[X]E[Y], yet Pr[X=0,Y=0] = 1/3 "
      "!= Pr[X=0]Pr[Y=0] = 1/9 (so the product rule 'need not' fail for dependent variables)",
      sum(Fr(x * x * x, 3) for x in xs) == 0 == sum(Fr(x, 3) for x in xs) * sum(Fr(x * x, 3) for x in xs))

# =====================================================================================================
# 4.3 Chebyshev
families = []
families.append(("X, Y, X xor Y", [(x, y, x ^ y) for x, y in itertools.product((0, 1), repeat=2)]))
families.append(("W, X, Y, Z", outcomes))
m = 4
subsets = [s for r in range(1, m + 1) for s in itertools.combinations(range(m), r)]
families.append(("all 15 XORs of 4 bits", [tuple(sum(b[i] for i in s) % 2 for s in subsets)
                                          for b in itertools.product((0, 1), repeat=m)]))
ok_pw = ok_var = ok_cheb = True
for name, outs in families:
    k = len(outs[0])
    ok_pw &= all(mutually_independent(outs, c) for c in itertools.combinations(range(k), 2))
    N = len(outs)
    S = [sum(o) for o in outs]
    mu = Fr(sum(S), N)
    ps = [Fr(sum(o[i] for o in outs), N) for i in range(k)]
    var = sum((Fr(s) - mu) ** 2 for s in S) / N
    ok_var &= var == sum(p * (1 - p) for p in ps) < mu
    for z2 in range(1, 200):
        z = Fr(z2, 4)
        ok_cheb &= Fr(sum(1 for s in S if (s - mu) ** 2 >= z), N) < mu / z
check("pairwise-independent families (X, Y, X xor Y; W, X, Y, Z; the 15 XORs of 4 bits) are pairwise independent", ok_pw)
check("Chebyshev's proof: E[(X - mu)^2] = sum p_i(1 - p_i) < mu for pairwise-independent indicators (exact)", ok_var)
check("Chebyshev: Pr[(X - mu)^2 >= z] < mu/z for all z on a grid, on these families", ok_cheb)
ok4 = True
for name, ps, d in PMFS:
    mu = mean(d)
    if mu == 0:
        continue
    for D4 in range(1, 4 * len(d) + 4):
        Dl = Fr(D4, 4)
        ok4 &= upper(d, mu + Dl) < mu / Dl ** 2 and lower(d, mu - Dl) < mu / Dl ** 2
    for dl in (Fr(1, 10), Fr(1, 4), Fr(1, 2), Fr(9, 10), Fr(1), Fr(2)):
        ok4 &= upper(d, (1 + dl) * mu) < 1 / (dl ** 2 * mu) and lower(d, (1 - dl) * mu) < 1 / (dl ** 2 * mu)
check("the four Chebyshev corollaries (additive and multiplicative, upper and lower tails) on all test distributions",
      ok4)

ok = True
for n in (10, 50, 200, 1000):
    for p in (0.1, 0.5, 0.8):
        for eps in (0.05, 0.1, 0.2):
            tail = binom.cdf(math.ceil(n * (p - eps)) - 1, n, p) + binom.sf(math.floor(n * (p + eps)), n, p)
            ok &= tail <= p * (1 - p) / (n * eps * eps) + 1e-12
check("weak law: Pr[|mean of n bits - p| > eps] <= p(1-p)/(n eps^2) (exact binomial tails)", ok)

# =====================================================================================================
# 4.4 Higher moments
five = [b + (sum(b) % 2,) for b in itertools.product((0, 1), repeat=4)]
check("5 bits with X5 = X1 xor ... xor X4: 4-wise independent, not 5-wise",
      all(mutually_independent(five, c) for c in itertools.combinations(range(5), 4))
      and not mutually_independent(five, tuple(range(5))))
S5 = [sum(o) for o in five]
mu5 = Fr(sum(S5), 16)
m4 = sum((s - mu5) ** 4 for s in S5) / 16
check("4-wise independent family: E[(X - mu)^4] = sum E[Y_i^4] + 6 sum_{i<j} E[Y_i^2]E[Y_j^2] <= mu + 3 mu^2",
      m4 == 5 * Fr(1, 16) + 6 * 10 * Fr(1, 16) and m4 <= mu5 + 3 * mu5 ** 2, f"m4 = {m4}, mu = {mu5}")
ok = True
for name, ps, d in PMFS:
    mu = mean(d)
    m4 = sum(q * (i - mu) ** 4 for i, q in enumerate(d))
    ok &= m4 <= mu + 3 * mu ** 2
    for z in range(1, 60):
        ok &= sum(q for i, q in enumerate(d) if (i - mu) ** 4 >= z) <= (mu + 3 * mu ** 2) / z
check("fourth-moment bound Pr[(X - mu)^4 >= z] <= (mu + 3 mu^2)/z, i.e. O(mu^2/z) once mu >= 1", ok)
ratios = [Fr(1, 10 ** j) / (16 * Fr(1, 10 ** j) ** 2) for j in (2, 4, 6)]  # p / (16 p^2)
check("why mu >= 1 is needed: one bit with Pr = p, Delta = 1/2: Pr[X >= mu + Delta] = p but (mu/Delta^2)^2 = 16p^2; "
      "the ratio 1/(16p) is unbounded", ratios == [Fr(100, 16), Fr(10 ** 4, 16), Fr(10 ** 6, 16)])

# =====================================================================================================
# 4.5 Chernoff
ok = True
for name, ps, d in PMFS:
    mu = float(mean(d))
    for a in (0.02, 0.1, 0.3, 0.5, 0.8, 1.0, 1.3, 2, 4, 10):
        lhs = math.prod((a - 1) * float(p) + 1 for p in ps)
        lhs2 = math.fsum(float(q) * a ** i for i, q in enumerate(d))
        ok &= abs(lhs - lhs2) <= 1e-9 * max(1, lhs) and lhs <= math.exp((a - 1) * mu) * TOL
check("exponential moment: E[alpha^X] = prod((alpha - 1)p_i + 1) <= e^{(alpha-1)mu} for alpha < 1 as well as "
      "alpha >= 1 (the lower-tail proof needs alpha < 1)", ok)


def chern_abs(x, mu):
    if x == 0:
        return math.exp(-mu)
    return math.exp(x - mu + x * math.log(mu / x))


ok_up = ok_lo = ok_alpha = ok_min = True
for name, ps, d in PMFS:
    mu = float(mean(d))
    n = len(d) - 1
    df = [float(q) for q in d]
    for x2 in range(0, 2 * n + 1):
        x = x2 / 2
        if x >= mu:
            t = math.fsum(df[i] for i in range(n + 1) if i >= x)
            ok_up &= t <= chern_abs(x, mu) * TOL
            for a in (1.05, 1.5, 2, 3, 10):
                ok_alpha &= t <= math.exp((a - 1) * mu) / a ** x * TOL
            if x > mu:
                best = chern_abs(x, mu)
                grid = [math.exp((a - 1) * mu) / a ** x for a in np.linspace(1.0001, 4 * x / mu + 2, 4000)]
                ok_min &= min(grid) >= best * (1 - 1e-9)
        if 0 < x <= mu:
            t = math.fsum(df[i] for i in range(n + 1) if i <= x)
            ok_lo &= t <= chern_abs(x, mu) * TOL
            for a in (0.1, 0.5, 0.9, 0.99):
                ok_alpha &= t <= math.exp((a - 1) * mu) / a ** x * TOL
            if x < mu:
                best = chern_abs(x, mu)
                grid = [math.exp((a - 1) * mu) / a ** x for a in np.linspace(1e-4, 0.9999, 4000)]
                ok_min &= min(grid) >= best * (1 - 1e-9)
check("Chernoff upper tail Pr[X >= x] <= e^{x-mu}(mu/x)^x for x >= mu (exact tails)", ok_up)
check("Chernoff lower tail Pr[X <= x] <= e^{x-mu}(mu/x)^x for 0 < x <= mu", ok_lo)
check("alpha-forms e^{(alpha-1)mu}/alpha^x (alpha > 1 upper, alpha < 1 lower) hold", ok_alpha)
check("the alpha-forms are minimized at alpha = x/mu (grid search)", ok_min)
ok_tr = ok_eq = True
for name, ps, d in PMFS:
    mu = float(mean(d))
    if mu == 0:
        continue
    df = [float(q) for q in d]
    n = len(d) - 1
    for Dl in np.linspace(0.05, n, 40):
        t = math.fsum(df[i] for i in range(n + 1) if i >= mu + Dl)
        b = math.exp(Dl) * (mu / (mu + Dl)) ** (mu + Dl)
        ok_tr &= t <= b * TOL
        ok_eq &= abs(b - chern_abs(mu + Dl, mu)) <= 1e-9 * b
        if Dl < mu:
            t = math.fsum(df[i] for i in range(n + 1) if i <= mu - Dl)
            b = math.exp(-Dl) * (mu / (mu - Dl)) ** (mu - Dl)
            ok_tr &= t <= b * TOL
    for dl in (0.05, 0.1, 0.3, 0.5, 0.9, 1, 2, 5):
        t = math.fsum(df[i] for i in range(n + 1) if i >= (1 + dl) * mu)
        b = (math.exp(dl) / (1 + dl) ** (1 + dl)) ** mu
        ok_tr &= t <= b * TOL
        ok_eq &= abs(b - chern_abs((1 + dl) * mu, mu)) <= 1e-9 * max(b, 1e-300)
        if dl < 1:
            t = math.fsum(df[i] for i in range(n + 1) if i <= (1 - dl) * mu)
            b = (math.exp(-dl) / (1 - dl) ** (1 - dl)) ** mu
            ok_tr &= t <= b * TOL
check("the four traditional Chernoff forms (additive/multiplicative, upper/lower) hold on all test distributions", ok_tr)
check("they are the absolute form with x = mu + Delta, (1 + delta) mu (algebraic identity)", ok_eq)
ok_simple = True
for name, ps, d in PMFS:
    mu = float(mean(d))
    df = [float(q) for q in d]
    n = len(d) - 1
    for dl in np.linspace(0.01, 0.99, 50):
        ok_simple &= math.fsum(df[i] for i in range(n + 1) if i >= (1 + dl) * mu) <= math.exp(-dl * dl * mu / 3) * TOL
        ok_simple &= math.fsum(df[i] for i in range(n + 1) if i <= (1 - dl) * mu) <= math.exp(-dl * dl * mu / 2) * TOL
check("simple forms exp(-delta^2 mu/3) (upper) and exp(-delta^2 mu/2) (lower), 0 < delta < 1", ok_simple)
dls = np.linspace(1e-6, 1 - 1e-6, 100001)
check("the simple forms follow: delta - (1+delta) ln(1+delta) <= -delta^2/3 and -delta - (1-delta) ln(1-delta) <= "
      "-delta^2/2 on (0, 1)",
      bool(np.all(dls - (1 + dls) * np.log1p(dls) <= -dls ** 2 / 3 + 1e-15))
      and bool(np.all(-dls - (1 - dls) * np.log1p(-dls) <= -dls ** 2 / 2 + 1e-15)))
check("... but the upper simple form is not implied for delta = 2: 2 - 3 ln 3 = -1.296 > -4/3",
      2 - 3 * math.log(3) > -4 / 3)
check("the note's first 'Taylor' inequality 1/ln(1+delta) <= 1/2 + 1/delta holds on (0, 1)",
      bool(np.all(1 / np.log1p(dls) <= 0.5 + 1 / dls + 1e-9)))
check("the note's second, ln(1-delta) >= -delta + delta^2/2, is false for every delta in (0, 1); "
      "(1-delta) ln(1-delta) >= -delta + delta^2/2 is what the lower simple form needs",
      bool(np.all(np.log1p(-dls) < -dls + dls ** 2 / 2)) and
      bool(np.all((1 - dls) * np.log1p(-dls) >= -dls + dls ** 2 / 2 - 1e-15)))

# =====================================================================================================
# 4.6 Coin flips
check("Markov: Pr[X >= alpha N] <= 1/(2 alpha): 2/3 at 3/4 and 5/9 at 9/10",
      Fr(1, 2) / Fr(3, 4) == Fr(2, 3) and Fr(1, 2) / Fr(9, 10) == Fr(5, 9))
cheb = lambda a: 2 / ((2 * a - 1) ** 2)       # note's Chebyshev form mu/Delta^2, times N
chebv = lambda a: 1 / ((2 * a - 1) ** 2)      # with the true variance N/4
check("Chebyshev with mu/Delta^2 (Delta = (2alpha - 1)N/2): 2/((2alpha-1)^2 N): 8/N at 3/4, 25/(8N) at 9/10",
      cheb(Fr(3, 4)) == 8 and cheb(Fr(9, 10)) == Fr(25, 8))
check("Chebyshev with the variance N/4: 1/((2alpha-1)^2 N): 4/N and 25/(16N)",
      chebv(Fr(3, 4)) == 4 and chebv(Fr(9, 10)) == Fr(25, 16))
check("the note's 1/((2alpha-1)N) (2/N, 5/(4N)) drops the square: it is smaller than both by a factor 2alpha - 1 or "
      "2(2alpha - 1)", 1 / (2 * Fr(3, 4) - 1) == 2 and 1 / (2 * Fr(9, 10) - 1) == Fr(5, 4))
viol = []
for N in range(1, 3001):
    p1 = binom.sf(math.ceil(3 * N / 4) - 1, N, 0.5)
    p2 = binom.sf(math.ceil(9 * N / 10) - 1, N, 0.5)
    if p1 > 2 / N or p2 > 5 / (4 * N):
        viol.append(N)
check("the note's 2/N and 5/(4N) happen to be true (exact tails, N <= 3000; beyond, e^{-N/24} < 2/N)",
      not viol and all(math.exp(-N / 24) < 2 / N for N in range(3000, 10 ** 5, 97)))
p55 = sum(Fr(math.comb(100, j), 2 ** 100) for j in range(55, 101))
check("the note's general formula 1/((2alpha-1)N) is false: alpha = 0.55, N = 100 gives 0.1 < Pr[X >= 55] = 0.184 "
      "(exact)", p55 > Fr(1, 10) and abs(float(p55) - 0.184) < 5e-4, f"{float(p55):.4f}")
check("simple Chernoff exponent (2alpha-1)^2/6: 1/24 at 3/4, 8/75 at 9/10, and 8/75 > 1/10",
      Fr(1, 4) / 6 == Fr(1, 24) and Fr(16, 25) / 6 == Fr(8, 75) > Fr(1, 10))
check("lower simple exponent (1-2alpha)^2/4: 1/16 at 1/4, 4/25 at 1/10, and 4/25 >= 1/7",
      Fr(1, 4) / 4 == Fr(1, 16) and Fr(16, 25) / 4 == Fr(4, 25) >= Fr(1, 7))
kl = lambda a: math.log(2) + a * math.log(a) + (1 - a) * math.log(1 - a)
check("binomial-coefficient bound (2 a^a (1-a)^(1-a))^-N = e^{-c N}: c = 0.13081 at 1/4 (> 1/8), 0.36806 at 1/10 (> 1/3)",
      abs(kl(0.25) - 0.13081) < 5e-6 and abs(kl(0.1) - 0.36806) < 5e-6 and kl(0.25) > 1 / 8 and kl(0.1) > 1 / 3,
      f"{kl(0.25):.6f} {kl(0.1):.6f}")
ok_s = ok_l = ok_kl = True
for N in range(1, 2001):
    up = lambda a: binom.sf(math.ceil(a * N) - 1, N, 0.5)
    lo = lambda a: binom.cdf(math.floor(a * N), N, 0.5)
    ok_s &= up(0.75) < math.exp(-N / 24) and up(0.9) < math.exp(-8 * N / 75)
    ok_l &= lo(0.25) < math.exp(-N / 16) and lo(0.1) < math.exp(-4 * N / 25)
    for a in (0.55, 0.6, 0.75, 0.9, 0.99):
        ok_kl &= up(a) <= math.exp(-kl(a) * N) * TOL and lo(1 - a) <= math.exp(-kl(a) * N) * TOL
        ok_s &= up(a) <= math.exp(-(2 * a - 1) ** 2 * N / 6) * TOL
        ok_l &= lo(1 - a) <= math.exp(-(1 - 2 * (1 - a)) ** 2 * N / 4) * TOL
check("coin flips, N = 1..2000: Pr[X >= 3N/4] < e^{-N/24}, Pr[X >= 9N/10] < e^{-8N/75}, and the general simple form",
      ok_s)
check("coin flips: Pr[X <= N/4] < e^{-N/16}, Pr[X <= N/10] < e^{-4N/25}, and the general lower form", ok_l)
check("coin flips: the binomial-coefficient bound holds for both tails (alpha = .55 ... .99)", ok_kl)
ok = True
for N in range(1, 41):
    d = pmf_pb([Fr(1, 2)] * N)
    for a in (Fr(3, 5), Fr(3, 4), Fr(9, 10)):
        ok &= float(upper(d, a * N)) <= math.exp(-kl(float(a)) * N) * TOL
check("binomial-coefficient bound against exact Fraction tails, N <= 40", ok)

# figure: N = 100
N = 100
fig_rows = []
for a in np.round(np.arange(0.5, 1.0001, 0.05), 2):
    fig_rows.append((a, binom.sf(math.ceil(a * N) - 1, N, 0.5)))
check("figure (N = 100): exact Pr[X >= 75] = 2.8e-7, Pr[X >= 90] = 1.5e-17, Pr[X = 100] = 7.9e-31",
      abs(binom.sf(74, 100, .5) / 2.818e-7 - 1) < 1e-3 and abs(binom.sf(89, 100, .5) / 1.531e-17 - 1) < 1e-3
      and abs(0.5 ** 100 / 7.889e-31 - 1) < 1e-3, f"{binom.sf(74, 100, .5):.4g} {binom.sf(89, 100, .5):.4g}")
check("figure (N = 100) at alpha = 3/4: Markov 2/3, Chebyshev 1/25 (variance 25), Chernoff e^{-100/24} = 0.0155, "
      "binomial-coefficient bound e^{-13.08} = 2.1e-6",
      abs(1 / 25 - 0.04) < 1e-15 and abs(math.exp(-100 / 24) - 0.0155) < 5e-5 and
      abs(math.exp(-kl(0.75) * 100) / 2.1e-6 - 1) < 0.02, f"{math.exp(-kl(.75) * 100):.3g}")

# concept-page example: 1000 flips, at least 600 heads
t600 = binom.sf(599, 1000, 0.5)
pre = math.exp(500 * (0.2 - 1.2 * math.log(1.2)))
check("concept example (N = 1000, X >= 600): exact 1.36e-10; Markov 5/6; Chebyshev 250/100^2 = 1/40; simple Chernoff "
      "e^{-20/3} = 1.3e-3; precise Chernoff 8.3e-5; binomial-coefficient bound e^{-20.14} = 1.8e-9",
      abs(t600 / 1.364e-10 - 1) < 2e-3 and Fr(500, 600) == Fr(5, 6) and Fr(250, 10000) == Fr(1, 40) and
      abs(math.exp(-20 / 3) / 1.27e-3 - 1) < 0.01 and abs(pre / 8.3e-5 - 1) < 0.02 and
      abs(kl(0.6) * 1000 - 20.14) < 0.005 and abs(math.exp(-kl(0.6) * 1000) / 1.8e-9 - 1) < 0.02,
      f"{t600:.4g} {pre:.3g} {math.exp(-kl(.6) * 1000):.3g}")
check("concept example: the ordering exact < bin.-coeff. < precise Chernoff < simple Chernoff < Chebyshev < Markov",
      t600 < math.exp(-kl(0.6) * 1000) < pre < math.exp(-20 / 3) < 1 / 40 < 5 / 6)

# =====================================================================================================
# treaps: exact depth distributions
EN = {}
for n in range(1, 8):
    joint = {}
    for perm in itertools.permutations(range(n)):
        pri = {k: perm[k - 1] for k in range(1, n + 1)}
        # ancestors via the "smallest priority in X(i,k)" rule (checked against the tree in n03.py)
        up = {(i, k): int(min(range(min(i, k), max(i, k) + 1), key=lambda j: pri[j]) == i)
              for i in range(1, n + 1) for k in range(1, n + 1) if i != k}
        joint[perm] = up
    EN[n] = joint


def indep(n, k, side):
    idx = [i for i in range(1, n + 1) if (i > k if side == ">" else i < k)]
    N = math.factorial(n)
    rows = [tuple(EN[n][p][(i, k)] for i in idx) for p in EN[n]]
    marg = [Fr(sum(r[j] for r in rows), N) for j in range(len(idx))]
    for vals in itertools.product((0, 1), repeat=len(idx)):
        joint = Fr(sum(1 for r in rows if r == vals), N)
        prod = Fr(1)
        for m_, v in zip(marg, vals):
            prod *= m_ if v else 1 - m_
        if joint != prod:
            return False
    return True


check("Lemma 1 (Take 2): for n <= 7 and every k, the indicators [i above k], i > k, are mutually independent, and so "
      "are those with i < k (exact, all n! orders)",
      all(indep(n, k, s) for n in EN for k in range(1, n + 1) for s in "<>"))
check("... but not all n - 1 together: n = 3, k = 2: Pr[1 above 2 and 3 above 2] = 1/3, not 1/4",
      Fr(sum(1 for p in EN[3] if EN[3][p][(1, 2)] and EN[3][p][(3, 2)]), 6) == Fr(1, 3))
check("the count in Lemma 1's proof: of the (n-k+1)! orders of the priorities of nodes k..n, (n-k)! have node n "
      "smallest (the note prints (n-k-1)! of the n-k priorities)",
      all(sum(1 for p in itertools.permutations(range(m)) if p[-1] == 0) == math.factorial(m - 1) for m in range(1, 8)))
check("note 4's E[depth(k)] = H_k + H_{n-k} - 2 (p. 8) is wrong for every n, k (n = 2, k = 2 gives -1/2); "
      "correct H_k + H_{n-k+1} - 2",
      all(H(k) + H(n - k) - 2 != H(k) + H(n - k + 1) - 2 for n in range(1, 30) for k in range(1, n + 1))
      and H(2) + H(0) - 2 == Fr(-1, 2))


def dist_of_sum(n, k, side):
    idx = [i for i in range(1, n + 1) if (i > k if side == ">" else i < k)]
    N = math.factorial(n)
    d = [Fr(0)] * (n + 1)
    for p in EN[n]:
        d[sum(EN[n][p][(i, k)] for i in idx)] += Fr(1, N)
    return d


ok = True
for n in EN:
    for k in range(1, n + 1):
        lo_ = pmf_pb([Fr(1, j) for j in range(2, k + 1)])
        hi_ = pmf_pb([Fr(1, j) for j in range(2, n - k + 2)])
        a, b = dist_of_sum(n, k, "<"), dist_of_sum(n, k, ">")
        ok &= a[:len(lo_)] == lo_ and all(x == 0 for x in a[len(lo_):])
        ok &= b[:len(hi_)] == hi_ and all(x == 0 for x in b[len(hi_):])
check("depth_<(k) has the distribution of Z_2 + ... + Z_k and depth_>(k) that of Z_2 + ... + Z_{n-k+1} (exact, n <= 7)",
      ok)

# Lemma 2
ok_l2 = ok_wrong = ok_mono = ok_ch = True
for n in range(2, 5001):
    mu = float(H(n) - 1) if n <= 60 else None
    if mu is None:
        mu = math.fsum(1 / j for j in range(2, n + 1))
    if n <= 60 or n % 37 == 0 or n in (100, 1000, 5000):
        d = pmf_pb_float([1 / j for j in range(2, n + 1)])
        x = 4 * math.log(n)
        t = float(d[np.arange(n) > x].sum())
        ok_l2 &= t < n ** (3 - 4 * math.log(4)) < 1 / n ** 2
        ok_ch &= t <= chern_abs(x, mu) * TOL
    ok_wrong &= (E ** 3 / 4 ** 4) ** mu > (E ** 3 / 4 ** 4) ** math.log(n)
    ok_mono &= mu < math.log(n)
check("Lemma 2: Pr[Z > 4 ln n] < n^{3 - 4 ln 4} = n^{-2.545} < 1/n^2 (exact distribution of Z, n from 2 to 5000)",
      ok_l2 and abs(3 - 4 * math.log(4) + 2.54518) < 1e-5)
check("mu = H_n - 1 < ln n, and Pr[Z > 4 ln n] <= e^{x-mu}(mu/x)^x at x = 4 ln n", ok_mono and ok_ch)
check("the note's step (e^3/4^4)^mu < (e^3/4^4)^{ln n} (p. 9) is false for every n >= 2: the base is < 1 and mu < ln n",
      ok_wrong and E ** 3 / 4 ** 4 < 1)
ok = True
for x in (2.0, 5.0, 20.0, 4 * math.log(1000)):
    vals = [chern_abs(x, m_) for m_ in np.linspace(0.01, x, 500)]
    ok &= all(b >= a * (1 - 1e-12) for a, b in zip(vals, vals[1:]))
check("the fix: e^{x-mu}(mu/x)^x increases with mu on (0, x], so mu may be replaced by ln n; at mu = ln n, "
      "x = 4 ln n it equals n^{3 - 4 ln 4}",
      ok and all(abs(chern_abs(4 * math.log(n), math.log(n)) / n ** (3 - 4 * math.log(4)) - 1) < 1e-9
                 for n in (2, 10, 1000)))


# exact height distribution of a random treap (random BST): Q[h+1][n] = Pr[height > h], empty height -1
def height_tails(Nmax, Hmax):
    Q = np.zeros((Hmax + 2, Nmax + 1))
    Q[0, 1:] = 1.0
    for hi in range(1, Hmax + 2):
        q = Q[hi - 1]
        conv = np.convolve(q, q)[:Nmax]
        cs = np.cumsum(q)[:Nmax]
        Q[hi, 1:] = (2 * cs - conv) / np.arange(1, Nmax + 1)
    return Q


NM, HM = 4000, 200
Q = height_tails(NM, HM)


def ptail(n, h):
    """Pr[height > h] for real h."""
    h = math.floor(h)
    if h < -1:
        return 1.0
    if h > HM:
        return 0.0
    return float(Q[h + 1][n])


# DP against enumeration and simulation
ok = True
for n in range(1, 8):
    cnt = {}
    for perm in itertools.permutations(range(n)):
        pri = {k: perm[k - 1] for k in range(1, n + 1)}
        dep = max(sum(EN[n][perm][(i, k)] for i in range(1, n + 1) if i != k) for k in range(1, n + 1)) if n > 1 else 0
        cnt[dep] = cnt.get(dep, 0) + 1
    for h in range(-1, n + 1):
        exact = sum(c for d_, c in cnt.items() if d_ > h) / math.factorial(n)
        ok &= abs(exact - ptail(n, h)) < 1e-12
check("height DP agrees with enumeration of all priority orders, n <= 7", ok)
srng = np.random.default_rng(4)


def sim_height(n):
    keys = srng.permutation(n)
    left, right = {}, {}
    root = keys[0]
    dmax, depth = 0, {root: 0}
    for k in keys[1:]:
        v = root
        d = 0
        while True:
            d += 1
            nxt = (left if k < v else right).get(v)
            if nxt is None:
                (left if k < v else right)[v] = k
                break
            v = nxt
        depth[k] = d
        dmax = max(dmax, d)
    return dmax


hs = [sim_height(200) for _ in range(4000)]
emp = np.mean(np.array(hs) > 14)
pt = ptail(200, 14)
check(f"height DP agrees with 4000 simulated random BSTs (n = 200): Pr[height > 14] = {pt:.4f} vs {emp:.4f} "
      "(tolerance 4.5 standard errors)", abs(emp - pt) < 4.5 * math.sqrt(pt * (1 - pt) / 4000))

ok = True
for n in range(2, NM + 1):
    ok &= ptail(n, 8 * math.log(n)) <= 2 * n ** (4 - 4 * math.log(4)) < 2 / n
check("Theorem 3: Pr[height > 8 ln n] <= 2n * n^{3 - 4 ln 4} = 2/n^{1.545} < 2/n (exact height distribution, "
      "n <= 4000)", ok)
EH = [math.fsum(ptail(n, h) for h in range(0, HM + 1)) for n in (100, 1000, 4000)]
check("expected height <= 8 ln n + (n - 1) 2/n: e.g. E[height] = 12.29 (n = 100), 21.04 (n = 1000)",
      all(e <= 8 * math.log(n) + 2 for e, n in zip(EH, (100, 1000, 4000))) and abs(EH[0] - 12.29) < 0.005
      and abs(EH[1] - 21.04) < 0.005, " ".join(f"{e:.3f}" for e in EH))
check("the note's generalization 'depth > c ln n with probability <= 2/n^{c ln c - c}' is false: n = 1000, c = 4: "
      "exact Pr = 0.0033 > 2/1000^{4 ln 4 - 4} = 4.6e-5; c = 5: 1.2e-6 > 1.4e-9",
      ptail(1000, 4 * math.log(1000)) > 2 / 1000 ** (4 * math.log(4) - 4) and
      abs(ptail(1000, 4 * math.log(1000)) - 0.00334) < 5e-5 and abs(2 / 1000 ** (4 * math.log(4) - 4) - 4.63e-5) < 1e-6
      and ptail(1000, 5 * math.log(1000)) > 2 / 1000 ** (5 * math.log(5) - 5),
      f"{ptail(1000, 4 * math.log(1000)):.4g} {ptail(1000, 5 * math.log(1000)):.3g}")
ok = True
for c in (3, 3.5, 4, 5, 6, 8):
    for n in range(2, NM + 1, 7):
        ok &= ptail(n, 2 * c * math.log(n)) <= 2 / n ** (c * math.log(c) - c) * TOL
    ok &= all(abs(2 * n * n ** (c - 1 - c * math.log(c)) - 2 / n ** (c * math.log(c) - c)) < 1e-12 for n in (2, 10, 99))
check("the note's bound is below the exact Pr[height > c ln n] for every c in [2.86, 8] (n = 1000), and >= 1 up to 2.81",
      all(2 / 1000 ** (c * math.log(c) - c) < ptail(1000, c * math.log(1000)) for c in np.linspace(2.86, 8, 5141))
      and all(2 / 1000 ** (c * math.log(c) - c) >= 1 for c in np.linspace(2.5, 2.81, 32))
      and 2 / 1000 ** (2.85 * math.log(2.85) - 2.85) > ptail(1000, 2.85 * math.log(1000)))
c_one = min(c for c in np.linspace(5.5, 5.8, 3001) if 2 / 1000 ** ((c / 2) * math.log(c / 2) - c / 2) < 1)
check("figure: the corrected bound is >= the exact tail for every c in [2, 8] and drops below 1 at c = 5.63 (n = 1000)",
      all(2 / 1000 ** ((c / 2) * math.log(c / 2) - c / 2) >= ptail(1000, c * math.log(1000))
          for c in np.linspace(2, 8, 601)) and abs(c_one - 5.63) < 0.005, f"{c_one:.4f}")
check("corrected: depth > 2c ln n with probability <= 2n * n^{c - 1 - c ln c} = 2/n^{c ln c - c} (exact, c = 3 ... 8)",
      ok)
check("equivalently depth > c ln n with probability <= 2/n^{(c/2) ln(c/2) - c/2}; c = 8 gives Theorem 3's 2/n^{1.545}",
      abs((4 * math.log(4) - 4) - 1.54518) < 1e-5)

# =====================================================================================================
# 4.7 Back to treaps, take 1
ok = True
worst = 1.0
for m in range(2, 401):
    for k in range(1, m + 1):
        g = 0.5  # k is the root: the level is decided by a fair coin
        for r in range(1, m + 1):
            if r == k:
                continue
            sz = r - 1 if r > k else m - r
            g += 1 if m / 4 <= sz <= 3 * m / 4 else 0
        worst = min(worst, g / m)
        ok &= g / m >= 0.5
check("take 1: in a subtree of any size m <= 400, whatever the position of k, the next level is good with probability "
      f">= 1/2 (minimum {worst})", ok and worst == 0.5)


# exact joint law of the good/bad labels of levels 1..I, coin flips included (review R28)
def chain_sizes(pri, k):
    lo, hi, out = 1, len(pri), []
    while True:
        r = min(range(lo, hi + 1), key=lambda j: pri[j])
        out.append(hi - lo + 1)
        if r == k:
            return out
        lo, hi = (lo, r - 1) if k < r else (r + 1, hi)


def level_law(n, k, I, note_def):
    law = {}
    for perm in itertools.permutations(range(n)):
        sz = chain_sizes({j + 1: perm[j] for j in range(n)}, k)
        d = len(sz) - 1
        lab = [(1 if sz[i - 1] / 4 <= sz[i] <= 3 * sz[i - 1] / 4 else 0)
               if (i < d if note_def else i <= d) else None for i in range(1, I + 1)]
        free = [j for j, v in enumerate(lab) if v is None]
        for bits in itertools.product((0, 1), repeat=len(free)):
            g = list(lab)
            for j, b in zip(free, bits):
                g[j] = b
            law[tuple(g)] = law.get(tuple(g), 0) + Fr(1, math.factorial(n) * 2 ** len(free))
    return law


marg = lambda law, i: sum(v for t, v in law.items() if t[i] == 1)
both = lambda law: sum(v for t, v in law.items() if t[0] == t[1] == 1)
L52 = level_law(5, 2, 1, True)
check("take 1, the note's labels (coin flip already at i = depth(k)): n = 5, k = 2, level 1 is good with probability "
      "7/15 < 1/2", marg(L52, 0) == Fr(7, 15))
okc, worstc = True, Fr(1)
for n in range(2, 8):
    for k in range(1, n + 1):
        law = level_law(n, k, 3, False)
        for i in range(3):
            for pre in itertools.product((0, 1), repeat=i):
                den = sum(v for t, v in law.items() if t[:i] == pre)
                if den:
                    worstc = min(worstc, sum(v for t, v in law.items() if t[:i] == pre and t[i] == 1) / den)
check("take 1, the page's labels (split for i <= depth(k)): Pr[level i good | labels of levels < i] >= 1/2 "
      f"(exact, n <= 7, i <= 3; minimum {worstc})", worstc == Fr(1, 2))
L31, L41 = level_law(3, 1, 2, False), level_law(4, 1, 2, True)
check("take 1: the levels are not independent: n = 3, k = 1 (page's labels) 5/6, 7/12, both 1/2 != 35/72; "
      "n = 4, k = 1 (note's labels) 31/48, 25/48, both 11/32 != 775/2304",
      (marg(L31, 0), marg(L31, 1), both(L31)) == (Fr(5, 6), Fr(7, 12), Fr(1, 2))
      and Fr(5, 6) * Fr(7, 12) == Fr(35, 72) != Fr(1, 2)
      and (marg(L41, 0), marg(L41, 1), both(L41)) == (Fr(31, 48), Fr(25, 48), Fr(11, 32))
      and Fr(31, 48) * Fr(25, 48) != Fr(11, 32))
ex = lambda c: (c - 2) ** 2 / (4 * c * LN43)
check("take 1: exp(-(1-2/c)^2 c log_{4/3} n / 4) = n^{-(c-2)^2/(4c ln(4/3))} (algebra, several c and n)",
      all(abs(math.exp(-(1 - 2 / c) ** 2 * c * (math.log(n) / LN43) / 4) / n ** -ex(c) - 1) < 1e-9
          for c in (2.5, 4, 5.75, 10) for n in (10, 1000)))
c20 = 20 * LN43
check("c = 20 ln(4/3) = 5.75364: c log_{4/3} n = 20 ln n and the exponent is 2.128 > 2",
      abs(c20 - 5.75364) < 5e-6 and abs(ex(c20) - 2.128) < 5e-4 and ex(c20) > 2, f"{ex(c20):.4f}")
check("specialized bound with c = 10: e^{-10 log_{4/3} n/3} = n^{-10/(3 ln(4/3))} = n^{-11.587} < n^{-11}",
      abs(10 / (3 * LN43) - 11.587) < 5e-4)


# exact single-node depth distribution, and the coin-flip domination it relies on
def node_depths(M):
    D = {}
    for m in range(1, M + 1):
        for k in range(1, m + 1):
            v = np.zeros(m)
            v[0] += 1
            for r in range(1, m + 1):
                if r > k:
                    v[1:m] += np.pad(D[(r - 1, k)], (0, m - 1 - len(D[(r - 1, k)])))
                elif r < k:
                    w = D[(m - r, k - r)]
                    v[1:m] += np.pad(w, (0, m - 1 - len(w)))
            D[(m, k)] = v / m
    return D


DD = node_depths(60)
okd = okm = True
for (m, k), v in DD.items():
    ed = float(np.dot(np.arange(len(v)), v))
    okm &= abs(ed - float(H(k) + H(m - k + 1) - 2)) < 1e-9
    if m >= 2:
        g = math.floor(math.log(m) / LN43 + 1e-12)
        for t in range(1, m):
            okd &= v[t:].sum() <= binom.cdf(g, t - 1, 0.5) + 1e-12
check("exact depth distribution of x_k (DP, n <= 60) has mean H_k + H_{n-k+1} - 2", okm)
check("take 1, made precise: Pr[depth(x_k) >= t] <= Pr[at most log_{4/3} n heads in t - 1 fair flips] (exact, n <= 60)",
      okd)
ok = all(ptail(n, 20 * math.log(n)) < 1 / n ** 2 and ptail(n, 10 * math.log(n) / LN43) < 1 / n ** 11
         for n in range(2, NM + 1))
check("take 1's conclusions hold (even for the height): Pr[> 20 ln n] < 1/n^2, Pr[> 10 log_{4/3} n] < 1/n^11, n <= 4000",
      ok)

# =====================================================================================================
# figures and page text
for name, needles in [("n04-markov", ["E[Z] = 3", "11/8"]), ("n04-coins", ["Markov", "Chebyshev", "Chernoff", "exact"]),
                      ("n04-height", ["0.0033", "1000", "2.86", "5.63"])]:
    p = os.path.join(FIGS, name + ".html")
    if os.path.exists(p):
        txt = open(p, encoding="utf-8").read()
        check(f"figure {name} mentions " + ", ".join(needles), all(s in txt for s in needles))
for path, needles in [(PAGE, ["H_k + H_{n-k+1} - 2", "0.13081", "0.36806", "5.75364", "2.128", "11.587", "0.0033",
                              "8/N", "25/(8N)", "4/N", "25/(16N)", "7/15", "0.184", "35/72"]),
                      (CONCEPT, ["1.36", "5/6", "1/40", "1.8", "8.3"])]:
    if os.path.exists(path):
        txt = open(path, encoding="utf-8").read().replace(" ", "")
        for s in needles:
            check(f"{os.path.basename(path)} states {s}", s.replace(" ", "") in txt)

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: {FAIL}")
