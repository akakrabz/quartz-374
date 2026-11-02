#!/usr/bin/env python3
"""Checks for content/2-algorithms/07-minimum-spanning-trees-exercises.md (solved exercises 7.1-7.6(a), 7.7, 7.8,
7.9(a)-(c) and 7.10 of Erickson's Algorithms).

Every algorithm is implemented the way the page states it and compared with brute force: enumeration of ALL spanning
trees (minimum, uniqueness, second smallest), all cycles, all cuts, all edge subsets (feedback edge sets) and all
simple paths (bottleneck distances), on every small graph of a family and on many random ones.  The counterexamples
and the book's figures (7.1 and the bottleneck figure of Exercise 7.9) are re-entered and every number on the page is
recomputed.  For Exercise 7.10 the book's pseudocode (Find with path compression, Union, FindSafeEdges, AddSafeEdges,
Boruvka) is run literally, counting Find invocations."""
import itertools
import math
import random

random.seed(374)
FAIL = []
INF = float("inf")
NEG = float("-inf")


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail != "" else ""))
    if not cond:
        FAIL.append(name)


# ============================================================================ brute-force helpers
# A graph is (n, E) with E a list of (u, v, w); edge ids are indices into E.  Simple graphs only.
class DSU:
    def __init__(self, n):
        self.p = list(range(n))

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


def components(n, E, ids=None):
    d = DSU(n)
    for i in (range(len(E)) if ids is None else ids):
        d.union(E[i][0], E[i][1])
    return [d.find(v) for v in range(n)]


def is_connected(n, E, ids=None):
    c = components(n, E, ids)
    return len(set(c)) <= 1


def acyclic(n, E, ids):
    d = DSU(n)
    return all(d.union(E[i][0], E[i][1]) for i in ids)


def spanning_trees(n, E):
    """All spanning trees, as frozensets of edge ids (brute force over all (n-1)-subsets)."""
    out = []
    for comb in itertools.combinations(range(len(E)), n - 1):
        if acyclic(n, E, comb):
            out.append(frozenset(comb))
    return out


def weight(E, ids):
    return sum(E[i][2] for i in ids)


def all_msts(n, E):
    trees = spanning_trees(n, E)
    best = min(weight(E, T) for T in trees)
    return [T for T in trees if weight(E, T) == best], best


def all_cycles(n, E):
    """All simple cycles, as frozensets of edge ids (edge subsets that are connected and 2-regular)."""
    out = []
    m = len(E)
    for mask in range(1, 1 << m):
        ids = [i for i in range(m) if mask >> i & 1]
        if len(ids) < 3:
            continue
        deg = {}
        for i in ids:
            for x in E[i][:2]:
                deg[x] = deg.get(x, 0) + 1
        if any(d != 2 for d in deg.values()):
            continue
        d = DSU(n)
        for i in ids:
            d.union(E[i][0], E[i][1])
        if len({d.find(x) for x in deg}) == 1:
            out.append(frozenset(ids))
    return out


def kruskal(n, E, order=None):
    """Kruskal's loop on the given order of edge ids (default: by weight, ties by id); a minimum spanning forest."""
    if order is None:
        order = sorted(range(len(E)), key=lambda i: (E[i][2], i))
    d = DSU(n)
    return frozenset(i for i in order if d.union(E[i][0], E[i][1]))


def tree_path(n, E, T, u, v):
    """Edge ids on the path from u to v in the forest T (None if not connected)."""
    adj = [[] for _ in range(n)]
    for i in T:
        a, b = E[i][:2]
        adj[a].append((b, i))
        adj[b].append((a, i))
    par = {u: None}
    stack = [u]
    while stack:
        x = stack.pop()
        for y, i in adj[x]:
            if y not in par:
                par[y] = (x, i)
                stack.append(y)
    if v not in par:
        return None
    path = []
    while v != u:
        x, i = par[v]
        path.append(i)
        v = x
    return path


def random_connected(n, p, weights="distinct", wmax=None):
    while True:
        pairs = [(u, v) for u in range(n) for v in range(u + 1, n) if random.random() < p]
        if weights == "distinct":
            ws = random.sample(range(1, 10 * len(pairs) + 10), len(pairs))
        else:
            ws = [random.randint(weights[0], weights[1]) for _ in pairs]
        E = [(u, v, w) for (u, v), w in zip(pairs, ws)]
        if is_connected(n, E):
            return E


def wfs_reach(n, E, ids, s):
    adj = [[] for _ in range(n)]
    for i in ids:
        a, b = E[i][:2]
        adj[a].append(b)
        adj[b].append(a)
    seen = {s}
    bag = [s]
    while bag:
        x = bag.pop()
        for y in adj[x]:
            if y not in seen:
                seen.add(y)
                bag.append(y)
    return seen


def fresh(n_lo, n_hi, p, count, weights="distinct"):
    for _ in range(count):
        n = random.randint(n_lo, n_hi)
        yield n, random_connected(n, p, weights)


# ============================================================================ the swap lemma and optimality conditions
ok_swap, ok_fcyc, ok_fcut, cnt = True, True, True, 0
for n, E in fresh(3, 6, 0.6, 300):
    T = kruskal(n, E)
    msts, best = all_msts(n, E)
    cnt += 1
    if [T] != msts:
        ok_fcyc = False
    for g in set(range(len(E))) - T:
        P = tree_path(n, E, T, E[g][0], E[g][1])
        for f in P:
            if not (acyclic(n, E, (T - {f}) | {g}) and len((T - {f}) | {g}) == n - 1):
                ok_swap = False
        if not all(E[g][2] > E[f][2] for f in P):  # fundamental cycle: g is its heaviest edge
            ok_fcyc = False
    for f in T:
        comp = components(n, E, T - {f})
        cross = [i for i in range(len(E)) if comp[E[i][0]] != comp[E[i][1]]]
        if min(cross, key=lambda i: E[i][2]) != f:  # fundamental cut: f is its lightest edge
            ok_fcut = False
check("swap lemma: T - f + g is a spanning tree for every non-tree g and every f on g's tree path", ok_swap,
      f"{cnt} random graphs")
check("fundamental cycle: every non-MST edge is the heaviest edge of the cycle it closes with T", ok_fcyc)
check("fundamental cut: every MST edge f is the lightest edge across the cut of T - f", ok_fcut)

# ============================================================================ Exercise 7.1
ok_a, ok_kr, ncyc = True, True, 0
for n, E in fresh(3, 6, 0.65, 300):
    msts, best = all_msts(n, E)
    T = msts[0]
    if len(msts) != 1:
        ok_a = False
    order = sorted(range(len(E)), key=lambda i: E[i][2])
    for C in all_cycles(n, E):
        ncyc += 1
        h = max(C, key=lambda i: E[i][2])
        if h in T:
            ok_a = False
        # Kruskal view: when h comes up, its endpoints are already joined by the forest built from lighter edges
        d = DSU(n)
        for i in order:
            if i == h:
                if d.find(E[h][0]) != d.find(E[h][1]):
                    ok_kr = False
                break
            d.union(E[i][0], E[i][1])
check("7.1(a) the heaviest edge of every cycle is not in the MST (distinct weights, brute-force MST)", ok_a,
      f"300 random graphs, {ncyc} cycles")
check("7.1(a) Kruskal view: the heaviest edge of a cycle is useless when Kruskal examines it", ok_kr)
# ties: the claim needs distinct weights
E3 = [(0, 1, 1), (1, 2, 1), (0, 2, 1)]
check("7.1(a) with ties: in a triangle of equal weights every MST contains a heaviest edge of the cycle",
      all(len(T) == 2 for T in all_msts(3, E3)[0]) and len(all_msts(3, E3)[0]) == 3)
# (b) the diamond
U, Vv, X, Y = 0, 1, 2, 3
D = [(U, X, 1), (X, Vv, 2), (U, Vv, 3), (U, Y, 4), (Vv, Y, 5)]
msts, best = all_msts(4, D)
cycD = all_cycles(4, D)
cyc_uvy = frozenset([2, 3, 4])
check("7.1(b) diamond: unique MST = {ux, xv, uy}, weight 7", msts == [frozenset([0, 1, 3])] and best == 7,
      f"{sorted(msts[0])}, {best}")
check("7.1(b) diamond: cycle u v y has lightest edge uv (3), which is not in the MST",
      cyc_uvy in cycD and min(cyc_uvy, key=lambda i: D[i][2]) == 2 and 2 not in msts[0])
check("7.1(b) diamond: uv is the heaviest edge of cycle u x v", frozenset([0, 1, 2]) in cycD and
      max([0, 1, 2], key=lambda i: D[i][2]) == 2)
check("7.1(b) diamond: three cycles in all", len(cycD) == 3)
tri_ok = True
for ws in itertools.permutations([1, 2, 3]):
    Et = [(0, 1, ws[0]), (1, 2, ws[1]), (0, 2, ws[2])]
    T = all_msts(3, Et)[0][0]
    if min(range(3), key=lambda i: Et[i][2]) not in T:
        tri_ok = False
check("7.1(b) no counterexample with 3 vertices (triangles keep their lightest edge)", tri_ok)
bad_b = 0
for n, E in fresh(4, 6, 0.7, 200):
    T = all_msts(n, E)[0][0]
    if any(min(C, key=lambda i: E[i][2]) not in T for C in all_cycles(n, E)):
        bad_b += 1
check("7.1(b) the claim fails often on random graphs", bad_b > 50, f"{bad_b}/200 random graphs")


# ============================================================================ Exercise 7.2
def cut_condition(n, E):
    for mask in range(1, (1 << n) - 1):
        cross = [E[i][2] for i in range(len(E)) if (mask >> E[i][0] & 1) != (mask >> E[i][1] & 1)]
        if cross and cross.count(min(cross)) > 1:
            return False
    return True


def cycle_condition(n, E, cycles=None):
    for C in (all_cycles(n, E) if cycles is None else cycles):
        ws = [E[i][2] for i in C]
        if ws.count(max(ws)) > 1:
            return False
    return True


def char_ii(n, E, T):
    """Every non-tree edge is strictly heavier than every edge on its tree path."""
    for g in set(range(len(E))) - T:
        P = tree_path(n, E, T, E[g][0], E[g][1])
        if any(E[g][2] <= E[f][2] for f in P):
            return False
    return True


def unique_mst_alg(n, E):
    """The page's UniqueMST: Kruskal; then Kruskal again with ties broken against T; compare."""
    T = kruskal(n, E)
    order2 = sorted(range(len(E)), key=lambda i: (E[i][2], i in T, random.random()))
    T2 = kruskal(n, E, order2)
    return T2 == T


# (a) the triangle
Ta = [(0, 1, 1), (1, 2, 1), (2, 0, 2)]  # a=0, b=1, c=2
tw = sorted(weight(Ta, T) for T in spanning_trees(3, Ta))
check("7.2(a) triangle 1,1,2: spanning-tree weights 2,3,3, unique MST {ab, bc}",
      tw == [2, 3, 3] and all_msts(3, Ta)[0] == [frozenset([0, 1])], f"{tw}")
check("7.2(b) triangle violates the cut bullet (S = {b}) but satisfies the cycle bullet",
      not cut_condition(3, Ta) and cycle_condition(3, Ta))
# H: a=0, b=1, c=2, x=3
H = [(0, 2, 1), (0, 3, 2), (1, 3, 3), (0, 1, 4), (1, 2, 4)]
mH, bH = all_msts(4, H)
check("7.2(b) graph H: unique MST {ac, ax, bx} of weight 6", mH == [frozenset([0, 1, 2])] and bH == 6,
      f"{sorted(mH[0])}, {bH}")
cH = all_cycles(4, H)
check("7.2(b) graph H: cycle abc has two heaviest edges ab, bc (weight 4); H satisfies the cut bullet",
      frozenset([0, 3, 4]) in cH and not cycle_condition(4, H) and cut_condition(4, H))
check("7.2(b) graph H: ab is the unique heaviest edge of cycle a x b, bc of cycle b c a x",
      frozenset([1, 2, 3]) in cH and frozenset([0, 1, 2, 4]) in cH)
# exhaustive: all connected graphs on 3 and 4 labelled vertices, weights in {1,2,3}
stats = dict(graphs=0, unique=0, uniq_not_cut=0, uniq_not_cyc=0, uniq_not_both=0)
ok_cut, ok_cyc, ok_ii, ok_alg, ok_ii_any = True, True, True, True, True
for n in (3, 4):
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for r in range(n - 1, len(pairs) + 1):
        for sub in itertools.combinations(pairs, r):
            if not is_connected(n, [(u, v, 0) for u, v in sub]):
                continue
            cyc0 = all_cycles(n, [(u, v, 0) for u, v in sub])
            for ws in itertools.product((1, 2, 3), repeat=r):
                E = [(u, v, w) for (u, v), w in zip(sub, ws)]
                msts, _ = all_msts(n, E)
                uniq = len(msts) == 1
                cu, cy = cut_condition(n, E), cycle_condition(n, E, cyc0)
                stats["graphs"] += 1
                stats["unique"] += uniq
                stats["uniq_not_cut"] += uniq and not cu
                stats["uniq_not_cyc"] += uniq and not cy
                stats["uniq_not_both"] += uniq and not (cu and cy)
                if cu and not uniq:
                    ok_cut = False
                if cy and not uniq:
                    ok_cyc = False
                if char_ii(n, E, kruskal(n, E)) != uniq:
                    ok_ii = False
                if any(char_ii(n, E, T) != uniq for T in msts):
                    ok_ii_any = False
                if unique_mst_alg(n, E) != uniq:
                    ok_alg = False
for n, E in fresh(5, 6, 0.6, 400, weights=(1, 3)):
    msts, _ = all_msts(n, E)
    uniq = len(msts) == 1
    cu, cy = cut_condition(n, E), cycle_condition(n, E)
    stats["graphs"] += 1
    stats["unique"] += uniq
    if (cu or cy) and not uniq:
        ok_cut = ok_cyc = False
    if char_ii(n, E, kruskal(n, E)) != uniq or unique_mst_alg(n, E) != uniq:
        ok_ii = ok_alg = False
check("7.2(b) the cut bullet alone implies a unique MST", ok_cut, f"{stats['graphs']} weighted graphs")
check("7.2(b) the cycle bullet alone implies a unique MST", ok_cyc)
check("7.2(b) 'only if' is false for each bullet: unique MSTs violating the cut / cycle bullet exist",
      stats["uniq_not_cut"] > 0 and stats["uniq_not_cyc"] > 0,
      f"{stats['unique']} unique, {stats['uniq_not_cut']} violate cut, {stats['uniq_not_cyc']} violate cycle")
check("7.2(b) corrected: unique iff every non-tree edge is strictly heavier than its tree path (T from Kruskal)", ok_ii)
check("7.2(b) corrected: the same holds for every MST T, not just Kruskal's", ok_ii_any)
check("7.2(c) Kruskal twice (ties broken against T) decides uniqueness", ok_alg)

# ============================================================================ Exercise 7.3
ok_a3, ok_b3, ok_eq, ok_c3, ok_dec, nb = True, True, True, True, True, 0
for n, E in fresh(3, 7, 0.5, 400):
    T = all_msts(n, E)[0][0] if n <= 6 else kruskal(n, E)
    m = len(E)
    bridges = {i for i in range(m) if not is_connected(n, E, [j for j in range(m) if j != i])}
    nb += len(bridges)
    if not bridges <= T:
        ok_a3 = False
    cyc = all_cycles(n, E) if m <= 12 else None
    if cyc is not None:
        on_cycle = set().union(*cyc) if cyc else set()
        if bridges != set(range(m)) - on_cycle:  # useful = on no cycle = bridge
            ok_a3 = False
        dangerous = {max(C, key=lambda i: E[i][2]) for C in cyc}
        if dangerous & T:
            ok_b3 = False
        if dangerous != set(range(m)) - T:
            ok_eq = False
    # (c) reverse delete
    H = set(range(m))
    for i in sorted(range(m), key=lambda i: -E[i][2]):
        H.discard(i)
        u, v = E[i][:2]
        # brute-force "dangerous in the current graph": i is the heaviest edge of some cycle of H + i
        lighter = [j for j in H if E[j][2] < E[i][2]]
        dang_now = v in wfs_reach(n, E, lighter, u)
        removed = v in wfs_reach(n, E, H, u)
        if removed != dang_now:
            ok_dec = False
        if not removed:
            H.add(i)
    if frozenset(H) != T:
        ok_c3 = False
check("7.3(a) useful edges (on no cycle) are exactly the bridges, and all are in the MST", ok_a3,
      f"400 random graphs, {nb} bridges")
check("7.3(b) no dangerous edge is in the MST", ok_b3)
check("7.3(b) in fact dangerous edges = edges not in the MST", ok_eq)
check("7.3(c) reverse-delete: 'endpoints still connected' = 'dangerous in the current graph'", ok_dec)
check("7.3(c) reverse-delete returns the MST", ok_c3)

# ============================================================================ Exercise 7.4
ok_max, ok_fes, ok_fes_pos, nf = True, True, True, 0
for n, E in fresh(3, 6, 0.6, 300):
    trees = spanning_trees(n, E)
    best = max(weight(E, T) for T in trees)
    Eneg = [(u, v, -w) for u, v, w in E]
    T = kruskal(n, Eneg)
    if weight(E, T) != best:
        ok_max = False


def min_fes_brute(n, E):
    m = len(E)
    best = INF
    for mask in range(1 << m):
        F = [i for i in range(m) if mask >> i & 1]
        rest = [i for i in range(m) if not mask >> i & 1]
        if acyclic(n, E, rest):
            best = min(best, weight(E, F))
    return best


def min_fes_alg(n, E):
    pos = [i for i in range(len(E)) if E[i][2] > 0]
    T = kruskal(n, E, sorted(pos, key=lambda i: -E[i][2]))  # maximum spanning forest of G+
    return [i for i in range(len(E)) if i not in T]


for _ in range(400):
    n = random.randint(2, 6)
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n) if random.random() < 0.6][:10]
    E = [(u, v, random.randint(-3, 6)) for u, v in pairs]
    F = min_fes_alg(n, E)
    rest = [i for i in range(len(E)) if i not in F]
    nf += 1
    if not acyclic(n, E, rest) or weight(E, F) != min_fes_brute(n, E):
        ok_fes = False
    Ep = [(u, v, abs(w) + 1) for u, v, w in E]
    Fp = min_fes_alg(n, Ep)
    if set(range(len(Ep))) - set(Fp) != set(kruskal(n, Ep, sorted(range(len(Ep)), key=lambda i: -Ep[i][2]))):
        ok_fes_pos = False
check("7.4(a) Kruskal on negated weights = maximum spanning tree (brute force)", ok_max, "300 random graphs")
check("7.4(b) E minus a maximum spanning forest of the positive edges is a minimum feedback edge set", ok_fes,
      f"{nf} random graphs, weights -3..6, possibly disconnected, vs all edge subsets")
check("7.4(b) with positive weights it is the complement of the maximum spanning forest", ok_fes_pos)


# ============================================================================ Exercise 7.5
def update_mst(n, E, T, e, neww):
    """The page's algorithm. E is the graph with the NEW weight already in place; T the old MST."""
    old = E_old_weight[e]
    u, v = E[e][:2]
    if neww < old:
        if e in T:
            return T, "dec-in"
        P = tree_path(n, E, T, u, v)
        f = max(P, key=lambda i: E[i][2])
        if neww < E[f][2]:
            return (T - {f}) | {e}, "dec-out-swap"
        return T, "dec-out-keep"
    else:
        if e not in T:
            return T, "inc-out"
        comp = components(n, E, T - {e})
        g = min((i for i in range(len(E)) if comp[E[i][0]] != comp[E[i][1]]), key=lambda i: E[i][2])
        return (T - {e}) | {g}, ("inc-in-keep" if g == e else "inc-in-swap")


ok5, cases = True, {}
for n, E in fresh(3, 7, 0.55, 300):
    T = kruskal(n, E)
    used = {w for _, _, w in E}
    for e in range(len(E)):
        for _ in range(3):
            neww = random.randint(0, 10 * len(E) + 20)
            if neww in used:
                continue
            E_old_weight = {e: E[e][2]}
            E2 = list(E)
            E2[e] = (E[e][0], E[e][1], neww)
            T2, case = update_mst(n, E2, T, e, neww)
            cases[case] = cases.get(case, 0) + 1
            ref = all_msts(n, E2)[0] if n <= 6 else [kruskal(n, E2)]
            if [T2] != ref:
                ok5 = False
check("7.5 MST update (all four cases) = brute-force MST of the new graph", ok5,
      ", ".join(f"{k} {v}" for k, v in sorted(cases.items())))
check("7.5 every case occurs", len(cases) == 6)


# ============================================================================ Exercise 7.6(a)
def heavy_table(n, E, T):
    """Heavy[s][v] = heaviest edge on the T-path from s to v (None if s = v): one search of T per vertex."""
    adj = [[] for _ in range(n)]
    for i in T:
        a, b = E[i][:2]
        adj[a].append((b, i))
        adj[b].append((a, i))
    Heavy = [[None] * n for _ in range(n)]
    for s in range(n):
        seen = {s}
        bag = [s]
        while bag:
            p = bag.pop()
            for v, i in adj[p]:
                if v not in seen:
                    seen.add(v)
                    hp = Heavy[s][p]
                    Heavy[s][v] = i if hp is None or E[i][2] > E[hp][2] else hp
                    bag.append(v)
    return Heavy


def second_mst(n, E):
    T = kruskal(n, E)
    Heavy = heavy_table(n, E, T)
    best, choice = INF, None
    for g in range(len(E)):
        if g in T:
            continue
        u, v = E[g][:2]
        f = Heavy[u][v]
        if E[g][2] - E[f][2] < best:
            best, choice = E[g][2] - E[f][2], (g, f)
    if choice is None:
        return None
    g, f = choice
    return (T - {f}) | {g}


ok6, ok_heavy, ntrees6, ok6claim = True, True, 0, True
for n, E in fresh(3, 6, 0.6, 400):
    T = kruskal(n, E)
    Heavy = heavy_table(n, E, T)
    for s in range(n):
        for v in range(n):
            if s != v:
                P = tree_path(n, E, T, s, v)
                if Heavy[s][v] != max(P, key=lambda i: E[i][2]):
                    ok_heavy = False
    trees = sorted(spanning_trees(n, E), key=lambda T: weight(E, T))
    ntrees6 += len(trees)
    T2 = second_mst(n, E)
    if len(trees) == 1:
        if T2 is not None:
            ok6 = False
        continue
    if T2 is None or T2 == T or len(T2) != n - 1 or not acyclic(n, E, T2) or weight(E, T2) != weight(E, trees[1]):
        ok6 = False
    for T2b in trees[1:]:
        if weight(E, T2b) == weight(E, trees[1]) and len(T - T2b) != 1:
            ok6claim = False
check("7.6(a) Heavy[s, v] from one search of T per vertex = heaviest edge on the tree path", ok_heavy)
check("7.6(a) claim: EVERY second smallest spanning tree differs from T in exactly one edge", ok6claim)
check("7.6(a) best single swap T - f + g = a second smallest spanning tree (all spanning trees enumerated)", ok6,
      f"400 random graphs, {ntrees6} spanning trees")
# Figure 7.1 of the book: hexagon with a centre
F71V = ["top", "UL", "UR", "C", "LL", "LR", "B"]
ix = {v: i for i, v in enumerate(F71V)}
F71 = [("top", "UL", 8), ("top", "UR", 5), ("UL", "UR", 10), ("UL", "C", 2), ("C", "UR", 3), ("UL", "LL", 18),
       ("UR", "LR", 16), ("C", "LL", 12), ("C", "LR", 30), ("C", "B", 14), ("LL", "B", 4), ("B", "LR", 26)]
E71 = [(ix[a], ix[b], w) for a, b, w in F71]
m71, b71 = all_msts(7, E71)
T71 = m71[0]
check("Figure 7.1: MST weights {2,3,4,5,12,16}, total 42", sorted(E71[i][2] for i in T71) == [2, 3, 4, 5, 12, 16]
      and b71 == 42 and len(m71) == 1)
H71 = heavy_table(7, E71, T71)
diffs = {E71[g][2]: (E71[H71[E71[g][0]][E71[g][1]]][2], E71[g][2] - E71[H71[E71[g][0]][E71[g][1]]][2])
         for g in range(12) if g not in T71}
check("7.6(a) Figure 7.1 table: non-tree edge -> heaviest path edge, difference",
      diffs == {8: (5, 3), 10: (3, 7), 14: (12, 2), 18: (12, 6), 26: (16, 10), 30: (16, 14)}, f"{diffs}")
t71 = sorted(spanning_trees(7, E71), key=lambda T: weight(E71, T))
S71 = second_mst(7, E71)
check("7.6(a) Figure 7.1: second smallest spanning tree swaps 12 for 14, weight 44 (brute force agrees, unique)",
      weight(E71, S71) == 44 == weight(E71, t71[1]) and weight(E71, t71[2]) > 44
      and sorted(E71[i][2] for i in S71) == [2, 3, 4, 5, 14, 16], f"{len(t71)} spanning trees")


# ============================================================================ Exercise 7.7
def dense_jarnik(n, Wm, s=0):
    """The page's array version: priority(v) = lightest edge from v to T; O(V) scan per iteration."""
    inT = [False] * n
    pr = [Wm[s][v] for v in range(n)]
    edge = [(s, v) for v in range(n)]
    inT[s] = True
    T, work = [], 0
    for _ in range(n - 1):
        v, bestp = None, INF
        for x in range(n):
            work += 1
            if not inT[x] and (v is None or pr[x] < bestp):
                v, bestp = x, pr[x]
        inT[v] = True
        T.append(edge[v])
        for u in range(n):
            work += 1
            if not inT[u] and Wm[v][u] < pr[u]:
                pr[u], edge[u] = Wm[v][u], (v, u)
    return T, work


ok7, ok7w = True, True
for n, E in fresh(2, 7, 0.7, 300):
    Wm = [[INF] * n for _ in range(n)]
    for u, v, w in E:
        Wm[u][v] = Wm[v][u] = w
    T, work = dense_jarnik(n, Wm, random.randrange(n))
    key = {frozenset((u, v)): i for i, (u, v, w) in enumerate(E)}
    ids = frozenset(key[frozenset(e)] for e in T)
    ref = all_msts(n, E)[0] if n <= 6 else [kruskal(n, E)]
    if [ids] != ref:
        ok7 = False
    if work != 2 * n * (n - 1):
        ok7w = False
check("7.7 array-based Jarnik = brute-force MST", ok7, "300 random graphs")
check("7.7 its work is exactly 2V(V-1) steps, whatever E is", ok7w)


# ============================================================================ Exercise 7.8
def counting_sort(L, k, K):
    buckets = [[] for _ in range(K)]
    for t in L:
        buckets[t[k]].append(t)
    return [t for b in buckets for t in b]


def boruvka_pass(n, E):
    """One contraction pass as on the page.  E: list of (u, v, w, orig).  Returns (n', E', marked origs, comp)."""
    adj = [[] for _ in range(n)]
    for i, (u, v, w, o) in enumerate(E):
        adj[u].append(i)
        adj[v].append(i)
    marked = {min(adj[v], key=lambda i: E[i][2]) for v in range(n)}  # step 1
    madj = [[] for _ in range(n)]  # step 2: CountAndLabel on (V, marked)
    for i in marked:
        u, v = E[i][:2]
        madj[u].append(v)
        madj[v].append(u)
    comp, c = [-1] * n, 0
    for s in range(n):
        if comp[s] < 0:
            comp[s] = c
            bag = [s]
            while bag:
                x = bag.pop()
                for y in madj[x]:
                    if comp[y] < 0:
                        comp[y] = c
                        bag.append(y)
            c += 1
    L = []  # step 3
    for u, v, w, o in E:
        a, b = comp[u], comp[v]
        if a != b:
            L.append((min(a, b), max(a, b), w, o))
    L = counting_sort(counting_sort(L, 1, c), 0, c)  # step 4: radix sort on the pair
    out = []
    for t in L:
        if out and out[-1][:2] == t[:2]:
            if t[2] < out[-1][2]:
                out[-1] = t
        else:
            out.append(t)
    return c, out, {E[i][3] for i in marked}, comp


def boruvka_contract(n, E, passes=None):
    G = [(u, v, w, i) for i, (u, v, w) in enumerate(E)]
    F, sizes = set(), [(n, len(G))]
    k = 0
    while n > 1 and (passes is None or k < passes):
        n, G, mk, _ = boruvka_pass(n, G)
        F |= mk
        sizes.append((n, len(G)))
        k += 1
    return F, sizes, n, G


ok8a, ok8forest, ok8half, ok8full, ok8simple = True, True, True, True, True
for n, E in fresh(2, 9, 0.5, 400):
    G = [(u, v, w, i) for i, (u, v, w) in enumerate(E)]
    n2, G2, mk, comp = boruvka_pass(n, G)
    T = kruskal(n, E)
    if not mk <= T:
        ok8a = False
    if not acyclic(n, E, mk):
        ok8forest = False
    if not 2 * n2 <= n:
        ok8half = False
    # brute-force contraction: lightest G-edge between every pair of components
    want = {}
    for u, v, w in E:
        a, b = comp[u], comp[v]
        if a != b:
            key = (min(a, b), max(a, b))
            if key not in want or w < want[key]:
                want[key] = w
    got = {(a, b): w for a, b, w, o in G2}
    if got != want or len(got) != len(G2):
        ok8simple = False
    F, sizes, _, _ = boruvka_contract(n, E)
    if frozenset(F) != T:
        ok8full = False
check("7.8(a) marked edges are MST edges and form a forest", ok8a and ok8forest, "400 random graphs")
check("7.8(a) a pass at least halves the number of vertices", ok8half)
check("7.8(a) radix-sort contraction = lightest edge between every pair of components, no loops or parallels",
      ok8simple)
check("7.8 repeated contraction passes compute the MST", ok8full)


# (b) the hybrid bound: f(k) = k(V+E) + E + (V/2^k) log2(V/2^k)
def hybrid(V, E, k):
    Vk = max(1.0, V / 2 ** k)
    return k * (V + E) + E + Vk * max(1.0, math.log2(Vk))


ok8b, ok8b_ll, worst_ratio, worst_ll = True, True, 0.0, 0.0
for lv in range(4, 31):
    V = 2 ** lv
    for E in sorted({V - 1, V, 2 * V, 4 * V, V * lv // 4, V * lv // 2, V * lv, 4 * V * lv, V * V // 8, V * (V - 1) // 2}):
        if E < V - 1 or E > V * (V - 1) // 2:
            continue
        best = min(hybrid(V, E, k) for k in range(0, lv + 1))
        kstar = max(0, math.ceil(math.log2(V * math.log2(V) / E)))
        fk = hybrid(V, E, kstar)
        bound = E * max(1.0, math.log2(V * math.log2(V) / E))
        if fk > 2 * best + 1e-9 or fk > 6 * bound:
            ok8b = False
        worst_ratio = max(worst_ratio, fk / bound)
        kll = math.ceil(math.log2(math.log2(V)))
        fll = hybrid(V, E, kll)
        worst_ll = max(worst_ll, fll / (E * math.log2(math.log2(V))))
        if fll > 6 * E * math.log2(math.log2(V)):
            ok8b_ll = False
check("7.8(b) k* = max(0, ceil(log2(V log2 V / E))) is within a factor 2 of the best k, and "
      "f(k*) = O(E max(1, log(V log V / E)))", ok8b, f"V = 2^4..2^30, max f(k*)/bound = {worst_ratio:.2f}")
check("7.8(b) k = ceil(log2 log2 V) gives O(E log log V)", ok8b_ll, f"max ratio {worst_ll:.2f}")
ok_shrink = True
for n, E in fresh(8, 40, 0.15, 200):
    F, sizes, _, _ = boruvka_contract(n, E)
    for k, (nk, ek) in enumerate(sizes):
        if nk > n / 2 ** k or ek > len(E):
            ok_shrink = False
check("7.8(b) after k passes at most V/2^k vertices and at most E edges remain", ok_shrink, "200 random graphs")


# (c) nice graphs: grids and triangulated grids (planar)
def grid(r, c, diag=False):
    idx = lambda i, j: i * c + j
    E = []
    for i in range(r):
        for j in range(c):
            if j + 1 < c:
                E.append((idx(i, j), idx(i, j + 1)))
            if i + 1 < r:
                E.append((idx(i, j), idx(i + 1, j)))
            if diag and i + 1 < r and j + 1 < c:
                E.append((idx(i, j), idx(i + 1, j + 1)))
    ws = random.sample(range(1, 10 * len(E)), len(E))
    return r * c, [(u, v, w) for (u, v), w in zip(E, ws)]


ok8c, ok8c_planar, worst8c = True, True, 0.0
for r, c, dg in [(2, 2, False), (3, 5, True), (10, 10, False), (10, 10, True), (30, 40, True), (60, 60, False),
                 (1, 50, False), (25, 80, True)]:
    n, E = grid(r, c, dg)
    F, sizes, _, _ = boruvka_contract(n, E)
    work = sum(a + b for a, b in sizes[:-1])
    worst8c = max(worst8c, work / n)
    if frozenset(F) != kruskal(n, E) or work > 8 * n:
        ok8c = False
    if any(b > 3 * a - 6 for a, b in sizes if a >= 3):
        ok8c_planar = False
check("7.8(c) on planar grids the contraction algorithm is correct and does sum(V_i + E_i) <= 8V work", ok8c,
      f"max work/V = {worst8c:.2f}")
check("7.8(c) every contracted grid still has E_i <= 3V_i - 6 (stays planar)", ok8c_planar)


# ============================================================================ Exercise 7.9
def bottleneck_brute(n, E, s, t):
    if s == t:
        return INF
    adj = [[] for _ in range(n)]
    for u, v, w in E:
        adj[u].append((v, w))
        adj[v].append((u, w))
    best = NEG

    def dfs(x, seen, width):
        nonlocal best
        if x == t:
            best = max(best, width)
            return
        for y, w in adj[x]:
            if y not in seen:
                seen.add(y)
                dfs(y, seen, min(width, w))
                seen.discard(y)

    dfs(s, {s}, INF)
    return best


def max_spanning_forest(n, E):
    return kruskal(n, E, sorted(range(len(E)), key=lambda i: (-E[i][2], i)))


def tree_width(n, E, T, s, t):
    if s == t:
        return INF
    P = tree_path(n, E, T, s, t)
    return NEG if P is None else min(E[i][2] for i in P)


def at_most(n, E, s, t, W):
    """The page's decision procedure: bottleneck(s, t) <= W iff t is NOT reachable from s using edges > W."""
    heavy = [i for i in range(len(E)) if E[i][2] > W]
    return t not in wfs_reach(n, E, heavy, s)


def contract(n, E, e):
    """Contract edge e = xy into a new node; keep the heaviest of parallel edges.  Returns (n-1, E', map)."""
    x, y = E[e][:2]
    mp, k = {}, 0
    for v in range(n):
        if v != y:
            mp[v] = k
            k += 1
    mp[y] = mp[x]
    best = {}
    for i, (u, v, w) in enumerate(E):
        a, b = mp[u], mp[v]
        if a == b:
            continue
        key = (min(a, b), max(a, b))
        best[key] = max(best.get(key, NEG), w)
    return n - 1, [(a, b, w) for (a, b), w in best.items()], mp


# the book's figure (Exercise 7.9): same hexagon, t = top, s = LL
B9 = [("top", "UL", 1), ("top", "UR", 11), ("UL", "UR", 6), ("UL", "C", 4), ("C", "UR", 3), ("UL", "LL", 5),
      ("UR", "LR", 9), ("C", "LL", 10), ("C", "LR", 12), ("C", "B", 7), ("LL", "B", 8), ("B", "LR", 2)]
E9 = [(ix[a], ix[b], w) for a, b, w in B9]
s9, t9 = ix["LL"], ix["top"]
T9 = max_spanning_forest(7, E9)
P9 = tree_path(7, E9, T9, s9, t9)
check("7.9 book figure: bottleneck distance between s and t is 9", bottleneck_brute(7, E9, s9, t9) == 9)
check("7.9 book figure: maximum spanning tree = {12, 11, 10, 9, 8, 6}",
      sorted(E9[i][2] for i in T9) == [6, 8, 9, 10, 11, 12])
check("7.9 book figure: its s-t path is s, C, LR, UR, t with weights 10, 12, 9, 11 (the highlighted path)",
      [E9[i][2] for i in reversed(P9)] == [10, 12, 9, 11])
heavy9 = sorted(E9[i][2] for i in range(12) if E9[i][2] >= 9)
check("7.9 book figure: the edges of weight >= 9 are exactly that path, so every other s-t path uses an edge "
      "of weight <= 8", heavy9 == sorted(E9[i][2] for i in P9) and
      bottleneck_brute(7, [e for e in E9 if e[2] != 9], s9, t9) <= 8)
ok9a, ok9b, ok9ci, ok9cii, n9, nci, ncii = True, True, True, True, 0, 0, 0
for trial in range(400):
    n = random.randint(2, 7)
    if trial % 4 == 0:  # possibly disconnected, with ties
        pairs = [(u, v) for u in range(n) for v in range(u + 1, n) if random.random() < 0.35]
        E = [(u, v, random.randint(1, 5)) for u, v in pairs]
    else:
        E = random_connected(n, 0.55, "distinct" if trial % 2 else (1, 6))
    T = max_spanning_forest(n, E)
    weights = sorted({w for _, _, w in E})
    for s in range(n):
        for t in range(n):
            B = bottleneck_brute(n, E, s, t)
            n9 += 1
            if tree_width(n, E, T, s, t) != B:
                ok9a = False
            for W in [0] + weights + [w + 0.5 for w in weights]:
                if at_most(n, E, s, t, W) != (B <= W):
                    ok9b = False
            if s == t:
                continue
            for e in range(len(E)):
                if E[e][2] < B:
                    nci += 1
                    if bottleneck_brute(n, E[:e] + E[e + 1:], s, t) != B:
                        ok9ci = False
                if E[e][2] > B:
                    ncii += 1
                    n2, E2, mp = contract(n, E, e)
                    if bottleneck_brute(n2, E2, mp[s], mp[t]) != B:
                        ok9cii = False
check("7.9(a) a maximum spanning forest contains a widest path between every pair", ok9a,
      f"{n9} pairs in 400 random graphs, ties and disconnected graphs included")
check("7.9(b) 'bottleneck <= W' iff t is unreachable from s using only edges heavier than W", ok9b)
check("7.9(c)i deleting any edge lighter than B leaves the bottleneck distance B", ok9ci, f"{nci} deletions")
check("7.9(c)ii contracting any edge heavier than B leaves the bottleneck distance B", ok9cii,
      f"{ncii} contractions")


# ============================================================================ Exercise 7.10: the book's pseudocode
class UpTrees:
    def __init__(self, n, oracle):
        self.parent = list(range(n))
        self.size = [1] * n
        self.oracle = oracle
        self.steps = 0  # Find invocations (each O(1) work)
        self.changes = 0

    def find(self, v):  # Find(v) with path compression; same effect and cost as the recursive version
        path = []
        self.steps += 1
        while self.parent[v] != v:
            path.append(v)
            v = self.parent[v]
            self.steps += 1
        for x in path:
            if self.parent[x] != v:
                self.changes += 1
            self.parent[x] = v
        return v

    def union(self, u, v, ctx=None):
        ub, vb = self.find(u), self.find(v)
        child, par = self.oracle(self, ub, vb, ctx)
        self.parent[child] = par
        self.size[par] += self.size[child]

    def root(self, v):  # for the adversary only: no cost, no compression
        while self.parent[v] != v:
            v = self.parent[v]
        return v

    def depth(self, v):
        d = 0
        while self.parent[v] != v:
            v = self.parent[v]
            d += 1
        return d


def boruvka_uf(n, E, oracle, log=None, order=None):
    """Borůvka with FindSafeEdges / AddSafeEdges, literally.  E: list of (u, v, w).  log collects per-call costs."""
    D = UpTrees(n, oracle)
    order = list(range(n)) if order is None else order
    F = set()
    while True:
        # FindSafeEdges
        s0, c0 = D.steps, D.changes
        safe = [None] * n
        found = False
        for i, (u, v, w) in enumerate(E):
            ub, vb = D.find(u), D.find(v)
            if ub != vb:
                if safe[ub] is None or w < E[safe[ub]][2]:
                    safe[ub] = i
                if safe[vb] is None or w < E[safe[vb]][2]:
                    safe[vb] = i
                found = True
        depth_ok = all(D.depth(v) <= 1 for v in range(n))
        rec = dict(fse=D.steps - s0, fse_changes=D.changes - c0, depth_ok=depth_ok,
                   comps=sum(1 for v in range(n) if D.parent[v] == v), E=len(E))
        if not found:
            if log is not None:
                log.append(rec)
            break
        # AddSafeEdges
        s1 = D.steps
        for v in order:
            if safe[v] is not None:
                x, y = E[safe[v]][:2]
                if D.find(x) != D.find(y):
                    D.union(x, y, ctx=v)
                    F.add(safe[v])
        rec["ase"] = D.steps - s1
        rec["with_safe"] = sum(1 for v in range(n) if safe[v] is not None)
        if log is not None:
            log.append(rec)
    return frozenset(F), D


def random_oracle(D, a, b, ctx):
    return (a, b) if random.random() < 0.5 else (b, a)


def by_size(D, a, b, ctx):
    return (a, b) if D.size[a] <= D.size[b] else (b, a)


ok10, ok10fse, ok10depth, ok10ch, worst_fse = True, True, True, True, 0.0
ok10size, ok10ase_size, ok10calls = True, True, True
for trial in range(300):
    n = random.randint(2, 40)
    E = random_connected(n, min(1.0, 3.0 / n + 0.05))
    random.shuffle(E)
    log = []
    F, D = boruvka_uf(n, E, random_oracle if trial % 2 else by_size, log, order=random.sample(range(n), n))
    if F != kruskal(n, E):
        ok10 = False
    if len(log) > math.floor(math.log2(n)) + 1:  # number of FindSafeEdges calls
        ok10calls = False
    for rec in log:
        calls = 2 * rec["E"]
        if rec["fse"] > 2 * calls + rec["fse_changes"] or rec["fse_changes"] > n:
            ok10fse = False
        worst_fse = max(worst_fse, rec["fse"] / (rec["E"] + n))
        if not rec["depth_ok"]:
            ok10depth = False
    if trial % 2 == 0:
        # union by size: depth <= log2(size of the tree) for every vertex
        for v in range(n):
            r = v
            while D.parent[r] != r:
                r = D.parent[r]
            if D.depth(v) > math.log2(D.size[r]) + 1e-9:
                ok10size = False
        for rec in log:
            if "ase" in rec and rec["ase"] > 4 * rec["with_safe"] * (1 + math.log2(n)):
                ok10ase_size = False
check("7.10 the up-tree variant of Boruvka computes the MST (random and by-size Union)", ok10, "300 random graphs")
check("7.10 at most floor(log2 V) + 1 calls to FindSafeEdges (components at least halve per iteration)", ok10calls)
check("7.10 FindSafeEdges: Find invocations <= 2 (number of Finds) + (pointer changes), each vertex changed at most "
      "once, so O(V + E)", ok10fse, f"max invocations/(V+E) = {worst_fse:.2f}")
check("7.10 hint: when FindSafeEdges ends, every up-tree has depth <= 1", ok10depth)
check("7.10 with union by size every vertex has depth <= log2(size of its up-tree)", ok10size)
check("7.10 with union by size AddSafeEdges makes <= 4c Finds of cost <= 1 + log2 V (c = roots with a safe edge)",
      ok10ase_size)


# the counterexample: a tree on V = 2^(k+1) vertices on which AddSafeEdges costs Theta(V log V)
def bad_instance(k):
    links, cnt = [], [0]

    def build(j):
        if j == 0:
            cnt[0] += 1
            return cnt[0] - 1
        a = build(j - 1)
        b = build(j - 1)
        links.append((b, a))
        return a

    r = build(k)
    nb = cnt[0]
    par = {b: a for b, a in links}
    dep = {}
    for v in range(nb):
        d, x = 0, v
        while x in par:
            x = par[x]
            d += 1
        dep[v] = d
    BIG = nb + 1
    edges = [(b, a, dep[b] * BIG + b) for b, a in links]  # a vertex's parent edge is lighter than its child edges
    # simulate AddSafeEdges to choose each leaf's neighbour: the deepest vertex of the current up-tree
    D = UpTrees(2 * nb, lambda D, a, b, c: (a, b))
    for b, a in links:
        D.find(b), D.find(a)
        D.parent[b] = a
    leaves = list(range(nb, 2 * nb))
    W0 = (k + 2) * BIG
    leaf_depths.clear()
    for i, u in enumerate(leaves):
        dep_now = [None] * u  # depths of all existing vertices (memoized walk)
        for x in range(u):
            stack, y = [], x
            while dep_now[y] is None and D.parent[y] != y:
                stack.append(y)
                y = D.parent[y]
            if dep_now[y] is None:
                dep_now[y] = 0
            d = dep_now[y]
            while stack:
                d += 1
                dep_now[stack.pop()] = d
        v = max(range(u), key=lambda x: (dep_now[x], -x))
        leaf_depths.append(dep_now[v])
        edges.append((u, v, W0 + i))
        D.find(u), D.find(v)
        rv = D.find(v)
        D.parent[rv] = u  # the big tree goes under the new singleton
    order = [b for b, a in links] + [r] + leaves
    leafset = set(leaves)

    def adversary(D, a, b, ctx):
        # a = root of x's tree, b = root of y's tree, ctx = the vertex whose safe edge is being added
        mine = D.root(ctx)
        other = b if mine == a else a
        return (other, mine) if ctx in leafset else (mine, other)

    return 2 * nb, edges, order, adversary


ok_bad, rows, leaf_depths, ok_depthk = True, [], [], True
for k in range(3, 13):
    n, E, order, adv = bad_instance(k)
    if min(leaf_depths) < k or len(leaf_depths) != 2 ** k:
        ok_depthk = False
    log = []
    F, D = boruvka_uf(n, E, adv, log, order=order)
    ase = log[0]["ase"]
    rows.append((k, n, len(E), ase, ase / len(E)))
    if F != frozenset(range(len(E))) or len(E) != n - 1 or ase < (k + 1) * 2 ** k:
        ok_bad = False
    # union by size on the same input
    log2 = []
    F2, _ = boruvka_uf(n, E, by_size, log2, order=order)
    rows[-1] += (log2[0]["ase"] / len(E),)
    if F2 != F:
        ok_bad = False
ratios = [r[4] for r in rows]
check("7.10 counterexample: on a tree with V = 2^(k+1), AddSafeEdges (adversarial Union) makes >= (k+1) 2^k Find "
      "invocations, so cost/E grows like (log2 V)/2", ok_bad and all(b > a + 0.35 for a, b in zip(ratios, ratios[1:])),
      "; ".join(f"V={r[1]}: {r[3]} = {r[4]:.2f}E (by size {r[5]:.2f}E)" for r in rows[-4:]))
check("7.10 counterexample: every leaf's Find starts at depth >= k (so makes >= k + 1 calls)", ok_depthk)
k13 = [r for r in rows if r[1] == 2 ** 13][0]
check("7.10 numbers on the page: V = 2^13 = 8192, E = 8191: AddSafeEdges makes 90,099 Find invocations (11.0 E); "
      "union by size on the same input 5.5 E; each doubling of V adds 0.5 E",
      (k13[1], k13[2], k13[3]) == (8192, 8191, 90099) and round(k13[4], 1) == 11.0 and round(k13[5], 1) == 5.5
      and all(abs((b - a) - 0.5) < 0.01 for a, b in zip(ratios[4:], ratios[5:])),
      f"{k13[1]}, {k13[2]}, {k13[3]}, {k13[4]:.3f}E, by size {k13[5]:.3f}E")

# ============================================================================ the numbers above, as printed on the page
import os
PAGE = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "content", "2-algorithms",
                         "07-minimum-spanning-trees-exercises.md"), encoding="utf-8").read()
check("page: 7.1(b) diamond weights 1..5 and MST of weight 7",
      "$ux$, $xv$, $uv$, $uy$, $vy$ of weights $1, 2, 3, 4, 5$" in PAGE and "$T = \\{ux, xv, uy\\}$, of weight $7$" in PAGE)
check("page: 7.2 triangle 1,1,2 (trees 2, 3, 3) and H with weights 1, 2, 3, 4, 4 and MST weight 6",
      "Its three spanning trees weigh $2$, $3$ and $3$" in PAGE
      and "$ac, ax, bx, ab, bc$ of weights $1, 2, 3, 4, 4$" in PAGE and "(weight $6$;" in PAGE)
check("page: 7.6 table for Figure 7.1 and the second smallest weight 44",
      "| non-tree edge $g$ | 8 | 10 | 14 | 18 | 26 | 30 |" in PAGE
      and "| heaviest edge $f$ on its tree path | 5 | 3 | 12 | 12 | 16 | 16 |" in PAGE
      and "| extra weight $w(g) - w(f)$ | 3 | 7 | **2** | 6 | 10 | 14 |" in PAGE
      and "the second smallest spanning tree weighs $44$" in PAGE)
check("page: 7.10 numbers (V = 2^13, 90,099 Find calls, about 11E, +0.5E per doubling, 5.5E by size)",
      "For $V = 2^{13}$ it makes $90{,}099$ calls of $\\textsf{Find}$" in PAGE and "about $11E$" in PAGE
      and "adds another $0.5E$" in PAGE and "the same input costs $5.5E$" in PAGE)
check("page: 7.10 cites Tarjan-van Leeuwen for arbitrary linking and hedges the depth claim to the simulated range",
      "O(n + m\\log_{2+m/n} n)" in PAGE and "for every $V$ up to $2^{13}$" in PAGE
      and max(r[1] for r in rows) == 2 ** 13)

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: {FAIL}")
