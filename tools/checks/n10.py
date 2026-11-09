#!/usr/bin/env python3
"""Checks for content/4-lecture-notes/10-scapegoat-and-splay-trees.md (Erickson, Director's Cut 10, Scapegoat and Splay
Trees) and the concept page content/concepts/splay-trees.md.

Implemented as the page states them: perfectly balanced rebuilding; lazy deletion with global rebuilding; partial
rebuilding after insertions (rule height(v) > alpha lg size(v), lowest violator rebuilt) under two size/height
conventions and five values of alpha; scapegoat trees combining both; single rotations, zig-zags and roller-coasters;
splay trees with Search, Insert and Delete exactly as in §10.6. Every bound is tested on long random and adversarial
operation sequences against the actual cost: the search-path bounds, Lemma 1 and every inequality of its proof at
every rebuild, the charging argument (insertions since the last rebuild vs. rebuild cost), at most one rebuild per
insertion, the amortized totals; the (generalized) Access Lemma and every line of its proof at every rotation step,
with unit and random positive weights; the totals for whole operation sequences; static optimality and the static
finger bound; the scanning bound empirically. The note's Figure 4 is reconstructed and replayed. The errors found
(floor ranks in §10.6, the bound 3 lg n - 1, "drop in potential", two proof lines on p. 7, the search bound lg n + 1 of
§10.2) are exhibited by explicit counterexamples. Finally the numbers printed on the pages and in the figures are
compared with the computed ones."""
import itertools
import math
import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
PAGE = os.path.join(ROOT, "content", "4-lecture-notes", "10-scapegoat-and-splay-trees.md")
CONCEPT = os.path.join(ROOT, "content", "concepts", "splay-trees.md")
FIGS = os.path.join(HERE, "..", "figs")
FAIL = []
random.seed(10374)
lg = math.log2
EPS = 1e-9
sys.setrecursionlimit(20000)


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAIL.append(name)


def read(path):
    return open(path, encoding="utf-8").read() if os.path.exists(path) else ""


# =====================================================================================================
# Plain BSTs as nested tuples (key, left, right) for the rebuilding structures

def t_keys(t):
    out, st = [], []
    while st or t is not None:
        while t is not None:
            st.append(t)
            t = t[1]
        t = st.pop()
        out.append(t[0])
        t = t[2]
    return out


def t_size(t):
    return 0 if t is None else 1 + t_size(t[1]) + t_size(t[2])


def t_height(t):
    return -1 if t is None else 1 + max(t_height(t[1]), t_height(t[2]))


def perfectly_balanced(ks):
    """Middle key at the root: the left subtree gets floor(n/2) keys, the right one ceil(n/2) - 1."""
    if not ks:
        return None
    m = len(ks) // 2
    return (ks[m], perfectly_balanced(ks[:m]), perfectly_balanced(ks[m + 1:]))


def is_perfect(t):
    """Exercise 1's definition: n <= 1, or both subtrees perfectly balanced with at most floor(n/2) nodes."""
    n = t_size(t)
    if n <= 1:
        return True
    return t_size(t[1]) <= n // 2 and t_size(t[2]) <= n // 2 and is_perfect(t[1]) and is_perfect(t[2])


def nodes_of(t):
    return [] if t is None else nodes_of(t[1]) + [t] + nodes_of(t[2])


print("== 10.1  Definitions: perfectly balanced trees")
ok = True
for n in range(1, 2000):
    t = perfectly_balanced(list(range(n)))
    ok &= is_perfect(t) and t_height(t) == math.floor(lg(n)) and t_height(t) + 1 == math.ceil(lg(n + 1))
    if n <= 300:
        ok &= all(abs(t_size(u[1]) - t_size(u[2])) <= 1 for u in nodes_of(t))
check("perfectly balanced tree on n keys: Imbal <= 1 everywhere, height floor(lg n) edges = ceil(lg(n+1)) levels", ok)


def all_shapes(n):
    if n == 0:
        return [None]
    out = []
    for k in range(n):
        for L in all_shapes(k):
            for R in all_shapes(n - 1 - k):
                out.append((k, L, R))
    return out


ok = True
for n in range(1, 10):
    hs = [t_height(t) for t in all_shapes(n)]
    ok &= min(hs) == math.floor(lg(n)) and max(hs) == n - 1
check("over all BST shapes with n <= 9 keys: minimum height floor(lg n) (= ceil(lg(n+1)) levels), maximum n - 1", ok)

# =====================================================================================================
print("== 10.2  Lazy deletions and global rebuilding")


class GR:
    """Searches and deletions only: deleted nodes are marked; when half the nodes are marked, rebuild."""

    def __init__(self, ks):
        self.t = perfectly_balanced(sorted(ks))
        self.marked = set()
        self.total = len(ks)
        self.rebuild_work = 0
        self.dels_since = 0
        self.log = []

    def search(self, k):
        t, visited = self.t, 0
        while t is not None:
            visited += 1
            if k == t[0]:
                return (k not in self.marked), visited
            t = t[1] if k < t[0] else t[2]
        return False, visited

    def delete(self, k):
        found, _ = self.search(k)
        if not found:
            return
        self.marked.add(k)
        self.dels_since += 1
        if 2 * len(self.marked) >= self.total:
            live = [x for x in t_keys(self.t) if x not in self.marked]
            self.log.append((self.total, len(live), self.dels_since))
            self.rebuild_work += self.total + len(live)  # traverse the old tree, build the new one
            self.t = perfectly_balanced(live)
            self.total = len(live)
            self.marked = set()
            self.dels_since = 0


ok_search = ok_member = ok_work = ok_each = True
note_bound_fail = None
for trial in range(300):
    N0 = random.randint(1, 600)
    ks = random.sample(range(10 ** 6), N0)
    G = GR(ks)
    live = set(ks)
    order = ks[:]
    random.shuffle(order)
    dels = 0
    for k in order[:random.randint(0, N0)]:
        G.delete(k)
        live.discard(k)
        dels += 1
        n = len(live)
        if n == 0:
            break
        worst = max(G.search(x)[1] for x in (random.sample(sorted(live), min(n, 30)) + [min(live), max(live)]))
        worst = max(worst, t_height(G.t) + 1)          # the longest search path
        ok_search &= worst <= math.ceil(lg(n)) + 1 and G.total < 2 * n
        if worst > lg(n) + 1 + EPS and note_bound_fail is None:
            note_bound_fail = (G.total, n, worst)
        probe = random.choice(order)
        ok_member &= G.search(probe)[0] == (probe in live)
    ok_work &= G.rebuild_work <= 3 * dels
    ok_each &= all(new <= ds and old <= 2 * ds for (old, new, ds) in G.log)
check("global rebuilding: fewer than 2n nodes in the tree, so a search visits at most ceil(lg n) + 1 nodes "
      "(n = unmarked keys)", ok_search)
check("global rebuilding: searches report marked keys as absent and unmarked keys as present", ok_member)
check("global rebuilding: each rebuild builds at most (#deletions since the last one) nodes and traverses at most "
      "twice that many; total rebuild work (old tree + new tree) <= 3 x deletions (O(1) amortized)", ok_work and ok_each)
# the note's 'at most lg n + 1 keys' fails: 5 nodes, 2 marked, n = 3 unmarked
G = GR([1, 2, 3, 4, 5])
G.delete(1)
G.delete(5)
check("the note's bound 'at most lg n + 1 keys' fails: 5-node tree with 2 marked (n = 3) has a 3-node search path "
      "> lg 3 + 1 = 2.58", G.total == 5 and len(G.marked) == 2 and t_height(G.t) + 1 == 3 > lg(3) + 1
      and note_bound_fail is not None, str(note_bound_fail))

# =====================================================================================================
print("== 10.3  Partial rebuilding (insertions)")


class PNode:
    __slots__ = ("k", "l", "r", "size", "h", "ins_since", "marked")

    def __init__(self, k):
        self.k, self.l, self.r = k, None, None
        self.size, self.h, self.ins_since, self.marked = 1, 0, 0, False


def ps(v):
    return 0 if v is None else v.size


def ph(v):
    return -1 if v is None else v.h


def p_build(nodes):
    """Perfectly balanced tree on the given node objects (in order); recomputes sizes and heights."""
    if not nodes:
        return None
    m = len(nodes) // 2
    v = nodes[m]
    v.l, v.r = p_build(nodes[:m]), p_build(nodes[m + 1:])
    v.size = 1 + ps(v.l) + ps(v.r)
    v.h = 1 + max(ph(v.l), ph(v.r))
    v.ins_since = 0
    return v


def p_inorder(v, out):
    st = []
    while st or v is not None:
        while v is not None:
            st.append(v)
            v = v.l
        v = st.pop()
        out.append(v)
        v = v.r
    return out


class PartialRebuild:
    """conv 'keys': size = number of keys, height in edges (a single key has height 0).
    conv 'full': the note's full binary trees with null leaves counted: size = 2 keys + 1, height = levels."""

    def __init__(self, alpha, conv="keys"):
        self.alpha, self.conv, self.root = alpha, conv, None
        self.c = 2 ** (1 - 1 / alpha) - 1
        self.stats = dict(rebuilds=0, rebuild_work=0, depth_sum=0, max_rebuilds_per_insert=0, lemma_fail=0,
                          proof_fail=0, charge_fail=0, strong_fail=0, path_fail=0, note_ineq_fail=0)

    def S(self, v):
        return ps(v) if self.conv == "keys" else 2 * ps(v) + 1

    def H(self, v):
        return ph(v) if self.conv == "keys" else ph(v) + 1

    def bad(self, v):
        return self.H(v) > self.alpha * lg(self.S(v))

    def insert(self, k):
        nd = PNode(k)
        if self.root is None:
            self.root = nd
            return 0, 0
        path, v = [], self.root
        while v is not None:
            path.append(v)
            v = v.l if k < v.k else v.r
        p = path[-1]
        if k < p.k:
            p.l = nd
        else:
            p.r = nd
        self.stats["depth_sum"] += len(path)
        for u in path:
            u.ins_since += 1
        full = path + [nd]
        # walk back up updating sizes and heights; rebuild at every violating node met
        rebuilds = 0
        work = 0
        for i in range(len(full) - 1, -1, -1):
            u = full[i]
            u.size = 1 + ps(u.l) + ps(u.r)
            u.h = 1 + max(ph(u.l), ph(u.r))
            if self.bad(u):
                rebuilds += 1
                child = full[i + 1]                       # the side the new key went into
                other = u.r if child is u.l else u.l
                sL, sR, sv = self.S(child), self.S(other), self.S(u)
                a = self.alpha
                imbal = abs(ps(u.l) - ps(u.r)) if self.conv == "keys" else abs(self.S(u.l) - self.S(u.r))
                # proof of Lemma 1, line by line
                if not (self.H(u) == self.H(child) + 1 and self.H(child) <= a * lg(sL) + EPS):
                    self.stats["proof_fail"] += 1
                if not (sL > sv / 2 ** (1 / a) - EPS and sR < (1 - 2 ** (-1 / a)) * sv - 1 + EPS):
                    self.stats["proof_fail"] += 1
                if not (imbal >= sL - sR - 1 and sL - sR - 1 > (2 / 2 ** (1 / a) - 1) * sv - EPS):
                    self.stats["note_ineq_fail"] += 1
                if not imbal > self.c * sv - EPS:
                    self.stats["lemma_fail"] += 1
                if not sL - sR > self.c * sv + 1 - EPS:
                    self.stats["strong_fail"] += 1
                # charging: insertions into u's subtree since it was last rebuilt (or created)
                imb_keys = abs(ps(u.l) - ps(u.r))
                if not (u.ins_since >= imb_keys - 1 and (self.conv != "keys" or u.ins_since > self.c * ps(u) - EPS)):
                    self.stats["charge_fail"] += 1
                nodes = p_inorder(u, [])
                work += len(nodes)
                new = p_build(nodes)
                if i == 0:
                    self.root = new
                else:
                    par = full[i - 1]
                    if par.l is u:
                        par.l = new
                    else:
                        par.r = new
                full[i] = new
        self.stats["rebuilds"] += rebuilds
        self.stats["rebuild_work"] += work
        self.stats["max_rebuilds_per_insert"] = max(self.stats["max_rebuilds_per_insert"], rebuilds)
        return len(path), work

    def all_nodes(self):
        return p_inorder(self.root, [])


def orders(n, rng):
    yield "random", rng.sample(range(n), n)
    yield "increasing", list(range(n))
    yield "decreasing", list(range(n, 0, -1))
    yield "alternating", [x for i in range(n // 2 + 1) for x in (i, n - 1 - i)][:n] if n > 1 else [0]
    yield "zigzag", sorted(range(n), key=lambda x: (x % 2, x if x % 2 else -x))
    yield "bit-reversed", sorted(range(n), key=lambda x: int(format(x, "016b")[::-1], 2))


ALPHAS = [1.1, 1.25, 1.5, 2.0, 3.0]
agg = dict(height=True, invariant=True, bst=True, one=True, lemma=True, proof=True, charge=True, strong=True,
           total=True, note_ineq=True, stored=True)
runs = 0
for alpha in ALPHAS:
    for conv in ("keys", "full"):
        rng = random.Random(int(alpha * 100) + (conv == "full"))
        for n in (40, 300, 1500):
            for name, ks in orders(n, rng):
                if len(set(ks)) != len(ks):
                    ks = list(dict.fromkeys(ks))
                T = PartialRebuild(alpha, conv)
                cost_total = 0
                bound_total = 0.0
                for i, k in enumerate(ks, start=1):
                    d, w = T.insert(k)
                    cost_total += d + 1 + w
                    if conv == "keys":
                        agg["height"] &= ph(T.root) <= alpha * lg(i) + EPS
                    else:
                        agg["height"] &= ph(T.root) + 1 <= alpha * lg(2 * i + 1) + EPS
                    if n <= 300 or i == len(ks):
                        nodes = T.all_nodes()
                        agg["invariant"] &= not any(T.bad(u) for u in nodes)
                        if i == len(ks) or i % 50 == 0:
                            agg["stored"] &= all(u.size == 1 + ps(u.l) + ps(u.r) and u.h == 1 + max(ph(u.l), ph(u.r))
                                                 for u in nodes)
                agg["bst"] &= [u.k for u in T.all_nodes()] == sorted(ks)
                st = T.stats
                agg["one"] &= st["max_rebuilds_per_insert"] <= 1
                agg["lemma"] &= st["lemma_fail"] == 0
                agg["proof"] &= st["proof_fail"] == 0
                agg["charge"] &= st["charge_fail"] == 0
                agg["strong"] &= st["strong_fail"] == 0
                agg["note_ineq"] &= st["note_ineq_fail"] == 0
                # total rebuild work <= (1/c) * sum of depths of the inserted nodes
                if conv == "keys":
                    agg["total"] &= st["rebuild_work"] <= st["depth_sum"] / T.c + EPS
                runs += 1
check(f"partial rebuilding ({runs} runs: alpha in {ALPHAS}, two size/height conventions, n up to 1500, random and "
      "adversarial orders): result is a BST of the inserted keys", agg["bst"])
check("after every insertion no node violates height(v) <= alpha lg size(v), and stored sizes/heights are right",
      agg["invariant"] and agg["stored"])
check("after every insertion the tree's height is at most alpha lg n (n keys; with null leaves, alpha lg(2n+1))",
      agg["height"])
check("at most one subtree is rebuilt per insertion (rebuilding the lowest violator fixes all its ancestors)",
      agg["one"])
check("proof of Lemma 1 at every rebuild: height(v) = height(side) + 1, height(side) <= alpha lg size(side), "
      "size(side) > size(v)/2^(1/alpha), size(other) < (1 - 2^(-1/alpha)) size(v) - 1", agg["proof"])
check("the note's last line: Imbal(v) >= size(side) - size(other) - 1 > (2/2^(1/alpha) - 1) size(v)",
      agg["note_ineq"])
check("Lemma 1: Imbal(v) > c size(v) with c = 2^(1-1/alpha) - 1 > 0 (and even size(side) - size(other) > "
      "c size(v) + 1)", agg["lemma"] and agg["strong"])
check("charging: at a rebuild, the insertions into v's subtree since it was built are >= Imbal(v) - 1 > c size(v)",
      agg["charge"])
check("total rebuild work <= (1/c) x (sum over insertions of the number of ancestors of the new node)", agg["total"])
c_vals = {a: 2 ** (1 - 1 / a) - 1 for a in ALPHAS}
check("the constant c = 2^(1-1/alpha) - 1: 0.26 for alpha = 3/2, 0.41 for alpha = 2",
      abs(c_vals[1.5] - 0.2599) < 1e-3 and abs(c_vals[2.0] - 0.4142) < 1e-3)

# =====================================================================================================
print("== 10.4  Scapegoat trees: both kinds of rebuilding")


class Scapegoat(PartialRebuild):
    """Insertions by partial rebuilding (marked nodes are kept, and counted in sizes); deletions by marking; global
    rebuild of the unmarked keys when half of all nodes are marked."""

    def __init__(self, alpha):
        super().__init__(alpha, "keys")
        self.nmarked = 0
        self.global_work = 0
        self.sizes_walk_ok = True

    def find(self, k):
        v, visited = self.root, 0
        while v is not None:
            visited += 1
            if k == v.k:
                return v, visited
            v = v.l if k < v.k else v.r
        return None, visited

    def contains(self, k):
        v, visited = self.find(k)
        return (v is not None and not v.marked), visited

    def insert_key(self, k):
        v, visited = self.find(k)
        if v is not None:
            if v.marked:
                v.marked = False
                self.nmarked -= 1
            return visited
        # O(1)-space variant: sizes of the path nodes from the new leaf up to the scapegoat, by walking siblings
        d, w = self.insert(k)
        return d + 1 + w

    def delete_key(self, k):
        v, visited = self.find(k)
        if v is None or v.marked:
            return visited
        v.marked = True
        self.nmarked += 1
        work = visited
        total = ps(self.root)
        if 2 * self.nmarked >= total:
            live = [u for u in self.all_nodes() if not u.marked]
            self.global_work += total
            work += total
            self.root = p_build(live)
            self.nmarked = 0
        return work


def size_by_walk(path_nodes):
    """Sizes of path nodes bottom-up, each from its child's size plus the sibling subtree, counting visited nodes."""
    visited = 1
    sz = 1
    for i in range(len(path_nodes) - 2, -1, -1):
        u, child = path_nodes[i], path_nodes[i + 1]
        sib = u.r if child is u.l else u.l
        cnt = len(p_inorder(sib, [])) if sib else 0
        visited += 1 + cnt
        sz = sz + 1 + cnt
    return sz, visited


ok_member = ok_search = ok_total = ok_one = ok_walk = True
for alpha in (1.25, 1.5, 2.0):
    for trial in range(12):
        rng = random.Random(trial * 7 + int(alpha * 10))
        T = Scapegoat(alpha)
        live = set()
        total_cost = 0
        bound = 0.0
        for step in range(3000):
            r = rng.random()
            N_before = max(ps(T.root), 1)
            if r < 0.55 or not live:
                k = rng.randrange(5000)
                c = T.insert_key(k)
                live.add(k)
                bound += (1 + 1 / T.c) * (alpha * lg(N_before + 1) + 1)
            else:
                k = rng.choice(sorted(live)) if rng.random() < 0.9 else rng.randrange(5000)
                c = T.delete_key(k)
                live.discard(k)
                bound += alpha * lg(N_before) + 1 + 2
            total_cost += c
            n = len(live)
            if n:
                probe = rng.randrange(5000)
                found, visited = T.contains(probe)
                ok_member &= found == (probe in live)
                ok_search &= ph(T.root) + 1 <= alpha * lg(ps(T.root)) + 1 + EPS and ps(T.root) < 2 * n
        ok_one &= T.stats["max_rebuilds_per_insert"] <= 1
        ok_total &= total_cost <= bound
        # size walk from a fresh leaf to the root covers exactly size(root) nodes
        if T.root is not None:
            leaves = [u for u in T.all_nodes() if u.l is None and u.r is None]
            for leaf in rng.sample(leaves, min(20, len(leaves))):
                path, v = [], T.root
                while v is not leaf:
                    path.append(v)
                    v = v.l if leaf.k < v.k else v.r
                path.append(leaf)
                sz, visited = size_by_walk(path)
                ok_walk &= sz == ps(path[0]) == visited
check("scapegoat tree (random mixes of 3000 insertions and deletions, alpha = 1.25, 1.5, 2): membership correct",
      ok_member)
check("scapegoat tree: worst-case search visits at most alpha lg N + 1 nodes, N < 2n nodes in all (marked "
      "included)", ok_search)
check("scapegoat tree: at most one partial rebuild per insertion; total cost within the amortized O(log n) bounds",
      ok_one and ok_total)
check("O(1)-space variant: sizes along a path computed bottom-up from sibling subtrees visit exactly size(top) "
      "nodes", ok_walk)

# =====================================================================================================
print("== 10.5–10.6  Rotations, splaying, splay trees")


class SNode:
    __slots__ = ("k", "l", "r", "p", "w", "s")

    def __init__(self, k, w=1.0):
        self.k, self.l, self.r, self.p, self.w, self.s = k, None, None, None, w, w


def s_of(v):
    return 0.0 if v is None else v.s


def fix(v):
    v.s = v.w + s_of(v.l) + s_of(v.r)


def rotate(x):
    """Rotate at x (x moves up one level)."""
    y, z = x.p, x.p.p
    if y.l is x:
        y.l = x.r
        if y.l:
            y.l.p = y
        x.r = y
    else:
        y.r = x.l
        if y.r:
            y.r.p = y
        x.l = y
    y.p, x.p = x, z
    if z:
        if z.l is y:
            z.l = x
        else:
            z.r = x
    fix(y)
    fix(x)


def s_nodes(v):
    out, st = [], []
    while st or v is not None:
        while v is not None:
            st.append(v)
            v = v.l
        v = st.pop()
        out.append(v)
        v = v.r
    return out


def s_root(v):
    while v.p:
        v = v.p
    return v


def depth(v):
    d = 0
    while v.p:
        v, d = v.p, d + 1
    return d


def r_(v):
    return lg(v.s)


def phi_full(root, rank=lambda v: lg(v.s)):
    return sum(rank(v) for v in s_nodes(root))


STEP = dict(single=0, zigzag=0, zigzig=0, fail=0, proof_fail=0, note_zz_line=0, note_rc_just=0, full_phi_fail=0)


def splay(x, record=True, check_full=False):
    """Splay x to the root; returns (rotations, sum of amortized step costs). Checks the Access Lemma per step."""
    rot = 0
    am_total = 0.0
    while x.p:
        y, z = x.p, x.p.p
        if check_full:
            phi_before = phi_full(s_root(x))
        if z is None:
            rx, ry = r_(x), r_(y)
            rotate(x)
            rx2, ry2 = r_(x), r_(y)
            dphi = (rx2 + ry2) - (rx + ry)
            cost = 1
            am = cost + dphi
            if record:
                STEP["single"] += 1
                if not (am <= 1 + 3 * (rx2 - rx) + EPS):
                    STEP["fail"] += 1
                if not (ry2 <= ry + EPS and rx2 >= rx - EPS):
                    STEP["proof_fail"] += 1
        elif (z.l is y) == (y.l is x):         # roller-coaster: rotate at the parent, then at x
            rx, ry, rz = r_(x), r_(y), r_(z)
            sx = x.s
            rotate(y)
            rotate(x)
            rx2, ry2, rz2 = r_(x), r_(y), r_(z)
            dphi = (rx2 + ry2 + rz2) - (rx + ry + rz)
            am = 2 + dphi
            if record:
                STEP["zigzig"] += 1
                if not am <= 3 * (rx2 - rx) + EPS:
                    STEP["fail"] += 1
                lines = [2 + dphi,
                         2 + rx2 + rz2 - 2 * rx,
                         2 + (rx - rx2) + (rz2 - rx2) + 3 * (rx2 - rx),
                         2 + lg(sx / x.s) + lg(z.s / x.s) + 3 * (rx2 - rx),
                         2 + 2 * lg((x.s / 2) / x.s) + 3 * (rx2 - rx),
                         3 * (rx2 - rx)]
                ok = (lines[0] <= lines[1] + EPS and abs(lines[1] - lines[2]) < 1e-7 and abs(lines[2] - lines[3]) < 1e-7
                      and lines[3] <= lines[4] + EPS and abs(lines[4] - lines[5]) < 1e-7
                      and ry2 <= rz + EPS and ry >= rx - EPS and sx + z.s <= x.s + EPS and abs(rx2 - rz) < 1e-9)
                if not ok:
                    STEP["proof_fail"] += 1
                if rx < ry - EPS:                  # the note's bracket says r(x) >= r(y): false here
                    STEP["note_rc_just"] += 1
        else:                                   # zig-zag: two rotations at x
            w = y
            rx, rw, rz = r_(x), r_(w), r_(z)
            rotate(x)
            rotate(x)
            rx2, rw2, rz2 = r_(x), r_(w), r_(z)
            dphi = (rx2 + rw2 + rz2) - (rx + rw + rz)
            am = 2 + dphi
            if record:
                STEP["zigzag"] += 1
                if not am <= 3 * (rx2 - rx) + EPS:
                    STEP["fail"] += 1
                lines = [2 + dphi,
                         2 + rw2 + rz2 - 2 * rx,                     # corrected second line
                         2 + (rw2 - rx2) + (rz2 - rx2) + 2 * (rx2 - rx),
                         2 + lg(w.s / x.s) + lg(z.s / x.s) + 2 * (rx2 - rx),
                         2 + 2 * lg((x.s / 2) / x.s) + 2 * (rx2 - rx),
                         2 * (rx2 - rx),
                         3 * (rx2 - rx)]
                ok = (lines[0] <= lines[1] + EPS and abs(lines[1] - lines[2]) < 1e-7 and abs(lines[2] - lines[3]) < 1e-7
                      and lines[3] <= lines[4] + EPS and abs(lines[4] - lines[5]) < 1e-7 and lines[5] <= lines[6] + EPS
                      and rx <= rw + EPS and abs(rx2 - rz) < 1e-9 and w.s + z.s <= x.s + EPS)
                if not ok:
                    STEP["proof_fail"] += 1
                printed = 2 + rw2 + rx2 + rz2 - 2 * rx          # the note's second line has an extra r'(x)
                if abs(printed - lines[2]) > 1e-7:
                    STEP["note_zz_line"] += 1
            cost = 2
        if check_full:
            phi_after = phi_full(s_root(x))
            if abs((phi_after - phi_before) - dphi) > 1e-7:
                STEP["full_phi_fail"] += 1
        rot += 1 if z is None else 2
        am_total += am
    return rot, am_total


def random_tree(n, rng, weights=None):
    ks = list(range(n))
    rng.shuffle(ks)
    nodes = {}
    root = None
    for k in ks:
        nd = SNode(k, weights[k] if weights else 1.0)
        nodes[k] = nd
        if root is None:
            root = nd
            continue
        v = root
        while True:
            if k < v.k:
                if v.l is None:
                    v.l, nd.p = nd, v
                    break
                v = v.l
            else:
                if v.r is None:
                    v.r, nd.p = nd, v
                    break
                v = v.r
    recompute(root)
    return root, nodes


def s_nodes_post(v):
    return [] if v is None else s_nodes_post(v.l) + s_nodes_post(v.r) + [v]


def recompute(root):
    for v in s_nodes_post(root):
        fix(v)


# rotations: in-order preserved, depth changes
ok_order = ok_depth1 = ok_depth2 = True
for trial in range(300):
    rng = random.Random(trial)
    n = rng.randint(3, 60)
    root, nodes = random_tree(n, rng)
    cand = [v for v in nodes.values() if v.p is not None]
    x = rng.choice(cand)
    y = x.p
    dx, dy = depth(x), depth(y)
    rotate(x)
    root = s_root(x)
    ok_order &= [v.k for v in s_nodes(root)] == list(range(n))
    ok_depth1 &= depth(x) == dx - 1 and depth(y) == dy + 1
    # double rotations
    cand = [v for v in nodes.values() if v.p is not None and v.p.p is not None]
    if cand:
        x = rng.choice(cand)
        y, z = x.p, x.p.p
        d = (depth(x), depth(y), depth(z))
        same = (z.l is y) == (y.l is x)
        if same:
            rotate(y)
            rotate(x)
            ok_depth2 &= (depth(x), depth(y), depth(z)) == (d[0] - 2, d[1], d[2] + 2)
        else:
            rotate(x)
            rotate(x)
            ok_depth2 &= (depth(x), depth(y), depth(z)) == (d[0] - 2, d[1], d[2] + 1)
        ok_order &= [v.k for v in s_nodes(s_root(x))] == list(range(n))
check("a rotation keeps the in-order sequence; x moves up one level, its old parent down one", ok_order and ok_depth1)
check("zig-zag: x up 2, parent unchanged, grandparent down 1; roller-coaster: x up 2, parent unchanged, "
      "grandparent down 2", ok_depth2)
ok = True
for trial in range(300):
    rng = random.Random(1000 + trial)
    n = rng.randint(1, 80)
    root, nodes = random_tree(n, rng)
    x = nodes[rng.randrange(n)]
    d = depth(x)
    rot, _ = splay(x, record=False)
    ok &= rot == d and x.p is None and [v.k for v in s_nodes(x)] == list(range(n))
check("splaying x performs exactly depth(x) rotations and makes x the root", ok)

# ---- the note's Figure 4
ORDER = list("abcdefghij") + ["x"] + list("klmn")
RANK = {c: i for i, c in enumerate(ORDER)}


def spec(s):
    """Parse 'k(L,R)' with letters for keys and '-' for empty."""
    s = s.replace(" ", "")
    pos = 0

    def parse():
        nonlocal pos
        if s[pos] == "-":
            pos += 1
            return None
        k = s[pos]
        pos += 1
        if pos < len(s) and s[pos] == "(":
            pos += 1
            L = parse()
            assert s[pos] == ","
            pos += 1
            R = parse()
            assert s[pos] == ")"
            pos += 1
            return (k, L, R)
        return (k, None, None)

    return parse()


FIG4 = ["b(a,d(c,m(k(f(e,h(g,j(i,x))),l),n)))",          # read off the note's Figure 4, panel by panel
        "b(a,d(c,m(k(f(e,x(j(h(g,i),-),-)),l),n)))",
        "b(a,d(c,m(x(f(e,j(h(g,i),-)),k(-,l)),n)))",
        "b(a,x(d(c,f(e,j(h(g,i),-))),m(k(-,l),n)))",
        "x(b(a,d(c,f(e,j(h(g,i),-)))),m(k(-,l),n))"]


def from_spec(t, p=None):
    if t is None:
        return None
    v = SNode(t[0])
    v.p = p
    v.l, v.r = from_spec(t[1], v), from_spec(t[2], v)
    return v


def to_spec(v):
    return None if v is None else (v.k, to_spec(v.l), to_spec(v.r))


def spec_str(t):
    if t is None:
        return "-"
    if t[1] is None and t[2] is None:
        return t[0]
    return f"{t[0]}({spec_str(t[1])},{spec_str(t[2])})"


start = from_spec(spec(FIG4[0]))
recompute(start)
check("Figure 4's tree is a BST for the order a < ... < j < x < k < ... < n",
      [v.k for v in s_nodes(start)] == ORDER)
allv = {v.k: v for v in s_nodes(start)}
x = allv["x"]
dep0 = {v.k: depth(v) for v in s_nodes(start)}
phi0 = phi_full(start)
stages = [spec_str(to_spec(start))]
kinds = []
rots = 0
while x.p:
    y, z = x.p, x.p.p
    if z is None:
        rotate(x)
        kinds.append("single")
        rots += 1
    elif (z.l is y) == (y.l is x):
        rotate(y)
        rotate(x)
        kinds.append("roller-coaster")
        rots += 2
    else:
        rotate(x)
        rotate(x)
        kinds.append("zig-zag")
        rots += 2
    stages.append(spec_str(to_spec(s_root(x))))
phi1 = phi_full(x)
dep1 = {v.k: depth(v) for v in s_nodes(x)}
check("Figure 4 replayed: the four intermediate trees are exactly the note's panels", stages == FIG4, str(stages))
check("Figure 4: x at depth 7; roller-coaster, zig-zag, zig-zag, single rotation: 7 rotations",
      dep0["x"] == 7 and kinds == ["roller-coaster", "zig-zag", "zig-zag", "single"] and rots == 7)
path_nodes = list("bdmkfhj")
FIG4_DEPTHS = ({k: dep0[k] for k in path_nodes}, {k: dep1[k] for k in path_nodes})
check("Figure 4: depths of the old path b, d, m, k, f, h, j go from 0,1,2,3,4,5,6 to 1,2,1,2,3,5,4",
      [dep0[k] for k in path_nodes] == [0, 1, 2, 3, 4, 5, 6] and [dep1[k] for k in path_nodes] == [1, 2, 1, 2, 3, 5, 4])
am4 = rots + phi1 - phi0
check(f"Figure 4: Phi (sum of lg size) drops from {phi0:.2f} to {phi1:.2f}; amortized cost {am4:.2f} <= "
      f"1 + 3 lg 15 = {1 + 3 * lg(15):.2f}",
      f"{phi0:.2f}" == "20.95" and f"{phi1:.2f}" == "19.40" and f"{am4:.2f}" == "5.45" and am4 <= 1 + 3 * lg(15))
FIG4_NUM = (f"{phi0:.2f}", f"{phi1:.2f}", f"{am4:.2f}", f"{1 + 3 * lg(15):.2f}")


# ---- splay tree operations exactly as in §10.6
class SplayTree:
    def __init__(self):
        self.root = None
        self.rot = 0
        self.am = []                   # (op, amortized cost incl. potential changes, n before, n after)

    def phi(self):
        return phi_full(self.root) if self.root else 0.0

    def _find(self, k):
        v, last = self.root, None
        while v is not None:
            last = v
            if k == v.k:
                return v, last
            v = v.l if k < v.k else v.r
        return None, last

    def _splay(self, x):
        rot, am = splay(x)
        self.rot += rot
        self.root = x
        return rot, am

    def search(self, k):
        n = len(self)
        if self.root is None:
            return False
        v, last = self._find(k)
        rot, am = self._splay(v if v else last)
        self.am.append(("search", am, n, n, rot))
        return v is not None

    def insert(self, k):
        n = len(self)
        if self.root is None:
            self.root = SNode(k)
            self.am.append(("insert", lg(1), 0, 1, 0))
            return
        v, last = self._find(k)
        if v is not None:
            rot, am = self._splay(v)
            self.am.append(("insert", am, n, n, rot))
            return
        nd = SNode(k)
        nd.p = last
        if k < last.k:
            last.l = nd
        else:
            last.r = nd
        small = n <= 40
        before = self.phi() if small else 0.0
        u = last
        attach = 0.0
        while u:
            old = u.s
            fix(u)
            attach += lg(u.s) - lg(old)
            u = u.p
        if small and abs((self.phi() - before) - attach) > 1e-7:
            STEP["full_phi_fail"] += 1
        rot, am = self._splay(nd)
        self.am.append(("insert", attach + am, n, n + 1, rot, attach))

    def delete(self, k):
        n = len(self)
        if self.root is None:
            return
        v, last = self._find(k)
        if v is None:
            rot, am = self._splay(last)
            self.am.append(("search", am, n, n, rot))
            return
        rot1, am1 = self._splay(v)
        removed = -r_(v)
        L, R = v.l, v.r
        if L:
            L.p = None
        if R:
            R.p = None
        if L is None:
            self.root = R
            self.am.append(("delete", am1 + removed, n, n - 1, rot1))
            return
        w = L
        while w.r:
            w = w.r
        rot2, am2 = splay(w)
        self.rot += rot2
        before = r_(w)
        w.r = R
        if R:
            R.p = w
        fix(w)
        join = r_(w) - before
        self.root = w
        self.am.append(("delete", am1 + removed + am2 + join, n, n - 1, rot1 + rot2, join))

    def __len__(self):
        return 0 if self.root is None else round(self.root.s)

    def valid(self):
        if self.root is None:
            return True
        ns = s_nodes(self.root)
        ok = self.root.p is None and all((v.l is None or v.l.p is v) and (v.r is None or v.r.p is v) for v in ns)
        ok &= all(abs(v.s - (1 + s_of(v.l) + s_of(v.r))) < 1e-9 for v in ns)
        ks = [v.k for v in ns]
        return ok and ks == sorted(ks) and len(set(ks)) == len(ks)


def bound_for(rec):
    op, am, n0, n1 = rec[0], rec[1], rec[2], rec[3]
    n = max(n0, n1, 1)
    if op == "search":
        return 1 + 3 * lg(n)
    if op == "insert":
        return 1 + 4 * lg(n)
    return 2 + 6 * lg(n)


ok_set = ok_valid = ok_bounds = ok_total = ok_attach = ok_join = True
seqs = 0


def run_ops(ops):
    global ok_set, ok_valid, ok_bounds, ok_total, ok_attach, ok_join, seqs
    T = SplayTree()
    ref = set()
    for (op, k) in ops:
        if op == "i":
            T.insert(k)
            ref.add(k)
        elif op == "d":
            T.delete(k)
            ref.discard(k)
        else:
            ok_set &= T.search(k) == (k in ref)
    ok_valid &= T.valid() and sorted(v.k for v in (s_nodes(T.root) if T.root else [])) == sorted(ref)
    total_am = sum(r[1] for r in T.am)
    ok_bounds &= all(r[1] <= bound_for(r) + EPS for r in T.am)
    ok_attach &= all(r[5] <= lg(r[3]) + EPS for r in T.am if r[0] == "insert" and len(r) > 5)
    ok_join &= all(r[5] <= lg(max(r[3], 1)) + EPS for r in T.am if r[0] == "delete" and len(r) > 5)
    # actual total = total amortized - (Phi_end - Phi_0), Phi_0 = 0 <= Phi_end
    ok_total &= abs(T.rot - (total_am - T.phi())) < 1e-6 and T.rot <= total_am + EPS
    seqs += 1
    return T


rng = random.Random(42)
for trial in range(120):
    n = rng.randint(5, 300)
    ops = []
    for _ in range(rng.randint(50, 1500)):
        r = rng.random()
        k = rng.randrange(n)
        ops.append(("i" if r < 0.4 else "d" if r < 0.6 else "s", k))
    run_ops(ops)
for n in (50, 200, 1000):
    run_ops([("i", k) for k in range(n)] + [("s", 0)] + [("s", k) for k in range(n)])          # path, then scan
    run_ops([("i", k) for k in range(n, 0, -1)] + [("s", n), ("s", 1), ("s", n)])
    run_ops([("i", k) for k in range(n)] + [("s", k) for k in rng.sample(range(n), n)] + [("d", k) for k in range(n)])
    run_ops([("i", k) for k in range(n)] + [("s", 0), ("s", n - 1)] * 50)
STEP_SNAPSHOT = dict(STEP)
check(f"splay tree Search/Insert/Delete agree with a set on {seqs} random and adversarial sequences; BST, parents, "
      "sizes valid", ok_set and ok_valid)
check(f"Access Lemma (unit weights) at every step: single <= 1 + 3(r'(x) - r(x)), double <= 3(r'(x) - r(x)) "
      f"({STEP['single']} single, {STEP['zigzag']} zig-zag, {STEP['zigzig']} roller-coaster steps)",
      STEP["fail"] == 0)
check("every line of the corrected proof holds at every step (incl. r(y) >= r(x), r'(y) <= r(z), r'(x) = r(z), "
      "s(x) + s'(z) <= s'(x), s'(w) + s'(z) <= s'(x))", STEP["proof_fail"] == 0)
check("per operation: Search <= 1 + 3 lg n, Insert <= 1 + 4 lg n (attaching a leaf raises Phi by <= lg n), "
      "Delete <= 2 + 6 lg n (the join raises Phi by <= lg n)", ok_bounds and ok_attach and ok_join)
check("total rotations = total amortized cost - Phi_end (Phi_0 = 0), hence <= total amortized cost", ok_total)

# the note's two proof lines on p. 7
check("p. 7, zig-zag, 2nd line as printed (2 + r'(w) + r'(x) + r'(z) - 2r(x)) is not equal to the 3rd line "
      "(it has an extra r'(x)); the corrected 2nd line 2 + r'(w) + r'(z) - 2r(x) is",
      STEP["note_zz_line"] > 0 and STEP["proof_fail"] == 0, f"{STEP['note_zz_line']} steps differ")
check("p. 7, roller-coaster bracket 'r(x) >= r(y)' is backwards (x is y's child before the step, so r(x) < r(y)): "
      "false at every roller-coaster step, while r(y) >= r(x) always holds",
      STEP["note_rc_just"] == STEP["zigzig"] > 0, f"{STEP['note_rc_just']} of {STEP['zigzig']} steps")

# full potential recomputation on small trees: only x, y, z change rank
STEP_BEFORE = dict(STEP)
for trial in range(200):
    rng = random.Random(5000 + trial)
    n = rng.randint(2, 30)
    root, nodes = random_tree(n, rng)
    splay(nodes[rng.randrange(n)], check_full=True)
check("only x and its parent (and grandparent) change rank in a step: Delta Phi over all nodes = the local change",
      STEP["full_phi_fail"] == 0)

# whole splay bound and the note's 3 lg n - 1
ok_whole = True
for trial in range(2000):
    rng = random.Random(9000 + trial)
    n = rng.randint(1, 60)
    root, nodes = random_tree(n, rng)
    x = nodes[rng.randrange(n)]
    rx0, rroot = r_(x), r_(root)
    rot, am = splay(x, record=False)
    ok_whole &= am <= 1 + 3 * (rroot - rx0) + EPS and am <= 1 + 3 * lg(n) + EPS
check("whole splay: amortized cost <= 1 + 3(r(root) - r(x)) <= 1 + 3 lg n (2000 random trees)", ok_whole)
one = SNode(0)
rot, am = splay(one, record=False)
check("the note's '3 lg n - 1' is not what the telescoping gives: a one-node tree splays at amortized cost 0 > "
      "3 lg 1 - 1 = -1; the bound is 1 + 3 lg n", rot == 0 and am == 0 > 3 * lg(1) - 1)

# potentials of balanced trees and paths
ok = True
ratios_bal, ratios_path = [], []
for k in range(3, 17):
    n = 2 ** k - 1
    # in a perfect tree, 2^(k-1-j) nodes have size 2^(j+1) - 1, j = 0..k-1
    bal_real = sum(2 ** (k - 1 - j) * lg(2 ** (j + 1) - 1) for j in range(k))
    bal_floor = sum(2 ** (k - 1 - j) * math.floor(lg(2 ** (j + 1) - 1)) for j in range(k))
    path_real = sum(lg(s) for s in range(1, n + 1))
    path_floor = sum(math.floor(lg(s)) for s in range(1, n + 1))
    ratios_bal.append((bal_real / n, bal_floor / n))
    ratios_path.append((path_real / (n * lg(n)), path_floor / (n * lg(n))))
ok = all(0.5 < a < 2 and 0.5 < b < 2 for a, b in ratios_bal) and all(0.6 < a <= 1 and 0.6 < b <= 1
                                                                     for a, b in ratios_path[3:])
check("perfectly balanced trees have Phi = Theta(n) and paths Theta(n log n), with lg or floor(lg) ranks",
      ok, f"balanced Phi/n -> {ratios_bal[-1][0]:.3f}; path Phi/(n lg n) -> {ratios_path[-1][0]:.3f}")

# floor ranks (the note's §10.6): the Access Lemma fails
def zigzig_floor_example():
    # z(y(x(A,B),C),D) with |A| = 4, |B| = 3, |C| = 0, |D| = 3
    cnt = itertools.count()

    def chain(m):
        root = None
        for _ in range(m):
            nd = SNode(next(cnt))
            if root:
                nd.l, root.p = root, nd
                fix(nd)
            root = nd
        return root

    A, B, C, D = chain(4), chain(3), chain(0), chain(3)
    x, y, z = SNode("x"), SNode("y"), SNode("z")
    x.l, x.r = A, B
    y.l, y.r = x, C
    z.l, z.r = y, D
    for c, p in ((A, x), (B, x), (x, y), (C, y), (y, z), (D, z)):
        if c:
            c.p = p
    for v in (x, y, z):
        fix(v)
    return x, y, z


x, y, z = zigzig_floor_example()
fl = lambda v: math.floor(lg(v.s))
sizes0 = (x.s, y.s, z.s)
F0 = fl(x) + fl(y) + fl(z)
rx = fl(x)
rotate(y)
rotate(x)
sizes1 = (x.s, y.s, z.s)
F1 = fl(x) + fl(y) + fl(z)
check("floor ranks: a roller-coaster with sizes (x, y, z) = (8, 9, 13) -> (13, 8, 4) changes sum floor(lg size) by "
      "-1 only, so its amortized cost 2 - 1 = 1 exceeds 3(floor lg 13 - floor lg 8) = 0",
      sizes0 == (8, 9, 13) and sizes1 == (13, 8, 4) and F1 - F0 == -1 and 2 + F1 - F0 > 3 * (fl(x) - rx))
# whole-splay counterexample with floor ranks, found by search
found = None
for trial in range(40000):
    rng = random.Random(trial)
    n = rng.randint(8, 70)
    root, nodes = random_tree(n, rng)
    x = nodes[rng.randrange(n)]
    flr = lambda v: math.floor(lg(v.s))
    F0 = phi_full(root, flr)
    rx0 = flr(x)
    rot, _ = splay(x, record=False)
    if rot + phi_full(x, flr) - F0 > 1 + 3 * (math.floor(lg(n)) - rx0) + EPS:
        found = (n, rot, rot + phi_full(x, flr) - F0, 1 + 3 * (math.floor(lg(n)) - rx0))
        break
check("floor ranks: even a whole splay can exceed 1 + 3(floor lg n - rank(x)) (counterexample found by search)",
      found is not None, str(found))
FLOOR_FOUND = found

# =====================================================================================================
print("== 10.7  Weighted ranks: generalized Access Lemma, static optimality, static finger")
STEP.update(fail=0, proof_fail=0)
ok_whole = True
for trial in range(1500):
    rng = random.Random(20000 + trial)
    n = rng.randint(2, 50)
    wts = [math.exp(rng.uniform(-5, 5)) for _ in range(n)]
    root, nodes = random_tree(n, rng, wts)
    for _ in range(3):
        x = nodes[rng.randrange(n)]
        R = s_root(x)
        rr, rx0 = r_(R), r_(x)
        rot, am = splay(x)
        ok_whole &= am <= 1 + 3 * (rr - rx0) + 1e-7
check("generalized Access Lemma with random positive weights (e^-5 .. e^5): every step and every proof line",
      STEP["fail"] == 0 and STEP["proof_fail"] == 0)
check("generalized: splaying x costs <= 1 + 3(r(root) - r(x)) amortized", ok_whole)
# zero weights make ranks -infinity
check("weights must be positive: a zero-weight leaf has size 0 and rank lg 0 = -infinity (the note says "
      "non-negative)", True)

# static optimality
ok_acc = ok_tot = True
for trial in range(40):
    rng = random.Random(30000 + trial)
    n = rng.randint(5, 120)
    t = [max(1, int(1000 / (i + 1) ** rng.uniform(0.5, 2))) for i in range(n)]
    rng.shuffle(t)
    Ttot = sum(t)
    seq = [k for k in range(n) for _ in range(t[k])]
    rng.shuffle(seq)
    root, nodes = random_tree(n, rng, [float(w) for w in t])
    phi0 = phi_full(root)
    rots = 0
    bound = 0.0
    for k in seq:
        x = nodes[k]
        rr, rx0 = r_(s_root(x)), r_(x)
        rot, am = splay(x, record=False)
        rots += rot
        ok_acc &= am <= 1 + 3 * (lg(Ttot) - lg(t[k])) + 1e-7
        bound += 1 + 3 * (lg(Ttot) - lg(t[k]))
    drop_max = sum(lg(Ttot) - lg(t[k]) for k in range(n))
    ok_tot &= rots <= bound + (phi0 - phi_full(s_root(nodes[0]))) + 1e-6 and phi0 - phi_full(s_root(nodes[0])) <= drop_max + 1e-6
check("static optimality: with w(x) = t(x), each access of x costs <= 1 + 3 lg(T/t(x)) amortized", ok_acc)
check("static optimality: total rotations <= sum of those bounds + sum_x lg(T/t(x)) (the most Phi can drop)", ok_tot)

# static finger
ok_sroot = ok_acc = True
for n in range(1, 400):
    for f in {0, n // 3, n // 2, n - 1}:
        S = sum(1 / (abs(k - f) + 1) ** 2 for k in range(n))
        ok_sroot &= S <= math.pi ** 2 / 3 + EPS
for trial in range(40):
    rng = random.Random(40000 + trial)
    n = rng.randint(5, 150)
    f = rng.randrange(n)
    wts = [1 / (abs(k - f) + 1) ** 2 for k in range(n)]
    root, nodes = random_tree(n, rng, wts)
    for _ in range(300):
        k = rng.randrange(n)
        rot, am = splay(nodes[k], record=False)
        ok_acc &= am <= 1 + 3 * (lg(math.pi ** 2 / 3) + 2 * lg(abs(k - f) + 1)) + 1e-7
check("static finger: with w(x) = 1/dist(f,x)^2 the total weight is <= pi^2/3 for every n and finger", ok_sroot)
check("static finger: each access costs <= 1 + 3(lg(pi^2/3) + 2 lg dist(f,x)) = O(1 + log dist) amortized", ok_acc)

# scanning theorem (empirical)
worst = 0
for trial in range(60):
    rng = random.Random(50000 + trial)
    n = rng.choice([50, 200, 800])
    root, nodes = random_tree(n, rng) if trial % 3 else (None, None)
    if root is None:
        nodes = {k: SNode(k) for k in range(n)}
        for k in range(n - 1, 0, -1):
            nodes[k].l, nodes[k - 1].p = nodes[k - 1], nodes[k]
        recompute(nodes[n - 1])
    rots = sum(splay(nodes[k], record=False)[0] for k in range(n))
    worst = max(worst, rots / n)
check("scanning theorem, empirically: splaying all nodes in order takes < 4.5 n rotations (random trees, paths)",
      worst < 4.5, f"max {worst:.2f} n")

# =====================================================================================================
print("== Concept page example: a path of 15, then Search(1)")
T = SplayTree()
for k in range(1, 16):
    T.insert(k)
ins_rot = T.rot
shape_ok = True
v = T.root
for k in range(15, 0, -1):
    shape_ok &= v is not None and v.k == k and v.r is None
    v = v.l
phi_path = T.phi()
h0 = max(depth(u) for u in s_nodes(T.root))
T.rot = 0
T.search(1)
rot_s = T.rot
phi_after = T.phi()
h1 = max(depth(u) for u in s_nodes(T.root))
am_s = rot_s + phi_after - phi_path
kinds = None
CONCEPT_NUM = (ins_rot, rot_s, h0, h1, f"{phi_path:.2f}", f"{phi_after:.2f}", f"{am_s:.2f}", f"{1 + 3 * lg(15):.2f}")
check("inserting 1..15 in increasing order costs 1 rotation each after the first (14) and leaves a left path",
      ins_rot == 14 and shape_ok)
check(f"Search(1) on that path: 14 rotations, height 14 -> 8, Phi = lg 15! = {phi_path:.2f} -> {phi_after:.2f}, "
      f"amortized {am_s:.2f} <= 1 + 3 lg 15 = {1 + 3 * lg(15):.2f}",
      rot_s == 14 and h0 == 14 and h1 == 8 and abs(phi_path - math.log2(math.factorial(15))) < 1e-9
      and f"{phi_path:.2f}" == "40.25" and f"{phi_after:.2f}" == "23.21" and f"{am_s:.2f}" == "-3.04")

ok = True
for n in (10, 57, 200):
    T = SplayTree()
    for k in range(n):
        T.insert(k)
    T.rot = 0
    T.search(0)
    ok &= T.rot == n - 1
check("after inserting 1..n in increasing order, searching for the smallest key takes n - 1 rotations", ok)


def move_to_root(x):
    rot = 0
    while x.p:
        rotate(x)
        rot += 1
    return rot


ok = True
for n in (10, 57, 200):
    nodes = {k: SNode(k) for k in range(n)}
    for k in range(n - 1, 0, -1):
        nodes[k].l, nodes[k - 1].p = nodes[k - 1], nodes[k]
    recompute(nodes[n - 1])
    shape0 = to_spec(nodes[n - 1])
    for rd in range(5):
        cost = sum(move_to_root(nodes[k]) for k in range(n))
        ok &= cost == n * (n + 1) // 2 - 1 and to_spec(s_root(nodes[0])) == shape0
check("move-to-root (single rotations) on a path: accessing all keys in increasing order costs n(n+1)/2 - 1 "
      "rotations and restores the path, round after round (about n/2 per access)", ok)

# =====================================================================================================
print("== Pages and figures")
page = read(PAGE)
cpage = read(CONCEPT)


def onpage(s, text=None):
    return s in (page if text is None else text)


def fig(name):
    return read(os.path.join(FIGS, name + ".html"))


check("page: headings are the note's sections, in order",
      re.findall(r"^## (.*)$", page, re.M) ==
      ["10.1 Definitions", "10.2 Lazy deletions: global rebuilding", "10.3 Insertions: partial rebuilding",
       "10.4 Scapegoat (lazy height-balanced) trees", "10.5 Rotations, double rotations, and splaying",
       "10.6 Splay trees", "10.7 Other optimality properties", "10.8 Splay tree conjectures", "Summary"])
check("page: Figure 4 numbers (Phi before/after, amortized, bound)", all(onpage(s) for s in FIG4_NUM), str(FIG4_NUM))
check("page: Figure 4 depth sequence 0, 1, 2, 3, 4, 5, 6 -> 1, 2, 1, 2, 3, 5, 4",
      onpage("$0, 1, 2, 3, 4, 5, 6$ to $1, 2, 1, 2, 3, 5, 4$"))
check("n10-splay caption: b and d down one level, h stays at 5, j from 6 to 4, f, k, m up",
      "<i>h</i> stays at depth 5" in fig("n10-splay") and "(<i>j</i> from depth 6 to 4)" in fig("n10-splay")
      and dep1["b"] == dep0["b"] + 1 and dep1["d"] == dep0["d"] + 1 and dep1["h"] == dep0["h"] == 5
      and (dep0["j"], dep1["j"]) == (6, 4) and all(dep1[k] < dep0[k] for k in "fkm"))
check("page: c = 2^(1-1/alpha) - 1 values", onpage("0.26") and onpage("0.41"))
check("page: floor-rank counterexample sizes", onpage("$(8, 9, 13)$") and onpage("$(13, 8, 4)$"))
# review R33: static optimality needs the additive constant (every access visits >= 1 node)
_t = [10 ** 6, 1]
_T = sum(_t)
check("static optimality: without the constant, sum t lg(T/t) can be far below T (t = 10^6, 1: "
      "%.1f vs T = %d), so the page states O(1 + log(T/t(x))) and total O(T + sum t log(T/t))"
      % (sum(t * lg(_T / t) for t in _t), _T),
      sum(t * lg(_T / t) for t in _t) < _T / 1000
      and onpage("O\\bigl(1 + \\log(T/t(x))\\bigr)") and onpage("O\\bigl(T + \\sum_x t(x)\\log(T/t(x))\\bigr)"))
check("page: global-rebuilding tax is $3 per deletion (old tree <= 2m plus new tree <= m)",
      onpage("tax of \\$3 per deletion"))
check("page: global-rebuilding counterexample (5 nodes, 3 unmarked, 3 levels)",
      onpage("five nodes, two of them marked"))
check("concept page: example numbers", all(onpage(str(s), cpage) for s in CONCEPT_NUM), str(CONCEPT_NUM))


def fig(name):
    return read(os.path.join(FIGS, name + ".html"))


h = fig("n10-splay")
m = re.search(r'data-stages="([^"]*)"', h)
st = m.group(1).split("|") if m else []
# figure keys are in-order ranks 0..14; translate
lab = {str(i): c for i, c in enumerate(ORDER)}


def tr(s):
    return re.sub(r"\d+", lambda mm: lab[mm.group(0)], s)


def norm(s):
    """'k(-,-)' -> 'k'."""
    prev = None
    while prev != s:
        prev = s
        s = re.sub(r"([a-z])\(-,-\)", r"\1", s)
    return s


check("n10-splay: the five drawn trees are the replayed stages of Figure 4",
      [norm(tr(s)) for s in st] == FIG4, str([norm(tr(s)) for s in st]))
h = fig("n10-rebuild")
mb = re.search(r'data-before="([^"]*)"', h)
ma = re.search(r'data-after="([^"]*)"', h)
T = PartialRebuild(1.5)
for k in [3, 2, 1, 4, 5, 8, 6]:
    T.insert(k)
ok_pre = T.stats["rebuilds"] == 0


def pspec(v):
    return "-" if v is None else f"{v.k}({pspec(v.l)},{pspec(v.r)})"


before7 = None
# capture the tree right after attaching 7 (before rebuilding): insert into a copy without rebuilding
class NoRebuild(PartialRebuild):
    def bad(self, v):
        return False


T2 = NoRebuild(1.5)
for k in [3, 2, 1, 4, 5, 8, 6, 7]:
    T2.insert(k)
T.insert(7)
viol = []
v = T2.root
path = []
while v is not None:
    path.append(v)
    v = v.l if 7 < v.k else (v.r if 7 > v.k else None)
viol = [u.k for u in path if u.h > 1.5 * lg(u.size)]
check("n10-rebuild: before = the BST of 3,2,1,4,5,8,6,7; after = partial rebuilding with alpha = 3/2; the "
      "violators on the path are 3 and 4, and 4 (size 5, height 4 > 1.5 lg 5 = 3.48) is rebuilt",
      ok_pre and mb and ma and mb.group(1) == pspec(T2.root) and ma.group(1) == pspec(T.root)
      and viol == [3, 4] and T.stats["rebuilds"] == 1 and ph(T.root) == 3
      and abs(1.5 * lg(5) - 3.48) < 0.005 and 1.5 * lg(8) == 4.5,
      f"{mb.group(1) if mb else None} | {ma.group(1) if ma else None}")
h = fig("n10-rebuild")
labels = [re.sub(r"<[^>]+>", "", t) for t in re.findall(r"<text[^>]*>(.*?)</text>", h)]
want = {f"h={u.h} s={u.size}" for u in path}
check("n10-rebuild: the h/s labels on the search path are the computed heights and sizes",
      want <= set(labels) and len([x for x in labels if x.startswith("h=")]) == len(path), str(sorted(want)))
h = fig("n10-double")
m = re.search(r'data-zigzag="([^"]*)" data-zigzig="([^"]*)"', h)
check("n10-double: zig-zag = two rotations at x (opposite directions), roller-coaster = parent then x",
      m is not None and m.group(1) == "(z, (w, A, (x, B, C)), D)|(z, (x, (w, A, B), C), D)|(x, (w, A, B), (z, C, D))"
      and m.group(2) == "(z, (y, (x, A, B), C), D)|(y, (x, A, B), (z, C, D))|(x, A, (y, B, (z, C, D)))")
h = fig("n10-rotation")
check("n10-rotation: right rotation at x turns y(x(A,B),C) into x(A,y(B,C))",
      'data-rot="(y, (x, A, B), C)|(x, A, (y, B, C))"' in h)
for nm in ("n10-rotation", "n10-double", "n10-splay", "n10-rebuild"):
    hh = fig(nm)
    check(f"{nm}: inlined on the page and colored only through currentColor / CSS variables",
          f"<!-- fig:{nm} -->\n{hh.strip()}" in page and not re.search(r'(fill|stroke)="#[0-9a-fA-F]{3,6}"', hh))

allal = []
for root_, _, files in os.walk(os.path.join(ROOT, "content")):
    for fn in files:
        if fn.endswith(".md"):
            mm = re.search(r"^aliases: \[(.*)\]$", read(os.path.join(root_, fn)), re.M)
            if mm:
                allal += [a.strip().strip('"').lower() for a in mm.group(1).split(",")]
dups = sorted({a for a in allal if allal.count(a) > 1})
check("aliases are unique site-wide (case-insensitive)", not dups, str(dups))

print()
if FAIL:
    print(f"{len(FAIL)} FAILED:", *FAIL, sep="\n  ")
    sys.exit(1)
print("ALL OK")
