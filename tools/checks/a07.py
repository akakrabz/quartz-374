#!/usr/bin/env python3
"""Checks for every concrete claim on content/2-algorithms/07-minimum-spanning-trees.md and the concept pages
minimum-spanning-trees and union-find.

The page's algorithms are transcribed as stated — ShorterEdge, CountAndLabel + AddAllSafeEdges (Borůvka),
JarníkBestFirst (a heap of edges), JarníkInit/JarníkLoop (a heap of vertices with DecreaseKey, and an unsorted
array), Kruskal with the labeling union-find (smaller set relabeled) and with the forest union-find (union by rank,
path compression), and the generic algorithm with random choices of safe edges — and compared with brute force
over all spanning trees on many random weighted graphs, with distinct weights and with many ties (broken by the
page's key). Lemmas 7.1-7.3 are tested on random vertex sets and random forests. Then every example, number,
order and table on the pages and in the figures (parsed from the figure HTML) is recomputed."""
import heapq
import itertools
import math
import os
import random
import re
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
PAGE = os.path.join(ROOT, "content", "2-algorithms", "07-minimum-spanning-trees.md")
CONCEPTS = os.path.join(ROOT, "content", "concepts")
FIGS = os.path.join(HERE, "..", "figs")
FAIL = []
random.seed(374)
INF = (math.inf,)


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAIL.append(name)


def read(path):
    return open(path, encoding="utf-8").read()


page = read(PAGE)
cmst = read(os.path.join(CONCEPTS, "minimum-spanning-trees.md"))
cuf = read(os.path.join(CONCEPTS, "union-find.md"))


# =====================================================================================================
# graphs: V = list of vertices (orderable), E = list of edges (u, v) with u < v, w = dict edge -> weight.
# The vertex numbering for ShorterEdge is the position in V (1-based).
def norm(u, v):
    return (u, v) if u < v else (v, u)


class Graph:
    def __init__(self, V, w):
        self.V = list(V)
        self.w = {norm(*e): x for e, x in w.items()}
        self.E = list(self.w)
        self.num = {v: i + 1 for i, v in enumerate(self.V)}
        self.adj = {v: [] for v in self.V}
        for (u, v) in self.E:
            self.adj[u].append(v)
            self.adj[v].append(u)

    def W(self, u, v):
        return self.w[norm(u, v)]

    def key(self, e):
        """The page's key: (w(ij), min{i, j}, max{i, j}) with vertices numbered 1..V."""
        i, j = self.num[e[0]], self.num[e[1]]
        return (self.W(*e), min(i, j), max(i, j))

    def less(self, e, f):
        return self.key(e) < self.key(f)


def shorter_edge(G, i, j, k, l):
    """The book's ShorterEdge, line for line (vertices given by their numbers)."""
    V = G.V
    w = lambda a, b: G.W(V[a - 1], V[b - 1])
    if w(i, j) < w(k, l):
        return (i, j)
    if w(i, j) > w(k, l):
        return (k, l)
    if min(i, j) < min(k, l):
        return (i, j)
    if min(i, j) > min(k, l):
        return (k, l)
    if max(i, j) < max(k, l):
        return (i, j)
    return (k, l)


def components(V, F):
    par = {v: v for v in V}

    def find(x):
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x

    for (u, v) in F:
        par[find(u)] = find(v)
    return {v: find(v) for v in V}


def is_spanning_tree(G, T):
    T = list(T)
    if len(T) != len(G.V) - 1:
        return False
    c = components(G.V, T)
    return len(set(c.values())) == 1


def is_forest(V, F):
    par = {v: v for v in V}

    def find(x):
        while par[x] != x:
            x = par[x]
        return x

    for (u, v) in F:
        a, b = find(u), find(v)
        if a == b:
            return False
        par[a] = b
    return True


def all_spanning_trees(G):
    n = len(G.V)
    return [frozenset(T) for T in itertools.combinations(G.E, n - 1) if is_forest(G.V, T)]


def weight(G, T):
    return sum(G.w[norm(*e)] for e in T)


def rand_connected(n, m, wmax=None, rng=random):
    """Random connected simple graph on n vertices with m edges (a random spanning tree plus random edges);
    weights distinct (wmax=None) or from 1..wmax (ties)."""
    V = list(range(n))
    perm = V[:]
    rng.shuffle(perm)
    E = set()
    for i in range(1, n):
        E.add(norm(perm[i], perm[rng.randrange(i)]))
    allpairs = [(u, v) for u in V for v in V if u < v]
    m = min(m, len(allpairs))
    while len(E) < m:
        E.add(rng.choice(allpairs))
    E = sorted(E)
    if wmax is None:
        ws = rng.sample(range(-40, 60), len(E))
    else:
        ws = [rng.randint(1, wmax) for _ in E]
    Vord = V[:]
    rng.shuffle(Vord)
    return Graph(Vord, dict(zip(E, ws)))


# =====================================================================================================
# the page's algorithms
def count_and_label(V, F):
    """CountAndLabel: whatever-first search from every unmarked vertex of the forest (V, F)."""
    adj = {v: [] for v in V}
    for (u, v) in F:
        adj[u].append(v)
        adj[v].append(u)
    comp, count = {}, 0
    for v in V:
        if v not in comp:
            count += 1
            bag = [v]
            while bag:
                x = bag.pop()
                if x not in comp:
                    comp[x] = count
                    bag.extend(adj[x])
    return count, comp


def add_all_safe_edges(G, F, count, comp, less, trace=None):
    safe = [None] * (count + 1)
    for (u, v) in G.E:
        if comp[u] != comp[v]:
            if safe[comp[u]] is None or less((u, v), safe[comp[u]]):
                safe[comp[u]] = (u, v)
            if safe[comp[v]] is None or less((u, v), safe[comp[v]]):
                safe[comp[v]] = (u, v)
    if trace is not None:
        trace.append({i: safe[i] for i in range(1, count + 1)})
    added = 0
    for i in range(1, count + 1):
        if safe[i] is not None and safe[i] not in F:
            F.add(safe[i])
            added += 1
    return added


def boruvka(G, less=None, stop_if_stuck=False, trace=None, max_phases=10 ** 6):
    less = less or G.less
    F = set()
    count, comp = count_and_label(G.V, F)
    counts = [count]
    phases = 0
    while count > 1:
        added = add_all_safe_edges(G, F, count, comp, less, trace)
        phases += 1
        count, comp = count_and_label(G.V, F)
        counts.append(count)
        if stop_if_stuck and added == 0:
            break
        if phases > max_phases:
            break
    return F, phases, counts


def jarnik_best_first(G, s, stats=None):
    """JarníkBestFirst: a binary heap of edges keyed by (the key of) their weight."""
    inT = {s}
    T = set()
    heap = []
    ins = ext = 0
    inserted = []
    for v in G.adj[s]:
        heapq.heappush(heap, (G.key((s, v)), (s, v)))
        ins += 1
        inserted.append(norm(s, v))
    order = []
    while heap:
        _, (u, v) = heapq.heappop(heap)
        ext += 1
        order.append(norm(u, v))
        assert u in inT
        if v not in inT:
            inT.add(v)
            T.add(norm(u, v))
            for x in G.adj[v]:
                if x not in inT:
                    heapq.heappush(heap, (G.key((v, x)), (v, x)))
                    ins += 1
                    inserted.append(norm(v, x))
    if stats is not None:
        stats.update(inserts=ins, extracts=ext, order=order, inserted=inserted)
    return T


class IndexedHeap:
    """Binary heap of vertices with priorities; Insert, ExtractMin, DecreaseKey."""

    def __init__(self):
        self.h, self.pos, self.pri = [], {}, {}

    def _swap(self, i, j):
        h = self.h
        h[i], h[j] = h[j], h[i]
        self.pos[h[i]], self.pos[h[j]] = i, j

    def _up(self, i):
        while i > 0 and self.pri[self.h[(i - 1) // 2]] > self.pri[self.h[i]]:
            self._swap(i, (i - 1) // 2)
            i = (i - 1) // 2

    def _down(self, i):
        n = len(self.h)
        while True:
            c = [k for k in (2 * i + 1, 2 * i + 2) if k < n]
            if not c:
                return
            m = min(c, key=lambda k: self.pri[self.h[k]])
            if self.pri[self.h[m]] < self.pri[self.h[i]]:
                self._swap(i, m)
                i = m
            else:
                return

    def insert(self, v, p):
        self.pri[v] = p
        self.h.append(v)
        self.pos[v] = len(self.h) - 1
        self._up(len(self.h) - 1)

    def extract_min(self):
        v = self.h[0]
        self._swap(0, len(self.h) - 1)
        self.h.pop()
        del self.pos[v]
        if self.h:
            self._down(0)
        return v

    def decrease_key(self, v, p):
        assert p < self.pri[v]
        self.pri[v] = p
        self._up(self.pos[v])


class ArrayPQ:
    """Unsorted array of priorities: ExtractMin scans."""

    def __init__(self):
        self.pri, self.scans = {}, 0

    def insert(self, v, p):
        self.pri[v] = p

    def extract_min(self):
        self.scans += len(self.pri)
        v = min(self.pri, key=lambda x: self.pri[x])
        del self.pri[v]
        return v

    def decrease_key(self, v, p):
        assert p < self.pri[v]
        self.pri[v] = p


def jarnik_vertices(G, s, pq_class=IndexedHeap, stats=None, table=None):
    """JarníkInit + JarníkLoop, priorities compared by the page's key."""
    Q = pq_class()
    edge, priority = {}, {}
    ins = ext = dk = 0
    dk_per_edge = {}
    for v in G.V:
        if v == s:
            continue
        if norm(v, s) in G.w:
            edge[v] = norm(v, s)
            priority[v] = G.key((v, s))
        else:
            edge[v] = None
            priority[v] = INF
        Q.insert(v, priority[v])
        ins += 1
    if table is not None:
        table.append((None, None, dict(priority), set()))
    inT = {s}
    T = set()
    for i in range(1, len(G.V)):
        v = Q.extract_min()
        ext += 1
        inT.add(v)
        T.add(edge[v])
        dec = set()
        for u in G.adj[v]:
            if u not in inT and priority[u] > G.key((u, v)):
                edge[u] = norm(u, v)
                priority[u] = G.key((u, v))
                Q.decrease_key(u, priority[u])
                dk += 1
                dk_per_edge[norm(u, v)] = dk_per_edge.get(norm(u, v), 0) + 1
                dec.add(u)
        if table is not None:
            table.append((v, edge[v], {x: priority[x] for x in priority if x not in inT}, dec))
    if stats is not None:
        stats.update(inserts=ins, extracts=ext, dk=dk, dk_per_edge=dk_per_edge,
                     scans=getattr(Q, "scans", None))
    return T


def kruskal_labels(G, stats=None, rows=None):
    """Kruskal with the book's union-find: labels, the smaller set relabeled; on a tie v's set takes u's label."""
    Es = sorted(G.E, key=G.key)
    label, members = {}, {}
    nmake = nfind = nunion = 0
    relabel = {v: 0 for v in G.V}
    for v in G.V:
        label[v] = v
        members[v] = [v]
        nmake += 1
    F = []
    for (u, v) in Es:
        fu, fv = label[u], label[v]
        nfind += 2
        if fu != fv:
            x, y = fu, fv
            if len(members[x]) < len(members[y]):
                x, y = y, x
            moved = members.pop(y)
            for z in moved:
                label[z] = x
                relabel[z] += 1
            members[x] += moved
            nunion += 1
            F.append((u, v))
            if rows is not None:
                rows.append(((u, v), fu, fv, "add", sorted(moved), {k: sorted(m) for k, m in members.items()}))
        elif rows is not None:
            rows.append(((u, v), fu, fv, "skip", [], None))
    if stats is not None:
        stats.update(make=nmake, find=nfind, union=nunion, relabel=relabel)
    return F


class ForestUF:
    """The concept page's forest: union by rank, path compression."""

    def __init__(self):
        self.parent, self.rank = {}, {}

    def make_set(self, v):
        self.parent[v] = v
        self.rank[v] = 0

    def find(self, v):
        if self.parent[v] != v:
            self.parent[v] = self.find(self.parent[v])
        return self.parent[v]

    def union(self, u, v):
        x, y = self.find(u), self.find(v)
        if x == y:
            return
        if self.rank[x] > self.rank[y]:
            x, y = y, x
        self.parent[x] = y
        if self.rank[x] == self.rank[y]:
            self.rank[y] += 1


def kruskal_forest(G):
    Es = sorted(G.E, key=G.key)
    U = ForestUF()
    for v in G.V:
        U.make_set(v)
    F = []
    for (u, v) in Es:
        if U.find(u) != U.find(v):
            U.union(u, v)
            F.append((u, v))
    return F


def classify(G, F, less=None):
    """safe edges (edge -> list of component ids it is safe for), useless, undecided."""
    less = less or G.less
    comp = components(G.V, F)
    Fs = {norm(*e) for e in F}
    best = {}
    for e in G.E:
        a, b = comp[e[0]], comp[e[1]]
        if a != b:
            for c in (a, b):
                if c not in best or less(e, best[c]):
                    best[c] = e
    safe = {}
    for c, e in best.items():
        safe.setdefault(e, []).append(c)
    useless = {e for e in G.E if e not in Fs and comp[e[0]] == comp[e[1]]}
    undecided = {e for e in G.E if e not in Fs and e not in safe and e not in useless}
    return safe, useless, undecided


def generic(G, rng, less=None):
    """GenericMST with random choices: add a random nonempty subset of the current safe edges."""
    F = set()
    useless_seen = set()
    ok = True
    while len(set(components(G.V, F).values())) > 1:
        safe, useless, _ = classify(G, F, less)
        if not useless_seen <= useless:
            ok = False
        useless_seen = set(useless)
        es = list(safe)
        k = rng.randint(1, len(es))
        F |= set(rng.sample(es, k))
        if not is_forest(G.V, F):
            ok = False
            break
    return F, ok


# =====================================================================================================
print("== ShorterEdge is the lexicographic key")
ok = True
for trial in range(300):
    G = rand_connected(random.randint(2, 7), random.randint(1, 15), wmax=3)
    for e, f in itertools.product(G.E, repeat=2):
        i, j = G.num[e[0]], G.num[e[1]]
        k, l = G.num[f[0]], G.num[f[1]]
        if random.random() < 0.5:
            i, j = j, i
        got = shorter_edge(G, i, j, k, l)
        want = e if G.key(e) <= G.key(f) else f
        if {G.V[got[0] - 1], G.V[got[1] - 1]} != set(want):
            ok = False
    if len({G.key(e) for e in G.E}) != len(G.E):
        ok = False
check("ShorterEdge(i, j, k, l) returns the edge with the smaller key (w, min, max); keys of different edges differ "
      "(300 graphs with ties)", ok)

print("== distinct weights: every algorithm = the unique brute-force MST")
ok_unique = ok_alg = ok_ops = ok_phases = ok_halve = ok_gen = ok_scan = True
nt = 0
for trial in range(500):
    n = random.randint(2, 7)
    m = random.randint(n - 1, min(13, n * (n - 1) // 2))
    G = rand_connected(n, m)
    trees = all_spanning_trees(G)
    best = min(weight(G, T) for T in trees)
    minimizers = [T for T in trees if weight(G, T) == best]
    if len(minimizers) != 1:
        ok_unique = False
    MST = minimizers[0]
    F, phases, counts = boruvka(G)
    res = [frozenset(F), frozenset(map(lambda e: norm(*e), kruskal_labels(G))),
           frozenset(map(lambda e: norm(*e), kruskal_forest(G)))]
    for s in G.V:
        st1, st2, st3 = {}, {}, {}
        res.append(frozenset(jarnik_best_first(G, s, st1)))
        res.append(frozenset(jarnik_vertices(G, s, IndexedHeap, st2)))
        res.append(frozenset(jarnik_vertices(G, s, ArrayPQ, st3)))
        deg = len(G.adj[s])
        if not (st1["inserts"] == len(G.E) == st1["extracts"] and sorted(st1["inserted"]) == sorted(G.E)):
            ok_ops = False
        if not (st2["inserts"] == st2["extracts"] == n - 1 and st2["dk"] <= len(G.E) - deg
                and all(c == 1 for c in st2["dk_per_edge"].values())):
            ok_ops = False
        if st3["scans"] > n * n:
            ok_scan = False
    if any(r != MST for r in res):
        ok_alg = False
    if phases > math.floor(math.log2(n)) if n > 1 else phases != 0:
        ok_phases = False
    if any(counts[i] > n // 2 ** i for i in range(len(counts))):
        ok_phases = False
    if any(counts[i + 1] > counts[i] // 2 for i in range(len(counts) - 1)):
        ok_halve = False
    Fg, okg = generic(G, random)
    if not okg or frozenset(Fg) != MST:
        ok_gen = False
    nt += 1
check(f"Lemma 7.1: distinct weights give exactly one minimum spanning tree ({nt} random graphs, n <= 7)", ok_unique)
check("Borůvka, Kruskal (labels and forest), JarníkBestFirst, Jarník with a binary heap and with an array, from "
      "every start vertex, all return the brute-force MST", ok_alg)
check("Borůvka: at most floor(V/2^i) components after i phases, so at most floor(log2 V) phases", ok_phases)
# exhaustive over small V: the worst case is exactly floor(log2 V) (ceil is not reached unless V is a power of 2)
ok_worst = True
for n in range(2, 9):
    pairs = list(itertools.combinations(range(n), 2))
    worst = 0
    for tree_seed in range(60):
        rng = random.Random(1000 * n + tree_seed)
        G = rand_connected(n, rng.randint(n - 1, len(pairs)), rng=rng)
        worst = max(worst, boruvka(G)[1])
    # paths with weights making components merge in pairs as long as possible
    for perm in itertools.permutations(range(1, n)):
        P = Graph(list(range(n)), {(i, i + 1): perm[i] for i in range(n - 1)})
        worst = max(worst, boruvka(P)[1])
    if worst != math.floor(math.log2(n)):
        ok_worst = False
check("Borůvka worst case for V = 2..8 (random graphs, all weightings of the path) is exactly "
      "floor(log2 V) phases", ok_worst)
check("page states the bound floor(log2 V) and the book's ceil",
      "there are at most $\\lfloor\\log_2 V\\rfloor$ phases. (The book says $\\lceil\\log_2 V\\rceil$" in page
      and "$\\le\\lfloor\\log_2 V\\rfloor$ phases" in cmst)
check("Borůvka: every phase at least halves the number of components", ok_halve)
check("GenericMST with random nonempty sets of safe edges: F stays a forest, useless edges stay useless, ends at "
      "the MST", ok_gen)
check("JarníkBestFirst: exactly E Inserts and E ExtractMins, every edge inserted exactly once; vertex version: V-1 "
      "Inserts and ExtractMins, at most one DecreaseKey per edge, at most E - deg(s) in all", ok_ops)
check("Jarník with an unsorted array scans at most V^2 entries in its ExtractMins", ok_scan)

print("== ties broken by the key")
ok_same = ok_min = ok_pert = True
ok_multi = False
for trial in range(400):
    n = random.randint(2, 7)
    m = random.randint(n - 1, min(13, n * (n - 1) // 2))
    G = rand_connected(n, m, wmax=random.choice([1, 2, 3]))
    trees = all_spanning_trees(G)
    best = min(weight(G, T) for T in trees)
    if sum(weight(G, T) == best for T in trees) > 1:
        ok_multi = True
    # perturbed weights w + eps * rank, exactly
    rank = {e: r + 1 for r, e in enumerate(sorted(G.E, key=G.key))}
    eps = Fraction(1, len(G.V) * len(G.E) + 1)
    pw = lambda T: sum(Fraction(G.w[e]) + eps * rank[e] for e in T)
    pv = sorted(pw(T) for T in trees)
    Tstar = [T for T in trees if pw(T) == pv[0]]
    if len(Tstar) != 1 or (len(pv) > 1 and pv[0] == pv[1]):
        ok_pert = False
    Tstar = Tstar[0]
    # perturbed weights order the edges like the keys
    if sorted(G.E, key=lambda e: Fraction(G.w[e]) + eps * rank[e]) != sorted(G.E, key=G.key):
        ok_pert = False
    res = [frozenset(boruvka(G)[0]), frozenset(norm(*e) for e in kruskal_labels(G)),
           frozenset(norm(*e) for e in kruskal_forest(G))]
    for s in G.V:
        res += [frozenset(jarnik_best_first(G, s)), frozenset(jarnik_vertices(G, s)),
                frozenset(jarnik_vertices(G, s, ArrayPQ))]
    if any(r != res[0] for r in res):
        ok_same = False
    if res[0] != Tstar:
        ok_pert = False
    if weight(G, res[0]) != best:
        ok_min = False
check("with ties (weights in 1..3), some graphs have several minimum spanning trees", ok_multi)
check("with ties broken by the key, all algorithms (every start vertex) return the same tree", ok_same)
check("that tree has minimum weight for the original weights", ok_min)
check("perturbation: w + eps*rank (eps = 1/(VE+1), exact fractions) has distinct tree weights, orders the edges "
      "like the key, and its unique MST is the algorithms' tree", ok_pert)
# converse of Lemma 7.1 is false: a tree with repeated weights
Gt = Graph("abcd", {("a", "b"): 1, ("b", "c"): 1, ("c", "d"): 1})
check("Lemma 7.1's converse fails: a tree with all weights equal has exactly one (minimum) spanning tree",
      len(all_spanning_trees(Gt)) == 1 and "for instance when $G$ is itself a tree" in page)
# all weights 1: every spanning tree is minimum with weight V - 1
Gk = Graph("abcd", {(u, v): 1 for u, v in itertools.combinations("abcd", 2)})
trees = all_spanning_trees(Gk)
check("all weights 1 (K4): all 16 spanning trees are minimum, weight V - 1 = 3",
      len(trees) == 16 and all(weight(Gk, T) == 3 for T in trees))

print("== Lemmas 7.2 and 7.3")
ok_cut = ok_safe = ok_useless = True
counter_useless = False
for trial in range(300):
    n = random.randint(2, 7)
    G = rand_connected(n, random.randint(n - 1, min(13, n * (n - 1) // 2)))
    MST = min(all_spanning_trees(G), key=lambda T: weight(G, T))
    for _ in range(10):
        S = {v for v in G.V if random.random() < 0.5}
        if not S or S == set(G.V):
            continue
        cross = [e for e in G.E if (e[0] in S) != (e[1] in S)]
        e = min(cross, key=G.key)
        if e not in MST:
            ok_cut = False
    for _ in range(10):
        # arbitrary random forest of G
        es = G.E[:]
        random.shuffle(es)
        F = []
        for e in es:
            if random.random() < 0.5 and is_forest(G.V, F + [e]):
                F.append(e)
        safe, useless, _ = classify(G, F)
        if not set(safe) <= MST:
            ok_safe = False
        if useless & MST:
            counter_useless = True
        # random forest inside the MST
        Fm = [e for e in MST if random.random() < 0.5]
        safe, useless, _ = classify(G, Fm)
        if not set(safe) <= MST or (useless & MST):
            ok_useless = False
check("cut property: for random S (3000 sets), the lightest edge with exactly one endpoint in S is in the MST",
      ok_cut)
check("Lemma 7.2 for arbitrary forests: every safe edge is in the MST, whether or not F is inside the MST", ok_safe)
check("Lemma 7.3 for forests inside the MST: no useless edge is in the MST", ok_useless)
check("without the invariant, a useless edge can be an MST edge (found on random forests)", counter_useless)
ok_bridge = True
for trial in range(200):
    n = random.randint(2, 7)
    G = rand_connected(n, random.randint(n - 1, min(11, n * (n - 1) // 2)))
    trees = all_spanning_trees(G)
    for e in G.E:
        rest = [f for f in G.E if f != e]
        if len(set(components(G.V, rest).values())) > 1:  # bridge
            if not all(e in T for T in trees):
                ok_bridge = False
check("every bridge is in every spanning tree (200 random graphs)", ok_bridge)

print("== shifting and negating weights; disconnected graphs")
ok_shift = ok_max = True
for trial in range(200):
    n = random.randint(2, 7)
    G = rand_connected(n, random.randint(n - 1, min(12, n * (n - 1) // 2)))
    trees = all_spanning_trees(G)
    T0 = min(trees, key=lambda T: weight(G, T))
    c = random.randint(-50, 50)
    G2 = Graph(G.V, {e: x + c for e, x in G.w.items()})
    if min(trees, key=lambda T: weight(G2, T)) != T0 or any(weight(G2, T) != weight(G, T) + (n - 1) * c
                                                           for T in trees):
        ok_shift = False
    G3 = Graph(G.V, {e: -x for e, x in G.w.items()})
    if frozenset(boruvka(G3)[0]) != max(trees, key=lambda T: weight(G, T)):
        ok_max = False
check("adding c to every weight adds (V-1)c to every spanning tree and leaves the MST unchanged", ok_shift)
check("the MST of -w is the maximum spanning tree", ok_max)
ok_dis = ok_loop = ok_jdis = True
for trial in range(150):
    G1 = rand_connected(random.randint(1, 4), 6)
    G2 = rand_connected(random.randint(1, 4), 6)
    V = [("x", v) for v in G1.V] + [("y", v) for v in G2.V]
    w = {(("x", u), ("x", v)): G1.w[(u, v)] for (u, v) in G1.E}
    w.update({(("y", u), ("y", v)): G2.w[(u, v)] + 100 for (u, v) in G2.E})
    G = Graph(V, w)
    want = {(("x", u), ("x", v)) for (u, v) in boruvka(G1)[0]} | {(("y", u), ("y", v)) for (u, v) in boruvka(G2)[0]}
    want = {norm(*e) for e in want}
    if {norm(*e) for e in kruskal_labels(G)} != want:
        ok_dis = False
    Fb, ph, cnt = boruvka(G, stop_if_stuck=True)
    if Fb != want:
        ok_dis = False
    _, ph2, cnt2 = boruvka(G, max_phases=20)
    if ph2 <= 20:  # the book's loop would have ended
        ok_loop = False
    s = V[0]
    if {norm(*e) for e in jarnik_best_first(G, s)} != {e for e in want if e[0][0] == "x"}:
        ok_jdis = False
check("disconnected: Kruskal and Borůvka-that-stops-when-stuck return the minimum spanning forest", ok_dis)
check("disconnected: the book's Borůvka loop (while count > 1) never ends", ok_loop)
check("disconnected: Jarník spans exactly the start vertex's component", ok_jdis)
check("page states the disconnected-graph behavior",
      "Kruskal then returns a minimum spanning **forest**" in page and "never ends" in page
      and "Jarník's best-first version spans only the component of its start vertex" in page)
# the vertex version (JarníkInit/JarníkLoop as printed) on disconnected graphs: extracts priority-infinity vertices
# with edge Null and grows a new tree from each; its non-Null edges form the minimum spanning forest
ok_jv = True
for trial in range(150):
    parts = [rand_connected(random.randint(1, 4), 6) for _ in range(random.randint(2, 3))]
    V, w = [], {}
    for p, Gp in enumerate(parts):
        V += [(p, v) for v in Gp.V]
        w.update({((p, u), (p, v)): Gp.w[(u, v)] + 100 * p for (u, v) in Gp.E})
    G = Graph(V, w)
    want = {norm(*e) for e in kruskal_labels(G)}
    s = random.choice(V)
    tabd = []
    T = jarnik_vertices(G, s, table=tabd)
    nulls = sum(1 for (v, e, _, _) in tabd[1:] if e is None)  # extractions with edge Null (T is a set)
    if {e for e in T if e is not None} != want or nulls != len(parts) - 1:
        ok_jv = False
check("disconnected: the vertex version extracts one priority-infinity vertex (edge Null) per further component "
      "and its other edges are the minimum spanning forest", ok_jv)

print("== Borůvka details")
# path v1..v8 with weights 1,5,2,7,3,6,4: phases 8 -> 4 -> 2 -> 1
P8 = Graph([f"v{i}" for i in range(1, 9)], {(f"v{i}", f"v{i + 1}"): x for i, x in enumerate([1, 5, 2, 7, 3, 6, 4], 1)})
F8, ph8, cnt8 = boruvka(P8)
check("the eight-vertex path with weights 1, 5, 2, 7, 3, 6, 4 needs exactly 3 = log2 8 phases, 8 -> 4 -> 2 -> 1",
      ph8 == 3 and cnt8 == [8, 4, 2, 1] and "$1, 5, 2, 7, 3, 6, 4$" in page and r"$8\to4\to2\to1$" in page)
# triangle with equal weights: inconsistent tie-breaking makes a cycle
Gx = Graph("xyz", {("x", "y"): 1, ("y", "z"): 1, ("x", "z"): 1})
pick = {"x": ("x", "y"), "y": ("y", "z"), "z": ("x", "z")}  # each vertex's own choice
cyc = {norm(*e) for e in pick.values()}
Fk, _, _ = boruvka(Gx)
check("triangle of weight-1 edges: picks xy, yz, zx add a cycle; with keys, x and y pick xy, z picks xz: a tree",
      len(cyc) == 3 and not is_forest(Gx.V, cyc) and Fk == {("x", "y"), ("x", "z")}
      and all(classify(Gx, [])[0][e] for e in Fk))
tr = []
_ = boruvka(Gx, trace=tr)
check("triangle: the safe edges found by AddAllSafeEdges with keys are xy (for x, y) and xz (for z)",
      sorted(tr[0].values()) == [("x", "y"), ("x", "y"), ("x", "z")])

# =====================================================================================================
print("== the book's example graph")
EX = Graph("abcdefg", {("a", "b"): 8, ("a", "c"): 5, ("b", "c"): 10, ("b", "d"): 2, ("c", "d"): 3, ("b", "e"): 18,
                       ("d", "e"): 12, ("d", "f"): 30, ("c", "f"): 16, ("d", "g"): 14, ("e", "g"): 4,
                       ("f", "g"): 26})
s2 = lambda e: e[0] + e[1]
trees = all_spanning_trees(EX)
MSTX = min(trees, key=lambda T: weight(EX, T))
check("example: 7 vertices, 12 distinct weights; MST {ac, bd, cd, cf, de, eg} of weight 2+3+4+5+12+16 = 42",
      len(EX.E) == 12 and len(set(EX.w.values())) == 12 and sorted(map(s2, MSTX)) == ["ac", "bd", "cd", "cf", "de", "eg"]
      and weight(EX, MSTX) == 42 == 2 + 3 + 4 + 5 + 12 + 16 and "of weight 42" in page)
check("example: unique MST", sum(weight(EX, T) == 42 for T in trees) == 1)
# partial forest
F1 = [("b", "d"), ("c", "d"), ("c", "f"), ("e", "g")]
safe1, useless1, und1 = classify(EX, F1)
comp1 = components(EX.V, F1)
groups = {}
for v, c in comp1.items():
    groups.setdefault(c, []).append(v)
safe_names = {s2(e): sorted("".join(sorted(groups[c])) for c in cs) for e, cs in safe1.items()}
check("partial forest F = {bd, cd, cf, eg}: components {a}, {b,c,d,f}, {e,g}; ac safe for {a} and {b,c,d,f}, de "
      "for {e,g}; useless bc, df; undecided ab, be, dg, fg; F inside the MST",
      sorted("".join(sorted(g)) for g in groups.values()) == ["a", "bcdf", "eg"]
      and safe_names == {"ac": ["a", "bcdf"], "de": ["eg"]} and sorted(map(s2, useless1)) == ["bc", "df"]
      and sorted(map(s2, und1)) == ["ab", "be", "dg", "fg"] and set(F1) <= MSTX
      and "the useless edges are $bc$ and $df$, and $ab$, $be$, $dg$, $fg$ are undecided" in page)
_, uF, _ = classify(EX, [("a", "b"), ("b", "c")])
check("F = {ab, bc}: ac is useless but an MST edge", ("a", "c") in uF and ("a", "c") in MSTX
      and "for $F = \\{ab, bc\\}$ in the example, $ac$ is useless but it is an MST edge" in page)
# cut exchange
T61 = {("a", "b"), ("a", "c"), ("c", "f"), ("f", "g"), ("e", "g"), ("b", "d")}
S4 = set("abcd")
cross = sorted([e for e in EX.E if (e[0] in S4) != (e[1] in S4)], key=EX.key)


def tpath(T, s, t):
    adj = {v: [] for v in EX.V}
    for (u, v) in T:
        adj[u].append(v)
        adj[v].append(u)
    par = {s: None}
    stack = [s]
    while stack:
        x = stack.pop()
        for y in adj[x]:
            if y not in par:
                par[y] = x
                stack.append(y)
    p = [t]
    while p[-1] != s:
        p.append(par[p[-1]])
    return p[::-1]


pth = tpath(T61, "d", "e")
pe = [norm(a, b) for a, b in zip(pth, pth[1:])]
cr = [e for e in pe if (e[0] in S4) != (e[1] in S4)]
T57 = (T61 - {("c", "f")}) | {("d", "e")}
T52 = (T57 - {("a", "b")}) | {("c", "d")}
T42 = (T52 - {("f", "g")}) | {("c", "f")}
check("cut exchange: T is a spanning tree of weight 61; the edges leaving S = {a,b,c,d} are de 12, dg 14, cf 16, "
      "be 18, df 30; path d-b-a-c-f-g-e crosses at cf; T - cf + de weighs 57 = 61 - 16 + 12",
      is_spanning_tree(EX, T61) and weight(EX, T61) == 61 and [s2(e) for e in cross] == ["de", "dg", "cf", "be", "df"]
      and "".join(pth) == "dbacfge" and cr == [("c", "f")] and is_spanning_tree(EX, T57) and weight(EX, T57) == 57)
check("cut exchange: two more exchanges (cd for ab, cf for fg) give spanning trees of weight 52 and 42 = the MST",
      is_spanning_tree(EX, T52) and weight(EX, T52) == 52 and T42 == MSTX)
# MST is not a shortest path tree
pfg = tpath(MSTX, "f", "g")
check("the MST path from f to g is f c d e g of weight 16+3+12+4 = 35; the edge fg weighs 26",
      "".join(pfg) == "fcdeg" and sum(EX.W(a, b) for a, b in zip(pfg, pfg[1:])) == 35 == 16 + 3 + 12 + 4
      and EX.W("f", "g") == 26 and "$f c d e g$ of weight $16 + 3 + 12 + 4 = 35$" in page)

# Borůvka on the example
trB = []
FB, phB, cntB = boruvka(EX, trace=trB)
_, compB0 = count_and_label(EX.V, set())
picks = [s2(trB[0][compB0[v]]) for v in EX.V]
check("Borůvka on the example: 2 phases = floor(log2 7), the most for 7 vertices (7 -> 3 -> 1 at worst); phase 1 "
      "picks ac, bd, cd, bd, eg, cf, eg for a..g (5 distinct edges); then 2 components, both pick de",
      phB == 2 == math.floor(math.log2(7)) and 7 // 2 == 3 and 3 // 2 == 1 and cntB == [7, 2, 1]
      and "two phases, the most that any seven-vertex graph can need ($\\lfloor\\log_2 7\\rfloor = 2$; at worst "
          "$7\\to3\\to1$)" in page
      and picks == ["ac", "bd", "cd", "bd", "eg", "cf", "eg"] and len(set(picks)) == 5
      and sorted(set(s2(e) for e in trB[1].values())) == ["de"] and len(trB[1]) == 2 and FB == set(MSTX)
      and "pick $ac$, $bd$, $cd$, $bd$, $eg$, $cf$, $eg$ (for $a, \\ldots, g$)" in page)
_, uB, _ = classify(EX, [e for e in MSTX if e != ("d", "e")])
check("after phase 1, ab, bc and df are useless", sorted(map(s2, uB)) == ["ab", "bc", "df"])

# Jarník on the example from g
stJ = {}
TJ = jarnik_best_first(EX, "g", stJ)
added_order = []
inT = {"g"}
for e in stJ["order"]:
    if not (e[0] in inT and e[1] in inT):
        added_order.append(s2(e))
        inT |= set(e)
check("JarníkBestFirst from g: extraction order eg, de, bd, cd, ac, ab, bc, dg, cf, be, fg, df; tree edges in the "
      "order eg, de, bd, cd, ac, cf; 12 Inserts, 12 ExtractMins",
      [s2(e) for e in stJ["order"]] == ["eg", "de", "bd", "cd", "ac", "ab", "bc", "dg", "cf", "be", "fg", "df"]
      and added_order == ["eg", "de", "bd", "cd", "ac", "cf"] and stJ["inserts"] == 12 == stJ["extracts"]
      and TJ == set(MSTX) and "12 Inserts and 12 ExtractMins for 6 tree edges" in page
      and "the order $eg$, $de$, $bd$, $cd$, $ac$, then $ab$, $bc$, $dg$ (all useless, discarded), $cf$, then "
          "$be$, $fg$, $df$ (discarded)" in page)
tab = []
stV = {}
jarnik_vertices(EX, "g", IndexedHeap, stV, tab)
# parse the page's priority table
m = re.search(r"> \| step \| ExtractMin \| edge added \|.*?\n((?:> \|.*\n)+)", page)
rows = [r for r in m.group(1).splitlines() if not r.startswith("> |---")]


def cell(c):
    c = c.strip()
    bold = c.startswith("**")
    c = c.strip("*")
    if c == "$\\infty$":
        return ("inf", bold)
    if c == "—":
        return (None, bold)
    return (int(c), bold)


ok_tab = len(rows) == 7
for r, (v, e, pri, dec) in zip(rows, tab):
    cells = [c.strip() for c in r.strip("> ").strip().strip("|").split("|")]
    step, ex, ed, vals = cells[0], cells[1], cells[2], cells[3:]
    if v is None:
        ok_tab &= ex == "" and ed == ""
    else:
        ok_tab &= ex == f"${v}$" and ed == f"${s2(e)}$ ({EX.w[e]})"
    for x, c in zip("abcdef", vals):
        got = cell(c)
        if x not in pri:
            want = (None, False)
        else:
            want = ("inf" if pri[x] == INF else pri[x][0], x in dec)
        ok_tab &= got == want
check("the vertex-version priority table from s = g matches JarníkInit/JarníkLoop (values, extractions, bold = "
      "decreased in that step)", ok_tab, f"{len(rows)} rows")
check("vertex version on the example: 6 Inserts, 6 ExtractMins, 7 DecreaseKeys",
      stV["inserts"] == 6 == stV["extracts"] and stV["dk"] == 7
      and "Six Inserts, six ExtractMins and seven DecreaseKeys" in page)

# Kruskal on the example
krows = []
kst = {}
FK = kruskal_labels(EX, kst, krows)
m = re.search(r"> \| # \| edge \$uv\$ \|.*?\n((?:> \|.*\n)+)", page)
prow = [r for r in m.group(1).splitlines() if not r.startswith("> |---")]
pc = [[c.strip() for c in r.strip("> ").strip().strip("|").split("|")] for r in prow]
ok_k = len(pc) == 10
for i, (e, fu, fv, act, moved, sets) in enumerate(krows[:9]):
    c = pc[i]
    ok_k &= c[0] == str(i + 1) and c[1] == f"${s2(e)}$" and c[2] == str(EX.w[e])
    ok_k &= c[3] == f"${fu}$" and c[4] == f"${fv}$"
    if act == "skip":
        ok_k &= c[5] == "skip" and c[6] == ""
    else:
        lab = fu if fu != fv and sets is not None and fu in sets else fv
        newlab = [k for k, mm in sets.items() if moved[0] in mm][0]
        mv = " and ".join(f"${x}$" for x in moved)
        ok_k &= c[5] == f"add; {mv} take{'s' if len(moved) == 1 else ''} label ${newlab}$"
        big = sorted([(k, mm) for k, mm in sets.items() if len(mm) >= 2], key=lambda kv: (-len(kv[1]), kv[0]))
        if len(big) == 1 and len(big[0][1]) == 7:
            ok_k &= c[6] == "all seven vertices"
        else:
            want = ", ".join("$\\{" + ", ".join([k] + [x for x in mm if x != k]) + "\\}$" for k, mm in big)
            ok_k &= c[6] == want
last = pc[9]
ok_k &= last[0] == "10–12" and last[1] == "$be$, $fg$, $df$" and last[2] == "18, 26, 30" and last[5] == "skip"
ok_k &= [(s2(r[0]), r[1], r[2], r[3]) for r in krows[9:]] == [("be", "b", "b", "skip"), ("fg", "b", "b", "skip"),
                                                             ("df", "b", "b", "skip")]
check("the Kruskal table (Find values, actions, relabeled vertices, sets after) matches the labeling union-find",
      ok_k)
check("Kruskal on the example: 7 MakeSets, 24 Finds, 6 Unions; 7 relabelings, at most 2 per vertex (g twice) = "
      "floor(log2 7); MST order bd, cd, eg, ac, de, cf",
      kst["make"] == 7 and kst["find"] == 24 == 2 * 12 and kst["union"] == 6
      and sum(kst["relabel"].values()) == 7 and max(kst["relabel"].values()) == 2 == math.floor(math.log2(7))
      and [v for v, k in kst["relabel"].items() if k == 2] == ["g"]
      and [s2(e) for e in FK] == ["bd", "cd", "eg", "ac", "de", "cf"]
      and "7 MakeSets, 24 Finds and 6 Unions; 7 relabelings in all" in page)
ok_lab = True
for trial in range(300):
    n = random.randint(2, 9)
    G = rand_connected(n, random.randint(n - 1, min(20, n * (n - 1) // 2)), wmax=random.choice([None, 3]))
    st = {}
    kruskal_labels(G, st)
    if not (st["make"] == n and st["find"] == 2 * len(G.E) and st["union"] == n - 1
            and max(st["relabel"].values()) <= math.floor(math.log2(n))):
        ok_lab = False
check("Kruskal (300 random graphs): exactly V MakeSets, 2E Finds, V-1 Unions; no vertex relabeled more than "
      "floor(log2 V) times", ok_lab)
# relabeling the growing side: Theta(V^2)
n = 20
lab = {v: v for v in range(n)}
mem = {v: [v] for v in range(n)}
cost = 0
for v in range(1, n):
    x, y = lab[v], lab[0]  # Union(v, 0), always relabel the set of 0 (the big one)
    for z in mem[y]:
        lab[z] = x
        cost += 1
    mem[x] += mem.pop(y)
check("always relabeling the growing set costs 1 + 2 + ... + (V-1) = V(V-1)/2 relabelings (V = 20)",
      cost == n * (n - 1) // 2)

# comparison: the three orders
check("comparison: Borůvka adds {ac, bd, cd, cf, eg} then de; Jarník from g eg, de, bd, cd, ac, cf; Kruskal bd, "
      "cd, eg, ac, de, cf",
      "Borůvka adds $\\{ac, bd, cd, cf, eg\\}$ and then $de$; Jarník from $g$ adds $eg, de, bd, cd, ac, cf$; "
      "Kruskal adds $bd, cd, eg, ac, de, cf$" in page
      and sorted(set(picks)) == ["ac", "bd", "cd", "cf", "eg"])

# =====================================================================================================
print("== concept pages")
SQ = Graph("pqrs", {("p", "q"): 1, ("r", "s"): 2, ("p", "r"): 3, ("q", "r"): 4, ("p", "s"): 5})
tsq = all_spanning_trees(SQ)
msq = min(tsq, key=lambda T: weight(SQ, T))
krs = []
kruskal_labels(SQ, rows=krs)
stq = {}
jarnik_best_first(SQ, "s", stq)
inT = {"s"}
jord = []
for e in stq["order"]:
    if not (e[0] in inT and e[1] in inT):
        jord.append(s2(e))
        inT |= set(e)
trq = []
Fq, phq, _ = boruvka(SQ, trace=trq)
_, c0 = count_and_label(SQ.V, set())
check("MST concept example: square pqrs with diagonal pr; MST {pq, rs, pr} of weight 6; Kruskal adds pq, rs, pr "
      "and skips qr, ps; Jarník from s adds rs, pr, pq; Borůvka phase 1 pq (p, q), rs (r, s), phase 2 pr for both",
      sorted(map(s2, msq)) == ["pq", "pr", "rs"] and weight(SQ, msq) == 6
      and sum(weight(SQ, T) == 6 for T in tsq) == 1
      and [(s2(r[0]), r[3]) for r in krs] == [("pq", "add"), ("rs", "add"), ("pr", "add"), ("qr", "skip"),
                                              ("ps", "skip")]
      and jord == ["rs", "pr", "pq"] and phq == 2
      and [s2(trq[0][c0[v]]) for v in "pqrs"] == ["pq", "pq", "rs", "rs"]
      and sorted(s2(e) for e in trq[1].values()) == ["pr", "pr"]
      and "The MST is $\\{pq, rs, pr\\}$, weight 6" in cmst)
# union-find example: 8 elements, balanced rounds
label = {i: i for i in range(1, 9)}
members = {i: [i] for i in range(1, 9)}
relab = {i: 0 for i in range(1, 9)}
hist8 = [8]
for (u, v) in [(1, 2), (3, 4), (5, 6), (7, 8), (1, 3), (5, 7), (1, 5)]:
    x, y = label[u], label[v]
    if len(members[x]) < len(members[y]):
        x, y = y, x
    for z in members[y]:
        label[z] = x
        relab[z] += 1
    members[x] += members.pop(y)
    if label[8] != hist8[-1]:
        hist8.append(label[8])
U = ForestUF()
for i in range(1, 9):
    U.make_set(i)
for (u, v) in [(1, 2), (3, 4), (5, 6), (7, 8), (1, 3), (5, 7), (1, 5)]:
    U.union(u, v)
roots = {U.find(i) for i in range(1, 9)}
check("union-find example: 12 relabelings (4 per round); element 8 labeled 8, 7, 5, 1 (3 = log2 8 relabelings, the "
      "maximum); the forest ends as one tree of rank 3",
      sum(relab.values()) == 12 and hist8 == [8, 7, 5, 1] and relab[8] == 3 == max(relab.values())
      and len(roots) == 1 and U.rank[roots.pop()] == 3
      and "12 relabelings in all, and element 8 — labeled $8$, then $7$, then $5$, then $1$ — is relabeled "
          "$3 = \\log_2 8$ times" in cuf and "one tree of rank 3" in cuf)
ok_h = True
for trial in range(200):
    n = random.randint(1, 40)
    U = ForestUF()
    for i in range(n):
        U.make_set(i)
    for _ in range(random.randint(0, 2 * n)):
        U.union(random.randrange(n), random.randrange(n))
    # union by rank: rank(root) <= log2(size)
    sizes = {}
    for i in range(n):
        r = U.find(i)
        sizes[r] = sizes.get(r, 0) + 1
    if any(2 ** U.rank[r] > sz for r, sz in sizes.items()):
        ok_h = False
check("forest union-find: every root of rank r has at least 2^r elements, so heights stay <= log2 n", ok_h)
check("aliases on the MST page include the five names", all(f'"{a}"' in cmst for a in
      ["Kruskal's algorithm", "Prim's algorithm", "Jarník's algorithm", "Borůvka's algorithm", "cut property"]))

# =====================================================================================================
print("== figures")
FIG = {}
for name in ["a07-example", "a07-cut-exchange", "a07-boruvka", "a07-jarnik", "a07-kruskal"]:
    FIG[name] = read(os.path.join(FIGS, name + ".html")).strip()
    check(f"figure {name} is inlined after its marker", f"<!-- fig:{name} -->\n{FIG[name]}" in page)


def roles(html):
    out = {}
    for p, e, r in re.findall(r'data-p="(\d+)" data-e="(\w\w)" data-r="(\w+)"', html):
        out.setdefault(int(p), {}).setdefault(r, set()).add("".join(sorted(e)))
    return out


def arrows(html):
    out = {}
    for p, e, r in re.findall(r'data-p="(\d+)" data-e="(\w\w)" data-r="(\w+)"[^>]*marker-end', html):
        out.setdefault(int(p), set()).add(e)
    return out


def names(es):
    return {s2(norm(*e)) for e in es}


ALL = names(EX.E)
R = roles(FIG["a07-example"])
A = arrows(FIG["a07-example"])
check("figure a07-example: left panel = MST thick, the rest plain; right panel = F, safe ac and de, useless bc df, "
      "undecided ab be dg fg; arrows from a and c along ac and from e along de",
      R[1] == {"tree": names(MSTX), "plain": ALL - names(MSTX)}
      and R[2] == {"tree": names(F1), "safe": {"ac", "de"}, "useless": {"bc", "df"},
                   "undecided": {"ab", "be", "dg", "fg"}}
      and A[2] == {"ac", "ca", "ed"}
      and "2 + 3 + 4 + 5 + 12 + 16 = 42" in FIG["a07-example"])
R = roles(FIG["a07-cut-exchange"])
check("figure a07-cut-exchange: left T with e = de dashed and e' = cf marked; right T' = T - cf + de, cf removed; "
      "captions 61, 57, 16 - 12 = 4",
      R[1] == {"tree": names(T61 - {("c", "f")}), "e": {"de"}, "e1": {"cf"}, "plain": ALL - names(T61) - {"de"}}
      and R[2] == {"tree": names(T57), "removed": {"cf"}, "plain": ALL - names(T57) - {"cf"}}
      and "weight 61" in FIG["a07-cut-exchange"] and "weight 57" in FIG["a07-cut-exchange"]
      and "16 − 12 = 4" in FIG["a07-cut-exchange"] and "of weight 42" in FIG["a07-cut-exchange"])
R = roles(FIG["a07-boruvka"])
A = arrows(FIG["a07-boruvka"])
ph1_arrows = {v + "".join(set(e) - {v}) for v, e in ((v, trB[0][compB0[v]]) for v in EX.V)}
_, compB1 = count_and_label(EX.V, [e for e in MSTX if e != ("d", "e")])
check("figure a07-boruvka: phase 1 safe edges with an arrow from every vertex along its pick; phase 2 F + safe de "
      "(arrows from d and e) + useless ab bc df; final MST with all other edges useless",
      R[1] == {"safe": set(picks), "undecided": ALL - set(picks)} and A[1] == ph1_arrows
      and R[2] == {"tree": names(MSTX) - {"de"}, "safe": {"de"}, "useless": {"ab", "bc", "df"},
                   "undecided": {"be", "dg", "fg"}} and A[2] == {"de", "ed"}
      and R[3] == {"tree": names(MSTX), "useless": ALL - names(MSTX)})
R = roles(FIG["a07-jarnik"])
A = arrows(FIG["a07-jarnik"])
ok_fj = len(R) == 6
inT, Te = {"g"}, set()
for k, e in enumerate(["eg", "de", "bd", "cd", "ac", "cf"], 1):
    out = [x for x in EX.E if (x[0] in inT) != (x[1] in inT)]
    safe = s2(min(out, key=EX.key))
    useless = {s2(x) for x in EX.E if x[0] in inT and x[1] in inT and s2(x) not in Te}
    want = {"tree": set(Te), "safe": {safe}, "useless": useless, "undecided": ALL - Te - {safe} - useless}
    want = {r: s for r, s in want.items() if s}
    frm = safe[0] if safe[0] in inT else safe[1]
    ok_fj &= safe == e and R[k] == want and A[k] == {frm + (set(safe) - {frm}).pop()}
    inT |= set(e)
    Te.add(e)
ok_fj &= {s2(x) for x in EX.E if s2(x) not in Te} == {"ab", "bc", "dg", "be", "df", "fg"}
check("figure a07-jarnik: each panel shows T, T's safe edge (arrow out of T) and exactly the useless edges; "
      "after step 6 df and fg are useless too", ok_fj)
R = roles(FIG["a07-kruskal"])
ok_fk = len(R) == 6
Fk, skipped = set(), set()
k = 0
for (e, fu, fv, act, moved, sets) in krows:
    if act == "skip":
        skipped.add(s2(e))
        continue
    k += 1
    want = {"tree": set(Fk), "new": {s2(e)}, "useless": set(skipped),
            "undecided": ALL - Fk - {s2(e)} - skipped}
    want = {r: s for r, s in want.items() if s}
    ok_fk &= R[k] == want
    # partition text under the panel
    parts = sorted(sets.items(), key=lambda kv: (-len(kv[1]), kv[0]))
    txt = "  ".join("{" + '<tspan font-weight="700">' + lab + "</tspan>" + "".join(" " + x for x in mm if x != lab)
                    + "}" for lab, mm in parts)
    ok_fk &= txt in FIG["a07-kruskal"]
    Fk.add(s2(e))
ok_fk &= "skipped: ab (8), bc (10)" in FIG["a07-kruskal"] and "skipped: dg (14)" in FIG["a07-kruskal"]
check("figure a07-kruskal: each panel = F before the union, the added edge, the edges skipped so far; the "
      "partition text after each union (label first, bold) matches the labeling union-find", ok_fk)
check("figure captions: Borůvka 5 distinct safe edges, two phases; Jarník order; Kruskal skipped edges",
      "so 5 distinct safe edges" in FIG["a07-boruvka"]
      and "<i>eg</i>, <i>de</i>, <i>bd</i>, <i>cd</i>, <i>ac</i>, <i>cf</i>" in FIG["a07-jarnik"]
      and "<i>ab</i>, <i>bc</i>, <i>dg</i>, and after the last union <i>be</i>, <i>fg</i>, <i>df</i>"
      in FIG["a07-kruskal"])

# =====================================================================================================
print("== numbers and statements in the text")
check("floor(log2 7) = 2 as printed (twice: Borůvka phases, Kruskal relabelings); no ceil(log2 7) = 3 left",
      page.count("$\\lfloor\\log_2 7\\rfloor = 2$") == 2 and "\\lceil\\log_2 7" not in page
      and math.floor(math.log2(7)) == 2)
check("the array row is attributed to the book's Exercise 7.7",
      "unsorted array of vertex priorities (the book's Exercise 7.7)" in page)
check("log E < 2 log V because E < V^2 for simple graphs",
      all(math.log(E) < 2 * math.log(V) for V in range(2, 60) for E in range(1, V * (V - 1) // 2 + 1)))
check("page has the fixed headings 7.1-7.5 and Summary",
      all(h in page for h in ["## 7.1 Distinct edge weights", "## 7.2 The only minimum spanning tree algorithm",
                              "## 7.3 Borůvka's algorithm", "## 7.4 Jarník's (Prim's) algorithm",
                              "## 7.5 Kruskal's algorithm", "## Summary"]))

print()
if FAIL:
    print(f"{len(FAIL)} FAILED:", *FAIL, sep="\n  ")
    sys.exit(1)
print("ALL OK")
