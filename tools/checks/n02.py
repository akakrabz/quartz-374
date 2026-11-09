#!/usr/bin/env python3
"""Checks for content/4-lecture-notes/02-nuts-and-bolts.md (Erickson, Director's Cut 2, "Nuts and Bolts").

Every algorithm on the page is implemented as stated, with nut-bolt tests counted. Randomized algorithms are analyzed
EXACTLY: run_all() enumerates every sequence of random choices (each Random(k) branches k ways with probability 1/k)
and returns the exact distribution of the result as Fractions. Closed forms (harmonic numbers) are compared with these
exact expectations for small n and with the exact recurrence for larger n."""
import itertools
import math
import os
import random
import sys
from collections import Counter, defaultdict
from fractions import Fraction as F
from functools import lru_cache

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import figs_n02 as FIG  # noqa: E402

sys.setrecursionlimit(10000)
FAIL = []


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAIL.append(name)


rng = random.Random(374)


@lru_cache(maxsize=None)
def H(n):
    return sum((F(1, k) for k in range(1, n + 1)), F(0))


class Need(Exception):
    pass


def run_all(algo, *args):
    """Exact distribution of algo(rnd, *args) over all random choices: list of (probability, result).
    rnd(k) returns a uniformly random integer in 1..k."""
    out = []
    stack = [()]
    while stack:
        prefix = stack.pop()
        state = {"pos": 0, "prob": F(1)}

        def rnd(k, prefix=prefix, state=state):
            i = state["pos"]
            if i < len(prefix):
                state["pos"] += 1
                state["prob"] /= k
                return prefix[i]
            raise Need(k)

        try:
            res = algo(rnd, *args)
        except Need as e:
            k = e.args[0]
            for v in range(1, k + 1):
                stack.append(prefix + (v,))
            continue
        out.append((state["prob"], res))
    assert sum(p for p, _ in out) == 1
    return out


def expect(dist, f=lambda r: r):
    return sum((p * f(r) for p, r in dist), F(0))


# =====================================================================================================
# nuts and bolts: sizes are ranks 1..n; bolt b fits nut x iff b == x
# =====================================================================================================
def test(bolt, nut, log):
    """One nut-bolt test: -1 if the nut is too small for the bolt, +1 if too big, 0 if it fits."""
    log.append((bolt, nut))
    return (nut > bolt) - (nut < bolt)


# ---- 2.1 / 2.3: one bolt, n nuts
def find_match_det(nuts, target):
    """Test the nuts in the given order; the last nut is never tested. Returns #tests."""
    log = []
    for x in nuts[:-1]:
        if test(target, x, log) == 0:
            return len(log)
    return len(log)


def find_match_rand(rnd, nuts, target):
    """Each step tests a uniformly random untested nut; the last remaining nut is never tested."""
    untested = list(nuts)
    log = []
    while len(untested) > 1:
        x = untested.pop(rnd(len(untested)) - 1)
        if test(target, x, log) == 0:
            return len(log)
    return len(log)


for n in range(1, 8):
    worst = max(find_match_det(list(p), t) for p in itertools.permutations(range(1, n + 1)) for t in range(1, n + 1))
    check(f"2.1 test-every-nut needs exactly n-1 = {n - 1} tests in the worst case (n = {n})", worst == max(n - 1, 0))

for n in range(1, 9):
    for target in {1, n}:
        dist = run_all(find_match_rand, list(range(1, n + 1)), target)
        pk = Counter()
        for p, t in dist:
            pk[t] += p
        if n == 1:
            ok = pk == {0: 1}
        else:
            want = {k: F(1, n) for k in range(1, n - 1)}
            want[n - 1] = want.get(n - 1, 0) + F(2, n)
            ok = dict(pk) == want
        e = expect(dist)
        check(f"2.3 random nut order, n = {n}, target {target}: Pr[T=k] = 1/n (k < n-1), 2/n (k = n-1); "
              f"E[T] = (n+1)/2 - 1/n = {e}", ok and e == F(n + 1, 2) - F(1, n), dict(pk))
        if n >= 2:
            check(f"2.3 T({n}) always between 1 and n-1", min(pk) >= 1 and max(pk) <= n - 1)
# the note's algebra and recurrence
for n in range(2, 60):
    lhs = sum((F(k, n) for k in range(1, n - 1)), F(0)) + F(2 * (n - 1), n)
    mid = sum((F(k, n) for k in range(1, n + 1)), F(0)) - F(1, n)
    check(f"2.3 sum_(k<=n-2) k/n + 2(n-1)/n = sum_(k<=n) k/n - 1/n = (n+1)/2 - 1/n, n = {n}",
          lhs == mid == F(n + 1, 2) - F(1, n)) if n in (2, 3, 4, 10, 59) else None
E = {1: F(0)}
t = {1: 0}
for n in range(2, 200):
    E[n] = 1 + F(n - 1, n) * E[n - 1]
    t[n] = n + t[n - 1]
check("2.3 recurrence E[T(n)] = 1 + (n-1)/n E[T(n-1)], T(1) = 0 gives (n+1)/2 - 1/n for n < 200",
      all(E[n] == F(n + 1, 2) - F(1, n) for n in E))
check("2.3 t(n) = n E[T(n)] satisfies t(n) = n + t(n-1), t(1) = 0, so t(n) = n(n+1)/2 - 1",
      all(t[n] == n * E[n] == F(n * (n + 1), 2) - 1 for n in t))


# ---- 2.4: all matches
def repeated_find_det(bolts, nuts):
    """For each bolt in turn, test the remaining nuts in order (the last one untested). Returns #tests."""
    nuts = list(nuts)
    total = 0
    for b in bolts:
        log = []
        found = None
        for x in nuts[:-1]:
            if test(b, x, log) == 0:
                found = x
                break
        if found is None:
            found = nuts[-1]
        nuts.remove(found)
        total += len(log)
    return total


for n in range(1, 8):
    worst = max(repeated_find_det(list(range(1, n + 1)), list(p)) for p in itertools.permutations(range(1, n + 1)))
    check(f"2.4 repeated single matching: worst case sum (i-1) = (n^2-n)/2 = {(n * n - n) // 2} tests (n = {n})",
          worst == (n * n - n) // 2)


def partition_step(b, bolts, nuts, log):
    """Pivot bolt b against every nut (|nuts| tests), then its nut against every other bolt (|bolts|-1 tests)."""
    sn, ln, nb = [], [], None
    for x in nuts:
        c = test(b, x, log)
        if c == 0:
            nb = x
        elif c < 0:
            sn.append(x)
        else:
            ln.append(x)
    sb, lb = [], []
    for y in bolts:
        if y == b:
            continue
        c = test(y, nb, log)          # nut nb compared with bolt y
        if c > 0:                      # nut too big for y: y is smaller
            sb.append(y)
        else:
            lb.append(y)
    return (b, nb), (sb, sn), (lb, ln)


def match_det(bolts, nuts, log):
    """Rawlins' algorithm with the FIRST bolt as pivot."""
    if not bolts:
        return []
    pair, (sb, sn), (lb, ln) = partition_step(bolts[0], bolts, nuts, log)
    return match_det(sb, sn, log) + [pair] + match_det(lb, ln, log)


def match_rand(rnd, bolts, nuts, log=None):
    """Rawlins' algorithm with a uniformly random pivot bolt. Returns (#tests, frozenset of tested pairs, pairs)."""
    top = log is None
    if top:
        log = []
    if bolts:
        b = bolts[rnd(len(bolts)) - 1]
        pair, (sb, sn), (lb, ln) = partition_step(b, bolts, nuts, log)
        pairs = match_rand(rnd, sb, sn, log)[2] + [pair] + match_rand(rnd, lb, ln, log)[2]
    else:
        pairs = []
    return (len(log), frozenset(log), pairs)


for n in range(1, 8):
    worst = 0
    allok = True
    for bo in itertools.permutations(range(1, n + 1)):
        log = []
        pairs = match_det(list(bo), list(reversed(range(1, n + 1))), log)
        allok &= pairs == [(i, i) for i in range(1, n + 1)]
        worst = max(worst, len(log))
    check(f"2.4 Rawlins' partitioning (first bolt as pivot) matches and sorts; worst case n^2 = {n * n} tests (n = {n})",
          allok and worst == n * n, worst)
W = {0: 0}
for n in range(1, 120):
    W[n] = 2 * n - 1 + max(W[k - 1] + W[n - k] for k in range(1, n + 1))
check("2.4 worst-case recurrence T(n) = 2n-1 + max_k (T(k-1)+T(n-k)) = 2n-1 + T(n-1) = sum (2i-1) = n^2",
      all(W[n] == n * n == 2 * n - 1 + W[n - 1] == sum(2 * i - 1 for i in range(1, n + 1)) for n in range(1, 120)))
check("2.4 the note's sum as printed, sum_(i=1..n) (2n-1), is n(2n-1), not n^2 (n = 5: 45 vs 25)",
      sum(2 * 5 - 1 for i in range(1, 6)) == 45 != 25)
def smallest_pivot_skipping(nuts):
    """Reviewer (R25): Rawlins' partitioning with the smallest bolt as pivot, skipping every test whose outcome is
    already known (the last nut when no earlier nut fitted; all nut-side tests, since every other nut turned out
    larger, so the pivot nut is the smallest). Returns #tests."""
    if not nuts:
        return 0
    b = min(nuts)
    tests = 0
    found = False
    for idx, x in enumerate(nuts):
        if idx == len(nuts) - 1 and not found:
            break                        # the last nut must be the match
        tests += 1
        found |= x == b
    return tests + smallest_pivot_skipping([x for x in nuts if x != b])


ok = True
for n in range(1, 8):
    costs = [smallest_pivot_skipping(list(p)) for p in itertools.permutations(range(1, n + 1))]
    ok &= min(costs) == n * (n - 1) // 2
check("2.4 skipping known outcomes, always-smallest pivots still cost at least sum (m-1) = n(n-1)/2 tests "
      "(attained), over all nut orders, n <= 7", ok)

# ---- 2.6 / 2.7: randomized matching, exactly
T = {0: F(0)}
for n in range(1, 301):
    T[n] = 2 * n - 1 + F(1, n) * sum((T[k - 1] + T[n - k] for k in range(1, n + 1)), F(0))
closed = {n: 4 * n * H(n) - 7 * n + 4 * H(n) for n in range(0, 301)}
check("2.6 recurrence T(n) = 2n-1 + (1/n) sum_k (T(k-1)+T(n-k)), T(0) = 0, equals 4nH_n - 7n + 4H_n for n <= 300",
      all(T[n] == closed[n] for n in T))
check("2.6 T(1) = 1 in this 'stupid' version (one test of the lone bolt against its nut)", T[1] == 1)

for n in range(1, 8):
    bolts = list(range(1, n + 1))
    nuts = list(range(1, n + 1))
    rng.shuffle(bolts)
    rng.shuffle(nuts)
    dist = run_all(match_rand, bolts, nuts)
    e = expect(dist, lambda r: r[0])
    sorted_ok = all(r[2] == [(i, i) for i in range(1, n + 1)] for _, r in dist)
    check(f"2.7 randomized matching, n = {n}: exact E[tests] = {e} = 4nH_n - 7n + 4H_n, and every run matches+sorts",
          e == closed[n] and sorted_ok)
    # comparison probabilities
    pij = defaultdict(F)
    for p, r in dist:
        for pr in r[1]:
            pij[pr] += p
    ok = all(pij[(i, j)] == (F(1) if i == j else F(2, abs(i - j) + 1)) for i in range(1, n + 1)
             for j in range(1, n + 1))
    check(f"2.7 Pr[B_i compared with N_j] = 2/(|i-j|+1) (i != j), 1 (i = j), n = {n}", ok)
    # every pair tested at most once
    check(f"2.7 no nut-bolt pair is tested twice, n = {n}",
          all(len(r[1]) == r[0] for _, r in dist))
    # input order does not matter
    bolts2, nuts2 = sorted(bolts, reverse=True), sorted(nuts)
    dist2 = run_all(match_rand, bolts2, nuts2)
    c1, c2 = Counter(), Counter()
    for p, r in dist:
        c1[r[1]] += p
    for p, r in dist2:
        c2[r[1]] += p
    check(f"2.7 the distribution of the set of tested pairs does not depend on the input order, n = {n}", c1 == c2)
    # iterative version: uniform pivot order over all n! permutations
    if n <= 7:
        c3 = Counter()
        lemma = True
        for order in itertools.permutations(range(1, n + 1)):
            nodes = FIG.iterative_tree(n, list(order))
            logset = set()
            for sub, p, step, par, side in nodes:
                for x in sub:
                    logset.add((p, x))        # pivot bolt p vs every nut in the block
                    if x != p:
                        logset.add((x, p))    # nut p vs every other bolt in the block
            c3[frozenset(logset)] += F(1, math.factorial(n))
            for i in range(1, n + 1):
                for j in range(1, n + 1):
                    lo, hi = min(i, j), max(i, j)
                    first = next(v for v in order if lo <= v <= hi)
                    lemma &= (((i, j) in logset) == (first in (i, j)))
        check(f"2.7 iterative version with a uniformly random pivot order performs the same tests "
              f"(same distribution of tested-pair sets), n = {n}", c3 == c1)
        check(f"2.7 key lemma: B_i and N_j are compared iff the first pivot drawn from ranks i..j is i or j, "
              f"for all {math.factorial(n)} orders, n = {n}", lemma)

for n in range(1, 301):
    s1 = n + 4 * sum((F(1, j - i + 1) for i in range(1, n + 1) for j in range(i + 1, n + 1)), F(0)) if n <= 60 else None
    s2 = n + 4 * sum((F(1, k) for i in range(1, n + 1) for k in range(2, n - i + 2)), F(0)) if n <= 60 else None
    s3 = n + 4 * sum((F(n - k + 1, k) for k in range(2, n + 1)), F(0))
    s4 = n + 4 * ((n + 1) * (H(n) - 1) - (n - 1))
    if n <= 60:
        assert s1 == s2
    if not (s3 == s4 == closed[n] and (n > 60 or s1 == s3)):
        check(f"2.7 summation steps, n = {n}", False)
        break
else:
    check("2.7 each line of the summation (substitute k = j-i+1, reorder, (n+1)(H_n-1)-(n-1)) equals 4nH_n - 7n + 4H_n "
          "(n <= 60 all lines, n <= 300 the last three)", True)

# ---- 2.8 masochistic analysis
ok = True
for n in range(1, 301):
    ok &= T[n] == F(2, n) * sum((T[k] for k in range(n)), F(0)) + 2 * n - 1
    ok &= n * T[n] - (n - 1) * T[n - 1] == 2 * T[n - 1] + 4 * n - 3
    ok &= T[n] == F(n + 1, n) * T[n - 1] + 4 - F(3, n)
    tn, tm = T[n] / (n + 1), T[n - 1] / n
    ok &= tn == tm + F(4, n + 1) - F(3, n * (n + 1)) == tm + F(7, n + 1) - F(3, n)
    ok &= tn == sum((F(7, i + 1) - F(3, i) for i in range(1, n + 1)), F(0)) == 7 * (H(n + 1) - 1) - 3 * H(n)
    ok &= tn == 4 * H(n) - 7 + F(7, n + 1)
    ok &= T[n] == 4 * (n + 1) * H(n) - 7 * (n + 1) + 7
    ok &= (n - 1) * T[n - 1] == 2 * sum((T[k] for k in range(n - 1)), F(0)) + 2 * n * n - 5 * n + 3
check("2.8 every step of the masochistic derivation holds exactly for n <= 300 (full-history form, shift-and-subtract, "
      "T(n) = (n+1)/n T(n-1) + 4 - 3/n, t(n) = t(n-1) + 7/(n+1) - 3/n, t(n) = 4H_n - 7 + 7/(n+1))", ok)

# ---- 2.6: convexity, good pivots, the conservative recurrence
check("2.6 T is convex: T(n+1) + T(n-1) - 2T(n) = 4/(n+1) > 0 for 1 <= n < 300",
      all(T[n + 1] + T[n - 1] - 2 * T[n] == F(4, n + 1) for n in range(1, 300)))


def good_fraction(n):
    return F(sum(1 for r in range(1, n + 1) if F(r - 1) >= F(n, 4) and F(n - r) >= F(n, 4)), n)


check("2.6 a uniformly random pivot is good (>= n/4 bolts on each side) with probability exactly 1/2 when 4 | n",
      all(good_fraction(n) == F(1, 2) for n in range(4, 400, 4)))
check("2.6 ... but not for other n (n = 5: 1/5, n = 6: 1/3); the fraction tends to 1/2",
      good_fraction(5) == F(1, 5) and good_fraction(6) == F(1, 3) and abs(good_fraction(9999) - F(1, 2)) < F(1, 1000),
      f"{good_fraction(5)}, {good_fraction(6)}, {float(good_fraction(9999)):.4f}")
ok = True
for trial in range(2000):      # reviewer (R25): replaces a check that was literally True
    nn, a, b, tv = rng.randint(1, 50), F(rng.randint(0, 999), 7), F(rng.randint(0, 999), 7), F(rng.randint(0, 3000), 7)
    ok &= (tv <= 2 * nn - 1 + (a + b) / 2 + tv / 2) == (tv <= 4 * nn - 2 + a + b)
check("2.6 algebra: T <= 2n-1 + (T(3n/4)+T(n/4))/2 + T(n)/2  <=>  T <= 4n-2 + T(3n/4) + T(n/4) (2000 random values)",
      ok)
check("2.6 the exact T satisfies T(n) <= 4n-2 + T(3n/4) + T(n/4) for every multiple of 4 up to 300",
      all(T[n] <= 4 * n - 2 + T[3 * n // 4] + T[n // 4] for n in range(4, 301, 4)))
Tc = {}


def Tcons(n):
    if n < 4:
        return float(n * n)
    if n in Tc:
        return Tc[n]
    v = 4 * n - 2 + Tcons(3 * n // 4) + Tcons(n // 4)
    Tc[n] = v
    return v


cons = 4 / -(0.75 * math.log(0.75) + 0.25 * math.log(0.25))
dev = [Tcons(4 ** k) / 4 ** k - cons * math.log(4 ** k) for k in range(10, 36)]
check("2.6 the conservative recurrence T(n) = 4n - 2 + T(3n/4) + T(n/4) solves to Theta(n log n): "
      "T(n)/n - c ln n stays bounded for n = 4^10 .. 4^35, c = 4/(-(3/4)ln(3/4) - (1/4)ln(1/4)) ≈ 7.11",
      max(dev) - min(dev) < 0.5 and abs(cons - 7.11) < 0.01, f"c = {cons:.4f}, range {min(dev):.3f} .. {max(dev):.3f}")


def Hf(n):
    return math.log(n) + 0.5772156649015329 + 1 / (2 * n) - 1 / (12 * n * n)


ratio = (4 * 10 ** 7 * Hf(10 ** 7) - 7 * 10 ** 7 + 4 * Hf(10 ** 7)) / (10 ** 7 * math.log(10 ** 7))
check("2.7 4nH_n - 7n + 4H_n = Theta(n log n): ratio to n ln n at n = 10^7 is about 4 (it tends to 4)",
      3.7 < ratio < 4.0, round(ratio, 4))
check("2.7 numbers: E[T(7)] = 32H_7 - 49 ≈ 33.97, E[T(8)] = 36H_8 - 56 = 2929/70 ≈ 41.84",
      round(float(closed[7]), 2) == 33.97 and closed[8] == F(2929, 70) and round(float(closed[8]), 2) == 41.84)

check("2.7 examples: 1, 4, 25/3, 41/3 expected tests for n = 1..4",
      [closed[n] for n in (1, 2, 3, 4)] == [1, 4, F(25, 3), F(41, 3)])
# ---- figures
nodes = FIG.iterative_tree(FIG.N_TREE, FIG.PIVOT_ORDER)
tot = sum(2 * len(sub) - 1 for sub, *_ in nodes)
check("figure tree: pivot order 3,6,1,5,2,7,4 gives blocks {1..7},{4..7},{1,2},{4,5},{2},{7},{4} and 29 tests",
      [sub for sub, *_ in nodes] == [(1, 2, 3, 4, 5, 6, 7), (4, 5, 6, 7), (1, 2), (4, 5), (2,), (7,), (4,)] and tot == 29,
      tot)
logset = set()
for sub, p, *_ in nodes:
    for x in sub:
        logset.add((p, x))
        if x != p:
            logset.add((x, p))
check("figure tree: bolt 2 and nut 5 are never compared; bolt 4 and nut 5 are (when 5 is the pivot of {4,5})",
      (2, 5) not in logset and (4, 5) in logset and len(logset) == 29)
mat = sum((F(1) if i == j else F(2, abs(i - j) + 1) for i in range(1, 9) for j in range(1, 9)), F(0))
check("figure matrix: the 64 entries 2/(|i-j|+1) (1 on the diagonal) sum to 36H_8 - 56 = 2929/70",
      mat == closed[8] == F(2929, 70))

# =====================================================================================================
# 2.5: reductions to and from sorting
# =====================================================================================================
for trial in range(300):
    n = rng.randint(1, 60)
    bolts_sorted = list(range(1, n + 1))
    nuts = list(range(1, n + 1))
    rng.shuffle(nuts)
    log = []
    ok = True
    maxtests = 0
    for x in nuts:
        lo, hi = 0, n - 1
        before = len(log)
        found = None
        while lo <= hi:
            mid = (lo + hi) // 2
            c = test(bolts_sorted[mid], x, log)
            if c == 0:
                found = bolts_sorted[mid]
                break
            elif c < 0:
                hi = mid - 1
            else:
                lo = mid + 1
        ok &= found == x
        maxtests = max(maxtests, len(log) - before)
    if not (ok and maxtests <= n.bit_length()):
        break
check("2.5 sorted bolts => match every nut by binary search with at most floor(log2 n)+1 tests each (300 random "
      "instances, n <= 60)", ok and maxtests <= n.bit_length())


def merge_sort_pairs(P, log):
    if len(P) <= 1:
        return P
    m = len(P) // 2
    A, B = merge_sort_pairs(P[:m], log), merge_sort_pairs(P[m:], log)
    out = []
    i = j = 0
    while i < len(A) and j < len(B):
        # pair A[i] before pair B[j] iff bolt of A[i] is smaller than nut of B[j]
        if test(A[i][0], B[j][1], log) > 0:
            out.append(A[i])
            i += 1
        else:
            out.append(B[j])
            j += 1
    return out + A[i:] + B[j:]


ok = True
for trial in range(300):
    n = rng.randint(1, 60)
    P = [(i, i) for i in range(1, n + 1)]
    rng.shuffle(P)
    ok &= merge_sort_pairs(P, []) == sorted(P)
check("2.5 matched pairs => mergesort using only nut-bolt tests (bolt of one pair vs nut of the other) sorts them",
      ok)

# =====================================================================================================
# Quicksort (Algorithms §1.5) with a random pivot: expected comparisons 2(n+1)H_n - 4n
# =====================================================================================================
def quicksort_rand(rnd, A):
    A = list(A)
    cnt = [0]

    def qs(lo, hi):          # sort A[lo..hi], 0-indexed inclusive
        n = hi - lo + 1
        if n > 1:
            p = lo + rnd(n) - 1
            A[p], A[hi] = A[hi], A[p]
            ell = lo - 1
            for i in range(lo, hi):
                cnt[0] += 1
                if A[i] < A[hi]:
                    ell += 1
                    A[ell], A[i] = A[i], A[ell]
            A[hi], A[ell + 1] = A[ell + 1], A[hi]
            r = ell + 1
            qs(lo, r - 1)
            qs(r + 1, hi)

    qs(0, len(A) - 1)
    return cnt[0], tuple(A)


for n in range(1, 8):
    A = list(range(1, n + 1))
    rng.shuffle(A)
    dist = run_all(quicksort_rand, A)
    e = expect(dist, lambda r: r[0])
    check(f"quicksort with a uniformly random pivot (Lomuto partition, n-1 comparisons), n = {n}: exact E[comparisons] "
          f"= {e} = 2(n+1)H_n - 4n; nuts-and-bolts = n + 2 x this",
          e == 2 * (n + 1) * H(n) - 4 * n and closed[n] == n + 2 * e and all(r[1] == tuple(range(1, n + 1))
                                                                            for _, r in dist))
check("quicksort: 2(n+1)H_n - 4n ~ 2n ln n ≈ 1.39 n log2 n", abs(2 * math.log(2) - 1.386) < 0.001)

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: " + "; ".join(FAIL))
