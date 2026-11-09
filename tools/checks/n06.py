#!/usr/bin/env python3
"""Checks for content/4-lecture-notes/06-filtering-and-streaming.md (Erickson, Director's Cut 6, "Filtering and
Streaming") and the concept page content/concepts/bloom-filters.md.

Bloom filters: MakeBloomFilter / BloomMembership implemented as printed; Pr[bit is 0] and the exact false-positive
rate computed by enumerating every outcome for tiny parameters and, for larger ones, from the exact occupancy
distribution (Fractions, or floats for m in the thousands); compared with Bloom's estimate (1 - e^{-kn/m})^k
(footnote 3: the estimate is below the true rate), the optimum k = (m/n) ln 2, the constant 0.61850, the sizing rule
and the two examples (10n bits / 7 functions, 32n bits / 22 functions), plus a simulation of real filters.
Count-min sketch: CMIncrement / CMEstimate as printed; never an underestimate; the per-row expectation and Markov
bound exactly over every salt of a universal family; the overall guarantee Pr[f^ > f + eps N] <= delta by simulation.
Distinct elements (Exercise 2's estimator m / min h): its two stated tail bounds exactly over a 2-uniform family.
Every number printed on the two pages and in the figures is recomputed."""
import itertools
import math
import os
import random
import re
import sys
from collections import Counter
from fractions import Fraction as Fr

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
PAGE = os.path.join(ROOT, "content", "4-lecture-notes", "06-filtering-and-streaming.md")
CONCEPT = os.path.join(ROOT, "content", "concepts", "bloom-filters.md")
FIGS = os.path.join(HERE, "..", "figs")
FAIL = []
random.seed(6374)
RNG = np.random.default_rng(6374)


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAIL.append(name)


def read(path):
    return open(path, encoding="utf-8").read() if os.path.exists(path) else ""


# =====================================================================================================
print("== §6.1 Bloom filters: the two procedures")


def make_bloom(X, hs, m):
    B = [0] * m
    for x in X:
        for hj in hs:
            B[hj(x)] = 1
    return B


def bloom_member(B, hs, y):
    for hj in hs:
        if B[hj(y)] == 0:
            return False
    return "Maybe"


ok_noneg = True
for _ in range(300):
    m, k = random.randint(4, 40), random.randint(1, 6)
    tabs = [dict() for _ in range(k)]
    hs = [lambda x, t=t, m=m: t.setdefault(x, random.randrange(m)) for t in tabs]
    X = random.sample(range(1000), random.randint(0, 15))
    B = make_bloom(X, hs, m)
    ok_noneg &= all(bloom_member(B, hs, x) == "Maybe" for x in X)
    ok_noneg &= all(bloom_member(B, hs, y) is False for y in range(1000, 1100)
                    if any(B[hj(y)] == 0 for hj in hs))
check("BloomMembership never answers False for a member (no false negatives), and answers False exactly when "
      "some probed bit is 0 (300 random filters)", ok_noneg)

# the page's figure example
FIG_M = 16
FIG_H = {"cat": (1, 6, 11), "dog": (3, 6, 14), "emu": (0, 9, 11), "fox": (2, 9, 14), "gnu": (1, 9, 14)}
FIG_X = ["cat", "dog", "emu"]
Bf = make_bloom(FIG_X, [lambda x, j=j: FIG_H[x][j] for j in range(3)], FIG_M)
ones = [i for i in range(FIG_M) if Bf[i]]
check("figure example: cat, dog, emu set bits 0, 1, 3, 6, 9, 11, 14 (7 of 16; bits 6 and 11 are set twice)",
      ones == [0, 1, 3, 6, 9, 11, 14] and Counter(v for x in FIG_X for v in FIG_H[x])[6] == 2
      and Counter(v for x in FIG_X for v in FIG_H[x])[11] == 2)
check("figure example: fox (2, 9, 14) is rejected by bit 2; gnu (1, 9, 14) is a false positive",
      Bf[2] == 0 and all(Bf[i] for i in FIG_H["gnu"]))
check("figure example: a query with fresh random hashes is a false positive with probability (7/16)^3 = 343/4096 "
      "= 8.4%", Fr(7, 16) ** 3 == Fr(343, 4096) and abs(343 / 4096 - 0.0837) < 1e-4)

print("== §6.2 False positive rate")


def p_zero_exact(m, k, n):
    return Fr(m - 1, m) ** (k * n)


def occupancy(m, balls):
    """exact distribution of the number of occupied bins after `balls` uniform balls into m bins (Fractions)."""
    dist = {0: Fr(1)}
    for _ in range(balls):
        new = {}
        for i, pr in dist.items():
            new[i] = new.get(i, 0) + pr * Fr(i, m)
            if i < m:
                new[i + 1] = new.get(i + 1, 0) + pr * Fr(m - i, m)
        dist = new
    return dist


def fp_exact(m, k, n):
    """exact false-positive probability: the query's k hashes are independent of the filter's kn hashes."""
    return sum(pr * Fr(i, m) ** k for i, pr in occupancy(m, k * n).items())


def fp_exact_float(m, k, n):
    dist = np.zeros(m + 1)
    dist[0] = 1.0
    idx = np.arange(m + 1)
    for _ in range(k * n):
        stay = dist * idx / m
        move = dist * (m - idx) / m
        dist = stay
        dist[1:] += move[:-1]
    return float(np.sum(dist * (idx / m) ** k))


def fp_enumerate(m, k, n):
    """brute force: every assignment of the k(n+1) hash values (n items and the query)."""
    tot, cnt = 0, 0
    for vals in itertools.product(range(m), repeat=k * (n + 1)):
        bits = set(vals[:k * n])
        tot += all(v in bits for v in vals[k * n:])
        cnt += 1
    return Fr(tot, cnt)


ok_enum = True
for (m, k, n) in [(3, 1, 1), (3, 2, 1), (4, 2, 1), (4, 1, 2), (3, 2, 2), (5, 2, 2), (4, 3, 1), (3, 3, 1)]:
    ok_enum &= fp_enumerate(m, k, n) == fp_exact(m, k, n)
    zeros = Fr(sum(1 for vals in itertools.product(range(m), repeat=k * n) if 0 not in vals), m ** (k * n))
    ok_enum &= zeros == p_zero_exact(m, k, n)
check("Pr[B[h] = 0] = (1 - 1/m)^{kn} and the exact false-positive rate, by enumerating every outcome (8 tiny cases)",
      ok_enum)
ok_order, ok_k1, worst_gap = True, True, 0.0
for m in range(2, 41, 3):
    for n in range(1, 11):
        for k in range(1, 7):
            ex = fp_exact(m, k, n)
            bloom = (1 - p_zero_exact(m, k, n)) ** k
            approx = (1 - math.exp(-k * n / m)) ** k
            if k == 1:
                ok_k1 &= ex == bloom
            else:
                ok_order &= approx < float(bloom) and bloom < ex
            worst_gap = max(worst_gap, float(ex) - approx)
check("footnote 3: (1 - e^{-kn/m})^k < (1 - (1-1/m)^{kn})^k < exact false-positive rate for k >= 2 "
      "(exact Fractions, m < 41, n <= 10, k <= 6); equality of the last two for k = 1", ok_order and ok_k1)
check("e^{-kn/m} > (1 - 1/m)^{kn}: the approximation p overestimates the fraction of 0-bits",
      all(math.exp(-k * n / m) > float(p_zero_exact(m, k, n)) for m in range(2, 50) for k in (1, 3) for n in (1, 5)))
ok_mono = True
for k in (2, 4):
    for m in (20, 40):
        vals = [fp_exact(m, k, n) for n in range(1, 8)]
        ok_mono &= all(a < b for a, b in zip(vals, vals[1:]))
    for n in (3, 6):
        vals = [fp_exact(m, k, n) for m in range(8, 40, 4)]
        ok_mono &= all(a > b for a, b in zip(vals, vals[1:]))
check("the false-positive rate increases with n and decreases with m (exact, k = 2, 4)", ok_mono)
# optimum k
grid = [i / 10000 for i in range(1, 10000)]
pmax = max(grid, key=lambda p: math.log(p) * math.log(1 - p))
check("ln p ln(1-p) is maximized at p = 1/2 (grid of 10^4 points)", abs(pmax - 0.5) < 1e-4)
from scipy.optimize import minimize_scalar
ok_opt = True
for c in (4, 8, 10, 16, 32):
    res = minimize_scalar(lambda k: k * math.log(1 - math.exp(-k / c)), bounds=(0.01, 5 * c), method="bounded",
                          options={"xatol": 1e-10})
    kbest = res.x
    fbest = (1 - math.exp(-kbest / c)) ** kbest
    ok_opt &= abs(kbest - c * math.log(2)) < 1e-5 and abs(fbest / 0.5 ** (c * math.log(2)) - 1) < 1e-9
check("for m/n = c the estimate (1 - e^{-k/c})^k is minimized at k = c ln 2, where it equals (1/2)^{c ln 2} "
      "(c = 4, 8, 10, 16, 32)", ok_opt)
check("(1/2)^{ln 2} = e^{-(ln 2)^2} = 0.61850...", abs(math.exp(-math.log(2) ** 2) - 0.61850) < 5e-6,
      f"{math.exp(-math.log(2) ** 2):.6f}")
# sizing rule and the two examples
approx = lambda c, k: (1 - math.exp(-k / c)) ** k
check("10n bits and 7 hash functions: estimated false-positive rate 0.82% (< 1%)",
      abs(approx(10, 7) - 0.00819) < 5e-5, f"{approx(10, 7):.5f}")
check("32n bits and 22 hash functions: 2.10e-7, 'just over 2 * 10^-7'", 2.0e-7 < approx(32, 22) < 2.15e-7,
      f"{approx(32, 22):.3e}")
c1 = math.log2(100) / math.log(2)
check("delta = 1%: the best integer k at m/n = 9.585 is 7", min(range(1, 20), key=lambda k: approx(c1, k)) == 7)
check("delta = 1%: m/n = lg(100)/ln 2 = 9.585 and k = ceil(lg 100) = 7 give an estimate of 1.004% -- slightly ABOVE "
      "delta; no integer k reaches 1% at that size",
      abs(c1 - 9.585) < 1e-3 and 0.01003 < approx(c1, 7) < 0.01005 and min(approx(c1, k) for k in range(1, 20)) > 0.01,
      f"{approx(c1, 7):.6f}")
rows = []
ok_rule = True
for delta in (0.5, 0.25, 0.1, 0.05, 0.01, 1e-3, 1e-4, 1e-6):
    c = math.log2(1 / delta) / math.log(2)
    k = math.ceil(math.log2(1 / delta))
    r = approx(c, k) / delta
    rows.append(f"{delta:g}: {r:.4f}")
    integral = abs(math.log2(1 / delta) - round(math.log2(1 / delta))) < 1e-12
    ok_rule &= (abs(r - 1) < 1e-9) if integral else (1 < r < 1.03)
check("the sizing rule m = ceil(n lg(1/delta)/ln 2), k = ceil(lg(1/delta)) gives exactly delta when lg(1/delta) is "
      "an integer and up to 3% more otherwise (ratio estimate/delta)", ok_rule, "; ".join(rows))
check("m = n lg(1/delta)/ln 2 = 1.44 n lg(1/delta) bits", abs(1 / math.log(2) - 1.4427) < 1e-4)
fp_10k = fp_exact_float(10000, 7, 1000)
fp_32k = fp_exact_float(32000, 22, 1000)
check("exact false-positive rate, n = 1000, m = 10000, k = 7: 0.82%, just above the estimate",
      approx(10, 7) < fp_10k < approx(10, 7) * 1.01, f"{fp_10k:.6f} vs {approx(10, 7):.6f}")
check("exact false-positive rate, n = 1000, m = 32000, k = 22: 2.1e-7, just above the estimate",
      approx(32, 22) < fp_32k < approx(32, 22) * 1.05, f"{fp_32k:.4e} vs {approx(32, 22):.4e}")
# simulation of real filters
sims = []
for _ in range(20):
    n, m, k = 1000, 10000, 7
    B = np.zeros(m, dtype=bool)
    B[RNG.integers(0, m, (n, k)).ravel()] = True
    q = RNG.integers(0, m, (20000, k))
    sims.append(float(np.mean(B[q].all(axis=1))))
check("simulation: 20 filters with n = 1000, m = 10000, k = 7 and 20000 queries each: false positives 0.82% +- 0.05%",
      abs(np.mean(sims) - fp_10k) < 5e-4, f"{np.mean(sims):.5f}")
# table on the concept page: bits per item -> best integer k and its estimated rate
table = {}
for c in (4, 8, 10, 16):
    kb = min(range(1, 30), key=lambda k: approx(c, k))
    table[c] = (kb, approx(c, kb))
check("bits per key c = 4, 8, 10, 16: best integer k = 3, 6, 7, 11 with estimated rates 14.7%, 2.16%, 0.82%, 0.046%",
      [table[c][0] for c in (4, 8, 10, 16)] == [3, 6, 7, 11]
      and [round(100 * table[c][1], 3 if c == 16 else 2) for c in (4, 8, 10, 16)] == [14.69, 2.16, 0.82, 0.046],
      str({c: (k, f"{100 * v:.4f}%") for c, (k, v) in table.items()}))

print("== §6.4 The count-min sketch")


class CountMin:
    def __init__(self, w, d, hs):
        self.w, self.d, self.hs = w, d, hs
        self.C = [[0] * w for _ in range(d)]

    def increment(self, x):
        for i in range(self.d):
            self.C[i][self.hs[i](x)] += 1

    def estimate(self, x):
        est = math.inf
        for i in range(self.d):
            est = min(est, self.C[i][self.hs[i](x)])
        return est


# figure example
CM_STREAM = list("abacadba")
CM_H = {"a": (0, 3, 1), "b": (2, 1, 4), "c": (3, 1, 0), "d": (2, 3, 0)}
cm = CountMin(5, 3, [lambda x, i=i: CM_H[x][i] for i in range(3)])
for x in CM_STREAM:
    cm.increment(x)
check("figure example: stream a b a c a d b a (N = 8) into 3 rows of 5 counters gives rows "
      "[4,0,3,1,0], [0,3,0,5,0], [2,4,0,0,2]",
      cm.C == [[4, 0, 3, 1, 0], [0, 3, 0, 5, 0], [2, 4, 0, 0, 2]])
f = Counter(CM_STREAM)
check("figure example: estimates a 4, b 2, c 1 (exact) and d = min(3, 5, 2) = 2 > f_d = 1",
      [cm.estimate(x) for x in "abcd"] == [4, 2, 1, 2] and [f[x] for x in "abcd"] == [4, 2, 1, 1])
# never an underestimate
ok = True
for _ in range(200):
    w, d = random.randint(1, 10), random.randint(1, 5)
    tabs = [dict() for _ in range(d)]
    hs = [lambda x, t=t, w=w: t.setdefault(x, random.randrange(w)) for t in tabs]
    cmr = CountMin(w, d, hs)
    S = [random.randrange(30) for _ in range(random.randint(0, 100))]
    for x in S:
        cmr.increment(x)
    fr = Counter(S)
    ok &= all(cmr.estimate(x) >= fr[x] for x in range(30))
    ok &= all(cmr.C[i][hs[i](x)] == fr[x] + sum(fr[y] for y in fr if y != x and hs[i](y) == hs[i](x))
              for x in range(30) for i in range(d))
check("CMEstimate never underestimates, and Count[i, h_i(x)] = f_x + X_{i,x} exactly (200 random sketches)", ok)
# per-row bound exactly over all salts of a universal family (MB+ with p = 31)
p = 31
ok_row = True
ok_strict = True
for w in (3, 5, 8):
    for _ in range(5):
        S = [random.choice(range(p)) for _ in range(40)]
        fr = Counter(S)
        N = len(S)
        x = random.choice(list(fr))
        Xs = []
        for a in range(1, p):
            for b in range(p):
                hx = ((a * x + b) % p) % w
                Xs.append(sum(fr[y] for y in fr if y != x and ((a * y + b) % p) % w == hx))
        EX = Fr(sum(Xs), len(Xs))
        ok_row &= EX <= Fr(N, w)
        for eps in (Fr(1, 4), Fr(1, 2), Fr(9, 10)):
            ok_row &= Fr(sum(1 for v in Xs if v > eps * N), len(Xs)) <= EX / (eps * N) <= 1 / (w * eps)
            pr_ = Fr(sum(1 for v in Xs if v > eps * N), len(Xs))
            ok_strict &= pr_ == 0 or pr_ < EX / (eps * N)   # R29: Markov is strict here
check("one row, over every salt of the universal family ((ax+b) mod 31) mod w: E[X_{i,x}] <= N/w and "
      "Pr[X_{i,x} > eps N] <= E[X]/(eps N) <= 1/(w eps) (exact)", ok_row)
check("the note's strict claim '< delta' holds: Pr[X_{i,x} > eps N] is 0 or strictly below E[X]/(eps N) "
      "(same exact computation), so the product over d rows is strictly below (1/(w eps))^d <= delta", ok_strict)
# parameters
for eps, delta, wexp, dexp in [(0.01, 0.001, 272, 7), (0.05, 0.05, 55, 3), (0.1, 0.01, 28, 5)]:
    w, d = math.ceil(math.e / eps), math.ceil(math.log(1 / delta))
    check(f"eps = {eps}, delta = {delta}: w = ceil(e/eps) = {wexp}, d = ceil(ln(1/delta)) = {dexp}, "
          f"{wexp * dexp} counters, and (1/(w eps))^d <= delta",
          (w, d) == (wexp, dexp) and (1 / (w * eps)) ** d <= delta)
# simulation of the guarantee
eps, delta = 0.05, 0.05
w, d = math.ceil(math.e / eps), math.ceil(math.log(1 / delta))
P = 2 ** 31 - 1
fails, total, worst_over = 0, 0, 0.0
for trial in range(60):
    zipf = RNG.zipf(1.3, 3000)
    S = [int(v) % 500 for v in zipf]
    fr = Counter(S)
    N = len(S)
    salts = [(int(RNG.integers(1, P)), int(RNG.integers(0, P))) for _ in range(d)]
    C = np.zeros((d, w), dtype=np.int64)
    items = np.array(sorted(fr))
    cnts = np.array([fr[x] for x in items])
    for i, (a, b) in enumerate(salts):
        hv = ((a * items + b) % P) % w
        np.add.at(C[i], hv, cnts)
    for x in range(500):
        est = min(int(C[i][((a * x + b) % P) % w]) for i, (a, b) in enumerate(salts))
        over = est - fr.get(x, 0)
        fails += over > eps * N
        total += 1
        worst_over = max(worst_over, over / N)
check(f"simulation, eps = delta = 0.05 (w = {w}, d = {d}), Zipf streams of 3000 items, 60 sketches x 500 queries: "
      f"the fraction of estimates above f_x + eps N is at most delta", fails / total <= delta,
      f"{fails}/{total} = {fails / total:.4f}; largest overestimate {worst_over:.3f} N")

print("== §6.5 / Exercise 2: estimating distinct items with m / min h")
ok_a, ok_b, rows = True, True, []
for p in (1009, 2003):
    for n in (5, 20, 50):
        S = np.array(random.sample(range(p), n))
        bvec = np.arange(p)
        cnt_over, cnt_under = Counter(), Counter()
        for a in range(p):
            mn = ((a * S[:, None] + bvec[None, :]) % p).min(axis=0)
            est = np.where(mn == 0, np.inf, p / np.maximum(mn, 1))
            for e in (0.1, 0.5, 0.9):
                cnt_over[e] += int((est > (1 + e) * n).sum())
                cnt_under[e] += int((est < (1 - e) * n).sum())
        for e in (0.1, 0.5, 0.9):
            po, pu = cnt_over[e] / p ** 2, cnt_under[e] / p ** 2
            ok_a &= po <= 1 / (1 + e)
            ok_b &= pu <= 1 - e
            rows.append(f"p={p},n={n},e={e}: {po:.3f}<= {1 / (1 + e):.3f}, {pu:.3f}<={1 - e:.1f}")
check("Exercise 2(a): Pr[n~ > (1+eps)n] <= 1/(1+eps), exactly over the 2-uniform family (ax+b) mod p, m = p "
      "(p = 1009, 2003; n = 5, 20, 50; eps = 0.1, 0.5, 0.9)", ok_a)
check("Exercise 2(b): Pr[n~ < (1-eps)n] <= 1-eps, same setting", ok_b, rows[4])
check("the family {(ax+b) mod p : a, b in [p]} is 2-uniform (p = 7)",
      all(len(Counter((((a * x + b) % 7), ((a * y + b) % 7)) for a in range(7) for b in range(7))) == 49
          for x in range(7) for y in range(x + 1, 7)))
# round-off matters when m is not large compared with n
S = np.array(random.Random(1).sample(range(211), 50))
bvec = np.arange(211)
over = 0
for a in range(211):
    mn = ((a * S[:, None] + bvec[None, :]) % 211).min(axis=0)
    est = np.where(mn == 0, np.inf, 211 / np.maximum(mn, 1))
    over += int((est > 1.9 * 50).sum())
check("with m = 211 and n = 50 (m not large), bound (a) can fail for eps = 0.9 -- the exercise's 'large m' matters",
      over / 211 ** 2 > 1 / 1.9, f"{over / 211 ** 2:.3f} > {1 / 1.9:.3f}")

# R29: the exercise ignores round-off; min h = 0 (no finite estimate) has probability <= n/m
cnt1 = sum(1 for v in range(1009) if v == 0 or 1009 / v > 1.9)
check("one item, m = p = 1009, eps = 0.9: Pr[n~ > 1.9 n] = 532/1009 > 1/1.9 (bound (a) fails, barely, because "
      "min h = 0 counts as an infinite estimate; without that value it would hold: 531/1009 < 1/1.9)",
      cnt1 == 532 and Fr(532, 1009) > Fr(10, 19) and Fr(531, 1009) < Fr(10, 19))
zero_pr, over_nz = 0, 0
for a in range(211):
    mn = ((a * S[:, None] + bvec[None, :]) % 211).min(axis=0)
    zero_pr += int((mn == 0).sum())
    over_nz += int(((mn > 0) & (211 / np.maximum(mn, 1) > 1.9 * 50)).sum())
check("m = 211, n = 50: Pr[min h = 0] <= n/m, and without that event bound (a) holds -- the failure is the "
      "zero minimum", Fr(zero_pr, 211 ** 2) <= Fr(50, 211) and over_nz / 211 ** 2 <= 1 / 1.9,
      f"Pr[min=0] = {zero_pr / 211 ** 2:.3f}, rest {over_nz / 211 ** 2:.3f}")

# =====================================================================================================
print("== numbers printed on the pages and in the figures")
page = read(PAGE)
concept = read(CONCEPT)
if page:
    check("page quotes 0.61850, 0.82%, 2.1, 1.004%, 9.59", all(t in page for t in ("0.61850", "0.82\\%", "2.1",
                                                                                 "1.004\\%", "9.59")))
    check("page quotes the count-min parameters 272 and 7 (1904 counters)", all(t in page for t in ("272", "1904")))
    check("page quotes 532/1009 for the one-item failure", "532/1009" in page)
if concept:
    check("concept page quotes 14.7%, 2.16%, 0.82%, 0.046%", all(t in concept for t in ("14.7", "2.16", "0.82", "0.046")))
bits = 1e6 * math.log2(100) / math.log(2)
check("concept example: n = 10^6, delta = 1%: m = 1.44 * 10^6 * lg 100 = 9.6e6 bits = 1.2 MB, k = ceil(lg 100) = 7",
      abs(bits / 1e6 - 9.585) < 0.01 and abs(bits / 8 / 1e6 - 1.198) < 0.002 and math.ceil(math.log2(100)) == 7)
check("concept example: 10^7 bits, 10^6 items, 7 functions: estimate 0.82%", round(100 * approx(10, 7), 2) == 0.82)
check("concept page: m/(w eps) <= 1/e when w = ceil(e/eps)", all(1 / (math.ceil(math.e / e) * e) <= 1 / math.e + 1e-15
                                                                  for e in (0.5, 0.1, 0.05, 0.01, 0.003)))
for name in ("n06-bloom", "n06-countmin"):
    check(f"figure {name} exists", os.path.exists(os.path.join(FIGS, name + ".html")))
fig = read(os.path.join(FIGS, "n06-bloom.html"))
if fig:
    bits = re.findall(r'data-bit="(\d+):(\d)"', fig)
    check("figure n06-bloom: the 16 drawn bits are the filter of cat, dog, emu",
          [int(v) for _, v in sorted(bits, key=lambda t: int(t[0]))] == Bf)
fig = read(os.path.join(FIGS, "n06-countmin.html"))
if fig:
    cells = re.findall(r'data-count="(\d+):(\d+):(\d+)"', fig)
    check("figure n06-countmin: the 15 drawn counters are the sketch of the stream",
          len(cells) == 15 and all(cm.C[int(i)][int(j)] == int(v) for i, j, v in cells))

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: " + "; ".join(FAIL))
sys.exit(1 if FAIL else 0)
