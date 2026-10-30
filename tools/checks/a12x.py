#!/usr/bin/env python3
"""Checks for content/2-algorithms/12-np-hardness-exercises.md (solved exercises 12.1-12.4, 12.6, 12.7(b)(c), 12.8,
12.10, 12.16, 12.22(a)(b), 12.26, 12.34, 12.38 of Erickson's Algorithms).

Every polynomial-time algorithm on the page is implemented as the page states it and compared with brute force
(exhaustive search over subsets, assignments, colorings, pairings, permutations or arrangements). Every reduction is
implemented as stated, applied to every small instance (all graphs on up to 4-5 vertices, all or many random formulas),
and its output is solved by brute force: the check is that the built instance is a YES instance exactly when the
input instance is (YES -> YES and NO -> NO). Where the page's constant is large (12 colors, 17 vertices, 374 edges,
31337 edges, ...) the same construction is also run with small values of the constant; the 12-color and 12-literal
constructions are also run with the page's constants. Brute-force Hamiltonian-cycle/path searches over subsets are
themselves validated against permutation search first."""
import itertools
import random
import sys
from collections import deque

random.seed(12374)
sys.setrecursionlimit(100000)
FAIL = []


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail != "" else ""))
    if not cond:
        FAIL.append(name)


# ============================================================================ graph helpers
# Undirected simple graph: (n, E) with vertices 0..n-1, E a set of frozenset({u, v}), u != v.
# Directed graph: (n, A) with A a set of pairs (u, v), u != v.

def all_graphs(n):
    pairs = list(itertools.combinations(range(n), 2))
    for bits in range(1 << len(pairs)):
        yield n, {frozenset(pairs[i]) for i in range(len(pairs)) if bits >> i & 1}


def rand_graph(n, p=0.5):
    return n, {frozenset((u, v)) for u, v in itertools.combinations(range(n), 2) if random.random() < p}


def all_digraphs(n):
    pairs = [(u, v) for u in range(n) for v in range(n) if u != v]
    for bits in range(1 << len(pairs)):
        yield n, {pairs[i] for i in range(len(pairs)) if bits >> i & 1}


def rand_digraph(n, p=0.5):
    return n, {(u, v) for u in range(n) for v in range(n) if u != v and random.random() < p}


def adjmask_und(n, E):
    adj = [0] * n
    for e in E:
        u, v = tuple(e)
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    return adj


def adjmask_dir(n, A):
    adj = [0] * n
    for u, v in A:
        adj[u] |= 1 << v
    return adj


def path_dp(n, adj, starts):
    """dp[mask] = bitmask of vertices v such that some simple path starting in `starts` (a bitmask) visits exactly the
    vertices of mask and ends at v."""
    dp = [0] * (1 << n)
    for s in range(n):
        if starts >> s & 1:
            dp[1 << s] |= 1 << s
    for mask in range(1, 1 << n):
        ends = dp[mask]
        if not ends:
            continue
        v = 0
        while ends:
            if ends & 1:
                nxt = adj[v] & ~mask
                w = 0
                while nxt:
                    if nxt & 1:
                        dp[mask | 1 << w] |= 1 << w
                    nxt >>= 1
                    w += 1
            ends >>= 1
            v += 1
    return dp


def ham_cycle_und(n, E):
    """Hamiltonian cycle in a simple undirected graph: needs at least 3 vertices."""
    if n < 3:
        return False
    adj = adjmask_und(n, E)
    dp = path_dp(n, adj, 1)
    ends = dp[(1 << n) - 1]
    return any(ends >> v & 1 and adj[v] & 1 for v in range(n))


def ham_cycle_dir(n, A):
    """Hamiltonian cycle in a directed graph without loops: needs at least 2 vertices."""
    if n < 2:
        return False
    adj = adjmask_dir(n, A)
    dp = path_dp(n, adj, 1)
    ends = dp[(1 << n) - 1]
    return any(ends >> v & 1 and adj[v] & 1 for v in range(n))


def ham_path_und(n, E):
    if n == 0:
        return True
    adj = adjmask_und(n, E)
    return path_dp(n, adj, (1 << n) - 1)[(1 << n) - 1] != 0


def path_sizes_und(n, E):
    """Set of vertex counts of simple paths (a single vertex is a path with 1 vertex)."""
    adj = adjmask_und(n, E)
    dp = path_dp(n, adj, (1 << n) - 1)
    return {bin(m).count("1") for m in range(1, 1 << n) if dp[m]}


# permutation brute force, used only to validate the subset DPs
def perm_ham_cycle_und(n, E):
    if n < 3:
        return False
    return any(all(frozenset((p[i], p[(i + 1) % n])) in E for i in range(n))
               for p in itertools.permutations(range(n)) if p[0] == 0)


def perm_ham_cycle_dir(n, A):
    if n < 2:
        return False
    return any(all((p[i], p[(i + 1) % n]) in A for i in range(n))
               for p in itertools.permutations(range(n)) if p[0] == 0)


def perm_ham_path_und(n, E):
    return any(all(frozenset((p[i], p[i + 1])) in E for i in range(n - 1)) for p in itertools.permutations(range(n)))


def colorable(n, E, k):
    """Brute force over all k^n colorings."""
    El = [tuple(e) for e in E]
    return any(all(c[u] != c[v] for u, v in El) for c in itertools.product(range(k), repeat=n))


def colorable_bt(n, E, k, order=None):
    """Backtracking k-coloring with symmetry breaking (a new vertex may use at most one color not used before)."""
    adj = [set() for _ in range(n)]
    for e in E:
        u, v = tuple(e)
        adj[u].add(v)
        adj[v].add(u)
    order = order or list(range(n))
    col = {}

    def go(i, used):
        if i == len(order):
            return True
        v = order[i]
        for c in range(min(used + 1, k)):
            if all(col.get(w) != c for w in adj[v]):
                col[v] = c
                if go(i + 1, max(used, c + 1)):
                    return True
                del col[v]
        return False
    return go(0, 0)


def alpha(n, E):
    """Independence number by brute force."""
    El = [tuple(e) for e in E]
    best = 0
    for mask in range(1 << n):
        if all(not (mask >> u & 1 and mask >> v & 1) for u, v in El):
            best = max(best, bin(mask).count("1"))
    return best


def min_vc(n, E):
    El = [tuple(e) for e in E]
    for k in range(n + 1):
        for C in itertools.combinations(range(n), k):
            S = set(C)
            if all(u in S or v in S for u, v in El):
                return k
    return n


def is_bipartite_brute(n, E):
    return colorable(n, E, 2)


# ============================================================================ formula helpers
# A literal is (variable index, sign) with sign True for x, False for x-bar. A clause is a tuple of literals.

def lit_val(lit, a):
    v, s = lit
    return a[v] if s else not a[v]


def rand_cnf(N, k, width):
    return [tuple((random.randrange(N), random.random() < 0.5) for _ in range(width)) for _ in range(k)]


def sat_brute(N, clauses):
    return any(all(any(lit_val(l, a) for l in C) for C in clauses) for a in itertools.product([False, True], repeat=N))


def dpll(clauses, assign=None):
    """Small DPLL solver (unit propagation + branching); validated against sat_brute below."""
    assign = dict(assign or {})
    clauses = [list(C) for C in clauses]
    while True:
        new = []
        unit = None
        for C in clauses:
            if any(v in assign and assign[v] == s for v, s in C):
                continue
            rest = [(v, s) for v, s in C if v not in assign]
            if not rest:
                return False
            if len(rest) == 1 and unit is None:
                unit = rest[0]
            new.append(rest)
        clauses = new
        if not clauses:
            return True
        if unit is None:
            break
        assign[unit[0]] = unit[1]
    v = clauses[0][0][0]
    return dpll(clauses, {**assign, v: True}) or dpll(clauses, {**assign, v: False})


# ============================================================================ validate brute-force helpers
bad = 0
for n in range(1, 6):
    for g in all_graphs(n):
        bad += ham_cycle_und(*g) != perm_ham_cycle_und(*g)
        bad += ham_path_und(*g) != perm_ham_path_und(*g)
check("helper: subset-DP Hamiltonian cycle/path == permutation search on all graphs with <= 5 vertices", bad == 0)
bad = 0
for n in range(1, 4):
    for g in all_digraphs(n):
        bad += ham_cycle_dir(*g) != perm_ham_cycle_dir(*g)
for _ in range(300):
    g = rand_digraph(random.randint(4, 6), random.uniform(0.2, 0.6))
    bad += ham_cycle_dir(*g) != perm_ham_cycle_dir(*g)
check("helper: subset-DP directed Hamiltonian cycle == permutation search (all digraphs <= 3 vertices, 300 random)",
      bad == 0)
bad = 0
for _ in range(400):
    N = random.randint(1, 6)
    cl = rand_cnf(N, random.randint(0, 9), random.randint(1, 3))
    bad += dpll(cl) != sat_brute(N, cl)
check("helper: DPLL == truth-table satisfiability on 400 random CNF formulas", bad == 0)
bad = 0
for n in range(1, 6):
    for g in all_graphs(n):
        for k in (1, 2, 3):
            bad += colorable_bt(*g, k) != colorable(*g, k)
check("helper: backtracking k-coloring == brute force on all graphs <= 5 vertices, k = 1, 2, 3", bad == 0)

# ============================================================================ 12.1 Partition in O(nM)


def partition_dp(S):
    """CanReach(i, t): some subset of S[1..i] sums to t, for -M <= t <= M. Answer: total even and CanReach(n, total/2)."""
    n = len(S)
    M = sum(abs(s) for s in S)
    total = sum(S)
    if total % 2:
        return False, (n + 1) * (2 * M + 1)
    off = M
    R = [[False] * (2 * M + 1) for _ in range(n + 1)]
    R[0][off] = True
    for i in range(1, n + 1):          # outer loop: i increasing
        s = S[i - 1]
        for t in range(-M, M + 1):     # inner loop: any order
            r = R[i - 1][t + off]
            if not r and -M <= t - s <= M:
                r = R[i - 1][t - s + off]
            R[i][t + off] = r
    return R[n][total // 2 + off], (n + 1) * (2 * M + 1)


def partition_brute(S):
    n = len(S)
    tot = sum(S)
    return any(2 * sum(S[i] for i in range(n) if mask >> i & 1) == tot for mask in range(1 << n))


bad = cells_ok = 0
for trial in range(1500):
    n = random.randint(0, 9)
    S = random.sample(range(-15, 16), n)
    got, cells = partition_dp(S)
    bad += got != partition_brute(S)
    cells_ok += cells == (n + 1) * (2 * sum(map(abs, S)) + 1)
check("12.1(a) CanReach DP == brute force over all 2^n subsets (1500 random sets of distinct integers in [-15,15])",
      bad == 0)
check("12.1(a) table has (n+1)(2M+1) entries, each O(1): O(nM) time", cells_ok == 1500)
# (b) a family where M is exponential in the input size: n numbers of n bits
for n in (10, 20, 40):
    S = [2 ** (n - 1) + i for i in range(n)]
    bits = sum(x.bit_length() for x in S)
    M = sum(S)
    check(f"12.1(b) n = {n} numbers of n bits: input {bits} bits, but M = {M} >= 2^(n-1)*n",
          bits == n * n and M >= n * 2 ** (n - 1))

# ============================================================================ 12.2 BoxDepth


def rand_rects(n, C=6):
    R = []
    for _ in range(n):
        x1, x2 = sorted(random.randint(0, C) for _ in range(2))
        y1, y2 = sorted(random.randint(0, C) for _ in range(2))
        R.append((x1, x2, y1, y2))
    return R


def contains(r, x, y):
    return r[0] <= x <= r[1] and r[2] <= y <= r[3]


def boxdepth_brute(R, C=6):
    # closed rectangles with integer corners: a nonempty intersection has an integer corner point
    return max([0] + [sum(contains(r, x, y) for r in R) for x in range(C + 1) for y in range(C + 1)])


def boxdepth_cubic(R):
    """Try every point (left edge of i, bottom edge of j); count the rectangles containing it."""
    return max([0] + [sum(contains(r, a[0], b[2]) for r in R) for a in R for b in R])


def intersect(r, s):
    return max(r[0], s[0]) <= min(r[1], s[1]) and max(r[2], s[2]) <= min(r[3], s[3])


def max_clique(n, E):
    best = 0
    for mask in range(1 << n):
        vs = [v for v in range(n) if mask >> v & 1]
        if all(frozenset((u, v)) in E for u, v in itertools.combinations(vs, 2)):
            best = max(best, len(vs))
    return best


bad_b = bad_a = 0
for trial in range(600):
    n = random.randint(0, 9)
    R = rand_rects(n)
    d = boxdepth_brute(R)
    bad_b += boxdepth_cubic(R) != d
    E = {frozenset((i, j)) for i, j in itertools.combinations(range(n), 2) if intersect(R[i], R[j])}
    bad_a += max_clique(n, E) != d
check("12.2(a) largest clique of the intersection graph == BoxDepth (600 random sets of <= 9 closed rectangles)",
      bad_a == 0)
check("12.2(b) the O(n^3) candidate-corner algorithm == brute force over all grid points", bad_b == 0)

# ============================================================================ 12.3 DNF-Sat


def dnf_sat(terms):
    """Satisfiable iff some term contains no variable together with its negation."""
    for T in terms:
        seen = {}
        ok = True
        for v, s in T:
            if seen.get(v, s) != s:
                ok = False
                break
            seen[v] = s
        if ok:
            return True
    return False


def dnf_brute(N, terms):
    return any(any(all(lit_val(l, a) for l in T) for T in terms) for a in itertools.product([False, True], repeat=N))


bad = 0
for trial in range(1500):
    N = random.randint(1, 5)
    terms = [tuple((random.randrange(N), random.random() < 0.5) for _ in range(random.randint(1, 4)))
             for _ in range(random.randint(0, 5))]
    bad += dnf_sat(terms) != dnf_brute(N, terms)
check("12.3(a) 'some term has no complementary pair' == truth table (1500 random DNF formulas)", bad == 0)

# book's example: (x + y + zbar)(xbar + ybar) == x ybar + y xbar + zbar xbar + zbar ybar
x, y, z = 0, 1, 2
lhs = [((x, True), (y, True), (z, False)), ((x, False), (y, False))]
rhs = [((x, True), (y, False)), ((y, True), (x, False)), ((z, False), (x, False)), ((z, False), (y, False))]
eq = all(all(any(lit_val(l, a) for l in C) for C in lhs) == any(all(lit_val(l, a) for l in T) for T in rhs)
         for a in itertools.product([False, True], repeat=3))
check("12.3(b) the book's CNF and DNF example formulas are equivalent", eq)


def distribute(clauses):
    """Distributive law: one term per choice of one literal from every clause."""
    return [tuple(choice) for choice in itertools.product(*clauses)]


for k in (1, 2, 3, 10):
    cl = [((3 * i, True), (3 * i + 1, True), (3 * i + 2, True)) for i in range(k)]
    check(f"12.3(b) distributing {k} disjoint 3-literal clauses gives 3^{k} = {3 ** k} terms",
          len(distribute(cl)) == 3 ** k)
# lower bound: every DNF equivalent to (x1+y1+z1)...(xk+yk+zk) has >= 3^k terms, because no implicant (term that
# implies the formula) is true at two of the 3^k "exactly one true literal per clause" assignments.
for k in (1, 2, 3):
    N = 3 * k
    cl = [((3 * i, True), (3 * i + 1, True), (3 * i + 2, True)) for i in range(k)]
    phi = 0
    for idx, a in enumerate(itertools.product([False, True], repeat=N)):
        if all(any(lit_val(l, a) for l in C) for C in cl):
            phi |= 1 << idx
    allmask = (1 << (1 << N)) - 1
    litmask = {}
    for v in range(N):
        m = 0
        for idx, a in enumerate(itertools.product([False, True], repeat=N)):
            if a[v]:
                m |= 1 << idx
        litmask[(v, True)] = m
        litmask[(v, False)] = allmask ^ m
    minimal = []
    for choice in itertools.product(range(3), repeat=k):
        a = [False] * N
        for i, c in enumerate(choice):
            a[3 * i + c] = True
        minimal.append(int("".join("1" if b else "0" for b in a), 2))
    worst = 0
    for signs in itertools.product((None, True, False), repeat=N):
        m = allmask
        for v, s in enumerate(signs):
            if s is not None:
                m &= litmask[(v, s)]
        if m and m & ~phi & allmask == 0:          # an implicant
            worst = max(worst, sum(m >> idx & 1 for idx in minimal))
    check(f"12.3(b) k = {k}: every implicant covers at most one of the 3^{k} minimal models (so any DNF has >= {3 ** k} terms)",
          worst == 1)

# ============================================================================ 12.4 AllOrNothing3Sat


def aon_sat(N, clauses):
    """Literal graph: vertex (v, s); for each clause l1 l2 l3, edges l1-l2, l2-l3 and the complementary edges.
    Satisfiable iff no x and x-bar lie in the same component (whatever-first search)."""
    adj = {(v, s): [] for v in range(N) for s in (True, False)}

    def comp(l):
        return (l[0], not l[1])
    for C in clauses:
        for a, b in ((C[0], C[1]), (C[1], C[2])):
            for p, q in ((a, b), (comp(a), comp(b))):
                adj[p].append(q)
                adj[q].append(p)
    label = {}
    for start in adj:
        if start in label:
            continue
        label[start] = start
        stack = [start]
        while stack:
            u = stack.pop()
            for w in adj[u]:
                if w not in label:
                    label[w] = start
                    stack.append(w)
    return all(label[(v, True)] != label[(v, False)] for v in range(N))


def aon_brute(N, clauses):
    return any(all(len({lit_val(l, a) for l in C}) == 1 for C in clauses)
               for a in itertools.product([False, True], repeat=N))


bad = 0
for trial in range(2500):
    N = random.randint(1, 6)
    cl = rand_cnf(N, random.randint(0, 7), 3)
    bad += aon_sat(N, cl) != aon_brute(N, cl)
check("12.4(a) components of the literal graph == brute force (2500 random 3CNF formulas)", bad == 0)
ex = [((0, True), (0, False), (1, True))]
check("12.4(b) (x + xbar + y) is satisfiable but not all-or-nothing satisfiable",
      sat_brute(2, ex) and not aon_brute(2, ex) and not aon_sat(2, ex))

# ============================================================================ 12.6 2Partition, 2Color, 2Sat


def two_partition(S):
    a = sorted(S)
    n2 = len(a)
    if n2 == 0:
        return True
    t = a[0] + a[-1]
    return all(a[i] + a[n2 - 1 - i] == t for i in range(n2 // 2))


def two_partition_brute(S):
    S = list(S)

    def go(rest, t):
        if not rest:
            return True
        x = rest[0]
        for j in range(1, len(rest)):
            if t is None or x + rest[j] == t:
                if go(rest[1:j] + rest[j + 1:], x + rest[j]):
                    return True
        return False
    return go(S, None)


bad = 0
yes = 0
for trial in range(3000):
    n = random.randint(0, 4)
    if random.random() < 0.5:
        # plant a YES instance
        t = random.randint(2 * n + 2, 30)
        S = set()
        while len(S) < 2 * n:
            a = random.randint(1, t - 1)
            if a != t - a and a not in S and t - a not in S:
                S |= {a, t - a}
        S = list(S)
    else:
        S = random.sample(range(1, 25), 2 * n)
    r = two_partition_brute(S)
    yes += r
    bad += two_partition(S) != r
check("12.6(a) sort and pair a_i with a_(2n+1-i) == brute force over all pairings (3000 sets of <= 8 numbers)",
      bad == 0, f"{yes} YES instances")


def two_color(n, E):
    adj = [[] for _ in range(n)]
    for e in E:
        u, v = tuple(e)
        adj[u].append(v)
        adj[v].append(u)
    col = [None] * n
    for s in range(n):
        if col[s] is None:
            col[s] = 0
            Q = deque([s])
            while Q:
                u = Q.popleft()
                for w in adj[u]:
                    if col[w] is None:
                        col[w] = 1 - col[u]
                        Q.append(w)
    return all(col[u] != col[v] for u, v in map(tuple, E))


bad = 0
for n in range(1, 7):
    for g in all_graphs(n) if n <= 5 else (rand_graph(6, random.random()) for _ in range(800)):
        bad += two_color(*g) != is_bipartite_brute(*g)
check("12.6(b) search-and-alternate 2-coloring == brute force (all graphs <= 5 vertices, 800 random on 6)", bad == 0)


def scc(nv, adj):
    """Kosaraju: returns comp[v] numbered in topological order of the component dag (sources first)."""
    order, seen = [], [False] * nv
    for s in range(nv):
        if seen[s]:
            continue
        seen[s] = True
        stack = [(s, iter(adj[s]))]
        while stack:
            u, it = stack[-1]
            for w in it:
                if not seen[w]:
                    seen[w] = True
                    stack.append((w, iter(adj[w])))
                    break
            else:
                stack.pop()
                order.append(u)
    radj = [[] for _ in range(nv)]
    for u in range(nv):
        for w in adj[u]:
            radj[w].append(u)
    comp = [-1] * nv
    c = 0
    for s in reversed(order):           # decreasing finish time: components come out in topological order
        if comp[s] != -1:
            continue
        comp[s] = c
        stack = [s]
        while stack:
            u = stack.pop()
            for w in radj[u]:
                if comp[w] == -1:
                    comp[w] = c
                    stack.append(w)
        c += 1
    return comp


def two_sat(N, clauses):
    """Implication graph: literal (v, s) -> index 2v + s. Clause (a + b): edges abar -> b, bbar -> a.
    Unsatisfiable iff some x, xbar share a strong component; else x = True iff comp(x) is later than comp(xbar)."""
    idx = lambda l: 2 * l[0] + (1 if l[1] else 0)
    neg = lambda l: (l[0], not l[1])
    adj = [[] for _ in range(2 * N)]
    for a, b in clauses:
        adj[idx(neg(a))].append(idx(b))
        adj[idx(neg(b))].append(idx(a))
    comp = scc(2 * N, adj)
    if any(comp[2 * v] == comp[2 * v + 1] for v in range(N)):
        return None
    return [comp[2 * v + 1] > comp[2 * v] for v in range(N)]


bad = bad_assign = 0
for trial in range(3000):
    N = random.randint(1, 6)
    cl = rand_cnf(N, random.randint(0, 10), 2)
    a = two_sat(N, cl)
    bad += (a is not None) != sat_brute(N, cl)
    if a is not None:
        bad_assign += not all(any(lit_val(l, a) for l in C) for C in cl)
check("12.6(c) strong components of the implication graph decide 2SAT == truth table (3000 random 2CNF)", bad == 0)
check("12.6(c) the assignment 'x true iff comp(x) after comp(xbar)' satisfies every satisfiable instance",
      bad_assign == 0)

# ============================================================================ 12.7(b) 12Color, (c) 12Sat


def k_color_reduction(n, E, k):
    """G plus a clique on k-3 new vertices, each adjacent to every original vertex."""
    Q = list(range(n, n + k - 3))
    E2 = set(E) | {frozenset(p) for p in itertools.combinations(Q, 2)} | {frozenset((q, v)) for q in Q for v in range(n)}
    return n + k - 3, E2


bad = 0
for k in (4, 5):
    for n in range(1, 6 if k == 4 else 5):
        for g in all_graphs(n):
            bad += colorable(*k_color_reduction(*g, k), k) != colorable(*g, 3)
check("12.7(b) same construction with k = 4, 5 colors (clique of k-3): 3-colorable <=> k-colorable, all small graphs",
      bad == 0)
bad = cnt = 0
for n in range(1, 6):
    for g in all_graphs(n):
        n2, E2 = k_color_reduction(*g, 12)
        bad += colorable_bt(n2, E2, 12, order=list(range(n, n2)) + list(range(n))) != colorable(*g, 3)
        bad += (n2, len(E2)) != (n + 9, len(g[1]) + 36 + 9 * n)
        cnt += 1
check("12.7(b) 12Color: G + K9 joined to every vertex is 12-colorable <=> G is 3-colorable; n+9 vertices, m+36+9n edges",
      bad == 0, f"all {cnt} graphs on <= 5 vertices")


def pad_sat(clauses, K):
    """Pad every clause to exactly K distinct literals with shared new variables y_1, y_2, ... (numbered after the
    originals): a clause with d distinct literals gets y_1..y_(K-d) in all 2^(K-d) sign patterns. Clauses containing a
    complementary pair are always true and are dropped."""
    N = 1 + max([v for C in clauses for v, _ in C], default=-1)
    out = []
    for C in clauses:
        lits = list(dict.fromkeys(C))
        if any((v, not s) in lits for v, s in lits):
            continue
        p = K - len(lits)
        for signs in itertools.product([True, False], repeat=p):
            out.append(tuple(lits) + tuple((N + i, signs[i]) for i in range(p)))
    return out, N + (K - 1)


bad = shape = 0
for trial in range(2500):
    N = random.randint(1, 4)
    cl = rand_cnf(N, random.randint(0, 6), 3)
    for K in (4, 5):
        out, N2 = pad_sat(cl, K)
        bad += sat_brute(N2, out) != sat_brute(N, cl)
        shape += any(len(set(C)) != K or len({v for v, _ in C}) != K for C in out)
check("12.7(c) padding to K = 4, 5 literals: padded formula satisfiable <=> 3CNF satisfiable (2500 random formulas)",
      bad == 0)
check("12.7(c) every padded clause has exactly K literals on K distinct variables", shape == 0)
bad = shape = cnt = 0
yes12 = 0
for trial in range(60):
    N = random.randint(3, 5)
    if trial % 2:
        cl = rand_cnf(N, random.randint(1, 7), 3)
    else:
        cl = [tuple((v, random.random() < 0.5) for v in random.sample(range(N), 3)) for _ in range(random.randint(1, 9))]
    yes12 += sat_brute(N, cl)
    out, N2 = pad_sat(cl, 12)
    bad += dpll(out) != sat_brute(N, cl)
    shape += any(len({v for v, _ in C}) != 12 for C in out)
    full = all(len({v for v, _ in C}) == 3 for C in cl)
    if full:
        cnt += 1
        shape += len(out) != 512 * len(cl)
check("12.7(c) K = 12 (9 padding variables): satisfiable <=> satisfiable, 12 distinct variables per clause, "
      "512 clauses per 3-variable clause", bad == 0 and shape == 0, f"60 random formulas ({yes12} satisfiable), {cnt} with 3 distinct vars per clause")

# ============================================================================ 12.8 directed / undirected Hamiltonian cycle


def und_to_dir(n, E):
    if n < 3:
        return 2, set()                     # fixed NO instance
    return n, {(u, v) for e in E for u, v in (tuple(e), tuple(e)[::-1])}


def dir_to_und(n, A):
    """v -> v_in = 3v, v_mid = 3v+1, v_out = 3v+2; arc u->v -> edge u_out v_in."""
    E = set()
    for v in range(n):
        E |= {frozenset((3 * v, 3 * v + 1)), frozenset((3 * v + 1, 3 * v + 2))}
    for u, v in A:
        E.add(frozenset((3 * u + 2, 3 * v)))
    return 3 * n, E


bad = yes = 0
for n in range(1, 7):
    for g in all_graphs(n) if n <= 5 else (rand_graph(6, random.random()) for _ in range(600)):
        r = ham_cycle_und(*g)
        yes += r
        bad += ham_cycle_dir(*und_to_dir(*g)) != r
check("12.8(a) both orientations of every edge (fixed NO instance if n < 3): directed HC <=> undirected HC",
      bad == 0, f"all graphs <= 5 vertices + 600 random on 6; {yes} YES")
naive = sum(ham_cycle_dir(2, {(0, 1), (1, 0)}) != ham_cycle_und(2, {frozenset((0, 1))}) for _ in [0])
check("12.8(a) without the special case, the one-edge graph K2 (no Hamiltonian cycle) would map to a directed 2-cycle",
      naive == 1)
bad = cnt = yes = 0
for n in range(1, 6):
    gs = all_digraphs(n) if n <= 3 else (rand_digraph(n, random.uniform(0.15, 0.6)) for _ in range(500))
    for g in gs:
        n2, E2 = dir_to_und(*g)
        r = ham_cycle_dir(*g)
        yes += r
        bad += ham_cycle_und(n2, E2) != r
        bad += len(E2) != 2 * n + len(g[1])
        cnt += 1
check("12.8(b) in/mid/out split: undirected HC <=> directed HC; 3n vertices, 2n + m edges", bad == 0,
      f"{cnt} digraphs (all on <= 3 vertices, 500 random each on 4, 5); {yes} YES")

# ============================================================================ 12.10 Hamiltonian path <-> cycle


def path_to_cycle(n, E):
    if n == 1:
        return 3, {frozenset(p) for p in itertools.combinations(range(3), 2)}   # fixed YES instance
    z = n
    return n + 1, set(E) | {frozenset((z, v)) for v in range(n)}


def cycle_to_path(n, E, v=0):
    if n < 3:
        return 2, set()                     # fixed NO instance
    vp, s, t = n, n + 1, n + 2
    E2 = set(E) | {frozenset((vp, u)) for e in E if v in e for u in e if u != v}
    E2 |= {frozenset((s, v)), frozenset((t, vp))}
    return n + 3, E2


bad = 0
for n in range(1, 8):
    gs = all_graphs(n) if n <= 5 else (rand_graph(n, random.uniform(0.2, 0.7)) for _ in range(400))
    for g in gs:
        bad += ham_cycle_und(*path_to_cycle(*g)) != ham_path_und(*g)
check("12.10(a) add a vertex adjacent to everything (fixed YES instance if n = 1): HC <=> HP", bad == 0,
      "all graphs <= 5 vertices, 400 random each on 6, 7")
bad = 0
for n in range(1, 8):
    gs = all_graphs(n) if n <= 5 else (rand_graph(n, random.uniform(0.2, 0.7)) for _ in range(400))
    for g in gs:
        for v in range(n):
            bad += ham_path_und(*cycle_to_path(*g, v)) != ham_cycle_und(*g)
check("12.10(b) copy v to v', pendants s-v and t-v' (fixed NO instance if n < 3): HP <=> HC, for every choice of v",
      bad == 0, "all graphs <= 5 vertices, 400 random each on 6, 7")
# without the n < 3 special case, a single edge (no Hamiltonian cycle) gives s v u v' t
n2 = 2
E2 = {frozenset((0, 1)), frozenset((2, 1)), frozenset((3, 0)), frozenset((4, 2))}
check("12.10(b) without the special case, K2 would map to a graph with Hamiltonian path s v u v' t",
      ham_path_und(5, E2) and not ham_cycle_und(2, {frozenset((0, 1))}))
check("12.10(a) without the n = 1 case, the one-vertex graph (Hamiltonian path) would map to K2 (no Hamiltonian cycle)",
      ham_path_und(1, set()) and not ham_cycle_und(2, {frozenset((0, 1))}))

# ============================================================================ 12.16


def add_isolated(n, E, c):
    return n + c, set(E)


bad = 0
for c in (1, 2, 3):
    for n in range(1, 6):
        for g in all_graphs(n):
            n2, E2 = add_isolated(*g, c)
            sizes = path_sizes_und(n2, E2)
            hp = ham_path_und(*g)
            bad += ((n2 - c) in sizes) != hp                    # visits all but exactly c vertices
            bad += (max(sizes) >= n2 - c) != hp                 # visits all but at most c vertices
check("12.16(a) G + c isolated vertices (c = 1, 2, 3): path missing exactly / at most c vertices <=> Hamiltonian path",
      bad == 0, "all graphs <= 5 vertices")


def spanning_trees(N, E, forced=()):
    """All spanning trees of (N, E) that contain every edge of `forced` (each edge of a degree-1 vertex must be in every
    spanning tree, so forcing them loses nothing). Yields edge lists."""
    forced = list(forced)
    free = [e for e in E if e not in set(forced)]
    need = N - 1 - len(forced)
    if need < 0:
        return
    for sub in itertools.combinations(free, need):
        T = forced + list(sub)
        parent = list(range(N))

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x
        ok = True
        for e in T:
            a, b = (find(u) for u in tuple(e))
            if a == b:
                ok = False
                break
            parent[a] = b
        if ok:
            yield T


def degree_forced(N, E):
    deg = [0] * N
    for e in E:
        for u in e:
            deg[u] += 1
    return [e for e in E if any(deg[u] == 1 for u in e)]


def degrees(N, T):
    deg = [0] * N
    for e in T:
        for u in e:
            deg[u] += 1
    return deg


def pendants_each(n, E, p):
    E2 = set(E)
    N = n
    for v in range(n):
        for _ in range(p):
            E2.add(frozenset((v, N)))
            N += 1
    return N, E2


bad = 0
for D in (2, 3, 4):
    for n in range(1, 6):
        for g in all_graphs(n):
            N2, E2 = pendants_each(*g, D - 2)
            got = any(max(degrees(N2, T)) <= D for T in spanning_trees(N2, list(E2), degree_forced(N2, E2))) \
                if N2 > 1 else True
            bad += got != ham_path_und(*g)
check("12.16(b) D-2 pendant leaves at every vertex (D = 2, 3, 4): spanning tree of max degree <= D <=> Hamiltonian path",
      bad == 0, "all graphs <= 5 vertices")
n2, _ = pendants_each(3, set(), 21)
check("12.16(b) with D = 23: 21 pendants per vertex, 22n vertices", n2 == 22 * 3)


def apex_with_pendants(n, E, L):
    z = n
    E2 = set(E) | {frozenset((z, v)) for v in range(n)}
    N = n + 1
    for _ in range(L - 1):
        E2.add(frozenset((z, N)))
        N += 1
    return N, E2


bad = 0
for L in (2, 3, 4):
    for n in range(1, 6):
        for g in all_graphs(n):
            N2, E2 = apex_with_pendants(*g, L)
            leaves = [sum(d == 1 for d in degrees(N2, T)) for T in spanning_trees(N2, list(E2), degree_forced(N2, E2))]
            bad += (min(leaves) <= L) != ham_path_und(*g)
check("12.16(c) apex z adjacent to all + L-1 pendants on z (L = 2, 3, 4): spanning tree with <= L leaves <=> HP",
      bad == 0, "all graphs <= 5 vertices")


def add_matching(n, E, c):
    return n + 2 * c, set(E) | {frozenset((n + 2 * i, n + 2 * i + 1)) for i in range(c)}


def max_sparse_set(N, E, c):
    """Largest S with at most c edges inside S."""
    El = [tuple(e) for e in E]
    best = 0
    for mask in range(1 << N):
        if sum(1 for u, v in El if mask >> u & 1 and mask >> v & 1) <= c:
            best = max(best, bin(mask).count("1"))
    return best


bad = 0
for c in (0, 1, 2, 3):
    for n in range(1, 6 if c < 3 else 5):
        for g in all_graphs(n):
            bad += max_sparse_set(*add_matching(*g, c), c) != alpha(*g) + 2 * c
check("12.16(d) G + c disjoint edges (c = 0..3): largest set with <= c inside edges == alpha(G) + 2c", bad == 0,
      "all graphs <= 5 vertices (<= 4 for c = 3)")


def attach_cliques(n, E, d):
    E2 = set(E)
    N = n
    for v in range(n):
        Q = list(range(N, N + d))
        N += d
        E2 |= {frozenset(p) for p in itertools.combinations(Q, 2)} | {frozenset((v, q)) for q in Q}
    return N, E2


def max_degree_bounded_set(N, E, d):
    """Largest S in which every vertex has at most d neighbors in S."""
    adj = adjmask_und(N, E)
    best = 0
    for mask in range(1 << N):
        if all(bin(adj[v] & mask).count("1") <= d for v in range(N) if mask >> v & 1):
            best = max(best, bin(mask).count("1"))
    return best


bad = 0
for d in (1, 2, 3):
    for n in range(1, 6 if d == 1 else (5 if d == 2 else 4)):
        for g in all_graphs(n):
            bad += max_degree_bounded_set(*attach_cliques(*g, d), d) != d * n + alpha(*g)
check("12.16(e) a d-clique joined to each vertex (d = 1, 2, 3): largest set with <= d neighbors inside == dn + alpha(G)",
      bad == 0, "all graphs <= 5 / 4 / 3 vertices")


def add_k4s(n, E, c):
    E2 = set(E)
    for i in range(c):
        Q = range(n + 4 * i, n + 4 * i + 4)
        E2 |= {frozenset(p) for p in itertools.combinations(Q, 2)}
    return n + 4 * c, E2


def min_mono(N, E):
    El = [tuple(e) for e in E]
    return min(sum(col[u] == col[v] for u, v in El) for col in itertools.product(range(3), repeat=N))


bad = 0
cnt = 0
for c in (1, 2):
    gs = []
    if c == 1:
        for n in range(1, 5):
            gs += list(all_graphs(n))
        gs += [rand_graph(5, random.uniform(0.3, 0.9)) for _ in range(50)]
    else:
        for n in range(1, 4):
            gs += list(all_graphs(n))
    for g in gs:
        bad += (min_mono(*add_k4s(*g, c)) <= c) != colorable(*g, 3)
        cnt += 1
check("12.16(f) G + c disjoint K4 (c = 1, 2): 3-coloring with <= c monochromatic edges <=> G 3-colorable",
      bad == 0, f"{cnt} graphs")
check("12.16(f) K4 alone: every 3-coloring has >= 1 monochromatic edge, and some has exactly 1",
      min_mono(*add_k4s(0, set(), 1)) == 1)

# ============================================================================ 12.22 dominos


def domino_arrangeable_all(D):
    """Exhaustive search: can all dominos of the bag D be lined up (each used once, either way round)?"""
    m = len(D)
    if m == 0:
        return True

    def go(used, end):
        if used == (1 << m) - 1:
            return True
        tried = set()
        for i in range(m):
            if not used >> i & 1 and D[i] not in tried:
                tried.add(D[i])
                a, b = D[i]
                if a == end and go(used | 1 << i, b):
                    return True
                if b == end and a != b and go(used | 1 << i, a):
                    return True
        return False
    for i in range(m):
        a, b = D[i]
        if go(1 << i, b) or go(1 << i, a):
            return True
    return False


def euler_test(D):
    """Edges = dominos (a double is a loop, adding 2 to the degree). Yes iff no dominos, or all dominos in one
    connected component and 0 or 2 labels of odd degree."""
    if not D:
        return True
    deg = {}
    adj = {}
    for a, b in D:
        deg[a] = deg.get(a, 0) + 1
        deg[b] = deg.get(b, 0) + 1
        adj.setdefault(a, set()).add(b)
        adj.setdefault(b, set()).add(a)
    start = D[0][0]
    seen = {start}
    stack = [start]
    while stack:
        u = stack.pop()
        for w in adj[u]:
            if w not in seen:
                seen.add(w)
                stack.append(w)
    return len(seen) == len(adj) and sum(d % 2 for d in deg.values()) in (0, 2)


bad = yes = 0
for trial in range(2500):
    m = random.randint(0, 7)
    L = random.randint(1, 5)
    D = [tuple(sorted((random.randint(0, L), random.randint(0, L)))) for _ in range(m)]
    r = domino_arrangeable_all(D)
    yes += r
    bad += euler_test(D) != r
check("12.22(a) Euler-trail test (connected + 0 or 2 odd labels) == exhaustive search (2500 random bags of <= 7)",
      bad == 0, f"{yes} YES")


def domino_twice(D, n):
    """Exhaustive search: a legal arrangement of some dominos from D (each at most once) in which every integer 1..n
    appears exactly twice (and no other integer appears)."""
    m = len(D)

    def ok(cnt):
        return all(cnt.get(x, 0) == 2 for x in range(1, n + 1)) and set(cnt) <= set(range(1, n + 1))

    def go(used, end, cnt):
        if ok(cnt):
            return True
        for i in range(m):
            if used >> i & 1:
                continue
            a, b = D[i]
            for p, q in ((a, b), (b, a)) if a != b else ((a, b),):
                if p == end:
                    c2 = dict(cnt)
                    c2[p] = c2.get(p, 0) + 1
                    c2[q] = c2.get(q, 0) + 1
                    if max(c2.values()) <= 2 and go(used | 1 << i, q, c2):
                        return True
        return False
    if ok({}):
        return True
    for i in range(m):
        a, b = D[i]
        for p, q in ((a, b), (b, a)):
            c = {p: 1}
            c[q] = c.get(q, 0) + 1
            if max(c.values()) <= 2 and go(1 << i, q, c):
                return True
    return False


def hc_to_dominos(n, E):
    if n < 3:
        return [], 1                       # fixed NO instance: no dominos, n = 1
    return [tuple(sorted((u + 1, v + 1))) for u, v in map(tuple, E)], n


bad = yes = 0
for n in range(1, 6):
    for g in all_graphs(n):
        D, n2 = hc_to_dominos(*g)
        r = ham_cycle_und(*g)
        yes += r
        bad += domino_twice(D, n2) != r
check("12.22(b) one domino [u|v] per edge (fixed NO instance if n < 3): 'every label twice' <=> Hamiltonian cycle",
      bad == 0, f"all graphs <= 5 vertices; {yes} YES")
plain_small = [domino_twice([tuple(sorted((u + 1, v + 1))) for u, v in map(tuple, g[1])], g[0])
               for n in (1, 2) for g in all_graphs(n)]
check("12.22(b) the n <= 2 case only shortens the proof: without it, every graph with n <= 2 (at most one domino) "
      "already maps to a NO instance, e.g. K2 gives {[1|2]}, which shows 1 and 2 once",
      plain_small == [False, False, False] and not domino_twice([(1, 2)], 2) and domino_twice([(1, 2), (1, 2)], 2))

# ============================================================================ 12.26 DominatingSet from VertexCover


def vc_to_ds(n, E):
    """Delete isolated vertices; add a vertex w_uv adjacent to u and v for every edge."""
    used = sorted({u for e in E for u in e})
    ren = {v: i for i, v in enumerate(used)}
    n0 = len(used)
    E2 = {frozenset((ren[u], ren[v])) for u, v in map(tuple, E)}
    N = n0
    for u, v in map(tuple, E):
        E2 |= {frozenset((N, ren[u])), frozenset((N, ren[v]))}
        N += 1
    return N, E2


def min_ds(N, E):
    adj = adjmask_und(N, E)
    closed = [adj[v] | 1 << v for v in range(N)]
    full = (1 << N) - 1
    for k in range(N + 1):
        for C in itertools.combinations(range(N), k):
            m = 0
            for v in C:
                m |= closed[v]
            if m == full:
                return k
    return N


bad = 0
cnt = 0
for n in range(1, 7):
    gs = all_graphs(n) if n <= 5 else (rand_graph(6, random.uniform(0.2, 0.6)) for _ in range(300))
    for g in gs:
        N2, E2 = vc_to_ds(*g)
        a, b = min_vc(*g), min_ds(N2, E2)
        for k in range(n + 1):
            bad += (a <= k) != (b <= k)
        bad += (N2, len(E2)) != (len({u for e in g[1] for u in e}) + len(g[1]), 3 * len(g[1]))
        cnt += 1
check("12.26 G (isolated vertices deleted) + w_uv per edge: vertex cover <= k <=> dominating set <= k, for every k",
      bad == 0, f"{cnt} graphs; n0 + m vertices, 3m edges")


def vc_to_ds_keep(n, E):
    """Trap variant: keep the isolated vertices, add w_uv per edge."""
    E2 = set(E)
    N = n
    for u, v in map(tuple, E):
        E2 |= {frozenset((N, u)), frozenset((N, v))}
        N += 1
    return N, E2


broken = bad = 0
for n in range(1, 6):
    for g in all_graphs(n):
        N2, E2 = vc_to_ds_keep(*g)
        iso = n - len({u for e in g[1] for u in e})
        a, b = min_vc(*g), min_ds(N2, E2)
        for k in range(n + 1):
            broken += (a <= k) != (b <= k)
            bad += (a <= k) != (b <= k + iso)
check("12.26 trap: keeping isolated vertices breaks the reduction (some graph and k), keeping them and raising k by "
      "their number works (all graphs <= 5 vertices, every k)", broken > 0 and bad == 0, f"{broken} broken pairs")

# ============================================================================ 12.34 red/blue stones


def sat_to_stones(N, clauses):
    """Rows = clauses (those without a complementary pair), columns = variables; red at (i, j) if x_j in C_i,
    blue if xbar_j in C_i."""
    rows = []
    for C in clauses:
        if any((v, not s) in C for v, s in C):
            continue
        row = {}
        for v, s in C:
            row[v] = "R" if s else "B"
        rows.append(row)
    return rows, N


def stones_brute(rows, N):
    """Exhaustive search over all subsets of stones to keep."""
    stones = [(i, j, c) for i, row in enumerate(rows) for j, c in row.items()]
    for mask in range(1 << len(stones)):
        kept = [stones[t] for t in range(len(stones)) if mask >> t & 1]
        if all(any(i == r for i, _, _ in kept) for r in range(len(rows))) and \
                all(len({c for _, j, c in kept if j == col}) <= 1 for col in range(N)):
            return True
    return False


bad = cnt = yes = 0
for trial in range(1500):
    N = random.randint(1, 4)
    k = random.randint(0, 4)
    cl = rand_cnf(N, k, 3)
    rows, N2 = sat_to_stones(N, cl)
    if sum(len(r) for r in rows) > 12:
        continue
    cnt += 1
    r = sat_brute(N, cl)
    yes += r
    bad += stones_brute(rows, N2) != r
check("12.34 grid with red/blue stones per positive/negative literal: solvable <=> satisfiable", bad == 0,
      f"{cnt} random 3CNF formulas ({yes} satisfiable), every subset of stones tried")

# ============================================================================ 12.38 Three-Way Mumbletypeg


def color_to_teams(n, E):
    """G plus a disjoint triangle; the party's acquaintance graph is the complement."""
    T = {frozenset(p) for p in itertools.combinations(range(n, n + 3), 2)}
    Gp = set(E) | T
    N = n + 3
    return N, {frozenset(p) for p in itertools.combinations(range(N), 2) if frozenset(p) not in Gp}


def teams_brute(N, K):
    """Split everyone into three nonempty teams in which everybody knows everybody."""
    for lab in itertools.product(range(3), repeat=N):
        if len(set(lab)) < 3:
            continue
        if all(frozenset((u, v)) in K for u, v in itertools.combinations(range(N), 2) if lab[u] == lab[v]):
            return True
    return False


bad = yes = 0
for n in range(1, 6):
    for g in all_graphs(n):
        r = colorable(*g, 3)
        yes += r
        bad += teams_brute(*color_to_teams(*g)) != r
check("12.38 complement of (G + triangle): three nonempty cliques <=> G 3-colorable", bad == 0,
      f"all graphs <= 5 vertices; {yes} YES")
# the triangle is needed: without it, a single vertex (3-colorable) cannot be split into three nonempty teams
check("12.38 without the triangle, the one-vertex graph would map to a NO instance", not teams_brute(1, set()))
bad_small = bad_big = 0
for n in range(1, 6):
    for g in all_graphs(n):
        comp = {frozenset(p) for p in itertools.combinations(range(n), 2) if frozenset(p) not in g[1]}
        r = teams_brute(n, comp) == colorable(*g, 3)
        if n < 3:
            bad_small += r          # should always disagree
        else:
            bad_big += not r        # should always agree
check("12.38 without the triangle the plain complement fails exactly on the graphs with < 3 vertices",
      bad_small == 0 and bad_big == 0)

# ============================================================================ the figures' examples
# 12.8(b): a -> b, b -> c, c -> a, a -> c
A8 = {(0, 1), (1, 2), (2, 0), (0, 2)}
n8, E8 = dir_to_und(3, A8)
check("figure 12.8(b): the directed example has a Hamiltonian cycle and so does its 9-vertex image",
      ham_cycle_dir(3, A8) and ham_cycle_und(n8, E8) and n8 == 9)
# 12.10(b): v a b c d with the 5-cycle and the chord a c; v = vertex 0
G10 = (5, {frozenset(e) for e in [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0), (1, 3)]})
n10, E10 = cycle_to_path(*G10, 0)
check("figure 12.10(b): G has a Hamiltonian cycle, G' (8 vertices) a Hamiltonian path",
      ham_cycle_und(*G10) and ham_path_und(n10, E10) and n10 == 8)
# 12.26: u v w x, edges uv uw vw wx
G26 = (4, {frozenset(e) for e in [(0, 1), (0, 2), (1, 2), (2, 3)]})
N26, E26 = vc_to_ds(*G26)
check("figure 12.26: smallest vertex cover 2, smallest dominating set of G' 2, G' has 4 + 4 vertices",
      min_vc(*G26) == 2 and min_ds(N26, E26) == 2 and N26 == 8)
# 12.34: the chapter's formula (a + b + c)(b + cbar + dbar)(abar + c + d)(a + bbar + dbar), a = c = T, b = d = F
F34 = [((0, True), (1, True), (2, True)), ((1, True), (2, False), (3, False)), ((0, False), (2, True), (3, True)),
       ((0, True), (1, False), (3, False))]
a34 = (True, False, True, False)
rows34, _ = sat_to_stones(4, F34)
kept = [{j: c for j, c in row.items() if (c == "R") == a34[j]} for row in rows34]
check("figure 12.34: the assignment satisfies the formula and leaves a stone in every row, one color per column",
      all(any(lit_val(l, a34) for l in C) for C in F34) and all(kept) and
      all(len({k[j] for k in kept if j in k}) <= 1 for j in range(4)) and stones_brute(rows34, 4))

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: " + "; ".join(FAIL))
