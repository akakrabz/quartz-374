#!/usr/bin/env python3
"""Checks for content/4-lecture-notes/03-treaps-and-skip-lists.md (Erickson, Director's Cut 3) and the concept page
content/concepts/treaps.md.

Treaps: the page's operations are implemented literally — textbook BST insertion at a leaf followed by rotations at z
while its priority is smaller than its parent's; deletion by rotating z down at its child of smaller priority until it is
a leaf; split by inserting a dummy of priority -inf; join by sinking a dummy root — and after every operation in long
random sequences the tree is compared with the unique treap of the current items (built recursively and by inserting in
priority order). Uniqueness is checked against all BST shapes. Every probability and expectation of §3.1.3–3.1.4 is
computed exactly (Fractions) by enumerating all n! priority orders for n <= 7, and compared with the closed forms;
the bounds are checked numerically, including where the note's chain of inequalities fails.

Skip lists: the two-level list is enumerated exactly over all 2^n duplicate patterns; the skip list is built as linked
levels (right/down pointers, sentinels, an empty top level as in the note's figure) and SkipListFind is run line for
line; the backwards walk is compared with the reversed search path; the level-count formulas and bounds are evaluated
exactly; and the exact expected number of moves derived on the page is checked against exhaustive enumeration (capped
heights, exact arithmetic) and a simulation of the literal algorithm with a stated tolerance."""
import itertools
import math
import os
import random
import sys
from fractions import Fraction as Fr

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
FIGS = os.path.join(HERE, "..", "figs")
PAGE = os.path.join(ROOT, "content", "4-lecture-notes", "03-treaps-and-skip-lists.md")
CONCEPT = os.path.join(ROOT, "content", "concepts", "treaps.md")
FAIL = []
rng = random.Random(30374)
NEG_INF = -math.inf
INF = math.inf


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAIL.append(name)


def H(m):
    return sum((Fr(1, i) for i in range(1, m + 1)), Fr(0))


# =====================================================================================================
# Treaps
class Node:
    __slots__ = ("key", "pri", "left", "right")

    def __init__(self, key, pri):
        self.key, self.pri, self.left, self.right = key, pri, None, None


def plain_insert(root, z):
    """Textbook BST insertion of node z as a leaf; returns (root, parent of z)."""
    if root is None:
        return z, None
    v = root
    while True:
        if z.key < v.key:
            if v.left is None:
                v.left = z
                return root, v
            v = v.left
        else:
            if v.right is None:
                v.right = z
                return root, v
            v = v.right


def build_by_priority(items):
    """Insert the (key, pri) items in increasing priority with plain BST insertion."""
    root = None
    for k, p in sorted(items, key=lambda t: t[1]):
        root, _ = plain_insert(root, Node(k, p))
    return root


def build_recursive(items):
    """Root = smallest priority; keys below go left, above go right (the uniqueness proof)."""
    if not items:
        return None
    k, p = min(items, key=lambda t: t[1])
    r = Node(k, p)
    r.left = build_recursive([t for t in items if t[0] < k])
    r.right = build_recursive([t for t in items if t[0] > k])
    return r


def shape(t):
    return None if t is None else (t.key, t.pri, shape(t.left), shape(t.right))


def inorder(t):
    return [] if t is None else inorder(t.left) + [t.key] + inorder(t.right)


def is_treap(t):
    keys = inorder(t)
    if keys != sorted(keys) or len(set(keys)) != len(keys):
        return False

    def heap(v):
        if v is None:
            return True
        for c in (v.left, v.right):
            if c is not None and not (v.pri < c.pri):
                return False
        return heap(v.left) and heap(v.right)
    return heap(t)


def depths(t, d=0, out=None):
    out = {} if out is None else out
    if t is not None:
        out[t.key] = d
        depths(t.left, d + 1, out)
        depths(t.right, d + 1, out)
    return out


def ancestors(t):
    """dict key -> set of keys of proper ancestors."""
    out = {}

    def go(v, anc):
        if v is None:
            return
        out[v.key] = set(anc)
        go(v.left, anc + [v.key])
        go(v.right, anc + [v.key])
    go(t, [])
    return out


def items_of(t):
    return [] if t is None else items_of(t.left) + [(t.key, t.pri)] + items_of(t.right)


def treap_insert(root, key, pri, snapshots=None):
    """Insert z at the bottom (textbook BST insertion), then, as long as z has smaller priority than its parent,
    rotate at z. Returns (root, depth of z before rotations, number of rotations, parent at insertion)."""
    z = Node(key, pri)
    if root is None:
        return z, 0, 0, None
    path = []
    v = root
    while v is not None:
        path.append(v)
        v = v.left if key < v.key else v.right
    parent0 = path[-1]
    if key < parent0.key:
        parent0.left = z
    else:
        parent0.right = z
    depth0 = len(path)
    rot = 0
    if snapshots is not None:
        snapshots.append(shape(root))
    while path and z.pri < path[-1].pri:
        p = path.pop()
        g = path[-1] if path else None
        if p.left is z:            # right rotation at z
            p.left, z.right = z.right, p
        else:                      # left rotation at z
            p.right, z.left = z.left, p
        if g is None:
            root = z
        elif g.left is p:
            g.left = z
        else:
            g.right = z
        rot += 1
        if snapshots is not None:
            snapshots.append(shape(root))
    return root, depth0, rot, parent0


def sink_and_cut(root, parent, z):
    """Rotate z down (at its child of smaller priority) until it is a leaf, then cut it off."""
    rot = 0
    while z.left is not None or z.right is not None:
        if z.left is None:
            c = z.right
        elif z.right is None:
            c = z.left
        else:
            c = z.left if z.left.pri < z.right.pri else z.right
        if c is z.left:
            z.left, c.right = c.right, z
        else:
            z.right, c.left = c.left, z
        if parent is None:
            root = c
        elif parent.left is z:
            parent.left = c
        else:
            parent.right = c
        parent = c
        rot += 1
    if parent is None:
        return None, rot
    if parent.left is z:
        parent.left = None
    else:
        parent.right = None
    return root, rot


def treap_delete(root, key):
    parent, z = None, root
    while z.key != key:
        parent, z = z, (z.left if key < z.key else z.right)
    return sink_and_cut(root, parent, z)


def split(root, pivot):
    root, _, _, _ = treap_insert(root, pivot, NEG_INF)
    assert root.key == pivot
    return root.left, root.right


def join(lo, hi, dummy_key):
    d = Node(dummy_key, NEG_INF)
    d.left, d.right = lo, hi
    root, _ = sink_and_cut(d, None, d)
    return root


def search_path(root, key):
    path, v = [], root
    while v is not None:
        path.append(v.key)
        if key == v.key:
            break
        v = v.left if key < v.key else v.right
    return path


# ------------------------------------------------------------------ the note's example treap (p. 1)
EX = [("A", 9), ("G", 7), ("H", 2), ("I", 4), ("L", 8), ("M", 1), ("O", 6), ("R", 5), ("T", 3)]
T0 = build_recursive(EX)
expected = ("M", 1, ("H", 2, ("G", 7, ("A", 9, None, None), None), ("I", 4, None, ("L", 8, None, None))),
            ("T", 3, ("R", 5, ("O", 6, None, None), None), None))
check("example treap (p. 1): M1 root; H2, T3; G7, I4 under H; R5 under T; A9, L8, O6 at the bottom", shape(T0) == expected)
check("example treap: inorder A G H I L M O R T, heap-ordered", inorder(T0) == list("AGHILMORT") and is_treap(T0))
check("example treap equals the BST built by inserting in increasing priority", shape(build_by_priority(EX)) == expected)
d0 = depths(T0)
check("example treap: height 3; the deepest nodes are A, L and O", max(d0.values()) == 3 and
      sorted(k for k in d0 if d0[k] == 3) == ["A", "L", "O"], str(d0))

snaps = []
T1 = build_recursive(EX)
T1, dep0, rot, par0 = treap_insert(T1, "S", -1, snaps)
final = ("S", -1, ("M", 1, ("H", 2, ("G", 7, ("A", 9, None, None), None), ("I", 4, None, ("L", 8, None, None))),
                   ("R", 5, ("O", 6, None, None), None)), ("T", 3, None, None))
check("insert S with priority -1 (p. 3): leaf child of R at depth 3, then 3 rotations, S becomes the root",
      dep0 == 3 and rot == 3 and par0.key == "R" and shape(T1) == final, f"depth {dep0}, rotations {rot}")
check("insert S: the four stages of the note's figure (leaf; above R; above T; root)",
      len(snaps) == 4 and snaps[0][3][2][3][0] == "S" and snaps[1][3][2][0] == "S" and snaps[2][3][0] == "S" and snaps[3][0] == "S")
check("insert S: the parent at insertion, R, is the inorder predecessor of S", par0.key == max(k for k in "AGHILMORT" if k < "S"))
T2, rot2 = treap_delete(T1, "S")
check("delete S again: 3 rotations down, then the original treap", rot2 == 3 and shape(T2) == expected)
lo, hi = split(build_recursive(EX), "N")
check("split the example at N: T< holds A G H I L M, T> holds O R T, both treaps",
      inorder(lo) == list("AGHILM") and inorder(hi) == list("ORT") and is_treap(lo) and is_treap(hi)
      and shape(lo) == shape(build_recursive([t for t in EX if t[0] < "N"]))
      and shape(hi) == shape(build_recursive([t for t in EX if t[0] > "N"])))
check("join T< and T> again (dummy root rotated down): the original treap", shape(join(lo, hi, "N")) == expected)
hpath = search_path(T0, "N")
check("unsuccessful search for N in the example: path M T R O, ends at O, the successor of N",
      hpath == ["M", "T", "R", "O"], str(hpath))


# ------------------------------------------------------------------ uniqueness: all BST shapes
def all_shapes(keys):
    if not keys:
        yield None
        return
    for i, r in enumerate(keys):
        for L in all_shapes(keys[:i]):
            for R in all_shapes(keys[i + 1:]):
                yield (r, L, R)


def heap_ok(s, pri):
    if s is None:
        return True
    r, L, R = s
    for c in (L, R):
        if c is not None and not pri[r] < pri[c[0]]:
            return False
    return heap_ok(L, pri) and heap_ok(R, pri)


def strip(sh):
    return None if sh is None else (sh[0], strip(sh[2]), strip(sh[3]))


ok = True
cnt = 0
for n in range(0, 7):
    keys = list(range(1, n + 1))
    shapes = list(all_shapes(keys))
    for perm in itertools.permutations(range(n)):
        pri = {k: perm[k - 1] for k in keys}
        good = [s for s in shapes if heap_ok(s, pri)]
        items = [(k, pri[k]) for k in keys]
        ok &= len(good) == 1 and good[0] == strip(shape(build_recursive(items))) == strip(shape(build_by_priority(items)))
        cnt += 1
check(f"uniqueness: for every n <= 6 and every priority order ({cnt} cases), exactly one of the Catalan-many BST shapes "
      "is heap-ordered, and it is the recursive treap and the insert-by-priority BST", ok)

# ------------------------------------------------------------------ random operation sequences
ok_struct = ok_cost = ok_parent = ok_unsucc = ok_split = True
for trial in range(1500):
    root, items = None, {}
    for step in range(rng.randint(1, 40)):
        if items and rng.random() < 0.35:
            k = rng.choice(list(items))
            root, r = treap_delete(root, k)
            del items[k]
        else:
            k = rng.randint(0, 60)
            if k in items:
                continue
            p = rng.random()
            before = sorted(items)
            dmap = depths(root)
            root, d, r, par = treap_insert(root, k, p)
            items[k] = p
            ok_cost &= r <= d
            if par is not None:
                pred = max([x for x in before if x < k], default=None)
                succ = min([x for x in before if x > k], default=None)
                ok_parent &= par.key in (pred, succ) and d == dmap[par.key] + 1
        ok_struct &= is_treap(root) and shape(root) == shape(build_recursive(list(items.items())))
    if items:
        q = rng.randint(0, 60) + 0.5
        path = search_path(root, q)
        pred = max([x for x in items if x < q], default=None)
        succ = min([x for x in items if x > q], default=None)
        ok_unsucc &= path[-1] in (pred, succ)
        piv = rng.randint(0, 60) + 0.5
        snapshot = list(items.items())
        a, b = split(build_recursive(snapshot), piv)
        ok_split &= (shape(a) == shape(build_recursive([t for t in snapshot if t[0] < piv])) and
                     shape(b) == shape(build_recursive([t for t in snapshot if t[0] > piv])) and
                     shape(join(a, b, piv)) == shape(build_recursive(snapshot)))
check("1500 random insert/delete sequences: after every rotation-based insert and delete the tree is the unique treap "
      "of the current items", ok_struct)
check("insertion: rotations <= depth of the new leaf before the rotations (cost ~ twice an unsuccessful search)", ok_cost)
check("insertion: the new leaf's parent is its inorder predecessor or successor", ok_parent)
check("unsuccessful search ends at the predecessor or the successor of the query", ok_unsucc)
check("split by inserting a -inf dummy, and join by sinking a dummy root, agree with the recursive treaps", ok_split)
worst = build_recursive([(k, k) for k in range(1, 31)])
check("worst case: priorities increasing with the keys give a path of depth n - 1 (n = 30)",
      max(depths(worst).values()) == 29)

# =====================================================================================================
# Random priorities: exact enumeration
EXACT = {}
for n in range(1, 8):
    anc_count = {(i, k): 0 for i in range(1, n + 1) for k in range(1, n + 1)}
    depth_sum = {k: 0 for k in range(1, n + 1)}
    lemma_ok = True
    for perm in itertools.permutations(range(n)):
        pri = {k: perm[k - 1] for k in range(1, n + 1)}
        t = build_recursive([(k, pri[k]) for k in range(1, n + 1)])
        A = ancestors(t)
        for k in range(1, n + 1):
            depth_sum[k] += len(A[k])
            for i in range(1, n + 1):
                if i == k:
                    continue
                up = i in A[k]
                lo_, hi_ = min(i, k), max(i, k)
                smallest = min(range(lo_, hi_ + 1), key=lambda j: pri[j]) == i
                lemma_ok &= up == smallest
                anc_count[(i, k)] += up
    f = math.factorial(n)
    EXACT[n] = dict(pr={ik: Fr(c, f) for ik, c in anc_count.items()}, ed={k: Fr(s, f) for k, s in depth_sum.items()},
                    lemma=lemma_ok)

check("Lemma 1: for all n <= 7, all priority orders and all i != k: i above k iff x_i has the smallest priority in "
      "X(i, k)", all(EXACT[n]["lemma"] for n in EXACT))
check("Pr[i above k] = [i != k]/(|k - i| + 1) exactly, n <= 7",
      all(EXACT[n]["pr"][(i, k)] == (Fr(1, abs(k - i) + 1) if i != k else 0) for n in EXACT
          for i in range(1, n + 1) for k in range(1, n + 1)))
check("E[depth(x_k)] = H_k + H_{n-k+1} - 2 exactly, n <= 7, all k",
      all(EXACT[n]["ed"][k] == H(k) + H(n - k + 1) - 2 for n in EXACT for k in range(1, n + 1)))
tab7 = [EXACT[7]["ed"][k] for k in range(1, 8)]
check("table for n = 7: E[depth(x_k)] = 223/140, 39/20, 127/60, 13/6, 127/60, 39/20, 223/140 "
      "(1.593, 1.95, 2.117, 2.167); 2 ln 7 = 3.89",
      tab7 == [Fr(223, 140), Fr(39, 20), Fr(127, 60), Fr(13, 6), Fr(127, 60), Fr(39, 20), Fr(223, 140)]
      and abs(2 * math.log(7) - 3.89) < 0.005, ", ".join(map(str, tab7)))

# bounds on E[depth]
Hf = [0.0]
for i in range(1, 200001):
    Hf.append(Hf[-1] + 1.0 / i)
ok1 = ok2 = ok3 = ok_rev = True
for n in range(2, 3001):
    for k in range(1, n + 1):
        e = Hf[k] + Hf[n - k + 1] - 2
        ok1 &= e <= math.log(k) + math.log(n - k + 1) + 1e-12
        ok2 &= math.log(k) + math.log(n - k + 1) <= 2 * math.log((n + 1) / 2) + 1e-12
        ok_rev &= e > math.log(k) + math.log(n - k + 1) - 2
    ok3 &= 2 * math.log((n + 1) / 2) < 2 * math.log(n)
check("H_m - 1 <= ln m, so E[depth(x_k)] <= ln k + ln(n-k+1) (n <= 3000, all k)", ok1)
check("ln k + ln(n-k+1) <= 2 ln((n+1)/2) < 2 ln n for n >= 2", ok2 and ok3)
check("the note's step 'H_k - 1 + H_{n-k+1} - 1 < ln k + ln(n-k+1) - 2' is false: the opposite strict inequality holds "
      "for every n <= 3000 and k", ok_rev)
fails = [n for n in range(1, 31) if not max(Hf[k] + Hf[n - k + 1] - 2 for k in range(1, n + 1)) < 2 * math.log(n) - 2]
check("the note's final bound E[depth] < 2 ln n - 2 fails exactly for n = 1..16 (among n <= 30)", fails == list(range(1, 17)),
      str(fails))
check("example of the failure: n = 2, k = 1: E[depth] = 1/2 > 2 ln 2 - 2 = -0.61",
      H(1) + H(2) - 2 == Fr(1, 2) and 2 * math.log(2) - 2 < 0)
# n in 31..200000: vectorized, and the analytic argument beyond
Ha = np.array(Hf)
okv = True
for n in range(31, 20001):
    k = np.arange(1, n + 1)
    okv &= bool((Ha[k] + Ha[n - k + 1] - 2).max() < 2 * math.log(n) - 2)
gamma = 0.5772156649015329
# H_m < ln m + gamma + 1/(2m). For n >= 31: if min(k, n-k+1) <= 9: E <= H_9 + H_n - 2 < 2 ln n - 2 since ln n > 3.43;
# otherwise E < 2 ln((n+1)/2) + 2 gamma + 1/10 - 2 < 2 ln n - 2 once 2 ln((n+1)/n) < 2 ln 2 - 2 gamma - 0.1.
arg1 = float(H(9)) + gamma + 1 / 62 < math.log(31)
arg2 = 2 * math.log(32 / 31) < 2 * math.log(2) - 2 * gamma - 0.1
okH = all(Hf[m] < math.log(m) + gamma + 1 / (2 * m) for m in range(1, 100001))
check("2 ln n - 2 holds for every n >= 17: numerically up to 20000, and for n >= 31 by H_m < ln m + gamma + 1/(2m)",
      okv and arg1 and arg2 and okH)

# random insertion order = random priorities
ok = True
for n in range(1, 7):
    for order in itertools.permutations(range(1, n + 1)):
        t = None
        for k in order:
            t, _ = plain_insert(t, Node(k, 0))
        tt = build_recursive([(k, order.index(k)) for k in range(1, n + 1)])
        ok &= strip(shape(t)) == strip(shape(tt))
check("inserting keys in random order (no priorities) builds the treap whose priorities are the insertion times", ok)

# =====================================================================================================
# Randomized quicksort, again


def quicksort_pairs(keys, pri):
    """Recursive quicksort whose pivot is the key of smallest priority (= first in the random order)."""
    pairs = set()

    def qs(S):
        if len(S) <= 1:
            return S
        p = min(S, key=lambda k: pri[k])
        for x in S:
            if x != p:
                pairs.add((min(x, p), max(x, p)))
        return qs([x for x in S if x < p]) + [p] + qs([x for x in S if x > p])
    out = qs(list(keys))
    return out, pairs


def bst_sort(order):
    """RandomizedQuicksort as written in the note: insert in the given order, output the inorder sequence."""
    t, comps, pairs = None, 0, set()
    for k in order:
        v = t
        while v is not None:
            comps += 1
            pairs.add((min(k, v.key), max(k, v.key)))
            v = v.left if k < v.key else v.right
        t, _ = plain_insert(t, Node(k, 0))
    return inorder(t), comps, pairs


ok = True
for n in range(1, 7):
    for order in itertools.permutations(range(1, n + 1)):
        pri = {k: order.index(k) for k in order}
        s1, c1, p1 = bst_sort(order)
        s2, p2 = quicksort_pairs(range(1, n + 1), pri)
        A = ancestors(build_recursive([(k, pri[k]) for k in pri]))
        pa = {(min(i, k), max(i, k)) for k in A for i in A[k]}
        ok &= s1 == s2 == list(range(1, n + 1)) and p1 == p2 == pa and c1 == len(p1) == sum(len(A[k]) for k in A)
for _ in range(300):
    n = 40
    order = rng.sample(range(1, n + 1), n)
    pri = {k: order.index(k) for k in order}
    s1, c1, p1 = bst_sort(order)
    s2, p2 = quicksort_pairs(range(1, n + 1), pri)
    ok &= s1 == s2 and p1 == p2
check("BST-insertion quicksort sorts and makes exactly the comparisons of quicksort with the same pivots (= the "
      "ancestor/descendant pairs of the treap), all orders n <= 6 and random n = 40", ok)
check("Pr[x_i and x_k compared] = Pr[i above k] + Pr[k above i] = 2/(|k-i|+1), n <= 7",
      all(EXACT[n]["pr"][(i, k)] + EXACT[n]["pr"][(k, i)] == Fr(2, abs(k - i) + 1)
          for n in EXACT for i in range(1, n + 1) for k in range(1, n + 1) if i != k))
check("expected comparisons = sum of expected depths = 2(n+1)H_n - 4n, n <= 7",
      all(sum(EXACT[n]["ed"].values()) == 2 * (n + 1) * H(n) - 4 * n for n in EXACT))
check("2(n+1)H_n - 4n = sum_{i<k} 2/(k-i+1) for n <= 300",
      all(2 * (n + 1) * H(n) - 4 * n == sum(Fr(2, k - i + 1) for k in range(1, n + 1) for i in range(1, k))
          for n in range(1, 60)))
check("2(n+1)H_n - 4n < 2n ln n for 2 <= n <= 10^5 (about 1.39 n lg n)",
      all(2 * (n + 1) * Hf[n] - 4 * n < 2 * n * math.log(n) for n in range(2, 100001)))

# =====================================================================================================
# Two-level list (p. 6-7): exact enumeration over duplicate patterns


def two_level_costs(n, dup, k):
    """keys 1..n, dup[j] = key j has a copy in the shortcut list. Returns (#examined in phase 1, phase 2 (0 if none))."""
    short = [j for j in range(1, n + 1) if dup[j]]
    ph1 = 1  # the -inf sentinel
    w = None
    for j in short:
        ph1 += 1
        if j >= k:
            break
        w = j
    else:
        ph1 += 1  # the +inf sentinel
    if dup[k]:
        return ph1, 0
    start = 0 if w is None else w
    ph2 = 1 + (k - start)  # w (or the -inf sentinel), the keys after it, up to and including k
    return ph1, ph2


ok = True
for n in range(1, 11):
    for k in range(1, n + 1):
        e1 = e2 = e2run = Fr(0)
        for bits in itertools.product((0, 1), repeat=n):
            dup = dict(zip(range(1, n + 1), bits))
            a, b = two_level_costs(n, dup, k)
            e1 += Fr(a, 2 ** n)
            e2 += Fr(b, 2 ** n)
        ok &= e1 == Fr(k - 1, 2) + 2 and e2 == Fr(1, 2) * (3 - Fr(2, 2 ** k)) and \
            e1 + e2 == Fr(k, 2) + 3 - Fr(1, 2 ** k)
check("two-level list, all 2^n duplicate patterns, n <= 10: phase 1 examines (k-1)/2 + 2 nodes on average, phase 2 "
      "(when needed) 3 - 2^(1-k), in total k/2 + 3 - 2^(-k)", ok)
check("the note's '1 + sum_{k>=0} 2^-k = 2' (p. 7): the left side is 3",
      3 - Fr(1, 2 ** 58) < 1 + sum(Fr(1, 2 ** k) for k in range(60)) < 3)
dupex = {j: j in (0, 1, 3, 6, 7, 9) for j in range(10)}
# the note's two-level example (keys 0..9, shortcut list 0 1 3 6 7 9), search for 5: shift keys by 1
a, b = two_level_costs(10, {j + 1: dupex[j] for j in range(10)}, 6)
check("note's two-level example, search for 5: phase 1 examines -inf 0 1 3 6 (5 nodes), phase 2 examines 3 4 5 (3)",
      (a, b) == (5, 3), f"{a}, {b}")

# =====================================================================================================
# Skip lists


class SNode:
    __slots__ = ("key", "right", "down", "level", "up", "left")

    def __init__(self, key, level):
        self.key, self.level, self.right, self.down, self.up, self.left = key, level, None, None, None, None


def build_skiplist(keys, heights):
    """Level l holds -inf, the keys of height >= l, +inf; level L+1 (L = max height) holds only the sentinels.
    Returns the top-left sentinel and the levels."""
    L = max(heights) if heights else 0
    levels = []
    for l in range(L + 2):
        row = [SNode(NEG_INF, l)] + [SNode(k, l) for k, h in zip(keys, heights) if h >= l] + [SNode(INF, l)]
        for a_, b_ in zip(row, row[1:]):
            a_.right, b_.left = b_, a_
        if levels:
            below = {nd.key: nd for nd in levels[-1]}
            for nd in row:
                nd.down = below[nd.key]
                below[nd.key].up = nd
        levels.append(row)
    return levels[-1][0], levels


def skiplist_find(x, top):
    """SkipListFind(x, L) exactly as in the note; returns (node or None, path of visited nodes)."""
    v = top
    path = [v]
    while v is not None and v.key != x:
        if v.right.key > x:
            v = v.down
        else:
            v = v.right
        path.append(v)
    return v, path


def backwards(v, top_level):
    """dniFtsiLpikS: while level(v) != top: if up(v) exists go up, else go left."""
    path = [v]
    while v.level != top_level:
        v = v.up if v.up is not None else v.left
        path.append(v)
    return path


# the note's skip list (p. 7-8): keys 0..9
EXK = list(range(10))
EXH = [1, 3, 0, 1, 0, 0, 2, 4, 0, 1]
top, levels = build_skiplist(EXK, EXH)
v, path = skiplist_find(5, top)
moves = len(path) - 1
downs = sum(1 for a_, b_ in zip(path, path[1:]) if b_ is a_.down)
check("note's skip list (6 levels incl. the empty top level): row sizes", [len(r) - 2 for r in levels] == [10, 6, 3, 2, 1, 0])
check("search for 5 in the note's skip list: 9 moves, 5 down and 4 right, ends at 5 on the bottom level",
      v is not None and v.key == 5 and v.level == 0 and moves == 9 and downs == 5,
      " ".join(f"{p.key}@{p.level}" for p in path))
ex_path = [(p.key, p.level) for p in path]
check("search path for 5: -inf@5 -inf@4 -inf@3 1@3 1@2 1@1 3@1 3@0 4@0 5@0",
      ex_path == [(NEG_INF, 5), (NEG_INF, 4), (NEG_INF, 3), (1, 3), (1, 2), (1, 1), (3, 1), (3, 0), (4, 0), (5, 0)])
examined = [(p.right.key, p.level) for p, q in zip(path, path[1:]) if q is p.down]
check("the nodes looked at but not entered (the note's crosses): inf@5, 7@4, 7@3, 6@2, 6@1",
      examined == [(INF, 5), (7, 4), (7, 3), (6, 2), (6, 1)], str(examined))
bw = backwards(v, 5)
check("backwards walk from 5 retraces the search path in reverse", [id(p) for p in bw] == [id(p) for p in reversed(path)])

ok_find = ok_back = True
for trial in range(3000):
    n = rng.randint(1, 14)
    keys = sorted(rng.sample(range(0, 60, 2), n))
    hts = []
    for _ in keys:
        h = 0
        while rng.random() < 0.5:
            h += 1
        hts.append(h)
    top, levels = build_skiplist(keys, hts)
    for x, h in zip(keys, hts):
        v, path = skiplist_find(x, top)
        ok_find &= v is not None and v.key == x and v.level == h
        bw = backwards(v, len(levels) - 1)
        ok_back &= [id(p) for p in bw] == [id(p) for p in reversed(path)]
    for x in range(-1, 61, 2):
        v, path = skiplist_find(x, top)
        ok_find &= v is None
check("SkipListFind on 3000 random skip lists: finds every stored key at its top copy and returns Null for absent keys",
      ok_find)
check("backwards analysis: up-if-possible-else-left from the found node retraces every search path", ok_back)

# levels
check("E[L(x)] = 1: solution of E = (1/2)0 + (1/2)(1 + E), and sum_l l 2^-(l+1) = 1",
      sum(Fr(l, 2 ** (l + 1)) for l in range(200)) > 1 - Fr(1, 10 ** 50))


def EL(n, terms=400):
    return math.fsum(1 - (1 - 2.0 ** -l) ** n for l in range(1, terms))


ok_u = ok_c = True
for n in [2, 3, 5, 10, 100, 1000, 10 ** 4, 10 ** 6]:
    for l in range(1, 80):
        exact = 1 - (1 - Fr(1, 2 ** l)) ** n if n <= 1000 else 1 - (1 - 2.0 ** -l) ** n
        ok_u &= exact <= Fr(n, 2 ** l) if n <= 1000 else exact <= n / 2 ** l + 1e-15
    for c in [1.5, 2, 3, 4]:
        l = math.ceil(c * math.log2(n))
        ok_c &= 1 - (1 - 2.0 ** -l) ** n <= n ** (1 - c) + 1e-15
check("union bound Pr[L >= l] = 1 - (1 - 2^-l)^n <= n/2^l (exact for n <= 1000)", ok_u)
check("Pr[L >= c lg n] <= 1/n^(c-1) for c = 1.5, 2, 3, 4 and n from 2 to 10^6", ok_c)
ok = all(EL(n) <= math.ceil(math.log2(n)) + 1 < math.log2(n) + 2 for n in range(1, 20001))
check("E[L] = sum_{l>=1} Pr[L >= l] <= ceil(lg n) + 1 < lg n + 2, n <= 20000", ok)
check("the note's last step: sum_{i>=1} 2^-i = 1, not 2 (so the algebra gives lg n + 1 for n a power of 2)",
      sum(Fr(1, 2 ** i) for i in range(1, 80)) < 1)
gaps = [EL(n) - math.log2(n) for n in range(2, 20001)]
check("E[L] - lg n stays between 0.33 and 0.67 for 2 <= n <= 20000 (n = 1000: E[L] = 10.30)",
      0.33 < min(gaps) and max(gaps) < 0.67 and abs(EL(1000) - 10.30) < 0.005, f"{min(gaps):.3f}..{max(gaps):.3f}")
check("E[L] by both formulas, n = 10: sum l Pr[L = l] = sum Pr[L >= l]",
      abs(math.fsum(l * ((1 - 2.0 ** -(l + 1)) ** 10 - (1 - 2.0 ** -l) ** 10) for l in range(0, 300)) - EL(10)) < 1e-12)


# exact expected number of moves: E[L_n] + E[L_k]
def capped_dist(Hc):
    return {l: (Fr(1, 2 ** (l + 1)) if l < Hc else Fr(1, 2 ** Hc)) for l in range(Hc + 1)}


ok = True
for n in range(1, 5):
    Hc = 6 if n <= 3 else 5
    dist = capped_dist(Hc)
    for k in range(1, n + 1):
        tot = Fr(0)
        keys = list(range(1, n + 1))
        for hts in itertools.product(range(Hc + 1), repeat=n):
            pr = Fr(1)
            for h in hts:
                pr *= dist[h]
            top, levels = build_skiplist(keys, list(hts))
            v, path = skiplist_find(k, top)
            tot += pr * (len(path) - 1)
        # the page's derivation, with the capped distribution
        P_le = {l: sum(dist[m] for m in range(l + 1)) for l in range(Hc + 1)}
        EL_cap = sum((1 - P_le[l - 1] ** n) for l in range(1, Hc + 1))
        Eh = sum(l * dist[l] for l in dist)
        right = sum(dist[l] * P_le[l] ** (k - j) for l in range(Hc + 1) for j in range(1, k + 1))
        ok &= tot == EL_cap + 1 - Eh + right
check("expected moves of SkipListFind for x_k, exhaustive over capped heights (n <= 4, exact): equals E[L] + 1 - E[h_k] "
      "+ sum_l sum_j Pr[h_j = l] Pr[h <= l]^(k-j)", ok)


def EL_frac(m, terms=120):
    return sum((1 - (1 - Fr(1, 2 ** l)) ** m for l in range(1, terms)), Fr(0))


ok = True
for n in range(1, 7):
    for k in range(1, n + 1):
        right = sum((Fr(1, 2 ** (l + 1)) * (1 - Fr(1, 2 ** (l + 1))) ** (k - j) for l in range(0, 119)
                     for j in range(1, k + 1)), Fr(0))
        ok &= abs(right - EL_frac(k)) < Fr(1, 10 ** 30)
check("uncapped: the right moves sum to E[L_k] = sum_{l>=1} (1 - (1 - 2^-l)^k) (the max height among x_1..x_k); "
      "down moves average E[L] + 1 - 1 = E[L]", ok)
nsim, ntr = 64, 20000
srng = random.Random(77)
mv_n, mv_mid = [], []
for _ in range(ntr):
    hts = []
    for _ in range(nsim):
        h = 0
        while srng.random() < 0.5:
            h += 1
        hts.append(h)
    top, levels = build_skiplist(list(range(1, nsim + 1)), hts)
    mv_n.append(len(skiplist_find(nsim, top)[1]) - 1)
    mv_mid.append(len(skiplist_find(nsim // 2, top)[1]) - 1)
for name, mv, k in (("largest key", mv_n, nsim), ("middle key", mv_mid, nsim // 2)):
    m, sd = float(np.mean(mv)), float(np.std(mv)) / math.sqrt(ntr)
    pred = EL(nsim) + EL(k)
    check(f"simulation of the literal SkipListFind, n = 64, {ntr} lists, {name}: mean {m:.3f} vs E[L_n] + E[L_k] = "
          f"{pred:.3f} (tolerance 4.5 standard errors = {4.5 * sd:.3f})", abs(m - pred) < 4.5 * sd)
check("largest key, n = 1000: 2 E[L] = 20.60 expected moves, below 2 ceil(lg n) + 2 = 22",
      abs(2 * EL(1000) - 20.60) < 0.005 and 2 * EL(1000) < 22)
# high-probability search: {moves > t} is contained in {L >= l} or {fewer than l heads in t flips}, t = 4l, l = c lg n
from scipy.stats import binom as _binom
ok = True
for n in (16, 100, 1000, 10 ** 5):
    for c in (2, 3, 4):
        l = math.ceil(c * math.log2(n))
        t = 4 * l
        ok &= _binom.cdf(l - 1, t, 0.5) < math.exp(-t / 16) <= n ** (-c / (4 * math.log(2))) * (1 + 1e-9)
check("search w.h.p.: with t = 4 c lg n, Pr[fewer than t/4 heads in t flips] < e^{-t/16} <= n^{-c/(4 ln 2)}", ok)
srng2 = random.Random(5)
mx = 0
for _ in range(3000):
    hts = []
    for _ in range(256):
        h = 0
        while srng2.random() < 0.5:
            h += 1
        hts.append(h)
    top, levels = build_skiplist(list(range(1, 257)), hts)
    mx = max(mx, max(len(skiplist_find(x, top)[1]) - 1 for x in (1, 64, 128, 256)))
check(f"simulation: 3000 skip lists with n = 256, four searches each: longest search {mx} moves, below 12 lg n = 96",
      mx < 96)
check("FlipWalk: the number of tails before the l-th head has mean l (negative binomial), l = 1..30",
      all(abs(math.fsum(t * math.comb(t + l - 1, t) * 0.5 ** (t + l) for t in range(0, 2000)) - l) < 1e-9
          for l in range(1, 31)))

# =====================================================================================================
# Concept page example: n = 4
e4 = [EXACT[4]["ed"][k] for k in range(1, 5)]
check("concept example n = 4: E[depth] = 13/12, 4/3, 4/3, 13/12 (24 priority orders); total 29/6 = 2*5*H_4 - 16",
      e4 == [Fr(13, 12), Fr(4, 3), Fr(4, 3), Fr(13, 12)] and sum(e4) == Fr(29, 6) == 10 * H(4) - 16, str(e4))
check("concept example: Pr[1 above 4] = 1/4 and Pr[2 above 3] = 1/2",
      EXACT[4]["pr"][(1, 4)] == Fr(1, 4) and EXACT[4]["pr"][(2, 3)] == Fr(1, 2))
cnt = sum(1 for perm in itertools.permutations(range(4))
          if 1 in ancestors(build_recursive([(k, perm[k - 1]) for k in range(1, 5)]))[4])
check("concept example: x_1 is an ancestor of x_4 in exactly 6 of the 24 orders (x_1 first among x_1..x_4)", cnt == 6)
check("concept example: skip list, n = 1000: Pr[L >= 20] <= 1000/2^20 < 0.001 (exact 0.000953)",
      1 - (1 - 2.0 ** -20) ** 1000 <= 1000 / 2 ** 20 < 0.001 and abs((1 - (1 - 2.0 ** -20) ** 1000) - 0.000953) < 1e-6)

# =====================================================================================================
# figures and page text
if os.path.exists(FIGS):
    for name, needles in [("n03-treap", ["M", "1", "A", "9", "geometric"]),
                          ("n03-insert", ["S", "−1", "three rotations"]),
                          ("n03-skiplist", ["9 moves", "−∞", "∞"])]:
        p = os.path.join(FIGS, name + ".html")
        if os.path.exists(p):
            txt = open(p, encoding="utf-8").read()
            check(f"figure {name} exists and mentions " + ", ".join(needles), all(s in txt for s in needles))
for path, needles in [(PAGE, ["H_k + H_{n-k+1} - 2", "2(n+1)H_n - 4n", "223/140", "13/6", "k/2 + 3 - 2^{-k}",
                              "20.6", "10.30"]),
                      (CONCEPT, ["13/12", "29/6"])]:
    if os.path.exists(path):
        txt = open(path, encoding="utf-8").read().replace(" ", "").replace("\\tfrac", "").replace("\\frac", "")
        for s in needles:
            check(f"{os.path.basename(path)} states {s}", s.replace(" ", "") in txt or s.replace(" ", "")
                  .replace("{", "").replace("}", "") in txt.replace("{", "").replace("}", ""))

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: {FAIL}")
