#!/usr/bin/env python3
"""Checks for the Chapter 12 concept pages independent-set, graph-coloring and hamiltonian-cycle.

Every reduction is implemented exactly as the page states it and checked by brute force: YES -> YES and NO -> NO on
every formula/graph of a small family plus many random ones (satisfiability by trying all assignments, independent
sets, cliques and vertex covers by trying all subsets, colorings by backtracking over all color choices, Hamiltonian
cycles by exhaustive depth-first search). The counts of vertices and edges stated on the pages, the clause-gadget
truth table, the half-gadget ("majority") behavior, the tree dynamic program, the complement relations, the
two-coloring algorithm, the counterexample to the book's 3SAT -> directed Hamiltonian cycle construction, the
book's vertex-cover construction (with its edge cases), directed -> undirected Hamiltonian cycle, and every number in
the three examples are recomputed and compared with the pages."""
import itertools
import os
import random
import re
import sys
from collections import deque

sys.setrecursionlimit(20000)
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
CONCEPTS = os.path.join(ROOT, "content", "concepts")
FAIL = []
random.seed(12374)


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAIL.append(name)


def read(path):
    return open(path, encoding="utf-8").read()


# =====================================================================================================
# Formulas: a 3CNF formula over variables 1..n is a list of clauses, each a tuple of three nonzero ints
# (+i = x_i, -i = not x_i). Repeated variables inside a clause are allowed (the reductions must survive them).
def satisfies(bits, clauses):
    return all(any(bits[abs(l) - 1] == (l > 0) for l in cl) for cl in clauses)


def sat_assignments(n, clauses):
    return [bits for bits in itertools.product([False, True], repeat=n) if satisfies(bits, clauses)]


def rand_formula(n, k, distinct=False, rng=random):
    cls = []
    for _ in range(k):
        vs = rng.sample(range(1, n + 1), 3) if (distinct and n >= 3) else [rng.randint(1, n) for _ in range(3)]
        cls.append(tuple(v if rng.random() < 0.5 else -v for v in vs))
    return cls


def all_formulas(n, k):
    lits = [l for v in range(1, n + 1) for l in (v, -v)]
    clauses = list(itertools.product(lits, repeat=3))
    return itertools.product(clauses, repeat=k)


# small family used for every 3SAT reduction: all formulas with n = 1, k <= 2 and n = 2, k <= 2, and random ones
SMALL = [list(f) for n_, k_ in ((1, 1), (1, 2), (2, 1), (2, 2)) for f in all_formulas(n_, k_)]


def formula_n(f):
    return max(abs(l) for cl in f for l in cl)


# =====================================================================================================
# Undirected graphs: (V list, set of frozenset edges)
def complement(V, E):
    return V, {frozenset((u, v)) for u, v in itertools.combinations(V, 2)} - E


def is_independent(S, E):
    return all(frozenset((u, v)) not in E for u, v in itertools.combinations(S, 2))


def is_clique(S, E):
    return all(frozenset((u, v)) in E for u, v in itertools.combinations(S, 2))


def is_vertex_cover(C, E):
    return all(e & C for e in E)


def max_is(V, E):
    for r in range(len(V), -1, -1):
        if any(is_independent(S, E) for S in itertools.combinations(V, r)):
            return r


def has_is(V, E, k):
    return any(is_independent(S, E) for S in itertools.combinations(V, k)) if 0 <= k <= len(V) else k <= 0


def max_clique(V, E):
    for r in range(len(V), -1, -1):
        if any(is_clique(S, E) for S in itertools.combinations(V, r)):
            return r


def min_vc(V, E):
    for r in range(len(V) + 1):
        if any(is_vertex_cover(set(S), E) for S in itertools.combinations(V, r)):
            return r


def rand_ugraph(n, p, rng=random):
    V = list(range(n))
    return V, {frozenset((u, v)) for u, v in itertools.combinations(V, 2) if rng.random() < p}


def all_ugraphs(n):
    V = list(range(n))
    pairs = list(itertools.combinations(V, 2))
    for mask in range(1 << len(pairs)):
        yield V, {frozenset(pairs[i]) for i in range(len(pairs)) if mask >> i & 1}


# =====================================================================================================
print("== independent-set: 3SAT -> IndependentSet (Section 12.7), as stated on the page")


def sat_to_is(clauses):
    """One vertex (j, t) per literal occurrence; triangle per clause; edge between x and not-x occurrences.
    Returns (V, E, k) with k = number of clauses."""
    V = [(j, t) for j in range(len(clauses)) for t in range(3)]
    lit = {(j, t): clauses[j][t] for (j, t) in V}
    E = set()
    for u, v in itertools.combinations(V, 2):
        if u[0] == v[0] or lit[u] == -lit[v]:
            E.add(frozenset((u, v)))
    return V, E, len(clauses)


def check_sat_is(formulas, label):
    bad = 0
    yes = no = 0
    for f in formulas:
        n = formula_n(f)
        V, E, k = sat_to_is(f)
        s = bool(sat_assignments(n, f))
        g = has_is(V, E, k)
        yes += s
        no += not s
        bad += s != g
        # size bound: no independent set larger than k (at most one vertex per triangle)
        if has_is(V, E, k + 1):
            bad += 1
    check(f"3SAT -> IndependentSet: Phi satisfiable <=> G has an independent set of size k, and none of size k+1 ({label})",
          bad == 0, f"{yes} YES, {no} NO, {bad} bad")


check_sat_is(SMALL, f"all {len(SMALL)} formulas with n <= 2 variables, k <= 2 clauses")
RAND_F = [rand_formula(random.randint(1, 4), random.randint(1, 4), distinct=random.random() < 0.5) for _ in range(1500)]
check_sat_is(RAND_F, "1500 random formulas, n <= 4, k <= 4")
# an unsatisfiable family with distinct variables in each clause: all 8 clauses on 3 variables (12 vertices... 24)
ALL8 = [tuple(s * v for s, v in zip(signs, (1, 2, 3))) for signs in itertools.product([1, -1], repeat=3)]
V8, E8, k8 = sat_to_is(ALL8)
best8 = 0
for r in range(k8, 0, -1):
    if has_is(V8, E8, r):
        best8 = r
        break
check("  ... largest independent set of the 24-vertex graph is 7 (every 7 of the 8 clauses are satisfiable)",
      best8 == 7 and not sat_assignments(3, ALL8), str(best8))

# sizes: 3k vertices; triangle edges 3k when the 3 literals of a clause are distinct occurrences (always, since vertices
# are occurrences); conflict edges = pairs of complementary occurrences in different clauses (complementary pairs inside a
# clause coincide with triangle edges)
ok = True
for f in RAND_F[:300]:
    V, E, k = sat_to_is(f)
    occ = [(j, t, f[j][t]) for j in range(k) for t in range(3)]
    conf = sum(1 for (j1, t1, l1), (j2, t2, l2) in itertools.combinations(occ, 2) if j1 != j2 and l1 == -l2)
    ok &= len(V) == 3 * k and len(E) == 3 * k + conf
check("  ... sizes: 3k vertices and 3k + (complementary pairs in different clauses) edges", ok)

print("== independent-set: complements (Section 12.9)")
ok_sets = ok_vals = True
cnt = 0
for n in range(0, 6):
    for V, E in all_ugraphs(n):
        cnt += 1
        Vb, Eb = complement(V, E)
        for r in range(n + 1):
            for S in itertools.combinations(V, r):
                a = is_independent(S, E)
                b = is_clique(S, Eb)
                c = is_vertex_cover(set(V) - set(S), E)
                ok_sets &= a == b == c
        ok_vals &= max_is(V, E) == max_clique(Vb, Eb) == n - min_vc(V, E)
for _ in range(300):
    n = random.randint(6, 9)
    V, E = rand_ugraph(n, random.random())
    Vb, Eb = complement(V, E)
    ok_vals &= max_is(V, E) == max_clique(Vb, Eb) == n - min_vc(V, E)
check(f"S independent in G <=> S clique in complement(G) <=> V - S vertex cover of G (all {cnt} graphs on <= 5 vertices, every S)",
      ok_sets)
check("MaxIndSet(G) = MaxClique(complement G) = n - MinVertexCover(G) (all graphs <= 5 vertices + 300 random on 6..9)", ok_vals)
ok = True
for n in range(0, 6):
    for V, E in all_ugraphs(n):
        Vb, Eb = complement(V, E)
        mi, mc, mv = max_is(V, E), max_clique(Vb, Eb), min_vc(V, E)
        for k in range(0, n + 1):
            yes_is = mi >= k
            ok &= yes_is == (mc >= k)                # (G, k) -> (complement G, k): Clique
            ok &= yes_is == (mv <= n - k)            # (G, k) -> (G, n - k): VertexCover
            ok &= (mv <= k) == (mi >= n - k)         # VertexCover -> IndependentSet, same map backwards
            # "at least k" = "exactly k" for independent sets and cliques; "at most k" = "exactly k" for covers
            ok &= yes_is == has_is(V, E, k)
            ok &= (mv <= k) == any(is_vertex_cover(set(S), E) for S in itertools.combinations(V, k))
check("decision maps (G,k) -> (complement G, k) and (G,k) -> (G, n-k): YES <-> YES for every k (all graphs <= 5 vertices); "
      "'size >= k' = 'size exactly k' for IS, 'size <= k' = 'exactly k' for VC", ok)

print("== independent-set: tree dynamic program (link to dynamic-programming-on-trees)")


def tree_mis(n, parent):
    kids = {v: [] for v in range(n)}
    for v in range(1, n):
        kids[parent[v]].append(v)
    yes, no = {}, {}
    for v in reversed(range(n)):          # parent[v] < v, so reverse order is a post-order
        yes[v] = 1 + sum(no[w] for w in kids[v])
        no[v] = sum(max(yes[w], no[w]) for w in kids[v])
    return max(yes[0], no[0])


ok = True
for _ in range(400):
    n = random.randint(1, 11)
    parent = [None] + [random.randrange(v) for v in range(1, n)]
    V = list(range(n))
    E = {frozenset((v, parent[v])) for v in range(1, n)}
    ok &= tree_mis(n, parent) == max_is(V, E)
check("tree MIS dynamic program (MISyes/MISno, post-order) = brute force on 400 random trees with <= 11 vertices", ok)

print("== independent-set: the example")
# (a or b or c) and (not a or not b or c) and (a or not b or not c)   a=1, b=2, c=3
EX_IS = [(1, 2, 3), (-1, -2, 3), (1, -2, -3)]
V, E, k = sat_to_is(EX_IS)
tri = [e for e in E if len({v[0] for v in e}) == 1]
conf = [e for e in E if len({v[0] for v in e}) == 2]
NAME = {1: "a", 2: "b", 3: "c", -1: "ā", -2: "b̄", -3: "c̄"}
conf_named = sorted(tuple(sorted(f"{NAME[EX_IS[j][t]]}{j + 1}" for (j, t) in e)) for e in conf)
check("example: 9 vertices, 9 triangle edges, 6 conflict edges, 15 edges",
      len(V) == 9 and len(tri) == 9 and len(conf) == 6 and len(E) == 15, str(conf_named))
check("example: conflict edges a1-ā2, b1-b̄2, b1-b̄3, c1-c̄3, ā2-a3, c2-c̄3",
      conf_named == sorted(tuple(sorted(p)) for p in [("a1", "ā2"), ("b1", "b̄2"), ("b1", "b̄3"), ("c1", "c̄3"),
                                                       ("ā2", "a3"), ("c2", "c̄3")]), str(conf_named))
S_ex = [(0, 0), (1, 2), (2, 1)]   # a in clause 1, c in clause 2, b̄ in clause 3
assign = {}
for (j, t) in S_ex:
    l = EX_IS[j][t]
    assign[abs(l)] = l > 0
check("example: {a1, c2, b̄3} is independent, gives a = c = True, b = False, which satisfies Phi",
      is_independent(S_ex, E) and assign == {1: True, 3: True, 2: False}
      and satisfies((True, False, True), EX_IS))
sats = sat_assignments(3, EX_IS)
check("example: Phi has 5 satisfying assignments; the 3 falsifying ones are FFF, TTF, FTT (a,b,c)",
      len(sats) == 5 and sorted(set(itertools.product([False, True], repeat=3)) - set(sats))
      == sorted([(False, False, False), (True, True, False), (False, True, True)]), str(len(sats)))
Vb, Eb = complement(V, E)
check("example: MaxIndSet = 3, MinVertexCover = 6, MaxClique(complement) = 3, complement has 36 - 15 = 21 edges",
      max_is(V, E) == 3 and min_vc(V, E) == 6 and max_clique(Vb, Eb) == 3 and len(Eb) == 21)
check("example: the vertex cover V - {a1, c2, b̄3} has 6 vertices and covers all 15 edges",
      is_vertex_cover(set(V) - set(S_ex), E) and len(set(V) - set(S_ex)) == 6)
# figure: same graph
FIG_IS = os.path.join(HERE, "..", "figs", "a12c-is-triangles.html")
if os.path.exists(FIG_IS):
    fig = read(FIG_IS)
    check("figure a12c-is-triangles: caption names the formula, 15 edges and the independent set",
          "15 edges" in fig and "independent set" in fig)

# =====================================================================================================
print("== graph-coloring: 3SAT -> 3Color (Section 12.10), as stated on the page")


def sat_to_3color(n, clauses):
    """Truth triangle T, F, X; variable triangle x_i, not-x_i, X; per clause (l1 v l2 v l3) five new vertices
    u, v, w, y, z and ten edges l1-u, l2-v, u-v, u-w, v-w, w-y, l3-z, y-z, y-T, z-T."""
    V = ["T", "F", "X"]
    E = [("T", "F"), ("F", "X"), ("X", "T")]
    for i in range(1, n + 1):
        V += [i, -i]
        E += [(i, -i), (i, "X"), (-i, "X")]
    for j, (l1, l2, l3) in enumerate(clauses):
        u, v, w, y, z = (("u", j), ("v", j), ("w", j), ("y", j), ("z", j))
        V += [u, v, w, y, z]
        E += [(l1, u), (l2, v), (u, v), (u, w), (v, w), (w, y), (l3, z), (y, z), (y, "T"), (z, "T")]
    return V, E


def colorings(V, E, k, fixed=None, limit=None):
    """All proper k-colorings (as dicts) by backtracking; fixed = partial dict to respect."""
    adj = {v: set() for v in V}
    for a, b in E:
        adj[a].add(b)
        adj[b].add(a)
    order = sorted(V, key=lambda v: -len(adj[v]))
    col = dict(fixed or {})
    out = []

    def bt(i):
        if limit is not None and len(out) >= limit:
            return
        if i == len(order):
            out.append(dict(col))
            return
        v = order[i]
        if v in col:
            if all(col.get(w) != col[v] for w in adj[v]):
                bt(i + 1)
            return
        for c in range(k):
            if all(col.get(w) != c for w in adj[v]):
                col[v] = c
                bt(i + 1)
                del col[v]
    if any(a == b for a, b in E):
        return []
    bt(0)
    return out


def k_colorable(V, E, k):
    return bool(colorings(V, E, k, limit=1))


def check_sat_3col(formulas, label):
    bad = yes = no = 0
    for f in formulas:
        n = formula_n(f)
        V, E = sat_to_3color(n, f)
        s = bool(sat_assignments(n, f))
        g = k_colorable(V, E, 3)
        yes += s
        no += not s
        bad += s != g
        bad += len(V) != 3 + 2 * n + 5 * len(f) or len(E) != 3 + 3 * n + 10 * len(f)
        bad += len(set(map(frozenset, E))) != len(E)
    check(f"3SAT -> 3Color: Phi satisfiable <=> G 3-colorable; 3 + 2n + 5k vertices, 3 + 3n + 10k distinct edges ({label})",
          bad == 0, f"{yes} YES, {no} NO, {bad} bad")


check_sat_3col(SMALL, f"all {len(SMALL)} formulas with n <= 2, k <= 2")
check_sat_3col(RAND_F[:800], "800 random formulas, n <= 4, k <= 4")
# the extraction direction: in every 3-coloring, literal nodes colored like T give a satisfying assignment
ok = True
for f in RAND_F[:150]:
    n = formula_n(f)
    V, E = sat_to_3color(n, f)
    for c in colorings(V, E, 3, limit=40):
        bits = tuple(c[i] == c["T"] for i in range(1, n + 1))
        ok &= all(c[i] in (c["T"], c["F"]) and c[-i] != c[i] for i in range(1, n + 1))
        ok &= satisfies(bits, f)
check("in every 3-coloring (first 40 per graph, 150 formulas): each x_i, not-x_i colored True/False oppositely, "
      "and 'x_i colored like T' satisfies Phi", ok)

print("== graph-coloring: gadgets")
# half-gadget: inputs p, q; triangle a (adj p), b (adj q), o (output)
half_V = ["p", "q", "a", "b", "o"]
half_E = [("p", "a"), ("q", "b"), ("a", "b"), ("a", "o"), ("b", "o")]
ok = True
for cp in range(3):
    for cq in range(3):
        outs = {c["o"] for c in colorings(half_V, half_E, 3, fixed={"p": cp, "q": cq})}
        ok &= outs == ({cp} if cp == cq else {0, 1, 2})
allhalf = colorings(half_V, half_E, 3)
check("half-gadget ('majority gate'): equal inputs force the output to their color; different inputs allow all 3",
      ok)
check("half-gadget has 24 proper 3-colorings = 4 up to permuting the colors (the book's Figure 12.14 draws 5, two of "
      "which differ only by swapping False and Other)", len(allhalf) == 24, str(len(allhalf)))
# clause gadget truth table with T, F, X colored 0, 1, 2 and literal nodes colored True(0)/False(1)
TRUE, FALSE, OTHER = 0, 1, 2
CL_V = ["T", "F", "X", "l1", "l2", "l3", "u", "v", "w", "y", "z"]
CL_E = [("T", "F"), ("F", "X"), ("X", "T"), ("l1", "u"), ("l2", "v"), ("u", "v"), ("u", "w"), ("v", "w"), ("w", "y"),
        ("l3", "z"), ("y", "z"), ("y", "T"), ("z", "T")]
table = {}
for vals in itertools.product([TRUE, FALSE], repeat=3):
    fx = {"T": TRUE, "F": FALSE, "X": OTHER, "l1": vals[0], "l2": vals[1], "l3": vals[2]}
    table[vals] = colorings(CL_V, CL_E, 3, fixed=fx)
check("clause gadget: extends to a 3-coloring for 7 of the 8 True/False colorings of l1, l2, l3; not for all False",
      all(bool(table[v]) == (v != (FALSE, FALSE, FALSE)) for v in table))
ex = table[(FALSE, FALSE, TRUE)]
check("clause-gadget example l1 = l2 = False, l3 = True: exactly 2 extensions; {u, v} = {True, Other}, w = False, "
      "y = Other, z = False",
      len(ex) == 2 and all({c["u"], c["v"]} == {TRUE, OTHER} and c["w"] == FALSE and c["y"] == OTHER
                           and c["z"] == FALSE for c in ex))
# the completion rule stated in the template's "=>" proof
ok = True
for vals in itertools.product([TRUE, FALSE], repeat=3):
    if vals == (FALSE, FALSE, FALSE):
        continue
    l1, l2, l3 = vals
    if TRUE in (l1, l2):
        w = TRUE
        u = OTHER if l1 == FALSE else (FALSE if l2 == FALSE else FALSE)
        v = ({FALSE, OTHER} - {u}).pop()
        if v == l2:                 # each of u, v avoids its literal's color
            u, v = v, u
        z = OTHER if l3 == FALSE else FALSE
        y = ({FALSE, OTHER} - {z}).pop()
    else:
        u, v, w, y, z = TRUE, OTHER, FALSE, OTHER, FALSE
    col = {"T": TRUE, "F": FALSE, "X": OTHER, "l1": l1, "l2": l2, "l3": l3, "u": u, "v": v, "w": w, "y": y, "z": z}
    ok &= all(col[a] != col[b] for a, b in CL_E) and {u, v} <= {FALSE, OTHER, TRUE}
    if TRUE in (l1, l2):
        ok &= {u, v} == {FALSE, OTHER} and {y, z} == {FALSE, OTHER}
check("template '=>' completion rule (w True and {u,v} = {y,z} = {False, Other}, z Other if l3 False; else "
      "True, Other, False, Other, False) is a proper coloring for all 7 satisfying literal colorings", ok)
# all False: w forced False, then y and z both Other
fx = {"T": TRUE, "F": FALSE, "X": OTHER, "l1": FALSE, "l2": FALSE, "l3": FALSE}
partial = colorings([v for v in CL_V], [e for e in CL_E if e != ("y", "z")], 3, fixed=fx)
check("all-False case: without edge yz every coloring has w = False and y = z = Other (so edge yz is violated)",
      partial and all(c["w"] == FALSE and c["y"] == OTHER and c["z"] == OTHER for c in partial))
# the book's formula (Figure 12.15)
BOOK = [(1, 2, 3), (2, -3, -4), (-1, 3, 4), (1, -2, -4)]
V, E = sat_to_3color(4, BOOK)
check("book's 4-clause formula: graph has 31 vertices and 55 edges, is 3-colorable; a = c = True, b = d = False satisfies it",
      len(V) == 31 and len(E) == 55 and k_colorable(V, E, 3) and satisfies((True, False, True, False), BOOK))

print("== graph-coloring: 2Color and kColor")


def two_color(V, E):
    adj = {v: [] for v in V}
    for e in E:
        a, b = tuple(e)
        adj[a].append(b)
        adj[b].append(a)
    col = {}
    for s in V:
        if s in col:
            continue
        col[s] = 0
        Q = deque([s])
        while Q:
            x = Q.popleft()
            for y in adj[x]:
                if y not in col:
                    col[y] = 1 - col[x]
                    Q.append(y)
    return all(col[a] != col[b] for a, b in map(tuple, E))


def has_odd_cycle(V, E):
    # brute force: some closed walk of odd length <= 2n+1 exists iff an odd cycle exists
    adj = {v: set() for v in V}
    for e in E:
        a, b = tuple(e)
        adj[a].add(b)
        adj[b].add(a)
    for s in V:
        reach = {s: {0}}
        frontier = {(s, 0)}
        seen = set(frontier)
        while frontier:
            nxt = set()
            for v, p in frontier:
                for w in adj[v]:
                    st = (w, 1 - p)
                    if st not in seen:
                        seen.add(st)
                        nxt.add(st)
            frontier = nxt
        if (s, 1) in seen:
            return True
    return False


ok = True
cnt = 0
for n in range(0, 6):
    for V, E in all_ugraphs(n):
        cnt += 1
        el = [tuple(e) for e in E]
        b = k_colorable(V, el, 2)
        ok &= two_color(V, E) == b == (not has_odd_cycle(V, E))
for _ in range(400):
    V, E = rand_ugraph(random.randint(6, 10), random.random() * 0.5)
    ok &= two_color(V, E) == k_colorable(V, [tuple(e) for e in E], 2) == (not has_odd_cycle(V, E))
check(f"2Color: alternate colors along a whatever-first search; correct <=> brute force <=> no odd cycle "
      f"(all {cnt} graphs <= 5 vertices + 400 random)", ok)
ok = True
for _ in range(250):
    V, E = rand_ugraph(random.randint(1, 7), random.random())
    el = [tuple(e) for e in E]
    c3 = k_colorable(V, el, 3)
    for kk in (4, 5):
        new = [("new", t) for t in range(kk - 3)]
        V2 = V + new
        E2 = el + [(a, b) for a, b in itertools.combinations(new, 2)] + [(a, v) for a in new for v in V]
        ok &= k_colorable(V2, E2, kk) == c3
check("3Color -> kColor (k = 4, 5): add k - 3 new vertices adjacent to each other and to every old vertex "
      "(250 random graphs)", ok)

# =====================================================================================================
print("== hamiltonian-cycle: helpers")


def ham_count(V, out, limit=None):
    """Number of directed Hamiltonian cycles (each counted once: start fixed at V[0])."""
    N = len(V)
    idx = {v: i for i, v in enumerate(V)}
    O = [sorted({idx[w] for w in out.get(v, ()) if w != v}) for v in V]
    I = [[] for _ in range(N)]
    for u in range(N):
        for w in O[u]:
            I[w].append(u)
    if N == 0:
        return 0
    if N == 1:
        return 0
    vis = [False] * N
    vis[0] = True
    cnt = [0]

    def feasible(cur):
        for v in range(N):
            if not vis[v]:
                if not any((not vis[u]) or u == cur for u in I[v]):
                    return False
                if not any((not vis[w]) or w == 0 for w in O[v]):
                    return False
        return True

    def dfs(cur, depth):
        if limit is not None and cnt[0] >= limit:
            return
        if depth == N:
            if 0 in O[cur]:
                cnt[0] += 1
            return
        if not feasible(cur):
            return
        for w in O[cur]:
            if not vis[w]:
                vis[w] = True
                dfs(w, depth + 1)
                vis[w] = False
    dfs(0, 1)
    return cnt[0]


def is_ham_cycle(V, out, cyc):
    return (len(cyc) == len(V) and set(cyc) == set(V)
            and all(cyc[(t + 1) % len(cyc)] in out.get(cyc[t], ()) for t in range(len(cyc))))


def expected_cycles(n, clauses):
    """Hamiltonian cycles of a correct construction: one per satisfying assignment and per choice, for each clause,
    of one of its (distinct) true literals to visit the clause vertex."""
    tot = 0
    for bits in itertools.product([False, True], repeat=n):
        p = 1
        for cl in clauses:
            p *= len({l for l in cl if bits[abs(l) - 1] == (l > 0)})
        tot += p
    return tot


print("== hamiltonian-cycle: 3SAT -> DirectedHamCycle, as stated on the page (separators and hubs)")


def sat_to_ham(n, clauses):
    """Row i: (i,0..3k), edges both ways between neighbors; hub h_i: h_i -> (i,0), h_i -> (i,3k),
    (i,0) -> h_{i+1}, (i,3k) -> h_{i+1} (h_{n+1} = h_1); clause j at positions 3j-2, 3j-1:
    x_i in c_j: (i,3j-2) -> [j] -> (i,3j-1); not-x_i in c_j: (i,3j-1) -> [j] -> (i,3j-2)."""
    k = len(clauses)
    L = 3 * k
    V, out = [], {}

    def E(a, b):
        out.setdefault(a, set()).add(b)
    for i in range(1, n + 1):
        V.append(("h", i))
        V += [(i, c) for c in range(L + 1)]
        for c in range(1, L + 1):
            E((i, c - 1), (i, c))
            E((i, c), (i, c - 1))
        nxt = ("h", i % n + 1)
        E(("h", i), (i, 0))
        E(("h", i), (i, L))
        E((i, 0), nxt)
        E((i, L), nxt)
    for j, cl in enumerate(clauses, 1):
        V.append(("c", j))
        p, q = 3 * j - 2, 3 * j - 1
        for l in cl:
            i = abs(l)
            if l > 0:
                E((i, p), ("c", j))
                E(("c", j), (i, q))
            else:
                E((i, q), ("c", j))
                E(("c", j), (i, p))
    return V, out


def n_edges(out):
    return sum(len(s - {a}) for a, s in out.items())


def check_sat_ham(formulas, label):
    bad = yes = no = cbad = 0
    for f in formulas:
        n = formula_n(f)
        V, out = sat_to_ham(n, f)
        s = bool(sat_assignments(n, f))
        c = ham_count(V, out)
        yes += s
        no += not s
        bad += (c > 0) != s
        cbad += c != expected_cycles(n, f)
        k = len(f)
        bad += len(V) != n * (3 * k + 2) + k
        if all(len(set(cl)) == 3 for cl in f):
            bad += n_edges(out) != 6 * k * n + 4 * n + 6 * k
    check(f"3SAT -> DirectedHamCycle: Phi satisfiable <=> H Hamiltonian; n(3k+2)+k vertices, 6kn+4n+6k edges ({label})",
          bad == 0, f"{yes} YES, {no} NO, {bad} bad")
    check(f"  ... and H has exactly sum over satisfying assignments of prod_j (#true literals of c_j) Hamiltonian "
          f"cycles, so no cycle 'cheats' ({label})", cbad == 0, f"{cbad} mismatches")


SMALL_H = [f for f in SMALL if len(f) <= 2 and formula_n(f) <= 2]
check_sat_ham(SMALL_H[:: 7] + [f for f in SMALL if formula_n(f) == 1], f"{len(SMALL_H[::7]) + sum(1 for f in SMALL if formula_n(f) == 1)} formulas with n <= 2, k <= 2")
RAND_H = [rand_formula(random.randint(1, 3), random.randint(1, 3), distinct=random.random() < 0.5) for _ in range(500)]
check_sat_ham(RAND_H, "500 random formulas, n <= 3, k <= 3")
UNSAT_H = [f for f in SMALL if not sat_assignments(formula_n(f), f)]
rng = random.Random(4)
while len(UNSAT_H) < 40:
    f = rand_formula(rng.randint(1, 3), rng.randint(2, 4), rng=rng)
    if not sat_assignments(formula_n(f), f):
        UNSAT_H.append(f)
check_sat_ham(UNSAT_H, f"{len(UNSAT_H)} unsatisfiable formulas, n <= 3, k <= 4")

print("== hamiltonian-cycle: the book's construction (Section 12.11, 'From 3SAT') is not correct")


def book_sat_to_ham(n, clauses, figure=False):
    """Text: rows (i,0..2k); figure: rows (i,1..2k). Row ends joined directly:
    (i,a) -> (i+1,b) for a, b in {first, last}; clause j at 2j-1, 2j."""
    k = len(clauses)
    cols = list(range(1, 2 * k + 1)) if figure else list(range(0, 2 * k + 1))
    first, last = cols[0], cols[-1]
    V, out = [], {}

    def E(a, b):
        if a != b:
            out.setdefault(a, set()).add(b)
    for i in range(1, n + 1):
        V += [(i, c) for c in cols]
        for a, b in zip(cols, cols[1:]):
            E((i, a), (i, b))
            E((i, b), (i, a))
        for a in (first, last):
            for b in (first, last):
                E((i, a), (i % n + 1, b))
    for j, cl in enumerate(clauses, 1):
        V.append(("c", j))
        for l in cl:
            i = abs(l)
            if l > 0:
                E((i, 2 * j - 1), ("c", j))
                E(("c", j), (i, 2 * j))
            else:
                E((i, 2 * j), ("c", j))
                E(("c", j), (i, 2 * j - 1))
    return V, out, cols


# the counterexample: all eight clauses on a, b, c, with (not a or b or c) last; assignment a = True, b = c = False
CE = [c for c in ALL8 if c != (-1, 2, 3)] + [(-1, 2, 3)]
bits = (True, False, False)
check("counterexample formula (all 8 clauses over a, b, c) is unsatisfiable, and a=T, b=c=F falsifies only "
      "(ā ∨ b ∨ c), the last clause",
      not sat_assignments(3, CE) and [cl for cl in CE if not satisfies(bits, [cl])] == [(-1, 2, 3)])
for figure in (False, True):
    V, out, cols = book_sat_to_ham(3, CE, figure)
    k = len(CE)
    cyc, used = [], set()
    for i in (1, 2, 3):
        row = [(i, c) for c in (cols if bits[i - 1] else cols[::-1])]
        for t, v in enumerate(row):
            cyc.append(v)
            if t + 1 < len(row):
                for j, cl in enumerate(CE, 1):
                    lit = i if bits[i - 1] else -i
                    if j not in used and j != k and lit in cl and ("c", j) in out[v] and row[t + 1] in out[("c", j)]:
                        cyc.append(("c", j))
                        used.add(j)
                        break
        if i == 1:
            cyc.append(("c", k))       # (a, last) -> [8] -> (b, last): replaces the connector edge
            used.add(k)
    check(f"book's construction ({'figure: 2k vertices per row' if figure else 'text: (i,0)..(i,2k)'}): H has "
          f"{len(V)} vertices and the Hamiltonian cycle row a left-to-right, (a,{cols[-1]}) -> [8] -> (b,{cols[-1]}), "
          "row b and row c right-to-left, other clauses by ordinary detours",
          is_ham_cycle(V, out, cyc) and len(used) == 8, f"{len(V)} vertices")
# the book's claim that G (rows and connectors only) has exactly 2^n Hamiltonian cycles holds for rows of >= 3 vertices
ok = True
for n in (1, 2, 3, 4):
    for k in (1, 2):
        V, out, cols = book_sat_to_ham(n, [], False)
        # rows for k clauses but no clause vertices
        kk = k
        Vg, outg = [], {}
        for i in range(1, n + 1):
            cols_ = list(range(0, 2 * kk + 1))
            Vg += [(i, c) for c in cols_]
            for a, b in zip(cols_, cols_[1:]):
                outg.setdefault((i, a), set()).add((i, b))
                outg.setdefault((i, b), set()).add((i, a))
            for a in (0, 2 * kk):
                for b in (0, 2 * kk):
                    if (i, a) != (i % n + 1, b):
                        outg.setdefault((i, a), set()).add((i % n + 1, b))
        ok &= ham_count(Vg, outg) == 2 ** n
check("book's claim: the variable-gadget graph G alone has exactly 2^n Hamiltonian cycles (n <= 4, k <= 2)", ok)
# the book's construction also has 'cheating' Hamiltonian cycles on satisfiable formulas
f = [(1, 3, 2), (-2, -1, 3)]
V, out, cols = book_sat_to_ham(3, f, True)
V2, out2, _ = book_sat_to_ham(3, f, False)
check("book's construction on (a ∨ c ∨ b) ∧ (b̄ ∨ ā ∨ c) has 'cheating' Hamiltonian cycles: 24 (text version) and "
      "29 (figure version) instead of 16 assignment/literal choices",
      ham_count(V2, out2) == 24 and ham_count(V, out) == 29 and expected_cycles(3, f) == 16,
      str((ham_count(V2, out2), ham_count(V, out), expected_cycles(3, f))))

print("== hamiltonian-cycle: the example")
# (a or not b or c) and (not a or b or not c)
EX_H = [(1, -2, 3), (-1, 2, -3)]
V, out = sat_to_ham(3, EX_H)
sats = sat_assignments(3, EX_H)
check("example: H has 3·8 + 2 = 26 vertices and 6·2·3 + 4·3 + 6·2 = 60 edges",
      len(V) == 26 and n_edges(out) == 60, f"{len(V)}, {n_edges(out)}")
check("example: Phi has 6 satisfying assignments; H has exactly 12 Hamiltonian cycles = sum of products",
      len(sats) == 6 and ham_count(V, out) == 12 == expected_cycles(3, EX_H),
      f"{len(sats)}, {ham_count(V, out)}, {expected_cycles(3, EX_H)}")
# the highlighted cycle: a = True, b = c = False; clause 1 via row a (1 -> [1] -> 2), clause 2 via row c (5 -> [2] -> 4)
cyc = [("h", 1)] + [(1, 0), (1, 1), ("c", 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6)] + [("h", 2)] \
    + [(2, c) for c in range(6, -1, -1)] + [("h", 3)] + [(3, 6), (3, 5), ("c", 2), (3, 4), (3, 3), (3, 2), (3, 1), (3, 0)]
check("example: the cycle h1, row a left to right with detour 1 -> [1] -> 2, h2, row b right to left, h3, row c right "
      "to left with detour 5 -> [2] -> 4, back to h1, is Hamiltonian; a = T, b = c = F satisfies Phi",
      is_ham_cycle(V, out, cyc) and satisfies((True, False, False), EX_H))
check("example: for a = T, b = c = F, clause 1 has 2 true literals (a, b̄) and clause 2 has 1 (c̄): 2 of the 12 cycles",
      len({l for l in EX_H[0] if (True, False, False)[abs(l) - 1] == (l > 0)}) == 2
      and len({l for l in EX_H[1] if (True, False, False)[abs(l) - 1] == (l > 0)}) == 1)

print("== hamiltonian-cycle: the book's VertexCover -> DirectedHamCycle")


def vc_to_ham(V, E, k):
    """Edge gadget per edge uv: (u,v,in),(u,v,out),(v,u,in),(v,u,out) with edges (u,v,in)->(u,v,out),
    (v,u,in)->(v,u,out), (u,v,in)<->(v,u,in), (u,v,out)<->(v,u,out); vertex chain of u through its incident gadgets:
    (u,v_i,out) -> (u,v_{i+1},in); cover vertices x_1..x_k with x -> first vertex of each chain, last -> x."""
    nbr = {u: [] for u in V}
    for e in E:
        a, b = sorted(e)
        nbr[a].append(b)
        nbr[b].append(a)
    H, out = [], {}

    def A(a, b):
        out.setdefault(a, set()).add(b)
    for e in E:
        u, v = sorted(e)
        H += [(u, v, "in"), (u, v, "out"), (v, u, "in"), (v, u, "out")]
        A((u, v, "in"), (u, v, "out"))
        A((v, u, "in"), (v, u, "out"))
        A((u, v, "in"), (v, u, "in"))
        A((v, u, "in"), (u, v, "in"))
        A((u, v, "out"), (v, u, "out"))
        A((v, u, "out"), (u, v, "out"))
    xs = [("x", t) for t in range(1, k + 1)]
    H += xs
    for u in V:
        d = nbr[u]
        for a, b in zip(d, d[1:]):
            A((u, a, "out"), (u, b, "in"))
        if d:
            for x in xs:
                A(x, (u, d[0], "in"))
                A((u, d[-1], "out"), x)
    return H, out


ok = True
edge_cases = []
cnt = 0
for n in range(1, 5):
    for V, E in all_ugraphs(n):
        nonisolated = {v for e in E for v in e}
        for k in range(1, n + 1):
            H, out = vc_to_ham(V, E, k)
            got = ham_count(H, out, limit=1) > 0
            want = min_vc(V, E) <= k
            if len(nonisolated) == n:
                cnt += 1
                ok &= got == want
            elif got != want:
                edge_cases.append((n, len(E), k))
for _ in range(60):
    n = 5
    V, E = rand_ugraph(n, 0.5)
    if {v for e in E for v in e} != set(V) or len(E) > 6:
        continue
    for k in range(1, n + 1):
        H, out = vc_to_ham(V, E, k)
        ok &= (ham_count(H, out, limit=1) > 0) == (min_vc(V, E) <= k)
        cnt += 1
check(f"VertexCover -> DirectedHamCycle (book): G has a vertex cover of size k <=> H Hamiltonian, for graphs without "
      f"isolated vertices and 1 <= k <= n ({cnt} instances)", ok)
check("  ... with isolated vertices it can fail: e.g. one edge plus an isolated vertex, k = 3 (cover exists, H has 3 "
      "cover vertices but only 2 vertex chains)", (3, 1, 3) in edge_cases, str(sorted(set(edge_cases))[:6]))
ok = True
cnt = 0
for n in range(0, 5):
    for V, E in all_ugraphs(n):
        V2 = sorted({v for e in E for v in e})
        for k in range(0, n + 1):
            want = min_vc(V, E) <= k
            if k >= len(V2):
                got = True
            else:
                H, out = vc_to_ham(V2, E, k)
                got = ham_count(H, out, limit=1) > 0
            ok &= got == want
            cnt += 1
check(f"  ... repaired: delete isolated vertices, answer YES if k >= vertices left, else the book's H ({cnt} instances, "
      "all graphs <= 4 vertices, 0 <= k <= n)", ok)
V, E = [0, 1, 2, 3], {frozenset(e) for e in [(0, 1), (0, 2), (0, 3), (1, 3), (2, 3)]}   # Figure 12.17: u v w x
H, out = vc_to_ham(V, E, 2)
covers2 = [set(S) for S in itertools.combinations(V, 2) if is_vertex_cover(set(S), E)]
check("book's Figure 12.17 graph (edges uv, uw, ux, vx, wx; k = 2): H has 4E + k = 22 vertices and "
      "6E + (2E - V) + 2kV = 52 edges, exactly 2 Hamiltonian cycles; {u, x} (Figure 12.18) is the only cover of size 2",
      len(H) == 22 and n_edges(out) == 52 and ham_count(H, out) == 2 and covers2 == [{0, 3}],
      f"{len(H)} vertices, {n_edges(out)} edges, {ham_count(H, out)} cycles, covers {covers2}")

print("== hamiltonian-cycle: directed -> undirected, TSP")


def und_ham_count(V, E, limit=None):
    out = {v: set() for v in V}
    for e in E:
        a, b = tuple(e)
        out[a].add(b)
        out[b].add(a)
    return ham_count(V, out, limit)


ok = True
for _ in range(300):
    n = random.randint(2, 6)
    Vd = list(range(n))
    outd = {u: {v for v in Vd if v != u and random.random() < 0.45} for u in Vd}
    Vu = [(v, s) for v in Vd for s in ("in", "mid", "out")]
    Eu = {frozenset(((v, "in"), (v, "mid"))) for v in Vd} | {frozenset(((v, "mid"), (v, "out"))) for v in Vd} \
        | {frozenset(((u, "out"), (v, "in"))) for u in Vd for v in outd[u]}
    ok &= (ham_count(Vd, outd, limit=1) > 0) == (und_ham_count(Vu, Eu, limit=1) > 0)
check("DirectedHamCycle -> UndirectedHamCycle by splitting v into v_in - v_mid - v_out, u->v becoming u_out v_in "
      "(300 random digraphs, n <= 6)", ok)
ok = True
for _ in range(200):
    V, E = rand_ugraph(random.randint(3, 7), random.random())
    w = {e: 1 for e in E}
    # cheapest Hamiltonian cycle weight by brute force over permutations
    best = None
    for perm in itertools.permutations(V[1:]):
        cyc = (V[0],) + perm
        es = [frozenset((cyc[t], cyc[(t + 1) % len(cyc)])) for t in range(len(cyc))]
        if all(e in E for e in es):
            c = sum(w[e] for e in es)
            best = c if best is None else min(best, c)
    ok &= (best is not None) == (und_ham_count(V, E, limit=1) > 0) and (best is None or best == len(V))
check("TSP with every weight 1: a tour of weight V exists <=> G has a Hamiltonian cycle (200 random graphs)", ok)

# =====================================================================================================
print("== page text")
PAGES = {s: os.path.join(CONCEPTS, s + ".md") for s in ("independent-set", "graph-coloring", "hamiltonian-cycle")}
TEXT = {s: read(p) if os.path.exists(p) else "" for s, p in PAGES.items()}


def onpage(slug, s):
    return s in TEXT[slug]


for slug in PAGES:
    t = TEXT[slug]
    check(f"{slug}: frontmatter tags [concept, algorithms, complexity]; Related: is the last line",
          "tags: [concept, algorithms, complexity]" in t and t.rstrip().split("\n")[-1].startswith("Related:"))
PHRASES = {
    "independent-set": [
        "$G$ has 9 vertices, 9 triangle edges and 6 conflict edges — $a_1\\bar a_2$, $b_1\\bar b_2$, $b_1\\bar b_3$, "
        "$c_1\\bar c_3$, $\\bar a_2a_3$, $c_2\\bar c_3$ — 15 edges in all",
        "The set $\\{a_1, c_2, \\bar b_3\\}$ is independent, and it gives $a = c = \\textsf{True}$, $b = \\textsf{False}$",
        "(as do 4 other assignments; only $a, b, c$ = FFF, TTF, FTT fail)",
        "$\\textsf{MaxIndSet}(G) = 3$; so $\\textsf{MinVertexCover}(G) = 9 - 3 = 6$",
        "which has $36 - 15 = 21$ edges, has 3 vertices",
        "$G$ has $3k$ vertices and $O(k^2)$ edges",
        "$(G, k)\\mapsto(\\overline{G}, k)$ reduces IndependentSet to Clique in $O(V^2)$ time",
    ],
    "graph-coloring": [
        "$G$ has $3 + 2n + 5k$ vertices and $3 + 3n + 10k$ edges, built in $O(n + k)$ time",
        "$G$ has $3 + 8 + 20 = 31$ vertices and $3 + 12 + 40 = 55$ edges",
        "exactly 2 completions",
        "five new vertices $u, v, w, y, z$ and ten edges, $\\ell_1u$, $\\ell_2v$ and the triangle $uvw$, then $wy$, "
        "$\\ell_3z$ and the triangle $yzT$",
        "$u, v, w, y, z$ get True, Other, False, Other, False",
        "add $k - 3$ new vertices adjacent to each other and to every old vertex",
    ],
    "hamiltonian-cycle": [
        "$H$ has $n(3k+2) + k$ vertices and $6kn + 4n + 6k$ edges (when each clause has three different literals)",
        "$H$ has $3\\cdot 8 + 2 = 26$ vertices and $6\\cdot 2\\cdot 3 + 4\\cdot 3 + 6\\cdot 2 = 60$ edges",
        "$\\Phi$ has 6 satisfying assignments and $H$ exactly 12 Hamiltonian cycles",
        "giving 2 of the 12",
        "if $x_i$ is in $c_j$, edges $(i, 3j-2)\\to[j]\\to(i, 3j-1)$",
        "if $\\bar x_i$ is in $c_j$, edges $(i, 3j-1)\\to[j]\\to(i, 3j-2)$",
        "edges $h_i\\to(i, 0)$, $h_i\\to(i, 3k)$, $(i, 0)\\to h_{i+1}$, $(i, 3k)\\to h_{i+1}$",
        "$H$, with $4E + k$ vertices, is Hamiltonian iff $G$ has a vertex cover of size $k$",
        "one edge plus an isolated vertex with $k = 3$",
        "all eight clauses on $a, b, c$, with $(\\bar a\\lor b\\lor c)$ last",
        "splitting each vertex $v$ into a path $v_{\\text{in}}\\,v_{\\text{mid}}\\,v_{\\text{out}}$",
    ],
}
for slug, phrases in PHRASES.items():
    missing = [ph for ph in phrases if ph not in TEXT[slug]]
    check(f"{slug}: every checked number/construction above is stated on the page ({len(phrases)} phrases)",
          not missing, str(missing))
for slug in PAGES:
    t = TEXT[slug]
    anchors = re.findall(r"\[\[2-algorithms/12-np-hardness#([^|\]]+)", t)
    check(f"{slug}: anchors into the chapter page use the fixed slugs", anchors and all(a in {
        "127-maximum-independent-set-from-3sat", "128-the-general-pattern",
        "129-clique-and-vertex-cover-from-independent-set", "1210-graph-coloring-from-3sat", "1211-hamiltonian-cycle",
        "1212-subset-sum-from-vertex-cover", "1213-other-useful-np-hard-problems", "1214-choosing-the-right-problem"}
        for a in anchors), str(anchors))
allal = []
for root, _, files in os.walk(os.path.join(ROOT, "content")):
    for fn in files:
        if fn.endswith(".md"):
            m = re.search(r"^aliases: \[(.*)\]$", read(os.path.join(root, fn)), re.M)
            if m:
                allal += [a.strip().strip('"').lower() for a in m.group(1).split(",")]
dups = sorted({a for a in allal if allal.count(a) > 1})
check("aliases are unique site-wide", not dups, str(dups))

print()
if FAIL:
    print(f"{len(FAIL)} FAILED:", *FAIL, sep="\n  ")
    sys.exit(1)
print("ALL OK")
