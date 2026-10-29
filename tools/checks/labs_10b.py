#!/usr/bin/env python3
"""Checks for content/3-homework-and-exams/lab-10b.md (Lab 10b, CS/ECE 374 A Fall 2026; no official solutions).

Problem 1 (one wrong edge weight in an all-pairs distance array).  Random directed graphs with negative edges and no
negative cycle under either weight; many of them have cycles of length 0 (weights c(e) + p(a) - p(b) with c(e) >= 0,
often 0).  Ground truth: Floyd-Warshall, itself cross-checked against an enumeration of all simple paths.
  (a) the repair rule, applied in place in several orders, against Floyd-Warshall with w'; column u and row v unchanged.
  (b) the O(1) test dist[u,v] <= w'(u->v) against actual correctness.
  (c) the page's checker CheckAPSP against actual correctness, on the old arrays (weight raised or lowered), on correct
      arrays, on perturbed arrays and on adversarial ones (distances of a lighter graph: no tense edge, D[x,x] = 0, but
      too low); the two naive checkers of the traps (no tense edge; a tight incoming edge) are shown to fail, the second
      only when a cycle of length 0 exists; the one-search test, the lemma "correct iff dist'(u,v) = dist[u,v]", the
      shortcut dist[u,v] < w(u->v), and the out-neighbor test (fails only with zero cycles).
  (d) the reduction: on random graphs H with nonnegative weights, the constructed G has an all-zero distance array
      under w, and its corrected array decodes to H's distances.
Problem 2 (arbitrage).  Random rate matrices with exact Fractions, with and without arbitrage (and with cycles whose
product is exactly 1): MaxCurrency by the max-product Bellman-Ford and by -ln weights (floats) against the best product
over all simple paths; detection (all amounts start at 1, n-1 rounds, one test pass) and max-product Floyd-Warshall
against all simple cycles; ArbitrageCycle returns a simple cycle with product > 1 exactly when one exists.  The handout's
example (1.44), the page's trace, the no-arbitrage example, the figure's -ln labels and the floating-point example.
Every example number on the page is recomputed here."""
import math
import random
from fractions import Fraction as Fr

random.seed(10302026)
FAIL = []
INF = float("inf")


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail != "" else ""))
    if not cond:
        FAIL.append(name)


# ============================================================================ helpers
def fw(n, W):
    """Floyd-Warshall, diagonal 0, non-edges inf.  W: dict (a, b) -> weight, a != b."""
    D = [[0 if i == j else INF for j in range(n)] for i in range(n)]
    for (a, b), c in W.items():
        D[a][b] = min(D[a][b], c)
    for r in range(n):
        for i in range(n):
            if D[i][r] == INF:
                continue
            for j in range(n):
                if D[i][r] + D[r][j] < D[i][j]:
                    D[i][j] = D[i][r] + D[r][j]
    return D


def has_neg_cycle(n, W):
    D = fw(n, W)
    return any(D[i][i] < 0 for i in range(n))


def adjacency(n, W):
    adj = [[] for _ in range(n)]
    for (a, b) in W:
        adj[a].append(b)
    return adj


def brute_dist(n, W):
    """Minimum over all simple paths (the distance when there is no negative cycle)."""
    adj = adjacency(n, W)
    D = [[INF] * n for _ in range(n)]

    def go(s, x, length, seen):
        if length < D[s][x]:
            D[s][x] = length
        for y in adj[x]:
            if y not in seen:
                go(s, y, length + W[(x, y)], seen | {y})

    for s in range(n):
        go(s, s, 0, {s})
    return D


def simple_cycles(n, W):
    """All simple cycles, each once (smallest vertex first), as vertex lists."""
    adj = adjacency(n, W)
    out = []

    def go(s, x, path):
        for y in adj[x]:
            if y == s:
                out.append(list(path))
            elif y > s and y not in path:
                path.append(y)
                go(s, y, path)
                path.pop()

    for s in range(n):
        go(s, s, [s])
    return out


def cycle_len(W, cyc):
    return sum(W[(cyc[i], cyc[(i + 1) % len(cyc)])] for i in range(len(cyc)))


def has_zero_cycle(n, W):
    return any(cycle_len(W, c) == 0 for c in simple_cycles(n, W))


def rand_graph(n, p, mode):
    """mode 'pot': w = c + p(a) - p(b) with c >= 0 (no negative cycle, zero cycles likely); 'raw': filtered."""
    while True:
        W = {}
        pot = [random.randint(-4, 4) for _ in range(n)]
        for a in range(n):
            for b in range(n):
                if a != b and random.random() < p:
                    if mode == "pot":
                        c = 0 if random.random() < 0.45 else random.randint(1, 5)
                        W[(a, b)] = c + pot[a] - pot[b]
                    else:
                        W[(a, b)] = random.randint(-3, 7)
        if W and not has_neg_cycle(n, W):
            return W


def with_weight(W, e, c):
    W2 = dict(W)
    W2[e] = c
    return W2


# ============================================================================ Problem 1 — the page's algorithms
def repair_decrease(D, u, v, wp, order):
    """(a) in place: dist[x,y] <- min(dist[x,y], dist[x,u] + w'(u->v) + dist[v,y]) for all (x, y) in the given order."""
    ops = 0
    for (x, y) in order:
        ops += 1
        cand = D[x][u] + wp + D[v][y]
        if D[x][y] > cand:
            D[x][y] = cand
    return ops


def test_b(D, u, v, wp):
    """(b) assuming w > w': the array is correct iff dist[u,v] <= w'(u->v)."""
    return D[u][v] <= wp


def check_apsp(n, Wp, D, ops=None):
    """(c) CheckAPSP: for every source x, D[x,x] = 0, no tense edge, every finite D[x,y] reached along tight edges."""
    adj = adjacency(n, Wp)
    cnt = 0
    for x in range(n):
        if D[x][x] != 0:
            return False
        for (a, b), c in Wp.items():
            cnt += 1
            if D[x][a] + c < D[x][b]:
                return False
        marked = [False] * n
        marked[x] = True
        stack = [x]
        while stack:
            a = stack.pop()
            cnt += 1
            for b in adj[a]:
                cnt += 1
                if not marked[b] and D[x][a] < INF and D[x][a] + Wp[(a, b)] == D[x][b]:
                    marked[b] = True
                    stack.append(b)
        for y in range(n):
            cnt += 1
            if D[x][y] < INF and not marked[y]:
                return False
    if ops is not None:
        ops.append(cnt)
    return True


def naive_no_tense(n, Wp, D):
    return all(D[x][x] == 0 for x in range(n)) and \
        all(D[x][a] + c >= D[x][b] for x in range(n) for (a, b), c in Wp.items())


def naive_tight_in(n, Wp, D):
    if not naive_no_tense(n, Wp, D):
        return False
    for x in range(n):
        for y in range(n):
            if y != x and D[x][y] < INF:
                if not any(b == y and D[x][a] < INF and D[x][a] + c == D[x][y] for (a, b), c in Wp.items()):
                    return False
    return True


def one_search(n, W, u, v, wp, D):
    """(c), faster: w' <= w -> test (b); w' > w -> is v reachable from u along edges tight for w' w.r.t. row u?"""
    if wp <= W[(u, v)]:
        return D[u][v] <= wp
    Wp = with_weight(W, (u, v), wp)
    adj = adjacency(n, Wp)
    marked = [False] * n
    marked[u] = True
    stack = [u]
    while stack:
        a = stack.pop()
        for b in adj[a]:
            if not marked[b] and D[u][a] < INF and D[u][a] + Wp[(a, b)] == D[u][b]:
                marked[b] = True
                stack.append(b)
    return marked[v]


def out_neighbor_test(W, u, v, D):
    """Trap: (raised weight) correct iff dist[u,v] < w(u->v) or some out-neighbor a != v has w(u->a) + dist[a,v] =
    dist[u,v].  Right without zero cycles, wrong with them."""
    if D[u][v] < W[(u, v)]:
        return True
    return any(a2 == u and b != v and W[(a2, b)] + D[b][v] == D[u][v] for (a2, b) in W)


# ============================================================================ Problem 1 — ground truth sanity
print("== Problem 1: ground truth")
ok = True
for _ in range(400):
    n = random.randint(2, 6)
    W = rand_graph(n, random.choice([0.3, 0.5, 0.8]), random.choice(["pot", "raw"]))
    if fw(n, W) != brute_dist(n, W):
        ok = False
check("Floyd-Warshall = minimum over all simple paths on 400 random graphs without negative cycles", ok)

# ---------------------------------------------------------------- random instances
inst_dec, inst_inc = [], []          # (n, W, u, v, wp)
zero_count = 0
while len(inst_dec) < 4000 or len(inst_inc) < 4000:
    n = random.randint(2, 6)
    W = rand_graph(n, random.choice([0.3, 0.5, 0.8]), random.choice(["pot", "pot", "raw"]))
    (u, v) = random.choice(sorted(W))
    w = W[(u, v)]
    if len(inst_dec) < 4000:
        wp = w - random.randint(1, 6)
        if not has_neg_cycle(n, with_weight(W, (u, v), wp)):
            inst_dec.append((n, W, u, v, wp))
    if len(inst_inc) < 4000:
        wp = w + random.randint(1, 6)
        inst_inc.append((n, W, u, v, wp))
zero_dec = sum(has_zero_cycle(n, W) for (n, W, u, v, wp) in inst_dec)
zero_inc = sum(has_zero_cycle(n, W) for (n, W, u, v, wp) in inst_inc)
check("instances: 4000 lowered and 4000 raised weights; many graphs have a zero-length cycle",
      zero_dec > 600 and zero_inc > 600, f"zero cycles in {zero_dec} and {zero_inc}")

# ---------------------------------------------------------------- the notation note
print("== Problem 1: column u and row v never change")
ok = True
for (n, W, u, v, wp) in inst_dec + inst_inc:
    D, Dp = fw(n, W), fw(n, with_weight(W, (u, v), wp))
    if any(D[x][u] != Dp[x][u] or D[v][x] != Dp[v][x] for x in range(n)):
        ok = False
check("dist'(x,u) = dist(x,u) and dist'(v,y) = dist(v,y) for all x, y (both lowered and raised weights)", ok)

# ---------------------------------------------------------------- (a)
print("== Problem 1(a): repair after lowering the weight")
ok_row = ok_rand = ok_col = ok_formula = True
changed_some = 0
for (n, W, u, v, wp) in inst_dec:
    D, Dp = fw(n, W), fw(n, with_weight(W, (u, v), wp))
    pairs = [(x, y) for x in range(n) for y in range(n)]
    E1 = [r[:] for r in D]
    ops = repair_decrease(E1, u, v, wp, pairs)
    ok_row &= (E1 == Dp) and ops == n * n
    E2 = [r[:] for r in D]
    random.shuffle(pairs)
    repair_decrease(E2, u, v, wp, pairs)
    ok_rand &= E2 == Dp
    E3 = [r[:] for r in D]
    repair_decrease(E3, u, v, wp, [(x, y) for y in range(n) for x in range(n)])
    ok_col &= E3 == Dp
    F = [[min(D[x][y], D[x][u] + wp + D[v][y]) for y in range(n)] for x in range(n)]
    ok_formula &= F == Dp
    changed_some += D != Dp
check("lemma: dist'(x,y) = min{dist(x,y), dist(x,u) + w'(u->v) + dist(v,y)} on 4000 instances", ok_formula)
check("RepairDecrease in place, row by row, equals Floyd-Warshall with w' (and makes exactly V^2 updates)", ok_row)
check("RepairDecrease in place in a random order and column by column: same result", ok_rand and ok_col)
check("the array actually changes in many instances", changed_some > 1500, f"{changed_some} of 4000")

# running example of Chapter 9 (vertices 1..4 -> 0..3)
RUN = {(0, 1): -2, (1, 2): 4, (2, 1): 1, (2, 3): 3, (3, 2): 2, (3, 0): -3}
DR = fw(4, RUN)
check("Ch 9 running example: dist matrix as on the Ch 9 page",
      DR == [[0, -2, 2, 5], [4, 0, 4, 7], [0, -2, 0, 3], [-3, -5, -1, 0]], DR)
W23 = with_weight(RUN, (1, 2), 2)
check("example (a): w'(2->3) = 2 creates no negative cycle; 1->2->3->4->1 becomes a zero cycle",
      not has_neg_cycle(4, W23) and cycle_len(W23, [0, 1, 2, 3]) == 0 and cycle_len(W23, [1, 2]) == 3)
E = [r[:] for r in DR]
repair_decrease(E, 1, 2, 2, [(x, y) for x in range(4) for y in range(4)])
check("example (a): repaired matrix rows (0 -2 0 3), (2 0 2 5), (0 -2 0 3), (-3 -5 -3 0) = Floyd-Warshall",
      E == [[0, -2, 0, 3], [2, 0, 2, 5], [0, -2, 0, 3], [-3, -5, -3, 0]] and E == fw(4, W23), E)
chg = sorted((x + 1, y + 1) for x in range(4) for y in range(4) if E[x][y] != DR[x][y])
check("example (a): exactly six entries change: (1,3), (1,4), (2,1), (2,3), (2,4), (4,3)",
      chg == [(1, 3), (1, 4), (2, 1), (2, 3), (2, 4), (4, 3)], chg)
check("example (a): column 2 is (-2, 0, -2, -5) and row 3 is (0, -2, 0, 3), before and after",
      [DR[x][1] for x in range(4)] == [-2, 0, -2, -5] == [E[x][1] for x in range(4)]
      and DR[2] == [0, -2, 0, 3] == E[2])

# ---------------------------------------------------------------- (b)
print("== Problem 1(b): the O(1) test after lowering the weight")
ok = True
cnt_true = cnt_false = 0
for (n, W, u, v, wp) in inst_dec:
    actual = fw(n, W) == fw(n, with_weight(W, (u, v), wp))
    t = test_b(fw(n, W), u, v, wp)
    ok &= (t == actual)
    cnt_true += actual
    cnt_false += not actual
check("dist[u,v] <= w'(u->v) iff the array is still correct (4000 instances)", ok,
      f"{cnt_true} still correct, {cnt_false} wrong")
check("example (b): w'(3->2) = 0 or -2 keeps the array correct; w'(3->2) = -3 does not; w'(2->3) = 2 does not",
      test_b(DR, 2, 1, 0) and fw(4, with_weight(RUN, (2, 1), 0)) == DR
      and not has_neg_cycle(4, with_weight(RUN, (2, 1), -2))
      and test_b(DR, 2, 1, -2) and fw(4, with_weight(RUN, (2, 1), -2)) == DR
      and not test_b(DR, 2, 1, -3) and fw(4, with_weight(RUN, (2, 1), -3)) != DR
      and not has_neg_cycle(4, with_weight(RUN, (2, 1), -3))
      and fw(4, with_weight(RUN, (2, 1), -3))[2][1] == -3
      and not test_b(DR, 1, 2, 2))
# the test is useless after a raise: it always says "correct"
check("after a raise, dist[u,v] <= w'(u->v) always holds (so it proves nothing)",
      all(fw(n, W)[u][v] <= wp for (n, W, u, v, wp) in inst_inc))

# ---------------------------------------------------------------- (c)
print("== Problem 1(c): checking an array")
ok_old = ok_correct = True
n_old_wrong = 0
ops_ok = True
for (n, W, u, v, wp) in inst_dec + inst_inc:
    Wp = with_weight(W, (u, v), wp)
    D, Dp = fw(n, W), fw(n, Wp)
    ops = []
    r = check_apsp(n, Wp, D, ops)
    ok_old &= r == (D == Dp)
    n_old_wrong += D != Dp
    ops2 = []
    ok_correct &= check_apsp(n, Wp, Dp, ops2)
    ops_ok &= ops2[0] <= n * (2 * len(Wp) + 2 * n)
check("CheckAPSP on the old array = actual correctness (8000 instances, lowered and raised weights)", ok_old,
      f"{n_old_wrong} wrong arrays")
check("CheckAPSP accepts every correct array", ok_correct)
check("CheckAPSP: at most V(2E + 2V) steps on accepted arrays (O(V(V+E)))", ops_ok)

# perturbed and adversarial arrays
ok_pert = True
n_pert = 0
naive1_fooled = naive2_fooled = naive2_fooled_nozero = 0
ok_adv = True
n_adv_wrong = 0
for (n, W, u, v, wp) in random.sample(inst_dec + inst_inc, 2000):
    Wp = with_weight(W, (u, v), wp)
    Dp = fw(n, Wp)
    cands = []
    for _ in range(4):
        P = [r[:] for r in Dp]
        x, y = random.randrange(n), random.randrange(n)
        P[x][y] = random.choice([P[x][y] + 1, P[x][y] - 1, P[x][y] + Fr(1, 2), INF, 0 if P[x][y] == INF else INF,
                                 -1 if P[x][y] == INF else P[x][y] - 2])
        cands.append(P)
    # adversarial: distances of a lighter graph (one or two edges lowered, or one edge added) -- no tense edge
    for _ in range(3):
        Wl = dict(Wp)
        for e in random.sample(sorted(Wl), min(len(Wl), random.randint(1, 2))):
            Wl[e] -= random.randint(1, 3)
        if random.random() < 0.5:
            a, b = random.sample(range(n), 2)
            if (a, b) not in Wl:
                Wl[(a, b)] = random.randint(-2, 4)
        if not has_neg_cycle(n, Wl):
            cands.append(fw(n, Wl))
    zero = has_zero_cycle(n, Wp)
    for P in cands:
        truth = P == Dp
        ok_pert &= check_apsp(n, Wp, P) == truth
        n_pert += 1
        if naive_no_tense(n, Wp, P) and not truth:
            naive1_fooled += 1
        if naive_tight_in(n, Wp, P) and not truth:
            naive2_fooled += 1
            naive2_fooled_nozero += not zero
check("CheckAPSP = actual correctness on perturbed and adversarial arrays", ok_pert, f"{n_pert} arrays")
check("trap: 'D[x,x] = 0 and no tense edge' accepts wrong arrays", naive1_fooled > 100, f"{naive1_fooled} fooled")
check("trap: '... and every finite entry has a tight incoming edge' accepts wrong arrays, but only in graphs with a "
      "zero-length cycle", naive2_fooled > 0 and naive2_fooled_nozero == 0,
      f"{naive2_fooled} fooled, {naive2_fooled_nozero} without zero cycle")
# naive2 on the old arrays after a raise
f_old = f_old_nozero = 0
for (n, W, u, v, wp) in inst_inc:
    Wp = with_weight(W, (u, v), wp)
    D, Dp = fw(n, W), fw(n, Wp)
    if D != Dp:
        check_n1 = naive_no_tense(n, Wp, D)
        if not check_n1:
            FAIL.append("raise made an edge tense")
        if naive_tight_in(n, Wp, D):
            f_old += 1
            f_old_nozero += not has_zero_cycle(n, Wp)
check("after a raise the old array never has a tense edge (all wrong old arrays pass the no-tense test)",
      "raise made an edge tense" not in FAIL)
check("the tight-incoming-edge test is fooled by some old arrays after a raise, only with zero cycles",
      f_old > 0 and f_old_nozero == 0, f"{f_old} fooled")

# the page's 4-vertex trap example: u=0, v=1, a=2, b=3
T = {(0, 1): 1, (0, 2): 0, (2, 0): 0, (1, 3): 0, (3, 1): 0}
Tp = with_weight(T, (0, 1), 5)
DT, DTp = fw(4, T), fw(4, Tp)
check("trap example: dist[u,v] = 1 but the true distance is 5; the array is wrong", DT[0][1] == 1 and DTp[0][1] == 5)
check("trap example: no tense edge and every finite entry has a tight incoming edge, yet CheckAPSP rejects",
      naive_no_tense(4, Tp, DT) and naive_tight_in(4, Tp, DT) and not check_apsp(4, Tp, DT))
check("trap example: the out-neighbor test is fooled (w(u->a) + dist[a,v] = 0 + 1 = dist[u,v])",
      out_neighbor_test(T, 0, 1, DT) and DT[2][1] == 1)
check("trap example: the one-search test rejects (v and b are not reached from u along tight edges)",
      not one_search(4, T, 0, 1, 5, DT))

# one search; the lemma; the shortcut; the out-neighbor test
ok_one = ok_lemma = ok_short = ok_out_nozero = True
out_fooled_zero = 0
short_used = 0
for (n, W, u, v, wp) in inst_dec + inst_inc:
    Wp = with_weight(W, (u, v), wp)
    D, Dp = fw(n, W), fw(n, Wp)
    truth = D == Dp
    ok_one &= one_search(n, W, u, v, wp, D) == truth
    ok_lemma &= (Dp[u][v] == D[u][v]) == truth
    if wp > W[(u, v)]:
        if D[u][v] < W[(u, v)]:
            short_used += 1
            ok_short &= truth
        o = out_neighbor_test(W, u, v, D)
        if has_zero_cycle(n, W):
            out_fooled_zero += o != truth
        else:
            ok_out_nozero &= o == truth
check("lemma: the array is correct iff dist'(u,v) = dist[u,v] (lowered and raised weights)", ok_lemma)
check("one search from u (or test (b) if w' <= w) = actual correctness on 8000 instances", ok_one)
check("shortcut: after a raise, dist[u,v] < w(u->v) implies the array is correct", ok_short and short_used > 500,
      f"{short_used} cases")
check("out-neighbor test is right in every graph without a zero-length cycle, wrong in some with one",
      ok_out_nozero and out_fooled_zero > 0, f"{out_fooled_zero} wrong")

# examples of (c) on the running example: raise every edge by 1 and by 100
res = {}
for e in RUN:
    res[e] = [fw(4, with_weight(RUN, e, RUN[e] + d)) == DR for d in (1, 100)]
    ok = all(one_search(4, RUN, e[0], e[1], RUN[e] + d, DR) == r for d, r in zip((1, 100), res[e]))
    ok &= all(check_apsp(4, with_weight(RUN, e, RUN[e] + d), DR) == r for d, r in zip((1, 100), res[e]))
    check(f"example (c): checkers agree with the truth when raising {e[0] + 1}->{e[1] + 1}", ok)
check("example (c): raising 3->2 or 4->3 (by 1 or by 100) keeps the array correct; raising any other edge by 1 "
      "breaks it", res[(2, 1)] == [True, True] and res[(3, 2)] == [True, True]
      and all(res[e] == [False, False] for e in RUN if e not in [(2, 1), (3, 2)]))
check("example (c): dist[3,2] = -2 < 1 = w(3->2) and dist[4,3] = -1 < 2 = w(4->3)",
      DR[2][1] == -2 and DR[3][2] == -1)


def count_simple_paths(n, W, s, t):
    adj = adjacency(n, W)

    def go(x, seen):
        if x == t:
            return 1
        return sum(go(y, seen | {y}) for y in adj[x] if y not in seen)

    return go(s, {s})


check("example (c): each of 1->2, 2->3, 3->4, 4->1 is the only path from its tail to its head",
      all(count_simple_paths(4, RUN, a, b) == 1 for (a, b) in [(0, 1), (1, 2), (2, 3), (3, 0)]))
check("example (c): raising 1->2 by 1: slack 0 + (-1) - (-2) = 1 > 0, and 1 has no other out-edge",
      [e for e in RUN if e[0] == 0] == [(0, 1)] and DR[0][0] + (RUN[(0, 1)] + 1) - DR[0][1] == 1)

# ---------------------------------------------------------------- (d)
print("== Problem 1(d): the reduction from APSP")


def reduction(nH, WH):
    u, v = nH, nH + 1
    G = dict(WH)
    for x in range(nH):
        G[(x, u)] = 0
        G[(v, x)] = 0
    G[(u, v)] = 0
    M = 1 + sum(WH.values())
    return G, u, v, M


ok_zero = ok_decode = ok_size = ok_ncyc = True
count = 0
unreach = 0
for _ in range(1500):
    nH = random.randint(1, 6)
    WH = {}
    for a in range(nH):
        for b in range(nH):
            if a != b and random.random() < random.choice([0.2, 0.4, 0.7]):
                WH[(a, b)] = random.randint(0, 9)
    G, u, v, M = reduction(nH, WH)
    N = nH + 2
    ok_size &= len(G) == len(WH) + 2 * nH + 1
    ok_ncyc &= not has_neg_cycle(N, G) and not has_neg_cycle(N, with_weight(G, (u, v), M))
    ok_zero &= fw(N, G) == [[0] * N for _ in range(N)]
    Dp = fw(N, with_weight(G, (u, v), M))
    DH = brute_dist(nH, WH)
    dec = [[Dp[x][y] if Dp[x][y] < M else INF for y in range(nH)] for x in range(nH)]
    ok_decode &= dec == DH == fw(nH, WH)
    ok_decode &= all(Dp[x][y] == min(DH[x][y], M) for x in range(nH) for y in range(nH))
    unreach += any(DH[x][y] == INF for x in range(nH) for y in range(nH))
    count += 1
check("reduction: G has n + 2 vertices and m + 2n + 1 edges", ok_size)
check("reduction: no negative cycle under w or w'", ok_ncyc)
check("reduction: the old array of G is all zeros", ok_zero)
check("reduction: dist'(x,y) = min{dist_H(x,y), M}, and decoding (>= M means unreachable) gives H's distances",
      ok_decode, f"{count} graphs H, {unreach} with unreachable pairs")
ok_many = True
for _ in range(300):
    nH = random.randint(1, 6)
    WH = {(a, b): random.randint(1, 9) for a in range(nH) for b in range(nH) if a != b and random.random() < 0.5}
    G, u, v, M = reduction(nH, WH)
    N = nH + 2
    before, after = fw(N, with_weight(G, (u, v), M)), fw(N, G)        # lowering u->v from M to 0
    changed = sum(before[x][y] != after[x][y] for x in range(N) for y in range(N))
    ok_many &= changed >= nH * (nH - 1)
check("(a) is optimal: lowering one weight can change Theta(V^2) entries (the gadget, u->v lowered from M to 0, "
      "positive weights in H: every pair of distinct vertices of H changes)", ok_many)
HX = {(0, 1): 2, (1, 2): 1, (2, 1): 3}
GX, uX, vX, MX = reduction(3, HX)
DX = fw(5, with_weight(GX, (uX, vX), MX))
check("figure example: H = p->q 2, q->r 1, r->q 3; M = 7; corrected distances p->q 2, p->r 3, q->r 1, r->q 3, "
      "q->p = r->p = 7 (decoded: unreachable)",
      MX == 7 and [DX[0][1], DX[0][2], DX[1][2], DX[2][1], DX[1][0], DX[2][0]] == [2, 3, 1, 3, 7, 7]
      and fw(5, GX) == [[0] * 5 for _ in range(5)])

# ============================================================================ Problem 2
print("== Problem 2: arbitrage")


def edges_of(R):
    n = len(R)
    return {(i, j): R[i][j] for i in range(n) for j in range(n) if i != j and R[i][j] > 0}


def brute_cycles(R):
    E = edges_of(R)
    out = []
    for c in simple_cycles(len(R), E):
        p = Fr(1)
        for i in range(len(c)):
            p *= E[(c[i], c[(i + 1) % len(c)])]
        out.append((c, p))
    return out


def brute_arb(R):
    return any(p > 1 for c, p in brute_cycles(R))


def brute_max(R):
    """Best product over all simple paths from currency 0 (1 for currency 0 itself, 0 if unreachable)."""
    n = len(R)
    E = edges_of(R)
    adj = adjacency(n, E)
    best = [Fr(0)] * n
    best[0] = Fr(1)

    def go(x, amt, seen):
        if amt > best[x]:
            best[x] = amt
        for y in adj[x]:
            if y not in seen:
                go(y, amt * E[(x, y)], seen | {y})

    go(0, Fr(1), {0})
    return best


def max_currency(R, ops=None):
    """(a), max-product form of Bellman-Ford from currency 1 (index 0): n - 1 rounds over all pairs."""
    n = len(R)
    amt = [Fr(0)] * n
    amt[0] = Fr(1)
    cnt = 0
    for _ in range(n - 1):
        for i in range(n):
            for j in range(n):
                if i != j:
                    cnt += 1
                    if amt[i] * R[i][j] > amt[j]:
                        amt[j] = amt[i] * R[i][j]
    if ops is not None:
        ops.append(cnt)
    return amt


def max_currency_log(R):
    """(a), Bellman-Ford on weights -ln R[i,j] (floats), MaxCurrency[i] = exp(-dist(1, i))."""
    n = len(R)
    dist = [INF] * n
    dist[0] = 0.0
    E = [(i, j, -math.log(R[i][j])) for i in range(n) for j in range(n) if i != j and R[i][j] > 0]
    for _ in range(n - 1):
        for (i, j, c) in E:
            if dist[i] + c < dist[j]:
                dist[j] = dist[i] + c
    return [math.exp(-d) if d < INF else 0.0 for d in dist]


def detect(R):
    """(b): every amount starts at 1 (the super-source), n - 1 rounds, then one test pass."""
    n = len(R)
    amt = [Fr(1)] * n
    for _ in range(n - 1):
        for i in range(n):
            for j in range(n):
                if i != j and amt[i] * R[i][j] > amt[j]:
                    amt[j] = amt[i] * R[i][j]
    return any(i != j and amt[i] * R[i][j] > amt[j] for i in range(n) for j in range(n))


def detect_super(R):
    """(b) literally: a new vertex s with rate 1 to every currency, Bellman-Ford from s, V - 1 = n rounds."""
    n = len(R)
    amt = [Fr(0)] * n + [Fr(1)]
    E = [(n, j, Fr(1)) for j in range(n)] + [(i, j, R[i][j]) for i in range(n) for j in range(n)
                                             if i != j and R[i][j] > 0]
    for _ in range(n):
        for (i, j, r) in E:
            if amt[i] * r > amt[j]:
                amt[j] = amt[i] * r
    return any(amt[i] * r > amt[j] for (i, j, r) in E)


def detect_fw(R):
    """(b) alternative: Floyd-Warshall in max-product form, diagonal 1; arbitrage iff some M[i,i] > 1."""
    n = len(R)
    M = [[Fr(1) if i == j else Fr(R[i][j]) for j in range(n)] for i in range(n)]
    for r in range(n):
        for i in range(n):
            for j in range(n):
                if M[i][r] * M[r][j] > M[i][j]:
                    M[i][j] = M[i][r] * M[r][j]
    return any(M[i][i] > 1 for i in range(n))


def arbitrage_cycle(R, ops=None, trace=None):
    """(c) ArbitrageCycle: as detect, with predecessors; on a tense trade i->j, relax it, walk back n steps from j,
    return the pointer cycle in trading order (the last currency trades back to the first)."""
    n = len(R)
    amt = [Fr(1)] * n
    pred = [None] * n
    cnt = 0
    if trace is not None:
        trace.append(list(amt))
    for _ in range(n - 1):
        for i in range(n):
            for j in range(n):
                if i != j:
                    cnt += 1
                    if amt[i] * R[i][j] > amt[j]:
                        amt[j] = amt[i] * R[i][j]
                        pred[j] = i
        if trace is not None:
            trace.append(list(amt))
    for i in range(n):
        for j in range(n):
            if i != j:
                cnt += 1
                if amt[i] * R[i][j] > amt[j]:
                    amt[j] = amt[i] * R[i][j]
                    pred[j] = i
                    x = j
                    for _ in range(n):
                        x = pred[x]
                    cyc = [x]
                    y = pred[x]
                    while y != x:
                        cyc.append(y)
                        y = pred[y]
                    cyc.reverse()
                    if ops is not None:
                        ops.append(cnt)
                    if trace is not None:
                        trace.append((i, j))
                    return cyc
    if ops is not None:
        ops.append(cnt)
    return None


RATES = [Fr(p, q) for p in range(1, 9) for q in range(1, 9)]


def rand_rates(n, mode):
    if mode == "raw":
        return [[Fr(1) if i == j else (Fr(0) if random.random() < 0.15 else random.choice(RATES))
                 for j in range(n)] for i in range(n)]
    # prices and fees: R[i,j] = f * price_i / price_j with f <= 1 (no arbitrage; f = 1 makes product-1 cycles)
    price = [Fr(random.randint(1, 9), random.randint(1, 9)) for _ in range(n)]
    R = [[Fr(1)] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                f = random.choice([Fr(1), Fr(1), Fr(1), Fr(9, 10), Fr(1, 2), Fr(0)])
                R[i][j] = f * price[i] / price[j]
    if mode == "tweak":           # push one rate up a little: often creates arbitrage
        i, j = random.sample(range(n), 2)
        R[i][j] *= Fr(random.choice([11, 21, 101]), random.choice([10, 20, 100]))
    return R


arb_inst = []
for _ in range(1500):
    n = random.randint(2, 6)
    arb_inst.append(rand_rates(n, random.choice(["raw", "fee", "tweak"])))
n_arb = sum(brute_arb(R) for R in arb_inst)
n_tie = sum(any(p == 1 for c, p in brute_cycles(R)) and not brute_arb(R) for R in arb_inst)
check("instances: 1500 random rate matrices, with and without arbitrage, some with product-exactly-1 cycles",
      300 < n_arb < 1200 and n_tie > 100, f"{n_arb} with arbitrage, {n_tie} without but with a product-1 cycle")

ok_a = ok_alog = True
n_a = 0
ops_ok = True
for R in arb_inst:
    if brute_arb(R):
        continue
    n_a += 1
    ops = []
    m = max_currency(R, ops)
    ok_a &= m == brute_max(R)
    n = len(R)
    ops_ok &= ops[0] == (n - 1) * n * (n - 1)
    ml = max_currency_log(R)
    ok_alog &= all(abs(float(a) - b) <= 1e-9 * max(1.0, float(a)) for a, b in zip(m, ml))
check("(a) max-product Bellman-Ford from currency 1 = best product over all simple paths (exact)", ok_a,
      f"{n_a} matrices without arbitrage")
check("(a) the -ln version, exp(-dist(1, i)), agrees to 1e-9", ok_alog)
check("(a) (n - 1) n (n - 1) relaxation tests: O(n^3)", ops_ok)

ok_b = ok_bs = ok_bfw = ok_c = True
for R in arb_inst:
    truth = brute_arb(R)
    ok_b &= detect(R) == truth
    ok_bs &= detect_super(R) == truth
    ok_bfw &= detect_fw(R) == truth
    ops = []
    cyc = arbitrage_cycle(R, ops)
    n = len(R)
    if truth:
        good = cyc is not None and len(set(cyc)) == len(cyc) and len(cyc) >= 2
        if good:
            p = Fr(1)
            for k in range(len(cyc)):
                r = R[cyc[k]][cyc[(k + 1) % len(cyc)]]
                good &= r > 0
                p *= r
            good &= p > 1
        ok_c &= good
    else:
        ok_c &= cyc is None
    ok_c &= ops[0] <= n * n * (n - 1)
check("(b) all amounts start at 1, n - 1 rounds, test pass: detects arbitrage iff some simple cycle has product > 1",
      ok_b)
check("(b) Bellman-Ford from a super-source (rate 1 to every currency, n rounds): same answers", ok_bs)
check("(b) max-product Floyd-Warshall (some M[i,i] > 1): same answers", ok_bfw)
check("(c) ArbitrageCycle returns a simple cycle of positive rates with product > 1 iff arbitrage exists; "
      "at most n * n(n - 1) tests", ok_c)

# ---------------------------------------------------------------- the handout's example and the page's examples
D_, Y_, E_ = 0, 1, 2
check("handout: 120 * 0.01 * 1.2 = 1.44 exactly", Fr(120) * Fr(1, 100) * Fr(6, 5) == Fr(144, 100))
MKT = [[Fr(1), Fr(120), Fr(4, 5)],
       [Fr(1, 125), Fr(1), Fr(1, 100)],
       [Fr(6, 5), Fr(100), Fr(1)]]
cyc_products = {tuple(c): p for c, p in brute_cycles(MKT)}
check("figure market: cycle products $Y 0.96, $E 0.96, YE 1, $YE$ 1.44, $EY$ 0.64",
      cyc_products == {(0, 1): Fr(96, 100), (0, 2): Fr(96, 100), (1, 2): Fr(1), (0, 1, 2): Fr(144, 100),
                       (0, 2, 1): Fr(64, 100)}, cyc_products)
lab = {e: round(-math.log(float(r)), 2) for e, r in edges_of(MKT).items()}
check("figure labels: -ln 120 = -4.79, -ln 0.01 = 4.61, -ln 1.2 = -0.18, -ln 0.008 = 4.83, -ln 100 = -4.61, "
      "-ln 0.8 = 0.22", lab == {(0, 1): -4.79, (1, 2): 4.61, (2, 0): -0.18, (1, 0): 4.83, (2, 1): -4.61,
                                (0, 2): 0.22}, lab)
check("figure: the arbitrage cycle has length -ln 1.44 = -0.36 (and -4.79 + 4.61 - 0.18 = -0.36)",
      round(-math.log(1.44), 2) == -0.36 and round(-4.79 + 4.61 - 0.18, 2) == -0.36
      and abs(sum(-math.log(float(MKT[a][b])) for a, b in [(0, 1), (1, 2), (2, 0)]) + math.log(1.44)) < 1e-12)
tr = []
cyc = arbitrage_cycle(MKT, trace=tr)
check("trace: amounts ($, Y, E) start (1, 1, 1), after round 1 (1.44, 120, 1.2), after round 2 (2.0736, 172.8, 1.728)",
      tr[0] == [1, 1, 1] and tr[1] == [Fr(144, 100), 120, Fr(12, 10)]
      and tr[2] == [Fr(20736, 10000), Fr(1728, 10), Fr(1728, 1000)], tr[:3])
check("trace: the test pass finds $ -> Y tense (2.0736 * 120 = 248.832 > 172.8) and returns E -> $ -> Y -> E",
      tr[3] == (0, 1) and Fr(20736, 10000) * 120 == Fr(248832, 1000) and cyc == [E_, D_, Y_], (tr[3], cyc))
MKT2 = [r[:] for r in MKT]
MKT2[2][0] = Fr(4, 5)
check("no-arbitrage example (E -> $ = 0.8): no arbitrage, MaxCurrency = (1, 120, 1.2)",
      not brute_arb(MKT2) and max_currency(MKT2) == [1, 120, Fr(6, 5)] == brute_max(MKT2)
      and not detect(MKT2) and arbitrage_cycle(MKT2) is None)
check("no-arbitrage example: direct $ -> E gives only 0.8; via yen 120 * 0.01 = 1.2",
      MKT2[0][2] == Fr(4, 5) and MKT2[0][1] * MKT2[1][2] == Fr(6, 5))
s = -math.log(1 / 6) - math.log(2) - math.log(3)
check("floating point: 1/6 * 2 * 3 = 1 exactly, but -ln(1/6) - ln 2 - ln 3 in double precision is about -2.2e-16",
      Fr(1, 6) * 2 * 3 == 1 and -3e-16 < s < -1e-16, s)
s2 = -math.log(10) - math.log(0.1)
check("floating point: -ln 10 - ln 0.1 is about -4.4e-16 in double precision", -5e-16 < s2 < -4e-16, s2)

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: {FAIL}")
