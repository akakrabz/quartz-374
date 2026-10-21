#!/usr/bin/env python3
"""Figures for the Chapter 6 exercises page (Erickson, Algorithms). Writes tools/figs/a06x-<name>.html; then run
tools/assemble.py on content/2-algorithms/06-depth-first-search-exercises.md. Every number drawn here is computed
by running the page's algorithm (the sweep of Exercise 6.3, CutDFS/BridgeDFS of 6.4-6.5, Tarry2 of 6.8);
tools/checks/a06x.py re-derives the same facts independently."""
import math
import os
from figlib import SVG, SERIF_IT, SANS, MONO

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")
os.makedirs(OUT, exist_ok=True)


def save(name, html):
    with open(os.path.join(OUT, name + ".html"), "w", encoding="utf-8") as f:
        f.write(html + "\n")
    print("wrote", name)


def vertex(S, x, y, name, r=12, stroke="currentColor", fill="var(--paper)", width=1.5, fill_opacity=None, size=15):
    S.circle(x, y, r, stroke=stroke, fill=fill, width=width, fill_opacity=fill_opacity)
    S.text(x, y + 1, name, size=size, font=SERIF_IT, italic=True)


def seg(S, p, q, r1, r2, **kw):
    (x1, y1), (x2, y2) = p, q
    L = math.hypot(x2 - x1, y2 - y1)
    ux, uy = (x2 - x1) / L, (y2 - y1) / L
    S.line(x1 + ux * r1, y1 + uy * r1, x2 - ux * (r2 + (2.5 if kw.get("arrow") else 0)),
           y2 - uy * (r2 + (2.5 if kw.get("arrow") else 0)), **kw)


# =========================================================================== 1. (s,t)-cut vertices by a sweep
F20_E = ["s f", "s g", "f g", "g a", "g b", "g h", "g c", "a b", "a c", "a h", "b h", "b c", "h c",
         "c d", "c i", "c j", "d i", "d j", "i j", "j e", "j t", "e t"]
E20 = [tuple(e.split()) for e in F20_E]
ORDER = "s f g a b h c d i j e t".split()
pos = {v: i + 1 for i, v in enumerate(ORDER)}
assert all(pos[u] < pos[v] for u, v in E20)
adj = {v: [w for u, w in E20 if u == v] for v in ORDER}
# the page's sweep
far, cuts = 1, []
for i in range(1, len(ORDER) + 1):
    if 1 < i < len(ORDER) and far <= i:
        cuts.append(ORDER[i - 1])
    for w in adj[ORDER[i - 1]]:
        far = max(far, pos[w])
assert cuts == ["g", "c", "j"]
DX, X0, Y0 = 53, 26, 104
S = SVG(636, 160)
X = lambda v: X0 + (pos[v] - 1) * DX
for u, v in E20:
    span = pos[v] - pos[u]
    if span == 1:
        seg(S, (X(u), Y0), (X(v), Y0), 12, 12, arrow=True, width=1.5)
    else:
        h = 20 + 22 * (span - 1)
        x1, x2 = X(u), X(v)
        a = math.radians(62)
        sx, sy = x1 + 12 * math.cos(a), Y0 - 12 * math.sin(a)
        ex, ey = x2 - 14.5 * math.cos(a), Y0 - 14.5 * math.sin(a)
        S.path(f"M{sx:.1f},{sy:.1f} C{x1 + 0.2 * (x2 - x1):.1f},{Y0 - h * 1.3:.1f} "
               f"{x2 - 0.2 * (x2 - x1):.1f},{Y0 - h * 1.3:.1f} {ex:.1f},{ey:.1f}",
               arrow=True, width=1.3, color="var(--accent)")
for v in ORDER:
    if v in cuts:
        vertex(S, X(v), Y0, v, stroke="var(--hi)", fill="var(--hi)", fill_opacity=0.28, width=2.2)
    else:
        vertex(S, X(v), Y0, v)
    S.text(X(v), Y0 + 26, str(pos[v]), size=12, color="var(--muted)")
S.text(X0 + 5.5 * DX, 150, "position in the topological order", size=12, color="var(--muted)")
save("a06x-cut-dag", S.figure(
    "<strong>Cut vertices are the ones no edge jumps over.</strong> The dag of the book's Figure 6.20, drawn in "
    "the topological order <i>s f g a b h c d i j e t</i>. Eleven edges join consecutive vertices (black); the "
    "other eleven (blue arcs) jump over every vertex strictly between their endpoints. Only <i>g</i>, <i>c</i> and "
    "<i>j</i> lie under no arc, so they are the (<i>s</i>, <i>t</i>)-cut vertices, as in the book.",
    alt="twelve vertices on a line with eleven arcs above; three vertices are not covered by any arc"))

# =========================================================================== 2. low numbers on Figure 6.21
POS21 = {"a": (40, 70), "b": (40, 180), "c": (145, 70), "d": (145, 180), "e": (250, 70), "f": (250, 180),
         "g": (355, 125), "h": (355, 238), "i": (440, 58), "j": (440, 192), "k": (520, 125), "l": (600, 58),
         "m": (600, 192)}
E21 = ["a b", "a d", "b d", "c e", "c d", "c f", "c g", "e d", "e f", "e g", "d f", "d g", "f g", "f h",
       "g i", "g j", "g k", "i j", "i k", "j k", "k l", "k m", "l m"]
E21 = [tuple(e.split()) for e in E21]
V21 = sorted(POS21)
ADJ21 = {v: sorted([w for u, w in E21 if u == v] + [u for u, w in E21 if w == v]) for v in V21}
pre, low, parent, children = {}, {}, {}, {v: [] for v in V21}
cut21, bridges21 = set(), set()
clock = [0]


def CutDFS(v, p):
    parent[v] = p
    clock[0] += 1
    pre[v] = low[v] = clock[0]
    for w in ADJ21[v]:
        if w not in pre:
            children[v].append(w)
            CutDFS(w, v)
            low[v] = min(low[v], low[w])
            if p is not None and low[w] >= pre[v]:
                cut21.add(v)
            if low[w] == pre[w]:
                bridges21.add((v, w))
        elif w != p:
            low[v] = min(low[v], pre[w])


CutDFS("a", None)
if len(children["a"]) >= 2:
    cut21.add("a")
assert cut21 == {"d", "f", "g", "k"} and bridges21 == {("f", "h")}
S = SVG(650, 272)
tree = {(parent[v], v) for v in V21 if parent[v] is not None}
for u, w in E21:
    p, q = POS21[u], POS21[w]
    if (u, w) in tree or (w, u) in tree:
        hi = (u, w) in bridges21 or (w, u) in bridges21
        seg(S, p, q, 12, 12, width=3.0 if not hi else 3.4, color="var(--hi)" if hi else "var(--accent)")
    else:
        seg(S, p, q, 12, 12, width=1.2, dash="4 3", color="var(--muted)")
LBL = {"a": (0, -24), "b": (0, 24), "c": (0, -24), "d": (0, 24), "e": (0, -24), "f": (-8, 25), "g": (-8, -25),
       "h": (34, 0), "i": (0, -24), "j": (0, 24), "k": (8, -25), "l": (0, -24), "m": (0, 24)}
for v in V21:
    x, y = POS21[v]
    if v in cut21:
        vertex(S, x, y, v, stroke="var(--hi)", fill="var(--hi)", fill_opacity=0.28, width=2.2)
    else:
        vertex(S, x, y, v)
    dx, dy = LBL[v]
    S.text(x + dx, y + dy, f"{pre[v]}/{low[v]}", size=12, font=MONO, halo=True)
S.text(325, 264, "label: pre/low · thick: DFS tree from a · dashed: non-tree edges", size=12, color="var(--muted)")
assert (pre["d"], low["c"], pre["f"], low["h"], pre["g"], low["i"], pre["k"], low["l"]) == (3, 3, 6, 13, 7, 7, 10, 10)
assert children["a"] == ["b"]
order = sorted(V21, key=lambda v: pre[v])
assert "".join(order) == "abdcefgijklmh"
save("a06x-low", S.figure(
    "<strong>Low numbers find cut vertices and bridges.</strong> The graph of the book's Figure 6.21 (our labels), "
    "searched from <i>a</i> with alphabetical adjacency lists; each vertex shows <i>v.pre</i>/<i>v.low</i>. "
    "A non-root vertex is a cut vertex when some child has low ≥ its own pre: <i>d</i> (child <i>c</i>, low 3), "
    "<i>f</i> (child <i>h</i>, low 13), <i>g</i> (child <i>i</i>, low 7) and <i>k</i> (child <i>l</i>, low 10). "
    "The root <i>a</i> has one child, so it is not. The only tree edge with <i>v.low</i> = <i>v.pre</i> is "
    "<i>fh</i>, the only bridge.",
    alt="a thirteen-vertex undirected graph with a depth-first tree, pre and low labels, four cut vertices and one bridge"))

# =========================================================================== 3. Tarry2 is not DFS
names = ["s", "a", "b", "x"]
ADJ8 = {"s": ["a", "x", "b"], "a": ["s", "b"], "b": ["a", "s", "x"], "x": ["s", "b"]}
color = {(v, w): "white" for v in ADJ8 for w in ADJ8[v]}
marked, pre8, post8 = set(), {}, {}
v, clk, walk = "s", 1, []
while True:
    walk.append(v)
    if v not in marked:
        pre8[v] = clk
        clk += 1
        marked.add(v)
    white = [w for w in ADJ8[v] if color[(v, w)] == "white"]
    green = [w for w in ADJ8[v] if color[(v, w)] == "green"]
    if white:
        w = white[0]
        if w not in marked:
            color[(w, v)] = "green"
        color[(v, w)] = "red"
        v = w
    elif green:
        post8[v] = clk
        clk += 1
        v = green[0]
    else:
        break
greens = {frozenset(e) for e, c in color.items() if c == "green"}
assert greens == {frozenset("sa"), frozenset("ab"), frozenset("sx")}
assert pre8 == {"s": 1, "a": 2, "b": 3, "x": 4} and post8 == {"x": 5, "b": 6, "a": 7}
assert "".join(walk) == "sabsxbxsbas"
P8 = {"s": (70, 50), "a": (190, 50), "b": (190, 160), "x": (70, 160)}
S = SVG(600, 250)
for u, w in [("s", "a"), ("a", "b"), ("s", "b"), ("s", "x"), ("x", "b")]:
    if frozenset((u, w)) in greens:
        seg(S, P8[u], P8[w], 13, 13, width=3.0, color="var(--accent)")
    else:
        seg(S, P8[u], P8[w], 13, 13, width=1.3, dash="5 3", color="var(--hi)" if {u, w} == {"x", "b"} else "var(--muted)")
for u in names:
    vertex(S, *P8[u], u, r=13)
lab = {u: f"{pre8[u]}/{post8.get(u, '–')}" for u in names}
for u, (dx, dy) in {"s": (-34, 0), "a": (34, 0), "b": (34, 0), "x": (-34, 0)}.items():
    S.text(P8[u][0] + dx, P8[u][1] + dy, lab[u], size=12, font=MONO)
for k, (u, w) in enumerate([("s", "a x b"), ("a", "s b"), ("b", "a s x"), ("x", "s b")]):
    S.text(46 + (k % 2) * 100, 198 + (k // 2) * 18, f"{u}: {w}", size=12, font=MONO, color="var(--muted)",
           anchor="start")
S.text(130, 240, "walk: " + " ".join(walk), size=12, font=MONO, color="var(--muted)")
# active intervals
TX0, TW, TY = 300, 38, 60
for t in range(1, 8):
    S.text(TX0 + (t - 0.5) * TW, TY + 140, str(t), size=12, color="var(--muted)")
    S.line(TX0 + (t - 0.5) * TW, TY - 22, TX0 + (t - 0.5) * TW, TY + 128, width=0.5, color="var(--muted)", dash="2 3")
rows = [("s", 1, 7.6, True), ("a", 2, 7, False), ("b", 3, 6, False), ("x", 4, 5, False)]
for k, (u, a0, b0, open_end) in enumerate(rows):
    y = TY + k * 34
    x1, x2 = TX0 + (a0 - 0.5) * TW, TX0 + (b0 - 0.5) * TW
    S.rect(x1 - 6, y - 9, x2 - x1 + 12, 18, rx=9, stroke="var(--hi)" if u == "x" else "currentColor",
           fill="var(--accent)", fill_opacity=0.15, width=1.3, dash="4 3" if open_end else None)
    S.text(TX0 - 16, y, u, size=15, font=SERIF_IT, italic=True)
S.text(TX0 + 3.5 * TW, TY - 38, "intervals [pre, post]", size=12, color="var(--muted)")
save("a06x-tarry2", S.figure(
    "<strong>Tarry2 is not depth-first search.</strong> Left: the green edges (thick) that Tarry2 leaves on this "
    "graph, with <i>pre</i>/<i>post</i> labels. Right: the intervals [<i>pre</i>, <i>post</i>]; <i>s</i> never gets "
    "a <i>post</i> label. The interval of <i>x</i> is nested in that of <i>b</i>, yet <i>x</i> is not a descendant "
    "of <i>b</i>, and the non-tree edge <i>xb</i> (red, dashed) joins two different subtrees of <i>s</i>. Neither "
    "can happen in a depth-first search of an undirected graph.",
    alt="a four-vertex graph with a spanning tree and nested intervals that no depth-first search can produce"))
