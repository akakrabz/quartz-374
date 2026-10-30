#!/usr/bin/env python3
"""Checks for content/2-algorithms/10-maximum-flows-and-minimum-cuts-exercises.md (solved exercises 10.0-10.9 of
Erickson's Algorithms).

Ground truth is computed independently of every algorithm on the page:
  * minimum cuts by enumerating all 2^(V-2) vertex partitions (s in S, t in T);
  * maximum-flow values as the brute-force minimum-cut capacity (cross-checked with networkx);
  * "the maximum flow is unique" and "some maximum flow is positive on a cycle" by enumerating every integral flow
    (exact; with integer capacities the polytope of maximum flows has integral vertices) and, on larger networks,
    by linear programming (scipy/HiGHS);
  * deletion problems by trying every k-subset of edges; decompositions by enumerating all simple cycles and paths.
Every algorithm on the page is implemented as stated and compared with that ground truth on many random small
networks; every counterexample and every number on the page is recomputed. Capacities are integers."""
import itertools
import random
import sys
from collections import deque

import networkx as nx
import numpy as np
from scipy.optimize import linprog

random.seed(10374)
sys.setrecursionlimit(100000)
FAIL = []


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail != "" else ""))
    if not cond:
        FAIL.append(name)


def section(title):
    print("== " + title)


# ============================================================================ networks
# A network is (n, E): vertices 0..n-1, E a list of directed edges (u, v, c); s = 0 and t = n-1 unless stated.
# Flows are lists indexed like E.

def rand_net(n, p, cmin=1, cmax=3, reduced=True, parallel=0.0, rng=random):
    """reduced: at most one edge per unordered pair (the book's assumption in 10.3). Otherwise every ordered pair
    independently, plus parallel copies with probability `parallel`."""
    E = []
    for u in range(n):
        for v in range(u + 1, n):
            if reduced:
                if rng.random() < p:
                    a, b = (u, v) if rng.random() < 0.5 else (v, u)
                    E.append((a, b, rng.randint(cmin, cmax)))
            else:
                for a, b in ((u, v), (v, u)):
                    if rng.random() < p:
                        E.append((a, b, rng.randint(cmin, cmax)))
                        while rng.random() < parallel:
                            E.append((a, b, rng.randint(cmin, cmax)))
    rng.shuffle(E)
    return E


def is_reduced(E):
    pairs = [frozenset((u, v)) for u, v, _ in E]
    return len(pairs) == len(set(pairs)) and all(u != v for u, v, _ in E)


def net_out(n, E, f):
    out = [0] * n
    for (u, v, _), x in zip(E, f):
        out[u] += x
        out[v] -= x
    return out


def feasible(E, f):
    return all(0 <= x <= c for (_, _, c), x in zip(E, f))


def conserves(n, E, f, s, t):
    out = net_out(n, E, f)
    return all(out[v] == 0 for v in range(n) if v not in (s, t))


def value(n, E, f, s):
    return net_out(n, E, f)[s]


def cut_cap(E, S):
    return sum(c for u, v, c in E if u in S and v not in S)


def all_cuts(n, s, t):
    others = [v for v in range(n) if v not in (s, t)]
    for r in range(len(others) + 1):
        for sub in itertools.combinations(others, r):
            yield frozenset((s,) + sub)


def min_cuts(n, E, s, t):
    caps = {S: cut_cap(E, S) for S in all_cuts(n, s, t)}
    lam = min(caps.values())
    return lam, [S for S, c in caps.items() if c == lam]


def nx_maxflow(n, E, s, t):
    G = nx.DiGraph()
    G.add_nodes_from(range(n))
    for i, (u, v, c) in enumerate(E):          # subdivide: parallel and opposite edges are fine
        x = ("e", i)
        G.add_edge(u, x, capacity=c)
        G.add_edge(x, v, capacity=c)
    return nx.maximum_flow_value(G, s, t)


# ---------------------------------------------------------------------------- residual graph, Ford-Fulkerson
def residual_arcs(E, f):
    """General residual multigraph: one arc per original edge and direction (agrees with the book's c_f on reduced
    graphs). Arc = (from, to, edge index, +1 forward / -1 backward, residual capacity)."""
    arcs = []
    for i, ((u, v, c), x) in enumerate(zip(E, f)):
        if x < c:
            arcs.append((u, v, i, +1, c - x))
        if x > 0:
            arcs.append((v, u, i, -1, x))
    return arcs


def reach_arcs(n, arcs, sources, reverse=False):
    A = [[] for _ in range(n)]
    for a, b, *_ in arcs:
        if reverse:
            A[b].append(a)
        else:
            A[a].append(b)
    seen = set(sources)
    Q = deque(sources)
    while Q:
        u = Q.popleft()
        for v in A[u]:
            if v not in seen:
                seen.add(v)
                Q.append(v)
    return seen


def find_path(n, arcs, s, t, rng=None):
    """Whatever-first search in the residual graph; random bag if rng is given (else BFS). Returns list of arcs."""
    A = [[] for _ in range(n)]
    for arc in arcs:
        A[arc[0]].append(arc)
    pred = {s: None}
    bag = [s]
    while bag:
        u = bag.pop(rng.randrange(len(bag))) if rng else bag.pop(0)
        if u == t:
            break
        order = list(A[u])
        if rng:
            rng.shuffle(order)
        for arc in order:
            if arc[1] not in pred:
                pred[arc[1]] = arc
                bag.append(arc[1])
    if t not in pred or s == t:
        return None
    path, v = [], t
    while v != s:
        path.append(pred[v])
        v = pred[v][0]
    return path[::-1]


def push(f, path, F):
    for _, _, i, d, _ in path:
        f[i] += d * F


def ford_fulkerson(n, E, s, t, rng=None, f=None, max_aug=None):
    f = [0] * len(E) if f is None else list(f)
    augs = 0
    while max_aug is None or augs < max_aug:
        path = find_path(n, residual_arcs(E, f), s, t, rng)
        if path is None:
            break
        push(f, path, min(a[4] for a in path))
        augs += 1
    return f, augs


def simple_cycles_E(n, E):
    """All simple directed cycles of the multigraph, as lists of edge indices (length >= 2; no self-loops here)."""
    out = []
    A = [[] for _ in range(n)]
    for i, (u, v, _) in enumerate(E):
        A[u].append((v, i))
    for st in range(n):
        path_e, on = [], {st}

        def go(u):
            for v, i in A[u]:
                if v == st:
                    out.append(path_e + [i])
                elif v > st and v not in on:
                    on.add(v)
                    path_e.append(i)
                    go(v)
                    path_e.pop()
                    on.discard(v)

        go(st)
    return out


def random_flow(n, E, s, t, steps, rng=random):
    """A random feasible integral flow: random pushes along residual s-t paths, residual t-s paths (so values can be
    negative) and directed cycles of G (so flows can be cyclic)."""
    f = [0] * len(E)
    cycles = simple_cycles_E(n, E)
    for _ in range(steps):
        r = rng.random()
        if r < 0.45:
            path = find_path(n, residual_arcs(E, f), s, t, rng)
        elif r < 0.6:
            path = find_path(n, residual_arcs(E, f), t, s, rng)
        else:
            path = None
            if cycles:
                C = rng.choice(cycles)
                room = min(E[i][2] - f[i] for i in C)
                if room > 0:
                    k = rng.randint(1, room)
                    for i in C:
                        f[i] += k
            continue
        if path:
            push(f, path, rng.randint(1, min(a[4] for a in path)))
    return f


# ---------------------------------------------------------------------------- integral and LP ground truth
def integral_flows(n, E, s, t, val):
    """Every integral feasible (s,t)-flow of value `val` (backtracking over edges with a conservation check)."""
    sols = []
    ranges = [range(c + 1) for _, _, c in E]
    for f in itertools.product(*ranges):
        if conserves(n, E, f, s, t) and value(n, E, f, s) == val:
            sols.append(f)
    return sols


def lp_bounds(n, E, s, t, lam):
    """Equality constraints and bounds describing the maximum flows (value lam)."""
    m = len(E)
    rows, rhs = [], []
    for v in range(n):
        if v in (s, t):
            continue
        row = [0.0] * m
        for i, (a, b, _) in enumerate(E):
            if a == v:
                row[i] -= 1
            if b == v:
                row[i] += 1
        rows.append(row)
        rhs.append(0.0)
    row = [0.0] * m
    for i, (a, b, _) in enumerate(E):
        if a == s:
            row[i] += 1
        if b == s:
            row[i] -= 1
    rows.append(row)
    rhs.append(float(lam))
    return np.array(rows), np.array(rhs), [(0, c) for _, _, c in E]


def lp_unique(n, E, s, t, lam):
    A, b, bnd = lp_bounds(n, E, s, t, lam)
    m = len(E)
    for i in range(m):
        for sgn in (1, -1):
            c = np.zeros(m)
            c[i] = sgn
            r = linprog(c, A_eq=A, b_eq=b, bounds=bnd, method="highs")
            assert r.status == 0
            if sgn == 1:
                lo = r.fun
            else:
                hi = -r.fun
        if hi - lo > 1e-7:
            return False
    return True


def lp_cycle_possible(n, E, s, t, lam, C):
    """Is there a maximum flow that is positive on every edge of the cycle C (edge indices)? max tau s.t. f_e >= tau."""
    A, b, bnd = lp_bounds(n, E, s, t, lam)
    m = len(E)
    A2 = np.hstack([A, np.zeros((A.shape[0], 1))])
    Aub = []
    for i in C:
        row = np.zeros(m + 1)
        row[i] = -1
        row[m] = 1
        Aub.append(row)
    c = np.zeros(m + 1)
    c[m] = -1
    r = linprog(c, A_ub=np.array(Aub), b_ub=np.zeros(len(C)), A_eq=A2, b_eq=b, bounds=bnd + [(0, 1)], method="highs")
    assert r.status == 0
    return -r.fun > 1e-7


# ============================================================================ sanity of the helpers
section("helpers")
ok = True
for trial in range(300):
    n = random.randint(2, 6)
    E = rand_net(n, 0.5, 1, 4, reduced=random.random() < 0.5, parallel=0.3)
    lam, _ = min_cuts(n, E, 0, n - 1)
    f, _ = ford_fulkerson(n, E, 0, n - 1, rng=random)
    ok &= feasible(E, f) and conserves(n, E, f, 0, n - 1) and value(n, E, f, 0) == lam == nx_maxflow(n, E, 0, n - 1)
check("Ford-Fulkerson (random augmenting paths) == brute-force min cut == networkx", ok, "300 random networks")

# ============================================================================ Exercise 10.0
section("Exercise 10.0: is f a maximum flow?")


def is_max_flow(n, E, s, t, f):
    if not feasible(E, f):
        return False
    if not conserves(n, E, f, s, t):
        return False
    return t not in reach_arcs(n, residual_arcs(E, f), [s])


counts = {True: 0, False: 0}
ok = True
neg_values = 0
for trial in range(1500):
    n = random.randint(2, 6)
    E = rand_net(n, 0.55, 1, 3, reduced=random.random() < 0.5, parallel=0.25)
    s, t = 0, n - 1
    lam, _ = min_cuts(n, E, s, t)
    kind = trial % 5
    if kind == 0:
        f, _ = ford_fulkerson(n, E, s, t, rng=random)
    elif kind == 1:
        f, _ = ford_fulkerson(n, E, s, t, rng=random, max_aug=random.randint(0, 2))
    elif kind == 2:
        f = random_flow(n, E, s, t, random.randint(1, 8))
    elif kind == 3:
        f, _ = ford_fulkerson(n, E, s, t, rng=random)
        if E:
            i = random.randrange(len(E))
            f[i] += random.choice([-1, 1])
    else:
        f = [random.randint(-1, c + 1) for _, _, c in E]
    truth = feasible(E, f) and conserves(n, E, f, s, t) and value(n, E, f, s) == lam
    got = is_max_flow(n, E, s, t, f)
    ok &= truth == got
    counts[truth] += 1
    if feasible(E, f) and conserves(n, E, f, s, t) and value(n, E, f, s) < 0:
        neg_values += 1
check("10.0 feasibility + conservation + no residual s-t path  <=>  f feasible with |f| = min cut (brute force)",
      ok, f"1500 networks with parallel/opposite edges; {counts[True]} maximum, {counts[False]} not")
check("10.0 the tests include feasible flows of negative value", neg_values > 0, neg_values)

# ============================================================================ Exercise 10.1
section("Exercise 10.1: f' - f is a flow in G_f")


def cf_reduced(E, f):
    """The book's residual capacity on a reduced graph, as a dict over ordered pairs."""
    cf = {}
    for (u, v, c), x in zip(E, f):
        cf[(u, v)] = cf.get((u, v), 0) + c - x
        cf[(v, u)] = cf.get((v, u), 0) + x
    return cf


def difference_flow(E, f, f2):
    g = {}
    for (u, v, _), x, y in zip(E, f, f2):
        d = y - x
        if d > 0:
            g[(u, v)] = d
        elif d < 0:
            g[(v, u)] = -d
    return g


ok = True
tested = 0
for trial in range(1500):
    n = random.randint(2, 7)
    E = rand_net(n, 0.5, 1, 4, reduced=True)
    s, t = 0, n - 1
    f = random_flow(n, E, s, t, random.randint(0, 6))
    f2 = random_flow(n, E, s, t, random.randint(0, 6))
    if value(n, E, f, s) == value(n, E, f2, s):
        continue
    if value(n, E, f, s) > value(n, E, f2, s):
        f, f2 = f2, f
    tested += 1
    cf = cf_reduced(E, f)
    g = difference_flow(E, f, f2)
    good = all(0 < x <= cf.get(k, 0) for k, x in g.items())
    out = [0] * n
    for (a, b), x in g.items():
        out[a] += x
        out[b] -= x
    good &= all(out[v] == 0 for v in range(n) if v not in (s, t))
    good &= out[s] == value(n, E, f2, s) - value(n, E, f, s)
    ok &= good
check("10.1 g = (positive part of f'-f forward, negative part backward) is feasible in G_f, conserved, |g| = |f'|-|f|",
      ok, f"{tested} pairs of random feasible flows on reduced networks")
ok = True
for trial in range(800):
    n = random.randint(2, 7)
    E = rand_net(n, 0.5, 1, 4, reduced=True)
    s, t = 0, n - 1
    f = random_flow(n, E, s, t, random.randint(0, 6))
    lam, _ = min_cuts(n, E, s, t)
    Ef = [(a, b, c) for (a, b), c in cf_reduced(E, f).items() if c > 0]
    ok &= min_cuts(n, Ef, s, t)[0] == lam - value(n, E, f, s)
check("10.1 remark: the maximum flow value of G_f is |f*| - |f|", ok, "800 random feasible flows")

# ============================================================================ Exercise 10.2
section("Exercise 10.2: an edge never crosses two minimum cuts in opposite directions")
ok = True
fwd_seen = 0
for trial in range(1500):
    n = random.randint(3, 7)
    E = rand_net(n, 0.5, 1, 3, reduced=random.random() < 0.5, parallel=0.2)
    lam, cuts = min_cuts(n, E, 0, n - 1)
    for u, v, c in E:
        a = any(u in S and v not in S for S in cuts)
        b = any(v in S and u not in S for S in cuts)
        fwd_seen += a
        ok &= not (a and b)
check("10.2 positive capacities: no edge u->v has min cuts with u in S, v in T and with v in S', u in T'",
      ok, f"1500 networks; {fwd_seen} edges cross some min cut forward")
# zero-capacity counterexample: s->t (1), u->v (0)
E0 = [(0, 3, 1), (1, 2, 0)]
lam, cuts = min_cuts(4, E0, 0, 3)
check("10.2 counterexample with c(u->v) = 0: all four placements of u, v give minimum cuts",
      lam == 1 and len(cuts) == 4 and any(1 in S and 2 not in S for S in cuts) and any(2 in S and 1 not in S for S in cuts))
# the proof: every max flow saturates S->T edges and avoids T->S edges of every min cut
ok = True
for trial in range(800):
    n = random.randint(2, 7)
    E = rand_net(n, 0.5, 0, 3, reduced=random.random() < 0.5, parallel=0.2)
    lam, cuts = min_cuts(n, E, 0, n - 1)
    f, _ = ford_fulkerson(n, E, 0, n - 1, rng=random)
    for S in cuts:
        for (u, v, c), x in zip(E, f):
            if u in S and v not in S:
                ok &= x == c
            if v in S and u not in S:
                ok &= x == 0
check("10.2/10.3 any max flow saturates every S->T edge and avoids every T->S edge of every min cut", ok, "800 networks")

# ============================================================================ Exercise 10.3
section("Exercise 10.3: minimum cuts are closed under intersection and union")
ok = True
multi = 0
for trial in range(1500):
    n = random.randint(3, 7)
    E = rand_net(n, 0.5, 1, 2, reduced=random.random() < 0.5, parallel=0.2)
    lam, cuts = min_cuts(n, E, 0, n - 1)
    cs = set(cuts)
    multi += len(cuts) > 1
    for A in cuts:
        for B in cuts:
            ok &= (A & B) in cs and (A | B) in cs
check("10.3 S n S' and S u S' are minimum cuts whenever S and S' are", ok, f"1500 networks, {multi} with several min cuts")
ok = True
for trial in range(300):
    n = random.randint(3, 7)
    E = rand_net(n, 0.5, 0, 4, reduced=random.random() < 0.5, parallel=0.2)
    cuts = list(all_cuts(n, 0, n - 1))
    for A in cuts:
        for B in cuts:
            ok &= cut_cap(E, A & B) + cut_cap(E, A | B) <= cut_cap(E, A) + cut_cap(E, B)
check("10.3 remark: cut capacity is submodular, ||S n S'|| + ||S u S'|| <= ||S|| + ||S'||", ok, "300 networks, all pairs")

# ============================================================================ Exercise 10.4
section("Exercise 10.4: simplifying opposing pairs (false as printed)")
s, u, v, t = 0, 1, 2, 3
G4 = [(s, u, 1), (u, v, 7), (v, u, 10), (v, t, 1)]
G4p = [(s, u, 1), (v, u, 3), (v, t, 1)]
lamG, cutsG = min_cuts(4, G4, s, t)
lamGp, cutsGp = min_cuts(4, G4p, s, t)
check("10.4 example: max flow 1 in G, 0 in G'", (lamG, lamGp) == (1, 0) and nx_maxflow(4, G4, s, t) == 1
      and nx_maxflow(4, G4p, s, t) == 0)
check("10.4 example: min cuts of G are {s} and {s,u,v} (capacity 1); of G' only {s,u} (capacity 0)",
      sorted(map(sorted, cutsG)) == [[0], [0, 1, 2]] and sorted(map(sorted, cutsGp)) == [[0, 1]])
caps = {tuple(sorted(S)): (cut_cap(G4, S), cut_cap(G4p, S)) for S in all_cuts(4, s, t)}
check("10.4 example: cut capacities in G / G': {s} 1/1, {s,u} 7/0, {s,v} 12/5, {s,u,v} 1/1",
      caps == {(0,): (1, 1), (0, 1): (7, 0), (0, 2): (12, 5), (0, 1, 2): (1, 1)}, caps)
check("10.4(a) fails: the zero flow is a maximum flow in G' but not in G", lamGp == 0 < lamG)


def simplify(E, i, j):
    """Exercise 10.4's G' for the opposing pair E[i] = u->v, E[j] = v->u."""
    (a, b, c1), (_, _, c2) = E[i], E[j]
    m = min(c1, c2)
    out = [e for k, e in enumerate(E) if k not in (i, j)]
    if c1 > m:
        out.append((a, b, c1 - m))
    if c2 > m:
        out.append((b, a, c2 - m))
    return out, m


ok_formula = ok_c = True
differ = 0
for trial in range(1500):
    n = random.randint(3, 7)
    E = rand_net(n, 0.45, 1, 4, reduced=True)
    a, b = random.sample(range(n), 2)
    E = [e for e in E if {e[0], e[1]} != {a, b}] + [(a, b, random.randint(1, 5)), (b, a, random.randint(1, 5))]
    i, j = len(E) - 2, len(E) - 1
    Ep, m = simplify(E, i, j)
    for S in all_cuts(n, 0, n - 1):
        sep = (a in S) != (b in S)
        ok_formula &= cut_cap(Ep, S) == cut_cap(E, S) - m * sep
    lam, _ = min_cuts(n, E, 0, n - 1)
    lamp, _ = min_cuts(n, Ep, 0, n - 1)
    differ += lam != lamp
    # (c): a max flow of G that G' cannot carry
    f, _ = ford_fulkerson(n, E, 0, n - 1, rng=random)
    c1, c2 = E[i][2], E[j][2]

    def fits(f):
        """Can G' carry f (same values on the surviving edges, 0 on the deleted ones)?"""
        if c1 >= c2:
            return f[j] == 0 and f[i] <= c1 - m
        return f[i] == 0 and f[j] <= c2 - m

    g = list(f)
    if fits(g):
        g[i] += m
        g[j] += m
    ok_c &= (feasible(E, g) and conserves(n, E, g, 0, n - 1) and value(n, E, g, 0) == lam and not fits(g))
check("10.4 ||S,T|| in G' = ||S,T|| in G - m if the cut separates u and v, unchanged otherwise", ok_formula,
      "1500 networks, every cut")
check("10.4 the max flow values of G and G' differ on some random networks", differ > 0, f"{differ} of 1500")
check("10.4(c) a max flow of G (pushed m around u->v->u if needed) is feasible in G, maximum, and not a flow of G'",
      ok_c)

# ============================================================================ Exercise 10.5
section("Exercise 10.5: unique maximum flows and unique minimum cuts")


def residual_pairs(E, f):
    R = set()
    for (u, v, c), x in zip(E, f):
        if x < c:
            R.add((u, v))
        if x > 0:
            R.add((v, u))
    return R


def unique_maxflow(n, E, s, t, rng=None):
    """10.5(a), reduced G: unique iff every strong component of G_f is a bidirected tree."""
    f, _ = ford_fulkerson(n, E, s, t, rng=rng)
    R = residual_pairs(E, f)
    H = nx.DiGraph()
    H.add_nodes_from(range(n))
    H.add_edges_from(R)
    for K in nx.strongly_connected_components(H):
        inside = [(x, y) for (x, y) in R if x in K and y in K]
        if any((y, x) not in R for (x, y) in inside):
            return False
        if len(inside) > 2 * (len(K) - 1):
            return False
    return True


def unique_mincut(n, E, s, t, rng=None):
    f, _ = ford_fulkerson(n, E, s, t, rng=rng)
    arcs = residual_arcs(E, f)
    Rs = reach_arcs(n, arcs, [s])
    Rt = reach_arcs(n, arcs, [t], reverse=True)
    return len(Rs | Rt) == n, Rs, Rt


ok = True
stats = {True: 0, False: 0}
for trial in range(700):
    n = random.randint(2, 5)
    E = rand_net(n, 0.6, 1, 2, reduced=True)
    while len(E) > 7:
        E.pop()
    lam, _ = min_cuts(n, E, 0, n - 1)
    truth = len(integral_flows(n, E, 0, n - 1, lam)) == 1
    stats[truth] += 1
    ok &= unique_maxflow(n, E, 0, n - 1, random) == truth
check("10.5(a) SCC/bidirected-tree test == enumeration of all integral maximum flows", ok,
      f"700 reduced networks, {stats[True]} unique, {stats[False]} not")
ok = True
stats = {True: 0, False: 0}
for trial in range(500):
    n = random.randint(3, 7)
    E = rand_net(n, 0.5, 1, 4, reduced=True)
    lam, _ = min_cuts(n, E, 0, n - 1)
    truth = lp_unique(n, E, 0, n - 1, lam)
    stats[truth] += 1
    ok &= unique_maxflow(n, E, 0, n - 1, random) == truth
check("10.5(a) SCC/bidirected-tree test == LP (min and max of every f(e) over all maximum flows)", ok,
      f"500 reduced networks up to 7 vertices, {stats[True]} unique, {stats[False]} not")
ok = True
ok_sandwich = True
stats = {True: 0, False: 0}
for trial in range(1500):
    n = random.randint(2, 7)
    E = rand_net(n, 0.5, 1, 3, reduced=random.random() < 0.5, parallel=0.2)
    lam, cuts = min_cuts(n, E, 0, n - 1)
    got, Rs, Rt = unique_mincut(n, E, 0, n - 1, random)
    stats[len(cuts) == 1] += 1
    ok &= got == (len(cuts) == 1)
    Smax = frozenset(range(n)) - Rt
    ok_sandwich &= frozenset(Rs) in cuts and Smax in cuts and all(Rs <= S <= Smax for S in cuts)
check("10.5(b) unique min cut <=> every vertex is reachable from s or reaches t in G_f (== enumeration)", ok,
      f"1500 networks, {stats[True]} unique, {stats[False]} not")
check("10.5(b) R_s and V - R^t are min cuts, and every min cut S has R_s <= S <= V - R^t", ok_sandwich)
# (c) and (d)
Ec = [(0, 1, 1), (1, 2, 1)]                     # s -> a -> t
lam, cuts = min_cuts(3, Ec, 0, 2)
check("10.5(c) s->a->t, capacities 1, 1: one maximum flow, two minimum cuts {s} and {s,a}",
      len(integral_flows(3, Ec, 0, 2, lam)) == 1 and lp_unique(3, Ec, 0, 2, lam) and len(cuts) == 2)
Ed = [(0, 1, 1), (1, 2, 2), (2, 3, 2), (1, 3, 2)]  # s->a 1, a->b 2, b->t 2, a->t 2
lam, cuts = min_cuts(4, Ed, 0, 3)
caps = {tuple(sorted(S)): cut_cap(Ed, S) for S in all_cuts(4, 0, 3)}
check("10.5(d) s->a 1, a->b 2, b->t 2, a->t 2: unique min cut {s} (capacities 1, 4, 3, 4), two integral max flows",
      cuts == [frozenset({0})] and caps == {(0,): 1, (0, 1): 4, (0, 2): 3, (0, 1, 2): 4}
      and len(integral_flows(4, Ed, 0, 3, lam)) == 2 and not lp_unique(4, Ed, 0, 3, lam), caps)
Et = [(0, 1, 1), (1, 2, 2)]                     # s->a 1, a->t 2
ft, _ = ford_fulkerson(3, Et, 0, 2)
check("10.5(a) trap: s->a (1), a->t (2) has a unique maximum flow, yet G_f has the 2-cycle a->t->a",
      len(integral_flows(3, Et, 0, 2, 1)) == 1 and lp_unique(3, Et, 0, 2, 1)
      and {(1, 2), (2, 1)} <= residual_pairs(Et, ft) and unique_maxflow(3, Et, 0, 2))
check("10.5 the algorithms agree on the two examples",
      unique_maxflow(3, Ec, 0, 2) and not unique_mincut(3, Ec, 0, 2)[0]
      and not unique_maxflow(4, Ed, 0, 3) and unique_mincut(4, Ed, 0, 3)[0])

# ============================================================================ Exercise 10.6
section("Exercise 10.6: acyclic maximum flows")


def make_acyclic(n, E, f):
    """Exercise 10.6(a)'s MakeAcyclic, exactly as on the page. Returns the new flow and the number of loop steps."""
    f = list(f)
    out = [[] for _ in range(n)]
    for i, (u, v, _) in enumerate(E):
        out[u].append(i)
    state = ["new"] * n
    ptr = [0] * n
    steps = 0
    cancel_len = 0
    for r in range(n):
        if state[r] != "new":
            continue
        stack = [r]
        state[r] = "active"
        while stack:
            steps += 1
            v = stack[-1]
            while ptr[v] < len(out[v]) and (f[out[v][ptr[v]]] == 0 or state[E[out[v][ptr[v]]][1]] == "done"):
                ptr[v] += 1
                steps += 1
            if ptr[v] == len(out[v]):
                stack.pop()
                state[v] = "done"
                continue
            i = out[v][ptr[v]]
            w = E[i][1]
            if state[w] == "new":
                stack.append(w)
                state[w] = "active"
            else:                                   # w is active: a flow cycle w ~> v -> w on the stack
                k = stack.index(w)
                cyc = [out[x][ptr[x]] for x in stack[k:]]    # pointer edges from w up to v (v's is v->w)
                F = min(f[j] for j in cyc)
                for j in cyc:
                    f[j] -= F
                cancel_len += len(cyc)
                steps += len(cyc)
                for x in stack[k + 1:]:
                    state[x] = "new"
                del stack[k + 1:]
    return f, steps, cancel_len


def flow_is_acyclic(n, E, f):
    H = nx.DiGraph()
    H.add_nodes_from(range(n))
    H.add_edges_from((u, v) for (u, v, _), x in zip(E, f) if x > 0)
    if any(x > 0 and u == v for (u, v, _), x in zip(E, f)):
        return False
    return nx.is_directed_acyclic_graph(H)


ok = ok_le = ok_time = ok_sum = True
cyclic_before = 0
for trial in range(2000):
    n = random.randint(2, 8)
    E = rand_net(n, 0.5, 1, 4, reduced=random.random() < 0.5, parallel=0.2)
    s, t = 0, n - 1
    if trial % 2:
        f, augs = ford_fulkerson(n, E, s, t, rng=random)
        lam, _ = min_cuts(n, E, s, t)
        ok_sum &= sum(f) <= (n - 1) * lam
        if trial % 4 == 1:            # add circulation around random cycles to make it cyclic
            for C in simple_cycles_E(n, E):
                room = min(E[i][2] - f[i] for i in C)
                if room > 0 and random.random() < 0.5:
                    for i in C:
                        f[i] += room
    else:
        f = random_flow(n, E, s, t, random.randint(1, 8))
    cyclic_before += not flow_is_acyclic(n, E, f)
    g, steps, cl = make_acyclic(n, E, f)
    ok &= (flow_is_acyclic(n, E, g) and conserves(n, E, g, s, t) and value(n, E, g, s) == value(n, E, f, s)
           and feasible(E, g))
    ok_le &= all(0 <= y <= x for x, y in zip(f, g))
    ok_time &= cl <= sum(f) and steps <= 3 * (n + len(E)) + 2 * sum(f)
check("10.6(a) MakeAcyclic returns a feasible acyclic flow with the same value", ok,
      f"2000 flows, {cyclic_before} of them cyclic")
check("10.6(a) MakeAcyclic only decreases flow values", ok_le)
check("10.6(a) total cancelled-cycle length <= sum_e f(e); loop steps <= 3(V+E) + 2 sum_e f(e)", ok_time)
check("10.6(a) Ford-Fulkerson's output has sum_e f(e) <= (V-1)|f*|", ok_sum)


Ep = [(0, 1, 1), (1, 2, 1), (2, 3, 1), (0, 2, 1), (2, 1, 1), (1, 3, 1)]   # s=0, a=1, b=2, t=3
fp = [1] * 6                                    # paths s->a->b->t and s->b->a->t
check("10.6 trap: the sum of the simple paths s->a->b->t and s->b->a->t is a cyclic flow (a->b->a)",
      conserves(4, Ep, fp, 0, 3) and value(4, Ep, fp, 0) == 2 and not flow_is_acyclic(4, Ep, fp))


def every_maxflow_acyclic(n, E, s, t, rng=None):
    """10.6(b), reduced G: H = edges that some max flow uses; every max flow is acyclic iff H is a dag."""
    f, _ = ford_fulkerson(n, E, s, t, rng=rng)
    R = residual_pairs(E, f)
    G_f = nx.DiGraph()
    G_f.add_nodes_from(range(n))
    G_f.add_edges_from(R)
    comp = {}
    for k, K in enumerate(nx.strongly_connected_components(G_f)):
        for x in K:
            comp[x] = k
    H = nx.DiGraph()
    H.add_nodes_from(range(n))
    for (u, v, c), x in zip(E, f):
        if x > 0 or (c > 0 and comp[u] == comp[v]):
            H.add_edge(u, v)
    return nx.is_directed_acyclic_graph(H), H


ok = ok_H = True
stats = {True: 0, False: 0}
for trial in range(400):
    n = random.randint(3, 7)
    E = rand_net(n, 0.5, 1, 3, reduced=True)
    lam, _ = min_cuts(n, E, 0, n - 1)
    truth = not any(lp_cycle_possible(n, E, 0, n - 1, lam, C) for C in simple_cycles_E(n, E))
    got, H = every_maxflow_acyclic(n, E, 0, n - 1, random)
    stats[truth] += 1
    ok &= got == truth
    # H is exactly the set of edges that are positive in some maximum flow
    for i, (u, v, c) in enumerate(E):
        A, b, bnd = lp_bounds(n, E, 0, n - 1, lam)
        cc = np.zeros(len(E))
        cc[i] = -1
        r = linprog(cc, A_eq=A, b_eq=b, bounds=bnd, method="highs")
        ok_H &= (-r.fun > 1e-7) == H.has_edge(u, v)
check("10.6(b) 'H is a dag' == LP over all simple cycles (no maximum flow is positive on a cycle)", ok,
      f"400 reduced networks, {stats[True]} always acyclic, {stats[False]} not")
check("10.6(b) H = the edges that are positive in some maximum flow (LP: max f(e) > 0)", ok_H)

# ============================================================================ Exercise 10.7
section("Exercise 10.7: unit capacities and distance d")


def bfs_levels(n, E, s):
    A = [[] for _ in range(n)]
    for u, v, _ in E:
        A[u].append(v)
    dist = [None] * n
    dist[s] = 0
    Q = deque([s])
    while Q:
        u = Q.popleft()
        for v in A[u]:
            if dist[v] is None:
                dist[v] = dist[u] + 1
                Q.append(v)
    return dist


ok_a = ok_b = ok_cuts = True
tested = 0
for trial in range(3000):
    n = random.randint(2, 9)
    simple = trial % 2 == 0
    E = rand_net(n, random.choice([0.2, 0.35, 0.5]), 1, 1, reduced=False, parallel=0.0 if simple else 0.4)
    s, t = 0, n - 1
    dist = bfs_levels(n, E, s)
    if dist[t] is None:
        continue
    d = dist[t]
    tested += 1
    lam = nx_maxflow(n, E, s, t)
    ok_a &= lam * d <= len(E)
    if simple:
        ok_b &= lam * d * d <= n * n
    # the level cuts: S_i = {dist <= i}, i < d, have disjoint edge sets, each from L_i to L_{i+1}
    used = set()
    L = [sum(1 for x in dist if x == i) for i in range(n + 1)]
    for i in range(d):
        S = {x for x in range(n) if dist[x] is not None and dist[x] <= i}
        cross = [k for k, (u, v, _) in enumerate(E) if u in S and v not in S]
        ok_cuts &= all(dist[E[k][0]] == i and dist[E[k][1]] == i + 1 for k in cross)
        ok_cuts &= not (used & set(cross))
        used |= set(cross)
        if simple:
            ok_cuts &= len(cross) <= L[i] * L[i + 1]
    best = min(L[i] + L[i + 1] for i in range(d))
    ok_cuts &= best * d <= 2 * n
check("10.7(a) unit capacities: |f*| <= E/d", ok_a, f"{tested} networks with parallel edges or simple")
check("10.7(b) simple unit-capacity graphs: |f*| <= V^2/d^2 (constant 1)", ok_b)
check("10.7 level cuts: edges leave S_i only from L_i to L_{i+1}, disjoint for different i, <= |L_i||L_i+1|; "
      "min_i (|L_i|+|L_i+1|) <= 2V/d", ok_cuts)
# tightness of (a): k edge-disjoint paths of length d
ok = True
for k in range(1, 5):
    for d in range(1, 5):
        n = 2 + k * (d - 1)
        E, nxt = [], 1
        for _ in range(k):
            prev = 0
            for _ in range(d - 1):
                E.append((prev, nxt, 1))
                prev = nxt
                nxt += 1
            E.append((prev, n - 1, 1))
        ok &= nx_maxflow(n, E, 0, n - 1) == k == len(E) // d and bfs_levels(n, E, 0)[n - 1] == d
check("10.7(a) is tight: k edge-disjoint s-t paths of length d have E = kd and max flow k", ok)

# ============================================================================ Exercise 10.8
section("Exercise 10.8: delete k edges to minimize the maximum flow")


def delete_k(n, E, s, t, k, rng=None):
    f, _ = ford_fulkerson(n, E, s, t, rng=rng)
    S = reach_arcs(n, residual_arcs(E, f), [s])
    cut = [i for i, (u, v, _) in enumerate(E) if u in S and v not in S]
    rest = [i for i in range(len(E)) if i not in cut]
    return (cut + rest)[:k]


ok = True
tested = 0
for trial in range(600):
    n = random.randint(2, 6)
    E = rand_net(n, 0.5, 1, 1, reduced=False, parallel=0.3)
    m = len(E)
    if m == 0:
        continue
    lam, _ = min_cuts(n, E, 0, n - 1)
    for k in range(0, min(m, 4) + 1):
        best = min(min_cuts(n, [e for i, e in enumerate(E) if i not in D], 0, n - 1)[0]
                   for D in itertools.combinations(range(m), k))
        D = set(delete_k(n, E, 0, n - 1, k, random))
        got = min_cuts(n, [e for i, e in enumerate(E) if i not in D], 0, n - 1)[0]
        ok &= best == max(lam - k, 0) == got and len(D) == k
        tested += 1
check("10.8 deleting k edges of a minimum cut leaves max(lambda - k, 0) == optimum over all k-subsets", ok,
      f"{tested} (network, k) pairs, unit capacities with parallel edges")

# ============================================================================ Exercise 10.9
section("Exercise 10.9: E - V + 1 cycles, E - V + 2 paths and cycles")


def mu(n, edges):
    """Cyclomatic number |edges| - n + (number of connected components of the undirected multigraph)."""
    H = nx.MultiGraph()
    H.add_nodes_from(range(n))
    H.add_edges_from((u, v) for u, v in edges)
    return len(edges) - n + nx.number_connected_components(H)


def greedy_decompose(n, E, f, s, t, rng=random):
    """The book's procedure: add t->s carrying |f|, then repeatedly subtract a flow cycle (found by following
    positive edges) at its bottleneck. Returns (number of s-t paths, number of cycles)."""
    E2 = E + [(t, s, 10 ** 9)]
    g = list(f) + [value(n, E, f, s)]
    assert g[-1] >= 0
    paths = cycles = 0
    while any(x > 0 for x in g):
        start = rng.choice([E2[i][0] for i, x in enumerate(g) if x > 0])
        walk, pos, edges = [start], {start: 0}, []
        while True:
            u = walk[-1]
            i = rng.choice([i for i, (a, b, _) in enumerate(E2) if a == u and g[i] > 0])
            edges.append(i)
            v = E2[i][1]
            if v in pos:
                C = edges[pos[v]:]
                break
            pos[v] = len(walk)
            walk.append(v)
        F = min(g[i] for i in C)
        for i in C:
            g[i] -= F
        if len(E2) - 1 in C:
            paths += 1
        else:
            cycles += 1
    return paths, cycles


ok_mu = True
for trial in range(1000):
    n = random.randint(2, 8)
    E = rand_net(n, 0.4, 1, 1, reduced=False, parallel=0.2)
    edges = [(u, v) for u, v, _ in E]
    m0 = mu(n, edges)
    for k in range(len(edges)):
        rest = edges[:k] + edges[k + 1:]
        H = nx.MultiGraph()
        H.add_nodes_from(range(n))
        H.add_edges_from(rest)
        on_cycle = nx.has_path(H, *edges[k])
        ok_mu &= mu(n, rest) == m0 - (1 if on_cycle else 0)
check("10.9 deleting an edge that lies on a cycle lowers E - V + c by 1; deleting a bridge leaves it unchanged",
      ok_mu, "1000 random multigraphs, every edge")

ok_a = ok_b = True
tested_a = tested_b = 0
for trial in range(3000):
    n = random.randint(2, 7)
    E = rand_net(n, 0.5, 1, 3, reduced=random.random() < 0.5, parallel=0.2)
    U = nx.MultiGraph()
    U.add_nodes_from(range(n))
    U.add_edges_from((u, v) for u, v, _ in E)
    if not nx.is_connected(U):
        continue
    s, t = 0, n - 1
    f = random_flow(n, E, s, t, random.randint(1, 8))
    val = value(n, E, f, s)
    if val < 0:
        continue
    supp = [(u, v) for (u, v, _), x in zip(E, f) if x > 0]
    paths, cycles = greedy_decompose(n, E, f, s, t)
    if val == 0:
        tested_a += 1
        ok_a &= paths == 0 and cycles <= mu(n, supp) <= len(E) - n + 1
    else:
        tested_b += 1
        ok_b &= paths + cycles <= mu(n, supp + [(t, s)]) <= len(E) - n + 2
check("10.9(a) |f| = 0, G connected: greedy decomposition uses <= mu(support) <= E - V + 1 cycles", ok_a,
      f"{tested_a} circulations")
check("10.9(b) |f| > 0, G connected: <= mu(support + t->s) <= E - V + 2 paths and cycles", ok_b, f"{tested_b} flows")
# connectivity is needed
Ea = [(0, 1, 1), (1, 2, 1), (2, 0, 1), (3, 4, 1), (4, 5, 1), (5, 3, 1)]
cyc_a = simple_cycles_E(6, Ea)
check("10.9(a) needs G connected: two disjoint directed triangles, E - V + 1 = 1, but the all-ones circulation "
      "needs 2 cycles", len(Ea) - 6 + 1 == 1 and len(cyc_a) == 2 and conserves(6, Ea, [1] * 6, 0, 5))
# review: the book's "arbitrary (s,t)-flow" needs f >= 0: -1 around a directed triangle (s = 0, t = 1) is a
# nonzero flow of value 0 with no edge of positive flow, so no combination of positive-flow cycles gives it
En9 = [(0, 1, 1), (1, 2, 1), (2, 0, 1)]
fn9 = [-1, -1, -1]
check("10.9 needs f >= 0: -1 on every edge of a directed triangle is a nonzero (s,t)-flow of value 0 with no "
      "edge of positive flow (so no cycle may be used)",
      conserves(3, En9, fn9, 0, 1) and value(3, En9, fn9, 0) == 0 and not any(x > 0 for x in fn9)
      and any(x != 0 for x in fn9))
# (c) tightness: a chain of k directed triangles (consecutive ones share a vertex)
ok = True
for k in range(1, 6):
    n = 2 * k + 1
    E = []
    for j in range(k):
        a, b, c = 2 * j, 2 * j + 1, 2 * j + 2
        E += [(a, b, 1), (b, c, 1), (c, a, 1)]
    cyc = simple_cycles_E(n, E)
    ok &= (len(E) - n + 1 == k and len(cyc) == k and sorted(i for C in cyc for i in C) == list(range(3 * k))
           and conserves(n, E, [1] * len(E), 0, n - 1))
check("10.9(c) chain of k triangles: E - V + 1 = k, its only directed cycles are the k triangles (edge-disjoint), "
      "so the all-ones circulation needs k cycles", ok, "k = 1..5")
ok = True
for k in range(1, 6):
    n = k + 2
    E = [(0, a, 1) for a in range(1, k + 1)] + [(a, n - 1, 1) for a in range(1, k + 1)]
    G = nx.DiGraph([(u, v) for u, v, _ in E])
    ok &= (len(E) - n + 2 == k and nx.is_directed_acyclic_graph(G)
           and len(list(nx.all_simple_paths(G, 0, n - 1))) == k and value(n, E, [1] * len(E), 0) == k)
check("10.9(c) k paths s->a_i->t: E - V + 2 = k, no cycles, exactly k s-t paths, each needed", ok, "k = 1..5")

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: " + "; ".join(FAIL))
