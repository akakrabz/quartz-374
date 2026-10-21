#!/usr/bin/env python3
"""Checks for content/2-algorithms/04-greedy-algorithms-exercises.md (solved exercises 4.1-4.6 and 4.8-4.10 of
Erickson's Algorithms).

Every greedy rule is simulated under EVERY possible tie-breaking (the book: ties are broken "in a manner that is
completely out of your control"), so "correct" means optimal on every run and "counterexample" means suboptimal on
every run.  Every algorithm on the page is implemented as its pseudocode states it and compared with an independent
brute force on all small inputs plus random ones; every number on the page (book figures included) is checked."""
import functools
import itertools
import math
import random
from bisect import bisect_left
from fractions import Fraction as Fr

random.seed(374)
FAIL = []


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail != "" else ""))
    if not cond:
        FAIL.append(name)


# =============================================================================== intervals (classes)
# A class is a closed interval (s, f, id) with s < f; ids keep identical intervals apart.
# Book p. 162: i and j are compatible iff S[i] > F[j] or S[j] > F[i]; so touching classes conflict.
def conflict(a, b):
    return not (a[0] > b[1] or b[0] > a[1])


def contains(a, b):
    """a completely contains b."""
    return a[0] <= b[0] and b[1] <= a[1]


def is_schedule(K):
    return all(not conflict(a, b) for a, b in itertools.combinations(K, 2))


def opt_size(X, weight=lambda c: 1):
    best = 0
    X = list(X)
    for r in range(len(X) + 1):
        for K in itertools.combinations(X, r):
            if is_schedule(K):
                best = max(best, sum(weight(c) for c in K))
    return best


def nconf(X, x):
    return sum(1 for y in X if y is not x and y != x and conflict(x, y))


def canon(X):
    return tuple(sorted(X))


# Each rule maps a (sorted) tuple of classes to the frozenset of all schedules it can output (over all tie-breaks).
def choose_rule(key):
    """'choose a class x minimizing key, discard the classes that conflict with x, and recurse'."""
    @functools.lru_cache(None)
    def run(X):
        if not X:
            return frozenset([frozenset()])
        vals = [key(X, x) for x in X]
        m = min(vals)
        out = set()
        for x, v in zip(X, vals):
            if v == m:
                rest = canon(y for y in X if y != x and not conflict(x, y))
                out |= {K | {x} for K in run(rest)}
        return frozenset(out)
    return run


def discard_rule(key):
    """'if no classes conflict, choose them all; otherwise discard a class x minimizing key, and recurse'."""
    @functools.lru_cache(None)
    def run(X):
        if is_schedule(X):
            return frozenset([frozenset(X)])
        vals = [key(X, x) for x in X]
        m = min(vals)
        out = set()
        for x, v in zip(X, vals):
            if v == m:
                out |= run(canon(y for y in X if y != x))
        return frozenset(out)
    return run


@functools.lru_cache(None)
def rule_h(X):
    """(h) x = a class with the earliest start, y = a class with the earliest start among the others."""
    if not X:
        return frozenset([frozenset()])
    if len(X) == 1:
        return frozenset([frozenset(X)])
    out = set()
    s1 = min(c[0] for c in X)
    for x in X:
        if x[0] != s1:
            continue
        others = [c for c in X if c != x]
        s2 = min(c[0] for c in others)
        for y in others:
            if y[0] != s2:
                continue
            if not conflict(x, y):
                out |= {K | {x} for K in rule_h(canon(others))}
            elif contains(x, y):
                out |= rule_h(canon(others))
            else:
                out |= rule_h(canon(c for c in X if c != y))
    return frozenset(out)


@functools.lru_cache(None)
def rule_i(X):
    """(i) discard a class that contains another; if none, choose a class that ends last, discard its conflicts."""
    if not X:
        return frozenset([frozenset()])
    out = set()
    containers = [x for x in X if any(y != x and contains(x, y) for y in X)]
    if containers:
        for x in containers:
            out |= rule_i(canon(c for c in X if c != x))
        return frozenset(out)
    fmax = max(c[1] for c in X)
    for y in X:
        if y[1] == fmax:
            out |= {K | {y} for K in rule_i(canon(c for c in X if c != y and not conflict(c, y)))}
    return frozenset(out)


RULES = {
    "EF": choose_rule(lambda X, x: x[1]),                 # the book's GreedySchedule: earliest finish
    "a": choose_rule(lambda X, x: -x[1]),                 # ends last
    "b": choose_rule(lambda X, x: x[0]),                  # starts first
    "c": choose_rule(lambda X, x: -x[0]),                 # starts last
    "d": choose_rule(lambda X, x: x[1] - x[0]),           # shortest duration
    "e": choose_rule(lambda X, x: nconf(X, x)),           # fewest conflicts
    "f": discard_rule(lambda X, x: -(x[1] - x[0])),       # discard longest
    "g": discard_rule(lambda X, x: -nconf(X, x)),         # discard most conflicts
    "h": rule_h,
    "i": rule_i,
}


def mk(pairs):
    return canon((s, f, k) for k, (s, f) in enumerate(pairs))


def all_class_sets(M, nmax):
    ivs = [(s, f) for s in range(M) for f in range(s + 1, M + 1)]
    for n in range(1, nmax + 1):
        for X in itertools.combinations(ivs, n):
            yield mk(X)


def rand_class_sets(count, nmax, M):
    for _ in range(count):
        n = random.randint(1, nmax)
        out = []
        for _ in range(n):
            s = random.randint(0, M - 1)
            out.append((s, random.randint(s + 1, M)))
        yield mk(out)


print("== Exercise 4.1: nine greedy rules for class scheduling")
tests = list(all_class_sets(5, 5)) + list(rand_class_sets(3000, 7, 8))
# duplicates (identical classes) and shared start/finish times
tests += [mk([(0, 2), (0, 2), (1, 3)]), mk([(0, 3), (0, 3), (1, 2), (1, 2)]), mk([(0, 4), (0, 2), (0, 3), (3, 5), (3, 5)])]
for name in ["EF", "c", "h", "i"]:
    bad = None
    for X in tests:
        o = opt_size(X)
        runs = RULES[name](X)
        if not all(is_schedule(K) and len(K) == o for K in runs):
            bad = X
            break
    label = "earliest finish (the book's GreedySchedule)" if name == "EF" else f"rule ({name})"
    check(f"4.1 {label} is optimal on every run, every input", bad is None,
          f"{len(tests)} inputs" if bad is None else f"fails on {bad}")
for name in "abdfg":
    found = any(min(len(K) for K in RULES[name](X)) < opt_size(X) for X in tests[:6000])
    check(f"4.1 rule ({name}) fails on some small input (brute-force search)", found)
check("4.1 rule (e) is optimal on every run of every small test input (its counterexample must be bigger)",
      all(min(len(K) for K in RULES["e"](X)) == opt_size(X) for X in tests[:6000]))


def every_run_fails(name, X):
    o = opt_size(X)
    runs = RULES[name](X)
    return all(is_schedule(K) for K in runs) and max(len(K) for K in runs) < o, o, sorted({len(K) for K in runs})


CX = {
    "ab": [(0, 5), (1, 2), (3, 4)],
    "d": [(0, 4), (5, 9), (3, 6)],
    "e": [(0, 4), (6, 10), (12, 16), (18, 22), (9, 13), (3, 7), (2, 7), (3, 8), (15, 19), (15, 20), (14, 19)],
    "f": [(0, 6), (7, 9), (8, 10)],
    "g": [(0, 3), (2, 7), (1, 8), (6, 14), (12, 19), (13, 18), (17, 20)],
}
for name, key in [("a", "ab"), ("b", "ab"), ("d", "d"), ("e", "e"), ("f", "f"), ("g", "g")]:
    ok, o, sizes = every_run_fails(name, mk(CX[key]))
    check(f"4.1 ({name}) page counterexample: every run is suboptimal", ok, f"optimum {o}, runs give {sizes}")
X = mk(CX["ab"])
check("4.1 (a)/(b) [0,5] is the unique class ending last and the unique class starting first; optimum {[1,2],[3,4]}",
      max(c[1] for c in X) == 5 and sum(c[1] == 5 for c in X) == 1 and sum(c[0] == 0 for c in X) == 1
      and opt_size(X) == 2)
X = mk(CX["d"])
check("4.1 (d) [3,6] is the unique shortest class and conflicts with both others",
      sorted(c[1] - c[0] for c in X) == [3, 4, 4] and all(conflict((3, 6), c) for c in [(0, 4), (5, 9)]))
X = mk(CX["e"])
cnt = {(c[0], c[1]): nconf(X, c) for c in X}
check("4.1 (e) conflict counts: [9,13] has 2 (the unique minimum), [0,4] and [18,22] have 3, all others 4",
      cnt[(9, 13)] == 2 and cnt[(0, 4)] == cnt[(18, 22)] == 3
      and all(v == 4 for k, v in cnt.items() if k not in [(9, 13), (0, 4), (18, 22)]), str(cnt))
ov = lambda X, iv: sorted((c[0], c[1]) for c in X if (c[0], c[1]) != iv and conflict(c, iv))
check("4.1 (e) [9,13] overlaps exactly [6,10] and [12,16]", ov(X, (9, 13)) == [(6, 10), (12, 16)])
grpL = [(0, 4), (2, 7), (3, 7), (3, 8)]
grpR = [(14, 19), (15, 19), (15, 20), (18, 22)]
check("4.1 (e) the two leftover groups are each pairwise conflicting; each of [2,7],[3,7],[3,8] overlaps [0,4] and [6,10]",
      all(conflict(a, b) for g in (grpL, grpR) for a, b in itertools.combinations(g, 2))
      and all(conflict(c, (0, 4)) and conflict(c, (6, 10)) and not conflict(c, (9, 13)) for c in grpL[1:])
      and all(conflict(c, (18, 22)) and conflict(c, (12, 16)) and not conflict(c, (9, 13)) for c in grpR[:3]))
check("4.1 (e) optimum 4 = {[0,4],[6,10],[12,16],[18,22]}; greedy gets 3",
      opt_size(X) == 4 and is_schedule([(0, 4), (6, 10), (12, 16), (18, 22)]) and {len(K) for K in RULES["e"](X)} == {3})
X = mk(CX["f"])
check("4.1 (f) [0,6] is the unique longest class; optimum 2 = {[0,6],[7,9]}; every run keeps 1 class",
      sorted(c[1] - c[0] for c in X) == [2, 2, 6] and opt_size(X) == 2 and {len(K) for K in RULES["f"](X)} == {1})
X = mk(CX["g"])
cnt = {(c[0], c[1]): nconf(X, c) for c in X}
check("4.1 (g) conflict counts: [6,14] has 4 (unique max), the ends [0,3],[17,20] have 2, the rest 3",
      cnt[(6, 14)] == 4 and cnt[(0, 3)] == cnt[(17, 20)] == 2
      and all(v == 3 for k, v in cnt.items() if k not in [(6, 14), (0, 3), (17, 20)]), str(cnt))
check("4.1 (g) optimum 3 = {[0,3],[6,14],[17,20]}; every run ends with 2 classes",
      opt_size(X) == 3 and is_schedule([(0, 3), (6, 14), (17, 20)]) and {len(K) for K in RULES["g"](X)} == {2})
triL, triR = [(0, 3), (2, 7), (1, 8)], [(12, 19), (13, 18), (17, 20)]
check("4.1 (g) bridge [6,14] overlaps exactly [2,7],[1,8],[12,19],[13,18]; triangles pairwise overlap, none across",
      ov(X, (6, 14)) == sorted([(2, 7), (1, 8), (12, 19), (13, 18)])
      and all(conflict(a, b) for t in (triL, triR) for a, b in itertools.combinations(t, 2))
      and not any(conflict(a, b) for a in triL for b in triR))
# (g) after discarding [6,14]: two triangles, every class has 2 conflicts
rest = [c for c in X if (c[0], c[1]) != (6, 14)]
check("4.1 (g) after [6,14] is discarded, every remaining class has exactly 2 conflicts",
      all(nconf(rest, c) == 2 for c in rest))
# (i) proof step: with no containments, the class that ends last also starts last (strictly)
okc = True
for X in tests:
    if not any(x != y and contains(x, y) for x in X for y in X):
        fmax = max(c[1] for c in X)
        for y in X:
            if y[1] == fmax:
                okc &= all(c[0] < y[0] for c in X if c != y)
check("4.1 (i) without containments, a class that ends last starts strictly after all others", okc)

# ============================================================================== Exercise 4.2 weighted
print("== Exercise 4.2: weighted class scheduling")
W2 = {(0, 3): 2, (1, 2): 1}
X = mk([(0, 3), (1, 2)])


def wt(c):
    return W2[(c[0], c[1])]


o = opt_size(X, wt)
for name in ["EF", "c", "h", "i"]:
    runs = RULES[name](X)
    check(f"4.2 [0,3] (2 credits) + [1,2] (1 credit): rule {name} earns 1 on every run, optimum 2",
          o == 2 and {sum(wt(c) for c in K) for K in runs} == {1})
check("4.2(b) with 1 credit per class the credit of a schedule is its size (so 4.1's counterexamples carry over)",
      all(opt_size(mk(CX[k]), lambda c: 1) == opt_size(mk(CX[k])) for k in CX))


def MaxCredit(S, F, C):
    """Page's DP: sort by finish time; Prev(j) = max{i : F[i] < S[j]} (0 if none, by binary search);
    MaxCredit(0) = 0; MaxCredit(j) = max{MaxCredit(j-1), C[j] + MaxCredit(Prev(j))}, j = 1..n."""
    order = sorted(range(len(S)), key=lambda i: F[i])
    S = [None] + [S[i] for i in order]
    F = [None] + [F[i] for i in order]
    C = [None] + [C[i] for i in order]
    n = len(S) - 1
    Fs = F[1:]
    Prev = [None] + [bisect_left(Fs, S[j]) for j in range(1, n + 1)]   # number of i with F[i] < S[j]
    M = {0: 0}
    for j in range(1, n + 1):
        M[j] = max(M[j - 1], C[j] + M[Prev[j]])
    return M[n]


def brute_credit(S, F, C):
    n = len(S)
    best = 0
    for r in range(n + 1):
        for K in itertools.combinations(range(n), r):
            if all(S[i] > F[j] or S[j] > F[i] for i, j in itertools.combinations(K, 2)):
                best = max(best, sum(C[i] for i in K))
    return best


bad = None
cnt = 0
for X in itertools.chain(all_class_sets(5, 4), rand_class_sets(3000, 9, 10)):
    S = [c[0] for c in X]
    F = [c[1] for c in X]
    for _ in range(3):
        C = [random.randint(1, 6) for _ in X]
        cnt += 1
        if MaxCredit(S, F, C) != brute_credit(S, F, C):
            bad = (S, F, C)
check("4.2(c) MaxCredit DP equals brute force (all class sets over 0..5 up to 4 classes, random up to 9)", bad is None,
      f"{cnt} weighted inputs" if bad is None else str(bad))

# ============================================================================== Exercise 4.3 smallest cover
print("== Exercise 4.3: smallest cover")


def union(ivs):
    """Union of closed intervals as a sorted list of disjoint maximal closed intervals."""
    out = []
    for L, R in sorted(ivs):
        if out and L <= out[-1][1]:
            out[-1][1] = max(out[-1][1], R)
        else:
            out.append([L, R])
    return [tuple(x) for x in out]


def SmallestCover(Ls, Rs):
    """Page's pseudocode, literally."""
    iv = sorted(zip(Ls, Rs))                       # sort by left endpoint
    n = len(iv)
    L = [None] + [a for a, b in iv]
    R = [None] + [b for a, b in iv]
    count, reach, i = 0, -math.inf, 1
    chosen = []
    while i <= n:
        if R[i] <= reach:                          # already covered
            i += 1
        else:
            t = max(reach, L[i])
            best, arg = R[i], i
            while i <= n and L[i] <= t:
                if R[i] > best:
                    best, arg = R[i], i
                i += 1
            count += 1
            reach = best
            chosen.append((L[arg], R[arg]))
    return count, chosen


def brute_cover(ivs):
    U = union(ivs)
    for r in range(len(ivs) + 1):
        for Y in itertools.combinations(ivs, r):
            if union(Y) == U:
                return r


def all_interval_lists(M, nmax, degenerate=True):
    ivs = [(a, b) for a in range(M + 1) for b in range(a if degenerate else a + 1, M + 1)]
    for n in range(1, nmax + 1):
        yield from itertools.combinations(ivs, n)


def rand_interval_lists(count, nmax, M, degenerate=True):
    for _ in range(count):
        n = random.randint(1, nmax)
        out = []
        for _ in range(n):
            a = random.randint(0, M)
            out.append((a, random.randint(a if degenerate else a + 1, M)))
        yield tuple(out)


bad = None
cnt = 0
for ivs in itertools.chain(all_interval_lists(4, 5), rand_interval_lists(4000, 9, 12)):
    cnt += 1
    k, Y = SmallestCover([a for a, b in ivs], [b for a, b in ivs])
    if k != brute_cover(ivs) or union(Y) != union(ivs) or len(Y) != k:
        bad = ivs
        break
check("4.3 SmallestCover returns a cover of minimum size (all lists over 0..4 up to 5 intervals, random up to 9)",
      bad is None, f"{cnt} inputs" if bad is None else str(bad))

# The book's figure (p. 178), measured from the page at 300 dpi: 16 intervals, pixel coordinates x 2 (integers).
COVER_FIG = [(117, 605), (867, 1317), (1355, 1842), (1917, 2049),
             (192, 529), (679, 1129), (1485, 1879),
             (361, 1185), (1242, 1692), (1955, 2142),
             (285, 585), (961, 1335), (1561, 2011),
             (249, 849), (923, 1073), (1411, 2085)]
COVER_SHADED = [(117, 605), (867, 1317), (679, 1129), (1242, 1692), (1955, 2142), (249, 849), (1411, 2085)]
k, Y = SmallestCover([a for a, b in COVER_FIG], [b for a, b in COVER_FIG])
check("4.3 book figure: 16 intervals whose union is a single interval", len(COVER_FIG) == 16 and len(union(COVER_FIG)) == 1)
check("4.3 book figure: the shaded 7 intervals form a cover", len(COVER_SHADED) == 7 and union(COVER_SHADED) == union(COVER_FIG))
check("4.3 book figure: SmallestCover finds 6, and 6 is the minimum", k == 6 == brute_cover(COVER_FIG), str(Y))
GREEDY_COVER_FIG = [(117, 605), (361, 1185), (961, 1335), (1242, 1692), (1411, 2085), (1955, 2142)]
check("4.3 book figure: the greedy cover is the page's list of six", Y == GREEDY_COVER_FIG)
robust = True
for _ in range(300):
    P = [(a + random.randint(-6, 6), b + random.randint(-6, 6)) for a, b in COVER_FIG]
    robust &= SmallestCover([a for a, b in P], [b for a, b in P])[0] == 6 and len(union(P)) == 1
check("4.3 book figure: minimum stays 6 when every endpoint moves by up to 3 pixels", robust)

# ============================================================================== Exercise 4.4 stabbing
print("== Exercise 4.4: stabbing points")


def StabIntervals(Ls, Rs):
    iv = sorted(zip(Ls, Rs), key=lambda t: t[1])   # sort by right endpoint
    P = []
    p = -math.inf
    for L, R in iv:
        if L > p:
            p = R
            P.append(p)
    return P


def brute_stab(ivs):
    lo = min(a for a, b in ivs)
    hi = max(b for a, b in ivs)
    cand = [Fr(t, 2) for t in range(2 * lo, 2 * hi + 1)]       # every half-integer point
    for r in range(len(ivs) + 1):
        for P in itertools.combinations(cand, r):
            if all(any(a <= p <= b for p in P) for a, b in ivs):
                return r


def max_disjoint(ivs):
    best = 0
    for r in range(len(ivs) + 1):
        for K in itertools.combinations(ivs, r):
            if all(a[0] > b[1] or b[0] > a[1] for a, b in itertools.combinations(K, 2)):
                best = r
    return best


bad = None
cnt = 0
for ivs in itertools.chain(all_interval_lists(4, 4), rand_interval_lists(1500, 8, 10)):
    cnt += 1
    P = StabIntervals([a for a, b in ivs], [b for a, b in ivs])
    if not all(any(a <= p <= b for p in P) for a, b in ivs) or len(P) != brute_stab(ivs) or len(P) != max_disjoint(ivs):
        bad = ivs
        break
check("4.4 StabIntervals stabs everything with the minimum number of points, = max # disjoint intervals",
      bad is None, f"{cnt} inputs" if bad is None else str(bad))
STAB_FIG = [(117, 605), (867, 1279), (1355, 1842), (1899, 2049),
            (192, 529), (679, 1167), (1485, 1861),
            (361, 1185), (1279, 1692), (1955, 2141),
            (285, 585), (961, 1335), (1561, 2011),
            (249, 849), (923, 1073), (1411, 2085)]
BOOK_POINTS = [492, 1053, 1613, 1985]
check("4.4 book figure: the four drawn points stab all 16 intervals",
      all(any(a <= p <= b for p in BOOK_POINTS) for a, b in STAB_FIG))
P = StabIntervals([a for a, b in STAB_FIG], [b for a, b in STAB_FIG])
check("4.4 book figure: greedy uses 4 points (right ends 529, 1073, 1692, 2049), and 4 is the minimum",
      P == [529, 1073, 1692, 2049] and max_disjoint(STAB_FIG) == 4, str(P))

# ============================================================================== Exercise 4.5 coloring
print("== Exercise 4.5: interval coloring")


def Depth(Ls, Rs):
    """Sweep: sort the 2n endpoints, left endpoints before right endpoints at equal coordinates."""
    ev = sorted([(L, 0) for L in Ls] + [(R, 1) for R in Rs])
    d = best = 0
    for x, kind in ev:
        d += 1 if kind == 0 else -1
        best = max(best, d)
    return best


def SweepColor(Ls, Rs):
    """Process endpoints in the same order; a left endpoint takes a free color (a new one if none is free),
    a right endpoint frees its color."""
    n = len(Ls)
    ev = sorted([(Ls[i], 0, i) for i in range(n)] + [(Rs[i], 1, i) for i in range(n)])
    free, ncolors, color = [], 0, [None] * n
    for x, kind, i in ev:
        if kind == 0:
            if free:
                color[i] = free.pop()
            else:
                ncolors += 1
                color[i] = ncolors
        else:
            free.append(color[i])
    return ncolors, color


def chromatic(ivs):
    n = len(ivs)
    adj = [[j for j in range(n) if j != i and not (ivs[i][0] > ivs[j][1] or ivs[j][0] > ivs[i][1])] for i in range(n)]
    for k in range(1, n + 1):
        col = [0] * n

        def bt(i):
            if i == n:
                return True
            for c in range(1, k + 1):
                if all(col[j] != c for j in adj[i] if j < i):
                    col[i] = c
                    if bt(i + 1):
                        return True
            col[i] = 0
            return False
        if bt(0):
            return k


def proper(ivs, color):
    return all(color[i] != color[j] for i, j in itertools.combinations(range(len(ivs)), 2)
               if not (ivs[i][0] > ivs[j][1] or ivs[j][0] > ivs[i][1]))


def depth_brute(ivs):
    pts = [Fr(t, 2) for t in range(2 * min(a for a, b in ivs), 2 * max(b for a, b in ivs) + 1)]
    return max(sum(a <= p <= b for a, b in ivs) for p in pts)


bad = None
cnt = 0
for ivs in itertools.chain(all_interval_lists(4, 5), rand_interval_lists(3000, 10, 12)):
    cnt += 1
    Ls, Rs = [a for a, b in ivs], [b for a, b in ivs]
    d = Depth(Ls, Rs)
    k, col = SweepColor(Ls, Rs)
    if not (d == chromatic(ivs) == depth_brute(ivs) == k and proper(ivs, col)):
        bad = ivs
        break
check("4.5 Depth = minimum number of colors (brute force), and SweepColor is proper with exactly Depth colors",
      bad is None, f"{cnt} inputs" if bad is None else str(bad))
BOOK_COLORS = [1, 2, 3, 4, 2, 1, 5, 4, 4, 3, 5, 5, 1, 3, 3, 2]
check("4.5 book figure: its coloring with five colors is proper", proper(STAB_FIG, BOOK_COLORS) and max(BOOK_COLORS) == 5)
check("4.5 book figure: the first greedy stabbing point (529) lies in exactly five intervals",
      sum(a <= 529 <= b for a, b in STAB_FIG) == 5)
check("4.5 book figure: depth 5 (all five intervals of the left group contain x = 492), so five colors is the minimum",
      Depth([a for a, b in STAB_FIG], [b for a, b in STAB_FIG]) == 5
      and sum(a <= 492 <= b for a, b in STAB_FIG) == 5 and chromatic(STAB_FIG) == 5)

# ============================================================================== Exercise 4.6 Huffman depth
print("== Exercise 4.6: deep Huffman trees")


@functools.lru_cache(maxsize=1 << 20)
def huff_depths(state):
    """state: sorted tuple of (weight, height) nodes. All possible tree depths over every tie-breaking."""
    if len(state) == 1:
        return frozenset([state[0][1]])
    ws = sorted(w for w, h in state)
    target = (ws[0], ws[1])
    out = set()
    seen = set()
    for i, j in itertools.combinations(range(len(state)), 2):
        a, b = state[i], state[j]
        if tuple(sorted((a[0], b[0]))) != target or (a, b) in seen:
            continue
        seen.add((a, b))
        rest = [state[k] for k in range(len(state)) if k != i and k != j]
        rest.append((a[0] + b[0], 1 + max(a[1], b[1])))
        out |= huff_depths(tuple(sorted(rest)))
    return frozenset(out)


def depths(f):
    return huff_depths(tuple(sorted((w, 0) for w in f)))


def fib(k):
    a, b = 0, 1
    for _ in range(k):
        a, b = b, a + b
    return a


def lucas(k):
    a, b = 2, 1
    for _ in range(k):
        a, b = b, a + b
    return a


def lucas_array(n):
    return [1, 1][:n] + [lucas(j - 2) for j in range(3, n + 1)]


def fav_array(n):
    return [1] + [fib(j - 1) for j in range(2, n + 1)]


check("4.6(a) the arrays: (1,1,1,3,4,7,11,18) and (1,1,1,2,3,5,8,13) for n = 8",
      lucas_array(8) == [1, 1, 1, 3, 4, 7, 11, 18] and fav_array(8) == [1, 1, 1, 2, 3, 5, 8, 13])
check("4.6(a) Lucas array: EVERY Huffman tree has depth n-1 (n = 1..18)",
      all(depths(lucas_array(n)) == {n - 1} for n in range(1, 19)))
check("4.6(a) Fibonacci array F_1..F_n: every Huffman tree has depth n-1 (n = 1..18)",
      all(depths([fib(k) for k in range(1, n + 1)]) == {n - 1} for n in range(1, 19)))
check("4.6(a) (1,1,1,2,3,5,...): SOME Huffman tree has depth n-1 (n = 1..18)",
      all(n - 1 in depths(fav_array(n)) for n in range(1, 19)))
check("4.6(a) ... but not every one for n >= 4 (ties)", all(depths(fav_array(n)) != {n - 1} for n in range(4, 19)))


def min_max_freq(n, robust):
    M = 1
    while True:
        for f0 in itertools.combinations_with_replacement(range(1, M + 1), n - 1):
            f = f0 + (M,)
            D = depths(f)
            if (D == {n - 1}) if robust else (n - 1 in D):
                return M, f
        M += 1


rob = {n: min_max_freq(n, True) for n in range(1, 9)}
fav = {n: min_max_freq(n, False) for n in range(1, 9)}
check("4.6(a) exhaustive (n <= 8): smallest possible largest frequency, every tree deep: 1,1,1,3,4,7,11,18 = L_{n-2} for n >= 3",
      [rob[n][0] for n in range(1, 9)] == [1, 1, 1, 3, 4, 7, 11, 18]
      and all(rob[n][0] == lucas(n - 2) for n in range(3, 9)), str({n: rob[n][1] for n in rob}))
check("4.6(a) exhaustive (n <= 8): smallest largest frequency if ties may go your way: 1,1,1,2,3,5,8,13 = F_{n-1} for n >= 2",
      [fav[n][0] for n in range(1, 9)] == [1, 1, 1, 2, 3, 5, 8, 13]
      and all(fav[n][0] == fib(n - 1) for n in range(2, 9)))
check("4.6(a) L_{n-2} < F_n for n >= 5, L_{n-2} = F_n for n = 4 (Fibonacci is not optimal)",
      all(lucas(n - 2) < fib(n) for n in range(5, 60)) and lucas(2) == fib(4))
check("4.6(a) Fibonacci: F_1 + ... + F_k = F_{k+2} - 1; L_m = F_{m-1} + F_{m+1}; n = 5: L_3 = 4 vs F_5 = 5",
      all(sum(fib(i) for i in range(1, k + 1)) == fib(k + 2) - 1 for k in range(1, 50))
      and all(lucas(m) == fib(m - 1) + fib(m + 1) for m in range(1, 50)) and lucas(3) == 4 and fib(5) == 5)
check("4.6(a) (1,1,1,2): Huffman trees of depth 3 and of depth 2 both occur", depths([1, 1, 1, 2]) == {2, 3})
check("4.6(a) n = 6 figure: (1,1,1,3,4,7), internal weights 2, 3, 6, 10, 17, every tree has depth 5",
      lucas_array(6) == [1, 1, 1, 3, 4, 7] and [sum(lucas_array(6)[:k]) for k in range(2, 7)] == [2, 3, 6, 10, 17]
      and depths(lucas_array(6)) == {5})
check("4.6(b) Fibonacci total N = F_{n+2} - 1", all(sum(fib(k) for k in range(1, n + 1)) == fib(n + 2) - 1 for n in range(1, 40)))
check("4.6(a) identity S_k = f_1 + ... + f_k = L_k - 1 for the Lucas array (k >= 2)",
      all(sum(lucas_array(k + 3)[:k]) == lucas(k) - 1 for k in range(2, 40)))


def huffman_tree_random(f):
    """One Huffman run with random tie-breaking. Returns parent pointers and weights."""
    nodes = [[w, None] for w in f]                 # weight, parent
    alive = list(range(len(f)))
    while len(alive) > 1:
        random.shuffle(alive)
        alive.sort(key=lambda v: nodes[v][0])
        a, b = alive[0], alive[1]
        nodes.append([nodes[a][0] + nodes[b][0], None])
        nodes[a][1] = nodes[b][1] = len(nodes) - 1
        alive = alive[2:] + [len(nodes) - 1]
    return nodes


ok_gp = ok_depth = True
for _ in range(3000):
    n = random.randint(2, 40)
    f = [random.choice([1, 1, 2, 3, random.randint(1, 50), random.randint(1, 1000)]) for _ in range(n)]
    nodes = huffman_tree_random(f)
    N = sum(f)
    for v in range(len(nodes)):
        p = nodes[v][1]
        if p is not None and nodes[p][1] is not None:
            ok_gp &= nodes[nodes[p][1]][0] >= 2 * nodes[v][0]
    for leaf in range(n):
        d, v = 0, leaf
        while nodes[v][1] is not None:
            v = nodes[v][1]
            d += 1
        ok_depth &= d <= 2 * math.log2(N) + 1
check("4.6(b) in random Huffman trees every grandparent weighs at least twice its grandchild", ok_gp)
check("4.6(b) every leaf depth is at most 2 log2 N + 1", ok_depth)
check("4.6(b) the bound is about right for Fibonacci frequencies: depth n-1 vs 2 log2 N + 1",
      all(n - 1 <= 2 * math.log2(sum(fib(k) for k in range(1, n + 1))) + 1 for n in range(2, 60)))

# ============================================================================== Exercise 4.8 ternary codes
print("== Exercise 4.8: optimal ternary codes")


def ternary_cost(f, naive=False, rng=None):
    """Page's algorithm: if n is even add a symbol of frequency 0; repeatedly merge the three smallest.
    naive=True: never add the dummy; merge three while >= 3 nodes remain, then merge the last two.
    Returns (cost, codeword lengths)."""
    items = [(w, [i]) for i, w in enumerate(f)]
    if not naive and len(f) % 2 == 0:
        items.append((0, []))
    depth = [0] * len(f)
    while len(items) > 1:
        if rng:
            rng.shuffle(items)
        items.sort(key=lambda t: t[0])
        k = 3 if len(items) >= 3 else 2
        group = items[:k]
        items = items[k:]
        leaves = [i for w, ls in group for i in ls]
        for i in leaves:
            depth[i] += 1
        items.append((sum(w for w, ls in group), leaves))
    return sum(w * d for w, d in zip(f, depth)), depth


def kraft_opt(f):
    """Independent: min sum f_i l_i over codeword lengths with sum 3^-l_i <= 1 (Kraft-McMillan)."""
    n = len(f)
    if n == 1:
        return 0
    fs = sorted(f, reverse=True)
    best = None
    for ls in itertools.combinations_with_replacement(range(1, n), n):
        if sum(Fr(1, 3 ** l) for l in ls) <= 1:
            c = sum(a * b for a, b in zip(fs, ls))
            best = c if best is None else min(best, c)
    return best


bad = None
cnt = 0
for n in range(1, 8):
    for _ in range(150 if n > 2 else 20):
        f = [random.randint(1, 12) for _ in range(n)]
        cnt += 1
        c, ls = ternary_cost(f, rng=random.Random(cnt))
        if c != kraft_opt(f) or sum(Fr(1, 3 ** l) for l in ls) > 1:
            bad = f
            break
check("4.8 ternary algorithm cost = Kraft brute force optimum (random ties), n = 1..7", bad is None,
      f"{cnt} inputs" if bad is None else str(bad))
check("4.8 n = 4, f = (1,1,1,1): algorithm cost 6 (lengths 1,1,2,2), naive cost 7 (lengths 1,2,2,2)",
      ternary_cost([1, 1, 1, 1])[0] == 6 == kraft_opt([1, 1, 1, 1]) and ternary_cost([1, 1, 1, 1], naive=True)[0] == 7
      and sorted(ternary_cost([1, 1, 1, 1])[1]) == [1, 1, 2, 2] and sorted(ternary_cost([1, 1, 1, 1], naive=True)[1]) == [1, 2, 2, 2])
check("4.8 for odd n the naive version coincides with the algorithm (no dummy needed)",
      all(ternary_cost(f, naive=True)[0] == ternary_cost(f)[0]
          for f in ([random.randint(1, 9) for _ in range(random.choice([1, 3, 5, 7]))] for _ in range(300))))


def full_tree_dummy_reduction_ok(trials=400):
    """Lemma check: for n even, OPT(f) = OPT_full(f + [0]); for n odd, OPT(f) = OPT_full(f)."""
    ok = True
    for _ in range(trials):
        n = random.randint(2, 6)
        f = [random.randint(1, 9) for _ in range(n)]
        ok &= kraft_opt(f) == kraft_opt_full(f + ([0] if n % 2 == 0 else []))
    return ok


def kraft_opt_full(f):
    """Min cost over FULL ternary trees: lengths with sum 3^-l = 1 exactly (n odd)."""
    n = len(f)
    if n == 1:
        return 0
    fs = sorted(f, reverse=True)
    best = None
    for ls in itertools.combinations_with_replacement(range(1, n), n):
        if sum(Fr(1, 3 ** l) for l in ls) == 1:
            c = sum(a * b for a, b in zip(fs, ls))
            best = c if best is None else min(best, c)
    return best


check("4.8 n = 1: cost 0 (empty codeword); n = 2: both codewords have length 1",
      ternary_cost([5])[0] == 0 == kraft_opt([5]) and ternary_cost([3, 9])[1] == [1, 1])
check("4.8 reduction: optimal code cost = optimal FULL ternary tree cost after adding one 0 when n is even",
      full_tree_dummy_reduction_ok())

# ============================================================================== Exercise 4.9 Gale-Shapley
print("== Exercise 4.9: Gale-Shapley in O(n^2) time")


def GaleShapley(Hpref, Dpref):
    """Page's pseudocode (1-based arrays emulated). Hpref[A][r] = r-th doctor of hospital A,
    Dpref[a][r] = r-th hospital of doctor a. Returns (Match, number of offers)."""
    n = len(Hpref) - 1
    Rank = [[None] * (n + 1) for _ in range(n + 1)]
    Match = [0] * (n + 1)
    for a in range(1, n + 1):
        for r in range(1, n + 1):
            Rank[a][Dpref[a][r]] = r
    Next = [None] + [1] * n
    Free = list(range(1, n + 1))
    offers = 0
    while Free:
        A = Free.pop()
        assert Next[A] <= n
        a = Hpref[A][Next[A]]
        Next[A] += 1
        offers += 1
        if Match[a] == 0:
            Match[a] = A
        elif Rank[a][A] < Rank[a][Match[a]]:
            Free.append(Match[a])
            Match[a] = A
        else:
            Free.append(A)
    return Match, offers


def stable_matchings(Hpref, Dpref):
    n = len(Hpref) - 1
    hr = {A: {Hpref[A][r]: r for r in range(1, n + 1)} for A in range(1, n + 1)}
    dr = {a: {Dpref[a][r]: r for r in range(1, n + 1)} for a in range(1, n + 1)}
    out = []
    for perm in itertools.permutations(range(1, n + 1)):
        hosp_of = {a: perm[a - 1] for a in range(1, n + 1)}       # doctor a -> hospital
        doc_of = {A: a for a, A in hosp_of.items()}
        if all(not (dr[a][B] < dr[a][hosp_of[a]] and hr[B][a] < hr[B][doc_of[B]])
               for a in range(1, n + 1) for B in range(1, n + 1)):
            out.append(hosp_of)
    return out, hr


def rand_prefs(n):
    H = [None] + [[None] + random.sample(range(1, n + 1), n) for _ in range(n)]
    D = [None] + [[None] + random.sample(range(1, n + 1), n) for _ in range(n)]
    return H, D


okgs = True
cnt = 0
for n in range(1, 7):
    for _ in range(200 if n > 2 else 20):
        H, D = rand_prefs(n)
        Match, offers = GaleShapley(H, D)
        sms, hr = stable_matchings(H, D)
        # hospital-optimal stable matching: every hospital gets its best feasible doctor
        best = {A: min((m_doc for m in sms for m_doc, m_h in m.items() if m_h == A), key=lambda a: hr[A][a])
                for A in range(1, n + 1)}
        cnt += 1
        okgs &= offers <= n * n and {a: Match[a] for a in range(1, n + 1)} in sms \
            and all(Match[best[A]] == A for A in range(1, n + 1))
check("4.9 implementation returns the hospital-optimal stable matching with <= n^2 offers (random, n <= 6)", okgs,
      f"{cnt} inputs")
# the book's example (p. 173): doctors q r s t = 1..4, hospitals A B C D = 1..4
q, r_, s, t = 1, 2, 3, 4
A, B, C, D_ = 1, 2, 3, 4
Dp = [None, [None, A, B, C, D_], [None, A, D_, C, B], [None, B, A, C, D_], [None, D_, B, C, A]]
Hp = [None, [None, t, s, r_, q], [None, r_, t, q, s], [None, t, r_, s, q], [None, s, r_, q, t]]
Match, offers = GaleShapley(Hp, Dp)
check("4.9 book example: the implementation returns {As, Bt, Cq, Dr}",
      Match[s] == A and Match[t] == B and Match[q] == C and Match[r_] == D_, f"{offers} offers")
sms, _ = stable_matchings(Hp, Dp)
check("4.9 book example: {As, Bt, Cq, Dr} is its ONLY stable matching", sms == [{s: A, t: B, q: C, r_: D_}])
alt = {r_: A, s: B, q: C, t: D_}                  # the book's second "stable" matching {Ar, Bs, Cq, Dt}
qB = Dp[q].index(B) < Dp[q].index(alt[q]) and Hp[B].index(q) < Hp[B].index(s)
check("4.9 book p. 174 error: {Ar, Bs, Cq, Dt} is NOT stable -- Dr. Quincy and Bedlam prefer each other", qB)

# ============================================================================== Exercise 4.10 many offers
print("== Exercise 4.10: Omega(n^2) offers")


def all_runs_offers(H, D):
    """Explore EVERY valid execution (any unmatched hospital may offer next). Returns (min, max) #offers and the
    set of final matchings."""
    n = len(H) - 1
    rank = {a: {D[a][r]: r for r in range(1, n + 1)} for a in range(1, n + 1)}

    @functools.lru_cache(None)
    def go(nxt, match):           # nxt[A-1]: next index in A's list; match[a-1]: hospital of doctor a (0 = none)
        matched = set(match) - {0}
        free = [A for A in range(1, n + 1) if A not in matched]
        if not free:
            return 0, 0, frozenset([match])
        lo, hi, finals = math.inf, -math.inf, set()
        for A in free:
            a = H[A][nxt[A - 1]]
            nx = list(nxt)
            nx[A - 1] += 1
            m = list(match)
            if m[a - 1] == 0 or rank[a][A] < rank[a][m[a - 1]]:
                m[a - 1] = A
            l, h, fs = go(tuple(nx), tuple(m))
            lo, hi, finals = min(lo, l + 1), max(hi, h + 1), finals | fs
        return lo, hi, frozenset(finals)
    return go(tuple([1] * n), tuple([0] * n))


ok10 = True
detail = []
for n in range(1, 7):
    Hid = [None] + [[None] + list(range(1, n + 1)) for _ in range(n)]
    Did = [None] + [[None] + list(range(1, n + 1)) for _ in range(n)]
    lo, hi, finals = all_runs_offers(Hid, Did)
    detail.append((n, lo, hi))
    ok10 &= lo == hi == n * (n + 1) // 2 and finals == {tuple(range(1, n + 1))}
check("4.10 identical preferences: every execution makes exactly n(n+1)/2 offers and pairs i with i (n <= 6)", ok10,
      str(detail))
sms, _ = stable_matchings([None] + [[None] + list(range(1, 6)) for _ in range(5)],
                          [None] + [[None] + list(range(1, 6)) for _ in range(5)])
check("4.10 identical preferences, n = 5: the only stable matching pairs hospital i with doctor i",
      sms == [{a: a for a in range(1, 6)}])


def turns_run(n):
    """(a) explicit run: A_1, ..., A_n take turns, each offering until accepted. Returns #offers, #drops, valid."""
    match, offers, drops, valid = {}, 0, 0, True
    for A in range(1, n + 1):
        for a in range(1, n + 1):                  # A's list in order
            offers += 1
            if a not in match:
                match[a] = A
                break
            if A < match[a]:                       # a prefers A (smaller index = better)
                drops += 1
            # otherwise a rejects A; valid as long as A offers to the next doctor on its list
    return offers, drops, match == {a: a for a in range(1, n + 1)}


check("4.10(a) explicit run: A_k offers to alpha_1..alpha_k, nobody is dropped, n(n+1)/2 offers (n <= 30)",
      all(turns_run(n) == (n * (n + 1) // 2, 0, True) for n in range(1, 31)))
Hid = [None] + [[None] + list(range(1, 7)) for _ in range(6)]
check("4.10 the stack implementation of 4.9 makes 21 = 6*7/2 offers on it for n = 6", GaleShapley(Hid, Hid)[1] == 21)

# ============================================================================== page text = checked data
print("== page text")
import os
import re
PAGE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "content", "2-algorithms",
                    "04-greedy-algorithms-exercises.md")
TEXT = open(PAGE, encoding="utf-8").read()


def section(title):
    return TEXT.split(title, 1)[1].split("\n### ", 1)[0].split("\n## ", 1)[0]


def ivs_in(s):
    return {(int(a), int(b)) for a, b in re.findall(r"\[(\d+),\s*(\d+)\]", s)}


for title, key in [("### (a) Ends last and (b) starts first", "ab"), ("### (d) Shortest duration", "d"),
                   ("### (e) Fewest conflicts", "e"), ("### (f) Discard the longest", "f"),
                   ("### (g) Discard the most conflicted", "g")]:
    check(f"page 4.1 {title[4:]}: the intervals on the page are exactly the checked counterexample",
          ivs_in(section(title)) == set(CX[key]), str(sorted(ivs_in(section(title)))))
check("page 4.2(a)/(b): the counterexample is [0,3] (2 credits) and [1,2] (1 credit)",
      ivs_in(section("### (a) and (b) Every greedy rule fails")) == {(0, 3), (1, 2)}
      and "$[0,3]$ worth 2 credits and $[1,2]$ worth 1 credit" in TEXT)
check("page 4.3/4.4/4.5: book figures need 6 cover intervals, 4 points, 5 colors",
      "covers it with **6** of them" in TEXT and "uses four points" in TEXT and "has depth 5" in TEXT)
check("page 4.6(a): answer (1, 1, 1, 3, 4, 7, 11, ...) with largest frequency L_{n-2}",
      "$f = (1, 1, 1, 3, 4, 7, 11, \\ldots)$ with $f[j] = L_{j-2}$" in TEXT)
check("page 4.8: (1,1,1,1) costs 7 the naive way and 6 with the dummy",
      "codeword lengths $1, 2, 2, 2$, cost 7" in TEXT and "lengths $1, 1, 2, 2$, cost 6" in TEXT)
check("page 4.10: n(n+1)/2 offers in every run", "\\frac{n(n+1)}{2} = \\Omega(n^2)" in TEXT)

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: {FAIL}")
