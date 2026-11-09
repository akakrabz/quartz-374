#!/usr/bin/env python3
"""Checks for content/4-lecture-notes/08-randomized-minimum-cut.md and content/concepts/randomized-minimum-cut.md
(Erickson, Director's Cut 8, "Randomized Minimum Cut"; the PDF numbers it 13).

Multigraphs are lists of edges (u, v) with repetitions. Edge contraction keeps parallel edges and deletes the edges
between the two merged vertices. The exact output distribution of GuessMinCut is computed by enumerating contraction
sequences (memoized on the vertex partition, exact Fractions) and compared with the bound 2/(n(n-1)) for every minimum
cut of many small graphs (cycles attain it); the number of minimum cuts is checked against n(n-1)/2 on all small
graphs; Karger–Stein's BetterGuess is evaluated exactly on small graphs; every product, recurrence and inequality of
the note is checked exactly or numerically, including the ones the note gets wrong (loop bounds, an inequality
direction, footnote 4, the amplification exponent, the constant alpha)."""
import itertools
import math
import os
import random
import re
import sys
from fractions import Fraction as Fr
from functools import lru_cache

import networkx as nx

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
PAGE = os.path.join(ROOT, "content", "4-lecture-notes", "08-randomized-minimum-cut.md")
CONCEPT = os.path.join(ROOT, "content", "concepts", "randomized-minimum-cut.md")
FAIL = []
random.seed(8374)


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAIL.append(name)


def read(path):
    return open(path, encoding="utf-8").read() if os.path.exists(path) else ""


# =====================================================================================================
# Multigraphs on vertices 0..n-1: tuple of edges (u, v), u != v, repetitions = parallel edges.
def cut_size(E, S):
    return sum(1 for u, v in E if (u in S) != (v in S))


def all_cuts(n):
    """Every cut once: the side S that contains vertex 0, S != V."""
    for k in range(0, n - 1):
        for X in itertools.combinations(range(1, n), k):
            yield frozenset((0,) + X)


def min_cuts(n, E):
    best, arg = None, []
    for S in all_cuts(n):
        c = cut_size(E, S)
        if best is None or c < best:
            best, arg = c, [S]
        elif c == best:
            arg.append(S)
    return best, arg


def connected(n, E):
    G = nx.MultiGraph()
    G.add_nodes_from(range(n))
    G.add_edges_from(E)
    return nx.is_connected(G)


def contract(E, u, v, name):
    """G/{u,v}: new vertex `name`; edges u-v vanish (no self-loops); every other edge keeps its multiplicity."""
    out = []
    for a, b in E:
        if {a, b} == {u, v}:
            continue
        a2 = name if a in (u, v) else a
        b2 = name if b in (u, v) else b
        out.append((a2, b2))
    return out


# ---- exact distributions over partitions (labels: tuple, label[v] = block representative)
def canon(lbl):
    m, out = {}, []
    for x in lbl:
        if x not in m:
            m[x] = len(m)
        out.append(m[x])
    return tuple(out)


def make_dist(n, E):
    E = tuple(E)

    @lru_cache(maxsize=None)
    def step_dist(lbl):
        """Distribution of the partition after one uniformly random contraction."""
        cross = [(u, v) for u, v in E if lbl[u] != lbl[v]]
        out = {}
        for u, v in cross:
            a, b = lbl[u], lbl[v]
            new = canon(tuple(a if x == b else x for x in lbl))
            out[new] = out.get(new, 0) + Fr(1, len(cross))
        return out

    @lru_cache(maxsize=None)
    def contract_to(lbl, t):
        """Distribution of the partition after contracting random edges until t blocks remain."""
        if len(set(lbl)) <= t:
            return {lbl: Fr(1)}
        out = {}
        for nxt, p in step_dist(lbl).items():
            for fin, q in contract_to(nxt, t).items():
                out[fin] = out.get(fin, 0) + p * q
        return out

    return step_dist, contract_to


def side0(lbl):
    return frozenset(v for v in range(len(lbl)) if lbl[v] == lbl[0])


def guess_distribution(n, E):
    """Exact distribution of the cut returned by GuessMinCut (contract until 2 vertices remain)."""
    _, contract_to = make_dist(n, E)
    dist = {}
    for lbl, p in contract_to(tuple(range(n)), 2).items():
        S = side0(lbl)
        dist[S] = dist.get(S, 0) + p
    return dist


def better_guess_success(n, E, target, base=2, calls=4):
    """Exact probability that BetterGuess returns a cut of size lambda(G); Contract(H, target(h)) then `calls`
    independent recursive calls on the same H; brute force when h <= base."""
    lam, _ = min_cuts(n, E)
    _, contract_to = make_dist(n, E)

    def lam_of(lbl):
        blocks = sorted(set(lbl))
        best = None
        for k in range(1, len(blocks)):
            for X in itertools.combinations(blocks[1:], k - 1):
                B = {blocks[0], *X}
                S = frozenset(v for v in range(n) if lbl[v] in B)
                c = cut_size(E, S)
                best = c if best is None else min(best, c)
        return best

    @lru_cache(maxsize=None)
    def S(lbl):
        h = len(set(lbl))
        if h <= base:
            return Fr(1) if lam_of(lbl) == lam else Fr(0)
        tot = Fr(0)
        for H, p in contract_to(lbl, target(h)).items():
            s = S(H)
            tot += p * (1 - (1 - s) ** calls)
        return tot

    return S(tuple(range(n)))


def cycle(n, mult=None):
    E = []
    for i in range(n):
        E += [(i, (i + 1) % n)] * (mult[i] if mult else 1)
    return E


def complete(n):
    return [(i, j) for i in range(n) for j in range(i + 1, n)]


def random_multigraph(n, m, maxmult=2):
    while True:
        E = []
        pairs = random.sample([(i, j) for i in range(n) for j in range(i + 1, n)], m)
        for p in pairs:
            E += [p] * random.randint(1, maxmult)
        if connected(n, E):
            return E


# =====================================================================================================
print("== 8.1 the multigraph of p. 1 ==")
NAMES = "abcdefgh"
I = {c: k for k, c in enumerate(NAMES)}
EP1 = [("a", "c"), ("a", "g"), ("a", "d"), ("c", "d"), ("c", "g"), ("c", "g"), ("g", "d"),
       ("a", "b"), ("d", "e"), ("g", "h"),
       ("b", "e"), ("b", "h"), ("b", "f"), ("b", "f"), ("e", "h"), ("h", "f")]
E1 = [(I[a], I[b]) for a, b in EP1]
lam1, mc1 = min_cuts(8, E1)
sides = sorted("".join(NAMES[v] for v in sorted(S if 0 in S and len(S) <= 4 else frozenset(range(8)) - S)) for S in mc1)
deg1 = {c: sum(1 for e in EP1 if c in e) for c in NAMES}
check("p. 1 multigraph: 8 vertices, 16 edges, minimum cut 3", len(E1) == 16 and lam1 == 3, f"degrees {deg1}")
check("its minimum cuts: {a,c,d,g} | {b,e,f,h}, {e} | rest, {f} | rest — exactly three", len(mc1) == 3
      and {frozenset(x) for x in [{I[c] for c in "acdg"}, set(range(8)) - {I["e"]}, set(range(8)) - {I["f"]}]}
      == set(mc1), str(sides))
d1 = guess_distribution(8, E1)
p1 = {"".join(sorted(NAMES[v] for v in (frozenset(range(8)) - S if len(S) > 4 else S))): d1.get(S, 0) for S in mc1}
succ1 = sum(d1.get(S, 0) for S in mc1)
check("GuessMinCut on it: every minimum cut has probability >= 2/(8*7) = 1/28 (exact)",
      all(d1.get(S, 0) >= Fr(1, 28) for S in mc1), ", ".join(f"{k}: {float(v):.4f}" for k, v in p1.items())
      + f"; success {float(succ1):.4f}")
P1_SUCC = succ1

print("== the figure of p. 2 (reconstructed) ==")
# T top, L top-left, R top-right, C centre, X bottom-left, Y bottom-right, B bottom (edge weights from the figure)
F2 = [("L", "T"), ("T", "R"), ("L", "R"), ("L", "C"), ("C", "R"), ("L", "X"), ("X", "C"), ("C", "Y"), ("R", "Y"),
      ("C", "B"), ("X", "B"), ("B", "Y")]
VN = "TLRCXYB"
J = {c: k for k, c in enumerate(VN)}
E2 = [(J[a], J[b]) for a, b in F2]
lam2, mc2 = min_cuts(7, E2)
check("p. 2 figure: the pictured G has minimum cut 2 (top vertex), no cut of size 1 as the text claims",
      lam2 == 2 and len(mc2) == 1)
E2c = contract(E2, J["L"], J["C"], 99)
par = sorted(e for e in E2c if 99 in e)
check("contracting the highlighted edge keeps two pairs of parallel edges (the figure deletes one of each pair)",
      sum(1 for e in E2c if set(e) == {99, J["R"]}) == 2 and sum(1 for e in E2c if set(e) == {99, J["X"]}) == 2)

print("== contraction lemmas ==")
lemma_ok = corr_ok = inc_ok = True
for trial in range(300):
    n = random.randint(3, 7)
    E = random_multigraph(n, random.randint(n, min(n * (n - 1) // 2, 2 * n)))
    lam, mcs = min_cuts(n, E)
    for (u, v) in set(E):
        Ec = contract(E, u, v, u)            # u absorbs v; vertex v disappears
        # cuts of G/{u,v} = cuts of G with u, v on the same side, with the same crossing edges
        for S in all_cuts(n):
            if (u in S) == (v in S):
                Sc = frozenset(x for x in S if x != v)
                if cut_size(Ec, Sc) != cut_size(E, S):
                    corr_ok = False
        Vc = [x for x in range(n) if x != v]
        m2 = n - 1
        relabel = {x: k for k, x in enumerate(Vc)}
        lamc, _ = min_cuts(m2, [(relabel[a], relabel[b]) for a, b in Ec])
        if lamc < lam:
            lemma_ok = False
        in_every = all((u in S) != (v in S) for S in mcs)
        if (lamc > lam) != in_every:
            inc_ok = False
check("every cut of G/{u,v} is a cut of G with exactly the same crossing edges (300 random multigraphs)", corr_ok)
check("contraction never decreases the minimum cut", lemma_ok)
check("contracting uv increases the minimum cut iff uv crosses every minimum cut", inc_ok)

# every vertex has degree >= lambda, so |E| >= lambda n / 2 and Pr[first edge in a fixed min cut] <= 2/n
deg_ok = True
for trial in range(300):
    n = random.randint(2, 8)
    E = random_multigraph(n, random.randint(n - 1, n * (n - 1) // 2), 3)
    lam, mcs = min_cuts(n, E)
    if not (2 * len(E) >= lam * n and Fr(lam, len(E)) <= Fr(2, n)):
        deg_ok = False
check("|E| >= lambda n/2, hence a random edge lies in a fixed minimum cut with probability <= 2/n", deg_ok)

print("== 8.2 GuessMinCut, exactly ==")
# the printed loop 'for i <- n downto 2' contracts n - 1 times: one vertex is left
def literal_guess(n, E, lo):
    V = set(range(n))
    E = list(E)
    nxt = n
    for i in range(n, lo - 1, -1):
        if not E:
            return None
        u, v = random.choice(E)
        E = contract(E, u, v, nxt)
        V = (V - {u, v}) | {nxt}
        nxt += 1
    return len(V)


check("GuessMinCut as printed ('for i <- n downto 2') contracts n - 1 edges and leaves 1 vertex, not 2",
      all(literal_guess(6, complete(6), 2) == 1 for _ in range(20))
      and all(literal_guess(6, complete(6), 3) == 2 for _ in range(20)))
check("Contract(G, m) as printed ('for i <- n downto m') leaves m - 1 vertices",
      all(literal_guess(8, complete(8), 4) == 3 for _ in range(10)))

bound_ok, cyc_ok = True, True
graphs = []
for n in range(3, 6):
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    for mask in range(1, 2 ** len(pairs)):
        E = [pairs[k] for k in range(len(pairs)) if mask >> k & 1]
        if connected(n, E):
            graphs.append((n, E))
for _ in range(60):
    n = random.choice([5, 6, 7])
    graphs.append((n, random_multigraph(n, random.randint(n, n * (n - 1) // 2), 3)))
worst_ratio = None
for n, E in graphs:
    lam, mcs = min_cuts(n, E)
    d = guess_distribution(n, E)
    for S in mcs:
        r = d.get(S, 0) / Fr(2, n * (n - 1))
        worst_ratio = r if worst_ratio is None else min(worst_ratio, r)
        if r < 1:
            bound_ok = False
check(f"every minimum cut is returned with probability >= 2/(n(n-1)): all {len([g for g in graphs if g[0] <= 5])} "
      f"connected simple graphs on 3-5 vertices and 60 random multigraphs on 5-7", bound_ok,
      f"min ratio prob / bound = {worst_ratio}")
for n in range(3, 9):
    d = guess_distribution(n, cycle(n))
    lam, mcs = min_cuts(n, cycle(n))
    if not (len(mcs) == n * (n - 1) // 2 and all(d[S] == Fr(2, n * (n - 1)) for S in mcs) and sum(d.values()) == 1):
        cyc_ok = False
check("cycles C_3..C_8 attain the bound: each of the n(n-1)/2 minimum cuts has probability exactly 2/(n(n-1))", cyc_ok)

# product of the recurrence
prod_ok = all(math.prod(Fr(i - 2, i) for i in range(3, n + 1)) == Fr(2, n * (n - 1)) for n in range(3, 60))
check("prod_{i=3}^{n} (i-2)/i = 2/(n(n-1)), n = 3..59", prod_ok)

# K_4 and C_4 (concept page)
dK4 = guess_distribution(4, complete(4))
lamK, mcK = min_cuts(4, complete(4))
check("K_4: minimum cut 3, four minimum cuts (single vertices), each returned with probability 1/5 >= 1/6, "
      "success 4/5", lamK == 3 and len(mcK) == 4 and all(dK4[S] == Fr(1, 5) for S in mcK)
      and sum(dK4[S] for S in mcK) == Fr(4, 5))
dC4 = guess_distribution(4, cycle(4))
check("C_4: six minimum cuts of size 2, each returned with probability exactly 1/6, success 1",
      min_cuts(4, cycle(4))[0] == 2 and len(dC4) == 6 and all(v == Fr(1, 6) for v in dC4.values()))

print("== number of minimum cuts ==")
cnt_ok, cnt_max = True, {}
for n in range(2, 7):
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    for mask in range(1, 2 ** len(pairs)):
        E = [pairs[k] for k in range(len(pairs)) if mask >> k & 1]
        if not connected(n, E):
            continue
        k = len(min_cuts(n, E)[1])
        cnt_max[n] = max(cnt_max.get(n, 0), k)
        if k > n * (n - 1) // 2:
            cnt_ok = False
for _ in range(300):
    n = 7
    E = random_multigraph(n, random.randint(n, 14), 2)
    if len(min_cuts(n, E)[1]) > 21:
        cnt_ok = False
check("at most n(n-1)/2 minimum cuts: all connected simple graphs on 2-6 vertices, 300 random multigraphs on 7",
      cnt_ok and all(cnt_max[n] == n * (n - 1) // 2 for n in cnt_max), f"max found {cnt_max} (attained by cycles)")

print("== 8.3 amplification ==")
dir_ok = True
for n in (5, 10, 50):
    x = Fr(2, n * (n - 1))
    for N in (1, 10, 100, 1000):
        lhs = 1 - (1 - float(x)) ** N
        rhs = 1 - math.exp(-2 * N / (n * (n - 1)))
        if not lhs >= rhs - 1e-15:
            dir_ok = False
check("1 - (1 - 2/(n(n-1)))^N >= 1 - e^{-2N/(n(n-1))} (the note prints <=; 1 + x <= e^x gives >=)", dir_ok
      and 1 - (1 - 0.1) ** 3 > 1 - math.exp(-0.3))
check("N = c C(n,2) ln n gives failure e^{-c ln n} = n^{-c}; N = n^2(n-1)/2 gives e^{-n}",
      all(abs(2 * (c * n * (n - 1) / 2 * math.log(n)) / (n * (n - 1)) - c * math.log(n)) < 1e-9
          and abs(2 * (n * n * (n - 1) / 2) / (n * (n - 1)) - n) < 1e-9 for c in (1, 2, 3) for n in (5, 50, 500)))
check("N = n^2(n-1)/2: failure probability (1 - 2/(n(n-1)))^N is at most (not equal to) e^{-n}",
      all((1 - Fr(2, n * (n - 1))) ** (n * n * (n - 1) // 2) < Fr(math.exp(-n)) for n in range(3, 9)))
# exact: KargerMinCut with N repetitions on the p.1 graph
N = 10
fail_exact = (1 - P1_SUCC) ** N
check(f"p. 1 multigraph: exact success probability of one guess {float(P1_SUCC):.4f}; with N = {N} independent guesses "
      f"failure {float(fail_exact):.2e}", fail_exact == (1 - P1_SUCC) ** N and P1_SUCC > Fr(1, 28))

print("== 8.4 Karger–Stein ==")
safe_ok = all(math.prod(Fr(i - 2, i) for i in range(n // 2 + 1, n + 1)) == Fr(n - 2, 4 * (n - 1)) == Fr((n // 2) * (n // 2 - 1), n * (n - 1))
              and Fr(n - 2, 4 * (n - 1)) < Fr(1, 4) for n in range(4, 200, 2))
check("safe phase to n/2 vertices: prod_{i=n/2+1}^{n} (i-2)/i = (n-2)/(4(n-1)) < 1/4 (n even, 4..198)", safe_ok)
plus1 = all(Fr((n // 2 + 1) * (n // 2), n * (n - 1)) == Fr(n + 2, 4 * (n - 1)) and Fr(n + 2, 4 * (n - 1)) > Fr(1, 4)
            for n in range(4, 200, 2))
check("contracting to n/2 + 1 vertices instead: (n+2)/(4(n-1)) > 1/4", plus1)
fn4 = [n for n in range(4, 2000) if Fr((math.ceil(n / 2) + 1) * math.ceil(n / 2), n * (n - 1)) > Fr(1, 2)]
check("footnote 4 is false: contracting to ceil(n/2) + 1 vertices gives t(t-1)/(n(n-1)) > 1/2 only for n = 5 "
      "(= 1/2 at n = 4, < 1/2 for n >= 6, tending to 1/4)", fn4 == [5],
      f"n=4: {Fr(3*2, 12)}, n=5: {Fr(4*3, 20)}, n=10: {Fr(6*5, 90)}, n=1000: {float(Fr(501*500, 1000*999)):.4f}")
fn4all = [n for n in range(2, 2000) if Fr((math.ceil(n / 2) + 1) * math.ceil(n / 2), n * (n - 1)) > Fr(1, 2)]
check("footnote 4 for every n >= 2: > 1/2 exactly for n = 2, 3 (ceil(n/2) + 1 = n: nothing contracted) and n = 5",
      fn4all == [2, 3, 5] and all(math.ceil(n / 2) + 1 == n for n in (2, 3)))
fix = all(Fr(t * (t - 1), n * (n - 1)) > Fr(1, 2) for n in range(3, 20000)
          for t in [math.ceil(1 + n / math.sqrt(2))] if t <= n)
check("contracting to ceil(1 + n/sqrt 2) vertices gives > 1/2 (n = 3..19999): the true Karger–Stein choice", fix)

# exact BetterGuess on small graphs: near-cycle with a unique minimum cut, and the p.1 graph
NEAR = cycle(8, [3, 4, 4, 4, 3, 4, 4, 4])  # unique minimum cut: the two edges of multiplicity 3
lamN, mcN = min_cuts(8, NEAR)
check("test graph: 8-cycle, multiplicities 3,4,4,4,3,4,4,4 has a unique minimum cut of size 6", lamN == 6 and len(mcN) == 1)
dN = guess_distribution(8, NEAR)
gN = dN.get(mcN[0], 0)
half = lambda h: h // 2                    # noqa: E731
half1 = lambda h: h // 2 + 1 if h > 3 else 2  # noqa: E731
ksN = better_guess_success(8, NEAR, half, base=2)
ksN1 = better_guess_success(8, NEAR, half1, base=3)
# the note's recurrence with base P(2) = 1: P(4) = 1/4, P(8) = 1/4 (1 - (3/4)^4) = 175/1024
P4 = Fr(1, 4) * (1 - (1 - Fr(1)) ** 4)
P8 = Fr(1, 4) * (1 - (1 - P4) ** 4)
check("note's recurrence with P(2) = 1: P(4) = 1/4, P(8) = 175/1024", P4 == Fr(1, 4) and P8 == Fr(175, 1024))
# exact survival of a fixed minimum cut S: no contracted edge crosses S <=> every block lies on one side of S
def survives(lbl, S):
    return all(len({(v in S) for v in range(len(lbl)) if lbl[v] == b}) == 1 for b in set(lbl))


_, ct = make_dist(8, NEAR)
surv = sum(p for lbl, p in ct(tuple(range(8)), 4).items() if survives(lbl, mcN[0]))
_, ctc = make_dist(8, cycle(8))
Sc = frozenset({0, 1, 2, 3})
survc = sum(p for lbl, p in ctc(tuple(range(8)), 4).items() if survives(lbl, Sc))
check(f"C_8: a fixed minimum cut survives contraction to 4 vertices with probability exactly 3/14 = (8-2)/(4*7) < 1/4",
      survc == Fr(3, 14))
check(f"near-cycle: the unique minimum cut survives contraction to 4 vertices with probability {float(surv):.4f} "
      f">= 3/14", surv >= Fr(3, 14))
# corrected recurrence for the n/2 version: P(n) >= t(t-1)/(n(n-1)) (1 - (1 - P(t))^4), t = n/2, P(2) = 1
Q4 = Fr(2 * 1, 4 * 3) * (1 - (1 - Fr(1)) ** 4)
Q8 = Fr(4 * 3, 8 * 7) * (1 - (1 - Q4) ** 4)
check(f"near-cycle: exact BetterGuess (to n/2, four calls, brute force at 2) succeeds with probability "
      f"{float(ksN):.4f} >= {float(Q8):.4f}, the recurrence with the exact survival factors 1/6 and 3/14",
      ksN >= Q8, str(ksN))
check(f"near-cycle: GuessMinCut {float(gN):.4f} >= 2/56; BetterGuess {float(ksN):.4f} > GuessMinCut",
      gN >= Fr(2, 56) and ksN > gN)
# version contracting to h/2 + 1 (8 -> 5 -> 3, brute force at 3): recurrence P(n) >= 1/4 (1 - (1 - P(n/2+1))^4) holds
rec5 = Fr(1, 4) * (1 - (1 - Fr(1)) ** 4)       # P(5) >= 1/4 (1 - (1 - P(3))^4), P(3) = 1
rec8 = Fr(1, 4) * (1 - (1 - rec5) ** 4)
check(f"near-cycle, contracting to h/2 + 1 (8 -> 5 -> 3): exact success {float(ksN1):.4f} >= recurrence bound "
      f"{float(rec8):.4f}", ksN1 >= rec8)
ks_p1 = better_guess_success(8, E1, half1, base=3)
check(f"p. 1 multigraph: BetterGuess (to h/2 + 1) succeeds with probability {float(ks_p1):.4f} >= {float(rec8):.4f}",
      ks_p1 >= rec8)
KS_NUM = (gN, ksN, ksN1, surv)

# 8.5 the recurrence: p(k) = 1/4 - 1/4 (1 - p(k-1))^4, p(1) = 1; d = 1/p
from decimal import Decimal, getcontext  # noqa: E402

getcontext().prec = 60
p = Decimal(1)
d_prev = Decimal(1)
rec_ok = True
ds = {1: Decimal(1)}
for k in range(2, 2001):
    p = Decimal(1) / 4 - (1 - p) ** 4 / 4
    d = 1 / p
    ds[k] = d
    if not (d_prev < d <= d_prev + 3 and d <= 3 * k - 2):
        rec_ok = False
    d_prev = d
check("d(k) = 1/p(k): d(k-1) < d(k) <= d(k-1) + 3 and d(k) <= 3k - 2 for k = 2..2000", rec_ok,
      f"d(2) = {float(ds[2]):.4f}, d(10) = {float(ds[10]):.3f}, d(100) = {float(ds[100]):.2f}, d(2000) = {float(ds[2000]):.1f}")
check("the reciprocal form: 1/(1/4 - (1-1/d)^4/4) = 4d^4/(d^4 - (d-1)^4) (k = 2..50)",
      all(abs(ds[k] - 4 * ds[k - 1] ** 4 / (ds[k - 1] ** 4 - (ds[k - 1] - 1) ** 4)) < Decimal(10) ** -40 for k in range(2, 51)))
slope = float(ds[2000] - ds[1000]) / 1000
check("in fact d(k) grows like 3k/2: (d(2000) - d(1000))/1000 is about 1.5, so P(n) ~ 2/(3 lg n)",
      abs(slope - 1.5) < 0.01, f"{slope:.4f}")


# the inequality x < 4x^4/(x^4 - (x-1)^4) <= x + 3 for x >= 1, exactly via polynomials
def pmul(a, b):
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return out


def padd(a, b):
    n = max(len(a), len(b))
    return [(a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0) for i in range(n)]


x4 = [0, 0, 0, 0, 1]
xm1_4 = pmul(pmul([-1, 1], [-1, 1]), pmul([-1, 1], [-1, 1]))
den = padd(x4, [-c for c in xm1_4])                            # 4x^3 - 6x^2 + 4x - 1
upper = padd(pmul([3, 1], den), [0, 0, 0, 0, -4])              # (x+3) den - 4x^4
check("x^4 - (x-1)^4 = 4x^3 - 6x^2 + 4x - 1 (> 0 for x >= 1)", den == [-1, 4, -6, 4, 0] or den[:4] == [-1, 4, -6, 4])
check("(x+3)(x^4-(x-1)^4) - 4x^4 = 6x^3 - 14x^2 + 11x - 3 = (x-1)(6x^2 - 8x + 3) >= 0 for x >= 1 (discriminant < 0)",
      upper[:4] == [-3, 11, -14, 6] and all(c == 0 for c in upper[4:]) and pmul([-1, 1], [3, -8, 6]) == [-3, 11, -14, 6]
      and 8 * 8 - 4 * 6 * 3 < 0)
check("4x^4 - x(x^4-(x-1)^4) = 6x^3 - 4x^2 + x = x(6x^2 - 4x + 1) > 0 for x >= 1 (discriminant < 0)",
      padd([0, 0, 0, 0, 4], [-c for c in pmul([0, 1], den)])[:5] == [0, 1, -4, 6, 0] and 16 - 24 < 0)
lo = [1 + i / 100 for i in range(0, 100000)]
check("numerically x < 4x^4/(x^4-(x-1)^4) <= x + 3 on [1, 1000]",
      all(x < 4 * x ** 4 / (x ** 4 - (x - 1) ** 4) <= x + 3 + 1e-9 for x in lo))
check("P(n) >= 1/(3 lg n - 2): p(k) >= 1/(3k - 2) for k = 1..2000", all(1 / ds[k] >= Decimal(1) / (3 * k - 2) for k in ds))
alpha_lim = float(1 / ds[2000]) * 2000 * math.log(2)
check(f"alpha in P(n) >= alpha/ln n: the proof gives ln 2/3 = {math.log(2)/3:.3f}, the limit is (2/3) ln 2 = "
      f"{2*math.log(2)/3:.3f} — not > 2 as the note says", abs(alpha_lim - 2 * math.log(2) / 3) < 0.01, f"{alpha_lim:.4f}")
# amplification with alpha < 1: the note's bound 1 - n^{-c/alpha} fails; 1 - n^{-c alpha} holds
a, c, n = math.log(2) / 3, 1.0, 1000.0
true_s = 1 - (1 - a / math.log(n)) ** (c * math.log(n) ** 2)
check(f"with alpha = ln2/3, c = 1, n = 1000: success {true_s:.5f} < 1 - n^(-c/alpha) = {1 - n ** (-c / a):.5f} (note's "
      f"inequality fails) but >= 1 - n^(-c alpha) = {1 - n ** (-c * a):.5f}",
      true_s < 1 - n ** (-c / a) and true_s >= 1 - n ** (-c * a))
# running time T(n) = n^2 + 4T(n/2), T(1) = 1: T(2^k) = 4^k (k+1) = n^2 (lg n + 1)
T = {1: 1}
for k in range(1, 30):
    T[2 ** k] = (2 ** k) ** 2 + 4 * T[2 ** (k - 1)]
check("T(n) = n^2 + 4T(n/2), T(1) = 1 gives exactly n^2 (lg n + 1) for n = 2^k", all(T[2 ** k] == 4 ** k * (k + 1) for k in range(30)))
@lru_cache(maxsize=None)
def T2(n):
    return n * n if n <= 3 else n * n + 4 * T2(n // 2 + 1)


sys.setrecursionlimit(10000)
vals = [(n, T2(n) / (n * n) - math.log2(n)) for n in (2 ** k + 2 for k in range(4, 61, 8))]
check("with n/2 + 1 in place of n/2, T(n) = n^2 + 4T(n/2 + 1) is still Theta(n^2 log n): T(n)/n^2 - lg n settles "
      "to a constant", abs(vals[-1][1] - vals[-2][1]) < 1e-3,
      ", ".join(f"2^{round(math.log2(n - 2))}+2: {r:.4f}" for n, r in vals))

print("== flows ==")
flow_ok = True
for _ in range(200):
    n = random.randint(2, 7)
    E = random_multigraph(n, random.randint(n - 1, n * (n - 1) // 2), 3) if n > 2 else [(0, 1)] * random.randint(1, 3)
    lam, _ = min_cuts(n, E)
    D = nx.DiGraph()
    for u, v in E:
        for a, b in ((u, v), (v, u)):
            D.add_edge(a, b, capacity=D[a][b]["capacity"] + 1 if D.has_edge(a, b) else 1)
    best = min(nx.minimum_cut_value(D, 0, t) for t in range(1, n))
    if best != lam:
        flow_ok = False
check("global minimum cut = min over t != s of the minimum (s,t)-cut (each edge in both directions, capacity = "
      "multiplicity): n - 1 maximum-flow computations (200 random multigraphs)", flow_ok)

print("== page text ==")
page = read(PAGE)
concept = read(CONCEPT)
check("page and concept page exist", bool(page) and bool(concept))
P1V = {k: float(v) for k, v in p1.items()}
check("page: p.1 graph probabilities 0.117 ({a,c,d,g}), 0.123 ({e}), 0.142 ({f}), success 0.382",
      round(P1V["acdg"], 3) == 0.117 and round(P1V["e"], 3) == 0.123 and round(P1V["f"], 3) == 0.142
      and round(float(P1_SUCC), 3) == 0.382 and all(x in page for x in ("0.117", "0.123", "0.142", "0.382")))
check("page: near-cycle GuessMinCut 0.068, BetterGuess 0.193", round(float(gN), 3) == 0.068
      and round(float(ksN), 3) == 0.193 and "0.068" in page and "0.193" in page)
n_small = len([g for g in graphs if g[0] <= 5])
check("page: 787 connected simple graphs on 3-5 vertices", n_small == 787 and "787" in page)
check("page: alpha = ln2/3 = 0.23 from the proof, limit (2/3) ln 2 = 0.46", round(math.log(2) / 3, 2) == 0.23
      and round(2 * math.log(2) / 3, 2) == 0.46 and "0.23" in page and "0.46" in page)
check("page: 2/56 = 0.036 and 2^(n-1) - 1 cuts in all", round(2 / 56, 3) == 0.036
      and all(sum(1 for _ in all_cuts(k)) == 2 ** (k - 1) - 1 for k in range(2, 9)))
# the second contraction in K_4 after contracting ab: edges x-c, x-c, x-d, x-d, c-d
Ek = contract(complete(4), 0, 1, 0)
second = {k: Fr(v, len(Ek)) for k, v in
          __import__("collections").Counter({(0, 2): "xc", (0, 3): "xd", (2, 3): "cd"}[tuple(sorted(e))] for e in Ek).items()}
check("concept example: K_4 numbers 2/5, 2/5, 1/5 for the second contraction",
      second == {"xc": Fr(2, 5), "xd": Fr(2, 5), "cd": Fr(1, 5)} and "1/5" in concept and "4/5" in concept, str(second))
check("K_4 after one contraction: x joined to c and d by two edges each, plus cd (5 edges)",
      sorted(Ek) == sorted([(0, 2), (0, 2), (0, 3), (0, 3), (2, 3)]))
fig = read(os.path.join(HERE, "..", "figs", "n08-multigraph.html"))
check("figure n08-multigraph: 8 vertices and 16 edges in the caption; e and f the other minimum cuts",
      "8 vertices and 16 edges" in fig and len(E1) == 16)
# figure n08-contraction (review R26): G on u..y, minimum cuts {u}, {u,v}, {y}, {x,y}; after contracting uv, three left
VC = "uvwxy"
EC = [("u", "v"), ("u", "v"), ("u", "w"), ("v", "w"), ("v", "x"), ("w", "x"), ("w", "y"), ("x", "y"), ("x", "y")]
ECi = [(VC.index(a), VC.index(b)) for a, b in EC]
lamC, mcC = min_cuts(5, ECi)
sidesC = sorted("".join(sorted(VC[v] for v in (S if len(S) <= 2 else frozenset(range(5)) - S))) for S in mcC)
ECc = contract(ECi, 0, 1, 0)
VCc = [0, 2, 3, 4]
lamCc, mcCc = min_cuts(4, [(VCc.index(a), VCc.index(b)) for a, b in ECc])
sidesCc = sorted("".join(sorted("U" if VCc[v] == 0 else VC[VCc[v]] for v in (S if 0 not in S else frozenset(range(4)) - S)))
                 for S in mcCc)
check("figure n08-contraction: G has 9 edges, minimum cut 3 by {u}, {u,v}, {y}, {x,y}; G/{u,v} has 7 edges, minimum "
      "cut 3, cuts {y}, {x,y} and {w,x,y} = {u,v} | rest",
      len(EC) == 9 and lamC == 3 and sidesC == ["u", "uv", "xy", "y"] and len(ECc) == 7 and lamCc == 3
      and sidesCc == ["wxy", "xy", "y"], f"{sidesC}; {sidesCc}")

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: {FAIL}")
