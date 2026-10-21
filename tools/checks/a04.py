#!/usr/bin/env python3
"""Checks for every concrete claim on content/2-algorithms/04-greedy-algorithms.md and the concept pages
greedy-algorithms, interval-scheduling, huffman-codes, stable-matching.

Every algorithm is implemented as the pages state it (pseudocode transcribed line by line) and compared with
brute force on all small inputs plus random ones; every example, number and counterexample is recomputed."""
import fractions
import functools
import heapq
import itertools
import math
import os
import random
import re
import sys

sys.setrecursionlimit(10000)
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
PAGE = os.path.join(ROOT, "content", "2-algorithms", "04-greedy-algorithms.md")
CONCEPTS = os.path.join(ROOT, "content", "concepts")
FIGS = os.path.join(HERE, "..", "figs")
FAIL = []
random.seed(374)


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAIL.append(name)


def read(path):
    return open(path, encoding="utf-8").read()


TEXT = read(PAGE)
CON = {k: read(os.path.join(CONCEPTS, k + ".md")) for k in
       ["greedy-algorithms", "interval-scheduling", "huffman-codes", "stable-matching"]}


def table_row(text, label):
    """Cells after the label cell of the first table row starting with `label`."""
    for ln in text.splitlines():
        t = ln.lstrip("> ").strip()
        if t.startswith("|"):
            cells = [c.strip() for c in t.strip("|").split("|")]
            if cells[0] == label:
                return cells[1:]
    raise KeyError(label)


def table_rows(text, label):
    """Concatenated cells of all rows labeled `label`."""
    out = []
    for ln in text.splitlines():
        t = ln.lstrip("> ").strip()
        if t.startswith("|"):
            cells = [c.strip() for c in t.strip("|").split("|")]
            if cells[0] == label:
                out += cells[1:]
    return out


def has(text, s):
    return s in text


# =====================================================================================================
print("== 4.1 tape sorting")


def exp_cost_double(order, L):
    n = len(order)
    return fractions.Fraction(sum(sum(L[order[i]] for i in range(k + 1)) for k in range(n)), n)


def exp_cost_weighted_form(order, L):
    n = len(order)
    return fractions.Fraction(sum((n - i) * L[order[i]] for i in range(n)), n)   # i is 0-based


def total_cost(order, L, F):
    t = tot = 0
    for i in order:
        t += L[i]
        tot += F[i] * t
    return tot


ok = True
for _ in range(500):
    n = random.randint(1, 7)
    L = [random.randint(1, 9) for _ in range(n)]
    p = list(range(n)); random.shuffle(p)
    ok &= exp_cost_double(p, L) == exp_cost_weighted_form(p, L)
check("E[cost] double sum = (1/n) sum (n-i+1) L[pi(i)] on 500 random orders", ok)

ok = True
for n in range(1, 6):
    for L in itertools.product(range(1, 5), repeat=n):
        best = min(exp_cost_double(p, L) for p in itertools.permutations(range(n)))
        srt = sorted(range(n), key=lambda i: L[i])
        ok &= exp_cost_double(srt, L) == best
        # every optimal order is sorted by length
        for p in itertools.permutations(range(n)):
            if exp_cost_double(p, L) == best:
                ok &= all(L[p[i]] <= L[p[i + 1]] for i in range(n - 1))
check("Lemma 4.1: sorted order optimal, and every optimal order sorted (all L in {1..4}^n, n<=5)", ok)

ok = True
for _ in range(400):
    n = random.randint(2, 7)
    L = [random.randint(1, 20) for _ in range(n)]
    p = list(range(n)); random.shuffle(p)
    i = random.randrange(n - 1)
    q = p[:]; q[i], q[i + 1] = q[i + 1], q[i]
    a, b = p[i], p[i + 1]
    ok &= exp_cost_double(q, L) - exp_cost_double(p, L) == fractions.Fraction(L[b] - L[a], n)
check("adjacent swap changes expected cost by (L[b]-L[a])/n", ok)

ok = True
for _ in range(400):
    n = random.randint(2, 7)
    L = [random.randint(1, 20) for _ in range(n)]
    F = [random.randint(1, 20) for _ in range(n)]
    p = list(range(n)); random.shuffle(p)
    i = random.randrange(n - 1)
    q = p[:]; q[i], q[i + 1] = q[i + 1], q[i]
    a, b = p[i], p[i + 1]
    ok &= total_cost(q, L, F) - total_cost(p, L, F) == L[b] * F[a] - L[a] * F[b]
check("weighted adjacent swap changes total cost by L[b]F[a] - L[a]F[b]", ok)

ok = True
cnt = 0
for _ in range(1500):
    n = random.randint(1, 6)
    L = [random.randint(1, 6) for _ in range(n)]
    F = [random.randint(1, 6) for _ in range(n)]
    best = min(total_cost(p, L, F) for p in itertools.permutations(range(n)))
    ratio_sorted = [p for p in itertools.permutations(range(n))
                    if all(L[p[i]] * F[p[i + 1]] <= L[p[i + 1]] * F[p[i]] for i in range(n - 1))]
    ok &= all(total_cost(p, L, F) == best for p in ratio_sorted) and len(ratio_sorted) > 0
    srt = sorted(range(n), key=lambda i: fractions.Fraction(L[i], F[i]))
    ok &= total_cost(srt, L, F) == best
    cnt += 1
check(f"Lemma 4.2: every ratio-sorted order is optimal (vs all permutations, {cnt} random inputs incl. ratio ties)", ok)

# the page's examples
Lx = {"a": 2, "b": 1, "c": 3, "d": 4}
Fx = {"a": 3, "b": 2, "c": 1, "d": 4}
names = "abcd"
Ll = [Lx[c] for c in names]; Fl = [Fx[c] for c in names]
srt = sorted(range(4), key=lambda i: Ll[i])
pref = list(itertools.accumulate(Ll[i] for i in srt))
rev = list(itertools.accumulate(Ll[i] for i in sorted(range(4), key=lambda i: -Ll[i])))
check("uniform example: sorted b,a,c,d reads 1,3,6,10, expected 20/4 = 5",
      "".join(names[i] for i in srt) == "bacd" and pref == [1, 3, 6, 10] and fractions.Fraction(sum(pref), 4) == 5
      and has(TEXT, "read costs $1, 3, 6, 10$ and expected cost $20/4 = 5$"))
check("uniform example: reverse d,c,a,b reads 4,7,9,10, expected 30/4 = 7.5",
      rev == [4, 7, 9, 10] and sum(rev) / 4 == 7.5 and has(TEXT, "read costs $4, 7, 9, 10$ and expected cost $30/4 = 7.5$"))
check("weighted example table L and F rows match", table_row(TEXT, "$L$") == ["2", "1", "3", "4"]
      and table_row(TEXT, "$F$") == ["3", "2", "1", "4"])
check("weighted example L/F row rounded", table_row(TEXT, "$L/F$") ==
      [f"{Ll[i] / Fl[i]:.2f}".rstrip("0").rstrip(".") for i in range(4)],
      str(table_row(TEXT, "$L/F$")))
opt = min(total_cost(p, Ll, Fl) for p in itertools.permutations(range(4)))
rord = sorted(range(4), key=lambda i: fractions.Fraction(Ll[i], Fl[i]))
byL = sorted(range(4), key=lambda i: Ll[i])
byF = sorted(range(4), key=lambda i: -Fl[i])
check("weighted example: ratio order b,a,d,c costs 49 = min over 24 orders",
      "".join(names[i] for i in rord) == "badc" and total_cost(rord, Ll, Fl) == 49 == opt
      and 2 * 1 + 3 * 3 + 4 * 7 + 1 * 10 == 49 and len(list(itertools.permutations(range(4)))) == 24)
check("weighted example: by length b,a,c,d costs 57; by decreasing frequency d,a,b,c costs 58",
      "".join(names[i] for i in byL) == "bacd" and total_cost(byL, Ll, Fl) == 57
      and "".join(names[i] for i in byF) == "dabc" and total_cost(byF, Ll, Fl) == 58)
check("weighted example: the page states 49 (ratio order b,a,d,c), 57 (by length) and 58 (by frequency)",
      has(TEXT, "The ratio order $b, a, d, c$ costs $2\\cdot1 + 3\\cdot3 + 4\\cdot7 + 1\\cdot10 = 49$")
      and has(TEXT, "Sorting by length ($b, a, c, d$) costs 57")
      and has(TEXT, "sorting by decreasing frequency ($d, a, b, c$) costs 58"))

# =====================================================================================================
print("== 4.2 scheduling classes")


def compatible(i, j, S, F):
    return S[i] > F[j] or S[j] > F[i]


def is_schedule(X, S, F):
    return all(compatible(i, j, S, F) for i, j in itertools.combinations(X, 2))


def brute_max(S, F):
    n = len(S)
    for r in range(n, -1, -1):
        for X in itertools.combinations(range(n), r):
            if is_schedule(X, S, F):
                return r
    return 0


def greedy_schedule(S, F):
    """Transcription of GreedySchedule; returns original indices."""
    n = len(S)
    perm = sorted(range(n), key=lambda i: F[i])           # sort F, permute S
    Ss = [None] + [S[i] for i in perm]
    Fs = [None] + [F[i] for i in perm]
    X = {}
    count = 1
    X[count] = 1
    for i in range(2, n + 1):
        if Ss[i] > Fs[X[count]]:
            count += 1
            X[count] = i
    return [perm[X[k] - 1] for k in range(1, count + 1)]


def rec_schedule(cls, S, F):
    """Book's 'take class 1 or not' recursion."""
    if not cls:
        return 0
    c, rest = cls[0], cls[1:]
    B = [i for i in rest if F[i] < S[c]]
    A = [i for i in rest if S[i] > F[c]]
    return max(rec_schedule(rest, S, F), 1 + rec_schedule(B, S, F) + rec_schedule(A, S, F))


ok = ok2 = True
count_inputs = 0
ivs = [(s, f) for s in range(0, 5) for f in range(s + 1, 6)]
for n in range(1, 5):
    for combo in itertools.combinations_with_replacement(ivs, n):
        S = [c[0] for c in combo]; F = [c[1] for c in combo]
        X = greedy_schedule(S, F)
        bm = brute_max(S, F)
        ok &= is_schedule(X, S, F) and len(X) == bm
        ok2 &= rec_schedule(list(range(n)), S, F) == bm
        count_inputs += 1
for _ in range(1500):
    n = random.randint(1, 9)
    S, F = [], []
    for _ in range(n):
        s = random.randint(0, 20); S.append(s); F.append(random.randint(s + 1, s + 8))
    X = greedy_schedule(S, F)
    bm = brute_max(S, F)
    ok &= is_schedule(X, S, F) and len(X) == bm
    if n <= 7:
        ok2 &= rec_schedule(list(range(n)), S, F) == bm
    count_inputs += 1
check(f"GreedySchedule returns a conflict-free schedule of maximum size ({count_inputs} inputs, ties included)", ok)
check("the book's take-class-1-or-not recursion = brute-force maximum", ok2)

ok = True
for _ in range(800):
    n = random.randint(1, 8)
    S, F = [], []
    for _ in range(n):
        s = random.randint(0, 15); S.append(s); F.append(random.randint(s + 1, s + 6))
    f = min(range(n), key=lambda i: F[i])
    bm = brute_max(S, F)
    ok &= any(f in X and is_schedule(X, S, F) for X in itertools.combinations(range(n), bm))
    # the exchange of Lemma 4.3 on every maximum schedule
    for X in itertools.combinations(range(n), bm):
        if is_schedule(X, S, F) and f not in X:
            g = min(X, key=lambda i: F[i])
            ok &= is_schedule([i for i in X if i != g] + [f], S, F)
check("Lemma 4.3: swapping f for the first-finishing class of any maximum schedule keeps it conflict-free", ok)

# the figure's nine classes
CL = [("a", 1, 3), ("b", 0, 8), ("c", 7, 9), ("d", 6, 11), ("e", 4, 13),
      ("f", 14, 16), ("g", 10, 17), ("h", 15, 18), ("i", 19, 24)]
S9 = [c[1] for c in CL]; F9 = [c[2] for c in CL]; N9 = [c[0] for c in CL]
G9 = [N9[i] for i in greedy_schedule(S9, F9)]
check("figure: classes listed in order of finish time with distinct endpoints",
      F9 == sorted(F9) and len(set(S9 + F9)) == 18)
check("figure: GreedySchedule picks a, c, f, i; maximum is 4", G9 == list("acfi") and brute_max(S9, F9) == 4)
check("figure: a, d, h, i is another maximum schedule",
      is_schedule([N9.index(c) for c in "adhi"], S9, F9))
fig = read(os.path.join(FIGS, "a04-schedule.html"))
check("figure caption names a, c, f, i and a, d, h, i",
      "<i>a</i>, <i>c</i>, <i>f</i>, <i>i</i>" in fig and "<i>a</i>, <i>d</i>, <i>h</i>, <i>i</i>" in fig)


def rule_outcomes(cls, key):
    """All results of: pick x minimizing key (any tie), drop conflicts, repeat."""
    S = [c[0] for c in cls]; F = [c[1] for c in cls]
    outs = set()

    @functools.lru_cache(maxsize=None)
    def go(rem):
        if not rem:
            return frozenset([0])
        vals = {i: key(i, rem, S, F) for i in rem}
        m = min(vals.values())
        res = set()
        for x in rem:
            if vals[x] == m:
                nxt = tuple(j for j in rem if j != x and compatible(x, j, S, F))
                res |= {1 + r for r in go(nxt)}
        return frozenset(res)

    return set(go(tuple(range(len(cls))))), brute_max(S, F)


def conflicts(i, rem, S, F):
    return sum(1 for j in rem if j != i and not compatible(i, j, S, F))


r = rule_outcomes([(0, 10), (1, 2), (3, 4)], lambda i, rem, S, F: S[i])
check("earliest start: [0,10],[1,2],[3,4] gives 1, optimum 2", r == ({1}, 2), str(r))
r = rule_outcomes([(0, 4), (3, 6), (5, 9)], lambda i, rem, S, F: F[i] - S[i])
check("shortest duration: [0,4],[3,6],[5,9] gives 1, optimum 2", r == ({1}, 2), str(r))
FC = [(0, 10), (20, 30), (40, 50), (60, 70), (28, 42), (7, 23), (8, 22), (9, 21), (47, 63), (48, 62), (49, 61)]
r = rule_outcomes(FC, conflicts)
Sfc = [c[0] for c in FC]; Ffc = [c[1] for c in FC]
cf = [conflicts(i, tuple(range(11)), Sfc, Ffc) for i in range(11)]
check("fewest conflicts: 11 classes, every tie-break gives 3, optimum 4", r == ({3}, 4), str(r))
check("fewest conflicts: the page lists exactly these 11 classes",
      has(TEXT, "take $[0,10]$, $[20,30]$, $[40,50]$, $[60,70]$ (the optimum), $[28,42]$, and three mutually "
          "overlapping classes over each gap, $[7,23]$, $[8,22]$, $[9,21]$ and $[47,63]$, $[48,62]$, $[49,61]$"))
check("trap table rows on the page: earliest start and shortest duration counterexamples",
      has(TEXT, "| earliest start | $[0,10]$, $[1,2]$, $[3,4]$ | 1 | 2 |")
      and has(TEXT, "| shortest duration | $[0,4]$, $[3,6]$, $[5,9]$ | 1 | 2 |"))
check("fewest conflicts: [28,42] is the only class with 2 conflicts (the minimum)",
      cf[4] == 2 and sorted(cf)[:2] == [2, 3] and len(set(Sfc + Ffc)) == 22, str(cf))
check("fewest conflicts: the three gap classes on each side overlap pairwise and [0,10]..[60,70] are disjoint",
      not any(compatible(i, j, Sfc, Ffc) for i, j in itertools.combinations([5, 6, 7], 2))
      and not any(compatible(i, j, Sfc, Ffc) for i, j in itertools.combinations([8, 9, 10], 2))
      and is_schedule([0, 1, 2, 3], Sfc, Ffc))
# weighted
Sw, Fw, Ww = [0, 1], [2, 10], [1, 5]
gw = sum(Ww[i] for i in greedy_schedule(Sw, Fw))
bw = max(sum(Ww[i] for i in X) for r_ in range(3) for X in itertools.combinations(range(2), r_) if is_schedule(X, Sw, Fw))
check("weighted: earliest finish earns 1 credit, optimum 5", gw == 1 and bw == 5)
# endpoint convention
Se, Fe = [1, 3, 5], [3, 5, 7]
touch = max(r_ for r_ in range(4) for X in itertools.combinations(range(3), r_)
            if all(Se[i] >= Fe[j] or Se[j] >= Fe[i] for i, j in itertools.combinations(X, 2)))
check("endpoints: [1,3],[3,5],[5,7] allow 2 strictly, 3 if touching allowed", brute_max(Se, Fe) == 2 and touch == 3)
# concept example
S6 = [2, 1, 3, 5, 6, 8]; F6 = [3, 4, 6, 7, 9, 10]
g6 = greedy_schedule(S6, F6)
check("concept example: greedy takes [2,3],[5,7],[8,10]; max over all 64 subsets is 3",
      F6 == sorted(F6) and [(S6[i], F6[i]) for i in g6] == [(2, 3), (5, 7), (8, 10)] and brute_max(S6, F6) == 3
      and 2 ** 6 == 64)

# =====================================================================================================
print("== 4.4 Huffman codes")


def huffman_cost(f):
    h = list(f); heapq.heapify(h); c = 0
    while len(h) > 1:
        a = heapq.heappop(h); b = heapq.heappop(h); c += a + b; heapq.heappush(h, a + b)
    return c


def huffman_depths(f, rng=None):
    """Huffman with random tie-breaking; returns depth per character."""
    items = [(w, [i]) for i, w in enumerate(f)]
    depth = [0] * len(f)
    while len(items) > 1:
        items.sort(key=lambda t: (t[0], rng.random() if rng else 0))
        (w1, s1), (w2, s2) = items[0], items[1]
        for i in s1 + s2:
            depth[i] += 1
        items = items[2:] + [(w1 + w2, s1 + s2)]
    return depth


def kraft_min(f):
    n = len(f)
    if n == 1:
        return 0
    best = None
    for d in itertools.product(range(1, n + 1), repeat=n):
        if sum(fractions.Fraction(1, 2 ** x) for x in d) <= 1:
            c = sum(a * b for a, b in zip(f, d))
            best = c if best is None or c < best else best
    return best


def all_trees(labels):
    """All full binary trees with these leaves (children unordered)."""
    labels = tuple(labels)
    if len(labels) == 1:
        yield labels[0]
        return
    first, rest = labels[0], labels[1:]
    for k in range(0, len(rest)):
        for left_rest in itertools.combinations(rest, k):
            left = (first,) + left_rest
            right = tuple(x for x in rest if x not in left_rest)
            for a in all_trees(left):
                for b in all_trees(right):
                    yield (a, b)


def tree_depths(t, d=0, out=None):
    out = {} if out is None else out
    if isinstance(t, tuple):
        tree_depths(t[0], d + 1, out); tree_depths(t[1], d + 1, out)
    else:
        out[t] = d
    return out


ok_k = ok_t = True
nin = 0
for n in range(1, 6):
    for f in itertools.combinations_with_replacement(range(1, 6), n):
        if n == 5 and random.random() > 0.15:
            continue
        hc = huffman_cost(f)
        ok_k &= hc == kraft_min(f)
        tmin = min(sum(f[i] * d for i, d in tree_depths(t).items()) for t in all_trees(range(n)))
        ok_t &= hc == tmin
        nin += 1
for _ in range(25):
    f = [random.randint(1, 30) for _ in range(6)]
    hc = huffman_cost(f)
    ok_k &= hc == kraft_min(f)
    ok_t &= hc == min(sum(f[i] * d for i, d in tree_depths(t).items()) for t in all_trees(range(6)))
    nin += 1
check(f"Huffman cost = minimum over all prefix codes (Kraft-feasible lengths), {nin} inputs, n<=6", ok_k)
check("Huffman cost = minimum over all full code trees with labeled leaves", ok_t)

ok = True
for _ in range(400):
    n = random.randint(1, 7)
    f = [random.randint(1, 6) for _ in range(n)]          # many ties
    ok &= len({sum(a * b for a, b in zip(f, huffman_depths(f, random))) for _ in range(5)} | {huffman_cost(f)}) == 1
check("every tie-breaking gives the same Huffman cost = sum of merged frequencies", ok)

ok = True
for _ in range(500):
    n = random.randint(1, 9)
    labels = list(range(n)); random.shuffle(labels)

    def rnd_tree(ls):
        if len(ls) == 1:
            return ls[0]
        k = random.randint(1, len(ls) - 1)
        return (rnd_tree(ls[:k]), rnd_tree(ls[k:]))

    t = rnd_tree(labels)
    f = [random.randint(0, 9) for _ in range(n)]

    def weight_sum(t):
        if not isinstance(t, tuple):
            return f[t], 0
        (wa, sa), (wb, sb) = weight_sum(t[0]), weight_sum(t[1])
        return wa + wb, sa + sb + wa + wb

    ok &= weight_sum(t)[1] == sum(f[i] * d for i, d in tree_depths(t).items())
    # deepest leaf has a leaf sibling
    D = max(tree_depths(t).values())

    def has_deep_pair(t, d=0):
        if not isinstance(t, tuple):
            return False
        if d + 1 == D and not isinstance(t[0], tuple) and not isinstance(t[1], tuple):
            return True
        return has_deep_pair(t[0], d + 1) or has_deep_pair(t[1], d + 1)

    ok &= n == 1 or has_deep_pair(t)
check("cost = sum of internal-node weights; every full tree has two sibling leaves at max depth (500 trees)", ok)

ok = True
for _ in range(300):
    n = random.randint(2, 6)
    f = [random.randint(1, 9) for _ in range(n)]
    trees = list(all_trees(range(n)))
    u, v = random.sample(range(n), 2)
    for t in random.sample(trees, min(5, len(trees))):
        d = tree_depths(t)
        d2 = dict(d); d2[u], d2[v] = d[v], d[u]
        c1 = sum(f[i] * d[i] for i in d); c2 = sum(f[i] * d2[i] for i in d2)
        ok &= c2 - c1 == (d[v] - d[u]) * (f[u] - f[v])
check("Lemma 4.5 swap formula: exchanging u and v changes cost by (depth v - depth u)(f[u] - f[v])", ok)

ok = True
for _ in range(300):
    n = random.randint(2, 6)
    f = [random.randint(1, 6) for _ in range(n)]
    order = sorted(range(n), key=lambda i: f[i])
    x, y = order[0], order[1]
    trees = list(all_trees(range(n)))
    best = min(sum(f[i] * d for i, d in tree_depths(t).items()) for t in trees)

    def deep_sibs(t, D, d=0):
        if not isinstance(t, tuple):
            return False
        if d + 1 == D and {t[0], t[1]} == {x, y}:
            return True
        return deep_sibs(t[0], D, d + 1) or deep_sibs(t[1], D, d + 1)

    ok &= any(sum(f[i] * dd for i, dd in tree_depths(t).items()) == best
              and deep_sibs(t, max(tree_depths(t).values())) for t in trees)
check("Lemma 4.5: some optimal tree has the two least frequent as siblings of max depth (300 inputs)", ok)

ok = True
for _ in range(300):
    n = random.randint(3, 7)
    f = [random.randint(1, 9) for _ in range(n)]
    trs = list(all_trees(range(n))) if n <= 6 else []
    for t in random.sample(trs, min(5, len(trs))):
        def contract(t):
            if isinstance(t, tuple):
                if set(t) == {0, 1}:
                    return "z"
                return (contract(t[0]), contract(t[1]))
            return t
        d = tree_depths(t)
        if d[0] == d[1]:
            c = contract(t)
            dd = tree_depths(c)
            if "z" in dd:
                fz = dict(enumerate(f)); fz["z"] = f[0] + f[1]
                cost_u = sum(f[i] * d[i] for i in d)
                cost_c = sum(fz[k] * dd[k] for k in dd)
                ok &= cost_u == cost_c + f[0] + f[1]
check("Theorem 4.6: cost(U) = cost(U') + f[1] + f[2] when 1, 2 are siblings", ok)


# ---- BuildHuffman transcription
class PQ:
    def __init__(self):
        self.h = []; self.ins = 0; self.ext = 0; self.c = 0

    def insert(self, item, key):
        self.c += 1; self.ins += 1
        heapq.heappush(self.h, (key, self.c, item))

    def extract_min(self):
        self.ext += 1
        if not self.h:
            raise IndexError("ExtractMin on empty queue")
        return heapq.heappop(self.h)[2]


def build_huffman(f1, start_at_n=False):
    """BuildHuffman; f1 is 1-indexed list."""
    n = len(f1) - 1
    f = dict(enumerate(f1)); L = {}; R = {}; P = {}
    Q = PQ()
    for i in range(1, n + 1):
        L[i] = 0; R[i] = 0
        Q.insert(i, f[i])
    first = n if start_at_n else n + 1
    for i in range(first, 2 * n):
        x = Q.extract_min()
        y = Q.extract_min()
        f[i] = f[x] + f[y]
        Q.insert(i, f[i])
        L[i] = x; P[x] = i
        R[i] = y; P[y] = i
    P[2 * n - 1] = 0
    return f, L, R, P, Q


def depths_from_arrays(n, L, R):
    out = {}

    def go(v, d):
        if v <= n:
            out[v] = d
        else:
            go(L[v], d + 1); go(R[v], d + 1)

    go(2 * n - 1, 0)
    return out


ok = True
for _ in range(500):
    n = random.randint(2, 12)
    fl = [None] + [random.randint(1, 20) for _ in range(n)]
    f, L, R, P, Q = build_huffman(fl)
    d = depths_from_arrays(n, L, R)
    ok &= sorted(d) == list(range(1, n + 1)) and sum(fl[i] * d[i] for i in d) == huffman_cost(fl[1:])
    ok &= Q.ins == 2 * n - 1 and Q.ext == 2 * n - 2 and P[2 * n - 1] == 0
    ok &= all(L[i] == 0 and R[i] == 0 for i in range(1, n + 1))
    ok &= all(P[v] > v for v in range(1, 2 * n - 1))
check("BuildHuffman (loop from n+1): optimal tree, 2n-1 Inserts, 2n-2 ExtractMins, root 2n-1 (500 inputs)", ok)
ok = True
for n in range(2, 12):
    fl = [None] + [random.randint(1, 20) for _ in range(n)]
    try:
        f, L, R, P, Q = build_huffman(fl, start_at_n=True)
        ok = False
    except IndexError:
        pass
check("book's loop 'for i <- n to 2n-1' runs one ExtractMin on an empty queue (n = 2..11)", ok)
ok = True
for n in range(2, 12):
    fl = [None] + [random.randint(1, 20) for _ in range(n)]
    Lx_ = {}
    Q = PQ()
    for i in range(1, n + 1):
        Lx_[i] = 0; Q.insert(i, fl[i])
    x = Q.extract_min(); y = Q.extract_min()
    Lx_[n] = x
    ok &= Lx_[n] != 0
check("book's loop: its first iteration makes leaf n an internal node (L[n] != 0)", ok)


# ---- encode / decode transcription
def make_codec(fl):
    n = len(fl) - 1
    f, L, R, P, Q = build_huffman(fl)
    st = {"m": 1, "B": {}}

    def encode_one(x):
        if x < 2 * n - 1:
            encode_one(P[x])
            st["B"][st["m"]] = 0 if x == L[P[x]] else 1
            st["m"] += 1

    def encode(A):
        st["m"] = 1; st["B"] = {}
        for a in A:
            encode_one(a)
        return [st["B"][k] for k in range(1, st["m"])]

    def decode(B):
        out = []
        v = 2 * n - 1
        for b in B:
            v = L[v] if b == 0 else R[v]
            if L[v] == 0:
                out.append(v)
                v = 2 * n - 1
        return out

    return encode, decode, depths_from_arrays(n, L, R)


ok = True
for _ in range(300):
    n = random.randint(2, 10)
    fl = [None] + [random.randint(1, 15) for _ in range(n)]
    enc, dec, d = make_codec(fl)
    A = [random.randint(1, n) for _ in range(random.randint(0, 40))]
    B = enc(A)
    ok &= dec(B) == A and len(B) == sum(d[a] for a in A)
check("HuffmanEncode / HuffmanDecode round-trip; encoded length = sum of depths (300 messages)", ok)

# ---- Sallows
SAL = ("THISSENTENCECONTAINSTHREEASTHREECSTWODSTWENTYSIXESFIVEFST"
       "HREEGSEIGHTHSTHIRTEENISTWOLSSIXTEENNSNINEOSSIXRSTWENTYSEV"
       "ENSSTWENTYTWOTSTWOUSFIVEVSEIGHTWSFOURXSFIVEYSANDONLYONEZ")
sentence = ("This sentence contains three a's, three c's, two d's, twenty-six e's, five f's, three g's, eight h's, "
            "thirteen i's, two l's, sixteen n's, nine o's, six r's, twenty-seven s's, twenty-two t's, two u's, "
            "five v's, eight w's, four x's, five y's, and only one z.")
letters = table_rows(TEXT, "letter")
freqs = [int(x) for x in table_rows(TEXT, "freq")]
depths = [int(x) for x in table_rows(TEXT, "depth")]
FQ = dict(zip(letters, freqs)); DQ = dict(zip(letters, depths))
check("Sallows: page sentence quoted exactly, its letters = the scriptio continua string",
      has(TEXT, sentence) and "".join(c for c in sentence.upper() if c.isalpha()) == SAL)
cnt = {c: SAL.count(c) for c in set(SAL)}
check("Sallows: 170 letters, frequency table = actual letter counts (the sentence is self-describing)",
      len(SAL) == 170 and cnt == FQ and len(letters) == 20)
check("Sallows: Huffman cost 649", huffman_cost(freqs) == 649)
check("Sallows: depth table gives 649 bits and satisfies Kraft with equality (full tree)",
      sum(FQ[c] * DQ[c] for c in letters) == 649 and sum(fractions.Fraction(1, 2 ** DQ[c]) for c in letters) == 1)
check("Sallows: fixed-length code 5 bits x 170 = 850", 2 ** 4 < 20 <= 2 ** 5 and 5 * 170 == 850)
# the book's tree
BOOK = {"A": "101000", "C": "101001", "G": "101010", "D": "1010110", "Z": "1010111", "I": "1011", "T": "100",
        "E": "110", "S": "111", "X": "00000", "L": "000010", "U": "000011", "O": "0001", "F": "00100",
        "V": "00101", "Y": "00110", "R": "00111", "N": "010", "H": "0110", "W": "0111"}
prefix_free = not any(a != b and BOOK[b].startswith(BOOK[a]) for a in BOOK for b in BOOK)
check("book tree: codewords prefix-free, lengths = page depth table", prefix_free
      and all(len(BOOK[c]) == DQ[c] for c in letters))
check("book tree: A = 101000, S = 111 (as on the page)", BOOK["A"] == "101000" and BOOK["S"] == "111"
      and has(TEXT, "A = `101000` and S = `111`"))
check("book tree: THISSE encodes as 100 0110 1011 111 111 110",
      " ".join(BOOK[c] for c in "THISSE") == "100 0110 1011 111 111 110"
      and has(TEXT, "`100 0110 1011 111 111 110` (T H I S S E)"))
check("book tree: the book's longer prefix THISSENTENCECONT matches",
      " ".join(BOOK[c] for c in "THISSENTENCECONT") ==
      "100 0110 1011 111 111 110 010 100 110 010 101001 110 101001 0001 010 100")


def internal_nodes(code, freq):
    """Weights of internal nodes from codewords."""
    w = {}
    for c, s in code.items():
        for k in range(len(s)):
            w[s[:k]] = w.get(s[:k], 0) + freq[c]
    return w


IW = internal_nodes(BOOK, FQ)
check("book tree: 19 internal nodes summing to 649, root 170", len(IW) == 19 and sum(IW.values()) == 649
      and IW[""] == 170)


def is_huffman_tree(code, freq):
    """Some tie-breaking of Huffman builds exactly this tree?"""
    nodes = {}
    for c, s in code.items():
        nodes[s] = freq[c]
    for p, w in internal_nodes(code, freq).items():
        nodes[p] = w

    @functools.lru_cache(maxsize=None)
    def go(cur):
        if len(cur) == 1:
            return True
        vals = sorted(nodes[p] for p in cur)
        two = vals[:2]
        for p in cur:
            if p and p[-1] == "0" and p[:-1] + "1" in cur:
                q = p[:-1] + "1"
                if sorted([nodes[p], nodes[q]]) == two:
                    if go(frozenset(cur - {p, q} | {p[:-1]})):
                        return True
        return False

    return go(frozenset(code.values()))


check("book tree is a Huffman tree (some tie-breaking builds it)", is_huffman_tree(BOOK, FQ))
# merge sequence claims
h = sorted(freqs)
first = h[:2]
rest = sorted(h[2:] + [sum(first)])
check("Sallows merges: Z(1) with a 2 -> 3; then the other two 2s; then the four 3s pair up",
      first == [1, 2] and FQ["Z"] == 1 and sorted(c for c in letters if FQ[c] == 2) == ["D", "L", "U"]
      and rest[:2] == [2, 2] and sorted(rest[2:] + [4])[:4] == [3, 3, 3, 3]
      and sorted(c for c in letters if FQ[c] == 3) == ["A", "C", "G"])
seen = set()
for _ in range(300):
    seen.add(tuple(huffman_depths(freqs, random)))
check("Sallows: different tie-breakings give different codeword lengths, all costing 649",
      len(seen) > 1 and all(sum(a * b for a, b in zip(freqs, d)) == 649 for d in seen), f"{len(seen)} depth vectors")
check("Morse: E is a prefix of I, S, H", all(x.startswith(".") for x in ["..", "...", "...."]))


# ---- Fano-Shannon counterexample
def fano(f):
    f = sorted(f, reverse=True)
    if len(f) == 1:
        return 0, []
    tot = sum(f)
    diffs = [abs(2 * sum(f[:k]) - tot) for k in range(1, len(f))]
    m = min(diffs)
    assert diffs.count(m) == 1
    k = diffs.index(m) + 1
    a, sa = fano(f[:k]); b, sb = fano(f[k:])
    return a + b + tot, [(f[:k], f[k:])] + sa + sb


fc, splits = fano([10, 4, 4, 4, 3])
check("Fano-Shannon on 10,4,4,4,3: splits {10,4}/{4,4,3}, then {4}/{4,3}; cost 57",
      fc == 57 and ([10, 4], [4, 4, 3]) in splits and ([4], [4, 3]) in splits)
check("Huffman on 10,4,4,4,3: merges 7, 8, 15, 25; cost 55 = 7+8+15+25",
      huffman_cost([10, 4, 4, 4, 3]) == 55 == 7 + 8 + 15 + 25 and kraft_min([10, 4, 4, 4, 3]) == 55)

# ---- concept: ABRACADABRA
AB = "ABRACADABRA"
fa = {c: AB.count(c) for c in "ABRCD"}
t1 = {"A": 1, "B": 3, "R": 3, "C": 3, "D": 3}
t2 = {"A": 1, "R": 2, "B": 3, "C": 4, "D": 4}
check("ABRACADABRA: A5 B2 R2 C1 D1; both trees cost 23 = 2+4+6+11 = optimum; fixed 33",
      fa == {"A": 5, "B": 2, "R": 2, "C": 1, "D": 1} and sum(fa[c] * t1[c] for c in fa) == 23
      and sum(fa[c] * t2[c] for c in fa) == 23 and 2 + 4 + 6 + 11 == 23 and huffman_cost(list(fa.values())) == 23
      and 3 * 11 == 33 and 2 ** 2 < 5 <= 2 ** 3)
c1 = {"A": "0", "C": "100", "D": "101", "B": "110", "R": "111"}
c2 = {"A": "0", "R": "10", "B": "110", "C": "1110", "D": "1111"}
check("ABRACADABRA: tree 1 (B+R, CD+BR, A+6) and tree 2 (B+CD, R+4, A+6) are Huffman trees with those lengths",
      all(len(c1[c]) == t1[c] and len(c2[c]) == t2[c] for c in fa)
      and is_huffman_tree(c1, fa) and is_huffman_tree(c2, fa))
check("concept huffman page states 23 and 33 bits", has(CON["huffman-codes"], "$2 + 4 + 6 + 11 = 23$ bits")
      and has(CON["huffman-codes"], "$3\\cdot 11 = 33$ bits"))

# =====================================================================================================
print("== 4.5 stable matching")


def stable(M, HP, DP):
    """M: hospital -> doctor."""
    return not unstable_pairs(M, HP, DP)


def unstable_pairs(M, HP, DP):
    inv = {d: h for h, d in M.items()}
    out = []
    for h in HP:
        for d in HP[h]:
            if HP[h].index(d) < HP[h].index(M[h]) and DP[d].index(h) < DP[d].index(inv[d]):
                out.append((d, h))
    return out


def all_matchings(HP, DP):
    H = sorted(HP)
    for p in itertools.permutations(sorted(DP)):
        yield dict(zip(H, p))


def gale_shapley(HP, DP, pick=None, trace=None):
    """Transcription of GaleShapley (hospitals offer)."""
    Rank = {(a, h): r for a in DP for r, h in enumerate(DP[a], 1)}
    Match = {a: 0 for a in DP}
    Next = {h: 1 for h in HP}
    Free = list(HP)
    offers = 0
    while Free:
        A = Free.pop(pick(len(Free)) if pick else -1)
        a = HP[A][Next[A] - 1]
        Next[A] += 1
        offers += 1
        if Match[a] == 0:
            Match[a] = A
            ev = (A, a, "accept", None)
        elif Rank[(a, A)] < Rank[(a, Match[a])]:
            Free.append(Match[a])
            ev = (A, a, "accept", Match[a])
            Match[a] = A
        else:
            Free.append(A)
            ev = (A, a, "reject", None)
        if trace is not None:
            trace.append((ev, len(Free)))
    return {h: a for a, h in Match.items()}, offers


def random_profile(n):
    H = [chr(65 + i) for i in range(n)]
    D = [chr(113 + i) if n <= 4 else f"d{i}" for i in range(n)]
    HP = {h: random.sample(D, n) for h in H}
    DP = {d: random.sample(H, n) for d in D}
    return HP, DP


def check_profile(HP, DP, runs=3):
    stables = [M for M in all_matchings(HP, DP) if stable(M, HP, DP)]
    feas = {(h, M[h]) for M in stables for h in M}
    best = {h: min((d for (hh, d) in feas if hh == h), key=lambda d: HP[h].index(d)) for h in HP}
    worst = {d: max((h for (h, dd) in feas if dd == d), key=lambda h: DP[d].index(h)) for d in DP}
    res = []
    for k in range(runs):
        M, off = gale_shapley(HP, DP, pick=(lambda m: random.randrange(m)) if k else None)
        res.append((M, off))
    M0 = res[0][0]
    good = all(M == M0 for M, _ in res) and stable(M0, HP, DP)
    good &= all(M0[h] == best[h] for h in HP) and all(worst[M0[h]] == h for h in HP)
    n = len(HP)
    good &= all(off <= n * n and off == sum(HP[h].index(best[h]) + 1 for h in HP) for _, off in res)
    return good, len(stables)


ok = True
nprof = 0
H3, D3 = "ABC", "qrs"
perms3 = ["".join(p) for p in itertools.permutations(D3)]
permsH = ["".join(p) for p in itertools.permutations(H3)]
for hp in itertools.product(perms3, repeat=3):
    for dp in itertools.product(permsH, repeat=3):
        HP = dict(zip(H3, hp)); DP = dict(zip(D3, dp))
        g, _ = check_profile(HP, DP, runs=2)
        ok &= g
        nprof += 1
check(f"Gale-Shapley, all {nprof} profiles with n = 3: stable, = best(A) for all A, = worst(alpha) for all "
      "alpha, same in every order, offers <= n^2 and = sum of ranks of best(A)", ok and nprof == 6 ** 6)
ok = True
for _ in range(400):
    n = random.choice([1, 2, 4, 5])
    HP, DP = random_profile(n)
    g, _ = check_profile(HP, DP, runs=4)
    ok &= g
check("Gale-Shapley, 400 random profiles with n in {1,2,4,5}: same properties", ok)

ok = True
for _ in range(300):
    n = random.randint(2, 5)
    HP, DP = random_profile(n)
    stables = [M for M in all_matchings(HP, DP) if stable(M, HP, DP)]
    feas = {(h, M[h]) for M in stables for h in M}
    tr = []
    gale_shapley(HP, DP, pick=lambda m: random.randrange(m), trace=tr)
    for (A, a, kind, dropped), _ in tr:
        if kind == "reject":
            ok &= (A, a) not in feas
        if dropped is not None:
            ok &= (dropped, a) not in feas
check("Lemma 4.7: every rejection (immediate or dropping) is by a doctor infeasible for that hospital", ok)

ok = True
for n in range(1, 9):
    D = [f"d{i}" for i in range(n)]; H = [f"H{i}" for i in range(n)]
    HP = {h: D[:] for h in H}; DP = {d: H[:] for d in D}
    for _ in range(5):
        M, off = gale_shapley(HP, DP, pick=lambda m: random.randrange(m))
        ok &= off == n * (n + 1) // 2 and all(M[H[k]] == D[k] for k in range(n))
check("identical preference lists: H_k gets d_k after exactly n(n+1)/2 offers in every run (n <= 8)", ok)

# the book's 4 x 4 example
cols = table_row(TEXT, "rank")
rows = [table_row(TEXT, r) for r in ["1st", "2nd", "3rd", "4th"]]
strip = lambda c: c.strip("$")
dnames = [strip(c) for c in cols[:4]]; hnames = [strip(c) for c in cols[5:]]
DP4 = {d: "".join(strip(rows[r][k]) for r in range(4)) for k, d in enumerate(dnames)}
HP4 = {h: "".join(strip(rows[r][5 + k]) for r in range(4)) for k, h in enumerate(hnames)}
check("4x4 table on the page = the book's lists",
      DP4 == {"q": "ABCD", "r": "ADCB", "s": "BACD", "t": "DBCA"}
      and HP4 == {"A": "tsrq", "B": "rtqs", "C": "trsq", "D": "srqt"}, f"{DP4} {HP4}")
ORDER = "ABCDADBCCC"


def run_order(HP, DP, order):
    nxt = {h: 0 for h in HP}; match = {}; steps = []
    for h in order:
        assert h not in match.values()
        d = HP[h][nxt[h]]; nxt[h] += 1
        cur = match.get(d)
        if cur is None:
            match[d] = h; steps.append(f"{h}>{d}")
        elif DP[d].index(h) < DP[d].index(cur):
            match[d] = h; steps.append(f"{h}>{d} drops {cur}")
        else:
            steps.append(f"{h}>{d} rejected")
    free = [h for h in HP if h not in match.values()]
    return {h: d for d, h in match.items()}, steps, free


M4, steps4, free4 = run_order(HP4, DP4, ORDER)
expect = ["A>t", "B>r", "C>t drops A", "D>s", "A>s drops D", "D>r drops B", "B>t drops C", "C>r rejected",
          "C>s rejected", "C>q"]
check("book run: the ten steps as on the page, ending with {As, Bt, Cq, Dr}",
      steps4 == expect and not free4 and M4 == {"A": "s", "B": "t", "C": "q", "D": "r"}
      and has(TEXT, "The result is $\\{As, Bt, Cq, Dr\\}$"), str(steps4))
# exactly one free hospital from step 5 on
nfree = []
nxt = {h: 0 for h in HP4}; match = {}
for k, h in enumerate(ORDER, 1):
    free = [x for x in HP4 if x not in match.values()]
    nfree.append(len(free))
    d = HP4[h][nxt[h]]; nxt[h] += 1
    cur = match.get(d)
    if cur is None or DP4[d].index(h) < DP4[d].index(cur):
        match[d] = h
check("book run: from step 5 on exactly one hospital is free (no more choices)", nfree[4:] == [1] * 6, str(nfree))
check("book run: the matching is stable", stable(M4, HP4, DP4))
stab4 = [M for M in all_matchings(HP4, DP4) if stable(M, HP4, DP4)]
check("book example: {As, Bt, Cq, Dr} is the ONLY stable matching", stab4 == [M4], str(stab4))
alt = {"A": "r", "B": "s", "C": "q", "D": "t"}
check("book error: {Ar, Bs, Cq, Dt} is unstable, its only unstable pair is (q, B)",
      unstable_pairs(alt, HP4, DP4) == [("q", "B")] and HP4["B"].index("q") < HP4["B"].index("s")
      and DP4["q"].index("B") < DP4["q"].index("C"))
check("book example: no doctor and no hospital gets its first choice; C gets its last",
      all(DP4[d][0] != h for h, d in M4.items()) and all(HP4[h][0] != d for h, d in M4.items())
      and HP4["C"][-1] == M4["C"])
Mg, offg = gale_shapley(HP4, DP4)
Md, offd = gale_shapley(DP4, HP4)
check("book example: 10 offers = 2+2+4+2; doctors offering gives the same matching after 9 offers",
      offg == 10 == sum(HP4[h].index(M4[h]) + 1 for h in HP4) and [HP4[h].index(M4[h]) + 1 for h in "ABCD"] == [2, 2, 4, 2]
      and {h: d for d, h in Md.items()} == M4 and offd == 9)
# figure check
figgs = read(os.path.join(FIGS, "a04-gale-shapley.html"))
nums = re.findall(r'fill="var\(--hi\)" style="[^"]*">(\d+)</text>', figgs)
check("figure: steps 1..10 each appear twice (once per panel)", sorted(map(int, nums)) == sorted(list(range(1, 11)) * 2),
      str(sorted(map(int, nums))))
# best offer received
recv = {}
for st in steps4:
    h, rest_ = st.split(">"); d = rest_[0]
    recv.setdefault(d, []).append(h)
check("figure caption: every doctor ends with the best offer she received",
      all(min(recv[d], key=lambda h: DP4[d].index(h)) == {v: k for k, v in M4.items()}[d] for d in recv))

# bad ideas
DP1 = {"q": "ACB", "r": "CAB", "s": "ABC"}; HP1 = {"A": "rqs", "B": "sqr", "C": "qrs"}
check("bad ideas input 1 as printed", has(TEXT, "- doctors: $q\\colon A\\succ C\\succ B$, $\\ r\\colon C\\succ A\\succ B$, "
      "$\\ s\\colon A\\succ B\\succ C$;\n- hospitals: $A\\colon r\\succ q\\succ s$, $\\ B\\colon s\\succ q\\succ r$, "
      "$\\ C\\colon q\\succ r\\succ s$."))
m0 = {"A": "q", "B": "r", "C": "s"}
check("{Aq, Br, Cs} is unstable with unstable pair (r, A)", ("r", "A") in unstable_pairs(m0, HP1, DP1))


def resolve(M, d, h):
    """Match d with h; partners matched together."""
    M = dict(M)
    inv = {dd: hh for hh, dd in M.items()}
    h_old_d = M[h]; d_old_h = inv[d]
    M[h] = d; M[d_old_h] = h_old_d
    return M


seq = [("A", "r"), ("C", "r"), ("C", "q"), ("A", "q")]
M = m0; ok = True; mats = [m0]
for h, d in seq:
    ok &= (d, h) in unstable_pairs(M, HP1, DP1)
    M = resolve(M, d, h); mats.append(M)
fmt = lambda M: "".join(h + M[h] for h in sorted(M))
check("Knuth's cycle: Ar, Cr, Cq, Aq are unstable in turn and lead back to {Aq, Br, Cs}",
      ok and [fmt(m) for m in mats] == ["AqBrCs", "ArBqCs", "AsBqCr", "AsBrCq", "AqBrCs"], str([fmt(m) for m in mats]))


def rounds_protocol(HP, DP):
    match = {}; rounds = 0; log = []
    while len(match) < len(HP):
        rounds += 1
        free_d = [d for d in DP if d not in match]
        offers = {}
        for h in HP:
            if h not in match.values():
                d = min(free_d, key=lambda x: HP[h].index(x))
                offers.setdefault(d, []).append(h)
        before = len(match)
        for d, hs in offers.items():
            match[d] = min(hs, key=lambda x: DP[d].index(x))
            log.append((rounds, d, match[d], sorted(hs)))
        if len(match) == before:
            return None, rounds, log
    return {h: d for d, h in match.items()}, rounds, log


Mr1, r1, _ = rounds_protocol(HP1, DP1)
check("rounds protocol on input 1: {Ar, Bs, Cq} after one round, stable",
      fmt(Mr1) == "ArBsCq" and r1 == 1 and stable(Mr1, HP1, DP1))
DP2 = {"q": "CBA", "r": "ACB", "s": "ABC"}; HP2 = {"A": "qsr", "B": "qrs", "C": "srq"}
check("bad ideas input 2 as printed", has(TEXT, "take doctors $q\\colon C\\succ B\\succ A$, $\\ r\\colon A\\succ C\\succ B$, "
      "$\\ s\\colon A\\succ B\\succ C$ and hospitals $A\\colon q\\succ s\\succ r$, $\\ B\\colon q\\succ r\\succ s$, "
      "$\\ C\\colon s\\succ r\\succ q$"))
Mr2, r2, log2 = rounds_protocol(HP2, DP2)
check("rounds protocol on input 2: q takes B over A, s takes C, round 2 A gets r; {Ar, Bq, Cs} unstable via (s, A)",
      fmt(Mr2) == "ArBqCs" and r2 == 2 and (1, "q", "B", ["A", "B"]) in log2 and (1, "s", "C", ["C"]) in log2
      and (2, "r", "A", ["A"]) in log2 and unstable_pairs(Mr2, HP2, DP2) == [("s", "A")])
ok = True
for hp in itertools.product(perms3, repeat=3):
    for dp in itertools.product(permsH, repeat=3):
        HP = dict(zip(H3, hp)); DP = dict(zip(D3, dp))
        Mx, _, _ = rounds_protocol(HP, DP)
        ok &= Mx is not None
for _ in range(500):
    HP, DP = random_profile(random.randint(1, 6))
    Mx, _, _ = rounds_protocol(HP, DP)
    ok &= Mx is not None
check("rounds protocol matches >= 1 new pair per round, so ends with a matching (all n=3, 500 random)", ok)

# manipulation (Dubins-Freedman)
doctor_gain = False; hospital_gain = False; coalition = None
for hp in itertools.product(perms3, repeat=3):
    for dp in itertools.product(permsH, repeat=3):
        HP = dict(zip(H3, hp)); DP = dict(zip(D3, dp))
        M, _ = gale_shapley(HP, DP)
        inv = {d: h for h, d in M.items()}
        for h in H3:
            for lie in perms3:
                HPx = dict(HP); HPx[h] = lie
                Mx, _ = gale_shapley(HPx, DP)
                if HP[h].index(Mx[h]) < HP[h].index(M[h]):
                    hospital_gain = True
        if not doctor_gain:
            for d in D3:
                for lie in permsH:
                    DPx = dict(DP); DPx[d] = lie
                    Mx, _ = gale_shapley(HP, DPx)
                    invx = {dd: hh for hh, dd in Mx.items()}
                    if DP[d].index(invx[d]) < DP[d].index(inv[d]):
                        doctor_gain = True
check("n = 3, all profiles: a doctor can sometimes gain by lying; a single hospital never can",
      doctor_gain and not hospital_gain)
for _ in range(20000):
    n = 4
    HP, DP = random_profile(n)
    M, _ = gale_shapley(HP, DP)
    hs = random.sample(sorted(HP), 2)
    HPx = dict(HP)
    for h in hs:
        HPx[h] = "".join(random.sample(HP[h], n))
    Mx, _ = gale_shapley(HPx, DP)
    better = [h for h in hs if HP[h].index(Mx[h]) < HP[h].index(M[h])]
    worse = [h for h in hs if HP[h].index(Mx[h]) > HP[h].index(M[h])]
    if better and not worse:
        coalition = (HP, DP, hs)
        break
check("two colluding hospitals can make one of them better off and neither worse off (found, n = 4)",
      coalition is not None)

# concept example (cyclic)
HPc = {"A": "qrs", "B": "rsq", "C": "sqr"}; DPc = {"q": "BCA", "r": "CAB", "s": "ABC"}
Mh, oh = gale_shapley(HPc, DPc)
Md_, od = gale_shapley(DPc, HPc)
Md_ = {h: d for d, h in Md_.items()}
stc = sorted(fmt(M) for M in all_matchings(HPc, DPc) if stable(M, HPc, DPc))
check("concept example: hospitals offering give {Aq, Br, Cs} after 3 offers (hospitals 1st, doctors last)",
      fmt(Mh) == "AqBrCs" and oh == 3 and all(HPc[h][0] == Mh[h] for h in HPc)
      and all(DPc[d][-1] == h for h, d in Mh.items()))
check("concept example: doctors offering give {As, Bq, Cr}; exactly 3 stable matchings, third {Ar, Bs, Cq} = "
      "everyone's 2nd choice",
      fmt(Md_) == "AsBqCr" and stc == ["AqBrCs", "ArBsCq", "AsBqCr"]
      and all(HPc[h][1] == d and DPc[d][1] == h for h, d in {"A": "r", "B": "s", "C": "q"}.items()))

# =====================================================================================================
print("== concept: knapsack example")
W = 10
items = {"a": (6, 9), "b": (5, 5), "c": (5, 5)}
order = sorted(items, key=lambda k: -fractions.Fraction(items[k][1], items[k][0]))
cap = W; val = 0
for k in order:
    if items[k][0] <= cap:
        cap -= items[k][0]; val += items[k][1]
best01 = max(sum(items[k][1] for k in S) for r_ in range(4) for S in itertools.combinations(items, r_)
             if sum(items[k][0] for k in S) <= W)


def frac_greedy(items, W):
    cap = fractions.Fraction(W); v = fractions.Fraction(0)
    for k in sorted(items, key=lambda k: -fractions.Fraction(items[k][1], items[k][0])):
        take = min(cap, items[k][0])
        v += fractions.Fraction(items[k][1]) * take / items[k][0]; cap -= take
    return v


def frac_opt(items, W):
    """LP optimum via vertices: one fractional item."""
    best = fractions.Fraction(0); ks = list(items)
    for r_ in range(len(ks) + 1):
        for S in itertools.combinations(ks, r_):
            w = sum(items[k][0] for k in S)
            if w > W:
                continue
            v = fractions.Fraction(sum(items[k][1] for k in S))
            best = max(best, v)
            for j in ks:
                if j not in S:
                    v2 = v + fractions.Fraction(items[j][1]) * min(1, fractions.Fraction(W - w, items[j][0]))
                    best = max(best, v2)
    return best


check("knapsack: ratio greedy 0/1 gets 9, optimum 10 (b + c)", order[0] == "a" and val == 9 and best01 == 10)
check("knapsack: fractional greedy a + 4/5 b = 13 = LP optimum", frac_greedy(items, W) == 13 == frac_opt(items, W)
      and 9 + fractions.Fraction(4, 5) * 5 == 13)
ok = True
for _ in range(500):
    m = random.randint(1, 5)
    its = {i: (random.randint(1, 9), random.randint(1, 9)) for i in range(m)}
    Wr = random.randint(1, 20)
    ok &= frac_greedy(its, Wr) == frac_opt(its, Wr)
check("fractional knapsack: greedy by value/weight = LP optimum on 500 random instances", ok)

# =====================================================================================================
print("== page text")
check("BuildHuffman on the page starts its loop at n + 1", has(TEXT, "for i ← n + 1 to 2n − 1"))
check("GreedySchedule test is strict (S[i] > F[X[count]])", has(TEXT, "if S[i] > F[X[count]]"))
check("Lemma 4.2 swap formula on the page", has(TEXT, "L[b]\\,F[a] - L[a]\\,F[b]"))
check("Huffman trap numbers 57 and 55 on the page", has(TEXT, "cost $57$") and has(TEXT, "$7 + 8 + 15 + 25 = 55$"))
check("page: 649 and 850 bits", has(TEXT, "= 649$ bits") and has(TEXT, "850 bits"))
check("page: n(n+1)/2 offers and 2+2+4+2 = 10", has(TEXT, "$n(n+1)/2$ offers") and has(TEXT, "$2 + 2 + 4 + 2 = 10$"))
bad = [w for w in ["clearly", "obviously", "trivially"] if re.search(r"\b" + w + r"\b", TEXT.split("> [!exam]")[0], re.I)]
check("no 'clearly/obviously/trivially' in the page body", not bad, str(bad))

# =====================================================================================================
print()
if FAIL:
    print(f"{len(FAIL)} FAILED:", *FAIL, sep="\n  ")
    sys.exit(1)
print("ALL OK")
