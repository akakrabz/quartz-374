#!/usr/bin/env python3
"""Checks for every concrete claim on content/2-algorithms/03-dynamic-programming.md and the concept pages
dynamic-programming, memoization, edit-distance, optimal-binary-search-trees, dynamic-programming-on-trees.

Every recurrence is implemented as stated on the pages, every pseudocode block is transcribed loop for loop
(with arrays that refuse out-of-range indices and reads of unwritten entries, so evaluation orders and index
ranges are tested too), and everything is compared with brute force on all small inputs plus random ones."""
import functools
import itertools
import math
import os
import random
import re
import sys
from collections import deque

sys.setrecursionlimit(10000)
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
PAGE = os.path.join(ROOT, "content", "2-algorithms", "03-dynamic-programming.md")
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


def table_row(text, label):
    """Cells (after the label cell) of the first markdown table row whose first cell is `label`."""
    for ln in text.splitlines():
        t = ln.lstrip("> ").strip()
        if t.startswith("|"):
            cells = [c.strip() for c in t.strip("|").split("|")]
            if cells[0] == label:
                return cells[1:]
    raise KeyError(label)


def num(c):
    c = c.replace("*", "").strip()
    return None if c == "" else int(c)


class Arr:
    """Array with declared inclusive index ranges; reading an unwritten entry or using an index outside the
    declared ranges raises IndexError (the pseudocode would be wrong)."""

    def __init__(self, *ranges):
        self.ranges = ranges
        self.d = {}
        self.writes = []

    def _key(self, k):
        k = k if isinstance(k, tuple) else (k,)
        if len(k) != len(self.ranges) or any(not (lo <= x <= hi) for x, (lo, hi) in zip(k, self.ranges)):
            raise IndexError(f"index {k} outside {self.ranges}")
        return k

    def __getitem__(self, k):
        k = self._key(k)
        if k not in self.d:
            raise IndexError(f"read of unwritten entry {k}")
        return self.d[k]

    def __setitem__(self, k, v):
        k = self._key(k)
        self.d[k] = v
        self.writes.append(k)

    def defined(self, k):
        return self._key(k) in self.d


def raises(f, *a):
    try:
        f(*a)
        return False
    except IndexError:
        return True


page = read(PAGE)
NEG = float("-inf")

# =====================================================================================================
# 3.1 Fibonacci
# =====================================================================================================
FIB = [0, 1]
while len(FIB) < 3000:
    FIB.append(FIB[-1] + FIB[-2])


def F(k):
    """Fibonacci numbers for all integers, F(-k) = (-1)^(k+1) F(k)."""
    return FIB[k] if k >= 0 else (-1) ** (-k + 1) * FIB[-k]


phi = (1 + 5 ** 0.5) / 2


def meters(n):
    """All sequences of light (1 beat, '•') and heavy (2 beats, '—') syllables with n beats."""
    if n == 0:
        return [""]
    out = [m + "•" for m in meters(n - 1)]
    if n >= 2:
        out += [m + "—" for m in meters(n - 2)]
    return out


check("M(n) = number of n-beat meters = F(n+1), and M(n) = M(n-1) + M(n-2), M(0) = M(1) = 1, n <= 20",
      all(len(meters(n)) == FIB[n + 1] for n in range(21)) and len(meters(0)) == 1 and len(meters(1)) == 1)
check("exactly five 4-beat meters: — —, — • •, • — •, • • —, • • • •",
      sorted(meters(4)) == sorted(["——", "—••", "•—•", "••—", "••••"]), str(meters(4)))


def rec_fibo_calls(n):
    cnt = {}

    def RecFibo(n):
        cnt[n] = cnt.get(n, 0) + 1
        if n == 0:
            return 0
        elif n == 1:
            return 1
        else:
            return RecFibo(n - 1) + RecFibo(n - 2)

    return RecFibo(n), cnt


ok_val = ok_T = ok_leaves = ok_k = True
book_k_wrong = False
T = {}
for n in range(0, 23):
    v, cnt = rec_fibo_calls(n)
    total = sum(cnt.values())
    T[n] = total
    ok_val &= v == FIB[n]
    ok_T &= total == 2 * FIB[n + 1] - 1
    if n >= 1:
        ok_leaves &= cnt.get(1, 0) == FIB[n] and cnt.get(0, 0) == FIB[n - 1]
        ok_k &= all(cnt[n - k] == FIB[k + 1] for k in range(0, n))
        if n >= 2 and any(cnt[n - k] != F(k - 1) for k in range(0, n)):
            book_k_wrong = True
check("RecFibo(n) = F(n) for n <= 22", ok_val)
check("RecFibo makes T(n) = 2F(n+1) - 1 calls, n <= 22", ok_T)
check("T(0) = T(1) = 1 and T(n) = T(n-1) + T(n-2) + 1", T[0] == 1 and T[1] == 1
      and all(T[n] == T[n - 1] + T[n - 2] + 1 for n in range(2, 23)))
check("induction step (2F_n - 1) + (2F_{n-1} - 1) + 1 = 2F_{n+1} - 1",
      all((2 * FIB[n] - 1) + (2 * FIB[n - 1] - 1) + 1 == 2 * FIB[n + 1] - 1 for n in range(1, 200)))
check("leaves: F(n) calls RecFibo(1) and F(n-1) calls RecFibo(0); F(n+1) leaves, 2F(n+1)-1 nodes (full binary tree)",
      ok_leaves and all(2 * (FIB[n] + FIB[n - 1]) - 1 == 2 * FIB[n + 1] - 1 for n in range(1, 50)))
check("RecFibo(n-k) is called F(k+1) times for 0 <= k < n (1, 1, 2, 3, 5, ...)", ok_k)
check("the book's F(k-1) is wrong (e.g. k = 1: one call, but F(0) = 0)", book_k_wrong and F(0) != 1)
check("book's list: 1, 2, 3, 5 calls to RecFibo(n-1..n-4) = F(k+1) for k = 1..4",
      [FIB[k + 1] for k in (1, 2, 3, 4)] == [1, 2, 3, 5])
check("T(7) = 41 (Figure 3.1 has 41 nodes), T(6) = 25", T[7] == 41 and T[6] == 25)
check("phi = (1+sqrt5)/2 ~ 1.61803 and F(n) = Theta(phi^n): F(n)/phi^n -> 1/sqrt5",
      abs(phi - 1.61803) < 1e-5 and abs(FIB[60] / phi ** 60 - 1 / 5 ** 0.5) < 1e-12)


def mem_fibo(n):
    Fm = {}
    calls = [0]
    order = []

    def MemFibo(n):
        calls[0] += 1
        if n == 0:
            return 0
        elif n == 1:
            return 1
        else:
            if n not in Fm:
                Fm[n] = MemFibo(n - 1) + MemFibo(n - 2)
                order.append(n)
            return Fm[n]

    return MemFibo(n), calls[0], order


ok = True
for n in range(1, 300):
    v, c, order = mem_fibo(n)
    ok &= v == FIB[n] and c == 2 * n - 1 and order == list(range(2, n + 1))
check("MemFibo(n) = F(n), makes 2n-1 calls (n >= 1), fills F[2], F[3], ..., F[n] in that order (n < 300)", ok)
check("MemFibo performs n-1 additions (one per entry F[2..n]): O(n)", all(len(mem_fibo(n)[2]) == n - 1 for n in range(1, 100)))


def IterFibo(n):
    Fa = Arr((0, max(n, 1)))
    Fa[0] = 0
    Fa[1] = 1
    for i in range(2, n + 1):
        Fa[i] = Fa[i - 1] + Fa[i - 2]
    return Fa[n]


def IterFibo2(n):
    prev, curr = 1, 0
    for i in range(1, n + 1):
        nxt = curr + prev
        prev = curr
        curr = nxt
    return curr


check("IterFibo(n) = F(n) for 0 <= n <= 300", all(IterFibo(n) == FIB[n] for n in range(301)))
check("IterFibo2(n) = F(n) for 0 <= n <= 300 (IterFibo2(0) = 0 via F(-1) = 1)",
      all(IterFibo2(n) == FIB[n] for n in range(301)) and IterFibo2(0) == 0 and F(-1) == 1)


@functools.lru_cache(None)
def Fib(i):
    return i if i <= 1 else Fib(i - 1) + Fib(i - 2)


check("rubric-format Fib(i): base Fib(i) = i for i <= 1, recurrence matches F", all(Fib(i) == FIB[i] for i in range(200)))

# =====================================================================================================
# 3.2 Faster Fibonacci
# =====================================================================================================


def matmul(X, Y):
    return [[X[0][0] * Y[0][0] + X[0][1] * Y[1][0], X[0][0] * Y[0][1] + X[0][1] * Y[1][1]],
            [X[1][0] * Y[0][0] + X[1][1] * Y[1][0], X[1][0] * Y[0][1] + X[1][1] * Y[1][1]]]


def matpow(X, n):
    """Repeated squaring; returns (X^n, number of matrix multiplications)."""
    if n == 0:
        return [[1, 0], [0, 1]], 0
    H, c = matpow(X, n // 2)
    R = matmul(H, H)
    c += 1
    if n % 2:
        R = matmul(R, X)
        c += 1
    return R, c


Mx = [[0, 1], [1, 1]]
ok = all([Mx[0][0] * x + Mx[0][1] * y, Mx[1][0] * x + Mx[1][1] * y] == [y, x + y] for x in range(-5, 6) for y in range(-5, 6))
check("[[0,1],[1,1]] (x, y) = (y, x+y)", ok)
ok = True
mults = 0
for n in range(0, 400):
    P, c = matpow(Mx, n)
    v = [P[0][0] * 1 + P[0][1] * 0, P[1][0] * 1 + P[1][1] * 0]
    ok &= v == [F(n - 1), F(n)]
    if n >= 1:
        ok &= c <= 2 * (n.bit_length())
check("M^n (1, 0) = (F(n-1), F(n)) for 0 <= n < 400, with O(log n) matrix products by repeated squaring", ok)
check("identity F_n = F_m F_{n-m-1} + F_{m+1} F_{n-m} for all integers -30 <= m, n <= 30",
      all(F(n) == F(m) * F(n - m - 1) + F(m + 1) * F(n - m) for m in range(-30, 31) for n in range(-30, 31)))
check("substituting (n, m) -> (2n-1, n-1) gives F_{2n-1} = F_{n-1}^2 + F_n^2",
      all(F(m) * F((2 * n - 1) - m - 1) + F(m + 1) * F((2 * n - 1) - m) == F(n - 1) ** 2 + F(n) ** 2
          for n in range(-20, 40) for m in [n - 1]))
check("substituting (n, m) -> (2n, n) gives F_{2n} = F_n (F_{n-1} + F_{n+1}) = F_n (2F_{n-1} + F_n)",
      all(F(n) * F(n - 1) + F(n + 1) * F(n) == F(2 * n) == F(n) * (F(n - 1) + F(n + 1)) == F(n) * (2 * F(n - 1) + F(n))
          for n in range(-20, 40)))


def fast_rec_fibo(n, calls):
    calls[0] += 1
    if n == 1:
        return 0, 1
    m = n // 2
    hprv, hcur = fast_rec_fibo(m, calls)
    prev = hprv ** 2 + hcur ** 2
    curr = hcur * (2 * hprv + hcur)
    nxt = prev + curr
    if n % 2 == 0:
        return prev, curr
    else:
        return curr, nxt


ok = True
for n in range(1, 2500):
    c = [0]
    ok &= fast_rec_fibo(n, c) == (FIB[n - 1], FIB[n]) and c[0] == n.bit_length() == math.floor(math.log2(n)) + 1
check("FastRecFibo(n) = (F(n-1), F(n)) with floor(log2 n) + 1 calls, 1 <= n < 2500", ok)
check("log10(phi) ~ 0.209 ~ 1/5 and log2(phi) ~ 0.694 (book: ~ 2/3)",
      abs(math.log10(phi) - 0.209) < 0.001 and abs(math.log2(phi) - 0.694) < 0.001 and abs(math.log10(phi) - 0.2) < 0.01)
check("F(n) has ~ n log10 phi decimal digits and ~ n log2 phi bits (n = 2000)",
      abs(len(str(FIB[2000])) / 2000 - math.log10(phi)) < 0.002 and abs(FIB[2000].bit_length() / 2000 - math.log2(phi)) < 0.002)
ratios = [sum(FIB[i].bit_length() for i in range(n + 1)) / n ** 2 for n in (500, 1000, 2000)]
check("IterFibo: n additions of O(n)-bit numbers = Theta(n^2) bit operations (sum of bit lengths / n^2 -> log2(phi)/2)",
      all(abs(r - math.log2(phi) / 2) < 0.01 for r in ratios), str([round(r, 4) for r in ratios]))
Tb = {0: 1, 1: 1}
for n in range(2, 200):
    Tb[n] = Tb[n - 1] + Tb[n - 2] + n
r1, r2 = Tb[150] / phi ** 150, Tb[199] / phi ** 199
check("T(n) = T(n-1) + T(n-2) + n is Theta(phi^n) (ratio settles)", abs(r1 / r2 - 1) < 1e-6, f"{r1:.6f} vs {r2:.6f}")


def Tfast(n):
    return 0 if n <= 1 else Tfast(n // 2) + n * math.log2(n)


rs = [Tfast(2 ** k) / (2 ** k * k) for k in (10, 15, 20)]
rs2 = [Tfast(n) / (n * math.log2(n)) for n in (10 ** 5 + 7, 10 ** 6 + 3)]
check("T(n) = T(floor(n/2)) + M(n) with M(n) = n log n is O(M(n)) (ratio bounded by 2)", all(r <= 2 for r in rs + rs2),
      str([round(r, 3) for r in rs + rs2]))

# =====================================================================================================
# 3.3 Text segmentation
# =====================================================================================================


def splittable_rec(A, D):
    n = len(A)

    @functools.lru_cache(None)
    def S(i):
        if i > n:
            return True
        return any(A[i - 1:j] in D and S(j + 1) for j in range(i, n + 1))

    return S(1), S


def FastSplittable(A, D):
    n = len(A)
    calls = [0]

    def IsWord(i, j):
        calls[0] += 1
        return A[i - 1:j] in D

    ST = Arr((1, n + 1))
    ST[n + 1] = True
    for i in range(n, 0, -1):
        ST[i] = False
        for j in range(i, n + 1):
            if IsWord(i, j) and ST[j + 1]:
                ST[i] = True
    return ST[1], calls[0], ST


def backtrack_splittable(A, D):
    n = len(A)
    calls = [0]

    def IsWord(i, j):
        calls[0] += 1
        return A[i - 1:j] in D

    def Splittable(i):
        if i > n:
            return True
        for j in range(i, n + 1):
            if IsWord(i, j):
                if Splittable(j + 1):
                    return True
        return False

    return Splittable(1), calls[0]


def segmentations(A, D):
    n = len(A)
    out = []
    for cuts in itertools.product([0, 1], repeat=max(n - 1, 0)):
        pieces, start = [], 0
        for k, c in enumerate(cuts):
            if c:
                pieces.append(A[start:k + 1])
                start = k + 1
        pieces.append(A[start:])
        if all(p in D for p in pieces):
            out.append(pieces)
    return out if n else [[]]


ok = True
cnt = 0
short = ["".join(p) for L in range(1, 4) for p in itertools.product("ab", repeat=L)]
for trial in range(60):
    D = set(random.sample(short, random.randint(1, 8)))
    for L in range(0, 9):
        for t in itertools.product("ab", repeat=L):
            A = "".join(t)
            bf = len(segmentations(A, D)) > 0
            r, _ = splittable_rec(A, D)
            f, c, _ = FastSplittable(A, D)
            b, _ = backtrack_splittable(A, D)
            ok &= r == f == b == bf and c == L * (L + 1) // 2
            cnt += 1
check(f"Splittable recurrence = FastSplittable = backtracking = brute force; FastSplittable makes n(n+1)/2 IsWord calls ({cnt} cases)", ok)
ok = all(backtrack_splittable("a" * (n - 1) + "b", {"a" * k for k in range(1, n + 1)}) == (False, 2 ** n - 1)
         for n in range(1, 16))
check("backtracking on a^(n-1) b with every string of a's a word: False after exactly 2^n - 1 IsWord calls (n <= 15)", ok)

DW = {"THE", "THEM", "END", "MEN", "MENTOR"}
res, calls, ST = FastSplittable("THEMENTOR", DW)
row = ["T" if ST[i] else "F" for i in range(1, 11)]
check("THEMENTOR: SplitTable[1..10] = T F F T F F F F F T (as in the page's table)",
      row == list("TFFTFFFFFT") and table_row(page, r"$\mathit{SplitTable}[i]$") == row, "".join(row))
check("THEMENTOR: A[4..9] = MENTOR, A[1..3] = THE; the only segmentation is THE·MENTOR",
      "THEMENTOR"[3:9] == "MENTOR" and "THEMENTOR"[0:3] == "THE" and segmentations("THEMENTOR", DW) == [["THE", "MENTOR"]])

# =====================================================================================================
# 3.5 Greed
# =====================================================================================================


def greedy_segment(A, D, pick):
    """Take the shortest/longest prefix that is a word, commit to it, repeat; True iff it reaches the end."""
    pieces = []
    while A:
        pre = [A[:k] for k in range(1, len(A) + 1) if A[:k] in D]
        if not pre:
            return False, pieces, A
        w = min(pre, key=len) if pick == "shortest" else max(pre, key=len)
        pieces.append(w)
        A = A[len(w):]
    return True, pieces, ""


g1 = greedy_segment("THEMENTOR", DW, "shortest")
g2 = greedy_segment("THEMENTOR", DW, "longest")
check("shortest-prefix greedy takes THE, MEN and is stuck at TOR", g1 == (False, ["THE", "MEN"], "TOR"), str(g1))
check("longest-prefix greedy takes THEM and is stuck at ENTOR", g2 == (False, ["THEM"], "ENTOR"), str(g2))


def lis_brute(A):
    n = len(A)
    best = 0
    for mask in range(1 << n):
        s = [A[k] for k in range(n) if mask >> k & 1]
        if all(s[t] < s[t + 1] for t in range(len(s) - 1)):
            best = max(best, len(s))
    return best


def lis_greedy(A):
    """Smallest element first (leftmost if tied), then repeat to its right among larger elements."""
    seq, lo, start = [], NEG, 0
    while True:
        cand = [(A[k], k) for k in range(start, len(A)) if A[k] > lo]
        if not cand:
            return seq
        v, k = min(cand)
        seq.append(v)
        lo, start = v, k + 1


check("LIS greedy on [3,4,5,1,2] picks 1, 2 (length 2); the LIS has length 3 (3, 4, 5)",
      lis_greedy([3, 4, 5, 1, 2]) == [1, 2] and lis_brute([3, 4, 5, 1, 2]) == 3)

# =====================================================================================================
# 3.6 LIS
# =====================================================================================================


def lisbigger_rec(A):
    n = len(A)
    B = [NEG] + list(A)

    @functools.lru_cache(None)
    def L(i, j):
        if j > n:
            return 0
        if B[i] >= B[j]:
            return L(i, j + 1)
        return max(L(i, j + 1), 1 + L(j, j + 1))

    return L(0, 1)


def FastLIS(A, order="columns"):
    n = len(A)
    B = Arr((0, n))
    B[0] = NEG
    for k in range(1, n + 1):
        B[k] = A[k - 1]
    L = Arr((0, n), (1, n + 1))
    for i in range(0, n + 1):
        L[i, n + 1] = 0

    def entry(i, j):
        keep = 1 + L[j, j + 1]
        skip = L[i, j + 1]
        L[i, j] = skip if B[i] >= B[j] else max(keep, skip)

    if order == "columns":            # the book's order: j = n down to 1, then i = 0 .. j-1
        for j in range(n, 0, -1):
            for i in range(0, j):
                entry(i, j)
    elif order == "columns-reversed-inner":
        for j in range(n, 0, -1):
            for i in range(j - 1, -1, -1):
                entry(i, j)
    elif order == "rows-top":         # rows i = 0..n-1 from the top, each row j = n down to i+1
        for i in range(0, n):
            for j in range(n, i, -1):
                entry(i, j)
    elif order == "rows-bottom":      # rows i = n-1 down to 0, each row j = n down to i+1
        for i in range(n - 1, -1, -1):
            for j in range(n, i, -1):
                entry(i, j)
    return L[0, 1]


def lisfirst_rec(A):
    n = len(A)
    B = [NEG] + list(A)

    @functools.lru_cache(None)
    def L(i):
        return 1 + max([L(j) for j in range(i + 1, n + 1) if B[j] > B[i]], default=0)

    return L(0) - 1, [L(i) for i in range(n + 1)]


def FastLIS2(A):
    n = len(A)
    B = [NEG] + list(A)
    L = Arr((0, n))
    for i in range(n, -1, -1):
        L[i] = 1
        for j in range(i + 1, n + 1):
            if B[j] > B[i] and 1 + L[j] > L[i]:
                L[i] = 1 + L[j]
    return L[0] - 1, [L[i] for i in range(n + 1)]


ok = True
cnt = 0
arrays = [list(t) for L in range(0, 8) for t in itertools.product(range(1, 5), repeat=L)]
arrays += [[random.randint(-20, 20) for _ in range(random.randint(8, 13))] for _ in range(300)]
for A in arrays:
    b = lis_brute(A)
    ok &= (lisbigger_rec(A) == FastLIS(A) == FastLIS(A, "columns-reversed-inner") == FastLIS(A, "rows-bottom")
           == lisfirst_rec(A)[0] == FastLIS2(A)[0] == b)
    cnt += 1
check(f"LISbigger recurrence = FastLIS (book order and reversed inner loop) = LISfirst recurrence = FastLIS2 = brute force ({cnt} arrays, all arrays of length <= 7 over 1..4)", ok)
check("FastLIS also works with rows from the bottom up (each row right to left)",
      all(FastLIS(A, "rows-bottom") == lis_brute(A) for A in arrays[:3000]))
check("FastLIS with rows from the top reads an unwritten entry (e.g. A = [2, 1, 3])",
      raises(FastLIS, [2, 1, 3], "rows-top") and all(raises(FastLIS, A, "rows-top") for A in arrays if len(A) >= 2))
check("LISfirst base case: max of the empty set = 0 gives LISfirst(n) = 1",
      all(lisfirst_rec(A)[1][len(A)] == 1 for A in arrays if A))
A8 = [3, 1, 4, 1, 5, 9, 2, 6]
ans, Lf = FastLIS2(A8)
check("example A = [3,1,4,1,5,9,2,6]: LISfirst[0..8] = 5 4 4 3 3 2 1 2 1 (as in the page's table), answer 4",
      Lf == [5, 4, 4, 3, 3, 2, 1, 2, 1] and ans == 4 and [num(c) for c in table_row(page, r"$\mathit{LISfirst}[i]$")] == Lf, str(Lf))
check("LISfirst[3] = 1 + max(LISfirst[5], LISfirst[6], LISfirst[8]) = 3; later elements > 4 are 5, 9, 6",
      [j for j in range(4, 9) if A8[j - 1] > 4] == [5, 6, 8] and [A8[j - 1] for j in (5, 6, 8)] == [5, 9, 6]
      and Lf[3] == 1 + max(Lf[5], Lf[6], Lf[8]) == 3)
check("3, 4, 5, 9 is an increasing subsequence of A of length 4",
      any([A8[a], A8[b], A8[c], A8[d]] == [3, 4, 5, 9] for a, b, c, d in itertools.combinations(range(8), 4)))

# =====================================================================================================
# 3.7 Edit distance
# =====================================================================================================


def edit_rec(A, B):
    @functools.lru_cache(None)
    def E(i, j):
        if j == 0:
            return i
        if i == 0:
            return j
        return min(E(i, j - 1) + 1, E(i - 1, j) + 1, E(i - 1, j - 1) + (A[i - 1] != B[j - 1]))

    return E(len(A), len(B)), E


def EditDistance(A, B):
    m, n = len(A), len(B)
    E = Arr((0, m), (0, n))
    for j in range(0, n + 1):
        E[0, j] = j
    for i in range(1, m + 1):
        E[i, 0] = i
        for j in range(1, n + 1):
            ins = E[i, j - 1] + 1
            dele = E[i - 1, j] + 1
            if A[i - 1] == B[j - 1]:
                rep = E[i - 1, j - 1]
            else:
                rep = E[i - 1, j - 1] + 1
            E[i, j] = min(ins, dele, rep)
    return E[m, n], E


def edit_bfs(A, B):
    """Shortest sequence of single-letter insertions, deletions, substitutions, by breadth-first search over strings
    of length <= max(|A|, |B|) over the letters of A and B (an optimal sequence can delete first, then substitute,
    then insert, so this restriction loses nothing)."""
    sigma = sorted(set(A + B)) or ["a"]
    cap = max(len(A), len(B))
    dist = {A: 0}
    Q = deque([A])
    while Q:
        s = Q.popleft()
        if s == B:
            return dist[s]
        nbrs = set()
        for k in range(len(s)):
            nbrs.add(s[:k] + s[k + 1:])
            for c in sigma:
                nbrs.add(s[:k] + c + s[k + 1:])
        if len(s) < cap:
            for k in range(len(s) + 1):
                for c in sigma:
                    nbrs.add(s[:k] + c + s[k:])
        for t in nbrs:
            if t not in dist:
                dist[t] = dist[s] + 1
                Q.append(t)


def traceback(A, B, E):
    """The page's recovery rule; returns the alignment (top, bottom)."""
    i, j = len(A), len(B)
    top, bot = [], []
    while i > 0 or j > 0:
        if i > 0 and j > 0 and E[i, j] == E[i - 1, j - 1] + (A[i - 1] != B[j - 1]):
            top.append(A[i - 1]); bot.append(B[j - 1]); i -= 1; j -= 1
        elif j > 0 and E[i, j] == E[i, j - 1] + 1:
            top.append("_"); bot.append(B[j - 1]); j -= 1
        else:
            assert i > 0 and E[i, j] == E[i - 1, j] + 1
            top.append(A[i - 1]); bot.append("_"); i -= 1
    return "".join(reversed(top)), "".join(reversed(bot))


def align_cost(top, bot):
    assert len(top) == len(bot)
    return sum(a != b for a, b in zip(top, bot))


def is_alignment(top, bot, A, B):
    return top.replace("_", "") == A and bot.replace("_", "") == B and not any(a == b == "_" for a, b in zip(top, bot))


ok = True
cnt = 0
strs = ["".join(t) for L in range(0, 5) for t in itertools.product("ab", repeat=L)]
pairs = [(a, b) for a in strs for b in strs]
pairs += [("".join(random.choice("abc") for _ in range(random.randint(0, 6))),
           "".join(random.choice("abc") for _ in range(random.randint(0, 6)))) for _ in range(400)]
match_shortcut = True
for A, B in pairs:
    d, E = EditDistance(A, B)
    r, Er = edit_rec(A, B)
    bf = edit_bfs(A, B)
    top, bot = traceback(A, B, E)
    ok &= d == r == bf and is_alignment(top, bot, A, B) and align_cost(top, bot) == d
    for i in range(1, len(A) + 1):
        for j in range(1, len(B) + 1):
            if A[i - 1] == B[j - 1]:
                match_shortcut &= E[i, j] == E[i - 1, j - 1]
    cnt += 1
check(f"Edit recurrence = EditDistance (row-major, as written) = breadth-first search; traceback gives an alignment of that cost ({cnt} pairs)", ok)
check("if A[i] = B[j] then Edit(i,j) = Edit(i-1,j-1) (the matching shortcut is correct, in all those tables)", match_shortcut)


def edit_colmajor(A, B):
    m, n = len(A), len(B)
    E = Arr((0, m), (0, n))
    for j in range(0, n + 1):
        for i in range(0, m + 1):
            if j == 0:
                E[i, j] = i
            elif i == 0:
                E[i, j] = j
            else:
                E[i, j] = min(E[i, j - 1] + 1, E[i - 1, j] + 1, E[i - 1, j - 1] + (A[i - 1] != B[j - 1]))
    return E[m, n]


check("column-major evaluation order works too", all(edit_colmajor(A, B) == EditDistance(A, B)[0] for A, B in pairs[:2000]))

A1, B1 = "ALGORITHM", "ALTRUISTIC"
d, E = EditDistance(A1, B1)
# the book's table (p. 115), rows = ALTRUISTIC prefixes j = 0..10, columns = ALGORITHM prefixes i = 0..9
BOOK = """0 1 2 3 4 5 6 7 8 9
1 0 1 2 3 4 5 6 7 8
2 1 0 1 2 3 4 5 6 7
3 2 1 1 2 3 4 4 5 6
4 3 2 2 2 2 3 4 5 6
5 4 3 3 3 3 3 4 5 6
6 5 4 4 4 4 3 4 5 6
7 6 5 5 5 5 4 4 5 6
8 7 6 6 6 6 5 4 5 6
9 8 7 7 7 7 6 5 5 6
10 9 8 8 8 8 7 6 6 6"""
book = [[int(x) for x in ln.split()] for ln in BOOK.splitlines()]
check("ALGORITHM vs ALTRUISTIC: our table Edit[0..9, 0..10] is the transpose of the book's printed table",
      all(E[i, j] == book[j][i] for i in range(10) for j in range(11)))
check("edit distance ALGORITHM / ALTRUISTIC = 6 (table and recurrence)", d == 6 == edit_rec(A1, B1)[0])


def optimal_paths(A, B, E):
    @functools.lru_cache(None)
    def P(i, j):
        if i == 0 and j == 0:
            return [("", "")]
        out = []
        if i > 0 and j > 0 and E[i, j] == E[i - 1, j - 1] + (A[i - 1] != B[j - 1]):
            out += [(t + A[i - 1], b + B[j - 1]) for t, b in P(i - 1, j - 1)]
        if j > 0 and E[i, j] == E[i, j - 1] + 1:
            out += [(t + "_", b + B[j - 1]) for t, b in P(i, j - 1)]
        if i > 0 and E[i, j] == E[i - 1, j] + 1:
            out += [(t + A[i - 1], b + "_") for t, b in P(i - 1, j)]
        return out

    return P(len(A), len(B))


paths = optimal_paths(A1, B1, E)
book_al = {("ALGORI_THM", "ALTRUISTIC"), ("ALGOR_I_THM", "AL_TRUISTIC"), ("ALGOR_I_THM", "ALT_RUISTIC")}
check("exactly three optimal paths = the book's three alignments, each of cost 6",
      len(paths) == 3 and set(paths) == book_al and all(align_cost(t, b) == 6 for t, b in paths), str(paths))
page_al = re.findall(r"^([A-Z_](?: [A-Z_])+)\s{3,}([A-Z_](?: [A-Z_])+)\s{3,}([A-Z_](?: [A-Z_])+)$", page, re.M)
if len(page_al) == 2:
    tops, bots = page_al
    shown = {(tops[k].replace(" ", ""), bots[k].replace(" ", "")) for k in range(3)}
else:
    shown = set()
check("the three alignments printed on the page are exactly those", shown == book_al, str(shown))
check("intro alignment A L G O R _ I _ T H M / A L _ T R U I S T I C is a valid alignment of cost 6",
      is_alignment("ALGOR_I_THM", "AL_TRUISTIC", A1, B1) and align_cost("ALGOR_I_THM", "AL_TRUISTIC") == 6
      and "A L G O R _ I _ T H M" in page and "A L _ T R U I S T I C" in page)
check("FOOD / MONEY: edit distance 4 (no three edits suffice), alignment F O O _ D / M O N E Y costs 4",
      EditDistance("FOOD", "MONEY")[0] == 4 == edit_bfs("FOOD", "MONEY") and is_alignment("FOO_D", "MONEY", "FOOD", "MONEY")
      and align_cost("FOO_D", "MONEY") == 4)


def one_edit(s, t):
    return edit_bfs(s, t) == 1


check("FOOD -> MOOD -> MOND -> MONED -> MONEY: each step is one edit",
      all(one_edit(s, t) for s, t in zip(["FOOD", "MOOD", "MOND", "MONED"], ["MOOD", "MOND", "MONED", "MONEY"])))
check("(m+1)(n+1) entries: 10 x 11 = 110 for ALGORITHM / ALTRUISTIC", len(E.d) == 110)

# =====================================================================================================
# 3.8 Subset sum
# =====================================================================================================


def ss_direct(X, T):
    n = len(X)

    @functools.lru_cache(None)
    def SS(i, t):
        if t == 0:
            return True
        if t < 0 or i > n:
            return False
        return SS(i + 1, t) or SS(i + 1, t - X[i - 1])

    return SS(1, T)


def ss_modified(X, T):
    n = len(X)

    @functools.lru_cache(None)
    def SS(i, t):
        assert t >= 0
        if t == 0:
            return True
        if i > n:
            return False
        if t < X[i - 1]:
            return SS(i + 1, t)
        return SS(i + 1, t) or SS(i + 1, t - X[i - 1])

    return SS(1, T)


def FastSubsetSum(X, T, book_bound=False):
    """The page's pseudocode: first inner loop t = 1 .. min{X[i] - 1, T} (book_bound=True: t = 1 .. X[i] - 1 as printed)."""
    n = len(X)
    S = Arr((1, n + 1), (0, T))
    S[n + 1, 0] = True
    for t in range(1, T + 1):
        S[n + 1, t] = False
    for i in range(n, 0, -1):
        S[i, 0] = True
        for t in range(1, (X[i - 1] - 1 if book_bound else min(X[i - 1] - 1, T)) + 1):
            S[i, t] = S[i + 1, t]
        for t in range(X[i - 1], T + 1):
            S[i, t] = S[i + 1, t] or S[i + 1, t - X[i - 1]]
    return S[1, T], S


def ss_brute(X, T):
    return any(sum(c) == T for r in range(len(X) + 1) for c in itertools.combinations(X, r))


ok = True
cnt = 0
for trial in range(400):
    X = [random.randint(1, 12) for _ in range(random.randint(0, 8))]
    for T_ in range(0, sum(X) + 3):
        r = FastSubsetSum(X, T_)[0]
        ok &= r == ss_direct(X, T_) == ss_modified(X, T_) == ss_brute(X, T_)
        cnt += 1
for X in itertools.product(range(1, 5), repeat=4):
    for T_ in range(0, 18):
        ok &= FastSubsetSum(list(X), T_)[0] == ss_brute(X, T_) == ss_modified(list(X), T_)
        cnt += 1
check(f"SS direct recurrence = modified recurrence = FastSubsetSum (as written) = brute force ({cnt} cases)", ok)
X1, X2 = [8, 6, 7, 5, 3, 10, 9], [11, 6, 5, 1, 7, 13, 12]
check("book examples: {8,6,7,5,3,10,9}, T=15 True; {11,6,5,1,7,13,12}, T=15 False",
      FastSubsetSum(X1, 15)[0] and not FastSubsetSum(X2, 15)[0])
check("8+7 = 7+5+3 = 6+9 = 5+10 = 15, all subsets of X", all(sum(s) == 15 and set(s) <= set(X1) for s in ([8, 7], [7, 5, 3], [6, 9], [5, 10])))
check("FastSubsetSum fills (n+1)(T+1) entries", len(FastSubsetSum(X1, 15)[1].d) == 8 * 16)
check("the page's first inner loop runs to min{X[i] - 1, T}", "for t ← 1 to min{X[i] − 1, T}" in page)
ok = True
for trial in range(300):
    X = [random.randint(1, 12) for _ in range(random.randint(1, 6))]
    T_ = random.randint(0, 14)
    ok &= raises(FastSubsetSum, X, T_, True) == any(x > T_ + 1 for x in X)
    if not any(x > T_ + 1 for x in X):
        ok &= FastSubsetSum(X, T_, True)[0] == ss_brute(X, T_)
check("the book's bound X[i] - 1 indexes past column T exactly when some X[i] > T + 1 (e.g. X = [5], T = 2)",
      ok and raises(FastSubsetSum, [5], 2, True) and not raises(FastSubsetSum, [5], 2))

# =====================================================================================================
# 3.9 Optimal binary search trees
# =====================================================================================================


def InitF(f):
    n = len(f)
    Fa = Arr((1, n), (0, n))
    for i in range(1, n + 1):
        Fa[i, i - 1] = 0
        for k in range(i, n + 1):
            Fa[i, k] = Fa[i, k - 1] + f[k - 1]
    return Fa


def obst_tables(f, order="diagonal", book3_bug=False):
    n = len(f)
    Fa = InitF(f)
    C = Arr((1, n + 1), (0, n))
    Rt = {}
    inner = [0]

    def ComputeOptCost(i, k):
        best = math.inf
        for r in range(i, k + 1):
            inner[0] += 1
            tmp = C[i, r - 1] + C[r + 1, k]
            if best > tmp:
                best = tmp
                Rt[i, k] = r
        C[i, k] = best + Fa[i, k]

    if order == "diagonal":
        for i in range(1, n + 2):
            C[i, i - 1] = 0
        for d in range(0, n):
            for i in range(1, n - d + 1):
                ComputeOptCost(i, i + d)
    elif order == "rows":                         # OptimalBST2
        for i in range(n + 1, 0, -1):
            C[i, i - 1] = 0
            for j in range(i, n + 1):
                ComputeOptCost(i, j)
    elif order == "columns":                      # OptimalBST3, outer loop j = 0 .. n (or n+1 as printed)
        for j in range(0, (n + 1 if book3_bug else n) + 1):
            C[j + 1, j] = 0
            for i in range(j, 0, -1):
                ComputeOptCost(i, j)
    return C, Rt, inner[0]


def all_bsts(i, k):
    """All BSTs on keys i..k as nested tuples (root, left, right); None for empty."""
    if i > k:
        return [None]
    return [(r, L, R) for r in range(i, k + 1) for L in all_bsts(i, r - 1) for R in all_bsts(r + 1, k)]


def bst_cost(t, f, depth=1):
    if t is None:
        return 0
    r, L, R = t
    return f[r - 1] * depth + bst_cost(L, f, depth + 1) + bst_cost(R, f, depth + 1)


def optcost_rec(f):
    n = len(f)

    @functools.lru_cache(None)
    def OC(i, k):
        if i > k:
            return 0
        return sum(f[i - 1:k]) + min(OC(i, r - 1) + OC(r + 1, k) for r in range(i, k + 1))

    return OC(1, n)


ok = True
cnt = 0
for trial in range(250):
    n = random.randint(0, 7)
    f = [random.randint(1, 9) for _ in range(n)]
    bf = min(bst_cost(t, f) for t in all_bsts(1, n))
    c1 = obst_tables(f, "diagonal")
    c2 = obst_tables(f, "rows")
    c3 = obst_tables(f, "columns")
    same = all(c1[0][i, k] == c2[0][i, k] == c3[0][i, k] for i in range(1, n + 2) for k in range(i - 1, n + 1))
    ok &= same and c1[0][1, n] == bf == optcost_rec(f)
    ok &= c1[2] == c2[2] == c3[2] == n * (n + 1) * (n + 2) // 6
    cnt += 1
check(f"OptCost recurrence = OptimalBST (diagonals) = rows = columns (j = 0..n) = brute force over all BSTs; inner loop runs n(n+1)(n+2)/6 times ({cnt} instances, n <= 7)", ok)
check("Catalan check: number of BSTs on 1..7 keys = 1, 2, 5, 14, 42, 132, 429",
      [len(all_bsts(1, n)) for n in range(1, 8)] == [1, 2, 5, 14, 42, 132, 429])
check("the book's OptimalBST3 with outer loop j = 0 .. n+1 indexes outside OptCost[1..n+1, 0..n]",
      all(raises(obst_tables, [random.randint(1, 9) for _ in range(n)], "columns", True) for n in range(0, 6)))
check("InitF: F[i,k] = f[i] + ... + f[k]", all(InitF(f)[i, k] == sum(f[i - 1:k]) for f in [[5, 2, 1, 3, 4], [1], [3, 3, 3]]
                                              for i in range(1, len(f) + 1) for k in range(i - 1, len(f) + 1)))
f5 = [5, 2, 1, 3, 4]
C5, R5, _ = obst_tables(f5)
want = {1: [0, 5, 9, 12, 21, 31], 2: [None, 0, 2, 4, 10, 18], 3: [None, None, 0, 1, 5, 13], 4: [None, None, None, 0, 3, 10],
        5: [None, None, None, None, 0, 4], 6: [None, None, None, None, None, 0]}
got = {i: [C5[i, k] if k >= i - 1 else None for k in range(0, 6)] for i in range(1, 7)}
pg = {i: [num(c) for c in table_row(page, str(i))] for i in range(1, 7)}
check("f = [5,2,1,3,4]: OptCost table as on the page", got == want == pg, str(got))
sums = [C5[1, r - 1] + C5[r + 1, 5] for r in range(1, 6)]
check("last entry: F[1,5] = 15, root sums 18, 18, 19, 16, 21; min 16 at r = 4 (unique); OptCost[1,5] = 31",
      InitF(f5)[1, 5] == 15 and sums == [18, 18, 19, 16, 21] and sums.index(min(sums)) == 3 and sums.count(16) == 1
      and C5[1, 5] == 31)
opt_trees = [t for t in all_bsts(1, 5) if bst_cost(t, f5) == 31]
check("the optimal tree is unique: root A[4], right child A[5], left child A[1] -> right A[2] -> right A[3]",
      opt_trees == [(4, (1, None, (2, None, (3, None, None))), (5, None, None))]
      and min(bst_cost(t, f5) for t in all_bsts(1, 5)) == 31)
check("its cost 3*1 + (5+4)*2 + 2*3 + 1*4 = 31", 3 * 1 + (5 + 4) * 2 + 2 * 3 + 1 * 4 == 31)


def greedy_bst(f, i, k):
    if i > k:
        return None
    r = max(range(i, k + 1), key=lambda r: (f[r - 1], -r))
    return (r, greedy_bst(f, i, r - 1), greedy_bst(f, r + 1, k))


g = greedy_bst(f5, 1, 5)
check("most-frequent-key-at-root greedy: path A[1], A[5], A[4], A[2], A[3], cost 35",
      g == (1, None, (5, (4, (2, None, (3, None, None)), None), None)) and bst_cost(g, f5) == 35, str(g))

# =====================================================================================================
# 3.10 Trees
# =====================================================================================================


class Node:
    def __init__(self, name):
        self.name = name
        self.children = []


def build(parent):
    """parent: dict child -> parent (root has parent None). Returns root Node and dict name -> Node."""
    nodes = {v: Node(v) for v in parent}
    root = None
    for v, p in parent.items():
        if p is None:
            root = nodes[v]
        else:
            nodes[p].children.append(nodes[v])
    return root, nodes


def TreeMIS(v, work):
    skipv = 0
    for w in v.children:
        skipv = skipv + TreeMIS(w, work)
        work[0] += 1
    keepv = 1
    for w in v.children:
        for x in w.children:
            keepv = keepv + x.MIS
            work[0] += 1
    v.MIS = max(keepv, skipv)
    return v.MIS


def TreeMIS2(v):
    v.MISno = 0
    v.MISyes = 1
    for w in v.children:
        v.MISno = v.MISno + TreeMIS2(w)
        v.MISyes = v.MISyes + w.MISno
    return max(v.MISyes, v.MISno)


def mis_rec(v):
    return max(sum(mis_rec(w) for w in v.children), 1 + sum(mis_rec(x) for w in v.children for x in w.children))


def mis_brute(parent):
    vs = list(parent)
    edges = [(v, p) for v, p in parent.items() if p is not None]
    best = 0
    for mask in range(1 << len(vs)):
        S = {vs[k] for k in range(len(vs)) if mask >> k & 1}
        if not any(a in S and b in S for a, b in edges):
            best = max(best, len(S))
    return best


def random_tree(n):
    parent = {0: None}
    for v in range(1, n):
        parent[v] = random.randrange(v)
    return parent


def prufer_trees(n):
    """All labeled trees on n >= 2 vertices (Prüfer sequences), rooted at 0, as parent dicts."""
    for seq in itertools.product(range(n), repeat=n - 2):
        deg = [1] * n
        for x in seq:
            deg[x] += 1
        adj = {v: [] for v in range(n)}
        s = list(seq)
        for x in s:
            leaf = min(v for v in range(n) if deg[v] == 1)
            adj[leaf].append(x); adj[x].append(leaf)
            deg[leaf] -= 1; deg[x] -= 1
        u, w = [v for v in range(n) if deg[v] == 1]
        adj[u].append(w); adj[w].append(u)
        parent = {0: None}
        stack = [0]
        while stack:
            v = stack.pop()
            for w in adj[v]:
                if w not in parent:
                    parent[w] = v
                    stack.append(w)
        yield parent


ok = True
lin = True
cnt = 0
trees = [{0: None}] + [p for n in range(2, 7) for p in prufer_trees(n)] + [random_tree(random.randint(1, 13)) for _ in range(500)]
for parent in trees:
    root, nodes = build(parent)
    work = [0]
    a = TreeMIS(root, work)
    root2, _ = build(parent)
    b = TreeMIS2(root2)
    bf = mis_brute(parent)
    ok &= a == b == mis_rec(root) == bf
    lin &= work[0] <= 2 * len(parent)
    cnt += 1
check(f"MIS recurrence = TreeMIS = TreeMIS2 = brute force ({cnt} rooted trees: all labeled trees on <= 6 vertices + random <= 13)", ok)
check("TreeMIS work (child + grandchild visits) <= 2n: each vertex counted once by its parent and once by its grandparent", lin)
check("a leaf gets MIS = max(0, 1) = 1; MISyes(leaf) = 1, MISno(leaf) = 0",
      TreeMIS(build({0: None})[0], [0]) == 1 and TreeMIS2(build({0: None})[0]) == 1)


# ---------------- the tree drawn in a03-tree-mis (same dict, same drawing order as tools/figs_a03.py)
FIG_TREE = {"r": None, "a": "r", "b": "r", "c": "r", "d": "a", "e": "a", "f": "d", "g": "d", "h": "d", "i": "e", "j": "e"}
root, nodes = build(FIG_TREE)
best = TreeMIS2(root)
check("figure tree: 11 vertices, largest independent set 8 = brute force; root values MISyes 6, MISno 8; a: 6 / 5",
      len(FIG_TREE) == 11 and best == 8 == mis_brute(FIG_TREE) and (nodes["r"].MISyes, nodes["r"].MISno) == (6, 8)
      and (nodes["a"].MISyes, nodes["a"].MISno) == (6, 5))

# =====================================================================================================
# Figures: the numbers drawn in tools/figs/a03-*.html
# =====================================================================================================
TEXT = re.compile(r'<text x="([\d.]+)" y="([\d.]+)"[^>]*fill="([^"]+)" style="([^"]*)">(.*?)</text>')

fig = read(os.path.join(FIGS, "a03-fib-tree.html"))
labels = [(m.group(3), re.search(r"<tspan[^>]*>(\d+)</tspan>", m.group(5)).group(1))
          for m in TEXT.finditer(fig) if m.group(5).startswith("F<tspan")]


def preorder(n):
    return [n] + ([] if n <= 1 else preorder(n - 1) + preorder(n - 2))


check("fib figure: 25 nodes, in preorder the calls of RecFibo(6)", [int(l) for _, l in labels] == preorder(6) and len(labels) == 25)
called = [l for c, l in labels if c != "var(--muted)"]
check("fib figure: exactly 2*6 - 1 = 11 nodes in color (MemFibo's calls); the lookups (preorder) are F2, F3, F4",
      len(called) == 11 and [l for c, l in labels if c == "var(--hi)"] == ["2", "3", "4"], str(called))
check("fib caption numbers: 25 = 2F7 - 1, 13 leaves = F6 + F5 = 8 + 5",
      25 == 2 * FIB[7] - 1 and FIB[6] == 8 and FIB[5] == 5 and preorder(6).count(1) == 8 and preorder(6).count(0) == 5)

fig = read(os.path.join(FIGS, "a03-edit-table.html"))
nums = [(float(m.group(1)), float(m.group(2)), m.group(3), m.group(4), m.group(5)) for m in TEXT.finditer(fig)
        if re.fullmatch(r"\d+", m.group(5))]
xs = sorted({x for x, *_ in nums})
ys = sorted({y for _, y, *_ in nums})
grid_fig = {(ys.index(y), xs.index(x)): (int(t), c, "font-weight:700" in st) for x, y, c, st, t in nums}
okt = len(xs) == 11 and len(ys) == 10 and all(grid_fig[i, j][0] == E[i, j] for i in range(10) for j in range(11))
okb = all(grid_fig[i, j][2] == (i > 0 and j > 0 and A1[i - 1] == B1[j - 1]) for i in range(10) for j in range(11))
check("edit figure: all 110 numbers equal Edit[i, j] (rows ALGORITHM, columns ALTRUISTIC)", okt)
check("edit figure: bold red exactly where A[i] = B[j]", okb)
edges_union = set()
for t, b in paths:
    i = j = 0
    for x, y in zip(t, b):
        ni, nj = i + (x != "_"), j + (y != "_")
        edges_union.add(((i, j), (ni, nj)))
        i, j = ni, nj
arrows = len(re.findall(r'<line [^>]*marker-end="url\(#ARR\)"', fig))
check("edit figure: one arrow per move used by the three optimal paths", arrows == len(edges_union), f"{arrows} arrows, {len(edges_union)} moves")

fig = read(os.path.join(FIGS, "a03-tree-mis.html"))
vals = [m.group(5) for m in TEXT.finditer(fig) if re.fullmatch(r"\d+ / \d+", m.group(5))]
rects = re.findall(r'<rect [^>]*rx="13" fill="([^"]+)"', fig)
check("tree figure: labels MISyes / MISno at every vertex, in drawing order",
      vals == [f"{nodes[v].MISyes} / {nodes[v].MISno}" for v in FIG_TREE], str(vals))
shaded = {v for v, f in zip(FIG_TREE, rects) if f == "var(--accent)"}
edges_t = [(v, p) for v, p in FIG_TREE.items() if p]
check("tree figure: the shaded vertices a, b, c, f, g, h, i, j form an independent set of size 8",
      shaded == set("abcfghij") and not any(u in shaded and w in shaded for u, w in edges_t) and len(shaded) == 8)
check("tree caption: root max{6, 8} = 8, exclude root (8 > 6), take a (6 > 5)",
      max(nodes["r"].MISyes, nodes["r"].MISno) == 8 and nodes["a"].MISyes > nodes["a"].MISno)

fig = read(os.path.join(FIGS, "a03-dependencies.html"))
RECT = re.compile(r'<rect x="([\d.]+)" y="([\d.]+)" width="18" height="18" rx="0" fill="([^"]+)" fill-opacity="([\d.]+)" stroke="([^"]+)"')
cs_, TOP_, cols_ = 18, 52, [56, 270, 484]
marked = {0: {"target": set(), "dep": set()}, 1: {"target": set(), "dep": set()}, 2: {"target": set(), "dep": set()}}
for m in RECT.finditer(fig):
    x, y = float(m.group(1)), float(m.group(2))
    if not (TOP_ <= y < TOP_ + 6 * cs_):
        continue
    p = max(k for k in range(3) if x >= cols_[k])
    r, c = int(round((y - TOP_) / cs_)), int(round((x - cols_[p]) / cs_))
    kind = "target" if m.group(5) == "var(--hi)" else "dep" if m.group(5) == "var(--accent)" else None
    if kind:
        marked[p][kind].add((r, c))
# panel A: rows i = r, columns j = c + 1; panel B: (i, j) = (r, c); panel C: (i, k) = (r + 1, c)
tA = {(r, c + 1) for r, c in marked[0]["target"]}
dA = {(r, c + 1) for r, c in marked[0]["dep"]}
(ia, ja), = tA
check("dependency figure, LISbigger: entry (1, 3) reads (i, j+1) and (j, j+1)", tA == {(1, 3)} and dA == {(ia, ja + 1), (ja, ja + 1)})
(ib, jb), = marked[1]["target"]
check("dependency figure, Edit: entry (3, 3) reads (i-1, j), (i, j-1), (i-1, j-1)",
      (ib, jb) == (3, 3) and marked[1]["dep"] == {(ib - 1, jb), (ib, jb - 1), (ib - 1, jb - 1)})
tC = {(r + 1, c) for r, c in marked[2]["target"]}
dC = {(r + 1, c) for r, c in marked[2]["dep"]}
(ic, kc), = tC
check("dependency figure, OptCost: entry (2, 4) reads OptCost[i, r-1] and OptCost[r+1, k] for i <= r <= k",
      tC == {(2, 4)} and dC == {(ic, r - 1) for r in range(ic, kc + 1)} | {(r + 1, kc) for r in range(ic, kc + 1)}, str(sorted(dC)))

# =====================================================================================================
# Concept pages
# =====================================================================================================
cdp = read(os.path.join(CONCEPTS, "dynamic-programming.md"))
cmemo = read(os.path.join(CONCEPTS, "memoization.md"))
cedit = read(os.path.join(CONCEPTS, "edit-distance.md"))
cobst = read(os.path.join(CONCEPTS, "optimal-binary-search-trees.md"))
ctree = read(os.path.join(CONCEPTS, "dynamic-programming-on-trees.md"))

# ---- dynamic-programming: making change


def MinCoinsTable(D, T):
    M = Arr((0, T))
    M[0] = 0
    for t in range(1, T + 1):
        M[t] = 1 + min([M[t - d] for d in D if d <= t], default=math.inf)
    return M


def coins_brute(D, T):
    """Fewest coins by breadth-first search over sums."""
    dist = {0: 0}
    Q = deque([0])
    while Q:
        s = Q.popleft()
        if s == T:
            return dist[s]
        for d in D:
            if s + d <= T and s + d not in dist:
                dist[s + d] = dist[s] + 1
                Q.append(s + d)
    return math.inf


def coins_greedy(D, T):
    out = []
    while T:
        d = max(x for x in D if x <= T)
        out.append(d)
        T -= d
    return out


ok = True
for trial in range(200):
    D = sorted({1} | {random.randint(2, 15) for _ in range(random.randint(0, 4))})
    M = MinCoinsTable(D, 60)
    ok &= all(M[t] == coins_brute(D, t) for t in range(61))
check("MinCoins recurrence (filled t = 0..T) = breadth-first search, 200 random coin systems containing 1, T <= 60", ok)
M = MinCoinsTable([1, 4, 5], 8)
check("D = (1,4,5): MinCoins[0..8] = 0 1 2 3 1 1 2 3 2; greedy for 8 is 5+1+1+1 (4 coins), optimum 4+4 (2 coins)",
      [M[t] for t in range(9)] == [0, 1, 2, 3, 1, 1, 2, 3, 2] and coins_greedy([1, 4, 5], 8) == [5, 1, 1, 1]
      and "$0, 1, 2, 3, 1, 1, 2, 3, 2$" in cdp)
check("dynamic-programming page: RecFibo 2F(n+1)-1 calls vs n+1 distinct arguments", all(T[n] == 2 * FIB[n + 1] - 1 for n in range(20)))

# ---- memoization: binomial coefficients


def choose_naive(n, k):
    c = [0]

    def C(n, k):
        c[0] += 1
        if k == 0 or k == n:
            return 1
        return C(n - 1, k - 1) + C(n - 1, k)

    return C(n, k), c[0]


def choose_memo(n, k):
    memo, c = {}, [0]

    def C(n, k):
        c[0] += 1
        if k == 0 or k == n:
            return 1
        if (n, k) not in memo:
            memo[n, k] = C(n - 1, k - 1) + C(n - 1, k)
        return memo[n, k]

    return C(n, k), c[0], set(memo)


ok = True
for n in range(0, 17):
    for k in range(0, n + 1):
        v, c = choose_naive(n, k)
        v2, c2, keys = choose_memo(n, k)
        want = {(a + b, a) for a in range(1, k + 1) for b in range(1, n - k + 1)}
        ok &= v == v2 == math.comb(n, k) and c == 2 * math.comb(n, k) - 1 and keys == want and len(keys) == k * (n - k) \
            and c2 == 2 * k * (n - k) + 1
check("Choose: naive 2C(n,k)-1 calls; memoized exactly the k(n-k) subproblems with 1<=k'<=k, 1<=n'-k'<=n-k, 2k(n-k)+1 calls (n <= 16)", ok)
check("C(10,5) = 252: 503 naive calls; 25 memoized subproblems, 51 calls",
      choose_naive(10, 5) == (252, 503) and choose_memo(10, 5)[1] == 51 and len(choose_memo(10, 5)[2]) == 25)
check("memoization page: MemFibo 2n-1 calls, RecFibo(n-k) called F(k+1) times (checked above)", ok_k and all(mem_fibo(n)[1] == 2 * n - 1 for n in range(1, 50)))

# ---- edit-distance: FOOD / MONEY
dF, EF = EditDistance("FOOD", "MONEY")
rows = []
blk = cedit[cedit.index("| | | M | O | N | E | Y |"):]
for ln in blk.splitlines()[2:7]:
    cells = [c.strip() for c in ln.strip().strip("|").split("|")]
    rows.append(cells)
tab = [[int(c.replace("*", "")) for c in r[1:]] for r in rows]
bold = {(i, j) for i, r in enumerate(rows) for j, c in enumerate(r[1:]) if c.startswith("**")}
check("FOOD/MONEY table on the concept page = EditDistance table; distance 4",
      tab == [[EF[i, j] for j in range(6)] for i in range(5)] and dF == 4 and [r[0] for r in rows] == ["", "F", "O", "O", "D"])
tb = traceback("FOOD", "MONEY", EF)
check("diagonal-first read-back gives F O _ O D / M O N E Y (cost 4)", tb == ("FO_OD", "MONEY") and align_cost(*tb) == 4)
# cells visited by the read-back
i, j, visited = 4, 5, {(4, 5)}
for x, y in zip(reversed(tb[0]), reversed(tb[1])):
    i, j = i - (x != "_"), j - (y != "_")
    visited.add((i, j))
check("bold entries = the read-back path (0,0),(1,1),(2,2),(2,3),(3,4),(4,5)", bold == visited == {(0, 0), (1, 1), (2, 2), (2, 3), (3, 4), (4, 5)})
pF = optimal_paths("FOOD", "MONEY", EF)
check("FOOD/MONEY has exactly three optimal alignments: FO_OD, FOO_D, FOOD_ over MONEY",
      sorted(pF) == sorted([("FO_OD", "MONEY"), ("FOO_D", "MONEY"), ("FOOD_", "MONEY")]))

# ---- optimal-binary-search-trees: f = (2, 3, 4)
f3 = [2, 3, 4]
C3, R3, _ = obst_tables(f3)
g3 = greedy_bst(f3, 1, 3)
check("f = (2,3,4): greedy builds the path A[3], A[2], A[1], cost 4*1 + 3*2 + 2*3 = 16",
      g3 == (3, (2, (1, None, None), None), None) and bst_cost(g3, f3) == 16 == 4 * 1 + 3 * 2 + 2 * 3)
check("f = (2,3,4): balanced tree rooted at A[2] costs 3*1 + (2+4)*2 = 15 = optimum (brute force)",
      bst_cost((2, (1, None, None), (3, None, None)), f3) == 15 == min(bst_cost(t, f3) for t in all_bsts(1, 3)) == C3[1, 3])
check("f = (2,3,4): F[1,3] = 9; root sums 10, 6, 7 (OptCost[2,3] = 10, [1,1] + [3,3] = 2 + 4, [1,2] = 7); min 6 at r = 2",
      InitF(f3)[1, 3] == 9 and [C3[1, r - 1] + C3[r + 1, 3] for r in (1, 2, 3)] == [10, 6, 7] and C3[2, 3] == 10
      and C3[1, 1] == 2 and C3[3, 3] == 4 and C3[1, 2] == 7 and R3[1, 3] == 2)


def obst_rows_topdown(f):
    n = len(f)
    Fa = InitF(f)
    C = Arr((1, n + 1), (0, n))
    for i in range(1, n + 2):
        C[i, i - 1] = 0
    for i in range(1, n + 1):
        for k in range(i, n + 1):
            C[i, k] = Fa[i, k] + min(C[i, r - 1] + C[r + 1, k] for r in range(i, k + 1))
    return C[1, n]


check("row by row from the top reads unfilled entries (every n >= 2)", all(raises(obst_rows_topdown, [1] * n) for n in range(2, 7)))

# ---- dynamic-programming-on-trees: vertex cover, naive MIS on a path


def vc_tree(parent):
    kids_ = {v: [w for w, p in parent.items() if p == v] for v in parent}
    rt = next(v for v, p in parent.items() if p is None)
    vin, vout = {}, {}

    def post(v):
        vin[v], vout[v] = 1, 0
        for w in kids_[v]:
            post(w)
            vin[v] += min(vin[w], vout[w])
            vout[v] += vin[w]

    post(rt)
    return min(vin[rt], vout[rt])


def vc_brute(parent):
    vs = list(parent)
    edges = [(v, p) for v, p in parent.items() if p is not None]
    return min(len(S) for r in range(len(vs) + 1) for S in map(set, itertools.combinations(vs, r))
               if all(a in S or b in S for a, b in edges))


ok = all(vc_tree(t) == vc_brute(t) == len(t) - mis_brute(t) for t in trees[:1200])
check("VCin/VCout recurrence = brute force = n - MIS on 1200 rooted trees", ok)
cover = {"r", "d", "e"}
check("figure tree: smallest vertex cover 3 = 11 - 8; {r, d, e} (root, two non-leaf grandchildren) is a cover",
      vc_tree(FIG_TREE) == 3 == 11 - 8 and all(v in cover or p in cover for v, p in FIG_TREE.items() if p)
      and FIG_TREE["d"] == FIG_TREE["e"] == "a" and FIG_TREE["a"] == "r")


def naive_mis_calls(n):
    parent = {0: None}
    for v in range(1, n):
        parent[v] = v - 1
    root_, _ = build(parent)
    c = [0]

    def M(v):
        c[0] += 1
        return max(sum(M(w) for w in v.children), 1 + sum(M(x) for w in v.children for x in w.children))

    M(root_)
    return c[0]


check("naive grandchildren MIS on an n-vertex path rooted at an end makes F(n+2) - 1 calls (n <= 22)",
      all(naive_mis_calls(n) == FIB[n + 2] - 1 for n in range(1, 23)))

# =====================================================================================================
print()
if FAIL:
    print(f"{len(FAIL)} FAILED:", *FAIL, sep="\n  ")
    sys.exit(1)
print("ALL OK")
