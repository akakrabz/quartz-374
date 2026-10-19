#!/usr/bin/env python3
"""Checks for every concrete claim on content/2-algorithms/01-recursion-exercises.md
(solved exercises for Chapter 1 of Erickson's Algorithms)."""
import itertools
import math
import random
from collections import deque
from fractions import Fraction

FAIL = []


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAIL.append(name)


random.seed(374)


def ruler(i):
    """rho(i): one more than the number of trailing zeros of i."""
    k = 1
    while i % 2 == 0:
        i //= 2
        k += 1
    return k


# =============================================================== Exercise 1 — Tower of Hanoi, non-recursive versions
def hanoi(n, src=0, dst=2, tmp=1, out=None):
    """The book's recursive algorithm; returns the list of moves (disk, from, to)."""
    if out is None:
        out = []
    if n > 0:
        hanoi(n - 1, src, tmp, dst, out)
        out.append((n, src, dst))
        hanoi(n - 1, tmp, dst, src, out)
    return out


def start(n):
    return [list(range(n, 0, -1)), [], []]


def legal(pegs, s, t):
    return s != t and pegs[s] and (not pegs[t] or pegs[t][-1] > pegs[s][-1])


def run(n, moves):
    """Apply moves to the start position; return final pegs, or None on an illegal move."""
    pegs = start(n)
    for d, s, t in moves:
        if not legal(pegs, s, t) or pegs[s][-1] != d:
            return None
        pegs[t].append(pegs[s].pop())
    return pegs


N1 = 12
for n in range(1, N1 + 1):
    H = hanoi(n)
    assert len(H) == 2 ** n - 1 and run(n, H) == [[], [], list(range(n, 0, -1))]

check(f"Fact H1: move i of Hanoi(n) moves disk rho(i), n <= {N1}",
      all(m[0] == ruler(i) for n in range(1, N1 + 1) for i, m in enumerate(hanoi(n), 1)))
check(f"Fact H2: disk k always moves forward (+1 mod 3) iff n-k is odd, backward iff n-k even, n <= {N1}",
      all(((t - s) % 3 == 1) == ((n - d) % 2 == 1) for n in range(1, N1 + 1) for d, s, t in hanoi(n)))
check("consecutive Hanoi moves never move the same disk (so Hanoi never undoes its previous move)",
      all(a[0] != b[0] for n in range(1, N1 + 1) for a, b in zip(hanoi(n), hanoi(n)[1:])))


def alg_a(n):
    """1(a): if n even swap the names of pegs 1 and 2; at step i make the only legal move avoiding peg i mod 3."""
    name = [0, 1, 2] if n % 2 else [0, 2, 1]  # name[j] = physical peg called j
    pegs, moves, i, unique = start(n), [], 1, True
    while True:
        avoid = name[i % 3]
        cand = [(pegs[s][-1], s, t) for s in range(3) for t in range(3)
                if avoid not in (s, t) and legal(pegs, s, t)]
        if not cand:
            return moves, unique, pegs[avoid] == list(range(n, 0, -1)) and avoid == 2
        unique &= len(cand) == 1
        d, s, t = cand[0]
        pegs[t].append(pegs[s].pop())
        moves.append((d, s, t))
        i += 1


ok_a = True
for n in range(1, N1 + 1):
    mv, uniq, stop_ok = alg_a(n)
    ok_a &= mv == hanoi(n) and uniq and stop_ok
check(f"1(a): avoid-peg-(i mod 3) algorithm = recursive Hanoi, move for move, and stops with all disks on peg 2, n <= {N1}", ok_a)


def legal_moves(pegs):
    return [(pegs[s][-1], s, t) for s in range(3) for t in range(3) if legal(pegs, s, t)]


# 1(b) as literally stated: after a move of a disk k >= 2, two legal moves involve a different disk (disk 1 can go
# to either other peg), so "the only legal move" is ambiguous.
amb = []
for n in range(2, 7):
    pegs = start(n)
    for idx, (d, s, t) in enumerate(hanoi(n)):
        pegs[t].append(pegs[s].pop())
        nxt = [m for m in legal_moves(pegs) if m[0] != d]
        if idx < 2 ** n - 2 and len(nxt) > 1:
            amb.append((n, idx + 1))
check("1(b) literal rule is ambiguous: after Hanoi move 2 for n = 2 disk 1 has two legal moves", (2, 2) in amb, str(amb[:3]))


def alg_b(n):
    """1(b) with disk 1 never returning to the peg it just left."""
    pegs = start(n)
    first = (1, 0, 1 if n % 2 == 0 else 2)
    pegs[first[2]].append(pegs[0].pop())
    moves, unique, last1_from = [first], True, 0
    while True:
        prev = moves[-1][0]
        cand = [m for m in legal_moves(pegs) if m[0] != prev and not (m[0] == 1 and m[2] == last1_from)]
        if not cand:
            return moves, unique, pegs[2] == list(range(n, 0, -1))
        unique &= len(cand) == 1
        d, s, t = cand[0]
        if d == 1:
            last1_from = s
        pegs[t].append(pegs[s].pop())
        moves.append((d, s, t))


ok_b = True
for n in range(1, N1 + 1):
    mv, uniq, fin = alg_b(n)
    ok_b &= mv == hanoi(n) and uniq and fin
check(f"1(b) with 'disk 1 never returns to the peg it just left': unique choice each step, = Hanoi, n <= {N1}", ok_b)


def alg_c(n):
    """1(c): fixed pretend disks n+1, n+2, n+3 at the bottom of pegs 0, 1, 2; parity rules + no undo."""
    pegs = [list(range(n + 1, 0, -1)), [n + 2], [n + 3]]
    pegs[0] = [n + 1] + list(range(n, 0, -1))
    moves, unique, inv_ok = [], True, True
    prev = None
    while True:
        # invariants: every peg alternates in parity from its base; exactly two tops are odd
        inv_ok &= all((p[j] - p[j + 1]) % 2 == 1 for p in pegs for j in range(len(p) - 1))
        inv_ok &= sum(p[-1] % 2 for p in pegs) == 2
        cand = []
        for s in range(3):
            for t in range(3):
                if s == t or pegs[s][-1] > n:  # pretend disks never move
                    continue
                d, top = pegs[s][-1], pegs[t][-1]
                if top < d or (top - d) % 2 == 0:
                    continue
                if prev == (d, t, s):
                    continue
                cand.append((d, s, t))
        if not cand:
            return moves, unique, inv_ok, [p[1:] for p in pegs] == [[], [], list(range(n, 0, -1))]
        unique &= len(cand) == 1
        d, s, t = cand[0]
        pegs[t].append(pegs[s].pop())
        moves.append((d, s, t))
        prev = (d, s, t)


ok_c = True
for n in range(1, N1 + 1):
    mv, uniq, inv, fin = alg_c(n)
    ok_c &= mv == hanoi(n) and uniq and inv and fin
check(f"1(c): parity/no-undo algorithm has exactly one allowed move per step, = Hanoi, stops when solved, n <= {N1}", ok_c)
check(f"1(c) invariants along Hanoi: pegs alternate in parity, exactly two odd tops, n <= {N1}",
      all(alg_c(n)[2] for n in range(1, N1 + 1)))


def ruler_hanoi(n, forward_test):
    """RulerHanoi with a given test (n, i, rho) -> move forward?"""
    pegs = start(n)
    moves, i = [], 1
    while ruler(i) <= n:
        d = ruler(i)
        s = next(p for p in range(3) if d in pegs[p])
        t = (s + 1) % 3 if forward_test(n, i, d) else (s - 1) % 3
        if not legal(pegs, s, t) or pegs[s][-1] != d:
            return moves, False
        pegs[t].append(pegs[s].pop())
        moves.append((d, s, t))
        i += 1
    return moves, True


book_rule = lambda n, i, d: (n - i) % 2 == 0  # noqa: E731  "if n - i is even, move forward"
fixed_rule = lambda n, i, d: (n - d) % 2 == 1  # noqa: E731  "if n - rho(i) is odd, move forward"
mv1, _ = ruler_hanoi(1, book_rule)
check("1(d) book's test 'n - i even => forward' fails already for n = 1 (moves disk 1 from peg 0 to peg 1)",
      mv1 == [(1, 0, 1)] and hanoi(1) == [(1, 0, 2)])
check(f"1(d) book's test gives the wrong sequence for every n <= {N1}",
      all(ruler_hanoi(n, book_rule)[0] != hanoi(n) for n in range(1, N1 + 1)))
check(f"1(d) corrected test 'n - rho(i) odd => forward' = Hanoi, n <= {N1}",
      all(ruler_hanoi(n, fixed_rule) == (hanoi(n), True) for n in range(1, N1 + 1)))
check("1(d) loop 'while rho(i) <= n' runs exactly for i = 1 .. 2^n - 1",
      all(all(ruler(i) <= n for i in range(1, 2 ** n)) and ruler(2 ** n) == n + 1 for n in range(1, N1 + 1)))
check("rho(42) = 2", ruler(42) == 2)

# =============================================================== Exercise 2 — Baguenaudier
def bag_off(k, out):
    """Moves turning bits 1..k from all 1s to all 0s."""
    if k == 0:
        return
    if k == 1:
        out.append(1)
        return
    bag_off(k - 2, out)
    out.append(k)
    bag_on(k - 2, out)
    bag_off(k - 1, out)


def bag_on(k, out):
    tmp = []
    bag_off(k, tmp)
    out.extend(reversed(tmp))


def bag_legal(bits, j):
    """bits[1..n]; bit 1 always; bit z+2 if the string ends with exactly z zeros."""
    n = len(bits) - 1
    if j == 1:
        return True
    z = 0
    while z < n and bits[z + 1] == 0:
        z += 1
    return j == z + 2 and j <= n


def bag_count(n):
    M = [0, 1]
    for k in range(2, n + 1):
        M.append(M[k - 1] + 2 * M[k - 2] + 1)
    return M[n]


seq5 = []
bag_off(5, seq5)
check("2(b): Off(5) prints 1,3,1,2,1,5,1,2,1,3,1,2,1,4,1,2,1,3,1,2,1 (the book's example)",
      seq5 == [1, 3, 1, 2, 1, 5, 1, 2, 1, 3, 1, 2, 1, 4, 1, 2, 1, 3, 1, 2, 1])
ok = True
for n in range(0, 17):
    s = []
    bag_off(n, s)
    bits = [None] + [1] * n
    for j in s:
        ok &= bag_legal(bits, j)
        bits[j] ^= 1
    ok &= bits[1:] == [0] * n
    ok &= all(a != b for a, b in zip(s, s[1:]))  # reduced
    ok &= len(s) == bag_count(n) == (2 ** (n + 1)) // 3
    ok &= len(s) == ((2 ** (n + 1) - 1) // 3 if n % 2 else (2 ** (n + 1) - 2) // 3)
    if n >= 1:
        ok &= s[0] == (1 if n % 2 else 2)
check("2(b,c): Off(n) is legal, reduced, ends at 0^n, first move 1/2 by parity; #moves = M(n) = floor(2^(n+1)/3), n <= 16", ok)
check("2(c): M(n) = M(n-1) + 2M(n-2) + 1 equals floor(2^(n+1)/3) for n <= 200",
      all(bag_count(n) == 2 ** (n + 1) // 3 for n in range(0, 201)))
check("2(c): M(5) = 21", bag_count(5) == 21)
check("2(c): M(0..7) = 0, 1, 2, 5, 10, 21, 42, 85", [bag_count(k) for k in range(8)] == [0, 1, 2, 5, 10, 21, 42, 85])

# =============================================================== Exercise 3 — Towers of Pisa
A, B, L = "A", "B", "L"


def pisa_T(m, a, b, out):
    """m disks from vertical a to vertical b (the leaning needle holds only larger disks)."""
    if m == 0:
        return
    if m == 1:
        out.append((1, 1, a, b))
        return
    pisa_S(m - 1, a, b, out)
    out.append((1, m, a, b))
    out.append((m - 1, m - 1, L, b))  # block of disks 1..m-1 off the leaning needle (bottom disk m-1)


def pisa_S(m, a, b, out):
    """m disks from vertical a onto the leaning needle (b is the other vertical)."""
    if m == 0:
        return
    pisa_T(m - 1, a, b, out)
    out.append((1, m, a, L))
    pisa_S(m - 1, b, a, out)


def pisa_run(n, moves):
    st = {A: list(range(n, 0, -1)), B: [], L: []}
    for cnt, bottom, s, t in moves:
        blk = st[s][-cnt:]
        if len(blk) != cnt or blk[0] != bottom:
            return None
        if cnt > 1 and s != L:
            return None
        if st[t] and st[t][-1] < blk[0]:
            return None
        del st[s][-cnt:]
        st[t].extend(blk)
    return st


def pisa_bfs(n):
    """Exact minimum number of moves, by BFS over positions (needle of each disk)."""
    startp, goal = tuple([A] * n), tuple([B] * n)
    dist = {startp: 0}
    q = deque([startp])
    while q:
        p = q.popleft()
        if p == goal:
            return dist[p]
        on = {x: [d for d in range(n) if p[d] == x] for x in (A, B, L)}  # disk indices 0..n-1 (0 = smallest)
        for s in (A, B, L):
            if not on[s]:
                continue
            for t in (A, B, L):
                if s == t:
                    continue
                tt = on[t][0] if on[t] else n
                maxcnt = len(on[s]) if s == L else 1
                for c in range(1, maxcnt + 1):
                    blk = on[s][:c]
                    if blk[-1] > tt:
                        break
                    np_ = list(p)
                    for d in blk:
                        np_[d] = t
                    np_ = tuple(np_)
                    if np_ not in dist:
                        dist[np_] = dist[p] + 1
                        q.append(np_)


def fib(k):
    a, b = 0, 1
    for _ in range(k):
        a, b = b, a + b
    return a


ok = True
for n in range(1, 15):
    mv = []
    pisa_T(n, A, B, mv)
    st = pisa_run(n, mv)
    ok &= st is not None and st[B] == list(range(n, 0, -1)) and len(mv) == 2 * fib(n + 1) - 1
check("3: Pisa algorithm is legal, ends on the other vertical needle, uses 2F(n+1) - 1 moves, n <= 14", ok)
ok = True
for m in range(1, 15):
    mv = []
    pisa_S(m, A, B, mv)
    ok &= len(mv) == 2 * fib(m + 2) - 3
check("3: moving m disks onto the leaning needle takes S(m) = 2F(m+2) - 3 moves, m <= 14", ok)
bfs3 = [pisa_bfs(n) for n in range(1, 10)]
check("3: 2F(n+1) - 1 is optimal (BFS), n <= 9", bfs3 == [2 * fib(n + 1) - 1 for n in range(1, 10)], str(bfs3))
check("3: move counts 1, 3, 5, 9, 15, 25 for n = 1..6",
      [2 * fib(n + 1) - 1 for n in range(1, 7)] == [1, 3, 5, 9, 15, 25])
mv7 = []
pisa_T(7, A, B, mv7)
fig117 = [(1, 1, A, B), (1, 2, A, L), (1, 1, B, L), (1, 3, A, B), (2, 2, L, B), (1, 4, A, L), (1, 1, B, L)]
check("3: for n = 7 the first 7 moves are those drawn in Figure 1.17 (5th move: two disks off the leaning needle)",
      mv7[:7] == fig117, str(mv7[:7]))


# =============================================================== Exercise 4(a) and 5(a) — restricted Hanoi
def leaf_to_leaf(m, x, y, hub, out):
    if m == 0:
        return
    leaf_to_leaf(m - 1, x, y, hub, out)
    out.append((m, x, hub))
    leaf_to_leaf(m - 1, y, x, hub, out)
    out.append((m, hub, y))
    leaf_to_leaf(m - 1, x, y, hub, out)


def hub_to_leaf(m, y, hub, other, out):
    if m == 0:
        return
    hub_to_leaf(m - 1, other, hub, y, out)
    out.append((m, hub, y))
    leaf_to_leaf(m - 1, other, y, hub, out)


def gen_run(n, moves, src, dst, allowed):
    pegs = {p: [] for p in (0, 1, 2)}
    pegs[src] = list(range(n, 0, -1))
    for d, s, t in moves:
        if (s, t) not in allowed or not pegs[s] or pegs[s][-1] != d or (pegs[t] and pegs[t][-1] < d):
            return False
        pegs[t].append(pegs[s].pop())
    return pegs[dst] == list(range(n, 0, -1))


def restricted_bfs(n, src, dst, allowed):
    startp, goal = tuple([src] * n), tuple([dst] * n)
    dist = {startp: 0}
    q = deque([startp])
    while q:
        p = q.popleft()
        if p == goal:
            return dist[p]
        tops = {}
        for d in range(n):
            tops.setdefault(p[d], d)
        for s, t in allowed:
            if s in tops and (t not in tops or tops[t] > tops[s]):
                np_ = list(p)
                np_[tops[s]] = t
                np_ = tuple(np_)
                if np_ not in dist:
                    dist[np_] = dist[p] + 1
                    q.append(np_)


HUB0 = {(0, 1), (1, 0), (0, 2), (2, 0)}
ok = True
for n in range(0, 11):
    mv = []
    hub_to_leaf(n, 2, 0, 1, mv)
    ok &= gen_run(n, mv, 0, 2, HUB0) and len(mv) == (3 ** n - 1) // 2
    mv = []
    leaf_to_leaf(n, 1, 2, 0, mv)
    ok &= gen_run(n, mv, 1, 2, HUB0) and len(mv) == 3 ** n - 1
check("4(a): every move touches peg 0; 0 -> 2 takes (3^n - 1)/2 moves, leaf -> leaf takes 3^n - 1, n <= 10", ok)
check("4(a): (3^n - 1)/2 is optimal (BFS), n <= 8",
      all(restricted_bfs(n, 0, 2, HUB0) == (3 ** n - 1) // 2 for n in range(1, 9)))
check("5(a) = end-to-end on a row of 3 pegs (middle = hub): 3^n - 1 is optimal (BFS), n <= 8",
      all(restricted_bfs(n, 1, 2, HUB0) == 3 ** n - 1 for n in range(1, 9)))
check("4(a) and 5(a) differ: (3^n-1)/2 != 3^n - 1 for n >= 1; e.g. n = 1: 1 vs 2 moves",
      (3 ** 1 - 1) // 2 == 1 and 3 ** 1 - 1 == 2)


# =============================================================== Exercise 5(b) — k = n+1 pegs in a row
def shift(m, a, d, pos, out):
    """Move disks 1..m (stacked on peg a, disks > m out of the way) to peg a + d, d >= m."""
    if m == 0:
        return

    def mv(disk, s, t):
        out.append((disk, s, t))
        pos[disk] = t

    for i in range(1, m):  # spread: disk i walks to peg a + d + 1 - i
        for p in range(a, a + d + 1 - i):
            mv(i, p, p + 1)
    for p in range(a, a + d):  # disk m walks right; a smaller disk in the way hops left to peg a
        blockers = [i for i in range(1, m) if pos[i] == p + 1]
        for i in blockers:
            for q in range(p + 1, a, -1):
                mv(i, q, q - 1)
        mv(m, p, p + 1)
    shift(m - 1, a, d, pos, out)


def row_run(n, k, moves):
    pegs = {p: [] for p in range(1, k + 1)}
    pegs[1] = list(range(n, 0, -1))
    for d, s, t in moves:
        if abs(s - t) != 1 or not (1 <= t <= k) or not pegs[s] or pegs[s][-1] != d or (pegs[t] and pegs[t][-1] < d):
            return False
        pegs[t].append(pegs[s].pop())
    return pegs[k] == list(range(n, 0, -1))


ok = True
counts5 = []
for n in range(1, 31):
    out = []
    shift(n, 1, n, {i: 1 for i in range(1, n + 1)}, out)
    counts5.append(len(out))
    ok &= row_run(n, n + 1, out) and 3 * len(out) == 2 * n ** 3 + 3 * n ** 2 - 2 * n
check("5(b): Shift(n, 1, n) is legal on n+1 pegs in a row and uses (2n^3 + 3n^2 - 2n)/3 moves, n <= 30", ok,
      str(counts5[:6]))
check("5(b): the per-round count n + (m-1)(2n+1-(m-1)) sums to (2n^3+3n^2-2n)/3",
      all(sum(n + (m - 1) * (2 * n + 1 - (m - 1)) for m in range(1, n + 1)) * 3 == 2 * n ** 3 + 3 * n ** 2 - 2 * n
          for n in range(1, 60)))
check("5(b): n = 2 gives 8 = 3^2 - 1 (same as part (a))", counts5[1] == 8)

# =============================================================== Exercises 6, 7, 8 — recurrences
def at_powers(a, b, f, K):
    """T(b^k) for k = 0..K with T(1) = 1, exact (Fraction) when f returns Fractions."""
    T = [Fraction(1)]
    for k in range(1, K + 1):
        T.append(a * T[-1] + f(b ** k, k))
    return T


def settles(ratios, tol):
    """ratios bounded and successive differences eventually below tol."""
    return max(ratios) / min(ratios) < 100 and abs(ratios[-1] - ratios[-2]) < tol


rec6 = {
    "A": (2, 4, lambda n, k: Fraction(2 ** k), lambda n, k: math.sqrt(n) * k),           # sqrt(n) log n
    "B": (2, 4, lambda n, k: Fraction(n), lambda n, k: n),
    "C": (2, 4, lambda n, k: Fraction(n * n), lambda n, k: n * n),
    "E": (3, 3, lambda n, k: Fraction(n), lambda n, k: n * k),
    "F": (3, 3, lambda n, k: Fraction(n * n), lambda n, k: n * n),
    "H": (4, 2, lambda n, k: Fraction(n), lambda n, k: n * n),
    "I": (4, 2, lambda n, k: Fraction(n * n), lambda n, k: n * n * k),
}
for name, (a, b, f, g) in rec6.items():
    T = at_powers(a, b, f, 40)
    r = [float(T[k]) / g(b ** k, k) for k in range(5, 41)]
    check(f"6: {name}(n) / claimed bound settles at n = {b}^k, k <= 40", settles(r, 0.03), f"last ratio {r[-1]:.4f}")
# D and G have sqrt(n) with n = 3^k, 2^k: use floats
for name, (a, b, g) in {"D": (3, 3, lambda n: n), "G": (4, 2, lambda n: n * n)}.items():
    T = [1.0]
    for k in range(1, 61):
        T.append(a * T[-1] + math.sqrt(b ** k))
    r = [T[k] / g(b ** k) for k in range(5, 61)]
    check(f"6: {name}(n) / claimed bound settles at n = {b}^k, k <= 60", settles(r, 1e-3), f"last ratio {r[-1]:.4f}")
ratios6 = [2 / math.sqrt(4), 2 / 4, 2 / 16, 3 / math.sqrt(3), 3 / 3, 3 / 9, 4 / math.sqrt(2), 4 / 2, 4 / 4]
check("6: level-sum ratios a/b^c: A 1, B 1/2, C 1/8, D sqrt3, E 1, F 1/3, G 2sqrt2, H 2, I 1",
      all(abs(x - y) < 1e-12 for x, y in zip(ratios6, [1, 0.5, 0.125, math.sqrt(3), 1, 1 / 3, 2 * math.sqrt(2), 2, 1])))


def memo_rec(terms, f, base=1):
    cache = {}

    def T(n):
        if n <= 1:
            return base
        if n in cache:
            return cache[n]
        v = sum(c * T(n // d) for c, d in terms) + f(n)
        cache[n] = v
        return v
    return T


# floor versions of all nine, bounded ratio over a range of n
fl6 = {
    "A": ([(2, 4)], lambda n: math.sqrt(n), lambda n: math.sqrt(n) * math.log(n)),
    "B": ([(2, 4)], lambda n: n, lambda n: n),
    "C": ([(2, 4)], lambda n: n * n, lambda n: n * n),
    "D": ([(3, 3)], lambda n: math.sqrt(n), lambda n: n),
    "E": ([(3, 3)], lambda n: n, lambda n: n * math.log(n)),
    "F": ([(3, 3)], lambda n: n * n, lambda n: n * n),
    "G": ([(4, 2)], lambda n: math.sqrt(n), lambda n: n * n),
    "H": ([(4, 2)], lambda n: n, lambda n: n * n),
    "I": ([(4, 2)], lambda n: n * n, lambda n: n * n * math.log(n)),
}
for name, (terms, f, g) in fl6.items():
    T = memo_rec(terms, f)
    ns = [random.randint(1000, 10 ** 9) for _ in range(300)] + [10 ** 9]
    r = [T(n) / g(n) for n in ns]
    check(f"6: {name}(n) with floors stays within a constant factor of the claimed bound, 1e3 <= n <= 1e9",
          max(r) / min(r) < 8, f"ratio range {min(r):.3f}..{max(r):.3f}")

# 7(j), 7(k), 7(l) with floors
J = memo_rec([(1, 2), (1, 3), (1, 6)], lambda n: n)
K = memo_rec([(1, 2), (2, 3), (3, 4)], lambda n: n * n)
Lr = memo_rec([(1, 15), (1, 10), (2, 6)], lambda n: math.sqrt(n))


def solve_rho():
    lo, hi = 0.5, 1.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if (1 / 15) ** mid + (1 / 10) ** mid + 2 * (1 / 6) ** mid > 1:
            lo = mid
        else:
            hi = mid
    return lo


rho = solve_rho()
check("7(l): rho with (1/15)^rho + (1/10)^rho + 2(1/6)^rho = 1 is 0.6596 (to 4 places), between 1/2 and 1",
      abs(rho - 0.6596) < 5e-5 and 0.5 < rho < 1, f"rho = {rho:.6f}")
check("7(k): level ratio 1/4 + 2/9 + 3/16 = 95/144 < 1",
      Fraction(1, 4) + 2 * Fraction(1, 9) + 3 * Fraction(1, 16) == Fraction(95, 144))
rl = 1 / math.sqrt(15) + 1 / math.sqrt(10) + 2 / math.sqrt(6)
check("7(l): level ratio 1/sqrt15 + 1/sqrt10 + 2/sqrt6 = 1.39 > 1, so d = 1/(r-1) = 2.56 works",
      abs(rl - 1.3909) < 1e-4 and abs(1 / (rl - 1) - 2.558) < 1e-3, f"r = {rl:.5f}")
for name, T, g in [("J", J, lambda n: n * math.log(n)), ("K", K, lambda n: n * n), ("L", Lr, lambda n: n ** rho)]:
    ns = [random.randint(1000, 10 ** 12) for _ in range(300)] + [10 ** 12]
    r = [T(n) / g(n) for n in ns]
    check(f"7: {name}(n) with floors stays within a constant factor of the claimed bound, 1e3 <= n <= 1e12",
          max(r) / min(r) < 4, f"ratio range {min(r):.3f}..{max(r):.3f}")


# real-valued versions (no floors), base T(x) = 1 for x < 1: ratio settles over growing n
def real_rec(terms, f):
    cache = {}

    def T(x):
        if x < 1:
            return 1.0
        key = round(x, 9)
        if key in cache:
            return cache[key]
        v = sum(c * T(x / d) for c, d in terms) + f(x)
        cache[key] = v
        return v
    return T


Jr = real_rec([(1, 2), (1, 3), (1, 6)], lambda x: x)
Lrr = real_rec([(1, 15), (1, 10), (2, 6)], lambda x: math.sqrt(x))
rj = [Jr(10.0 ** e) / (10.0 ** e * math.log(10.0 ** e)) for e in range(3, 16)]
check("7(j): real-valued J(n)/(n ln n) lies between 1/ln 6 and 1/ln 2 + small, n = 1e3..1e15",
      all(1 / math.log(6) * 0.9 < x < 1 / math.log(2) * 1.5 for x in rj), f"{rj[0]:.3f}..{rj[-1]:.3f}")
okj = all(x * math.log(x, 6) <= Jr(x) <= x * (math.log2(x) + 1) + 6 * x for x in [10.0 ** e for e in range(0, 16)]
          + [random.uniform(1, 1e9) for _ in range(200)])
check("7(j): n log_6 n <= J(n) <= n (log_2 n + 1) + 6n (real-valued, base J(x) = 1 for x < 1)", okj)
Kr = real_rec([(1, 2), (2, 3), (3, 4)], lambda x: x * x)
rk = [Kr(x) / (x * x) for x in [10.0 ** e for e in range(1, 16)] + [random.uniform(10, 1e9) for _ in range(200)]]
rk5 = [Kr(x) / (x * x) for x in [10.0 ** e for e in range(5, 16)] + [random.uniform(1e5, 1e9) for _ in range(200)]]
check("7(k): K(n)/n^2 >= 1 always and <= 144/49 + 0.01 once the leaf terms are negligible (n >= 1e5; 144/49 = 2.9388)",
      min(rk) >= 1 and max(rk5) < 144 / 49 + 0.01, f"{min(rk):.4f}..{max(rk5):.4f} (n >= 1e5), max {max(rk):.4f} overall")
fl = lambda t: (1 / 15) ** t + (1 / 10) ** t + 2 * (1 / 6) ** t  # noqa: E731
check("7(l): characteristic sum is r = 1.39 at rho = 1/2 and exactly 1/2 at rho = 1, decreasing in between",
      abs(fl(0.5) - rl) < 1e-12 and abs(fl(1) - 0.5) < 1e-12 and all(fl(t / 100) > fl((t + 1) / 100) for t in range(50, 100)))
rlr = [Lrr(10.0 ** e) / (10.0 ** e) ** rho for e in range(4, 16)]
check("7(l): real-valued L(n)/n^rho stays in a narrow band, n = 1e4..1e15", max(rlr) / min(rlr) < 1.5,
      f"{min(rlr):.3f}..{max(rlr):.3f}")
# substitution proof of 7(l): L(n) <= c n^rho - d sqrt(n) with d = 1/(r-1) is consistent
check("7(l) substitution: with d = 1/(r-1) the inequality c n^rho - d sqrt n is preserved by the recurrence",
      abs(sum(a / b ** rho for a, b in [(1, 15), (1, 10), (2, 6)]) - 1) < 1e-12
      and abs(sum(a / math.sqrt(b) for a, b in [(1, 15), (1, 10), (2, 6)]) * (1 / (rl - 1)) - 1 - 1 / (rl - 1)) < 1e-12)

# 8(m), 8(n) at powers of two, exact
Mx = at_powers(2, 2, lambda n, k: Fraction(n * k), 60)
check("8(m): M(2^k) = 2^k (1 + k(k+1)/2) with M(1) = 1, k <= 60",
      all(Mx[k] == 2 ** k * (1 + Fraction(k * (k + 1), 2)) for k in range(61)))
Nx = at_powers(2, 2, lambda n, k: Fraction(n, k), 200)
check("8(n): N(2^k) = 2^k (1 + H_k) with N(1) = 1, k <= 200",
      all(Nx[k] == 2 ** k * (1 + sum(Fraction(1, j) for j in range(1, k + 1))) for k in range(0, 201)))
check("8(n): H_k / ln k -> 1 (so N(n) = Theta(n log log n)); H_200/ln 200 within 15%",
      abs(float(Nx[200] / 2 ** 200 - 1) / math.log(200) - 1) < 0.15)


# 8(p): P(n) = sqrt(n) P(sqrt n) + n, base P(n) = 1 for n <= 2 (real-valued)
def Pp(x):
    return 1.0 if x <= 2 else math.sqrt(x) * Pp(math.sqrt(x)) + x


check("8(p): P(2^(2^k)) = 2^(2^k) (k + 1/2) exactly (k <= 9, via the exact identity P(n)/n = P(sqrt n)/sqrt n + 1)",
      all(abs(Pp(2.0 ** (2 ** k)) / 2.0 ** (2 ** k) - (k + 0.5)) < 1e-9 for k in range(0, 10)))
rp = [Pp(10.0 ** e) / (10.0 ** e * math.log2(math.log2(10.0 ** e))) for e in range(2, 300, 7)]
check("8(p): P(n) / (n lg lg n) bounded in [0.5, 1.5] for n = 1e2..1e299", all(0.5 < x < 1.5 for x in rp),
      f"{min(rp):.3f}..{max(rp):.3f}")


# 8(q): Q(n) = sqrt(2n) Q(sqrt(2n)) + sqrt(n), base Q(n) = 1 for n <= 4
def Qq(x):
    return 1.0 if x <= 4 else math.sqrt(2 * x) * Qq(math.sqrt(2 * x)) + math.sqrt(x)


rq = [Qq(10.0 ** e) / (10.0 ** e * math.log2(10.0 ** e)) for e in range(2, 300, 3)]
check("8(q): Q(n) / (n lg n) stays in a constant band for n = 1e2..1e299", max(rq) / min(rq) < 4 and min(rq) > 0.1,
      f"{min(rq):.3f}..{max(rq):.3f}")
# the n_k = 2 t^(1/2^k) description: arguments decrease to 2, never below
xs = [1e12]
while xs[-1] > 4:
    xs.append(math.sqrt(2 * xs[-1]))
check("8(q): arguments n_{k+1} = sqrt(2 n_k) satisfy n_k/2 = (n/2)^(1/2^k) and stay above 2",
      all(abs(xs[k] / 2 - (1e12 / 2) ** (1 / 2 ** k)) < 1e-6 * xs[k] for k in range(len(xs))) and min(xs) > 2)
levels = []
x = 1e12
cnt = 1.0
while x > 4:
    levels.append(cnt * math.sqrt(x))
    cnt *= math.sqrt(2 * x)
    x = math.sqrt(2 * x)
check("8(q): each level sum is at least twice the previous one",
      all(levels[k + 1] >= 2 * levels[k] for k in range(len(levels) - 1)))
okL = True
for e in range(1, 300, 3):
    n0 = 10.0 ** e
    x, L_ = n0, 0
    while x > 4:
        x = math.sqrt(2 * x)
        L_ += 1
    okL &= L_ == math.ceil(math.log2(math.log2(n0 / 2)) - 1e-12) and math.log2(n0 / 2) <= 2 ** L_ < 2 * math.log2(n0 / 2) + 1e-9
check("8(q): depth L = ceil(lg lg(n/2)) and lg(n/2) <= 2^L < 2 lg(n/2), n = 1e1..1e298", okL)
check("8(q): level k sum = 2^k n / sqrt(n_k) (n = 1e12)",
      all(abs(levels[k] - 2 ** k * 1e12 / math.sqrt(xs[k])) < 1e-6 * levels[k] for k in range(len(levels))))


# =============================================================== Exercise 9 — pancakes
def flip(s, k):
    return s[:k][::-1] + s[k:]


def pancake_sort(s):
    s, flips = list(s), 0
    for k in range(len(s), 1, -1):
        p = s.index(max(s[:k])) + 1
        if p == k:
            continue
        if p != 1:
            s = flip(s, p)
            flips += 1
        s = flip(s, k)
        flips += 1
    return s, flips


ok, worst = True, {}
for n in range(1, 9):
    mx = 0
    for p in itertools.permutations(range(1, n + 1)):
        s, f = pancake_sort(p)
        ok &= s == sorted(p)
        mx = max(mx, f)
    worst[n] = mx
check("9(a): algorithm sorts every stack, n <= 8", ok)
check("9(a): worst case is exactly 2n - 3 flips for 2 <= n <= 8 (0 for n = 1)",
      all(worst[n] == 2 * n - 3 for n in range(2, 9)) and worst[1] == 0, str(worst))


def W(n):
    if n == 2:
        return [2, 1]
    r = W(n - 1)[::-1]
    return [r[0], n] + r[1:]


check("9(a): the family W_2 = (2,1), W_n = (r1, n, r2, ..., r_{n-1}) with r = reverse(W_{n-1}) needs 2n - 3 flips",
      all(pancake_sort(W(n))[1] == 2 * n - 3 for n in range(2, 40)))
check("9(a): W_5 = 1 5 3 4 2", W(5) == [1, 5, 3, 4, 2])


def adjacencies(s):
    t = list(s) + [len(s) + 1]
    return sum(abs(t[i] - t[i + 1]) == 1 for i in range(len(s)))


ok = True
for n in range(1, 8):
    for p in itertools.permutations(range(1, n + 1)):
        a = adjacencies(p)
        ok &= all(abs(adjacencies(flip(list(p), k)) - a) <= 1 for k in range(1, n + 1))
check("9(b): a flip changes the number of adjacencies (plate counted) by at most 1, all stacks n <= 7", ok)


def bad_stack(n):
    same = [v for v in range(1, n + 1) if v % 2 == n % 2]
    other = [v for v in range(1, n + 1) if v % 2 != n % 2]
    return same + other


def min_flips(start_):
    n = len(start_)
    goal = tuple(range(1, n + 1))
    dist = {tuple(start_): 0}
    q = deque([tuple(start_)])
    while q:
        s = q.popleft()
        if s == goal:
            return dist[s]
        for k in range(2, n + 1):
            t = tuple(flip(list(s), k))
            if t not in dist:
                dist[t] = dist[s] + 1
                q.append(t)


check("9(b): bad_stack(n) has no adjacencies for 4 <= n <= 200",
      all(adjacencies(bad_stack(n)) == 0 for n in range(4, 201)))
check("9(b): examples 2 4 1 3 (n=4) and 1 3 5 2 4 (n=5)", bad_stack(4) == [2, 4, 1, 3] and bad_stack(5) == [1, 3, 5, 2, 4])
mf = {n: min_flips(bad_stack(n)) for n in range(4, 10)}
check("9(b): bad_stack(n) needs at least n flips (BFS), 4 <= n <= 9", all(mf[n] >= n for n in mf), str(mf))


def burnt_sort(s):
    """s: list of (size, up) top to bottom; up=True means burned side up. Goal: sorted, all burned sides down."""
    def bflip(s, k):
        return [(v, not u) for v, u in s[:k][::-1]] + s[k:]
    s, flips = list(s), 0
    for k in range(len(s), 0, -1):
        p = max(range(k), key=lambda i: s[i][0]) + 1
        if p == k and not s[k - 1][1]:
            continue
        if p != 1:
            s = bflip(s, p)
            flips += 1
        if not s[0][1]:  # burned side down on top: flip it alone
            s = bflip(s, 1)
            flips += 1
        s = bflip(s, k)
        flips += 1
    return s, flips


ok, worstb = True, {}
for n in range(1, 7):
    mx = 0
    for p in itertools.permutations(range(1, n + 1)):
        for ups in itertools.product([False, True], repeat=n):
            s, f = burnt_sort(list(zip(p, ups)))
            ok &= s == [(v, False) for v in range(1, n + 1)]
            mx = max(mx, f)
    worstb[n] = mx
check("9(c): burned-pancake algorithm sorts every stack burned side down, n <= 6", ok)
check("9(c): worst case is exactly 3n - 2 flips, n <= 6", all(worstb[n] == 3 * n - 2 for n in worstb), str(worstb))
check("9(c): sorted stack with every burned side up needs 3n - 2 flips, n <= 50",
      all(burnt_sort([(v, True) for v in range(1, n + 1)])[1] == 3 * n - 2 for n in range(1, 51)))


# =============================================================== Exercise 10(a) — median-of-three, stable partition
def m3_perm(n):
    q = (n + 1) // 2 - 1
    return list(range(1, 2 * q, 2)) + list(range(2, 2 * q + 1, 2)) + list(range(2 * q + 1, n + 1))


def m3_quicksort(A, log):
    n = len(A)
    if n <= 1:
        return A, 0
    mid = (n + 1) // 2  # 1-indexed middle, ceil(n/2)
    trio = sorted([A[0], A[mid - 1], A[n - 1]])
    piv = trio[1]
    log.append((n, sorted(A).index(piv) + 1))
    left = [x for x in A if x < piv]   # stable partition
    right = [x for x in A if x > piv]
    comps = n - 1
    L_, c1 = m3_quicksort(left, log)
    R_, c2 = m3_quicksort(right, log)
    return L_ + [piv] + R_, comps + c1 + c2


check("10(a): the permutation for n = 9 is 1 3 5 7 2 4 6 8 9 and for n = 10 is 1 3 5 7 2 4 6 8 9 10",
      m3_perm(9) == [1, 3, 5, 7, 2, 4, 6, 8, 9] and m3_perm(10) == [1, 3, 5, 7, 2, 4, 6, 8, 9, 10])
ok = True
for n in range(1, 400):
    P = m3_perm(n)
    ok &= sorted(P) == list(range(1, n + 1))
    log = []
    out, comps = m3_quicksort(P, log)
    ok &= out == list(range(1, n + 1))
    ok &= all(rank == 2 for size, rank in log if size >= 3)
    ok &= comps == sum(k - 1 for k in range(n, 1, -2)) if n >= 2 else True
check("10(a): on m3_perm(n) every call with >= 3 elements picks the 2nd smallest as pivot, n < 400", ok)
check("10(a): partition comparisons (n-1)+(n-3)+... = floor(n^2/4)",
      all(sum(k - 1 for k in range(n, 1, -2)) == n * n // 4 for n in range(1, 500)))


def m3_shift(n):
    P = m3_perm(n)
    log = []
    piv = sorted([P[0], P[(n + 1) // 2 - 1], P[-1]])[1]
    rest = [x for x in P if x > piv]
    return rest == [x + 2 for x in m3_perm(n - 2)]


check("10(a): after partition the right part is m3_perm(n-2) + 2 (the induction step), 3 <= n < 300",
      all(m3_shift(n) for n in range(3, 300)))


# =============================================================== Exercise 11 — StoogeSort
def stooge(A, lo, n, ceil=True, stats=None):
    if n == 2:
        if stats is not None:
            stats[0] += 1
        if A[lo] > A[lo + 1]:
            A[lo], A[lo + 1] = A[lo + 1], A[lo]
            if stats is not None:
                stats[1] += 1
    elif n > 2:
        m = -(-2 * n // 3) if ceil else (2 * n) // 3
        stooge(A, lo, m, ceil, stats)
        stooge(A, lo + n - m, m, ceil, stats)
        stooge(A, lo, m, ceil, stats)


def inversions_brute(A):
    return sum(A[i] > A[j] for i in range(len(A)) for j in range(i + 1, len(A)))


ok, swaps_ok, comps_ok = True, True, True
memoC = {0: 0, 1: 0, 2: 1}


def Cst(n):
    if n not in memoC:
        memoC[n] = 3 * Cst(-(-2 * n // 3))
    return memoC[n]


for n in range(0, 9):
    for p in itertools.permutations(range(n)):
        A = list(p)
        st = [0, 0]
        stooge(A, 0, n, True, st)
        ok &= A == sorted(p)
        swaps_ok &= st[1] == inversions_brute(list(p)) <= n * (n - 1) // 2
        comps_ok &= st[0] == Cst(n)
for n in range(9, 15):
    for bits in itertools.product([0, 1], repeat=n):
        A = list(bits)
        stooge(A, 0, n)
        ok &= A == sorted(bits)
for _ in range(300):
    n = random.randint(9, 40)
    A0 = [random.randint(0, 5) for _ in range(n)]
    A = list(A0)
    st = [0, 0]
    stooge(A, 0, n, True, st)
    ok &= A == sorted(A0)
    swaps_ok &= st[1] == inversions_brute(A0)
    comps_ok &= st[0] == Cst(n)
check("11(a): StoogeSort sorts all permutations n <= 8, all 0/1 arrays 9 <= n <= 14, random arrays with repeats", ok)
B = [3, 4, 1, 2]
stooge(B, 0, 4, ceil=False)
check("11(b): floor version leaves [3,4,1,2] unsorted (halves of size 2 never interact)", B == [3, 4, 1, 2])
okf = True
for p in itertools.permutations(range(4)):
    A = list(p)
    stooge(A, 0, 4, ceil=False)
    okf &= (A == sorted(p)) == (sorted(p[:2])[1] < sorted(p[2:])[0])
check("11(b): floor version on n = 4 sorts exactly the inputs whose first half is already below the second half", okf)
check("11(c): instrumented comparison count = C(n) with C(0)=C(1)=0, C(2)=1, C(n)=3C(ceil(2n/3))", comps_ok)
alpha = math.log(3) / math.log(1.5)
check("11(d): log_{3/2} 3 = 2.7095", abs(alpha - 2.7095) < 5e-5, f"{alpha:.6f}")
rs = [Cst(n) / n ** alpha for n in range(2, 200001)]
check("11(d): with the ceiling, 0.15 < C(n) / n^log_{3/2}3 < 0.81 for all 2 <= n <= 200000",
      min(rs) > 0.15 and max(rs) < 0.81, f"{min(rs):.4f}..{max(rs):.4f}")


def Creal(x):
    return 1.0 if x <= 2 else 3 * Creal(2 * x / 3)


okr = all((x / 2) ** alpha * (1 - 1e-9) <= Creal(x) < 3 * (x / 2) ** alpha
          for x in [random.uniform(4 / 3 + 1e-9, 1e7) for _ in range(2000)])
check("11(d): real-valued C(x) (C = 1 on (4/3, 2]) satisfies (x/2)^alpha <= C(x) < 3 (x/2)^alpha", okr)
check("11(d): without the ceiling, C(2 (3/2)^k) = 3^k exactly (3^k = (n/2)^alpha)",
      all(abs(3 ** k - (2 * 1.5 ** k / 2) ** alpha) < 1e-6 * 3 ** k for k in range(0, 40)))
check("11(e): swaps = number of inversions of the input <= n(n-1)/2", swaps_ok)


# =============================================================== Exercise 12(b)-(e) — Cruel and Unusual
def unusual(A, lo, n, variant, stats):
    if n == 2:
        stats[0] += 1
        if A[lo] > A[lo + 1]:
            A[lo], A[lo + 1] = A[lo + 1], A[lo]
        return
    if variant != "noloop":
        for i in range(n // 4):
            a, b = lo + i + n // 4, lo + i + n // 2
            A[a], A[b] = A[b], A[a]
    if variant == "swapped":
        unusual(A, lo, n // 2, variant, stats)
        unusual(A, lo + n // 4, n // 2, variant, stats)
        unusual(A, lo + n // 2, n // 2, variant, stats)
    else:
        unusual(A, lo, n // 2, variant, stats)
        unusual(A, lo + n // 2, n // 2, variant, stats)
        unusual(A, lo + n // 4, n // 2, variant, stats)


def cruel(A, lo, n, variant="orig", stats=None):
    if stats is None:
        stats = [0]
    if n > 1:
        cruel(A, lo, n // 2, variant, stats)
        cruel(A, lo + n // 2, n // 2, variant, stats)
        unusual(A, lo, n, variant, stats)
    return stats


ok = True
for n in (2, 4, 8):
    for p in itertools.permutations(range(n)):
        A = list(p)
        cruel(A, 0, n)
        ok &= A == sorted(p)
for bits in itertools.product([0, 1], repeat=16):
    A = list(bits)
    cruel(A, 0, 16)
    ok &= A == sorted(bits)
check("12: Cruel sorts all permutations for n = 2, 4, 8 and all 0/1 arrays for n = 16", ok)
for variant in ("noloop", "swapped"):
    A = [3, 4, 1, 2]
    cruel(A, 0, 4, variant)
    check(f"12: variant '{variant}' turns [3,4,1,2] into {A} (not sorted)",
          A != [1, 2, 3, 4] and A == ([3, 1, 4, 2] if variant == "noloop" else [1, 3, 2, 4]))
Ucomp = {2: 1}
for k in range(2, 21):
    Ucomp[2 ** k] = 3 * Ucomp[2 ** (k - 1)]
check("12(d): Unusual(n) makes 3^(lg n - 1) = n^lg3 / 3 comparisons",
      all(abs(Ucomp[2 ** k] - (2 ** k) ** math.log2(3) / 3) < 1e-6 * Ucomp[2 ** k] for k in range(1, 21)))
ok = True
for k in range(1, 12):
    n = 2 ** k
    st = [0]
    unusual(list(range(n)), 0, n, "orig", st)
    ok &= st[0] == Ucomp[n]
check("12(d): instrumented Unusual comparison count matches, n = 2..2048", ok)
Ccr = {1: 0}
for k in range(1, 21):
    Ccr[2 ** k] = 2 * Ccr[2 ** (k - 1)] + Ucomp[2 ** k]
check("12(e): Cruel comparisons C(n) = 2C(n/2) + n^lg3/3 = n^lg3 - n, so Theta(n^lg3)",
      all(Ccr[2 ** k] == 3 ** k - 2 ** k for k in range(1, 21)))
ok = True
for k in range(1, 11):
    n = 2 ** k
    A = list(range(n))
    random.shuffle(A)
    ok &= cruel(A, 0, n)[0] == Ccr[n]
check("12(e): instrumented Cruel comparison count = 3^k - 2^k, n = 2..1024", ok)


# =============================================================== Exercise 13 — counting inversions
def count_inv(A):
    """Sorts A in place (mergesort); returns the number of inversions it had."""
    n = len(A)
    if n <= 1:
        return 0
    m = n // 2
    Lh, Rh = A[:m], A[m:]
    x = count_inv(Lh)
    y = count_inv(Rh)
    i = j = z = 0
    for k in range(n):
        if j >= len(Rh) or (i < m and Lh[i] <= Rh[j]):
            A[k] = Lh[i]
            i += 1
        else:
            A[k] = Rh[j]
            j += 1
            z += m - i
    return x + y + z


ok = True
for n in range(0, 9):
    for p in itertools.permutations(range(n)):
        A = list(p)
        ok &= count_inv(A) == inversions_brute(list(p)) and A == sorted(p)
for n in range(0, 9):
    for t in itertools.product(range(3), repeat=n):
        A = list(t)
        ok &= count_inv(A) == inversions_brute(list(t))
for _ in range(200):
    n = random.randint(0, 300)
    A0 = [random.randint(0, 50) for _ in range(n)]
    A = list(A0)
    ok &= count_inv(A) == inversions_brute(A0) and A == sorted(A0)
check("13: mergesort-based count = brute-force count (all perms n <= 8, all arrays over {0,1,2} n <= 8, random)", ok)
check("13: reversed array of size n has n(n-1)/2 inversions, n <= 100",
      all(count_inv(list(range(n, 0, -1))) == n * (n - 1) // 2 for n in range(101)))

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: {FAIL}")
