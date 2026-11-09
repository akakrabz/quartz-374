#!/usr/bin/env python3
"""Checks for content/4-lecture-notes/11-disjoint-sets.md (Erickson, Director's Cut 11, Disjoint Sets).

Every data structure is implemented exactly as the page (and the note) states it: reversed trees with plain Union,
union by depth, threaded trees (as printed, and with the Null-terminated thread), WeightedUnion, union by rank with
recursive path-compressing Find. Invariants are checked after every operation of long random and adversarial runs;
the Seidel-Sharir quantities (pointer assignments of Compress, the reordering of Unions before Compresses, the split of
a forest at rank s) are recomputed by simulation; lg*, lg**, lg^{*c}, alpha and the Ackermann hierarchy are computed
exactly (big integers) where they are finite and small enough."""
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
PAGE = os.path.join(ROOT, "content", "4-lecture-notes", "11-disjoint-sets.md")
FAIL = []
random.seed(11)
sys.setrecursionlimit(10000)


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAIL.append(name)


def flg(n):
    return n.bit_length() - 1  # floor(lg n) for n >= 1


# =====================================================================================================
# 11.1 reversed trees, plain Union (parent(ybar) <- xbar)
class Plain:
    def __init__(self):
        self.parent = {}
        self.steps = 0

    def make(self, x):
        self.parent[x] = x

    def find(self, x):
        while x != self.parent[x]:
            x = self.parent[x]
            self.steps += 1
        return x

    def union(self, x, y):
        xb, yb = self.find(x), self.find(y)
        self.parent[yb] = xb


def depth(parent, x):
    d = 0
    while parent[x] != x:
        x = parent[x]
        d += 1
    return d


for n in (2, 5, 10, 50, 200):
    P = Plain()
    for i in range(1, n + 1):
        P.make(i)
    P.steps = 0
    for i in range(2, n + 1):
        P.union(i, 1)
    path_ok = all(P.parent[i] == i + 1 for i in range(1, n)) and P.parent[n] == n
    check(f"11.1 Union(2,1), ..., Union({n},1) builds the path 1->2->...->{n}", path_ok)
    check(f"11.1 that sequence costs (n-1)(n-2)/2 = {(n - 1) * (n - 2) // 2} Find steps (Theta(n^2)), n={n}",
          P.steps == (n - 1) * (n - 2) // 2, f"{P.steps}")
    s0 = P.steps
    P.find(1)
    check(f"11.1 then Find(1) walks n-1 = {n - 1} edges", P.steps - s0 == n - 1)


# union by depth, exactly as printed
class ByDepth:
    def __init__(self):
        self.parent, self.depth = {}, {}

    def make(self, x):
        self.parent[x] = x
        self.depth[x] = 0

    def find(self, x):
        while x != self.parent[x]:
            x = self.parent[x]
        return x

    def union(self, x, y):
        xb, yb = self.find(x), self.find(y)
        if self.depth[xb] > self.depth[yb]:
            self.parent[yb] = xb
        else:
            self.parent[xb] = yb
            if self.depth[xb] == self.depth[yb]:
                self.depth[yb] += 1


def members(parent):
    roots = {}
    for v in parent:
        r = v
        while parent[r] != r:
            r = parent[r]
        roots.setdefault(r, []).append(v)
    return roots


ok_height = ok_size = ok_lg = True
for trial in range(300):
    n = random.randint(2, 70)
    B = ByDepth()
    for i in range(n):
        B.make(i)
    for _ in range(3 * n):
        a, b = random.randrange(n), random.randrange(n)
        if B.find(a) != B.find(b):
            B.union(a, b)
        groups = members(B.parent)
        for r, mem in groups.items():
            h = max(depth(B.parent, v) for v in mem)
            ok_height &= (B.depth[r] == h)
            ok_size &= (len(mem) >= 2 ** B.depth[r])
            ok_lg &= (h <= flg(n))
check("11.1 union by depth: the depth field of every leader equals the height of its tree", ok_height)
check("11.1 union by depth: size of every set >= 2^depth(leader)", ok_size)
check("11.1 union by depth: every Find walks at most floor(lg n) edges", ok_lg)

# balanced rounds reach depth k on 2^k elements: Theta(log n) is attained
for k in range(1, 11):
    B = ByDepth()
    n = 2 ** k
    for i in range(n):
        B.make(i)
    w = 1
    while w < n:
        for i in range(0, n, 2 * w):
            B.union(i, i + w)
        w *= 2
    h = max(depth(B.parent, v) for v in range(n))
    check(f"11.1 balanced rounds on 2^{k} elements give depth exactly {k} = lg n", h == k)

# Union of two elements of the same set: the printed code bumps the depth (motivates the guard)
B = ByDepth()
B.make("x")
B.union("x", "x")
check("11.1 printed Union(x, x) on a singleton sets depth(x) = 1 > lg 1 (needs an 'if xbar = ybar return' guard)",
      B.depth["x"] == 1 and 1 > 2 ** B.depth["x"] - 2)


# =====================================================================================================
# 11.2 threaded trees
class Threaded:
    def __init__(self, null_terminated=True, cap=10 ** 5):
        self.leader, self.next = {}, {}
        self.nt = null_terminated
        self.relabels = 0
        self.cap = cap

    def make(self, x):
        self.leader[x] = x
        self.next[x] = None if self.nt else x  # the note prints next(x) <- x

    def find(self, x):
        return self.leader[x]

    def union(self, x, y):
        xb, yb = self.find(x), self.find(y)
        y = yb
        self.leader[y] = xb
        self.relabels += 1
        steps = 0
        while self.next[y] is not None:
            y = self.next[y]
            self.leader[y] = xb
            self.relabels += 1
            steps += 1
            if steps > self.cap:
                raise RuntimeError("loop")
        self.next[y] = self.next[xb]
        self.next[xb] = yb


T = Threaded(null_terminated=False, cap=1000)
T.make(1)
T.make(2)
try:
    T.union(1, 2)
    loops = False
except RuntimeError:
    loops = True
check("11.2 as printed (MakeSet sets next(x) <- x, Union loops while next(y) != Null) Union never terminates", loops)


def thread_ok(T):
    groups = {}
    for v, l in T.leader.items():
        groups.setdefault(l, set()).add(v)
    for l, mem in groups.items():
        if T.leader[l] != l:
            return False
        seen, v = [], l
        while v is not None:
            seen.append(v)
            v = T.next[v]
            if len(seen) > len(T.leader):
                return False
        if set(seen) != mem or len(seen) != len(mem):
            return False
    return True


ok = True
for trial in range(300):
    n = random.randint(1, 40)
    T = Threaded()
    for i in range(n):
        T.make(i)
    for _ in range(2 * n):
        a, b = random.randrange(n), random.randrange(n)
        if T.find(a) != T.find(b):
            sz = sum(1 for v in T.leader if T.leader[v] == T.find(b))
            r0 = T.relabels
            T.union(a, b)
            ok &= (T.relabels - r0 == sz)
        ok &= thread_ok(T)
check("11.2 Null-terminated threads: Union(x, y) relabels exactly the set of y; threads list each set from its leader", ok)

for n in (2, 3, 10, 100, 300):
    T = Threaded()
    T.make(1)
    for i in range(2, n + 1):
        T.make(i)
        T.union(1, i)
    a = T.relabels
    T = Threaded()
    T.make(1)
    for i in range(2, n + 1):
        T.make(i)
        T.union(i, 1)
    b = T.relabels
    check(f"11.2 WorstCaseSequence as printed (Union(1, i)) does only n-1 = {n - 1} relabels, n={n}", a == n - 1)
    check(f"11.2 with Union(i, 1) it does n(n-1)/2 = {n * (n - 1) // 2} relabels (Theta(n^2)), n={n}",
          b == n * (n - 1) // 2)


class Weighted(Threaded):
    def make(self, x):
        super().make(x)
        if not hasattr(self, "size"):
            self.size = {}
        self.size[x] = 1

    def wunion(self, x, y):
        xb, yb = self.find(x), self.find(y)
        if self.size[xb] > self.size[yb]:
            self.union(xb, yb)
            self.size[xb] += self.size[yb]
        else:
            self.union(yb, xb)
            self.size[yb] = self.size[xb] + self.size[yb]


ok_per, ok_lg, ok_two = True, True, True
for trial in range(400):
    m = random.randint(2, 120)
    W = Weighted()
    for i in range(m):
        W.make(i)
    changes = {i: 0 for i in range(m)}
    nu = 0
    for _ in range(random.randint(1, m - 1)):
        a, b = random.randrange(m), random.randrange(m)
        if W.find(a) == W.find(b):
            continue
        before = dict(W.leader)
        W.wunion(a, b)
        nu += 1
        for v in range(m):
            if W.leader[v] != before[v]:
                changes[v] += 1
    final = {}
    for v in range(m):
        final.setdefault(W.leader[v], []).append(v)
    ok_per &= all(changes[v] <= flg(len(final[W.leader[v]])) for v in range(m))
    ok_lg &= max(changes.values()) <= flg(nu + 1)
    ok_two &= sum(1 for v in range(m) if changes[v] > 0) <= nu and sum(
        len(s) for s in final.values() if len(s) > 1) <= 2 * nu
check("11.2 WeightedUnion: every object changes leader at most floor(lg(size of its final set)) times", ok_per)
check("11.2 WeightedUnion: after n unions no object changed leader more than floor(lg(n+1)) times", ok_lg)
check("11.2 WeightedUnion: at most 2n objects are in non-singleton sets after n unions", ok_two)
# the note's two sub-claims fail
W = Weighted()
W.make(1)
W.make(2)
W.wunion(1, 2)
check("11.2 counterexample to 'the largest set has at most n members' (n = 1 union makes a set of 2 = n + 1)",
      W.size[W.find(1)] == 2)
W = Weighted()
for i in range(10):
    W.make(i)
for i in range(0, 10, 2):
    W.wunion(i, i + 1)
check("11.2 counterexample to 'at most n objects are not in singletons' (5 unions of pairs: 10 = 2n objects)",
      sum(1 for v in range(10) if W.size[W.find(v)] > 1) == 10)

# worst case of n WeightedUnions building one set: DP over merge trees, cost of a merge = min(a, b) relabels
f = {1: 0}
for s in range(2, 257):
    f[s] = max(f[a] + f[s - a] + min(a, s - a) for a in range(1, s))
check("11.2 most relabels to build a set of s objects is <= (s/2) lg s, s <= 256",
      all(f[s] <= s / 2 * math.log2(s) + 1e-9 for s in f))
check("11.2 ... with equality k 2^(k-1) exactly when s = 2^k (balanced rounds)",
      all((abs(f[s] - s / 2 * math.log2(s)) < 1e-9) == (s & (s - 1) == 0) for s in f))
for k in range(1, 9):
    W = Weighted()
    n = 2 ** k
    for i in range(n):
        W.make(i)
    w = 1
    while w < n:
        for i in range(0, n, 2 * w):
            W.wunion(i, i + w)
        w *= 2
    check(f"11.2 balanced rounds on 2^{k} objects: {k * 2 ** (k - 1)} relabels by {n - 1} WeightedUnions",
          W.relabels - (n - 1) == k * 2 ** (k - 1) - (n - 1) and W.relabels == k * 2 ** (k - 1))


# =====================================================================================================
# 11.3 union by rank + recursive path compression, instrumented
class RankPC:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n
        self.n = n
        self.finds = 0          # m: number of Find calls (also those inside Union)
        self.assign = 0         # parent assignments made by the recursive Find
        self.changes = 0        # assignments that actually change a pointer (= Compress(x, y) with y below the root)
        self.pathlen = 0
        self.bad_parent_rank = False
        self.log = []           # events for the reordering check

    def find(self, x, top=True):
        if top:
            self.finds += 1
            d = 0
            v = x
            while self.parent[v] != v:
                v = self.parent[v]
                d += 1
            self.pathlen += d
            root = v
            # y for the figure convention: the child of the root on x's path (or x itself if depth <= 1)
            y = x
            while self.parent[y] != root and self.parent[y] != y:
                y = self.parent[y]
            self.log.append(("F", x, y if d >= 1 else x, root))
        if x != self.parent[x]:
            old = self.parent[x]
            new = self.find(old, top=False)
            if new != old:
                self.changes += 1
                if self.rank[new] <= self.rank[old]:
                    self.bad_parent_rank = True
            self.parent[x] = new
            self.assign += 1
        return self.parent[x]

    def union(self, x, y):
        xb, yb = self.find(x), self.find(y)
        if xb == yb:
            return False
        if self.rank[xb] > self.rank[yb]:
            self.parent[yb] = xb
            self.log.append(("L", yb, xb, None))
        else:
            self.parent[xb] = yb
            inc = self.rank[xb] == self.rank[yb]
            if inc:
                self.rank[yb] += 1
            self.log.append(("L", xb, yb, yb if inc else None))
        return True


def rank_invariants(U):
    n = U.n
    ok1 = all(U.rank[v] < U.rank[U.parent[v]] for v in range(n) if U.parent[v] != v)
    roots = {}
    for v in range(n):
        r = v
        while U.parent[r] != r:
            r = U.parent[r]
        roots.setdefault(r, []).append(v)
    ok2 = all(len(mem) >= 2 ** U.rank[r] for r, mem in roots.items())
    ok3 = max(U.rank) <= flg(n)
    cnt = {}
    for v in range(n):
        cnt[U.rank[v]] = cnt.get(U.rank[v], 0) + 1
    ok4 = all(c <= n / 2 ** r for r, c in cnt.items())
    ok5 = all(depth(U.parent, v) <= flg(n) for v in range(n))
    # rank(x) >= height of the subtree of x
    height = [0] * n
    for v in sorted(range(n), key=lambda v: -depth(U.parent, v)):
        p = U.parent[v]
        if p != v:
            height[p] = max(height[p], height[v] + 1)
    ok6 = all(height[v] <= U.rank[v] for v in range(n))
    return ok1, ok2, ok3, ok4, ok5, ok6


inv = [True] * 6
leader_ok = True
parent_rank_ok = True
for trial in range(150):
    n = random.randint(2, 60)
    U = RankPC(n)
    for _ in range(4 * n):
        if random.random() < 0.5:
            a, b = random.randrange(n), random.randrange(n)
            ra, rb = U.find(a), U.find(b)
            if ra != rb:
                oldranks = (U.rank[ra], U.rank[rb])
                U.union(a, b)
                newroot = U.find(a)
                loser = rb if newroot == ra else ra
                leader_ok &= U.rank[newroot] > U.rank[loser]
        else:
            U.find(random.randrange(n))
        res = rank_invariants(U)
        inv = [i and r for i, r in zip(inv, res)]
    parent_rank_ok &= not U.bad_parent_rank
check("11.3 rank(x) < rank(parent(x)) for every non-leader x (after every operation)", inv[0])
check("11.3 whenever path compression changes parent(x), the new parent has larger rank than the old one",
      parent_rank_ok)
check("11.3 whenever x's leader changes, the new leader has larger rank than the old one", leader_ok)
check("11.3 size of every set >= 2^rank(leader)", inv[1])
check("11.3 every rank <= floor(lg n)", inv[2])
check("11.3 at most n/2^r objects of rank r, for every r", inv[3])
check("11.3 depth <= floor(lg n) at all times: Find is O(log n) worst case even with path compression", inv[4])
check("11.3 rank(x) >= height of the subtree of x, for every node x at all times", inv[5])


# --------------------------------------------------------------------------------- iterated logarithms, alpha
def lgc(c, r):
    """lg^{*c} r as defined in the note (c = 0: lg r)."""
    if c == 0:
        return math.log2(r)
    if r <= 2:
        return 1
    return 1 + lgc(c, lgc(c - 1, r))


def lgstar(r):
    return lgc(1, r)


def alpha(r):
    c = 1
    while lgc(c, r) > 3:
        c += 1
    return c


INF = float("inf")


def up(c, n, cap=10 ** 6):
    """2 ↑^c n exactly, or INF when it has more than `cap` bits (iterative in n)."""
    if n == 1:
        return 2
    if c == 0:
        return 2 * n
    v = 2
    for _ in range(2, n + 1):
        if c == 1:
            v = 2 * v
        elif c == 2:
            v = 2 ** v if v <= cap else INF
        else:
            v = up(c - 1, v, cap) if v != INF and v <= 10 ** 7 else INF
        if v == INF:
            return INF
    return v


def ceil_lg(r):
    return (r - 1).bit_length()  # ceil(lg r) for integers r >= 1


def lgstar_exact(r):
    """lg* of a (big) integer without floating point: lg* only steps at integers, so lg*(r) = 1 + lg*(ceil lg r)."""
    return 1 if r <= 2 else 1 + lgstar_exact(ceil_lg(r))


# values used on the page
check("lg* values: lg* n = 1, 2, 3, 4, 5 on n <= 2, 3..4, 5..16, 17..65536, 65537..2^65536",
      [lgstar(x) for x in (1, 2, 3, 4, 5, 16, 17, 65536, 65537, 2 ** 65536)] == [1, 1, 2, 2, 3, 3, 4, 4, 5, 5])
check("exact integer lg* agrees with the definition for n < 2*10^5", all(lgstar_exact(x) == lgstar(x) for x in range(1, 200001)))
check("lg* 2^65536 = 5 and lg* (2^65536 + 1) = 6 (exact)", lgstar_exact(2 ** 65536) == 5 and lgstar_exact(2 ** 65536 + 1) == 6)
cnt_ok = True
for x in list(range(2, 5000)) + [2 ** 20, 2 ** 64 + 7, 10 ** 30]:
    v, k = x, 0
    while v > 1:
        v = math.log2(v)
        k += 1
    cnt_ok &= (k == lgstar(x))
check("lg* n = number of lg's until the value is <= 1 (not '< 1': for n = 2 that count is 2, the formula 1), n >= 2",
      cnt_ok)
v, k = 2, 0
while v >= 1:
    v = math.log2(v) if v > 0 else -1
    k += 1
check("... the note's words ('until less than 1') give 2 for n = 2, the formula gives 1", k == 2 and lgstar(2) == 1)
check("lg** values: 1 (n <= 2), 2 (3..4), 3 (5..65536), 4 above", [lgc(2, x) for x in (2, 3, 4, 5, 65536, 65537)]
      == [1, 2, 2, 3, 3, 4])
check("for n <= 2^256: lg* n <= 5, lg** n <= 4, lg^{*c} n <= 3 for c >= 3 (at n = 2^256, functions monotone)",
      lgstar(2 ** 256) == 5 and lgc(2, 2 ** 256) == 4 and all(lgc(c, 2 ** 256) == 3 for c in range(3, 8)))
mono = all(lgc(c, x) <= lgc(c, x + 1) for c in range(1, 5) for x in range(1, 3000))
check("lg^{*c} is non-decreasing (c = 1..4, n < 3000)", mono)
check("lg^{*c} 5 = 3 for every c = 1..8: the threshold 2 would never be reached (the note says '>= 2')",
      all(lgc(c, 5) == 3 for c in range(1, 9)))
check("lg^{*c} n >= 2 for every n > 2, c >= 1", all(lgc(c, x) >= 2 for c in range(1, 5) for x in range(3, 2000)))

# inverse of the Ackermann rows
inv_ok = True
for c in range(1, 5):
    vals = [up(c + 1, k) for k in range(1, 6)]
    for x in list(range(1, 70000)) + [2 ** 100, 2 ** 65536]:
        want = next(k for k in range(1, 6) if vals[k - 1] >= x)
        if lgc(c, x) != want:
            inv_ok = False
check("lg^{*c} n = min{k >= 1 : 2 ↑^{c+1} k >= n} (c = 1..4, n < 70000 and n = 2^100, 2^65536)", inv_ok)
check("alpha(n) = 1 for n <= 16, 2 for 17..65536, 3 at 65537 and at 2^65536",
      [alpha(x) for x in (1, 16, 17, 65536, 65537, 2 ** 65536)] == [1, 1, 2, 2, 3, 3])
a_ok = all(alpha(x) == min(c for c in range(1, 6) if up(c + 1, 3) >= x) for x in range(1, 70000))
check("alpha(n) = min{c >= 1 : 2 ↑^{c+1} 3 >= n} (n < 70000)", a_ok)
check("... not 2 ↑^{c+2} 3 as printed: that would give alpha(17) = 1, but lg* 17 = 4 > 3 so alpha(17) = 2",
      up(3, 3) == 65536 and alpha(17) == 2 and lgstar(17) == 4)


def alpha_t(r):  # footnote 5's version: min{c >= 1 : lg^{*c} r <= c}
    c = 1
    while lgc(c, r) > c:
        c += 1
    return c


check("footnote 5: alpha~(n) <= alpha(n) <= alpha~(n) + 2 for n > 65536 (computable range n < 70000, n = 2^100); "
      "alpha~(16) = 3 > alpha(16) = 1, so 'large n' is needed",
      all(alpha_t(x) <= alpha(x) <= alpha_t(x) + 2 for x in list(range(65537, 70000)) + [2 ** 100])
      and alpha_t(16) == 3 and alpha(16) == 1)
check("footnote 5 via the inverse relation: alpha~(n) <= c iff n <= 2↑^{c+1} c, for c = 1..3 and n < 70000",
      all((alpha_t(x) <= c) == (x <= up(c + 1, c)) for c in (1, 2, 3) for x in range(1, 70000)))


def alpha_mn(m, n, cmax=40):
    """The note's alpha(m, n) = min{c >= 1 : lg^{*c}(lg n) <= m/n}; None when no c qualifies."""
    for c in range(1, cmax):
        if lgc(c, math.log2(n)) <= m / n:
            return c
    return None


# reviewer (R34): the printed alpha(m, n) is an empty minimum for m < 3n once n >= 17
check("alpha(m, n) as printed: for n = 17..3000, lg^{*c}(lg n) >= 3 for c = 1..7, so no c qualifies at m = 3n - 1; "
      "m = 3n works", all(lgc(c, math.log2(n)) >= 3 for c in range(1, 8) for n in range(17, 3001))
      and all(alpha_mn(3 * n - 1, n) is None and alpha_mn(3 * n, n) is not None for n in range(17, 3001)))
check("... so it is undefined for m = n (every n = 5..3000): 'alpha(m,n) = Theta(alpha(n)) when m = Theta(n)' needs "
      "m >= 3n; at m = 3n it equals alpha(lg n) <= alpha(n) (n = 17..70000)",
      all(alpha_mn(n, n) is None for n in range(5, 3001))
      and all(alpha_mn(3 * n, n) == alpha(math.log2(n)) <= alpha(n) for n in range(17, 70000)))

# Ackermann table
table = {0: [2, 4, 6, 8, 10], 1: [2, 4, 8, 16, 32], 2: [2, 4, 16, 65536, 2 ** 65536], 3: [2, 4, 65536]}
t_ok = all(up(c, n + 1) == v for c, row in table.items() for n, v in enumerate(row))
check("Ackermann table: rows 2n, 2↑n, 2↑↑n (to n = 5) and 2↑↑↑n (to n = 3) as printed", t_ok)
check("2 ↑^c 2 = 4 for every c = 0..8", all(up(c, 2) == 4 for c in range(9)))
check("2 ↑^c 1 = 2 for every c", all(up(c, 1) == 2 for c in range(9)))
check("2↑↑↑4 = 2↑↑65536 and 2↑↑↑↑3 = 2↑↑↑4 (identity 2↑^{c+1}3 = 2↑^c 4) — both towers, not computed",
      up(3, 4) == INF and up(2, 4) == 65536 and all(up(c + 1, 3) == up(c, 4) for c in range(0, 3)))
check("2↑↑n is a tower of n 2s", all(up(2, n) == (lambda n: (lambda f: f(f, n))(lambda f, n: 2 if n == 1 else 2 ** f(f, n - 1)))(n) for n in range(1, 5)))
check("each row 2↑^c n increases in n (computable entries)", all(
    up(c, n) < up(c, n + 1) for c in range(0, 3) for n in range(1, 4)))


# --------------------------------------------------------------------------------- recurrences of 11.4 / 11.5
check("11.4 s = floor(lg r) does not give r/2^s <= 1 (r = 3: 1.5), so 'T(F+, C+) <= n' needs s = ceil(lg r)",
      3 / 2 ** flg(3) == 1.5 and all(r / 2 ** ceil_lg(r) <= 1 for r in range(1, 10 ** 5)))
check("lg*(ceil(lg r)) = lg* r - 1 for 3 <= r <= 2*10^5 (lg* only steps at the integers 2, 4, 16, 65536)",
      all(lgstar(ceil_lg(r)) == lgstar(r) - 1 for r in range(3, 200001)))


def U1(r):  # T'(m,n,r)/n with T' = T - m: base T <= n r <= 2n for r <= 2
    return min(r, 2) if r <= 2 else U1(ceil_lg(r)) + 2


check("recurrence T'(r) <= T'(ceil lg r) + 2n solves to <= 2n lg* r (r <= 2*10^5)",
      all(U1(r) <= 2 * lgstar(r) for r in range(1, 200001)))


def U2(r):  # T''/n with T'' = T - 2m
    return min(r, 2) if r <= 2 else U2(lgstar(r)) + 3


check("recurrence T''(r) <= T''(lg* r) + 3n solves to <= 3n lg** r (r <= 2*10^5)",
      all(U2(r) <= 3 * lgc(2, r) for r in range(1, 200001)))
check("lg* r / 2^{lg* r} <= 1/2, so Theorem 3 on F+ with s = lg* r costs <= m+ + n (the note bounds it by m+ + 2n)",
      all(lgstar(r) / 2 ** lgstar(r) <= 0.5 for r in range(1, 10 ** 5)))


def Uc(c, r):  # T_c/n where T_c = T - c m
    if r <= 2:
        return min(r, 2)
    s = ceil_lg(r) if c == 1 else lgc(c - 1, r)
    return Uc(c, s) + (c + 1)


check("general crank: T - cm <= (c+1) n lg^{*c} r (c = 1..4, r <= 10^5)",
      all(Uc(c, r) <= (c + 1) * lgc(c, r) for c in range(1, 5) for r in range(1, 100001)))


# --------------------------------------------------------------------------------- simulations of Theorems 2-4
def bounds(m, n, r):
    if r == 0:
        return {}
    a = alpha(r)
    return {"Thm2 n r": n * r, "Thm3 m+2n lg* r": m + 2 * n * lgstar(r), "2m+3n lg** r": 2 * m + 3 * n * lgc(2, r),
            "Thm4 m alpha(r)+3n(alpha(r)+1)": m * a + 3 * n * (a + 1)}


worst = {}


def record(U, label):
    r = max(U.rank)
    for k, b in bounds(U.finds, U.n, r).items():
        ratio = U.changes / b
        worst[k] = max(worst.get(k, (0, ""))[0], ratio), label if ratio >= worst.get(k, (0, ""))[0] else worst[k][1]
        if U.changes > b:
            check(f"bound {k} on {label}", False, f"T={U.changes} > {b}")
    if U.bad_parent_rank:
        check(f"new parent has larger rank on {label}", False)


# W1: random
for n in (2 ** 10, 2 ** 14):
    U = RankPC(n)
    for _ in range(12 * n):
        if random.random() < 0.4:
            U.union(random.randrange(n), random.randrange(n))
        else:
            U.find(random.randrange(n))
    record(U, f"random n={n}")


# W2: binomial trees (balanced rounds, no finds in between), then Finds on all nodes deepest first
def binomial(k):
    n = 2 ** k
    U = RankPC(n)
    w = 1
    while w < n:
        for i in range(0, n, 2 * w):
            U.union(i + w, i)  # both arguments are roots here
        w *= 2
    return U


for k in (10, 14):
    U = binomial(k)
    order = sorted(range(2 ** k), key=lambda v: -depth(U.parent, v))
    for v in order:
        U.find(v)
    record(U, f"binomial 2^{k}, finds deepest first")

# W3: repeatedly merge equal-rank trees and compress the deepest leaf of each before the union
for k in (10, 13):
    n = 2 ** k
    U = RankPC(n)
    w = 1
    while w < n:
        for i in range(0, n, 2 * w):
            for blk in (i, i + w):
                deepest = max(range(blk, blk + w), key=lambda v: depth(U.parent, v))
                U.find(deepest)
            U.union(i + w, i)
        w *= 2
    for v in sorted(range(n), key=lambda v: -depth(U.parent, v)):
        U.find(v)
    record(U, f"merge-and-compress 2^{k}")

# W4: many seeds of small random runs
for t in range(300):
    n = random.randint(2, 300)
    U = RankPC(n)
    for _ in range(random.randint(n, 8 * n)):
        if random.random() < 0.5:
            U.union(random.randrange(n), random.randrange(n))
        else:
            U.find(random.randrange(n))
    record(U, f"small random #{t}")
for k, (v, lab) in sorted(worst.items()):
    check(f"simulations: pointer changes T <= {k} on every run (largest ratio {v:.3f}, on {lab})", v <= 1)


# --------------------------------------------------------------------------------- reordering Unions before Compresses
def replay(n, log, convention):
    parent = list(range(n))
    rank = [0] * n
    for ev in log:
        if ev[0] == "L":
            parent[ev[1]] = ev[2]
            if ev[3] is not None:
                rank[ev[3]] += 1
    cost = 0
    valid = True

    def compress(x, y):
        nonlocal cost
        if x != y:
            compress(parent[x], y)
            parent[x] = parent[y]
            cost += 1

    for ev in log:
        if ev[0] == "F":
            x, yfig, root = ev[1], ev[2], ev[3]
            y = yfig if convention == "figure" else root
            # y must be an ancestor of x
            v = x
            while v != y and parent[v] != v:
                v = parent[v]
            if v != y:
                valid = False
                continue
            compress(x, y)
    return cost, parent, valid


eq_fig, mism_text = True, 0
for t in range(400):
    n = random.randint(2, 40)
    U = RankPC(n)
    for _ in range(4 * n):
        if random.random() < 0.5:
            U.union(random.randrange(n), random.randrange(n))
        else:
            U.find(random.randrange(n))
    cost, par, valid = replay(n, U.log, "figure")
    eq_fig &= valid and cost == U.changes and par == U.parent
    cost2, _, valid2 = replay(n, U.log, "text")
    if (not valid2) or cost2 != U.assign:
        mism_text += 1
check("11.4 Unions moved before all Compresses: same number of pointer assignments and the same final forest, when "
      "Find(x) is Compress(x, y) with y the child of the root (as in the note's figure)", eq_fig)
check(f"11.4 ... but not with y = the leader (the note's text): counts differ in {mism_text} of 400 random runs",
      mism_text > 0)
# the 4-node example of the page
U = RankPC(4)  # x=0, a=1, b=2, c=3
U.union(0, 1)  # parent(x) <- a, rank(a) = 1
U.union(3, 2)  # parent(c) <- b, rank(b) = 1
U.log = [e for e in U.log if e[0] == "L"]
U.find(0)
U.union(1, 2)  # a under b
U.log = [e for e in U.log if not (e[0] == "F" and e[1] in (1, 2))]  # keep only the two Find(x) events
U.find(0)
U.log = [e for e in U.log if not (e[0] == "F" and e[1] != 0)]
text_orig = 1 + 2      # Compress(x, a) then Compress(x, b) in the original order, leader convention
c_text, _, _ = replay(4, U.log, "text")
c_fig, _, _ = replay(4, U.log, "figure")
check("11.4 example: x->a, c->b; Find(x); Union(a, b); Find(x): leader convention 3 assignments in order, "
      "2 after reordering; child-of-root convention 1 and 1",
      c_text == 2 and text_orig == 3 and c_fig == 1 and U.changes == 1)


# --------------------------------------------------------------------------------- the split at rank s
def split_check(trials=150):
    ok_real = ok_shatter = ok_red = ok_sum = ok_npl = ok_thm2p = True
    for t in range(trials):
        n = random.randint(16, 400)
        U = RankPC(n)
        for _ in range(5 * n):
            if random.random() < 0.55:
                U.union(random.randrange(n), random.randrange(n))
            else:
                U.find(random.randrange(n))
        # final forest after all links; compress sequence = the recorded Finds (figure convention)
        parent = list(range(n))
        rank = [0] * n
        for ev in U.log:
            if ev[0] == "L":
                parent[ev[1]] = ev[2]
                if ev[3] is not None:
                    rank[ev[3]] += 1
        comps = [(ev[1], ev[2]) for ev in U.log if ev[0] == "F" and ev[1] != ev[2]]
        r = max(rank)
        for s in range(1, max(r, 1)):
            P = parent[:]
            hi = [rank[v] > s for v in range(n)]
            tot = plus = lowlow = shatter = red = 0
            shattered = set()
            m_plus = 0
            for (x, y) in comps:
                path = []
                v = x
                while v != y:
                    path.append(v)
                    v = P[v]
                newp = P[y]
                involves_high = hi[y] or hi[newp]
                m_plus += 1 if (hi[y]) else 0
                reds_here = 0
                for v in path:
                    old = P[v]
                    if old == newp:
                        ok_real = False
                    tot += 1
                    if hi[v]:
                        plus += 1
                    elif not hi[newp]:
                        lowlow += 1
                    elif not hi[old]:
                        shatter += 1
                        if v in shattered:
                            ok_shatter = False
                        shattered.add(v)
                    else:
                        red += 1
                        reds_here += 1
                    P[v] = newp
                if reds_here > 1 or (reds_here == 1 and not hi[y]):
                    ok_red = False
            n_minus = sum(1 for v in range(n) if not hi[v])
            n_plus = n - n_minus
            ok_shatter &= shatter <= n_minus
            ok_red &= red <= m_plus
            ok_sum &= tot == plus + lowlow + shatter + red and tot <= plus + lowlow + m_plus + n
            ok_npl &= n_plus <= n / 2 ** s
            ok_thm2p &= plus <= n_plus * (r - s)
    check("11.4 split: every Compress assignment changes a pointer (y is never a root)", ok_real)
    check("11.4 split: low nodes whose parent jumps from low to high (the Shatters) — each at most once, <= n-",
          ok_shatter)
    check("11.4 split: low nodes moved from one high parent to another (the (!?) line) — at most one per Compress "
          "whose top node is high, <= m+", ok_red)
    check("11.4 split: T(F,C) = T(F+,C+) + T(F-,C-) + shatters + (!?) <= T(F+,C+) + T(F-,C-) + m+ + n", ok_sum)
    check("11.4 split: n+ <= n/2^s", ok_npl)
    check("11.4 split: T(F+,C+) <= n+ (r - s) (Theorem 2 inside F+)", ok_thm2p)


split_check()

# --------------------------------------------------------------------------------- page text
if os.path.exists(PAGE):
    page = open(PAGE, encoding="utf-8").read()
    for frag in ["2^{65536}", "65536", r"\lfloor\lg(n+1)\rfloor", "$2n$", r"\lceil\lg r\rceil", "(n-1)(n-2)/2",
                 "n(n-1)/2", r"k\,2^{k-1}", r"\alpha(17) = 2", r"2\uparrow^{c+1} 3", r"m + 2n\lg^* r",
                 r"m\,\alpha(r) + 3n(\alpha(r) + 1)", r"2m + 3n\lg^{**} r", "1 + 2", "1 + 1", "1.5n",
                 r"\lg^{*^c} 5 = 3", r"$m < 3n$ and $n\ge 17$", r"m\ge 3n"]:
        check(f"page mentions {frag}", frag in page)
else:
    print("(page not written yet)")

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: {FAIL}")
