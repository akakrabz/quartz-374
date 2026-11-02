#!/usr/bin/env python3
"""Checks for every concrete claim on content/2-algorithms/05-basic-graph-algorithms.md and the concept pages
graphs, whatever-first-search and graph-reductions.

WhateverFirstSearch is implemented exactly as the page states it (pairs (p, v) in the bag, a vertex is marked
when a pair naming it is taken out, then all its edges are put in), with a stack, a queue, a priority queue
and a random bag, and instrumented to count every bag operation. It is compared on all small graphs and many
random ones with independent references: transitive closure (Warshall), Floyd-Warshall distances,
Bellman-Ford, Kruskal and brute-force spanning trees, brute-force widest paths, union-find, brute-force
arborescences, brute-force pixel regions."""
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
PAGE = os.path.join(ROOT, "content", "2-algorithms", "05-basic-graph-algorithms.md")
CONCEPTS = os.path.join(ROOT, "content", "concepts")
FIGS = os.path.join(HERE, "..", "figs")
FAIL = []
random.seed(374)
INF = float("inf")


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAIL.append(name)


def read(path):
    return open(path, encoding="utf-8").read()


TEXT = read(PAGE)
CG = read(os.path.join(CONCEPTS, "graphs.md"))
CW = read(os.path.join(CONCEPTS, "whatever-first-search.md"))
CR = read(os.path.join(CONCEPTS, "graph-reductions.md"))
FIG = {n: read(os.path.join(FIGS, f"a05-{n}.html")) for n in
       ("representations", "spanning-trees", "flood-fill", "parity")}


def table_row(text, label):
    """Cells (after the label cell) of the first markdown table row whose first cell is `label`."""
    for ln in text.splitlines():
        t = ln.lstrip("> ").strip()
        if t.startswith("|"):
            cells = [c.strip() for c in t.strip("|").split("|")]
            if cells[0] == label:
                return cells[1:]
    raise KeyError(label)


def norm(s):
    return re.sub(r"\s+", " ", s)


# ===================================================================================== graphs and bags
class Graph:
    """Vertices 0..n-1 (or any hashables), adjacency lists in a chosen order. Undirected graphs store each
    edge in both lists."""

    def __init__(self, vertices, edges, directed=False):
        self.V = list(vertices)
        self.directed = directed
        self.adj = {v: [] for v in self.V}
        self.E = set()
        for u, v in edges:
            key = (u, v) if directed else frozenset((u, v))
            if key in self.E:
                continue
            assert directed or u != v
            self.E.add(key)
            self.adj[u].append(v)
            if not directed:
                self.adj[v].append(u)

    def shuffle(self, rng):
        for v in self.V:
            rng.shuffle(self.adj[v])
        return self

    def deg(self, v):
        return len(self.adj[v])

    def indeg(self, v):
        return sum(1 for u in self.V for w in self.adj[u] if w == v)

    def m(self):
        return len(self.E)


def random_graph(n, p, directed=False, rng=random, loops=False):
    edges = []
    for u in range(n):
        for v in range(n):
            if u == v and not (directed and loops):
                continue
            if not directed and v < u:
                continue
            if rng.random() < p:
                edges.append((u, v))
    return Graph(range(n), edges, directed).shuffle(rng)


def all_undirected(n):
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        yield Graph(range(n), [pairs[k] for k in range(len(pairs)) if mask >> k & 1])


def all_directed(n):
    pairs = [(u, v) for u in range(n) for v in range(n) if u != v]
    for mask in range(1 << len(pairs)):
        yield Graph(range(n), [pairs[k] for k in range(len(pairs)) if mask >> k & 1], directed=True)


class Stack:
    def __init__(self):
        self.a = []

    def put(self, x):
        self.a.append(x)

    def take(self):
        return self.a.pop()

    def __len__(self):
        return len(self.a)


class Queue(Stack):
    def __init__(self):
        self.a = deque()

    def take(self):
        return self.a.popleft()


class RandomBag(Stack):
    def __init__(self, rng):
        self.a, self.rng = [], rng

    def take(self):
        k = self.rng.randrange(len(self.a))
        self.a[k], self.a[-1] = self.a[-1], self.a[k]
        return self.a.pop()


class PQ(Stack):
    """Priority queue of pairs; prio(pair) is computed when the pair is put in. best='min' or 'max'.
    Ties: first in, first out."""

    def __init__(self, prio, best="min"):
        self.h, self.c, self.prio, self.sign = [], 0, prio, (1 if best == "min" else -1)
        self.a = self.h

    def put(self, x):
        self.c += 1
        heapq.heappush(self.h, (self.sign * self.prio(x), self.c, x))

    def take(self):
        return heapq.heappop(self.h)[2]


def wfs(G, s, bag, on_mark=None, marked=None, check_mark=True, limit=None):
    """The page's WhateverFirstSearch(s), instrumented.
    Returns dict: order (marking order), parent, puts (line ⋆⋆ count, plus the initial put), takes (line ⋆),
    loops (line † count), per-vertex put counts, max bag size, pairs taken in order."""
    marked = {} if marked is None else marked
    st = dict(order=[], parent={}, puts=0, takes=0, loops=0, inbag={}, maxbag=0, taken=[], maxdup=0)

    def put(pair):
        bag.put(pair)
        st["puts"] += 1
        st["inbag"][pair[1]] = st["inbag"].get(pair[1], 0) + 1
        st["maxbag"] = max(st["maxbag"], len(bag))

    put((None, s))
    while len(bag):
        if limit is not None and st["takes"] > limit:
            st["runaway"] = True
            return st
        p, v = bag.take()
        st["takes"] += 1
        st["taken"].append((p, v))
        if not check_mark or v not in marked:
            marked[v] = True
            st["parent"][v] = p
            st["order"].append(v)
            if on_mark:
                on_mark(p, v)
            st["loops"] += 1
            for w in G.adj[v]:
                put((v, w))
    return st


def closure(G):
    """Warshall's transitive closure: R[u] = set of vertices reachable from u (u itself included)."""
    R = {u: {u} | set(G.adj[u]) for u in G.V}
    for k in G.V:
        for i in G.V:
            if k in R[i]:
                R[i] |= R[k]
    return R


def floyd(G, weight=None):
    d = {u: {v: (0 if u == v else INF) for v in G.V} for u in G.V}
    for u in G.V:
        for v in G.adj[u]:
            w = 1 if weight is None else weight(u, v)
            d[u][v] = min(d[u][v], w)
    for k in G.V:
        for i in G.V:
            for j in G.V:
                if d[i][k] + d[k][j] < d[i][j]:
                    d[i][j] = d[i][k] + d[k][j]
    return d


def tree_ok(G, st, s):
    """Parent edges: one per marked vertex except s, each an edge of G (directed parent -> child), every
    parent path ends at s, so they form a tree rooted at s spanning the marked vertices."""
    par = st["parent"]
    if par.get(s, "x") is not None:
        return False
    for v, p in par.items():
        if v == s:
            continue
        if p not in par or v not in G.adj[p]:
            return False
        seen, x = set(), v
        while x != s:
            if x in seen:
                return False
            seen.add(x)
            x = par[x]
    edges = {(p, v) for v, p in par.items() if v != s}
    return len(edges) == len(par) - 1


class UF:
    def __init__(self, items):
        self.p = {x: x for x in items}

    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        a, b = self.find(a), self.find(b)
        if a == b:
            return False
        self.p[a] = b
        return True


def bags(rng):
    return [("stack", Stack()), ("queue", Queue()), ("random", RandomBag(rng))]


# ===================================================================================== §5.2 counting facts
check("simple undirected graphs on V vertices have at most V(V-1)/2 edges; directed without loops V(V-1); "
      "with loops V^2 (V <= 9)",
      all(len([(u, v) for u in range(n) for v in range(u + 1, n)]) == n * (n - 1) // 2 ==
          math.comb(n, 2) and len([(u, v) for u in range(n) for v in range(n) if u != v]) == n * (n - 1)
          and len(list(itertools.product(range(n), repeat=2))) == n * n for n in range(1, 10)))
ok = True
for _ in range(400):
    n = random.randint(1, 10)
    G = random_graph(n, random.random())
    D = random_graph(n, random.random(), directed=True, loops=True)
    ok &= sum(G.deg(v) for v in G.V) == 2 * G.m()
    ok &= sum(D.deg(v) for v in D.V) == D.m() == sum(D.indeg(v) for v in D.V)
check("handshake: sum of degrees = 2E (undirected); sum of out-degrees = sum of in-degrees = E (directed), "
      "400 random graphs", ok)


def is_tree(n, edges):
    uf = UF(range(n))
    return len(edges) == n - 1 and all(uf.union(u, v) for u, v in edges)


ok = True
for n in range(1, 6):
    for G in all_undirected(n):
        E = [tuple(e) for e in G.E]
        conn = closure(G)[0] == set(G.V)
        uf = UF(range(n))
        acyclic = all(uf.union(u, v) for u, v in E)
        # tree <=> connected and acyclic <=> connected with V-1 edges
        ok &= (conn and acyclic) == (conn and len(E) == n - 1) == is_tree(n, E)
        # spanning tree exists <=> connected
        has_st = any(is_tree(n, list(sub)) for sub in itertools.combinations(E, n - 1)) if len(E) >= n - 1 else False
        ok &= has_st == conn
check("all graphs on <= 5 vertices: tree = connected + acyclic = connected with V-1 edges; "
      "a spanning tree exists iff connected", ok)

# ===================================================================================== the example graph G
VX = "abcdefgh"
EX = ["ab", "ac", "bc", "bd", "cd", "de", "ef", "gh"]
GX = Graph(VX, [tuple(e) for e in EX])
for v in VX:
    GX.adj[v].sort()
ncomp = len({frozenset(r) for r in closure(GX).values()})
check("example graph G: V = 8, E = 8, two components, degrees a2 b3 c3 d3 e2 f1 g1 h1",
      len(GX.V) == 8 and GX.m() == 8 and ncomp == 2 and
      [GX.deg(v) for v in VX] == [2, 3, 3, 3, 2, 1, 1, 1])
check("figure a05-representations: 2E = 16 list records and 16 ones in the 64-entry matrix; caption says so",
      sum(GX.deg(v) for v in VX) == 16 and "2<i>E</i> = 16 records" in FIG["representations"]
      and "<i>V</i>² = 64 entries" in FIG["representations"] and "its 16 ones" in FIG["representations"])
# adjacency array (1-indexed offsets, sorted neighbor lists concatenated)
arr, first = [], []
for v in VX:
    first.append(len(arr) + 1)
    arr += GX.adj[v]
row_first = table_row(TEXT, "first")
row_nbrs = table_row(TEXT, "records")
check("adjacency array of G on the page: offsets 1 3 6 9 12 14 15 16, records b c a c d a b d b c e d f e h g",
      [int(c) for c in row_first] == first == [1, 3, 6, 9, 12, 14, 15, 16] and
      "".join(row_nbrs).replace(" ", "") == "".join(arr) == "bcacdabdbcedfehg", f"{first} {''.join(arr)}")
lookup_ok = True
for u in VX:
    for v in VX:
        seg = arr[first[VX.index(u)] - 1: (first + [len(arr) + 1])[VX.index(u) + 1] - 1]
        import bisect
        k = bisect.bisect_left(seg, v)
        lookup_ok &= ((k < len(seg) and seg[k] == v) == (frozenset((u, v)) in GX.E))
check("adjacency array: binary search in u's sorted interval answers 'is uv an edge?' for all 64 pairs", lookup_ok)

# the book's running example (Figures 5.4, 5.9-5.11)
BOOK = {"a": "be", "b": "acef", "c": "bdfg", "d": "cg", "e": "abfgh", "f": "bceg", "g": "cdefi", "h": "e", "i": "g",
        "j": "klm", "k": "jl", "l": "jkm", "m": "jl"}
GB = Graph(BOOK, [(u, v) for u in BOOK for v in BOOK[u]])
check("book's example graph (Fig. 5.11 matrix): symmetric, 13 vertices, 19 edges, 2 components",
      all(u in BOOK[v] for u in BOOK for v in BOOK[u]) and len(GB.V) == 13 and GB.m() == 19 and
      len({frozenset(r) for r in closure(GB).values()}) == 2)
offs, recs = [], []
names = sorted(BOOK)
for v in names:
    offs.append(len(recs) + 1)
    recs += [names.index(w) + 1 for w in sorted(BOOK[v])]
check("book's adjacency array (Fig. 5.10) offsets 1 3 7 11 13 18 22 27 28 29 32 34 37 and its 38 records",
      offs == [1, 3, 7, 11, 13, 18, 22, 27, 28, 29, 32, 34, 37] and
      recs == [2, 5, 1, 3, 5, 6, 2, 4, 6, 7, 3, 7, 1, 2, 6, 7, 8, 2, 3, 5, 7, 3, 4, 5, 6, 9, 5, 7, 11, 12, 13, 10, 12,
               10, 11, 13, 10, 12])
check("page states the book's example has 13 vertices, 19 edges and two components",
      "13 vertices, 19 edges and two components" in norm(TEXT))

# ===================================================================================== Table 5.1 (operation counts)
ok = True
for _ in range(300):
    n = random.randint(1, 12)
    G = random_graph(n, random.random())
    M = [[1 if v in G.adj[u] else 0 for v in G.V] for u in G.V]
    ok &= all(M[u][v] == M[v][u] for u in G.V for v in G.V) and all(M[u][u] == 0 for u in G.V)
    for u in G.V:
        for v in G.V:
            # simultaneous scan of both lists, one record of each per step
            steps, found = 0, False
            a, b = G.adj[u], G.adj[v]
            for k in range(max(len(a), len(b)) + 1):
                steps += 1
                if k < len(a) and a[k] == v or k < len(b) and b[k] == u:
                    found = True
                    break
                if k >= len(a) or k >= len(b):
                    break
            ok &= found == (M[u][v] == 1) and steps <= 1 + min(G.deg(u), G.deg(v))
check("undirected adjacency matrix symmetric with zero diagonal; scanning both lists in parallel decides uv in "
      "<= 1 + min{deg u, deg v} steps (300 random graphs)", ok)

# ===================================================================================== Lemma 5.1 and the analysis
def lemma_check(G, s, bag):
    st = wfs(G, s, bag)
    R = closure(G)[s]
    marked = set(st["order"])
    res = {}
    res["reach"] = marked == R
    res["tree"] = tree_ok(G, st, s)
    res["loops"] = st["loops"] == len(marked)
    star2 = st["puts"] - 1
    if G.directed:
        res["puts"] = star2 == sum(G.deg(v) for v in marked) <= G.m()
        res["per"] = all(st["inbag"].get(w, 0) - (w == s) == sum(1 for u in marked if w in G.adj[u])
                         <= G.indeg(w) for w in G.V)
    else:
        Ecomp = sum(1 for e in G.E if set(e) <= marked)
        res["puts"] = star2 == sum(G.deg(v) for v in marked) == 2 * Ecomp <= 2 * G.m()
        res["per"] = all(st["inbag"].get(w, 0) - (w == s) == (G.deg(w) if w in marked else 0) for w in G.V)
    res["takes"] = st["takes"] == st["puts"] <= (G.m() if G.directed else 2 * G.m()) + 1
    return res, st


agg = {}
cnt = 0
rng = random.Random(1)
for n in range(1, 6):
    for G in all_undirected(n):
        G.shuffle(rng)
        for s in G.V:
            for name, bag in bags(rng):
                res, _ = lemma_check(G, s, bag)
                cnt += 1
                for k, v in res.items():
                    agg[k] = agg.get(k, True) and v
for n in range(1, 5):
    for G in all_directed(n):
        G.shuffle(rng)
        for s in G.V:
            for name, bag in bags(rng):
                res, _ = lemma_check(G, s, bag)
                cnt += 1
                for k, v in res.items():
                    agg[k] = agg.get(k, True) and v
for _ in range(3000):
    n = rng.randint(1, 14)
    G = random_graph(n, rng.random() ** 2, directed=rng.random() < 0.5, rng=rng, loops=True)
    s = rng.randrange(n)
    for name, bag in bags(rng):
        res, _ = lemma_check(G, s, bag)
        cnt += 1
        for k, v in res.items():
            agg[k] = agg.get(k, True) and v
check(f"Lemma 5.1: WFS marks exactly the vertices reachable from s (= transitive closure), stack/queue/random bag, "
      f"all undirected graphs <= 5 vertices, all digraphs <= 4, 3000 random ({cnt} runs)", agg["reach"])
check("Lemma 5.1: parent edges form a tree rooted at s spanning the marked vertices, every parent edge an edge of G "
      "(directed: parent -> child)", agg["tree"])
check("analysis: the for loop (†) runs once per marked vertex", agg["loops"])
check("analysis: line (⋆⋆) runs sum of deg over marked vertices = 2 E(component) <= 2E times (undirected), "
      "<= E (directed)", agg["puts"])
check("analysis: each vertex w != s enters the bag exactly deg(w) times if reachable (undirected), "
      "#marked in-neighbors <= indeg(w) times (directed); s once more", agg["per"])
check("analysis: line (⋆) runs as often as pairs are put in: <= 2E + 1 (undirected), <= E + 1 (directed)",
      agg["takes"])

# adjacency matrix version: listing neighbors scans a whole row
ok = True
for _ in range(200):
    n = random.randint(1, 10)
    G = random_graph(n, random.random(), directed=random.random() < 0.5)
    M = [[1 if v in G.adj[u] else 0 for v in G.V] for u in G.V]
    probes = 0
    bag, marked = [0], set()
    while bag:
        v = bag.pop()
        if v not in marked:
            marked.add(v)
            for w in G.V:
                probes += 1
                if M[v][w]:
                    bag.append(w)
    ok &= probes == n * len(marked) and marked == closure(G)[0]
check("adjacency-matrix WFS reads exactly V matrix entries per marked vertex: O(V^2 + ET)", ok)

# forgetting the mark test never stops on an undirected graph with a reachable edge
ok = True
for _ in range(100):
    n = random.randint(2, 7)
    G = random_graph(n, 0.6)
    s = random.randrange(n)
    st = wfs(G, s, Stack(), check_mark=False, limit=5000)
    ok &= st.get("runaway", False) == (G.deg(s) > 0)
    st = wfs(G, s, Queue(), check_mark=False, limit=5000)
    ok &= st.get("runaway", False) == (G.deg(s) > 0)
check("without the test 'if v is unmarked' the loop never ends once s has an edge (stack and queue)", ok)

# ===================================================================================== the page's trace on G
st_s = wfs(GX, "a", Stack())
st_q = wfs(GX, "a", Queue())


def pairs_str(st):
    return ", ".join(f"({p or '∅'},{v})" for p, v in st["taken"])


check("trace, stack from a: takes (∅,a), (a,c), (c,d), (d,e), (e,f), (f,e), (e,d), (d,c), (d,b), (b,d), (b,c), (b,a), "
      "(c,b), (c,a), (a,b); marks a c d e f b",
      pairs_str(st_s) == "(∅,a), (a,c), (c,d), (d,e), (e,f), (f,e), (e,d), (d,c), (d,b), (b,d), (b,c), (b,a), (c,b), "
                         "(c,a), (a,b)" and "".join(st_s["order"]) == "acdefb")
check("trace, stack: 15 = 2·7 + 1 pairs taken; b entered the bag 3 = deg(b) times, as (a,b), (c,b), (d,b); "
      "parent(b) = d; g, h untouched",
      st_s["takes"] == 15 == 2 * 7 + 1 and st_s["inbag"]["b"] == 3 and st_s["parent"]["b"] == "d"
      and "g" not in st_s["inbag"] and "h" not in st_s["inbag"])
check("trace, stack: depth-first tree a-c, c-d, d-e, e-f, d-b",
      {(p, v) for v, p in st_s["parent"].items() if p} == {("a", "c"), ("c", "d"), ("d", "e"), ("e", "f"), ("d", "b")})
check("trace, queue from a: marks a b c d e f; parents b,c <- a, d <- b, e <- d, f <- e; distances 1 1 2 3 4",
      "".join(st_q["order"]) == "abcdef" and st_q["parent"] == {"a": None, "b": "a", "c": "a", "d": "b", "e": "d",
                                                                 "f": "e"}
      and [floyd(GX)["a"][v] for v in "bcdef"] == [1, 1, 2, 3, 4])
page_trace = norm(TEXT)
check("page shows the stack trace and the trees as computed",
      "(∅,a), (a,c), (c,d), (d,e), (e,f)" in page_trace and "(f,e), (e,d), (d,c)" in page_trace
      and "(b,d), (b,c), (b,a), (c,b), (c,a), (a,b)" in page_trace)

# ===================================================================================== DFS: recursive vs iterative
def rec_dfs(G, s):
    order, parent = [], {s: None}

    def go(v, p):
        if v in order_set:
            return
        order_set.add(v)
        order.append(v)
        parent[v] = p
        for w in G.adj[v]:
            go(w, v)

    order_set = set()
    go(s, None)
    return order, parent


ok_rev = ok_same = True
for _ in range(1500):
    n = random.randint(1, 12)
    G = random_graph(n, random.random(), directed=random.random() < 0.5)
    s = random.randrange(n)
    o1, p1 = rec_dfs(G, s)
    Grev = Graph(G.V, [], G.directed)
    Grev.adj = {v: list(reversed(G.adj[v])) for v in G.V}
    st = wfs(Grev, s, Stack())
    ok_rev &= st["order"] == o1 and st["parent"] == p1
    # the book's IterativeDFS (bare vertices) marks in the same order as WFS with a stack
    bag, mk, order = [s], set(), []
    while bag:
        v = bag.pop()
        if v not in mk:
            mk.add(v)
            order.append(v)
            for w in G.adj[v]:
                bag.append(w)
    ok_same &= order == wfs(G, s, Stack())["order"]
check("IterativeDFS that pushes each neighbor list in reverse marks the vertices in RecursiveDFS's order and builds "
      "the same tree (1500 random graphs)", ok_rev)
check("IterativeDFS (bare vertices) = WhateverFirstSearch with a stack, same marking order", ok_same)

# ===================================================================================== BFS
ok_dist = ok_mono = True
for _ in range(2000):
    n = random.randint(1, 14)
    G = random_graph(n, random.random() ** 1.5, directed=random.random() < 0.5)
    s = random.randrange(n)
    st = wfs(G, s, Queue())
    d = floyd(G)[s]

    def depth(v):
        k = 0
        while st["parent"][v] is not None:
            v, k = st["parent"][v], k + 1
        return k

    ok_dist &= all(depth(v) == d[v] for v in st["order"])
    ok_mono &= all(d[a] <= d[b] for a, b in zip(st["order"], st["order"][1:]))
check("BFS: the parent path of every marked v has dist(s, v) edges (Floyd-Warshall), 2000 random graphs", ok_dist)
check("BFS marks vertices in nondecreasing order of distance from s", ok_mono)

# ===================================================================================== EagerWFS
def eager(G, s, bag):
    mk, parent, order = {s}, {s: None}, [s]
    bag.put(s)
    while len(bag):
        v = bag.take()
        for w in G.adj[v]:
            if w not in mk:
                mk.add(w)
                parent[w] = v
                order.append(w)
                bag.put(w)
    return order, parent


ok = True
for _ in range(1500):
    n = random.randint(1, 12)
    G = random_graph(n, random.random(), directed=random.random() < 0.5)
    s = random.randrange(n)
    o, p = eager(G, s, Queue())
    st = wfs(G, s, Queue())
    ok &= o == st["order"] and p == st["parent"]
check("EagerWFS (mark when put in) with a queue = breadth-first search: same order, same tree", ok)
T3 = Graph("abc", [("a", "b"), ("b", "c"), ("a", "c")])
dfs_trees, eager_trees = set(), set()
for perm in itertools.product(*[list(itertools.permutations(T3.adj[v])) for v in "abc"]):
    H = Graph("abc", [])
    H.adj = dict(zip("abc", [list(x) for x in perm]))
    dfs_trees.add(frozenset((p, v) for v, p in rec_dfs(H, "a")[1].items() if p))
    for bag in (Stack(), Queue()):
        eager_trees.add(frozenset((p, v) for v, p in eager(H, "a", bag)[1].items() if p))
check("triangle abc from a: every depth-first tree gives a a single child (ab, bc or ac, cb), every EagerWFS tree "
      "(stack or queue, any neighbor order) makes a the parent of b and c",
      eager_trees == {frozenset({("a", "b"), ("a", "c")})}
      and dfs_trees == {frozenset({("a", "b"), ("b", "c")}), frozenset({("a", "c"), ("c", "b")})}
      and all(sum(1 for p, v in t if p == "a") == 1 for t in dfs_trees) and not (dfs_trees & eager_trees)
      and "gives $a$ a single child (tree $ab, bc$ or $ac, cb$)" in TEXT)

# ===================================================================================== best-first search
def best_first(G, s, w, kind):
    """kind: 'prim' (priority w(uv), min), 'dijkstra' (dist(u) + w(u->v), min), 'widest' (min{width(u), w}, max)."""
    val = {}
    if kind == "prim":
        bag = PQ(lambda pr: -INF if pr[0] is None else w(pr[0], pr[1]))
    elif kind == "dijkstra":
        bag = PQ(lambda pr: 0 if pr[0] is None else val[pr[0]] + w(pr[0], pr[1]))
    else:
        bag = PQ(lambda pr: INF if pr[0] is None else min(val[pr[0]], w(pr[0], pr[1])), best="max")

    def on_mark(p, v):
        if p is None:
            val[v] = 0 if kind == "dijkstra" else INF
        elif kind == "dijkstra":
            val[v] = val[p] + w(p, v)
        elif kind == "widest":
            val[v] = min(val[p], w(p, v))

    st = wfs(G, s, bag, on_mark=on_mark)
    return st, val


def kruskal(G, w):
    uf = UF(G.V)
    T = []
    for e in sorted(G.E, key=lambda e: w(*tuple(e))):
        u, v = tuple(e)
        if uf.union(u, v):
            T.append(frozenset(e))
    return T


def weights(G, rng, distinct=False, lo=1, hi=9):
    if distinct:
        vals = rng.sample(range(1, 10 * len(G.E) + 10), len(G.E))
    else:
        vals = [rng.randint(lo, hi) for _ in G.E]
    W = dict(zip(G.E, vals))
    if G.directed:
        return lambda u, v: W[(u, v)]
    return lambda u, v: W[frozenset((u, v))]


ok_prim = ok_unique = ok_brute = ok_size = True
dup_two = False
rng = random.Random(7)
for trial in range(1200):
    n = rng.randint(1, 9)
    G = random_graph(n, rng.random(), rng=rng)
    distinct = trial % 2 == 0
    w = weights(G, rng, distinct=distinct)
    s = rng.randrange(n)
    st, _ = best_first(G, s, w, "prim")
    comp = set(st["order"])
    T = {frozenset((p, v)) for v, p in st["parent"].items() if p is not None}
    Gc = Graph(sorted(comp), [tuple(e) for e in G.E if set(e) <= comp])
    K = kruskal(Gc, w)
    ok_prim &= sum(w(*tuple(e)) for e in T) == sum(w(*tuple(e)) for e in K)
    ok_size &= st["maxbag"] <= 2 * G.m() + 1
    if distinct:
        for s2 in comp:
            H = Graph(G.V, [tuple(e) for e in G.E]).shuffle(rng)
            st2, _ = best_first(H, s2, w, "prim")
            ok_unique &= {frozenset((p, v)) for v, p in st2["parent"].items() if p is not None} == set(K) == T
    if len(Gc.E) <= 12 and len(comp) <= 7:
        Es = list(Gc.E)
        idx = {v: k for k, v in enumerate(sorted(comp))}
        cands = [sum(w(*tuple(e)) for e in sub) for sub in itertools.combinations(Es, len(comp) - 1)
                 if is_tree(len(comp), [(idx[a], idx[b]) for a, b in (tuple(e) for e in sub)])]
        ok_brute &= min(cands) == sum(w(*tuple(e)) for e in T)
check("best-first with priority w(uv) ('Prim') = minimum spanning tree weight (Kruskal) of s's component, "
      "1200 random weighted graphs", ok_prim)
check("best-first MST weight = brute force over all spanning trees (components <= 7 vertices, <= 12 edges)", ok_brute)
check("distinct weights: the same tree from every start vertex and every neighbor order (= Kruskal's)", ok_unique)
check("the priority queue never holds more than 2E + 1 pairs", ok_size)
# both directions of one undirected edge can sit in the priority queue together
G2 = Graph("abc", [("a", "b"), ("a", "c"), ("b", "c")])
Wt = {frozenset("ab"): 1, frozenset("ac"): 2, frozenset("bc"): 9}
bag = PQ(lambda pr: -INF if pr[0] is None else Wt[frozenset(pr)])
both = [False]
orig_put = bag.put


def spy_put(x):
    orig_put(x)
    pairs = {tuple(t[2]) for t in bag.h}
    if ("b", "c") in pairs and ("c", "b") in pairs:
        both[0] = True


bag.put = spy_put
wfs(G2, "a", bag)
check("undirected: both pairs (b,c) and (c,b) of one edge can be in the priority queue at once (triangle, "
      "weights ab 1, ac 2, bc 9)", both[0])


def bellman_ford(G, s, w):
    d = {v: INF for v in G.V}
    d[s] = 0
    for _ in range(len(G.V)):
        for u in G.V:
            for v in G.adj[u]:
                if d[u] + w(u, v) < d[v]:
                    d[v] = d[u] + w(u, v)
    return d


def widest_brute(G, s, w):
    best = {s: INF}

    def go(v, width, seen):
        for x in G.adj[v]:
            if x not in seen:
                nw = min(width, w(v, x))
                if nw > best.get(x, -INF):
                    best[x] = nw
                go(x, nw, seen | {x})

    go(s, INF, {s})
    return best


ok_d = ok_w = ok_d0 = True
for trial in range(1500):
    n = rng.randint(1, 8)
    G = random_graph(n, rng.random(), directed=rng.random() < 0.5, rng=rng)
    w = weights(G, rng)
    s = rng.randrange(n)
    st, dist = best_first(G, s, w, "dijkstra")
    bf = bellman_ford(G, s, w)
    ok_d &= set(dist) == {v for v in G.V if bf[v] < INF} and all(dist[v] == bf[v] for v in dist)
    # parent path length equals dist
    for v in dist:
        L, x = 0, v
        while st["parent"][x] is not None:
            L += w(st["parent"][x], x)
            x = st["parent"][x]
        ok_d &= L == dist[v]
    st, width = best_first(G, s, w, "widest")
    ok_w &= width == widest_brute(G, s, w)
    w0 = weights(G, rng, lo=0, hi=4)
    st, dist = best_first(G, s, w0, "dijkstra")
    bf = bellman_ford(G, s, w0)
    ok_d0 &= all(dist[v] == bf[v] for v in dist)
check("best-first 'Dijkstra' (priority dist(u) + w(u->v)) = Bellman-Ford distances, and each parent path has "
      "that length; positive weights, directed and undirected, 1500 graphs", ok_d)
check("best-first widest path (priority min{width(u), w(u->v)}, largest first) = brute force over all simple "
      "paths", ok_w)
check("(the 'Dijkstra' variant is also right with zero-weight edges)", ok_d0)

# directed: best-first with priority w(u->v) is NOT a minimum-weight arborescence
def min_arborescence(G, s, w, reach):
    others = [v for v in reach if v != s]
    best = INF
    choices = [[u for u in reach if v in G.adj[u]] for v in others]
    for pick in itertools.product(*choices):
        par = dict(zip(others, pick))
        good = True
        for v in others:
            seen, x = set(), v
            while x != s:
                if x in seen:
                    good = False
                    break
                seen.add(x)
                x = par[x]
            if not good:
                break
        if good:
            best = min(best, sum(w(par[v], v) for v in others))
    return best


DG = Graph("sab", [("s", "a"), ("s", "b"), ("b", "a")], directed=True)
DW = {("s", "a"): 2, ("s", "b"): 3, ("b", "a"): 1}
st, _ = best_first(DG, "s", lambda u, v: DW[(u, v)], "prim")
bfw = sum(DW[(p, v)] for v, p in st["parent"].items() if p)
check("directed counterexample on the page: best-first picks s->a, s->b (weight 5); the arborescence s->b, b->a "
      "weighs 4", bfw == 5 and min_arborescence(DG, "s", lambda u, v: DW[(u, v)], "sab") == 4
      and {(p, v) for v, p in st["parent"].items() if p} == {("s", "a"), ("s", "b")})
worse = 0
for trial in range(300):
    n = rng.randint(2, 6)
    G = random_graph(n, rng.random(), directed=True, rng=rng)
    w = weights(G, rng)
    st, _ = best_first(G, 0, w, "prim")
    reach = st["order"]
    got = sum(w(p, v) for v, p in st["parent"].items() if p is not None)
    opt = min_arborescence(G, 0, w, reach)
    worse += got > opt
    assert got >= opt
check("random digraphs: best-first by edge weight is often heavier than the best arborescence", worse > 20,
      f"{worse} of 300")

# ===================================================================================== components
def count_components(G):
    marked, count = {}, 0
    puts = 0
    for v in G.V:
        if v not in marked:
            count += 1
            puts += wfs(G, v, Stack(), marked=marked)["puts"]
    return count, puts


def count_and_label(G, book_literal=False):
    marked, comp, count = set(), {}, 0
    for v in G.V:
        if v not in marked:
            count += 1
            bag = []
            if not book_literal:
                bag.append(v)  # put v into the bag
            while bag:
                x = bag.pop()
                if x not in marked:
                    marked.add(x)
                    comp[x] = count
                    for w in G.adj[x]:
                        bag.append(w)
    return count, comp


ok = ok_lab = ok_puts = ok_lit = True
for _ in range(1500):
    n = random.randint(1, 15)
    G = random_graph(n, random.random() ** 2)
    uf = UF(G.V)
    for e in G.E:
        uf.union(*tuple(e))
    C = len({uf.find(v) for v in G.V})
    c, puts = count_components(G)
    ok &= c == C
    ok_puts &= puts == 2 * G.m() + C
    c2, comp = count_and_label(G)
    ok_lab &= c2 == C and all((comp[u] == comp[v]) == (uf.find(u) == uf.find(v)) for u in G.V for v in G.V)
    c3, comp3 = count_and_label(G, book_literal=True)
    ok_lit &= c3 == n and comp3 == {}
check("CountComponents = number of union-find classes (1500 random graphs)", ok)
check("CountAndLabel: comp(u) = comp(v) iff u, v in the same union-find class", ok_lab)
check("WFSAll puts exactly 2E + C pairs into the bag in all (C = number of components)", ok_puts)
check("book's LabelOne as printed (no 'put v into the bag') labels nothing and CountAndLabel returns V", ok_lit)
c, comp = count_and_label(GX)
check("example graph G: CountAndLabel returns 2, labels a-f with 1 and g, h with 2; 2E + C = 18 bag insertions",
      c == 2 and all(comp[v] == 1 for v in "abcdef") and comp["g"] == comp["h"] == 2
      and count_components(GX) == (2, 18))

# directed: tree of the reachable set only
DG2 = Graph("abc", [("a", "b"), ("c", "b")], directed=True)
st = wfs(DG2, "a", Stack())
check("directed a->b, c->b: from a, WFS marks only a, b (c is not reachable though the drawing is connected)",
      set(st["order"]) == {"a", "b"})

# ===================================================================================== §5.3 examples
def hanoi_graph(k):
    confs = list(itertools.product(range(3), repeat=k))  # conf[i] = peg of disk i (disk 0 smallest)
    edges = set()
    for c in confs:
        for d in range(k):
            if any(c[e] == c[d] for e in range(d)):
                continue  # a smaller disk sits on d
            for peg in range(3):
                if peg != c[d] and not any(c[e] == peg for e in range(d)):
                    c2 = c[:d] + (peg,) + c[d + 1:]
                    edges.add(frozenset((c, c2)))
    return Graph(confs, [tuple(e) for e in edges])


H4 = hanoi_graph(4)
st = wfs(H4, (0,) * 4, Queue())
depth = {}
for v in st["order"]:
    p = st["parent"][v]
    depth[v] = 0 if p is None else depth[p] + 1
check("4-disk Tower of Hanoi configuration graph: 81 vertices, 120 edges; BFS from all-on-one-peg reaches "
      "all-on-another at depth 15 = 2^4 - 1", len(H4.V) == 81 and H4.m() == 120 and depth[(2,) * 4] == 15
      and floyd(H4)[(0,) * 4][(2,) * 4] == 15)
H3 = hanoi_graph(3)
degs = sorted(H3.deg(v) for v in H3.V)
check("3-disk Hanoi graph: 27 vertices, 39 edges, three corners of degree 2 and 24 vertices of degree 3; "
      "3·2 + 24·3 = 78 = 2·39; corner to corner 7 = 2^3 - 1",
      len(H3.V) == 27 and H3.m() == 39 and degs == [2] * 3 + [3] * 24 and 3 * 2 + 24 * 3 == 78 == 2 * 39
      and floyd(H3)[(0,) * 3][(1,) * 3] == 7 and all(H3.deg((p,) * 3) == 2 for p in range(3)))
check("Hanoi graph has 3(3^k - 1)/2 edges for k = 1..5", all(hanoi_graph(k).m() == 3 * (3 ** k - 1) // 2
                                                            for k in range(1, 6)))


def acyclic(G):
    color = {}

    def go(v):
        color[v] = 1
        for w in G.adj[v]:
            if color.get(w) == 1 or (w not in color and not go(w)):
                return False
        color[v] = 2
        return True

    return all(color.get(v) or go(v) for v in G.V)


ok = True
for n in range(1, 30):
    F = Graph(range(n + 1), [(i - 1, i) for i in range(2, n + 1)] + [(i - 2, i) for i in range(2, n + 1)],
              directed=True)
    ok &= len(F.V) == n + 1 and F.m() == 2 * (n - 1) and acyclic(F)
check("Fibonacci dependency graph: n + 1 vertices, 2(n - 1) edges, a dag (n = 1..29)", ok)
ok = True
for m in range(0, 7):
    for n in range(0, 7):
        Vs = [(i, j) for i in range(m + 1) for j in range(n + 1)]
        Es = [((i - 1, j), (i, j)) for i in range(1, m + 1) for j in range(1, n + 1)] + \
             [((i, j - 1), (i, j)) for i in range(1, m + 1) for j in range(1, n + 1)] + \
             [((i - 1, j - 1), (i, j)) for i in range(1, m + 1) for j in range(1, n + 1)]
        D = Graph(Vs, Es, directed=True)
        ok &= len(D.V) == (m + 1) * (n + 1) and D.m() == 3 * m * n and acyclic(D)
        # Ch 5 direction (needed -> needing): the row-major evaluation order is a topological order,
        # i.e. a reverse topological order of the reversed (Ch 6) graph
        pos = {v: k for k, v in enumerate(sorted(Vs))}
        ok &= all(pos[u] < pos[v] for u, v in Es)
check("edit-distance dependency graph: (m+1)(n+1) vertices, 3mn edges into the non-base subproblems, a dag; the "
      "row-major evaluation order is a topological order of it (Ch 5 edge direction)", ok
      and "that is a **topological order**" in TEXT and "*reverse* topological order" in TEXT)

# DFA emptiness by reachability
ok = True
for _ in range(600):
    q = random.randint(1, 6)
    sig = random.randint(1, 3)
    delta = {(p, a): random.randrange(q) for p in range(q) for a in range(sig)}
    acc = {p for p in range(q) if random.random() < 0.3}
    GM = Graph(range(q), [(p, delta[(p, a)]) for p in range(q) for a in range(sig)], directed=True)
    reach_acc = bool(set(wfs(GM, 0, Stack())["order"]) & acc)
    nonempty = False
    for L in range(q):
        for w in itertools.product(range(sig), repeat=L):
            p = 0
            for a in w:
                p = delta[(p, a)]
            if p in acc:
                nonempty = True
                break
        if nonempty:
            break
    ok &= reach_acc == nonempty and GM.m() <= q * sig
check("DFA M: L(M) is empty iff no accepting state is reachable from s in G_M (brute force over strings of length "
      "< |Q|; G_M has <= |Q||Σ| edges), 600 random DFAs", ok)

# ===================================================================================== §5.7 flood fill
def grid_graph(P):
    m = len(P)
    k = len(P[0])
    Vs = [(i, j) for i in range(m) for j in range(k)]
    Es = [((i, j), (i + 1, j)) for i in range(m - 1) for j in range(k) if P[i][j] == P[i + 1][j]] + \
         [((i, j), (i, j + 1)) for i in range(m) for j in range(k - 1) if P[i][j] == P[i][j + 1]]
    return Graph(Vs, Es)


def region_brute(P, s):
    """Fixpoint: pixels of s's color joined to the set by a horizontal/vertical step."""
    R = {s}
    changed = True
    while changed:
        changed = False
        for i in range(len(P)):
            for j in range(len(P[0])):
                if (i, j) not in R and P[i][j] == P[s[0]][s[1]] and any(
                        (i + di, j + dj) in R for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    R.add((i, j))
                    changed = True
    return R


def flood_fill_graph(P, s, new):
    G = grid_graph(P)
    Q = [list(r) for r in P]

    def on_mark(p, v):
        Q[v[0]][v[1]] = new

    wfs(G, s, Stack(), on_mark=on_mark)
    return Q


def flood_fill_implicit(P, s, new, limit=None):
    """Pixel map as implicit adjacency list, color as the mark."""
    Q = [list(r) for r in P]
    old = Q[s[0]][s[1]]
    bag, steps, puts = [s], 0, 1
    while bag:
        steps += 1
        if limit and steps > limit:
            return None, puts
        i, j = bag.pop()
        if Q[i][j] == old:  # unmarked
            Q[i][j] = new  # mark
            for di, dj in ((-1, 0), (0, 1), (1, 0), (0, -1)):
                a, b = i + di, j + dj
                if 0 <= a < len(Q) and 0 <= b < len(Q[0]) and Q[a][b] == old:
                    bag.append((a, b))
                    puts += 1
    return Q, puts


def flood_fill_blackbox(P, s, new):
    """The page's write-up: whatever-first search in G from s as a black box, then recolor every marked vertex."""
    G = grid_graph(P)
    marked = set(wfs(G, s, RandomBag(random.Random(5)))["order"])
    return [[new if (i, j) in marked else P[i][j] for j in range(len(P[0]))] for i in range(len(P))]


ok = ok_imp = ok_puts = ok_edges = True
for _ in range(1500):
    m, k = random.randint(1, 9), random.randint(1, 9)
    ncol = random.randint(1, 3)
    P = [[random.randrange(ncol) for _ in range(k)] for _ in range(m)]
    s = (random.randrange(m), random.randrange(k))
    new = ncol + 1
    R = region_brute(P, s)
    expect = [[new if (i, j) in R else P[i][j] for j in range(k)] for i in range(m)]
    ok &= flood_fill_graph(P, s, new) == expect == flood_fill_blackbox(P, s, new)
    Q, puts = flood_fill_implicit(P, s, new)
    ok_imp &= Q == expect
    ok_puts &= puts <= 4 * len(R) + 1
    G = grid_graph(P)
    ok_edges &= len(G.V) == m * k and G.m() <= m * (k - 1) + (m - 1) * k
check("flood fill by WFS in G (recolor every marked vertex afterwards, as written up; or when marking, as in the "
      "book) = brute-force region, 1500 random maps up to 9 x 9, 1-3 colors", ok)
check("implicit version (pixel map as adjacency list, color as the mark) gives the same picture", ok_imp)
check("implicit version puts at most 4k + 1 pixels into the bag for a region of k pixels", ok_puts)
ok = all(grid_graph([[0] * n for _ in range(n)]).m() == 2 * n * (n - 1) <= 2 * n * n for n in range(1, 15))
check("n x n map: n^2 vertices and at most 2n(n - 1) < 2n^2 edges (equality for a one-color map)", ok and ok_edges)
P1 = [[1, 1], [1, 0]]
Q, _ = flood_fill_implicit(P1, (0, 0), 1, limit=10000)
check("color as the mark fails when the new color equals the old one: the loop never ends", Q is None)

# the figure's pixel map
PIX = ["...#..#.", ".#.#..#.", "...#.##.", "##.#....", "..##.#.#", ".#.#.#..", "...#.##.", "####...."]
R = region_brute(PIX, (2, 1))
GP = grid_graph(PIX)
check("flood-fill figure: 8 x 8 map, 57 edges in G, region of the circled pixel (2,1) has 9 pixels; (4,1) touches "
      "it only diagonally and keeps its color",
      GP.m() == 57 and len(R) == 9 and (4, 1) not in R and PIX[4][1] == "." and (3, 2) in R
      and "(57 edges" in FIG["flood-fill"] and "the 9 plain pixels" in FIG["flood-fill"])

# ===================================================================================== figure: spanning trees
N7 = 7
ORDER = [(-1, 0), (0, 1), (1, 0), (0, -1)]
GG = Graph([(i, j) for i in range(N7) for j in range(N7)], [])
GG.adj = {(i, j): [(i + a, j + b) for a, b in ORDER if 0 <= i + a < N7 and 0 <= j + b < N7]
          for i in range(N7) for j in range(N7)}
GG.E = {frozenset((v, w)) for v in GG.adj for w in GG.adj[v]}
C7 = (3, 3)


def tdepth(st):
    best = 0
    for v in st["parent"]:
        k = 0
        while st["parent"][v] is not None:
            v, k = st["parent"][v], k + 1
        best = max(best, k)
    return best


class FigRandom(Stack):
    """The figure's random bag: list.pop(rng.randrange(len))."""

    def __init__(self, rng):
        self.a, self.rng = [], rng

    def take(self):
        return self.a.pop(self.rng.randrange(len(self.a)))


s1, s2, s3 = wfs(GG, C7, Stack()), wfs(GG, C7, Queue()), wfs(GG, C7, FigRandom(random.Random(3)))
check("grid figure: 7 x 7 grid has 84 edges; each search takes 169 = 2E + 1 pairs",
      len(GG.E) == 84 and s1["takes"] == s2["takes"] == s3["takes"] == 169 == 2 * 84 + 1)
check("grid figure: depth-first tree is a Hamiltonian path (depth 48), breadth-first depth 6, random-bag depth 8; "
      "all three are spanning trees", tdepth(s1) == 48 and tdepth(s2) == 6 == max(floyd(GG)[C7].values())
      and tdepth(s3) == 8 and all(tree_ok(GG, s, C7) and len(s["order"]) == 49 for s in (s1, s2, s3))
      and "(depth 48)" in FIG["spanning-trees"] and "has depth 6" in FIG["spanning-trees"]
      and "(depth 8)" in FIG["spanning-trees"])

# ===================================================================================== even walks (parity graph)
def parity_graph(G):
    Vs = [(v, b) for v in G.V for b in (0, 1)]
    Es = []
    for e in G.E:
        u, v = tuple(e)
        Es += [((u, 0), (v, 1)), ((u, 1), (v, 0))]
    return Graph(Vs, Es)


def even_walk_brute(G, s, t):
    """Sets of endpoints of walks from s of length exactly L, L = 0 .. 2V; even L reaching t?"""
    cur = {s}
    for L in range(2 * len(G.V) + 1):
        if L % 2 == 0 and t in cur:
            return True
        cur = {w for v in cur for w in G.adj[v]}
    return False


ok = ok_size = True
for n in range(1, 6):
    for G in all_undirected(n):
        H = parity_graph(G)
        ok_size &= len(H.V) == 2 * n and H.m() == 2 * G.m()
        for s in G.V:
            reach = set(wfs(H, (s, 0), Stack())["order"])
            for t in G.V:
                ok &= ((t, 0) in reach) == even_walk_brute(G, s, t)
check("even walks: (t,0) reachable from (s,0) in H iff G has an s-t walk with an even number of edges "
      "(all graphs <= 5 vertices, all s, t; brute force over walk lengths <= 2V)", ok)
check("H has 2V vertices and 2E edges", ok_size)
GPAR = Graph("stuv", [("s", "t"), ("t", "u"), ("u", "v"), ("v", "t")])
HP = parity_graph(GPAR)
path = [("s", 0), ("t", 1), ("u", 0), ("v", 1), ("t", 0)]
GPAR2 = Graph("stuv", [("s", "t"), ("t", "u"), ("u", "v")])
check("parity figure: s-t-u-v-t is a walk of length 4, the colored path is a path in H, H has 8 edges; without the "
      "triangle edge vt the graph is bipartite and (t,0) is unreachable",
      all(frozenset((a, b)) in HP.E for a, b in zip(path, path[1:])) and HP.m() == 8
      and ("t", 0) in wfs(HP, ("s", 0), Stack())["order"]
      and ("t", 0) not in wfs(parity_graph(GPAR2), ("s", 0), Stack())["order"]
      and not even_walk_brute(GPAR2, "s", "t") and floyd(GPAR)["s"]["t"] == 1)

# ===================================================================================== concept pages
# K_n (whatever-first-search concept page)
ok = True
for n in range(2, 9):
    Kn = Graph(range(n), [(u, v) for u in range(n) for v in range(u + 1, n)])
    for _ in range(20):
        Kn.shuffle(random)
        s = random.randrange(n)
        a, b = wfs(Kn, s, Stack()), wfs(Kn, s, Queue())
        ok &= a["puts"] == b["puts"] == n * (n - 1) + 1 and len(a["order"]) == n
        ok &= tdepth(a) == n - 1 and tdepth(b) == 1
        ok &= all(b["parent"][v] == s for v in Kn.V if v != s)
check("K_n: n(n - 1) + 1 pairs go through the bag for n marks; the depth-first tree is a path (depth n - 1), the "
      "breadth-first tree a star (n = 2..8, random orders)", ok)
K5 = 5 * 4 + 1
check("K_5 numbers on the concept page: 21 pairs, 10 edges, 5 marks",
      K5 == 21 and "21" in CW and "K_5" in CW)


# knights (graph-reductions concept page)
def knight_graph(n):
    Vs = [(i, j) for i in range(1, n + 1) for j in range(1, n + 1)]
    Es = [((i, j), (i + a, j + b)) for i, j in Vs for a, b in ((1, 2), (2, 1), (1, -2), (2, -1))
          if 1 <= i + a <= n and 1 <= j + b <= n]
    return Graph(Vs, Es)


K8 = knight_graph(8)
st = wfs(K8, (1, 1), Queue())
depth = {}
for v in st["order"]:
    p = st["parent"][v]
    depth[v] = 0 if p is None else depth[p] + 1
reach5 = {(1, 1)}
frontier = {(1, 1)}
for _ in range(5):
    frontier = {w for v in frontier for w in K8.adj[v]}
    reach5 |= frontier
check("knights, 8 x 8: BFS from (1,1) reaches (8,8) at depth 6; no walk of <= 5 moves gets there",
      depth[(8, 8)] == 6 and (8, 8) not in reach5)
K3 = knight_graph(3)
check("knights, 3 x 3: the center square (2,2) has no knight move, so it is unreachable from a corner",
      K3.deg((2, 2)) == 0 and (2, 2) not in wfs(K3, (1, 1), Stack())["order"])
check("knight graph on n x n has at most 4n^2 edges (each square <= 8 neighbors), n = 1..12; 168 for n = 8",
      all(knight_graph(n).m() <= 4 * n * n and all(knight_graph(n).deg(v) <= 8 for v in knight_graph(n).V)
          for n in range(1, 13)) and K8.m() == 168)

# ===================================================================================== text claims
T = norm(TEXT)
check("page states the bag bounds 2E + 1 and E + 1, and O(V + ET), O(V^2 + ET)",
      "2E+1" in T.replace(" ", "") and "E+1" in T.replace(" ", "") and "O(V + ET)" in T and "O(V^2 + ET)" in T)
check("page states best-first O(V + E log E)", "O(V + E\\log E)" in T)
check("Hanoi numbers on the pages: 81 configurations, 120 edges, 15 moves; 27, 39 on the graphs concept page",
      "81" in T and "120" in T and "15" in T and "27" in CG and "39" in CG and "78" in CG)
check("page's edit-distance dependency graph: (m+1)(n+1) vertices and 3mn edges",
      "(m+1)(n+1)" in T.replace(" ", "") and "3mn" in T.replace(" ", ""))
check("knight numbers on the concept page: 6 moves on 8 x 8, center of 3 x 3 unreachable, 4n^2 edges",
      "6 moves" in CR and "4n^2" in CR.replace(" ", ""))

# =====================================================================================================
print()
if FAIL:
    print(f"{len(FAIL)} FAILED:", *FAIL, sep="\n  ")
    sys.exit(1)
print("ALL OK")
