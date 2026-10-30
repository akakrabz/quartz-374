#!/usr/bin/env python3
"""Checks for every concrete claim on content/2-algorithms/10-maximum-flows-and-minimum-cuts.md and the concept pages
maximum-flow and ford-fulkerson.

The page's definitions are transcribed literally — value, net flow, feasibility, cut capacity, residual capacity
(three cases), augmentation (three cases) — and FordFulkerson is implemented line for line with three path rules: any
path (a randomized whatever-first search), the fattest path (Dijkstra-style best-first search with min/max) and the
shortest path (breadth-first search, Edmonds–Karp). On thousands of random small networks the result is compared with
a brute-force minimum cut over all S containing s and not t; every lemma and bound the page states is checked at run
time (Lemma 10.1 on every intermediate flow and every cut, the augmentation lemma, the integrality theorem, the
iteration bounds |f*|, E ln|f*| and EV, Lemmas 10.2 and 10.3, the residual-maximum-flow identity, the smallest
minimum cut). The flow-decomposition algorithm of §10.5 is implemented and checked on random flows, circulations and
acyclic flows. Then every example on the pages — the book's network and its flow, residual graph, augmenting path and
cut; Edmonds and Karp's bad example; Zwick's irrational network, simulated in exact arithmetic over Q(sqrt 5); the
decomposition of the book's Figure 10.9 flow; the concept-page examples — is recomputed and compared with the numbers
printed on the pages and in the figures."""
import heapq
import itertools
import math
import os
import random
import re
import sys
from collections import deque
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
PAGE = os.path.join(ROOT, "content", "2-algorithms", "10-maximum-flows-and-minimum-cuts.md")
CONCEPTS = os.path.join(ROOT, "content", "concepts")
FIGS = os.path.join(HERE, "..", "figs")
FAIL = []
random.seed(10374)
INF = math.inf


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAIL.append(name)


def read(path):
    return open(path, encoding="utf-8").read()


# =====================================================================================================
# Networks: V = list of vertices, E = list of directed edges (u, v) (no loops; "reduced" = no antiparallel pair),
# c = dict edge -> capacity. A flow is a dict edge -> number.

def value(E, f, s):
    """|f| = sum_w f(s->w) - sum_u f(u->s)  (page §10.1)."""
    return sum(f[e] for e in E if e[0] == s) - sum(f[e] for e in E if e[1] == s)


def net_out(E, f, v):
    """∂f(v) = net flow out of v (page §10.1)."""
    return sum(f[e] for e in E if e[0] == v) - sum(f[e] for e in E if e[1] == v)


def is_flow(V, E, f, s, t):
    return all(net_out(E, f, v) == 0 for v in V if v not in (s, t))


def feasible(E, c, f):
    return all(0 <= f[e] <= c[e] for e in E)


def cut_capacity(E, c, S):
    return sum(c[e] for e in E if e[0] in S and e[1] not in S)


def all_cuts(V, s, t):
    others = [v for v in V if v not in (s, t)]
    for k in range(len(others) + 1):
        for X in itertools.combinations(others, k):
            yield frozenset((s,) + X)


def brute_min_cut(V, E, c, s, t):
    best, arg = None, []
    for S in all_cuts(V, s, t):
        cap = cut_capacity(E, c, S)
        if best is None or cap < best:
            best, arg = cap, [S]
        elif cap == best:
            arg.append(S)
    return best, arg


def reduced(E):
    Es = set(E)
    return all((v, u) not in Es for (u, v) in E) and all(u != v for (u, v) in E)


def residual(V, E, c, f):
    """c_f on ordered pairs, page §10.3 (reduced network): c - f forward, f backward, 0 otherwise.
    Returns the dict of pairs with positive residual capacity (the edges of G_f)."""
    Es = set(E)
    r = {}
    for u in V:
        for v in V:
            if u == v:
                continue
            if (u, v) in Es:
                cf = c[(u, v)] - f[(u, v)]
            elif (v, u) in Es:
                cf = f[(v, u)]
            else:
                cf = 0
            if cf > 0:
                r[(u, v)] = cf
    return r


def out_adj(V, r):
    adj = {v: [] for v in V}
    for (u, v) in r:
        adj[u].append(v)
    return adj


def reach(V, r, s):
    adj = out_adj(V, r)
    seen, stack = {s}, [s]
    while stack:
        u = stack.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                stack.append(v)
    return seen


def bfs_levels(V, r, s):
    adj = out_adj(V, r)
    lev = {v: INF for v in V}
    lev[s] = 0
    Q = deque([s])
    while Q:
        u = Q.popleft()
        for v in adj[u]:
            if lev[v] == INF:
                lev[v] = lev[u] + 1
                Q.append(v)
    return lev


# ----------------------------------------------------------------------------------- path rules
def path_any(V, r, s, t, rng):
    """'any path from s to t in G_f': whatever-first search with a random bag."""
    adj = out_adj(V, r)
    for v in adj:
        rng.shuffle(adj[v])
    pred = {s: None}
    bag = [s]
    while bag:
        u = bag.pop(rng.randrange(len(bag)))
        for v in adj[u]:
            if v not in pred:
                pred[v] = u
                bag.append(v)
    if t not in pred:
        return None
    P, x = [t], t
    while pred[x] is not None:
        x = pred[x]
        P.append(x)
    return P[::-1]


def path_bfs(V, r, s, t, rng=None):
    """Shortest augmenting path: breadth-first search in G_f (vertex order = V, edge order = V)."""
    adj = {u: [v for v in V if (u, v) in r] for u in V}
    pred = {s: None}
    Q = deque([s])
    while Q:
        u = Q.popleft()
        for v in adj[u]:
            if v not in pred:
                pred[v] = u
                Q.append(v)
    if t not in pred:
        return None
    P, x = [t], t
    while pred[x] is not None:
        x = pred[x]
        P.append(x)
    return P[::-1]


def path_fattest(V, r, s, t, rng=None):
    """Fattest path: Dijkstra with b(v) = max over u->v of min{b(u), c_f(u->v)} and a max-priority queue."""
    adj = {u: [v for v in V if (u, v) in r] for u in V}
    b = {v: 0 for v in V}
    pred = {v: None for v in V}
    b[s] = INF
    pq = [(-INF, 0, s)]
    done = set()
    cnt = 1
    while pq:
        nb, _, u = heapq.heappop(pq)
        if u in done:
            continue
        done.add(u)
        for v in adj[u]:
            nbv = min(b[u], r[(u, v)])
            if nbv > b[v] and v not in done:
                b[v] = nbv
                pred[v] = u
                heapq.heappush(pq, (-nbv, cnt, v))
                cnt += 1
    if b[t] == 0:
        return None
    P, x = [t], t
    while x != s:
        x = pred[x]
        P.append(x)
    return P[::-1]


def max_bottleneck_brute(V, r, s, t):
    """max over all simple s-t paths in G_f of the minimum residual capacity."""
    best = 0
    adj = out_adj(V, r)

    def dfs(u, seen, bott):
        nonlocal best
        if u == t:
            best = max(best, bott)
            return
        for v in adj[u]:
            if v not in seen:
                dfs(v, seen | {v}, min(bott, r[(u, v)]))
    dfs(s, {s}, INF)
    return best


def augment(E, f, P, F):
    """Page §10.3/§10.4: +F on forward edges of P, -F on the edge reversed by a backward edge of P."""
    Es = set(E)
    g = dict(f)
    for (u, v) in zip(P, P[1:]):
        if (u, v) in Es:
            g[(u, v)] += F
        else:
            g[(v, u)] -= F
    return g


def ford_fulkerson(V, E, c, s, t, rule, rng=None, max_iter=10 ** 6, trace=None):
    """FordFulkerson as written on the page; returns (f, number of augmentations)."""
    f = {e: 0 for e in E}
    it = 0
    while True:
        r = residual(V, E, c, f)
        P = rule(V, r, s, t, rng)
        if P is None:
            break
        F = min(r[e] for e in zip(P, P[1:]))
        if trace is not None:
            trace.append((dict(f), r, P, F))
        f = augment(E, f, P, F)
        it += 1
        if it > max_iter:
            raise RuntimeError("no termination")
    if trace is not None:
        trace.append((dict(f), residual(V, E, c, f), None, None))
    return f, it


def random_network(n, p, cmax, rng, allow_anti=False, zero_prob=0.1):
    V = ["s"] + [f"v{i}" for i in range(n - 2)] + ["t"]
    E = []
    pairs = list(itertools.permutations(V, 2))
    rng.shuffle(pairs)
    Es = set()
    for (u, v) in pairs:
        if rng.random() < p and (allow_anti or (v, u) not in Es):
            E.append((u, v))
            Es.add((u, v))
    c = {e: (0 if rng.random() < zero_prob else rng.randint(1, cmax)) for e in E}
    return V, E, c


# =====================================================================================================
print("== Random networks: Ford–Fulkerson (any path), fattest path, Edmonds–Karp vs brute-force minimum cut")
rng = random.Random(1)
stats = dict(nets=0, ff_ok=0, lemma101=0, l101_eq=0, ek_ratio=0.0, ek_iter_ok=0, fat_ok=0, l102=0, l103=0,
             smallest=0, resid_ident=0, bott_ok=0, aug_ok=0, integral=0, ff_iter_ok=0, fat_bound=0)
ok_all = dict((k, True) for k in ["ff", "l101", "l101eq", "netflow", "aug", "integral", "ffiter", "fatbott",
                                  "fatiter", "fatfactor", "ek", "l102", "l103", "ekiter", "smallest", "residmax",
                                  "reach", "sat_avoid", "netout"])
max_ratio = 0.0
max_dis = 0
for trial in range(2500):
    n = rng.randint(2, 7)
    V, E, c = random_network(n, rng.choice([0.3, 0.5, 0.7]), rng.choice([1, 3, 10, 30]), rng)
    s, t = "s", "t"
    assert reduced(E)
    stats["nets"] += 1
    mc, mcs = brute_min_cut(V, E, c, s, t)
    cuts = list(all_cuts(V, s, t))
    for name, rule in (("any", path_any), ("fattest", path_fattest), ("bfs", path_bfs)):
        tr = []
        f, it = ford_fulkerson(V, E, c, s, t, rule, rng, trace=tr)
        val = value(E, f, s)
        if not (val == mc and feasible(E, c, f) and is_flow(V, E, f, s, t)):
            ok_all["ff"] = False
        if not all(isinstance(f[e], int) for e in E):
            ok_all["integral"] = False
        # no augmenting path at the end; S = reach(G_f) is a minimum cut, saturated / avoided
        rF = residual(V, E, c, f)
        S = reach(V, rF, s)
        if t in S or cut_capacity(E, c, S) != val:
            ok_all["reach"] = False
        if not (all(f[e] == c[e] for e in E if e[0] in S and e[1] not in S)
                and all(f[e] == 0 for e in E if e[1] in S and e[0] not in S)):
            ok_all["sat_avoid"] = False
        # smallest minimum cut: S is contained in the source side of every minimum cut
        if not all(S <= set(X) for X in mcs):
            ok_all["smallest"] = False
        # Lemma 10.1, net flow across cuts, ∂f(s) = |f| = -∂f(t) on every intermediate flow
        for (g, r, P, F) in tr:
            vg = value(E, g, s)
            if not (net_out(E, g, s) == vg == -net_out(E, g, t)):
                ok_all["netout"] = False
            for X in cuts:
                out_ = sum(g[e] for e in E if e[0] in X and e[1] not in X)
                in_ = sum(g[e] for e in E if e[1] in X and e[0] not in X)
                if out_ - in_ != vg:
                    ok_all["netflow"] = False
                capX = cut_capacity(E, c, X)
                if vg > capX:
                    ok_all["l101"] = False
                cond = (all(g[e] == c[e] for e in E if e[0] in X and e[1] not in X)
                        and all(g[e] == 0 for e in E if e[1] in X and e[0] not in X))
                if (vg == capX) != cond:
                    ok_all["l101eq"] = False
            # residual maximum flow = |f*| - |f|  (max flow of G_f by brute-force min cut on G_f)
            if P is not None and rule is not path_any:
                Er = list(r.keys())
                mr, _ = brute_min_cut(V, Er, r, s, t)
                if mr != mc - vg:
                    ok_all["residmax"] = False
        # augmentation lemma: f' feasible, |f'| = |f| + F, F a positive integer
        for (g, r, P, F) in tr[:-1]:
            g2 = augment(E, g, P, F)
            if not (feasible(E, c, g2) and is_flow(V, E, g2, s, t) and value(E, g2, s) == value(E, g, s) + F
                    and isinstance(F, int) and F >= 1):
                ok_all["aug"] = False
        if name == "any":
            if it > mc:
                ok_all["ffiter"] = False
        if name == "fattest":
            Ecount = len(E)
            bound = max(1, math.ceil(Ecount * math.log(mc))) if mc >= 1 else 0
            if it > bound:
                ok_all["fatiter"] = False
            for (g, r, P, F) in tr[:-1]:
                if F != max_bottleneck_brute(V, r, s, t):
                    ok_all["fatbott"] = False
                if F * Ecount < mc - value(E, g, s):
                    ok_all["fatfactor"] = False
        if name == "bfs":
            Vn, En = len(V), len(E)
            if it > En * Vn:
                ok_all["ekiter"] = False
            if En * Vn:
                max_ratio = max(max_ratio, it / (En * Vn / 2))
            levels = [bfs_levels(V, r, s) for (g, r, P, F) in tr]
            for i in range(1, len(levels)):
                if any(levels[i][v] < levels[i - 1][v] for v in V):
                    ok_all["l102"] = False
            # Lemma 10.3: count disappearances of every residual edge
            dis = {}
            for i in range(1, len(tr)):
                before, after = set(tr[i - 1][1]), set(tr[i][1])
                P = tr[i - 1][2]
                pe = set(zip(P, P[1:]))
                for e in before - after:
                    dis[e] = dis.get(e, 0) + 1
                    if e not in pe:
                        ok_all["l103"] = False
                if not (before - after):
                    ok_all["l103"] = False  # some edge must disappear in every iteration
            if dis and max(dis.values()) > Vn / 2:
                ok_all["l103"] = False
            max_dis = max([max_dis] + list(dis.values()))
check(f"FF (any path), fattest path and Edmonds–Karp all return a feasible flow of value = brute-force minimum cut "
      f"({stats['nets']} random reduced networks, 2–7 vertices)", ok_all["ff"])
check("every flow is integral (integrality theorem); each augmentation adds an integer F >= 1, f' feasible, "
      "|f'| = |f| + F", ok_all["integral"] and ok_all["aug"])
check("at the end G_f has no s-t path; S = vertices reachable from s is a cut of capacity |f|, its S->T edges "
      "saturated and its T->S edges avoided", ok_all["reach"] and ok_all["sat_avoid"])
check("that S is contained in the source side of every minimum cut (the smallest minimum cut)", ok_all["smallest"])
check("Lemma 10.1 on every intermediate flow and every cut: |f| <= ||S,T||, equality iff saturate S->T and avoid "
      "T->S", ok_all["l101"] and ok_all["l101eq"])
check("net flow across every cut (out of S minus into S) equals |f|; ∂f(s) = |f| = -∂f(t)",
      ok_all["netflow"] and ok_all["netout"])
check("Ford–Fulkerson with integer capacities makes at most |f*| augmentations", ok_all["ffiter"])
check("fattest rule: best-first search finds the maximum-bottleneck path (= brute force over simple paths)",
      ok_all["fatbott"])
check("fattest rule: F >= (|f*| - |f|)/E at every step, and at most max(1, ceil(E ln|f*|)) augmentations",
      ok_all["fatfactor"] and ok_all["fatiter"])
check("the maximum flow of G_f has value |f*| - |f| at every step (brute-force minimum cut of G_f)",
      ok_all["residmax"])
check("Lemma 10.2: BFS levels in the residual graph never decrease (Edmonds–Karp)", ok_all["l102"])
check("Lemma 10.3: an edge disappears only as a bottleneck of the augmenting path, at least one per iteration, "
      f"and each residual edge at most V/2 times (max seen {max_dis})", ok_all["l103"])
check(f"Edmonds–Karp makes at most EV augmentations (largest ratio to the book's EV/2 seen: {max_ratio:.3f})",
      ok_all["ekiter"])

# ------------------------------------------------------------------------------ subdivision (Figure 10.4)
print("== Subdividing edges preserves the maximum flow and the minimum cut")
ok_sub = True
for trial in range(400):
    n = rng.randint(2, 6)
    V, E, c = random_network(n, 0.6, 10, rng, allow_anti=True)
    mc, _ = brute_min_cut(V, E, c, "s", "t")
    V2, E2, c2 = list(V), [], {}
    for i, (u, v) in enumerate(E):
        x = f"x{i}"
        V2.append(x)
        E2 += [(u, x), (x, v)]
        c2[(u, x)] = c2[(x, v)] = c[(u, v)]
    assert reduced(E2)
    mc2, _ = brute_min_cut(V2, E2, c2, "s", "t") if len(V2) <= 16 else (None, None)
    f2, _ = ford_fulkerson(V2, E2, c2, "s", "t", path_bfs)
    if value(E2, f2, "s") != mc or (mc2 is not None and mc2 != mc):
        ok_sub = False
check("400 random networks with antiparallel edges: subdividing every edge gives the same maximum-flow value and "
      "minimum-cut capacity", ok_sub)

# ------------------------------------------------------------------------------ flow decomposition (§10.5)
print("== Flow decomposition")


def decompose(V, E, f, s, t, rng=None):
    """The page's version of §10.5's algorithm: add an edge t->s carrying |f| (needs |f| >= 0); repeatedly start at
    any vertex with positive outflow and follow positive-flow edges (arbitrary choices) until a vertex repeats;
    subtract the cycle's bottleneck; a cycle through the added edge is an s-t path. Returns (kind, vertices, weight)."""
    rng = rng or random.Random(0)
    VIRT = ("t", "s", "virtual")
    g = {e: f[e] for e in E}
    g[VIRT] = value(E, f, s)
    assert g[VIRT] >= 0
    Ev = list(E) + [VIRT]
    out = []
    steps = 0
    while any(g[e] > 0 for e in Ev):
        steps += 1
        if steps > len(Ev) + 1:
            raise RuntimeError("decomposition takes too many steps")
        start = rng.choice([e[0] for e in Ev if g[e] > 0])
        walk, wedges, pos = [start], [], {start: 0}
        while True:
            u = walk[-1]
            cand = [e for e in Ev if e[0] == u and g[e] > 0]
            assert cand, "stuck"
            e = rng.choice(cand)
            v = e[1]
            wedges.append(e)
            if v in pos:
                cyc = wedges[pos[v]:]
                break
            pos[v] = len(walk)
            walk.append(v)
        F = min(g[e] for e in cyc)
        for e in cyc:
            g[e] -= F
        if VIRT in cyc:
            i = cyc.index(VIRT)
            pe = cyc[i + 1:] + cyc[:i]
            out.append(("path", [pe[0][0]] + [e[1] for e in pe], F))
        else:
            out.append(("cycle", [cyc[0][0]] + [e[1] for e in cyc], F))
    return out


def book_decompose(V, E, f, s, t):
    """The book's description (p. 339), literally: walk from s if s has outflow, stopping at t (path) or at a
    repeated vertex (cycle); otherwise walk from any vertex with outflow until a repeat. Returns pieces or 'stuck'."""
    g = {e: f[e] for e in E}
    out = []
    while any(g[e] > 0 for e in E):
        start = s if any(g[e] > 0 for e in E if e[0] == s) else next(e[0] for e in E if g[e] > 0)
        walk, pos = [start], {start: 0}
        while True:
            u = walk[-1]
            if u == t and start == s and len(walk) > 1:
                piece, kind = walk, "path"
                break
            nxt = next((e[1] for e in E if e[0] == u and g[e] > 0), None)
            if nxt is None:
                return "stuck"
            if nxt in pos:
                piece, kind = walk[pos[nxt]:] + [nxt], "cycle"
                break
            pos[nxt] = len(walk)
            walk.append(nxt)
        es = list(zip(piece, piece[1:]))
        F = min(g[e] for e in es)
        for e in es:
            g[e] -= F
        out.append((kind, piece, F))
    return out


def recombine(E, pieces):
    h = {e: 0 for e in E}
    for kind, p, w in pieces:
        for e in zip(p, p[1:]):
            h[e] += w
    return h


def has_cycle(V, E, f):
    adj = {v: [e[1] for e in E if e[0] == v and f[e] > 0] for v in V}
    color = {v: 0 for v in V}

    def dfs(u):
        color[u] = 1
        for v in adj[u]:
            if color[v] == 1 or (color[v] == 0 and dfs(v)):
                return True
        color[u] = 2
        return False
    return any(color[v] == 0 and dfs(v) for v in V)


def simple_paths(V, E, s, t):
    adj = {v: [e[1] for e in E if e[0] == v] for v in V}
    res = []

    def dfs(u, p):
        if u == t:
            res.append(p)
            return
        for v in adj[u]:
            if v not in p:
                dfs(v, p + [v])
    dfs(s, [s])
    return res


def simple_cycles(V, E):
    adj = {v: [e[1] for e in E if e[0] == v] for v in V}
    order = {v: i for i, v in enumerate(V)}
    res = []

    def dfs(start, u, p):
        for v in adj[u]:
            if v == start and len(p) >= 2:
                res.append(p + [start])
            elif v not in p and order[v] > order[start]:
                dfs(start, v, p + [v])
    for v in V:
        dfs(v, v, [v])
    return res


ok_dec, ok_circ, ok_acyc, ok_support, ok_lin = True, True, True, True, True
for trial in range(1500):
    n = rng.randint(2, 7)
    V, E, c = random_network(n, 0.5, 10, rng, allow_anti=rng.random() < 0.3)
    s, t = "s", "t"
    P = simple_paths(V, E, s, t)
    C = simple_cycles(V, E)
    mode = rng.choice(["mixed", "circ", "acyc"])
    pieces = []
    if mode in ("mixed", "acyc"):
        pieces += [("path", p, rng.randint(1, 5)) for p in P if rng.random() < 0.5]
    if mode in ("mixed", "circ"):
        pieces += [("cycle", cy, rng.randint(1, 5)) for cy in C if rng.random() < 0.5]
    f = recombine(E, pieces)
    if mode == "acyc" and has_cycle(V, E, f):
        continue
    if not is_flow(V, E, f, s, t):
        ok_dec = False
        continue
    d = decompose(V, E, f, s, t, rng)
    nf = sum(1 for e in E if f[e] > 0)
    h = recombine(E, d)
    if h != f or len(d) > nf:
        ok_dec = False
    used = {e for kind, p, w in d for e in zip(p, p[1:])}
    if used != {e for e in E if f[e] > 0} or any(w <= 0 for _, _, w in d):
        ok_support = False
    for kind, p, w in d:
        if kind == "path" and not (p[0] == s and p[-1] == t and len(set(p)) == len(p)):
            ok_dec = False
        if kind == "cycle" and not (p[0] == p[-1] and len(set(p[:-1])) == len(p) - 1):
            ok_dec = False
    if value(E, f, s) == 0 and is_flow(V, E, f, s, t) and all(net_out(E, f, v) == 0 for v in V):
        if any(k == "path" for k, _, _ in d) or len(d) > max(0, nf - 1):
            ok_circ = False
    if not has_cycle(V, E, f) and any(k == "cycle" for k, _, _ in d):
        ok_acyc = False
    # linear combinations of (not necessarily feasible) flows
    g = recombine(E, [("path", p, rng.randint(-3, 3)) for p in P] + [("cycle", cy, rng.randint(-3, 3)) for cy in C])
    al, be = Fr(rng.randint(-9, 9), rng.randint(1, 5)), Fr(rng.randint(-9, 9), rng.randint(1, 5))
    hh = {e: al * f[e] + be * g[e] for e in E}
    if not (is_flow(V, E, hh, s, t) and value(E, hh, s) == al * value(E, f, s) + be * value(E, g, s)):
        ok_lin = False
check("decomposition algorithm: the pieces add up to f, are simple s-t paths and simple cycles, and number at most "
      "#f (edges with positive flow) — random flows built from paths and cycles", ok_dec)
check("an edge lies on some piece iff it carries positive flow; every weight is positive", ok_support)
check("circulations decompose into cycles only, at most max{0, #f - 1}; acyclic flows into paths only",
      ok_circ and ok_acyc)
check("alpha f + beta g is an (s,t)-flow of value alpha|f| + beta|g| (random rational alpha, beta, flows of any sign)",
      ok_lin)
# the book's literal algorithm can get stuck
CV = ["s", "a", "b", "t"]
CE = [("s", "a"), ("a", "t"), ("t", "b"), ("b", "s")]
circ = {e: 1 for e in CE}
CV2 = ["s", "a", "b", "c", "t"]
CE2 = [("s", "a"), ("a", "t"), ("s", "b"), ("b", "t"), ("t", "c"), ("c", "s")]
f2 = dict(zip(CE2, [1, 1, 5, 5, 5, 5]))
check("the book's walk-from-s-until-t version gets stuck on the circulation s a t b s (path s a t first, then "
      "t->b->s has nowhere to go) and on a flow of value 1; the page's version decomposes both",
      is_flow(CV, CE, circ, "s", "t") and value(CE, circ, "s") == 0 and book_decompose(CV, CE, circ, "s", "t") == "stuck"
      and value(CE2, f2, "s") == 1 and book_decompose(CV2, CE2, f2, "s", "t") == "stuck"
      and recombine(CE, decompose(CV, CE, circ, "s", "t")) == circ
      and recombine(CE2, decompose(CV2, CE2, f2, "s", "t")) == f2)
# FF's maximum flows: cancel cycles -> acyclic maximum flow
ok_acmax = True
for trial in range(300):
    V, E, c = random_network(rng.randint(3, 7), 0.6, 10, rng)
    f, _ = ford_fulkerson(V, E, c, "s", "t", path_any, rng)
    d = decompose(V, E, f, "s", "t", rng)
    fa = recombine(E, [x for x in d if x[0] == "path"])
    if not (feasible(E, c, fa) and is_flow(V, E, fa, "s", "t") and value(E, fa, "s") == value(E, f, "s")):
        ok_acmax = False
check("keeping only the paths of a maximum flow's decomposition gives a maximum flow (300 networks)", ok_acmax)
# the theorem needs |f| >= 0: one unit on t->s
Vn, En = ["s", "t"], [("t", "s"), ("s", "t")]
fneg = {("t", "s"): 1, ("s", "t"): 0}
check("a non-negative flow of value -1 (one unit on t->s) is a flow; paths have value 1 and cycles 0, so no positive "
      "combination of them gives it", is_flow(Vn, En, fneg, "s", "t") and value(En, fneg, "s") == -1)
# the book's path flow with -1 on reversed edges breaks conservation when antiparallel edges exist
Vb = ["s", "u", "v", "t"]
Eb = [("s", "v"), ("v", "u"), ("u", "v"), ("u", "t")]
Pb = ["s", "v", "u", "t"]
pe = set(zip(Pb, Pb[1:]))
book_P = {e: (1 if e in pe else (-1 if (e[1], e[0]) in pe else 0)) for e in Eb}
page_P = {e: (1 if e in pe else 0) for e in Eb}
check("path flow with 1 on the path's edges is a flow of value 1; the book's extra -1 on reversed edges breaks "
      "conservation when u->v and v->u are both edges",
      is_flow(Vb, Eb, page_P, "s", "t") and value(Eb, page_P, "s") == 1 and not is_flow(Vb, Eb, book_P, "s", "t"))
# review: the -1 clause fits residual paths of a reduced network (augmenting paths use edges backward)
ok_resP, n_back = True, 0
for trial in range(400):
    V, E, c = random_network(rng.randint(4, 7), 0.8, 10, rng, zero_prob=0)
    tr = []
    ford_fulkerson(V, E, c, "s", "t", path_any, rng, trace=tr)
    for (f0, r0, _, _) in tr:
        for P in simple_paths(V, list(r0), "s", "t"):  # every augmenting path of every intermediate flow
            pe = set(zip(P, P[1:]))
            n_back += sum(1 for e in pe if e not in set(E))
            F = min(r0[e] for e in pe)
            bP = {e: (1 if e in pe else (-1 if (e[1], e[0]) in pe else 0)) for e in E}
            if not (is_flow(V, E, bP, "s", "t") and value(E, bP, "s") == 1
                    and {e: f0[e] + F * bP[e] for e in E} == augment(E, f0, P, F)):
                ok_resP = False
check("the book's path flow (with -1 on reversed edges) of an augmenting path in a reduced network is a flow of "
      "value 1, and f + F·P is the augmented flow  [every augmenting path of every intermediate flow, 400 networks]",
      ok_resP and n_back > 0, f"{n_back} backward edges used")
# review: the book's walk-from-s version works when no flow enters s, e.g. on Ford–Fulkerson's flows
ok_bookw, ok_noin, n_bw = True, True, 0
for trial in range(600):
    V, E, c = random_network(rng.randint(3, 7), 0.6, 10, rng)
    if trial % 2 == 0:
        f, _ = ford_fulkerson(V, E, c, "s", "t", rng.choice([path_any, path_bfs, path_fattest]), rng)
        if any(f[e] > 0 for e in E if e[1] == "s"):
            ok_noin = False
    else:  # random non-negative flow from s-t paths and cycles avoiding s
        Es = [e for e in E if e[1] != "s"]
        f = {e: 0 for e in E}
        Ps = simple_paths(V, Es, "s", "t")
        Cs = [cy for cy in simple_cycles(V, Es)]
        for p in (rng.sample(Ps, min(3, len(Ps))) + rng.sample(Cs, min(3, len(Cs)))):
            w = rng.randint(1, 4)
            for e in zip(p, p[1:]):
                f[e] += w
    d = book_decompose(V, E, f, "s", "t")
    n_bw += 1
    npos = sum(1 for e in E if f[e] > 0)
    if d == "stuck" or recombine(E, d) != f or len(d) > npos or any(w <= 0 for _, _, w in d):
        ok_bookw = False
check("the book's walk-from-s-until-t decomposition never gets stuck when no flow enters s: Ford–Fulkerson flows "
      "(any, shortest, fattest paths) carry no flow into s, and on them and on random such flows it returns at most "
      "#f positive pieces adding up to f", ok_bookw and ok_noin, f"{n_bw} flows")
check("page: the book's version is credited where it works (no flow into s, Ford–Fulkerson's flows) and the "
      "-1 clause where it fits (augmenting paths)",
      "The book's version does work whenever no edge into $s$ carries flow" in read(PAGE)
      and "augmenting gives $f + F\\cdot P$" in read(PAGE))



def cancel_cycles(V, E, f):
    """Page §10.5: while some directed cycle carries positive flow on all its edges, subtract its bottleneck."""
    g = dict(f)
    steps = 0
    while True:
        cyc = None
        for C in simple_cycles(V, [e for e in E if g[e] > 0]):
            cyc = C
            break
        if cyc is None:
            return g, steps
        es = list(zip(cyc, cyc[1:]))
        F = min(g[e] for e in es)
        for e in es:
            g[e] -= F
        steps += 1


ok_cc = True
for trial in range(400):
    V, E, c = random_network(rng.randint(3, 7), 0.6, 10, rng)
    f, _ = ford_fulkerson(V, E, c, "s", "t", path_any, rng)
    g, steps = cancel_cycles(V, E, f)
    if not (feasible(E, c, g) and is_flow(V, E, g, "s", "t") and value(E, g, "s") == value(E, f, "s")
            and not has_cycle(V, E, g) and steps <= sum(1 for e in E if f[e] > 0)):
        ok_cc = False
check("cancelling positive cycles one at a time keeps the value and feasibility, empties an edge each time and ends "
      "with an acyclic maximum flow (400 networks)", ok_cc)

# levels can decrease when the augmenting path is not a shortest path
LV = ["s", "a", "b", "u", "v", "t"]
LE = [("s", "v"), ("s", "a"), ("a", "b"), ("b", "u"), ("u", "v"), ("v", "t")]
Lc = dict(zip(LE, [1, 1, 1, 1, 1, 2]))
L0 = {e: 0 for e in LE}
lev0 = bfs_levels(LV, residual(LV, LE, Lc, L0), "s")
r0 = residual(LV, LE, Lc, L0)
LP = list("sabuvt")
L1 = augment(LE, L0, LP, min(r0[e] for e in zip(LP, LP[1:])))
lev1 = bfs_levels(LV, residual(LV, LE, Lc, L1), "s")
check("with a non-shortest augmenting path, BFS levels can decrease: s->v, s->a, a->b, b->u, u->v (1), v->t (2); "
      "augmenting s a b u v t lowers level(u) from 3 to 2 (Lemma 10.2 needs shortest paths)",
      lev0["u"] == 3 and lev1["u"] == 2 and is_flow(LV, LE, L1, "s", "t") and feasible(LE, Lc, L1))

# Edmonds–Karp stress test on larger networks
ok_ek2, max_ratio2, max_dis2 = True, 0.0, 0
for trial in range(600):
    n = rng.randint(6, 10)
    V, E, c = random_network(n, rng.choice([0.3, 0.5, 0.8]), rng.choice([1, 2, 100]), rng, zero_prob=0.0)
    mc, _ = brute_min_cut(V, E, c, "s", "t")
    tr = []
    f, it = ford_fulkerson(V, E, c, "s", "t", path_bfs, trace=tr)
    if value(E, f, "s") != mc or (E and it > len(E) * len(V)):
        ok_ek2 = False
    if E:
        max_ratio2 = max(max_ratio2, it / (len(E) * len(V) / 2))
    levels = [bfs_levels(V, r, "s") for (g, r, P, F) in tr]
    if any(levels[i][v] < levels[i - 1][v] for i in range(1, len(levels)) for v in V):
        ok_ek2 = False
    dis = {}
    for i in range(1, len(tr)):
        for e in set(tr[i - 1][1]) - set(tr[i][1]):
            dis[e] = dis.get(e, 0) + 1
    if dis and max(dis.values()) > len(V) / 2:
        ok_ek2 = False
    max_dis2 = max([max_dis2] + list(dis.values()))
check(f"Edmonds–Karp on 600 networks with 6–10 vertices: correct value, levels monotone, each residual edge "
      f"disappears <= V/2 times (max seen {max_dis2}), <= EV iterations (largest ratio to EV/2: {max_ratio2:.3f})",
      ok_ek2)

# =====================================================================================================
print("== The book's network (Figures 10.2, 10.3, 10.5, 10.6)")
BV = ["s", "a", "b", "c", "d", "t"]
BE = [("s", "a"), ("s", "c"), ("a", "b"), ("a", "c"), ("b", "c"), ("d", "b"), ("b", "t"), ("c", "d"), ("d", "t")]
Bc = dict(zip(BE, [20, 10, 5, 10, 15, 10, 15, 10, 20]))
Bf = dict(zip(BE, [10, 0, 0, 10, 0, 5, 5, 10, 5]))
check("Figure 10.2: feasible flow, conserved at a, b, c, d, value 10 = net flow into t",
      feasible(BE, Bc, Bf) and is_flow(BV, BE, Bf, "s", "t") and value(BE, Bf, "s") == 10
      and -net_out(BE, Bf, "t") == 10 and reduced(BE))
check("it saturates exactly a->c and c->d and avoids exactly s->c, a->b, b->c",
      {e for e in BE if Bf[e] == Bc[e]} == {("a", "c"), ("c", "d")}
      and {e for e in BE if Bf[e] == 0} == {("s", "c"), ("a", "b"), ("b", "c")})
cuts_tab = {}
for S in all_cuts(BV, "s", "t"):
    out_ = sum(Bf[e] for e in BE if e[0] in S and e[1] not in S)
    in_ = sum(Bf[e] for e in BE if e[1] in S and e[0] not in S)
    cuts_tab[S] = (cut_capacity(BE, Bc, S), out_, in_)
CT = {frozenset("s"): (30, 10, 0), frozenset("sac"): (15, 10, 0), frozenset("sab"): (50, 15, 5),
      frozenset("sabcd"): (35, 10, 0)}
check("the cut table on the page: {s} 30 (10 - 0), {s,a,c} 15 (10 - 0), {s,a,b} 50 (15 - 5), V-t 35 (10 - 0)",
      all(cuts_tab[S] == v for S, v in CT.items()), str({''.join(sorted(S)): cuts_tab[S] for S in CT}))
mcB, mcsB = brute_min_cut(BV, BE, Bc, "s", "t")
check("16 cuts; the minimum cut is {s, a, c}, capacity 15, and it is the only minimum cut",
      len(cuts_tab) == 16 and mcB == 15 and mcsB == [frozenset("sac")])
RB = residual(BV, BE, Bc, Bf)
check("residual graph of the flow (Figure 10.5): 13 edges with the capacities in the figure",
      RB == {("s", "a"): 10, ("a", "s"): 10, ("s", "c"): 10, ("a", "b"): 5, ("c", "a"): 10, ("b", "c"): 15,
             ("d", "b"): 5, ("b", "d"): 5, ("b", "t"): 10, ("t", "b"): 5, ("d", "c"): 10, ("d", "t"): 15,
             ("t", "d"): 5})
check("for the flow of value 10, every vertex (t included) is reachable from s in G_f", reach(BV, RB, "s") == set(BV))
PB = ["s", "c", "a", "b", "d", "t"]
caps = [RB[e] for e in zip(PB, PB[1:])]
check("augmenting path s c a b d t: residual capacities 10, 10, 5, 5, 15, F = 5; c->a and b->d are backward edges",
      caps == [10, 10, 5, 5, 15] and min(caps) == 5 and ("a", "c") in Bc and ("d", "b") in Bc
      and ("c", "a") not in Bc and ("b", "d") not in Bc)
Bf2 = augment(BE, Bf, PB, 5)
check("augmented flow (Figure 10.6): s->a 10, s->c 5, a->b 5, a->c 5, b->c 0, d->b 0, b->t 5, c->d 10, d->t 10; "
      "value 15, feasible",
      Bf2 == dict(zip(BE, [10, 5, 5, 5, 0, 0, 5, 10, 10])) and value(BE, Bf2, "s") == 15
      and feasible(BE, Bc, Bf2) and is_flow(BV, BE, Bf2, "s", "t"))
RB2 = residual(BV, BE, Bc, Bf2)
check("after augmenting: reachable from s in G_f' = {s, a, c}; a->b 5/5 and c->d 10/10 saturated, b->c 0/15 "
      "avoided; 15 = 5 + 10", reach(BV, RB2, "s") == set("sac") and Bf2[("a", "b")] == 5 == Bc[("a", "b")]
      and Bf2[("c", "d")] == 10 == Bc[("c", "d")] and Bf2[("b", "c")] == 0)
# Edmonds–Karp and fattest path on the book's network
tr = []
fEK, itEK = ford_fulkerson(BV, BE, Bc, "s", "t", path_bfs, trace=tr)
check("Edmonds–Karp on the book's network: s a b t (5), then s c d t (10); value 15 after two augmentations",
      itEK == 2 and [(x[2], x[3]) for x in tr[:-1]] == [(list("sabt"), 5), (list("scdt"), 10)]
      and value(BE, fEK, "s") == 15)
tr = []
fFP, itFP = ford_fulkerson(BV, BE, Bc, "s", "t", path_fattest, trace=tr)
check("fattest path on the book's network: bottlenecks 10, then 5", [x[3] for x in tr[:-1]] == [10, 5])
# s a c d t and s a c d b t give the book's flow
fx = augment(BE, augment(BE, {e: 0 for e in BE}, list("sacdt"), 5), list("sacdbt"), 5)
check("the flow of value 10 is s a c d t (5) + s a c d b t (5)", fx == Bf)

# ------------------------------------------------------------------------------ Edmonds–Karp's bad example
print("== Edmonds and Karp's bad example (Figure 10.7)")
ok_bad = True
for X in range(1, 31):
    V7 = ["s", "u", "v", "t"]
    E7 = [("s", "u"), ("s", "v"), ("u", "v"), ("u", "t"), ("v", "t")]
    c7 = {("s", "u"): X, ("s", "v"): X, ("u", "v"): 1, ("u", "t"): X, ("v", "t"): X}
    mc7, _ = brute_min_cut(V7, E7, c7, "s", "t")
    f = {e: 0 for e in E7}
    k = 0
    while True:
        r = residual(V7, E7, c7, f)
        P = list("suvt") if k % 2 == 0 else list("svut")
        if not all(e in r for e in zip(P, P[1:])):
            break
        F = min(r[e] for e in zip(P, P[1:]))
        if F != 1:
            ok_bad = False
        f = augment(E7, f, P, F)
        k += 1
    rr = residual(V7, E7, c7, f)
    fe, ite = ford_fulkerson(V7, E7, c7, "s", "t", path_bfs)
    if not (mc7 == 2 * X and k == 2 * X and value(E7, f, "s") == 2 * X and path_bfs(V7, rr, "s", "t") is None
            and ite == 2):
        ok_bad = False
    if X == 5:
        r1 = residual(V7, E7, c7, augment(E7, {e: 0 for e in E7}, list("suvt"), 1))
        fig_res = r1 == {("s", "u"): X - 1, ("u", "s"): 1, ("s", "v"): X, ("v", "u"): 1, ("u", "t"): X,
                         ("v", "t"): X - 1, ("t", "v"): 1}
check("X = 1..30: maximum flow 2X; alternating s u v t / s v u t pushes 1 unit each time, 2X augmentations; "
      "Edmonds–Karp needs 2", ok_bad)
check("residual graph after the first bad augmentation (figure, right): s->u X-1, u->s 1, s->v X, v->u 1, u->t X, "
      "v->t X-1, t->v 1", fig_res)

# ------------------------------------------------------------------------------ Zwick's network, exact arithmetic
print("== Zwick's network (Figure 10.8) in exact arithmetic over Q(sqrt 5)")


class Q5:
    """a + b*sqrt(5) with rational a, b."""
    __slots__ = ("a", "b")

    def __init__(self, a, b=0):
        self.a, self.b = Fr(a), Fr(b)

    def __add__(self, o):
        o = o if isinstance(o, Q5) else Q5(o)
        return Q5(self.a + o.a, self.b + o.b)
    __radd__ = __add__

    def __neg__(self):
        return Q5(-self.a, -self.b)

    def __sub__(self, o):
        return self + (-(o if isinstance(o, Q5) else Q5(o)))

    def __rsub__(self, o):
        return Q5(o) - self

    def __mul__(self, o):
        o = o if isinstance(o, Q5) else Q5(o)
        return Q5(self.a * o.a + 5 * self.b * o.b, self.a * o.b + self.b * o.a)
    __rmul__ = __mul__

    def inv(self):
        d = self.a * self.a - 5 * self.b * self.b
        return Q5(self.a / d, -self.b / d)

    def __truediv__(self, o):
        o = o if isinstance(o, Q5) else Q5(o)
        return self * o.inv()

    def __rtruediv__(self, o):
        return Q5(o) * self.inv()

    def sign(self):
        a, b = self.a, self.b
        if a >= 0 and b >= 0:
            return 0 if (a == 0 and b == 0) else 1
        if a <= 0 and b <= 0:
            return -1
        # opposite signs: compare a^2 with 5 b^2
        if a > 0:
            return 1 if a * a > 5 * b * b else -1
        return 1 if 5 * b * b > a * a else -1

    def __eq__(self, o):
        o = o if isinstance(o, Q5) else Q5(o)
        return self.a == o.a and self.b == o.b

    def __hash__(self):
        return hash((self.a, self.b))

    def __lt__(self, o):
        return (self - o).sign() < 0

    def __le__(self, o):
        return (self - o).sign() <= 0

    def __gt__(self, o):
        return (self - o).sign() > 0

    def __ge__(self, o):
        return (self - o).sign() >= 0

    def __float__(self):
        return float(self.a) + float(self.b) * math.sqrt(5)


PHI = Q5(Fr(-1, 2), Fr(1, 2))
check("phi = (sqrt5 - 1)/2 satisfies 1 - phi = phi^2", 1 - PHI == PHI * PHI and abs(float(PHI) - 0.618034) < 1e-6)


def phipow(k):
    r = Q5(1)
    for _ in range(k):
        r = r * PHI
    return r


Xz = Q5(10)
ZV = ["s", "a", "b", "c", "d", "t"]
ZE = [("s", "a"), ("s", "b"), ("s", "d"), ("b", "a"), ("b", "c"), ("d", "c"), ("a", "t"), ("c", "t"), ("d", "t")]
Zc = {e: Xz for e in ZE}
Zc[("b", "a")], Zc[("b", "c")], Zc[("d", "c")] = Q5(1), Q5(1), PHI
HOR = [("b", "a"), ("b", "c"), ("d", "c")]
XE = [e for e in ZE if e not in HOR]
check("Zwick's network is reduced, with six X edges and horizontal capacities 1, 1, phi",
      reduced(ZE) and len(XE) == 6)
mcz, mczs = brute_min_cut(ZV, ZE, Zc, "s", "t")
check("its maximum flow (minimum cut) is 2X + 1 (X = 10)", mcz == 2 * Xz + 1)
PATHS = {"central": "sbct", "A": "sabct", "B": "sdcbat", "C": "sbcdt"}
zf = {e: Q5(0) for e in ZE}
seq = ["central"]
for rnd in range(8):
    seq += ["B", "C", "B", "A"]
ok_z, ok_x, ok_claims = True, True, True
amounts, triples, values = [], [], []
for step, name in enumerate(seq):
    r = residual(ZV, ZE, Zc, zf)
    P = list(PATHS[name])
    pe = list(zip(P, P[1:]))
    if not all(e in r for e in pe):
        ok_z = False
        break
    F = min((r[e] for e in pe), key=lambda q: (float(q)))
    Fx = r[pe[0]]
    for e in pe:
        if r[e] < Fx:
            Fx = r[e]
    F = Fx
    # the bottleneck is a horizontal edge, never an X edge
    for e in pe:
        if (e in XE) and r[e] < Xz - 3:
            ok_x = False
        if (e[1], e[0]) in XE:
            ok_x = False  # paths never use an X edge backward
    zf = augment(ZE, zf, P, F)
    if not all(zf[e] <= 3 for e in XE):
        ok_x = False
    amounts.append(F)
    triples.append(tuple(Zc[e] - zf[e] for e in HOR))
    values.append(value(ZE, zf, "s"))
    if not (feasible(ZE, Zc, zf) and is_flow(ZV, ZE, zf, "s", "t")):
        ok_z = False
check("every path of the sequence central, (B, C, B, A) x 8 is an augmenting path at its turn", ok_z)
check("the X edges are never the bottleneck: their residual capacity stays >= X - 3, flow on them <= 3", ok_x)
ok_tab = triples[0] == (Q5(1), Q5(0), PHI) and amounts[0] == Q5(1)
for rnd in range(8):
    k = 1 + 2 * rnd
    i = 1 + 4 * rnd
    exp_amt = [phipow(k), phipow(k), phipow(k + 1), phipow(k + 1)]
    exp_tri = [(phipow(k + 1), phipow(k), Q5(0)), (phipow(k + 1), Q5(0), phipow(k)),
               (Q5(0), phipow(k + 1), phipow(k + 2)), (phipow(k + 1), Q5(0), phipow(k + 2))]
    if triples[i - 1] != (phipow(k - 1), Q5(0), phipow(k)):
        ok_tab = False
    if amounts[i:i + 4] != exp_amt or triples[i:i + 4] != exp_tri:
        ok_tab = False
check("table: from phi^(k-1), 0, phi^k the steps B, C, B, A push phi^k, phi^k, phi^(k+1), phi^(k+1) and leave "
      "(phi^(k+1), phi^k, 0), (phi^(k+1), 0, phi^k), (0, phi^(k+1), phi^(k+2)), (phi^(k+1), 0, phi^(k+2)); "
      "k = 1, 3, 5, ... (8 rounds)", ok_tab)
ok_4n1 = all(triples[4 * n] == (phipow(2 * n), Q5(0), phipow(2 * n + 1)) for n in range(9))
book_4n1 = any(triples[4 * n] == (phipow(2 * n - 2) if n >= 1 else None, Q5(0), phipow(2 * n - 1) if n >= 1 else None)
               for n in range(1, 9))
check("after 4n + 1 augmentations the horizontal residual capacities are phi^(2n), 0, phi^(2n+1) (n = 0..8); the "
      "book's phi^(2n-2), 0, phi^(2n-1) never matches", ok_4n1 and not book_4n1)
ok_val = True
for n in range(9):
    v = values[4 * n]
    s_ = Q5(1)
    for i in range(1, 2 * n + 1):
        s_ = s_ + 2 * phipow(i)
    lim = Q5(2, 1)
    if not (v == s_ and v == lim - 2 * phipow(2 * n + 1) / (1 - PHI) and v < lim):
        ok_val = False
check("flow value after 4n + 1 augmentations = 1 + 2(phi + ... + phi^(2n)) = (2 + sqrt5) - 2 phi^(2n+1)/(1 - phi)",
      ok_val)
limit = Q5(2, 1)
series = Q5(1) + 2 * PHI / (1 - PHI)
check("the limit 1 + 2 sum_{i>=1} phi^i equals 2 + sqrt5 (about 4.236), not the book's 1 + 2/(1 - phi) = 4 + sqrt5",
      series == limit and Q5(1) + 2 / (1 - PHI) == Q5(4, 1) and abs(float(limit) - 4.2360679) < 1e-6
      and limit < Q5(7))
check("the flow values increase strictly and stay below 2 + sqrt5, while the maximum flow is 2X + 1 = 21",
      all(values[i] < values[i + 1] for i in range(len(values) - 1)) and values[-1] < limit and mcz == Q5(21))

# ------------------------------------------------------------------------------ Figure 10.9 decomposition
print("== Flow decomposition of the book's Figure 10.9 flow")
DF = dict(zip(BE, [9, 6, 4, 5, 3, 3, 4, 14, 11]))
PIECES = [("path", list("sabt"), 4), ("path", list("sacdt"), 5), ("path", list("scdt"), 6),
          ("cycle", list("cdbc"), 3)]
check("the flow is conserved, value 15, 9 edges carry flow; it equals s a b t (4) + s a c d t (5) + s c d t (6) "
      "+ cycle c d b c (3)", is_flow(BV, BE, DF, "s", "t") and value(BE, DF, "s") == 15
      and sum(1 for e in BE if DF[e] > 0) == 9 and recombine(BE, PIECES) == DF)
ALT = [("path", list("sabcdt"), 3), ("path", list("scdbt"), 3), ("path", list("sabt"), 1),
       ("path", list("sacdt"), 5), ("path", list("scdt"), 3)]
check("the same flow is also s a b c d t (3) + s c d b t (3) + s a b t (1) + s a c d t (5) + s c d t (3): five "
      "paths, no cycle", recombine(BE, ALT) == DF and sum(w for _, _, w in ALT) == 15)
check("c->d carries 5 + 6 + 3 = 14 in the first decomposition", 5 + 6 + 3 == DF[("c", "d")])
d = decompose(BV, BE, DF, "s", "t")
check("the walk algorithm decomposes it into at most 9 pieces adding up to the flow (20 random runs)",
      all(recombine(BE, dd) == DF and len(dd) <= 9
          for dd in (decompose(BV, BE, DF, "s", "t", random.Random(i)) for i in range(20))))
check("the five-path decomposition is a sum of paths, yet the flow has the positive cycle c d b c (a sum of paths "
      "need not be acyclic)", has_cycle(BV, BE, DF) and all(DF[e] > 0 for e in [("c", "d"), ("d", "b"), ("b", "c")]))

# ------------------------------------------------------------------------------ other small claims
print("== Small claims in the traps and on the concept pages")
# diamond: GreedyFlow gets stuck at 1, residual path s b a t; EK picks s a t and s b t
DV = ["s", "a", "b", "t"]
DE = [("s", "a"), ("s", "b"), ("a", "b"), ("a", "t"), ("b", "t")]
Dc = {e: 1 for e in DE}
g1 = augment(DE, {e: 0 for e in DE}, list("sabt"), 1)
rem = {e: Dc[e] - g1[e] for e in DE}
stuck = path_any(DV, {e: rem[e] for e in DE if rem[e] > 0}, "s", "t", rng) is None
r1 = residual(DV, DE, Dc, g1)
P2 = list("sbat")
g2 = augment(DE, g1, P2, min(r1[e] for e in zip(P2, P2[1:])))
tr = []
fD, itD = ford_fulkerson(DV, DE, Dc, "s", "t", path_bfs, trace=tr)
check("diamond (all capacities 1): after s a b t no path has spare capacity without backward edges, but G_f has "
      "s b a t (through b->a); maximum flow 2", stuck and all(e in r1 for e in zip(P2, P2[1:]))
      and value(DE, g2, "s") == 2 and brute_min_cut(DV, DE, Dc, "s", "t")[0] == 2 and g2[("a", "b")] == 0)
check("diamond: Edmonds–Karp augments s a t then s b t (2 edges each) and never uses a->b",
      [x[2] for x in tr[:-1]] == [list("sat"), list("sbt")] and fD[("a", "b")] == 0)
# fractional maximum flow with integer capacities
FV = ["s", "a", "b", "c", "t"]
FE = [("s", "a"), ("s", "b"), ("a", "c"), ("b", "c"), ("c", "t")]
Fc = {e: 1 for e in FE}
ff = {("s", "a"): Fr(1, 2), ("s", "b"): Fr(1, 2), ("a", "c"): Fr(1, 2), ("b", "c"): Fr(1, 2), ("c", "t"): 1}
check("integer capacities, fractional maximum flow: s->a, s->b, a->c, b->c, c->t all 1; halves on the four edges "
      "and 1 on c->t is a feasible flow of the maximum value 1",
      feasible(FE, Fc, ff) and is_flow(FV, FE, ff, "s", "t") and value(FE, ff, "s") == 1
      and brute_min_cut(FV, FE, Fc, "s", "t")[0] == 1)
# concept page maximum-flow example
MV = ["s", "a", "b", "t"]
ME = [("s", "a"), ("s", "b"), ("a", "b"), ("a", "t"), ("b", "t")]
Mc = dict(zip(ME, [3, 2, 1, 2, 3]))
Mf = dict(zip(ME, [3, 2, 1, 2, 3]))
mcM, mcsM = brute_min_cut(MV, ME, Mc, "s", "t")
capsM = {''.join(sorted(S, key=MV.index)): cut_capacity(ME, Mc, S) for S in all_cuts(MV, "s", "t")}
fM, _ = ford_fulkerson(MV, ME, Mc, "s", "t", path_bfs)
check("maximum-flow example: flow s->a 3, s->b 2, a->b 1, a->t 2, b->t 3 is feasible, value 5; cuts {s} 5, "
      "{s,a} 5, {s,a,b} 5, {s,b} 6; three minimum cuts; the flow is the only maximum flow; residual reach = {s}",
      feasible(ME, Mc, Mf) and is_flow(MV, ME, Mf, "s", "t") and value(ME, Mf, "s") == 5 and mcM == 5
      and capsM == {"s": 5, "sa": 5, "sb": 6, "sab": 5} and len(mcsM) == 3 and fM == Mf
      and reach(MV, residual(MV, ME, Mc, Mf), "s") == {"s"}, str(capsM))
# uniqueness of that maximum flow: every flow of value 5 saturates s->a and s->b; brute force over integer flows
uniq = []
for vals in itertools.product(*[range(Mc[e] + 1) for e in ME]):
    g = dict(zip(ME, vals))
    if is_flow(MV, ME, g, "s", "t") and value(ME, g, "s") == 5:
        uniq.append(g)
check("... (integral maximum flows of that network: exactly one)", len(uniq) == 1 and uniq[0] == Mf)

# =====================================================================================================
print("== Page text: numbers stated in prose and tables")
page = read(PAGE)
mf_page = read(os.path.join(CONCEPTS, "maximum-flow.md"))
ff_page = read(os.path.join(CONCEPTS, "ford-fulkerson.md"))


def onpage(x, text=None):
    return x in (page if text is None else text)


def sto(path_str):
    return "\\to ".join(path_str).replace("\\to ", "\\to ")


# the cut table, rows generated from the computation
rows_ok = True
ROWNAMES = {frozenset("s"): "$\\{s\\}$", frozenset("sac"): "$\\{s, a, c\\}$", frozenset("sab"): "$\\{s, a, b\\}$",
            frozenset("sabcd"): "$V\\setminus\\{t\\}$"}
for S, nm in ROWNAMES.items():
    cap_, out_, in_ = cuts_tab[S]
    es = [e for e in BE if e[0] in S and e[1] not in S]
    edges_txt = ", ".join(f"${u}\\to {v}$" for u, v in es)
    caps_txt = " + ".join(str(Bc[e]) for e in es) + f" = {cap_}"
    row = f"> | {nm} | {edges_txt} | ${caps_txt}$ | ${out_} - {in_}$"
    if row not in page:
        rows_ok = False
        print("   missing row:", row)
check("cut table rows (edges, capacities, net flow) match the computation", rows_ok)
check("cut example prose: last column always |f| = 10; 2^4 = 16 cuts; {s,a,c} the only cut of capacity 15",
      onpage("The last column is always $|f| = 10$") and onpage("Of the network's $2^4 = 16$ cuts, $(\\{s,a,c\\}, \\{b,d,t\\})$ is the only one of capacity 15"))
check("augmentation example: residual capacities 10, 10, 5, 5, 15, F = 5; a->c 10 -> 5, d->b 5 -> 0; value 15; "
      "cut capacity 5 + 10 = 15",
      onpage("has residual capacities $10, 10, 5, 5, 15$, so $F = 5$")
      and onpage("they lower $f(a\\to c)$ from 10 to 5 and $f(d\\to b)$ from 5 to 0")
      and onpage("The new flow has value 15") and onpage("the cut $S = \\{s, a, c\\}$ of capacity $5 + 10 = 15$")
      and Bf2[("a", "c")] == 5 and Bf2[("d", "b")] == 0)
check("Edmonds–Karp / fattest example prose (values checked above)", onpage("breadth-first search finds $s\\to a\\to b\\to t$ (3 edges, bottleneck 5) and then $s\\to c\\to d\\to t$ (bottleneck 10)")
      and onpage("a path of bottleneck 10 (such as $s\\to c\\to d\\to t$), then one of bottleneck 5")
      and min(RBc for RBc in [Bc[("s", "c")], Bc[("c", "d")], Bc[("d", "t")]]) == 10)
# Zwick table rows
ztab = ["> | B: $s\\,d\\,c\\,b\\,a\\,t$ | $\\varphi^k$ | $\\varphi^{k+1},\\ \\varphi^k,\\ 0$ |",
        "> | C: $s\\,b\\,c\\,d\\,t$ | $\\varphi^k$ | $\\varphi^{k+1},\\ 0,\\ \\varphi^k$ |",
        "> | B: $s\\,d\\,c\\,b\\,a\\,t$ | $\\varphi^{k+1}$ | $0,\\ \\varphi^{k+1},\\ \\varphi^{k+2}$ |",
        "> | A: $s\\,a\\,b\\,c\\,t$ | $\\varphi^{k+1}$ | $\\varphi^{k+1},\\ 0,\\ \\varphi^{k+2}$ |"]
check("Zwick table on the page matches the verified steps (paths A, B, C as in the figure)",
      all(r in page for r in ztab) and PATHS == {"central": "sbct", "A": "sabct", "B": "sdcbat", "C": "sbcdt"})
check("Zwick prose: central path 1 unit, start 1, 0, phi; after 4n+1: phi^(2n), 0, phi^(2n+1); limit 2 + sqrt5 "
      "~ 4.24 < 7; max 2X + 1; the book's versions quoted",
      onpage("After the central path $s\\to b\\to c\\to t$ (1 unit) the three numbers are $1, 0, \\varphi$")
      and onpage("After $4n+1$ augmentations the horizontal residual capacities are $\\varphi^{2n}, 0, \\varphi^{2n+1}$")
      and onpage("1 + 2\\sum_{i\\ge 1}\\varphi^i = 1 + \\frac{2\\varphi}{1-\\varphi} = 2 + \\sqrt5 \\approx 4.24 < 7")
      and onpage("while the maximum flow is $2X + 1$")
      and onpage("$\\varphi^{2n-2}, 0, \\varphi^{2n-1}$ and the limit as $1 + 2/(1-\\varphi) = 4 + \\sqrt5$")
      and onpage("never carry more than 3 units") and abs(float(limit) - 4.24) < 0.005
      and Q5(1) + 2 * PHI / (1 - PHI) == limit)
check("decomposition prose: second decomposition and the 'not acyclic' remark",
      onpage("$s\\,a\\,b\\,c\\,d\\,t$ (3), $s\\,c\\,d\\,b\\,t$ (3), $s\\,a\\,b\\,t$ (1), $s\\,a\\,c\\,d\\,t$ (5) and $s\\,c\\,d\\,t$ (3)")
      and onpage("($c\\to d\\to b\\to c$ carries flow on every edge)"))
check("book-decomposition counterexample prose: circulation s a t b s, path s a t, leftover t b s",
      onpage("on the circulation $s\\to a\\to t\\to b\\to s$ it removes the path $s\\,a\\,t$ and leaves the flow $t\\to b\\to s$"))
check("diamond trap and fractional-flow trap on the page",
      onpage("In the network $s\\to a$, $s\\to b$, $a\\to b$, $a\\to t$, $b\\to t$, all of capacity 1, pushing 1 unit along $s\\to a\\to b\\to t$ leaves no path with spare capacity, yet the maximum flow is 2")
      and onpage("The residual graph has the path $s\\to b\\to a\\to t$")
      and onpage("the network $s\\to a$, $s\\to b$, $a\\to c$, $b\\to c$, $c\\to t$ has the fractional maximum flow $\\tfrac12$ on the first four edges and 1 on $c\\to t$"))
check("bad-example prose: maximum flow 2X, 2X iterations, EK and fattest need 2",
      onpage("the maximum flow is $2X$") and onpage("$2X$ iterations, $\\Theta(X) = \\Omega(|f^*|)$")
      and onpage("both rules choose $s\\to u\\to t$ and $s\\to v\\to t$ and finish after 2 augmentations instead of $2X$"))
ok_fat_bad = True
for X in (3, 7, 20):
    V7 = ["s", "u", "v", "t"]
    E7 = [("s", "u"), ("s", "v"), ("u", "v"), ("u", "t"), ("v", "t")]
    c7 = {("s", "u"): X, ("s", "v"): X, ("u", "v"): 1, ("u", "t"): X, ("v", "t"): X}
    for rule in (path_bfs, path_fattest):
        tr = []
        ford_fulkerson(V7, E7, c7, "s", "t", rule, trace=tr)
        if sorted("".join(x[2]) for x in tr[:-1]) != ["sut", "svt"]:
            ok_fat_bad = False
check("... and indeed both rules augment along s u t and s v t on the bad example (X = 3, 7, 20)", ok_fat_bad)
check("the Lemma 10.2 trap (levels can drop for arbitrary paths, verified above) is on the page",
      onpage("it is not a property of arbitrary augmenting paths"))
check("flow figure caption facts: at d 10 in, 5 + 5 out; value 10 + 0 = 10 = 5 + 5",
      Bf[("c", "d")] == 10 and Bf[("d", "b")] + Bf[("d", "t")] == 10 and Bf[("s", "a")] + Bf[("s", "c")] == 10
      and Bf[("b", "t")] + Bf[("d", "t")] == 10)
check("concept page maximum-flow example prose",
      onpage("Edges $s\\to a$ (3), $s\\to b$ (2), $a\\to b$ (1), $a\\to t$ (2), $b\\to t$ (3). The flow $3, 2, 1, 2, 3$", mf_page)
      and onpage("$S = \\{s,a\\}$ ($2 + 1 + 2$) and $S = \\{s,a,b\\}$ ($2 + 3$) also have capacity 5, while $S = \\{s,b\\}$ has 6", mf_page)
      and onpage("the recipe returns $S = \\{s\\}$, the smallest", mf_page))
check("concept page ford-fulkerson example prose",
      onpage("An unlucky Ford–Fulkerson first augments along $s\\to a\\to b\\to t$; then the only augmenting path is $s\\to b\\to a\\to t$", ff_page)
      and onpage("breadth-first search finds the two-edge paths $s\\to a\\to t$ and $s\\to b\\to t$", ff_page))
# "then the only augmenting path is s b a t": enumerate simple s-t paths in G_f after s a b t
paths_after = simple_paths(DV, list(r1.keys()), "s", "t")
check("... after s a b t the residual graph of the diamond has exactly one s-t path, s b a t",
      paths_after == [list("sbat")], str(paths_after))
check("headings: the fixed Ch 10 headings are present, in order",
      [h for h in re.findall(r"^## (.*)$", page, re.M)] ==
      ["10.1 Flows", "10.2 Cuts", "10.3 The maxflow-mincut theorem",
       "10.4 Ford and Fulkerson's augmenting-path algorithm", "10.5 Combining and decomposing flows",
       "10.6 Edmonds and Karp's algorithms", "10.7 Further progress", "Maximum flow as a black box", "Summary"])

# =====================================================================================================
print("== Figures: every number drawn is the computed one")


def fig_texts(name):
    html = read(os.path.join(FIGS, name + ".html"))
    return [re.sub(r"<[^>]+>", "", t) for t in re.findall(r"<text[^>]*>(.*?)</text>", html)]


ft = fig_texts("a10-flow")
check("a10-flow: one flow/capacity label per edge, exactly the book's flow",
      sorted(x for x in ft if "/" in x) == sorted(f"{Bf[e]}/{Bc[e]}" for e in BE))
ft = fig_texts("a10-residual")
check("a10-residual: the 13 residual capacities, as a multiset",
      sorted(int(x) for x in ft if x.isdigit()) == sorted(RB.values()))
ft = fig_texts("a10-mincut")
check("a10-mincut: labels are the augmented flow f'/c, and the caption line says 15 = 5 + 10",
      sorted(x for x in ft if "/" in x) == sorted(f"{Bf2[e]}/{Bc[e]}" for e in BE)
      and any("15" in x and "5 + 10" in x for x in ft))
ft = fig_texts("a10-bad-example")
check("a10-bad-example: left labels X, X, 1, X, X; right residual labels X, X−1, 1, 1, X, X−1, 1",
      sorted(x for x in ft if x in ("X", "1", "X−1"))
      == sorted(["X"] * 4 + ["1"] + ["X", "X−1", "1", "1", "X", "X−1", "1"]))
ft = fig_texts("a10-zwick")
check("a10-zwick: six X labels, two 1s and one φ; paths A, B, C spelled as on the page",
      ft.count("X") == 6 and ft.count("1") == 2 and ft.count("φ") == 1
      and "s a b c t" in ft and "s d c b a t" in ft and "s b c d t" in ft)
ft = fig_texts("a10-decomposition")
check("a10-decomposition: edge labels are the Figure 10.9 flow; the four pieces with weights 4, 5, 6, 3",
      sorted(int(x) for x in ft if x.isdigit()) == sorted(DF.values())
      and {"path s a b t: 4", "path s a c d t: 5", "path s c d t: 6", "cycle c d b c: 3"} <= set(ft))
for nm in ("a10-flow", "a10-residual", "a10-mincut", "a10-bad-example", "a10-zwick", "a10-decomposition"):
    html = read(os.path.join(FIGS, nm + ".html"))
    check(f"{nm}: inlined on the page and colored only through currentColor / CSS variables",
          f"<!-- fig:{nm} -->\n{html.strip()}" in page
          and not re.search(r'(fill|stroke)="#[0-9a-fA-F]{3,6}"', html))

# aliases unique site-wide
allal = []
for root_, _, files in os.walk(os.path.join(ROOT, "content")):
    for fn in files:
        if fn.endswith(".md"):
            m = re.search(r"^aliases: \[(.*)\]$", read(os.path.join(root_, fn)), re.M)
            if m:
                allal += [a.strip().strip('"').lower() for a in m.group(1).split(",")]
dups = sorted({a for a in allal if allal.count(a) > 1})
check("aliases are unique site-wide", not dups, str(dups))

# =====================================================================================================
print()
if FAIL:
    print(f"{len(FAIL)} FAILED:", *FAIL, sep="\n  ")
    sys.exit(1)
print("ALL OK")
