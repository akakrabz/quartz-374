#!/usr/bin/env python3
"""Checks for content/3-homework-and-exams/lab-10a.md (Lab 10a, CS/ECE 374 A Fall 2026: shortest paths).

No official solutions were posted, so every algorithm on the page is implemented exactly as the page states it and
compared with brute force that never uses the page's ideas:

  Problem 1 (one negative edge u->v, no negative cycle): Bellman-Ford from s, and an exhaustive search over all simple
      paths, against (a) two Dijkstra runs in G - (u->v) combined as min{d_s(t), d_s(u) + w(u->v) + d_v(t)}, with the
      path rebuilt from the predecessor pointers; (b) one Dijkstra run in the two-layer graph; (c) the book's Dijkstra
      (re-inserting a vertex whose distance drops) run on G itself, instrumented: extractions per vertex, the drop in
      the extracted keys, finality of every extraction after u's, operation counts.  Also NonnegativeDijkstra and early
      stopping, which the page says fail, and the page's worked example (numbers and the run table).
  Problem 2 (meeting city): two Dijkstra runs and a scan, against exhaustive simple-path search from p and q, on random
      undirected (and, for the remark, directed) weighted graphs; the traps and the remarks.
  Problem 3 (looped trees): the split-root dag with DagSSSP and the closed form D/L, against Floyd-Warshall for all
      pairs on random looped trees; edge counts, the dag claim, the handout's figure numbers, the single-cycle case, the
      work of the one-query procedure on growing trees."""
import heapq
import itertools
import math
import random
import sys

random.seed(1028)
sys.setrecursionlimit(100000)
INF = math.inf
FAIL = []


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail != "" else ""))
    if not cond:
        FAIL.append(name)


# =============================================================================================== generic black boxes
def out_lists(V, E):
    """E: dict (a, b) -> weight (no parallel edges)."""
    out = {v: [] for v in V}
    for (a, b), w in E.items():
        out[a].append((b, w))
    return out


def book_dijkstra(V, E, s, tiebreak=None, stop=None):
    """The book's / lecture's Dijkstra (Ford's framework): Insert s; ExtractMin; relax every tense out-edge; a relaxed
    vertex is DecreaseKey'd if it is in the queue and Insert'ed (again) otherwise.  Priority queue = heap with stale
    entries skipped (semantically a DecreaseKey).  Ties between equal keys are broken by `tiebreak` (random if None).
    Returns dist, pred, the extraction log [(v, key)], and operation counts."""
    out = out_lists(V, E)
    rnd = tiebreak or random.random
    dist = {v: INF for v in V}
    pred = {v: None for v in V}
    dist[s] = 0
    inq = {v: False for v in V}
    heap = [(0, rnd(), s)]
    inq[s] = True
    log = []
    ops = dict(insert=1, decrease=0, extract=0, relax=0, scan=0)
    while heap:
        key, _, x = heapq.heappop(heap)
        if not inq[x] or key != dist[x]:
            continue                                  # stale entry: not a real queue element
        inq[x] = False
        ops["extract"] += 1
        log.append((x, key))
        if stop is not None and x == stop:
            break
        for y, w in out[x]:
            ops["scan"] += 1
            if dist[x] + w < dist[y]:                 # tense
                dist[y] = dist[x] + w
                pred[y] = x
                ops["relax"] += 1
                if inq[y]:
                    ops["decrease"] += 1
                else:
                    ops["insert"] += 1
                    inq[y] = True
                heapq.heappush(heap, (dist[y], rnd(), y))
    return dist, pred, log, ops


def nonneg_dijkstra(V, E, s):
    """NonnegativeDijkstra: every vertex extracted once and never scanned again (a 'finished' set)."""
    out = out_lists(V, E)
    dist = {v: INF for v in V}
    dist[s] = 0
    done = set()
    heap = [(0, s)]
    while heap:
        d, x = heapq.heappop(heap)
        if x in done or d != dist[x]:
            continue
        done.add(x)
        for y, w in out[x]:
            if y not in done and dist[x] + w < dist[y]:
                dist[y] = dist[x] + w
                heapq.heappush(heap, (dist[y], y))
    return dist


def dijkstra(V, E, s):
    """Black-box Dijkstra for non-negative weights (asserted)."""
    assert all(w >= 0 for w in E.values())
    d, p, _, _ = book_dijkstra(V, E, s)
    return d, p


def bellman_ford(V, E, s):
    """Distances from s; None if a negative cycle is reachable from s."""
    d = {v: INF for v in V}
    d[s] = 0
    for _ in range(len(V) - 1):
        for (a, b), w in E.items():
            if d[a] + w < d[b]:
                d[b] = d[a] + w
    for (a, b), w in E.items():
        if d[a] + w < d[b]:
            return None
    return d


def has_negative_cycle(V, E):
    d = {v: 0 for v in V}                            # virtual source to all
    for _ in range(len(V)):
        ch = False
        for (a, b), w in E.items():
            if d[a] + w < d[b]:
                d[b] = d[a] + w
                ch = True
        if not ch:
            return False
    return True


def simple_path_min(V, E, s):
    """Exhaustive: for every t, the minimum length over all simple paths from s to t (also returns, for each t, the
    largest number of times any shortest simple path uses a given edge -- always <= 1 by definition)."""
    out = out_lists(V, E)
    best = {v: INF for v in V}
    best[s] = 0

    def go(x, length, seen):
        for y, w in out[x]:
            if y not in seen:
                if length + w < best[y]:
                    best[y] = length + w
                seen.add(y)
                go(y, length + w, seen)
                seen.discard(y)
    go(s, 0, {s})
    return best


def floyd(V, E):
    d = {(a, b): (0 if a == b else INF) for a in V for b in V}
    for (a, b), w in E.items():
        d[(a, b)] = min(d[(a, b)], w)
    for k in V:
        for a in V:
            dak = d[(a, k)]
            if dak == INF:
                continue
            for b in V:
                if dak + d[(k, b)] < d[(a, b)]:
                    d[(a, b)] = dak + d[(k, b)]
    return d


def walk_length(E, walk):
    return sum(E[(walk[i], walk[i + 1])] for i in range(len(walk) - 1))


def pred_path(pred, s, x):
    p = [x]
    while p[-1] != s:
        p.append(pred[p[-1]])
        assert len(p) <= len(pred) + 1
    return p[::-1]


# =============================================================================================== Problem 1
print("== Problem 1: shortest s-t path with exactly one negative edge u->v (no negative cycle)")


def p1_two_runs(V, E, neg, s, t):
    """Page, Solution 1: G+ = G - (u->v); Dijkstra in G+ from s (d_s) and from v (d_v);
    answer min{d_s(t), d_s(u) + w(u->v) + d_v(t)}; ties go to d_s(t).  Returns (length, walk or None)."""
    u, v = neg
    Gp = {e: w for e, w in E.items() if e != neg}
    ds, ps = dijkstra(V, Gp, s)
    dv, pv = dijkstra(V, Gp, v)
    first = ds[t]
    second = ds[u] + E[neg] + dv[t]
    if first == INF and second == INF:
        return INF, None
    if first <= second:
        return first, pred_path(ps, s, t)
    return second, pred_path(ps, s, u) + pred_path(pv, v, t)


def p1_layered(V, E, neg, s, t):
    """Page, the one-run variant: two copies of G+; the edge (u,0)->(v,1) gets weight 0;
    answer min{dist((s,0),(t,0)), dist((s,0),(t,1)) + w(u->v)}."""
    u, v = neg
    HV = [(x, i) for x in V for i in (0, 1)]
    HE = {}
    for (a, b), w in E.items():
        if (a, b) != neg:
            HE[((a, 0), (b, 0))] = w
            HE[((a, 1), (b, 1))] = w
    HE[((u, 0), (v, 1))] = 0
    d, _ = dijkstra(HV, HE, (s, 0))
    return min(d[(t, 0)], d[(t, 1)] + E[neg])


def random_one_negative(n, p, wmax=9, negmax=15):
    """A random directed graph on n vertices with exactly one negative edge and no negative cycle."""
    while True:
        V = list(range(n))
        E = {}
        for a in V:
            for b in V:
                if a != b and random.random() < p:
                    E[(a, b)] = random.randint(0, wmax)
        if not E:
            continue
        neg = random.choice(sorted(E))
        E[neg] = -random.randint(1, negmax)
        if not has_negative_cycle(V, E):
            return V, E, neg


stats = dict(graphs=0, pairs=0, neg_used=0, twice=0, t_twice=0, t_first_wrong=0, nonneg_wrong=0, drops=0,
             ties_simple=0)
bad = []
maxext = 0
for trial in range(6000):
    n = random.randint(2, 7)
    V, E, neg = random_one_negative(n, random.choice([0.25, 0.4, 0.6, 0.9]))
    u, v = neg
    stats["graphs"] += 1
    s = random.choice(V)
    bf = bellman_ford(V, E, s)
    sp = simple_path_min(V, E, s)
    if bf != sp:
        bad.append(("bf vs simple paths", V, E, s))
    # (c) the book's Dijkstra on G as it is
    dist, pred, log, ops = book_dijkstra(V, E, s)
    if dist != bf:
        bad.append(("book dijkstra", V, E, s))
    cnt = {x: 0 for x in V}
    for x, _ in log:
        cnt[x] += 1
    maxext = max(maxext, max(cnt.values()))
    if max(cnt.values()) > 2 or cnt[u] > 1:
        bad.append(("extractions", V, E, s, cnt))
    if max(cnt.values()) == 2:
        stats["twice"] += 1
    # keys drop at most once, and only from u's extraction to the extraction of v right after it
    drops = [i for i in range(len(log) - 1) if log[i + 1][1] < log[i][1]]
    stats["drops"] += len(drops)
    if len(drops) > 1 or any(log[i][0] != u or log[i + 1][0] != v for i in drops):
        bad.append(("drops", V, E, s, log))
    # every extraction after u's (only) extraction is final; so is every extraction if u is never extracted
    iu = next((i for i, (x, _) in enumerate(log) if x == u), None)
    for i, (x, key) in enumerate(log):
        if (iu is None or i > iu) and key != bf[x]:
            bad.append(("final after u", V, E, s, log))
    # operation counts: ExtractMin <= 2V, relaxations (= Insert + DecreaseKey - 1) <= 2E
    if ops["extract"] > 2 * len(V) or ops["relax"] > 2 * len(E) or ops["insert"] + ops["decrease"] != ops["relax"] + 1:
        bad.append(("ops", V, E, s, ops))
    # the predecessor path is a shortest path, and simple
    for t in V:
        if bf[t] < INF:
            pp = pred_path(pred, s, t)
            if walk_length(E, pp) != bf[t] or len(set(pp)) != len(pp):
                bad.append(("pred path", V, E, s, t))
    # NonnegativeDijkstra is sometimes wrong
    if nonneg_dijkstra(V, E, s) != bf:
        stats["nonneg_wrong"] += 1
    for t in V:
        stats["pairs"] += 1
        if cnt[t] == 2:
            stats["t_twice"] += 1
            first_key = next(k for x, k in log if x == t)
            if first_key != bf[t]:
                stats["t_first_wrong"] += 1
        # (a) two runs in G+
        L, walk = p1_two_runs(V, E, neg, s, t)
        if L != bf[t]:
            bad.append(("two runs", V, E, s, t))
        if walk is not None:
            if walk[0] != s or walk[-1] != t or walk_length(E, walk) != L:
                bad.append(("two runs walk", V, E, s, t, walk))
            if len(set(walk)) != len(walk):              # ties go to d_s(t): the walk is a simple path
                bad.append(("two runs walk not simple", V, E, s, t, walk))
            if neg in zip(walk, walk[1:]):
                stats["neg_used"] += 1
        # (b) one run in the two-layer graph
        if p1_layered(V, E, neg, s, t) != bf[t]:
            bad.append(("layered", V, E, s, t))
check("random graphs with one negative edge: Bellman-Ford == exhaustive simple-path search (a shortest walk is a "
      "simple path, so it uses u->v at most once)", not [b for b in bad if b[0] == "bf vs simple paths"],
      f"{stats['graphs']} graphs")
check("Solution 1: min{d_s(t), d_s(u) + w(u->v) + d_v(t)} from two Dijkstra runs in G - (u->v) == Bellman-Ford, "
      "every source/target pair", not [b for b in bad if b[0] == "two runs"],
      f"{stats['pairs']} pairs, {stats['neg_used']} of them answered through u->v")
check("Solution 1: the rebuilt walk (pred path to u, u->v, pred path from v; or pred path to t) goes from s to t, has "
      "the computed length, and with ties to d_s(t) is a simple path",
      not [b for b in bad if b[0] in ("two runs walk", "two runs walk not simple")])
check("one-run variant: Dijkstra in the two-layer graph, crossing edge of weight 0, then + w(u->v) == Bellman-Ford",
      not [b for b in bad if b[0] == "layered"])
check("Solution 2: the book's Dijkstra on G unmodified computes every distance correctly (any tie-breaking)",
      not [b for b in bad if b[0] == "book dijkstra"])
check("Solution 2: every vertex is extracted at most twice, the tail u at most once", not [b for b in bad if b[0] ==
      "extractions"], f"max extractions of one vertex: {maxext}; graphs with a vertex extracted twice: {stats['twice']}")
check("Solution 2: the extracted keys decrease at most once, from the extraction of u to the extraction of v right "
      "after it", not [b for b in bad if b[0] == "drops"], f"{stats['drops']} drops in {stats['graphs']} runs")
check("Solution 2: every extraction after u's extraction (all of them if u is never extracted) has its final "
      "distance", not [b for b in bad if b[0] == "final after u"])
check("Solution 2: ExtractMin <= 2V and relaxations <= 2E; Insert + DecreaseKey = relaxations + 1",
      not [b for b in bad if b[0] == "ops"])
check("Solution 2: predecessor paths are shortest simple paths", not [b for b in bad if b[0] == "pred path"])
check("the bound 'twice' is attained, and a target can leave the queue first with a wrong distance (no early stop "
      "at its first extraction)", stats["twice"] > 0 and stats["t_first_wrong"] > 0,
      f"targets extracted twice: {stats['t_twice']}, first key wrong: {stats['t_first_wrong']}")
check("NonnegativeDijkstra (a finished vertex is never scanned again) is wrong on some of these graphs",
      stats["nonneg_wrong"] > 0, f"{stats['nonneg_wrong']} of {stats['graphs']} graphs")
if bad:
    print("   first failure:", bad[0])

# ---- the "stale copies" heap (no DecreaseKey, no in-queue flags; skip an entry whose key exceeds dist) is the same
def lazy_dijkstra(V, E, s):
    out = out_lists(V, E)
    dist = {v: INF for v in V}
    dist[s] = 0
    heap = [(0, s)]
    log = []
    while heap:
        k, x = heapq.heappop(heap)
        if k > dist[x]:
            continue
        log.append((x, k))
        for y, w in out[x]:
            if k + w < dist[y]:
                dist[y] = k + w
                heapq.heappush(heap, (dist[y], y))
    return dist, log


oklazy = True
for trial in range(2000):
    V, E, neg = random_one_negative(random.randint(2, 7), 0.5)
    s0 = random.choice(V)
    d1, _, l1, _ = book_dijkstra(V, E, s0, tiebreak=lambda: 0.0)
    d2, l2 = lazy_dijkstra(V, E, s0)
    oklazy &= d1 == d2 and l1 == l2
check("a heap with stale copies (skip a popped key > dist) makes exactly the same extractions as Insert/DecreaseKey",
      oklazy)

# ---- adversarial: large negative weights (tight against negative cycles), zero-weight edges, many ties
bad2 = 0
for trial in range(3000):
    n = random.randint(2, 7)
    V = list(range(n))
    E = {}
    for a in V:
        for b in V:
            if a != b and random.random() < 0.5:
                E[(a, b)] = random.choice([0, 0, 1, 1, 2, 5])
    if not E:
        continue
    neg = random.choice(sorted(E))
    u, v = neg
    E[neg] = 0
    back = bellman_ford(V, {e: w for e, w in E.items() if e != neg}, v)
    lim = back[u] if back is not None and back[u] < INF else 20      # most negative weight without a negative cycle
    E[neg] = -random.randint(1, max(1, lim)) if lim > 0 else -random.randint(1, 20)
    if has_negative_cycle(V, E):
        continue
    for s in V:
        bf = bellman_ford(V, E, s)
        for tb in (lambda: 0.0, None):
            dist, _, log, _ = book_dijkstra(V, E, s, tiebreak=tb)
            cnt = {x: 0 for x in V}
            for x, _k in log:
                cnt[x] += 1
            if dist != bf or max(cnt.values()) > 2 or cnt[u] > 1:
                bad2 += 1
        for t in V:
            if p1_two_runs(V, E, neg, s, t)[0] != bf[t] or p1_layered(V, E, neg, s, t) != bf[t]:
                bad2 += 1
check("adversarial graphs (zero-weight cycles, |w(u->v)| up to the limit set by the cycles through u->v, fixed and "
      "random tie-breaking): all three solutions correct, extraction bounds hold", bad2 == 0, f"{bad2} failures")

# ---- operation counts on growing graphs
rows = []
okg = True
for n in (200, 800, 3200):
    m = 4 * n
    V = list(range(n))
    while True:
        E = {}
        while len(E) < m:
            a, b = random.randrange(n), random.randrange(n)
            if a != b:
                E[(a, b)] = random.randint(1, 100)
        neg = random.choice(sorted(E))
        u, v = neg
        Gp = {e: w for e, w in E.items() if e != neg}
        dv, _ = dijkstra(V, Gp, v)
        if dv[u] < INF and dv[u] > 1:
            E[neg] = -int(dv[u])                  # as negative as possible: the cycles through u->v weigh >= 0
            break
    while True:                                   # a source that reaches u
        s = random.choice(V)
        if dijkstra(V, Gp, s)[0][u] < INF:
            break
    dist, _, log, ops = book_dijkstra(V, E, s)
    twice = sum(1 for x in V if sum(1 for y, _k in log if y == x) == 2)
    okg &= ops["extract"] <= 2 * n and ops["relax"] <= 2 * len(E) and dist == bellman_ford(V, E, s)
    rows.append(f"V={n}: ExtractMin/V={ops['extract'] / n:.2f} ({twice} vertices twice), "
                f"relax/E={ops['relax'] / len(E):.2f}")
check("growing random graphs (E = 4V, w(u->v) = -d_v(u), the most negative allowed): ExtractMin <= 2V, relaxations "
      "<= 2E, correct", okg, "; ".join(rows))

# ---- the page's example
EX_V = ["s", "a", "b", "t", "u", "v"]
EX = {("s", "a"): 1, ("s", "u"): 7, ("a", "b"): 2, ("a", "t"): 6, ("b", "t"): 3, ("u", "v"): -5, ("v", "b"): 0,
      ("t", "a"): 2}
EXNEG = ("u", "v")
check("example: exactly one negative edge, no negative cycle, and not a dag (t->a->t)",
      sum(w < 0 for w in EX.values()) == 1 and not has_negative_cycle(EX_V, EX) and ("t", "a") in EX)
Gp = {e: w for e, w in EX.items() if e != EXNEG}
ds, _ = dijkstra(EX_V, Gp, "s")
dv, _ = dijkstra(EX_V, Gp, "v")
check("example: d_s = s 0, a 1, b 3, t 6, u 7, v inf", ds == dict(s=0, a=1, b=3, t=6, u=7, v=INF), ds)
check("example: d_v = v 0, b 0, t 3, a 5, s inf, u inf", dv == dict(s=INF, a=5, b=0, t=3, u=INF, v=0), dv)
bfx = bellman_ford(EX_V, EX, "s")
check("example: delta(s,t) = min{6, 7 - 5 + 3} = 5 along s u v b t; true distances s 0, a 1, u 7, v 2, b 2, t 5",
      min(ds["t"], ds["u"] - 5 + dv["t"]) == 5 == bfx["t"] and bfx == dict(s=0, a=1, u=7, v=2, b=2, t=5)
      and walk_length(EX, ["s", "u", "v", "b", "t"]) == 5 and p1_two_runs(EX_V, EX, EXNEG, "s", "t") ==
      (5, ["s", "u", "v", "b", "t"]), bfx)
dist, pred, log, ops = book_dijkstra(EX_V, EX, "s", tiebreak=lambda: 0.0)
check("example: the book's Dijkstra extracts s 0, a 1, b 3, t 6, u 7, v 2, b 2, t 5 (b and t twice, u once)",
      log == [("s", 0), ("a", 1), ("b", 3), ("t", 6), ("u", 7), ("v", 2), ("b", 2), ("t", 5)], log)
check("example: the run makes 8 Insert (b and t twice), 1 DecreaseKey (t 7 -> 6 while queued), 8 ExtractMin",
      (ops["insert"], ops["decrease"], ops["extract"]) == (8, 1, 8), ops)
check("example: stopping at t's first extraction would report 6; NonnegativeDijkstra reports 6",
      book_dijkstra(EX_V, EX, "s", tiebreak=lambda: 0.0, stop="t")[0]["t"] == 6 and nonneg_dijkstra(EX_V, EX, "s")["t"]
      == 6)
check("example: the one-run layered graph also gives 5", p1_layered(EX_V, EX, EXNEG, "s", "t") == 5)


def nonneg_dijkstra_book(V, E, s):
    """The book's NonnegativeDijkstra: every vertex inserted at the start; tense edges relaxed (also into extracted
    vertices), but an extracted vertex is never extracted or scanned again."""
    out = out_lists(V, E)
    dist = {v: INF for v in V}
    dist[s] = 0
    Q = set(V)
    while Q:
        x = min(Q, key=lambda z: (dist[z], str(z)))
        Q.discard(x)
        for y, w in out[x]:
            if dist[x] + w < dist[y]:
                dist[y] = dist[x] + w
    return dist


nb = nonneg_dijkstra_book(EX_V, EX, "s")
check("example: the book's NonnegativeDijkstra lowers b to 2 but never rescans it, and reports 6 for t",
      nb["t"] == 6 and nb["b"] == 2)
shift = {e: w + 5 for e, w in EX.items()}
dsh, psh = dijkstra(EX_V, shift, "s")
check("trap: adding 5 to every edge makes Dijkstra pick s a t (shifted 17, real length 7), not s u v b t (shifted 25)",
      dsh["t"] == 17 and pred_path(psh, "s", "t") == ["s", "a", "t"] and walk_length(EX, ["s", "a", "t"]) == 7 and
      walk_length(shift, ["s", "u", "v", "b", "t"]) == 25 and walk_length(shift, ["s", "a", "b", "t"]) == 21)

# the run table on the page: after each extraction, the queue contents
rows = []
dist = {x: INF for x in EX_V}
dist["s"] = 0
Q = {"s": 0}
out = out_lists(EX_V, EX)
order = []
while Q:
    x = min(Q, key=lambda z: (Q[z], EX_V.index(z)))
    k = Q.pop(x)
    note = []
    for y, w in out[x]:
        if dist[x] + w < dist[y]:
            old = dist[y]
            dist[y] = dist[x] + w
            note.append((y, old, dist[y], "dec" if y in Q else "ins"))
            Q[y] = dist[y]
    order.append((x, k, note, dict(Q)))
expected = [
    ("s", 0, [("a", INF, 1, "ins"), ("u", INF, 7, "ins")], {"a": 1, "u": 7}),
    ("a", 1, [("b", INF, 3, "ins"), ("t", INF, 7, "ins")], {"u": 7, "b": 3, "t": 7}),
    ("b", 3, [("t", 7, 6, "dec")], {"u": 7, "t": 6}),
    ("t", 6, [], {"u": 7}),
    ("u", 7, [("v", INF, 2, "ins")], {"v": 2}),
    ("v", 2, [("b", 3, 2, "ins")], {"b": 2}),
    ("b", 2, [("t", 6, 5, "ins")], {"t": 5}),
    ("t", 5, [], {}),
]
check("example: the page's run table (relaxations, Insert vs DecreaseKey, queue after each step)", order == expected,
      order)
check("example: a is not lowered by t->a (6 + 2 > 1, 5 + 2 > 1)", 6 + 2 > 1 and 5 + 2 > 1)

# ---- the walk that uses u->v twice contains a closed walk through u->v, of weight >= 0
okc = True
for trial in range(2000):
    n = random.randint(2, 6)
    V, E, neg = random_one_negative(n, 0.6)
    u, v = neg
    back = bellman_ford(V, {e: w for e, w in E.items() if e != neg}, v)
    if back is not None and back[u] < INF:
        okc &= back[u] + E[neg] >= 0              # every cycle through u->v: u->v then a path v ~> u in G+
check("no negative cycle <=> d_v(u) + w(u->v) >= 0 (every cycle through u->v is u->v plus a v-u path in G+)", okc)

# =============================================================================================== Problem 2
print("== Problem 2: where to meet")


def p2_page(V, E, p, q, directed=False):
    """Page: Dijkstra from p and from q (an undirected road = two directed edges); T(t) = max{d_p(t), d_q(t)};
    return (min T, set of minimizers)."""
    D = dict(E)
    if not directed:
        for (a, b), w in E.items():
            D[(b, a)] = w
    dp, _ = dijkstra(V, D, p)
    dq, _ = dijkstra(V, D, q)
    T = {t: max(dp[t], dq[t]) for t in V}
    best = min(T.values())
    return best, {t for t in V if T[t] == best}, dp, dq


def p2_brute(V, E, p, q, directed=False):
    D = dict(E)
    if not directed:
        for (a, b), w in E.items():
            D[(b, a)] = w
    bp = simple_path_min(V, D, p)
    bq = simple_path_min(V, D, q)
    T = {t: max(bp[t], bq[t]) for t in V}
    best = min(T.values())
    return best, {t for t in V if T[t] == best}, bp, bq


okp, cnt2, sum_wrong, nodes_wrong, lb_ok, unreach = True, 0, 0, 0, True, 0
for trial in range(4000):
    n = random.randint(1, 8)
    V = list(range(n))
    directed = trial % 4 == 3
    E = {}
    for a in V:
        for b in V:
            if a != b and (directed or a < b) and random.random() < random.choice([0.2, 0.4, 0.7]):
                E[(a, b)] = random.randint(0, 9)
    p, q = random.choice(V), random.choice(V)
    pg = p2_page(V, E, p, q, directed)
    br = p2_brute(V, E, p, q, directed)
    okp &= pg[0] == br[0] and pg[1] == br[1]
    cnt2 += 1
    if pg[0] == INF:
        unreach += 1
        continue
    dp, dq = pg[2], pg[3]
    # minimizing the sum can choose a city with a later meeting
    S = {t: dp[t] + dq[t] for t in V}
    smin = min(S.values())
    if any(S[t] == smin and max(dp[t], dq[t]) > pg[0] for t in V):
        sum_wrong += 1
    if not directed:
        lb_ok &= all(2 * max(dp[t], dq[t]) >= dp[q] for t in V)     # triangle inequality: T(t) >= d(p,q)/2
        # best city off every shortest p-q path?
        if all(dp[t] + dq[t] > dp[q] for t in pg[1]):
            nodes_wrong += 1
check("random graphs: two Dijkstra runs + scan == exhaustive simple-path search (value and the set of best cities); "
      "undirected, and directed (one-way roads) in a quarter of the cases", okp,
      f"{cnt2} instances, {unreach} with no common reachable city")
check("trap: minimizing d(p,t) + d(q,t) can pick a city with a later meeting", sum_wrong > 0,
      f"{sum_wrong} random instances")
check("trap: the best city can lie off every shortest p-q path", nodes_wrong > 0, f"{nodes_wrong} random instances")
check("undirected: every meeting time is >= d(p,q)/2", lb_ok)
# the page's examples
V2 = ["p", "a", "q", "c"]
E2 = {("p", "a"): 1, ("a", "q"): 9, ("p", "c"): 6, ("q", "c"): 6}
best, arg, dp, dq = p2_page(V2, E2, "p", "q")
T2 = {t: max(dp[t], dq[t]) for t in V2}
check("trap example: meeting times p 10, a 9, q 10, c 6; best city c; d(p,q) = 10 along p a q, c is on no shortest "
      "p-q path (6 + 6 = 12 > 10)", T2 == dict(p=10, a=9, q=10, c=6) and arg == {"c"} and dp["q"] == 10 and
      dp["c"] + dq["c"] == 12, T2)
V3 = ["p", "a", "q"]
E3 = {("p", "a"): 1, ("a", "q"): 1}
b3, a3, dp3, dq3 = p2_page(V3, E3, "p", "q")
check("sum trap (Ex 8.14's example): on p - a - q with two roads of length 1 the sum is 2 everywhere, but only a "
      "gives meeting time 1", all(dp3[t] + dq3[t] == 2 for t in V3) and a3 == {"a"} and b3 == 1)
check("mid-road remark: one road p-q of length 2: best city time 2, halfway point time 1",
      p2_page(["p", "q"], {("p", "q"): 2}, "p", "q")[0] == 2 and max(1, 2 - 1) == 1)

# =============================================================================================== Problem 3
print("== Problem 3: looped trees")


def random_binary_tree(n):
    """Random binary tree on nodes 0..n-1 (0 = root): attach each new node to a random node with a free child slot."""
    kids = {0: []}
    par = {0: None}
    for x in range(1, n):
        cand = [y for y in kids if len(kids[y]) < 2]
        y = random.choice(cand)
        kids[y].append(x)
        kids[x] = []
        par[x] = y
    return kids, par


def looped_tree(kids, wmax=9, zero_bias=0.2):
    W = {}
    for x, cs in kids.items():
        for c in cs:
            W[(x, c)] = 0 if random.random() < zero_bias else random.randint(0, wmax)
    for x, cs in kids.items():
        if not cs:
            W[(x, 0)] = 0 if random.random() < zero_bias else random.randint(0, wmax)   # leaf -> root (root 0)
    return W


def dag_sssp(order, E, src):
    """DagSSSP: relax the out-edges of every vertex in topological order."""
    out = {x: [] for x in order}
    for (a, b), w in E.items():
        out[a].append((b, w))
    d = {x: INF for x in order}
    d[src] = 0
    ops = 0
    for x in order:
        if d[x] < INF:
            for y, w in out[x]:
                ops += 1
                if d[x] + w < d[y]:
                    d[y] = d[x] + w
    return d, ops


def split_root(kids, W, root=0):
    """Page, (b): H = the looped tree with the root split into r_out (edges to its children) and r_in (loop edges).
    A topological order: preorder of the tree (r_out first), then r_in."""
    H = {}
    for (a, b), w in W.items():
        a2 = "r_out" if a == root else a
        b2 = "r_in" if b == root else b                   # every edge into the root is a loop edge
        H[(a2, b2)] = w
    pre = []

    def go(x):
        pre.append("r_out" if x == root else x)
        for c in kids[x]:
            go(c)
    go(root)
    return H, pre + ["r_in"]


def p3_dag(kids, W, u, v, root=0):
    """Page, (b): if u = v return 0; u' = r_out if u is the root, v' = r_in if v is the root;
    delta(u, v) = min{dist_H(u', v'), dist_H(u', r_in) + dist_H(r_out, v')} by two DagSSSP runs."""
    if u == v:
        return 0, 0
    H, order = split_root(kids, W, root)
    u2 = "r_out" if u == root else u
    v2 = "r_in" if v == root else v
    du, o1 = dag_sssp(order, H, u2)
    dr, o2 = dag_sssp(order, H, "r_out")
    return min(du[v2], du["r_in"] + dr[v2]), o1 + o2


def D_L(kids, W, root=0):
    D = {root: 0}
    stack = [root]
    while stack:
        x = stack.pop()
        for c in kids[x]:
            D[c] = D[x] + W[(x, c)]
            stack.append(c)
    L = {}

    def post(x):
        if not kids[x]:
            L[x] = W[(x, root)]
        else:
            for c in kids[x]:
                post(c)
            L[x] = min(W[(x, c)] + L[c] for c in kids[x])
    post(root)
    return D, L


def ancestor(par, u, v):
    """Is u an ancestor of v (u = v included)?"""
    x = v
    while x is not None:
        if x == u:
            return True
        x = par[x]
    return False


def p3_closed(kids, par, W, u, v, root=0):
    """Page, closed form: D(v) - D(u) if u is an ancestor of v (u = v included), else L(u) + D(v)."""
    D, L = D_L(kids, W, root)
    return D[v] - D[u] if ancestor(par, u, v) else L[u] + D[v]


def p3_one_query(kids, par, W, u, v, root=0):
    """Page, the direct O(n) procedure: walk up from v summing weights; if u is met, that sum is the answer; otherwise
    the sum is D(v), and L(u) comes from one postorder traversal of the subtree of u.  Returns (answer, steps)."""
    steps = 0
    x, acc = v, 0
    while x != u and par[x] is not None:
        acc += W[(par[x], x)]
        x = par[x]
        steps += 1
    if x == u:
        return acc, steps
    Dv = acc

    def Lsub(y):
        nonlocal steps
        steps += 1
        if not kids[y]:
            return W[(y, root)]
        return min(W[(y, c)] + Lsub(c) for c in kids[y])
    return Lsub(u) + Dv, steps


okA = okB = okC = okE = okDag = okSC = True
pairs = 0
cases = dict(desc=0, notdesc=0, same=0, to_root=0, from_root=0)
for trial in range(1500):
    n = random.randint(1, 12)
    kids, par = random_binary_tree(n)
    W = looped_tree(kids)
    V = list(range(n))
    leaves = sum(1 for x in V if not kids[x])
    okE &= leaves <= (n + 1) / 2 and len(W) == n - 1 + leaves and len(W) <= (3 * n - 1) / 2
    FW = floyd(V, W)
    okSC &= all(FW[(a, b)] < INF for a in V for b in V)
    H, order = split_root(kids, W)
    pos = {x: i for i, x in enumerate(order)}
    okDag &= all(pos[a] < pos[b] for (a, b) in H) and len(H) == len(W)
    for u in V:
        for v in V:
            pairs += 1
            truth = FW[(u, v)]
            okA &= p3_dag(kids, W, u, v)[0] == truth
            okB &= p3_closed(kids, par, W, u, v) == truth
            okC &= p3_one_query(kids, par, W, u, v)[0] == truth
            if u == v:
                cases["same"] += 1
            elif ancestor(par, u, v):
                cases["desc"] += 1
            else:
                cases["notdesc"] += 1
            cases["to_root"] += (v == 0 and u != 0)
            cases["from_root"] += (u == 0 and v != 0)
check("random looped trees, n = 1..12: the split-root dag + two DagSSSP runs == Floyd-Warshall for every pair",
      okA, f"{pairs} pairs: {cases}")
check("random looped trees: closed form D(v) - D(u) (u ancestor of v) / L(u) + D(v) == Floyd-Warshall", okB)
check("random looped trees: the one-query procedure (walk up from v, postorder of the subtree of u) == Floyd-Warshall",
      okC)
check("leaves <= (n+1)/2 and E = n - 1 + leaves <= (3n-1)/2", okE)

def p3_preprocess(kids, W, root=0):
    """Page: D, L and pre-/postorder numbers for all nodes, in O(n); then O(1) per query."""
    D, L = D_L(kids, W, root)
    pre, post = {}, {}
    cnt = [0, 0]

    def go(x):
        pre[x] = cnt[0]
        cnt[0] += 1
        for c in kids[x]:
            go(c)
        post[x] = cnt[1]
        cnt[1] += 1
    go(root)

    def query(u, v):
        anc = pre[u] <= pre[v] and post[v] <= post[u]       # u = v or ancestor, as page
        return D[v] - D[u] if anc else L[u] + D[v]
    return query


okP = True
for trial in range(600):
    n = random.randint(1, 14)
    kids, par = random_binary_tree(n)
    W = looped_tree(kids)
    FW = floyd(list(range(n)), W)
    q = p3_preprocess(kids, W)
    okP &= all(q(u, v) == FW[(u, v)] for u in range(n) for v in range(n))
check("O(1) queries after O(n) preprocessing (D, L, and 'u = v or u is an ancestor of v' as pre(u) <= pre(v) and "
      "post(u) >= post(v)) == Floyd-Warshall", okP)
check("H is a dag: preorder (r_out first) then r_in is a topological order; H has as many edges as G", okDag)
check("a looped tree is strongly connected (every distance finite)", okSC)
# full binary trees attain the edge bound
kids_full, _ = random_binary_tree(1)
kids_full = {0: [1, 2], 1: [3, 4], 2: [5, 6], 3: [], 4: [], 5: [], 6: []}
Wf = looped_tree(kids_full)
check("a full binary tree attains E = (3n-1)/2 (n = 7: 10 edges)", len(Wf) == (3 * 7 - 1) / 2)

# single-cycle looped trees (one leaf): any vertex can serve as the root
okcyc = True
for n in range(1, 8):
    w = [random.randint(0, 9) for _ in range(n)]
    Ec = {(i, (i + 1) % n): w[i] for i in range(n)} if n > 1 else {(0, 0): w[0]}
    FW = floyd(list(range(n)), {e: x for e, x in Ec.items() if e[0] != e[1]})
    for r in range(n):
        # relabel so that r becomes 0: node j -> (j - r) mod n; tree is the path 0 -> 1 -> ... -> n-1, loop n-1 -> 0
        kids = {j: ([j + 1] if j + 1 < n else []) for j in range(n)}
        par = {j: (j - 1 if j > 0 else None) for j in range(n)}
        W = {(j, j + 1): w[(j + r) % n] for j in range(n - 1)}
        W[(n - 1, 0)] = w[(n - 1 + r) % n]
        for a in range(n):
            for b in range(n):
                okcyc &= p3_closed(kids, par, W, a, b) == FW[((a + r) % n, (b + r) % n)]
check("one leaf: the looped tree is a single cycle, and the formula is right with any vertex as the root", okcyc)
# the root is the only vertex of in-degree >= 2 when there are >= 2 leaves
okroot = True
for trial in range(300):
    n = random.randint(3, 15)
    kids, par = random_binary_tree(n)
    W = looped_tree(kids)
    indeg = {x: 0 for x in range(n)}
    for (a, b) in W:
        indeg[b] += 1
    leaves = sum(1 for x in range(n) if not kids[x])
    if leaves >= 2:
        okroot &= [x for x in range(n) if indeg[x] != 1] == [0] and indeg[0] == leaves
    else:
        okroot &= all(d == 1 for d in indeg.values())
check("given only the graph: with >= 2 leaves the root is the unique vertex of in-degree != 1 (in-degree = number of "
      "leaves); with one leaf every in-degree is 1", okroot)

# the handout's tree (same as the book's; names as on the Chapter 8 exercises page)
TREE = [("r", "a", 5), ("r", "b", 8), ("a", "c", 17), ("a", "d", 0), ("c", "e", 23), ("b", "f", 1), ("f", "g", 9),
        ("f", "h", 14)]
LOOP = {"e": 4, "d": 16, "g": 7, "h": 42}
names = ["r", "a", "b", "c", "d", "e", "f", "g", "h"]
kidsH = {x: [] for x in names}
parH = {"r": None}
WH = {}
for a, b, w in TREE:
    kidsH[a].append(b)
    parH[b] = a
    WH[(a, b)] = w
for l, w in LOOP.items():
    WH[(l, "r")] = w
D, L = D_L(kidsH, WH, "r")
check("handout tree: D = r 0, a 5, b 8, c 22, d 5, e 45, f 9, g 18, h 23",
      D == dict(r=0, a=5, b=8, c=22, d=5, e=45, f=9, g=18, h=23), D)
check("handout tree: L = r 21, a 16, b 17, c 27, d 16, e 4, f 16, g 7, h 42",
      L == dict(r=21, a=16, b=17, c=27, d=16, e=4, f=16, g=7, h=42), L)
FWH = floyd(names, WH)
check("handout tree: delta(b, d) = L(b) + D(d) = 17 + 5 = 22 along b f g r a d (1 + 9 + 7 + 5 + 0)",
      FWH[("b", "d")] == 22 == L["b"] + D["d"] == walk_length(WH, ["b", "f", "g", "r", "a", "d"]))
check("handout tree: the other way out of b, through h, costs 1 + 14 + 42 = 57 to the root (62 to d)",
      walk_length(WH, ["b", "f", "h", "r"]) == 57 and walk_length(WH, ["b", "f", "h", "r", "a", "d"]) == 62)
check("handout tree: no way up -- delta(c, d) = L(c) + D(d) = 27 + 5 = 32 along c e r a d, not 17 + 0 through a",
      FWH[("c", "d")] == 32 == L["c"] + D["d"] == walk_length(WH, ["c", "e", "r", "a", "d"]))
check("handout tree: Exercise 8.1's numbers delta(a,h) = 39, delta(c,a) = 32, delta(a,e) = 40 (tree path; via the "
      "root 16 + 45 = 61)", (FWH[("a", "h")], FWH[("c", "a")], FWH[("a", "e")]) == (39, 32, 40) and L["a"] + D["e"]
      == 61)
check("handout tree: delta(r, v) = D(v) and delta(u, r) = L(u) for all u != r",
      all(FWH[("r", x)] == D[x] for x in names) and all(FWH[(x, "r")] == L[x] for x in names if x != "r"))
check("handout tree: n = 9, 4 leaves, 12 edges <= (3*9-1)/2 = 13", len(WH) == 12 and len(LOOP) == 4)
okall = all(p3_closed(kidsH, parH, WH, a, b, "r") == FWH[(a, b)] for a in names for b in names)
check("handout tree: closed form right for all 81 pairs", okall)
check("handout tree: the case u = v must go to D(v) - D(u) = 0 -- L(u) + D(u) > 0 for every u (strict 'ancestor' "
      "would be wrong on the diagonal)", all(FWH[(x, x)] == 0 < L[x] + D[x] for x in names))

# work of the one-query procedure and of the DagSSSP version on growing trees; Dijkstra's heap work for comparison
rows = []
okw = True
for n in (1000, 4000, 16000):
    kids, par = random_binary_tree(n)
    W = looped_tree(kids, wmax=100)
    worst = 0
    for _ in range(30):
        u, v = random.randrange(n), random.randrange(n)
        a1, st = p3_one_query(kids, par, W, u, v)
        worst = max(worst, st)
    a2, ops = p3_dag(kids, W, 1 % n, 0)
    okw &= worst <= n and ops <= 2 * len(W)
    _, _, _, dops = book_dijkstra(list(range(n)), W, 0)
    rows.append(f"n={n}: one-query steps <= {worst} (<= n), DagSSSP edge scans {ops} (<= 2E = {2 * len(W)}), "
                f"Dijkstra heap ops {dops['insert'] + dops['decrease'] + dops['extract']}")
check("growing looped trees: the one-query procedure takes <= n steps, the two DagSSSP runs <= 2E edge scans", okw,
      "; ".join(rows))
# Dijkstra on a looped tree: every vertex once (non-negative weights), E = O(n)
kids, par = random_binary_tree(500)
W = looped_tree(kids)
dd, _, logd, opsd = book_dijkstra(list(range(500)), W, 0)
check("(a) Dijkstra on a looped tree: each vertex extracted once, at most E relaxations",
      opsd["extract"] == 500 and opsd["relax"] <= len(W))

# adversary for the single-query lower bound: tree weights 0, loops 1 -> L(u) = 1; any one loop set to 0 -> L(u) = 0
okadv = True
for trial in range(200):
    n = random.randint(2, 15)
    kids, par = random_binary_tree(n)
    W = {(a, b): (1 if b == 0 else 0) for (a, b) in looped_tree(kids)}
    u = random.randrange(n)
    Dd, Ll = D_L(kids, W)
    sub_leaves = [x for x in range(n) if not kids[x] and ancestor(par, u, x)]
    okadv &= Ll[u] == 1
    for l in sub_leaves:
        W2 = dict(W)
        W2[(l, 0)] = 0
        okadv &= D_L(kids, W2)[1][u] == 0
check("lower-bound remark: with tree edges 0 and loop edges 1, L(u) = 1, and setting any one loop edge below u to 0 "
      "makes L(u) = 0", okadv)

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: {FAIL}")
