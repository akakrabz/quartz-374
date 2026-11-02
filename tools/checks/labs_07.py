#!/usr/bin/env python3
"""Checks for content/3-homework-and-exams/lab-07a.md (backtracking) and lab-07b.md (dynamic programming):
longest decreasing, alternating and convex subsequences, longest palindrome subsequence, shortest palindrome
supersequence.

Lab 7a: every recurrence is implemented as plain recursion exactly as the page states it (with call counters for the
running-time claims).  Lab 7b: every dynamic program is filled in the page's evaluation order with a memo table that
refuses to be read before it is written (so a wrong order fails loudly).  Everything is compared with brute force over
ALL subsequences (and, for supersequences, over all palindromes of each length) on all small arrays plus random ones.
The handout examples (5, 17, 6, 7, 15) are reproduced, every witness subsequence is checked, and the official
solutions' variants that the pages correct are shown to fail."""
import functools
import itertools
import random
import sys

random.seed(374)
sys.setrecursionlimit(100000)
INF = float("inf")
FAIL = []


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


def all_checks(name, inputs, f, g):
    cnt = 0
    for a in inputs:
        cnt += 1
        x, y = f(a), g(a)
        if x != y:
            check(name, False, f"input {a}: page {x}, brute force {y}")
            return
    check(name, True, f"{cnt} inputs")


# ------------------------------------------------------------------ inputs
def int_arrays(nmax, vals):
    for n in range(nmax + 1):
        yield from (list(t) for t in itertools.product(vals, repeat=n))


def perms(nmax):
    for n in range(nmax + 1):
        yield from (list(p) for p in itertools.permutations(range(1, n + 1)))


def rand_arrays(count, nlo, nhi, lo, hi):
    return [[random.randint(lo, hi) for _ in range(random.randint(nlo, nhi))] for _ in range(count)]


SMALL = list(int_arrays(7, range(1, 5))) + list(perms(7)) + rand_arrays(400, 8, 12, -6, 6)
TINY = list(int_arrays(5, range(1, 4))) + list(perms(5)) + rand_arrays(60, 6, 7, 1, 4)   # for supersequences

PI = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5, 8, 9, 7, 9, 3, 2, 3, 8, 4, 6, 2, 7]
PI10 = PI[:10]
check("the handout's array has 23 elements; Problem 5 uses its first 10", len(PI) == 23 and PI10 == [3, 1, 4, 1, 5, 9, 2, 6, 5, 3])


# ------------------------------------------------------------------ definitions (literal, 1-based as in the handout)
def is_subseq(x, y):
    it = iter(y)
    return all(c in it for c in x)


def is_decreasing(B):          # B[i] < B[i-1] for every i >= 2
    return all(B[i] < B[i - 1] for i in range(1, len(B)))


def is_alternating(B):         # B[i] < B[i-1] for even i >= 2, B[i] > B[i-1] for odd i >= 3 (1-based)
    return all((B[i - 1] < B[i - 2]) if i % 2 == 0 else (B[i - 1] > B[i - 2]) for i in range(2, len(B) + 1))


def is_convex(B):              # B[i] - B[i-1] > B[i-1] - B[i-2] for every i >= 3
    return all(B[i] - B[i - 1] > B[i - 1] - B[i - 2] for i in range(2, len(B)))


def is_palindrome(B):          # B[i] = B[l - i + 1]
    return all(B[i] == B[len(B) - 1 - i] for i in range(len(B)))


def is_zigzag(B):              # steps strictly alternate in direction, either first direction
    d = [(B[i] > B[i - 1]) - (B[i] < B[i - 1]) for i in range(1, len(B))]
    return all(x != 0 for x in d) and all(d[i] == -d[i - 1] for i in range(1, len(d)))


BRUTE = {}


def brute_longest(A, pred):
    """Largest length of a subsequence (over all 2^n index subsets) satisfying pred (cached per input)."""
    key = (tuple(A), pred.__name__)
    if key not in BRUTE:
        BRUTE[key] = _brute_longest(A, pred)
    return BRUTE[key]


def _brute_longest(A, pred):
    n = len(A)
    best = 0
    for m in range(1 << n):
        B = [A[i] for i in range(n) if m >> i & 1]
        if len(B) > best and pred(B):
            best = len(B)
    return best


def brute_sps(A):
    """Shortest palindrome containing A: try every palindrome of each length L = n, n+1, ... over A's symbols plus a
    fresh one (enough: a symbol the embedding does not use can be deleted together with its mirror image)."""
    n = len(A)
    if n == 0:
        return 0
    alph = sorted(set(A)) + [max(A) + 1]
    for L in range(n, 2 * n):
        h = (L + 1) // 2
        for half in itertools.product(alph, repeat=h):
            P = list(half) + list(half[:L // 2])[::-1]
            if is_subseq(A, P):
                return L
    raise AssertionError("no palindrome of length < 2n")


# subsequence/substring examples from the two handouts (SUBSEQUENCE)
W = "SUBSEQUENCE"
check("handouts: SUBSEQUENCE, UBSEQU and the empty string are substrings of SUBSEQUENCE",
      all(s in W for s in ["SUBSEQUENCE", "UBSEQU", ""]))
check("handouts: SBSQNC, SQUEE, UEQUE, EEE are subsequences but not substrings",
      all(is_subseq(s, W) and s not in W for s in ["SBSQNC", "SQUEE", "UEQUE", "EEE"]))
check("handouts: QUEUE, EQUUS, DIMAGGIO, SSS, FOOBAR are not subsequences",
      all(not is_subseq(s, W) for s in ["QUEUE", "EQUUS", "DIMAGGIO", "SSS", "FOOBAR"]))
check("alternating means: first step down, then up, down, ... (3,1,4 yes; 1,3,2 no)",
      is_alternating([3, 1, 4]) and not is_alternating([1, 3, 2]) and is_alternating([5]) and is_alternating([]))
check("convex <=> 2B[i-1] < B[i-2] + B[i] (all triples of small integers)",
      all((c - b > b - a) == (2 * b < a + c) for a, b, c in itertools.product(range(-3, 4), repeat=3)))

# ================================================================== LAB 7a: the recurrences as backtracking
print("\n== Lab 7a, Problem 1: longest decreasing subsequence")
CALLS = [0]


def LDS_main(A):
    """LDSsmaller(i, j): longest decreasing subsequence of A[j..n] with every element smaller than A[i]; A[0] = +inf;
    answer LDSsmaller(0, 1).  Plain recursion."""
    n = len(A)
    X = [INF] + A

    def LDSsmaller(i, j):
        CALLS[0] += 1
        if j > n:
            return 0
        if X[j] >= X[i]:
            return LDSsmaller(i, j + 1)
        return max(LDSsmaller(i, j + 1), 1 + LDSsmaller(j, j + 1))

    return LDSsmaller(0, 1)


def LDS_first(A, sentinel=True):
    """LDSfirst(i) = 1 + max{LDSfirst(j) : j > i, A[j] < A[i]}, max of nothing = 0."""
    n = len(A)
    X = [INF] + A

    def LDSfirst(i):
        return 1 + max([LDSfirst(j) for j in range(i + 1, n + 1) if X[j] < X[i]], default=0)

    return LDSfirst(0) - 1 if sentinel else max([LDSfirst(i) for i in range(1, n + 1)], default=0)


def LDS_prefix(A):
    """Official 'prefix plus one later index': LDS(i, j) over A[1..i], every element larger than A[j]; A[n+1] = -inf."""
    n = len(A)
    X = [None] + A + [-INF]

    def L(i, j):
        if i < 1:
            return 0
        if X[i] <= X[j]:
            return L(i - 1, j)
        return max(L(i - 1, j), 1 + L(i - 1, i))

    return L(n, n + 1)


def LIS_bigger(A):
    """The site's LISbigger(0, 1) with A[0] = -inf (Algorithms §2.6)."""
    n = len(A)
    X = [-INF] + A

    @functools.lru_cache(None)
    def L(i, j):
        if j > n:
            return 0
        if X[i] >= X[j]:
            return L(i, j + 1)
        return max(L(i, j + 1), 1 + L(j, j + 1))

    return L(0, 1)


brute_dec = lambda A: brute_longest(A, is_decreasing)
all_checks("7a P1: LDSsmaller(0,1) with A[0] = +inf equals brute force", SMALL, LDS_main, brute_dec)
all_checks("7a P1: LDSfirst(0) - 1 with A[0] = +inf equals brute force", SMALL, LDS_first, brute_dec)
all_checks("7a P1: max_i LDSfirst(i) equals brute force", SMALL, lambda A: LDS_first(A, False), brute_dec)
all_checks("7a P1: official prefix version LDS(n, n+1) equals brute force", SMALL, LDS_prefix, brute_dec)
all_checks("7a P1: LIS of the negated array equals brute force", SMALL, lambda A: LIS_bigger([-x for x in A]), brute_dec)
all_checks("7a P1: LIS of the reversed array equals brute force", SMALL, lambda A: LIS_bigger(A[::-1]), brute_dec)

ok = True
for n in range(0, 13):
    CALLS[0] = 0
    LDS_main(list(range(n, 0, -1)))
    ok &= CALLS[0] == 2 ** (n + 1) - 1
check("7a P1 time: on a strictly decreasing array LDSsmaller(0,1) makes exactly 2^(n+1) - 1 calls (n <= 12)", ok)
worst = {}
for A in SMALL:
    CALLS[0] = 0
    LDS_main(A)
    worst[len(A)] = max(worst.get(len(A), 0), CALLS[0])
check("7a P1 time: never more than 2^(n+1) - 1 calls (T(n) <= 2T(n-1) + O(1))",
      all(c <= 2 ** (n + 1) - 1 for n, c in worst.items()), worst)

print("\n== Lab 7a, Problem 2: longest alternating subsequence")


def LAS_main(A):
    """LASabove(i, j): longest alternating (down, up, down, ...) subsequence of A[j..n] whose first element is larger
    than A[i]; LASbelow(i, j): longest inverted (up, down, ...) subsequence of A[j..n] whose first element is smaller
    than A[i].  A[0] = -inf; answer LASabove(0, 1)."""
    n = len(A)
    X = [-INF] + A

    def above(i, j):
        CALLS[0] += 1
        if j > n:
            return 0
        if X[j] <= X[i]:
            return above(i, j + 1)
        return max(above(i, j + 1), 1 + below(j, j + 1))

    def below(i, j):
        CALLS[0] += 1
        if j > n:
            return 0
        if X[j] >= X[i]:
            return below(i, j + 1)
        return max(below(i, j + 1), 1 + above(j, j + 1))

    return above(0, 1)


def LAS_first(A):
    """Down(i) = 1 + max{Up(j) : j > i, A[j] < A[i]}, Up(i) = 1 + max{Down(j) : j > i, A[j] > A[i]};
    answer max_i Down(i) (0 if n = 0) — Exercise 2.4(d) / 3.5(d)."""
    n = len(A)

    @functools.lru_cache(None)
    def Down(i):
        return 1 + max([Up(j) for j in range(i + 1, n) if A[j] < A[i]], default=0)

    @functools.lru_cache(None)
    def Up(i):
        return 1 + max([Down(j) for j in range(i + 1, n) if A[j] > A[i]], default=0)

    return max([Down(i) for i in range(n)], default=0)


brute_alt = lambda A: brute_longest(A, is_alternating)
all_checks("7a P2: LASabove(0,1) with A[0] = -inf equals brute force", SMALL, LAS_main, brute_alt)
all_checks("7a P2: one-parameter version max_i Down(i) equals brute force", SMALL, LAS_first, brute_alt)
worst = {}
for A in SMALL:
    CALLS[0] = 0
    LAS_main(A)
    worst[len(A)] = max(worst.get(len(A), 0), CALLS[0])
check("7a P2 time: never more than 2^(n+1) - 1 calls", all(c <= 2 ** (n + 1) - 1 for n, c in worst.items()), worst)

print("\n== Lab 7a, Problem 3: longest convex subsequence")


def LXS_main(A, base=2):
    """LXS(i, j) = max({2} U {1 + LXS(j, k) : j < k <= n, A[i] + A[k] > 2A[j]}); answer max_{i<j} LXS(i, j), or n if
    n <= 1.  base=0 with '1 + max' gives the official recurrence (max of nothing = 0)."""
    n = len(A)
    X = [None] + A

    def LXS(i, j):
        CALLS[0] += 1
        if base == 2:
            return max([2] + [1 + LXS(j, k) for k in range(j + 1, n + 1) if X[i] + X[k] > 2 * X[j]])
        return 1 + max([LXS(j, k) for k in range(j + 1, n + 1) if X[i] + X[k] > 2 * X[j]], default=0)

    if base == 2:
        return max([min(n, 2)] + [LXS(i, j) for i in range(1, n + 1) for j in range(i + 1, n + 1)])
    return max([LXS(i, j) for i in range(1, n + 1) for j in range(i + 1, n + 1)], default=0)


def LXS_sentinel(A, base=2):
    """Shift so that the minimum is 0, add A[0] = 2M + 1 and A[-1] = 4M + 3 (M = new maximum); answer LXS(-1, 0) - 2."""
    n = len(A)
    if n == 0:
        Y = []
    else:
        m = min(A)
        Y = [x - m for x in A]
    M = max(Y, default=0)
    X = {-1: 4 * M + 3, 0: 2 * M + 1}
    for t, y in enumerate(Y, 1):
        X[t] = y

    def LXS(i, j):
        if base == 2:
            return max([2] + [1 + LXS(j, k) for k in range(j + 1, n + 1) if X[i] + X[k] > 2 * X[j]])
        return 1 + max([LXS(j, k) for k in range(j + 1, n + 1) if X[i] + X[k] > 2 * X[j]], default=0)

    return LXS(-1, 0) - 2


brute_cvx = lambda A: brute_longest(A, is_convex)
all_checks("7a P3: max(min(n,2), max_{i<j} LXS(i,j)) with base value 2 equals brute force", SMALL, LXS_main, brute_cvx)
all_checks("7a P3: sentinel version LXS(-1, 0) - 2 (after shifting) equals brute force", SMALL, LXS_sentinel, brute_cvx)
off = [A for A in SMALL if len(A) >= 2 and LXS_main(A, base=0) != brute_cvx(A) - 1]
check("7a P3: the official recurrence (1 + max, max of nothing = 0) is exactly one too small whenever n >= 2",
      not off, f"{len([A for A in SMALL if len(A) >= 2])} inputs")
check("7a P3: ... and its sentinel version LCS(-1,0) - 2 is one too small too",
      all(LXS_sentinel(A, base=0) == brute_cvx(A) - 1 for A in SMALL if len(A) >= 1))
check("7a P3: on the handout's array the official recurrence gives 5, the corrected one 6",
      LXS_main(PI, base=0) == 5 and LXS_main(PI) == 6)
ok = True
for n in range(2, 12):
    A = [2 ** k for k in range(1, n + 1)]
    check_all = is_convex(A)
    for j in range(2, n + 1):
        CALLS[0] = 0
        X = [None] + A

        def LXSc(i, jj):
            CALLS[0] += 1
            return max([2] + [1 + LXSc(jj, k) for k in range(jj + 1, n + 1) if X[i] + X[k] > 2 * X[jj]])

        LXSc(1, j)
        ok &= check_all and CALLS[0] == 2 ** (n - j)
check("7a P3 time: on A[k] = 2^k (every subsequence convex) LXS(i, j) makes exactly 2^(n-j) calls", ok)
worst_ok = True
for A in SMALL[:6000]:
    n = len(A)
    X = [None] + A
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            CALLS[0] = 0

            def LXSc2(i_, j_):
                CALLS[0] += 1
                return max([2] + [1 + LXSc2(j_, k) for k in range(j_ + 1, n + 1) if X[i_] + X[k] > 2 * X[j_]])

            LXSc2(i, j)
            worst_ok &= CALLS[0] <= 2 ** (n - j)
check("7a P3 time: LXS(i, j) never makes more than 2^(n-j) calls (6000 arrays, all pairs)", worst_ok)

print("\n== Lab 7a, Problem 4: longest palindrome subsequence")


def LPS_main(A, shortcut=False):
    """LPS(i, j): 0 if i > j; 1 if i = j; otherwise max of LPS(i+1, j), LPS(i, j-1) and, if A[i] = A[j],
    2 + LPS(i+1, j-1).  shortcut: if A[i] = A[j] return 2 + LPS(i+1, j-1) only."""
    n = len(A)
    X = [None] + A

    def LPS(i, j):
        CALLS[0] += 1
        if i > j:
            return 0
        if i == j:
            return 1
        if shortcut and X[i] == X[j]:
            return 2 + LPS(i + 1, j - 1)
        best = max(LPS(i + 1, j), LPS(i, j - 1))
        if X[i] == X[j]:
            best = max(best, 2 + LPS(i + 1, j - 1))
        return best

    return LPS(1, n)


brute_pal = lambda A: brute_longest(A, is_palindrome)
all_checks("7a P4: LPS(1, n) equals brute force", SMALL, LPS_main, brute_pal)
all_checks("7a P4: LPS(1, n) with the shortcut (equal ends => 2 + LPS(i+1, j-1)) equals brute force",
           SMALL, lambda A: LPS_main(A, True), brute_pal)


def lps_table(A):
    n = len(A)
    T = {}
    for i in range(n + 1, 0, -1):
        T[i, i - 1] = 0
        for j in range(i, n + 1):
            if i == j:
                T[i, j] = 1
            else:
                T[i, j] = max(T[i + 1, j], T[i, j - 1], (2 + T[i + 1, j - 1]) if A[i - 1] == A[j - 1] else 0)
    return T


ok = True
for A in SMALL[:8000]:
    T = lps_table(A)
    n = len(A)
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            ok &= T[i + 1, j] <= 2 + T[i + 1, j - 1] and T[i, j - 1] <= 2 + T[i + 1, j - 1]
check("7a P4 lemma: LPS(i+1, j) <= 2 + LPS(i+1, j-1) and LPS(i, j-1) <= 2 + LPS(i+1, j-1) (all intervals)", ok)
ok = True
for n in range(0, 15):
    CALLS[0] = 0
    LPS_main([7] * n)
    c_eq = CALLS[0]
    CALLS[0] = 0
    LPS_main(list(range(n)), True)
    c_dist = CALLS[0]
    ok &= c_eq <= 3 ** n and (n == 0 or c_dist == 2 ** n - 1)
check("7a P4 time: all-equal arrays use <= 3^n calls; with the shortcut, distinct arrays use exactly 2^n - 1", ok)
worst = True
for A in SMALL:
    n = len(A)
    CALLS[0] = 0
    LPS_main(A, True)
    worst &= CALLS[0] <= max(1, 2 ** n - 1)
    CALLS[0] = 0
    LPS_main(A)
    worst &= CALLS[0] <= 3 ** n
check("7a P4 time: plain recursion <= 3^n calls, with the shortcut <= 2^n - 1 calls (all test arrays)", worst)

print("\n== Lab 7a, Problem 5: shortest palindrome supersequence")


def SPS_main(A, shortcut=False):
    """SPS(i, j): 0 if i > j; 1 if i = j; otherwise 2 + min of SPS(i+1, j), SPS(i, j-1) and, if A[i] = A[j],
    SPS(i+1, j-1).  shortcut: if A[i] = A[j] return 2 + SPS(i+1, j-1) only."""
    n = len(A)
    X = [None] + A

    def SPS(i, j):
        CALLS[0] += 1
        if i > j:
            return 0
        if i == j:
            return 1
        if shortcut and X[i] == X[j]:
            return 2 + SPS(i + 1, j - 1)
        best = 2 + min(SPS(i + 1, j), SPS(i, j - 1))
        if X[i] == X[j]:
            best = min(best, 2 + SPS(i + 1, j - 1))
        return best

    return SPS(1, n)


all_checks("7a P5: SPS(1, n) equals brute force over all palindromes", TINY, SPS_main, brute_sps)
all_checks("7a P5: SPS(1, n) with the shortcut (equal ends => 2 + SPS(i+1, j-1)) equals brute force",
           TINY, lambda A: SPS_main(A, True), brute_sps)
all_checks("7a P5: SPS(1, n) = 2n - LPS(1, n)", SMALL, lambda A: SPS_main(A, True), lambda A: 2 * len(A) - LPS_main(A, True))
ok = True
for A in SMALL[:5000]:
    n = len(A)
    for i in range(1, n + 1):
        for j in range(i, n + 1):
            ok &= SPS_main(A[i - 1:j], True) == 2 * (j - i + 1) - LPS_main(A[i - 1:j], True)
check("7a P5: SPS(i, j) = 2(j - i + 1) - LPS(i, j) for every interval (5000 arrays)", ok)

# ================================================================== the handout's examples
print("\n== The handout's examples (array 3,1,4,1,5,9,2,6,5,3,5,8,9,7,9,3,2,3,8,4,6,2,7)")


def all_valid(A, ok_next):
    """Enumerate every index sequence i1 < i2 < ... whose values pass ok_next(prefix values, next value) — an
    exhaustive search over the subsequences that can still be valid; returns the longest length."""
    n = len(A)
    best = [0]

    def go(last, vals):
        best[0] = max(best[0], len(vals))
        for k in range(last + 1, n):
            if ok_next(vals, A[k]):
                vals.append(A[k])
                go(k, vals)
                vals.pop()

    go(-1, [])
    return best[0]


dec_ok = lambda v, x: not v or x < v[-1]
alt_ok = lambda v, x: is_alternating(v + [x])
cvx_ok = lambda v, x: len(v) < 2 or x - v[-1] > v[-1] - v[-2]
check("P1 example: exhaustive search over decreasing subsequences gives 5", all_valid(PI, dec_ok) == 5)
check("P1 example: LDSsmaller(0,1) = LDSfirst(0) - 1 = LIS(-A) = 5",
      LDS_main(PI) == LDS_first(PI) == LIS_bigger([-x for x in PI]) == 5)
w = [9, 6, 5, 4, 2]
check("P1 witness 9,6,5,4,2 is a decreasing subsequence of length 5", is_subseq(w, PI) and is_decreasing(w) and len(w) == 5)
check("P2 example: exhaustive search over alternating subsequences gives 17", all_valid(PI, alt_ok) == 17)
check("P2 example: LASabove(0,1) = max_i Down(i) = 17", LAS_main(PI) == LAS_first(PI) == 17)
w = [3, 1, 4, 1, 5, 2, 6, 5, 8, 7, 9, 3, 8, 4, 6, 2, 7]
check("P2 witness 3,1,4,1,5,2,6,5,8,7,9,3,8,4,6,2,7 is an alternating subsequence of length 17",
      is_subseq(w, PI) and is_alternating(w) and len(w) == 17)
check("P3 example: exhaustive search over convex subsequences gives 6", all_valid(PI, cvx_ok) == 6)
check("P3 example: corrected LXS gives 6 (both versions)", LXS_main(PI) == LXS_sentinel(PI) == 6)
w = [3, 1, 1, 2, 5, 9]
check("P3 witness 3,1,1,2,5,9 is a convex subsequence of length 6 (steps -2, 0, 1, 3, 4)",
      is_subseq(w, PI) and is_convex(w) and [b - a for a, b in zip(w, w[1:])] == [-2, 0, 1, 3, 4])


def lcs(X, Y):
    m, n = len(X), len(Y)
    T = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m - 1, -1, -1):
        for j in range(n - 1, -1, -1):
            T[i][j] = 1 + T[i + 1][j + 1] if X[i] == Y[j] else max(T[i + 1][j], T[i][j + 1])
    return T[0][0]


def all_pal_lengths(A):
    """Exhaustive: every palindromic index subsequence, built by choosing its outermost pair of indices."""
    n = len(A)
    lens = set([0])

    def go(lo, hi, outer):
        lens.add(outer)
        for i in range(lo, hi + 1):
            lens.add(outer + 1)                 # A[i] as the middle element
            for j in range(i + 1, hi + 1):
                if A[i] == A[j]:
                    go(i + 1, j - 1, outer + 2)

    go(0, n - 1, 0)
    return max(lens)


check("P4 example: LPS(1, n) = 9, not the handout's 7 (with and without the shortcut)",
      LPS_main(PI) == LPS_main(PI, True) == 9)
check("P4 example: exhaustive search over palindromic subsequences gives 9; LCS(A, reverse A) = 9",
      all_pal_lengths(PI) == 9 and lcs(PI, PI[::-1]) == 9)
w = [4, 9, 5, 3, 5, 9, 4]
check("P4 handout's witness 4,9,5,3,5,9,4 is a palindromic subsequence, but of length 7 only",
      is_subseq(w, PI) and is_palindrome(w) and len(w) == 7)
for w in ([2, 6, 8, 9, 7, 9, 8, 6, 2], [3, 2, 3, 9, 7, 9, 3, 2, 3]):
    check(f"P4 witness {','.join(map(str, w))} is a palindromic subsequence of length 9",
          is_subseq(w, PI) and is_palindrome(w) and len(w) == 9)
pos = [7, 8, 12, 13, 14, 15, 19, 21, 22]
check("P4 witness 2,6,8,9,7,9,8,6,2 sits at positions 7, 8, 12, 13, 14, 15, 19, 21, 22",
      [PI[p - 1] for p in pos] == [2, 6, 8, 9, 7, 9, 8, 6, 2] and pos == sorted(set(pos)))
check("P5 example: SPS(1, 10) = 15 for 3,1,4,1,5,9,2,6,5,3 (with and without the shortcut)",
      SPS_main(PI10) == SPS_main(PI10, True) == 15)
alph = sorted(set(PI10)) + [0]
none14 = not any(is_subseq(PI10, list(h) + list(h)[::-1]) for h in itertools.product(alph, repeat=7))
check("P5 example: no palindrome of length 14 over the array's symbols plus a fresh one contains it "
      "(so none of length <= 14: a palindrome can always be lengthened by one at its center)", none14)
w = [3, 5, 6, 2, 9, 5, 1, 4, 1, 5, 9, 2, 6, 5, 3]
check("P5 witness 3,5,6,2,9,5,1,4,1,5,9,2,6,5,3 is a palindrome of length 15 containing the array",
      is_palindrome(w) and is_subseq(PI10, w) and len(w) == 15)
check("P5 example: 15 = 2*10 - LPS, with LPS(3,1,4,1,5,9,2,6,5,3) = 5", LPS_main(PI10) == 5 and 2 * 10 - 5 == 15)

# ================================================================== LAB 7b: the dynamic programs
print("\n== Lab 7b, Problem 1: FastLDS (2D table) and FastLDS2 (1D table)")
OPS = [0]


def FastLDS(A):
    """LDSsmaller[0..n, 1..n+1]; outer loop j from n+1 down to 1 (base column first), inner loop i from 0 to j-1."""
    n = len(A)
    X = [INF] + A
    T = Memo()
    for i in range(0, n + 1):
        T[i, n + 1] = 0
    for j in range(n, 0, -1):
        for i in range(0, j):
            OPS[0] += 1
            if X[j] >= X[i]:
                T[i, j] = T[i, j + 1]
            else:
                T[i, j] = max(T[i, j + 1], 1 + T[j, j + 1])
    return T[0, 1]


def FastLDS_down(A):
    """Same table, inner loop i from j-1 down to 0 (the official order)."""
    n = len(A)
    X = [INF] + A
    T = Memo()
    for i in range(0, n + 1):
        T[i, n + 1] = 0
    for j in range(n, 0, -1):
        for i in range(j - 1, -1, -1):
            T[i, j] = T[i, j + 1] if X[j] >= X[i] else max(T[i, j + 1], 1 + T[j, j + 1])
    return T[0, 1]


def FastLDS2(A):
    """LDSfirst[0..n], i from n down to 0; returns LDSfirst[0] - 1."""
    n = len(A)
    X = [INF] + A
    T = Memo()
    for i in range(n, -1, -1):
        OPS[0] += 1
        T[i] = 1
        for j in range(i + 1, n + 1):
            OPS[0] += 1
            if X[j] < X[i] and 1 + T[j] > T[i]:
                T[i] = 1 + T[j]
    return T[0] - 1


all_checks("7b P1: FastLDS (columns right to left, i = 0..j-1) equals brute force", SMALL, FastLDS, brute_dec)
all_checks("7b P1: FastLDS with i from j-1 down to 0 (official order) equals brute force", SMALL, FastLDS_down, brute_dec)
all_checks("7b P1: FastLDS2 (LDSfirst, i from n down to 0) equals brute force", SMALL, FastLDS2, brute_dec)
check("7b P1: both give 5 on the handout's array", FastLDS(PI) == FastLDS2(PI) == 5)


def ratios(f, sizes, power):
    out = []
    for n in sizes:
        A = [random.randint(1, 3 * n) for _ in range(n)]
        OPS[0] = 0
        f(A)
        out.append(OPS[0] / n ** power)
    return out


r = ratios(FastLDS, [50, 100, 200, 400], 2)
check("7b P1 time: FastLDS does n(n+1)/2 entry computations: ops/n^2 -> 1/2", abs(r[-1] - 0.5) < 0.01, [round(x, 4) for x in r])
r = ratios(FastLDS2, [50, 100, 200, 400], 2)
check("7b P1 time: FastLDS2 does Theta(n^2) loop steps: ops/n^2 -> 1/2", abs(r[-1] - 0.5) < 0.01, [round(x, 4) for x in r])

print("\n== Lab 7b, Problem 2: FastLAS (two 2D tables), the official answer formula, GreedyLAS")


def FastLAS(A, official_answer=False):
    """LASabove[0..n, 1..n+1], LASbelow[0..n, 1..n+1], filled together: j from n+1 down to 1, i from 0 to j-1."""
    n = len(A)
    X = [-INF] + A
    U, D = Memo(), Memo()
    for i in range(0, n + 1):
        U[i, n + 1] = 0
        D[i, n + 1] = 0
    for j in range(n, 0, -1):
        for i in range(0, j):
            OPS[0] += 1
            U[i, j] = U[i, j + 1]
            if X[j] > X[i]:
                U[i, j] = max(U[i, j], 1 + D[j, j + 1])
            D[i, j] = D[i, j + 1]
            if X[j] < X[i]:
                D[i, j] = max(D[i, j], 1 + U[j, j + 1])
    if official_answer:      # official: max_j max{1 + LAS+(j, j+1), 1 + LAS-(j, j+1)}
        return max([max(1 + U[j, j + 1], 1 + D[j, j + 1]) for j in range(1, n + 1)], default=0)
    return U[0, 1]


all_checks("7b P2: FastLAS returning LASabove[0, 1] equals brute force", SMALL, FastLAS, brute_alt)


def FastLAS_start_below(A):
    """max_j (1 + LASbelow(j, j+1)): the alternating subsequence that starts at A[j]."""
    n = len(A)
    X = [-INF] + A
    U, D = Memo(), Memo()
    for i in range(0, n + 1):
        U[i, n + 1] = 0
        D[i, n + 1] = 0
    for j in range(n, 0, -1):
        for i in range(0, j):
            U[i, j] = max(U[i, j + 1], 1 + D[j, j + 1]) if X[j] > X[i] else U[i, j + 1]
            D[i, j] = max(D[i, j + 1], 1 + U[j, j + 1]) if X[j] < X[i] else D[i, j + 1]
    return max([1 + D[j, j + 1] for j in range(1, n + 1)], default=0)


all_checks("7b P2: max_j (1 + LASbelow[j, j+1]) equals brute force", SMALL, FastLAS_start_below, brute_alt)
brute_zig = lambda A: brute_longest(A, is_zigzag)
check("7b P2: the official answer formula returns 2 on A = [1, 2], where the answer is 1",
      FastLAS([1, 2], official_answer=True) == 2 and brute_alt([1, 2]) == 1)
bad = [A for A in SMALL if FastLAS(A, official_answer=True) != brute_alt(A)]
check("7b P2: the official formula computes the longest zigzag (either first direction) instead",
      all(FastLAS(A, official_answer=True) == brute_zig(A) for A in SMALL), f"wrong on {len(bad)} of {len(SMALL)} inputs")
check("7b P2: ... which exceeds the answer by at most 1",
      all(brute_alt(A) <= brute_zig(A) <= brute_alt(A) + 1 for A in SMALL))
r = ratios(FastLAS, [50, 100, 200, 400], 2)
check("7b P2 time: n(n+1)/2 pairs of entries: ops/n^2 -> 1/2", abs(r[-1] - 0.5) < 0.01, [round(x, 4) for x in r])


def GreedyLAS(A):
    """Ours: B[0] = -inf, B[1..m] = A without repeated neighbors; return 1 + #{1 <= i <= m-1: B[i] strict local
    extremum of B[0..m]} (0 if n = 0)."""
    n = len(A)
    if n == 0:
        return 0
    B = [-INF, A[0]]
    m = 1
    for i in range(1, n):
        OPS[0] += 1
        if A[i] != B[m]:
            m += 1
            B.append(A[i])
    ell = 1
    for i in range(1, m):
        OPS[0] += 1
        if B[i] > max(B[i - 1], B[i + 1]) or B[i] < min(B[i - 1], B[i + 1]):
            ell += 1
    return ell


def GreedyLAS_official(A):
    """The official GreedyLAS: collapse runs, l <- 2, count interior local extrema of B[1..m]."""
    B = [A[0]]
    for x in A[1:]:
        if x != B[-1]:
            B.append(x)
    m = len(B)
    ell = 2
    for i in range(1, m - 1):
        if B[i] < min(B[i - 1], B[i + 1]) or B[i] > max(B[i - 1], B[i + 1]):
            ell += 1
    return ell


all_checks("7b P2: GreedyLAS (with the sentinel -inf) equals brute force", SMALL, GreedyLAS, brute_alt)
check("7b P2: GreedyLAS gives 17 on the handout's array", GreedyLAS(PI) == 17)
check("7b P2: the official GreedyLAS returns 2 on [5], [5, 5, 5] and [1, 2] (answers 1, 1, 1)",
      [GreedyLAS_official(A) for A in ([5], [5, 5, 5], [1, 2])] == [2, 2, 2]
      and [brute_alt(A) for A in ([5], [5, 5, 5], [1, 2])] == [1, 1, 1])
check("7b P2: the official GreedyLAS equals the longest zigzag whenever A has two distinct values",
      all(GreedyLAS_official(A) == brute_zig(A) for A in SMALL if len(set(A)) >= 2))


def turning_points(C):
    m = len(C) - 1
    return [0] + [i for i in range(1, m) if C[i] > max(C[i - 1], C[i + 1]) or C[i] < min(C[i - 1], C[i + 1])] + [m]


ok = True
cnt = 0
for A in SMALL:
    C = [A[0]] + [A[i] for i in range(1, len(A)) if A[i] != A[i - 1]] if A else []
    if len(C) >= 2:
        cnt += 1
        tp = turning_points(C)
        ok &= brute_zig(C) == len(tp) and is_zigzag([C[p] for p in tp])
check("7b P2 lemma: with no equal neighbors, the longest zigzag subsequence = number of turning points, "
      "and the turning points themselves form one", ok, f"{cnt} sequences")
ok = all(brute_alt(A) == brute_alt([A[0]] + [A[i] for i in range(1, len(A)) if A[i] != A[i - 1]]) for A in SMALL if A)
check("7b P2 step 1: deleting repeated neighbors does not change the answer", ok)
ok = all(brute_alt(A) == brute_zig([-100] + A) - 1 for A in SMALL)
check("7b P2 step 2: longest alternating subsequence of A = longest zigzag of (-inf, A) minus 1", ok)


def zig_injection_ok(C, S):
    """The proof's injection for one zigzag S (index list) of C: interior elements -> distinct interior turning points."""
    imgs = []
    for r in range(1, len(S) - 1):
        lo, hi = S[r - 1], S[r + 1]
        window = range(lo, hi + 1)
        if C[S[r]] > C[S[r - 1]]:      # peak of S
            p = max(window, key=lambda t: C[t])
            if not (lo < p < hi and C[p] > C[p - 1] and C[p] > C[p + 1]):
                return False
        else:
            p = min(window, key=lambda t: C[t])
            if not (lo < p < hi and C[p] < C[p - 1] and C[p] < C[p + 1]):
                return False
        imgs.append(p)
    return len(set(imgs)) == len(imgs)


ok = True
cnt = 0
for A in list(int_arrays(6, range(1, 5))) + list(perms(6)):
    C = [A[0]] + [A[i] for i in range(1, len(A)) if A[i] != A[i - 1]] if A else []
    for r in range(3, len(C) + 1):
        for S in itertools.combinations(range(len(C)), r):
            if is_zigzag([C[t] for t in S]):
                cnt += 1
                ok &= zig_injection_ok(C, list(S))
check("7b P2 proof: window maxima/minima give distinct interior turning points for every zigzag", ok, f"{cnt} zigzags")
r = ratios(GreedyLAS, [1000, 2000, 4000, 8000], 1)
check("7b P2 time: GreedyLAS does at most 2n loop steps (O(n))", all(x <= 2 for x in r), [round(x, 3) for x in r])

print("\n== Lab 7b, Problem 3: FastLXS")


def FastLXS(A, init=2):
    """LXS[1..n, 1..n] (i < j); i from n-1 down to 1 (outer), j from i+1 to n, k from j+1 to n; best = min(n, 2) first.
    init=1 reproduces the official pseudocode (LCS[i, j] <- 1)."""
    n = len(A)
    X = [None] + A
    T = Memo()
    best = min(n, 2) if init == 2 else 0
    for i in range(n - 1, 0, -1):
        for j in range(i + 1, n + 1):
            T[i, j] = init
            for k in range(j + 1, n + 1):
                OPS[0] += 1
                if X[i] + X[k] > 2 * X[j]:
                    T[i, j] = max(T[i, j], 1 + T[j, k])
            best = max(best, T[i, j])
    return best


all_checks("7b P3: FastLXS (rows bottom to top) equals brute force", SMALL, FastLXS, brute_cvx)
check("7b P3: FastLXS gives 6 on the handout's array; the official pseudocode (initial value 1) gives 5",
      FastLXS(PI) == 6 and FastLXS(PI, init=1) == 5)
check("7b P3: the official pseudocode is one too small whenever n >= 2",
      all(FastLXS(A, init=1) == brute_cvx(A) - 1 for A in SMALL if len(A) >= 2))
r = ratios(FastLXS, [40, 80, 160, 320], 3)
check("7b P3 time: the k-loop runs C(n,3) times in total: ops/n^3 -> 1/6", abs(r[-1] - 1 / 6) < 0.01, [round(x, 4) for x in r])

print("\n== Lab 7b, Problems 4 and 5: FastLPS and FastSPS")


def FastLPS(A):
    """LPS[1..n+1, 0..n]; i from n+1 down to 1 (outer): LPS[i, i-1] = 0, then j from i up to n (inner)."""
    n = len(A)
    X = [None] + A
    T = Memo()
    for i in range(n + 1, 0, -1):
        T[i, i - 1] = 0
        for j in range(i, n + 1):
            OPS[0] += 1
            if i == j:
                T[i, j] = 1
            else:
                T[i, j] = max(T[i + 1, j], T[i, j - 1])
                if X[i] == X[j]:
                    T[i, j] = max(T[i, j], 2 + T[i + 1, j - 1])
    return T[1, n], T


def FastSPS(A):
    n = len(A)
    X = [None] + A
    T = Memo()
    for i in range(n + 1, 0, -1):
        T[i, i - 1] = 0
        for j in range(i, n + 1):
            OPS[0] += 1
            if i == j:
                T[i, j] = 1
            else:
                T[i, j] = 2 + min(T[i + 1, j], T[i, j - 1])
                if X[i] == X[j]:
                    T[i, j] = min(T[i, j], 2 + T[i + 1, j - 1])
    return T[1, n], T


all_checks("7b P4: FastLPS (i from n+1 down to 1, j from i up to n) equals brute force", SMALL, lambda A: FastLPS(A)[0], brute_pal)
all_checks("7b P5: FastSPS (same order) equals brute force", TINY, lambda A: FastSPS(A)[0], brute_sps)
all_checks("7b P5: FastSPS = 2n - FastLPS on all test arrays", SMALL, lambda A: FastSPS(A)[0], lambda A: 2 * len(A) - FastLPS(A)[0])
check("7b P4, P5: 9 on the handout's array, 15 on its first ten elements", FastLPS(PI)[0] == 9 and FastSPS(PI10)[0] == 15)
r = ratios(lambda A: FastLPS(A), [50, 100, 200, 400], 2)
check("7b P4 time: n(n+1)/2 entries with i <= j: ops/n^2 -> 1/2", abs(r[-1] - 0.5) < 0.01, [round(x, 4) for x in r])

# the small table on the Lab 7b page: A = 3, 1, 4, 1, 5
EX5 = [3, 1, 4, 1, 5]
_, TL = FastLPS(EX5)
_, TS = FastSPS(EX5)
LPS_ROWS = {1: [1, 1, 1, 3, 3], 2: [1, 1, 3, 3], 3: [1, 1, 1], 4: [1, 1], 5: [1]}
SPS_ROWS = {1: [1, 3, 5, 5, 7], 2: [1, 3, 3, 5], 3: [1, 3, 5], 4: [1, 3], 5: [1]}
print("    LPS table for 3,1,4,1,5:", {i: [TL[i, j] for j in range(i, 6)] for i in range(1, 6)})
print("    SPS table for 3,1,4,1,5:", {i: [TS[i, j] for j in range(i, 6)] for i in range(1, 6)})
check("7b table: LPS(i, j) for A = 3,1,4,1,5 as printed on the page",
      all([TL[i, j] for j in range(i, 6)] == LPS_ROWS[i] for i in range(1, 6)))
check("7b table: SPS(i, j) for A = 3,1,4,1,5 as printed on the page",
      all([TS[i, j] for j in range(i, 6)] == SPS_ROWS[i] for i in range(1, 6)))
check("7b table: 1,4,1 is a longest palindrome subsequence (3) and 3,5,1,4,1,5,3 a shortest supersequence (7)",
      is_subseq([1, 4, 1], EX5) and is_subseq(EX5, [3, 5, 1, 4, 1, 5, 3]) and is_palindrome([3, 5, 1, 4, 1, 5, 3])
      and brute_pal(EX5) == 3 and brute_sps(EX5) == 7)

print("\n== Figures (tools/figs_labs.py, Lab 7 section) and the handout's witness in the SPS example")
import os
import re
FIGS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figs")
C = [-INF] + PI
turn = [k for k in range(1, len(PI)) if C[k] > max(C[k - 1], C[k + 1]) or C[k] < min(C[k - 1], C[k + 1])] + [len(PI)]
tvals = [PI[k - 1] for k in turn]
check("zigzag figure: the example has no equal neighbors and 17 turning points after the sentinel",
      all(PI[i] != PI[i + 1] for i in range(len(PI) - 1)) and len(turn) == 17 and GreedyLAS(PI) == 17)
check("zigzag figure: the turning points are 3,1,4,1,9,2,6,3,9,7,9,2,8,4,6,2,7 and form an alternating subsequence",
      tvals == [3, 1, 4, 1, 9, 2, 6, 3, 9, 7, 9, 2, 8, 4, 6, 2, 7] and is_alternating(tvals))
check("zigzag figure: the hollow (non-turning) points are positions 5, 9, 11, 12, 16, 18",
      sorted(set(range(1, 24)) - set(turn)) == [5, 9, 11, 12, 16, 18])
html = open(os.path.join(FIGS, "lab-07b-zigzag.html"), encoding="utf-8").read()
cap = re.search(r"<figcaption>(.*)</figcaption>", html).group(1)
check("zigzag figure: caption lists exactly that sequence and the length 17",
      "3, 1, 4, 1, 9, 2, 6, 3, 9, 7, 9, 2, 8, 4, 6, 2, 7" in cap and "length 17" in cap)
filled = len(re.findall(r'<circle[^>]*fill="var\(--accent\)"', html))
check("zigzag figure: 17 filled points drawn", filled == 17, filled)
check("dependencies figure exists", os.path.exists(os.path.join(FIGS, "lab-07b-dependencies.html")))
P15 = [3, 5, 6, 2, 9, 5, 1, 4, 1, 5, 9, 2, 6, 5, 3]
emb, it = [], 0
for x in PI10:                      # leftmost embedding of the array in the handout's palindrome
    while P15[it] != x:
        it += 1
    emb.append(it + 1)
    it += 1
U = set(emb)
paired = sorted(p for p in U if 16 - p in U)
check("SPS example: in the handout's palindrome the array sits at 1,7,...,15; the self-paired elements are 3,1,4,1,3",
      emb == [1, 7, 8, 9, 10, 11, 12, 13, 14, 15] and [P15[p - 1] for p in paired] == [3, 1, 4, 1, 3]
      and is_subseq([3, 1, 4, 1, 3], PI10) and [P15[p - 1] for p in sorted(U - set(paired))] == [5, 9, 2, 6, 5])

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: {FAIL}")
