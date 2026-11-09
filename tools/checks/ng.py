#!/usr/bin/env python3
"""Checks for content/4-lecture-notes/g-minimum-cost-flows.md (Erickson, Extended Dance Remix G, "Minimum-Cost
Flows") and the concept page content/concepts/minimum-cost-flow.md.

Convention (the note's): balance b(v) = (flow into v) - (flow out of v); b < 0 supply, b > 0 demand. References: an
LP (scipy HiGHS) for every instance, and networkx.min_cost_flow where it applies (no lower bounds).
1. G.1: maximum flow as a minimum-cost circulation (edge t->s of cost -1), with the sign of the value; Klein's cycle
   canceling (Bellman-Ford negative cycles) on random circulations: cost drops by exactly c_f(gamma) * cost(gamma), at
   most |cost(f*)| <= ECK iterations, final cost = LP; the optimality criterion (no negative residual cycle) on random
   feasible circulations; the general two-stage algorithm with lower bounds, and the residual graph it needs.
2. G.2: successive shortest paths, as printed (arbitrary supply s, arbitrary demand t, Bellman-Ford), after enforcing
   the two assumptions; Lemma G.1 after every iteration; at most B iterations; final cost = LP; the strong-
   connectivity trick and the "report infeasible at once" remark.
3. G.3: Lemma G.2 and the reduced-cost path identity; FastSuccessiveShortestPaths with Dijkstra, with the potential
   update pi <- pi + dist (Lemma G.3 checked after every iteration) and with the printed pi <- dist.
4. G.4: Fulkerson's reduction to the transportation problem (sizes, bipartiteness, costs, recovery); transportation
   to assignment by copying vertices (scipy linear_sum_assignment); single-supply transshipment = shortest paths
   (cost = sum dist(v) b(v), the canonical tree flow, SSP builds it); a spanning-tree optimal flow.
5. The page's examples and the concept page's example, number by number.
"""
import heapq
import itertools
import math
import os
import random
import sys

import networkx as nx
import numpy as np
from scipy.optimize import linear_sum_assignment, linprog

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
PAGE = os.path.join(ROOT, "content", "4-lecture-notes", "g-minimum-cost-flows.md")
CONCEPT = os.path.join(ROOT, "content", "concepts", "minimum-cost-flow.md")
FAIL = []
random.seed(374007)
INF = math.inf


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAIL.append(name)


# ============================================================================ instances and references
class Net:
    """Edges are indexed (parallel and antiparallel edges allowed): E[i] = (u, v); lo, c, cost are lists."""

    def __init__(self, V, E, c, cost, b=None, lo=None):
        self.V, self.E, self.c, self.cost = list(V), list(E), list(c), list(cost)
        self.lo = list(lo) if lo is not None else [0] * len(E)
        self.b = dict(b) if b is not None else {v: 0 for v in V}


def netin(N, f, v):
    return sum(f[i] for i, (a, bb) in enumerate(N.E) if bb == v) - sum(f[i] for i, (a, bb) in enumerate(N.E) if a == v)


def feasible(N, f, b=None):
    b = N.b if b is None else b
    return (all(N.lo[i] - 1e-9 <= f[i] <= N.c[i] + 1e-9 for i in range(len(N.E))) and
            all(abs(netin(N, f, v) - b[v]) < 1e-7 for v in N.V))


def total_cost(N, f):
    return sum(N.cost[i] * f[i] for i in range(len(N.E)))


def lp(N):
    if not N.E:
        return (0, []) if all(x == 0 for x in N.b.values()) else None
    A = np.zeros((len(N.V), len(N.E)))
    for j, (u, v) in enumerate(N.E):
        A[N.V.index(v), j] += 1
        A[N.V.index(u), j] -= 1
    bounds = [(N.lo[i], None if N.c[i] == INF else N.c[i]) for i in range(len(N.E))]
    res = linprog(np.array(N.cost, dtype=float), A_eq=A, b_eq=[N.b[v] for v in N.V], bounds=bounds, method="highs")
    if res.status == 2:
        return None
    assert res.status == 0, res.message
    return res.fun, list(res.x)


def nx_cost(N):
    G = nx.DiGraph()
    for v in N.V:
        G.add_node(v, demand=N.b[v])
    for i, (u, v) in enumerate(N.E):
        assert not G.has_edge(u, v)
        kw = dict(weight=N.cost[i])
        if N.c[i] != INF:
            kw["capacity"] = N.c[i]
        G.add_edge(u, v, **kw)
    try:
        return nx.min_cost_flow_cost(G)
    except nx.NetworkXUnfeasible:
        return None


def residual_arcs(N, f):
    """Residual arcs (u, v, cap, cost, i, dir): forward cap c - f (cost), backward cap f - lo (cost -cost)."""
    arcs = []
    for i, (u, v) in enumerate(N.E):
        if N.c[i] - f[i] > 1e-12:
            arcs.append((u, v, N.c[i] - f[i], N.cost[i], i, +1))
        if f[i] - N.lo[i] > 1e-12:
            arcs.append((v, u, f[i] - N.lo[i], -N.cost[i], i, -1))
    return arcs


def negative_cycle(V, arcs, shuffle=True):
    """Bellman-Ford from a virtual source; returns a list of arcs forming a negative cycle, or None."""
    arcs = list(arcs)
    if shuffle:
        random.shuffle(arcs)
    d = {v: 0 for v in V}
    par = {v: None for v in V}
    x = None
    for _ in range(len(V)):
        x = None
        for a in arcs:
            u, v, cap, w = a[0], a[1], a[2], a[3]
            if d[u] + w < d[v] - 1e-12:
                d[v] = d[u] + w
                par[v] = a
                x = v
        if x is None:
            return None
    for _ in range(len(V)):
        x = par[x][0]
    cyc = []
    y = x
    while True:
        a = par[y]
        cyc.append(a)
        y = a[0]
        if y == x:
            break
    cyc.reverse()
    return cyc


def augment(f, path, R):
    for a in path:
        f[a[4]] += R * a[5]


def cycle_cancel(N, f0, log=None):
    f = list(f0)
    it = 0
    ok_step = True
    while True:
        cyc = negative_cycle(N.V, residual_arcs(N, f))
        if cyc is None:
            return f, it, ok_step
        R = min(a[2] for a in cyc)
        cc = sum(a[3] for a in cyc)
        before = total_cost(N, f)
        augment(f, cyc, R)
        ok_step &= abs(total_cost(N, f) - (before + R * cc)) < 1e-9 and feasible(N, f)
        if log is not None:
            log.append(([(a[0], a[1]) for a in cyc], R, cc))
        it += 1


def random_net(n, p=0.5, cmax=5, kmax=6, neg=True, inf_frac=0.0):
    V = list(range(n))
    E, c, cost = [], [], []
    for u in V:
        for v in V:
            if u != v and random.random() < p and (v, u) not in E:
                E.append((u, v))
                c.append(INF if random.random() < inf_frac else random.randint(1, cmax))
                cost.append(random.randint(-kmax if neg else 0, kmax))
    return V, E, c, cost


def random_b(V, total):
    b = {v: 0 for v in V}
    for _ in range(total):
        x, y = random.sample(V, 2)
        b[x] -= 1
        b[y] += 1
    return b


def maxflow_value(N, s, t):
    G = nx.DiGraph()
    G.add_nodes_from(N.V)
    for i, (u, v) in enumerate(N.E):
        G.add_edge(u, v, capacity=N.c[i])
    return nx.maximum_flow_value(G, s, t)


# ============================================================================ 1. G.1
okred = okval = okcc = okcc_step = okcc_it = okFF = True
for _ in range(150):
    n = random.choice([3, 4, 5, 6])
    V, E, c, _ = random_net(n, p=0.5, cmax=6)
    s, t = 0, n - 1
    N = Net(V, E + [(t, s)], c + [10 ** 4], [0] * len(E) + [-1])
    mf = maxflow_value(Net(V, E, c, [0] * len(E)), s, t)
    opt, x = lp(N)
    okred &= abs(opt + mf) < 1e-6
    f, it, okst = cycle_cancel(N, [0] * len(N.E))
    okcc &= abs(total_cost(N, f) + mf) < 1e-9
    fr = f[:-1]
    value = sum(fr[i] for i, e in enumerate(E) if e[0] == s) - sum(fr[i] for i, e in enumerate(E) if e[1] == s)
    okval &= value == f[-1] and value == mf
    # every negative residual cycle of the zero circulation uses t->s
    for _ in range(3):
        cyc = negative_cycle(N.V, residual_arcs(N, [0] * len(N.E)))
        if cyc:
            okFF &= any(a[4] == len(N.E) - 1 for a in cyc)
check("G.1 reduction: min-cost circulation with t->s of cost -1 = -(maximum flow), 150 networks (LP)", okred)
check("  cycle canceling on these instances ends with cost -|f*|", okcc)
check("  the restriction's value is +f(t->s) (the note says -f(t->s))", okval)
check("  every negative residual cycle of these instances passes through t->s", okFF)

okgen = okcrit = True
okits = True
nonopt = 0
for _ in range(250):
    n = random.choice([3, 4, 5, 6])
    V, E, c, cost = random_net(n, p=0.5, cmax=5, kmax=6)
    if not E:
        continue
    N = Net(V, E, c, cost)
    opt, _ = lp(N)
    f, it, okst = cycle_cancel(N, [0] * len(E))
    okgen &= abs(total_cost(N, f) - opt) < 1e-6 and feasible(N, f)
    okcc_step &= okst
    C, K = max(c), max(abs(k) for k in cost)
    okits &= it <= abs(total_cost(N, f)) <= len(E) * C * K
    nc = nx_cost(N)
    okgen &= nc is not None and abs(nc - opt) < 1e-6
    # optimality criterion on a random feasible circulation (sum of random residual cycles of the zero flow)
    g = [0] * len(E)
    for _ in range(random.randint(0, 4)):
        G = nx.DiGraph()
        for i, (u, v) in enumerate(E):
            if g[i] < c[i]:
                G.add_edge(u, v, i=i)
        cycles = list(itertools.islice(nx.simple_cycles(G), 20))
        if not cycles:
            break
        cy = random.choice(cycles)
        ids = [G[cy[k]][cy[(k + 1) % len(cy)]]["i"] for k in range(len(cy))]
        R = min(c[i] - g[i] for i in ids)
        for i in ids:
            g[i] += random.randint(1, R)
            g[i] = min(g[i], c[i])
    if not feasible(N, g):
        continue
    is_opt = abs(total_cost(N, g) - opt) < 1e-9
    no_neg = negative_cycle(N.V, residual_arcs(N, g)) is None
    okcrit &= is_opt == no_neg
    nonopt += not is_opt
check("Klein's cycle canceling = LP = networkx on 250 random min-cost circulations (costs of both signs)", okgen)
check("  every cancellation: cost(f') = cost(f) + c_f(gamma) * cost(gamma), f' feasible", okcc_step)
check("  iterations <= |cost(f*)| <= E C K (integer data)", okits)
check(f"optimality criterion: a feasible circulation is optimal iff its residual graph has no negative cycle "
      f"({nonopt} non-optimal test circulations)", okcrit)


# general min-cost flow, two stages (feasible flow, then min-cost circulation in the residual graph)
def feasible_flow_lb(N):
    """A feasible flow with lower bounds and balances via the maximum-flow reduction of note F."""
    G = nx.DiGraph()
    G.add_nodes_from(N.V + ["S*", "T*"])
    bb = dict(N.b)
    for i, (u, v) in enumerate(N.E):
        bb[v] -= N.lo[i]
        bb[u] += N.lo[i]
    mid = {}
    for i, (u, v) in enumerate(N.E):
        w = ("m", i)  # subdivide to allow parallel edges
        G.add_edge(u, w, capacity=N.c[i] - N.lo[i])
        G.add_edge(w, v, capacity=N.c[i] - N.lo[i])
        mid[i] = w
    need = 0
    for v in N.V:
        if bb[v] < 0:
            G.add_edge("S*", v, capacity=-bb[v])
        elif bb[v] > 0:
            G.add_edge(v, "T*", capacity=bb[v])
            need += bb[v]
    val, fl = nx.maximum_flow(G, "S*", "T*")
    if val != need:
        return None
    return [N.lo[i] + fl[u][mid[i]] for i, (u, v) in enumerate(N.E)]


oktwo = True
okres_need = 0
cnt = 0
for _ in range(200):
    n = random.choice([3, 4, 5])
    V, E, c, cost = random_net(n, p=0.6, cmax=5, kmax=5)
    if not E:
        continue
    lo = [random.choice([0, 0, random.randint(0, c[i])]) for i in range(len(E))]
    b = random_b(V, random.randint(0, 6))
    N = Net(V, E, c, cost, b, lo)
    ref = lp(N)
    f = feasible_flow_lb(N)
    if ref is None:
        oktwo &= f is None
        continue
    cnt += 1
    oktwo &= f is not None and feasible(N, f)
    g, it, okst = cycle_cancel(N, f)
    oktwo &= feasible(N, g) and abs(total_cost(N, g) - ref[0]) < 1e-6
    # the residual graph without lower bounds (backward capacity f) can leave the feasible region
    arcs_wrong = []
    for i, (u, v) in enumerate(E):
        if c[i] - f[i] > 0:
            arcs_wrong.append((u, v, c[i] - f[i], cost[i], i, +1))
        if f[i] > 0:
            arcs_wrong.append((v, u, f[i], -cost[i], i, -1))
    h = list(f)
    for _ in range(50):
        cyc = negative_cycle(V, arcs_wrong)
        if cyc is None:
            break
        R = min(a[2] for a in cyc)
        augment(h, cyc, R)
        arcs_wrong = []
        for i, (u, v) in enumerate(E):
            if c[i] - h[i] > 0:
                arcs_wrong.append((u, v, c[i] - h[i], cost[i], i, +1))
            if h[i] > 0:
                arcs_wrong.append((v, u, h[i], -cost[i], i, -1))
    if any(h[i] < lo[i] for i in range(len(E))):
        okres_need += 1
check(f"two-stage general min-cost flow (lower bounds, balances) = LP on {cnt} feasible random instances", oktwo)
check("  the residual graph must give backward capacity f - l: with backward capacity f, cycle canceling violates a "
      "lower bound on some instances", okres_need > 0, f"{okres_need}")


# ============================================================================ 2. successive shortest paths
def bellman_ford(V, arcs, s):
    d = {v: INF for v in V}
    par = {v: None for v in V}
    d[s] = 0
    for _ in range(len(V) - 1):
        ch = False
        for a in arcs:
            u, v, w = a[0], a[1], a[3]
            if d[u] + w < d[v] - 1e-12:
                d[v] = d[u] + w
                par[v] = a
                ch = True
        if not ch:
            break
    return d, par


def dijkstra(V, arcs, s, w):
    """Textbook Dijkstra (each vertex finalized once) with arc weights w(a)."""
    adj = {v: [] for v in V}
    for a in arcs:
        adj[a[0]].append(a)
    d = {v: INF for v in V}
    par = {v: None for v in V}
    d[s] = 0
    done = set()
    pq = [(0, 0, s)]
    k = 1
    while pq:
        du, _, u = heapq.heappop(pq)
        if u in done:
            continue
        done.add(u)
        for a in adj[u]:
            v = a[1]
            if v not in done and du + w(a) < d[v] - 1e-12:
                d[v] = du + w(a)
                par[v] = a
                heapq.heappush(pq, (d[v], k, v))
                k += 1
    return d, par


def path_to(par, s, t):
    p = []
    v = t
    while v != s:
        a = par[v]
        p.append(a)
        v = a[0]
    p.reverse()
    return p


def ssp_prepare(N, strong=True):
    """Enforce the assumptions: start from psi = c on edges of cost <= 0 and psi = l elsewhere (all residual costs then
    non-negative); optionally add a vertex q with expensive uncapacitated edges to and from every vertex."""
    M = 1 + 2 * sum(abs(k) for k in N.cost) + 1
    V, E = list(N.V), list(N.E)
    c, cost, lo = list(N.c), list(N.cost), list(N.lo)
    if strong:
        V.append("q")
        for v in N.V:
            E += [(v, "q"), ("q", v)]
            c += [10 ** 6, 10 ** 6]
            cost += [M, M]
            lo += [0, 0]
    b = dict(N.b)
    b.setdefault("q", 0)
    N2 = Net(V, E, c, cost, b, lo)
    # the note saturates every edge of cost <= 0; cost-0 edges may stay at l (their residual costs are 0 either way),
    # which keeps uncapacitated cost-0 edges finite
    psi = [N2.c[i] if N2.cost[i] < 0 or (N2.cost[i] == 0 and N2.c[i] != INF) else N2.lo[i] for i in range(len(E))]
    return N2, psi, M


def ssp(N, fast=False, update="sum", pick="arbitrary", stop_on_q=False, check_lemma=True):
    """SuccessiveShortestPaths (fast=False: Bellman-Ford) or FastSuccessiveShortestPaths (fast=True: Dijkstra on reduced
    costs; update 'sum': pi <- pi + dist, 'printed': pi <- dist). Returns dict with the flow on the original edges."""
    N2, psi, M = ssp_prepare(N)
    m0 = len(N.E)
    pi = {v: 0 for v in N2.V}
    out = dict(lemma=True, lemma3=True, used_q=False, reported=False, iters=0, wrong_dist=False, paths=[], pis=[],
               dists=[])
    bpsi = {v: N2.b[v] - netin(N2, psi, v) for v in N2.V}
    B = sum(abs(x) for x in bpsi.values()) / 2
    out["B0"] = B
    while B > 0:
        arcs = residual_arcs(N2, psi)
        sup = [v for v in N2.V if bpsi[v] < 0]
        dem = [v for v in N2.V if bpsi[v] > 0]
        s = random.choice(sup) if pick == "arbitrary" else sup[0]
        t = random.choice(dem) if pick == "arbitrary" else dem[0]
        if not fast:
            d, par = bellman_ford(N2.V, arcs, s)
        else:
            d, par = dijkstra(N2.V, arcs, s, lambda a: pi[a[0]] + a[3] - pi[a[1]])
            dtrue, _ = bellman_ford(N2.V, arcs, s)
            if abs((d[t] - pi[s] + pi[t]) - dtrue[t]) > 1e-9:
                out["wrong_dist"] = True
        sigma = path_to(par, s, t)
        if any("q" in (a[0], a[1]) for a in sigma):
            out["used_q"] = True
            if stop_on_q:
                out["reported"] = True
                return out
        R = min([-bpsi[s], bpsi[t]] + [a[2] for a in sigma])
        out["paths"].append(([(a[0], a[1]) for a in sigma], R, sum(a[3] for a in sigma)))
        out["dists"].append(dict(d))
        augment(psi, sigma, R)
        B -= R
        bpsi = {v: N2.b[v] - netin(N2, psi, v) for v in N2.V}
        out["iters"] += 1
        if fast:
            if update == "sum":
                pi = {v: pi[v] + d[v] for v in N2.V}
            else:
                pi = {v: d[v] for v in N2.V}
            out["pis"].append(dict(pi))
            if check_lemma:
                out["lemma3"] &= all(pi[a[0]] + a[3] - pi[a[1]] >= -1e-9 for a in residual_arcs(N2, psi))
        if check_lemma:
            out["lemma"] &= negative_cycle(N2.V, residual_arcs(N2, psi), shuffle=False) is None
        out["feasible_psi"] = all(N2.lo[i] <= psi[i] <= N2.c[i] for i in range(len(N2.E)))
    out["flow"] = psi[:m0]
    out["q_flow"] = sum(psi[m0:])
    return out


okssp = oklemma = okB = okq = True
false_reports = 0
nfe = 0
for _ in range(200):
    n = random.choice([3, 4, 5, 6])
    V, E, c, cost = random_net(n, p=random.choice([0.35, 0.55]), cmax=5, kmax=6)
    if not E:
        continue
    lo = [random.choice([0, 0, random.randint(0, c[i])]) for i in range(len(E))]
    b = random_b(V, random.randint(1, 6))
    N = Net(V, E, c, cost, b, lo)
    ref = lp(N)
    out = ssp(N)
    oklemma &= out["lemma"]
    okB &= out["iters"] <= out["B0"]
    if ref is None:
        okssp &= out["q_flow"] > 0
    else:
        nfe += 1
        okssp &= out["q_flow"] == 0 and feasible(N, out["flow"]) and abs(total_cost(N, out["flow"]) - ref[0]) < 1e-6
        rep = ssp(N, stop_on_q=True, check_lemma=False)
        false_reports += rep["reported"]
check(f"SuccessiveShortestPaths (arbitrary s and t, Bellman-Ford) = LP on {nfe} feasible instances; on the others it "
      f"ends with flow on q's edges", okssp)
check("  Lemma G.1: no negative residual cycle after every iteration", oklemma)
check("  at most B iterations (integer data, B after enforcing the assumptions)", okB)
check("  'report infeasible as soon as a path uses q' is wrong when t is arbitrary: false reports on feasible inputs",
      false_reports > 0, f"{false_reports} of {nfe}")
# the smallest such example: two separate supply-demand pairs
Nsep = Net(["s1", "t1", "s2", "t2"], [("s1", "t1"), ("s2", "t2")], [1, 1], [1, 1], {"s1": -1, "t1": 1, "s2": -1, "t2": 1})
random.seed(5)
seen_q = False
for _ in range(20):
    o = ssp(Nsep, stop_on_q=True, check_lemma=False)
    seen_q |= o["reported"]
o2 = ssp(Nsep)
check("  example s1->t1, s2->t2 (one unit each): pairing s1 with t2 routes through q; run to the end, q carries nothing",
      seen_q and o2["q_flow"] == 0 and total_cost(Nsep, o2["flow"]) == 2)
random.seed(374107)

# ============================================================================ 3. potentials
okG2 = okpath = True
for _ in range(300):
    n = random.choice([3, 4, 5, 6])
    V, E, c, cost = random_net(n, p=0.5, kmax=5)
    arcs = [(u, v, 1, cost[i], i, 1) for i, (u, v) in enumerate(E)]
    hasneg = negative_cycle(V, arcs) is not None
    # potentials: distances from a new vertex with 0-edges to every vertex
    V2 = V + ["src"]
    d, _ = bellman_ford(V2, arcs + [("src", v, 1, 0, -1, 1) for v in V], "src")
    good = all(d[u] + w - d[v] >= -1e-9 for (u, v, _, w, _, _) in arcs)
    okG2 &= hasneg != good
    pi = {v: random.randint(-9, 9) for v in V}
    for _ in range(5):
        k = random.randint(1, 4)
        walk = [random.choice(V)]
        for _ in range(k):
            walk.append(random.choice(V))
        w = [random.randint(-5, 5) for _ in range(k)]
        red = sum(pi[walk[j]] + w[j] - pi[walk[j + 1]] for j in range(k))
        okpath &= red == pi[walk[0]] + sum(w) - pi[walk[-1]]
check("Lemma G.2 on 300 random digraphs: no negative cycle iff some potential makes every reduced cost >= 0", okG2)
check("reduced cost of a path = pi(start) + cost - pi(end) (intermediate potentials cancel)", okpath)

okfast = okL3 = True
lit_neg = lit_wrong = 0
cnt = 0
for _ in range(200):
    n = random.choice([3, 4, 5, 6])
    V, E, c, cost = random_net(n, p=random.choice([0.4, 0.6]), cmax=4, kmax=6)
    if not E:
        continue
    b = random_b(V, random.randint(1, 6))
    N = Net(V, E, c, cost, b)
    ref = lp(N)
    if ref is None:
        continue
    cnt += 1
    out = ssp(N, fast=True, update="sum")
    okfast &= out["q_flow"] == 0 and feasible(N, out["flow"]) and abs(total_cost(N, out["flow"]) - ref[0]) < 1e-6
    okfast &= not out["wrong_dist"]
    okL3 &= out["lemma3"]
    outp = ssp(N, fast=True, update="printed")
    lit_neg += not outp["lemma3"]
    lit_wrong += outp["wrong_dist"] or outp["q_flow"] > 0 or abs(total_cost(N, outp["flow"]) - ref[0]) > 1e-6
check(f"FastSuccessiveShortestPaths with pi <- pi + dist (Dijkstra) = LP on {cnt} feasible instances; every Dijkstra "
      f"distance is the true one", okfast)
check("  Lemma G.3: after every iteration every residual edge has reduced cost >= 0", okL3)
check("  with the printed update pi <- dist, some reduced costs become negative", lit_neg > 0, f"{lit_neg} of {cnt}")
check("  ... and Dijkstra then returns wrong distances or a non-optimal flow on some instances", lit_wrong > 0,
      f"{lit_wrong} of {cnt}")


# ============================================================================ 4. G.4
def fulkerson(N):
    """Replace every edge u->v by u->z, v->z (uncapacitated); b(z) = c - l, b(u) += l, b(v) -= c."""
    V = list(N.V)
    E, c, cost = [], [], []
    b = dict(N.b)
    for i, (u, v) in enumerate(N.E):
        z = ("z", i)
        V.append(z)
        E += [(u, z), (v, z)]
        c += [INF, INF]
        cost += [N.cost[i], 0]
        b[z] = N.c[i] - N.lo[i]
        b[u] += N.lo[i]
        b[v] -= N.c[i]
    return Net(V, E, c, cost, b)


okful = oksize = okbip = okrec = oksign = True
for _ in range(200):
    n = random.choice([3, 4, 5])
    V, E, c, cost = random_net(n, p=0.6, cmax=5, kmax=5)
    if not E:
        continue
    lo = [random.choice([0, random.randint(0, c[i])]) for i in range(len(E))]
    b = random_b(V, random.randint(0, 6))
    N = Net(V, E, c, cost, b, lo)
    H = fulkerson(N)
    oksize &= len(H.V) == len(V) + len(E) and len(H.E) == 2 * len(E)
    oksign &= all(H.b[("z", i)] >= 0 for i in range(len(E)))
    oksign &= all(not (isinstance(u, tuple)) and isinstance(v, tuple) for (u, v) in H.E)
    r1, r2 = lp(N), lp(H)
    if r1 is None:
        okful &= r2 is None
        continue
    okful &= r2 is not None and abs(r1[0] - (r2[0] + sum(lo[i] * cost[i] for i in range(len(E))))) < 1e-6
    okbip &= all(H.b[v] <= 1e-9 for v in V)
    # recover f from f'
    fp = r2[1]
    f = [fp[2 * i] + lo[i] for i in range(len(E))]
    okrec &= feasible(N, f) and abs(total_cost(N, f) - r1[0]) < 1e-6
    # and the forward map
    x = r1[1]
    fpp = []
    for i in range(len(E)):
        fpp += [x[i] - lo[i], c[i] - x[i]]
    okrec &= feasible(H, fpp) and abs(total_cost(H, fpp) - (total_cost(N, x) - sum(lo[i] * cost[i]
                                                                                    for i in range(len(E))))) < 1e-6
check("Fulkerson's reduction: H has V + E vertices and 2E uncapacitated edges, all from an old vertex to a new one",
      oksize and oksign)
check("  min cost(G) = min cost(H) + sum l(e) cost(e); infeasible exactly together (200 random instances, LP)", okful)
check("  in feasible instances every old vertex has balance <= 0 in H (a supply node), every z has c - l >= 0", okbip)
check("  the maps f -> f' and f' -> f preserve feasibility and shift the cost by sum l(e) cost(e)", okrec)


def transport_lp(sup, dem, C):
    V = [("p", i) for i in range(len(sup))] + [("d", j) for j in range(len(dem))]
    E, c, cost = [], [], []
    for i in range(len(sup)):
        for j in range(len(dem)):
            if C[i][j] is not None:
                E.append((("p", i), ("d", j)))
                c.append(INF)
                cost.append(C[i][j])
    b = {("p", i): -sup[i] for i in range(len(sup))}
    b.update({("d", j): dem[j] for j in range(len(dem))})
    return lp(Net(V, E, c, cost, b))


def transport_assign(sup, dem, C):
    rows = [i for i in range(len(sup)) for _ in range(sup[i])]
    cols = [j for j in range(len(dem)) for _ in range(dem[j])]
    BIGM = 10 ** 6
    M = np.array([[C[i][j] if C[i][j] is not None else BIGM for j in cols] for i in rows], dtype=float)
    r, cc = linear_sum_assignment(M)
    tot = M[r, cc].sum()
    return None if tot >= BIGM else tot


okass = True
for _ in range(150):
    p, q = random.randint(1, 3), random.randint(1, 3)
    tot = random.randint(1, 7)
    sup = [0] * p
    dem = [0] * q
    for _ in range(tot):
        sup[random.randrange(p)] += 1
        dem[random.randrange(q)] += 1
    C = [[random.randint(0, 9) if random.random() < 0.85 else None for _ in range(q)] for _ in range(p)]
    r = transport_lp(sup, dem, C)
    a = transport_assign(sup, dem, C)
    okass &= (r is None and a is None) or (r is not None and a is not None and abs(r[0] - a) < 1e-6)
check("transportation = assignment after replacing each vertex v by |b(v)| copies (150 random instances)", okass)

# single-supply transshipment
okss = okft = okssp_tree = oktree = True
for _ in range(150):
    n = random.choice([3, 4, 5, 6])
    V, E, c, cost = random_net(n, p=0.6, kmax=9, neg=False)
    s = 0
    G = nx.DiGraph()
    G.add_nodes_from(V)
    for i, (u, v) in enumerate(E):
        G.add_edge(u, v, weight=cost[i])
    reach = nx.descendants(G, s) | {s}
    if len(reach) < n:
        continue
    b = {v: (random.randint(0, 3) if v != s else 0) for v in V}
    b[s] = -sum(b.values())
    N = Net(V, E, [INF] * len(E), cost, b)
    ref = lp(N)
    dist = nx.single_source_dijkstra_path_length(G, s)
    okss &= abs(ref[0] - sum(dist[v] * b[v] for v in V)) < 1e-6
    # canonical tree flow
    par = nx.single_source_dijkstra_path(G, s)
    T = {v: (par[v][-2], v) for v in V if v != s}
    children = {}
    for v, (u, _) in T.items():
        children.setdefault(u, []).append(v)

    def sub(v):
        return b[v] + sum(sub(w) for w in children.get(v, []))
    fT = [0] * len(E)
    for v, e in T.items():
        fT[E.index(e)] = sub(v)
    okft &= feasible(N, fT) and abs(total_cost(N, fT) - ref[0]) < 1e-6
    # unique shortest-path tree => SSP builds f_T
    uniq = all(dist[u] + cost[i] > dist[v] for i, (u, v) in enumerate(E) if (u, v) not in T.values() and v != s)
    if uniq:
        out = ssp(N, check_lemma=False)
        okssp_tree &= [round(x) for x in out["flow"]] == fT
    # a minimum-cost flow supported on a tree (network simplex returns one)
    Gn = nx.DiGraph()
    for v in V:
        Gn.add_node(v, demand=b[v])
    for i, (u, v) in enumerate(E):
        Gn.add_edge(u, v, weight=cost[i])
    cst, fl = nx.network_simplex(Gn)
    supp = nx.Graph()
    supp.add_nodes_from(V)
    supp.add_edges_from((u, v) for u in fl for v in fl[u] if fl[u][v] > 0)
    oktree &= abs(cst - ref[0]) < 1e-6 and nx.is_forest(supp)
check("single-supply transshipment: minimum cost = sum_v dist(s, v) b(v) (150 random networks, LP)", okss)
check("  the canonical flow on a shortest-path tree (f_T(u->v) = total demand below v) is feasible and optimal", okft)
check("  with a unique shortest-path tree, successive shortest paths produces exactly f_T", okssp_tree)
check("  some minimum-cost flow is positive only on the edges of a forest (network simplex)", oktree)

# ============================================================================ 5. the page's examples
V = ["s", "a", "b", "t"]
E = [("s", "a"), ("s", "b"), ("a", "b"), ("a", "t"), ("b", "t")]
cap = [2, 2, 2, 2, 3]
cst = [1, 3, 1, 4, 1]
bx = {"s": -4, "a": 0, "b": 0, "t": 4}
NX = Net(V, E, cap, cst, bx)
opt, x = lp(NX)
check("page example: minimum cost 16 (LP and networkx)", abs(opt - 16) < 1e-9 and nx_cost(NX) == 16)
fopt = [2, 2, 1, 1, 3]
check("  optimal flow s->a 2, s->b 2, a->b 1, a->t 1, b->t 3", feasible(NX, fopt) and total_cost(NX, fopt) == 16)
f18 = [2, 2, 0, 2, 2]
check("  the feasible flow s->a 2, s->b 2, a->t 2, b->t 2 costs 2 + 6 + 8 + 2 = 18",
      feasible(NX, f18) and total_cost(NX, f18) == 18)
arcs = residual_arcs(NX, f18)
cyc = [("a", "b"), ("b", "t"), ("t", "a")]
A = {(a[0], a[1]): a for a in arcs}
check("  its residual graph has the cycle a->b->t->a: capacities 2, 1, 2, costs 1, 1, -4, total -2",
      all(e in A for e in cyc) and [A[e][2] for e in cyc] == [2, 1, 2] and [A[e][3] for e in cyc] == [1, 1, -4])
g = list(f18)
augment(g, [A[e] for e in cyc], 1)
check("  canceling it (1 unit) gives the optimal flow, cost 18 - 2 = 16, with no negative residual cycle left",
      g == fopt and total_cost(NX, g) == 16 and negative_cycle(V, residual_arcs(NX, g)) is None)
neg_all = []
G = nx.DiGraph()
for a in arcs:
    G.add_edge(a[0], a[1], w=a[3])
for cy in nx.simple_cycles(G):
    w = sum(G[cy[k]][cy[(k + 1) % len(cy)]]["w"] for k in range(len(cy)))
    if w < 0:
        neg_all.append((cy, w))
check("  ... and it is the only negative residual cycle of the 18-flow", len(neg_all) == 1 and neg_all[0][1] == -2,
      f"{neg_all}")
# successive shortest paths, deterministic
random.seed(1)
out = ssp(NX, fast=True, update="sum", pick="first")
paths = [(p_, R, c_) for (p_, R, c_) in out["paths"]]
check("  SSP: paths s-a-b-t (cost 3, 2 units), s-b-t (4, 1 unit), s-b-a-t (6, 1 unit, uses b->a backward)",
      paths == [([("s", "a"), ("a", "b"), ("b", "t")], 2, 3), ([("s", "b"), ("b", "t")], 1, 4),
                ([("s", "b"), ("b", "a"), ("a", "t")], 1, 6)], f"{paths}")
check("  SSP total 2*3 + 4 + 6 = 16, the minimum", total_cost(NX, out["flow"]) == 16 and out["flow"] == fopt)
pis = [tuple(p[v] for v in V) for p in out["pis"]]
ds = [tuple(d[v] for v in V) for d in out["dists"]]
check("  Dijkstra distances (reduced costs) (0,1,2,3), (0,1,1,1), (0,0,0,2); potentials after each iteration "
      "(0,1,2,3), (0,2,3,4), (0,2,3,6)",
      ds == [(0, 1, 2, 3), (0, 1, 1, 1), (0, 0, 0, 2)] and pis == [(0, 1, 2, 3), (0, 2, 3, 4), (0, 2, 3, 6)],
      f"{ds} {pis}")
# reduced costs in the second iteration
f1 = [2, 0, 2, 0, 2]
pi1 = {"s": 0, "a": 1, "b": 2, "t": 3}
red = {(a[0], a[1]): pi1[a[0]] + a[3] - pi1[a[1]] for a in residual_arcs(NX, f1)}
check("  second iteration reduced costs: s->b 1, a->t 2, b->t 0, b->a 0, a->s 0, t->b 0 (all >= 0)",
      red == {("s", "b"): 1, ("a", "t"): 2, ("b", "t"): 0, ("b", "a"): 0, ("a", "s"): 0, ("t", "b"): 0}, f"{red}")
f2 = [2, 1, 2, 0, 3]
pil = {"s": 0, "a": 1, "b": 1, "t": 1}
redl = {(a[0], a[1]): pil[a[0]] + a[3] - pil[a[1]] for a in residual_arcs(NX, f2)}
check("  with the printed update pi <- dist = (0,1,1,1), the residual edge b->s gets reduced cost 1 - 3 - 0 = -2",
      redl[("b", "s")] == -2)

# transportation example
sup = [3, 2]
dem = [2, 2, 1]
C = [[4, 6, 9], [5, 3, 8]]
r = transport_lp(sup, dem, C)
check("transportation example: minimum cost 23 (LP) = assignment on 5 x 5 copies", abs(r[0] - 23) < 1e-9 and
      transport_assign(sup, dem, C) == 23)
plan = {("p", "x"): 2, ("p", "z"): 1, ("q", "y"): 2}
check("  plan p->x 2, p->z 1, q->y 2: 8 + 9 + 6 = 23", 2 * 4 + 1 * 9 + 2 * 3 == 23)
alts = []
for pz in range(0, 2):
    for px in range(0, 3):
        py = 3 - px - pz
        if py < 0:
            continue
        qx, qy, qz = 2 - px, 2 - py, 1 - pz
        if min(qx, qy, qz) < 0:
            continue
        alts.append(4 * px + 6 * py + 9 * pz + 5 * qx + 3 * qy + 8 * qz)
check("  23 is the unique minimum among all integral plans", sorted(alts)[0] == 23 and sorted(alts)[1] > 23,
      f"{sorted(alts)}")

# concept page example: unit diamond
Vd = ["s", "a", "b", "t"]
Ed = [("s", "a"), ("s", "b"), ("a", "b"), ("a", "t"), ("b", "t")]
Nd = Net(Vd, Ed, [1] * 5, [1, 3, 1, 3, 1], {"s": -2, "a": 0, "b": 0, "t": 2})
random.seed(2)
o = ssp(Nd, fast=True, update="sum", pick="first")
check("concept example: SSP paths s-a-b-t (cost 3) then s-b-a-t (3 - 1 + 3 = 5), total 8",
      [(p_, c_) for (p_, R, c_) in o["paths"]] == [([("s", "a"), ("a", "b"), ("b", "t")], 3),
                                                  ([("s", "b"), ("b", "a"), ("a", "t")], 5)])
check("  final flow = s-a-t plus s-b-t (a->b empty), cost 8 = minimum", o["flow"] == [1, 1, 0, 1, 1] and
      lp(Nd)[0] == 8)
fd = [1, 0, 1, 0, 1]
pid = {"s": 0, "a": 1, "b": 2, "t": 3}
redd = {(a[0], a[1]): pid[a[0]] + a[3] - pid[a[1]] for a in residual_arcs(Nd, fd)}
check("  after the first path, potentials (0,1,2,3) give reduced costs s->b 1, a->t 1, b->a 0, a->s 0, t->b 0",
      redd == {("s", "b"): 1, ("a", "t"): 1, ("b", "a"): 0, ("a", "s"): 0, ("t", "b"): 0}, f"{redd}")
fwd = nx.DiGraph()
fwd.add_nodes_from(Vd)
fwd.add_edges_from((a[0], a[1]) for a in residual_arcs(Nd, fd) if a[5] == 1)
check("  using forward residual edges only, s cannot reach t after the first path (greedy path-by-path gets stuck)",
      not nx.has_path(fwd, "s", "t"))


# ============================================================================ review R30: choosing the cycle (p. 4)
def _min_edges_negcycle_brute(n, w):
    for k in range(1, n + 1):
        for cyc in itertools.permutations(range(n), k):
            if cyc[0] != min(cyc):
                continue
            es = [(cyc[i], cyc[(i + 1) % k]) for i in range(k)]
            if all(e in w for e in es) and sum(w[e] for e in es) < 0:
                return k
    return None


def _min_edges_negcycle_dp(n, w):
    """Smallest k such that some closed walk of exactly k edges has negative cost (k rounds of relaxation from each
    start vertex): polynomial, O(V^2 E) in all."""
    for k in range(1, n + 1):
        for s in range(n):
            d = [INF] * n
            d[s] = 0
            for _ in range(k):
                nd = [INF] * n
                for (u, v), x in w.items():
                    if d[u] + x < nd[v]:
                        nd[v] = d[u] + x
                d = nd
            if d[s] < 0:
                return k
    return None


_rng = random.Random(30)
ok_fe, n_neg = True, 0
for _ in range(400):
    n = _rng.randint(2, 6)
    w = {(u, v): _rng.randint(-5, 6) for u in range(n) for v in range(n) if u != v and _rng.random() < 0.5}
    a_ = _min_edges_negcycle_brute(n, w)
    ok_fe &= a_ == _min_edges_negcycle_dp(n, w)
    n_neg += a_ is not None
check("p. 4: the negative cycle with fewest edges is NOT NP-hard: its length = the smallest k with a negative closed "
      "k-edge walk (polynomial recurrence), brute force on 400 digraphs", ok_fe, f"{n_neg} with a negative cycle")
# the most negative simple cycle with all costs -1 is a longest cycle (Hamiltonian when one exists)
Kn = {(u, v): -1 for u in range(4) for v in range(4) if u != v}
best = min(sum(Kn[(c_[i], c_[(i + 1) % len(c_)])] for i in range(len(c_)))
           for k in range(2, 5) for c_ in itertools.permutations(range(4), k))
check("with every cost -1 the most negative simple cycle is a longest one (K4: cost -4, Hamiltonian)", best == -4)


# ============================================================================ page text
def page_checks():
    if not os.path.exists(PAGE):
        check("page exists", False, PAGE)
        return
    txt = open(PAGE, encoding="utf-8").read().replace(" ", "")
    for s_ in ["18-2=16", "2\\cdot3+4+6=16", "8+9+6=23", "1-3-0=-2", "butthatoneispolynomial"]:
        check(f"page mentions '{s_}'", s_ in txt)
    if os.path.exists(CONCEPT):
        ct = open(CONCEPT, encoding="utf-8").read().replace(" ", "")
        check("concept page mentions '3-1+3=5'", "3-1+3=5" in ct)
        check("concept page: 'at most B iterations' qualified by integer data", "iterationswithintegercapacitiesandbalances" in ct)


page_checks()
print()
if FAIL:
    print(f"{len(FAIL)} FAILED")
    sys.exit(1)
print("ALL OK")
