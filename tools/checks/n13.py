#!/usr/bin/env python3
"""Checks for content/4-lecture-notes/13-adversary-arguments.md (Erickson, Director's Cut 13, Adversary Arguments)
and the concept page content/concepts/adversary-arguments.md.

Decision-tree complexities are computed by exhaustive minimax search: for bit-probing problems (any-ones, the
pattern 01, graph properties given by adjacency matrices) the state is the set of inputs consistent with the bits
seen so far; for comparison problems (min-and-max, median, k-th largest, is-it-sorted) the state is the set of
permutations consistent with the answers so far. The adversaries of the page are played against every probe or
comparison sequence that is too short (all of them for small n, random ones for larger n), and the min-and-max
algorithm is run on every permutation."""
import itertools
import math
import os
import random

import networkx as nx

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
PAGE = os.path.join(ROOT, "content", "4-lecture-notes", "13-adversary-arguments.md")
CONCEPT = os.path.join(ROOT, "content", "concepts", "adversary-arguments.md")
FAIL = []
random.seed(13)


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAIL.append(name)


def clg(x):
    return (x - 1).bit_length()


# =====================================================================================================
# bit-probing games
class ProbeGame:
    """f: {0,1}^n -> bool given as a function of an int (bit i = x_{i+1}). States: bitmask over the 2^n inputs."""

    def __init__(self, n, f):
        self.n = n
        N = 1 << n
        self.full = (1 << N) - 1
        self.true = 0
        for x in range(N):
            if f(x):
                self.true |= 1 << x
        self.one = []
        for i in range(n):
            m = 0
            for x in range(N):
                if (x >> i) & 1:
                    m |= 1 << x
            self.one.append(m)
        self.memo = {}

    def terminal(self, S):
        return (S & self.true) == S or (S & self.true) == 0

    def value(self, S=None):
        if S is None:
            S = self.full
        if S in self.memo:
            return self.memo[S]
        if self.terminal(S):
            self.memo[S] = 0
            return 0
        best = math.inf
        for i in range(self.n):
            a, b = S & self.one[i], S & ~self.one[i]
            if not a or not b:
                continue
            v = 1 + max(self.value(a), self.value(b))
            if v < best:
                best = v
                if best == 1:
                    break
        self.memo[S] = best
        return best

    def can(self, budget, S=None, memo=None):
        """Can the value be determined with at most `budget` more probes?"""
        if S is None:
            S, memo = self.full, {}
        if self.terminal(S):
            return True
        if budget == 0:
            return False
        key = (S, budget)
        if key in memo:
            return memo[key]
        res = False
        for i in range(self.n):
            a, b = S & self.one[i], S & ~self.one[i]
            if not a or not b:
                continue
            if self.can(budget - 1, a, memo) and self.can(budget - 1, b, memo):
                res = True
                break
        memo[key] = res
        return res


def bits(x, n):
    return "".join("1" if (x >> i) & 1 else "0" for i in range(n))  # position 1 first


def evasive(n, f):
    g = ProbeGame(n, f)
    if g.terminal(g.full):
        return False
    return not g.can(n - 1)


# 13.2 any ones
check("13.2 'any ones?' (OR of n bits) needs all n probes, n = 1..10",
      all(ProbeGame(n, lambda x: x != 0).value() == n for n in range(1, 11)))

# 13.3 the pattern 01
D01 = {n: ProbeGame(n, lambda x, n=n: "01" in bits(x, n)).value() for n in range(1, 11)}
check("13.3 pattern 01: worst-case probes = n for even n, n - 1 for odd n >= 3 (0 for n = 1), n = 1..10",
      all(D01[n] == (n if n % 2 == 0 else (n - 1 if n >= 3 else 0)) for n in D01), f"{D01}")


def odd_algorithm(B):
    """The page's algorithm for odd n: probe the even positions, then only the odd positions that matter."""
    n = len(B)
    probes = set()

    def look(i):
        probes.add(i)
        return B[i - 1]

    ev = {i: look(i) for i in range(2, n, 2)}
    seen0 = False
    for i in range(2, n, 2):
        if ev[i] == "0":
            seen0 = True
        elif seen0:
            return True, probes          # a 0 at an even position before a 1 at a later even position
    # even bits are 1...10...0: check the odd positions where a 01 could start or end
    for i in range(1, n + 1, 2):
        left = ev.get(i - 1)   # even neighbour on the left (None for i = 1)
        right = ev.get(i + 1)  # even neighbour on the right (None for i = n)
        # the bit at i matters only if it can complete a 01 with a neighbour
        if (left == "0") or (right == "1"):
            b = look(i)
            if (left == "0" and b == "1") or (right == "1" and b == "0"):
                return True, probes
    return False, probes


ok_c = ok_p = True
for n in range(1, 16, 2):
    for x in range(1 << n):
        B = bits(x, n)
        ans, pr = odd_algorithm(B)
        ok_c &= ans == ("01" in B)
        ok_p &= len(pr) <= max(n - 1, 0)
check("13.3 odd n: the even-positions-first algorithm is correct on all inputs, n = 1, 3, ..., 15", ok_c)
check("13.3 ... and never probes more than n - 1 bits", ok_p)

# reviewer (R34): when the even bits read 1..10..0, the skipped bit is the one between the last 1 and the first 0
ok_skip = True
for n in range(5, 16, 2):
    evens = list(range(2, n, 2))
    for a in range(1, len(evens)):  # a even 1s, then even 0s (both nonempty)
        skip = evens[a - 1] + 1     # between the last even 1 and the first even 0
        for x in range(1 << n):
            s = bits(x, n)
            if any(s[i - 1] != ("1" if k < a else "0") for k, i in enumerate(evens)):
                continue
            ans, pr = odd_algorithm(s)
            t = s[:skip - 1] + ("1" if s[skip - 1] == "0" else "0") + s[skip:]
            ok_skip &= skip not in pr and (("01" in s) == ("01" in t))
check("13.3 odd n, even bits 1..10..0: the bit between the last 1 and the first 0 is never probed and never matters "
      "(the note says 'between the last 0 and the first 1'), n = 5..15", ok_skip)


def hide01(n, version):
    """Return a function probe(i) and the state, as an object."""
    class A:
        def __init__(self):
            self.l, self.r, self.B = 0, n + 1, {}

        def probe(self, i):
            if i <= self.l:
                b = 1
            elif i >= self.r:
                b = 0
            elif ((i - self.l) % 2 == 0) == (version == "printed"):
                b = 0
                self.r = i
            else:
                b = 1
                self.l = i
            self.B[i] = b
            return b
    return A()


def completions_both(n, known):
    has, hasnt = False, False
    unk = [i for i in range(1, n + 1) if i not in known]
    for x in range(1 << len(unk)):
        s = dict(known)
        for k, i in enumerate(unk):
            s[i] = (x >> k) & 1
        st = "".join(str(s[i]) for i in range(1, n + 1))
        if "01" in st:
            has = True
        else:
            hasnt = True
        if has and hasnt:
            return True
    return False


def adversary_forces_all(n, version):
    """True if after every probe sequence of < n distinct positions both answers are still possible."""
    def dfs(seq, adv_state):
        if len(seq) == n:
            return True
        if not completions_both(n, adv_state.B):
            return False
        for i in range(1, n + 1):
            if i in adv_state.B:
                continue
            a2 = hide01(n, version)
            for j in seq + [i]:
                a2.probe(j)
            if not dfs(seq + [i], a2):
                return False
        return True
    return dfs([], hide01(n, version))


check("13.3 Hide01 with the parity test as on the page (i - l odd: answer 0, r <- i) forces all n probes, "
      "every probe order, even n = 2..8", all(adversary_forces_all(n, "fixed") for n in (2, 4, 6, 8)))
check("13.3 Hide01 as printed (i - l even: answer 0) fails already for n = 2: after probing B[1] = 1 the answer "
      "is known", not adversary_forces_all(2, "printed") and not adversary_forces_all(4, "printed"))
inv = True
for n in (2, 4, 6, 8, 10):
    for _ in range(300):
        a = hide01(n, "fixed")
        for i in random.sample(range(1, n + 1), n):
            a.probe(i)
            inv &= (a.r - a.l - 1) % 2 == 0
check("13.3 invariant kept by the corrected Hide01: r - l - 1 (the number of bits strictly between) stays even", inv)
a = hide01(4, "fixed")
check("13.3 initially l = 0, r = n + 1: r - l = n + 1 is odd for even n (the note says r - l is even)",
      (a.r - a.l) % 2 == 1)

# which patterns are evasive for every n >= |p| (n <= 10): only 0 and 1 among patterns of length <= 3
pat_ok = True
first_non = {}
for L in (1, 2, 3):
    for t in itertools.product("01", repeat=L):
        p = "".join(t)
        non = [n for n in range(L, 11) if not evasive(n, lambda x, n=n, p=p: p in bits(x, n))]
        first_non[p] = non[0] if non else None
        if L == 1:
            pat_ok &= not non
        else:
            pat_ok &= bool(non)
check("13.3 among patterns of length <= 3, only 0 and 1 are evasive for every n (checked |p| <= n <= 10)", pat_ok,
      f"first non-evasive n: {first_non}")
D11 = {n: ProbeGame(n, lambda x, n=n: "11" in bits(x, n)).value() for n in range(1, 11)}
print("     info: worst-case probes for pattern 11, n = 1..10:", D11)
D111 = {n: ProbeGame(n, lambda x, n=n: "111" in bits(x, n)).value() for n in range(1, 11)}
print("     info: worst-case probes for pattern 111, n = 1..10:", D111)
check("exercise 1(c) as printed ('11 is evasive iff n mod 3 = 1') is reversed: for n = 1..10, 11 is evasive "
      "exactly when n mod 3 != 1 (n = 4: 3 probes suffice)", all((D11[n] == n) == (n % 3 != 1) for n in range(1, 11))
      and D11[4] == 3)
check("exercise 1(d) ('111 is evasive iff n mod 4 = 0 or 3') agrees with the search for n = 1..10",
      all((D111[n] == n) == (n % 4 in (0, 3)) for n in range(1, 11)))


# =====================================================================================================
# 13.4-13.6 graph properties from the adjacency matrix
def edges_of(n):
    return list(itertools.combinations(range(n), 2))


def graph_of(n, x):
    E = edges_of(n)
    G = nx.Graph()
    G.add_nodes_from(range(n))
    G.add_edges_from(e for k, e in enumerate(E) if (x >> k) & 1)
    return G


def prop_table(n, P):
    return {x: P(graph_of(n, x)) for x in range(1 << len(edges_of(n)))}


for n in range(2, 6):
    E = len(edges_of(n))
    emp = prop_table(n, lambda G: G.number_of_edges() == 0)
    con = prop_table(n, nx.is_connected)
    check(f"13.4 emptiness is evasive for n = {n}: all {E} entries needed", evasive(E, lambda x: emp[x]))
    check(f"13.5 connectedness is evasive for n = {n}: all {E} entries needed", evasive(E, lambda x: con[x]))


class HideConn:
    def __init__(self, n):
        self.n = n
        self.M = set(edges_of(n))
        self.Y = set()

    def probe(self, e):
        M2 = self.M - {e}
        G = nx.Graph()
        G.add_nodes_from(range(self.n))
        G.add_edges_from(M2)
        if nx.is_connected(G):
            self.M = M2
            return 0
        self.Y.add(e)
        return 1


def gr(n, E):
    G = nx.Graph()
    G.add_nodes_from(range(n))
    G.add_edges_from(E)
    return G


def invariants(a):
    n = a.n
    GY, GM = gr(n, a.Y), gr(n, a.M)
    ok = a.Y <= a.M and nx.is_connected(GM) and nx.is_forest(GY)
    for c in nx.cycle_basis(GM):
        cyc = {tuple(sorted((c[i], c[(i + 1) % len(c)]))) for i in range(len(c))}
        ok &= not (cyc & a.Y)
    # every edge of M on some cycle of M is not in Y (stronger than the basis check)
    for e in a.Y:
        H = gr(n, a.M - {e})
        ok &= not nx.is_connected(H)  # Y edges are bridges of M
    if a.Y != a.M:
        ok &= not nx.is_connected(GY)
    return ok


ok_inv, ok_end, states = True, True, 0
for n in (3, 4):
    for order in itertools.permutations(edges_of(n)):
        a = HideConn(n)
        for k, e in enumerate(order):
            a.probe(e)
            ok_inv &= invariants(a)
            states += 1
            if k < len(order) - 1:
                ok_end &= a.Y != a.M  # the algorithm cannot know yet
        ok_end &= a.Y == a.M and nx.is_tree(gr(n, a.Y))
check(f"13.5 HideConnectedness, every probe order for n = 3, 4 ({states} states): Y ⊆ M, M connected, Y acyclic, "
      "edges of Y are bridges of M (no cycle of M uses them), Y ≠ M ⇒ Y disconnected", ok_inv)
check("13.5 ... before the last probe Y ≠ M (one consistent graph connected, one not); at the end Y = M is a tree",
      ok_end)
ok_inv = ok_end = ok_mst = True
for n in (5, 6, 7, 8):
    for _ in range(150 if n <= 6 else 60):
        order = edges_of(n)
        random.shuffle(order)
        a = HideConn(n)
        for k, e in enumerate(order):
            a.probe(e)
            if n <= 6:
                ok_inv &= invariants(a)
            if k < len(order) - 1:
                ok_end &= a.Y != a.M and nx.is_connected(gr(n, a.M)) and not nx.is_connected(gr(n, a.Y))
        K = nx.Graph()
        for t, e in enumerate(order):
            K.add_edge(*e, weight=t)
        T = {tuple(sorted(e)) for e in nx.maximum_spanning_tree(K).edges()}
        ok_mst &= a.Y == a.M == T
check("13.5 random probe orders, n = 5..8: invariants hold, Y ≠ M with M connected and Y disconnected until the "
      "last probe", ok_inv and ok_end)
check("13.5 at the end Y = M = the maximum spanning tree of K_n weighted by probe time", ok_mst)


# the figure's snapshot: K5, edges asked in lexicographic order 12, 13, 14, 15, 23, 24, 25
a = HideConn(5)
ans = [a.probe((u - 1, v - 1)) for u, v in ((1, 2), (1, 3), (1, 4), (1, 5), (2, 3), (2, 4), (2, 5))]
check("figure: K5, edges 12..25 in order: answers 0 0 0 1 0 0 1, Y = {15, 25}, M = Y + {34, 35, 45} connected, "
      "Y disconnected", ans == [0, 0, 0, 1, 0, 0, 1] and a.Y == {(0, 4), (1, 4)}
      and a.M == {(0, 4), (1, 4), (2, 3), (2, 4), (3, 4)} and nx.is_connected(gr(5, a.M))
      and not nx.is_connected(gr(5, a.Y)))
for e in ((2, 3), (2, 4), (3, 4)):
    a.probe(e)
check("figure: finishing the lexicographic order gives Y = M = the star at 5 (the maximum spanning tree)",
      a.Y == a.M == {(0, 4), (1, 4), (2, 4), (3, 4)})
h = hide01(10, "fixed")
ans = [h.probe(i) for i in (4, 9, 1, 10)]
check("figure: Hide01 on n = 10, probes 4, 9, 1, 10 answer 1, 0, 1, 0 and leave l = 4, r = 9 (4 bits between)",
      ans == [1, 0, 1, 0] and (h.l, h.r) == (4, 9) and completions_both(10, h.B))

# monotone properties (closed under deleting an edge)
def monotone(n, P):
    tab = prop_table(n, P)
    E = len(edges_of(n))
    return all(tab[x & ~(1 << k)] for x in tab if tab[x] for k in range(E) if (x >> k) & 1)


check("13.6 emptiness, acyclicity, non-connectedness and planarity are monotone (n = 5, all graphs)",
      monotone(5, lambda G: G.number_of_edges() == 0) and monotone(5, nx.is_forest)
      and monotone(5, lambda G: not nx.is_connected(G)) and monotone(5, lambda G: nx.check_planarity(G)[0]))
check("13.6 being a tree and having a vertex of degree 3 are not monotone (n = 5)",
      not monotone(5, nx.is_tree) and not monotone(5, lambda G: 3 in dict(G.degree()).values()))


# AKR for n <= 4: every nontrivial monotone graph property (isomorphism-invariant) is evasive
def akr(n):
    E = edges_of(n)
    perms = list(itertools.permutations(range(n)))
    idx = {e: k for k, e in enumerate(E)}

    def canon(x):
        best = None
        for p in perms:
            y = 0
            for k, (u, v) in enumerate(E):
                if (x >> k) & 1:
                    y |= 1 << idx[tuple(sorted((p[u], p[v])))]
            best = y if best is None or y < best else best
        return best
    cls = {}
    for x in range(1 << len(E)):
        cls.setdefault(canon(x), []).append(x)
    reps = list(cls)
    count, all_ev = 0, True
    for mask in range(1, (1 << len(reps)) - 1):
        P = set()
        for k, r in enumerate(reps):
            if (mask >> k) & 1:
                P |= set(cls[r])
        if not all(x & ~(1 << k) in P for x in P for k in range(len(E)) if (x >> k) & 1):
            continue
        count += 1
        all_ev &= evasive(len(E), lambda x: x in P)
    return count, all_ev


for n in (2, 3, 4):
    c, ev = akr(n)
    check(f"13.6 all {c} nontrivial monotone properties of {n}-vertex graphs are evasive (AKR holds, n = {n})", ev)


# =====================================================================================================
# comparison games
class CompGame:
    def __init__(self, n, answer):
        self.n = n
        self.perms = list(itertools.permutations(range(n)))
        self.full = (1 << len(self.perms)) - 1
        self.lt = {}
        for i in range(n):
            for j in range(i + 1, n):
                m = 0
                for k, p in enumerate(self.perms):
                    if p[i] < p[j]:
                        m |= 1 << k
                self.lt[(i, j)] = m
        self.classes = {}
        for k, p in enumerate(self.perms):
            self.classes[answer(p)] = self.classes.get(answer(p), 0) | (1 << k)
        self.cls = list(self.classes.values())
        self.memo = {}

    def value(self, S=None):
        if S is None:
            S = self.full
        if S in self.memo:
            return self.memo[S]
        k = sum(1 for c in self.cls if c & S)
        if k <= 1:
            self.memo[S] = 0
            return 0
        lb = clg(k)
        best = math.inf
        for (i, j), m in self.lt.items():
            a, b = S & m, S & ~m
            if not a or not b:
                continue
            v = 1 + max(self.value(a), self.value(b))
            if v < best:
                best = v
                if best <= lb:
                    break
        self.memo[S] = best
        return best


def minmax_target(n):
    return math.ceil(3 * n / 2) - 2


mm = {n: CompGame(n, lambda p: (p.index(0), p.index(len(p) - 1))).value() for n in range(1, 7)}
check("13.7 exhaustive search: min and max together need exactly ceil(3n/2) - 2 comparisons, n = 1..6",
      all(mm[n] == minmax_target(n) for n in mm), f"{mm}")


def min_and_max(x, cnt):
    n = len(x)
    S, L = [], []
    for i in range(0, n - 1, 2):
        cnt[0] += 1
        if x[i] < x[i + 1]:
            S.append(i)
            L.append(i + 1)
        else:
            S.append(i + 1)
            L.append(i)
    if n % 2:
        S.append(n - 1)
        L.append(n - 1)
    lo = S[0]
    for i in S[1:]:
        cnt[0] += 1
        if x[i] < x[lo]:
            lo = i
    hi = L[0]
    for i in L[1:]:
        cnt[0] += 1
        if x[i] > x[hi]:
            hi = i
    return lo, hi


ok = True
for n in range(1, 10):
    for p in itertools.permutations(range(n)):
        c = [0]
        lo, hi = min_and_max(p, c)
        ok &= (p[lo] == 0 and p[hi] == n - 1 and c[0] == minmax_target(n))
check("13.7 pair-then-scan algorithm: correct and exactly floor(n/2) + 2(ceil(n/2) - 1) = ceil(3n/2) - 2 "
      "comparisons on every permutation, n = 1..9", ok)
check("13.7 the arithmetic: floor(n/2) + 2(ceil(n/2) - 1) = ceil(3n/2) - 2 and 2n - 2 - floor(n/2) = ceil(3n/2) - 2",
      all(n // 2 + 2 * (math.ceil(n / 2) - 1) == minmax_target(n) == 2 * n - 2 - n // 2 for n in range(1, 1000)))
check("13.7 naive bound 2n - 3 (min in n - 1, then max of the rest in n - 2) equals ceil(3n/2) - 2 for n = 2, 3 "
      "and is larger for n >= 4", all(2 * n - 3 > minmax_target(n) for n in range(4, 1000))
      and all(2 * n - 3 == minmax_target(n) for n in (2, 3)))


class MarkAdversary:
    """States: N (both marks), W (+ only: never lost), L (- only: never won), O (no marks). Values are kept so that
    every answer is consistent: W elements are raised above everything, L elements lowered below everything."""

    def __init__(self, n):
        self.n = n
        self.st = ["N"] * n
        self.val = [None] * n
        self.hi, self.lo = 0, 0
        self.answers = []
        self.double = 0

    def raise_(self, i):
        self.hi += 1
        self.val[i] = self.hi

    def lower(self, i):
        self.lo -= 1
        self.val[i] = self.lo

    def compare(self, i, j):
        """Return True iff x_i > x_j."""
        si, sj = self.st[i], self.st[j]
        before = self.marks()
        if si == "N" and sj == "N":
            self.raise_(i); self.lower(j); self.st[i], self.st[j] = "W", "L"
            self.double += 1
        elif "N" in (si, sj):
            k, o = (i, j) if si == "N" else (j, i)
            so = self.st[o]
            if so == "W":
                self.raise_(o); self.lower(k); self.st[k] = "L"
            else:  # o is L or O: k wins
                if so == "L":
                    self.lower(o)
                self.raise_(k); self.st[k] = "W"
        elif si == "W" and sj == "W":
            self.raise_(i); self.st[j] = "O"
        elif si == "L" and sj == "L":
            self.lower(j); self.st[i] = "O"
        else:
            for k in (i, j):
                if self.st[k] == "W":
                    self.raise_(k)
                elif self.st[k] == "L":
                    self.lower(k)
        res = self.val[i] > self.val[j]
        self.answers.append((i, j, res))
        assert before - self.marks() <= (2 if (si, sj) == ("N", "N") else 1)
        return res

    def marks(self):
        return sum({"N": 2, "W": 1, "L": 1, "O": 0}[s] for s in self.st)

    def consistent(self, x):
        return all((x[i] > x[j]) == r for i, j, r in self.answers)

    def completion(self):
        x = list(self.val)
        for i in range(self.n):
            if x[i] is None:
                x[i] = 0.5 + i * 1e-3  # untouched elements sit between L and W values
        return x


def play(n, seq):
    A = MarkAdversary(n)
    for i, j in seq:
        A.compare(i, j)
    x = A.completion()
    ok = A.consistent(x) and len(set(x)) == n
    ok &= A.double <= n // 2
    ok &= A.marks() >= 2 * n - len(seq) - A.double
    plus = [k for k in range(n) if A.st[k] in "NW"]
    minus = [k for k in range(n) if A.st[k] in "NL"]
    answers = set()
    # every + element can be made the maximum, every - element the minimum, consistently
    for k in plus:
        y = list(x)
        y[k] = max(x) + 1
        if A.consistent(y):
            answers.add(("max", k))
    for k in minus:
        y = list(x)
        y[k] = min(x) - 1
        if A.consistent(y):
            answers.add(("min", k))
    ok &= len([a for a in answers if a[0] == "max"]) == len(plus)
    ok &= len([a for a in answers if a[0] == "min"]) == len(minus)
    return ok, len(plus), len(minus)


ok_play = ok_open = True
cnt = 0
for n in range(2, 6):
    pairs = list(itertools.combinations(range(n), 2))
    L = minmax_target(n) - 1
    for seq in itertools.product(pairs, repeat=L):
        cnt += 1
        o, p, m = play(n, seq)
        ok_play &= o
        ok_open &= (p >= 2 or m >= 2) and p >= 1 and m >= 1
for n in range(6, 15):
    pairs = list(itertools.combinations(range(n), 2))
    for _ in range(3000):
        seq = [random.choice(pairs) for _ in range(minmax_target(n) - 1)]
        cnt += 1
        o, p, m = play(n, seq)
        ok_play &= o
        ok_open &= (p >= 2 or m >= 2)
check(f"13.7 mark adversary vs {cnt} comparison sequences of length ceil(3n/2) - 3 (all of them for n <= 5, random "
      "for n = 6..14): answers consistent, only N-vs-N comparisons remove two marks, every + element can still be "
      "the maximum and every - element the minimum", ok_play)
check("13.7 ... and after that many comparisons some answer is still open (two + or two - marks remain)", ok_open)

# =====================================================================================================
# 13.8 median and k-th largest
def kth_largest(k):
    return lambda p: p.index(len(p) - k)


med = {}
games = {}
for n in (2, 4, 6):
    g = CompGame(n, kth_largest(n // 2))
    med[n] = g.value()
    games[n] = g
check("13.8 exhaustive search: the median (n/2-th largest) of n = 2, 4, 6 needs exactly 1, 4, 8 comparisons",
      [med[n] for n in (2, 4, 6)] == [1, 4, 8], f"{med}")
note_lb = {n: n // 2 - 1 + math.log2(math.comb(n, n // 2 - 1)) for n in (2, 4, 6)}
fix_lb = {n: n // 2 + math.log2(math.comb(n, n // 2 - 1)) for n in (2, 4, 6)}
check("13.8 the page's bound n/2 + lg C(n, n/2-1) (X minus L has n/2 + 1 elements) holds and is exact for n = 2, 4",
      all(math.ceil(fix_lb[n] - 1e-9) <= med[n] for n in med) and math.ceil(fix_lb[2]) == 1 and math.ceil(fix_lb[4]) == 4)
check("13.8 the note's n/2 - 1 + lg C(n, n/2-1) is one lower (0, 3 and 6 for n = 2, 4, 6)",
      [math.ceil(note_lb[n] - 1e-9) for n in (2, 4, 6)] == [0, 3, 6])
# Lemma 1 on every state the search visited
lem = True
for n in (4, 6):
    g = games[n]
    m_target = n - n // 2  # value of the n/2-th largest in 0..n-1
    for S in g.memo:
        idx = [k for k in range(len(g.perms)) if (S >> k) & 1]
        meds = {g.perms[k].index(m_target) for k in idx}
        if len(meds) == 1:
            m = meds.pop()
            for i in range(n):
                if i != m:
                    lem &= len({g.perms[k][i] > g.perms[k][m] for k in idx}) == 1
check("13.8 Lemma 1 on every state reached in the search (n = 4, 6): once the median is determined, so is the side of "
      "the median every other element is on", lem)
kth_ok, exact_k12 = True, True
for n in range(2, 7):
    for k in range(1, n // 2 + 1):
        v = CompGame(n, kth_largest(k)).value()
        lb = n - k + clg(math.comb(n, k - 1))
        kth_ok &= lb <= v
        if k in (1, 2):
            exact_k12 &= v == lb
check("13.8 n - k + ceil(lg C(n, k-1)) <= exact cost of the k-th largest, all k <= n/2, n <= 6", kth_ok)
check("13.8 ... with equality for k = 1 (n - 1) and k = 2 (n - 2 + ceil(lg n)), n <= 6", exact_k12)
r = [2 ** (math.log2(math.comb(n, n // 2 - 1)) + 0.5 * math.log2(n / 2) - n) for n in (100, 1000, 10000)]
check("13.8 C(n, n/2 - 1) ≈ 2^n sqrt(2/(pi n)): the note's 2^n/sqrt(n/2) is off by the constant sqrt(pi) "
      "(ratio -> 1/sqrt(pi) ≈ 0.564)", all(abs(x - 1 / math.sqrt(math.pi)) < 0.02 for x in r), f"{r}")
check("13.8 n/2 + lg C(n, n/2-1) = 3n/2 - O(log n): difference from 3n/2 - (1/2) lg n bounded (n <= 4000)",
      max(abs(n / 2 + math.log2(math.comb(n, n // 2 - 1)) - (1.5 * n - 0.5 * math.log2(n))) for n in range(4, 4001, 2)) < 2)

# =====================================================================================================
# concept page example: is the array sorted?
srt = {n: CompGame(n, lambda p: p == tuple(sorted(p))).value() for n in range(1, 7)}
check("concept: deciding whether x_1 < ... < x_n needs exactly n - 1 comparisons, n = 1..6",
      all(srt[n] == max(n - 1, 0) for n in srt), f"{srt}")
ok = True
for n in range(2, 7):
    pairs = list(itertools.combinations(range(n), 2))
    for L in range(0, n - 1):
        for seq in itertools.product(pairs, repeat=L):
            adj = [i for i in range(n - 1) if (i, i + 1) not in seq]
            if not adj:
                ok = False
                continue
            i = adj[0]
            x = list(range(n))
            y = list(x)
            y[i], y[i + 1] = y[i + 1], y[i]
            ok &= all((x[a] < x[b]) == (y[a] < y[b]) for a, b in seq) and y != sorted(y)
check("concept: answering as if x_i = i, every sequence of < n - 1 comparisons skips an adjacent pair, and swapping "
      "it gives an unsorted input with the same answers (n <= 6)", ok)

# page text
check("13.8 the page's rounded bound ceil(n/2 + lg C(n, n/2-1)) is 1, 4, 7 for n = 2, 4, 6",
      [math.ceil(fix_lb[n] - 1e-9) for n in (2, 4, 6)] == [1, 4, 7])
for path, frags in ((PAGE, [r"\lceil 3n/2\rceil - 2", "r - \\ell - 1", "Aanderaa", "$1, 4, 8$", "$1, 4, 7$",
                            "127,226", "all 22 nontrivial", r"n\bmod 3\ne 1"]),
                    (CONCEPT, ["n - 1", r"\lceil 3n/2\rceil - 2", "$n\\le 6$"])):
    if os.path.exists(path):
        txt = open(path, encoding="utf-8").read()
        for f in frags:
            check(f"{os.path.basename(path)} mentions {f}", f in txt)
    else:
        print(f"({os.path.basename(path)} not written yet)")

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: {FAIL}")
