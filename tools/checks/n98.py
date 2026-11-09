#!/usr/bin/env python3
"""Checks for content/4-lecture-notes/98-proof-by-induction.md (Erickson, Appendix I, Proof by Induction) and the
concept page content/concepts/strong-induction.md.

Every theorem of the note with a computable statement is checked on all small cases; every proof that is really an
algorithm (factoring, postage, triomino tilings, the four binary-representation proofs, the leaf-finding walk) is
implemented as the page states it and its output validated; every number in the note's examples (including the
exercises' examples) is recomputed; the "build-up" non-proof gets a concrete false claim that the same pattern
"proves"; and the note's errors are confirmed (a wrong cross-reference, a circular hypothesis, an off-by-one, miscomputed
exercise examples, a false exercise)."""
import itertools
import math
import random
import sys
from fractions import Fraction

import networkx as nx

sys.setrecursionlimit(100000)
FAIL = []


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAIL.append(name)


rng = random.Random(98)


def divisors(n):
    return [d for d in range(1, n + 1) if n % d == 0]


def is_prime(n):
    return n >= 2 and all(n % d for d in range(2, int(n ** 0.5) + 1))


# =====================================================================================================
# §1 Prime divisors
# =====================================================================================================
check("1 has exactly one divisor (neither prime nor composite)", divisors(1) == [1])
check("prime <=> exactly two divisors <=> 1 is the only proper divisor, n <= 500",
      all(is_prime(n) == (len(divisors(n)) == 2) == (n > 1 and [d for d in divisors(n) if d < n] == [1])
          for n in range(1, 501)))
check("composite <=> more than one proper divisor, 2 <= n <= 500",
      all((len(divisors(n)) > 2) == (len([d for d in divisors(n) if d < n]) > 1) for n in range(2, 501)))


def prime_divisor(n):
    """The induction proof of Theorem 1 as a recursive algorithm: n prime -> n; else recurse on a proper divisor d."""
    if is_prime(n):
        return n
    d = next(d for d in range(2, n) if n % d == 0)       # any divisor with 1 < d < n
    assert 1 < d < n
    return prime_divisor(d)                                # the induction hypothesis, applied to d < n


ok = True
for n in range(2, 20001):
    p = prime_divisor(n)
    ok &= is_prime(p) and n % p == 0
check("Theorem 1: the proof's recursion returns a prime divisor of n, 2 <= n <= 20000", ok)
# the transitivity step: d | n and p | d  =>  p | n  (n/p = (n/d)(d/p))
check("n/p = (n/d)*(d/p) is an integer whenever d | n and p | d (n <= 300)",
      all((n // d) * (d // p) * p == n for n in range(2, 301) for d in divisors(n) for p in divisors(d)))

# =====================================================================================================
# §2 Well-ordering and the axiom of induction (finite truth tables)
# =====================================================================================================
N = 12
ok_ax, ok_wo, ok_eq = True, True, True
for bits in range(1 << N):
    P = [None] + [(bits >> (i - 1)) & 1 == 1 for i in range(1, N + 1)]
    step_all = all((not all(P[1:n])) or P[n] for n in range(1, N + 1))      # (P1 ^ ... ^ P(n-1)) -> P(n)
    ok_ax &= (not step_all) or all(P[1:])
    some_false = not all(P[1:])
    smallest_cex = any(all(P[1:n]) and not P[n] for n in range(1, N + 1))
    ok_wo &= (not some_false) or smallest_cex
    ok_eq &= step_all == (not smallest_cex)
check(f"axiom of induction holds for all 2^{N} predicates on 1..{N}", ok_ax)
check(f"well-ordering: some counterexample => a smallest one, all 2^{N} predicates", ok_wo)
check("'every n: hypothesis -> P(n)' <=> 'no smallest counterexample' (same predicates)", ok_eq)
check("not(p and not q) == (p -> q) for all truth values",
      all((not (p and not q)) == ((not p) or q) for p in (0, 1) for q in (0, 1)))


# =====================================================================================================
# §3 Stamps
# =====================================================================================================
def makeable(n, coins):
    can = [True] + [False] * n
    for v in range(1, n + 1):
        can[v] = any(v >= c and can[v - c] for c in coins)
    return can


can = makeable(2000, (5, 7))
check("Theorem 2: every amount 24..2000 is a sum of 5s and 7s", all(can[n] for n in range(24, 2001)))
check("23 cents cannot be made (the threshold is sharp; 23 = 5*7 - 5 - 7)", not can[23] and 5 * 7 - 5 - 7 == 23)
check("non-makeable amounts are 1,2,3,4,6,8,9,11,13,16,18,23",
      [n for n in range(1, 30) if not can[n]] == [1, 2, 3, 4, 6, 8, 9, 11, 13, 16, 18, 23])
base = {24: [7, 7, 5, 5], 25: [5] * 5, 26: [7, 7, 7, 5], 27: [7, 5, 5, 5, 5], 28: [7, 7, 7, 7]}
check("the five base cases 24..28 as printed", all(sum(v) == k and set(v) <= {5, 7} for k, v in base.items()))
scheme = {24: [5, 5, 7, 7], 25: [5] * 5, 26: [5, 7, 7, 7], 27: [5, 5, 5, 5, 7], 28: [7] * 4}
check("the Scheme program's base-case lists", all(sum(v) == k for k, v in scheme.items()))
check("for n > 28: 23 < n - 5 < n (the inductive case applies)", all(23 < n - 5 < n for n in range(29, 2001)))


def postage(n):
    assert n > 23
    if n <= 28:
        return list(base[n])
    return postage(n - 5) + [5]


check("Postage(n) returns 5s and 7s summing to n, 24 <= n <= 1000",
      all(sum(postage(n)) == n and set(postage(n)) <= {5, 7} for n in range(24, 1001)))
check("five consecutive base cases are needed: a step of 5 from 24..28 reaches every n >= 24",
      sorted({b + 5 * k for b in range(24, 29) for k in range(200)} & set(range(24, 1000))) == list(range(24, 1000)))


def postage_calls(n):
    return 1 if n <= 28 else 1 + postage_calls(n - 5)


check("Postage(n) makes floor((n-24)/5) + 1 calls, 24 <= n <= 1000",
      all(postage_calls(n) == (n - 24) // 5 + 1 for n in range(24, 1001)))
check("four base cases 24..27 would not do: n = 28 + 5k is never reached",
      not ({b + 5 * k for b in range(24, 28) for k in range(200)} >= set(range(24, 1000))))


# =====================================================================================================
# §4 Products of primes
# =====================================================================================================
def factor_a(n):
    """Proof 1: n = 1 -> empty product; n >= 2 -> a prime divisor p and recurse on n/p."""
    if n == 1:
        return []
    p = prime_divisor(n)
    return factor_a(n // p) + [p]


def factor_b(n):
    """Proof 2: 1 -> empty; prime -> [n]; composite -> any proper divisor d > 1, recurse on d and n/d."""
    if n == 1:
        return []
    if is_prime(n):
        return [n]
    d = next(d for d in range(2, n) if n % d == 0)
    m = n // d
    assert 1 <= d < n and 1 <= m < n
    return factor_b(d) + factor_b(m)


check("Theorem 3, proof 1: n is the product of the primes returned, 1 <= n <= 5000",
      all(math.prod(factor_a(n)) == n and all(map(is_prime, factor_a(n))) for n in range(1, 5001)))
check("Theorem 3, proof 2: same, 1 <= n <= 5000",
      all(math.prod(factor_b(n)) == n and all(map(is_prime, factor_b(n))) for n in range(1, 5001)))
check("the two proofs give the same multiset of primes (uniqueness is not claimed, but it holds)",
      all(sorted(factor_a(n)) == sorted(factor_b(n)) for n in range(1, 3001)))
check("1 is the empty product", math.prod([]) == 1)
# pp. 4 and 10: "a/any proper divisor d" must be d > 1 -- by the note's definition 1 is a proper divisor of every n >= 2
check("1 is a proper divisor of every n >= 2, has no prime divisor, and d = 1 gives m = n/d = n, not < n (pp. 4, 10)",
      all(1 in [d for d in divisors(n) if d < n] and n // 1 == n for n in range(2, 501))
      and not any(is_prime(p) for p in divisors(1)))
check("every proper divisor d > 1 of a composite n has 1 < d < n and 1 < n/d < n (n <= 500)",
      all(1 < d < n and 1 < n // d < n for n in range(4, 501) if not is_prime(n)
          for d in divisors(n) if 1 < d < n))

# =====================================================================================================
# §5 Summations
# =====================================================================================================
check("Theorem 4: sum_{i=0}^n 3^i = (3^{n+1}-1)/2, 0 <= n <= 300",
      all(sum(3 ** i for i in range(n + 1)) * 2 == 3 ** (n + 1) - 1 for n in range(301)))
check("n = 0: sum = 3^0 = 1 = (3^1-1)/2", 3 ** 0 == 1 == (3 ** 1 - 1) // 2)
check("inductive step 1: (3^n-1)/2 + 3^n = (3^{n+1}-1)/2, n <= 300",
      all(Fraction(3 ** n - 1, 2) + 3 ** n == Fraction(3 ** (n + 1) - 1, 2) for n in range(1, 301)))
check("inductive step 2: 3^0 + 3*(3^n-1)/2 = (3^{n+1}-1)/2, n <= 300",
      all(1 + 3 * Fraction(3 ** n - 1, 2) == Fraction(3 ** (n + 1) - 1, 2) for n in range(1, 301)))
check("sum_{i=0}^n 3^i = 3^0 + 3 * sum_{i=0}^{n-1} 3^i, n <= 100",
      all(sum(3 ** i for i in range(n + 1)) == 1 + 3 * sum(3 ** i for i in range(n)) for n in range(1, 101)))


# =====================================================================================================
# §6 Triomino tilings
# =====================================================================================================
def tile_topdown(n, hole, r0=0, c0=0, out=None, calls=None):
    """Tile the 2^n x 2^n board with top-left corner (r0, c0) minus square `hole`.
    Returns a list of triominos (each a frozenset of 3 cells)."""
    if out is None:
        out = []
    if calls is not None:
        calls[0] += 1
    if n == 0:
        return out
    h = 1 << (n - 1)
    quads = [(r0, c0), (r0, c0 + h), (r0 + h, c0), (r0 + h, c0 + h)]
    centre = [(r0 + h - 1, c0 + h - 1), (r0 + h - 1, c0 + h), (r0 + h, c0 + h - 1), (r0 + h, c0 + h)]
    holes, tri = [], []
    for (qr, qc), cc in zip(quads, centre):
        if qr <= hole[0] < qr + h and qc <= hole[1] < qc + h:
            holes.append(hole)
        else:
            holes.append(cc)
            tri.append(cc)
    assert len(tri) == 3
    out.append(frozenset(tri))
    for (qr, qc), hh in zip(quads, holes):
        tile_topdown(n - 1, hh, qr, qc, out, calls)
    return out


def tile_bottomup(n, hole):
    """Cluster into 2x2 blocks, tile the 2^(n-1) board of blocks minus the hole's block with (double-size)
    triominos, split each double-size triomino into four, and add the hole's block minus the hole."""
    if n == 0:
        return []
    coarse = tile_bottomup(n - 1, (hole[0] // 2, hole[1] // 2))
    out = []
    for T in coarse:
        # a double-size triomino = 3 blocks in an L; its 12 cells are tiled by 4 triominos:
        # the corner block of the L minus its inner cell... use the standard split: one triomino at the
        # L's inner corner and one in each block minus the cell it gives to that triomino.
        blocks = sorted(T)
        rs = [b[0] for b in blocks]
        cs = [b[1] for b in blocks]
        br, bc = min(rs), min(cs)                       # the 2x2 bounding box of the L (in block coordinates)
        missing = [(br + i, bc + j) for i in (0, 1) for j in (0, 1) if (br + i, bc + j) not in T][0]
        # the centre of the 4x4 region in cell coordinates is (2br+2, 2bc+2); the 4 central cells:
        cen = [(2 * br + 1, 2 * bc + 1), (2 * br + 1, 2 * bc + 2), (2 * br + 2, 2 * bc + 1), (2 * br + 2, 2 * bc + 2)]
        cen_in = [c for c in cen if (c[0] // 2, c[1] // 2) != missing]
        out.append(frozenset(cen_in))
        for b in T:
            cells = {(2 * b[0] + i, 2 * b[1] + j) for i in (0, 1) for j in (0, 1)}
            out.append(frozenset(cells - set(cen_in)))
    hb = (hole[0] // 2, hole[1] // 2)
    cells = {(2 * hb[0] + i, 2 * hb[1] + j) for i in (0, 1) for j in (0, 1)}
    out.append(frozenset(cells - {hole}))
    return out


def is_L(t):
    if len(t) != 3:
        return False
    rs = [c[0] for c in t]
    cs = [c[1] for c in t]
    return max(rs) - min(rs) == 1 and max(cs) - min(cs) == 1


def valid_tiling(n, hole, tiles):
    N = 1 << n
    cells = [c for t in tiles for c in t]
    want = {(r, c) for r in range(N) for c in range(N)} - {hole}
    return all(is_L(t) for t in tiles) and len(cells) == len(set(cells)) and set(cells) == want


for n in range(0, 6):
    N = 1 << n
    ok_td = ok_bu = ok_cnt = True
    holes = [(r, c) for r in range(N) for c in range(N)]
    for h in holes:
        a = tile_topdown(n, h)
        b = tile_bottomup(n, h)
        ok_td &= valid_tiling(n, h, a)
        ok_bu &= valid_tiling(n, h, b)
        ok_cnt &= len(a) == len(b) == (4 ** n - 1) // 3
    check(f"Theorem 5, n={n}: top-down tiling valid for all {N * N} holes", ok_td)
    check(f"Theorem 5, n={n}: bottom-up tiling valid for all {N * N} holes", ok_bu)
    check(f"n={n}: (4^n-1)/3 = {(4 ** n - 1) // 3} triominos", ok_cnt)
check("4^n mod 3 = 1, so 4^n is never a multiple of 3 (n <= 50)", all(pow(4, n, 3) == 1 for n in range(51)))
calls_ok = True
for n in range(0, 7):
    c = [0]
    tile_topdown(n, (0, 0), calls=c)
    calls_ok &= c[0] == (4 ** (n + 1) - 1) // 3
check("top-down tiling makes (4^{n+1}-1)/3 calls: T(n) = 4T(n-1) + O(1) = Theta(4^n), linear in the board", calls_ok)
# the figure's boards
FIG_HOLE = (1, 5)
check("figure: top-down and bottom-up tilings of the 8x8 board minus (1,5) are valid, 21 triominos each",
      valid_tiling(3, FIG_HOLE, tile_topdown(3, FIG_HOLE)) and valid_tiling(3, FIG_HOLE, tile_bottomup(3, FIG_HOLE))
      and len(tile_topdown(3, FIG_HOLE)) == 21)


# =====================================================================================================
# §7 Binary numbers exist — four proofs as algorithms
# =====================================================================================================
def bin_topdown(n):
    if n == 0:
        return []
    k = n.bit_length() - 1                      # largest k with 2^k <= n
    assert 2 ** k <= n < 2 ** (k + 1)
    m = n - 2 ** k
    assert 0 <= m < 2 ** k and m < n
    rest = bin_topdown(m)
    assert all(p < 2 ** k for p in rest)
    return rest + [2 ** k]


def bin_bottomup(n):
    if n == 0:
        return []
    m = n // 2
    assert 0 <= m < n
    rest = [2 * p for p in bin_bottomup(m)]
    assert all(p > 1 for p in rest)
    return rest + ([1] if n % 2 else [])


def bin_algorithm(n):
    S = [1] * n
    it = 0
    while True:
        dup = next((x for x in sorted(set(S)) if S.count(x) > 1), None)
        if dup is None:
            break
        size = len(S)
        S.remove(dup)
        S.remove(dup)
        S.append(2 * dup)
        it += 1
        assert sum(S) == n and len(S) == size - 1          # invariant; cardinality drops by 1
    assert it <= max(n - 1, 0)
    return S


BABY = {0: []}


def bin_babystep(n, trace=None):
    """'Weak' induction: representation of n-1, plus 2^0, then the carry loop of the note (i counts from 0)."""
    if n == 0:
        return []
    if n - 1 not in BABY:
        bin_babystep(n - 1)
    S = list(BABY[n - 1]) + [1]
    i = 0
    if trace is not None:
        trace.append((0, sorted(S)))
    while S.count(2 ** i) > 1:
        S.remove(2 ** i)
        S.remove(2 ** i)
        S.append(2 ** (i + 1))
        i += 1
        if trace is not None:
            trace.append((i, sorted(S)))
    BABY[n] = list(S)
    return S


def distinct_powers(S, n):
    return sum(S) == n and len(S) == len(set(S)) and all(p > 0 and p & (p - 1) == 0 for p in S)


for name, f in [("top-down", bin_topdown), ("bottom-up", bin_bottomup), ("by algorithm", bin_algorithm),
                ("baby-step", bin_babystep)]:
    lim = 600 if name == "by algorithm" else 3000
    check(f"Theorem 6, {name} proof: distinct powers of 2 summing to n, 0 <= n <= {lim}",
          all(distinct_powers(f(n), n) for n in range(lim + 1)))
check("all four proofs produce the same set (the binary representation), n <= 600",
      all(sorted(bin_topdown(n)) == sorted(bin_bottomup(n)) == sorted(bin_algorithm(n)) == sorted(bin_babystep(n))
          for n in range(601)))
# the baby-step invariants with the correct indexing: after the j-th iteration (j = 0: before the loop), the sum is n
# and the elements are distinct except possibly two copies of 2^j; the j-th iteration (1-indexed) merges 2^(j-1).
ok_inv, ok_idx = True, True
for n in range(1, 1500):
    tr = []
    bin_babystep(n, tr)
    for j, S in tr:
        ok_inv &= sum(S) == n
        dups = [x for x in set(S) if S.count(x) > 1]
        ok_inv &= dups == [] or dups == [2 ** j] and S.count(2 ** j) == 2
    for (j0, S0), (j1, S1) in zip(tr, tr[1:]):
        # iteration number j1 (1-indexed) removed two copies of 2^(j1-1) and added 2^j1
        ok_idx &= S0.count(2 ** (j1 - 1)) - S1.count(2 ** (j1 - 1)) == 2
check("baby-step invariants: sum n; only possible duplicate after iteration j is two copies of 2^j", ok_inv)
check("the j-th iteration (1-indexed) merges two copies of 2^(j-1), not 2^j as printed (p. 17)", ok_idx)
tr = []
bin_babystep(8, tr)
check("baby-step example n = 8: 7 = 4+2+1, add 1, carry three times -> {8}",
      tr == [(0, [1, 1, 2, 4]), (1, [2, 2, 4]), (2, [4, 4]), (3, [8])], tr)
check("binary representation is unique (subsets of {1,2,4,...,2^11} have distinct sums)",
      len({sum(s) for r in range(13) for s in itertools.combinations([2 ** i for i in range(12)], r)}) == 2 ** 12)

# =====================================================================================================
# §8 sqrt 2 is irrational
# =====================================================================================================
LIM = 3000
sq = {p * p for p in range(1, 2 * LIM)}
check(f"Theorem 7: p^2 != 2q^2 for all 1 <= p, q <= {LIM}", all(2 * q * q not in sq for q in range(1, LIM + 1)))
check("case p odd: p^2 = 4i^2 + 4i + 1 is odd (i = floor(p/2))",
      all(p * p == 4 * (p // 2) ** 2 + 4 * (p // 2) + 1 and p * p % 2 == 1 for p in range(1, 2000, 2)))
check("case p even, q odd: p^2 = 4i^2 divisible by 4, 2q^2 = 4(2j^2 + 2j) + 2 is not",
      all(p * p % 4 == 0 for p in range(2, 2000, 2)) and
      all(2 * q * q == 4 * (2 * (q // 2) ** 2 + 2 * (q // 2)) + 2 for q in range(1, 2000, 2)))
check("case both even: p^2 = 2q^2 <=> i^2 = 2j^2 with i = p/2 < p, j = q/2 < q",
      all((p * p == 2 * q * q) == ((p // 2) ** 2 == 2 * (q // 2) ** 2) for p in range(2, 400, 2)
          for q in range(2, 400, 2)))

# =====================================================================================================
# §9 Fibonacci parity
# =====================================================================================================
F = [0, 1]
for i in range(2, 3001):
    F.append(F[-1] + F[-2])
check("Fibonacci numbers 0,1,1,2,3,5,8,13,21,34,55,89 as printed", F[:12] == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89])
check("Theorem 8: F_n even <=> 3 | n, 0 <= n <= 3000", all((F[n] % 2 == 0) == (n % 3 == 0) for n in range(3001)))
check("if 3 | n (n >= 3) then neither n-1 nor n-2 is divisible by 3; otherwise exactly one is",
      all(((n - 1) % 3 != 0 and (n - 2) % 3 != 0) if n % 3 == 0 else (((n - 1) % 3 == 0) + ((n - 2) % 3 == 0) == 1)
          for n in range(2, 3001)))
# the printed hypothesis 'F_k even iff n divisible by 3' (k < n) is false as a statement, e.g. for n = 4, k = 3
n, k = 4, 3
check("the printed hypothesis 'F_k even iff n divisible by 3' fails for n = 4, k = 3 (p. 18)",
      ((F[k] % 2 == 0) == (n % 3 == 0)) is False)


# =====================================================================================================
# §10 Recursive functions
# =====================================================================================================
def Ffun(n, memo={0: 0}):
    if n not in memo:
        memo[n] = 1 + Ffun(n // 2)
    return memo[n]


check("Theorem 9: F(n) = 1 + floor(log2 n) for 1 <= n <= 200000",
      all(Ffun(n) == 1 + (n.bit_length() - 1) for n in range(1, 200001)))
check("F(n) = number of bits of n (= 1 + floor(log2 n)); exact floor log via bit_length, 1 <= n <= 2^20",
      all(n.bit_length() - 1 == math.floor(math.log2(n)) for n in [1, 2, 3, 4, 7, 8, 1023, 1024, 2 ** 20 - 1, 2 ** 20]))
check("1 <= floor(n/2) < n for n >= 2", all(1 <= n // 2 < n for n in range(2, 100000)))
check("odd n > 1: floor(log2 n) = floor(log2 (n-1)) (n is not a power of 2)",
      all((n.bit_length() == (n - 1).bit_length()) for n in range(3, 200001, 2)))
check("even n: floor(log2(n/2)) = floor(log2 n) - 1", all((n // 2).bit_length() == n.bit_length() - 1
                                                          for n in range(2, 200001, 2)))
check("the formula 1 + floor(log2 n) is undefined at n = 0 (F(0) = 0 is the definition's base case only)",
      Ffun(0) == 0)


# concept page example: f(1) = 0, f(n) = f(floor(n/2)) + f(ceil(n/2)) + 1 => f(n) = n - 1
def fsplit(n, memo={1: 0}):
    if n not in memo:
        memo[n] = fsplit(n // 2) + fsplit((n + 1) // 2) + 1
    return memo[n]


check("concept example: f(1)=0, f(n)=f(floor(n/2))+f(ceil(n/2))+1 gives f(n) = n-1, n <= 100000",
      all(fsplit(n) == n - 1 for n in range(1, 100001)))
check("concept example: for n >= 2, 1 <= floor(n/2) <= ceil(n/2) < n and they sum to n",
      all(1 <= n // 2 <= (n + 1) // 2 < n and n // 2 + (n + 1) // 2 == n for n in range(2, 100001)))
check("concept example: for n >= 4 neither floor(n/2) nor ceil(n/2) is n-1 (a weak hypothesis does not reach them)",
      all(n // 2 != n - 1 and (n + 1) // 2 != n - 1 for n in range(4, 100001)))


def mergesort_merges(A, cnt):
    """Algorithms §1.4 MergeSort: split at m = floor(n/2); count the Merge calls."""
    n = len(A)
    if n <= 1:
        return A
    m = n // 2
    L, R = mergesort_merges(A[:m], cnt), mergesort_merges(A[m:], cnt)
    cnt[0] += 1
    out, i, j = [], 0, 0
    while i < len(L) or j < len(R):
        if j >= len(R) or (i < len(L) and L[i] <= R[j]):
            out.append(L[i])
            i += 1
        else:
            out.append(R[j])
            j += 1
    return out


ok = True
for n in range(1, 1500):
    c = [0]
    A = [rng.randrange(100) for _ in range(n)]
    ok &= mergesort_merges(A, c) == sorted(A) and c[0] == fsplit(n) == n - 1
check("concept example: MergeSort on n items makes exactly f(n) = n - 1 Merge calls (n < 1500)", ok)
# concept trap: induction over all the integers is unsound
check("concept trap: for every integer n some k < n is negative, so 'every k < n is >= 0 => n >= 0' holds "
      "vacuously, yet -1 >= 0 is false (n in -500..500)",
      all(min(n, 0) - 1 < n and min(n, 0) - 1 < 0 for n in range(-500, 501)) and not (-1 >= 0))


# =====================================================================================================
# §11 Trees
# =====================================================================================================
def all_trees(maxn):
    for n in range(1, maxn + 1):
        if n == 1:
            g = nx.Graph()
            g.add_node(0)
            yield g
        else:
            yield from nx.nonisomorphic_trees(n)


trees = list(all_trees(11))
check(f"{len(trees)} non-isomorphic trees on 1..11 vertices enumerated", len(trees) == sum(
    [1, 1, 1, 2, 3, 6, 11, 23, 47, 106, 235]))
check("Theorem 10: |V| = |E| + 1 for every tree on <= 11 vertices", all(T.number_of_nodes() == T.number_of_edges() + 1
                                                                        for T in trees))
# direct proof: root anywhere, orient away; every non-root vertex has exactly one incoming edge
ok = True
for T in trees:
    for r in T.nodes:
        D = nx.bfs_tree(T, r)
        ok &= D.in_degree(r) == 0 and all(D.in_degree(v) == 1 for v in T.nodes if v != r)
        ok &= D.number_of_edges() == T.number_of_edges()
check("direct proof: orienting away from any root gives in-degree 1 at every other vertex", ok)
# proof 1: deleting any edge leaves exactly two components, both trees, sizes adding up
ok = True
for T in trees:
    for e in list(T.edges):
        H = T.copy()
        H.remove_edge(*e)
        comps = [H.subgraph(c) for c in nx.connected_components(H)]
        ok &= len(comps) == 2 and all(nx.is_tree(C) for C in comps)
        ok &= sum(C.number_of_nodes() for C in comps) == T.number_of_nodes()
        ok &= sum(C.number_of_edges() for C in comps) + 1 == T.number_of_edges()
check("proof 1: T minus any edge has exactly two components, both trees (all trees <= 11 vertices)", ok)
# proof 2: deleting a vertex of degree d leaves exactly d components, all trees
ok = True
for T in trees:
    for v in T.nodes:
        d = T.degree(v)
        H = T.copy()
        H.remove_node(v)
        comps = [H.subgraph(c) for c in nx.connected_components(H)]
        ok &= len(comps) == d and all(nx.is_tree(C) for C in comps)
        ok &= T.number_of_edges() == d + sum(C.number_of_edges() for C in comps)
check("proof 2: T minus a vertex of degree d has exactly d components, all trees", ok)


# proof 3: the maximal walk without repeated edges ends at a leaf
def maximal_walk(T, start, r):
    used, v, path = set(), start, [start]
    while True:
        nxt = [w for w in T.neighbors(v) if frozenset((v, w)) not in used]
        if not nxt:
            return path
        w = r.choice(nxt)
        used.add(frozenset((v, w)))
        path.append(w)
        v = w


ok_leaf, ok_simple = True, True
for T in trees:
    if T.number_of_nodes() < 2:
        continue
    for s in T.nodes:
        for _ in range(5):
            p = maximal_walk(T, s, rng)
            ok_leaf &= T.degree(p[-1]) == 1
            ok_simple &= len(p) == len(set(p))
check("proof 3: a maximal walk without repeated edges never repeats a vertex and ends at a leaf", ok_leaf and ok_simple)
check("every tree with >= 2 vertices has a leaf (in fact >= 2)",
      all(sum(1 for v in T if T.degree(v) == 1) >= 2 for T in trees if T.number_of_nodes() >= 2))
check("deleting a leaf from a tree leaves a tree with one vertex and one edge fewer",
      all(nx.is_tree(T.subgraph([u for u in T if u != l])) for T in trees if T.number_of_nodes() >= 2
          for l in T if T.degree(l) == 1))


# The "not a proof": building up by adding leaves. The theorem is true and every tree CAN be built that way...
def buildable_by_leaves(maxn):
    seen = {1: {nx.weisfeiler_lehman_graph_hash(nx.empty_graph(1))}}
    level = [nx.empty_graph(1)]
    for n in range(2, maxn + 1):
        new, hashes = [], set()
        for T in level:
            for v in list(T.nodes):
                U = T.copy()
                U.add_edge(v, n * 100)
                U = nx.convert_node_labels_to_integers(U)
                if not any(nx.is_isomorphic(U, X) for X in new):
                    new.append(U)
        level = new
        seen[n] = new
    return seen


built = buildable_by_leaves(9)
check("every tree on <= 9 vertices arises by adding leaves to a 1-vertex tree (the build-up claim is true here)",
      all(len(built[n]) == len([T for T in trees if T.number_of_nodes() == n]) for n in range(2, 10)))
# ... but the same pattern "proves" a false claim: a graph on >= 2 vertices with min degree >= 1 is connected.
ok_step = True
for n in range(2, 7):
    for G in (nx.graph_atlas(i) for i in range(1, 1253)):
        if G.number_of_nodes() != n or min((d for _, d in G.degree), default=0) < 1 or not nx.is_connected(G):
            continue
        for v in G.nodes:
            H = G.copy()
            H.add_edge(v, "new")
            ok_step &= nx.is_connected(H) and min(d for _, d in H.degree) >= 1
check("build-up 'inductive step' is valid: adding a vertex joined to a connected min-degree-1 graph keeps both", ok_step)
K2 = nx.complete_graph(2)
twoK2 = nx.Graph([(0, 1), (2, 3)])
check("build-up base case K2 holds, yet two disjoint edges is a counterexample to the false claim",
      nx.is_connected(K2) and min(d for _, d in twoK2.degree) >= 1 and not nx.is_connected(twoK2))
check("two disjoint edges cannot be built up: deleting any vertex leaves an isolated vertex",
      all(min(d for _, d in twoK2.subgraph([u for u in twoK2 if u != v]).degree) == 0 for v in twoK2))
cex = [G for G in (nx.graph_atlas(i) for i in range(1, 1253)) if G.number_of_nodes() >= 2
       and min(d for _, d in G.degree) >= 1 and not nx.is_connected(G)]
check("smallest counterexamples to the false claim have 4 vertices (two disjoint edges)",
      min(G.number_of_nodes() for G in cex) == 4 and
      [nx.is_isomorphic(G, twoK2) for G in cex if G.number_of_nodes() == 4] == [True])

# =====================================================================================================
# Exercises (pp. 21-30): statements and the numbers in their examples (not solved on the page)
# =====================================================================================================
can_ex1 = makeable(3000, (6, 10, 15))
check("Ex 1: every amount > 29 is a sum of 6s, 10s, 15s; 29 is not",
      all(can_ex1[n] for n in range(30, 3001)) and not can_ex1[29])
check("Ex 2: sum r^i = (1 - r^{n+1})/(1 - r) (rational r != 1, n <= 25)",
      all(sum(r ** i for i in range(n + 1)) == (1 - r ** (n + 1)) / (1 - r)
          for r in [Fraction(a, b) for a in range(-5, 6) for b in (1, 2, 3)] if r != 1 for n in range(26)))
check("Ex 3: (sum i)^2 = sum i^3, n <= 500", all(sum(range(n + 1)) ** 2 == sum(i ** 3 for i in range(n + 1))
                                                for n in range(501)))
Fm = {0: 0, 1: 1}
for i in range(2, 80):
    Fm[i] = Fm[i - 1] + Fm[i - 2]
for i in range(1, 80):
    Fm[-i] = Fm[-i + 2] - Fm[-i + 1]
check("Ex 4(a): sum_{i<=n} F_i = F_{n+2} - 1", all(sum(Fm[i] for i in range(n + 1)) == Fm[n + 2] - 1 for n in range(70)))
check("Ex 4(b): F_n^2 - F_{n+1}F_{n-1} = (-1)^{n+1}, 0 <= n <= 70 (F_{-1} = 1)",
      all(Fm[n] ** 2 - Fm[n + 1] * Fm[n - 1] == (-1) ** (n + 1) for n in range(71)))
check("Ex 4(c): m | n => F_m | F_n (1 <= m <= n <= 70)",
      all(Fm[n] % Fm[m] == 0 for m in range(1, 71) for n in range(m, 71, m)))
check("Ex 5 examples: 42 = 3^4-3^3-3^2-3^1, 25 = 3^3-3^1+3^0, 17 = 3^3-3^2-3^0",
      81 - 27 - 9 - 3 == 42 and 27 - 3 + 1 == 25 and 27 - 9 - 1 == 17)


def bal3(n):
    out, i = [], 0
    while n:
        r = n % 3
        if r == 1:
            out.append((1, i))
            n -= 1
        elif r == 2:
            out.append((-1, i))
            n += 1
        n //= 3
        i += 1
    return out


check("Ex 5: every integer |n| <= 5000 is a sum of distinct +-3^i",
      all(sum(s * 3 ** i for s, i in bal3(n)) == n for n in range(-5000, 5001)))
check("Ex 6 example 42 as printed: (-2)^6+(-2)^5+(-2)^4+(-2)^0 = 49, not 42 (p. 22)",
      (-2) ** 6 + (-2) ** 5 + (-2) ** 4 + (-2) ** 0 == 49)
check("Ex 6: correct is 42 = (-2)^6+(-2)^5+(-2)^4+(-2)^3+(-2)^2+(-2)^1",
      sum((-2) ** i for i in (6, 5, 4, 3, 2, 1)) == 42)
check("Ex 6 examples 25 = (-2)^6+(-2)^5+(-2)^3+(-2)^0 and 17 = (-2)^4+(-2)^0",
      sum((-2) ** i for i in (6, 5, 3, 0)) == 25 and sum((-2) ** i for i in (4, 0)) == 17)


def negabin(n):
    d, i = [], 0
    while n != 0:
        r = n % 2
        if r:
            d.append(i)
        n = (n - r) // -2
        i += 1
    return d


check("Ex 6: every |n| <= 5000 is a sum of distinct powers of -2",
      all(sum((-2) ** i for i in negabin(n)) == n for n in range(-5000, 5001)))
check("Ex 7(a) examples: 17 = F7+F4+F2, 42 = F9+F6, 54 = F9+F7+F5+F3",
      Fm[7] + Fm[4] + Fm[2] == 17 and Fm[9] + Fm[6] == 42 and Fm[9] + Fm[7] + Fm[5] + Fm[3] == 54)
check("Ex 7(b) examples: 16 = F6+F5+F3+F2, 42 = F8+F7+F5+F3+F1, 54 = F8+...+F1",
      Fm[6] + Fm[5] + Fm[3] + Fm[2] == 16 and Fm[8] + Fm[7] + Fm[5] + Fm[3] + Fm[1] == 42
      and sum(Fm[i] for i in range(1, 9)) == 54)
check("Ex 7(c) table F_{-1..-10} = 1,-1,2,-3,5,-8,13,-21,34,-55 and F_{-n} = (-1)^{n+1} F_n",
      [Fm[-i] for i in range(1, 11)] == [1, -1, 2, -3, 5, -8, 13, -21, 34, -55]
      and all(Fm[-n] == (-1) ** (n + 1) * Fm[n] for n in range(70)))
check("Ex 7(d) examples 17 = F-7+F-5+F-2 and -42 = F-10+F-7",
      Fm[-7] + Fm[-5] + Fm[-2] == 17 and Fm[-10] + Fm[-7] == -42)
check("Ex 7(d) example 54 as printed: F-9+F-7+F-5+F-3+F-1 = 55, not 54 (p. 23); correct 54 = F-9+F-7+F-5+F-3",
      Fm[-9] + Fm[-7] + Fm[-5] + Fm[-3] + Fm[-1] == 55 and Fm[-9] + Fm[-7] + Fm[-5] + Fm[-3] == 54)


def legal_move(a, b, extended=False):
    """Is the multiset b reachable from a in one move of the coin game of Ex 8 (extended: part (c))?"""
    a, b = sorted(a, reverse=True), sorted(b, reverse=True)
    succ = set()
    L = list(a)
    m = len(L)
    if not extended:
        for i in range(m):
            for j in range(m):
                if i != j and L[j] <= L[i] - 2:
                    M = L[:]
                    M[i] -= 1
                    M[j] += 1
                    succ.add(tuple(sorted([x for x in M if x], reverse=True)))
            M = L[:]
            M[i] -= 1
            succ.add(tuple(sorted([x for x in M if x] + [1], reverse=True)))
            if L[i] == 1:
                succ.add(tuple(sorted(L[:i] + L[i + 1:], reverse=True)))
    else:
        for i in range(m):
            for j in range(m):
                for k in range(m):
                    if len({i, j, k}) == 3 and L[j] <= L[i] - 2 and L[k] <= L[i] - 2:
                        M = L[:]
                        M[i] -= 1
                        M[j] += 1
                        M[k] += 1
                        succ.add(tuple(sorted([x for x in M if x], reverse=True)))
                if i != j and L[j] <= L[i] - 2:
                    M = L[:]
                    M[i] -= 1
                    M[j] += 1
                    succ.add(tuple(sorted([x for x in M if x] + [1], reverse=True)))
            M = L[:]
            M[i] -= 1
            succ.add(tuple(sorted([x for x in M if x] + [1, 1], reverse=True)))
            if L[i] == 1:
                succ.add(tuple(sorted(L[:i] + L[i + 1:], reverse=True)))
    return tuple(b) in succ


game_a = [(4, 2, 1), (4, 1, 1, 1), (3, 2, 1, 1), (2, 2, 2, 1), (2, 2, 1, 1, 1), (2, 1, 1, 1, 1, 1), (2, 1, 1, 1, 1),
          (2, 1, 1, 1), (2, 1, 1), (2, 1), (2,), (1, 1), (1,), ()]
check("Ex 8 example game: every printed move is legal", all(legal_move(x, y) for x, y in zip(game_a, game_a[1:])))
game_c = [(4, 2, 1), (3, 3, 2), (3, 2, 2, 1, 1), (3, 2, 2, 1), (3, 2, 2), (3, 2, 1, 1, 1), (2, 2, 2, 2, 1),
          (2, 2, 2, 2), (2, 2, 2, 1, 1, 1), (2, 2, 2, 1, 1), (2, 2, 2, 1), (2, 2, 2), (2, 2, 1, 1, 1), (2, 2, 1, 1),
          (2, 2, 1), (2, 2), (2, 1, 1, 1), (1, 1, 1, 1, 1, 1), (1, 1, 1, 1, 1), (1, 1, 1, 1), (1, 1, 1), (1, 1),
          (1,), ()]
check("Ex 8(c) example game: every printed move is legal",
      all(legal_move(x, y, True) for x, y in zip(game_c, game_c[1:])),
      [i for i, (x, y) in enumerate(zip(game_c, game_c[1:])) if not legal_move(x, y, True)])
check("Ex 9: |A x B| = |A||B| and |B|^|A| functions A -> B (sizes <= 4)",
      all(len(list(itertools.product(range(a), range(b)))) == a * b and
          len(list(itertools.product(range(b), repeat=a))) == b ** a for a in range(1, 5) for b in range(1, 5)))


def full_binary_trees(n_internal):
    if n_internal == 0:
        return [None]
    out = []
    for k in range(n_internal):
        for L in full_binary_trees(k):
            for R in full_binary_trees(n_internal - 1 - k):
                out.append((L, R))
    return out


def leaves_internal(t):
    if t is None:
        return 1, 0
    a, b = leaves_internal(t[0])
    c, d = leaves_internal(t[1])
    return a + c, b + d + 1


check("Ex 10: in every full binary tree with <= 9 internal nodes, leaves = internal + 1",
      all(l == i + 1 for k in range(10) for t in full_binary_trees(k) for l, i in [leaves_internal(t)]))


def binomial(k):
    if k == 0:
        return ()
    t = binomial(k - 1)
    return tuple(sorted(t + (t,)))   # children multiset of the root, canonical (unordered)


def canon(t):
    return tuple(sorted(canon(c) for c in t))


def size(t):
    return 1 + sum(size(c) for c in t)


def depth_counts(t, d=0, acc=None):
    acc = acc if acc is not None else {}
    acc[d] = acc.get(d, 0) + 1
    for c in t:
        depth_counts(c, d + 1, acc)
    return acc


def add_leaf_everywhere(t):
    return tuple(sorted(tuple(add_leaf_everywhere(c) for c in t) + ((),)))


check("Ex 11(a): a binomial tree of order k has 2^k nodes (k <= 12)", all(size(binomial(k)) == 2 ** k for k in range(13)))
check("Ex 11(b): a leaf added to every node of B_{k-1} gives B_k (k <= 10)",
      all(canon(add_leaf_everywhere(binomial(k - 1))) == canon(binomial(k)) for k in range(1, 11)))
check("Ex 11(c): B_k has C(k, d) nodes at depth d (k <= 12)",
      all(depth_counts(binomial(k)).get(d, 0) == math.comb(k, d) for k in range(13) for d in range(k + 2)))


def fib_tree(n):
    """Ordered binary trees as (left, right) with None for a missing child."""
    t = (None, None)
    for _ in range(2, n + 1):
        t = grow(t)
    return t


def grow(t):
    if t is None:
        return None
    L, R = t
    if L is None and R is None:
        return (None, (None, None))          # a leaf gets a right child
    nl, nr = grow(L), grow(R)
    if (L is None) != (R is None):           # exactly one child (in the old tree): add a left child
        if nl is None:
            nl = (None, None)
    return (nl, nr)


def leaves(t):
    if t is None:
        return 0
    return 1 if t == (None, None) else leaves(t[0]) + leaves(t[1])


def nodes(t):
    return 0 if t is None else 1 + nodes(t[0]) + nodes(t[1])


check("Ex 12(a): the Fibonacci tree F_n has F_n leaves (n <= 20)", all(leaves(fib_tree(n)) == Fm[n] for n in range(1, 21)))
check("Ex 12(c): right subtree of F_n is F_{n-1} (2 <= n <= 18)", all(fib_tree(n)[1] == fib_tree(n - 1)
                                                                       for n in range(2, 19)))
check("Ex 12(d): left subtree of F_n is F_{n-2} (3 <= n <= 18)", all(fib_tree(n)[0] == fib_tree(n - 2)
                                                                      for n in range(3, 19)))
check("Ex 12 figure: the first six Fibonacci trees have 1, 2, 4, 7, 12, 20 nodes (as drawn on p. 25)",
      [nodes(fib_tree(n)) for n in range(1, 7)] == [1, 2, 4, 7, 12, 20])


def gray(d):
    if d == 1:
        return ["0", "1"]
    g = gray(d - 1)
    return ["0" + x for x in g] + ["1" + x for x in reversed(g)]


check("Ex 13: the d-cube has a Hamiltonian cycle for 2 <= d <= 12 (reflected Gray code)",
      all(len(set(gray(d))) == 2 ** d and all(sum(a != b for a, b in zip(gray(d)[i], gray(d)[(i + 1) % 2 ** d])) == 1
                                              for i in range(2 ** d)) for d in range(2, 13)))
check("Ex 13: the 1-cube has no Hamiltonian cycle (a single edge)", len(gray(1)) == 2)


def ham_paths(n, E):
    return [p for p in itertools.permutations(range(n)) if all((p[i], p[i + 1]) in E for i in range(n - 1))]


def has_triangle(n, E):
    return any((a, b) in E and (b, c) in E and (c, a) in E for a, b, c in itertools.permutations(range(n), 3))


ok_a, ok_b = True, True
for n in range(1, 6):
    pairs = list(itertools.combinations(range(n), 2))
    for bits in range(1 << len(pairs)):
        E = {(a, b) if (bits >> i) & 1 else (b, a) for i, (a, b) in enumerate(pairs)}
        hp = ham_paths(n, E)
        ok_a &= len(hp) >= 1
        ok_b &= len(hp) == 1 or has_triangle(n, E)
check("Ex 14(a): every tournament on <= 5 vertices has a Hamiltonian path (all of them)", ok_a)
check("Ex 14(b): every tournament on <= 5 vertices has exactly one Hamiltonian path or a directed triangle", ok_b)
# Ex 14 figure, edges read off the PDF (p. 25)
V = "uvwxyz"
Efig = {("u", "v"), ("u", "z"), ("v", "z"), ("v", "w"), ("w", "x"), ("x", "z"), ("z", "y"), ("x", "y"), ("y", "u"),
        ("u", "x"), ("y", "v"), ("z", "w"), ("v", "x"), ("w", "u"), ("y", "w")}
idx = {c: i for i, c in enumerate(V)}
Ei = {(idx[a], idx[b]) for a, b in Efig}
check("Ex 14 figure: the reconstructed graph is a tournament on 6 vertices",
      len(Efig) == 15 and all(((a, b) in Efig) != ((b, a) in Efig) for a, b in itertools.combinations(V, 2)))
paths = {"".join(V[i] for i in p) for p in ham_paths(6, Ei)}
check("Ex 14 figure: uvwxzy and yuvxzw are Hamiltonian paths and wxz is a directed triangle",
      {"uvwxzy", "yuvxzw"} <= paths and {("w", "x"), ("x", "z"), ("z", "w")} <= Efig, f"{len(paths)} paths in all")


def nertex_trees(maxsize):
    """For every root colour and size <= maxsize: a dict (R, G, B) -> number of Ygdrasil family trees with those counts
    (children ordered: a red nertex's green child first)."""
    from functools import lru_cache

    @lru_cache(None)
    def T(colour, size):
        res = {}
        if colour == "B":
            if size == 1:
                res[(0, 0, 1)] = 1
        elif colour == "G":
            for c in ("R", "B"):
                for (r, g, b), m in T(c, size - 1).items():
                    res[(r, g + 1, b)] = res.get((r, g + 1, b), 0) + m
        else:
            for k in range(1, size - 1):
                for c in ("R", "B"):
                    for a, m1 in T("G", k).items():
                        for b2, m2 in T(c, size - 1 - k).items():
                            key = (a[0] + b2[0] + 1, a[1] + b2[1], a[2] + b2[2])
                            res[key] = res.get(key, 0) + m1 * m2
        return res

    return [(c, rgb, m) for c in "RGB" for s in range(1, maxsize + 1) for rgb, m in T(c, s).items()]


nt = nertex_trees(16)
check("Ex 15: B = R + 1, G in {R, B}, and G = B iff Rudy is green (all families <= 16 nertices)",
      all(b == r + 1 and g in (r, b) and ((g == b) == (c == "G")) for c, (r, g, b), m in nt),
      f"{sum(m for *_, m in nt)} family trees")
check("Ex 16 example: the two formulas are equivalent",
      all(bool((not ((p and q) or not r)) and ((not (p or not r)) and q)) ==
          bool((((not p) or (not q)) and r) and (((not p) and r) and q)) for p, q, r in itertools.product((0, 1), repeat=3)))
a = complex(-1, 1)
table = {0: 1, 1: -1 + 1j, 2: -2j, 3: 2 + 2j, 4: -4, 5: 4 - 4j, 6: 8j, 7: -8 - 8j, 8: 16, 9: -16 + 16j, 10: -32j,
         11: 32 + 32j, 12: -64, 13: 64 - 64j, 14: 128j, 15: -128 - 128j}
check("Ex 19: the table of powers of alpha = -1 + i", all(a ** k == v for k, v in table.items()))
ex19 = {4: (8, 7, 6, 4), -8: (7, 6), 15j: (9, 8, 2, 1, 0), 1 + 6j: (6, 2, 0), 2 - 3j: (5, 4, 3, 2, 1, 0),
        -4 + 2j: (9, 8, 7, 5, 2)}
check("Ex 19: the six examples", all(sum(a ** k for k in ks) == z for z, ks in ex19.items()))


def lazy_next(digits):
    d = digits[:]
    d[-1] += 1
    if 2 in d:
        i = max(j for j, x in enumerate(d) if x == 2)
        d[i] = 0
        if i == 0:
            d.insert(0, 1)
        else:
            d[i - 1] += 1
    return d


printed = ("0, 1, 10, 11, 20, 101, 110, 111, 120, 201, 210, 1011, 1020, 1101, 1110, 1111, 1120, 1201, 1210, 2011, 2020, "
           "2101, 2110, 10111, 10120, 10201, 10210, 11011, 11020, 11101, 11110, 11111, 11120, 11201, 11210, 12011, "
           "12020, 12101, 12110, 20111, 20120, 20201, 20210, 21011, 21020, 21101, 21110, 101111, 101120, 101201, "
           "101210, 102011, 102020").split(", ")
seq, d = [], [0]
for N in range(20000):
    seq.append("".join(map(str, d)))
    d = lazy_next(d)
check("Ex 20: the printed lazy-binary list (53 numbers) matches the rule", seq[:len(printed)] == printed,
      [(i, seq[i], printed[i]) for i in range(len(printed)) if seq[i] != printed[i]][:3])
check("Ex 20(b): digit sum of N in lazy binary = floor(lg(N+1)), N < 20000",
      all(sum(map(int, s)) == (N + 1).bit_length() - 1 for N, s in enumerate(seq)))


def between_ok(s):
    marks = [c for c in s if c in "02"]
    return all(x != y for x, y in zip(marks, marks[1:]))


check("Ex 20(a): between two 2s there is a 0 and between two 0s a 2, N < 20000", all(between_ok(s) for s in seq))
R = [Fraction(0)]
for n in range(1, 1 << 17):
    x = R[-1]
    R.append(1 / (2 * math.floor(x) - x + 1))
printed21 = [Fraction(0), Fraction(1), Fraction(1, 2), Fraction(2), Fraction(1, 3), Fraction(3, 2), Fraction(2, 3),
             Fraction(3), Fraction(1, 4), Fraction(4, 3), Fraction(3, 5), Fraction(5, 2), Fraction(2, 5),
             Fraction(5, 3), Fraction(3, 4), Fraction(4), Fraction(1, 5)]
check("Ex 21: the printed first 17 terms", R[:17] == printed21)
pos = {}
dup = False
for i, x in enumerate(R):
    dup |= x in pos
    pos.setdefault(x, i)
check("Ex 21: no repeats in the first 2^17 terms, and every p/q with p + q <= 16 appears",
      not dup and all(Fraction(p, q) in pos for q in range(1, 16) for p in range(0, 16 - q + 1)))
# Ex 22 as printed is false: f(x) = x^(2 lg pi) satisfies both conditions but is not O(x)
alpha = 2 * math.log2(math.pi)
f22 = lambda x: x ** alpha
check("Ex 22 as printed is false: f(x) = x^(2 lg pi) > 0 and f(x) = pi f(x/sqrt2) for x > 1, yet f(x)/x -> infinity",
      all(abs(f22(x) - math.pi * f22(x / math.sqrt(2))) <= 1e-9 * f22(x) for x in [1.01, 2, 10, 1e3, 1e6])
      and f22(1e6) / 1e6 > 1e10 and abs(alpha - 3.3029) < 1e-3, f"exponent {alpha:.4f}")

print()
if FAIL:
    print(f"{len(FAIL)} FAILED: " + "; ".join(FAIL))
    sys.exit(1)
print("ALL OK")
