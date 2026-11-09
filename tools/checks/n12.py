#!/usr/bin/env python3
"""Checks for content/4-lecture-notes/12-lower-bounds.md (Erickson, Director's Cut 12, Lower Bounds) and the concept
page content/concepts/comparison-lower-bounds.md.

The decision trees on the page (guess-the-animal, the dictionary tree for the first eight primes, insertion sort on
three elements) are encoded and run on every input; information-theoretic bounds and Stirling's bound are computed
exactly; the optimal worst-case number of comparisons for sorting and for the maximum is computed by exhaustive
minimax search over comparison trees (states = sets of permutations consistent with the answers so far); the
maximum adversary is played against every comparison sequence that is too short; mergesort's worst case is counted
on all permutations."""
import itertools
import math
import os
import random
from functools import lru_cache

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
PAGE = os.path.join(ROOT, "content", "4-lecture-notes", "12-lower-bounds.md")
CONCEPT = os.path.join(ROOT, "content", "concepts", "comparison-lower-bounds.md")
FAIL = []
random.seed(12)


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAIL.append(name)


def clg(x):
    """ceil(lg x) for a positive integer x, exactly."""
    return (x - 1).bit_length()


# =====================================================================================================
# 12.2 decision trees
ANIMALS = {  # name: (lives in water, has scales, more than four legs, has wings)
    "fish": (1, 1, 0, 0), "frog": (1, 0, 0, 0), "fly": (0, 0, 1, 1), "spider": (0, 0, 1, 0), "gnu": (0, 0, 0, 0),
    "eagle": (0, 0, 0, 1)}
TREE = ("water", ("scales", "fish", "frog"),
        ("legs", ("wings", "fly", "spider"), ("wings", "eagle", "gnu")))
Q = {"water": 0, "scales": 1, "legs": 2, "wings": 3}


def run(tree, a):
    d = 0
    while not isinstance(tree, str):
        q, yes, no = tree
        tree = yes if ANIMALS[a][Q[q]] else no
        d += 1
    return tree, d


res = {a: run(TREE, a) for a in ANIMALS}
check("12.2 the animal tree identifies all six animals", all(res[a][0] == a for a in ANIMALS))
check("12.2 T(frog) = 2 queries; worst case (depth) 3", res["frog"][1] == 2 and max(d for _, d in res.values()) == 3)

PRIMES = [2, 3, 5, 7, 11, 13, 17, 19]
# decision tree for the dictionary problem: internal ('<', k, yes, no); pre-leaf ('=', i): x == A[i] ? i : none
DT = ("<", 11, ("<", 5, ("<", 3, ("=", 1), ("=", 2)), ("<", 7, ("=", 3), ("=", 4))),
      ("<", 17, ("<", 13, ("=", 5), ("=", 6)), ("<", 19, ("=", 7), ("=", 8))))


def dict_run(t, x):
    d = 0
    while t[0] == "<":
        t = t[2] if x < t[1] else t[3]
        d += 1
    d += 1
    return (t[1] if x == PRIMES[t[1] - 1] else 0), d


ok = True
depths = set()
for x2 in range(0, 46):
    x = x2 / 2
    want = PRIMES.index(x) + 1 if x in PRIMES else 0
    got, d = dict_run(DT, x)
    ok &= got == want
    depths.add(d)
check("12.2 the dictionary tree for the first eight primes returns the right index or 'none' for every x in 0..22.5",
      ok)
check("12.2 every root-to-leaf path asks 4 queries; the tree has 16 leaves (8 indices, 8 'none')",
      depths == {4} and 2 ** 4 == 16)
check("12.3 dictionary: n + 1 = 9 outputs need depth >= ceil(lg 9) = 4 — the tree is optimal", clg(9) == 4)
check("12.3 ceil(log_k (n+1)) for n = 8: k = 2 gives 4, k = 3 gives 2",
      math.ceil(math.log(9, 2)) == 4 and math.ceil(math.log(9, 3) - 1e-12) == 2)


# =====================================================================================================
# 12.5 sorting: information-theoretic bound, Stirling
LGF = [clg(math.factorial(n)) for n in range(0, 17)]
check("12.5 ceil(lg n!) for n = 1..12: 0 1 3 5 7 10 13 16 19 22 26 29",
      LGF[1:13] == [0, 1, 3, 5, 7, 10, 13, 16, 19, 22, 26, 29], f"{LGF[1:13]}")
check("12.5 n! > (n/e)^n for n = 1..300", all(math.lgamma(n + 1) > n * (math.log(n) - 1) for n in range(1, 301)))
check("12.5 n! = (n/e)^n sqrt(2 pi n)(1 + Theta(1/n)): n * (ratio - 1) -> 1/12",
      all(abs(n * (math.exp(math.lgamma(n + 1) - n * (math.log(n) - 1) - 0.5 * math.log(2 * math.pi * n)) - 1)
              - 1 / 12) < 0.01 for n in (100, 1000, 10000)))
check("12.5 lg n! >= n lg n - n lg e for n = 1..300",
      all(math.lgamma(n + 1) / math.log(2) >= n * math.log2(n) - n * math.log2(math.e) for n in range(1, 301)))
check("12.5 lg n! / (n lg n) -> 1 (0.9 at n = 10^6)", 0.9 < math.lgamma(10 ** 6 + 1) / math.log(2) / (10 ** 6 * math.log2(10 ** 6)) < 1)


# mergesort (the book's Merge), comparisons counted
def merge_sort(A, cnt):
    if len(A) <= 1:
        return A
    m = len(A) // 2
    L, R = merge_sort(A[:m], cnt), merge_sort(A[m:], cnt)
    out, i, j = [], 0, 0
    while i < len(L) and j < len(R):
        cnt[0] += 1
        if L[i] < R[j]:
            out.append(L[i])
            i += 1
        else:
            out.append(R[j])
            j += 1
    return out + L[i:] + R[j:]


def ms_worst_formula(n):
    k = clg(n)
    return n * k - 2 ** k + 1


MSW = {}
for n in range(1, 9):
    worst = 0
    for p in itertools.permutations(range(n)):
        c = [0]
        assert merge_sort(list(p), c) == list(range(n))
        worst = max(worst, c[0])
    MSW[n] = worst
check("12.5 mergesort's worst case on all permutations, n <= 8, equals n ceil(lg n) - 2^ceil(lg n) + 1",
      all(MSW[n] == ms_worst_formula(n) for n in MSW), f"{MSW}")
def ms_worst_rec(n):  # W(n) = W(ceil n/2) + W(floor n/2) + n - 1
    return 0 if n <= 1 else ms_worst_rec((n + 1) // 2) + ms_worst_rec(n // 2) + n - 1


check("12.5 the closed form agrees with the recurrence W(n) = W(ceil(n/2)) + W(floor(n/2)) + n - 1, n <= 2000",
      all(ms_worst_rec(n) == ms_worst_formula(n) for n in range(1, 2001)))
check("12.5 table: n = 4, 5, 8, 12, 16: ceil(lg n!) = 5, 7, 16, 29, 45 and mergesort's worst case 5, 8, 17, 33, 49",
      [LGF[n] for n in (4, 5, 8, 12, 16)] == [5, 7, 16, 29, 45]
      and [ms_worst_formula(n) for n in (4, 5, 8, 12, 16)] == [5, 8, 17, 33, 49])


# --------------------------------------------------------------------------------- exhaustive comparison-tree search
class CompGame:
    """Minimum worst-case number of comparisons x_i : x_j to determine answer(p), where the input is a permutation
    p (x_i = p[i]); states are bitmasks of consistent permutations."""

    def __init__(self, n, answer):
        self.n = n
        self.perms = list(itertools.permutations(range(n)))
        self.full = (1 << len(self.perms)) - 1
        self.lt = {}
        for i in range(n):
            for j in range(i + 1, n):
                m = 0
                for k, p in enumerate(self.perms):
                    if p[i] < p[j]:
                        m |= 1 << k
                self.lt[(i, j)] = m
        self.classes = {}
        for k, p in enumerate(self.perms):
            self.classes.setdefault(answer(p), 0)
            self.classes[answer(p)] |= 1 << k
        self.cls = list(self.classes.values())
        self.memo = {}

    def nclasses(self, S):
        return sum(1 for c in self.cls if c & S)

    def value(self, S=None):
        if S is None:
            S = self.full
        if S in self.memo:
            return self.memo[S]
        k = self.nclasses(S)
        if k <= 1:
            self.memo[S] = 0
            return 0
        lb = clg(k)
        best = math.inf
        for (i, j), m in self.lt.items():
            a, b = S & m, S & ~m
            if not a or not b:
                continue
            v = 1 + max(self.value(a), self.value(b))
            if v < best:
                best = v
                if best <= lb:
                    break
        self.memo[S] = best
        return best


sort_vals = {}
for n in range(1, 6):
    g = CompGame(n, lambda p: p)
    sort_vals[n] = g.value()
check("12.5 exhaustive search: the best comparison tree sorts n = 1..5 elements in exactly ceil(lg n!) = 0 1 3 5 7 "
      "comparisons", [sort_vals[n] for n in range(1, 6)] == [LGF[n] for n in range(1, 6)], f"{sort_vals}")
check("concept example: 5 elements need ceil(lg 120) = 7 comparisons, 7 suffice, mergesort needs 8",
      sort_vals[5] == 7 and clg(120) == 7 and MSW[5] == 8)


# insertion sort on three elements: the comparison tree drawn on the page
def insertion_trace(p):
    A = list(range(3))  # indices, sorted prefix grows
    trace = []
    srt = [0]
    for i in (1, 2):
        pos = len(srt)
        while pos > 0:
            j = srt[pos - 1]
            less = p[i] < p[j]
            trace.append((min(i, j), max(i, j), (p[min(i, j)] < p[max(i, j)])))
            if less:
                pos -= 1
            else:
                break
        srt.insert(pos, i)
    return trace, tuple(srt)


traces = {p: insertion_trace(p) for p in itertools.permutations(range(3))}
leaves = {tuple(t): out for t, out in traces.values()}
check("figure: insertion sort's comparison tree on 3 elements has 6 leaves, depth 3, two leaves at depth 2",
      len(leaves) == 6 and max(len(t) for t in leaves) == 3 and sum(1 for t in leaves if len(t) == 2) == 2)
expected = {  # path (i, j, x_i < x_j) -> sorted order of indices (1-based in the figure)
    ((0, 1, True), (1, 2, True)): "123", ((0, 1, True), (1, 2, False), (0, 2, True)): "132",
    ((0, 1, True), (1, 2, False), (0, 2, False)): "312", ((0, 1, False), (0, 2, True)): "213",
    ((0, 1, False), (0, 2, False), (1, 2, True)): "231", ((0, 1, False), (0, 2, False), (1, 2, False)): "321"}
check("figure: the six root-to-leaf paths and leaf labels as drawn",
      {t: "".join(str(i + 1) for i in out) for t, out in leaves.items()} == expected)
for p, (t, out) in traces.items():
    assert [p[i] for i in out] == sorted(p)


# =====================================================================================================
# 12.6 maximum
max_vals = {}
for n in range(1, 8):
    g = CompGame(n, lambda p: p.index(max(p)))
    max_vals[n] = g.value()
check("12.6 exhaustive search: finding the maximum needs exactly n - 1 comparisons, n = 1..7",
      all(max_vals[n] == n - 1 for n in max_vals), f"{max_vals}")
check("12.6 information-theoretic bound for the maximum is only ceil(lg n) (n = 7: 3 < 6)", clg(7) == 3)
ok = True
for n in range(1, 9):
    for p in itertools.permutations(range(n)) if n <= 7 else []:
        m = p.index(max(p))
        q = 0
        idx = 0
        for b in range(clg(n)):     # 'is bit b of the index of the maximum 1?'
            q += 1
            if (m >> b) & 1:
                idx |= 1 << b
        ok &= idx == m and q == clg(n)
check("12.6 ceil(lg n) 'unreasonable' yes/no questions (bits of the index) find the maximum, n <= 7", ok)


def scan_max(p, cnt):
    best = 0
    for i in range(1, len(p)):
        cnt[0] += 1
        if p[i] > p[best]:
            best = i
    return best


check("12.6 the linear scan uses exactly n - 1 comparisons and is correct (all permutations, n <= 7)",
      all(scan_max(p, c := [0]) == p.index(max(p)) and c[0] == len(p) - 1
          for n in range(1, 8) for p in itertools.permutations(range(n))))

# the adversary: pretend x_i = i; mark the smaller element of every comparison
ok_unmarked = ok_consistent = True
count = 0
for n in range(2, 7):
    pairs = [(i, j) for i in range(1, n + 1) for j in range(i + 1, n + 1)]
    for L in range(0, n - 1):  # fewer than n - 1 comparisons
        for seq in itertools.product(pairs, repeat=L):
            count += 1
            marked = {min(i, j) for i, j in seq}  # x_i = i: the smaller index loses
            if n in marked:
                ok_unmarked = False
            cand = [k for k in range(1, n) if k not in marked]
            if not cand:
                ok_unmarked = False
                continue
            k = cand[0]
            x = {i: i for i in range(1, n + 1)}
            x[k] = n + 1
            # every answered comparison keeps its outcome
            ok_consistent &= all((x[i] < x[j]) == (i < j) for i, j in seq)
            ok_consistent &= max(x, key=x.get) == k != n
check(f"12.6 adversary x_i = i vs all {count} comparison sequences of length < n - 1 (n = 2..6): x_n never marked, "
      "some x_k (k != n) unmarked", ok_unmarked)
check("12.6 ... raising that x_k to n + 1 is consistent with every answer and moves the maximum from x_n to x_k",
      ok_consistent)

# =====================================================================================================
# concept page: what the bound does not cover — counting sort beats it on small integers (no comparisons)
def counting_sort(A, K):
    C = [0] * K
    for a in A:
        C[a] += 1
    out = []
    for v in range(K):
        out += [v] * C[v]
    return out


check("concept: counting sort sorts integers in 0..K-1 with no comparisons at all (random tests)",
      all(counting_sort(A, 10) == sorted(A) for A in ([random.randrange(10) for _ in range(random.randint(0, 50))]
                                                      for _ in range(500))))

def insertion_count(p):
    A, c = list(p), 0
    for i in range(1, len(A)):
        j = i
        while j > 0:
            c += 1
            if A[j - 1] > A[j]:
                A[j - 1], A[j] = A[j], A[j - 1]
                j -= 1
            else:
                break
    return c


check("concept: insertion sort makes n - 1 comparisons on sorted input (n <= 50)",
      all(insertion_count(range(n)) == max(n - 1, 0) for n in range(0, 51)))
check("concept: k lg(n/k) <= lg C(n, k) <= k lg(e n / k) for 1 <= k <= n <= 200",
      all(k * math.log2(n / k) <= math.log2(math.comb(n, k)) + 1e-9 <= k * math.log2(math.e * n / k) + 2e-9
          for n in range(1, 201) for k in range(1, n + 1)))

# page text
for path, frags in ((PAGE, ["| 5 | 7 | 16 | 29 | 45 |", "| 5 | 8 | 17 | 33 | 49 |", r"\lceil\lg 9\rceil = 4",
                            "$0, 1, 3, 5, 7$", "55,400", r"n\lceil\lg n\rceil - 2^{\lceil\lg n\rceil} + 1"]),
                    (CONCEPT, [r"\lceil\lg 120\rceil = 7", "8"])):
    if os.path.exists(path):
        txt = open(path, encoding="utf-8").read()
        for f in frags:
            check(f"{os.path.basename(path)} mentions {f}", f in txt)
    else:
        print(f"({os.path.basename(path)} not written yet)")

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: {FAIL}")
