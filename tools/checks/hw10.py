#!/usr/bin/env python3
"""Checks for content/3-homework-and-exams/hw10-np-hardness.md (Homework 10, CS/ECE 374 A Fall 2026).

Homework 10 was open when the page was written, so the page is a study guide and this script contains NO solution
to Problems 1 and 2.  It checks only what the page states as fact:
  * the definitions, by exhaustive search: the perfect matchings of the page's five self-test graphs, and that a
    graph with an odd number of vertices never has one;
  * the handout's two StringMatch examples, straight from the definition (try every binary string w);
  * the handout's own solved problem (RedBlue, Problem 3): the published reduction from 3Sat is run on random
    3CNF formulas and compared with an exhaustive search over the puzzle; both certificate translations of the
    published proof are executed; and the one case the published solution does not cover (a clause containing a
    variable and its negation) is exhibited."""
import itertools
import random

random.seed(11172026)
FAIL = []


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail != "" else ""))
    if not cond:
        FAIL.append(name)


# ============================================================================ Problem 1: the definition only
def perfect_matchings(n, edges):
    """All perfect matchings (sets of edges covering every vertex exactly once), by exhaustive search."""
    out = []
    if n % 2:
        return out
    for M in itertools.combinations(edges, n // 2):
        covered = [v for e in M for v in e]
        if len(set(covered)) == n:
            out.append(M)
    return out


TESTS = {
    "a single edge": (2, [(0, 1)], 1),
    "a path on three vertices": (3, [(0, 1), (1, 2)], 0),
    "a triangle": (3, [(0, 1), (1, 2), (0, 2)], 0),
    "a 4-cycle": (4, [(0, 1), (1, 2), (2, 3), (0, 3)], 2),
    "a star with three leaves": (4, [(0, 1), (0, 2), (0, 3)], 0),
}
for name, (n, edges, want) in TESTS.items():
    got = len(perfect_matchings(n, edges))
    check(f"1 self-test graph, {name}: {want} perfect matching(s)", got == want, got)
def has_cover_by_disjoint_edges(n, edges):
    """Is there a set of pairwise disjoint edges that covers every vertex?  No parity shortcut."""
    for r in range(0, len(edges) + 1):
        for M in itertools.combinations(edges, r):
            covered = [v for e in M for v in e]
            if len(covered) == len(set(covered)) == n:
                return True
    return False


ok = True
cnt = 0
for n in (1, 3, 5):
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [p for i, p in enumerate(pairs) if mask >> i & 1]
        if n == 5 and len(edges) > 7 and mask % 5:
            continue                          # sample the dense 5-vertex graphs
        cnt += 1
        ok &= not has_cover_by_disjoint_edges(n, edges)
check(f"1 no graph with an odd number of vertices has a perfect matching ({cnt} graphs on 1, 3 and 5 vertices, "
      "searched without using parity): a matching with r edges covers 2r vertices", ok)
check("1 the complete graph on 4 vertices has 3 perfect matchings; 'perfect' means 2|M| = |V|",
      len(perfect_matchings(4, list(itertools.combinations(range(4), 2)))) == 3
      and all(2 * len(M) == 4 for M in perfect_matchings(4, list(itertools.combinations(range(4), 2)))))

# ============================================================================ Problem 2: the handout's examples only
def matches(w, s):
    return any(a == b for a, b in zip(w, s))


def string_match(S):
    n = len(S[0])
    assert all(len(s) == n and set(s) <= set("012") for s in S)
    return ["".join(w) for w in itertools.product("01", repeat=n) if all(matches(w, s) for s in S)]


S1 = ["01220", "21110", "21120", "00211", "11101"]
S2 = ["2002", "2112", "2012", "2102"]
W1 = string_match(S1)
check("2 handout example 1: S = {01220, 21110, 21120, 00211, 11101} is a True instance, and w = 01001 works",
      "01001" in W1, len(W1))
check("2 handout example 1: exactly 23 of the 32 binary strings of length 5 work", len(W1) == 23, len(W1))
check("2 handout example 1: 01001 agrees with the first three strings in the second position and with the last "
      "two in the last position",
      all(s[1] == "01001"[1] for s in S1[:3]) and all(s[4] == "01001"[4] for s in S1[3:]))
check("2 handout example 2: S = {2002, 2112, 2012, 2102} is a False instance (none of the 16 binary strings works)",
      string_match(S2) == [])
check("2 handout example 2: the four strings carry every pattern 00, 11, 01, 10 in their two middle positions",
      sorted(s[1:3] for s in S2) == ["00", "01", "10", "11"] and all(s[0] == "2" == s[3] for s in S2))

# ============================================================================ Problem 3: the handout's solved problem
# a board: dict (row, col) -> 'B' or 'R'; rows 0 .. n-1 (clauses), columns 0 .. m-1 (variables)
def solvable_by_subsets(board, nrows, ncols):
    """Exhaustive search over the sets of stones to keep."""
    cells = list(board)
    for mask in range(1 << len(cells)):
        keep = [c for i, c in enumerate(cells) if mask >> i & 1]
        if len({r for r, _ in keep}) != nrows:
            continue
        ok = True
        for c in range(ncols):
            cols = {board[x] for x in keep if x[1] == c}
            if len(cols) > 1:
                ok = False
                break
        if ok:
            return True
    return nrows == 0


def solvable_by_columns(board, nrows, ncols):
    """Equivalent search: each column keeps its blue stones, its red stones, or nothing."""
    for choice in itertools.product("BR-", repeat=ncols):
        rows = {r for (r, c), col in board.items() if choice[c] == col}
        if len(rows) == nrows:
            return choice
    return None


def sat(phi, m):
    for a in itertools.product([False, True], repeat=m):
        if all(any((a[abs(l) - 1] if l > 0 else not a[abs(l) - 1]) for l in c) for c in phi):
            return a
    return None


def redblue_from_3sat(phi, m):
    """The handout's reduction: row i = clause i, column j = variable x_j; blue if x_j is in the clause,
    red if its negation is."""
    board = {}
    for i, c in enumerate(phi):
        for l in c:
            assert (i, abs(l) - 1) not in board, "a clause with a variable and its negation needs two stones"
            board[(i, abs(l) - 1)] = "B" if l > 0 else "R"
    return board


def random_3cnf(m, k):
    out = []
    for _ in range(k):
        vs = random.sample(range(1, m + 1), 3)
        out.append(tuple(v if random.random() < 0.5 else -v for v in vs))
    return out


ok_two = True
for _ in range(150):
    m = random.randint(3, 4)
    phi = random_3cnf(m, random.randint(1, 4))
    b = redblue_from_3sat(phi, m)
    ok_two &= solvable_by_subsets(b, len(phi), m) == (solvable_by_columns(b, len(phi), m) is not None)
check("3 (tool) searching over kept-stone sets and searching over one choice per column agree on 150 small boards",
      ok_two)
ok_iff = ok_fw = ok_bw = ok_size = True
ns = nu = 0
for t in range(600):
    m = random.randint(3, 5)
    if t % 3 == 0:        # planted: all eight sign patterns on three variables (unsatisfiable), plus extras
        a, b_, c = random.sample(range(1, m + 1), 3)
        phi = [(s1 * a, s2 * b_, s3 * c) for s1 in (1, -1) for s2 in (1, -1) for s3 in (1, -1)]
        if t % 6 == 0:
            phi.pop(random.randrange(8))
        phi += random_3cnf(m, random.randint(0, 2))
    else:
        phi = random_3cnf(m, random.randint(1, 5 * m))
    board = redblue_from_3sat(phi, m)
    a = sat(phi, m)
    sol = solvable_by_columns(board, len(phi), m)
    ns += a is not None
    nu += a is None
    ok_iff &= (a is not None) == (sol is not None)
    ok_size &= len(board) == 3 * len(phi)
    if a is not None:
        # => (handout): remove red stones from column j if x_j is True, blue stones if x_j is False
        keep = {x: col for x, col in board.items() if col == ("B" if a[x[1]] else "R")}
        ok_fw &= len({r for r, _ in keep}) == len(phi) and all(
            len({col for (r, c), col in keep.items() if c == j}) <= 1 for j in range(m))
    if sol is not None:
        # <= (handout): blue column -> True, red column -> False, empty column -> arbitrary
        back = tuple(True if ch == "B" else False for ch in sol)
        ok_bw &= all(any((back[abs(l) - 1] if l > 0 else not back[abs(l) - 1]) for l in c) for c in phi)
check(f"3 the handout's reduction: the formula is satisfiable iff the puzzle is solvable (600 3CNF formulas with "
      f"three distinct variables per clause; {ns} satisfiable, {nu} not)", ok_iff and ns > 150 and nu > 100)
check("3 the board has one row per clause, one column per variable and exactly three stones per row", ok_size)
check("3 =>: removing the stones of the false literals leaves one color per column and a stone in every row", ok_fw)
check("3 <=: blue column True, red column False, empty column arbitrary gives a satisfying assignment", ok_bw)
try:
    redblue_from_3sat([(1, -1, 2)], 2)
    gap = False
except AssertionError:
    gap = True
check("3 the case the published solution does not mention: the clause (x1 or not x1 or x2) would need a blue and "
      "a red stone in the same square", gap)

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: {FAIL}")
