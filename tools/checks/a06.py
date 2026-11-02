#!/usr/bin/env python3
"""Checks for every concrete claim on content/2-algorithms/06-depth-first-search.md and the concept pages
depth-first-search, topological-sort, dynamic-programming-on-dags, strongly-connected-components.

Every pseudocode block on the page is transcribed line for line (DFS with the clock, IsAcyclic, TopologicalSort,
PostProcess, LongestPath in both forms, KosarajuSharir, FindLow, Tarjan) and compared with brute force on
random directed graphs and dags with random vertex orders and random adjacency-list orders: cycles against
exhaustive reachability, topological orders against every edge, strong components against mutual reachability
from the transitive closure, longest paths against enumeration of all paths. Then every example on the pages
(the book's 16-vertex graph and dag, the weighted dag, the concept-page examples) is recomputed and compared with
the numbers, orders and tables printed on the pages and in the figures."""
import itertools
import math
import os
import random
import re
import sys

sys.setrecursionlimit(20000)
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
PAGE = os.path.join(ROOT, "content", "2-algorithms", "06-depth-first-search.md")
CONCEPTS = os.path.join(ROOT, "content", "concepts")
FIGS = os.path.join(HERE, "..", "figs")
FAIL = []
random.seed(374)
NEG = -math.inf


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAIL.append(name)


def read(path):
    return open(path, encoding="utf-8").read()


# =====================================================================================================
# graphs: dict vertex -> ordered list of out-neighbours (the adjacency list; its order is the order in which
# "for each edge v->w" considers the edges). Vertex order of the dict = order of "for all vertices v".
def graph(vertices, edges):
    G = {v: [] for v in vertices}
    for e in edges.split():
        u, v = e[0], e[1]
        G[u].append(v)
    return G


def edges_of(G):
    return [(u, v) for u in G for v in G[u]]


def rev(G):
    R = {v: [] for v in G}
    for u in G:
        for v in G[u]:
            R[v].append(u)
    return R


def shuffled(G, rng=random):
    """Same graph, random vertex order and random adjacency-list orders."""
    V = list(G)
    rng.shuffle(V)
    H = {}
    for v in V:
        nb = list(G[v])
        rng.shuffle(nb)
        H[v] = nb
    return H


def rand_digraph(n, p, loops=False, rng=random):
    G = {v: [] for v in range(n)}
    for u in range(n):
        for v in range(n):
            if (u != v or loops) and rng.random() < p:
                G[u].append(v)
    return shuffled(G, rng)


def rand_dag(n, p, rng=random):
    perm = list(range(n))
    rng.shuffle(perm)
    G = {v: [] for v in range(n)}
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < p:
                G[perm[i]].append(perm[j])
    return shuffled(G, rng)


def reach_set(G, s):
    seen, stack = {s}, [s]
    while stack:
        u = stack.pop()
        for w in G[u]:
            if w not in seen:
                seen.add(w)
                stack.append(w)
    return seen


def closure(G):
    return {v: reach_set(G, v) for v in G}


def brute_has_cycle(G):
    """Some vertex reaches itself by a path of at least one edge."""
    R = closure(G)
    return any(u in R[v] for u, v in edges_of(G))


def brute_scc(G):
    R = closure(G)
    comp = {}
    for v in G:
        comp[v] = frozenset(u for u in G if u in R[v] and v in R[u])
    return comp


def is_topological(order, G):
    pos = {v: i for i, v in enumerate(order)}
    return sorted(order, key=str) == sorted(G, key=str) and all(pos[u] < pos[v] for u, v in edges_of(G))


def comp_graph(G, comp):
    """scc(G): vertices = components, edges between different components (parallel edges collapsed)."""
    C = {}
    for v in G:
        C.setdefault(comp[v], set())
    for u, v in edges_of(G):
        if comp[u] != comp[v]:
            C[comp[u]].add(comp[v])
    return {c: sorted(C[c], key=lambda x: sorted(map(str, x))) for c in C}


# =====================================================================================================
# The page's pseudocode, transcribed.
def dfs_basic_reach(G, v):
    """DFS(v): if v is unmarked: mark v; for each edge v->w: DFS(w)."""
    marked = set()

    def DFS(v):
        if v not in marked:
            marked.add(v)
            for w in G[v]:
                DFS(w)

    DFS(v)
    return marked


class Run:
    """DFSAll(G) with the clock (Figure 6.3), recording what the page's lemmas talk about:
    pre, post, parent; for every vertex u the set of vertices that were new just before DFS(u) was called
    and the set of active vertices just after it was called; and the order in which edges are examined, with
    the state of the head when the edge is examined."""

    def __init__(self, G, order=None):
        self.G = G
        self.pre, self.post, self.parent = {}, {}, {}
        self.new_before, self.active_after = {}, {}
        self.examined = []           # (u, w, state of w when the edge is examined)
        self.calls = 0
        self.edge_looks = 0
        marked, stack = set(), []
        self.roots = []

        def state(w):
            if w not in marked:
                return "new"
            return "active" if w in stack else "finished"

        def DFS(v, clock):
            self.calls += 1
            self.new_before[v] = frozenset(x for x in G if x not in marked)
            marked.add(v)
            stack.append(v)
            self.active_after[v] = frozenset(stack)
            clock += 1
            self.pre[v] = clock
            for w in G[v]:
                self.edge_looks += 1
                self.examined.append((v, w, state(w)))
                if w not in marked:
                    self.parent[w] = v
                    clock = DFS(w, clock)
            clock += 1
            self.post[v] = clock
            stack.pop()
            return clock

        clock = 0
        for v in (order if order is not None else list(G)):
            if v not in marked:
                self.parent[v] = None
                self.roots.append(v)
                clock = DFS(v, clock)
        self.clock = clock

    def preorder(self):
        return sorted(self.G, key=self.pre.get)

    def postorder(self):
        return sorted(self.G, key=self.post.get)

    def is_ancestor(self, u, v):
        """u is an ancestor of v (u = v allowed) in the forest of parent pointers."""
        while v is not None:
            if v == u:
                return True
            v = self.parent[v]
        return False

    def classify_intervals(self, u, v):
        """The page's table: classification by the order of the active intervals."""
        P, Q = self.pre, self.post
        if P[u] < P[v] < Q[v] < Q[u]:
            return "tree" if self.parent[v] == u else "forward"
        if P[v] <= P[u] < Q[u] <= Q[v]:
            return "back"
        if Q[v] < P[u]:
            return "cross"
        return "impossible"

    def classify_states(self, u, v):
        """The book's bullets: the state of v when DFS(u) begins."""
        if v in self.new_before[u] and v != u:
            return "tree" if self.parent[v] == u else "forward"
        if v in self.active_after[u]:
            return "back"
        return "cross"


def dfsall_with_source(G, order):
    """The second wrapper: add a vertex s with edges s->v (in the wrapper's order), then DFS(s)."""
    H = {"__s__": list(order)}
    H.update({v: list(G[v]) for v in G})
    return Run(H, ["__s__"])


def is_acyclic(G, order=None):
    """IsAcyclic(G) and IsAcyclicDFS(v), Figure 6.7."""
    status = {}
    for v in G:
        status[v] = "New"

    def IsAcyclicDFS(v):
        status[v] = "Active"
        for w in G[v]:
            if status[w] == "Active":
                return False
            elif status[w] == "New":
                if IsAcyclicDFS(w) is False:
                    return False
        status[v] = "Finished"
        return True

    for v in (order if order is not None else list(G)):
        if status[v] == "New":
            if IsAcyclicDFS(v) is False:
                return False
    return True


class Cycle(Exception):
    pass


def topological_sort(G, order=None, as_printed=False):
    """TopologicalSort(G) and TopSortDFS(v, clock), Figure 6.9 (with the recursive call on w; as_printed=True
    uses the book's TopSortDFS(v, clock))."""
    V = len(G)
    S = {}
    status = {}
    for v in G:
        status[v] = "New"

    def TopSortDFS(v, clock):
        status[v] = "Active"
        for w in G[v]:
            if status[w] == "New":
                clock = TopSortDFS(v if as_printed else w, clock)
            elif status[w] == "Active":
                raise Cycle()                 # fail gracefully
        status[v] = "Finished"
        assert 1 <= clock <= V and clock not in S
        S[clock] = v
        clock = clock - 1
        return clock

    clock = V
    for v in (order if order is not None else list(G)):
        if status[v] == "New":
            clock = TopSortDFS(v, clock)
    return [S[i] for i in range(1, V + 1)]


def post_process(G, order=None):
    """PostProcess(G) / PostProcessDFS(v): returns the order in which Process(v) is called."""
    processed = []
    status = {v: "New" for v in G}

    def PostProcessDFS(v):
        status[v] = "Active"
        for w in G[v]:
            if status[w] == "New":
                PostProcessDFS(w)
            elif status[w] == "Active":
                raise Cycle()
        status[v] = "Finished"
        processed.append(v)

    for v in (order if order is not None else list(G)):
        if status[v] == "New":
            PostProcessDFS(v)
    return processed


def post_process_dag(G, order=None):
    """PostProcessDag(G) / PostProcessDagDFS(v) (marks only; the call in the wrapper is on v)."""
    processed, marked = [], set()

    def PostProcessDagDFS(v):
        marked.add(v)
        for w in G[v]:
            if w not in marked:
                PostProcessDagDFS(w)
        processed.append(v)

    for v in (order if order is not None else list(G)):
        if v not in marked:
            PostProcessDagDFS(v)
    return processed


def longest_path_memo(G, ell, s, t, as_printed=False):
    """LongestPath(v, t), memoized in a field v.LLP; `return v.LLP` outside the `if` (as_printed=True puts it
    inside, as the book prints it, so a call on an already-evaluated vertex returns nothing)."""
    LLP = {}

    def LongestPath(v, t):
        if v == t:
            return 0
        if v not in LLP:
            LLP[v] = NEG
            for w in G[v]:
                r = LongestPath(w, t)
                if r is None:
                    raise TypeError("LongestPath returned nothing")
                LLP[v] = max(LLP[v], ell[(v, w)] + r)
            if as_printed:
                return LLP[v]
        if not as_printed:
            return LLP[v]
        return None

    return LongestPath(s, t)


def longest_path_dp(G, ell, s, t, order=None):
    """LongestPath(s, t), dynamic programming: for each node v in postorder (of DFSAll(G))."""
    run = Run(G, order)
    LLP = {}
    for v in run.postorder():
        if v == t:
            LLP[v] = 0
        else:
            LLP[v] = NEG
            for w in G[v]:
                LLP[v] = max(LLP[v], ell[(v, w)] + LLP[w])     # KeyError if w not yet evaluated
    return LLP[s], LLP


def brute_longest(G, ell, s, t):
    best = NEG

    def go(v, length):
        nonlocal best
        if v == t:
            best = max(best, length)
        for w in G[v]:
            go(w, length + ell[(v, w)])

    go(s, 0)
    return best


def kosaraju_sharir(G, order=None, trace=None):
    """KosarajuSharir(G), PushPostRevDFS(v, S), LabelOneDFS(v, r), Figure 6.16. `for each edge u->v` (reversed)
    runs over the in-edges of v, in the order of the in-adjacency list rev(G)[v]."""
    IN = rev(G)
    S = []
    marked, root = set(), {}
    for v in G:
        root[v] = None
    order = order if order is not None else list(G)

    def PushPostRevDFS(v, S):
        marked.add(v)
        for u in IN[v]:
            if u not in marked:
                PushPostRevDFS(u, S)
        S.append(v)

    def LabelOneDFS(v, r):
        root[v] = r
        for w in G[v]:
            if root[w] is None:
                LabelOneDFS(w, r)

    for v in order:
        if v not in marked:
            PushPostRevDFS(v, S)
    if trace is not None:
        trace["phase1"] = list(S)
    pops, found = [], []
    while S:
        v = S.pop()
        pops.append(v)
        if root[v] is None:
            before = {x for x in G if root[x] is not None}
            LabelOneDFS(v, v)
            found.append((v, frozenset(x for x in G if root[x] is not None) - before))
    if trace is not None:
        trace["pops"], trace["found"] = pops, found
    return root


def find_low(G, order=None):
    """FindLow(G) / FindLowDFS(v), Figure 6.18."""
    marked, pre, low = set(), {}, {}
    clock = 0

    def FindLowDFS(v):
        nonlocal clock
        marked.add(v)
        clock += 1
        pre[v] = clock
        low[v] = pre[v]
        for w in G[v]:
            if w not in marked:
                FindLowDFS(w)
                low[v] = min(low[v], low[w])
            else:
                low[v] = min(low[v], pre[w])

    for v in (order if order is not None else list(G)):
        if v not in marked:
            FindLowDFS(v)
    return pre, low


def tarjan(G, order=None, trace=None):
    """Tarjan(G) / TarjanDFS(v), Figure 6.19."""
    marked, pre, low, root = set(), {}, {}, {}
    S = []
    clock = 0
    for v in G:
        root[v] = None
    emitted = []

    def TarjanDFS(v):
        nonlocal clock
        marked.add(v)
        clock += 1
        pre[v] = clock
        low[v] = pre[v]
        S.append(v)
        for w in G[v]:
            if w not in marked:
                TarjanDFS(w)
                low[v] = min(low[v], low[w])
            elif root[w] is None:
                low[v] = min(low[v], pre[w])
        if low[v] == pre[v]:
            popped = []
            while True:
                w = S.pop()
                root[w] = v
                popped.append(w)
                if w == v:
                    break
            emitted.append((v, frozenset(popped), list(popped)))

    for v in (order if order is not None else list(G)):
        if v not in marked:
            TarjanDFS(v)
    if trace is not None:
        trace.update(pre=pre, low=low, emitted=emitted)
    return root


# =====================================================================================================
print("== random graphs: DFS, intervals, classification, Lemma 6.1 ==")
GRAPHS = []
for trial in range(700):
    n = random.randint(1, 9)
    p = random.choice([0.1, 0.2, 0.3, 0.45])
    GRAPHS.append(rand_digraph(n, p))
for trial in range(500):
    GRAPHS.append(rand_dag(random.randint(1, 9), random.choice([0.2, 0.35, 0.5])))
LOOPY = [rand_digraph(random.randint(1, 7), 0.25, loops=True) for _ in range(300)]

ok = {k: True for k in ["reach", "once", "clock", "nest", "nest-anc", "classes", "class-agree", "examined",
                        "no-fourth", "lemma61", "active-path", "wrapper", "counts", "postback"]}
for G in GRAPHS:
    R = closure(G)
    run = Run(G)
    V, E = len(G), len(edges_of(G))
    for v in G:
        if dfs_basic_reach(G, v) != R[v]:
            ok["reach"] = False
    # DFS called once per vertex, every edge examined once
    if run.calls != V or run.edge_looks != E:
        ok["once"] = False
    if sorted(list(run.pre.values()) + list(run.post.values())) != list(range(1, 2 * V + 1)):
        ok["clock"] = False
    for u in G:
        for v in G:
            Iu, Iv = (run.pre[u], run.post[u]), (run.pre[v], run.post[v])
            disjoint = Iu[1] < Iv[0] or Iv[1] < Iu[0]
            u_contains_v = Iu[0] <= Iv[0] and Iv[1] <= Iu[1]
            v_contains_u = Iv[0] <= Iu[0] and Iu[1] <= Iv[1]
            if not (disjoint or u_contains_v or v_contains_u):
                ok["nest"] = False
            # Lemma 6.1: (a) ancestor <=> (b) nested <=> (c) u active just after DFS(v) is called
            #            <=> (d) path of new vertices from u to v just before DFS(u) is called
            a = run.is_ancestor(u, v)
            b = run.pre[u] <= run.pre[v] < run.post[v] <= run.post[u]
            c = u in run.active_after[v]
            newset = run.new_before[u]
            d = u in newset and v in reach_set({x: [y for y in G[x] if y in newset] for x in newset}, u)
            if not (a == b == c == d):
                ok["lemma61"] = False
            if u_contains_v != a:
                ok["nest-anc"] = False
    # active vertices form a directed path: the recursion stack is a path of tree edges
    for v in G:
        st = sorted(run.active_after[v], key=run.pre.get)
        if any(run.parent[st[i + 1]] != st[i] for i in range(len(st) - 1)) or st[-1] != v:
            ok["active-path"] = False
    counts = {"tree": 0, "forward": 0, "back": 0, "cross": 0}
    for u, v in edges_of(G):
        ci, cs = run.classify_intervals(u, v), run.classify_states(u, v)
        if ci == "impossible":
            ok["no-fourth"] = False
        if ci != cs:
            ok["class-agree"] = False
        counts[ci] = counts.get(ci, 0) + 1
        # u.post < v.post exactly for back edges, and then v reaches u
        if (run.post[u] < run.post[v]) != (ci == "back") or (ci == "back" and u not in R[v]):
            ok["postback"] = False
    # classification by the state of w when the edge v->w is examined: new -> tree, active -> back,
    # finished -> forward or cross
    for u, v, st in run.examined:
        cls = run.classify_intervals(u, v)
        want = {"new": {"tree"}, "active": {"back"}, "finished": {"forward", "cross"}}[st]
        if cls not in want:
            ok["examined"] = False
    if counts["tree"] != V - len(run.roots):
        ok["counts"] = False
    # second wrapper (added source s): same intervals shifted by one, trees = children of s
    order = list(G)
    run2 = dfsall_with_source(G, order)
    if any(run2.pre[v] != run.pre[v] + 1 or run2.post[v] != run.post[v] + 1 for v in G) or \
            [v for v in G if run2.parent[v] == "__s__"] != run.roots:
        ok["wrapper"] = False
check("DFS(v) from scratch marks exactly reach(v) (1200 random graphs, every start vertex)", ok["reach"])
check("DFSAll calls DFS once per vertex and examines every edge once: O(V + E)", ok["once"])
check("the clock assigns pre and post the values 1, ..., 2V, each once", ok["clock"])
check("active intervals are disjoint or nested", ok["nest"])
check("[u.pre, u.post] contains [v.pre, v.post] iff u is an ancestor of v", ok["nest-anc"])
check("Lemma 6.1: (a) ancestor <=> (b) u.pre <= v.pre < v.post <= u.post <=> (c) u active just after DFS(v) "
      "is called <=> (d) path of new vertices from u to v just before DFS(u) is called", ok["lemma61"])
check("the active vertices always form a directed path of tree edges ending at the current vertex", ok["active-path"])
check("no edge u->v has u.post < v.pre (the fourth ordering is impossible)", ok["no-fourth"])
check("classification by intervals = classification by the state of v when DFS(u) begins", ok["class-agree"])
check("state of w when v->w is examined: new -> tree, active -> back, finished -> forward or cross", ok["examined"])
check("number of tree edges = V - number of DFS trees", ok["counts"])
check("u.post < v.post for an edge u->v iff it is a back edge, and then v reaches u", ok["postback"])
check("wrapper with an added source s: same pre/post (shifted by 1), DFS trees = children of s", ok["wrapper"])

# self-loops are back edges
okl = True
for G in LOOPY:
    run = Run(G)
    for u, v in edges_of(G):
        if u == v and run.classify_intervals(u, v) != "back":
            okl = False
check("a loop u->u is classified as a back edge (300 graphs with loops)", okl)

# DFSAll on a directed path: between 1 and V trees depending on the wrapper order
P5 = {i: ([i + 1] if i < 4 else []) for i in range(5)}
check("path 0->1->2->3->4: DFSAll finds 1 tree in order 0..4 and 5 trees in order 4..0",
      len(Run(P5, [0, 1, 2, 3, 4]).roots) == 1 and len(Run(P5, [4, 3, 2, 1, 0]).roots) == 5)

# =====================================================================================================
print("\n== cycles and dags ==")
okc = {"isacyc": True, "back": True, "post": True, "srcsnk": True, "dagscc": True, "looppost": True}
for G in GRAPHS + LOOPY:
    loopfree = not any(u == v for u, v in edges_of(G))
    cyc = brute_has_cycle(G)
    for _ in range(3):
        H = shuffled(G)
        if is_acyclic(H) != (not cyc):
            okc["isacyc"] = False
        run = Run(H)
        back = any(run.classify_intervals(u, v) == "back" for u, v in edges_of(H))
        if back != cyc:
            okc["back"] = False
        if loopfree and any(run.post[u] < run.post[v] for u, v in edges_of(H)) != cyc:
            okc["post"] = False
        if any(run.post[u] <= run.post[v] for u, v in edges_of(H)) != cyc:
            okc["looppost"] = False
    if not cyc and G:
        src = [v for v in G if all(v not in G[u] for u in G)]
        snk = [v for v in G if not G[v]]
        if not src or not snk:
            okc["srcsnk"] = False
    if not any(u == v for u, v in edges_of(G)):
        comp = brute_scc(G)
        if (not cyc) != all(len(comp[v]) == 1 for v in G):
            okc["dagscc"] = False
check("IsAcyclic (Figure 6.7) = no cycle by brute force (random vertex and edge orders, loops included)",
      okc["isacyc"])
check("G has a cycle iff the DFS finds a back edge (any DFS)", okc["back"])
check("loop-free G has a cycle iff some edge u->v has u.post < v.post", okc["post"])
check("with loops allowed: G has a cycle iff some edge u->v has u.post <= v.post", okc["looppost"])
check("every nonempty dag has a source and a sink", okc["srcsnk"])
check("loop-free G is a dag iff every strong component is a single vertex", okc["dagscc"])

# =====================================================================================================
print("\n== topological sort ==")
DAGS = [G for G in GRAPHS if not brute_has_cycle(G)]
okt = {"revpost": True, "explicit": True, "pp": True, "ppdag": True, "fail": True, "printed": True,
       "revtopo": True, "allpost": True}
for G in DAGS:
    for _ in range(3):
        H = shuffled(G)
        run = Run(H)
        if not is_topological(run.postorder()[::-1], H):
            okt["revpost"] = False
        if any(run.post[u] <= run.post[v] for u, v in edges_of(H)):
            okt["revpost"] = False
        S = topological_sort(H)
        if not is_topological(S, H) or S != run.postorder()[::-1]:
            okt["explicit"] = False
        if post_process(H) != run.postorder() or not is_topological(post_process(H)[::-1], H):
            okt["pp"] = False
        if post_process_dag(H) != run.postorder():
            okt["ppdag"] = False
    H = shuffled(G)
    deeper = len(Run(H).roots) < len(H)          # some DFS call reaches a new vertex
    try:
        topological_sort(H, as_printed=True)
        loops_forever = False
    except RecursionError:
        loops_forever = True
    if loops_forever != deeper:
        okt["printed"] = False
P2 = graph("ab", "ab")
try:
    topological_sort(P2, as_printed=True)
    p2_forever = False
except RecursionError:
    p2_forever = True
for G in GRAPHS:
    if brute_has_cycle(G):
        try:
            topological_sort(G)
            okt["fail"] = False
        except Cycle:
            pass
check("for a dag, u.post > v.post for every edge u->v, so reverse postorder is a topological order "
      "(random orders)", okt["revpost"])
check("TopologicalSort (Figure 6.9, recursive call on w) writes S[V], ..., S[1] = reverse postorder, "
      "a topological order", okt["explicit"])
check("TopologicalSort fails gracefully (finds an active vertex) exactly on graphs with cycles", okt["fail"])
check("as printed, TopSortDFS(v, clock) recurses on v forever as soon as it meets an edge to a new vertex "
      "(e.g. the one-edge dag a->b, a first)", okt["printed"] and p2_forever)
check("PostProcess and PostProcessDag call Process in postorder = reverse topological order", okt["pp"] and okt["ppdag"])


def all_topological_orders(G):
    V = list(G)
    return [p for p in itertools.permutations(V) if is_topological(list(p), G)]


small = [G for G in DAGS if len(G) <= 6][:150]
for G in small:
    T = set(all_topological_orders(G))
    TR = set(all_topological_orders(rev(G)))
    if TR != {t[::-1] for t in T}:
        okt["revtopo"] = False
    # every reverse topological order is the postorder of the DFSAll run whose wrapper takes the vertices in
    # that order; so for a dag the postorders are exactly the reverse topological orders
    for t in T:
        if Run(G, list(t[::-1])).postorder() != list(t[::-1]):
            okt["allpost"] = False
check("topological orders of rev(G) = reversals of topological orders of G (150 small dags, all orders)",
      okt["revtopo"])
check("every reverse topological order of a dag is a postorder (wrapper visits the vertices in that order)",
      okt["allpost"])

# =====================================================================================================
print("\n== memoization is depth-first search; longest paths in dags ==")


def edit_memo_order(A, B):
    """Memoized Edit(i, j) with recursive calls in the order (i, j-1), (i-1, j), (i-1, j-1); returns the
    order in which values are finalized."""
    memo, fin = {}, []

    def Edit(i, j):
        if (i, j) in memo:
            return memo[(i, j)]
        if j == 0:
            val = i
        elif i == 0:
            val = j
        else:
            val = min(Edit(i, j - 1) + 1, Edit(i - 1, j) + 1, Edit(i - 1, j - 1) + (A[i - 1] != B[j - 1]))
        memo[(i, j)] = val
        fin.append((i, j))
        return val

    return Edit(len(A), len(B)), fin, memo


def edit_dep_graph(m, n):
    D = {}
    for i in range(m + 1):
        for j in range(n + 1):
            D[(i, j)] = [] if i == 0 or j == 0 else [(i, j - 1), (i - 1, j), (i - 1, j - 1)]
    return D


okm = {"memo=dfs": True, "rowmajor": True, "dag": True, "sp": True}
for trial in range(200):
    A = "".join(random.choice("ab") for _ in range(random.randint(0, 6)))
    B = "".join(random.choice("abc") for _ in range(random.randint(0, 6)))
    val, fin, memo = edit_memo_order(A, B)
    D = edit_dep_graph(len(A), len(B))
    run = Run(D, [(len(A), len(B))])
    reached = sorted(run.post, key=run.post.get)
    if fin != reached:
        okm["memo=dfs"] = False
    if brute_has_cycle(D):
        okm["dag"] = False
    rowmajor = [(i, j) for i in range(len(A) + 1) for j in range(len(B) + 1)]
    if not is_topological(rowmajor[::-1], D):
        okm["rowmajor"] = False
    # edit distance = shortest path from (m, n) to (0, 0) in the dependency dag with weights 1, 1, [A[i] != B[j]]
    ell = {}
    for (i, j), out in D.items():
        for w in out:
            ell[((i, j), w)] = 1 if w != (i - 1, j - 1) else int(A[i - 1] != B[j - 1])
    # the page's grid dag: (i,j)->(i,j-1) and (i,j)->(i-1,j) of weight 1 wherever both ends exist,
    # (i,j)->(i-1,j-1) of weight [A[i] != B[j]] for i, j >= 1
    D = {}
    ell = {}
    for i in range(len(A) + 1):
        for j in range(len(B) + 1):
            D[(i, j)] = []
            if j > 0:
                D[(i, j)].append((i, j - 1)); ell[((i, j), (i, j - 1))] = 1
            if i > 0:
                D[(i, j)].append((i - 1, j)); ell[((i, j), (i - 1, j))] = 1
            if i > 0 and j > 0:
                D[(i, j)].append((i - 1, j - 1)); ell[((i, j), (i - 1, j - 1))] = int(A[i - 1] != B[j - 1])
    negl = {k: -x for k, x in ell.items()}
    lp, _ = longest_path_dp(D, negl, (len(A), len(B)), (0, 0))
    if -lp != val:
        okm["sp"] = False
check("memoized Edit(i, j) finalizes subproblems in exactly the postorder of a DFS of its dependency graph "
      "(200 random string pairs)", okm["memo=dfs"])
check("the edit-distance dependency graph is a dag; row-major order is a reverse topological order",
      okm["dag"] and okm["rowmajor"])
check("edit distance = shortest path from (m, n) to (0, 0) in the dependency dag (weights 1, 1, [A[i] != B[j]])",
      okm["sp"])

okl = {"memo": True, "dp": True, "printed": True, "neg": True}
for trial in range(1500):
    n = random.randint(1, 8)
    G = rand_dag(n, random.choice([0.25, 0.4, 0.6]))
    ell = {e: random.randint(-5, 9) for e in edges_of(G)}
    s, t = random.choice(list(G)), random.choice(list(G))
    want = brute_longest(G, ell, s, t)
    if longest_path_memo(G, ell, s, t) != want:
        okl["memo"] = False
    for _ in range(2):
        H = shuffled(G)
        got, table = longest_path_dp(H, ell, s, t)
        if got != want:
            okl["dp"] = False
        # LLP(v) = -inf exactly when v cannot reach t
        Rt = closure(H)
        if any((table[v] == NEG) != (t not in Rt[v]) for v in H):
            okl["neg"] = False
check("memoized LongestPath(s, t) = maximum over all s-to-t paths (brute force; 1500 dags, weights -5..9)",
      okl["memo"])
check("dynamic-programming LongestPath (postorder of DFSAll) = brute force; every w.LLP read is already "
      "computed", okl["dp"])
check("LLP(v) = -infinity exactly for the vertices that cannot reach t", okl["neg"])
# the book's printed version returns nothing for a vertex evaluated earlier: s->a, s->b, a->c, b->c, c->t
DIAMOND = graph("sabct", "sa sb ac bc ct")
DL = {e: 1 for e in edges_of(DIAMOND)}
try:
    longest_path_memo(DIAMOND, DL, "s", "t", as_printed=True)
    printed_fails = False
except TypeError:
    printed_fails = True
check("as printed (return inside the if), LongestPath returns nothing on its second call on c in the diamond "
      "s->a->c, s->b->c, c->t; corrected it returns 3", printed_fails and longest_path_memo(DIAMOND, DL, "s", "t") == 3)

# =====================================================================================================
print("\n== strong components ==")
oks = {k: True for k in ["one", "sccdag", "revscc", "reach", "l62", "contig", "l63", "sinkrev", "keylemma",
                         "ks", "ksonce", "ksorder", "low", "l64", "tarjan", "tarjanorder", "tarjansink",
                         "tarjanstack", "almost"]}
tarjan_first_source_always = True
for G in GRAPHS:
    comp = brute_scc(G)
    R = closure(G)
    RR = closure(rev(G))
    for v in G:
        if comp[v] != frozenset(R[v] & RR[v]):
            oks["one"] = False
    C = comp_graph(G, comp)
    if brute_has_cycle(C):
        oks["sccdag"] = False
    Crev = comp_graph(rev(G), brute_scc(rev(G)))
    if {c: set(map(frozenset, Crev[c])) for c in Crev} != {c: set(map(frozenset, rev(C)[c])) for c in rev(C)}:
        oks["revscc"] = False
    CR = closure(C)
    if any((v in R[u]) != (comp[v] in CR[comp[u]]) for u in G for v in G):
        oks["reach"] = False
    for _ in range(2):
        H = shuffled(G)
        run = Run(H)
        for c in set(comp.values()):
            no_parent_in_c = [v for v in c if run.parent[v] not in c]
            rootc = min(c, key=run.pre.get)
            if no_parent_in_c != [rootc] or not all(run.is_ancestor(rootc, v) for v in c):
                oks["l62"] = False
            # every vertex on the tree path from the root of C to a vertex of C lies in C
            for v in c:
                x = v
                while x != rootc:
                    if x not in c:
                        oks["contig"] = False
                    x = run.parent[x]
        last = run.postorder()[-1]
        if any(comp[last] in C[c] for c in C):         # some component has an edge into comp[last]
            oks["l63"] = False
        rrun = Run(rev(H))
        lastrev = rrun.postorder()[-1]
        if C[comp[lastrev]]:                             # comp[lastrev] must be a sink of scc(G)
            oks["sinkrev"] = False
        # key lemma behind phase 2: an edge of G from C to C' means some vertex of C' finishes after every vertex
        # of C in the DFS of rev(G)
        for c in C:
            for c2 in C[c]:
                if not max(rrun.post[v] for v in c2) > max(rrun.post[v] for v in c):
                    oks["keylemma"] = False
        tr = {}
        root = kosaraju_sharir(H, trace=tr)
        if any(comp[v] != frozenset(u for u in H if root[u] == root[v]) or root[v] not in comp[v] for v in H):
            oks["ks"] = False
        if [c for _, c in tr["found"]] != list(dict.fromkeys(comp[r] for r, _ in tr["found"])) or \
                any(c != comp[r] for r, c in tr["found"]):
            oks["ksonce"] = False
        # components are found sinks first: every edge of scc(G) goes from a later-found to an earlier-found one
        idx = {c: i for i, (_, c) in enumerate(tr["found"])}
        if any(idx[c] <= idx[c2] for c in C for c2 in C[c]):
            oks["ksorder"] = False
        # FindLow computes low(v) as defined; Lemma 6.4
        pre, low = find_low(H)
        run3 = Run(H)
        # FindLow's clock counts starts only (pre = 1..V), in the same order as DFSAll's starting times
        if sorted(H, key=pre.get) != run3.preorder():
            oks["low"] = False
        for v in H:
            desc = [x for x in H if run3.is_ancestor(v, x)]
            cand = [pre[v]] + [pre[y] for x in desc for y in H[x] if run3.parent[y] != x]
            if low[v] != min(cand):
                oks["low"] = False
            is_root_sink = (min(comp[v], key=run3.pre.get) == v) and not C[comp[v]]
            cond = low[v] == pre[v] and all(low[x] < pre[x] for x in desc if x != v)
            if is_root_sink != cond:
                oks["l64"] = False
        tt = {}
        root = tarjan(H, trace=tt)
        if any(comp[v] != frozenset(u for u in H if root[u] == root[v]) or root[v] != min(comp[v], key=tt["pre"].get)
               for v in H):
            oks["tarjan"] = False
        idx = {c: i for i, (_, c, _) in enumerate(tt["emitted"])}
        if any(idx[c] <= idx[c2] for c in C for c2 in C[c]):
            oks["tarjanorder"] = False
        first = tt["emitted"][0][1] if tt["emitted"] else None
        if first is not None and C[first]:
            oks["tarjansink"] = False
        if first is not None and any(first in C[c] for c in C):
            tarjan_first_source_always = False
        # the popped vertices are the top of the stack and the deepest of them is v
        if any(popped[-1] != v for v, _, popped in tt["emitted"]):
            oks["tarjanstack"] = False
    # the almost-algorithm of Figure 6.15, with the magic done by brute force
    Hrem = {v: list(G[v]) for v in G}
    label, count = {}, 0
    while Hrem:
        count += 1
        Cr = brute_scc(Hrem)
        sinkv = next(v for v in Hrem if all(w in Cr[v] for x in Cr[v] for w in Hrem[x]))
        Cset = reach_set(Hrem, sinkv)
        for w in Cset:
            label[w] = count
        Hrem = {v: [w for w in Hrem[v] if w not in Cset] for v in Hrem if v not in Cset}
    if any((label[u] == label[v]) != (comp[u] == comp[v]) for u in G for v in G):
        oks["almost"] = False
check("strong component of v = reach(v) ∩ reach^-1(v), reach^-1 by searching rev(G)", oks["one"])
check("scc(G) is a dag (1200 random graphs)", oks["sccdag"])
check("rev(scc(G)) = scc(rev(G))", oks["revscc"])
check("u reaches v in G iff S(u) reaches S(v) in scc(G)", oks["reach"])
check("Lemma 6.2: each strong component has exactly one vertex without a parent in it — its earliest-starting "
      "vertex, an ancestor of all of it", oks["l62"])
check("tree paths from the root of a component to its vertices stay inside the component", oks["contig"])
check("Lemma 6.3: the last vertex of any postordering of G lies in a source component", oks["l63"])
check("the last vertex of a postordering of rev(G) lies in a sink component of G", oks["sinkrev"])
check("edge of G from component C to C': in the DFS of rev(G), some vertex of C' finishes after all of C",
      oks["keylemma"])
check("KosarajuSharir (Figure 6.16) labels every vertex with a vertex of its own strong component, equal labels "
      "iff same component", oks["ks"])
check("Kosaraju-Sharir: each LabelOneDFS call from phase 2 labels exactly one strong component", oks["ksonce"])
check("Kosaraju-Sharir finds the components sinks first (a reverse topological order of scc(G))", oks["ksorder"])
check("FindLow (Figure 6.18) computes low(v) as defined (min start time over tree paths + one non-tree edge)",
      oks["low"])
check("Lemma 6.4: v is the root of a sink component iff low(v) = v.pre and low(w) < w.pre for every proper "
      "descendant w", oks["l64"])
check("Tarjan (Figure 6.19) labels every vertex with the earliest-starting vertex of its component", oks["tarjan"])
check("Tarjan emits the components in reverse topological order of scc(G); the first one is a sink",
      oks["tarjanorder"] and oks["tarjansink"])
check("Tarjan's first component need not be a source component (so 'source' on book p. 242 should be 'sink')",
      not tarjan_first_source_always)
check("when v.low = v.pre, popping down to v pops exactly v's component, v deepest", oks["tarjanstack"])
check("the almost-algorithm of Figure 6.15 (sink vertex by magic) labels the strong components", oks["almost"])

# the first vertex of a postorder need not lie in a sink component: a->b, b->a, a->c, DFS from a, b first
T3 = graph("abc", "ab ba ac")
r3 = Run(T3)
comp3 = brute_scc(T3)
check("a->b, b->a, a->c from a with b first: postorder b c a; b's component {a, b} is not a sink (edge a->c)",
      "".join(r3.postorder()) == "bca" and comp3["b"] == frozenset("ab") and "c" in T3["a"])

# more random-graph claims made on the page
okx = {"wfs2": True, "sym": True, "order": True, "sc": True}
for G in GRAPHS[:600]:
    comp = brute_scc(G)
    # phase 2 may be any whatever-first search: breadth-first labeling gives the same partition
    IN = rev(G)
    run_rev = Run(IN)
    stack = run_rev.postorder()
    root = {v: None for v in G}
    while stack:
        v = stack.pop()
        if root[v] is None:
            queue = [v]
            root[v] = v
            while queue:
                x = queue.pop(0)
                for w in G[x]:
                    if root[w] is None:
                        root[w] = v
                        queue.append(w)
    if any(comp[v] != frozenset(u for u in G if root[u] == root[v]) for v in G):
        okx["wfs2"] = False
    # symmetric version: phase 1 on G, phase 2 on rev(G) (= Kosaraju-Sharir run on rev(G))
    root2 = kosaraju_sharir(rev(G))
    if any(comp[v] != frozenset(u for u in G if root2[u] == root2[v]) for v in G):
        okx["sym"] = False
    # order the components topologically, vertices inside arbitrarily: backward edges stay inside components
    C = comp_graph(G, comp)
    corder = topological_sort(C)
    vorder = [v for c in corder for v in sorted(c, key=str)]
    pos = {v: i for i, v in enumerate(vorder)}
    if any(pos[u] > pos[v] and comp[u] != comp[v] for u, v in edges_of(G)):
        okx["order"] = False
    # strongly connected iff a search of G and of rev(G) from one vertex both reach everything
    if G:
        v0 = next(iter(G))
        if (len(set(comp.values())) == 1) != (reach_set(G, v0) == set(G) == reach_set(IN, v0)):
            okx["sc"] = False
check("Kosaraju-Sharir with a breadth-first second phase gives the same components", okx["wfs2"])
check("symmetric Kosaraju-Sharir (phase 1 on G, phase 2 on rev(G)) gives the same components", okx["sym"])
check("vertices ordered by a topological order of scc(G): every backward edge joins two vertices of one component",
      okx["order"])
check("G strongly connected iff one search of G and one of rev(G) from the same vertex reach everything", okx["sc"])

# =====================================================================================================
print("\n== the chapter page: the book's 16-vertex graph ==")
page = read(PAGE)


def seq(order):
    return "\\,".join(order)


def on_page(s, text=None):
    return s in (page if text is None else text)


G16 = graph("abcdefghijklmnop", "ab bf fg fl ga gc gk ch dc hd hl kh kl lo lp ok ef ei in jk jm mi nj no")
for v in G16:
    G16[v].sort()
r16 = Run(G16)
pre16, post16 = r16.pre, r16.post
check("book graph: 16 vertices, 24 edges; alphabetical DFSAll has preorder abfgchdlokpeinjm, postorder "
      "dkoplhcgfbamjnie (the book's Figure 6.4)",
      len(G16) == 16 and len(edges_of(G16)) == 24 and "".join(r16.preorder()) == "abfgchdlokpeinjm"
      and "".join(r16.postorder()) == "dkoplhcgfbamjnie")
cls16 = {}
for u, v in edges_of(G16):
    cls16.setdefault(r16.classify_intervals(u, v), set()).add(u + v)
check("book graph edge classes: tree 14, forward {fl, gk}, back {ga, dc, kh, kl, mi}, cross {ef, jk, no}",
      len(cls16["tree"]) == 14 and cls16["forward"] == {"fl", "gk"} and cls16["back"] == {"ga", "dc", "kh", "kl", "mi"}
      and cls16["cross"] == {"ef", "jk", "no"} and r16.roots == ["a", "e"])
ex = page[page.index("[!example] Example — the edges of the figure"):]
ex = ex[:ex.index("\n\n")]
check("page example lists exactly these forward, back and cross edges",
      all(f"${u}\\to {v}$" in ex for u, v in ["fl", "gk", "ga", "dc", "kh", "kl", "mi", "ef", "jk", "no"])
      and "14 **tree** edges" in ex and "2 **forward**" in ex and "5 **back**" in ex and "3 **cross**" in ex)
check("page: f->l has [9, 16] inside [3, 20]; e->f has f.post = 20 < 23 = e.pre",
      (pre16["l"], post16["l"], pre16["f"], post16["f"]) == (9, 16, 3, 20) and post16["f"] == 20 and pre16["e"] == 23
      and "$[9, 16]$ inside $[3, 20]$" in ex and "$f.\\mathit{post} = 20 < 23 = e.\\mathit{pre}$" in ex)
check("back edges of the book graph = edges with u.post < v.post (figure caption)",
      {u + v for u, v in edges_of(G16) if post16[u] < post16[v]} == cls16["back"])
fig1 = read(os.path.join(FIGS, "a06-dfs-forest.html"))
labels = re.findall(r">(\d+)/(\d+)</text>", fig1)
check("figure a06-dfs-forest shows the 16 pre/post labels of the traversal",
      sorted((int(a), int(b)) for a, b in labels) == sorted((pre16[v], post16[v]) for v in G16)
      and "abfgchdlokpeinjm" in fig1 and "dkoplhcgfbamjnie" in fig1
      and all(f"{k} ({len(cls16[k])})" in fig1 for k in cls16))
fig2 = read(os.path.join(FIGS, "a06-intervals.html"))
bars = re.findall(r'<rect x="([\d.]+)" y="[\d.]+" width="([\d.]+)"[^>]*fill-opacity="0.14"[^>]*/><text[^>]*>(\w)</text>', fig2)
step, x0 = 17.2, 28
okbars = len(bars) == 16
for x, w, v in bars:
    t1 = round((float(x) - x0) / step) + 1
    t2 = round((float(x) + float(w) - x0) / step) + 1
    if (t1, t2) != (pre16[v], post16[v]):
        okbars = False
check("figure a06-intervals: every bar spans [v.pre, v.post]", okbars)
comp16 = brute_scc(G16)
roots16 = sorted({min(c, key=pre16.get) for c in comp16.values()}, key=pre16.get)
check("Lemma 6.2 roots in the first figure's traversal, by starting time: a, c, p, e, i",
      roots16 == ["a", "c", "p", "e", "i"] and "the roots are $a$, $c$, $p$, $e$ and $i$" in page)

# the dag of Figures 6.6 and 6.8
D16 = graph("abcdefghijklmnop", "ab fb dc gc hc hd ga fg fl ei gk kh lh jk kl jm jn in mi no ok ol lp")
for v in D16:
    D16[v].sort()
rd = Run(D16)
srcs = [v for v in D16 if all(v not in D16[u] for u in D16)]
snks = [v for v in D16 if not D16[v]]
check("book dag: acyclic, 23 edges, sources e, f, j and sinks b, c, p (page: 'sources $e, f, j$ and the sinks $b, c, p$')",
      not brute_has_cycle(D16) and len(edges_of(D16)) == 23 and srcs == list("efj") and snks == list("bcp")
      and "sources $e, f, j$ and the sinks $b, c, p$" in page)
check("book dag: postorder b a c d h p l k o n i e g f m j, topological order j m f g e i n o k l p h d c a b "
      "(Figure 6.8), as on the page",
      "".join(rd.postorder()) == "bacdhplkoniegfmj" and is_topological(rd.postorder()[::-1], D16)
      and seq(rd.postorder()) in page and seq(rd.postorder()[::-1]) in page)

# =====================================================================================================
print("\n== the chapter page: other examples ==")
check("page: DFSAll on the path 0->...->4 gives 1 or 5 trees (checked above); claim on page",
      "the order $0, 1, 2, 3, 4$ gives one tree and the order $4, 3, 2, 1, 0$ gives five" in page)
FWD = graph("abc", "ab ac bc")
rf = Run(FWD)
check("trap dag a->b, b->c, a->c: acyclic, and a->c is a forward edge reaching the finished vertex c",
      not brute_has_cycle(FWD) and rf.classify_intervals("a", "c") == "forward"
      and ("a", "c", "finished") in rf.examined and "In the dag $a\\to b$, $b\\to c$, $a\\to c$" in page)
T6 = graph("abcdef", "ab ac bd cd de fc")
r6 = Run(T6)
pre6, post6 = r6.preorder(), r6.postorder()
posp = {v: i for i, v in enumerate(pre6)}
posr = {v: i for i, v in enumerate(pre6[::-1])}
check("trap dag a->b, a->c, b->d, c->d, d->e, f->c: preorder a b d e c f puts c before f (f->c); reversed puts e "
      "before d (d->e); reverse postorder is topological",
      "".join(pre6) == "abdecf" and posp["c"] < posp["f"] and posr["e"] < posr["d"]
      and is_topological(post6[::-1], T6) and not is_topological(pre6, T6) and not is_topological(pre6[::-1], T6)
      and "the preorder $a\\,b\\,d\\,e\\,c\\,f$ puts $c$ before $f$ although $f\\to c$" in page)

# weighted dag
WD = graph("saxbcdt", "sa sb ab ac ax bc bd cd ct dt")
W = {("s", "a"): 2, ("s", "b"): 5, ("a", "b"): 4, ("a", "c"): 3, ("a", "x"): 7, ("b", "c"): 1,
     ("b", "d"): 2, ("c", "d"): 2, ("c", "t"): 5, ("d", "t"): 4}
rw = Run(WD, ["s"])
check("weighted dag: DFS(s) postorder t d c b x a s, topological order s a x b c d t (page, figure caption)",
      "".join(rw.postorder()) == "tdcbxas" and is_topological(rw.postorder()[::-1], WD)
      and seq(rw.postorder()) in page and seq(rw.postorder()[::-1]) in page)
lp, table = longest_path_dp(WD, W, "s", "t", ["s"])
want_tab = {"t": 0, "d": 4, "c": 6, "b": 7, "x": NEG, "a": 11, "s": 13}
check("weighted dag: LLP = t 0, d 4, c 6, b 7, x -inf, a 11, s 13 (dynamic program = memoized = brute force)",
      table == want_tab and lp == 13 == longest_path_memo(WD, W, "s", "t") == brute_longest(WD, W, "s", "t"))
exw = page[page.index("[!example] Example — the dag in the figure"):]
exw = exw[:exw.index("\n\n")]
check("weighted dag example text: every max on the page evaluates as printed",
      all(s_ in exw for s_ in ["$\\textsf{LLP}(d) = 4 + 0 = 4$", "\\max\\{2 + 4,\\ 5 + 0\\} = 6",
                               "\\max\\{1 + 6,\\ 2 + 4\\} = 7", "\\max\\{4 + 7,\\ 3 + 6,\\ 7 - \\infty\\} = 11",
                               "\\max\\{2 + 11,\\ 5 + 7\\} = 13"])
      and max(2 + 4, 5 + 0) == 6 and max(1 + 6, 2 + 4) == 7 and max(4 + 7, 3 + 6) == 11 and max(2 + 11, 5 + 7) == 13)
negW = {e: -x for e, x in W.items()}
sp = -longest_path_dp(WD, negW, "s", "t", ["s"])[0]
check("weighted dag: shortest path s->a->c->t of length 10; longest path s a b c d t unique of length 13",
      sp == 10 == W[("s", "a")] + W[("a", "c")] + W[("c", "t")]
      and "$s\\to a\\to c\\to t$ of length 10" in exw)


def all_paths(G, s, t):
    out = []

    def go(v, path):
        if v == t:
            out.append(path)
        for w in G[v]:
            go(w, path + [w])

    go(s, [s])
    return out


paths = all_paths(WD, "s", "t")
lengths = sorted(sum(W[(p[i], p[i + 1])] for i in range(len(p) - 1)) for p in paths)
longest = [p for p in paths if sum(W[(p[i], p[i + 1])] for i in range(len(p) - 1)) == 13]
v, greedy = "s", ["s"]
while WD[v]:
    v = max(WD[v], key=lambda w: W[(v, w)])
    greedy.append(v)
glen = sum(W[(greedy[i], greedy[i + 1])] for i in range(len(greedy) - 1))
check("weighted dag: heaviest-edge greedy from s gives s b d t of length 11; the longest path is unique",
      "".join(greedy) == "sbdt" and glen == 11 and longest == [list("sabcdt")] and lengths[-2] < 13)
fig3 = read(os.path.join(FIGS, "a06-longest-path.html"))
boxes = re.findall(r'<text x="([\d.]+)" y="187.5" text-anchor="middle"[^>]*>([^<]+)</text>', fig3)
check("figure a06-longest-path: LLP boxes read 13, 11, −∞, 7, 6, 4, 0 under s a x b c d t",
      [b for _, b in boxes] == ["13", "11", "−∞", "7", "6", "4", "0"])

# strong components of the book graph
comps16 = sorted({"".join(sorted(c)) for c in comp16.values()})
C16 = comp_graph(G16, comp16)
cedges = {("".join(sorted(a)), "".join(sorted(b))) for a in C16 for b in C16[a]}
check("book graph: components abfg, cdhklo, e, ijmn, p; scc(G) edges e->abfg, e->ijmn, abfg->cdhklo, "
      "ijmn->cdhklo, cdhklo->p (Figure 6.13; figure a06-scc)",
      comps16 == ["abfg", "cdhklo", "e", "ijmn", "p"]
      and cedges == {("e", "abfg"), ("e", "ijmn"), ("abfg", "cdhklo"), ("ijmn", "cdhklo"), ("cdhklo", "p")})
tr = {}
root = kosaraju_sharir(G16, trace=tr)
found = [(r_, "".join(sorted(c))) for r_, c in tr["found"]]
check("Kosaraju-Sharir on the book graph: phase 1 finishes b e f g a m i n j l o k h d c p; pops p c d h k o l j "
      "n i m a g f e b (Figure 6.17), as on the page",
      "".join(tr["phase1"]) == "befgaminjlokhdcp" and "".join(tr["pops"]) == "pcdhkoljnimagfeb"
      and seq(tr["phase1"]) in page and seq(tr["pops"]) in page)
check("Kosaraju-Sharir on the book graph: roots p, c, j, a, e label {p}, {c,d,h,k,l,o}, {i,j,m,n}, {a,b,f,g}, {e}",
      found == [("p", "p"), ("c", "cdhklo"), ("j", "ijmn"), ("a", "abfg"), ("e", "e")]
      and "| root | $p$ | $c$ | $j$ | $a$ | $e$ |" in page
      and "| component | $\\{p\\}$ | $\\{c, d, h, k, l, o\\}$ | $\\{i, j, m, n\\}$ | $\\{a, b, f, g\\}$ | $\\{e\\}$ |" in page)
tt = {}
tarjan(G16, trace=tt)
# Tarjan's clock counts starts only; translate its values into the figure's starting times
tpre = tt["pre"]
by_tpre = {tpre[v]: v for v in G16}
assert sorted(G16, key=tpre.get) == r16.preorder()
low_fig = {v: pre16[by_tpre[tt["low"][v]]] for v in G16}


def table_row(text, label):
    for ln in text.splitlines():
        t = ln.lstrip("> ").strip()
        if t.startswith("|"):
            cells = [c.strip() for c in t.strip("|").split("|")]
            if cells[0] == label:
                return cells[1:]
    raise KeyError(label)


hdr = [c.strip("$") for c in table_row(page, "$v$")]
prow = [int(c) for c in table_row(page, "$v.\\mathit{pre}$")]
lrow = [int(c) for c in table_row(page, "$v.\\mathit{low}$")]
check("Tarjan table on the page: vertices in preorder, pre = the figure's starting times, low = TarjanDFS's values",
      hdr == r16.preorder() and prow == [pre16[v] for v in hdr] and lrow == [low_fig[v] for v in hdr])
emitted = [(v, "".join(sorted(c))) for v, c, _ in tt["emitted"]]
check("Tarjan on the book graph: roots a, c, p, e, i; popped {p}, {c,...,o}, {a,b,f,g}, {i,j,m,n}, {e}",
      sorted(v for v in G16 if low_fig[v] == pre16[v]) == sorted("acpei")
      and emitted == [("p", "p"), ("c", "cdhklo"), ("a", "abfg"), ("i", "ijmn"), ("e", "e")]
      and "are $a, c, p, e, i$" in page
      and "$\\{p\\}$, $\\{c, d, h, k, l, o\\}$, $\\{a, b, f, g\\}$, $\\{i, j, m, n\\}$, $\\{e\\}$" in page)
pre_fl, low_fl = find_low(G16)
check("without the root test (plain FindLow), low(e) = 3 (cross edge e->f; f.pre = 3) and e is not recognized",
      low_fl["e"] == pre_fl["f"] == 3 == pre16["f"] and low_fl["e"] != pre_fl["e"]
      and "$\\textsf{low}(e) = 3$" in page)


def find_low_printed(G):
    """FindLow as printed in Figure 6.18 (book p. 243): the second loop is nested inside the first,
    'for all v: unmark v; for all u: if u is unmarked: FindLowDFS(u)' (all vertices start unmarked)."""
    marked, pre, low = set(), {}, {}
    clock = 0

    def FindLowDFS(v):
        nonlocal clock
        marked.add(v)
        clock += 1
        pre[v] = clock
        low[v] = pre[v]
        for w in G[v]:
            if w not in marked:
                FindLowDFS(w)
                low[v] = min(low[v], low[w])
            else:
                low[v] = min(low[v], pre[w])

    for v in G:
        marked.discard(v)
        for u in G:
            if u not in marked:
                FindLowDFS(u)
    return pre, low


NEST = graph("abc", "bc cb")
pre_n, low_n = find_low_printed(NEST)
pre_c, low_c = find_low(NEST)
check("FindLow with the book's nested loops (p. 243) breaks Lemma 6.4: on a, b->c, c->b the sink component {b, c} "
      "gets no root (low < pre for both); with consecutive loops b is its root; page notes the nesting",
      all(low_n[v] < pre_n[v] for v in "bc") and low_c["b"] == pre_c["b"] and low_c["c"] < pre_c["c"]
      and "the book prints its second loop indented inside the first" in page)
check("page states the diamond for the printed LongestPath and the a->b, b->a, a->c trap",
      "the diamond $s\\to a\\to c$, $s\\to b\\to c$, $c\\to t$" in page
      and "In $G$: $a\\to b$, $b\\to a$, $a\\to c$" in page)
check("page summary/abstract numbers: clock values 1..2V; 14 = 16 - 2 tree edges", r16.clock == 32 and 14 == 16 - 2)

# =====================================================================================================
print("\n== concept pages ==")
cdfs = read(os.path.join(CONCEPTS, "depth-first-search.md"))
D5 = graph("abcde", "ab ad bc ca cd eb ed")
r5 = Run(D5)
cl5 = {u + v: r5.classify_intervals(u, v) for u, v in edges_of(D5)}
check("depth-first-search example: times a 1/8, b 2/7, c 3/6, d 4/5, e 9/10; preorder abcde, postorder dcbae",
      {v: (r5.pre[v], r5.post[v]) for v in D5} == {"a": (1, 8), "b": (2, 7), "c": (3, 6), "d": (4, 5), "e": (9, 10)}
      and "$a$ 1/8, $b$ 2/7, $c$ 3/6, $d$ 4/5, $e$ 9/10" in cdfs
      and seq(r5.preorder()) in cdfs and seq(r5.postorder()) in cdfs)
check("depth-first-search example: tree ab, bc, cd; forward ad; back ca (cycle abca, c.post 6 < 8 a.post); cross eb, ed",
      cl5 == {"ab": "tree", "bc": "tree", "cd": "tree", "ad": "forward", "ca": "back", "eb": "cross", "ed": "cross"}
      and brute_has_cycle(D5) and r5.post["c"] == 6 and r5.post["a"] == 8
      and "$c.\\mathit{post} = 6 < 8 = a.\\mathit{post}$" in cdfs)
ctop = read(os.path.join(CONCEPTS, "topological-sort.md"))
check("topological-sort example: times a 1/10, b 2/7, d 3/6, e 4/5, c 8/9, f 11/12; postorder e d b c a f; "
      "order f a c b d e; preorder a b d e c f; reversed f c e d b a",
      {v: (r6.pre[v], r6.post[v]) for v in T6} == {"a": (1, 10), "b": (2, 7), "d": (3, 6), "e": (4, 5), "c": (8, 9),
                                                   "f": (11, 12)}
      and "$a$ 1/10, $b$ 2/7, $d$ 3/6, $e$ 4/5, $c$ 8/9, $f$ 11/12" in ctop
      and seq(post6) in ctop and seq(post6[::-1]) in ctop and seq(pre6) in ctop and seq(pre6[::-1]) in ctop
      and len(edges_of(T6)) == 6)
cdag = read(os.path.join(CONCEPTS, "dynamic-programming-on-dags.md"))
A = [5, 2, 8, 6, 3, 6, 9, 7]
n = len(A)
B = [NEG] + A + [math.inf]
L = {i: [j for j in range(i + 1, n + 2) if B[i] < B[j]] for i in range(n + 2)}
ellL = {(i, j): 1 for i in L for j in L[i]}
llp0 = longest_path_dp(L, ellL, 0, n + 1)[0]
best = max(k for k in range(n + 1) for c in itertools.combinations(A, k) if all(c[i] < c[i + 1] for i in range(k - 1)))
check("dynamic-programming-on-dags LIS example: 10 vertices, 36 edges, LLP(0) = 5, LIS = 4 = brute force; 2,3,6,9 "
      "is increasing", len(L) == 10 and len(edges_of(L)) == 36 and llp0 == 5 and best == 4
      and [2, 3, 6, 9] == [A[1], A[4], A[5], A[6]] and "10 vertices and 36 edges" in cdag
      and "$\\textsf{LLP}(0) = 5$" in cdag and "the answer is 4, for example $2, 3, 6, 9$" in cdag)
oklis = True
for trial in range(400):
    n_ = random.randint(0, 9)
    A_ = [random.randint(1, 6) for _ in range(n_)]
    B_ = [NEG] + A_ + [math.inf]
    L_ = {i: [j for j in range(i + 1, n_ + 2) if B_[i] < B_[j]] for i in range(n_ + 2)}
    got = longest_path_dp(L_, {(i, j): 1 for i in L_ for j in L_[i]}, 0, n_ + 1)[0] - 1
    want = max(k for k in range(n_ + 1) for c in itertools.combinations(A_, k)
               if all(c[i] < c[i + 1] for i in range(k - 1)))
    if got != want:
        oklis = False
check("LIS = longest path from 0 to n+1 minus 1 (400 random arrays, brute force)", oklis)
cscc = read(os.path.join(CONCEPTS, "strongly-connected-components.md"))
S8 = graph("abcdefgh", "ab bc ca bd de ef fd gf gh hg")
comp8 = brute_scc(S8)
C8 = comp_graph(S8, comp8)
ce8 = {("".join(sorted(a)), "".join(sorted(b))) for a in C8 for b in C8[a]}
tr8 = {}
kosaraju_sharir(S8, trace=tr8)
check("strongly-connected-components example: components abc, def, gh; scc edges abc->def, gh->def",
      sorted({"".join(sorted(c)) for c in comp8.values()}) == ["abc", "def", "gh"]
      and ce8 == {("abc", "def"), ("gh", "def")})
check("strongly-connected-components example: phase 1 finishes b c a e h g f d; searches start at d, g, a and "
      "label def, gh, abc",
      "".join(tr8["phase1"]) == "bcaehgfd" and seq(tr8["phase1"]) in cscc
      and [(r_, "".join(sorted(c))) for r_, c in tr8["found"]] == [("d", "def"), ("g", "gh"), ("a", "abc")]
      and "starts searches of $G$ at $d$, $g$ and $a$" in cscc)

# =====================================================================================================
print()
if FAIL:
    print(f"{len(FAIL)} FAILED:", *FAIL, sep="\n  ")
    sys.exit(1)
print("ALL OK")
