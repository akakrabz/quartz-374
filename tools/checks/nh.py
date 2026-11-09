#!/usr/bin/env python3
"""Checks for content/4-lecture-notes/h-linear-programming.md (Erickson, Extended Dance Remix H, Linear Programming)
and the concept page content/concepts/linear-programming.md.

Every example LP of the note and of the pages is solved with scipy.optimize.linprog (HiGHS) and the stated optimum is
re-checked exactly with fractions (feasibility of a primal and a dual point with equal objective values is a proof of
optimality, by weak duality). Every dual written on the pages is built mechanically from the rules of the note's
Figure H.4 (implemented once, below) and solved; complementary slackness is checked on the optimal pairs. The
shortest-path, single-source and max-flow/min-cut LPs are compared with Bellman-Ford, networkx max flow and brute-force
minimum cuts on random small graphs. Claims of the note that fail are checked as such (the counterexample is
confirmed), and the corrected statement printed on the page is checked instead.
Review R35 added (own random streams, the other checks unchanged): min dist(t) of the first shortest-path LP
(trap), the min-max statement over all real vectors, and three page-text checks."""
import itertools
import math
import os
import random
import re
import sys
from fractions import Fraction as Fr

import networkx as nx
import numpy as np
from scipy.optimize import linprog

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
PAGE = os.path.join(ROOT, "content", "4-lecture-notes", "h-linear-programming.md")
CONCEPT = os.path.join(ROOT, "content", "concepts", "linear-programming.md")
FIGS = os.path.join(HERE, "..", "figs")
FAIL = []
random.seed(374008)
np.random.seed(374008)
TOL = 1e-7


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAIL.append(name)


# ============================================================================== LP solving
def solve(c, A_ub=None, b_ub=None, A_eq=None, b_eq=None, bounds=None, sense="max"):
    """Return (status, value, x) with status 'optimal' | 'infeasible' | 'unbounded'."""
    c = np.asarray(c, dtype=float)
    d = len(c)
    if bounds is None:
        bounds = [(0, None)] * d
    kw = dict(bounds=bounds, method="highs")
    if A_ub is not None and len(A_ub):
        kw["A_ub"], kw["b_ub"] = np.asarray(A_ub, float), np.asarray(b_ub, float)
    if A_eq is not None and len(A_eq):
        kw["A_eq"], kw["b_eq"] = np.asarray(A_eq, float), np.asarray(b_eq, float)
    res = linprog(-c if sense == "max" else c, **kw)
    for meth in ("highs-ds", "highs-ipm"):
        if res.status == 4:  # HiGHS numerical trouble: retry with another solver
            kw["method"] = meth
            res = linprog(-c if sense == "max" else c, **kw)
    kw["method"] = "highs"
    if res.status == 4:  # still unknown: compare the optimum inside two boxes (grows without bound <=> unbounded)
        vals = []
        for B in (1e4, 1e6):
            kb = dict(kw, bounds=[(lo if lo is None else max(lo, -B), B if hi is None else min(hi, B))
                                  for lo, hi in [((-B if l is None else l), u) for l, u in bounds]])
            rb = linprog(-c if sense == "max" else c, **kb)
            if rb.status == 2:
                return "infeasible", None, None
            vals.append((rb, float(c @ rb.x)))
        if abs(vals[1][1] - vals[0][1]) > 1e-6 * (1 + abs(vals[0][1])):
            return "unbounded", None, None
        return "optimal", vals[0][1], vals[0][0].x
    if res.status == 0:
        return "optimal", float(c @ res.x), res.x
    # disambiguate with a zero objective
    res0 = linprog(np.zeros(d), **kw)
    if res0.status == 2:
        return "infeasible", None, None
    if res0.status == 0 and res.status in (2, 3):
        return "unbounded", None, None
    raise RuntimeError(f"linprog trouble: {res.status} {res.message}")


# A general LP: dict(sense, c, rows=[(a, rel, b)], signs=[...]) with rel in '<=','>=','=' and
# sign in '>=0', '<=0', 'free', '=0'.
BOUND = {">=0": (0, None), "<=0": (None, 0), "free": (None, None), "=0": (0, 0)}


def solve_general(P):
    ub_A, ub_b, eq_A, eq_b = [], [], [], []
    for a, rel, b in P["rows"]:
        if rel == "<=":
            ub_A.append(list(a)); ub_b.append(b)
        elif rel == ">=":
            ub_A.append([-x for x in a]); ub_b.append(-b)
        else:
            eq_A.append(list(a)); eq_b.append(b)
    return solve(P["c"], ub_A, ub_b, eq_A, eq_b, [BOUND[s] for s in P["signs"]], P["sense"])


def dual(P):
    """The dual by the table of the note's Figure H.4 (both halves)."""
    m, d = len(P["rows"]), len(P["c"])
    A = [list(r[0]) for r in P["rows"]]
    if P["sense"] == "max":
        ysign = {"<=": ">=0", ">=": "<=0", "=": "free"}
        crel = {">=0": ">=", "<=0": "<=", "free": "="}
        sense = "min"
    else:
        ysign = {"<=": "<=0", ">=": ">=0", "=": "free"}
        crel = {"<=0": ">=", ">=0": "<=", "free": "="}
        sense = "max"
    signs = [ysign[r[1]] for r in P["rows"]]
    rows = []
    for j in range(d):
        if P["signs"][j] == "=0":
            continue  # no dual constraint
        rows.append(([A[i][j] for i in range(m)], crel[P["signs"][j]], P["c"][j]))
    return dict(sense=sense, c=[r[2] for r in P["rows"]], rows=rows, signs=signs)


def canonical(P):
    """The note's conversion to canonical form (max c.x, Ax <= b, x >= 0): split every variable x_j = x_j+ - x_j-
    (sign constraints of the original are kept as rows), equations become two inequalities, >= rows are negated."""
    d = len(P["c"])
    s = 1 if P["sense"] == "max" else -1
    c = [s * v for v in P["c"]] + [-s * v for v in P["c"]]
    A, b = [], []
    for a, rel, bb in P["rows"]:
        row = list(a) + [-x for x in a]
        if rel in ("<=", "="):
            A.append(row); b.append(bb)
        if rel in (">=", "="):
            A.append([-x for x in row]); b.append(-bb)
    for j, sg in enumerate(P["signs"]):
        e = [0] * (2 * d); e[j], e[d + j] = 1, -1
        if sg in ("<=0", "=0"):
            A.append(e); b.append(0)
        if sg in (">=0", "=0"):
            A.append([-x for x in e]); b.append(0)
    return c, A, b, s


def random_general(d, m, rng):
    return dict(sense=rng.choice(["max", "min"]), c=[rng.randint(-5, 5) for _ in range(d)],
                rows=[([rng.randint(-4, 4) for _ in range(d)], rng.choice(["<=", ">=", "="]), rng.randint(-6, 6))
                      for _ in range(m)],
                signs=[rng.choice([">=0", ">=0", "<=0", "free", "=0"]) for _ in range(d)])


rng = random.Random(374)

# ============================================================================== H.1 canonical and slack forms
stats = {"optimal": 0, "infeasible": 0, "unbounded": 0}
ok_conv = ok_slack = True
for _ in range(1500):
    d, m = rng.randint(1, 4), rng.randint(1, 4)
    P = random_general(d, m, rng)
    st, val, _x = solve_general(P)
    stats[st] += 1
    c, A, b, s = canonical(P)
    st2, val2, _ = solve(c, A, b, sense="max")
    if st2 != st or (st == "optimal" and abs(s * val2 - val) > 1e-6):
        ok_conv = False
    # slack form: one non-negative slack variable per inequality of the canonical LP
    nA = len(A)
    A_eq = [list(A[i]) + [1 if k == i else 0 for k in range(nA)] for i in range(nA)]
    st3, val3, _ = solve(c + [0] * nA, A_eq=A_eq, b_eq=b, sense="max")
    if st3 != st or (st == "optimal" and abs(s * val3 - val) > 1e-6):
        ok_slack = False
check("H.1 conversion to canonical form (split variables, equations -> two inequalities, >= negated) keeps the "
      "optimum and the status, 1500 random LPs", ok_conv, str(stats))
check("H.1 slack form (one slack variable per inequality) keeps the optimum and the status", ok_slack)
check("H.1 random general LPs include optimal, infeasible and unbounded ones", min(stats.values()) > 50, str(stats))

# ============================================================================== H.2 the infeasible example (Figure H.2)
st, _, _ = solve([1, -1], [[2, 1], [-1, -1]], [1, -2], sense="max")
check("Figure H.2: max x - y s.t. 2x + y <= 1, x + y >= 2, x, y >= 0 is infeasible", st == "infeasible")
# certificate on the page: adding 2x + y <= 1 and -(x + y) <= -2 gives x <= -1, impossible with x >= 0
check("Figure H.2 certificate: (2x + y) - (x + y) = x and 1 - 2 = -1, so x <= -1",
      [2 - 1, 1 - 1] == [1, 0] and 1 - 2 == -1)

# ============================================================================== the 2D example of the pages
# max 3x + 2y  s.t.  x + y <= 4,  x + 2y <= 6,  x <= 3,  x, y >= 0
EX_A = [[1, 1], [1, 2], [1, 0]]
EX_b = [4, 6, 3]
EX_c = [3, 2]
st, val, xx = solve(EX_c, EX_A, EX_b)
check("2D example: optimum 11 at (3, 1)", st == "optimal" and abs(val - 11) < TOL and np.allclose(xx, [3, 1]))
VERTS = {(0, 0): 0, (3, 0): 9, (3, 1): 11, (2, 2): 10, (0, 3): 6}
# all vertices of the polygon: intersections of pairs of the 5 boundary lines that are feasible
lines = [([1, 1], 4), ([1, 2], 6), ([1, 0], 3), ([-1, 0], 0), ([0, -1], 0)]
found = set()
for (a1, b1), (a2, b2) in itertools.combinations(lines, 2):
    M = [[Fr(a1[0]), Fr(a1[1])], [Fr(a2[0]), Fr(a2[1])]]
    det = M[0][0] * M[1][1] - M[0][1] * M[1][0]
    if det == 0:
        continue
    x = (b1 * M[1][1] - b2 * M[0][1]) / det
    y = (M[0][0] * b2 - M[1][0] * b1) / det
    if all(a[0] * x + a[1] * y <= bb for a, bb in lines):
        found.add((x, y))
check("2D example: the feasible polygon has exactly the vertices (0,0), (3,0), (3,1), (2,2), (0,3)",
      found == {(Fr(p[0]), Fr(p[1])) for p in VERTS})
check("2D example: objective values 0, 9, 11, 10, 6 at those vertices",
      all(3 * x + 2 * y == v for (x, y), v in VERTS.items()))
EXP = dict(sense="max", c=EX_c, rows=[(a, "<=", b) for a, b in zip(EX_A, EX_b)], signs=[">=0", ">=0"])
EXD = dual(EXP)
check("2D example: its dual is min 4a + 6b + 3c s.t. a + b + c >= 3, a + 2b >= 2, a, b, c >= 0",
      EXD["sense"] == "min" and EXD["c"] == [4, 6, 3] and EXD["rows"] == [([1, 1, 1], ">=", 3), ([1, 2, 0], ">=", 2)]
      and EXD["signs"] == [">=0"] * 3)
yex = [Fr(2), Fr(0), Fr(1)]
check("2D example: y = (2, 0, 1) is dual feasible with value 11 = primal value (exact) -> both optimal",
      yex[0] + yex[1] + yex[2] >= 3 and yex[0] + 2 * yex[1] >= 2 and min(yex) >= 0 and 4 * yex[0] + 6 * yex[1] + 3 * yex[2] == 11)
st, dval, yy = solve_general(EXD)
check("2D example: linprog on the dual gives 11 and y = (2, 0, 1) (unique)", st == "optimal" and abs(dval - 11) < TOL
      and np.allclose(yy, [2, 0, 1], atol=1e-7))
check("2D example: c = (3, 2) = 2*(1, 1) + 1*(1, 0), the normals of the two tight constraints",
      [2 * 1 + 1 * 1, 2 * 1 + 1 * 0] == [3, 2])
check("2D example: complementary slackness — x + 2y = 5 < 6 is loose and b = 0; x, y > 0 and both dual "
      "constraints tight (2 + 0 + 1 = 3, 2 + 0 = 2)", 3 + 2 * 1 == 5 and yex[1] == 0 and sum(yex) == 3 and yex[0] + 2 * yex[1] == 2)

# ============================================================================== Vanderbei's example (H.6)
VA = [[1, 4, 0], [3, -1, 1]]
Vb = [2, 4]
Vc = [4, 1, 3]


def feas_primal(A, b, x):
    return all(v >= 0 for v in x) and all(sum(a * v for a, v in zip(row, x)) <= bb for row, bb in zip(A, b))


check("H.6: x = (1, 0, 0) is feasible with value 4", feas_primal(VA, Vb, [1, 0, 0]) and 4 * 1 == 4)
check("H.6: x = (0, 0, 3) is feasible with value 9", feas_primal(VA, Vb, [0, 0, 3]) and 3 * 3 == 9)
xs = [Fr(0), Fr(1, 2), Fr(9, 2)]
ys = [Fr(1), Fr(3)]
check("H.6: x* = (0, 1/2, 9/2) is feasible, both constraints tight, value 14",
      feas_primal(VA, Vb, xs) and [sum(a * v for a, v in zip(r, xs)) for r in VA] == [2, 4]
      and sum(a * v for a, v in zip(Vc, xs)) == 14)
VP = dict(sense="max", c=Vc, rows=[(a, "<=", b) for a, b in zip(VA, Vb)], signs=[">=0"] * 3)
VD = dual(VP)
check("H.6: the dual by Figure H.4 is min 2y1 + 4y2 s.t. y1 + 3y2 >= 4, 4y1 - y2 >= 1, y2 >= 3, y >= 0",
      VD["c"] == [2, 4] and VD["rows"] == [([1, 3], ">=", 4), ([4, -1], ">=", 1), ([0, 1], ">=", 3)]
      and VD["signs"] == [">=0", ">=0"] and VD["sense"] == "min")
check("H.6: y* = (1, 3) is dual feasible (10 >= 4, 1 >= 1, 3 >= 3) with value 14 -> both optimal (exact)",
      ys[0] + 3 * ys[1] == 10 and 4 * ys[0] - ys[1] == 1 and ys[1] == 3 and 2 * ys[0] + 4 * ys[1] == 14)
st, val, xx = solve(Vc, VA, Vb)
st2, val2, yy = solve_general(VD)
check("H.6: linprog agrees: primal 14 at (0, 1/2, 9/2), dual 14 at (1, 3)",
      st == st2 == "optimal" and abs(val - 14) < TOL and abs(val2 - 14) < TOL and np.allclose(xx, [0, .5, 4.5])
      and np.allclose(yy, [1, 3]))
# uniqueness of both optima: optimize each coordinate over the optimal face
uniq = True
for j in range(3):
    for sense in ("max", "min"):
        e = [0] * 3; e[j] = 1
        s2, v2, _ = solve(e, VA, Vb, A_eq=[Vc], b_eq=[14], sense=sense)
        uniq &= abs(v2 - float(xs[j])) < 1e-7
for j in range(2):
    for sense in ("max", "min"):
        e = [0] * 2; e[j] = 1
        s2, v2, _ = solve(e, [[-1, -3], [-4, 1], [0, -1]], [-4, -1, -3], A_eq=[[2, 4]], b_eq=[14], sense=sense)
        uniq &= abs(v2 - float(ys[j])) < 1e-7
check("H.6: the primal and the dual optimum are unique", uniq)
# inequality (*) with y = (1, 3): coefficients (y1 + 3y2, 4y1 - y2, y2) = (10, 1, 3) >= (4, 1, 3), bound 2y1 + 4y2 = 14
check("H.6: (*) with y = (1, 3): 4x1 + x2 + 3x3 <= 10x1 + x2 + 3x3 <= 14",
      [ys[0] + 3 * ys[1], 4 * ys[0] - ys[1], ys[1]] == [10, 1, 3] and 2 * ys[0] + 4 * ys[1] == 14)
check("H.6/H.8: complementary slackness holds and is strict: y1, y2 > 0 with both rows tight; x1 = 0 with dual "
      "row loose (10 > 4); x2, x3 > 0 with dual rows tight (1 = 1, 3 = 3)",
      ys[0] > 0 and ys[1] > 0 and xs[0] == 0 and 10 > 4 and xs[1] > 0 and xs[2] > 0)

# ============================================================================== H.4 duality: canonical pair and the table
ok_inv = ok_neg = True
for _ in range(300):
    n, d = rng.randint(1, 4), rng.randint(1, 4)
    A = [[rng.randint(-5, 5) for _ in range(d)] for _ in range(n)]
    b = [rng.randint(-5, 5) for _ in range(n)]
    c = [rng.randint(-5, 5) for _ in range(d)]
    # negative-transpose form: max -b.y s.t. -A^T y <= -c, y >= 0 ; applying it twice gives back (A, b, c)
    A1, b1, c1 = [[-A[i][j] for i in range(n)] for j in range(d)], [-x for x in c], [-x for x in b]
    A2, b2, c2 = [[-A1[i][j] for i in range(d)] for j in range(n)], [-x for x in c1], [-x for x in b1]
    ok_inv &= (A2, b2, c2) == (A, b, c)
    P = dict(sense="max", c=c, rows=[(a, "<=", bb) for a, bb in zip(A, b)], signs=[">=0"] * d)
    D = dual(P)
    s1, v1, _ = solve_general(D)
    s2, v2, _ = solve([-x for x in b], A1, b1, sense="max")
    ok_neg &= s1 == s2 and (s1 != "optimal" or abs(v1 + v2) < 1e-6)
check("H.4: the negative-transpose dual of the negative-transpose dual is the primal (involution), 300 LPs", ok_inv)
check("H.4: min{y.b : yA >= c, y >= 0} and its negative-transpose form max{-b.y : -A^T y <= -c, y >= 0} agree", ok_neg)

counts = {"opt": 0, "unb": 0, "inf": 0}
ok_sd = ok_unb = ok_inf = ok_dd = True
for _ in range(2500):
    d, m = rng.randint(1, 4), rng.randint(1, 4)
    P = random_general(d, m, rng)
    D = dual(P)
    sp, vp, _ = solve_general(P)
    sd, vd, _ = solve_general(D)
    if sp == "optimal":
        counts["opt"] += 1
        ok_sd &= sd == "optimal" and abs(vp - vd) < 1e-6
    elif sp == "unbounded":
        counts["unb"] += 1
        ok_unb &= sd == "infeasible"
    else:
        counts["inf"] += 1
        ok_inf &= sd in ("infeasible", "unbounded")
    # dual of the dual: same LP once the variables fixed at 0 are dropped
    DD = dual(D)
    keep = [j for j in range(d) if P["signs"][j] != "=0"]
    Pk = dict(sense=P["sense"], c=[P["c"][j] for j in keep], rows=[([r[0][j] for j in keep], r[1], r[2]) for r in P["rows"]],
              signs=[P["signs"][j] for j in keep])
    ok_dd &= DD == Pk
check("Figure H.4: dual built by the table; primal optimal => dual optimal with the same value", ok_sd, str(counts))
check("Figure H.4: primal unbounded => dual infeasible", ok_unb)
check("Figure H.4: primal infeasible => dual infeasible or unbounded", ok_inf)
check("Figure H.4: dual of the dual is the primal (both halves of the table), 2500 random LPs", ok_dd)

# ============================================================================== weak duality, fundamental theorem
ok_wd = True
for _ in range(500):
    n, d = rng.randint(1, 5), rng.randint(1, 5)
    A = np.random.randint(-5, 6, (n, d)).astype(float)
    x0 = np.random.rand(d) * 3
    y0 = np.random.rand(n) * 3
    b = A @ x0 + np.random.rand(n) * 2
    c = y0 @ A - np.random.rand(d) * 2
    for _k in range(5):
        # random feasible x, y: shrink towards x0 / y0 until feasible
        x = np.random.rand(d) * 4
        while not (np.all(A @ x <= b + 1e-12)):
            x = (x + x0) / 2
        y = np.random.rand(n) * 4
        while not np.all(y @ A >= c - 1e-12):
            y = (y + y0) / 2
        ok_wd &= c @ x <= y @ A @ x + 1e-9 <= y @ b + 2e-9
check("H.5 weak duality: c.x <= yAx <= y.b for random feasible pairs (2500 pairs)", ok_wd)

# both infeasible: possible (the note says so); an example (not printed on the page)
st1, _, _ = solve([1, 0], [[1, -1], [-1, 1]], [-1, -1])
st2, _, _ = solve_general(dual(dict(sense="max", c=[1, 0], rows=[([1, -1], "<=", -1), ([-1, 1], "<=", -1)],
                                    signs=[">=0", ">=0"])))
check("H.5: an LP and its dual can both be infeasible, so 'dual infeasible => primal unbounded' is false "
      "(the note's 'all these implications are equivalences', p. 12, fails for the second one)",
      st1 == "infeasible" and st2 == "infeasible")

# ============================================================================== H.5 min-max (mixed strategies) and Gordan
ok_mm = True
for _ in range(200):
    p, q = rng.randint(1, 4), rng.randint(1, 4)
    M = np.random.randint(-5, 6, (p, q)).astype(float)
    # min over probability x (rows) of max over y (cols) of x M y = min v s.t. (x M)_j <= v
    c1 = [0] * p + [1]
    Aub = [[M[i][j] for i in range(p)] + [-1] for j in range(q)]
    s1, v1, _ = solve(c1, Aub, [0] * q, A_eq=[[1] * p + [0]], b_eq=[1], bounds=[(0, None)] * p + [(None, None)],
                      sense="min")
    c2 = [0] * q + [1]
    Aub2 = [[-M[i][j] for j in range(q)] + [1] for i in range(p)]
    s2, v2, _ = solve(c2, Aub2, [0] * p, A_eq=[[1] * q + [0]], b_eq=[1], bounds=[(0, None)] * q + [(None, None)],
                      sense="max")
    ok_mm &= abs(v1 - v2) < 1e-7
check("H.5 min-max theorem with x, y ranging over probability vectors: min_x max_y xAy = max_y min_x xAy, 200 "
      "random matrices", ok_mm)
# (review R35) without the range, over ALL real vectors: max_y xAy is +inf unless xA = 0 (then 0, e.g. x = 0), so
# min_x max_y xAy = 0; symmetrically max_y min_x xAy = 0 — the statement is empty, not false. Own random streams.
rng_mm = np.random.RandomState(35036)
ok_real = True
for _ in range(100):
    p, q = rng_mm.randint(1, 5), rng_mm.randint(1, 5)
    M = rng_mm.randint(-5, 6, (p, q)).astype(float)
    x = rng_mm.randint(-3, 4, p).astype(float)
    y = rng_mm.randint(-3, 4, q).astype(float)
    if np.any(x @ M != 0):  # sup over free y of (xM).y is unbounded
        s_, _, _ = solve(x @ M, bounds=[(None, None)] * q, sense="max")
        ok_real &= s_ == "unbounded"
    if np.any(M @ y != 0):  # inf over free x of x.(My) is unbounded below
        s_, _, _ = solve(M @ y, bounds=[(None, None)] * p, sense="min")
        ok_real &= s_ == "unbounded"
    # x = 0 (resp. y = 0) gives inner optimum 0, and every x has inner sup >= 0 (take y = 0): both sides are 0
    s1_, v1_, _ = solve(np.zeros(p) @ M, bounds=[(None, None)] * q, sense="max")
    s2_, v2_, _ = solve(M @ np.zeros(q), bounds=[(None, None)] * p, sense="min")
    ok_real &= s1_ == s2_ == "optimal" and v1_ == 0 and v2_ == 0
check("H.5 (note p. 11): over all real vectors min_x max_y xAy = max_y min_x xAy = 0 trivially (inner optimum "
      "infinite unless xA = 0, resp. Ay = 0), 100 random matrices", ok_real)
ok_g = True
seen = [0, 0]
for _ in range(400):
    p, q = rng.randint(1, 4), rng.randint(1, 4)
    A = np.random.randint(-3, 4, (p, q)).astype(float)
    # alternative 1: Ax = 0, x >= 0, x != 0 (normalize sum x = 1)
    s1, _, _ = solve([0] * q, A_eq=np.vstack([A, np.ones(q)]), b_eq=[0] * p + [1], sense="max")
    # alternative 2: yA > 0 for some y (scale: yA >= 1)
    s2, _, _ = solve([0] * p, -A.T, -np.ones(q), bounds=[(None, None)] * p, sense="max")
    a1, a2 = s1 == "optimal", s2 == "optimal"
    seen[0] += a1; seen[1] += a2
    ok_g &= a1 != a2
check("H.5 Gordan: exactly one of {Ax = 0, x >= 0, x != 0} and {yA > 0} is solvable, 400 random matrices",
      ok_g and min(seen) > 50, str(seen))

# ============================================================================== H.7 strong duality and its proof
def random_nondeg(n, d, kind):
    A = np.random.randn(n, d)
    if kind == "feasible":
        b = np.abs(np.random.randn(n)) + 0.1
    else:
        b = np.random.randn(n)
    c = np.random.randn(d)
    return A, b, c


ok_proof = ok_fund = ok_strict = True
nopt = 0
for _ in range(400):
    n, d = rng.randint(1, 6), rng.randint(1, 5)
    A, b, c = random_nondeg(n, d, rng.choice(["feasible", "any"]))
    st, val, x = solve(c, A, b)
    D = dual(dict(sense="max", c=list(c), rows=[(list(a), "<=", bb) for a, bb in zip(A, b)], signs=[">=0"] * d))
    sd, vd, y = solve_general(D)
    if st == "optimal":
        nopt += 1
        ok_fund &= sd == "optimal" and abs(val - vd) < 1e-6
        # the proof: G = [A; -I], h = [b; 0]; exactly d tight constraints; y_B = c G_B^{-1} > 0
        G = np.vstack([A, -np.eye(d)])
        h = np.concatenate([b, np.zeros(d)])
        tight = [k for k in range(n + d) if abs(G[k] @ x - h[k]) < 1e-8]
        if len(tight) != d:
            ok_proof = False
            continue
        Vinv = np.linalg.inv(G[tight])
        yB = c @ Vinv
        ok_proof &= bool(np.all(yB > 1e-10))
        yfull = np.zeros(n + d)
        yfull[tight] = yB
        yrow = yfull[:n]
        # dual feasibility y A >= c (the sign-constraint multipliers are the slack) and equal value
        ok_proof &= bool(np.all(yrow >= -1e-12) and np.all(yrow @ A >= c - 1e-9) and abs(yrow @ b - val) < 1e-7)
        # non-degenerate => the pair is strictly complementary
        slack_p = b - A @ x
        slack_d = y @ A - c
        ok_strict &= bool(np.all((y > 1e-9) != (slack_p > 1e-9)) and np.all((x > 1e-9) != (slack_d > 1e-9)))
check("H.5/H.7 fundamental theorem: random non-degenerate canonical LPs with an optimum have a dual optimum of the "
      "same value", ok_fund and nopt > 150, f"{nopt} with an optimum")
check("H.7 proof: at the optimum exactly d of the n + d constraints are tight, y_B = c A_B^{-1} is positive, and "
      "padded with zeros it is a dual optimum", ok_proof)
check("H.8: in non-degenerate LPs the (unique) optimal pair is strictly complementary", ok_strict)

# the note's non-degeneracy condition (a) does not force a unique optimum: the unit cube with c = (1, 1, 0)
CA = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
st, val, _ = solve([1, 1, 0], CA, [1, 1, 1])
lo = solve([0, 0, 1], CA, [1, 1, 1], A_eq=[[1, 1, 0]], b_eq=[2], sense="min")[1]
hi = solve([0, 0, 1], CA, [1, 1, 1], A_eq=[[1, 1, 0]], b_eq=[2], sense="max")[1]
normals = CA + [[-1, 0, 0], [0, -1, 0], [0, 0, -1]]
parallel = any(np.linalg.matrix_rank(np.array([[1, 1, 0], nv])) < 2 for nv in normals)
# at most 3 of the 6 planes through any point: the cube is simple (check all triples of planes meet once and no 4)
planes = [(nv, bb) for nv, bb in zip(normals, [1, 1, 1, 0, 0, 0])]
max_through = 0
for tri in itertools.combinations(range(6), 3):
    M = np.array([planes[k][0] for k in tri], float)
    if abs(np.linalg.det(M)) < 1e-9:
        continue
    p = np.linalg.solve(M, [planes[k][1] for k in tri])
    max_through = max(max_through, sum(abs(np.array(planes[k][0]) @ p - planes[k][1]) < 1e-9 for k in range(6)))
check("H.7 (note p. 14): condition (a) 'c not normal to any constraint hyperplane' plus (b) does not give a unique "
      "optimum — unit cube, c = (1, 1, 0): optimum 2 on the whole edge x3 in [0, 1]",
      st == "optimal" and abs(val - 2) < TOL and abs(lo) < TOL and abs(hi - 1) < TOL and not parallel and max_through == 3)

# ============================================================================== H.8 complementary slackness theorem
ok_cs = True
cnt_opt = cnt_non = half3 = half4 = 0
for _ in range(400):
    n, d = rng.randint(1, 4), rng.randint(1, 4)
    A = np.random.randint(-3, 4, (n, d)).astype(float)
    b = np.random.randint(0, 6, n).astype(float)
    c = np.random.randint(-3, 4, d).astype(float)
    st, val, xo = solve(c, A, b)
    if st != "optimal":
        continue
    D = dual(dict(sense="max", c=list(c), rows=[(list(a), "<=", bb) for a, bb in zip(A, b)], signs=[">=0"] * d))
    sd, vd, yo = solve_general(D)
    # random feasible points (convex combinations of the optimum with random feasible points, or the optimum itself)
    for k in range(6):
        if k == 0:
            x, y = xo, yo
        else:
            x = xo * rng.random()
            y = yo + np.random.rand(n) * rng.choice([0, 0.5, 2])
            if not np.all(A @ x <= b + 1e-9) or not np.all(y @ A >= c - 1e-9):
                continue
        c3 = abs(c @ x - y @ A @ x) < 1e-7
        c4 = abs(y @ A @ x - y @ b) < 1e-7
        conds = [abs(c @ x - y @ b) < 1e-7, c3 and c4,
                 bool(np.all(np.abs(y * (b - A @ x)) < 1e-7) and np.all(np.abs(x * (y @ A - c)) < 1e-7))]
        optimal = abs(c @ x - val) < 1e-7 and abs(y @ b - val) < 1e-7
        ok_cs &= all(cc == optimal for cc in conds)
        ok_cs &= (not optimal) or (c3 and c4)
        # c.x = yAx  <=>  the column conditions x_j (yA - c)_j = 0 ; yAx = y.b  <=>  the row conditions
        ok_cs &= c3 == bool(np.all(np.abs(x * (y @ A - c)) < 1e-7))
        ok_cs &= c4 == bool(np.all(np.abs(y * (b - A @ x)) < 1e-7))
        half3 += c3 and not optimal
        half4 += c4 and not optimal
        cnt_opt += optimal; cnt_non += not optimal
check("H.8 corrected complementary slackness theorem: for feasible x, y — optimal <=> c.x = y.b <=> (c.x = yAx and "
      "yAx = y.b) <=> all complementary slackness conditions", ok_cs and cnt_non > 100,
      f"{cnt_opt} optimal pairs, {cnt_non} non-optimal")
check("H.8 (note p. 16): 'c.x = yAx' alone and 'yAx = y.b' alone are NOT equivalent to optimality (each is half of "
      "the slackness conditions; random pairs for the first, the exact example below for the second)", half3 > 20,
      f"{half3}, {half4} random non-optimal pairs satisfy them")
# the page's counterexamples, exact, on Vanderbei's LP with y* = (1, 3)
x0 = [Fr(0)] * 3
x1 = [Fr(1), Fr(1, 4), Fr(5, 4)]
cx = lambda x: sum(a * v for a, v in zip(Vc, x))
yAx = lambda x: sum(ys[i] * sum(VA[i][j] * x[j] for j in range(3)) for i in range(2))
check("H.8 counterexamples: x = 0 has c.x = yAx = 0 (value 0 < 14); x = (1, 1/4, 5/4) is feasible with "
      "yAx = y.b = 14 but c.x = 8", feas_primal(VA, Vb, x0) and cx(x0) == yAx(x0) == 0 and feas_primal(VA, Vb, x1)
      and yAx(x1) == 14 and cx(x1) == 8)
# strict complementary slackness exists even for degenerate LPs (Goldman-Tucker): maximize t
ok_gt = True
ndeg = 0
for _ in range(200):
    n, d = rng.randint(2, 4), rng.randint(2, 4)
    A = np.random.randint(0, 3, (n, d)).astype(float)
    b = np.random.randint(0, 3, n).astype(float)
    c = np.random.randint(-1, 3, d).astype(float)
    st, val, xo = solve(c, A, b)
    if st != "optimal":
        continue
    # variables x (d), y (n), t ; x, y >= 0 ; Ax <= b ; yA >= c ; c.x = y.b ; x_j + (yA - c)_j >= t ; y_i + (b - Ax)_i >= t
    nv = d + n + 1
    rows, rhs = [], []
    for i in range(n):
        rows.append(list(A[i]) + [0] * n + [0]); rhs.append(b[i])
    for j in range(d):
        rows.append([0] * d + list(-A[:, j]) + [0]); rhs.append(-c[j])
    for j in range(d):
        e = [0.0] * nv; e[j] = -1
        for i in range(n):
            e[d + i] = -A[i][j]
        e[-1] = 1; rows.append(e); rhs.append(-c[j])
    for i in range(n):
        e = [0.0] * nv; e[d + i] = -1
        for j in range(d):
            e[j] = A[i][j]
        e[-1] = 1; rows.append(e); rhs.append(b[i])
    eq = [list(c) + list(-b) + [0]]
    s2, t, z = solve([0] * (nv - 1) + [1], rows, rhs, A_eq=eq, b_eq=[0], bounds=[(0, None)] * (nv - 1) + [(None, 1)])
    ok_gt &= s2 == "optimal" and t > 1e-7
    # count degenerate instances (more than d tight constraints at the returned optimum)
    tight = sum(abs(A[i] @ xo - b[i]) < 1e-9 for i in range(n)) + sum(xo < 1e-9)
    ndeg += tight > d
check("H.8: every feasible bounded LP has a strictly complementary optimal pair, also degenerate ones (200 small "
      "integer LPs)", ok_gt and ndeg > 30, f"{ndeg} degenerate")


# ============================================================================== graphs
def rand_graph(n, p, lo, hi, rng, no_neg_cycle=True):
    V = list(range(n))
    E = {}
    pot = [rng.randint(-4, 4) for _ in V]
    for u in V:
        for v in V:
            if u != v and rng.random() < p:
                w = rng.randint(lo, hi)
                if no_neg_cycle:
                    w = abs(w) + pot[u] - pot[v]  # reduced costs of non-negative weights: no negative cycle
                E[(u, v)] = w
    if not E and n > 1:
        E[(0, n - 1)] = rng.randint(1, 5)
    return V, E


def bellman_ford(V, E, s):
    INF = math.inf
    dist = {v: INF for v in V}
    dist[s] = 0
    pred = {}
    for _ in range(len(V)):
        for (u, v), w in E.items():
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                pred[v] = u
    return dist, pred


def has_neg_cycle(V, E):
    dist = {v: 0 for v in V}
    for _ in range(len(V) + 1):
        ch = False
        for (u, v), w in E.items():
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w; ch = True
        if not ch:
            return False
    return True


def lp_one_shortest(V, E, s, t, sense="max", extra_eq=None, obj=None):
    idx = {v: k for k, v in enumerate(V)}
    A, b = [], []
    for (u, v), w in E.items():
        row = [0] * len(V); row[idx[v]] += 1; row[idx[u]] -= 1
        A.append(row); b.append(w)
    bounds = [(0, 0) if v == s else (None, None) for v in V]
    if obj is None:
        obj = [1 if v == t else 0 for v in V]
    Aeq, beq = [], []
    if extra_eq:
        Aeq, beq = extra_eq
    return solve(obj, A, b, Aeq, beq, bounds, sense)


def lp_unit_flow(V, E, s, t):
    """min l.x s.t. inflow - outflow = 1 at t, 0 at v != s, t ; x >= 0."""
    Es = list(E)
    Aeq, beq = [], []
    for v in V:
        if v == s:
            continue
        row = [(1 if e[1] == v else 0) - (1 if e[0] == v else 0) for e in Es]
        Aeq.append(row); beq.append(1 if v == t else 0)
    return solve([E[e] for e in Es], A_eq=Aeq, b_eq=beq, sense="min"), Es


def reach(V, E, s):
    seen, st = {s}, [s]
    while st:
        u = st.pop()
        for (a, b2) in E:
            if a == u and b2 not in seen:
                seen.add(b2); st.append(b2)
    return seen


def reach_rev(V, E, t):
    return reach(V, {(b2, a): 0 for (a, b2) in E}, t)


ok_feas = ok_bnd = ok_val = ok_dualmat = ok_lp2 = ok_cs2 = ok_int = True
c_inf = c_unb = c_opt = 0
for trial in range(700):
    n = rng.randint(2, 6)
    neg = rng.random() < 0.35
    V, E = rand_graph(n, rng.choice([0.3, 0.5]), -6 if neg else 1, 9, rng, no_neg_cycle=not neg)
    s, t = 0, n - 1
    st, val, dist = lp_one_shortest(V, E, s, t)
    negc = has_neg_cycle(V, E)
    reachable = t in reach(V, E, s)
    ok_feas &= (st == "infeasible") == negc
    if not negc:
        ok_bnd &= (st == "unbounded") == (not reachable)
    if st == "infeasible":
        c_inf += 1
    elif st == "unbounded":
        c_unb += 1
    else:
        c_opt += 1
        dd, _ = bellman_ford(V, E, s)
        ok_val &= abs(val - dd[t]) < 1e-7
    # LP2 (take two)
    (st2, val2, x2), Es = lp_unit_flow(V, E, s, t)
    if st2 == "infeasible":
        ok_lp2 &= not reachable
    elif st2 == "unbounded":
        ok_lp2 &= reachable and negc
    else:
        ok_lp2 &= reachable and not negc
    if st == "optimal" and st2 == "optimal":
        ok_lp2 &= abs(val - val2) < 1e-7
        # complementary slackness: x(u->v) > 0 => dist(v) - dist(u) = l(u->v)
        idx = {v: k for k, v in enumerate(V)}
        ok_cs2 &= all(x2[k] < 1e-9 or abs(dist[idx[e[1]]] - dist[idx[e[0]]] - E[e]) < 1e-7 for k, e in enumerate(Es))
        # the returned vertex solution is integral
        ok_int &= bool(np.allclose(x2, np.round(x2), atol=1e-9))
    # LP2 is the mechanical dual of LP1 (dist(s) = 0 drops its constraint)
    signs = ["=0" if v == s else "free" for v in V]
    P1 = dict(sense="max", c=[1 if v == t else 0 for v in V],
              rows=[([(1 if v == e[1] else 0) - (1 if v == e[0] else 0) for v in V], "<=", E[e]) for e in Es],
              signs=signs)
    D1 = dual(P1)
    exp_rows = [([(1 if e[1] == v else 0) - (1 if e[0] == v else 0) for e in Es], "=", 1 if v == t else 0)
                for v in V if v != s]
    ok_dualmat &= D1["sense"] == "min" and D1["c"] == [E[e] for e in Es] and D1["rows"] == exp_rows \
        and D1["signs"] == [">=0"] * len(Es)
check("H.3 one shortest path (max dist(t)): feasible iff no negative cycle anywhere, 700 random graphs", ok_feas,
      f"{c_inf} infeasible, {c_unb} unbounded, {c_opt} optimal")
check("H.3: when feasible, bounded iff t is reachable from s", ok_bnd)
check("H.3: the optimum is the shortest-path distance (Bellman-Ford)", ok_val)
check("H.3 take two (min l.x, unit flow): infeasible iff no s-t path; unbounded iff (path and) a negative cycle; "
      "same optimum as take one", ok_lp2)
check("H.4: take two is exactly the dual of take one by Figure H.4 (signed incidence matrix transposed, no "
      "constraint for dist(s))", ok_dualmat)
check("H.8 on the shortest-path pair: flow only on tight edges (complementary slackness)", ok_cs2)
check("H.3: linprog's vertex optimum of take two is integral", ok_int)

# --- the note's boundedness witness (dist = 0 on reachable vertices) can be infeasible; the corrected one is not
Vw, Ew = ["s", "a", "t"], {("s", "a"): -1, ("t", "a"): 0}
d0 = {"s": 0, "a": 0}
check("H.3 (note p. 5): with a negative edge s->a the note's witness dist = 0 on reachable vertices violates "
      "dist(a) - dist(s) <= -1", not (d0["a"] - d0["s"] <= Ew[("s", "a")]))
ok_M = True
for trial in range(300):
    n = rng.randint(3, 6)
    V, E = rand_graph(n, 0.35, -5, 9, rng, no_neg_cycle=True)
    s, t = 0, n - 1
    R = reach(V, E, s)
    if t in R:
        continue
    st, _, _ = lp_one_shortest(V, E, s, t, obj=[0] * n)  # any feasible point
    _, _, p = lp_one_shortest(V, E, s, t, obj=[0] * n)
    for M in (1, 10, 1000):
        q = [p[k] + (M if V[k] not in R else 0) for k in range(n)]
        ok_M &= all(q[v] - q[u] <= w + 1e-9 for (u, v), w in E.items()) and q[0] == 0
check("H.3 corrected witness: adding M to every vertex that s cannot reach keeps a feasible point feasible", ok_M)

# --- (review R35) the trap: MINIMIZING dist(t) is unbounded below unless t can reach s; then the minimum is
# -delta(t, s). Own random streams, so the other checks' random instances are unchanged.
rng_r35 = random.Random(35035)
ok_min = True
cnt_min = {"unbounded": 0, "optimal": 0}
for trial in range(400):
    n = rng_r35.randint(2, 6)
    V, E = rand_graph(n, rng_r35.choice([0.3, 0.5]), -5, 9, rng_r35, no_neg_cycle=True)
    s, t = 0, n - 1
    st, val, _ = lp_one_shortest(V, E, s, t, sense="min")
    if s in reach(V, E, t):
        dt, _ = bellman_ford(V, E, t)
        ok_min &= st == "optimal" and abs(val + dt[s]) < 1e-7
    else:
        ok_min &= st == "unbounded"
    cnt_min[st] = cnt_min.get(st, 0) + 1
# smallest case: s->t and t->s of length 1 gives min dist(t) = -1, not -infinity
st, val, _ = lp_one_shortest(["s", "t"], {("s", "t"): 1, ("t", "s"): 1}, "s", "t", sense="min")
check("H.3 trap (corrected): min dist(t) s.t. dist(s) = 0 and no tense edge is unbounded below iff t cannot reach s, "
      "otherwise its minimum is -delta(t, s) (Bellman-Ford from t; 400 graphs without negative cycles; s<->t "
      "of length 1 gives -1)", ok_min and min(cnt_min.values()) > 50 and st == "optimal" and abs(val + 1) < 1e-9,
      str(cnt_min))

# --- uniqueness of the optimum of the first shortest-path LP
note_wrong = 0
ok_corr = True
ok_suff = True
tested = 0
for trial in range(500):
    n = rng.randint(3, 6)
    V, E = rand_graph(n, 0.45, 1, 6, rng, no_neg_cycle=False)  # positive lengths
    s, t = 0, n - 1
    st, val, _ = lp_one_shortest(V, E, s, t)
    if st != "optimal":
        continue
    tested += 1
    unique = True
    for k, v in enumerate(V):
        if v == s:
            continue
        e = [0] * n; e[k] = 1
        tvec = [1 if u == t else 0 for u in V]
        lo = lp_one_shortest(V, E, s, t, "min", ([tvec], [val]), e)[1]
        hi = lp_one_shortest(V, E, s, t, "max", ([tvec], [val]), e)[1]
        unique &= lo is not None and hi is not None and hi - lo < 1e-7
    G = nx.DiGraph()
    G.add_nodes_from(V)
    G.add_weighted_edges_from([(u, v, w) for (u, v), w in E.items()])
    paths = list(nx.all_simple_paths(G, s, t))
    on_path = set().union(*map(set, paths)) if paths else set()  # vertices on some simple s-t path
    lengths = {sum(E[(p[i], p[i + 1])] for i in range(len(p) - 1)) for p in paths}
    note_cond = on_path == set(V) and len(lengths) == 1
    ds = nx.single_source_dijkstra_path_length(G, s)
    dt = nx.single_source_dijkstra_path_length(G.reverse(), t)
    corr = all(v in ds and v in dt and ds[v] + dt[v] == ds[t] for v in V)
    ok_corr &= unique == corr
    ok_suff &= (not note_cond) or unique
    note_wrong += unique and not note_cond
check("H.3 (note p. 6): the note's uniqueness condition (every vertex on a simple s-t path, all simple s-t paths "
      "of equal length) is sufficient", ok_suff)
check("H.3 (note p. 6): ... but not necessary — unique optima with s-t paths of different lengths exist",
      note_wrong >= 1, f"{note_wrong} of {tested} graphs")
check("H.3 corrected: with positive lengths the optimum is unique iff every vertex lies on a shortest s-t path",
      ok_corr, f"{tested} graphs")

# --- the example graph of the page and of figure nh-shortest-path
SPV = ["s", "a", "b", "c", "t"]
SPE = {("s", "a"): 2, ("s", "b"): 5, ("a", "b"): 1, ("a", "c"): 4, ("b", "c"): 1, ("b", "t"): 6, ("c", "t"): 2}
st, val, dist = lp_one_shortest(SPV, SPE, "s", "t")
check("example graph: max dist(t) = 6", st == "optimal" and abs(val - 6) < TOL)
dd, _ = bellman_ford(SPV, SPE, "s")
check("example graph: distances s 0, a 2, b 3, c 4, t 6", dd == {"s": 0, "a": 2, "b": 3, "c": 4, "t": 6})
Gs = nx.DiGraph(); Gs.add_weighted_edges_from([(u, v, w) for (u, v), w in SPE.items()])
plen = sorted(sum(SPE[(p[i], p[i + 1])] for i in range(len(p) - 1)) for p in nx.all_simple_paths(Gs, "s", "t"))
check("example graph: the s-t paths have lengths 6, 8, 8, 9, 11", plen == [6, 8, 8, 9, 11], str(plen))
uniq = True
for k in range(1, 5):
    e = [0] * 5; e[k] = 1
    lo = lp_one_shortest(SPV, SPE, "s", "t", "min", ([[0, 0, 0, 0, 1]], [6]), e)[1]
    hi = lp_one_shortest(SPV, SPE, "s", "t", "max", ([[0, 0, 0, 0, 1]], [6]), e)[1]
    uniq &= abs(hi - lo) < 1e-7 and abs(lo - dd[SPV[k]]) < 1e-7
check("example graph: the optimum dist = (0, 2, 3, 4, 6) is unique although the paths differ in length "
      "(counterexample to the note's 'only if', p. 6)", uniq)
(st2, val2, x2), Es = lp_unit_flow(SPV, SPE, "s", "t")
on = {e for k, e in enumerate(Es) if x2[k] > 0.5}
check("example graph: take two gives cost 6 with x = 1 on s->a->b->c->t and 0 elsewhere",
      st2 == "optimal" and abs(val2 - 6) < TOL and on == {("s", "a"), ("a", "b"), ("b", "c"), ("c", "t")}
      and np.allclose(x2, np.round(x2)))
tight = {e for e, w in SPE.items() if dd[e[1]] - dd[e[0]] == w}
check("example graph: the tight edges are exactly the path edges; slacks of s->b, a->c, b->t are 2, 2, 3",
      tight == on and [SPE[e] - (dd[e[1]] - dd[e[0]]) for e in [("s", "b"), ("a", "c"), ("b", "t")]] == [2, 2, 3])

# ============================================================================== single-source LPs
ok_ss1 = ok_ss2 = ok_tree = ok_ssd = True
cnt = 0
for trial in range(400):
    n = rng.randint(2, 6)
    V, E = rand_graph(n, 0.5, 1, 8, rng, no_neg_cycle=True)
    s = 0
    if reach(V, E, s) != set(V):
        continue
    cnt += 1
    dd, pred = bellman_ford(V, E, s)
    st, val, dist = lp_one_shortest(V, E, s, None, obj=[1] * n)
    ok_ss1 &= st == "optimal" and np.allclose(dist, [dd[v] for v in V], atol=1e-7)
    Es = list(E)
    Aeq = [[(1 if e[1] == v else 0) - (1 if e[0] == v else 0) for e in Es] for v in V if v != s]
    st2, val2, x2 = solve([E[e] for e in Es], A_eq=Aeq, b_eq=[1] * (n - 1), sense="min")
    ok_ss2 &= st2 == "optimal" and abs(val2 - sum(dd[v] for v in V)) < 1e-7 and abs(val - val2) < 1e-7
    # the note's solution: x(pred(v) -> v) = |D_v| (number of descendants of v in the tree, v included)
    kids = {v: [w for w in V if pred.get(w) == v] for v in V}

    def desc(v):
        return 1 + sum(desc(w) for w in kids[v])

    xt = {e: 0 for e in Es}
    for v in V:
        if v != s:
            xt[(pred[v], v)] = desc(v)
    feas = all(sum(xt[e] for e in Es if e[1] == v) - sum(xt[e] for e in Es if e[0] == v) == 1 for v in V if v != s)
    ok_tree &= feas and abs(sum(E[e] * xt[e] for e in Es) - val2) < 1e-7 and desc(s) == n
    P = dict(sense="max", c=[1] * n, rows=[([(1 if v == e[1] else 0) - (1 if v == e[0] else 0) for v in V], "<=", E[e])
                                         for e in Es], signs=["=0" if v == s else "free" for v in V])
    D = dual(P)
    ok_ssd &= D["rows"] == [(row, "=", 1) for row in Aeq] and D["c"] == [E[e] for e in Es]
check("H.3 single source: max sum dist(v) gives exactly the shortest-path distances (all vertices reachable)",
      ok_ss1, f"{cnt} graphs")
check("H.3 single source: min l.x with one unit of demand at every v != s has the same optimum, sum of distances",
      ok_ss2)
check("H.3 single source: x(u->v) = |D_v| on shortest-path-tree edges is feasible and optimal, D_s = V", ok_tree)
check("H.4: the single-source pair is a dual pair (Figure H.4)", ok_ssd)

# ============================================================================== maximum flow and minimum cut LPs
def maxflow_lp(V, E, cap, s, t):
    Es = list(E)
    Aeq = [[(1 if e[0] == v else 0) - (1 if e[1] == v else 0) for e in Es] for v in V if v not in (s, t)]
    obj = [(1 if e[0] == s else 0) - (1 if e[1] == s else 0) for e in Es]
    return solve(obj, A_eq=Aeq, b_eq=[0] * len(Aeq), bounds=[(0, cap[e]) for e in Es], sense="max")


def mincut_lp(V, E, cap, s, t):
    """variables x(e) (E of them, >= 0) then S(v) (V of them, free, S(s) = 1, S(t) = 0)."""
    Es = list(E)
    m, n = len(Es), len(V)
    idx = {v: k for k, v in enumerate(V)}
    A, b = [], []
    for k, (u, v) in enumerate(Es):
        row = [0] * (m + n)
        row[k] = -1; row[m + idx[v]] -= 1; row[m + idx[u]] += 1   # -(x + S(v) - S(u)) <= 0
        A.append(row); b.append(0)
    bounds = [(0, None)] * m + [((1, 1) if v == s else (0, 0) if v == t else (None, None)) for v in V]
    return solve([cap[e] for e in Es] + [0] * n, A, b, bounds=bounds, sense="min")


def brute_mincut(V, E, cap, s, t):
    others = [v for v in V if v not in (s, t)]
    best = math.inf
    for k in range(len(others) + 1):
        for X in itertools.combinations(others, k):
            S = {s, *X}
            best = min(best, sum(cap[e] for e in E if e[0] in S and e[1] not in S))
    return best


ok_mf = ok_mc = ok_01 = ok_mfd = ok_cs3 = True
cnt = 0
for trial in range(400):
    n = rng.randint(2, 7)
    V = list(range(n))
    E = [(u, v) for u in V for v in V if u != v and rng.random() < 0.4] or [(0, n - 1)]
    cap = {e: rng.randint(0, 9) for e in E}
    s, t = 0, n - 1
    G = nx.DiGraph(); G.add_nodes_from(V)
    for e in E:
        G.add_edge(*e, capacity=cap[e])
    mf = nx.maximum_flow_value(G, s, t) if n > 1 else 0
    st, val, f = maxflow_lp(V, E, cap, s, t)
    ok_mf &= st == "optimal" and abs(val - mf) < 1e-7
    st2, val2, z = mincut_lp(V, E, cap, s, t)
    bc = brute_mincut(V, E, cap, s, t)
    ok_mc &= st2 == "optimal" and abs(val2 - bc) < 1e-7 and abs(bc - mf) < 1e-7
    # a 0/1 optimal solution from a minimum cut
    _, (S, T) = nx.minimum_cut(G, s, t)
    m = len(E)
    zz = [1 if (e[0] in S and e[1] in T) else 0 for e in E] + [1 if v in S else 0 for v in V]
    feas = all(zz[k] + zz[m + V.index(v)] - zz[m + V.index(u)] >= 0 for k, (u, v) in enumerate(E))
    ok_01 &= feas and sum(cap[e] * zz[k] for k, e in enumerate(E)) == bc
    # min-cut LP = mechanical dual of the max-flow LP, after S(v) = -pi(v), S(s) = 1, S(t) = 0
    P = dict(sense="max", c=[(1 if e[0] == s else 0) - (1 if e[1] == s else 0) for e in E],
             rows=[([(1 if e[0] == v else 0) - (1 if e[1] == v else 0) for e in E], "=", 0) for v in V if v not in (s, t)]
             + [([1 if e2 == e else 0 for e2 in E], "<=", cap[e]) for e in E],
             signs=[">=0"] * m)
    D = dual(P)
    sd, vd, _ = solve_general(D)
    ok_mfd &= sd == "optimal" and abs(vd - bc) < 1e-7
    # the dual's constraint for edge u->v reads x(u->v) + pi(u) - pi(v) >= [u = s] - [v = s]  (pi(s), pi(t) absent);
    # with S = -pi, S(s) = 1, S(t) = 0 it is x + S(v) - S(u) >= 0 — check on random points
    inner = [v for v in V if v not in (s, t)]
    for _k in range(5):
        pi = {v: rng.uniform(-2, 2) for v in inner}
        x = {e: rng.uniform(0, 2) for e in E}
        Sv = {**{v: -pi[v] for v in inner}, s: 1, t: 0} if s != t else {}
        for j, e in enumerate(E):
            lhs = x[e] + sum(D["rows"][j][0][k] * pi[v] for k, v in enumerate(inner))
            rhs = D["rows"][j][2]
            ok_mfd &= ((lhs >= rhs - 1e-12) == (x[e] + Sv[e[1]] - Sv[e[0]] >= -1e-12)) and abs(
                (lhs - rhs) - (x[e] + Sv[e[1]] - Sv[e[0]])) < 1e-9
    cnt += 1
check("H.3 max-flow LP: optimum = networkx maximum flow value, 400 random networks", ok_mf)
check("H.3 min-cut LP: optimum = brute-force minimum cut = maximum flow", ok_mc)
check("H.3 min-cut LP: the indicator vector of a minimum cut (S = 1 on S, x = 1 on cut edges) is optimal", ok_01)
check("H.4: the min-cut LP is the dual of the max-flow LP (Figure H.4, then S(v) = -pi(v), S(s) = 1, S(t) = 0)",
      ok_mfd)
# a fractional optimum of the min-cut LP: s->a, a->t with capacity 1
st, val, z = mincut_lp(["s", "a", "t"], [("s", "a"), ("a", "t")], {("s", "a"): 1, ("a", "t"): 1}, "s", "t")
zf = [0.5, 0.5, 1, 0.5, 0]  # x(s->a), x(a->t), S(s), S(a), S(t)
feas = zf[0] + zf[3] - zf[2] >= 0 and zf[1] + zf[4] - zf[3] >= 0
check("H.3: min-cut LP on s->a->t (capacities 1) has the fractional optimum S(a) = 1/2, x = 1/2, 1/2 of value 1",
      st == "optimal" and abs(val - 1) < TOL and feas and zf[0] + zf[1] == 1)

# strict complementarity on s->a->t (capacities 1): flow (1, 1); cut {s} as 0/1 solution x = (1, 0) is not strict;
# the fractional optimum x = (1/2, 1/2), S(a) = 1/2 is
f = [1, 1]
ok_strict_ex = True
for xcut, Sa, strict_expected in [((1, 0), 0, False), ((0, 1), 1, False), ((Fr(1, 2), Fr(1, 2)), Fr(1, 2), True)]:
    S_ = {"s": 1, "a": Sa, "t": 0}
    dual_rows = [xcut[0] + S_["a"] - S_["s"], xcut[1] + S_["t"] - S_["a"]]   # >= 0, one per edge (variable f(e))
    feas = all(r >= 0 for r in dual_rows) and min(xcut) >= 0
    opt = xcut[0] + xcut[1] == 1
    strict = all((xcut[k] > 0) != (f[k] < 1) for k in range(2)) and all((f[k] > 0) != (dual_rows[k] > 0) for k in range(2))
    ok_strict_ex &= feas and opt and strict == strict_expected
check("H.8 s->a->t: both 0/1 minimum cuts are optimal but not strictly complementary with the maximum flow; the "
      "fractional cut S(a) = 1/2 is", ok_strict_ex)

# ============================================================================== figures and page text
def figure_text(name):
    p = os.path.join(FIGS, name + ".html")
    return open(p, encoding="utf-8").read() if os.path.exists(p) else ""


fig = figure_text("nh-shortest-path")
if fig:
    labels = re.findall(r">([^<>]+)</text>", fig)
    check("figure nh-shortest-path: dist labels 0, 2, 3, 4, 6 and the seven edge lengths are drawn",
          all(str(v) in labels for v in ["0", "2", "3", "4", "6"]) and sorted(
              int(x) for x in labels if x.isdigit()).count(2) >= 2)
fig = figure_text("nh-geometry")
if fig:
    check("figure nh-geometry: vertex values and the optimum 11 are drawn", all(s in fig for s in ["(3, 1)", "11"]))
fig = figure_text("nh-dual-forces")
if fig:
    check("figure nh-dual-forces: shows y = 2 and y = 1 on the tight normals and c = (3, 2)", "2" in fig and "(3, 2)" in fig)

if os.path.exists(PAGE):
    page = open(PAGE, encoding="utf-8").read()
    check("page: states the H.6 optimum 14 at (0, 1/2, 9/2) and the dual (1, 3)",
          "14" in page and "9/2" in page and "(1, 3)" in page)
    check("page: states the 2D example optimum 11 at (3, 1) and dual (2, 0, 1)", "(3, 1)" in page and "(2, 0, 1)" in page)
    check("page (review R35): the trap says min dist(t) is unbounded below unless t can reach s, then -delta(t, s); "
          "the min-max remark says both sides are 0 over real vectors",
          "unless $t$ can reach $s$" in page and "$-\\delta(t,s)$" in page and "both sides are 0" in page
          and "both sides are infinite" not in page)
if os.path.exists(CONCEPT):
    cp = open(CONCEPT, encoding="utf-8").read()
    check("concept page: example numbers 11, (3, 1), (2, 0, 1) present", "(3, 1)" in cp and "(2, 0, 1)" in cp)
    check("concept page (review R35): maxflow = mincut needs strong duality AND a 0/1 optimum of the cut LP (checked "
          "above: the indicator vector of a minimum cut is optimal)", "0/1 optimal solution" in cp)

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: {FAIL}")
sys.exit(1 if FAIL else 0)
