#!/usr/bin/env python3
"""Checks for content/4-lecture-notes/e-matroids.md (Erickson, Extended Dance Remix E, "Matroids") and the concept
page content/concepts/matroids.md.

1. The three axioms (non-emptiness, heredity, exchange) are checked exhaustively on every example of the note on
   small ground sets: uniform, graphic (all graphs on 4 vertices, random ones on 5), cographic (the note's definition
   and the corrected one), linear (random rational matrices), matching and edge-disjoint-path matroids (random
   graphs), and the scheduling matroid of realistic task sets (every deadline vector for n <= 4, random n = 5, 6).
   Bases, ranks and circuits are compared with the descriptions in the note.
2. GreedyBasis, as printed, is compared with brute force (max-weight basis and max-weight independent set) on random
   weights for every example; the stronger "greedy dominates every basis rank by rank" fact used in the proof of
   Theorem E.1 is checked too.
3. Theorem E.2 is checked on every hereditary family over 3 and 4 elements: greedy is optimal for all weights
   exactly for the matroids, and for every non-matroid the proof's weights (m + 2 on Y, m + 1 on X \\ Y, 0 elsewhere)
   make greedy return m(m + 2) < (m + 1)^2 <= w(X), for every tie-breaking order.
4. The non-matroid examples (class scheduling, matchings as edge sets) and the "two classes" remark.
5. Section E.2: Lemma E.3 against brute force over schedules, Lemma E.4's proof construction (t*, j, Z) and its
   inequality, Realistic? as printed and corrected, GreedySchedule as printed (increasing order) and corrected,
   compared with the brute-force optimum over all permutations; the page's worked example.
6. The concept page's linear-matroid example.
"""
import itertools
import os
import random
import re
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
PAGE = os.path.join(ROOT, "content", "4-lecture-notes", "e-matroids.md")
CONCEPT = os.path.join(ROOT, "content", "concepts", "matroids.md")
FAIL = []
random.seed(374005)


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAIL.append(name)


def subsets(xs):
    xs = list(xs)
    for k in range(len(xs) + 1):
        for c in itertools.combinations(xs, k):
            yield frozenset(c)


# ============================================================================ generic matroid machinery
def axioms(S, I):
    """Return (nonempty, hereditary, exchange_ok, witness) for a family I of frozensets over ground set S."""
    I = set(I)
    ne = frozenset() in I
    her = all((X - {x}) in I for X in I for x in X)
    by = {}
    for X in I:
        by.setdefault(len(X), []).append(X)
    wit = None
    # exchange for |X| = |Y| + 1 suffices given heredity (take any (|Y|+1)-subset of X)
    for k in by:
        for Y in by[k]:
            for X in by.get(k + 1, []):
                if not any((Y | {x}) in I for x in X - Y):
                    wit = (X, Y)
                    break
            if wit:
                break
        if wit:
            break
    return ne, her, wit is None, wit


def is_matroid(S, I):
    ne, her, ex, _ = axioms(S, I)
    return ne and her and ex


def bases(I):
    I = set(I)
    return [X for X in I if not any(len(Y) > len(X) and X < Y for Y in I)]


def circuits(S, I):
    I = set(I)
    return [C for C in subsets(S) if C not in I and all((C - {x}) in I for x in C)]


def greedy_basis(order, I):
    """GreedyBasis: scan in the given order (already sorted by decreasing weight), keep x if G + x is independent."""
    G = frozenset()
    for x in order:
        if (G | {x}) in I:
            G = G | {x}
    return G


def sorted_order(S, w, rng=None):
    xs = list(S)
    if rng:
        rng.shuffle(xs)  # random tie-breaking
    return sorted(xs, key=lambda x: -w[x])


def W(X, w):
    return sum(w[x] for x in X)


def greedy_vs_brute(S, I, trials, name, real=False):
    I = set(I)
    B = bases(I)
    ok_basis = ok_ind = ok_dom = True
    for _ in range(trials):
        if real:
            w = {x: random.randint(-6, 6) for x in S}
        else:
            w = {x: random.randint(0, 6) for x in S}
        G = greedy_basis(sorted_order(S, w, random), I)
        best_basis = max(W(X, w) for X in B)
        if G not in B or W(G, w) != best_basis:
            ok_basis = False
        if not real:
            if W(G, w) != max(W(X, w) for X in I):
                ok_ind = False
        gs = sorted((w[x] for x in G), reverse=True)
        for H in B:
            hs = sorted((w[x] for x in H), reverse=True)
            if any(g < h for g, h in zip(gs, hs)):
                ok_dom = False
    check(f"Theorem E.1: GreedyBasis returns a maximum-weight basis — {name}", ok_basis)
    if not real:
        check(f"  ... which is also a maximum-weight independent set (non-negative weights) — {name}", ok_ind)
    check(f"  ... and dominates every basis rank by rank (the proof's first-difference step) — {name}", ok_dom)


# ============================================================================ the note's examples
# ---- uniform matroids
ok = okb = okc = True
for n in range(0, 6):
    S = range(1, n + 1)
    for k in range(0, n + 1):
        I = [X for X in subsets(S) if len(X) <= k]
        ok &= is_matroid(S, I)
        okb &= sorted(map(sorted, bases(I))) == sorted(map(sorted, (frozenset(c) for c in itertools.combinations(S, k))))
        if k < n:
            okc &= sorted(map(sorted, circuits(S, I))) == sorted(
                map(sorted, (frozenset(c) for c in itertools.combinations(S, k + 1))))
check("uniform U(k,n), all 0<=k<=n<=5: matroid", ok)
check("uniform: the bases are the k-subsets", okb)
check("uniform: the circuits are the (k+1)-subsets (k < n)", okc)
greedy_vs_brute(range(1, 6), [X for X in subsets(range(1, 6)) if len(X) <= 3], 300, "U(3,5)")
greedy_vs_brute(range(1, 6), [X for X in subsets(range(1, 6)) if len(X) <= 3], 200, "U(3,5), weights of any sign",
                real=True)
# greedy on U(k,n) = the k largest elements
okk = True
for _ in range(300):
    w = {x: random.randint(0, 20) for x in range(1, 7)}
    G = greedy_basis(sorted_order(range(1, 7), w, random), [X for X in subsets(range(1, 7)) if len(X) <= 2])
    okk &= sorted((w[x] for x in G), reverse=True) == sorted(w.values(), reverse=True)[:2]
check("uniform: greedy computes the k largest elements", okk)


# ---- graphs
def components(Vs, Es):
    p = {v: v for v in Vs}

    def find(x):
        while p[x] != x:
            p[x] = p[p[x]]
            x = p[x]
        return x
    for (u, v) in Es:
        p[find(u)] = find(v)
    return len({find(v) for v in Vs})


def acyclic(Vs, Es):
    return components(Vs, Es) == len(Vs) - len(Es)


def simple_cycles_undirected(Vs, Es):
    """Edge sets of the simple cycles of a simple undirected graph."""
    out = set()
    for k in range(3, len(Es) + 1):
        for C in itertools.combinations(Es, k):
            deg = {}
            for (u, v) in C:
                deg[u] = deg.get(u, 0) + 1
                deg[v] = deg.get(v, 0) + 1
            if all(d == 2 for d in deg.values()) and components(list(deg), C) == 1:
                out.add(frozenset(C))
    return out


def spanning_trees(Vs, Es):
    return {frozenset(T) for T in itertools.combinations(Es, len(Vs) - 1) if acyclic(Vs, T) and
            components(Vs, T) == 1}


V4 = [0, 1, 2, 3]
ALL4 = list(itertools.combinations(V4, 2))
okm = okb = okc = okcf = okcog = okcog_b = okcog_c = okdis = okfix = True
nconn = 0
for mask in range(1 << len(ALL4)):
    Es = [e for i, e in enumerate(ALL4) if mask >> i & 1]
    I = [frozenset(X) for X in subsets(Es) if acyclic(V4, X)]
    okm &= is_matroid(Es, I)
    okc &= set(circuits(Es, I)) == simple_cycles_undirected(V4, Es)
    conn = components(V4, Es) == 1
    if conn:
        nconn += 1
        okb &= set(bases(I)) == spanning_trees(V4, Es)
        # cographic (the note's definition): X independent iff (V, E \\ X) connected
        Ic = [X for X in subsets(Es) if components(V4, [e for e in Es if e not in X]) == 1]
        okcog &= is_matroid(Es, Ic)
        okcog_b &= set(bases(Ic)) == {frozenset(Es) - T for T in spanning_trees(V4, Es)}
        bonds = {X for X in subsets(Es) if components(V4, [e for e in Es if e not in X]) > 1 and
                 all(components(V4, [e for e in Es if e not in X - {x}]) == 1 for x in X)}
        okcog_c &= set(circuits(Es, Ic)) == bonds
    else:
        # basis = spanning forest: one tree per component
        okcf &= all(components(V4, B) == components(V4, Es) for B in bases(I))
        Ic = [X for X in subsets(Es) if components(V4, [e for e in Es if e not in X]) == 1]
        okdis &= Ic == []
        k0 = components(V4, Es)
        Ifix = [X for X in subsets(Es) if components(V4, [e for e in Es if e not in X]) == k0]
        okfix &= is_matroid(Es, Ifix)
check("graphic M(G), all 64 graphs on 4 labelled vertices: matroid", okm)
check("graphic: circuits = edge sets of simple cycles (all 64 graphs)", okc)
check(f"graphic, connected G ({nconn} graphs): bases = spanning trees", okb)
check("graphic, disconnected G: bases = spanning forests (one tree per component), not spanning trees", okcf)
check("cographic M*(G), connected G: matroid", okcog)
check("cographic, connected G: bases = complements of spanning trees", okcog_b)
check("cographic, connected G: circuits = bonds (minimal disconnecting edge sets)", okcog_c)
check("cographic as defined in the note, disconnected G: no set (not even the empty set) is independent", okdis)
check("cographic corrected (removing X keeps the number of components): matroid for disconnected G too", okfix)

# random graphs on 5 vertices: graphic matroid + greedy = maximum spanning forest (Kruskal on decreasing weights)
V5 = list(range(5))
ALL5 = list(itertools.combinations(V5, 2))
okm5 = True
for _ in range(25):
    Es = [e for e in ALL5 if random.random() < 0.6]
    I = [X for X in subsets(Es) if acyclic(V5, X)]
    okm5 &= is_matroid(Es, I)
check("graphic: 25 random graphs on 5 vertices: matroid", okm5)
Es = ALL5[:]
IK5 = [X for X in subsets(Es) if acyclic(V5, X)]
greedy_vs_brute(Es, IK5, 150, "graphic M(K5) (maximum spanning tree)")
Ic5 = [X for X in subsets(Es) if components(V5, [e for e in Es if e not in X]) == 1]
okmst = True
for _ in range(150):
    w = {e: random.randint(0, 9) for e in Es}
    G = greedy_basis(sorted_order(Es, w, random), set(Ic5))
    T = frozenset(Es) - G
    best = min(W(T2, w) for T2 in spanning_trees(V5, Es))
    okmst &= components(V5, T) == 1 and len(T) == 4 and W(T, w) == best
check("cographic M*(K5): greedy's complement is a minimum spanning tree (150 random weightings)", okmst)


# ---- linear matroids over Q
def rank(vectors):
    rows = [list(map(Fr, v)) for v in vectors]
    r = 0
    if not rows:
        return 0
    m = len(rows[0])
    for col in range(m):
        piv = next((i for i in range(r, len(rows)) if rows[i][col] != 0), None)
        if piv is None:
            continue
        rows[r], rows[piv] = rows[piv], rows[r]
        for i in range(len(rows)):
            if i != r and rows[i][col] != 0:
                f = rows[i][col] / rows[r][col]
                rows[i] = [a - f * b for a, b in zip(rows[i], rows[r])]
        r += 1
    return r


oklin = oklr = okspan = True
for _ in range(60):
    d, m = random.choice([(2, 4), (3, 5), (3, 6)])
    cols = [[random.choice([-1, 0, 0, 1, 2]) for _ in range(d)] for _ in range(m)]
    S = range(m)
    I = [X for X in subsets(S) if rank([cols[i] for i in X]) == len(X)]
    oklin &= is_matroid(S, I)
    full = rank(cols)
    oklr &= all(len(B) == full for B in bases(I))
    okspan &= all(rank([cols[i] for i in B]) == full for B in bases(I))
    for X in subsets(S):
        if max(len(Y) for Y in I if Y <= X) != rank([cols[i] for i in X]):
            oklr = False
check("linear: 60 random rational matrices (2x4, 3x5, 3x6): matroid", oklin)
check("linear: matroid rank of every subset = linear-algebra rank of its columns", oklr)
check("linear: every basis spans the column space", okspan)
cols = [[1, 0, 1], [0, 1, 1], [1, 1, 2], [1, -1, 0], [2, 0, 2]]
I = [X for X in subsets(range(5)) if rank([cols[i] for i in X]) == len(X)]
greedy_vs_brute(range(5), I, 200, "a 3x5 linear matroid")


# ---- matching matroid
def max_matching_covers(Vs, Es):
    """All vertex sets covered by some matching (brute force over matchings)."""
    cov = set()
    for k in range(len(Vs) // 2 + 1):
        for M in itertools.combinations(Es, k):
            used = [x for e in M for x in e]
            if len(set(used)) == 2 * k:
                cov.add(frozenset(used))
    # I independent iff I is a subset of some covered set
    return {X for C in cov for X in subsets(C)}


okmm = okpm = True
for trial in range(80):
    n = random.choice([4, 5, 6])
    Vs = list(range(n))
    Es = [e for e in itertools.combinations(Vs, 2) if random.random() < 0.45]
    I = max_matching_covers(Vs, Es)
    okmm &= is_matroid(Vs, I)
    # all weights 1: greedy basis has size |V| iff a perfect matching exists
    G = greedy_basis(Vs, I)
    has_pm = any(len({x for e in M for x in e}) == n for M in itertools.combinations(Es, n // 2)) if n % 2 == 0 else False
    okpm &= (len(G) == n) == has_pm
check("matching matroid: 80 random graphs on 4-6 vertices: matroid", okmm)
check("matching matroid with equal weights: greedy basis = V iff G has a perfect matching", okpm)
# matchings as EDGE sets are not a matroid (path a-b-c-d)
Pe = [("a", "b"), ("b", "c"), ("c", "d")]
Im = [X for X in subsets(Pe) if len({x for e in X for x in e}) == 2 * len(X)]
ne_, her_, ex_, wit = axioms(Pe, Im)
check("matchings as edge sets (path a-b-c-d): hereditary but not a matroid", ne_ and her_ and not ex_,
      f"X={sorted(wit[0])}, Y={sorted(wit[1])}")


# ---- edge-disjoint path matroid
def max_flow_unit(n, arcs, s, sinks):
    """Edge-disjoint paths from s to distinct members of `sinks` (a set; s itself allowed, via the empty path)."""
    T = n
    cap = {}
    for (u, v) in arcs:
        cap[(u, v)] = cap.get((u, v), 0) + 1
    for v in sinks:
        cap[(v, T)] = cap.get((v, T), 0) + 1
    flow = 0
    while True:
        prev = {s: None}
        q = [s]
        while q and T not in prev:
            u = q.pop(0)
            for (a, b), c in cap.items():
                if a == u and c > 0 and b not in prev:
                    prev[b] = a
                    q.append(b)
        if T not in prev:
            return flow
        v = T
        while prev[v] is not None:
            u = prev[v]
            cap[(u, v)] -= 1
            cap[(v, u)] = cap.get((v, u), 0) + 1
            v = u
        flow += 1


okdp = True
for _ in range(40):
    n = 5
    arcs = [(u, v) for u in range(n) for v in range(n) if u != v and random.random() < 0.35]
    I = [X for X in subsets(range(n)) if max_flow_unit(n, arcs, 0, X) == len(X)]
    okdp &= is_matroid(range(n), I)
check("edge-disjoint-path matroid: 40 random digraphs on 5 vertices, s = 0: matroid", okdp)


# ============================================================================ Theorem E.2 on all small subset systems
def downsets(n):
    S = list(range(n))
    allsub = list(subsets(S))
    idx = {X: i for i, X in enumerate(allsub)}
    fams = []
    for mask in range(1 << len(allsub)):
        fam = {X for X in allsub if mask >> idx[X] & 1}
        if frozenset() not in fam:
            continue
        if all((X - {x}) in fam for X in fam for x in X):
            fams.append(fam)
    return S, fams


for n, expect in [(3, 19), (4, 167)]:
    S, fams = downsets(n)
    nmat = 0
    okmat = okprf = okstrict = True
    weights = list(itertools.product(range(4), repeat=n))
    for fam in fams:
        if is_matroid(S, fam):
            nmat += 1
            B = bases(fam)
            for wv in weights:
                w = dict(zip(S, wv))
                best = max(W(X, w) for X in fam)
                orders = {tuple(p) for p in itertools.permutations(S) if all(w[p[i]] >= w[p[i + 1]] for i in range(n - 1))}
                for o in orders:
                    if W(greedy_basis(o, fam), w) != best:
                        okmat = False
        else:
            _, _, _, (X, Y) = axioms(S, fam)
            m = len(Y)
            w = {x: (m + 2 if x in Y else m + 1 if x in X else 0) for x in S}
            orders = [p for p in itertools.permutations(S) if all(w[p[i]] >= w[p[i + 1]] for i in range(n - 1))]
            for o in orders:
                G = greedy_basis(o, fam)
                if W(G, w) != m * (m + 2):
                    okprf = False
            if not (W(X, w) >= (m + 1) ** 2 > m * (m + 2)):
                okstrict = False
            # exchange-failing pairs always have |Y| >= 1 (singletons of X are independent)
            if m < 1:
                okstrict = False
    check(f"all {len(fams)} hereditary families on {n} elements enumerated (Dedekind number minus the empty family: {expect})",
          len(fams) == expect)
    check(f"  {nmat} of them are matroids; for each, greedy is optimal for all weights in {{0..3}}^{n} and every "
          f"tie-breaking order", okmat)
    check(f"  for each of the {len(fams) - nmat} non-matroids, the proof's weights make greedy return exactly "
          f"m(m+2), for every tie-breaking order", okprf)
    check(f"  ... while w(X) >= (m+1)^2 > m(m+2), and m = |Y| >= 1", okstrict)
# the iff needs non-negative weights when 'optimal' means a maximum-weight independent set (review R30)
I11 = [frozenset(), frozenset({1})]
Gneg = greedy_basis([1], I11)
check("iff stated for non-negative weights: on the matroid U(1,1) with w = -1, GreedyBasis returns {1} (weight -1), "
      "not the best independent set (empty, weight 0)", Gneg == frozenset({1}) and is_matroid([1], I11))


# ============================================================================ class scheduling (non-matroid)
def overlap(a, b):
    # Chapter 4 convention: classes [S, F] conflict unless one finishes strictly before the other starts
    return not (a[1] < b[0] or b[1] < a[0])


def class_family(cl):
    return {X for X in subsets(range(len(cl))) if all(not overlap(cl[i], cl[j]) for i, j in itertools.combinations(X, 2))}


cl3 = [(0, 2), (3, 5), (1, 4)]
I3 = class_family(cl3)
ne_, her_, ex_, wit = axioms(range(3), I3)
check("classes [0,2], [3,5], [1,4]: hereditary, not a matroid", ne_ and her_ and not ex_)
w3 = {0: 2, 1: 2, 2: 3}
G3 = greedy_basis(sorted_order(range(3), w3), I3)
check("  heaviest-first greedy with weights 2, 2, 3 takes only [1,4]: weight 3, optimum 4",
      W(G3, w3) == 3 and max(W(X, w3) for X in I3) == 4)
# every pair of classes: heaviest-first greedy is optimal
ok2 = True
pts = range(0, 6)
ivs = [(a, b) for a in pts for b in pts if a < b]
for c1 in ivs:
    for c2 in ivs:
        fam = class_family([c1, c2])
        for wv in itertools.product(range(4), repeat=2):
            w = dict(zip(range(2), wv))
            for o in itertools.permutations(range(2)):
                if all(w[o[i]] >= w[o[i + 1]] for i in range(1)):
                    if W(greedy_basis(o, fam), w) != max(W(X, w) for X in fam):
                        ok2 = False
check("two classes never defeat heaviest-first greedy (all pairs of intervals in [0,5], weights 0..3)", ok2)
# the two-class counterexample is for the earliest-finish rule
cl2 = [(0, 2), (1, 10)]
w2 = {0: 1, 1: 5}
ef = sorted(range(2), key=lambda i: cl2[i][1])
take = []
for i in ef:
    if all(not overlap(cl2[i], cl2[j]) for j in take):
        take.append(i)
check("two classes defeat earliest-finish: [0,2] worth 1, [1,10] worth 5 -> 1 versus 5",
      sum(w2[i] for i in take) == 1 and max(W(X, w2) for X in class_family(cl2)) == 5)


# ============================================================================ E.2 scheduling with deadlines
def realistic_brute(X, D, n):
    for perm in itertools.permutations(range(1, n + 1), len(X)):
        if all(day <= D[x] for x, day in zip(X, perm)):
            return True
    return not X


def realistic_count(X, D, n):
    return all(sum(1 for x in X if D[x] <= t) <= t for t in range(0, n + 1))


def sched_family(D, n):
    return {X for X in subsets(range(n)) if realistic_count(X, D, n)}


okE3 = okE4 = okproof = okineq = True
strict_fail = None
for n in range(1, 5):
    for Dv in itertools.product(range(1, n + 1), repeat=n):
        D = dict(enumerate(Dv))
        for X in subsets(range(n)):
            if realistic_brute(sorted(X), D, n) != realistic_count(X, D, n):
                okE3 = False
        fam = sched_family(D, n)
        if not is_matroid(range(n), fam):
            okE4 = False
        for X in fam:
            for Y in fam:
                if len(X) <= len(Y):
                    continue

                def cnt(Z, t):
                    return sum(1 for z in Z if D[z] <= t)
                tstar = max(t for t in range(0, n + 1) if cnt(X, t) <= cnt(Y, t))
                cands = [j for j in X - Y if D[j] == tstar + 1]
                if not cands:
                    okproof = False
                    continue
                Z = Y | {cands[0]}
                if Z not in fam:
                    okproof = False
                for t in range(tstar + 1, n + 1):
                    if not (cnt(Z, t) == cnt(Y, t) + 1 <= cnt(X, t) <= t):
                        okineq = False
                    if cnt(X, t) == t and strict_fail is None:
                        strict_fail = (Dv, sorted(X), sorted(Y), t)
check("Lemma E.3: X realistic (brute force over schedules) iff |X(t)| <= t for all t — every D, n <= 4", okE3)
check("Lemma E.4: realistic sets form a matroid — every deadline vector, n <= 4", okE4)
check("Lemma E.4's proof: t* exists, some j in X \\ Y has deadline t* + 1, and Z = Y + j is realistic", okproof)
check("  for t > t*: |Z(t)| = |Y(t)| + 1 <= |X(t)| <= t", okineq)
check("  the note's strict '|X(t)| < t' fails: |X(t)| = t can happen for t > t*", strict_fail is not None,
      f"D={strict_fail[0]}, X={strict_fail[1]}, Y={strict_fail[2]}, t={strict_fail[3]}" if strict_fail else "")
okE4r = True
for _ in range(40):
    n = random.choice([5, 6])
    D = {i: random.randint(1, n) for i in range(n)}
    okE4r &= is_matroid(range(n), sched_family(D, n))
check("Lemma E.4 on 40 random deadline vectors with n = 5, 6", okE4r)


def realistic_printed(X, D, n, j0=0, loop="if"):
    """Realistic?(X[1..m], D[1..n]) as printed: X sorted by deadline, N <- 0, j <- j0, for t <- 1..n: if D[X[j]] = t ..."""
    Xa = [None] + list(X)  # 1-indexed
    m = len(X)
    N, j = 0, j0
    for t in range(1, n + 1):
        if loop == "if":
            if j == 0:
                raise IndexError("X[0] is not defined")
            if j <= m and D[Xa[j]] == t:
                N += 1
                j += 1
        else:
            while j <= m and D[Xa[j]] == t:
                N += 1
                j += 1
        if N > t:
            return False
    return True


# ---- the page's example
names = "abcdef"
Dx = {"a": 2, "b": 1, "c": 2, "d": 3, "e": 1, "f": 4}
Px = {"a": 9, "b": 8, "c": 7, "d": 5, "e": 4, "f": 2}
n = 6


def is_real(X):
    return realistic_count(X, Dx, n)


def greedy_schedule(order):
    X = []
    log = []
    for i in order:
        cand = sorted(X + [i], key=lambda x: (Dx[x], x))   # kept sorted by deadline
        ok_ = realistic_printed(cand, Dx, n, j0=1, loop="while")
        log.append((i, ok_))
        if ok_:
            X = cand
    return X, log


dec = sorted(names, key=lambda x: -Px[x])
Xg, log = greedy_schedule(dec)
check("example: greedy by decreasing penalty keeps a, b, d, f and rejects c and e",
      sorted(Xg) == list("abdf") and [x for x, o in log if not o] == ["c", "e"])
canon = sorted(Xg, key=lambda x: Dx[x]) + sorted(set(names) - set(Xg))
check("example: canonical schedule b, a, d, f on days 1-4 (all on time), then c and e (late)",
      canon == list("badfce") and all(canon.index(x) + 1 <= Dx[x] for x in Xg))
pen = sum(Px[x] for x in names if canon.index(x) + 1 > Dx[x])
best = min(sum(Px[x] for x, day in zip(p, range(1, n + 1)) if day > Dx[x]) for p in itertools.permutations(names))
check("example: total penalty 11 = 7 + 4, the minimum over all 720 schedules", pen == 11 and best == 11)
check("example: on-time penalty 9 + 8 + 5 + 2 = 24 of 35", sum(Px[x] for x in Xg) == 24 and sum(Px.values()) == 35)
inc = sorted(names, key=lambda x: Px[x])
Xi, _ = greedy_schedule(inc)
pen_i = sum(Px[x] for x in names if x not in Xi)
check("example: the printed 'increasing order' keeps c, d, e, f and pays 9 + 8 = 17", sorted(Xi) == list("cdef")
      and pen_i == 17)
try:
    realistic_printed(["b", "a", "c"], Dx, n, j0=0, loop="if")
    raised = False
except IndexError:
    raised = True
check("Realistic? as printed starts with j <- 0 and reads the undefined X[0]", raised)
check("Realistic? with j <- 1 but 'if' accepts {a, b, c}, which has three deadlines <= 2",
      realistic_printed(["b", "a", "c"], Dx, n, j0=1, loop="if") is True and not is_real({"a", "b", "c"}))
okR = True
for nn in range(1, 6):
    for Dv in itertools.product(range(1, nn + 1), repeat=nn):
        D = dict(enumerate(Dv))
        for X in subsets(range(nn)):
            Xs = sorted(X, key=lambda x: D[x])
            okR &= realistic_printed(Xs, D, nn, j0=1, loop="while") == realistic_count(X, D, nn)
check("Realistic? corrected (j <- 1, 'while') agrees with Lemma E.3 on every subset, every D, n <= 5", okR)
okRif = all(realistic_printed(sorted(X, key=lambda x: D[x]), D, 4, j0=1, loop="if") == realistic_count(X, D, 4)
            for Dv in itertools.product(range(1, 5), repeat=4) for D in [dict(enumerate(Dv))] for X in subsets(range(4)))
check("  the 'if' version disagrees somewhere (n = 4)", not okRif)

# GreedySchedule corrected vs brute force; printed (increasing) loses on some
okgs, nbad = True, 0
for _ in range(150):
    nn = random.choice([4, 5, 6])
    D = {i: random.randint(1, nn) for i in range(nn)}
    P = {i: random.randint(0, 9) for i in range(nn)}
    fam = sched_family(D, nn)

    def gs(order):
        X = []
        for i in order:
            cand = sorted(X + [i], key=lambda x: D[x])
            if realistic_printed(cand, D, nn, j0=1, loop="while"):
                X = cand
        return X
    Xd = gs(sorted(range(nn), key=lambda i: -P[i]))
    penalty = sum(P[i] for i in range(nn) if i not in Xd)
    bestp = min(sum(P[i] for i, day in zip(p, range(1, nn + 1)) if day > D[i]) for p in itertools.permutations(range(nn)))
    okgs &= penalty == bestp
    Xi = gs(sorted(range(nn), key=lambda i: P[i]))
    if sum(P[i] for i in range(nn) if i not in Xi) > bestp:
        nbad += 1
check("GreedySchedule (decreasing penalty) matches the brute-force minimum on 150 random instances", okgs)
check("GreedySchedule as printed (increasing penalty) is suboptimal on some of them", nbad > 0, f"{nbad} of 150")

# ============================================================================ concept page: a linear matroid
vec = {"v1": (1, 0, 0), "v2": (0, 1, 0), "v3": (1, 1, 0), "v4": (0, 0, 1), "v5": (1, 1, 1)}
wt = {"v1": 5, "v2": 4, "v3": 6, "v4": 2, "v5": 3}
Sx = list(vec)
Ix = {X for X in subsets(Sx) if rank([vec[x] for x in X]) == len(X)}
check("concept example: matroid", is_matroid(Sx, Ix))
order = sorted(Sx, key=lambda x: -wt[x])
G = frozenset()
trace = []
for x in order:
    acc = (G | {x}) in Ix
    trace.append((x, acc))
    if acc:
        G = G | {x}
check("concept example: greedy order v3, v1, v2, v5, v4; keeps v3, v1, v5; rejects v2 (= v3 - v1) and v4",
      order == ["v3", "v1", "v2", "v5", "v4"] and trace == [("v3", True), ("v1", True), ("v2", False), ("v5", True),
                                                         ("v4", False)])
Bx = bases(Ix)
check("concept example: weight 14, the maximum over all bases; next best 13",
      W(G, wt) == 14 and max(W(X, wt) for X in Bx) == 14 and sorted({W(X, wt) for X in Bx})[-2] == 13)
check("concept example: {v1, v2, v3} is a circuit", frozenset({"v1", "v2", "v3"}) in circuits(Sx, Ix))
check("concept example: the bases are exactly the 3-sets of rank 3 (8 of the 10)",
      len(Bx) == 8 == sum(1 for T in itertools.combinations(Sx, 3) if rank([vec[x] for x in T]) == 3))


# ============================================================================ page text
def page_checks():
    if not os.path.exists(PAGE):
        check("page exists", False, PAGE)
        return
    txt = open(PAGE, encoding="utf-8").read()
    for s in ["7 + 4 = 11", "9 + 8 = 17", "m(m+2)", "(m+1)^2", "every choice of non-negative weights"]:
        check(f"page mentions '{s}'", s.replace(" ", "") in txt.replace(" ", ""))
    if os.path.exists(CONCEPT):
        ct = open(CONCEPT, encoding="utf-8").read()
        for s in ["14", "v_3", "v_5", "optimal for all non-negative weights"]:
            check(f"concept page mentions '{s}'", s in ct)


page_checks()
print()
if FAIL:
    print(f"{len(FAIL)} FAILED")
    sys.exit(1)
print("ALL OK")
