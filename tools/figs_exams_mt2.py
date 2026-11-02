#!/usr/bin/env python3
"""Figures for the Midterm 2 practice pages (content/3-homework-and-exams/midterm-2-*.md).
Writes tools/figs/exam-mt2*.html; then run tools/assemble.py on those pages.
Every graph and number drawn here is verified in tools/checks/exams_mt2.py."""
import os
from figlib import Automaton, SVG, MONO, SANS

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")
os.makedirs(OUT, exist_ok=True)


def save(name, html):
    with open(os.path.join(OUT, name + ".html"), "w", encoding="utf-8") as f:
        f.write(html + "\n")
    print("wrote", name)


# =====================================================================================================
# Practice test 1, Problem 2: the handout's quadhopper puzzle and a longest move sequence
# =====================================================================================================
H = [(1, 8, 4, 2), (5, 2, 3, 6), (13, 67, 42, 86), (3, 8, 9, 4), (7, 2, 1, 6), (3, 8, 4, 9), (6, 9, 7, 10),
     (4, 8, 6, 3), (5, 7, 2, 9), (1, 4, 3, 8), (5, 9, 7, 2), (10, 2, 7, 6), (3, 5, 1, 4)]
MAXMOVES = [7, 6, 1, 4, 5, 4, 2, 3, 3, 3, 2, 1, 1]
BEST = [(1, 1), (2, 3), (5, 1), (6, 3), (9, 2), (11, 2), (13, 1)]      # (square, hop)
GREEDY = [(1, 1), (2, 2), (4, 3), (7, 6), (13, 1)]
S = SVG(650, 234, font_size=13)
x0, cw, gap = 74, 38, 5
top = 78


def cx(i):  # centre of square i (1-based)
    return x0 + (i - 1) * (cw + gap) + cw / 2


for i in range(1, 14):
    x = x0 + (i - 1) * (cw + gap)
    S.rect(x, top, cw, 40, rx=3, width=1.3)
    a, b, c, d = H[i - 1]
    for (val, dx, dy) in ((a, 10, 11), (b, 28, 11), (c, 10, 29), (d, 28, 29)):
        used_best = (i, val) in BEST
        S.text(x + dx, top + dy, str(val), size=11, color="var(--accent)" if used_best else "currentColor",
               weight="700" if used_best else None)
    S.text(cx(i), top + 52, str(i), size=10.5, color="var(--muted)")
    S.text(cx(i), top + 68, str(MAXMOVES[i - 1]), size=11.5, font=MONO, weight="600")
S.text(x0 - 8, top + 52, "square", size=10.5, color="var(--muted)", anchor="end")
S.text(x0 - 8, top + 68, "MaxMoves", size=10.5, color="var(--muted)", anchor="end")
for (i, d) in BEST:
    j = i + d
    xa, xb = cx(i), (cx(j) if j <= 13 else cx(13) + 32)
    h = 16 + 7 * min(d, 4)
    S.path(f"M{xa},{top - 2} Q{(xa + xb) / 2},{top - 2 - 2 * h} {xb},{top - 4}", color="var(--accent)", width=1.8,
           arrow=True)
yb = top + 80
for (i, d) in GREEDY:
    j = i + d
    xa, xb = cx(i), (cx(j) if j <= 13 else cx(13) + 32)
    h = 12 + 4 * min(d, 6)
    S.path(f"M{xa},{yb} Q{(xa + xb) / 2},{yb + 2 * h} {xb},{yb + 2}", color="var(--hi)", width=1.5,
           arrow=True, dash="4 3")
S.text(x0, 14, "longest: 7 moves (hops 1, 3, 1, 3, 2, 2, 1)", size=12, anchor="start", color="var(--accent)",
       weight="600")
S.text(x0, 226, "greedy, smallest number first: 5 moves (hops 1, 2, 3, 6, 1)", size=12, anchor="start",
       color="var(--hi)", weight="600")
save("exam-mt2p1-quadhopper", S.figure(
    "<strong>The handout's puzzle.</strong> Each box is a square with its four numbers; under it, the square's index "
    "and the value of <i>MaxMoves</i>, the most moves that can still be made from that square. Top arcs: a longest "
    "sequence, 7 moves (the numbers used are bold). Dashed arcs below: always taking the smallest number, which makes "
    "only 5 moves — the jump of 6 from square 7 skips everything.",
    alt="thirteen squares of four numbers each, with the longest move sequence drawn above and the greedy one below"))

# =====================================================================================================
# Practice test 2, Problem 1: the graph and three trees
# =====================================================================================================
EDGES = [("t", "u", 4), ("t", "v", 3), ("t", "x", 6), ("t", "y", 2), ("u", "x", 1), ("u", "z", 4), ("v", "u", 2),
         ("v", "w", 6), ("v", "z", -2), ("w", "u", 5), ("w", "y", 2), ("w", "z", 4), ("y", "x", 2), ("z", "x", 1),
         ("z", "y", -7)]
POS = {"t": (40, 62), "u": (130, 62), "v": (220, 62), "w": (175, 132), "x": (40, 202), "y": (130, 202),
       "z": (220, 202)}
BEND = {("t", "v"): 22, ("z", "x"): 26}
LABEL = {("t", "u"): dict(label_side=1), ("t", "x"): dict(label_side=-1), ("u", "x"): dict(label_pos=0.3),
         ("t", "y"): dict(label_pos=0.3, label_side=-1), ("w", "u"): dict(label_side=1),
         ("w", "y"): dict(label_side=-1), ("v", "w"): dict(label_side=-1), ("w", "z"): dict(label_side=1),
         ("v", "z"): dict(label_side=-1), ("u", "z"): dict(label_pos=0.5), ("t", "v"): dict(label_pos=0.5)}
TREES = {
    "given": ("the graph", []),
    "a": ("(a) depth-first tree from v", [("v", "u"), ("u", "x"), ("u", "z"), ("z", "y"), ("v", "w")]),
    "b": ("(b) breadth-first tree from w", [("w", "u"), ("w", "y"), ("w", "z"), ("u", "x")]),
    "c": ("(c) shortest-path tree from t", [("t", "u"), ("t", "v"), ("v", "w"), ("v", "z"), ("z", "y"),
                                            ("y", "x")]),
}
ROOT = {"a": "v", "b": "w", "c": "t"}
DIST = {"t": "0", "u": "4", "v": "3", "w": "9", "x": "−4", "y": "−6", "z": "1"}
G = Automaton(640, 560, r=14, font_size=13)
offs = {"given": (10, 20), "a": (320, 20), "b": (10, 300), "c": (320, 300)}
for key, (title, tree) in TREES.items():
    ox, oy = offs[key]
    G.text(ox + 6, oy + 2, title, size=13, anchor="start", weight="600",
           color="currentColor" if key == "given" else "var(--accent)")
    reach = None
    if key in ("a", "b"):
        reach = {ROOT[key]} | {b for a, b in tree}
    for v, (x, y) in POS.items():
        dim = reach is not None and v not in reach
        G.state(key + v, ox + x, oy + y, label=v, color="var(--muted)" if dim else "currentColor",
                hi=(key in ROOT and v == ROOT[key]))
    for (a, b, w) in EDGES:
        on = (a, b) in tree
        if (a, b) == ("u", "z"):   # drawn by hand: up from u, over v, down the right side into z
            (ux, uy), (zx, zy) = POS["u"], POS["z"]
            col = "var(--accent)" if on else ("currentColor" if key == "given" else "var(--muted)")
            G.path(f"M{ox + ux + 4},{oy + uy - 14} C{ox + ux + 20},{oy + uy - 64} {ox + zx + 72},{oy + uy - 50} "
                   f"{ox + zx + 14},{oy + zy - 12}", color=col, width=3.0 if on else (1.6 if key == "given" else 1.0),
                   arrow=True)
            if key in ("given", "c"):
                G.text(ox + zx + 45, oy + 104, "4", size=13, halo=True)
            continue
        kw = dict(LABEL.get((a, b), {}))
        G.edge(key + a, key + b, str(w) if key in ("given", "c") else "", bend=BEND.get((a, b), 0),
               color="var(--accent)" if on else ("currentColor" if key == "given" else "var(--muted)"),
               width=3.0 if on else (1.6 if key == "given" else 1.0), label_dist=10, mono=False, **kw)
save("exam-mt2p2-trees", G.figure(
    "<strong>Practice test 2, Problem 1.</strong> Top left, the graph (it is a dag; its only topological order is "
    "<i>t, v, w, u, z, y, x</i>). The other panels mark the requested trees in color, with out-neighbors taken in "
    "alphabetical order; grayed vertices are not reachable from the root (circled in red). The distances from <i>t</i>: "
    "<i>u</i> 4, <i>v</i> 3, <i>w</i> 9, <i>x</i> −4, <i>y</i> −6, <i>z</i> 1.",
    alt="a seven-vertex weighted dag drawn four times, with a depth-first tree, a breadth-first tree and a "
        "shortest-path tree highlighted"))

# =====================================================================================================
# Practice test 3, Problem 1(b) and 1(c)
# =====================================================================================================
D = Automaton(560, 150, r=17, font_size=14)
D.text(14, 14, "(b)", size=13, anchor="start", weight="600")
D.state("s", 60, 80)
D.state("a", 150, 40)
D.state("b", 150, 120)
D.state("t", 240, 80)
for a, b in (("s", "a"), ("s", "b"), ("a", "t"), ("b", "t")):
    D.edge(a, b)
D.text(300, 14, "(c)", size=13, anchor="start", weight="600")
D.state("s2", 340, 80, label="s")
D.state("a2", 430, 40, label="a")
D.state("b2", 430, 120, label="b")
D.state("t2", 520, 80, label="t")
D.edge("s2", "a2", "1", mono=False)
D.edge("a2", "t2", "4", mono=False)
D.edge("s2", "b2", "2", label_side=-1, mono=False)
D.edge("b2", "t2", "3", label_side=-1, mono=False)
save("exam-mt2p3-small-graphs", D.figure(
    "<strong>Practice test 3, Problem 1(b) and (c).</strong> (b) One source <i>s</i>, one sink <i>t</i>, and two "
    "topological orders, <i>s, a, b, t</i> and <i>s, b, a, t</i>. (c) Distinct positive weights 1, 2, 3, 4, and two "
    "shortest paths from <i>s</i> to <i>t</i>, both of length 5.",
    alt="two four-vertex graphs: a diamond-shaped dag, and the same diamond with weights 1, 4 on top and 2, 3 below"))

# =====================================================================================================
# Practice test 3, Problem 5: the handout's zigzag walk, and the two-copy graph
# =====================================================================================================
Z = Automaton(620, 230, r=15, font_size=13)
Z.text(10, 14, "the handout's graph", size=12.5, anchor="start", weight="600")
P = {"a": (40, 70), "b": (130, 70), "c": (220, 70), "d": (40, 170), "e": (130, 170), "f": (220, 170)}
for v, (x, y) in P.items():
    Z.state(v, x, y)
WALK = {("a", "b"), ("d", "b"), ("d", "f"), ("c", "f"), ("c", "e")}
for a, b in ["ab", "bc", "ca", "be", "bf", "ce", "cf", "db", "ed", "df"]:
    on = (a, b) in WALK
    Z.edge(a, b, bend={("c", "a"): 24, ("d", "f"): -26}.get((a, b), 0),
           color="var(--accent)" if on else "currentColor", width=2.8 if on else 1.3)
Z.text(130, 214, "a → b ← d → f ← c → e", size=12.5, color="var(--accent)", weight="600")
# the gadget
Z.text(330, 14, "one edge u → v of weight w becomes two edges", size=12.5, anchor="start", weight="600")
Z.state("uF", 380, 70, label="u,F", shape="rounded", w=44, italic=False)
Z.state("vF", 560, 70, label="v,F", shape="rounded", w=44, italic=False, color="var(--muted)")
Z.state("uB", 380, 170, label="u,B", shape="rounded", w=44, italic=False, color="var(--muted)")
Z.state("vB", 560, 170, label="v,B", shape="rounded", w=44, italic=False)
Z.edge("uF", "vB", "w", bend=10, color="var(--accent)", width=2.0, mono=False, label_pos=0.35)
Z.edge("vB", "uF", "w", bend=10, color="var(--accent2)", width=2.0, mono=False, label_pos=0.35)
Z.text(470, 214, "F: next edge forward · B: next edge backward", size=11.5, color="var(--muted)")
save("exam-mt2p3-zigzag", Z.figure(
    "<strong>Zigzag walks.</strong> Left: the handout's example, every edge of weight 1; the highlighted walk "
    "<i>a → b ← d → f ← c → e</i> has length 5, and no zigzag walk from <i>a</i> to <i>e</i> is shorter. Right: the "
    "reduction. A vertex remembers whether the next edge must be followed forward (F) or backward (B); the edge "
    "<i>u → v</i> is followed forward from (<i>u</i>, F) to (<i>v</i>, B), and backward from (<i>v</i>, B) to "
    "(<i>u</i>, F).",
    alt="the six-vertex example graph with a zigzag walk highlighted, and the two directed edges that replace one edge "
        "in the reduction"))
