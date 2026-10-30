#!/usr/bin/env python3
"""Figures for Algorithms Chapter 12 (NP-hardness). Writes tools/figs/a12-<name>.html; then run tools/assemble.py on
the chapter page. Every value drawn (wire values, the independent set, the 3-coloring, the Hamiltonian cycle) is
computed here from the constructions; tools/checks/a12.py re-checks the same instances independently."""
import itertools
import math
import os

from figlib import SVG, Automaton, SANS, SERIF_IT, MONO

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")
os.makedirs(OUT, exist_ok=True)


def save(name, html):
    with open(os.path.join(OUT, name + ".html"), "w", encoding="utf-8") as f:
        f.write(html + "\n")
    print("wrote", name)


def overlay_figure(A, overlay, caption, alt):
    svg = A.svg(alt).replace("</svg>", "".join(overlay.items) + "</svg>")
    out = f'<figure class="cs-fig">{svg}<figcaption>{caption}</figcaption></figure>'
    assert "\n\n" not in out
    return out.replace("\n", " ")


def mathlabel(S, x, y, name, neg=False, sub=None, size=15, color="currentColor", halo=False, anchor="middle"):
    """Italic variable name, optional subscript, optional bar (negation) drawn as a short line."""
    if sub is None:
        S.text(x, y, name, size=size, font=SERIF_IT, italic=True, color=color, halo=halo, anchor=anchor)
        w = size * 0.5
    else:
        body = (f'{name}<tspan dy="4" style="font-size:{size * 0.68:.1f}px">{sub}</tspan>')
        S.text(x, y, body, size=size, font=SERIF_IT, italic=True, color=color, halo=halo, anchor=anchor, raw=True)
        w = size * 0.85
    if neg:
        cx = x if anchor == "middle" else x + w / 2
        S.line(cx - size * 0.28 + 1, y - size * 0.62, cx + size * 0.28 + 1, y - size * 0.62, color=color, width=1.2)


# =========================================================================== 1. the shape of a reduction
S = SVG(640, 200)
S.rect(92, 22, 410, 150, rx=10, stroke="currentColor", width=1.4, dash="5 4")
S.text(297, 38, "an algorithm for X", size=13, color="var(--muted)", weight="600")
S.rect(112, 62, 150, 76, rx=8, stroke="var(--accent)", fill="var(--accent)", fill_opacity=0.08, width=1.8)
S.text(187, 86, "reduction", size=14, weight="600", color="var(--accent)")
S.text(187, 106, "build y from x", size=13)
S.text(187, 124, "in polynomial time", size=13)
S.rect(338, 62, 120, 76, rx=8, stroke="currentColor", fill="var(--muted)", fill_opacity=0.10, width=1.6)
S.text(398, 90, "black box", size=14, weight="600")
S.text(398, 112, "for Y", size=13)
S.text(398, 128, "(hypothetical)", size=12, color="var(--muted)")
S.line(20, 100, 109, 100, arrow=True, width=1.6)
S.text(52, 82, "instance x", size=13)
S.text(52, 118, "of X", size=13)
S.line(264, 100, 335, 100, arrow=True, width=1.6)
S.text(300, 82, "instance y", size=13)
S.text(300, 118, "of Y", size=13)
S.path("M460,86 L480,86 L480,70 L630,70", arrow=True, width=1.6)
S.path("M460,114 L480,114 L480,130 L630,130", arrow=True, width=1.6)
S.text(568, 56, "YES: x is YES", size=13, color="var(--accent)", weight="600")
S.text(568, 146, "NO: x is NO", size=13, color="var(--hi)", weight="600")
S.text(297, 188, "correct: x is YES ⟺ y is YES  ·  fast: |y| is polynomial in |x|", size=12.5)
html = S.figure(
    "<strong>A polynomial-time reduction from X to Y</strong> (the book draws one for every reduction in the "
    "chapter). The reduction turns an arbitrary instance <i>x</i> of the known problem X into an instance <i>y</i> "
    "of the new problem Y, and the black box's answer for <i>y</i> is returned unchanged. If Y could be solved in "
    "polynomial time, so could X; since X is NP-hard, Y is NP-hard. The arrow of the reduction points "
    "<i>from</i> the known problem <i>to</i> the new one.",
    alt="block diagram: an instance x of X enters a reduction box that outputs an instance y of Y, which goes into a black box for Y whose yes or no answer is the answer for x")
save("a12-reduction", html)


# =========================================================================== 2. the book's circuit (Figures 12.2, 12.5)
def and_gate(S, x0, cy, h=30, w=34, ninputs=2):
    y0 = cy - h / 2
    S.path(f"M{x0},{y0} L{x0 + w - h / 2},{y0} A{h / 2},{h / 2} 0 0 1 {x0 + w - h / 2},{y0 + h} L{x0},{y0 + h} Z",
           fill="var(--paper)", width=1.6)
    return x0 + w, cy


def or_gate(S, x0, cy, h=30, w=36):
    y0 = cy - h / 2
    S.path(f"M{x0},{y0} Q{x0 + w * 0.62},{y0} {x0 + w},{cy} Q{x0 + w * 0.62},{y0 + h} {x0},{y0 + h} "
           f"Q{x0 + 9},{cy} {x0},{y0} Z", fill="var(--paper)", width=1.6)
    return x0 + w, cy


def not_gate(S, x0, cy, h=22, w=24):
    y0 = cy - h / 2
    S.path(f"M{x0},{y0} L{x0 + w},{cy} L{x0},{y0 + h} Z", fill="var(--paper)", width=1.6)
    S.circle(x0 + w + 4, cy, 4, width=1.4)
    return x0 + w + 8, cy


BOOK_IN = ["x1", "x2", "x3", "x4", "x5"]
BOOK_GATES = [("y1", "and", ["x1", "x4"]), ("y2", "not", ["x4"]), ("y3", "and", ["x3", "y2"]),
              ("y4", "or", ["y1", "x2"]), ("y5", "not", ["x2"]), ("y6", "not", ["x5"]),
              ("y7", "or", ["y3", "y5"]), ("z", "and", ["y4", "y7", "y6"])]
OPS = {"and": all, "or": any, "not": lambda xs: not xs[0]}
XS = dict(zip(BOOK_IN, [False, True, True, False, False]))
val = dict(XS)
for w, op, ins in BOOK_GATES:
    val[w] = OPS[op]([val[i] for i in ins])
assert val["z"] and [int(val[w]) for w in ["y1", "y2", "y3", "y4", "y5", "y6", "y7"]] == [0, 1, 1, 1, 0, 1, 1]

S = SVG(620, 270)
WIRES = SVG(620, 270)
IY = {"x1": 40, "x2": 92, "x3": 140, "x4": 186, "x5": 236}


def wire(points, name):
    on = val[name]
    d = "M" + " L".join(f"{x},{y}" for x, y in points)
    WIRES.path(d, color="var(--accent)" if on else "currentColor", width=2.6 if on else 1.3)


def dot(x, y, name):
    WIRES.circle(x, y, 3.2, stroke="none", fill="var(--accent)" if val[name] else "currentColor")


# input wires
wire([(46, 40), (150, 40)], "x1")                                   # x1 -> AND1
wire([(46, 92), (110, 92), (110, 68), (262, 68)], "x2")              # x2 -> OR (y4)
wire([(110, 92), (110, 112), (178, 112)], "x2")                      # x2 -> NOT (y5)
dot(110, 92, "x2")
wire([(46, 140), (262, 140)], "x3")                                  # x3 -> AND (y3)
wire([(46, 186), (150, 186)], "x4")                                  # x4 -> NOT (y2)
wire([(80, 186), (80, 54), (150, 54)], "x4")                         # x4 -> AND1
dot(80, 186, "x4")
wire([(46, 236), (178, 236)], "x5")                                  # x5 -> NOT (y6)
# gate outputs
wire([(184, 47), (262, 47)], "y1")
wire([(182, 186), (220, 186), (220, 156), (262, 156)], "y2")
wire([(296, 148), (330, 148), (330, 136), (372, 136)], "y3")
wire([(298, 57), (480, 57), (480, 116), (500, 116)], "y4")
wire([(210, 112), (372, 112)], "y5")
wire([(210, 236), (480, 236), (480, 144), (500, 144)], "y6")
wire([(408, 124), (440, 124), (440, 130), (500, 130)], "y7")
wire([(534, 130), (600, 130)], "z")
# gates on top of the wire ends
G = SVG(620, 270)
and_gate(G, 150, 47, h=28)
not_gate(G, 150, 186)
not_gate(G, 178, 112)
not_gate(G, 178, 236)
or_gate(G, 262, 57, h=36)
and_gate(G, 262, 148)
or_gate(G, 372, 124)
and_gate(G, 500, 130, h=40)
LAB = SVG(620, 270)
for x, yy in IY.items():
    mathlabel(LAB, 24, yy, x[0], sub=x[1], size=15)
    LAB.text(24, yy + 17, "1" if XS[x] else "0", size=12, color="var(--accent)" if XS[x] else "var(--muted)",
             font=MONO)
for name, (x, yy) in {"y1": (222, 36), "y2": (232, 174), "y3": (314, 160), "y4": (452, 46), "y5": (300, 100),
                      "y6": (452, 225), "y7": (450, 113), "z": (585, 116)}.items():
    if name == "z":
        mathlabel(LAB, x, yy, "z", size=15, halo=True)
    else:
        mathlabel(LAB, x, yy, "y", sub=name[1], size=15, halo=True)
S.items = WIRES.items + G.items + LAB.items
html = S.figure(
    "<strong>A boolean circuit</strong> (the book's Figures 12.2 and 12.5, redrawn): five inputs, three And gates, "
    "two Or gates, three Not gates, one output <i>z</i>; every interior wire is named <i>y</i><sub>1</sub>, …, "
    "<i>y</i><sub>7</sub> for the transcription of §12.5. Shown is the input <i>x</i> = 01100, which turns the light "
    "on: thick blue wires carry True. Exactly 4 of the 32 inputs do (all with <i>x</i><sub>5</sub> = 0).",
    alt="a boolean circuit with inputs x1 to x5, interior wires y1 to y7 and output z, evaluated on input 01100")
save("a12-circuit", html)

# =========================================================================== 3. the NAND circuit and its 3CNF
S = SVG(640, 190)
W2 = SVG(640, 190)
G2 = SVG(640, 190)
L2 = SVG(640, 190)
W2.path("M40,52 L74,52", width=1.4)
W2.path("M40,88 L74,88", width=1.4)
W2.path("M108,70 L144,70", width=1.4)
W2.path("M176,70 L204,70", width=1.4)
and_gate(G2, 74, 70, h=48, w=36)
not_gate(G2, 144, 70)
mathlabel(L2, 22, 52, "x", sub="1")
mathlabel(L2, 22, 88, "x", sub="2")
mathlabel(L2, 126, 58, "y", halo=True)
mathlabel(L2, 216, 70, "z")
L2.text(120, 128, "z = NOT(x₁ AND x₂)", size=12.5, color="var(--muted)")
L2.line(236, 14, 236, 176, color="var(--muted)", width=1, dash="3 4")
rows = [("gate", "Φ₂: its CNF clauses", "Φ₃ clauses"),
        ("y = x₁ ∧ x₂", "(y ∨ ¬x₁ ∨ ¬x₂)", "1"),
        ("", "(¬y ∨ x₁), (¬y ∨ x₂)", "2 × 2 (new p₁, p₂)"),
        ("z = ¬y", "(z ∨ y), (¬z ∨ ¬y)", "2 × 2 (new p₃, p₄)"),
        ("output", "(z)", "4 (new p₅, p₆)")]
for r, (a, b, c) in enumerate(rows):
    yy = 28 + r * 30
    hdr = r == 0
    col = "var(--muted)" if hdr else "currentColor"
    for x, t, it in ((250, a, not hdr and a != "output"), (336, b, not hdr), (500, c, False)):
        L2.text(x, yy, t, size=13 if hdr else 13.5, anchor="start", weight="600" if hdr else None, color=col,
                font=SERIF_IT if it else SANS, italic=it)
L2.text(436, 176, "6 clauses → 13 clauses with exactly 3 literals", size=12.5, color="var(--accent)",
        weight="600")
S.items = W2.items + G2.items + L2.items
html = S.figure(
    "<strong>CircuitSat → 3Sat on a two-gate circuit.</strong> The circuit computes <i>z</i> = ¬(<i>x</i><sub>1</sub> ∧ "
    "<i>x</i><sub>2</sub>). Each gate becomes its CNF (stage 3), and each clause with fewer than three literals is "
    "padded with new variables <i>p</i><sub>1</sub>, …, <i>p</i><sub>6</sub> (stage 4); the full 13-clause formula "
    "Φ<sub>3</sub> is written out below. Φ<sub>3</sub> is satisfiable exactly when the circuit is: 3 of the 4 inputs "
    "work, and each extends to 2<sup>6</sup> satisfying assignments, one for each value of the padding variables.",
    alt="a two-gate NAND circuit and a table listing the clauses produced for each gate")
save("a12-tseitin", html)

# =========================================================================== 4. 3Sat -> independent set (Figure 12.8)
PHI = [[("a", 1), ("b", 1), ("c", 1)], [("b", 1), ("c", 0), ("d", 0)], [("a", 0), ("c", 1), ("d", 1)],
       [("a", 1), ("b", 0), ("d", 0)]]
POS = {(0, 0): (200, 40), (0, 2): (320, 40), (0, 1): (260, 86),
       (1, 0): (432, 122), (1, 1): (384, 200), (1, 2): (432, 278),
       (3, 1): (88, 122), (3, 0): (136, 200), (3, 2): (88, 278),
       (2, 2): (260, 314), (2, 0): (200, 360), (2, 1): (320, 360)}
CHOSEN = {(0, 0), (1, 2), (2, 1), (3, 0)}
V = list(POS)
E_tri = [(u, v) for u, v in itertools.combinations(V, 2) if u[0] == v[0]]
E_neg = [(u, v) for u, v in itertools.combinations(V, 2)
         if u[0] != v[0] and PHI[u[0]][u[1]][0] == PHI[v[0]][v[1]][0] and PHI[u[0]][u[1]][1] != PHI[v[0]][v[1]][1]]
assert len(E_tri) == 12 and len(E_neg) == 8
assert not any(u in CHOSEN and v in CHOSEN for u, v in E_tri + E_neg)
S = SVG(520, 400)
for u, v in E_neg:
    (x1, y1), (x2, y2) = POS[u], POS[v]
    S.line(x1, y1, x2, y2, color="var(--hi)", width=1.6)
for u, v in E_tri:
    (x1, y1), (x2, y2) = POS[u], POS[v]
    S.line(x1, y1, x2, y2, color="currentColor", width=1.6)
for v, (x, y) in POS.items():
    name, pos = PHI[v[0]][v[1]]
    if v in CHOSEN:
        S.circle(x, y, 19, stroke="var(--accent)", fill="var(--paper)", width=1.6)
        S.circle(x, y, 15, stroke="var(--accent)", fill="var(--accent)", fill_opacity=0.18, width=1.6)
    else:
        S.circle(x, y, 15, stroke="currentColor", fill="var(--paper)", width=1.6)
    mathlabel(S, x, y + 1, name, neg=not pos, size=16)
for j, (x, y) in enumerate([(260, 14), (478, 200), (260, 392), (40, 200)]):
    pass
S.text(512, 372, "clauses: 1 top, 2 right,", size=12, color="var(--muted)", anchor="end")
S.text(512, 388, "3 bottom, 4 left", size=12, color="var(--muted)", anchor="end")
html = S.figure(
    "<strong>3Sat → MaxIndSet</strong> (the book's Figure 12.8, recomputed) for Φ = (<i>a</i> ∨ <i>b</i> ∨ <i>c</i>) ∧ "
    "(<i>b</i> ∨ <i>c̄</i> ∨ <i>d̄</i>) ∧ (<i>ā</i> ∨ <i>c</i> ∨ <i>d</i>) ∧ (<i>a</i> ∨ <i>b̄</i> ∨ <i>d̄</i>). One "
    "triangle per clause (black edges), and a red edge between every pair of contradictory literals — 12 vertices, "
    "12 + 8 edges. The four circled vertices form an independent set of size 4 = number of clauses; making their "
    "literals true gives <i>a</i> = <i>c</i> = True, <i>d</i> = False, which satisfies Φ for either value of "
    "<i>b</i>.",
    alt="twelve vertices in four triangles, one per clause, with extra edges between contradictory literals; four vertices, one per triangle, are highlighted")
save("a12-indset", html)

# =========================================================================== 5. 3-coloring gadgets
TRUE, FALSE, OTHER = 0, 1, 2
COLOR = {TRUE: "var(--accent)", FALSE: "var(--hi)", OTHER: "var(--accent2)"}
INIT = {TRUE: "T", FALSE: "F", OTHER: "O"}
# clause gadget for (a or b or ~c): literal nodes a, b, cbar; new nodes p q r s t; T
CV = ["a", "b", "cbar", "p", "q", "r", "s", "t", "T"]
CE = [("a", "p"), ("b", "q"), ("p", "q"), ("p", "r"), ("q", "r"), ("r", "s"), ("cbar", "t"), ("s", "t"), ("s", "T"),
      ("t", "T")]
fixedc = {"a": TRUE, "b": FALSE, "cbar": FALSE, "T": TRUE}
sols = []
for cols in itertools.product(range(3), repeat=5):
    c = dict(fixedc, **dict(zip("pqrst", cols)))
    if all(c[u] != c[v] for u, v in CE) and c["p"] != FALSE and c["q"] != TRUE:
        pass
    if all(c[u] != c[v] for u, v in CE):
        sols.append(c)
assert sols
col = sorted(sols, key=lambda c: [c[x] for x in "pqrst"])[0]
S = SVG(640, 266)
P1 = {"X": (80, 62), "T": (38, 140), "F": (122, 140)}
P2 = {"X": (220, 62), "a": (178, 140), "abar": (262, 140)}
P3 = {"a": (330, 50), "b": (330, 125), "cbar": (330, 200), "p": (395, 50), "q": (395, 125), "r": (455, 88),
      "s": (520, 88), "t": (520, 200), "T": (592, 144)}
cols1 = {"X": OTHER, "T": TRUE, "F": FALSE}
cols2 = {"X": OTHER, "a": TRUE, "abar": FALSE}
cols3 = dict(col)
for P, edges in ((P1, [("X", "T"), ("X", "F"), ("T", "F")]), (P2, [("X", "a"), ("X", "abar"), ("a", "abar")]),
                 (P3, CE)):
    for u, v in edges:
        (x1, y1), (x2, y2) = P[u], P[v]
        S.line(x1, y1, x2, y2, width=1.5)
for P, cols, names in ((P1, cols1, {"X": "X", "T": "T", "F": "F"}), (P2, cols2, {"X": "X", "a": "a", "abar": "a"}),
                       (P3, cols3, {"a": "a", "b": "b", "cbar": "c", "T": "T"})):
    for v, (x, y) in P.items():
        c = cols[v]
        S.circle(x, y, 15, stroke=COLOR[c], fill="var(--paper)", width=2.2)
        S.circle(x, y, 15, stroke="none", fill=COLOR[c], fill_opacity=0.22)
        if v in names:
            mathlabel(S, x, y + 1, names[v], neg=v in ("abar", "cbar"), size=16)
        else:
            S.text(x, y + 1, INIT[c], size=12, color=COLOR[c], weight="700")
S.text(80, 180, "truth gadget", size=12.5, color="var(--muted)")
S.text(220, 180, "variable gadget", size=12.5, color="var(--muted)")
S.text(470, 250, "clause gadget for (a ∨ b ∨ c̄)", size=12.5, color="var(--muted)")
S.text(458, 128, "majority", size=11.5, color="var(--muted)")
for nm, (dx, dy) in {"p": (0, -24), "q": (0, 24), "r": (0, -24), "s": (0, -24), "t": (0, 24)}.items():
    x, y = P3[nm]
    mathlabel(S, x + dx, y + dy, nm, size=13, color="var(--muted)")
for k, (c, name) in enumerate(((TRUE, "True"), (FALSE, "False"), (OTHER, "Other"))):
    x = 40 + k * 78
    S.circle(x, 222, 8, stroke=COLOR[c], fill="var(--paper)", width=2)
    S.circle(x, 222, 8, stroke="none", fill=COLOR[c], fill_opacity=0.22)
    S.text(x + 13, 222, f"{INIT[c]} = {name}", size=12, anchor="start")
S.line(150, 30, 150, 160, color="var(--muted)", width=1, dash="3 4")
S.line(292, 30, 292, 160, color="var(--muted)", width=1, dash="3 4")
html = S.figure(
    "<strong>The gadgets of 3Sat → 3Color</strong> (the book's Figures 12.12–12.13). The truth triangle names the "
    "three colors True, False and Other; each variable triangle forces <i>a</i> and <i>ā</i> to take opposite truth "
    "colors; the clause gadget (five new vertices, ten edges) joins the clause's three literal nodes to <i>T</i>. "
    "Shown: a valid coloring of the clause gadget with <i>a</i> True and <i>b</i>, <i>c̄</i> False. The left "
    "triangle acts as a majority gate: equal input colors force the same color at its tip. If all three literal "
    "nodes were False, both <i>s</i> and <i>t</i> (the right-hand pair) would have to be Other — impossible.",
    alt="three small graphs: a triangle T F X, a triangle a a-bar X, and a ten-edge clause gadget joining literal nodes a, b, c-bar to T, each vertex colored True, False or Other")
save("a12-coloring", html)

# =========================================================================== 6. the edge gadget of VertexCover -> HamCycle
S = SVG(660, 250)
ACC = dict(color="var(--accent)", width=2.6)
FAINT = dict(color="var(--muted)", width=1.1)
titles = ["the edge gadget for uv", "u ∈ C and v ∈ C", "only u ∈ C", "only v ∈ C"]
TOP, BOT = 84, 170
for k in range(4):
    if k == 0:
        x0, L, R = 0, 60, 190
    else:
        x0 = 230 + (k - 1) * 143
        L, R = x0 + 36, x0 + 106
    P = {"uvo": (L, TOP), "vuo": (R, TOP), "uvi": (L, BOT), "vui": (R, BOT)}
    used = {0: None, 1: {("uvi", "uvo"), ("vui", "vuo")}, 2: {("uvi", "vui"), ("vui", "vuo"), ("vuo", "uvo")},
            3: {("vui", "uvi"), ("uvi", "uvo"), ("uvo", "vuo")}}[k]
    stubs_used = {0: None, 1: {"L", "R"}, 2: {"L"}, 3: {"R"}}[k]

    def st(e):
        if used is None:
            return dict(color="currentColor", width=1.5)
        return ACC if e in used else FAINT

    def seg(a, b, bend=0):
        (x1, y1), (x2, y2) = P[a], P[b]
        dx, dy = x2 - x1, y2 - y1
        Ln = math.hypot(dx, dy)
        ux, uy = dx / Ln, dy / Ln
        sx, sy, ex, ey = x1 + ux * 9, y1 + uy * 9, x2 - ux * 11, y2 - uy * 11
        style = st((a, b))
        if bend:
            cx, cy = (sx + ex) / 2 - uy * bend, (sy + ey) / 2 + ux * bend
            S.path(f"M{sx:.1f},{sy:.1f} Q{cx:.1f},{cy:.1f} {ex:.1f},{ey:.1f}", arrow=True, **style)
        else:
            S.path(f"M{sx:.1f},{sy:.1f} L{ex:.1f},{ey:.1f}", arrow=True, **style)

    seg("uvi", "uvo")
    seg("vui", "vuo")
    seg("uvi", "vui", bend=-10)
    seg("vui", "uvi", bend=-10)
    seg("uvo", "vuo", bend=-10)
    seg("vuo", "uvo", bend=-10)
    for side, x in (("L", L), ("R", R)):
        sty = dict(color="currentColor", width=1.5) if stubs_used is None else (
            ACC if side in stubs_used else dict(color="var(--muted)", width=1.1, dash="3 3"))
        S.path(f"M{x},{BOT + 46} L{x},{BOT + 11}", arrow=True, **sty)
        S.path(f"M{x},{TOP - 9} L{x},{TOP - 44}", arrow=True, **sty)
    for v, (x, y) in P.items():
        S.circle(x, y, 8, width=1.6)
    S.text((L + R) / 2, 12, titles[k], size=12.5, weight="600" if k == 0 else None)
    mathlabel(S, L, 30, "u", size=14)
    mathlabel(S, R, 30, "v", size=14)
    if k == 0:
        for (x, y, t, anc) in ((L + 9, TOP + 24, "(u,v,out)", "start"), (R - 9, TOP + 24, "(v,u,out)", "end"),
                               (L + 9, BOT - 22, "(u,v,in)", "start"), (R - 9, BOT - 22, "(v,u,in)", "end")):
            S.text(x, y, t, size=11.5, anchor=anc, color="var(--muted)", font=SERIF_IT, italic=True)
    else:
        S.line(x0 - 4, 26, x0 - 4, 226, color="var(--muted)", width=1, dash="3 4")
S.text(60, 240, "u's chain ↑", size=11.5, color="var(--muted)")
S.text(190, 240, "v's chain ↑", size=11.5, color="var(--muted)")
html = S.figure(
    "<strong>The edge gadget for an edge <i>uv</i></strong> (the book's Figure 12.16): four vertices, six directed "
    "edges. The left column lies on <i>u</i>'s vertex chain, the right column on <i>v</i>'s (chains run upward; the "
    "stubs are the chain edges in and out). A Hamiltonian cycle can cross the gadget in only three ways: straight up "
    "both columns, or along one chain with a detour through the other column — which leaves the other chain's stubs "
    "unused. The vertex whose chain is used is in the cover; a detour means the other endpoint is not.",
    alt="four panels showing a four-vertex edge gadget and the three ways a Hamiltonian cycle can pass through it")
save("a12-vc-gadget", html)

# =========================================================================== 7. the repaired 3Sat -> HamCycle
FORM = [[("a", True), ("b", True)], [("a", False), ("b", False)]]
k = len(FORM)
order = ["a", "b"]
asg = {"a": True, "b": False}
num = {v: i + 1 for i, v in enumerate(order)}
Vh, Eh = [], set()
for i in (1, 2):
    Vh.append(("h", i))
    Vh += [(i, j) for j in range(3 * k + 1)]
    for j in range(1, 3 * k + 1):
        Eh |= {((i, j - 1), (i, j)), ((i, j), (i, j - 1))}
    i2 = i % 2 + 1
    Eh |= {(("h", i), (i, 0)), (("h", i), (i, 3 * k)), ((i, 0), ("h", i2)), ((i, 3 * k), ("h", i2))}
for j, cl in enumerate(FORM, start=1):
    Vh.append(("c", j))
    for v, p in cl:
        i = num[v]
        Eh |= ({((i, 3 * j - 2), ("c", j)), (("c", j), (i, 3 * j - 1))} if p else
               {((i, 3 * j - 1), ("c", j)), (("c", j), (i, 3 * j - 2))})
cyc = []
for i in (1, 2):
    cyc.append(("h", i))
    right = asg[order[i - 1]]
    cols = range(0, 3 * k + 1) if right else range(3 * k, -1, -1)
    for jj in cols:
        cyc.append((i, jj))
        for j, cl in enumerate(FORM, start=1):
            v, p = next((v, p) for v, p in cl if asg[v] == p)
            if num[v] == i and ((right and jj == 3 * j - 2) or (not right and jj == 3 * j - 1)):
                cyc.append(("c", j))
CYC = set(zip(cyc, cyc[1:] + cyc[:1]))
assert sorted(map(str, cyc)) == sorted(map(str, Vh)) and CYC <= Eh
XC = {j: 110 + 70 * j for j in range(3 * k + 1)}
YR = {1: 88, 2: 228}
POSH = {("h", 1): (320, 28), ("h", 2): (320, 158), ("c", 1): (215, 158), ("c", 2): (425, 158)}
for i in (1, 2):
    for j in range(3 * k + 1):
        POSH[(i, j)] = (XC[j], YR[i])
A = SVG(640, 300)
R = 9
CYS = dict(color="var(--accent)", width=2.4)
THIN = dict(color="var(--muted)", width=1.2)


def arrow_between(u, v, style):
    (x1, y1), (x2, y2) = POSH[u], POSH[v]
    r1 = 11 if u[0] in ("h", "c") else R
    r2 = 11 if v[0] in ("h", "c") else R
    dx, dy = x2 - x1, y2 - y1
    Ln = math.hypot(dx, dy)
    ux, uy = dx / Ln, dy / Ln
    A.path(f"M{x1 + ux * (r1 + 1):.1f},{y1 + uy * (r1 + 1):.1f} L{x2 - ux * (r2 + 3):.1f},{y2 - uy * (r2 + 3):.1f}",
           arrow=True, **style)


def wrap(u, style):
    x, y = POSH[u]
    side = -1 if u[1] == 0 else 1
    xo = 60 if side < 0 else 580
    hx = 320 + side * 13
    A.path(f"M{x + side * (R + 1)},{y} L{xo},{y} L{xo},{28} L{hx + side * 2},{28}", arrow=True, **style)


drawn_pairs = set()
for (u, v) in sorted(Eh, key=str):
    if isinstance(u[0], int) and isinstance(v[0], int):
        key = frozenset((u, v))
        if key in drawn_pairs:
            continue
        drawn_pairs.add(key)
        if (u, v) in CYC or (v, u) in CYC:
            a, b = (u, v) if (u, v) in CYC else (v, u)
            arrow_between(a, b, CYS)
        else:
            (x1, y1), (x2, y2) = POSH[u], POSH[v]
            sgn = 1 if x2 > x1 else -1
            A.line(x1 + sgn * R, y1, x2 - sgn * R, y2, **THIN)
        continue
    style = CYS if (u, v) in CYC else THIN
    if v == ("h", 1) and u[0] == 2:
        wrap(u, style)
    else:
        arrow_between(u, v, style)
for v, (x, y) in POSH.items():
    if v[0] == "c":
        A.rect(x - 11, y - 11, 22, 22, rx=3, stroke="var(--hi)", fill="var(--paper)", width=1.8)
        A.text(x, y + 1, str(v[1]), size=12, color="var(--hi)", weight="700")
    elif v[0] == "h":
        A.circle(x, y, 12, stroke="currentColor", fill="var(--paper)", width=1.8)
        mathlabel(A, x - 1, y, "h", sub=str(v[1]), size=13)
    else:
        spacer = v[1] % 3 == 0
        A.circle(x, y, R, stroke="currentColor", fill="var(--muted)" if spacer else "var(--paper)", width=1.5,
                 fill_opacity=0.35 if spacer else None)
for i, name, note in ((1, "a", "True →"), (2, "b", "← False")):
    mathlabel(A, 28, YR[i] - 8, name, size=16)
    A.text(28, YR[i] + 12, note, size=11.5, color="var(--accent)")
for j in range(3 * k + 1):
    A.text(XC[j], 256, str(j), size=11, color="var(--muted)")
A.text(320, 284, "positions 0–6; shaded: spacers 0, 3, 6; clause j sits at 3j − 2, 3j − 1", size=12,
       color="var(--muted)")
html = (f'<figure class="cs-fig">{A.svg("two rows of seven vertices with hub vertices and two clause vertices, and the Hamiltonian cycle for a true, b false highlighted")}'
        f'<figcaption><strong>3Sat → DirectedHamCycle, repaired</strong>, for (<i>a</i> ∨ <i>b</i>) ∧ (<i>ā</i> ∨ '
        f'<i>b̄</i>). Each variable has a row of 3<i>k</i> + 1 = 7 vertices (a thin segment is a pair of opposite '
        f'edges); shaded vertices are spacers, and clause <i>j</i> (red square) attaches at positions 3<i>j</i> − 2 '
        f'and 3<i>j</i> − 1 — a rightward detour for a positive literal, a leftward one for a negative literal. Hub '
        f'<i>h</i><sub><i>i</i></sub> leads into either end of row <i>i</i>, and both ends lead to the next hub '
        f'(row <i>b</i> wraps around to <i>h</i><sub>1</sub>). Blue: the Hamiltonian cycle for <i>a</i> = True, '
        f'<i>b</i> = False, which collects clause 1 on row <i>a</i> and clause 2 on row <i>b</i>. This graph has '
        f'exactly two Hamiltonian cycles, one per satisfying assignment.</figcaption></figure>')
save("a12-ham-3sat", html.replace("\n", " "))
