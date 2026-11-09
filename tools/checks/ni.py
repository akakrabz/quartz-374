#!/usr/bin/env python3
"""Checks for content/4-lecture-notes/i-linear-programming-algorithms.md (Erickson, Extended Dance Remix I, Linear
Programming Algorithms) and the concept page content/concepts/simplex-algorithm.md.

The note describes the simplex algorithm geometrically, not as a tableau: a basis is a set of d of the n + d
constraints of a canonical LP, its location the point where they are tight, and a pivot swaps one constraint. This
script implements exactly that — PrimalSimplex, DualSimplex, DualPrimalSimplex (rotate the objective, Figure I.4) and
PrimalDualSimplex (translate the constraints, Figure I.5) — with several pivot rules, and compares every outcome
(optimal value / Infeasible / Unbounded) with scipy's linprog on thousands of random non-degenerate LPs. It also
checks the basis-level claims of I.1 by enumerating all bases, the network-simplex claims of I.4 on random
transshipment instances (enumerating all spanning trees), and SeidelLP of I.5 in dimensions 1, 2 and 3 (exact expected
numbers of calls by recursion over subsets, compared with the note's recurrence). There is no worked pivot sequence
in the note; the dictionary-form example and the Klee-Minty run on the pages are checked here as well."""
import itertools
import math
import os
import random
import re
import sys
from fractions import Fraction as Fr
from functools import lru_cache

import numpy as np
from scipy.optimize import linprog

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
PAGE = os.path.join(ROOT, "content", "4-lecture-notes", "i-linear-programming-algorithms.md")
CONCEPT = os.path.join(ROOT, "content", "concepts", "simplex-algorithm.md")
FIGS = os.path.join(HERE, "..", "figs")
FAIL = []
rng = random.Random(3740009)
np.random.seed(3740009)
TOL = 1e-9


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAIL.append(name)


def lp_status(c, A, b):
    """linprog on max c.x, Ax <= b, x >= 0 -> (status, value)."""
    d = len(c)
    res = linprog(-np.asarray(c), A_ub=A, b_ub=b, bounds=[(0, None)] * d, method="highs")
    if res.status == 0:
        return "optimal", -res.fun
    r0 = linprog(np.zeros(d), A_ub=A, b_ub=b, bounds=[(0, None)] * d, method="highs")
    if r0.status == 2:
        return "infeasible", None
    if res.status in (2, 3):
        return "unbounded", None
    # HiGHS sometimes answers 'unknown' on unbounded LPs: compare two boxes
    v = []
    for B in (1e4, 1e6):
        rb = linprog(-np.asarray(c), A_ub=A, b_ub=b, bounds=[(0, B)] * d, method="highs")
        v.append(-rb.fun)
    return ("unbounded", None) if v[1] > v[0] + 1e-6 * (1 + abs(v[0])) else ("optimal", v[0])


# ============================================================================== the geometric simplex (I.1-I.3)
class LP:
    """max c.x subject to the n + d halfspaces G[k].x <= h[k]: rows 0..n-1 are Ax <= b, rows n..n+d-1 are -x_j <= 0."""

    def __init__(self, A, b, c, G=None, h=None):
        self.A, self.b, self.c = np.asarray(A, float), np.asarray(b, float), np.asarray(c, float)
        self.n, self.d = self.A.shape
        self.G = np.vstack([self.A, -np.eye(self.d)]) if G is None else G
        self.h = np.concatenate([self.b, np.zeros(self.d)]) if h is None else h
        self.N = self.n + self.d

    def loc(self, B):
        return np.linalg.solve(self.G[list(B)], self.h[list(B)])

    def mult(self, B, c=None):
        """y_B with c = y_B G_B: the 'forces' of the d constraints of B."""
        return np.linalg.solve(self.G[list(B)].T, self.c if c is None else c)

    def feasible(self, B, h=None):
        x = self.loc(B) if h is None else np.linalg.solve(self.G[list(B)], h[list(B)])
        return bool(np.all(self.G @ x <= (self.h if h is None else h) + 1e-9))

    def locopt(self, B, c=None):
        return bool(np.all(self.mult(B, c) >= -1e-9))

    def value(self, B, c=None, h=None):
        x = self.loc(B) if h is None else np.linalg.solve(self.G[list(B)], h[list(B)])
        return float((self.c if c is None else c) @ x)

    def bases(self):
        return [frozenset(B) for B in itertools.combinations(range(self.N), self.d)]

    def neighbors(self, B):
        for i in sorted(B):
            for k in range(self.N):
                if k not in B:
                    yield (B - {i}) | {k}


def choose(cands, rule, key):
    if rule == "random":
        return rng.choice(cands)
    if rule == "best":
        return max(cands, key=key)
    if rule == "first":
        return cands[0]
    raise ValueError(rule)


def primal_phase(P, B, rule, c=None, h=None, trace=None):
    """Pivot down (larger c.x) through feasible bases until locally optimal; 'lower' = larger objective value."""
    cc = P.c if c is None else c
    steps = 0
    while not P.locopt(B, cc):
        v = P.value(B, cc, h)
        cands = [B2 for B2 in P.neighbors(B) if P.feasible(B2, h) and P.value(B2, cc, h) > v + 1e-12]
        if not cands:
            return "unbounded", B, steps
        B = choose(cands, rule, lambda X: P.value(X, cc, h))
        steps += 1
        if trace is not None:
            trace.append(B)
    return "optimal", B, steps


def dual_phase(P, B, rule, c=None, h=None, trace=None):
    """Pivot up (smaller c.x) through locally optimal bases until feasible."""
    cc = P.c if c is None else c
    steps = 0
    while not P.feasible(B, h):
        v = P.value(B, cc, h)
        cands = [B2 for B2 in P.neighbors(B) if P.locopt(B2, cc) and P.value(B2, cc, h) < v - 1e-12]
        if not cands:
            return "infeasible", B, steps
        B = choose(cands, rule, lambda X: -P.value(X, cc, h))
        steps += 1
        if trace is not None:
            trace.append(B)
    return "optimal", B, steps


def dual_primal_simplex(P, rule, B0=None):
    """Figure I.4: rotate the objective so that an arbitrary basis is locally optimal; dual phase; primal phase."""
    B = B0 or frozenset(rng.sample(range(P.N), P.d))
    w = np.array([rng.uniform(0.5, 1.5) for _ in range(P.d)])
    ct = w @ P.G[sorted(B)]  # a positive combination of the d normals
    assert P.locopt(B, ct)
    st, B, s1 = dual_phase(P, B, rule, c=ct)
    if st == "infeasible":
        return "infeasible", None, s1
    st, B, s2 = primal_phase(P, B, rule)
    return st, (P.value(B) if st == "optimal" else None), s1 + s2


def primal_dual_simplex(P, rule, B0=None):
    """Figure I.5: translate the constraints so that an arbitrary basis is feasible; primal phase; dual phase."""
    B = B0 or frozenset(rng.sample(range(P.N), P.d))
    x0 = P.loc(B)
    ht = P.G @ x0 + np.array([0 if k in B else rng.uniform(0.5, 2) for k in range(P.N)])
    assert P.feasible(B, ht)
    st, B, s1 = primal_phase(P, B, rule, h=ht)
    if st == "unbounded":
        return "unbounded", None, s1
    st, B, s2 = dual_phase(P, B, rule)
    return st, (P.value(B) if st == "optimal" else None), s1 + s2


def random_lp(n, d, kind):
    A = np.random.randn(n, d)
    b = np.abs(np.random.randn(n)) + 0.05 if kind == "origin" else np.random.randn(n)
    c = np.random.randn(d)
    return LP(A, b, c)


# ---------------------------------------------------------------------- I.1 bases on random non-degenerate LPs
ok_count = ok_nb = ok_dualfeas = ok_order = ok_inf = ok_unb = ok_unique = ok_valeq = True
outcomes = {"optimal": 0, "infeasible": 0, "unbounded": 0}
for trial in range(250):
    n, d = rng.randint(1, 5), rng.randint(1, 4)
    P = random_lp(n, d, rng.choice(["origin", "any"]))
    st, val = lp_status(P.c, P.A, P.b)
    outcomes[st] += 1
    Bs = P.bases()
    ok_count &= len(Bs) == math.comb(n + d, d)
    ok_nb &= all(len(set(P.neighbors(B))) == d * n for B in Bs[:5])
    feas = [B for B in Bs if P.feasible(B)]
    lo = [B for B in Bs if P.locopt(B)]
    # the dual: max -b.y s.t. -A^T y <= -c, y >= 0 ; labels: dual row j <-> primal sign label n + j,
    # dual sign label d + i <-> primal row i ; a primal basis B corresponds to the complement of its image
    Q = LP(-P.A.T, -P.c, -P.b)
    phi = {i: d + i for i in range(n)}
    phi.update({n + j: j for j in range(d)})
    for B in Bs:
        D = frozenset(phi[k] for k in range(P.N) if k not in B)
        ok_dualfeas &= P.locopt(B) == Q.feasible(D) and P.feasible(B) == Q.locopt(D)
        ok_valeq &= abs(P.value(B) + Q.value(D)) < 1e-7
    if feas and lo:
        ok_order &= max(P.value(B) for B in feas) <= min(P.value(B) for B in lo) + 1e-9
    ok_inf &= (not feas) == (st == "infeasible")
    ok_unb &= (not lo) == (st == "unbounded")
    if st == "optimal":
        both = [B for B in feas if P.locopt(B)]
        ok_unique &= len(both) == 1 and abs(P.value(both[0]) - val) < 1e-7 and abs(
            max(P.value(B) for B in feas) - val) < 1e-7 and abs(min(P.value(B) for B in lo) - val) < 1e-7
check("I.1: a canonical LP with n + d constraints has C(n+d, d) bases, every one with d*n neighbors", ok_count and ok_nb,
      str(outcomes))
check("I.1: B is locally optimal for the LP iff the complementary n constraints form a feasible basis of the dual "
      "(and B feasible iff that dual basis is locally optimal), with equal values", ok_dualfeas and ok_valeq)
check("I.1: every feasible basis has value <= every locally optimal basis (weak duality)", ok_order)
check("I.1: no feasible basis <=> infeasible; no locally optimal basis <=> unbounded (non-degenerate LPs)",
      ok_inf and ok_unb)
check("I.1: if an optimum exists it is the unique feasible and locally optimal basis, the best feasible and the worst "
      "locally optimal one", ok_unique)

# ---------------------------------------------------------------------- I.2 PrimalSimplex and DualSimplex
ok_ps = ok_ds = ok_mono = ok_bound = ok_corr = True
cnt = {"primal": 0, "dual": 0}
for trial in range(500):
    n, d = rng.randint(1, 5), rng.randint(1, 4)
    P = random_lp(n, d, rng.choice(["origin", "any"]))
    st, val = lp_status(P.c, P.A, P.b)
    Bs = P.bases()
    feas = [B for B in Bs if P.feasible(B)]
    lo = [B for B in Bs if P.locopt(B)]
    rule = rng.choice(["random", "best", "first"])
    if feas:  # PrimalSimplex from any feasible vertex ("if the intersection is empty, return Infeasible")
        trace = [rng.choice(feas)]
        s2, B, steps = primal_phase(P, trace[0], rule, trace=trace)
        cnt["primal"] += 1
        ok_ps &= s2 == st and (st != "optimal" or abs(P.value(B) - val) < 1e-7)
        vals = [P.value(X) for X in trace]
        ok_mono &= all(v2 > v1 for v1, v2 in zip(vals, vals[1:])) and all(P.feasible(X) for X in trace)
        ok_bound &= steps <= math.comb(n + d, d)
    else:
        ok_ps &= st == "infeasible"
    if lo:
        trace = [rng.choice(lo)]
        s3, B, steps = dual_phase(P, trace[0], rule, trace=trace)
        cnt["dual"] += 1
        ok_ds &= s3 == ("optimal" if st == "optimal" else "infeasible") and (st != "optimal" or abs(P.value(B) - val) < 1e-7)
        vals = [P.value(X) for X in trace]
        ok_mono &= all(v2 < v1 for v1, v2 in zip(vals, vals[1:])) and all(P.locopt(X) for X in trace)
        ok_bound &= steps <= math.comb(n + d, d)
    else:
        ok_ds &= st == "unbounded"
    # PrimalSimplex on the LP = DualSimplex on its dual, pivot for pivot (rule 'best' on both sides)
    if feas:
        Q = LP(-P.A.T, -P.c, -P.b)
        phi = {i: d + i for i in range(n)}
        phi.update({n + j: j for j in range(d)})
        comp = lambda B: frozenset(phi[k] for k in range(P.N) if k not in B)
        B0 = feas[0]
        t1, t2 = [B0], [comp(B0)]
        r1 = primal_phase(P, B0, "best", trace=t1)
        r2 = dual_phase(Q, comp(B0), "best", trace=t2)
        ok_corr &= [comp(X) for X in t1] == t2 and (r1[0] == "optimal") == (r2[0] == "optimal")
check("I.2 PrimalSimplex (random, best and first-candidate rules) agrees with linprog, starting from a feasible "
      "vertex", ok_ps, str(cnt))
check("I.2 DualSimplex agrees with linprog (Infeasible when it gets stuck), starting from a locally optimal vertex",
      ok_ds)
check("I.2: primal pivots raise c.x and stay feasible; dual pivots lower c.x and stay locally optimal", ok_mono)
check("I.2: at most C(n+d, d) pivots", ok_bound)
check("I.2: PrimalSimplex on the LP and DualSimplex on its dual visit complementary bases, pivot for pivot", ok_corr)

# ---------------------------------------------------------------------- I.3 initialization
ok_dp = ok_pd = True
cnt3 = {"optimal": 0, "infeasible": 0, "unbounded": 0}
for trial in range(1500):
    n, d = rng.randint(1, 6), rng.randint(1, 4)
    P = random_lp(n, d, rng.choice(["origin", "any", "any"]))
    st, val = lp_status(P.c, P.A, P.b)
    cnt3[st] += 1
    rule = rng.choice(["random", "best", "first"])
    s1, v1, _ = dual_primal_simplex(P, rule)
    s2, v2, _ = primal_dual_simplex(P, rule)
    ok_dp &= s1 == st and (st != "optimal" or abs(v1 - val) < 1e-6)
    ok_pd &= s2 == st and (st != "optimal" or abs(v2 - val) < 1e-6)
check("I.3 DualPrimalSimplex (Figure I.4: objective rotated to a positive combination of the start basis' normals) "
      "agrees with linprog on 1500 random LPs", ok_dp, str(cnt3))
check("I.3 PrimalDualSimplex (Figure I.5: constraints translated so the start basis is feasible) agrees with linprog",
      ok_pd)

# the note's sufficient condition 'positive inner product with each of the d normals' is not sufficient
bad = tot = 0
for trial in range(2000):
    n, d = rng.randint(1, 4), rng.randint(2, 4)
    P = random_lp(n, d, "any")
    B = frozenset(rng.sample(range(P.N), d))
    GB = P.G[sorted(B)]
    c2 = np.random.randn(d)
    if np.all(GB @ c2 > 0):
        tot += 1
        bad += not P.locopt(B, c2)
check("I.3 (note p. 5): 'a positive inner product with each normal' does not make a basis locally optimal",
      bad > 0.1 * tot and tot > 100, f"{bad} of {tot} such vectors fail")
# the page's counterexample: max x + 2y s.t. x <= 0, x + y <= 0 ; origin; c.(1,0) = 1 > 0, c.(1,1) = 3 > 0
P2 = LP([[1, 0], [1, 1]], [0, 0], [1, 2])
B = frozenset([0, 1])
x = np.array([-1.0, 1.0])
check("I.3 counterexample: c = (1, 2), normals (1, 0) and (1, 1): both inner products positive, yet (-1, 1) is "
      "feasible for the two constraints with value 1 > 0, and c = -1*(1, 0) + 2*(1, 1)",
      np.allclose(P2.loc(B), [0, 0]) and not P2.locopt(B) and np.all(P2.A @ x <= 0) and P2.c @ x == 1
      and np.allclose(P2.mult(B), [-1, 2]))
ok_sum = True
for trial in range(500):
    n, d = rng.randint(1, 4), rng.randint(1, 4)
    P = random_lp(n, d, "any")
    B = frozenset(rng.sample(range(P.N), d))
    ct = P.G[sorted(B)].sum(0)
    ok_sum &= P.locopt(B, ct) and np.allclose(P.mult(B, ct), 1)
check("I.3: c = sum of the normals of B makes B locally optimal (multipliers all 1), 500 random bases", ok_sum)

# ---------------------------------------------------------------------- Exercise 1(a) needs a bounded region
P3 = LP([[1, -1]], [1], [0, 1])
B0 = frozenset([1, 2])  # x1 = 0, x2 = 0
fn = [B for B in P3.neighbors(B0) if P3.feasible(B)]
check("Exercise 1(a) (p. 12) fails without boundedness: in {x >= 0, x1 - x2 <= 1} the feasible vertex (0, 0) has "
      "1 feasible neighbor, not d = 2", P3.feasible(B0) and len(fn) == 1)


# ============================================================================== dictionary (tableau) simplex
def dictionary_simplex(A, b, c, rule="dantzig", trace=None):
    """Textbook dictionary simplex for max c.x, Ax <= b, x >= 0 with b >= 0 (start at the origin), exact arithmetic.
    Variables 0..d-1 are x, d..d+n-1 the slacks w. Returns (status, value, x, pivots)."""
    n, d = len(A), len(c)
    # basic variable of row i, and row i: x_B = beta_i + sum_j alpha_ij x_N(j)
    basic = [d + i for i in range(n)]
    nonbasic = list(range(d))
    beta = [Fr(v) for v in b]
    alpha = [[Fr(-A[i][j]) for j in range(d)] for i in range(n)]
    z0, zc = Fr(0), [Fr(v) for v in c]
    pivots = 0
    while True:
        enter_cands = [j for j in range(d) if zc[j] > 0]
        if not enter_cands:
            break
        if rule == "dantzig":
            j = max(enter_cands, key=lambda k: (zc[k], -nonbasic[k]))
        else:  # Bland: smallest variable index
            j = min(enter_cands, key=lambda k: nonbasic[k])
        rows = [i for i in range(n) if alpha[i][j] < 0]
        if not rows:
            return "unbounded", None, None, pivots
        i = min(rows, key=lambda r: (beta[r] / -alpha[r][j], basic[r]))
        # solve row i for the entering variable
        a = alpha[i][j]
        new_beta = -beta[i] / a
        new_row = [-alpha[i][k] / a for k in range(d)]
        new_row[j] = Fr(1) / a  # coefficient of the leaving variable
        for r in range(n):
            if r == i:
                continue
            f = alpha[r][j]
            beta[r] += f * new_beta
            alpha[r] = [alpha[r][k] + f * new_row[k] if k != j else f * new_row[j] for k in range(d)]
        f = zc[j]
        z0 += f * new_beta
        zc = [zc[k] + f * new_row[k] if k != j else f * new_row[j] for k in range(d)]
        beta[i], alpha[i] = new_beta, new_row
        basic[i], nonbasic[j] = nonbasic[j], basic[i]
        pivots += 1
        if trace is not None:
            xv = [Fr(0)] * d
            for r in range(n):
                if basic[r] < d:
                    xv[basic[r]] = beta[r]
            trace.append((nonbasic[j], basic[i], tuple(xv), z0, frozenset(nonbasic), dict(zip(nonbasic, zc))))
    xv = [Fr(0)] * d
    for r in range(n):
        if basic[r] < d:
            xv[basic[r]] = beta[r]
    return "optimal", z0, xv, pivots


# the concept page's worked example: Vanderbei's LP from note H.6
VA, Vb, Vc = [[1, 4, 0], [3, -1, 1]], [2, 4], [4, 1, 3]
tr = []
st, z, xv, piv = dictionary_simplex(VA, Vb, Vc, trace=tr)
check("dictionary simplex on max 4x1 + x2 + 3x3 (Dantzig's rule): optimum 14 at (0, 1/2, 9/2) after 3 pivots",
      st == "optimal" and z == 14 and xv == [0, Fr(1, 2), Fr(9, 2)] and piv == 3)
# variables: 0, 1, 2 = x1, x2, x3 ; 3, 4 = w1, w2 (slacks of rows 1, 2)
expect = [(0, 4, (Fr(4, 3), 0, 0), Fr(16, 3)), (1, 3, (Fr(18, 13), Fr(2, 13), 0), Fr(74, 13)),
          (2, 0, (0, Fr(1, 2), Fr(9, 2)), Fr(14))]
got = [(basic_in, out, x, v) for (out, basic_in, x, v, _, _) in tr]
check("dictionary example: x1 enters/w2 leaves -> (4/3, 0, 0), 16/3; x2 enters/w1 leaves -> (18/13, 2/13, 0), 74/13; "
      "x3 enters/x1 leaves -> (0, 1/2, 9/2), 14", got == expect, str(got))
# Erickson's basis = the d tight constraints = the NONbasic variables of the dictionary
ok_tight = True
for (_, _, x, v, nb, _) in tr:
    rows = [sum(Fr(VA[i][j]) * x[j] for j in range(3)) for i in range(2)]
    tight = {j for j in range(3) if x[j] == 0} | {3 + i for i in range(2) if rows[i] == Vb[i]}
    ok_tight &= tight == set(nb) and len(tight) == 3
check("dictionary vs Erickson: at every vertex of the run the tight constraints (x_j = 0 or row i tight) are exactly "
      "the nonbasic variables (x_j or w_i), d = 3 of them", ok_tight)

check("dictionary example: after pivot 1 the objective is 16/3 + 7/3 x2 + 5/3 x3 - 4/3 w2; after pivot 3 every "
      "coefficient is negative", tr[0][5] == {1: Fr(7, 3), 2: Fr(5, 3), 4: Fr(-4, 3)} and all(v < 0 for v in tr[2][5].values()),
      str(tr[2][5]))
check("dictionary example: the ratio test of pivot 1 allows x1 <= 2 (row 1) and x1 <= 4/3 (row 2)",
      Fr(Vb[0], VA[0][0]) == 2 and Fr(Vb[1], VA[1][0]) == Fr(4, 3))

# Klee-Minty (Chvatal's form): Dantzig's rule takes 2^d - 1 pivots
ok_km = True
for d in range(1, 8):
    A = [[(2 * 10 ** (i - j) if j < i else 1 if j == i else 0) for j in range(d)] for i in range(d)]
    b = [100 ** i for i in range(d)]
    c = [10 ** (d - 1 - j) for j in range(d)]
    st, z, xv, piv = dictionary_simplex(A, b, c)
    stB, zB, _, pivB = dictionary_simplex(A, b, c, rule="bland")
    ok_km &= st == "optimal" and piv == 2 ** d - 1 and z == 100 ** (d - 1) and zB == z
check("Klee-Minty cube (max sum 10^(d-j) x_j, 2 sum_{j<i} 10^(i-j) x_j + x_i <= 100^(i-1)): Dantzig's rule makes "
      "2^d - 1 pivots, d = 1..7, optimum 100^(d-1)", ok_km)
ok_cmp = True
for trial in range(300):
    n, d = rng.randint(1, 5), rng.randint(1, 4)
    A = [[rng.randint(-4, 6) for _ in range(d)] for _ in range(n)]
    b = [rng.randint(0, 8) for _ in range(n)]
    c = [rng.randint(-3, 6) for _ in range(d)]
    st0, val = lp_status(c, A, b)
    stB, zB, _, _ = dictionary_simplex(A, b, c, rule="bland")
    ok_cmp &= st0 == stB and (st0 != "optimal" or abs(float(zB) - val) < 1e-7)
check("dictionary simplex with Bland's rule (degenerate integer LPs, origin feasible) agrees with linprog", ok_cmp)


# ============================================================================== I.4 network simplex
def spanning_trees(V, E):
    n = len(V)
    for F in itertools.combinations(range(len(E)), n - 1):
        parent = {v: v for v in V}

        def find(v):
            while parent[v] != v:
                parent[v] = parent[parent[v]]
                v = parent[v]
            return v
        ok = True
        for k in F:
            a, b2 = find(E[k][0]), find(E[k][1])
            if a == b2:
                ok = False
                break
            parent[a] = b2
        if ok:
            yield frozenset(F)


def comp_without(V, E, T, k):
    """Vertex set of the component of T - E[k] that contains E[k][1] (the head)."""
    adj = {v: [] for v in V}
    for j in T:
        if j != k:
            u, v = E[j]
            adj[u].append(v); adj[v].append(u)
    start = E[k][1]
    seen, st = {start}, [start]
    while st:
        u = st.pop()
        for w in adj[u]:
            if w not in seen:
                seen.add(w); st.append(w)
    return seen


def flow_T(V, E, bal, T):
    """The note's formula: flow on tree edge u->v = total balance of the component of T - uv containing v."""
    f = [0.0] * len(E)
    for k in T:
        f[k] = sum(bal[v] for v in comp_without(V, E, T, k))
    return f


def potentials(V, E, cost, T):
    root = V[0]
    pi = {root: 0.0}
    changed = True
    while changed:
        changed = False
        for k in T:
            u, v = E[k]
            if u in pi and v not in pi:
                pi[v] = pi[u] + cost[k]; changed = True
            elif v in pi and u not in pi:
                pi[u] = pi[v] - cost[k]; changed = True
    return pi


def tree_path(V, E, T, a, b2):
    """Edges (index, +1 forward / -1 backward) of the tree path from a to b2."""
    adj = {v: [] for v in V}
    for k in T:
        u, v = E[k]
        adj[u].append((v, k, +1)); adj[v].append((u, k, -1))
    prev = {a: None}
    st = [a]
    while st:
        u = st.pop()
        for w, k, sg in adj[u]:
            if w not in prev:
                prev[w] = (u, k, sg); st.append(w)
    path, x = [], b2
    while prev[x] is not None:
        u, k, sg = prev[x]
        path.append((k, sg)); x = u
    return path[::-1]


def slack_T(V, E, cost, T):
    """slack(u->v) = cost of the cycle u->v + tree path v ~> u (0 on tree edges)."""
    s = [0.0] * len(E)
    for k in range(len(E)):
        if k in T:
            continue
        u, v = E[k]
        s[k] = cost[k] + sum(sg * cost[j] for j, sg in tree_path(V, E, T, v, u))
    return s


def tcost(cost, f):
    return sum(c * x for c, x in zip(cost, f))


def random_transship(rng):
    while True:
        n = rng.randint(3, 5)
        V = list(range(n))
        E = []
        for u in V:
            for v in V:
                if u != v and rng.random() < 0.45:
                    E.append((u, v))
        if len(E) > 8 or len(E) < n - 1:
            continue
        # connected as an undirected graph?
        if not any(True for _ in spanning_trees(V, E)):
            continue
        bal = [rng.uniform(-5, 5) for _ in V[:-1]]
        bal.append(-sum(bal))
        if rng.random() < 0.5:
            pot = [rng.uniform(-3, 3) for _ in V]
            cost = [rng.uniform(0.1, 6) + pot[u] - pot[v] for (u, v) in E]  # no negative cycle
        else:
            cost = [rng.uniform(-3, 6) for _ in E]
        return V, E, bal, cost


def lp_transship(V, E, bal, cost):
    Aeq = [[(1 if e[1] == v else 0) - (1 if e[0] == v else 0) for e in E] for v in V[1:]]
    res = linprog(cost, A_eq=Aeq, b_eq=bal[1:], bounds=[(0, None)] * len(E), method="highs")
    if res.status == 0:
        return "optimal", res.fun
    r0 = linprog(np.zeros(len(E)), A_eq=Aeq, b_eq=bal[1:], bounds=[(0, None)] * len(E), method="highs")
    return ("infeasible", None) if r0.status == 2 else ("unbounded", None)


ok_l1 = ok_basis = ok_char = ok_opt = ok_cs = ok_neg = ok_pivot = ok_srule = ok_dual = ok_spt = ok_note_dual = True
ok_ns = True
negfree = 0
cnts = {"optimal": 0, "infeasible": 0, "unbounded": 0}
for trial in range(300):
    V, E, bal, cost = random_transship(rng)
    n, m = len(V), len(E)
    st, val = lp_transship(V, E, bal, cost)
    cnts[st] += 1
    trees = list(spanning_trees(V, E))
    # balanced bases <=> spanning trees: the V-1 balance rows plus f_e = 0 for e not in F are independent iff F is a tree
    Aeq = np.array([[(1 if e[1] == v else 0) - (1 if e[0] == v else 0) for e in E] for v in V[1:]], float)
    for F in itertools.combinations(range(m), n - 1):
        rows = [Aeq] + [np.eye(m)[[k]] for k in range(m) if k not in F]
        full = np.linalg.matrix_rank(np.vstack(rows)) == m
        ok_basis &= full == (frozenset(F) in set(trees))
    found = []
    for T in trees:
        f = flow_T(V, E, bal, T)
        # Lemma I.1: balanced everywhere and the unique flow supported on T
        ok_l1 &= all(abs(sum(f[k] for k in range(m) if E[k][1] == v) - sum(f[k] for k in range(m) if E[k][0] == v)
                         - bal[v]) < 1e-9 for v in V)
        sol = np.linalg.solve(np.vstack([Aeq[:, sorted(T)]]), np.array(bal[1:]))
        ok_l1 &= np.allclose([f[k] for k in sorted(T)], sol)
        s = slack_T(V, E, cost, T)
        pi = potentials(V, E, cost, T)
        ok_l1 &= all(abs(s[k] - (cost[k] + pi[E[k][0]] - pi[E[k][1]])) < 1e-9 for k in range(m))  # reduced costs
        ok_cs &= all(abs(f[k] * s[k]) < 1e-12 for k in range(m))
        feasible = all(f[k] >= 0 for k in T)
        locopt = all(s[k] >= 0 for k in range(m) if k not in T)
        negfree += any(f[k] < 0 for k in T)
        if feasible and locopt:
            found.append(tcost(cost, f))
    if st == "optimal":
        ok_opt &= len(found) == 1 and abs(found[0] - val) < 1e-7
    else:
        ok_opt &= not found
    # primal network simplex from a feasible tree
    feas_trees = [T for T in trees if all(x >= 0 for k, x in enumerate(flow_T(V, E, bal, T)) if k in T)]
    if feas_trees:
        T = rng.choice(feas_trees)
        result = None
        for _ in range(200):
            f = flow_T(V, E, bal, T); s = slack_T(V, E, cost, T)
            cand = [k for k in range(m) if k not in T and s[k] < -1e-12]
            if not cand:
                result = ("optimal", tcost(cost, f)); break
            ein = rng.choice(cand)
            u, v = E[ein]
            cyc = tree_path(V, E, T, v, u)
            back = [(k, f[k]) for k, sg in cyc if sg < 0]
            if not back:
                result = ("unbounded", None); break
            eout = min(back, key=lambda z: z[1])[0]
            T2 = (T - {eout}) | {ein}
            f2 = flow_T(V, E, bal, T2); s2 = slack_T(V, E, cost, T2)
            ok_pivot &= all(f2[k] >= -1e-9 for k in T2)
            ok_pivot &= abs(tcost(cost, f2) - tcost(cost, f) - f[eout] * s[ein]) < 1e-7 and f[eout] * s[ein] < 0
            # the S rule: S = component of T - eout containing the tail of eout; ein leaves S
            Sc = comp_without(V, E, T, eout)            # head side of eout
            S = set(V) - Sc
            ok_srule &= E[ein][0] in S and E[ein][1] not in S
            sig = s[ein]
            for k in range(m):
                a, b2 = E[k]
                exp = s[k] - sig * (a in S and b2 not in S) + sig * (a not in S and b2 in S)
                ok_srule &= abs(s2[k] - exp) < 1e-7
            T = T2
        ok_ns &= result is not None and result[0] == st and (st != "optimal" or abs(result[1] - val) < 1e-7)
    # dual network simplex from a locally optimal tree (e.g. a shortest-path tree)
    lo_trees = [T for T in trees if all(x >= 0 for k, x in enumerate(slack_T(V, E, cost, T)) if k not in T)]
    if lo_trees:
        T = rng.choice(lo_trees)
        result = None
        for _ in range(200):
            f = flow_T(V, E, bal, T); s = slack_T(V, E, cost, T)
            cand = [k for k in T if f[k] < -1e-12]
            if not cand:
                result = ("optimal", tcost(cost, f)); break
            eout = rng.choice(cand)
            Sc = comp_without(V, E, T, eout)
            S = set(V) - Sc                          # contains the tail of eout
            ins = [k for k in range(m) if k not in T and E[k][0] in Sc and E[k][1] in S]  # from V\S into S
            if not ins:
                result = ("infeasible", None); break
            ein = min(ins, key=lambda k: s[k])
            sig = s[ein]
            T2 = (T - {eout}) | {ein}
            f2 = flow_T(V, E, bal, T2); s2 = slack_T(V, E, cost, T2)
            ok_dual &= all(s2[k] >= -1e-9 for k in range(m) if k not in T2)
            ok_dual &= tcost(cost, f2) >= tcost(cost, f) - 1e-9
            ok_dual &= abs(tcost(cost, f2) - tcost(cost, f) + f[eout] * sig) < 1e-7
            for k in range(m):
                a, b2 = E[k]
                exp = s[k] + sig * (a in S and b2 not in S) - sig * (a not in S and b2 in S)
                ok_dual &= abs(s2[k] - exp) < 1e-7
            # the note's bullet (subtract from S -> V\S, add to V\S -> S) would give ein the slack 2*sig, not 0
            ok_note_dual &= sig < 1e-12 or abs(s[ein] + sig - 0) > 1e-9
            T = T2
        ok_dual &= result is not None and (result[0] == "optimal") == (st == "optimal") and (
            st != "optimal" or abs(result[1] - val) < 1e-7) and (result[0] != "infeasible" or st == "infeasible")
    # a shortest-path tree from a root that reaches every vertex is locally optimal (no negative cycles)
    root = 0
    dist = {v: math.inf for v in V}; dist[root] = 0; pred = {}
    for _ in range(n):
        for k, (u, v) in enumerate(E):
            if dist[u] + cost[k] < dist[v] - 1e-12:
                dist[v] = dist[u] + cost[k]; pred[v] = k
    negcyc = any(dist[u] + cost[k] < dist[v] - 1e-9 for k, (u, v) in enumerate(E))
    if not negcyc and all(dist[v] < math.inf for v in V):
        T = frozenset(pred.values())
        s = slack_T(V, E, cost, T)
        ok_spt &= len(T) == n - 1 and all(s[k] >= -1e-9 for k in range(m))
check("I.4: the V - 1 balance constraints plus 'f(e) = 0' for the edges outside F are independent iff F is a "
      "spanning tree (balanced bases = spanning trees)", ok_basis, str(cnts))
check("Lemma I.1: flow_T (balance of the head side of each tree edge) is balanced everywhere and is the unique flow "
      "supported on T; slack_T = cost of the fundamental cycle = reduced cost", ok_l1)
check("I.4: flow_T(e) * slack_T(e) = 0 for every edge (complementary slackness automatically)", ok_cs)
check("I.4: the tree that is both feasible (flow >= 0) and locally optimal (slack >= 0) is unique and gives the "
      "minimum cost (linprog), and exists iff the LP has an optimum", ok_opt)
check("I.4 (note p. 8): flows of balanced bases can be negative on free (tree) edges", negfree > 100,
      f"{negfree} trees with a negative tree flow")
check("I.4 primal pivot: e_in with negative slack, e_out = backward cycle edge of least flow; stays feasible; cost "
      "changes by flow(e_out) * slack(e_in) < 0", ok_pivot)
check("I.4 primal pivot: e_in goes from S (tail side of e_out) to V\\S; slacks drop by slack(e_in) on edges S -> "
      "V\\S and rise on edges V\\S -> S", ok_srule)
check("I.4 primal network simplex (cycle cancelling) reaches linprog's optimum or detects unboundedness", ok_ns)
check("I.4 dual pivot: e_out with negative flow, e_in = least-slack edge from V\\S into S; slacks rise by "
      "slack(e_in) on S -> V\\S and drop on V\\S -> S (the reverse of the primal rule); cost rises by "
      "|flow(e_out)| * slack(e_in); ends at the optimum or 'infeasible'", ok_dual)
check("I.4: a shortest-path tree (root reaches every vertex, no negative cycle) is locally optimal", ok_spt)


# ============================================================================== I.5 Seidel's algorithm
def solve_small(H, B, d, c, M):
    """Brute force: max c.x over the halfspaces H (list of (a, b)), the hyperplanes B and the box |x_i| <= M."""
    box = [(tuple(1.0 if i == j else 0.0 for i in range(d)), M) for j in range(d)] + \
          [(tuple(-1.0 if i == j else 0.0 for i in range(d)), M) for j in range(d)]
    cons = list(H) + box
    best = None
    for S in itertools.combinations(range(len(cons)), d - len(B)):
        rows = [np.array(a) for a, _ in B] + [np.array(cons[k][0]) for k in S]
        rhs = [bb for _, bb in B] + [cons[k][1] for k in S]
        Mx = np.array(rows)
        if abs(np.linalg.det(Mx)) < 1e-12:
            continue
        x = np.linalg.solve(Mx, rhs)
        if all(np.dot(a, x) <= bb + 1e-9 for a, bb in cons):
            v = float(np.dot(c, x))
            if best is None or v > best[0] + 1e-12:
                best = (v, tuple(np.round(x, 12)))
    return best


def seidel(H, B, d, c, M, counter):
    """SeidelLP(H, B) as in the note, plus a bounding box that is never sampled (so every subproblem is bounded)."""
    counter["calls"] += 1
    if len(B) == d:
        counter["leaves"] += 1
        x = np.linalg.solve(np.array([a for a, _ in B]), [bb for _, bb in B])
        return tuple(np.round(x, 12))
    if len(H) + len(B) == d:
        counter["leaves"] += 1
        return solve_small(H, B, d, c, M)[1]
    h = rng.choice(H)
    H2 = [g for g in H if g is not h]
    x = seidel(H2, B, d, c, M, counter)
    if np.dot(h[0], x) > h[1] + 1e-9:
        return seidel(H2, B + [h], d, c, M, counter)
    return x


def T_note(n, delta):
    @lru_cache(None)
    def T(n, dl):
        if dl == 0 or n == dl:
            return Fr(1)
        return T(n - 1, dl) + Fr(dl, n) * T(n - 1, dl - 1)
    return T(n, delta)


def T_calls(n, delta):
    @lru_cache(None)
    def T(n, dl):
        if dl == 0 or n == dl:
            return Fr(1)
        return 1 + T(n - 1, dl) + Fr(dl, n) * T(n - 1, dl - 1)
    return T(n, delta)


def exact_expectations(H, d, c, M):
    """Exact E[#calls] and E[#base calls] of the randomized recursion, by recursion over (subset of H, B)."""
    idx = list(range(len(H)))

    @lru_cache(None)
    def opt(Hs, Bs):
        return solve_small([H[i] for i in Hs], [H[i] for i in Bs], d, c, M)[1]

    @lru_cache(None)
    def E(Hs, Bs):
        if len(Bs) == d or len(Hs) + len(Bs) == d:
            return Fr(1), Fr(1)
        tc, tl = Fr(0), Fr(0)
        for i in Hs:
            H2 = tuple(j for j in Hs if j != i)
            c1, l1 = E(H2, Bs)
            x = opt(H2, Bs)
            tc += c1; tl += l1
            a, bb = H[i]
            if np.dot(a, x) > bb + 1e-9:
                c2, l2 = E(H2, tuple(sorted(Bs + (i,))))
                tc += c2; tl += l2
        k = len(Hs)
        return 1 + tc / k, tl / k

    return E(tuple(idx), ())


ok_seidel = True
for trial in range(300):
    d = rng.choice([1, 2, 2, 3])
    n = rng.randint(d, 9 if d < 3 else 7)
    H = [(tuple(np.random.randn(d)), float(abs(np.random.randn()) + 0.2)) for _ in range(n)]
    c = np.random.randn(d)
    M = 50.0
    cnt = {"calls": 0, "leaves": 0}
    x = seidel(H, [], d, c, M, cnt)
    ref = solve_small(H, [], d, c, M)
    A = np.array([a for a, _ in H] + [list(e) for e in np.eye(d)] + [list(-e) for e in np.eye(d)])
    bvec = [bb for _, bb in H] + [M] * (2 * d)
    res = linprog(-c, A_ub=A, b_ub=bvec, bounds=[(None, None)] * d, method="highs")
    ok_seidel &= abs(float(np.dot(c, x)) - ref[0]) < 1e-7 and abs(-res.fun - ref[0]) < 1e-6
check("I.5 SeidelLP (with a never-sampled bounding box) returns the optimum (brute force and linprog), d = 1, 2, 3, "
      "300 random LPs", ok_seidel)

# d = 1, halfspaces x >= a_i, lowest point = max a_i: every subproblem is bounded, no box needed, exact equality
ok_d1 = True
for n in range(1, 9):
    H = [((-1.0,), -float(a)) for a in np.random.rand(n) * 10]  # -x <= -a  <=>  x >= a
    ec, el = exact_expectations(H, 1, np.array([-1.0]), 1e6)
    Hn = sum(Fr(1, k) for k in range(1, n + 1))
    ok_d1 &= el == T_note(n, 1) == Hn and ec == T_calls(n, 1) == n + Hn - 1
check("I.5, d = 1: the note's recurrence T(n, 1) = H_n is the exact expected number of BASE-CASE calls; the expected "
      "number of all calls is n + H_n - 1, from the recurrence with '1 +' (n = 1..8)", ok_d1)
ok_le = True
for trial in range(60):
    d = rng.choice([2, 2, 3])
    n = rng.randint(d, 7 if d == 2 else 6)
    H = [(tuple(np.random.randn(d)), float(abs(np.random.randn()) + 0.2)) for _ in range(n)]
    c = np.random.randn(d)
    ec, el = exact_expectations(H, d, c, 50.0)
    ok_le &= el <= T_note(n, d) + Fr(1, 10 ** 9) and ec <= T_calls(n, d) + Fr(1, 10 ** 9)
check("I.5, d = 2, 3: exact E[#base calls] <= T(n, d) and E[#calls] <= T'(n, d) (violation probability <= (d-b)/n "
      "once a bounding box may define the optimum)", ok_le)
ok_rec = ok_rec2 = ok_over = True
for dl in range(0, 7):
    cdl = sum(Fr(math.factorial(dl), math.factorial(k)) for k in range(dl + 1))
    for n in range(max(dl, 1), 80):
        ok_rec &= T_note(n, dl) <= math.factorial(dl) * n
        ok_rec2 &= T_calls(n, dl) <= cdl * n and cdl < math.e * math.factorial(dl) + 1e-12
    if 1 <= dl <= 3:
        ok_over &= T_calls(60, dl) > math.factorial(dl) * 60
check("I.5: the note's induction T(n, delta) <= delta! n holds (delta <= 6, n < 80)", ok_rec)
check("I.5: with '1 +' the bound becomes T'(n, delta) <= (sum_k delta!/k!) n < e delta! n — still O(delta! n)", ok_rec2)
check("I.5: ... but T'(n, delta) <= delta! n itself fails (n = 60, delta = 1, 2, 3)", ok_over)
check("I.5: T'(n, 1) = n + H_n - 1 > n for n >= 2", all(T_calls(n, 1) == n + sum(Fr(1, k) for k in range(1, n + 1)) - 1
                                                      for n in range(1, 30)))

# ============================================================================== figures and page text
def figure_text(name):
    p = os.path.join(FIGS, name + ".html")
    return open(p, encoding="utf-8").read() if os.path.exists(p) else ""


# the LP of figure ni-simplex-paths: max x + 5y, x + 3y <= 9, 2x + 3y <= 12, x + y <= 7, x, y >= 0
PF = LP([[1, 3], [2, 3], [1, 1]], [9, 12, 7], [1, 5])
st, val = lp_status(PF.c, PF.A, PF.b)
B = frozenset([3, 4])
ppath = [B]
while not PF.locopt(B):
    B = min((X for X in PF.neighbors(B) if PF.feasible(X) and PF.value(X) > PF.value(B) + 1e-12), key=PF.value)
    ppath.append(B)
B = max((X for X in PF.bases() if PF.locopt(X)), key=PF.value)
dpath = [B]
while not PF.feasible(B):
    B = max((X for X in PF.neighbors(B) if PF.locopt(X) and PF.value(X) < PF.value(B) - 1e-12), key=PF.value)
    dpath.append(B)
check("figure ni-simplex-paths: optimum 15 at (0, 3) (linprog); primal run (smaller gain each time) visits "
      "(0,0) 0, (6,0) 6, (3,2) 13, (0,3) 15; dual run from the top locally optimal vertex visits (0,7) 35, (0,4) 20, "
      "(0,3) 15", st == "optimal" and abs(val - 15) < 1e-9
      and [tuple(np.round(PF.loc(X), 9)) for X in ppath] == [(0, 0), (6, 0), (3, 2), (0, 3)]
      and [round(PF.value(X), 9) for X in ppath] == [0, 6, 13, 15]
      and [tuple(np.round(PF.loc(X), 9)) for X in dpath] == [(0, 7), (0, 4), (0, 3)]
      and [round(PF.value(X), 9) for X in dpath] == [35, 20, 15])
check("figure ni-simplex-paths: 4 feasible and 3 locally optimal vertices among the 10; x + y <= 7 is redundant",
      sum(PF.feasible(X) for X in PF.bases()) == 4 and sum(PF.locopt(X) for X in PF.bases()) == 3
      and lp_status(PF.c, PF.A[:2], PF.b[:2])[1] == val)
fig = figure_text("ni-simplex-paths")
check("figure ni-simplex-paths: labels drawn", all(t in fig for t in ["(0, 0): 0", "(6, 0): 6", "(3, 2): 13",
                                                                     "(0, 3): 15", "(0, 4): 20", "(0, 7): 35"]))
# the network of figure ni-network-pivot
NV = [0, 1, 2, 3]  # a b c d
NE = [(0, 1), (0, 2), (1, 2), (1, 3), (2, 3)]
NB = [-5, 2, 1, 2]
NC = [2, 5, 1, 4, 2]
st, val = lp_transship(NV, NE, NB, NC)
T = frozenset([0, 1, 3])
costs, seq = [], []
for _ in range(5):
    f = flow_T(NV, NE, NB, T); sl = slack_T(NV, NE, NC, T)
    costs.append(round(tcost(NC, f), 9))
    cand = [k for k in range(5) if k not in T and sl[k] < 0]
    if not cand:
        break
    ein = min(cand, key=lambda k: sl[k])
    u, v = NE[ein]
    back = [(k, f[k]) for k, sg in tree_path(NV, NE, T, v, u) if sg < 0]
    eout = min(back, key=lambda z: z[1])[0]
    seq.append((NE[ein], NE[eout], round(sl[ein], 9), round(f[eout], 9)))
    T = (T - {eout}) | {ein}
check("figure ni-network-pivot: costs 21 -> 19 -> 17 = linprog's minimum; pivots in b->c (slack -2) out a->c "
      "(flow 1), then in c->d (slack -1) out b->d (flow 2)", st == "optimal" and abs(val - 17) < 1e-9
      and costs == [21, 19, 17] and seq == [((1, 2), (0, 2), -2, 1), ((2, 3), (1, 3), -1, 2)])
check("figure ni-network-pivot: non-degenerate (no proper subset of balances sums to 0)",
      all(sum(NB[v] for v in S_) != 0 for k in range(1, 4) for S_ in itertools.combinations(NV, k)))
fig = figure_text("ni-network-pivot")
check("figure ni-network-pivot: drawn", "cost 21" in fig and "cost 19" in fig and "cost 17" in fig)

if os.path.exists(PAGE):
    page = open(PAGE, encoding="utf-8").read()
    check("page: Klee-Minty count 2^d - 1 stated", "2^d - 1" in page or "2^d-1" in page or "2^d − 1" in page)
if os.path.exists(CONCEPT):
    cp = open(CONCEPT, encoding="utf-8").read()
    check("concept page: the worked example's values 16/3 and 14 present", "16/3" in cp and "14" in cp)

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: {FAIL}")
sys.exit(1 if FAIL else 0)
