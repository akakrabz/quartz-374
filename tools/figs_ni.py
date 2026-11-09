#!/usr/bin/env python3
"""Figures for note I (linear programming algorithms). Writes tools/figs/ni-<name>.html; then run
tools/assemble.py on content/4-lecture-notes/i-linear-programming-algorithms.md. The simplex runs and the network
simplex pivots drawn here are computed below (exact fractions) and asserted; tools/checks/ni.py re-checks them."""
import itertools
import os
from fractions import Fraction as Fr

from figlib import SVG, Automaton, SERIF_IT, fmt

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")
os.makedirs(OUT, exist_ok=True)


def save(name, html):
    with open(os.path.join(OUT, name + ".html"), "w", encoding="utf-8") as f:
        f.write(html + "\n")
    print("wrote", name)


# =========================================================================== 1. primal and dual simplex in 2D
# max x + 5y  s.t.  x + 3y <= 9,  2x + 3y <= 12,  x + y <= 7,  x, y >= 0   (n = 3, d = 2)
G = [(1, 3), (2, 3), (1, 1), (-1, 0), (0, -1)]
H = [9, 12, 7, 0, 0]
C = (1, 5)
NAMES = ["x + 3y ≤ 9", "2x + 3y ≤ 12", "x + y ≤ 7", "x ≥ 0", "y ≥ 0"]


def loc(B):
    i, j = B
    (a, b), (c, d) = G[i], G[j]
    det = Fr(a * d - b * c)
    return ((H[i] * d - H[j] * b) / det, (a * H[j] - c * H[i]) / det)


def mult(B):
    i, j = B
    (a, b), (c, d) = G[i], G[j]
    det = Fr(a * d - b * c)
    return ((C[0] * d - C[1] * c) / det, (a * C[1] - b * C[0]) / det)


BASES = [B for B in itertools.combinations(range(5), 2)]
assert all(G[i][0] * G[j][1] - G[i][1] * G[j][0] != 0 for i, j in BASES)  # no parallel pair
feas = {B: all(G[k][0] * loc(B)[0] + G[k][1] * loc(B)[1] <= H[k] for k in range(5)) for B in BASES}
lopt = {B: all(m > 0 for m in mult(B)) for B in BASES}
assert all(m != 0 for B in BASES for m in mult(B))
val = {B: C[0] * loc(B)[0] + C[1] * loc(B)[1] for B in BASES}
assert len(set(val.values())) == len(val)


def nbrs(B):
    for i in B:
        for k in range(5):
            if k not in B:
                yield tuple(sorted((set(B) - {i}) | {k}))


# primal: from the origin, always the improving feasible neighbor with the SMALLER gain (to show a long run)
B = (3, 4)
primal = [B]
while not lopt[B]:
    B = min((X for X in nbrs(B) if feas[X] and val[X] > val[B]), key=lambda X: val[X])
    primal.append(B)
# dual: from the locally optimal vertex of largest value, always the locally optimal neighbor with the smaller drop
B = max((X for X in BASES if lopt[X]), key=lambda X: val[X])
dual = [B]
while not feas[B]:
    B = max((X for X in nbrs(B) if lopt[X] and val[X] < val[B]), key=lambda X: val[X])
    dual.append(B)
P_PTS = [loc(B) for B in primal]
D_PTS = [loc(B) for B in dual]
assert P_PTS == [(0, 0), (6, 0), (3, 2), (0, 3)], P_PTS
assert D_PTS == [(0, 7), (0, 4), (0, 3)], D_PTS
assert [val[B] for B in primal] == [0, 6, 13, 15] and [val[B] for B in dual] == [35, 20, 15]
OPTB = primal[-1]
assert dual[-1] == OPTB and feas[OPTB] and lopt[OPTB]
assert sum(feas.values()) == 4 and sum(lopt.values()) == 3


class Plot(SVG):
    """LP coordinates -> pixels, with the y-axis pointing DOWN, so that the objective c = (1, 5) points down."""

    def __init__(self, w, h, x0, y0, s):
        super().__init__(w, h)
        self.x0, self.y0, self.s = x0, y0, s

    def P(self, x, y):
        return self.x0 + float(x) * self.s, self.y0 + float(y) * self.s

    def seg(self, p, q, **kw):
        (a, b), (c, d) = self.P(*p), self.P(*q)
        self.line(a, b, c, d, **kw)

    def poly(self, pts, fill, opacity):
        d = "M" + " L".join(f"{fmt(self.P(*p)[0])},{fmt(self.P(*p)[1])}" for p in pts) + " Z"
        self.add(f'<path d="{d}" fill="{fill}" fill-opacity="{opacity}" stroke="none"/>')


S = Plot(540, 400, 125, 80, 31)
XMIN, XMAX, YMIN, YMAX = -0.8, 9.7, -2.3, 9.0
S.poly([(0, 0), (6, 0), (3, 2), (0, 3)], "var(--accent)", 0.14)
# the five lines, clipped to the box
for k, ((a, b), h) in enumerate(zip(G, H)):
    pts = []
    if b != 0:
        for x in (XMIN, XMAX):
            y = (h - a * x) / b
            if YMIN <= y <= YMAX:
                pts.append((x, y))
    if a != 0:
        for y in (YMIN, YMAX):
            x = (h - b * y) / a
            if XMIN <= x <= XMAX:
                pts.append((x, y))
    pts = sorted(set(pts))
    S.seg(pts[0], pts[-1], width=1.1, color="currentColor", opacity=0.5)
LABPOS = {0: ((-0.8, Fr(49, 15)), -5, 0, "end"), 1: ((-0.8, Fr(68, 15)), -5, 0, "end"),
          2: ((-0.8, Fr(39, 5)), -5, 0, "end"), 3: ((0, 9.0), 6, -4, "start"), 4: ((9.7, 0), -2, -10, "end")}
for k, (p, dx, dy, anc) in LABPOS.items():
    x, y = S.P(*p)
    S.text(x + dx, y + dy, NAMES[k], size=12.5, font=SERIF_IT, italic=True, anchor=anc, halo=True)
# paths
for path, col, dash, off in [(P_PTS, "var(--accent)", None, 0), (D_PTS, "var(--accent2)", "6 4", -9)]:
    for p, q in zip(path, path[1:]):
        (x1, y1), (x2, y2) = S.P(*p), S.P(*q)
        ox = off if x1 == x2 else 0
        oy = off if y1 == y2 else 0
        L = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        ux, uy = (x2 - x1) / L, (y2 - y1) / L
        S.line(x1 + ox + ux * 7, y1 + oy + uy * 7, x2 + ox - ux * 8, y2 + oy - uy * 8, color=col, width=2.6,
               arrow=True, dash=dash)
# vertices: filled = feasible, ring = locally optimal
for B in BASES:
    x, y = S.P(*loc(B))
    if B == OPTB:
        S.circle(x, y, 6.5, stroke="var(--hi)", fill="var(--hi)", width=1.6)
    elif feas[B]:
        S.circle(x, y, 4.2, stroke="var(--accent)", fill="var(--accent)", width=1.2)
    elif lopt[B]:
        S.circle(x, y, 5, stroke="var(--accent2)", fill="var(--paper)", width=2)
    else:
        S.circle(x, y, 3, stroke="currentColor", fill="var(--paper)", width=1.1)
VOFF = {(0, 0): (-8, -11, "end"), (6, 0): (6, -11, "start"), (3, 2): (9, 10, "start"), (0, 3): (12, 4, "start"),
        (0, 4): (12, 6, "start"), (0, 7): (12, 4, "start")}
for B in set(primal) | set(dual):
    p = loc(B)
    x, y = S.P(*p)
    dx, dy, anc = VOFF[p]
    col = "var(--hi)" if B == OPTB else ("var(--accent)" if feas[B] else "var(--accent2)")
    S.text(x + dx, y + dy, f"({p[0]}, {p[1]}): {val[B]}", size=12.5, anchor=anc, halo=True, color=col,
           weight="600" if B == OPTB else None)
# objective arrow and legend
x, y = S.P(6.6, 3.0)
S.line(x, y, x + 0.20 * 31 * 1, y + 0.20 * 31 * 5, color="currentColor", width=2, arrow=True)
S.text(x + 12, y + 14, "c = (1, 5)", size=12.5, anchor="start", halo=True)
LX, LY = 300, 296
S.line(LX, LY, LX + 30, LY, color="var(--accent)", width=2.6, arrow=True)
S.text(LX + 38, LY, "PrimalSimplex", size=12.5, anchor="start")
S.line(LX, LY + 21, LX + 30, LY + 21, color="var(--accent2)", width=2.6, arrow=True, dash="6 4")
S.text(LX + 38, LY + 21, "DualSimplex", size=12.5, anchor="start")
S.circle(LX + 6, LY + 44, 4.2, stroke="var(--accent)", fill="var(--accent)", width=1.2)
S.text(LX + 16, LY + 44, "feasible", size=12.5, anchor="start")
S.circle(LX + 80, LY + 44, 5, stroke="var(--accent2)", fill="var(--paper)", width=2)
S.text(LX + 91, LY + 44, "locally optimal", size=12.5, anchor="start")
S.circle(LX + 6, LY + 66, 3, stroke="currentColor", fill="var(--paper)", width=1.1)
S.text(LX + 16, LY + 66, "neither", size=12.5, anchor="start")
S.circle(LX + 80, LY + 66, 6.5, stroke="var(--hi)", fill="var(--hi)", width=1.6)
S.text(LX + 91, LY + 66, "both: the optimum", size=12.5, anchor="start")
for (lx, ly, t) in [(XMAX, 0, "x"), (0, YMAX, "y")]:
    pass
save("ni-simplex-paths", S.figure(
    "<strong>Falling marble and rising bubble.</strong> The arrangement of the five constraint lines of "
    "max <i>x</i> + 5<i>y</i> s.t. <i>x</i> + 3<i>y</i> ≤ 9, 2<i>x</i> + 3<i>y</i> ≤ 12, <i>x</i> + <i>y</i> ≤ 7, "
    "<i>x</i>, <i>y</i> ≥ 0, drawn with the <i>y</i>-axis pointing down so that the objective <i>c</i> points down, as "
    "in the note’s picture; each vertex (basis) is labeled with its value. Solid: PrimalSimplex from the origin "
    "walks down through feasible vertices (shaded region), 0 → 6 → 13 → 15, here always taking the smaller of the "
    "available improvements. Dashed: DualSimplex from the locally optimal vertex (0, 7) — on the redundant line "
    "<i>x</i> + <i>y</i> = 7 — rises through locally optimal, infeasible vertices, 35 → 20 → 15. Both stop at the "
    "only vertex that is feasible and locally optimal, the optimum (0, 3).",
    alt="the arrangement of five lines; a solid path along the feasible polygon from the origin to (0,3) and a "
        "dashed path down the y-axis from (0,7) to (0,3)"))

# =========================================================================== 2. network simplex pivots
VV = ["a", "b", "c", "d"]
BAL = {"a": -5, "b": 2, "c": 1, "d": 2}
EE = [("a", "b"), ("a", "c"), ("b", "c"), ("b", "d"), ("c", "d")]
COST = {("a", "b"): 2, ("a", "c"): 5, ("b", "c"): 1, ("b", "d"): 4, ("c", "d"): 2}
assert sum(BAL.values()) == 0
assert all(sum(BAL[v] for v in S_) != 0 for k in range(1, 4) for S_ in itertools.combinations(VV, k))


def side(T, e):
    """vertices of the component of T - e containing the head of e."""
    adj = {v: set() for v in VV}
    for f in T:
        if f != e:
            adj[f[0]].add(f[1]); adj[f[1]].add(f[0])
    seen, st = {e[1]}, [e[1]]
    while st:
        u = st.pop()
        for w in adj[u] - seen:
            seen.add(w); st.append(w)
    return seen


def flows(T):
    return {e: (sum(BAL[v] for v in side(T, e)) if e in T else 0) for e in EE}


def pots(T):
    pi = {"a": 0}
    while len(pi) < 4:
        for (u, v) in T:
            if u in pi and v not in pi:
                pi[v] = pi[u] + COST[(u, v)]
            elif v in pi and u not in pi:
                pi[u] = pi[v] - COST[(u, v)]
    return pi


def slacks(T):
    pi = pots(T)
    return {e: COST[e] + pi[e[0]] - pi[e[1]] for e in EE}


def cost(T):
    f = flows(T)
    return sum(COST[e] * f[e] for e in EE)


T0 = [("a", "b"), ("a", "c"), ("b", "d")]
runs = [T0]
T = T0
pivots = []
while True:
    f, s = flows(T), slacks(T)
    assert all(f[e] >= 0 for e in T)
    neg = [e for e in EE if e not in T and s[e] < 0]
    if not neg:
        break
    ein = min(neg, key=lambda e: s[e])
    # cycle: ein then the tree path from head(ein) back to tail(ein); backward tree edges lose flow
    u, v = ein
    # tree path v -> u
    adj = {x: [] for x in VV}
    for e in T:
        adj[e[0]].append((e[1], e, +1)); adj[e[1]].append((e[0], e, -1))
    prev = {v: None}
    st = [v]
    while st:
        x = st.pop()
        for y, e, sg in adj[x]:
            if y not in prev:
                prev[y] = (x, e, sg); st.append(y)
    path, x = [], u
    while prev[x] is not None:
        px, e, sg = prev[x]
        path.append((e, sg)); x = px
    back = [e for e, sg in path if sg < 0]
    eout = min(back, key=lambda e: f[e])
    pivots.append((ein, eout, s[ein], f[eout]))
    T2 = [e for e in T if e != eout] + [ein]
    assert cost(T2) == cost(T) + f[eout] * s[ein]
    T = T2
    runs.append(T)
assert [cost(T) for T in runs] == [21, 19, 17]
assert pivots == [(("b", "c"), ("a", "c"), -2, 1), (("c", "d"), ("b", "d"), -1, 2)]
assert all(x >= 0 for x in slacks(runs[-1]).values())

POS = {"a": (34, 104), "b": (118, 40), "c": (118, 168), "d": (200, 104)}
PW = 228


class Panel(Automaton):
    pass


A = Automaton(3 * PW, 250, r=14)
LAB = SVG(3 * PW, 250)
LOFF = {("a", "b"): (-14, -10), ("a", "c"): (-14, 10), ("b", "c"): (-2, 0), ("b", "d"): (14, -10),
        ("c", "d"): (14, 10)}
for k, T in enumerate(runs):
    ox = k * PW
    f, s = flows(T), slacks(T)
    for v, (x, y) in POS.items():
        A.state(f"{v}{k}", ox + x, y, label=v)
        bx = {"a": -2, "b": 0, "c": 0, "d": 2}[v]
        by = {"a": -24, "b": -24, "c": 25, "d": -24}[v]
        LAB.text(ox + x + bx, y + by, f"{BAL[v]:+d}".replace("-", "−"), size=11.5, color="var(--muted)", halo=True)
    ein = pivots[k][0] if k < len(pivots) else None
    eout = pivots[k][1] if k < len(pivots) else None
    for e in EE:
        u, v = e
        if e in T:
            col = "var(--accent2)" if e == eout else "var(--accent)"
            A.edge(f"{u}{k}", f"{v}{k}", color=col, width=2.6)
            txt = f"{f[e]}"
        else:
            col = "var(--hi)" if e == ein else "var(--muted)"
            A.edge(f"{u}{k}", f"{v}{k}", color=col, width=1.6 if e != ein else 2.2, dash="5 4")
            txt = (f"{s[e]:+d}" if s[e] else "0").replace("-", "−")
        (x1, y1), (x2, y2) = POS[u], POS[v]
        dx, dy = LOFF[e]
        if e == ("b", "c"):
            dx = -12 if e in T else 12
        LAB.text(ox + (x1 + x2) / 2 + dx, (y1 + y2) / 2 + dy, txt, size=12.5, halo=True,
                 color=col if col != "var(--muted)" else "currentColor", weight="600")
    title = ["start: cost 21", "after pivot 1: cost 19", "after pivot 2: cost 17, optimal"][k]
    LAB.text(ox + 118, 222, title, size=12.5, halo=True)
    if k < len(pivots):
        sub = f"in {pivots[k][0][0]}→{pivots[k][0][1]}, out {pivots[k][1][0]}→{pivots[k][1][1]}"
        LAB.text(ox + 118, 240, sub, size=12, halo=True, color="var(--muted)")
svg = A.svg("three spanning trees of a four-vertex transshipment network, with tree flows and non-tree slacks")
svg = svg.replace("</svg>", "".join(LAB.items) + "</svg>")
cap = ("<strong>Primal network simplex on a transshipment network.</strong> Balances in grey (supply −5 at "
       "<i>a</i>, demands 2, 1, 2); costs <i>a</i>→<i>b</i> 2, <i>a</i>→<i>c</i> 5, <i>b</i>→<i>c</i> 1, "
       "<i>b</i>→<i>d</i> 4, <i>c</i>→<i>d</i> 2. Solid edges form the spanning tree <i>T</i> and carry "
       "flow<sub><i>T</i></sub> (the total balance on the head side); dashed edges are free of flow and carry "
       "slack<sub><i>T</i></sub> (the cost of their fundamental cycle). Each pivot brings in a negative-slack edge "
       "(red) and pushes flow around its cycle until a backward tree edge (green) empties: the cost drops by "
       "flow · |slack|, 21 − 1·2 = 19, then 19 − 2·1 = 17. With every slack ≥ 0 and every flow ≥ 0 the tree is "
       "optimal.")
html = f'<figure class="cs-fig">{svg}<figcaption>{cap}</figcaption></figure>'
save("ni-network-pivot", html.replace("\n", " "))
