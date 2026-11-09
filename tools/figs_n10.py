#!/usr/bin/env python3
"""Figures for lecture note 10 (Scapegoat and splay trees). Writes tools/figs/n10-<name>.html; then run
tools/assemble.py on content/4-lecture-notes/10-scapegoat-and-splay-trees.md. The trees drawn are computed here by
minimal re-implementations (BST insertion, partial rebuilding, rotations, splaying); tools/checks/n10.py recomputes
them independently and compares them with the data-* attributes and labels in the HTML."""
import math
import os

from figlib import SVG, SERIF_IT, MONO

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")
os.makedirs(OUT, exist_ok=True)


def save(name, html):
    with open(os.path.join(OUT, name + ".html"), "w", encoding="utf-8") as f:
        f.write(html + "\n")
    print("wrote", name)


# ------------------------------------------------------------------ tiny BST toolkit (tuples: (key, left, right))
def ins(t, k):
    if t is None:
        return (k, None, None)
    key, L, R = t
    return (key, ins(L, k), R) if k < key else (key, L, ins(R, k))


def keys(t):
    return [] if t is None else keys(t[1]) + [t[0]] + keys(t[2])


def size(t):
    return 0 if t is None else 1 + size(t[1]) + size(t[2])


def height(t):
    return -1 if t is None else 1 + max(height(t[1]), height(t[2]))


def balanced(ks):
    if not ks:
        return None
    m = len(ks) // 2
    return (ks[m], balanced(ks[:m]), balanced(ks[m + 1:]))


def find_path(t, k):
    path = []
    while t is not None:
        path.append(t)
        if k == t[0]:
            break
        t = t[1] if k < t[0] else t[2]
    return path


def draw_bst(S, t, x0, y0, dx, dy, r=9, hi=(), hi2=(), labels=None, font_size=12, ann=None):
    """Draw tree t with x by inorder rank, y by depth. hi: keys drawn in var(--hi); hi2: keys filled with accent.
    ann: dict key -> (text, side) annotation. Returns positions."""
    order = keys(t)
    pos = {}

    def walk(u, d):
        if u is None:
            return
        pos[u[0]] = (x0 + order.index(u[0]) * dx, y0 + d * dy)
        walk(u[1], d + 1)
        walk(u[2], d + 1)

    walk(t, 0)

    def edges(u):
        if u is None:
            return
        for c in (u[1], u[2]):
            if c is not None:
                (x1, y1), (x2, y2) = pos[u[0]], pos[c[0]]
                L = math.hypot(x2 - x1, y2 - y1)
                ux, uy = (x2 - x1) / L, (y2 - y1) / L
                S.line(x1 + ux * r, y1 + uy * r, x2 - ux * r, y2 - uy * r, width=1.2)
                edges(c)

    edges(t)
    for k, (x, y) in pos.items():
        col = "var(--hi)" if k in hi else "currentColor"
        fill = "var(--accent)" if k in hi2 else "var(--paper)"
        S.add(f'<circle data-node="{k}" cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" '
              f'{"fill-opacity=" + chr(34) + "0.25" + chr(34) + " " if k in hi2 else ""}'
              f'stroke="{col}" stroke-width="{2.2 if k in hi else 1.3}"/>')
        S.text(x, y + 0.5, (labels or {}).get(k, str(k)), size=font_size, color=col, font=SERIF_IT, italic=True,
               weight="bold" if k in hi else None)
        if ann and k in ann:
            txt, side = ann[k]
            S.text(x + (r + 5) * (1 if side > 0 else -1), y, txt, size=10.5, anchor="start" if side > 0 else "end",
                   color="var(--muted)", font=MONO, halo=True)
    return pos


def shape_attr(t):
    """Serialize a tree as nested parentheses of keys: k(L,R)."""
    if t is None:
        return "-"
    return f"{t[0]}({shape_attr(t[1])},{shape_attr(t[2])})"


# ------------------------------------------------------------------ partial rebuilding example (alpha = 3/2)
ALPHA = 1.5
order = [3, 2, 1, 4, 5, 8, 6]
t = None
for k in order:
    t = ins(t, k)
    # no node violates height <= alpha lg size before the last insertion
    def ok(u):
        return u is None or (height(u) <= ALPHA * math.log2(size(u)) and ok(u[1]) and ok(u[2]))
    assert ok(t)
before = t
after_ins = ins(before, 7)
path = find_path(after_ins, 7)
viol = [u[0] for u in path if height(u) > ALPHA * math.log2(size(u))]
assert viol == [3, 4], viol          # the root and 4 violate; 4 is the lowest
scape = [u for u in path if u[0] == 4][0]
rebuilt_sub = balanced(keys(scape))


def replace(u, k, new):
    if u is None:
        return None
    if u[0] == k:
        return new
    return (u[0], replace(u[1], k, new), replace(u[2], k, new))


after = replace(after_ins, 4, rebuilt_sub)
assert keys(after) == list(range(1, 9)) and height(after) == 3
assert all(height(u) <= ALPHA * math.log2(size(u)) for u in [after] + [x for x in find_path(after, 7)])

S = SVG(600, 222, font_size=12)
ann = {u[0]: (f"h={height(u)} s={size(u)}", 1) for u in path}
draw_bst(S, after_ins, 40, 40, 30, 32, r=10, hi=(4,), hi2=(7,), ann=ann)
S.text(140, 14, "after inserting 7", size=12, color="var(--muted)")
S.line(328, 100, 362, 100, arrow=True, width=1.6)
S.text(345, 86, "rebuild", size=11, color="var(--muted)")
draw_bst(S, after, 385, 40, 27, 32, r=10, hi=(6,))
S.text(480, 14, "after rebuilding the subtree of 4", size=12, color="var(--muted)")
S.add(f'<g data-before="{shape_attr(after_ins)}" data-after="{shape_attr(after)}"></g>')
cap = ("<strong>Partial rebuilding with α = 3/2.</strong> Keys 3, 2, 1, 4, 5, 8, 6 were inserted with no violation; "
       "inserting 7 makes the search path 3, 4, 5, 8, 6, 7 (heights h and sizes s shown). Walking back up, node 4 is "
       "the first with height(<i>v</i>) &gt; α lg size(<i>v</i>): 4 &gt; 1.5 lg 5 ≈ 3.48 (the root also violates, "
       "5 &gt; 1.5 lg 8 = 4.5). Rebuilding the five keys under 4 into a perfectly balanced subtree also brings the "
       "root back to height 3.")
save("n10-rebuild", S.figure(cap, alt="A binary search tree before and after rebuilding the subtree of a scapegoat"))


# ------------------------------------------------------------------ rotations (subtrees as triangles)
def tri(S, x, y, label, w=24, h=26):
    S.path(f"M{x:.1f},{y:.1f} L{x - w / 2:.1f},{y + h:.1f} L{x + w / 2:.1f},{y + h:.1f} Z", width=1.2)
    S.text(x, y + h * 0.66, label, size=12, font=SERIF_IT, italic=True)


def node(S, x, y, label, r=11, hot=False):
    S.circle(x, y, r, stroke="var(--hi)" if hot else "currentColor", width=2 if hot else 1.4)
    S.text(x, y + 0.5, label, size=13, font=SERIF_IT, italic=True, color="var(--hi)" if hot else "currentColor")


def edge(S, x1, y1, x2, y2, r1=11, r2=0):
    L = math.hypot(x2 - x1, y2 - y1)
    ux, uy = (x2 - x1) / L, (y2 - y1) / L
    S.line(x1 + ux * r1, y1 + uy * r1, x2 - ux * r2, y2 - uy * r2, width=1.2)


def draw_spec(S, spec, x, y, dx, dy=38, hot="x"):
    """spec: ('name', left, right) for a node or 'A' for a subtree triangle. Layout: x by in-order rank (spacing dx,
    leftmost item at x), y by depth."""
    order = inorder_spec(spec)
    pos = {}

    def place(s, d):
        key = s if isinstance(s, str) else s[0]
        pos[key] = (x + order.index(key) * dx, y + d * dy)
        if not isinstance(s, str):
            place(s[1], d + 1)
            place(s[2], d + 1)

    place(spec, 0)

    def draw(s):
        if isinstance(s, str):
            tri(S, pos[s][0], pos[s][1] - 4, s)
            return
        px, py = pos[s[0]]
        for c in (s[1], s[2]):
            ck = c if isinstance(c, str) else c[0]
            cx, cy = pos[ck]
            edge(S, px, py, cx, cy, 11, 0 if isinstance(c, str) else 11)
            draw(c)
        node(S, px, py, s[0], hot=(s[0] == hot))

    draw(spec)


def inorder_spec(s):
    return [s] if isinstance(s, str) else inorder_spec(s[1]) + [s[0]] + inorder_spec(s[2])


def rot_right(s):        # rotate at the left child x of the root y
    y, (x, A, B), C = s
    return (x, A, (y, B, C))


def rot_left(s):         # rotate at the right child of the root
    x, A, (y, B, C) = s
    return (y, (x, A, B), C)


left_t = ("y", ("x", "A", "B"), "C")
right_t = rot_right(left_t)
assert right_t == ("x", "A", ("y", "B", "C")) and rot_left(right_t) == left_t
assert inorder_spec(left_t) == inorder_spec(right_t) == ["A", "x", "B", "y", "C"]
S = SVG(470, 150, font_size=12)
draw_spec(S, left_t, 30, 28, 32)
draw_spec(S, right_t, 312, 28, 32)
S.line(200, 70, 270, 70, arrow=True)
S.line(270, 88, 200, 88, arrow=True)
S.text(235, 58, "right rotation at x", size=11, color="var(--muted)")
S.text(235, 102, "left rotation at y", size=11, color="var(--muted)")
S.add(f'<g data-rot="{left_t}|{right_t}"></g>'.replace("'", ""))
cap = ("<strong>A single rotation.</strong> A right rotation at <i>x</i> (left) makes <i>x</i> the parent of its old "
       "parent <i>y</i>; the left rotation at <i>y</i> undoes it. Subtree <i>B</i> changes parent; the in-order "
       "sequence <i>A x B y C</i> is unchanged, <i>x</i> moves up one level and <i>y</i> down one. Only "
       "<i>x</i> and <i>y</i> change size.")
save("n10-rotation", S.figure(cap, alt="Right and left rotation between nodes x and y with subtrees A, B, C"))

# double rotations
zz0 = ("z", ("w", "A", ("x", "B", "C")), "D")                 # zig-zag at x
zz1 = ("z", rot_left(zz0[1]), "D")                             # rotate at x (left)
zz2 = rot_right(zz1)                                           # rotate at x again (right)
assert zz2 == ("x", ("w", "A", "B"), ("z", "C", "D"))
rc0 = ("z", ("y", ("x", "A", "B"), "C"), "D")                  # roller-coaster at x
rc1 = rot_right(rc0)                                           # rotate at y (parent) first
rc2 = ("y", None, None)
rc2 = (rc1[0], rot_right(rc1[1]), rc1[2]) if False else None
# rotate at x: x is now the left child of the root y
rc2 = rot_right(rc1)
assert rc1 == ("y", ("x", "A", "B"), ("z", "C", "D")) and rc2 == ("x", "A", ("y", "B", ("z", "C", "D")))
for a, b in ((zz0, zz2), (rc0, rc2)):
    assert inorder_spec(a) == inorder_spec(b)
S = SVG(640, 384, font_size=12)
S.text(14, 16, "zig-zag at x", size=12, color="var(--muted)", anchor="start")
draw_spec(S, zz0, 18, 44, 27)
S.line(194, 95, 228, 95, arrow=True)
draw_spec(S, zz1, 242, 44, 27)
S.line(418, 95, 452, 95, arrow=True)
draw_spec(S, zz2, 466, 44, 27)
S.text(14, 206, "roller-coaster (zig-zig) at x", size=12, color="var(--muted)", anchor="start")
draw_spec(S, rc0, 18, 234, 27)
S.line(194, 285, 228, 285, arrow=True)
draw_spec(S, rc1, 242, 234, 27)
S.line(418, 285, 452, 285, arrow=True)
draw_spec(S, rc2, 466, 234, 27)
S.add(f'<g data-zigzag="{zz0}|{zz1}|{zz2}" data-zigzig="{rc0}|{rc1}|{rc2}"></g>'.replace("'", ""))
cap = ("<strong>The two double rotations.</strong> Top: a <em>zig-zag</em> at <i>x</i> (its parent <i>w</i> and "
       "grandparent <i>z</i> on opposite sides) is two rotations at <i>x</i>, in opposite directions; <i>x</i> rises "
       "two levels, <i>w</i> stays at its depth, <i>z</i> drops one. Bottom: a <em>roller-coaster</em> or zig-zig "
       "(both links on the same side) rotates first at the parent <i>y</i>, then at <i>x</i>; <i>x</i> rises two "
       "levels, <i>y</i> stays, <i>z</i> drops two. Mirror images are not shown.")
save("n10-double", S.figure(cap, alt="Zig-zag and roller-coaster double rotations"))


# ------------------------------------------------------------------ the note's Figure 4: splaying x
class Nd:
    def __init__(self, k):
        self.k, self.l, self.r, self.p = k, None, None, None


def from_tuple(t, p=None):
    if t is None:
        return None
    v = Nd(t[0])
    v.p = p
    v.l, v.r = from_tuple(t[1], v), from_tuple(t[2], v)
    return v


def to_tuple(v):
    return None if v is None else (v.k, to_tuple(v.l), to_tuple(v.r))


def rotate(x):
    y, z = x.p, x.p.p
    if y.l is x:
        y.l, x.r = x.r, y
        if y.l:
            y.l.p = y
    else:
        y.r, x.l = x.l, y
        if y.r:
            y.r.p = y
    y.p, x.p = x, z
    if z:
        if z.l is y:
            z.l = x
        else:
            z.r = x


def root(v):
    while v.p:
        v = v.p
    return v


ORDER = list("abcdefghij") + ["x"] + list("klmn")     # in-order key order: x lies between j and k
RANK = {c: i for i, c in enumerate(ORDER)}


def T(k, L=None, R=None):
    return (RANK[k], L, R)


fig4 = T("b", T("a"), T("d", T("c"), T("m", T("k", T("f", T("e"), T("h", T("g"), T("j", T("i"), T("x")))), T("l")),
                                            T("n"))))
assert keys(fig4) == list(range(15))
r = from_tuple(fig4)
nodes = {}


def collect(v):
    if v:
        nodes[v.k] = v
        collect(v.l)
        collect(v.r)


collect(r)
x = nodes[RANK["x"]]
stages = [to_tuple(r)]
kinds = []
while x.p:
    y, z = x.p, x.p.p
    if z is None:
        rotate(x)
        kinds.append("single")
    elif (z.l is y) == (y.l is x):
        rotate(y)
        rotate(x)
        kinds.append("roller-coaster")
    else:
        rotate(x)
        rotate(x)
        kinds.append("zig-zag")
    stages.append(to_tuple(root(x)))
assert kinds == ["roller-coaster", "zig-zag", "zig-zag", "single"]
LAB = {i: c for c, i in RANK.items()}
S = SVG(640, 470, font_size=11)
spots = [(16, 34), (226, 34), (436, 34), (110, 270), (380, 270)]
titles = ["start: x at depth 7", "after a roller-coaster", "after a zig-zag", "after a second zig-zag",
          "after a single rotation"]
for (sx, sy), st, title in zip(spots, stages, titles):
    draw_bst(S, st, sx + 9, sy + 14, 12.6, 24, r=8.5, hi=(RANK["x"],), labels=LAB, font_size=11.5)
    S.text(sx + 95, sy - 12, title, size=11, color="var(--muted)")
S.add(f'<g data-stages="{"|".join(shape_attr(s) for s in stages)}"></g>')
cap = ("<strong>Splaying a node (the note's Figure 4).</strong> The keys are in alphabetical order except that "
       "<i>x</i> lies between <i>j</i> and <i>k</i>. Node <i>x</i> starts at depth 7: a roller-coaster (parent "
       "<i>j</i> and grandparent <i>h</i> on the same side), two zig-zags and a final single rotation — 7 "
       "rotations — bring it to the root. On the old search path, <i>b</i> and <i>d</i> move down one level, "
       "<i>h</i> stays at depth 5, and <i>j</i>, <i>f</i>, <i>k</i>, <i>m</i> move up (<i>j</i> from depth 6 to 4).")
save("n10-splay", S.figure(cap, alt="Five stages of splaying node x to the root"))
