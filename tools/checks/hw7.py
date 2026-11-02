"""Brute-force checks for the HW7 writeup recurrences. Every recurrence is implemented exactly as the
writeup states it (same parameters, same cases) and compared with exhaustive search on small inputs."""
import itertools, random, sys
from functools import lru_cache
random.seed(374)
fails = 0
def check(name, cond, detail=""):
    global fails
    print(("OK   " if cond else "FAIL ") + name + ("" if cond else "   " + str(detail)))
    if not cond: fails += 1

# ---------------------------------------------------------------- 1(a) longest common decreasing subsequence
def subsequences(X):
    for r in range(len(X) + 1):
        for idx in itertools.combinations(range(len(X)), r):
            yield tuple(X[i] for i in idx)

def is_subseq(P, X):
    it = iter(X)
    return all(any(c == x for x in it) for c in P)

def brute_lcds(A, B):
    best = 0
    for P in subsequences(A):
        if all(P[t] > P[t + 1] for t in range(len(P) - 1)) and is_subseq(P, B):
            best = max(best, len(P))
    return best

def lcds_dp(A, B):
    """Dec(i, j) = longest common decreasing subsequence of A[1..i], B[1..j] that ends with B[j]."""
    m, n = len(A), len(B)
    A = [None] + A; B = [None] + B
    Dec = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            skip = Dec[i - 1][j]
            if A[i] == B[j]:
                use = 1 + max([Dec[i - 1][k] for k in range(1, j) if B[k] > B[j]], default=0)
                Dec[i][j] = max(skip, use)
            else:
                Dec[i][j] = skip
    return max([Dec[m][j] for j in range(1, n + 1)], default=0), Dec

def lcds_fast(A, B):
    """the O(mn) version: running maximum inside each row"""
    m, n = len(A), len(B)
    A = [None] + A; B = [None] + B
    Dec = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        best = 0                       # max Dec[i-1][k] over k < j with B[k] > A[i]
        for j in range(1, n + 1):
            if A[i] == B[j]:
                Dec[i][j] = max(Dec[i - 1][j], 1 + best)
            else:
                Dec[i][j] = Dec[i - 1][j]
            if B[j] > A[i]:
                best = max(best, Dec[i - 1][j])
    return max([Dec[m][j] for j in range(1, n + 1)], default=0)

ok = True; cnt = 0
for m in range(0, 6):
    for n in range(0, 6):
        for _ in range(60):
            A = [random.randint(1, 4) for _ in range(m)]
            B = [random.randint(1, 4) for _ in range(n)]
            b = brute_lcds(A, B); d, _ = lcds_dp(A, B); f = lcds_fast(A, B)
            cnt += 1
            if not (b == d == f):
                ok = False; print("   mismatch", A, B, b, d, f)
check(f"1(a) Dec recurrence = O(mn) version = brute force on {cnt} random pairs (lengths <= 5, values 1..4)", ok)
A = [5, 3, 4, 1, 2]; B = [3, 5, 4, 2, 1]
ans, Dec = lcds_dp(A, B)
check("1(a) example A=[5,3,4,1,2], B=[3,5,4,2,1]: answer 3 (5,4,2 or 5,4,1)", ans == brute_lcds(A, B) == 3, ans)
print("     Dec table (rows i = 1..m, cols j = 1..n):")
for i in range(1, len(A) + 1):
    print("      ", Dec[i][1:])

# ---------------------------------------------------------------- 1(b) longest common palindromic subsequence
def brute_lcps(A, B):
    best = 0
    for P in subsequences(A):
        if P == P[::-1] and is_subseq(P, B):
            best = max(best, len(P))
    return best

def lcps_dp(A, B):
    """Pal(i, j, k, l) = longest common palindromic subsequence of A[i..j] and B[k..l]."""
    m, n = len(A), len(B)
    A = [None] + A; B = [None] + B
    @lru_cache(maxsize=None)
    def Pal(i, j, k, l):
        if i > j or k > l:
            return 0
        if A[i] == A[j] == B[k] == B[l]:
            if i == j or k == l:
                return 1
            return 2 + Pal(i + 1, j - 1, k + 1, l - 1)
        return max(Pal(i + 1, j, k, l), Pal(i, j - 1, k, l), Pal(i, j, k + 1, l), Pal(i, j, k, l - 1))
    return Pal(1, m, 1, n)

def lcps_iter(A, B):
    """the same recurrence filled by nested loops: i down, j up, k down, l up"""
    m, n = len(A), len(B)
    A = [None] + A; B = [None] + B
    P = {}
    def get(i, j, k, l):
        return 0 if (i > j or k > l) else P[(i, j, k, l)]
    for i in range(m + 1, 0, -1):
        for j in range(i - 1, m + 1):
            for k in range(n + 1, 0, -1):
                for l in range(k - 1, n + 1):
                    if i > j or k > l:
                        v = 0
                    elif A[i] == A[j] == B[k] == B[l]:
                        v = 1 if (i == j or k == l) else 2 + get(i + 1, j - 1, k + 1, l - 1)
                    else:
                        v = max(get(i + 1, j, k, l), get(i, j - 1, k, l), get(i, j, k + 1, l), get(i, j, k, l - 1))
                    P[(i, j, k, l)] = v
    return get(1, m, 1, n)

ok = True; cnt = 0
for m in range(0, 7):
    for n in range(0, 7):
        for _ in range(40):
            A = [random.choice("AB" if random.random() < .5 else "ABC") for _ in range(m)]
            B = [random.choice("ABC") for _ in range(n)]
            b = brute_lcps(A, B); d = lcps_dp(A, B); e = lcps_iter(A, B)
            cnt += 1
            if not (b == d == e):
                ok = False; print("   mismatch", "".join(A), "".join(B), b, d, e)
check(f"1(b) Pal recurrence (memoized and nested loops) = brute force on {cnt} random pairs (lengths <= 6)", ok)
check("1(b) example A=ABCBA..: LCPS(BANANA, ANANAS) = 5 (ANANA)", lcps_dp(list("BANANA"), list("ANANAS")) == 5 == brute_lcps(list("BANANA"), list("ANANAS")))
check("1(b) example LCPS(ABCBA, ACBCA) = 3", lcps_dp(list("ABCBA"), list("ACBCA")) == brute_lcps(list("ABCBA"), list("ACBCA")) == 3,
      lcps_dp(list("ABCBA"), list("ACBCA")))
check("1(b) the endpoint rule is needed: LCPS(AA, AA) = 2 but A,A not both usable twice", lcps_dp(list("AA"), list("AA")) == 2)
# the "take the four-way match" case is forced: a smaller max would be wrong on this input
check("1(b) LCPS(ABA, ABA) = 3, LCPS(AB, BA) = 1", lcps_dp(list("ABA"), list("ABA")) == 3 and lcps_dp(list("AB"), list("BA")) == 1)

# ---------------------------------------------------------------- 2 orthogonally separable rectangles
def separable(rects):
    """rects: list of (a, b, c, d). The definition, literally (with lines between distinct coordinates)."""
    if len(rects) <= 1:
        return True
    xs = sorted(set([r[0] for r in rects] + [r[2] for r in rects]))
    ys = sorted(set([r[1] for r in rects] + [r[3] for r in rects]))
    for t in range(len(xs) - 1):
        line = (xs[t] + xs[t + 1]) / 2
        S1 = [r for r in rects if r[2] < line]; S2 = [r for r in rects if r[0] > line]
        if len(S1) + len(S2) == len(rects) and S1 and S2 and separable(S1) and separable(S2):
            return True
    for t in range(len(ys) - 1):
        line = (ys[t] + ys[t + 1]) / 2
        S1 = [r for r in rects if r[3] < line]; S2 = [r for r in rects if r[1] > line]
        if len(S1) + len(S2) == len(rects) and S1 and S2 and separable(S1) and separable(S2):
            return True
    return False

def brute_sep(rects):
    best = 0
    for r in range(len(rects), 0, -1):
        for sub in itertools.combinations(rects, r):
            if separable(list(sub)):
                return r
    return 0

def sep_dp(rects):
    """Sep(a, b, c, d) = max orthogonally separable subset among rectangles inside the box
    [X[a], X[b]] x [Y[c], Y[d]], X and Y the sorted coordinate arrays."""
    n = len(rects)
    X = [None] + sorted([r[0] for r in rects] + [r[2] for r in rects])
    Y = [None] + sorted([r[1] for r in rects] + [r[3] for r in rects])
    N = 2 * n
    inside = {}
    def count_inside(a, b, c, d):
        return sum(1 for r in rects if X[a] <= r[0] and r[2] <= X[b] and Y[c] <= r[1] and r[3] <= Y[d])
    Sep = {}
    for w in range(1, N):
        for h in range(1, N):
            for a in range(1, N - w + 1):
                b = a + w
                for c in range(1, N - h + 1):
                    d = c + h
                    v = 1 if count_inside(a, b, c, d) >= 1 else 0
                    for e in range(a + 1, b):
                        v = max(v, Sep[(a, e, c, d)] + Sep[(e, b, c, d)])
                    for f in range(c + 1, d):
                        v = max(v, Sep[(a, b, c, f)] + Sep[(a, b, f, d)])
                    Sep[(a, b, c, d)] = v
    return Sep[(1, N, 1, N)] if n else 0

def random_rects(n):
    xs = random.sample(range(1, 40), 2 * n); ys = random.sample(range(1, 40), 2 * n)
    rects = []
    for i in range(n):
        x1, x2 = sorted(xs[2 * i:2 * i + 2]); y1, y2 = sorted(ys[2 * i:2 * i + 2])
        rects.append((x1, y1, x2, y2))
    return rects

ok = True; cnt = 0
for n in range(1, 6):
    for _ in range(25 if n < 5 else 8):
        rects = random_rects(n)
        b = brute_sep(rects); d = sep_dp(rects); cnt += 1
        if b != d:
            ok = False; print("   mismatch", rects, b, d)
check(f"2 Sep recurrence = brute force over all subsets on {cnt} random inputs (n <= 5, distinct coordinates)", ok)
ex = [(1, 1, 3, 3), (4, 2, 6, 5), (2, 4, 5, 7), (7, 1, 9, 8)]   # the third overlaps the first two's x- and y-ranges
check("2 example: four rectangles, best separable subset has size 3", sep_dp(ex) == brute_sep(ex) == 3, (sep_dp(ex), brute_sep(ex)))
pin = [(1, 3, 10, 4), (3, 1, 4, 10), (5, 5, 6, 6)]
check("2 a cross (two overlapping rectangles) is not separable: answer 2 for the cross plus one more", sep_dp(pin) == brute_sep(pin) == 2)

# ---------------------------------------------------------------- 3 broadcasting in a binary tree
def random_binary_tree(n):
    """children[v] = list of up to two children; node 0 is the root"""
    children = {0: []}
    for v in range(1, n):
        cand = [u for u in children if len(children[u]) < 2]
        p = random.choice(cand)
        children[p].append(v); children[v] = []
    return children

def brute_rounds(children):
    """BFS over sets of informed nodes; each round every informed node sends to at most one uninformed child"""
    n = len(children)
    start = frozenset([0]); seen = {start}; frontier = [start]; rounds = 0
    while True:
        if any(len(s) == n for s in frontier):
            return rounds
        nxt = set()
        for s in frontier:
            senders = [v for v in s if any(w not in s for w in children[v])]
            options = []
            for v in senders:
                options.append([None] + [w for w in children[v] if w not in s])
            for choice in itertools.product(*options):
                t = frozenset(s | {w for w in choice if w is not None})
                if t not in seen:
                    seen.add(t); nxt.add(t)
        frontier = list(nxt); rounds += 1

def rounds_dp(children):
    """Rounds(v) = min rounds to inform every node of v's subtree, given v already knows the message."""
    @lru_cache(maxsize=None)
    def Rounds(v):
        ch = children[v]
        if not ch:
            return 0
        if len(ch) == 1:
            return 1 + Rounds(ch[0])
        x, y = Rounds(ch[0]), Rounds(ch[1])
        return min(max(1 + x, 2 + y), max(1 + y, 2 + x))     # send to ch[0] first, or to ch[1] first
    return Rounds(0)

ok = True; cnt = 0
for n in range(1, 11):
    for _ in range(30):
        ch = random_binary_tree(n); cnt += 1
        if brute_rounds(ch) != rounds_dp(ch):
            ok = False; print("   mismatch", ch, brute_rounds(ch), rounds_dp(ch))
check(f"3 Rounds recurrence = brute force over all broadcast schedules on {cnt} random binary trees (n <= 10)", ok)
# the handout figure: root with two children; left child has two children, the left one of which has two leaf children;
# the right child has two children, the right of which has one child with one child (a path of length 2).
fig = {0: [1, 2], 1: [3, 4], 2: [5, 6], 3: [7, 8], 4: [], 5: [], 6: [9], 7: [], 8: [], 9: [10], 10: []}
check("3 a tree shaped like the handout figure takes 5 rounds", rounds_dp(fig) == brute_rounds(fig) == 5, rounds_dp(fig))
check("3 'larger child first' = min over both orders: max(1+big, 2+small)",
      all(min(max(1 + x, 2 + y), max(1 + y, 2 + x)) == max(1 + max(x, y), 2 + min(x, y)) for x in range(8) for y in range(8)))
path = {i: [i + 1] for i in range(6)}; path[6] = []
check("3 a path of 7 nodes takes 6 rounds; a complete binary tree of depth 2 (7 nodes) takes 4", rounds_dp(path) == 6 and rounds_dp({0: [1, 2], 1: [3, 4], 2: [5, 6], 3: [], 4: [], 5: [], 6: []}) == 4)

print("ALL OK" if not fails else f"{fails} FAILED")
sys.exit(1 if fails else 0)
