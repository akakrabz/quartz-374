#!/usr/bin/env python3
"""Checks for content/3-homework-and-exams/lab-11.md (Lab 11, CS/ECE 374 A Fall 2026; no official solutions in the folder).

Problem 1 (longest increasing subsequence with at most k icky numbers).
  (a) the dynamic program Icky(i, c) exactly as the page states it (suffix form, 'starts with A[i]'), bottom-up,
      against an exhaustive search over all subsequences (all arrays of length <= 7 over a small range with all icky
      patterns sampled, random arrays up to length 11); the handout's example (k = 2, answer 5, the subsequence
      4, 5*, 6, 7, 9*); the page's small table; the number of table entries and of inner-loop steps; budgets k > n.
  (b) the graph reduction: vertices (i, c) plus s and t, built exactly as on the page; the graph is a dag (every edge
      goes to a larger index); the longest s-t path equals the answer; vertex and edge counts; the same example.
  the two traps: forgetting the budget (plain LIS) and a greedy that drops icky numbers.
Problem 2 (the longest palindrome that labels a path of a dag).
  (a) the dynamic program LongPal(u, v) exactly as on the page, in the stated evaluation order, against an
      enumeration of every path of the dag (random labeled dags on up to 8 vertices); the faster two-step version;
      the count of inner steps (at most E^2 + V^2 resp. 2VE + V^2).
  (b) the product graph: pairs with equal labels, a source and a target, weights 2 / 1 / 0 as on the page; it is a
      dag; its longest s-t path equals the answer.
  the handout's 14-vertex example, transcribed from the figure (27 edges): the answer is 6 (HANNAH), the path found
  is the highlighted one, and no palindromic path label has length 7 or more.
Every example number on the page is recomputed here."""
import itertools
import random

random.seed(11042026)
FAIL = []
NEG = float("-inf")


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail != "" else ""))
    if not cond:
        FAIL.append(name)


# ============================================================================ Problem 1
def brute_lis_icky(A, I, k):
    n = len(A)
    best = 0
    for mask in range(1 << n):
        idx = [i for i in range(n) if mask >> i & 1]
        if sum(I[i] for i in idx) > k:
            continue
        if all(A[idx[t]] < A[idx[t + 1]] for t in range(len(idx) - 1)):
            best = max(best, len(idx))
    return best


def lis_icky_dp(A, I, k, count=None):
    """Page, 1(a).  L[i][c] = length of the longest increasing subsequence of A[i..n] that starts with A[i] and
    contains at most c icky numbers (A[i] included); -inf if A[i] is icky and c = 0.
    L[i][c] = -inf if c - [Icky[i]] < 0, else 1 + max(0, max{ L[j][c - [Icky[i]]] : j > i, A[j] > A[i] }).
    Evaluation: i from n down to 1 (outer), c in any order.  Answer: max(0, max_i L[i][k])."""
    n = len(A)
    L = [[NEG] * (k + 1) for _ in range(n + 2)]
    for i in range(n, 0, -1):
        for c in range(0, k + 1):
            c2 = c - (1 if I[i - 1] else 0)
            if c2 < 0:
                L[i][c] = NEG
                continue
            best = 0
            for j in range(i + 1, n + 1):
                if count is not None:
                    count[0] += 1
                if A[j - 1] > A[i - 1] and L[j][c2] > best:
                    best = L[j][c2]
            L[i][c] = 1 + best
    ans = 0
    for i in range(1, n + 1):
        ans = max(ans, L[i][k])
    return ans, L


def lis_icky_graph(A, I, k):
    """Page, 1(b).  Vertices s, t and (i, c) for 1 <= i <= n, 0 <= c <= k.  Edges (weight 1 unless stated):
    s -> (i, [Icky[i]]) if [Icky[i]] <= k;  (i, c) -> (j, c + [Icky[j]]) if i < j, A[i] < A[j], c + [Icky[j]] <= k;
    (i, c) -> t with weight 0;  s -> t with weight 0.  Answer: the length of the longest path from s to t."""
    n = len(A)
    verts = ["s"] + [(i, c) for i in range(1, n + 1) for c in range(k + 1)] + ["t"]
    edges = [("s", "t", 0)]
    for i in range(1, n + 1):
        ic = 1 if I[i - 1] else 0
        if ic <= k:
            edges.append(("s", (i, ic), 1))
        for c in range(k + 1):
            edges.append(((i, c), "t", 0))
            for j in range(i + 1, n + 1):
                jc = c + (1 if I[j - 1] else 0)
                if A[i - 1] < A[j - 1] and jc <= k:
                    edges.append(((i, c), (j, jc), 1))
    # topological order: s, then (i, c) by increasing i, then t; every edge goes forward in it
    order = {v: r for r, v in enumerate(verts)}
    is_dag = all(order[a] < order[b] for a, b, _ in edges)
    dist = {v: NEG for v in verts}
    dist["s"] = 0
    for a, b, w in sorted(edges, key=lambda e: order[e[0]]):
        if dist[a] != NEG and dist[a] + w > dist[b]:
            dist[b] = dist[a] + w
    return dist["t"], len(verts), len(edges), is_dag


ok_dp = ok_graph = ok_dag = ok_sizes = ok_count = ok_bigk = True
cnt = 0
tests = []
for n in range(0, 6):
    for A in itertools.product(range(1, 4), repeat=n):
        for _ in range(2):
            tests.append((list(A), [random.random() < 0.5 for _ in range(n)], random.randint(0, 3)))
for _ in range(700):
    n = random.randint(4, 11)
    tests.append(([random.randint(1, 9) for _ in range(n)], [random.random() < random.choice([0.3, 0.6]) for _ in range(n)],
                  random.randint(0, 4)))
for A, I, k in tests:
    cnt += 1
    n = len(A)
    truth = brute_lis_icky(A, I, k)
    c = [0]
    got, _ = lis_icky_dp(A, I, k, c)
    ok_dp &= got == truth
    ok_count &= c[0] <= (k + 1) * n * (n - 1) // 2
    g, nv, ne, dag = lis_icky_graph(A, I, k)
    ok_graph &= g == truth
    ok_dag &= dag
    ok_sizes &= nv == n * (k + 1) + 2 and ne <= 1 + n + n * (k + 1) + (k + 1) * n * (n - 1) // 2
    ok_bigk &= lis_icky_dp(A, I, n + 3)[0] == lis_icky_dp(A, I, n)[0] == brute_lis_icky(A, I, n)
check(f"1(a) the dynamic program equals an exhaustive search over all subsequences ({cnt} inputs)", ok_dp)
check("1(a) at most (k+1) n(n-1)/2 inner steps: O(n^2 k) time for an (n) x (k+1) table", ok_count)
check("1(a) a budget k >= n behaves like k = n (so k can be capped at n)", ok_bigk)
check("1(b) the longest s-t path of the layered dag equals the same answer", ok_graph)
check("1(b) every edge goes from a smaller index to a larger one (s first, t last): the graph is a dag", ok_dag)
check("1(b) n(k+1) + 2 vertices and at most 1 + n + n(k+1) + (k+1) n(n-1)/2 edges: O(n^2 k)", ok_sizes)

HA = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5, 9, 7, 9, 3, 2, 3, 8, 4, 6, 2, 6]
HI = [1, 1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1]
HI = [bool(x) for x in HI]


def brute_bt(A, I, k):
    """Exhaustive search by backtracking (for the 22-element example)."""
    n = len(A)
    best = [0]

    def go(i, last, used, length):
        best[0] = max(best[0], length)
        for j in range(i, n):
            if A[j] > last and used + I[j] <= k:
                go(j + 1, A[j], used + I[j], length + 1)
    go(0, float("-inf"), 0, 0)
    return best[0]


check("1 handout example: 22 numbers, 10 of them icky, k = 2", len(HA) == 22 and sum(HI) == 10)
check("1 handout example: the answer is 5 (dynamic program, graph reduction and exhaustive backtracking agree)",
      lis_icky_dp(HA, HI, 2)[0] == 5 == lis_icky_graph(HA, HI, 2)[0] == brute_bt(HA, HI, 2))
sub = [(2, 4), (4, 5), (7, 6), (12, 7), (13, 9)]            # 0-based positions of 4, 5*, 6, 7, 9*
check("1 handout example: 4, 5*, 6, 7, 9* is an increasing subsequence with exactly two icky numbers",
      all(HA[p] == v for p, v in sub) and [HI[p] for p, _ in sub] == [False, True, False, False, True]
      and all(sub[t][0] < sub[t + 1][0] and sub[t][1] < sub[t + 1][1] for t in range(4)))
check("1 handout example with other budgets: k = 0 gives 3, k = 1 gives 4, k = 3 gives 6, no budget (k = 10) "
      "gives 6",
      [brute_bt(HA, HI, k) for k in (0, 1, 3, 10)] == [lis_icky_dp(HA, HI, k)[0] for k in (0, 1, 3, 10)]
      == [3, 4, 6, 6], [brute_bt(HA, HI, k) for k in (0, 1, 3, 10)])
# page's small example: A = 2*, 5, 3*, 4, 6*  with k = 1
SA, SI = [2, 5, 3, 4, 6], [True, False, True, False, True]
ans, L = lis_icky_dp(SA, SI, 1)
tab = [[L[i][c] for c in (0, 1)] for i in range(1, 6)]
check("1 small example A = 2*, 5, 3*, 4, 6*, k = 1: the answer is 2", ans == 2 == brute_lis_icky(SA, SI, 1), ans)
check("1 small example: the table rows (c = 0, c = 1) for i = 1..5",
      tab == [[NEG, 2], [1, 2], [NEG, 2], [1, 2], [NEG, 1]], tab)
check("1 small example: the answers for k = 0, 1, 2, 3 are 1, 2, 3, 4 (2*, 3*, 4, 6* needs all three icky numbers)",
      [brute_lis_icky(SA, SI, k) for k in range(4)] == [1, 2, 3, 4] == [lis_icky_dp(SA, SI, k)[0] for k in range(4)])
check("1 small example: L(1, 1) = 2 comes from 1 + L(2, 0) or 1 + L(4, 0), both 1 (the budget is spent on 2*)",
      L[1][1] == 2 and L[2][0] == 1 and L[4][0] == 1 and L[3][0] == NEG)
# traps
def plain_lis(A):
    return brute_lis_icky(A, [False] * len(A), 0)
def greedy_drop_icky(A, I, k):
    """Wrong: delete all icky numbers, take the LIS of the rest."""
    B = [a for a, x in zip(A, I) if not x]
    return plain_lis(B)
check("1 trap: ignoring the budget overcounts (small example: plain LIS 4, correct answer 2)",
      plain_lis(SA) == 4 and ans == 2)
check("1 trap: deleting every icky number first undercounts (small example: 1 instead of 2)",
      greedy_drop_icky(SA, SI, 1) == 1 and ans == 2, greedy_drop_icky(SA, SI, 1))

# ============================================================================ Problem 2
def all_paths(n, adj):
    """Every directed path of the dag, as a vertex list."""
    out = []

    def go(path):
        out.append(path[:])
        for w in adj[path[-1]]:
            path.append(w)
            go(path)
            path.pop()
    for s in range(n):
        go([s])
    return out


def brute_pal(n, edges, lab):
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
    best, arg = 0, None
    for p in all_paths(n, adj):
        s = [lab[v] for v in p]
        if s == s[::-1] and len(p) > best:
            best, arg = len(p), p
    return best, arg


def topo(n, edges):
    indeg = [0] * n
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b); indeg[b] += 1
    order = [v for v in range(n) if indeg[v] == 0]
    for v in order:
        for w in adj[v]:
            indeg[w] -= 1
            if indeg[w] == 0:
                order.append(w)
    assert len(order) == n, "not a dag"
    return order


def longpal_dp(n, edges, lab, count=None):
    """Page, 2(a).  LongPal(u, v) = number of vertices of the longest path from u to v whose label is a palindrome,
    -inf if there is none.
      -inf                                             if label(u) != label(v)
      1                                                if u = v
      max( 2 if u->v in E,  2 + max{ LongPal(x, y) : u->x in E, y->v in E } )   otherwise (-inf if nothing)
    Order: u in reverse topological order (outer), v in topological order (inner).  Answer: max over all (u, v)."""
    out = [[] for _ in range(n)]
    inn = [[] for _ in range(n)]
    E = set(edges)
    for a, b in edges:
        out[a].append(b); inn[b].append(a)
    order = topo(n, edges)
    LP = [[NEG] * n for _ in range(n)]
    for u in reversed(order):
        for v in order:
            if count is not None:
                count[0] += 1
            if lab[u] != lab[v]:
                continue
            if u == v:
                LP[u][v] = 1
                continue
            best = 2 if (u, v) in E else NEG
            for x in out[u]:
                for y in inn[v]:
                    if count is not None:
                        count[0] += 1
                    if LP[x][y] != NEG and 2 + LP[x][y] > best:
                        best = 2 + LP[x][y]
            LP[u][v] = best
    ans = max([LP[u][v] for u in range(n) for v in range(n)] + [0])
    return (0 if ans == NEG else ans), LP


def longpal_fast(n, edges, lab, count=None):
    """Page, 2(a) refinement: Half(x, v) = max{ LongPal(x, y) : y->v in E };
    LongPal(u, v) = max(2 if u->v, 2 + max{ Half(x, v) : u->x in E }).  O(VE) time."""
    out = [[] for _ in range(n)]
    inn = [[] for _ in range(n)]
    E = set(edges)
    for a, b in edges:
        out[a].append(b); inn[b].append(a)
    order = topo(n, edges)
    LP = [[NEG] * n for _ in range(n)]
    Half = [[NEG] * n for _ in range(n)]
    for u in reversed(order):
        for v in order:
            if count is not None:
                count[0] += 1
            if lab[u] == lab[v]:
                if u == v:
                    LP[u][v] = 1
                else:
                    best = 2 if (u, v) in E else NEG
                    for x in out[u]:
                        if count is not None:
                            count[0] += 1
                        if Half[x][v] != NEG and 2 + Half[x][v] > best:
                            best = 2 + Half[x][v]
                    LP[u][v] = best
        # Half(u, v) for all v needs LongPal(u, y) for all y: the whole row u is now complete
        for v in order:
            for y in inn[v]:
                if count is not None:
                    count[0] += 1
                if LP[u][y] > Half[u][v]:
                    Half[u][v] = LP[u][y]
    ans = max([LP[u][v] for u in range(n) for v in range(n)] + [0])
    return 0 if ans == NEG else ans


def longpal_graph(n, edges, lab):
    """Page, 2(b).  Vertices: s, t and every pair (u, v) with label(u) = label(v).
    Edges: s -> (u, v) weight 0;  (u, u) -> t weight 1;  (u, v) -> t weight 2 if u->v in E;
    (u, v) -> (x, y) weight 2 if u != v, u->x in E, y->v in E, label(x) = label(y).
    Answer: the longest path from s to t."""
    E = set(edges)
    out = [[] for _ in range(n)]
    inn = [[] for _ in range(n)]
    for a, b in edges:
        out[a].append(b); inn[b].append(a)
    pairs = [(u, v) for u in range(n) for v in range(n) if lab[u] == lab[v]]
    ed = []
    for (u, v) in pairs:
        ed.append(("s", (u, v), 0))
        if u == v:
            ed.append(((u, v), "t", 1))
        else:
            if (u, v) in E:
                ed.append(((u, v), "t", 2))
            for x in out[u]:
                for y in inn[v]:
                    if lab[x] == lab[y]:
                        ed.append(((u, v), (x, y), 2))
    pos = {v: r for r, v in enumerate(topo(n, edges))}
    rank = lambda z: -1 if z == "s" else (10 ** 9 if z == "t" else pos[z[0]])
    is_dag = all(rank(a) < rank(b) for a, b, _ in ed)
    dist = {"s": 0, "t": NEG}
    dist.update({p: NEG for p in pairs})
    for a, b, w in sorted(ed, key=lambda e: rank(e[0])):
        if dist[a] != NEG and dist[a] + w > dist[b]:
            dist[b] = dist[a] + w
    return (0 if dist["t"] == NEG else dist["t"]), len(pairs) + 2, len(ed), is_dag


def random_dag(n, p):
    perm = list(range(n))
    random.shuffle(perm)
    return [(perm[i], perm[j]) for i in range(n) for j in range(i + 1, n) if random.random() < p]


ok_dp2 = ok_fast = ok_g2 = ok_dag2 = ok_cnt = ok_cnt_fast = ok_sz2 = True
cnt = 0
for _ in range(1200):
    n = random.randint(0, 8)
    edges = random_dag(n, random.choice([0.25, 0.4, 0.6]))
    lab = [random.choice("AB" if random.random() < 0.6 else "ABC") for _ in range(n)]
    truth, _ = brute_pal(n, edges, lab)
    c = [0]
    got, _ = longpal_dp(n, edges, lab, c)
    ok_dp2 &= got == truth
    ok_cnt &= c[0] <= n * n + len(edges) ** 2
    c2 = [0]
    ok_fast &= longpal_fast(n, edges, lab, c2) == truth
    ok_cnt_fast &= c2[0] <= n * n + 2 * n * len(edges)
    g, nv, ne, dag = longpal_graph(n, edges, lab)
    ok_g2 &= g == truth
    ok_dag2 &= dag
    ok_sz2 &= nv <= n * n + 2 and ne <= 2 * n * n + len(edges) ** 2
    cnt += 1
check(f"2(a) LongPal, in the stated order, equals an enumeration of all paths ({cnt} random labeled dags on up to "
      "8 vertices)", ok_dp2)
check("2(a) at most V^2 + E^2 steps", ok_cnt)
check("2(a) the two-step version with Half(x, v) gives the same answers", ok_fast)
check("2(a) the two-step version takes at most V^2 + 2VE steps", ok_cnt_fast)
check("2(b) the longest s-t path of the pair graph equals the same answer", ok_g2)
check("2(b) the pair graph is a dag (the first coordinate moves forward along an edge of G)", ok_dag2)
check("2(b) at most V^2 + 2 vertices and 2V^2 + E^2 edges", ok_sz2)

# the handout's figure: 14 vertices, 27 edges
NAMES = ["S", "H1", "A1", "N1", "E", "O1", "N2", "T1", "T2", "O2", "N3", "H2", "D", "A2"]
IDX = {x: i for i, x in enumerate(NAMES)}
FE = [("S", "H1"), ("S", "E"), ("S", "O2"), ("O2", "H1"), ("H1", "A1"), ("A1", "N1"), ("A1", "E"), ("A1", "N2"),
      ("N1", "O1"), ("N1", "T1"), ("E", "T1"), ("E", "N3"), ("O1", "T2"), ("T1", "O1"), ("N2", "T1"), ("N2", "N3"),
      ("O2", "N2"), ("O2", "D"), ("D", "N2"), ("D", "N3"), ("D", "A2"), ("N3", "A2"), ("N3", "T2"), ("A2", "T1"),
      ("A2", "H2"), ("T1", "H2"), ("H2", "T2")]
fedges = [(IDX[a], IDX[b]) for a, b in FE]
flab = [x[0] for x in NAMES]
check("2 handout figure: 14 vertices, 27 edges, acyclic", len(NAMES) == 14 and len(set(fedges)) == 27
      and len(topo(14, fedges)) == 14)
bt, bp = brute_pal(14, fedges, flab)
check("2 handout figure: the longest palindromic path label has length 6, and the path is H A N N A H "
      "(the highlighted one)", bt == 6 and [NAMES[v] for v in bp] == ["H1", "A1", "N2", "N3", "A2", "H2"],
      (bt, [NAMES[v] for v in bp] if bp else None))
adjf = [[] for _ in range(14)]
for a, b in fedges:
    adjf[a].append(b)
pals = sorted({"".join(flab[v] for v in p) for p in all_paths(14, adjf)
               if [flab[v] for v in p] == [flab[v] for v in p][::-1] and len(p) >= 4})
check("2 handout figure: the only palindromic path labels with at least 4 letters are ANNA and HANNAH",
      pals == ["ANNA", "HANNAH"], pals)
check("2 handout figure: dynamic program, two-step version and pair graph all return 6",
      longpal_dp(14, fedges, flab)[0] == 6 == longpal_fast(14, fedges, flab) == longpal_graph(14, fedges, flab)[0])
_, LPf = longpal_dp(14, fedges, flab)
check("2 handout figure: LongPal(N2, N3) = 2, LongPal(A1, A2) = 4, LongPal(H1, H2) = 6",
      LPf[IDX["N2"]][IDX["N3"]] == 2 and LPf[IDX["A1"]][IDX["A2"]] == 4 and LPf[IDX["H1"]][IDX["H2"]] == 6)
npaths = len(all_paths(14, adjf))
check(f"2 handout figure: {npaths} directed paths in all were enumerated", npaths > 100, npaths)
# trap: reversing the string / LCS-style reasoning on a single path is not available; the two ends must move together
check("2 trap: a path whose label merely starts and ends with the same letter need not be a palindrome: "
      "H -> A -> E -> T -> H is a path of the figure with label HAETH",
      [flab[IDX[x]] for x in ["H1", "A1", "E", "T1", "H2"]] == list("HAETH")
      and all((IDX[a], IDX[b]) in set(fedges) for a, b in [("H1", "A1"), ("A1", "E"), ("E", "T1"), ("T1", "H2")]))

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: {FAIL}")
