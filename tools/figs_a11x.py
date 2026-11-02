#!/usr/bin/env python3
"""Figures for the Chapter 11 exercises page (content/2-algorithms/11-applications-of-flows-and-cuts-exercises.md).
Writes tools/figs/a11x-<name>.html; then run tools/assemble.py on the page. The book's graphs and boards are
re-entered from its figures; every highlighted structure (cut, disjoint paths, escape paths, cycle cover, tiling) is
validated by the asserts below, and tools/checks/a11x.py re-derives the same facts with max flow and brute force."""
import itertools
import os
from figlib import SVG, Automaton, SERIF_IT, SANS, MONO

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")
os.makedirs(OUT, exist_ok=True)


def save(name, html):
    with open(os.path.join(OUT, name + ".html"), "w", encoding="utf-8") as f:
        f.write(html + "\n")
    print("wrote", name)


# =========================================================================== 1. Exercise 11.4: Sodor
# coordinates measured on the book's figure (300 dpi crop), scaled
raw = {"s": (115, 255), "a": (295, 75), "b": (295, 255), "c": (295, 435), "X": (497, 165), "Y": (497, 340),
       "p": (677, 165), "q": (677, 340), "d": (767, 75), "e": (767, 435), "t": (945, 255)}
k = 0.6
P = {v: (32 + (x - 115) * k, 26 + (y - 75) * k) for v, (x, y) in raw.items()}
edges = [("s", "a"), ("s", "b"), ("s", "c"), ("a", "X"), ("a", "Y"), ("b", "X"), ("b", "Y"), ("c", "X"),
         ("c", "Y"), ("X", "p"), ("X", "q"), ("X", "d"), ("Y", "q"), ("Y", "p"), ("Y", "e"), ("p", "t"),
         ("q", "t"), ("d", "t"), ("d", "e"), ("e", "t")]
paths = [["s", "a", "X", "p", "t"], ["s", "b", "Y", "q", "t"]]
closed = {"X", "Y"}
E = {frozenset(e) for e in edges}
for pth in paths:
    assert all(frozenset((pth[i], pth[i + 1])) in E for i in range(len(pth) - 1))
assert not (set(paths[0][1:-1]) & set(paths[1][1:-1]))
# closing X and Y disconnects s from t
adj = {v: set() for v in P}
for a, b in edges:
    adj[a].add(b)
    adj[b].add(a)
seen, st = {"s"}, ["s"]
while st:
    u = st.pop()
    for v in adj[u] - closed - seen:
        seen.add(v)
        st.append(v)
assert "t" not in seen and seen == {"s", "a", "b", "c"}
# no single station suffices
for x in set(P) - {"s", "t"}:
    seen, st = {"s"}, ["s"]
    while st:
        u = st.pop()
        for v in adj[u] - {x} - seen:
            seen.add(v)
            st.append(v)
    assert "t" in seen

W, H = 560, 270
A = Automaton(W, H, r=13)
on_path = {frozenset((pth[i], pth[i + 1])) for pth in paths for i in range(len(pth) - 1)}
for a, b in edges:
    (x1, y1), (x2, y2) = P[a], P[b]
    if frozenset((a, b)) in on_path:
        A.line(x1, y1, x2, y2, color="var(--accent)", width=3.2)
    else:
        A.line(x1, y1, x2, y2, color="currentColor", width=1.3, opacity=0.55)
for v, (x, y) in P.items():
    if v in ("s", "t"):
        A.state(v, x, y, label=v)
    else:
        A.state(v, x, y, label="", r=9)
for v in closed:
    x, y = P[v]
    A.circle(x, y, 14, stroke="var(--hi)", fill="none", width=3)
A.text(P["X"][0] - 6, P["X"][1] - 30, "closed", size=12.5, color="var(--hi)", weight=600, halo=True)
A.text(P["Y"][0] - 6, P["Y"][1] + 30, "closed", size=12.5, color="var(--hi)", weight=600, halo=True)
html = A.figure(
    "<strong>The book's Sodor network.</strong> Closing the two circled stations (red) cuts every route from "
    "<i>s</i> to <i>t</i>: after it only <i>s</i> and the three stations next to it are reachable. One station is "
    "not enough, because the two blue routes share no station other than <i>s</i> and <i>t</i>. In the split network "
    "these are a cut of capacity 2 and a flow of value 2, so the answer is 2.",
    alt="eleven stations; two vertex-disjoint s-t routes in blue; two middle stations circled in red")
save("a11x-sodor", html)


# =========================================================================== 2. Exercise 11.5: escape (Figure 11.10)
n = 7
terms = [(2, 5), (3, 2), (3, 4), (4, 4), (4, 6), (5, 3), (5, 4), (6, 5)]
book_paths = [
    [(3, 2), (2, 2), (1, 2)],
    [(5, 3), (4, 3), (3, 3), (2, 3), (1, 3)],
    [(2, 5), (1, 5)],
    [(3, 4), (3, 5), (3, 6), (3, 7)],
    [(4, 4), (4, 5), (5, 5), (5, 6), (5, 7)],
    [(4, 6), (4, 7)],
    [(5, 4), (6, 4), (7, 4)],
    [(6, 5), (7, 5)],
]
allv = [v for p in book_paths for v in p]
assert len(allv) == len(set(allv)) and sorted(p[0] for p in book_paths) == sorted(terms)
assert all(abs(p[i][0] - p[i + 1][0]) + abs(p[i][1] - p[i + 1][1]) == 1 for p in book_paths for i in range(len(p) - 1))
assert all(p[-1][0] in (1, n) or p[-1][1] in (1, n) for p in book_paths)

step = 40
x0, y0 = 46, 30
G = SVG(560, 316)


def gx(j):
    return x0 + (j - 1) * step


def gy(i):
    return y0 + (i - 1) * step


# boundary band
G.rect(gx(1) - 15, gy(1) - 15, (n - 1) * step + 30, (n - 1) * step + 30, rx=10, stroke="var(--muted)",
       fill="var(--accent2)", fill_opacity=0.10, width=1, dash="4 4")
G.rect(gx(2) - 15, gy(2) - 15, (n - 3) * step + 30, (n - 3) * step + 30, rx=8, stroke="var(--muted)",
       fill="var(--paper)", width=1, dash="4 4")
for i in range(1, n + 1):
    G.line(gx(1), gy(i), gx(n), gy(i), width=1.1, opacity=0.5)
    G.line(gx(i), gy(1), gx(i), gy(n), width=1.1, opacity=0.5)
for p in book_paths:
    d = "M" + " L".join(f"{gx(j)},{gy(i)}" for i, j in p)
    G.path(d, color="var(--accent)", width=5)
for i in range(1, n + 1):
    for j in range(1, n + 1):
        if (i, j) in terms:
            G.circle(gx(j), gy(i), 8.5, stroke="var(--accent)", fill="var(--accent)", width=1.6)
        else:
            end = any(p[-1] == (i, j) for p in book_paths)
            G.circle(gx(j), gy(i), 6.5, stroke="var(--accent)" if end else "currentColor",
                     fill="var(--paper)", width=2.2 if end else 1.3)
# legend
lx = 352
G.circle(lx, 70, 8.5, stroke="var(--accent)", fill="var(--accent)")
G.text(lx + 16, 70, "terminal (8 of them)", anchor="start", size=13.5)
G.line(lx - 10, 104, lx + 10, 104, color="var(--accent)", width=5)
G.text(lx + 16, 104, "escape path", anchor="start", size=13.5)
G.rect(lx - 10, 128, 20, 16, rx=4, stroke="var(--muted)", fill="var(--accent2)", fill_opacity=0.10, width=1, dash="4 4")
G.text(lx + 16, 136, "boundary vertices", anchor="start", size=13.5)
G.text(lx - 10, 178, "network: every grid vertex", anchor="start", size=13, color="var(--muted)")
G.text(lx - 10, 196, "has capacity 1; s feeds each", anchor="start", size=13, color="var(--muted)")
G.text(lx - 10, 214, "terminal 1 unit; each boundary", anchor="start", size=13, color="var(--muted)")
G.text(lx - 10, 232, "vertex drains 1 unit into t.", anchor="start", size=13, color="var(--muted)")
G.text(lx - 10, 258, "max flow = 8 = m: YES", anchor="start", size=13.5, weight=600, color="var(--accent)")
save("a11x-escape", G.figure(
    "<strong>The escape problem (book's Figure 11.10).</strong> Eight terminals in a 7 × 7 grid and one set of "
    "eight vertex-disjoint escape paths (the book's). Unit vertex capacities make paths vertex-disjoint; the "
    "capacity-1 edges from <i>s</i> make every terminal start one path. The maximum flow is 8 = <i>m</i>.",
    alt="7 by 7 grid; eight filled terminal vertices with thick paths to the border"))


# =========================================================================== 3. Exercise 11.7: cycle cover
V = ["a", "b", "c", "d", "e"]
Ecc = [("a", "b"), ("b", "c"), ("c", "a"), ("d", "e"), ("e", "d"), ("b", "e"), ("c", "d"), ("d", "b")]
cover = {("a", "b"), ("b", "c"), ("c", "a"), ("d", "e"), ("e", "d")}
Es = set(Ecc)
perms = [pi for pi in itertools.permutations(V) if all((u, pi[i]) in Es for i, u in enumerate(V))]
assert len(perms) == 1 and {(u, perms[0][i]) for i, u in enumerate(V)} == cover

C = Automaton(620, 258, r=16)
pos = {"a": (50, 74), "b": (190, 74), "c": (120, 194), "e": (300, 74), "d": (300, 194)}
for v, (x, y) in pos.items():
    C.state(v, x, y)
for (u, v) in Ecc:
    inc = (u, v) in cover
    bend = 0
    if {u, v} == {"d", "e"}:
        bend = 14
    C.edge(u, v, "", bend=bend, color="var(--hi)" if inc else "var(--muted)", width=2.6 if inc else 1.4,
           dash=None if inc else "5 4")
C.text(175, 240, "cycle cover: (a b c)(d e)", size=13.5, color="var(--hi)", weight=600)
# bipartite graph
Lx, Rx, top, gap = 420, 560, 50, 40
Lp = {v: (Lx, top + i * gap) for i, v in enumerate(V)}
Rp = {v: (Rx, top + i * gap) for i, v in enumerate(V)}
for (u, v) in Ecc:
    inc = (u, v) in cover
    (x1, y1), (x2, y2) = Lp[u], Rp[v]
    C.line(x1 + 15, y1, x2 - 15, y2, color="var(--hi)" if inc else "var(--muted)", width=2.6 if inc else 1.3,
           dash=None if inc else "5 4")
for v in V:
    C.state(v + "-", *Lp[v], label=v + "⁻", r=15)
    C.state(v + "+", *Rp[v], label=v + "⁺", r=15)
C.text(Lx, 16, "out-copies", size=12.5, color="var(--muted)")
C.text(Rx, 16, "in-copies", size=12.5, color="var(--muted)")
C.text(490, 240, "perfect matching", size=13.5, color="var(--hi)", weight=600)
save("a11x-cycle-cover", C.figure(
    "<strong>Cycle covers are perfect matchings.</strong> Left: a directed graph with eight edges; its only cycle "
    "cover is (<i>a b c</i>)(<i>d e</i>) (red). Right: the bipartite graph with an edge "
    "<i>u</i>⁻<i>v</i>⁺ for every edge <i>u</i>→<i>v</i>. The cover edges form a perfect matching — every vertex "
    "gets one successor and one predecessor — and a perfect matching, read as a successor function, is a "
    "permutation, which splits into disjoint cycles.",
    alt="five-vertex digraph with a red triangle and red two-cycle; bipartite graph with five red matching edges"))


# =========================================================================== 4. Exercise 11.8: dominoes (Figure 11.12)
fig12 = {1: [1, 2, 3, 7, 8, 9], 2: [1, 2, 3, 4, 5, 7, 8, 9], 3: [2, 4, 6, 7, 8, 9], 4: [2, 4, 6, 7, 8, 9],
         5: [4, 6, 9], 6: [1, 2, 4, 5, 6, 7, 8], 7: [1, 2, 4, 5, 6, 7], 8: [1, 2, 3, 4, 5, 6, 7, 8],
         9: [1, 2, 3, 4, 5, 6]}
tiles = [((1, 1), (2, 1)), ((1, 2), (2, 2)), ((1, 3), (2, 3)), ((2, 4), (2, 5)), ((1, 7), (2, 7)),
         ((1, 8), (1, 9)), ((2, 8), (3, 8)), ((2, 9), (3, 9)), ((3, 2), (4, 2)), ((3, 4), (4, 4)),
         ((3, 6), (3, 7)), ((4, 6), (5, 6)), ((4, 7), (4, 8)), ((4, 9), (5, 9)), ((5, 4), (6, 4)),
         ((6, 1), (6, 2)), ((6, 5), (6, 6)), ((6, 7), (6, 8)), ((7, 1), (7, 2)), ((7, 4), (8, 4)),
         ((7, 5), (8, 5)), ((7, 6), (7, 7)), ((8, 1), (9, 1)), ((8, 2), (8, 3)), ((8, 6), (9, 6)),
         ((8, 7), (8, 8)), ((9, 2), (9, 3)), ((9, 4), (9, 5))]
cells = {(i, j) for i, js in fig12.items() for j in js}
cov = [c for t in tiles for c in t]
assert len(cov) == len(set(cov)) == len(cells) == 56 and set(cov) == cells
assert all(abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1 and (a[0] + a[1]) % 2 != (b[0] + b[1]) % 2 for a, b in tiles)
nb = sum((i + j) % 2 == 0 for i, j in cells)
assert nb == 28

cs = 30
D = SVG(600, 300)
ox, oy = 16, 14
for (i, j) in cells:
    dark = (i + j) % 2 == 0
    D.rect(ox + (j - 1) * cs, oy + (i - 1) * cs, cs, cs, stroke="currentColor", width=0.8,
           fill="var(--accent)" if dark else "var(--paper)", fill_opacity=0.22 if dark else None)
for a, b in tiles:
    (i1, j1), (i2, j2) = a, b
    x = ox + (min(j1, j2) - 1) * cs + 5
    y = oy + (min(i1, i2) - 1) * cs + 5
    w = (abs(j1 - j2) + 1) * cs - 10
    h = (abs(i1 - i2) + 1) * cs - 10
    D.rect(x, y, w, h, rx=6, stroke="var(--hi)", width=2)
lx = 310
D.rect(lx, 40, 18, 18, stroke="currentColor", width=0.8, fill="var(--accent)", fill_opacity=0.22)
D.text(lx + 28, 49, "“black” square, i + j even: 28", anchor="start", size=13.5)
D.rect(lx, 70, 18, 18, stroke="currentColor", width=0.8, fill="var(--paper)")
D.text(lx + 28, 79, "“white” square, i + j odd: 28", anchor="start", size=13.5)
D.rect(lx - 2, 99, 22, 12, rx=4, stroke="var(--hi)", width=2)
D.text(lx + 28, 105, "domino = matching edge", anchor="start", size=13.5)
D.text(lx, 146, "Blank cells are deleted.", anchor="start", size=13, color="var(--muted)")
D.text(lx, 166, "Each domino covers one black", anchor="start", size=13, color="var(--muted)")
D.text(lx, 184, "and one white square, so a tiling", anchor="start", size=13, color="var(--muted)")
D.text(lx, 202, "is a perfect matching between", anchor="start", size=13, color="var(--muted)")
D.text(lx, 220, "black and white squares.", anchor="start", size=13, color="var(--muted)")
D.text(lx, 250, "max flow = 28 = #black = #white", anchor="start", size=13.5, weight=600, color="var(--hi)")
save("a11x-dominoes", D.figure(
    "<strong>The book's board (Figure 11.12), colored and tiled.</strong> The 56 undeleted squares of the 9 × 9 "
    "board split into 28 of each color; adjacent squares always differ in color. The 28 dominoes (the book's "
    "tiling) form a perfect matching in the bipartite graph of adjacent black–white pairs.",
    alt="partial 9 by 9 checkerboard with shaded and plain squares and 28 domino outlines"))
