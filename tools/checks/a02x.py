#!/usr/bin/env python3
"""Checks for content/2-algorithms/02-backtracking-exercises.md (Erickson, Algorithms, Chapter 2 exercises).

Every recursive algorithm / recursive definition on the page is implemented exactly as the page states it
(memoized with lru_cache only to save time; memoization does not change the values) and compared with an
independent brute force on all small inputs plus random larger ones. Every number on the page (the book's
examples, call counts, example values) is checked here as well."""
import itertools
import random
import sys
from functools import lru_cache

sys.setrecursionlimit(100000)
FAIL = []
INF = float("inf")
NEG = float("-inf")
random.seed(374)


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAIL.append(name)


def subsets(n):
    """All index subsets of range(n), as tuples."""
    for r in range(n + 1):
        yield from itertools.combinations(range(n), r)


def is_subseq(x, y):
    it = iter(y)
    return all(c in it for c in x)


# =====================================================================================================
# Exercise 2.1 — subset sum variants
# =====================================================================================================
def num_subsets(X, T):
    """NumSubsets(i, T) exactly as on the page; X is 1-indexed via X[i-1]."""
    calls = [0]

    def rec(i, t):
        calls[0] += 1
        if t == 0:
            return 1
        elif t < 0 or i == 0:
            return 0
        else:
            with_ = rec(i - 1, t - X[i - 1])
            wout = rec(i - 1, t)
            return with_ + wout
    return rec(len(X), T), calls[0]


def max_weight(X, W, T):
    def rec(i, t):
        if t == 0:
            return 0
        elif t < 0 or i == 0:
            return NEG
        else:
            with_ = W[i - 1] + rec(i - 1, t - X[i - 1])
            wout = rec(i - 1, t)
            return max(with_, wout)
    return rec(len(X), T)


def bf_count(X, T):
    return sum(1 for S in subsets(len(X)) if sum(X[i] for i in S) == T)


def bf_maxw(X, W, T):
    best = NEG
    for S in subsets(len(X)):
        if sum(X[i] for i in S) == T:
            best = max(best, sum(W[i] for i in S))
    return best


ok_a = ok_b = True
cnt = 0
for n in range(0, 7):
    for X in itertools.product(range(1, 5), repeat=n):
        for T in range(-1, sum(X) + 2):
            cnt += 1
            if num_subsets(X, T)[0] != bf_count(X, T):
                ok_a = False
for _ in range(3000):
    n = random.randint(0, 8)
    X = [random.randint(1, 6) for _ in range(n)]
    T = random.randint(-1, sum(X) + 1)
    if num_subsets(X, T)[0] != bf_count(X, T):
        ok_a = False
check("Ex 2.1(a) NumSubsets = brute-force count (all X over {1..4}, n<=6, all T; 3000 random)", ok_a, f"{cnt} exhaustive cases")
for n in range(0, 6):
    for X in itertools.product(range(1, 4), repeat=n):
        for W in itertools.product(range(1, 4), repeat=n):
            for T in range(-1, sum(X) + 2):
                if max_weight(X, W, T) != bf_maxw(X, W, T):
                    ok_b = False
for _ in range(3000):
    n = random.randint(0, 9)
    X = [random.randint(1, 6) for _ in range(n)]
    W = [random.randint(1, 20) for _ in range(n)]
    T = random.randint(-1, sum(X) + 1)
    if max_weight(X, W, T) != bf_maxw(X, W, T):
        ok_b = False
check("Ex 2.1(b) MaxWeight = brute-force max weight, -inf if no subset (all X,W over {1..3}, n<=5; 3000 random)", ok_b)

bx = [8, 6, 7, 5, 3, 10, 9]
c, _ = num_subsets(bx, 15)
check("book example: X = {8,6,7,5,3,10,9}, T = 15 has exactly 4 subsets ({8,7},{7,5,3},{6,9},{5,10})", c == 4 and bf_count(bx, 15) == 4, c)
c2, _ = num_subsets([11, 6, 5, 1, 7, 13, 12], 15)
check("book example: X = {11,6,5,1,7,13,12}, T = 15 has 0 subsets", c2 == 0, c2)
# zero elements would break the T = 0 base case (positivity matters)
check("trap: with a zero element allowed, 'T = 0 -> 1' undercounts (X = (0, 1), T = 1 has 2 subsets)",
      num_subsets([0, 1], 1)[0] == 1 and bf_count([0, 1], 1) == 2)
# call counts: worst case (T larger than the sum) makes 2^(n+1) - 1 calls; T(n) = 2T(n-1) + O(1)
ok = all(num_subsets([1] * n, n + 1)[1] == 2 ** (n + 1) - 1 for n in range(0, 15))
check("worst case (T > sum X): NumSubsets makes exactly 2^(n+1) - 1 calls, so Theta(2^n)", ok)
ok = all(num_subsets(X, T)[1] <= 2 ** (len(X) + 1) - 1 for X in itertools.product(range(1, 4), repeat=5) for T in range(0, 17))
check("NumSubsets never makes more than 2^(n+1) - 1 calls (n = 5, all X over {1..3})", ok)
# example on the page for (b): X = (8,6,7,5,3,10,9), W = (1,..,7) ?
bw = [2, 5, 1, 4, 3, 1, 2]
mw = max_weight(bx, bw, 15)
check("page example (b): X = (8,6,7,5,3,10,9), W = (2,5,1,4,3,1,2), T = 15 -> 8 ({7,5,3}: 1+4+3)",
      mw == 8 == bf_maxw(bx, bw, 15), mw)
check("page example (b): same X, W, T = 4 -> -inf", max_weight(bx, bw, 4) == NEG)

# =====================================================================================================
# Exercise 2.2 — text segmentation variants
# =====================================================================================================
def num_splits(A, isword):
    """NumSplits(i) exactly as on the page; returns (value, number of IsWord calls)."""
    n = len(A)
    calls = [0]

    def IsWord(i, j):
        calls[0] += 1
        return isword(A[i - 1:j])

    def rec(i):
        if i > n:
            return 1
        total = 0
        for j in range(i, n + 1):
            if IsWord(i, j):
                total += rec(j + 1)
        return total
    return rec(1), calls[0]


def both_splittable(A, B, isword):
    n = len(A)

    def rec(i):
        if i > n:
            return True
        for j in range(i, n + 1):
            if isword(A[i - 1:j]) and isword(B[i - 1:j]):
                if rec(j + 1):
                    return True
        return False
    return rec(1)


def num_both_splits(A, B, isword):
    n = len(A)

    def rec(i):
        if i > n:
            return 1
        total = 0
        for j in range(i, n + 1):
            if isword(A[i - 1:j]) and isword(B[i - 1:j]):
                total += rec(j + 1)
        return total
    return rec(1)


def segmentations(n):
    """All segmentations of range n as lists of (start, end) half-open intervals: 2^(n-1) for n >= 1, 1 for n = 0."""
    if n == 0:
        yield []
        return
    for cuts in itertools.product([0, 1], repeat=n - 1):
        segs, s = [], 0
        for p, c in enumerate(cuts, start=1):
            if c:
                segs.append((s, p))
                s = p
        segs.append((s, n))
        yield segs


def bf_num_splits(A, isword):
    return sum(1 for segs in segmentations(len(A)) if all(isword(A[a:b]) for a, b in segs))


def bf_num_both(A, B, isword):
    return sum(1 for segs in segmentations(len(A)) if all(isword(A[a:b]) and isword(B[a:b]) for a, b in segs))


def all_strings(alpha, maxlen):
    for L in range(maxlen + 1):
        for t in itertools.product(alpha, repeat=L):
            yield "".join(t)


short = [w for w in all_strings("ab", 3) if w]
ok_a = ok_b = ok_c = True
trials = 0
for _ in range(60):
    D = set(random.sample(short, random.randint(1, len(short))))
    wd = D.__contains__
    for A in all_strings("ab", 7):
        trials += 1
        if num_splits(A, wd)[0] != bf_num_splits(A, wd):
            ok_a = False
for _ in range(400):
    D = set(random.sample(short, random.randint(1, len(short))))
    wd = D.__contains__
    n = random.randint(0, 8)
    A = "".join(random.choice("ab") for _ in range(n))
    B = "".join(random.choice("ab") for _ in range(n))
    bf = bf_num_both(A, B, wd)
    if num_both_splits(A, B, wd) != bf:
        ok_c = False
    if both_splittable(A, B, wd) != (bf > 0):
        ok_b = False
for n in range(0, 6):
    D = {"a", "b", "ab", "ba", "aab", "bb"}
    for A in itertools.product("ab", repeat=n):
        for B in itertools.product("ab", repeat=n):
            A_, B_ = "".join(A), "".join(B)
            bf = bf_num_both(A_, B_, D.__contains__)
            if num_both_splits(A_, B_, D.__contains__) != bf or both_splittable(A_, B_, D.__contains__) != (bf > 0):
                ok_b = ok_c = False
check("Ex 2.2(a) NumSplits = brute-force count of segmentations (60 random dictionaries x all strings over {a,b} up to length 7)", ok_a, f"{trials} cases")
check("Ex 2.2(b) BothSplittable = brute force (all pairs over {a,b} up to length 5, fixed dictionary; 400 random)", ok_b)
check("Ex 2.2(c) NumBothSplits = brute-force count of common segmentations", ok_c)

DICT = {"A", "ART", "ARTIST", "IS", "TO", "TOIL", "OIL", "I", "IT"}
v, _ = num_splits("ARTISTOIL", DICT.__contains__)
check("book example (a): ARTISTOIL has 2 partitions (ARTIST.OIL, ART.IS.TOIL) with dictionary {A, ART, ARTIST, IS, TO, TOIL, OIL, I, IT}", v == 2, v)
# worst case: every substring is a word -> 2^(n-1) partitions and exactly 2^n - 1 IsWord calls
ok = all(num_splits("x" * n, lambda w: True) == (2 ** (n - 1) if n else 1, 2 ** n - 1) for n in range(0, 16))
check("worst case (every substring a word): 2^(n-1) partitions and exactly 2^n - 1 IsWord calls", ok)
A1, B1 = "BOTHEARTHANDSATURNSPIN", "PINSTARTRAPSANDRAGSLAP"
D12 = {"BOT", "HEART", "HAND", "SAT", "URNS", "PIN", "START", "RAPS", "AND", "RAGS", "LAP"}
D16 = D12 | {"URN", "SPIN", "RAG", "SLAP"}
check("book example (b): both strings have length 22", len(A1) == len(B1) == 22)
check("book example (b): BOT.HEART.HAND.SAT.URNS.PIN / PIN.START.RAPS.AND.RAGS.LAP is a common segmentation",
      both_splittable(A1, B1, D12.__contains__) and num_both_splits(A1, B1, D12.__contains__) == 1)
nb = num_both_splits(A1, B1, D16.__contains__)
check("page example (c): adding URN, SPIN, RAG, SLAP gives exactly 2 common segmentations (second: ...URN.SPIN / ...RAG.SLAP)",
      nb == 2 == bf_num_both(A1, B1, D16.__contains__), nb)

# =====================================================================================================
# Exercise 2.3 — addition chains
# =====================================================================================================
def shortest_chain(X, n):
    """ShortestChain(X[0..k]) exactly as on the page (global n)."""
    k = len(X) - 1
    if X[k] == n:
        return list(X)
    best = None
    for i in range(0, k + 1):
        for j in range(i, k + 1):
            if X[k] < X[i] + X[j] <= n:
                C = shortest_chain(X + [X[i] + X[j]], n)
                if best is None or len(C) < len(best):
                    best = C
    return best


def is_chain(c, n):
    if not c or c[0] != 1 or c[-1] != n:
        return False
    if any(c[t] >= c[t + 1] for t in range(len(c) - 1)):
        return False
    return all(any(c[a] + c[b] == c[t] for a in range(t) for b in range(a, t)) for t in range(1, len(c)))


def l_iddfs(n):
    """Independent: minimum addition-chain length by iterative deepening with the doubling bound."""
    if n == 1:
        return 0

    def dfs(ch, L):
        last = ch[-1]
        if last == n:
            return True
        if len(ch) - 1 == L or last << (L - (len(ch) - 1)) < n:
            return False
        cands = sorted({a + b for a in ch for b in ch if last < a + b <= n}, reverse=True)
        for x in cands:
            ch.append(x)
            if dfs(ch, L):
                return True
            ch.pop()
        return False
    L = 1
    while not dfs([1], L):
        L += 1
    return L


# OEIS A003313 (length of shortest addition chain for n), n = 1..32
A003313 = [0, 1, 2, 2, 3, 3, 4, 3, 4, 4, 5, 4, 5, 5, 5, 4, 5, 5, 6, 5, 6, 6, 6, 5, 6, 6, 6, 6, 7, 6, 7, 5]
ok_valid = ok_len = True
for n in range(1, 13):
    c = shortest_chain([1], n)
    ok_valid &= is_chain(c, n)
    ok_len &= (len(c) - 1 == l_iddfs(n) == A003313[n - 1])
check("Ex 2.3(a) ShortestChain(<1>) returns a valid addition chain for every n <= 12", ok_valid)
check("Ex 2.3(a) its length equals the minimum (iterative deepening and OEIS A003313) for n <= 12", ok_len)
check("independent search agrees with OEIS A003313 for n <= 32", all(l_iddfs(n) == A003313[n - 1] for n in range(1, 33)))
book = [1, 2, 3, 5, 10, 20, 23, 46, 92, 184, 187, 374]
check("book example: <1,2,3,5,10,20,23,46,92,184,187,374> is an addition chain for 374 of length 11",
      is_chain(book, 374) and len(book) - 1 == 11)
l374 = l_iddfs(374)
check("the book's chain for 374 is shortest: l(374) = 11", l374 == 11, l374)
# binary method gives floor(lg n) + popcount(n) - 1 = 8 + 6 - 1 = 13 for 374
check("for comparison, the square-and-multiply chain for 374 has length 13", (374).bit_length() - 1 + bin(374).count("1") - 1 == 13)
check("page example: l(15) = 5 via 1,2,3,5,10,15, while square-and-multiply 1,2,3,6,7,14,15 has length 6",
      l_iddfs(15) == 5 and is_chain([1, 2, 3, 5, 10, 15], 15) and is_chain([1, 2, 3, 6, 7, 14, 15], 15))
check("15 is the smallest n where square-and-multiply is not shortest",
      min(n for n in range(1, 33) if A003313[n - 1] < (n.bit_length() - 1) + bin(n).count("1") - 1) == 15)

# =====================================================================================================
# Exercise 2.4 — recursive definitions
# =====================================================================================================
def lcs(A, B, simple=False):
    m, n = len(A), len(B)

    @lru_cache(None)
    def f(i, j):
        if i > m or j > n:
            return 0
        if A[i - 1] == B[j - 1]:
            if simple:
                return 1 + f(i + 1, j + 1)
            return max(f(i + 1, j), f(i, j + 1), 1 + f(i + 1, j + 1))
        return max(f(i + 1, j), f(i, j + 1))
    return f(1, 1)


def scs(A, B, simple=False):
    m, n = len(A), len(B)

    @lru_cache(None)
    def f(i, j):
        if i > m:
            return n - j + 1
        if j > n:
            return m - i + 1
        if A[i - 1] == B[j - 1]:
            if simple:
                return 1 + f(i + 1, j + 1)
            return 1 + min(f(i + 1, j), f(i, j + 1), f(i + 1, j + 1))
        return 1 + min(f(i + 1, j), f(i, j + 1))
    return f(1, 1)


def bf_lcs(A, B):
    best = 0
    for S in subsets(len(A)):
        if len(S) > best and is_subseq([A[i] for i in S], B):
            best = len(S)
    return best


def bf_scs(A, B):
    alpha = sorted(set(A) | set(B))
    for L in range(max(len(A), len(B)), len(A) + len(B) + 1):
        for Z in itertools.product(alpha, repeat=L):
            if is_subseq(A, Z) and is_subseq(B, Z):
                return L
    raise AssertionError


ok1 = ok2 = ok3 = ok4 = ok5 = True
for m in range(0, 6):
    for A in itertools.product("ab", repeat=m):
        for n in range(0, 6):
            for B in itertools.product("ab", repeat=n):
                v = lcs(A, B)
                ok1 &= v == bf_lcs(A, B)
                ok2 &= v == lcs(A, B, simple=True)
for m in range(0, 5):
    for A in itertools.product("ab", repeat=m):
        for n in range(0, 5):
            for B in itertools.product("ab", repeat=n):
                v = scs(A, B)
                ok3 &= v == bf_scs(A, B)
                ok4 &= v == scs(A, B, simple=True)
                ok5 &= v == m + n - lcs(A, B)
for _ in range(300):
    A = [random.choice("abc") for _ in range(random.randint(0, 8))]
    B = [random.choice("abc") for _ in range(random.randint(0, 8))]
    ok1 &= lcs(A, B) == bf_lcs(A, B)
    ok2 &= lcs(A, B) == lcs(A, B, simple=True)
for _ in range(200):
    A = [random.choice("abc") for _ in range(random.randint(0, 4))]
    B = [random.choice("abc") for _ in range(random.randint(0, 4))]
    ok3 &= scs(A, B) == bf_scs(A, B)
    ok4 &= scs(A, B) == scs(A, B, simple=True)
    ok5 &= scs(A, B) == len(A) + len(B) - lcs(A, B)
check("Ex 2.4(a) lcs recurrence = brute force (all pairs over {a,b} up to length 5; 300 random over {a,b,c} up to 8)", ok1)
check("Ex 2.4(a) when A[i] = B[j] the match always wins: simplified recurrence gives the same values", ok2)
check("Ex 2.4(b) scs recurrence = brute-force shortest common supersequence (all pairs over {a,b} up to length 4; 200 random)", ok3)
check("Ex 2.4(b) simplified scs recurrence (A[i] = B[j] -> 1 + scs(i+1, j+1)) gives the same values", ok4)
check("Ex 2.4(b) scs(A, B) = m + n - lcs(A, B) on all tested pairs", ok5)
check("page example: lcs(ALGORITHM, ALTRUISTIC) = 5 and scs = 14",
      lcs("ALGORITHM", "ALTRUISTIC") == 5 == bf_lcs("ALGORITHM", "ALTRUISTIC") and scs("ALGORITHM", "ALTRUISTIC") == 14)


# ---- (c) bitonic -----------------------------------------------------------------------------------
def lbs(A):
    n = len(A)

    @lru_cache(None)
    def lis_last(i):            # longest increasing subsequence of A[1..i] ending with A[i]
        return 1 + max([lis_last(h) for h in range(1, i) if A[h - 1] < A[i - 1]], default=0)

    @lru_cache(None)
    def lds_first(i):           # longest decreasing subsequence of A[i..n] starting with A[i]
        return 1 + max([lds_first(j) for j in range(i + 1, n + 1) if A[j - 1] < A[i - 1]], default=0)

    return max([lis_last(i) + lds_first(i) - 1 for i in range(1, n + 1) if lis_last(i) >= 2 and lds_first(i) >= 2], default=0)


def is_bitonic(X):
    """Book's definition: some index i with 1 < i < n, X[1..i] increasing and X[i..n] decreasing (strictly)."""
    n = len(X)
    for i in range(2, n):         # 1-indexed i in 2..n-1
        if all(X[t] < X[t + 1] for t in range(0, i - 1)) and all(X[t] > X[t + 1] for t in range(i - 1, n - 1)):
            return True
    return False


def bf_longest(A, pred):
    best = 0
    for S in subsets(len(A)):
        if len(S) > best and pred([A[i] for i in S]):
            best = len(S)
    return best


# ---- (d) oscillating -------------------------------------------------------------------------------
def is_osc(X):
    """X[i] < X[i+1] for even i, X[i] > X[i+1] for odd i (1-indexed)."""
    return all((X[t - 1] < X[t]) if t % 2 == 0 else (X[t - 1] > X[t]) for t in range(1, len(X)))


def los(A, sentinel=False):
    n = len(A)

    @lru_cache(None)
    def down(i):
        return 1 + max([up(j) for j in range(i + 1, n + 1) if A[j - 1] < A[i - 1]], default=0)

    @lru_cache(None)
    def up(i):
        return 1 + max([down(j) for j in range(i + 1, n + 1) if A[j - 1] > A[i - 1]], default=0)

    if sentinel:   # A[0] = -infinity, answer Up(0) - 1
        return 1 + max([down(j) for j in range(1, n + 1)], default=0) - 1
    return max([down(i) for i in range(1, n + 1)], default=0)


# ---- (e) shortest oscillating supersequence ---------------------------------------------------------
def sos(A, simple=False):
    n = len(A)
    if n == 0:
        return 0

    @lru_cache(None)
    def sdown(i):
        if i == n:
            return 1
        if simple:
            return 1 + sup(i + 1) if A[i - 1] > A[i] else 2 + sdown(i + 1)
        adj = 1 + sup(i + 1) if A[i - 1] > A[i] else 3 + sup(i + 1)
        return min(adj, 2 + sdown(i + 1))

    @lru_cache(None)
    def sup(i):
        if i == n:
            return 1
        if simple:
            return 1 + sdown(i + 1) if A[i - 1] < A[i] else 2 + sup(i + 1)
        adj = 1 + sdown(i + 1) if A[i - 1] < A[i] else 3 + sdown(i + 1)
        return min(adj, 2 + sup(i + 1))

    if simple:
        return sdown(1)
    return min(sdown(1), 1 + sup(1))


def bf_sos(A):
    """Breadth-first search over (number of A-symbols matched greedily, last value, length parity),
    appending any integer from a range wide enough to realize every order type of a sequence of length <= 3n+3."""
    n = len(A)
    if n == 0:
        return 0
    lo, hi = min(A) - 3 * n - 4, max(A) + 3 * n + 4
    start = (0, None, 0)
    frontier, seen, L = [start], {start}, 0
    while frontier:
        for (mt, last, ln) in frontier:
            if mt == n:
                return L
        L += 1
        nxt = []
        for (mt, last, ln) in frontier:
            for v in range(lo, hi + 1):
                if last is not None:
                    # position ln (1-indexed) holds `last`; need last > v if ln odd, last < v if ln even
                    if ln % 2 == 1 and not last > v:
                        continue
                    if ln % 2 == 0 and not last < v:
                        continue
                m2 = mt + (1 if mt < n and v == A[mt] else 0)
                st = (m2, v, ln + 1)
                if st not in seen:
                    seen.add(st)
                    nxt.append(st)
        frontier = nxt
    raise AssertionError


def sos_witness(A):
    """Build the supersequence described by the simplified rule and return it (for a constructive check)."""
    big, small = max(A) + 1, min(A) - 1
    X = [A[0]]
    for i in range(1, len(A)):
        pos = len(X)                      # 1-indexed position of X[-1]
        need_down = pos % 2 == 1
        if (need_down and X[-1] > A[i]) or (not need_down and X[-1] < A[i]):
            X.append(A[i])
        else:
            X.append(small if need_down else big)
            X.append(A[i])
    return X


# ---- (f) convex --------------------------------------------------------------------------------------
def is_convex(X):
    return all(2 * X[t] < X[t - 1] + X[t + 1] for t in range(1, len(X) - 1))


def lxs(A):
    n = len(A)

    @lru_cache(None)
    def LXS(i, j):
        return max([2] + [1 + LXS(j, k) for k in range(j + 1, n + 1) if 2 * A[j - 1] < A[i - 1] + A[k - 1]])

    return max([min(n, 2)] + [LXS(i, j) for i in range(1, n + 1) for j in range(i + 1, n + 1)])


okc = okd = okd2 = oke = oke2 = oke3 = okf = True
for n in range(0, 8):
    for A in itertools.product(range(4), repeat=n):
        okc &= lbs(A) == bf_longest(A, is_bitonic)
        v = los(A)
        okd &= v == bf_longest(A, is_osc)
        okd2 &= v == los(A, sentinel=True)
for n in range(0, 7):
    for A in itertools.product(range(5), repeat=n):
        okf &= lxs(A) == bf_longest(A, is_convex)
for n in range(0, 7):
    for A in itertools.product(range(3), repeat=n):
        v = sos(A)
        oke &= v == bf_sos(A)
        oke2 &= v == sos(A, simple=True)
        if n:
            W = sos_witness(A)
            oke3 &= is_osc(W) and is_subseq(A, W) and len(W) == v
for _ in range(300):
    A = [random.randint(0, 9) for _ in range(random.randint(8, 11))]
    okc &= lbs(A) == bf_longest(A, is_bitonic)
    okd &= los(A) == bf_longest(A, is_osc)
    okf &= lxs(A) == bf_longest(A, is_convex)
for _ in range(300):
    A = [random.randint(0, 9) for _ in range(random.randint(7, 9))]
    v = sos(A)
    oke &= v == bf_sos(A)
    oke2 &= v == sos(A, simple=True)
    W = sos_witness(A)
    oke3 &= is_osc(W) and is_subseq(A, W) and len(W) == v
check("Ex 2.4(c) lbs definition = brute force, book's bitonic definition (all arrays over {0..3} up to length 7; 300 random up to 11)", okc)
check("Ex 2.4(d) los definition = brute force (all arrays over {0..3} up to length 7; 300 random up to 11)", okd)
check("Ex 2.4(d) sentinel version Up(0) - 1 with A[0] = -inf gives the same values", okd2)
check("Ex 2.4(e) sos recurrence = breadth-first brute force over integer sequences (all arrays over {0,1,2} up to length 6; 300 random)", oke)
check("Ex 2.4(e) simplified scan (insert one element exactly when the next comparison fails) gives the same values", oke2)
check("Ex 2.4(e) the witness built by the scan is oscillating, contains A, and has length sos(A)", oke3)
check("Ex 2.4(f) lxs definition = brute force (all arrays over {0..4} up to length 6; 300 random up to 11)", okf)

PI10 = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3]
vals = (lbs(PI10), los(PI10), sos(PI10), lxs(PI10))
check("page examples on A = 3,1,4,1,5,9,2,6,5,3: lbs = 7, los = 8, sos = 12, lxs = 5",
      vals == (7, 8, 12, 5) and bf_longest(PI10, is_bitonic) == 7 and bf_longest(PI10, is_osc) == 8
      and bf_sos(PI10) == 12 and bf_longest(PI10, is_convex) == 5, vals)
check("page example witnesses: 1,4,5,9,6,5,3 bitonic; 3,1,4,1,5,2,6,5 oscillating; 3,1,1,2,6 convex",
      is_bitonic([1, 4, 5, 9, 6, 5, 3]) and is_subseq([1, 4, 5, 9, 6, 5, 3], PI10)
      and is_osc([3, 1, 4, 1, 5, 2, 6, 5]) and is_subseq([3, 1, 4, 1, 5, 2, 6, 5], PI10)
      and is_convex([3, 1, 1, 2, 6]) and is_subseq([3, 1, 1, 2, 6], PI10))
W = sos_witness(PI10)
check("page example: scan witness for 3,1,4,1,5,9,2,6,5,3 is 3,1,4,1,5,0,9,2,6,5,10,3", W == [3, 1, 4, 1, 5, 0, 9, 2, 6, 5, 10, 3], W)
check("trap: an increasing array has no bitonic subsequence under the book's definition (lbs(1,2,3) = 0)", lbs((1, 2, 3)) == 0)

# =====================================================================================================
# Exercise 2.5 — subsequences of two arrays
# =====================================================================================================
def is_subseq_bt(X, Y, greedy=False):
    k, n = len(X), len(Y)
    calls = [0]

    def rec(i, j):
        calls[0] += 1
        if i > k:
            return True
        elif j > n:
            return False
        elif X[i - 1] == Y[j - 1]:
            if greedy:
                return rec(i + 1, j + 1)
            return rec(i + 1, j + 1) or rec(i, j + 1)
        else:
            return rec(i, j + 1)
    return rec(1, 1), calls[0]


def min_del(X, Y):
    k, n = len(X), len(Y)

    @lru_cache(None)
    def rec(i, j):
        if i > k:
            return INF
        elif j > n:
            return 0
        elif X[i - 1] != Y[j - 1]:
            return rec(i, j + 1)
        else:
            return min(1 + rec(i, j + 1), rec(i + 1, j + 1))
    return rec(1, 1)


def bf_min_del(X, Y):
    n = len(Y)
    for r in range(0, n + 1):
        for D in itertools.combinations(range(n), r):
            Z = [Y[t] for t in range(n) if t not in D]
            if not is_subseq(X, Z):
                return r
    return INF


oka = okg = okb = True
for k in range(0, 4):
    for X in itertools.product("ab", repeat=k):
        for n in range(0, 8):
            for Y in itertools.product("ab", repeat=n):
                v = is_subseq_bt(X, Y)[0]
                oka &= v == is_subseq(X, Y)
                okg &= v == is_subseq_bt(X, Y, greedy=True)[0]
                okb &= min_del(X, Y) == bf_min_del(X, Y)
for _ in range(300):
    X = [random.choice("abc") for _ in range(random.randint(0, 4))]
    Y = [random.choice("abc") for _ in range(random.randint(0, 9))]
    oka &= is_subseq_bt(X, Y)[0] == is_subseq(X, Y)
    okb &= min_del(X, Y) == bf_min_del(X, Y)
check("Ex 2.5(a) IsSubseq backtracking = direct subsequence test (all X over {a,b} up to 3, Y up to 7; 300 random)", oka)
check("Ex 2.5(a) greedy version (only IsSubseq(i+1, j+1) when X[i] = Y[j]) gives the same answers", okg)
check("Ex 2.5(b) MinDel = brute-force fewest deletions (same inputs)", okb)
PP, PEN = "PPAP", "PENPINEAPPLEAPPLEPEN"
check("book example (a): PPAP is a subsequence of PENPINEAPPLEAPPLEPEN", is_subseq_bt(PP, PEN)[0] and is_subseq_bt(PP, PEN, True)[0])
md = min_del(PP, PEN)
one_enough = any(not is_subseq(PP, PEN[:t] + PEN[t + 1:]) for t in range(len(PEN)))
two_As = PEN.replace("A", "")
check("book example (b): MinDel(PPAP, PENPINEAPPLEAPPLEPEN) = 2 (no single deletion works; deleting both A's works)",
      md == 2 and not one_enough and not is_subseq(PP, two_As), md)
gc = is_subseq_bt(PP, PEN, greedy=True)[1]
check("greedy IsSubseq makes at most n + 1 calls on the example", gc <= len(PEN) + 1, gc)

# =====================================================================================================
# Exercise 2.6 — optimal balanced binary search trees
# =====================================================================================================
def all_bsts(i, k):
    """All BSTs on keys i..k as (root, left, right) or None."""
    if i > k:
        return [None]
    out = []
    for r in range(i, k + 1):
        for L in all_bsts(i, r - 1):
            for R in all_bsts(r + 1, k):
                out.append((r, L, R))
    return out


def nodes(t):
    return [] if t is None else [t[0]] + nodes(t[1]) + nodes(t[2])


def height(t):
    return 0 if t is None else 1 + max(height(t[1]), height(t[2]))


def is_avl(t):
    return t is None or (abs(height(t[1]) - height(t[2])) <= 1 and is_avl(t[1]) and is_avl(t[2]))


def cost(t, f, d=1):
    return 0 if t is None else f[t[0] - 1] * d + cost(t[1], f, d + 1) + cost(t[2], f, d + 1)


def rb_ok(t, color, red_root_ok=False, aa=False):
    """color: dict key -> 'R'/'B'. Literal check: every red node has a black parent (so a red root is illegal
    unless red_root_ok), every root-to-null path has the same number of black nodes; aa: no left child is red."""
    def walk(t, parent_color, is_left):
        if t is None:
            return 0
        c = color[t[0]]
        if c == "R":
            if parent_color is None and not red_root_ok:
                return None
            if parent_color == "R":
                return None
            if aa and is_left:
                return None
        a = walk(t[1], c, True)
        b = walk(t[2], c, False)
        if a is None or b is None or a != b:
            return None
        return a + (1 if c == "B" else 0)
    return walk(t, None, False) is not None


def opt_avl(f):
    n = len(f)
    F = lambda i, k: sum(f[i - 1:k])

    @lru_cache(None)
    def A(i, k, h):
        if i > k:
            return 0 if h == 0 else INF
        if h <= 0:
            return INF
        best = INF
        for r in range(i, k + 1):
            for hl, hr in ((h - 1, h - 1), (h - 1, h - 2), (h - 2, h - 1)):
                best = min(best, A(i, r - 1, hl) + A(r + 1, k, hr))
        return F(i, k) + best
    return min(A(1, n, h) for h in range(0, n + 1))


def opt_rb(f, aa=False):
    n = len(f)
    F = lambda i, k: sum(f[i - 1:k])

    @lru_cache(None)
    def Black(i, k, b):
        if i > k:
            return 0 if b == 0 else INF
        if b <= 0:
            return INF
        if aa:
            return F(i, k) + min(Black(i, r - 1, b - 1) + Any(r + 1, k, b - 1) for r in range(i, k + 1))
        return F(i, k) + min(Any(i, r - 1, b - 1) + Any(r + 1, k, b - 1) for r in range(i, k + 1))

    @lru_cache(None)
    def Red(i, k, b):
        if i > k:
            return INF
        return F(i, k) + min(Black(i, r - 1, b) + Black(r + 1, k, b) for r in range(i, k + 1))

    @lru_cache(None)
    def Any(i, k, b):
        return min(Black(i, k, b), Red(i, k, b))

    return min(Black(1, n, b) for b in range(0, n + 1))


def opt_cost(f):
    n = len(f)

    @lru_cache(None)
    def O(i, k):
        if i > k:
            return 0
        return sum(f[i - 1:k]) + min(O(i, r - 1) + O(r + 1, k) for r in range(i, k + 1))
    return O(1, n)


# precompute, for each n <= 7, the trees and the valid (tree) sets per constraint
VALID = {}
for n in range(0, 8):
    trees = all_bsts(1, n)
    avl = [t for t in trees if is_avl(t)]
    rb, rb_redroot, aa = [], [], []
    for t in trees:
        keys = nodes(t)
        good = goodr = gooda = False
        for cols in itertools.product("RB", repeat=len(keys)):
            col = dict(zip(keys, cols))
            if not good and rb_ok(t, col):
                good = True
            if not goodr and rb_ok(t, col, red_root_ok=True):
                goodr = True
            if not gooda and rb_ok(t, col, aa=True):
                gooda = True
        if good:
            rb.append(t)
        if goodr:
            rb_redroot.append(t)
        if gooda:
            aa.append(t)
    VALID[n] = (trees, avl, rb, rb_redroot, aa)

ok_avl = ok_rb = ok_aa = ok_rr = ok_plain = True
cases = 0
for n in range(0, 8):
    trees, avl, rb, rbr, aa = VALID[n]
    fs = [tuple([1] * n)] + [tuple(random.randint(1, 20) for _ in range(n)) for _ in range(25)]
    fs += [tuple(2 ** (n - 1 - t) for t in range(n)), tuple(2 ** t for t in range(n))]
    for f in fs:
        cases += 1
        ok_avl &= opt_avl(f) == min(cost(t, f) for t in avl)
        ok_rb &= opt_rb(f) == min(cost(t, f) for t in rb)
        ok_rr &= min(cost(t, f) for t in rb) == min(cost(t, f) for t in rbr)
        ok_aa &= opt_rb(f, aa=True) == min(cost(t, f) for t in aa)
        ok_plain &= opt_cost(f) == min(cost(t, f) for t in trees)
check("Ex 2.6(a) OptAVL recurrence = min cost over all AVL trees (brute force over all BSTs, n <= 7)", ok_avl, f"{cases} frequency vectors")
check("Ex 2.6(b) red-black recurrence = min cost over all validly colorable BSTs (all 2^n colorings, n <= 7)", ok_rb)
check("Ex 2.6(b) allowing a red root does not change the optimum (recolor the root black)", ok_rr)
check("Ex 2.6(c) AA recurrence = min cost over all BSTs with a valid AA coloring (n <= 7)", ok_aa)
check("unconstrained OptCost (book's Section 2.8) = brute force (sanity check of the cost function)", ok_plain)
check("counts: 429 BSTs on 7 keys; AVL / red-black / AA shapes on 7 keys: "
      + "/".join(str(len(VALID[7][t])) for t in (1, 2, 4)), len(VALID[7][0]) == 429)

check("every AVL shape on n <= 7 keys has a red-black coloring, and every AA shape is a red-black shape",
      all(set(map(repr, VALID[n][1])) <= set(map(repr, VALID[n][2])) and set(map(repr, VALID[n][4])) <= set(map(repr, VALID[n][2]))
          for n in range(8)))
f6 = (1, 1, 1, 1, 2, 6)
vals = (opt_cost(f6), opt_rb(f6), opt_avl(f6), opt_rb(f6, aa=True))
bf6 = tuple(min(cost(t, f6) for t in VALID[6][s]) for s in (0, 2, 1, 4))
check("page example f = (1,1,1,1,2,6): unconstrained 25 < red-black 26 < AVL 27 < AA 31", vals == (25, 26, 27, 31) == bf6, vals)
f8421, f1248 = (8, 4, 2, 1), (1, 2, 4, 8)
vals = tuple(g(f) for f in (f8421, f1248) for g in (opt_cost, opt_rb, lambda f: opt_rb(f, aa=True)))
check("page example: f = (8,4,2,1) -> plain 26, red-black 27, AA 27; mirror f = (1,2,4,8) -> 26, 27, 28 (AA is not symmetric)",
      vals == (26, 27, 27, 26, 27, 28), vals)

# =====================================================================================================
# Further claims on the page: example details, worst-case bounds, memoized costs
# =====================================================================================================
def num_splits_from(A, isword, i0):
    n = len(A)

    def rec(i):
        if i > n:
            return 1
        return sum(rec(j + 1) for j in range(i, n + 1) if isword(A[i - 1:j]))
    return rec(i0)


wd = DICT.__contains__
check("page example (a): NumSplits(2) = 0 (after A), NumSplits(4) = 1 (after ART), NumSplits(7) = 1 (after ARTIST)",
      (num_splits_from("ARTISTOIL", wd, 2), num_splits_from("ARTISTOIL", wd, 4), num_splits_from("ARTISTOIL", wd, 7)) == (0, 1, 1)
      and [j for j in range(1, 10) if wd("ARTISTOIL"[:j])] == [1, 3, 6])
Dt = {"A", "BC", "XY", "Z"}.__contains__
check("trap (b): with words A, BC, XY, Z both ABC and XYZ are splittable, but not at the same indices",
      num_splits("ABC", Dt)[0] == 1 and num_splits("XYZ", Dt)[0] == 1 and not both_splittable("ABC", "XYZ", Dt))
cuts = [0, 3, 8, 12, 15, 19, 22]
check("book example (b): cutting after positions 3, 8, 12, 15, 19 gives the listed words in both strings",
      [A1[cuts[t]:cuts[t + 1]] for t in range(6)] == ["BOT", "HEART", "HAND", "SAT", "URNS", "PIN"]
      and [B1[cuts[t]:cuts[t + 1]] for t in range(6)] == ["PIN", "START", "RAPS", "AND", "RAGS", "LAP"])
check("page example (c): the second segmentation is BOT.HEART.HAND.SAT.URN.SPIN / PIN.START.RAPS.AND.RAG.SLAP",
      all(w in D16 for w in ["BOT", "HEART", "HAND", "SAT", "URN", "SPIN", "PIN", "START", "RAPS", "AND", "RAG", "SLAP"])
      and "BOTHEARTHANDSATURNSPIN" == "BOT" + "HEART" + "HAND" + "SAT" + "URN" + "SPIN"
      and "PINSTARTRAPSANDRAGSLAP" == "PIN" + "START" + "RAPS" + "AND" + "RAG" + "SLAP" and len(D12) == 11)
ok = True
for _ in range(300):
    D = set(random.sample(short, random.randint(1, len(short))))
    A = "".join(random.choice("ab") for _ in range(random.randint(0, 10)))
    ok &= num_splits(A, D.__contains__)[1] <= 2 ** len(A) - 1
check("NumSplits never calls IsWord more than 2^n - 1 times (300 random dictionaries and strings)", ok)
check("lcs example: ALRIT is a common subsequence of ALGORITHM and ALTRUISTIC",
      is_subseq("ALRIT", "ALGORITHM") and is_subseq("ALRIT", "ALTRUISTIC"))


def lis_last_ex(A, i):
    return 1 + max([lis_last_ex(A, h) for h in range(1, i) if A[h - 1] < A[i - 1]], default=0)


def lds_first_ex(A, i):
    return 1 + max([lds_first_ex(A, j) for j in range(i + 1, len(A) + 1) if A[j - 1] < A[i - 1]], default=0)


check("lbs example: at the peak 9 (index 6), LISlast = 4 and LDSfirst = 4",
      PI10[5] == 9 and lis_last_ex(PI10, 6) == 4 and lds_first_ex(PI10, 6) == 4)
fails = [t for t in range(1, 10) if not ((PI10[t - 1] > PI10[t]) if t % 2 == 1 else (PI10[t - 1] < PI10[t]))]
check("sos example: on the raw array the pattern >,<,>,... first fails at 5 > 9", fails[0] == 5 and PI10[4:6] == [5, 9])
occ1, occ2 = [1, 4, 8, 14], [9, 10, 13, 18]
check("Ex 2.5(b) example: PPAP occurs at positions 1,4,8,14 and, disjointly, at 9,10,13,18 of PENPINEAPPLEAPPLEPEN",
      "".join(PEN[t - 1] for t in occ1) == "PPAP" == "".join(PEN[t - 1] for t in occ2) and not set(occ1) & set(occ2))
# memoized costs stated on the page (counts of subproblems and inner-loop work)
ok = True
for n in range(1, 30):
    ok &= sum(1 for i in range(1, n + 1) for j in range(i, n + 1)) == n * (n + 1) // 2            # NumSplits: IsWord(i, j), i <= j
    ok &= sum(n - j for i in range(1, n + 1) for j in range(i + 1, n + 1)) == n * (n - 1) * (n - 2) // 6   # lxs inner loops
    ok &= sum(n - i for i in range(1, n + 1)) == n * (n - 1) // 2                                # LISfirst-style loops
check("memoized work: NumSplits n(n+1)/2 IsWord calls; lbs/los n(n-1)/2 loop steps per function; lxs C(n,3) loop steps", ok)

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: {FAIL}")
