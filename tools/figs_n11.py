#!/usr/bin/env python3
"""Figures for lecture note 11 (Disjoint sets). Writes tools/figs/n11-<name>.html; then run tools/assemble.py on
content/4-lecture-notes/11-disjoint-sets.md. The forests drawn here are produced by running the page's union-by-rank
Union, path-compressing Find and threaded WeightedUnion on the named elements; the drawing reads the resulting
parent / leader / next pointers and ranks."""
import os

from figlib import SVG, SERIF_IT, SANS, fmt

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")
os.makedirs(OUT, exist_ok=True)


def save(name, html):
    with open(os.path.join(OUT, name + ".html"), "w", encoding="utf-8") as f:
        f.write(html + "\n")
    print("wrote", name)


# ------------------------------------------------------------------ the page's structures
class RankForest:
    def __init__(self, names):
        self.parent = {v: v for v in names}
        self.rank = {v: 0 for v in names}

    def find(self, x):
        if x != self.parent[x]:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def link(self, x, y):  # Union on two leaders, union by rank, as on the page
        if self.rank[x] > self.rank[y]:
            self.parent[y] = x
        else:
            self.parent[x] = y
            if self.rank[x] == self.rank[y]:
                self.rank[y] += 1

    def union(self, x, y):
        xb, yb = self.find(x), self.find(y)
        if xb != yb:
            self.link(xb, yb)


R_ = 13


def node(S, x, y, name, hi=False, rank=None, rank_side="right"):
    col = "var(--hi)" if hi else "currentColor"
    S.circle(x, y, R_, stroke=col, fill="var(--paper)", width=2.2 if hi else 1.5)
    S.text(x, y + 1, name, size=15, font=SERIF_IT, italic=True, color=col)
    if rank is not None:
        dx = R_ + 9 if rank_side == "right" else -(R_ + 9)
        S.text(x + dx, y - 9, str(rank), size=11.5, color="var(--muted)")


def up_arrow(S, a, b, hi=False, dash=None, width=None):
    """Arrow from child at a to parent at b (centres)."""
    import math
    (x1, y1), (x2, y2) = a, b
    L = math.hypot(x2 - x1, y2 - y1)
    ux, uy = (x2 - x1) / L, (y2 - y1) / L
    S.line(x1 + ux * R_, y1 + uy * R_, x2 - ux * (R_ + 2.5), y2 - uy * (R_ + 2.5),
           color="var(--hi)" if hi else "currentColor", width=width or (2.2 if hi else 1.4), arrow=True, dash=dash)


def root_loop(S, x, y):
    S.path(f"M{fmt(x - 5)},{fmt(y - R_ + 1)} C{fmt(x - 14)},{fmt(y - R_ - 20)} {fmt(x + 14)},{fmt(y - R_ - 20)} "
           f"{fmt(x + 5.5)},{fmt(y - R_ - 1.5)}", width=1.3, arrow=True)


def draw_forest(S, F, pos, hi=(), ranks=True, rank_side=None):
    for v, (x, y) in pos.items():
        p = F.parent[v]
        if p == v:
            root_loop(S, x, y)
        else:
            up_arrow(S, (x, y), pos[p], hi=v in hi)
    for v, (x, y) in pos.items():
        node(S, x, y, v, hi=v in hi, rank=F.rank[v] if ranks else None,
             rank_side=(rank_side or {}).get(v, "right"))


def big_arrow(S, x, y):
    S.path(f"M{x},{y - 7} L{x + 22},{y - 7} L{x + 22},{y - 13} L{x + 36},{y} L{x + 22},{y + 13} L{x + 22},{y + 7} "
           f"L{x},{y + 7} z", color="var(--muted)", width=1.2, fill="var(--muted)")


# ================================================================== 1. union by rank
F = RankForest("abcdpqr")
F.union("c", "b")      # b over c, rank(b) = 1
F.union("d", "a")      # a over d, rank(a) = 1
F.union("b", "a")      # equal ranks: b goes under a, rank(a) = 2
F.union("q", "p")
F.union("r", "p")      # p over q, r, rank(p) = 1
assert F.parent == {"a": "a", "b": "a", "c": "b", "d": "a", "p": "p", "q": "p", "r": "p"}
assert F.rank == {"a": 2, "b": 1, "c": 0, "d": 0, "p": 1, "q": 0, "r": 0}
S = SVG(600, 205)
before = {"a": (75, 52), "b": (45, 112), "d": (105, 112), "c": (45, 172),
          "p": (215, 52), "q": (185, 112), "r": (245, 112)}
draw_forest(S, F, before)
S.text(150, 14, "before: rank(a) = 2, rank(p) = 1", size=12.5)
big_arrow(S, 288, 100)
old = dict(F.parent)
F.union("b", "q")      # Find(b) = a, Find(q) = p (no pointer changes): rank(a) > rank(p), so parent(p) <- a
assert F.parent["p"] == "a" and F.rank["a"] == 2
assert {v for v in F.parent if F.parent[v] != old[v]} == {"p"}
after = {"a": (455, 52), "b": (385, 112), "d": (445, 112), "p": (520, 112), "c": (385, 172),
         "q": (495, 172), "r": (550, 172)}
draw_forest(S, F, after, hi={"p"})
S.text(465, 14, "after Union(b, q): parent(p) ← a", size=12.5)
save("n11-union-by-rank", S.figure(
    "<strong>Union by rank.</strong> Arrows point to parents; the small grey numbers are ranks. Union(<i>b</i>, <i>q</i>) "
    "first finds the leaders <i>a</i> (rank 2) and <i>p</i> (rank 1) and makes the leader of smaller rank, <i>p</i>, a "
    "child of the other; no rank changes, because the ranks differ. Linking the other way would have made the tree "
    "deeper.", alt="two up-trees with ranks; union by rank makes the root p of rank 1 a child of the root a of rank 2"))

# ================================================================== 2. path compression
# the note's example (p. 4): p is the root; a, q, r its children; b, d children of a; c a child of b
F = RankForest("pqrabdc")
F.parent.update({"a": "p", "q": "p", "r": "p", "b": "a", "d": "a", "c": "b"})
S = SVG(600, 225)
before = {"p": (110, 50), "a": (60, 108), "q": (115, 108), "r": (165, 108), "b": (40, 160), "d": (85, 166),
          "c": (20, 206)}
draw_forest(S, F, before, ranks=False)
S.text(110, 14, "before Find(c)", size=12.5)
big_arrow(S, 255, 110)
old = dict(F.parent)
F.find("c")
changed = {v for v in F.parent if F.parent[v] != old[v]}
assert changed == {"c", "b"} and F.parent["c"] == F.parent["b"] == "p" and F.parent["a"] == "p"
after = {"p": (450, 50), "c": (345, 120), "b": (397, 120), "a": (450, 120), "q": (503, 120), "r": (555, 120),
         "d": (450, 185)}
draw_forest(S, F, after, hi=changed, ranks=False)
S.text(450, 14, "after: every node on the path points to p", size=12.5)
save("n11-path-compression", S.figure(
    "<strong>Path compression during Find(<i>c</i>).</strong> Find walks <i>c</i> → <i>b</i> → <i>a</i> → <i>p</i>, "
    "and on the way back down the recursion makes every node on that path a child of the root. The shaded nodes "
    "<i>c</i> and <i>b</i> get a new parent (<i>a</i> already pointed to <i>p</i>); the next Find on any of them "
    "takes one step. Ranks are not changed, so they no longer equal the heights (the note’s figure on p. 4).",
    alt="path compression: before, c is at depth 3 below p; after Find(c), c and b are children of p"))


# ================================================================== 3. threaded trees, WeightedUnion
class Threads:
    def __init__(self):
        self.leader, self.next, self.size = {}, {}, {}

    def make(self, x):
        self.leader[x], self.next[x], self.size[x] = x, None, 1

    def union(self, x, y):  # relabel the set of y; splice its thread after x's leader
        xb, yb = self.leader[x], self.leader[y]
        y = yb
        self.leader[y] = xb
        while self.next[y] is not None:
            y = self.next[y]
            self.leader[y] = xb
        self.next[y] = self.next[xb]
        self.next[xb] = yb

    def wunion(self, x, y):
        xb, yb = self.leader[x], self.leader[y]
        if self.size[xb] > self.size[yb]:
            self.union(xb, yb)
            self.size[xb] += self.size[yb]
        else:
            self.union(yb, xb)
            self.size[yb] = self.size[xb] + self.size[yb]

    def thread(self, l):
        out = [l]
        while self.next[out[-1]] is not None:
            out.append(self.next[out[-1]])
        return out


T = Threads()
for v in "abcdpqr":
    T.make(v)
for v in "dcb":
    T.wunion(v, "a")   # on a tie the second argument's leader stays leader
for v in "rq":
    T.wunion(v, "p")
assert T.thread("a") == list("abcd") and T.thread("p") == list("pqr")


def draw_threads(S, T, y0, x0, gap, hi=()):
    import math
    leaders = [l for l in T.leader if T.leader[l] == l]
    pos = {}
    x = x0
    for l in sorted(leaders):
        th = T.thread(l)
        members = th[1:]
        width = (len(members) - 1) * gap
        lx = x + width / 2
        pos[l] = (lx, y0)
        for k, v in enumerate(members):
            pos[v] = (x + k * gap, y0 + 62)
        x += width + 2.2 * gap
    for l in sorted(leaders):
        th = T.thread(l)
        lx, ly = pos[l]
        root_loop(S, lx, ly)
        for v in th[1:]:
            up_arrow(S, pos[v], pos[l], hi=v in hi)
        # thread: leader -> first member -> ... (dashed, muted, below the row)
        for u, v in zip(th, th[1:]):
            (x1, y1), (x2, y2) = pos[u], pos[v]
            if u == l:
                # from the leader's left side down to the first member's left side
                S.path(f"M{fmt(x1 - R_)},{fmt(y1 + 3)} Q{fmt(x2 - R_ - 22)},{fmt(y1 + 10)} {fmt(x2 - R_ - 2)},"
                       f"{fmt(y2 - 2)}", color="var(--accent)", width=1.3, arrow=True, dash="4 3")
            else:
                S.line(x1 + R_, y1, x2 - R_ - 2.5, y2, color="var(--accent)", width=1.3, arrow=True, dash="4 3")
    for v, (x, y) in pos.items():
        node(S, x, y, v, hi=v in hi)
    return pos


S = SVG(600, 292)
S.text(16, 13, "before: two sets, leaders a (size 4) and p (size 3)", size=12.5, anchor="start")
draw_threads(S, T, 58, 40, 46)
T.wunion("b", "q")
assert T.thread("a") == list("apqrbcd") and all(T.leader[v] == "a" for v in "abcdpqr")
S.text(16, 160, "after WeightedUnion(b, q): the smaller set takes leader a; its thread is spliced in after a",
       size=12.5, anchor="start")
draw_threads(S, T, 205, 160, 46, hi=set("pqr"))
save("n11-threaded", S.figure(
    "<strong>Threaded trees and WeightedUnion.</strong> Solid arrows point to the leader; dashed arrows form the "
    "thread, a linked list from the leader through its set, ending in Null. WeightedUnion relabels the "
    "<em>smaller</em> set — <i>p</i>, <i>q</i>, <i>r</i>, shaded — walking its thread (3 leader updates), and "
    "splices that thread in right after <i>a</i> in O(1) time: <i>a</i> → <i>p</i> → <i>q</i> → <i>r</i> → "
    "<i>b</i> → <i>c</i> → <i>d</i>.",
    alt="two threaded trees; after WeightedUnion the three members of the smaller set point to leader a"))
