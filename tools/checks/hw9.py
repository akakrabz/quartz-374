#!/usr/bin/env python3
"""Checks for content/3-homework-and-exams/hw9-more-graph-algorithms.md (Homework 9, CS/ECE 374 A Fall 2026: the
student's submitted solutions, verified).

Problem 1 (maps: dags with one source s and one sink b).
  (a) lo[v] and hi[v] (shortest and longest path from s, in edges) by the submitted recurrences in topological
      order; 'all s-b paths have the same length' iff lo[b] = hi[b]; against an enumeration of all s-b paths of
      random maps; every vertex is reachable from s and reaches b; the page's two small maps.
  (b) R(v, h), the most relics still to be collected from v with health h, by the submitted recurrence, filled in
      reverse topological order; the answer R(s, k), or -inf; against a simulation of every s-b path; the number of
      (edge, health) steps is at most kE; damage 0 allowed; damage and relic of the boss space count; the page's
      example and its two traps.
Problem 2 (energetic walks: 2 * red < blue).
  (a) balance +2 for red, -1 for blue; Bellman-Ford from a new source finds a negative cycle iff some simple cycle
      is energetic (all simple cycles enumerated on small graphs).
  (b) the splitting step on random energetic closed walks with a repeated vertex: two closed walks, the edges and
      balances add up, each part is strictly shorter, one part is energetic; and the claim itself: the shortest
      energetic closed walk (found with a much larger balance range) has the weight of the shortest energetic
      simple cycle.
  (c) the layered graph with balances -V .. 2V exactly as on the page, Dijkstra from every (s, 0), minimum over
      (s, t), t < 0: against the enumeration of all simple cycles; its size ((3V+1)V vertices, at most (3V+1)E
      edges); the lower end -V is needed (an all-blue Hamiltonian cycle), the range -V+1 .. fails there; the
      page's example.
Every example on the page is recomputed here."""
import heapq
import itertools
import random

random.seed(11032026)
FAIL = []
INF = float("inf")
NEG = float("-inf")


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail != "" else ""))
    if not cond:
        FAIL.append(name)


# ============================================================================ Problem 1
def random_map(n, p):
    """A dag on 0 .. n-1 (edges go from smaller to larger numbers) with exactly one source 0 and one sink n-1."""
    edges = {(i, j) for i in range(n) for j in range(i + 1, n) if random.random() < p}
    for v in range(1, n):
        if not any(b == v for a, b in edges):
            edges.add((random.randrange(0, v), v))
    for v in range(0, n - 1):
        if not any(a == v for a, b in edges):
            edges.add((v, random.randrange(v + 1, n)))
    perm = list(range(1, n - 1))
    random.shuffle(perm)
    name = [0] + perm + [n - 1]            # hide the topological order in the names
    return sorted((name[a], name[b]) for a, b in edges)


def topo(n, edges):
    indeg = [0] * n
    out = [[] for _ in range(n)]
    for a, b in edges:
        out[a].append(b); indeg[b] += 1
    order = [v for v in range(n) if indeg[v] == 0]
    for v in order:
        for w in out[v]:
            indeg[w] -= 1
            if indeg[w] == 0:
                order.append(w)
    assert len(order) == n
    return order


def all_paths(n, edges, s, b):
    out = [[] for _ in range(n)]
    for u, v in edges:
        out[u].append(v)
    res = []

    def go(path):
        if path[-1] == b:
            res.append(path[:])
            return
        for w in out[path[-1]]:
            path.append(w); go(path); path.pop()
    go([s])
    return res


def lo_hi(n, edges, s):
    """Page, 1(a): lo[s] = hi[s] = 0; lo[v] = 1 + min lo[u], hi[v] = 1 + max hi[u] over edges u -> v;
    vertices in topological order."""
    inn = [[] for _ in range(n)]
    for u, v in edges:
        inn[v].append(u)
    lo, hi = [None] * n, [None] * n
    for v in topo(n, edges):
        if v == s:
            lo[v] = hi[v] = 0
        else:
            lo[v] = 1 + min(lo[u] for u in inn[v])
            hi[v] = 1 + max(hi[u] for u in inn[v])
    return lo, hi


ok_a = ok_lohi = ok_reach = True
cnt = same = 0
maps = []
for _ in range(900):
    n = random.randint(2, 9)
    edges = random_map(n, random.choice([0.15, 0.3, 0.5]))
    maps.append((n, edges))
for n, edges in maps:
    s, b = 0, n - 1
    paths = all_paths(n, edges, s, b)
    lens = {len(p) - 1 for p in paths}
    lo, hi = lo_hi(n, edges, s)
    ok_lohi &= lo[b] == min(lens) and hi[b] == max(lens)
    ok_a &= (lo[b] == hi[b]) == (len(lens) == 1)
    onpath = set().union(*[set(p) for p in paths])
    ok_reach &= onpath == set(range(n))
    same += len(lens) == 1
    cnt += 1
check(f"1(a) lo[b] and hi[b] are the lengths of the shortest and longest s-b paths ({cnt} random maps)", ok_lohi)
check(f"1(a) all s-b paths have the same length iff lo[b] = hi[b] ({same} maps with equal lengths, {cnt - same} "
      "without)", ok_a and same > 100 and cnt - same > 100)
check("1(a) with one source and one sink, every vertex lies on some s-b path (so the recurrences never see an "
      "empty min or max)", ok_reach)
D1 = [(0, 1), (0, 2), (1, 3), (2, 3)]
D2 = [(0, 1), (0, 2), (1, 2), (2, 3)]
check("1(a) examples: the diamond s->a->b, s->c->b has lo = hi = 2 (True); with the extra edge a->c "
      "(s->a, s->c, a->c, c->b) lo = 2 and hi = 3 (False)",
      (lo_hi(4, D1, 0)[0][3], lo_hi(4, D1, 0)[1][3]) == (2, 2) and (lo_hi(4, D2, 0)[0][3], lo_hi(4, D2, 0)[1][3]) == (2, 3))


def max_relics(n, edges, s, b, relic, damage, k, count=None):
    """Page, 1(b): R[b][h] = 0; R[v][h] = max{ [Relic(w)] + R[w][h - Damage(w)] : v -> w, h - Damage(w) >= 1 },
    -inf over nothing; vertices in REVERSE topological order, h = 1 .. k in any order.  Answer R[s][k]."""
    out = [[] for _ in range(n)]
    for u, v in edges:
        out[u].append(v)
    R = [[NEG] * (k + 1) for _ in range(n)]
    for v in reversed(topo(n, edges)):
        for h in range(1, k + 1):
            if v == b:
                R[v][h] = 0
                continue
            best = NEG
            for w in out[v]:
                if count is not None:
                    count[0] += 1
                h2 = h - damage[w]
                if h2 >= 1 and R[w][h2] != NEG:
                    best = max(best, (1 if relic[w] else 0) + R[w][h2])
            R[v][h] = best
    return R[s][k], R


def brute_relics(n, edges, s, b, relic, damage, k):
    best = NEG
    for p in all_paths(n, edges, s, b):
        h, r, alive = k, 0, True
        for v in p[1:]:
            h -= damage[v]
            if h <= 0:
                alive = False
                break
            r += 1 if relic[v] else 0
        if alive:
            best = max(best, r)
    return best


ok_b = ok_steps = True
cnt = dead = 0
for n, edges in maps:
    s, b = 0, n - 1
    for _ in range(2):
        k = random.randint(1, 6)
        relic = [False] + [random.random() < 0.5 for _ in range(n - 1)]
        damage = [0] + [random.choice([0, 0, 1, 1, 2, 3]) for _ in range(n - 1)]
        c = [0]
        got, _ = max_relics(n, edges, s, b, relic, damage, k, c)
        truth = brute_relics(n, edges, s, b, relic, damage, k)
        ok_b &= got == truth
        ok_steps &= c[0] <= k * len(edges)
        dead += truth == NEG
        cnt += 1
check(f"1(b) R(s, k) equals a simulation of every s-b path ({cnt} inputs, {dead} of them with no surviving path: "
      "-inf)", ok_b and dead > 100 and cnt - dead > 500)
check("1(b) at most kE recurrence terms are evaluated: O(k(V + E)) time", ok_steps)
# page example: s -> a -> b, s -> c -> b; a: relic, damage 2; c: no relic, damage 0; b: damage 1, no relic
EXE = [(0, 1), (0, 2), (1, 3), (2, 3)]
REL = [False, True, False, False]
DMG = [0, 2, 0, 1]
vals = [max_relics(4, EXE, 0, 3, REL, DMG, k)[0] for k in (1, 2, 3, 4)]
check("1(b) example (a: relic, damage 2; c: nothing; boss: damage 1): k = 1 gives -inf, k = 2 and 3 give 0, "
      "k = 4 gives 1", vals == [NEG, 0, 0, 1] == [brute_relics(4, EXE, 0, 3, REL, DMG, k) for k in (1, 2, 3, 4)], vals)
_, Rt = max_relics(4, EXE, 0, 3, REL, DMG, 4)
check("1(b) example, table for k = 4: R(a, 2) = 0 and R(a, 1) = -inf (the boss deals 1), R(s, 4) = 1 via a, "
      "R(s, 3) = 0 via c", Rt[1][2] == 0 and Rt[1][1] == NEG and Rt[0][4] == 1 and Rt[0][3] == 0)
check("1(b) trap: 'take the path with the most relics' (ignoring health) picks s->a->b, which dies for k = 3; "
      "the answer is 0, not 1 and not -inf", vals[2] == 0 and 3 - DMG[1] - DMG[3] <= 0)
check("1(b) the boss's own damage counts: with k = 1 even the harmless path s->c->b dies on entering b",
      vals[0] == NEG and 1 - DMG[2] - DMG[3] <= 0)

# ============================================================================ Problem 2
def simple_cycles(n, edges):
    """Every simple directed cycle, as a list of edge indices (loops included)."""
    out = [[] for _ in range(n)]
    for i, (u, v, col, w) in enumerate(edges):
        out[u].append((v, i))
    res = []

    def go(start, v, used, path):
        for (w, i) in out[v]:
            if w == start:
                res.append(path + [i])
            elif w > start and w not in used:
                used.add(w)
                go(start, w, used, path + [i])
                used.discard(w)
    for s in range(n):
        go(s, s, {s}, [])
    return res


def bal(e):
    return 2 if e[2] == "R" else -1


def energetic_cycle_exists(n, edges):
    """Page, 2(a): weights +2 / -1, a new source x with 0-weight edges to all vertices, Bellman-Ford."""
    dist = [0] * n                      # after relaxing the edges out of x
    for _ in range(n):                  # V + 1 vertices in all: V rounds
        for e in edges:
            if dist[e[0]] + bal(e) < dist[e[1]]:
                dist[e[1]] = dist[e[0]] + bal(e)
    return any(dist[e[0]] + bal(e) < dist[e[1]] for e in edges)


def random_colored(n, m, pred):
    return [(random.randrange(n), random.randrange(n), "R" if random.random() < pred else "B",
             random.choice([1, 2, 3, 5, 8])) for _ in range(m)]


def shortest_energetic_cycle_brute(n, edges):
    best = INF
    for cyc in simple_cycles(n, edges):
        if sum(bal(edges[i]) for i in cyc) < 0:
            best = min(best, sum(edges[i][3] for i in cyc))
    return best


def layered(n, edges, lo, hi):
    """Vertices (v, t), lo <= t <= hi; edge (u, t) -> (v, t + 2) for red u -> v, (u, t) -> (v, t - 1) for blue,
    with the weight of u -> v, whenever the new balance is in range."""
    adj = {}
    ne = 0
    for (u, v, col, w) in edges:
        d = 2 if col == "R" else -1
        for t in range(lo, hi + 1):
            if lo <= t + d <= hi:
                adj.setdefault((u, t), []).append(((v, t + d), w)); ne += 1
    return adj, n * (hi - lo + 1), ne


def dijkstra(adj, src):
    dist = {src: 0}
    pq = [(0, 0, src)]
    tie = 0
    done = set()
    while pq:
        d, _, u = heapq.heappop(pq)
        if u in done:
            continue
        done.add(u)
        for v, w in adj.get(u, []):
            if d + w < dist.get(v, INF):
                dist[v] = d + w
                tie += 1
                heapq.heappush(pq, (d + w, tie, v))
    return dist


def shortest_energetic(n, edges, lo=None, hi=None):
    """Page, 2(c): layers -V .. 2V; Dijkstra from (s, 0) for every s; min of dist((s, 0), (s, t)) over t < 0."""
    lo = -n if lo is None else lo
    hi = 2 * n if hi is None else hi
    adj, nv, ne = layered(n, edges, lo, hi)
    best = INF
    for s in range(n):
        dist = dijkstra(adj, (s, 0))
        for t in range(lo, 0):
            best = min(best, dist.get((s, t), INF))
    return best, nv, ne


ok_2a = ok_2c = ok_2b = ok_sz = ok_wide = True
cnt = yes = 0
for _ in range(1300):
    n = random.randint(1, 6)
    edges = random_colored(n, random.randint(0, 2 * n + 2), random.choice([0.2, 0.35, 0.5, 0.7]))
    brute = shortest_energetic_cycle_brute(n, edges)
    ok_2a &= energetic_cycle_exists(n, edges) == (brute < INF)
    got, nv, ne = shortest_energetic(n, edges)
    ok_2c &= got == brute
    ok_sz &= nv == (3 * n + 1) * n and ne <= (3 * n + 1) * len(edges)
    # (b): closed walks with far more room for the balance: the shortest energetic closed walk is no shorter
    wide = shortest_energetic(n, edges, -4 * n - 4, 8 * n + 8)[0]
    ok_wide &= wide == brute
    yes += brute < INF
    cnt += 1
check(f"2(a) Bellman-Ford with weights +2 / -1 reports a negative cycle iff some simple cycle is energetic "
      f"({cnt} random two-colored graphs on up to 6 vertices, {yes} with an energetic cycle)",
      ok_2a and 300 < yes < cnt - 300)
check("2(c) the layered algorithm (balances -V .. 2V, Dijkstra from every (s, 0)) returns the weight of the "
      "shortest energetic simple cycle, or infinity", ok_2c)
check("2(c) the layered graph has (3V + 1)V vertices and at most (3V + 1)E edges", ok_sz)
check("2(b) with a much wider balance range (-4V-4 .. 8V+8), which admits many more closed walks, the shortest "
      "energetic closed walk still has the weight of the shortest energetic simple cycle", ok_wide)

# the splitting step of 2(b) on explicit random closed walks
def random_closed_walk(n, edges, maxlen):
    out = [[] for _ in range(n)]
    for i, e in enumerate(edges):
        out[e[0]].append(i)
    for _ in range(200):
        s = random.randrange(n)
        v, walk = s, []
        for _ in range(maxlen):
            if not out[v]:
                break
            i = random.choice(out[v])
            walk.append(i)
            v = edges[i][1]
            if v == s and walk and random.random() < 0.4:
                return s, walk
    return None


ok_split = True
nsplit = 0
for _ in range(4000):
    n = random.randint(2, 5)
    edges = random_colored(n, random.randint(n, 3 * n), 0.25)
    rw = random_closed_walk(n, edges, 9)
    if rw is None:
        continue
    s, walk = rw
    if sum(bal(edges[i]) for i in walk) >= 0:
        continue                                    # not energetic
    verts = [s] + [edges[i][1] for i in walk]       # v_0 .. v_k, v_k = v_0
    k = len(walk)
    rep = [(i, j) for i in range(k) for j in range(i + 1, k) if verts[i] == verts[j]]
    if not rep:
        continue                                    # already a simple cycle
    i, j = random.choice(rep)
    W2 = walk[i:j]                                  # v_i -> ... -> v_j
    W1 = walk[:i] + walk[j:]                        # v_0 -> ... -> v_i = v_j -> ... -> v_k
    b1, b2 = sum(bal(edges[x]) for x in W1), sum(bal(edges[x]) for x in W2)
    w1, w2 = sum(edges[x][3] for x in W1), sum(edges[x][3] for x in W2)
    wt = sum(edges[x][3] for x in walk)
    closed1 = edges[W1[0]][0] == edges[W1[-1]][1] and all(edges[W1[t]][1] == edges[W1[t + 1]][0] for t in range(len(W1) - 1))
    closed2 = edges[W2[0]][0] == edges[W2[-1]][1] and all(edges[W2[t]][1] == edges[W2[t + 1]][0] for t in range(len(W2) - 1))
    ok_split &= (len(W1) >= 1 and len(W2) >= 1 and closed1 and closed2 and b1 + b2 == sum(bal(edges[x]) for x in walk)
                 and w1 + w2 == wt and w1 < wt and w2 < wt and (b1 < 0 or b2 < 0))
    nsplit += 1
check(f"2(b) splitting an energetic closed walk at a repeated vertex ({nsplit} random walks): two closed walks, "
      "each with at least one edge, balances and weights add up, each is strictly lighter, and at least one is "
      "energetic", ok_split and nsplit > 300)

# the range of balances
TRI = [(0, 1, "B", 1), (1, 2, "B", 1), (2, 0, "B", 1)]
check("2(c) the lower end -V is needed: an all-blue triangle is an energetic cycle of weight 3 whose balance "
      "reaches -3 = -V; with layers -V .. 2V the algorithm returns 3",
      shortest_energetic(3, TRI)[0] == 3 == shortest_energetic_cycle_brute(3, TRI))
check("2(c) ... and with layers -V+1 .. 2V-2 (a cycle wrongly assumed to have at most V - 1 edges) it finds "
      "nothing", shortest_energetic(3, TRI, -2, 4)[0] == INF)
ok_hi = True
for _ in range(600):
    n = random.randint(1, 6)
    edges = random_colored(n, random.randint(0, 2 * n + 2), random.choice([0.2, 0.35, 0.5]))
    ok_hi &= shortest_energetic(n, edges, -n, n)[0] == shortest_energetic_cycle_brute(n, edges)
check("2(c) remark: the upper layers are generous - balances -V .. V already give the same answers on 600 random "
      "graphs (a prefix balance above V could never come back below 0 within V edges)", ok_hi)
# page example: red a->b (5), blue b->c (1), blue c->a (1), blue c->d (1), blue d->a (1) ... a cheap long cycle
EXG = [(0, 1, "R", 1), (1, 2, "B", 1), (2, 0, "B", 1),          # a -R-> b -B-> c -B-> a : balance 0, not energetic
       (2, 3, "B", 4), (3, 4, "B", 4), (4, 0, "B", 4)]          # c -B-> d -B-> e -B-> a
cyc = simple_cycles(5, EXG)
info = sorted((len(c), sum(bal(EXG[i]) for i in c), sum(EXG[i][3] for i in c)) for c in cyc)
check("2 example: the cycle a b c has balance 2 - 2 = 0 (not energetic, weight 3); the cycle a b c d e has "
      "balance 2 - 4 = -2 (energetic, weight 14); there are no other cycles", info == [(3, 0, 3), (5, -2, 14)], info)
check("2 example: part (a) says yes, part (c) returns 14",
      energetic_cycle_exists(5, EXG) and shortest_energetic(5, EXG)[0] == 14)
check("2 example: the closed walk a b c a b c d e a (the short cycle, then the long one) has balance -2 and "
      "weight 17 - energetic, but longer than the simple cycle inside it", 0 + (-2) == -2 and 3 + 14 == 17)
check("2(a) a blue loop is an energetic cycle of one edge; a red loop is not",
      energetic_cycle_exists(1, [(0, 0, "B", 7)]) and shortest_energetic(1, [(0, 0, "B", 7)])[0] == 7
      and not energetic_cycle_exists(1, [(0, 0, "R", 7)]))

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: {FAIL}")
