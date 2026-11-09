#!/usr/bin/env python3
"""Figures for Erickson's lecture note 3 (treaps and skip lists). Writes tools/figs/n03-<name>.html; then run
tools/assemble.py on content/4-lecture-notes/03-treaps-and-skip-lists.md. Every tree drawn here is computed from the
(key, priority) pairs by a minimal treap implementation (insert by rotations); every search path is computed by running
SkipListFind on the drawn skip list. tools/checks/n03.py re-checks the same structures independently."""
import os

from figlib import SVG, MONO, SERIF_IT

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")
os.makedirs(OUT, exist_ok=True)


def save(name, html):
    with open(os.path.join(OUT, name + ".html"), "w", encoding="utf-8") as f:
        f.write(html + "\n")
    print("wrote", name)


# ------------------------------------------------------------------ minimal treap
class Node:
    def __init__(self, key, pri):
        self.key, self.pri, self.left, self.right = key, pri, None, None


def build(items):
    if not items:
        return None
    k, p = min(items, key=lambda t: t[1])
    r = Node(k, p)
    r.left = build([t for t in items if t[0] < k])
    r.right = build([t for t in items if t[0] > k])
    return r


def insert_stages(root, key, pri):
    """Textbook insertion at a leaf, then rotations at z while z.pri < parent.pri; returns the list of roots after
    each stage (leaf inserted, after each rotation) as copies, and the rotated (child, parent) pairs."""
    import copy
    z = Node(key, pri)
    path, v = [], root
    while v is not None:
        path.append(v)
        v = v.left if key < v.key else v.right
    if key < path[-1].key:
        path[-1].left = z
    else:
        path[-1].right = z
    stages = [copy.deepcopy(root)]
    while path and z.pri < path[-1].pri:
        p = path.pop()
        g = path[-1] if path else None
        if p.left is z:
            p.left, z.right = z.right, p
        else:
            p.right, z.left = z.left, p
        if g is None:
            root = z
        elif g.left is p:
            g.left = z
        else:
            g.right = z
        stages.append(copy.deepcopy(root))
    return stages


def layout(t, d=0, out=None, order=None):
    """(key -> (inorder rank, depth))"""
    out = {} if out is None else out
    order = [0] if order is None else order
    if t is None:
        return out
    layout(t.left, d + 1, out, order)
    out[t.key] = (order[0], d, t.pri)
    order[0] += 1
    layout(t.right, d + 1, out, order)
    return out


def edges(t):
    if t is None:
        return []
    out = []
    for c in (t.left, t.right):
        if c is not None:
            out.append((t.key, c.key))
            out += edges(c)
    return out


def pri_label(p):
    return "−∞" if p == float("-inf") else ("−" + str(-p) if p < 0 else str(p))


def draw_treap(S, t, x0, y0, dx, dy, r=13, hi=(), hi_edges=(), key_size=14, pri_size=12):
    pos = layout(t)
    P = {k: (x0 + rk * dx, y0 + d * dy) for k, (rk, d, _) in pos.items()}
    for a, b in edges(t):
        (x1, y1), (x2, y2) = P[a], P[b]
        L = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        ux, uy = (x2 - x1) / L, (y2 - y1) / L
        h = (a, b) in hi_edges or (b, a) in hi_edges
        S.line(x1 + ux * r, y1 + uy * r, x2 - ux * r, y2 - uy * r, color="var(--hi)" if h else "currentColor",
               width=2.2 if h else 1.2, opacity=None if h else 0.6)
    for k, (x, y) in P.items():
        col = "var(--hi)" if k in hi else "currentColor"
        S.circle(x, y, r, stroke=col, fill="var(--paper)", width=2.2 if k in hi else 1.4)
        S.text(x, y + 0.5, k, size=key_size, font=MONO, color=col, weight="600" if k in hi else None)
        S.text(x + r * 0.9, y + r * 0.9, pri_label(pos[k][2]), size=pri_size, anchor="start",
               color="var(--hi)" if k in hi else "var(--accent)", halo=True, weight="600")
    return P


EX = [("A", 9), ("G", 7), ("H", 2), ("I", 4), ("L", 8), ("M", 1), ("O", 6), ("R", 5), ("T", 3)]
T0 = build(EX)

# ------------------------------------------------------------------ 1. the example treap and its geometric picture
S = SVG(620, 262)
S.text(150, 14, "the treap", size=13, color="var(--muted)")
draw_treap(S, T0, 26, 46, 31, 50)
# geometric interpretation: x = key rank, y = priority (1 on top)
gx0, gy0, gdx, gdy = 352, 48, 28, 20
keys = [k for k, _ in sorted(EX)]
X = {k: gx0 + i * gdx for i, k in enumerate(keys)}
Y = {p: gy0 + (p - 1) * gdy for p in range(1, 10)}
left_edge, right_edge, bottom = gx0 - 16, gx0 + 8 * gdx + 16, gy0 + 8 * gdy + 14
S.text((left_edge + right_edge) / 2, 14, "the same treap as points (key, priority)", size=13, color="var(--muted)")
S.rect(left_edge, gy0 - 12, right_edge - left_edge, bottom - gy0 + 12, stroke="var(--muted)", width=1)


def tees(t, lo, hi_):
    """Draw the T of node t inside the x-interval [lo, hi_] (pixels)."""
    if t is None:
        return
    x, y = X[t.key], Y[t.pri]
    S.line(lo, y, hi_, y, width=1.3)
    S.line(x, y, x, bottom, width=1.3, opacity=0.55)
    tees(t.left, lo, x)
    tees(t.right, x, hi_)


tees(T0, left_edge, right_edge)
for k, p in EX:
    S.circle(X[k], Y[p], 4.2, stroke="var(--accent)", fill="var(--paper)", width=1.8)
    S.text(X[k] + 6, Y[p] - 7, f"{k}{p}", size=10.5, anchor="start", color="var(--accent)", halo=True)
for k in keys:
    S.text(X[k], bottom + 13, k, size=13, font=MONO)
for p in range(1, 10):
    S.text(left_edge - 9, Y[p], str(p), size=11, color="var(--muted)", anchor="end")
S.text(left_edge - 9, gy0 - 22, "priority", size=11, color="var(--muted)", anchor="end")
html = S.figure(
    "<strong>A treap and its geometric picture (the note’s figures on pp. 1–2).</strong> Left: letters are search keys, "
    "the small numbers are priorities; the keys are in binary-search-tree order and every priority is smaller than its "
    "children’s, so M1, the smallest priority, is the root. Right: each node is the point (key, priority), priority 1 "
    "at the top. The root’s T — a horizontal line through M1 and a vertical line down from it — has nothing above it "
    "and splits the remaining points into the left and right subtrees, which are split the same way.",
    alt="the example treap with keys A G H I L M O R T and priorities 9 7 2 4 8 1 6 5 3, and the same nodes drawn as "
        "points with recursively nested T shapes")
save("n03-treap", html)

# ------------------------------------------------------------------ 2. rotation
S = SVG(560, 190)


def tri(x, y, lab, w=34, h=44):
    S.add(f'<path d="M{x},{y} L{x - w / 2},{y + h} L{x + w / 2},{y + h} Z" fill="var(--accent)" fill-opacity="0.12" '
          f'stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"/>')
    S.text(x, y + h * 0.66, lab, size=14, font=SERIF_IT, italic=True)


def node(x, y, lab, hi=False):
    S.circle(x, y, 14, stroke="var(--hi)" if hi else "currentColor", width=2.2 if hi else 1.5)
    S.text(x, y + 1, lab, size=15, font=SERIF_IT, italic=True, color="var(--hi)" if hi else "currentColor")


def seg(x1, y1, x2, y2):
    import math
    L = math.hypot(x2 - x1, y2 - y1)
    ux, uy = (x2 - x1) / L, (y2 - y1) / L
    S.line(x1 + ux * 14, y1 + uy * 14, x2, y2, width=1.4)


# left tree: y root, x left child (subtrees A, B), C right of y
seg(140, 30, 90, 80); seg(90, 80, 60, 122); seg(90, 80, 120, 122); seg(140, 30, 180, 112)
node(140, 30, "y"); node(90, 80, "x", hi=True)
tri(60, 122, "A"); tri(120, 122, "B"); tri(180, 112, "C")
# right tree: x root, A left, y right child with B, C
seg(420, 30, 380, 112); seg(420, 30, 470, 80); seg(470, 80, 440, 122); seg(470, 80, 500, 122)
node(420, 30, "x", hi=True); node(470, 80, "y")
tri(380, 112, "A"); tri(440, 122, "B"); tri(500, 122, "C")
S.line(238, 70, 318, 70, width=1.6, arrow=True)
S.text(278, 58, "right rotation at x", size=12.5)
S.line(318, 104, 238, 104, width=1.6, arrow=True)
S.text(278, 118, "left rotation at y", size=12.5)
S.text(278, 178, "inorder A x B y C on both sides", size=12.5, color="var(--muted)")
html = S.figure(
    "<strong>A rotation (the note’s figure on p. 3).</strong> A right rotation at <i>x</i> makes <i>x</i> the parent "
    "of its old parent <i>y</i>; subtree <i>B</i> changes sides. The left rotation at <i>y</i> undoes it. Both keep the "
    "inorder sequence, so the search-tree property survives; <i>x</i> moves up a level, <i>y</i> down a level, and "
    "only three pointers change: <i>O</i>(1) time.",
    alt="two binary trees related by a rotation: y over x with subtrees A B C, and x over y with the same subtrees")
save("n03-rotation", html)

# ------------------------------------------------------------------ 3. inserting S with priority -1
stages = insert_stages(build(EX), "S", -1)
assert len(stages) == 4
S = SVG(640, 424)
titles = ["S inserted as a leaf (below R)", "after rotating at S: above R", "after rotating again: above T",
          "after the third rotation: the root"]
offs = [(18, 44), (338, 44), (18, 256), (338, 256)]
prev_par = ["R", "T", "M"]
for i, (t, (ox, oy)) in enumerate(zip(stages, offs)):
    S.text(ox + 140, oy - 26, f"{i}. " + titles[i], size=12.5, color="var(--muted)")
    hl = ()
    if i < 3:
        hl = (("S", prev_par[i]),)
    draw_treap(S, t, ox + 8, oy, 29, 37, r=12, hi=("S",), hi_edges=hl, key_size=13, pri_size=10)
S.line(320, 18, 320, 404, color="var(--muted)", width=1, dash="3 4")
S.line(10, 210, 630, 210, color="var(--muted)", width=1, dash="3 4")
html = S.figure(
    "<strong>Inserting S with priority −1 (the note’s figure on p. 3).</strong> Ordinary BST insertion puts S below "
    "R5 (stage 0); its priority is smaller than its parent’s, so S is rotated up — past R5, past T3, past M1 — until "
    "the heap property holds again: three rotations, the depth of the new leaf. The highlighted edge is the next "
    "rotation. Read backwards, the four trees delete S: rotate it down at the child of smaller priority (M1, then "
    "T3, then R5) until it is a leaf, and cut it off.",
    alt="four treaps: S with priority minus 1 inserted as a leaf, then after one, two and three rotations, when S is "
        "the root")
save("n03-insert", html)

# ------------------------------------------------------------------ 4. skip list search for 5
NEG, POS = float("-inf"), float("inf")
KEYS = list(range(10))
HTS = [1, 3, 0, 1, 0, 0, 2, 4, 0, 1]
L = max(HTS)
levels = []
for l in range(L + 2):
    levels.append([NEG] + [k for k, h in zip(KEYS, HTS) if h >= l] + [POS])


def find(x):
    """SkipListFind on the level lists: returns the path of (key, level) and the looked-at-but-not-entered nodes."""
    l, i = L + 1, 0       # index into levels[l]
    path, crosses = [(NEG, L + 1)], []
    while True:
        key = levels[l][i]
        if key == x:
            break
        nxt = levels[l][i + 1]
        if nxt > x:
            crosses.append((nxt, l))
            if l == 0:
                return path, crosses, False
            l -= 1
            i = levels[l].index(key)
        else:
            i += 1
        path.append((levels[l][i], l))
    return path, crosses, True


path, crosses, found = find(5)
assert found and len(path) - 1 == 9
col = {k: i for i, k in enumerate([NEG] + KEYS + [POS])}
cx0, cdx, ry0, rdy = 34, 47, 22, 34
W, Hh = 26, 20
S = SVG(620, 212)


def pos(key, l):
    return cx0 + col[key] * cdx, ry0 + (L + 1 - l) * rdy


onpath = set(path)
pedges = set(zip(path, path[1:]))
for l, row in enumerate(levels):
    for a, b in zip(row, row[1:]):
        (x1, y1), (x2, y2) = pos(a, l), pos(b, l)
        hi = ((a, l), (b, l)) in pedges
        S.line(x1 + W / 2, y1, x2 - W / 2 - 1, y2, color="var(--hi)" if hi else "currentColor",
               width=2.4 if hi else 1.1, arrow=True, opacity=None if hi else 0.7)
    if l > 0:
        for k in row:
            (x1, y1), (x2, y2) = pos(k, l), pos(k, l - 1)
            hi = ((k, l), (k, l - 1)) in pedges
            S.line(x1, y1 + Hh / 2, x2, y2 - Hh / 2 - 1, color="var(--hi)" if hi else "currentColor",
                   width=2.4 if hi else 1.0, arrow=True, opacity=None if hi else 0.55)
crossset = set(crosses)
for l, row in enumerate(levels):
    for k in row:
        x, y = pos(k, l)
        lab = "−∞" if k == NEG else ("∞" if k == POS else str(k))
        if (k, l) in onpath:
            S.rect(x - W / 2, y - Hh / 2, W, Hh, rx=3, stroke="var(--hi)", fill="var(--hi)", fill_opacity=0.12,
                   width=2.0)
            S.text(x, y + 0.5, lab, size=12.5, font=MONO, color="var(--hi)", weight="600")
        elif (k, l) in crossset:
            S.rect(x - W / 2, y - Hh / 2, W, Hh, rx=3, stroke="var(--hi)", fill="var(--paper)", width=1.4, dash="3 2")
            S.text(x, y + 0.5, lab, size=12.5, font=MONO)
        else:
            S.rect(x - W / 2, y - Hh / 2, W, Hh, rx=3, stroke="currentColor", fill="var(--paper)", width=1.1)
            S.text(x, y + 0.5, lab, size=12.5, font=MONO)
for l in range(L + 2):
    S.text(8, pos(NEG, l)[1], str(l), size=11, color="var(--muted)")
html = S.figure(
    "<strong>Searching for 5 in a skip list (the note’s figures on pp. 7–8).</strong> Level 0 (bottom) holds all ten "
    "keys; each key is copied up once per coin flip that came up heads (7 has four copies above the bottom, so "
    "<i>L</i> = 4), and the top level holds only the sentinels. SkipListFind starts at the top-left −∞ and moves right "
    "unless the next key exceeds 5, otherwise down: 9 moves (5 down, 4 right), ending at 5 on level 0. The dashed "
    "boxes are the nodes it looks at but does not enter — ∞, 7, 7, 6, 6.",
    alt="a six-level skip list on keys 0 to 9 with the search path for 5 highlighted")
save("n03-skiplist", html)
