#!/usr/bin/env python3
"""Checks for every concrete claim on content/2-algorithms/02-backtracking.md and the concept pages
backtracking.md, subset-sum.md, longest-increasing-subsequence.md.

Each algorithm is implemented exactly as the page's pseudocode / recurrence states it (1-indexed arrays with a
dummy slot 0 where the book uses A[0]) and compared with brute force."""
import math
import random
import sys
from functools import lru_cache
from itertools import combinations, permutations, product

sys.setrecursionlimit(100000)
FAIL = []


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAIL.append(name)


random.seed(374)
NEG_INF = float("-inf")

# =====================================================================================================
# 2.1 N queens
# =====================================================================================================


def place_queens_all(n):
    """PlaceQueens exactly as in the book's Figure 2.2. Returns (solutions in print order, calls per level)."""
    Q = [0] * (n + 1)
    printed, level = [], {}

    def PlaceQueens(r):
        level[r - 1] = level.get(r - 1, 0) + 1  # depth = number of queens already placed
        if r == n + 1:
            printed.append(tuple(Q[1:]))
        else:
            for j in range(1, n + 1):
                legal = True
                for i in range(1, r):
                    if Q[i] == j or Q[i] == j + r - i or Q[i] == j - r + i:
                        legal = False
                if legal:
                    Q[r] = j
                    PlaceQueens(r + 1)
    PlaceQueens(1)
    return printed, [level.get(d, 0) for d in range(n + 1)]


def is_solution(q):
    n = len(q)
    return all(q[a] != q[b] and abs(q[a] - q[b]) != b - a for a in range(n) for b in range(a + 1, n))


def brute_queens(n):
    return sorted(p for p in permutations(range(1, n + 1)) if is_solution(p))


counts = {}
calls = {}
for n in range(1, 10):
    sols, lv = place_queens_all(n)
    counts[n] = len(sols)
    calls[n] = sum(lv)
    bf = brute_queens(n)
    check(f"PlaceQueens n={n}: prints exactly the {len(bf)} solutions, each once, in lexicographic order",
          sols == bf, f"{len(sols)} printed")
# n = 10 by the algorithm only (brute force over 10! permutations is slow but still feasible; do it once)
sols10, lv10 = place_queens_all(10)
counts[10], calls[10] = len(sols10), sum(lv10)
check("PlaceQueens n=10: 724 solutions, all valid and distinct",
      len(sols10) == 724 and len(set(sols10)) == 724 and all(is_solution(s) for s in sols10))
check("solution counts n=1..10 are 1,0,0,2,10,4,40,92,352,724",
      [counts[n] for n in range(1, 11)] == [1, 0, 0, 2, 10, 4, 40, 92, 352, 724], str(counts))
check("call counts n=1..10 are 2,3,6,17,54,153,552,2057,8394,35539",
      [calls[n] for n in range(1, 11)] == [2, 3, 6, 17, 54, 153, 552, 2057, 8394, 35539], str(calls))
check("Gauss's first solution [5,7,1,4,2,8,6,3] is an 8-queens solution", is_solution((5, 7, 1, 4, 2, 8, 6, 3)))
check("... and PlaceQueens prints it", (5, 7, 1, 4, 2, 8, 6, 3) in place_queens_all(8)[0])
s4, lv4 = place_queens_all(4)
check("4 queens: solutions [2,4,1,3] and [3,1,4,2]", s4 == [(2, 4, 1, 3), (3, 1, 4, 2)])
check("4 queens: recursion tree has 17 nodes, 1,4,6,4,2 per level", lv4 == [1, 4, 6, 4, 2] and sum(lv4) == 17, str(lv4))


def queens_tree(n):
    """The recursion tree as nested (partial, [children]); used for leaf counts and for the figure."""
    def rec(q):
        r = len(q) + 1
        kids = []
        if r <= n:
            for j in range(1, n + 1):
                if all(not (q[i - 1] == j or q[i - 1] == j + r - i or q[i - 1] == j - r + i) for i in range(1, r)):
                    kids.append(rec(q + (j,)))
        return (q, kids)
    return rec(())


def leaves(t):
    return [t[0]] if not t[1] else [x for k in t[1] for x in leaves(k)]


L4 = leaves(queens_tree(4))
check("4 queens: 6 leaves, 2 complete solutions and 4 dead ends",
      len(L4) == 6 and sum(len(q) == 4 for q in L4) == 2, str(L4))
check("4 queens leaves are (1,3), (1,4,2), (2,4,1,3), (3,1,4,2), (4,1,3), (4,2)",
      L4 == [(1, 3), (1, 4, 2), (2, 4, 1, 3), (3, 1, 4, 2), (4, 1, 3), (4, 2)])
# the diagonal test: Q[i] = j + r - i or Q[i] = j - r + i  <=>  |Q[i] - j| = r - i   (i < r)
check("diagonal test equals |Q[i]-j| = r-i for all 1<=i<r<=9, 1<=j,Q[i]<=9",
      all(((qi == j + r - i) or (qi == j - r + i)) == (abs(qi - j) == r - i)
          for r in range(1, 10) for i in range(1, r) for j in range(1, 10) for qi in range(1, 10)))
# node counts at depth d are at most n!/(n-d)! (distinct columns); total calls <= e * n!
ok = True
for n in range(1, 11):
    lv = place_queens_all(n)[1] if n < 10 else lv10
    ok &= all(lv[d] <= math.factorial(n) // math.factorial(n - d) for d in range(n + 1))
    ok &= sum(lv) <= math.e * math.factorial(n)
check("level d of the recursion tree has <= n!/(n-d)! nodes; total calls <= e*n!  (n<=10)", ok)
# the recurrence T(m) <= m T(m-1) + c n^2, solved: T(m) <= c n^2 * sum_{k<=m} m!/k! <= e c n^2 m!
ok = True
for m in range(0, 15):
    Tm = 1.0
    for k in range(1, m + 1):
        Tm = k * Tm + 1.0
    ok &= Tm <= math.e * math.factorial(m) + 1e-9
check("T(m) = m T(m-1) + 1, T(0)=1 stays below e*m! for m<=14", ok)
check("8 queens: 2057 calls vs 8! = 40320", calls[8] == 2057 and math.factorial(8) == 40320)

# =====================================================================================================
# 2.2 Game trees: PlayAnyGame on the subtraction game (take 1 or 2; whoever takes the last token wins)
# =====================================================================================================


def PlayAnyGame(n, trace=None):
    """State = pile size n, player to move implicit. 'Already lost' = facing an empty pile."""
    if trace is not None:
        trace.append(n)
    if n == 0:
        return "Bad"          # the opponent took the last token: the player to move has lost
    for take in (1, 2):       # legal moves, tried in this order
        if take <= n:
            if PlayAnyGame(n - take, trace) == "Bad":
                return "Good"
    return "Bad"


check("subtraction game: state n is Bad iff n is a multiple of 3 (n <= 30)",
      all((PlayAnyGame(n) == "Bad") == (n % 3 == 0) for n in range(31)))


def game_tree(n):
    return (n, [game_tree(n - t) for t in (1, 2) if t <= n])


def size(t):
    return 1 + sum(size(k) for k in t[1])


def label(t):
    """Good iff some child is Bad; a leaf (n = 0) is Bad."""
    n, kids = t
    if not kids:
        return "Bad"
    return "Good" if any(label(k) == "Bad" for k in kids) else "Bad"


G4 = game_tree(4)
check("game tree from 4 tokens has 12 nodes and 5 leaves", size(G4) == 12 and len(leaves(G4)) == 5)
check("labels in the figure: 4 G; 3 B; 2 G; 1 G; 0 B (every node with the same pile has the same label)",
      all(label(game_tree(n)) == lab for n, lab in [(4, "Good"), (3, "Bad"), (2, "Good"), (1, "Good"), (0, "Bad")]))
check("from 4 the winning move is take 1 (to 3, Bad); take 2 (to 2) is Good for the opponent",
      label(game_tree(3)) == "Bad" and label(game_tree(2)) == "Good")
tr = []
PlayAnyGame(4, tr)
check("PlayAnyGame(4) makes 8 calls (visits 3,2,1,0,0,1,0 below the root) and skips the 4-node subtree of 2",
      tr == [4, 3, 2, 1, 0, 0, 1, 0] and size(game_tree(2)) == 4 and len(tr) == 12 - 4, str(tr))


def fib(k):
    a, b = 0, 1
    for _ in range(k):
        a, b = b, a + b
    return a


Ng = [1, 2]
for n in range(2, 30):
    Ng.append(1 + Ng[n - 1] + Ng[n - 2])
check("game-tree size N(n) = 1 + N(n-1) + N(n-2), N(0)=1, N(1)=2, equals F(n+3) - 1 and the drawn tree size",
      all(Ng[n] == fib(n + 3) - 1 == size(game_tree(n)) for n in range(20)))
ok = True
for n in range(0, 25):
    tr = []
    PlayAnyGame(n, tr)
    ok &= len(tr) <= Ng[n]
check("PlayAnyGame(n) makes at most N(n) calls (the size of the game tree), n < 25", ok)

# the "no draws" qualifier: with a drawn terminal state, Good no longer means "can force a win"
def play_generic(state, moves, won, lost):
    if won(state):
        return "Good"
    if lost(state):
        return "Bad"
    for y in moves(state):
        if play_generic(y, moves, won, lost) == "Bad":
            return "Good"
    return "Bad"


DRAW_GAME = {"start": ["draw"], "draw": []}   # one move, into a finished game that nobody won
check("with a draw, PlayAnyGame returns Good from a state whose only continuation is a draw (so the page restricts to no draws)",
      play_generic("start", DRAW_GAME.__getitem__, lambda s: False, lambda s: False) == "Good")
phi = (1 + 5 ** 0.5) / 2
r = [Ng[n] / phi ** n for n in (20, 25, 29)]
check("N(n) / phi^n settles (Theta(phi^n))", abs(r[0] - r[2]) < 1e-3, str(r))

# =====================================================================================================
# 2.3 Subset sum
# =====================================================================================================


def subsets_summing(X, T):
    return [set(c) for k in range(len(X) + 1) for c in combinations(X, k) if sum(c) == T]


S1 = subsets_summing([8, 6, 7, 5, 3, 10, 9], 15)
check("X={8,6,7,5,3,10,9}, T=15: exactly the four subsets {8,7},{7,5,3},{6,9},{5,10}",
      sorted(map(sorted, S1)) == sorted(map(sorted, [{8, 7}, {7, 5, 3}, {6, 9}, {5, 10}])), str(S1))
check("X={11,6,5,1,7,13,12}, T=15: no subset", subsets_summing([11, 6, 5, 1, 7, 13, 12], 15) == [])


def SubsetSumSet(X, T):
    """The set version: any x in X."""
    if T == 0:
        return True
    elif T < 0 or not X:
        return False
    else:
        x = random.choice(sorted(X))
        rest = X - {x}
        return SubsetSumSet(rest, T - x) or SubsetSumSet(rest, T)


CALLS = [0]


def SubsetSum(X, i, T):
    """Index version: does any subset of X[1..i] sum to T?  (X[0] is a dummy.)"""
    CALLS[0] += 1
    if T == 0:
        return True
    elif T < 0 or i == 0:
        return False
    else:
        with_ = SubsetSum(X, i - 1, T - X[i])
        wout = SubsetSum(X, i - 1, T)
        return with_ or wout


def brute_ss(xs, T):
    return any(sum(c) == T for k in range(len(xs) + 1) for c in combinations(xs, k))


ok_set = ok_idx = True
for n in range(0, 6):
    for xs in product(range(1, 6), repeat=n):
        for T in range(-2, sum(xs) + 3):
            b = brute_ss(xs, T)
            ok_idx &= SubsetSum([0] + list(xs), n, T) == b
            if len(set(xs)) == n:
                ok_set &= SubsetSumSet(set(xs), T) == b
for _ in range(300):
    xs = [random.randint(1, 30) for _ in range(random.randint(0, 9))]
    T = random.randint(-3, 120)
    ok_idx &= SubsetSum([0] + xs, len(xs), T) == brute_ss(xs, T)
check("SubsetSum(X, i, T) = brute force (all arrays over 1..5 up to length 5, all T; 300 random)", ok_idx)
check("set version SubsetSum(X, T) = brute force (distinct elements)", ok_set)
ok = True
for n in range(0, 13):
    xs = [random.randint(1, 9) for _ in range(n)]
    CALLS[0] = 0
    SubsetSum([0] + xs, n, sum(xs) + 1)
    ok &= CALLS[0] == 2 ** (n + 1) - 1
check("T > sum(X): exactly 2^(n+1) - 1 calls (complete binary recursion tree of depth n), n <= 12", ok)
# T(n) = 2T(n-1) + 1 solves to 2^(n+1) - 1 = Theta(2^n): exact closed form
t = [1]
for n in range(1, 30):
    t.append(2 * t[-1] + 1)
check("recurrence T(n) = 2T(n-1) + 1, T(0) = 1 has T(n) = 2^(n+1) - 1", all(t[n] == 2 ** (n + 1) - 1 for n in range(30)))


def ConstructSubset(X, i, T):
    """Figure 2.6 with the base case 'i = 0' (the book prints 'n = 0'). Returns a list or None."""
    if T == 0:
        return []
    if T < 0 or i == 0:
        return None
    Y = ConstructSubset(X, i - 1, T)
    if Y is not None:
        return Y
    Y = ConstructSubset(X, i - 1, T - X[i])
    if Y is not None:
        return Y + [X[i]]
    return None


ok = True
for n in range(0, 6):
    for xs in product(range(1, 6), repeat=n):
        for T in range(-1, sum(xs) + 2):
            Y = ConstructSubset([0] + list(xs), n, T)
            if brute_ss(xs, T):
                # Y must be a sub-multiset of xs summing to T
                ok &= Y is not None and sum(Y) == T and all(Y.count(v) <= list(xs).count(v) for v in Y)
            else:
                ok &= Y is None
check("ConstructSubset (base case i = 0) returns a subset summing to T iff one exists", ok)


def ConstructSubsetLiteral(X, i, T, n, depth=0):
    """The book's printed version: base case 'T < 0 or n = 0' with n the (fixed) array length."""
    if depth > 50:
        return "runaway"
    if T == 0:
        return []
    if T < 0 or n == 0:
        return None
    if i < 1:
        return "index<1"   # would read X[0], X[-1], ...
    Y = ConstructSubsetLiteral(X, i - 1, T, n, depth + 1)
    if Y is not None:
        return Y
    Y = ConstructSubsetLiteral(X, i - 1, T - X[i], n, depth + 1)
    if isinstance(Y, list):
        return Y + [X[i]]
    return Y


check("book's literal 'n = 0' test recurses below i = 1 (e.g. X = [5], T = 3)",
      ConstructSubsetLiteral([0, 5], 1, 3, 1) == "index<1")
# concept page example: X = [3,5,6,8], T = 14
check("concept: subsets of [3,5,6,8] summing to 14 are exactly {3,5,6} and {6,8}",
      sorted(map(sorted, subsets_summing([3, 5, 6, 8], 14))) == [[3, 5, 6], [6, 8]])
check("concept: ConstructSubset([3,5,6,8], 4, 14) returns {3,5,6} (exclude-first order)",
      sorted(ConstructSubset([0, 3, 5, 6, 8], 4, 14)) == [3, 5, 6])


def first_found_with_first(X, i, T):
    """The subset SubsetSum's search reaches first: 'with' is evaluated before 'wout'."""
    if T == 0:
        return []
    if T < 0 or i == 0:
        return None
    Y = first_found_with_first(X, i - 1, T - X[i])
    if Y is not None:
        return Y + [X[i]]
    return first_found_with_first(X, i - 1, T)


check("concept: SubsetSum([3,5,6,8], 4, 14) is True and its first success (with-first order) is {6,8}",
      SubsetSum([0, 3, 5, 6, 8], 4, 14) and sorted(first_found_with_first([0, 3, 5, 6, 8], 4, 14)) == [6, 8])
check("concept: no subset of [3,5,6,8] sums to 12", not brute_ss([3, 5, 6, 8], 12))


def FastSubsetSum(X, T):
    """Chapter 3 DP: S[i][t] = SS(i, t) = some subset of X[i..n] sums to t; rows i = n+1 down to 1."""
    n = len(X) - 1
    S = [[False] * (T + 1) for _ in range(n + 2)]
    S[n + 1][0] = True
    for i in range(n, 0, -1):
        S[i][0] = True
        for t in range(1, T + 1):
            S[i][t] = S[i + 1][t] or (t >= X[i] and S[i + 1][t - X[i]])
    return S


ok = True
for _ in range(400):
    xs = [random.randint(1, 12) for _ in range(random.randint(0, 8))]
    T = random.randint(0, 50)
    S = FastSubsetSum([0] + xs, T)
    ok &= all(S[i][t] == brute_ss(xs[i - 1:], t) for i in range(1, len(xs) + 2) for t in range(T + 1))
check("FastSubsetSum table: S[i][t] = (some subset of X[i..n] sums to t), 400 random instances", ok)
S = FastSubsetSum([0, 3, 5, 6, 8], 14)
row1 = [t for t in range(15) if S[1][t]]
check("concept: sums reachable from [3,5,6,8] within 0..14 are 0,3,5,6,8,9,11,13,14",
      row1 == [0, 3, 5, 6, 8, 9, 11, 13, 14], str(row1))


def NoAdj(X, i, t):
    """Concept page example: some subset of X[1..i] with no two adjacent indices sums to t."""
    if t == 0:
        return True
    if t < 0 or i <= 0:
        return False
    return NoAdj(X, i - 1, t) or NoAdj(X, i - 2, t - X[i])


def brute_noadj(xs, t):
    n = len(xs)
    for mask in range(1 << n):
        if mask & (mask >> 1):
            continue
        if sum(xs[k] for k in range(n) if mask >> k & 1) == t:
            return True
    return False


ok = True
for n in range(0, 7):
    for xs in product(range(1, 5), repeat=n):
        for t in range(-1, sum(xs) + 2):
            ok &= NoAdj([0] + list(xs), n, t) == brute_noadj(xs, t)
check("concept: NoAdj(i, t) = brute force over non-adjacent subsets (all arrays over 1..4 up to length 6)", ok)
check("concept: X = [4,1,2,7,3]: 10 = 7+3 = 1+2+7 = 4+1+2+3 but no non-adjacent subset sums to 10; 9 = 4+2+3 does",
      brute_ss([4, 1, 2, 7, 3], 10) and not NoAdj([0, 4, 1, 2, 7, 3], 5, 10) and not brute_noadj([4, 1, 2, 7, 3], 10)
      and NoAdj([0, 4, 1, 2, 7, 3], 5, 9) and 4 + 2 + 3 == 9)
NA = sorted({t for t in range(0, 18) if brute_noadj([4, 1, 2, 7, 3], t)})
check("concept: non-adjacent subset sums of [4,1,2,7,3] are 0..9 and 11", NA == list(range(10)) + [11], str(NA))
X5 = [4, 1, 2, 7, 3]
S10 = [c for k in range(6) for c in combinations(range(5), k) if sum(X5[q] for q in c) == 10]
check("concept: the subsets of [4,1,2,7,3] summing to 10 are {7,3}, {1,2,7}, {4,1,2,3}, each with two neighbors",
      sorted(sorted(X5[q] for q in c) for c in S10) == [[1, 2, 3, 4], [1, 2, 7], [3, 7]]
      and all(any(c[k + 1] == c[k] + 1 for k in range(len(c) - 1)) for c in S10))
ok = True
for n in range(0, 25):
    calls_na = [0]

    def NoAdjC(i, t, X):
        calls_na[0] += 1
        if t == 0:
            return True
        if t < 0 or i <= 0:
            return False
        return NoAdjC(i - 1, t, X) or NoAdjC(i - 2, t - X[i], X)
    NoAdjC(n, 10 ** 9, [0] + [1] * n)
    ok &= calls_na[0] <= 3 * (fib(n + 3))
check("concept: NoAdj makes O(phi^n) calls (at most 3 F(n+3) on an unreachable target, n < 25)", ok)

# =====================================================================================================
# 2.5 Text segmentation
# =====================================================================================================
check("BOTH EARTH AND SATURN SPIN = BOT HEART HANDS AT URNS PIN = BOTHEARTHANDSATURNSPIN",
      "".join("BOTH EARTH AND SATURN SPIN".split()) == "".join("BOT HEART HANDS AT URNS PIN".split())
      == "BOTHEARTHANDSATURNSPIN")
check("BLUE STEM UNIT ROBOT and BLUEST EMU NITRO BOT are both BLUESTEMUNITROBOT (17 letters)",
      "".join("BLUE STEM UNIT ROBOT".split()) == "".join("BLUEST EMU NITRO BOT".split()) == "BLUESTEMUNITROBOT"
      and len("BLUESTEMUNITROBOT") == 17)
WORDS = {"HE", "HEAR", "HEART", "HEARTH", "THAN", "HAND", "HANDS", "AND", "SAT", "SATURN", "AT", "URN", "URNS",
         "TURN", "SPIN", "PIN", "IN", "EARTH", "ART", "ARTH", "BOT", "BOTH", "TH"}
SUF = "HEARTHANDSATURNSPIN"
check("prefixes of HEARTHANDSATURNSPIN among {HE, HEAR, HEART, HEARTH, ...} are the four next-word choices",
      [SUF[:k] for k in range(1, len(SUF) + 1) if SUF[:k] in {"HE", "HEAR", "HEART", "HEARTH"}]
      == ["HE", "HEAR", "HEART", "HEARTH"])
check("ROTATOR is a palindrome, PALINDROME is not", "ROTATOR" == "ROTATOR"[::-1] and "PALINDROME" != "PALINDROME"[::-1])


def make_splittable_array(isword):
    def Splittable(A):
        n = len(A)
        if n == 0:
            return True
        for i in range(1, n + 1):
            if isword(A[:i]):
                if Splittable(A[i:]):
                    return True
        return False
    return Splittable


def make_splittable_index(A, isword, counter=None):
    n = len(A)

    def IsWord(i, j):
        if counter is not None:
            counter[0] += 1
        return isword(A[i - 1:j])

    def Splittable(i):
        if i > n:
            return True
        for j in range(i, n + 1):
            if IsWord(i, j):
                if Splittable(j + 1):
                    return True
        return False
    return Splittable


def segmentations(s):
    """All ways to split s into nonempty pieces."""
    if not s:
        yield []
        return
    for k in range(1, len(s) + 1):
        for rest in segmentations(s[k:]):
            yield [s[:k]] + rest


D = {"a", "ab", "ba", "bab", "bb", "aab"}
isw = D.__contains__
ok = True
for n in range(0, 11):
    for tup in product("ab", repeat=n):
        s = "".join(tup)
        b = any(all(p in D for p in seg) for seg in segmentations(s)) if n <= 10 else None
        ok &= make_splittable_array(isw)(s) == b == make_splittable_index(s, isw)(1)
check("Splittable(A[1..n]) = Splittable(1) = brute force, dictionary {a,ab,ba,bab,bb,aab}, all strings <= 10", ok)
ispal = lambda w: w == w[::-1]
ok = all(make_splittable_index(s, ispal)(1) for s in ["".join(t) for n in range(0, 9) for t in product("ab", repeat=n)])
check("with IsWord = palindrome every string is splittable (single letters are palindromes)", ok)
check("a string of length n >= 1 has 2^(n-1) segmentations (n <= 12)",
      all(sum(1 for _ in segmentations("x" * n)) == 2 ** (n - 1) for n in range(1, 13)))
ok = True
for n in range(1, 17):
    s = "a" * (n - 1) + "b"
    cnt = [0]
    res = make_splittable_index(s, lambda w: len(w) > 0 and set(w) == {"a"}, cnt)(1)
    ok &= (res is False) and cnt[0] == 2 ** n - 1
check("a^(n-1)b with words = nonempty runs of a: not splittable, exactly 2^n - 1 IsWord calls (n <= 16)", ok)
Cm = {1: 1}
for m in range(2, 20):
    Cm[m] = m + sum(Cm[k] for k in range(1, m))
check("C(m) = m + sum_{k<m} C(k), C(1) = 1 gives C(m) = 2^m - 1", all(Cm[m] == 2 ** m - 1 for m in Cm))
# full-history recurrence with alpha = 1: T(n) = sum_{i<n} T(i) + n, T(0) = 1  ->  T(n) = 2T(n-1) + 1 for n >= 2
T = [1]
for n in range(1, 40):
    T.append(sum(T) + n)
check("T(n) = sum_{i<n} T(i) + alpha n satisfies T(n) = 2T(n-1) + alpha for n >= 2",
      all(T[n] == 2 * T[n - 1] + 1 for n in range(2, 40)))
rat = [T[n] / 2 ** n for n in (30, 35, 39)]
check("... and T(n)/2^n settles (Theta(2^n))", abs(rat[0] - rat[2]) < 1e-6, str(rat))
# footnote: with a polynomial-time IsWord the time is still O(2^n): T(n) = sum T(i) + n * n^3
T = [1]
for n in range(1, 60):
    T.append(sum(T) + n * n ** 3)
rat = [T[n] / 2 ** n for n in (40, 50, 59)]
check("with IsWord costing n^3, T(n) = sum T(i) + n^4 is still Theta(2^n)", abs(rat[1] - rat[2]) / rat[2] < 1e-6, str(rat))


def make_maxscore(A, score):
    n = len(A)

    @lru_cache(maxsize=None)
    def MaxScore(i):
        if i > n:
            return 0
        return max(score(A[i - 1:j]) + MaxScore(j + 1) for j in range(i, n + 1))
    return MaxScore


ok = True
for _ in range(200):
    n = random.randint(0, 9)
    s = "".join(random.choice("abc") for _ in range(n))
    tbl = {}

    def score(w, tbl=tbl):
        if w not in tbl:
            tbl[w] = random.randint(-5, 9)
        return tbl[w]
    best = max(sum(score(p) for p in seg) for seg in segmentations(s))
    ok &= make_maxscore(s, score)(1) == best
check("MaxScore(1) = max over all segmentations of the summed scores (200 random strings and score tables)", ok)

# =====================================================================================================
# 2.6 / 2.7 Longest increasing subsequence
# =====================================================================================================


def is_subseq(x, s):
    it = iter(s)
    return all(c in it for c in x)


SB = "SUBSEQUENCEBACKTRACKING"
check("BENT, ACKACK, SQUARING, SUBSEQUENT are subsequences of SUBSEQUENCEBACKTRACKING",
      all(is_subseq(w, SB) for w in ["BENT", "ACKACK", "SQUARING", "SUBSEQUENT", "", SB]))
check("QUEUE, EQUUS, TALLYHO are not", not any(is_subseq(w, SB) for w in ["QUEUE", "EQUUS", "TALLYHO"]))
check("MASHER and LAUGHTER are subsequences of MANSLAUGHTER; only LAUGHTER is a substring",
      is_subseq("MASHER", "MANSLAUGHTER") and is_subseq("LAUGHTER", "MANSLAUGHTER")
      and "LAUGHTER" in "MANSLAUGHTER" and "MASHER" not in "MANSLAUGHTER")


def brute_lis(A):
    n = len(A)
    best = 0
    for mask in range(1 << n):
        seq = [A[k] for k in range(n) if mask >> k & 1]
        if all(seq[k] < seq[k + 1] for k in range(len(seq) - 1)):
            best = max(best, len(seq))
    return best


def LISbigger_arr(prev, A):
    """Array version (book p. 88)."""
    n = len(A)
    if n == 0:
        return 0
    elif A[0] <= prev:
        return LISbigger_arr(prev, A[1:])
    else:
        skip = LISbigger_arr(prev, A[1:])
        take = LISbigger_arr(A[0], A[1:]) + 1
        return max(skip, take)


def make_lisbigger(A, counter=None):
    """Index version on A[0..n] with A[0] = -inf; A passed 0-indexed with sentinel at position 0."""
    n = len(A) - 1

    def LISbigger(i, j):
        if counter is not None:
            counter[0] += 1
        if j > n:
            return 0
        elif A[i] >= A[j]:
            return LISbigger(i, j + 1)
        else:
            skip = LISbigger(i, j + 1)
            take = LISbigger(j, j + 1) + 1
            return max(skip, take)
    return LISbigger


def make_lisfirst(A, counter=None):
    n = len(A) - 1

    def LISfirst(i):
        if counter is not None:
            counter[0] += 1
        best = 0
        for j in range(i + 1, n + 1):
            if A[j] > A[i]:
                best = max(best, LISfirst(j))
        return 1 + best
    return LISfirst


def LIS_take1(A):
    return make_lisbigger([NEG_INF] + list(A))(0, 1)


def LIS_take2_loop(A):
    f = make_lisfirst([NEG_INF] + list(A))
    best = 0
    for i in range(1, len(A) + 1):
        best = max(best, f(i))
    return best


def LIS_take2_sentinel(A):
    return make_lisfirst([NEG_INF] + list(A))(0) - 1


def FastLIS(A):
    """Chapter 3: table LISbigger[i, j], 0 <= i <= n, 1 <= j <= n+1; columns j = n down to 1."""
    n = len(A)
    A = [NEG_INF] + list(A)
    T = [[0] * (n + 2) for _ in range(n + 1)]
    for i in range(0, n + 1):
        T[i][n + 1] = 0
    for j in range(n, 0, -1):
        for i in range(0, j):
            keep = 1 + T[j][j + 1]
            skip = T[i][j + 1]
            T[i][j] = skip if A[i] >= A[j] else max(keep, skip)
    return T[0][1], T, A


def FastLIS2(A):
    n = len(A)
    A = [NEG_INF] + list(A)
    L = [0] * (n + 1)
    for i in range(n, -1, -1):
        L[i] = 1
        for j in range(i + 1, n + 1):
            if A[j] > A[i] and 1 + L[j] > L[i]:
                L[i] = 1 + L[j]
    return L[0] - 1, L


ok1 = ok2 = ok3 = ok4 = ok5 = ok6 = True
cnt = 0
for n in range(0, 8):
    for A in product(range(1, 5), repeat=n):
        b = brute_lis(A)
        cnt += 1
        ok1 &= LISbigger_arr(NEG_INF, list(A)) == b
        ok2 &= LIS_take1(A) == b
        ok3 &= LIS_take2_loop(A) == b == LIS_take2_sentinel(A)
        ok4 &= FastLIS(A)[0] == b
        ok5 &= FastLIS2(A)[0] == b
for _ in range(300):
    A = [random.randint(-20, 20) for _ in range(random.randint(0, 12))]
    b = brute_lis(A)
    ok1 &= LISbigger_arr(NEG_INF, A) == b
    ok2 &= LIS_take1(A) == b
    ok3 &= LIS_take2_loop(A) == b == LIS_take2_sentinel(A)
    ok4 &= FastLIS(A)[0] == b
    ok5 &= FastLIS2(A)[0] == b
check(f"LISbigger(prev, A[1..n]) with prev = -inf = brute force ({cnt} arrays over 1..4, length <= 7, + 300 random)", ok1)
check("LIS via LISbigger(0, 1) with sentinel = brute force", ok2)
check("LIS via max_i LISfirst(i) and via LISfirst(0) - 1 = brute force", ok3)
check("FastLIS (table, columns right to left) = brute force", ok4)
check("FastLIS2 (array, i from n down to 0) = brute force", ok5)
# meaning of the functions, for every (i, j) / i on all small arrays


def brute_bigger(A, i, j):
    """LIS of A[j..n] with every element > A[i] (A has sentinel at 0)."""
    return brute_lis([a for a in A[j:] if a > A[i]])


def brute_first(A, i):
    return 1 + brute_lis([a for a in A[i + 1:] if a > A[i]])


for n in range(0, 7):
    for A0 in product(range(1, 4), repeat=n):
        A = [NEG_INF] + list(A0)
        f = make_lisbigger(A)
        g = make_lisfirst(A)
        ok6 &= all(f(i, j) == brute_bigger(A, i, j) for j in range(1, n + 2) for i in range(0, j))
        ok6 &= all(g(i) == brute_first(A, i) for i in range(0, n + 1))
        _, Tb, _ = FastLIS(A0)
        ok6 &= all(Tb[i][j] == brute_bigger(A, i, j) for j in range(1, n + 2) for i in range(0, j))
        ok6 &= FastLIS2(A0)[1] == [brute_first(A, i) for i in range(n + 1)]
check("every value LISbigger(i, j) (i < j) and LISfirst(i) matches its English definition (arrays over 1..3, n <= 6)",
      ok6)

PI = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5, 8, 9, 7, 9, 3, 2, 3, 8, 4, 6, 2, 6]
check("book's example has 23 elements (digits of pi)", len(PI) == 23 and "".join(map(str, PI)) == "31415926535897932384626")
inc = lambda c: all(PI[c[k]] < PI[c[k + 1]] for k in range(len(c) - 1))
check("LIS of the book's example has length 6 (brute force: some 6 indices increase, no 7 do; all four algorithms agree)",
      any(inc(c) for c in combinations(range(23), 6)) and not any(inc(c) for c in combinations(range(23), 7))
      and LIS_take1(PI) == 6 == LIS_take2_loop(PI) == FastLIS(PI)[0] == FastLIS2(PI)[0])
check("1,4,5,6,8,9 is an increasing subsequence of it (positions 3,5,8,12,13 ...)",
      is_subseq([1, 4, 5, 6, 8, 9], PI))
A = [NEG_INF] + PI
f = make_lisbigger(A)
check("take-1 picture: chosen 1,4,5,6 from A[1..10] is increasing and ends with A[8] = 6",
      is_subseq([1, 4, 5, 6], PI[:10]) and PI[7] == 6 and PI[10] == 5 and PI[11] == 8)
check("take-1 picture: A[11] = 5 <= 6 must be skipped; LISbigger(8, 11) = LISbigger(8, 12) = 2",
      f(8, 11) == 2 and f(8, 12) == 2 and A[11] <= A[8])
check("... so the partial solution 1,4,5,6 extends to an LIS of length 4 + 2 = 6", 4 + f(8, 11) == 6)
LF = [make_lisfirst(A)(i) for i in range(1, 24)]
check("LISfirst(1..23) on the example = 6 6 5 6 4 1 5 3 3 4 3 2 1 2 1 3 4 3 1 2 1 2 1",
      LF == [6, 6, 5, 6, 4, 1, 5, 3, 3, 4, 3, 2, 1, 2, 1, 3, 4, 3, 1, 2, 1, 2, 1], str(LF))
check("LISfirst(0) - 1 = 6 with the sentinel", make_lisfirst(A)(0) - 1 == 6)
cand = [(j, A[j]) for j in range(9, 24) if A[j] > A[8]]
check("take-2 picture: after A[8] = 6 the candidates are 8,9,7,9,8 at positions 12,13,14,15,19",
      cand == [(12, 8), (13, 9), (14, 7), (15, 9), (19, 8)], str(cand))
check("LISfirst(8) = 3 (6 then two more, e.g. 6,8,9)", make_lisfirst(A)(8) == 3)
lf = make_lisfirst(A)
check("LISfirst(8) = 1 + LISfirst(12): candidates 12,14 give 2, candidates 13,15,19 give 1",
      lf(8) == 1 + lf(12) and lf(12) == lf(14) == 2 and lf(13) == lf(15) == lf(19) == 1)
check("the maximum 6 of LISfirst is attained at i = 1, 2, 4", [i for i in range(1, 24) if lf(i) == 6] == [1, 2, 4])
# exact call counts on increasing input
ok = True
for n in range(0, 14):
    c = [0]
    make_lisbigger([NEG_INF] + list(range(n)), c)(0, 1)
    ok &= c[0] == 2 ** (n + 1) - 1
check("increasing input of length n: LISbigger(0, 1) makes exactly 2^(n+1) - 1 calls (n <= 13)", ok)
ok = True
for n in range(0, 14):
    c = [0]
    make_lisfirst([NEG_INF] + list(range(n)), c)(0)
    ok &= c[0] == 2 ** n
    c2 = [0]
    g = make_lisfirst([NEG_INF] + list(range(n)), c2)
    for i in range(1, n + 1):
        g(i)
    ok &= c2[0] == 2 ** n - 1
check("increasing input: LISfirst(0) makes 2^n calls; the loop over LISfirst(1..n) makes 2^n - 1 (n <= 13)", ok)
ok = True
for _ in range(200):
    A0 = [random.randint(0, 9) for _ in range(random.randint(0, 11))]
    c = [0]
    make_lisbigger([NEG_INF] + A0, c)(0, 1)
    ok &= c[0] <= 2 ** (len(A0) + 1) - 1
    c = [0]
    make_lisfirst([NEG_INF] + A0, c)(0)
    ok &= c[0] <= 2 ** len(A0)
check("on 200 random arrays the call counts never exceed those bounds", ok)
# concept page example
E = [5, 2, 8, 6, 3, 6, 9, 7]
AE = [NEG_INF] + E
check("concept: LISfirst(1..8) for 5 2 8 6 3 6 9 7 = 3 4 2 2 3 2 1 1",
      [make_lisfirst(AE)(i) for i in range(1, 9)] == [3, 4, 2, 2, 3, 2, 1, 1])
check("concept: LIS = 4 (e.g. 2,3,6,9 and 2,3,6,7); 2,3,6,6,9 is not increasing",
      brute_lis(E) == 4 and is_subseq([2, 3, 6, 9], E) and is_subseq([2, 3, 6, 7], E) and FastLIS2(E)[0] == 4)
check("concept: FastLIS2 array LISfirst[0..8] = 5 3 4 2 2 3 2 1 1", FastLIS2(E)[1] == [5, 3, 4, 2, 2, 3, 2, 1, 1],
      str(FastLIS2(E)[1]))
_, TE, _ = FastLIS(E)
check("concept: FastLIS table LISbigger[0, 1] = 4 and LISbigger[1, 2] = 2 (after 5: 8,9 or 6,9 or 6,7)",
      TE[0][1] == 4 and TE[1][2] == 2)

# =====================================================================================================
# 2.8 Optimal binary search trees
# =====================================================================================================


def all_trees(i, k):
    if i > k:
        yield None
        return
    for r in range(i, k + 1):
        for Lt in all_trees(i, r - 1):
            for Rt in all_trees(r + 1, k):
                yield (r, Lt, Rt)


def cost_def(t, f, depth=1):
    """Definition (*): sum of f[i] * (#ancestors of v_i, counting v_i itself)."""
    if t is None:
        return 0
    r, Lt, Rt = t
    return f[r] * depth + cost_def(Lt, f, depth + 1) + cost_def(Rt, f, depth + 1)


def cost_rec(t, f, i, k):
    """The recursive decomposition: sum f[i..k] + Cost(left) + Cost(right)."""
    if t is None:
        return 0
    r, Lt, Rt = t
    return sum(f[i:k + 1]) + cost_rec(Lt, f, i, r - 1) + cost_rec(Rt, f, r + 1, k)


OC_CALLS = [0]


def make_optcost(f, counter=None):
    def OptCost(i, k):
        if counter is not None:
            counter[0] += 1
        if i > k:
            return 0
        total = 0
        for j in range(i, k + 1):
            total += f[j]
        best = math.inf
        for r in range(i, k + 1):
            best = min(best, OptCost(i, r - 1) + OptCost(r + 1, k))
        return total + best
    return OptCost


ok_dec = ok_opt = True
for n in range(0, 8):
    for _ in range(12 if n < 7 else 4):
        f = [0] + [random.randint(0, 9) for _ in range(n)]
        trees = list(all_trees(1, n))
        ok_dec &= all(cost_def(t, f) == cost_rec(t, f, 1, n) for t in trees)
        oc = make_optcost(f)
        ok_opt &= oc(1, n) == min(cost_def(t, f) for t in trees)
        # every interval too
        if n <= 5:
            ok_opt &= all(oc(i, k) == min(cost_def(t, f) for t in all_trees(i, k))
                          for i in range(1, n + 1) for k in range(i - 1, n + 1))
check("Cost(T, f) definition (*) = recursive decomposition, every tree, n <= 7", ok_dec)
check("OptCost(i, k) = min over all BSTs on keys i..k (brute force), n <= 7", ok_opt)
check("number of BSTs enumerated for n = 0..8 is 1,1,2,5,14,42,132,429,1430",
      [sum(1 for _ in all_trees(1, n)) for n in range(9)] == [1, 1, 2, 5, 14, 42, 132, 429, 1430])
# example: keys A..G with f = 4 2 6 3 1 5 2
F = [0, 4, 2, 6, 3, 1, 5, 2]
keys = " ABCDEFG"
oc = make_optcost(F)
check("example: total frequency 23", sum(F) == 23)
check("example: OptCost(1, 7) = 49", oc(1, 7) == 49)
trees7 = list(all_trees(1, 7))
best7 = [t for t in trees7 if cost_def(t, F) == 49]
OPT = (3, (1, None, (2, None, None)), (6, (4, None, (5, None, None)), (7, None, None)))
check("example: the optimal tree is unique: C(A(-,B), F(D(-,E), G))", best7 == [OPT])
BAL = (4, (2, (1, None, None), (3, None, None)), (6, (5, None, None), (7, None, None)))
check("example: the perfectly balanced tree (root D) costs 56", cost_def(BAL, F) == 56)
check("example: optimal cost by depths 6*1 + (4+5)*2 + (2+3+2)*3 + 1*4 = 49", 6 * 1 + (4 + 5) * 2 + (2 + 3 + 2) * 3 + 1 * 4 == 49)
check("example: balanced cost by depths 3*1 + (2+5)*2 + (4+6+1+2)*3 = 56", 3 * 1 + (2 + 5) * 2 + (4 + 6 + 1 + 2) * 3 == 56)


def height(t):
    return 0 if t is None else 1 + max(height(t[1]), height(t[2]))


check("example: optimal tree has 4 levels, balanced has 3", height(OPT) == 4 and height(BAL) == 3)
root_vals = [oc(1, r - 1) + oc(r + 1, 7) for r in range(1, 8)]
check("example: OptCost(1,r-1) + OptCost(r+1,7) for r = 1..7 is 39 38 26 31 35 31 43",
      root_vals == [39, 38, 26, 31, 35, 31, 43], str(root_vals))
check("example: the minimum is at r = 3 (key C): 23 + 26 = 49", min(root_vals) == 26 and root_vals.index(26) == 2)
check("example: with root D the best is 23 + 31 = 54", root_vals[3] == 31
      and min(cost_def(t, F) for t in trees7 if t[0] == 4) == 54)
check("example: OptCost(1,2) = 8 (root A) and OptCost(4,7) = 18 (root F)",
      oc(1, 2) == 8 and oc(4, 7) == 18 and cost_def((1, None, (2, None, None)), F) == 8
      and cost_def((6, (4, None, (5, None, None)), (7, None, None)), F) == 18)
LR = [(oc(1, r - 1), oc(r + 1, 7)) for r in range(1, 8)]
check("example: (left, right) pairs = (0,39) (4,34) (8,18) (20,11) (26,9) (29,2) (43,0)",
      LR == [(0, 39), (4, 34), (8, 18), (20, 11), (26, 9), (29, 2), (43, 0)], str(LR))
ok = True
for n in range(1, 9):
    fh = [0] + [2 ** (n - i) for i in range(1, n + 1)]
    trs = list(all_trees(1, n))
    m = min(cost_def(t, fh) for t in trs)
    opt = [t for t in trs if cost_def(t, fh) == m]
    ok &= len(opt) == 1 and height(opt[0]) == n and all(t[1] is None for t in [opt[0]])
check("frequencies 2^(n-1), ..., 2, 1: the unique optimal tree is a path of depth n (root = smallest key), n <= 8", ok)
# the rotation argument: f[x] > sum of all later frequencies for halving frequencies
check("halving frequencies: each f[i] exceeds the sum of all later ones (n <= 30)",
      all(2 ** (n - i) > sum(2 ** (n - k) for k in range(i + 1, n + 1)) for n in range(1, 31) for i in range(1, n + 1)))
# exact number of calls: 3^n
ok = True
for n in range(0, 11):
    c = [0]
    make_optcost([0] + [1] * n, c)(1, n)
    ok &= c[0] == 3 ** n
check("OptCost(1, n) makes exactly 3^n calls (n <= 10), for any frequencies", ok)
# recurrence T(n) = sum_{k=1}^n (T(k-1) + T(n-k)) + alpha n  =>  T(n) = 3T(n-1) + alpha  (n >= 2)
T = [1]
for n in range(1, 30):
    T.append(sum(T[k - 1] + T[n - k] for k in range(1, n + 1)) + n)
check("T(n) = sum_k (T(k-1) + T(n-k)) + alpha n satisfies T(n) = 3T(n-1) + alpha for n >= 2",
      all(T[n] == 3 * T[n - 1] + 1 for n in range(2, 30)))
rat = [T[n] / 3 ** n for n in (20, 25, 29)]
check("... and T(n)/3^n settles (Theta(3^n))", abs(rat[0] - rat[2]) < 1e-6, str(rat))
# Catalan numbers
N = [1]
for n in range(1, 400):
    N.append(sum(N[r - 1] * N[n - r] for r in range(1, n + 1)))
check("N(n) = sum_{r=1}^{n} N(r-1) N(n-r), N(0) = 1: 1,1,2,5,14,42,132,429",
      N[:8] == [1, 1, 2, 5, 14, 42, 132, 429])
Nbook = [1]
for n in range(1, 6):
    Nbook.append(sum(Nbook[r - 1] * Nbook[n - r] for r in range(1, n)))
check("book's printed upper limit r = n-1 would give N(1) = 0 (so the sum must run to n)", Nbook[1] == 0)
check("N(n) = binom(2n, n)/(n+1)", all(N[n] == math.comb(2 * n, n) // (n + 1) for n in range(400)))
r1 = [N[n] * n ** 1.5 / 4 ** n for n in (100, 200, 399)]
check("N(n) n^{3/2} / 4^n -> 1/sqrt(pi) = 0.564...: N(n) = Theta(4^n / n^{3/2})",
      abs(r1[2] - 1 / math.sqrt(math.pi)) < 0.002, str(r1))
r2 = [N[n] * n ** 0.5 / 4 ** n for n in (100, 200, 399)]
check("N(n) sqrt(n) / 4^n -> 0, so the book's Theta(4^n / sqrt n) is not right", r2[2] < r2[1] < r2[0] < 0.01, str(r2))
check("3^n > N(n) for 1 <= n <= 16, 3^n < N(n) for every n >= 17 (checked to 399), and 3^n / N(n) -> 0",
      all(3 ** n > N[n] for n in range(1, 17)) and all(3 ** n < N[n] for n in range(17, 400))
      and 3 ** 399 / N[399] < 1e-40)
check("n = 7: 3^7 = 2187 calls vs 429 trees", 3 ** 7 == 2187 and N[7] == 429)

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: {FAIL}")
