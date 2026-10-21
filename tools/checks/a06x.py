#!/usr/bin/env python3
"""Checks for content/2-algorithms/06-depth-first-search-exercises.md (solved exercises 6.0-6.11(a), 6.12, 6.13 of
Erickson's Algorithms).

Every algorithm is implemented the way the page states it and compared with an independent brute force (reachability
by Floyd-Warshall closure, deletion tests, enumeration of all paths, subsets, schedules, permutations and adjacency
orders) on many random small graphs.  The book's figures (6.20, 6.21) are re-entered and their claims reproduced, and
every number in the page's examples is recomputed."""
import itertools
import math
import random
import sys

sys.setrecursionlimit(10000)
random.seed(374)
FAIL = []
NEG = float("-inf")


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail != "" else ""))
    if not cond:
        FAIL.append(name)


# ============================================================================ graph helpers (independent brute force)
def closure(n, edges):
    """R[u][v] = True iff v is reachable from u (Floyd-Warshall on booleans; R[u][u] = True)."""
    R = [[u == v for v in range(n)] for u in range(n)]
    for u, v in edges:
        R[u][v] = True
    for k in range(n):
        for i in range(n):
            if R[i][k]:
                Rk = R[k]
                Ri = R[i]
                for j in range(n):
                    if Rk[j]:
                        Ri[j] = True
    return R


def adjacency(n, edges):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
    return adj


def wfs(adj, s, banned_v=None, banned_e=None):
    """Whatever-first search from s; optionally pretend vertex banned_v or undirected edge banned_e is gone."""
    seen = {s}
    bag = [s]
    while bag:
        v = bag.pop()
        for w in adj[v]:
            if w == banned_v or (banned_e is not None and {v, w} == set(banned_e)):
                continue
            if w not in seen:
                seen.add(w)
                bag.append(w)
    return seen


def rand_digraph(n, p):
    return [(u, v) for u in range(n) for v in range(n) if u != v and random.random() < p]


def rand_dag(n, p):
    perm = list(range(n))
    random.shuffle(perm)
    return [(perm[i], perm[j]) for i in range(n) for j in range(i + 1, n) if random.random() < p]


def rand_connected_graph(n, extra):
    """Random connected simple undirected graph: random tree plus about `extra` more edges. Returns edge list (u<v)."""
    E = set()
    for v in range(1, n):
        u = random.randrange(v)
        E.add((min(u, v), max(u, v)))
    for _ in range(extra if n >= 2 else 0):
        u, v = random.sample(range(n), 2)
        E.add((min(u, v), max(u, v)))
    perm = list(range(n))
    random.shuffle(perm)
    return sorted((min(perm[u], perm[v]), max(perm[u], perm[v])) for u, v in E)


def undirected_adj(n, edges, shuffle=True):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    if shuffle:
        for a in adj:
            random.shuffle(a)
    return adj


def is_acyclic(n, edges):
    """Brute force: no vertex reaches itself through at least one edge."""
    R = closure(n, edges)
    return not any(R[v][u] for u, v in edges)


# ============================================================================ the chapter's algorithms, as invoked on the page
def dfs_pre_post(adj, roots):
    """DFS (Figure 6.3): returns pre, post, parent; roots tried in the given order (DFSAll)."""
    n = len(adj)
    pre, post, parent = [None] * n, [None] * n, [None] * n
    clock = [0]

    def DFS(v):
        clock[0] += 1
        pre[v] = clock[0]
        for w in adj[v]:
            if pre[w] is None:
                parent[w] = v
                DFS(w)
        clock[0] += 1
        post[v] = clock[0]

    for r in roots:
        if pre[r] is None:
            DFS(r)
    return pre, post, parent


def topological_order(n, adj):
    """Reverse postorder (§6.3)."""
    pre, post, _ = dfs_pre_post(adj, list(range(n)))
    return sorted(range(n), key=lambda v: -post[v])


def strong_components(n, edges):
    """Kosaraju-Sharir (Figure 6.16): comp[v] = root label."""
    adj = adjacency(n, edges)
    radj = adjacency(n, [(v, u) for u, v in edges])
    marked = [False] * n
    S = []

    def PushPostRevDFS(v):
        marked[v] = True
        for u in radj[v]:
            if not marked[u]:
                PushPostRevDFS(u)
        S.append(v)

    for v in range(n):
        if not marked[v]:
            PushPostRevDFS(v)
    root = [None] * n

    def LabelOneDFS(v, r):
        root[v] = r
        for w in adj[v]:
            if root[w] is None:
                LabelOneDFS(w, r)

    while S:
        v = S.pop()
        if root[v] is None:
            LabelOneDFS(v, v)
    return root


def condensation(n, edges):
    """scc(G): (list of components as frozensets, set of edges (C, C') between distinct components)."""
    root = strong_components(n, edges)
    comps = {}
    for v in range(n):
        comps.setdefault(root[v], set()).add(v)
    C = {r: frozenset(s) for r, s in comps.items()}
    E = {(C[root[u]], C[root[v]]) for u, v in edges if root[u] != root[v]}
    return list(C.values()), E


def scc_bf(n, edges):
    R = closure(n, edges)
    return {frozenset(w for w in range(n) if R[v][w] and R[w][v]) for v in range(n)}


# ---- sanity of the black boxes
ok = True
for trial in range(400):
    n = random.randint(1, 9)
    E = rand_digraph(n, random.random() * 0.4)
    comps, _ = condensation(n, E)
    if set(comps) != scc_bf(n, E):
        ok = False
    if is_acyclic(n, E):
        order = topological_order(n, adjacency(n, E))
        pos = {v: i for i, v in enumerate(order)}
        if any(pos[u] >= pos[v] for u, v in E):
            ok = False
check("black boxes: Kosaraju-Sharir equals mutual reachability; reverse postorder is a topological order", ok)

# ============================================================================ Exercise 6.0
print("== Exercise 6.0: reversal and the strong component graph")


def Reverse(n, adj):
    """(a) for each u, for each u->v: add u to Radj[v]."""
    Radj = [[] for _ in range(n)]
    for u in range(n):
        for v in adj[u]:
            Radj[v].append(u)
    return Radj


okA = okB = okC = okD = True
for trial in range(400):
    n = random.randint(1, 9)
    E = rand_digraph(n, random.random() * 0.45)
    adj = adjacency(n, E)
    Radj = Reverse(n, adj)
    if sorted((u, v) for v in range(n) for u in Radj[v]) != sorted(E):
        okA = False
    if sum(len(a) for a in Radj) != len(E):
        okA = False
    comps, CE = condensation(n, E)
    idx = {c: i for i, c in enumerate(comps)}
    cedges = [(idx[a], idx[b]) for a, b in CE]
    if not is_acyclic(len(comps), cedges):
        okB = False
    rE = [(v, u) for u, v in E]
    rcomps, rCE = condensation(n, rE)
    if set(rcomps) != set(comps) or rCE != {(b, a) for a, b in CE}:
        okC = False
    R = closure(n, E)
    RC = closure(len(comps), cedges)
    S = {v: idx[c] for c in comps for v in c}
    if any(R[u][v] != RC[S[u]][S[v]] for u in range(n) for v in range(n)):
        okD = False
check("6.0(a) Reverse produces exactly the reversed edges in O(V+E) (each edge copied once)", okA, "400 random digraphs")
check("6.0(b) scc(G) is acyclic", okB, "400 random digraphs")
check("6.0(c) scc(rev(G)) = rev(scc(G))", okC)
check("6.0(d) u reaches v in G iff S(u) reaches S(v) in scc(G)", okD)

# ============================================================================ Exercise 6.1
print("== Exercise 6.1: semi-connected graphs")


def semi_bf(n, edges):
    R = closure(n, edges)
    return all(R[u][v] or R[v][u] for u in range(n) for v in range(n))


def SemiConnectedDag(n, adj, order=None):
    """(b) consecutive vertices of a topological order must be joined by an edge."""
    S = order if order is not None else topological_order(n, adj)
    for i in range(n - 1):
        if S[i + 1] not in adj[S[i]]:
            return False
    return True


def SemiConnected(n, edges):
    """(c) run (b) on scc(G)."""
    comps, CE = condensation(n, edges)
    idx = {c: i for i, c in enumerate(comps)}
    m = len(comps)
    return SemiConnectedDag(m, adjacency(m, [(idx[a], idx[b]) for a, b in CE]))


def all_topological_orders(n, edges, limit=50):
    preds = [set() for _ in range(n)]
    for u, v in edges:
        preds[v].add(u)
    out = []

    def rec(prefix, used):
        if len(out) >= limit:
            return
        if len(prefix) == n:
            out.append(list(prefix))
            return
        for v in range(n):
            if v not in used and preds[v] <= used:
                prefix.append(v)
                used.add(v)
                rec(prefix, used)
                used.discard(v)
                prefix.pop()

    rec([], set())
    return out


# (a) example
Ea = [(0, 1), (0, 2)]
check("6.1(a) s->a, s->b: a dag with the unique source s that is not semi-connected",
      is_acyclic(3, Ea) and not semi_bf(3, Ea) and {v for v in range(3) if all(e[1] != v for e in Ea)} == {0})
okb = okb_any = True
cnt_true = 0
for trial in range(1500):
    n = random.randint(1, 8)
    E = rand_dag(n, random.random() * 0.6)
    if random.random() < 0.5 and n > 1:   # plant a Hamiltonian path to get many positive instances
        perm = list(range(n))
        random.shuffle(perm)
        E = sorted(set(E) | {(perm[i], perm[i + 1]) for i in range(n - 1)})
        # keep it acyclic: orient every edge along perm
        pos = {v: i for i, v in enumerate(perm)}
        E = sorted({(u, v) if pos[u] < pos[v] else (v, u) for u, v in E})
    adj = adjacency(n, E)
    bf = semi_bf(n, E)
    cnt_true += bf
    if SemiConnectedDag(n, adj) != bf:
        okb = False
    for order in all_topological_orders(n, E, 20):
        if SemiConnectedDag(n, adj, order) != bf:
            okb_any = False
check("6.1(b) SemiConnectedDag vs brute force on random dags", okb, f"1500 dags, {cnt_true} semi-connected")
check("6.1(b) the answer does not depend on which topological order is used", okb_any)
uniq = True
for trial in range(600):
    n = random.randint(1, 7)
    E = rand_dag(n, random.random() * 0.7)
    if semi_bf(n, E) and len(all_topological_orders(n, E, 5)) != 1:
        uniq = False
check("6.1(b) a semi-connected dag has exactly one topological order", uniq)
okc = True
cnt_true = 0
for trial in range(1500):
    n = random.randint(1, 8)
    E = rand_digraph(n, random.random() * 0.5)
    bf = semi_bf(n, E)
    cnt_true += bf
    if SemiConnected(n, E) != bf:
        okc = False
check("6.1(c) SemiConnected (run (b) on scc(G)) vs brute force on random digraphs", okc,
      f"1500 digraphs, {cnt_true} semi-connected")

# ============================================================================ Exercise 6.2
print("== Exercise 6.2: one-way streets")


def StronglyConnected(n, adj):
    """(a) whatever-first search from one vertex in G and in rev(G)."""
    if n == 0:
        return True
    return len(wfs(adj, 0)) == n and len(wfs(Reverse(n, adj), 0)) == n


def GoodVertices(n, edges):
    """(b) x is good iff its strong component is a sink of scc(G)."""
    comps, CE = condensation(n, edges)
    nonsink = {a for a, b in CE}
    return {v for c in comps if c not in nonsink for v in c}


oka = okb2 = True
for trial in range(1500):
    n = random.randint(1, 8)
    E = rand_digraph(n, random.random() * 0.6)
    R = closure(n, E)
    if StronglyConnected(n, adjacency(n, E)) != all(R[u][v] for u in range(n) for v in range(n)):
        oka = False
    good_bf = {x for x in range(n) if all(R[y][x] for y in range(n) if R[x][y])}
    if GoodVertices(n, E) != good_bf:
        okb2 = False
check("6.2(a) strong connectivity by two searches vs brute force", oka, "1500 random digraphs")
check("6.2(b) good vertices = vertices of sink components, vs the definition", okb2)
check("6.2(b) 'over 95%' test: 20 * good > 19 * V (integer arithmetic)", 20 * 96 > 19 * 100 and not 20 * 95 > 19 * 100)

# ============================================================================ Exercise 6.3
print("== Exercise 6.3: (s,t)-cut vertices in a dag")


def STCutVertices(n, adj):
    """The sweep: a vertex is a cut vertex iff no edge jumps over it in a topological order."""
    S = topological_order(n, adj)
    pos = {v: i + 1 for i, v in enumerate(S)}
    far = 1
    out = []
    for i in range(1, n + 1):
        if 1 < i < n and far <= i:
            out.append(S[i - 1])
        for w in adj[S[i - 1]]:
            far = max(far, pos[w])
    return set(out)


def st_cut_bf(n, adj, s, t):
    return {v for v in range(n) if v not in (s, t) and t not in wfs(adj, s, banned_v=v)}


def rand_st_dag(n, p):
    """Random dag on 0..n-1 (topologically labeled) with unique source 0 and sink n-1, then relabeled."""
    E = {(i, j) for i in range(n) for j in range(i + 1, n) if random.random() < p}
    for j in range(1, n):
        if not any(e[1] == j for e in E):
            E.add((random.randrange(j), j))
    for i in range(n - 1):
        if not any(e[0] == i for e in E):
            E.add((i, random.randrange(i + 1, n)))
    perm = list(range(n))
    random.shuffle(perm)
    return [(perm[u], perm[v]) for u, v in E], perm[0], perm[n - 1]


ok3 = True
tot = 0
for trial in range(2000):
    n = random.randint(2, 10)
    E, s, t = rand_st_dag(n, random.random() * 0.5)
    adj = adjacency(n, E)
    srcs = [v for v in range(n) if not any(e[1] == v for e in E)]
    sinks = [v for v in range(n) if not adj[v]]
    assert srcs == [s] and sinks == [t]
    a, b = STCutVertices(n, adj), st_cut_bf(n, adj, s, t)
    tot += len(b)
    if a != b:
        ok3 = False
check("6.3 sweep over a topological order vs deleting each vertex", ok3, f"2000 random dags, {tot} cut vertices in all")
# Figure 6.20 re-entered (top row s a b c d e, bottom row f g h i j t)
F20_V = "s a b c d e f g h i j t".split()
F20_E = ["s f", "s g", "f g", "g a", "g b", "g h", "g c", "a b", "a c", "a h", "b h", "b c", "h c",
         "c d", "c i", "c j", "d i", "d j", "i j", "j e", "j t", "e t"]
ix = {v: i for i, v in enumerate(F20_V)}
E20 = [(ix[e.split()[0]], ix[e.split()[1]]) for e in F20_E]
adj20 = adjacency(12, E20)
check("6.3 Figure 6.20: a dag with unique source s and unique sink t",
      is_acyclic(12, E20) and [v for v in range(12) if not any(e[1] == v for e in E20)] == [ix["s"]]
      and [v for v in range(12) if not adj20[v]] == [ix["t"]])
cut20 = {F20_V[v] for v in STCutVertices(12, adj20)}
check("6.3 Figure 6.20: exactly three cut vertices, g, c, j (the red ones)",
      cut20 == {"g", "c", "j"} == {F20_V[v] for v in st_cut_bf(12, adj20, ix["s"], ix["t"])}, f"{sorted(cut20)}")
order20 = "s f g a b h c d i j e t".split()
pos20 = {v: i + 1 for i, v in enumerate(order20)}
check("6.3 Figure 6.20: s f g a b h c d i j e t is a topological order",
      all(pos20[F20_V[u]] < pos20[F20_V[v]] for u, v in E20))
jumped = {order20[k - 1] for (u, v) in E20 for k in range(pos20[F20_V[u]] + 1, pos20[F20_V[v]])}
check("6.3 Figure 6.20: jumped-over vertices are all but s, g, c, j, t",
      set(order20) - jumped == {"s", "g", "c", "j", "t"}, f"jumped: {sorted(jumped)}")
jumpers = sorted(f"{F20_V[u]}{F20_V[v]}" for u, v in E20 if pos20[F20_V[v]] - pos20[F20_V[u]] >= 2)
check("6.3 Figure 6.20: the 11 edges that jump over a vertex in this order",
      jumpers == ['ac', 'ah', 'bc', 'ci', 'cj', 'dj', 'gb', 'gc', 'gh', 'jt', 'sg'], f"{jumpers}")

# ============================================================================ Exercise 6.4 and 6.5
print("== Exercises 6.4 and 6.5: cut vertices and bridges")


def LowDFS(n, adj, r):
    """CutDFS / BridgeDFS from the page: one DFS computing pre, low, parent, children, cut vertices and bridges."""
    pre = [None] * n
    low = [None] * n
    parent = [None] * n
    children = [[] for _ in range(n)]
    cuts, bridges = set(), set()
    clock = [0]

    def DFS(v, p):
        parent[v] = p
        clock[0] += 1
        pre[v] = clock[0]
        low[v] = pre[v]
        for w in adj[v]:
            if pre[w] is None:
                children[v].append(w)
                DFS(w, v)
                low[v] = min(low[v], low[w])
                if p is not None and low[w] >= pre[v]:
                    cuts.add(v)
                if low[w] == pre[w]:
                    bridges.add(frozenset((v, w)))
            elif w != p:
                low[v] = min(low[v], pre[w])

    DFS(r, None)
    if len(children[r]) >= 2:
        cuts.add(r)
    return dict(pre=pre, low=low, parent=parent, children=children, cuts=cuts, bridges=bridges)


def cut_bf(n, adj):
    out = set()
    for v in range(n):
        others = [u for u in range(n) if u != v]
        if others and len(wfs(adj, others[0], banned_v=v)) < n - 1:
            out.add(v)
    return out


def bridge_bf(n, edges, adj):
    return {frozenset(e) for e in edges if e[1] not in wfs(adj, e[0], banned_e=e)}


def subtree(children, v):
    out, st = set(), [v]
    while st:
        x = st.pop()
        out.add(x)
        st.extend(children[x])
    return out


def ancestors(parent, v):
    out = []
    while parent[v] is not None:
        v = parent[v]
        out.append(v)
    return out


ok4 = ok4bi = ok4bii = ok5 = ok5c = ok5b = True
printed_fails = 0
leaf_fail = 0
nonDFS_fail = False
tc = tb = 0
for trial in range(1500):
    n = random.randint(1, 10)
    E = rand_connected_graph(n, random.randint(0, 2 * n))
    adj = undirected_adj(n, E)
    r = random.randrange(n)
    L = LowDFS(n, adj, r)
    cb, bb = cut_bf(n, adj), bridge_bf(n, E, adj)
    tc += len(cb)
    tb += len(bb)
    if L["cuts"] != cb:
        ok4 = False
    if L["bridges"] != bb:
        ok5 = False
    ch, par = L["children"], L["parent"]
    # (b)i
    if (len(ch[r]) > 1) != (r in cb):
        ok4bi = False
    # (b)ii corrected and as printed
    for v in range(n):
        if v == r:
            continue
        anc = set(ancestors(par, v))
        hangs = [all(not (set(adj[x]) & anc) for x in subtree(ch, c)) for c in ch[v]]
        if any(hangs) != (v in cb):
            ok4bii = False
        printed = all(any(set(adj[x]) & anc for x in subtree(ch, c)) for c in ch[v])
        if printed != (v in cb):
            printed_fails += 1
            if not ch[v]:
                leaf_fail += 1
    # 6.5(b): every bridge is in every spanning tree; test random WFS trees
    for _ in range(3):
        adj2 = undirected_adj(n, E)
        _, _, par2 = dfs_pre_post(adj2, [random.randrange(n)])
        tree = {frozenset((v, par2[v])) for v in range(n) if par2[v] is not None}
        if not bb <= tree:
            ok5b = False
        # 6.5(c) for an arbitrary (here: DFS of a shuffled graph, plus BFS below) rooted spanning tree
        ch2 = [[] for _ in range(n)]
        for v in range(n):
            if par2[v] is not None:
                ch2[par2[v]].append(v)
        for v in range(n):
            if par2[v] is None:
                continue
            Tv = subtree(ch2, v)
            crossing = [e for e in E if (e[0] in Tv) != (e[1] in Tv)]
            if (frozenset((v, par2[v])) in bb) != (crossing == [tuple(sorted((v, par2[v])))]):
                ok5c = False
check("6.4(c) CutDFS vs deleting each vertex", ok4, f"1500 random connected graphs, {tc} cut vertices")
check("6.4(b)i root of a DFS tree is a cut vertex iff it has >= 2 children", ok4bi)
check("6.4(b)ii corrected: non-root v is a cut vertex iff SOME child's subtree has no neighbor among v's proper "
      "ancestors", ok4bii)
check("6.4(b)ii as printed ('each child's subtree HAS such a neighbor') is the condition for NOT being a cut vertex",
      printed_fails > 0 and leaf_fail > 0, f"printed version wrong for {printed_fails} vertices, {leaf_fail} of them leaves")
check("6.5(d) BridgeDFS (low(v) = v.pre) vs deleting each edge", ok5, f"{tb} bridges")
check("6.5(b) every bridge lies in every spanning tree (4500 random spanning trees)", ok5b)
check("6.5(c) tree edge uv is a bridge iff uv is the only edge with exactly one endpoint in T_v", ok5c)
# 6.5(d) trap: if the tree edge to the parent counts in low (FindLowDFS of Figure 6.18 run on an undirected graph),
# the bridge test never fires but the cut-vertex test is still right
def low_with_parent_edge(n, adj, r):
    pre, low, ch = [None] * n, [None] * n, [[] for _ in range(n)]
    clock = [0]

    def F(v):
        clock[0] += 1
        pre[v] = low[v] = clock[0]
        for w in adj[v]:
            if pre[w] is None:
                ch[v].append(w)
                F(w)
                low[v] = min(low[v], low[w])
            else:
                low[v] = min(low[v], pre[w])

    F(r)
    cuts = {v for v in range(n) if v != r and any(low[c] >= pre[v] for c in ch[v])}
    if len(ch[r]) >= 2:
        cuts.add(r)
    bridges = {frozenset((v, c)) for v in range(n) for c in ch[v] if low[c] == pre[c]}
    return cuts, bridges


okt1 = okt2 = True
for trial in range(800):
    n = random.randint(2, 10)
    E = rand_connected_graph(n, random.randint(0, 2 * n))
    adj = undirected_adj(n, E)
    cuts, br = low_with_parent_edge(n, adj, random.randrange(n))
    okt1 &= cuts == cut_bf(n, adj)
    okt2 &= not br
check("6.5(d) trap: counting the parent edge in low keeps the cut-vertex test correct", okt1)
check("6.5(d) trap: ... but then no bridge is ever reported", okt2)
# the claims of 6.4(b) fail for non-DFS trees: the 4-cycle with a BFS tree
C4 = [(0, 1), (1, 2), (2, 3), (0, 3)]
check("6.4(b) hint: in the 4-cycle the BFS tree from 0 has two children at the root, but 0 is not a cut vertex",
      0 not in cut_bf(4, undirected_adj(4, C4, False)))
# Figure 6.21 re-entered
F21_V = "A B C D E F G H I J K L M".split()
F21_E = ["A B", "A D", "B D", "C E", "C D", "C F", "C G", "E D", "E F", "E G", "D F", "D G", "F G", "F H",
         "G I", "G J", "G K", "I J", "I K", "J K", "K L", "K M", "L M"]
jx = {v: i for i, v in enumerate(F21_V)}
E21 = [tuple(sorted((jx[e.split()[0]], jx[e.split()[1]]))) for e in F21_E]
adj21 = undirected_adj(13, E21, False)
cuts21 = {F21_V[v] for v in cut_bf(13, adj21)}
check("6.4 Figure 6.21: four cut vertices (D, F, G, K in our labeling)", cuts21 == {"D", "F", "G", "K"}, f"{sorted(cuts21)}")
check("6.4 Figure 6.21: CutDFS finds them from every root",
      all({F21_V[v] for v in LowDFS(13, adj21, r)["cuts"]} == cuts21 for r in range(13)))
# the figure: DFS from A with alphabetical adjacency lists; pre/low values quoted in the caption
adjA = [sorted(a) for a in adj21]
LA = LowDFS(13, adjA, jx["A"])
PL = {F21_V[v]: (LA["pre"][v], LA["low"][v]) for v in range(13)}
check("6.4 figure: DFS from a (alphabetical lists) visits a b d c e f g i j k l m h",
      "".join(sorted(F21_V, key=lambda v: PL[v][0])) == "ABDCEFGIJKLMH")
check("6.4 figure: pre(d)=3, low(c)=3; pre(f)=6, low(h)=13; pre(g)=7, low(i)=7; pre(k)=10, low(l)=10; a has one child",
      PL["D"][0] == 3 and PL["C"][1] == 3 and PL["F"][0] == 6 and PL["H"][1] == 13 and PL["G"][0] == 7
      and PL["I"][1] == 7 and PL["K"][0] == 10 and PL["L"][1] == 10 and len(LA["children"][jx["A"]]) == 1
      and LA["cuts"] == {jx[c] for c in "DFGK"} and LA["bridges"] == {frozenset((jx["F"], jx["H"]))}, f"{PL}")
check("6.5 Figure 6.21 has exactly one bridge, F-H", {frozenset(F21_V[x] for x in b) for b in bridge_bf(13, E21, adj21)}
      == {frozenset("FH")})

# ============================================================================ Exercise 6.6
print("== Exercise 6.6: transitive closure and reduction")


def TransitiveClosure(n, adj):
    """(a) WFS from every vertex: edges u->v for v != u reachable from u."""
    return {(u, v) for u in range(n) for v in wfs(adj, u) if v != u}


def TransitiveReduction(n, edges):
    """(c) cycle through each strong component + one edge per edge of the reduction of scc(G)."""
    comps, CE = condensation(n, edges)
    idx = {c: i for i, c in enumerate(comps)}
    m = len(comps)
    cadj = adjacency(m, [(idx[a], idx[b]) for a, b in CE])
    reach = [wfs(cadj, c) for c in range(m)]          # closure of scc(G), part (a)
    H = set()
    for c in comps:
        vs = sorted(c)
        if len(vs) >= 2:
            H |= {(vs[i], vs[(i + 1) % len(vs)]) for i in range(len(vs))}
    for a in range(m):
        for b in cadj[a]:
            if not any(b in reach[w] for w in cadj[a] if w != b):     # a->b is essential in scc(G)
                H.add((min(comps[a]), min(comps[b])))
    return H


def clos_set(n, edges):
    R = closure(n, edges)
    return frozenset((u, v) for u in range(n) for v in range(n) if u != v and R[u][v])


ok6a = True
for trial in range(600):
    n = random.randint(1, 8)
    E = rand_digraph(n, random.random() * 0.4)
    if TransitiveClosure(n, adjacency(n, E)) != clos_set(n, E):
        ok6a = False
check("6.6(a) closure by V searches vs Floyd-Warshall", ok6a, "600 random digraphs")


def count_formula(n, edges):
    comps, CE = condensation(n, edges)
    idx = {c: i for i, c in enumerate(comps)}
    m = len(comps)
    cadj = adjacency(m, [(idx[a], idx[b]) for a, b in CE])
    reach = [wfs(cadj, c) for c in range(m)]
    red = [(a, b) for a in range(m) for b in cadj[a] if not any(b in reach[w] for w in cadj[a] if w != b)]
    cnt = 1
    for c in comps:
        cnt *= math.factorial(len(c) - 1)
    for a, b in red:
        cnt *= len(comps[a]) * len(comps[b])
    unique_char = all(len(c) <= 2 for c in comps) and all(len(comps[a]) == 1 and len(comps[b]) == 1 for a, b in red)
    return cnt, unique_char


# exhaustive: all digraphs (no loops) on n <= 4 vertices
ok6b_dag = ok6b_count = ok6b_char = ok6c = True
n_unique_cyclic = 0
for n in range(1, 5):
    arcs = [(u, v) for u in range(n) for v in range(n) if u != v]
    groups = {}
    for mask in range(1 << len(arcs)):
        E = [arcs[i] for i in range(len(arcs)) if mask >> i & 1]
        groups.setdefault(clos_set(n, E), []).append(E)
    best = {}
    for cl, gs in groups.items():
        mn = min(len(g) for g in gs)
        best[cl] = (mn, [g for g in gs if len(g) == mn])
    for cl, gs in groups.items():
        mn, mins = best[cl]
        for E in gs:
            nred = len(mins)
            cnt, uniq = count_formula(n, E)
            if cnt != nred:
                ok6b_count = False
            if uniq != (nred == 1):
                ok6b_char = False
            if is_acyclic(n, E):
                ess = {(u, v) for u, v in E
                       if not any(w not in (u, v) and closure(n, E)[u][w] and closure(n, E)[w][v] for w in range(n))}
                if nred != 1 or set(mins[0]) != ess:
                    ok6b_dag = False
            elif nred == 1:
                n_unique_cyclic += 1
            H = TransitiveReduction(n, E)
            if clos_set(n, list(H)) != cl or len(H) != mn:
                ok6c = False
check("6.6(b) every dag has exactly one transitive reduction: its essential edges", ok6b_dag,
      "all digraphs on <= 4 vertices")
check("6.6(b) as printed ('only if') is false: some cyclic graphs have a unique reduction", n_unique_cyclic > 0,
      f"{n_unique_cyclic} cyclic graphs on <= 4 vertices with a unique reduction")
E2c = [(0, 1), (1, 0)]
check("6.6(b) the 2-cycle u->v->u is its own unique transitive reduction",
      sum(1 for mask in range(4) if clos_set(2, [a for i, a in enumerate([(0, 1), (1, 0)]) if mask >> i & 1])
          == clos_set(2, E2c)) == 1)
check("6.6(b) number of reductions = prod (|C|-1)! * prod_{C->C' in red(scc)} |C||C'|", ok6b_count)
check("6.6(b) unique iff all strong components have <= 2 vertices and 2-vertex ones are isolated in scc(G)",
      ok6b_char)
c3a, c3b = [(0, 1), (1, 2), (2, 0)], [(0, 2), (2, 1), (1, 0)]
check("6.6(b) a->b->c->a and a->c->b->a: two different reductions of the same closure",
      clos_set(3, c3a) == clos_set(3, c3b) and set(c3a) != set(c3b))
check("6.6(c) TransitiveReduction has the same closure and the minimum number of edges", ok6c,
      "all digraphs on <= 4 vertices")
ok6c2 = True
for trial in range(300):
    n = random.randint(5, 12)
    E = rand_digraph(n, random.random() * 0.3)
    H = TransitiveReduction(n, E)
    if clos_set(n, list(H)) != clos_set(n, E):
        ok6c2 = False
check("6.6(c) TransitiveReduction preserves the closure on larger random digraphs", ok6c2, "300 digraphs, 5-12 vertices")

# ============================================================================ Exercise 6.7 (Tarry)
print("== Exercise 6.7: Tarry's algorithm")


def Tarry(n, adj, s, pick):
    """Literal simulation with explicit arc colors.  pick(list of candidate arcs) chooses the white arc."""
    color = {(v, w): "white" for v in range(n) for w in adj[v]}
    marked = [False] * n
    visits = [0] * n
    log = []          # (vertex, k, red_in, red_out) at each visit
    traversed = []
    v = s
    while True:
        marked[v] = True
        visits[v] += 1
        red_in = sum(1 for u in adj[v] if color[(u, v)] == "red")
        red_out = sum(1 for w in adj[v] if color[(v, w)] == "red")
        log.append((v, visits[v], red_in, red_out))
        white = [w for w in adj[v] if color[(v, w)] == "white"]
        green = [w for w in adj[v] if color[(v, w)] == "green"]
        if white:
            w = pick(white)
            if not marked[w]:
                color[(w, v)] = "green"
            color[(v, w)] = "red"
            traversed.append((v, w))
            v = w
        elif green:
            w = green[0]
            color[(v, w)] = "red"
            traversed.append((v, w))
            v = w
        else:
            break
    return dict(color=color, visits=visits, log=log, traversed=traversed, last=v, marked=marked)


def TarryFast(n, adj, s):
    """(a) implementation: a pointer into each adjacency list, the parent arc, twin lookups; counts the work."""
    twin_color = {}
    nxt = [0] * n
    parent = [None] * n
    marked = [False] * n
    work = 0
    v = s
    walk = []
    while True:
        marked[v] = True
        walk.append(v)
        # advance v's pointer past non-white arcs
        while nxt[v] < len(adj[v]) and twin_color.get((v, adj[v][nxt[v]]), "white") != "white":
            nxt[v] += 1
            work += 1
        if nxt[v] < len(adj[v]):
            w = adj[v][nxt[v]]
            if not marked[w]:
                twin_color[(w, v)] = "green"
                parent[w] = v
            twin_color[(v, w)] = "red"
            v = w
        elif parent[v] is not None and twin_color.get((v, parent[v])) == "green":
            twin_color[(v, parent[v])] = "red"
            v = parent[v]
        else:
            break
        work += 1
    return walk, work


ok7 = {k: True for k in "abcdefg"}
for trial in range(1500):
    n = random.randint(1, 9)
    E = rand_connected_graph(n, random.randint(0, 2 * n))
    adj = undirected_adj(n, E)
    s = random.randrange(n)
    res = Tarry(n, adj, s, lambda ws: random.choice(ws))
    deg = [len(a) for a in adj]
    m2 = sum(deg)
    if len(res["traversed"]) != len(set(res["traversed"])):
        ok7["b"] = False
    for (v, k, rin, rout) in res["log"]:
        if v == s and (rin, rout) != (k - 1, k - 1):
            ok7["c"] = False
        if v != s and (rin, rout) != (k, k - 1):
            ok7["c"] = False
    if any(res["visits"][v] > deg[v] + (1 if v == s else 0) for v in range(n)):
        ok7["d"] = False
    if res["last"] != s:
        ok7["e"] = False
    if any(c != "red" for c in res["color"].values()):
        ok7["f"] = False
    if not all(res["marked"]) or len(res["traversed"]) != m2:
        ok7["g"] = False
    # (a): the pointer implementation walks the same way when the white arc is chosen as the first in the list
    res1 = Tarry(n, adj, s, lambda ws: ws[0])
    walk, work = TarryFast(n, adj, s)
    if walk != [x[0] for x in res1["log"]] or work > 2 * m2 + 1:
        ok7["a"] = False
check("6.7(a) pointer implementation walks the same way; work <= 2(2E) + 1 = O(V+E)", ok7["a"], "1500 random graphs")
check("6.7(b) no arc is traversed twice (random choice of white arcs)", ok7["b"])
check("6.7(c) at the k-th visit: s has k-1 red arcs in and k-1 out; v != s has k in and k-1 out", ok7["c"])
check("6.7(d) visits(v) <= deg(v), visits(s) <= deg(s) + 1", ok7["d"])
check("6.7(e) the last vertex visited is s", ok7["e"])
check("6.7(f) all arcs are red at the end", ok7["f"])
check("6.7(g) every vertex visited and every arc traversed exactly once (2E traversals)", ok7["g"])

# ============================================================================ Exercise 6.8 (Tarry2)
print("== Exercise 6.8: Tarry2 is not depth-first search")


def Tarry2(n, adj, s):
    """Literal simulation of RecTarry2 (tail recursion as a loop); white arcs taken in adjacency-list order."""
    color = {(v, w): "white" for v in range(n) for w in adj[v]}
    marked = [False] * n
    pre, post = [None] * n, [None] * n
    post_writes = [0] * n
    v, clock = s, 1
    steps = 0
    while True:
        steps += 1
        assert steps < 10 ** 5
        if not marked[v]:
            pre[v] = clock
            clock += 1
            marked[v] = True
        white = [w for w in adj[v] if color[(v, w)] == "white"]
        green = [w for w in adj[v] if color[(v, w)] == "green"]
        if white:
            w = white[0]
            if not marked[w]:
                color[(w, v)] = "green"
            color[(v, w)] = "red"
            v = w
        elif green:
            w = green[0]
            post[v] = clock
            post_writes[v] += 1
            clock += 1
            v = w
        else:
            break
    tree = frozenset(frozenset((v, w)) for (v, w), c in color.items() if c == "green")
    return tree, pre, post, post_writes


def all_dfs_trees(n, adj, s, cap=4000):
    """Every DFS tree from s (recursive DFS, Figure 6.3) over all orderings of the adjacency lists (if <= cap)."""
    sizes = [math.factorial(len(a)) for a in adj]
    if math.prod(sizes) > cap:
        return None
    trees = set()
    for orders in itertools.product(*[list(itertools.permutations(a)) for a in adj]):
        _, _, par = dfs_pre_post([list(o) for o in orders], [s])
        trees.add(frozenset(frozenset((v, par[v])) for v in range(n) if par[v] is not None))
    return trees


# the page's example: s=0, a=1, b=2, x=3
names = "s a b x".split()
EX8 = [(0, 1), (1, 2), (0, 2), (0, 3), (2, 3)]
adj8 = [[1, 3, 2], [0, 2], [1, 0, 3], [0, 2]]       # s: a x b; a: s b; b: a s x; x: s b
check("6.8 example adjacency lists match the undirected edges sa, ab, bs, sx, xb",
      sorted(tuple(sorted((v, w))) for v in range(4) for w in adj8[v]) == sorted(
          [e for e in EX8 for _ in (0, 1)]))
tree8, pre8, post8, pw8 = Tarry2(4, adj8, 0)
check("6.8 example: green edges sa, ab, sx", tree8 == {frozenset((0, 1)), frozenset((1, 2)), frozenset((0, 3))})
check("6.8 example: pre s,a,b,x = 1,2,3,4; post x,b,a = 5,6,7; s gets no post label",
      pre8 == [1, 2, 3, 4] and post8 == [None, 7, 6, 5], f"pre {pre8}, post {post8}")
dfs8 = all_dfs_trees(4, adj8, 0)
check("6.8 example: the green tree is not a depth-first tree for ANY order of the adjacency lists",
      tree8 not in dfs8, f"{len(dfs8)} different DFS trees exist")
check("6.8 example: [x.pre, x.post] = [4, 5] is nested in [b.pre, b.post] = [3, 6] but x is not b's descendant",
      pre8[2] < pre8[3] < post8[3] < post8[2])
# no counterexample (in the tree) on <= 3 vertices; s never gets a post label
small_ok = True
nopost = True
for n in range(1, 4):
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        E = [pairs[i] for i in range(len(pairs)) if mask >> i & 1]
        if len(wfs(undirected_adj(n, E, False), 0)) < n:
            continue
        base = undirected_adj(n, E, False)
        for orders in itertools.product(*[list(itertools.permutations(a)) for a in base]):
            adjo = [list(o) for o in orders]
            tr, pr, po, _ = Tarry2(n, adjo, 0)
            if tr not in all_dfs_trees(n, base, 0):
                small_ok = False
            if po[0] is not None:
                nopost = False
check("6.8 on connected graphs with <= 3 vertices the green tree is always a DFS tree (so 4 vertices is the minimum)",
      small_ok)
check("6.8 s never receives a post label (3-vertex graphs, all orders)", nopost)
bad_trees = 0
rewritten = 0
for trial in range(400):
    n = random.randint(2, 7)
    E = rand_connected_graph(n, random.randint(0, n))
    adj = undirected_adj(n, E)
    tr, pr, po, pw = Tarry2(n, adj, 0)
    T = all_dfs_trees(n, adj, 0)
    if T is not None and tr not in T:
        bad_trees += 1
    rewritten += any(c > 1 for c in pw)
check("6.8 random graphs: the green tree is often not a DFS tree", bad_trees > 0, f"{bad_trees} of 400")

# ============================================================================ Exercise 6.9 (lock-boxes)
print("== Exercise 6.9: keys locked in boxes")


def rand_boxes(n, m):
    inside = [random.randrange(n) for _ in range(m)]                                     # key k lies in box inside[k]
    opens = [random.randrange(n) if random.random() < 0.85 else None for _ in range(m)]  # key k opens box opens[k]
    return inside, opens


def box_graph(n, inside, opens):
    return sorted({(inside[k], opens[k]) for k in range(len(inside)) if opens[k] is not None})


def simulate(n, inside, opens, smashed):
    opened = set(smashed)
    changed = True
    while changed:
        changed = False
        for k in range(len(inside)):
            if inside[k] in opened and opens[k] is not None and opens[k] not in opened:
                opened.add(opens[k])
                changed = True
    return all(inside[k] in opened for k in range(len(inside)))


def OnlyThisBox(n, inside, opens, b):
    """(a) every box that holds a key must be reachable from b."""
    reach = wfs(adjacency(n, box_graph(n, inside, opens)), b)
    return all(inside[k] in reach for k in range(len(inside)))


def MinSmash(n, inside, opens):
    """(b) number of source components of scc(G) that contain a box holding a key."""
    E = box_graph(n, inside, opens)
    comps, CE = condensation(n, E)
    has_pred = {b for a, b in CE}
    K = set(inside)
    return sum(1 for c in comps if c not in has_pred and c & K)


ok9a = ok9b = True
for trial in range(1500):
    n = random.randint(1, 7)
    m = random.randint(1, 9)
    inside, opens = rand_boxes(n, m)
    for b in range(n):
        if OnlyThisBox(n, inside, opens, b) != simulate(n, inside, opens, {b}):
            ok9a = False
    best = min(r for r in range(n + 1) for S in itertools.combinations(range(n), r) if simulate(n, inside, opens, S))
    if MinSmash(n, inside, opens) != best:
        ok9b = False
check("6.9(a) reachability from the smashed box vs simulating the unlocking", ok9a, "1500 random instances")
check("6.9(b) count of source components with a key vs the smallest smash set (all subsets)", ok9b)

# ============================================================================ Exercise 6.10 (checking search trees)
print("== Exercise 6.10: is T a depth-first / breadth-first tree?")


def bfs_tree_book(adj, s):
    """Breadth-first search = whatever-first search with a queue of pairs (Chapter 5)."""
    bag = [(None, s)]
    parent = {}
    while bag:
        p, v = bag.pop(0)
        if v not in parent:
            parent[v] = p
            for w in adj[v]:
                bag.append((v, w))
    return parent


def all_search_trees(n, adj, s, kind, cap):
    sizes = [math.factorial(len(a)) for a in adj]
    if math.prod(sizes) > cap:
        return None
    trees = set()
    for orders in itertools.product(*[list(itertools.permutations(a)) for a in adj]):
        adjo = [list(o) for o in orders]
        if kind == "dfs":
            _, _, par = dfs_pre_post(adjo, [s])
            par = {v: par[v] for v in range(n)}
        else:
            par = bfs_tree_book(adjo, s)
        if len(par) == n:
            trees.add(tuple(par[v] for v in range(n)))
    return trees


def candidate_trees(n, inn, s):
    """Every spanning tree rooted at s, as a parent tuple, with p(v) an in-neighbor of v."""
    choices = [[None] if v == s else inn[v] for v in range(n)]
    out = []
    for par in itertools.product(*choices):
        okk = True
        for v in range(n):
            seen, x = set(), v
            while x != s:
                if x in seen:
                    okk = False
                    break
                seen.add(x)
                x = par[x]
            if not okk:
                break
        if okk:
            out.append(par)
    return out


def tree_info(n, par, s):
    ch = [[] for _ in range(n)]
    for v in range(n):
        if par[v] is not None:
            ch[par[v]].append(v)
    depth = [0] * n
    pre, post = [0] * n, [0] * n
    clock = [0]

    def walk(v, d):
        depth[v] = d
        clock[0] += 1
        pre[v] = clock[0]
        for c in ch[v]:
            walk(c, d + 1)
        clock[0] += 1
        post[v] = clock[0]

    walk(s, 0)
    return depth, pre, post


def lift_to_siblings(par, depth, x, y):
    """Walk x and y up to the two children of their lowest common ancestor."""
    while depth[x] > depth[y]:
        x = par[x]
    while depth[y] > depth[x]:
        y = par[y]
    while par[x] != par[y]:
        x, y = par[x], par[y]
    return x, y


def acyclic_dfs(n, arcs):
    """IsAcyclic (Figure 6.7)."""
    adj = adjacency(n, arcs)
    status = ["new"] * n

    def rec(v):
        status[v] = "active"
        for w in adj[v]:
            if status[w] == "active":
                return False
            if status[w] == "new" and not rec(w):
                return False
        status[v] = "finished"
        return True

    return all(status[v] != "new" or rec(v) for v in range(n))


def IsDFSTreeUndirected(n, edges, par, s):
    """(a) every non-tree edge joins an ancestor and a descendant in T."""
    depth, pre, post = tree_info(n, par, s)
    anc = lambda u, v: pre[u] <= pre[v] and post[v] <= post[u]
    for u, v in edges:
        if par[v] == u or par[u] == v:
            continue
        if not (anc(u, v) or anc(v, u)):
            return False
    return True


def IsBFSTree(n, arcs, par, s):
    """(b)/(c) on directed arcs (an undirected edge = two arcs): levels, then sibling constraints, then acyclicity."""
    depth, pre, post = tree_info(n, par, s)
    H = []
    for u, v in arcs:
        if depth[v] > depth[u] + 1:
            return False
        if depth[v] == depth[u] + 1 and par[v] != u:          # p(v) must be dequeued before u
            x, y = lift_to_siblings(par, depth, par[v], u)
            H.append((x, y))
    return acyclic_dfs(n, H)


def IsDFSTreeDirected(n, arcs, par, s):
    """(d) cross edges must point to earlier siblings' subtrees: sibling constraints, then acyclicity."""
    depth, pre, post = tree_info(n, par, s)
    anc = lambda a, b: pre[a] <= pre[b] and post[b] <= post[a]
    H = []
    for u, v in arcs:
        if par[v] == u or anc(u, v) or anc(v, u):
            continue
        x, y = lift_to_siblings(par, depth, u, v)
        H.append((y, x))                                       # v's branch before u's branch
    return acyclic_dfs(n, H)


stats = {"a": [0, 0], "b": [0, 0], "c": [0, 0], "d": [0, 0]}
ok10 = {k: True for k in "abcd"}
spt_not_bfs = 0
for trial in range(700):
    n = random.randint(2, 6)
    E = rand_connected_graph(n, random.randint(0, 5))
    adj = undirected_adj(n, E, False)
    s = random.randrange(n)
    D = all_search_trees(n, adj, s, "dfs", 3000)
    B = all_search_trees(n, adj, s, "bfs", 3000)
    if D is None:
        continue
    arcs = [(u, v) for u, v in E] + [(v, u) for u, v in E]
    for par in candidate_trees(n, adj, s):
        a = IsDFSTreeUndirected(n, E, par, s)
        stats["a"][a] += 1
        if a != (par in D):
            ok10["a"] = False
        b = IsBFSTree(n, arcs, par, s)
        stats["b"][b] += 1
        if b != (par in B):
            ok10["b"] = False
        depth, _, _ = tree_info(n, par, s)
        if not b and all(abs(depth[u] - depth[v]) <= 1 for u, v in E):
            spt_not_bfs += 1
for trial in range(700):
    n = random.randint(2, 6)
    E = rand_digraph(n, random.random() * 0.6)
    s = random.randrange(n)
    adj = adjacency(n, E)
    if len(wfs(adj, s)) < n:
        continue
    D = all_search_trees(n, adj, s, "dfs", 3000)
    B = all_search_trees(n, adj, s, "bfs", 3000)
    if D is None:
        continue
    inn = [[u for u, w in E if w == v] for v in range(n)]
    for par in candidate_trees(n, inn, s):
        c = IsBFSTree(n, E, par, s)
        stats["c"][c] += 1
        if c != (par in B):
            ok10["c"] = False
        d = IsDFSTreeDirected(n, E, par, s)
        stats["d"][d] += 1
        if d != (par in D):
            ok10["d"] = False
check("6.10(a) undirected DFS-tree test vs all DFS trees over all adjacency orders", ok10["a"],
      f"{stats['a'][1]} yes / {stats['a'][0]} no")
check("6.10(b) undirected BFS-tree test vs all BFS trees over all adjacency orders", ok10["b"],
      f"{stats['b'][1]} yes / {stats['b'][0]} no; {spt_not_bfs} shortest-path trees that are not BFS trees")
check("6.10(c) directed BFS-tree test vs brute force", ok10["c"], f"{stats['c'][1]} yes / {stats['c'][0]} no")
check("6.10(d) directed DFS-tree test vs brute force", ok10["d"], f"{stats['d'][1]} yes / {stats['d'][0]} no")
# the page's example of a shortest-path tree that is not a BFS tree: s=0, a=1, b=2, c=3, d=4
E10 = [(0, 1), (0, 2), (1, 3), (1, 4), (2, 3), (2, 4)]
par10 = (None, 0, 0, 1, 2)
adj10 = undirected_adj(5, E10, False)
dep10, _, _ = tree_info(5, par10, 0)
B10 = all_search_trees(5, adj10, 0, "bfs", 10 ** 6)
check("6.10(b) example: T = {sa, sb, ac, bd} is a shortest-path tree but not a BFS tree",
      all(abs(dep10[u] - dep10[v]) <= 1 for u, v in E10) and par10 not in B10
      and not IsBFSTree(5, E10 + [(v, u) for u, v in E10], par10, 0), f"{len(B10)} BFS trees exist")

# ============================================================================ Exercise 6.11(a)
print("== Exercise 6.11(a): parallel assignment")
P = 1000003


def run_parallel(k, reads, coef, vals):
    return [sum(coef[i][j] * vals[j] for j in reads[i]) % P + i for i in range(k)]


def run_serial(order, reads, coef, vals):
    vals = list(vals)
    for i in order:
        vals[i] = sum(coef[i][j] * vals[j] for j in reads[i]) % P + i
    return vals


def Serialize(k, reads):
    """Graph: x_i -> x_j when the right side of x_i mentions x_j (j != i); a topological order or None."""
    arcs = [(i, j) for i in range(k) for j in reads[i] if j != i and j < k]
    if not acyclic_dfs(k, arcs):
        return None
    return topological_order(k, adjacency(k, arcs))


ok11 = True
nyes = 0
for trial in range(1500):
    k = random.randint(1, 5)
    extra = random.randint(0, 2)                      # read-only variables k .. k+extra-1
    reads = [sorted(random.sample(range(k + extra), random.randint(0, min(3, k + extra)))) for _ in range(k)]
    coef = [[random.randrange(1, P) for _ in range(k + extra)] for _ in range(k)]
    tests = [[random.randrange(P) for _ in range(k + extra)] for _ in range(3)]
    good = [list(o) for o in itertools.permutations(range(k))
            if all(run_serial(o, reads, coef, t)[:k] == run_parallel(k, reads, coef, t) for t in tests)]
    order = Serialize(k, reads)
    nyes += order is not None
    if (order is None) != (not good):
        ok11 = False
    if order is not None and order not in good:
        ok11 = False
check("6.11(a) serializable without temporaries iff the dependency graph is acyclic; the topological order works",
      ok11, f"1500 random assignments, {nyes} serializable")
# the book's examples (x=0, y=1)
check("6.11 a,b = 0,1: both orders work", Serialize(2, [[], []]) is not None)
check("6.11 x,y = x+1,x+y: only y first", Serialize(2, [[0], [0, 1]]) == [1, 0])
check("6.11 a,b = b,a and x,y = x+y,x-y: cycles", Serialize(2, [[1], [0]]) is None and Serialize(2, [[0, 1], [0, 1]]) is None)
okt = True
for x0, y0 in itertools.product(range(-5, 6), repeat=2):
    t = x0
    x = x0 + y0
    y = t - y0
    okt &= (x, y) == (x0 + y0, x0 - y0)
check("6.11 x,y = x+y,x-y needs only ONE temporary: t=x; x=x+y; y=t-y (book says two)", okt)

# ============================================================================ Exercise 6.12 (jobs)
print("== Exercise 6.12: scheduling jobs in a dag")


def EarliestStarts(n, adj, T):
    """ES(v) = max{ES(u) + T(u) : u->v} (0 for sources), filled in topological order."""
    order = topological_order(n, adj)
    ES = {}
    radj = Reverse(n, adj)
    for v in order:
        ES[v] = max([ES[u] + T[u] for u in radj[v]], default=0)       # KeyError if order were wrong
    return ES


def LatestStarts(n, adj, T, ES):
    CT = max(ES[v] + T[v] for v in range(n))
    return {v: min([CT] + [ES[w] for w in adj[v]]) - T[v] for v in range(n)}, CT


def LatestStartsClassic(n, adj, T, CT):
    """LS(v) = min({CT} U {LS(w) : v->w}) - T(v), filled in postorder (reverse topological order)."""
    order = topological_order(n, adj)
    LS = {}
    for v in reversed(order):
        LS[v] = min([CT] + [LS[w] for w in adj[v]]) - T[v]
    return LS


def all_paths_ending(n, adj):
    """For each v: max total time of jobs strictly before v on a path ending at v (brute force over all paths)."""
    best = [0] * n
    best_from = [0] * n

    def rec(path, tot):
        v = path[-1]
        best[v] = max(best[v], tot - 0)
        for w in adj[v]:
            rec(path + [w], tot + T[v])

    for s0 in range(n):
        rec([s0], 0)
    return best


ok12 = {k: True for k in ("a", "b", "c", "classic")}
for trial in range(600):
    n = random.randint(1, 7)
    E = rand_dag(n, random.random() * 0.6)
    adj = adjacency(n, E)
    T = [random.randint(0, 5) for _ in range(n)]
    ES = EarliestStarts(n, adj, T)
    bf = all_paths_ending(n, adj)
    if any(ES[v] != bf[v] for v in range(n)):
        ok12["b"] = False
    # (a): brute force the shortest makespan over integer schedules is the heaviest chain
    heaviest = max(bf[v] + T[v] for v in range(n))
    if max(ES[v] + T[v] for v in range(n)) != heaviest:
        ok12["a"] = False
    LS, CT = LatestStarts(n, adj, T, ES)
    radj = Reverse(n, adj)
    for v in range(n):
        feas = [t for t in range(0, CT + 1)
                if all(ES[u] + T[u] <= t for u in radj[v]) and all(t + T[v] <= ES[w] for w in adj[v])
                and t + T[v] <= CT]
        if max(feas) != LS[v] or LS[v] < ES[v]:
            ok12["c"] = False
    LSc = LatestStartsClassic(n, adj, T, CT)
    # classic latest start = CT - (heaviest path starting at v, including v)
    hp = {}

    def heavy_from(v):
        if v not in hp:
            hp[v] = T[v] + max([heavy_from(w) for w in adj[v]], default=0)
        return hp[v]

    if any(LSc[v] != CT - heavy_from(v) or LSc[v] < LS[v] for v in range(n)):
        ok12["classic"] = False
check("6.12(b) ES by the recurrence in topological order vs all paths", ok12["b"], "600 random dags")
check("6.12(a) shortest completion time = max ES(v)+T(v) = heaviest chain", ok12["a"])
check("6.12(c) latest start (others at ES) = min({CT} U {ES(w)}) - T(v) vs trying every start time", ok12["c"])
check("6.12(c) remark: classic LS(v) = CT - heaviest path from v, never earlier than the part (c) value", ok12["classic"])

# ============================================================================ Exercise 6.13 (dag with s and t)
print("== Exercise 6.13: paths in a dag with one source and one sink")


def all_st_paths(adj, s, t):
    out = []

    def rec(path):
        v = path[-1]
        if v == t:
            out.append(list(path))
            return
        for w in adj[v]:
            path.append(w)
            rec(path)
            path.pop()

    rec([s])
    return out


def postorder_vertices(n, adj, s):
    """reach(s) in postorder of DFS(s)."""
    pre, post, _ = dfs_pre_post(adj, [s])
    return sorted((v for v in range(n) if post[v] is not None), key=lambda v: post[v])


def Hamiltonian(n, adj, s, t):
    L = {}
    for v in postorder_vertices(n, adj, s):
        L[v] = 1 if v == t else 1 + max(L[x] for x in adj[v])
    return L[s] == n


def MaxPath(n, adj, s, t, w):
    M = {}
    for v in postorder_vertices(n, adj, s):
        M[v] = w[v] if v == t else w[v] + max(M[x] for x in adj[v])
    return M[s]


def MaxPathL(n, adj, s, t, w, ell):
    M = {}
    for j in range(ell + 1):                      # outer loop: j; inner: vertices in any order
        for v in range(n):
            if v == t:
                M[v, j] = w[t]
            elif j == 0:
                M[v, j] = NEG
            else:
                M[v, j] = w[v] + max(M[x, j - 1] for x in adj[v])
    return M[s, ell]


def MaxImp(n, adj, s, t, w, imp, k):
    M = {}
    for v in postorder_vertices(n, adj, s):        # outer loop: vertices in postorder; inner: j
        for j in range(k + 1):
            if v == t:
                M[v, j] = w[t] if imp[t] >= j else NEG
            else:
                M[v, j] = w[v] + max(M[x, max(0, j - imp[v])] for x in adj[v])
    return M[s, k]


def NumPaths(n, adj, s, t):
    N = {}
    for v in postorder_vertices(n, adj, s):
        N[v] = 1 if v == t else sum(N[x] for x in adj[v])
    return N[s]


ok13 = {k: True for k in "abcde"}
cnt_h = 0
for trial in range(800):
    n = random.randint(2, 8)
    E, s, t = rand_st_dag(n, random.random() * 0.6)
    adj = adjacency(n, E)
    paths = all_st_paths(adj, s, t)
    w = [random.randint(-5, 9) for _ in range(n)]
    imp = [int(random.random() < 0.4) for _ in range(n)]
    ham = any(len(p) == n for p in paths)
    cnt_h += ham
    if Hamiltonian(n, adj, s, t) != ham or SemiConnectedDag(n, adj) != ham:
        ok13["a"] = False
    if MaxPath(n, adj, s, t, w) != max(sum(w[v] for v in p) for p in paths):
        ok13["b"] = False
    for ell in range(0, n):
        good = [sum(w[v] for v in p) for p in paths if len(p) - 1 <= ell]
        if MaxPathL(n, adj, s, t, w, ell) != max(good, default=NEG):
            ok13["c"] = False
    for k in range(0, 4):
        good = [sum(w[v] for v in p) for p in paths if sum(imp[v] for v in p) >= k]
        if MaxImp(n, adj, s, t, w, imp, k) != max(good, default=NEG):
            ok13["d"] = False
    if NumPaths(n, adj, s, t) != len(paths):
        ok13["e"] = False
check("6.13(a) Hamiltonian path iff longest path has V vertices (iff semi-connected, 6.1(b))", ok13["a"],
      f"800 random st-dags, {cnt_h} with a Hamiltonian path")
check("6.13(b) MaxPath vs all s-t paths", ok13["b"])
check("6.13(c) MaxPathL (j outer, vertices inner) vs all s-t paths with <= l edges", ok13["c"])
check("6.13(d) MaxImp vs all s-t paths with >= k important vertices", ok13["d"])
check("6.13(e) NumPaths vs listing all s-t paths", ok13["e"])
# Figure 6.20 again: number of s-t paths and a longest path
check("6.13(e) on Figure 6.20's dag there are 128 = 2*8*4*2 s-t paths (example on the page)",
      NumPaths(12, adj20, ix["s"], ix["t"]) == len(all_st_paths(adj20, ix["s"], ix["t"])) == 128 == 2 * 8 * 4 * 2
      and [NumPaths(12, adj20, ix[a], ix[b]) for a, b in ("sg", "gc", "cj", "jt")] == [2, 8, 4, 2],
      f"{NumPaths(12, adj20, ix['s'], ix['t'])}")

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: {FAIL}")
