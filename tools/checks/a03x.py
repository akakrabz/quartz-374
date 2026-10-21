#!/usr/bin/env python3
"""Checks for content/2-algorithms/03-dynamic-programming-exercises.md (solved exercises 3.1-3.10 of Erickson's Algorithms).

Every recurrence is implemented exactly as the page states it, filled in the page's evaluation order with a memo table that
refuses to be read before it is written (so a wrong evaluation order fails loudly), and compared with an independent brute
force on all small inputs plus random ones.  The book's examples are checked too.  Exact arithmetic (Fraction) throughout."""
import functools
import itertools
import math
import random
from bisect import bisect_left, insort
from fractions import Fraction as Fr

random.seed(374)
FAIL = []
INF = float("inf")


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail != "" else ""))
    if not cond:
        FAIL.append(name)


class Memo(dict):
    """Memo array: reading an entry that has not been written yet raises (checks the evaluation order)."""

    def __getitem__(self, k):
        if k not in self:
            raise KeyError(f"memo entry {k} read before it was written")
        return dict.__getitem__(self, k)


def all_checks(name, gen, f, g, show=lambda x: x):
    """Compare f and g on every input from gen; report the first mismatch."""
    cnt = 0
    for x in gen:
        cnt += 1
        a, b = f(*x), g(*x)
        if a != b:
            check(name, False, f"input {show(x)}: page {a}, brute force {b}")
            return
    check(name, True, f"{cnt} inputs")


def subseqs(A):
    """All subsequences of A as tuples of indices (0-based)."""
    n = len(A)
    for r in range(n + 1):
        yield from itertools.combinations(range(n), r)


def is_subseq(x, y):
    it = iter(y)
    return all(c in it for c in x)


# ============================================================================ Exercise 3.1 — Dream-Dollars
print("== Exercise 3.1: making change in Nadiria")
D = [1, 4, 7, 13, 28, 52, 91, 365]


def greedy_bills(k):
    out = []
    for d in sorted(D, reverse=True):
        while k >= d:
            k -= d
            out.append(d)
    return out


CALLS = [0]


def MinBills_rec(k):
    """(b) MinBills(k) = 0 if k = 0, else 1 + min{MinBills(k - d) : d in D, d <= k} — plain recursion."""
    CALLS[0] += 1
    if k == 0:
        return 0
    return 1 + min(MinBills_rec(k - d) for d in D if d <= k)


def MinBills_dp(K):
    """(c) the same recurrence, array MinBills[0..K] filled in increasing order of k."""
    M = Memo()
    M[0] = 0
    for k in range(1, K + 1):
        M[k] = 1 + min(M[k - d] for d in D if d <= k)
    return M


def bfs_bills(K):
    """Independent: the fewest bills via breadth-first search over amounts (level t = sums of exactly t bills)."""
    dist = {0: 0}
    frontier = [0]
    while frontier:
        nxt = []
        for s in frontier:
            for d in D:
                if s + d <= K and s + d not in dist:
                    dist[s + d] = dist[s] + 1
                    nxt.append(s + d)
        frontier = nxt
    return dist


K = 3000
M = MinBills_dp(K)
B = bfs_bills(K)
check("3.1(c) DP equals BFS optimum for all k <= 3000", all(M[k] == B[k] for k in range(K + 1)))
check("3.1(a) the book's example: greedy pays 122 as 91 + 28 + 1 + 1 + 1", greedy_bills(122) == [91, 28, 1, 1, 1])
check("3.1(a) greedy for 416 is 365+28+13+7+1+1+1 (7 bills)", greedy_bills(416) == [365, 28, 13, 7, 1, 1, 1])
check("3.1(a) 91+91+91+91+52 = 416 with 5 bills, and 5 is optimal", 4 * 91 + 52 == 416 and M[416] == 5 == B[416])
bad = [k for k in range(1, K + 1) if len(greedy_bills(k)) > B[k]]
check("3.1(a) 416 is the smallest amount where greedy is not optimal", bad[0] == 416, f"first few: {bad[:4]}")
check("3.1(a) 455 = 5*91 (5 bills) while greedy uses 365+52+28+7+1+1+1 (7)",
      greedy_bills(455) == [365, 52, 28, 7, 1, 1, 1] and B[455] == 5)
check("3.1(b) recursive algorithm equals the DP for k <= 40",
      all(MinBills_rec(k) == M[k] for k in range(41)))
# number of calls T(k) = 1 + sum_{d <= k} T(k - d)
T = [1]
for k in range(1, 3001):
    T.append(1 + sum(T[k - d] for d in D if d <= k))
CALLS[0] = 0
MinBills_rec(30)
check("3.1(b) call-count recurrence matches the instrumented recursion at k = 30", CALLS[0] == T[30], f"T(30) = {T[30]}")
lo, hi = 1.0, 2.0
for _ in range(200):
    mid = (lo + hi) / 2
    if sum(mid ** (-d) for d in D) > 1:
        lo = mid
    else:
        hi = mid
r = lo
check("3.1(b) growth rate r (root of sum r^-d = 1) is 1.449...", abs(r - 1.449) < 0.001, f"r = {r:.6f}")
logratios = [math.log(T[k]) - k * math.log(r) for k in (1000, 1500, 2000, 2500, 3000)]   # log(T(k)/r^k)
check("3.1(b) T(k)/r^k settles (so T(k) = Theta(r^k))", max(logratios) - min(logratios) < 1e-9,
      f"T(k)/r^k -> {math.exp(logratios[-1]):.6g}")
check("3.1(b) T(k) >= 2^floor(k/4) for all k <= 3000", all(T[k] >= 2 ** (k // 4) for k in range(3001)))

# ============================================================================ Exercise 3.2 — text segmentation variants
print("== Exercise 3.2: text segmentation variants")


def make_isword(words, counter=None):
    def IsWord(s):
        if counter is not None:
            counter[0] += 1
        return "".join(s) in words
    return IsWord


def NumSplits(A, IsWord):
    """(a) NumSplits(i) = # partitions of A[i..n]; NumSplits(n+1) = 1;
    NumSplits(i) = sum_{j=i}^{n} [IsWord(A[i..j])] * NumSplits(j+1); i from n+1 down to 1."""
    n = len(A)
    N = Memo()
    N[n + 1] = 1
    for i in range(n, 0, -1):
        N[i] = sum(N[j + 1] for j in range(i, n + 1) if IsWord(A[i - 1:j]))
    return N[1]


def SameSplit(A, B, IsWord):
    """(b) SameSplit(n+1) = True; SameSplit(i) = OR_j (IsWord(A[i..j]) and IsWord(B[i..j]) and SameSplit(j+1))."""
    n = len(A)
    S = Memo()
    S[n + 1] = True
    for i in range(n, 0, -1):
        S[i] = any(IsWord(A[i - 1:j]) and IsWord(B[i - 1:j]) and S[j + 1] for j in range(i, n + 1))
    return S[1]


def NumSameSplits(A, B, IsWord):
    """(c) NumSameSplits(n+1) = 1; NumSameSplits(i) = sum_j [IsWord(A[i..j]) and IsWord(B[i..j])] NumSameSplits(j+1)."""
    n = len(A)
    S = Memo()
    S[n + 1] = 1
    for i in range(n, 0, -1):
        S[i] = sum(S[j + 1] for j in range(i, n + 1) if IsWord(A[i - 1:j]) and IsWord(B[i - 1:j]))
    return S[1]


def cutsets(n):
    """All partitions of positions 1..n into consecutive blocks, as lists of (start, end) 1-based."""
    for mask in range(1 << max(n - 1, 0)):
        cuts = [c for c in range(1, n) if mask >> (c - 1) & 1]
        bounds = [0] + cuts + [n]
        yield [(bounds[t] + 1, bounds[t + 1]) for t in range(len(bounds) - 1)]


def brute_partitions(A, words):
    if not A:
        return 1
    return sum(all("".join(A[s - 1:e]) in words for s, e in P) for P in cutsets(len(A)))


def brute_same(A, B, words):
    if not A:
        return 1
    return sum(all("".join(A[s - 1:e]) in words and "".join(B[s - 1:e]) in words for s, e in P) for P in cutsets(len(A)))


all_words = ["".join(p) for L in (1, 2, 3) for p in itertools.product("ab", repeat=L)]
okA = okB = okC = okCalls = True
detail = ""
for trial in range(400):
    words = set(w for w in all_words if random.random() < 0.5)
    n = random.randint(0, 8)
    A = [random.choice("ab") for _ in range(n)]
    Bs = [random.choice("ab") for _ in range(n)]
    cnt = [0]
    got = NumSplits(A, make_isword(words, cnt))
    if got != brute_partitions(A, words):
        okA = False
        detail = f"{A} {words}"
    if cnt[0] != n * (n + 1) // 2:
        okCalls = False
    cnt = [0]
    if SameSplit(A, Bs, make_isword(words, cnt)) != (brute_same(A, Bs, words) > 0) or cnt[0] > n * (n + 1):
        okB = False
    if NumSameSplits(A, Bs, make_isword(words)) != brute_same(A, Bs, words):
        okC = False
check("3.2(a) NumSplits equals brute-force count (400 random dictionaries/strings)", okA, detail)
check("3.2(a) exactly n(n+1)/2 calls to IsWord", okCalls)
check("3.2(b) SameSplit equals brute force, at most n(n+1) calls", okB)
check("3.2(c) NumSameSplits equals brute force", okC)
dict1 = {"A", "I", "IT", "TO", "ART", "ARTIST", "IS", "OIL", "TOIL"}
check("3.2(a) ARTISTOIL -> 2 (ARTIST·OIL, ART·IS·TOIL) with a small English dictionary",
      NumSplits(list("ARTISTOIL"), make_isword(dict1)) == 2)
dict2 = {"BOT", "BOTH", "HEART", "EARTH", "EAR", "ART", "HAND", "AND", "SAT", "SATURN", "URN", "URNS", "TURN",
         "TURNS", "SPIN", "PIN", "PINS", "START", "STAR", "TAR", "RAP", "RAPS", "TRAP", "TRAPS", "SAND", "RAG", "RAGS",
         "LAP", "SLAP", "AS", "AN", "A"}
A2, B2 = list("BOTHEARTHANDSATURNSPIN"), list("PINSTARTRAPSANDRAGSLAP")
check("3.2(b) BOTHEARTHANDSATURNSPIN / PINSTARTRAPSANDRAGSLAP -> True", SameSplit(A2, B2, make_isword(dict2)))
cuts = [3, 8, 12, 15, 19, 22]   # BOT·HEART·HAND·SAT·URNS·PIN
pieces = lambda S: ["".join(S[a:b]) for a, b in zip([0] + cuts[:-1], cuts)]
check("3.2(b) the book's common partition", pieces(A2) == ["BOT", "HEART", "HAND", "SAT", "URNS", "PIN"]
      and pieces(B2) == ["PIN", "START", "RAPS", "AND", "RAGS", "LAP"])

# ============================================================================ Exercise 3.3 — maximum subarray sum / product
print("== Exercise 3.3: maximum subarray sum and product")


def MaxSubarraySum(A):
    """(a) MaxSuffixSum(0) = 0, MaxSuffixSum(j) = max(0, MaxSuffixSum(j-1) + A[j]); answer max_j MaxSuffixSum(j)."""
    n = len(A)
    S = Memo()
    S[0] = 0
    for j in range(1, n + 1):
        S[j] = max(0, S[j - 1] + A[j - 1])
    return max(S[j] for j in range(n + 1))


def MaxSubarrayProduct(A):
    """(b) MaxSuffixProd(0) = MinSuffixProd(0) = 1;
    MaxSuffixProd(j) = max(1, A[j]*MaxSuffixProd(j-1), A[j]*MinSuffixProd(j-1)); Min analogous; answer max_j MaxSuffixProd(j)."""
    n = len(A)
    Hi, Lo = Memo(), Memo()
    Hi[0] = Lo[0] = 1
    for j in range(1, n + 1):
        a = A[j - 1]
        Hi[j] = max(1, a * Hi[j - 1], a * Lo[j - 1])
        Lo[j] = min(1, a * Hi[j - 1], a * Lo[j - 1])
    return max(Hi[j] for j in range(n + 1))


def intervals(n):
    """All (i, j), 1 <= i <= j+1 <= n+1: A[i..j] (empty when i = j+1)."""
    for i in range(1, n + 2):
        for j in range(i - 1, n + 1):
            yield i, j


def brute_sum(A):
    return max(sum(A[i - 1:j]) for i, j in intervals(len(A)))


def brute_prod(A):
    return max(math.prod(A[i - 1:j]) for i, j in intervals(len(A)))


VALS = [Fr(-2), Fr(-1), Fr(-1, 2), Fr(0), Fr(1, 2), Fr(1), Fr(3)]


def small_arrays(maxn, vals=VALS):
    for n in range(maxn + 1):
        yield from (list(p) for p in itertools.product(vals, repeat=n))


def rand_arrays(cnt, maxn, vals=VALS):
    for _ in range(cnt):
        yield [random.choice(vals) for _ in range(random.randint(0, maxn))]


gen = lambda: itertools.chain(small_arrays(5), rand_arrays(3000, 14))
all_checks("3.3(a) MaxSubarraySum vs brute force (all arrays n <= 5 over 7 values incl. fractions, + random)",
           ((A,) for A in gen()), MaxSubarraySum, brute_sum)
all_checks("3.3(b) MaxSubarrayProduct vs brute force (same inputs)", ((A,) for A in gen()), MaxSubarrayProduct, brute_prod)
ex = [-6, 12, -7, 0, 14, -7, 5]
check("3.3 example: sum 19, product 504", MaxSubarraySum(ex) == 19 == 12 - 7 + 0 + 14 and MaxSubarrayProduct(ex) == 504 == -6 * 12 * -7)
S_ = [0]
for a_ in ex:
    S_.append(max(0, S_[-1] + a_))
check("3.3(a) example: MaxSuffixSum(1..7) = 0, 12, 5, 5, 19, 12, 17", S_[1:] == [0, 12, 5, 5, 19, 12, 17])
check("3.3 example [-374]: sum 0, product 1", MaxSubarraySum([-374]) == 0 and MaxSubarrayProduct([-374]) == 1)


def only_max_product(A):
    """The trap: keep only the largest suffix product."""
    hi, best = 1, 1
    for a in A:
        hi = max(1, a * hi)
        best = max(best, hi)
    return best


check("3.3(b) trap: [-2, 3, -4] -> 24, but keeping only the maximum gives 3",
      MaxSubarrayProduct([-2, 3, -4]) == 24 and only_max_product([-2, 3, -4]) == 3)
check("3.3(b) trap: [3, 1/4, 3] -> 3, not the product 9/4 of the whole zero-free stretch",
      MaxSubarrayProduct([3, Fr(1, 4), 3]) == 3 and 3 * Fr(1, 4) * 3 == Fr(9, 4))

# ============================================================================ Exercise 3.4 — maximum subarray variants
print("== Exercise 3.4: maximum-subarray variants")


def CircularMax(A):
    """(a) max(MaxSubarraySum(A), Total(A) + MaxSubarraySum(-A))."""
    return max(MaxSubarraySum(A), sum(A) + MaxSubarraySum([-a for a in A]))


def brute_circular(A):
    n = len(A)
    best = 0
    for s in range(n):
        for L in range(n + 1):
            best = max(best, sum(A[(s + t) % n] for t in range(L)))
    return best


all_checks("3.4(a) circular maximum vs brute force over all circular windows",
           ((A,) for A in itertools.chain(small_arrays(5), rand_arrays(2000, 12))), CircularMax, brute_circular)


def AtLeast(A, X):
    """(b) P = prefix sums; MaxSuffixSum as in 3.3(a);
    LongEnd(j) = (P[j] - P[j-X]) + MaxSuffixSum(j - X) for X <= j <= n; answer max_j LongEnd(j)."""
    n = len(A)
    P = [0]
    for a in A:
        P.append(P[-1] + a)
    S = Memo()
    S[0] = 0
    for j in range(1, n + 1):
        S[j] = max(0, S[j - 1] + A[j - 1])
    return max((P[j] - P[j - X]) + S[j - X] for j in range(X, n + 1))


def brute_atleast(A, X):
    return max(sum(A[i - 1:j]) for i, j in intervals(len(A)) if j - i + 1 >= X)


def AtMost(A, X):
    """(c) P[0..n] prefix sums; blocks of w = X+1 consecutive indices of P (block of t = t // w);
    PreMin(t) = P[t] if t is a block start, else min(PreMin(t-1), P[t])        (t increasing)
    SufMin(t) = P[t] if t is a block end or t = n, else min(SufMin(t+1), P[t]) (t decreasing)
    WinMin(j) = PreMin(j) if j < X, else min(SufMin(j - X), PreMin(j)) = min P[max(0, j-X) .. j]
    ShortEnd(j) = P[j] - WinMin(j); answer max_{0 <= j <= n} ShortEnd(j)."""
    n = len(A)
    P = [0]
    for a in A:
        P.append(P[-1] + a)
    w = X + 1
    Pre, Suf = Memo(), Memo()
    for t in range(n + 1):
        Pre[t] = P[t] if t % w == 0 else min(Pre[t - 1], P[t])
    for t in range(n, -1, -1):
        Suf[t] = P[t] if (t % w == w - 1 or t == n) else min(Suf[t + 1], P[t])
    best = None
    for j in range(n + 1):
        win = Pre[j] if j < X else min(Suf[j - X], Pre[j])
        assert win == min(P[max(0, j - X):j + 1])
        v = P[j] - win
        best = v if best is None else max(best, v)
    return best


def brute_atmost(A, X):
    return max(sum(A[i - 1:j]) for i, j in intervals(len(A)) if j - i + 1 <= X)


def PriceIsRight(A, X):
    """(d) Scan j = 0..n keeping the prefix sums P[0..j] in a sorted structure; for each j the best start is the
    smallest P[t] >= P[j] - X (successor query); answer max_j (P[j] - that P[t])."""
    n = len(A)
    seen = []
    best = None
    s = 0
    for j in range(n + 1):
        if j > 0:
            s += A[j - 1]
        insort(seen, s)                       # insert P[j] (t = j is the empty subarray)
        q = seen[bisect_left(seen, s - X)]    # successor of P[j] - X: exists because P[j] >= P[j] - X
        v = s - q
        best = v if best is None else max(best, v)
    return best


def brute_price(A, X):
    return max(sum(A[i - 1:j]) for i, j in intervals(len(A)) if sum(A[i - 1:j]) <= X)


def PriceNonneg(A, X):
    """(e) two pointers: t = smallest index with P[j] - P[t] <= X; t only moves right as j grows."""
    n = len(A)
    P = [0]
    for a in A:
        P.append(P[-1] + a)
    t, best = 0, 0
    for j in range(n + 1):
        while P[j] - P[t] > X:
            t += 1
        best = max(best, P[j] - P[t])
    return best


def with_X(arrs, xs):
    for A in arrs:
        for X in xs(A):
            yield A, X


all_checks("3.4(b) at least X vs brute force (all n <= 5, all 0 <= X <= n, + random)",
           with_X(itertools.chain(small_arrays(5), rand_arrays(2000, 12)), lambda A: range(len(A) + 1)),
           AtLeast, brute_atleast)
all_checks("3.4(c) at most X (block prefix/suffix minima) vs brute force",
           with_X(itertools.chain(small_arrays(5), rand_arrays(2000, 12)), lambda A: range(len(A) + 2)),
           AtMost, brute_atmost)
XS = [Fr(0), Fr(1, 2), Fr(1), Fr(2), Fr(5, 2), Fr(4)]
all_checks("3.4(d) largest sum <= X vs brute force",
           with_X(itertools.chain(small_arrays(4), rand_arrays(2000, 12)), lambda A: XS), PriceIsRight, brute_price)
NN = [Fr(0), Fr(1, 2), Fr(1), Fr(2), Fr(3)]
all_checks("3.4(e) two pointers (non-negative entries) vs brute force",
           with_X(itertools.chain(small_arrays(5, NN), rand_arrays(2000, 14, NN)), lambda A: XS), PriceNonneg, brute_price)

# ============================================================================ Exercise 3.5 — optimal subsequences
print("== Exercise 3.5: optimal subsequences")


def LCS(A, B):
    """(a) LCS(i, j) = 0 if i > m or j > n; else max(LCS(i+1, j), LCS(i, j+1), 1 + LCS(i+1, j+1) if A[i] = B[j]).
    i from m+1 down to 1 (outer), j from n+1 down to 1 (inner)."""
    m, n = len(A), len(B)
    L = Memo()
    for i in range(m + 1, 0, -1):
        for j in range(n + 1, 0, -1):
            if i > m or j > n:
                L[i, j] = 0
            else:
                L[i, j] = max(L[i + 1, j], L[i, j + 1], 1 + L[i + 1, j + 1] if A[i - 1] == B[j - 1] else 0)
    return L[1, 1]


def brute_lcs(A, B):
    return max(len(I) for I in subseqs(A) if is_subseq([A[i] for i in I], B))


def SCS(A, B):
    """(b) SCS(i, n+1) = m-i+1, SCS(m+1, j) = n-j+1; else 1 + min(SCS(i+1, j), SCS(i, j+1), SCS(i+1, j+1) if A[i] = B[j])."""
    m, n = len(A), len(B)
    S = Memo()
    for i in range(m + 1, 0, -1):
        for j in range(n + 1, 0, -1):
            if j > n:
                S[i, j] = m - i + 1
            elif i > m:
                S[i, j] = n - j + 1
            else:
                S[i, j] = 1 + min(S[i + 1, j], S[i, j + 1], S[i + 1, j + 1] if A[i - 1] == B[j - 1] else INF)
    return S[1, 1]


def brute_scs(A, B):
    alph = sorted(set(A) | set(B)) or ["a"]
    for L in range(max(len(A), len(B)), len(A) + len(B) + 1):
        for Z in itertools.product(alph, repeat=L):
            if is_subseq(A, Z) and is_subseq(B, Z):
                return L


def strpairs(maxlen, alph="ab"):
    for m in range(maxlen + 1):
        for n in range(maxlen + 1):
            for A in itertools.product(alph, repeat=m):
                for B in itertools.product(alph, repeat=n):
                    yield list(A), list(B)


all_checks("3.5(a) LCS vs brute force (all pairs over {a,b} of length <= 4)", strpairs(4), LCS, brute_lcs)
all_checks("3.5(a) LCS vs brute force (random over {a,b,c}, length <= 8)",
           (([random.choice("abc") for _ in range(random.randint(0, 8))],
             [random.choice("abc") for _ in range(random.randint(0, 8))]) for _ in range(500)), LCS, brute_lcs)
all_checks("3.5(b) SCS vs brute force (all pairs over {a,b} of length <= 4)", strpairs(4), SCS, brute_scs)
all_checks("3.5(b) SCS vs brute force (pairs over {a,b,c} of length <= 3)", strpairs(3, "abc"), SCS, brute_scs)


def Bitonic(A):
    """(c) IncEnd(i) = 1 + max({0} u {IncEnd(h) : h < i, A[h] < A[i]})    (i increasing)
    DecStart(i) = 1 + max({0} u {DecStart(j) : j > i, A[j] < A[i]})      (i decreasing)
    answer max{IncEnd(i) + DecStart(i) - 1 : IncEnd(i) >= 2 and DecStart(i) >= 2}, or 0 if there is no such i."""
    n = len(A)
    Inc, Dec = Memo(), Memo()
    for i in range(1, n + 1):
        Inc[i] = 1 + max([0] + [Inc[h] for h in range(1, i) if A[h - 1] < A[i - 1]])
    for i in range(n, 0, -1):
        Dec[i] = 1 + max([0] + [Dec[j] for j in range(i + 1, n + 1) if A[j - 1] < A[i - 1]])
    c = [Inc[i] + Dec[i] - 1 for i in range(1, n + 1) if Inc[i] >= 2 and Dec[i] >= 2]
    return max(c) if c else 0


def is_bitonic(X):
    n = len(X)
    return any(all(X[t] < X[t + 1] for t in range(i - 1)) and all(X[t] > X[t + 1] for t in range(i - 1, n - 1))
               for i in range(2, n))        # peak at 1-based position i, 1 < i < n


def brute_best(A, pred):
    return max(len(I) for I in subseqs(A) if pred([A[i] for i in I]))


def int_arrays(maxn, vals=range(4)):
    for n in range(maxn + 1):
        yield from (list(p) for p in itertools.product(vals, repeat=n))


def rand_ints(cnt, maxn, lo=0, hi=6):
    for _ in range(cnt):
        yield [random.randint(lo, hi) for _ in range(random.randint(0, maxn))]


gen5 = lambda: ((A,) for A in itertools.chain(int_arrays(6), rand_ints(400, 11)))
all_checks("3.5(c) bitonic vs brute force (all arrays n <= 6 over 0..3, + random)", gen5(), Bitonic,
           lambda A: brute_best(A, lambda X: len(X) == 0 or is_bitonic(X)) if any(is_bitonic([A[i] for i in I]) for I in subseqs(A)) else 0)


def Oscillating(A):
    """(d) OscDown(i) = 1 + max({0} u {OscUp(j) : j > i, A[j] < A[i]}), OscUp(i) = 1 + max({0} u {OscDown(j) : j > i, A[j] > A[i]});
    i from n down to 1, both at each i; answer max(0, max_i OscDown(i))."""
    n = len(A)
    Dn, Up = Memo(), Memo()
    for i in range(n, 0, -1):
        Dn[i] = 1 + max([0] + [Up[j] for j in range(i + 1, n + 1) if A[j - 1] < A[i - 1]])
        Up[i] = 1 + max([0] + [Dn[j] for j in range(i + 1, n + 1) if A[j - 1] > A[i - 1]])
    return max([0] + [Dn[i] for i in range(1, n + 1)])


def is_osc(X):
    # X[i] < X[i+1] for even i, X[i] > X[i+1] for odd i (1-based)
    return all((X[i - 1] < X[i]) if i % 2 == 0 else (X[i - 1] > X[i]) for i in range(1, len(X)))


all_checks("3.5(d) oscillating vs brute force", gen5(), Oscillating, lambda A: brute_best(A, is_osc))


def ShortestOscSuper(A):
    """(e) OscSuper(i, p) = length of a shortest oscillating supersequence of A[1..i] that ends with A[i] at a position of
    parity p (1 = odd, 0 = even).  OscSuper(1, odd) = 1, OscSuper(1, even) = 2;
    OscSuper(i, p) = min( OscSuper(i-1, p) + 2,  OscSuper(i-1, 1-p) + (1 if Step(i-1, 1-p) else 3) ),
    where Step(h, q) says A[h] at parity q may be followed directly by A[h+1]: A[h] > A[h+1] if q odd, A[h] < A[h+1] if even.
    answer 0 if n = 0, else min_p OscSuper(n, p)."""
    n = len(A)
    if n == 0:
        return 0
    step = lambda h, q: (A[h - 1] > A[h]) if q == 1 else (A[h - 1] < A[h])
    S = Memo()
    S[1, 1], S[1, 0] = 1, 2
    for i in range(2, n + 1):
        for p in (0, 1):
            S[i, p] = min(S[i - 1, p] + 2, S[i - 1, 1 - p] + (1 if step(i - 1, 1 - p) else 3))
    return min(S[n, 0], S[n, 1])


def brute_osc_super(A):
    """Independent: breadth-first search over sequences built one value at a time from V = [min-2, max+2];
    state = (# of A matched greedily, last value, length parity)."""
    n = len(A)
    if n == 0:
        return 0
    V = range(min(A) - 2, max(A) + 3)
    from collections import deque
    start = []
    dist = {}
    q = deque()
    for v in V:          # first element, at position 1
        st = (1 if v == A[0] else 0, v, 1)
        if st not in dist:
            dist[st] = 1
            q.append(st)
    while q:
        st = q.popleft()
        k, last, par = st
        if k == n:
            return dist[st]
        for v in V:
            ok = (last > v) if par == 1 else (last < v)       # position par: odd -> must go down
            if not ok:
                continue
            ns = (k + 1 if v == A[k] else k, v, 1 - par)
            if ns not in dist:
                dist[ns] = dist[st] + 1
                q.append(ns)


check("3.5(e) [1, 1] -> 3 (for instance 1, 0, 1); [3, 1, 2, 4] -> value of the DP equals BFS",
      ShortestOscSuper([1, 1]) == 3 == brute_osc_super([1, 1]) and is_osc([1, 0, 1])
      and ShortestOscSuper([3, 1, 2, 4]) == brute_osc_super([3, 1, 2, 4]))
all_checks("3.5(e) shortest oscillating supersequence vs breadth-first search",
           ((A,) for A in itertools.chain(int_arrays(5), rand_ints(300, 8))), ShortestOscSuper, brute_osc_super)


def PairDP(A, ok):
    """(f)(g)(h) Convex / WeakInc / DoubleInc(i, j), i < j: longest subsequence of the given kind that starts with A[i], A[j];
    DoubleInc(i, j) = 1 + max({1} u {DoubleInc(j, k) : k > j, A[k] > A[i]}), the others with their own test ok(A[i], A[j], A[k]); i from n down to 1 (outer), any j;
    answer n if n <= 2, else max_{i<j} F(i, j)."""
    n = len(A)
    if n <= 2:
        return n
    Fm = Memo()
    for i in range(n, 0, -1):
        for j in range(n, i, -1):
            Fm[i, j] = 1 + max([1] + [Fm[j, k] for k in range(j + 1, n + 1) if ok(A[i - 1], A[j - 1], A[k - 1])])
    return max(Fm[i, j] for i in range(1, n + 1) for j in range(i + 1, n + 1))


convex_ok = lambda a, b, c: 2 * b < a + c
weak_ok = lambda a, b, c: 2 * c > a + b
dbl_ok = lambda a, b, c: c > a
is_convex = lambda X: all(2 * X[i] < X[i - 1] + X[i + 1] for i in range(1, len(X) - 1))
is_weak = lambda X: all(2 * X[i] > X[i - 1] + X[i - 2] for i in range(2, len(X)))
is_dbl = lambda X: all(X[i] > X[i - 2] for i in range(2, len(X)))
gen6 = lambda: ((A,) for A in itertools.chain(int_arrays(6, range(-1, 3)), rand_ints(300, 10, -3, 5)))
all_checks("3.5(f) convex (pair DP) vs brute force", gen6(), lambda A: PairDP(A, convex_ok), lambda A: brute_best(A, is_convex))
all_checks("3.5(g) weakly increasing (pair DP) vs brute force", gen6(), lambda A: PairDP(A, weak_ok), lambda A: brute_best(A, is_weak))
all_checks("3.5(h) double-increasing (pair DP) vs brute force", gen6(), lambda A: PairDP(A, dbl_ok), lambda A: brute_best(A, is_dbl))

# ============================================================================ Exercise 3.6 — shuffles
print("== Exercise 3.6: shuffles")


def Shuffle(A, B, C):
    """(a) Shuf(i, j): is C[i+j-1..m+n] a shuffle of A[i..m] and B[j..n]?  Shuf(m+1, n+1) = True;
    Shuf(i, j) = (i <= m and A[i] = C[i+j-1] and Shuf(i+1, j)) or (j <= n and B[j] = C[i+j-1] and Shuf(i, j+1)).
    i from m+1 down to 1 (outer), j from n+1 down to 1 (inner)."""
    m, n = len(A), len(B)
    if len(C) != m + n:
        return False
    S = Memo()
    for i in range(m + 1, 0, -1):
        for j in range(n + 1, 0, -1):
            if i == m + 1 and j == n + 1:
                S[i, j] = True
            else:
                S[i, j] = ((i <= m and A[i - 1] == C[i + j - 2] and S[i + 1, j]) or
                           (j <= n and B[j - 1] == C[i + j - 2] and S[i, j + 1]))
    return S[1, 1]


def SmoothShuffle(X, Y, Z):
    """(b) SmX(i, j): is Z[i+j-1..] a smooth shuffle of X[i..m] and Y[j..n] whose first run comes from X
    (or are both suffixes empty)?  SmY symmetric.  SmX(m+1, n+1) = SmY(m+1, n+1) = True;
    SmX(i, j) = (i <= m and X[i] = Z[i+j-1] and SmY(i+1, j)) or (i+1 <= m and X[i..i+1] = Z[i+j-1..i+j] and SmY(i+2, j))
    SmY(i, j) = (j <= n and Y[j] = Z[i+j-1] and SmX(i, j+1)) or (j+1 <= n and Y[j..j+1] = Z[i+j-1..i+j] and SmX(i, j+2))
    i from m+1 down to 1 (outer), j from n+1 down to 1 (inner), SmX and SmY together; answer SmX(1,1) or SmY(1,1)."""
    m, n = len(X), len(Y)
    if len(Z) != m + n:
        return False
    SX, SY = Memo(), Memo()
    z = lambda t: Z[t - 1]
    get = lambda T, i, j: T[i, j] if (i <= m + 1 and j <= n + 1) else False   # out-of-range indices: False
    for i in range(m + 1, 0, -1):
        for j in range(n + 1, 0, -1):
            if i == m + 1 and j == n + 1:
                SX[i, j] = SY[i, j] = True
                continue
            SX[i, j] = ((i <= m and X[i - 1] == z(i + j - 1) and get(SY, i + 1, j)) or
                        (i + 1 <= m and X[i - 1] == z(i + j - 1) and X[i] == z(i + j) and get(SY, i + 2, j)))
            SY[i, j] = ((j <= n and Y[j - 1] == z(i + j - 1) and get(SX, i, j + 1)) or
                        (j + 1 <= n and Y[j - 1] == z(i + j - 1) and Y[j] == z(i + j) and get(SX, i, j + 2)))
    return bool(SX[1, 1] or SY[1, 1])


def brute_shuffle(A, B, C, smooth=False):
    m, n = len(A), len(B)
    if len(C) != m + n:
        return False
    for S in itertools.combinations(range(m + n), m):
        Ss = set(S)
        if [C[t] for t in S] == list(A) and [C[t] for t in range(m + n) if t not in Ss] == list(B):
            if not smooth:
                return True
            src = [t in Ss for t in range(m + n)]
            if all(not (src[t] == src[t + 1] == src[t + 2]) for t in range(m + n - 2)):
                return True
    return False


def shuffle_inputs(maxlen, alph="ab"):
    for A, B in strpairs(maxlen, alph):
        for C in itertools.product(alph, repeat=len(A) + len(B)):
            yield A, B, list(C)


all_checks("3.6(a) Shuffle vs brute force (all A, B over {a,b} of length <= 3, all C)", shuffle_inputs(3), Shuffle, brute_shuffle)
all_checks("3.6(b) SmoothShuffle vs brute force (same inputs)", shuffle_inputs(3), SmoothShuffle,
           lambda A, B, C: brute_shuffle(A, B, C, True))
all_checks("3.6(b) SmoothShuffle vs brute force (unary strings up to 8 + 8)",
           ((["x"] * a, ["x"] * b, ["x"] * (a + b)) for a in range(9) for b in range(9)), SmoothShuffle,
           lambda A, B, C: brute_shuffle(A, B, C, True))
rnd = []
for _ in range(400):
    A = [random.choice("ab") for _ in range(random.randint(0, 5))]
    B = [random.choice("ab") for _ in range(random.randint(0, 5))]
    C = list(A + B)
    pos = sorted(random.sample(range(len(C)), len(A))) if C else []
    it_a, it_b = iter(A), iter(B)
    C = [next(it_a) if t in pos else next(it_b) for t in range(len(C))]
    if random.random() < 0.3 and C:
        C[random.randrange(len(C))] = random.choice("ab")
    rnd.append((A, B, C))
all_checks("3.6(a) Shuffle vs brute force (random, length <= 5 + 5)", rnd, Shuffle, brute_shuffle)
all_checks("3.6(b) SmoothShuffle vs brute force (random, length <= 5 + 5)", rnd, SmoothShuffle,
           lambda A, B, C: brute_shuffle(A, B, C, True))
L = list


def greedy_A_first(A, B, C):
    """The trap: take the next character from A whenever it matches."""
    i = j = 0
    for c in C:
        if i < len(A) and A[i] == c:
            i += 1
        elif j < len(B) and B[j] == c:
            j += 1
        else:
            return False
    return i == len(A) and j == len(B)


check("3.6(a) trap: acab is a shuffle of ab and ac, but A-first greedy says no",
      Shuffle(L("ab"), L("ac"), L("acab")) and not greedy_A_first("ab", "ac", "acab"))
check("3.6 BANANAANANAS is a shuffle of BANANA and ANANAS", Shuffle(L("BANANA"), L("ANANAS"), L("BANANAANANAS")))
check("3.6 PRODGYRNAMAMMIINCG and DYPRONGARMAMMICING are shuffles of DYNAMIC and PROGRAMMING",
      Shuffle(L("DYNAMIC"), L("PROGRAMMING"), L("PRODGYRNAMAMMIINCG")) and
      Shuffle(L("DYNAMIC"), L("PROGRAMMING"), L("DYPRONGARMAMMICING")))
check("3.6(b) PRDOYGNARAMMMIICNG is a smooth shuffle", SmoothShuffle(L("DYNAMIC"), L("PROGRAMMING"), L("PRDOYGNARAMMMIICNG")))
check("3.6(b) DYPRNOGRAAMMMICING is a shuffle but not smooth",
      Shuffle(L("DYNAMIC"), L("PROGRAMMING"), L("DYPRNOGRAAMMMICING")) and
      not SmoothShuffle(L("DYNAMIC"), L("PROGRAMMING"), L("DYPRNOGRAAMMMICING")))
# the book's colored example interleaves runs XX,X,X,X,X,XX,XX,XX,XX,X,X,X,XX: blue 2+1+1+2+2+1+2 = 11, red 1+1+2+2+1+1 = 8
runs_blue, runs_red = [2, 1, 1, 2, 2, 1, 2], [1, 1, 2, 2, 1, 1]
check("3.6(b) the book's picture of 19 X's uses 8 + 11 symbols (the book prints the first string with 7)",
      sum(runs_blue) == 11 and sum(runs_red) == 8 and sum(runs_blue) + sum(runs_red) == 19)
check("3.6(b) X^19 is a smooth shuffle of X^8 and X^11; X^18 of X^7 and X^11; none for X^4 and X^12",
      SmoothShuffle(["X"] * 8, ["X"] * 11, ["X"] * 19) and SmoothShuffle(["X"] * 7, ["X"] * 11, ["X"] * 18)
      and not SmoothShuffle(["X"] * 4, ["X"] * 12, ["X"] * 16))
check("3.6(b) unary rule: X^a, X^b smooth iff max(a,b) <= 2(min(a,b)+1)",
      all(SmoothShuffle(["x"] * a, ["x"] * b, ["x"] * (a + b)) == (max(a, b) <= 2 * (min(a, b) + 1))
          for a in range(9) for b in range(9)))

# ============================================================================ Exercise 3.7 — subsequence problems
print("== Exercise 3.7: subsequences of Y")


def IsSubsequence(X, Y):
    """(a) greedy: match X[i] with the first unused occurrence in Y."""
    i = 0
    for y in Y:
        if i < len(X) and X[i] == y:
            i += 1
    return i == len(X)


def Cut(X, Y):
    """(b) Cut(i, j): fewest symbols to delete from Y[j..n] so that X[i..k] is not a subsequence of what is left.
    Cut(k+1, j) = inf; Cut(i, n+1) = 0 for i <= k;
    Cut(i, j) = Cut(i, j+1) if Y[j] != X[i];  min(1 + Cut(i, j+1), Cut(i+1, j+1)) if Y[j] = X[i].
    j from n+1 down to 1 (outer), i from k+1 down to 1 (inner)."""
    k, n = len(X), len(Y)
    C = Memo()
    for j in range(n + 1, 0, -1):
        for i in range(k + 1, 0, -1):
            if i == k + 1:
                C[i, j] = INF
            elif j == n + 1:
                C[i, j] = 0
            elif Y[j - 1] != X[i - 1]:
                C[i, j] = C[i, j + 1]
            else:
                C[i, j] = min(1 + C[i, j + 1], C[i + 1, j + 1])
    return C[1, 1]


def brute_cut(X, Y):
    n = len(Y)
    for r in range(n + 1):
        for D_ in itertools.combinations(range(n), r):
            rest = [Y[t] for t in range(n) if t not in D_]
            if not is_subseq(X, rest):
                return r
    return INF


def MinCost(X, Y, Cst):
    """(d) MinCost(i, j): cheapest occurrence of X[i..k] in Y[j..n]; MinCost(k+1, j) = 0; MinCost(i, n+1) = inf (i <= k);
    MinCost(i, j) = min(MinCost(i, j+1), C[j] + MinCost(i+1, j+1) if X[i] = Y[j])."""
    k, n = len(X), len(Y)
    Mc = Memo()
    for j in range(n + 1, 0, -1):
        for i in range(k + 1, 0, -1):
            if i == k + 1:
                Mc[i, j] = 0
            elif j == n + 1:
                Mc[i, j] = INF
            else:
                Mc[i, j] = min(Mc[i, j + 1], Cst[j - 1] + Mc[i + 1, j + 1] if X[i - 1] == Y[j - 1] else INF)
    return Mc[1, 1]


def NumOcc(X, Y):
    """(e) NumOcc(i, j) = # occurrences of X[i..k] in Y[j..n]; NumOcc(k+1, j) = 1; NumOcc(i, n+1) = 0 (i <= k);
    NumOcc(i, j) = NumOcc(i, j+1) + [X[i] = Y[j]] * NumOcc(i+1, j+1)."""
    k, n = len(X), len(Y)
    Cn = Memo()
    for j in range(n + 1, 0, -1):
        for i in range(k + 1, 0, -1):
            if i == k + 1:
                Cn[i, j] = 1
            elif j == n + 1:
                Cn[i, j] = 0
            else:
                Cn[i, j] = Cn[i, j + 1] + (Cn[i + 1, j + 1] if X[i - 1] == Y[j - 1] else 0)
    return Cn


def occurrences(X, Y):
    return [I for I in itertools.combinations(range(len(Y)), len(X)) if all(Y[I[t]] == X[t] for t in range(len(X)))]


def xy_pairs(maxk, maxn, alph="ab"):
    for n in range(maxn + 1):
        for k in range(min(maxk, n) + 1):
            for X in itertools.product(alph, repeat=k):
                for Y in itertools.product(alph, repeat=n):
                    yield list(X), list(Y)


all_checks("3.7(a) greedy IsSubsequence vs brute force (k <= n <= 7 over {a,b})", xy_pairs(4, 7), IsSubsequence,
           lambda X, Y: len(occurrences(X, Y)) > 0)
all_checks("3.7(b) Cut vs brute force (k <= 3, n <= 7 over {a,b})", xy_pairs(3, 7), Cut, brute_cut)
all_checks("3.7(b) Cut vs brute force (random over {a,b,c}, n <= 9)",
           ((L("".join(random.choice("abc") for _ in range(random.randint(1, 3)))),
             L("".join(random.choice("abc") for _ in range(random.randint(3, 9))))) for _ in range(300)), Cut, brute_cut)
ok = True
for X, Y in xy_pairs(3, 7):
    Cst = [random.choice([-3, -1, 0, 1, 2, 5]) for _ in Y]
    occ = occurrences(X, Y)
    want = min((sum(Cst[t] for t in I) for I in occ), default=INF)
    if MinCost(X, Y, Cst) != want:
        ok = False
        break
check("3.7(d) MinCost vs brute force (all k <= 3, n <= 7, random costs incl. negative)", ok)
all_checks("3.7(e) NumOcc vs brute force (k <= 4, n <= 7)", xy_pairs(4, 7), lambda X, Y: NumOcc(X, Y)[1, 1],
           lambda X, Y: len(occurrences(X, Y)))
PEN, PPAP = L("PENPINEAPPLEAPPLEPEN"), L("PPAP")
check("3.7(a) PPAP is a subsequence of PENPINEAPPLEAPPLEPEN", IsSubsequence(PPAP, PEN))
check("3.7(b) removing 2 symbols kills PPAP (and 1 does not)", Cut(PPAP, PEN) == 2 == brute_cut(PPAP, PEN))
check("3.7(b) the A's of PENPINEAPPLEAPPLEPEN are at positions 8 and 13; deleting them kills PPAP",
      [t + 1 for t, c in enumerate(PEN) if c == "A"] == [8, 13] and not IsSubsequence(PPAP, [c for c in PEN if c != "A"]))
check("3.7(e) PPAP occurs 23 times", NumOcc(PPAP, PEN)[1, 1] == 23 == len(occurrences(PPAP, PEN)))
check("3.7(e) all-equal strings give C(n,k) for all k <= n <= 12",
      all(NumOcc(["x"] * k, ["x"] * n)[1, 1] == math.comb(n, k) for n in range(13) for k in range(n + 1)))
ok = True
for X, Y in xy_pairs(3, 7):
    Cn = NumOcc(X, Y)
    k, n = len(X), len(Y)
    if any(Cn[i, j] > math.comb(n - j + 1, k - i + 1) for i in range(1, k + 2) for j in range(1, n + 2)):
        ok = False
check("3.7(f) every NumOcc(i, j) <= C(n-j+1, k-i+1) <= 2^n (so entries have O(n) bits)", ok)
check("3.7(f) C(n, n/2) has at least n - log2(n+1) bits (so Theta(n)-bit numbers do occur), n <= 400",
      all(math.comb(n, n // 2).bit_length() >= n - math.log2(n + 1) for n in range(1, 401)))
check("3.7(f) log2 C(n,k) <= k log2(e n / k) for 1 <= k <= n <= 200",
      all(math.log2(math.comb(n, k)) <= k * math.log2(math.e * n / k) + 1e-9 for n in range(1, 201) for k in range(1, n + 1)))

# ============================================================================ Exercise 3.8 — forward and backward
print("== Exercise 3.8: longest substring that appears forward and backward")


def ForwardBackward(T):
    """Mirror(i, j) = 0 if i >= j or T[i] != T[j]; else 1 + Mirror(i+1, j-1).  Answer max_{i<j} Mirror(i, j) (0 if n < 2).
    i from n down to 1 (outer), j from 1 to n (inner)."""
    n = len(T)
    R = Memo()
    for i in range(n + 1, 0, -1):          # i = n+1 row only for the boundary R[i+1, j-1]
        for j in range(0, n + 1):
            if i >= j or T[i - 1] != T[j - 1]:
                R[i, j] = 0
            else:
                R[i, j] = 1 + R[i + 1, j - 1]
    return max([0] + [R[i, j] for i in range(1, n + 1) for j in range(i + 1, n + 1)])


def brute_fb(T):
    n = len(T)
    best = 0
    for L_ in range(1, n // 2 + 1):
        for i in range(n - L_ + 1):
            for j in range(n - L_ + 1):
                if (i + L_ <= j or j + L_ <= i) and T[i:i + L_] == T[j:j + L_][::-1]:
                    best = max(best, L_)
    return best


all_checks("3.8 Mirror recurrence vs brute force (all strings over {a,b} of length <= 12, + random over {a,b,c} up to 20)",
           ((s,) for s in itertools.chain(("".join(p) for n in range(13) for p in itertools.product("ab", repeat=n)),
                                          ("".join(random.choice("abc") for _ in range(random.randint(0, 20))) for _ in range(500)))),
           ForwardBackward, brute_fb)
for s, want in [("ALGORITHM", 0), ("RECURSION", 1), ("REDIVIDE", 3), ("DYNAMICPROGRAMMINGMANYTIMES", 4)]:
    check(f"3.8 {s} -> {want}", ForwardBackward(s) == want == brute_fb(s))
check("3.8 REDIVIDE: EDI = T[2..4] and its reversal IDE = T[6..8] do not overlap",
      "REDIVIDE"[1:4] == "EDI" and "REDIVIDE"[5:8] == "IDE")
def mirror_table(T):
    n = len(T)
    R = {}
    for i in range(n, 0, -1):
        for j in range(1, n + 1):
            R[i, j] = 0 if (i >= j or T[i - 1] != T[j - 1]) else 1 + R[i + 1, j - 1]
    return R


check("3.8 REDIVIDE: Mirror(2, 8) = 3", mirror_table("REDIVIDE")[2, 8] == 3)
check("3.8 YNAM and MANY: DYNAMICPROGRAMMINGMANYTIMES[2..5] = YNAM, [19..22] = MANY",
      "DYNAMICPROGRAMMINGMANYTIMES"[1:5] == "YNAM" and "DYNAMICPROGRAMMINGMANYTIMES"[18:22] == "MANY")

# ============================================================================ Exercise 3.9 — palindromes
print("== Exercise 3.9: palindromes")


def LongestPalSubseq(T):
    """(a) LPS(i, j) = 0 if i > j, 1 if i = j; else max(LPS(i+1, j), LPS(i, j-1), 2 + LPS(i+1, j-1) if T[i] = T[j]).
    i from n down to 1 (outer), j from i-1 up to n (inner)."""
    n = len(T)
    P = Memo()
    for i in range(n + 1, 0, -1):
        for j in range(i - 1, n + 1):
            if j < i:
                P[i, j] = 0
            elif i == j:
                P[i, j] = 1
            else:
                P[i, j] = max(P[i + 1, j], P[i, j - 1], 2 + P[i + 1, j - 1] if T[i - 1] == T[j - 1] else 0)
    return P[1, n] if n else 0


def ShortestPalSuper(T):
    """(b) SPS(i, j) = 0 if i > j, 1 if i = j; else 2 + min(SPS(i+1, j), SPS(i, j-1), SPS(i+1, j-1) if T[i] = T[j])."""
    n = len(T)
    S = Memo()
    for i in range(n + 1, 0, -1):
        for j in range(i - 1, n + 1):
            if j < i:
                S[i, j] = 0
            elif i == j:
                S[i, j] = 1
            else:
                S[i, j] = 2 + min(S[i + 1, j], S[i, j - 1], S[i + 1, j - 1] if T[i - 1] == T[j - 1] else INF)
    return S[1, n] if n else 0


def IsPalTable(T):
    """IsPal(i, j) = True if j <= i; else T[i] = T[j] and IsPal(i+1, j-1); i from n down to 1, j from i-1 up to n."""
    n = len(T)
    P = Memo()
    for i in range(n + 1, 0, -1):
        for j in range(i - 1, n + 1):
            P[i, j] = True if j <= i else (T[i - 1] == T[j - 1] and P[i + 1, j - 1])
    return P


def MinPal(T):
    """(c) MinPal(n+1) = 0; MinPal(i) = 1 + min{MinPal(j+1) : i <= j <= n, IsPal(i, j)}; i decreasing."""
    n = len(T)
    P = IsPalTable(T)
    Mp = Memo()
    Mp[n + 1] = 0
    for i in range(n, 0, -1):
        Mp[i] = 1 + min(Mp[j + 1] for j in range(i, n + 1) if P[i, j])
    return Mp[1]


def MaxMinLen(T):
    """(d) MaxMinLen(n+1) = inf; MaxMinLen(i) = max{min(j-i+1, MaxMinLen(j+1)) : i <= j <= n, IsPal(i, j)}; i decreasing."""
    n = len(T)
    P = IsPalTable(T)
    Mm = Memo()
    Mm[n + 1] = INF
    for i in range(n, 0, -1):
        Mm[i] = max(min(j - i + 1, Mm[j + 1]) for j in range(i, n + 1) if P[i, j])
    return Mm[1]


def NumPal(T):
    """(e) NumPal(n+1) = 1; NumPal(i) = sum{NumPal(j+1) : i <= j <= n, IsPal(i, j)}; i decreasing."""
    n = len(T)
    P = IsPalTable(T)
    Np = Memo()
    Np[n + 1] = 1
    for i in range(n, 0, -1):
        Np[i] = sum(Np[j + 1] for j in range(i, n + 1) if P[i, j])
    return Np[1]


ispal = lambda s: s == s[::-1]


def brute_lps(T):
    return max(len(I) for I in subseqs(T) if ispal("".join(T[i] for i in I)))


def brute_sps(T):
    alph = sorted(set(T)) + ["#"]
    n = len(T)
    for Lh in range(n, 2 * n + 1):
        half = (Lh + 1) // 2
        for h in itertools.product(alph, repeat=half):
            h = "".join(h)
            P = h + (h[::-1][1:] if Lh % 2 else h[::-1])
            if is_subseq(T, P):
                return Lh


def decomps(T):
    for P in cutsets(len(T)):
        pieces = [T[s - 1:e] for s, e in P]
        if all(ispal(p) for p in pieces):
            yield pieces


nonempty = lambda maxn, alph: ("".join(p) for n in range(1, maxn + 1) for p in itertools.product(alph, repeat=n))
all_checks("3.9(a) LPS vs brute force (all strings over {a,b,c} of length <= 7)", ((s,) for s in nonempty(7, "abc")),
           LongestPalSubseq, brute_lps)
all_checks("3.9(b) SPS vs brute force (all strings over {a,b,c} of length <= 5)", ((s,) for s in nonempty(5, "abc")),
           ShortestPalSuper, brute_sps)
all_checks("3.9(c) MinPal vs brute force (all strings over {a,b,c} of length <= 8)", ((s,) for s in nonempty(8, "abc")),
           MinPal, lambda s: min(len(d) for d in decomps(s)))
all_checks("3.9(d) MaxMinLen vs brute force", ((s,) for s in nonempty(8, "abc")), MaxMinLen,
           lambda s: max(min(len(p) for p in d) for d in decomps(s)))
all_checks("3.9(e) NumPal vs brute force", ((s,) for s in nonempty(8, "abc")), NumPal, lambda s: sum(1 for _ in decomps(s)))
check("3.9(a) MAHDYNAMICPROGRAMZLETMESHOWYOUTHEM -> 11", LongestPalSubseq("MAHDYNAMICPROGRAMZLETMESHOWYOUTHEM") == 11)
check("3.9(a) MHYMRORMYHM is a palindromic subsequence of it",
      ispal("MHYMRORMYHM") and is_subseq("MHYMRORMYHM", "MAHDYNAMICPROGRAMZLETMESHOWYOUTHEM"))
check("3.9(b) TWENTYONE -> 13 (TWENTOYOTNEWT)", ShortestPalSuper("TWENTYONE") == 13 and ispal("TWENTOYOTNEWT")
      and is_subseq("TWENTYONE", "TWENTOYOTNEWT"))
BUB = "BUBBASEESABANANA"
check("3.9(c) BUBBASEESABANANA -> 3", MinPal(BUB) == 3)
check("3.9(d) PALINDROME -> 1, BUBBASEESABANANA -> 3, a^n -> n",
      MaxMinLen("PALINDROME") == 1 and MaxMinLen(BUB) == 3 and all(MaxMinLen("a" * n) == n for n in range(1, 15)))
check("3.9(e) PALINDROME -> 1, a^n -> 2^(n-1)",
      NumPal("PALINDROME") == 1 and all(NumPal("a" * n) == 2 ** (n - 1) for n in range(1, 15)))
nb = sum(1 for _ in decomps(BUB))
check("3.9(e) BUBBASEESABANANA -> 97 by the DP and by listing all 2^15 cut sets (the book says 70 = 5 shown + 65 others)",
      NumPal(BUB) == 97 == nb, f"DP {NumPal(BUB)}, brute force {nb}")
pals = sorted({(i + 1, i + L) for L in range(2, 17) for i in range(17 - L) if ispal(BUB[i:i + L])})
check("3.9(e) BUBBASEESABANANA has exactly 11 palindromic substrings of length >= 2",
      len(pals) == 11, ", ".join(BUB[a - 1:b] for a, b in pals))
check("3.9(c) the five decompositions shown are palindromic decompositions of BUBBASEESABANANA",
      all("".join(d) == BUB and all(ispal(p) for p in d) for d in
          [["BUB", "BASEESAB", "ANANA"], ["B", "U", "BB", "ASEESA", "B", "ANANA"], ["BUB", "B", "A", "SEES", "ABA", "N", "ANA"],
           ["B", "U", "BB", "A", "S", "EE", "S", "A", "B", "A", "NAN", "A"], list(BUB)]))

# ============================================================================ Exercise 3.10 — back and forth
print("== Exercise 3.10: increasing back-and-forth subsequences")


def BackForth(A, rule="book"):
    """BackForth(i) = 1 + max({0} u {BackForth(j) : A[j] > A[i], and j > i if i is even, j < i if i is odd});
    evaluated in decreasing order of A[i]; answer max_i BackForth(i) (0 if n = 0)."""
    n = len(A)
    allowed = (lambda i, j: (j > i) if i % 2 == 0 else (j < i)) if rule == "book" else \
              (lambda i, j: (j < i) if i % 2 == 0 else (j > i))
    Bf = Memo()
    for i in sorted(range(1, n + 1), key=lambda t: -A[t - 1]):
        Bf[i] = 1 + max([0] + [Bf[j] for j in range(1, n + 1) if A[j - 1] > A[i - 1] and allowed(i, j)])
    return max([0] + [Bf[i] for i in range(1, n + 1)])


def brute_bf(A, rule="book"):
    n = len(A)
    allowed = (lambda i, j: (j > i) if i % 2 == 0 else (j < i)) if rule == "book" else \
              (lambda i, j: (j < i) if i % 2 == 0 else (j > i))
    best = 0

    def dfs(i, L_):
        nonlocal best
        best = max(best, L_)
        for j in range(1, n + 1):
            if A[j - 1] > A[i - 1] and allowed(i, j):
                dfs(j, L_ + 1)
    for i in range(1, n + 1):
        dfs(i, 1)
    return best


all_checks("3.10 BackForth recurrence vs brute force (all arrays n <= 6 over 1..4, + random n <= 10)",
           ((A,) for A in itertools.chain(int_arrays(6, range(1, 5)), rand_ints(400, 10, 1, 9))), BackForth, brute_bf)
EX10 = [1, 1, 8, 7, 5, 6, 3, 6, 4, 4, 8, 3, 9, 1, 2, 2, 3, 9, 4, 0]
check("3.10 book's example array: answer 7 under the stated rule", BackForth(EX10) == 7 == brute_bf(EX10))
seq7 = [14, 15, 12, 19, 5, 4, 11]
okseq = all(EX10[a - 1] < EX10[b - 1] and ((b > a) if a % 2 == 0 else (b < a)) for a, b in zip(seq7, seq7[1:]))
check("3.10 positions 14,15,12,19,5,4,11 (values 1,2,3,4,5,7,8) form a valid sequence",
      okseq and [EX10[t - 1] for t in seq7] == [1, 2, 3, 4, 5, 7, 8])
book_seq = [20, 1, 15, 18, 10, 6, 4, 3, 13]
check("3.10 the book's sequence moves right from odd squares and left from even ones (opposite of the rule)",
      all(((b > a) if a % 2 == 1 else (b < a)) for a, b in zip(book_seq, book_seq[1:])))
check("3.10 the book's sequence has A[18] = 9, not 3 (so it is not increasing either)",
      [EX10[t - 1] for t in book_seq] == [0, 1, 2, 9, 4, 6, 7, 8, 9])
sw = [20, 1, 16, 7, 10, 5, 6, 4, 3, 13]
check("3.10 swapped rule: 20,1,16,7,10,5,6,4,3,13 is valid with values 0..9",
      [EX10[t - 1] for t in sw] == list(range(10))
      and all(((b > a) if a % 2 == 1 else (b < a)) for a, b in zip(sw, sw[1:])))
check("3.10 with the directions swapped the answer would be 10, not 9", BackForth(EX10, "swapped") == 10 == brute_bf(EX10, "swapped"))

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: {FAIL}")
