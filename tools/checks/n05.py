#!/usr/bin/env python3
"""Checks for content/4-lecture-notes/05-hashing.md (Erickson, Director's Cut 5, "Hash Tables") and the concept page
content/concepts/hashing.md.

Every hash family the note defines is built as an explicit list of functions and its uniformity, (near-)universality
or k-uniformity is computed EXACTLY (Fractions, all salts, all pairs of keys) for small primes, word sizes and table
sizes: the constant family, ideal random functions, polynomial families, prime multiplicative hashing MP (Lemmas 1-3,
the Carter-Wegman example, the 5x4 table on p. 7), the universal family MB+ (Theorem 1, the exact collision formula,
the five tables on p. 8) and binary multiplicative hashing MB (Lemma 4, Theorem 2 and its three cases). Chaining:
expected chain lengths over every salt. Balls and bins: exact max-load distributions by counting functions, the
inequalities in the proofs of Lemmas 5 and 6, and simulation of the max load for n up to 10^6. Perfect hashing: the
sum-of-squares identity, Lemma 7 exactly over every salt, secondary tables. Open addressing: the recurrence and its
exact solution against brute force over all permutations. Linear, quadratic, double and binary probing sequences;
linear probing against Knuth's formulas by simulation; binary probing (the structural lemma inside Lemma 8's proof on
random tables, LooseBinaryProbe as printed and corrected, the inequalities of Lemmas 8 and 9). Cuckoo hashing (concept
page only) by simulation. Finally every number printed on the two pages and in the figures is recomputed."""
import itertools
import math
import os
import random
import re
import sys
from collections import Counter
from fractions import Fraction as Fr

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
PAGE = os.path.join(ROOT, "content", "4-lecture-notes", "05-hashing.md")
CONCEPT = os.path.join(ROOT, "content", "concepts", "hashing.md")
FIGS = os.path.join(HERE, "..", "figs")
FAIL = []
random.seed(5374)
RNG = np.random.default_rng(5374)


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAIL.append(name)


def read(path):
    return open(path, encoding="utf-8").read() if os.path.exists(path) else ""


def primes(lo, hi):
    return [p for p in range(max(lo, 2), hi) if all(p % d for d in range(2, int(p ** 0.5) + 1))]


# =====================================================================================================
# Families of hash functions: a family is a list of tuples h, with h[x] the hash value of key x in U = range(u).

def prob_uniform(H, u, m):
    """True iff Pr_h[h(x) = i] = 1/m for every x and every i."""
    N = len(H)
    for x in range(u):
        c = Counter(h[x] for h in H)
        if any(Fr(c[i], N) != Fr(1, m) for i in range(m)):
            return False
    return True


def max_collision(H, u):
    """max over x != y of Pr_h[h(x) = h(y)] (exact)."""
    A = np.array(H)
    N = len(H)
    best = 0
    for x in range(u):
        eq = (A[:, x + 1:] == A[:, [x]]).sum(axis=0)
        if eq.size:
            best = max(best, int(eq.max()))
    return Fr(best, N)


def collision_table(H, u):
    A = np.array(H)
    N = len(H)
    return {(x, y): Fr(int((A[:, x] == A[:, y]).sum()), N) for x in range(u) for y in range(x + 1, u)}


def is_k_uniform(H, u, m, k):
    N = len(H)
    for xs in itertools.combinations(range(u), k):
        c = Counter(tuple(h[x] for x in xs) for h in H)
        if len(c) != m ** k or any(Fr(v, N) != Fr(1, m ** k) for v in c.values()):
            return False
    return True


def fam_MP(p, m, U):
    """prime multiplicative hashing: multp_a(x) = (a x mod p) mod m, a in [p]^+."""
    return [tuple((a * x % p) % m for x in U) for a in range(1, p)]


def fam_MBplus(p, m, U):
    """h_{a,b}(x) = ((a x + b) mod p) mod m, a in [p]^+, b in [p]."""
    return [tuple(((a * x + b) % p) % m for x in U) for a in range(1, p) for b in range(p)]


def multb(a, x, w, l):
    return ((a * x) % (1 << w)) >> (w - l)


# =====================================================================================================
print("== §5.2 The importance of being random")
for (u, m) in [(10, 3), (100, 7), (1000, 32)]:
    ok = True
    for _ in range(50):
        h = [random.randrange(m) for _ in range(u)]
        ok &= max(Counter(h).values()) >= math.ceil(u / m)
    check(f"any fixed h: some slot receives >= ceil(u/m) keys (u={u}, m={m}, 50 random h)", ok)
check("division method x mod m: h(x + a m) = h(x) for all a, x (m = 13, |a|, x < 200)",
      all((x + a * 13) % 13 == x % 13 for x in range(200) for a in range(-200, 200)))
check("the division method with m = 2^l keeps the low-order bits of the KEY x (the note writes 'of m')",
      all(x % 16 == x & 15 for x in range(1000)))

print("== §5.3 ...But not too random: uniform, universal, near-universal, k-uniform")
u, m = 4, 3
K = [tuple(a for _ in range(u)) for a in range(m)]
check("constant family K: uniform", prob_uniform(K, u, m))
check("constant family K: not universal (every pair collides with probability 1)", max_collision(K, u) == 1)
IDEAL = list(itertools.product(range(m), repeat=u))
check("ideal random functions [4] -> [3]: uniform, universal with Pr = 1/m exactly",
      prob_uniform(IDEAL, u, m) and set(collision_table(IDEAL, u).values()) == {Fr(1, m)})
check("ideal random functions are k-uniform for k = 1, 2, 3, 4 (u = 4, m = 3)",
      all(is_k_uniform(IDEAL, u, m, k) for k in (1, 2, 3, 4)))
for p in (5, 7):
    for k in (2, 3):
        POLY = [tuple(sum(c * x ** i for i, c in enumerate(cs)) % p for x in range(p))
                for cs in itertools.product(range(p), repeat=k)]
        check(f"polynomials of degree < {k} over Z_{p} (m = p, {len(POLY)} functions) are {k}-uniform"
              f" and not {k + 1}-uniform", is_k_uniform(POLY, p, p, k) and not is_k_uniform(POLY, p, p, k + 1))
# universal does not imply uniform: MB+ with p = 5, m = 3 (and p = 7, m = 3 for the concept page)
for p, m in [(5, 3), (7, 3)]:
    H = fam_MBplus(p, m, range(p))
    c0 = Fr(sum(1 for h in H if h[0] == 0), len(H))
    check(f"MB+ with p={p}, m={m} is universal but not uniform: Pr[h(x)=0] = {c0}",
          max_collision(H, p) <= Fr(1, m) and not prob_uniform(H, p, m) and c0 == Fr(-(-p // m), p))
H7 = fam_MBplus(7, 3, range(7))
check("concept example: MB+ with p=7, m=3 has collision probability exactly 5/21 for every pair",
      set(collision_table(H7, 7).values()) == {Fr(5, 21)})
check("concept example: ... and Pr[h(x) = 0] = 3/7, Pr[h(x) = 1] = Pr[h(x) = 2] = 2/7 for every x",
      all(Fr(sum(1 for h in H7 if h[x] == i), len(H7)) == (Fr(3, 7) if i == 0 else Fr(2, 7))
          for x in range(7) for i in range(3)))

print("== §5.4 Chaining: expected chain lengths")
p, m = 101, 8
for n in (4, 8, 16, 24):
    worst_univ, worst_near = Fr(0), Fr(0)
    for trial in range(6):
        S = random.sample(range(p), n + 1)
        x, T = S[0], S[1:]
        Hp = [(a, b) for a in range(1, p) for b in range(p)]
        el = Fr(sum(sum(1 for y in T if ((a * x + b) % p) % m == ((a * y + b) % p) % m) for a, b in Hp), len(Hp))
        worst_univ = max(worst_univ, el / Fr(n, m))
        el2 = Fr(sum(sum(1 for y in T if (a * x % p) % m == (a * y % p) % m) for a in range(1, p)), p - 1)
        worst_near = max(worst_near, el2 / Fr(n, m))
    check(f"x not in T, |T| = {n}, m = {m}: E[l(x)] <= alpha over all MB+ salts and <= 2 alpha over all MP salts",
          worst_univ <= 1 and worst_near <= 2, f"max ratios {float(worst_univ):.3f}, {float(worst_near):.3f}")
# the note's figure: ten letters of ALGORITHMS in ten slots, chains H-M, O-I, A-T-S
slots = ["G", "H", "", "", "", "R", "O", "", "A", "L"]
chains = {"H": ["M"], "O": ["I"], "A": ["T", "S"]}
items = [s for s in slots if s] + [y for v in chains.values() for y in v]
check("the note's chained-table figure (p. 4): 10 items in 10 slots, load factor 1, 4 empty slots, longest chain 3",
      len(items) == 10 and sorted(items) == sorted("ALGORITHMS") and slots.count("") == 4
      and max(1 + len(chains.get(s, [])) for s in slots if s) == 3)

# the page's own example (figures n05-chained and n05-perfect)
EX_KEYS = [12, 23, 31, 44, 58, 67, 75, 89]
EX_P, EX_M, EX_A, EX_B = 101, 8, 23, 8
hx = {x: ((EX_A * x + EX_B) % EX_P) % EX_M for x in EX_KEYS}
buckets = {i: [x for x in EX_KEYS if hx[x] == i] for i in range(EX_M)}
check("page example: h(x) = ((23x + 8) mod 101) mod 8 sends 12,23,31,44,58,67,75,89 to 2,0,6,2,5,2,0,3",
      [hx[x] for x in EX_KEYS] == [2, 0, 6, 2, 5, 2, 0, 3])
check("page example: chains T[0] = 23,75; T[2] = 12,44,67; T[3] = 89; T[5] = 58; T[6] = 31; three empty slots",
      buckets == {0: [23, 75], 1: [], 2: [12, 44, 67], 3: [89], 4: [], 5: [58], 6: [31], 7: []})
sizes = [len(buckets[i]) for i in range(EX_M)]
check("page example: sum of n_i^2 = 16 (<= 3n - 2 = 22), secondary sizes 2 n_i^2 = 8, 18, 2, 2, 2: 32 cells",
      sum(s * s for s in sizes) == 16 and [2 * s * s for s in sizes if s] == [8, 18, 2, 2, 2]
      and sum(2 * s * s for s in sizes) == 32)
# successful search cost in the example: average number of list items examined
check("page example: a successful search examines (1+2 + 1+2+3 + 1+1+1)/8 = 12/8 = 1.5 list items on average",
      Fr(sum(sum(range(1, len(b) + 1)) for b in buckets.values()), len(EX_KEYS)) == Fr(3, 2))

print("== §5.5.1 Prime multiplicative hashing MP")
check("Lemma 1: every a in [p]^+ has a unique inverse mod p (all primes p < 200)",
      all(sum(1 for z in range(1, p) if a * z % p == 1) == 1 for p in primes(2, 200) for a in range(1, p)))
only_if, iff_fail, ce = True, 0, None
for p in primes(3, 32):
    for m in range(2, p + 2):
        for a in range(1, p):
            mult = [(a * x % p) % m for x in range(p)]
            for x in range(1, p):
                for y in range(1, p):
                    col = mult[x] == mult[y]
                    rhs = x == y or mult[(x - y) % p] == 0 or mult[(y - x) % p] == 0
                    if col and not rhs:
                        only_if = False
                    if rhs and not col:
                        iff_fail += 1
                        if ce is None or (p, m, a, x, y) < ce:
                            ce = (p, m, a, x, y)
check("Lemma 2, 'only if' direction: a collision implies x = y or multp(x-y) = 0 or multp(y-x) = 0 (p < 32, all m, a)",
      only_if)
check("Lemma 2, 'if' direction FAILS: the right side does not imply a collision", iff_fail > 0 and ce is not None,
      f"{iff_fail} counterexamples; smallest (p, m, a, x, y) = {ce}")
check("the counterexample quoted on the page: p=7, m=3, a=1, x=1, y=2: multp(6) = 0 but multp(1)=1 != multp(2)=2",
      (6 % 7) % 3 == 0 and (1 % 7) % 3 == 1 and (2 % 7) % 3 == 2)
check("Lemma 3: exactly floor((p-1)/m) salts give multp_a(z) = 0, for every z in [p]^+ (p < 100, 2 <= m <= p+1)",
      all(sum(1 for a in range(1, p) if (a * z % p) % m == 0) == (p - 1) // m
          for p in primes(3, 100) for m in range(2, p + 2) for z in range(1, p)))
worst = Fr(0)
for p in primes(3, 40):
    for m in range(2, p + 3):
        worst = max(worst, max_collision(fam_MP(p, m, range(p)), p) * m)
check("MP is near-universal: max over pairs in [p] of Pr[collision] <= 2/m (all p < 40, 2 <= m <= p+2)", worst <= 2,
      f"max m*Pr = {worst} = {float(worst):.4f}")
cw_ok, cw_n = True, 0
for p in primes(3, 400):
    for m in range(2, p - 1):
        if (p - 1) % (m + 1) == 0:
            c = Fr(sum(1 for a in range(1, p) if a % m == (a * (m + 1) % p) % m), p - 1)
            cw_ok &= c == Fr(2, m + 1) and c > Fr(1, m)
            cw_n += 1
check("Carter-Wegman: if p mod (m+1) = 1 then Pr[multp(1) = multp(m+1)] = 2/(m+1) > 1/m (all such p < 400)",
      cw_ok and cw_n > 100, f"{cw_n} pairs (p, m)")
TAB7 = [[0, 0, 0, 0], [1, 2, 0, 1], [2, 1, 1, 0], [0, 1, 1, 2], [1, 0, 2, 1]]
check("the table on p. 7 (p=5, m=3, rows a = 0..4, columns x = 1..4) is (a x mod 5) mod 3",
      TAB7 == [[(a * x % 5) % 3 for x in range(1, 5)] for a in range(5)])
check("p=5, m=3: Pr_a[multp(1) = multp(4)] = 1/2 over a in [5]^+ (the table's row a = 0 is not a salt)",
      Fr(sum(1 for a in range(1, 5) if TAB7[a][0] == TAB7[a][3]), 4) == Fr(1, 2))

print("== §5.5.2 Actually universal hashing MB+")
for p in primes(3, 60):
    xs, ys = random.sample(range(p), 2)
    sol = {}
    for a in range(1, p):
        for b in range(p):
            sol.setdefault(((a * xs + b) % p, (a * ys + b) % p), []).append((a, b))
    inv = pow(xs - ys, -1, p)
    ok = (len(sol) == p * (p - 1) and all(len(v) == 1 for v in sol.values()) and all(r != s for r, s in sol)
          and all(sol[(r, s)] == [((r - s) * inv % p, (s * xs - r * ys) * inv % p)] for (r, s) in sol))
    if not ok:
        break
check("Theorem 1 proof: (a,b) -> (ax+b, ay+b) mod p is a bijection from [p]^+ x [p] onto pairs r != s, with the "
      "printed formulas for a and b (all p < 60, random x != y)", ok)
ok_univ, ok_formula, ok_strict, ok_N = True, True, True, True
for p in primes(3, 30):
    for m in range(2, p + 3):
        H = fam_MBplus(p, m, range(p))
        ct = collision_table(H, p)
        ok_univ &= max(ct.values()) <= Fr(1, m)
        N = sum(1 for r in range(p) for s in range(p) if r != s and r % m == s % m)
        ok_N &= N <= Fr(p * (p - 1), m) and all(
            sum(1 for s in range(p) if s != r and s % m == r % m) <= max(p // m, 0) for r in range(p))
        if m < p:
            f = Fr((p - p % m) * (p - (m - p % m)), m * p * (p - 1))
            ok_formula &= set(ct.values()) == {f}
            ok_strict &= f < Fr(1, m)
check("Theorem 1: MB+ is universal, exhaustively (all p < 30, 2 <= m <= p+2, all pairs in [p])", ok_univ)
check("Theorem 1 proof: N <= p(p-1)/m and at most floor(p/m) partners s per r", ok_N)
check("ceil(p/m) - 1 <= (p-1)/m for all p, m >= 1; = floor(p/m) when m does not divide p",
      all(-(-p // m) - 1 <= Fr(p - 1, m) and (p % m == 0 or -(-p // m) - 1 == p // m)
          for p in range(1, 200) for m in range(1, 210)))
check("exact collision probability (p - p mod m)(p - (m - p mod m)) / (m p (p-1)) for EVERY pair (2 <= m < p < 30)",
      ok_formula)
check("... and it is strictly less than 1/m", ok_strict)
check("p=5, m=3: the formula gives 1/5", Fr((5 - 5 % 3) * (5 - (3 - 5 % 3)), 3 * 4 * 5) == Fr(1, 5))
TAB8 = {0: [[0, 0, 0, 0], [1, 2, 0, 1], [2, 1, 1, 0], [0, 1, 1, 2], [1, 0, 2, 1]],
        1: [[1, 1, 1, 1], [2, 0, 1, 0], [0, 0, 2, 1], [1, 2, 0, 0], [0, 1, 0, 2]],
        2: [[2, 2, 2, 2], [0, 1, 0, 1], [1, 1, 0, 0], [0, 0, 1, 1], [1, 0, 1, 0]],
        3: [[0, 0, 0, 0], [1, 0, 1, 2], [0, 2, 1, 1], [1, 1, 2, 0], [2, 1, 0, 1]],
        4: [[1, 1, 1, 1], [0, 1, 2, 0], [1, 0, 0, 2], [2, 0, 0, 1], [0, 2, 1, 0]]}
check("the five tables on p. 8 (p=5, m=3, b = 0..4, rows a = 0..4, columns x = 1..4) are ((ax+b) mod 5) mod 3",
      all(TAB8[b] == [[((a * x + b) % 5) % 3 for x in range(1, 5)] for a in range(5)] for b in range(5)))
check("p. 8 tables: keys 1 and 4 collide for 4 of the 20 salts (a,b), a != 0: probability 1/5",
      sum(1 for b in range(5) for a in range(1, 5) if TAB8[b][a][0] == TAB8[b][a][3]) == 4)

print("== §5.5.3 Binary multiplicative hashing MB")
check("Lemma 4: x -> a x mod 2^w is a bijection on the odd words W (w <= 12, every odd x)",
      all(len({a * x % (1 << w) for a in range(1, 1 << w, 2)}) == 1 << (w - 1)
          and all(a * x % (1 << w) % 2 == 1 for a in range(1, 1 << w, 2))
          for w in range(1, 13) for x in range(1, 1 << w, 2)))
near_ok, not_univ, impl_ok, worst_mb = True, False, True, Fr(0)
univ_exact = True   # R29: universal exactly when l >= w-1
for w in range(2, 9):
    U = np.arange(1 << w)
    for l in range(1, w + 1):
        A = np.array([((a * U) % (1 << w)) >> (w - l) for a in range(1, 1 << w, 2)], dtype=np.int64)
        nA = A.shape[0]
        C = np.zeros((1 << w, 1 << w), dtype=np.int64)
        for v in range(1 << l):
            M = (A == v).astype(np.int64)
            C += M.T @ M
        np.fill_diagonal(C, 0)
        mx = Fr(int(C.max()), nA)
        worst_mb = max(worst_mb, mx * (1 << l))
        near_ok &= mx <= Fr(2, 1 << l)
        not_univ |= mx > Fr(1, 1 << l)
        univ_exact &= (mx <= Fr(1, 1 << l)) == (l >= w - 1)
        # the proof's reduction: a collision implies multb(y - x) in {0, m-1}
        for x in range(0, 1 << w, max(1, (1 << w) // 16)):
            for y in range(x + 1, 1 << w):
                col = A[:, x] == A[:, y]
                z = (y - x) % (1 << w)
                rhs = (A[:, z] == 0) | (A[:, z] == (1 << l) - 1)
                impl_ok &= bool(np.all(~col | rhs))
check("Theorem 2: MB is near-universal, exhaustively (w <= 8, every l, every pair of words): Pr <= 2/2^l", near_ok,
      f"max m*Pr = {worst_mb}")
check("MB is not universal: some pair collides with probability > 1/2^l", not_univ)
check("MB is universal exactly when l >= w-1: not universal for every l <= w-2, universal for l = w-1, w "
      "(exhaustive, 2 <= w <= 8)", univ_exact)
check("Theorem 2 proof: multb(x) = multb(y) implies multb(y-x) = 0 or m-1 (w <= 8)", impl_ok)
case_ok = True
case_seen = set()
for w in range(2, 11):
    for l in range(1, w + 1):
        for r in range(w):
            for q in random.sample(range(1, 1 << (w - r), 2), min(4, 1 << (w - r - 1))):
                z = q << r
                vals = [multb(a, z, w, l) for a in range(1, 1 << w, 2)]
                N = len(vals)
                p0, p1 = Fr(vals.count(0), N), Fr(vals.count((1 << l) - 1), N)
                if l == 1:   # m - 1 = 0: the two events coincide
                    continue
                if r < w - l:
                    case_ok &= p0 == p1 == Fr(1, 1 << l); case_seen.add("<")
                elif r == w - l:
                    case_ok &= p0 == 0 and p1 == Fr(2, 1 << l); case_seen.add("=")
                else:
                    case_ok &= p0 == 0 and p1 == 0; case_seen.add(">")
check("Theorem 2's three cases (w <= 10): r < w-l gives 1/2^l and 1/2^l; r = w-l gives 0 and 2/2^l; "
      "r > w-l (printed as 'r < w-l' in the third bullet) gives 0 and 0", case_ok and case_seen == {"<", "=", ">"})
check("the C macro ((a)*(x) >> (WORDSIZE-HASHBITS)) on w-bit unsigned words computes multb (w = 16, l = 5)",
      all((((a * x) & 0xFFFF) >> 11) == multb(a, x, 16, 5)
          for a in random.sample(range(1, 1 << 16, 2), 50) for x in random.sample(range(1 << 16), 50)))
# the figure's example
BW, BL, BA, BX = 8, 3, 0b10110101, 0b00101011
prod = BA * BX
check("figure n05-binary-mult: a = 10110101 (181), x = 00101011 (43), a.x = 7783 = 0001111001100111, "
      "low word 01100111, hash = top 3 bits = 011 = 3",
      prod == 7783 and format(prod, "016b") == "0001111001100111" and format(prod % 256, "08b") == "01100111"
      and multb(BA, BX, BW, BL) == 3)

print("== §5.6 Balls and bins")


def count_maxload_le(n, bins, t):
    """number of functions [n] -> [bins] with every fiber of size <= t (exact integer)."""
    ways = [1] + [0] * n
    for _ in range(bins):
        new = [0] * (n + 1)
        for s in range(n + 1):
            tot = 0
            for j in range(0, min(t, s) + 1):
                tot += math.comb(s, j) * ways[s - j]
            new[s] = tot
        ways = new
    return ways[n]


def exp_maxload(n, tmax=None):
    tmax = n if tmax is None else tmax
    total = n ** n
    E = Fr(0)
    for t in range(0, tmax):
        E += 1 - Fr(count_maxload_le(n, n, t), total)
    return E


E10 = exp_maxload(10)
check("E[max load], 10 balls in 10 bins, exact by counting all 10^10 functions: 2.7487 (2.75)",
      abs(float(E10) - 2.74869) < 1e-5, f"{E10} = {float(E10):.5f}")
E100 = exp_maxload(100, 16)  # Pr[max > 16] <= 100/17! < 1e-12
check("E[max load], 100 balls in 100 bins (exact up to < 1e-12): 4.2326 (4.23)", abs(float(E100) - 4.23260) < 1e-5,
      f"{float(E100):.5f}")
tail_ok = True
for n in (5, 10, 30, 100, 300):
    for k in range(1, min(n, 25) + 1):
        exact = sum(math.comb(n, j) * Fr(n - 1, n) ** (n - j) * Fr(1, n) ** j for j in range(k, n + 1))
        tail_ok &= exact <= Fr(math.comb(n, k), n ** k) <= Fr(1, math.factorial(k))
check("Lemma 5 proof: Pr[X_j >= k] <= C(n,k)/n^k <= 1/k! (exact, n in {5,10,30,100,300}, k <= 25)", tail_ok)
check("k! >= k^(k/2) for 1 <= k <= 300", all(math.lgamma(k + 1) >= (k / 2) * math.log(k) - 1e-9 for k in range(1, 301)))
check("the printed '=': k^(k/2) is not (2c lg n/lg lg n)^(2c lg n/lg lg n) = k^k (e.g. k = 8)", 8 ** 4 != 8 ** 8)
L, c = 64, 1
k = 2 * c * L / math.log2(L)
check("the printed step k^(k/2) >= (sqrt(lg n))^k FAILS: lg n = 64, c = 1, k = 21.33: k^(k/2) = e^32.6 < 8^k = e^44.4",
      (k / 2) * math.log(k) < k * math.log(math.sqrt(L)), f"{(k / 2) * math.log(k):.1f} vs {k * math.log(math.sqrt(L)):.1f}")
check("the printed conclusion k! >= n^c FAILS for n = 2^16, c = 1: k = 2*16/4 = 8 and 8! = 40320 < 65536",
      2 * 16 / math.log2(16) == 8 and math.factorial(8) == 40320 < 2 ** 16)


def first_good(c, f):
    """smallest L (lg n) from which f(L) holds for every L up to 10^5."""
    good = None
    for L in range(10 ** 5, 3, -1):
        if not f(L, c):
            return good
        good = L
    return good


fact_ge = lambda L, c: math.lgamma(2 * c * L / math.log2(L) + 1) >= c * L * math.log(2)
kek_ge = lambda L, c: (lambda k: k * math.log(k / math.e) >= k * 0.5 * math.log(L))(2 * c * L / math.log2(L))
L1, L2 = first_good(1, fact_ge), first_good(1, kek_ge)
check("fix: k! >= n^c does hold for all large n (c = 1: for every lg n >= L1); "
      "and (k/e)^k >= (sqrt(lg n))^k for lg n >= L2", L1 is not None and L2 is not None and L1 <= L2,
      f"L1 = {L1}, L2 = {L2}")
# 'max > k' means 'some X_j > k', not 'all'
n3 = 3
p_max_ge2 = 1 - Fr(count_maxload_le(n3, n3, 1), n3 ** n3)
check("max_j X_j > k means X_j > k for SOME j: 3 balls in 3 bins, Pr[max >= 2] = 7/9 while Pr[all X_j >= 2] = 0",
      p_max_ge2 == Fr(7, 9))
# union bound and the lemma's conclusion, exactly, n = 100, c = 2
n, c = 100, 2
kk = 2 * c * math.log2(n) / math.log2(math.log2(n))
K = math.ceil(kk)
pmax = 1 - Fr(count_maxload_le(n, n, K - 1), n ** n)
p1 = sum(math.comb(n, j) * Fr(n - 1, n) ** (n - j) * Fr(1, n) ** j for j in range(K, n + 1))
check(f"Lemma 5 at n = 100, c = 2: k = {kk:.2f}; Pr[max >= {K}] <= n Pr[X_1 >= {K}] < 1/n^(c-1)",
      pmax <= n * p1 < Fr(1, n ** (c - 1)), f"{float(pmax):.2e} <= {float(n * p1):.2e}")
# simulation of the max load
sim = {}
for n in (10 ** 3, 10 ** 4, 10 ** 5, 10 ** 6):
    loads = [int(np.bincount(RNG.integers(0, n, n), minlength=n).max()) for _ in range(30)]
    sim[n] = (float(np.mean(loads)), min(loads), max(loads))
ratios = {n: sim[n][0] / (math.log(n) / math.log(math.log(n))) for n in sim}
check("simulated E[max load] (30 trials each) is between 1.4 and 2.0 times ln n / ln ln n for n = 10^3 ... 10^6",
      all(1.4 <= r <= 2.0 for r in ratios.values()),
      "; ".join(f"n={n}: mean {sim[n][0]:.2f} (range {sim[n][1]}-{sim[n][2]}), ratio {ratios[n]:.2f}" for n in sim))
check("n = 10^6: the max load averages about 8.7 (between 8.3 and 9.2), while ln n / ln ln n = 5.26",
      8.3 <= sim[10 ** 6][0] <= 9.2 and abs(math.log(1e6) / math.log(math.log(1e6)) - 5.26) < 0.01)
# pairwise collisions
ok = True
for n in range(2, 60):
    m = n * n
    EC = Fr(math.comb(n, 2), m)
    pno = math.prod(Fr(m - i, m) for i in range(n))
    ok &= EC == Fr(n - 1, 2 * n) < Fr(1, 2) and 1 - pno <= EC and 1 - pno < Fr(1, 2)
check("m = n^2, ideal random: E[C] = C(n,2)/m = (n-1)/(2n) < 1/2 and Pr[some collision] <= E[C] < 1/2 (n < 60)", ok)
check("near-universal with m = 2n^2: E[C] <= C(n,2) * 2/m = (n-1)/(2n) < 1/2 (n < 200)",
      all(Fr(math.comb(n, 2) * 2, 2 * n * n) < Fr(1, 2) for n in range(2, 200)))
for (p, n) in [(31, 4), (61, 5)]:
    m = 2 * n * n
    worst = Fr(0)
    for _ in range(20):
        S = random.sample(range(p), n)
        pr = Fr(sum(1 for a in range(1, p) if len({(a * x % p) % m for x in S}) < n), p - 1)
        worst = max(worst, pr)
    check(f"MP (near-universal), n = {n}, m = 2n^2 = {m}: Pr[some collision] < 1/2 over every salt (20 random sets)",
          worst < Fr(1, 2), f"max {worst}")
ok6 = True
for n in range(2, 25):
    for m in sorted({n, n + 1, 2 * n, n * n, 2 * n * n, n ** 3}):
        P0 = Fr(m - 1, m) ** n
        P1 = n * Fr(1, m) * Fr(m - 1, m) ** (n - 1)
        Pmax = 1 - math.prod(Fr(m - i, m) for i in range(n))
        ok6 &= P0 > 1 - Fr(n, m)
        ok6 &= (P1 > Fr(n, m) - Fr(n * (n - 1), m * m)) if n > 2 else (P1 == Fr(n, m) - Fr(n * (n - 1), m * m))
        ok6 &= 1 - P0 - P1 < Fr(n * (n - 1), m * m)
        ok6 &= Pmax <= m * (1 - P0 - P1) < Fr(n * (n - 1), m)
check("Lemma 6 proof: Pr[X_j=0] > 1-n/m, Pr[X_j=1] > n/m - n(n-1)/m^2 (equality when n = 2), "
      "Pr[X_j>1] < n(n-1)/m^2, "
      "Pr[max > 1] < n(n-1)/m (exact, 2 <= n < 25, several m)", ok6)
check("p. 11 typo: (1 - 1/m)^n = sum_{i=0}^n C(n,i)(-1/m)^i; the printed sum from i = 1 is (1-1/m)^n - 1",
      all(sum(math.comb(n, i) * Fr(-1, m) ** i for i in range(0, n + 1)) == Fr(m - 1, m) ** n
          and sum(math.comb(n, i) * Fr(-1, m) ** i for i in range(1, n + 1)) == Fr(m - 1, m) ** n - 1
          for n in range(1, 15) for m in range(2, 30)))
ok = all(math.prod(Fr(n ** 3 - i, n ** 3) for i in range(n)) >= 1 - Fr(1, n) for n in range(2, 40))
ok &= all(math.prod(1 - i / math.ceil(n ** 2.5) for i in range(n)) >= 1 - n ** -0.5 for n in range(2, 400))
check("Lemma 6: with m = n^(2+eps) bins, Pr[no bin has two balls] >= 1 - 1/n^eps (eps = 1/2, 1; n < 40)", ok)

print("== §5.7 Perfect hashing")
ok = True
for _ in range(200):
    n, m = random.randint(1, 30), random.randint(1, 30)
    h = [random.randrange(m) for _ in range(n)]
    ni = Counter(h)
    coll = sum(1 for i in range(n) for j in range(i + 1, n) if h[i] == h[j])
    ok &= sum(v * v for v in ni.values()) == n + 2 * coll
check("identity: sum_i n_i^2 = n + 2 (number of colliding pairs) (200 random assignments)", ok)
ok_mp, ok_mbp, ok_mb = True, True, True
worst = {}
for n in (3, 5, 8, 13):
    p = 101
    for _ in range(6):
        S = random.sample(range(p), n)
        e_mp = Fr(sum(sum(v * v for v in Counter((a * x % p) % n for x in S).values()) for a in range(1, p)), p - 1)
        e_mbp = Fr(sum(sum(v * v for v in Counter(((a * x + b) % p) % n for x in S).values())
                       for a in range(1, p) for b in range(p)), p * (p - 1))
        ok_mp &= e_mp <= 3 * n - 2
        ok_mbp &= e_mbp <= 2 * n - 1
        worst[n] = max(worst.get(n, 0), float(e_mp) / n)
check("Lemma 7 exactly over all salts, m = n: E[sum n_i^2] <= 3n - 2 for MP (near-universal) "
      "and <= 2n - 1 for MB+ (universal) (n in {3,5,8,13}, random sets in [101])", ok_mp and ok_mbp,
      "max E/n for MP: " + ", ".join(f"{k}: {v:.2f}" for k, v in worst.items()))
for w, l in [(6, 2), (6, 3), (7, 3), (8, 4)]:
    n = 1 << l
    for _ in range(4):
        S = random.sample(range(1 << w), n)
        e = Fr(sum(sum(v * v for v in Counter(multb(a, x, w, l) for x in S).values()) for a in range(1, 1 << w, 2)),
               1 << (w - 1))
        ok_mb &= e <= 3 * n - 2
check("Lemma 7 for binary multiplicative hashing MB with m = n = 2^l (w <= 8): E[sum n_i^2] <= 3n - 2", ok_mb)
check("ideal random hashing, m = n: E[sum n_i^2] = n + n(n-1)/n = 2n - 1 (exact, all functions for n <= 6)",
      all(Fr(sum(sum(v * v for v in Counter(f).values()) for f in itertools.product(range(n), repeat=n)), n ** n)
          == 2 * n - 1 for n in range(1, 7)))
# secondary tables: size 2 n_j^2, near-universal => no collision with probability >= 1/2
ok = True
for nj in range(2, 7):
    p = 101
    m = 2 * nj * nj
    for _ in range(10):
        S = random.sample(range(p), nj)
        good = sum(1 for a in range(1, p) if len({(a * x % p) % m for x in S}) == nj)
        ok &= Fr(good, p - 1) >= Fr(1, 2)
check("secondary table of size 2 n_j^2 with MP salts: no collision with probability >= 1/2 (n_j = 2..6)", ok)
# the page example's secondary tables: salts drawn as in tools/figs_n05.py (random.Random(374)), redrawn on collision
rng374 = random.Random(374)
SEC = {}
for i, b in buckets.items():
    if not b:
        continue
    sz = 2 * len(b) ** 2
    tries = 0
    while True:
        tries += 1
        a2, b2 = rng374.randrange(1, EX_P), rng374.randrange(EX_P)
        pos = {x: ((a2 * x + b2) % EX_P) % sz for x in b}
        if len(set(pos.values())) == len(b):
            break
    SEC[i] = (a2, b2, sz, pos, tries)
check("page example: secondary salts (a,b) = (43,19), (92,64), (100,16), (19,93), (96,65) for slots 0, 2, 3, 5, 6, "
      "each collision-free at the first draw",
      [(SEC[i][0], SEC[i][1]) for i in (0, 2, 3, 5, 6)] == [(43, 19), (92, 64), (100, 16), (19, 93), (96, 65)]
      and all(v[4] == 1 for v in SEC.values()))
check("page example: T_0 (size 8): 23 -> 3, 75 -> 4; T_2 (size 18): 12 -> 3, 44 -> 0, 67 -> 13",
      SEC[0][3] == {23: 3, 75: 4} and SEC[2][3] == {12: 3, 44: 0, 67: 13})
check("page example: total size 8 primary + 32 secondary cells; Lemma 7's bound 7n - 4 = 52",
      EX_M + sum(v[2] for v in SEC.values()) == 40 and 7 * 8 - 4 == 52)
# collision in secondary table T[2] with the trivial salt? (illustrates retrying)
ok_retry = any(len({((a2 * x + b2) % EX_P) % 18 for x in buckets[2]}) < 3 for a2 in range(1, EX_P) for b2 in range(EX_P))
check("page example: some salts DO collide in T_2 (so the retry step is needed in general)", ok_retry)
pr10 = math.prod(Fr(20 - i, 20) for i in range(10))
check("trap: 10 keys in 20 cells (ideal hashing) collide with probability 1 - 20!/(10! 20^10) > 0.93",
      1 - pr10 > Fr(93, 100), f"{float(1 - pr10):.4f}")
check("Lemma 7: expected total size n + sum 2 n_j^2 <= n + 2(3n - 2) = 7n - 4", all(n + 2 * (3 * n - 2) == 7 * n - 4
                                                                                     for n in range(1, 50)))

print("== §5.8 Open addressing")


def ET(m, n):
    """E[T(m, n)] from the recurrence E[T(m,n)] = 1 + (n/m) E[T(m-1,n-1)], T(m,0) = 1."""
    return Fr(1) if n == 0 else 1 + Fr(n, m) * ET(m - 1, n - 1)


check("the recurrence solves to E[T(m,n)] = (m+1)/(m-n+1) <= m/(m-n) (all 0 <= n < m <= 60)",
      all(ET(m, n) == Fr(m + 1, m - n + 1) <= Fr(m, m - n) for m in range(1, 61) for n in range(m)))
check("... and also for a full table: E[T(m,m)] = m + 1 (the note's bound needs n < m)",
      all(ET(m, m) == m + 1 for m in range(1, 30)))
ok = True
for m in range(1, 7):
    perms = list(itertools.permutations(range(m)))
    for n in range(m):
        tot, cnt = 0, 0
        for occ in itertools.combinations(range(m), n):
            occ = set(occ)
            for pi in perms:
                probes = next(i for i, s in enumerate(pi) if s not in occ) + 1
                tot += probes
                cnt += 1
        ok &= Fr(tot, cnt) == Fr(m + 1, m - n + 1)
check("brute force over all probe permutations and occupied sets (m <= 6): unsuccessful search averages "
      "(m+1)/(m-n+1) probes", ok)
check("alpha = 1/2: (m+1)/(m-n+1) -> 2 and the bound 1/(1-alpha) = 2; alpha = 0.9: bound 10",
      abs(float(Fr(1001, 501)) - 2) < 0.01 and abs(1 / (1 - 0.9) - 10) < 1e-9)


def oa_search(T, probe, x):
    m = len(T)
    for i in range(m):
        j = probe(x, i)
        if T[j] == x:
            return j
        elif T[j] is None:
            return "absent"
    return "full"


def oa_insert(T, probe, x):
    m = len(T)
    for i in range(m):
        j = probe(x, i)
        if T[j] == x:
            return j
        elif T[j] is None:
            T[j] = x
            return j
    return "full"


ok = True
for trial in range(200):
    m = random.randint(1, 12)
    perms = {}

    def probe(x, i, perms=perms, m=m):
        if x not in perms:
            perms[x] = random.sample(range(m), m)
        return perms[x][i]

    T = [None] * m
    S = random.sample(range(100), random.randint(0, m))
    for x in S:
        ok &= oa_insert(T, probe, x) != "full"
    for x in range(100):
        r = oa_search(T, probe, x)
        if x in S:
            ok &= r != "absent" and r != "full" and T[r] == x
        else:
            ok &= r == ("full" if len(S) == m else "absent")
check("OpenAddressSearch / insert (second-to-last line replaced by the store): correct on 200 random tables", ok)

print("== §5.9 Linear and binary probing")
check("linear probing (h + i) mod m and binary probing h XOR i (m = 2^l) give permutations of the slots",
      all(sorted((h + i) % m for i in range(m)) == list(range(m)) for m in range(1, 40) for h in range(m))
      and all(sorted(h ^ i for i in range(1 << l)) == list(range(1 << l)) for l in range(0, 7) for h in range(1 << l)))
check("quadratic probing (h + i^2) mod m, i < m, is NOT a permutation for any m >= 3 (m < 200)",
      all(len({(i * i) % m for i in range(m)}) < m for m in range(3, 200)))
check("quadratic probing with m prime visits only (m+1)/2 slots (odd primes < 200)",
      all(len({(i * i) % m for i in range(m)}) == (m + 1) // 2 for m in primes(3, 200)))
check("double hashing (h + i h') mod m is a permutation iff gcd(h', m) = 1 (m < 40)",
      all((sorted((i * hp) % m for i in range(m)) == list(range(m))) == (math.gcd(hp, m) == 1)
          for m in range(1, 40) for hp in range(1, m + 1)))


def lp_unsuccessful_mean(m, n, trials, rng):
    tot = 0.0
    for _ in range(trials):
        occ = np.zeros(m, dtype=bool)
        for h in rng.integers(0, m, n):
            while occ[h]:
                h = (h + 1) % m
            occ[h] = True
        # a new key hashed to slot j probes the occupied run starting at j, then one empty slot
        d = 0
        dist = np.zeros(m, dtype=np.int64)
        for j in list(range(m - 1, -1, -1)) * 2:   # two backward passes around the circle
            if not occ[j]:
                d = 0
            else:
                d += 1
            dist[j] = d
        tot += float(np.mean(dist + 1))
    return tot / trials


def lp_successful_mean(m, n, trials, rng):
    tot = 0.0
    for _ in range(trials):
        occ = np.zeros(m, dtype=bool)
        s = 0
        for h in rng.integers(0, m, n):
            k = 1
            while occ[h]:
                h = (h + 1) % m
                k += 1
            occ[h] = True
            s += k
        tot += s / n
    return tot / trials


LP = {}
for alpha in (0.5, 0.75, 0.9):
    m = 4001
    n = int(alpha * m)
    un = lp_unsuccessful_mean(m, n, 12, RNG)
    su = lp_successful_mean(m, n, 12, RNG)
    knuth_un = 0.5 * (1 + 1 / (1 - alpha) ** 2)
    knuth_su = 0.5 * (1 + 1 / (1 - alpha))
    LP[alpha] = (un, su, knuth_un, knuth_su)
    check(f"linear probing, alpha = {alpha}, m = {m}, 12 trials: unsuccessful ~ (1 + 1/(1-a)^2)/2 = {knuth_un:.1f}"
          f" and successful ~ (1 + 1/(1-a))/2 = {knuth_su:.2f} (within 10%)",
          abs(un / knuth_un - 1) < 0.10 and abs(su / knuth_su - 1) < 0.10, f"simulated {un:.2f}, {su:.2f}")
check("clustering: linear probing's unsuccessful-search cost exceeds the uniform-hashing bound 1/(1-alpha) "
      "(2 vs 2.5, 4 vs 8.5, 10 vs 50.5)",
      all(LP[a][2] > 1 / (1 - a) for a in LP) and [round(LP[a][2], 1) for a in LP] == [2.5, 8.5, 50.5])

print("== §5.10 Analysis of binary probing")


def bp_build(l, hs):
    m = 1 << l
    H = [None] * m
    for key, h in enumerate(hs):
        for i in range(m):
            j = h ^ i
            if H[j] is None:
                H[j] = key
                break
    return H


def block(l, k, c):
    return range(c << k, (c + 1) << k)


struct_ok, struct_n = True, 0
for trial in range(3000):
    l = random.randint(1, 6)
    m = 1 << l
    n = random.randint(0, m)
    hs = [random.randrange(m) for _ in range(n)]
    H = bp_build(l, hs)
    for k in range(l + 1):
        for c in range(m >> k):
            B = block(l, k, c)
            full = all(H[j] is not None for j in B)
            if not full:
                continue
            struct_n += 1
            popular = lambda kk, cc: sum(1 for h in hs if (h >> kk) == cc) >= (1 << kk)
            uncles = [(kk, (c >> (kk - k)) ^ 1) for kk in range(k, l)]
            struct_ok &= popular(k, c) or any(popular(kk, cc) for kk, cc in uncles)
check("Lemma 8 proof: in a binary-probing table every full block is popular or has a popular uncle "
      "(3000 random tables, m <= 64)", struct_ok and struct_n > 1000, f"{struct_n} full blocks examined")
check("binary probing probes B'_0(x), B'_1(x), ... in order: i in [2^k, 2^(k+1)) gives the uncle block B'_k(x)",
      all({h ^ i for i in range(1 << k, 1 << (k + 1))} == set(block(6, k, (h >> k) ^ 1))
          for h in range(64) for k in range(6)))


def loose_probe(H, l, h, x, variant):
    """variant 'printed': inner test 'if first != Dunno' (as on p. 15); 'dunno': inner test 'if first = Dunno',
    cells of each uncle block scanned in index order; 'priority': the block's verdict is True if it contains x,
    else False if it contains an empty cell (order-independent)."""
    probes = 1
    if H[h] == x:
        return True, probes
    if H[h] is None:
        return False, probes
    first = "Dunno"
    for k in range(l):
        found = empty = False
        for j in block(l, k, (h >> k) ^ 1):
            probes += 1
            if variant == "priority":
                found |= H[j] == x
                empty |= H[j] is None
                continue
            cond = (first != "Dunno") if variant == "printed" else (first == "Dunno")
            if cond:
                if H[j] == x:
                    first = True
                if H[j] is None:
                    first = False
        if variant == "priority" and (found or empty):
            first = found
        if first != "Dunno":
            return first, probes
    return "Full", probes


def real_probe(H, l, h, x):
    for i in range(1 << l):
        j = h ^ i
        if H[j] == x:
            return True, i + 1
        if H[j] is None:
            return False, i + 1
    return "Full", 1 << l


ok_prio, ok_dunno_absent, dunno_wrong, bug_seen = True, True, None, False
for trial in range(2000):
    l = random.randint(1, 6)
    m = 1 << l
    n = random.randint(0, m)
    hs = [random.randrange(m) for _ in range(n)]
    H = bp_build(l, hs)
    for x in range(n + 3):
        h = hs[x] if x < n else random.randrange(m)
        r_real, p_real = real_probe(H, l, h, x)
        r_pr, p_pr = loose_probe(H, l, h, x, "priority")
        r_du, _ = loose_probe(H, l, h, x, "dunno")
        r_bug, _ = loose_probe(H, l, h, x, "printed")
        ok_prio &= r_real == r_pr and p_pr >= p_real
        if x >= n:
            ok_dunno_absent &= r_du == r_real
        elif r_du != r_real and dunno_wrong is None:
            dunno_wrong = (m, x, r_real, r_du)
        if r_real is False and r_bug == "Full":
            bug_seen = True
check("LooseBinaryProbe as printed ('if first != Dunno' inside the loop) never sets first: it returns Full for an "
      "absent key even when the table has empty cells", bug_seen)
check("with the inner test 'if first = Dunno' it is right for ABSENT keys (the case the proof analyzes)",
      ok_dunno_absent)
check("... but scanning a block in arbitrary order can meet an empty cell before x: a PRESENT key reported absent",
      dunno_wrong is not None, f"first example (m, key, real, loose) = {dunno_wrong}")
check("order-independent version (a block containing x answers True, else one with an empty cell answers False) "
      "agrees with binary probing and probes at least as many cells (2000 random tables)", ok_prio)
# Lemma 8 numerically
for l in (10, 14):
    m = 1 << l
    n = m // 4
    tot, cnt = 0, 0
    for _ in range(3):
        hs = RNG.integers(0, m, n).tolist()
        H = bp_build(l, hs)
        for h in RNG.integers(0, m, 3000).tolist():
            tot += real_probe(H, l, h, -1)[1]
            cnt += 1
    check(f"Lemma 8 numerically: m = 2^{l}, n = m/4, ideal random hashing: unsuccessful search averages "
          f"{tot / cnt:.2f} probes (< 1.5)", tot / cnt < 1.5)
ok = True
for m in (64, 256, 1024):
    n = m // 4
    for k in range(0, 6):
        s = 1 << k
        if s > n:
            break
        ok &= math.comb(n, s) * Fr(s, m) ** s <= Fr(n ** s, math.factorial(s)) * Fr(s, m) ** s
        ok &= math.comb(n, s) * (s / m) ** s < (math.e * n / m) ** s
        exact = sum(math.comb(n, j) * Fr(s, m) ** j * (1 - Fr(s, m)) ** (n - j) for j in range(s, n + 1))
        ok &= exact <= math.comb(n, s) * Fr(s, m) ** s
check("P_k: Pr[popular] <= C(n,2^k)(2^k/m)^(2^k) (a union bound -- the note writes '=') < (en/m)^(2^k) "
      "(m in {64,256,1024}, n = m/4)", ok)
check("(e/4)^(2^k) < 4^(-k) holds for k >= 4 and fails for k = 1, 2, 3 ('sufficiently large k')",
      all((math.e / 4) ** (2 ** k) < 4 ** -k for k in range(4, 30))
      and all((math.e / 4) ** (2 ** k) >= 4 ** -k for k in (1, 2, 3)))
# Lemma 9
ok = True
for pp in [Fr(1, 2), Fr(1, 3), Fr(1, 16), Fr(3, 7)]:
    EQ2 = pp * (1 - pp) ** 2 + (1 - pp) * pp ** 2
    EQ4 = pp * (1 - pp) ** 4 + (1 - pp) * pp ** 4
    ok &= EQ2 == pp * (1 - pp) < pp and EQ4 == pp * (1 - pp) * ((1 - pp) ** 3 + pp ** 3) < pp
check("Lemma 9: E[Q_y^2] = p(1-p) < p and E[Q_y^4] = p(1-p)((1-p)^3 + p^3) < p", ok)
ok = True
for N in range(1, 6):
    for pp in [Fr(1, 4), Fr(1, 3)]:
        E4 = Fr(0)
        for bits in itertools.product((0, 1), repeat=N):
            pr = math.prod(pp if b else 1 - pp for b in bits)
            Q = sum(b - pp for b in bits)
            E4 += pr * Q ** 4
        EQ2 = pp * (1 - pp)
        EQ4 = pp * (1 - pp) * ((1 - pp) ** 3 + pp ** 3)
        ok &= E4 == N * EQ4 + 6 * math.comb(N, 2) * EQ2 ** 2
check("Lemma 9: E[Q^4] = sum E[Q_y^4] + 6 sum_{y<z} E[Q_y^2] E[Q_z^2] for independent indicators "
      "(exact, up to 5 variables)", ok)
ok_sign = all(2 ** k - 1 - Fr(2 ** k * (n - 1), m) == 2 ** k * (1 - Fr(n, m) + Fr(1, m)) - 1
              and 2 ** k - 1 - Fr(2 ** k * (n - 1), m) != 2 ** k * (1 - Fr(n, m) - Fr(1, m)) - 1
              for m in (16, 64) for n in range(1, m // 4 + 1) for k in range(1, 6))
check("Lemma 9 sign error (p. 16): 2^k - 1 - 2^k(n-1)/m = 2^k(1 - n/m + 1/m) - 1, not 2^k(1 - n/m - 1/m) - 1",
      ok_sign)
check("Lemma 9: the step to Pr[Q >= 2^(k-1)] needs 2^k(3/4 - 1/m) - 1 >= 2^(k-1); false for k <= 2 (every m)",
      all(2 ** k * (Fr(3, 4) - Fr(1, m)) - 1 < 2 ** (k - 1) for k in (0, 1, 2) for m in (4, 8, 1 << 20)))
check("... with the correct sign the threshold 2^k(1 - (n-1)/m) - 1 >= 2^k (3/4) - 1 >= 2^(k-1) for k >= 2",
      all(2 ** k * (1 - Fr(n - 1, m)) - 1 >= 2 ** (k - 1) for k in range(2, 12) for m in (16, 64, 256)
          for n in range(1, m // 4 + 1)))
check("Lemma 9 (p. 17): with p = 2^k/m, the printed '<' between mp/4 + 3(mp/4)^2 and 2^(k-2) + 3 * 2^(2(k-2)) "
      "is an equality", all(Fr(m * Fr(2 ** k, m), 4) + 3 * Fr(m * Fr(2 ** k, m), 4) ** 2
                            == Fr(2) ** (k - 2) + 3 * Fr(2) ** (2 * (k - 2)) for m in (16, 64, 1024) for k in range(0, 5)))
check("Lemma 9: 2^(k-2) + 3 * 2^(2(k-2)) < 2^(2(k-1)) holds for k >= 3, with equality at k = 2, false at k = 0, 1",
      all(Fr(2) ** (k - 2) + 3 * Fr(2) ** (2 * (k - 2)) < Fr(2) ** (2 * (k - 1)) for k in range(3, 40))
      and 1 + 3 == 4 and all(Fr(2) ** (k - 2) + 3 * Fr(2) ** (2 * (k - 2)) > Fr(2) ** (2 * (k - 1)) for k in (0, 1)))
check("Lemma 9 (page version, n stored keys): threshold 2^k - p n >= (3/4) 2^k >= 2^(k-1) when n <= m/4 (all k)",
      all(2 ** k - Fr(2 ** k, m) * n >= Fr(3, 4) * 2 ** k >= Fr(2 ** k, 2)
          for m in (16, 64, 256) for n in range(1, m // 4 + 1) for k in range(0, 9)))
check("Lemma 9 (page version): n p + 3 n^2 p^2 <= 2^(k-2) + 3 * 2^(2(k-2)) <= 2^(2(k-1)) for k >= 2 (p = 2^k/m, n <= m/4)",
      all(n * Fr(2 ** k, m) + 3 * n * n * Fr(2 ** k, m) ** 2 <= Fr(2) ** (k - 2) + 3 * Fr(2) ** (2 * (k - 2))
          <= Fr(2) ** (2 * (k - 1)) for m in (16, 64, 256) for n in range(1, m // 4 + 1) for k in range(2, 9)))
check("Lemma 9 (page version): E[Q^4] = n E[Q_y^4] + 3 n (n-1) E[Q_y^2]^2 < n p + 3 n^2 p^2",
      all(nn * pp * (1 - pp) * ((1 - pp) ** 3 + pp ** 3) + 3 * nn * (nn - 1) * (pp * (1 - pp)) ** 2 < nn * pp + 3 * nn * nn * pp * pp
          for nn in range(1, 60) for pp in (Fr(1, 2), Fr(1, 8), Fr(1, 64), Fr(3, 5))))
ok = True
for l in (8, 10, 12):
    m = 1 << l
    n = m // 4
    for k in range(2, l):
        s_ = 1 << k
        pr = Fr(s_, m)
        exact = sum(math.comb(n, j) * pr ** j * (1 - pr) ** (n - j) for j in range(s_, n + 1))
        ok &= exact <= Fr(1, 4 ** (k - 1))
check("Lemma 9's conclusion under ideal (hence 5-uniform) hashing: Pr[block popular] <= 2^(-2(k-1)) "
      "(exact binomial, m = 2^8, 2^10, 2^12, n = m/4 keys, k >= 2)", ok)

print("== §5.11 Cuckoo hashing (concept page: standard facts, not in the note)")


def cuckoo_build(n, r, rng, maxloop):
    """two tables of size r, two fully random hash functions; returns (ok, total displacements)."""
    h1 = rng.integers(0, r, n)
    h2 = rng.integers(0, r, n)
    T = [[-1] * r, [-1] * r]
    moves = 0
    for key in range(n):
        x, side = key, 0
        for _ in range(maxloop):
            pos = (h1 if side == 0 else h2)[x]
            x, T[side][pos] = T[side][pos], x
            if x == -1:
                break
            moves += 1
            side ^= 1
        else:
            return False, moves
    # every key is at one of its two cells
    for key in range(n):
        if T[0][h1[key]] != key and T[1][h2[key]] != key:
            return False, moves
    return True, moves


res = {}
for (n, eps, trials) in [(250, 0.1, 400), (1000, 0.1, 300), (4000, 0.1, 150), (1000, 0.5, 100)]:
    r = int((1 + eps) * n)
    maxloop = int(3 * math.log(r) / math.log(1 + eps)) + 1
    fails, mv = 0, 0
    for _ in range(trials):
        okb, moves = cuckoo_build(n, r, RNG, maxloop)
        fails += not okb
        mv += moves
    res[(n, eps)] = (fails / trials, mv / trials / n)
fr = {k: f"{v[0]:.3f}" for k, v in res.items()}
check("cuckoo hashing, two tables of size 1.1n, MaxLoop = 3 log_1.1 r: the build fails (needs a rehash) less often "
      "as n grows (n = 250, 1000, 4000), and rarely (<= 3%) at n = 4000",
      res[(250, 0.1)][0] > res[(4000, 0.1)][0] and res[(4000, 0.1)][0] <= 0.03, str(fr))
check("cuckoo hashing: fewer than 0.7 displacements per insertion on average (eps = 0.1), about 0.34 (eps = 0.5)",
      all(res[(n, 0.1)][1] < 0.7 for n in (250, 1000, 4000)) and abs(res[(1000, 0.5)][1] - 0.34) < 0.03
      and res[(1000, 0.5)][0] == 0, "; ".join(f"{k}: {v[1]:.2f}" for k, v in res.items()))
fails = sum(not cuckoo_build(1000, 800, RNG, 200)[0] for _ in range(60))
check("cuckoo hashing above load 1/2 (1000 keys, two tables of 800) fails almost always", fails >= 54, f"{fails}/60")

# =====================================================================================================
print("== numbers printed on the pages and in the figures")
page = read(PAGE)
concept = read(CONCEPT)
if page:
    check("page: quotes the counterexample to Lemma 2's 'if' (p = 7, m = 3, a = 1, x = 1, y = 2)",
          re.search(r"p = 7\$, \$m = 3\$, \$a = 1\$, \$x = 1\$, \$y = 2", page) is not None)
    check("page: quotes 8! = 40320 < 2^16 = 65536", "40320" in page and "65536" in page)
    check("page: states the exact solution (m+1)/(m-n+1)", "\\frac{m+1}{m-n+1}" in page)
    check("page: E[max load] 2.75 (n = 10), 4.23 (n = 100), 8.7 (n = 10^6), ln n/ln ln n = 5.3",
          all(t in page for t in ("2.75", "4.23", "8.7", "5.3")))
    check("page: Knuth's values 2.5, 8.5, 50.5 against 2, 4, 10", all(t in page for t in ("$2.5$", "$8.5$", "$50.5$")))
    check("page: binary probing averages about 1.4 probes at load 1/4", "about 1.4 probes" in page)
    check("page: lg n >= 36 threshold quoted", "\\lg n\\ge 36" in page)
    check("page: MB not universal only for l <= w-2", "For $\\ell\\le w-2$ it is not universal" in page)
    check("page: linear-probing simulations quoted as within about 10%", "within about 10%" in page)
    check("page: sum n_j^2 = 16 and 7n - 4 quoted", "= 16" in page and "7n - 4" in page)
if concept:
    check("concept page: example p = 7, m = 3 with 5/21 and 3/7", "5/21" in concept or "\\tfrac{5}{21}" in concept
          or "\\frac{5}{21}" in concept)
for name in ("n05-chained", "n05-perfect", "n05-binary-mult", "n05-binary-probing", "n05-probes"):
    fp = os.path.join(FIGS, name + ".html")
    check(f"figure {name} exists", os.path.exists(fp))
fig = read(os.path.join(FIGS, "n05-chained.html"))
if fig:
    texts = re.findall(r">([0-9]+)</text>", fig)
    check("figure n05-chained shows exactly the eight keys (plus slot numbers 0-7)",
          sorted(int(t) for t in texts if int(t) > 7) == sorted(EX_KEYS))
fig = read(os.path.join(FIGS, "n05-perfect.html"))
if fig:
    check("figure n05-perfect: every key drawn in the cell its secondary salt gives it",
          all(f"data-cell=\"{i}:{x}:{c}\"" in fig for i, v in SEC.items() for x, c in v[3].items())
          and all(f"a = {v[0]}, b = {v[1]}" in fig for v in SEC.values()))
fig = read(os.path.join(FIGS, "n05-binary-probing.html"))
if fig:
    order = [5 ^ i for i in range(16)]
    check("figure n05-binary-probing: probe order for h(x) = 5 is 5,4,7,6,1,0,3,2,13,12,15,14,9,8,11,10",
          order == [5, 4, 7, 6, 1, 0, 3, 2, 13, 12, 15, 14, 9, 8, 11, 10]
          and all(f"data-rank=\"{j}:{i}\"" in fig for i, j in enumerate(order)))

fig = read(os.path.join(FIGS, "n05-binary-mult.html"))
if fig:
    cells = re.findall(r">([01])</text>", fig)
    want = format(BX, "08b") + format(BA, "08b") + format(prod, "016b") + format(multb(BA, BX, BW, BL), "03b")
    check("figure n05-binary-mult: the bit rows are x, a, a*x (16 bits) and h(x) = 011", "".join(cells) == want)
fig = read(os.path.join(FIGS, "n05-probes.html"))
if fig:
    pts = [(float(a_), float(v)) for a_, v in re.findall(r"α = ([0-9.]+): simulated ([0-9.]+) probes", fig)]
    knuth = lambda a_: 0.5 * (1 + 1 / (1 - a_) ** 2)
    check("figure n05-probes: 8 simulated linear-probing points, each within 10% of Knuth's estimate",
          len(pts) == 8 and all(abs(v / knuth(a_) - 1) < 0.10 for a_, v in pts),
          ", ".join(f"{a_}: {v}/{knuth(a_):.2f}" for a_, v in pts))

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: " + "; ".join(FAIL))
sys.exit(1 if FAIL else 0)
