#!/usr/bin/env python3
"""Figures for Algorithms Chapter 5 (basic graph algorithms). Writes tools/figs/a05-<name>.html; then run
tools/assemble.py on the chapter page. Every tree, region and count drawn here is computed by running the
page's WhateverFirstSearch (pairs in the bag, mark on the way out); tools/checks/a05.py re-derives the numbers
in the captions independently."""
import math
import os
import random
from figlib import SVG, MONO, SERIF_IT, SANS

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")
os.makedirs(OUT, exist_ok=True)


def save(name, html):
    with open(os.path.join(OUT, name + ".html"), "w", encoding="utf-8") as f:
        f.write(html + "\n")
    print("wrote", name)


def wfs(adj, s, take):
    """The page's WhateverFirstSearch(s); take(bag) removes and returns one pair. Returns (order, parent)."""
    bag = [(None, s)]
    parent, order = {}, []
    while bag:
        p, v = take(bag)
        if v not in parent:
            parent[v] = p
            order.append(v)
            for w in adj[v]:
                bag.append((v, w))
    return order, parent


STACK = lambda bag: bag.pop()
QUEUE = lambda bag: bag.pop(0)


def vertex(S, x, y, name, r=12, stroke="currentColor", fill="var(--paper)", width=1.5, fill_opacity=None, size=15):
    S.circle(x, y, r, stroke=stroke, fill=fill, width=width, fill_opacity=fill_opacity)
    S.text(x, y + 1, name, size=size, font=SERIF_IT, italic=True)


def seg(S, p, q, r1, r2, **kw):
    """Undirected edge between two circles of radii r1, r2."""
    (x1, y1), (x2, y2) = p, q
    L = math.hypot(x2 - x1, y2 - y1)
    ux, uy = (x2 - x1) / L, (y2 - y1) / L
    S.line(x1 + ux * r1, y1 + uy * r1, x2 - ux * r2, y2 - uy * r2, **kw)


# =========================================================================== 1. adjacency list and matrix
V = "abcdefgh"
EDGES = ["ab", "ac", "bc", "bd", "cd", "de", "ef", "gh"]
ADJ = {v: sorted([e[1] for e in EDGES if e[0] == v] + [e[0] for e in EDGES if e[1] == v]) for v in V}
POS = {"a": (34, 128), "b": (94, 82), "c": (94, 174), "d": (154, 128), "e": (214, 82), "f": (214, 174),
       "g": (268, 82), "h": (268, 174)}
S = SVG(660, 244)
S.text(150, 16, "the graph G", size=13, color="var(--muted)")
for e in EDGES:
    seg(S, POS[e[0]], POS[e[1]], 12, 12, width=1.5)
for v in V:
    vertex(S, *POS[v], v)
S.text(150, 232, "V = 8,  E = 8,  two components", size=13, color="var(--muted)")
# adjacency list: one row per vertex, array cell then linked cells
X0, Y0, CW, RH = 318, 46, 21, 21.5
S.text(X0 + 52, 16, "adjacency list", size=13, color="var(--muted)")
for k, v in enumerate(V):
    y = Y0 + k * RH
    S.rect(X0, y, CW, CW - 2, stroke="currentColor", fill="var(--accent)", fill_opacity=0.12, width=1.2)
    S.text(X0 + CW / 2, y + (CW - 2) / 2 + 1, v, size=14, font=SERIF_IT, italic=True)
    x = X0 + CW
    for w in ADJ[v]:
        S.line(x + 2, y + (CW - 2) / 2, x + 13, y + (CW - 2) / 2, width=1.1, arrow=True)
        x += 16
        S.rect(x, y, CW - 2, CW - 2, rx=3, stroke="currentColor", fill="var(--paper)", width=1.1)
        S.text(x + (CW - 2) / 2, y + (CW - 2) / 2 + 1, w, size=14, font=SERIF_IT, italic=True)
        x += CW - 2
# adjacency matrix
MX, MY, MC = 476, 46, 21
S.text(MX + 4 * MC, 16, "adjacency matrix", size=13, color="var(--muted)")
for j, w in enumerate(V):
    S.text(MX + j * MC + MC / 2, MY - 8 + 1, w, size=13, font=SERIF_IT, italic=True, color="var(--muted)")
ones = 0
for i, v in enumerate(V):
    S.text(MX - 10, MY + i * MC + MC / 2 + 1, v, size=13, font=SERIF_IT, italic=True, color="var(--muted)")
    for j, w in enumerate(V):
        bit = 1 if w in ADJ[v] else 0
        ones += bit
        x, y = MX + j * MC, MY + i * MC
        if bit:
            S.rect(x, y, MC, MC, stroke="none", fill="var(--accent)", fill_opacity=0.22, width=0)
        S.rect(x, y, MC, MC, stroke="currentColor", fill="none", width=0.4)
        S.text(x + MC / 2, y + MC / 2 + 1, str(bit), size=12, font=MONO,
               color="currentColor" if bit else "var(--muted)")
S.rect(MX, MY, 8 * MC, 8 * MC, stroke="currentColor", fill="none", width=1.2)
assert ones == 2 * len(EDGES) == sum(len(ADJ[v]) for v in V)
S.text(MX + 4 * MC, 232, "symmetric, zero diagonal", size=12, color="var(--muted)")
save("a05-representations", S.figure(
    "<strong>One graph, two data structures.</strong> The example graph <i>G</i> of this page, its standard "
    "adjacency list and its adjacency matrix. In the list every undirected edge appears twice, once at each "
    "endpoint (2<i>E</i> = 16 records; the order within a list is arbitrary — here alphabetical). The matrix has "
    "<i>V</i>² = 64 entries whatever the number of edges; its 16 ones form a symmetric pattern with zeros on the "
    "diagonal.",
    alt="an eight-vertex graph with two components, its adjacency lists and its adjacency matrix"))

# =========================================================================== 2. spanning trees on a grid
N = 7
ORDER = [(-1, 0), (0, 1), (1, 0), (0, -1)]  # neighbor lists: up, right, down, left


def grid_adj(n):
    adj = {}
    for i in range(n):
        for j in range(n):
            adj[(i, j)] = [(i + di, j + dj) for di, dj in ORDER if 0 <= i + di < n and 0 <= j + dj < n]
    return adj


GA = grid_adj(N)
C = (N // 2, N // 2)
rng = random.Random(3)
RAND = lambda bag: bag.pop(rng.randrange(len(bag)))
trees = []
for name, take in [("stack", STACK), ("queue", QUEUE), ("random", RAND)]:
    order, parent = wfs(GA, C, take)

    def depth(v):
        d = 0
        while parent[v] is not None:
            v, d = parent[v], d + 1
        return d

    trees.append((name, parent, max(depth(v) for v in GA)))
DEPTHS = [t[2] for t in trees]
SP, PW = 25, 214
S = SVG(3 * PW, 238)
titles = ["stack: depth-first", "queue: breadth-first", "random bag"]
for k, (name, parent, dmax) in enumerate(trees):
    ox, oy = k * PW + (PW - (N - 1) * SP) / 2, 34
    P = lambda v: (ox + v[1] * SP, oy + v[0] * SP)
    for v, ws in GA.items():
        for w in ws:
            if v < w:
                S.line(*P(v), *P(w), width=1.0, color="var(--muted)", opacity=0.6)
    for v, p in parent.items():
        if p is not None:
            S.line(*P(p), *P(v), width=3.2, color="var(--accent)")
    for v in GA:
        if v == C:
            S.circle(*P(v), 6.5, stroke="var(--hi)", fill="var(--hi)", width=1.5)
        else:
            S.circle(*P(v), 3.6, stroke="currentColor", fill="var(--paper)", width=1.2)
    S.text(k * PW + PW / 2, 14, titles[k], size=13)
    S.text(k * PW + PW / 2, oy + (N - 1) * SP + 24, f"tree depth {dmax}", size=13, color="var(--muted)")
assert DEPTHS[0] == N * N - 1 and DEPTHS[1] == 2 * (N // 2)
save("a05-spanning-trees", S.figure(
    "<strong>Whatever-first, three ways.</strong> WhateverFirstSearch from the center (red) of a 7 × 7 grid, "
    "every neighbor list in the order up, right, down, left; the parent edges are thick. With a stack the "
    f"depth-first tree is a single path through all 49 vertices (depth {DEPTHS[0]}); with a queue the "
    f"breadth-first tree has depth {DEPTHS[1]}, the true distance to the corners; taking a random pair out of the "
    f"bag still gives a spanning tree (depth {DEPTHS[2]}). Each search takes 169 = 2<i>E</i> + 1 pairs out of the bag.",
    alt="three spanning trees of a seven by seven grid: a long snake, a short bushy tree and a random tree"))

# =========================================================================== 3. flood fill
PIX = ["...#..#.",
       ".#.#..#.",
       "...#.##.",
       "##.#....",
       "..##.#.#",
       ".#.#.#..",
       "...#.##.",
       "####...."]
n = len(PIX)
assert all(len(r) == n for r in PIX)
START = (2, 1)


def pix_adj(pix):
    m = len(pix)
    adj = {}
    for i in range(m):
        for j in range(m):
            adj[(i, j)] = [(i + di, j + dj) for di, dj in ORDER
                           if 0 <= i + di < m and 0 <= j + dj < m and pix[i + di][j + dj] == pix[i][j]]
    return adj


PA = pix_adj(PIX)
REGION, _ = wfs(PA, START, STACK)
REGION = set(REGION)
NE = sum(len(ws) for ws in PA.values()) // 2
CELL = 26
S = SVG(600, 254)
for k in range(2):
    ox, oy = 28 + k * 320, 36
    after = k == 1
    for i in range(n):
        for j in range(n):
            x, y = ox + j * CELL, oy + i * CELL
            if after and (i, j) in REGION:
                S.rect(x, y, CELL, CELL, stroke="none", fill="var(--accent)", fill_opacity=0.55, width=0)
            elif PIX[i][j] == "#":
                S.rect(x, y, CELL, CELL, stroke="none", fill="currentColor", fill_opacity=0.72, width=0)
            S.rect(x, y, CELL, CELL, stroke="var(--muted)", fill="none", width=0.5)
    S.rect(ox, oy, n * CELL, n * CELL, stroke="currentColor", fill="none", width=1.2)
    if not after:
        for v, ws in PA.items():
            for w in ws:
                if v < w:
                    (i1, j1), (i2, j2) = v, w
                    inreg = v in REGION
                    dark = PIX[i1][j1] == "#"
                    S.line(ox + j1 * CELL + CELL / 2, oy + i1 * CELL + CELL / 2, ox + j2 * CELL + CELL / 2,
                           oy + i2 * CELL + CELL / 2, width=2.2 if inreg else 1.1,
                           color="var(--accent)" if inreg else ("var(--paper)" if dark else "var(--muted)"))
        for i in range(n):
            for j in range(n):
                cx, cy = ox + j * CELL + CELL / 2, oy + i * CELL + CELL / 2
                if (i, j) in REGION:
                    S.circle(cx, cy, 3.0, stroke="var(--accent)", fill="var(--accent)", width=1)
                else:
                    S.circle(cx, cy, 1.8, stroke="none", fill="var(--paper)" if PIX[i][j] == "#" else "var(--muted)",
                             width=0)
    si, sj = START
    S.circle(ox + sj * CELL + CELL / 2, oy + si * CELL + CELL / 2, 8.5, stroke="var(--hi)", fill="none", width=2.2)
    S.text(ox + n * CELL / 2, 18, "before: the pixel map and the graph G" if not after else "after FloodFill",
           size=13)
S.line(28 + n * CELL + 14, 36 + n * CELL / 2, 348 - 14, 36 + n * CELL / 2, width=2.2, color="var(--accent)",
       arrow=True)
assert len(REGION) == 9
save("a05-flood-fill", S.figure(
    "<strong>Flood fill is reachability.</strong> Left: an 8 × 8 pixel map in two colors, plain and shaded; the "
    "graph <i>G</i> joins horizontally or vertically adjacent pixels of the same color "
    f"({NE} edges, drawn between pixel centers). The region of the circled pixel is its component in <i>G</i> — "
    f"the {len(REGION)} plain pixels in color. Right: whatever-first search from the circled pixel recolors exactly "
    "that component. Plain pixels that touch the region only diagonally, or are cut off by shaded pixels, keep "
    "their color.",
    alt="an eight by eight pixel map with its same-color adjacency graph, before and after flood fill"))

# =========================================================================== 4. walks of even length
GV = ["s", "t", "u", "v"]
GE = ["st", "tu", "uv", "vt"]
GP = {"s": (40, 130), "t": (110, 130), "u": (170, 70), "v": (170, 190)}
S = SVG(620, 222)
S.text(105, 20, "G", size=14, font=SERIF_IT, italic=True)
for e in GE:
    seg(S, GP[e[0]], GP[e[1]], 13, 13, width=1.5)
for v in GV:
    vertex(S, *GP[v], v, r=13)
# H = G x {0, 1}
HX = {"s": 290, "t": 380, "u": 470, "v": 560}
HY = {0: 70, 1: 190}
S.text(425, 20, "H = G × {0, 1}", size=14, font=SERIF_IT, italic=True)
S.text(252, HY[0], "0", size=13, color="var(--muted)", anchor="end")
S.text(252, HY[1], "1", size=13, color="var(--muted)", anchor="end")
HE = []
for e in GE:
    u, v = e
    for b in (0, 1):
        HE.append(((u, b), (v, 1 - b)))
PATH = [("s", 0), ("t", 1), ("u", 0), ("v", 1), ("t", 0)]
pe = {frozenset(p) for p in zip(PATH, PATH[1:])}
for a, b in HE:
    on = frozenset((a, b)) in pe
    seg(S, (HX[a[0]], HY[a[1]]), (HX[b[0]], HY[b[1]]), 17, 17, width=2.8 if on else 1.2,
        color="var(--accent)" if on else "currentColor", opacity=None if on else 0.55)
for v in GV:
    for b in (0, 1):
        x, y = HX[v], HY[b]
        hi = (v, b) in (("s", 0), ("t", 0))
        S.circle(x, y, 17, stroke="var(--hi)" if hi else "currentColor", fill="var(--paper)", width=1.8 if hi else 1.3)
        S.text(x, y + 1, f"{v},{b}", size=14, font=SERIF_IT, italic=True)
assert len(HE) == 2 * len(GE)
save("a05-parity", S.figure(
    "<strong>Remembering parity in the vertices.</strong> Every vertex <i>v</i> of <i>G</i> becomes two vertices "
    "(<i>v</i>, 0) and (<i>v</i>, 1) of <i>H</i>, and every edge <i>uv</i> becomes two edges that switch the "
    "parity bit. The only path from <i>s</i> to <i>t</i> in <i>G</i> has one edge, but (<i>t</i>, 0) is "
    "reachable from (<i>s</i>, 0) in <i>H</i>, along the colored path; it is the walk "
    "<i>s</i>→<i>t</i>→<i>u</i>→<i>v</i>→<i>t</i> of length 4. Without the triangle, <i>G</i> would be "
    "bipartite and (<i>t</i>, 0) unreachable.",
    alt="a four-vertex graph and its two-layer parity graph with an even walk highlighted"))
