#!/usr/bin/env python3
"""Checks for every concrete claim on content/2-algorithms/08-shortest-paths.md and the concept pages
shortest-paths, breadth-first-search, dijkstras-algorithm, bellman-ford.

Every pseudocode block on the page is transcribed line for line — InitSSSP/Relax/FordSSSP (with a random choice of
tense edge), BFS and BFSWithToken, DagSSSP in its three forms, Dijkstra (with an indexed binary heap: Insert,
ExtractMin, DecreaseKey) and NonnegativeDijkstra, BellmanFord in both forms, Moore with the token, BellmanFordDP and
its three refinements — and compared with independent brute force on thousands of random graphs: shortest simple
paths by exhaustive enumeration, shortest walks with at most i edges by enumerating all such walks, negative cycles
by enumerating all simple cycles, plus Floyd–Warshall on larger graphs. Every invariant the page states (Ford's four
claims, Lemma 8.1, Lemmas 8.3/8.4, Lemmas 8.6/8.7, the Dijkstra tense-edge invariant) is checked at run time. Then
every example on the pages (the book's BFS graph, dag and negative-edge graph, the Dijkstra example, the negative-edge
counterexample, the Bellman–Ford table, the Shier–Witzgall graphs, the reductions, the concept-page examples) is
recomputed and compared with the numbers, traces and tables printed on the pages and in the figures."""
import heapq
import itertools
import math
import os
import random
import re
import sys
from collections import deque

sys.setrecursionlimit(20000)
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
PAGE = os.path.join(ROOT, "content", "2-algorithms", "08-shortest-paths.md")
CONCEPTS = os.path.join(ROOT, "content", "concepts")
FIGS = os.path.join(HERE, "..", "figs")
FAIL = []
random.seed(8374)
INF = math.inf
TOKEN = "✠"


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAIL.append(name)


def read(path):
    return open(path, encoding="utf-8").read()


# =====================================================================================================
# Weighted directed graphs: dict vertex -> ordered list of (w_vertex, weight). Dict order = order of "for all
# vertices"; list order = order of "for all edges u->v". EDGES(G) = edge list in that order.
def wgraph(vertices, edges):
    """edges: list of (u, v, w)."""
    G = {v: [] for v in vertices}
    for u, v, w in edges:
        G[u].append((v, w))
    return G


def edges_of(G):
    return [(u, v, w) for u in G for (v, w) in G[u]]


def rev(G):
    R = {v: [] for v in G}
    for u, v, w in edges_of(G):
        R[v].append((u, w))
    return R


def rand_graph(n, p, wlo, whi, rng=random, loops=False):
    G = {v: [] for v in range(n)}
    for u in range(n):
        for v in range(n):
            if (u != v or loops) and rng.random() < p:
                G[u].append((v, rng.randint(wlo, whi)))
    return G


def rand_dag(n, p, wlo, whi, rng=random):
    perm = list(range(n))
    rng.shuffle(perm)
    G = {v: [] for v in range(n)}
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < p:
                G[perm[i]].append((perm[j], rng.randint(wlo, whi)))
    for v in G:
        rng.shuffle(G[v])
    return G


def reach_from(G, s):
    seen, st = {s}, [s]
    while st:
        u = st.pop()
        for v, _ in G[u]:
            if v not in seen:
                seen.add(v)
                st.append(v)
    return seen


# ------------------------------------------------------------------ brute-force references (no relaxation at all)
def brute_simple_paths(G, s):
    """Shortest SIMPLE path length from s to every vertex, by enumerating every simple path (DFS over paths)."""
    best = {v: INF for v in G}
    best[s] = 0

    def go(u, length, onpath):
        for v, w in G[u]:
            if v not in onpath:
                L = length + w
                if L < best[v]:
                    best[v] = L
                onpath.add(v)
                go(v, L, onpath)
                onpath.discard(v)

    go(s, 0, {s})
    return best


def brute_walks_at_most(G, s, i):
    """dist_{<=i}(v): shortest WALK from s with at most i edges, by enumerating every such walk."""
    best = {v: INF for v in G}

    def go(u, length, k):
        if length < best[u]:
            best[u] = length
        if k == i:
            return
        for v, w in G[u]:
            go(v, length + w, k + 1)

    go(s, 0, 0)
    return best


def simple_cycles(G):
    """Every simple directed cycle (as a vertex tuple starting at its smallest vertex) with its weight; brute force."""
    V = list(G)
    W = {}
    for u, v, w in edges_of(G):
        W[(u, v)] = min(w, W.get((u, v), INF))
    out = []
    idx = {v: i for i, v in enumerate(V)}
    for k in range(1, len(V) + 1):
        for combo in itertools.combinations(V, k):
            first = combo[0]
            for perm in itertools.permutations(combo[1:]):
                cyc = (first,) + perm
                ok, tot = True, 0
                for a, b in zip(cyc, cyc[1:] + (first,)):
                    if (a, b) not in W:
                        ok = False
                        break
                    tot += W[(a, b)]
                if ok:
                    out.append((cyc, tot))
    return out


def neg_cycle_reachable(G, s):
    R = reach_from(G, s)
    return any(tot < 0 and any(v in R for v in cyc) for cyc, tot in simple_cycles(G))


def floyd_warshall(G):
    V = list(G)
    d = {(u, v): (0 if u == v else INF) for u in V for v in V}
    for u, v, w in edges_of(G):
        d[(u, v)] = min(d[(u, v)], w)
    for k in V:
        for i in V:
            if d[(i, k)] == INF:
                continue
            for j in V:
                if d[(i, k)] + d[(k, j)] < d[(i, j)]:
                    d[(i, j)] = d[(i, k)] + d[(k, j)]
    return d


def walk_weight(G, walk):
    tot = 0
    for a, b in zip(walk, walk[1:]):
        ws = [w for (v, w) in G[a] if v == b]
        if not ws:
            return None
        tot += min(ws)
    return tot


def pred_path(pred, s, v, limit):
    path = [v]
    while path[-1] != s:
        p = pred[path[-1]]
        if p is None or len(path) > limit:
            return None
        path.append(p)
    return path[::-1]


def pred_acyclic(pred):
    for v in pred:
        seen, x = set(), v
        while x is not None:
            if x in seen:
                return False
            seen.add(x)
            x = pred[x]
    return True


# =====================================================================================================
# The page's pseudocode
def InitSSSP(G, s):
    dist = {v: INF for v in G}
    pred = {v: None for v in G}
    dist[s] = 0
    return dist, pred


def is_tense(dist, u, v, w):
    return dist[u] + w < dist[v]


def FordSSSP(G, s, rng=random, cap=20000, track=None):
    """Relax a uniformly random tense edge until none is left. Returns (dist, pred, halted, relaxations).
    track: dict that receives the walk behind every dist value and the invariant results."""
    dist, pred = InitSSSP(G, s)
    E = edges_of(G)
    walk = {s: [s]}
    nrel = 0
    inv1 = inv2 = invtree = True
    while True:
        T = [(u, v, w) for (u, v, w) in E if is_tense(dist, u, v, w)]
        if not T:
            break
        if nrel >= cap:
            if track is not None:
                track.update(inv1=inv1, inv2=inv2, invtree=invtree)
            return dist, pred, False, nrel
        u, v, w = rng.choice(T)
        dist[v] = dist[u] + w          # Relax(u->v)
        pred[v] = u
        walk[v] = walk[u] + [v]
        nrel += 1
        if track is not None:
            # Claim 1: dist(v) is the length of a walk from s to v (the walk that produced it)
            for x in walk:
                if walk[x][0] != s or walk[x][-1] != x or walk_weight(G, walk[x]) != dist[x]:
                    inv1 = False
            # Claim 2 (no negative cycles): that walk is a simple path
            if track.get("no_neg"):
                if any(len(set(walk[x])) != len(walk[x]) for x in walk):
                    inv2 = False
                if not pred_acyclic(pred):
                    invtree = False
    if track is not None:
        track.update(inv1=inv1, inv2=inv2, invtree=invtree)
    return dist, pred, True, nrel


def BFS(G, s):
    """The book's BFS: InitSSSP, queue of vertices, relax u->v with weight 1 when tense."""
    dist, pred = InitSSSP(G, s)
    Q = deque([s])
    while Q:
        u = Q.popleft()
        for v, _ in G[u]:
            if dist[v] > dist[u] + 1:
                dist[v] = dist[u] + 1
                pred[v] = u
                Q.append(v)
    return dist, pred


def BFS_marks(G, s):
    """The same with the test "if dist(v) = infinity"."""
    dist, pred = InitSSSP(G, s)
    Q = deque([s])
    while Q:
        u = Q.popleft()
        for v, _ in G[u]:
            if dist[v] == INF:
                dist[v] = dist[u] + 1
                pred[v] = u
                Q.append(v)
    return dist, pred


def BFSWithToken(G, s, weighted=False, moore=False, cap_phases=None, log=None):
    """BFSWithToken (weighted=False) and Moore (weighted=True, moore=True: push only if not already queued).
    Returns dist, pred, the pulled sequence (with TOKEN), per-phase snapshots (dist, queue) at each token pull,
    counters, and whether it halted."""
    dist, pred = InitSSSP(G, s)
    Q = deque([s, TOKEN])
    pulled, snaps = [], []
    pushes = {v: 0 for v in G}
    pushes[s] = 1
    pulls = {v: 0 for v in G}
    compares = {}
    token_pulls = 0
    while any(x != TOKEN for x in Q):
        u = Q.popleft()
        pulled.append(u)
        if log is not None:
            log.append(("pull", u, dict(dist)))
        if u == TOKEN:
            token_pulls += 1
            snaps.append((dict(dist), [x for x in Q]))
            if cap_phases is not None and token_pulls >= cap_phases:
                return dist, pred, pulled, snaps, pushes, pulls, compares, False
            Q.append(TOKEN)
        else:
            pulls[u] += 1
            for v, w in G[u]:
                ww = w if weighted else 1
                compares[(u, v)] = compares.get((u, v), 0) + 1
                if log is not None:
                    log.append(("cmp", (u, v, w), dist[v] > dist[u] + ww))
                if dist[v] > dist[u] + ww:
                    dist[v] = dist[u] + ww
                    pred[v] = u
                    if not moore or v not in Q:
                        Q.append(v)
                        pushes[v] += 1
    return dist, pred, pulled, snaps, pushes, pulls, compares, True


def Moore(G, s, cap_phases=None, log=None):
    return BFSWithToken(G, s, weighted=True, moore=True, cap_phases=cap_phases, log=log)


def topo_order(G, rng=None):
    """A topological order (Kahn, with random choice among sources if rng is given)."""
    indeg = {v: 0 for v in G}
    for u, v, w in edges_of(G):
        indeg[v] += 1
    S = [v for v in G if indeg[v] == 0]
    out = []
    while S:
        i = rng.randrange(len(S)) if rng else 0
        u = S.pop(i)
        out.append(u)
        for v, w in G[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                S.append(v)
    return out if len(out) == len(G) else None


def DagSSSP_dp(G, s, order):
    """Figure 8.7: dynamic programming, pulling over incoming edges, in topological order."""
    R = rev(G)
    dist = {}
    for v in order:
        if v == s:
            dist[v] = 0
        else:
            dist[v] = INF
            for u, w in R[v]:
                if dist[v] > dist[u] + w:
                    dist[v] = dist[u] + w
    return dist


def DagSSSP_ford(G, s, order, trace=None):
    """Figure 8.8: InitSSSP, then relax tense incoming edges in topological order."""
    R = rev(G)
    dist, pred = InitSSSP(G, s)
    for v in order:
        for u, w in R[v]:
            if is_tense(dist, u, v, w):
                dist[v] = dist[u] + w
                pred[v] = u
                if trace is not None:
                    trace.append((u, v, dist[v]))
    return dist, pred


def PushDagSSSP(G, s, order, trace=None):
    """Relax tense OUTGOING edges in topological order."""
    dist, pred = InitSSSP(G, s)
    for u in order:
        for v, w in G[u]:
            if is_tense(dist, u, v, w):
                dist[v] = dist[u] + w
                pred[v] = u
                if trace is not None:
                    trace.append((u, v, dist[v]))
    return dist, pred


class IndexedHeap:
    """Binary min-heap with Insert, ExtractMin, DecreaseKey and membership; ties broken by insertion counter."""

    def __init__(self):
        self.h, self.pos, self.cnt = [], {}, 0
        self.ops = {"Insert": 0, "ExtractMin": 0, "DecreaseKey": 0}

    def __contains__(self, x):
        return x in self.pos

    def __len__(self):
        return len(self.h)

    def _less(self, i, j):
        return self.h[i][:2] < self.h[j][:2]

    def _swap(self, i, j):
        self.h[i], self.h[j] = self.h[j], self.h[i]
        self.pos[self.h[i][2]] = i
        self.pos[self.h[j][2]] = j

    def _up(self, i):
        while i > 0 and self._less(i, (i - 1) // 2):
            self._swap(i, (i - 1) // 2)
            i = (i - 1) // 2

    def _down(self, i):
        n = len(self.h)
        while True:
            m = i
            for c in (2 * i + 1, 2 * i + 2):
                if c < n and self._less(c, m):
                    m = c
            if m == i:
                return
            self._swap(i, m)
            i = m

    def insert(self, x, key):
        self.ops["Insert"] += 1
        self.cnt += 1
        self.h.append((key, self.cnt, x))
        self.pos[x] = len(self.h) - 1
        self._up(len(self.h) - 1)

    def extract_min(self):
        self.ops["ExtractMin"] += 1
        self._swap(0, len(self.h) - 1)
        key, _, x = self.h.pop()
        del self.pos[x]
        if self.h:
            self._down(0)
        return x, key

    def decrease_key(self, x, key):
        self.ops["DecreaseKey"] += 1
        i = self.pos[x]
        assert key <= self.h[i][0]
        self.h[i] = (key, self.h[i][1], x)
        self._up(i)

    def items(self):
        return {x: k for (k, _, x) in self.h}


def Dijkstra(G, s, cap=200000, trace=None, invariant=None):
    """Figure 8.11 (the book's Dijkstra: re-Insert a vertex whose distance drops after it was extracted).
    trace: list receiving (u, dist(u), [relaxed edges with 'Insert'/'DecreaseKey'], queue after the step).
    invariant: dict; checks 'every tense edge u->v has u in the queue or u = the vertex being scanned'."""
    dist, pred = InitSSSP(G, s)
    PQ = IndexedHeap()
    PQ.insert(s, 0)
    extracted, nrel, extract_seq, d_seq = {v: 0 for v in G}, 0, [], []
    E = edges_of(G)
    while len(PQ):
        u, key = PQ.extract_min()
        extracted[u] += 1
        extract_seq.append(u)
        d_seq.append(dist[u])
        rel = []
        for v, w in G[u]:
            if is_tense(dist, u, v, w):
                dist[v] = dist[u] + w
                pred[v] = u
                nrel += 1
                if nrel > cap:
                    return dist, pred, dict(halted=False, extracted=extracted, relax=nrel, seq=extract_seq,
                                            d=d_seq, ops=PQ.ops)
                if v in PQ:
                    PQ.decrease_key(v, dist[v])
                    rel.append((u, v, "DecreaseKey"))
                else:
                    PQ.insert(v, dist[v])
                    rel.append((u, v, "Insert"))
        if invariant is not None:
            for (a, b, w) in E:
                if is_tense(dist, a, b, w) and a not in PQ:
                    invariant["ok"] = False
        if trace is not None:
            trace.append((u, dist[u], rel, PQ.items()))
    return dist, pred, dict(halted=True, extracted=extracted, relax=nrel, seq=extract_seq, d=d_seq, ops=PQ.ops)


def NonnegativeDijkstra(G, s, info=None):
    """Figure 8.13: Insert every vertex at the start; only DecreaseKey afterwards. A Relax into a vertex that is no
    longer in the queue updates dist and pred, but the vertex is never scanned again (it cannot be decreased)."""
    dist, pred = InitSSSP(G, s)
    PQ = IndexedHeap()
    for v in G:
        PQ.insert(v, dist[v])
    late = 0
    while len(PQ):
        u, _ = PQ.extract_min()
        for v, w in G[u]:
            if is_tense(dist, u, v, w):
                dist[v] = dist[u] + w
                pred[v] = u
                if v in PQ:
                    PQ.decrease_key(v, dist[v])
                else:
                    late += 1
    if info is not None:
        info["late"] = late
        info["ops"] = PQ.ops
    return dist, pred


def NonnegativeDijkstra_skip(G, s):
    """The common variant that never relaxes an edge into an already extracted vertex."""
    dist, pred = InitSSSP(G, s)
    PQ = IndexedHeap()
    for v in G:
        PQ.insert(v, dist[v])
    while len(PQ):
        u, _ = PQ.extract_min()
        for v, w in G[u]:
            if v in PQ and is_tense(dist, u, v, w):
                dist[v] = dist[u] + w
                pred[v] = u
                PQ.decrease_key(v, dist[v])
    return dist, pred


def BellmanFord_while(G, s, cap=None):
    """BellmanFord(s): while there is a tense edge, relax every tense edge (in edge-list order)."""
    dist, pred = InitSSSP(G, s)
    E = edges_of(G)
    rounds = 0
    cap = cap or 4 * len(G) + 10
    while any(is_tense(dist, u, v, w) for (u, v, w) in E):
        if rounds >= cap:
            return dist, pred, rounds, False
        for (u, v, w) in E:
            if is_tense(dist, u, v, w):
                dist[v] = dist[u] + w
                pred[v] = u
        rounds += 1
    return dist, pred, rounds, True


def BellmanFord(G, s, rounds_out=None, E=None):
    """BellmanFord(s) with V-1 rounds and the negative-cycle test. Returns (dist, pred, 'Negative cycle!' or None).
    E: the order of "for every edge u->v" (default: by tail, in adjacency-list order)."""
    dist, pred = InitSSSP(G, s)
    E = E or edges_of(G)
    for i in range(len(G) - 1):
        for (u, v, w) in E:
            if is_tense(dist, u, v, w):
                dist[v] = dist[u] + w
                pred[v] = u
        if rounds_out is not None:
            rounds_out.append(dict(dist))
    for (u, v, w) in E:
        if is_tense(dist, u, v, w):
            return dist, pred, "Negative cycle!"
    return dist, pred, None


def BellmanFordDP(G, s):
    """dist[i, v] = dist_{<=i}(v) by Bellman's recurrence; rows i = 0 .. V-1."""
    R = rev(G)
    V = list(G)
    d = [{v: (0 if v == s else INF) for v in V}]
    for i in range(1, len(V)):
        row = {}
        for v in V:
            row[v] = d[i - 1][v]
            for u, w in R[v]:
                if row[v] > d[i - 1][u] + w:
                    row[v] = d[i - 1][u] + w
        d.append(row)
    return d


def BellmanFordDP2(G, s):
    V = list(G)
    d = [{v: (0 if v == s else INF) for v in V}]
    for i in range(1, len(V)):
        row = {v: d[i - 1][v] for v in V}
        for (u, v, w) in edges_of(G):
            if row[v] > d[i - 1][u] + w:
                row[v] = d[i - 1][u] + w
        d.append(row)
    return d


def BellmanFordDP3(G, s):
    V = list(G)
    d = [{v: (0 if v == s else INF) for v in V}]
    for i in range(1, len(V)):
        row = {v: d[i - 1][v] for v in V}
        for (u, v, w) in edges_of(G):
            if row[v] > row[u] + w:          # not i-1!
                row[v] = row[u] + w
        d.append(row)
    return d


def BellmanFordFinal(G, s):
    dist = {v: (0 if v == s else INF) for v in G}
    for i in range(1, len(G)):
        for (u, v, w) in edges_of(G):
            if dist[v] > dist[u] + w:
                dist[v] = dist[u] + w
    return dist


# =====================================================================================================
# Helpers for the checks
def undirected(V, E):
    G = {v: [] for v in V}
    for u, v, w in E:
        G[u].append((v, w))
        G[v].append((u, w))
    return G


def unit(G):
    return {u: [(v, 1) for v, _ in G[u]] for u in G}


def has_neg_cycle(G):
    return any(tot < 0 for _, tot in simple_cycles(G))


def pred_paths_ok(G, s, dist, pred, ref):
    """pred pointers form a tree rooted at s whose paths have length dist = ref (finite entries)."""
    if not pred_acyclic(pred):
        return False
    for v in G:
        if ref[v] == INF:
            if dist[v] != INF:
                return False
            continue
        P = pred_path(pred, s, v, len(G) + 1)
        if P is None or walk_weight(G, P) != dist[v] or dist[v] != ref[v]:
            return False
    return True


def minplus_walks(G, s, L):
    """min over walks with at most L edges, by L rounds of min-plus vector-matrix products (independent code)."""
    V = list(G)
    W = {}
    for u, v, w in edges_of(G):
        W[(u, v)] = min(w, W.get((u, v), INF))
    cur = {v: (0 if v == s else INF) for v in V}
    best = dict(cur)
    for _ in range(L):
        nxt = {v: min([cur[u] + W[(u, v)] for u in V if (u, v) in W and cur[u] < INF] or [INF]) for v in V}
        cur = nxt
        best = {v: min(best[v], cur[v]) for v in V}
    return best


def tclosure(G):
    R = {v: reach_from(G, v) for v in G}
    return R


page = read(PAGE)
pflat = re.sub(r"\s+", " ", page)


def onpage(snippet, text=None):
    return re.sub(r"\s+", " ", snippet) in (pflat if text is None else re.sub(r"\s+", " ", text))


def fig_html(name):
    return read(os.path.join(FIGS, name + ".html"))


NUMRE = re.compile(r"^−?\d+$|^∞$")


def fig_labels(name):
    """(weight labels, distance tags): pure-number <text> contents without / with font-weight."""
    h = fig_html(name)
    wl, tags = [], []
    for style, body in re.findall(r'<text [^>]*style="([^"]*)"[^>]*>([^<]*)</text>', h):
        if NUMRE.match(body):
            (tags if "font-weight" in style else wl).append(body)
    return sorted(wl), sorted(tags)


def lab(x):
    return "∞" if x == INF else str(x).replace("-", "−")


def fig_on_page(name):
    return f"<!-- fig:{name} -->\n" + fig_html(name).strip() in page


# =====================================================================================================
print("== Ford's generic algorithm (8.3): random graphs, random tense-edge choices, brute force")
ok = dict(dist=True, inv1=True, inv2=True, tree=True, halt=True, claim34=True)
n_neg = n_pos = 0
for trial in range(900):
    n = random.randint(1, 6)
    G = rand_graph(n, random.choice([0.3, 0.5, 0.7]), -3, 6)
    s = random.randrange(n)
    reach_neg = neg_cycle_reachable(G, s)
    tr = {"no_neg": not has_neg_cycle(G)}
    # without negative cycles every dist(v) is the length of a path, so at most (V-1) * 65 < 400 relaxations for V <= 6
    dist, pred, halted, nrel = FordSSSP(G, s, cap=400, track=tr if not reach_neg else None)
    if reach_neg:
        tr.update(inv1=True, inv2=True, invtree=True)
        _, _, _, _ = FordSSSP(G, s, cap=60, track=tr)   # Claim 1 also holds on the way into a negative cycle
    if halted != (not reach_neg):
        ok["halt"] = False
    if not tr["inv1"]:
        ok["inv1"] = False
    if tr["no_neg"] and not (tr["inv2"] and tr["invtree"]):
        ok["inv2"] = False
    if not reach_neg:
        n_pos += 1
        ref = brute_simple_paths(G, s)
        if dist != ref:
            ok["dist"] = False
        if not pred_paths_ok(G, s, dist, pred, ref):
            ok["tree"] = False
        # Claim 4 directly: with no tense edge, dist(v) <= length of every walk with <= V+2 edges
        bw = brute_walks_at_most(G, s, min(n + 2, 6))
        if any(dist[v] > bw[v] for v in G):
            ok["claim34"] = False
    else:
        n_neg += 1
check(f"FordSSSP halts iff no negative cycle is reachable from s ({n_pos} halting, {n_neg} non-halting graphs)", ok["halt"])
check("Claim 1: every dist(v) is the length of the walk that produced it, starting at s (checked after every relaxation)", ok["inv1"])
check("Claim 2: without negative cycles every such walk is a simple path, and predecessor pointers never form a cycle",
      ok["inv2"])
check("FordSSSP ends with dist = brute-force shortest simple paths", ok["dist"])
check("Claims 3-4: at the end the predecessor pointers form a tree whose paths have length dist(v) = delta(v)",
      ok["tree"] and ok["claim34"])

print("== Shortest-path trees exist (8.1): the fewest-edges construction of the proof")
okspt = True
for trial in range(500):
    n = random.randint(1, 6)
    G = rand_graph(n, 0.5, -2, 4)
    s = random.randrange(n)
    if neg_cycle_reachable(G, s):
        continue
    best = {v: (INF, INF, None) for v in G}   # (length, edges, pred) minimal lexicographically
    best[s] = (0, 0, None)

    def go(u, L, k, onpath, path):
        for v, w in G[u]:
            if v not in onpath:
                cand = (L + w, k + 1)
                if cand < best[v][:2]:
                    best[v] = (L + w, k + 1, u)
                onpath.add(v)
                go(v, L + w, k + 1, onpath, path)
                onpath.discard(v)

    go(s, 0, 0, {s}, [s])
    pred = {v: best[v][2] for v in G}
    ref = {v: best[v][0] for v in G}
    if not pred_paths_ok(G, s, ref, pred, brute_simple_paths(G, s)):
        okspt = False
check("choosing, for each v, the predecessor on a fewest-edge shortest path always gives a shortest-path tree "
      "(random graphs with negative edges and zero-weight cycles)", okspt)

print("== Negative edges (8.2)")
okexist = True
for trial in range(250):
    n = random.randint(2, 5)
    G = rand_graph(n, 0.5, -3, 3)
    s = random.randrange(n)
    cyc = [(c, tot) for c, tot in simple_cycles(G) if tot < 0]
    R = tclosure(G)
    lo = minplus_walks(G, s, n - 1)
    hi = minplus_walks(G, s, 200)
    for t in G:
        touches = any(any(x in R[s] and t in R[x] for x in c) for c, _ in cyc)
        exists = t in R[s] and not touches
        # a shortest walk exists iff taking many more edges never helps
        if exists != (lo[t] < INF and hi[t] == lo[t]):
            okexist = False
check("a shortest walk s->t exists iff s reaches t and no s-t walk touches a negative cycle (min-plus walks with "
      "V-1 vs 200 edges, all cycles enumerated)", okexist)
NC = wgraph("sabcdt", [("s", "a", 5), ("a", "b", 2), ("b", "c", -8), ("c", "t", 3), ("c", "d", 1), ("d", "a", 4)])
cyc_w = [tot for c, tot in simple_cycles(NC)]
w_more = [minplus_walks(NC, "s", L)["t"] for L in (4, 8, 12, 16)]
check("Figure 8.3: one cycle a b c d a of weight 2 - 8 + 1 + 4 = -1; the walk to t gets 1 shorter per lap",
      cyc_w == [-1] and w_more == [2, 1, 0, -1] and onpage("2 − 8 + 1 + 4 = −1", fig_html("a08-negative")))
TRI = undirected("suv", [("s", "u", 1), ("s", "v", 1), ("u", "v", -1)])


def simple_paths_all(G, s, t):
    out = []

    def go(u, path):
        if u == t:
            out.append(list(path))
            return
        for v, w in G[u]:
            if v not in path:
                path.append(v)
                go(v, path)
                path.pop()

    go(s, [s])
    return out


sp_u = sorted((walk_weight(TRI, P), P) for P in simple_paths_all(TRI, "s", "u"))
sp_v = sorted((walk_weight(TRI, P), P) for P in simple_paths_all(TRI, "s", "v"))
union = {frozenset(e) for P in (sp_u[0][1], sp_v[0][1]) for e in zip(P, P[1:])}
check("Figure 8.4: unique shortest undirected paths s v u and s u v, both of length 0; together they use all three "
      "edges (no tree); the subpath s v has length 1 > 0",
      sp_u[0] == (0, ["s", "v", "u"]) and sp_u[1][0] > 0 and sp_v[0] == (0, ["s", "u", "v"]) and sp_v[1][0] > 0
      and len(union) == 3 and walk_weight(TRI, ["s", "v"]) == 1 and has_neg_cycle(TRI)
      and min(t for c, t in simple_cycles(TRI) if len(c) == 2) == -2)
Z = wgraph("sat", [("s", "a", 1), ("a", "s", -1), ("a", "t", 2)])
check("footnote 2 (p. 275): with a zero-weight cycle, the non-simple walk s a s a t is as short as the path s a t",
      walk_weight(Z, list("sasat")) == walk_weight(Z, list("sat")) == minplus_walks(Z, "s", 50)["t"] == 3)
C1 = wgraph("sat", [("s", "t", 1), ("s", "a", -2), ("a", "t", 2)])
C2 = wgraph("sat", [("s", "t", 3), ("s", "a", 0), ("a", "t", 4)])
check("adding a constant changes the answer: s->t 1 vs s a t 0; after +2: s->t 3 beats s a t 4",
      brute_simple_paths(C1, "s")["t"] == 0 and walk_weight(C1, list("sat")) == 0
      and brute_simple_paths(C2, "s")["t"] == 3 and walk_weight(C2, list("sat")) == 4
      and onpage("add 2 to every weight and $s\\to t$ (now 3) beats $s\\,a\\,t$ (now 4)"))
# a negative cycle s can reach but that cannot reach t leaves delta(t) finite, yet BellmanFord/Ford see it
NR = wgraph("sabt", [("s", "t", 2), ("s", "a", 1), ("a", "b", -3), ("b", "a", 1)])
check("a negative cycle reachable from s that cannot reach t: delta(t) = 2 is finite, but Bellman-Ford reports a "
      "negative cycle and Ford does not halt",
      minplus_walks(NR, "s", 3)["t"] == minplus_walks(NR, "s", 200)["t"] == 2
      and BellmanFord(NR, "s")[2] == "Negative cycle!" and FordSSSP(NR, "s", cap=500)[2] is False)
okun = True
for trial in range(300):
    n = random.randint(2, 6)
    G = rand_graph(n, 0.5, -3, 4)
    s = random.randrange(n)
    if not neg_cycle_reachable(G, s):
        continue
    # unreachable part: add an isolated negative 2-cycle that s cannot reach
    G2 = {v: list(G[v]) for v in G}
    G2["x"] = [("y", -5)]
    G2["y"] = [("x", 1)]
    if BellmanFord(G2, "x" if False else s)[2] != "Negative cycle!":
        okun = False
okun2 = True
for trial in range(300):
    n = random.randint(2, 6)
    G = rand_graph(n, 0.5, 0, 6)
    s = random.randrange(n)
    G2 = {v: list(G[v]) for v in G}
    G2["x"] = [("y", -5)]
    G2["y"] = [("x", 1)]
    d2, _, r2 = BellmanFord(G2, s)
    if r2 is not None or any(d2[v] != brute_simple_paths(G, s)[v] for v in G) or d2["x"] != INF:
        okun2 = False
check("a negative cycle that s cannot reach is not reported and changes no distance (Bellman-Ford)", okun2 and okun)

print("== Shortest-path tree vs minimum spanning tree (8.1 figure)")
FAN = [("s", "a", 5), ("s", "b", 6), ("s", "c", 7), ("s", "d", 8), ("a", "b", 2), ("b", "c", 3), ("c", "d", 4)]
FG = undirected("sabcd", FAN)
fd = brute_simple_paths(FG, "s")


def kruskal(V, E):
    par = {v: v for v in V}

    def f(x):
        while par[x] != x:
            x = par[x]
        return x

    T = []
    for u, v, w in sorted(E, key=lambda e: e[2]):
        if f(u) != f(v):
            par[f(u)] = f(v)
            T.append((u, v, w))
    return T


T = kruskal("sabcd", FAN)
fdist, fpred, _ = Dijkstra(FG, "s")
spt = {frozenset((fpred[v], v)) for v in "abcd"}
mst = {frozenset((u, v)) for u, v, w in T}
check("fan graph: MST {sa, ab, bc, cd} of weight 14; shortest-path tree = the four spokes, weight 26; distances "
      "5 6 7 8; MST path s a b c d has length 14; the trees share only sa",
      mst == {frozenset(e) for e in ["sa", "ab", "bc", "cd"]} and sum(w for *_, w in T) == 14
      and spt == {frozenset(e) for e in ["sa", "sb", "sc", "sd"]}
      and sum(w for u, v, w in FAN if frozenset((u, v)) in spt) == 26
      and fd == {"s": 0, "a": 5, "b": 6, "c": 7, "d": 8} and walk_weight(FG, list("sabcd")) == 14
      and spt & mst == {frozenset("sa")})
wl, tags = fig_labels("a08-sp-tree")
check("figure a08-sp-tree: weight labels twice each, distance tags 0 5 6 7 8, totals 14 and 26 in the text",
      wl == sorted([str(w) for *_, w in FAN] * 2) and tags == sorted(["0", "5", "6", "7", "8"])
      and "weight 14" in fig_html("a08-sp-tree") and "weight 26" in fig_html("a08-sp-tree"))
oklight = True
for trial in range(400):
    n = random.randint(2, 7)
    V = list(range(n))
    ws = random.sample(range(1, 60), n * (n - 1) // 2)
    E = [(u, v, ws.pop()) for u in V for v in V if u < v and random.random() < 0.6]
    G = undirected(V, E)
    if len(reach_from(G, 0)) < n:
        continue
    at_s = [(w, u if v == 0 else v) for u, v, w in E if 0 in (u, v)]
    w0, x = min(at_s)
    paths = [P for P in simple_paths_all(G, 0, x)]
    best = min(walk_weight(G, P) for P in paths)
    only = [P for P in paths if walk_weight(G, P) == best]
    if only != [[0, x]] or not any({u, v} == {0, x} for u, v, w in kruskal(V, E)):
        oklight = False
check("distinct positive weights: the lightest edge at s is the unique shortest path to its endpoint, and it is in "
      "the MST (so SPT and MST always share it)", oklight)

print("== Relaxation figure")
wl, tags = fig_labels("a08-relax")
check("a08-relax: 3 + 4 = 7 < 9 is tense; after Relax dist(v) = 7; labels 2, 4 (twice); tags 0 7 3 9 | 0 7 3 7",
      3 + 4 < 9 and wl == sorted(["2", "4"] * 2) and tags == sorted(["0", "7", "3", "9", "0", "7", "3", "7"])
      and onpage("3 + 4 = 7 &lt; 9 = <i>dist</i>(<i>v</i>)", fig_html("a08-relax")))

print("== Breadth-first search (8.4)")
ok = dict(dist=True, same=True, lemma=True, once=True, marks=True, tree=True)
for trial in range(700):
    n = random.randint(1, 8)
    G = rand_graph(n, random.choice([0.2, 0.4, 0.6]), 1, 1)
    if random.random() < 0.3:
        H = {v: list(G[v]) for v in G}
        for u, v, w in edges_of(G):
            if (u, 1) not in H[v]:
                H[v].append((u, 1))
        G = H
    s = random.randrange(n)
    d1, p1 = BFS(G, s)
    d2, p2, pulled, snaps, pushes, pulls, comps, halted = BFSWithToken(G, s)
    d3, p3 = BFS_marks(G, s)
    ref = brute_simple_paths(unit(G), s)
    if d1 != ref:
        ok["dist"] = False
    if (d1, p1) != (d2, p2):
        ok["same"] = False
    if (d1, p1) != (d3, p3):
        ok["marks"] = False
    if not pred_paths_ok(unit(G), s, d1, p1, ref):
        ok["tree"] = False
    for i, (dd, Q) in enumerate(snaps, start=1):
        for v in G:
            if not (dd[v] == INF or dd[v] <= i) or ((v in Q) != (dd[v] == i)):
                ok["lemma"] = False
    if any(x > 1 for x in pushes.values()) or any(x > 1 for x in pulls.values()) or any(
            x > 1 for x in comps.values()):
        ok["once"] = False
check("BFS = brute-force fewest-edge distances (700 random directed and undirected graphs)", ok["dist"])
check("BFSWithToken pushes, pulls and outputs exactly what BFS does", ok["same"])
check("Lemma 8.1 at the end of every phase: dist(v) = inf or <= i, and v is queued iff dist(v) = i", ok["lemma"])
check("each vertex pushed at most once, pulled at most once, each edge tested at most once", ok["once"])
check("the test 'dist(v) = inf' gives the same distances and predecessors", ok["marks"])
check("BFS predecessor pointers form a tree of shortest paths", ok["tree"])
BV = "sabcdefgh"
BE = "sb sd as cs ba bc dc dg cg cf ae eh eb fe fb gf hf hg".split()
BG = wgraph(BV, [(e[0], e[1], 1) for e in BE])
BG["b"] = [("c", 1), ("a", 1)]         # b lists c before a (the order of the book's run)
bd, bp, bpulled, bsnaps, bpush, bpull, bcomp, _ = BFSWithToken(BG, "s")
blog = []
BFSWithToken(BG, "s", log=blog)
dc_tense = [t for kind, e, t in [x for x in blog if x[0] == "cmp"] if e[:2] == ("d", "c")]
check("book's Figure 8.6: pulled s ✠ b d ✠ c a g ✠ f e ✠ h (the loop stops with only the token left: no trailing "
      "✠ ✠); dist s0 b1 d1 a2 c2 g2 e3 f3 h4; queues b d | c a g | f e | h",
      " ".join(bpulled) == "s ✠ b d ✠ c a g ✠ f e ✠ h"
      and bd == dict(s=0, a=2, b=1, c=2, d=1, e=3, f=3, g=2, h=4)
      and [" ".join(Q) for _, Q in bsnaps] == ["b d", "c a g", "f e", "h"]
      and bp == dict(s=None, a="b", b="s", c="b", d="s", e="a", f="c", g="d", h="e"))
check("book's run: d->c is not tense when d is scanned; 18 edges, each tested once; every vertex pushed and pulled once",
      dc_tense == [False] and len(BE) == 18 and sorted(bcomp.values()) == [1] * 18
      and set(bpush.values()) == {1} and set(bpull.values()) == {1}
      and onpage("each of the 18 edges was tested once"))
h = fig_html("a08-bfs")
check("figure a08-bfs: pulled sequence, phase queues and BFS-tree edges as computed",
      "s ✠ b d ✠ c a g ✠ f e ✠ h" in h and all(f">{' '.join(Q)}<" in h for _, Q in bsnaps)
      and fig_on_page("a08-bfs"))
check("figure a08-bfs caption: no edge skips a layer forward (dist(v) <= dist(u) + 1), some go back two layers",
      all(bd[v] <= bd[u] + 1 for u, v, w in edges_of(BG)) and any(bd[u] - bd[v] >= 2 for u, v, w in edges_of(BG)))
BW = wgraph("sat", [("s", "t", 10), ("s", "a", 1), ("a", "t", 1)])
check("BFS trap: s->t 10 vs s a t of weights 1, 1: BFS picks the one-edge path, the shortest path has length 2",
      BFS(BW, "s")[1]["t"] == "s" and Dijkstra(BW, "s")[0]["t"] == 2)

print("== Dags (8.5)")
ok = dict(three=True, ref=True, tree=True, identity=True)
for trial in range(600):
    n = random.randint(1, 8)
    G = rand_dag(n, random.choice([0.3, 0.5, 0.8]), -6, 8)
    s = random.randrange(n)
    for rep in range(2):
        order = topo_order(G, random)
        a = DagSSSP_dp(G, s, order)
        b, pb = DagSSSP_ford(G, s, order)
        c, pc = PushDagSSSP(G, s, order)
        ref = brute_simple_paths(G, s)
        if not (a == b == c):
            ok["three"] = False
        if a != ref:
            ok["ref"] = False
        if not (pred_paths_ok(G, s, b, pb, ref) and pred_paths_ok(G, s, c, pc, ref)):
            ok["tree"] = False
for trial in range(400):
    n = random.randint(1, 6)
    G = rand_graph(n, 0.5, -2, 6)
    s = random.randrange(n)
    if has_neg_cycle(G):
        continue
    d = brute_simple_paths(G, s)
    R = rev(G)
    for v in G:
        rhs = 0 if v == s else min([d[u] + w for u, w in R[v]] or [INF])
        if d[v] != rhs:
            ok["identity"] = False
NS = wgraph("sa", [("s", "a", -1), ("a", "s", -1)])
# with negative cycles (delta = -inf allowed): the identity fails exactly at s, and only when delta(s) = -inf
okid_s = okid_other = True
for trial in range(400):
    n = random.randint(1, 5)
    G = rand_graph(n, 0.5, -4, 5)
    s = random.randrange(n)
    Rs, TC = reach_from(G, s), tclosure(G)
    doomed = set()
    for cyc, tot in simple_cycles(G):
        if tot < 0 and cyc[0] in Rs:
            doomed |= TC[cyc[0]]
    d = brute_simple_paths(G, s)
    dl = {v: (-INF if v in doomed else d[v]) for v in G}
    R = rev(G)
    for v in G:
        rhs = 0 if v == s else min([dl[u] + w for u, w in R[v]] or [INF])
        if v == s and (dl[v] != rhs) != (dl[s] == -INF):
            okid_s = False
        if v != s and dl[v] != rhs:
            okid_other = False
check("with negative cycles (delta = -inf allowed, -inf + w = -inf) the dag identity holds at every v != s and fails "
      "at s exactly when delta(s) = -inf (the Sources' correction of p. 282)", okid_s and okid_other
      and onpage("it fails at $s$ whenever $\\delta(s) = -\\infty$, for instance when $s$ lies on a negative cycle"))
check("DagSSSP (DP form), DagSSSP (Ford form) and PushDagSSSP agree, for random topological orders", ok["three"])
check("... and equal brute-force shortest paths in random dags with negative weights", ok["ref"])
check("... and their predecessor pointers form shortest-path trees", ok["tree"])
check("the identity delta(v) = min over u->v of delta(u) + w holds in random graphs without negative cycles; with a "
      "negative cycle through s, delta(s) < 0", ok["identity"] and minplus_walks(NS, "s", 2)["s"] == -2)
DN = list("sabcdef")
DE = [("s", "a", 3), ("s", "b", 8), ("s", "c", 7), ("a", "b", 6), ("a", "d", 12), ("b", "c", -2), ("b", "d", 5),
      ("b", "e", 0), ("c", "e", 10), ("d", "e", 1), ("d", "f", -3), ("e", "f", 1)]
DG = wgraph(DN, DE)
dd = DagSSSP_dp(DG, "s", DN)
ptrace = []
pd, pp = PushDagSSSP(DG, "s", DN, ptrace)
vals_d = [x for (u, v, x) in ptrace if v == "d"]
vals_f = [x for (u, v, x) in ptrace if v == "f"]
terms = []
RD = rev(DG)
for v in DN[1:]:
    ts = [f"{dd[u]} + {w}" if w >= 0 else f"{dd[u]} - {-w}" for u, w in sorted(RD[v], key=lambda x: DN.index(x[0]))]
    terms.append((v, ts))
expect = ", ".join(
    f"$\\delta({v}) = " + (f"{ts[0]} = {dd[v]}$" if len(ts) == 1 else "\\min\\{" + ",\\ ".join(ts) + f"\\}} = {dd[v]}$")
    for v, ts in terms)
check("book's dag (Figures 8.9/8.10): delta = 0 3 8 6 13 8 9; the page's min-expressions are the in-edges in order",
      [dd[v] for v in DN] == [0, 3, 8, 6, 13, 8, 9] and pd == dd
      and onpage(expect.replace(", $\\delta(f)", " and $\\delta(f)")), expect)
check("PushDagSSSP sets dist(d) to 15 then 13, dist(f) to 10 then 9; the pull version also passes through 15 and 10",
      vals_d == [15, 13] and vals_f == [10, 9] and onpage("scanning $a$ sets $\\mathit{dist}(d) = 15$")
      and "to 15 before lowering it to 13" in fig_html("a08-dag") and "to 10 before lowering it to 9" in fig_html("a08-dag"))
wl, tags = fig_labels("a08-dag")
hd = fig_html("a08-dag")
boxes = re.findall(r'<text [^>]*>(\d+)</text>', hd.split('fill-opacity="0.1"', 1)[1]) if 'fill-opacity="0.1"' in hd else []
check("figure a08-dag: the 12 edge weights and the 7 boxed distances",
      wl[:] == sorted([lab(w) for *_, w in DE] + [lab(dd[v]) for v in DN]) and fig_on_page("a08-dag"),
      f"{wl}")

print("== Dijkstra (8.6)")
ok = dict(ref=True, l83=True, l84=True, ops=True, extract=True, inv=True, nonneg=True, late=True, tree=True)
for trial in range(900):
    n = random.randint(1, 8)
    G = rand_graph(n, random.choice([0.2, 0.4, 0.7]), 0, 9)
    s = random.randrange(n)
    inv = {"ok": True}
    tr = []
    d, p, info = Dijkstra(G, s, trace=tr, invariant=inv)
    ref = brute_simple_paths(G, s)
    if d != ref:
        ok["ref"] = False
    if not pred_paths_ok(G, s, d, p, ref):
        ok["tree"] = False
    if any(a > b for a, b in zip(info["d"], info["d"][1:])):
        ok["l83"] = False
    if any(x > 1 for x in info["extracted"].values()):
        ok["l84"] = False
    E = len(edges_of(G))
    if not (info["ops"]["Insert"] <= n and info["ops"]["ExtractMin"] <= n and info["ops"]["DecreaseKey"] <= E
            and info["relax"] <= E):
        ok["ops"] = False
    if any(du != ref[u] for u, du, _, _ in tr):
        ok["extract"] = False        # distance final at extraction: early stop at t is safe
    if not inv["ok"]:
        ok["inv"] = False
    li = {}
    dn, pn = NonnegativeDijkstra(G, s, li)
    if dn != ref or not pred_paths_ok(G, s, dn, pn, ref):
        ok["nonneg"] = False
    if li["late"] != 0:
        ok["late"] = False
check("Dijkstra = brute force on 900 random graphs with non-negative (incl. zero) weights; pred is a shortest-path tree",
      ok["ref"] and ok["tree"])
check("Lemma 8.3: extracted values non-decreasing", ok["l83"])
check("Lemma 8.4: every vertex extracted at most once", ok["l84"])
check("at most V Insert, V ExtractMin, E DecreaseKey and E relaxations", ok["ops"])
check("with non-negative weights, dist(u) is final when u is extracted (so the search may stop at t)", ok["extract"])
check("invariant: after every scan, the tail of every tense edge is in the priority queue", ok["inv"])
check("NonnegativeDijkstra = Dijkstra with non-negative weights, and never relaxes into an extracted vertex",
      ok["nonneg"] and ok["late"])
ok = dict(ref=True, inv=True, wrong=0, total=0, nohalt=True)
for trial in range(900):
    n = random.randint(2, 7)
    G = rand_graph(n, 0.45, -4, 8)
    s = random.randrange(n)
    reach_neg = neg_cycle_reachable(G, s)
    inv = {"ok": True}
    d, p, info = Dijkstra(G, s, cap=4000, invariant=inv)
    if reach_neg:
        if info["halted"]:
            ok["nohalt"] = False
        continue
    ref = brute_simple_paths(G, s)
    if d != ref or not info["halted"] or not pred_paths_ok(G, s, d, p, ref):
        ok["ref"] = False
    if not inv["ok"]:
        ok["inv"] = False
    if any(w < 0 for *_, w in edges_of(G)):
        ok["total"] += 1
        if NonnegativeDijkstra(G, s)[0] != ref:
            ok["wrong"] += 1
check("book's Dijkstra is correct with negative edges when no negative cycle is reachable, and never halts when one is",
      ok["ref"] and ok["nohalt"])
check("the tense-edge invariant also holds with negative edges", ok["inv"])
check(f"NonnegativeDijkstra is wrong on {ok['wrong']} of {ok['total']} random graphs with negative edges (no "
      "negative cycles)", ok["wrong"] > 0)
IV = wgraph("sab", [("s", "a", 1), ("s", "b", 5), ("b", "a", 1)])
tr = []
Dijkstra(IV, "s", trace=tr)
after_s = tr[0][3]
check("the converse of the invariant fails: after extracting s, b is in the queue but b->a (5 + 1 > 1) is not tense",
      "b" in after_s and not is_tense({"s": 0, "a": 1, "b": 5}, "b", "a", 1))
JV = list("sabcdt")
JE = [("s", "a", 2), ("s", "b", 5), ("s", "c", 9), ("a", "c", 6), ("a", "d", 9), ("b", "c", 1), ("b", "d", 3),
      ("c", "t", 9), ("d", "c", 3), ("d", "t", 1)]
JG = wgraph(JV, JE)
tr = []
jd, jp, jinfo = Dijkstra(JG, "s", trace=tr)


def row_of(step, u, du, rel, pq):
    ins = [(v, jd_at[v]) for (_, v, k) in rel if k == "Insert"]
    dec = [(v, jd_at[v]) for (_, v, k) in rel if k == "DecreaseKey"]
    return ins, dec


rows = []
cur = {"s": 0}
keys_c = [9]
for k, (u, du, rel, pq) in enumerate(tr, start=1):
    rows.append((u, du, [(v, kind, pq.get(v)) for (_, v, kind) in rel], pq))
expect_rows = [
    "| 0 | — | Insert $s$ with key 0 | $s{:}\\,0$ |",
    "| 1 | $s$, 0 | Insert $a$ 2, $b$ 5, $c$ 9 | $a{:}\\,2$, $b{:}\\,5$, $c{:}\\,9$ |",
    "| 2 | $a$, 2 | DecreaseKey $c$ to 8; Insert $d$ 11 | $b{:}\\,5$, $c{:}\\,8$, $d{:}\\,11$ |",
    "| 3 | $b$, 5 | DecreaseKey $c$ to 6 and $d$ to 8 | $c{:}\\,6$, $d{:}\\,8$ |",
    "| 4 | $c$, 6 | Insert $t$ 15 | $d{:}\\,8$, $t{:}\\,15$ |",
    "| 5 | $d$, 8 | $d\\to c$ is not tense ($8 + 3 > 6$); DecreaseKey $t$ to 9 | $t{:}\\,9$ |",
    "| 6 | $t$, 9 | — | empty |",
]
recomputed = [[(u, du, [(v, kind) for v, kind, _ in rel], sorted(pq.items(), key=lambda x: x[1]))]
              for u, du, rel, pq in rows]
want = [
    [("s", 0, [("a", "Insert"), ("b", "Insert"), ("c", "Insert")], [("a", 2), ("b", 5), ("c", 9)])],
    [("a", 2, [("c", "DecreaseKey"), ("d", "Insert")], [("b", 5), ("c", 8), ("d", 11)])],
    [("b", 5, [("c", "DecreaseKey"), ("d", "DecreaseKey")], [("c", 6), ("d", 8)])],
    [("c", 6, [("t", "Insert")], [("d", 8), ("t", 15)])],
    [("d", 8, [("t", "DecreaseKey")], [("t", 9)])],
    [("t", 9, [], [])],
]
check("Dijkstra example: the trace (extractions, Insert/DecreaseKey, queue contents) matches the page's table",
      recomputed == want and all(("> " + r) in page for r in expect_rows)
      and not is_tense(jd, "d", "c", 3) and 8 + 3 > 6)
check("Dijkstra example: final distances s0 a2 b5 c6 d8 t9, tree a<-s b<-s c<-b d<-b t<-d; 6 Insert, 6 ExtractMin, "
      "4 DecreaseKey; keys of c 9 -> 8 -> 6",
      jd == dict(s=0, a=2, b=5, c=6, d=8, t=9) and jp == dict(s=None, a="s", b="s", c="b", d="b", t="d")
      and jinfo["ops"] == {"Insert": 6, "ExtractMin": 6, "DecreaseKey": 4} and jd == brute_simple_paths(JG, "s")
      and onpage("6 Insert, 6 ExtractMin and 4 DecreaseKey") and onpage("$9\\to 8\\to 6$")
      and onpage("The extracted keys $0, 2, 5, 6, 8, 9$ increase"))
wl, tags = fig_labels("a08-dijkstra")
check("figure a08-dijkstra: the 10 weights and the 6 distances", wl == sorted(str(w) for *_, w in JE)
      and tags == sorted(lab(jd[v]) for v in JV) and fig_on_page("a08-dijkstra"))
CE = wgraph("sabt", [("s", "a", 2), ("s", "b", 3), ("a", "t", 2), ("b", "a", -2)])
li = {}
nd, npd = NonnegativeDijkstra(CE, "s", li)
sd, spd = NonnegativeDijkstra_skip(CE, "s")
tr = []
bd2, bp2, binfo = Dijkstra(CE, "s", trace=tr)
check("counterexample: NonnegativeDijkstra ends with dist(a) = 1, dist(t) = 4 and a->t still tense; the skipping "
      "variant with dist(a) = 2, dist(t) = 4; the book's Dijkstra re-inserts a and gets dist(t) = 3 = delta(t)",
      nd["a"] == 1 and nd["t"] == 4 and is_tense(nd, "a", "t", 2) and li["late"] == 1
      and sd["a"] == 2 and sd["t"] == 4 and bd2 == brute_simple_paths(CE, "s") == dict(s=0, a=1, b=3, t=3)
      and [u for u, *_ in tr] == ["s", "a", "b", "a", "t"] and [x for _, x, *_ in tr][:3] == [0, 2, 3]
      and onpage("with $\\mathit{dist}(a) = 2$ and $\\mathit{dist}(t) = 4$"))
wl, tags = fig_labels("a08-dijkstra-negative")
check("figure a08-dijkstra-negative: weights twice, tags 0 3 1 4 | 0 3 1 3",
      wl == sorted(["2", "3", "−2", "2"] * 2) and tags == sorted(["0", "3", "1", "4", "0", "3", "1", "3"]))
N = wgraph("sabcdef", [("s", "a", 3), ("s", "b", 10), ("s", "c", 4), ("a", "b", 6), ("a", "d", 2), ("b", "d", -7),
                       ("b", "f", -5), ("c", "b", 8), ("c", "f", 3), ("f", "d", -3), ("f", "e", 1), ("e", "d", -5)])
tr = []
nd_, np_, ninfo = Dijkstra(N, "s", trace=tr)
relcount = {}
for u, du, rel, pq in tr:
    for (a_, b_, k) in rel:
        relcount[(a_, b_)] = relcount.get((a_, b_), 0) + 1


def dijkstra_ties(G, s):
    """Re-run the book's Dijkstra, reporting whether any ExtractMin had a tie for the minimum key."""
    dist, pred = InitSSSP(G, s)
    pq = {s: 0}
    ties = False
    while pq:
        m = min(pq.values())
        c = [v for v in pq if pq[v] == m]
        ties |= len(c) > 1
        u = c[0]
        del pq[u]
        for v, w in G[u]:
            if is_tense(dist, u, v, w):
                dist[v] = dist[u] + w
                pred[v] = u
                pq[v] = dist[v]
    return ties


d_vals = [du for u, du, *_ in tr if u == "d"]
check("book's Figure 8.15 graph: Dijkstra extracts d six times with dist 5 4 3 2 1 0, and relaxes e->d, f->e, f->d "
      "twice each (all other edges at most once); no ExtractMin ever has a tie",
      ninfo["extracted"]["d"] == 6 and d_vals == [5, 4, 3, 2, 1, 0]
      and relcount[("e", "d")] == relcount[("f", "e")] == relcount[("f", "d")] == 2
      and all(c == 1 for e, c in relcount.items() if e not in {("e", "d"), ("f", "e"), ("f", "d")})
      and not dijkstra_ties(N, "s") and onpage("$\\mathit{dist}(d) = 5, 4, 3, 2, 1, 0$"))


def shier_witzgall(k):
    V = ["x0"]
    E = []
    for j in range(k, 0, -1):          # j-th triangle from the right
        i = k - j
        V += [f"y{i + 1}", f"x{i + 1}"]
        E += [(f"x{i}", f"y{i + 1}", 0), (f"y{i + 1}", f"x{i + 1}", -2 ** j), (f"x{i}", f"x{i + 1}", -2 ** (j - 1))]
    return wgraph(V, E)


oksw = True
for k in range(1, 13):
    G = shier_witzgall(k)
    d, p, info = Dijkstra(G, "x0")
    if len(G) != 2 * k + 1 or info["relax"] != 3 * (2 ** k - 1):
        oksw = False
    if k <= 6 and d != brute_simple_paths(G, "x0"):
        oksw = False
    if any(p[f"x{i}"] != f"y{i}" for i in range(1, k + 1)):
        oksw = False
ratio = [3 * (2 ** k - 1) / 2 ** ((2 * k + 1) / 2) for k in (10, 20, 30)]
check("Shier-Witzgall graphs: V = 2k+1, Dijkstra makes exactly 3(2^k - 1) relaxations (k = 1..12), the shortest-path "
      "tree is the zig-zag through the apexes, and 3(2^k-1)/2^(V/2) -> 3/sqrt(2): Theta(2^(V/2))",
      oksw and abs(ratio[-1] - 3 / math.sqrt(2)) < 1e-6 and onpage("$3(2^k - 1) = \\Theta(2^{V/2})$"))
UND_ok = True
for trial in range(200):
    n = random.randint(1, 6)
    V = list(range(n))
    E = [(u, v, random.randint(0, 9)) for u in V for v in V if u < v and random.random() < 0.5]
    G = undirected(V, E)
    if Dijkstra(G, 0)[0] != brute_simple_paths(G, 0):
        UND_ok = False
check("undirected graphs with non-negative weights: Dijkstra on the doubled graph = brute-force undirected paths",
      UND_ok)

print("== Bellman-Ford (8.7)")
ok = dict(detect=True, ref=True, tree=True, l86=True, rounds=True, nohalt=True, anywhere=True)
for trial in range(700):
    n = random.randint(1, 6)
    G = rand_graph(n, random.choice([0.3, 0.5]), -4, 7)
    s = random.randrange(n)
    reach_neg = neg_cycle_reachable(G, s)
    rounds = []
    d, p, res = BellmanFord(G, s, rounds)
    if (res == "Negative cycle!") != reach_neg:
        ok["detect"] = False
    G2 = {v: list(G[v]) for v in G}
    G2["new"] = [(v, 0) for v in G]
    if (BellmanFord(G2, "new")[2] == "Negative cycle!") != has_neg_cycle(G):
        ok["anywhere"] = False
    for i, row in enumerate(rounds, start=1):
        bw = brute_walks_at_most(G, s, i)
        if any(row[v] > bw[v] for v in G):
            ok["l86"] = False
    dw, pw, nr, halted = BellmanFord_while(G, s)
    if reach_neg:
        if halted:
            ok["nohalt"] = False
        continue
    ref = brute_simple_paths(G, s)
    if d != ref or dw != ref:
        ok["ref"] = False
    if not (pred_paths_ok(G, s, d, p, ref) and pred_paths_ok(G, s, dw, pw, ref)):
        ok["tree"] = False
    if nr > max(n - 1, 0):
        ok["rounds"] = False
check("BellmanFord returns 'Negative cycle!' iff a negative cycle is reachable from s (cycles enumerated)", ok["detect"])
check("with a new source joined to every vertex by 0-weight edges it detects every negative cycle", ok["anywhere"])
check("otherwise both forms end with brute-force distances and a shortest-path tree", ok["ref"] and ok["tree"])
check("Lemma 8.6: after i rounds dist(v) <= dist_{<=i}(v) (all walks with <= i edges enumerated)", ok["l86"])
check("the while-form makes at most V-1 rounds of relaxations without negative cycles, and never halts with one",
      ok["rounds"] and ok["nohalt"])
ok = dict(dp=True, dp2=True, dp3=True, fin=True)
for trial in range(500):
    n = random.randint(1, 6)
    G = rand_graph(n, 0.5, -4, 7)
    s = random.randrange(n)
    T1, T2, T3 = BellmanFordDP(G, s), BellmanFordDP2(G, s), BellmanFordDP3(G, s)
    for i in range(n):
        bw = brute_walks_at_most(G, s, i)
        if T1[i] != bw:
            ok["dp"] = False
        if T2[i] != bw:
            ok["dp2"] = False
        if any(T3[i][v] > bw[v] for v in G):
            ok["dp3"] = False
    if not neg_cycle_reachable(G, s):
        ref = brute_simple_paths(G, s)
        if T3[n - 1] != ref or BellmanFordFinal(G, s) != ref or T1[n - 1] != ref:
            ok["fin"] = False
check("BellmanFordDP computes dist_{<=i}(v) exactly (brute-force walks), row by row", ok["dp"])
check("with the edge loop outside the vertex loop (BellmanFordDP2) still exactly", ok["dp2"])
check("reading row i (BellmanFordDP3): dist[i, v] <= dist_{<=i}(v)", ok["dp3"])
check("without reachable negative cycles the last row of every version and BellmanFordFinal are the distances",
      ok["fin"])
rows = BellmanFordDP(N, "s")
tbl = []
for i, row in enumerate(rows):
    tbl.append("> | " + " | ".join([str(i)] + [("$\\infty$" if row[v] == INF else str(row[v])) for v in "sabcdef"]) + " |")
check("the dist_{<=i} table for the book's graph (rows 0..6) is the page's table; it settles at i = 5",
      all(r in page for r in tbl) and rows[4] != rows[5] == rows[6] and rows[5]["d"] == 0
      and walk_weight(N, list("sabfed")) == 0 and onpage("3 + 6 − 5 + 1 − 5 = 0", fig_html("a08-bellman-ford")),
      "\n".join(tbl))
NREF = ref = brute_simple_paths(N, "s")
NE_book = [("s", "a", 3), ("s", "b", 10), ("s", "c", 4), ("a", "b", 6), ("a", "d", 2), ("b", "d", -7), ("b", "f", -5),
           ("c", "b", 8), ("c", "f", 3), ("f", "d", -3), ("f", "e", 1), ("e", "d", -5)]
assert sorted(NE_book) == sorted(edges_of(N))
rr = []
d, p, res = BellmanFord(N, "s", rr, E=NE_book)
NE_late = [e for e in NE_book if e[:2] != ("e", "d")]
NE_late.insert(NE_late.index(("f", "d", -3)), ("e", "d", -5))
rr2 = []
d2_, p2_, res2_ = BellmanFord(N, "s", rr2, E=NE_late)
order_txt = ", ".join(f"${u}\\to {v}$" for u, v, w in NE_book)
check("in-place BellmanFord, edges in the listed order: every distance after one round; with e->d moved before f->d "
      "and f->e: all but dist(d) = 1 after one round, all after two; no negative cycle either way",
      rr[0] == ref and res is None and d == ref
      and {v for v in N if rr2[0][v] != ref[v]} == {"d"} and rr2[0]["d"] == 1 and rr2[1] == ref and res2_ is None
      and onpage("relaxing the edges in the order " + order_txt))
wl, tags = fig_labels("a08-bellman-ford")
check("figure a08-bellman-ford: 12 weights, 7 distances s0 a3 b9 c4 d0 e5 f4, tree as computed",
      wl == sorted(lab(w) for *_, w in edges_of(N)) and tags == sorted(lab(ref[v]) for v in N)
      and ref == dict(s=0, a=3, b=9, c=4, d=0, e=5, f=4) and p == dict(s=None, a="s", b="a", c="s", d="e", e="f", f="b")
      and fig_on_page("a08-bellman-ford"))

print("== Moore (8.7)")
ok = dict(ref=True, l87=True, once=True, nodup=True, tokens=True, crit=True, examined=True)
maxpulls, attained = 0, False
for trial in range(700):
    n = random.randint(1, 7)
    G = rand_graph(n, random.choice([0.3, 0.5]), -4, 7)
    s = random.randrange(n)
    reach_neg = neg_cycle_reachable(G, s)
    log = []
    d, p, pulled, snaps, pushes, pulls, comps, halted = Moore(G, s, cap_phases=n + 3, log=log)
    tokens = pulled.count(TOKEN)
    # criterion: negative cycle reachable iff the token is pulled a V-th time
    if (tokens >= n) != reach_neg:
        ok["crit"] = False
    if reach_neg:
        if halted:
            ok["tokens"] = False
        continue
    maxpulls = max(maxpulls, tokens - (n - 1))
    attained |= tokens == n - 1 and n > 1
    if not halted or tokens > n - 1:
        ok["tokens"] = False
    ref = brute_simple_paths(G, s)
    if d != ref or not pred_paths_ok(G, s, d, p, ref):
        ok["ref"] = False
    for i, (dd_, Q) in enumerate(snaps, start=1):
        bw = brute_walks_at_most(G, s, i)
        if any(dd_[v] > bw[v] for v in G):
            ok["l87"] = False
        if len(Q) != len(set(Q)):
            ok["nodup"] = False
    # per phase: each vertex pulled at most once; every edge tense at the start of a phase is examined in it
    phase, seen, start_tense = [], set(), None
    E = edges_of(G)
    cur_dist = {v: (0 if v == s else INF) for v in G}
    events = [("phase_start", None, cur_dist)] + log
    for ev in log:
        pass
    i = 0
    dist_now = {v: (0 if v == s else INF) for v in G}
    tense0 = {(u, v, w) for (u, v, w) in E if is_tense(dist_now, u, v, w)}
    pulled_this = []
    examined = set()
    for ev in log:
        if ev[0] == "pull":
            u, dsnap = ev[1], ev[2]
            if u == TOKEN:
                if not tense0 <= examined or len(pulled_this) != len(set(pulled_this)):
                    ok["examined"] = False
                    ok["once"] = False if len(pulled_this) != len(set(pulled_this)) else ok["once"]
                tense0 = {(a, b, w) for (a, b, w) in E if is_tense(dsnap, a, b, w)}
                pulled_this, examined = [], set()
            else:
                pulled_this.append(u)
        else:
            examined.add(ev[1])
check("Moore = brute force when no negative cycle is reachable; predecessor pointers form a shortest-path tree",
      ok["ref"])
check("Lemma 8.7: after i phases dist(v) <= dist_{<=i}(v); the queue never holds a vertex twice",
      ok["l87"] and ok["nodup"])
check("in every phase each vertex is pulled at most once, and every edge tense at the start of a phase is examined "
      "during it", ok["once"] and ok["examined"])
check(f"without negative cycles Moore halts after at most V-1 token pulls (attained on random graphs: {attained}); "
      "with a reachable negative cycle it never halts", ok["tokens"] and maxpulls <= 0 and attained)
check("a negative cycle is reachable iff the token is pulled a V-th time (700 random graphs)", ok["crit"])
okpath = True
for n in range(2, 9):
    P = wgraph(range(n), [(i, i + 1, 1) for i in range(n - 1)])
    d, p, pulled, snaps, *_ = Moore(P, 0)
    dd_, Q = snaps[n - 2]          # snapshot at the (V-1)th token pull
    if not (pulled.count(TOKEN) == n - 1 and any(x != TOKEN for x in Q) and (n - 1) in Q and not neg_cycle_reachable(P, 0)):
        okpath = False
check("book's criterion is off by one: on the path s -> v1 -> ... -> v_{V-1} (V = 2..8) the queue still holds v_{V-1} "
      "right after the (V-1)th token pull, with no negative cycle", okpath)
md, mp, mpulled, *_ = Moore(N, "s")
check("Moore on the book's graph (Figure 8.17): pulls s ✠ a b c ✠ d f ✠ d e ✠ d (no trailing ✠ ✠), the token four "
      "times, and ends with the distances of the figure",
      " ".join(mpulled) == "s ✠ a b c ✠ d f ✠ d e ✠ d" and mpulled.count(TOKEN) == 4 and md == NREF
      and onpage("the token is pulled four times"))

print("== Reductions")
# (1) fewest moves with at most k jumps: BFS in a layered graph vs a level-set simulation
def jump_moves(free, n, i, j):
    steps, jumps = [], []
    for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        a, b = i + di, j + dj
        if 0 <= a < n and 0 <= b < n and free[a][b]:
            steps.append((a, b))
        a2, b2 = i + 2 * di, j + 2 * dj
        if 0 <= a2 < n and 0 <= b2 < n and free[a2][b2] and not free[a][b]:
            jumps.append((a2, b2))
    return steps, jumps


def jump_reduction(free, n, k, s, t):
    H = {}
    for i in range(n):
        for j in range(n):
            if free[i][j]:
                for c in range(k + 1):
                    H[(i, j, c)] = []
    for (i, j, c) in H:
        steps, jumps = jump_moves(free, n, i, j)
        for (a, b) in steps:
            H[(i, j, c)].append(((a, b, c), 1))
        if c < k:
            for (a, b) in jumps:
                H[(i, j, c)].append(((a, b, c + 1), 1))
    d, _ = BFS(H, (s[0], s[1], 0))
    return min(d[(t[0], t[1], c)] for c in range(k + 1)), len(H), len(edges_of(H))


def jump_sim(free, n, k, s, t):
    level = {(s, 0)}
    seen = set(level)
    m = 0
    while level:
        if any(cell == t for cell, c in level):
            return m
        nxt = set()
        for (cell, c) in level:
            steps, jumps = jump_moves(free, n, *cell)
            for x in steps:
                nxt.add((x, c))
            if c < k:
                for x in jumps:
                    nxt.add((x, c + 1))
        level = nxt - seen
        seen |= nxt
        m += 1
    return INF


okj = True
for trial in range(400):
    n = random.randint(1, 5)
    k = random.randint(0, 2)
    free = [[random.random() < 0.65 for _ in range(n)] for _ in range(n)]
    cells = [(i, j) for i in range(n) for j in range(n) if free[i][j]]
    if not cells:
        continue
    s, t = random.choice(cells), random.choice(cells)
    ans, nv, ne = jump_reduction(free, n, k, s, t)
    if ans != jump_sim(free, n, k, s, t) or nv > (k + 1) * n * n or ne > 8 * (k + 1) * n * n:
        okj = False
check("jumps: BFS in H from (s,0), min over (t,c) = fewest moves by direct simulation; at most (k+1)n^2 vertices and "
      "8(k+1)n^2 edges", okj)


# (2) coupon: Dijkstra in two layers vs brute force over walks
def coupon_reduction(G, s, t):
    H = {(v, b): [] for v in G for b in (0, 1)}
    for u, v, w in edges_of(G):
        H[(u, 0)].append(((v, 0), w))
        H[(u, 1)].append(((v, 1), w))
        H[(u, 0)].append(((v, 1), 0))
    d, _, _ = Dijkstra(H, (s, 0))
    return min(d[(t, 0)], d[(t, 1)]), len(H), len(edges_of(H))


def coupon_brute(G, s, t, L):
    best = INF

    def go(u, tot, mx, k):
        nonlocal best
        if u == t:
            best = min(best, tot - mx)
        if k == L:
            return
        for v, w in G[u]:
            go(v, tot + w, max(mx, w), k + 1)

    go(s, 0, 0, 0)
    return best


okc = True
for trial in range(300):
    n = random.randint(1, 5)
    G = rand_graph(n, 0.45, 0, 9)
    s, t = random.randrange(n), random.randrange(n)
    ans, nv, ne = coupon_reduction(G, s, t)
    if ans != coupon_brute(G, s, t, 2 * n - 1) or nv != 2 * n or ne != 3 * len(edges_of(G)):
        okc = False
check("coupon: Dijkstra in H, min over (t,0),(t,1) = brute force over all walks (2V-1 edges); H has 2V vertices, "
      "3E edges", okc)


# (3) at most k edges: DagSSSP in the layered dag
def layered(G, s, k, stay=False):
    H = {(v, i): [] for v in G for i in range(k + 1)}
    for i in range(1, k + 1):
        for u, v, w in edges_of(G):
            H[(u, i - 1)].append(((v, i), w))
        if stay:
            for v in G:
                H[(v, i - 1)].append(((v, i), 0))
    order = [(v, i) for i in range(k + 1) for v in G]
    assert topo_order(H) is not None
    d, p = DagSSSP_ford(H, (s, 0), order)
    return H, d, p


okl = True
for trial in range(400):
    n = random.randint(1, 5)
    G = rand_graph(n, 0.5, -4, 6)
    s, t = random.randrange(n), random.randrange(n)
    k = random.randint(0, 5)
    H, d, _ = layered(G, s, k)
    if min(d[(t, i)] for i in range(k + 1)) != brute_walks_at_most(G, s, k)[t]:
        okl = False
    if len(H) != (k + 1) * n or len(edges_of(H)) != k * len(edges_of(G)):
        okl = False
    H2, d2, _ = layered(G, s, n - 1, stay=True)
    T = BellmanFordDP(G, s)
    if any(d2[(v, i)] != T[i][v] for v in G for i in range(n)):
        okl = False
check("at most k edges: DagSSSP in the layered dag = brute-force walks with <= k edges (negative cycles allowed); "
      "(k+1)V vertices, kE edges; with k = V-1 and 0-weight stay edges it reproduces BellmanFordDP row by row", okl)
LG = wgraph("sabt", [("s", "a", 1), ("s", "b", 4), ("a", "b", 2), ("b", "a", -3), ("a", "t", 5), ("b", "t", 1)])
H, d, p = layered(LG, "s", 3)
path = [("t", 3)]
while path[-1] != ("s", 0):
    path.append(p[path[-1]])
check("figure example: cycle a b a has weight -1; best walk to t with <= 3 edges is s a b t of length 4; with 5 "
      "edges it is 3",
      [tot for c, tot in simple_cycles(LG)] == [-1] and min(d[("t", i)] for i in range(4)) == 4
      and [v for v, i in path[::-1]] == list("sabt") and brute_walks_at_most(LG, "s", 5)["t"] == 3)
wl, tags = fig_labels("a08-layered")
check("figure a08-layered: weights of G and the 16 labels of H (inf for unreachable copies)",
      wl == sorted(lab(w) for *_, w in edges_of(LG)) and tags == sorted(lab(d[x]) for x in H)
      and fig_on_page("a08-layered"))
check("the negative-cycle figure and the relaxation figure are inlined after their markers",
      fig_on_page("a08-negative") and fig_on_page("a08-relax") and fig_on_page("a08-sp-tree")
      and fig_on_page("a08-dijkstra-negative"))

print("== Concept pages")
csp = read(os.path.join(CONCEPTS, "shortest-paths.md"))
CG = wgraph("sabt", [("s", "t", 7), ("s", "a", 2), ("a", "b", 2), ("b", "t", 1)])
outcomes, counts = set(), set()


def all_runs(dist, pred, k):
    T_ = [(u, v, w) for (u, v, w) in edges_of(CG) if is_tense(dist, u, v, w)]
    if not T_:
        outcomes.add((tuple(sorted(dist.items())), pred["t"]))
        counts.add(k)
        return
    for (u, v, w) in T_:
        d2, p2 = dict(dist), dict(pred)
        d2[v] = d2[u] + w
        p2[v] = u
        all_runs(d2, p2, k + 1)


all_runs(*InitSSSP(CG, "s"), 0)
check("shortest-paths example: every run of Ford ends with dist a2 b4 t5, pred(t) = b; runs make 3 or 4 relaxations",
      outcomes == {((("a", 2), ("b", 4), ("s", 0), ("t", 5)), "b")} and counts == {3, 4}
      and BFS(CG, "s")[1]["t"] == "s" and "for 4 in all" in csp and "for 3." in csp)
cbfs = read(os.path.join(CONCEPTS, "breadth-first-search.md"))
grid = [(i, j) for i in range(1, 4) for j in range(1, 4)]
GE = [((i, j), (a, b), 1) for (i, j) in grid for (a, b) in grid if abs(i - a) + abs(j - b) == 1]
GG = wgraph(grid, GE)
gd, gp, gpulled, gsnaps, gpush, gpull, gcomp, _ = BFSWithToken(GG, (1, 1))
phase_sizes = [len(list(g)) for k_, g in itertools.groupby(gpulled, key=lambda x: x == TOKEN) if not k_]
check("breadth-first-search example: 3x3 grid, 12 undirected edges; label i + j - 2; phases pull 1 2 3 2 1; each of "
      "24 directed edges tested once",
      len(GE) == 24 and all(gd[(i, j)] == i + j - 2 for (i, j) in grid) and phase_sizes == [1, 2, 3, 2, 1]
      and sorted(gcomp.values()) == [1] * 24 and "pull 1, 2, 3, 2 and 1 cells" in cbfs)
okrev = okmulti = True
for trial in range(300):
    n = random.randint(1, 7)
    G = rand_graph(n, 0.35, 1, 1)
    t = random.randrange(n)
    dt, _ = BFS(rev(G), t)
    for v in G:
        if dt[v] != brute_simple_paths(G, v)[t]:
            okrev = False
    S = random.sample(range(n), random.randint(1, n))
    G2 = {v: list(G[v]) for v in G}
    G2["new"] = [(x, 1) for x in S]
    dm, _ = BFS(G2, "new")
    for v in G:
        want = min(brute_simple_paths(unit(G), x)[v] for x in S)
        if dm[v] - 1 != want and not (dm[v] == INF and want == INF):
            okmulti = False
check("BFS from t in rev(G) gives the distances to t; a new vertex joined to several starts gives the multi-source "
      "distances plus 1", okrev and okmulti)
cdij = read(os.path.join(CONCEPTS, "dijkstras-algorithm.md"))
DU = undirected("sabt", [("s", "a", 4), ("s", "b", 1), ("b", "a", 2), ("a", "t", 1), ("b", "t", 5)])
tr = []
dud, dup, _ = Dijkstra(DU, "s", trace=tr)
seen_keys = {}
for u, du, rel, pq in tr:
    for v, k_ in pq.items():
        seen_keys.setdefault(v, []).append(k_)
check("dijkstras-algorithm example: extracts s0 b1 a3 t4; a lowered from 4, t from 6; path s b a t; two-edge paths "
      "s a t = 5 and s b t = 6",
      [(u, du) for u, du, *_ in tr] == [("s", 0), ("b", 1), ("a", 3), ("t", 4)]
      and seen_keys["a"][0] == 4 and 6 in seen_keys["t"] and pred_path(dup, "s", "t", 9) == list("sbat")
      and walk_weight(DU, list("sat")) == 5 and walk_weight(DU, list("sbt")) == 6
      and "$a$ (3, lowered from 4), $t$ (4, lowered from 6)" in cdij)
cbf = read(os.path.join(CONCEPTS, "bellman-ford.md"))
B1 = wgraph("sabc", [("s", "a", 2), ("s", "c", 4), ("a", "b", 1), ("b", "c", -3), ("c", "a", 3)])
B2 = wgraph("sabc", [("s", "a", 2), ("s", "c", 4), ("a", "b", 1), ("b", "c", -3), ("c", "a", 1)])
r1, r2 = [], []
d1, _, res1 = BellmanFord(B1, "s", r1)
d2, _, res2 = BellmanFord(B2, "s", r2)
prev = {v: INF for v in "abc"}
falling = True
for row in r2:
    if not all(row[v] < prev[v] for v in "abc"):
        falling = False
    prev = row
check("bellman-ford example: cycle a b c a weighs +1 -> a2 b3 c0, nothing reported; with c->a = 1 it weighs -1, "
      "a, b, c fall in every round and 'Negative cycle!' is returned",
      [t_ for c_, t_ in simple_cycles(B1)] == [1] and d1 == dict(s=0, a=2, b=3, c=0) and res1 is None
      and [t_ for c_, t_ in simple_cycles(B2)] == [-1] and falling and res2 == "Negative cycle!" and len(r2) == 3
      and "the distances are $a$ 2, $b$ 3, $c$ 0" in cbf)

print("== Page text: numbers stated in prose")
check("8.2/8.6/8.7 statements present: d->c not tense, BellmanFord rounds, extract sequence of the counterexample",
      onpage("the edge $d\\to c$ is not tense, because $\\mathit{dist}(c) = 2 = \\mathit{dist}(d) + 1$ already")
      and onpage("it has every distance after a single iteration; moving $e\\to d$ before $f\\to d$ and $f\\to e$, it has all of them except $\\mathit{dist}(d) = 1$ after one iteration, and the rest after two")
      and onpage("Phase 5 scans $h$"))
wfs = read(os.path.join(CONCEPTS, "whatever-first-search.md"))
al = re.search(r"^aliases: (.*)$", wfs, re.M).group(1)
check("whatever-first-search no longer claims the aliases BFS / breadth-first search, and links the new page",
      '"BFS"' not in al and '"breadth-first search"' not in al and "[[concepts/breadth-first-search]]" in wfs)
allal = []
for root, _, files in os.walk(os.path.join(ROOT, "content")):
    for fn in files:
        if fn.endswith(".md"):
            m = re.search(r"^aliases: \[(.*)\]$", read(os.path.join(root, fn)), re.M)
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
