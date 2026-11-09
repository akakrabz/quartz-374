#!/usr/bin/env python3
"""Figures for note H (linear programming). Writes tools/figs/nh-<name>.html; then run tools/assemble.py on
content/4-lecture-notes/h-linear-programming.md. Every vertex, value, distance and multiplier drawn here is computed
below (exact fractions) and asserted; tools/checks/nh.py re-checks the numbers independently."""
import itertools
import math
import os
from fractions import Fraction as Fr

from figlib import SVG, Automaton, SERIF_IT, SANS, fmt

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")
os.makedirs(OUT, exist_ok=True)


def save(name, html):
    with open(os.path.join(OUT, name + ".html"), "w", encoding="utf-8") as f:
        f.write(html + "\n")
    print("wrote", name)


class Plot(SVG):
    """An SVG with a linear map from LP coordinates (x right, y up) to pixels."""

    def __init__(self, w, h, x0, y0, scale):
        super().__init__(w, h)
        self.x0, self.y0, self.s = x0, y0, scale  # pixel position of the origin, pixels per unit

    def P(self, x, y):
        return self.x0 + float(x) * self.s, self.y0 - float(y) * self.s

    def seg(self, p, q, **kw):
        (a, b), (c, d) = self.P(*p), self.P(*q)
        self.line(a, b, c, d, **kw)

    def poly(self, pts, fill, opacity, stroke="none", width=0):
        d = "M" + " L".join(f"{fmt(self.P(*p)[0])},{fmt(self.P(*p)[1])}" for p in pts) + " Z"
        self.add(f'<path d="{d}" fill="{fill}" fill-opacity="{opacity}" stroke="{stroke}" stroke-width="{width}"/>')

    def dot(self, p, r=3.6, color="currentColor", fill=None):
        x, y = self.P(*p)
        self.circle(x, y, r, stroke=color, fill=fill or color, width=1.2)

    def lab(self, p, s, dx=0, dy=0, **kw):
        x, y = self.P(*p)
        kw.setdefault("halo", True)
        self.text(x + dx, y + dy, s, **kw)

    def axes(self, xmax, ymax, xmin=-0.3, ymin=-0.3, ticks=True):
        self.seg((xmin, 0), (xmax, 0), width=1.1, arrow=True, color="var(--muted)")
        self.seg((0, ymin), (0, ymax), width=1.1, arrow=True, color="var(--muted)")
        self.lab((xmax, 0), "x", dx=-4, dy=13, font=SERIF_IT, italic=True, size=14, color="var(--muted)")
        self.lab((0, ymax), "y", dx=-11, dy=5, font=SERIF_IT, italic=True, size=14, color="var(--muted)")
        if ticks:
            for k in range(1, int(xmax)):
                x, y = self.P(k, 0)
                self.line(x, y - 3, x, y + 3, width=1, color="var(--muted)")
            for k in range(1, int(ymax)):
                x, y = self.P(0, k)
                self.line(x - 3, y, x + 3, y, width=1, color="var(--muted)")


def line_in_box(a, b, c, xmin, xmax, ymin, ymax):
    """The segment of the line a x + b y = c inside the box."""
    pts = []
    if b != 0:
        for x in (xmin, xmax):
            y = (c - a * x) / b
            if ymin - 1e-9 <= y <= ymax + 1e-9:
                pts.append((x, y))
    if a != 0:
        for y in (ymin, ymax):
            x = (c - b * y) / a
            if xmin - 1e-9 <= x <= xmax + 1e-9:
                pts.append((x, y))
    pts = sorted(set((round(float(p[0]), 9), round(float(p[1]), 9)) for p in pts))
    return pts[0], pts[-1]


# =========================================================================== the 2D example LP
# max 3x + 2y  s.t.  x + y <= 4,  x + 2y <= 6,  x <= 3,  x, y >= 0
CONS = [((1, 1), 4), ((1, 2), 6), ((1, 0), 3), ((-1, 0), 0), ((0, -1), 0)]
C = (3, 2)
verts = set()
for (a1, b1), (a2, b2) in itertools.combinations(CONS, 2):
    det = Fr(a1[0] * a2[1] - a1[1] * a2[0])
    if det == 0:
        continue
    x = (b1 * a2[1] - b2 * a1[1]) / det
    y = (a1[0] * b2 - a2[0] * b1) / det
    if all(a[0] * x + a[1] * y <= bb for a, bb in CONS):
        verts.add((x, y))
POLY = [(0, 0), (3, 0), (3, 1), (2, 2), (0, 3)]
assert verts == {(Fr(p[0]), Fr(p[1])) for p in POLY}
VAL = {p: C[0] * p[0] + C[1] * p[1] for p in POLY}
assert VAL == {(0, 0): 0, (3, 0): 9, (3, 1): 11, (2, 2): 10, (0, 3): 6}
OPT = max(POLY, key=lambda p: VAL[p])
assert OPT == (3, 1)
# the dual: c = 2*(1,1) + 0*(1,2) + 1*(1,0)
Y = (2, 0, 1)
assert tuple(Y[0] * CONS[0][0][k] + Y[1] * CONS[1][0][k] + Y[2] * CONS[2][0][k] for k in range(2)) == C
assert Y[0] * 4 + Y[1] * 6 + Y[2] * 3 == 11


def base_plot(w, h, x0, y0, s, xmax, ymax, labels=True):
    S = Plot(w, h, x0, y0, s)
    S.poly(POLY, "var(--accent)", 0.13)
    S.axes(xmax, ymax)
    # constraint lines across the view
    for ((a, b), c), txt, (lp, dx, dy) in [
            (CONS[0], "x + y ≤ 4", ((0.75, 3.25), 34, -8)),
            (CONS[1], "x + 2y ≤ 6", ((4.2, 0.9), 10, -16)),
            (CONS[2], "x ≤ 3", ((3, 3.35), 0, -8))]:
        p, q = line_in_box(a, b, c, -0.25, xmax - 0.25, -0.25, ymax - 0.25)
        S.seg(p, q, width=1.2, color="currentColor", opacity=0.55)
        if labels:
            S.lab(lp, txt, dx=dx, dy=dy, size=13.5, color="currentColor", font=SERIF_IT, italic=True)
    S.poly(POLY, "none", 1, stroke="currentColor", width=1.8)
    return S


# --------------------------------------------------------------------------- 1. geometry
S = base_plot(420, 300, 52, 250, 55, 5.4, 4.2)
# level line of the optimum, 3x + 2y = 11, and the objective direction
p, q = line_in_box(3, 2, 11, 2.35, 4.6, -0.2, 3.9)
S.seg(p, q, width=1.4, color="var(--hi)", dash="6 4")
S.lab((4.25, -0.55), "3x + 2y = 11", dx=0, dy=6, size=12.5, color="var(--hi)")
S.seg((0.55, 1.15), (0.55 + 0.5 * 3 / math.hypot(3, 2) * 1.6, 1.15 + 0.5 * 2 / math.hypot(3, 2) * 1.6),
      width=2.2, color="var(--accent2)", arrow=True)
S.lab((0.62, 1.15), "c = (3, 2)", dx=-2, dy=16, size=12.5, color="var(--accent2)", anchor="start")
offs = {(0, 0): (-14, 13), (3, 0): (10, 14), (3, 1): (12, -10), (2, 2): (10, -12), (0, 3): (-16, -8)}
for p in POLY:
    S.dot(p, r=4.2 if p == OPT else 3.4, color="var(--hi)" if p == OPT else "currentColor")
    S.lab(p, f"{VAL[p]}", dx=offs[p][0], dy=offs[p][1], size=12.5,
          color="var(--hi)" if p == OPT else "currentColor", weight="600" if p == OPT else None)
S.lab(OPT, "(3, 1)", dx=34, dy=6, size=12.5, color="var(--hi)")
save("nh-geometry", S.figure(
    "<strong>The feasible region of a two-variable LP.</strong> Maximize 3<i>x</i> + 2<i>y</i> subject to "
    "<i>x</i> + <i>y</i> ≤ 4, <i>x</i> + 2<i>y</i> ≤ 6, <i>x</i> ≤ 3 and <i>x</i>, <i>y</i> ≥ 0: the shaded pentagon "
    "is the intersection of five halfplanes. The numbers at its vertices are the objective values; the objective "
    "grows in the direction <i>c</i>, and the dashed level line 3<i>x</i> + 2<i>y</i> = 11 touches the region only "
    "at the optimal vertex (3, 1).",
    alt="a pentagon with vertices (0,0), (3,0), (3,1), (2,2), (0,3); objective values 0, 9, 11, 10, 6; the optimum "
        "(3,1) is highlighted"))

# --------------------------------------------------------------------------- 2. infeasible (Figure H.2)
S = Plot(360, 290, 40, 250, 88)
xmax, ymax = 3.4, 2.7
S.poly([(0, 0), (Fr(1, 2), 0), (0, 1)], "var(--accent)", 0.30)
S.poly([(2, 0), (3.25, 0), (3.25, 2.55), (0, 2.55), (0, 2)], "var(--accent2)", 0.13)
S.axes(xmax, ymax)
p, q = line_in_box(2, 1, 1, -0.15, 1.0, -0.2, 1.2)
S.seg(p, q, width=1.6, color="var(--accent)")
p, q = line_in_box(1, 1, 2, -0.2, 2.2, -0.2, 2.2)
S.seg(p, q, width=1.6, color="var(--accent2)")
S.lab((0.47, 0.2), "2x + y ≤ 1", dx=0, dy=0, size=13.5, color="var(--accent)", anchor="start", font=SERIF_IT,
      italic=True)
S.lab((1.85, 1.55), "x + y ≥ 2", dx=0, dy=0, size=13.5, color="var(--accent2)", anchor="start", font=SERIF_IT,
      italic=True)
# assertions: the triangle lies strictly below the line x + y = 2
assert all(float(a) + float(b) <= 1 for a, b in [(0, 0), (0.5, 0), (0, 1)])
save("nh-infeasible", S.figure(
    "<strong>An infeasible LP (the note’s Figure H.2).</strong> In the quadrant <i>x</i>, <i>y</i> ≥ 0 the "
    "constraint 2<i>x</i> + <i>y</i> ≤ 1 leaves the small triangle, where <i>x</i> + <i>y</i> ≤ 1; the constraint "
    "<i>x</i> + <i>y</i> ≥ 2 leaves the region beyond the line <i>x</i> + <i>y</i> = 2. They do not meet, so no "
    "objective can be optimized.",
    alt="two disjoint shaded regions in the first quadrant: a small triangle under 2x + y = 1 and the region above "
        "x + y = 2"))

# --------------------------------------------------------------------------- 3. the shortest-path pair
V = ["s", "a", "b", "c", "t"]
L = {("s", "a"): 2, ("s", "b"): 5, ("a", "b"): 1, ("a", "c"): 4, ("b", "c"): 1, ("b", "t"): 6, ("c", "t"): 2}
dist = {v: math.inf for v in V}
dist["s"] = 0
for _ in V:
    for (u, v), w in L.items():
        dist[v] = min(dist[v], dist[u] + w)
assert dist == {"s": 0, "a": 2, "b": 3, "c": 4, "t": 6}
tight = {e for e, w in L.items() if dist[e[1]] - dist[e[0]] == w}
assert tight == {("s", "a"), ("a", "b"), ("b", "c"), ("c", "t")}
POS = {"s": (48, 140), "a": (178, 60), "b": (178, 222), "c": (318, 140), "t": (452, 140)}


class Net(Automaton):
    def __init__(self, w, h, r=17):
        super().__init__(w, h, r=r)
        self.LAB = SVG(w, h)


A = Net(510, 290)
for v, (x, y) in POS.items():
    A.state(v, x, y, hi=False)
LOFF = {("s", "a"): (-14, -9), ("s", "b"): (-36, 12), ("a", "b"): (-11, 0), ("a", "c"): (34, -12),
        ("b", "c"): (-6, -12), ("b", "t"): (40, 38), ("c", "t"): (0, -12)}
BEND = {("b", "t"): -22}
for e, w in L.items():
    on = e in tight
    A.edge(*e, color="var(--hi)" if on else "currentColor", width=2.6 if on else 1.5, bend=BEND.get(e, 0))
    (x1, y1), (x2, y2) = POS[e[0]], POS[e[1]]
    dx, dy = LOFF[e]
    sl = w - (dist[e[1]] - dist[e[0]])
    txt = f"{w}" if on else f"{w}  (slack {sl})"
    A.LAB.text((x1 + x2) / 2 + dx, (y1 + y2) / 2 + dy, txt, size=13, halo=True,
               color="var(--hi)" if on else "currentColor", weight="600" if on else None)
for v, (x, y) in POS.items():
    dy = -30 if v in ("a", "c", "s", "t") else 31
    A.LAB.text(x, y + dy, f"{dist[v]}", size=13.5, halo=True, color="var(--accent2)", weight="600")
svg = A.svg("the shortest-path example graph with distances at the vertices and the shortest path highlighted")
svg = svg.replace("</svg>", "".join(A.LAB.items) + "</svg>")
cap = ("<strong>Both shortest-path LPs on one graph.</strong> Numbers on edges are lengths; the bold numbers at "
       "the vertices are the optimal <i>dist</i> values of the maximization LP, 0, 2, 3, 4, 6 — the unique optimum. "
       "The highlighted edges are tight (<i>dist</i>(<i>v</i>) − <i>dist</i>(<i>u</i>) = ℓ(<i>u</i>→<i>v</i>)); "
       "the minimization LP puts one unit of flow on exactly these edges, the path <i>s</i> <i>a</i> <i>b</i> "
       "<i>c</i> <i>t</i> of length 6, and nothing on the three loose edges.")
html = f'<figure class="cs-fig">{svg}<figcaption>{cap}</figcaption></figure>'
save("nh-shortest-path", html.replace("\n", " "))

# --------------------------------------------------------------------------- 4. the dual as forces
S = base_plot(440, 300, 52, 250, 55, 5.4, 4.2, labels=False)
for txt, lp, dx, dy in [("x + y ≤ 4", (0.75, 3.25), 34, -8), ("x ≤ 3", (3, 3.35), 0, -8),
                        ("x + 2y ≤ 6", (4.75, 0.62), 4, 14)]:
    S.lab(lp, txt, dx=dx, dy=dy, size=13.5, color="currentColor", font=SERIF_IT, italic=True)
k = 0.55
o = OPT
n1 = (o[0] + k * Y[0] * 1, o[1] + k * Y[0] * 1)        # 2 * (1, 1)
n3 = (o[0] + k * Y[2] * 1, o[1] + k * Y[2] * 0)        # 1 * (1, 0)
cc = (o[0] + k * C[0], o[1] + k * C[1])                 # (3, 2)
assert abs((n1[0] - o[0]) + (n3[0] - o[0]) - (cc[0] - o[0])) < 1e-12
assert abs((n1[1] - o[1]) + (n3[1] - o[1]) - (cc[1] - o[1])) < 1e-12
S.seg(n1, cc, width=1.1, dash="4 3", color="var(--muted)")
S.seg(n3, cc, width=1.1, dash="4 3", color="var(--muted)")
S.seg(o, n1, width=2.2, color="var(--accent)", arrow=True)
S.seg(o, n3, width=2.2, color="var(--accent)", arrow=True)
S.seg(o, cc, width=2.6, color="var(--accent2)", arrow=True)
S.dot(o, r=4.2, color="var(--hi)")
S.lab(n1, "2 · (1, 1)", dx=-34, dy=-10, size=13, color="var(--accent)")
S.lab(n3, "1 · (1, 0)", dx=18, dy=16, size=13, color="var(--accent)")
S.lab(cc, "c = (3, 2)", dx=40, dy=-2, size=13, color="var(--accent2)")
S.lab(o, "(3, 1)", dx=-26, dy=12, size=13, color="var(--hi)")
save("nh-dual-forces", S.figure(
    "<strong>The dual solution as forces at the optimum.</strong> At (3, 1) the constraints <i>x</i> + <i>y</i> ≤ 4 "
    "and <i>x</i> ≤ 3 are tight; their outward normals (1, 1) and (1, 0) combine to the objective vector, "
    "<i>c</i> = (3, 2) = 2 · (1, 1) + 1 · (1, 0). The coefficients are the optimal dual variables, "
    "<i>y</i> = (2, 0, 1): the loose constraint <i>x</i> + 2<i>y</i> ≤ 6 gets 0, and the dual value "
    "4 · 2 + 3 · 1 = 11 equals the primal optimum. (Arrows drawn at 0.55 scale.)",
    alt="the pentagon with the optimum (3,1); arrows 2 times (1,1) and 1 times (1,0) add up to the objective vector "
        "(3,2)"))
