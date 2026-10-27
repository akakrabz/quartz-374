#!/usr/bin/env python3
"""Checks for every concrete claim on content/2-algorithms/09-all-pairs-shortest-paths.md and the concept pages
all-pairs-shortest-paths, johnsons-algorithm and floyd-warshall.

Every algorithm on the page is transcribed as the page states it: V runs of breadth-first search, of the dag
dynamic program, of Dijkstra (binary heap) and of Bellman-Ford; reweighting by prices; JohnsonAPSP (Figure 9.2);
ShimbelAPSP (with the page's fix, and as printed in the book), AllPairsBellmanFord; FischerMeyerAPSP and
LeyzorekAPSP; the min-plus product, iterated and by repeated squaring; KleeneAPSP and FloydWarshall (with
predecessors, negative-cycle detection, the wrong loop order, Warshall's transitive closure and the
shortest-cycle variant). They are compared with each other and with brute force (enumeration of all simple paths,
of all walks with at most l edges, of all simple cycles) on thousands of random digraphs with negative edges,
with and without negative cycles. Then every matrix, number and label of the running example, the figures and
the concept-page examples is recomputed and compared with the text."""
import heapq
import itertools
import math
import os
import random
import re
import sys
from collections import deque

sys.setrecursionlimit(10000)
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
PAGE = os.path.join(ROOT, "content", "2-algorithms", "09-all-pairs-shortest-paths.md")
CONCEPTS = os.path.join(ROOT, "content", "concepts")
FIGS = os.path.join(HERE, "..", "figs")
FAIL = []
random.seed(374)
INF = math.inf


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAIL.append(name)


def read(path):
    return open(path, encoding="utf-8").read()


# =====================================================================================================
# Graphs: vertices 0..n-1 (printed 1..n); E = dict (u, v) -> weight, no parallel edges; loops only when asked.
def adj_out(n, E):
    A = {u: [] for u in range(n)}
    for (u, v), w in E.items():
        A[u].append((v, w))
    return A


def adj_in(n, E):
    A = {v: [] for v in range(n)}
    for (u, v), w in E.items():
        A[v].append((u, w))
    return A


def wmatrix(n, E, diag=0):
    """w(u->v), with w(v->v) = diag (0 by the book's convention) and infinity for non-edges."""
    W = [[INF] * n for _ in range(n)]
    for (u, v), w in E.items():
        W[u][v] = w
    for v in range(n):
        if (v, v) not in E:
            W[v][v] = diag
        else:
            W[v][v] = min(diag, E[(v, v)])
    return W


def rand_graph(n, p, lo=-4, hi=9, loops=False, rng=random):
    E = {}
    for u in range(n):
        for v in range(n):
            if (u != v or loops) and rng.random() < p:
                E[(u, v)] = rng.randint(lo, hi)
    return E


# --------------------------------------------------------------------------------------------- brute force
def simple_paths(n, E, u, v):
    """All simple paths from u to v (u != v) as (length, vertex list); for u == v only the empty path."""
    A = adj_out(n, E)
    if u == v:
        return [(0, [u])]
    out = []

    def go(x, seen, L, path):
        if x == v:
            out.append((L, path))
            return
        for y, w in A[x]:
            if y not in seen:
                go(y, seen | {y}, L + w, path + [y])

    go(u, {u}, 0, [u])
    return out


def simple_cycles(n, E):
    """All simple directed cycles, each once (smallest vertex first), as (length, vertex list)."""
    A = adj_out(n, E)
    out = []
    for s in range(n):
        def go(x, seen, L, path):
            for y, w in A[x]:
                if y == s:
                    out.append((L + w, path[:]))
                elif y > s and y not in seen:
                    go(y, seen | {y}, L + w, path + [y])
        go(s, {s}, 0, [s])
    return out


def brute_has_neg_cycle(n, E):
    return any(L < 0 for L, _ in simple_cycles(n, E))


def brute_apsp(n, E):
    """True distances (no negative cycles): min over simple paths; 0 on the diagonal."""
    return [[min((L for L, _ in simple_paths(n, E, u, v)), default=INF) for v in range(n)] for u in range(n)]


def brute_walk(n, E, l, exact=False):
    """Shortest walk from u to v with at most (exactly) l edges, by enumerating every walk."""
    A = adj_out(n, E)
    D = [[INF] * n for _ in range(n)]
    for u in range(n):
        frontier = {(u,): 0}
        if not exact or l == 0:
            D[u][u] = min(D[u][u], 0)
        for k in range(1, l + 1):
            nxt = {}
            for walk, L in frontier.items():
                for y, w in A[walk[-1]]:
                    nxt[walk + (y,)] = L + w
            frontier = nxt
            for walk, L in frontier.items():
                if not exact or k == l:
                    D[u][walk[-1]] = min(D[u][walk[-1]], L)
    return D


def reach_matrix(n, E):
    R = [[False] * n for _ in range(n)]
    A = adj_out(n, E)
    for s in range(n):
        seen, st = {s}, [s]
        while st:
            x = st.pop()
            for y, _ in A[x]:
                if y not in seen:
                    seen.add(y)
                    st.append(y)
        for v in seen:
            R[s][v] = True
    return R


# --------------------------------------------------------------------------------------------- SSSP (Chapter 8)
def bfs_sssp(n, E, s):
    A = adj_out(n, E)
    dist = [INF] * n
    dist[s] = 0
    Q = deque([s])
    while Q:
        u = Q.popleft()
        for v, _ in A[u]:
            if dist[v] > dist[u] + 1:
                dist[v] = dist[u] + 1
                Q.append(v)
    return dist


def topo_order(n, E):
    A = adj_out(n, E)
    seen, post = set(), []

    def dfs(v):
        seen.add(v)
        for w, _ in A[v]:
            if w not in seen:
                dfs(w)
        post.append(v)

    for v in range(n):
        if v not in seen:
            dfs(v)
    return post[::-1]


def dag_sssp(n, E, s):
    A = adj_out(n, E)
    dist = [INF] * n
    dist[s] = 0
    for u in topo_order(n, E):
        for v, w in A[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
    return dist


COUNT = {"relax": 0}


def dijkstra(n, E, s):
    """The book's Dijkstra (lazy deletion stands in for DecreaseKey); with nonnegative weights each vertex is
    scanned once."""
    A = adj_out(n, E)
    dist = [INF] * n
    pred = [None] * n
    dist[s] = 0
    pq = [(0, s)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for v, w in A[u]:
            if dist[u] + w < dist[v]:        # u->v is tense
                dist[v] = dist[u] + w
                pred[v] = u
                COUNT["relax"] += 1
                heapq.heappush(pq, (dist[v], v))
    return dist, pred


def bellman_ford(n, E, s):
    """V-1 rounds of relaxing every edge, then one more round: a tense edge means a negative cycle."""
    dist = [INF] * n
    pred = [None] * n
    dist[s] = 0
    for _ in range(n - 1):
        for (u, v), w in E.items():
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                pred[v] = u
    neg = any(dist[u] + w < dist[v] for (u, v), w in E.items())
    return dist, pred, neg


def obvious_apsp(n, E, sssp):
    return [list(sssp(n, E, s)) for s in range(n)]


# --------------------------------------------------------------------------------------------- reweighting
def reweight(E, pi):
    return {(u, v): pi[u] + w - pi[v] for (u, v), w in E.items()}


def johnson_apsp(n, E, trace=None):
    """Figure 9.2. Returns None if Bellman-Ford finds a negative cycle."""
    s = n
    E2 = dict(E)
    for v in range(n):                      # add a new vertex s and edges s->v of weight 0
        E2[(s, v)] = 0
    ds, _, neg = bellman_ford(n + 1, E2, s)
    if neg:
        return None
    pi = ds[:n]
    Ep = {}
    for (u, v), w in E.items():
        Ep[(u, v)] = ds[u] + w - ds[v]
    distp = [dijkstra(n, Ep, u)[0] for u in range(n)]
    dist = [[INF] * n for _ in range(n)]
    loops = 0
    for u in range(n):
        for v in range(n):
            dist[u][v] = distp[u][v] - ds[u] + ds[v]
            loops += 1
    if trace is not None:
        trace.update(pi=pi, Ep=Ep, distp=distp, final_loop=loops)
    return dist


# --------------------------------------------------------------------------------------------- dynamic programming
class Undefined(Exception):
    pass


def shimbel_apsp(n, E, as_printed=False):
    """ShimbelAPSP. dist[u][v][l] for l = 0..V-1. as_printed: the book's loop over v != u, which never assigns
    dist[u, u, l] for l >= 1; reading such an entry raises Undefined."""
    Ain = adj_in(n, E)
    U = None
    dist = [[[U] * n for _ in range(n)] for _ in range(n)]
    for u in range(n):
        for v in range(n):
            dist[u][v][0] = 0 if u == v else INF

    def get(u, v, l):
        x = dist[u][v][l]
        if x is None:
            raise Undefined((u, v, l))
        return x

    work = 0
    for l in range(1, n):
        for u in range(n):
            for v in range(n):
                if as_printed and v == u:
                    continue
                dist[u][v][l] = get(u, v, l - 1)
                work += 1
                for x, w in Ain[v]:
                    work += 1
                    if dist[u][v][l] > get(u, x, l - 1) + w:
                        dist[u][v][l] = get(u, x, l - 1) + w
    return dist, work


def all_pairs_bellman_ford(n, E, trace=None):
    dist = [[0 if u == v else INF for v in range(n)] for u in range(n)]
    for l in range(1, n):
        for u in range(n):
            for (x, v), w in E.items():
                if dist[u][v] > dist[u][x] + w:
                    dist[u][v] = dist[u][x] + w
        if trace is not None:
            trace.append([r[:] for r in dist])
    return dist


def clg(n):
    return 0 if n <= 1 else (n - 1).bit_length()     # ceil(lg n)


def fischer_meyer_apsp(n, E):
    W = wmatrix(n, E)
    L = clg(n)
    dist = [[[None] * (L + 1) for _ in range(n)] for _ in range(n)]
    for u in range(n):
        for v in range(n):
            dist[u][v][0] = W[u][v]
    work = 0
    for i in range(1, L + 1):
        for u in range(n):
            for v in range(n):
                dist[u][v][i] = INF
                for x in range(n):
                    work += 1
                    if dist[u][v][i] > dist[u][x][i - 1] + dist[x][v][i - 1]:
                        dist[u][v][i] = dist[u][x][i - 1] + dist[x][v][i - 1]
    return dist, work


def leyzorek_apsp(n, E, trace=None):
    W = wmatrix(n, E)
    dist = [r[:] for r in W]
    for i in range(1, clg(n) + 1):
        for u in range(n):
            for v in range(n):
                for x in range(n):
                    if dist[u][v] > dist[u][x] + dist[x][v]:
                        dist[u][v] = dist[u][x] + dist[x][v]
        if trace is not None:
            trace.append([r[:] for r in dist])
    return dist


def minplus(A, B):
    n = len(A)
    C = [[INF] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            for k in range(n):
                C[i][j] = min(C[i][j], A[i][k] + B[k][j])
    return C


def identity(n):
    return [[0 if i == j else INF for j in range(n)] for i in range(n)]


def kleene_apsp(n, E, order=None):
    """KleeneAPSP: dist[r] is the matrix dist(., ., r) for r = 0..V (vertex order[r-1] is 'vertex r')."""
    order = list(range(n)) if order is None else order
    D = [wmatrix(n, E)]
    for k in range(1, n + 1):
        r = order[k - 1]
        P, N = D[-1], [[None] * n for _ in range(n)]
        for u in range(n):
            for v in range(n):
                if P[u][v] < P[u][r] + P[r][v]:
                    N[u][v] = P[u][v]
                else:
                    N[u][v] = P[u][r] + P[r][v]
        D.append(N)
    return D


def floyd_warshall(n, E, order=None, trace=None, diag=0, pred=False):
    dist = wmatrix(n, E, diag)
    P = [[(u if (u, v) in E and u != v else None) for v in range(n)] for u in range(n)]
    order = list(range(n)) if order is None else order
    work = 0
    for r in order:
        for u in range(n):
            for v in range(n):
                work += 1
                if dist[u][v] > dist[u][r] + dist[r][v]:
                    dist[u][v] = dist[u][r] + dist[r][v]
                    P[u][v] = P[r][v]
        if trace is not None:
            trace.append([row[:] for row in dist])
    if pred:
        return dist, P
    return dist


def fw_count(n, E):
    dist = wmatrix(n, E)
    c = 0
    for r in range(n):
        for u in range(n):
            for v in range(n):
                c += 1
                if dist[u][v] > dist[u][r] + dist[r][v]:
                    dist[u][v] = dist[u][r] + dist[r][v]
    return c


def fw_wrong_order(n, E):
    """One pass with the loops nested u, v, r (r innermost), in place."""
    dist = wmatrix(n, E)
    for u in range(n):
        for v in range(n):
            for r in range(n):
                if dist[u][v] > dist[u][r] + dist[r][v]:
                    dist[u][v] = dist[u][r] + dist[r][v]
    return dist


def warshall(n, E):
    R = [[(u == v) or ((u, v) in E) for v in range(n)] for u in range(n)]
    for r in range(n):
        for u in range(n):
            for v in range(n):
                R[u][v] = R[u][v] or (R[u][r] and R[r][v])
    return R


def path_from_pred(P, u, v):
    """Follow pred[u, .] back from v to u."""
    path = [v]
    while path[-1] != u:
        p = P[u][path[-1]]
        if p is None or len(path) > len(P) + 1:
            return None
        path.append(p)
    return path[::-1]


def path_len(E, path):
    return sum(E[(path[i], path[i + 1])] for i in range(len(path) - 1))


def matrices_equal(A, B):
    return all(A[i][j] == B[i][j] for i in range(len(A)) for j in range(len(A)))


def mat_le(A, B):
    return all(A[i][j] <= B[i][j] for i in range(len(A)) for j in range(len(A)))


def show(M):
    return "[" + "; ".join(" ".join("∞" if x == INF else ("−∞" if x == -INF else str(x)) for x in row) for row in M) + "]"


# =====================================================================================================
# 1. random tests: every algorithm against brute force
def random_graphs(count, nmax=6, neg_ok=False, rng=random):
    """Random digraphs on 1..nmax vertices (mostly 3..nmax); two thirds of them must have a negative edge."""
    out = []
    while len(out) < count:
        n = rng.randint(1, nmax) if rng.random() < 0.15 else rng.randint(3, nmax)
        p = rng.choice([0.2, 0.35, 0.5, 0.7])
        lo = rng.choice([-2, -4, -6])
        E = rand_graph(n, p, lo=lo, hi=9, rng=rng)
        if len(out) % 3 and not any(w < 0 for w in E.values()):
            continue
        neg = brute_has_neg_cycle(n, E)
        if neg and not neg_ok:
            continue
        out.append((n, E, neg))
    return out


GOOD = random_graphs(2500)                     # no negative cycles, negative edges allowed
MIXED = random_graphs(1500, neg_ok=True)       # some with negative cycles
NEGS = [g for g in MIXED if g[2]]
NNEG = sum(1 for n, E, _ in GOOD if any(w < 0 for w in E.values()))
check("random families: 2500 graphs without negative cycles (%d with negative edges); %d of 1500 mixed graphs "
      "have a negative cycle" % (NNEG, len(NEGS)), len(NEGS) > 200 and NNEG > 1500)

ok = {k: True for k in ["bfs", "dag", "dijkstra", "bf", "johnson", "johnson_neg", "shimbel", "shimbel_l",
                        "apbf", "apbf_l", "fm", "fm_i", "ley", "minplus_pow", "minplus_sq",
                        "minplus_exact", "kleene", "kleene_r", "fw", "fw_inplace", "fw_order", "fw_pred",
                        "reduced_nonneg", "reduced_paths", "reduced_cycles", "tight_tree", "pi_formula",
                        "fw_detect", "fw_neg_on_cycle", "fw_neg_walk", "fw_inplace_le", "warshall",
                        "fw_cycle", "assoc", "ident", "shimbel_printed", "counts", "ley_le_fm", "sq_detect"]}
bad = {}


def fail(key, info):
    if ok[key]:
        bad[key] = info
    ok[key] = False


for n, E, _ in GOOD:
    T = brute_apsp(n, E)
    # V runs of single-source algorithms
    if not matrices_equal(obvious_apsp(n, E, lambda n_, E_, s: bellman_ford(n_, E_, s)[0]), T):
        fail("bf", (n, E))
    if all(w >= 0 for w in E.values()) and not matrices_equal(
            obvious_apsp(n, E, lambda n_, E_, s: dijkstra(n_, E_, s)[0]), T):
        fail("dijkstra", (n, E))
    # Johnson
    tr = {}
    J = johnson_apsp(n, E, tr)
    if J is None or not matrices_equal(J, T):
        fail("johnson", (n, E))
    else:
        pi, Ep = tr["pi"], tr["Ep"]
        if any(w < 0 for w in Ep.values()):
            fail("reduced_nonneg", (n, E))
        if tr["final_loop"] != n * n:
            fail("counts", ("johnson final loop", n))
        # pi(v) = min(0, min_u dist(u, v))
        if any(pi[v] != min(0, min(T[u][v] for u in range(n))) for v in range(n)):
            fail("pi_formula", (n, E))
        # edges on shortest paths from s (u->v with pi(v) = pi(u) + w) have reduced weight 0, and conversely
        for (u, v), w in E.items():
            if (pi[u] + w == pi[v]) != (Ep[(u, v)] == 0):
                fail("tight_tree", (n, E))
    # arbitrary prices: every path changes by pi(u) - pi(v), cycles keep their length
    pi = [random.randint(-7, 7) for _ in range(n)]
    Ep = reweight(E, pi)
    for u in range(n):
        for v in range(n):
            for L, path in simple_paths(n, E, u, v):
                if path_len(Ep, path) != L + pi[u] - pi[v]:
                    fail("reduced_paths", (n, E, pi))
    for L, cyc in simple_cycles(n, E):
        if path_len(Ep, cyc + [cyc[0]]) != L:
            fail("reduced_cycles", (n, E, pi))
    Tp = brute_apsp(n, Ep) if not brute_has_neg_cycle(n, Ep) else None
    if Tp is None or any(Tp[u][v] != (T[u][v] + pi[u] - pi[v] if T[u][v] < INF else INF)
                         for u in range(n) for v in range(n)):
        fail("reduced_paths", ("dist'", n, E, pi))
    # Shimbel: dist[u][v][l] = shortest walk with at most l edges
    S, work = shimbel_apsp(n, E)
    for l in range(n):
        Bl = brute_walk(n, E, l) if n <= 5 or l <= 3 else None
        if Bl is not None and any(S[u][v][l] != Bl[u][v] for u in range(n) for v in range(n)):
            fail("shimbel_l", (n, E, l))
    if n >= 1 and any(S[u][v][n - 1] != T[u][v] for u in range(n) for v in range(n)):
        fail("shimbel", (n, E))
    if work != (n - 1) * n * (n + len(E)):
        fail("counts", ("shimbel", n, len(E), work))
    try:
        shimbel_apsp(n, E, as_printed=True)
        printed_ok = True
    except Undefined:
        printed_ok = False
    # as printed it reads an unassigned diagonal entry as soon as V >= 3 and some edge leaves... check below
    if n >= 3 and any(u != v for (u, v) in E) and printed_ok:
        # it can only succeed if no dist[u, u, l-1] with l-1 >= 1 is ever read: no edge u->v read at l >= 2
        fail("shimbel_printed", (n, E))
    # AllPairsBellmanFord
    trace = []
    A = all_pairs_bellman_ford(n, E, trace)
    if not matrices_equal(A, T):
        fail("apbf", (n, E))
    for l, M in enumerate(trace, start=1):
        Bl = [[S[u][v][l] for v in range(n)] for u in range(n)]
        if not (mat_le(M, Bl) and mat_le(T, M)):
            fail("apbf_l", (n, E, l))
    # Fischer-Meyer and Leyzorek
    F, work = fischer_meyer_apsp(n, E)
    L = clg(n)
    if not (2 ** L >= n - 1 and 2 ** L < 2 * n or n == 1):
        fail("fm", ("ell bound", n))
    if any(F[u][v][L] != T[u][v] for u in range(n) for v in range(n)):
        fail("fm", (n, E))
    for i in range(L + 1):
        Bi = brute_walk(n, E, min(2 ** i, n)) if (n <= 5) else None
        if Bi is not None and any(F[u][v][i] != Bi[u][v] for u in range(n) for v in range(n)):
            fail("fm_i", (n, E, i))
    if work != L * n ** 3:
        fail("counts", ("fm", n, work))
    trace = []
    Ly = leyzorek_apsp(n, E, trace)
    if not matrices_equal(Ly, T):
        fail("ley", (n, E))
    for i, M in enumerate(trace, start=1):
        Fi = [[F[u][v][i] for v in range(n)] for u in range(n)]
        if not (mat_le(M, Fi) and mat_le(T, M)):
            fail("ley_le_fm", (n, E, i))
    # min-plus powers
    W = wmatrix(n, E)
    P = identity(n)
    for l in range(1, n):
        P = minplus(P, W)
        if not all(P[u][v] == S[u][v][l] for u in range(n) for v in range(n)):
            fail("minplus_pow", (n, E, l))
    Q = W
    for _ in range(L):
        Q = minplus(Q, Q)
    if not matrices_equal(Q, T):
        fail("minplus_sq", (n, E))
    if n <= 5:
        W0 = wmatrix(n, E, diag=INF)
        P0 = W0
        for l in range(1, 4):
            if not matrices_equal(P0, brute_walk(n, E, l, exact=True)):
                fail("minplus_exact", (n, E, l))
            P0 = minplus(P0, W0)
    if not matrices_equal(minplus(identity(n), W), W) or not matrices_equal(minplus(W, identity(n)), W):
        fail("ident", (n, E))
    # Kleene and Floyd-Warshall
    K = kleene_apsp(n, E)
    if not matrices_equal(K[n], T):
        fail("kleene", (n, E))
    # dist(u, v, r) = shortest path with intermediate vertices < r (0-based) by brute force
    for r in range(n + 1):
        for u in range(n):
            for v in range(n):
                best = min((Lp for Lp, path in simple_paths(n, E, u, v) if all(x < r for x in path[1:-1])),
                           default=INF)
                if K[r][u][v] != best:
                    fail("kleene_r", (n, E, r, u, v))
    trace = []
    FW = floyd_warshall(n, E, trace=trace)
    if not matrices_equal(FW, T):
        fail("fw", (n, E))
    for r, M in enumerate(trace, start=1):
        if not matrices_equal(M, K[r]):
            fail("fw_inplace", (n, E, r))
    order = list(range(n))
    random.shuffle(order)
    if not matrices_equal(floyd_warshall(n, E, order=order), T):
        fail("fw_order", (n, E, order))
    D, Pm = floyd_warshall(n, E, pred=True)
    for u in range(n):
        for v in range(n):
            if u == v:
                if Pm[u][v] is not None:
                    fail("fw_pred", (n, E, "diag"))
            elif T[u][v] == INF:
                if Pm[u][v] is not None:
                    fail("fw_pred", (n, E, "unreachable"))
            else:
                path = path_from_pred(Pm, u, v)
                if path is None or path_len(E, path) != T[u][v]:
                    fail("fw_pred", (n, E, u, v))
    if fw_count(n, E) != n ** 3:
        fail("counts", ("fw", n))
    # shortest cycle through v: diagonal initialized to infinity
    C = floyd_warshall(n, E, diag=INF)
    for v in range(n):
        best = min((L for L, cyc in simple_cycles(n, E) if v in cyc), default=INF)
        if C[v][v] != best:
            fail("fw_cycle", (n, E, v))
    # Warshall's transitive closure
    R = reach_matrix(n, E)
    if warshall(n, E) != R:
        fail("warshall", (n, E))
    # unweighted graphs: V breadth-first searches give the edge counts
    E1 = {e: 1 for e in E}
    if not matrices_equal(obvious_apsp(n, E, bfs_sssp), brute_apsp(n, E1)):
        fail("bfs", (n, E))

# dags with negative edges: V runs of the dag dynamic program
for trial in range(600):
    n = random.randint(1, 7)
    perm = list(range(n))
    random.shuffle(perm)
    E = {}
    for i in range(n):
        for j in range(i + 1, n):
            if random.random() < 0.45:
                E[(perm[i], perm[j])] = random.randint(-6, 9)
    if not matrices_equal(obvious_apsp(n, E, dag_sssp), brute_apsp(n, E)):
        fail("dag", (n, E))

# graphs with negative cycles
for n, E, neg in MIXED:
    if johnson_apsp(n, E) is None and not neg:
        fail("johnson_neg", (n, E))
    if neg and johnson_apsp(n, E) is not None:
        fail("johnson_neg", (n, E))
    FW = floyd_warshall(n, E)
    if any(FW[v][v] < 0 for v in range(n)) != neg:
        fail("fw_detect", (n, E))
    cyc = simple_cycles(n, E)
    for L, c in cyc:
        if L < 0 and any(FW[v][v] >= 0 for v in c):
            fail("fw_neg_on_cycle", (n, E, c))
    # a negative diagonal entry means v lies on a negative closed walk: v is strongly connected to a negative cycle
    R = reach_matrix(n, E)
    for v in range(n):
        if FW[v][v] < 0:
            if not any(L < 0 and R[v][c[0]] and R[c[0]][v] for L, c in cyc):
                fail("fw_neg_walk", (n, E, v))
    K = kleene_apsp(n, E)
    if not mat_le(FW, K[n]):
        fail("fw_inplace_le", (n, E))
    # repeated squaring (Fischer-Meyer, Leyzorek): negative diagonal iff negative cycle, on every cycle vertex
    Fm, _ = fischer_meyer_apsp(n, E)
    Lz = leyzorek_apsp(n, E)
    L_ = clg(n)
    for Dg in ([Fm[v][v][L_] for v in range(n)], [Lz[v][v] for v in range(n)]):
        if any(x < 0 for x in Dg) != neg or any(Lc < 0 and any(Dg[v] >= 0 for v in c) for Lc, c in cyc):
            fail("sq_detect", (n, E))

# graphs with loops: a negative loop is a negative cycle; FloydWarshall with dist[v, v] = min{0, w(v->v)}
okloops = True
for trial in range(800):
    n = random.randint(1, 5)
    E = rand_graph(n, random.choice([0.25, 0.45]), lo=-3, hi=8, loops=True)
    neg = brute_has_neg_cycle(n, E)
    FW = floyd_warshall(n, E)
    if any(FW[v][v] < 0 for v in range(n)) != neg:
        okloops = False
    if not neg and not matrices_equal(FW, brute_apsp(n, E)):
        okloops = False
check("graphs with loops (800): FloydWarshall with dist[v, v] = min{0, w(v->v)} detects exactly the negative cycles "
      "(negative loops included) and is otherwise correct", okloops)

# V runs of Bellman-Ford detect every negative cycle; Johnson's augmented graph has V+1 vertices and E+V edges
okbfneg = all(any(bellman_ford(n, E, s_)[2] for s_ in range(n)) == neg for n, E, neg in MIXED)
check("V runs of Bellman-Ford report a negative cycle iff there is one (1500 mixed graphs)", okbfneg)
okaug = True
for n, E, _ in GOOD[:300]:
    E2 = dict(E)
    for v in range(n):
        E2[(n, v)] = 0
    if len(E2) != len(E) + n or len({x for e in E2 for x in e} | set(range(n + 1))) != n + 1:
        okaug = False
    ds_, _, _ = bellman_ford(n + 1, E2, n)
    T_ = brute_apsp(n + 1, E2)
    if any(T_[u][v] != brute_apsp(n, E)[u][v] for u in range(n) for v in range(n)) or any(x > 0 for x in ds_[:n]):
        okaug = False
check("Johnson's new vertex: V+1 vertices, E+V edges, no distance between old vertices changes, every price <= 0",
      okaug)

# associativity of the min-plus product on random matrices with infinite entries
for trial in range(300):
    m = random.randint(1, 5)
    M = [[[random.choice([INF, random.randint(-5, 9)]) for _ in range(m)] for _ in range(m)] for _ in range(3)]
    if not matrices_equal(minplus(minplus(M[0], M[1]), M[2]), minplus(M[0], minplus(M[1], M[2]))):
        fail("assoc", M)

LABELS = {
    "bfs": "V breadth-first searches = brute-force edge-count distances (unweighted)",
    "dag": "V runs of the dag dynamic program = brute force (600 random dags, negative edges)",
    "dijkstra": "V runs of Dijkstra = brute force (graphs with nonnegative weights)",
    "bf": "V runs of Bellman-Ford = brute force",
    "johnson": "JohnsonAPSP (Figure 9.2) = brute force",
    "johnson_neg": "JohnsonAPSP fails gracefully exactly when there is a negative cycle",
    "reduced_nonneg": "Johnson's reduced weights are all nonnegative",
    "pi_formula": "Johnson's prices: pi(v) = dist(s, v) = min{0, min_u dist(u, v)}",
    "tight_tree": "reduced weight 0 exactly for the edges with pi(u) + w(u->v) = pi(v) (shortest paths from s)",
    "reduced_paths": "random prices: every simple path u~>v changes by pi(u) - pi(v); dist' = dist + pi(u) - pi(v)",
    "reduced_cycles": "random prices: every cycle keeps its length",
    "shimbel": "ShimbelAPSP: dist[u, v, V-1] = brute force",
    "shimbel_l": "ShimbelAPSP: dist[u, v, l] = shortest walk with at most l edges (enumerated walks)",
    "shimbel_printed": "ShimbelAPSP as printed (v != u) reads an unassigned dist[u, u, l] whenever V >= 3 and E is nonempty",
    "apbf": "AllPairsBellmanFord = brute force",
    "apbf_l": "AllPairsBellmanFord after iteration l: true dist <= dist[u, v] <= dist(u, v, l)",
    "fm": "FischerMeyerAPSP: dist[u, v, ceil(lg V)] = brute force, and V-1 <= 2^ceil(lg V) < 2V",
    "fm_i": "FischerMeyerAPSP: dist[u, v, i] = shortest walk with at most 2^i edges",
    "ley": "LeyzorekAPSP = brute force",
    "ley_le_fm": "LeyzorekAPSP after iteration i: true dist <= dist[u, v] <= dist(u, v, 2^i)",
    "minplus_pow": "min-plus powers: I (x) W^l = dist(., ., l) (W with 0 diagonal)",
    "minplus_sq": "repeated squaring: W^(2^ceil(lg V)) = distance matrix",
    "minplus_exact": "with infinity on the diagonal, the l-th min-plus power = shortest walk with exactly l edges",
    "ident": "the min-plus identity (0 diagonal, infinity elsewhere) is an identity",
    "assoc": "the min-plus product is associative (300 random triples with infinite entries)",
    "kleene": "KleeneAPSP: dist[u, v, V] = brute force",
    "kleene_r": "KleeneAPSP: dist[u, v, r] = shortest path with intermediate vertices <= r (brute force)",
    "fw": "FloydWarshall = brute force",
    "fw_inplace": "FloydWarshall in place: the matrix after phase r equals KleeneAPSP's dist(., ., r) exactly",
    "fw_order": "FloydWarshall with the vertices r taken in a random order = brute force",
    "fw_pred": "FloydWarshall with pred[u, v] <- pred[r, v]: following pred gives a shortest path; Null on the diagonal and for unreachable pairs",
    "counts": "work counts: FloydWarshall V^3, Leyzorek/FischerMeyer ceil(lg V) V^3, Shimbel (V-1) V (V+E), Johnson's last loop V^2",
    "fw_cycle": "FloydWarshall with infinity on the diagonal: dist[v, v] = shortest cycle through v",
    "warshall": "Warshall (or/and) = transitive closure by search",
    "fw_detect": "FloydWarshall: some dist[v, v] < 0 iff the graph has a negative cycle (1500 mixed graphs)",
    "fw_neg_on_cycle": "FloydWarshall: every vertex of a negative cycle ends with dist[v, v] < 0",
    "fw_neg_walk": "FloydWarshall: dist[v, v] < 0 only if v is strongly connected to a negative cycle",
    "fw_inplace_le": "FloydWarshall in place <= KleeneAPSP entrywise, also with negative cycles",
    "sq_detect": "FischerMeyerAPSP and LeyzorekAPSP: some dist[v, v] < 0 iff the graph has a negative cycle, and every "
                 "vertex of a negative cycle gets dist[v, v] < 0 (concept page: the repeated-squaring diagonal)",
}
for k in ok:
    check(LABELS[k], ok[k], str(bad.get(k, ""))[:300])

# =====================================================================================================
# 2. the running example
EX_N = 4
EX = {(0, 1): -2, (1, 2): 4, (2, 1): 1, (2, 3): 3, (3, 2): 2, (3, 0): -3}     # 1->2 -2, 2->3 4, 3->2 1, ...
# (page checks follow)
page = read(PAGE)
CAPSP = read(os.path.join(CONCEPTS, "all-pairs-shortest-paths.md"))
CJOH = read(os.path.join(CONCEPTS, "johnsons-algorithm.md"))
CFW = read(os.path.join(CONCEPTS, "floyd-warshall.md"))
FIG = {k: read(os.path.join(FIGS, f"a09-{k}.html")) for k in
       ("example", "reweighting", "fw-phases", "fw-structure", "minplus")}


def missing(text, *subs):
    return [x for x in subs if x not in text]


def on(name, cond, text, *subs):
    miss = missing(text, *subs)
    check(name, cond and not miss, ("missing on page: " + " | ".join(miss)) if miss else "")


def M1(M):
    """0-based matrix -> dict keyed by 1-based pairs."""
    n = len(M)
    return {(u + 1, v + 1): M[u][v] for u in range(n) for v in range(n)}


def fnum(x):
    return "∞" if x == INF else ("–" if x is None else str(x).replace("-", "−"))


T = brute_apsp(EX_N, EX)
ROWS = [[0, -2, 2, 5], [4, 0, 4, 7], [0, -2, 0, 3], [-3, -5, -1, 0]]
check("running example: distance matrix rows (0 −2 2 5), (4 0 4 7), (0 −2 0 3), (−3 −5 −1 0) (brute force)",
      T == ROWS)
cyc = sorted((L, tuple(x + 1 for x in c)) for L, c in simple_cycles(EX_N, EX))
check("running example: simple cycles 1-2-3-4-1 (2), 2-3-2 (5), 3-4-3 (5); no negative cycle",
      cyc == [(2, (1, 2, 3, 4)), (5, (2, 3)), (5, (3, 4))])
# unique shortest paths, so pred is well defined; pred from brute force
uniq, PB = True, {}
for u in range(EX_N):
    for v in range(EX_N):
        if u != v:
            ps = simple_paths(EX_N, EX, u, v)
            L = min(p[0] for p in ps)
            best = [p for p in ps if p[0] == L]
            uniq &= len(best) == 1
            PB[(u + 1, v + 1)] = best[0][1][-2] + 1
        else:
            PB[(u + 1, v + 1)] = None
D, Pm = floyd_warshall(EX_N, EX, pred=True)
PRED = {(u + 1, v + 1): (None if Pm[u][v] is None else Pm[u][v] + 1) for u in range(EX_N) for v in range(EX_N)}
check("running example: every shortest path is unique; pred matrix rows (– 1 2 3), (4 – 2 3), (4 1 – 3), (4 1 2 –) "
      "= FloydWarshall's predecessors", uniq and PB == PRED and
      [[PRED[(u, v)] for v in range(1, 5)] for u in range(1, 5)] ==
      [[None, 1, 2, 3], [4, None, 2, 3], [4, 1, None, 3], [4, 1, 2, None]])
sp32 = min(simple_paths(EX_N, EX, 2, 1))
sp43 = min(simple_paths(EX_N, EX, 3, 2))
check("running example: 3->4->1->2 has length −2 against the edge 3->2 (1); 4->1->2->3 has length −1 against 4->3 (2)",
      sp32 == (-2, [2, 3, 0, 1]) and EX[(2, 1)] == 1 and sp43 == (-1, [3, 0, 1, 2]) and EX[(3, 2)] == 2)

# ---------------------------------------------------------------------------------------- figure helpers
TXT = re.compile(r'<text x="([-\d.]+)" y="([-\d.]+)"[^>]*style="([^"]*)"[^>]*>(.*?)</text>')
CIRC = re.compile(r'<circle cx="([-\d.]+)" cy="([-\d.]+)" r="([\d.]+)"')
ARROW = re.compile(r'<path d="([^"]+)" fill="none" stroke="([^"]+)" stroke-width="([\d.]+)"[^>]*marker-end')


def texts(html):
    return [(float(x), float(y), st, re.sub(r"<[^>]+>", "", c)) for x, y, st, c in TXT.findall(html)]


def text_at(html, x, y, tol=0.6):
    hits = [c for X, Y, _, c in texts(html) if abs(X - x) < tol and abs(Y - y) < tol]
    return hits[0] if len(hits) == 1 else ("??" if not hits else "??" + "|".join(hits))


def read_matrix(html, x0, y0, cw=34, ch=26):
    return {(i + 1, j + 1): text_at(html, x0 + j * cw + cw / 2, y0 + i * ch + ch / 2 + 1)
            for i in range(4) for j in range(4)}


def hi_cells(html, x0, y0, cw=34, ch=26):
    out = set()
    for x, y in re.findall(r'<rect x="([-\d.]+)" y="([-\d.]+)" width="[\d.]+" height="[\d.]+" rx="4" '
                           r'fill="var\(--accent\)" fill-opacity="0.18" stroke="var\(--accent\)"', html):
        j = (float(x) - 2 - x0) / cw
        i = (float(y) - 2 - y0) / ch
        if abs(j - round(j)) < 1e-6 and abs(i - round(i)) < 1e-6 and 0 <= round(i) < 4 and 0 <= round(j) < 4:
            out.add((round(i) + 1, round(j) + 1))
    return out


def shaded_cells(html, x0, y0, cw=34, ch=26):
    out = set()
    for x, y in re.findall(r'<rect x="([-\d.]+)" y="([-\d.]+)" width="[\d.]+" height="[\d.]+" rx="0" '
                           r'fill="var\(--muted\)" fill-opacity="0.22"', html):
        j = (float(x) - x0) / cw
        i = (float(y) - y0) / ch
        if abs(j - round(j)) < 1e-6 and abs(i - round(i)) < 1e-6 and 0 <= round(i) < 4 and 0 <= round(j) < 4:
            out.add((round(i) + 1, round(j) + 1))
    return out


def fig_edges(html, region=None):
    """(tail label, head label, weight label, stroke color) for every arrow whose endpoints lie on vertex circles;
    the weight label is the nearest haloed text to the curve's midpoint."""
    circles = []
    for cx, cy, r in CIRC.findall(html):
        cx, cy, r = float(cx), float(cy), float(r)
        lab = text_at(html, cx, cy + 1)
        if not lab.startswith("??"):
            circles.append((cx, cy, r, lab))
    halos = [(x, y, c) for x, y, st, c in texts(html) if "paint-order" in st]
    out = []
    for d, color, width in ARROW.findall(html):
        nums = [float(t) for t in re.findall(r"-?[\d.]+", d)]
        sx, sy, ex, ey = nums[0], nums[1], nums[-2], nums[-1]
        if "Q" in d:
            cx, cy = nums[2], nums[3]
            mx, my = 0.25 * sx + 0.5 * cx + 0.25 * ex, 0.25 * sy + 0.5 * cy + 0.25 * ey
        else:
            mx, my = (sx + ex) / 2, (sy + ey) / 2

        def near(x, y):
            best = min(circles, key=lambda c: math.hypot(c[0] - x, c[1] - y))
            return best[3] if abs(math.hypot(best[0] - x, best[1] - y) - best[2]) < 4.5 else None

        a, b = near(sx, sy), near(ex, ey)
        if a is None or b is None:
            continue
        if region and not region(sx, sy):
            continue
        lab = min(halos, key=lambda h: math.hypot(h[0] - mx, h[1] - my))
        out.append((a, b, lab[2], color, float(width)))
    return out


def weight_text(w):
    return str(w).replace("-", "−")


# ---------------------------------------------------------------------------------------- figure 1
f1 = FIG["example"]
E1 = sorted((a, b, w) for a, b, w, _, _ in fig_edges(f1))
want1 = sorted((str(u + 1), str(v + 1), weight_text(w)) for (u, v), w in EX.items())
check("figure a09-example: the six drawn edges and their weight labels are the running example's", E1 == want1,
      str(E1))
dm, pm = read_matrix(f1, 322, 92), read_matrix(f1, 494, 92)
check("figure a09-example: the dist and pred matrices drawn are the brute-force distances and predecessors",
      dm == {k: fnum(x) for k, x in M1(T).items()} and pm == {k: fnum(x) for k, x in PRED.items()}, str((dm, pm)))
on("figure a09-example caption: cycle lengths 5, 5, 2 and the two paths that beat a direct edge",
   True, f1, "lengths 5 (2→3→2), 5 (3→4→3) and 2 (1→2→3→4→1)", "3→4→1→2 has length −2 against 1 for the edge 3→2",
   "4→1→2→3 has length −1 against 2 for 4→3")

# ---------------------------------------------------------------------------------------- Johnson
tr = {}
J = johnson_apsp(EX_N, EX, tr)
pi, Ep, distp = tr["pi"], tr["Ep"], tr["distp"]
check("running example, Johnson: prices pi(1..4) = −3, −5, −1, 0; JohnsonAPSP = brute force",
      pi == [-3, -5, -1, 0] and J == T)
EP1 = {(u + 1, v + 1): w for (u, v), w in Ep.items()}
check("running example, Johnson: reduced weights 1->2 0, 2->3 0, 4->1 0, 3->4 2, 4->3 3, 3->2 5",
      EP1 == {(1, 2): 0, (2, 3): 0, (4, 1): 0, (3, 4): 2, (4, 3): 3, (3, 2): 5})
# shortest-path tree from s: s->4->1->2->3 (Bellman-Ford with s = vertex 4 in 0-based numbering)
Es = dict(EX)
for v in range(EX_N):
    Es[(EX_N, v)] = 0
ds, ps_, _ = bellman_ford(EX_N + 1, Es, EX_N)
check("running example, Johnson: the shortest-path tree from s is s->4->1->2->3, and pi(2) = −5 along s->4->1->2",
      [p + 1 if p is not None and p < EX_N else ("s" if p == EX_N else None) for p in ps_[:EX_N]] == [4, 1, 2, "s"]
      and ds[1] == Es[(EX_N, 3)] + EX[(3, 0)] + EX[(0, 1)] == -5)
check("running example, Johnson: dist'(3, .) = (2, 2, 0, 2); dist(3, 2) = 2 + 1 − 5 = −2; dist(3, 1) = 2 + 1 − 3 = 0",
      distp[2] == [2, 2, 0, 2] and distp[2][1] - pi[2] + pi[1] == 2 + 1 - 5 == -2
      and distp[2][0] - pi[2] + pi[0] == 2 + 1 - 3 == 0 == T[2][0])
check("running example, Johnson: the reduced-weight-0 edges are exactly the tree edges 4->1, 1->2, 2->3",
      {e for e, w in EP1.items() if w == 0} == {(4, 1), (1, 2), (2, 3)})
check("running example, Johnson: cycles keep their length: 2-3-2 = 0 + 5, 3-4-3 = 2 + 3, 1-2-3-4-1 = 0 + 0 + 2 + 0",
      EP1[(2, 3)] + EP1[(3, 2)] == 0 + 5 == 5 and EP1[(3, 4)] + EP1[(4, 3)] == 2 + 3 == 5
      and EP1[(1, 2)] + EP1[(2, 3)] + EP1[(3, 4)] + EP1[(4, 1)] == 0 + 0 + 2 + 0 == 2)
on("page: Johnson example numbers", True, page,
   "$\\pi(1), \\pi(2), \\pi(3), \\pi(4) = -3, -5, -1, 0$", "$\\pi(2) = -5$ along $s\\to4\\to1\\to2$",
   "$w'(1\\to2) = -3 - 2 + 5 = 0$", "$w'(2\\to3) = 0$", "$w'(4\\to1) = 0$", "$w'(3\\to4) = 2$", "$w'(4\\to3) = 3$",
   "$w'(3\\to2) = -1 + 1 + 5 = 5$", "$\\textsf{dist}'(3, \\cdot) = (2, 2, 0, 2)$",
   "\\textsf{dist}(3, 2) = \\textsf{dist}'(3, 2) - \\pi(3) + \\pi(2) = 2 + 1 - 5 = -2",
   "\\textsf{dist}(3, 1) = 2 + 1 - 3 = 0")
check("Johnson price arithmetic as printed: −3 − 2 + 5 = 0 and −1 + 1 + 5 = 5 are pi(u) + w − pi(v)",
      pi[0] + EX[(0, 1)] - pi[1] == -3 - 2 + 5 == 0 and pi[2] + EX[(2, 1)] - pi[1] == -1 + 1 + 5 == 5)
# figure 2
f2 = FIG["reweighting"]
# left panel: vertices at x <= 240; right panel: x >= 410
EL = sorted((a, b, w, c) for a, b, w, c, _ in fig_edges(f2, region=lambda x, y: x < 330))
ER = sorted((a, b, w, c) for a, b, w, c, _ in fig_edges(f2, region=lambda x, y: x > 330))
wantL = sorted([(str(u + 1), str(v + 1), weight_text(w),
                 "var(--accent)" if (u + 1, v + 1) in {(4, 1), (1, 2), (2, 3)} else "currentColor")
                for (u, v), w in EX.items()] +
               [("s", str(v), "0", "var(--accent)" if v == 4 else "var(--muted)") for v in range(1, 5)])
wantR = sorted((str(u), str(v), weight_text(w), "var(--accent)" if w == 0 else "currentColor")
               for (u, v), w in EP1.items())
check("figure a09-reweighting: left panel = G + s with weights w, tree s->4->1->2->3 colored", EL == wantL, str(EL))
check("figure a09-reweighting: right panel = reduced weights, the weight-0 edges colored", ER == wantR, str(ER))
plabels = sorted(c for x, y, st, c in texts(f2) if c.startswith("π = "))
check("figure a09-reweighting: price labels π = −3, −5, −1, 0 next to vertices 1, 2, 3, 4",
      plabels == sorted("π = " + weight_text(p) for p in pi)
      and all(text_at(f2, 70 + cx * 170 + dx, 74 + cy * 170 + dy) == "π = " + weight_text(pi[v - 1])
              for v, (cx, cy), (dx, dy) in [(1, (0, 0), (-30, -27)), (2, (1, 0), (30, -27)), (3, (1, 1), (30, 27)),
                                            (4, (0, 1), (-30, 27))]))
on("figure a09-reweighting caption: prices, tree and cycle sums", True, f2, "π(1), π(2), π(3), π(4) = −3, −5, −1, 0",
   "<i>s</i>→4→1→2→3", "2→3→2 is 0 + 5, 3→4→3 is 2 + 3, and 1→2→3→4→1 is 0 + 0 + 2 + 0")

# ---------------------------------------------------------------------------------------- adding a constant
# the book's Figure 9.1: s->a->t with 4, 4; s->b->c->t with 2, 3, 2
F91 = {(0, 1): 4, (1, 4): 4, (0, 2): 2, (2, 3): 3, (3, 4): 2}
best0 = min(simple_paths(5, F91, 0, 4))
F91b = {e: w + 2 for e, w in F91.items()}
best2 = min(simple_paths(5, F91b, 0, 4))
check("Figure 9.1: path lengths 8 and 7; after adding 2 they are 12 and 13 and the shortest path changes",
      best0 == (7, [0, 2, 3, 4]) and best2 == (12, [0, 1, 4])
      and path_len(F91b, [0, 2, 3, 4]) == 13 and path_len(F91, [0, 1, 4]) == 8)
EXc = {e: w + 3 for e, w in EX.items()}
check("running example + 3: the most negative weight is −3; 3->4->1->2 becomes 6 + 0 + 1 = 7 > 4 = edge 3->2, "
      "so the shortest path from 3 to 2 changes",
      min(EX.values()) == -3 and path_len(EXc, [2, 3, 0, 1]) == 6 + 0 + 1 == 7 and EXc[(2, 1)] == 1 + 3 == 4
      and min(simple_paths(EX_N, EXc, 2, 1))[1] == [2, 1])
on("page: the adding-a-constant trap", True, page, "two edges of weight 4 (total 8)",
   "three edges of weights 2, 3, 2 (total 7)", "Adding 2 to every edge makes them 12 and 13",
   "the most negative weight is $-3$", "$6 + 0 + 1 = 7$", "$1 + 3 = 4$")

# ---------------------------------------------------------------------------------------- dynamic programs
S3, _ = shimbel_apsp(EX_N, EX)
W = wmatrix(EX_N, EX)
W2 = minplus(W, W)
W3 = minplus(W2, W)
W4 = minplus(W2, W2)
check("running example: W^2 != W^3 = W^4 = distances; Shimbel's level 2 = W^2, level 3 = distances",
      W2 != W3 and W3 == W4 == T and [[S3[u][v][2] for v in range(4)] for u in range(4)] == W2
      and [[S3[u][v][3] for v in range(4)] for u in range(4)] == T)
f5 = FIG["minplus"]
mW, mW2, mW4 = (read_matrix(f5, x, 62) for x in (40, 236, 432))
h2, h4 = hi_cells(f5, 236, 62), hi_cells(f5, 432, 62)
ch2 = {k for k, x in M1(W2).items() if x != M1(W)[k]}
ch4 = {k for k, x in M1(W4).items() if x != M1(W2)[k]}
check("figure a09-minplus: matrices W, W^2, W^4 and the highlighted improvements",
      mW == {k: fnum(x) for k, x in M1(W).items()} and mW2 == {k: fnum(x) for k, x in M1(W2).items()}
      and mW4 == {k: fnum(x) for k, x in M1(W4).items()} and h2 == ch2 and h4 == ch4
      and not hi_cells(f5, 40, 62), str((h2, h4)))
on("figure a09-minplus caption", True, f5, "<i>V</i> − 1 = 3 edges", "W³ = W⁴ = dist")
check("V - 1 <= 2^ceil(lg V) < 2V for V = 2 .. 100000",
      all(V_ - 1 <= 2 ** clg(V_) < 2 * V_ for V_ in range(2, 100001)))
okt = True
for n_ in range(1, 9):
    E_ = rand_graph(n_, 0.5, lo=0, hi=5)
    F_, _ = fischer_meyer_apsp(n_, E_)
    if len(F_) * len(F_[0]) * len(F_[0][0]) != n_ * n_ * (clg(n_) + 1):
        okt = False
check("FischerMeyerAPSP's table has V^2 (ceil(lg V) + 1) entries, O(V^2 log V)", okt)
check("Strassen: lg 7 = 2.807355 to six decimals", round(math.log2(7), 6) == 2.807355
      and "O(n^{2.807355})" in page)
# Shimbel as printed on the running example
try:
    shimbel_apsp(EX_N, EX, as_printed=True)
    printed = "ran"
except Undefined as e:
    printed = e.args[0]
check("ShimbelAPSP as printed on the running example reads dist[u, u, 1] (never assigned) at l = 2",
      isinstance(printed, tuple) and printed[0] == printed[1] and printed[2] == 1)

# ---------------------------------------------------------------------------------------- Floyd-Warshall
K = kleene_apsp(EX_N, EX)
trace = []
floyd_warshall(EX_N, EX, trace=trace)
check("running example: FloydWarshall's matrix after phase r = KleeneAPSP's dist(., ., r), r = 1..4",
      all(trace[r - 1] == K[r] for r in range(1, 5)))
f3 = FIG["fw-phases"]
slots = [(46, 64), (232, 64), (418, 64), (46, 226), (232, 226)]
okf, detail = True, []
for r, (x, y) in enumerate(slots):
    got = read_matrix(f3, x, y)
    want = {k: fnum(v) for k, v in M1(K[r]).items()}
    changed = {k for k, v in M1(K[r]).items() if r > 0 and v != M1(K[r - 1])[k]}
    shade = shaded_cells(f3, x, y)
    want_shade = {(i, j) for i in range(1, 5) for j in range(1, 5) if r > 0 and (i == r or j == r)}
    if got != want or hi_cells(f3, x, y) != changed or shade != want_shade:
        okf = False
        detail.append(r)
check("figure a09-fw-phases: the five matrices, the improved entries and the shaded row/column r", okf, str(detail))
# caption: what each phase finds
PHASES = {1: [((4, 2), [4, 1, 2], -5)],
          2: [((1, 3), [1, 2, 3], 2), ((4, 3), [4, 1, 2, 3], -1)],
          3: [((1, 4), [1, 2, 3, 4], 5), ((2, 4), [2, 3, 4], 7)],
          4: [((2, 1), [2, 3, 4, 1], 4), ((3, 1), [3, 4, 1], 0), ((3, 2), [3, 4, 1, 2], -2)]}
okc = True
for r, items in PHASES.items():
    changed = {k for k, v in M1(K[r]).items() if v != M1(K[r - 1])[k]}
    if changed != {k for k, _, _ in items}:
        okc = False
    for (u, v), path, L in items:
        p0 = [x - 1 for x in path]
        if path_from_pred(Pm, u - 1, v - 1) != p0 or path_len(EX, p0) != L or T[u - 1][v - 1] != L \
                or max(path[1:-1]) != r:
            okc = False
check("figure a09-fw-phases caption: phase r finds exactly the listed shortest paths, each through r", okc)
on("figure a09-fw-phases caption text", True, f3, "Phase 1 finds 4→1→2 (−5)", "phase 2 finds 1→2→3 (2) and 4→1→2→3 (−1)",
   "phase 3 finds 1→2→3→4 (5) and 2→3→4 (7)", "phase 4 finds 2→3→4→1 (4), 3→4→1 (0) and 3→4→1→2 (−2)")
# phase r leaves row r and column r unchanged (no negative cycles), on many random graphs
okrc = True
for n, E, _ in GOOD[:800]:
    Kr = kleene_apsp(n, E)
    for r in range(1, n + 1):
        if any(Kr[r][r - 1][v] != Kr[r - 1][r - 1][v] or Kr[r][v][r - 1] != Kr[r - 1][v][r - 1] for v in range(n)):
            okrc = False
check("phase r never changes row r or column r (800 random graphs without negative cycles)", okrc)
# wrong loop order on the running example
dist = wmatrix(EX_N, EX)
seen_at_21 = None
for u in range(EX_N):
    for v in range(EX_N):
        if (u, v) == (1, 0):
            seen_at_21 = (dist[1][3], dist[2][0])
        for r in range(EX_N):
            if dist[u][v] > dist[u][r] + dist[r][v]:
                dist[u][v] = dist[u][r] + dist[r][v]
check("wrong loop order (u, v, r), one pass: dist[2, 1] stays ∞ although 2->3->4->1 has length 4; when (2, 1) is "
      "computed, dist[2, 4] and dist[3, 1] are still ∞",
      dist == fw_wrong_order(EX_N, EX) and dist[1][0] == INF and T[1][0] == 4
      and path_len(EX, [1, 2, 3, 0]) == 4 and seen_at_21 == (INF, INF))
on("page: the wrong-loop-order trap", True, page, "leaves $\\mathit{dist}[2, 1] = \\infty$",
   "$2\\to3\\to4\\to1$ has length 4", "neither $\\mathit{dist}[2, 4]$ nor $\\mathit{dist}[3, 1]$ is known yet")
Cy = floyd_warshall(EX_N, EX, diag=INF)
check("running example with infinity on the diagonal: all four diagonal entries 2 (the cycle 1->2->3->4->1)",
      [Cy[v][v] for v in range(4)] == [2, 2, 2, 2])
on("page: shortest-cycle tip", True, page, "all four diagonal entries become 2, the cycle $1\\to2\\to3\\to4\\to1$")
f4 = FIG["fw-structure"]
check("figure a09-fw-structure: three pieces labeled ≤ r − 1 and the 0 at (r, r)",
      sum(1 for *_, c in texts(f4) if c == "≤ r − 1") == 3 and text_at(f4, 400 + 2 * 30 + 15, 40 + 2 * 30 + 16) == "0")

# ---------------------------------------------------------------------------------------- concept pages
# all-pairs-shortest-paths: a, b, c = 0, 1, 2
EA = {(0, 1): 2, (1, 2): -1, (0, 2): 4, (2, 1): 3}
TA = brute_apsp(3, EA)
_, PA = floyd_warshall(3, EA, pred=True)
WA = wmatrix(3, EA)
check("concept all-pairs-shortest-paths example: rows (0, 2, 1), (∞, 0, −1), (∞, 3, 0); pred(a, c) = b; the only "
      "cycle has length 2; W^2 = distances while W has 4 at (a, c)",
      TA == [[0, 2, 1], [INF, 0, -1], [INF, 3, 0]] and PA[0][2] == 1
      and [L for L, _ in simple_cycles(3, EA)] == [2] and minplus(WA, WA) == TA and WA[0][2] == 4 and 3 - 1 == 2)
on("concept all-pairs-shortest-paths example text", True, CAPSP,
   "$a\\to b$ (2), $b\\to c$ ($-1$), $a\\to c$ (4), $c\\to b$ (3)", "$b\\to c\\to b$, has length 2",
   "$(0, 2, 1)$, $(\\infty, 0, -1)$ and $(\\infty, 3, 0)$", "$\\textsf{pred}(a, c) = b$", "Since $V - 1 = 2$",
   "still has 4 in entry $(a, c)$")
on("concept all-pairs-shortest-paths trap: the diagonal of Floyd-Warshall and of repeated squaring detects negative "
   "cycles (checked as sq_detect, fw_detect)", ok["sq_detect"] and ok["fw_detect"], CAPSP,
   "except the diagonal of Floyd–Warshall or of the repeated-squaring algorithms: some entry is negative iff there "
   "is a negative cycle")
# johnsons-algorithm
EJ = {(0, 1): -2, (1, 2): 1, (0, 2): 3, (2, 0): 2}
trj = {}
TJ = johnson_apsp(3, EJ, trj)
EPJ = trj["Ep"]
check("concept johnsons-algorithm example: prices 0, −2, −1; reduced weights 0, 0, 4, 1; cycles 1 = 0 + 0 + 1 and "
      "5 = 4 + 1; "
      "dist'(a, c) = 0, dist(a, c) = −1; dist'(c, b) = 1, dist(c, b) = 0",
      trj["pi"] == [0, -2, -1] and EPJ == {(0, 1): 0, (1, 2): 0, (0, 2): 4, (2, 0): 1}
      and sorted(L for L, _ in simple_cycles(3, EJ)) == [1, 5] and EPJ[(0, 1)] + EPJ[(1, 2)] + EPJ[(2, 0)] == 1
      and EPJ[(0, 2)] + EPJ[(2, 0)] == 4 + 1 == 5
      and trj["distp"][0][2] == 0 and TJ[0][2] == 0 - 0 + (-1) == -1 == path_len(EJ, [0, 1, 2])
      and trj["distp"][2][1] == 1 and TJ[2][1] == 1 + 1 - 2 == 0 == path_len(EJ, [2, 0, 1])
      and TJ == brute_apsp(3, EJ))
on("concept johnsons-algorithm example text", True, CJOH,
   "$a\\to b$ ($-2$), $b\\to c$ (1), $a\\to c$ (3), $c\\to a$ (2)", "$a\\to b\\to c\\to a$ and $a\\to c\\to a$ have lengths 1 and 5",
   "$\\pi(a), \\pi(b), \\pi(c) = 0, -2, -1$", "$w'(a\\to b) = 0 - 2 + 2 = 0$", "$w'(b\\to c) = -2 + 1 + 1 = 0$",
   "$w'(a\\to c) = 0 + 3 + 1 = 4$", "$w'(c\\to a) = -1 + 2 - 0 = 1$", "$0 + 0 + 1 = 1$ and $4 + 1 = 5$",
   "$\\textsf{dist}'(a, c) = 0$", "$\\textsf{dist}(a, c) = 0 - 0 + (-1) = -1$", "$\\textsf{dist}'(c, b) = 1$",
   "$\\textsf{dist}(c, b) = 1 + 1 - 2 = 0$")
# floyd-warshall
EF = {(0, 1): 3, (1, 2): -1, (2, 0): 2, (0, 2): 4}
KF = kleene_apsp(3, EF)
trF = []
floyd_warshall(3, EF, trace=trF)
EFn = dict(EF)
EFn[(2, 0)] = -3
FN = floyd_warshall(3, EFn)
CF = floyd_warshall(3, EF, diag=INF)
check("concept floyd-warshall example: start (0,3,4),(∞,0,−1),(2,∞,0); phase 1 finds 3->1->2 (5); phase 2 sets "
      "(1,3) = 2; phase 3 finds 2->3->1 (1); final (0,3,2),(1,0,−1),(2,5,0)",
      KF[0] == [[0, 3, 4], [INF, 0, -1], [2, INF, 0]] and trF[0][2][1] == 5 and trF[0] == KF[1]
      and [k for k in M1(KF[1]) if M1(KF[1])[k] != M1(KF[0])[k]] == [(3, 2)]
      and [k for k in M1(KF[2]) if M1(KF[2])[k] != M1(KF[1])[k]] == [(1, 3)] and KF[2][0][2] == 3 - 1 == 2
      and [k for k in M1(KF[3]) if M1(KF[3])[k] != M1(KF[2])[k]] == [(2, 1)] and KF[3][1][0] == 1
      and KF[3] == trF[2] == [[0, 3, 2], [1, 0, -1], [2, 5, 0]] == brute_apsp(3, EF))
check("concept floyd-warshall example: cycles 1-2-3-1 (4) and 1-3-1 (6); with w(3->1) = −3 the first has length −1; diagonal −1, −1, −2; (3, 1) = −4; "
      "with infinity on the diagonal the original graph gets 4, 4, 4",
      sorted(L for L, _ in simple_cycles(3, EFn)) == [3 - 1 - 3, 4 - 3] == [-1, 1]
      and sorted(L for L, _ in simple_cycles(3, EF)) == [4, 6] and [FN[v][v] for v in range(3)] == [-1, -1, -2]
      and FN[2][0] == -4 and [CF[v][v] for v in range(3)] == [4, 4, 4])
on("concept floyd-warshall example text", True, CFW,
   "$1\\to2$ (3), $2\\to3$ ($-1$), $3\\to1$ (2), $1\\to3$ (4)", "$(0, 3, 4), (\\infty, 0, -1), (2, \\infty, 0)$",
   "phase 1 finds $3\\to1\\to2$ (5)", "improves $(1, 3)$ to $3 - 1 = 2$", "phase 3 finds $2\\to3\\to1$ (1)",
   "$(0, 3, 2), (1, 0, -1), (2, 5, 0)$", "($3 - 1 - 3 = -1$)", "diagonal entries $-1, -1, -2$",
   "$-4$ for $(3, 1)$", "ends with 4 on the diagonal")

# ---------------------------------------------------------------------------------------- page facts
on("page: section headings and anchors used by other pages", True, page,
   "## 9.1 Introduction", "## 9.2 Lots of single sources", "## 9.3 Reweighting", "## 9.4 Johnson's algorithm",
   "## 9.5 Dynamic programming", "## 9.6 Divide and conquer", "## 9.7 Funny matrix multiplication",
   "## 9.8 Floyd–Warshall", "## Summary")
on("page: meta line (book pages, whole-book PDF, prev, exercises)", True, page,
   "*Algorithms, Chapter 9 · book pp. 309–326 · [whole-book PDF](https://jeffe.cs.illinois.edu/teaching/algorithms/"
   "book/Algorithms-JeffE.pdf) · prev: [[2-algorithms/08-shortest-paths|Chapter 8]] · exercises: "
   "[[2-algorithms/09-all-pairs-shortest-paths-exercises|solved exercises]]*")
check("page: every figure marker has its figure inlined",
      all(f"<!-- fig:a09-{k} -->\n" + FIG[k].strip() in page for k in FIG))

print()
if FAIL:
    print(f"{len(FAIL)} FAILED:", *FAIL, sep="\n  ")
    sys.exit(1)
print("ALL OK")
