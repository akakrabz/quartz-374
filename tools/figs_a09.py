#!/usr/bin/env python3
"""Figures for Algorithms Chapter 9 (all-pairs shortest paths). Writes tools/figs/a09-<name>.html; then run
tools/assemble.py on the chapter page. Every number drawn (distances, predecessors, prices, reduced weights, the
Floyd-Warshall matrices, the min-plus powers) is computed here by running the algorithms the page states;
tools/checks/a09.py recomputes them independently and compares them with the figure HTML."""
import math
import os

from figlib import SVG, Automaton, SANS, SERIF_IT

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")
os.makedirs(OUT, exist_ok=True)
INF = math.inf


def save(name, html):
    with open(os.path.join(OUT, name + ".html"), "w", encoding="utf-8") as f:
        f.write(html + "\n")
    print("wrote", name)


def overlay_figure(A, overlay, caption, alt):
    """A.figure(), with the SVG items of `overlay` drawn on top of the edges and states."""
    svg = A.svg(alt).replace("</svg>", "".join(overlay.items) + "</svg>")
    out = f'<figure class="cs-fig">{svg}<figcaption>{caption}</figcaption></figure>'
    assert "\n\n" not in out
    return out.replace("\n", " ")


def num(x):
    if x == INF:
        return "∞"
    if x is None:
        return "–"
    return str(x).replace("-", "−")


# ------------------------------------------------------------------------------------------- the running example
N = 4
EX = {(1, 2): -2, (2, 3): 4, (3, 2): 1, (3, 4): 3, (4, 3): 2, (4, 1): -3}      # vertices 1..4
V = [1, 2, 3, 4]


def wmatrix(E, diag=0):
    W = {(u, v): (diag if u == v else E.get((u, v), INF)) for u in V for v in V}
    return W


def floyd_warshall_phases(E):
    """In-place FloydWarshall with predecessors; returns the matrices after each phase and pred."""
    D = wmatrix(E)
    P = {(u, v): (u if (u, v) in E else None) for u in V for v in V}
    phases = [dict(D)]
    for r in V:
        for u in V:
            for v in V:
                if D[(u, v)] > D[(u, r)] + D[(r, v)]:
                    D[(u, v)] = D[(u, r)] + D[(r, v)]
                    P[(u, v)] = P[(r, v)]
        phases.append(dict(D))
    return phases, P


def bellman_ford(E, verts, s):
    d = {v: INF for v in verts}
    pred = {v: None for v in verts}
    d[s] = 0
    for _ in range(len(verts) - 1):
        for (u, v), w in E.items():
            if d[u] + w < d[v]:
                d[v] = d[u] + w
                pred[v] = u
    assert not any(d[u] + w < d[v] for (u, v), w in E.items())
    return d, pred


def minplus(A, B):
    return {(i, j): min(A[(i, k)] + B[(k, j)] for k in V) for i in V for j in V}


PH, PRED = floyd_warshall_phases(EX)
DIST = PH[-1]
assert [[DIST[(u, v)] for v in V] for u in V] == [[0, -2, 2, 5], [4, 0, 4, 7], [0, -2, 0, 3], [-3, -5, -1, 0]]
assert [[PRED[(u, v)] for v in V] for u in V] == [[None, 1, 2, 3], [4, None, 2, 3], [4, 1, None, 3],
                                                  [4, 1, 2, None]]

# Johnson: new vertex s with 0-edges, Bellman-Ford prices, reduced weights
ES = dict(EX)
for v in V:
    ES[("s", v)] = 0
PI, SPRED = bellman_ford(ES, V + ["s"], "s")
assert [PI[v] for v in V] == [-3, -5, -1, 0]
assert {v: SPRED[v] for v in V} == {1: 4, 2: 1, 3: 2, 4: "s"}
EP = {(u, v): PI[u] + w - PI[v] for (u, v), w in EX.items()}
assert EP == {(1, 2): 0, (2, 3): 0, (3, 2): 5, (3, 4): 2, (4, 3): 3, (4, 1): 0}
assert all(w >= 0 for w in EP.values())


# ------------------------------------------------------------------------------------------- drawing helpers
POS = {1: (0, 0), 2: (1, 0), 3: (1, 1), 4: (0, 1)}


def draw_graph(A, x0, y0, side, weights, colors=None, widths=None, prefix=""):
    """The square layout of the running example: 1 top left, 2 top right, 3 bottom right, 4 bottom left.
    The two 2-cycles are drawn as curved pairs, outer edges 2->3 and 3->4, inner edges 3->2 and 4->3."""
    colors = colors or {}
    widths = widths or {}
    for v in V:
        cx, cy = POS[v]
        A.state(prefix + str(v), x0 + cx * side, y0 + cy * side, label=str(v), italic=False, font=SANS)
    BEND = {(2, 3): 16, (3, 2): 16, (3, 4): 16, (4, 3): 16}
    for (u, v), w in weights.items():
        A.edge(prefix + str(u), prefix + str(v), label=num(w), bend=BEND.get((u, v), 0),
               color=colors.get((u, v), "currentColor"), width=widths.get((u, v), 1.6),
               label_color="currentColor", mono=False, label_dist=11)


def matrix(S, x0, y0, M, title=None, cw=34, ch=26, hi=(), shade_row=None, shade_col=None, muted_none=True,
           title_size=13):
    """Draw the 4x4 matrix M[(u, v)] with row labels at the left and column labels on top; (x0, y0) is the top
    left corner of the cell (1, 1)."""
    if title:
        S.text(x0 + 2 * cw, y0 - 34, title, size=title_size, raw=True)
    for k, v in enumerate(V):
        S.text(x0 + k * cw + cw / 2, y0 - 12, str(v), size=11.5, color="var(--muted)")
        S.text(x0 - 12, y0 + k * ch + ch / 2, str(v), size=11.5, color="var(--muted)")
    for i, u in enumerate(V):
        for j, v in enumerate(V):
            x, y = x0 + j * cw, y0 + i * ch
            if (shade_row is not None and u == shade_row) or (shade_col is not None and v == shade_col):
                S.rect(x, y, cw, ch, stroke="none", fill="var(--muted)", fill_opacity=0.22, width=0)
            if (u, v) in hi:
                S.rect(x + 2, y + 2, cw - 4, ch - 4, rx=4, stroke="var(--accent)", fill="var(--accent)",
                       fill_opacity=0.18, width=1.2)
    for k in range(5):
        S.line(x0, y0 + k * ch, x0 + 4 * cw, y0 + k * ch, width=0.6, opacity=0.45)
        S.line(x0 + k * cw, y0, x0 + k * cw, y0 + 4 * ch, width=0.6, opacity=0.45)
    S.rect(x0, y0, 4 * cw, 4 * ch, stroke="currentColor", fill="none", width=1.1)
    for i, u in enumerate(V):
        for j, v in enumerate(V):
            val = M[(u, v)]
            S.text(x0 + j * cw + cw / 2, y0 + i * ch + ch / 2 + 1, num(val), size=13.5,
                   weight=600 if (u, v) in hi else None,
                   color="var(--muted)" if (val is None and muted_none) else "currentColor")


# ========================================================================== 1. the running example and its matrices
A = Automaton(640, 262, r=17, font_size=14)
draw_graph(A, 58, 64, 150, EX)
OV = SVG(640, 262)
matrix(OV, 322, 92, DIST, title="dist[<tspan font-style='italic'>u</tspan>, <tspan font-style='italic'>v</tspan>]")
matrix(OV, 494, 92, PRED, title="pred[<tspan font-style='italic'>u</tspan>, <tspan font-style='italic'>v</tspan>]")
save("a09-example", overlay_figure(A, OV,
    "<strong>The running example and its two output arrays.</strong> Six edges, two of them negative; the "
    "simple cycles have lengths 5 (2→3→2), 5 (3→4→3) and 2 (1→2→3→4→1), so there is no negative cycle. "
    "Row <i>u</i> of dist holds the distances from <i>u</i>; row <i>u</i> of pred holds the shortest-path tree "
    "rooted at <i>u</i> (pred[<i>u</i>, <i>v</i>] is the second-to-last vertex of the shortest path, – means "
    "Null). Two shortest paths beat a direct edge: 3→4→1→2 has length −2 against 1 for the edge 3→2, and "
    "4→1→2→3 has length −1 against 2 for 4→3.",
    alt="four-vertex weighted directed graph with its 4 by 4 distance and predecessor matrices"))

# ========================================================================== 2. reweighting
TREE = {(4, 1), (1, 2), (2, 3)}
R = Automaton(640, 286, r=17, font_size=14)
X1, Y1, SIDE = 70, 74, 170
draw_graph(R, X1, Y1, SIDE, EX, colors={e: "var(--accent)" for e in TREE},
           widths={e: 2.6 for e in TREE}, prefix="L")
R.state("s", X1 + SIDE / 2, Y1 + SIDE / 2, label="s", italic=True)
for v in V:
    tree = SPRED[v] == "s"
    R.edge("s", "L" + str(v), color="var(--accent)" if tree else "var(--muted)", width=2.6 if tree else 1.3,
           dash=None if tree else "5 4", label="0", mono=False, label_pos=0.42, label_dist=9,
           label_color="var(--muted)")
X2 = 410
draw_graph(R, X2, Y1, SIDE, EP, colors={e: "var(--accent)" for e in EP if EP[e] == 0},
           widths={e: 2.6 for e in EP if EP[e] == 0}, prefix="R")
OV = SVG(640, 286)
OFF = {1: (-30, -27), 2: (30, -27), 3: (30, 27), 4: (-30, 27)}
for v in V:
    cx, cy = POS[v]
    dx, dy = OFF[v]
    OV.text(X1 + cx * SIDE + dx, Y1 + cy * SIDE + dy, "π = " + num(PI[v]), size=12.5, halo=True,
            color="var(--accent)")
OV.text(X1 + SIDE / 2, 18, "G + s, weights w, prices π(v) = dist(s, v)", size=12.5, color="var(--muted)")
OV.text(X2 + SIDE / 2, 18, "G, reduced weights w′ = π(u) + w − π(v)", size=12.5, color="var(--muted)")
save("a09-reweighting", overlay_figure(R, OV,
    "<strong>Johnson’s reweighting of the running example.</strong> Left: a new vertex <i>s</i> with an edge "
    "of weight 0 to every vertex (dashed unless used). Bellman–Ford from <i>s</i> gives the prices "
    "π(1), π(2), π(3), π(4) = −3, −5, −1, 0, along the shortest-path tree <i>s</i>→4→1→2→3 (colored). "
    "Right: the reduced weights, all nonnegative; exactly the tree edges get weight 0. Every cycle keeps its "
    "length: 2→3→2 is 0 + 5, 3→4→3 is 2 + 3, and 1→2→3→4→1 is 0 + 0 + 2 + 0.",
    alt="the example graph with an added source and vertex prices, and the same graph with reduced weights"))

# ========================================================================== 3. Floyd-Warshall phases
CW, CH = 34, 26
F = SVG(600, 332)
slots = [(46, 64), (232, 64), (418, 64), (46, 226), (232, 226)]
for r, (x, y) in enumerate(slots):
    M = PH[r]
    changed = {k for k in M if r > 0 and M[k] != PH[r - 1][k]}
    title = ("before: <tspan font-style='italic'>w</tspan>(<tspan font-style='italic'>u</tspan>→"
             "<tspan font-style='italic'>v</tspan>)" if r == 0 else
             f"after phase <tspan font-style='italic'>r</tspan> = {r}")
    matrix(F, x, y, M, title=title, cw=CW, ch=CH, hi=changed, shade_row=r or None, shade_col=r or None)
# legend in the sixth slot
lx, ly = 420, 214
F.rect(lx, ly, 22, 16, stroke="none", fill="var(--muted)", fill_opacity=0.22, width=0)
F.text(lx + 30, ly + 8, "row and column r:", size=12, anchor="start")
F.text(lx + 30, ly + 24, "unchanged in phase r", size=12, anchor="start")
F.rect(lx + 2, ly + 44, 18, 14, rx=4, stroke="var(--accent)", fill="var(--accent)", fill_opacity=0.18, width=1.2)
F.text(lx + 30, ly + 51, "improved in phase r", size=12, anchor="start")
F.text(lx + 30, ly + 67, "(via vertex r)", size=12, anchor="start")
CHG = [sorted(k for k in PH[r] if PH[r][k] != PH[r - 1][k]) for r in range(1, 5)]
assert CHG == [[(4, 2)], [(1, 3), (4, 3)], [(1, 4), (2, 4)], [(2, 1), (3, 1), (3, 2)]]
save("a09-fw-phases", F.figure(
    "<strong>FloydWarshall on the running example, one matrix per phase.</strong> Entry (<i>u</i>, <i>v</i>) "
    "after phase <i>r</i> is the shortest path from <i>u</i> to <i>v</i> whose intermediate vertices are all at "
    "most <i>r</i>. Phase <i>r</i> tries the detour through <i>r</i>: dist[<i>u</i>, <i>v</i>] ← "
    "min{dist[<i>u</i>, <i>v</i>], dist[<i>u</i>, <i>r</i>] + dist[<i>r</i>, <i>v</i>]}. Phase 1 finds "
    "4→1→2 (−5); phase 2 finds 1→2→3 (2) and 4→1→2→3 (−1); phase 3 finds 1→2→3→4 (5) and 2→3→4 (7); "
    "phase 4 finds 2→3→4→1 (4), 3→4→1 (0) and 3→4→1→2 (−2). The last matrix is the distance array.",
    alt="five 4 by 4 matrices: the weight matrix and the Floyd-Warshall matrix after each of the four phases"))

# ========================================================================== 4. the recursive structure
S = SVG(640, 246)


def wavy(S, x1, y1, x2, y2, color="currentColor", width=1.6, amp=6, waves=3, arrow=True):
    """A gently wavy arrow from (x1, y1) to (x2, y2) (a path, not necessarily an edge)."""
    L = math.hypot(x2 - x1, y2 - y1)
    ux, uy = (x2 - x1) / L, (y2 - y1) / L
    nx, ny = -uy, ux
    k = 2 * waves
    d = f"M{x1:.1f},{y1:.1f}"
    for i in range(k):
        a, b = i / k, (i + 1) / k
        sgn = 1 if i % 2 == 0 else -1
        cx = x1 + (x2 - x1) * (a + b) / 2 + nx * amp * 2 * sgn
        cy = y1 + (y2 - y1) * (a + b) / 2 + ny * amp * 2 * sgn
        ex, ey = x1 + (x2 - x1) * b, y1 + (y2 - y1) * b
        if i == k - 1:
            ex, ey = ex - ux * 2.5, ey - uy * 2.5
        d += f" Q{cx:.1f},{cy:.1f} {ex:.1f},{ey:.1f}"
    S.path(d, color=color, width=width, arrow=arrow)


def node(S, x, y, lab, color="currentColor"):
    S.circle(x, y, 13, stroke=color, fill="var(--paper)", width=1.5)
    S.text(x, y + 1, lab, size=15, font=SERIF_IT, italic=True, color=color)


R0 = 13
# top: the path
node(S, 34, 46, "u")
node(S, 300, 46, "v")
wavy(S, 34 + R0 + 2, 46, 300 - R0 - 1, 46, amp=5, waves=4)
S.text(167, 22, "shortest path, intermediate vertices ≤ r", size=12.5, color="var(--muted)")
# either
S.text(14, 92, "either it avoids r:", size=12.5, anchor="start")
node(S, 34, 122, "u")
node(S, 300, 122, "v")
wavy(S, 34 + R0 + 2, 122, 300 - R0 - 1, 122, color="var(--accent2)", amp=5, waves=4)
S.text(167, 146, "≤ r − 1", size=12.5, color="var(--accent2)")
# or
S.text(14, 172, "or it passes through r once:", size=12.5, anchor="start")
node(S, 34, 206, "u")
node(S, 167, 206, "r", color="var(--hi)")
node(S, 300, 206, "v")
wavy(S, 34 + R0 + 2, 206, 167 - R0 - 1, 206, color="var(--accent)", amp=4, waves=2)
wavy(S, 167 + R0 + 2, 206, 300 - R0 - 1, 206, color="var(--accent)", amp=4, waves=2)
S.text(100, 232, "≤ r − 1", size=12.5, color="var(--accent)")
S.text(234, 232, "≤ r − 1", size=12.5, color="var(--accent)")
S.line(338, 14, 338, 236, width=0.8, opacity=0.4)
# right: the table dependency
GX, GY, C = 400, 40, 30
names_r = {2: "r", 4: "u"}
names_c = {2: "r", 5: "v"}
for i in range(6):
    for j in range(6):
        if i == 2 or j == 2:
            S.rect(GX + j * C, GY + i * C, C, C, stroke="none", fill="var(--muted)", fill_opacity=0.22, width=0)
for k in range(7):
    S.line(GX, GY + k * C, GX + 6 * C, GY + k * C, width=0.6, opacity=0.45)
    S.line(GX + k * C, GY, GX + k * C, GY + 6 * C, width=0.6, opacity=0.45)
S.rect(GX, GY, 6 * C, 6 * C, width=1.1)
for i, lab in names_r.items():
    S.text(GX - 12, GY + i * C + C / 2, lab, size=14, font=SERIF_IT, italic=True)
for j, lab in names_c.items():
    S.text(GX + j * C + C / 2, GY - 12, lab, size=14, font=SERIF_IT, italic=True)
S.text(GX + 2 * C + C / 2, GY + 2 * C + C / 2 + 1, "0", size=13)
for (i, j), col in [((4, 2), "var(--accent)"), ((2, 5), "var(--accent)"), ((4, 5), "var(--hi)")]:
    S.rect(GX + j * C + 3, GY + i * C + 3, C - 6, C - 6, rx=4, stroke=col, fill=col, fill_opacity=0.2, width=1.4)
cx = lambda j: GX + j * C + C / 2
cy = lambda i: GY + i * C + C / 2
S.path(f"M{cx(2) + 10},{cy(4)} L{cx(5) - 12},{cy(4)}", color="var(--accent)", width=1.5, arrow=True)
S.path(f"M{cx(5)},{cy(2) + 10} L{cx(5)},{cy(4) - 12}", color="var(--accent)", width=1.5, arrow=True)
S.text(GX + 3 * C, GY + 6 * C + 16, "dist[u, v] ← min{dist[u, v], dist[u, r] + dist[r, v]}", size=12)
save("a09-fw-structure", S.figure(
    "<strong>The recursive structure behind Floyd–Warshall.</strong> Left: a shortest path from <i>u</i> to "
    "<i>v</i> whose intermediate vertices are at most <i>r</i> either avoids <i>r</i>, or passes through "
    "<i>r</i> exactly once and splits there into two paths with intermediate vertices at most <i>r</i> − 1 "
    "(the book’s Figure 9.3). Right: in phase <i>r</i>, entry (<i>u</i>, <i>v</i>) reads entries (<i>u</i>, "
    "<i>r</i>) and (<i>r</i>, <i>v</i>), which lie in column <i>r</i> and row <i>r</i>. Those do not change "
    "during phase <i>r</i>, because dist[<i>r</i>, <i>r</i>] = 0 — so one matrix, updated in place, suffices.",
    alt="a path through intermediate vertices at most r split at vertex r, and the matrix cells read in phase r"))

# ========================================================================== 5. min-plus powers
W1 = wmatrix(EX)
W2 = minplus(W1, W1)
W3 = minplus(W2, W1)
W4 = minplus(W2, W2)
assert W3 == W4 == DIST and W2 != W3
M = SVG(580, 186)
xs = [40, 236, 432]
mats = [(W1, "<tspan font-style='italic'>W</tspan>", set()),
        (W2, "<tspan font-style='italic'>W</tspan>² = <tspan font-style='italic'>W</tspan> ⊗ "
             "<tspan font-style='italic'>W</tspan>", {k for k in W2 if W2[k] != W1[k]}),
        (W4, "<tspan font-style='italic'>W</tspan>⁴ = <tspan font-style='italic'>W</tspan>² ⊗ "
             "<tspan font-style='italic'>W</tspan>²", {k for k in W4 if W4[k] != W2[k]})]
for x, (Mx, title, hi) in zip(xs, mats):
    matrix(M, x, 62, Mx, title=title, hi=hi)
for x in xs[:2]:
    M.text(x + 4 * 34 + 30, 62 + 52, "→", size=20, color="var(--muted)")
M.text(290, 178, "at most 1, 2 and 4 edges; W³ = W⁴ = dist", size=12, color="var(--muted)")
CH2 = sorted(k for k in W2 if W2[k] != W1[k])
CH4 = sorted(k for k in W4 if W4[k] != W2[k])
assert CH2 == [(1, 3), (2, 4), (3, 1), (4, 2)] and CH4 == [(1, 4), (2, 1), (3, 2), (4, 3)]
save("a09-minplus", M.figure(
    "<strong>Min-plus powers of the weight matrix, by repeated squaring.</strong> <i>W</i> has the edge "
    "weights, 0 on the diagonal and ∞ for missing edges; entry (<i>u</i>, <i>v</i>) of the min-plus power "
    "<i>W</i><sup>ℓ</sup> is the shortest walk from <i>u</i> to <i>v</i> with at most ℓ edges. Colored entries "
    "improved since the previous matrix. Two squarings reach <i>W</i>⁴, which equals <i>W</i>³ because no "
    "shortest path needs more than <i>V</i> − 1 = 3 edges; computing <i>W</i>², <i>W</i>³ one product at a "
    "time is ShimbelAPSP.",
    alt="three 4 by 4 matrices: W, its min-plus square, and its fourth min-plus power"))
