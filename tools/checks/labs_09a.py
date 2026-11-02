#!/usr/bin/env python3
"""Checks for content/3-homework-and-exams/lab-09a.md (Lab 9a, CS/ECE 374 A Fall 2026: number-maze variants).

No official solutions were posted, so each of the page's six reductions is built exactly as the page describes it,
searched with a plain breadth-first search, and compared with searches that never look at the page's graphs and apply
each variant's rule, as the handout states it, to whole move sequences:

  (A) raw enumeration: every move sequence of length <= L from the start square, simulated on the maze, and the
      variant's condition checked on the complete sequence (directions and lengths).  L is the largest length within a
      work budget; for problem 5 it is n - 1, which is conclusive (a strictly increasing sequence of legal move
      lengths, all in 1..n-1, has at most n - 1 terms), and for sparse mazes it reaches the pigeonhole bound of the
      variant, which is conclusive too (see bound()).
  (B) exact searches with a different state:
        problems 1 and 3: the set R_m of squares reachable in exactly m moves, iterated until (R_m, m mod 5) repeats;
        problems 2, 4, 5: their conditions are conjunctions over consecutive pairs of moves, so the set of
            (square, last raw move (direction, length)) pairs after m valid moves, iterated until it repeats;
        problem 6: a subset construction over move-length sequences s: the pair (A_s, B_s) of the squares reachable
            from the start along lengths s and the squares that reach the goal along reverse(s).
Both readings of the rules are checked: the token may pass through the goal before its last move (the page's default),
or the game ends on arrival (the page: give the goal a label >= n).  The handout's example (answer 8, unique) is
reproduced, its answers for problems 2-6 are computed for every possible goal label, and every claim the page makes
about it is re-derived.  Vertex and edge counts are compared with the page's bounds, and BFS work is counted on growing
mazes."""
import itertools
import random
import sys
from collections import deque

random.seed(374)
sys.setrecursionlimit(100000)
FAIL = []


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail != "" else ""))
    if not cond:
        FAIL.append(name)


DIRS = {"U": (-1, 0), "D": (1, 0), "L": (0, -1), "R": (0, 1)}
OPP = {"U": "D", "D": "U", "L": "R", "R": "L"}
AXIS = {"U": "V", "D": "V", "L": "H", "R": "H"}


def squares(n):
    return [(i, j) for i in range(n) for j in range(n)]


def moves(M, p):
    """The legal moves out of square p as (direction, length, target); 0-indexed, row 0 on top.  A label >= n allows
    no move (every move would leave the board)."""
    n = len(M)
    i, j = p
    k = M[i][j]
    out = []
    for d, (di, dj) in DIRS.items():
        a, b = i + k * di, j + k * dj
        if 0 <= a < n and 0 <= b < n:
            out.append((d, k, (a, b)))
    return out


BFS_OPS = [0]


def bfs(adj, s):
    """The black box: breadth-first search from s; returns the distance of every reachable vertex."""
    dist, Q = {s: 0}, deque([s])
    while Q:
        u = Q.popleft()
        BFS_OPS[0] += 1
        for v in adj[u]:
            BFS_OPS[0] += 1
            if v not in dist:
                dist[v] = dist[u] + 1
                Q.append(v)
    return dist


def nedges(adj):
    return sum(len(v) for v in adj.values())


def is_dag(adj):
    indeg = {v: 0 for v in adj}
    for u in adj:
        for v in adj[u]:
            indeg[v] += 1
    Q = deque(v for v in adj if indeg[v] == 0)
    seen = 0
    while Q:
        u = Q.popleft()
        seen += 1
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                Q.append(v)
    return seen == len(adj)


# ============================================================================ the page's graphs, as the page states them
def page1(M):
    """Problem 1: vertices = squares; an edge p -> q for every legal move from p to q."""
    n = len(M)
    return {p: [q for _, _, q in moves(M, p)] for p in squares(n)}


def page2(M):
    """Problem 2: vertices s and (p, a), a in {H, V} = axis of the move that brought the token to p.
    s -> (q, axis) for each move out of (1,1); (p, a) -> (q, axis(move)) for each move out of p of the other axis."""
    n = len(M)
    adj = {"s": [(q, AXIS[d]) for d, _, q in moves(M, (0, 0))]}
    for p in squares(n):
        for a in "HV":
            adj[(p, a)] = [(q, AXIS[d]) for d, _, q in moves(M, p) if AXIS[d] != a]
    return adj


def page3(M):
    """Problem 3: vertices (p, r), r in Z_5; (p, r) -> (q, r + 1 mod 5) for every move p -> q."""
    n = len(M)
    return {(p, r): [(q, (r + 1) % 5) for _, _, q in moves(M, p)] for p in squares(n) for r in range(5)}


def page4(M):
    """Problem 4: vertices s and (p, d), d in {U, D, L, R} = direction of the move that brought the token to p.
    s -> (q, d) for each move out of (1,1); (p, d) -> (q, d') for each move out of p whose direction d' != opp(d)."""
    n = len(M)
    adj = {"s": [(q, d) for d, _, q in moves(M, (0, 0))]}
    for p in squares(n):
        for d0 in "UDLR":
            adj[(p, d0)] = [(q, d) for d, _, q in moves(M, p) if d != OPP[d0]]
    return adj


def page5(M):
    """Problem 5: vertices = squares and t (the end of a solution).  p -> q for a move p -> q with M[q] > M[p]
    (another, longer move can follow); p -> t for every move from p into the goal (the last move)."""
    n = len(M)
    G = (n - 1, n - 1)
    adj = {p: [] for p in squares(n)}
    adj["t"] = []
    for p in squares(n):
        for _, _, q in moves(M, p):
            if M[q[0]][q[1]] > M[p[0]][p[1]]:
                adj[p].append(q)
            if q == G:
                adj[p].append("t")
    return adj


def page5_direct(M):
    """Problem 5, the direct version: vertices (p, l), l in {0..n-1} = length of the last move (0: none yet);
    (p, l) -> (q, M[p]) for every move p -> q with M[p] > l."""
    n = len(M)
    adj = {(p, l): [] for p in squares(n) for l in range(n)}
    for p in squares(n):
        for l in range(n):
            for _, k, q in moves(M, p):
                if k > l:
                    assert k <= n - 1
                    adj[(p, l)].append((q, k))
    return adj


def moves_into_by_length(M):
    """For every square b and length k: the squares b' with a move of length k into b (b' = b -+ k in some direction,
    labeled k) -- at most four."""
    n = len(M)
    into = {}
    for b in squares(n):
        for k in range(1, n):
            lst = []
            for di, dj in DIRS.values():
                c = (b[0] - k * di, b[1] - k * dj)
                if 0 <= c[0] < n and 0 <= c[1] < n and M[c[0]][c[1]] == k:
                    lst.append(c)
            into[(b, k)] = lst
    return into


def page6(M):
    """Problem 6: vertices (f, b), all ordered pairs of squares.  (f, b) -> (f', b') for every move f -> f' and every
    move b' -> b of the same length (M[b'] = M[f])."""
    n = len(M)
    into = moves_into_by_length(M)
    adj = {}
    for f in squares(n):
        fm = moves(M, f)
        for b in squares(n):
            adj[(f, b)] = [(f2, b2) for _, k, f2 in fm for b2 in into[(b, k)]]
    return adj


def page_answer(M, prob):
    """The page's algorithm: build the graph, run BFS once from the start vertex, read off the answer."""
    n = len(M)
    G = (n - 1, n - 1)
    if prob == 1:
        return bfs(page1(M), (0, 0)).get(G)
    if prob == 3:
        return bfs(page3(M), ((0, 0), 0)).get((G, 0))
    if prob == 6:
        dist = bfs(page6(M), ((0, 0), G))
        best = None
        for (f, b), x in dist.items():
            if f == b:
                c = 2 * x
            elif any(q == b for _, _, q in moves(M, f)):
                c = 2 * x + 1
            else:
                continue
            best = c if best is None else min(best, c)
        return best
    if n == 1:  # the start is the goal: the empty sequence (stated on the page for problems 2, 4, 5)
        return 0
    if prob == 2:
        dist = bfs(page2(M), "s")
        c = [dist[(G, a)] for a in "HV" if (G, a) in dist]
        return min(c) if c else None
    if prob == 4:
        dist = bfs(page4(M), "s")
        c = [dist[(G, d)] for d in "UDLR" if (G, d) in dist]
        return min(c) if c else None
    if prob == 5:
        return bfs(page5(M), (0, 0)).get("t")
    if prob == "5d":
        dist = bfs(page5_direct(M), ((0, 0), 0))
        c = [dist[(G, l)] for l in range(n) if (G, l) in dist]
        return min(c) if c else None
    raise ValueError(prob)


PROBS = [1, 2, 3, 4, 5, "5d", 6]


def page_all(M):
    return {p: page_answer(M, p) for p in PROBS}


# ============================================================================ independent searches
VALID = {  # each variant's condition, written straight from the handout, on the whole sequence
    1: lambda D, Ls: True,
    2: lambda D, Ls: all(AXIS[a] != AXIS[b] for a, b in zip(D, D[1:])),  # alternate horizontal / vertical
    3: lambda D, Ls: len(D) % 5 == 0,  # number of moves a multiple of 5
    4: lambda D, Ls: all(OPP[a] != b for a, b in zip(D, D[1:])),  # no two adjacent moves in opposite directions
    5: lambda D, Ls: all(x < y for x, y in zip(Ls, Ls[1:])),  # each move longer than the previous one
    6: lambda D, Ls: Ls == Ls[::-1],  # the sequence of lengths is a palindrome
}


def walk_counts(M, L, stop=False):
    """Number of move sequences of length <= m from the start, for m = 0..L (stop: no move after reaching the goal)."""
    n = len(M)
    G = (n - 1, n - 1)
    cur, tot, out = {(0, 0): 1}, 1, [1]
    for _ in range(L):
        nxt = {}
        for p, c in cur.items():
            if stop and p == G:
                continue
            for _, _, q in moves(M, p):
                nxt[q] = nxt.get(q, 0) + c
        cur = nxt
        tot += sum(cur.values())
        out.append(tot)
    return out


def raw_min(M, L, stop=False):
    """(A) Every move sequence of length <= L, simulated; for each problem the fewest moves of a sequence that ends on
    the goal and satisfies the condition.  stop: the game ends on arrival (no move after reaching the goal)."""
    n = len(M)
    G = (n - 1, n - 1)
    best = {k: None for k in VALID}
    D, Ls = [], []

    def visit(p):
        m = len(D)
        if p == G:
            for k in VALID:
                if (best[k] is None or m < best[k]) and VALID[k](D, Ls):
                    best[k] = m
            if stop:
                return
        if m == L:
            return
        for d, k, q in moves(M, p):
            D.append(d)
            Ls.append(k)
            visit(q)
            D.pop()
            Ls.pop()

    visit((0, 0))
    return best


def exact_1_3(M):
    """(B) Problems 1 and 3 from the sets R_m of squares reachable in exactly m moves (no graph built)."""
    n = len(M)
    G = (n - 1, n - 1)
    R, m, seen, a1, a3 = frozenset([(0, 0)]), 0, set(), None, None
    while (R, m % 5) not in seen:
        seen.add((R, m % 5))
        if G in R:
            a1 = m if a1 is None else a1
            if a3 is None and m % 5 == 0:
                a3 = m
        R = frozenset(q for p in R for _, _, q in moves(M, p))
        m += 1
    return a1, a3


def exact_pairs(M, k):
    """(B) Problems 2, 4, 5: the condition is a conjunction over consecutive moves, so a valid prefix is summarized by
    its last square and its last raw move (direction, length); iterate the level sets until they repeat."""
    n = len(M)
    G = (n - 1, n - 1)
    R, m, seen = frozenset([((0, 0), None)]), 0, set()
    while R and R not in seen:
        if any(p == G for p, _ in R):
            return m
        seen.add(R)
        nxt = set()
        for p, last in R:
            for d, l, q in moves(M, p):
                if last is None or VALID[k]([last[0], d], [last[1], l]):
                    nxt.add((q, (d, l)))
        R = frozenset(nxt)
        m += 1
    return None


def exact_6(M):
    """(B) Problem 6 by a subset construction over length sequences s: A_s = squares reachable from the start along
    lengths s, B_s = squares from which the goal is reachable along reverse(s).  Length 2|s| works iff A_s and B_s
    meet; length 2|s|+1 iff some move leads from A_s into B_s (the middle move)."""
    n = len(M)
    G = (n - 1, n - 1)
    sq = squares(n)
    lab = lambda p: M[p[0]][p[1]]
    start = (frozenset([(0, 0)]), frozenset([G]))
    seen, level, h = {start}, [start], 0
    while level:
        best = None
        for A, B in level:
            if A & B:
                c = 2 * h
            elif any(q in B for p in A for _, _, q in moves(M, p)):
                c = 2 * h + 1
            else:
                continue
            best = c if best is None else min(best, c)
        if best is not None:
            return best
        nxt = []
        for A, B in level:
            for x in range(1, n):
                A2 = frozenset(q for p in A if lab(p) == x for _, _, q in moves(M, p))
                B2 = frozenset(p for p in sq if lab(p) == x and any(q in B for _, _, q in moves(M, p)))
                if A2 and B2 and (A2, B2) not in seen:
                    seen.add((A2, B2))
                    nxt.append((A2, B2))
        level, h = nxt, h + 1
    return None


def exact_all(M):
    a1, a3 = exact_1_3(M)
    return {1: a1, 2: exact_pairs(M, 2), 3: a3, 4: exact_pairs(M, 4), 5: exact_pairs(M, 5), 6: exact_6(M)}


def bound(n, k):
    """Pigeonhole bounds on a shortest valid solution (if one exists): its prefixes never repeat a (square, state)
    pair, since cutting the loop between two equal ones leaves a shorter valid solution.  State: nothing (1),
    last axis or none (2), length mod 5 (3), last direction or none (4); problem 5: lengths strictly increase within
    1..n-1; problem 6: the pairs (p_k, p_{m-k}), k <= m/2, are distinct (cut both loops at once)."""
    return {1: n * n - 1, 2: 2 * n * n, 3: 5 * n * n - 1, 4: 4 * n * n, 5: n - 1, 6: 2 * n ** 4 - 1}[k]


def stop_version(M):
    """The page's rule for the 'game ends on arrival' reading: give the goal a label >= n."""
    n = len(M)
    M2 = [row[:] for row in M]
    M2[n - 1][n - 1] = n
    return M2


def fmt(a):
    return "none" if a is None else str(a)


# ============================================================================ the handout's example
print("== the handout's 5x5 example")
EX = [[3, 5, 7, 4, 6], [5, 3, 1, 5, 3], [2, 8, 3, 1, 4], [4, 5, 7, 2, 3], [3, 1, 3, 2, 5]]  # goal label: see below
SOL8 = "R3 D4 L2 R1 U3 L1 R3 D3".split()


def simulate(M, seq):
    p, path = (0, 0), [(0, 0)]
    for mv in seq:
        d, k = mv[0], int(mv[1:])
        assert M[p[0]][p[1]] == k, (p, mv)
        p = (p[0] + k * DIRS[d][0], p[1] + k * DIRS[d][1])
        assert 0 <= p[0] < len(M) and 0 <= p[1] < len(M)
        path.append(p)
    return path


EXPECT = {1: 8, 2: None, 3: 10, 4: None, 5: None, "5d": None, 6: None}
for g in range(1, 10):  # the goal is drawn as a star; g >= 5 means no move leaves it
    M = [row[:] for row in EX]
    M[4][4] = g
    ans = page_all(M)
    check(f"example, goal label {g}: page answers 1..6 = 8, none, 10, none, none, none", ans == EXPECT,
          {k: fmt(v) for k, v in ans.items()})
    ex = exact_all(M)
    check(f"example, goal label {g}: independent exact searches agree", all(ex[k] == ans[k] for k in ex), ex)
    if g in (3, 5):
        rw = raw_min(M, 12)
        check(f"example, goal label {g}: raw enumeration of all sequences up to 12 moves agrees",
              all(rw[k] == (ans[k] if ans[k] is not None and ans[k] <= 12 else None) for k in rw), rw)
        rw5 = raw_min(M, 4)
        check(f"example, goal label {g}: problem 5 conclusive (all sequences up to n - 1 = 4 moves): none",
              rw5[5] is None)
path = simulate(EX, SOL8)
check("example: the drawn solution R3 D4 L2 R1 U3 L1 R3 D3 reaches the goal", path[-1] == (4, 4), path)
D8, L8 = [m[0] for m in SOL8], [int(m[1:]) for m in SOL8]
check("example: the drawn solution is valid for none of problems 2-6",
      not any(VALID[k](D8, L8) for k in (2, 3, 4, 5, 6)), [VALID[k](D8, L8) for k in (2, 3, 4, 5, 6)])


def count_walks_to_goal(M, m):
    cur = {(0, 0): 1}
    for _ in range(m):
        nxt = {}
        for p, c in cur.items():
            for _, _, q in moves(M, p):
                nxt[q] = nxt.get(q, 0) + c
        cur = nxt
    return cur.get((len(M) - 1, len(M) - 1), 0)


def walks_to_goal(M, m, avoid_goal):
    """All walks of exactly m moves from the start to the goal (avoid_goal: not passing through it before the end)."""
    n = len(M)
    G = (n - 1, n - 1)
    out = []

    def rec(p, seq):
        if len(seq) == m:
            if p == G:
                out.append(" ".join(seq))
            return
        if avoid_goal and p == G and seq:
            return
        for d, k, q in moves(M, p):
            rec(q, seq + [f"{d}{k}"])

    rec((0, 0), [])
    return out


SOL10 = "R3 D4 L2 R1 U3 L1 R3 L3 R3 D3"
for g in range(1, 10):
    M = [row[:] for row in EX]
    M[4][4] = g
    w8, w5, w10 = walks_to_goal(M, 8, False), walks_to_goal(M, 5, False), walks_to_goal(M, 10, True)
    check(f"example, goal label {g}: the drawn solution is the only one with 8 moves; none has 5 moves; the only one "
          f"with 10 moves that does not pass through the goal is {SOL10}",
          w8 == [" ".join(SOL8)] and w5 == [] and w10 == [SOL10], (len(w8), len(w5), w10))
    if g == 3:
        print("     goal label 3, all 10-move solutions:", walks_to_goal(M, 10, False))
p10 = simulate(EX, SOL10.split())
check("example: the 10-move solution is the 8-move one with the detour L3 R3 inserted before the last move",
      SOL10.split() == SOL8[:7] + ["L3", "R3"] + SOL8[7:] and p10[-1] == (4, 4), p10)


def into(M, b):
    return sorted((p, d, k) for p in squares(len(M)) for d, k, q in moves(M, p) if q == b)


for g in range(1, 10):
    M = [row[:] for row in EX]
    M[4][4] = g
    ok = (into(M, (4, 4)) == [((1, 4), "D", 3)]
          and into(M, (1, 4)) == sorted([((1, 1), "R", 3)] + ([((4, 4), "U", 3)] if g == 3 else []))
          and into(M, (1, 1)) == sorted([((1, 2), "L", 1), ((1, 4), "L", 3)]))
    check(f"example, goal label {g}: only D3 from (2,5) enters the goal; only R3 from (2,2) (or U3 from the goal "
          f"when its label is 3) enters (2,5); only L1 from (2,3) and L3 from (2,5) enter (2,2)", ok)
for g in range(1, 10):  # the consequences, checked on every solution with at most 14 moves
    M = [row[:] for row in EX]
    M[4][4] = g
    sols = [w.split() for m in range(1, 15) for w in walks_to_goal(M, m, False)]
    ok = bool(sols)
    for w in sols:
        pos = simulate(M, w)
        ok &= any(a[0] == "L" and b == "R3" and pos[t + 1] == (1, 1) for t, (a, b) in enumerate(zip(w, w[1:])))
        ok &= [int(x[1:]) for x in w[:2]] == [3, 4] and [int(x[1:]) for x in w[-2:]] == [3, 3]
        if g >= 5:
            ok &= w[-2:] == ["R3", "D3"] and pos[-3] == (1, 1)
    check(f"example, goal label {g}: all {len(sols)} solutions with <= 14 moves contain a left move into (2,2) "
          f"followed by R3, start with lengths 3, 4 and end with lengths 3, 3"
          + (" (and end R3 from (2,2), D3)" if g >= 5 else ""), ok)
check("example: the first move is R3 to (1,4) or D3 to (4,1), both labeled 4",
      sorted((d, k, q) for d, k, q in moves(EX, (0, 0))) == [("D", 3, (3, 0)), ("R", 3, (0, 3))]
      and EX[0][3] == 4 and EX[3][0] == 4)

# ============================================================================ the traps on the page
print("== the traps")


def modified_bfs_squares(M, prob, full=False):
    """The wrong approach: BFS on the squares, each marked once, skipping a move that breaks the rule together with
    the move that first reached the current square; moves tried in the order up, down, left, right.
    full: also return the marked squares with the direction that first reached each."""
    n = len(M)
    dist, last, Q = {(0, 0): 0}, {(0, 0): None}, deque([(0, 0)])
    while Q:
        u = Q.popleft()
        for d, _, q in moves(M, u):
            l = last[u]
            if l is not None and ((prob == 2 and AXIS[l] == AXIS[d]) or (prob == 4 and OPP[l] == d)):
                continue
            if q not in dist:
                dist[q], last[q] = dist[u] + 1, d
                Q.append(q)
    if full:
        return dist.get((n - 1, n - 1)), last
    return dist.get((n - 1, n - 1))


TRAP2 = [[1, 1, 1], [1, 1, 1], [1, 2, 1]]
check("trap (Problem 2): on 111/111/121 the square-marking BFS reports no solution, the page's answer is 4",
      modified_bfs_squares(TRAP2, 2) is None and page_answer(TRAP2, 2) == 4 and exact_pairs(TRAP2, 2) == 4)
_, last2 = modified_bfs_squares(TRAP2, 2, full=True)
check("trap (Problem 2): the square-marking BFS reaches the center by down, right; from it up hits the marked (1,2) "
      "and down reaches (3,2), which has no horizontal move; it marks only (1,1), (2,1), (1,2), (2,2), (3,2)",
      last2 == {(0, 0): None, (1, 0): "D", (0, 1): "R", (1, 1): "R", (2, 1): "D"}
      and sorted((d, q) for d, _, q in moves(TRAP2, (1, 1)) if AXIS[d] == "V") == [("D", (2, 1)), ("U", (0, 1))]
      and not any(AXIS[d] == "H" for d, _, _ in moves(TRAP2, (2, 1))), last2)
pth = simulate(TRAP2, ["R1", "D1", "R1", "D1"])
check("trap (Problem 2): right, down, right, down is a valid 4-move solution of 111/111/121",
      pth[-1] == (2, 2) and VALID[2](list("RDRD"), [1, 1, 1, 1]), pth)
ONES2 = [[1, 1], [1, 1]]
check("trap (Problem 3): in the all-1 2x2 maze Problem 1 gives 2 and Problem 3 gives 10, and no walk of odd "
      "length reaches the goal",
      page_answer(ONES2, 1) == 2 and page_answer(ONES2, 3) == 10 and exact_all(ONES2)[3] == 10
      and all(count_goal == 0 for count_goal in
              [sum(1 for w in walks_to_goal(ONES2, m, False)) for m in range(1, 16, 2)]))

print("== out-degrees stated on the page")
deg_ok = {2: True, 4: True, 6: True, "t": True}
for _ in range(300):
    n = random.randint(1, 6)
    M = [[1 if random.random() < 0.5 else random.randint(1, n) for _ in range(n)] for _ in range(n)]
    deg_ok[2] &= max(len(v) for v in page2(M).values()) <= 2
    deg_ok[4] &= max(len(v) for v in page4(M).values()) <= 3 and len(page4(M)["s"]) <= 2
    if n <= 5:
        deg_ok[6] &= max(len(v) for v in page6(M).values()) <= 16
    deg_ok["t"] &= sum(v.count("t") for v in page5(M).values()) <= 2 * (n - 1)
check("Problem 2: at most 2 edges leave each vertex", deg_ok[2])
check("Problem 4: at most 3 edges leave each vertex, at most 2 leave s", deg_ok[4])
check("Problem 6: at most 16 edges leave each vertex", deg_ok[6])
check("Problem 5: at most 2(n-1) edges enter t", deg_ok["t"])
check("Problem 6: the all-1 5x5 maze attains out-degree 16",
      max(len(v) for v in page6([[1] * 5 for _ in range(5)]).values()) == 16)

# ============================================================================ exhaustive and random comparisons
print("== page vs independent exact searches (both readings of the rules)")


def compare_exact(M, stats):
    """Page answers vs (B), for the pass-through reading and the stop-on-arrival reading; also: problem 5 equals its
    direct version, the answer of problem 5 is at most n - 1, and problem 1 <= every variant."""
    bad = []
    for reading in ("pass", "stop"):
        MM = M if reading == "pass" else stop_version(M)
        pa, ex = page_all(MM), exact_all(MM)
        for k in ex:
            if pa[k] != ex[k]:
                bad.append((reading, k, pa[k], ex[k]))
        if pa[5] != pa["5d"]:
            bad.append((reading, "5 vs 5d", pa[5], pa["5d"]))
        if pa[5] is not None and pa[5] > len(M) - 1:
            bad.append((reading, "5 > n-1", pa[5]))
        for k in (2, 3, 4, 5, 6):
            if pa[k] is not None and (pa[1] is None or pa[k] < pa[1]):
                bad.append((reading, "below problem 1", k))
        for k in ex:
            stats.setdefault((reading, k), [0, 0])[pa[k] is None] += 1
    return bad


def run_family(name, mazes):
    stats, bad, cnt = {}, [], 0
    for M in mazes:
        b = compare_exact(M, stats)
        cnt += 1
        if b:
            bad.append((M, b))
    for M, b in bad[:5]:
        print("    MISMATCH", M, b)
    solved = {k: stats[("pass", k)][0] for k in VALID}
    check(f"{name}: page == exact on {cnt} mazes, both readings", not bad,
          "solvable (pass-through reading) per problem: " + ", ".join(f"{k}:{solved[k]}" for k in VALID))
    return stats


run_family("all 1x1 and 2x2 mazes, labels 1..3",
           [[[a]] for a in (1, 2, 3)] + [[list(t[:2]), list(t[2:])] for t in itertools.product((1, 2, 3), repeat=4)])
run_family("all 3x3 mazes, labels 1..3",
           [[list(t[0:3]), list(t[3:6]), list(t[6:9])] for t in itertools.product((1, 2, 3), repeat=9)])
run_family("random 4x4 mazes, labels 1..4", [[[random.randint(1, 4) for _ in range(4)] for _ in range(4)]
                                              for _ in range(1500)])
run_family("random 4x4 mazes, labels 1..3", [[[random.randint(1, 3) for _ in range(4)] for _ in range(4)]
                                              for _ in range(1500)])
run_family("random 5x5 mazes, labels 1..5", [[[random.randint(1, 5) for _ in range(5)] for _ in range(5)]
                                              for _ in range(800)])
run_family("random 5x5 mazes, labels 1..4", [[[random.randint(1, 4) for _ in range(5)] for _ in range(5)]
                                              for _ in range(800)])
def sample_p5_solvable(n, hi, count):
    out = []
    while len(out) < count:
        M = [[random.randint(1, hi) for _ in range(n)] for _ in range(n)]
        if bfs(page5(M), (0, 0)).get("t") is not None or random.random() < 0.02:
            out.append(M)
    return out


run_family("random 4x4..6x6 mazes, mostly ones where problem 5 has a solution",
           sample_p5_solvable(4, 3, 150) + sample_p5_solvable(5, 4, 150) + sample_p5_solvable(6, 5, 60))
run_family("random 5x5 mazes, labels 1..2", [[[random.randint(1, 2) for _ in range(5)] for _ in range(5)]
                                              for _ in range(300)])

print("== page vs raw enumeration of move sequences (no state, condition checked on the whole sequence)")
BUDGET = 60000
agree, total, concl, concl_none, found, lens = True, 0, 0, 0, 0, []
p5_conclusive = True
for trial in range(700):
    n = random.choice([2, 3, 3, 4, 4, 4, 5, 5, 5])
    hi = random.choice([n, n, n - 1]) if n > 2 else n
    M = [[random.randint(1, max(1, hi)) for _ in range(n)] for _ in range(n)]
    for reading in ("pass", "stop"):
        stop = reading == "stop"
        cnts = walk_counts(M, 4 * n ** 4, stop)
        L = max(m for m in range(len(cnts)) if cnts[m] <= BUDGET)
        rw = raw_min(M, L, stop)
        pa = page_all(stop_version(M) if stop else M)
        lens.append(L)
        for k in VALID:
            total += 1
            exp = pa[k] if pa[k] is not None and pa[k] <= L else None
            if rw[k] != exp:
                agree = False
                print("    MISMATCH", reading, M, k, pa[k], rw[k], L)
            if L >= bound(n, k) or cnts[-1] == cnts[L]:  # past the pigeonhole bound, or every sequence enumerated
                concl += 1
                concl_none += pa[k] is None
            found += rw[k] is not None
        rw5 = raw_min(M, n - 1, stop)
        p5_conclusive &= rw5[5] == pa[5]
check(f"raw enumeration (budget {BUDGET} sequences, L from {min(lens)} to {max(lens)}): every page answer <= L "
      f"found by the raw search, and nothing found when the page says > L or none",
      agree, f"{total} comparisons, {found} with a solution found; {concl} conclusive by the length bound "
             f"(of which {concl_none} 'no solution')")
check("problem 5: raw enumeration up to n - 1 moves (conclusive bound) equals the page on every random maze",
      p5_conclusive)

# the pigeonhole bounds themselves, on mazes small and sparse enough to enumerate past them
mism, cmp = [], 0
for M in [[list(t[:2]), list(t[2:])] for t in itertools.product((1, 2), repeat=4)]:
    for k in (1, 2, 3, 4, 5):
        rw = raw_min(M, bound(2, k))
        cmp += 1
        if rw[k] != page_answer(M, k):
            mism.append((M, k))
check("all 2x2 mazes, labels 1..2: raw enumeration up to the pigeonhole bound (3, 8, 19, 16, 1 moves) equals the "
      "page for problems 1-5", not mism, f"{cmp} comparisons, mismatches: {mism[:3]}")

# ============================================================================ sizes and running times
print("== vertex and edge counts against the page's bounds")
BOUNDS = {  # problem: (graph builder, V formula, E bound)
    1: (page1, lambda n: n * n, lambda n: 4 * n * n),
    2: (page2, lambda n: 2 * n * n + 1, lambda n: 4 * n * n + 2),
    3: (page3, lambda n: 5 * n * n, lambda n: 20 * n * n),
    4: (page4, lambda n: 4 * n * n + 1, lambda n: 12 * n * n + 3),
    5: (page5, lambda n: n * n + 1, lambda n: 4 * n * n + 2 * n),
    "5d": (page5_direct, lambda n: n ** 3, lambda n: 4 * n ** 3),
    6: (page6, lambda n: n ** 4, lambda n: 16 * n ** 4),
}
for k, (build, Vf, Ef) in BOUNDS.items():
    ok, maxratio = True, 0.0
    for n in range(1, 9 if k != 6 else 7):
        mazes = [[[1] * n for _ in range(n)]]  # the all-1 maze: every square has as many moves as possible
        for hi in (1, 2, max(1, n - 1), n):
            mazes += [[[random.randint(1, hi) for _ in range(n)] for _ in range(n)] for _ in range(20 if n < 6 else 4)]
        for M in mazes:
            adj = build(M)
            V, E = len(adj), nedges(adj)
            ok &= V == Vf(n) and E <= Ef(n)
            maxratio = max(maxratio, E / Ef(n))
    check(f"problem {k}: V = formula and E <= bound on random mazes, n = 1..8 (n = 1..6 for problem 6)", ok,
          f"largest E / bound = {maxratio:.3f}")
check("problem 2: from (1,1) only the moves right and down can stay on the board (s has at most 2 edges)",
      all(d in "RD" for n in range(1, 8) for M in [[[random.randint(1, n) for _ in range(n)] for _ in range(n)]]
          for d, _, _ in moves(M, (0, 0))))

dag5 = dag5d = True
for _ in range(400):
    n = random.randint(1, 6)
    M = [[random.randint(1, n) for _ in range(n)] for _ in range(n)]
    dag5 &= is_dag(page5(M))
    dag5d &= is_dag(page5_direct(M))
check("problem 5: both graphs are dags (labels strictly increase along square-to-square edges)", dag5 and dag5d)


def topo_by_capped_label(M):
    """Problem 5's DP order on the page: squares by label capped at n (counting sort, stable), then t."""
    n = len(M)
    buckets = [[] for _ in range(n + 1)]
    for p in squares(n):
        buckets[min(M[p[0]][p[1]], n)].append(p)
    return [p for bk in buckets for p in bk] + ["t"]


topo_ok, cap_ok = True, True
for _ in range(400):
    n = random.randint(1, 6)
    M = [[random.randint(1, 2 * n) for _ in range(n)] for _ in range(n)]
    adj = page5(M)
    pos = {v: i for i, v in enumerate(topo_by_capped_label(M))}
    topo_ok &= all(pos[u] < pos[v] for u in adj for v in adj[u])
    capped = [[min(x, n) for x in row] for row in M]
    cap_ok &= {u: sorted(map(str, v)) for u, v in page5(capped).items()} == {u: sorted(map(str, v))
                                                                             for u, v in adj.items()}
check("problem 5: capping labels at n changes no edge, and squares by capped label (then t) is a topological order",
      topo_ok and cap_ok)

two_ok = True
for M in [[[a]] for a in (1, 2)] + [[[random.randint(1, random.choice([2, 3, 5])) for _ in range(n)] for _ in range(n)]
                                     for n in (2, 3, 4, 5) for _ in range(300)]:
    n = len(M)
    G = (n - 1, n - 1)
    adj = page2(M)
    c = [bfs(adj, ((0, 0), a)).get((G, b)) for a in "HV" for b in "HV"]
    c = [x for x in c if x is not None]
    two_ok &= (min(c) if c else None) == page_answer(M, 2)
check("problem 2: BFS from each of the two copies of (1,1), keeping the smaller distance, gives the page's answer "
      "(n = 1 included)", two_ok)
ones = [[1, 1], [1, 1]]
check("problems 1-4 and 6: the graphs of the all-1 2x2 maze have cycles (not dags in general)",
      not any(is_dag(b(ones)) for b in (page1, page2, page3, page4, page6)))

print("== graph size and BFS work on growing mazes")
for k, sizes in ((1, (16, 32, 64)), (2, (16, 32, 64)), (3, (16, 32, 64)), (4, (16, 32, 64)), (5, (16, 32, 64)),
                 ("5d", (8, 16, 32)), (6, (6, 9, 12))):
    build, Vf, Ef = BOUNDS[k]
    unit_name = "n^4" if k == 6 else "n^3" if k == "5d" else "n^2"
    ok, sizes_r, work_r = True, [], []
    for n in sizes:
        unit = n ** 4 if k == 6 else n ** 3 if k == "5d" else n * n
        # labels increasing along the anti-diagonals make problem 5 traverse a large part of its graph
        M = ([[min(n - 1, 1 + i + j) for j in range(n)] for i in range(n)] if k in (5, "5d") else
             [[1 if random.random() < 0.6 else random.randint(1, n - 1) for _ in range(n)] for _ in range(n)])
        adj = build(M)
        size = len(adj) + nedges(adj)
        start = {1: (0, 0), 2: "s", 3: ((0, 0), 0), 4: "s", 5: (0, 0), "5d": ((0, 0), 0),
                 6: ((0, 0), (n - 1, n - 1))}[k]
        BFS_OPS[0] = 0
        bfs(adj, start)
        ok &= size <= Vf(n) + Ef(n) and BFS_OPS[0] <= size
        sizes_r.append(size / unit)
        work_r.append(BFS_OPS[0] / unit)
    check(f"problem {k}: graph size V + E <= the bounds and BFS work <= V + E, n = {sizes}", ok,
          f"(V+E)/{unit_name} = " + " ".join(f"{r:.2f}" for r in sizes_r)
          + f"; BFS work/{unit_name} = " + " ".join(f"{r:.2f}" for r in work_r))

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: {FAIL}")
