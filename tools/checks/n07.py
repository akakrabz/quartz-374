#!/usr/bin/env python3
"""Checks for content/4-lecture-notes/07-string-matching.md and content/concepts/string-matching.md
(Erickson, Director's Cut 7, "String Matching").

Every algorithm of the note is transcribed with 1-based arrays exactly as printed — AlmostBruteForce, NumberSearch,
KarpRabin (random prime modulus), CarterWegmanKarpRabin (random radix), KnuthMorrisPratt, ComputeFailure,
OptimizeFailure, ComputeOptFailure — and compared with a brute-force reference on all short texts and patterns over
small alphabets. Failure functions are compared with their definition (longest proper border, O(m^3)), the recursive
definition and the "optimized" definition; every failure-function table of the note is recomputed (one entry is
wrong); the ComputeFailure trace of p. 9 is replayed; comparison counts are checked against the stated bounds; the
Karp-Rabin false-match bounds are checked exactly (prime divisors, polynomial roots) and numerically; the KMP automaton
is built as a DFA and checked against "contains P" and for minimality with tools/automata; every example on the pages
(including the HOCUSPOCUS shifts, where the note is off by one) is recomputed."""
import itertools
import math
import os
import random
import re
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
from automata import DFA, NFA, strings  # noqa: E402

ROOT = os.path.join(HERE, "..", "..")
PAGE = os.path.join(ROOT, "content", "4-lecture-notes", "07-string-matching.md")
CONCEPT = os.path.join(ROOT, "content", "concepts", "string-matching.md")
FIGS = os.path.join(HERE, "..", "figs")
FAIL = []
random.seed(7374)


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAIL.append(name)


def read(path):
    return open(path, encoding="utf-8").read() if os.path.exists(path) else ""


# =====================================================================================================
# Reference
def first_match(T, P):
    """Smallest 1-based shift s with T[s .. s+m-1] = P, or None."""
    k = T.find(P)
    return None if k < 0 else k + 1


def all_texts(alpha, maxlen, minlen=0):
    for L in range(minlen, maxlen + 1):
        for t in itertools.product(alpha, repeat=L):
            yield "".join(t)


# =====================================================================================================
# 7.1 AlmostBruteForce (p. 2), with a comparison counter
def almost_brute_force(T, P):
    n, m = len(T), len(P)
    T1, P1 = " " + T, " " + P
    comps = 0
    for s in range(1, n - m + 2):
        equal, i = True, 1
        while equal and i <= m:
            comps += 1
            if T1[s + i - 1] != P1[i]:
                equal = False
            else:
                i += 1
        if equal:
            return s, comps
    return None, comps


# 7.2 NumberSearch (p. 3) on decimal digits; T[n+1] is read by the last update: record it, use 0.
def number_search(T, P):
    n, m = len(T), len(P)
    Td = [None] + [int(c) for c in T]
    Pd = [None] + [int(c) for c in P]
    oob = [False]

    def Tat(k):
        if k > n:
            oob[0] = True
            return 0
        return Td[k]

    sigma = 10 ** (m - 1)
    p, t = 0, 0
    for i in range(1, m + 1):
        p = 10 * p + Pd[i]
        t = 10 * t + Tat(i)
    for s in range(1, n - m + 2):
        if p == t:
            return s, oob[0]
        t = 10 * (t - sigma * Tat(s)) + Tat(s + m)
    return None, oob[0]


# 7.3 KarpRabin (p. 4) for a given prime q; counts false matches; also checks every fingerprint against the direct value
def karp_rabin(T, P, q, check_rolling=False):
    n, m = len(T), len(P)
    Td = [None] + [int(c) for c in T] + [0]
    Pd = [None] + [int(c) for c in P]
    sigma = pow(10, m - 1, q)
    pt, tt = 0, 0
    for i in range(1, m + 1):
        pt = (10 * pt % q + Pd[i]) % q
        tt = (10 * tt % q + Td[i]) % q
    F = 0
    rolling_ok = True
    for s in range(1, n - m + 2):
        if check_rolling and tt != int(T[s - 1:s - 1 + m]) % q:
            rolling_ok = False
        if pt == tt:
            if P == T[s - 1:s - 1 + m]:
                return s, F, rolling_ok
            F += 1
        tt = (10 * (tt - sigma * Td[s] % q) % q + Td[s + m]) % q
    return None, F, rolling_ok


# 7.3 CarterWegmanKarpRabin (p. 5): characters given as integers (list), prime q, radix b
def cwkr(T, P, q, b):
    n, m = len(T), len(P)
    Td = [None] + list(T) + [0]
    Pd = [None] + list(P)
    sigma = pow(b, m - 1, q)
    pt, tt = 0, 0
    for i in range(1, m + 1):
        pt = (b * pt % q + Pd[i]) % q
        tt = (b * tt % q + Td[i]) % q
    F = 0
    for s in range(1, n - m + 2):
        if pt == tt:
            if list(P) == list(T[s - 1:s - 1 + m]):
                return s, F
            F += 1
        tt = (b * (tt - sigma * Td[s] % q) % q + Td[s + m]) % q
    return None, F


# 7.5 KnuthMorrisPratt (p. 7): returns (shift, successful comparisons, failed comparisons)
def kmp(T, P, fail):
    n, m = len(T), len(P)
    T1, P1 = " " + T, " " + P
    j = 1
    succ = bad = 0
    for i in range(1, n + 1):
        while j > 0:
            if T1[i] != P1[j]:
                bad += 1
                j = fail[j]
            else:
                succ += 1
                break
        if j == m:
            return i - m + 1, succ, bad
        j += 1
    return None, succ, bad


# 7.6 ComputeFailure (p. 8); also records the p. 9 style trace and the comparisons
def compute_failure(P, trace=None):
    m = len(P)
    P1 = " " + P
    fail = [None] * (m + 1)
    j = 0
    comps = 0
    if trace is not None:
        trace.append(("init", j, 1))
    for i in range(1, m + 1):
        fail[i] = j
        if trace is not None:
            trace.append(("fail", i, j))
        while j > 0:
            comps += 1
            if P1[i] != P1[j]:
                j = fail[j]
                if trace is not None:
                    trace.append(("back", j, i))
            else:
                break
        j += 1
        if trace is not None and i < m:
            trace.append(("adv", j, i + 1))
    return fail, comps


def borders_len(x):
    """Lengths of all proper borders (prefix = suffix, shorter than x), by brute force."""
    return [k for k in range(len(x)) if x[:k] == x[len(x) - k:]]


def fail_def(P):
    """Definition (p. 8): fail[1] = 0; for j > 1, P[1 .. fail[j]-1] is the longest proper prefix of P[1 .. j-1] that
    is also a suffix of it."""
    m = len(P)
    f = [None, 0]
    for j in range(2, m + 1):
        f.append(max(borders_len(P[:j - 1])) + 1)
    return f


def fail_iter(fail, j, c):
    for _ in range(c):
        if j == 0:
            return None
        j = fail[j]
    return j


def fail_recursive(P):
    """Recursive definition (p. 10), with base case i = 1 and the convention that P[0] (the $ node) matches every
    character: fail[i] = max over c >= 1 of fail^c[i-1] + 1 with P[i-1] = P[fail^c[i-1]]."""
    m = len(P)
    P1 = " " + P
    f = [None] * (m + 1)
    f[1] = 0
    for i in range(2, m + 1):
        best = None
        c = 1
        while True:
            k = fail_iter(f, i - 1, c)
            if k is None:
                break
            if k == 0 or P1[i - 1] == P1[k]:
                best = k + 1 if best is None else max(best, k + 1)
            c += 1
        f[i] = best
    return f


# 7.7 OptimizeFailure and ComputeOptFailure (p. 10)
def optimize_failure(P, fail):
    m = len(P)
    P1 = " " + P
    f = list(fail)
    for i in range(2, m + 1):
        if P1[i] == P1[f[i]]:
            f[i] = f[f[i]]
    return f


def compute_opt_failure(P):
    """Printed with 'if P[i] = P[j]' also when j = 0; P[0] must then match nothing (fail[0] does not exist)."""
    m = len(P)
    P1 = " " + P
    fail = [None] * (m + 1)
    j = 0
    for i in range(1, m + 1):
        if j > 0 and P1[i] == P1[j]:
            fail[i] = fail[j]
        else:
            fail[i] = j
        while j > 0 and P1[i] != P1[j]:
            j = fail[j]
        j += 1
    return fail


def opt_def(P):
    """Optimized failure: the first k in the chain fail[j], fail^2[j], ... with k = 0 or P[k] != P[j]."""
    f = fail_def(P)
    P1 = " " + P
    o = [None] * (len(P) + 1)
    for j in range(1, len(P) + 1):
        k = f[j]
        while k > 0 and P1[k] == P1[j]:
            k = f[k]
        o[j] = k
    return o


# KMP automaton as a DFA for "contains P": states 0..m = number of characters matched; m absorbs.
def kmp_dfa_delta(P, fail, alpha):
    m = len(P)
    d = {}

    def step(k, a):
        while True:
            if k < m and P[k] == a:
                return k + 1
            if k == 0:
                return 0
            k = fail[k + 1] - 1

    for k in range(m + 1):
        for a in alpha:
            d[(k, a)] = m if k == m else step(k, a)
    return d


def dfa_def_delta(P, alpha):
    m = len(P)
    d = {}
    for k in range(m + 1):
        for a in alpha:
            if k == m:
                d[(k, a)] = m
                continue
            x = P[:k] + a
            d[(k, a)] = max(L for L in range(0, min(m, len(x)) + 1) if x.endswith(P[:L]))
    return d


# =====================================================================================================
print("== algorithms against brute force, exhaustively ==")
ALPHAS = [("AB", 9, 5), ("ABC", 6, 4)]
bf_ok = kmp_ok = kmpo_ok = cf_ok = rec_ok = opt_ok = optd_ok = True
fewer_ok = True
max_succ = Counter()
max_bad = Counter()
max_tot = Counter()
cf_comps_ok = True
count = 0
for alpha, nmax, mmax in ALPHAS:
    pats = list(all_texts(alpha, mmax, 1))
    for P in pats:
        f, cc = compute_failure(P)
        if f != fail_def(P):
            cf_ok = False
        if cc > 2 * len(P):
            cf_comps_ok = False
        if fail_recursive(P) != f:
            rec_ok = False
        o1 = optimize_failure(P, f)
        o2 = compute_opt_failure(P)
        if not (o1 == o2 == opt_def(P)):
            opt_ok = False
        for T in all_texts(alpha, nmax):
            count += 1
            ref = first_match(T, P)
            if almost_brute_force(T, P)[0] != ref:
                bf_ok = False
            r, sc, bc = kmp(T, P, f)
            if r != ref:
                kmp_ok = False
            r2, sc2, bc2 = kmp(T, P, o2)
            if r2 != ref:
                kmpo_ok = False
            if sc2 + bc2 > sc + bc:
                fewer_ok = False
            n = len(T)
            max_succ[n] = max(max_succ[n], sc)
            max_bad[n] = max(max_bad[n], bc)
            max_tot[n] = max(max_tot[n], sc + bc)
check(f"AlmostBruteForce = brute force on all {count} (text, pattern) pairs (|T| <= 9 over AB, <= 6 over ABC)", bf_ok)
check("ComputeFailure = definition (longest proper border + 1) for every pattern", cf_ok)
check("ComputeFailure makes at most 2m character comparisons", cf_comps_ok)
check("recursive definition (base case i = 1, P[0] matches everything) = ComputeFailure", rec_ok)
check("OptimizeFailure(ComputeFailure) = ComputeOptFailure (P[0] matches nothing) = definition of the optimized function",
      opt_ok)
check("KnuthMorrisPratt with ComputeFailure = brute force on all pairs", kmp_ok)
check("KnuthMorrisPratt with the optimized failure function = brute force on all pairs", kmpo_ok)
check("the optimized failure function never causes more comparisons than the unoptimized one", fewer_ok)
check("KMP: successful comparisons <= n, failed comparisons <= n, total <= 2n - 1 (max over all inputs)",
      all(max_succ[n] <= n and max_bad[n] <= n and max_tot[n] <= max(2 * n - 1, 0) for n in max_succ),
      f"max succ {dict(max_succ)}; max failed {dict(max_bad)}; max total {dict(max_tot)}")
check("the note's 'at most n - 1 successful / n - 1 failed comparisons' is off by one: n successful (T = P = AB), "
      "n failed (T = B, P = A) are possible", kmp("AB", "AB", compute_failure("AB")[0])[1] == 2
      and kmp("B", "A", compute_failure("A")[0])[2] == 1
      and all(max_succ[n] == n and max_bad[n] == n for n in max_succ))
check("2n - 1 is attained for every n >= 1 (bound is tight)", all(max_tot[n] == 2 * n - 1 for n in max_tot if n >= 1),
      str(dict(max_tot)))
# review R26: mismatches are bounded by the increments of j, not by the matches
check("KMP search: mismatches can exceed matches (T = BBB, P = A: 0 matches, 3 mismatches) — they are paid for by "
      "advances of j", kmp("BBB", "A", compute_failure("A")[0])[1:] == (0, 3))


def cf_counts(P):
    """ComputeFailure: (matches, mismatches, increments of j made before the last comparison)."""
    m, P1 = len(P), " " + P
    fail, j, s, b = [None] * (len(P) + 1), 0, 0, 0
    for i in range(1, m + 1):
        fail[i] = j
        while j > 0:
            if P1[i] != P1[j]:
                b += 1
                j = fail[j]
            else:
                s += 1
                break
        j += 1
    return s, b, m - 1


cfc = [(P, *cf_counts(P)) for P in all_texts("AB", 9, 1)]
check("ComputeFailure: mismatches <= increments of j (m - 1), matches <= m, total <= 2m (all patterns over AB, m <= 9); "
      "mismatches can exceed matches (P = AB: 0 and 1)",
      all(b <= inc and s <= len(P) and s + b <= 2 * len(P) for P, s, b, inc in cfc) and cf_counts("AB")[:2] == (0, 1))

# NumberSearch on all short digit strings over {0,1,2}
ns_ok, oob_seen = True, False
for P in all_texts("012", 3, 1):
    for T in all_texts("012", 7):
        r, oob = number_search(T, P)
        if r != first_match(T, P):
            ns_ok = False
        oob_seen = oob_seen or oob
check("NumberSearch = brute force on all digit strings over {0,1,2} (|T| <= 7, |P| <= 3)", ns_ok)
check("NumberSearch/KarpRabin read T[n+1] in the last update when no earlier match ends the loop",
      number_search("12", "3")[1] and not number_search("31", "3")[1])

# Karp–Rabin: for every prime q in a range, on all short digit strings: correct, and false matches = q | p - t_s != 0
def primes_upto(N):
    sieve = bytearray([1]) * (N + 1)
    sieve[0:2] = b"\x00\x00"
    for i in range(2, int(N ** 0.5) + 1):
        if sieve[i]:
            sieve[i * i::i] = bytearray(len(sieve[i * i::i]))
    return [i for i in range(N + 1) if sieve[i]]


PR = primes_upto(200)
kr_ok = fm_ok = roll_ok = True
for P in all_texts("0123", 3, 1):
    for T in random.sample([t for t in all_texts("0123", 6) if len(t) >= len(P)], 300):
        for q in PR[:25]:
            r, F, rok = karp_rabin(T, P, q, check_rolling=True)
            ref = first_match(T, P)
            if r != ref:
                kr_ok = False
            roll_ok = roll_ok and rok
            # count false matches up to the answer
            m = len(P)
            last = (ref if ref else len(T) - m + 1)
            F2 = sum(1 for s in range(1, last + 1) if s != ref and len(T) >= m
                     and (int(P) - int(T[s - 1:s - 1 + m])) % q == 0 and P != T[s - 1:s - 1 + m])
            if F != F2:
                fm_ok = False
check("KarpRabin = brute force for every prime q < 100 (random digit texts, all patterns |P| <= 3 over 0-3)", kr_ok)


# the page's KarpRabin: update only if s < n - m + 1, so T[n+1] is never read
def karp_rabin_page(T, P, q):
    n, m = len(T), len(P)
    Td = [None] + [int(c) for c in T]          # no padding: T[n+1] would raise IndexError
    Pd = [None] + [int(c) for c in P]
    sigma = pow(10, m - 1, q)
    pt = tt = 0
    for i in range(1, m + 1):
        pt = (10 * pt + Pd[i]) % q
        tt = (10 * tt + Td[i]) % q
    for s in range(1, n - m + 2):
        if pt == tt and P == T[s - 1:s - 1 + m]:
            return s
        if s < n - m + 1:
            tt = (10 * (tt - sigma * Td[s]) + Td[s + m]) % q
    return None


check("page's KarpRabin (update guarded by s < n - m + 1) = brute force without reading T[n+1] (all digit strings over "
      "0-2, |T| <= 7, |P| <= 3, primes < 30)",
      all(karp_rabin_page(T, P, q) == first_match(T, P) for P in all_texts("012", 3, 1)
          for T in all_texts("012", 7, len(P)) for q in PR[:10])
      and "if s < n − m + 1" in read(PAGE))
check("rolling update gives t_s mod q at every shift", roll_ok)
check("false match at s  <=>  q divides p - t_s != 0", fm_ok)

# Lemma 2 (p. 4): x has at most floor(lg x) distinct prime divisors
def omega_table(N):
    om = [0] * (N + 1)
    for p in primes_upto(N):
        for k in range(p, N + 1, p):
            om[k] += 1
    return om


OM = omega_table(200000)
check("Lemma 2: every 1 <= x <= 200000 has at most floor(lg x) distinct prime divisors",
      all(OM[x] <= int(math.log2(x)) for x in range(1, 200001)))

# Exact false-match probability bound for the random-prime version, m = 2..6, q uniform among primes <= ceil(m^2 lg m)
rows = []
kr_bound_ok = True
for m in range(2, 7):
    U = math.ceil(m * m * math.log2(m))
    Q = primes_upto(U)
    N = 10 ** m
    cnt = [0] * N  # number of primes q <= U dividing x
    for q in Q:
        for k in range(q, N, q):
            cnt[k] += 1
    worst = max(cnt[1:])
    bound = math.floor(m * math.log2(10))
    if worst > bound:
        kr_bound_ok = False
    rows.append((m, U, len(Q), worst, bound))
check("random prime: Pr[false match at a shift] = #{prime q <= ceil(m^2 lg m) dividing |p - t_s|}/#primes "
      "<= floor(m lg 10)/#primes, m = 2..6", kr_bound_ok, "; ".join(f"m={a}: U={b}, {c} primes, worst {d} <= {e}"
                                                                    for a, b, c, d, e in rows))
# Asymptotically O(1/m): m * floor(m lg 10) / pi(m^2 lg m) stays bounded
PRS = primes_upto(10 ** 7)


def pi_le(u):
    lo, hi = 0, len(PRS)
    while lo < hi:
        mid = (lo + hi) // 2
        if PRS[mid] <= u:
            lo = mid + 1
        else:
            hi = mid
    return lo


ratios = {m: m * math.floor(m * math.log2(10)) / pi_le(math.ceil(m * m * math.log2(m))) for m in (10, 30, 100, 300, 900)}
check("m * floor(m lg 10) / pi(m^2 lg m) stays bounded (about 5): the false-match probability is O(1/m)",
      all(r < 6 for r in ratios.values()), ", ".join(f"m={m}: {r:.2f}" for m, r in ratios.items()))
check("prime number theorem: pi(u) ln u / u in [1, 1.2] for u = 10^4 .. 10^7",
      all(1.0 <= pi_le(u) * math.log(u) / u <= 1.2 for u in (10 ** 4, 10 ** 5, 10 ** 6, 10 ** 7)))

# Polynomial hashing (p. 5): for q prime >= m^2 and character values distinct mod q, at most m - 1 bad radices b
def horner(vals, b, q):
    h = 0
    for v in vals:
        h = (b * h + v) % q
    return h


poly_ok = True
for m, q, sig in ((2, 5, 4), (2, 7, 5), (3, 11, 4), (3, 13, 3), (4, 17, 3)):
    worst = 0
    for Pv in itertools.product(range(sig), repeat=m):
        for Wv in itertools.product(range(sig), repeat=m):
            if Pv == Wv:
                continue
            bad = sum(1 for b in range(q) if horner(Pv, b, q) == horner(Wv, b, q))
            worst = max(worst, bad)
    if not (worst <= m - 1 and (m - 1) * m < q):
        poly_ok = False
check("Carter–Wegman: for P != T_s (characters < q), at most m - 1 of the q radices collide, and (m-1)/q < 1/m "
      "(exhaustive, m = 2..4, q = 5..17)", poly_ok)
# the corrected index range of p(b) matches the Horner loop; the printed one (i = 1..m, needs P[0]) does not
idx_ok = True
for Pv in itertools.product(range(3), repeat=3):
    for b in range(11):
        P1 = (None,) + Pv
        good = sum(b ** i * P1[3 - i] for i in range(0, 3)) % 11
        if good != horner(Pv, b, 11):
            idx_ok = False
check("p(b) = sum_{i=0}^{m-1} b^i P[m-i] equals the Horner loop's fingerprint (the note's sum runs i = 1..m and "
      "reaches P[0])", idx_ok)
# characters equal mod q break the bound: digits with q = 5, m = 2, P = 00, T_s = 55
bad = sum(1 for b in range(5) if horner((0, 0), b, 5) == horner((5, 5), b, 5))
check("counterexample: digits, q = 5 (> m^2 = 4), P = 00, T_s = 55 collide for all 5 radices (needs q > alphabet)",
      bad == 5 and cwkr([5, 5], [0, 0], 5, 3) == (None, 1))
cw_ok = True
for P in all_texts("012", 3, 1):
    for T in all_texts("012", 6, len(P)):
        for q, b in ((11, 0), (11, 3), (13, 7), (17, 16)):
            if cwkr([int(c) for c in T], [int(c) for c in P], q, b)[0] != first_match(T, P):
                cw_ok = False
check("CarterWegmanKarpRabin = brute force for several (q, b), all digit strings over 0-2", cw_ok)

# =====================================================================================================
print("== the note's examples ==")
check("AMANAPLANACATACANALPANAMA: CAN first at shift 15; SPAM: None",
      first_match("AMANAPLANACATACANALPANAMA", "CAN") == 15 and first_match("AMANAPLANACATACANALPANAMA", "SPAM") is None
      and kmp("AMANAPLANACATACANALPANAMA", "CAN", compute_failure("CAN")[0])[0] == 15
      and almost_brute_force("AMANAPLANACATACANALPANAMA", "SPAM")[0] is None)
PI = "31415926535897932384626433832795028841971"
check("pi digits: t_17 = 2384 for m = 4", int(PI[16:20]) == 2384)
for n, m in ((20, 4), (30, 5), (12, 6)):
    r, c = almost_brute_force("A" * n, "A" * (m - 1) + "B")
    check(f"worst case A^{m-1}B in A^{n}: exactly (n-m+1)m = {(n - m + 1) * m} comparisons", r is None and c == (n - m + 1) * m)
# expected comparisons per shift for random window and pattern over sigma letters: sum_{i<m} sigma^-i < sigma/(sigma-1)
from fractions import Fraction as Fr  # noqa: E402

for sig, m in ((2, 4), (3, 3), (4, 3)):
    tot = Fr(0)
    al = "ABCD"[:sig]
    for P in all_texts(al, m, m):
        for W in all_texts(al, m, m):
            c = 0
            for x, y in zip(W, P):
                c += 1
                if x != y:
                    break
            tot += c
    E = tot / sig ** (2 * m)
    check(f"random window and pattern, sigma = {sig}, m = {m}: E[comparisons at one shift] = {E} < {Fr(sig, sig - 1)}",
          E == sum(Fr(1, sig ** i) for i in range(m)) and E < Fr(sig, sig - 1))

HOC = "HOCUSPOCUSABRABRACADABRA"
AB = "ABRACADABRA"
check("HOCUSPOCUS text: at s = 11 the comparison fails at the 5th position (T[15] = B, not C)",
      HOC[10:14] == "ABRA" and HOC[14] == "B" and AB[4] == "C")
check("s = 12 and s = 13 fail at the first character; s = 14 is a full match (the note says s = 13, 14 fail, s = 15)",
      HOC[11] != "A" and HOC[12] != "A" and HOC[13:24] == AB and first_match(HOC, AB) == 14)
check("T[14] = P[4] = A (the note writes T[15] = P[4]; T[15] = B)", HOC[13] == "A" == AB[3] and HOC[14] == "B")
# KMP on it: after the mismatch at i = 15, j = 5, it continues with j = fail[5] = 2, i.e. shift 15 - 2 + 1 = 14
fAB, _ = compute_failure(AB)
check("KMP on HOCUSPOCUS...: mismatch T[15] vs P[5], fail[5] = 2, i.e. next shift 15 - 2 + 1 = 14; finds 14",
      fAB[5] == 2 and kmp(HOC, AB, fAB)[0] == 14)
check("next reasonable shift rule: smallest s with T[s .. 14] a proper prefix of P is 14",
      min(s for s in range(12, 16) if AB.startswith(HOC[s - 1:14])) == 14)

# failure-function tables (p. 8 and p. 11)
TABLES = {
    "ABRACADABRA": ([0, 1, 1, 1, 2, 1, 2, 1, 2, 3, 4], [0, 1, 1, 0, 2, 0, 2, 0, 1, 1, 1]),
    "ANANABANANANA": ([0, 1, 1, 2, 3, 4, 1, 2, 3, 4, 5, 6, 5], [0, 1, 0, 1, 0, 4, 0, 1, 0, 1, 0, 6, 0]),
    "ABABCABABCABC": ([0, 1, 1, 2, 3, 1, 2, 3, 4, 5, 6, 7, 8], [0, 1, 0, 1, 3, 0, 1, 0, 1, 3, 0, 1, 8]),
    "ABBABBABABBAB": ([0, 1, 1, 1, 2, 3, 4, 5, 6, 2, 3, 4, 5], [0, 1, 1, 0, 1, 1, 0, 1, 6, 1, 1, 0, 1]),
}
for P, (un, op) in TABLES.items():
    f = compute_failure(P)[0][1:]
    o = compute_opt_failure(P)[1:]
    check(f"{P}: unoptimized fail as printed", f == un, str(f))
    if P == "ABRACADABRA":
        diff = [i + 1 for i in range(len(o)) if o[i] != op[i]]
        check("ABRACADABRA optimized: printed table differs only at i = 11 (printed 1, correct 0)",
              diff == [11] and o[10] == 0 and op[10] == 1, str(o))
        check("ABRACADABRA optimized, i = 11: chain 11 -> 4 -> 1 -> 0 has P[4] = P[1] = A = P[11]",
              fAB[11] == 4 and fAB[4] == 1 and fAB[1] == 0 and AB[10] == AB[3] == AB[0] == "A")
    else:
        check(f"{P}: optimized fail as printed", o == op, str(o))
check("p. 11 says 'four more example strings' but prints three tables", len(TABLES) - 1 == 3)

# ComputeFailure trace of p. 9, run on ABRACADABRX (the X shows the final while loop)
tr = []
compute_failure("ABRACADABRX", tr)
printed = [("init", 0, 1), ("fail", 1, 0), ("adv", 1, 2), ("fail", 2, 1), ("back", 0, 2), ("adv", 1, 3),
           ("fail", 3, 1), ("back", 0, 3), ("adv", 1, 4), ("fail", 4, 1), ("adv", 2, 5), ("fail", 5, 2),
           ("back", 1, 5), ("back", 0, 5), ("adv", 1, 6), ("fail", 6, 1), ("adv", 2, 7), ("fail", 7, 2),
           ("back", 1, 7), ("back", 0, 7), ("adv", 1, 8), ("fail", 8, 1), ("adv", 2, 9), ("fail", 9, 2),
           ("adv", 3, 10), ("fail", 10, 3), ("adv", 4, 11), ("fail", 11, 4), ("back", 1, 11), ("back", 0, 11)]
check("ComputeFailure trace of p. 9 (30 lines) replayed step by step", tr == printed, str(tr[:6]))

# the compact table on the page: for each i, the j values compared with P[i] and the new j
def compact(P):
    m = len(P)
    P1 = " " + P
    fail = [None] * (m + 1)
    j = 0
    rows = []
    for i in range(1, m + 1):
        fail[i] = j
        tried = []
        while j > 0:
            tried.append(j)
            if P1[i] != P1[j]:
                j = fail[j]
            else:
                break
        j += 1
        rows.append((i, P1[i], fail[i], tried, j))
    return rows


CROWS = compact("ABRACADABRA")
for r in CROWS:
    print("   compact", r)

# iterated failure functions: P[1 .. fail^c[i]-1], c >= 1, are exactly the proper borders of P[1 .. i-1]
it_ok = True
for P in all_texts("AB", 8, 1):
    f = fail_def(P)
    for i in range(1, len(P) + 1):
        ch, c = set(), 1
        while True:
            k = fail_iter(f, i, c)
            if k is None or k == 0:
                break
            ch.add(k - 1)
            c += 1
        if i >= 2 and ch != set(borders_len(P[:i - 1])):
            it_ok = False
check("P[1 .. fail^c[i] - 1] (c >= 1) are exactly the proper borders of P[1 .. i-1] (all patterns over AB, m <= 8)",
      it_ok)
check("the note's base case 'fail[i] = 0 if i = 0' must read i = 1: fail[1] = 0 and fail[0] is never used",
      fail_recursive("ABRACADABRA")[1:] == [0, 1, 1, 1, 2, 1, 2, 1, 2, 3, 4])

# =====================================================================================================
print("== the KMP automaton as a DFA ==")
dfa_ok = lang_ok = min_ok = fool_ok = subset_ok = True
for alpha, mmax, L in (("AB", 5, 10), ("ABC", 3, 6)):
    for P in all_texts(alpha, mmax, 1):
        f = fail_def(P)
        d = kmp_dfa_delta(P, f, alpha)
        if d != dfa_def_delta(P, alpha):
            dfa_ok = False
        M = DFA(alpha, range(len(P) + 1), 0, [len(P)], d)
        for w in strings(alpha, L):
            if M.accepts(w) != (P in w):
                lang_ok = False
                break
        if M.minimize().num_states() != len(P) + 1:
            min_ok = False
        m = len(P)
        for i in range(m + 1):
            for j in range(i + 1, m + 1):
                z = P[j:]
                if not ((P[:j] + z == P) and P not in P[:i] + z):
                    fool_ok = False
        # NFA for Sigma* P (strings ending in P): subset construction has exactly m + 1 states
        dl = {(0, a): {0} for a in alpha}
        for k in range(m):
            dl.setdefault((k, P[k]), set()).add(k + 1)
        N = NFA(alpha, range(m + 1), 0, [m], dl)
        S, _ = N.subset_construction()
        if S.num_states() != m + 1:
            subset_ok = False
check("DFA built from the failure function = definition delta(k, a) = longest prefix of P that is a suffix of P[1..k]a",
      dfa_ok)
check("that DFA (state m absorbing) accepts exactly the strings containing P (all P, all w up to length 10 / 6)", lang_ok)
check("it is minimal: m + 1 states after Moore minimization, for every P", min_ok)
check("fooling set: the m + 1 prefixes of P; P[j+1..m] distinguishes P[1..i] and P[1..j] for i < j", fool_ok)
check("subset construction of the NFA for Sigma* P (strings ending in P) has exactly m + 1 reachable states", subset_ok)
# the figure's DFA for ABAB
dABAB = kmp_dfa_delta("ABAB", fail_def("ABAB"), "AB")
check("ABAB: fail = 0 1 1 2; DFA rows 0:(1,0) 1:(1,2) 2:(3,0) 3:(1,4) 4:(4,4)",
      fail_def("ABAB")[1:] == [0, 1, 1, 2]
      and [(dABAB[(k, "A")], dABAB[(k, "B")]) for k in range(5)] == [(1, 0), (1, 2), (3, 0), (1, 4), (4, 4)])
# contains-11 DFA of Part 1 §3.5 is the KMP DFA for P = 11
d11 = kmp_dfa_delta("11", fail_def("11"), "01")
check("KMP DFA for P = 11 over {0,1}: 0 -0-> 0, 0 -1-> 1, 1 -0-> 0, 1 -1-> 2, 2 absorbing (3 states, minimal)",
      d11 == {(0, "0"): 0, (0, "1"): 1, (1, "0"): 0, (1, "1"): 2, (2, "0"): 2, (2, "1"): 2})

# =====================================================================================================
print("== concept page example ==")
Pc, Tc = "AABA", "AAABAABA"
fc = compute_failure(Pc)[0]
oc = compute_opt_failure(Pc)
print("   concept: fail", fc[1:], "opt", oc[1:], "kmp", kmp(Tc, Pc, fc), "kmp opt", kmp(Tc, Pc, oc),
      "first match", first_match(Tc, Pc))


def kmp_trace(T, P, fail):
    T1, P1 = " " + T, " " + P
    j, out = 1, []
    for i in range(1, len(T) + 1):
        cmp = []
        while j > 0:
            cmp.append(j)
            if T1[i] != P1[j]:
                j = fail[j]
            else:
                break
        out.append((i, T1[i], cmp))
        if j == len(P):
            return out, i - len(P) + 1
        j += 1
    return out, None


print("   trace", kmp_trace(Tc, Pc, fc))
print("   trace opt", kmp_trace(Tc, Pc, oc))

# =====================================================================================================
print("== page text ==")
page = read(PAGE)
concept = read(CONCEPT)
check("page and concept page exist", bool(page) and bool(concept))


def table_rows(text, first_cell):
    """Rows of markdown tables (inside callouts) whose first cell is first_cell; returns lists of cell strings."""
    out = []
    for ln in text.split("\n"):
        ln = ln.lstrip("> ").strip()
        if ln.startswith("|"):
            cells = [c.strip() for c in ln.strip("|").split("|")]
            if cells[0] == first_cell:
                out.append([c for c in cells[1:] if c])
    return out


def ints(cells):
    return [int(c.replace("*", "")) for c in cells]


pats = ["".join(c.strip("`") for c in r) for r in table_rows(page, "$P$")]
fails = [ints(r) for r in table_rows(page, r"$\mathit{fail}$")]
opts = [ints(r) for r in table_rows(page, "optimized")]
check("page §7.7 table: the four patterns, their failure functions and optimized versions are the computed ones",
      pats == list(TABLES) and fails == [compute_failure(P)[0][1:] for P in TABLES]
      and opts == [compute_opt_failure(P)[1:] for P in TABLES], f"{pats}")
d1 = table_rows(page, r"$\mathit{fail}[j]$")
check("page §7.6 definition table: fail of ABRACADABRA", len(d1) == 1 and ints(d1[0]) == fAB[1:])
ct = table_rows(page, r"$\mathit{fail}[i]$ set to")
cj = table_rows(page, "$P[i]$ compared with $P[j]$ for $j =$")
ca = table_rows(page, "$j$ afterwards")
check("page §7.6 ComputeFailure table matches the replay (fail[i], the j's compared, j afterwards)",
      ct and ints(ct[0]) == [r[2] for r in CROWS]
      and cj and [[int(x) for x in c.split(",")] if c != "—" else [] for c in cj[0]] == [r[3] for r in CROWS]
      and ca and ints(ca[0]) == [r[4] for r in CROWS])
for frag in ("$t_{17} = 2384$", "shift 15", "at most $2n - 1$ comparisons", "$O(m\\log^{3.5} m)$",
             "$\\mathtt{00}$ and $\\mathtt{55}$", "194,586"):
    check(f"page states {frag}", frag in page)
check("page: 194,586 = number of (text, pattern) pairs tested", count == 194586)
check("page: numerically the ratio stays near 5 for m from 10 to 900", all(4.5 < r < 5.5 for r in ratios.values()))
# concept page example: P = AABA on AABBAABA
fc, oc = compute_failure("AABA")[0], compute_opt_failure("AABA")
r1, r2 = kmp("AABBAABA", "AABA", fc), kmp("AABBAABA", "AABA", oc)
check("concept example: fail(AABA) = 0 1 2 1, optimized 0 0 2 0", fc[1:] == [0, 1, 2, 1] and oc[1:] == [0, 0, 2, 0])
check("concept example: on AABBAABA a match at shift 5, 9 comparisons (8 with the optimized table)",
      r1[0] == r2[0] == 5 and r1[1] + r1[2] == 9 and r2[1] + r2[2] == 8 and kmp_trace("AABBAABA", "AABA", fc)[0][3][2] == [4, 1])
check("concept trap: prefix function pi[j] = border length of P[1..j] = fail[j+1] - 1",
      all(max(borders_len(P[:j])) == fail_def(P)[j + 1] - 1 for P in all_texts("AB", 7, 2) for j in range(1, len(P))))
fig = read(os.path.join(FIGS, "n07-kmp-machine.html"))
check("figure n07-kmp-machine: caption lists both failure functions",
      "0 1 1 1 2 1 2 1 2 3 4" in fig and "0 1 1 0 2 0 2 0 1 1 0" in fig)
fig3 = read(os.path.join(FIGS, "n07-kmp-dfa.html"))
check("figure n07-kmp-dfa: fail = 0 1 1 2 for ABAB, 5 states", "0 1 1 2" in fig3 and fail_def("ABAB")[1:] == [0, 1, 1, 2])

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: {FAIL}")
