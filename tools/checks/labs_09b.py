#!/usr/bin/env python3
"""Checks for content/3-homework-and-exams/lab-09b.md (Lab 9b, CS/ECE 374 A Fall 2026; no official solutions).

Problem 1 (consistent ranking): the page's graph (edges a->b, b->c per game) and its topological sort with three states
are compared with brute force over all n! rankings, on every input with 4 players and at most 2 games and on random
inputs; the returned ranking is checked against every game.

Problems 2-4 (Judy's tour): every algorithm is implemented exactly as the page states it (the dag H' and LLP for
Problem 2, the layered dag for Problem 3, the token dag G4 for Problem 4) and compared with an exhaustive search over
all tours, on every graph with at most 4 galaxies and every distance array with values in {1,2,3}, and on random
connected graphs with 5-9 galaxies and three kinds of distance arrays: small integers (ties), distinct reals, and BFS
hop distances.  Exhaustive search is finite: between paid teleports D strictly increases, so a tour has at most
(k+1)(n-1) + k + 1 teleports.  The page's example instance, its answers, tours and sweep trace are reproduced; vertex
and edge counts of the constructed graphs are checked against the page's bounds; Problem 4 is re-run with random
tie-breaks of the ranks on distance arrays with ties."""
import itertools
import random
import sys

sys.setrecursionlimit(100000)
random.seed(374)
FAIL = []
NEG = float("-inf")
TOP = "T"          # a finished token


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail != "" else ""))
    if not cond:
        FAIL.append(name)


# ============================================================================ Problem 1
print("== Problem 1: consistent overall ranking")


def ranking_graph(n, games):
    """Page: vertices = players 0..n-1; for each game (a, b, c) ranked 1st, 2nd, 3rd, edges a->b and b->c."""
    adj = [[] for _ in range(n)]
    for a, b, c in games:
        adj[a].append(b)
        adj[b].append(c)
    return adj


def topological_sort(n, adj):
    """TopologicalSort of Section 6.3: DFS with New/Active/Finished, clock counting down; None on a cycle."""
    status = ["New"] * n
    S = [None] * n
    clock = [n - 1]
    cyc = [False]

    def dfs(v):
        status[v] = "Active"
        for w in adj[v]:
            if status[w] == "New":
                dfs(w)
            elif status[w] == "Active":
                cyc[0] = True          # fail gracefully: G has a cycle
        status[v] = "Finished"
        S[clock[0]] = v
        clock[0] -= 1

    for v in range(n):
        if status[v] == "New":
            dfs(v)
    return None if cyc[0] else S


def consistent(order, games):
    pos = {v: i for i, v in enumerate(order)}
    return all(pos[a] < pos[b] < pos[c] for a, b, c in games)


def brute_ranking_exists(n, games):
    return any(consistent(p, games) for p in itertools.permutations(range(n)))


def rank_ok(n, games):
    adj = ranking_graph(n, games)
    S = topological_sort(n, adj)
    ex = brute_ranking_exists(n, games)
    if S is None:
        return not ex
    return ex and sorted(S) == list(range(n)) and consistent(S, games)


triples4 = list(itertools.permutations(range(4), 3))
cnt = bad = 0
for m in range(3):
    for games in itertools.product(triples4, repeat=m):
        cnt += 1
        if not rank_ok(4, list(games)):
            bad += 1
check("P1: every input with 4 players and at most 2 games: ranking iff one exists, and it is consistent",
      bad == 0, f"{cnt} inputs, {bad} failures")
cnt = bad = yes = 0
for trial in range(1500):
    n = random.randint(3, 7)
    m = random.randint(0, 7)
    games = [tuple(random.sample(range(n), 3)) for _ in range(m)]
    cnt += 1
    yes += brute_ranking_exists(n, games)
    if not rank_ok(n, games):
        bad += 1
check("P1: random inputs (3-7 players, 0-7 games) agree with brute force over all n! rankings",
      bad == 0, f"{cnt} inputs, {yes} with a ranking, {cnt - yes} without, {bad} failures")
ok = all(sum(len(a) for a in ranking_graph(n, g)) == 2 * len(g)
         for n, g in [(5, [(0, 1, 2), (2, 3, 4), (4, 0, 1)]), (3, [])])
check("P1: the graph has n vertices and exactly 2m edges", ok)
# page example: players A..F = 0..5
A, B, C, Dp, E, F = range(6)
ex_games = [(A, B, C), (B, Dp, E), (F, A, Dp)]
S = topological_sort(6, ranking_graph(6, ex_games))
names = "ABCDEF"
check("P1 example: games ABC, BDE, FAD give a ranking (DFS in alphabetical order)",
      S is not None and consistent(S, ex_games), "".join(names[v] for v in S))
check("P1 example: the page's ranking F A B D E C", "".join(names[v] for v in S) == "FABDEC")
ex2 = ex_games + [(E, F, C)]
check("P1 example: adding game E F C creates the cycle F A B D E F and no ranking exists",
      topological_sort(6, ranking_graph(6, ex2)) is None and not brute_ranking_exists(6, ex2))

# ============================================================================ Judy: common
print("== Problems 2-4: Judy's tour")


def make_adj(n, edges):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    return adj


def rand_connected(n, extra):
    edges = set()
    for v in range(1, n):
        edges.add((random.randrange(v), v))
    rest = [(u, v) for u in range(n) for v in range(u + 1, n) if (u, v) not in edges]
    random.shuffle(rest)
    edges |= set(rest[:extra])
    return sorted(edges)


def bfs_dist(n, adj, s):
    D = [None] * n
    D[s] = 0
    q = [s]
    for v in q:
        for w in adj[v]:
            if D[w] is None:
                D[w] = D[v] + 1
                q.append(w)
    return D


def all_tours(n, adj, s, D, k, home_mid=False):
    """Exhaustive: every tour s=w0,...,wt=s, t>=2: each step away (D up) except at most k paid steps (D down, landing
    on a galaxy other than s unless home_mid) and the final step into s from a neighbor of s.  Equal-D steps never."""
    out = []

    def rec(walk, j):
        v = walk[-1]
        if len(walk) >= 2 and s in adj[v]:
            out.append(walk + [s])
        for w in adj[v]:
            if D[w] > D[v]:
                rec(walk + [w], j)
            elif D[w] < D[v] and j < k and (w != s or home_mid):
                rec(walk + [w], j + 1)

    rec([s], 0)
    return out


def brute(n, adj, s, D, k, distinct, home_mid=False):
    """Best tour value; staying home (no tour) counts 1."""
    best = 1
    longest = 0
    for W in all_tours(n, adj, s, D, k, home_mid):
        longest = max(longest, len(W) - 1)
        best = max(best, len(set(W)) if distinct else len(W) - 1)
    assert longest <= (k + 1) * (n - 1) + k + 1
    return best


# ---------------------------------------------------------------------------- Problem 2
def judy2_graph(n, adj, s, D):
    """Page: H' has vertices 0..n-1 and h = n; u->v for every teleport-way uv with D[u] < D[v]; v->h for v in N(s)."""
    h = n
    out = [[] for _ in range(n + 1)]
    for u in range(n):
        for v in adj[u]:
            if D[u] < D[v]:
                out[u].append(v)
    for v in adj[s]:
        out[v].append(h)
    return out, h


def llp(out, src, tgt, ops=None):
    """LLP(v) = length of the longest path from v to tgt (unit lengths), -inf if none; memoized DFS (Section 6.4)."""
    memo = {}

    def L(v):
        if v == tgt:
            return 0
        if v not in memo:
            best = NEG
            for w in out[v]:
                if ops is not None:
                    ops[0] += 1
                best = max(best, 1 + L(w))
            memo[v] = best
        return memo[v]

    return L(src)


def judy2(n, adj, s, D, ops=None):
    out, h = judy2_graph(n, adj, s, D)
    return max(1, llp(out, s, h, ops))


# ---------------------------------------------------------------------------- Problem 3
def judy3_graph(n, adj, s, D, k=2, home_mid=False):
    """Page: vertices (v, j), 0 <= j <= k, and h.  Free (u,j)->(v,j) if D[u] < D[v]; paid (u,j)->(v,j+1) if D[u] > D[v],
    v != s, j < k; final (v,j)->h for v in N(s).  Variant home_mid: paid teleports may land on s."""
    out = {("h",): []}
    for v in range(n):
        for j in range(k + 1):
            out[(v, j)] = []
    for u in range(n):
        for v in adj[u]:
            for j in range(k + 1):
                if D[u] < D[v]:
                    out[(u, j)].append((v, j))
                elif D[u] > D[v] and j < k and (v != s or home_mid):
                    out[(u, j)].append((v, j + 1))
    for v in adj[s]:
        for j in range(k + 1):
            out[(v, j)].append(("h",))
    return out


def judy3(n, adj, s, D, k=2, home_mid=False, ops=None):
    out = judy3_graph(n, adj, s, D, k, home_mid)
    return max(1, llp(out, (s, 0), ("h",), ops))


# ---------------------------------------------------------------------------- Problem 4
def ranks(n, D, tie=None):
    """Rank = position in increasing D; ties broken by tie[v] (default: by index), i.e. arbitrarily."""
    order = sorted(range(n), key=lambda v: (D[v], v if tie is None else tie[v]))
    return {v: i + 1 for i, v in enumerate(order)}


def leader(p, rank):
    act = [i for i in range(len(p)) if p[i] != TOP]
    if not act:
        return None
    return min(act, key=lambda i: (rank[p[i]], i))


def g4_out(p, t, s, adj, H, rank):
    """Out-edges of tuple (p, t) in the page's dag, as (new p, weight).  r = len(t) = number of paid teleports."""
    r = len(t)
    i = leader(p, rank)
    u = p[i]
    edges = []
    if (i < r and u == t[i]) or (i == r and s in adj[u]):
        q = list(p)
        q[i] = TOP
        edges.append((tuple(q), 0))
    if not (i < r and u == t[i]):
        occupied = {p[j] for j in range(len(p)) if j != i and p[j] != TOP}
        for w in H[u]:
            q = list(p)
            q[i] = w
            edges.append((tuple(q), 0 if w in occupied else 1))
    return edges


def judy4_r(n, adj, s, D, r, home_mid=False, stats=None, tie=None):
    """Exactly r paid teleports: longest path from sigma to an all-finished tuple."""
    rank = ranks(n, D, tie)
    H = [[w for w in adj[v] if D[w] > D[v]] for v in range(n)]
    paid = [(x, y) for x in range(n) for y in adj[x] if D[y] < D[x] and (y != s or home_mid)]
    memo = {}

    def L(p, t):
        key = (p, t)
        if key in memo:
            return memo[key]
        if all(q == TOP for q in p):
            memo[key] = 0
            return 0
        best = NEG
        for q, wt in g4_out(p, t, s, adj, H, rank):
            if stats is not None:
                stats["edges"] += 1
            best = max(best, wt + L(q, t))
        memo[key] = best
        if stats is not None:
            stats["tuples"] += 1
        return best

    best = NEG
    for combo in itertools.product(paid, repeat=r):
        t = tuple(x for x, y in combo)
        p = (s,) + tuple(y for x, y in combo)
        if stats is not None:
            stats["start"] += 1
        best = max(best, len(set(p)) + L(p, t))
    return best


def judy4(n, adj, s, D, k=2, home_mid=False, stats=None, tie=None):
    return max([1] + [judy4_r(n, adj, s, D, r, home_mid, stats, tie) for r in range(k + 1)])


# ---------------------------------------------------------------------------- exhaustive comparisons
def compare_all(instances, label):
    bad = {}
    tally = {"n": 0}
    for (n, edges, s, D) in instances:
        adj = make_adj(n, edges)
        tally["n"] += 1
        r2 = judy2(n, adj, s, D)
        if r2 != brute(n, adj, s, D, 0, False) or r2 != brute(n, adj, s, D, 0, True):
            bad.setdefault("P2", (n, edges, s, D))
        for k in range(3):
            if judy3(n, adj, s, D, k) != brute(n, adj, s, D, k, False):
                bad.setdefault(f"P3 k={k}", (n, edges, s, D))
            if judy4(n, adj, s, D, k) != brute(n, adj, s, D, k, True):
                bad.setdefault(f"P4 k={k}", (n, edges, s, D))
        for k in (1, 2):
            if judy3(n, adj, s, D, k, True) != brute(n, adj, s, D, k, False, True):
                bad.setdefault(f"P3 variant k={k}", (n, edges, s, D))
            if judy4(n, adj, s, D, k, True) != brute(n, adj, s, D, k, True, True):
                bad.setdefault(f"P4 variant k={k}", (n, edges, s, D))
    check(f"{label}: Problems 2, 3 (k=0,1,2), 4 (k=0,1,2) and the land-at-home variants agree with exhaustive search",
          not bad, f"{tally['n']} instances" + (f"; first failures {bad}" if bad else ""))


# every graph on at most 4 galaxies (s = 0), every D in {1,2,3}^(n-1)
small = []
for n in range(1, 5):
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [pairs[i] for i in range(len(pairs)) if mask >> i & 1]
        for Dt in itertools.product([1, 2, 3], repeat=n - 1):
            small.append((n, edges, 0, [0] + list(Dt)))
compare_all(small, "all graphs with n <= 4 galaxies, all D in {1,2,3}")

rand_inst = []
for trial in range(900):
    n = random.randint(5, 9 if trial % 3 == 0 else 8)
    edges = rand_connected(n, random.randint(0, n + 2))
    s = random.randrange(n)
    kind = trial % 3
    if kind == 0:
        D = [random.randint(1, 5) for _ in range(n)]
    elif kind == 1:
        D = [random.random() * 10 + 0.01 for _ in range(n)]
    else:
        D = bfs_dist(n, make_adj(n, edges), s)
    D[s] = 0
    rand_inst.append((n, edges, s, D))
compare_all(rand_inst, "random connected graphs, n = 5..9, D with ties / distinct reals / BFS hops")

# how much the random tests exercise: answers that differ between problems
stat = {"P4 < n": 0, "P4: k2 > k1": 0, "P4: k1 > k0": 0, "P3 > P4": 0}
for (n, edges, s, D) in rand_inst[:300]:
    adj = make_adj(n, edges)
    a0, a1, a2 = (judy4(n, adj, s, D, k) for k in range(3))
    m2 = judy3(n, adj, s, D, 2)
    stat["P4 < n"] += a2 < n
    stat["P4: k2 > k1"] += a2 > a1
    stat["P4: k1 > k0"] += a1 > a0
    stat["P3 > P4"] += m2 > a2
check("tests are not degenerate: P4 often < n, paid teleports often help, multiplicity often exceeds distinct",
      all(v >= 30 for v in stat.values()), stat)

# ---------------------------------------------------------------------------- BFS distances degenerate
bad2 = bad3 = 0
seen6 = False
for (n, edges, s, D) in rand_inst:
    if any(isinstance(x, float) for x in D) or D != bfs_dist(n, make_adj(n, edges), s):
        continue
    adj = make_adj(n, edges)
    for u, v in edges:
        assert abs(D[u] - D[v]) <= 1
    if judy2(n, adj, s, D) != 2:
        bad2 += 1
    a3 = judy3(n, adj, s, D, 2)
    if a3 > 6:
        bad3 += 1
    seen6 |= a3 == 6
check("BFS hop distances: |D[u]-D[v]| <= 1 on every edge and the Problem 2 answer is always 2", bad2 == 0)
check("BFS hop distances: the Problem 3 answer is at most 6 (and 6 occurs)", bad3 == 0 and seen6)

# ---------------------------------------------------------------------------- sizes and operation counts
bad = 0
for (n, edges, s, D) in rand_inst:
    adj = make_adj(n, edges)
    m = len(edges)
    out2, h = judy2_graph(n, adj, s, D)
    E2 = sum(len(o) for o in out2)
    if not (len(out2) == n + 1 and E2 <= m + len(adj[s])):
        bad += 1
    for k in range(3):
        out3 = judy3_graph(n, adj, s, D, k)
        E3 = sum(len(o) for o in out3.values())
        if not (len(out3) == (k + 1) * n + 1 and E3 <= (2 * k + 1) * m + (k + 1) * len(adj[s])):
            bad += 1
    ops = [0]
    judy2(n, adj, s, D, ops)
    if ops[0] > E2:
        bad += 1
    ops = [0]
    judy3(n, adj, s, D, 2, False, ops)
    if ops[0] > 5 * m + 3 * len(adj[s]):
        bad += 1
check("P2/P3 sizes: H' has n+1 vertices and <= m + deg(s) edges; the layered dag (k+1)n+1 vertices and "
      "<= (2k+1)m + (k+1)deg(s) edges; LLP looks at each edge once", bad == 0)


def check_dag(out):
    color = {}

    def dfs(v):
        color[v] = 1
        for w in out[v]:
            c = color.get(w, 0)
            if c == 1:
                return False
            if c == 0 and not dfs(w):
                return False
        color[v] = 2
        return True

    return all(dfs(v) for v in out if v not in color)


okdag = all(check_dag(judy3_graph(n, make_adj(n, e), s, D, 2)) for (n, e, s, D) in rand_inst[:200])
check("P3: the layered graph is a dag (no edge into an active vertex in any DFS)", okdag)

bad = 0
growth = []
for n in range(5, 12):
    for rep in range(3):
        edges = rand_connected(n, n // 2)
        s = 0
        D = [0] + random.sample(range(1, 3 * n), n - 1)
        adj = make_adj(n, edges)
        m = len(edges)
        st = {"tuples": 0, "edges": 0, "start": 0}
        judy4_r(n, adj, s, D, 2, False, st)
        if st["tuples"] > (n + 1) ** 3 * n ** 2 or st["edges"] > (n + 1) ** 3 * n ** 2 + 3 * n ** 2 * (n + 1) ** 2 * m \
                or st["start"] > m ** 2:
            bad += 1
        if rep == 0:
            growth.append((n, m, st["tuples"], st["edges"]))
check("P4 sizes: reachable tuples <= (n+1)^3 n^2, edges <= that + 3 n^2 (n+1)^2 m, start edges <= m^2",
      bad == 0, "  ".join(f"n={a},m={b}: {c} tuples, {d} edges" for a, b, c, d in growth))

# ties in D are broken arbitrarily: every tie-break order gives the brute-force answer
bad = cnt = 0
for (n, edges, s, D) in rand_inst[:300]:
    if len(set(D)) == n:
        continue
    adj = make_adj(n, edges)
    true = brute(n, adj, s, D, 2, True)
    for rep in range(3):
        tie = list(range(n))
        random.shuffle(tie)
        cnt += 1
        bad += judy4(n, adj, s, D, 2, tie=tie) != true
check("P4: with ties in D, every random tie-break of the ranks gives the exhaustive answer", bad == 0 and cnt > 100,
      f"{cnt} runs, {bad} failures")

# climb edges summed over ALL tuples (not just reachable ones) <= 3 n^2 (n+1)^2 m, as on the page
bad = 0
for trial in range(12):
    n = random.randint(3, 6)
    edges = rand_connected(n, random.randint(0, n))
    adj = make_adj(n, edges)
    m = len(edges)
    s = 0
    D = [0] + [random.randint(1, 4) for _ in range(n - 1)]
    rank = ranks(n, D)
    H = [[w for w in adj[v] if D[w] > D[v]] for v in range(n)]
    climbs = 0
    for p in itertools.product(list(range(n)) + [TOP], repeat=3):
        if all(q == TOP for q in p):
            continue
        u = p[leader(p, rank)]
        climbs += len(H[u])          # upper bound: ignores the "unless u = t_i" rule
    climbs *= n * n                   # every choice of (t0, t1)
    bad += climbs > 3 * n ** 2 * (n + 1) ** 2 * m
check("P4 time: climb edges summed over all (n+1)^3 n^2 tuples are at most 3 n^2 (n+1)^2 m", bad == 0)

# ---------------------------------------------------------------------------- the page's example
print("== the page's example instance")
NAMES = "sabcdefgh"
idx = {c: i for i, c in enumerate(NAMES)}
EXD = [0, 1, 3, 4, 5, 6, 7, 8, 9]                     # D for s a b c d e f g h
EXE = [("s", "c"), ("s", "h"), ("c", "g"), ("c", "b"), ("g", "f"), ("g", "h"),
       ("f", "d"), ("d", "a"), ("h", "e"), ("h", "a")]
exn = 9
exedges = [(idx[a], idx[b]) for a, b in EXE]
exadj = make_adj(exn, exedges)


def tour_ok(word, k, home_mid=False):
    W = [idx[c] for c in word]
    tours = {tuple(t) for t in all_tours(exn, exadj, 0, EXD, k, home_mid)}
    return tuple(W) in tours


ans = {"P2": judy2(exn, exadj, 0, EXD),
       "P3k1": judy3(exn, exadj, 0, EXD, 1), "P3k2": judy3(exn, exadj, 0, EXD, 2),
       "P4k1": judy4(exn, exadj, 0, EXD, 1), "P4k2": judy4(exn, exadj, 0, EXD, 2)}
check("example: answers P2 = 4, P3 = 9 (k=1) and 14 (k=2), P4 = 7 (k=1) and 8 (k=2)",
      ans == {"P2": 4, "P3k1": 9, "P3k2": 14, "P4k1": 7, "P4k2": 8}, ans)
check("example: brute force agrees", ans["P2"] == brute(exn, exadj, 0, EXD, 0, False)
      and ans["P3k2"] == brute(exn, exadj, 0, EXD, 2, False) and ans["P4k2"] == brute(exn, exadj, 0, EXD, 2, True)
      and ans["P3k1"] == brute(exn, exadj, 0, EXD, 1, False) and ans["P4k1"] == brute(exn, exadj, 0, EXD, 1, True))
check("example tours are valid: scghs (k=0), scghadfghs (k=1), scghadfghadfghs and scghehadfghs (k=2)",
      tour_ok("scghs", 0) and tour_ok("scghadfghs", 1) and tour_ok("scghadfghadfghs", 2)
      and tour_ok("scghehadfghs", 2))
check("example tour lengths: 4, 9 teleports / 7 galaxies, 14 teleports, 8 galaxies",
      [len("scghs") - 1, len("scghadfghs") - 1, len(set("scghadfghs")), len("scghadfghadfghs") - 1,
       len(set("scghehadfghs"))] == [4, 9, 7, 14, 8])
pockets = {idx["a"], idx["b"], idx["e"]}
best8 = [W for W in all_tours(exn, exadj, 0, EXD, 2) if len(set(W)) == 8]
check("example: every tour with <= 2 paid teleports visits at most two of a, b, e; the best tours miss exactly one "
      "galaxy, and it is one of a, b, e",
      all(len(pockets & set(W)) <= 2 for W in all_tours(exn, exadj, 0, EXD, 2))
      and all(len(set(range(exn)) - set(W)) == 1 and (set(range(exn)) - set(W)) <= pockets for W in best8),
      "best tours: " + " ".join(sorted({"".join(NAMES[v] for v in W) for W in best8})))
check("example: galaxies a, b, e can only be entered by a paid teleport (all their neighbors are farther)",
      all(all(EXD[w] > EXD[idx[c]] for w in exadj[idx[c]]) for c in "abe"))
Hex = [[w for w in exadj[v] if EXD[w] > EXD[v]] for v in range(exn)]
check("example: the away dag has the 10 edges s->c s->h c->g b->c g->h f->g d->f e->h a->d a->h",
      sorted(NAMES[u] + NAMES[w] for u in range(exn) for w in Hex[u]) ==
      sorted(["sc", "sh", "cg", "bc", "gh", "fg", "df", "eh", "ad", "ah"]))

reach = {0}
stack = [0]
while stack:
    u = stack.pop()
    for w in Hex[u]:
        if w not in reach:
            reach.add(w)
            stack.append(w)
check("example: in the away dag, s reaches exactly s, c, g, h (a, b, d, e, f are unreachable)",
      sorted(NAMES[v] for v in reach) == ["c", "g", "h", "s"])


def sweep_trace(chains, targets, rank):
    """Run the page's sweep on given chains (lists of galaxies); returns rows (leader, from, to, weight) and total."""
    pos = [0] * len(chains)
    p = [c[0] for c in chains]
    total = len(set(p))
    rows = []
    r = len(targets)
    while any(q != TOP for q in p):
        i = leader(p, rank)
        u = p[i]
        if pos[i] == len(chains[i]) - 1:
            assert (i < r and u == targets[i]) or (i == r and 0 in exadj[u])
            rows.append((i, NAMES[u], "finish", 0))
            p[i] = TOP
            continue
        w = chains[i][pos[i] + 1]
        assert w in Hex[u]
        wt = 0 if any(p[j] == w for j in range(len(p)) if j != i) else 1
        rows.append((i, NAMES[u], NAMES[w], wt))
        pos[i] += 1
        p[i] = w
        total += wt
    return rows, total


rk = ranks(exn, EXD)
chains = [[idx[c] for c in "scgh"], [idx[c] for c in "eh"], [idx[c] for c in "adfgh"]]
rows, total = sweep_trace(chains, [idx["h"], idx["h"]], rk)
expect = [(0, "s", "c", 1), (2, "a", "d", 1), (0, "c", "g", 1), (2, "d", "f", 1), (1, "e", "h", 1),
          (2, "f", "g", 0), (0, "g", "h", 0), (2, "g", "h", 0), (0, "h", "finish", 0), (1, "h", "finish", 0),
          (2, "h", "finish", 0)]
check("example sweep trace for chains scgh / eh / adfgh matches the page's table, total 3 + 5 = 8",
      rows == expect and total == 8, rows)
# the trace is a path in G4: every step is an edge of g4_out with the same weight
p = (0, idx["e"], idx["a"])
t = (idx["h"], idx["h"])
okpath = True
for (i, frm, to, wt) in rows:
    nxt = list(p)
    nxt[i] = TOP if to == "finish" else idx[to]
    if (tuple(nxt), wt) not in g4_out(p, t, 0, exadj, Hex, rk):
        okpath = False
    p = tuple(nxt)
check("example: every row of the trace is an edge of the token dag with that weight", okpath)

# ---------------------------------------------------------------------------- traps on the page
print("== traps")


def judy4_anyorder(n, adj, s, D, k):
    """Wrong variant: move the token on the HIGHEST galaxy (not the lowest); same collision test."""
    rank = ranks(n, D)
    rank_rev = {v: n + 1 - rank[v] for v in rank}
    H = [[w for w in adj[v] if D[w] > D[v]] for v in range(n)]
    paid = [(x, y) for x in range(n) for y in adj[x] if D[y] < D[x] and y != s]
    best = 1
    for r in range(k + 1):
        memo = {}

        def L(p, t):
            if all(q == TOP for q in p):
                return 0
            if (p, t) not in memo:
                memo[(p, t)] = max([NEG] + [wt + L(q, t) for q, wt in g4_out(p, t, s, adj, H, rank_rev)])
            return memo[(p, t)]

        for combo in itertools.product(paid, repeat=r):
            t = tuple(x for x, y in combo)
            p = (s,) + tuple(y for x, y in combo)
            best = max(best, len(set(p)) + L(p, t))
    return best


wrong_order = wrong_layer = 0
for (n, edges, s, D) in rand_inst[:300]:
    adj = make_adj(n, edges)
    true = brute(n, adj, s, D, 2, True)
    wrong_order += judy4_anyorder(n, adj, s, D, 2) != true
    wrong_layer += min(n, judy3(n, adj, s, D, 2)) != true
check("trap: moving the highest token instead of the lowest gives wrong answers on most instances", wrong_order > 150,
      f"{wrong_order} of 300 instances")
check("trap: Problem 3's answer capped at n is not Problem 4's answer", wrong_layer > 0,
      f"{wrong_layer} of 300 instances")
check("example: Problem 3's dag counts h twice in its best tour (14 > 9 galaxies)", ans["P3k2"] == 14 > exn)


def sweep_memory(W, D, rank):
    """Max over sweep positions r of (#chains in progress: start <= r < end) + (#paid teleports x->y pending:
    rank(y) <= r < rank(x)) for the tour W."""
    chains, links, cur = [], [], [W[0]]
    for u, v in zip(W[:-2], W[1:-1]):
        if D[v] > D[u]:
            cur.append(v)
        else:
            chains.append(cur)
            links.append((u, v))
            cur = [v]
    chains.append(cur)
    n = len(rank)
    return max(sum(rank[c[0]] <= r < rank[c[-1]] for c in chains) + sum(rank[y] <= r < rank[x] for x, y in links)
               for r in range(1, n + 1))


five = total = 0
for (n, edges, s, D) in rand_inst[:300]:
    adj = make_adj(n, edges)
    T = all_tours(n, adj, s, D, 2)
    if not T:
        continue
    total += 1
    opt = max(len(set(W)) for W in T)
    rk_ = ranks(n, D)
    five += min(sweep_memory(W, D, rk_) for W in T if len(set(W)) == opt) == 5
check("what we do not know: in about one instance in seven, every best tour has a moment with 3 chains in progress "
      "and both paid teleports pending (5 galaxies to remember)", 0.1 <= five / total <= 0.2,
      f"{five} of {total} instances")

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: {FAIL}")
