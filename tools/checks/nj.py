#!/usr/bin/env python3
"""Checks for content/4-lecture-notes/j-approximation-algorithms.md (Erickson's note J, Approximation Algorithms) and the
concept page content/concepts/approximation-algorithms.md.

Every algorithm is implemented exactly as the page states it and run on many small random instances whose optimum is
computed by brute force; the claimed ratio is checked on every instance and the worst ratio seen is printed.
  * J.1  GreedyLoadBalance / SortedGreedyLoadBalance against brute-force makespans (ratios 2, 3/2 and the exact
         2 - 1/m, 4/3 - 1/(3m)), the steps of both proofs, instances attaining the exact ratios, the Partition remark.
  * J.3  GreedyVertexCover on every graph with at most 6 vertices and random larger ones: the halving lemma, the bound
         OPT(floor(lg m) + 1) on the number of iterations (the note's OPT lg m fails for one edge), H(Delta); an
         explicit family with ratio growing like log n (the note's claim; the family itself is not on the page).
  * J.4  GreedySetCover / GreedyHittingSet against brute force, H(max set size) bounds, duality, and the family that
         refutes the note's O(log |F|) for set cover (greedy k sets, optimum 2, |F| = k + 2).
  * J.5  DumbVertexCover (a maximal matching, both ends) and its hitting-set version; the weighted path example.
  * J.6  LP rounding with scipy.optimize.linprog: LP <= OPT <= rounded <= 2 LP; C5 and K_n.
  * J.7  Randomized rounding: exact expectations and probabilities by enumeration; the note's "minimized" and
         "exactly N OPT~" are wrong (maximized; at most).
  * J.8  Hamiltonian cycle -> TSP with lengths 1/2, 1/(n+1) and 1/(alpha n + 1) on all graphs with <= 5 vertices and
         random ones with 6 or 7; a factor of exactly 2 does not separate (C5 plus a chord; the path P5).
  * J.9  Tree doubling and Christofides (brute-force minimum perfect matching, Hierholzer) against brute-force or
         Held-Karp optimal tours on random Euclidean and random graph metrics; every inequality of both proofs; the
         figure instance; tight families for both; a non-metric instance where tree doubling exceeds 2.
  * J.10 GonzalezKCenter against the exact continuous k-center optimum (subset DP over minimum enclosing circles).
  * J.11 The grid approximation scheme for k-center (phases 1-3) against the exact optimum.
  * J.12 Exact SubsetSum (sets of sums), ApproxSubsetSum with Filter (Y[1] <- Z[1]) against brute force: the
         (1 + eps) and (1 - eps) guarantees, the inductive claim with delta = eps/(2n), the size bound, the failing
         middle step of the note's case (2), the constant 4 n ln n / eps.
Then the numbers in the page's examples and figure captions are recomputed and compared with the page text.
Reviewer additions (R32): the double dual, the strip's 2k-1 triangles, the survivor count by the ratio argument, and
the wording of the TSP inapproximability (f computable in polynomial time)."""
import fractions
import itertools
import math
import os
import random
import re
import sys

import numpy as np
from scipy.optimize import linprog

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
PAGE = os.path.join(ROOT, "content", "4-lecture-notes", "j-approximation-algorithms.md")
CONCEPT = os.path.join(ROOT, "content", "concepts", "approximation-algorithms.md")
FIGS = os.path.join(HERE, "..", "figs")
FAIL = []
random.seed(374)
F = fractions.Fraction
EPS = 1e-9


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAIL.append(name)


def H(k):
    return sum(F(1, i) for i in range(1, k + 1))


# =====================================================================================================================
# J.1 Load balancing
def greedy_load_balance(T, m, tie=None):
    """GreedyLoadBalance(T[1..n], m): each job to the machine with the smallest Total (lowest index on ties, or a
    random one among the minima if tie is a Random)."""
    Total = [0] * m
    A = []
    for t in T:
        lo = min(Total)
        cands = [i for i in range(m) if Total[i] == lo]
        mini = cands[0] if tie is None else tie.choice(cands)
        A.append(mini)
        Total[mini] += t
    return A, Total


def sorted_greedy(T, m, tie=None):
    return greedy_load_balance(sorted(T, reverse=True), m, tie)


def opt_makespan(T, m):
    best = sum(T)
    n = len(T)
    # job 0 on machine 0 (symmetry)
    for rest in itertools.product(range(m), repeat=n - 1):
        loads = [0] * m
        loads[0] = T[0]
        for t, i in zip(T[1:], rest):
            loads[i] += t
        best = min(best, max(loads))
    return best


print("== J.1 load balancing")
worst = {"g": 0, "s": 0}
steps_ok = True
cnt = 0
tie = random.Random(1)
for trial in range(1500):
    m = random.choice([2, 2, 3, 3, 4])
    n = random.randint(1, 8 if m < 4 else 7)
    T = [random.choice([random.randint(0, 9), random.randint(1, 30)]) for _ in range(n)]
    if sum(T) == 0:
        continue
    OPT = opt_makespan(T, m)
    for tb in (None, tie):
        A, Tot = greedy_load_balance(T, m, tb)
        g = max(Tot)
        A2, Tot2 = sorted_greedy(T, m, tb)
        s = max(Tot2)
        cnt += 1
        # Theorem J.1, its proof, and the exact ratio 2 - 1/m
        i = max(range(m), key=lambda k: Tot[k])
        j = max(jj for jj in range(n) if A[jj] == i)
        # Total[i] - T[j] was the minimum load when j was assigned, so it is <= every final load and the average
        steps_ok &= T[j] <= OPT and (Tot[i] - T[j]) * m <= sum(T) and max(T) <= OPT and sum(T) <= m * OPT
        steps_ok &= all(Tot[i] - T[j] <= Tot[k] for k in range(m))
        if not (g <= 2 * OPT and m * g <= (2 * m - 1) * OPT and s <= F(3, 2) * OPT and 3 * m * s <= (4 * m - 1) * OPT):
            print("   counterexample", T, m, g, s, OPT)
            steps_ok = False
        worst["g"] = max(worst["g"], F(g, OPT))
        worst["s"] = max(worst["s"], F(s, OPT))
check("Theorem J.1 / J.2 and the exact ratios 2-1/m, 4/3-1/(3m) hold on random instances (both tie rules)", steps_ok,
      f"{cnt} runs; worst greedy ratio {worst['g']} = {float(worst['g']):.3f}, worst sorted {worst['s']} = "
      f"{float(worst['s']):.3f}")
# Theorem J.2's proof: two of the first m+1 sorted jobs share a machine in any schedule, so T[m+1] <= OPT/2
ok = True
for trial in range(400):
    m = random.randint(2, 3)
    n = random.randint(m + 1, 7)
    T = sorted([random.randint(1, 20) for _ in range(n)], reverse=True)
    ok &= 2 * T[m] <= opt_makespan(T, m)
check("J.2 proof: T[m+1] <= OPT/2 for jobs sorted in decreasing order", ok)
# instances attaining the exact ratios (not on the page: Exercise 1(b) asks for the first)
for m in range(2, 7):
    T = [1] * (m * (m - 1)) + [m]
    g = max(greedy_load_balance(T, m)[1])
    opt = m  # lower bound max T = m and total/m = m; achieved by m-1 machines of m ones and one machine {m}
    check(f"greedy attains 2-1/m for m={m}", F(g, opt) == 2 - F(1, m) and sum(T) == m * opt and max(T) == opt)
    T = [x for v in range(2 * m - 1, m, -1) for x in (v, v)] + [m, m, m]
    s = max(sorted_greedy(T, m)[1])
    sched = [[m + i, 2 * m - i] for i in range(1, m)] + [[m, m, m]]
    okS = sorted(x for b in sched for x in b) == sorted(T) and all(sum(b) == 3 * m for b in sched)
    check(f"sorted greedy attains 4/3-1/(3m) for m={m}", okS and sum(T) == 3 * m * m and F(s, 3 * m) == F(4, 3) - F(1, 3 * m),
          f"{s} vs OPT {3 * m}")
    if m <= 3:
        check(f"  brute force confirms both optima for m={m}", opt_makespan([1] * (m * (m - 1)) + [m], m) == m and
              opt_makespan(T, m) == 3 * m)
# Partition: an even split exists iff two machines reach makespan sum/2
ok = True
for trial in range(300):
    T = [random.randint(1, 12) for _ in range(random.randint(1, 8))]
    even = any(2 * sum(c) == sum(T) for r in range(len(T) + 1) for c in itertools.combinations(T, r))
    ok &= even == (2 * opt_makespan(T, 2) == sum(T))
check("Partition <-> two machines with makespan sum/2", ok)


# =====================================================================================================================
# J.3 Greedy vertex cover
def greedy_vc(n, edges, tie=None, trace=False):
    """GreedyVertexCover: repeatedly take a vertex of maximum degree in the remaining graph and delete it."""
    adj = {v: set() for v in range(n)}
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    C, ds, sizes = [], [], []
    m = len(edges)
    while m > 0:
        dmax = max(len(adj[v]) for v in adj)
        cands = [v for v in sorted(adj) if len(adj[v]) == dmax]
        v = cands[0] if tie is None else tie.choice(cands)
        sizes.append(m)
        ds.append(dmax)
        for w in adj[v]:
            adj[w].discard(v)
        m -= len(adj[v])
        del adj[v]
        C.append(v)
    return (C, ds, sizes) if trace else C


def is_vc(edges, C):
    S = set(C)
    return all(u in S or v in S for u, v in edges)


def min_vc(n, edges):
    best = n
    masks = [(1 << u) | (1 << v) for u, v in edges]
    for S in range(1 << n):
        k = bin(S).count("1")
        if k < best and all(S & mk for mk in masks):
            best = k
    return best


def all_graphs(n):
    pairs = list(itertools.combinations(range(n), 2))
    for bits in range(1 << len(pairs)):
        yield [pairs[i] for i in range(len(pairs)) if bits >> i & 1]


def rand_graph(n, p):
    return [(u, v) for u, v in itertools.combinations(range(n), 2) if random.random() < p]


print("== J.3 greedy vertex cover")
worst_vc = F(1)
ok_vc = ok_half = ok_iter = ok_H = True
note_bound_fail = []
graphs = [(n, E) for n in range(2, 7) for E in all_graphs(n)]
graphs += [(n, rand_graph(n, random.choice([0.2, 0.35, 0.5, 0.7]))) for n in range(7, 13) for _ in range(150)]
for n, E in graphs:
    if not E:
        continue
    OPT = min_vc(n, E)
    for tb in (None, tie):
        C, ds, sizes = greedy_vc(n, E, tb, trace=True)
        ok_vc &= is_vc(E, C)
        m = len(E)
        Delta = max(sum(v in e for e in E) for v in range(n))
        ok_H &= len(C) <= H(Delta) * OPT
        # the halving lemma: the first OPT iterations remove at least half of the edges
        ok_half &= 2 * sum(ds[:OPT]) >= m
        ok_iter &= len(C) <= OPT * (int(math.floor(math.log2(m))) + 1)
        if len(C) > OPT * math.log2(m):
            note_bound_fail.append((n, E, len(C), OPT))
        worst_vc = max(worst_vc, F(len(C), OPT))
N_VC_ALL = sum(1 for n, E in graphs if n <= 6)
N_VC_RAND = len(graphs) - N_VC_ALL
check("GreedyVertexCover returns a vertex cover", ok_vc, f"{len(graphs)} graphs (all with <= 6 vertices + random)")
check("halving lemma: sum of d_1..d_OPT >= |E|/2", ok_half)
check("iterations <= OPT (floor(lg m) + 1)", ok_iter)
check("|greedy| <= H(Delta) OPT", ok_H, f"worst ratio seen {worst_vc} = {float(worst_vc):.3f}")
check("the note's bound OPT lg|G| fails exactly on graphs with one edge",
      note_bound_fail and all(len(E) == 1 for n, E, c, o in note_bound_fail), f"{len(note_bound_fail)} failures")
# the note's claim of an Omega(log n) family (Exercise 2(b), not on the page): verify one standard family
for N in (6, 12, 24, 48):
    E = []
    nxt = N
    for i in range(2, N + 1):
        for b in range(N // i):
            for t in range(b * i, b * i + i):
                E.append((t, nxt))
            nxt += 1
    C = greedy_vc(nxt, E)
    import networkx as nx
    G = nx.Graph()
    G.add_nodes_from(range(nxt))
    G.add_edges_from(E)
    opt = len(nx.bipartite.maximum_matching(G, top_nodes=range(N))) // 2  # Konig
    check(f"log-n family N={N}: greedy {len(C)} vs OPT {opt}", len(C) == sum(N // i for i in range(2, N + 1)) and opt == N,
          f"ratio {len(C) / opt:.2f}, vertices {nxt}")


# =====================================================================================================================
# J.4 Set cover and hitting set
def greedy_set_cover(X, Fam):
    X = set(X)
    C = []
    while X:
        S = max(range(len(Fam)), key=lambda s: (len(Fam[s] & X), -s))
        X -= Fam[S]
        C.append(S)
    return C


def greedy_hitting_set(X, Fam):
    Xs = sorted(X)
    Fam = [set(S) for S in Fam]
    Hs = []
    while Fam:
        x = max(Xs, key=lambda x: (sum(x in S for S in Fam), -Xs.index(x)))
        Fam = [S for S in Fam if x not in S]
        Hs.append(x)
    return Hs


def min_set_cover(X, Fam):
    for r in range(len(Fam) + 1):
        for c in itertools.combinations(range(len(Fam)), r):
            if set().union(*[Fam[i] for i in c]) >= set(X):
                return r


def min_hitting_set(X, Fam):
    for r in range(len(X) + 1):
        for c in itertools.combinations(sorted(X), r):
            if all(S & set(c) for S in Fam):
                return r


print("== J.4 set cover and hitting set")
ok_sc = ok_hs = ok_dual = True
w_sc = w_hs = F(1)
for trial in range(1500):
    nx_ = random.randint(1, 8)
    X = set(range(nx_))
    Fam = [set(random.sample(range(nx_), random.randint(1, nx_))) for _ in range(random.randint(1, 7))]
    if set().union(*Fam) != X:
        Fam.append(X - set().union(*Fam))
    C = greedy_set_cover(X, Fam)
    opt = min_set_cover(X, Fam)
    ok_sc &= set().union(*[Fam[i] for i in C]) == X and len(C) <= H(max(len(S) for S in Fam)) * opt
    w_sc = max(w_sc, F(len(C), opt))
    Hs = greedy_hitting_set(X, Fam)
    oh = min_hitting_set(X, Fam)
    maxdeg = max(sum(x in S for S in Fam) for x in X)
    ok_hs &= all(S & set(Hs) for S in Fam) and len(Hs) <= H(maxdeg) * oh
    w_hs = max(w_hs, F(len(Hs), oh))
    # dual system: ground set = indices of Fam, family = x* = {S : x in S}
    Xstar = [frozenset(i for i in range(len(Fam)) if x in Fam[i]) for x in sorted(X)]
    ok_dual &= oh == min_set_cover(set(range(len(Fam))), [set(s) for s in Xstar])
    ok_dual &= min_set_cover(X, Fam) == min_hitting_set(set(range(len(Fam))), [set(s) for s in Xstar])
check("GreedySetCover covers, size <= H(max |S|) OPT", ok_sc, f"worst ratio {w_sc} = {float(w_sc):.3f}")
check("GreedyHittingSet hits, size <= H(max #sets per element) OPT", ok_hs, f"worst ratio {w_hs} = {float(w_hs):.3f}")
check("hitting sets of (X,F) = set covers of the dual (F,X*) and vice versa (optimal sizes)", ok_dual)


# reviewer: the dual of the dual is the original system iff no two elements lie in exactly the same sets
def dual(ground, fam):
    """(ground, fam) -> (fam, {x* : x in ground}) with frozensets."""
    return frozenset(fam), frozenset(frozenset(S for S in fam if x in S) for x in ground)


ok_dd = True
rv = random.Random(3232)  # own stream: keeps the page's run counts unchanged
for trial in range(400):
    nx_ = rv.randint(1, 6)
    Xg = frozenset(range(nx_))
    Fam = frozenset(frozenset(rv.sample(range(nx_), rv.randint(0, nx_))) for _ in range(rv.randint(1, 6)))
    stars = [frozenset(S for S in Fam if x in S) for x in Xg]
    distinct = len(set(stars)) == len(stars)
    G2, F2 = dual(*dual(Xg, Fam))
    # x -> x* is the renaming; the double dual is isomorphic iff that map is injective
    iso = distinct and F2 == frozenset(frozenset(stars[x] for x in S) for S in Fam)
    ok_dd &= (len(G2) == len(Xg)) == distinct and (iso or not distinct)
G2, F2 = dual(*dual(frozenset("ab"), frozenset([frozenset("ab")])))
check("double dual = original up to renaming exactly when the x* are distinct; X = {a,b}, F = {{a,b}}: 1 element",
      ok_dd and len(G2) == 1)


def bad_set_cover(k):
    """Blocks B_1..B_k of sizes 2, 4, ..., 2^k, each split into a top and a bottom half; F = two rows + k columns."""
    X, cols, top, bot, nxt = set(), [], set(), set(), 0
    for i in range(1, k + 1):
        B = list(range(nxt, nxt + 2 ** i))
        nxt += 2 ** i
        cols.append(set(B))
        top |= set(B[: len(B) // 2])
        bot |= set(B[len(B) // 2:])
        X |= set(B)
    return X, [top, bot] + cols


for k in range(2, 13):
    X, Fam = bad_set_cover(k)
    C = greedy_set_cover(X, Fam)
    # strict preference at every step: the column B_j beats the rows by one element
    cover2 = Fam[0] | Fam[1] == X
    check(f"set-cover family k={k}: greedy picks the k columns, OPT = 2, |F| = k+2, |X| = 2^(k+1)-2",
          sorted(C) == list(range(2, k + 2)) and cover2 and len(Fam) == k + 2 and len(X) == 2 ** (k + 1) - 2 and
          k <= 2 * H(2 ** k), f"ratio {k}/2; log2|F| = {math.log2(k + 2):.2f}")
check("so the greedy set-cover ratio is not O(log |F|): ratio/(log2 |F|) grows", 12 / 2 / math.log2(14) > 1.5 > 2 / 2 / math.log2(4))


# =====================================================================================================================
# J.5 DumbVertexCover
def dumb_vc(edges, pick=None):
    E = list(edges)
    C, M = [], []
    while E:
        u, v = E[0] if pick is None else pick.choice(E)
        M.append((u, v))
        C += [u, v]
        E = [e for e in E if u not in e and v not in e]
    return C, M


print("== J.5 vertex cover redux")
ok = True
wd = F(1)
for n, E in graphs[::3]:
    if not E:
        continue
    for pk in (None, tie):
        C, M = dumb_vc(E, pk)
        opt = min_vc(n, E)
        ok &= is_vc(E, C) and len(set(C)) == len(C) == 2 * len(M) <= 2 * opt
        ok &= len({x for e in M for x in e}) == 2 * len(M)  # a matching
        wd = max(wd, F(len(C), opt))
check("DumbVertexCover: a vertex cover, the chosen edges a matching, size <= 2 OPT", ok, f"worst ratio {wd}")
ok = True
for trial in range(800):
    nx_ = random.randint(1, 7)
    X = set(range(nx_))
    Fam = [set(random.sample(range(nx_), random.randint(1, nx_))) for _ in range(random.randint(1, 6))]
    Hs, Fs = set(), [S for S in Fam]
    while Fs:
        S = Fs[0]
        Hs |= S
        Fs = [T for T in Fs if not (T & Hs)]
    ok &= all(S & Hs for S in Fam) and len(Hs) <= max(len(S) for S in Fam) * min_hitting_set(X, Fam)
check("dumb hitting set (take all of any unhit set): ratio <= max |S|", ok)
# weighted path a - b - c with w = 1, 10^100, 1
W = {0: 1, 1: 10 ** 100, 2: 1}
E = [(0, 1), (1, 2)]
g = greedy_vc(3, E)
dms = {tuple(sorted(dumb_vc([e] + [f for f in E if f != e])[0])) for e in E}
check("weighted path: greedy weight 10^100, dumb 10^100+1 (either edge), lightest 2",
      sum(W[v] for v in g) == 10 ** 100 and all(sum(W[v] for v in d) == 10 ** 100 + 1 for d in dms) and
      min(sum(W[v] for v in S) for r in range(4) for S in itertools.combinations(range(3), r) if is_vc(E, S)) == 2)


# =====================================================================================================================
# J.6 LP rounding
def vc_lp(n, edges, w):
    A = np.zeros((len(edges), n))
    for k, (u, v) in enumerate(edges):
        A[k, u] = A[k, v] = -1
    res = linprog(c=w, A_ub=A if edges else None, b_ub=-np.ones(len(edges)) if edges else None,
                  bounds=[(0, 1)] * n, method="highs")
    assert res.status == 0
    return res.x, res.fun


def min_wvc(n, edges, w):
    best = None
    for S in range(1 << n):
        if all(S >> u & 1 or S >> v & 1 for u, v in edges):
            c = sum(w[v] for v in range(n) if S >> v & 1)
            best = c if best is None or c < best else best
    return best


print("== J.6 LP rounding")
ok = True
wr = 0
N_LP = 0
for trial in range(600):
    n = random.randint(2, 10)
    E = rand_graph(n, random.choice([0.3, 0.5, 0.8]))
    if not E:
        continue
    N_LP += 1
    w = [random.randint(1, 10) for _ in range(n)]
    x, lp = vc_lp(n, E, w)
    opt = min_wvc(n, E, w)
    xr = [1 if xv >= 0.5 - 1e-9 else 0 for xv in x]
    rw = sum(w[v] * xr[v] for v in range(n))
    ok &= lp <= opt + EPS and is_vc(E, [v for v in range(n) if xr[v]]) and rw <= 2 * lp + 1e-7 and all(
        xr[v] <= 2 * x[v] + 1e-9 for v in range(n))
    wr = max(wr, rw / opt)
check("LP <= OPT; rounding x* >= 1/2 gives a vertex cover of weight <= 2 LP <= 2 OPT", ok, f"worst rounded/OPT {wr:.3f}")
x, lp = vc_lp(5, [(i, (i + 1) % 5) for i in range(5)], [1] * 5)
check("C5: LP optimum 5/2 (all 1/2), rounding takes all 5 vertices, OPT 3",
      abs(lp - 2.5) < 1e-9 and all(abs(v - 0.5) < 1e-9 for v in x) and min_vc(5, [(i, (i + 1) % 5) for i in range(5)]) == 3)
ok = True
for n in range(3, 8):
    E = list(itertools.combinations(range(n), 2))
    x, lp = vc_lp(n, E, [1] * n)
    ok &= abs(lp - n / 2) < 1e-9 and min_vc(n, E) == n - 1
check("K_n: LP n/2, OPT n-1 (OPT/LP -> 2)", ok)


# =====================================================================================================================
# J.7 Randomized rounding
print("== J.7 randomized LP rounding")
# (1-a)(1-b) on a+b >= 1, 0 <= a,b <= 1: maximum 1/4 at a = b = 1/2, minimum 0
grid = [F(i, 40) for i in range(41)]
vals = [((1 - a) * (1 - b), a, b) for a in grid for b in grid if a + b >= 1]
check("Pr[edge uncovered] = (1-a)(1-b) <= 1/4, maximized (not minimized) at a = b = 1/2; its minimum is 0",
      max(vals)[0] == F(1, 4) and [(a, b) for v, a, b in vals if v == F(1, 4)] == [(F(1, 2), F(1, 2))] and min(vals)[0] == 0)


def exact_round(xs, w, edges, N=1):
    """Exact distribution of independent rounding, Pr[v in C] = 1-(1-x)^N: E[w(C)], E[#covered], Pr[cover]."""
    n = len(xs)
    p = [1 - (1 - xv) ** N for xv in xs]
    Ew = Ecov = Pcov = F(0)
    for S in range(1 << n):
        pr = F(1)
        for v in range(n):
            pr *= p[v] if S >> v & 1 else 1 - p[v]
        Ew += pr * sum(w[v] for v in range(n) if S >> v & 1)
        cov = sum(1 for u, v in edges if S >> u & 1 or S >> v & 1)
        Ecov += pr * cov
        if cov == len(edges):
            Pcov += pr
    return Ew, Ecov, Pcov


C5 = [(i, (i + 1) % 5) for i in range(5)]
Ew, Ecov, _ = exact_round([F(1, 2)] * 5, [1] * 5, C5)
check("C5, one round: E[w] = LP = 5/2, E[#covered edges] = 15/4 = 3/4 of 5", Ew == F(5, 2) and Ecov == F(15, 4))
ok = True
for trial in range(200):
    n = random.randint(2, 7)
    E = rand_graph(n, 0.5)
    if not E:
        continue
    w = [random.randint(1, 9) for _ in range(n)]
    x, lp = vc_lp(n, E, w)
    xs = [F(round(v * 2), 2) if abs(v * 2 - round(v * 2)) < 1e-9 else F(v).limit_denominator(1000) for v in x]
    Ew, Ecov, _ = exact_round(xs, w, E)
    ok &= Ew == sum(w[v] * xs[v] for v in range(n)) and 4 * Ecov >= 3 * len(E)
check("one round: E[w(x')] = LP exactly; at least 3/4 of the edges covered in expectation", ok)
Ew2, _, _ = exact_round([F(1, 2)] * 5, [1] * 5, C5, N=2)
check("N rounds: Pr[v in C] = 1-(1-x)^N <= N x, so E[w(C)] <= N LP, not = (C5, N=2: 15/4 < 5)",
      Ew2 == F(15, 4) and all(1 - (1 - a) ** N <= N * a for a in grid for N in range(1, 8)))
ok = True
for n in (4, 8, 16):
    N = 2 * int(math.log2(n))
    ok &= F(1, 4) ** N == F(1, n ** 4)
check("4^(-N) = n^(-4) for N = 2 lg n", ok)
for n in (4, 8):
    N = 2 * int(math.log2(n))
    E = list(itertools.combinations(range(n), 2))
    _, _, Pc = exact_round([F(1, 2)] * n, [1] * n, E, N=N)
    check(f"K_{n}, x* = 1/2, N = {N}: Pr[C is a vertex cover] >= 1 - 1/n^2", Pc >= 1 - F(1, n * n),
          f"{float(Pc):.8f}")


# =====================================================================================================================
# J.8 TSP: the bad news
def held_karp(D):
    n = len(D)
    if n <= 3:
        return sum(D[i][(i + 1) % n] for i in range(n)) if n > 1 else 0
    dp = {(1 << 0 | 1 << j, j): D[0][j] for j in range(1, n)}
    for size in range(3, n + 1):
        for sub in itertools.combinations(range(1, n), size - 1):
            S = 1 | sum(1 << j for j in sub)
            for j in sub:
                Sj = S & ~(1 << j)
                dp[(S, j)] = min(dp[(Sj, k)] + D[k][j] for k in sub if k != j)
    full = (1 << n) - 1
    return min(dp[(full, j)] + D[j][0] for j in range(1, n))


def brute_tsp(D):
    n = len(D)
    return min(sum(D[t[i]][t[(i + 1) % n]] for i in range(n)) for t in
               ((0,) + p for p in itertools.permutations(range(1, n))))


def hamiltonian(n, E):
    S = {frozenset(e) for e in E}
    return any(all(frozenset((t[i], t[(i + 1) % n])) in S for i in range(n)) for t in
               ((0,) + p for p in itertools.permutations(range(1, n))))


def is_metric(D):
    n = len(D)
    return all(D[i][j] <= D[i][k] + D[k][j] + 1e-9 for i in range(n) for j in range(n) for k in range(n))


print("== J.8 traveling salesman: the bad news")
ok12 = okn1 = okal = True
cases = [(n, E) for n in range(3, 6) for E in all_graphs(n)] + [(n, rand_graph(n, 0.55)) for n in (6, 7) for _ in range(80)]
for n, E in cases:
    S = {frozenset(e) for e in E}
    ham = hamiltonian(n, E)
    for absent, test in ((2, "12"), (n + 1, "n1"), ("a", "al")):
        alpha = 3
        a = alpha * n + 1 if absent == "a" else absent
        D = [[0 if i == j else (1 if frozenset((i, j)) in S else a) for j in range(n)] for i in range(n)]
        opt = held_karp(D)
        if test == "12":
            ok12 &= (opt == n) == ham and (ham or opt >= n + 1)
        elif test == "n1":
            okn1 &= (opt == n) == ham and (ham or opt >= 2 * n)
        else:
            okal &= (opt == n) == ham and (ham or opt > alpha * n)
check("lengths 1/2: tour of length n iff Hamiltonian, otherwise >= n+1 (and 1/2 lengths are metric)",
      ok12 and all(is_metric([[0 if i == j else (1 if frozenset((i, j)) in {frozenset(e) for e in E} else 2)
                                for j in range(n)] for i in range(n)]) for n, E in cases[:200]), f"{len(cases)} graphs")
N_TSP_ALL = sum(1 for n, E in cases if n <= 5)
N_TSP_RAND = len(cases) - N_TSP_ALL
check("lengths 1/(n+1): n if Hamiltonian, otherwise >= 2n", okn1)
check("lengths 1/(alpha n + 1), alpha = 3: n if Hamiltonian, otherwise > alpha n", okal)
ok = True
for n, E in cases:
    S = {frozenset(e) for e in E}
    for a in (n + 2, 2 * n):
        D = [[0 if i == j else (1 if frozenset((i, j)) in S else a) for j in range(n)] for i in range(n)]
        ok &= hamiltonian(n, E) or held_karp(D) > 2 * n
check("lengths 1/(n+2) and 1/(2n): non-Hamiltonian optimum > 2n", ok)
# factor exactly 2 does not separate: C5 plus a chord is Hamiltonian and has a tour of length exactly 2n = 10;
# the path P5 is not Hamiltonian and its optimum is exactly 2n
E = [(i, (i + 1) % 5) for i in range(5)] + [(0, 2)]
S = {frozenset(e) for e in E}
D = [[0 if i == j else (1 if frozenset((i, j)) in S else 6) for j in range(5)] for i in range(5)]
tour = [1, 0, 2, 3, 4]
L = sum(D[tour[i]][tour[(i + 1) % 5]] for i in range(5))
P5 = [(i, i + 1) for i in range(4)]
SP = {frozenset(e) for e in P5}
DP = [[0 if i == j else (1 if frozenset((i, j)) in SP else 6) for j in range(5)] for i in range(5)]
check("factor 2 is not enough: C5+chord has a tour of length 10 = 2n (allowed for a 2-approximation), P5 has OPT 10",
      hamiltonian(5, E) and L == 10 and not hamiltonian(5, P5) and held_karp(DP) == 10)


# =====================================================================================================================
# J.9 Metric TSP
def prim(D, order_root=0):
    n = len(D)
    inT, E = {order_root}, []
    while len(inT) < n:
        w, u, v = min((D[u][v], u, v) for u in inT for v in range(n) if v not in inT)
        inT.add(v)
        E.append((u, v))
    return E


def dfs_preorder(n, E, root=0, child_order=None):
    adj = {v: [] for v in range(n)}
    for u, v in E:
        adj[u].append(v)
        adj[v].append(u)
    order, walk, seen = [], [], set()

    def go(v):
        seen.add(v)
        order.append(v)
        walk.append(v)
        nb = sorted(adj[v]) if child_order is None else sorted(adj[v], key=child_order)
        for w in nb:
            if w not in seen:
                go(w)
                walk.append(v)
    go(root)
    return order, walk


def tour_len(D, t):
    return sum(D[t[i]][t[(i + 1) % len(t)]] for i in range(len(t)))


def min_matching(D, vs):
    if not vs:
        return 0, []
    a, best = vs[0], None
    for i in range(1, len(vs)):
        c, m = min_matching(D, vs[1:i] + vs[i + 1:])
        c += D[a][vs[i]]
        if best is None or c < best[0]:
            best = (c, [(a, vs[i])] + m)
    return best


def euler_circuit(n, edges, start=0):
    adj = {v: [] for v in range(n)}
    for k, (u, v) in enumerate(edges):
        adj[u].append((v, k))
        adj[v].append((u, k))
    used = [False] * len(edges)
    stack, circ = [start], []
    while stack:
        v = stack[-1]
        while adj[v] and used[adj[v][-1][1]]:
            adj[v].pop()
        if adj[v]:
            w, k = adj[v].pop()
            used[k] = True
            stack.append(w)
        else:
            circ.append(stack.pop())
    return circ[::-1]


def shortcut(walk):
    seen, t = set(), []
    for v in walk:
        if v not in seen:
            seen.add(v)
            t.append(v)
    return t


def christofides(D, root=0):
    n = len(D)
    T = prim(D)
    deg = [0] * n
    for u, v in T:
        deg[u] += 1
        deg[v] += 1
    odd = [v for v in range(n) if deg[v] % 2]
    mom, M = min_matching(D, odd)
    circ = euler_circuit(n, T + M, root)
    return T, odd, mom, M, circ, shortcut(circ)


def metric_closure(W):
    n = len(W)
    D = [row[:] for row in W]
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if D[i][k] + D[k][j] < D[i][j]:
                    D[i][j] = D[i][k] + D[k][j]
    return D


print("== J.9 traveling salesman: the good news")
ok2 = ok15 = okpf = True
w2 = w15 = 0
inst = 0
for trial in range(700):
    n = random.randint(3, 8)
    if trial % 2:
        P = [(random.random(), random.random()) for _ in range(n)]
        D = [[math.dist(p, q) for q in P] for p in P]
    else:
        W = [[0] * n for _ in range(n)]
        for i, j in itertools.combinations(range(n), 2):
            W[i][j] = W[j][i] = random.randint(1, 20)
        D = metric_closure(W)
    assert is_metric(D)
    inst += 1
    opt = held_karp(D) if n > 7 else brute_tsp(D)
    T = prim(D)
    mst = sum(D[u][v] for u, v in T)
    order, walk = dfs_preorder(n, T, root=random.randrange(n))
    A = tour_len(D, order)
    wl = sum(D[walk[i]][walk[i + 1]] for i in range(len(walk) - 1))
    ok2 &= abs(wl - 2 * mst) < 1e-9 and A <= 2 * mst + 1e-9 and mst <= opt + 1e-9 and A <= 2 * opt + 1e-9
    w2 = max(w2, A / opt)
    T, odd, mom, M, circ, tour = christofides(D)
    deg = [0] * n
    for u, v in T + M:
        deg[u] += 1
        deg[v] += 1
    A = tour_len(D, tour)
    odd_opt = brute_tsp([[D[a][b] for b in odd] for a in odd]) if len(odd) > 2 else (2 * D[odd[0]][odd[1]] if odd else 0)
    okpf &= len(odd) % 2 == 0 and all(d % 2 == 0 for d in deg) and len(circ) == len(T) + len(M) + 1
    okpf &= sorted(tour) == list(range(n)) and odd_opt <= opt + 1e-9 and 2 * mom <= odd_opt + 1e-9
    ok15 &= A <= mst + mom + 1e-9 and 2 * mom <= opt + 1e-9 and 2 * A <= 3 * opt + 1e-9
    w15 = max(w15, A / opt)
check("tree doubling: walk = 2 MST, tour <= 2 MST, MST <= OPT, tour <= 2 OPT", ok2,
      f"{inst} metric instances (Euclidean and graph metrics), worst ratio {w2:.3f}")
check("Christofides: |O| even, T+M even degrees, Euler circuit uses every edge; odd-vertex tour <= OPT, MOM <= half of it",
      okpf)
check("Christofides: tour <= MST + MOM, MOM <= OPT/2, tour <= 3/2 OPT", ok15, f"worst ratio {w15:.3f}")
# MST <= OPT can be strict and is the right direction (the note prints MST >= OPT)
Dsq = [[math.dist(p, q) for q in [(0, 0), (1, 0), (1, 1), (0, 1)]] for p in [(0, 0), (1, 0), (1, 1), (0, 1)]]
check("unit square: MST 3 < OPT 4 (so 'MST >= OPT' is false in general)",
      abs(sum(Dsq[u][v] for u, v in prim(Dsq)) - 3) < 1e-9 and abs(brute_tsp(Dsq) - 4) < 1e-9)
# without the triangle inequality tree doubling can exceed 2 OPT
# wheel: center 0, rim cycle 1-2-3-4, the two rim diagonals have length 100
Dn = [[0 if i == j else (100 if {i, j} in ({1, 3}, {2, 4}) else 1) for j in range(5)] for i in range(5)]
Tn = prim(Dn)
on, _ = dfs_preorder(5, Tn, root=0, child_order=lambda v: [0, 1, 3, 2, 4].index(v))
check("non-metric instance: tree doubling tour > 2 OPT", not is_metric(Dn) and tour_len(Dn, on) > 2 * brute_tsp(Dn),
      f"MST {sorted(Tn)}, tour {on} of length {tour_len(Dn, on)} vs OPT {brute_tsp(Dn)}")

# the figure instance (the note's tree shape, integer coordinates); page names a..g = preorder from the center
NAMES = ["c", "L", "R", "B", "UR", "T", "TL"]
LAB = {"c": "a", "L": "b", "R": "c", "B": "d", "UR": "e", "T": "f", "TL": "g"}
PTS = {"TL": (0, 0), "T": (3, 0), "c": (5, 3), "L": (1, 8), "B": (8, 10), "UR": (11, 4), "R": (8, 4)}
idx = {v: i for i, v in enumerate(NAMES)}
Df = [[math.dist(PTS[a], PTS[b]) for b in NAMES] for a in NAMES]
Tf = prim(Df)
TREE = {frozenset(e) for e in [("TL", "T"), ("T", "c"), ("c", "L"), ("c", "R"), ("R", "UR"), ("R", "B")]}
check("figure: the MST is the note's tree", {frozenset((NAMES[u], NAMES[v])) for u, v in Tf} == TREE)
adjT = {v: [] for v in NAMES}
for e in TREE:
    a, b = tuple(e)
    adjT[a].append(b)
    adjT[b].append(a)


def tpath(a, b, prev=None):
    if a == b:
        return [a]
    for x in adjT[a]:
        if x != prev:
            p = tpath(x, b, a)
            if p:
                return [a] + p


# uniqueness: every non-tree pair is longer than every tree edge on its tree path
marg = min(math.dist(PTS[a], PTS[b]) - max(math.dist(PTS[p[i]], PTS[p[i + 1]]) for i in range(len(p) - 1))
           for a, b in itertools.combinations(NAMES, 2) if frozenset((a, b)) not in TREE for p in [tpath(a, b)])
check("figure: the MST is unique (margin > 0)", marg > 0.4, f"margin {marg:.3f}")
mstf = sum(Df[u][v] for u, v in Tf)
ordf, walkf = dfs_preorder(7, Tf, root=idx["c"], child_order=lambda v: LAB[NAMES[v]])
WORD = lambda seq: " ".join(LAB[NAMES[v]] if isinstance(v, int) else LAB[v] for v in seq)
check("figure: DFS from a with alphabetical children: walk a b a c d c e c a f g f a, preorder a..g",
      WORD(walkf) == "a b a c d c e c a f g f a" and WORD(ordf) == "a b c d e f g")
dt = tour_len(Df, ordf)
optf = brute_tsp(Df)
deg = {v: sum(v in e for e in TREE) for v in NAMES}
oddf = [v for v in NAMES if deg[v] % 2]
momf, Mf = min_matching(Df, [idx[v] for v in oddf])
Mnames = {frozenset((NAMES[a], NAMES[b])) for a, b in Mf}
allm = []


def all_matchings(vs):
    if not vs:
        yield []
        return
    for i in range(1, len(vs)):
        for m in all_matchings(vs[1:i] + vs[i + 1:]):
            yield [(vs[0], vs[i])] + m


costs = sorted(sum(Df[a][b] for a, b in m) for m in all_matchings([idx[v] for v in oddf]))
check("figure: odd vertices a b c d e g; the minimum matching ag, bd, ce is unique",
      sorted(LAB[v] for v in oddf) == list("abcdeg") and costs[1] - costs[0] > 0.1 and
      {"".join(sorted(LAB[x] for x in e)) for e in Mnames} == {"ag", "bd", "ce"})
circ = ["c", "L", "B", "R", "UR", "R", "c", "TL", "T", "c"]
Eall = [tuple(sorted(e)) for e in TREE] + [tuple(sorted(e)) for e in Mnames]
steps = [tuple(sorted((circ[i], circ[i + 1]))) for i in range(len(circ) - 1)]
check("figure: a b d c e c a g f a is an Euler circuit of T + M", sorted(steps) == sorted(Eall) and WORD(circ) == "a b d c e c a g f a")
cht = shortcut(circ)
chl = tour_len(Df, [idx[v] for v in cht])
n_short_dt = sum(1 for i in range(7) if frozenset((NAMES[ordf[i]], NAMES[ordf[(i + 1) % 7]])) not in TREE)
n_short_ch = sum(1 for i in range(7) if frozenset((cht[i], cht[(i + 1) % 7])) not in TREE | Mnames)
check("figure: Christofides tour a b d c e g f, 4 shortcuts for tree doubling and 1 for Christofides",
      WORD(cht) == "a b d c e g f" and n_short_dt == 4 and n_short_ch == 1)
FIGNUM = {"mst": mstf, "dt": dt, "ch": chl, "opt": optf, "mom": momf}
print("   figure numbers:", {k: round(v, 3) for k, v in FIGNUM.items()})
check("figure: tour lengths obey the bounds", dt <= 2 * mstf and chl <= mstf + momf and mstf <= optf and 2 * momf <= optf)

# tight families
# (a) Christofides: a strip of triangles; zigzag edges 1, row edges 1+e, metric = shortest paths
for k in range(2, 6):
    e = F(1, 100)
    nv = 2 * k + 1  # bottom b0..bk (k+1), top t0..t_{k-1} (k)
    bot = list(range(k + 1))
    top = list(range(k + 1, 2 * k + 1))
    W = [[10 ** 6] * nv for _ in range(nv)]
    for i in range(nv):
        W[i][i] = 0
    for i in range(k):
        for a, b in ((bot[i], top[i]), (top[i], bot[i + 1])):
            W[a][b] = W[b][a] = 1
    for i in range(k):
        W[bot[i]][bot[i + 1]] = W[bot[i + 1]][bot[i]] = 1 + e
    for i in range(k - 1):
        W[top[i]][top[i + 1]] = W[top[i + 1]][top[i]] = 1 + e
    D = metric_closure(W)
    T, odd, mom, M, circ, tour = christofides(D, root=0)
    A = tour_len(D, tour)
    opt = held_karp(D)
    check(f"Christofides tight strip k={k}: MST = zigzag 2k, tour = 2k + k(1+e), OPT = 2 + (2k-1)(1+e)",
          sum(D[u][v] for u, v in T) == 2 * k and A == 2 * k + k * (1 + e) and opt == 2 + (2 * k - 1) * (1 + e),
          f"ratio {float(A / opt):.3f}")
    # reviewer: the strip has 2k-1 triangles (k on bottom edges, k-1 on top edges), not 2k
    unit = {frozenset((a, b)) for a in range(nv) for b in range(nv) if a < b and W[a][b] < 10 ** 6}
    tris = [c for c in itertools.combinations(range(nv), 3)
            if all(frozenset(p) in unit for p in itertools.combinations(c, 2))]
    check(f"  strip k={k} has 2k-1 = {2 * k - 1} triangles (E - V + 1 = {len(unit) - nv + 1})",
          len(tris) == 2 * k - 1 == len(unit) - nv + 1)
# (b) tree doubling: cycle metric, MST = path, DFS from the middle vertex
for n in (6, 10, 20, 40):
    D = [[min(abs(i - j), n - abs(i - j)) for j in range(n)] for i in range(n)]
    D[0][n - 1] = D[n - 1][0] = 1  # unchanged; MST from Prim below is a path
    T = [(i, i + 1) for i in range(n - 1)]
    o, _ = dfs_preorder(n, T, root=n // 2, child_order=lambda v: -v)
    A = tour_len(D, o)
    check(f"tree doubling on the {n}-cycle metric (MST = path, DFS from the middle): tour 2n-2 vs OPT n",
          A == 2 * n - 2 and sum(D[u][v] for u, v in T) == n - 1 and is_metric(D) and
          (n > 10 or held_karp(D) == n) and sum(D[u][v] for u, v in prim(D)) == n - 1)


# =====================================================================================================================
# J.10 k-center: Gonzalez
def mec(pts):
    """Radius and center of the minimum enclosing circle (brute force over pairs and triples)."""
    if len(pts) == 1:
        return 0.0, pts[0]
    best = None
    cands = []
    for a, b in itertools.combinations(pts, 2):
        cands.append(((a[0] + b[0]) / 2, (a[1] + b[1]) / 2))
    for a, b, c in itertools.combinations(pts, 3):
        d = 2 * (a[0] * (b[1] - c[1]) + b[0] * (c[1] - a[1]) + c[0] * (a[1] - b[1]))
        if abs(d) < 1e-12:
            continue
        ux = ((a[0] ** 2 + a[1] ** 2) * (b[1] - c[1]) + (b[0] ** 2 + b[1] ** 2) * (c[1] - a[1]) + (c[0] ** 2 + c[1] ** 2) * (a[1] - b[1])) / d
        uy = ((a[0] ** 2 + a[1] ** 2) * (c[0] - b[0]) + (b[0] ** 2 + b[1] ** 2) * (a[0] - c[0]) + (c[0] ** 2 + c[1] ** 2) * (b[0] - a[0])) / d
        cands.append((ux, uy))
    for c in cands:
        r = max(math.dist(c, p) for p in pts)
        if best is None or r < best[0] - 1e-12:
            best = (r, c)
    return best


def kcenter_opt(P, k):
    """Exact continuous k-center cost: min over partitions into <= k clusters of the largest enclosing radius."""
    n = len(P)
    rad = {}
    for S in range(1, 1 << n):
        rad[S] = mec([P[i] for i in range(n) if S >> i & 1])
    full = (1 << n) - 1
    from functools import lru_cache

    @lru_cache(None)
    def f(S, j):
        if S == 0:
            return (0.0, ())
        if j == 0:
            return (float("inf"), ())
        low = S & -S
        best = (float("inf"), ())
        sub = S
        while sub:
            if sub & low:
                r, c = rad[sub]
                rest = f(S & ~sub, j - 1)
                v = max(r, rest[0])
                if v < best[0]:
                    best = (v, (c,) + rest[1])
            sub = (sub - 1) & S
        return best
    return f(full, k)


def gonzalez(P, k):
    """GonzalezKCenter(P, k), exactly as in the note: returns centers c_1..c_{k+1} (when defined) and r_1..r_k."""
    n = len(P)
    d = [float("inf")] * n
    c = [P[0]]
    r = []
    for j in range(k):
        rj = 0
        nxt = None
        for i in range(n):
            d[i] = min(d[i], math.dist(P[i], c[j]))
            if rj < d[i]:
                rj = d[i]
                nxt = P[i]
        r.append(rj)
        if nxt is None:
            break
        c.append(nxt)
    return c, r


print("== J.10 k-center clustering")
ok = okmono = oksep = True
wk = 0
for trial in range(250):
    n = random.randint(2, 9)
    k = random.randint(1, 3)
    P = [(random.randint(0, 40) / 4, random.randint(0, 40) / 4) for _ in range(n)]
    if len(set(P)) < n:
        continue
    c, r = gonzalez(P, k)
    opt = kcenter_opt(P, k)[0]
    rk = r[-1]
    cost = max(min(math.dist(p, q) for q in c[:k]) for p in P)
    ok &= abs(cost - rk) < 1e-9 and rk <= 2 * opt + 1e-9 and opt <= rk + 1e-9
    okmono &= all(r[i] >= r[i + 1] for i in range(len(r) - 1))
    if len(c) == k + 1:
        oksep &= all(math.dist(c[i], c[j]) >= rk - 1e-9 for i, j in itertools.combinations(range(k + 1), 2))
    if opt > 0:
        wk = max(wk, rk / opt)
check("Gonzalez: cost = r_k, r* <= r_k <= 2 r*", ok, f"worst r_k/r* {wk:.3f}")
check("Gonzalez: r_1 >= r_2 >= ... >= r_k", okmono)
check("Gonzalez: the k+1 centers are pairwise >= r_k apart", oksep)
c, r = gonzalez([(-1, 0), (0, 0), (1, 0)], 1)
check("tight: points -1, 0, 1 with p_1 = -1, k = 1: r_1 = 2, OPT = 1", r == [2] and abs(kcenter_opt([(-1, 0), (0, 0), (1, 0)], 1)[0] - 1) < 1e-12)

# J.11 the grid scheme
print("== J.11 approximation schemes")
ok = True
for trial in range(40):
    n = random.randint(6, 13)
    k = random.choice([1, 2])
    eps = random.choice([1.0, 0.5])
    P = [(random.uniform(0, 10), random.uniform(0, 10)) for _ in range(n)]
    c, r = gonzalez(P, k)
    rr = r[-1]
    delta = eps * rr / (2 * math.sqrt(2))
    cells = {}
    for p in P:
        cells.setdefault((math.floor(p[0] / delta), math.floor(p[1] / delta)), p)
    Q = list(cells.values())
    if len(Q) > 13:
        continue
    rq, centers = kcenter_opt(Q, k)
    rstar = kcenter_opt(P, k)[0]
    cost = max(min(math.dist(p, q) for q in centers) for p in P)
    ok &= rq <= rstar + 1e-9 and cost <= rq + delta * math.sqrt(2) + 1e-9 and cost <= (1 + eps) * rstar + 1e-9
    ok &= abs(delta * math.sqrt(2) - eps * rr / 2) < 1e-12 and rstar <= rr + 1e-9 <= 2 * rstar + 2e-9
    ok &= len(Q) <= k * (math.ceil(2 * rstar / delta) + 1) ** 2
check("grid scheme: r~ <= r*, cost <= r~ + delta sqrt2 <= (1+eps) r*; |Q| <= k (ceil(2r*/delta)+1)^2", ok)


# =====================================================================================================================
# J.12 Subset sum
def subset_sum_exact(X, t):
    S = {0}
    sizes = []
    for x in X:
        S = {s for s in S | {s + x for s in S} if s <= t}
        sizes.append(len(S))
    return max(S), sizes


def filt(Z, delta):
    """Filter(Z[1..k], delta) with the first line fixed: Y[1] <- Z[1]."""
    Z = sorted(Z)
    Y = [Z[0]]
    for z in Z[1:]:
        if z > (1 + delta) * Y[-1]:
            Y.append(z)
    return Y


def approx_subset_sum(X, t, eps, trace=False):
    X = sorted(X)
    n = len(X)
    R = [0]
    hist = [R]
    for x in X:
        R = sorted(set(R) | {r + x for r in R})
        R = filt(R, fractions.Fraction(eps) / (2 * n))
        R = [r for r in R if r <= t]
        hist.append(R)
    return (max(R), hist, X) if trace else max(R)


print("== J.12 an FPTAS for subset sum")
okx = oka = okc = oksz = True
wss = 1.0
for trial in range(1200):
    n = random.randint(1, 10)
    X = [random.choice([random.randint(1, 50), random.randint(1, 10 ** 6)]) for _ in range(n)]
    t = random.randint(1, sum(X))
    best = max(sum(c) for r in range(n + 1) for c in itertools.combinations(X, r) if sum(c) <= t)
    ex, sizes = subset_sum_exact(X, t)
    okx &= ex == best and all(sz <= min(2 ** (i + 1), t + 1) for i, sz in enumerate(sizes))
    eps = random.choice([F(1), F(1, 2), F(1, 5), F(1, 20)])
    r, hist, Xs = approx_subset_sum(X, t, eps, trace=True)
    oka &= r <= best and best <= (1 + eps) * r and r >= (1 - eps) * best
    if best:
        wss = min(wss, r / best)
    # the inductive claim, with delta = eps/(2n)
    delta = eps / (2 * n)
    S = {0}
    for i, x in enumerate(Xs, 1):
        S = {s for s in S | {s + x for s in S} if s <= t}
        okc &= all(any(rr <= s <= rr * (1 + delta) ** i for rr in hist[i]) for s in S)
        # size: |R_i| <= |R_{i-1}| + floor(log_{1+delta} i) + 1
        oksz &= len(hist[i]) <= len(hist[i - 1]) + math.floor(math.log(i) / math.log(1 + delta) + 1e-12) + 1
check("exact SubsetSum (sets of sums) = brute force; |S_i| <= min(2^i, t+1)", okx)
check("ApproxSubsetSum: r* <= s* <= (1+eps) r*, so r* >= (1-eps) s*", oka, f"worst r*/s* {float(wss):.4f}")
check("inductive claim with delta = eps/(2n): every s in S_i has r in R_i with r <= s <= r (1+delta)^i", okc)
check("|R_i| <= |R_{i-1}| + floor(log_{1+delta} i) + 1", oksz)
check("the note's ceil(log_{1+delta} i) undercounts at i = 1 (R_1 = {0, x_1})",
      len(approx_subset_sum([5], 10, 1, trace=True)[1][1]) == 2 and math.ceil(math.log(1) / math.log(1.5)) == 0)
# reviewer: survivors of R_{i-1} + x_i, the ratio argument of the page's proof, and why one-per-interval is not enough
ok_ratio = ok_ceil = True
rv = random.Random(3233)  # own stream: keeps the page's run counts unchanged
for trial in range(1500):
    n = rv.randint(1, 9)
    X = [rv.randint(1, 60) for _ in range(n)]
    t = rv.randint(1, sum(X))
    eps = rv.choice([F(1), F(1, 2), F(1, 3)])
    delta = eps / (2 * n)
    _, hist, Xs = approx_subset_sum(X, t, eps, trace=True)
    for i, x in enumerate(Xs, 1):
        surv = sorted(r for r in hist[i] if r - x in hist[i - 1])
        L = math.log(i) / math.log(1 + delta)
        if len(surv) >= 2:
            ok_ratio &= F(surv[-1], surv[0]) > (1 + delta) ** (len(surv) - 1) and surv[-1] <= i * x and surv[0] >= x
        ok_ratio &= len(surv) <= math.floor(L + 1e-12) + 1
        if i >= 2:
            ok_ceil &= len(surv) <= math.ceil(L - 1e-12)
check("survivors p of R_{i-1}+x_i: largest/smallest > (1+delta)^(p-1), both in [x_i, i x_i], so p <= floor(L)+1", ok_ratio)
check("the note's ceil(log_{1+delta} i) is a valid count for i >= 2 (wrong only at i = 1)", ok_ceil)
ks = {math.floor(math.log(v, 2) + 1e-12) for v in range(3, 3 * 3 + 1)}
check("one survivor per interval alone allows floor(L)+2: delta = 1, i = 3, x_i = 3, [3, 9] meets 3 intervals",
      len(ks) == 3 == math.floor(math.log(3, 2)) + 2)
# middle step of case (2): r' + x <= r(1+delta) does not give r'(1+delta)^(i-1) <= (r - x)(1+delta)^i
delta, i, x, r = F(1, 10), 2, F(5), F(20)
rp = r * (1 + delta) - x
check("note's case (2) middle step fails (delta=1/10, i=2, x=5, r=20, r'=17); the corrected chain holds",
      rp * (1 + delta) ** (i - 1) + x > (r - x) * (1 + delta) ** i + x and
      rp * (1 + delta) ** (i - 1) + x <= r * (1 + delta) ** i)
check("(1+eps/2n)^n <= e^(eps/2) <= 1+eps for 0 < eps <= 1",
      all(n * math.log1p(e / (2 * n)) <= e / 2 + 1e-15 and math.expm1(e / 2) <= e
          for e in np.linspace(1e-6, 1, 200) for n in range(1, 60)))
check("ln(1+delta) >= delta/2 on [0,1], so log_{1+delta} n <= 2 ln n/delta = 4 n ln n/eps (not n ln n/eps)",
      all(math.log(1 + d) >= d / 2 for d in np.linspace(1e-9, 1, 500)) and
      abs(2 * math.log(50) / (0.3 / 100) - 4 * 50 * math.log(50) / 0.3) < 1e-6)


# =====================================================================================================================
print("== more evidence for the corrections, and the figures")
# set-cover LP integrality gap with m sets: elements = (m/2+1)-subsets of [m], element A lies in the sets i in A
for m in (6, 8, 10):
    elems = list(itertools.combinations(range(m), m // 2 + 1))
    A = np.zeros((len(elems), m))
    for r_, Aset in enumerate(elems):
        for i in Aset:
            A[r_, i] = -1
    res = linprog(c=np.ones(m), A_ub=A, b_ub=-np.ones(len(elems)), bounds=[(0, 1)] * m, method="highs")
    opt = min(r_ for r_ in range(m + 1) for I in itertools.combinations(range(m), r_)
              if all(set(I) & set(Aset) for Aset in elems))
    check(f"set-cover LP gap, m = {m} sets: LP = m/(m/2+1), OPT = m/2, gap (m+2)/4",
          abs(res.fun - m / (m / 2 + 1)) < 1e-9 and opt == m // 2 and abs(opt / res.fun - (m + 2) / 4) < 1e-9)

# load-balancing figure
A1, T1 = greedy_load_balance([2, 3, 4, 1, 1, 6, 1], 3)
A2, T2 = sorted_greedy([2, 3, 4, 1, 1, 6, 1], 3)
check("load-balance figure: greedy makespan 9 on M2, last job 6 over load 3; sorted 6 = OPT = 18/3",
      max(T1) == 9 and T1.index(9) == 1 and A1[5] == 1 and max(j for j in range(7) if A1[j] == 1) == 5 and
      max(T2) == 6 and opt_makespan([2, 3, 4, 1, 1, 6, 1], 3) == 6 and A1 == [0, 1, 2, 0, 0, 1, 0])

# set-cover figure (k = 4)
X4, F4 = bad_set_cover(4)
Xr = set(X4)
newc = []
for s_ in greedy_set_cover(X4, F4):
    rows_best = max(len(F4[0] & Xr), len(F4[1] & Xr))
    newc.append((s_ - 1, len(F4[s_] & Xr), rows_best))
    Xr -= F4[s_]
check("set-cover figure: greedy C4 C3 C2 C1 with 16 8 4 2 new elements, rows 15 7 3 1; 30 elements, 6 sets, OPT 2",
      newc == [(4, 16, 15), (3, 8, 7), (2, 4, 3), (1, 2, 1)] and len(X4) == 30 and len(F4) == 6 and
      (F4[0] | F4[1]) == X4 and all(F4[i] != X4 for i in range(6)))

# k-center figure
KC = [(1, 2), (2, 1), (3, 3), (1, 4), (11, 2), (12, 4), (10, 4), (13, 2), (6, 10), (7, 12), (5, 11), (8, 11)]
c, r = gonzalez(KC, 3)
optk, cent = kcenter_opt(KC, 3)
check("k-center figure: centers (1,2), (13,2), (7,12), next (10,4); r3 = sqrt13 = 3.61; OPT = sqrt13/2 = 1.80",
      c == [(1, 2), (13, 2), (7, 12), (10, 4)] and abs(r[-1] - math.sqrt(13)) < 1e-12 and
      abs(optk - math.sqrt(13) / 2) < 1e-9 and abs(max(mec(KC[4 * i:4 * i + 4])[0] for i in range(3)) - optk) < 1e-9)

# =====================================================================================================================
print("== page text")
page = open(PAGE, encoding="utf-8").read()
src = page[page.index("### Sources for this page"):]


def has(text, *subs):
    return all(x in text for x in subs)


check("figure captions carry the recomputed TSP numbers",
      has(page, f"MST {mstf:.2f}", f"tour {dt:.2f}", f"optimal tour {optf:.2f}", f"matching {momf:.2f}",
          f"= {mstf + momf:.2f}", f"tour {chl:.2f}", f"{dt / optf:.2f} times", f"{chl / optf:.2f} times",
          "a b a c d c e c a f g f a", "a b d c e c a g f a", "a b d c e g f a", "the 4 shortcuts", "1 shortcut"))
flat = re.sub(r"\s+", " ", page)
check("figure captions: k-center 3.61 and 1.80; load balance 9, 3, 18/3 = 6",
      has(flat, f"= {r[-1]:.2f} from its nearest center", f"{optk:.2f} = √13/2", "reaches 9", "the load under it, 3",
          "average 18/3 = 6", "makespan 6"))
check("sources: run counts and worst ratios match this run",
      has(src, f"{cnt:,} runs", f"worst ratios seen {float(worst['g']):.3f} greedy, {float(worst['s']):.3f} sorted",
          f"plus {N_VC_RAND:,} random ones (worst {float(worst_vc):.1f})", f"{N_LP} graphs; worst rounded/OPT {wr:.1f}",
          f"and {N_TSP_RAND} random ones", f"{inst} Euclidean and graph metrics",
          f"worst ratios {w2:.3f} and {w15:.3f}", f"(worst {wk:.1f})", f"worst $r^*/s^* = {float(wss):.3f}$"),
      f"cnt={cnt} vc_rand={N_VC_RAND} lp={N_LP} tsp_rand={N_TSP_RAND} inst={inst} w2={w2:.3f} w15={w15:.3f} "
      f"wk={wk:.2f} wss={float(wss):.3f} wg={float(worst['g']):.3f} ws={float(worst['s']):.3f} wvc={float(worst_vc)}")
lhs = F(17) * F(11, 10) + 5            # r' (1+delta)^(i-1) + x with r' = r(1+delta) - x = 17
nb = (F(20) - 5) * F(11, 10) ** 2 + 5   # the note's (r - x)(1+delta)^i + x
check("page: C5 numbers (LP 5/2, rounding 5, OPT 3; N = 2 gives 15/4 < 5) and the case-(2) numbers",
      has(page, r"\widetilde{\mathrm{OPT}}\ge\frac52", r"\mathrm{OPT} = 3$", r"\frac{15}4 < 5",
          f"is ${float(lhs)}$ and that bound ${float(nb)}$") and F(17) == F(20) * F(11, 10) - 5 and lhs > nb,
      f"{float(lhs)} vs {float(nb)}")

concept = re.sub(r"\s+", " ", open(CONCEPT, encoding="utf-8").read())
# reviewer: Theorem J.4 needs f computable in polynomial time (for f(n) = 2^(2^n) the trivial tour is an
# f(n)-approximation for positive integer lengths: inputs of size >= 2^n allow Held-Karp, smaller ones have every
# length < 2^(2^n)); the strip has 2k-1 triangles
check("page and concept page: TSP inapproximability stated for polynomial-time computable f only; strip of 2k-1",
      not re.search(r"(any|every|no) computable", flat + concept) and "no factor at all" not in concept and
      has(flat, "any polynomial-time computable factor $f(n)$", "every factor $f(n)$ computable in polynomial time",
          "strip of $2k-1$ triangles") and has(concept, "no polynomial-time computable $f(n)$"))
c1, r1 = gonzalez([(-1, 0), (0, 0), (1, 0)], 1)
check("concept page: the Gonzalez example (r_1 = 2, OPT 1, c_1 = -1 and c_2 = 1 two apart) and the K_n LP remark",
      has(concept, "so $r_1 = 2$", "radius 1", "value $n/2$ on $K_n$ while $\\mathrm{OPT} = n-1$") and r1 == [2] and
      c1 == [(-1, 0), (1, 0)] and abs(kcenter_opt([(-1, 0), (0, 0), (1, 0)], 1)[0] - 1) < 1e-12)

# =====================================================================================================================
print()
if FAIL:
    print("FAILED:", len(FAIL))
    for f in FAIL:
        print("  ", f)
    sys.exit(1)
print("ALL OK")
