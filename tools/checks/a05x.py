#!/usr/bin/env python3
"""Checks for content/2-algorithms/05-basic-graph-algorithms-exercises.md (solved exercises 5.1-5.19 of Erickson's
Algorithms).

Graph-theory claims (5.1-5.6) are checked on every graph with at most 5 or 6 vertices plus random larger ones;
traversal claims (5.7-5.10) by running the page's algorithms under every adjacency order or every nondeterministic
choice on small graphs; every reduction (5.11-5.19) by building the page's graph from random small inputs and comparing
its BFS/WFS answer with a brute force that applies the puzzle's rules directly (all move sequences, collapsed only by
the full configuration, or all walks up to a length bound that makes the search exhaustive). The book's examples are
reproduced."""
import itertools
import math
import random
import sys
from collections import deque

random.seed(374)
sys.setrecursionlimit(1000000)
FAIL = []
INF = float("inf")


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail != "" else ""))
    if not cond:
        FAIL.append(name)


# ============================================================================ helpers: undirected simple graphs
def all_graphs(n):
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        yield [pairs[i] for i in range(len(pairs)) if mask >> i & 1]


def random_graph(n, p):
    return [e for e in itertools.combinations(range(n), 2) if random.random() < p]


def adj_of(n, E):
    A = {v: [] for v in range(n)}
    for u, v in E:
        A[u].append(v)
        A[v].append(u)
    return A


def components(n, E):
    """Number of components, by union-find (independent of any search)."""
    par = list(range(n))

    def f(x):
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x

    for u, v in E:
        par[f(u)] = f(v)
    return len({f(x) for x in range(n)})


def connected(n, E):
    return components(n, E) == 1


def same_comp(n, E, u, v):
    par = list(range(n))

    def f(x):
        while par[x] != x:
            x = par[x]
        return x

    for a, b in E:
        par[f(a)] = f(b)
    return f(u) == f(v)


def cycles(n, A):
    """All simple cycles (length >= 3), each as a frozenset of undirected edges."""
    found = set()
    for s in range(n):
        path = [s]

        def go():
            x = path[-1]
            for y in A[x]:
                if y == s and len(path) >= 3:
                    found.add(frozenset(frozenset(e) for e in zip(path, path[1:] + [s])))
                elif y > s and y not in path:
                    path.append(y)
                    go()
                    path.pop()

        go()
    return found


def simple_paths(A, u, v):
    out = []
    path = [u]

    def go():
        x = path[-1]
        if x == v:
            out.append(tuple(path))
            return
        for y in A[x]:
            if y not in path:
                path.append(y)
                go()
                path.pop()

    go()
    return out


def prufer_tree(n):
    """Uniformly random labeled tree on n >= 2 vertices (Pruefer decoding) — independent of the predicates."""
    if n == 2:
        return [(0, 1)]
    seq = [random.randrange(n) for _ in range(n - 2)]
    deg = [1] * n
    for x in seq:
        deg[x] += 1
    E = []
    for x in seq:
        leaf = min(i for i in range(n) if deg[i] == 1)
        E.append((min(leaf, x), max(leaf, x)))
        deg[leaf] -= 1
        deg[x] -= 1
    u, v = [i for i in range(n) if deg[i] == 1]
    E.append((u, v))
    return E


def bfs_dist(adj, s):
    """Plain BFS distances (number of edges) from s in a graph given as dict vertex -> list of out-neighbors."""
    dist = {s: 0}
    Q = deque([s])
    while Q:
        v = Q.popleft()
        for w in adj[v]:
            if w not in dist:
                dist[w] = dist[v] + 1
                Q.append(w)
    return dist


def bfs_path(adj, s, t):
    par = {s: None}
    Q = deque([s])
    while Q:
        v = Q.popleft()
        for w in adj[v]:
            if w not in par:
                par[w] = v
                Q.append(w)
    if t not in par:
        return None
    p = [t]
    while par[p[-1]] is not None:
        p.append(par[p[-1]])
    return p[::-1]


def wfs_reach(adj, s):
    """WhateverFirstSearch(s) with a stack; the set of marked vertices."""
    marked, bag = set(), [s]
    while bag:
        v = bag.pop()
        if v not in marked:
            marked.add(v)
            bag.extend(adj[v])
    return marked


# ---------- the book's searches (Ch. 5), as written on the page
def recursive_dfs(A, s):
    """RecursiveDFS with parent pointers: mark v; for each edge vw: if w unmarked: parent(w) <- v; RecursiveDFS(w)."""
    parent, order = {s: None}, [s]

    def go(v):
        for w in A[v]:
            if w not in parent:
                parent[w] = v
                order.append(w)
                go(w)

    go(s)
    return order, parent


def wfs_pairs(A, s, take):
    """The book's WhateverFirstSearch with pairs (p, v) in the bag; mark when a pair comes out."""
    bag, parent, order = [(None, s)], {}, []
    while bag:
        p, v = take(bag)
        if v not in parent:
            parent[v] = p
            order.append(v)
            for w in A[v]:
                bag.append((v, w))
    return order, parent


STACK = lambda bag: bag.pop()
QUEUE = lambda bag: bag.pop(0)


def RANDOM(bag):
    return bag.pop(random.randrange(len(bag)))


def tree_edges(parent):
    return frozenset(frozenset((v, p)) for v, p in parent.items() if p is not None)


def depth_in(parent, v):
    d = 0
    while parent[v] is not None:
        v, d = parent[v], d + 1
    return d


def is_ancestor(parent, a, v):
    while v is not None:
        if v == a:
            return True
        v = parent[v]
    return False


def all_orders(A):
    """Every assignment of adjacency-list orders (product of permutations)."""
    keys = sorted(A)
    for combo in itertools.product(*[list(itertools.permutations(A[k])) for k in keys]):
        yield {k: list(c) for k, c in zip(keys, combo)}


def n_orders(A):
    return math.prod(math.factorial(len(A[k])) for k in A)


def is_tree(n, E):
    return connected(n, E) and len(E) == n - 1


# ============================================================================ Exercise 5.1 — seven definitions
print("== Exercise 5.1: seven definitions of a tree")


def has_cycle(n, E):
    return bool(cycles(n, adj_of(n, E)))


def defs(n, E):
    A = adj_of(n, E)
    conn = connected(n, E)
    acyc = not cycles(n, A)
    Es = set(E)
    d1 = conn and acyc
    d2 = acyc and components(n, E) == 1
    d3 = conn and len(E) <= n - 1
    d4 = conn and all(not connected(n, [f for f in E if f != e]) for e in E)
    d5 = acyc and len(E) >= n - 1
    d6 = acyc and all(has_cycle(n, E + [(u, v)]) for u, v in itertools.combinations(range(n), 2) if (u, v) not in Es)
    d7 = all(len(simple_paths(A, u, v)) == 1 for u, v in itertools.combinations(range(n), 2))
    return (d1, d2, d3, d4, d5, d6, d7)


ok_eq, ok_A, ok_B, cnt, ntrees = True, True, True, 0, 0
for n in range(1, 7):
    for E in all_graphs(n):
        cnt += 1
        D = defs(n, E)
        if len(set(D)) != 1:
            ok_eq = False
            print("   mismatch", n, E, D)
        ntrees += D[0]
        A = adj_of(n, E)
        cyc = cycles(n, A)
        # Lemma A: uv lies on a cycle iff u, v are connected in G - uv
        for e in E:
            on_cycle = any(frozenset(e) in c for c in cyc)
            if on_cycle != same_comp(n, [f for f in E if f != e], *e):
                ok_A = False
        # Lemma B: E >= V - c, with equality iff acyclic
        c = components(n, E)
        if not (len(E) >= n - c and ((len(E) == n - c) == (not cyc))):
            ok_B = False
check("5.1 the seven definitions agree on every graph with 1..6 vertices", ok_eq, f"{cnt} graphs, {ntrees} trees")
check("5.1 Lemma A: an edge uv is on a cycle iff u, v stay connected in G - uv", ok_A)
check("5.1 Lemma B: E >= V - c, with equality iff acyclic", ok_B)
# labeled trees on n vertices: n^(n-2) (Cayley) — sanity check of the enumeration
check("5.1 tree counts 1, 1, 3, 16, 125, 1296 (Cayley n^(n-2))",
      [sum(defs(n, E)[0] for E in all_graphs(n)) for n in range(1, 7)] == [1, 1, 3, 16, 125, 1296])

# ============================================================================ Exercise 5.2 — two vertices of degree 1
print("== Exercise 5.2: two vertices of degree 1")
ok_two, ok_ends, cnt = True, True, 0
trees = [(n, E) for n in range(2, 7) for E in all_graphs(n) if connected(n, E) and not has_cycle(n, E)]
trees += [(n, prufer_tree(n)) for n in range(7, 13) for _ in range(300)]
for n, E in trees:
    cnt += 1
    A = adj_of(n, E)
    deg = [len(A[v]) for v in range(n)]
    if sum(d == 1 for d in deg) < 2:
        ok_two = False
    # endpoints of a longest path have degree 1
    longest = max((p for u in range(n) for v in range(n) if u != v for p in simple_paths(A, u, v)), key=len)
    L = len(longest)
    for u in range(n):
        for v in range(n):
            if u != v:
                for p in simple_paths(A, u, v):
                    if len(p) == L and not (deg[p[0]] == 1 and deg[p[-1]] == 1):
                        ok_ends = False
check("5.2 every connected acyclic graph with n >= 2 has >= 2 vertices of degree 1", ok_two, f"{cnt} trees")
check("5.2 both ends of every longest path have degree 1", ok_ends)

# ============================================================================ Exercise 5.3 — bipartite graphs
print("== Exercise 5.3: bipartite graphs")


def bipartite_brute(n, E):
    return any(all((m >> u & 1) != (m >> v & 1) for u, v in E) for m in range(1 << n))


def bipartite_alg(n, A, take):
    """Page's algorithm: WFSAll; depth(v) = depth(parent) + 1 when v is marked; side = depth mod 2; test every edge."""
    depth = {}
    for r in range(n):
        if r in depth:
            continue
        bag = [(None, r)]
        while bag:
            p, v = take(bag)
            if v not in depth:
                depth[v] = 0 if p is None else depth[p] + 1
                for w in A[v]:
                    bag.append((v, w))
    return all(depth[u] % 2 != depth[v] % 2 for u in A for v in A[u])


ok_b, ok_c, ok_a, cnt = True, True, True, 0
graphs = [(n, E) for n in range(1, 6) for E in all_graphs(n)] + \
         [(n, random_graph(n, random.choice([0.2, 0.35, 0.5]))) for n in range(6, 9) for _ in range(500)]
for n, E in graphs:
    cnt += 1
    A = adj_of(n, E)
    bip = bipartite_brute(n, E)
    odd = any(len(c) % 2 for c in cycles(n, A))
    if bip == odd:
        ok_b = False
    for take in (STACK, QUEUE, RANDOM):
        if bipartite_alg(n, A, take) != bip:
            ok_c = False
    if connected(n, E) and len(E) == n - 1 and not bip:
        ok_a = False
check("5.3(a) every tree is bipartite", ok_a)
check("5.3(b) bipartite <=> every cycle is even", ok_b, f"{cnt} graphs")
check("5.3(c) WFS depth parity + edge test == brute force (stack, queue, random bag)", ok_c)

# ============================================================================ Exercise 5.4 — pecking orders
print("== Exercise 5.4: pecking orders (tournaments)")


def all_tournaments(n):
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        P = [[False] * n for _ in range(n)]
        for k, (i, j) in enumerate(pairs):
            if mask >> k & 1:
                P[i][j] = True
            else:
                P[j][i] = True
        yield P


def random_tournament(n):
    P = [[False] * n for _ in range(n)]
    for i, j in itertools.combinations(range(n), 2):
        if random.random() < 0.5:
            P[i][j] = True
        else:
            P[j][i] = True
    return P


def is_procession(P, proc):
    """Each pigeon pecks the preceding one: P[proc[i+1]][proc[i]]."""
    return all(P[proc[i + 1]][proc[i]] for i in range(len(proc) - 1))


def pecking_order(n, P):
    """Page: insert x just before the first pigeon that pecks x, or at the end if none does."""
    proc = []
    for x in range(n):
        i = next((k for k, p in enumerate(proc) if P[p][x]), len(proc))
        proc.insert(i, x)
    return proc


def has_3cycle(n, P):
    return any(P[i][j] and P[j][k] and P[k][i] for i, j, k in itertools.permutations(range(n), 3))


def has_dicycle(n, P):
    # a digraph has a directed cycle iff repeatedly deleting in-degree-0 vertices leaves something
    alive = set(range(n))
    while True:
        src = [v for v in alive if not any(P[u][v] for u in alive)]
        if not src:
            return bool(alive)
        alive -= set(src)


ok_ins, ok_uniq, ok_pos, ok_short, cnt = True, True, True, True, 0
tours = [(n, P) for n in range(1, 6) for P in all_tournaments(n)] + \
        [(n, random_tournament(n)) for n in (6, 7) for _ in range(400)]
for n, P in tours:
    cnt += 1
    proc = pecking_order(n, P)
    if sorted(proc) != list(range(n)) or not is_procession(P, proc):
        ok_ins = False
    if has_dicycle(n, P) != has_3cycle(n, P):
        ok_short = False
    if n >= 3 and not has_3cycle(n, P):
        procs = [p for p in itertools.permutations(range(n)) if is_procession(P, p)]
        if len(procs) != 1:
            ok_uniq = False
        elif any(procs[0].index(x) != sum(P[x]) for x in range(n)):  # position (0-based) = number pecked
            ok_pos = False
for n in (10, 25, 60):
    for _ in range(50):
        P = random_tournament(n)
        proc = pecking_order(n, P)
        ok_ins &= sorted(proc) == list(range(n)) and is_procession(P, proc)
check("5.4(a,b) the insertion rule always yields a procession", ok_ins, f"{cnt} small + 150 large tournaments")
check("5.4(c) a tournament with a directed cycle has a 3-cycle", ok_short)
check("5.4(c) no 3-cycle (n >= 3) => exactly one procession", ok_uniq)
check("5.4(c) ... and each pigeon's position is 1 + the number of pigeons it pecks", ok_pos)

# ============================================================================ Exercise 5.5 — Euler tours
print("== Exercise 5.5: Euler tours")


def euler_exists_brute(n, E):
    m = len(E)
    if m == 0:
        return True
    A = adj_of(n, E)
    used = set()
    start = E[0][0]  # any tour passes through E[0][0]; rotate it to start there

    def go(v, k):
        if k == m:
            return v == start
        for w in A[v]:
            e = frozenset((v, w))
            if e not in used:
                used.add(e)
                if go(w, k + 1):
                    return True
                used.discard(e)
        return False

    return go(start, 0)


def euler_tour(n, E):
    """Page's algorithm: odd degree -> None; Walk(s) appends v after all unused edges at v are followed; check length."""
    deg = [0] * n
    for u, v in E:
        deg[u] += 1
        deg[v] += 1
    if any(d % 2 for d in deg):
        return None
    if not E:
        return [0]
    L = {v: [] for v in range(n)}
    for k, (u, v) in enumerate(E):
        L[u].append((v, k))
        L[v].append((u, k))
    used, ptr, tour = [False] * len(E), [0] * n, []

    def walk(v):
        while ptr[v] < len(L[v]):
            w, k = L[v][ptr[v]]
            ptr[v] += 1
            if not used[k]:
                used[k] = True
                walk(w)
        tour.append(v)

    s = next(v for v in range(n) if deg[v] > 0)
    walk(s)
    if len(tour) < len(E) + 1:
        return None
    return tour


def is_euler_tour(E, T):
    if T is None or T[0] != T[-1]:
        return False
    steps = [frozenset(p) for p in zip(T, T[1:])]
    return sorted(map(sorted, steps)) == sorted(map(sorted, map(frozenset, E))) and len(steps) == len(E)


ok_ab, ok_c, cnt = True, True, 0
for n in range(1, 6):
    for E in all_graphs(n):
        cnt += 1
        ex = euler_exists_brute(n, E)
        A = adj_of(n, E)
        even = all(len(A[v]) % 2 == 0 for v in range(n))
        if connected(n, E) and ex != even:
            ok_ab = False
        T = euler_tour(n, E)
        if ex != (T is not None) or (T is not None and E and not is_euler_tour(E, T)):
            ok_c = False
for _ in range(3000):
    n = random.randint(4, 12)
    E = random_graph(n, random.choice([0.3, 0.5, 0.8]))
    A = adj_of(n, E)
    nontriv = [v for v in range(n) if A[v]]
    cond = all(len(A[v]) % 2 == 0 for v in range(n)) and \
        (not E or all(same_comp(n, E, nontriv[0], v) for v in nontriv))
    T = euler_tour(n, E)
    if cond != (T is not None) or (T is not None and E and not is_euler_tour(E, T)):
        ok_c = False
# random Eulerian graphs (unions of random closed walks) to exercise long tours
for _ in range(300):
    n = random.randint(3, 15)
    Es = set()
    for _ in range(random.randint(1, 6)):
        cyc = random.sample(range(n), random.randint(3, n))
        for e in zip(cyc, cyc[1:] + cyc[:1]):
            Es ^= {tuple(sorted(e))}
    E = sorted(Es)
    T = euler_tour(n, E)
    A = adj_of(n, E)
    nontriv = [v for v in range(n) if A[v]]
    one = not E or all(same_comp(n, E, nontriv[0], v) for v in nontriv)
    if one != (T is not None) or (T is not None and E and not is_euler_tour(E, T)):
        ok_c = False
check("5.5(a,b) connected graph: Euler tour exists (brute force) <=> all degrees even", ok_ab, f"{cnt} graphs")
check("5.5(c) Walk/Hierholzer returns a valid tour exactly when one exists", ok_c)


def walk_parity_log(n, E, s):
    """The page's Walk, instrumented: for every edge vw taken, record whether the moment was even (every vertex has
    an even number of unused edges), whether it was a loop resumption (not the call's first edge), and the first
    entry appended inside Walk(w)."""
    L = {v: [] for v in range(n)}
    for k, (u, v) in enumerate(E):
        L[u].append((v, k))
        L[v].append((u, k))
    used, ptr, tour, log = [False] * len(E), [0] * n, [], []

    def even():
        c = [0] * n
        for k, (u, v) in enumerate(E):
            if not used[k]:
                c[u] += 1
                c[v] += 1
        return all(x % 2 == 0 for x in c)

    def walk(v):
        taken = 0
        while ptr[v] < len(L[v]):
            w, k = L[v][ptr[v]]
            ptr[v] += 1
            if not used[k]:
                ev = even()
                used[k] = True
                before = len(tour)
                walk(w)
                log.append((v, ev, taken > 0, tour[before]))
                taken += 1
        tour.append(v)

    walk(s)
    return log


ok_res, ok_first, cnt = True, True, 0
for _ in range(1500):
    n = random.randint(3, 10)
    Es = set()
    for _ in range(random.randint(1, 5)):
        cyc = random.sample(range(n), random.randint(3, n))
        for e in zip(cyc, cyc[1:] + cyc[:1]):
            Es ^= {tuple(sorted(e))}
    E = sorted(Es)
    if not E:
        continue
    random.shuffle(E)
    log = walk_parity_log(n, E, E[0][0])
    ok_res &= all(ev for v, ev, resumed, first in log if resumed)
    ok_first &= all(first == v for v, ev, resumed, first in log if ev)
    cnt += 1
TRI_LOG = walk_parity_log(3, [(0, 1), (1, 2), (2, 0)], 0)  # s = 0 takes s-a = 0-1 first; a = 1, b = 2
check("5.5(c) parity: loops resume only at even moments; an edge taken at an even moment makes the caller's vertex "
      "the first entry appended inside the call", ok_res and ok_first, f"{cnt} random Eulerian graphs")
check("5.5(c) parity: the condition matters — on the triangle, Walk(b) called from Walk(a) appends s first",
      (1, False, False, 0) in TRI_LOG)  # caller a = 1, odd moment, first entry inside Walk(b) is s = 0

# ============================================================================ Exercise 5.6 — hypercubes
print("== Exercise 5.6: hypercubes")


def gray_cycle(d):
    C = ["00", "01", "11", "10"]
    for _ in range(d - 2):
        C = ["0" + c for c in C] + ["1" + c for c in reversed(C)]
    return C


def hamming1(a, b):
    return sum(x != y for x, y in zip(a, b)) == 1


ok_h = True
for d in range(2, 13):
    C = gray_cycle(d)
    if not (len(C) == 2 ** d == len(set(C)) and all(hamming1(C[i], C[(i + 1) % len(C)]) for i in range(len(C)))):
        ok_h = False
check("5.6(a) reflected Gray code is a Hamiltonian cycle of Q_d, d = 2..12", ok_h)


def hypercube(d):
    n = 2 ** d
    return n, [(u, u ^ (1 << b)) for u in range(n) for b in range(d) if u < u ^ (1 << b)]


ok_e = True
for d in range(0, 9):
    n, E = hypercube(d)
    T = euler_tour(n, E)
    if (T is not None) != (d % 2 == 0) or (T is not None and E and not is_euler_tour(E, T)):
        ok_e = False
    if d <= 3 and euler_exists_brute(n, E) != (d % 2 == 0):
        ok_e = False
check("5.6(b) Q_d has an Euler tour iff d is even (d = 0..8; brute force for d <= 3)", ok_e)

# ============================================================================ Exercise 5.7 — strong orientations
print("== Exercise 5.7: strongly connected orientations")


def strongly_connected(n, arcs):
    out = {v: [] for v in range(n)}
    inn = {v: [] for v in range(n)}
    for u, v in arcs:
        out[u].append(v)
        inn[v].append(u)
    return len(wfs_reach(out, 0)) == n and len(wfs_reach(inn, 0)) == n


def exists_strong_orientation(n, E):
    for mask in range(1 << len(E)):
        arcs = [(u, v) if mask >> k & 1 else (v, u) for k, (u, v) in enumerate(E)]
        if strongly_connected(n, arcs):
            return True
    return False


def dfs_orientation(n, A, E, s=0):
    """Page: RecursiveDFS(s); tree edges parent -> child, other edges descendant -> ancestor. None if not all reached."""
    order, parent = recursive_dfs(A, s)
    if len(order) < n:
        return None
    arcs = []
    for u, v in E:
        if parent[v] == u:
            arcs.append((u, v))
        elif parent[u] == v:
            arcs.append((v, u))
        elif is_ancestor(parent, u, v):  # u ancestor of v: descendant v -> ancestor u
            arcs.append((v, u))
        elif is_ancestor(parent, v, u):
            arcs.append((u, v))
        else:
            raise AssertionError("cross edge in a DFS tree")
    return arcs


def bridgeless(n, E):
    return all(same_comp(n, [f for f in E if f != e], *e) for e in E)


def shuffled(A):
    return {v: random.sample(ws, len(ws)) for v, ws in A.items()}


ok_alg, ok_char, ok_star, cnt = True, True, True, 0
graphs = [(n, E) for n in range(1, 6) for E in all_graphs(n)] + \
         [(n, random_graph(n, random.choice([0.3, 0.5]))) for n in (6, 7) for _ in range(150)]
for n, E in graphs:
    if len(E) > 12:
        continue
    cnt += 1
    ex = exists_strong_orientation(n, E)
    if ex != (connected(n, E) and bridgeless(n, E)):
        ok_char = False
    A = adj_of(n, E)
    for _ in range(4):
        A2 = shuffled(A)
        s = random.randrange(n)
        order, parent = recursive_dfs(A2, s)
        # (*) every edge between marked vertices joins an ancestor and a descendant
        for u, v in E:
            if u in parent and v in parent and not (is_ancestor(parent, u, v) or is_ancestor(parent, v, u)):
                ok_star = False
        arcs = dfs_orientation(n, A2, E, s)
        alg = arcs is not None and strongly_connected(n, arcs)
        if alg != ex:
            ok_alg = False
check("5.7 strong orientation exists (all 2^E tried) <=> connected and every edge on a cycle", ok_char, f"{cnt} graphs")
check("5.7 (*) RecursiveDFS: every edge joins an ancestor and a descendant", ok_star)
check("5.7 the DFS orientation is strongly connected exactly when some orientation is", ok_alg)

# ============================================================================ Exercise 5.8 — DFS tree = BFS tree
print("== Exercise 5.8: a tree that is both depth-first and breadth-first")
ok8, ok_same, ok_bfsdepth, cnt, both_cnt = True, True, True, 0, 0
pool = []
while len(pool) < 400:
    n = random.randint(2, 6)
    E = random_graph(n, random.choice([0.4, 0.6, 0.9]))
    if connected(n, E) and n_orders(adj_of(n, E)) <= 3000:
        pool.append((n, E))
pool += [(4, list(itertools.combinations(range(4), 2)))]  # K4
for n, E in pool:
    cnt += 1
    A = adj_of(n, E)
    Gset = frozenset(map(frozenset, E))
    for r in range(n):
        dist = bfs_dist(A, r)
        dfs_trees, stack_trees, bfs_trees = set(), set(), set()
        for O in all_orders(A):
            dfs_trees.add(tree_edges(recursive_dfs(O, r)[1]))
            stack_trees.add(tree_edges(wfs_pairs(O, r, STACK)[1]))
            o, par = wfs_pairs(O, r, QUEUE)
            bfs_trees.add(tree_edges(par))
            if any(depth_in(par, v) != dist[v] for v in range(n)):
                ok_bfsdepth = False
        if dfs_trees != stack_trees:
            ok_same = False
        for T in dfs_trees & bfs_trees:
            both_cnt += 1
            if T != Gset:
                ok8 = False
check("5.8 whatever-first search with a stack builds exactly RecursiveDFS's trees (all adjacency orders)", ok_same,
      f"{cnt} graphs, every root")
check("5.8 breadth-first tree depth = BFS distance (book's claim)", ok_bfsdepth)
check("5.8 a spanning tree that is both depth-first and breadth-first equals G", ok8, f"{both_cnt} such trees")

# ============================================================================ Exercise 5.9 — EagerWFS
print("== Exercise 5.9: EagerWFS")


def eager_wfs(A, s, take):
    marked, parent, order, bag = {s}, {s: None}, [s], [s]
    while bag:
        v = take(bag)
        for w in A[v]:
            if w not in marked:
                marked.add(w)
                parent[w] = v
                order.append(w)
                bag.append(w)
    return order, parent


ok_a, ok_b, cnt = True, True, 0
for _ in range(2000):
    n = random.randint(1, 10)
    E = random_graph(n, random.choice([0.15, 0.3, 0.6]))
    A = shuffled(adj_of(n, E))
    s = random.randrange(n)
    reach = wfs_reach(A, s)
    for take in (STACK, QUEUE, RANDOM):
        order, parent = eager_wfs(A, s, take)
        T = tree_edges(parent)
        if set(order) != reach or len(order) != len(set(order)):
            ok_a = False
        # parent edges: a spanning tree of the marked set (|T| = k - 1 and connected)
        idx = {v: i for i, v in enumerate(sorted(reach))}
        if len(T) != len(reach) - 1 or not connected(len(reach), [tuple(idx[x] for x in e) for e in T]):
            ok_a = False
        if any(frozenset(e) not in set(map(frozenset, E)) for e in T):
            ok_a = False
    if eager_wfs(A, s, QUEUE) != wfs_pairs(A, s, QUEUE):
        ok_b = False
    cnt += 1
check("5.9(a) EagerWFS marks exactly the reachable vertices; parent edges form a spanning tree", ok_a, f"{cnt} graphs")
check("5.9(b) EagerWFS with a queue == BFS: same marking order, same parents", ok_b)


def all_eager_trees(A, s):
    """Every tree EagerWFS(s) can build with ANY bag (every choice of the item taken out)."""
    out = set()

    def go(bag, parent):
        if not bag:
            out.add(tree_edges(parent))
            return
        for i in range(len(bag)):
            v = bag[i]
            rest = bag[:i] + bag[i + 1:]
            p2, b2 = dict(parent), list(rest)
            for w in A[v]:
                if w not in p2:
                    p2[w] = v
                    b2.append(w)
            go(b2, p2)

    go([s], {s: None})
    return out


TRI = adj_of(3, [(0, 1), (0, 2), (1, 2)])
eager_T = set().union(*[all_eager_trees(O, 0) for O in all_orders(TRI)])
dfs_T = {tree_edges(recursive_dfs(O, 0)[1]) for O in all_orders(TRI)}
star = frozenset({frozenset((0, 1)), frozenset((0, 2))})
check("5.9(c) triangle: every EagerWFS tree (any bag, any order) is the star at s", eager_T == {star})
check("5.9(c) triangle: every RecursiveDFS tree is a path, never the star", len(dfs_T) == 2 and star not in dfs_T,
      sorted(sorted(map(sorted, t)) for t in dfs_T))
dfs_T_any = {tree_edges(recursive_dfs(O, r)[1]) for O in all_orders(TRI) for r in range(3)}
check("5.9(c) triangle: with other start vertices RecursiveDFS can build the star at s (so both must start at s)",
      star in dfs_T_any)
K4A = adj_of(4, list(itertools.combinations(range(4), 2)))
eager_K4 = set()
for O in all_orders(K4A):
    for r in range(4):
        eager_K4 |= all_eager_trees(O, r)
dfs_K4 = {tree_edges(recursive_dfs(O, r)[1]) for O in all_orders(K4A) for r in range(4)}
check("5.9(c) K4, any start, any order, any bag: EagerWFS trees are the stars at the start, RecursiveDFS trees are "
      "Hamiltonian paths; none in common",
      all(any(sum(r in e for e in T) == 3 for r in range(4)) for T in eager_K4)
      and all(max(sum(v in e for e in T) for v in range(4)) == 2 for T in dfs_K4) and not (eager_K4 & dfs_K4),
      f"{len(eager_K4)} eager, {len(dfs_K4)} dfs trees")

# ============================================================================ Exercise 5.10 — three colors
print("== Exercise 5.10: three-color search")
ok_inv, ok_end, ok_steps, cnt = True, True, True, 0
for _ in range(1500):
    n = random.randint(1, 10)
    E = random_graph(n, random.choice([0.15, 0.3, 0.6]))
    A = adj_of(n, E)
    s = random.randrange(n)
    color = {v: "W" for v in range(n)}
    color[s] = "G"
    parent, steps = {s: None}, 0
    while any(c == "G" for c in color.values()):
        v = random.choice([x for x in range(n) if color[x] == "G"])
        whites = [w for w in A[v] if color[w] == "W"]
        if not whites:
            color[v] = "B"
        else:
            w = random.choice(whites)
            parent[w] = v
            color[w] = "G"
        steps += 1
        if any(color[u] == "B" and color[w] == "W" for u in range(n) for w in A[u]):
            ok_inv = False
    reach = wfs_reach(A, s)
    if any((color[v] == "B") != (v in reach) or color[v] == "G" for v in range(n)):
        ok_end = False
    T = tree_edges(parent)
    idx = {v: i for i, v in enumerate(sorted(reach))}
    if set(parent) != reach or len(T) != len(reach) - 1 or not connected(len(reach), [tuple(idx[x] for x in e) for e in T]):
        ok_end = False
    if steps > 2 * n:
        ok_steps = False
    cnt += 1
check("5.10(a) no black vertex is ever adjacent to a white one", ok_inv, f"{cnt} random runs")
check("5.10(b) at the end: reachable = black, others white, parent edges = spanning tree", ok_end)
check("5.10(b) at most 2V steps", ok_steps)


def three_color_runs(A, s, kind, push_v_first=True):
    """All runs of ThreeColorStackSearch / ThreeColorQueueSearch: every choice of white neighbor.
    Returns the set of (order in which vertices turn gray, parent pairs); asserts the stack invariant."""
    out = set()
    inv = [True]

    def go(color, parent, store, order):
        grays = [v for v in color if color[v] == "G"]
        if kind == "stack" and sorted(store) != sorted(grays):
            inv[0] = False
        if kind == "stack" and len(store) > 1 and any(parent[store[i]] != store[i - 1] for i in range(1, len(store))):
            inv[0] = False
        if not grays:
            out.add((tuple(order), frozenset(parent.items())))
            return
        if kind == "stack":
            v, rest = store[-1], store[:-1]
        else:
            v, rest = store[0], store[1:]
        whites = [w for w in A[v] if color[w] == "W"]
        if not whites:
            c2 = dict(color)
            c2[v] = "B"
            go(c2, parent, rest, order)
            return
        for w in whites:
            c2, p2 = dict(color), dict(parent)
            c2[w] = "G"
            p2[w] = v
            go(c2, p2, rest + ([v, w] if push_v_first else [w, v]), order + [w])

    color = {v: "W" for v in A}
    color[s] = "G"
    go(color, {s: None}, [s], [s])
    return out, inv[0]


ok_c, ok_inv_c, cnt = True, True, 0
pool = []
while len(pool) < 300:
    n = random.randint(1, 6)
    E = random_graph(n, random.choice([0.3, 0.5, 0.8]))
    if n_orders(adj_of(n, E)) <= 2000:
        pool.append((n, E))
pool.append((4, list(itertools.combinations(range(4), 2))))
for n, E in pool:
    A = adj_of(n, E)
    s = random.randrange(n)
    runs, inv = three_color_runs(A, s, "stack")
    rec = set()
    for O in all_orders(A):
        order, parent = recursive_dfs(O, s)
        rec.add((tuple(order), frozenset(parent.items())))
    if runs != rec:
        ok_c = False
    ok_inv_c &= inv
    cnt += 1
check("5.10(c) ThreeColorStackSearch runs == RecursiveDFS runs over all adjacency orders (order + parents)", ok_c,
      f"{cnt} graphs")
check("5.10(c) the stack always holds the gray vertices, each once, along a parent path", ok_inv_c)
K4 = adj_of(4, list(itertools.combinations(range(4), 2)))
bfsK4 = {tree_edges(wfs_pairs(O, 0, QUEUE)[1]) for O in all_orders(K4)}
starK4 = frozenset(frozenset((0, v)) for v in (1, 2, 3))
okd = bfsK4 == {starK4}
for pv in (True, False):
    runs, _ = three_color_runs(K4, 0, "queue", pv)
    trees_q = {frozenset(frozenset((v, p)) for v, p in par if p is not None) for _, par in runs}
    okd &= len(trees_q) > 0 and starK4 not in trees_q
    okd &= all(max(depth_in(dict(par), v) for v in range(4)) == 2 for _, par in runs)
check("5.10(d) K4: every BFS tree is the star; no ThreeColorQueue run (either push order) builds it", okd)


# ============================================================================ reductions: shared brute force
def first_goal_time(start, moves, goal, limit):
    """Exhaustive search over all move sequences, collapsed by configuration: cur = the set of configurations reachable
    by exactly t moves, t = 0..limit. Returns the first t with a goal configuration, else None. With limit >= (number
    of configurations) - 1 this is exact, because a shortest solution never repeats a configuration."""
    cur = {start}
    for t in range(limit + 1):
        if any(goal(c) for c in cur):
            return t
        cur = {d for c in cur for d in moves(c)}
    return None


def sequences_endpoints(start, moves, t):
    """Naive enumeration of every move sequence of length t (no collapsing) — cross-checks the level sets."""
    out, stack = set(), [(start, 0)]
    while stack:
        c, k = stack.pop()
        if k == t:
            out.add(c)
            continue
        for d in moves(c):
            stack.append((d, k + 1))
    return out


DIRS = ((-1, 0), (1, 0), (0, -1), (0, 1))

# ============================================================================ Exercise 5.11 — number maze
print("== Exercise 5.11: number maze")


def maze_graph(M):
    """Page: vertex (i, j) per square; directed edge (i, j) -> (i -+ k, j), (i, j -+ k) inside the grid, k = M[i][j]."""
    n = len(M)
    return {(i, j): [(i + M[i][j] * di, j + M[i][j] * dj) for di, dj in DIRS
                     if 0 <= i + M[i][j] * di < n and 0 <= j + M[i][j] * dj < n]
            for i in range(n) for j in range(n)}


def maze_rules(M):
    n = len(M)

    def moves(pos):
        i, j = pos
        k = M[i][j]
        cand = [(i - k, j), (i + k, j), (i, j - k), (i, j + k)]  # up, down, left, right
        return {(a, b) for a, b in cand if 0 <= a < n and 0 <= b < n}

    return moves


FIG514 = [[3, 5, 7, 4, 6], [5, 3, 1, 5, 3], [2, 8, 3, 1, 4], [4, 5, 7, 2, 3], [3, 1, 3, 2, 1]]  # goal label unused
d = bfs_dist(maze_graph(FIG514), (0, 0))
MAZE_PATH = bfs_path(maze_graph(FIG514), (0, 0), (4, 4))
check("5.11 Figure 5.14: BFS distance from (1,1) to (5,5) is 8", d.get((4, 4)) == 8, d.get((4, 4)))
check("5.11 Figure 5.14: the goal's label does not matter",
      all(bfs_dist(maze_graph([r[:4] + [g] if i == 4 else r for i, r in enumerate(FIG514)]), (0, 0))[(4, 4)] == 8
          for g in range(1, 9)))
print("     one shortest solution:", [(i + 1, j + 1) for i, j in MAZE_PATH])
check("5.11 Figure 5.14: BFS finds the book's drawn solution R3 D4 L2 R1 U3 L1 R3 D3",
      MAZE_PATH == [(0, 0), (0, 3), (4, 3), (4, 1), (4, 2), (1, 2), (1, 1), (1, 4), (4, 4)])
GTERM = maze_graph(FIG514)
GTERM[(4, 4)] = []  # the goal square has no label: the token stops there
dT = bfs_dist(GTERM, (0, 0))
FIG_DIST = [[0, None, 6, 1, 3], [5, 6, 5, 4, 7], [5, None, 4, 3, 4], [1, 3, None, 4, 2], [4, 3, 4, 2, 8]]
check("5.11 figure: the BFS distance grid (3 unreachable squares)",
      all(dT.get((i, j)) == FIG_DIST[i][j] for i in range(5) for j in range(5)))
ok, cnt, unsolv = True, 0, 0
for _ in range(1500):
    n = random.randint(1, 5)
    M = [[random.randint(1, max(1, n - 1)) for _ in range(n)] for _ in range(n)]
    page = bfs_dist(maze_graph(M), (0, 0)).get((n - 1, n - 1))
    brute = first_goal_time((0, 0), maze_rules(M), lambda c: c == (n - 1, n - 1), n * n)
    if page != brute:
        ok = False
        print("   ", M, page, brute)
    for t in range(4):
        cur = {(0, 0)}
        for _ in range(t):
            cur = {d for c in cur for d in maze_rules(M)(c)}
        if cur != sequences_endpoints((0, 0), maze_rules(M), t):
            ok = False
    unsolv += page is None
    cnt += 1
check("5.11 BFS in the page's graph == exhaustive move search", ok, f"{cnt} random mazes, {unsolv} unsolvable")

# ============================================================================ Exercise 5.12 — snakes and ladders
print("== Exercise 5.12: snakes and ladders")


def sl_graph(n, k, jumps):
    """Page: dest(j) = other end if j is a snake's top or a ladder's bottom, else j; edge i -> dest(j), i < j <= i+k."""
    N = n * n
    dest = {j: jumps.get(j, j) for j in range(1, N + 1)}
    return {i: [dest[j] for j in range(i + 1, min(i + k, N) + 1)] for i in range(1, N + 1)}


def sl_rules(n, k, jumps):
    N = n * n

    def moves(i):
        out = set()
        for step in range(1, k + 1):
            j = i + step
            if j > N:
                break
            out.add(jumps[j] if j in jumps else j)  # slide down a snake / climb a ladder
        return out

    return moves


def row(n, sq):
    return (sq - 1) // n


SNAKES = {98: 6, 95: 71, 79: 40, 67: 10, 27: 17}
LADDERS = {3: 42, 8: 54, 24: 86, 50: 93, 58: 65, 59: 81}
J515 = {**SNAKES, **LADDERS}
ends = list(J515) + list(J515.values())
check("5.12 Figure 5.15 as read: 5 snakes down, 6 ladders up, distinct endpoints in different rows",
      len(ends) == len(set(ends)) == 22 and all(a > b for a, b in SNAKES.items()) and
      all(a < b for a, b in LADDERS.items()) and all(row(10, a) != row(10, b) for a, b in J515.items()))
SL = {}
for k in range(1, 13):
    SL[k] = bfs_dist(sl_graph(10, k, J515), 1).get(100)
    if k <= 8:
        check(f"5.12 Figure 5.15, k = {k}: BFS == exhaustive move search",
              SL[k] == first_goal_time(1, sl_rules(10, k, J515), lambda c: c == 100, 100), SL[k])
print("     Figure 5.15 minimum moves for k = 1..12:", SL)
check("5.12 Figure 5.15, k = 6: 5 moves, e.g. 1 ->(3) 42 -> 44 ->(50) 93 -> 94 -> 100", SL[6] == 5 and
      all(b in sl_graph(10, 6, J515)[a] for a, b in zip([1, 42, 44, 93, 94, 100], [42, 44, 93, 94, 100])))
REST1 = set(bfs_dist(sl_graph(10, 1, J515), 1))  # squares where the token can rest with k = 1
LAND1 = {i + 1 for i in REST1}  # squares it can land on
check("5.12 Figure 5.15, k = 1: square 100 is unreachable; the forced route cycles through 93, 94, 95 (-> 71), "
      "..., 79 (-> 40), ..., 50 (-> 93) and never lands beyond 95",
      SL[1] is None and max(LAND1) == 95 and 98 not in LAND1
      and {93, 94, 71, 78, 40, 49} <= REST1 and {95, 79, 50} <= LAND1 and max(REST1) == 94)
SL_PATH = bfs_path(sl_graph(10, 6, J515), 1, 100)
print("     k = 6, one shortest route (squares where the token rests):", SL_PATH)
SL_NOJ = bfs_dist(sl_graph(10, 6, {}), 1)[100]
check("5.12 the empty 10x10 board needs ceil(99/6) = 17 moves with k = 6", SL_NOJ == 17, SL_NOJ)
ok, cnt = True, 0
for _ in range(1500):
    n = random.randint(2, 5)
    N = n * n
    k = random.randint(1, 4)
    free = list(range(2, N))
    random.shuffle(free)
    jumps = {}
    while len(free) >= 2 and random.random() < 0.7:
        a, b = free.pop(), free.pop()
        if row(n, a) != row(n, b):
            jumps[a] = b  # a snake if a > b, a ladder if a < b
    page = bfs_dist(sl_graph(n, k, jumps), 1).get(N)
    brute = first_goal_time(1, sl_rules(n, k, jumps), lambda c: c == N, N)
    ok &= page == brute
    cnt += 1
check("5.12 BFS in the page's graph == exhaustive move search", ok, f"{cnt} random boards")

# ============================================================================ Exercise 5.13 — Vidrach Itky Leda
print("== Exercise 5.13: Vidrach Itky Leda")


def vil_graph(M):
    """Page: vertex (r, b), r != b; move red by M[b] or blue by M[r] in one of 4 directions, inside, onto a free square."""
    n = len(M)
    sq = [(i, j) for i in range(n) for j in range(n)]
    inside = lambda p: 0 <= p[0] < n and 0 <= p[1] < n
    adj = {}
    for r in sq:
        for b in sq:
            if r == b:
                continue
            out = []
            for di, dj in DIRS:
                k = M[b[0]][b[1]]
                r2 = (r[0] + k * di, r[1] + k * dj)
                if inside(r2) and r2 != b:
                    out.append((r2, b))
                k = M[r[0]][r[1]]
                b2 = (b[0] + k * di, b[1] + k * dj)
                if inside(b2) and b2 != r:
                    out.append((r, b2))
            adj[(r, b)] = out
    return adj


def vil_rules(M):
    n = len(M)

    def moves(c):
        red, blue = c
        out = set()
        for (mi, mj), other, which in ((red, blue, 0), (blue, red, 1)):
            k = M[other[0]][other[1]]  # distance set by the OTHER token
            for a, b in ((mi - k, mj), (mi, mj + k), (mi + k, mj), (mi, mj - k)):  # up, right, down, left
                if 0 <= a < n and 0 <= b < n and (a, b) != other:
                    out.add(((a, b), blue) if which == 0 else (red, (a, b)))
        return out

    return moves


FIG516 = [[1, 2, 4, 3], [3, 4, 1, 2], [3, 1, 2, 3], [2, 3, 1, 2]]
G516 = vil_graph(FIG516)
d = bfs_dist(G516, ((0, 0), (3, 3)))
check("5.13 Figure 5.16: BFS distance from (red TL, blue BR) to (red BR, blue TL) is 5", d.get(((3, 3), (0, 0))) == 5,
      d.get(((3, 3), (0, 0))))
BOOK516 = [((0, 0), (3, 3)), ((2, 0), (3, 3)), ((2, 0), (0, 3)), ((2, 3), (0, 3)), ((2, 3), (0, 0)), ((3, 3), (0, 0))]
check("5.13 Figure 5.16: the book's five moves are edges of the page's graph",
      all(b in G516[a] for a, b in zip(BOOK516, BOOK516[1:])))
check("5.13 the graph has n^2(n^2-1) vertices and at most 8 out-edges each",
      len(G516) == 16 * 15 and max(len(v) for v in G516.values()) <= 8)
ok, cnt, unsolv = True, 0, 0
for _ in range(400):
    n = random.randint(2, 4)
    M = [[random.randint(1, n) for _ in range(n)] for _ in range(n)]
    page = bfs_dist(vil_graph(M), ((0, 0), (n - 1, n - 1))).get(((n - 1, n - 1), (0, 0)))
    brute = first_goal_time(((0, 0), (n - 1, n - 1)), vil_rules(M), lambda c: c == ((n - 1, n - 1), (0, 0)),
                            n * n * (n * n - 1))
    ok &= page == brute
    unsolv += page is None
    cnt += 1
check("5.13 BFS in the page's graph == exhaustive move search", ok, f"{cnt} random puzzles, {unsolv} unsolvable")

# ============================================================================ Exercise 5.14 — walks of length 0 mod 3
print("== Exercise 5.14: walks whose length is divisible by 3")


def mod3_graph(G):
    """Page: vertices (v, i), i in {0,1,2}; edge (u, i) -> (v, i+1 mod 3) for every u -> v."""
    return {(u, i): [(v, (i + 1) % 3) for v in G[u]] for u in G for i in range(3)}


def walks_upto(G, s, L, ok_step=None):
    """Naive enumeration of every walk from s with at most L edges: yields (end vertex, length, walk)."""
    stack = [(s, [s])]
    while stack:
        v, w = stack.pop()
        yield v, len(w) - 1, w
        if len(w) - 1 < L:
            for x in G[v]:
                stack.append((x, w + [x]))


EX14 = {"s": ["w"], "w": ["t", "y"], "x": ["s"], "y": ["x", "z"], "z": ["t"], "t": []}
H14 = mod3_graph(EX14)
check("5.14 example: (t,0) reachable from (s,0)", ("t", 0) in wfs_reach(H14, ("s", 0)))
WALK14 = ["s", "w", "y", "x", "s", "w", "t"]
check("5.14 example: s w y x s w t is a walk of length 6", all(b in EX14[a] for a, b in zip(WALK14, WALK14[1:])))
check("5.14 example: and 6 is the shortest such length", bfs_dist(H14, ("s", 0))[("t", 0)] == 6)
ok, cnt, yes = True, 0, 0
for _ in range(1500):
    n = random.randint(1, 5)
    V = list(range(n))
    G = {v: [w for w in V if w != v and random.random() < 0.3] for v in V}
    s, t = random.choice(V), random.choice(V)
    page = (t, 0) in wfs_reach(mod3_graph(G), (s, 0))
    brute = any(v == t and ln % 3 == 0 for v, ln, _ in walks_upto(G, s, 3 * n - 1))
    ok &= page == brute
    yes += page
    cnt += 1
check("5.14 WFS in V x {0,1,2} == brute force over all walks of length < 3V", ok, f"{cnt} random digraphs, {yes} yes")

# ============================================================================ Exercise 5.15 — no three in a row
print("== Exercise 5.15: no three consecutive edges of the same color")


def rb_graph(V, edges, s):
    """Page: vertices (v, c, k) (last color c, run length k in {1, 2}) and a start vertex; edges as described."""
    START = ("start",)
    adj = {START: []}
    for v in V:
        for c in "RB":
            for k in (1, 2):
                adj[(v, c, k)] = []
    for u, v, c in edges:
        if u == s:
            adj[START].append((v, c, 1))
        for c0 in "RB":
            if c != c0:
                adj[(u, c0, 1)].append((v, c, 1))
                adj[(u, c0, 2)].append((v, c, 1))
            else:
                adj[(u, c0, 1)].append((v, c, 2))
    return adj, START


def rb_answer(V, edges, s, t):
    adj, START = rb_graph(V, edges, s)
    if s == t:
        return 0
    d = bfs_dist(adj, START)
    return min([d[(t, c, k)] for c in "RB" for k in (1, 2) if (t, c, k) in d], default=INF)


def legal(colors):
    return all(not (colors[i] == colors[i + 1] == colors[i + 2]) for i in range(len(colors) - 2))


def rb_brute(V, edges, s, t, L):
    out = {v: [] for v in V}
    for u, v, c in edges:
        out[u].append((v, c))
    best = INF
    stack = [(s, "")]
    while stack:
        v, cols = stack.pop()
        if v == t:
            best = min(best, len(cols))
        if len(cols) < L:
            for w, c in out[v]:
                if legal(cols[-2:] + c):
                    stack.append((w, cols + c))
    return best


V15 = list("sabcdt")
E15 = [("s", "a", "R"), ("a", "b", "R"), ("b", "t", "R"), ("t", "d", "R"), ("d", "c", "R"), ("c", "s", "R"),
       ("c", "a", "B"), ("d", "s", "B"), ("b", "d", "B"), ("t", "a", "B")]
check("5.15 example: shortest legal walk from s to t has 7 edges", rb_answer(V15, E15, "s", "t") == 7,
      rb_answer(V15, E15, "s", "t"))
W15 = [("s", "a"), ("a", "b"), ("b", "d"), ("d", "c"), ("c", "a"), ("a", "b"), ("b", "t")]
col15 = {(u, v): c for u, v, c in E15}
check("5.15 example: the book's walk s a b d c a b t is legal (RRBRBRR)",
      all(e in col15 for e in W15) and legal("".join(col15[e] for e in W15)) and
      "".join(col15[e] for e in W15) == "RRBRBRR")
check("5.15 example: brute force agrees", rb_brute(V15, E15, "s", "t", 12) == 7)
check("5.15 the page's graph has 4V + 1 vertices and at most 4E edges",
      len(rb_graph(V15, E15, "s")[0]) == 4 * 6 + 1 and
      sum(map(len, rb_graph(V15, E15, "s")[0].values())) <= 4 * len(E15))
ok, cnt, fin = True, 0, 0
for _ in range(1500):
    n = random.randint(1, 4)
    V = list(range(n))
    edges = [(u, v, random.choice("RB")) for u in V for v in V if u != v and random.random() < 0.45]
    s, t = random.choice(V), random.choice(V)
    page = rb_answer(V, edges, s, t)
    brute = rb_brute(V, edges, s, t, 4 * n)
    ok &= page == brute
    fin += page < INF
    cnt += 1
check("5.15 BFS in the page's graph == brute force over all walks of length <= 4V", ok, f"{cnt} random, {fin} solvable")

# ============================================================================ Exercise 5.16 — French flag walks
print("== Exercise 5.16: French flag walks")
FLAG = {0: "R", 1: "W", 2: "B"}


def flag_graph(V, edges):
    """Page: vertices (v, i); edge (u, i) -> (w, i+1 mod 3) iff u -> w has color red/white/blue for i = 0/1/2."""
    adj = {(v, i): [] for v in V for i in range(3)}
    for u, w, c in edges:
        for i in range(3):
            if c == FLAG[i]:
                adj[(u, i)].append((w, (i + 1) % 3))
    return adj


def flag_brute(V, edges, v, L):
    out = {x: [] for x in V}
    for a, b, c in edges:
        out[a].append((b, c))
    seen, stack = set(), [(v, 0)]
    while stack:
        x, k = stack.pop()
        seen.add(x)
        if k < L:
            for y, c in out[x]:
                if c == FLAG[k % 3]:
                    stack.append((y, k + 1))
    return seen


ok, cnt = True, 0
for _ in range(1500):
    n = random.randint(1, 5)
    V = list(range(n))
    edges = [(a, b, random.choice("RWB")) for a in V for b in V if a != b and random.random() < 0.5]
    v = random.choice(V)
    G = flag_graph(V, edges)
    page = {w for (w, i) in wfs_reach(G, (v, 0))}
    ok &= page == flag_brute(V, edges, v, 3 * n - 1)
    ok &= sum(map(len, G.values())) == len(edges)
    cnt += 1
check("5.16 WFS from (v,0) == brute force over all French flag walks of length < 3V; E' = E", ok, f"{cnt} random")

# ============================================================================ Exercise 5.17 — Judy's teleports
print("== Exercise 5.17: teleports with cost divisible by 5")


def judy_a(n, ways, s, t):
    """Page: vertices (g, r), r = cost so far mod 5; edges (g, r) -> (h, r + c(e) mod 5) both ways along e = gh."""
    adj = {(g, r): [] for g in range(n) for r in range(5)}
    for g, h, c in ways:
        for r in range(5):
            adj[(g, r)].append((h, (r + c) % 5))
            adj[(h, r)].append((g, (r + c) % 5))
    return bfs_dist(adj, (s, 0)).get((t, 0), INF), adj


def judy_b(n, ways, s, t):
    """Page: vertices (g, r, f), f = coupon used; paying edges keep f, free edges (g, r, 0) -> (h, r, 1)."""
    adj = {(g, r, f): [] for g in range(n) for r in range(5) for f in (0, 1)}
    for g, h, c in ways:
        for r in range(5):
            for f in (0, 1):
                adj[(g, r, f)].append((h, (r + c) % 5, f))
                adj[(h, r, f)].append((g, (r + c) % 5, f))
            adj[(g, r, 0)].append((h, r, 1))
            adj[(h, r, 0)].append((g, r, 1))
    d = bfs_dist(adj, (s, 0, 0))
    return min(d.get((t, 0, 0), INF), d.get((t, 0, 1), INF)), d.get((t, 0, 1), INF), adj


def judy_brute(n, ways, s, t, L, coupon):
    """Level sets of (galaxy, exact total cost, coupon used) after exactly l teleports — no mod-5 abstraction."""
    cur = {(s, 0, False)}
    best_opt, best_forced = INF, INF
    for l in range(L + 1):
        for g, cost, used in cur:
            if g == t and cost % 5 == 0:
                if not coupon and not used:
                    best_opt = min(best_opt, l)
                if coupon:
                    best_opt = min(best_opt, l)
                    if used:
                        best_forced = min(best_forced, l)
        nxt = set()
        for g, cost, used in cur:
            for a, b, c in ways:
                for x, y in ((a, b), (b, a)):
                    if x == g:
                        nxt.add((y, cost + c, used))
                        if coupon and not used:
                            nxt.add((y, cost, True))
        cur = nxt
    return best_opt, best_forced


ok_a, ok_b, ok_size, cnt = True, True, True, 0
for _ in range(600):
    n = random.randint(1, 4)
    ways = [(random.randrange(n), random.randrange(n), random.randint(1, 12)) for _ in range(random.randint(0, 5))]
    ways = [(g, h, c) for g, h, c in ways if g != h]
    s, t = random.randrange(n), random.randrange(n)
    pa, adja = judy_a(n, ways, s, t)
    pb, pbf, adjb = judy_b(n, ways, s, t)
    ok_a &= pa == judy_brute(n, ways, s, t, 5 * n, False)[0]
    ok_b &= (pb, pbf) == judy_brute(n, ways, s, t, 10 * n, True)
    m = len(ways)
    ok_size &= len(adja) == 5 * n and sum(map(len, adja.values())) == 10 * m
    ok_size &= len(adjb) == 10 * n and sum(map(len, adjb.values())) == 30 * m
    cnt += 1
check("5.17(a) BFS from (s,0) to (t,0) == exhaustive search over walks with exact costs", ok_a, f"{cnt} random")
check("5.17(b) min over (t,0,0),(t,0,1) [coupon optional] and (t,0,1) [coupon used] == exhaustive search", ok_b)
check("5.17 graph sizes: 5n vertices/10m edges, 10n vertices/30m edges", ok_size)

# ============================================================================ Exercise 5.18 — Three Seashells
print("== Exercise 5.18: Three Seashells")


def shells_graph(A):
    """Page: vertices = ordered triples of distinct vertices; (p,q,r) -> (p',q',r') if pp', qq', rr' in E, distinct."""
    adj = {}
    for p, q, r in itertools.permutations(list(A), 3):
        adj[(p, q, r)] = [(p2, q2, r2) for p2 in A[p] for q2 in A[q] for r2 in A[r] if len({p2, q2, r2}) == 3]
    return adj


def shells_solvable(A, abc, xyz):
    R = wfs_reach(shells_graph(A), abc)
    return any(perm in R for perm in itertools.permutations(xyz))


def shells_rules(A):
    def moves(S):  # S = frozenset of the three token positions; every token moves along an edge
        p, q, r = sorted(S)
        return {frozenset((a, b, c)) for a in A[p] for b in A[q] for c in A[r] if len({a, b, c}) == 3}

    return moves


SH_V = ["a", "b", "c", "p", "q", "r", "x", "y", "z"]
SH_E = [("a", "b"), ("b", "c"), ("a", "p"), ("b", "q"), ("p", "q"), ("q", "r"), ("q", "x"), ("q", "y"), ("r", "z")]
SH_A = {v: [] for v in SH_V}
for u, v in SH_E:
    SH_A[u].append(v)
    SH_A[v].append(u)
SHG = shells_graph(SH_A)
check("5.18 Figure 5.17 as drawn: NOT solvable (WFS on triples)", not shells_solvable(SH_A, ("a", "b", "c"), ("x", "y", "z")))
check("5.18 Figure 5.17 as drawn: brute force over move sequences agrees (no solution)",
      first_goal_time(frozenset("abc"), shells_rules(SH_A), lambda S: S == frozenset("xyz"), 84) is None)
check("5.18 Figure 5.17 as drawn: x and y have the same single neighbor q", SH_A["x"] == ["q"] and SH_A["y"] == ["q"])
check("5.18 Figure 5.17: the book's first two turns are legal ((a,b,c) -> (p,q,b) -> (q,y,a), tokens blue, green, red)",
      ("p", "q", "b") in SHG[("a", "b", "c")] and ("q", "y", "a") in SHG[("p", "q", "b")])
# repair: hang x from p instead of q
SH_E2 = [e for e in SH_E if e != ("q", "x")] + [("p", "x")]
SH_A2 = {v: [] for v in SH_V}
for u, v in SH_E2:
    SH_A2[u].append(v)
    SH_A2[v].append(u)
SHG2 = shells_graph(SH_A2)
dsh = bfs_dist(SHG2, ("a", "b", "c"))
SH_TURNS = min(dsh[p] for p in itertools.permutations(("x", "y", "z")) if p in dsh)
SH_SOL = [("a", "b", "c"), ("p", "q", "b"), ("q", "y", "a"), ("r", "q", "p"), ("z", "y", "x")]
check("5.18 with x hung from p instead: solvable, minimum 4 turns", SH_TURNS == 4, SH_TURNS)
check("5.18 ... and the book's two turns extend to the 4-turn solution (q,y,a) -> (r,q,p) -> (z,y,x)",
      all(b in SHG2[a] for a, b in zip(SH_SOL, SH_SOL[1:])))
check("5.18 ... brute force agrees on 4 turns",
      first_goal_time(frozenset("abc"), shells_rules(SH_A2), lambda S: S == frozenset("xyz"), 84) == 4)
ok, cnt, yes = True, 0, 0
while cnt < 400:
    n = random.randint(3, 7)
    E = random_graph(n, random.choice([0.3, 0.5]))
    if not connected(n, E):
        continue
    A = adj_of(n, E)
    abc = tuple(random.sample(range(n), 3))
    xyz = tuple(random.sample(range(n), 3))
    page = shells_solvable(A, abc, xyz)
    brute = first_goal_time(frozenset(abc), shells_rules(A), lambda S: S == frozenset(xyz), math.comb(n, 3)) is not None
    ok &= page == brute
    edges = sum(map(len, shells_graph(A).values()))
    ok &= edges <= (2 * len(E)) ** 3
    yes += page
    cnt += 1
check("5.18 WFS on ordered triples == brute force over move sequences; at most (2E)^3 edges", ok,
      f"{cnt} random, {yes} solvable")

# ============================================================================ Exercise 5.19 — coins
print("== Exercise 5.19: moving coins together")


def double_cover(A):
    """Page: H = G x {0,1}: vertices (x, i); edges (x, i)(y, 1-i) for every edge xy."""
    return {(x, i): [(y, 1 - i) for y in A[x]] for x in A for i in (0, 1)}


def coins_meet(A, starts):
    """Page: BFS in H from each (u, 0); answer = min over (x, i) reached from all starts of the max distance."""
    H = double_cover(A)
    ds = [bfs_dist(H, (u, 0)) for u in starts]
    best = INF
    for x in A:
        for i in (0, 1):
            if all((x, i) in d for d in ds):
                best = min(best, max(d[(x, i)] for d in ds))
    return best


def coins_rules(A):
    def moves(c):
        return set(itertools.product(*[A[x] for x in c]))

    return moves


def coins_brute(A, starts):
    t = first_goal_time(tuple(starts), coins_rules(A), lambda c: len(set(c)) == 1, len(A) ** len(starts))
    return INF if t is None else t


ok2, ok3, ok4, ok42, oklemma, cnt = True, True, True, True, True, 0
while cnt < 500:
    n = random.randint(1, 7)
    E = random_graph(n, random.choice([0.3, 0.5, 0.7]))
    if not connected(n, E):
        continue
    A = adj_of(n, E)
    for k, flag in ((2, "2"), (3, "3"), (4, "4")):
        if k == 4 and n > 6:
            continue
        starts = [random.randrange(n) for _ in range(k)]
        res = coins_meet(A, starts) == coins_brute(A, starts)
        if k == 2:
            ok2 &= res
        elif k == 3:
            ok3 &= res
        else:
            ok4 &= res
    # lemma: a walk of length exactly t from u to x exists iff t >= d_u(x, t mod 2)  (n >= 2)
    if n >= 2:
        u = random.randrange(n)
        dH = bfs_dist(double_cover(A), (u, 0))
        reach = {u}
        for t in range(0, 2 * n + 2):
            for x in range(n):
                if (x in reach) != ((x, t % 2) in dH and t >= dH[(x, t % 2)]):
                    oklemma = False
            reach = {y for z in reach for y in A[z]}
    # (c): 42 coins — possible iff G is not bipartite or all coins start on the same side
    starts = [random.randrange(n) for _ in range(42)]
    bip = bipartite_brute(n, E) if n <= 7 else None
    if bip:
        m = next(m for m in range(1 << n) if all((m >> a & 1) != (m >> b & 1) for a, b in E))
        same = len({m >> u & 1 for u in starts}) == 1
        ok42 &= (coins_meet(A, starts) < INF) == same
        one_side = [u for u in range(n) if (m >> u & 1) == (m & 1)]
        ok42 &= coins_meet(A, [random.choice(one_side) for _ in range(42)]) < INF
    else:
        ok42 &= coins_meet(A, starts) < INF
    cnt += 1
check("5.19 lemma: walk of length exactly t from u to x <=> t >= shortest walk of t's parity (V >= 2)", oklemma)
check("5.19(a) two coins: parity formula == brute force over coin configurations", ok2, f"{cnt} random connected graphs")
check("5.19(b) three coins: parity formula == brute force", ok3)
check("5.19 four coins: parity formula == brute force (sanity check of the general rule)", ok4)
check("5.19(c) 42 coins: reachable from all (u_j, 0) <=> non-bipartite or all starts on one side", ok42)

print()
if FAIL:
    print("FAILED:", len(FAIL))
    for f in FAIL:
        print("  ", f)
    sys.exit(1)
print("ALL OK")
