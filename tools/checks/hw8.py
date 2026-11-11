#!/usr/bin/env python3
"""Checks for content/3-homework-and-exams/hw8-graph-algorithms.md (Homework 8, CS/ECE 374 A Fall 2026: the student's
submitted solutions, verified).

Problem 1 (tram stickers).  The state graph V x {A, B, C} exactly as on the page (travel edges at half price inside
the matching system, zero-cost peel edges A -> B -> C), Dijkstra from (s, A), answer dist(t, C):
  * against an independent formula: min over stations x, y of dA(s, x) + dB(x, y) + dC(y, t), where dS is the
    all-pairs distance with system S at half price (Floyd-Warshall);
  * against an exhaustive search over all walks with all peeling decisions on small networks;
  * the size of the state graph (3V vertices, 3E + 2V edges); dist(t, C) is the smallest of the three copies of t;
  * the six edges of the handout's worked route (cost 21.5 = 5.5 + 12 + 4), the page's two traps.
Problem 2(a) (a walk whose label string contains 374).  The submitted 4-state DFA against the definition on every
  digit string of length <= 5 and random longer ones; the product graph V x {0, 1, 2, 3} with whatever-first search
  from (s, 0), answer '(t, 3) marked': against an exhaustive enumeration of walks on small graphs and against an
  independent search that remembers the last two labels; the marked set equals {(v, state after sigma(W))};
  the posted solution's 'guess the start' variant gives the same answers; sizes 4V and 4E.
Problem 2(b) (a walk whose label string is accepted by a given DFA).  The product V x Q against an exhaustive
  enumeration of walks with the DFA simulated on each label string, for random graphs and random DFAs, including
  s = t (the empty walk, accepted iff the start state is accepting); 2(a) as the special case |Q| = 4; sizes.
Every example on the page is recomputed here."""
import heapq
import itertools
import random

random.seed(10272026)
FAIL = []
INF = float("inf")


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail != "" else ""))
    if not cond:
        FAIL.append(name)


# ============================================================================ Problem 1
SYS = "ABC"


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


def tram_state_graph(n, edges):
    """edges: (u, v, system, cost).  Returns the adjacency of G' and its vertex and edge counts."""
    adj = {}
    ne = 0
    for v in range(n):
        for a, b in (("A", "B"), ("B", "C")):
            adj.setdefault((v, a), []).append(((v, b), 0)); ne += 1
    for (u, v, sy, c) in edges:
        for S in SYS:
            adj.setdefault((u, S), []).append(((v, S), c / 2 if sy == S else c)); ne += 1
    return adj, 3 * n, ne


def tram(n, edges, s, t):
    adj, nv, ne = tram_state_graph(n, edges)
    dist = dijkstra(adj, (s, "A"))
    return dist.get((t, "C"), INF), dist, nv, ne


def tram_three_phase(n, edges, s, t):
    """Independent: three Floyd-Warshall tables, one per system at half price; min over the two peel stations."""
    D = {}
    for S in SYS:
        d = [[0 if i == j else INF for j in range(n)] for i in range(n)]
        for (u, v, sy, c) in edges:
            w = c / 2 if sy == S else c
            if u != v:
                d[u][v] = min(d[u][v], w)
        for r in range(n):
            for i in range(n):
                for j in range(n):
                    if d[i][r] + d[r][j] < d[i][j]:
                        d[i][j] = d[i][r] + d[r][j]
        D[S] = d
    return min(D["A"][s][x] + D["B"][x][y] + D["C"][y][t] for x in range(n) for y in range(n))


def tram_exhaustive(n, edges, s, t):
    """Every walk with every peeling decision, by depth-first search with a cost bound (costs are positive, so an
    optimal plan uses at most 3(n-1) edges)."""
    out = [[] for _ in range(n)]
    for (u, v, sy, c) in edges:
        out[u].append((v, sy, c))
    best = [INF]

    def go(v, state, cost, steps):
        if cost >= best[0]:
            return
        if v == t:
            best[0] = cost
        if steps == 3 * (n - 1):
            return
        if state < 2:
            go_peel(v, state + 1, cost, steps)
        for (w, sy, c) in out[v]:
            go(w, state, cost + (c / 2 if sy == SYS[state] else c), steps + 1)

    def go_peel(v, state, cost, steps):
        if state < 2:
            go_peel(v, state + 1, cost, steps)
        for (w, sy, c) in out[v]:
            go(w, state, cost + (c / 2 if sy == SYS[state] else c), steps + 1)
    go(s, 0, 0, 0)
    return best[0]


def random_net(n, m):
    return [(random.randrange(n), random.randrange(n), random.choice(SYS), random.choice([1, 2, 3, 4, 6, 8, 10]))
            for _ in range(m)]


ok_three = ok_exh = ok_size = ok_tc = True
cnt = nreach = 0
for _ in range(1500):
    n = random.randint(2, 7)
    edges = [e for e in random_net(n, random.randint(1, 3 * n)) if e[0] != e[1]]
    s, t = random.sample(range(n), 2)
    got, dist, nv, ne = tram(n, edges, s, t)
    ok_three &= abs(got - tram_three_phase(n, edges, s, t)) < 1e-9 if got < INF else tram_three_phase(n, edges, s, t) == INF
    ok_size &= nv == 3 * n and ne == 3 * len(edges) + 2 * n
    ok_tc &= got <= dist.get((t, "A"), INF) and got <= dist.get((t, "B"), INF)
    nreach += got < INF
    cnt += 1
check(f"1 Dijkstra on the state graph equals the three-phase formula min dA(s,x) + dB(x,y) + dC(y,t) ({cnt} random "
      f"networks, t reachable in {nreach})", ok_three and nreach > 500)
check("1 the state graph has 3V vertices and 3E + 2V edges", ok_size)
check("1 dist(t, C) is never larger than dist(t, A) or dist(t, B): the free peel edges make (t, C) the one target",
      ok_tc)
cnt = 0
for _ in range(400):
    n = random.randint(2, 4)
    edges = [e for e in random_net(n, random.randint(1, 2 * n)) if e[0] != e[1]]
    s, t = random.sample(range(n), 2)
    got = tram(n, edges, s, t)[0]
    ex = tram_exhaustive(n, edges, s, t)
    ok_exh &= (got == INF and ex == INF) or abs(got - ex) < 1e-9
    cnt += 1
check(f"1 ... and an exhaustive search over all walks and all peeling decisions ({cnt} small networks)", ok_exh)
# the handout's worked route: s -> b -> e -> d -> c -> f -> t
R = {"s": 0, "b": 1, "e": 2, "d": 3, "c": 4, "f": 5, "t": 6}
ROUTE = [("s", "b", "C", 1), ("b", "e", "A", 9), ("e", "d", "B", 10), ("d", "c", "A", 3), ("c", "f", "B", 8),
         ("f", "t", "C", 8)]
redges = [(R[u], R[v], sy, c) for u, v, sy, c in ROUTE]
check("1 handout route: as A on s->b->e costs 1 + 4.5 = 5.5, as B on e->d->c->f costs 5 + 3 + 4 = 12, as C on f->t "
      "costs 4; total 21.5", 1 + 9 / 2 == 5.5 and 10 / 2 + 3 + 8 / 2 == 12 and 8 / 2 == 4 and 5.5 + 12 + 4 == 21.5)
check("1 handout route: on these six edges the algorithm returns 21.5",
      tram(7, redges, R["s"], R["t"])[0] == 21.5 == tram_exhaustive(7, redges, R["s"], R["t"]))
single = {S: sum(c / 2 if sy == S else c for _, _, sy, c in ROUTE) for S in SYS}
check("1 handout route: never peeling costs 33, peeling once at the start 30, both at the start 34.5 - one system "
      "for the whole trip is not optimal", single == {"A": 33.0, "B": 30.0, "C": 34.5}, single)
TR = [(0, 1, "C", 10), (1, 2, "A", 10)]
check("1 trap: s -> x in system C then x -> t in system A, 10 each: the answer is 15, not 10 - the card cannot go "
      "back from C to A", tram(3, TR, 0, 2)[0] == 15 == tram_exhaustive(3, TR, 0, 2)
      and sum(c / 2 for _, _, _, c in TR) == 10)
check("1 an unreachable t gives infinity", tram(3, [(0, 1, "A", 2)], 0, 2)[0] == INF)

# ============================================================================ Problem 2
def next374(j, d):
    """The submitted transition table: state j < 3 = length of the longest suffix read that is a prefix of 374."""
    if j == 3:
        return 3
    if d == 3:
        return 1
    if j == 1 and d == 7:
        return 2
    if j == 2 and d == 4:
        return 3
    return 0


TABLE = {0: {3: 1, 7: 0, 4: 0, "other": 0}, 1: {3: 1, 7: 2, 4: 0, "other": 0}, 2: {3: 1, 7: 0, 4: 3, "other": 0},
         3: {3: 3, 7: 3, 4: 3, "other": 3}}
check("2(a) the function used below is the page's table (rows 0-3, columns 3, 7, 4, other)",
      all(next374(j, d) == TABLE[j][d if d in (3, 7, 4) else "other"] for j in range(4) for d in range(10)))


def run374(x):
    j = 0
    for d in x:
        j = next374(j, d)
    return j


ok = True
cnt = 0
for L in range(0, 6):
    for x in itertools.product(range(10), repeat=L):
        cnt += 1
        ok &= (run374(x) == 3) == ("374" in "".join(map(str, x)))
for _ in range(20000):
    x = [random.choice([3, 7, 4, 3, 7, 4, 0, 9]) for _ in range(random.randint(6, 14))]
    cnt += 1
    ok &= (run374(x) == 3) == ("374" in "".join(map(str, x)))
check(f"2(a) the DFA ends in state 3 exactly on the strings that contain 374 ({cnt} strings: all of length <= 5 "
      "over ten digits, random longer ones)", ok)
ok = True
for L in range(0, 6):
    for x in itertools.product([3, 7, 4, 5], repeat=L):
        j = run374(x)
        if j < 3:
            sx = "".join(map(str, x))
            longest = max(k for k in range(0, 3) if sx.endswith("374"[:k]))
            ok &= j == longest
check("2(a) in a state j < 3, j is the length of the longest suffix of the input that is a prefix of 374", ok)


def wfs(start, succ):
    marked = set()
    bag = [start]
    while bag:
        u = bag.pop()
        if u in marked:
            continue
        marked.add(u)
        bag.extend(succ(u))
    return marked


def product_marked(n, edges, lab, delta, q0):
    """Page: V' = V x Q, edge (u, q) -> (v, delta(q, lab(v))) for every edge u -> v and state q; WFS from (s, q0)."""
    out = [[] for _ in range(n)]
    for u, v in edges:
        out[u].append(v)
    return lambda s: wfs((s, q0), lambda z: [(v, delta(z[1], lab[v])) for v in out[z[0]]])


def has374(n, edges, lab, s, t):
    return (t, 3) in product_marked(n, edges, lab, next374, 0)(s)


def walks_states(n, edges, lab, s, delta, q0, L):
    """All (end vertex, DFA state) pairs over all walks from s with at most L edges, by plain enumeration."""
    out = [[] for _ in range(n)]
    for u, v in edges:
        out[u].append(v)
    seen = set()

    def go(v, q, steps):
        seen.add((v, q))
        if steps == L:
            return
        for w in out[v]:
            go(w, delta(q, lab[w]), steps + 1)
    go(s, q0, 0)
    return seen


def walks_contain374(n, edges, lab, s, t, L):
    """Enumerate walks as explicit label strings and search for the substring - no automaton."""
    out = [[] for _ in range(n)]
    for u, v in edges:
        out[u].append(v)
    found = [False]

    def go(v, text, steps):
        if found[0]:
            return
        if v == t and "374" in text:
            found[0] = True
            return
        if steps == L:
            return
        for w in out[v]:
            go(w, text + str(lab[w]), steps + 1)
    go(s, "", 0)
    return found[0]


def last_two_search(n, edges, lab, s, t):
    """Independent of the DFA: states (vertex, last two labels read, found?)."""
    out = [[] for _ in range(n)]
    for u, v in edges:
        out[u].append(v)

    def succ(z):
        v, tail, f = z
        res = []
        for w in out[v]:
            nt = (tail + str(lab[w]))[-3:]
            res.append((w, nt[-2:], f or nt == "374"))
        return res
    return any(v == t and f for (v, tail, f) in wfs((s, "", False), succ))


def guess_start(n, edges, lab, s, t):
    """The posted solution's variant: layers eps, 3, 37, 374; stay in eps or guess that a 374 starts here."""
    out = [[] for _ in range(n)]
    for u, v in edges:
        out[u].append(v)

    def succ(z):
        u, st = z
        res = []
        for v in out[u]:
            if st == 0:
                res.append((v, 0))
                if lab[v] == 3:
                    res.append((v, 1))
            elif st == 1 and lab[v] == 7:
                res.append((v, 2))
            elif st == 2 and lab[v] == 4:
                res.append((v, 3))
            elif st == 3:
                res.append((v, 3))
        return res
    return (t, 3) in wfs((s, 0), succ)


def small_out_graph(n, maxout):
    edges = []
    for u in range(n):
        for v in random.sample(range(n), random.randint(0, min(maxout, n))):
            edges.append((u, v))
    return edges


def planted374(n, maxout):
    """A random graph and labeling in which, half of the time, some 3 -> 7 -> 4 path is planted."""
    edges = small_out_graph(n, maxout)
    lab = [random.choice([3, 7, 4, 3, 7, 4, 5]) for _ in range(n)]
    if n >= 3 and random.random() < 0.6:
        a, b, c = random.sample(range(n), 3)
        lab[a], lab[b], lab[c] = 3, 7, 4
        edges = [e for e in edges if e[0] not in (a, b) or random.random() < 0.5] + [(a, b), (b, c)]
        edges = list(dict.fromkeys(edges))
        edges = [e for i, e in enumerate(edges) if sum(1 for f in edges[:i] if f[0] == e[0]) < maxout + 1]
    return edges, lab


ok_enum = ok_set = ok_last2 = ok_guess = ok_sz = True
cnt = yes = 0
for trial in range(420):
    n = 3 if trial % 3 else 4
    edges, lab = planted374(n, 2)
    s, t = random.randrange(n), random.randrange(n)
    got = has374(n, edges, lab, s, t)
    L = 4 * n - 1
    ok_enum &= got == walks_contain374(n, edges, lab, s, t, L)
    ok_set &= product_marked(n, edges, lab, next374, 0)(s) == walks_states(n, edges, lab, s, next374, 0, L)
    ok_last2 &= got == last_two_search(n, edges, lab, s, t)
    ok_guess &= got == guess_start(n, edges, lab, s, t)
    yes += got
    cnt += 1
check(f"2(a) '(t, 3) is marked' equals an enumeration of all walks with at most 4V - 1 edges, read as strings and "
      f"searched for 374 ({cnt} graphs on 3-4 vertices, {yes} yes)", ok_enum and 40 < yes < cnt - 40)
check("2(a) the marked set is exactly {(v, state of M after sigma(W))} over all walks W from s (the lemma)", ok_set)
cnt = yes = 0
for _ in range(1500):
    n = random.randint(3, 9)
    edges, lab = planted374(n, 3)
    s, t = random.randrange(n), random.randrange(n)
    got = has374(n, edges, lab, s, t)
    ok_last2 &= got == last_two_search(n, edges, lab, s, t)
    ok_guess &= got == guess_start(n, edges, lab, s, t)
    reach = product_marked(n, edges, lab, next374, 0)(s)
    ok_sz &= len(reach) <= 4 * n
    yes += got
    cnt += 1
check(f"2(a) ... and an independent search that remembers the last two labels ({cnt} more graphs on 3-9 vertices, "
      f"{yes} yes)", ok_last2 and 200 < yes < cnt - 200)
check("2(a) the posted solution's 'guess where 374 starts' layers give the same answers", ok_guess)
check("2(a) at most 4V product vertices are marked", ok_sz)
# page examples for 2(a)
EX = [(0, 1), (1, 2), (2, 3), (3, 1)]            # s=0 -> 3 -> 7 -> 4 -> back to the 3
EL = [5, 3, 7, 4]
check("2(a) example: vertices labeled 5, 3, 7, 4 with edges s->a->b->c->a: the walk s a b c has string 374, so "
      "(c, 3) is marked; so is (a, 3) (go round once more); (s, 3) is not",
      has374(4, EX, EL, 0, 3) and has374(4, EX, EL, 0, 1) and not has374(4, EX, EL, 0, 0))
check("2(a) example: the first label is not read - starting AT the vertex labeled 3, the walk a b c has string 74 "
      "and no walk from a to c of length 2 contains 374, but going round the cycle does",
      "".join(str(EL[v]) for v in [2, 3]) == "74" and has374(4, EX, EL, 1, 3)
      and not walks_contain374(4, EX, EL, 1, 3, 2) and walks_contain374(4, EX, EL, 1, 3, 5))
check("2(a) with s = t and no edges the answer is False (the empty string does not contain 374)",
      not has374(1, [], [3], 0, 0))


# ---- 2(b)
def accepts_walk(n, edges, lab, s, t, delta, q0, acc):
    return any(v == t and q in acc for (v, q) in product_marked(n, edges, lab, delta, q0)(s))


ok_b = ok_empty = ok_bsz = True
cnt = yes = 0
for _ in range(900):
    n = random.randint(1, 4)
    edges = small_out_graph(n, 2)
    sig = random.choice([2, 3])
    lab = [random.randrange(sig) for _ in range(n)]
    Q = random.randint(1, 3)
    tab = [[random.randrange(Q) for _ in range(sig)] for _ in range(Q)]
    delta = lambda q, a, tab=tab: tab[q][a]
    acc = {q for q in range(Q) if random.random() < 0.4}
    s, t = random.randrange(n), random.randrange(n)
    got = accepts_walk(n, edges, lab, s, t, delta, 0, acc)
    brute = any(v == t and q in acc for (v, q) in walks_states(n, edges, lab, s, delta, 0, n * Q - 1))
    ok_b &= got == brute
    ok_bsz &= len(product_marked(n, edges, lab, delta, 0)(s)) <= n * Q
    if s == t and not edges:
        ok_empty &= got == (0 in acc)
    yes += got
    cnt += 1
check(f"2(b) the product V x Q equals an enumeration of all walks with at most V*Q - 1 edges, with the DFA simulated "
      f"on each label string ({cnt} random graphs and DFAs, {yes} yes)", ok_b and 150 < yes < cnt - 150)
check("2(b) at most V*Q product vertices are marked", ok_bsz)
check("2(b) with s = t and no edges, the answer is True exactly when the start state is accepting (the empty walk)",
      ok_empty and accepts_walk(1, [], [0], 0, 0, lambda q, a: 0, 0, {0})
      and not accepts_walk(1, [], [0], 0, 0, lambda q, a: 0, 0, set()))
ok = True
for _ in range(500):
    n = random.randint(3, 7)
    edges, lab = planted374(n, 3)
    s, t = random.randrange(n), random.randrange(n)
    ok &= has374(n, edges, lab, s, t) == accepts_walk(n, edges, lab, s, t, next374, 0, {3})
check("2(b) with the 374 automaton (Q = 4, accepting state 3) the general algorithm is the algorithm of 2(a)", ok)
# sizes of the full product graph
n, edges = 5, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0), (0, 2)]
check("2 the full product graph has |V||Q| vertices and |E||Q| edges (5 vertices, 6 edges, Q = 4: 20 and 24)",
      len([(v, q) for v in range(n) for q in range(4)]) == 20
      and len([((u, q), (v, next374(q, 3))) for (u, v) in edges for q in range(4)]) == 24)

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: {FAIL}")
