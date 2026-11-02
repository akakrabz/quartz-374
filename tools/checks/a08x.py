#!/usr/bin/env python3
"""Checks for content/2-algorithms/08-shortest-paths-exercises.md (solved exercises 8.0-8.8 and 8.11-8.17 of
Erickson's Algorithms).

Ground truth for shortest-path distances is computed by brute force, independently of every algorithm on the page:
dist(v) = -inf iff some negative simple cycle is reachable from s and reaches v (cycles enumerated exhaustively),
otherwise the minimum weight of a simple path from s to v (all simple paths enumerated), or +inf. Every algorithm on
the page is implemented as stated and compared with that ground truth (or with an exhaustive search over walks or
move sequences) on many random small inputs; every counterexample is replayed step by step; the book's examples are
reproduced. Weights are integers, so all comparisons are exact."""
import heapq
import itertools
import random
import sys
from collections import deque

random.seed(8374)
sys.setrecursionlimit(100000)
FAIL = []
INF = float("inf")
NINF = -INF


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail != "" else ""))
    if not cond:
        FAIL.append(name)


# ============================================================================ helpers: weighted digraphs
# A graph is (n, E) with vertices 0..n-1 and E a list of directed edges (u, v, w); no parallel edges.

def rand_digraph(n, p, wlo, whi, loops=False):
    E = []
    for u in range(n):
        for v in range(n):
            if (u != v or loops) and random.random() < p:
                E.append((u, v, random.randint(wlo, whi)))
    return E


def out_adj(n, E):
    A = [[] for _ in range(n)]
    for u, v, w in E:
        A[u].append((v, w))
    return A


def reach(n, E, sources):
    A = out_adj(n, E)
    seen = set(sources)
    Q = deque(sources)
    while Q:
        u = Q.popleft()
        for v, _ in A[u]:
            if v not in seen:
                seen.add(v)
                Q.append(v)
    return seen


def simple_paths(n, E, s):
    """Yield (vertex list, weight) for every simple path starting at s (including the one-vertex path)."""
    A = out_adj(n, E)
    path, on = [s], {s}

    def go(u, wt):
        yield list(path), wt
        for v, w in A[u]:
            if v not in on:
                path.append(v)
                on.add(v)
                yield from go(v, wt + w)
                path.pop()
                on.discard(v)

    yield from go(s, 0)


def simple_cycles(n, E):
    """Yield (vertex list, weight) for every simple directed cycle (self-loops included), each once."""
    A = out_adj(n, E)
    for u, v, w in E:
        if u == v:
            yield [u], w
    for st in range(n):
        path, on = [st], {st}

        def go(u, wt):
            for v, w in A[u]:
                if v == st and u != st:
                    yield list(path), wt + w
                elif v > st and v not in on:
                    path.append(v)
                    on.add(v)
                    yield from go(v, wt + w)
                    path.pop()
                    on.discard(v)

        yield from go(st, 0)


def truth(n, E, s):
    """Brute-force shortest-walk distances from s: -inf, a number, or +inf."""
    R = reach(n, E, [s])
    bad = set()
    for cyc, wt in simple_cycles(n, E):
        if wt < 0 and cyc[0] in R:
            bad |= reach(n, E, cyc)
    best = [INF] * n
    for p, wt in simple_paths(n, E, s):
        best[p[-1]] = min(best[p[-1]], wt)
    return [NINF if v in bad else best[v] for v in range(n)]


def has_neg_cycle_reachable(n, E, s):
    R = reach(n, E, [s])
    return any(wt < 0 and cyc[0] in R for cyc, wt in simple_cycles(n, E))


def dijkstra(n, A, s):
    """A: adjacency lists of (v, w) with w >= 0. Returns dist, pred, extraction order."""
    dist, pred, done, order = [INF] * n, [None] * n, [False] * n, []
    dist[s] = 0
    pq = [(0, s)]
    while pq:
        d, u = heapq.heappop(pq)
        if done[u]:
            continue
        done[u] = True
        order.append(u)
        for v, w in A[u]:
            if d + w < dist[v]:
                dist[v], pred[v] = d + w, u
                heapq.heappush(pq, (dist[v], v))
    return dist, pred, order


def is_acyclic(n, edges):
    """Kahn's algorithm on an edge list of (u, v) pairs."""
    indeg = [0] * n
    A = [[] for _ in range(n)]
    for u, v in edges:
        A[u].append(v)
        indeg[v] += 1
    Q = deque(v for v in range(n) if indeg[v] == 0)
    cnt = 0
    while Q:
        u = Q.popleft()
        cnt += 1
        for v in A[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                Q.append(v)
    return cnt == n


def edge_weight(E):
    return {(u, v): w for u, v, w in E}


# ============================================================================ Exercise 8.0(a)
print("== Exercise 8.0(a): verifying distance labels")


def verify_dist(n, E, s, dist):
    if dist[s] != 0:
        return False
    for u, v, w in E:
        if dist[u] + w < dist[v]:          # tense (inf + w = inf is never < anything)
            return False
    T = [[] for _ in range(n)]
    for u, v, w in E:
        if dist[u] < INF and dist[u] + w == dist[v]:
            T[u].append(v)
    marked, Q = {s}, deque([s])
    while Q:
        u = Q.popleft()
        for v in T[u]:
            if v not in marked:
                marked.add(v)
                Q.append(v)
    return all(v in marked for v in range(n) if dist[v] < INF)


def labels_correct(tr, dist):
    return all(x != NINF for x in tr) and list(dist) == list(tr)


# exhaustive over labels on every 3-vertex digraph (random weights per graph)
pairs3 = [(u, v) for u in range(3) for v in range(3) if u != v]
tot = pos = bad = 0
for mask in range(1 << 6):
    for _ in range(3):
        E = [(u, v, random.randint(-2, 3)) for i, (u, v) in enumerate(pairs3) if mask >> i & 1]
        tr = truth(3, E, 0)
        for d0 in (-1, 0, 1):
            for d1 in (-2, -1, 0, 1, 2, 3, 4, INF):
                for d2 in (-2, -1, 0, 1, 2, 3, 4, INF):
                    dist = [d0, d1, d2]
                    a, b = verify_dist(3, E, 0, dist), labels_correct(tr, dist)
                    tot += 1
                    pos += b
                    bad += (a != b)
check("8.0(a) VerifyDist == ground truth, every labeling in {-2..4, inf} on every 3-vertex digraph", bad == 0,
      f"{tot} labelings, {pos} correct ones, {bad} mismatches")

tot = pos = bad = 0
for trial in range(1500):
    n = random.randint(3, 6)
    E = rand_digraph(n, random.uniform(0.2, 0.6), -4, 9)
    tr = truth(n, E, 0)
    cands = []
    base = [x if x != NINF else -50 for x in tr]
    cands.append(base)
    for _ in range(6):
        d = list(base)
        v = random.randrange(n)
        d[v] = random.choice([INF, (d[v] if d[v] < INF else 0) + random.choice([-2, -1, 1, 2])])
        cands.append(d)
    for d in cands:
        a, b = verify_dist(n, E, 0, d), labels_correct(tr, d)
        tot += 1
        pos += b
        bad += (a != b)
check("8.0(a) VerifyDist == ground truth on random digraphs (true labels and perturbations, negative cycles allowed)",
      bad == 0, f"{tot} labelings, {pos} correct, {bad} mismatches")

# the counterexample: tight in-edges everywhere, nothing tense, labels wrong
Ecx = [(0, 1, 1), (1, 2, 1), (2, 1, -1)]
dcx = [0, 0, 1]
tense = [e for e in Ecx if dcx[e[0]] + e[2] < dcx[e[1]]]
tight_in = all(any(u != v and dcx[u] + w == dcx[v] for u, vv, w in Ecx if vv == v) for v in (1, 2))
check("8.0(a) counterexample s->a (1), a->b (1), b->a (-1) with labels 0,0,1: no tense edge", tense == [])
check("8.0(a) ... every vertex other than s has a tight incoming edge", tight_in)
check("8.0(a) ... but the true distances are 0,1,2 and VerifyDist rejects the labels",
      truth(3, Ecx, 0) == [0, 1, 2] and not verify_dist(3, Ecx, 0, dcx))
check("8.0(a) ... and accepts the true labels 0,1,2", verify_dist(3, Ecx, 0, [0, 1, 2]))

# ============================================================================ Exercise 8.0(b)
print("== Exercise 8.0(b): verifying predecessor pointers")


def verify_pred(n, E, s, pred):
    omega = [None] * n
    for u, v, w in E:
        if v != s and pred[v] == u:
            omega[v] = w
    if any(v != s and pred[v] is not None and omega[v] is None for v in range(n)):
        return False
    kids = [[] for _ in range(n)]
    for v in range(n):
        if v != s and pred[v] is not None:
            kids[pred[v]].append(v)
    d, seen, st = [INF] * n, {s}, [s]
    d[s] = 0
    while st:
        u = st.pop()
        for c in kids[u]:
            if c not in seen:
                seen.add(c)
                d[c] = d[u] + omega[c]
                st.append(c)
    if any(v != s and pred[v] is not None and v not in seen for v in range(n)):
        return False
    return verify_dist(n, E, s, d)


def is_spt(n, E, s, pred, tr):
    """Ground truth: pred defines a shortest-path tree rooted at s."""
    if any(x == NINF for x in tr):
        return False
    W = edge_weight(E)
    for v in range(n):
        if v == s:
            continue
        if tr[v] == INF:
            if pred[v] is not None:
                return False
            continue
        x, length, steps = v, 0, 0
        while x != s:
            p = pred[x]
            if p is None or (p, x) not in W or steps > n:
                return False
            length += W[(p, x)]
            x, steps = p, steps + 1
        if length != tr[v]:
            return False
    return True


tot = pos = bad = 0
for trial in range(300):
    n = random.randint(3, 4)
    E = rand_digraph(n, random.uniform(0.3, 0.8), -3, 6)
    tr = truth(n, E, 0)
    choices = [list(range(n)) + [None] for _ in range(n)]
    for combo in itertools.product(*[[p for p in range(n) if p != v] + [None] for v in range(1, n)]):
        pred = [None] + list(combo)
        a, b = verify_pred(n, E, 0, pred), is_spt(n, E, 0, pred, tr)
        tot += 1
        pos += b
        bad += (a != b)
check("8.0(b) VerifyPred == ground truth, every pred assignment on random 3- and 4-vertex digraphs", bad == 0,
      f"{tot} assignments, {pos} shortest-path trees, {bad} mismatches")

# ============================================================================ Exercise 8.1
print("== Exercise 8.1: looped trees")


def looped_tree_random(n):
    kids = [[] for _ in range(n)]
    par = [None] * n
    for i in range(1, n):
        cand = [x for x in range(i) if len(kids[x]) < 2]
        p = random.choice(cand)
        kids[p].append(i)
        par[i] = p
    E = [(par[i], i, random.randint(0, 9)) for i in range(1, n)]
    leaves = [x for x in range(n) if not kids[x]]
    E += [(l, 0, random.randint(0, 9)) for l in leaves]
    return E, par, kids


def looped_formula(n, E, par, kids):
    W = edge_weight(E)
    D = [0] * n
    order = [0]
    for x in order:
        for c in kids[x]:
            D[c] = D[x] + W[(x, c)]
            order.append(c)
    L = [0] * n
    for x in reversed(order):
        L[x] = W[(x, 0)] if not kids[x] else min(W[(x, c)] + L[c] for c in kids[x])

    def anc(u, v):
        while v is not None:
            if v == u:
                return True
            v = par[v]
        return False

    return D, L, (lambda u, v: D[v] - D[u] if anc(u, v) else L[u] + D[v])


bad = edges_ok = 0
for trial in range(400):
    n = random.randint(2, 14)
    E, par, kids = looped_tree_random(n)
    D, L, f = looped_formula(n, E, par, kids)
    A = out_adj(n, E)
    for u in range(n):
        du, _, _ = dijkstra(n, A, u)
        for v in range(n):
            bad += (du[v] != f(u, v))
    edges_ok += (2 * len(E) <= 3 * n - 1)
check("8.1(b) dist(u,v) = D(v)-D(u) if u is an ancestor of v, else L(u)+D(v): == Dijkstra for all pairs",
      bad == 0, "400 random looped binary trees, 2-14 nodes")
check("8.1(a) a looped binary tree with n nodes has E <= (3n-1)/2 edges", edges_ok == 400)

# the book's looped tree: r a b c d e f g h
names = "r a b c d e f g h".split()
ix = {x: i for i, x in enumerate(names)}
Ebook = [(ix[a], ix[b], w) for a, b, w in [("r", "a", 5), ("r", "b", 8), ("a", "c", 17), ("a", "d", 0), ("c", "e", 23),
                                            ("b", "f", 1), ("f", "g", 9), ("f", "h", 14),
                                            ("e", "r", 4), ("d", "r", 16), ("g", "r", 7), ("h", "r", 42)]]
par_b = [None] * 9
kids_b = [[] for _ in range(9)]
for u, v, w in Ebook[:8]:
    par_b[v] = u
    kids_b[u].append(v)
Db, Lb, fb = looped_formula(9, Ebook, par_b, kids_b)
check("8.1 book's tree: D = r0 a5 b8 c22 d5 e45 f9 g18 h23", Db == [0, 5, 8, 22, 5, 45, 9, 18, 23], Db)
check("8.1 book's tree: L = a16 b17 c27 d16 e4 f16 g7 h42 (r: 21)", Lb == [21, 16, 17, 27, 16, 4, 16, 7, 42], Lb)
Ab = out_adj(9, Ebook)
da, _, _ = dijkstra(9, Ab, ix["a"])
dc, _, _ = dijkstra(9, Ab, ix["c"])
dh, _, _ = dijkstra(9, Ab, ix["h"])
check("8.1 book's tree: dist(a,h) = 16 + 23 = 39, dist(c,a) = 27 + 5 = 32, dist(h,g) = 42 + 18 = 60",
      (da[ix["h"]], dc[ix["a"]], dh[ix["g"]]) == (39, 32, 60) == (fb(1, 8), fb(3, 1), fb(8, 7)))
check("8.1 book's tree: dist(a,e) = 17 + 23 = 40 (down the tree)", da[ix["e"]] == 40 == fb(1, 5))

# ============================================================================ Exercise 8.2
print("== Exercise 8.2: few negative edges")


def one_negative(n, E):
    """Returns the list of dist(s, t) for all t, by the page's two-Dijkstra formula (s = 0)."""
    (x, y, wn), = [e for e in E if e[2] < 0]
    Ap = out_adj(n, [e for e in E if e[2] >= 0])
    ds, _, _ = dijkstra(n, Ap, 0)
    dy, _, _ = dijkstra(n, Ap, y)
    negcyc = dy[x] + wn < 0
    out = []
    for t in range(n):
        if negcyc and ds[x] < INF and dy[t] < INF:
            out.append(NINF)
        else:
            out.append(min(ds[t], ds[x] + wn + dy[t]))
    return out


def k_negative(n, E, s=0, layers_out=None):
    neg = [e for e in E if e[2] < 0]
    k = len(neg)
    plus = out_adj(n, [e for e in E if e[2] >= 0])
    delta = [dijkstra(n, plus, s)[0]]
    for i in range(1, k + 2):
        c = {}
        for x, y, w in neg:
            if delta[i - 1][x] < INF:
                c[y] = min(c.get(y, INF), delta[i - 1][x] + w)
        if not c:
            delta.append([INF] * n)
            continue
        m = min(c.values())
        A2 = [list(a) for a in plus] + [[(y, cy - m) for y, cy in c.items()]]
        d, _, _ = dijkstra(n + 1, A2, n)
        delta.append([d[v] + m for v in range(n)])
    Dk = [min(delta[i][v] for i in range(k + 1)) for v in range(n)]
    improved = [v for v in range(n) if delta[k + 1][v] < Dk[v]]
    badset = reach(n, E, improved) if improved else set()
    if layers_out is not None:
        layers_out.extend(delta)
    return [NINF if v in badset else Dk[v] for v in range(n)]


def rand_with_negatives(n, k, p):
    E = rand_digraph(n, p, 0, 9)
    idx = random.sample(range(len(E)), min(k, len(E)))
    for i in idx:
        u, v, _ = E[i]
        E[i] = (u, v, -random.randint(1, 12))
    return E


bad = cnt = ninf_cases = 0
for trial in range(1500):
    n = random.randint(2, 6)
    E = rand_with_negatives(n, 1, random.uniform(0.25, 0.7))
    if sum(1 for e in E if e[2] < 0) != 1:
        continue
    tr = truth(n, E, 0)
    cnt += 1
    ninf_cases += any(x == NINF for x in tr)
    bad += one_negative(n, E) != tr
check("8.2(a) two Dijkstras: min(d_s(t), d_s(x)+w(x->y)+d_y(t)); -inf iff d_y(x)+w<0, x reached, t reached from y",
      bad == 0, f"{cnt} random digraphs with one negative edge, {ninf_cases} with -inf distances")

bad = cnt = ninf_cases = 0
for trial in range(2500):
    n = random.randint(2, 6)
    k = random.randint(0, 4)
    E = rand_with_negatives(n, k, random.uniform(0.25, 0.7))
    tr = truth(n, E, 0)
    cnt += 1
    ninf_cases += any(x == NINF for x in tr)
    bad += k_negative(n, E) != tr
check("8.2(b) k+2 layers of Dijkstra; -inf = reachable from a vertex improved in layer k+1: == ground truth",
      bad == 0, f"{cnt} random digraphs with 0-4 negative edges, {ninf_cases} with -inf distances")

# the page's figure: s a c b t with s->a 1, a->c 2, b->c 2, s->t 2 and negative a->b -3, c->t -2
vf = {x: i for i, x in enumerate("s a b c t".split())}
Efig = [(vf[a], vf[b], w) for a, b, w in [("s", "a", 1), ("a", "c", 2), ("b", "c", 2), ("s", "t", 2), ("a", "b", -3),
                                         ("c", "t", -2)]]
lay = []
res = k_negative(5, Efig, 0, lay)
check("8.2(b) figure: delta_0(t), delta_1(t), delta_2(t) = 2, 1, -2 and dist(s,t) = -2 (ground truth agrees)",
      [lay[i][vf["t"]] for i in range(3)] == [2, 1, -2] and res[vf["t"]] == -2 == truth(5, Efig, 0)[vf["t"]])
check("8.2(b) figure: layers 0,1,2 = (s0 a1 b inf c3 t2), (b-2 c0 t1), (t-2); layer 3 all inf",
      [lay[0][vf[x]] for x in "sabct"] == [0, 1, INF, 3, 2] and [lay[1][vf[x]] for x in "sabct"] == [INF, INF, -2, 0, 1]
      and [lay[2][vf[x]] for x in "sabct"] == [INF] * 4 + [-2] and lay[3] == [INF] * 5)

# ============================================================================ Exercise 8.3
print("== Exercise 8.3: vertex weights")


def rand_ugraph(n, p):
    return [(u, v) for u, v in itertools.combinations(range(n), 2) if random.random() < p]


bad = cnt = 0
for trial in range(1500):
    n = random.randint(2, 7)
    UE = rand_ugraph(n, random.uniform(0.2, 0.7))
    wt = [random.randint(1, 9) for _ in range(n)]
    s, t = random.sample(range(n), 2)
    DE = [(u, v, wt[v]) for u, v in UE] + [(v, u, wt[u]) for u, v in UE]
    d, _, _ = dijkstra(n, out_adj(n, DE), s)
    alg = wt[s] + d[t]
    brute = INF
    for p, _ in simple_paths(n, [(u, v, 0) for u, v, _ in DE], s):
        if p[-1] == t:
            brute = min(brute, sum(wt[x] for x in p))
    bad += alg != brute
    cnt += brute < INF
check("8.3(b) w(s) + Dijkstra in the directed graph with w(u->v) = w(v) == min vertex weight over all s-t paths",
      bad == 0, f"1500 random graphs, {cnt} with a path")

# (a): every spanning tree weighs the sum of all vertex weights; a WFS tree is a spanning tree of a connected graph
ok = True
for trial in range(300):
    n = random.randint(2, 6)
    UE = rand_ugraph(n, 0.6)
    trees = [T for T in itertools.combinations(UE, n - 1) if len(reach(n, [(u, v, 0) for u, v in T] +
                                                                     [(v, u, 0) for u, v in T], [0])) == n]
    wt = [random.randint(1, 9) for _ in range(n)]
    for T in trees:
        ok &= sum(wt[x] for x in set(itertools.chain(*T)) | ({0} if n == 1 else set())) == sum(wt)
check("8.3(a) every spanning tree has total vertex weight = sum of all vertex weights", ok)

# ============================================================================ Exercise 8.4(a)
print("== Exercise 8.4(a): replacement paths when the shortest path visits every vertex")


def replacement_sweep(n, E, P):
    pos = {v: i for i, v in enumerate(P)}
    W = edge_weight(E)
    D = [0] * n
    for i in range(1, n):
        D[i] = D[i - 1] + W[(P[i - 1], P[i])]
    total = D[n - 1]
    path_idx = {}
    for j, (u, v, w) in enumerate(E):
        if pos[v] == pos[u] + 1:
            path_idx[j] = pos[u]
    starts = [[] for _ in range(n)]
    for j, (a, b, w) in enumerate(E):
        if j in path_idx:
            continue
        if pos[a] < pos[b]:
            starts[pos[a]].append((D[pos[a]] + w + total - D[pos[b]], pos[b]))
    heap, ans = [], []
    for i in range(n - 1):
        for item in starts[i]:
            heapq.heappush(heap, item)
        while heap and heap[0][1] <= i:
            heapq.heappop(heap)
        ans.append(heap[0][0] if heap else INF)
    return [ans[path_idx[j]] if j in path_idx else total for j in range(len(E))]


bad = cnt = inf_cases = 0
tries = 0
while cnt < 1200:
    tries += 1
    n = random.randint(2, 8)
    P = list(range(n))
    random.shuffle(P)
    E = [(P[i], P[i + 1], random.randint(0, 4)) for i in range(n - 1)]
    have = {(u, v) for u, v, _ in E}
    for u in range(n):
        for v in range(n):
            if u != v and (u, v) not in have and random.random() < 0.35:
                E.append((u, v, random.randint(0, 14)))
    s, t = P[0], P[-1]
    d, _, _ = dijkstra(n, out_adj(n, E), s)
    if d[t] != sum(w for _, _, w in E[:n - 1]):
        continue                          # P is not a shortest path: not an instance
    cnt += 1
    alg = replacement_sweep(n, E, P)
    brute = [dijkstra(n, out_adj(n, E[:j] + E[j + 1:]), s)[0][t] for j in range(len(E))]
    inf_cases += INF in brute
    bad += alg != brute
check("8.4(a) bypass-interval sweep == Dijkstra in G minus e, for every edge e", bad == 0,
      f"{cnt} random instances with a shortest Hamiltonian s-t path ({tries} generated), {inf_cases} with an inf entry")

# the page's figure: path s a b c d t (2,1,3,1,2), bypasses s->b 6, a->d 6, b->t 8, c->t 5
pf = {x: i for i, x in enumerate("s a b c d t".split())}
Ep = [(pf[a], pf[b], w) for a, b, w in [("s", "a", 2), ("a", "b", 1), ("b", "c", 3), ("c", "d", 1), ("d", "t", 2),
                                       ("s", "b", 6), ("a", "d", 6), ("b", "t", 8), ("c", "t", 5)]]
alg = replacement_sweep(6, Ep, list(range(6)))
brute = [dijkstra(6, out_adj(6, Ep[:j] + Ep[j + 1:]), 0)[0][5] for j in range(len(Ep))]
check("8.4(a) figure: dist(s,t) = 9; deleting the path edges gives 12, 10, 10, 10, 11; any other edge 9",
      dijkstra(6, out_adj(6, Ep), 0)[0][5] == 9 and alg == brute == [12, 10, 10, 10, 11, 9, 9, 9, 9], alg)
Ep2 = Ep + [(pf["d"], pf["a"], 1)]
check("8.4(a) a backward edge (d->a, weight 1) changes no answer",
      replacement_sweep(6, Ep2, list(range(6)))[:5] == [12, 10, 10, 10, 11] ==
      [dijkstra(6, out_adj(6, Ep2[:j] + Ep2[j + 1:]), 0)[0][5] for j in range(5)])

# ============================================================================ Exercise 8.5
print("== Exercise 8.5: reinserting one edge")
bad = cnt = improved = 0
for trial in range(1500):
    n = random.randint(2, 7)
    G = rand_digraph(n, random.uniform(0.3, 0.8), 0, 9)
    if not G:
        continue
    H = [e for e in G if random.random() < 0.5]
    missing = [e for e in G if e not in H]
    if not missing:
        continue
    s, t = random.sample(range(n), 2)
    ds, _, _ = dijkstra(n, out_adj(n, H), s)
    dt, _, _ = dijkstra(n, out_adj(n, [(v, u, w) for u, v, w in H]), t)
    cand = [(ds[u] + w + dt[v], (u, v, w)) for u, v, w in missing]
    best_val, best_e = min(cand)
    alg = min(ds[t], best_val)
    brute = {e: dijkstra(n, out_adj(n, H + [e]), s)[0][t] for e in missing}
    bad += (alg != min(brute.values())) or (brute[best_e] != min(brute.values()))
    cnt += 1
    improved += best_val < ds[t]
check("8.5 argmin over missing u->v of d_s(u)+w(u->v)+d_t(v) is a best edge; value == brute force", bad == 0,
      f"{cnt} random (G, H) pairs, {improved} where reinsertion helps")

# ============================================================================ Exercise 8.6
print("== Exercise 8.6: Bellman-Ford that returns a negative cycle, and -inf labels")


def bf_cycle(n, E, s):
    dist, pred = [INF] * n, [None] * n
    dist[s] = 0
    for _ in range(n - 1):
        for u, v, w in E:
            if dist[u] + w < dist[v]:
                dist[v], pred[v] = dist[u] + w, u
    for u, v, w in E:
        if dist[u] + w < dist[v]:
            dist[v], pred[v] = dist[u] + w, u
            x = v
            for _ in range(n):
                x = pred[x]
                assert x is not None, "pred chain reached Null"
            cyc, y = [x], pred[x]
            while y != x:
                cyc.append(y)
                y = pred[y]
            return "cycle", cyc[::-1]
    return "tree", (dist, pred)


def bf_minus_inf(n, E, s):
    dist = [INF] * n
    dist[s] = 0
    for _ in range(n - 1):
        for u, v, w in E:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
    heads = [v for u, v, w in E if dist[u] + w < dist[v]]
    badset = reach(n, E, heads) if heads else set()
    return [NINF if v in badset else dist[v] for v in range(n)]


bad_a = bad_b = cnt = cyc_cases = 0
for trial in range(2500):
    n = random.randint(2, 7)
    E = rand_digraph(n, random.uniform(0.2, 0.6), -6, 9)
    random.shuffle(E)
    tr = truth(n, E, 0)
    neg = has_neg_cycle_reachable(n, E, 0)
    kind, res = bf_cycle(n, E, 0)
    W = edge_weight(E)
    R = reach(n, E, [0])
    if kind == "cycle":
        cyc_cases += 1
        cyc = res
        edges_ok = all((cyc[i], cyc[(i + 1) % len(cyc)]) in W for i in range(len(cyc)))
        wsum = sum(W[(cyc[i], cyc[(i + 1) % len(cyc)])] for i in range(len(cyc))) if edges_ok else 0
        ok = neg and edges_ok and wsum < 0 and len(set(cyc)) == len(cyc) and cyc[0] in R
    else:
        dist, pred = res
        ok = (not neg) and list(dist) == tr and is_spt(n, E, 0, pred, tr)
    bad_a += not ok
    bad_b += bf_minus_inf(n, E, 0) != tr
    cnt += 1
check("8.6(a) Bellman-Ford + pred walk: returns a negative cycle of G reachable from s iff one exists, else a SPT",
      bad_a == 0, f"{cnt} random digraphs (shuffled edge orders), {cyc_cases} cycles returned")
check("8.6(b) Bellman-Ford, then -inf for everything reachable from heads of still-tense edges == ground truth",
      bad_b == 0)

# ============================================================================ Ford's algorithm simulator (8.7, 8.8)


class Ford:
    def __init__(self, n, E, s):
        self.n, self.E, self.s = n, E, s
        self.dist, self.pred = [INF] * n, [None] * n
        self.dist[s] = 0
        self.R = set()
        self.W = edge_weight(E)

    def tense(self, e):
        u, v, w = e
        return self.dist[u] + w < self.dist[v]

    def tense_edges(self):
        return [e for e in self.E if self.tense(e)]

    def relax(self, e):
        u, v, w = e
        assert self.tense(e)
        self.dist[v], self.pred[v] = self.dist[u] + w, u
        self.R.add((u, v))

    def P(self):
        return [(self.pred[v], v) for v in range(self.n) if self.pred[v] is not None]

    def X(self):
        return [(u, v) for u, v, w in self.tense_edges()]


def cycles_in(n, pairs, W):
    """All simple cycles (with weights) of the edge set `pairs`."""
    return list(simple_cycles(n, [(u, v, W[(u, v)]) for u, v in set(pairs)]))


# ============================================================================ Exercise 8.7
print("== Exercise 8.7: FellmanBored")
bad = cnt = 0
for trial in range(3000):
    n = random.randint(1, 6)
    E = rand_digraph(n, random.uniform(0.3, 0.8), -5, 9)
    A = out_adj(n, E)
    walk, x = [], 0
    for _ in range(random.randint(0, 8)):
        if not A[x]:
            break
        v, w = random.choice(A[x])
        walk.append((x, v, w))
        x = v
    seq, pos_last = [], -1
    for e in walk:
        for _ in range(random.randint(0, 3)):
            if E:
                seq.append(random.choice(E))
        seq.append(e)
        pos_last = len(seq) - 1
    for _ in range(random.randint(0, 6)):
        if E:
            seq.append(random.choice(E))
    F = Ford(n, E, 0)
    WW = sum(w for _, _, w in walk)
    end = walk[-1][1] if walk else 0
    ok = True
    if pos_last < 0:
        ok &= F.dist[0] <= 0
    for i, e in enumerate(seq):
        if F.tense(e):
            F.relax(e)
        if i >= pos_last:
            ok &= F.dist[end] <= WW
    bad += not ok
    cnt += 1
check("8.7 dist(v_l) <= w(W) at every moment after FellmanBored has examined W's edges in order", bad == 0,
      f"{cnt} random runs, negative edges and cycles allowed")

# ============================================================================ Exercise 8.8
print("== Exercise 8.8: detecting negative cycles with Ford's algorithm")
# (a) counterexample: pred(s) changes, but no negative cycle passes through s
s_, a_, b_ = 0, 1, 2
Ea = [(s_, a_, 0), (a_, b_, -1), (b_, a_, -1), (a_, s_, 100)]
F = Ford(3, Ea, s_)
F.relax(Ea[0])
steps = 1
while not F.tense(Ea[3]):
    F.relax(Ea[1] if F.tense(Ea[1]) else Ea[2])
    steps += 1
check("8.8(a) ... a->s first becomes tense after 51 rounds of a->b, b->a, when dist(a) = -102 < -100",
      steps == 1 + 2 * 51 and F.dist[a_] == -102)
F.relax(Ea[3])
cyc_a = list(simple_cycles(3, Ea))
check("8.8(a) counterexample: the run s->a, then a->b, b->a alternately, then a->s changes pred(s)",
      F.pred[s_] == a_, f"{steps + 1} relaxations, dist(a) = {F.dist[a_] - 0}")
check("8.8(a) ... every cycle through s is nonnegative (s->a->s weighs 100) ...",
      all(wt >= 0 for c, wt in cyc_a if s_ in c) and any(s_ in c for c, wt in cyc_a))
check("8.8(a) ... but the graph has a negative cycle (a->b->a weighs -2), reachable from s and reaching s",
      any(wt < 0 for c, wt in cyc_a) and truth(3, Ea, s_)[s_] == NINF)

# random runs: whenever pred(s) changes, dist(s) = -inf (a negative cycle reachable from s reaches s)
bad = changes = 0
for trial in range(1500):
    n = random.randint(2, 6)
    E = rand_digraph(n, random.uniform(0.3, 0.7), -6, 9)
    tr = truth(n, E, 0)
    F = Ford(n, E, 0)
    for _ in range(300):
        T = F.tense_edges()
        if not T:
            break
        F.relax(random.choice(T))
        if F.pred[0] is not None:
            changes += 1
            bad += tr[0] != NINF
            break
check("8.8(a) corrected claim on random runs: if pred(s) changes, s lies on a negative closed walk (dist(s) = -inf)",
      bad == 0, f"{changes} runs in which pred(s) changed")

# (b) pred(s) never changes although s lies on a negative cycle
Eb = [(0, 1, 1), (1, 0, -2), (0, 2, 0), (2, 3, -1), (3, 2, 0)]
F = Ford(4, Eb, 0)
okb = True
for e in [Eb[0], Eb[2]] + [Eb[3], Eb[4]] * 500:
    okb &= F.tense(e)
    F.relax(e)
    okb &= F.pred[0] is None and F.tense(Eb[1])
check("8.8(b) example: s->a->s weighs -1; relaxing s->a, s->b, then b->c, c->b forever is a legal run",
      okb and sum(w for u, v, w in Eb[:2]) == -1, "1002 relaxations, each of a tense edge")
check("8.8(b) ... pred(s) stays Null although a->s is tense the whole time", okb)

# (c) P u X is always a dag iff no negative cycle is reachable (we check the stronger statement for P alone too)


def avoid_choice(F):
    T = F.tense_edges()
    safe = []
    for e in T:
        u, v, w = e
        x, steps, closes = u, 0, False
        while x is not None and steps <= F.n:
            if x == v:
                closes = True
                break
            x, steps = F.pred[x], steps + 1
        if not closes:
            safe.append(e)
    return random.choice(safe or T)


bad_dir1 = bad_dir2 = bad_neg = 0
n_noneg = n_neg = max_steps_seen = 0
for trial in range(700):
    n = random.randint(2, 6)
    E = rand_digraph(n, random.uniform(0.3, 0.7), -5, 9)
    neg = has_neg_cycle_reachable(n, E, 0)
    W = edge_weight(E)
    for strategy in ("random", "avoid"):
        F = Ford(n, E, 0)
        found = False
        for step in range(20000):
            P, X = F.P(), F.X()
            if not is_acyclic(n, P + X):
                # every cycle of P u X is negative
                bad_neg += any(wt >= 0 for c, wt in cycles_in(n, P + X, W))
                found = True
                if neg and not is_acyclic(n, P):
                    max_steps_seen = max(max_steps_seen, step)
                    break
            if not neg and found:
                break
            T = F.tense_edges()
            if not T:
                break
            F.relax(random.choice(T) if strategy == "random" else avoid_choice(F))
        if neg:
            n_neg += 1
            bad_dir2 += not (found and not is_acyclic(n, F.P()))
        else:
            n_noneg += 1
            bad_dir1 += found
check("8.8(c) no reachable negative cycle: P u X stays a dag in every run (random and cycle-avoiding choices)",
      bad_dir1 == 0, f"{n_noneg} runs to termination")
check("8.8(c) reachable negative cycle: P itself (hence P u X) gets a cycle, even when relaxations avoid closing one",
      bad_dir2 == 0, f"{n_neg} runs, latest at relaxation {max_steps_seen}")
check("8.8(c) every cycle ever seen in P u X has negative weight", bad_neg == 0)

# a negative cycle that s cannot reach is invisible: Ford halts at once, P u X empty
Eu = [(1, 2, -1), (2, 1, -1)]
F = Ford(3, Eu, 0)
check("8.8(c) remark: with only an unreachable negative cycle, no edge is ever tense (P u X stays empty)",
      F.tense_edges() == [] and F.P() == [])

# (d) counterexample: R gets a cycle without any negative cycle
Ed = [(0, 1, 10), (0, 2, 0), (1, 2, 1), (2, 1, 1)]   # s=0, u=1, v=2
F = Ford(3, Ed, 0)
okd = True
for e in [Ed[0], Ed[2], Ed[1], Ed[3]]:
    okd &= F.tense(e)
    F.relax(e)
check("8.8(d) counterexample run s->u, u->v, s->v, v->u is legal and then halts", okd and F.tense_edges() == [],
      f"dist = {F.dist}")
check("8.8(d) ... R = all four edges contains the cycle u->v->u (weight 2) ...", not is_acyclic(3, list(F.R)))
check("8.8(d) ... although the graph has no negative cycle", not any(wt < 0 for c, wt in simple_cycles(3, Ed)))
# the true half: if R is always a dag then no reachable negative cycle (follows from P being a subset of R)
bad = 0
for trial in range(300):
    n = random.randint(2, 6)
    E = rand_digraph(n, 0.5, -5, 9)
    if not has_neg_cycle_reachable(n, E, 0):
        continue
    F = Ford(n, E, 0)
    for _ in range(20000):
        if not is_acyclic(n, list(F.R)):
            break
        F.relax(avoid_choice(F))
    bad += is_acyclic(n, list(F.R))
check("8.8(d) the true half: with a reachable negative cycle, R gets a cycle in every run", bad == 0)

# the infinite-run lemma, numerically: with a reachable negative cycle some label eventually drops below
# -(sum of |w|), which no simple path can reach
bad = 0
for trial in range(300):
    n = random.randint(2, 6)
    E = rand_digraph(n, 0.5, -5, 9)
    if not has_neg_cycle_reachable(n, E, 0):
        continue
    F = Ford(n, E, 0)
    bound = -sum(abs(w) for _, _, w in E)
    hit = False
    for _ in range(50000):
        if min(F.dist) < bound:
            hit = True
            break
        F.relax(avoid_choice(F))
    bad += not hit
check("8.8 lemma: in an endless run some label drops below -(sum of |w(e)|)", bad == 0)

# ============================================================================ Exercise 8.11
print("== Exercise 8.11: every edge negative")


def scc(n, E):
    A = out_adj(n, E)
    RA = out_adj(n, [(v, u, w) for u, v, w in E])
    seen, order = [False] * n, []

    def dfs1(u):
        seen[u] = True
        for v, _ in A[u]:
            if not seen[v]:
                dfs1(v)
        order.append(u)

    for u in range(n):
        if not seen[u]:
            dfs1(u)
    comp = [None] * n

    def dfs2(u, c):
        comp[u] = c
        for v, _ in RA[u]:
            if comp[v] is None:
                dfs2(v, c)

    c = 0
    for u in reversed(order):
        if comp[u] is None:
            dfs2(u, c)
            c += 1
    return comp


def all_negative(n, E, s):
    R = reach(n, E, [s])
    comp = scc(n, E)
    size = {}
    for v in range(n):
        size[comp[v]] = size.get(comp[v], 0) + 1
    loops = {u for u, v, w in E if u == v}
    Z = [v for v in R if size[comp[v]] >= 2 or v in loops]
    badset = reach(n, E, Z) if Z else set()
    U = R - badset
    EU = [(u, v, w) for u, v, w in E if u in U and v in U]
    assert is_acyclic(n, [(u, v) for u, v, w in EU])
    # relax in topological order (Kahn) from s
    indeg = [0] * n
    AU = out_adj(n, EU)
    for u, v, w in EU:
        indeg[v] += 1
    Q = deque(v for v in U if indeg[v] == 0)
    dist = [INF] * n
    if s in U:
        dist[s] = 0
    while Q:
        u = Q.popleft()
        for v, w in AU[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
            indeg[v] -= 1
            if indeg[v] == 0:
                Q.append(v)
    return [NINF if v in badset else dist[v] for v in range(n)]


bad = cnt = ninf = 0
for trial in range(2000):
    n = random.randint(1, 7)
    E = rand_digraph(n, random.uniform(0.1, 0.45), -9, -1, loops=random.random() < 0.3)
    tr = truth(n, E, 0)
    ninf += NINF in tr
    bad += all_negative(n, E, 0) != tr
    cnt += 1
check("8.11 reach + strong components + dag relaxation (O(V+E)) == ground truth", bad == 0,
      f"{cnt} random all-negative digraphs (some with self-loops), {ninf} with -inf distances")

# ============================================================================ Exercises 8.12 and 8.13
print("== Exercises 8.12 and 8.13: best paths and counting shortest paths (Figure 8.18)")
# Figure 8.18: 3x3 grid, named on the page s a b / c d e / f g t (book's figure has no names; A..I row by row)
fig = "A B C D E F G H I".split()
PAGE = dict(zip(fig, "s a b c d e f g t".split()))
fx = {x: i for i, x in enumerate(fig)}
E818 = [(fx[a], fx[b], w) for a, b, w in [
    ("A", "B", 2), ("B", "C", 1), ("A", "I", 14), ("D", "A", 2), ("B", "D", 4), ("B", "E", 3), ("C", "E", 2),
    ("C", "F", 1), ("E", "D", 1), ("F", "E", 1), ("D", "G", 2), ("G", "E", 3), ("E", "H", 5), ("I", "E", 3),
    ("I", "F", 5), ("G", "H", 2), ("H", "I", 4)]]


def best_paths(n, E, s):
    dist, _, _ = dijkstra(n, out_adj(n, E), s)
    T = [[] for _ in range(n)]
    for u, v, w in E:
        if dist[u] < INF and dist[u] + w == dist[v]:
            T[u].append(v)
    hops, pred = [INF] * n, [None] * n
    hops[s] = 0
    Q = deque([s])
    while Q:
        u = Q.popleft()
        for v in T[u]:
            if hops[v] == INF:
                hops[v], pred[v] = hops[u] + 1, u
                Q.append(v)
    return dist, hops, pred, T


def count_paths(n, E, s):
    dist, _, order = dijkstra(n, out_adj(n, E), s)
    N = [0] * n
    N[s] = 1
    for v in order:          # increasing dist: a topological order of the tight dag
        if v == s:
            continue
        N[v] = sum(N[u] for u, vv, w in E if vv == v and dist[u] + w == dist[v])
    return dist, N


d818, hops818, pred818, T818 = best_paths(9, E818, fx["A"])
paths = [(p, wt) for p, wt in simple_paths(9, E818, fx["A"]) if p[-1] == fx["I"]]
short = [p for p, wt in paths if wt == 14]
check("8.12 Figure 8.18: dist(s, t) = 14", d818[fx["I"]] == 14 == min(wt for p, wt in paths))
drawn = [["A", "I"], ["A", "B", "D", "G", "H", "I"], ["A", "B", "E", "H", "I"],
         ["A", "B", "C", "F", "E", "D", "G", "H", "I"]]
check("8.12 Figure 8.18: the four drawn paths are shortest paths with 1, 5, 4 and 8 edges",
      all([fx[x] for x in p] in short for p in drawn))
check("8.12 Figure 8.18: the best path is the single edge s->t", hops818[fx["I"]] == 1 and pred818[fx["I"]] == fx["A"])
dist_c, N818 = count_paths(9, E818, fx["A"])
check("8.13 Figure 8.18: exactly 8 shortest paths from s to t; N(t) = N(s) + N(g) = 1 + 7", N818[fx["I"]] == 8 == len(short), N818[fx["I"]])
check("8.13 Figure 8.18: path counts N = s1 a1 b1 c4 d3 e1 f4 g7 t8",
      N818 == [1, 1, 1, 4, 3, 1, 4, 7, 8], N818)
check("8.13 Figure 8.18: distances s0 a2 b3 c6 d5 e4 f8 g10 t14", dist_c == [0, 2, 3, 6, 5, 4, 8, 10, 14], dist_c)
tight818 = sorted(fig[u] + fig[v] for u in range(9) for v in T818[u])
check("8.12 Figure 8.18: 13 tight edges; the 4 others are c->s, f->d, t->d, t->e (book A..I: D->A, G->E, I->E, I->F)",
      len(tight818) == 13 and sorted(fig[u] + fig[v] for u, v, w in E818 if fig[u] + fig[v] not in tight818)
      == ["DA", "GE", "IE", "IF"], tight818)
check("8.12 Figure 8.18: BFS in the tight dag gives fewest-edge counts s0 a1 b2 c2 d2 e3 f3 g3 t1",
      hops818 == [0, 1, 2, 2, 2, 3, 3, 3, 1], hops818)

bad12 = bad12b = bad13 = cnt = 0
for trial in range(1500):
    n = random.randint(2, 7)
    E = rand_digraph(n, random.uniform(0.25, 0.7), 1, 4)
    dist, hops, pred, T = best_paths(n, E, 0)
    bestw, bestlen, count = [INF] * n, [INF] * n, [0] * n
    for p, wt in simple_paths(n, E, 0):
        v = p[-1]
        if (wt, len(p) - 1) < (bestw[v], bestlen[v]):
            bestw[v], bestlen[v] = wt, len(p) - 1
    for p, wt in simple_paths(n, E, 0):
        count[p[-1]] += wt == bestw[p[-1]]
    W = edge_weight(E)
    ok = True
    for v in range(n):
        ok &= dist[v] == bestw[v] and hops[v] == bestlen[v]
        if dist[v] < INF and v != 0:      # the pred chain is a best path
            x, L, k = v, 0, 0
            while x != 0:
                L, k, x = L + W[(pred[x], x)], k + 1, pred[x]
            ok &= (L, k) == (bestw[v], bestlen[v])
    bad12 += not ok
    # lexicographic alternative with integer weights: V*w + 1
    dlex, _, _ = dijkstra(n, out_adj(n, [(u, v, n * w + 1) for u, v, w in E]), 0)
    bad12b += any(dlex[v] != (n * bestw[v] + bestlen[v] if bestw[v] < INF else INF) for v in range(n))
    _, N = count_paths(n, E, 0)
    bad13 += any(N[v] != count[v] for v in range(n))
    cnt += 1
check("8.12 Dijkstra, tight edges, BFS from s == lexicographically smallest (weight, #edges) over all paths",
      bad12 == 0, f"{cnt} random digraphs with weights 1-4 (many ties)")
check("8.12 alternative: Dijkstra with integer weights V*w(e)+1 gives V*dist + #edges of a best path", bad12b == 0)
check("8.13 Dijkstra, then N(v) = sum of N(u) over tight u->v in extraction order == number of shortest paths",
      bad13 == 0)

# ============================================================================ Exercise 8.14
print("== Exercise 8.14: meeting in the middle")
bad = 0
for trial in range(800):
    n = random.randint(2, 7)
    UE = [(u, v, random.randint(0, 9)) for u, v in rand_ugraph(n, 0.5)]
    DE = UE + [(v, u, w) for u, v, w in UE]
    p, q = random.sample(range(n), 2)
    dp, _, _ = dijkstra(n, out_adj(n, DE), p)
    dq, _, _ = dijkstra(n, out_adj(n, DE), q)
    alg = min(max(dp[t], dq[t]) for t in range(n))
    tp = truth(n, DE, p)
    tq = truth(n, DE, q)
    brute = min(max(tp[t], tq[t]) for t in range(n))
    bad += alg != brute
check("8.14 min over t of max(d(p,t), d(q,t)) by two Dijkstras == brute force", bad == 0, "800 random graphs")
Etrap = [(0, 1, 1), (1, 0, 1), (1, 2, 1), (2, 1, 1)]
dp, _, _ = dijkstra(3, out_adj(3, Etrap), 0)
dq, _, _ = dijkstra(3, out_adj(3, Etrap), 2)
check("8.14 trap: on p -1- a -1- q every vertex minimizes d(p,t)+d(q,t) = 2, but only a gives meeting time 1",
      [dp[t] + dq[t] for t in range(3)] == [2, 2, 2] and [max(dp[t], dq[t]) for t in range(3)] == [2, 1, 2])

# ============================================================================ Exercise 8.15
print("== Exercise 8.15: espresso stops")
bad_a = bad_b = bad_c = 0
for trial in range(1000):
    n = random.randint(2, 7)
    UE = [(u, v, random.randint(1, 12)) for u, v in rand_ugraph(n, 0.5)]
    s, t = random.sample(range(n), 2)
    L = random.randint(1, 12)
    green = [random.random() < 0.5 for _ in range(n)]
    green[s] = green[t] = False
    DE = UE + [(v, u, w) for u, v, w in UE]
    # (a)
    ok_alg = t in reach(n, [e for e in DE if e[2] <= L], [s])
    paths = [p for p, _ in simple_paths(n, [(u, v, 0) for u, v, _ in DE], s) if p[-1] == t]
    W = edge_weight(DE)
    maxe = [max(W[(p[i], p[i + 1])] for i in range(len(p) - 1)) for p in paths]
    ok_brute = any(m <= L for m in maxe)
    bad_a += ok_alg != ok_brute
    # (b): binary search over the sorted distinct lengths
    lens = sorted({w for _, _, w in UE})
    lo, hi, ans = 0, len(lens) - 1, INF
    while lo <= hi:
        mid = (lo + hi) // 2
        if t in reach(n, [e for e in DE if e[2] <= lens[mid]], [s]):
            ans, hi = lens[mid], mid - 1
        else:
            lo = mid + 1
    bad_b += ans != (min(maxe) if maxe else INF)
    # (c): 0/1 weights = greenness of the head
    H = [(u, v, int(green[v])) for u, v, w in DE if w <= L]
    d, _, _ = dijkstra(n, out_adj(n, H), s)
    brute_c = min((sum(green[x] for x in p) for p, m in zip(paths, maxe) if m <= L), default=INF)
    bad_c += d[t] != brute_c
check("8.15(a) WFS from s in the edges of length <= L == brute force over paths", bad_a == 0, "1000 random graphs")
check("8.15(b) binary search over sorted edge lengths with (a) == min over paths of the longest edge", bad_b == 0)
check("8.15(c) Dijkstra with w(u->v) = [v green] on edges <= L == fewest green vertices over all paths", bad_c == 0)

# ============================================================================ Exercise 8.16
print("== Exercise 8.16: shortest walk with a multiple of 3 edges")


def mod3_layered(n, E, s, t):
    LE = [(3 * u + i, 3 * v + (i + 1) % 3, w) for u, v, w in E for i in range(3)]
    d, _, _ = dijkstra(3 * n, out_adj(3 * n, LE), 3 * s)
    return d[3 * t]


def mod3_brute(n, E, s, t):
    """Exact-length DP over walks: best[k][v] = shortest walk from s with exactly k edges; k up to 3n+3."""
    cur = [INF] * n
    cur[s] = 0
    best = cur[t]
    for k in range(1, 3 * n + 4):
        nxt = [INF] * n
        for u, v, w in E:
            if cur[u] + w < nxt[v]:
                nxt[v] = cur[u] + w
        cur = nxt
        if k % 3 == 0:
            best = min(best, cur[t])
    return best


ex16 = "s w t x y z".split()
e16 = {x: i for i, x in enumerate(ex16)}
E16 = [(e16[a], e16[b], 1) for a, b in [("s", "w"), ("w", "t"), ("w", "y"), ("y", "x"), ("x", "s"), ("y", "z"),
                                         ("z", "t")]]
walk16 = [e16[x] for x in "s w y x s w t".split()]
check("8.16 the walk s w y x s w t uses 6 edges of G", all((walk16[i], walk16[i + 1], 1) in E16 for i in range(6)))
check("8.16 book's example: 6 (all weights 1)", mod3_layered(6, E16, 0, 2) == 6 == mod3_brute(6, E16, 0, 2))
bad = 0
for trial in range(1500):
    n = random.randint(1, 7)
    E = rand_digraph(n, random.uniform(0.2, 0.6), 0, 9)
    s, t = random.randrange(n), random.randrange(n)
    bad += mod3_layered(n, E, s, t) != mod3_brute(n, E, s, t)
check("8.16 Dijkstra from (s,0) to (t,0) in V x {0,1,2} == exhaustive DP over walk lengths up to 3V+3", bad == 0)
# a check of the length bound used by the brute force: going further never helps
bad = 0
for trial in range(300):
    n = random.randint(1, 5)
    E = rand_digraph(n, 0.5, 0, 9)
    s, t = random.randrange(n), random.randrange(n)
    cur = [INF] * n
    cur[s] = 0
    best_short = best_long = cur[t]
    for k in range(1, 12 * n + 4):
        nxt = [INF] * n
        for u, v, w in E:
            nxt[v] = min(nxt[v], cur[u] + w)
        cur = nxt
        if k % 3 == 0:
            best_long = min(best_long, cur[t])
            if k <= 3 * n + 3:
                best_short = min(best_short, cur[t])
    bad += best_short != best_long
check("8.16 brute-force bound: walks longer than 3V+3 edges never improve the answer (tested to 12V)", bad == 0)

# ============================================================================ Exercise 8.17
print("== Exercise 8.17: no three consecutive edges of one color, weighted")


def color_state_dijkstra(n, E, col, s, t):
    """Vertices: 0 = start, then (v, c, k) -> 1 + 4v + 2c + (k-1). Edges as on the page."""
    def vid(v, c, k):
        return 1 + 4 * v + 2 * c + (k - 1)

    SE = []
    for (u, v, w), c2 in zip(E, col):
        if u == s:
            SE.append((0, vid(v, c2, 1), w))
        for c in (0, 1):
            for k in (1, 2):
                if c != c2:
                    SE.append((vid(u, c, k), vid(v, c2, 1), w))
        SE.append((vid(u, c2, 1), vid(v, c2, 2), w))
    N = 1 + 4 * n
    d, _, _ = dijkstra(N, out_adj(N, SE), 0)
    if s == t:
        return 0
    return min(d[vid(t, c, k)] for c in (0, 1) for k in (1, 2))


def color_brute(n, E, col, s, t, maxlen):
    A = [[] for _ in range(n)]
    for (u, v, w), c in zip(E, col):
        A[u].append((v, w, c))
    best = 0 if s == t else INF

    def go(u, wt, c1, c2, depth):
        nonlocal best
        if depth == maxlen:
            return
        for v, w, c in A[u]:
            if c1 is not None and c1 == c2 == c:
                continue
            if v == t:
                best = min(best, wt + w)
            go(v, wt + w, c2, c, depth + 1)

    go(s, 0, None, None, 0)
    return best


ex17 = "s a b c d t".split()
e17 = {x: i for i, x in enumerate(ex17)}
RED, BLUE = 0, 1
E17 = [("s", "a", RED), ("a", "b", RED), ("b", "t", RED), ("t", "d", RED), ("d", "c", RED), ("c", "s", RED),
       ("c", "a", BLUE), ("d", "s", BLUE), ("b", "d", BLUE), ("t", "a", BLUE)]
E17w = [(e17[a], e17[b], 1 if c == RED else 2) for a, b, c in E17]
col17 = [c for _, _, c in E17]
check("8.17 book's example (red 1, blue 2): 9", color_state_dijkstra(6, E17w, col17, 0, 5) == 9 ==
      color_brute(6, E17w, col17, 0, 5, 14))
W17 = {(e17[a], e17[b]): (1 if c == RED else 2, c) for a, b, c in E17}
walk_t = [e17[x] for x in "s a b d c a b t".split()]
walk_c = [e17[x] for x in "s a b d c a b c".split()]
legal = all((walk_t[i], walk_t[i + 1]) in W17 for i in range(7))
cols = [W17[(walk_t[i], walk_t[i + 1])][1] for i in range(7)]
no3 = all(not (cols[i] == cols[i + 1] == cols[i + 2]) for i in range(5))
check("8.17 the walk s a b =>d c =>a b t is legal (RRBRBRR) and weighs 9",
      legal and no3 and sum(W17[(walk_t[i], walk_t[i + 1])][0] for i in range(7)) == 9)
check("8.17 the printed walk ends b -> c, but the graph has no edge b -> c (book typo for b -> t)",
      (e17["b"], e17["c"]) not in W17)
bad = 0
for trial in range(700):
    n = random.randint(1, 4)
    E = rand_digraph(n, random.uniform(0.3, 0.7), 0, 6)
    col = [random.randint(0, 1) for _ in E]
    s, t = random.randrange(n), random.randrange(n)
    bad += color_state_dijkstra(n, E, col, s, t) != color_brute(n, E, col, s, t, 4 * n + 3)
check("8.17 Dijkstra in the (vertex, color, run) graph == exhaustive search over all walks of <= 4V+3 edges",
      bad == 0, "700 random red/blue digraphs")

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: " + "; ".join(FAIL))
