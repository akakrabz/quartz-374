#!/usr/bin/env python3
"""Checks for content/4-lecture-notes/d-advanced-dynamic-programming.md (Erickson, Extended Dance Remix D).

Every recurrence and pseudocode block is implemented as printed in the note (tables refuse reads of unwritten
entries and out-of-range indices) and as corrected on the page; everything is compared with the plain dynamic
programs or brute force on many random inputs; every structural property the note claims (Knuth's monotonicity,
monotone / totally monotone / Monge arrays and the lemmas about them, Reduce's invariants) is tested on random
arrays; operation counts confirm the running times; every number in the note's examples is recomputed."""
import functools
import heapq
import itertools
import math
import os
import random
import sys
from fractions import Fraction

sys.setrecursionlimit(20000)
FAIL = []
random.seed(374)
INF = float("inf")


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAIL.append(name)


class Unwritten(Exception):
    pass


class Table:
    def __init__(self, *ranges):
        self.ranges = ranges
        self.d = {}

    def _ok(self, key):
        key = key if isinstance(key, tuple) else (key,)
        for k, r in zip(key, self.ranges):
            if r is not None and k not in r:
                raise IndexError(f"index {key} outside range")
        return key

    def __getitem__(self, key):
        key = self._ok(key)
        if key not in self.d:
            raise Unwritten(f"read of unwritten entry {key}")
        return self.d[key]

    def __setitem__(self, key, v):
        self.d[self._ok(key)] = v


def rand_str(n, alpha):
    return "".join(random.choice(alpha) for _ in range(n))


# =====================================================================================================
# D.1 Hirschberg
# =====================================================================================================
random.seed(375)
def edit_table(A, B):
    m, n = len(A), len(B)
    E = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        for j in range(n + 1):
            if i == 0:
                E[i][j] = j
            elif j == 0:
                E[i][j] = i
            else:
                E[i][j] = min(E[i][j - 1] + 1, E[i - 1][j] + 1, E[i - 1][j - 1] + (A[i - 1] != B[j - 1]))
    return E


def half_table(A, B, E):
    """The note's Half(i, j) (p. 2), cases tested in the printed order."""
    m, n = len(A), len(B)
    mid = m // 2
    H = [[None] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        for j in range(n + 1):
            if i < mid:
                H[i][j] = INF
            elif i == mid:
                H[i][j] = j
            elif E[i][j] == E[i - 1][j] + 1:
                H[i][j] = H[i - 1][j]
            elif j > 0 and E[i][j] == E[i][j - 1] + 1:
                H[i][j] = H[i][j - 1]
            else:
                H[i][j] = H[i - 1][j - 1]
    return H


def half_linear_space(A, B, counter):
    """Edit(m, n) and Half(m, n) with two rows of each table (O(n) space); counts cells."""
    m, n = len(A), len(B)
    mid = m // 2
    pe = list(range(n + 1))
    ph = [INF] * (n + 1) if mid > 0 else list(range(n + 1))
    counter[0] += n + 1
    for i in range(1, m + 1):
        ce = [i] + [0] * n
        ch = [None] * (n + 1)
        for j in range(n + 1):
            if j > 0:
                ce[j] = min(ce[j - 1] + 1, pe[j] + 1, pe[j - 1] + (A[i - 1] != B[j - 1]))
            if i < mid:
                ch[j] = INF
            elif i == mid:
                ch[j] = j
            elif ce[j] == pe[j] + 1:
                ch[j] = ph[j]
            elif j > 0 and ce[j] == ce[j - 1] + 1:
                ch[j] = ch[j - 1]
            else:
                ch[j] = ph[j - 1]
        counter[0] += n + 1
        pe, ph = ce, ch
    return pe[n], ph[n]


def align_small(A, B, counter):
    """Plain DP with traceback (base case: one string has length <= 1)."""
    E = edit_table(A, B)
    counter[0] += (len(A) + 1) * (len(B) + 1)
    i, j, cols = len(A), len(B), []
    while i > 0 or j > 0:
        if i > 0 and j > 0 and E[i][j] == E[i - 1][j - 1] + (A[i - 1] != B[j - 1]):
            cols.append((A[i - 1], B[j - 1]))
            i, j = i - 1, j - 1
        elif i > 0 and E[i][j] == E[i - 1][j] + 1:
            cols.append((A[i - 1], "-"))
            i -= 1
        else:
            cols.append(("-", B[j - 1]))
            j -= 1
    return cols[::-1]


def hirschberg(A, B, counter, depth=0, stats=None):
    if stats is not None:
        stats["depth"] = max(stats.get("depth", 0), depth)
    if len(A) <= 1 or len(B) <= 1:
        return align_small(A, B, counter)
    mid = len(A) // 2
    _, h = half_linear_space(A, B, counter)
    return hirschberg(A[:mid], B[:h], counter, depth + 1, stats) + hirschberg(A[mid:], B[h:], counter, depth + 1, stats)


def cost(cols):
    return sum(a != b for a, b in cols)


# the note's example (p. 2): rows ALTRUISTIC (A, m = 10), columns ALGORITHM (B, n = 9)
A0, B0 = "ALTRUISTIC", "ALGORITHM"
E0 = edit_table(A0, B0)
printed_edit = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [1, 0, 1, 2, 3, 4, 5, 6, 7, 8], [2, 1, 0, 1, 2, 3, 4, 5, 6, 7],
    [3, 2, 1, 1, 2, 3, 4, 4, 5, 6], [4, 3, 2, 2, 2, 2, 3, 4, 5, 6], [5, 4, 3, 3, 3, 3, 3, 4, 5, 6],
    [6, 5, 4, 4, 4, 4, 3, 4, 5, 6], [7, 6, 5, 5, 5, 5, 4, 4, 5, 6], [8, 7, 6, 6, 6, 6, 5, 4, 5, 6],
    [9, 8, 7, 7, 7, 7, 6, 5, 5, 6], [10, 9, 8, 8, 8, 8, 7, 6, 6, 6]]
check("D.1 example: the Edit table for ALTRUISTIC x ALGORITHM (p. 2) is correct", E0 == printed_edit)
red = [(i, j) for i in range(1, 11) for j in range(1, 10) if A0[i - 1] == B0[j - 1]]
check("D.1 example: the red entries of the Edit table are exactly the match points A[i] = B[j]",
      red == [(1, 1), (2, 2), (3, 7), (4, 5), (6, 6), (8, 7), (9, 6)], str(red))
H0 = half_table(A0, B0, E0)
printed_half = [[INF] * 10] * 5 + [list(range(10))] + [[0, 1, 2, 3, 4, 5, 5, 5, 5, 5]] * 5
check("D.1 example: the Half table (p. 2) is correct; Half(10, 9) = 5", H0 == printed_half and H0[10][9] == 5)
check("D.1 example: split ALTRU/ALGOR (cost 3) + ISTIC/ITHM (cost 3) = 6",
      edit_table("ALTRU", "ALGOR")[5][5] == 3 and edit_table("ISTIC", "ITHM")[5][4] == 3 and E0[10][9] == 6)
cnt = [0]
al = hirschberg(A0, B0, cnt)
top = "".join(a for a, b in al)
bot = "".join(b for a, b in al)
check("D.1 example: Hirschberg's alignment has cost 6 and spells both strings",
      cost(al) == 6 and top.replace("-", "") == A0 and bot.replace("-", "") == B0, f"{top} / {bot}")

ok_half = ok_lin = ok_align = True
worst_ratio = 0
for trial in range(3000):
    m, n = random.randint(0, 12), random.randint(0, 12)
    alpha = random.choice(["AB", "ABC", "ACGT"])
    A, B = rand_str(m, alpha), rand_str(n, alpha)
    E = edit_table(A, B)
    if m >= 1:
        H = half_table(A, B, E)
        h = H[m][n]
        mid = m // 2
        if not (0 <= h <= n and edit_table(A[:mid], B[:h])[mid][h] + edit_table(A[mid:], B[h:])[m - mid][n - h] == E[m][n]):
            ok_half = False
        c = [0]
        d, h2 = half_linear_space(A, B, c)
        ok_lin &= (d == E[m][n] and h2 == h)
    c = [0]
    al = hirschberg(A, B, c)
    if not (cost(al) == E[m][n] and "".join(a for a, b in al).replace("-", "") == A
            and "".join(b for a, b in al).replace("-", "") == B and all(a != "-" or b != "-" for a, b in al)):
        ok_align = False
check("D.1: Half(m, n) always gives an optimal split: Edit(A[..m/2], B[..h]) + Edit(rest) = Edit(A, B) "
      "(3000 random pairs)", ok_half)
check("D.1: the two-row (linear-space) sweep computes Edit(m, n) and the same Half(m, n)", ok_lin)
check("D.1: Hirschberg's recursion returns a valid optimal alignment every time", ok_align)

# running time: cells computed in all calls / ((m + 1)(n + 1)), for growing sizes; recursion depth
ratios = []
ok_depth = True
for m, n in [(16, 16), (32, 32), (64, 64), (128, 128), (128, 64), (64, 200), (200, 50), (256, 256)]:
    worst = 0
    for _ in range(3):
        A, B = rand_str(m, "ACGT"), rand_str(n, "ACGT")
        c = [0]
        st = {}
        hirschberg(A, B, c, stats=st)
        worst = max(worst, c[0] / ((m + 1) * (n + 1)))
        ok_depth &= st["depth"] <= math.ceil(math.log2(m))
    ratios.append(round(worst, 3))
check("D.1: total cells computed / the first sweep's (m+1)(n+1) is about 2 (between 2 and 2.4, decreasing to"
      " 2.06 at 256 x 256), random strings", 2 <= min(ratios) and max(ratios) <= 2.4 and ratios[-1] < 2.1, str(ratios))
check("D.1: recursion depth <= ceil(log2 m)", ok_depth)


# worst-case recurrence T(m, n) = mn + max_h [T(floor(m/2), h) + T(ceil(m/2), n - h)], T = n if m <= 1, m if n <= 1
@functools.lru_cache(maxsize=None)
def Tw(m, n):
    if m <= 1:
        return n
    if n <= 1:
        return m
    return m * n + max(Tw(m // 2, h) + Tw(m - m // 2, n - h) for h in range(n + 1))


viol = [(m, n) for m in range(2, 41) for n in range(2, 41) if Tw(m, n) > 2 * m * n]
fits = all(Tw(m, n) <= 2 * m * n + (m + n) * math.log2(m) for m in range(2, 41) for n in range(2, 41))
ratio_T = max(Tw(m, n) / (m * n) for m in range(2, 41) for n in range(2, 41))
check("D.1: worst case of the recurrence: T(m, n) <= 2mn fails for some (m, n) (subproblems with h = 0 cost m/2)",
      len(viol) > 0, f"{len(viol)} of 1521 pairs, e.g. {viol[:3]}")
check("D.1: worst case of the recurrence: T(m, n) <= 2mn + (m + n) log2 m for all 2 <= m, n <= 40, and T(5, 40) = 442"
      " > 2mn = 400", fits and Tw(5, 40) == 442)
check("D.1: worst case of the recurrence: T(m, n) / mn <= 2.6 for all 2 <= m, n <= 40 (so O(mn))", ratio_T <= 2.6,
      f"max ratio {ratio_T:.3f}")
# the corrected induction: T(m, n) <= 4mn + m + n (step: mn + 4[ah + b(n-h)] + m + n <= 3mn + 3n + m, fine for m >= 2)
check("D.1: the guess T(m, n) <= 4mn + m + n holds for all 0 <= m, n <= 40 (base cases and rounding included)",
      all(Tw(m, n) <= 4 * m * n + m + n for m in range(0, 41) for n in range(0, 41)))
check("D.1: the induction step for that guess: mn + 4(floor(m/2) h + ceil(m/2)(n - h)) + m + n <= 4mn + m + n for all"
      " 2 <= m <= 40, 0 <= h <= n <= 40",
      all(m * n + 4 * ((m // 2) * h + (m - m // 2) * (n - h)) + m + n <= 4 * m * n + m + n
          for m in range(2, 41) for n in range(0, 41) for h in range(n + 1)))

# =====================================================================================================
# D.2 Sparse LCS
# =====================================================================================================
random.seed(376)
def lcs_table(A, B):
    m, n = len(A), len(B)
    L = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            L[i][j] = L[i - 1][j - 1] + 1 if A[i - 1] == B[j - 1] else max(L[i][j - 1], L[i - 1][j])
    return L


# Figure D.1: rows « A L T R U I S T I C », columns « A L G O R I T H M S » with sentinels « (index 0) and » (m+1)
RA, CB = "ALTRUISTIC", "ALGORITHMS"
Ls = lcs_table(RA + ">", CB + ">")
printed_lcs = [
    [0] * 12, [0] + [1] * 11, [0, 1] + [2] * 10, [0, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3],
    [0, 1, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3], [0, 1, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3],
    [0, 1, 2, 2, 3, 3, 4, 4, 4, 4, 4, 4], [0, 1, 2, 2, 3, 3, 4, 4, 4, 4, 5, 5],
    [0, 1, 2, 2, 3, 3, 4, 5, 5, 5, 5, 5], [0, 1, 2, 2, 3, 3, 4, 5, 5, 5, 5, 5],
    [0, 1, 2, 2, 3, 3, 4, 5, 5, 5, 5, 5], [0, 1, 2, 2, 3, 3, 4, 5, 5, 5, 5, 6]]
diff = [(i, j, printed_lcs[i][j], Ls[i][j]) for i in range(12) for j in range(12) if Ls[i][j] != printed_lcs[i][j]]
check("D.2 note error p. 4: Figure D.1 is correct except column O, rows U, I, S, T, I, C, >> (printed 3, correct 2)",
      [(i, j) for i, j, _, _ in diff] == [(i, 4) for i in range(5, 12)] and all(p == 3 and c == 2 for _, _, p, c in diff),
      str(diff))
check("D.2 example: LCS(ALTRU, ALGO) = 2 (A, L): the printed 3 is impossible", lcs_table("ALTRU", "ALGO")[5][4] == 2)
check("D.2 example: LCS(ALGORITHMS, ALTRUISTIC) = 5 = LCS(m+1, n+1) - 1", Ls[11][11] - 1 == 5 == lcs_table(RA, CB)[10][10])
K0 = sum(1 for a in RA for b in CB if a == b)
red_lcs = [(i, j, Ls[i][j]) for i in range(1, 11) for j in range(1, 11) if RA[i - 1] == CB[j - 1]]
check("D.2 example: K = 8 match points (+ the 2 sentinels), with values 1,2,3,3,4,5,5,4 (row order) as printed in red",
      K0 == 8 and [v for _, _, v in red_lcs] == [1, 2, 3, 3, 4, 5, 5, 4], f"{red_lcs}")


def sparse_lcs_recurrence(A, B):
    """The note's sparse recurrence (p. 4) with sentinels; returns dict (i, j) -> value for all 0 <= i <= m+1 etc."""
    m, n = len(A), len(B)
    AA = ["<"] + list(A) + [">"]
    BB = ["<"] + list(B) + [">"]
    match = [(i, j) for i in range(m + 2) for j in range(n + 2) if AA[i] == BB[j]]
    val = {}
    for i in range(m + 2):
        for j in range(n + 2):
            if i == 0 and j == 0:
                val[(i, j)] = 0
            elif AA[i] == BB[j]:
                val[(i, j)] = max(val[p] for p in match if p[0] < i and p[1] < j) + 1
            else:
                val[(i, j)] = max(val[p] for p in match if p[0] <= i and p[1] <= j)
    return val


ok_sparse_rec = True
for trial in range(400):
    A = rand_str(random.randint(0, 9), random.choice(["AB", "ABC", "ABCD"]))
    B = rand_str(random.randint(0, 9), random.choice(["AB", "ABC", "ABCD"]))
    L = lcs_table(A + ">", B + ">")
    v = sparse_lcs_recurrence(A, B)
    for i in range(len(A) + 2):
        for j in range(len(B) + 2):
            if v[(i, j)] != L[i][j]:
                ok_sparse_rec = False
check("D.2: the sparse recurrence (strict for match points, non-strict otherwise) reproduces every entry of the LCS"
      " table, sentinels included (400 random pairs)", ok_sparse_rec)


# edit distance without substitutions (or with substitutions costing 2) = m + n - 2 LCS
def indel(A, B, sub=None):
    m, n = len(A), len(B)
    E = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        for j in range(n + 1):
            if i == 0 or j == 0:
                E[i][j] = i + j
            else:
                opts = [E[i - 1][j] + 1, E[i][j - 1] + 1]
                if A[i - 1] == B[j - 1]:
                    opts.append(E[i - 1][j - 1])
                elif sub is not None:
                    opts.append(E[i - 1][j - 1] + sub)
                E[i][j] = min(opts)
    return E[m][n]


ok_indel = True
for trial in range(1000):
    A = rand_str(random.randint(0, 10), random.choice(["AB", "ABC", "ACGT"]))
    B = rand_str(random.randint(0, 10), random.choice(["AB", "ABC", "ACGT"]))
    l = lcs_table(A, B)[len(A)][len(B)]
    ok_indel &= indel(A, B) == indel(A, B, sub=2) == len(A) + len(B) - 2 * l
check("D.2: edit distance without substitutions = with substitutions costing 2 = m + n - 2 LCS (1000 random pairs)",
      ok_indel)


class Loop(Exception):
    pass


def find_matches_printed(A, B, cap=10000):
    """FindMatches exactly as printed (p. 5), 1-indexed, with an iteration cap and index guard."""
    m, n = len(A), len(B)
    I = sorted(range(1, m + 1), key=lambda i: A[i - 1])
    J = sorted(range(1, n + 1), key=lambda j: B[j - 1])
    SA = [None] + [A[i - 1] for i in I]
    SB = [None] + [B[j - 1] for j in J]
    I = [None] + I
    J = [None] + J
    out, steps = [], 0
    i, j = 1, 1
    while i < m and j < n:
        steps += 1
        if steps > cap:
            raise Loop
        if SA[i] < SB[j]:
            i += 1
        elif SA[i] > SB[j]:
            j += 1
        else:
            ii = i
            while SA[ii] == SA[i]:
                jj = j
                while SB[jj] == SB[j]:
                    out.append((I[ii], J[jj]))
                    jj += 1
                    steps += 1
                    if steps > cap:
                        raise Loop
                ii = i + 1
                steps += 1
                if steps > cap:
                    raise Loop
            i, j = ii, jj
    return out


def find_matches(A, B, work=None):
    """Corrected: i <= m and j <= n, bounded inner loops, ii <- ii + 1."""
    m, n = len(A), len(B)
    I = sorted(range(1, m + 1), key=lambda i: A[i - 1])
    J = sorted(range(1, n + 1), key=lambda j: B[j - 1])
    SA = [A[i - 1] for i in I]
    SB = [B[j - 1] for j in J]
    out, i, j = [], 0, 0
    while i < m and j < n:
        if work is not None:
            work[0] += 1
        if SA[i] < SB[j]:
            i += 1
        elif SA[i] > SB[j]:
            j += 1
        else:
            ii = i
            while ii < m and SA[ii] == SA[i]:
                jj = j
                while jj < n and SB[jj] == SB[j]:
                    out.append((I[ii], J[jj]))
                    if work is not None:
                        work[0] += 1
                    jj += 1
                ii += 1
            i, j = ii, jj
    return out


outcomes = {"loop": 0, "index": 0, "wrong": 0, "right": 0}
ok_fm = ok_fm_work = True
for trial in range(2000):
    A = rand_str(random.randint(1, 10), random.choice(["AB", "ABC", "ABCDE"]))
    B = rand_str(random.randint(1, 10), random.choice(["AB", "ABC", "ABCDE"]))
    truth = sorted((i, j) for i in range(1, len(A) + 1) for j in range(1, len(B) + 1) if A[i - 1] == B[j - 1])
    try:
        got = sorted(find_matches_printed(A, B))
        outcomes["right" if got == truth else "wrong"] += 1
    except Loop:
        outcomes["loop"] += 1
    except IndexError:
        outcomes["index"] += 1
    w = [0]
    got2 = sorted(find_matches(A, B, w))
    ok_fm &= (got2 == truth)
    ok_fm_work &= (w[0] <= len(A) + len(B) + len(truth))
check("D.2 note error p. 5: FindMatches as printed loops forever, runs off the arrays or misses matches",
      outcomes["loop"] > 0 and outcomes["wrong"] > 0, str(outcomes))
check("D.2: corrected FindMatches reports exactly the match points (2000 random pairs)", ok_fm)
check("D.2: corrected FindMatches merge phase takes <= m + n + K steps (after sorting)", ok_fm_work)
try:
    r = find_matches_printed("AB", "AB")
    printed_ab = sorted(r)
except Exception as e:  # noqa: BLE001
    printed_ab = type(e).__name__
check("D.2 note error p. 5: on A = B = AB, printed FindMatches finds only (1, 1) ('i < m' stops early)",
      printed_ab == [(1, 1)], str(printed_ab))


def sparse_lcs_printed(A, B):
    """SparseLCS exactly as printed (p. 5): loop k <- 1 to K, 'min'."""
    m, n = len(A), len(B)
    Mt = sorted(find_matches(A, B)) + [(m + 1, n + 1)]
    K = len(Mt) - 1
    LCS = Table(range(1, K + 2))
    for k in range(1, K + 1):
        i, j = Mt[k - 1]
        LCS[k] = 1
        for l in range(1, k):
            i2, j2 = Mt[l - 1]
            if i2 < i and j2 < j:
                LCS[k] = min(LCS[k], 1 + LCS[l])
    return LCS[K + 1] - 1


def sparse_lcs(A, B, work=None):
    """Corrected: k <- 1 to K + 1, 'max'."""
    m, n = len(A), len(B)
    Mt = sorted(find_matches(A, B)) + [(m + 1, n + 1)]
    K = len(Mt) - 1
    LCS = Table(range(1, K + 2))
    for k in range(1, K + 2):
        i, j = Mt[k - 1]
        LCS[k] = 1
        for l in range(1, k):
            if work is not None:
                work[0] += 1
            i2, j2 = Mt[l - 1]
            if i2 < i and j2 < j:
                LCS[k] = max(LCS[k], 1 + LCS[l])
    return LCS[K + 1] - 1


def lcs_klogk(A, B):
    """O(K log K) after finding matches: longest strictly increasing j over matches sorted (i asc, j desc)."""
    Mt = sorted(find_matches(A, B), key=lambda p: (p[0], -p[1]))
    tails = []
    import bisect
    for _, j in Mt:
        k = bisect.bisect_left(tails, j)
        if k == len(tails):
            tails.append(j)
        else:
            tails[k] = j
    return len(tails)


ok_sp = ok_sp_work = ok_klogk = True
printed_bad = 0
for trial in range(1500):
    A = rand_str(random.randint(0, 12), random.choice(["AB", "ABC", "ABCDEFG"]))
    B = rand_str(random.randint(0, 12), random.choice(["AB", "ABC", "ABCDEFG"]))
    truth = lcs_table(A, B)[len(A)][len(B)]
    w = [0]
    ok_sp &= (sparse_lcs(A, B, w) == truth)
    K = len(find_matches(A, B))
    ok_sp_work &= (w[0] == (K + 1) * K // 2)
    ok_klogk &= (lcs_klogk(A, B) == truth)
    try:
        if sparse_lcs_printed(A, B) != truth:
            printed_bad += 1
    except Unwritten:
        printed_bad += 1
check("D.2: corrected SparseLCS (max, k up to K + 1) equals the plain LCS (1500 random pairs)", ok_sp)
check("D.2: corrected SparseLCS's inner loop runs exactly K(K+1)/2 times: O(K^2) after the matches", ok_sp_work)
check("D.2 note error p. 5: SparseLCS as printed (min; k only up to K) never computes LCS[K+1]", printed_bad == 1500,
      f"{printed_bad} of 1500 fail")
check("D.2: the O(m log m + n log n + K log K) improvement exists (LIS over matches sorted by i, then j decreasing)",
      ok_klogk)

# =====================================================================================================
# D.3 Knuth's monotonicity for optimal binary search trees
# =====================================================================================================
random.seed(377)
def obst(f, rule="left"):
    n = len(f)
    F = [[0] * (n + 2) for _ in range(n + 2)]
    for i in range(1, n + 1):
        for j in range(i, n + 1):
            F[i][j] = F[i][j - 1] + f[j - 1]
    C = {}
    R = {}
    for i in range(1, n + 2):
        C[(i, i - 1)] = 0
    for d in range(0, n):
        for i in range(1, n - d + 1):
            j = i + d
            vals = [(C[(i, r - 1)] + C[(r + 1, j)], r) for r in range(i, j + 1)]
            best = min(v for v, _ in vals)
            roots = [r for v, r in vals if v == best]
            C[(i, j)] = best + F[i][j]
            R[(i, j)] = roots[0] if rule == "left" else roots[-1]
    return C, R, F


def knuth_ok(R, n):
    for i in range(1, n + 1):
        for j in range(i, n + 1):
            lo = R[(i, j - 1)] if j - 1 >= i else i
            hi = R[(i + 1, j)] if i + 1 <= j else j
            if not (lo <= R[(i, j)] <= hi):
                return False
    return True


ok_kl = ok_kr = True
for trial in range(1500):
    n = random.randint(1, 9)
    f = [random.randint(1, random.choice([2, 4, 10])) for _ in range(n)]
    _, Rl, _ = obst(f, "left")
    _, Rr, _ = obst(f, "right")
    ok_kl &= knuth_ok(Rl, n)
    ok_kr &= knuth_ok(Rr, n)
check("D.3: Knuth's OptRoot[i, j-1] <= OptRoot[i, j] <= OptRoot[i+1, j] holds with the leftmost optimal root "
      "(1500 random frequency arrays, many ties)", ok_kl)
check("D.3: ... and with the rightmost optimal root", ok_kr)
# with an arbitrary choice among tied optimal roots it can fail
bad_tie = None
for trial in range(3000):
    n = random.randint(2, 6)
    f = [random.randint(1, 2) for _ in range(n)]
    C, Rl, F = obst(f, "left")
    # choose a random optimal root
    Rrand = {}
    for (i, j) in Rl:
        best = C[(i, j)] - F[i][j]
        roots = [r for r in range(i, j + 1) if C[(i, r - 1)] + C[(r + 1, j)] == best]
        Rrand[(i, j)] = random.choice(roots)
    if not knuth_ok(Rrand, n):
        bad_tie = (f, Rrand)
        break
check("D.3: with ties broken arbitrarily the inequalities can fail (so 'the optimal root' needs a fixed tie rule)",
      bad_tie is not None, str(bad_tie[0]) if bad_tie else "")
C1, _, F1 = obst([1, 1, 1, 1, 1])
ties14 = [r for r in range(1, 5) if C1[(1, r - 1)] + C1[(r + 1, 4)] == C1[(1, 4)] - F1[1][4]]
ties15 = [r for r in range(1, 6) if C1[(1, r - 1)] + C1[(r + 1, 5)] == C1[(1, 5)] - F1[1][5]]
check("D.3: f = [1,1,1,1,1]: optimal roots of f[1..4] are {2,3} and of f[1..5] are {2,3,4}; choosing 3 and 2 violates"
      " OptRoot[1,4] <= OptRoot[1,5]", ties14 == [2, 3] and ties15 == [2, 3, 4], f"{ties14}, {ties15}")


def faster_obst_printed(f):
    """FasterOptimalSearchTree exactly as printed (p. 6)."""
    n = len(f)
    F = [[0] * (n + 2) for _ in range(n + 2)]
    for i in range(1, n + 1):
        for j in range(i, n + 1):
            F[i][j] = F[i][j - 1] + f[j - 1]
    OC = Table(range(1, n + 2), range(0, n + 1))
    OR = Table(range(1, n + 2), range(0, n + 1))
    for i in (range(1, n + 1) if n <= 1 else []):  # 'for i <- 1 downto n' is empty unless n <= 1
        OC[i, i - 1] = 0
        OR[i, i - 1] = i
    for d in range(0, n + 1):
        for i in range(1, n + 1):
            j = i + d
            OC[i, j] = INF
            for r in range(OR[i, j - 1], OR[i + 1, j] + 1):
                tmp = OC[i, r - 1] + OC[r + 1, j]
                if OC[i, j] > tmp:
                    OC[i, j] = tmp
                    OR[i, j] = r
            OC[i, j] = OC[i, j] + F[i][j]
    return OC[1, n]


def faster_obst(f, work=None, perd=None):
    """Corrected: bases OptCost[i, i-1] = 0 (i = 1..n+1), OptCost[i, i] = f[i], OptRoot[i, i] = i;
    then d <- 1 to n - 1, i <- 1 to n - d, r from OptRoot[i, j-1] to OptRoot[i+1, j]."""
    n = len(f)
    F = [[0] * (n + 2) for _ in range(n + 2)]
    for i in range(1, n + 1):
        for j in range(i, n + 1):
            F[i][j] = F[i][j - 1] + f[j - 1]
    OC = Table(range(1, n + 2), range(0, n + 1))
    OR = Table(range(1, n + 1), range(1, n + 1))
    for i in range(1, n + 2):
        OC[i, i - 1] = 0
    for i in range(1, n + 1):
        OC[i, i] = f[i - 1]
        OR[i, i] = i
    for d in range(1, n):
        cnt = 0
        for i in range(1, n - d + 1):
            j = i + d
            OC[i, j] = INF
            for r in range(OR[i, j - 1], OR[i + 1, j] + 1):
                cnt += 1
                tmp = OC[i, r - 1] + OC[r + 1, j]
                if OC[i, j] > tmp:
                    OC[i, j] = tmp
                    OR[i, j] = r
            OC[i, j] = OC[i, j] + F[i][j]
        if work is not None:
            work[0] += cnt
        if perd is not None:
            perd.append((d, cnt))
    return (OC[1, n] if n >= 1 else 0), OR


ok_fast = ok_root = ok_perd = True
printed_fail = 0
for trial in range(1500):
    n = random.randint(1, 10)
    f = [random.randint(1, random.choice([2, 5, 20])) for _ in range(n)]
    C, Rl, _ = obst(f, "left")
    perd = []
    got, OR = faster_obst(f, perd=perd)
    ok_fast &= (got == C[(1, n)])
    ok_root &= all(OR[i, j] == Rl[(i, j)] for i in range(1, n + 1) for j in range(i, n + 1))
    ok_perd &= all(c <= 2 * n for d, c in perd)
    try:
        if faster_obst_printed(f) != C[(1, n)]:
            printed_fail += 1
    except (Unwritten, IndexError):
        printed_fail += 1
check("D.3: corrected FasterOptimalSearchTree computes the optimal cost (1500 random inputs)", ok_fast)
check("D.3: ... and its strict '>' picks exactly the leftmost optimal root in every subproblem", ok_root)
check("D.3: for each d, the loop over r runs at most 2n times in all (O(n) per diagonal, O(n^2) total)", ok_perd)
check("D.3 note error p. 6: as printed ('for i <- 1 downto n', 'for d <- 0 to n', 'for i <- 1 to n') the algorithm"
      " reads unset entries or leaves the table", printed_fail == 1500, f"{printed_fail} of 1500 fail")
# exact count for one diagonal: sum over i of (R[i+1,j] - R[i,j-1] + 1) = R[n-d+1, n] - R[1, d] + n - d
okexact = True
for trial in range(300):
    n = random.randint(2, 12)
    f = [random.randint(1, 9) for _ in range(n)]
    perd = []
    _, OR = faster_obst(f, perd=perd)
    for d, c in perd:
        okexact &= (c == OR[n - d + 1, n] - OR[1, d] + n - d)
check("D.3: per diagonal d the r-loop runs exactly OptRoot[n-d+1, n] - OptRoot[1, d] + (n - d) times (telescoping)", okexact)
# example on the page: f = [5, 2, 1, 3, 4] (the site's Chapter 3 example)
f5 = [5, 2, 1, 3, 4]
C5, R5, _ = obst(f5)
w5 = [0]
got5, OR5 = faster_obst(f5, work=w5)
roots5 = {(i, j): R5[(i, j)] for i in range(1, 6) for j in range(i, 6)}
check("D.3 example: f = [5,2,1,3,4]: OptCost[1,5] = 31 and the OptRoot table",
      got5 == 31 and roots5 == {(1, 1): 1, (1, 2): 1, (1, 3): 1, (1, 4): 1, (1, 5): 4, (2, 2): 2, (2, 3): 2,
                                 (2, 4): 4, (2, 5): 4, (3, 3): 3, (3, 4): 4, (3, 5): 4, (4, 4): 4, (4, 5): 5,
                                 (5, 5): 5}, str(roots5))
plain5 = sum(j - i + 1 for i in range(1, 6) for j in range(i, 6))
check("D.3 example: the r-loop runs 35 times in the plain O(n^3) program, 30 of them for d >= 1, and 24 times with"
      " Knuth's ranges (d >= 1)", plain5 == 35 and plain5 - 5 == 30 and w5[0] == 24, f"plain {plain5}, Knuth {w5[0]}")

# =====================================================================================================
# D.4 monotone arrays
# =====================================================================================================
random.seed(378)
def LM(M):
    return [min(range(len(row)), key=lambda c: (row[c], c)) for row in M]


def is_monotone(M):
    L = LM(M)
    return all(L[i] <= L[i + 1] for i in range(len(L) - 1))


def is_tm(M):
    m, n = len(M), len(M[0])
    for i in range(m):
        for i2 in range(i + 1, m):
            for j in range(n):
                for j2 in range(j + 1, n):
                    if M[i][j] > M[i][j2] and M[i2][j] <= M[i2][j2]:
                        return False
    return True


def tm_violation(M):
    m, n = len(M), len(M[0])
    for i in range(m):
        for i2 in range(i + 1, m):
            for j in range(n):
                for j2 in range(j + 1, n):
                    if M[i][j] > M[i][j2] and M[i2][j] <= M[i2][j2]:
                        return (i + 1, i2 + 1, j + 1, j2 + 1)
    return None


X1 = [[12, 21, 38, 76, 27], [74, 14, 14, 29, 60], [21, 8, 25, 10, 71], [68, 45, 29, 15, 76], [97, 8, 12, 2, 6]]
X2 = [[12, 21, 38, 76, 89], [47, 14, 14, 29, 60], [21, 8, 20, 10, 71], [68, 16, 29, 15, 76], [97, 8, 12, 2, 6]]
check("D.4 example: the 5x5 array is monotone, leftmost row minima in columns 1,2,2,4,4",
      is_monotone(X1) and [c + 1 for c in LM(X1)] == [1, 2, 2, 4, 4])
check("D.5 example: the same array is not totally monotone; rows 1,3 x columns 3,5 (the gray 2x2) is a violation",
      not is_tm(X1) and X1[0][2] > X1[0][4] and X1[2][2] <= X1[2][4])
viols = [(i + 1, i2 + 1, j + 1, j2 + 1) for i in range(5) for i2 in range(i + 1, 5) for j in range(5)
         for j2 in range(j + 1, 5) if X1[i][j] > X1[i][j2] and X1[i2][j] <= X1[i2][j2]]
check("D.5 example: the first array has 11 violating 2x2 subarrays, the gray one (rows 1,3; columns 3,5) among them",
      len(viols) == 11 and (1, 3, 3, 5) in viols, str(viols))
check("D.5 example: the second array is totally monotone (all 100 2x2 subarrays checked), minima 1,2,2,4,4",
      is_tm(X2) and [c + 1 for c in LM(X2)] == [1, 2, 2, 4, 4])


def rand_monotone(m, n, vmax=9):
    L = sorted(random.randrange(n) for _ in range(m))
    M = []
    for i in range(m):
        v = random.randint(0, vmax)
        row = [random.randint(v + 1, v + 1 + vmax) if c < L[i] else random.randint(v, v + vmax) for c in range(n)]
        row[L[i]] = v
        M.append(row)
    return M


def rand_monge(m, n, terms=None, vmax=5):
    """Monge: r_i + c_j + sum of lambda * [i <= a, j >= b] (upper-right blocks), lambda >= 0."""
    r = [random.randint(-vmax, vmax) for _ in range(m)]
    c = [random.randint(-vmax, vmax) for _ in range(n)]
    M = [[r[i] + c[j] for j in range(n)] for i in range(m)]
    for _ in range(terms if terms is not None else random.randint(0, m + n)):
        a, b, lam = random.randrange(m), random.randrange(n), random.randint(1, 3)
        for i in range(a + 1):
            for j in range(b, n):
                M[i][j] += lam
    return M


def is_monge(M):
    m, n = len(M), len(M[0])
    return all(M[i][j] + M[i2][j2] <= M[i][j2] + M[i2][j]
               for i in range(m) for i2 in range(i + 1, m) for j in range(n) for j2 in range(j + 1, n))


def is_monge_local(M):
    m, n = len(M), len(M[0])
    return all(M[i][j] + M[i + 1][j + 1] <= M[i][j + 1] + M[i + 1][j] for i in range(m - 1) for j in range(n - 1))


def even_odd(M, rows=None, cnt=None, levels=None, depth=0):
    """The note's 'recursively compute the odd rows, then fill the even rows' algorithm (p. 7-8).
    rows: list of row indices (0-based positions in M); returns dict row -> leftmost min column."""
    if rows is None:
        rows = list(range(len(M)))
    n = len(M[0])
    if not rows:
        return {}
    if len(rows) == 1:
        r = rows[0]
        if cnt is not None:
            cnt[0] += n - 1
        if levels is not None:
            levels[depth] = levels.get(depth, 0) + n - 1
        return {r: min(range(n), key=lambda c: (M[r][c], c))}
    odd = rows[0::2]  # 1st, 3rd, 5th ... rows of this subproblem (1-indexed odd)
    res = even_odd(M, odd, cnt, levels, depth + 1)
    for k in range(1, len(rows), 2):
        lo = res[rows[k - 1]]
        hi = res[rows[k + 1]] if k + 1 < len(rows) else n - 1
        r = rows[k]
        best = min(range(lo, hi + 1), key=lambda c: (M[r][c], c))
        if cnt is not None:
            cnt[0] += hi - lo
        if levels is not None:
            levels[depth] = levels.get(depth, 0) + hi - lo
        res[r] = best
    return res


def dandc(M, r0, r1, c0, c1, cnt=None, seen=None, levels=None, depth=0):
    """The note's divide and conquer (p. 8): middle row by brute force, recurse on the two corner subarrays."""
    if r0 > r1:
        return {}
    mid = (r0 + r1) // 2
    h = min(range(c0, c1 + 1), key=lambda c: (M[mid][c], c))
    if cnt is not None:
        cnt[0] += c1 - c0
    if levels is not None:
        levels[depth] = levels.get(depth, 0) + c1 - c0
    if seen is not None:
        seen.update((mid, c) for c in range(c0, c1 + 1))
    res = {mid: h}
    res.update(dandc(M, r0, mid - 1, c0, h, cnt, seen, levels, depth + 1))
    res.update(dandc(M, mid + 1, r1, h, c1, cnt, seen, levels, depth + 1))
    return res


ok_eo = ok_dc = ok_eo_cnt = ok_dc_cnt = ok_levels = True
for trial in range(2000):
    m, n = random.randint(1, 20), random.randint(1, 20)
    M = rand_monotone(m, n) if trial % 2 else rand_monge(m, n)
    if not is_monotone(M):
        continue
    truth = LM(M)
    c1 = [0]
    lv = {}
    r1 = even_odd(M, cnt=c1, levels=lv)
    ok_eo &= ([r1[i] for i in range(m)] == truth)
    ok_levels &= all(v <= n - 1 for v in lv.values()) and len(lv) <= math.ceil(math.log2(m)) + 1
    ok_eo_cnt &= (c1[0] <= (n - 1) * (math.ceil(math.log2(m)) + 1))
    c2 = [0]
    lv2 = {}
    r2 = dandc(M, 0, m - 1, 0, n - 1, cnt=c2, levels=lv2)
    ok_dc &= ([r2[i] for i in range(m)] == truth)
    ok_dc_cnt &= all(v <= n - 1 + 2 ** d for d, v in lv2.items())
check("D.4: even-odd algorithm finds every leftmost row minimum of random monotone arrays (up to 20 x 20)", ok_eo)
check("D.4: even-odd: at most n - 1 comparisons per level and at most ceil(log2 m) + 1 levels: O(m + n log m)",
      ok_levels and ok_eo_cnt)
check("D.4: divide and conquer (middle row first) is correct", ok_dc)
check("D.4: divide and conquer: comparisons on level d <= n - 1 + 2^d (the shared boundary columns)", ok_dc_cnt)

# 'morally identical': same examined entries? compare the comparisons made
same_sets = []
for m in [3, 7, 15]:
    n = 12
    M = rand_monotone(m, n)
    seen_dc = set()
    dandc(M, 0, m - 1, 0, n - 1, seen=seen_dc)

    def eo_seen(rows, M=M):
        n = len(M[0])
        if len(rows) == 1:
            r = rows[0]
            return {(r, c) for c in range(n)}, {r: min(range(n), key=lambda c: (M[r][c], c))}
        odd = rows[0::2]
        s, res = eo_seen(odd)
        for k in range(1, len(rows), 2):
            lo = res[rows[k - 1]]
            hi = res[rows[k + 1]] if k + 1 < len(rows) else n - 1
            s |= {(rows[k], c) for c in range(lo, hi + 1)}
            res[rows[k]] = min(range(lo, hi + 1), key=lambda c: (M[rows[k]][c], c))
        return s, res

    def ee_seen(rows, M=M):
        """Variant recursing on the EVEN rows (2nd, 4th, ...) and filling the odd ones."""
        n = len(M[0])
        if len(rows) == 1:
            r = rows[0]
            return {(r, c) for c in range(n)}, {r: min(range(n), key=lambda c: (M[r][c], c))}
        ev = rows[1::2]
        s, res = ee_seen(ev)
        for k in range(0, len(rows), 2):
            lo = res[rows[k - 1]] if k - 1 >= 0 else 0
            hi = res[rows[k + 1]] if k + 1 < len(rows) else n - 1
            s |= {(rows[k], c) for c in range(lo, hi + 1)}
            res[rows[k]] = min(range(lo, hi + 1), key=lambda c: (M[rows[k]][c], c))
        return s, res

    s_odd, _ = eo_seen(list(range(m)))
    s_even, _ = ee_seen(list(range(m)))
    same_sets.append((m, s_odd == seen_dc, s_even == seen_dc))
check("D.4: for m = 2^k - 1, divide and conquer examines exactly the entries of the variant that recurses on the "
      "EVEN rows; the printed odd-row version examines a different set", all(not a and b for _, a, b in same_sets),
      str(same_sets))

# D.4: the OBST array M[i, r] for a fixed d is monotone (its leftmost minima are the leftmost optimal roots)
ok_obstM = True
for trial in range(300):
    n = random.randint(2, 9)
    f = [random.randint(1, 6) for _ in range(n)]
    C, Rl, _ = obst(f)
    for d in range(0, n):
        rows = []
        for i in range(1, n - d + 1):
            rows.append([C[(i, r - 1)] + C[(r + 1, i + d)] if i <= r <= i + d else INF for r in range(1, n + 1)])
        L = LM(rows)
        ok_obstM &= all(L[k] + 1 == Rl[(k + 1, k + 1 + d)] for k in range(len(rows))) and is_monotone(rows)
check("D.4: for each d, the array M[i, r] = OptCost[i, r-1] + OptCost[r+1, i+d] (inf outside i..i+d) is monotone"
      " and its leftmost row minima are the optimal roots", ok_obstM)

# =====================================================================================================
# D.5 Monge arrays
# =====================================================================================================
random.seed(379)
ok_m_tm = ok_local = True
local_tests = 0
for trial in range(1500):
    m, n = random.randint(1, 7), random.randint(1, 7)
    M = rand_monge(m, n)
    ok_m_tm &= is_monge(M) and is_tm(M)
    # local condition <=> Monge, on arbitrary small arrays and on perturbed Monge arrays
    N = [[random.randint(0, 3) for _ in range(n)] for _ in range(m)] if trial % 2 else \
        [[x + (random.random() < 0.1) * random.choice([-1, 1]) for x in row] for row in rand_monge(m, n)]
    local_tests += 1
    ok_local &= (is_monge(N) == is_monge_local(N))
check("D.5: every (random) Monge array is totally monotone", ok_m_tm)
check("D.5: Monge iff the local condition M[i,j] + M[i+1,j+1] <= M[i,j+1] + M[i+1,j] (1500 random arrays)", ok_local)

# geometric example
ok_geo = ok_cross = True
for trial in range(500):
    m, n = random.randint(2, 7), random.randint(2, 7)
    P = sorted(random.uniform(0, 10) for _ in range(m))
    Qx = sorted(random.uniform(0, 10) for _ in range(n))
    hgt = random.uniform(0.1, 5)
    D = [[math.hypot(P[i] - Qx[j], hgt) for j in range(n)] for i in range(m)]
    ok_geo &= all(D[i][j] + D[i2][j2] <= D[i][j2] + D[i2][j] + 1e-9
                  for i in range(m) for i2 in range(i + 1, m) for j in range(n) for j2 in range(j + 1, n))
    # segments p_i q_j' and p_i' q_j cross (both x-orders reversed between the two lines)
    for i in range(m):
        for i2 in range(i + 1, m):
            for j in range(n):
                for j2 in range(j + 1, n):
                    # param t where x-coordinates coincide: (P[i] + t (Q[j2] - P[i])) = (P[i2] + t (Q[j] - P[i2]))
                    den = (Qx[j2] - P[i]) - (Qx[j] - P[i2])
                    t = (P[i2] - P[i]) / den if den else None
                    if den and not (-1e-12 <= t <= 1 + 1e-12):
                        ok_cross = False
check("D.5: distances between ordered points on two parallel lines form a Monge array (500 random instances)", ok_geo)
check("D.5: the segments p_i q_j' and p_i' q_j always meet (the point x of the proof exists)", ok_cross)


def blk(m, n, r0, r1, c0, c1):
    return [[1 if (r0 <= i <= r1 and c0 <= j <= c1) else 0 for j in range(n)] for i in range(m)]


ok_parts = True
for trial in range(300):
    m, n = random.randint(2, 6), random.randint(2, 6)
    rr = [random.randint(-5, 5) for _ in range(m)]
    cc = [random.randint(-5, 5) for _ in range(n)]
    a, b = random.randrange(m), random.randrange(n)
    X, Y = rand_monge(m, n), rand_monge(m, n)
    lam = random.randint(1, 5)
    ok_parts &= is_monge([[rr[i]] * n for i in range(m)])  # (a)
    ok_parts &= is_monge([cc[:] for _ in range(m)])  # (b)
    ok_parts &= is_monge(blk(m, n, 0, a, b, n - 1))  # (c) upper-right block
    ok_parts &= is_monge(blk(m, n, a, m - 1, 0, b))  # (d) lower-left block
    ok_parts &= is_monge([[lam * x for x in row] for row in X])  # (e)
    ok_parts &= is_monge([[X[i][j] + Y[i][j] for j in range(n)] for i in range(m)])  # (f)
    ok_parts &= is_monge([list(col) for col in zip(*X)])  # (g)
check("D.5: lemma (a)-(g): row-constant, column-constant, upper-right and lower-left corner blocks, positive"
      " multiples, sums and transposes are Monge", ok_parts)
check("D.5: a block of 1s that does not touch the upper-right (or lower-left) corner need not be Monge",
      not is_monge(blk(3, 3, 1, 1, 1, 1)) and not is_monge(blk(3, 3, 0, 0, 0, 0)))
check("D.5: an upper-LEFT corner block of 1s is not Monge", not is_monge(blk(3, 3, 0, 1, 0, 1)))

# characterization: every Monge array = r_i + c_j + sum_{a,b} lambda_{a,b} [i <= a, j >= b] with lambda >= 0
ok_char = True
for trial in range(400):
    m, n = random.randint(1, 6), random.randint(1, 6)
    if trial % 2:
        M = rand_monge(m, n)
    else:  # geometric (irrational) Monge arrays, exact up to rounding: use Fractions of rounded floats
        P = sorted(random.uniform(0, 10) for _ in range(m))
        Qx = sorted(random.uniform(0, 10) for _ in range(n))
        M = [[Fraction(round(math.hypot(P[i] - Qx[j], 1.0) * 10 ** 6)) for j in range(n)] for i in range(m)]
        if not is_monge(M):
            continue
    lam = {}
    for a in range(m - 1):
        for b in range(1, n):
            lam[(a, b)] = M[a][b] + M[a + 1][b - 1] - M[a][b - 1] - M[a + 1][b]
    if any(v < 0 for v in lam.values()):
        ok_char = False
        continue
    R = [[M[i][j] - sum(v for (a, b), v in lam.items() if i <= a and j >= b) for j in range(n)] for i in range(m)]
    # remainder must be r_i + c_j
    ok_char &= all(R[i][j] - R[i][0] - R[0][j] + R[0][0] == 0 for i in range(m) for j in range(n))
check("D.5: characterization: every Monge array decomposes as row-constant + column-constant + a non-negative"
      " combination of upper-right blocks (400 random arrays, exact arithmetic)", ok_char)

# =====================================================================================================
# D.6 SMAWK
# =====================================================================================================
random.seed(380)
ok_obs = True
for trial in range(400):
    m, n = random.randint(1, 7), random.randint(2, 7)
    M = rand_monge(m, n)
    L = LM(M)
    for i in range(m):
        for p in range(n):
            for q in range(p + 1, n):
                if M[i][p] <= M[i][q]:
                    ok_obs &= all(M[h][p] <= M[h][q] and L[h] != q for h in range(i + 1))
                else:
                    ok_obs &= all(M[j][p] > M[j][q] and L[j] != p for j in range(i, m))
check("D.6: the two observations (compare M[i,p] and M[i,q]: the right entry and everything above it, or the left"
      " entry and everything below it, is dead) hold on random totally monotone arrays", ok_obs)


def reduce_printed(M, rows, cols, cnt=None):
    """Reduce exactly as printed (p. 12): t <- 1, S[1] <- first column, k over ALL columns, pop while >=."""
    m = len(rows)
    S = [None] * (m + 1)
    t = 1
    S[1] = cols[0]
    for k in cols:
        while t > 0:
            if cnt is not None:
                cnt[0] += 1
            if M[rows[t - 1]][S[t]] >= M[rows[t - 1]][k]:
                t -= 1
            else:
                break
        if t < m:
            t += 1
            S[t] = k
    return S[1:t + 1]


def reduce_fixed(M, rows, cols, cnt=None, inv=None):
    """Corrected: start with the first column on the stack, k over the remaining columns, pop while >."""
    m = len(rows)
    S = [None] * (m + 1)
    t = 1
    S[1] = cols[0]
    for kk, k in enumerate(cols[1:], start=1):
        if inv is not None:
            inv(S[1:t + 1], cols[:kk], k)
        while t > 0:
            if cnt is not None:
                cnt[0] += 1
            if M[rows[t - 1]][S[t]] > M[rows[t - 1]][k]:
                t -= 1
            else:
                break
        if t < m:
            t += 1
            S[t] = k
    return S[1:t + 1]


ok_red = ok_red_cnt = ok_inv = True
printed_ties_bad = printed_distinct_bad = n_tied = 0
for trial in range(3000):
    m, n = random.randint(1, 8), random.randint(1, 16)
    M = rand_monge(m, n, vmax=2 if trial % 2 else 50)
    rows, cols = list(range(m)), list(range(n))
    L = LM(M)
    c = [0]

    def inv(stack, done, k, M=M, L=L, m=m):
        global ok_inv
        ok_inv &= all(stack[x] < stack[x + 1] for x in range(len(stack) - 1))
        for jpos, col in enumerate(stack, start=1):  # top jpos-1 entries of column S[jpos] dead
            ok_inv &= all(L[r] != col for r in range(min(jpos - 1, m)))
        for col in done:
            if col not in stack:
                ok_inv &= all(L[r] != col for r in range(m))

    S = reduce_fixed(M, rows, cols, cnt=c, inv=inv)
    ok_red &= set(L) <= set(S) and len(S) <= m
    ok_red_cnt &= c[0] <= 2 * n
    Sp = reduce_printed(M, rows, cols)
    distinct = all(len(set(row)) == n for row in M)
    n_tied += not distinct
    if not set(L) <= set(Sp):
        if distinct:
            printed_distinct_bad += 1
        else:
            printed_ties_bad += 1
check("D.6: corrected Reduce keeps every column that holds a leftmost row minimum, and at most m columns", ok_red)
check("D.6: Reduce makes at most 2n comparisons", ok_red_cnt)
check("D.6: Reduce's three invariants hold before every step (sorted stack; top j-1 entries of S[j] dead; columns"
      " left behind are dead)", ok_inv)
check("D.6 note error p. 12: Reduce as printed (pop on >=) can discard a column holding a leftmost minimum when a row"
      " has ties", printed_ties_bad > 0, f"{printed_ties_bad} failures among {n_tied} arrays with ties (3000 arrays)")
check("D.6: ... but never when the entries of each row are distinct", printed_distinct_bad == 0)
check("D.6 note error p. 12: smallest failure [[1,1],[0,5]]: printed Reduce keeps only column 2, but LM = (1, 1)",
      reduce_printed([[1, 1], [0, 5]], [0, 1], [0, 1]) == [1] and LM([[1, 1], [0, 5]]) == [0, 0]
      and is_tm([[1, 1], [0, 5]]))


def smawk(M, rows, cols, cnt):
    """SMAWK as described on pp. 11-14: Reduce if wider than tall, recurse on every other row, fill in the rest."""
    if not rows:
        return {}
    if len(cols) > len(rows):
        cols = reduce_fixed(M, rows, cols, cnt=cnt)
    sub = smawk(M, rows[1::2], cols, cnt)
    res = dict(sub)
    pos = {c: x for x, c in enumerate(cols)}
    for k in range(0, len(rows), 2):
        lo = pos[res[rows[k - 1]]] if k - 1 >= 0 else 0
        hi = pos[res[rows[k + 1]]] if k + 1 < len(rows) else len(cols) - 1
        best = cols[lo]
        for x in range(lo + 1, hi + 1):
            cnt[0] += 1
            if M[rows[k]][cols[x]] < M[rows[k]][best]:
                best = cols[x]
        res[rows[k]] = best
    return res


ok_smawk = True
worst = 0
for trial in range(2000):
    m, n = random.randint(1, 30), random.randint(1, 60)
    M = rand_monge(m, n, vmax=3 if trial % 3 == 0 else 100)
    c = [0]
    r = smawk(M, list(range(m)), list(range(n)), c)
    ok_smawk &= [r[i] for i in range(m)] == LM(M)
    worst = max(worst, c[0] / (m + n))
check("D.6: SMAWK finds every leftmost row minimum of random totally monotone (Monge) arrays up to 30 x 60", ok_smawk)
big = []
for m, n in [(100, 100), (200, 50), (50, 400), (400, 400), (1000, 1000)]:
    M = rand_monge(m, n, terms=3 * (m + n), vmax=1000)
    c = [0]
    r = smawk(M, list(range(m)), list(range(n)), c)
    big.append(round(c[0] / (m + n), 2))
    ok_smawk &= [r[i] for i in range(m)] == LM(M)
check("D.6: SMAWK makes at most 2.2 (m + n) comparisons (O(m + n)); random arrays up to 1000 x 1000",
      max(big + [worst]) <= 2.2, f"small max {worst:.2f}; large {big}")

# =====================================================================================================
# D.7 Using SMAWK: Bellman-Ford on the complete bipartite Euclidean graph
# =====================================================================================================
random.seed(381)
def dijkstra(adj, s, V):
    dist = {v: INF for v in V}
    dist[s] = 0
    pq = [(0, s)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for v, w in adj[u]:
            if d + w < dist[v]:
                dist[v] = d + w
                heapq.heappush(pq, (d + w, v))
    return dist


def rowmin_smawk(Mfun, m, n, cnt):
    class Lazy:
        def __getitem__(self, i):
            class Row:
                def __getitem__(_, j):
                    cnt[0] += 1
                    return Mfun(i, j)
            return Row()
    lz = Lazy()
    c = [0]
    r = smawk(lz, list(range(m)), list(range(n)), c)
    return [Mfun(i, r[i]) for i in range(m)]


ok_bf = ok_mod = ok_sm = ok_blocks = True
evals = []
for trial in range(60):
    n = random.randint(2, 12)
    P = sorted(random.uniform(0, 10) for _ in range(n))
    Qx = sorted(random.uniform(0, 10) for _ in range(n))
    gap = random.uniform(0.5, 3)
    D = [[math.hypot(P[i] - Qx[j], gap) for j in range(n)] for i in range(n)]
    V = [("p", i) for i in range(n)] + [("q", j) for j in range(n)]
    adj = {v: [] for v in V}
    for i in range(n):
        for j in range(n):
            adj[("p", i)].append((("q", j), D[i][j]))
            adj[("q", j)].append((("p", i), D[i][j]))
    s = random.choice(V)
    truth = dijkstra(adj, s, V)
    # standard Bellman-Ford
    dist = {v: INF for v in V}
    dist[s] = 0
    for _ in range(len(V) - 1):
        for u in V:
            for v, w in adj[u]:
                if dist[v] > dist[u] + w:
                    dist[v] = dist[u] + w
    ok_bf &= all(abs(dist[v] - truth[v]) < 1e-9 for v in V)
    # ModBellmanFord with naive row minima
    dist = {v: INF for v in V}
    dist[s] = 0
    for _ in range(len(V) - 1):
        mind = {v: min(dist[u] + w for u, w in adj[v]) for v in V}
        for v in V:
            dist[v] = min(dist[v], mind[v])
    ok_mod &= all(abs(dist[v] - truth[v]) < 1e-9 for v in V)
    # SMAWK version: U[i,j] = dist(q_j) + |p_i q_j| (rows p_i), V[i,j] = dist(p_j) + |p_j q_i| (rows q_i)
    dist = {v: INF for v in V}
    dist[s] = 0
    c = [0]
    for rnd in range(len(V) - 1):
        dq = [dist[("q", j)] for j in range(n)]
        dp = [dist[("p", j)] for j in range(n)]
        BIG = 10 ** 6
        Uf = lambda i, j: (dq[j] if dq[j] < INF else BIG) + D[i][j]  # noqa: E731
        Vf = lambda i, j: (dp[j] if dp[j] < INF else BIG) + D[j][i]  # noqa: E731
        if rnd < 3:
            Um = [[Uf(i, j) for j in range(n)] for i in range(n)]
            Vm = [[Vf(i, j) for j in range(n)] for i in range(n)]
            ok_blocks &= all(Um[i][j] + Um[i2][j2] <= Um[i][j2] + Um[i2][j] + 1e-7
                             for i in range(n) for i2 in range(i + 1, n) for j in range(n) for j2 in range(j + 1, n))
            ok_blocks &= all(Vm[i][j] + Vm[i2][j2] <= Vm[i][j2] + Vm[i2][j] + 1e-7
                             for i in range(n) for i2 in range(i + 1, n) for j in range(n) for j2 in range(j + 1, n))
        before = c[0]
        mp = rowmin_smawk(Uf, n, n, c)
        mq = rowmin_smawk(Vf, n, n, c)
        evals.append((c[0] - before) / n)
        for i in range(n):
            if mp[i] < BIG / 2:
                dist[("p", i)] = min(dist[("p", i)], mp[i])
            if mq[i] < BIG / 2:
                dist[("q", i)] = min(dist[("q", i)], mq[i])
    ok_sm &= all(abs(dist[v] - truth[v]) < 1e-9 for v in V)
check("D.7: Bellman-Ford on the complete bipartite Euclidean graph matches Dijkstra (60 random instances)", ok_bf)
check("D.7: ModBellmanFord (row minima of M[v,u] = dist(u) + w(u->v), then dist <- min) matches", ok_mod)
check("D.7: the blocks U = Q + D and V = P + D^T are Monge in every round (inf replaced by a large constant)",
      ok_blocks)
growth = []
for n in [50, 200, 800]:
    P = sorted(random.uniform(0, 10) for _ in range(n))
    Qx = sorted(random.uniform(0, 10) for _ in range(n))
    D = [[math.hypot(P[i] - Qx[j], 1.0) for j in range(n)] for i in range(n)]
    dq = [random.uniform(0, 20) for _ in range(n)]
    c = [0]
    got = rowmin_smawk(lambda i, j: dq[j] + D[i][j], n, n, c)
    ok_sm &= all(abs(got[i] - min(dq[j] + D[i][j] for j in range(n))) < 1e-12 for i in range(n))
    growth.append(round(c[0] / n, 2))
check("D.7: SMAWK-based ModBellmanFord matches Dijkstra; entries evaluated per block / n stays bounded (O(n) per"
      " round, O(n^2) total)", ok_sm and max(evals) <= 16 and max(growth) <= 8,
      f"small n: max {max(evals) / 2:.2f} per block per n; n = 50, 200, 800: {growth}")

# ModBellmanFord's dist after k rounds = shortest walk from s with at most k edges (enumerated)
ok_rounds = True
for trial in range(40):
    n = random.randint(1, 3)
    P = sorted(random.uniform(0, 10) for _ in range(n))
    Qx = sorted(random.uniform(0, 10) for _ in range(n))
    D = [[math.hypot(P[i] - Qx[j], 1.0) for j in range(n)] for i in range(n)]
    V = [("p", i) for i in range(n)] + [("q", j) for j in range(n)]
    adj = {v: [] for v in V}
    for i in range(n):
        for j in range(n):
            adj[("p", i)].append((("q", j), D[i][j]))
            adj[("q", j)].append((("p", i), D[i][j]))
    s = V[0]
    dist = {v: INF for v in V}
    dist[s] = 0
    for k in range(1, len(V)):
        mind = {v: min(dist[u] + w for u, w in adj[v]) for v in V}
        for v in V:
            dist[v] = min(dist[v], mind[v])
        best = {v: INF for v in V}
        best[s] = 0
        walks = [(s, 0.0)]
        for _ in range(k):
            walks = [(v, c + w) for (u, c) in walks for v, w in adj[u]]
            for v, c in walks:
                best[v] = min(best[v], c)
        ok_rounds &= all(abs(dist[v] - best[v]) < 1e-9 or dist[v] == best[v] == INF for v in V)
check("D.7: after k rounds, ModBellmanFord's dist(v) = length of the shortest walk from s to v with at most k edges",
      ok_rounds)

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: {FAIL}")
sys.exit(1 if FAIL else 0)
