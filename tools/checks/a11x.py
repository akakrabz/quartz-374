#!/usr/bin/env python3
"""Checks for content/2-algorithms/11-applications-of-flows-and-cuts-exercises.md (solved exercises 11.1-11.10,
without 11.5(b,c), of Erickson's Algorithms).

One maximum-flow routine (augmenting paths on a skew-symmetric net flow, so antiparallel edges and infinite
capacities are allowed) serves every reduction on the page; it is itself checked against brute-force minimum cuts.
Every network is built exactly as the page defines it, and its verdict is compared with an exhaustive search that
knows nothing about flows (simple paths, vertex subsets, permutations, tilings, set partitions) on many random small
instances. The book's examples (the Sodor graph, Figures 11.10, 11.12 and 11.13) are re-entered from the figures."""
import itertools
import random
import sys
from collections import deque
from fractions import Fraction

random.seed(11374)
sys.setrecursionlimit(100000)
FAIL = []
INF = float("inf")


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail != "" else ""))
    if not cond:
        FAIL.append(name)


def section(s):
    print("== " + s)


# ============================================================================ maximum flow
# A network is a dict cap[(u, v)] = capacity (>= 0, possibly INF); both (u, v) and (v, u) may be present.
# Flows are stored as skew-symmetric net flows F[(u, v)] = -F[(v, u)].

def neighbors(cap):
    N = {}
    for (u, v) in cap:
        N.setdefault(u, set()).add(v)
        N.setdefault(v, set()).add(u)
    return N


def residual(cap, F, u, v):
    return cap.get((u, v), 0) - F.get((u, v), 0)


def find_path(cap, F, N, s, t, method):
    """An s-t path in the residual graph, as a parent map, or None."""
    parent = {s: None}
    if method == "bfs":
        Q = deque([s])
        while Q:
            u = Q.popleft()
            for v in sorted(N.get(u, ()), key=repr):
                if v not in parent and residual(cap, F, u, v) > 0:
                    parent[v] = u
                    if v == t:
                        return parent
                    Q.append(v)
        return None
    # "dfs" or "random": depth-first, neighbors in sorted or random order
    stack = [s]
    while stack:
        u = stack.pop()
        nb = list(N.get(u, ()))
        if method == "random":
            random.shuffle(nb)
        else:
            nb.sort(key=repr, reverse=True)
        for v in nb:
            if v not in parent and residual(cap, F, u, v) > 0:
                parent[v] = u
                if v == t:
                    return parent
                stack.append(v)
    return None


def maxflow(cap, s, t, method="bfs"):
    """Ford-Fulkerson with the given path rule. Returns (value, F, S) with S = vertices reachable from s in the
    final residual graph (a minimum cut)."""
    F = {}
    N = neighbors(cap)
    value = 0
    if s == t:
        raise ValueError("s == t")
    while True:
        par = find_path(cap, F, N, s, t, method)
        if par is None:
            break
        path = []
        v = t
        while par[v] is not None:
            path.append((par[v], v))
            v = par[v]
        b = min(residual(cap, F, u, v) for u, v in path)
        if b == INF:
            return INF, F, None
        for u, v in path:
            F[(u, v)] = F.get((u, v), 0) + b
            F[(v, u)] = F.get((v, u), 0) - b
        value += b
    S = reach_residual(cap, F, N, [s])
    return value, F, S


def reach_residual(cap, F, N, sources):
    seen = set(sources)
    Q = deque(sources)
    while Q:
        u = Q.popleft()
        for v in N.get(u, ()):
            if v not in seen and residual(cap, F, u, v) > 0:
                seen.add(v)
                Q.append(v)
    return seen


def cut_capacity(cap, S):
    return sum(c for (u, v), c in cap.items() if u in S and v not in S)


def flow_on(F, u, v):
    """Flow on the directed edge u->v (positive part of the net flow)."""
    return max(F.get((u, v), 0), 0)


def decompose_paths(cap, F, s, t):
    """Peel s-t paths off an integral net flow (each path one unit); returns the list of vertex sequences."""
    G = {}
    for (u, v), x in F.items():
        if x > 0:
            G[(u, v)] = x
    paths = []
    while True:
        # walk from s along positive edges, cancelling cycles when found
        path = [s]
        pos = {s: 0}
        u = s
        while u != t:
            nxt = None
            for (a, b), x in G.items():
                if a == u and x > 0:
                    nxt = b
                    break
            if nxt is None:
                return paths
            if nxt in pos:   # cycle: cancel one unit around it and restart
                cyc = path[pos[nxt]:] + [nxt]
                for a, b in zip(cyc, cyc[1:]):
                    G[(a, b)] -= 1
                break
            pos[nxt] = len(path)
            path.append(nxt)
            u = nxt
        else:
            for a, b in zip(path, path[1:]):
                G[(a, b)] -= 1
            paths.append(path)


# ---- self-test of maxflow against brute-force minimum cuts
section("maximum flow routine")
bad = 0
for trial in range(400):
    n = random.randint(2, 7)
    cap = {}
    for u in range(n):
        for v in range(n):
            if u != v and random.random() < 0.4:
                cap[(u, v)] = random.choice([random.randint(0, 6), Fraction(random.randint(1, 12), random.randint(1, 4))])
    s, t = 0, n - 1
    best = min(cut_capacity(cap, {s} | set(X)) for r in range(n - 1)
               for X in itertools.combinations(range(1, n - 1), r))
    for method in ("bfs", "dfs", "random"):
        val, F, S = maxflow(cap, s, t, method)
        ok = val == best and cut_capacity(cap, S) == val and t not in S
        ok &= all(F.get((u, v), 0) <= cap.get((u, v), 0) for u in range(n) for v in range(n))
        ok &= all(sum(F.get((x, y), 0) for y in range(n)) == 0 for x in range(1, n - 1))
        bad += not ok
check("Ford-Fulkerson (BFS, DFS, random paths) == brute-force minimum cut, feasible, conserving", bad == 0,
      "400 random networks x 3 path rules, integer and rational capacities")


# ============================================================================ Exercise 11.1
section("Exercise 11.1: balanced digraphs")


def rand_balanced(n, walks):
    """Random multigraph with indeg = outdeg everywhere: a union of random closed walks."""
    E = []
    for _ in range(walks):
        L = random.randint(2, n + 2)
        w = [random.randrange(n) for _ in range(L)]
        cyc = w + [w[0]]
        for a, b in zip(cyc, cyc[1:]):
            if a != b:
                E.append((a, b))
    return E


def mult_cap(E):
    cap = {}
    for a, b in E:
        cap[(a, b)] = cap.get((a, b), 0) + 1
    return cap


bad_sym = bad_bal = bad_cut = 0
count = 0
for trial in range(700):
    n = random.randint(2, 7)
    E = rand_balanced(n, random.randint(1, 5))
    indeg = [0] * n
    outdeg = [0] * n
    for a, b in E:
        outdeg[a] += 1
        indeg[b] += 1
    assert indeg == outdeg
    cap = mult_cap(E)
    for X in itertools.chain.from_iterable(itertools.combinations(range(n), r) for r in range(n + 1)):
        S = set(X)
        out = sum(1 for a, b in E if a in S and b not in S)
        inn = sum(1 for a, b in E if a not in S and b in S)
        bad_bal += out != inn
    for u, v in itertools.permutations(range(n), 2):
        k1 = maxflow(cap, u, v)[0]
        k2 = maxflow(cap, v, u)[0]
        bf = min(cut_capacity(cap, {u} | set(X)) for r in range(n - 1)
                 for X in itertools.combinations([x for x in range(n) if x not in (u, v)], r))
        bad_cut += k1 != bf
        bad_sym += k1 != k2
        count += 1
check("11.1 balanced digraph: edges leaving S == edges entering S, for every vertex set S", bad_bal == 0,
      "700 random balanced multigraphs, all subsets")
check("11.1 max # edge-disjoint u->v paths (unit-capacity max flow) == min # edges leaving a set with u, not v",
      bad_cut == 0, f"{count} ordered pairs")
check("11.1 answer YES: k edge-disjoint u->v paths  =>  k edge-disjoint v->u paths (flow values equal)",
      bad_sym == 0, f"{count} ordered pairs")
cap = {("u", "v"): 1}
check("11.1 trap: without balance it fails (single edge u->v: 1 path u->v, 0 paths v->u)",
      maxflow(cap, "u", "v")[0] == 1 and maxflow(cap, "v", "u")[0] == 0)


# ============================================================================ Exercise 11.2
section("Exercise 11.2: a path from u to w through v")


def rand_ugraph(n, p):
    return [(a, b) for a in range(n) for b in range(a + 1, n) if random.random() < p]


def through_network(n, E, u, v, w):
    """The page's network: split x != v into (x,'in') -> (x,'out') of capacity 1; source (v,'out');
    edges x_out -> y_in and y_out -> x_in of capacity 1 for every edge xy with y != v (resp. x != v);
    u_out -> T and w_out -> T of capacity 1."""
    cap = {}
    for x in range(n):
        if x != v:
            cap[((x, "in"), (x, "out"))] = 1
    for a, b in E:
        if b != v:
            cap[((a, "out"), (b, "in"))] = 1
        if a != v:
            cap[((b, "out"), (a, "in"))] = 1
    cap[((u, "out"), "T")] = 1
    cap[((w, "out"), "T")] = 1
    return cap


def simple_paths(adj, a, b):
    out = []

    def go(x, path, seen):
        if x == b:
            out.append(list(path))
            return
        for y in adj[x]:
            if y not in seen:
                seen.add(y)
                path.append(y)
                go(y, path, seen)
                path.pop()
                seen.discard(y)
    go(a, [a], {a})
    return out


bad = bad_le2 = bad_extract = 0
count = yes = 0
for trial in range(500):
    n = random.randint(3, 8)
    E = rand_ugraph(n, random.choice([0.25, 0.4, 0.6]))
    adj = [[] for _ in range(n)]
    for a, b in E:
        adj[a].append(b)
        adj[b].append(a)
    for u, v, w in itertools.permutations(range(n), 3):
        if u > w:
            continue
        truth = any(v in P for P in simple_paths(adj, u, w))
        cap = through_network(n, E, u, v, w)
        val, F, _ = maxflow(cap, (v, "out"), "T")
        bad_le2 += val > 2
        bad += (val == 2) != truth
        if val == 2:
            yes += 1
            P = decompose_paths(cap, F, (v, "out"), "T")
            # P[i] = [(v,out), (x,in), (x,out), ..., (end,out), T]
            seqs = [[v] + [z[0] for z in p[1:-1] if z[1] == "out"] for p in P]
            ends = sorted(sq[-1] for sq in seqs)
            a_ = next(sq for sq in seqs if sq[-1] == u)
            b_ = next(sq for sq in seqs if sq[-1] == w)
            walk = list(reversed(a_)) + b_[1:]
            okp = len(P) == 2 and ends == sorted([u, w]) and len(set(walk)) == len(walk)
            okp &= all(walk[i + 1] in adj[walk[i]] for i in range(len(walk) - 1)) and v in walk
            okp &= walk[0] == u and walk[-1] == w
            bad_extract += not okp
        count += 1
check("11.2 max flow from v_out to T is at most 2", bad_le2 == 0, f"{count} (graph, u, v, w) instances")
check("11.2 max flow == 2  <=>  some simple u-w path passes through v (all simple paths enumerated)", bad == 0,
      f"{count} instances, {yes} positive")
check("11.2 the two flow paths, one reversed and joined at v, form a simple u-w path through v", bad_extract == 0)
# trap: u-x, x-v, u-y, y-v, x-w (vertices u=0, v=1, w=2, x=3, y=4)
Et = [(0, 3), (3, 1), (0, 4), (4, 1), (3, 2)]
adj = [[] for _ in range(5)]
for a, b in Et:
    adj[a].append(b)
    adj[b].append(a)
good = [P for P in simple_paths(adj, 0, 2) if 1 in P]
check("11.2 trap graph: the only u-w path through v is u y v x w", good == [[0, 4, 1, 3, 2]], str(good))
check("11.2 trap graph: after taking u x v first, v cannot reach w without x",
      not any(set(P) & {0, 3} == set() for P in [q[1:] for q in simple_paths(adj, 1, 2)]))
check("11.2 trap graph: the network has a flow of value 2", maxflow(through_network(5, Et, 0, 1, 2), (1, "out"), "T")[0] == 2)


# ============================================================================ Exercise 11.3
section("Exercise 11.3: multi-terminal flows")


def max_multi_flow(cap, n, srcs, tgts, method, order=None):
    """The book's MaxMultiFlow: f <- f + MaxFlow(G_f, s_i, t_j) for i outer, j inner. Returns F and a log of the
    reach sets after each iteration (for the invariant checks)."""
    F = {}
    pairs = order or [(i, j) for i in range(len(srcs)) for j in range(len(tgts))]
    log = []
    for (i, j) in pairs:
        rcap = {}
        for x in range(n):
            for y in range(n):
                r = residual(cap, F, x, y)
                if x != y and r > 0:
                    rcap[(x, y)] = r
        if srcs[i] in {a for a, _ in rcap} or True:
            val, Fp, _ = maxflow(rcap, srcs[i], tgts[j], method) if rcap else (0, {}, None)
        for (x, y), z in Fp.items():
            F[(x, y)] = F.get((x, y), 0) + z
        N = neighbors(cap)
        log.append((i, j, {k: reach_residual(cap, F, N, [srcs[k]]) for k in range(len(srcs))}))
    return F, log


def mt_value(F, n, srcs):
    return sum(F.get((s, y), 0) for s in srcs for y in range(n))


bad_val = bad_feas = bad_inv = bad_final = bad_super = 0
count = 0
for trial in range(500):
    n = random.randint(3, 8)
    cap = {}
    for x in range(n):
        for y in range(n):
            if x != y and random.random() < 0.35:
                cap[(x, y)] = random.choice([random.randint(1, 5), Fraction(random.randint(1, 9), random.randint(1, 3))])
    sig = random.randint(1, min(3, n - 1))
    tau = random.randint(1, min(3, n - sig))
    perm = random.sample(range(n), n)
    srcs, tgts = perm[:sig], perm[sig:sig + tau]
    others = [x for x in range(n) if x not in srcs and x not in tgts]
    # brute force: min over S containing all sources and no target of c(S, V-S)
    bf = min(cut_capacity(cap, set(srcs) | set(X)) for r in range(len(others) + 1)
             for X in itertools.combinations(others, r))
    for method in ("bfs", "dfs", "random"):
        F, log = max_multi_flow(cap, n, srcs, tgts, method)
        count += 1
        bad_val += mt_value(F, n, srcs) != bf
        bad_feas += not all(F.get((x, y), 0) <= cap.get((x, y), 0) for x in range(n) for y in range(n))
        bad_feas += not all(sum(F.get((x, y), 0) for y in range(n)) == 0 for x in others)
        # invariant of the proof: once source i is finished, its reach set contains no target and never grows
        for k, (i, j, R) in enumerate(log):
            if j == tau - 1:
                Ri = R[i]
                bad_inv += any(t in Ri for t in tgts)
                bad_inv += any(not log[l][2][i] <= Ri for l in range(k, len(log)))
        N = neighbors(cap)
        final = reach_residual(cap, F, N, list(srcs))
        bad_final += any(t in final for t in tgts)
    # part (b): one max flow with a super-source and super-target
    cap2 = dict(cap)
    for s in srcs:
        cap2[("S*", s)] = INF
    for t in tgts:
        cap2[(t, "T*")] = INF
    bad_super += maxflow(cap2, "S*", "T*")[0] != bf
check("11.3(a) MaxMultiFlow value == brute-force min over S (all sources, no target) of c(S, V-S)", bad_val == 0,
      f"{count} runs: 500 random networks x 3 MaxFlow implementations, integer and rational capacities")
check("11.3(a) MaxMultiFlow returns a feasible multi-terminal flow (capacities, conservation at non-terminals)",
      bad_feas == 0)
check("11.3(a) invariant: after (i, tau) no target is reachable from s_i, and that reach set never grows", bad_inv == 0)
check("11.3(a) at the end, no target is reachable from any source in G_f", bad_final == 0)
check("11.3(b) super-source/super-target max flow == the same brute-force value", bad_super == 0)


# ============================================================================ Exercise 11.4
section("Exercise 11.4: Sodor (minimum vertex cut)")


def sodor_network(n, E, s, t):
    """x_in -> x_out of capacity 1 for x not in {s, t}; for every edge xy: x_out -> y_in and y_out -> x_in, INF.
    Source s_out, target t_in; s and t are not split (their in/out are joined by INF)."""
    cap = {}
    for x in range(n):
        cap[((x, "in"), (x, "out"))] = INF if x in (s, t) else 1
    for a, b in E:
        cap[((a, "out"), (b, "in"))] = INF
        cap[((b, "out"), (a, "in"))] = INF
    return cap


def sodor(n, E, s, t):
    if any({a, b} == {s, t} for a, b in E):
        return INF, None
    cap = sodor_network(n, E, s, t)
    val, F, S = maxflow(cap, (s, "out"), (t, "in"))
    C = [x for x in range(n) if (x, "in") in S and (x, "out") not in S]
    return val, C


def blocks(n, E, s, t, C):
    adj = [[] for _ in range(n)]
    for a, b in E:
        adj[a].append(b)
        adj[b].append(a)
    seen = {s}
    Q = deque([s])
    while Q:
        x = Q.popleft()
        for y in adj[x]:
            if y not in seen and y not in C:
                seen.add(y)
                Q.append(y)
    return t not in seen


# the book's example, read off the figure: s; left column a,b,c; the two circled stations X (top), Y (bottom);
# p, q right of them; d, e on the right; t
names = ["s", "a", "b", "c", "X", "Y", "p", "q", "d", "e", "t"]
ix = {x: i for i, x in enumerate(names)}
book_edges = [("s", "a"), ("s", "b"), ("s", "c"), ("a", "X"), ("a", "Y"), ("b", "X"), ("b", "Y"), ("c", "X"),
              ("c", "Y"), ("X", "p"), ("X", "q"), ("X", "d"), ("Y", "q"), ("Y", "p"), ("Y", "e"), ("p", "t"),
              ("q", "t"), ("d", "t"), ("d", "e"), ("e", "t")]
Eb = [(ix[a], ix[b]) for a, b in book_edges]
val, C = sodor(len(names), Eb, ix["s"], ix["t"])
check("11.4 book's example: the algorithm returns 2", val == 2, f"closes {[names[c] for c in C]}")
check("11.4 book's example: the cut found is the two circled stations", sorted(names[c] for c in C) == ["X", "Y"])
bf = min(r for r in range(len(names)) for Cc in itertools.combinations(
    [i for i in range(len(names)) if names[i] not in ("s", "t")], r) if blocks(len(names), Eb, ix["s"], ix["t"], set(Cc)))
check("11.4 book's example: brute force over station subsets also gives 2", bf == 2)
cap = sodor_network(len(names), Eb, ix["s"], ix["t"])
_, F, _ = maxflow(cap, (ix["s"], "out"), (ix["t"], "in"))
P = decompose_paths(cap, F, (ix["s"], "out"), (ix["t"], "in"))
st = [[names[z[0]] for z in p if z[1] == "in"] for p in P]
inner = [set(q[:-1]) for q in st]
check("11.4 book's example: the max flow is two vertex-disjoint s-t paths", len(P) == 2 and not (inner[0] & inner[1]),
      str([["s"] + q for q in st]))

bad = bad_cut = 0
count = 0
for trial in range(1500):
    n = random.randint(3, 9)
    E = rand_ugraph(n, random.choice([0.25, 0.35, 0.5]))
    s, t = 0, n - 1
    if any({a, b} == {s, t} for a, b in E):
        continue
    val, C = sodor(n, E, s, t)
    best = min(r for r in range(n) for Cc in itertools.combinations(range(1, n - 1), r) if blocks(n, E, s, t, set(Cc)))
    bad += val != best
    bad_cut += not (len(C) == val and blocks(n, E, s, t, set(C)) and s not in C and t not in C)
    count += 1
check("11.4 max flow value == fewest stations whose closing disconnects s from t (all subsets tried)", bad == 0,
      f"{count} random graphs with s, t not adjacent")
check("11.4 the stations x with x_in reachable and x_out unreachable in the final residual graph form such a set",
      bad_cut == 0)
val, C = sodor(3, [(0, 2), (0, 1)], 0, 2)
check("11.4 s adjacent to t: no set of closures works (reported as impossible)", val == INF)
bad = 0
for trial in range(300):
    n = random.randint(3, 9)
    E = rand_ugraph(n, 0.5)
    if any({a, b} == {0, n - 1} for a, b in E):
        continue
    bad += sodor(n, E, 0, n - 1)[0] > n - 2
check("11.4 |f*| <= V - 2 (closing every other station is a cut)", bad == 0)
# trap (review): capacity-1 split edges for s and t matter only with terminals s_in / t_out
_rng = random.Random(44)
ok_out = ok_in = True
drops = 0
for trial in range(300):
    n = _rng.randint(3, 9)
    E = [(a, b) for a in range(n) for b in range(a + 1, n) if _rng.random() < 0.4]
    s, t = 0, n - 1
    if any({a, b} == {s, t} for a, b in E):
        continue
    ref = maxflow(sodor_network(n, E, s, t), (s, "out"), (t, "in"))[0]
    cap1 = sodor_network(n, E, s, t)
    cap1[((s, "in"), (s, "out"))] = cap1[((t, "in"), (t, "out"))] = 1
    ok_out &= maxflow(cap1, (s, "out"), (t, "in"))[0] == ref
    v1 = maxflow(cap1, (s, "in"), (t, "out"))[0]
    ok_in &= v1 == min(ref, 1) and maxflow(sodor_network(n, E, s, t), (s, "in"), (t, "out"))[0] == ref
    drops += v1 < ref
check("11.4 trap: capacity-1 split edges for s and t change nothing with source s_out, target t_in; with s_in, t_out "
      "they cap the flow at 1", ok_out and ok_in and drops > 0, f"{drops} graphs lose flow")


# ============================================================================ Exercise 11.5(a)
section("Exercise 11.5(a): the escape problem")


def escape_network(n, terms):
    cap = {}
    for i in range(1, n + 1):
        for j in range(1, n + 1):
            cap[((i, j, "in"), (i, j, "out"))] = 1
            for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                a, b = i + di, j + dj
                if 1 <= a <= n and 1 <= b <= n:
                    cap[((i, j, "out"), (a, b, "in"))] = 1
            if i in (1, n) or j in (1, n):
                cap[((i, j, "out"), "t")] = 1
    for (x, y) in terms:
        cap[("s", (x, y, "in"))] = 1
    return cap


def escape_flow(n, terms):
    cap = escape_network(n, terms)
    val, F, _ = maxflow(cap, "s", "t")
    return val, cap, F


def grid_nbrs(n, v):
    i, j = v
    for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        a, b = i + di, j + dj
        if 1 <= a <= n and 1 <= b <= n:
            yield (a, b)


def is_boundary(n, v):
    return v[0] in (1, n) or v[1] in (1, n)


def escape_brute(n, terms, truncate=True):
    """Exhaustive search for vertex-disjoint escape paths. With truncate, paths stop at the first boundary vertex
    (complete: truncating every path of a solution keeps a solution)."""
    terms = list(terms)
    used = set(terms)

    def route(k):
        if k == len(terms):
            return True
        start = terms[k]

        def extend(v, mine):
            if is_boundary(n, v):
                if route(k + 1):
                    return True
                if truncate:
                    return False
            for u in grid_nbrs(n, v):
                if u not in used:
                    used.add(u)
                    mine.append(u)
                    if extend(u, mine):
                        return True
                    mine.pop()
                    used.discard(u)
            return False
        return extend(start, [start])
    return route(0)


# Figure 11.10 (7 x 7), terminals read off the figure as (row, column) from the top left
fig_terms = [(2, 5), (3, 2), (3, 4), (4, 4), (4, 6), (5, 3), (5, 4), (6, 5)]
val, cap, F = escape_flow(7, fig_terms)
check("11.5 Figure 11.10: max flow == m == 8 (a positive instance)", val == 8 == len(fig_terms))
book_paths = [
    [(3, 2), (2, 2), (1, 2)],
    [(5, 3), (4, 3), (3, 3), (2, 3), (1, 3)],
    [(2, 5), (1, 5)],
    [(3, 4), (3, 5), (3, 6), (3, 7)],
    [(4, 4), (4, 5), (5, 5), (5, 6), (5, 7)],
    [(4, 6), (4, 7)],
    [(5, 4), (6, 4), (7, 4)],
    [(6, 5), (7, 5)],
]
allv = [v for p in book_paths for v in p]
ok = len(allv) == len(set(allv)) and sorted(p[0] for p in book_paths) == sorted(fig_terms)
ok &= all(p[i + 1] in set(grid_nbrs(7, p[i])) for p in book_paths for i in range(len(p) - 1))
ok &= all(is_boundary(7, p[-1]) for p in book_paths)
check("11.5 Figure 11.10: the book's eight drawn paths are vertex-disjoint grid paths to the boundary", ok)
P = decompose_paths(cap, F, "s", "t")
seqs = [[(z[0], z[1]) for z in p[1:-1] if z[2] == "out"] for p in P]
allv = [v for q in seqs for v in q]
check("11.5 Figure 11.10: the flow decomposes into 8 vertex-disjoint terminal-to-boundary paths",
      len(seqs) == 8 and len(allv) == len(set(allv)) and sorted(q[0] for q in seqs) == sorted(fig_terms)
      and all(is_boundary(7, q[-1]) for q in seqs))
# a negative instance: a terminal whose four neighbors are terminals
plus = [(3, 3), (2, 3), (4, 3), (3, 2), (3, 4)]
check("11.5 a plus of five terminals in a 5 x 5 grid cannot escape (flow 4 < 5)",
      escape_flow(5, plus)[0] == 4 and not escape_brute(5, plus))
capp = escape_network(5, plus)
Scut = {"s", (3, 3, "in"), (3, 3, "out")} | {(i, j, "in") for (i, j) in plus}
check("11.5 trap: s + the middle terminal + the in-copies of the outer four is a cut of capacity 4 (their split edges)",
      cut_capacity(capp, Scut) == 4 and sorted(u for (u, v) in capp if u in Scut and v not in Scut)
      == sorted((i, j, "in") for (i, j) in plus if (i, j) != (3, 3)))
bad = 0
for n in range(3, 8):
    for ci in range(2, n):
        for cj in range(2, n):
            pl = [(ci, cj), (ci - 1, cj), (ci + 1, cj), (ci, cj - 1), (ci, cj + 1)]
            bad += escape_flow(n, pl)[0] >= 5
check("11.5 trap: a plus never escapes, every position in grids n = 3..7", bad == 0)

bad = bad_tr = 0
count = pos = 0
for trial in range(1200):
    n = random.randint(1, 6)
    if trial % 2 or n < 3:
        m = random.randint(1, min(n * n, 3 * n))
        terms = random.sample([(i, j) for i in range(1, n + 1) for j in range(1, n + 1)], m)
    else:   # crowd the terminals into a random 3 x 3 block to get negative instances
        a, b = random.randint(1, n - 2), random.randint(1, n - 2)
        block = [(i, j) for i in range(a, a + 3) for j in range(b, b + 3)]
        m = random.randint(5, 9)
        terms = random.sample(block, m)
    val = escape_flow(n, terms)[0]
    truth = escape_brute(n, terms)
    bad += (val == m) != truth
    pos += truth
    if n <= 4:
        bad_tr += escape_brute(n, terms, truncate=False) != truth
    count += 1
check("11.5(a) max flow == m  <=>  vertex-disjoint escape paths exist (exhaustive search)", bad == 0,
      f"{count} random instances, n <= 6, {pos} positive")
check("11.5 brute force: stopping paths at the first boundary vertex loses nothing (n <= 4)", bad_tr == 0)
check("11.5(a) |f*| <= 4n - 4 boundary vertices for n >= 2",
      all(escape_flow(n, [(i, j) for i in range(1, n + 1) for j in range(1, n + 1)])[0] == 4 * n - 4
          for n in range(2, 7)))


# ============================================================================ bipartite matching helper
def matching_network(L, R, E):
    cap = {}
    for x in L:
        cap[("s", ("L", x))] = 1
    for y in R:
        cap[(("R", y), "t")] = 1
    for x, y in E:
        cap[(("L", x), ("R", y))] = 1
    return cap


def max_matching(L, R, E):
    cap = matching_network(L, R, E)
    val, F, _ = maxflow(cap, "s", "t")
    M = [(x, y) for x, y in E if F.get((("L", x), ("R", y)), 0) == 1]
    return val, M


# ============================================================================ Exercise 11.6
section("Exercise 11.6: mini-golf (perfect bipartite matching)")
bad = bad_m = 0
for trial in range(1500):
    n = random.randint(1, 7)
    p = random.choice([0.2, 0.35, 0.5, 0.7])
    E = [(i, j) for i in range(n) for j in range(n) if random.random() < p]
    Es = set(E)
    truth = any(all((i, pi[i]) in Es for i in range(n)) for pi in itertools.permutations(range(n)))
    val, M = max_matching(range(n), range(n), E)
    bad += (val == n) != truth
    bad_m += not (len(M) == val and len({x for x, _ in M}) == val and len({y for _, y in M}) == val)
check("11.6 max flow == n  <=>  some permutation pairs every start with a visible hole", bad == 0,
      "1500 random bipartite graphs, n <= 7")
check("11.6 the edges carrying flow form a matching of size |f*|", bad_m == 0)


# full pipeline on a small orthogonal course: segment-intersection predicate + matching vs permutations
def seg_inter(p, q, a, b):
    """Closed segments pq and ab intersect (touching counts)."""
    def orient(u, v, w):
        d = (v[0] - u[0]) * (w[1] - u[1]) - (v[1] - u[1]) * (w[0] - u[0])
        return (d > 0) - (d < 0)

    def onseg(u, v, w):
        return min(u[0], v[0]) <= w[0] <= max(u[0], v[0]) and min(u[1], v[1]) <= w[1] <= max(u[1], v[1])
    o1, o2, o3, o4 = orient(p, q, a), orient(p, q, b), orient(a, b, p), orient(a, b, q)
    if o1 != o2 and o3 != o4:
        return True
    return ((o1 == 0 and onseg(p, q, a)) or (o2 == 0 and onseg(p, q, b)) or (o3 == 0 and onseg(a, b, p))
            or (o4 == 0 and onseg(a, b, q)))


# a U-shaped field: corners in order
U = [(0, 0), (12, 0), (12, 10), (8, 10), (8, 4), (4, 4), (4, 10), (0, 10)]
walls = list(zip(U, U[1:] + U[:1]))


def inside(pt):
    x, y = pt
    return (0 < x < 12 and 0 < y < 4) or (0 < x < 4 and 0 < y < 10) or (8 < x < 12 and 0 < y < 10)


cells = [(x + 0.5, y + 0.5) for x in range(12) for y in range(10) if inside((x + 0.5, y + 0.5))]
bad = 0
pos = 0
for trial in range(300):
    n = random.randint(1, 5)
    pts = random.sample(cells, 2 * n)
    S, H = pts[:n], pts[n:]
    E = [(i, j) for i in range(n) for j in range(n) if not any(seg_inter(S[i], H[j], a, b) for a, b in walls)]
    Es = set(E)
    truth = any(all((i, pi[i]) in Es for i in range(n)) for pi in itertools.permutations(range(n)))
    pos += truth
    bad += (max_matching(range(n), range(n), E)[0] == n) != truth
check("11.6 pipeline on a U-shaped course: visibility edges + max flow == brute force over correspondences",
      bad == 0, f"300 random point sets, {pos} positive")


# ============================================================================ Exercise 11.7
section("Exercise 11.7: cycle covers")
bad = bad_cyc = 0
count = pos = 0
for trial in range(2000):
    n = random.randint(1, 7)
    loops = random.random() < 0.3
    E = [(u, v) for u in range(n) for v in range(n) if (u != v or loops) and random.random() < random.choice([0.2, 0.35, 0.5])]
    Es = set(E)
    truth = any(all((u, pi[u]) in Es for u in range(n)) for pi in itertools.permutations(range(n)))
    val, M = max_matching(range(n), range(n), E)
    bad += (val == n) != truth
    pos += truth
    if val == n:
        succ = dict(M)
        seen = set()
        cycles = []
        for u in range(n):
            if u not in seen:
                c = [u]
                seen.add(u)
                x = succ[u]
                while x != u:
                    c.append(x)
                    seen.add(x)
                    x = succ[x]
                cycles.append(c)
        ok = sorted(v for c in cycles for v in c) == list(range(n))
        ok &= all((c[k], c[(k + 1) % len(c)]) in Es for c in cycles for k in range(len(c)))
        bad_cyc += not ok
    count += 1
check("11.7 perfect matching (max flow == V) in the out-copy/in-copy graph  <=>  cycle cover (all permutations)",
      bad == 0, f"{count} random digraphs (some with loops), {pos} with a cycle cover")
check("11.7 following matched successors splits the vertices into directed cycles of G", bad_cyc == 0)


# ============================================================================ Exercise 11.8
section("Exercise 11.8: domino tilings")


def domino_flow(D):
    n = len(D)
    sq = [(i, j) for i in range(n) for j in range(n) if not D[i][j]]
    blacks = [(i, j) for (i, j) in sq if (i + j) % 2 == 0]
    whites = [(i, j) for (i, j) in sq if (i + j) % 2 == 1]
    E = [(b, w) for b in blacks for w in grid_nbrs_0(n, b) if not D[w[0]][w[1]]]
    val, M = max_matching(blacks, whites, E)
    return val == len(blacks) == len(whites), val, M, len(blacks), len(whites)


def grid_nbrs_0(n, v):
    i, j = v
    for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        a, b = i + di, j + dj
        if 0 <= a < n and 0 <= b < n:
            yield (a, b)


def tile_brute(D):
    n = len(D)
    free = {(i, j) for i in range(n) for j in range(n) if not D[i][j]}

    def go():
        if not free:
            return True
        v = min(free)          # first free square in row-major order
        for w in ((v[0], v[1] + 1), (v[0] + 1, v[1])):
            if w in free:
                free.discard(v)
                free.discard(w)
                if go():
                    free.add(v)
                    free.add(w)
                    return True
                free.add(v)
                free.add(w)
        return False
    return go()


# Figure 11.12: undeleted columns in each row (1-indexed), read off the figure
fig12 = {1: [1, 2, 3, 7, 8, 9], 2: [1, 2, 3, 4, 5, 7, 8, 9], 3: [2, 4, 6, 7, 8, 9], 4: [2, 4, 6, 7, 8, 9],
         5: [4, 6, 9], 6: [1, 2, 4, 5, 6, 7, 8], 7: [1, 2, 4, 5, 6, 7], 8: [1, 2, 3, 4, 5, 6, 7, 8],
         9: [1, 2, 3, 4, 5, 6]}
D12 = [[(j + 1) not in fig12[i + 1] for j in range(9)] for i in range(9)]
ok, val, M, nb, nw = domino_flow(D12)
check("11.8 Figure 11.12: 56 squares, 28 of each color, max flow 28 -> True",
      ok and val == 28 and nb == nw == 28 and sum(map(len, fig12.values())) == 56)
check("11.8 Figure 11.12: exhaustive tiling search agrees", tile_brute(D12))
# the book's drawn tiling, as pairs of (row, col)
book_tiles = [((1, 1), (2, 1)), ((1, 2), (2, 2)), ((1, 3), (2, 3)), ((2, 4), (2, 5)), ((1, 7), (2, 7)),
              ((1, 8), (1, 9)), ((2, 8), (3, 8)), ((2, 9), (3, 9)), ((3, 2), (4, 2)), ((3, 4), (4, 4)),
              ((3, 6), (3, 7)), ((4, 6), (5, 6)), ((4, 7), (4, 8)), ((4, 9), (5, 9)), ((5, 4), (6, 4)),
              ((6, 1), (6, 2)), ((6, 5), (6, 6)), ((6, 7), (6, 8)), ((7, 1), (7, 2)), ((7, 4), (8, 4)),
              ((7, 5), (8, 5)), ((7, 6), (7, 7)), ((8, 1), (9, 1)), ((8, 2), (8, 3)), ((8, 6), (9, 6)),
              ((8, 7), (8, 8)), ((9, 2), (9, 3)), ((9, 4), (9, 5))]
cov = [c for t_ in book_tiles for c in t_]
ok = len(cov) == len(set(cov)) == 56 and all(c[1] in fig12[c[0]] for c in cov)
ok &= all(abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1 for a, b in book_tiles)
check("11.8 Figure 11.12: the book's drawn tiling covers each square once with 28 dominoes", ok)
bad = 0
count = pos = 0
for trial in range(1500):
    n = random.randint(1, 6)
    p = random.choice([0.0, 0.1, 0.25, 0.4])
    D = [[random.random() < p for _ in range(n)] for _ in range(n)]
    truth = tile_brute(D)
    bad += domino_flow(D)[0] != truth
    pos += truth
    count += 1
check("11.8 matching test (equal colors and max flow == #black) == exhaustive tiling search", bad == 0,
      f"{count} random boards, n <= 6, {pos} tileable")
D = [[True] * 3 for _ in range(3)]
D[0][0] = D[1][2] = False
check("11.8 trap: two non-adjacent squares of opposite colors (equal counts) cannot be tiled",
      domino_flow(D)[3:] == (1, 1) and domino_flow(D)[0] is False and not tile_brute(D))
D = [[False] * 8 for _ in range(8)]
D[0][0] = D[7][7] = True
check("11.8 mutilated 8 x 8 board (opposite corners deleted): 30 vs 32 squares of the two colors -> False",
      domino_flow(D)[0] is False and domino_flow(D)[3:] == (30, 32))


# ============================================================================ Exercise 11.9
section("Exercise 11.9: one token per row and column on white squares")
fig13 = {1: [4, 5, 6], 2: [6], 3: [1, 3, 5], 4: [1, 3, 5], 5: [1, 2, 3, 5, 7, 8], 6: [3, 9], 7: [3, 8], 8: [9],
         9: [7, 8]}
book_tokens = {1: 4, 2: 6, 3: 1, 4: 5, 5: 2, 6: 3, 7: 8, 8: 9, 9: 7}
W = [[(j + 1) in fig13[i + 1] for j in range(9)] for i in range(9)]


def rooks(W):
    n = len(W)
    E = [(i, j) for i in range(n) for j in range(n) if W[i][j]]
    return max_matching(range(n), range(n), E)


val, M = rooks(W)
check("11.9 Figure 11.13: max flow == 9 -> True", val == 9)
check("11.9 Figure 11.13: the book's tokens are on white squares, one per row and column",
      sorted(book_tokens.values()) == list(range(1, 10)) and all(c in fig13[r] for r, c in book_tokens.items()))
sols = [pi for pi in itertools.permutations(range(9)) if all(W[i][pi[i]] for i in range(9))]
check("11.9 Figure 11.13: exactly 2 placements exist; the book's is one of them", len(sols) == 2 and
      tuple(book_tokens[r] - 1 for r in range(1, 10)) in sols, str([[c + 1 for c in pi] for pi in sols]))
other = [pi for pi in sols if pi != tuple(book_tokens[r] - 1 for r in range(1, 10))][0]
check("11.9 Figure 11.13: the other placement puts row 3 in column 5 and row 4 in column 1, all else equal",
      [c + 1 for c in other] == [4, 6, 5, 1, 2, 3, 8, 9, 7])
bad = 0
pos = 0
for trial in range(1500):
    n = random.randint(1, 7)
    p = random.choice([0.2, 0.35, 0.5, 0.7])
    Wr = [[random.random() < p for _ in range(n)] for _ in range(n)]
    truth = any(all(Wr[i][pi[i]] for i in range(n)) for pi in itertools.permutations(range(n)))
    bad += (rooks(Wr)[0] == n) != truth
    pos += truth
check("11.9 max flow == n  <=>  a placement exists (all permutations)", bad == 0,
      f"1500 random grids, n <= 7, {pos} positive")


# ============================================================================ Exercise 11.10
section("Exercise 11.10: nesting boxes")


def fits_rot(a, b):
    return any(all(a[p[k]] < b[k] for k in range(3)) for p in itertools.permutations(range(3)))


def fits_sorted(a, b):
    A, B = sorted(a), sorted(b)
    return all(A[k] < B[k] for k in range(3))


bad = 0
for trial in range(20000):
    a = [random.randint(11, 19) for _ in range(3)]
    b = [random.randint(11, 19) for _ in range(3)]
    bad += fits_rot(a, b) != fits_sorted(a, b)
check("11.10 some rotation of a fits in b  <=>  sorted sides of a < sorted sides of b, coordinatewise", bad == 0,
      "20000 random pairs")


def set_partitions(items):
    if not items:
        yield []
        return
    first, rest = items[0], items[1:]
    for p in set_partitions(rest):
        for k in range(len(p)):
            yield p[:k] + [[first] + p[k]] + p[k + 1:]
        yield [[first]] + p


def min_chains_brute(boxes):
    n = len(boxes)
    best = n
    for P in set_partitions(list(range(n))):
        if len(P) >= best:
            continue
        if all(all(fits_rot(boxes[x], boxes[y]) or fits_rot(boxes[y], boxes[x]) for x, y in itertools.combinations(B, 2))
               for B in P):
            best = len(P)
    return best


def nest(boxes):
    n = len(boxes)
    E = [(i, j) for i in range(n) for j in range(n) if fits_sorted(boxes[i], boxes[j])]
    val, M = max_matching(range(n), range(n), E)
    return n - val, M


bad = bad_nest = 0
for trial in range(600):
    n = random.randint(1, 8)
    boxes = [[random.randint(11, 19) for _ in range(3)] for _ in range(n)]
    vis, M = nest(boxes)
    bad += vis != min_chains_brute(boxes)
    inner = dict(M)                     # i is placed directly inside inner[i]
    ok = len(set(inner.values())) == len(inner)          # each box holds at most one box directly
    ok &= all(fits_rot(boxes[i], boxes[j]) for i, j in inner.items())
    ok &= n - len(inner) == vis
    bad_nest += not ok
check("11.10 n - (max matching) == fewest chains in a partition of the boxes (all set partitions)", bad == 0,
      "600 random sets of <= 8 boxes, sides 11..19")
check("11.10 matched pairs give a valid nesting: each box directly inside at most one, holding at most one",
      bad_nest == 0)
def max_antichain(boxes):
    n = len(boxes)
    return max(r for r in range(n + 1) for X in itertools.combinations(range(n), r)
               if not any(fits_rot(boxes[x], boxes[y]) or fits_rot(boxes[y], boxes[x]) for x, y in itertools.permutations(X, 2)))


bad = 0
for trial in range(300):
    n = random.randint(1, 8)
    boxes = [[random.randint(11, 19) for _ in range(3)] for _ in range(n)]
    bad += nest(boxes)[0] != max_antichain(boxes)
check("11.10 remark: fewest visible boxes == largest set of pairwise non-nesting boxes (Dilworth)", bad == 0,
      "300 random sets")
# page example: A..E
ex = {"A": (12, 18, 11), "B": (13, 12, 17), "C": (19, 14, 19), "D": (15, 16, 13), "E": (11, 11, 11)}
keys = list(ex)
bx = [list(ex[k]) for k in keys]
vis, M = nest(bx)
fits_pairs = sorted(keys[i] + "<" + keys[j] for i in range(5) for j in range(5) if fits_rot(bx[i], bx[j]))
check("11.10 page example: fitting pairs are exactly A<C, B<C, D<C, E<B, E<C, E<D",
      fits_pairs == sorted(["A<C", "B<C", "D<C", "E<B", "E<C", "E<D"]), str(fits_pairs))
check("11.10 page example: 3 visible boxes, and A, B, D pairwise do not nest",
      vis == 3 and min_chains_brute(bx) == 3 and max_antichain(bx) == 3 and not any(
          fits_rot(ex[x], ex[y]) for x, y in itertools.permutations("ABD", 2)),
      f"matched (inner, outer) pairs {[(keys[i], keys[j]) for i, j in M]}")
check("11.10 page example: E in B in C, with A and D alone, is a valid 3-chain nesting",
      fits_rot(ex["E"], ex["B"]) and fits_rot(ex["B"], ex["C"]))

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: {FAIL}")
