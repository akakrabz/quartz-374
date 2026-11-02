#!/usr/bin/env python3
"""Figures for the Chapter 12 concept pages independent-set, graph-coloring and hamiltonian-cycle.
Writes tools/figs/a12c-<name>.html; then run tools/assemble.py on the concept pages. Every graph drawn here is
built by a minimal re-implementation of the page's reduction, and every highlighted solution is checked here
(independent set, proper coloring, Hamiltonian cycle) before it is drawn; tools/checks/a12c.py re-checks the
reductions and the numbers in the captions independently."""
import itertools
import math
import os

from figlib import SVG, SANS, SERIF_IT

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")
os.makedirs(OUT, exist_ok=True)


def save(name, html):
    with open(os.path.join(OUT, name + ".html"), "w", encoding="utf-8") as f:
        f.write(html + "\n")
    print("wrote", name)


NAME = {1: "a", 2: "b", 3: "c", -1: "ā", -2: "b̄", -3: "c̄"}


def node(S, x, y, label, r=15, stroke="currentColor", fill="var(--paper)", fill_opacity=None, width=1.6, size=16,
         italic=True, ring=False):
    if ring:
        S.circle(x, y, r + 4, stroke=stroke, fill="var(--paper)", width=1.4)
    S.circle(x, y, r, stroke=stroke, fill=fill, width=width, fill_opacity=fill_opacity)
    if label:
        S.text(x, y + 1, label, size=size, font=SERIF_IT if italic else SANS, italic=italic)


def shorten(x1, y1, x2, y2, r1, r2):
    L = math.hypot(x2 - x1, y2 - y1)
    ux, uy = (x2 - x1) / L, (y2 - y1) / L
    return x1 + ux * r1, y1 + uy * r1, x2 - ux * r2, y2 - uy * r2


# =========================================================================== 1. 3SAT -> independent set
PHI = [(1, 2, 3), (-1, -2, 3), (1, -2, -3)]
# vertices (j, t): literal PHI[j][t]
Vis = [(j, t) for j in range(3) for t in range(3)]
Eis = {frozenset((u, v)) for u, v in itertools.combinations(Vis, 2)
       if u[0] == v[0] or PHI[u[0]][u[1]] == -PHI[v[0]][v[1]]}
S_IS = [(0, 0), (1, 2), (2, 1)]
assert all(frozenset((u, v)) not in Eis for u, v in itertools.combinations(S_IS, 2))
assert len(Eis) == 15
POS = {
    (0, 0): (172, 122), (0, 1): (92, 62), (0, 2): (92, 178),      # a1 right, b1 top, c1 bottom
    (1, 0): (352, 70), (1, 1): (255, 62), (1, 2): (318, 178),     # ā2, b̄2, c2
    (2, 0): (428, 122), (2, 1): (508, 62), (2, 2): (508, 178),    # a3 left, b̄3 top, c̄3 bottom
}
S = SVG(600, 262)
R = 16
# triangle edges first, then conflict edges
for e in Eis:
    u, v = tuple(e)
    (x1, y1), (x2, y2) = POS[u], POS[v]
    if u[0] == v[0]:
        S.line(*shorten(x1, y1, x2, y2, R, R), width=1.6)
CURVE = {frozenset(((0, 1), (2, 1))): -32, frozenset(((0, 2), (2, 2))): 246}   # long conflicts: arcs above/below
for e in Eis:
    u, v = sorted(e)
    if u[0] == v[0]:
        continue
    (x1, y1), (x2, y2) = POS[u], POS[v]
    if e in CURVE:
        cy = CURVE[e]
        mx = (x1 + x2) / 2
        # start/end on the circle toward the control point
        sx, sy, _, _ = shorten(x1, y1, mx, cy, R, 0)
        ex, ey, _, _ = shorten(x2, y2, mx, cy, R, 0)
        S.path(f"M{sx:.1f},{sy:.1f} Q{mx:.1f},{cy:.1f} {ex:.1f},{ey:.1f}", color="var(--hi)", width=1.6, dash="6 4")
    else:
        S.line(*shorten(x1, y1, x2, y2, R, R), color="var(--hi)", width=1.6, dash="6 4")
for v in Vis:
    x, y = POS[v]
    inS = v in S_IS
    node(S, x, y, NAME[PHI[v[0]][v[1]]], r=R, stroke="var(--accent)" if inS else "currentColor",
         fill="var(--accent)" if inS else "var(--paper)", fill_opacity=0.18 if inS else None,
         width=2.6 if inS else 1.6, ring=inS)
for j, cx in enumerate((120, 300, 480)):
    cl = " ∨ ".join(NAME[l] for l in PHI[j])
    S.text(cx, 246, f"clause {j + 1}: ({cl})", size=14, halo=True)
html = S.figure(
    "<strong>3SAT → independent set.</strong> The graph for (<i>a</i> ∨ <i>b</i> ∨ <i>c</i>) ∧ (<i>ā</i> ∨ "
    "<i>b̄</i> ∨ <i>c</i>) ∧ (<i>a</i> ∨ <i>b̄</i> ∨ <i>c̄</i>): one vertex per literal occurrence, a triangle per clause "
    "(solid) and a conflict edge between every <i>x</i> and <i>x̄</i> (dashed), 15 edges in all. The ringed vertices "
    "form an independent set of size 3 = number of clauses — one true literal per clause, never both <i>x</i> and "
    "<i>x̄</i> — so the assignment <i>a</i> = <i>c</i> = True, <i>b</i> = False satisfies the formula.",
    alt="three clause triangles with dashed conflict edges between complementary literals and an independent set of "
        "three ringed vertices")
save("a12c-is-triangles", html)

# =========================================================================== 2. 3SAT -> 3Color gadgets
TRUE, FALSE, OTHER = "var(--accent)", "var(--hi)", "var(--accent2)"
COLNAME = {TRUE: "True", FALSE: "False", OTHER: "Other"}
# left panel: truth triangle T F X and variable triangle X a ā sharing X
G2 = SVG(640, 300)
LP = {"T": (40, 70), "F": (40, 190), "X": (125, 130), "a": (210, 70), "ā": (210, 190)}
LC = {"T": TRUE, "F": FALSE, "X": OTHER, "a": FALSE, "ā": TRUE}
LE = [("T", "F"), ("F", "X"), ("X", "T"), ("X", "a"), ("X", "ā"), ("a", "ā")]
for u, v in LE:
    assert LC[u] != LC[v]
    (x1, y1), (x2, y2) = LP[u], LP[v]
    G2.line(*shorten(x1, y1, x2, y2, 17, 17), width=1.6)
for v, (x, y) in LP.items():
    node(G2, x, y, v, r=17, stroke=LC[v], fill=LC[v], fill_opacity=0.2, width=2.2)
G2.text(125, 240, "truth gadget + variable", size=13)
G2.text(125, 258, "gadget for a", size=13)
G2.line(262, 20, 262, 270, color="var(--muted)", width=1, dash="3 4")
# right panel: clause gadget for (a ∨ b ∨ c̄) with a = b = c = False
RP = {"a": (300, 50), "b": (300, 140), "c̄": (300, 230), "u": (370, 50), "v": (370, 140), "w": (440, 95),
      "y": (520, 95), "z": (520, 230), "T": (600, 162)}
RC = {"a": FALSE, "b": FALSE, "c̄": TRUE, "u": TRUE, "v": OTHER, "w": FALSE, "y": OTHER, "z": FALSE, "T": TRUE}
RE = [("a", "u"), ("b", "v"), ("u", "v"), ("u", "w"), ("v", "w"), ("w", "y"), ("c̄", "z"), ("y", "z"), ("y", "T"),
      ("z", "T")]
assert len(RE) == 10
for u, v in RE:
    assert RC[u] != RC[v], (u, v)
    (x1, y1), (x2, y2) = RP[u], RP[v]
    G2.line(*shorten(x1, y1, x2, y2, 17, 17), width=1.6)
# the coloring is the forced one: check by brute force over the five gadget vertices
cols3 = [TRUE, FALSE, OTHER]
sols = []
for c in itertools.product(cols3, repeat=5):
    asg = dict(RC)
    asg.update(dict(zip("uvwyz", c)))
    if all(asg[p] != asg[q] for p, q in RE):
        sols.append(c)
assert len(sols) == 2 and (RC["u"], RC["v"], RC["w"], RC["y"], RC["z"]) in sols
for v, (x, y) in RP.items():
    node(G2, x, y, v, r=17, stroke=RC[v], fill=RC[v], fill_opacity=0.2, width=2.2)
# legend
for t, (col, nm) in enumerate(((TRUE, "True"), (FALSE, "False"), (OTHER, "Other"))):
    lx = 340 + t * 95
    G2.circle(lx, 284, 8, stroke=col, fill=col, fill_opacity=0.2, width=2.2)
    G2.text(lx + 14, 284, nm, size=13, anchor="start")
html = G2.figure(
    "<strong>3SAT → 3Color gadgets.</strong> Left: the truth triangle <i>T</i>, <i>F</i>, <i>X</i> names the three "
    "colors True, False, Other; "
    "a variable triangle through <i>X</i> forces <i>a</i> and <i>ā</i> to get True and False in some order. Right: "
    "the clause gadget for (<i>a</i> ∨ <i>b</i> ∨ <i>c̄</i>) — five new vertices and ten edges, ending at the same "
    "vertex <i>T</i> — colored for "
    "<i>a</i> = <i>b</i> = <i>c</i> = False: <i>u</i> True, <i>v</i> Other, <i>w</i> False, <i>y</i> Other, "
    "<i>z</i> False. If <i>c̄</i> were False too, <i>y</i> and <i>z</i> would both have to be Other.",
    alt="truth triangle and a variable triangle sharing X, and a clause gadget of two triangles attached to the "
        "literal vertices a, b, c-bar and to T, all properly 3-colored")
save("a12c-coloring-gadgets", html)

# =========================================================================== 3. 3SAT -> directed Hamiltonian cycle
EXH = [(1, -2, 3), (-1, 2, -3)]
n, k = 3, 2
L = 3 * k
Vh, out = [], {}


def A(a, b):
    out.setdefault(a, set()).add(b)


for i in range(1, n + 1):
    Vh.append(("h", i))
    Vh += [(i, c) for c in range(L + 1)]
    for c in range(1, L + 1):
        A((i, c - 1), (i, c))
        A((i, c), (i, c - 1))
    nx = ("h", i % n + 1)
    A(("h", i), (i, 0))
    A(("h", i), (i, L))
    A((i, 0), nx)
    A((i, L), nx)
for j, cl in enumerate(EXH, 1):
    Vh.append(("c", j))
    p, q = 3 * j - 2, 3 * j - 1
    for l in cl:
        i = abs(l)
        if l > 0:
            A((i, p), ("c", j))
            A(("c", j), (i, q))
        else:
            A((i, q), ("c", j))
            A(("c", j), (i, p))
CYC = [("h", 1), (1, 0), (1, 1), ("c", 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), ("h", 2)] \
    + [(2, c) for c in range(6, -1, -1)] + [("h", 3), (3, 6), (3, 5), ("c", 2), (3, 4), (3, 3), (3, 2), (3, 1), (3, 0)]
assert len(CYC) == len(Vh) == 26 and set(CYC) == set(Vh)
assert all(CYC[(t + 1) % len(CYC)] in out[CYC[t]] for t in range(len(CYC)))
CE = {(CYC[t], CYC[(t + 1) % len(CYC)]) for t in range(len(CYC))}

X0, DX = 110, 62
ROWY = {1: 78, 2: 178, 3: 278}
HUBY = {1: 28, 2: 128, 3: 228}
HX = X0 + 3 * DX
P = {}
for i in range(1, n + 1):
    for c in range(L + 1):
        P[(i, c)] = (X0 + c * DX, ROWY[i])
    P[("h", i)] = (HX, HUBY[i])
P[("c", 1)] = (X0 + 1.5 * DX, 128 + 3)
P[("c", 2)] = (X0 + 4.5 * DX, 228 + 3)
H = SVG(640, 330)
rv, rh, rc = 9, 10, 9


def arrow(a, b, on):
    (x1, y1), (x2, y2) = P[a], P[b]
    ra = rh if a[0] == "h" else (rc if a[0] == "c" else rv)
    rb = rh if b[0] == "h" else (rc if b[0] == "c" else rv)
    sx, sy, ex, ey = shorten(x1, y1, x2, y2, ra, rb + 1.5)
    if a[0] not in ("h", "c") and b[0] not in ("h", "c") and a[0] == b[0]:
        # row edges: two parallel arrows, offset vertically
        off = -3.2 if b[1] > a[1] else 3.2
        sy += off
        ey += off
    H.line(sx, sy, ex, ey, color="var(--accent)" if on else "var(--muted)", width=2.4 if on else 1.1, arrow=True,
           opacity=None if on else 0.9)


# wrap-around edges (i = 3 ends -> h1) drawn as paths around the sides
for a, s in out.items():
    for b in s:
        on = (a, b) in CE
        if b == ("h", 1) and a[0] == 3:
            (x1, y1) = P[a]
            hx, hy = P[b]
            side = -1 if a[1] == 0 else 1
            xo = x1 + side * 40
            col = "var(--accent)" if on else "var(--muted)"
            H.path(f"M{x1 + side * rv:.1f},{y1:.1f} L{xo:.1f},{y1:.1f} L{xo:.1f},{hy:.1f} L{hx + side * (rh + 2.5):.1f},{hy:.1f}",
                   color=col, width=2.4 if on else 1.1, arrow=True)
        else:
            arrow(a, b, on)
for v in Vh:
    x, y = P[v]
    if v[0] == "h":
        H.circle(x, y, rh, stroke="currentColor", fill="var(--paper)", width=1.6)
        H.text(x, y + 1, f"h{v[1]}", size=11, font=SERIF_IT, italic=True)
    elif v[0] == "c":
        H.rect(x - rc, y - rc, 2 * rc, 2 * rc, stroke="var(--hi)", fill="var(--paper)", width=1.8)
        H.text(x + 15, y - 1, f"[{v[1]}]", size=12, anchor="start", color="var(--hi)", halo=True)
    else:
        sep = v[1] % 3 == 0
        H.circle(x, y, rv, stroke="currentColor", fill="var(--paper)" if not sep else "var(--muted)",
                 width=1.4, fill_opacity=None if not sep else 0.35)
for i, nm in ((1, "a"), (2, "b"), (3, "c")):
    H.text(X0 - 72, ROWY[i] - 9, f"{nm}", size=16, font=SERIF_IT, italic=True)
    val = {1: "True →", 2: "← False", 3: "← False"}[i]
    H.text(X0 - 72, ROWY[i] + 11, val, size=12, color="var(--accent)", halo=True)
for c in range(L + 1):
    H.text(X0 + c * DX, 312, str(c), size=12, color="var(--muted)")
html = H.figure(
    "<strong>3SAT → directed Hamiltonian cycle.</strong> The graph for (<i>a</i> ∨ <i>b̄</i> ∨ <i>c</i>) ∧ "
    "(<i>ā</i> ∨ <i>b</i> ∨ <i>c̄</i>): one row of 3<i>k</i> + 1 = 7 vertices per variable (positions 0–6 at the "
    "bottom; shaded spacers at 0, 3, 6), hubs <i>h</i><sub>1</sub>, <i>h</i><sub>2</sub>, <i>h</i><sub>3</sub>, "
    "and clause vertices [1], [2] attached at positions 1, 2 and 4, 5; 26 vertices and 60 edges. Highlighted: the "
    "Hamiltonian cycle for <i>a</i> = True, <i>b</i> = <i>c</i> = False — row <i>a</i> left to right with the "
    "detour 1 → [1] → 2, row <i>c</i> right to left with the detour 5 → [2] → 4.",
    alt="three doubly linked rows of seven vertices with hub vertices between them and two clause vertices, and a "
        "highlighted Hamiltonian cycle")
save("a12c-ham-3sat", html)
