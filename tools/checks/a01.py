#!/usr/bin/env python3
"""Checks for every concrete claim on content/2-algorithms/01-recursion.md and on the concept pages
recursion, divide-and-conquer, recursion-trees and linear-time-selection.

Every algorithm is implemented exactly as the page's pseudocode states it (1-indexed subarrays A[lo..hi]),
then compared with brute force / Python built-ins on all small inputs and many random ones. Move counts,
multiplication counts and comparison counts are counted by instrumenting the code; recurrence solutions are
checked numerically (exact closed forms where the page states one, otherwise the ratio to the claimed bound
must settle)."""
import itertools
import math
import os
import random
import sys
from collections import deque
from fractions import Fraction
from functools import lru_cache

sys.setrecursionlimit(100000)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

FAIL = []


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAIL.append(name)


rng = random.Random(374)
INF = float("inf")


def small_arrays(maxlen, alphabet=(1, 2, 3)):
    """All arrays over a small alphabet (duplicates included) up to length maxlen."""
    for n in range(0, maxlen + 1):
        for t in itertools.product(alphabet, repeat=n):
            yield list(t)


def lg(x):
    return math.log2(x)


def settles(f, g, ns, tol=0.06):
    """f(n)/g(n) is bounded away from 0 and infinity and its last values change by < tol (relative)."""
    rs = [f(n) / g(n) for n in ns]
    tail = rs[-4:]
    ok = all(r > 0 for r in rs) and (max(tail) - min(tail)) / max(tail) < tol
    return ok, rs


# =====================================================================================================
# 1.2  PeasantMultiply
# =====================================================================================================
def peasant_multiply(x, y, calls):
    calls[0] += 1
    if x == 0:
        return 0
    x2, y2 = x // 2, y + y
    prod = peasant_multiply(x2, y2, calls)
    if x % 2 == 1:
        prod = prod + y
    return prod


ok, depth_ok = True, True
for x in range(0, 300):
    for y in range(0, 60):
        c = [0]
        ok &= peasant_multiply(x, y, c) == x * y
        depth_ok &= c[0] == (x.bit_length() + 1)
check("PeasantMultiply(x, y) = x*y for 0 <= x < 300, 0 <= y < 60", ok)
check("PeasantMultiply makes (number of bits of x) + 1 calls (x halves each time)", depth_ok)

# =====================================================================================================
# 1.3  Tower of Hanoi
# =====================================================================================================
def hanoi(n, src, dst, tmp, moves):
    if n > 0:
        hanoi(n - 1, src, tmp, dst, moves)
        moves.append((n, src, dst))
        hanoi(n - 1, tmp, dst, src, moves)


def simulate(n, moves):
    pegs = {0: list(range(n, 0, -1)), 1: [], 2: []}
    for disk, s, d in moves:
        if not pegs[s] or pegs[s][-1] != disk:
            return False
        if pegs[d] and pegs[d][-1] < disk:
            return False
        pegs[d].append(pegs[s].pop())
    return pegs[2] == list(range(n, 0, -1)) and not pegs[0] and not pegs[1]


ok = True
for n in range(0, 17):
    mv = []
    hanoi(n, 0, 2, 1, mv)
    ok &= simulate(n, mv) and len(mv) == 2 ** n - 1
check("Hanoi(n,0,2,1) is legal, solves the puzzle, and makes exactly 2^n - 1 moves, n = 0..16", ok)
T = [0]
for n in range(1, 70):
    T.append(2 * T[-1] + 1)
check("T(0) = 0, T(n) = 2T(n-1) + 1 has closed form 2^n - 1 (n < 70)", all(T[n] == 2 ** n - 1 for n in range(70)))
check("2^64 - 1 = 18,446,744,073,709,551,615", 2 ** 64 - 1 == 18446744073709551615)
years = (2 ** 64 - 1) / (365.25 * 24 * 3600)
check("2^64 - 1 seconds is about 585 billion years", 584e9 < years < 586e9, f"{years:.4e}")


def hanoi_bfs(n):
    """Shortest solution length by breadth-first search over all 3^n configurations."""
    start = tuple([0] * n)
    goal = tuple([2] * n)
    dist = {start: 0}
    q = deque([start])
    while q:
        s = q.popleft()
        if s == goal:
            return dist[s]
        tops = {}
        for disk in range(n):          # disk 0 is the smallest
            tops.setdefault(s[disk], disk)
        for p, disk in tops.items():
            for p2 in range(3):
                if p2 != p and (p2 not in tops or tops[p2] > disk):
                    t = list(s)
                    t[disk] = p2
                    t = tuple(t)
                    if t not in dist:
                        dist[t] = dist[s] + 1
                        q.append(t)


check("no solution is shorter: BFS over all 3^n configurations gives 2^n - 1, n = 1..8",
      all(hanoi_bfs(n) == 2 ** n - 1 for n in range(1, 9)))
# figure a01-hanoi: n = 4, phases of 7, 1, 7 moves
mv = []
hanoi(4, 0, 2, 1, mv)
check("figure: n = 4 splits into 7 + 1 + 7 = 15 moves; move 8 is disk 4 from src to dst",
      len(mv) == 15 and mv[7] == (4, 0, 2) and all(d < 4 for d, _, _ in mv[:7] + mv[8:]))
# after phase 1 the three small disks sit on tmp
pegs = {0: [4, 3, 2, 1], 1: [], 2: []}
for d, s, t in mv[:7]:
    pegs[t].append(pegs[s].pop())
check("figure: after the first recursive call, disks 1-3 are on tmp and disk 4 alone on src",
      pegs == {0: [4], 1: [3, 2, 1], 2: []})

# =====================================================================================================
# 1.4  Merge and MergeSort (the book's pseudocode, Figure 1.6), on A[lo..hi] (0-based inclusive)
# =====================================================================================================
CMP = [0]


def merge(A, lo, hi, m):
    """Merge(A[1..n], m): the subarray A[lo..hi] plays A[1..n]; A[lo..lo+m-1] and A[lo+m..hi] are sorted."""
    n = hi - lo + 1
    B = [None] * (n + 1)
    i, j = 1, m + 1
    for k in range(1, n + 1):
        if j > n:
            B[k] = A[lo + i - 1]; i += 1
        elif i > m:
            B[k] = A[lo + j - 1]; j += 1
        else:
            CMP[0] += 1
            if A[lo + i - 1] < A[lo + j - 1]:
                B[k] = A[lo + i - 1]; i += 1
            else:
                B[k] = A[lo + j - 1]; j += 1
    for k in range(1, n + 1):
        A[lo + k - 1] = B[k]


def merge_sort(A, lo=0, hi=None, trace=None):
    if hi is None:
        hi = len(A) - 1
    n = hi - lo + 1
    if n > 1:
        m = n // 2
        merge_sort(A, lo, lo + m - 1)
        if trace is not None:
            trace.append(list(A))
        merge_sort(A, lo + m, hi)
        if trace is not None:
            trace.append(list(A))
        merge(A, lo, hi, m)


ok = True
for A in small_arrays(8):
    B = list(A)
    merge_sort(B)
    ok &= B == sorted(A)
check("MergeSort sorts every array over {1,2,3} of length <= 8", ok)
ok = True
for _ in range(400):
    A = [rng.randint(-50, 50) for _ in range(rng.randint(0, 300))]
    B = list(A)
    merge_sort(B)
    ok &= B == sorted(A)
check("MergeSort sorts 400 random arrays of length <= 300", ok)
# Lemma 1.1 directly: merge of two sorted halves, every split point, every pair of sorted arrays
ok, cmp_ok = True, True
for A in small_arrays(7):
    n = len(A)
    for m in range(0, n + 1):
        L, R = sorted(A[:m]), sorted(A[m:])
        C = L + R
        CMP[0] = 0
        merge(C, 0, n - 1, m)
        ok &= C == sorted(A)
        cmp_ok &= CMP[0] <= max(n - 1, 0)
check("Lemma 1.1: Merge(A, m) merges any two sorted halves (all splits, length <= 7)", ok)
check("Merge makes at most n - 1 comparisons", cmp_ok)
# the book's example (Figure 1.5)
tr = []
A = list("SORTINGEXAMPL")
merge_sort(A, trace=tr)
check("mergesort example: divide SORTIN | GEXAMPL, left -> INORST, right -> AEGLMPX, merge -> AEGILMNOPRSTX",
      "".join(tr[-2]) == "INORSTGEXAMPL" and "".join(tr[-1]) == "INORSTAEGLMPX" and "".join(A) == "AEGILMNOPRSTX",
      f"{''.join(tr[-2])} / {''.join(tr[-1])} / {''.join(A)}")
# with ties Merge takes the right element first: not stable
C = [(1, "a"), (1, "b")]
# compare by key only
class K:
    def __init__(s, k, t): s.k, s.t = k, t
    def __lt__(s, o): return s.k < o.k
C = [K(1, "a"), K(1, "b")]
merge(C, 0, 1, 1)
check("Merge with '<' puts the right copy of a tie first (so this MergeSort is not stable)", [c.t for c in C] == ["b", "a"])


# recurrence T(n) = T(ceil(n/2)) + T(floor(n/2)) + n
@lru_cache(None)
def T_ms(n):
    return 0 if n <= 1 else T_ms((n + 1) // 2) + T_ms(n // 2) + n


ok, rs = settles(T_ms, lambda n: n * lg(n), [2 ** k + 3 for k in range(10, 22)] + [10 ** 6, 3 * 10 ** 6, 5 * 10 ** 6, 10 ** 7])
check("T(n) = T(ceil n/2) + T(floor n/2) + n is Theta(n log n) (ratio to n lg n -> 1)", ok and abs(rs[-1] - 1) < 0.05,
      f"{rs[0]:.3f} ... {rs[-1]:.3f}")
check("for n = 2^k it is exactly n lg n", all(T_ms(2 ** k) == k * 2 ** k for k in range(25)))


# trap: any split point is correct; split m = 1 is quadratic, a constant-fraction split (n/3) is still n log n
def merge_sort_split(A, lo, hi, split, work):
    n = hi - lo + 1
    if n > 1:
        m = split(n)
        merge_sort_split(A, lo, lo + m - 1, split, work)
        merge_sort_split(A, lo + m, hi, split, work)
        merge(A, lo, hi, m)
        work[0] += n                     # Merge's loop runs n times


ok = True
for A in small_arrays(7):
    for sp in (lambda n: 1, lambda n: n - 1, lambda n: max(1, n // 3)):
        B = list(A)
        merge_sort_split(B, 0, len(B) - 1, sp, [0])
        ok &= B == sorted(A)
check("MergeSort with split m = 1, m = n-1 or m = floor(n/3) still sorts (all arrays over {1,2,3}, length <= 7)", ok)
w1 = []
for n in (200, 400, 800):
    w = [0]
    merge_sort_split(list(range(n)), 0, n - 1, lambda n: 1, w)
    w1.append(w[0])
check("split m = 1: Merge work sum_{k=2}^n k = n(n+1)/2 - 1 = Theta(n^2)",
      w1 == [n * (n + 1) // 2 - 1 for n in (200, 400, 800)], str(w1))
w3 = []
for k in range(10, 17):
    n = 2 ** k
    w = [0]
    merge_sort_split(list(range(n)), 0, n - 1, lambda n: max(1, n // 3), w)
    w3.append(w[0] / (n * lg(n)))
check("split m = floor(n/3): Merge work / (n lg n) settles (Theta(n log n))",
      (max(w3[-3:]) - min(w3[-3:])) / max(w3[-3:]) < 0.06, f"{w3[0]:.3f} ... {w3[-1]:.3f}")

# =====================================================================================================
# 1.5  Partition (Lomuto) and QuickSort (Figure 1.8)
# =====================================================================================================
def partition(A, lo, hi, p, inv=None):
    """Partition(A[1..n], p) on the subarray A[lo..hi]; p is 1-based within the subarray. Returns r (1-based)."""
    n = hi - lo + 1
    a = lambda t: lo + t - 1          # 1-based index -> list index
    A[a(p)], A[a(n)] = A[a(n)], A[a(p)]
    l = 0
    for i in range(1, n):
        CMP[0] += 1
        if A[a(i)] < A[a(n)]:
            l += 1
            A[a(l)], A[a(i)] = A[a(i)], A[a(l)]
        if inv is not None:   # loop invariant: A[1..l] < pivot, A[l+1..i] >= pivot
            piv = A[a(n)]
            inv[0] &= all(A[a(t)] < piv for t in range(1, l + 1)) and all(A[a(t)] >= piv for t in range(l + 1, i + 1))
    A[a(n)], A[a(l + 1)] = A[a(l + 1)], A[a(n)]
    return l + 1


def quick_sort(A, lo=0, hi=None, choose=lambda A, lo, hi: hi - lo + 1, inv=None):
    if hi is None:
        hi = len(A) - 1
    n = hi - lo + 1
    if n > 1:
        p = choose(A, lo, hi)
        r = partition(A, lo, hi, p, inv)
        quick_sort(A, lo, lo + r - 2, choose, inv)
        quick_sort(A, lo + r, hi, choose, inv)


first = lambda A, lo, hi: 1
last = lambda A, lo, hi: hi - lo + 1
rand = lambda A, lo, hi: rng.randint(1, hi - lo + 1)


def med3(A, lo, hi):
    n = hi - lo + 1
    idx = [1, (n + 1) // 2, n]
    idx.sort(key=lambda t: (A[lo + t - 1], t))
    return idx[1]


ok, inv = True, [True]
for A in small_arrays(8):
    for ch in (first, last, rand, med3):
        B = list(A)
        quick_sort(B, choose=ch, inv=inv)
        ok &= B == sorted(A)
check("QuickSort (first, last, random, median-of-3 pivots) sorts every array over {1,2,3}, length <= 8", ok)
check("Partition loop invariant holds after every iteration: A[1..l] < pivot <= A[l+1..i]", inv[0])
ok = True
for _ in range(300):
    A = [rng.randint(-40, 40) for _ in range(rng.randint(0, 300))]
    for ch in (rand, med3):
        B = list(A)
        quick_sort(B, choose=ch)
        ok &= B == sorted(A)
check("QuickSort sorts 300 random arrays of length <= 300", ok)
# partition postcondition on all permutations / pivots
ok = True
for n in range(1, 8):
    for P in itertools.permutations(range(n)):
        for p in range(1, n + 1):
            B = list(P)
            piv = B[p - 1]
            r = partition(B, 0, n - 1, p)
            ok &= B[r - 1] == piv and all(x < piv for x in B[:r - 1]) and all(x > piv for x in B[r:]) and r == piv + 1
check("Partition returns the pivot's rank r and leaves smaller | pivot | larger (all permutations, n <= 7)", ok)
# the book's example: pivot P (index 12 of SORTINGEXAMPL)
A = list("SORTINGEXAMPL")
r = partition(A, 0, 12, 12)
check("Lomuto Partition of SORTINGEXAMPL around P gives OINGEAML P RTSX, r = 9", "".join(A) == "OINGEAMLPRTSX" and r == 9,
      "".join(A))
check("(the book's Figure 1.7 row AGOEINLMPTXSR is a different, also valid, partition)",
      sorted("AGOEINLM") == sorted("OINGEAMLP".replace("P", "")) and "AGOEINLMPTXSR" != "".join(A))
quick_sort(A, 0, 7)
s1 = "".join(A)
quick_sort(A, 9, 12)
check("then recursing left gives AEGILMNO P RTSX and right gives AEGILMNOPRSTX",
      s1 == "AEGILMNOPRTSX" and "".join(A) == "AEGILMNOPRSTX", s1)
# worst case: last-element pivot on sorted input -> n(n-1)/2 comparisons
ok = True
for n in range(1, 120):
    CMP[0] = 0
    quick_sort(list(range(n)), choose=last)
    ok &= CMP[0] == n * (n - 1) // 2
check("last-element pivot on sorted input: exactly n(n-1)/2 comparisons (r = n every time)", ok)
ok = True
for n in range(1, 120):
    CMP[0] = 0
    quick_sort(list(range(n)), choose=first)
    ok &= CMP[0] == n * (n - 1) // 2
check("first-element pivot on sorted input: also n(n-1)/2 comparisons", ok)
# median of three: rank in [2, n-1]
ok = True
for n in range(3, 9):
    for P in itertools.permutations(range(1, n + 1)):
        piv = P[med3(list(P), 0, n - 1) - 1]
        ok &= 2 <= piv <= n - 1
check("median-of-three pivot always has rank between 2 and n-1 (all permutations, 3 <= n <= 8)", ok)
ok = any(P[med3(list(P), 0, 7) - 1] == 2 for P in itertools.permutations(range(1, 9)))
check("... and rank 2 does occur", ok)


def m3_killer(P):
    """True if median-of-3 QuickSort (book's Partition) picks rank 2 or n-1 in every call of size >= 4."""
    A = list(P)
    good = [True]

    def qs(lo, hi):
        n = hi - lo + 1
        if n > 1:
            p = med3(A, lo, hi)
            piv = A[lo + p - 1]
            rank = sum(x < piv for x in A[lo:hi + 1]) + 1
            if n >= 4 and rank not in (2, n - 1):
                good[0] = False
            r = partition(A, lo, hi, p)
            qs(lo, lo + r - 2)
            qs(lo + r, hi)
    qs(0, len(A) - 1)
    return good[0]


check("median of three: for every n = 4..8 some input forces rank 2 or n-1 in every call of size >= 4",
      all(any(m3_killer(P) for P in itertools.permutations(range(n))) for n in range(4, 9)))
# recurrences
@lru_cache(None)
def T_lin(n):  # T(n) = T(n-1) + n
    return 0 if n <= 0 else T_lin(n - 1) + n


@lru_cache(None)
def T_m3(n):   # T(n) = T(1) + T(n-2) + n
    return 1 if n <= 2 else T_m3(1) + T_m3(n - 2) + n


check("T(n) = T(n-1) + n = n(n+1)/2 = Theta(n^2)", all(T_lin(n) == n * (n + 1) // 2 for n in range(2000)))
ok, rs = settles(T_m3, lambda n: n * n, list(range(1000, 5001, 400)))
check("T(n) = T(1) + T(n-2) + n is Theta(n^2) (ratio to n^2 -> 1/4)", ok and abs(rs[-1] - 0.25) < 0.01, f"{rs[-1]:.4f}")


@lru_cache(None)
def T_med(n):  # median pivot: T(ceil(n/2)-1) + T(floor(n/2)) + n
    return 0 if n <= 1 else T_med((n + 1) // 2 - 1) + T_med(n // 2) + n


ok, rs = settles(T_med, lambda n: n * lg(n), [2 ** k for k in range(12, 24)])
check("median pivot: T(ceil(n/2) - 1) + T(floor(n/2)) + n = Theta(n log n)", ok, f"{rs[-1]:.3f}")


@lru_cache(None)
def T_1090(n):  # pivot rank n/10: T(floor(n/10)) + T(n - 1 - floor(n/10)) + n
    return 0 if n <= 1 else T_1090(n // 10) + T_1090(n - 1 - n // 10) + n


ok, rs = settles(T_1090, lambda n: n * lg(n), [2 ** k for k in range(10, 17)], tol=0.08)
check("pivot rank always ~n/10: T(n/10) + T(9n/10) + n = Theta(n log n)", ok and rs[-1] < 2.5, f"{rs[0]:.3f} ... {rs[-1]:.3f}")

# =====================================================================================================
# 1.7  Recursion trees
# =====================================================================================================
def level_sums(n, branches, f, depth):
    """branches: list of fractions (subproblem size = frac * size); f: work function. Level sums of the tree."""
    level = [n]
    sums = []
    for _ in range(depth):
        sums.append(sum(f(x) for x in level))
        level = [b * x for x in level for b in branches]
    return sums


N = Fraction(2 ** 20)
ms = level_sums(N, [Fraction(1, 2)] * 2, lambda x: x, 6)
check("mergesort tree 2T(n/2) + n: every level sums to n", all(s == N for s in ms))
ks = level_sums(N, [Fraction(1, 2)] * 3, lambda x: x, 6)
check("Karatsuba tree 3T(n/2) + n: level i sums to (3/2)^i n", all(ks[i] == Fraction(3, 2) ** i * N for i in range(6)))
mo = level_sums(N, [Fraction(1, 5), Fraction(7, 10)], lambda x: x, 6)
check("MomSelect tree T(n/5) + T(7n/10) + n: level i sums to (9/10)^i n",
      all(mo[i] == Fraction(9, 10) ** i * N for i in range(6)))
check("MomSelect tree level 2 nodes: n/25, 7n/50, 7n/50, 49n/100",
      sorted([a * b for a in (Fraction(1, 5), Fraction(7, 10)) for b in (Fraction(1, 5), Fraction(7, 10))])
      == [Fraction(1, 25), Fraction(7, 50), Fraction(7, 50), Fraction(49, 100)])
s4 = level_sums(N, [Fraction(1, 2)] * 4, lambda x: x, 6)
check("SplitMultiply tree 4T(n/2) + n: level i sums to 2^i n", all(s4[i] == 2 ** i * N for i in range(6)))
sq = level_sums(N, [Fraction(1, 2)] * 2, lambda x: x * x, 6)
check("tree 2T(n/2) + n^2: level i sums to n^2 / 2^i", all(sq[i] == N * N / 2 ** i for i in range(6)))
th = level_sums(N, [Fraction(1, 3), Fraction(2, 3)], lambda x: x, 6)
check("tree T(n/3) + T(2n/3) + n: full levels sum to n", all(s == N for s in th))
# leaves r^L = n^(log_c r)
ok = all(abs(r ** (math.log(n) / math.log(c)) - n ** (math.log(r) / math.log(c))) / n ** (math.log(r) / math.log(c)) < 1e-9
         for r in (2, 3, 4, 7) for c in (2, 3, 4) for n in (10, 1000, 10 ** 6))
check("number of leaves r^(log_c n) = n^(log_c r)", ok)


def solve(rec, ns):
    memo = {}

    def T(n):
        if n not in memo:
            memo[n] = rec(T, n)
        return memo[n]
    for n in sorted(ns):       # fill bottom-up-ish to keep recursion shallow
        for m in range(1, n + 1, max(1, n // 200)):
            T(m)
    return T


examples = [
    # name, recurrence, bound, sample ns
    ("2T(n/2) + n = Theta(n log n)", lambda T, n: 1 if n <= 1 else 2 * T(n // 2) + n, lambda n: n * lg(n)),
    ("3T(n/2) + n = Theta(n^lg3)", lambda T, n: 1 if n <= 1 else 3 * T(n // 2) + n, lambda n: n ** lg(3)),
    ("4T(n/2) + n = Theta(n^2)", lambda T, n: 1 if n <= 1 else 4 * T(n // 2) + n, lambda n: n ** 2),
    ("2T(n/2) + n^2 = Theta(n^2)", lambda T, n: 1 if n <= 1 else 2 * T(n // 2) + n * n, lambda n: n ** 2),
    ("T(n/2) + 1 = Theta(log n)", lambda T, n: 1 if n <= 1 else T(n // 2) + 1, lambda n: lg(n)),
    ("T(n/5) + T(7n/10) + n = Theta(n)", lambda T, n: 1 if n <= 25 else T(-(-n // 5)) + T(7 * n // 10) + n, lambda n: n),
    ("T(n/3) + T(2n/3) + n = Theta(n log n)", lambda T, n: 1 if n <= 2 else T(n // 3) + T(n - n // 3) + n, lambda n: n * lg(n)),
    ("T(n/7) + T(5n/7) + n = Theta(n)", lambda T, n: 1 if n <= 49 else T(-(-n // 7)) + T(5 * n // 7) + n, lambda n: n),
    ("7T(n/2) + n^2 = Theta(n^lg7)", lambda T, n: 1 if n <= 1 else 7 * T(n // 2) + n * n, lambda n: n ** lg(7)),
    ("2T(n/2) + n lg n = Theta(n log^2 n)", lambda T, n: 1 if n <= 1 else 2 * T(n // 2) + n * lg(n), lambda n: n * lg(n) ** 2),
]
for name, rec, bound in examples:
    memo = {}

    def T(n, rec=rec, memo=memo):
        if n not in memo:
            memo[n] = rec(T, n)
        return memo[n]
    ns = [2 ** k for k in range(16, 41, 3)]
    rs = [T(n) / bound(n) for n in ns]
    tail = rs[-3:]
    ok = (max(tail) - min(tail)) / max(tail) < 0.06
    check("recursion-tree solution " + name, ok, " ".join(f"{r:.3f}" for r in rs[-3:]))

# exact closed forms quoted on the pages
def T_kara(n):
    return 1 if n == 1 else 3 * T_kara(n // 2) + n


check("3T(n/2) + n, T(1) = 1: T(2^k) = 3^(k+1) - 2^(k+1)",
      all(T_kara(2 ** k) == 3 ** (k + 1) - 2 ** (k + 1) for k in range(30)))
check("7T(n/2) + n^2, T(1) = 1: T(2^k) = (7^(k+1) - 4^(k+1))/3",
      all((lambda k: (lambda f: f(f, 2 ** k))(lambda f, n: 1 if n == 1 else 7 * f(f, n // 2) + n * n))(k)
          == (7 ** (k + 1) - 4 ** (k + 1)) // 3 for k in range(30)))
check("lg 7 = 2.807...", f"{lg(7):.3f}" == "2.807")


def T_8(n):
    return 1 if n == 1 else 8 * T_8(n // 2) + n * n


check("8T(n/2) + n^2, T(1) = 1: T(2^k) = 2n^3 - n^2 = Theta(n^3)",
      all(T_8(2 ** k) == 2 * 8 ** k - 4 ** k for k in range(25)))
# 2T(n/2) + n lg n: level i sums to n (lg n - i)
check("2T(n/2) + n lg n: level i sums to n(lg n - i), total n lg n (lg n + 1)/2 for n = 2^k (leaves cost 0)",
      all((lambda k: (lambda f: f(f, 2 ** k))(lambda f, n: 0 if n == 1 else 2 * f(f, n // 2) + n * (n.bit_length() - 1)))(k)
          == 2 ** k * k * (k + 1) // 2 for k in range(30)))
# T(n/3) + T(2n/3) + n: depth log_{3/2} n, full levels log_3 n
for n in (3 ** 8, 10 ** 5):
    sizes = [Fraction(n)]
    full, d = 0, 0
    while sizes:
        if len(sizes) == 2 ** d:
            full = d
        sizes = [s * b for s in sizes for b in (Fraction(1, 3), Fraction(2, 3)) if s * b >= 1]
        d += 1
    check(f"T(n/3)+T(2n/3) tree for n = {n}: depth ~ log_(3/2) n, full levels ~ log_3 n",
          abs(d - math.log(n, 1.5)) <= 2 and abs(full - math.log(n, 3)) <= 2,
          f"depth {d} vs {math.log(n, 1.5):.1f}, full {full} vs {math.log(n, 3):.1f}")


# domain transformation: T(x) = 2T(x/2 + 1) + x (reals), S(x) = T(x + 2) satisfies S(x) = 2S(x/2) + x + 2
@lru_cache(None)
def Tr(x):
    return 1.0 if x <= 4 else 2 * Tr(x / 2 + 1) + x


ok = all(abs(Tr(x + 2) - (2 * Tr(x / 2 + 2) + x + 2)) < 1e-6 * Tr(x + 2) for x in (10.0, 37.5, 1000.0, 123456.0))
check("domain transformation: alpha = 2 turns T(n) <= 2T(n/2 + 1) + n into S(n) <= 2S(n/2) + n + 2", ok)
ok, rs = settles(Tr, lambda n: n * lg(n), [2.0 ** k for k in range(12, 40, 3)])
check("... and T(n) = 2T(n/2 + 1) + n is Theta(n log n)", ok, f"{rs[-1]:.3f}")
check("T(ceil n/2) + T(floor n/2) + n <= 2T(ceil n/2) + n (T is nondecreasing)",
      all(T_ms(n) <= 2 * T_ms((n + 1) // 2) + n for n in range(1, 5000)) and all(T_ms(n) <= T_ms(n + 1) for n in range(1, 5000)))

# =====================================================================================================
# 1.8  QuickSelect and MomSelect (Figures 1.12 and the MomSelect box)
# =====================================================================================================
def quick_select(A, k, lo=0, hi=None, choose=rand):
    if hi is None:
        hi = len(A) - 1
    n = hi - lo + 1
    if n == 1:
        return A[lo]
    p = choose(A, lo, hi)
    r = partition(A, lo, hi, p)
    if k < r:
        return quick_select(A, k, lo, lo + r - 2, choose)
    elif k > r:
        return quick_select(A, k - r, lo + r, hi, choose)
    return A[lo + r - 1]


ok = True
for A in small_arrays(7):
    for k in range(1, len(A) + 1):
        for ch in (first, last, rand, med3):
            ok &= quick_select(list(A), k, choose=ch) == sorted(A)[k - 1]
check("QuickSelect(A, k) returns the k-th smallest for every array over {1,2,3}, length <= 7, every k, 4 pivot rules", ok)
ok = True
for _ in range(300):
    A = [rng.randint(-1000, 1000) for _ in range(rng.randint(1, 400))]
    k = rng.randint(1, len(A))
    ok &= quick_select(list(A), k) == sorted(A)[k - 1]
check("QuickSelect on 300 random arrays", ok)
# worst case n(n-1)/2 comparisons with a bad pivot rule
CMP[0] = 0
quick_select(list(range(200)), 200, choose=first)
check("QuickSelect with first-element pivot on sorted input, k = n: n(n-1)/2 comparisons (Theta(n^2))",
      CMP[0] == 200 * 199 // 2, str(CMP[0]))

SECOND = []   # (n, m, size of the second recursive call)
MOMS = []     # (n, m, #smaller than mom, #larger than mom) for distinct inputs


def median_of_five(block):
    return sorted(block)[2]


def mom_select(A, k, lo=0, hi=None, record=True, base=25):
    if hi is None:
        hi = len(A) - 1
    n = hi - lo + 1
    if n <= base:
        return sorted(A[lo:hi + 1])[k - 1]
    m = -(-n // 5)
    M = []
    for i in range(1, m + 1):
        blk = A[lo + 5 * i - 5: min(lo + 5 * i, hi + 1)]
        blk = blk + [INF] * (5 - len(blk))
        M.append(median_of_five(blk))
    mom = mom_select(M, m // 2, record=False, base=base)
    p = A[lo:hi + 1].index(mom) + 1           # Partition needs mom's position
    if record:
        sub = A[lo:hi + 1]
        MOMS.append((n, m, sum(x < mom for x in sub), sum(x > mom for x in sub)))
    r = partition(A, lo, hi, p)
    if k < r:
        if record:
            SECOND.append((n, m, r - 1))
        return mom_select(A, k, lo, lo + r - 2, record, base)
    elif k > r:
        if record:
            SECOND.append((n, m, n - r))
        return mom_select(A, k - r, lo + r, hi, record, base)
    return mom


ok = True
for _ in range(400):
    n = rng.randint(1, 600)
    A = [rng.randint(-5, 5) if rng.random() < 0.3 else rng.randint(-10 ** 6, 10 ** 6) for _ in range(n)]
    k = rng.randint(1, n)
    ok &= mom_select(list(A), k) == sorted(A)[k - 1]
check("MomSelect(A, k) = k-th smallest on 400 random arrays (with duplicates), n <= 600", ok)
ok = True
for n in range(26, 80):
    A = list(range(n))
    rng.shuffle(A)
    for k in range(1, n + 1):
        ok &= mom_select(list(A), k) == k - 1
check("MomSelect correct for every k on random permutations, n = 26..79", ok)
ok = True
for base in (5, 9):          # smaller brute-force thresholds still work (k = floor(m/2) >= 1 needs m >= 2)
    for _ in range(100):
        n = rng.randint(1, 300)
        A = [rng.randint(0, 10 ** 4) for _ in range(n)]
        k = rng.randint(1, n)
        ok &= mom_select(list(A), k, base=base) == sorted(A)[k - 1]
check("MomSelect also correct with brute-force threshold 5 or 9 (m >= 2 so floor(m/2) >= 1)", ok)
check("threshold n <= 5 is the smallest that works: with n = 5, m = 1 and floor(m/2) = 0 is not a valid rank",
      (-(-5 // 5)) // 2 == 0 and (-(-6 // 5)) // 2 == 1)
# guarantees, distinct inputs: smaller >= 3 floor(m/2) - 1, larger >= 3 ceil(m/2) - 1, second call <= n - 3 floor(m/2)
SECOND.clear(); MOMS.clear()
for _ in range(1500):
    n = rng.randint(26, 2000)
    A = rng.sample(range(10 ** 7), n)
    mom_select(A, rng.randint(1, n))
ok1 = all(s >= 3 * (m // 2) - 1 and l >= 3 * (m - m // 2) - 1 for n, m, s, l in MOMS)
check("distinct inputs: at least 3*floor(m/2) - 1 elements < mom and 3*ceil(m/2) - 1 > mom (random runs)", ok1, f"{len(MOMS)} pivots")
ok2 = all(sz <= n - 3 * (m // 2) for n, m, sz in SECOND)
check("distinct inputs: second recursive call has at most n - 3*floor(m/2) elements", ok2, f"{len(SECOND)} calls")
check("n - 3*floor(ceil(n/5)/2) <= 7n/10 + 3/2 for all 26 <= n <= 10^5",
      all(n - 3 * ((-(-n // 5)) // 2) <= Fraction(7 * n, 10) + Fraction(3, 2) for n in range(26, 10 ** 5)))
check("... and = 7n/10 when n is a multiple of 10 (e.g. n = 50: 35)",
      all(n - 3 * ((n // 5) // 2) == 7 * n // 10 for n in range(30, 10 ** 4, 10)))


# a tight input: elements < mom are exactly the guaranteed ones
def tight_input(m):
    """Blocks whose arrangement makes exactly 3*floor(m/2) - 1 elements smaller than mom (n = 5m)."""
    h = m // 2
    small = list(range(1, 3 * h))            # 3h - 1 small values
    mom = 3 * h
    big = list(range(3 * h + 1, 5 * m + 1))
    blocks = []
    si, bi = 0, 0
    for c in range(m):
        if c < h - 1:
            blk = small[si:si + 3] + big[bi:bi + 2]; si += 3; bi += 2
        elif c == h - 1:
            blk = small[si:si + 2] + [mom] + big[bi:bi + 2]; si += 2; bi += 2
        else:
            blk = big[bi:bi + 5]; bi += 5
        blocks.append(blk)
    return [x for b in blocks for x in b], mom


A, mom = tight_input(10)
SECOND.clear(); MOMS.clear()
mom_select(list(A), 50)
check("tight example n = 50: mom = 15, exactly 14 elements below it, so k > 15 recurses on 35 = 7n/10 elements",
      MOMS[0][:3] == (50, 10, 14) and SECOND[0] == (50, 10, 35), f"{MOMS[0]} {SECOND[0]}")
# duplicates break the bound with a two-way partition
SECOND.clear()
mom_select([7] * 200, 200)
check("all-equal input: Lomuto Partition puts everything right of the pivot, second call has n - 1 elements",
      SECOND[0] == (200, 40, 199))
# ... so without distinct elements the Theta(n) bound fails: comparisons per element grow with n
eq_ratio = []
for n in (100, 200, 400, 800):
    CMP[0] = 0
    mom_select([7] * n, n, record=False)
    eq_ratio.append(CMP[0] / n)
check("all-equal input, k = n: MomSelect's comparisons per element keep growing (not O(n); distinctness needed)",
      all(b > 1.8 * a for a, b in zip(eq_ratio, eq_ratio[1:])), " ".join(f"{r:.0f}" for r in eq_ratio))


# median of 5 elements needs exactly 6 comparisons in the worst case (adaptive decision tree, exhaustive)
PERMS5 = list(itertools.permutations(range(5)))


@lru_cache(None)
def need(S):
    """Fewest comparisons that determine the median's position for every permutation in S (worst case)."""
    if len({p.index(2) for p in S}) == 1:
        return 0
    best = 99
    for i in range(5):
        for j in range(i + 1, 5):
            lo = frozenset(p for p in S if p[i] < p[j])
            hi = S - lo
            if not lo or not hi:
                continue
            best = min(best, 1 + max(need(lo), need(hi)))
            if best == 1:
                return 1
    return best


check("selecting the median of 5 needs (and can be done with) 6 comparisons in the worst case",
      need(frozenset(PERMS5)) == 6)
check("6n/5 + 2n/5 = 8n/5 and (8n/5) * sum (9/10)^i = 16n",
      Fraction(6, 5) + Fraction(2, 5) == Fraction(8, 5) and Fraction(8, 5) * 10 == 16)
check("partitioning after the call: n - 1 - 3n/10 - 3n/10 ~ 2n/5 comparisons", Fraction(1) - Fraction(6, 10) == Fraction(2, 5))


@lru_cache(None)
def T16(x):
    return 0.0 if x < 1 else T16(x / 5) + T16(7 * x / 10) + 8 * x / 5


rs = [T16(float(10 ** k)) / 10 ** k for k in range(2, 13, 2)]
check("T(n) <= T(n/5) + T(7n/10) + 8n/5 stays below 16n (and approaches it)",
      all(r < 16 for r in rs) and rs == sorted(rs) and rs[-1] > 15.5,
      " ".join(f"{r:.2f}" for r in rs))
# group sizes g: fractions 1/g + (3g-1)/(4g) = (3g+3)/(4g)
for g, frac in ((3, Fraction(1)), (5, Fraction(9, 10)), (7, Fraction(6, 7))):
    check(f"blocks of {g}: subproblems n/{g} and {Fraction(3 * g - 1, 4 * g)}n, level-sum ratio {frac}",
          Fraction(1, g) + Fraction(3 * g - 1, 4 * g) == frac)
check("blocks of 3 keep at least (2/3)... i.e. second call <= 2n/3; blocks of 5: 7n/10; blocks of 7: 5n/7",
      Fraction(3 * 3 - 1, 12) == Fraction(2, 3) and Fraction(14, 20) == Fraction(7, 10) and Fraction(20, 28) == Fraction(5, 7))
# blocks of 3 really cost Theta(n log n): Mom3Select-style recurrence with exact integer sizes
memo3 = {}


def T3(n):
    if n <= 9:
        return n
    if n not in memo3:
        m = -(-n // 3)
        memo3[n] = T3(m) + T3(n - 2 * (m // 2)) + n
    return memo3[n]


rs = [T3(3 ** k) / (3 ** k * lg(3 ** k)) for k in range(8, 20)]
check("blocks of 3: T(n) = T(n/3) + T(n - 2 floor(m/2)) + n grows like n log n (ratio to n lg n settles)",
      (max(rs[-3:]) - min(rs[-3:])) / max(rs[-3:]) < 0.06, f"{rs[-1]:.3f}")

# randomized quickselect: expected comparisons for the median <= 4n
NMAX = 160
E = [[0.0] * (NMAX + 2) for _ in range(NMAX + 2)]
for n in range(2, NMAX + 1):
    for k in range(1, n + 1):
        s = 0.0
        for r in range(1, n + 1):
            if k < r:
                s += E[r - 1][k]
            elif k > r:
                s += E[n - r][k - r]
        E[n][k] = (n - 1) + s / n
check(f"random pivot: expected comparisons to find the median <= 4n (exact, n <= {NMAX}); even max over k <= 3.4n",
      all(E[n][(n + 1) // 2] <= 4 * n for n in range(1, NMAX + 1)) and all(max(E[n][1:n + 1]) <= 3.4 * n for n in range(2, NMAX + 1)),
      f"E[{NMAX}][median]/n = {E[NMAX][(NMAX + 1) // 2] / NMAX:.3f}")

# the grid figure (a01-mom-grid)
try:
    import figs_a01 as F
    G = F.MOM_GRID   # list of 10 columns, each 5 values top (small) to bottom (large)
    cols = G
    meds = [c[2] for c in cols]
    vals = sorted(v for c in cols for v in c)
    gmom = sorted(meds)[len(meds) // 2 - 1]
    check("grid figure: the 50 values are 1..50, columns sorted, columns ordered by median",
          vals == list(range(1, 51)) and all(c == sorted(c) for c in cols) and meds == sorted(meds))
    check("grid figure: mom (5th smallest of 10 medians) = 15, in column 5 row 3", gmom == 15 and cols[4][2] == 15)
    below = [cols[c][r] for c in range(4) for r in range(3)] + [cols[4][0], cols[4][1]]
    above = [cols[c][r] for c in range(5, 10) for r in range(2, 5)] + [cols[4][3], cols[4][4]]
    check("grid figure: the 14 shaded top-left cells are < mom, the 17 shaded bottom-right cells are > mom",
          len(below) == 14 and all(v < 15 for v in below) and len(above) == 17 and all(v > 15 for v in above))
    check("grid figure: so k > 15 recurses on 35 elements, k < 15 on at most 50 - 17 - 1 = 32",
          sum(v > 15 for v in vals) == 35 and 50 - 17 - 1 == 32)
    flat = [x for c in F.MOM_INPUT_BLOCKS for x in c]
    SECOND.clear(); MOMS.clear()
    res = mom_select(list(flat), 40)
    check("grid figure: MomSelect on the figure's input (blocks in input order) picks mom = 15 and returns the 40th smallest",
          res == 40 and MOMS[0][:3] == (50, 10, 14) and SECOND[0] == (50, 10, 35))
    check("grid figure: input blocks are a reordering of the grid's columns (same sets)",
          sorted(sorted(b) for b in F.MOM_INPUT_BLOCKS) == sorted(cols))
except ImportError as e:
    check("figs_a01 importable for the grid checks", False, str(e))

# =====================================================================================================
# 1.9  SplitMultiply and FastMultiply (Karatsuba)
# =====================================================================================================
MUL = [0]
VIOL = [0]


def split(x, m):
    """x = 10^m a + b, splitting the absolute value (a and b get the sign of x)."""
    s = -1 if x < 0 else 1
    q, r = divmod(abs(x), 10 ** m)
    return s * q, s * r


def split_multiply(x, y, n):
    if abs(x) >= 10 ** n or abs(y) >= 10 ** n:
        VIOL[0] += 1
    if n == 1:
        MUL[0] += 1
        return x * y
    m = -(-n // 2)
    a, b = split(x, m)
    c, d = split(y, m)
    e = split_multiply(a, c, m)
    f = split_multiply(b, d, m)
    g = split_multiply(b, c, m)
    h = split_multiply(a, d, m)
    return 10 ** (2 * m) * e + 10 ** m * (g + h) + f


def fast_multiply(x, y, n, splitter=split):
    if abs(x) >= 10 ** n or abs(y) >= 10 ** n:
        VIOL[0] += 1
    if n == 1:
        MUL[0] += 1
        return x * y
    m = -(-n // 2)
    a, b = splitter(x, m)
    c, d = splitter(y, m)
    e = fast_multiply(a, c, m, splitter)
    f = fast_multiply(b, d, m, splitter)
    g = fast_multiply(a - b, c - d, m, splitter)
    return 10 ** (2 * m) * e + 10 ** m * (e + f - g) + f


ok = True
VIOL[0] = 0
for x in range(0, 1000, 7):
    for y in range(0, 1000, 3):
        ok &= split_multiply(x, y, 3) == x * y and fast_multiply(x, y, 3) == x * y
check("SplitMultiply and FastMultiply correct for 3-digit inputs (sampled grid)", ok)
ok = True
for _ in range(300):
    n = rng.randint(1, 70)
    x, y = rng.randrange(10 ** n), rng.randrange(10 ** n)
    ok &= fast_multiply(x, y, n) == x * y and (n > 30 or split_multiply(x, y, n) == x * y)
check("both correct on 300 random n-digit pairs, n <= 70 (n not a power of 2 included)", ok)
check("every recursive call gets numbers of at most its digit count, even for a - b and c - d (signs split off)",
      VIOL[0] == 0, f"{VIOL[0]} violations")
ok = True
for _ in range(2000):
    a, b, c, d = (rng.randint(-10 ** 6, 10 ** 6) for _ in range(4))
    ok &= a * c + b * d - (a - b) * (c - d) == b * c + a * d
    ok &= (10 ** 3 * a + b) * (10 ** 3 * c + d) == 10 ** 6 * a * c + 10 ** 3 * (b * c + a * d) + b * d
check("identities (10^m a + b)(10^m c + d) = 10^2m ac + 10^m (bc + ad) + bd and ac + bd - (a - b)(c - d) = bc + ad", ok)


def floor_split(x, m):
    return x // 10 ** m, x % 10 ** m


VIOL[0] = 0
ok = True
for _ in range(300):
    n = rng.randint(2, 40)
    x, y = rng.randrange(10 ** n), rng.randrange(10 ** n)
    ok &= fast_multiply(x, y, n, floor_split) == x * y
check("(with floor division on negatives the product is still right, but inputs can outgrow their digit count)",
      ok and VIOL[0] > 0, f"{VIOL[0]} oversized calls")
# single-digit multiplication counts for n = 2^k
ok = True
for k in range(0, 9):
    n = 2 ** k
    x, y = rng.randrange(10 ** n), rng.randrange(10 ** n)
    MUL[0] = 0
    fast_multiply(x, y, n)
    c3 = MUL[0]
    MUL[0] = 0
    if k <= 6:
        split_multiply(x, y, n)
        ok &= MUL[0] == 4 ** k == n * n
    ok &= c3 == 3 ** k
check("n = 2^k digits: SplitMultiply does 4^k = n^2 one-digit products, FastMultiply 3^k = n^lg3", ok)
check("n = 1024: 1,048,576 versus 59,049 one-digit products", 4 ** 10 == 1048576 and 3 ** 10 == 59049)
check("lg 3 = 1.58496...", f"{lg(3):.5f}" == "1.58496")


@lru_cache(None)
def T4(n):
    return 1 if n == 1 else 4 * T4(-(-n // 2)) + n


@lru_cache(None)
def T3k(n):
    return 1 if n == 1 else 3 * T3k(-(-n // 2)) + n


ok4, r4 = settles(T4, lambda n: n * n, [2 ** k for k in range(10, 40, 3)])
ok3, r3 = settles(T3k, lambda n: n ** lg(3), [2 ** k for k in range(10, 40, 3)])
check("T(n) = 4T(ceil n/2) + n = Theta(n^2) and 3T(ceil n/2) + n = Theta(n^lg3)", ok4 and ok3, f"{r4[-1]:.3f}, {r3[-1]:.3f}")
check("Toom-Cook: (2k-1) T(n/k) + n gives exponent log_k(2k-1) < 1 + 1/lg k, k = 2..10",
      all(math.log(2 * k - 1, k) < 1 + 1 / lg(k) for k in range(2, 11)))

# =====================================================================================================
# 1.10  Exponentiation
# =====================================================================================================
def slow_power(a, n, cnt):
    x = a
    for _ in range(2, n + 1):
        x = x * a; cnt[0] += 1
    return x


def pingala_power(a, n, cnt, chain):
    if n == 1:
        return a
    x = pingala_power(a, n // 2, cnt, chain)
    if n % 2 == 0:
        cnt[0] += 1; chain.append(2 * (n // 2))
        return x * x
    cnt[0] += 2; chain.extend([2 * (n // 2), n])
    return x * x * a


def peasant_power(a, n, cnt, chain, e=1):
    """chain records the exponents of the products formed (a is a^e)."""
    if n == 1:
        return a
    cnt[0] += 1; chain.append(2 * e)          # a^2
    if n % 2 == 0:
        return peasant_power(a * a, n // 2, cnt, chain, 2 * e)
    r = peasant_power(a * a, n // 2, cnt, chain, 2 * e)
    cnt[0] += 1; chain.append(e * n)
    return r * a


ok_s, ok_p, ok_q, ok_bound = True, True, True, True
for n in range(1, 3000):
    c = [0]
    ok_s &= slow_power(3, n, c) == 3 ** n and c[0] == n - 1
    c1, c2 = [0], [0]
    ok_p &= pingala_power(3, n, c1, []) == 3 ** n and pingala_power(7, n, [0], []) % 1000003 == pow(7, n, 1000003)
    ok_q &= peasant_power(3, n, c2, []) == 3 ** n
    formula = (n.bit_length() - 1) + bin(n).count("1") - 1
    ok_bound &= c1[0] == c2[0] == formula and c1[0] <= 2 * math.floor(lg(n)) and c1[0] >= math.ceil(lg(n))
check("SlowPower computes a^n with exactly n - 1 multiplications", ok_s)
check("PingalaPower and PeasantPower compute a^n, n = 1..2999", ok_p and ok_q)
check("both use exactly floor(lg n) + (number of 1 bits of n) - 1 multiplications, between ceil(lg n) and 2 floor(lg n)", ok_bound)
check("summary: the count equals the lower bound ceil(lg n) exactly when n has at most two 1 bits, n < 2^16",
      all((((n.bit_length() - 1) + bin(n).count("1") - 1) == math.ceil(lg(n))) == (bin(n).count("1") <= 2)
          for n in range(1, 2 ** 16)))
check("summary: e.g. n = 3, 5, 6, 12 meet ceil(lg n) though they are not powers of 2; n = 7 does not",
      all((n.bit_length() - 1) + bin(n).count("1") - 1 == math.ceil(lg(n)) for n in (3, 5, 6, 12))
      and (7).bit_length() - 1 + 3 - 1 == 4 > math.ceil(lg(7)))
check("n = 2^k: exactly lg n multiplications",
      all((lambda c: (pingala_power(1, 2 ** k, c, []), c[0])[1])([0]) == k for k in range(1, 40)) and
      all((lambda c: (peasant_power(1, 2 ** k, c, []), c[0])[1])([0]) == k for k in range(1, 40)))
c, ch = [0], []
pingala_power(5, 15, c, ch)
check("Pingala on a^15: chain 2, 3, 6, 7, 14, 15 (six multiplications)", ch == [2, 3, 6, 7, 14, 15] and c[0] == 6, str(ch))
c, ch = [0], []
peasant_power(5, 15, c, ch)
check("Peasant on a^15: chain 2, 4, 8, 12, 14, 15 (six multiplications)", sorted(ch) == [2, 4, 8, 12, 14, 15] and c[0] == 6,
      str(ch))


def shortest_chain(n):
    """Length of a shortest addition chain for n (iterative deepening)."""
    if n == 1:
        return 0
    best = [None]

    def dfs(chain, limit):
        last = chain[-1]
        if last == n:
            return True
        if len(chain) - 1 >= limit or last << (limit - len(chain) + 1) < n:
            return False
        seen = set()
        for i in range(len(chain) - 1, -1, -1):
            for j in range(i, -1, -1):
                s = chain[i] + chain[j]
                if last < s <= n and s not in seen:
                    seen.add(s)
                    if dfs(chain + [s], limit):
                        return True
        return False
    L = math.ceil(lg(n))
    while not dfs([1], L):
        L += 1
    return L


check("a^15 needs only 5 multiplications: 1, 2, 3, 5, 10, 15 is a valid chain and no 4-step chain exists",
      shortest_chain(15) == 5 and all(t in (1, 2, 3, 5, 10, 15) for t in (1 + 1, 2 + 1, 3 + 2, 5 + 5, 10 + 5)))
check("lower bound: every n <= 128 needs at least ceil(lg n) multiplications (exhaustive chain search)",
      all(shortest_chain(n) >= math.ceil(lg(n)) for n in range(1, 129)))
check("repeated squaring is optimal for powers of 2 but not always (n = 15, 23, 27, ... beat it)",
      all(shortest_chain(2 ** k) == k for k in range(1, 8)) and
      [n for n in range(1, 40) if shortest_chain(n) < (n.bit_length() - 1) + bin(n).count("1") - 1][:3] == [15, 23, 27])

# =====================================================================================================
# concept pages
# =====================================================================================================
# recursion: BinarySearch on A[1..n]
def binary_search(A, x, lo=0, hi=None, calls=None):
    if hi is None:
        hi = len(A) - 1
    if calls is not None:
        calls[0] += 1
    n = hi - lo + 1
    if n == 0:
        return False
    m = (n + 1) // 2
    if x == A[lo + m - 1]:
        return True
    if x < A[lo + m - 1]:
        return binary_search(A, x, lo, lo + m - 2, calls)
    return binary_search(A, x, lo + m, hi, calls)


ok, calls_ok = True, True
for A in small_arrays(8, alphabet=(1, 3, 5)):
    A = sorted(A)
    for x in range(0, 7):
        c = [0]
        ok &= binary_search(A, x, calls=c) == (x in A)
        calls_ok &= c[0] <= (len(A).bit_length() + 1)
check("concept recursion: BinarySearch(A, x) = (x in A) for all sorted arrays over {1,3,5}, length <= 8", ok)
check("concept recursion: at most floor(lg n) + 2 calls", calls_ok)
ok = True
for _ in range(500):
    A = sorted(rng.sample(range(10 ** 5), rng.randint(0, 3000)))
    x = rng.randint(0, 10 ** 5)
    c = [0]
    ok &= binary_search(A, x, calls=c) == (x in A) and c[0] <= len(A).bit_length() + 1
check("concept recursion: BinarySearch on 500 random sorted arrays, calls <= floor(lg n) + 2", ok)


def bad_search(A, x, lo, hi, depth=0):
    """Recursing on A[m..n] instead of A[m+1..n]."""
    if depth > 200:
        raise RecursionError
    n = hi - lo + 1
    if n == 0:
        return False
    m = (n + 1) // 2
    if x == A[lo + m - 1]:
        return True
    if x < A[lo + m - 1]:
        return bad_search(A, x, lo, lo + m - 2, depth + 1)
    return bad_search(A, x, lo + m - 1, hi, depth + 1)


try:
    bad_search([4], 9, 0, 0)
    looped = False
except RecursionError:
    looped = True
check("concept recursion: recursing on A[m..n] loops forever on A = [4], x = 9 (m = 1, same instance)", looped)


# divide-and-conquer: MinMax
def min_max(A, lo, hi, cnt):
    n = hi - lo + 1
    if n == 1:
        return A[lo], A[lo]
    if n == 2:
        cnt[0] += 1
        return (A[lo], A[hi]) if A[lo] < A[hi] else (A[hi], A[lo])
    m = n // 2
    a1, b1 = min_max(A, lo, lo + m - 1, cnt)
    a2, b2 = min_max(A, lo + m, hi, cnt)
    cnt[0] += 2
    return (a1 if a1 < a2 else a2), (b1 if b1 > b2 else b2)


ok = True
for A in small_arrays(7, alphabet=(1, 2, 3, 4)):
    if A:
        ok &= min_max(A, 0, len(A) - 1, [0]) == (min(A), max(A))
for _ in range(300):
    A = [rng.randint(-99, 99) for _ in range(rng.randint(1, 500))]
    ok &= min_max(A, 0, len(A) - 1, [0]) == (min(A), max(A))
check("concept divide-and-conquer: MinMax returns (min, max) on all small arrays and 300 random ones", ok)
ok = True
for k in range(1, 15):
    c = [0]
    A = [rng.random() for _ in range(2 ** k)]
    min_max(A, 0, len(A) - 1, c)
    ok &= c[0] == 3 * 2 ** k // 2 - 2
check("concept divide-and-conquer: n = 2^k uses exactly 3n/2 - 2 comparisons (T(2) = 1, T(n) = 2T(n/2) + 2)", ok)
c = [0]
min_max(list(range(6)), 0, 5, c)
check("... (not for every n: n = 6 uses 8 > ceil(3n/2) - 2 = 7)", c[0] == 8)
check("concept divide-and-conquer: separate scans use 2n - 2 comparisons; 1024 elements: 2046 vs 1534",
      2 * 1024 - 2 == 2046 and 3 * 1024 // 2 - 2 == 1534)


# linear-time selection: the k elements closest to the median
def closest_to_median(A, k):
    n = len(A)
    med = mom_select(list(A), (n + 1) // 2, record=False)
    D = [abs(a - med) for a in A]
    d = mom_select(list(D), k, record=False)
    out = [a for a in A if abs(a - med) < d]
    out += [a for a in A if abs(a - med) == d][:k - len(out)]
    return med, out


ok = True
for _ in range(400):
    n = rng.randint(1, 300)
    A = rng.sample(range(-10 ** 4, 10 ** 4), n)
    k = rng.randint(1, n)
    med, out = closest_to_median(A, k)
    true_med = sorted(A)[(n + 1) // 2 - 1]
    ok &= med == true_med and len(out) == k and len(set(out)) == k and set(out) <= set(A)
    ok &= sorted(abs(a - med) for a in out) == sorted(abs(a - med) for a in A)[:k]
check("concept selection: the k numbers closest to the median (two selections + two scans) match brute force", ok)
A = [12, 3, 17, 8, 25, 1, 14, 9, 30]
med, out = closest_to_median(A, 4)
check("concept selection example: A = 12,3,17,8,25,1,14,9,30, k = 4: median 12, answer {12, 14, 9, 8}",
      med == 12 and sorted(out) == [8, 9, 12, 14], f"{med} {out}")

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: {FAIL}")
