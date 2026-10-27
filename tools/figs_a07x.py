#!/usr/bin/env python3
"""Figures for the Chapter 7 exercises page (Erickson, Algorithms). Writes tools/figs/a07x-<name>.html; then run
tools/assemble.py on content/2-algorithms/07-minimum-spanning-trees-exercises.md. Every tree drawn here is computed
(Kruskal on the drawn weights) and every claim in a caption is asserted; tools/checks/a07x.py re-derives the same
facts by brute force over all spanning trees and all paths."""
import math
import os
from figlib import SVG, SERIF_IT, SANS

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")
os.makedirs(OUT, exist_ok=True)


def save(name, html):
    with open(os.path.join(OUT, name + ".html"), "w", encoding="utf-8") as f:
        f.write(html + "\n")
    print("wrote", name)


def kruskal(V, E, sign=1):
    """E: list of (a, b, w) with vertex names; returns the set of indices of a minimum (sign=1) or maximum
    (sign=-1) spanning forest."""
    p = {v: v for v in V}

    def find(x):
        while p[x] != x:
            x = p[x]
        return x

    out = set()
    for i in sorted(range(len(E)), key=lambda i: sign * E[i][2]):
        a, b = find(E[i][0]), find(E[i][1])
        if a != b:
            p[a] = b
            out.add(i)
    return out


def tree_path(E, T, s, t):
    adj = {}
    for i in T:
        a, b, _ = E[i]
        adj.setdefault(a, []).append((b, i))
        adj.setdefault(b, []).append((a, i))
    par = {s: None}
    bag = [s]
    while bag:
        x = bag.pop()
        for y, i in adj.get(x, []):
            if y not in par:
                par[y] = (x, i)
                bag.append(y)
    path = []
    while t != s:
        x, i = par[t]
        path.append(i)
        t = x
    return path[::-1]


R = 12  # vertex radius


def vertex(S, x, y, name="", stroke="currentColor", fill="var(--paper)", width=1.5, fill_opacity=None):
    S.circle(x, y, R, stroke=stroke, fill=fill, width=width, fill_opacity=fill_opacity)
    if name:
        S.text(x, y + 1, name, size=15, font=SERIF_IT, italic=True)


def seg(S, p, q, **kw):
    (x1, y1), (x2, y2) = p, q
    L = math.hypot(x2 - x1, y2 - y1)
    ux, uy = (x2 - x1) / L, (y2 - y1) / L
    S.line(x1 + ux * R, y1 + uy * R, x2 - ux * R, y2 - uy * R, **kw)


def wlabel(S, p, q, w, side=1, dist=11, t=0.5, color="currentColor", dx=0, dy=0):
    """Weight label near the point at fraction t of pq, pushed `dist` px to the left (side=1) or right (-1)."""
    (x1, y1), (x2, y2) = p, q
    L = math.hypot(x2 - x1, y2 - y1)
    nx, ny = (y2 - y1) / L, -(x2 - x1) / L
    x, y = x1 + (x2 - x1) * t + nx * dist * side + dx, y1 + (y2 - y1) * t + ny * dist * side + dy
    S.text(x, y, str(w), size=13, color=color, halo=True)


THICK = dict(width=3.4, color="var(--accent)")
THIN = dict(width=1.3, color="currentColor")
HI_DASH = dict(width=2.2, color="var(--hi)", dash="6 4")

# =========================================================================== 1. Exercise 7.1(b): the diamond
P = {"u": (60, 105), "v": (260, 105), "x": (160, 40), "y": (160, 175)}
DE = [("u", "x", 1), ("x", "v", 2), ("u", "v", 3), ("u", "y", 4), ("v", "y", 5)]
T = kruskal(P, DE)
assert {DE[i][:2] for i in T} == {("u", "x"), ("x", "v"), ("u", "y")}
uv = 2
assert uv not in T and DE[uv][2] == min(w for a, b, w in DE if {a, b} <= {"u", "v", "y"})
assert DE[uv][2] == max(w for a, b, w in DE if {a, b} <= {"u", "v", "x"})
S = SVG(520, 215)
S.path(f"M{P['u'][0]},{P['u'][1]} L{P['x'][0]},{P['x'][1]} L{P['v'][0]},{P['v'][1]} Z", color="none",
       fill="var(--accent2)", opacity=0.13)
S.path(f"M{P['u'][0]},{P['u'][1]} L{P['y'][0]},{P['y'][1]} L{P['v'][0]},{P['v'][1]} Z", color="none",
       fill="var(--hi)", opacity=0.10)
for i, (a, b, w) in enumerate(DE):
    seg(S, P[a], P[b], **(THICK if i in T else HI_DASH if i == uv else THIN))
LBL = {("u", "x"): 1, ("x", "v"): 1, ("u", "v"): 1, ("u", "y"): -1, ("v", "y"): -1}
for a, b, w in DE:
    wlabel(S, P[a], P[b], w, side=LBL[(a, b)], color="var(--hi)" if (a, b) == ("u", "v") else "currentColor")
for v, (x, y) in P.items():
    vertex(S, x, y, v)
S.text(300, 62, "cycle u x v: uv is the heaviest edge", size=13, anchor="start", color="currentColor")
S.text(300, 80, "→ not in the MST, by part (a)", size=13, anchor="start", color="var(--muted)")
S.text(300, 140, "cycle u v y: uv is the lightest edge", size=13, anchor="start", color="currentColor")
S.text(300, 158, "→ still not in the MST", size=13, anchor="start", color="var(--muted)")
S.text(160, 205, "thick: the MST {ux, xv, uy}, weight 7", size=12, color="var(--muted)")
save("a07x-diamond", S.figure(
    "<strong>The lightest edge of a cycle can be left out.</strong> The edge <i>uv</i> (weight 3, red dashed) lies on "
    "two cycles. It is the heaviest edge of the cycle <i>u x v</i> (blue tint), so by part (a) the MST excludes it — "
    "yet it is the lightest edge of the cycle <i>u v y</i> (red tint). The MST (thick) is {<i>ux</i>, <i>xv</i>, "
    "<i>uy</i>}.",
    alt="a four-vertex graph with two triangles sharing the edge uv; the minimum spanning tree avoids uv"))

# =========================================================================== 2. Exercise 7.2(b): unique MSTs that violate a bullet
S = SVG(600, 250)
# left: the triangle a b c with ab = bc = 1, ca = 2
PL = {"a": (50, 175), "b": (140, 50), "c": (230, 175)}
TE = [("a", "b", 1), ("b", "c", 1), ("c", "a", 2)]
TT = kruskal(PL, TE)
assert TT == {0, 1}
S.path("M140,14 C196,14 196,98 140,98 C84,98 84,14 140,14 Z", color="var(--hi)", width=1.4, dash="4 3")
S.text(203, 30, "S = {b}", size=13, anchor="start", color="var(--hi)")
for i, (a, b, w) in enumerate(TE):
    seg(S, PL[a], PL[b], **(THICK if i in TT else THIN))
wlabel(S, PL["a"], PL["b"], 1, side=1, color="var(--hi)")
wlabel(S, PL["b"], PL["c"], 1, side=1, color="var(--hi)")
wlabel(S, PL["c"], PL["a"], 2, side=1)
for v, (x, y) in PL.items():
    vertex(S, x, y, v)
S.text(140, 212, "unique MST {ab, bc}; the cut S has", size=12, color="var(--muted)")
S.text(140, 228, "two lightest edges (cut condition fails)", size=12, color="var(--muted)")
# right: H with ac 1, ax 2, bx 3, ab 4, bc 4
PR = {"a": (330, 115), "b": (540, 115), "x": (435, 40), "c": (435, 185)}
HE = [("a", "c", 1), ("a", "x", 2), ("b", "x", 3), ("a", "b", 4), ("b", "c", 4)]
TH = kruskal(PR, HE)
assert TH == {0, 1, 2}
S.path("M330,115 L540,115 L435,185 Z", color="none", fill="var(--hi)", opacity=0.10)
for i, (a, b, w) in enumerate(HE):
    seg(S, PR[a], PR[b], **(THICK if i in TH else HI_DASH))
wlabel(S, PR["a"], PR["c"], 1, side=-1)
wlabel(S, PR["a"], PR["x"], 2, side=-1)
wlabel(S, PR["b"], PR["x"], 3, side=1)
wlabel(S, PR["a"], PR["b"], 4, side=1, color="var(--hi)")
wlabel(S, PR["b"], PR["c"], 4, side=1, color="var(--hi)")
for v, (x, y) in PR.items():
    vertex(S, x, y, v)
S.text(435, 212, "unique MST {ac, ax, bx}; the cycle a b c has", size=12, color="var(--muted)")
S.text(435, 228, "two heaviest edges (cycle condition fails)", size=12, color="var(--muted)")
S.line(282, 20, 282, 235, width=0.8, color="var(--muted)", dash="2 4")
save("a07x-unique", S.figure(
    "<strong>Unique minimum spanning trees that break the book's conditions.</strong> Left: the triangle of part (a). "
    "Its MST {<i>ab</i>, <i>bc</i>} is unique, but the cut around <i>S</i> = {<i>b</i>} has two lightest edges. "
    "Right: the graph <i>H</i>. Its MST (thick) is unique, but the cycle <i>a b c</i> (tinted) has two heaviest "
    "edges, <i>ab</i> and <i>bc</i>. Each of them is the strictly heaviest edge of another cycle (<i>a x b</i>, and "
    "<i>b c a x</i>), so no MST uses it.",
    alt="two small weighted graphs, each with a unique minimum spanning tree, one violating the cut condition and "
        "one violating the cycle condition"))

# =========================================================================== hexagon of the book's Figure 7.1
HX = {"top": (0, -104), "UL": (-92, -52), "UR": (92, -52), "C": (0, 0), "LL": (-92, 52), "LR": (92, 52),
      "B": (0, 104)}
# label offsets (dx, dy) relative to the midpoint, per edge
HLBL = {("top", "UL"): (-10, -10), ("top", "UR"): (10, -10), ("UL", "UR"): (0, -10), ("UL", "C"): (-6, 11),
        ("C", "UR"): (6, 11), ("UL", "LL"): (-13, 0), ("UR", "LR"): (13, 0), ("C", "LL"): (-8, -11),
        ("C", "LR"): (8, -11), ("C", "B"): (-11, 0), ("LL", "B"): (-10, 10), ("B", "LR"): (10, 10)}


def hexgraph(S, ox, oy, E, styles, names=None, label_colors=None, vstyle=None):
    pos = {v: (ox + x, oy + y) for v, (x, y) in HX.items()}
    for i, (a, b, w) in enumerate(E):
        seg(S, pos[a], pos[b], **styles(i))
    for i, (a, b, w) in enumerate(E):
        (x1, y1), (x2, y2) = pos[a], pos[b]
        dx, dy = HLBL[(a, b)]
        col = (label_colors or {}).get(i, "currentColor")
        S.text((x1 + x2) / 2 + dx, (y1 + y2) / 2 + dy, str(w), size=13, color=col, halo=True)
    for v, (x, y) in pos.items():
        st = (vstyle or {}).get(v, {})
        vertex(S, x, y, (names or {}).get(v, ""), **st)
    return pos


# =========================================================================== 3. Exercise 7.6(a): second smallest spanning tree
F71 = [("top", "UL", 8), ("top", "UR", 5), ("UL", "UR", 10), ("UL", "C", 2), ("C", "UR", 3), ("UL", "LL", 18),
       ("UR", "LR", 16), ("C", "LL", 12), ("C", "LR", 30), ("C", "B", 14), ("LL", "B", 4), ("B", "LR", 26)]
T71 = kruskal(HX, F71)
assert sorted(F71[i][2] for i in T71) == [2, 3, 4, 5, 12, 16]
best = None
for g in range(len(F71)):
    if g in T71:
        continue
    path = tree_path(F71, T71, F71[g][0], F71[g][1])
    f = max(path, key=lambda i: F71[i][2])
    d = F71[g][2] - F71[f][2]
    if best is None or d < best[0]:
        best = (d, g, f)
d, g, f = best
assert (F71[g][2], F71[f][2], d) == (14, 12, 2)
S = SVG(480, 265)


def st71(i):
    if i == g:
        return HI_DASH
    if i == f:
        return dict(width=3.4, color="var(--accent)", opacity=0.35)
    return THICK if i in T71 else dict(width=1.2, color="var(--muted)")


pos = hexgraph(S, 130, 132, F71, st71, label_colors={g: "var(--hi)", f: "var(--hi)"})
# cross out f
(x1, y1), (x2, y2) = pos["C"], pos["LL"]
mx, my = x1 + 0.68 * (x2 - x1), y1 + 0.68 * (y2 - y1)
S.line(mx - 7, my - 7, mx + 7, my + 7, width=2.4, color="var(--hi)")
S.line(mx - 7, my + 7, mx + 7, my - 7, width=2.4, color="var(--hi)")
S.text(262, 70, "MST T (thick): weight 42", size=13, anchor="start")
S.text(262, 98, "g = 14 (dashed) closes a cycle", size=13, anchor="start", color="var(--hi)")
S.text(262, 116, "whose heaviest tree edge is", size=13, anchor="start", color="var(--hi)")
S.text(262, 134, "f = 12 (crossed out)", size=13, anchor="start", color="var(--hi)")
S.text(262, 162, "T − f + g: weight 44,", size=13, anchor="start")
S.text(262, 180, "the second smallest", size=13, anchor="start")
save("a07x-second", S.figure(
    "<strong>The second smallest spanning tree is one swap away.</strong> The graph of the book's Figure 7.1 with its "
    "MST (thick, weight 42). Of the six non-tree edges, 14 is the cheapest to swap in: it closes the cycle through "
    "12 and 4, and removing 12 costs only 14 − 12 = 2 extra. The result, weight 44, is the second smallest "
    "spanning tree.",
    alt="the book's seven-vertex example graph with its minimum spanning tree and one swap marked"))

# =========================================================================== 4. Exercise 7.9: bottleneck distance
B9 = [("top", "UL", 1), ("top", "UR", 11), ("UL", "UR", 6), ("UL", "C", 4), ("C", "UR", 3), ("UL", "LL", 5),
      ("UR", "LR", 9), ("C", "LL", 10), ("C", "LR", 12), ("C", "B", 7), ("LL", "B", 8), ("B", "LR", 2)]
TM = kruskal(HX, B9, sign=-1)
assert sorted(B9[i][2] for i in TM) == [6, 8, 9, 10, 11, 12]
P9 = tree_path(B9, TM, "LL", "top")
assert [B9[i][2] for i in P9] == [10, 12, 9, 11] and min(B9[i][2] for i in P9) == 9
S = SVG(420, 265)


def st9(i):
    if i in P9:
        return dict(width=3.6, color="var(--hi)")
    return THICK if i in TM else dict(width=1.2, color="var(--muted)")


onpath = {v for i in P9 for v in B9[i][:2]}
pos = hexgraph(S, 130, 132, B9, st9, names={"top": "t", "LL": "s"},
               label_colors={i: "var(--hi)" for i in P9},
               vstyle={v: dict(stroke="var(--hi)", fill="var(--hi)", fill_opacity=0.18, width=1.8) for v in onpath})
S.text(262, 80, "thick: the maximum", size=13, anchor="start")
S.text(262, 98, "spanning tree", size=13, anchor="start")
S.text(262, 130, "red: its s–t path", size=13, anchor="start", color="var(--hi)")
S.text(262, 148, "10, 12, 9, 11 — width 9", size=13, anchor="start", color="var(--hi)")
S.text(262, 180, "no s–t path is wider:", size=13, anchor="start")
S.text(262, 198, "bottleneck distance 9", size=13, anchor="start")
save("a07x-bottleneck", S.figure(
    "<strong>The maximum spanning tree contains a widest path.</strong> The graph of the book's figure for "
    "Exercise 7.9. Its maximum spanning tree (thick) uses the edges 12, 11, 10, 9, 8 and 6; the path from <i>s</i> "
    "to <i>t</i> inside it (red) has width 9, the bottleneck distance the book states. Every other <i>s</i>–<i>t</i> "
    "path uses an edge of weight at most 8.",
    alt="the seven-vertex example graph with its maximum spanning tree and the widest s-t path"))
