#!/usr/bin/env python3
"""Figures for the Chapter 12 exercises page (content/2-algorithms/12-np-hardness-exercises.md). Writes
tools/figs/a12x-<name>.html; then run tools/assemble.py on the page. Every highlighted cycle, path, dominating set and
puzzle solution is built here by the page's reduction and asserted to be what the caption says; tools/checks/a12x.py
re-checks the same examples by brute force."""
import itertools
import math
import os
from figlib import SVG, SERIF_IT, SANS, MONO

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")
os.makedirs(OUT, exist_ok=True)


def save(name, html):
    with open(os.path.join(OUT, name + ".html"), "w", encoding="utf-8") as f:
        f.write(html + "\n")
    print("wrote", name)


def seg(S, p, q, r1, r2, **kw):
    (x1, y1), (x2, y2) = p, q
    L = math.hypot(x2 - x1, y2 - y1)
    ux, uy = (x2 - x1) / L, (y2 - y1) / L
    S.line(x1 + ux * r1, y1 + uy * r1, x2 - ux * r2, y2 - uy * r2, **kw)


def node(S, p, r, label="", size=15, italic=True, stroke="currentColor", fill="var(--paper)", width=1.5,
         color="currentColor", font=SERIF_IT):
    S.circle(p[0], p[1], r, stroke=stroke, fill=fill, width=width)
    if label:
        S.text(p[0], p[1] + 1, label, size=size, font=font, italic=italic, color=color)


HI = dict(width=2.8, color="var(--hi)")
THIN = dict(width=1.3, color="currentColor")
MUTED = dict(width=1.3, color="var(--muted)", dash="5 4")

# =========================================================================== 1. Exercise 12.8(b): split vertices
DV = ["a", "b", "c"]
DA = [("a", "b"), ("b", "c"), ("c", "a"), ("a", "c")]
HC = ["a", "b", "c"]                       # directed Hamiltonian cycle a -> b -> c -> a
assert all((HC[i], HC[(i + 1) % 3]) in DA for i in range(3))
# undirected image: v_in v_mid v_out, and u_out v_in per arc
UE = [((v, "in"), (v, "mid")) for v in DV] + [((v, "mid"), (v, "out")) for v in DV] + \
     [((u, "out"), (v, "in")) for u, v in DA]
cyc = []
for v in HC:
    cyc += [(v, "in"), (v, "mid"), (v, "out")]
cyc_edges = {frozenset((cyc[i], cyc[(i + 1) % len(cyc)])) for i in range(len(cyc))}
assert cyc_edges <= {frozenset(e) for e in UE} and len(set(cyc)) == 9

S = SVG(620, 280)
# left: the directed graph
L = {"a": (110, 58), "b": (176, 196), "c": (44, 196)}
r = 17
for (u, v) in DA:
    hi = (u, v) in {(HC[i], HC[(i + 1) % 3]) for i in range(3)}
    if (u, v) == ("a", "c"):
        # draw a -> c as a curve bowing inward, distinct from c -> a
        (x1, y1), (x2, y2) = L[u], L[v]
        cx, cy = 128, 150
        def bound(p, q, rr):
            dx, dy = q[0] - p[0], q[1] - p[1]
            d = math.hypot(dx, dy)
            return p[0] + dx / d * rr, p[1] + dy / d * rr
        sx, sy = bound(L[u], (cx, cy), r)
        ex, ey = bound(L[v], (cx, cy), r + 2.5)
        S.path(f"M{sx:.1f},{sy:.1f} Q{cx},{cy} {ex:.1f},{ey:.1f}", arrow=True, color="var(--muted)", width=1.3, dash="5 4")
    else:
        (x1, y1), (x2, y2) = L[u], L[v]
        d = math.hypot(x2 - x1, y2 - y1)
        ux, uy = (x2 - x1) / d, (y2 - y1) / d
        kw = HI if hi else THIN
        S.line(x1 + ux * r, y1 + uy * r, x2 - ux * (r + 2.5), y2 - uy * (r + 2.5), arrow=True, **kw)
for v, p in L.items():
    node(S, p, r, v)
S.text(110, 250, "directed G", size=13, color="var(--muted)")
S.line(232, 30, 232, 250, width=0.8, color="var(--muted)", dash="2 4")
# right: the undirected graph H
P = {("a", "in"): (300, 58), ("a", "mid"): (380, 58), ("a", "out"): (460, 58),
     ("b", "in"): (560, 96), ("b", "mid"): (560, 150), ("b", "out"): (560, 204),
     ("c", "in"): (460, 232), ("c", "mid"): (380, 232), ("c", "out"): (300, 232)}
rr = 16
# group boxes
S.rect(274, 36, 212, 44, rx=22, stroke="var(--muted)", dash="3 3", width=1)
S.rect(538, 72, 44, 156, rx=22, stroke="var(--muted)", dash="3 3", width=1)
S.rect(274, 210, 212, 44, rx=22, stroke="var(--muted)", dash="3 3", width=1)
S.text(380, 22, "a", size=15, font=SERIF_IT, italic=True)
S.text(600, 150, "b", size=15, font=SERIF_IT, italic=True)
S.text(380, 270, "c", size=15, font=SERIF_IT, italic=True)
for e in UE:
    p, q = P[e[0]], P[e[1]]
    seg(S, p, q, rr, rr, **(HI if frozenset(e) in cyc_edges else MUTED))
for k, p in P.items():
    node(S, p, rr, k[1], size=11, italic=False, font=SANS)
S.text(380, 150, "undirected H", size=13, color="var(--muted)")
cap = ("<strong>Splitting vertices (Exercise 12.8(b)).</strong> Each vertex <i>v</i> of the directed graph becomes a "
       "path <i>v</i><sub>in</sub> <i>v</i><sub>mid</sub> <i>v</i><sub>out</sub>, and each edge <i>u</i>→<i>v</i> becomes "
       "the undirected edge <i>u</i><sub>out</sub><i>v</i><sub>in</sub>. A middle vertex has degree 2, so a Hamiltonian "
       "cycle of <i>H</i> runs straight through every triple, in at an in-vertex and out at an out-vertex: red, the "
       "cycle for <i>a</i>→<i>b</i>→<i>c</i>→<i>a</i>. The edge <i>a</i>→<i>c</i> (dashed) is not used.")
save("a12x-split", S.figure(cap, alt="a directed triangle a, b, c with an extra edge a to c, and the undirected graph "
                                     "of in, mid, out triples with the corresponding 9-vertex cycle in red"))

# =========================================================================== 2. Exercise 12.10(b): cycle to path
GV = ["v", "a", "b", "c", "d"]
GE = [("v", "a"), ("a", "b"), ("b", "c"), ("c", "d"), ("d", "v"), ("a", "c")]
Nv = {u for e in GE if "v" in e for u in e if u != "v"}
assert Nv == {"a", "d"}
E2 = [tuple(e) for e in GE] + [("v'", u) for u in sorted(Nv)] + [("s", "v"), ("t", "v'")]
path = ["s", "v", "a", "b", "c", "d", "v'", "t"]
E2s = {frozenset(e) for e in E2}
assert all(frozenset((path[i], path[i + 1])) in E2s for i in range(len(path) - 1)) and len(set(path)) == 8
pe = {frozenset((path[i], path[i + 1])) for i in range(len(path) - 1)}
# the cycle of G it comes from
gcyc = ["v", "a", "b", "c", "d"]
assert all(frozenset((gcyc[i], gcyc[(i + 1) % 5])) in {frozenset(e) for e in GE} for i in range(5))

S = SVG(520, 260)
Q = {"s": (50, 70), "v": (150, 70), "v'": (150, 200), "t": (50, 200),
     "a": (280, 40), "b": (430, 70), "c": (430, 190), "d": (280, 222)}
r = 16
for e in E2:
    new = "v'" in e or "s" in e or "t" in e
    kw = HI if frozenset(e) in pe else (dict(width=1.3, color="var(--accent)", dash="5 4") if new else THIN)
    seg(S, Q[e[0]], Q[e[1]], r, r, **kw)
for k, p in Q.items():
    new = k in ("v'", "s", "t")
    node(S, p, r, k, stroke="var(--accent)" if new else "currentColor", color="var(--accent)" if new else "currentColor")
cap = ("<strong>Cutting a cycle open (Exercise 12.10(b)).</strong> The new vertex <i>v</i>′ (blue) copies the neighbors "
       "<i>a</i>, <i>d</i> of <i>v</i>, and the leaves <i>s</i> and <i>t</i> hang on <i>v</i> and <i>v</i>′. Leaves must be "
       "the ends of a Hamiltonian path, so every Hamiltonian path runs <i>s</i>, <i>v</i>, …, <i>v</i>′, <i>t</i>; its "
       "middle part is a Hamiltonian cycle of the original graph with its last edge redirected to <i>v</i>′. Red: the "
       "path <i>s v a b c d v</i>′ <i>t</i>, from the cycle <i>v a b c d v</i>.")
save("a12x-cycle-to-path", S.figure(cap, alt="a five-vertex graph with a copy v' of v and pendant vertices s and t; "
                                             "a Hamiltonian path from s to t highlighted"))

# =========================================================================== 3. Exercise 12.26: dominating set
DG = {"u": (110, 60), "v": (110, 200), "w": (280, 130), "x": (450, 130)}
DGE = [("u", "v"), ("u", "w"), ("v", "w"), ("w", "x")]
WPOS = {("u", "v"): (40, 130), ("u", "w"): (215, 48), ("v", "w"): (215, 212), ("w", "x"): (365, 72)}
D = {"v", "w"}
assert all(a in D or b in D for a, b in DGE)                      # a vertex cover
closed = {k: {k} for k in list(DG) + [("w",) + e for e in DGE]}
nb = {k: set() for k in closed}
for a, b in DGE:
    nb[a].add(b)
    nb[b].add(a)
    we = ("w",) + (a, b)
    nb[we] |= {a, b}
    nb[a].add(we)
    nb[b].add(we)
dominated = set(D) | set().union(*(nb[d] for d in D))
assert dominated == set(nb)                                       # dominates G'
# no single vertex dominates G'
assert all(({k} | nb[k]) != set(nb) for k in nb)

S = SVG(520, 260)
r = 16
for a, b in DGE:
    seg(S, DG[a], DG[b], r, r, **THIN)
    wp = WPOS[(a, b)]
    for c in (a, b):
        seg(S, wp, DG[c], 8, r, width=1.3, color="var(--accent)")
for (a, b), wp in WPOS.items():
    S.rect(wp[0] - 8, wp[1] - 8, 16, 16, rx=2, stroke="var(--accent)", fill="var(--paper)", width=1.5)
    dx, dy = {("u", "v"): (-26, 0), ("u", "w"): (0, -20), ("v", "w"): (0, 21), ("w", "x"): (0, -20)}[(a, b)]
    S.text(wp[0] + dx, wp[1] + dy, f'w<tspan baseline-shift="sub" font-size="10">{a}{b}</tspan>', size=15,
           font=SERIF_IT, italic=True, color="var(--accent)", halo=True, raw=True)
for k, p in DG.items():
    if k in D:
        node(S, p, r, k, stroke="var(--hi)", fill="var(--hi)", width=2, color="var(--paper)")
    else:
        node(S, p, r, k)
cap = ("<strong>Dominating set from vertex cover (Exercise 12.26).</strong> Every edge <i>uv</i> of <i>G</i> gets a new "
       "vertex <i>w<sub>uv</sub></i> (blue square) adjacent to <i>u</i> and <i>v</i>. Only <i>u</i>, <i>v</i> and "
       "<i>w<sub>uv</sub></i> itself dominate <i>w<sub>uv</sub></i>, so a dominating set must touch every edge. Red: "
       "{<i>v</i>, <i>w</i>}, a smallest vertex cover of <i>G</i> and a smallest dominating set of the new graph, both "
       "of size 2.")
save("a12x-dominating", S.figure(cap, alt="a triangle u v w with pendant x; every edge has an extra square vertex joined "
                                          "to its two ends; v and w highlighted"))

# =========================================================================== 4. Exercise 12.34: stones
VARS = "abcd"
CL = [(("a", 1), ("b", 1), ("c", 1)), (("b", 1), ("c", 0), ("d", 0)), (("a", 0), ("c", 1), ("d", 1)),
      (("a", 1), ("b", 0), ("d", 0))]
ASG = {"a": True, "b": False, "c": True, "d": False}
assert all(any(ASG[v] == bool(s) for v, s in C) for C in CL)
grid = [{v: ("R" if s else "B") for v, s in C} for C in CL]
keep = [{v: c for v, c in row.items() if (c == "R") == ASG[v]} for row in grid]
assert all(keep[i] for i in range(4))                             # every row keeps a stone
assert all(len({keep[i][v] for i in range(4) if v in keep[i]}) <= 1 for v in VARS)

S = SVG(600, 236)
cell = 36
OX = [170, 420]
OY = 46


def lit(v, s):
    return v if s else v + "̄"


for i, C in enumerate(CL):
    S.text(150, OY + cell * i + cell / 2, " ∨ ".join(lit(v, s) for v, s in C), size=14, anchor="end",
           font=SERIF_IT, italic=True)
for g, ox in enumerate(OX):
    for j, v in enumerate(VARS):
        S.text(ox + cell * j + cell / 2, OY - 14, v, size=15, font=SERIF_IT, italic=True,
               color=("var(--muted)" if g == 0 else ("var(--hi)" if ASG[v] else "var(--accent)")))
    S.rect(ox, OY, cell * 4, cell * 4, stroke="currentColor", width=1.2)
    for k in range(1, 4):
        S.line(ox + cell * k, OY, ox + cell * k, OY + cell * 4, width=0.6, color="var(--muted)")
        S.line(ox, OY + cell * k, ox + cell * 4, OY + cell * k, width=0.6, color="var(--muted)")
    for i, row in enumerate(grid):
        for v, c in row.items():
            j = VARS.index(v)
            cx, cy = ox + cell * j + cell / 2, OY + cell * i + cell / 2
            kept = g == 0 or v in keep[i]
            col = "var(--hi)" if c == "R" else "var(--accent)"
            if kept:
                if c == "R":
                    S.circle(cx, cy, 11, stroke=col, fill=col, width=1.5)
                else:
                    S.rect(cx - 10, cy - 10, 20, 20, rx=3, stroke=col, fill=col, width=1.5)
            else:
                if c == "R":
                    S.add(f'<circle cx="{cx}" cy="{cy}" r="11" fill="none" stroke="{col}" stroke-width="1.2" '
                          f'stroke-dasharray="3 3" opacity="0.6"/>')
                else:
                    S.rect(cx - 10, cy - 10, 20, 20, rx=3, stroke=col, fill="none", width=1.2, dash="3 3")
S.text(OX[0] + 2 * cell, OY + 4 * cell + 22, "the puzzle", size=13, color="var(--muted)")
S.text(OX[1] + 2 * cell, OY + 4 * cell + 22, "a = c = True, b = d = False", size=13, color="var(--muted)")
S.text(OX[1] - 40, OY + 2 * cell, "→", size=22, color="var(--muted)")
cap = ("<strong>Stones from a formula (Exercise 12.34).</strong> The chapter's formula "
       "(<i>a</i> ∨ <i>b</i> ∨ <i>c</i>) ∧ (<i>b</i> ∨ <i>c̄</i> ∨ <i>d̄</i>) ∧ (<i>ā</i> ∨ <i>c</i> ∨ <i>d</i>) ∧ "
       "(<i>a</i> ∨ <i>b̄</i> ∨ <i>d̄</i>): one row per clause, one column per variable, a red disc for a positive literal "
       "and a blue square for a negative one. Right: the assignment <i>a</i> = <i>c</i> = True, <i>b</i> = <i>d</i> = "
       "False keeps the red stones of columns <i>a</i>, <i>c</i> and the blue stones of <i>b</i>, <i>d</i> (removed "
       "stones dashed). Every column is one color, and every row keeps a stone because every clause has a True literal.")
save("a12x-stones", S.figure(cap, alt="two 4 by 4 grids of red discs and blue squares, before and after removing the "
                                      "stones that disagree with the assignment"))
