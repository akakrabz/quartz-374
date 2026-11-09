#!/usr/bin/env python3
"""Figures for Director's Cut note 8 (randomized minimum cut). Writes tools/figs/n08-<name>.html; then run
tools/assemble.py on content/4-lecture-notes/08-randomized-minimum-cut.md. Cut sizes and minimum cuts drawn here are
computed below by brute force; tools/checks/n08.py checks the same numbers independently."""
import itertools
import math
import os

from figlib import SVG, SERIF_IT

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")
os.makedirs(OUT, exist_ok=True)


def save(name, html):
    with open(os.path.join(OUT, name + ".html"), "w", encoding="utf-8") as f:
        f.write(html + "\n")
    print("wrote", name)


def min_cuts(V, E):
    best, arg = None, []
    v0 = V[0]
    for k in range(0, len(V) - 1):
        for X in itertools.combinations(V[1:], k):
            S = {v0, *X}
            c = sum(1 for u, v in E if (u in S) != (v in S))
            if best is None or c < best:
                best, arg = c, [S]
            elif c == best:
                arg.append(S)
    return best, arg


class UG(SVG):
    """Undirected multigraph drawing: vertices as small circles with outside labels; parallel edges as bows."""

    def __init__(self, w, h, r=7):
        super().__init__(w, h)
        self.P, self.r, self.lab, self.under = {}, r, [], []

    def vertex(self, v, x, y, lx=0, ly=-17, label=None, hi=False):
        self.P[v] = (x, y, lx, ly, v if label is None else label, hi)

    def edges(self, E, color=lambda e: "currentColor", width=lambda e: 1.5, dash=lambda e: None):
        seen = {}
        for e in E:
            key = frozenset(e)
            seen[key] = seen.get(key, 0) + 1
        done = {}
        for e in E:
            key = frozenset(e)
            k, tot = done.get(key, 0), seen[key]
            done[key] = k + 1
            (x1, y1, *_), (x2, y2, *_) = self.P[e[0]], self.P[e[1]]
            off = 0 if tot == 1 else (k - (tot - 1) / 2) * 22
            if off == 0:
                self.line(x1, y1, x2, y2, color=color(e), width=width(e), dash=dash(e))
            else:
                L = math.hypot(x2 - x1, y2 - y1)
                nx, ny = -(y2 - y1) / L, (x2 - x1) / L
                cx, cy = (x1 + x2) / 2 + nx * off, (y1 + y2) / 2 + ny * off
                self.path(f"M{x1:.1f},{y1:.1f} Q{cx:.1f},{cy:.1f} {x2:.1f},{y2:.1f}", color=color(e),
                          width=width(e), dash=dash(e))

    def draw_vertices(self):
        for v, (x, y, lx, ly, lab, hi) in self.P.items():
            col = "var(--hi)" if hi else "currentColor"
            self.circle(x, y, self.r, stroke=col, width=1.6)
            self.text(x + lx, y + ly, lab, size=15, font=SERIF_IT, italic=True, color=col)


# =========================================================================== 1. the multigraph of p. 1
EP1 = [("a", "c"), ("a", "g"), ("a", "d"), ("c", "d"), ("c", "g"), ("c", "g"), ("g", "d"),
       ("a", "b"), ("d", "e"), ("g", "h"),
       ("b", "e"), ("b", "h"), ("b", "f"), ("b", "f"), ("e", "h"), ("h", "f")]
lam, mcs = min_cuts(list("abcdefgh"), EP1)
assert lam == 3 and len(mcs) == 3
LEFT = set("acdg")
CROSS = [e for e in EP1 if (e[0] in LEFT) != (e[1] in LEFT)]
assert len(CROSS) == 3
G = UG(470, 215)
G.vertex("a", 110, 40, -14, -10)
G.vertex("b", 340, 40, 14, -10)
G.vertex("c", 30, 110, -14, 0)
G.vertex("d", 190, 110, 4, 18)
G.vertex("e", 260, 110, -4, 18, hi=True)
G.vertex("f", 420, 110, 15, 0, hi=True)
G.vertex("g", 110, 180, -14, 10)
G.vertex("h", 340, 180, 14, 10)
G.edges(EP1, color=lambda e: "var(--hi)" if e in CROSS else "currentColor",
        width=lambda e: 2.6 if e in CROSS else 1.5)
G.draw_vertices()
G.text(70, 206, "S = {a, c, d, g}", size=12.5, color="var(--accent)")
G.text(390, 206, "{b, e, f, h}", size=12.5, color="var(--accent2)")
html = G.figure(
    "<strong>A multigraph whose minimum cut has three edges (the note’s first figure, recomputed).</strong> It has "
    "8 vertices and 16 edges (two pairs are parallel). The thick edges <i>ab</i>, <i>de</i>, <i>gh</i> cross the "
    "cut ({<i>a</i>, <i>c</i>, <i>d</i>, <i>g</i>}, {<i>b</i>, <i>e</i>, <i>f</i>, <i>h</i>}). No cut has fewer "
    "than 3 crossing edges, and exactly two other cuts have 3: separating <i>e</i> alone or <i>f</i> alone (both "
    "have degree 3). A minimum cut need not be unique.",
    alt="eight vertices a to h; a left cluster a c d g and a right cluster b e f h joined by three edges")
save("n08-multigraph", html)

# =========================================================================== 2. contraction
E = [("u", "v"), ("u", "v"), ("u", "w"), ("v", "w"), ("v", "x"), ("w", "x"), ("w", "y"), ("x", "y"), ("x", "y")]
V = list("uvwxy")
lamG, mG = min_cuts(V, E)
sidesG = sorted("".join(sorted(S if len(S) <= 2 else set(V) - S)) for S in mG)
assert lamG == 3 and sidesG == ["u", "uv", "xy", "y"], sidesG
Ec = [("uv" if a in "uv" else a, "uv" if b in "uv" else b) for a, b in E if {a, b} != {"u", "v"}]
Vc = ["uv", "w", "x", "y"]
lamC, mC = min_cuts(Vc, Ec)
cutsC = {frozenset(S) if "uv" not in S else frozenset(set(Vc) - S) for S in mC}
assert len(E) == 9 and len(Ec) == 7 and lamC == 3 and cutsC == {frozenset(Vc) - {"uv"}, frozenset({"y"}),
                                                                   frozenset({"x", "y"})}, cutsC
C = UG(560, 190)
OX = 300
C.vertex("u", 40, 60, -14, -6)
C.vertex("v", 40, 140, -14, 6)
C.vertex("w", 130, 100, 0, -17)
C.vertex("x", 200, 150, 0, 19)
C.vertex("y", 230, 60, 12, -10)
C.edges(E, color=lambda e: "var(--hi)" if set(e) == {"u", "v"} else "currentColor",
        width=lambda e: 2.6 if set(e) == {"u", "v"} else 1.5)
C.vertex("uv", OX + 50, 100, -2, 20, label="uv", hi=True)
C.vertex("w2", OX + 130, 100, 0, -17, label="w")
C.vertex("x2", OX + 200, 150, 0, 19, label="x")
C.vertex("y2", OX + 230, 60, 12, -10, label="y")
ren = {"uv": "uv", "w": "w2", "x": "x2", "y": "y2"}
C.edges([(ren[a], ren[b]) for a, b in Ec])
C.draw_vertices()
C.line(262, 100, 322, 100, arrow=True, width=1.6, color="var(--muted)")
C.text(292, 86, "contract uv", size=11.5, color="var(--muted)")
C.text(130, 178, "G: 9 edges", size=12, color="var(--muted)")
C.text(OX + 140, 178, "G/{u,v}: 7 edges", size=12, color="var(--muted)")
html = C.figure(
    "<strong>Contracting an edge of a multigraph.</strong> Contracting (either copy of) <i>uv</i> merges <i>u</i> "
    "and <i>v</i>, deletes <em>both</em> <i>uv</i> edges (no self-loops) and keeps every other edge: <i>uw</i> and "
    "<i>vw</i> become two parallel edges. <i>G</i> has minimum cut 3, attained by four cuts — {<i>u</i>}, "
    "{<i>u</i>, <i>v</i>}, {<i>y</i>} and {<i>x</i>, <i>y</i>} against the rest. In <i>G</i>/{<i>u</i>, <i>v</i>} "
    "the minimum cut is still 3: the cut {<i>u</i>}, which the thick edges cross, is gone; the other three survive "
    "with the same three crossing edges each.",
    alt="a five-vertex multigraph with a double edge uv, and the four-vertex multigraph after contracting uv")
save("n08-contraction", html)
