#!/usr/bin/env python3
"""Checks for content/3-homework-and-exams/lab-12a.md (Lab 12a, CS/ECE 374 A Fall 2026; no official solutions).

Every "magic box" is replaced by a brute-force decision procedure that counts its calls and refuses inputs outside
its specification (a non-positive L for the path box, a non-graph for the others).  Every algorithm is implemented
exactly as the page states it and compared with exhaustive search.

Problem 1 (longest path from a decision box).  All directed graphs on up to 4 vertices and random ones on 5-7:
  (a) the scan L = 1 .. V-1 and the binary search against the longest simple path found by exhaustive search; the box
      is monotone in L; call counts.
  (b) the edge-deletion algorithm, in several edge orders: what remains is one simple path of the optimal length,
      made of edges of G; V - 1 + E calls at most; every surviving edge lies on every longest path of what remains;
      the two traps (deleting an edge whenever some longest path avoids it "in G" without updating G; testing with
      L* + 1) are shown to fail.
Problem 2 (maximum independent set from a decision box).  All undirected graphs on up to 6 vertices, random on 7-9:
  (a) the scan and the binary search against exhaustive search; "exactly k" and "at least k" agree; monotone.
  (b) the vertex-deletion algorithm in several orders: what remains is an independent set of maximum size; the
      take-or-discard variant (delete the closed neighborhood, lower k); call counts; the trap (keeping every vertex
      that lies in SOME maximum independent set) fails on a single edge.
Problem 3 (optimal coloring from a decision box that takes only a graph and k).  All graphs on up to 5 vertices,
      random on 6-8: the chromatic number by scanning k; the edge-adding algorithm: the final graph is complete
      multipartite with exactly chi(G) parts, non-adjacency is an equivalence relation in it, and the classes are a
      proper coloring of G with chi(G) colors; call counts; the page's 5-cycle example; the merging variant.
Problem 4 (a satisfying input from a CircuitSat box).  Every boolean function of 1, 2 and 3 inputs (as a circuit of
      And/Or/Not gates) and random circuits on 4-6 inputs: the algorithm that Ands one literal at a time onto the
      output returns a satisfying input exactly when one exists, with n + 1 calls, every circuit handed to the box has
      the same n inputs and one output, and the output is the lexicographically largest satisfying input (True first);
      the same search with a box for Sat and unit clauses.
Every example number on the page is recomputed here."""
import itertools
import math
import random

random.seed(11112026)
FAIL = []


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail != "" else ""))
    if not cond:
        FAIL.append(name)


# ============================================================================ Problem 1: longest path
def longest_path_brute(n, edges):
    """Number of edges of a longest simple directed path (0 if n >= 1), by exhaustive search, and one such path."""
    adj = [[] for _ in range(n)]
    for (a, b) in edges:
        adj[a].append(b)
    best = [0, [0] if n else []]

    def dfs(v, seen, path):
        if len(path) - 1 > best[0]:
            best[0], best[1] = len(path) - 1, path[:]
        for w in adj[v]:
            if w not in seen:
                seen.add(w); path.append(w)
                dfs(w, seen, path)
                path.pop(); seen.discard(w)

    for s in range(n):
        dfs(s, {s}, [s])
    return best[0], best[1]


class PathBox:
    """The handout's box: a directed graph and a POSITIVE integer L; True iff some simple path has length >= L."""

    def __init__(self):
        self.calls = 0

    def __call__(self, n, edges, L):
        assert isinstance(L, int) and L >= 1, "the box takes a positive integer"
        self.calls += 1
        return longest_path_brute(n, edges)[0] >= L


def longest_length_scan(box, n, edges):
    """Page, 1(a): ell <- 0; for L <- 1 to V-1: if Box(G, L) then ell <- L else stop."""
    ell = 0
    for L in range(1, n):
        if box(n, edges, L):
            ell = L
        else:
            break
    return ell


def longest_length_binary(box, n, edges):
    """Page, 1(a) variant: binary search for the largest L in 0 .. V-1 with Box(G, L) (L = 0 is always True)."""
    lo, hi = 0, max(n - 1, 0)          # invariant: answer in lo .. hi, Box(lo) true (lo = 0: trivially)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if box(n, edges, mid):
            lo = mid
        else:
            hi = mid - 1
    return lo


def longest_path_search(box, n, edges, order=None):
    """Page, 1(b): L* <- LongestLength(G); for every edge e of G: if Box(G - e, L*) then G <- G - e.
    Returns (L*, remaining edges)."""
    Lstar = longest_length_scan(box, n, edges)
    cur = list(edges)
    if Lstar == 0:
        return 0, []
    for e in (order if order is not None else list(edges)):
        trial = [f for f in cur if f != e]
        if box(n, trial, Lstar):
            cur = trial
    return Lstar, cur


def is_simple_path(n, edges, length):
    """The edge set is exactly one simple directed path with `length` edges; returns its vertex sequence or None."""
    if len(edges) != length or len(set(edges)) != length:
        return None
    if length == 0:
        return []
    out, inn = {}, {}
    for (a, b) in edges:
        if a in out or b in inn or a == b:
            return None
        out[a] = b; inn[b] = a
    starts = [a for a in out if a not in inn]
    if len(starts) != 1:
        return None
    seq = [starts[0]]
    while seq[-1] in out:
        seq.append(out[seq[-1]])
        if len(seq) > length + 1:
            return None
    return seq if len(seq) == length + 1 and len(set(seq)) == length + 1 else None


def all_digraphs(n):
    pairs = [(a, b) for a in range(n) for b in range(n) if a != b]
    for mask in range(1 << len(pairs)):
        yield [p for i, p in enumerate(pairs) if mask >> i & 1]


def random_digraph(n, p):
    return [(a, b) for a in range(n) for b in range(n) if a != b and random.random() < p]


ok_scan = ok_bin = ok_mono = ok_calls_a = True
ok_search = ok_calls_b = ok_every = True
cnt = 0
worst_scan = worst_bin = 0
graphs1 = [(n, g) for n in range(1, 5) for g in all_digraphs(n)]
for n in (5, 6, 7):
    for _ in range(140 if n < 7 else 60):
        graphs1.append((n, random_digraph(n, random.choice([0.15, 0.3, 0.5]))))
for n, g in graphs1:
    cnt += 1
    truth = longest_path_brute(n, g)[0]
    b = PathBox()
    ok_scan &= longest_length_scan(b, n, g) == truth
    ok_calls_a &= b.calls <= max(n - 1, 0)
    worst_scan = max(worst_scan, b.calls)
    b2 = PathBox()
    ok_bin &= longest_length_binary(b2, n, g) == truth
    ok_calls_a &= b2.calls <= math.ceil(math.log2(n)) if n > 1 else b2.calls == 0
    worst_bin = max(worst_bin, b2.calls)
    bm = PathBox()
    ans = [bm(n, g, L) for L in range(1, n + 2)]
    ok_mono &= all(ans[i] or not ans[i + 1] for i in range(len(ans) - 1)) and not ans[-1] and (n < 2 or not ans[n - 1])
    orders = [list(g), list(reversed(g))] + [random.sample(g, len(g)) for _ in range(2)]
    for od in orders if (n <= 3 or cnt % 7 == 0 or n >= 5) else orders[:1]:
        b3 = PathBox()
        Ls, rest = longest_path_search(b3, n, g, od)
        seq = is_simple_path(n, rest, Ls)
        ok_search &= Ls == truth and seq is not None and set(rest) <= set(g)
        ok_calls_b &= b3.calls <= max(n - 1, 0) + len(g)
        if Ls > 0 and seq is not None:
            # every surviving edge is on every longest path of what remains (here: the remaining graph IS the path)
            ok_every &= longest_path_brute(n, rest)[0] == Ls and all(
                longest_path_brute(n, [f for f in rest if f != e])[0] < Ls for e in rest)
check(f"1(a) the scan L = 1 .. V-1 returns the length of the longest simple path ({cnt} directed graphs: all on <= 4 "
      "vertices, random on 5-7)", ok_scan)
check("1(a) binary search over L returns the same length", ok_bin)
check("1(a) the box is monotone: True for L implies True for L-1; it is always False for L = V", ok_mono)
check("1(a) call counts: the scan makes at most V-1 calls, binary search at most ceil(log2 V)", ok_calls_a,
      f"max scan calls {worst_scan}, max binary calls {worst_bin}")
check("1(b) after the edge deletions, exactly one simple path of length L* remains, made of edges of G (several "
      "edge orders)", ok_search)
check("1(b) call count at most (V-1) + E", ok_calls_b)
check("1(b) in what remains, deleting any edge destroys every path of length L*", ok_every)

# page example for 1: a 5-vertex graph with a cycle
EX1 = [(0, 1), (1, 2), (2, 0), (2, 3), (3, 4), (1, 3)]         # a->b, b->c, c->a, c->d, d->e, b->d
t1, p1 = longest_path_brute(5, EX1)
b = PathBox()
L1, rest1 = longest_path_search(b, 5, EX1)
names = "abcde"
kept1 = [names[x] + names[y] for x, y in rest1]
gone1 = [names[x] + names[y] for x, y in EX1 if (x, y) not in rest1]
check("1 example (a->b, b->c, c->a, c->d, d->e, b->d): the longest path has 4 edges; there are exactly two such "
      "paths, a->b->c->d->e and c->a->b->d->e", t1 == 4 and L1 == 4 and sorted(
          "".join(names[v] for v in p) for p in itertools.permutations(range(5))
          if all((p[i], p[i + 1]) in EX1 for i in range(4))) == ["abcde", "cabde"])
check("1 example, edges tried in the order listed: a->b kept, b->c deleted, c->a kept, c->d deleted, d->e kept, "
      "b->d kept; what remains is the path c->a->b->d->e",
      kept1 == ["ab", "ca", "de", "bd"] and gone1 == ["bc", "cd"] and is_simple_path(5, rest1, 4) == [2, 0, 1, 3, 4],
      (kept1, gone1))
check("1 example: 4 calls for the length (L = 1, 2, 3, 4, all True) and 6 for the edges: 10 calls", b.calls == 10,
      b.calls)
b = PathBox()
_, rest1r = longest_path_search(b, 5, EX1, list(reversed(EX1)))
check("1 example, edges tried in the reverse order: the other longest path a->b->c->d->e remains",
      is_simple_path(5, rest1r, 4) == [0, 1, 2, 3, 4], rest1r)
b = PathBox()
check("1 example: Box(G, 5) is not needed (a path has at most V-1 = 4 edges) and would be False",
      not b(5, EX1, 5))

# trap 1: decide all deletions against the ORIGINAL graph (no update): may delete too much
def search_no_update(n, edges):
    box = PathBox()
    Ls = longest_length_scan(box, n, edges)
    return Ls, [e for e in edges if not box(n, [f for f in edges if f != e], Ls)]
TR = [(0, 1), (0, 2)]                                           # two longest paths of length 1
Ls, rest = search_no_update(3, TR)
check("1 trap: testing every edge against the original G (never deleting) leaves nothing on a->b, a->c "
      "(each edge alone is avoidable)", Ls == 1 and rest == [], rest)
# trap 2: the path box cannot be asked about L = 0
try:
    PathBox()(3, TR, 0)
    raised = False
except AssertionError:
    raised = True
check("1 the box refuses L = 0 (the handout says positive integer); the algorithms above never ask it", raised)

# ============================================================================ Problem 2: independent set
def alpha_brute(n, edges):
    best = 0
    arg = ()
    es = [tuple(e) for e in edges]
    for mask in range(1 << n):
        if all(not (mask >> a & 1 and mask >> b & 1) for a, b in es):
            c = bin(mask).count("1")
            if c > best:
                best, arg = c, tuple(i for i in range(n) if mask >> i & 1)
    return best, arg


class ISBox:
    """An undirected graph (vertex list, edge list) and an integer k; True iff some independent set has size k."""

    def __init__(self):
        self.calls = 0

    def __call__(self, verts, edges, k):
        assert isinstance(k, int)
        self.calls += 1
        if k < 0 or k > len(verts):
            return False
        idx = {v: i for i, v in enumerate(verts)}
        es = [(idx[a], idx[b]) for a, b in edges]
        n = len(verts)
        for mask in range(1 << n):
            if bin(mask).count("1") == k and all(not (mask >> a & 1 and mask >> b & 1) for a, b in es):
                return True
        return False


def induced(verts, edges, keep):
    ks = set(keep)
    return [v for v in verts if v in ks], [(a, b) for a, b in edges if a in ks and b in ks]


def max_is_size_scan(box, verts, edges):
    """Page, 2(a): k <- 0; while k < V and Box(G, k+1): k <- k+1."""
    k = 0
    while k < len(verts) and box(verts, edges, k + 1):
        k += 1
    return k


def max_is_size_binary(box, verts, edges):
    lo, hi = 0, len(verts)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if box(verts, edges, mid):
            lo = mid
        else:
            hi = mid - 1
    return lo


def max_is_delete(box, verts, edges, order=None):
    """Page, 2(b): k* <- MaxSize(G); for every vertex v: if Box(G - v, k*) then G <- G - v.  Return V(G)."""
    kstar = max_is_size_scan(box, verts, edges)
    cv, ce = list(verts), list(edges)
    for v in (order if order is not None else list(verts)):
        tv, te = induced(cv, ce, [u for u in cv if u != v])
        if box(tv, te, kstar):
            cv, ce = tv, te
    return kstar, cv


def max_is_take(box, verts, edges):
    """Page, 2(b) variant: for every remaining vertex v: if Box(G - N[v], k-1): take v, G <- G - N[v], k <- k-1;
    else G <- G - v."""
    k = max_is_size_scan(box, verts, edges)
    kstar = k
    cv, ce = list(verts), list(edges)
    S = []
    for v in list(verts):
        if v not in cv:
            continue
        if k == 0:
            break
        nb = {v} | {b for a, b in ce if a == v} | {a for a, b in ce if b == v}
        tv, te = induced(cv, ce, [u for u in cv if u not in nb])
        if box(tv, te, k - 1):
            S.append(v); cv, ce = tv, te; k -= 1
        else:
            cv, ce = induced(cv, ce, [u for u in cv if u != v])
    return kstar, S


def is_independent(S, edges):
    s = set(S)
    return all(not (a in s and b in s) for a, b in edges)


def all_graphs(n):
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        yield [p for i, p in enumerate(pairs) if mask >> i & 1]


def random_graph(n, p):
    return [(a, b) for a, b in itertools.combinations(range(n), 2) if random.random() < p]


ok_a = ok_ab = ok_mono2 = ok_exact = ok_del = ok_take = ok_calls2 = ok_calls2a = True
cnt = 0
graphs2 = [(n, g) for n in range(0, 6) for g in all_graphs(n)]
graphs2 += [(6, g) for i, g in enumerate(all_graphs(6)) if i % 37 == 0]
for n in (7, 8, 9):
    for _ in range(40):
        graphs2.append((n, random_graph(n, random.choice([0.2, 0.4, 0.6]))))
for n, g in graphs2:
    cnt += 1
    verts = list(range(n))
    a, _ = alpha_brute(n, g)
    b = ISBox()
    ok_a &= max_is_size_scan(b, verts, g) == a
    ok_calls2a &= b.calls <= min(a + 1, n) and b.calls <= n
    b2 = ISBox()
    ok_ab &= max_is_size_binary(b2, verts, g) == a
    ok_calls2a &= b2.calls <= (math.ceil(math.log2(n + 1)) if n else 0)
    bm = ISBox()
    ans = [bm(verts, g, k) for k in range(0, n + 2)]
    ok_mono2 &= ans[0] and not ans[-1] and all(ans[i] or not ans[i + 1] for i in range(len(ans) - 1))
    ok_exact &= all(ans[k] == (a >= k) for k in range(0, n + 2))
    if n <= 4 or cnt % 5 == 0:
        for od in [verts, verts[::-1], random.sample(verts, n)]:
            b3 = ISBox()
            ks, S = max_is_delete(b3, verts, g, od)
            ok_del &= ks == a and len(S) == a and is_independent(S, g)
            ok_calls2 &= b3.calls <= 2 * n
        b4 = ISBox()
        ks, S = max_is_take(b4, verts, g)
        ok_take &= ks == a and len(S) == a and is_independent(S, g) and len(set(S)) == len(S)
        ok_calls2 &= b4.calls <= 2 * n
check(f"2(a) the scan k = 1, 2, ... returns the size of the largest independent set ({cnt} graphs: all on <= 5 "
      "vertices, a sample on 6, random on 7-9)", ok_a)
check("2(a) binary search over k returns the same size", ok_ab)
check("2(a) the box is monotone in k (a subset of an independent set is independent); True for k = 0, False for "
      "k = V + 1", ok_mono2)
check("2(a) 'an independent set of size exactly k' and 'of size at least k' are the same question", ok_exact)
check("2(a) call counts: the scan at most V calls, binary search at most ceil(log2(V+1))", ok_calls2a)
check("2(b) vertex deletion: the surviving vertices are an independent set of maximum size (three vertex orders)",
      ok_del)
check("2(b) variant: take v and delete its closed neighborhood when Box(G - N[v], k-1), else delete v: a maximum "
      "independent set", ok_take)
check("2(b) at most 2V calls in all (V for the size, V for the deletions)", ok_calls2)

# page example for 2: the path a - b - c - d - e plus the edge b - d  (a 'bull'-like graph)
EX2 = [(0, 1), (1, 2), (2, 3), (3, 4), (1, 3)]
a2, _ = alpha_brute(5, EX2)
b = ISBox()
ks, S = max_is_delete(b, list(range(5)), EX2)
check("2 example (edges ab, bc, cd, de, bd): the largest independent set has 3 vertices, and vertex deletion in the "
      "order a..e returns {a, c, e}", a2 == 3 and ks == 3 and S == [0, 2, 4], (a2, S))
check("2 example: 4 calls for the size (k = 1, 2, 3 True, 4 False) and 5 for the deletions",
      b.calls == 9, b.calls)
allmax = [m for m in range(32) if bin(m).count("1") == 3 and is_independent([i for i in range(5) if m >> i & 1], EX2)]
check("2 example: {a, c, e} is the only independent set of size 3", allmax == [0b10101], allmax)
# trap: 'keep v if v is in SOME maximum independent set' keeps both ends of an edge
EDGE = [(0, 1)]
b = ISBox()
kept = []
for v in (0, 1):
    nb = {v} | {y for x, y in EDGE if x == v} | {x for x, y in EDGE if y == v}
    tv, te = induced([0, 1], EDGE, [u for u in (0, 1) if u not in nb])
    if b(tv, te, 1 - 1):
        kept.append(v)
check("2 trap: on a single edge uv, 'v is in some maximum independent set' is True for both u and v, and {u, v} "
      "is not independent: decisions must update the graph", kept == [0, 1] and not is_independent(kept, EDGE))

# ============================================================================ Problem 3: coloring
def chromatic_brute(n, edges):
    """Chromatic number by trying k = 0, 1, 2, ... with backtracking."""
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b); adj[b].add(a)

    def colorable(k):
        col = [-1] * n

        def go(v):
            if v == n:
                return True
            for c in range(min(k, v + 1)):      # symmetry breaking: vertex v uses a color < v+1
                if all(col[u] != c for u in adj[v]):
                    col[v] = c
                    if go(v + 1):
                        return True
                    col[v] = -1
            return False
        return go(0)
    k = 0
    while not colorable(k):
        k += 1
    return k


class ColorBox:
    """An undirected graph and an integer k; True iff the graph has a proper coloring with k colors."""

    def __init__(self):
        self.calls = 0
        self.memo = {}

    def __call__(self, n, edges, k):
        assert isinstance(k, int)
        assert all(isinstance(e, tuple) and len(e) == 2 and e[0] != e[1] for e in edges), "a graph and only a graph"
        self.calls += 1
        key = (n, frozenset(frozenset(e) for e in edges))
        if key not in self.memo:
            self.memo[key] = chromatic_brute(n, edges)
        return k >= self.memo[key]


def optimal_coloring(box, n, edges):
    """Page, 3: k* <- the smallest k in 1 .. V with Box(G, k); for every pair u, v not adjacent in G:
    if Box(G + uv, k*) then G <- G + uv.  Then color: a vertex gets the color of an earlier vertex it is NOT
    adjacent to in the final graph, or a new color if there is none."""
    if n == 0:
        return 0, [], []
    kstar = 1
    while not box(n, edges, kstar):
        kstar += 1
    H = set(frozenset(e) for e in edges)
    for u, v in itertools.combinations(range(n), 2):
        if frozenset((u, v)) in H:
            continue
        trial = H | {frozenset((u, v))}
        if box(n, [tuple(sorted(e)) for e in trial], kstar):
            H = trial
    col = [None] * n
    used = 0
    for v in range(n):
        for u in range(v):
            if frozenset((u, v)) not in H:
                col[v] = col[u]
                break
        else:
            col[v] = used
            used += 1
    return kstar, col, H


def proper(col, edges):
    return all(col[a] != col[b] for a, b in edges)


ok_chi = ok_col = ok_multi = ok_calls3 = ok_equiv = True
cnt = 0
graphs3 = [(n, g) for n in range(0, 6) for g in all_graphs(n)]
for n in (6, 7, 8):
    for _ in range(60 if n < 8 else 25):
        graphs3.append((n, random_graph(n, random.choice([0.2, 0.4, 0.6, 0.8]))))
for n, g in graphs3:
    cnt += 1
    chi = chromatic_brute(n, g)
    b = ColorBox()
    ks, col, H = optimal_coloring(b, n, g)
    ok_chi &= ks == chi
    ok_col &= proper(col, g) and len(set(col)) == chi and (n == 0 or max(col) == chi - 1)
    # the final graph is complete multipartite with exactly chi parts: u ~ v  iff  different colors
    ok_multi &= all((frozenset((u, v)) in H) == (col[u] != col[v]) for u, v in itertools.combinations(range(n), 2))
    # non-adjacency (or equality) in H is an equivalence relation
    non = lambda u, v: u == v or frozenset((u, v)) not in H
    ok_equiv &= all((not (non(u, v) and non(v, w))) or non(u, w) for u in range(n) for v in range(n) for w in range(n))
    ok_calls3 &= b.calls <= n + (n * (n - 1) // 2 - len(g))
check(f"3 the smallest k with Box(G, k) is the chromatic number ({cnt} graphs: all on <= 5 vertices, random on 6-8)",
      ok_chi)
check("3 the classes read off the final graph are a proper coloring of G with exactly chi(G) colors", ok_col)
check("3 the final graph is complete multipartite: two vertices are adjacent in it iff they got different colors",
      ok_multi)
check("3 in the final graph, 'not adjacent' is an equivalence relation", ok_equiv)
check("3 at most V + (V choose 2) - E calls", ok_calls3)
C5 = [(0, 1), (1, 2), (2, 3), (3, 4), (0, 4)]
b = ColorBox()
ks, col, H = optimal_coloring(b, 5, C5)
added = sorted(tuple(sorted(e)) for e in H - set(frozenset(e) for e in C5))
check("3 example, the 5-cycle a b c d e: chromatic number 3 (Box says False for k = 1, 2 and True for 3)",
      ks == 3 and chromatic_brute(5, C5) == 3)
check("3 example: the non-adjacent pairs are tried in the order ac, ad, bd, be, ce; ac and ad are added, bd is "
      "refused, be is added, ce is refused; the classes are {a}, {b, d}, {c, e}",
      added == [(0, 2), (0, 3), (1, 4)] and col == [0, 1, 2, 1, 2], (added, col))
check("3 example: 3 calls for the chromatic number and 5 for the pairs: 8 calls", b.calls == 8, b.calls)
bb = ColorBox()
check("3 example: C5 + ac + ad is 3-colorable; adding bd is refused (not 3-colorable); C5 + ac + ad + be is "
      "3-colorable; adding ce to that is refused",
      bb(5, C5 + [(0, 2), (0, 3)], 3) and not bb(5, C5 + [(0, 2), (0, 3), (1, 3)], 3)
      and bb(5, C5 + [(0, 2), (0, 3), (1, 4)], 3) and not bb(5, C5 + [(0, 2), (0, 3), (1, 4), (2, 4)], 3))
def is_clique(S, edges):
    es = set(frozenset(e) for e in edges)
    return all(frozenset((u, v)) in es for u, v in itertools.combinations(S, 2))
check("3 example: with bd, the vertices a, b, c, d would be pairwise adjacent (a 4-clique); with ce, the vertices "
      "a, c, d, e would be",
      is_clique([0, 1, 2, 3], C5 + [(0, 2), (0, 3), (1, 3)])
      and is_clique([0, 2, 3, 4], C5 + [(0, 2), (0, 3), (1, 4), (2, 4)]))
check("3 example: the final graph is the complete 3-partite graph with parts {a}, {b, d}, {c, e}: 8 edges",
      len(H) == 8 and all((frozenset((u, v)) in H) == (col[u] != col[v])
                          for u, v in itertools.combinations(range(5), 2)))

# ---- the merging variant of Problem 3
def optimal_coloring_merge(box, n, edges):
    """Page, 3 'another way': while some two vertices are not adjacent: if the graph with them merged is still
    k*-colorable, merge them (same color); otherwise add the edge.  The final graph is a clique on k* vertices."""
    if n == 0:
        return 0, []
    kstar = 1
    while not box(n, edges, kstar):
        kstar += 1
    groups = [[v] for v in range(n)]                         # current vertices = groups of original vertices
    E = set(frozenset(e) for e in edges)                     # edges between group indices

    def relabel(gs, es):
        idx = {g: i for i, g in enumerate(sorted(gs))}
        return len(gs), [tuple(sorted((idx[a], idx[b]))) for a, b in (tuple(e) for e in es)]
    alive = set(range(n))
    while True:
        pair = next(((u, v) for u, v in itertools.combinations(sorted(alive), 2) if frozenset((u, v)) not in E), None)
        if pair is None:
            break
        u, v = pair
        merged = set()
        for e in E:
            a, b = tuple(e)
            a2, b2 = (u if a == v else a), (u if b == v else b)
            if a2 != b2:
                merged.add(frozenset((a2, b2)))
        nn, ee = relabel(alive - {v}, merged)
        if box(nn, ee, kstar):
            alive.discard(v)
            groups[u] += groups[v]
            E = merged
        else:
            E.add(frozenset((u, v)))
    col = [None] * n
    for c, g in enumerate(sorted(alive)):
        for x in groups[g]:
            col[x] = c
    return kstar, col


ok_merge = True
for n, g in graphs3[::3]:
    b = ColorBox()
    ks, col = optimal_coloring_merge(b, n, g)
    ok_merge &= ks == chromatic_brute(n, g) and proper(col, g) and len(set(col)) == ks \
        and b.calls <= n + n * (n - 1) // 2
check("3 variant: merge two non-adjacent vertices when the merged graph stays k*-colorable, else add the edge; the "
      "final graph is a clique on chi(G) merged vertices, and the groups are an optimal proper coloring", ok_merge)

# ============================================================================ Problem 4: CircuitSat search
# circuits: ('in', i) | ('not', c) | ('and', c, d) | ('or', c, d)
def ev(c, x):
    t = c[0]
    if t == 'in':
        return x[c[1]]
    if t == 'not':
        return not ev(c[1], x)
    if t == 'and':
        return ev(c[1], x) and ev(c[2], x)
    return ev(c[1], x) or ev(c[2], x)


def inputs_of(c):
    if c[0] == 'in':
        return {c[1]}
    return set().union(*[inputs_of(d) for d in c[1:]])


class CircuitBox:
    """A boolean circuit with n inputs and one output; True iff some input makes the output True."""

    def __init__(self, n):
        self.n = n
        self.calls = 0

    def __call__(self, c):
        assert inputs_of(c) <= set(range(self.n))
        self.calls += 1
        return any(ev(c, x) for x in itertools.product([False, True], repeat=self.n))


def find_input(box, K, n):
    """Page, 4: if not Box(K) return None; for i <- 1 to n: if Box(K and x_i): K <- K and x_i, a_i <- True
    else K <- K and (not x_i), a_i <- False.  Return a."""
    if not box(K):
        return None
    a = []
    for i in range(n):
        K1 = ('and', K, ('in', i))
        if box(K1):
            K = K1; a.append(True)
        else:
            K = ('and', K, ('not', ('in', i))); a.append(False)
    return tuple(a)


def circuit_of_table(n, table):
    """A circuit (Or of minterms) computing the given truth table; the constant False as x0 and not x0."""
    terms = []
    for x in itertools.product([False, True], repeat=n):
        if table[x]:
            lits = [('in', i) if x[i] else ('not', ('in', i)) for i in range(n)]
            t = lits[0]
            for l in lits[1:]:
                t = ('and', t, l)
            terms.append(t)
    if not terms:
        return ('and', ('in', 0), ('not', ('in', 0)))
    c = terms[0]
    for t in terms[1:]:
        c = ('or', c, t)
    return c


def random_circuit(n, size):
    pool = [('in', i) for i in range(n)]
    for _ in range(size):
        r = random.random()
        if r < 0.3:
            pool.append(('not', random.choice(pool)))
        elif r < 0.7:
            pool.append(('and', random.choice(pool), random.choice(pool)))
        else:
            pool.append(('or', random.choice(pool), random.choice(pool)))
    return pool[-1]


ok4 = ok4_calls = ok4_lex = ok4_none = True
cnt = 0
tests4 = []
for n in (1, 2, 3):
    xs = list(itertools.product([False, True], repeat=n))
    for mask in range(1 << len(xs)):
        tests4.append((n, circuit_of_table(n, {x: bool(mask >> i & 1) for i, x in enumerate(xs)})))
for n in (4, 5, 6):
    for _ in range(150):
        c = random_circuit(n, random.randint(3, 14))
        r = random.random()
        if r < 0.3:                          # tightly constrained instances
            c = ('and', c, ('not', random_circuit(n, random.randint(1, 8))))
        elif r < 0.55:                       # unsatisfiable by construction: c and not (c or d)
            c = ('and', c, ('not', ('or', c, random_circuit(n, random.randint(1, 6)))))
        tests4.append((n, c))
nunsat = 0
for n, K in tests4:
    cnt += 1
    box = CircuitBox(n)
    a = find_input(box, K, n)
    sat = [x for x in itertools.product([False, True], repeat=n) if ev(K, x)]
    if not sat:
        nunsat += 1
        ok4_none &= a is None and box.calls == 1
    else:
        ok4 &= a is not None and ev(K, a)
        ok4_calls &= box.calls == n + 1
        ok4_lex &= a == max(sat)             # True first: the lexicographically largest satisfying input
check(f"4 the algorithm returns an input that makes K True whenever one exists ({cnt} circuits: every boolean "
      "function of 1, 2 and 3 inputs, random circuits on 4-6 inputs)", ok4)
check(f"4 it returns None, after one call, exactly when K is unsatisfiable ({nunsat} unsatisfiable circuits)",
      ok4_none and nunsat > 50)
check("4 exactly n + 1 calls on a satisfiable circuit; every circuit handed to the box has the same n inputs", ok4_calls)
check("4 the answer is the lexicographically largest satisfying input (True tried first)", ok4_lex)
# page example: K = (x1 or x2) and not(x1 and x3)
K = ('and', ('or', ('in', 0), ('in', 1)), ('not', ('and', ('in', 0), ('in', 2))))
box = CircuitBox(3)
a = find_input(box, K, 3)
check("4 example K = (x1 or x2) and not(x1 and x3): the answers are True (K), True (K and x1), True (and x2), "
      "False (and x3), and the output is (True, True, False)", a == (True, True, False) and box.calls == 4, a)
check("4 example: K has 4 satisfying inputs out of 8",
      sum(ev(K, x) for x in itertools.product([False, True], repeat=3)) == 4)

# ---- the same search with a box for Sat (CNF formulas): add unit clauses
def cnf_sat(phi, n):
    return any(all(any((x[abs(l) - 1] if l > 0 else not x[abs(l) - 1]) for l in c) for c in phi)
               for x in itertools.product([False, True], repeat=n))


def find_assignment(phi, n):
    calls = 1
    if not cnf_sat(phi, n):
        return None, calls
    a = []
    for i in range(1, n + 1):
        calls += 1
        if cnf_sat(phi + [(i,)], n):
            phi = phi + [(i,)]; a.append(True)
        else:
            phi = phi + [(-i,)]; a.append(False)
    return tuple(a), calls


ok_sat = True
for _ in range(1500):
    n = random.randint(1, 5)
    lits = list(range(1, n + 1)) + [-v for v in range(1, n + 1)]
    phi = [tuple(random.sample(lits, random.randint(1, min(3, 2 * n)))) for _ in range(random.randint(1, 4 * n))]
    a, calls = find_assignment(phi, n)
    sat = cnf_sat(phi, n)
    ok_sat &= (a is None) == (not sat) and (a is None or (
        all(any((a[abs(l) - 1] if l > 0 else not a[abs(l) - 1]) for l in c) for c in phi) and calls == n + 1))
check("4 remark: with a box for Sat, adding the unit clause (x_i) or (not x_i) in each round finds a satisfying "
      "assignment of a CNF formula with n + 1 calls (1500 random formulas)", ok_sat)

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: {FAIL}")
