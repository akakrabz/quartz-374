#!/usr/bin/env python3
"""Checks for content/2-algorithms/09-all-pairs-shortest-paths-exercises.md (solved exercises 9.1-9.10 of Erickson's
Algorithms).

Every algorithm is implemented the way the page states it (LeyzorekAPSP and FloydWarshall with predecessor pointers,
the negative-cycle variants of Johnson / Leyzorek / Floyd-Warshall, Bellman-Ford negative-cycle extraction, the
zero-cycle subgraph, the k-subset distances, arbitrage, Morty's walk, vertex elimination, boolean matrix products and
transitive closures) and compared with an independent brute force -- enumeration of all simple paths and simple cycles
-- on many random small digraphs with negative and zero edges.  Every example and counterexample on the page is
re-derived.  Exercise 11 (skipped on the page) is also run as printed, to back the remark about its typos."""
import heapq
import itertools
import math
import random
import sys
from fractions import Fraction

sys.setrecursionlimit(10000)
random.seed(374)
FAIL = []
INF = math.inf
NINF = -math.inf


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail != "" else ""))
    if not cond:
        FAIL.append(name)


# ============================================================================ random graphs and brute force
def rand_graph(n, p, lo, hi):
    """Directed graph without loops as a dict {(u, v): weight}."""
    return {(u, v): random.randint(lo, hi) for u in range(n) for v in range(n) if u != v and random.random() < p}


def out_adj(n, E):
    adj = [[] for _ in range(n)]
    for (u, v) in E:
        adj[u].append(v)
    return adj


def simple_paths(n, E, u):
    """All simple paths starting at u, as vertex lists (including the one-vertex path [u])."""
    adj = out_adj(n, E)
    out = []

    def go(path, seen):
        out.append(list(path))
        for w in adj[path[-1]]:
            if w not in seen:
                seen.add(w)
                path.append(w)
                go(path, seen)
                path.pop()
                seen.discard(w)

    go([u], {u})
    return out


def simple_cycles(n, E):
    """All simple directed cycles (vertex lists, smallest vertex first, length >= 2)."""
    cyc = []
    adj = out_adj(n, E)
    for s in range(n):
        def go(path, seen):
            for w in adj[path[-1]]:
                if w == s and len(path) >= 2:
                    cyc.append(list(path))
                elif w > s and w not in seen:
                    seen.add(w)
                    path.append(w)
                    go(path, seen)
                    path.pop()
                    seen.discard(w)
        go([s], {s})
    return cyc


def plen(E, path):
    return sum(E[(path[i], path[i + 1])] for i in range(len(path) - 1))


def clen(E, cyc):
    return sum(E[(cyc[i], cyc[(i + 1) % len(cyc)])] for i in range(len(cyc)))


def reach(n, E):
    R = [[u == v for v in range(n)] for u in range(n)]
    for (u, v) in E:
        R[u][v] = True
    for k in range(n):
        for i in range(n):
            if R[i][k]:
                for j in range(n):
                    if R[k][j]:
                        R[i][j] = True
    return R


def brute_apsp(n, E):
    """True distances with the book's conventions: inf if unreachable, -inf if u reaches a negative cycle that
    reaches v, else the shortest simple path (all cycles on u-v walks are then non-negative)."""
    R = reach(n, E)
    bad = set()
    for c in simple_cycles(n, E):
        if clen(E, c) < 0:
            bad.update(c)
    D = [[INF] * n for _ in range(n)]
    for u in range(n):
        for p in simple_paths(n, E, u):
            v = p[-1]
            D[u][v] = min(D[u][v], plen(E, p))
        for v in range(n):
            if any(R[u][x] and R[x][v] for x in bad):
                D[u][v] = NINF
    return D


def has_negcycle(n, E):
    return any(clen(E, c) < 0 for c in simple_cycles(n, E))


def quick_negcycle(n, E):
    """Only used to generate inputs: plain Floyd-Warshall, negative diagonal."""
    d = [[0 if u == v else E.get((u, v), INF) for v in range(n)] for u in range(n)]
    for r in range(n):
        for u in range(n):
            for v in range(n):
                if d[u][r] + d[r][v] < d[u][v]:
                    d[u][v] = d[u][r] + d[r][v]
    return any(d[x][x] < 0 for x in range(n))


def rand_noneg(n, p, lo, hi):
    while True:
        E = rand_graph(n, p, lo, hi)
        if not quick_negcycle(n, E):
            assert not has_negcycle(n, E) if n <= 5 else True
            return E


def rand_n(lo=2, hi=6):
    """Mostly small sizes; size 7 now and then (exhaustive path enumeration is exponential)."""
    return 7 if random.random() < 0.06 else random.randint(lo, hi)


def is_cycle_of(E, cyc):
    k = len(cyc)
    return k >= 2 and len(set(cyc)) == k and all((cyc[i], cyc[(i + 1) % k]) in E for i in range(k))


def is_path_of(E, path):
    return len(set(path)) == len(path) and all((path[i], path[i + 1]) in E for i in range(len(path) - 1))


# ============================================================================ the chapter's algorithms
def init_tables(n, E):
    dist = [[0 if u == v else E.get((u, v), INF) for v in range(n)] for u in range(n)]
    pred = [[u if (u != v and (u, v) in E) else None for v in range(n)] for u in range(n)]
    return dist, pred


def lg_ceil(n):
    return 0 if n <= 1 else math.ceil(math.log2(n))


def LeyzorekAPSP(n, E, order=None):
    """Book's LeyzorekAPSP (in place), with the pred update of Exercise 1(a): pred[u,v] <- pred[x,v]."""
    order = order or list(range(n))
    dist, pred = init_tables(n, E)
    for _ in range(lg_ceil(n)):
        for u in order:
            for v in order:
                for x in order:
                    if dist[u][v] > dist[u][x] + dist[x][v]:
                        dist[u][v] = dist[u][x] + dist[x][v]
                        pred[u][v] = pred[x][v]
    return dist, pred


def LeyzorekPairs(n, E, order=None):
    """Exercise 1(a), fixed: the same algorithm on weights (w(e), 1) compared lexicographically."""
    order = order or list(range(n))
    INFP = (INF, INF)
    dist = [[(0, 0) if u == v else ((E[(u, v)], 1) if (u, v) in E else INFP) for v in range(n)] for u in range(n)]
    pred = [[u if (u != v and (u, v) in E) else None for v in range(n)] for u in range(n)]
    add = lambda a, b: (a[0] + b[0], a[1] + b[1])
    for _ in range(lg_ceil(n)):
        for u in order:
            for v in order:
                for x in order:
                    c = add(dist[u][x], dist[x][v])
                    if dist[u][v] > c:
                        dist[u][v] = c
                        pred[u][v] = pred[x][v]
    return [[d[0] for d in row] for row in dist], pred, dist


def FloydWarshall(n, E, order=None):
    """Book's FloydWarshall with the pred update of Exercise 1(b): pred[u,v] <- pred[r,v]."""
    order = order or list(range(n))
    dist, pred = init_tables(n, E)
    for r in order:
        for u in order:
            for v in order:
                if dist[u][v] > dist[u][r] + dist[r][v]:
                    dist[u][v] = dist[u][r] + dist[r][v]
                    pred[u][v] = pred[r][v]
    return dist, pred


def FloydWarshallPairs(n, E, order=None):
    """9.1(b) remark: the pair trick of 9.1(a) applied to FloydWarshall."""
    order = order or list(range(n))
    INFP = (INF, INF)
    dist = [[(0, 0) if u == v else ((E[(u, v)], 1) if (u, v) in E else INFP) for v in range(n)] for u in range(n)]
    pred = [[u if (u != v and (u, v) in E) else None for v in range(n)] for u in range(n)]
    for r in order:
        for u in order:
            for v in order:
                c = (dist[u][r][0] + dist[r][v][0], dist[u][r][1] + dist[r][v][1])
                if dist[u][v] > c:
                    dist[u][v] = c
                    pred[u][v] = pred[r][v]
    return [[d[0] for d in row] for row in dist], pred


def follow(pred, u, v, n):
    """Walk the pointers back from v; return the path u..v, or None if they cycle or break."""
    path = [v]
    x = v
    for _ in range(n):
        if x == u:
            return path[::-1]
        x = pred[u][x]
        if x is None:
            return None
        path.append(x)
    return path[::-1] if x == u else None


def pred_ok(n, E, dist, pred):
    for u in range(n):
        for v in range(n):
            if u == v or dist[u][v] in (INF, NINF):
                continue
            p = follow(pred, u, v, n)
            if p is None or not is_path_of(E, p) or plen(E, p) != dist[u][v]:
                return False
    return True


def dijkstra(n, adj_w, s):
    """adj_w[u] = list of (v, w >= 0). Binary-heap Dijkstra (lazy deletion)."""
    d = [INF] * n
    d[s] = 0
    pq = [(0, s)]
    while pq:
        du, u = heapq.heappop(pq)
        if du > d[u]:
            continue
        for v, w in adj_w[u]:
            assert w >= 0
            if du + w < d[v]:
                d[v] = du + w
                heapq.heappush(pq, (d[v], v))
    return d


def bellman_ford(N, edges, s, shuffle=True):
    """Book's BellmanFord: V-1 rounds over all edges (in a random fixed order), then the tense-edge test.
    Returns (dist, pred, tense_edge or None)."""
    dist = [INF] * N
    pred = [None] * N
    dist[s] = 0
    edges = list(edges)
    if shuffle:
        random.shuffle(edges)
    for _ in range(N - 1):
        for (u, v, w) in edges:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                pred[v] = u
    for (u, v, w) in edges:
        if dist[u] + w < dist[v]:
            return dist, pred, (u, v, w)
    return dist, pred, None


def bf_negative_cycle(N, edges, s):
    """Exercise 3(a): Bellman-Ford; if an edge u->v is still tense, relax it, walk N pred pointers back from v,
    and read off the cycle through the vertex reached.  Returns (dist, None) or (None, cycle)."""
    dist, pred, t = bellman_ford(N, edges, s)
    if t is None:
        return dist, None
    u, v, w = t
    dist[v] = dist[u] + w
    pred[v] = u
    x = v
    for _ in range(N):
        x = pred[x]
        assert x is not None, "pointer walk reached the source"
    cyc = [x]
    y = pred[x]
    while y != x:
        cyc.append(y)
        y = pred[y]
    return None, cyc[::-1]


def johnson_prices(n, E):
    """Add s = n with 0-edges to every vertex, run Bellman-Ford. Returns (pi, cycle-or-None)."""
    edges = [(u, v, w) for (u, v), w in E.items()] + [(n, v, 0) for v in range(n)]
    dist, cyc = bf_negative_cycle(n + 1, edges, n)
    return (dist[:n] if dist else None), cyc


def JohnsonAPSP(n, E):
    pi, cyc = johnson_prices(n, E)
    assert cyc is None
    adj_w = [[] for _ in range(n)]
    for (u, v), w in E.items():
        adj_w[u].append((v, pi[u] + w - pi[v]))
    D = []
    for u in range(n):
        d = dijkstra(n, adj_w, u)
        D.append([d[v] - pi[u] + pi[v] if d[v] < INF else INF for v in range(n)])
    return D


def sccs(n, E):
    """Kosaraju-Sharir (black box). Returns comp[v] = component id."""
    adj = out_adj(n, E)
    radj = [[] for _ in range(n)]
    for (u, v) in E:
        radj[v].append(u)
    seen, post = [False] * n, []

    def dfs1(v):
        seen[v] = True
        for w in radj[v]:
            if not seen[w]:
                dfs1(w)
        post.append(v)

    for v in range(n):
        if not seen[v]:
            dfs1(v)
    comp = [None] * n

    def dfs2(v, c):
        comp[v] = c
        for w in adj[v]:
            if comp[w] is None:
                dfs2(w, c)

    c = 0
    for v in reversed(post):
        if comp[v] is None:
            dfs2(v, c)
            c += 1
    return comp


def wfs(adj, sources):
    seen = set(sources)
    bag = list(sources)
    while bag:
        v = bag.pop()
        for w in adj[v]:
            if w not in seen:
                seen.add(w)
                bag.append(w)
    return seen


# ---------------------------------------------------------------------------- Exercise 2
def JohnsonNeg(n, E):
    """Exercise 2(a)."""
    comp = sccs(n, E)
    B = set()
    for c in set(comp):
        C = [v for v in range(n) if comp[v] == c]
        idx = {v: i for i, v in enumerate(C)}
        edges = [(idx[u], idx[v], w) for (u, v), w in E.items() if comp[u] == c and comp[v] == c]
        _, _, t = bellman_ford(len(C), edges, 0)
        if t is not None:
            B.update(C)
    keep = [v for v in range(n) if v not in B]
    ix = {v: i for i, v in enumerate(keep)}
    E2 = {(ix[u], ix[v]): w for (u, v), w in E.items() if u in ix and v in ix}
    D2 = JohnsonAPSP(len(keep), E2) if keep else []
    adj = out_adj(n, E)
    D = [[INF] * n for _ in range(n)]
    for u in range(n):
        R = wfs(adj, [u])
        minus = wfs(adj, [x for x in R if x in B])
        for v in range(n):
            if v in minus:
                D[u][v] = NINF
            elif u in ix and v in ix:
                D[u][v] = D2[ix[u]][ix[v]]
    return D, B


def fix_negative(n, dist, in_place=True):
    """Exercises 2(b), 2(c): mark u ->-inf-> v when some x has dist[x,x] < 0 and u reaches x reaches v.
    In place, exactly as the page's pseudocode (in_place=False: write into a copy, reading the original)."""
    D = dist if in_place else [row[:] for row in dist]
    src = dist
    for x in range(n):
        if src[x][x] < 0:
            for u in range(n):
                for v in range(n):
                    if src[u][x] < INF and src[x][v] < INF:
                        D[u][v] = NINF
    return D


# ---------------------------------------------------------------------------- Exercise 3
def FloydWarshallCycle(n, E):
    """Exercise 3(c): before phase r, look for u with dist[u,r] + dist[r,u] < 0; if found, return the cycle made of
    the pointer paths u ~> r (row u) and r ~> u (row r)."""
    dist, pred = init_tables(n, E)
    for r in range(n):
        for u in range(n):
            if u != r and dist[u][r] + dist[r][u] < 0:
                p1 = follow(pred, u, r, n)
                p2 = follow(pred, r, u, n)
                assert p1 is not None and p2 is not None
                return None, p1[:-1] + p2[:-1]
        for u in range(n):
            for v in range(n):
                if dist[u][v] > dist[u][r] + dist[r][v]:
                    dist[u][v] = dist[u][r] + dist[r][v]
                    pred[u][v] = pred[r][v]
    return dist, None


def LeyzorekCycle(n, E, alg=None):
    """Exercise 3(b) (and 3(c) with alg=FloydWarshall): run the algorithm; if some dist[x,x] < 0, Bellman-Ford from x
    with cycle extraction."""
    dist, _ = (alg or LeyzorekAPSP)(n, E)
    xs = [x for x in range(n) if dist[x][x] < 0]
    if not xs:
        return dist, None
    edges = [(u, v, w) for (u, v), w in E.items()]
    d, cyc = bf_negative_cycle(n, edges, xs[0])
    assert cyc is not None
    return None, cyc


# ============================================================================ Exercise 1
print("== Exercise 1: predecessor pointers")
stats = dict(graphs=0, zero=0, leyz_fail=0, leyz_fail_poscyc=0, pairs_fail=0, fw_fail=0, dist_fail=0)
for trial in range(5000):
    n = rand_n()
    E = rand_noneg(n, random.random(), -2, 3)
    order = list(range(n))
    random.shuffle(order)
    T = brute_apsp(n, E)
    cyc = simple_cycles(n, E)
    zero = any(clen(E, c) == 0 for c in cyc)
    stats["graphs"] += 1
    stats["zero"] += zero
    dL, pL = LeyzorekAPSP(n, E, order)
    dP, pP, _ = LeyzorekPairs(n, E, order)
    dF, pF = FloydWarshall(n, E, order)
    dFP, pFP = FloydWarshallPairs(n, E, order)
    if not (dL == T and dP == T and dF == T and dFP == T):
        stats["dist_fail"] += 1
    if not pred_ok(n, E, dL, pL):
        stats["leyz_fail"] += 1
        if not zero:
            stats["leyz_fail_poscyc"] += 1
    if not pred_ok(n, E, dP, pP):
        stats["pairs_fail"] += 1
    if not pred_ok(n, E, dF, pF) or not pred_ok(n, E, dFP, pFP):
        stats["fw_fail"] += 1
check("LeyzorekAPSP, its pair version and FloydWarshall compute the true distances (no negative cycles)",
      stats["dist_fail"] == 0, f"{stats['graphs']} random graphs, weights -2..3, {stats['zero']} with a zero cycle")
check("1(a) plain pred update in LeyzorekAPSP fails on some graphs, and only on graphs with a zero-length cycle",
      stats["leyz_fail"] > 0 and stats["leyz_fail_poscyc"] == 0, f"{stats['leyz_fail']} failures")
check("1(a) (length, #edges) pairs compared lexicographically: pointers always trace shortest paths",
      stats["pairs_fail"] == 0)
check("1(b) FloydWarshall pred update (plain, and with pairs): pointers always trace shortest paths, zero cycles "
      "included",
      stats["fw_fail"] == 0)

# the page's counterexample: a=0, b=1, c=2, d=3; d->c->b->a (1,1,1) and a->b (-1); loops in the order a,b,c,d
CE = {(3, 2): 1, (2, 1): 1, (1, 0): 1, (0, 1): -1}
dL, pL = LeyzorekAPSP(4, CE)
check("1(a) counterexample: Leyzorek distances from d are 3, 2, 1 to a, b, c and are correct",
      dL[3][:3] == [3, 2, 1] and dL == brute_apsp(4, CE), f"{dL[3]}")
check("1(a) counterexample: pred[d,a] = b and pred[d,b] = a (a pointer cycle), pred[d,c] = d",
      pL[3][0] == 1 and pL[3][1] == 0 and pL[3][2] == 3 and follow(pL, 3, 0, 4) is None)
# trace of the first pass for row d, as described on the page
dist, pred = init_tables(4, CE)
log = []
for u in range(4):
    for v in range(4):
        for x in range(4):
            if dist[u][v] > dist[u][x] + dist[x][v]:
                dist[u][v] = dist[u][x] + dist[x][v]
                pred[u][v] = pred[x][v]
                log.append((u, v, x, dist[u][v], pred[u][v]))
check("1(a) counterexample trace: (c,a) via b; (d,a) via c gets pred b; (d,b) via a gets pred a; nothing else",
      log == [(2, 0, 1, 2, 1), (3, 0, 2, 3, 1), (3, 1, 0, 2, 0)], f"{log}")
dP, pP, dpair = LeyzorekPairs(4, CE)
dF, pF = FloydWarshall(4, CE)
check("1(a) pairs fix the counterexample: (d,b) = (2, 2 edges) with pred c; FloydWarshall gets pred[d,b] = c too",
      dpair[3][1] == (2, 2) and pP[3][1] == 2 and pF[3][1] == 2 and pred_ok(4, CE, dP, pP) and pred_ok(4, CE, dF, pF))

# ============================================================================ Exercise 2
print("== Exercise 2: correct distances with negative cycles")
ok2 = dict(a=True, b=True, c=True)
cnt_neg = 0
for trial in range(2500):
    n = random.randint(1, 6)
    E = rand_graph(n, random.random(), -3, 3)
    T = brute_apsp(n, E)
    cnt_neg += has_negcycle(n, E)
    DJ, B = JohnsonNeg(n, E)
    if DJ != T:
        ok2["a"] = False
    dL, _ = LeyzorekAPSP(n, E)
    if fix_negative(n, [r[:] for r in dL], False) != T or fix_negative(n, dL) != T:
        ok2["b"] = False
    dF, _ = FloydWarshall(n, E)
    if fix_negative(n, [r[:] for r in dF], False) != T or fix_negative(n, dF) != T:
        ok2["c"] = False
check("2(a) Johnson + bad components (Bellman-Ford per strong component) + reachability = brute force", ok2["a"],
      f"2500 random graphs, weights -3..3, {cnt_neg} with a negative cycle")
check("2(b) LeyzorekAPSP + negative-diagonal marking (in place, and into a copy) = brute force", ok2["b"])
check("2(c) FloydWarshall + negative-diagonal marking (in place, and into a copy) = brute force", ok2["c"])
# the lemma used: after Leyzorek / Floyd-Warshall, every vertex on a negative simple cycle has dist[x,x] < 0, and
# every vertex with dist[x,x] < 0 lies in a strong component that contains a negative cycle
okl = True
for trial in range(1500):
    n = random.randint(2, 6)
    E = rand_graph(n, random.random(), -3, 3)
    comp = sccs(n, E)
    on = set()
    badc = set()
    for c in simple_cycles(n, E):
        if clen(E, c) < 0:
            on.update(c)
            badc.add(comp[c[0]])
    for alg in (LeyzorekAPSP, FloydWarshall):
        d, _ = alg(n, E)
        neg = {x for x in range(n) if d[x][x] < 0}
        if not (on <= neg and all(comp[x] in badc for x in neg)):
            okl = False
check("2 lemma: on a negative cycle => negative diagonal => in a strong component with a negative cycle", okl)

# ============================================================================ Exercise 3
print("== Exercise 3: returning a negative cycle")
ok3 = dict(a=True, b=True, c=True, cbf=True)
cnt = 0
for trial in range(2500):
    n = rand_n()
    E = rand_graph(n, random.random(), -3, 4)
    neg = has_negcycle(n, E)
    cnt += neg
    T = brute_apsp(n, E)
    # (a) Johnson: Bellman-Ford from the artificial source
    pi, cyc = johnson_prices(n, E)
    if neg:
        if cyc is None or not is_cycle_of(E, cyc) or clen(E, cyc) >= 0:
            ok3["a"] = False
    else:
        if cyc is not None or JohnsonAPSP(n, E) != T:
            ok3["a"] = False
    for key, alg in (("b", LeyzorekCycle), ("c", FloydWarshallCycle),
                     ("cbf", lambda n, E: LeyzorekCycle(n, E, FloydWarshall))):
        d, cyc = alg(n, E)
        if neg:
            if cyc is None or not is_cycle_of(E, cyc) or clen(E, cyc) >= 0:
                ok3[key] = False
        elif cyc is not None or d != T:
            ok3[key] = False
check("3(a) Johnson: Bellman-Ford pointer walk returns a simple negative cycle, else the distances", ok3["a"],
      f"2500 random graphs, {cnt} with a negative cycle")
check("3(b) Leyzorek: negative diagonal, then Bellman-Ford from x returns a simple negative cycle", ok3["b"])
check("3(c) Floyd-Warshall: negative diagonal, then Bellman-Ford from x returns a simple negative cycle", ok3["cbf"])
check("3(c) Floyd-Warshall without Bellman-Ford: the pre-phase test u~>r~>u returns a simple negative cycle",
      ok3["c"])

# ============================================================================ Exercise 4
print("== Exercise 4: zero-length cycles")


def zero_subgraphs(n, E):
    """Returns (pi, Z, H): reduced weights, zero-reduced edges, and the edges of Z inside one strong component of Z."""
    pi, cyc = johnson_prices(n, E)
    assert cyc is None
    red = {(u, v): pi[u] + w - pi[v] for (u, v), w in E.items()}
    assert all(r >= 0 for r in red.values())
    Z = {e: E[e] for e, r in red.items() if r == 0}
    comp = sccs(n, Z)
    H = {e: E[e] for e in Z if comp[e[0]] == comp[e[1]]}
    return pi, red, Z, H


def find_cycle(n, Z):
    """DFS cycle detection on Z (black box of section 6.2): return the cycle closed by the first back edge."""
    adj = out_adj(n, Z)
    state = [0] * n
    parent = [None] * n
    found = []

    def dfs(v):
        state[v] = 1
        for w in adj[v]:
            if found:
                return
            if state[w] == 0:
                parent[w] = v
                dfs(w)
            elif state[w] == 1:
                cyc = [v]
                x = v
                while x != w:
                    x = parent[x]
                    cyc.append(x)
                found.append(cyc[::-1])
                return
        state[v] = 2

    for v in range(n):
        if state[v] == 0 and not found:
            dfs(v)
    return found[0] if found else None


ok4 = dict(a=True, b=True)
cz = 0
for trial in range(3000):
    n = rand_n(1)
    E = rand_noneg(n, random.random(), -2, 3)
    cycles = simple_cycles(n, E)
    zc = [c for c in cycles if clen(E, c) == 0]
    cz += bool(zc)
    pi, red, Z, H = zero_subgraphs(n, E)
    c = find_cycle(n, Z)
    if bool(zc) != (c is not None) or (c is not None and not (is_cycle_of(E, c) and clen(E, c) == 0)):
        ok4["a"] = False
    Hc = simple_cycles(n, H)
    zc_edges = {(c[i], c[(i + 1) % len(c)]) for c in zc for i in range(len(c))}
    if not (all(clen(H, c) == 0 for c in Hc) and zc_edges <= set(H) and (zc or not H)):
        ok4["b"] = False
    # H is in fact exactly the union of the zero cycles' edges
    if set(H) != zc_edges:
        ok4["b"] = False
check("4(a) a zero cycle exists iff the zero-reduced-weight subgraph Z has a cycle; DFS returns one", ok4["a"],
      f"3000 random graphs without negative cycles, {cz} with a zero cycle")
check("4(b) H = edges of Z inside a strong component of Z: all cycles zero, every zero cycle kept, = union of zero "
      "cycles", ok4["b"])

# the page's example (figure a09x-zero): a b c d e f
FIG4 = {(0, 1): 2, (1, 2): -3, (2, 0): 1, (1, 3): -1, (3, 4): 2, (4, 3): -2, (2, 5): 1, (5, 4): 0, (4, 1): 3}
pi4, red4, Z4, H4 = zero_subgraphs(6, FIG4)
ZC4 = [c for c in simple_cycles(6, FIG4) if clen(FIG4, c) == 0]
check("4 figure: prices pi = (-2, 0, -3, -4, -2, -2) for a..f",
      pi4 == [-2, 0, -3, -4, -2, -2], f"{pi4}")
check("4 figure: reduced weights a->b 0, b->c 0, c->a 0, b->d 3, d->e 0, e->d 0, c->f 0, f->e 0, e->b 1",
      [red4[e] for e in [(0, 1), (1, 2), (2, 0), (1, 3), (3, 4), (4, 3), (2, 5), (5, 4), (4, 1)]]
      == [0, 0, 0, 3, 0, 0, 0, 0, 1], f"{red4}")
check("4 figure: no negative cycle; zero cycles are exactly a->b->c->a and d->e->d",
      not has_negcycle(6, FIG4) and sorted(ZC4) == [[0, 1, 2], [3, 4]], f"{ZC4}")
check("4 figure: Z = H + {c->f, f->e}; H = {a->b, b->c, c->a, d->e, e->d}; DFS on Z finds a zero cycle",
      set(H4) == {(0, 1), (1, 2), (2, 0), (3, 4), (4, 3)} and set(Z4) == set(H4) | {(2, 5), (5, 4)}
      and find_cycle(6, Z4) is not None and clen(FIG4, find_cycle(6, Z4)) == 0, f"Z={sorted(Z4)} H={sorted(H4)}")
check("4 figure: other cycles b->d->e->b and b->c->f->e->b have lengths 4 and 1",
      clen(FIG4, [1, 3, 4]) == 4 and clen(FIG4, [1, 2, 5, 4]) == 1
      and sorted(map(tuple, simple_cycles(6, FIG4))) == [(0, 1, 2), (1, 2, 5, 4), (1, 3, 4), (3, 4)])

# ============================================================================ Exercise 5
print("== Exercise 5: distances between k vertex classes")


def delta_alg(n, E, part, k):
    pi, cyc = johnson_prices(n, E)
    assert cyc is None and all(p <= 0 for p in pi)
    res = [[INF] * k for _ in range(k)]
    for i in range(k):
        z = n
        adj_w = [[] for _ in range(n + 1)]
        for (u, v), w in E.items():
            adj_w[u].append((v, pi[u] + w - pi[v]))
        for x in range(n):
            if part[x] == i:
                adj_w[z].append((x, -pi[x]))
        D = dijkstra(n + 1, adj_w, z)
        for v in range(n):
            if D[v] < INF:
                j = part[v]
                res[i][j] = min(res[i][j], D[v] + pi[v])
    return res


def delta_wrong(n, E, part, k):
    """The tempting version: 0-weight edges from the super-source in the reweighted graph."""
    pi, _ = johnson_prices(n, E)
    res = [[INF] * k for _ in range(k)]
    for i in range(k):
        adj_w = [[] for _ in range(n + 1)]
        for (u, v), w in E.items():
            adj_w[u].append((v, pi[u] + w - pi[v]))
        for x in range(n):
            if part[x] == i:
                adj_w[n].append((x, 0))
        D = dijkstra(n + 1, adj_w, n)
        for v in range(n):
            if D[v] < INF:
                res[i][part[v]] = min(res[i][part[v]], D[v] + pi[v])
    return res


ok5, wrong_seen = True, 0
for trial in range(2500):
    n = rand_n(1)
    E = rand_noneg(n, random.random(), -3, 5)
    k = random.randint(1, n)
    part = [random.randrange(k) for _ in range(n)]
    for i in range(k):           # every class non-empty
        part[i] = i
    random.shuffle(part)
    T = brute_apsp(n, E)
    want = [[min(T[a][b] for a in range(n) if part[a] == i for b in range(n) if part[b] == j) for j in range(k)]
            for i in range(k)]
    if delta_alg(n, E, part, k) != want:
        ok5 = False
    if delta_wrong(n, E, part, k) != want:
        wrong_seen += 1
check("5 reweight once, then one Dijkstra per class from a super-source with edges z->x of weight -pi(x)", ok5,
      "2500 random graphs and partitions")
check("5 trap: weight-0 super-source edges in the reweighted graph give wrong answers", wrong_seen > 0,
      f"wrong on {wrong_seen} of 2500")

# ============================================================================ Exercise 6
print("== Exercise 6: arbitrage")


def max_amount(n, X):
    """Bellman-Ford in the (max, x) form: amt[1] = 1, relax amt[v] < amt[u] * X[u][v]; V-1 rounds (exact)."""
    amt = [Fraction(0)] * n
    amt[0] = Fraction(1)
    for _ in range(n - 1):
        for u in range(n):
            for v in range(n):
                if u != v and X[u][v] > 0 and amt[u] * X[u][v] > amt[v]:
                    amt[v] = amt[u] * X[u][v]
    return amt


def max_amount_log(n, X):
    """The same with weights -ln X[u][v] and ordinary Bellman-Ford (floating point)."""
    d = [INF] * n
    d[0] = 0.0
    for _ in range(n - 1):
        for u in range(n):
            for v in range(n):
                if u != v and X[u][v] > 0 and d[u] - math.log(X[u][v]) < d[v]:
                    d[v] = d[u] - math.log(X[u][v])
    return [math.exp(-x) if x < INF else 0.0 for x in d]


def arbitrage_cycle(n, X):
    """Exercise 6(b)/(c): Bellman-Ford from an artificial source on weights -ln X, with cycle extraction; the
    tense test is done exactly on products (amounts) to avoid rounding: an edge is tense iff amt[u]*X > amt[v]."""
    N = n + 1
    amt = [Fraction(0)] * N
    pred = [None] * N
    amt[n] = Fraction(1)
    edges = [(n, v, Fraction(1)) for v in range(n)] + [(u, v, X[u][v]) for u in range(n) for v in range(n)
                                                         if u != v and X[u][v] > 0]
    for _ in range(N - 1):
        for (u, v, x) in edges:
            if amt[u] * x > amt[v]:
                amt[v] = amt[u] * x
                pred[v] = u
    for (u, v, x) in edges:
        if amt[u] * x > amt[v]:
            amt[v] = amt[u] * x
            pred[v] = u
            y = v
            for _ in range(N):
                y = pred[y]
            cyc = [y]
            z = pred[y]
            while z != y:
                cyc.append(z)
                z = pred[z]
            return cyc[::-1]
    return None


def cyc_product(X, c):
    p = Fraction(1)
    for i in range(len(c)):
        p *= X[c[i]][c[(i + 1) % len(c)]]
    return p


ok6 = dict(a=True, alog=True, b=True, c=True)
narb = 0
for trial in range(1500):
    n = random.randint(2, 6)
    mode = random.random()
    if mode < 0.5:   # no arbitrage: prices with fees
        price = [Fraction(random.randint(1, 9), random.randint(1, 9)) for _ in range(n)]
        X = [[(price[j] / price[i]) * Fraction(random.choice([1, 1, 9, 19, 49]), random.choice([1, 1, 10, 20, 50]))
              if i != j else Fraction(1) for j in range(n)] for i in range(n)]
        X = [[min(X[i][j], price[j] / price[i]) for j in range(n)] for i in range(n)]
    else:
        X = [[Fraction(random.randint(1, 12), random.randint(1, 12)) if i != j else Fraction(1) for j in range(n)]
             for i in range(n)]
        for i in range(n):
            for j in range(n):
                if i != j and random.random() < 0.2:
                    X[i][j] = Fraction(0)
    Eall = {(i, j): 1 for i in range(n) for j in range(n) if i != j and X[i][j] > 0}
    cycles = simple_cycles(n, Eall)
    arb = any(cyc_product(X, c) > 1 for c in cycles)
    narb += arb
    c = arbitrage_cycle(n, X)
    if arb != (c is not None):
        ok6["b"] = False
    if c is not None and not (is_cycle_of(Eall, c) and cyc_product(X, c) > 1):
        ok6["c"] = False
    if not arb:
        best = [Fraction(0)] * n
        for p in simple_paths(n, Eall, 0):
            prod = Fraction(1)
            for i in range(len(p) - 1):
                prod *= X[p[i]][p[i + 1]]
            best[p[-1]] = max(best[p[-1]], prod)
        if max_amount(n, X) != best:
            ok6["a"] = False
        ml = max_amount_log(n, X)
        if any(abs(ml[i] - float(best[i])) > 1e-9 * max(1.0, float(best[i])) for i in range(n)):
            ok6["alog"] = False
check("6(a) MaxAmt by Bellman-Ford on products = best product over all simple paths from currency 1", ok6["a"],
      f"1500 random markets, {narb} with arbitrage")
check("6(a) the -ln weights version gives the same amounts (floating point, rel. error 1e-9)", ok6["alog"])
check("6(b) Bellman-Ford from an artificial source detects exactly the markets with a cycle of product > 1", ok6["b"])
check("6(c) the extracted cycle is a simple cycle with product > 1", ok6["c"])
ex = Fraction(120) * Fraction(1, 100) * Fraction(6, 5)
check("6 book example: 1 USD -> 120 JPY -> 1.2 EUR -> 1.44 USD, cycle weight -ln 1.44 < 0",
      ex == Fraction(144, 100) and -math.log(1.44) < 0, f"{ex}")

# ============================================================================ Exercise 7
print("== Exercise 7: Morty")


def morty(n, E, P, F, L):
    """Dijkstra from every vertex of the smaller of P, F, in G and in rev(G); answer min dist(p,f)+dist(f,p)."""
    adj = [[] for _ in range(n)]
    radj = [[] for _ in range(n)]
    for (u, v), w in E.items():
        adj[u].append((v, w))
        radj[v].append((u, w))
    best = (INF, None)
    if len(F) <= len(P):
        for f in F:
            frm = dijkstra(n, adj, f)       # dist(f, .)
            to = dijkstra(n, radj, f)       # dist(., f)
            for p in P:
                if to[p] <= L and to[p] + frm[p] < best[0]:
                    best = (to[p] + frm[p], (p, p, f))
    else:
        for p in P:
            frm = dijkstra(n, adj, p)
            to = dijkstra(n, radj, p)
            for f in F:
                if frm[f] <= L and frm[f] + to[f] < best[0]:
                    best = (frm[f] + to[f], (p, p, f))
    return best


ok7, ok7s = True, True
for trial in range(1500):
    n = rand_n()
    E = rand_graph(n, random.random(), 0, 9)
    vs = list(range(n))
    random.shuffle(vs)
    a = random.randint(1, n - 1)
    b = random.randint(a + 1, n)
    P, F = vs[:a], vs[a:b]
    L = random.randint(0, 15)
    T = brute_apsp(n, E)
    want = min((T[s][p] + T[p][f] + T[f][s] for s in range(n) for p in P for f in F if T[p][f] <= L), default=INF)
    got, arg = morty(n, E, P, F, L)
    if got != want:
        ok7 = False
    if arg is not None:
        s, p, f = arg
        if not (s == p and T[p][f] <= L and T[s][p] + T[p][f] + T[f][s] == want):
            ok7s = False
check("7 min over (s, p, f) of dist(s,p)+dist(p,f)+dist(f,s) = min over (p, f) of dist(p,f)+dist(f,p)", ok7,
      "1500 random graphs with weights 0..9 and random thresholds")
check("7 the start vertex s = p attains the optimum", ok7s)

# ============================================================================ Exercise 8
print("== Exercise 8: deleting a vertex")


def eliminate(n, W, v):
    """W: dict-of-weights (complete matrix with INF). Returns the weight matrix of G' on V - {v} (same indices)."""
    W2 = {}
    others = [x for x in range(n) if x != v]
    for u in others:
        for w in others:
            if u != w:
                W2[(u, w)] = min(W.get((u, w), INF), W.get((u, v), INF) + W.get((v, w), INF))
    return {e: x for e, x in W2.items() if x < INF}


def extend(n, W, v, Dp):
    """Exercise 8(b): from the distances Dp of G' (a dict {(x, y): dist}), distances from and to v in G."""
    others = [x for x in range(n) if x != v]
    frm = {v: 0}
    to = {v: 0}
    for x in others:
        frm[x] = min((W[(v, y)] + Dp[(y, x)] for y in others if (v, y) in W), default=INF)
        to[x] = min((Dp[(x, y)] + W[(y, v)] for y in others if (y, v) in W), default=INF)
    return frm, to


def ElimAPSP(verts, W):
    """Exercise 8(c): delete the last vertex, recurse, put it back. Returns {(x, y): dist}."""
    if len(verts) == 1:
        return {(verts[0], verts[0]): 0}
    v = verts[-1]
    rest = verts[:-1]
    W2 = {}
    for u in rest:
        for w in rest:
            if u != w:
                c = min(W.get((u, w), INF), W.get((u, v), INF) + W.get((v, w), INF))
                if c < INF:
                    W2[(u, w)] = c
    Dp = ElimAPSP(rest, W2)
    D = dict(Dp)
    D[(v, v)] = 0
    for x in rest:
        D[(v, x)] = min((W[(v, y)] + Dp[(y, x)] for y in rest if (v, y) in W), default=INF)
        D[(x, v)] = min((Dp[(x, y)] + W[(y, v)] for y in rest if (y, v) in W), default=INF)
    return D


ok8 = dict(a=True, b=True, c=True)
for trial in range(2500):
    n = rand_n()
    E = rand_noneg(n, random.random(), -3, 5)
    T = brute_apsp(n, E)
    v = random.randrange(n)
    W2 = eliminate(n, E, v)
    others = [x for x in range(n) if x != v]
    ix = {x: i for i, x in enumerate(others)}
    T2 = brute_apsp(n - 1, {(ix[a], ix[b]): w for (a, b), w in W2.items()})
    if any(T2[ix[x]][ix[y]] != T[x][y] for x in others for y in others):
        ok8["a"] = False
    Dp = {(x, y): T2[ix[x]][ix[y]] for x in others for y in others}
    frm, to = extend(n, E, v, Dp)
    if any(frm[x] != T[v][x] or to[x] != T[x][v] for x in range(n)):
        ok8["b"] = False
    D = ElimAPSP(list(range(n)), E)
    if any(D[(x, y)] != T[x][y] for x in range(n) for y in range(n)):
        ok8["c"] = False
check("8(a) G' with w'(u->w) = min(w(u->w), w(u->v)+w(v->w)) keeps all distances among V - {v}", ok8["a"],
      "2500 random graphs without negative cycles, weights -3..5")
check("8(b) dist(v,x) = min over v->y of w(v->y)+dist'(y,x), and symmetrically dist(x,v)", ok8["b"])
check("8(c) eliminate-recurse-extend APSP = brute force", ok8["c"])
# count of the O(V^2) work: T(V) = T(V-1) + c V^2 is Theta(V^3); exact count of inner-loop steps
cnt = {}


def elim_count(V):
    return 0 if V == 1 else (V - 1) * (V - 2) + 2 * (V - 1) * (V - 1) + elim_count(V - 1)


check("8(c) work recurrence T(V) = T(V-1) + O(V^2): T(V)/V^3 -> 1 (exact count (V-1)(V-2) + 2(V-1)^2 per level)",
      abs(elim_count(400) / 400 ** 3 - 1) < 0.01, f"{elim_count(400) / 400 ** 3:.4f}")
# the figure's example
FIG8 = {(0, 2): 2, (1, 2): -1, (2, 3): 3, (2, 4): 1, (0, 3): 4, (4, 1): 2}
W8 = eliminate(5, FIG8, 2)
check("8 figure: deleting v from u1->v (2), u2->v (-1), v->x1 (3), v->x2 (1), u1->x1 (4), x2->u2 (2)",
      W8 == {(0, 3): 4, (0, 4): 3, (1, 3): 2, (1, 4): 0, (4, 1): 2} and not has_negcycle(5, FIG8), f"{W8}")

# ============================================================================ Exercise 9
print("== Exercise 9: boolean matrix products")


def bool_mult(A, B):
    n = len(A)
    return [[any(A[i][k] and B[k][j] for k in range(n)) for j in range(n)] for i in range(n)]


def min_plus(A, B):
    n = len(A)
    return [[min(A[i][k] + B[k][j] for k in range(n)) for j in range(n)] for i in range(n)]


def std_mult(A, B):
    n = len(A)
    return [[sum(A[i][k] * B[k][j] for k in range(n)) for j in range(n)] for i in range(n)]


def bmm_minplus(A, B):
    n = len(A)
    A2 = [[0 if A[i][j] else 1 for j in range(n)] for i in range(n)]
    B2 = [[0 if B[i][j] else 1 for j in range(n)] for i in range(n)]
    C = min_plus(A2, B2)
    return [[C[i][j] == 0 for j in range(n)] for i in range(n)]


def bmm_std(A, B):
    n = len(A)
    C = std_mult([[int(x) for x in r] for r in A], [[int(x) for x in r] for r in B])
    return [[C[i][j] > 0 for j in range(n)] for i in range(n)]


ok9 = dict(a=True, b=True)
for trial in range(1500):
    n = random.randint(1, 7)
    A = [[random.random() < 0.4 for _ in range(n)] for _ in range(n)]
    B = [[random.random() < 0.4 for _ in range(n)] for _ in range(n)]
    C = bool_mult(A, B)
    ok9["a"] &= bmm_minplus(A, B) == C
    ok9["b"] &= bmm_std(A, B) == C
check("9(a) 0 for True, 1 for False, then min-plus product = 0 exactly where the boolean product is True", ok9["a"])
check("9(b) ordinary product of 0/1 matrices > 0 exactly where the boolean product is True", ok9["b"])

# ============================================================================ Exercise 10
print("== Exercise 10: transitive closure by matrix multiplication")
MULTS = [0]


def bmul(A, B):
    MULTS[0] += 1
    return bool_mult(A, B)


def closure_squaring(n, A):
    """10(a): R <- A or I, squared ceil(lg n) times."""
    R = [[A[i][j] or i == j for j in range(n)] for i in range(n)]
    for _ in range(lg_ceil(n)):
        R = bmul(R, R)
    return R


def closure_dag_sorted(A):
    """10(b) on a dag whose vertices 0..n-1 are in topological order: reflexive closure by divide and conquer."""
    n = len(A)
    if n == 1:
        return [[True]]
    h = n // 2
    RX = closure_dag_sorted([row[:h] for row in A[:h]])
    RY = closure_dag_sorted([row[h:] for row in A[h:]])
    AXY = [row[h:] for row in A[:h]]
    # R_XY = R_X * A_XY * R_Y (pad to square for the black-box multiplication)
    m = max(h, n - h)
    pad = lambda M, r, c: [[M[i][j] if i < r and j < c else False for j in range(m)] for i in range(m)]
    T1 = bmul(pad(RX, h, h), pad(AXY, h, n - h))
    RXY = bmul(T1, pad(RY, n - h, n - h))
    R = [[False] * n for _ in range(n)]
    for i in range(h):
        for j in range(h):
            R[i][j] = RX[i][j]
        for j in range(n - h):
            R[i][h + j] = RXY[i][j]
    for i in range(n - h):
        for j in range(n - h):
            R[h + i][h + j] = RY[i][j]
    return R


def topo_order(n, A):
    indeg = [sum(A[u][v] for u in range(n)) for v in range(n)]
    order, bag = [], [v for v in range(n) if indeg[v] == 0]
    while bag:
        v = bag.pop()
        order.append(v)
        for w in range(n):
            if A[v][w]:
                indeg[w] -= 1
                if indeg[w] == 0:
                    bag.append(w)
    return order


def closure_dag(n, A):
    order = topo_order(n, A)
    pos = {v: i for i, v in enumerate(order)}
    As = [[A[order[i]][order[j]] for j in range(n)] for i in range(n)]
    Rs = closure_dag_sorted(As)
    return [[Rs[pos[u]][pos[v]] for v in range(n)] for u in range(n)]


def closure_general(n, A):
    """10(c): strong components, closure of the component dag by (b), then copy back."""
    E = {(u, v): 1 for u in range(n) for v in range(n) if A[u][v] and u != v}
    comp = sccs(n, E)
    k = max(comp) + 1
    Ac = [[False] * k for _ in range(k)]
    for (u, v) in E:
        if comp[u] != comp[v]:
            Ac[comp[u]][comp[v]] = True
    Rc = closure_dag(k, Ac)
    return [[Rc[comp[u]][comp[v]] for v in range(n)] for u in range(n)]


def bmm_via_closure(A, B):
    """10(d): three layers I, K, J; edges i->k if A[i][k], k->j if B[k][j]."""
    n = len(A)
    N = 3 * n
    G = [[False] * N for _ in range(N)]
    for i in range(n):
        for k in range(n):
            if A[i][k]:
                G[i][n + k] = True
            if B[i][k]:
                G[n + i][2 * n + k] = True
    R = closure_squaring(N, G)          # any closure algorithm
    return [[R[i][2 * n + j] for j in range(n)] for i in range(n)]


ok10 = dict(a=True, aplus=True, b=True, c=True, d=True)
for trial in range(800):
    n = random.randint(1, 9)
    A = [[i != j and random.random() < random.random() * 0.5 for j in range(n)] for i in range(n)]
    E = {(u, v): 1 for u in range(n) for v in range(n) if A[u][v]}
    R = reach(n, E)
    ok10["a"] &= closure_squaring(n, A) == R
    Rstar = closure_squaring(n, A)
    Rplus = bool_mult(A, Rstar)        # strict closure: paths with at least one edge
    want_plus = [[any(A[u][x] and R[x][v] for x in range(n)) for v in range(n)] for u in range(n)]
    ok10["aplus"] &= Rplus == want_plus
    ok10["c"] &= closure_general(n, A) == R
    # random dag: edges only forward in a random permutation
    perm = list(range(n))
    random.shuffle(perm)
    D = [[perm[i] < perm[j] and random.random() < 0.4 for j in range(n)] for i in range(n)]
    ED = {(u, v): 1 for u in range(n) for v in range(n) if D[u][v]}
    ok10["b"] &= closure_dag(n, D) == reach(n, ED)
    B = [[random.random() < 0.4 for _ in range(n)] for _ in range(n)]
    C0 = [[random.random() < 0.4 for _ in range(n)] for _ in range(n)]
    ok10["d"] &= bmm_via_closure(C0, B) == bool_mult(C0, B)
check("10(a) (A or I) squared ceil(lg n) times = reflexive transitive closure", ok10["a"], "800 random graphs")
check("10(a) one more product A * R* gives the strict closure (paths with >= 1 edge)", ok10["aplus"])
check("10(b) divide and conquer on a topologically sorted dag: R_XY = R_X A_XY R_Y", ok10["b"])
check("10(c) strong components + (b) on the component dag", ok10["c"])
check("10(d) boolean product read off the closure of the 3n-vertex layered graph", ok10["d"])
# products used by (b): M(n) = M(floor) + M(ceil) + 2, M(1) = 0, i.e. 2(n - 1)
okm = True
for n in range(1, 40):
    MULTS[0] = 0
    closure_dag_sorted([[i < j and random.random() < 0.3 for j in range(n)] for i in range(n)])
    okm &= MULTS[0] == 2 * (n - 1)
check("10(b) the recursion makes exactly 2(n-1) products of size <= n/2 (two per internal node)", okm)
for omega in (2.0, 2.3728639, 2.807355):
    def Tw(n):
        return 1 if n == 1 else Tw(n // 2) + Tw(n - n // 2) + 2 * math.ceil(n / 2) ** omega
    r = [Tw(2 ** k) / (2 ** k) ** omega for k in (10, 14, 18)]
    check(f"10(b) T(n) = 2T(n/2) + 2(n/2)^w is Theta(n^w) for w = {omega}: T/n^w settles",
          abs(r[2] - r[1]) < 0.01 and r[2] < 2.01, f"{[round(x, 4) for x in r]}")

# ============================================================================ Exercise 11 (skipped on the page)
print("== Exercise 11 (not solved on the page): RecursiveAPSP as printed")


BOOK_ORDER = lambda h: [(0, 0, 0), (0, 0, h), (0, h, 0), (0, h, h), (h, 0, 0), (h, 0, h), (h, h, 0), (h, h, h)]
GOOD_ORDER = lambda h: [(0, 0, 0), (0, h, 0), (h, 0, 0), (h, h, 0), (h, h, h), (h, 0, h), (0, h, h), (0, 0, h)]


def rec_apsp(n, E, printed_init, printed_typo, order):
    D = [[None] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if printed_init:   # as printed: "if i = j: 0 ; if i->j in E: w ; else: inf"
                if i == j:
                    D[i][j] = 0
                if (i, j) in E:
                    D[i][j] = E[(i, j)]
                else:
                    D[i][j] = INF
            else:
                D[i][j] = 0 if i == j else E.get((i, j), INF)

    def rec(m, i, j, k):
        if m == 1:
            if printed_typo:
                D[i][j] = min(D[i][j], D[i][k] + D[j][k])      # as printed: D[j, k]
            else:
                D[i][j] = min(D[i][j], D[i][k] + D[k][j])
            return
        h = m // 2
        for (a, b, c) in order(h):
            rec(h, i + a, j + b, k + c)

    rec(n, 0, 0, 0)
    return D


cnt11 = dict(tot=0, printed=0, init=0, typo=0, order=0, good=0)
for trial in range(1500):
    n = random.choice([1, 2, 4, 8])
    E = rand_noneg(n, random.random(), -2, 5)
    T = FloydWarshall(n, E)[0]
    cnt11["tot"] += 1
    cnt11["printed"] += rec_apsp(n, E, True, True, BOOK_ORDER) != T
    cnt11["init"] += rec_apsp(n, E, True, False, GOOD_ORDER) != T
    cnt11["typo"] += rec_apsp(n, E, False, True, GOOD_ORDER) != T
    cnt11["order"] += rec_apsp(n, E, False, False, BOOK_ORDER) != T
    cnt11["good"] += rec_apsp(n, E, False, False, GOOD_ORDER) == T
check("11 as printed the code is wrong on most inputs", cnt11["printed"] > cnt11["tot"] // 2, f"{cnt11}")
check("11 each of the three defects alone breaks it: diagonal overwritten by inf; D[j,k] for D[k,j]; call order",
      cnt11["init"] > 0 and cnt11["typo"] > 0 and cnt11["order"] > 0)
check("11 fixed init, D[k,j], and calls (k-half 1: blocks 11,12,21,22; k-half 2: 22,21,12,11) = Floyd-Warshall",
      cnt11["good"] == cnt11["tot"])
CE11 = {(1, 3): 1, (3, 2): 1, (2, 0): 1}       # 2 -> 4 -> 3 -> 1 in the book's 1-based names
check("11 printed call order (typos fixed) misses dist(2,1) = 3 on the path 2->4->3->1 of unit edges",
      rec_apsp(4, CE11, False, False, BOOK_ORDER)[1][0] == INF and FloydWarshall(4, CE11)[0][1][0] == 3
      and rec_apsp(4, CE11, False, False, GOOD_ORDER) == FloydWarshall(4, CE11)[0])

# ============================================================================ the page states what is checked above
print("== page text")
import os
import re
PAGE = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "content", "2-algorithms",
                         "09-all-pairs-shortest-paths-exercises.md"), encoding="utf-8").read()
FIGX = {k: open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figs", f"a09x-{k}.html"),
                encoding="utf-8").read() for k in ("pointer-cycle", "zero", "eliminate")}
PAGE_STRINGS = [
    # 9.1(a) counterexample trace (checked above as "1(a) counterexample trace")
    "$\\mathit{dist}[d, a] = 3$ through $c$ (so $\\mathit{pred}[d, a] = \\mathit{pred}[c, a] = b$)",
    "$\\mathit{dist}[d, a] + \\mathit{dist}[a, b] = 3 - 1 = 2$ through $a$ (so $\\mathit{pred}[d, b] = "
    "\\mathit{pred}[a, b] = a$)",
    # 9.2(a): a vertex of a bad component lies on a negative closed walk (several turns may be needed)
    "around it often enough, and back inside $C$",
    # 9.4 example (checked above as "4 figure: ...")
    "$b\\to d\\to e\\to b$ and $b\\to c\\to f\\to e\\to b$, have lengths 4 and 1",
    # 9.5 super-source weights and answer
    "an edge $z_i\\to x$ of weight $-\\pi(x)\\ge 0$", "\\delta(i, j) = \\min_{v\\in V_j}\\big(\\textsf{dist}_{G_i}(z_i, v) + \\pi(v)\\big)",
    # 9.6 book example
    "$w = -\\ln 120 - \\ln 0.01 - \\ln 1.2 = -\\ln 1.44 < 0$",
    # 9.11 note (checked above as "11 ...")
    "with unit weights on $2\\to4\\to3\\to1$ it leaves $D[2, 1] = \\infty$",
]
miss = [s for s in PAGE_STRINGS if s not in PAGE]
check("page states the checked numbers (9.1(a) trace, 9.2(a), 9.4 example, 9.5 construction, 9.6 example, 9.11 note)",
      not miss, " | ".join(miss))
check("figure a09x-zero: the price labels are the computed prices pi(a..f) = -2, 0, -3, -4, -2, -2",
      re.findall(r">π=([−\d]+)<", FIGX["zero"]) == [str(p).replace("-", "−") for p in pi4])
check("figure a09x-pointer-cycle: the grey distance labels from d are 0, 1, 2, 3 for d, c, b, a",
      all(f">{x}</text>" in FIGX["pointer-cycle"] for x in "0123"))
check("figure a09x-eliminate caption: u1->x1 keeps 4 < 2 + 3; three new edges",
      "keeps its weight 4 &lt; 2 + 3" in FIGX["eliminate"] and "Three new edges" in FIGX["eliminate"]
      and len(set(W8) - set(FIG8)) == 3 and W8[(0, 3)] == 4 < FIG8[(0, 2)] + FIG8[(2, 3)] == 5)

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: {FAIL}")
