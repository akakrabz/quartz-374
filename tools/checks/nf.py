#!/usr/bin/env python3
"""Checks for content/4-lecture-notes/f-balances-and-pseudoflows.md (Erickson, Extended Dance Remix F, "Balances and
Pseudoflows").

Convention (the note's F.1): the balance of v is (flow into v) - (flow out of v); b > 0 is demand, b < 0 supply.
1. The note's network (Figures on pp. 2-5, vertex names a..f added): balances, capacities, the transformed network
   G', the feasible flow and its saturating flow, the pseudoflow, its residual balances and residual graph, the
   augmenting path and the push of 4 units, and one more augmentation to a feasible flow.
2. Lemma F.1 and Theorem F.2 on random networks: feasible flow (LP) <=> saturating flow in G' <=> no infeasible cut
   (brute force over all 2^V cuts).
3. FeasibleFlow, as printed (with the reversed-edge update corrected), on random networks against an LP: every
   invariant (feasibility of psi, B decreasing by R, at most B iterations), the infeasible-cut certificate in both the
   note's and the corrected orientation, the note's B_psi := sum |b_psi| (twice the supply), the literal
   psi(e) <- psi(e) - R. Theorem F.2 also needs sum b = 0 (counterexample).
   The shortest-augmenting-path rule (one multi-source breadth-first search) and its iteration bound.
4. F.4: maximum (s,t)-flow with balances by the note's construction (vertex z, edges t->z and z->s) and the corrected
   one (also z->t and s->z), two stages, against an LP maximum; the counterexample; lower bounds (psi = max{l, 0},
   negative lower bounds as opposing edges), against an LP; the antisymmetric residual formulas, literal and fixed.
5. F.5 push-relabel, exactly as stated (arbitrary active vertex, push along a downward residual edge, relabel by +1),
   plus FIFO and highest-label selection, against Edmonds-Karp on random networks; Lemmas F.3-F.8 are checked after
   every operation (compatibility, no residual s-t path, active vertices reach s, heights < 2V, relabels per vertex,
   saturating pushes per residual edge <= V, the potential argument for non-saturating pushes); the page's trace.
"""
import itertools
import math
import os
import random
import sys
from collections import deque

import numpy as np
from scipy.optimize import linprog

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
PAGE = os.path.join(ROOT, "content", "4-lecture-notes", "f-balances-and-pseudoflows.md")
FAIL = []
random.seed(374006)


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAIL.append(name)


# ============================================================================ basics
def netin(E, f, v):
    return sum(f[e] for e in E if e[1] == v) - sum(f[e] for e in E if e[0] == v)


def is_feasible_flow(V, E, c, b, f, lo=None):
    lo = lo or {e: 0 for e in E}
    return (all(lo[e] - 1e-9 <= f[e] <= c[e] + 1e-9 for e in E) and
            all(abs(netin(E, f, v) - b[v]) < 1e-9 for v in V))


def lp_feasible(V, E, c, b, lo=None):
    lo = lo or {e: 0 for e in E}
    if not E:
        return all(b[v] == 0 for v in V)
    A = np.zeros((len(V), len(E)))
    for j, (u, v) in enumerate(E):
        A[V.index(v), j] += 1
        A[V.index(u), j] -= 1
    res = linprog(np.zeros(len(E)), A_eq=A, b_eq=[b[v] for v in V], bounds=[(lo[e], c[e]) for e in E], method="highs")
    return res.status == 0


def lp_maxflow_bal(V, E, c, b, s, t, lo=None):
    """max |f| = net out of s, subject to lo <= f <= c and netin(v) = b(v) for v != s, t. None if infeasible."""
    lo = lo or {e: 0 for e in E}
    inner = [v for v in V if v not in (s, t)]
    if not E:
        return 0 if all(b[v] == 0 for v in inner) else None
    A = np.zeros((max(1, len(inner)), len(E)))
    for j, (u, v) in enumerate(E):
        if v in inner:
            A[inner.index(v), j] += 1
        if u in inner:
            A[inner.index(u), j] -= 1
    obj = np.array([(-1 if u == s else 0) + (1 if v == s else 0) for (u, v) in E], dtype=float)
    beq = [b[v] for v in inner] if inner else [0]
    res = linprog(obj, A_eq=A, b_eq=beq, bounds=[(lo[e], c[e]) for e in E], method="highs")
    if res.status != 0:
        return None
    return -res.fun


def residual_caps(E, c, f):
    """Residual capacities of a reduced network (no antiparallel pair): (u,v) -> c - f forward, f backward."""
    r = {}
    for (u, v) in E:
        if c[(u, v)] - f[(u, v)] > 0:
            r[(u, v)] = r.get((u, v), 0) + c[(u, v)] - f[(u, v)]
        if f[(u, v)] > 0:
            r[(v, u)] = r.get((v, u), 0) + f[(u, v)]
    return r


def reach_from(r, x):
    seen, st = {x}, [x]
    while st:
        u = st.pop()
        for (a, bb), cap in r.items():
            if a == u and cap > 0 and bb not in seen:
                seen.add(bb)
                st.append(bb)
    return seen


def reach_to(r, x):
    rev = {(bb, a): cap for (a, bb), cap in r.items()}
    return reach_from(rev, x)


def maxflow_pairs(nodes, cap, s, t):
    """Edmonds-Karp on a dict (u,v) -> capacity (antiparallel and parallel pairs allowed; capacities summed).
    Returns (value, net) where net[(u,v)] = flow pushed from u to v (antisymmetric)."""
    r = {}
    for (u, v), x in cap.items():
        r[(u, v)] = r.get((u, v), 0) + x
        r.setdefault((v, u), 0)
    adj = {v: [] for v in nodes}
    for (u, v) in r:
        adj[u].append(v)
    net = {k: 0 for k in r}
    val = 0
    while True:
        prev = {s: None}
        q = deque([s])
        while q and t not in prev:
            u = q.popleft()
            for v in adj[u]:
                if r[(u, v)] > 1e-12 and v not in prev:
                    prev[v] = u
                    q.append(v)
        if t not in prev:
            return val, net
        path = []
        v = t
        while prev[v] is not None:
            path.append((prev[v], v))
            v = prev[v]
        F = min(r[e] for e in path)
        for (u, v) in path:
            r[(u, v)] -= F
            r[(v, u)] += F
            net[(u, v)] += F
            net[(v, u)] -= F
        val += F


def cut_cap(E, c, S):
    return sum(c[e] for e in E if e[0] in S and e[1] not in S)


def random_network(n, p=0.45, cmax=9, reduced=True):
    V = list(range(n))
    E = []
    for u in V:
        for v in V:
            if u != v and random.random() < p and (not reduced or (v, u) not in E):
                E.append((u, v))
    c = {e: random.randint(1, cmax) for e in E}
    return V, E, c


def random_balances(V, total=8):
    b = {v: 0 for v in V}
    for _ in range(total):
        x, y = random.sample(V, 2)
        b[x] -= 1
        b[y] += 1
    return b


# ============================================================================ FeasibleFlow (F.3), as printed
def feasible_flow(V, E, c, b, rule="any", log=None, literal_rev=False):
    """FeasibleFlow(V, E, c, b). rule: 'any' (random supply s, random reachable demand t, random path) or 'shortest'
    (a shortest path over all supply/demand pairs: one multi-source BFS). Returns ('flow', psi, iters) or
    ('infeasible', psi, s, iters)."""
    psi = {e: 0 for e in E}
    B = sum(abs(b[v]) for v in V) / 2
    iters = 0
    inv = True
    while B > 0:
        bpsi = {v: b[v] - netin(E, psi, v) for v in V}
        r = residual_caps(E, c, psi)
        supplies = [v for v in V if bpsi[v] < 0]
        if rule == "any":
            s = random.choice(supplies)
            R_ = reach_from(r, s)
            dem = [v for v in R_ if bpsi[v] > 0]
            if not dem:
                return ("infeasible", psi, s, iters, inv)
            t = random.choice(dem)
            # any path in G_psi from s to t: randomized DFS
            prev = {s: None}
            st = [s]
            while st:
                u = st.pop()
                nb = [v for (a, v), cp in r.items() if a == u and cp > 0 and v not in prev]
                random.shuffle(nb)
                for v in nb:
                    if v not in prev:
                        prev[v] = u
                        st.append(v)
        else:
            prev = {x: None for x in supplies}
            q = deque(supplies)
            t = None
            while q:
                u = q.popleft()
                if bpsi[u] > 0:
                    t = u
                    break
                for (a, v), cp in r.items():
                    if a == u and cp > 0 and v not in prev:
                        prev[v] = u
                        q.append(v)
            if t is None:
                s = supplies[0]
                return ("infeasible", psi, s, iters, inv)
        path = []
        v = t
        while prev[v] is not None:
            path.append((prev[v], v))
            v = prev[v]
        path.reverse()
        s = path[0][0] if path else t
        R = min([-bpsi[s], bpsi[t]] + [r[e] for e in path])
        if log is not None:
            log.append((path, R))
        B -= R
        for (u, v) in path:
            if (u, v) in E:
                psi[(u, v)] += R
            else:
                if literal_rev:
                    psi[(u, v)] = psi.get((u, v), 0) - R       # the printed line, taken literally
                else:
                    psi[(v, u)] -= R                            # psi(rev(e)) <- psi(rev(e)) - R
        iters += 1
        if not literal_rev:
            bnew = {x: b[x] - netin(E, psi, x) for x in V}
            inv &= all(0 <= psi[e] <= c[e] for e in E)
            inv &= abs(sum(abs(bnew[x]) for x in V) / 2 - B) < 1e-9
            inv &= sum(bnew.values()) == 0
    return ("flow", psi, iters, inv)


# ============================================================================ 1. the note's network
V0 = list("abcdef")
E0 = [("a", "b"), ("b", "c"), ("b", "f"), ("c", "f"), ("c", "d"), ("e", "c"), ("d", "e"), ("f", "e"), ("f", "a")]
c0 = dict(zip(E0, [20, 5, 10, 15, 15, 10, 20, 10, 10]))
b0 = {"a": -5, "b": 2, "c": -1, "d": 6, "e": -4, "f": 2}
check("note's network: balances sum to zero", sum(b0.values()) == 0)
# G'
sup = {v: -b0[v] for v in V0 if b0[v] < 0}
dem = {v: b0[v] for v in V0 if b0[v] > 0}
check("G': edges s->a, s->c, s->e with capacities 5, 1, 4 and b->t, d->t, f->t with 2, 6, 2",
      sup == {"a": 5, "c": 1, "e": 4} and dem == {"b": 2, "d": 6, "f": 2})
f3 = dict(zip(E0, [10, 5, 3, 9, 7, 10, 1, 5, 5]))
check("p. 3 figure: the flow 10, 5, 3, 9, 7, 10, 1, 5, 5 is feasible in G", is_feasible_flow(V0, E0, c0, b0, f3))
capG = dict(c0)
for v, x in sup.items():
    capG[("s*", v)] = x
for v, x in dem.items():
    capG[(v, "t*")] = x
val, _ = maxflow_pairs(V0 + ["s*", "t*"], capG, "s*", "t*")
check("G' has a saturating flow: maximum flow 10 = 5 + 1 + 4 = 2 + 6 + 2", val == 10)
# pseudoflow (p. 5, left)
psi0 = dict(zip(E0, [5, 0, 3, 4, 7, 10, 1, 0, 5]))
bpsi0 = {v: b0[v] - netin(E0, psi0, v) for v in V0}
check("p. 5 pseudoflow: residual balances a = -5, e = +5, all others 0",
      bpsi0 == {"a": -5, "b": 0, "c": 0, "d": 0, "e": 5, "f": 0})
r0 = residual_caps(E0, c0, psi0)
expect_r = {("a", "b"): 15, ("b", "a"): 5, ("b", "c"): 5, ("b", "f"): 7, ("f", "b"): 3, ("c", "f"): 11,
            ("f", "c"): 4, ("c", "d"): 8, ("d", "c"): 7, ("c", "e"): 10, ("d", "e"): 19, ("e", "d"): 1,
            ("f", "e"): 10, ("f", "a"): 5, ("a", "f"): 5}
check("p. 5 residual graph: the 15 residual capacities in the middle panel", r0 == expect_r)
P = [("a", "b"), ("b", "f"), ("f", "c"), ("c", "e")]
R = min([-bpsi0["a"], bpsi0["e"]] + [r0[e] for e in P])
check("augmenting path a->b->f->c->e: residual capacities 15, 7, 4, 10, R = min(5, 5, 4) = 4",
      [r0[e] for e in P] == [15, 7, 4, 10] and R == 4)
psi1 = dict(psi0)
for (u, v) in P:
    if (u, v) in E0:
        psi1[(u, v)] += R
    else:
        psi1[(v, u)] -= R
check("after pushing 4: psi(a->b) = 9, psi(b->f) = 7, psi(c->f) = 0, psi(e->c) = 6 (p. 5, right)",
      (psi1[("a", "b")], psi1[("b", "f")], psi1[("c", "f")], psi1[("e", "c")]) == (9, 7, 0, 6))
bpsi1 = {v: b0[v] - netin(E0, psi1, v) for v in V0}
check("  residual balances now a = -1, e = +1; B = 1", bpsi1 == {"a": -1, "b": 0, "c": 0, "d": 0, "e": 1, "f": 0})
r1 = residual_caps(E0, c0, psi1)
P2 = [("a", "b"), ("b", "c"), ("c", "e")]
R2 = min([1, 1] + [r1[e] for e in P2])
psi2 = dict(psi1)
for (u, v) in P2:
    if (u, v) in E0:
        psi2[(u, v)] += R2
    else:
        psi2[(v, u)] -= R2
check("one more augmentation a->b->c->e (residual 11, 5, 6) moves R = 1 unit and gives a feasible flow",
      [r1[e] for e in P2] == [11, 5, 6] and R2 == 1 and is_feasible_flow(V0, E0, c0, b0, psi2))
check("  that flow: a->b 10, b->c 1, b->f 7, c->f 0, c->d 7, e->c 5, d->e 1, f->e 0, f->a 5",
      [psi2[e] for e in E0] == [10, 1, 7, 0, 7, 5, 1, 0, 5])
# literal reversed-edge update on the note's own path
psil = dict(psi0)
for (u, v) in P:
    if (u, v) in E0:
        psil[(u, v)] += 4
    else:
        psil[(u, v)] = psil.get((u, v), 0) - 4
bl = {v: b0[v] - netin(E0, {e: psil[e] for e in E0}, v) for v in V0}
check("literal 'psi(e) <- psi(e) - R' on the reversed edges f->c, c->e leaves psi(c->f), psi(e->c) unchanged: "
      "e still has +5, f gets -4", psil[("c", "f")] == 4 and psil[("e", "c")] == 10 and bl == {"a": -1, "b": 0, "c": 0,
                                                                                         "d": 0, "e": 5, "f": -4},
      f"residual balances {bl}")
# the page's variant: c->d of capacity 5 makes T = {d} infeasible
c0b = dict(c0)
c0b[("c", "d")] = 5
check("variant with c->d capacity 5: T = {d} is an infeasible cut (5 < 6) and the LP finds no feasible flow",
      cut_cap(E0, c0b, set(V0) - {"d"}) == 5 < b0["d"] and not lp_feasible(V0, E0, c0b, b0))
# B_psi as printed in the note (p. 4, with absolute values; review R30 re-read the PDF)
check("the note's B_psi := sum_v |b_psi(v)| is twice the total residual supply (10 = 2 * 5) and the push of R = 4 "
      "lowers it by 2R = 8; sum|b_psi|/2 (the pseudocode's B) drops by R",
      sum(abs(x) for x in bpsi0.values()) == 10 == 2 * sum(-x for x in bpsi0.values() if x < 0)
      and sum(abs(x) for x in bpsi0.values()) - sum(abs(x) for x in bpsi1.values()) == 2 * R
      and (sum(abs(x) for x in bpsi0.values()) - sum(abs(x) for x in bpsi1.values())) / 2 == R)


# ============================================================================ 2. Lemma F.1, Theorem F.2
def infeasible_cuts(V, E, c, b):
    out = []
    for k in range(len(V) + 1):
        for S in itertools.combinations(V, k):
            S = set(S)
            T = [v for v in V if v not in S]
            if cut_cap(E, c, S) < sum(b[v] for v in T):
                out.append(S)
    return out


okF1 = okF2 = okF2x = True
nfeas = ninf = 0
for _ in range(400):
    n = random.choice([3, 4, 5, 6])
    V, E, c = random_network(n, p=random.choice([0.3, 0.45, 0.6]), cmax=6)
    b = random_balances(V, total=random.randint(1, 9))
    feas = lp_feasible(V, E, c, b)
    cap = dict(c)
    for v in V:
        if b[v] < 0:
            cap[("s*", v)] = -b[v]
        if b[v] > 0:
            cap[(v, "t*")] = b[v]
    val, _ = maxflow_pairs(V + ["s*", "t*"], cap, "s*", "t*")
    okF1 &= feas == (val == sum(x for x in b.values() if x > 0))
    bad = infeasible_cuts(V, E, c, b)
    okF2 &= feas == (len(bad) == 0)
    nfeas += feas
    ninf += not feas
check(f"Lemma F.1 on 400 random networks: feasible (LP) iff G' has a saturating flow ({nfeas} feasible, {ninf} not)",
      okF1)
check("Theorem F.2: a feasible flow exists iff no cut (S, T) has ||S,T|| < b(T) (all 2^V cuts)", okF2)
# Theorem F.2 needs sum b = 0 (review R30): a single vertex of balance -1 has neither a flow nor an infeasible cut
V1, E1, c1, b1 = ["v"], [], {}, {"v": -1}
check("Theorem F.2 without sum b = 0 fails: one vertex with b = -1 has no feasible flow and no infeasible cut",
      not lp_feasible(V1, E1, c1, b1) and infeasible_cuts(V1, E1, c1, b1) == [])
nb_ok = True
_state = random.getstate()  # keep the main random stream unchanged
random.seed(30)
for _ in range(100):
    n = random.choice([3, 4, 5])
    V, E, c = random_network(n, p=0.45, cmax=6)
    b = random_balances(V, total=random.randint(1, 6))
    b[random.choice(V)] += random.choice([-2, -1, 1, 2])
    tot = sum(b.values())
    bad = infeasible_cuts(V, E, c, b)
    nb_ok &= not lp_feasible(V, E, c, b)
    if tot > 0:
        nb_ok &= set() in bad  # S empty, T = V: 0 < b(V)
random.setstate(_state)
check("  with sum b != 0 there is never a feasible flow; sum b > 0 is caught by the cut T = V (100 networks)", nb_ok)

# ============================================================================ 3. FeasibleFlow
okalg = okinv = okiter = okcut = True
note_cut_fail = 0
cut_cases = 0
okshort = okshort_it = True
for _ in range(500):
    n = random.choice([3, 4, 5, 6])
    V, E, c = random_network(n, p=random.choice([0.3, 0.45, 0.6]), cmax=6)
    b = random_balances(V, total=random.randint(1, 9))
    feas = lp_feasible(V, E, c, b)
    B0 = sum(abs(x) for x in b.values()) / 2
    res = feasible_flow(V, E, c, b, "any")
    if res[0] == "flow":
        _, psi, iters, inv = res
        okalg &= feas and is_feasible_flow(V, E, c, b, psi)
        okinv &= inv
        okiter &= iters <= B0
    else:
        _, psi, s, iters, inv = res
        okalg &= not feas
        okinv &= inv
        bpsi = {v: b[v] - netin(E, psi, v) for v in V}
        r = residual_caps(E, c, psi)
        # corrected: a supply vertex that reaches no demand -> S = everything it reaches
        S = reach_from(r, s)
        T = [v for v in V if v not in S]
        okcut &= cut_cap(E, c, S) < sum(b[v] for v in T)
        # corrected, demand side: a demand vertex no supply reaches -> T = everything that reaches it
        for v in V:
            if bpsi[v] > 0:
                Tv = reach_to(r, v)
                if not any(bpsi[x] < 0 for x in Tv):
                    Sv = set(V) - Tv
                    okcut &= cut_cap(E, c, Sv) < sum(b[x] for x in Tv)
        # the note's orientation: for b_psi(s) < 0, T = vertices that can reach s
        cut_cases += 1
        Tn = reach_to(r, s)
        Sn = set(V) - Tn
        if not cut_cap(E, c, Sn) < sum(b[x] for x in Tn):
            note_cut_fail += 1
    rs = feasible_flow(V, E, c, b, "shortest")
    okshort &= (rs[0] == "flow") == feas and (rs[0] != "flow" or is_feasible_flow(V, E, c, b, rs[1]))
    nV, nE = len(V) + 2, len(E) + sum(1 for v in V if b[v] != 0)
    okshort_it &= rs[2] <= nV * nE
check("FeasibleFlow (random supply, random reachable demand, random path) agrees with the LP on 500 networks", okalg)
check("  invariants after every push: 0 <= psi <= c, B = sum|b_psi|/2 drops by exactly R, sum b_psi = 0", okinv)
check("  at most B = sum|b|/2 iterations (integer data)", okiter)
check("  when it returns Infeasible: S = vertices reachable from the stuck supply vertex gives ||S,T|| < b(T); "
      "for a demand vertex no supply reaches, T = vertices that reach it does", okcut)
check("  the note's orientation (b_psi(v) < 0: T = vertices that can reach v) is not an infeasible cut in some cases",
      note_cut_fail > 0, f"{note_cut_fail} of {cut_cases}")
check("shortest augmenting paths (multi-source BFS): same answers, iterations <= V'E' of G'", okshort and okshort_it)
# the small infeasible example of the page
Vx = ["x", "y", "z"]
Ex = [("x", "y"), ("y", "z")]
cx = {("x", "y"): 2, ("y", "z"): 5}
bx = {"x": -3, "y": 0, "z": 3}
res = feasible_flow(Vx, Ex, cx, bx, "any")
psi = res[1]
r = residual_caps(Ex, cx, psi)
check("page example x->y (2), y->z (5), b = -3, 0, +3: one push of 2, then Infeasible",
      res[0] == "infeasible" and psi == {("x", "y"): 2, ("y", "z"): 2})
S = reach_from(r, "x")
check("  S = reachable from x = {x}: ||S,T|| = 2 < b(T) = 3", S == {"x"} and cut_cap(Ex, cx, S) == 2)
check("  the note's rule: vertices that can reach x = {x, y, z}, so S would be empty — not a cut",
      reach_to(r, "x") == {"x", "y", "z"})
check("  demand side: T = vertices that can reach z = {y, z}, the same cut; the note's 'reachable from z' is all of V",
      reach_to(r, "z") == {"y", "z"} and reach_from(r, "z") == {"x", "y", "z"})


# ============================================================================ 4. F.4: max flow with balances
BIG = 10 ** 6


def two_stage_maxflow(V, E, c, b, s, t, corrected=True):
    """Stage 1: feasible (s,t)-flow via the z construction; stage 2: max flow in the residual graph. Returns
    (value, f) or None if stage 1 reports infeasible."""
    bb = {v: (0 if v in (s, t) else b[v]) for v in V}
    bb["z"] = -sum(bb.values())
    E2 = list(E) + [("t", "z")] if False else list(E)
    E2 = list(E) + [(t, "z"), ("z", s)]
    c2 = dict(c)
    c2[(t, "z")] = BIG
    c2[("z", s)] = BIG
    if corrected:
        E2 += [("z", t), (s, "z")]
        c2[("z", t)] = BIG
        c2[(s, "z")] = BIG
    if not lp_feasible(V + ["z"], E2, c2, bb):
        return None
    res = feasible_flow(V + ["z"], E2, c2, bb, "any")
    if res[0] != "flow":
        return None
    f = {e: res[1][e] for e in E}
    # stage 2: residual network of G w.r.t. f, standard max flow
    cap = residual_caps(E, c, f)
    val2, net = maxflow_pairs(V, cap, s, t)
    g = {}
    for (u, v) in E:
        g[(u, v)] = f[(u, v)] + net.get((u, v), 0)
    return sum(g[e] for e in E if e[0] == s) - sum(g[e] for e in E if e[1] == s), g


okmb = True
note_fail = 0
cnt = 0
for _ in range(300):
    n = random.choice([3, 4, 5])
    V, E, c = random_network(n, p=0.5, cmax=6)
    s, t = 0, n - 1
    b = random_balances(V, total=random.randint(0, 6))
    opt = lp_maxflow_bal(V, E, c, b, s, t)
    out = two_stage_maxflow(V, E, c, b, s, t, corrected=True)
    if opt is None:
        okmb &= out is None
    else:
        cnt += 1
        okmb &= out is not None and abs(out[0] - opt) < 1e-6
        g = out[1]
        okmb &= all(0 <= g[e] <= c[e] for e in E) and all(netin(E, g, v) == b[v] for v in V if v not in (s, t))
        if two_stage_maxflow(V, E, c, b, s, t, corrected=False) is None:
            note_fail += 1
check(f"F.4 two-stage maximum flow with balances (z with edges both ways) = LP maximum on 300 networks ({cnt} feasible)",
      okmb)
check("  the note's z construction (only t->z and z->s) wrongly reports infeasible on some feasible instances",
      note_fail > 0, f"{note_fail} of {cnt}")
Vc = ["s", "t", "v"]
Ec = [("s", "t"), ("t", "v")]
cc = {("s", "t"): 10, ("t", "v"): 20}
bc = {"s": 0, "t": 0, "v": 15}
check("page counterexample s->t (10), t->v (20), v absorbs 15: LP maximum 10",
      abs(lp_maxflow_bal(Vc, Ec, cc, bc, "s", "t") - 10) < 1e-9)
check("  the note's G' has no feasible flow (t->z would need -15 + |f| < 0)",
      two_stage_maxflow(Vc, Ec, cc, bc, "s", "t", corrected=False) is None)
outc = two_stage_maxflow(Vc, Ec, cc, bc, "s", "t", corrected=True)
check("  with z->t and s->z added: maximum flow 10, with f(t->v) = 15", outc is not None and outc[0] == 10 and
      outc[1][("t", "v")] == 15)


# ---- lower bounds
def maxflow_lower_bounds(V, E, lo, c, s, t):
    """The note's recipe: psi = max(l, 0); residual lower bounds <= 0; negative residual lower bounds become an
    opposing edge; then the two-stage max flow with balances. Returns (value, f) or None."""
    psi = {e: max(lo[e], 0) for e in E}
    if any(psi[e] > c[e] for e in E):
        return None
    bpsi = {v: 0 - netin(E, psi, v) for v in V}          # residual balance (b = 0 for v != s, t)
    # residual network: forward edge cap c - psi, and an opposing edge v->u of cap -(l - psi) if l - psi < 0
    E2, c2 = [], {}
    sub = 0
    for (u, v) in E:
        x = ("x", sub)
        sub += 1
        E2 += [(u, x), (x, v)]                         # subdivide (keeps the network reduced)
        c2[(u, x)] = c2[(x, v)] = c[(u, v)] - psi[(u, v)]
        lr = lo[(u, v)] - psi[(u, v)]
        if lr < 0:
            y = ("y", sub)
            sub += 1
            E2 += [(v, y), (y, u)]
            c2[(v, y)] = c2[(y, u)] = -lr
    V2 = V + sorted({w for e in E2 for w in e if isinstance(w, tuple)}, key=str)
    b2 = {v: (bpsi[v] if v in bpsi else 0) for v in V2}
    out = two_stage_maxflow(V2, E2, c2, b2, s, t, corrected=True)
    if out is None:
        return None
    val2, g2 = out
    f = {}
    sub = 0
    for (u, v) in E:
        x = ("x", sub)
        sub += 1
        fl = psi[(u, v)] + g2[(u, x)]
        if lo[(u, v)] - psi[(u, v)] < 0:
            y = ("y", sub)
            sub += 1
            fl -= g2[(v, y)]
        f[(u, v)] = fl
    return sum(f[e] for e in E if e[0] == s) - sum(f[e] for e in E if e[1] == s), f


oklb = True
nlb = 0
for _ in range(200):
    n = random.choice([3, 4, 5])
    V, E, c = random_network(n, p=0.55, cmax=6)
    lo = {e: random.choice([0, 0, random.randint(-3, c[e])]) for e in E}
    s, t = 0, n - 1
    b = {v: 0 for v in V}
    opt = lp_maxflow_bal(V, E, c, b, s, t, lo=lo)
    out = maxflow_lower_bounds(V, E, lo, c, s, t)
    if opt is None:
        oklb &= out is None
    else:
        nlb += 1
        oklb &= out is not None and abs(out[0] - opt) < 1e-6
        if out is not None:
            f = out[1]
            oklb &= all(lo[e] <= f[e] <= c[e] for e in E) and all(netin(E, f, v) == 0 for v in V if v not in (s, t))
check(f"lower bounds (some negative): psi = max(l,0), opposing edges, two stages = LP maximum ({nlb} of 200 feasible)",
      oklb)

# antisymmetric residual bounds
ok_fix = True
lit_fail = 0
for _ in range(300):
    cuv = random.randint(0, 6)
    luv = random.randint(-4, cuv)
    p_ = random.randint(luv, cuv)                       # psi(u->v), feasible
    # extension to the reversal
    l_vu, c_vu, p_vu = -cuv, -luv, -p_
    # case 1 (u->v in E)
    lres_uv, cres_uv = luv - p_, cuv - p_
    # case 2 for the pair v->u (whose reversal u->v is in E): printed vs corrected
    lres_vu_print, cres_vu_print = p_vu - cuv, p_vu - luv          # psi(v->u) - c(u->v), psi(v->u) - l(u->v)
    lres_vu_fix, cres_vu_fix = p_ - cuv, p_ - luv                  # psi(u->v) - c(u->v), psi(u->v) - l(u->v)
    ok_fix &= lres_vu_fix == -cres_uv and cres_vu_fix == -lres_uv
    ok_fix &= lres_vu_fix == l_vu - p_vu and cres_vu_fix == c_vu - p_vu
    if not (lres_vu_print == -cres_uv and cres_vu_print == -lres_uv):
        lit_fail += 1
check("antisymmetric residual bounds: l_psi(e) = l(e) - psi(e), c_psi(e) = c(e) - psi(e) for e and its reversal; "
      "l_psi(v->u) = -c_psi(u->v)", ok_fix)
check("  the printed second case (psi of the pair itself, under antisymmetry) breaks antisymmetry whenever psi != 0",
      lit_fail > 0, f"{lit_fail} of 300")


# ============================================================================ 5. push-relabel
def push_relabel(V, E, c, s, t, select="any", trace=None, check_inv=True):
    n = len(V)
    r = {}
    for (u, v) in E:
        r[(u, v)] = r.get((u, v), 0) + c[(u, v)]
        r.setdefault((v, u), 0)
    nb = {v: [] for v in V}
    for (u, v) in r:
        nb[u].append(v)
    h = {v: 0 for v in V}
    h[s] = n
    ex = {v: 0 for v in V}
    for v in nb[s]:
        x = r[(s, v)]
        if x > 0:
            r[(s, v)] -= x
            r[(v, s)] += x
            ex[v] += x
            ex[s] -= x
    stats = dict(relabel={v: 0 for v in V}, sat={}, nonsat=0, ops=0, phi_inc=0, phi_dec_nonsat=0)
    ok = dict(compat=True, nost=True, back=True, height=True, preflow=True, nonsat_drop=True)
    fifo = deque([v for v in V if v not in (s, t) and ex[v] > 0])

    def active():
        return [v for v in V if v not in (s, t) and ex[v] > 0]

    def phi():
        return sum(h[v] for v in active())

    while True:
        act = active()
        if not act:
            break
        if select == "any":
            u = random.choice(act)
        elif select == "fifo":
            while fifo and not (fifo[0] not in (s, t) and ex[fifo[0]] > 0):
                fifo.popleft()
            u = fifo[0]
        else:
            u = max(act, key=lambda x: (h[x], random.random()))
        down = [v for v in nb[u] if r[(u, v)] > 0 and h[u] > h[v]]
        p0 = phi()
        if down:
            v = random.choice(down) if select == "any" else down[0]
            d = min(ex[u], r[(u, v)])
            sat = d == r[(u, v)]
            was_active = v not in (s, t) and ex[v] > 0
            r[(u, v)] -= d
            r[(v, u)] += d
            ex[u] -= d
            ex[v] += d
            if select == "fifo" and v not in (s, t) and not was_active:
                fifo.append(v)
            if sat:
                stats["sat"][(u, v)] = stats["sat"].get((u, v), 0) + 1
                stats["phi_inc"] += max(0, phi() - p0)
            else:
                stats["nonsat"] += 1
                stats["phi_dec_nonsat"] += p0 - phi()
                ok["nonsat_drop"] &= p0 - phi() >= 1
            if trace is not None:
                trace.append(("push", u, v, d, sat))
            if select == "fifo" and ex[u] == 0:
                fifo.popleft()
        else:
            h[u] += 1
            stats["relabel"][u] += 1
            stats["phi_inc"] += phi() - p0
            if trace is not None:
                trace.append(("relabel", u, h[u]))
        stats["ops"] += 1
        if check_inv:
            ok["compat"] &= all(h[a] <= h[b_] + 1 for (a, b_), x in r.items() if x > 0)
            ok["nost"] &= t not in reach_from({k: x for k, x in r.items() if x > 0}, s)
            ok["preflow"] &= all(ex[v] >= 0 for v in V if v != s)
            back = reach_to({k: x for k, x in r.items() if x > 0}, s)
            ok["back"] &= all(v in back for v in active())
            ok["height"] &= all(h[v] < 2 * n for v in V)
    flowval = ex[t]
    return flowval, stats, ok, h


okpr = {k: True for k in ["value", "compat", "nost", "back", "height", "preflow", "nonsat_drop", "relabels", "sat",
                          "nonsat", "fifo", "hl"]}
maxsat = 0
for _ in range(250):
    n = random.choice([3, 4, 5, 6, 7])
    V, E, c = random_network(n, p=random.choice([0.35, 0.5, 0.7]), cmax=9, reduced=False)
    s, t = 0, n - 1
    val, _ = maxflow_pairs(V, {e: c[e] for e in E}, s, t)
    fv, st, ok, h = push_relabel(V, E, c, s, t, "any")
    okpr["value"] &= fv == val
    for k in ok:
        okpr[k] &= ok[k]
    okpr["relabels"] &= all(x < 2 * n for x in st["relabel"].values())
    okpr["sat"] &= all(x <= n for x in st["sat"].values())
    maxsat = max([maxsat] + list(st["sat"].values()))
    okpr["nonsat"] &= st["nonsat"] <= st["phi_dec_nonsat"] <= st["phi_inc"]
    fv2, st2, ok2, _ = push_relabel(V, E, c, s, t, "fifo", check_inv=False)
    okpr["fifo"] &= fv2 == val and st2["nonsat"] <= 4 * n ** 3
    fv3, st3, ok3, _ = push_relabel(V, E, c, s, t, "highest", check_inv=False)
    okpr["hl"] &= fv3 == val
check("push-relabel (arbitrary active vertex, random downward edge, relabel +1) = Edmonds-Karp value, 250 networks",
      okpr["value"])
check("  Lemma F.3: heights compatible with psi after every operation", okpr["compat"])
check("  Lemma F.4: no residual path from s to t after every operation", okpr["nost"])
check("  preflow: every vertex except s has non-negative excess", okpr["preflow"])
check("  Lemma F.6's proof: every active vertex has a residual path to s; every height < 2V", okpr["back"] and
      okpr["height"])
check("  Lemma F.6: each vertex is relabeled fewer than 2V times", okpr["relabels"])
check("  Lemma F.7: at most V saturating pushes along each residual edge", okpr["sat"], f"max seen {maxsat}")
check("  Lemma F.8: each non-saturating push lowers Phi by >= 1; their number <= total increase of Phi",
      okpr["nonsat"] and okpr["nonsat_drop"])
check("FIFO selection: correct, non-saturating pushes <= 4V^3", okpr["fifo"])
check("highest-label selection: correct", okpr["hl"])

# the page's trace: s->a 3, s->b 2, a->b 1, a->t 2, b->t 3 (maximum flow 5), FIFO, first downward edge in order
Vt = ["s", "a", "b", "t"]
Et = [("s", "a"), ("s", "b"), ("a", "b"), ("a", "t"), ("b", "t")]
ct = dict(zip(Et, [3, 2, 1, 2, 3]))
tr = []
fv, st, ok, h = push_relabel(Vt, Et, ct, "s", "t", "fifo", trace=tr)
print("     trace:", tr, "heights", h)
check("page trace (FIFO): value 5", fv == 5 and all(ok.values()))
ops = [x for x in tr]
check("page trace: a relabels to 1 and pushes 1 to b and 2 to t; b relabels to 1 and pushes 3 to t (all saturating)",
      ops == [("relabel", "a", 1), ("push", "a", "b", 1, True), ("push", "a", "t", 2, True),
              ("relabel", "b", 1), ("push", "b", "t", 3, True)], f"{ops}")
# excess returned to the source: s->a (3), a->t (1)
tr2 = []
fv, st, ok, h = push_relabel(["s", "a", "t"], [("s", "a"), ("a", "t")], {("s", "a"): 3, ("a", "t"): 1}, "s", "t",
                             "fifo", trace=tr2)
print("     trace:", tr2, "heights", h)
check("page trace 2 (s->a 3, a->t 1): a relabels to 1, pushes 1 to t, relabels to 2, 3, 4 = |V| + 1, pushes 2 back "
      "to s; value 1",
      fv == 1 and all(ok.values()) and tr2 == [("relabel", "a", 1), ("push", "a", "t", 1, True), ("relabel", "a", 2),
                                               ("relabel", "a", 3), ("relabel", "a", 4),
                                               ("push", "a", "s", 2, False)], f"{tr2}")


# ============================================================================ page text
def page_checks():
    if not os.path.exists(PAGE):
        check("page exists", False, PAGE)
        return
    txt = open(PAGE, encoding="utf-8").read()
    for s_ in ["\\min\\{5, 5, 4\\} = 4", "15, 7, 4, 10", "||S,T||", "2 < 3", "11, 5, 6", "10, 1, 7, 0, 7, 5, 1, 0, 5",
               "whose balances sum to zero", "twice the total residual supply"]:
        check(f"page mentions '{s_}'", s_.replace(" ", "") in txt.replace(" ", "").replace("\\lVert", "||")
              .replace("\\rVert", "||"))


page_checks()
print()
if FAIL:
    print(f"{len(FAIL)} FAILED")
    sys.exit(1)
print("ALL OK")
