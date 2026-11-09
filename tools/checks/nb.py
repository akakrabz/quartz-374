#!/usr/bin/env python3
"""Checks for content/4-lecture-notes/b-fast-exponential-algorithms.md (Erickson, Extended Dance Remix B, Faster
Exponential Algorithms; status: unfinished) and the B line added to content/concepts/np-hardness.md.

Every algorithm is implemented as the page states it — 3Sat (three branches), Faster3Sat (pure literals, four
branches), Local3Sat (copy semantics, and the figure's shared-array version), the deterministic and randomized
local-search wrappers, the naive and the improved MaximumIndSetSize (all four stages of the case analysis), the
subset dynamic program for 3-coloring, Lawler's maximal-independent-set versions for 3-coloring and chromatic number,
and the whatever-first backtracking for 3-coloring — and compared with brute force on many random small instances
(all graphs with at most 6 vertices for the graph algorithms). Recursive-call counts are compared with the
running-time recurrences; every recurrence is solved numerically (dominant root of its characteristic polynomial,
and the growth ratio of the recurrence itself) and compared with the bases stated in the note."""
import itertools
import math
import random
import sys
from functools import lru_cache

import numpy as np

sys.setrecursionlimit(100000)
FAIL = []


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAIL.append(name)


rng = random.Random(374)


# ====================================================================================== recurrences and roots
def char_poly(terms):
    """terms: list of (coefficient c_i, shift a_i) for T(n) = sum c_i T(n - a_i). Returns numpy coefficients of
    r^A - sum c_i r^(A - a_i), A = max a_i (highest power first)."""
    A = max(a for _, a in terms)
    coef = [0.0] * (A + 1)
    coef[0] = 1.0
    for c, a in terms:
        coef[a] -= c
    return coef


def dominant_root(terms):
    """The positive real root of the characteristic polynomial (there is exactly one, by Descartes' rule of signs);
    returned together with all roots so that callers can check it has the largest modulus."""
    roots = np.roots(char_poly(terms))
    pos = [r for r in roots if abs(r.imag) < 1e-9 and r.real > 0]
    assert len(pos) == 1
    return complex(pos[0].real, 0), roots


K = 60  # (T(N)/T(N-K))^(1/K): immune to the period-2 and period-3 oscillation of r^10 - r^8 - ... and r^3 - 3


def growth(terms, N=900, poly=lambda n: 1):
    """Numerically iterate T(n) = poly(n) + sum c T(n - a) (T(m) = 1 for m <= 0); return (T(N)/T(N-K))^(1/K)."""
    T = {}
    for n in range(-max(a for _, a in terms), N + 1):
        T[n] = 1.0 if n <= 0 else poly(n) + sum(c * T[n - a] for c, a in terms)
    return (T[N] / T[N - K]) ** (1 / K)


def growth_max(cases, N=1200):
    """T(n) = 1 + max over cases of sum c T(n - a): the 'solve each case and take the larger' rule."""
    A = max(a for case in cases for _, a in case)
    T = {}
    for n in range(-A, N + 1):
        T[n] = 1.0 if n <= 0 else 1 + max(sum(c * T[n - a] for c, a in case) for case in cases)
    return (T[N] / T[N - K]) ** (1 / K)


check("intro: for n = 100, 2^n = 1.3e30, 1.5^n = 4.1e17, 1.25^n = 4.9e9",
      f"{2 ** 100:.1e}" == "1.3e+30" and f"{1.5 ** 100:.1e}" == "4.1e+17" and f"{1.25 ** 100:.1e}" == "4.9e+09")
lam3, roots3 = dominant_root([(1, 1), (1, 2), (1, 3)])
cplx = sorted([r for r in roots3 if abs(r.imag) > 1e-9], key=lambda z: z.imag)
check("B.1 r^3 - r^2 - r - 1 has roots 1.83928676 and -0.41964338 ± 0.60629073i (sum of the roots = 1)",
      abs(lam3 - 1.83928676) < 1e-8 and abs(cplx[1] - complex(-0.41964338, 0.60629073)) < 1e-8
      and abs(cplx[0] - complex(-0.41964338, -0.60629073)) < 1e-8 and abs(sum(roots3) - 1) < 1e-12,
      f"{lam3.real:.10f}, {cplx[1]:.10f}")
check("B.1 ERROR p. 4 (last digits): the real part of the complex roots is -0.4196433776 = (1 - 1.8392867552)/2, "
      "not -0.419643337 as printed", abs(cplx[1].real - (1 - lam3.real) / 2) < 1e-12 and abs(cplx[1].real + 0.419643337) > 3e-8)
check("B.1 the real root has the largest modulus (|complex roots| = 0.7374)", abs(cplx[1]) < lam3.real and abs(abs(cplx[1]) - 0.7374) < 1e-4)
check("B.1 T(n) = T(n-1)+T(n-2)+T(n-3)+1: T(n)/T(n-1) -> 1.839287", abs(growth([(1, 1), (1, 2), (1, 3)]) - lam3.real) < 1e-9)
check("B.1 T(n) = T(n-1)+T(n-2)+T(n-3)+n^3: same ratio (polynomial noise does not change the base)",
      abs(growth([(1, 1), (1, 2), (1, 3)], poly=lambda n: n ** 3) - lam3.real) < 1e-6)
check("B.1 O(lambda^n poly(n)) = O(1.83929^n) since 1.83928676 < 1.83929", lam3.real < 1.83929)
check("B.1 T(n) <= 3T(n-1) + poly(n) gives 3^n", abs(dominant_root([(3, 1)])[0] - 3) < 1e-12)

lamF, _ = dominant_root([(2, 2), (2, 3)])
check("B.1 r^3 - 2r - 2: largest root 1.76929235 < 1.76930", abs(lamF - 1.76929235) < 1e-8 and lamF.real < 1.76930, f"{lamF.real:.10f}")
check("B.1 T(n) = 1 + max{T(n-1), 2T(n-2) + 2T(n-3)}: growth 1.769292 (the T(n-1) case is polynomial)",
      abs(growth_max([[(1, 1)], [(2, 2), (2, 3)]]) - lamF.real) < 1e-6)

# the general statement on p. 4: degree of the characteristic polynomial is a_k, not k
_, r4 = dominant_root([(1, 1), (1, 4)])
check("B.1 ERROR p. 4: r^(a_k) - sum r^(a_k - a_i) has a_k roots, not k: T(n) = T(n-1) + T(n-4) has k = 2 terms "
      "but r^4 - r^3 - 1 has 4 roots", len(r4) == 4)
ok = True
all_terms = [[(1, 1), (1, 2), (1, 3)], [(2, 2), (2, 3)], [(1, 1), (1, 2)], [(1, 1), (1, 3)], [(3, 3)], [(1, 1), (1, 4)],
             [(1, 4), (1, 5)], [(1, 3), (1, 5)], [(1, 2), (1, 8), (2, 10)]]
for t in all_terms:
    lam, roots = dominant_root(t)
    ok &= lam.real > 1 and max(abs(r) for r in roots) <= lam.real + 1e-9
    ok &= abs(growth(t) - lam.real) < 1e-6
check("B.1 for every recurrence on the page the unique positive root lambda > 1 has the largest modulus (ties: "
      "-lambda for r^10 - r^8 - r^2 - 2, two complex roots for r^3 - 3), and T(n) grows like lambda^n", ok)

# ====================================================================================== 3SAT machinery


def variables(F):
    return {abs(l) for C in F for l in C}


def restrict(F, lits):
    """F|l1 l2 ...: set every literal in lits True and simplify (drop satisfied clauses, delete false literals)."""
    S = set(lits)
    neg = {-l for l in S}
    out = []
    for C in F:
        if C & S:
            continue
        out.append(frozenset(C - neg))
    return out


def satisfies(F, A):
    """A: dict var -> bool."""
    return all(any((l > 0) == A[abs(l)] for l in C) for C in F)


def brute_sat(F, n):
    return any(satisfies(F, dict(zip(range(1, n + 1), bits))) for bits in itertools.product([False, True], repeat=n))


def random_formula(n, m, maxw=3):
    F = []
    for _ in range(m):
        w = rng.randint(1, min(maxw, n)) if rng.random() < 0.15 else min(3, n)
        vs = rng.sample(range(1, n + 1), w)
        F.append(frozenset(v if rng.random() < 0.5 else -v for v in vs))
    return F


CALLS = [0]


def ThreeSat(F):
    """The note's 3Sat plus the missing failure case (an empty clause)."""
    CALLS[0] += 1
    if not F:
        return True
    if any(len(C) == 0 for C in F):
        return False
    x = sorted(F[0], key=abs)  # (x or y or z), Phi' = the rest
    neg = []
    for l in x:  # Phi|x, Phi|~x y, Phi|~x ~y z
        if ThreeSat(restrict(F, neg + [l])):
            return True
        neg.append(-l)
    return False


def pure_literal(F):
    lits = {l for C in F for l in C}
    for l in sorted(lits, key=lambda l: (abs(l), l)):
        if -l not in lits:
            return l
    return None


def Faster3Sat(F):
    CALLS[0] += 1
    if not F:
        return True
    if any(len(C) == 0 for C in F):
        return False
    p = pure_literal(F)
    if p is not None:
        return Faster3Sat(restrict(F, [p]))
    C = sorted(F[0], key=abs)
    x = C[0]
    D = next(D for D in F if -x in D)  # exists: x is not pure
    uv = sorted(D - {-x}, key=abs)
    neg = []
    for l in uv:  # Phi|x u, Phi|x ~u v
        if Faster3Sat(restrict(F, [x] + neg + [l])):
            return True
        neg.append(-l)
    neg = []
    for l in C[1:]:  # Phi|~x y, Phi|~x ~y z
        if Faster3Sat(restrict(F, [-x] + neg + [l])):
            return True
        neg.append(-l)
    return False


def bound_3sat(n, memo={}):
    if n < 0:
        return 0
    if n == 0:
        return 1
    if n not in memo:
        memo[n] = 1 + bound_3sat(n - 1) + bound_3sat(n - 2) + bound_3sat(n - 3)
    return memo[n]


def bound_faster(n, memo={}):
    if n < 0:
        return 0
    if n == 0:
        return 1
    if n not in memo:
        memo[n] = 1 + max(bound_faster(n - 1), 2 * bound_faster(n - 2) + 2 * bound_faster(n - 3))
    return memo[n]


formulas = []
for trial in range(2500):
    n = rng.randint(1, 9)
    m = rng.randint(0, 6 * n)
    formulas.append((random_formula(n, m), n))
nsat = sum(brute_sat(F, n) for F, n in formulas)
check("B.1 test set: 2500 random formulas, 1-9 variables, clauses of at most 3 literals on distinct variables, both kinds",
      200 < nsat < 2300, f"{nsat} satisfiable")

ok = okc = okc_unsat = True
reach_empty = True
for F, n in formulas:
    truth = brute_sat(F, n)
    CALLS[0] = 0
    res = ThreeSat(F)
    ok &= res == truth
    okc &= CALLS[0] <= bound_3sat(len(variables(F)))
check("B.1 3Sat (with the empty-clause base case) = brute force on all 2500 formulas", ok)
check("B.1 3Sat makes at most B(n) calls, B(n) = 1 + B(n-1) + B(n-2) + B(n-3)", okc)


def reaches_empty_clause(F):
    if not F:
        return False
    if any(len(C) == 0 for C in F):
        return True
    x = sorted(F[0], key=abs)
    neg = []
    hit = False
    for l in x:
        hit |= reaches_empty_clause(restrict(F, neg + [l]))
        neg.append(-l)
    return hit


check("B.1 ERROR p. 3: the printed 3Sat never returns False; on every unsatisfiable test formula the recursion reaches "
      "a formula with an empty clause, where it needs 'return False'",
      all(reaches_empty_clause(F) for F, n in formulas if not brute_sat(F, n)))

ok = okc = True
for F, n in formulas:
    CALLS[0] = 0
    ok &= Faster3Sat(F) == brute_sat(F, n)
    okc &= CALLS[0] <= bound_faster(len(variables(F)))
check("B.1 Faster3Sat (pure literals; branches x u, x ~u v, ~x y, ~x ~y z) = brute force on all 2500 formulas", ok)
check("B.1 Faster3Sat makes at most B'(n) calls, B'(n) = 1 + max{B'(n-1), 2B'(n-2) + 2B'(n-3)}", okc)
check("B.1 bound ratios: B(60)/B(59) -> 1.8393, B'(60)/B'(59) -> 1.7693",
      abs(bound_3sat(200) / bound_3sat(199) - lam3.real) < 1e-9 and abs(bound_faster(200) / bound_faster(199) - lamF.real) < 1e-6)

# x AND Psi = x AND (Psi|x); pure literals
ok = True
for F, n in formulas[:600]:
    for l in list({l for C in F for l in C})[:3]:
        for bits in itertools.product([False, True], repeat=n):
            A = dict(zip(range(1, n + 1), bits))
            xval = (l > 0) == A[abs(l)]
            ok &= (xval and satisfies(F, A)) == (xval and satisfies(restrict(F, [l]), A))
check("B.1 x AND Psi = x AND (Psi|x) (truth tables, 600 formulas)", ok)
ok = True
for F, n in formulas:
    lits = {l for C in F for l in C}
    if brute_sat(F, n):
        for l in lits:
            if -l not in lits:
                ok &= brute_sat(restrict(F, [l]), n)
check("B.1 a satisfiable formula stays satisfiable after setting any pure literal True", ok)

# ---------------------------------------------------------------------------------- local search


def unsat_clause(F, A):
    return next((C for C in F if not any((l > 0) == A[abs(l)] for l in C)), None)


LCALLS = [0]


def Local3Sat(F, A, r):
    """Copy semantics: each recursive call gets its own assignment (A_x, A_y, A_z = A with one variable flipped)."""
    LCALLS[0] += 1
    C = unsat_clause(F, A)
    if C is None:
        return True
    if r == 0:
        return False
    for v in sorted({abs(l) for l in C}):
        B = dict(A)
        B[v] = not B[v]
        if Local3Sat(F, B, r - 1):
            return True
    return False


def Local3SatShared(F, A, r):
    """Figure B.2 read literally with ONE shared array: the last branch flips A[z] and returns without undoing it."""
    C = unsat_clause(F, A)
    if C is None:
        return True
    if r == 0:
        return False
    vs = sorted({abs(l) for l in C})
    for i, v in enumerate(vs):
        A[v] = not A[v]
        if i == len(vs) - 1:
            return Local3SatShared(F, A, r - 1)
        if Local3SatShared(F, A, r - 1):
            return True
        A[v] = not A[v]
    return False


def ham(A, B):
    return sum(A[v] != B[v] for v in A)


ok = okc = True
shared_fn = 0
shared_bad = None
shared_tests = shared_wrong = 0
for F, n in formulas[:700]:
    if n > 6:
        continue
    sats = [dict(zip(range(1, n + 1), bits)) for bits in itertools.product([False, True], repeat=n)
            if satisfies(F, dict(zip(range(1, n + 1), bits)))]
    for bits in itertools.product([False, True], repeat=n):
        A = dict(zip(range(1, n + 1), bits))
        dmin = min((ham(A, S) for S in sats), default=None)
        for r in range(0, n + 1):
            LCALLS[0] = 0
            res = Local3Sat(F, A, r)
            ok &= res == (dmin is not None and dmin <= r)
            okc &= LCALLS[0] <= (3 ** (r + 1) - 1) // 2
            sres = Local3SatShared(F, dict(A), r)
            shared_tests += 1
            if res and not sres:
                shared_fn += 1
            if sres != res:
                shared_wrong += 1
                if shared_bad is None or len(F) < len(shared_bad[0]):
                    shared_bad = (F, n, dict(A), r, res, sres)
check("B.1 Local3Sat(Phi, A, r) = True exactly when some satisfying assignment is within Hamming distance r of A "
      "(every start A, every r, formulas with <= 6 variables)", ok)
check("B.1 Local3Sat makes at most 1 + 3 + ... + 3^r = (3^(r+1) - 1)/2 calls: O(3^r poly(n))", okc)
check("B.1 NOTE p. 6 (Figure B.2): read with one shared array A, the last branch leaves A[z] flipped; this changes "
      f"answers ({shared_wrong} of {shared_tests} runs), so A must be passed by value (or the flip undone)",
      shared_wrong > 0, f"smallest bad case: {len(shared_bad[0])} clauses, n = {shared_bad[1]}, r = {shared_bad[3]}, "
      f"correct {shared_bad[4]}, shared {shared_bad[5]}" if shared_bad else "")

ok = True
for F, n in formulas:
    allT = {v: True for v in range(1, n + 1)}
    allF = {v: False for v in range(1, n + 1)}
    ok &= (Local3Sat(F, allT, n // 2) or Local3Sat(F, allF, n // 2)) == brute_sat(F, n)
check("B.1 deterministic local search: radius floor(n/2) from all-True and from all-False decides every test formula", ok)
dec_wrong = sum((Local3SatShared(F, {v: True for v in range(1, n + 1)}, n // 2)
                 or Local3SatShared(F, {v: False for v in range(1, n + 1)}, n // 2)) != brute_sat(F, n) for F, n in formulas)
check("B.1 NOTE p. 6: with the shared array the search also misses satisfying assignments within distance r "
      f"({shared_fn} runs), and the deterministic algorithm built on it answers wrongly on {dec_wrong} of 2500 formulas",
      shared_fn > 0 and dec_wrong > 0)
check("B.1 3^(n/2) = (sqrt 3)^n and sqrt 3 = 1.7320508 < 1.73206", math.sqrt(3) < 1.73206 and abs(math.sqrt(3) - 1.7320508) < 1e-7)

# random starting assignments


def V(n, r):
    return sum(math.comb(n, i) for i in range(0, r + 1))


ok = True
for F, n in formulas[:700]:
    if n > 7 or not brute_sat(F, n):
        continue
    starts = [dict(zip(range(1, n + 1), bits)) for bits in itertools.product([False, True], repeat=n)]
    for r in range(0, n + 1):
        succ = sum(Local3Sat(F, A, r) for A in starts)
        ok &= succ * 1 >= V(n, r)  # P(r) = succ / 2^n >= V(r) / 2^n
check("B.1 P(r) >= V(r)/2^n: from a uniformly random start, local search with radius r succeeds with probability at "
      "least V(r)/2^n (exact enumeration over all starts)", ok)
ok = all((1 - x) ** (n / x) <= math.exp(-n) + 1e-15 for n in range(1, 40) for x in [k / 1000 for k in range(1, 1001)])
check("B.1 with N(r) = n 2^n / V(r) runs the failure probability (1 - P)^N <= (1 - V/2^n)^(n 2^n/V) <= e^-n", ok)


def H(a):
    return (1 / a) ** a * (1 / (1 - a)) ** (1 - a)


check("B.1 H(alpha) = (1/alpha)^alpha (1/(1-alpha))^(1-alpha) is 2^(binary entropy): H(1/4) = 1.7548, H(1/2) = 2",
      all(abs(H(a) - 2 ** (-a * math.log2(a) - (1 - a) * math.log2(1 - a))) < 1e-12 for a in [0.1, 0.25, 0.5, 0.8])
      and abs(H(0.25) - 1.7548) < 1e-4 and abs(H(0.5) - 2) < 1e-12)
ratios = [V(n, n // 4) * math.sqrt(n) / H(0.25) ** n for n in range(4, 801, 4)]
check("B.1 V(n/4) = Omega(H(1/4)^n / sqrt n): V(n/4) sqrt(n) / H(1/4)^n stays between 0.4 and 1.6 for n = 4..800",
      0.4 < min(ratios) and max(ratios) < 1.6, f"min {min(ratios):.3f}, max {max(ratios):.3f}")
check("B.1 3^alpha / H(alpha) = (3 alpha)^alpha (1-alpha)^(1-alpha)",
      all(abs(3 ** a / H(a) - (3 * a) ** a * (1 - a) ** (1 - a)) < 1e-12 for a in [0.05, 0.25, 0.4, 0.7]))
f = lambda a: 2 * (3 * a) ** a * (1 - a) ** (1 - a)
grid = [k / 100000 for k in range(1, 100000)]
amin = min(grid, key=f)
check("B.1 2 (3a)^a (1-a)^(1-a) is minimized at a = 1/4, where it equals 3/2 (derivative ln 3a - ln(1-a))",
      abs(amin - 0.25) < 1e-4 and abs(f(0.25) - 1.5) < 1e-12 and abs(math.log(3 * 0.25) - math.log(0.75)) < 1e-15)
ok = True
for n in range(8, 801, 8):
    cost = 2 ** n * 3 ** (n // 4) / V(n, n // 4)
    ok &= cost / 1.5 ** n <= 3 * math.sqrt(n)
check("B.1 total work 2^n 3^(n/4) / V(n/4) is at most 3 sqrt(n) (3/2)^n for n = 8..800", ok)

# ====================================================================================== B.2 independent sets


def all_graphs(n):
    E = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(E)):
        G = {v: set() for v in range(n)}
        for i, (u, v) in enumerate(E):
            if mask >> i & 1:
                G[u].add(v)
                G[v].add(u)
        yield G


def random_graph(n, p):
    G = {v: set() for v in range(n)}
    for u, v in itertools.combinations(range(n), 2):
        if rng.random() < p:
            G[u].add(v)
            G[v].add(u)
    return G


def remove(G, S):
    return {v: G[v] - S for v in G if v not in S}


def N(G, v):
    return {v} | G[v]


def independent(G, S):
    return all(not (G[u] & S) for u in S)


def brute_mis(G):
    vs = list(G)
    best = 0
    for k in range(len(vs), -1, -1):
        if any(independent(G, set(S)) for S in itertools.combinations(vs, k)):
            return k
    return best


MCALLS = [0]


def MISnaive(G):
    MCALLS[0] += 1
    if not G:
        return 0
    v = min(G)
    return max(1 + MISnaive(remove(G, N(G, v))), MISnaive(remove(G, {v})))


def MISdeg0(G):
    if not G:
        return 0
    v0 = next((v for v in sorted(G) if not G[v]), None)
    if v0 is not None:
        return 1 + MISdeg0(remove(G, {v0}))
    v = min(G)
    return max(1 + MISdeg0(remove(G, N(G, v))), MISdeg0(remove(G, {v})))


def MISdeg1(G):
    if not G:
        return 0
    v1 = next((v for v in sorted(G) if len(G[v]) <= 1), None)
    if v1 is not None:
        return 1 + MISdeg1(remove(G, N(G, v1)))
    v = min(G)
    return max(1 + MISdeg1(remove(G, N(G, v))), MISdeg1(remove(G, {v})))


def MISdeg3(G):
    """Stage 'degree >= 3': all-degree-2 graphs branch three ways on a path u v w."""
    if not G:
        return 0
    v1 = next((v for v in sorted(G) if len(G[v]) <= 1), None)
    if v1 is not None:
        return 1 + MISdeg3(remove(G, N(G, v1)))
    v3 = next((v for v in sorted(G) if len(G[v]) >= 3), None)
    if v3 is not None:
        return max(1 + MISdeg3(remove(G, N(G, v3))), MISdeg3(remove(G, {v3})))
    v = min(G)
    u, w = sorted(G[v])
    return max(1 + MISdeg3(remove(G, N(G, x))) for x in (u, v, w))


def components(G):
    seen, comps = set(), []
    for s in G:
        if s in seen:
            continue
        stack, comp = [s], set()
        seen.add(s)
        while stack:
            x = stack.pop()
            comp.add(x)
            for y in G[x]:
                if y not in seen:
                    seen.add(y)
                    stack.append(y)
        comps.append(comp)
    return comps


def MISfinal(G):
    """Figure B.3."""
    MCALLS[0] += 1
    if not G:
        return 0
    v1 = next((v for v in sorted(G) if len(G[v]) <= 1), None)
    if v1 is not None:
        return 1 + MISfinal(remove(G, N(G, v1)))
    v3 = next((v for v in sorted(G) if len(G[v]) > 2), None)
    if v3 is not None:
        withv = 1 + MISfinal(remove(G, N(G, v3)))
        withoutv = MISfinal(remove(G, {v3}))
        return max(withv, withoutv)
    return sum(len(c) // 2 for c in components(G))  # every node has degree 2: disjoint cycles


ok = {k: True for k in ("naive", "d0", "d1", "d3", "final")}
cnt = 0
for n in range(0, 7):
    for G in all_graphs(n):
        t = brute_mis(G)
        ok["naive"] &= MISnaive(G) == t
        ok["d0"] &= MISdeg0(G) == t
        ok["d1"] &= MISdeg1(G) == t
        ok["d3"] &= MISdeg3(G) == t
        ok["final"] &= MISfinal(G) == t
        cnt += 1
rand_graphs = [random_graph(n, rng.choice([0.15, 0.25, 0.4, 0.6])) for n in range(7, 15) for _ in range(40)]
for G in rand_graphs:
    t = brute_mis(G)
    ok["naive"] &= MISnaive(G) == t
    ok["d0"] &= MISdeg0(G) == t
    ok["d1"] &= MISdeg1(G) == t
    ok["d3"] &= MISdeg3(G) == t
    ok["final"] &= MISfinal(G) == t
check(f"B.2 naive MaximumIndSetSize = brute force ({cnt} labelled graphs with <= 6 vertices + 320 random with 7-14)", ok["naive"])
check("B.2 degree-0 rule (take an isolated vertex) = brute force", ok["d0"])
check("B.2 degree-1 rule (take a vertex of degree <= 1) = brute force", ok["d1"])
check("B.2 degree >= 3 stage (three-way branch on a path u v w when every degree is 2) = brute force", ok["d3"])
check("B.2 final algorithm (Figure B.3, cycles solved directly) = brute force", ok["final"])


def bound_final(n, memo={}):
    if n <= 0:
        return 1
    if n not in memo:
        memo[n] = 1 + max(bound_final(n - 1), bound_final(n - 1) + bound_final(n - 4))
    return memo[n]


okc = True
for G in rand_graphs + [random_graph(n, 0.3) for n in range(15, 31) for _ in range(5)]:
    MCALLS[0] = 0
    MISfinal(G)
    okc &= MCALLS[0] <= bound_final(len(G))
check("B.2 Figure B.3 makes at most B(n) calls, B(n) = 1 + B(n-1) + B(n-4) (graphs up to 30 vertices)", okc)

# the degree-1 lemma
ok = True
for n in range(1, 7):
    for G in all_graphs(n):
        t = brute_mis(G)
        for v in G:
            if len(G[v]) <= 1:
                ok &= 1 + brute_mis(remove(G, N(G, v))) == t
check("B.2 if deg(v) <= 1, some maximum independent set contains v (all graphs with <= 6 vertices)", ok)
check("B.2 cycle C_k has maximum independent set floor(k/2), k = 3..16",
      all(brute_mis({i: {(i - 1) % k, (i + 1) % k} for i in range(k)}) == k // 2 for k in range(3, 17)))


def maximal_independent_sets(G):
    vs = sorted(G)
    out = []
    for k in range(len(vs) + 1):
        for S in itertools.combinations(vs, k):
            S = set(S)
            if independent(G, S) and all(v in S or (G[v] & S) for v in vs):
                out.append(frozenset(S))
    return out


maxM = {}
iso_ok = True
for n in range(1, 7):
    best = 0
    for G in all_graphs(n):
        M = maximal_independent_sets(G)
        best = max(best, len(M))
        iso = [v for v in G if not G[v]]
        iso_ok &= all(all(v in S for S in M) for v in iso)
    maxM[n] = best
check("B.2 an isolated vertex is in every maximal independent set (all graphs <= 6 vertices)", iso_ok)
check("B.2 most maximal independent sets in an n-vertex graph, n = 1..6: 1, 2, 3, 4, 6, 9",
      [maxM[n] for n in range(1, 7)] == [1, 2, 3, 4, 6, 9], str(maxM))
check("B.2 M(n) <= 2M(n-1), M(1) = 1 gives M(n) <= 2^(n-1) (tighter than the note's 2^n - 1); true maximum <= 3^(n/3)",
      all(maxM[n] <= 2 ** (n - 1) <= 2 ** n - 1 and maxM[n] <= 3 ** (n / 3) + 1e-9 for n in range(1, 7)))
two_tri = {0: {1, 2}, 1: {0, 2}, 2: {0, 1}, 3: {4, 5}, 4: {3, 5}, 5: {3, 4}}
check("B.2 two disjoint triangles have 3^2 = 9 maximal independent sets", len(maximal_independent_sets(two_tri)) == 9)

# bases of the case analysis
phi = (1 + 5 ** 0.5) / 2
l1, _ = dominant_root([(1, 1), (1, 2)])
l2, _ = dominant_root([(1, 1), (1, 3)])
l3, _ = dominant_root([(3, 3)])
l4, _ = dominant_root([(1, 1), (1, 4)])
check("B.2 degree 0: T(n-1) + T(n-2) -> phi = 1.6180340 < 1.61804", abs(l1 - phi) < 1e-12 and phi < 1.61804)
check("B.2 degree 1: r^3 - r^2 - 1 -> 1.4655712 < 1.46558", abs(l2 - 1.4655712) < 1e-7 and l2.real < 1.46558, f"{l2.real:.8f}")
check("B.2 degree >= 3: 3T(n-3) -> r^3 - 3 -> 3^(1/3) = 1.4422496 < 1.44225", abs(l3 - 3 ** (1 / 3)) < 1e-12 and 3 ** (1 / 3) < 1.44225)
check("B.2 T(n-1) + T(n-4) -> r^4 - r^3 - 1 -> 1.3802776 < 1.38028", abs(l4 - 1.3802776) < 1e-7 and l4.real < 1.38028, f"{l4.real:.8f}")
check("B.2 multi-case recurrences: growth of 1 + max{...} equals the largest single-case root",
      abs(growth_max([[(1, 1)], [(1, 1), (1, 2)]]) - phi) < 1e-6
      and abs(growth_max([[(1, 1)], [(1, 2)], [(1, 1), (1, 3)]]) - l2.real) < 1e-6
      and abs(growth_max([[(1, 1)], [(1, 2)], [(1, 1), (1, 4)], [(3, 3)]]) - l3.real) < 1e-6
      and abs(growth_max([[(1, 1)], [(1, 2)], [(1, 1), (1, 4)]]) - l4.real) < 1e-6)
check("B.2 table of bases: 2, 1.6180340, 1.4655712, 1.4422496, 1.3802776 (7 decimals)",
      [f"{dominant_root(t)[0].real:.7f}" for t in ([(2, 1)], [(1, 1), (1, 2)], [(1, 1), (1, 3)], [(3, 3)], [(1, 1), (1, 4)])]
      == ["2.0000000", "1.6180340", "1.4655712", "1.4422496", "1.3802776"])
check("B.3 bases: 3^(1/3) = 1.44225 -> O(1.4423^n); 1 + 3^(1/3) = 2.44225 -> O(2.4423^n)",
      3 ** (1 / 3) < 1.4423 and 1 + 3 ** (1 / 3) < 2.4423 and abs(1 + 3 ** (1 / 3) - 2.44225) < 1e-5)
la, _ = dominant_root([(1, 4), (1, 5)])
lb, _ = dominant_root([(1, 3), (1, 5)])
check("B.2 T(n-4) + T(n-5) (1.1673) is dominated by T(n-3) + T(n-5) (1.1939)", la.real < lb.real and abs(la - 1.1673) < 1e-4
      and abs(lb - 1.1939) < 1e-4, f"{la.real:.5f} < {lb.real:.5f}")

TT = [[(1, 2), (1, 6)], [(1, 2), (2, 8)], [(1, 2), (1, 8), (2, 10)], [(1, 3), (1, 5)], [(1, 4), (1, 6), (1, 8)],
      [(1, 4), (2, 7)], [(1, 4), (1, 8), (3, 11)], [(1, 4), (2, 8), (1, 10)], [(1, 4), (1, 9), (2, 12)],
      [(1, 4), (4, 10)], [(1, 5), (4, 9)], [(1, 5), (6, 11), (4, 14), (1, 17)]]
roots_tt = [dominant_root(c)[0].real for c in TT]
check("B.2 Figure B.4: of the 12 cases the third, T(n-2) + T(n-8) + 2T(n-10), has the largest root",
      max(range(12), key=lambda i: roots_tt[i]) == 2, ", ".join(f"{r:.5f}" for r in roots_tt))
check("B.2 its characteristic polynomial is r^10 - r^8 - r^2 - 2 with root 1.25603 < 2^(1/3) = 1.25992",
      char_poly(TT[2]) == [1, 0, -1, 0, 0, 0, 0, 0, -1, 0, -2] and abs(roots_tt[2] - 1.25603) < 1e-5 and roots_tt[2] < 2 ** (1 / 3),
      f"{roots_tt[2]:.7f}")
check("B.2 printed to 6 decimals the Tarjan-Trojanowski base is 1.256020; 2^(1/3) = 1.259921",
      f"{roots_tt[2]:.6f}" == "1.256020" and f"{2 ** (1 / 3):.6f}" == "1.259921")
check("B.2 ERROR p. 11: Robson's O(1.1889^n) is not O(2^(n/4) poly(n)) the other way round: 2^(1/4) = 1.18921 > 1.1889",
      2 ** 0.25 > 1.1889 and abs(2 ** 0.25 - 1.18921) < 1e-5)

# ====================================================================================== B.3 dynamic programming (draft)


def brute_colorable(G, k):
    vs = sorted(G)
    for cols in itertools.product(range(k), repeat=len(vs)):
        c = dict(zip(vs, cols))
        if all(c[u] != c[v] for u in G for v in G[u]):
            return True
    return False


def bipartite(G):
    color = {}
    for s in G:
        if s in color:
            continue
        color[s] = 0
        stack = [s]
        while stack:
            x = stack.pop()
            for y in G[x]:
                if y not in color:
                    color[y] = 1 - color[x]
                    stack.append(y)
                elif color[y] == color[x]:
                    return False
    return True


def three_color_dp(G):
    V_ = frozenset(G)

    @lru_cache(maxsize=None)
    def OPT(X):
        if not independent(G, set(X)):
            return False
        if bipartite(remove(G, set(X))):
            return True
        return any(OPT(X | {v}) for v in V_ - X)

    return OPT(frozenset())


def three_color_lawler(G):
    return any(bipartite(remove(G, set(I))) for I in maximal_independent_sets(G))


def three_color_wfs(G):
    """Backtracking along a whatever-first (here breadth-first) order, per component: the root is red, the second
    vertex green, every later vertex gets one of the two colors that differ from its parent's.
    Returns (colorable?, number of candidate colorings examined for each component)."""
    counts = []
    for comp in components(G):
        order, parent = [], {}
        s = min(comp)
        parent[s] = None
        q = [s]
        while q:
            x = q.pop(0)
            order.append(x)
            for y in sorted(G[x]):
                if y not in parent:
                    parent[y] = x
                    q.append(y)
        cands = 0
        found = False
        choices = []
        for i, v in enumerate(order):
            if i == 0:
                choices.append([0])
            elif i == 1:
                choices.append([1])
            else:
                choices.append(None)

        def rec(i, col):
            nonlocal cands, found
            if i == len(order):
                cands += 1
                if all(col[u] != col[w] for u in comp for w in G[u]):
                    found = True
                return
            v = order[i]
            opts = [0] if i == 0 else [1] if i == 1 else [c for c in range(3) if c != col[parent[v]]]
            for c in opts:
                col[v] = c
                rec(i + 1, col)
            del col[v]

        rec(0, {})
        counts.append((len(comp), cands))
        if not found:
            return False, counts
    return True, counts


ok_dp = ok_law = ok_wfs = ok_cnt = True
tests = [G for n in range(0, 6) for G in all_graphs(n)] + [random_graph(n, rng.choice([0.3, 0.45, 0.6])) for n in range(6, 10) for _ in range(40)]
for G in tests:
    t = brute_colorable(G, 3)
    ok_dp &= three_color_dp(G) == t
    ok_law &= three_color_lawler(G) == t
    res, counts = three_color_wfs(G)
    ok_wfs &= res == t
    if res:
        ok_cnt &= all(c == (2 ** (k - 2) if k >= 2 else 1) for k, c in counts)
check(f"B.3 3-coloring DP over subsets X (X independent, G - X bipartite, else OR of OPT(X + v)) = brute force "
      f"({len(tests)} graphs)", ok_dp)
check("B.3 Lawler: G is 3-colorable iff G - I is bipartite for some maximal independent set I", ok_law)
check("B.3 whatever-first backtracking (first two vertices red, green; each later vertex 2 choices) = brute force", ok_wfs)
check("B.3 it examines exactly 2^(n-2) colorings of a connected component with n >= 2 vertices", ok_cnt)


def chromatic_lawler(G):
    @lru_cache(maxsize=None)
    def OPT(X):
        if not X:
            return 0
        H = {v: G[v] & X for v in X}
        return 1 + min(OPT(X - I) for I in maximal_independent_sets(H))

    return OPT(frozenset(G))


def brute_chromatic(G):
    k = 0
    while not brute_colorable(G, k):
        k += 1
    return k


ok = all(chromatic_lawler(G) == brute_chromatic(G) for G in [G for n in range(0, 6) for G in all_graphs(n)][::7]
         + [random_graph(n, rng.choice([0.3, 0.5, 0.7])) for n in range(6, 9) for _ in range(25)])
check("B.3 Lawler's chromatic-number recurrence (1 + min over maximal independent sets I of OPT(X - I)) = brute force", ok)
K = {v: set(range(10)) - {v} for v in range(10)}
check("B.3 ERROR p. 12: 'O(3^(k/3)) maximal independent sets of size k' is false (K_10 has 10 of size 1); the bound is "
      "3^(k/3) for a graph with k vertices", len(maximal_independent_sets(K)) == 10 and 10 > 3 ** (1 / 3) * 5)
check("B.3 sum_k C(n,k) 3^(k/3) = (1 + 3^(1/3))^n (binomial theorem), 1 + 3^(1/3) = 2.4422",
      all(abs(sum(math.comb(n, k) * 3 ** (k / 3) for k in range(n + 1)) - (1 + 3 ** (1 / 3)) ** n) < 1e-6 * (1 + 3 ** (1 / 3)) ** n
          for n in range(1, 60)) and abs(1 + 3 ** (1 / 3) - 2.4422) < 1e-4)

# exercise 5(a) as printed (p. 13): sum_{i <= alpha n} C(n, i) < H(alpha)^n "for all constant 0 < alpha < 1"
n = 40
check("Exercise 5(a) p. 13: the bound sum_{i<=an} C(n,i) < H(a)^n fails for a > 1/2 (a = 3/4, n = 40: 2^40 - 3.7e8 = 1.1e12 vs 5.9e9)",
      V(n, 30) > H(0.75) ** n and all(V(m, int(a * m)) <= H(a) ** m for m in range(2, 80) for a in [0.1, 0.25, 0.4, 0.5]),
      f"{V(n, 30):.3e} vs {H(0.75) ** n:.3e}")

print()
if FAIL:
    print(f"{len(FAIL)} FAILED")
    sys.exit(1)
print("ALL OK")
