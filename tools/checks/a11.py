#!/usr/bin/env python3
"""Checks for every concrete claim on content/2-algorithms/11-applications-of-flows-and-cuts.md and the concept pages
flow-reductions and bipartite-matching.

A maximum-flow routine (Edmonds–Karp on an edge list, antiparallel edges and infinite capacities allowed) is validated
against brute-force minimum cuts; then every reduction on the page is implemented exactly as the page describes it and
compared with brute force on many random small instances: edge-disjoint paths (directed and undirected) and
vertex-disjoint paths by exhaustive packing of simple paths, vertex capacities against a linear program, bipartite
matching by exhaustive search (plus the alternating-path algorithm and Berge's theorem), tuple selection by exhaustive
search over multisets of tuples, exam scheduling over all schedules, disjoint-path covers over all edge subsets,
faculty hiring over all partitions of the classes, baseball elimination over all outcomes of the remaining games (with
the certificate-cut theorem), and project selection over all subsets. Every number, table entry and figure label on
the pages is recomputed."""
import itertools
import math
import os
import random
import re
import sys
from collections import deque

import numpy as np
from scipy.optimize import linprog

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
PAGE = os.path.join(ROOT, "content", "2-algorithms", "11-applications-of-flows-and-cuts.md")
CONCEPTS = os.path.join(ROOT, "content", "concepts")
FIGS = os.path.join(HERE, "..", "figs")
FAIL = []
random.seed(11374)
INF = math.inf


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAIL.append(name)


def read(path):
    return open(path, encoding="utf-8").read()


# =====================================================================================================
# Maximum flow: Edmonds–Karp on an edge list. edges: list of (u, v, capacity); capacity int or INF.
def maxflow(edges, s, t, rand=None):
    """Returns (value, flow list aligned with edges, set of vertices reachable from s in the final residual graph).
    rand=True: Ford–Fulkerson with augmenting paths found by a randomized depth-first search; rand=False:
    Edmonds–Karp (breadth-first search); rand=None (default): either, at random, so that every reduction is tested
    with different maximum flows."""
    if rand is None:
        rand = random.random() < 0.5
    to, cap, adj = [], [], {}
    for u, v, c in edges:
        for x in (u, v):
            adj.setdefault(x, [])
        adj[u].append(len(to)); to.append(v); cap.append(c)
        adj[v].append(len(to)); to.append(u); cap.append(0)
    adj.setdefault(s, []); adj.setdefault(t, [])
    val = 0
    while True:
        pred = {s: None}
        if rand:  # true depth-first search (mark when popped), random neighbor order
            pred, stack = {}, [(s, None)]
            while stack and t not in pred:
                u, e0 = stack.pop()
                if u in pred:
                    continue
                pred[u] = e0
                for e in random.sample(adj[u], len(adj[u])):
                    if cap[e] > 0 and to[e] not in pred:
                        stack.append((to[e], e))
        Q = deque([] if rand else [s])
        while Q and t not in pred:
            u = Q.popleft()
            for e in adj[u]:
                if cap[e] > 0 and to[e] not in pred:
                    pred[to[e]] = e
                    Q.append(to[e])
        if t not in pred:
            break
        b, v = INF, t
        path = []
        while pred[v] is not None:
            e = pred[v]
            path.append(e)
            b = min(b, cap[e])
            v = to[e ^ 1]
        assert b < INF, "infinite augmenting path"
        for e in path:
            cap[e] -= b
            cap[e ^ 1] += b
        val += b
    flow = [cap[2 * i + 1] for i in range(len(edges))]  # residual of the reverse edge = flow
    return val, flow, set(pred)


def flow_ok(edges, flow, s, t, value):
    """Feasibility: 0 <= f <= c, conservation at every vertex but s, t, and the stated value."""
    bal = {}
    for (u, v, c), f in zip(edges, flow):
        if f < 0 or f > c:
            return False
        bal[u] = bal.get(u, 0) - f
        bal[v] = bal.get(v, 0) + f
    if any(b != 0 for x, b in bal.items() if x not in (s, t)):
        return False
    return -bal.get(s, 0) == value


def cut_capacity(edges, S):
    return sum(c for u, v, c in edges if u in S and v not in S)


def brute_mincut(edges, s, t):
    V = sorted({x for u, v, c in edges for x in (u, v)} | {s, t}, key=str)
    others = [x for x in V if x not in (s, t)]
    best = INF
    for r in range(len(others) + 1):
        for X in itertools.combinations(others, r):
            best = min(best, cut_capacity(edges, set(X) | {s}))
    return best


def decompose(edges, flow, s, t):
    """Integral flow -> list of s-t paths (vertex lists), one per unit of value; cycles are discarded."""
    units = {}
    for (u, v, c), f in zip(edges, flow):
        for _ in range(int(f)):
            units.setdefault(u, []).append(v)
    paths = []
    while units.get(s):
        walk = [s]
        pos = {s: 0}
        while walk[-1] != t:
            u = walk[-1]
            v = units[u].pop()
            if v in pos:  # shortcut a cycle
                for x in walk[pos[v] + 1:]:
                    del pos[x]
                walk = walk[:pos[v] + 1]
            else:
                pos[v] = len(walk)
                walk.append(v)
        paths.append(walk)
    return paths


# ----------------------------------------------------------------- validate the max-flow routine
ok = True
for trial in range(400):
    n = random.randint(2, 6)
    edges = []
    for u in range(n):
        for v in range(n):
            if u != v and random.random() < 0.45:
                edges.append((u, v, random.randint(0, 4)))
    if random.random() < 0.3 and edges:
        u, v, c = random.choice(edges)
        edges.append((u, v, INF if random.random() < 0.5 else 2))  # parallel / infinite edges
    s, t = 0, n - 1
    if brute_mincut(edges, s, t) == INF:
        continue
    val, fl, S = maxflow(edges, s, t)
    if not (flow_ok(edges, fl, s, t, val) and val == brute_mincut(edges, s, t) and s in S and t not in S
            and cut_capacity(edges, S) == val):
        ok = False
        print("  maxflow mismatch", edges, val, brute_mincut(edges, s, t))
        break
check("max-flow routine: value = brute-force minimum cut, flow feasible, residual cut is minimum (400 networks)", ok)


# =====================================================================================================
def simple_paths(adj, s, t):
    out = []

    def rec(p, seen):
        u = p[-1]
        if u == t:
            out.append(list(p))
            return
        for v in adj.get(u, []):
            if v not in seen:
                seen.add(v); p.append(v)
                rec(p, seen)
                p.pop(); seen.discard(v)
    rec([s], {s})
    return out


def max_packing(items, conflict):
    """Largest set of pairwise non-conflicting items (exhaustive)."""
    best = 0

    def rec(i, chosen):
        nonlocal best
        if len(chosen) + (len(items) - i) <= best:
            return
        if i == len(items):
            best = max(best, len(chosen))
            return
        if all(not conflict(items[i], c) for c in chosen):
            chosen.append(items[i]); rec(i + 1, chosen); chosen.pop()
        rec(i + 1, chosen)
    rec(0, [])
    return best


def rand_digraph(n, p):
    return [(u, v) for u in range(n) for v in range(n) if u != v and random.random() < p]


# ----------------------------------------------------------------- 11.1 edge-disjoint paths, directed
ok, cnt, vbound = True, 0, True
for trial in range(500):
    n = random.randint(2, 6)
    E = rand_digraph(n, 0.45)
    s, t = 0, n - 1
    adj = {}
    for u, v in E:
        adj.setdefault(u, []).append(v)
    P = [frozenset(zip(p, p[1:])) for p in simple_paths(adj, s, t)]
    brute = max_packing(P, lambda a, b: bool(a & b))
    net = [(u, v, 1) for u, v in E]
    val, fl, _ = maxflow(net, s, t)
    paths = decompose(net, fl, s, t)
    used = [e for p in paths for e in zip(p, p[1:])]
    valid = (len(paths) == val and len(used) == len(set(used)) and all(e in set(E) for e in used)
             and all(p[0] == s and p[-1] == t and len(set(p)) == len(p) for p in paths))
    ok &= (val == brute and valid)
    vbound &= val <= n - 1
    cnt += 1
check(f"11.1 directed: max flow = max number of edge-disjoint paths (exhaustive), and the walks give that many "
      f"edge-disjoint simple paths ({cnt} graphs)", ok)
check("11.1: |f*| <= V - 1 in simple graphs", vbound)

# Menger (edge version): min number of edges whose deletion separates t from s = max flow
ok = True
for trial in range(200):
    n = random.randint(2, 5)
    E = rand_digraph(n, 0.5)
    s, t = 0, n - 1
    val = maxflow([(u, v, 1) for u, v in E], s, t)[0]
    best = None
    for r in range(len(E) + 1):
        for F in itertools.combinations(E, r):
            rest = [e for e in E if e not in F]
            adj = {}
            for u, v in rest:
                adj.setdefault(u, []).append(v)
            seen, st = {s}, [s]
            while st:
                u = st.pop()
                for v in adj.get(u, []):
                    if v not in seen:
                        seen.add(v); st.append(v)
            if t not in seen:
                best = r
                break
        if best is not None:
            break
    ok &= best == val
check("11.1 Menger, edge version: minimum separating edge set = maximum flow (200 graphs, exhaustive)", ok)

# ----------------------------------------------------------------- 11.1 undirected
ok, needed_cancel = True, 0
for trial in range(800):
    n = random.randint(2, 7)
    UE = [(u, v) for u in range(n) for v in range(u + 1, n) if random.random() < 0.55]
    s, t = 0, n - 1
    adj = {}
    for u, v in UE:
        adj.setdefault(u, []).append(v); adj.setdefault(v, []).append(u)
    P = [frozenset(frozenset(e) for e in zip(p, p[1:])) for p in simple_paths(adj, s, t)]
    brute = max_packing(P, lambda a, b: bool(a & b))
    net = [(u, v, 1) for u, v in UE] + [(v, u, 1) for u, v in UE]
    val, fl, _ = maxflow(net, s, t, rand=trial % 2 == 1)
    m = len(UE)
    fl = list(fl)
    for i in range(m):
        if fl[i] == 1 and fl[i + m] == 1:
            fl[i] = fl[i + m] = 0
            needed_cancel += 1
    feasible = flow_ok(net, fl, s, t, val)
    paths = decompose(net, fl, s, t)
    used = [frozenset(e) for p in paths for e in zip(p, p[1:])]
    ok &= (feasible and val == brute and len(paths) == val and len(used) == len(set(used))
           and all(e in {frozenset(x) for x in UE} for e in used))
check("11.1 undirected: two directed unit edges per edge; after canceling two-way flow the value is unchanged and the "
      "walks give max-many edge-disjoint undirected paths (800 graphs, BFS and randomized DFS augmentation, exhaustive)", ok and needed_cancel > 0,
      f"two-way flow canceled {needed_cancel} times")


# ----------------------------------------------------------------- 11.2 vertex splitting
def split_net(n, s, t, E, ecap, vcap):
    """Page's construction: v -> v_in -> v_out for v not in {s, t}; u->v becomes u_out -> v_in."""
    io = lambda v, side: v if v in (s, t) else (v, side)
    net = [((v, "in"), (v, "out"), vcap[v]) for v in range(n) if v not in (s, t)]
    k = len(net)
    net += [(io(u, "out"), io(v, "in"), ecap[(u, v)]) for u, v in E]
    return net, k


def lp_vertex_maxflow(n, s, t, E, ecap, vcap):
    m = len(E)
    c = np.zeros(m)
    for i, (u, v) in enumerate(E):
        if u == s:
            c[i] -= 1
        if v == s:
            c[i] += 1
    Aeq, beq, Aub, bub = [], [], [], []
    for x in range(n):
        if x in (s, t):
            continue
        row = np.zeros(m)
        rin = np.zeros(m)
        for i, (u, v) in enumerate(E):
            if v == x:
                row[i] += 1; rin[i] = 1
            if u == x:
                row[i] -= 1
        Aeq.append(row); beq.append(0)
        Aub.append(rin); bub.append(vcap[x])
    res = linprog(c, A_ub=np.array(Aub) if Aub else None, b_ub=bub if bub else None,
                  A_eq=np.array(Aeq) if Aeq else None, b_eq=beq if beq else None,
                  bounds=[(0, ecap[e]) for e in E], method="highs")
    return -res.fun, res.x


ok, ok_conv = True, True
for trial in range(300):
    n = random.randint(2, 6)
    E = rand_digraph(n, 0.45)
    if not E:
        continue
    s, t = 0, n - 1
    ecap = {e: random.randint(1, 3) for e in E}
    vcap = {v: random.randint(0, 3) for v in range(n)}
    net, k = split_net(n, s, t, E, ecap, vcap)
    val, fl, _ = maxflow(net, s, t)
    f = {E[i]: fl[k + i] for i in range(len(E))}
    # map back: feasible in G with vertex capacities, same value
    good = all(0 <= f[e] <= ecap[e] for e in E)
    for x in range(n):
        if x in (s, t):
            continue
        fin = sum(f[e] for e in E if e[1] == x)
        fout = sum(f[e] for e in E if e[0] == x)
        good &= fin == fout and fin <= vcap[x]
    good &= sum(f[e] for e in E if e[0] == s) - sum(f[e] for e in E if e[1] == s) == val
    lpval, lpx = lp_vertex_maxflow(n, s, t, E, ecap, vcap)
    ok &= good and abs(lpval - val) < 1e-7
    # converse: the LP's (possibly fractional) flow in G maps to a feasible flow in the split graph
    fbar = [sum(lpx[i] for i, e in enumerate(E) if e[1] == u[0]) for (u, v, c) in net[:k]] + list(lpx)
    tol = 1e-7
    bal = {}
    for (u, v, c), x in zip(net, fbar):
        ok_conv &= -tol <= x <= c + tol
        bal[u] = bal.get(u, 0) - x
        bal[v] = bal.get(v, 0) + x
    ok_conv &= all(abs(b) < 1e-6 for x, b in bal.items() if x not in (s, t))
check("11.2 vertex splitting: max flow in the split graph maps back to a feasible flow with vertex capacities of the "
      "same value, equal to the LP optimum in G (300 graphs)", ok)
check("11.2 vertex splitting, converse: a flow in G with vertex capacities (LP optimum) maps to a feasible flow in the "
      "split graph", ok_conv)

# ----------------------------------------------------------------- 11.2 vertex-disjoint paths
ok = True
for trial in range(500):
    n = random.randint(2, 7)
    E = rand_digraph(n, 0.4)
    s, t = 0, n - 1
    adj = {}
    for u, v in E:
        adj.setdefault(u, []).append(v)
    P = [frozenset(p[1:-1]) for p in simple_paths(adj, s, t)]
    brute = max_packing(P, lambda a, b: bool(a & b))
    net, k = split_net(n, s, t, E, {e: 1 for e in E}, {v: 1 for v in range(n)})
    val, fl, _ = maxflow(net, s, t)
    paths = decompose(net, fl, s, t)
    gp = []
    for p in paths:
        q = [x if not isinstance(x, tuple) else x[0] for x in p]
        q = [x for i, x in enumerate(q) if i == 0 or q[i - 1] != x]  # contract v_in v_out
        gp.append(q)
    inner = [x for q in gp for x in q[1:-1]]
    ok &= (val == brute and len(gp) == val and len(inner) == len(set(inner))
           and all(e in set(E) for q in gp for e in zip(q, q[1:])))
check("11.2 vertex-disjoint paths: flow in the unit split graph = max number of internally vertex-disjoint paths "
      "(500 graphs, exhaustive); contracted paths are valid", ok)
# with infinite edge capacities and an edge s->t, the flow would be unbounded (trap)
net, k = split_net(3, 0, 2, [(0, 1), (1, 2), (0, 2)], {(0, 1): INF, (1, 2): INF, (0, 2): INF}, {1: 1})
check("11.2 trap: with infinite edge capacities an edge s->t has no finite cut (unbounded flow)",
      brute_mincut(net, 0, 2) == INF)

# the bowtie of the figure
BOW_E = [("s", "a"), ("s", "b"), ("a", "m"), ("b", "m"), ("m", "c"), ("m", "d"), ("c", "t"), ("d", "t")]
names = ["s", "a", "b", "m", "c", "d", "t"]
idx = {v: i for i, v in enumerate(names)}
Ei = [(idx[u], idx[v]) for u, v in BOW_E]
ev = maxflow([(u, v, 1) for u, v in Ei], 0, 6)[0]
net, k = split_net(7, 0, 6, Ei, {e: 1 for e in Ei}, {v: 1 for v in range(7)})
vv, vf, vS = maxflow(net, 0, 6)
check("figure a11-split: bowtie has 2 edge-disjoint and 1 vertex-disjoint path; m's split edge is a minimum cut",
      ev == 2 and vv == 1 and cut_capacity(net, {0, (1, "in"), (1, "out"), (2, "in"), (2, "out"), (3, "in")}) == 1,
      f"{ev} {vv}")

# trap (review): splitting s and t too. Terminals s_out, t_in: their split-edge capacity is irrelevant.
# Terminals s_in, t_out: capacity 1 there caps the flow at 1; capacity INF is needed.
_rng = random.Random(20)


def split_all(n, s, t, E, st_cap):
    net = [((v, "in"), (v, "out"), st_cap if v in (s, t) else 1) for v in range(n)]
    net += [((u, "out"), (v, "in"), 1) for u, v in E]
    return net


ok_out, ok_in, drops = True, True, 0
for trial in range(300):
    n = _rng.randint(2, 7)
    E = [(u, v) for u in range(n) for v in range(n) if u != v and _rng.random() < 0.4]
    s, t = 0, n - 1
    net0, _ = split_net(n, s, t, E, {e: 1 for e in E}, {v: 1 for v in range(n)})
    ref = maxflow(net0, s, t, rand=False)[0]
    for stc in (1, INF):
        ok_out &= maxflow(split_all(n, s, t, E, stc), (s, "out"), (t, "in"), rand=False)[0] == ref
    ok_in &= maxflow(split_all(n, s, t, E, INF), (s, "in"), (t, "out"), rand=False)[0] == ref
    v1 = maxflow(split_all(n, s, t, E, 1), (s, "in"), (t, "out"), rand=False)[0]
    ok_in &= v1 == min(ref, 1)
    drops += v1 < ref
check("11.2 trap: s, t split too: with terminals s_out, t_in their split capacity (1 or INF) does not change the "
      "flow; with s_in, t_out capacity 1 caps it at 1 and INF is needed (300 graphs)", ok_out and ok_in and drops > 0,
      f"{drops} graphs where capacity 1 at s_in/t_out loses flow")


# =====================================================================================================
# 11.3 bipartite matching
def brute_matching(L, R, E):
    best = 0

    def rec(i, usedR, size):
        nonlocal best
        if size + (len(L) - i) <= best:
            return
        if i == len(L):
            best = max(best, size)
            return
        for (l, r) in E:
            if l == L[i] and r not in usedR:
                usedR.add(r); rec(i + 1, usedR, size + 1); usedR.discard(r)
        rec(i + 1, usedR, size)
    rec(0, set(), 0)
    return best


def matching_net(L, R, E):
    return ([("s", ("L", l), 1) for l in L] + [(("L", l), ("R", r), 1) for l, r in E]
            + [(("R", r), "t", 1) for r in R])


def alternating_path(L, R, E, M):
    """BFS for an alternating path from an unmatched L vertex to an unmatched R vertex; returns the vertex list."""
    mL = {l: r for l, r in M}
    mR = {r: l for l, r in M}
    pred = {}
    Q = deque()
    for l in L:
        if l not in mL:
            pred[("L", l)] = None
            Q.append(("L", l))
    while Q:
        x = Q.popleft()
        side, v = x
        if side == "L":
            for (l, r) in E:
                if l == v and mL.get(l) != r and ("R", r) not in pred:
                    pred[("R", r)] = x
                    if r not in mR:
                        path, y = [], ("R", r)
                        while y is not None:
                            path.append(y); y = pred[y]
                        return path[::-1]
                    Q.append(("R", r))
        else:
            l = mR[v]
            if ("L", l) not in pred:
                pred[("L", l)] = x
                Q.append(("L", l))
    return None


def xor_path(M, path):
    pe = set()
    for a, b in zip(path, path[1:]):
        pe.add((a[1], b[1]) if a[0] == "L" else (b[1], a[1]))
    return set(M) ^ pe


ok_flow, ok_alg, ok_bound = True, True, True
for trial in range(600):
    nl, nr = random.randint(1, 5), random.randint(1, 5)
    L = [f"l{i}" for i in range(nl)]
    R = [f"r{j}" for j in range(nr)]
    E = [(l, r) for l in L for r in R if random.random() < 0.4]
    brute = brute_matching(L, R, E)
    net = matching_net(L, R, E)
    val, fl, _ = maxflow(net, "s", "t")
    M = [(net[i][0][1], net[i][1][1]) for i in range(nl, nl + len(E)) if fl[i] == 1]
    ends = [x for e in M for x in (("L", e[0]), ("R", e[1]))]
    ok_flow &= val == brute == len(M) and len(ends) == len(set(ends))
    ok_bound &= val <= min(nl, nr)
    # the alternating-path algorithm
    Mc, it = set(), 0
    while True:
        p = alternating_path(L, R, E, Mc)
        if p is None:
            break
        new = xor_path(Mc, p)
        ends = [x for e in new for x in (("L", e[0]), ("R", e[1]))]
        ok_alg &= len(new) == len(Mc) + 1 and len(ends) == len(set(ends)) and all(e in E for e in new)
        Mc, it = new, it + 1
    ok_alg &= len(Mc) == brute and it == brute
check("11.3: max flow in s->L->R->t = maximum matching (exhaustive), read-off edges form a matching (600 graphs)",
      ok_flow)
check("11.3: |f*| <= min(|L|, |R|)", ok_bound)
check("11.3: AlternatingPathMatching gains one edge per iteration and ends with a maximum matching", ok_alg)

# Berge: M maximum iff no alternating path (all matchings of small random graphs; paths found exhaustively)
ok, tested = True, 0


def has_alt_path_exhaustive(L, R, E, M):
    mL = {l: r for l, r in M}
    mR = {r: l for l, r in M}

    def rec(l, seenR, seenL):
        for (a, r) in E:
            if a == l and mL.get(l) != r and r not in seenR:
                if r not in mR:
                    return True
                l2 = mR[r]
                if l2 not in seenL and rec(l2, seenR | {r}, seenL | {l2}):
                    return True
        return False
    return any(rec(l, set(), {l}) for l in L if l not in mL)


for trial in range(150):
    nl, nr = random.randint(1, 4), random.randint(1, 4)
    L = [f"l{i}" for i in range(nl)]
    R = [f"r{j}" for j in range(nr)]
    E = [(l, r) for l in L for r in R if random.random() < 0.5]
    best = brute_matching(L, R, E)
    for k in range(len(E) + 1):
        for M in itertools.combinations(E, k):
            ends = [x for e in M for x in (("L", e[0]), ("R", e[1]))]
            if len(ends) != len(set(ends)):
                continue
            tested += 1
            ok &= (len(M) == best) == (not has_alt_path_exhaustive(L, R, E, M))
check("11.3 Berge: a matching is maximum iff it has no alternating path (all matchings of 150 graphs)", ok,
      f"{tested} matchings")

# the figure's example
L, R = ["a", "b", "c"], ["x", "y", "z"]
E = [("a", "x"), ("a", "y"), ("b", "x"), ("c", "y"), ("c", "z")]
M0 = {("a", "x"), ("c", "y")}
maximal = all(l in {e[0] for e in M0} or r in {e[1] for e in M0} for l, r in E)
AP = [("L", "b"), ("R", "x"), ("L", "a"), ("R", "y"), ("L", "c"), ("R", "z")]
alt = all(((a[1], b[1]) if a[0] == "L" else (b[1], a[1])) in M0 for a, b in list(zip(AP, AP[1:]))[1::2]) and \
    all(((a[1], b[1]) if a[0] == "L" else (b[1], a[1])) not in M0 for a, b in list(zip(AP, AP[1:]))[0::2])
check("figure a11-matching: {ax, cy} is maximal but not maximum; b x a y c z is alternating; M xor P = {bx, ay, cz}",
      maximal and brute_matching(L, R, E) == 3 and alt and xor_path(M0, AP) == {("b", "x"), ("a", "y"), ("c", "z")})


# =====================================================================================================
# 11.4 tuple selection
def tuple_net(X, cx, cxy):
    net = []
    for i, Xi in enumerate(X):
        for x in Xi:
            net.append((("in", x), ("out", x), cx[x]))
    for w in X[0]:
        net.append(("s", ("in", w), INF))
    for z in X[-1]:
        net.append((("out", z), "t", INF))
    for i in range(len(X) - 1):
        for x in X[i]:
            for y in X[i + 1]:
                if cxy[(x, y)] > 0:
                    net.append((("out", x), ("in", y), cxy[(x, y)]))
    return net


def brute_tuples(X, cx, cxy):
    T = list(itertools.product(*X))
    remx, remp = dict(cx), dict(cxy)
    best = 0

    def rec(i, total):
        nonlocal best
        if i == len(T):
            best = max(best, total)
            return
        tup = T[i]
        pairs = list(zip(tup, tup[1:]))
        k = 0
        rec(i + 1, total)
        while all(remx[x] > 0 for x in tup) and all(remp[p] > 0 for p in pairs):
            for x in tup:
                remx[x] -= 1
            for p in pairs:
                remp[p] -= 1
            k += 1
            rec(i + 1, total + k)
        for x in tup:
            remx[x] += k
        for p in pairs:
            remp[p] += k
    rec(0, 0)
    return best


ok, multi = True, 0
for trial in range(300):
    d = random.randint(2, 3)
    X = [[f"x{i}{j}" for j in range(random.randint(1, 2 if d == 3 else 3))] for i in range(d)]
    cx = {}
    for i, Xi in enumerate(X):
        for x in Xi:
            cx[x] = random.choice([0, 1, 2]) if i == 0 else random.choice([0, 1, 2, INF])
    cxy = {(x, y): random.choice([0, 1, 2, INF]) for i in range(d - 1) for x in X[i] for y in X[i + 1]}
    net = tuple_net(X, cx, cxy)
    val, fl, _ = maxflow(net, "s", "t")
    brute = brute_tuples(X, cx, cxy)
    paths = decompose(net, fl, "s", "t")
    tuples = [tuple(v[1] for v in p[1:-1:2]) for p in paths]
    good = len(tuples) == val and all(len(tp) == d and all(tp[i] in X[i] for i in range(d)) for tp in tuples)
    for x in cx:
        good &= sum(tp.count(x) for tp in tuples) <= cx[x]
    for pr in cxy:
        good &= sum(1 for tp in tuples if pr in set(zip(tp, tp[1:]))) <= cxy[pr]
    multi += len(set(tuples)) < len(tuples)
    ok &= val == brute and good
check("11.4 tuple selection: max flow = maximum number of tuples (exhaustive over multisets), and the decomposition "
      "gives a valid selection (300 instances)", ok, f"{multi} optimal selections repeat a tuple")
net = tuple_net([["x"], ["y"]], {"x": 2, "y": 2}, {("x", "y"): 2})
check("11.4 multiplicity: one possible tuple with all capacities 2 -> flow 2, but only 1 distinct tuple",
      maxflow(net, "s", "t")[0] == 2 and len(list(itertools.product(["x"], ["y"]))) == 1)


# ----------------------------------------------------------------- exam scheduling
def exam_net(n, r, t, p, E, S, A, limit):
    net = [("s'", ("c", i), 1) for i in range(n)]
    net += [(("c", i), ("r", j), INF) for i in range(n) for j in range(r) if E[i] <= S[j]]
    net += [(("r", j), ("t", k), 1) for j in range(r) for k in range(t)]
    net += [(("t", k), ("p", l), 1) for k in range(t) for l in range(p) if A[k][l]]
    net += [(("p", l), "t'", limit) for l in range(p)]
    return net


def exam_valid(sched, n, E, S, A, limit):
    rs, ps, cnt = set(), set(), {}
    for i, (j, k, l) in sched.items():
        if E[i] > S[j] or not A[k][l] or (j, k) in rs or (k, l) in ps:
            return False
        rs.add((j, k)); ps.add((k, l)); cnt[l] = cnt.get(l, 0) + 1
    return all(c <= limit for c in cnt.values())


def exam_brute(n, r, t, p, E, S, A, limit):
    opts = [None] + [(j, k, l) for j in range(r) for k in range(t) for l in range(p)]
    best = 0
    for choice in itertools.product(opts, repeat=n):
        sched = {i: c for i, c in enumerate(choice) if c is not None}
        if len(sched) > best and exam_valid(sched, n, E, S, A, limit):
            best = len(sched)
    return best


ok = True
for trial in range(150):
    n, r, t, p = random.randint(1, 4), random.randint(1, 2), random.randint(1, 2), random.randint(1, 2)
    E = [random.randint(1, 5) for _ in range(n)]
    S = [random.randint(1, 5) for _ in range(r)]
    A = [[random.random() < 0.6 for _ in range(p)] for _ in range(t)]
    limit = random.choice([1, 2, 5])
    net = exam_net(n, r, t, p, E, S, A, limit)
    val, fl, _ = maxflow(net, "s'", "t'")
    paths = decompose(net, fl, "s'", "t'")
    sched = {p_[1][1]: (p_[2][1], p_[3][1], p_[4][1]) for p_ in paths}
    ok &= (val == exam_brute(n, r, t, p, E, S, A, limit) and len(sched) == len(paths) == val
           and exam_valid(sched, n, E, S, A, limit))
check("11.4 exam scheduling: max flow = most classes schedulable (all schedules enumerated), and the decomposition "
      "is a valid schedule (150 instances)", ok)


# =====================================================================================================
# 11.5 disjoint-path covers
def cover_brute(n, E):
    """Fewest paths in a disjoint-path cover of a dag: max edge set with in/out degree <= 1 (paths only)."""
    for k in range(min(len(E), n - 1), -1, -1):
        for F in itertools.combinations(E, k):
            if len({u for u, v in F}) == k and len({v for u, v in F}) == k:
                return n - k
    return n


def cover_by_matching(n, E):
    net = [("s", ("f", u), 1) for u in range(n)] + [(("f", u), ("h", v), 1) for u, v in E] + \
          [(("h", v), "t", 1) for v in range(n)]
    val, fl, _ = maxflow(net, "s", "t")
    Mp = [(u, v) for (a, b, c), f in zip(net, fl) if f and a != "s" and b != "t" for u, v in [(a[1], b[1])]]
    succ = dict(Mp)
    has_pred = {v for u, v in Mp}
    paths = []
    for v in range(n):
        if v not in has_pred:
            p = [v]
            while p[-1] in succ:
                p.append(succ[p[-1]])
            paths.append(p)
    return val, paths


ok = True
for trial in range(400):
    n = random.randint(1, 7)
    E = [(u, v) for u in range(n) for v in range(u + 1, n) if random.random() < 0.35]
    val, paths = cover_by_matching(n, E)
    allv = [v for p in paths for v in p]
    ok &= (cover_brute(n, E) == n - val == len(paths) and sorted(allv) == list(range(n))
           and all(e in set(E) for p in paths for e in zip(p, p[1:])))
check("11.5: minimum disjoint-path cover of a dag (exhaustive) = V - maximum matching in G', and the matching gives "
      "such a cover (400 dags)", ok)
# k paths <-> matching of size V - k, for every edge subset
ok = True
for trial in range(100):
    n = random.randint(1, 5)
    E = [(u, v) for u in range(n) for v in range(u + 1, n) if random.random() < 0.5]
    for k in range(len(E) + 1):
        for F in itertools.combinations(E, k):
            is_cover = len({u for u, v in F}) == k and len({v for u, v in F}) == k
            ends = [("f", u) for u, v in F] + [("h", v) for u, v in F]
            is_matching = len(ends) == len(set(ends))
            ok &= is_cover == is_matching
check("11.5: an edge set is a disjoint-path cover (with V - |F| paths) iff its flat/sharp copy is a matching", ok)
# cycles break it
check("11.5 trap: 2-cycle u->v->u has a matching of size 2 but needs 1 path (V - 2 = 0 is wrong)",
      cover_by_matching(2, [(0, 1), (1, 0)])[0] == 2)

# the figure's dag
PV = "abcdef"
PE = [("a", "c"), ("a", "f"), ("b", "d"), ("c", "d"), ("c", "e"), ("d", "f")]
ix = {v: i for i, v in enumerate(PV)}
Ei = [(ix[u], ix[v]) for u, v in PE]
val, paths = cover_by_matching(6, Ei)
adj = {}
for u, v in Ei:
    adj.setdefault(u, []).append(v)
allp = [p for s_ in range(6) for t_ in range(6) for p in simple_paths(adj, s_, t_)]
longest = max(len(p) for p in allp)
lps = [p for p in allp if len(p) == longest]
rest = [v for v in range(6) if v not in lps[0]]
restE = [(u, v) for u, v in Ei if u in rest and v in rest]
greedy = 1 + cover_brute(len(rest), [(rest.index(u), rest.index(v)) for u, v in restE])
check("figure a11-path-cover: min cover 2 = 6 - 4 with paths a c e, b d f; the unique longest path a c d f leaves "
      "b, e and gives 3 paths",
      val == 4 and cover_brute(6, Ei) == 2 and sorted("".join(PV[v] for v in p) for p in paths) == ["ace", "bdf"]
      and len(lps) == 1 and "".join(PV[v] for v in lps[0]) == "acdf" and greedy == 3, str(paths))


# ----------------------------------------------------------------- minimal faculty hiring
def compat(C, T, i, j):
    return C[j][0] >= C[i][1] + T[C[i][2]][C[j][2]]


def partitions(items):
    if not items:
        yield []
        return
    first, rest = items[0], items[1:]
    for p in partitions(rest):
        yield [[first]] + p
        for k in range(len(p)):
            yield p[:k] + [[first] + p[k]] + p[k + 1:]


def profs_brute(C, T, mode):
    n = len(C)
    best = n
    for part in partitions(list(range(n))):
        if len(part) >= best:
            continue
        good = True
        for grp in part:
            g = sorted(grp, key=lambda i: C[i][0])
            pairs = list(itertools.combinations(g, 2)) if mode == "all" else list(zip(g, g[1:]))
            if not all(compat(C, T, i, j) for i, j in pairs):
                good = False
                break
        if good:
            best = len(part)
    return best


def profs_flow(C, T):
    n = len(C)
    E = [(i, j) for i in range(n) for j in range(n) if i != j and compat(C, T, i, j)]
    # dag check: compatibility goes strictly forward in start time
    acyclic = all(C[j][0] > C[i][0] for i, j in E)
    return n - cover_by_matching(n, E)[0], acyclic


ok_metric, ok_consec, ok_dag = True, True, True
for trial in range(250):
    n = random.randint(2, 6)
    m = random.randint(1, 3)
    if random.random() < 0.5:
        X = [random.randint(0, 5) for _ in range(m)]
        T = [[abs(X[u] - X[v]) for v in range(m)] for u in range(m)]
        metric = True
    else:
        T = [[0 if u == v else random.randint(0, 6) for v in range(m)] for u in range(m)]
        metric = all(T[u][w] <= T[u][v] + T[v][w] for u in range(m) for v in range(m) for w in range(m))
    C = []
    for _ in range(n):
        st = random.randint(0, 12)
        C.append((st, st + random.randint(1, 3), random.randrange(m)))
    fl, acyclic = profs_flow(C, T)
    ok_dag &= acyclic
    ok_consec &= fl == profs_brute(C, T, "consecutive")
    if metric:
        ok_metric &= fl == profs_brute(C, T, "all")
check("11.5 faculty hiring: path-cover answer = fewest professors with the condition on consecutive classes "
      "(all partitions, 250 instances)", ok_consec)
check("11.5 faculty hiring: with walking times obeying the triangle inequality it also equals the all-pairs version",
      ok_metric)
check("11.5 faculty hiring: positive class lengths make the compatibility graph a dag", ok_dag)
C3 = [(0, 1, 0), (1, 2, 1), (2, 3, 2)]
T3 = [[0, 0, 100], [0, 0, 0], [100, 0, 0]]
check("11.5 precision: without the triangle inequality the all-pairs reading can need more professors (1 vs 2)",
      profs_flow(C3, T3)[0] == 1 and profs_brute(C3, T3, "all") == 2)


# =====================================================================================================
# 11.6 baseball elimination
def can_win_brute(W, G, full):
    """Can the last team finish with the most wins (ties allowed)? full=True also enumerates its own games."""
    n = len(W)
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n) if G[i][j] and (full or j != n - 1)]
    base = list(W)
    if not full:
        base[n - 1] += sum(G[n - 1])
    for split in itertools.product(*[range(G[i][j] + 1) for i, j in pairs]):
        w = list(base)
        for (i, j), k in zip(pairs, split):
            w[i] += k
            w[j] += G[i][j] - k
        if w[n - 1] >= max(w):
            return True
    return False


def baseball_net(W, G, Rn):
    n = len(W)
    net = []
    for i in range(n - 1):
        for j in range(i + 1, n - 1):
            if G[i][j]:
                net.append(("s", ("g", i, j), G[i][j]))
                net.append((("g", i, j), ("t", i), INF))
                net.append((("g", i, j), ("t", j), INF))
    for i in range(n - 1):
        net.append((("t", i), "t", W[n - 1] + Rn - W[i]))
    return net


def flow_test(W, G, Rn):
    n = len(W)
    if any(W[i] > W[n - 1] + Rn for i in range(n - 1)):
        return False, None
    net = baseball_net(W, G, Rn)
    val, fl, S = maxflow(net, "s", "t")
    total = sum(G[i][j] for i in range(n - 1) for j in range(i + 1, n - 1))
    return val == total, S


def certificate_exists(W, G, best):
    n = len(W)
    for r in range(1, n):
        for Q in itertools.combinations(range(n - 1), r):
            if sum(W[i] for i in Q) + sum(G[i][j] for i, j in itertools.combinations(Q, 2)) > r * best:
                return Q
    return None


ok_flow, ok_wlog, ok_cert, ok_cut, elim = True, True, True, True, 0
for trial in range(500):
    n = random.randint(2, 5)
    W = [random.randint(0, 10) for _ in range(n)]
    G = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            G[i][j] = G[j][i] = random.randint(0, 2 if n <= 4 else 1)
    Rn = sum(G[n - 1])
    b_full = can_win_brute(W, G, True)
    b_wlog = can_win_brute(W, G, False)
    ok_wlog &= b_full == b_wlog
    ft, S = flow_test(W, G, Rn)
    ok_flow &= ft == b_full
    Q = certificate_exists(W, G, W[n - 1] + Rn)
    ok_cert &= (Q is None) == b_full
    if not b_full:
        elim += 1
        if S is not None:
            Qc = [i for i in range(n - 1) if ("t", i) in S]
            lhs = sum(W[i] for i in Qc) + sum(G[i][j] for i, j in itertools.combinations(Qc, 2))
            ok_cut &= lhs > len(Qc) * (W[n - 1] + Rn)
check("11.6: team n may be assumed to win all its games (same answer with all its outcomes enumerated, 500 leagues)",
      ok_wlog)
check("11.6 theorem: team n can finish first iff the max flow saturates every game edge (all outcomes enumerated)",
      ok_flow, f"{elim} eliminated")
check("11.6 certificate: eliminated iff some set Q has wins + mutual games > |Q|(W[n] + R[n])", ok_cert)
check("11.6 certificate: the team vertices on the source side of the residual minimum cut form such a Q", ok_cut)

# Detroit, August 30, 1996
TEAMS = ["NYY", "BAL", "BOS", "TOR", "DET"]
WON = [75, 71, 69, 63, 49]
LOST = [59, 63, 66, 72, 86]
LEFT = [28, 28, 27, 27, 27]
TAB = [[0, 3, 8, 7, 3], [3, 0, 2, 7, 4], [8, 2, 0, 0, 0], [7, 7, 0, 0, 0], [3, 4, 0, 0, 0]]
check("Detroit table: games-left matrix is symmetric", all(TAB[i][j] == TAB[j][i] for i in range(5) for j in range(5)))
Rn = LEFT[4]
best = WON[4] + Rn
caps = [best - WON[i] for i in range(4)]
games = sum(TAB[i][j] for i in range(4) for j in range(i + 1, 4))
Gd = [row[:4] + [0] for row in TAB[:4]] + [[0] * 5]
val, fl, S = maxflow(baseball_net(WON, Gd, Rn), "s", "t")
check("Detroit: 49 + 27 = 76; capacities 1, 5, 7, 13 (sum 26); 3+8+7+2+7 = 27 games among rivals; max flow 26",
      best == 76 and caps == [1, 5, 7, 13] and sum(caps) == 26 and games == 27 and val == 26
      and [TAB[i][j] for i, j in [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]] == [3, 8, 7, 2, 7, 0])
check("Detroit: 20 of its 27 remaining games are outside the division (3 + 4 inside)",
      Rn - sum(TAB[4][:4]) == 20 and sum(TAB[4][:4]) == 7)
# brute force over the 27 rival games: none keeps every rival at <= 76 wins
pairs = [(i, j) for i in range(4) for j in range(i + 1, 4) if TAB[i][j]]
possible = False
count = 0
for split in itertools.product(*[range(TAB[i][j] + 1) for i, j in pairs]):
    count += 1
    w = WON[:4]
    w = list(w)
    for (i, j), k in zip(pairs, split):
        w[i] += k
        w[j] += TAB[i][j] - k
    if max(w) <= best:
        possible = True
check("Detroit is eliminated: no outcome of the rivals' games keeps all of them at <= 76 wins", not possible and
      count == 4 * 9 * 8 * 3 * 8, str(count))
Qcut = [TEAMS[i] for i in range(4) if ("t", i) in S]
cert = [Q for r in range(1, 5) for Q in itertools.combinations(range(4), r)
        if sum(WON[i] for i in Q) + sum(TAB[i][j] for i, j in itertools.combinations(Q, 2)) > r * best]
check("Detroit certificate: Q = all four rivals (278 + 27 = 305 > 304) is the only one, and the residual cut finds it",
      cert == [(0, 1, 2, 3)] and sum(WON[:4]) == 278 and 278 + 27 == 305 and 4 * 76 == 304
      and Qcut == ["NYY", "BAL", "BOS", "TOR"])
# the footnote example: rivals A, B, C at 8, 8, 0; A-B 5, A-C 1, B-C 1; team n at 7 with 2 games vs C
Wf = [8, 8, 0, 7]
Gf = [[0, 5, 1, 0], [5, 0, 1, 0], [1, 1, 0, 2], [0, 0, 2, 0]]
Rf = sum(Gf[3])
capf = [Wf[3] + Rf - Wf[i] for i in range(3)]
gamesf = sum(Gf[i][j] for i in range(3) for j in range(i + 1, 3))
check("footnote example: capacities 1 + 1 + 9 = 11 >= 7 games, yet eliminated (Q = {A, B}: 21 > 18; a rival reaches 11)",
      Rf == 2 and capf == [1, 1, 9] and sum(capf) == 11 and gamesf == 7 and not can_win_brute(Wf, Gf, True)
      and not flow_test(Wf, Gf, Rf)[0] and 8 + 8 + 5 == 21 and 2 * 9 == 18 and math.ceil(21 / 2) == 11)


# =====================================================================================================
# 11.7 project selection
def proj_net(profit, deps):
    net = [("s", v, p) for v, p in profit.items() if p > 0]
    net += [(u, "t", -p) for u, p in profit.items() if p < 0]
    net += [(u, v, INF) for u, v in deps]
    return net


def closed(X, deps):
    return all(u not in X or v in X for u, v in deps)


ok, ok_id = True, True
for trial in range(400):
    n = random.randint(1, 8)
    V = list(range(n))
    deps = [(u, v) for u in V for v in V if u != v and random.random() < 0.2]
    profit = {v: random.randint(-6, 6) for v in V}
    best = max(sum(profit[v] for v in X) for r in range(n + 1) for X in itertools.combinations(V, r)
               if closed(set(X), deps))
    net = proj_net(profit, deps)
    P = sum(p for p in profit.values() if p > 0)
    val, fl, S = maxflow(net, "s", "t")
    X = S - {"s"}
    ok &= P - val == best and closed(X, deps) and sum(profit[v] for v in X) == best
    if n <= 6:
        for r in range(n + 1):
            for Xs in itertools.combinations(V, r):
                Xs = set(Xs)
                capc = cut_capacity(net, Xs | {"s"})
                ok_id &= (capc < INF) == closed(Xs, deps)
                if capc < INF:
                    ok_id &= capc == P - sum(profit[v] for v in Xs)
check("11.7: P - min cut = best profit over all valid sets, and the residual source side is a best valid set "
      "(400 instances, cycles allowed)", ok)
check("11.7: a cut is finite iff its source side is valid, and then its capacity is P - profit", ok_id)
# the book's example
PROFIT = {"A": -2, "B": -3, "C": -5, "D": -8, "p4": 4, "p6": 6, "p2": 2, "p3": 3}
DEPS = [("B", "A"), ("p4", "A"), ("p4", "B"), ("p6", "B"), ("p6", "p2"), ("p2", "C"), ("p3", "C"), ("p3", "D")]
net = proj_net(PROFIT, DEPS)
val, fl, S = maxflow(net, "s", "t")
allsets = sorted(((sum(PROFIT[v] for v in X), frozenset(X)) for r in range(9)
                  for X in itertools.combinations(PROFIT, r) if closed(set(X), DEPS)), key=lambda x: -x[0])
cut = sorted((u, v) for u, v, c in net if u in S and v not in S)
check("book example: P = 15, min cut 13 (2 + 3 + 5 + 3), best set {4, 6, 2, -2, -3, -5} with profit 2, unique; "
      "next best 0",
      sum(p for p in PROFIT.values() if p > 0) == 15 and val == 13 and S - {"s"} == {"p4", "p6", "p2", "A", "B", "C"}
      and allsets[0][0] == 2 and allsets[1][0] < 2 and allsets[1][0] == 0
      and cut == sorted([("A", "t"), ("B", "t"), ("C", "t"), ("s", "p3")]), f"{allsets[:3]}")
# trap (review): reversed infinite edges. u needs v, p(u) = 5, p(v) = -1: the right network takes both (profit 4);
# reversed, the cut takes u without its prerequisite v, and taking v forces u.
rnet = [("s", "u", 5), ("v", "t", 1), ("v", "u", INF)]
rval, _, rS = maxflow(rnet, "s", "t", rand=False)
cval, _, cS = maxflow(proj_net({"u": 5, "v": -1}, [("u", "v")]), "s", "t", rand=False)
check("11.7 trap: reversed infinite edges select a project without its prerequisite and forbid a prerequisite "
      "without its dependents",
      rS - {"s"} == {"u"} and not closed({"u"}, [("u", "v")]) and cut_capacity(rnet, {"s", "v"}) == INF
      and cS - {"s"} == {"u", "v"} and 5 - cval == 4)


# =====================================================================================================
# concept pages
# reviewer assignment
def reviewer(limits):
    papers = ["P1", "P2", "P3"]
    ok_ = {"A": ["P1", "P2"], "B": ["P1", "P3"], "C": ["P2", "P3"]}
    net = [("s", p, 2) for p in papers] + [(p, j, 1) for j in ok_ for p in ok_[j]] + \
          [(j, "t", limits[j]) for j in ok_]
    val = maxflow(net, "s", "t")[0]
    pairs = [(p, j) for j in ok_ for p in ok_[j]]
    bestb = 0
    for k in range(len(pairs) + 1):
        for F in itertools.combinations(pairs, k):
            if all(sum(1 for p, j in F if p == q) <= 2 for q in papers) and \
                    all(sum(1 for p, j in F if j == r) <= limits[r] for r in ok_):
                bestb = max(bestb, k)
    return val, bestb


v1, b1 = reviewer({"A": 2, "B": 2, "C": 2})
v2, b2 = reviewer({"A": 2, "B": 2, "C": 1})
asg = {"P1": ["A", "B"], "P2": ["A", "C"], "P3": ["B", "C"]}
check("flow-reductions example: max flow 6 = 2*3 with limits 2, 2, 2 (assignment valid); 5 < 6 when C's limit is 1",
      v1 == b1 == 6 and v2 == b2 == 5
      and all(sum(1 for p in asg if j in asg[p]) <= 2 for j in "ABC")
      and all(p in {"A": ["P1", "P2"], "B": ["P1", "P3"], "C": ["P2", "P3"]}[j] for p in asg for j in asg[p]))
# bipartite matching example
L, R = ["1", "2", "3", "4"], ["A", "B", "C"]
E = [("1", "A"), ("1", "B"), ("2", "A"), ("2", "C"), ("3", "C"), ("4", "C")]
greedy, uL, uR = [], set(), set()
for l, r in E:
    if l not in uL and r not in uR:
        greedy.append((l, r)); uL.add(l); uR.add(r)
maximal = all(l in uL or r in uR for l, r in E)
AP = [("L", "3"), ("R", "C"), ("L", "2"), ("R", "A"), ("L", "1"), ("R", "B")]
net = matching_net(L, R, E)
val, fl, S = maxflow(net, "s", "t")
cutE = sorted((str(u), str(v)) for u, v, c in net if u in S and v not in S)
check("bipartite-matching example: greedy gives {1A, 2C} (maximal); 3 C 2 A 1 B switches to {1B, 2A, 3C}; maximum 3; "
      "residual source side {s, 3, 4, C}, cut s->1, s->2, C->t",
      greedy == [("1", "A"), ("2", "C")] and maximal and xor_path(set(greedy), AP) == {("1", "B"), ("2", "A"), ("3", "C")}
      and val == brute_matching(L, R, E) == 3 and S == {"s", ("L", "3"), ("L", "4"), ("R", "C")}
      and cutE == sorted([("s", "('L', '1')"), ("s", "('L', '2')"), ("('R', 'C')", "t")]), str(cutE))


# =====================================================================================================
# page text: headings, meta line, numbers
page = read(PAGE)
heads = re.findall(r"^## (.*)$", page, re.M)
want = ["11.1 Edge-disjoint paths", "11.2 Vertex capacities and vertex-disjoint paths", "11.3 Bipartite matching",
        "11.4 Tuple selection", "11.5 Disjoint-path covers", "11.6 Baseball elimination", "11.7 Project selection",
        "All the reductions at a glance", "Summary"]
check("page: fixed ## headings in order", heads == want, str(heads))
check("page: frontmatter title, tags, chapter",
      'title: "Chapter 11 — Applications of flows and cuts"' in page and "tags: [chapter, algorithms, flows]" in page
      and "\nchapter: 11\n" in page)
check("page: meta line", "*Algorithms, Chapter 11 · book pp. 353–378 · [chapter PDF](https://jeffe.cs.illinois.edu/"
      "teaching/algorithms/book/11-maxflowapps.pdf) · prev: [[2-algorithms/10-maximum-flows-and-minimum-cuts|Chapter 10]]"
      " · next: [[2-algorithms/12-np-hardness|Chapter 12]] · exercises: [[2-algorithms/11-applications-of-flows-and-"
      "cuts-exercises|solved exercises]]*" in page)
for s_ in ["$76-75 = 1$", "$76-71 = 5$", "$76-69 = 7$", "$76-63 = 13$", "in total 26", "$3+8+7+2+7 = 27$",
           "$W[n]+R[n] = 49 + 27 = 76$", "include 20 against teams outside", "$75+71+69+63 = 278$", "make 305 wins",
           "$4\\cdot 76 = 304$", "$1 + 1 + 9 = 11\\ge 7$", "$8 + 8 + 5 = 21 > 2\\cdot 9 = 18$", "at least 11 wins",
           "$P = 4+6+2+3 = 15$", "capacity 13", "$2+3+5$", "$15 - 13 = 2$", "every other valid set earns at most 0",
           "$V = n + r + t + p + 2 = O(N)$", "$E = O(nr + rt + tp) = O(N^2)$", "**$O(N^3)$**", "$O(VE) = O(n^4)$",
           "$O(VE) = O(n^3)$", "$\\lvert f^*\\rvert\\le V-1$", "$\\lvert f^*\\rvert\\le\\min(\\lvert L\\rvert,"
           "\\lvert R\\rvert)\\le V/2$", "$O(\\sqrt{V}\\,E)$", "3 paths instead of 2", "| New York Yankees | 75–59 | 28 | | 3 | 8 | 7 | 3 |",
           "| Baltimore Orioles | 71–63 | 28 | 3 | | 2 | 7 | 4 |", "| Boston Red Sox | 69–66 | 27 | 8 | 2 | | 0 | 0 |",
           "| Toronto Blue Jays | 63–72 | 27 | 7 | 7 | 0 | | 0 |", "| Detroit Tigers | 49–86 | 27 | 3 | 4 | 0 | 0 | |",
           "let you take a project without its prerequisites but force you to take every project that needs a "
           "selected one", "With $s_{\\text{in}}$ and $t_{\\text{out}}$ instead, those split edges need capacity "
           "$\\infty$"]:
    check(f"page states: {s_}", s_ in page)
check("Detroit table won–lost matches the data", all(f"{WON[i]}–{LOST[i]} | {LEFT[i]}" in page for i in range(5)))
for fig in ["a11-split", "a11-matching", "a11-path-cover", "a11-baseball", "a11-projects"]:
    html = read(os.path.join(FIGS, fig + ".html")).strip()
    check(f"figure {fig} is inlined after its marker", f"<!-- fig:{fig} -->\n{html}" in page)

# figure labels
fig = lambda n: read(os.path.join(FIGS, n + ".html"))
check("figure labels: split", "c(m) = 1" in fig("a11-split") and "maximum flow 1" in fig("a11-split")
      and "2 edge-disjoint paths, both through m" in fig("a11-split"))
check("figure labels: matching", "flow of value 3 = matching {bx, ay, cz}" in fig("a11-matching")
      and "M = {ax, cy};  path b x a y c z" in fig("a11-matching"))
check("figure labels: path cover", "6 − 4 = 2 paths" in fig("a11-path-cover") and "cover: a c e and b d f" in
      fig("a11-path-cover") and "<i>a c d f</i>" in fig("a11-path-cover"))
check("figure labels: baseball", "into t: 1 + 5 + 7 + 13 = 26" in fig("a11-baseball") and "out of s: 27 games" in
      fig("a11-baseball") and all(f">{g}<" in fig("a11-baseball") for g in ["3", "8", "7", "2"]))
check("figure labels: projects", "cut 2 + 3 + 5 + 3 = 13" in fig("a11-projects") and "P = 15, profit 15 − 13 = 2" in
      fig("a11-projects"))

# concept pages
for slug in ["flow-reductions", "bipartite-matching"]:
    c = read(os.path.join(CONCEPTS, slug + ".md"))
    check(f"concept {slug}: tags and Related last",
          "tags: [concept, algorithms, flows]" in c and c.rstrip().split("\n")[-1].startswith("Related:"))
c = read(os.path.join(CONCEPTS, "flow-reductions.md"))
check("flow-reductions states the example numbers", "$6 = 2\\cdot 3$" in c and "$2+2+1 = 5 < 6$" in c)
c = read(os.path.join(CONCEPTS, "bipartite-matching.md"))
check("bipartite-matching states the example", "$\\{1A, 2C\\}$" in c and "$\\{1B, 2A, 3C\\}$" in c
      and "$\\{s, 3, 4, C\\}$" in c and "capacity 3" in c)

allal = []
for root, _, files in os.walk(os.path.join(ROOT, "content")):
    for fn in files:
        if fn.endswith(".md"):
            m = re.search(r"^aliases: \[(.*)\]$", read(os.path.join(root, fn)), re.M)
            if m:
                allal += [a.strip().strip('"').lower() for a in m.group(1).split(",")]
dups = sorted({a for a in allal if allal.count(a) > 1})
check("aliases are unique site-wide", not dups, str(dups))

print()
if FAIL:
    print(f"{len(FAIL)} FAILED:", *FAIL, sep="\n  ")
    sys.exit(1)
print("ALL OK")
