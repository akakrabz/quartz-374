#!/usr/bin/env python3
"""Checks for content/0-toolkit/08-review-algorithms.md (the Midterm 2 review).

1. Recurrences: every solution on the page (the key box's three cases on a grid of a, b, d; the rule for pieces of
   different sizes; the subtractive rows; the table of standard recurrences; drill group A) — exact closed forms
   where they exist, otherwise the ratio T(n)/g(n) for growing n must settle inside a narrow band while the ratio to
   the next candidate drifts.
2. Backtracking call counts (2^n, 3^n bounds of §3).
3. Every dynamic program of §4's table, implemented as the page states it, against brute force on random inputs;
   the evaluation orders of the shapes table and of drill group B by simulating the fill and checking every read.
4. The greedy coin counterexample.
5. Graph algorithms on random graphs: whatever-first search (any bag) marks reach(s); components; DFS edge
   classification by intervals and by finishing times; cycle iff back edge; reverse postorder is topological;
   Kosaraju-Sharir as stated (rev(G) first, then G in decreasing finishing time, sink components first);
   BFS, DagSSSP, Dijkstra, Bellman-Ford (rounds and the DP over the number of edges, including the row-V test and
   the super-source), Floyd-Warshall (r outer, in place, negative-cycle test via the diagonal; r inner fails),
   the layered dag for walks with at most k edges, reversal for distances to t, vertex splitting, token pairs.
6. Every drill answer (groups A-D) by brute force, the drill graph rebuilt from tools/figs_review_mt2.py.
7. Key strings of the page, so that the page says what is checked here."""
import heapq
import itertools
import math
import os
import random
import re
import sys
from collections import deque
from fractions import Fraction
from functools import lru_cache

sys.setrecursionlimit(100000)
HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.join(HERE, "..")
sys.path.insert(0, TOOLS)
PAGE = os.path.join(TOOLS, "..", "content", "0-toolkit", "08-review-algorithms.md")
TEXT = open(PAGE, encoding="utf-8").read()
FAIL = []
random.seed(374)
INF = math.inf


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAIL.append(name)


def on_page(s):
    return s in TEXT


# =====================================================================================================
# 1. Recurrences
# =====================================================================================================
print("== 1. recurrences")


def settles(ratios, tol):
    """ratios over a geometric range of n: the last third varies by less than tol (relative), all finite > 0."""
    tail = ratios[len(ratios) * 2 // 3:]
    lo, hi = min(tail), max(tail)
    return lo > 0 and hi / lo < 1 + tol, (round(lo, 4), round(hi, 4))


def powers_rec(a, b, d_num, K, T1=1):
    """T(b^k) = a T(b^(k-1)) + (b^k)^d with b^d an integer (d_num = b^d); exact integers."""
    T = [T1]
    for k in range(1, K + 1):
        T.append(a * T[-1] + d_num ** k)
    return T


# --- the key box: three cases for a T(n/b) + n^d, on a grid where b^d is an integer
grid_ok = True
bad = []
for b in (2, 3, 4):
    for bd in (1, b, b * b):          # d = 0, 1, 2
        d = math.log(bd, b)
        for a in range(1, 10):
            K = 300
            T = powers_rec(a, b, bd, K)
            ratio = a / bd
            if ratio < 1:      # root: Theta(n^d) = bd^k
                r = [T[k] / bd ** k for k in range(100, K + 1, 10)]
            elif ratio == 1:   # equal: Theta(n^d log n) = bd^k * k
                r = [T[k] / (bd ** k * k) for k in range(100, K + 1, 10)]
            else:              # leaves: Theta(n^(log_b a)) = a^k
                r = [T[k] / a ** k for k in range(100, K + 1, 10)]
            ok, _ = settles(r, 0.02)
            if not ok:
                grid_ok = False
                bad.append((a, b, d))
check("key box: the three cases on a in 1..9, b in {2,3,4}, d in {0,1,2} (exact at powers of b)", grid_ok, bad)

# ratio form with sqrt: 4T(n/16) + sqrt n, at powers of 16 exact: T = 4^k (k+1)  (drill A4)
T = powers_rec(4, 16, 4, 200)
check("drill A4: 4T(n/16)+sqrt(n) = sqrt(n)(log_16 n + 1) exactly at powers of 16 (Theta(sqrt n log n))",
      all(T[k] == 4 ** k * (k + 1) for k in range(201)))

# drill A1: 4T(n/2) + n^2 = n^2 (lg n + 1) at powers of 2
T = powers_rec(4, 2, 4, 200)
check("drill A1: 4T(n/2)+n^2 = n^2(lg n + 1) exactly (Theta(n^2 log n))",
      all(T[k] == 4 ** k * (k + 1) for k in range(201)))
# drill A2: 5T(n/2) + n^2 -> Theta(n^lg5) = 5^k
T = powers_rec(5, 2, 4, 400)
ok, rng = settles([T[k] / 5 ** k for k in range(100, 401, 10)], 1e-6)
check("drill A2: 5T(n/2)+n^2 / n^(lg 5) settles (Theta(n^lg5), lg 5 ~ 2.32)", ok and abs(math.log2(5) - 2.32) < 0.005, rng)


# floors versions for multi-term recurrences
def floor_rec(parts, f, base=1):
    """T(n) = sum T(floor(p*n)) + f(n) for n >= 2, T(n) = base for n <= 1; parts are Fractions."""
    @lru_cache(None)
    def T(n):
        if n <= 1:
            return base
        return sum(T(int(p * n)) for p in parts) + f(n)
    return T


NS = [int(10 ** (e / 4)) for e in range(16, 61)]   # 1e4 .. 1e15


def band(T, g, ns=NS):
    r = [T(n) / g(n) for n in ns]
    tail = r[len(r) // 2:]
    return min(tail), max(tail)


lg = math.log2
# drill A3: T(n/2) + T(n/3) + n -> Theta(n)
T3 = floor_rec([Fraction(1, 2), Fraction(1, 3)], lambda n: n)
lo, hi = band(T3, lambda n: n)
check("drill A3: T(n/2)+T(n/3)+n is Theta(n) (T(n)/n in a band, at most 6)", 1 <= lo and hi <= 6 and hi / lo < 1.3, (lo, hi))
# three pieces adding up to n: Theta(n log n)
T6 = floor_rec([Fraction(1, 2), Fraction(1, 3), Fraction(1, 6)], lambda n: n)
lo, hi = band(T6, lambda n: n * lg(n))
r_n = [T6(n) / n for n in (10 ** 4, 10 ** 15)]
check("T(n/2)+T(n/3)+T(n/6)+n is Theta(n log n): T/(n lg n) in a band, T/n grows", hi / lo < 1.3 and r_n[1] > 2.5 * r_n[0], (lo, hi, r_n))
# blocks of 3: T(n/3)+T(2n/3)+n
TB3 = floor_rec([Fraction(1, 3), Fraction(2, 3)], lambda n: n)
lo, hi = band(TB3, lambda n: n * lg(n))
check("T(n/3)+T(2n/3)+n is Theta(n log n)", hi / lo < 1.3, (lo, hi))
# median of medians: T(n/5)+T(7n/10)+n -> Theta(n), at most 10n
TM = floor_rec([Fraction(1, 5), Fraction(7, 10)], lambda n: n)
lo, hi = band(TM, lambda n: n)
check("median of medians T(n/5)+T(7n/10)+n is Theta(n) (ratio <= 10)", hi <= 10 and hi / lo < 1.3 and abs(1 / 5 + 7 / 10 - 9 / 10) < 1e-12, (lo, hi))
# pieces with sum > 1: T(n/2)+T(n/2)+T(n/3)+n -> Theta(n^rho), 2(1/2)^rho + (1/3)^rho = 1
lo_r, hi_r = 1.0, 3.0
for _ in range(100):
    mid = (lo_r + hi_r) / 2
    if 2 * 0.5 ** mid + (1 / 3) ** mid > 1:
        lo_r = mid
    else:
        hi_r = mid
rho = lo_r
TG = floor_rec([Fraction(1, 2), Fraction(1, 2), Fraction(1, 3)], lambda n: n)
lo, hi = band(TG, lambda n: n ** rho)
check(f"pieces adding to more than 1 (1/2+1/2+1/3): Theta(n^rho), rho = {rho:.4f}", hi / lo < 1.3 and rho > 1, (lo, hi))
# d = 2 version of the different-sizes rule: T(n/2)+T(n/2)+T(n/2)+T(n/2) is a=4,b=2 (covered); try T(n/2)+T(n/3)+n^2:
# sum alpha^2 = 1/4+1/9 < 1 -> Theta(n^2)
TQ = floor_rec([Fraction(1, 2), Fraction(1, 3)], lambda n: n * n)
lo, hi = band(TQ, lambda n: n * n)
check("different sizes with d = 2: T(n/2)+T(n/3)+n^2 is Theta(n^2)", hi / lo < 1.05, (lo, hi))
# d = 1/2, sum alpha^(1/2) = 1: T(n/4) + T(n/4) + sqrt n ~ a=2,b=4: Theta(sqrt n log n) (equal)
TS = floor_rec([Fraction(1, 4), Fraction(1, 4)], lambda n: math.sqrt(n))
lo, hi = band(TS, lambda n: math.sqrt(n) * lg(n))
check("different sizes, equal case with d = 1/2: Theta(sqrt n log n)", hi / lo < 1.35, (lo, hi))

# subtractive rows
T = [0]
for n in range(1, 200):
    T.append(T[-1] + 1)
check("T(n-1)+1 = n (Theta(n))", T[199] == 199)
T = [0]
for n in range(1, 2001):
    T.append(T[-1] + n)
check("T(n-1)+n = n(n+1)/2 (Theta(n^2)): quicksort and quickselect worst case", all(T[n] == n * (n + 1) // 2 for n in range(2001)))
H = [0]
for n in range(1, 64):
    H.append(2 * H[-1] + 1)
check("Hanoi T(n) = 2T(n-1)+1 = 2^n - 1 exactly", all(H[n] == 2 ** n - 1 for n in range(64)))


def hanoi_moves(n, src=0, dst=2, tmp=1, out=None):
    out = [] if out is None else out
    if n:
        hanoi_moves(n - 1, src, tmp, dst, out)
        out.append((src, dst))
        hanoi_moves(n - 1, tmp, dst, src, out)
    return out


check("Hanoi algorithm makes 2^n - 1 moves for n <= 12", all(len(hanoi_moves(n)) == 2 ** n - 1 for n in range(13)))

# mergesort: 2T(n/2)+n at powers of 2 with T(1)=0 is n lg n; with floors/ceilings Theta(n log n)
T = powers_rec(2, 2, 2, 60, T1=0)
check("mergesort 2T(n/2)+n = n lg n exactly at powers of 2", all(T[k] == 2 ** k * k for k in range(61)))


@lru_cache(None)
def msort(n):
    return 0 if n <= 1 else msort((n + 1) // 2) + msort(n // 2) + n


lo, hi = band(msort, lambda n: n * lg(n))
check("mergesort with floors and ceilings is Theta(n log n)", 0.9 < lo and hi < 1.1, (lo, hi))


def merge_sort(A):
    if len(A) <= 1:
        return A
    m = len(A) // 2
    L, R = merge_sort(A[:m]), merge_sort(A[m:])
    out, i, j = [], 0, 0
    while i < len(L) and j < len(R):
        if L[i] < R[j]:
            out.append(L[i]); i += 1
        else:
            out.append(R[j]); j += 1
    return out + L[i:] + R[j:]


check("MergeSort sorts 300 random arrays", all(merge_sort(A) == sorted(A) for A in
                                               ([random.randint(0, 20) for _ in range(random.randint(0, 40))] for _ in range(300))))

# quicksort random pivot: expected comparisons C(n) = n-1 + (2/n) sum C(k) = 2(n+1)H_n - 4n
C = [Fraction(0)]
S = Fraction(0)
for n in range(1, 301):
    S += C[-1]
    C.append(n - 1 + Fraction(2, n) * S)
Hn = [Fraction(0)]
for n in range(1, 301):
    Hn.append(Hn[-1] + Fraction(1, n))
check("random quicksort: C(n) = n-1 + (2/n) sum_{k<n} C(k) equals 2(n+1)H_n - 4n exactly (n <= 300)",
      all(C[n] == 2 * (n + 1) * Hn[n] - 4 * n for n in range(301)))
rs = []
for n in (10 ** 3, 10 ** 4, 10 ** 5, 10 ** 6, 10 ** 7):
    h = sum(1.0 / k for k in range(1, n + 1))
    rs.append((2 * (n + 1) * h - 4 * n) / (n * math.log(n)))
check("random quicksort is Theta(n log n): C(n)/(n ln n) increases towards 2 and stays below it",
      all(x < y for x, y in zip(rs, rs[1:])) and rs[-1] < 2 and rs[0] > 1.5, [round(x, 3) for x in rs])


# empirical check of the expected-comparisons recurrence on actual randomized quicksort
def rq_comparisons(A):
    if len(A) <= 1:
        return 0
    p = random.choice(A)
    L = [x for x in A if x < p]
    R = [x for x in A if x > p]
    return len(A) - 1 + rq_comparisons(L) + rq_comparisons(R)


n = 60
avg = sum(rq_comparisons(list(range(n))) for _ in range(3000)) / 3000
exact = float(C[n])
check("randomized quicksort on 60 distinct keys averages close to C(60)", abs(avg - exact) / exact < 0.03, (round(avg, 2), round(exact, 2)))

# binary search T(n) = T(floor(n/2)) + 1, T(1) = 1 -> floor(lg n) + 1
@lru_cache(None)
def bs(n):
    return 1 if n <= 1 else bs(n // 2) + 1


check("binary search T(floor(n/2))+1 = floor(lg n)+1 (Theta(log n))", all(bs(n) == n.bit_length() for n in range(1, 5000)))


@lru_cache(None)
def qs_med(n):
    return 1 if n <= 1 else qs_med(n // 2) + n


lo, hi = band(qs_med, lambda n: n)
check("quickselect with median pivot T(n/2)+n is Theta(n) (ratio -> 2)", 1.9 < lo and hi <= 2.0, (lo, hi))

# splitting multiplication 4T(n/2)+n = 2n^2 - n; Karatsuba 3T(n/2)+n = 3 n^lg3 - 2n; Strassen 7T(n/2)+n^2
T = powers_rec(4, 2, 2, 100)
check("4T(n/2)+n = 2n^2 - n exactly (Theta(n^2))", all(T[k] == 2 * 4 ** k - 2 ** k for k in range(101)))
T = powers_rec(3, 2, 2, 100)
check("Karatsuba 3T(n/2)+n = 3n^(lg 3) - 2n exactly (Theta(n^lg3))", all(T[k] == 3 * 3 ** k - 2 * 2 ** k for k in range(101)))
check("lg 3 < 1.585 and lg 7 < 2.808", math.log2(3) < 1.585 and math.log2(7) < 2.808 and math.log2(7) > 2.807)
T = powers_rec(7, 2, 4, 100)
check("Strassen-like 7T(n/2)+n^2 = (7 n^lg7 - 4 n^2)/3 exactly (Theta(n^lg7))",
      all(3 * T[k] == 7 * 7 ** k - 4 * 4 ** k for k in range(101)))


# exponentiation by repeated squaring: number of multiplications Theta(log n)
def pingala(a, n, cnt):
    if n == 1:
        return a
    x = pingala(a, n // 2, cnt)
    cnt[0] += 1
    x = x * x
    if n % 2:
        cnt[0] += 1
        x = x * a
    return x


okp = True
for n in range(1, 3000):
    cnt = [0]
    v = pingala(3, n, cnt)
    if v != 3 ** n or not (n.bit_length() - 1 <= cnt[0] <= 2 * (n.bit_length() - 1)):
        okp = False
check("repeated squaring: correct, between floor(lg n) and 2 floor(lg n) multiplications (Theta(log n))", okp)

# drill A5: T(n/2) + lg n at powers of 2 with T(1) = 0 -> k(k+1)/2 = Theta(log^2 n)
T = [0]
for k in range(1, 200):
    T.append(T[-1] + k)
check("drill A5: T(n/2)+lg n = lg n (lg n + 1)/2 at powers of 2 (Theta(log^2 n))", all(T[k] == k * (k + 1) // 2 for k in range(200)))

# a ratio check that the key box needs: sizes of levels for different pieces = (sum alpha_i^d)^i n^d
# (complete tree, ignoring the missing nodes): exact for the first levels with Fractions
alphas = [Fraction(1, 2), Fraction(1, 3)]
lvl = [Fraction(1)]
for i in range(6):
    lvl = [x * a for x in lvl for a in alphas]
    check(f"drill A3: level {i + 1} of the tree for T(n/2)+T(n/3)+n sums to (5/6)^{i + 1} n", sum(lvl) == Fraction(5, 6) ** (i + 1))

# type 1: T(n/2)+T(n/3)+T(n/6)+n, nodes of size >= 1 recurse: every level sums to at most n,
# the first floor(log_6 n) levels to exactly n (multiset of sizes, exact)
from collections import Counter
ok_pieces = True
for n0 in (6 ** 3, 6 ** 4, 1000, 777):
    lvl, i = Counter({Fraction(n0): 1}), 0
    while lvl:
        s_i = sum(x * c for x, c in lvl.items())
        ok_pieces &= s_i <= n0 and (s_i == n0) == (i <= math.floor(math.log(n0, 6) + 1e-9))
        nxt = Counter()
        for x, c in lvl.items():
            for a in (Fraction(1, 2), Fraction(1, 3), Fraction(1, 6)):
                if x * a >= 1:
                    nxt[x * a] += c
        lvl, i = nxt, i + 1
check("T(n/2)+T(n/3)+T(n/6)+n: every level sums to at most n, exactly n for the first floor(log_6 n) levels", ok_pieces)

# type 1: a log factor in f: ratio a f(n/b)/f(n) for 2T(n/2)+n lg n is (k-1)/k at n = 2^k, not constant
rat = [Fraction(2 * (2 ** (k - 1)) * (k - 1), (2 ** k) * k) for k in range(2, 12)]
check("log factor: 2 f(n/2)/f(n) for f = n lg n is (lg n - 1)/lg n, increasing towards 1 (no constant ratio)",
      rat == [Fraction(k - 1, k) for k in range(2, 12)] and all(x < y < 1 for x, y in zip(rat, rat[1:])))

# =====================================================================================================
# 2. Backtracking call counts
# =====================================================================================================
print("== 2. backtracking")


def subset_sum_calls(X, i, T, cnt):
    cnt[0] += 1
    if T == 0:
        return True
    if T < 0 or i == 0:
        return False
    a = subset_sum_calls(X, i - 1, T - X[i - 1], cnt)
    b = subset_sum_calls(X, i - 1, T, cnt)
    return a or b


ok = True
for n in range(0, 13):
    X = [random.randint(1, 9) for _ in range(n)]
    cnt = [0]
    subset_sum_calls(X, n, sum(X) + 1, cnt)
    ok &= cnt[0] == 2 ** (n + 1) - 1
check("SubsetSum(X, i, T) with T > sum X makes 2^(n+1) - 1 calls (O(2^n))", ok)

ok = True
for _ in range(200):
    n = random.randint(0, 9)
    X = [random.randint(1, 9) for _ in range(n)]
    T = random.randint(0, 30)
    got = subset_sum_calls(X, n, T, [0])
    want = any(sum(c) == T for r in range(n + 1) for c in itertools.combinations(X, r))
    ok &= got == want
check("SubsetSum(X, n, T) correct against all subsets (200 random)", ok)


def splittable_calls(A, i, words, cnt):
    cnt[0] += 1
    if i >= len(A):
        return True
    res = False
    for j in range(i, len(A)):
        if A[i:j + 1] in words and splittable_calls(A, j + 1, words, cnt):
            res = True
    return res


ok = True
for n in range(1, 15):
    A = "a" * (n - 1) + "b"
    words = {"a" * k for k in range(1, n + 1)}
    cnt = [0]
    splittable_calls(A, 0, words, cnt)
    ok &= cnt[0] <= 2 ** n
check("backtracking Splittable makes at most 2^n calls on a^(n-1)b with every a^k a word", ok)


def lisbigger_calls(A, i, j, cnt):
    cnt[0] += 1
    if j >= len(A):
        return 0
    skip = lisbigger_calls(A, i, j + 1, cnt)
    if i < 0 or A[j] > A[i]:
        return max(skip, 1 + lisbigger_calls(A, j, j + 1, cnt))
    return skip


def lisfirst_calls(A, i, cnt):
    cnt[0] += 1
    best = 0
    for j in range(i + 1, len(A)):
        if i < 0 or A[j] > A[i]:
            best = max(best, lisfirst_calls(A, j, cnt))
    return 1 + best


def lis_brute(A):
    best = 0
    for r in range(len(A) + 1):
        for c in itertools.combinations(range(len(A)), r):
            if all(A[c[t]] < A[c[t + 1]] for t in range(len(c) - 1)):
                best = max(best, r)
    return best


ok_cnt, ok_val = True, True
for _ in range(150):
    n = random.randint(0, 10)
    A = [random.randint(0, 9) for _ in range(n)]
    c1, c2 = [0], [0]
    v1 = lisbigger_calls(A, -1, 0, c1)
    v2 = lisfirst_calls(A, -1, c2) - 1
    ok_cnt &= c1[0] <= 2 ** (n + 1) and c2[0] <= 2 ** n
    ok_val &= v1 == v2 == lis_brute(A)
check("LISbigger and LISfirst backtracking: correct, at most 2^(n+1) and 2^n calls", ok_cnt and ok_val)


def optcost_calls(k_count, cnt):
    """count calls of the OptCost recursion on an interval of k keys"""
    cnt[0] += 1
    for r in range(k_count):
        optcost_calls(r, cnt)
        optcost_calls(k_count - 1 - r, cnt)


ok = True
for n in range(0, 11):
    cnt = [0]
    optcost_calls(n, cnt)
    ok &= cnt[0] == 3 ** n
check("OptCost backtracking makes exactly 3^n calls (Theta(3^n))", ok)

# =====================================================================================================
# 3. Dynamic programs of §4, as stated, against brute force; evaluation orders
# =====================================================================================================
print("== 3. dynamic programs")

fib = [0, 1]
for i in range(2, 90):
    fib.append(fib[-1] + fib[-2])
check("Fib(i) = Fib(i-1) + Fib(i-2) gives the Fibonacci numbers", fib[10] == 55 and fib[50] == 12586269025)


def splittable_dp(A, words):
    n = len(A)
    S = [False] * (n + 2)
    S[n + 1] = True                     # 1-indexed: S[i] for suffix A[i..n]
    for i in range(n, 0, -1):            # i decreasing
        S[i] = any(A[i - 1:j] in words and S[j + 1] for j in range(i, n + 1))
    return S[1]


def splittable_brute(A, words):
    n = len(A)
    for mask in range(2 ** max(n - 1, 0)):
        cuts = [0] + [k + 1 for k in range(n - 1) if mask >> k & 1] + [n]
        if all(A[cuts[t]:cuts[t + 1]] in words for t in range(len(cuts) - 1)):
            return True
    return n == 0


ok = True
for _ in range(400):
    n = random.randint(0, 9)
    A = "".join(random.choice("ab") for _ in range(n))
    words = {"".join(random.choice("ab") for _ in range(random.randint(1, 3))) for _ in range(random.randint(1, 6))}
    ok &= splittable_dp(A, words) == splittable_brute(A, words)
check("Splittable(i) recurrence, i decreasing, against all segmentations (400 random)", ok)


def lisfirst_dp(A):
    n = len(A)
    B = [-INF] + A                       # sentinel A[0] = -inf
    L = [0] * (n + 1)
    for i in range(n, -1, -1):
        L[i] = 1 + max([L[j] for j in range(i + 1, n + 1) if B[j] > B[i]], default=0)
    return L[0] - 1


ok = all(lisfirst_dp(A) == lis_brute(A) for A in ([random.randint(0, 6) for _ in range(random.randint(0, 9))] for _ in range(300)))
check("LISfirst(i) = 1 + max{LISfirst(j) : j > i, A[j] > A[i]} (max over nothing = 0), against brute force", ok)


def edit_dp(A, B):
    m, n = len(A), len(B)
    E = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):              # i increasing outer
        for j in range(n + 1):          # j increasing inner
            if i == 0:
                E[i][j] = j
            elif j == 0:
                E[i][j] = i
            else:
                E[i][j] = min(E[i - 1][j] + 1, E[i][j - 1] + 1, E[i - 1][j - 1] + (A[i - 1] != B[j - 1]))
    return E[m][n]


def edit_brute(A, B):
    """BFS over strings: insert, delete, substitute, each cost 1."""
    alphabet = "ab"
    limit = len(A) + len(B)
    dist = {A: 0}
    q = deque([A])
    while q:
        s = q.popleft()
        if s == B:
            return dist[s]
        nb = set()
        for k in range(len(s) + 1):
            for c in alphabet:
                if len(s) < limit:
                    nb.add(s[:k] + c + s[k:])
        for k in range(len(s)):
            nb.add(s[:k] + s[k + 1:])
            for c in alphabet:
                nb.add(s[:k] + c + s[k + 1:])
        for t in nb:
            if t not in dist:
                dist[t] = dist[s] + 1
                q.append(t)


ok = True
for _ in range(150):
    A = "".join(random.choice("ab") for _ in range(random.randint(0, 4)))
    B = "".join(random.choice("ab") for _ in range(random.randint(0, 4)))
    ok &= edit_dp(A, B) == edit_brute(A, B)
check("Edit(i, j) recurrence, row by row, against BFS over strings (150 random pairs)", ok)


def ss_dp(X, T):
    n = len(X)
    S = [[False] * (T + 1) for _ in range(n + 2)]   # S[i][t], 1-indexed i
    for t in range(T + 1):
        S[n + 1][t] = (t == 0)
    for i in range(n, 0, -1):                      # i decreasing outer
        for t in range(T + 1):                     # t any order
            S[i][t] = S[i + 1][t] or (t >= X[i - 1] and S[i + 1][t - X[i - 1]])
    return S[1][T]


ok = True
for _ in range(300):
    X = [random.randint(1, 9) for _ in range(random.randint(0, 8))]
    T = random.randint(0, 25)
    ok &= ss_dp(X, T) == any(sum(c) == T for r in range(len(X) + 1) for c in itertools.combinations(X, r))
check("SS(i, t) = SS(i+1, t) or SS(i+1, t - X[i]), i decreasing, against all subsets", ok)


def optcost_dp(f):
    n = len(f)
    F = [0] + f
    pre = [0] * (n + 1)
    for i in range(1, n + 1):
        pre[i] = pre[i - 1] + F[i]
    C = [[0] * (n + 2) for _ in range(n + 2)]      # C[i][k], k >= i-1
    for i in range(n, 0, -1):                       # i decreasing outer
        for k in range(i, n + 1):                   # k increasing inner
            C[i][k] = pre[k] - pre[i - 1] + min(C[i][r - 1] + C[r + 1][k] for r in range(i, k + 1))
    return C[1][n] if n else 0


def bst_brute(keys, f, depth=1):
    if not keys:
        return 0
    return min(f[r] * depth + bst_brute(keys[:keys.index(r)], f, depth + 1) + bst_brute(keys[keys.index(r) + 1:], f, depth + 1)
               for r in keys)


ok = True
for _ in range(150):
    n = random.randint(0, 6)
    f = [random.randint(1, 9) for _ in range(n)]
    ok &= optcost_dp(f) == bst_brute(list(range(n)), f)
check("OptCost(i, k) = sum f + min over roots, i decreasing / k increasing, against all BSTs", ok)


def random_tree(n):
    parent = {0: None}
    for v in range(1, n):
        parent[v] = random.randrange(v)
    children = {v: [] for v in range(n)}
    for v in range(1, n):
        children[parent[v]].append(v)
    return parent, children


def mis_dp(children, root=0):
    yes, no = {}, {}

    def post(v):
        for w in children[v]:
            post(w)
        yes[v] = 1 + sum(no[w] for w in children[v])
        no[v] = sum(max(yes[w], no[w]) for w in children[v])
    post(root)
    return max(yes[root], no[root])


ok = True
for _ in range(200):
    n = random.randint(1, 12)
    parent, children = random_tree(n)
    best = 0
    for mask in range(2 ** n):
        if all(not (mask >> v & 1 and parent[v] is not None and mask >> parent[v] & 1) for v in range(n)):
            best = max(best, bin(mask).count("1"))
    ok &= mis_dp(children) == best
check("MISyes/MISno in postorder against all vertex subsets of 200 random trees", ok)


def random_dag(n, p, wlo=-5, whi=8):
    order = list(range(n))
    random.shuffle(order)
    E = {}
    for a in range(n):
        for b in range(a + 1, n):
            if random.random() < p:
                E[(order[a], order[b])] = random.randint(wlo, whi)
    return E


def all_paths(n, E, s, t):
    adj = {v: [] for v in range(n)}
    for (u, v) in E:
        adj[u].append(v)
    out = []

    def go(v, path, w):
        if v == t:
            out.append(w)
        for x in adj[v]:
            if x not in path:
                go(x, path | {x}, w + E[(v, x)])
    go(s, {s}, 0)
    return out


def dfs_post(n, adj, order=None):
    pre, post, parent = {}, {}, {}
    clock = [0]

    def dfs(v):
        clock[0] += 1
        pre[v] = clock[0]
        for w in adj[v]:
            if w not in pre:
                parent[w] = v
                dfs(w)
        clock[0] += 1
        post[v] = clock[0]
    for v in (order if order is not None else range(n)):
        if v not in pre:
            parent[v] = None
            dfs(v)
    return pre, post, parent


def llp_dp(n, E, t):
    adj = {v: sorted(w for (u, w) in E if u == v) for v in range(n)}
    pre, post, _ = dfs_post(n, adj)
    L = {}
    for v in sorted(range(n), key=lambda v: post[v]):    # postorder
        L[v] = 0 if v == t else max([E[(v, w)] + L[w] for w in adj[v]], default=-INF)
    return L


ok = True
for _ in range(200):
    n = random.randint(1, 7)
    E = random_dag(n, 0.45)
    t = random.randrange(n)
    L = llp_dp(n, E, t)
    for s in range(n):
        ps = all_paths(n, E, s, t)
        ok &= L[s] == (max(ps) if ps else -INF)
check("LLP(v) = max over v->w of l(v->w) + LLP(w), in DFS postorder, against all paths (200 random dags)", ok)


# ---- evaluation orders: simulate the fill and check that every read is already written
def order_ok(entries_in_order, deps):
    done = set()
    for e in entries_in_order:
        for d in deps(e):
            if d not in done:
                return False
        done.add(e)
    return True


n, T, m = 7, 9, 6
X = [random.randint(1, 5) for _ in range(n)]
# SS(i, t): reads (i+1, t), (i+1, t - X[i]); i decreasing outer, t either direction
ss_deps = lambda e: [] if e[0] == n + 1 else [(e[0] + 1, e[1])] + ([(e[0] + 1, e[1] - X[e[0] - 1])] if e[1] >= X[e[0] - 1] else [])
for tdir in (1, -1):
    order = [(i, t) for i in range(n + 1, 0, -1) for t in (range(T + 1) if tdir == 1 else range(T, -1, -1))]
    check(f"order: SS with i decreasing outer, t {'up' if tdir == 1 else 'down'} inner", order_ok(order, ss_deps))
# LISbigger(i, j): reads (i, j+1) and (j, j+1); j decreasing outer, i any
lb_deps = lambda e: [] if e[1] == n + 1 else [(e[0], e[1] + 1), (e[1], e[1] + 1)]
order = [(i, j) for j in range(n + 1, 0, -1) for i in range(0, j)]
order2 = [(i, j) for j in range(n + 1, 0, -1) for i in range(j - 1, -1, -1)]
check("order: LISbigger with the suffix index j decreasing outer, i in either direction", order_ok(order, lb_deps) and order_ok(order2, lb_deps))
bad_order = [(i, j) for i in range(0, n + 1) for j in range(i + 1, n + 2)]
check("order: LISbigger row by row from the top is NOT valid (the trap of §3.4)", not order_ok(bad_order, lb_deps))
# Edit(i, j): reads (i-1, j), (i, j-1), (i-1, j-1)
ed_deps = lambda e: [] if e[0] == 0 or e[1] == 0 else [(e[0] - 1, e[1]), (e[0], e[1] - 1), (e[0] - 1, e[1] - 1)]
check("order: Edit with i increasing outer, j increasing inner",
      order_ok([(i, j) for i in range(m + 1) for j in range(n + 1)], ed_deps))
# interval OptCost(i, k): reads (i, r-1), (r+1, k) for i <= r <= k; empty intervals (k = i-1) are base cases
oc_deps = lambda e: [] if e[1] < e[0] else [(e[0], r - 1) for r in range(e[0], e[1] + 1)] + [(r + 1, e[1]) for r in range(e[0], e[1] + 1)]
base = [(i, i - 1) for i in range(1, n + 2)]
order_a = base + [(i, k) for i in range(n, 0, -1) for k in range(i, n + 1)]
order_b = base + [(i, i + L) for L in range(0, n) for i in range(1, n - L + 1)]
check("order: interval DP with i decreasing outer and k increasing inner, and by increasing length",
      order_ok(order_a, oc_deps) and order_ok(order_b, oc_deps))
# prefix/suffix orders for Splittable and LISfirst
check("order: Splittable(i) with i decreasing",
      order_ok(list(range(n + 1, 0, -1)), lambda i: [] if i == n + 1 else list(range(i + 1, n + 2))))
# Bellman-Ford DP rows, Floyd-Warshall r outer: dist(u,v,r) reads (u,v,r-1),(u,r,r-1),(r,v,r-1)
V = 5
bf_deps = lambda e: [] if e[0] == 0 else [(e[0] - 1, u) for u in range(V)]
check("order: Bellman-Ford DP with i increasing outer, vertices in any order",
      order_ok([(i, v) for i in range(V) for v in random.sample(range(V), V)], bf_deps))
fw_deps = lambda e: [] if e[2] == 0 else [(e[0], e[1], e[2] - 1), (e[0], e[2], e[2] - 1), (e[2], e[1], e[2] - 1)]
check("order: Floyd-Warshall recurrence with r increasing outer",
      order_ok([(u, v, r) for r in range(V + 1) for u in range(1, V + 1) for v in range(1, V + 1)], fw_deps))

# =====================================================================================================
# 4. Greedy counterexample
# =====================================================================================================
print("== 4. greedy counterexample")


def greedy_coins(coins, x):
    out = []
    for c in sorted(coins, reverse=True):
        while x >= c:
            x -= c
            out.append(c)
    return out


def min_coins(coins, x):
    best = [0] + [INF] * x
    for y in range(1, x + 1):
        best[y] = min((best[y - c] + 1 for c in coins if c <= y), default=INF)
    return best[x]


g = greedy_coins([1, 3, 4], 6)
check("coins 1, 3, 4: largest-first pays 6 as 4+1+1 (3 coins); optimum 3+3 (2 coins)",
      g == [4, 1, 1] and min_coins([1, 3, 4], 6) == 2 and sum([3, 3]) == 6)

# =====================================================================================================
# 5. Graph algorithms
# =====================================================================================================
print("== 5. graph algorithms")


def random_digraph(n, p, wlo=1, whi=9, loops=False):
    E = {}
    for u in range(n):
        for v in range(n):
            if (u != v or loops) and random.random() < p:
                E[(u, v)] = random.randint(wlo, whi)
    return E


def adj_of(n, E):
    adj = {v: [] for v in range(n)}
    for (u, v) in sorted(E):
        adj[u].append(v)
    return adj


def reach_brute(n, adj, s):
    R = {s}
    changed = True
    while changed:
        changed = False
        for u in list(R):
            for v in adj[u]:
                if v not in R:
                    R.add(v)
                    changed = True
    return R


def wfs(n, adj, s, bag):
    marked = set()
    B = [(None, s)]
    parent = {}
    while B:
        if bag == "stack":
            p, v = B.pop()
        elif bag == "queue":
            p, v = B.pop(0)
        else:
            p, v = B.pop(random.randrange(len(B)))
        if v not in marked:
            marked.add(v)
            parent[v] = p
            for w in adj[v]:
                B.append((v, w))
    return marked, parent


ok = True
for _ in range(300):
    n = random.randint(1, 8)
    E = random_digraph(n, 0.25)
    adj = adj_of(n, E)
    s = random.randrange(n)
    R = reach_brute(n, adj, s)
    for bag in ("stack", "queue", "random"):
        M, par = wfs(n, adj, s, bag)
        ok &= M == R and all(par[v] is None or (par[v], v) in E for v in M) and sum(par[v] is None for v in M) == 1
check("whatever-first search with a stack, a queue or a random bag marks exactly reach(s), parents form a tree", ok)

# components by WFSAll versus union-find (undirected)
ok = True
for _ in range(200):
    n = random.randint(1, 10)
    und = set()
    for u in range(n):
        for v in range(u + 1, n):
            if random.random() < 0.2:
                und.add((u, v))
    adj = {v: [] for v in range(n)}
    for u, v in und:
        adj[u].append(v)
        adj[v].append(u)
    marked, comps = set(), 0
    for v in range(n):
        if v not in marked:
            comps += 1
            M, _ = wfs(n, adj, v, "random")
            marked |= M
    uf = list(range(n))

    def find(x):
        while uf[x] != x:
            x = uf[x]
        return x
    for u, v in und:
        uf[find(u)] = find(v)
    ok &= comps == len({find(v) for v in range(n)})
check("WFSAll counts the components of 200 random undirected graphs", ok)


# ---- depth-first search
def classify(adj, pre, post, parent):
    def anc(u, v):          # u ancestor of v (or equal)?
        while v is not None:
            if v == u:
                return True
            v = parent[v]
        return False
    out = {}
    for u in adj:
        for v in adj[u]:
            if parent[v] == u:              # the edge that discovered v (simple graphs)
                out[(u, v)] = "tree"
            elif anc(u, v) and u != v:
                out[(u, v)] = "forward"
            elif anc(v, u):
                out[(u, v)] = "back"
            else:
                out[(u, v)] = "cross"
    return out


ok_iv, ok_post, ok_never, ok_cycle = True, True, True, True
for _ in range(400):
    n = random.randint(1, 8)
    E = random_digraph(n, 0.3)
    adj = adj_of(n, E)
    order = random.sample(range(n), n)
    pre, post, parent = dfs_post(n, adj, order)
    cl = classify(adj, pre, post, parent)
    for (u, v), c in cl.items():
        if c in ("tree", "forward"):
            ok_iv &= pre[u] < pre[v] < post[v] < post[u]
            ok_post &= post[u] > post[v]
        elif c == "back":
            ok_iv &= pre[v] <= pre[u] < post[u] <= post[v]
            ok_post &= post[u] <= post[v]
        else:
            ok_iv &= pre[v] < post[v] < pre[u] < post[u]
            ok_post &= post[u] > post[v]
        ok_never &= not (post[u] < pre[v])
    # cycle iff back edge iff some edge with post[u] < post[v]
    has_back = any(c == "back" for c in cl.values())
    has_post = any(post[u] < post[v] for (u, v) in E)
    # brute force: a directed cycle exists iff no topological order (Kahn)
    indeg = {v: 0 for v in range(n)}
    for (u, v) in E:
        indeg[v] += 1
    q = [v for v in range(n) if indeg[v] == 0]
    seen = 0
    while q:
        u = q.pop()
        seen += 1
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    cyc = seen < n
    ok_cycle &= cyc == has_back == has_post
check("DFS edge classes match the interval table (tree/forward nested, back containing, cross disjoint)", ok_iv)
check("finishing times: u.post < v.post exactly for back edges", ok_post)
check("no edge u->v ever has u.post < v.pre", ok_never)
check("cycle iff back edge iff some edge has u.post < v.post (400 random digraphs, Kahn as reference)", ok_cycle)

ok = True
for _ in range(200):
    n = random.randint(2, 10)
    und = [(u, v) for u in range(n) for v in range(u + 1, n) if random.random() < 0.3]
    adj = {v: [] for v in range(n)}
    for u, v in und:
        adj[u].append(v)
        adj[v].append(u)
    pre, post, parent = dfs_post(n, adj, random.sample(range(n), n))

    def anc(a, b):
        while b is not None:
            if a == b:
                return True
            b = parent[b]
        return False
    ok &= all(anc(u, v) or anc(v, u) for u, v in und)
check("undirected DFS: every edge joins an ancestor and a descendant", ok)

# reverse postorder is a topological order of a dag
ok = True
for _ in range(300):
    n = random.randint(1, 9)
    E = random_dag(n, 0.35)
    adj = adj_of(n, E)
    pre, post, _ = dfs_post(n, adj, random.sample(range(n), n))
    pos = {v: i for i, v in enumerate(sorted(range(n), key=lambda v: -post[v]))}
    ok &= all(pos[u] < pos[v] for (u, v) in E) and all(post[u] > post[v] for (u, v) in E)
check("in a dag every edge has u.post > v.post, so decreasing finishing time is a topological order", ok)

# preorder is not a topological order (the chapter's example)
names = "abcdef"
Ex = ["ab", "ac", "bd", "cd", "de", "fc"]
adjx = {v: sorted(e[1] for e in Ex if e[0] == v) for v in names}
pre, post, _ = dfs_post(6, {i: [names.index(w) for w in adjx[names[i]]] for i in range(6)})
preorder = "".join(names[v] for v in sorted(range(6), key=lambda v: pre[v]))
is_topo = lambda s: all(s.index(e[0]) < s.index(e[1]) for e in Ex)
check("preorder is not a topological order, read either way (a b d e c f)", preorder == "abdecf" and not is_topo(preorder) and not is_topo(preorder[::-1]))


# Kosaraju-Sharir as stated on the page
def kosaraju(n, adj):
    radj = {v: [] for v in range(n)}
    for u in adj:
        for v in adj[u]:
            radj[v].append(u)
    _, post, _ = dfs_post(n, radj, random.sample(range(n), n))
    comp = {}
    found = []
    for v in sorted(range(n), key=lambda v: -post[v]):       # decreasing finishing time in rev(G)
        if v not in comp:
            # whatever-first search in G from v, restricted to unmarked vertices
            M = set()
            B = [v]
            while B:
                x = B.pop(random.randrange(len(B)))
                if x not in comp and x not in M:
                    M.add(x)
                    B.extend(adj[x])
            for x in M:
                comp[x] = len(found)
            found.append(M)
    return comp, found


ok_scc, ok_sink, ok_dag = True, True, True
for _ in range(400):
    n = random.randint(1, 9)
    E = random_digraph(n, 0.25)
    adj = adj_of(n, E)
    comp, found = kosaraju(n, adj)
    R = {v: reach_brute(n, adj, v) for v in range(n)}
    ok_scc &= all((comp[u] == comp[v]) == (v in R[u] and u in R[v]) for u in range(n) for v in range(n))
    first = found[0]
    ok_sink &= all(comp[v] == comp[next(iter(first))] for (u, v) in E if u in first)
    # condensation is a dag
    CE = {(comp[u], comp[v]) for (u, v) in E if comp[u] != comp[v]}
    k = len(found)
    cadj = {c: [d for (cc, d) in CE if cc == c] for c in range(k)}
    _, cpost, _ = dfs_post(k, cadj)
    ok_dag &= all(cpost[c] > cpost[d] for (c, d) in CE)
check("Kosaraju-Sharir (DFSAll on rev(G), then WFS in G in decreasing finishing time) = mutual reachability", ok_scc)
check("Kosaraju-Sharir finds a sink component first", ok_sink)
check("the condensation scc(G) is a dag", ok_dag)


# ---- shortest paths
def bfs_dist(n, adj, s):
    d = {s: 0}
    q = deque([s])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if v not in d:
                d[v] = d[u] + 1
                q.append(v)
    return d


def brute_dist(n, E, s):
    """shortest walk lengths with no negative cycles: minimum over simple paths"""
    adj = adj_of(n, E)
    best = {v: INF for v in range(n)}

    def go(v, seen, w):
        if w < best[v]:
            best[v] = w
        for x in adj[v]:
            if x not in seen:
                go(x, seen | {x}, w + E[(v, x)])
    go(s, {s}, 0)
    return best


def neg_cycles(n, E):
    """all simple cycles with negative weight, as vertex sets"""
    adj = adj_of(n, E)
    out = []
    for s in range(n):
        def go(v, path, w):
            for x in adj[v]:
                if x == s and w + E[(v, x)] < 0:
                    out.append(set(path))
                elif x > s and x not in path:
                    go(x, path + [x], w + E[(v, x)])
        go(s, [s], 0)
        if (s, s) in E and E[(s, s)] < 0:
            out.append({s})
    return out


ok = True
for _ in range(300):
    n = random.randint(1, 8)
    E = random_digraph(n, 0.3, 1, 1)
    adj = adj_of(n, E)
    s = random.randrange(n)
    d = bfs_dist(n, adj, s)
    b = brute_dist(n, E, s)
    ok &= all(d.get(v, INF) == b[v] for v in range(n))
check("breadth-first search distances = fewest edges (brute force over paths)", ok)


def dag_sssp(n, E, s):
    adj = adj_of(n, E)
    _, post, _ = dfs_post(n, adj)
    dist = {v: INF for v in range(n)}
    dist[s] = 0
    for u in sorted(range(n), key=lambda v: -post[v]):       # topological order
        for v in adj[u]:
            if dist[u] + E[(u, v)] < dist[v]:
                dist[v] = dist[u] + E[(u, v)]
    return dist


ok = True
for _ in range(300):
    n = random.randint(1, 8)
    E = random_dag(n, 0.4, -6, 8)
    s = random.randrange(n)
    ok &= dag_sssp(n, E, s) == brute_dist(n, E, s)
check("DagSSSP (relax in topological order) with negative weights = brute force (300 random dags)", ok)

ok = True
for _ in range(300):
    n = random.randint(1, 8)
    E = random_dag(n, 0.4, -6, 8)
    s = random.randrange(n)
    neg = {e: -w for e, w in E.items()}
    d = dag_sssp(n, neg, s)
    for t in range(n):
        ps = all_paths(n, E, s, t)
        ok &= (-d[t] if d[t] < INF else -INF) == (max(ps) if ps else -INF)
check("longest paths in a dag = DagSSSP with negated weights", ok)


def dijkstra(n, E, s):
    adj = adj_of(n, E)
    dist = {v: INF for v in range(n)}
    dist[s] = 0
    pq = [(0, s)]
    done = set()
    while pq:
        d, u = heapq.heappop(pq)
        if u in done:
            continue
        done.add(u)
        for v in adj[u]:
            if d + E[(u, v)] < dist[v]:
                dist[v] = d + E[(u, v)]
                heapq.heappush(pq, (dist[v], v))
    return dist


ok = True
for _ in range(300):
    n = random.randint(1, 8)
    E = random_digraph(n, 0.35, 0, 9)
    s = random.randrange(n)
    ok &= dijkstra(n, E, s) == brute_dist(n, E, s)
check("Dijkstra (binary heap) with non-negative weights = brute force", ok)


def bellman_ford_dp(n, E, s, rows):
    """dist_{<=i}(v) for i = 0 .. rows, exactly the box's recurrence"""
    D = [[INF] * n for _ in range(rows + 1)]
    D[0][s] = 0
    for i in range(1, rows + 1):
        for v in range(n):
            D[i][v] = min([D[i - 1][v]] + [D[i - 1][u] + w for (u, x), w in E.items() if x == v])
    return D


def walks_upto(n, E, s, i):
    """brute force: min weight of a walk from s with at most i edges, per end vertex"""
    best = {v: INF for v in range(n)}
    best[s] = 0
    frontier = {(s,): 0}
    for _ in range(i):
        new = {}
        for walk, w in frontier.items():
            for (u, v), ww in E.items():
                if u == walk[-1]:
                    new[walk + (v,)] = w + ww
                    best[v] = min(best[v], w + ww)
        frontier = new
    return best


def bellman_ford(n, E, s):
    dist = {v: INF for v in range(n)}
    dist[s] = 0
    for _ in range(n - 1):
        for (u, v), w in E.items():
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
    neg = any(dist[u] + w < dist[v] for (u, v), w in E.items())
    return dist, neg


ok_walks, ok_rows, ok_bf, ok_test, ok_super = True, True, True, True, True
for _ in range(400):
    n = random.randint(1, 5)
    E = random_digraph(n, 0.4, -4, 6)
    s = random.randrange(n)
    D = bellman_ford_dp(n, E, s, n)
    for i in range(min(n, 4) + 1):
        ok_walks &= [D[i][v] for v in range(n)] == [walks_upto(n, E, s, i)[v] for v in range(n)]
    cycles = neg_cycles(n, E)
    R = reach_brute(n, adj_of(n, E), s)
    reachable_neg = any(c & R for c in cycles)
    dist, neg = bellman_ford(n, E, s)
    ok_test &= neg == reachable_neg
    ok_rows &= reachable_neg == any(D[n][v] < D[n - 1][v] for v in range(n))
    if not reachable_neg:
        b = brute_dist(n, E, s)
        ok_rows &= [D[n - 1][v] for v in range(n)] == [b[v] for v in range(n)]
        ok_bf &= [dist[v] for v in range(n)] == [b[v] for v in range(n)]
    # super-source: new vertex n with 0-weight edges to every vertex detects every negative cycle
    E2 = dict(E)
    for v in range(n):
        E2[(n, v)] = 0
    _, neg2 = bellman_ford(n + 1, E2, n)
    ok_super &= neg2 == bool(cycles)
check("Bellman-Ford DP: dist_{<=i}(v) = shortest walk with at most i edges (brute force over walks)", ok_walks)
check("Bellman-Ford DP: row V-1 = distances without negative cycles; row V improves iff a negative cycle is reachable", ok_rows)
check("Bellman-Ford (V-1 rounds) = brute force when no negative cycle is reachable", ok_bf)
check("Bellman-Ford's test (an edge tense after V-1 rounds) iff a negative cycle is reachable from s", ok_test)
check("a super-source with 0-weight edges makes Bellman-Ford detect every negative cycle", ok_super)


def floyd_warshall(n, E, outer="r"):
    d = [[0 if u == v else E.get((u, v), INF) for v in range(n)] for u in range(n)]
    if outer == "r":
        for r in range(n):
            for u in range(n):
                for v in range(n):
                    if d[u][r] + d[r][v] < d[u][v]:
                        d[u][v] = d[u][r] + d[r][v]
    else:                                   # r innermost: u, v, r
        for u in range(n):
            for v in range(n):
                for r in range(n):
                    if d[u][r] + d[r][v] < d[u][v]:
                        d[u][v] = d[u][r] + d[r][v]
    return d


def kleene3(n, E):
    D = [[[0 if u == v else E.get((u, v), INF) for v in range(n)] for u in range(n)]]
    for r in range(n):
        P = D[-1]
        D.append([[min(P[u][v], P[u][r] + P[r][v]) for v in range(n)] for u in range(n)])
    return D[-1]


ok_fw, ok_3d, ok_neg = True, True, True
inner_fails = 0
for _ in range(500):
    n = random.randint(1, 6)
    E = random_digraph(n, 0.4, -4, 7)
    cycles = neg_cycles(n, E)
    d = floyd_warshall(n, E)
    ok_neg &= bool(cycles) == any(d[v][v] < 0 for v in range(n))
    if not cycles:
        ok_3d &= kleene3(n, E) == d
        for s in range(n):
            b = brute_dist(n, E, s)
            ok_fw &= [d[s][v] for v in range(n)] == [b[v] for v in range(n)]
        if floyd_warshall(n, E, "inner") != d:
            inner_fails += 1
check("Floyd-Warshall (r outer, in place, diagonal 0) = brute force without negative cycles", ok_fw)
check("in-place Floyd-Warshall = the three-index recurrence dist(u, v, r)", ok_3d)
check("negative cycle iff dist[v][v] < 0 for some v after Floyd-Warshall (500 random digraphs)", ok_neg)
check("with r as the innermost loop, one pass is sometimes wrong", inner_fails > 0, f"{inner_fails} random graphs")

# layered dag for walks with at most k edges (negative cycles allowed): DagSSSP from (s,0), min over (t, i)
ok = True
for _ in range(300):
    n = random.randint(1, 5)
    E = random_digraph(n, 0.4, -4, 6)
    s = random.randrange(n)
    k = random.randint(0, 4)
    idx = lambda v, i: i * n + v
    H = {}
    for i in range(1, k + 1):
        for (u, v), w in E.items():
            H[(idx(u, i - 1), idx(v, i))] = w
    d = dag_sssp((k + 1) * n, H, idx(s, 0))
    want = walks_upto(n, E, s, k)
    ok &= all(min(d[idx(t, i)] for i in range(k + 1)) == want[t] for t in range(n))
    ok &= len(H) == k * len(E)
check("layered dag (k+1 copies): DagSSSP gives the shortest walks with at most k edges, negative cycles allowed", ok)

# all pairs in a dag: DagSSSP from every vertex = Floyd-Warshall (the parenthesis in the which-algorithm table)
ok = True
for _ in range(200):
    n = random.randint(1, 7)
    E = random_dag(n, 0.4, -6, 8)
    d = floyd_warshall(n, E)
    ok &= all([dag_sssp(n, E, s)[v] for v in range(n)] == d[s] for s in range(n))
check("all pairs in a dag: DagSSSP from every vertex = Floyd-Warshall (200 random dags, negative weights)", ok)

# distances to t = one search from t in rev(G)
ok = True
for _ in range(200):
    n = random.randint(1, 7)
    E = random_digraph(n, 0.35, 0, 9)
    t = random.randrange(n)
    rev = {(v, u): w for (u, v), w in E.items()}
    dt = dijkstra(n, rev, t)
    ok &= all(dt[v] == brute_dist(n, E, v)[t] for v in range(n))
check("distances to t from every vertex = Dijkstra from t in the reversed graph", ok)

# vertex splitting: path weight with vertex weights = shortest path in the split graph
ok = True
for _ in range(200):
    n = random.randint(1, 6)
    E = random_digraph(n, 0.4, 0, 6)
    c = [random.randint(0, 5) for _ in range(n)]
    s, t = random.randrange(n), random.randrange(n)
    H = {(2 * v, 2 * v + 1): c[v] for v in range(n)}            # v_in = 2v, v_out = 2v+1
    for (u, v), w in E.items():
        H[(2 * u + 1, 2 * v)] = w
    got = dijkstra(2 * n, H, 2 * s)[2 * t + 1]
    best = INF
    adj = adj_of(n, E)

    def go(v, seen, w):
        global best
        if v == t:
            best = min(best, w)
        for x in adj[v]:
            if x not in seen:
                go(x, seen | {x}, w + E[(v, x)] + c[x])
    go(s, {s}, c[s])
    ok &= got == best
check("splitting every vertex into v_in -> v_out carries vertex weights correctly", ok)

# tokens as pairs: one token moves -> sum (outdeg x + outdeg y) = 2nm edges; both move -> m^2 edges
ok = True
for _ in range(100):
    n = random.randint(1, 7)
    E = random_digraph(n, 0.4)
    m = len(E)
    out = {v: sum(1 for (u, w) in E if u == v) for v in range(n)}
    one = sum(out[x] + out[y] for x in range(n) for y in range(n))
    both = sum(out[x] * out[y] for x in range(n) for y in range(n))
    ok &= one == 2 * n * m and both == m * m
check("token pairs: n^2 vertices, 2nm edges when one token moves, m^2 when both move", ok)


# Dijkstra for drill C10, two non-re-extracting variants and the re-inserting one
def nonneg_dijkstra(n, E, s, relax_extracted):
    adj = adj_of(n, E)
    dist = {v: INF for v in range(n)}
    dist[s] = 0
    pq = [(0, s)]
    done = set()
    while pq:
        d, u = heapq.heappop(pq)
        if u in done or d > dist[u]:
            continue
        done.add(u)
        for v in adj[u]:
            if v in done and not relax_extracted:
                continue
            if dist[u] + E[(u, v)] < dist[v]:
                dist[v] = dist[u] + E[(u, v)]
                if v not in done:
                    heapq.heappush(pq, (dist[v], v))
    return dist


def reinserting_dijkstra(n, E, s):
    adj = adj_of(n, E)
    dist = {v: INF for v in range(n)}
    dist[s] = 0
    pq = [(0, s)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for v in adj[u]:
            if dist[u] + E[(u, v)] < dist[v]:
                dist[v] = dist[u] + E[(u, v)]
                heapq.heappush(pq, (dist[v], v))
    return dist


# =====================================================================================================
# 6. The drill
# =====================================================================================================
print("== 6. drill")
# B6: Huh(i, j)
n6, k6 = 6, 5
A6 = [random.randint(-3, 5) for _ in range(n6)]


@lru_cache(None)
def huh(i, j):
    if i == 0 or j == 0:
        return 0
    return max(huh(i - 1, j), huh(i, j - 1) + A6[i - 1], 2 * huh(i - 1, j - 1))


huh_deps = lambda e: [] if e[0] == 0 or e[1] == 0 else [(e[0] - 1, e[1]), (e[0], e[1] - 1), (e[0] - 1, e[1] - 1)]
rowmajor = [(i, j) for i in range(n6 + 1) for j in range(k6 + 1)]
colmajor = [(i, j) for j in range(k6 + 1) for i in range(n6 + 1)]
check("drill B6: Huh row by row (i up outer, j up inner) and with the loops swapped are valid orders",
      order_ok(rowmajor, huh_deps) and order_ok(colmajor, huh_deps))
H = {}
for (i, j) in rowmajor:
    H[(i, j)] = 0 if i == 0 or j == 0 else max(H[(i - 1, j)], H[(i, j - 1)] + A6[i - 1], 2 * H[(i - 1, j - 1)])
check("drill B6: the iterative fill equals the recursion; (n+1)(k+1) entries, O(1) each",
      all(H[e] == huh(*e) for e in rowmajor) and len(rowmajor) == (n6 + 1) * (k6 + 1))

# B7: Meh(i, j)
n7 = 8
A7 = [random.randint(-3, 5) for _ in range(n7)]


@lru_cache(None)
def meh(i, j):
    if j <= i + 1:
        return 0
    return A7[i - 1] * A7[j - 1] + min(meh(i, m) + meh(m, j) for m in range(i + 1, j))


meh_deps = lambda e: [] if e[1] <= e[0] + 1 else [(e[0], m) for m in range(e[0] + 1, e[1])] + [(m, e[1]) for m in range(e[0] + 1, e[1])]
o1 = [(i, j) for i in range(n7, 0, -1) for j in range(i, n7 + 1)]
o2 = [(i, i + L) for L in range(0, n7) for i in range(1, n7 - L + 1)]
o_bad = [(i, j) for i in range(1, n7 + 1) for j in range(i, n7 + 1)]
check("drill B7: Meh with i down outer / j up inner, and by increasing j - i, are valid; i up outer is not",
      order_ok(o1, meh_deps) and order_ok(o2, meh_deps) and not order_ok(o_bad, meh_deps))
M7 = {}
for (i, j) in o1:
    M7[(i, j)] = 0 if j <= i + 1 else A7[i - 1] * A7[j - 1] + min(M7[(i, m)] + M7[(m, j)] for m in range(i + 1, j))
check("drill B7: the iterative fill equals the recursion", all(M7[e] == meh(*e) for e in o1))
work = lambda N: sum(max(j - i - 1, 0) for i in range(1, N + 1) for j in range(i, N + 1))
rs = [work(N) / N ** 3 for N in (100, 200, 400)]
check("drill B7: total work of the mins is Theta(n^3) (ratio to n^3 -> 1/6)", abs(rs[-1] - 1 / 6) < 0.01, [round(x, 4) for x in rs])

# C8: unique topological order iff a path through all vertices (all dags on 4 vertices labeled in a topological order)
def topo_count(vs, E):
    c = 0
    for p in itertools.permutations(vs):
        pos = {v: i for i, v in enumerate(p)}
        if all(pos[u] < pos[v] for (u, v) in E):
            c += 1
    return c


pairs = [(u, v) for u in range(4) for v in range(u + 1, 4)]
ok = True
for mask in range(2 ** len(pairs)):
    E = [pairs[t] for t in range(len(pairs)) if mask >> t & 1]
    unique = topo_count(range(4), E) == 1
    ham = all((i, i + 1) in E for i in range(3))
    ok &= unique == ham
check("drill C8: a dag on 4 vertices has exactly one topological order iff it contains a path through all vertices", ok)
check("drill C8: a->b->c->d has exactly one topological order", topo_count("abcd", [("a", "b"), ("b", "c"), ("c", "d")]) == 1)


# C9: four edge types
def dfs_named(V, Es):
    adj = {v: sorted(e[1] for e in Es if e[0] == v) for v in V}
    pre, post, parent = {}, {}, {}
    clock = [0]

    def dfs(v):
        clock[0] += 1
        pre[v] = clock[0]
        for w in adj[v]:
            if w not in pre:
                parent[w] = v
                dfs(w)
        clock[0] += 1
        post[v] = clock[0]
    for v in V:
        if v not in pre:
            parent[v] = None
            dfs(v)

    def anc(u, v):
        while v is not None:
            if v == u:
                return True
            v = parent[v]
        return False
    cls = {}
    for e in Es:
        u, v = e[0], e[1]
        if parent[v] == u:
            cls[e] = "tree"
        elif anc(u, v):
            cls[e] = "forward"
        elif anc(v, u):
            cls[e] = "back"
        else:
            cls[e] = "cross"
    return pre, post, parent, cls


pre, post, parent, cls = dfs_named("abcd", ["ab", "bc", "ac", "ca", "db"])
check("drill C9: times a[1,6], b[2,5], c[3,4], d[7,8]",
      [(pre[v], post[v]) for v in "abcd"] == [(1, 6), (2, 5), (3, 4), (7, 8)])
check("drill C9: a->b, b->c tree; c->a back; a->c forward; d->b cross",
      cls == {"ab": "tree", "bc": "tree", "ca": "back", "ac": "forward", "db": "cross"})

# C10: NonnegativeDijkstra fails
Ec = {(0, 1): 1, (0, 2): 2, (2, 1): -2, (1, 3): 2}        # s=0, a=1, b=2, c=3
check("drill C10: one negative edge, no negative cycle", sum(w < 0 for w in Ec.values()) == 1 and not neg_cycles(4, Ec))
true = brute_dist(4, Ec, 0)
v1 = nonneg_dijkstra(4, Ec, 0, relax_extracted=False)
v2 = nonneg_dijkstra(4, Ec, 0, relax_extracted=True)
v3 = reinserting_dijkstra(4, Ec, 0)
check("drill C10: delta(c) = 2 via s->b->a->c; NonnegativeDijkstra returns 3 (both variants); re-inserting returns 2",
      true[3] == 2 and v1[3] == 3 and v2[3] == 3 and v3[3] == 2 and bellman_ford(4, Ec, 0)[0][3] == 2)

# D: the drill graph, rebuilt from the figure script
from figs_review_mt2 import EDGES as DRILL
VD = "abcdefg"
pre, post, parent, cls = dfs_named(VD, DRILL)
check("drill graph: 7 vertices, 9 edges, a dag", len(DRILL) == 9 and all(c != "back" for c in cls.values()))
times = {v: (pre[v], post[v]) for v in VD}
check("drill D11: times a[1,12] b[2,9] c[3,6] f[4,5] e[7,8] d[10,11] g[13,14]",
      times == {"a": (1, 12), "b": (2, 9), "c": (3, 6), "f": (4, 5), "e": (7, 8), "d": (10, 11), "g": (13, 14)}, times)
check("drill D11: tree a->b, b->c, c->f, b->e, a->d; a->e forward; e->f, d->e, g->d cross",
      {e for e, c in cls.items() if c == "tree"} == {"ab", "bc", "cf", "be", "ad"}
      and cls["ae"] == "forward" and all(cls[e] == "cross" for e in ("ef", "de", "gd")))
revpost = "".join(sorted(VD, key=lambda v: -post[v]))
postord = "".join(sorted(VD, key=lambda v: post[v]))
is_topo_d = lambda s: all(s.index(e[0]) < s.index(e[1]) for e in DRILL)
check("drill D12: decreasing finishing time g a d b e c f; a g b c d e f is another topological order",
      revpost == "gadbecf" and is_topo_d(revpost) and is_topo_d("agbcdef"))
firsts = {p[0] for p in itertools.permutations(VD) if is_topo_d(p)}
check("drill D12: only a and g can come first; 14 topological orders", firsts == {"a", "g"} and topo_count(VD, [tuple(e) for e in DRILL]) == 14)
adjD = {v: sorted(e[1] for e in DRILL if e[0] == v) for v in VD}
N = {}
LP = {}
for v in postord:                     # postorder: f c e b d a g
    N[v] = 1 if v == "f" else sum(N[w] for w in adjD[v])
    LP[v] = max([1 + LP[w] for w in adjD[v]], default=0)


def count_paths(u, t):
    return 1 if u == t else sum(count_paths(w, t) for w in adjD[u])


check("drill D13: postorder f c e b d a g", postord == "fcebdag")
check("drill D13: N(f)=1, N(c)=N(e)=1, N(b)=2, N(d)=1, N(a)=4 paths to f (brute force agrees)",
      [N[v] for v in "fcebda"] == [1, 1, 1, 2, 1, 4] and count_paths("a", "f") == 4)
longest_brute = max(len(p) - 1 for r in range(1, 8) for p in itertools.permutations(VD, r)
                    if p[0] == "a" and all(p[i] + p[i + 1] in DRILL for i in range(len(p) - 1)))
check("drill D13: the longest path from a has 3 edges; a->b->c->f is one", LP["a"] == 3 == longest_brute and all(x in DRILL for x in ("ab", "bc", "cf")))
dB, parB = {"a": 0}, {"a": None}
q = deque("a")
while q:
    u = q.popleft()
    for w in adjD[u]:
        if w not in dB:
            dB[w] = dB[u] + 1
            parB[w] = u
            q.append(w)
check("drill D13: breadth-first tree from a: a->b, a->d, a->e, b->c, e->f; g unreachable",
      {parB[v] + v for v in parB if parB[v]} == {"ab", "ad", "ae", "bc", "ef"} and "g" not in dB)

# =====================================================================================================
# 7. The page says what is checked
# =====================================================================================================
print("== 7. page text")
for s in [
    "$2^n - 1$ exactly", "$\\Theta(n^{\\lg 3}) = O(n^{1.585})$", "$\\Theta(n^{\\lg 7}) = O(n^{2.808})$",
    "root: $\\tfrac15 + \\tfrac7{10} = \\tfrac9{10}$", "equal: $\\tfrac12 + \\tfrac13 + \\tfrac16 = 1$",
    "Level ratio $4/2^2 = 1$: equal, $\\Theta(n^2\\log n)$", "$\\Theta(n^{\\lg 5})\\approx\\Theta(n^{2.32})$",
    "$(5/6)^i n$: root, $\\Theta(n)$", "equal, $\\Theta(\\sqrt n\\log n)$", "sum directly: $\\Theta(\\log^2 n)$",
    "$O(nk)$ time", "$O(n^3)$ time",
    "$a$ $[1, 6]$, $b$ $[2, 5]$, $c$ $[3, 4]$, $d$ $[7, 8]$",
    "$a$ $[1, 12]$, $b$ $[2, 9]$, $c$ $[3, 6]$, $f$ $[4, 5]$, $e$ $[7, 8]$, $d$ $[10, 11]$, $g$ $[13, 14]$",
    "$g, a, d, b, e, c, f$", "$a, g, b, c, d, e, f$", "14 topological orders",
    "$N(a) = N(b) + N(d) + N(e) = 4$", "$a\\to b$, $a\\to d$, $a\\to e$, $b\\to c$, $e\\to f$",
    "$s\\to a$ (weight 1), $s\\to b$ (2), $b\\to a$ ($-2$), $a\\to c$ (2)",
    "pays $4 + 1 + 1$, three coins; $3 + 3$ uses two",
    "$\\mathit{dist}[v, v] < 0$ for some $v$ at the end", "**$r$ is the outer loop**",
    # added in review R19: the statements the checks above implement, as the page prints them
    "\\min\\big\\{\\mathit{dist}_{\\le i-1}(v),\\ \\min_{u\\to v}\\{\\mathit{dist}_{\\le i-1}(u) + w(u\\to v)\\}\\big\\}",
    "\\min\\{\\textsf{dist}(u, v, r-1),\\ \\textsf{dist}(u, r, r-1) + \\textsf{dist}(r, v, r-1)\\}",
    "| tree or forward ($v$ a descendant of $u$) | $u.\\mathit{pre} < v.\\mathit{pre} < v.\\mathit{post} < u.\\mathit{post}$ | $u.\\mathit{post} > v.\\mathit{post}$ |",
    "| back ($v$ an ancestor of $u$, still active) | $v.\\mathit{pre} < u.\\mathit{pre} < u.\\mathit{post} < v.\\mathit{post}$ | $u.\\mathit{post} < v.\\mathit{post}$ |",
    "| cross ($v$ finished, unrelated) | $v.\\mathit{pre} < v.\\mathit{post} < u.\\mathit{pre} < u.\\mathit{post}$ | $u.\\mathit{post} > v.\\mathit{post}$ |",
    "above 1: $\\Theta(n^\\rho)$, where $\\sum_i\\alpha_i^{\\,\\rho} = 1$",
    "every level sums to at most $n$ (the first $\\log_6 n$ levels to exactly $n$)",
    "a $\\max$ over nothing is 0 in $\\textsf{LISfirst}$ but $-\\infty$ in $\\textsf{LLP}$",
    "in a dag: DagSSSP from every vertex, $O(VE)$",
    "a negative cycle is reachable from $s$ exactly when row $V$ would still improve some entry",
]:
    check("page states: " + s[:70], on_page(s))

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: " + "; ".join(FAIL))
