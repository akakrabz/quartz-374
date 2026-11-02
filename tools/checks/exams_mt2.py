#!/usr/bin/env python3
"""Checks for the Midterm 2 practice pages (CS/ECE 374 A, Fall 2026):

  content/3-homework-and-exams/midterm-2-practice-1.md
  content/3-homework-and-exams/midterm-2-practice-2.md
  content/3-homework-and-exams/midterm-2-practice-3.md
  content/3-homework-and-exams/midterm-2-dp-practice.md
  content/0-toolkit/09-midterm-2-cheat-sheet.md (the recurrence table and the greedy counterexamples)

No official solutions were posted.  Every algorithm and recurrence on the pages is implemented exactly as the page
states it and compared with brute force that does not use the page's idea (exhaustive search over all choices, all
walks, all partitions, all subsequences, all game moves), on all small inputs or many random ones.  Every iterative
evaluation order is run with a guard that fails if an entry is read before it is written.  Every recurrence solution is
checked numerically (the ratio to the claimed bound settles).  Every number on the pages (the handouts' examples, the
counterexamples, the graph of Practice 2 Problem 1) is recomputed."""
import functools
import heapq
import itertools
import math
import random
import sys
from collections import deque

random.seed(1102)
sys.setrecursionlimit(100000)
INF = math.inf
FAIL = []


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail != "" else ""))
    if not cond:
        FAIL.append(name)


class Guarded:
    """A table that fails if an entry is read before it is written (checks an evaluation order)."""

    def __init__(self):
        self.d = {}
        self.bad = 0

    def __getitem__(self, key):
        if key not in self.d:
            self.bad += 1
            return 0
        return self.d[key]

    def __setitem__(self, key, val):
        self.d[key] = val


def settles(values, lo=0.05, hi=20.0, drift=1.35):
    """values: ratios T(n)/bound(n) for growing n.  True if all lie in [lo, hi] and the last few vary by < drift."""
    tail = values[-4:]
    return all(lo <= v <= hi for v in values) and max(tail) / min(tail) < drift


def dijkstra(adj, src):
    """adj: dict v -> list of (w, weight >= 0).  Returns dict of distances."""
    dist = {v: INF for v in adj}
    dist[src] = 0
    pq = [(0, src)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for v, w in adj[u]:
            if d + w < dist[v]:
                dist[v] = d + w
                heapq.heappush(pq, (dist[v], v))
    return dist


def bfs(adj, src):
    dist = {v: INF for v in adj}
    dist[src] = 0
    q = deque([src])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if dist[v] == INF:
                dist[v] = dist[u] + 1
                q.append(v)
    return dist


# =====================================================================================================================
print("=" * 30, "Practice test 1", "=" * 30)

# ---------------------------------------------------------------- 1(a) recurrences
@functools.lru_cache(None)
def A1(n):
    return 1 if n < 2 else A1(5 * n // 11) + math.sqrt(n)


@functools.lru_cache(None)
def B1(n):
    return 1 if n < 2 else 8 * B1(n // 2) + n * n


@functools.lru_cache(None)
def C1(n):
    return 1 if n < 2 else C1(n // 2) + C1(n // 3) + C1(n // 6) + n


Ns = [10 ** k for k in range(3, 13)]
rA = [A1(n) / math.sqrt(n) for n in Ns]
check("P1 1(a) A(n) = A(5n/11) + sqrt(n) is Theta(sqrt n): A(n)/sqrt(n) settles", settles(rA), [round(x, 3) for x in rA])
Ns2 = [2 ** k for k in range(6, 40, 3)]
rB = [B1(n) / n ** 3 for n in Ns2]
check("P1 1(a) B(n) = 8B(n/2) + n^2 is Theta(n^3): B(n)/n^3 settles", settles(rB), [round(x, 3) for x in rB])
rC = [C1(n) / (n * math.log2(n)) for n in Ns]
check("P1 1(a) C(n) = C(n/2)+C(n/3)+C(n/6) + n is Theta(n log n): C(n)/(n lg n) settles", settles(rC, drift=1.15),
      [round(x, 3) for x in rC])
check("P1 1(a) C: the three fractions sum to 1, so every full level of the recursion tree sums to n",
      abs(1 / 2 + 1 / 3 + 1 / 6 - 1) < 1e-12)


# ---------------------------------------------------------------- 1(b) Foo and Bar
def foo_rec(A, n):  # A is 1-indexed (A[0] unused)
    @functools.lru_cache(None)
    def Foo(i, k):
        if i >= k - 1:
            return 0
        return max(Foo(i, j) + Foo(j, k) for j in range(i + 1, k)) + sum(A[j] for j in range(i, k + 1))
    return Foo(1, n)


def foo_iter(A, n):
    """The page: Foo[1..n, 1..n] (entries with i <= k), i from n down to 1 (outer), k from i up to n (inner)."""
    T = Guarded()
    work = 0
    for i in range(n, 0, -1):
        for k in range(i, n + 1):
            if i >= k - 1:
                T[i, k] = 0
            else:
                T[i, k] = max(T[i, j] + T[j, k] for j in range(i + 1, k)) + sum(A[j] for j in range(i, k + 1))
                work += 2 * (k - i)
    return T[1, n], T.bad, work


okf, okord, maxratio = True, True, 0
for trial in range(300):
    n = random.randint(1, 9)
    A = [0] + [random.randint(-9, 9) for _ in range(n)]
    v, bad, _ = foo_iter(A, n)
    okf &= v == foo_rec(A, n)
    okord &= bad == 0
for n in (20, 40, 80):
    A = [0] + [1] * n
    _, _, work = foo_iter(A, n)
    maxratio = max(maxratio, work / n ** 3)
check("P1 1(b) Foo: the iterative order (i down, k up) equals the recursion on 300 random arrays", okf)
check("P1 1(b) Foo: no entry is read before it is written", okord)
check("P1 1(b) Foo: O(n^2) entries with O(n) work each, O(n^3) total", maxratio < 1, round(maxratio, 3))


def bar_rec(X, n):  # X 1-indexed
    @functools.lru_cache(None)
    def Bar(i, s):
        if i < 0 or s > n:
            return INF
        if i == 0:
            return 0
        return min(Bar(i, 2 * s), X[i] * s + Bar(i - s, s))
    return Bar(n, 1)


def bar_iter(X, n):
    """The page: Bar[0..n, 0..E] with s = 2^e, E = floor(lg n); i from 0 up to n (outer), e from E down to 0 (inner)."""
    E = n.bit_length() - 1
    T = Guarded()

    def get(i, e):
        s = 2 ** e
        if i < 0 or s > n:
            return INF
        return T[i, e]
    entries = 0
    for i in range(0, n + 1):
        for e in range(E, -1, -1):
            s = 2 ** e
            entries += 1
            if i == 0:
                T[i, e] = 0
            else:
                T[i, e] = min(get(i, e + 1), X[i] * s + get(i - s, e))
    return T[n, 0], T.bad, entries, E


okb, okord = True, True
for trial in range(300):
    n = random.randint(1, 20)
    X = [0] + [random.randint(-5, 9) for _ in range(n)]
    v, bad, entries, E = bar_iter(X, n)
    okb &= v == bar_rec(X, n)
    okord &= bad == 0 and entries == (n + 1) * (E + 1)
check("P1 1(b) Bar: the iterative order (i up, s down) equals the recursion on 300 random arrays", okb)
check("P1 1(b) Bar: no entry is read before it is written; (n+1)(floor(lg n)+1) = O(n log n) entries", okord)
okb2 = True
for n in range(1, 12):
    X = [0] + [random.randint(-5, 9) for _ in range(n)]
    E = n.bit_length() - 1
    T = Guarded()
    for e in range(E, -1, -1):          # the other order the page allows: s down (outer), i up (inner)
        for i in range(0, n + 1):
            s = 2 ** e
            if i == 0:
                T[i, e] = 0
            else:
                up = INF if 2 * s > n else T[i, e + 1]
                left = INF if i - s < 0 else T[i - s, e]
                T[i, e] = min(up, X[i] * s + left)
    okb2 &= T.bad == 0 and T[n, 0] == bar_rec(X, n)
check("P1 1(b) Bar: the swapped order (s down outer, i up inner) also works", okb2)


# ---------------------------------------------------------------- 2 Quadhopper
def quad_dp(N):  # N[1..n], each a tuple of four positive integers; returns MaxMoves(1)
    n = len(N) - 1
    M = Guarded()
    for i in range(n, 0, -1):
        M[i] = 1 + max(0 if i + d > n else M[i + d] for d in N[i])
    assert M.bad == 0
    return M[1]


def quad_brute(N):
    n = len(N) - 1
    best = 0

    def go(i, moves):
        nonlocal best
        if i > n:
            best = max(best, moves)
            return
        for d in N[i]:
            go(i + d, moves + 1)
    go(1, 0)
    return best


def quad_greedy(N):
    n = len(N) - 1
    i, moves = 1, 0
    while i <= n:
        i += min(N[i])
        moves += 1
    return moves


okq = True
for trial in range(400):
    n = random.randint(1, 9)
    N = [None] + [tuple(random.randint(1, 5) for _ in range(4)) for _ in range(n)]
    okq &= quad_dp(N) == quad_brute(N)
check("P1 2(b) MaxMoves equals exhaustive search over all move sequences on 400 random puzzles", okq)

H = [None, (1, 8, 4, 2), (5, 2, 3, 6), (13, 67, 42, 86), (3, 8, 9, 4), (7, 2, 1, 6), (3, 8, 4, 9), (6, 9, 7, 10),
     (4, 8, 6, 3), (5, 7, 2, 9), (1, 4, 3, 8), (5, 9, 7, 2), (10, 2, 7, 6), (3, 5, 1, 4)]
seq = [(1, 4), (5, 1), (6, 3), (9, 2), (11, 2), (13, 1)]
pos, okseq = 1, True
for sq, d in seq:
    okseq &= pos == sq and d in H[sq]
    pos += d
check("P1 2: the handout's figure is a legal sequence of 6 moves (4, 1, 3, 2, 2, 1) that leaves the board",
      okseq and pos > 13 and len(seq) == 6)
check("P1 2(a) greedy on the handout's puzzle: 5 moves (squares 1, 2, 4, 7, 13)", quad_greedy(H) == 5)
OPT_H = quad_dp(H)
check("P1 2(b) the handout's puzzle allows 7 moves at most", OPT_H == 7 == quad_brute(H), OPT_H)
MM = Guarded()
for i in range(13, 0, -1):
    MM[i] = 1 + max(0 if i + d > 13 else MM[i + d] for d in H[i])
check("P1 2(b) the table MaxMoves(1..13) on the handout's puzzle is 7 6 1 4 5 4 2 3 3 3 2 1 1",
      [MM[i] for i in range(1, 14)] == [7, 6, 1, 4, 5, 4, 2, 3, 3, 3, 2, 1, 1])
pos, oks7 = 1, True
for d in (1, 3, 1, 3, 2, 2, 1):
    oks7 &= pos <= 13 and d in H[pos]
    pos += d
check("P1 2(b) an optimal sequence: squares 1, 2, 5, 6, 9, 11, 13 with hops 1, 3, 1, 3, 2, 2, 1", oks7 and pos > 13)
small = [None, (1, 2, 2, 2), (4, 4, 4, 4), (1, 1, 1, 1), (1, 1, 1, 1)]
check("P1 2(a) small counterexample: greedy 2 moves, optimum 3 (2, 1, 1)",
      quad_greedy(small) == 2 and quad_dp(small) == 3)


# ---------------------------------------------------------------- 3 highest walk of length <= L
def walk_page(V, edges, h, s, t, L):
    adj = {v: [] for v in V}
    for u, v, l in edges:  # undirected
        adj[u].append((v, l))
        adj[v].append((u, l))
    ds, dt = dijkstra(adj, s), dijkstra(adj, t)
    cand = [h[v] for v in V if ds[v] + dt[v] <= L]
    return max(cand) if cand else None


def walk_brute(V, edges, h, s, t, L):
    adj = {v: [] for v in V}
    for u, v, l in edges:
        adj[u].append((v, l))
        adj[v].append((u, l))
    best = None

    def go(u, length, mx):
        nonlocal best
        if u == t:
            best = mx if best is None else max(best, mx)
        for v, l in adj[u]:
            if length + l <= L:
                go(v, length + l, max(mx, h[v]))
    go(s, 0, h[s])
    return best


okw = True
for trial in range(300):
    nv = random.randint(2, 6)
    V = list(range(nv))
    edges = [(u, v, random.randint(1, 4)) for u, v in itertools.combinations(V, 2) if random.random() < 0.5]
    h = {v: random.randint(0, 20) for v in V}
    s, t = random.sample(V, 2) if random.random() < 0.85 else (0, 0)
    L = random.randint(0, 9)
    okw &= walk_page(V, edges, h, s, t, L) == walk_brute(V, edges, h, s, t, L)
check("P1 3 max{h(v) : dist(s,v) + dist(v,t) <= L} equals exhaustive search over all walks on 300 random graphs", okw)


# ---------------------------------------------------------------- 4 longest verbal subsequence
def verbal_dp(T, words):
    n = len(T)
    M = Guarded()
    M[n + 1] = 0
    for i in range(n, 0, -1):
        best = M[i + 1]
        for j in range(i, n + 1):
            if T[i - 1:j] in words:
                best = max(best, 1 + M[j + 1])
        M[i] = best
    assert M.bad == 0
    return M[1]


def verbal_brute(T, words):
    n = len(T)
    ivs = [(i, j) for i in range(n) for j in range(i, n) if T[i:j + 1] in words]
    best = 0
    for r in range(len(ivs) + 1):
        if r > n:
            break
        for comb in itertools.combinations(ivs, r):
            cs = sorted(comb)
            if all(cs[a][1] < cs[a + 1][0] for a in range(len(cs) - 1)):
                best = max(best, r)
    return best


okv = True
for trial in range(300):
    n = random.randint(0, 8)
    T = "".join(random.choice("ab") for _ in range(n))
    words = {"".join(random.choice("ab") for _ in range(random.randint(1, 3))) for _ in range(random.randint(0, 4))}
    okv &= verbal_dp(T, words) == verbal_brute(T, words)
check("P1 4 MaxWords equals exhaustive search over all sets of disjoint word occurrences on 300 random strings", okv)
ex = "STUDYNAMICEXTRAPROGRAMBLE"
w1, w2 = ["STUDY", "AM", "ICE", "TRAP", "RAMBLE"], ["DYNAMIC", "EXTRA", "PROGRAM"]


def disjoint_in_order(T, ws):
    p = 0
    for w in ws:
        k = T.find(w, p)
        if k < 0:
            return False
        p = k + len(w)
    return True


check("P1 4 the handout's two verbal subsequences occur in order without overlap",
      disjoint_in_order(ex, w1) and disjoint_in_order(ex, w2))
check("P1 4 with exactly the handout's eight words as the dictionary, the answer on its example is 5",
      verbal_dp(ex, set(w1 + w2)) == 5)


# ---------------------------------------------------------------- 5 closest pair
def iwalktheline(P, a):  # brute force stand-in for Timothy's subroutine on the list P (sorted by x)
    best = None
    for i in range(len(P)):
        for j in range(len(P)):
            if P[i][0] <= a < P[j][0]:
                d = math.dist(P[i], P[j])
                if best is None or d < best[0]:
                    best = (d, i, j)
    return best[1], best[2]


calls = []


def closest(P, lo, hi):  # P[lo..hi], 0-indexed inclusive
    if hi - lo + 1 < 2:
        return INF
    if hi - lo + 1 == 2:
        return math.dist(P[lo], P[hi])
    m = (lo + hi) // 2
    sub = P[lo:hi + 1]
    calls.append(len(sub))
    i, j = iwalktheline(sub, P[m][0])
    return min(closest(P, lo, m), closest(P, m + 1, hi), math.dist(sub[i], sub[j]))


okc = True
for trial in range(300):
    n = random.randint(2, 14)
    xs = random.sample(range(100), n)
    ys = random.sample(range(100), n)
    P = sorted(zip(xs, ys))
    okc &= abs(closest(P, 0, n - 1) - min(math.dist(p, q) for p, q in itertools.combinations(P, 2))) < 1e-9
check("P1 5 ClosestPair equals the minimum over all pairs on 300 random point sets", okc)
for n in (64, 1024, 4096):
    calls.clear()
    P = sorted(zip(random.sample(range(10 ** 6), n), random.sample(range(10 ** 6), n)))
    m_ = (0 + n - 1) // 2
    # count only the sizes passed to IWalkTheLine (do not run the quadratic stand-in on big inputs)

    def count(lo, hi):
        if hi - lo + 1 <= 2:
            return 0
        m = (lo + hi) // 2
        return (hi - lo + 1) + count(lo, m) + count(m + 1, hi)
    tot = count(0, n - 1)
    check(f"P1 5 n = {n}: total size of the IWalkTheLine calls is at most n lg n", tot <= n * math.log2(n),
          f"{tot} <= {n * math.log2(n):.0f}")

# =====================================================================================================================
print("=" * 30, "Practice test 2", "=" * 30)
G2 = [("t", "u", 4), ("t", "v", 3), ("t", "x", 6), ("t", "y", 2), ("u", "x", 1), ("u", "z", 4), ("v", "u", 2),
      ("v", "w", 6), ("v", "z", -2), ("w", "u", 5), ("w", "y", 2), ("w", "z", 4), ("y", "x", 2), ("z", "x", 1),
      ("z", "y", -7)]
V2 = sorted({a for e in G2 for a in e[:2]})
out2 = {v: sorted(b for a, b, _ in G2 if a == v) for v in V2}
check("P2 1 the graph has 7 vertices and 15 edges", len(V2) == 7 and len(G2) == 15)


def topo_orders(V, E):
    res = []
    for perm in itertools.permutations(V):
        pos = {v: i for i, v in enumerate(perm)}
        if all(pos[a] < pos[b] for a, b, *_ in E):
            res.append("".join(perm))
    return res


tos = topo_orders(V2, G2)
check("P2 1(d) the graph is a dag with exactly one topological order: t v w u z y x", tos == ["tvwuzyx"], tos)

# (a) depth-first search from v, out-neighbors in alphabetical order
seen, tree_a, order_a = set(), [], []


def dfs(u):
    seen.add(u)
    order_a.append(u)
    for v in out2[u]:
        if v not in seen:
            tree_a.append(u + v)
            dfs(v)


dfs("v")
check("P2 1(a) DFS from v (alphabetical): tree edges v->u, u->x, u->z, z->y, v->w; t is not reachable",
      tree_a == ["vu", "ux", "uz", "zy", "vw"] and "t" not in seen, tree_a)


# every DFS tree from v: enumerate all neighbor orders
def all_dfs_trees(src):
    trees = set()
    orders = [itertools.permutations(out2[v]) for v in V2]
    for choice in itertools.product(*[list(o) for o in orders]):
        nb = dict(zip(V2, choice))
        sn, tr = set(), []

        def go(u):
            sn.add(u)
            for w in nb[u]:
                if w not in sn:
                    tr.append(u + w)
                    go(w)
        go(src)
        trees.add(tuple(sorted(tr)))
    return trees


dts = all_dfs_trees("v")
check("P2 1(a) the depth-first trees rooted at v are not unique (several neighbor orders)", len(dts) > 1, len(dts))

# (b) breadth-first search from w, alphabetical
dist_w, par_w = {"w": 0}, {}
q = deque(["w"])
while q:
    u = q.popleft()
    for v in out2[u]:
        if v not in dist_w:
            dist_w[v] = dist_w[u] + 1
            par_w[v] = u
            q.append(v)
check("P2 1(b) BFS from w (alphabetical): u, y, z at distance 1 (parent w), x at distance 2 (parent u); t, v unreachable",
      dist_w == {"w": 0, "u": 1, "y": 1, "z": 1, "x": 2} and par_w == {"u": "w", "y": "w", "z": "w", "x": "u"},
      (dist_w, par_w))
check("P2 1(b) x could also hang below y or z (edges y->x and z->x, both from distance 1)",
      ("y", "x") in [(a, b) for a, b, _ in G2] and ("z", "x") in [(a, b) for a, b, _ in G2])

# (c) shortest paths from t (dag, negative edges): DP in topological order, ties detected
dist_t = {v: INF for v in V2}
dist_t["t"] = 0
preds_t = {v: [] for v in V2}
for v in "tvwuzyx":
    if v == "t":
        continue
    cands = [(dist_t[a] + w, a) for a, b, w in G2 if b == v]
    best = min(c[0] for c in cands)
    dist_t[v] = best
    preds_t[v] = [a for d, a in cands if d == best]
check("P2 1(c) distances from t: v 3, w 9, u 4, z 1, y -6, x -4",
      dist_t == {"t": 0, "u": 4, "v": 3, "w": 9, "x": -4, "y": -6, "z": 1}, dist_t)
check("P2 1(c) the shortest-path tree is unique: t->u, t->v, v->w, v->z, z->y, y->x",
      preds_t == {"t": [], "u": ["t"], "v": ["t"], "w": ["v"], "x": ["y"], "y": ["z"], "z": ["v"]}, preds_t)


# Bellman-Ford as an independent check
def bellman_ford(V, E, s):
    d = {v: INF for v in V}
    d[s] = 0
    for _ in range(len(V) - 1):
        for a, b, w in E:
            if d[a] + w < d[b]:
                d[b] = d[a] + w
    return d


check("P2 1(c) Bellman-Ford from t gives the same distances", bellman_ford(V2, G2, "t") == dist_t)


def nonneg_dijkstra(V, E, s):
    """Dijkstra that never extracts a vertex twice (relaxes into finished vertices but never rescans them)."""
    dist = {v: INF for v in V}
    dist[s] = 0
    done, first = set(), {}
    while len(done) < len(V):
        u = min((v for v in V if v not in done), key=lambda v: dist[v])
        if dist[u] == INF:
            break
        done.add(u)
        first[u] = dist[u]
        for a, b, w in E:
            if a == u and dist[u] + w < dist[b]:
                dist[b] = dist[u] + w
    return dist, first


dnd, first_nd = nonneg_dijkstra(V2, G2, "t")
check("P2 1(c) Dijkstra without re-extraction finishes y at 2 before z->y is relaxed, and ends with dist(x) = 2, not -4",
      first_nd["y"] == 2 and dnd["x"] == 2 and dist_t["x"] == -4, (first_nd, dnd))


# ---------------------------------------------------------------- 2 rainbow walks
def rainbow_page(V, E, s):
    """G': vertices (v, c) for c in colors, plus (s, None); edge (u, c) -> (v, c') for every edge u->v of color c' != c,
    and (s, None) -> (v, c') for every edge s->v of color c'.  Whatever-first search from (s, None)."""
    adj = {(v, c): [] for v in V for c in "rgb"}
    adj[(s, None)] = []
    for u, v, c2 in E:
        for c in "rgb":
            if c != c2:
                adj[(u, c)].append((v, c2))
        if u == s:
            adj[(s, None)].append((v, c2))
    seen = {(s, None)}
    stack = [(s, None)]
    while stack:
        x = stack.pop()
        for y in adj[x]:
            if y not in seen:
                seen.add(y)
                stack.append(y)
    nV = len(adj)
    nE = sum(len(l) for l in adj.values())
    return {v for v, c in seen}, nV, nE


def rainbow_brute(V, E, s):
    out = {v: [] for v in V}
    for u, v, c in E:
        out[u].append((v, c))
    reach = {s}
    limit = 3 * len(V) + 1

    def go(u, last, depth):
        if depth == limit:
            return
        for v, c in out[u]:
            if c != last:
                reach.add(v)
                go(v, c, depth + 1)
    go(s, None, 0)
    return reach


okr, oksz = True, True
for trial in range(200):
    nv = random.randint(1, 5)
    V = list(range(nv))
    E = [(u, v, random.choice("rgb")) for u in V for v in V if random.random() < 0.3]
    s = random.choice(V)
    got, nV, nE = rainbow_page(V, E, s)
    okr &= got == rainbow_brute(V, E, s)
    oksz &= nV == 3 * nv + 1 and nE <= 3 * len(E)
check("P2 2 reachability in the color-layered graph equals exhaustive search over rainbow walks (200 random graphs)",
      okr)
check("P2 2 the layered graph has 3V + 1 vertices and at most 3E edges", oksz)


# ---------------------------------------------------------------- 3 square-depth
def is_square(digits):
    v = int("".join(map(str, digits)))
    r = math.isqrt(v)
    return r * r == v


def sqdepth_dp(X):  # X 1-indexed list of digits, X[0] unused
    n = len(X) - 1
    SD = Guarded()
    for i in range(n + 1, 0, -1):          # i from n+1 down to 1 (outer)
        for j in range(i - 1, n + 1):      # j from i-1 up to n (inner)
            if i > j:
                SD[i, j] = 0
            else:
                SD[i, j] = (1 if is_square(X[i:j + 1]) else 0) + max(SD[i + 1, j], SD[i, j - 1])
    assert SD.bad == 0
    return SD[1, n]


def sqdepth_brute(X):
    n = len(X) - 1
    best = 0
    for choices in itertools.product("LR", repeat=n):
        i, j, cnt = 1, n, 0
        for c in choices:
            if is_square(X[i:j + 1]):
                cnt += 1
            if c == "L":
                i += 1
            else:
                j -= 1
        best = max(best, cnt)
    return best


oks = True
for trial in range(300):
    n = random.randint(1, 8)
    X = [None] + [random.choice([0, 1, 4, 6, 9, 2, 5]) for _ in range(n)]
    oks &= sqdepth_dp(X) == sqdepth_brute(X)
check("P2 3 SquareDepth equals exhaustive search over all 2^n deletion sequences on 300 random integers", oks)
check("P2 3 the handout's 32492 has square-depth 3 (3249 = 57^2, 324 = 18^2, 4 = 2^2)",
      sqdepth_dp([None, 3, 2, 4, 9, 2]) == 3 and 57 ** 2 == 3249 and 18 ** 2 == 324)
okw4 = all(sum((j - i + 1) ** 2 for i in range(1, n + 1) for j in range(i, n + 1)) <= n ** 4 for n in range(1, 60))
check("P2 3 total IsSquare cost sum over intervals of (j-i+1)^2 is at most n^4", okw4)


# ---------------------------------------------------------------- 4 merge k sorted arrays
merge_work = [0]


def merge2(a, b):
    out, i, j = [], 0, 0
    while i < len(a) and j < len(b):
        merge_work[0] += 1
        if a[i] <= b[j]:
            out.append(a[i])
            i += 1
        else:
            out.append(b[j])
            j += 1
    merge_work[0] += len(a) - i + len(b) - j
    return out + a[i:] + b[j:]


def merge_all(arrs, lo, hi):  # arrays lo..hi
    if lo == hi:
        return list(arrs[lo])
    m = (lo + hi) // 2
    return merge2(merge_all(arrs, lo, m), merge_all(arrs, m + 1, hi))


okm = True
for trial in range(300):
    k, n = random.randint(1, 9), random.randint(0, 6)
    arrs = [sorted(random.randint(0, 30) for _ in range(n)) for _ in range(k)]
    okm &= merge_all(arrs, 0, k - 1) == sorted(x for a in arrs for x in a)
check("P2 4 MergeAll returns the sorted union on 300 random inputs", okm)
okt = True
for k in (2, 8, 64, 512):
    n = 40
    arrs = [sorted(random.sample(range(10 ** 6), n)) for _ in range(k)]
    merge_work[0] = 0
    merge_all(arrs, 0, k - 1)
    okt &= merge_work[0] <= n * k * math.ceil(math.log2(k))
check("P2 4 the merges cost at most n k ceil(lg k) steps (k = 2, 8, 64, 512)", okt)


# ---------------------------------------------------------------- 5 Burgoo
def terms(V, E):
    """Term(v) = 1 + max{Term(u) : u->v}, computed in topological order (page, part (a))."""
    order = [v for perm in [None] for v in toposort(V, E)]
    T = {}
    for v in order:
        T[v] = 1 + max([T[u] for u, w in E if w == v], default=0)
    return T


def toposort(V, E):
    indeg = {v: 0 for v in V}
    for u, v in E:
        indeg[v] += 1
    q = deque([v for v in V if indeg[v] == 0])
    out = []
    while q:
        u = q.popleft()
        out.append(u)
        for a, b in E:
            if a == u:
                indeg[b] -= 1
                if indeg[b] == 0:
                    q.append(b)
    return out


def random_dag(nv, p):
    perm = random.sample(range(nv), nv)
    return list(range(nv)), [(perm[i], perm[j]) for i in range(nv) for j in range(i + 1, nv) if random.random() < p]


oka, okb_ = True, True
for trial in range(150):
    nv = random.randint(1, 5)
    V, E = random_dag(nv, 0.4)
    T = terms(V, E)
    # (a) brute force: fewest terms over all assignments respecting every edge
    bestT = None
    for Tm in range(1, nv + 1):
        for assign in itertools.product(range(1, Tm + 1), repeat=nv):
            if all(assign[u] < assign[v] for u, v in E):
                bestT = Tm
                break
        if bestT:
            break
    oka &= max(T.values()) == bestT and all(T[u] < T[v] for u, v in E)
    # (b) brute force: fewest terms to take >= 75% of the classes, prerequisites included
    need = None
    for Tm in range(0, nv + 1):
        for assign in itertools.product(range(0, Tm + 1), repeat=nv):  # 0 = not taken
            taken = [v for v in V if assign[v] > 0]
            if 4 * len(taken) < 3 * nv:
                continue
            if all(assign[u] > 0 and assign[u] < assign[v] for u, v in E if assign[v] > 0):
                need = Tm
                break
        if need is not None:
            break
    page_b = min(Tm for Tm in range(0, nv + 1) if 4 * sum(1 for v in V if T[v] <= Tm) >= 3 * nv)
    okb_ &= page_b == need
check("P2 5(a) Term(v) is a valid schedule and max Term equals the brute-force minimum number of terms "
      "(150 random dags)", oka)
check("P2 5(b) the smallest T with |{v : Term(v) <= T}| >= 3V/4 equals the brute-force minimum (150 random dags)",
      okb_)

# =====================================================================================================================
print("=" * 30, "Practice test 3", "=" * 30)


@functools.lru_cache(None)
def A3(n):
    return 1 if n < 2 else 3 * A3(n // 2) + n * n


@functools.lru_cache(None)
def B3(n):
    return 1 if n < 2 else 7 * B3(n // 2) + n * n


@functools.lru_cache(None)
def C3(n):
    return 1 if n < 2 else 4 * C3(n // 2) + n * n


Ns3 = [2 ** k for k in range(6, 50, 4)]
check("P3 1(a) A(n) = 3A(n/2) + n^2 is Theta(n^2)", settles([A3(n) / n ** 2 for n in Ns3]))
check("P3 1(a) B(n) = 7B(n/2) + n^2 is Theta(n^lg 7)", settles([B3(n) / n ** math.log2(7) for n in Ns3]))
check("P3 1(a) C(n) = 4C(n/2) + n^2 is Theta(n^2 log n)", settles([C3(n) / (n * n * math.log2(n)) for n in Ns3]))
check("P3 1(a) lg 7 = 2.807...", abs(math.log2(7) - 2.807) < 0.001)

Vb, Eb = list("sabt"), [("s", "a"), ("s", "b"), ("a", "t"), ("b", "t")]
src = [v for v in Vb if all(b != v for a, b in Eb)]
snk = [v for v in Vb if all(a != v for a, b in Eb)]
check("P3 1(b) s->a, s->b, a->t, b->t: one source, one sink, topological orders sabt and sbat",
      src == ["s"] and snk == ["t"] and sorted(topo_orders(Vb, Eb)) == ["sabt", "sbat"])

Ec = [("s", "a", 1), ("a", "t", 4), ("s", "b", 2), ("b", "t", 3)]
paths = [(["s", "a", "t"], 5), (["s", "b", "t"], 5)]
check("P3 1(c) weights 1, 2, 3, 4 are distinct and positive; both s-t paths have length 5, the minimum",
      len({w for *_, w in Ec}) == 4 and all(w > 0 for *_, w in Ec)
      and bellman_ford(list("sabt"), Ec, "s")["t"] == 5)


def huh_rec(A, n):
    @functools.lru_cache(None)
    def Huh(i, k):
        if i > n or k < 0:
            return 0
        if A[i][k] % 2 == 0:
            return min(Huh(i + 1, k - 2), Huh(i + 2, k - 1)) + A[i][k]
        return max(Huh(i + 1, k - 2), Huh(i + 2, k - 1)) - A[i][k]
    return Huh(1, n)


def huh_iter(A, n):
    """Huh[1..n+2, -2..n]; i from n+2 down to 1 (outer), k from -2 up to n (inner)."""
    T = Guarded()
    for i in range(n + 2, 0, -1):
        for k in range(-2, n + 1):
            if i > n or k < 0:
                T[i, k] = 0
            elif A[i][k] % 2 == 0:
                T[i, k] = min(T[i + 1, k - 2], T[i + 2, k - 1]) + A[i][k]
            else:
                T[i, k] = max(T[i + 1, k - 2], T[i + 2, k - 1]) - A[i][k]
    return T[1, n], T.bad


okh = True
for trial in range(300):
    n = random.randint(1, 10)
    A = [[random.randint(-9, 9) for _ in range(n + 1)] for _ in range(n + 1)]
    v, bad = huh_iter(A, n)
    okh &= bad == 0 and v == huh_rec(A, n)
check("P3 1(d) Huh: the iterative order (i down, k up) equals the recursion and never reads an unwritten entry", okh)


# ---------------------------------------------------------------- 2 Elmo
def elmo_after(C, i, j):  # 1-indexed C; Elmo moves on C[i..j]; returns the remaining interval
    if i > j:
        return i, j
    return (i + 1, j) if C[i] > C[j] else (i, j - 1)


def you_dp(C):  # C 1-indexed, C[0] unused
    n = len(C) - 1
    B = Guarded()
    for i in range(n + 1, 0, -1):       # i from n+1 down to 1 (outer)
        for j in range(i - 1, n + 1):   # j from i-1 up to n (inner)
            if i > j:
                B[i, j] = 0
            else:
                B[i, j] = max(C[i] + B[elmo_after(C, i + 1, j)], C[j] + B[elmo_after(C, i, j - 1)])
    assert B.bad == 0
    if n == 0:
        return 0
    return B[elmo_after(C, 1, n)]


def you_brute(C):
    n = len(C) - 1

    @functools.lru_cache(None)
    def play(i, j, my_turn):
        if i > j:
            return 0
        if not my_turn:
            a, b = elmo_after(C, i, j)
            return play(a, b, True)
        return max(C[i] + play(i + 1, j, False), C[j] + play(i, j - 1, False))
    return play(1, n, False)


def you_greedy(C):
    n = len(C) - 1
    i, j, you, turn = 1, n, 0, "E"
    while i <= j:
        if C[i] > C[j]:
            v, i = C[i], i + 1
        else:
            v, j = C[j], j - 1
        if turn == "Y":
            you += v
        turn = "Y" if turn == "E" else "E"
    return you


oke = True
for trial in range(400):
    n = random.randint(0, 9)
    C = [None] + random.sample(range(-20, 21), n)
    oke &= you_dp(C) == you_brute(C)
check("P3 2(b) the recurrence equals game-tree search against greedy Elmo on 400 random rows", oke)
C4 = [None, 4, 3, 7, 1, 2]
tot = sum(C4[1:])
check("P3 2(a) cards 4 3 7 1 2: greedy you gets 5 (Elmo 12); best play gets 9 (Elmo 8), a win",
      you_greedy(C4) == 5 and you_dp(C4) == 9 and tot == 17)
small_ok = True
for n in range(1, 5):
    for perm in itertools.permutations(range(1, 8), n):
        C = [None] + list(perm)
        if 2 * you_dp(C) > sum(perm) and 2 * you_greedy(C) <= sum(perm):
            small_ok = False
check("P3 2(a) no row of at most 4 cards (values 1..7) works as a counterexample, so 5 cards is the minimum",
      small_ok)


# ---------------------------------------------------------------- 3 remoteness
def remote_page(V, E, color):
    adj = {v: [] for v in V}
    for u, v in E:
        adj[u].append(v)
    best = None
    dist = {}
    for c in "rgb":
        a2 = {v: list(adj[v]) for v in V}
        a2["S"] = [v for v in V if color[v] == c]
        d = bfs(a2, "S")
        dist[c] = {v: d[v] - 1 for v in V}
    rem = {v: max(dist[c][v] for c in "rgb") for v in V}
    return min(rem.values()), rem


def remote_brute(V, E, color):
    adj = {v: [] for v in V}
    for u, v in E:
        adj[u].append(v)
    d = {u: bfs(adj, u) for u in V}
    rem = {}
    for v in V:
        rem[v] = max(min([d[u][v] for u in V if color[u] == c], default=INF) for c in "rgb")
    return min(rem.values()), rem


okrm = True
for trial in range(300):
    nv = random.randint(1, 7)
    V = list(range(nv))
    E = [(u, v) for u in V for v in V if u != v and random.random() < 0.3]
    color = {v: random.choice("rgb") for v in V}
    okrm &= remote_page(V, E, color) == remote_brute(V, E, color)
check("P3 3 three BFS runs from color super-sources give every vertex's remoteness (300 random graphs)", okrm)


# ---------------------------------------------------------------- 4 the unique even pair
def find_pair(A):  # 1-indexed
    def good(m):
        return (A[m] - A[1] - (m - 1)) % 2 == 0
    lo, hi = 1, len(A) - 1
    steps = 0
    while hi - lo > 1:   # invariant: good(lo), not good(hi)
        steps += 1
        mid = (lo + hi) // 2
        if good(mid):
            lo = mid
        else:
            hi = mid
    return lo, steps


okp = True
for trial in range(2000):
    n = random.randint(2, 60)
    i = random.randint(1, n - 1)
    p0 = random.randint(0, 1)
    par = [None] + [(p0 + m - 1) % 2 if m <= i else (p0 + m) % 2 for m in range(1, n + 1)]
    A = [None] + [2 * random.randint(-50, 50) + par[m] for m in range(1, n + 1)]
    evens = [m for m in range(1, n) if (A[m] + A[m + 1]) % 2 == 0]
    got, steps = find_pair(A)
    okp &= evens == [i] and got == i and steps <= math.ceil(math.log2(n))
check("P3 4 binary search on good(m) finds the unique i with A[i] + A[i+1] even, in <= ceil(lg n) steps (2000 arrays)",
      okp)
Aex = [None, 17, 40, 23, 72, 39, 88, 62, 13, 40, 53, 92, 21, 10, 73, 68]
trace, lo, hi = [], 1, 15
while hi - lo > 1:
    trace.append((lo, hi))
    mid = (lo + hi) // 2
    if (Aex[mid] - Aex[1] - (mid - 1)) % 2 == 0:
        lo = mid
    else:
        hi = mid
trace.append((lo, hi))
check("P3 4 on the handout's array the search narrows (1,15) (1,8) (4,8) (6,8) (6,7)",
      trace == [(1, 15), (1, 8), (4, 8), (6, 8), (6, 7)], trace)
check("P3 4 on the handout's array m is good exactly when A[m] + m is even",
      all(((Aex[m] - Aex[1] - (m - 1)) % 2 == 0) == ((Aex[m] + m) % 2 == 0) for m in range(1, 16)))
check("P3 4 the handout's array: answer 6", find_pair(Aex)[0] == 6
      and [m for m in range(1, 15) if (Aex[m] + Aex[m + 1]) % 2 == 0] == [6])


# ---------------------------------------------------------------- 5 zigzag walks
def zigzag_page(V, E, s, t):
    """G': (v, F) and (v, B); for each edge u->v of weight w: (u,F)->(v,B) and (v,B)->(u,F), weight w.
    Dijkstra from (s, F); answer min of the distances to (t, F) and (t, B)."""
    adj = {(v, x): [] for v in V for x in "FB"}
    for u, v, w in E:
        adj[(u, "F")].append(((v, "B"), w))
        adj[(v, "B")].append(((u, "F"), w))
    d = dijkstra(adj, (s, "F"))
    return min(d[(t, "F")], d[(t, "B")])


def zigzag_brute(V, E, s, t):
    best = 0 if s == t else INF
    limit = 2 * len(V)

    def go(u, forward, length, depth):
        nonlocal best
        if u == t:
            best = min(best, length)
        if depth == limit:
            return
        for a, b, w in E:
            if forward and a == u:
                go(b, False, length + w, depth + 1)
            if not forward and b == u:
                go(a, True, length + w, depth + 1)
    go(s, True, 0, 0)
    return best


okz = True
for trial in range(250):
    nv = random.randint(1, 5)
    V = list(range(nv))
    E = [(u, v, random.randint(0, 5)) for u in V for v in V if u != v and random.random() < 0.35]
    s, t = random.choice(V), random.choice(V)
    okz &= zigzag_page(V, E, s, t) == zigzag_brute(V, E, s, t)
check("P3 5 Dijkstra in the two-copy graph equals exhaustive search over zigzag walks (250 random graphs)", okz)
Ez = [(a, b, 1) for a, b in ["ab", "bc", "ca", "be", "bf", "ce", "cf", "db", "ed", "df"]]
walk = [("a", "b", "F"), ("d", "b", "B"), ("d", "f", "F"), ("c", "f", "B"), ("c", "e", "F")]
okex = all((a, b, 1) in Ez for a, b, _ in walk) and [d for *_, d in walk] == list("FBFBF")
check("P3 5 the handout's walk a->b<-d->f<-c->e uses five edges of the figure, alternately forward and backward",
      okex)
check("P3 5 in the handout's graph (unit weights) the shortest zigzag walk from a to e has length 5, "
      "so the handout's walk is a shortest one",
      zigzag_page(list("abcdef"), Ez, "a", "e") == 5 == zigzag_brute(list("abcdef"), Ez, "a", "e"))

# =====================================================================================================================
print("=" * 30, "Dynamic programming practice", "=" * 30)


def dance_dp(Score, Wait):  # 1-indexed
    n = len(Score) - 1
    M = Guarded()
    M[n + 1] = 0
    for k in range(n, 0, -1):
        M[k] = max(M[k + 1], Score[k] + M[min(n + 1, k + Wait[k] + 1)])
    assert M.bad == 0
    return M[1]


def dance_brute(Score, Wait):
    n = len(Score) - 1
    best = 0
    for mask in range(1 << n):
        S = [k for k in range(1, n + 1) if mask >> (k - 1) & 1]
        if all(S[a + 1] > S[a] + Wait[S[a]] for a in range(len(S) - 1)):
            best = max(best, sum(Score[k] for k in S))
    return best


okd = True
for trial in range(300):
    n = random.randint(0, 10)
    Score = [None] + [random.randint(0, 20) for _ in range(n)]
    Wait = [None] + [random.randint(0, 4) for _ in range(n)]
    okd &= dance_dp(Score, Wait) == dance_brute(Score, Wait)
check("DP 1 MaxScore equals the best over all subsets of songs on 300 random contests", okd)
check("DP 1 greedy (highest score first) on Score [3,2,2], Wait [2,0,0]: 3, optimum 4",
      dance_dp([None, 3, 2, 2], [None, 2, 0, 0]) == 4 == dance_brute([None, 3, 2, 2], [None, 2, 0, 0]))


def districts_dp(Good, k):  # Good 1-indexed booleans
    n = len(Good) - 1
    pre = [0] * (n + 1)
    for m in range(1, n + 1):
        pre[m] = pre[m - 1] + (1 if Good[m] else 0)
    M = Guarded()
    M[n + 1] = 0
    for i in range(n, 0, -1):
        best = -INF
        for l in range(max(k, 2), 2 * k + 1):   # a district has at least two addresses (i < j)
            j = i + l - 1
            if j > n:
                break
            g = 1 if 2 * (pre[j] - pre[i - 1]) > l else 0
            best = max(best, g + M[j + 1])
        M[i] = best
    assert M.bad == 0
    return M[1]


def districts_brute(Good, k):
    n = len(Good) - 1
    best = -INF

    def go(i, cnt):
        nonlocal best
        if i == n + 1:
            best = max(best, cnt)
            return
        for l in range(1, n + 1):
            j = i + l - 1
            if j > n or not (k <= l <= 2 * k and l >= 2):
                continue
            g = 1 if 2 * sum(1 for m in range(i, j + 1) if Good[m]) > l else 0
            go(j + 1, cnt + g)
    go(1, 0)
    return best


okg = True
for trial in range(300):
    n, k = random.randint(1, 12), random.randint(1, 3)
    Good = [None] + [random.random() < 0.5 for _ in range(n)]
    okg &= districts_dp(Good, k) == districts_brute(Good, k)
check("DP 2 MaxGood equals exhaustive search over all legal partitions (300 random streets; -inf when none exists)",
      okg)
fig = "OXO XOXX OXO XXX OO OXO XXXX".split()
Gfig = [None] + [c == "O" for c in "".join(fig)]
good_in_fig = sum(1 for d in fig if 2 * d.count("O") > len(d))
check("DP 2 the handout's partition: 22 addresses, sizes in [2, 4], 4 good and 3 bad districts",
      len(Gfig) - 1 == 22 and all(2 <= len(d) <= 4 for d in fig) and good_in_fig == 4 and len(fig) == 7)
best_fig = districts_dp(Gfig, 2)
check("DP 2 on the handout's street no legal partition has more than 4 good districts (the figure is optimal)",
      best_fig == 4 == districts_brute(Gfig, 2), best_fig)


def partition_dp(A, k):  # A 1-indexed
    n = len(A) - 1
    pre = [0] * (n + 1)
    for m in range(1, n + 1):
        pre[m] = pre[m - 1] + A[m]
    M = Guarded()
    for i in range(n, 0, -1):
        M[i, 1] = pre[n] - pre[i - 1]
    for m in range(2, k + 1):            # m from 2 up to k (outer)
        for i in range(n, 0, -1):        # i from n down to 1 (inner)
            if n - i + 1 < m:
                M[i, m] = INF
                continue
            M[i, m] = min(max(pre[j] - pre[i - 1], M[j + 1, m - 1]) for j in range(i, n - m + 2))
    assert M.bad == 0
    return M[1, k]


def partition_brute(A, k):
    n = len(A) - 1
    best = INF
    for cuts in itertools.combinations(range(1, n), k - 1):
        b = [0] + list(cuts) + [n]
        best = min(best, max(sum(A[b[r] + 1:b[r + 1] + 1]) for r in range(k)))
    return best


okpa = True
for trial in range(300):
    n = random.randint(1, 9)
    k = random.randint(1, n)
    A = [None] + [random.randint(-6, 9) for _ in range(n)]
    okpa &= partition_dp(A, k) == partition_brute(A, k)
check("DP 3 MinCost equals exhaustive search over all ways to cut into k non-empty intervals (300 random arrays)", okpa)
Aex3 = [None, 1, 6, -1, 8, 0, 3, 3, 9, 8, 8, 7, 4, 9, 8, 9, 4, 8, 4, 8, 2]
check("DP 3 the handout's example: cost 37 (intervals summing to 37, 36, 35)",
      partition_dp(Aex3, 3) == 37 and sum(Aex3[1:10]) == 37 and sum(Aex3[10:15]) == 36 and sum(Aex3[15:21]) == 35)


def mostly_odd_dp(A):  # A 1-indexed; MaxBal(i, l) = max (#odd - #even) over increasing subsequences of length l from A[i]
    n = len(A) - 1
    p = [None] + [1 if A[i] % 2 else -1 for i in range(1, n + 1)]
    MB = Guarded()
    for l in range(1, n + 1):            # l from 1 up to n (outer)
        for i in range(n, 0, -1):        # any order for i (inner)
            if l == 1:
                MB[i, l] = p[i]
            else:
                MB[i, l] = p[i] + max([MB[j, l - 1] for j in range(i + 1, n + 1) if A[j] > A[i]], default=-INF)
    assert MB.bad == 0
    return max([l for l in range(1, n + 1) for i in range(1, n + 1) if MB[i, l] >= 1], default=0)


def mostly_odd_brute(A):
    n = len(A) - 1
    best = 0
    for mask in range(1, 1 << n):
        S = [A[i] for i in range(1, n + 1) if mask >> (i - 1) & 1]
        if all(S[a] < S[a + 1] for a in range(len(S) - 1)) and 2 * sum(1 for x in S if x % 2) > len(S):
            best = max(best, len(S))
    return best


okmo = True
for trial in range(300):
    n = random.randint(1, 10)
    A = [None] + [random.randint(-5, 15) for _ in range(n)]
    okmo &= mostly_odd_dp(A) == mostly_odd_brute(A)
check("DP 4 the length recurrence equals exhaustive search over all subsequences (300 random arrays)", okmo)
Aex4 = [None, 2, 4, 6, 8, 10, 1, 7, 12, 13, 14, 19, 25, 16, 18, 20, 22, 24]
s7 = [4, 6, 7, 13, 14, 19, 25]
s11 = [2, 4, 6, 7, 12, 13, 14, 19, 20, 22, 24]
odd_only = [x for x in Aex4[1:] if x % 2]
check("DP 4 the odd elements of the example form the increasing sequence 1 7 13 19 25 (5 < 7); the answer has 3 evens",
      odd_only == [1, 7, 13, 19, 25] and sum(1 for x in s7 if x % 2 == 0) == 3)
check("DP 4 the handout's example: answer 7; its witness is increasing and mostly odd; the length-11 one is not",
      mostly_odd_dp(Aex4) == 7 and s7 == sorted(s7) and 2 * sum(x % 2 for x in s7) > 7
      and s11 == sorted(s11) and 2 * sum(x % 2 for x in s11) <= 11)

# =====================================================================================================================
print("=" * 30, "Cheat sheet (content/0-toolkit/09-midterm-2-cheat-sheet.md)", "=" * 30)


def rec(a_terms, f, base=1):
    """T(n) = sum of c * T(g(n)) over a_terms (pairs (c, g)) + f(n); T(n) = base for n < 2."""
    @functools.lru_cache(None)
    def T(n):
        if n < 2:
            return base
        return sum(c * T(g(n)) for c, g in a_terms) + f(n)
    return T


lg = math.log2
P2 = [2 ** k for k in range(10, 60, 4)]
P10 = [10 ** k for k in range(3, 15)]
table = [
    ("T(n/2) + 1", rec([(1, lambda n: n // 2)], lambda n: 1), lambda n: lg(n), P2),
    ("T(n/2) + n", rec([(1, lambda n: n // 2)], lambda n: n), lambda n: n, P2),
    ("2T(n/2) + 1", rec([(2, lambda n: n // 2)], lambda n: 1), lambda n: n, P2),
    ("2T(n/2) + n", rec([(2, lambda n: n // 2)], lambda n: n), lambda n: n * lg(n), P2),
    ("2T(n/2) + n^2", rec([(2, lambda n: n // 2)], lambda n: n * n), lambda n: n * n, P2),
    ("3T(n/2) + n", rec([(3, lambda n: n // 2)], lambda n: n), lambda n: n ** lg(3), P2),
    ("4T(n/2) + n", rec([(4, lambda n: n // 2)], lambda n: n), lambda n: n * n, P2),
    ("3T(n/2) + n^2", rec([(3, lambda n: n // 2)], lambda n: n * n), lambda n: n * n, P2),
    ("4T(n/2) + n^2", rec([(4, lambda n: n // 2)], lambda n: n * n), lambda n: n * n * lg(n), P2),
    ("7T(n/2) + n^2", rec([(7, lambda n: n // 2)], lambda n: n * n), lambda n: n ** lg(7), P2),
    ("8T(n/2) + n^2", rec([(8, lambda n: n // 2)], lambda n: n * n), lambda n: n ** 3, P2),
    ("T(n/5) + T(7n/10) + n", rec([(1, lambda n: n // 5), (1, lambda n: 7 * n // 10)], lambda n: n), lambda n: n, P10),
    ("T(n/2) + T(n/3) + n", rec([(1, lambda n: n // 2), (1, lambda n: n // 3)], lambda n: n), lambda n: n, P10),
    ("T(n/3) + T(2n/3) + n", rec([(1, lambda n: n // 3), (1, lambda n: 2 * n // 3)], lambda n: n),
     lambda n: n * lg(n), P10),
    ("T(n/2) + T(n/3) + T(n/6) + n", rec([(1, lambda n: n // 2), (1, lambda n: n // 3), (1, lambda n: n // 6)],
                                          lambda n: n), lambda n: n * lg(n), P10),
    ("T(5n/11) + sqrt n", rec([(1, lambda n: 5 * n // 11)], lambda n: math.isqrt(n)), lambda n: math.sqrt(n), P10),
    ("4T(n/16) + sqrt n", rec([(4, lambda n: n // 16)], lambda n: math.isqrt(n)), lambda n: math.sqrt(n) * lg(n),
     [16 ** k for k in range(3, 16)]),
    ("T(n/2) + lg n", rec([(1, lambda n: n // 2)], lambda n: lg(n)), lambda n: lg(n) ** 2, P2),
    ("T(sqrt n) + 1", rec([(1, lambda n: math.isqrt(n))], lambda n: 1), lambda n: lg(lg(n)),
     [2 ** (2 ** k) for k in range(3, 13)]),
]
for name, T, bound, Ns_ in table:
    vals = [T(n) / bound(n) for n in Ns_]
    check(f"Cheat sheet 2: {name} = Theta(stated solution)", settles(vals, drift=1.25), [round(v, 3) for v in vals[-4:]])


@functools.lru_cache(None)
def sub1(n):
    return 1 if n == 0 else sub1(n - 1) + 1


@functools.lru_cache(None)
def subn(n):
    return 1 if n == 0 else subn(n - 1) + n


@functools.lru_cache(None)
def hanoi(n):
    return 0 if n == 0 else 2 * hanoi(n - 1) + 1


check("Cheat sheet 2: T(n-1) + 1 = Theta(n), T(n-1) + n = Theta(n^2), 2T(n-1) + 1 = 2^n - 1 exactly",
      sub1(500) == 501 and subn(500) == 1 + 500 * 501 // 2 and all(hanoi(n) == 2 ** n - 1 for n in range(60)))
check("Cheat sheet 2: lg 3 ~ 1.585, lg 5 ~ 2.32, lg 7 ~ 2.807",
      abs(lg(3) - 1.585) < 5e-4 and abs(lg(5) - 2.32) < 5e-3 and abs(lg(7) - 2.807) < 5e-4)
check("Cheat sheet 2: sum over intervals of (j-i+1)^2 is Theta(n^4) (ratio to n^4 tends to 1/12)",
      all(abs(sum((j - i + 1) ** 2 for i in range(1, n + 1) for j in range(i, n + 1)) / n ** 4 - 1 / 12) < 0.2 / 12
          for n in (100, 200)))


def coins_greedy(amount, coins):
    cnt = 0
    for c in sorted(coins, reverse=True):
        cnt += amount // c
        amount %= c
    return cnt


@functools.lru_cache(None)
def coins_best(amount):
    return 0 if amount == 0 else 1 + min(coins_best(amount - c) for c in (1, 3, 4) if c <= amount)


check("Cheat sheet 3: coins {1,3,4} paying 6: greedy 3 coins, best 2", coins_greedy(6, (1, 3, 4)) == 3 and coins_best(6) == 2)
check("Cheat sheet 3: the quadhopper, card and dance counterexamples (as on the practice pages)",
      quad_greedy(small) == 2 and quad_dp(small) == 3 and you_greedy(C4) == 5 and you_dp(C4) == 9
      and dance_dp([None, 3, 2, 2], [None, 2, 0, 0]) == 4)

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: {FAIL}")
