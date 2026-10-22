#!/usr/bin/env python3
"""Checks for content/3-homework-and-exams/lab-06a.md and lab-06b.md (Lab 6: binary search and Karatsuba).

Lab 6a: every algorithm is implemented exactly as the page states it (1-indexed arrays, index 0 unused) and
compared with brute force on all small inputs and many random ones; the handout's examples and the page's traces are
reproduced; comparison counts are counted and checked against the stated exact bounds.

Lab 6b: decimal numbers are digit arrays (little-endian lists of digits 0..9) and every single-digit addition,
subtraction and multiplication is counted. Karatsuba is the site's FastMultiply (a - b variant, signs split off).
The conversion algorithms are run digit by digit and compared with Python's own conversion. For large n the same
algorithms run on Python integers ("fast mode") and are charged exactly the digit operations the digit-array version
performs (the two counts are checked equal on all n up to a few hundred bits); then the counts on growing n are
compared with n^lg3, n^lg3 log n, n log n, n log^2 n. Problem 4 charges an O(n log n) multiplication L*ceil(lg L)."""
import itertools
import math
import random
import sys
from fractions import Fraction

sys.setrecursionlimit(100000)
if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)

FAIL = []


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAIL.append(name)


rng = random.Random(3746)
INF = float("inf")
LG3 = math.log2(3)


def clg(x):
    """ceil(lg x) for an integer x >= 1"""
    return (x - 1).bit_length()


def flg(x):
    """floor(lg x) for an integer x >= 1"""
    return x.bit_length() - 1


def one(lst):
    """1-indexed copy: index 0 unused"""
    return [None] + list(lst)


def sorted_distinct_arrays(lo, hi, maxlen):
    for n in range(1, maxlen + 1):
        for c in itertools.combinations(range(lo, hi + 1), n):
            yield list(c)


print("=" * 30, "Lab 6a", "=" * 30)

# ----------------------------------------------------------------------------------------- Problem 1
# FindMatch(A, lo, hi): an index i in [lo, hi] with A[i] = i, or None.


def find_match(A, lo, hi, cnt):
    if lo > hi:
        return None
    mid = (lo + hi) // 2
    cnt[0] += 1
    if A[mid] == mid:
        return mid
    elif A[mid] < mid:
        return find_match(A, mid + 1, hi, cnt)
    else:
        return find_match(A, lo, mid - 1, cnt)


def find_match_loop(A, n):
    lo, hi = 1, n
    while lo <= hi:
        mid = (lo + hi) // 2
        if A[mid] == mid:
            return mid
        elif A[mid] < mid:
            lo = mid + 1
        else:
            hi = mid - 1
    return None


def find_match_pos(A):
    return 1 if A[1] == 1 else None


ok_rec = ok_loop = ok_delta = ok_probe = True
ok_pos = True
npos = total = 0
for arr in sorted_distinct_arrays(-4, 10, 8):
    n = len(arr)
    A = one(arr)
    matches = [i for i in range(1, n + 1) if A[i] == i]
    cnt = [0]
    r = find_match(A, 1, n, cnt)
    ok_rec &= (r is None and not matches) or (r in matches)
    ok_probe &= cnt[0] <= flg(n) + 1
    r2 = find_match_loop(A, n)
    ok_loop &= (r2 is None and not matches) or (r2 in matches)
    d = [A[i] - i for i in range(1, n + 1)]
    ok_delta &= all(d[i] <= d[i + 1] for i in range(n - 1))
    total += 1
    if A[1] > 0:
        npos += 1
        r3 = find_match_pos(A)
        ok_pos &= (r3 is None and not matches) or (r3 in matches)
check(f"6a.1 Delta[i] = A[i] - i is nondecreasing for all {total} sorted arrays of distinct integers in [-4,10], n <= 8",
      ok_delta)
check("6a.1(a) FindMatch (recursive) agrees with brute force on all of them", ok_rec)
check("6a.1(a) FindMatch (loop version) agrees with brute force on all of them", ok_loop)
check("6a.1(a) at most floor(lg n) + 1 probes", ok_probe)
check(f"6a.1(b) FindMatchPos (A[1] = 1 or nothing) agrees with brute force on all {npos} arrays with A[1] > 0", ok_pos)

ok = ok_p = True
worst = {}
for _ in range(3000):
    n = rng.randint(1, 3000)
    vals = sorted(rng.sample(range(-n, 2 * n), n))
    if rng.random() < 0.5:   # plant a match sometimes
        i = rng.randint(1, n)
        shift = i - vals[i - 1]
        vals = [v + shift for v in vals]
    A = one(vals)
    matches = {i for i in range(1, n + 1) if A[i] == i}
    cnt = [0]
    r = find_match(A, 1, n, cnt)
    ok &= (r is None and not matches) or (r in matches)
    ok_p &= cnt[0] <= flg(n) + 1
check("6a.1(a) FindMatch correct on 3000 random arrays up to n = 3000 (half with a planted match)", ok)
check("6a.1(a) probes <= floor(lg n) + 1 on them", ok_p)
# the bound is attained: no match, every probe goes right
okt = True
for n in range(1, 200):
    A = one([-5 * n + i for i in range(1, n + 1)])   # A[i] < i everywhere
    cnt = [0]
    okt &= find_match(A, 1, n, cnt) is None and cnt[0] == flg(n) + 1
check("6a.1(a) the bound floor(lg n) + 1 is attained (A[i] < i everywhere, n < 200)", okt)

# traps: integers and distinctness are both needed
A = one([1.5, 2])
check("6a.1 trap: A = [1.5, 2] (not integers): Delta = [0.5, 0] is not sorted and FindMatch misses A[2] = 2",
      find_match(A, 1, 2, [0]) is None and A[2] == 2)
A = one([1, 1, 1])
check("6a.1 trap: A = [1, 1, 1] (not distinct): FindMatch misses A[1] = 1",
      find_match(A, 1, 3, [0]) is None and A[1] == 1)

# ----------------------------------------------------------------------------------------- Problem 2


def is_local_min(A, n, x):
    return 2 <= x <= n - 1 and A[x - 1] >= A[x] <= A[x + 1]


def local_min(A, lo, hi, cnt):
    """assumes hi - lo >= 2, A[lo] >= A[lo+1], A[hi-1] <= A[hi]"""
    if hi - lo == 2:
        return lo + 1
    mid = (lo + hi) // 2
    cnt[0] += 1
    if A[mid] < A[mid + 1]:
        return local_min(A, lo, mid + 1, cnt)
    else:
        return local_min(A, mid, hi, cnt)


def local_min_official(A, lo, hi, c, interior):
    """the official version: brute force when hi - lo < c; interior=False takes the first minimum of A[lo..hi]"""
    if hi - lo < c:
        rng_ = range(lo + 1, hi) if interior else range(lo, hi + 1)
        return min(rng_, key=lambda i: (A[i], i))
    mid = (lo + hi) // 2
    if A[mid] < A[mid + 1]:
        return local_min_official(A, lo, mid + 1, c, interior)
    else:
        return local_min_official(A, mid, hi, c, interior)


ex = [9, 7, 7, 2, 1, 3, 7, 5, 4, 7, 3, 3, 4, 8, 6, 9]
A = one(ex)
n = len(ex)
mins = [x for x in range(1, n + 1) if is_local_min(A, n, x)]
check("6a.2 handout array: boundary conditions hold and there are exactly six local minima, at 2, 5, 9, 11, 12, 15",
      A[1] >= A[2] and A[n - 1] <= A[n] and mins == [2, 5, 9, 11, 12, 15], str(mins))
check("6a.2 handout array: A[9] = 4 is a local minimum (the handout's example answer 9)", is_local_min(A, n, 9))
# the trace on the page
trace = []


def local_min_trace(A, lo, hi):
    if hi - lo == 2:
        trace.append((lo, hi, None))
        return lo + 1
    mid = (lo + hi) // 2
    trace.append((lo, hi, mid))
    if A[mid] < A[mid + 1]:
        return local_min_trace(A, lo, mid + 1)
    return local_min_trace(A, mid, hi)


r = local_min_trace(A, 1, 16)
check("6a.2 trace: [1,16] mid 8 (5 >= 4) -> [8,16] mid 12 (3 < 4) -> [8,13] mid 10 (7 >= 3) -> [10,13] mid 11 "
      "(3 >= 3) -> [11,13] -> returns 12", r == 12 and trace == [(1, 16, 8), (8, 16, 12), (8, 13, 10), (10, 13, 11),
                                                                 (11, 13, None)], str(trace))
check("6a.2 trace values: A[8]=5, A[9]=4, A[12]=3, A[13]=4, A[10]=7, A[11]=3, A[12]=3",
      (A[8], A[9], A[12], A[13], A[10], A[11]) == (5, 4, 3, 4, 7, 3))
check("6a.2 trace: 4 comparisons = ceil(lg(16 - 2))", clg(14) == 4)

ok = okc = okmax = ok_exist = True
count_inputs = 0
for n in range(3, 11):
    worst = 0
    for t in itertools.product((1, 2, 3), repeat=n):
        if not (t[0] >= t[1] and t[n - 2] <= t[n - 1]):
            continue
        count_inputs += 1
        A = one(t)
        cnt = [0]
        x = local_min(A, 1, n, cnt)
        ok &= is_local_min(A, n, x)
        okc &= cnt[0] <= clg(n - 2)
        worst = max(worst, cnt[0])
        # existence: the minimum of A[2..n-1] is a local minimum
        y = min(range(2, n), key=lambda i: A[i])
        ok_exist &= is_local_min(A, n, y)
    okmax &= worst == clg(n - 2)
check(f"6a.2 LocalMin returns a local minimum on all {count_inputs} arrays over {{1,2,3}} with n = 3..10 and the "
      "boundary conditions", ok)
check("6a.2 hint: the minimum of A[2..n-1] is always a local minimum (same inputs)", ok_exist)
check("6a.2 LocalMin makes at most ceil(lg(n - 2)) comparisons, and the maximum is attained for each n = 3..10",
      okc and okmax)
ok = okc = True
for _ in range(3000):
    n = rng.randint(3, 5000)
    t = [rng.randint(0, 6) for _ in range(n)]
    t[0] = max(t[0], t[1])
    t[n - 1] = max(t[n - 1], t[n - 2])
    A = one(t)
    cnt = [0]
    x = local_min(A, 1, n, cnt)
    ok &= is_local_min(A, n, x)
    okc &= cnt[0] <= clg(n - 2)
check("6a.2 LocalMin correct on 3000 random arrays with ties, n up to 5000, within ceil(lg(n-2)) comparisons", ok and okc)
# the interior count m = hi - lo - 1 goes to ceil(m/2) (left) or floor(m/2) (right)
ok = True
for lo in range(1, 20):
    for hi in range(lo + 3, lo + 60):
        m = hi - lo - 1
        mid = (lo + hi) // 2
        ok &= (mid + 1) - lo - 1 == (m + 1) // 2 and hi - mid - 1 == m // 2 and lo < mid and mid + 1 < hi
check("6a.2 the number of interior positions hi - lo - 1 = m becomes ceil(m/2) (left) or floor(m/2) (right)", ok)

# the official base case
A = one([1, 1, 2])
check("6a.2 official base case 'minimum of A[lo..hi]' can return index 1 on [1, 1, 2], which is not a local minimum",
      local_min_official(A, 1, 3, 100, False) == 1 and not is_local_min(A, 3, 1))
bad = 0
ok = True
for _ in range(3000):
    n = rng.randint(3, 400)
    t = [rng.randint(0, 3) for _ in range(n)]
    t[0] = max(t[0], t[1])
    t[n - 1] = max(t[n - 1], t[n - 2])
    A = one(t)
    for c in (3, 4, 7, 100):
        ok &= is_local_min(A, n, local_min_official(A, 1, n, c, True))
    bad += not is_local_min(A, n, local_min_official(A, 1, n, 10, False))
check("6a.2 official algorithm with the base case fixed (minimum of the interior A[lo+1..hi-1]) is correct, "
      "thresholds 3, 4, 7, 100", ok)
check("6a.2 with the unfixed base case it fails on some random inputs with ties", bad > 0, f"{bad} of 3000")

# ----------------------------------------------------------------------------------------- Problem 3


def median(A, B, cnt=None, log=None):
    """A, B: sorted Python lists of the same length n >= 1 (0-indexed storage of A[1..n], B[1..n])."""
    n = len(A)
    if cnt is not None:
        cnt[0] += 1
    if n == 1:
        if log is not None:
            log.append((1, None, A[0], B[0]))
        return min(A[0], B[0])
    m = (n + 1) // 2
    if log is not None:
        log.append((n, m, A[m - 1], B[m - 1]))
    if A[m - 1] > B[m - 1]:
        return median(A[:m], B[n - m:], cnt, log)
    else:
        return median(A[n - m:], B[:m], cnt, log)


def nth_smallest(A, B, k):
    return sorted(A + B)[k - 1]


def interleavings(m, n):
    """all ways to split the values 1..m+n into sorted A (m values) and sorted B (n values)"""
    for c in itertools.combinations(range(1, m + n + 1), m):
        s = set(c)
        yield list(c), [v for v in range(1, m + n + 1) if v not in s]


ok = okc = okdisc = True
cases = 0
for n in range(1, 9):
    for A, B in interleavings(n, n):
        cases += 1
        cnt = [0]
        med = nth_smallest(A, B, n)
        ok &= median(A, B, cnt) == med
        okc &= cnt[0] == clg(n) + 1
        if n >= 2:   # the discard claim, strictly
            m = (n + 1) // 2
            if A[m - 1] > B[m - 1]:
                okdisc &= all(a > med for a in A[m:]) and all(b < med for b in B[:n - m])
                okdisc &= sum(1 for v in A + B if v > B[n - m - 1]) >= n + 1 if n - m >= 1 else True
            else:
                okdisc &= all(b > med for b in B[m:]) and all(a < med for a in A[:n - m])
check(f"6a.3 Median agrees with brute force on all {cases} interleavings of two sorted arrays, n = 1..8", ok)
check("6a.3 in every call the discarded A[m+1..n] lie strictly above and B[1..n-m] strictly below the median "
      "(B[n-m] has at least n+1 larger elements)", okdisc)
check("6a.3 exactly ceil(lg n) comparisons A[m] vs B[m] plus one at the base (calls = ceil(lg n) + 1)", okc)
ok = okc = True
for _ in range(2000):
    n = rng.randint(1, 3000)
    vals = rng.sample(range(10 ** 6), 2 * n)
    A = sorted(vals[:n])
    B = sorted(vals[n:])
    cnt = [0]
    ok &= median(A, B, cnt) == sorted(vals)[n - 1]
    okc &= cnt[0] == clg(n) + 1
check("6a.3 Median correct on 2000 random pairs up to n = 3000, with ceil(lg n) + 1 calls", ok and okc)
A = [0, 1, 6, 9, 12, 13, 18, 20]
B = [2, 4, 5, 8, 17, 19, 21, 23]
log = []
r = median(A, B, None, log)
check("6a.3 handout example: the median of A and B is 9", r == 9 and nth_smallest(A, B, 8) == 9)
check("6a.3 trace: (8, m=4: 9 > 8), (4, m=2: 1 < 19), (2, m=1: 6 < 17), base min(9, 17) = 9",
      log == [(8, 4, 9, 8), (4, 2, 1, 19), (2, 1, 6, 17), (1, None, 9, 17)], str(log))
# the remaining arrays in the trace
check("6a.3 trace arrays: [0,1,6,9]/[17,19,21,23] -> [6,9]/[17,19] -> [9]/[17]",
      (A[:4], B[4:]) == ([0, 1, 6, 9], [17, 19, 21, 23]) and ([0, 1, 6, 9][2:], [17, 19, 21, 23][:2]) ==
      ([6, 9], [17, 19]) and ([6, 9][1:], [17, 19][:1]) == ([9], [17]))
# n = 1 must be a base case: with m = ceil(1/2) = 1 the call would repeat itself
check("6a.3 n = 1 needs the base case (m = 1, the recursive call would be on the same arrays)",
      (1 + 1) // 2 == 1 and 1 - 1 + 1 == 1)
# the official write-up's count for B[n-m]: 2n - 2m + 1 >= n only gives B[n-m] <= median when n is odd
ok = True
for n in range(3, 40, 2):
    m = (n + 1) // 2
    ok &= 2 * n - 2 * m + 1 == n
check("6a.3 for odd n the official count 2n - 2m + 1 equals n (not enough for 'strictly below'); the page counts "
      "n + 1", ok)

# ----------------------------------------------------------------------------------------- Problem 4


def lower_median(X, Y, cnt=None, log=None):
    return median(X, Y, cnt, log)


def upper_median(X, Y, cnt=None):
    """l-th largest of X u Y for |X| = |Y| = l: negate and reverse, take the l-th smallest, negate"""
    return -median([-x for x in reversed(X)], [-y for y in reversed(Y)], cnt)


def select(A, B, k, cnt=None, log=None):
    """k-th smallest of A[1..m] u B[1..n] (0-indexed storage); padding +-inf outside the arrays"""
    m, n = len(A), len(B)
    if k < (m + n) / 2:
        X = [A[i - 1] if i <= m else INF for i in range(1, k + 1)]
        Y = [B[i - 1] if i <= n else INF for i in range(1, k + 1)]
        return lower_median(X, Y, cnt, log)
    else:
        X = [A[i - 1] if i >= 1 else -INF for i in range(k - n, m + 1)]
        Y = [B[i - 1] if i >= 1 else -INF for i in range(k - m, n + 1)]
        assert len(X) == len(Y) == m + n - k + 1
        return upper_median(X, Y, cnt)


def kth_direct(A, B, k):
    """the alternative: compare A[i] and B[j] with i, j = min(length, floor(k/2)); drop the smaller prefix"""
    if not A:
        return B[k - 1]
    if not B:
        return A[k - 1]
    if k == 1:
        return min(A[0], B[0])
    i = min(len(A), k // 2)
    j = min(len(B), k // 2)
    if A[i - 1] < B[j - 1]:
        return kth_direct(A[i:], B, k - i)
    return kth_direct(A, B[j:], k - j)


ok = okd = okc = True
cases = 0
for m in range(0, 7):
    for n in range(0, 7):
        if m + n == 0:
            continue
        for A, B in interleavings(m, n):
            for k in range(1, m + n + 1):
                cases += 1
                cnt = [0]
                want = nth_smallest(A, B, k)
                ok &= select(A, B, k, cnt) == want
                ell = k if k < (m + n) / 2 else m + n - k + 1
                okc &= cnt[0] == clg(ell) + 1 and ell <= min(k, m + n - k + 1) + 1
                okd &= kth_direct(A, B, k) == want
check(f"6a.4 Select (padding + LowerMedian/UpperMedian) agrees with brute force on all {cases} cases, "
      "m, n <= 6, every k", ok)
check("6a.4 Select makes ceil(lg l) + 1 median calls, l = k or m + n - k + 1, l <= min(k, m+n-k+1) + 1", okc)
check("6a.4 the direct alternative (drop floor(k/2) elements per step) agrees on the same cases", okd)
ok = True
for m in range(0, 6):
    for n in range(0, 6):
        for A, B in interleavings(m, n):
            for k in range(1, m + n + 1):
                want = nth_smallest(A, B, k)
                X = [A[i - 1] if i <= m else INF for i in range(1, k + 1)]
                Y = [B[i - 1] if i <= n else INF for i in range(1, k + 1)]
                ok &= lower_median(X, Y) == want
                X = [A[i - 1] if i >= 1 else -INF for i in range(k - n, m + 1)]
                Y = [B[i - 1] if i >= 1 else -INF for i in range(k - m, n + 1)]
                ok &= upper_median(X, Y) == want
check("6a.4 either option alone (first k entries with inf padding, or last m+n-k+1 upside down) is correct for "
      "every k (m, n <= 5)", ok)
ok = okd = True
for _ in range(3000):
    m = rng.randint(0, 400)
    n = rng.randint(0, 400)
    if m + n == 0:
        continue
    vals = rng.sample(range(10 ** 6), m + n)
    A, B = sorted(vals[:m]), sorted(vals[m:])
    k = rng.randint(1, m + n)
    want = sorted(vals)[k - 1]
    ok &= select(A, B, k) == want
    okd &= kth_direct(A, B, k) == want
check("6a.4 both correct on 3000 random cases with m, n <= 400", ok and okd)
A = [0, 1, 6, 9, 12, 13, 18, 20]
B = [2, 5, 7, 17, 19]
log = []
r = select(A, B, 6, None, log)
check("6a.4 handout example: k = 6 gives 7", r == 7 and nth_smallest(A, B, 6) == 7)
check("6a.4 example: 6 < 13/2, so LowerMedian([0,1,6,9,12,13], [2,5,7,17,19,inf])", 6 < 13 / 2)
check("6a.4 trace: (6, m=3: 6 < 7), (3, m=2: 12 > 5), (2, m=1: 9 > 5), base min(9, 7) = 7",
      log == [(6, 3, 6, 7), (3, 2, 12, 5), (2, 1, 9, 5), (1, None, 9, 7)], str(log))
check("6a.4 the k-th smallest is the k-th smallest of A[1..k] u B[1..k] (example)",
      nth_smallest(A[:6], B[:6], 6) == 7)
# ties between padding values: a comparison inf > inf is False, i.e. A's padding counts as smaller than B's
check("6a.4 inf > inf is False in the comparison (A's padding is treated as smaller than B's)", not (INF > INF))

print()
print("=" * 30, "Lab 6b", "=" * 30)

# ----------------------------------------------------------------------------------------- digit arithmetic
OPS = [0]


def strip(D):
    D = list(D)
    while len(D) > 1 and D[-1] == 0:
        D.pop()
    return D


def to_digits(x):
    return [int(c) for c in reversed(str(x))]


def from_digits(D):
    return int("".join(str(d) for d in reversed(D)))


def mag_add(X, Y, L):
    out = [0] * L
    carry = 0
    for i in range(L):
        s = (X[i] if i < len(X) else 0) + (Y[i] if i < len(Y) else 0) + carry
        out[i] = s % 10
        carry = s // 10
    OPS[0] += L
    assert carry == 0 and all(v == 0 for v in X[L:]) and all(v == 0 for v in Y[L:])
    return out


def mag_cmp(X, Y):
    L = max(len(X), len(Y))
    for i in range(L - 1, -1, -1):
        a = X[i] if i < len(X) else 0
        b = Y[i] if i < len(Y) else 0
        if a != b:
            return 1 if a > b else -1
    return 0


def mag_sub(X, Y, L):
    """X >= Y"""
    out = [0] * L
    borrow = 0
    for i in range(L):
        s = (X[i] if i < len(X) else 0) - (Y[i] if i < len(Y) else 0) - borrow
        borrow = 1 if s < 0 else 0
        out[i] = s + 10 * borrow
    OPS[0] += L
    assert borrow == 0
    return out


def s_add(x, y, L):
    (sx, X), (sy, Y) = x, y
    if sx == sy:
        return (sx, mag_add(X, Y, L))
    if mag_cmp(X, Y) >= 0:
        return (sx, mag_sub(X, Y, L))
    return (sy, mag_sub(Y, X, L))


def s_neg(x):
    return (-x[0], x[1])


def fast_multiply(x, y, n):
    """the site's FastMultiply on signed digit arrays of exactly n digits; returns 2n digits"""
    (sx, X), (sy, Y) = x, y
    assert len(X) == n and len(Y) == n
    if n == 1:
        OPS[0] += 1
        p = X[0] * Y[0]
        return (sx * sy, [p % 10, p // 10])
    m = (n + 1) // 2
    pad = [0] * (2 * m - n)
    a, b = (sx, X[m:] + pad), (sx, X[:m])     # x = 10^m a + b, a and b with the sign of x
    c, d = (sy, Y[m:] + pad), (sy, Y[:m])
    e = fast_multiply(a, c, m)
    f = fast_multiply(b, d, m)
    g = fast_multiply(s_add(a, s_neg(b), m), s_add(c, s_neg(d), m), m)
    mid = s_add(s_add(e, f, 2 * m + 1), s_neg(g), 2 * m + 1)
    L = 2 * n

    def shifted(z, s):
        D = [0] * s + z[1]
        assert all(v == 0 for v in D[L:])
        return (z[0], D[:L] + [0] * (L - len(D[:L])))
    r = s_add(shifted(f, 0), shifted(mid, m), L)
    r = s_add(r, shifted(e, 2 * m), L)
    return r


def K_formula_table(N):
    K = [0, 1]
    for L in range(2, N + 1):
        m = (L + 1) // 2
        K.append(3 * K[m] + 6 * m + 2 + 4 * L)
    return K


KTAB = K_formula_table(1 << 17)


def K(L):
    while L >= len(KTAB):
        KTAB.extend(K_formula_table(2 * len(KTAB))[len(KTAB):])
    return KTAB[L]


def dec_multiply(U, V):
    L = max(len(U), len(V))
    s, R = fast_multiply((1, U + [0] * (L - len(U))), (1, V + [0] * (L - len(V))), L)
    return strip(R)


def dec_add(U, V):
    L = max(len(U), len(V))
    R = mag_add(U, V, L + 1)
    OPS[0] -= 1          # count L digit additions; the carry digit is not an operation
    return strip(R)


def dec_double(Z):
    out = []
    carry = 0
    for z in Z:
        s = 2 * z + carry
        out.append(s % 10)
        carry = s // 10
        OPS[0] += 1
    if carry:
        out.append(carry)
    return out


# Karatsuba checks
ok = True
for _ in range(400):
    n = rng.randint(1, 60)
    x = rng.randrange(10 ** n)
    y = rng.randrange(10 ** n)
    sx, sy = rng.choice((1, -1)), rng.choice((1, -1))
    X = to_digits(x) + [0] * (n - len(to_digits(x)))
    Y = to_digits(y) + [0] * (n - len(to_digits(y)))
    s, R = fast_multiply((sx, X), (sy, Y), n)
    ok &= s * from_digits(R) == sx * sy * x * y or (x * y == 0 and from_digits(R) == 0)
check("6b FastMultiply on signed digit arrays is correct on 400 random pairs up to 60 digits", ok)
ok = True
for L in range(1, 161):
    OPS[0] = 0
    x = rng.randrange(10 ** L)
    y = rng.randrange(10 ** L)
    R = dec_multiply(to_digits(x) + [0] * (L - len(to_digits(x))), to_digits(y) + [0] * (L - len(to_digits(y))))
    ok &= from_digits(R) == x * y and OPS[0] == K(L)
check("6b digit operations of FastMultiply on L digits depend only on L: K(1) = 1, K(L) = 3K(ceil(L/2)) + 6ceil(L/2)"
      " + 4L + 2 (measured = formula for every L <= 160)", ok)
rat = [K(2 ** j) / (2 ** j) ** LG3 for j in range(6, 17)]
check("6b K(2^j)/(2^j)^lg3 settles (Karatsuba is Theta(n^lg3)): j = 14, 15, 16 within 1%",
      max(rat[-3:]) / min(rat[-3:]) < 1.01, ", ".join(f"{v:.3f}" for v in rat[-4:]))
check("6b K(L)/L^lg3 stays between 5 and 40 for every L in 2..2^17 (bounded: Theta(L^lg3))",
      all(5 < K(L) / L ** LG3 < 40 for L in range(2, 1 << 17)),
      f"min {min(K(L) / L ** LG3 for L in range(2, 1 << 17)):.2f}, max {max(K(L) / L ** LG3 for L in range(2, 1 << 17)):.2f}")


# ----------------------------------------------------------------------------------------- fast mode helpers
P10 = {}


def pow10(k):
    if k not in P10:
        P10[k] = 10 ** k
    return P10[k]


def ndig(x):
    if x < 10:
        return 1
    k = int((x.bit_length() - 1) * 0.30102999566398120) + 1
    while k > 1 and pow10(k - 1) > x:
        k -= 1
    while pow10(k) <= x:
        k += 1
    return k


check("6b ndig agrees with len(str(x)) on 3000 random and boundary values",
      all(ndig(x) == len(str(x)) for x in [rng.randrange(10 ** rng.randint(1, 400)) for _ in range(2000)] +
          [10 ** k for k in range(300)] + [10 ** k - 1 for k in range(1, 300)] + [0, 1, 9]))
check("6b 2^n has floor(n log10 2) + 1 decimal digits (n <= 3000): Theta(n)",
      all(len(str(2 ** n)) == math.floor(n * math.log10(2)) + 1 for n in range(0, 3001)))


def kara_cost(L):
    return K(L)


def fft_cost(L):
    """an O(n log n) multiplication, charged L * ceil(lg L) (at least L)"""
    return L * max(1, clg(L))


# ----------------------------------------------------------------------------------------- Problem 1
def two_to_the_digits(n):
    if n == 0:
        return [1]
    Z = two_to_the_digits(n // 2)
    Z = dec_multiply(Z, Z)
    if n % 2 == 1:
        Z = dec_double(Z)
    return Z


TT_CACHE = {}


def two_to_the_fast(n, mulcost):
    """returns (2^n, digit operations of DecimalTwoToThe(n)); cached by (n, mulcost) — the cost is charged in full"""
    key = (n, mulcost)
    if key in TT_CACHE:
        return TT_CACHE[key]
    if n == 0:
        res = (1, 0)
    else:
        z, c = two_to_the_fast(n // 2, mulcost)
        L = ndig(z)
        c += mulcost(L)
        z = z * z
        if n % 2 == 1:
            c += ndig(z)
            z = 2 * z
        res = (z, c)
    TT_CACHE[key] = res
    return res


ok = okc = True
for n in range(0, 401):
    OPS[0] = 0
    D = two_to_the_digits(n)
    c = OPS[0]
    ok &= from_digits(D) == 2 ** n and D == to_digits(2 ** n)
    okc &= two_to_the_fast(n, kara_cost) == (2 ** n, c)
check("6b.1 DecimalTwoToThe(n) (digit arrays, Karatsuba squaring, doubling) outputs the digits of 2^n for n <= 400", ok)
check("6b.1 fast mode charges exactly the digit operations counted digit by digit (n <= 400)", okc)
r1 = [two_to_the_fast(2 ** k, kara_cost)[1] / (2 ** k) ** LG3 for k in range(6, 21)]
check("6b.1 ops(2^k)/(2^k)^lg3 settles for k = 6..20 (last three within 1%): Theta(n^lg3)",
      max(r1[-3:]) / min(r1[-3:]) < 1.01, ", ".join(f"{v:.3f}" for v in r1[-5:]))
r1b = [two_to_the_fast(n, kara_cost)[1] / n ** LG3 for n in range(1000, 200001, 997)]
check("6b.1 ops(n)/n^lg3 stays bounded for all sampled n in 1000..200000",
      max(r1b) / min(r1b) < 4, f"min {min(r1b):.2f}, max {max(r1b):.2f}")
# the final squaring is the bulk of the work
ok = True
fr = []
for n in list(range(64, 5000, 37)) + [2 ** k for k in range(6, 21)]:
    z, c = two_to_the_fast(n, kara_cost)
    zprev, _ = two_to_the_fast(n // 2, kara_cost)
    last = kara_cost(ndig(zprev))
    fr.append(last / c)
check("6b.1 the last squaring is 67-70% of all digit operations (sampled n), so the others cost at most half of it",
      0.665 <= min(fr) and max(fr) <= 0.705,
      f"fraction between {min(fr):.3f} and {max(fr):.3f}")
# level values n^lg3 / 3^i
check("6b.1 recursion-tree values: (n/2^i)^lg3 = n^lg3 / 3^i (exact: 2^(i lg3) = 3^i)",
      all(abs(2 ** (i * LG3) - 3 ** i) < 1e-6 * 3 ** i for i in range(30)))
check("6b.1 level sums 1 + 1/3 + 1/9 + ... < 3/2", sum(Fraction(1, 3 ** i) for i in range(60)) < Fraction(3, 2))

# the standard algorithm: n-bit long division by 10, once per output digit
ok = True
rs = []
for n in [2 ** k for k in range(6, 14)]:
    x = rng.getrandbits(n) | (1 << (n - 1))
    bitops = 0
    digits = []
    while True:
        bitops += x.bit_length()
        digits.append(x % 10)
        x //= 10
        if x == 0:
            break
    rs.append(bitops / n ** 2)
check("6b intro: repeated division by 10 costs Theta(n^2) bit operations (ratio to n^2 settles near 1/(2 lg 10))",
      max(rs[-3:]) / min(rs[-3:]) < 1.02 and abs(rs[-1] - 1 / (2 * math.log2(10))) < 0.01,
      ", ".join(f"{v:.4f}" for v in rs[-3:]))


# ----------------------------------------------------------------------------------------- Problem 2
def bits_of(x, n):
    return [(x >> i) & 1 for i in range(n)]


def decimal2_digits(X):
    """Problem 2: X[0..n-1] little-endian bits; three recursive calls"""
    n = len(X)
    if n <= 3:
        OPS[0] += 1
        return [X[0] + 2 * (X[1] if n > 1 else 0) + 4 * (X[2] if n > 2 else 0)]
    m = (n + 1) // 2
    T = [0] * m + [1]                     # 2^m in binary, m + 1 bits
    M = decimal2_digits(T)
    A = decimal2_digits(X[m:])
    B = decimal2_digits(X[:m])
    return dec_add(dec_multiply(A, M), B)


D2_CACHE = {}


def decimal2_fast(X, mulcost):
    n = len(X)
    if n <= 3:
        return (X[0] + 2 * (X[1] if n > 1 else 0) + 4 * (X[2] if n > 2 else 0), 1)
    m = (n + 1) // 2
    key = (m, mulcost)
    if key not in D2_CACHE:              # the call on 2^m depends only on m: simulate once, charge every time
        D2_CACHE[key] = decimal2_fast([0] * m + [1], mulcost)
    M, cm = D2_CACHE[key]
    A, ca = decimal2_fast(X[m:], mulcost)
    B, cb = decimal2_fast(X[:m], mulcost)
    c = cm + ca + cb + mulcost(max(ndig(A), ndig(M)))
    P = A * M
    c += max(ndig(P), ndig(B))
    return (P + B, c)


# ----------------------------------------------------------------------------------------- Problem 3
def decimal3_digits(X):
    n = len(X)
    if n <= 3:
        OPS[0] += 1
        return [X[0] + 2 * (X[1] if n > 1 else 0) + 4 * (X[2] if n > 2 else 0)]
    m = (n + 1) // 2
    M = two_to_the_digits(m)
    A = decimal3_digits(X[m:])
    B = decimal3_digits(X[:m])
    return dec_add(dec_multiply(A, M), B)


def decimal3_fast(X, mulcost):
    n = len(X)
    if n <= 3:
        return (X[0] + 2 * (X[1] if n > 1 else 0) + 4 * (X[2] if n > 2 else 0), 1)
    m = (n + 1) // 2
    M, cm = two_to_the_fast(m, mulcost)
    A, ca = decimal3_fast(X[m:], mulcost)
    B, cb = decimal3_fast(X[:m], mulcost)
    c = cm + ca + cb + mulcost(max(ndig(A), ndig(M)))
    P = A * M
    c += max(ndig(P), ndig(B))
    return (P + B, c)


def decimal4_both(X, mulcost):
    """Problem 4, second version: returns (x, 2^n, cost)"""
    n = len(X)
    if n <= 3:
        return (X[0] + 2 * (X[1] if n > 1 else 0) + 4 * (X[2] if n > 2 else 0), 2 ** n, 1)
    m = (n + 1) // 2
    DA, MA, ca = decimal4_both(X[m:], mulcost)       # a and 2^(n-m)
    DB, MB, cb = decimal4_both(X[:m], mulcost)       # b and 2^m
    c = ca + cb + mulcost(max(ndig(DA), ndig(MB)))
    P = DA * MB
    c += max(ndig(P), ndig(DB))
    DX = P + DB
    c += mulcost(max(ndig(MA), ndig(MB)))
    MX = MA * MB
    return (DX, MX, c)


ok2 = ok3 = okc2 = okc3 = True
cnt_all = 0
for n in range(1, 13):
    for x in range(2 ** n):
        X = bits_of(x, n)
        cnt_all += 1
        OPS[0] = 0
        D = decimal2_digits(X)
        c2 = OPS[0]
        ok2 &= D == to_digits(x)
        OPS[0] = 0
        D = decimal3_digits(X)
        c3 = OPS[0]
        ok3 &= D == to_digits(x)
        if n in (4, 7, 12) and x % 17 == 0:
            okc2 &= decimal2_fast(X, kara_cost) == (x, c2)
            okc3 &= decimal3_fast(X, kara_cost) == (x, c3)
for _ in range(60):
    n = rng.randint(13, 300)
    x = rng.getrandbits(n)
    X = bits_of(x, n)
    OPS[0] = 0
    D = decimal2_digits(X)
    c2 = OPS[0]
    ok2 &= D == to_digits(x)
    OPS[0] = 0
    D = decimal3_digits(X)
    c3 = OPS[0]
    ok3 &= D == to_digits(x)
    okc2 &= decimal2_fast(X, kara_cost) == (x, c2)
    okc3 &= decimal3_fast(X, kara_cost) == (x, c3)
check(f"6b.2 Decimal (three recursive calls) outputs the right digits on all {cnt_all} bit strings of length <= 12 "
      "and 60 random ones up to 300 bits", ok2)
check(f"6b.3 Decimal with DecimalTwoToThe for 2^m: same inputs, right digits", ok3)
check("6b.2/6b.3 fast mode charges exactly the digit-by-digit operation counts (sampled short inputs and the 60 random)",
      okc2 and okc3)

ks = list(range(5, 17))
c2s = []
c3s = []
for k in ks:
    n = 2 ** k
    x = rng.getrandbits(n) | (1 << (n - 1))
    X = bits_of(x, n)
    v2, c2 = decimal2_fast(X, kara_cost)
    v3, c3 = decimal3_fast(X, kara_cost)
    assert v2 == x and v3 == x
    c2s.append(c2)
    c3s.append(c3)
r2 = [c / (2 ** k) ** LG3 for c, k in zip(c2s, ks)]
d2 = [r2[i + 1] - r2[i] for i in range(len(r2) - 1)]
r2l = [c / ((2 ** k) ** LG3 * k) for c, k in zip(c2s, ks)]
check("6b.2 ops/n^lg3 keeps growing: it increases by a roughly constant amount per doubling of n (last four "
      "increments within 10% of each other)", min(d2) > 0 and max(d2[-4:]) / min(d2[-4:]) < 1.10,
      "increments " + ", ".join(f"{v:.2f}" for v in d2[-5:]))
check("6b.2 ops/(n^lg3 lg n) stays between 1 and 1.5 for n = 2^9..2^16 (slowly rising toward the increment): "
      "Theta(n^lg3 log n)", all(1 < v < 1.5 for v in r2l[4:]) and all(r2l[i] < r2l[i + 1] for i in range(4, len(r2l) - 1)),
      ", ".join(f"{v:.2f}" for v in r2l[4:]))
r3 = [c / (2 ** k) ** LG3 for c, k in zip(c3s, ks)]
for k in (17, 18):                       # Problem 3 alone runs fast enough to go further
    n = 2 ** k
    x = rng.getrandbits(n) | (1 << (n - 1))
    v3, c3 = decimal3_fast(bits_of(x, n), kara_cost)
    assert v3 == x
    r3.append(c3 / n ** LG3)
d3 = [r3[i + 1] - r3[i] for i in range(len(r3) - 1)]
check("6b.3 ops/n^lg3 settles: its increments shrink geometrically (each of the last six at most 0.8 times the one "
      "before) and the last three ratios are within 2%: Theta(n^lg3)",
      all(0 < d3[i + 1] <= 0.8 * d3[i] for i in range(len(d3) - 7, len(d3) - 1)) and max(r3[-3:]) / min(r3[-3:]) < 1.02,
      "ratios " + ", ".join(f"{v:.3f}" for v in r3[-5:]) + "; increments " + ", ".join(f"{v:.3f}" for v in d3[-5:]))
check("6b.3 Problem 3 beats Problem 2 by a factor that grows with n", all(c2 > c3 for c2, c3 in zip(c2s, c3s)) and
      c2s[-1] / c3s[-1] > c2s[3] / c3s[3] + 1, ", ".join(f"{a / b:.2f}" for a, b in zip(c2s, c3s)))
check("6b.3 Problem 2 / Problem 3 digit operations: about 1.2 at n = 32, about 3 at n = 65536",
      abs(c2s[0] / c3s[0] - 1.2) < 0.05 and abs(c2s[-1] / c3s[-1] - 3.0) < 0.1 and ks[0] == 5 and ks[-1] == 16,
      f"{c2s[0] / c3s[0]:.3f}, {c2s[-1] / c3s[-1]:.3f}")
check("6b.2 the per-doubling increment of ops/n^lg3 is about 1.5", all(1.4 < d < 1.55 for d in d2[-4:]))
check("6b.3 recursion-tree level sums 2^i (n/2^i)^lg3 = (2/3)^i n^lg3 (exact)",
      all(abs(2 ** i * 2 ** (-i * LG3) - (2 / 3) ** i) < 1e-12 for i in range(40)))
check("6b.2 recursion-tree level sums 3^i (n/2^i)^lg3 = n^lg3 (exact)",
      all(abs(3 ** i * 2 ** (-i * LG3) - 1) < 1e-9 for i in range(40)))

# ----------------------------------------------------------------------------------------- Problem 4
r4a = [two_to_the_fast(2 ** k, fft_cost)[1] / (2 ** k * k) for k in range(6, 21)]
check("6b.4 DecimalTwoToThe with an n log n multiplication: ops/(n lg n) settles (last three within 2%): O(n log n)",
      max(r4a[-3:]) / min(r4a[-3:]) < 1.02, ", ".join(f"{v:.3f}" for v in r4a[-4:]))
ks4 = list(range(5, 18))
c4, c4b, c4c = [], [], []
for k in ks4:
    n = 2 ** k
    x = rng.getrandbits(n) | (1 << (n - 1))
    X = bits_of(x, n)
    v, c = decimal3_fast(X, fft_cost)
    assert v == x
    c4.append(c)
    v, mx, c = decimal4_both(X, fft_cost)
    assert v == x and mx == 2 ** n
    c4b.append(c)
    if k <= 15:
        v, c = decimal2_fast(X, fft_cost)
        assert v == x
        c4c.append(c)
for name, cs in (("Problem 3's algorithm", c4), ("the version returning x and 2^n", c4b)):
    rr = [c / (2 ** k * k) for c, k in zip(cs, ks4)]
    dd = [rr[i + 1] - rr[i] for i in range(len(rr) - 1)]
    rl = [c / (2 ** k * k * k) for c, k in zip(cs, ks4)]
    check(f"6b.4 {name} with n log n multiplication: ops/(n lg n) grows by a roughly constant amount per doubling "
          "(last four increments within 10%)", min(dd) > 0 and max(dd[-4:]) / min(dd[-4:]) < 1.10,
          "increments " + ", ".join(f"{v:.2f}" for v in dd[-4:]))
    check(f"6b.4 {name}: ops/(n lg^2 n) approaches a constant (last three within 6%): Theta(n log^2 n)",
          max(rl[-3:]) / min(rl[-3:]) < 1.06, ", ".join(f"{v:.3f}" for v in rl[-4:]))
rr = [c / (2 ** k) ** LG3 for c, k in zip(c4c, ks4)]
check("6b.4 Problem 2's three-call algorithm with n log n multiplication: ops/n^lg3 settles (leaves dominate, "
      "Theta(n^lg3))", max(rr[-3:]) / min(rr[-3:]) < 1.03, ", ".join(f"{v:.3f}" for v in rr[-4:]))
# the recurrence 2T(n/2) + n lg n at powers of two
T = {1: 0}
for k in range(1, 30):
    T[2 ** k] = 2 * T[2 ** (k - 1)] + 2 ** k * k
check("6b.4 T(n) = 2T(n/2) + n lg n, T(1) = 0 gives n lg n (lg n + 1)/2 at powers of 2",
      all(T[2 ** k] == 2 ** k * k * (k + 1) // 2 for k in range(30)))

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: {FAIL}")
