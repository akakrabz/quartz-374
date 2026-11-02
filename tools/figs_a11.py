#!/usr/bin/env python3
"""Figures for Algorithms Chapter 11 (applications of flows and cuts). Writes tools/figs/a11-<name>.html; then run
tools/assemble.py on the chapter page. Every flow value, matching, path cover and cut drawn here is computed by the
small max-flow routine below; tools/checks/a11.py re-checks the figure HTML independently."""
import itertools
import math
import os
from collections import deque

from figlib import SVG, Automaton

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


def maxflow(cap, s, t):
    """Edmonds–Karp. cap: dict (u, v) -> capacity. Returns (value, flow dict, source side of a minimum cut)."""
    res, adj = {}, {}
    for (u, v), c in cap.items():
        res[(u, v)] = res.get((u, v), 0) + c
        res.setdefault((v, u), 0)
        adj.setdefault(u, set()).add(v)
        adj.setdefault(v, set()).add(u)
    adj.setdefault(s, set())
    adj.setdefault(t, set())
    val = 0
    while True:
        pred, Q = {s: None}, deque([s])
        while Q and t not in pred:
            u = Q.popleft()
            for v in sorted(adj[u], key=str):
                if v not in pred and res[(u, v)] > 0:
                    pred[v] = u
                    Q.append(v)
        if t not in pred:
            break
        b, v = INF, t
        while pred[v] is not None:
            b = min(b, res[(pred[v], v)])
            v = pred[v]
        v = t
        while pred[v] is not None:
            u = pred[v]
            res[(u, v)] -= b
            res[(v, u)] += b
            v = u
        val += b
    flow = {e: max(0, c - res[e]) if c != INF else None for e, c in cap.items()}
    for e, c in cap.items():
        if c == INF:
            flow[e] = res[(e[1], e[0])] - cap.get((e[1], e[0]), 0)
    return val, flow, set(pred)


class Graph(Automaton):
    """Automaton plus undirected edges (no arrowhead)."""

    def uedge(self, a, b, color="currentColor", width=1.6, dash=None):
        A, B = self.states[a], self.states[b]
        dx, dy = B["x"] - A["x"], B["y"] - A["y"]
        sx, sy = self._boundary(A, dx, dy)
        ex, ey = self._boundary(B, -dx, -dy)
        self.edges.append(("raw", f'<line x1="{sx:.1f}" y1="{sy:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" stroke="{color}" '
                                  f'stroke-width="{width}" stroke-linecap="round"'
                                  + (f' stroke-dasharray="{dash}"' if dash else "") + "/>"))

    def svg(self, alt=""):
        raw = [e for e in self.edges if e[0] == "raw"]
        self.edges = [e for e in self.edges if e[0] != "raw"]
        before = self.items
        self.items = before + [r[1] for r in raw]
        out = super().svg(alt)
        self.items = before
        self.edges += raw
        return out


FLOW = dict(color="var(--accent)", width=2.6)
FLOW2 = dict(color="var(--accent2)", width=2.6)
PLAIN = dict(color="currentColor", width=1.3)
CUT = dict(color="var(--hi)", width=2.6)

# =========================================================================== 1. vertex splitting (bowtie)
BOW_V = ["s", "a", "b", "m", "c", "d", "t"]
BOW_E = [("s", "a"), ("s", "b"), ("a", "m"), ("b", "m"), ("m", "c"), ("m", "d"), ("c", "t"), ("d", "t")]
ev, ef, _ = maxflow({e: 1 for e in BOW_E}, "s", "t")
assert ev == 2


def split_cap(V, E, vcap, ecap=1):
    cap = {}
    for v in V:
        if v not in ("s", "t"):
            cap[(v + "_in", v + "_out")] = vcap
    io = lambda v, side: v if v in ("s", "t") else v + side
    for u, v in E:
        cap[(io(u, "_out"), io(v, "_in"))] = ecap
    return cap


SPL = split_cap(BOW_V, BOW_E, 1)
vv, vf, vS = maxflow(SPL, "s", "t")
assert vv == 1
assert vS == {"s", "a_in", "a_out", "b_in", "b_out", "m_in"}, vS  # minimum cut = the split edge of m
spl_path = [e for e, x in vf.items() if x]
assert sorted(spl_path) == sorted([("s", "a_in"), ("a_in", "a_out"), ("a_out", "m_in"), ("m_in", "m_out"),
                                   ("m_out", "c_in"), ("c_in", "c_out"), ("c_out", "t")]), spl_path

W, H = 600, 345
A = Graph(W, H, r=15)
LAB = SVG(W, H)
# top: G
TOP = {"s": (60, 85), "a": (170, 40), "b": (170, 130), "m": (280, 85), "c": (390, 40), "d": (390, 130),
       "t": (500, 85)}
for v, (x, y) in TOP.items():
    A.state("G" + v, x, y, label=v)
P1 = {("s", "a"), ("a", "m"), ("m", "c"), ("c", "t")}
P2 = {("s", "b"), ("b", "m"), ("m", "d"), ("d", "t")}
for u, v in BOW_E:
    st = FLOW if (u, v) in P1 else FLOW2
    A.edge("G" + u, "G" + v, color=st["color"], width=st["width"])
A.text(560, 22, "graph G", size=13, color="var(--muted)")
LAB.text(300, 160, "2 edge-disjoint paths, both through m", size=12.5, halo=True)
A.line(20, 178, 580, 178, color="var(--muted)", width=1, dash="3 4")
# bottom: split graph
Y0 = 255
BX = {"s": 40, "a": 140, "b": 140, "m": 280, "c": 420, "d": 420, "t": 540}
BY = {"s": Y0, "a": Y0 - 45, "b": Y0 + 45, "m": Y0, "c": Y0 - 45, "d": Y0 + 45, "t": Y0}
GAP = 23
for v in BOW_V:
    if v in ("s", "t"):
        A.state("H" + v, BX[v], BY[v], label=v)
    else:
        A.rect(BX[v] - GAP - 17, BY[v] - 17, 2 * GAP + 34, 34, rx=17, stroke="var(--muted)", fill="none",
               width=1, dash="3 3")
        A.state("H" + v + "_in", BX[v] - GAP, BY[v], label=v, r=12)
        A.state("H" + v + "_out", BX[v] + GAP, BY[v], label=v, r=12)
for (u, v), c in SPL.items():
    if vf[(u, v)]:
        st = CUT if (u, v) == ("m_in", "m_out") else FLOW
    else:
        st = PLAIN
    A.edge("H" + u, "H" + v, color=st["color"], width=st["width"])
A.text(560, 198, "split graph", size=13, color="var(--muted)")
LAB.text(280, Y0 - 30, "c(m) = 1", size=12.5, color="var(--hi)", halo=True)
LAB.text(300, 333, "every edge and every split edge has capacity 1: maximum flow 1", size=12.5, halo=True)
html = overlay_figure(A, LAB,
    "<strong>Edge-disjoint versus vertex-disjoint paths, and vertex splitting.</strong> Top: in <i>G</i> the two "
    "colored paths <i>s a m c t</i> and <i>s b m d t</i> share no edge, so <i>G</i> has 2 edge-disjoint paths "
    "from <i>s</i> to <i>t</i>; but both pass through <i>m</i>, and every path from <i>s</i> to <i>t</i> does, so "
    "<i>G</i> has only 1 vertex-disjoint path. Bottom: the split graph <i>Ḡ</i>, in which every vertex other than "
    "<i>s</i> and <i>t</i> becomes a pair <i>v</i><sub>in</sub> → <i>v</i><sub>out</sub> (left and right circle "
    "of each dashed box) and every edge <i>u</i>→<i>v</i> becomes <i>u</i><sub>out</sub> → <i>v</i><sub>in</sub>. "
    "With capacity 1 everywhere the maximum flow is 1 (thick path); the split edge of <i>m</i> (highlighted) is a "
    "minimum cut on its own.",
    alt="a bowtie graph with two edge-disjoint paths through a middle vertex m, and its split graph in which m's "
        "split edge of capacity 1 is a minimum cut")
save("a11-split", html)

# =========================================================================== 2. bipartite matching and its network
ML, MR = ["a", "b", "c"], ["x", "y", "z"]
ME = [("a", "x"), ("a", "y"), ("b", "x"), ("c", "y"), ("c", "z")]
M0 = {("a", "x"), ("c", "y")}
AP = ["b", "x", "a", "y", "c", "z"]
pe = {tuple(sorted(p)) for p in zip(AP, AP[1:])}
# alternating: edges alternate not-in-M / in-M, endpoints unmatched
matched0 = {v for e in M0 for v in e}
assert AP[0] not in matched0 and AP[-1] not in matched0
for i, (u, v) in enumerate(zip(AP, AP[1:])):
    e = (u, v) if u in ML else (v, u)
    assert (e in M0) == (i % 2 == 1)
M1 = (M0 - {e for e in M0 if tuple(sorted(e)) in pe}) | {e for e in ME if tuple(sorted(e)) in pe and e not in M0}
assert M1 == {("b", "x"), ("a", "y"), ("c", "z")}, M1
cap = {("s", l): 1 for l in ML}
cap.update({(l, r): 1 for l, r in ME})
cap.update({(r, "t"): 1 for r in MR})
mv, mf, _ = maxflow(cap, "s", "t")
assert mv == 3 and {(l, r) for l, r in ME if mf[(l, r)]} == M1
W, H = 640, 240
A = Graph(W, H, r=15)
LAB = SVG(W, H)
LY = {"a": 50, "b": 115, "c": 180, "x": 50, "y": 115, "z": 180}
for v in ML:
    A.state("L" + v, 50, LY[v], label=v)
for v in MR:
    A.state("L" + v, 210, LY[v], label=v)
for l, r in ME:
    if (l, r) in M0:
        A.uedge("L" + l, "L" + r, color=FLOW["color"], width=3.2)
    else:
        A.uedge("L" + l, "L" + r, color="var(--hi)", width=2.0, dash="6 4")
A.text(50, 18, "L", size=14, font="'STIX Two Math','Latin Modern Math',serif", italic=True)
A.text(210, 18, "R", size=14, font="'STIX Two Math','Latin Modern Math',serif", italic=True)
A.text(130, 222, "M = {ax, cy};  path b x a y c z", size=12.5)
A.line(290, 15, 290, 225, color="var(--muted)", width=1, dash="3 4")
NX = {"s": 330, "t": 610}
A.state("Ns", 330, 115, label="s")
A.state("Nt", 610, 115, label="t")
for v in ML:
    A.state("N" + v, 420, LY[v], label=v)
for v in MR:
    A.state("N" + v, 520, LY[v], label=v)
for (u, v), c in cap.items():
    st = FLOW if mf[(u, v)] else PLAIN
    A.edge("N" + u, "N" + v, color=st["color"], width=st["width"])
A.text(470, 222, "flow of value 3 = matching {bx, ay, cz}", size=12.5)
html = overlay_figure(A, LAB,
    "<strong>A bipartite graph and its flow network.</strong> Left: the matching <i>M</i> = {<i>ax</i>, <i>cy</i>} "
    "(thick) cannot be extended by any edge, yet it is not maximum: <i>b x a y c z</i> is an alternating path — "
    "it starts and ends at unmatched vertices and its edges alternate between dashed edges outside <i>M</i> and "
    "thick edges in <i>M</i> — and <i>M</i> ⊕ <i>P</i> = {<i>bx</i>, <i>ay</i>, <i>cz</i>} is a perfect matching. "
    "Right: the network <i>G</i>′ — edges oriented from <i>L</i> to <i>R</i>, a source <i>s</i> and a target "
    "<i>t</i>, every capacity 1 — with the maximum flow (thick, one unit per edge) that corresponds to that perfect "
    "matching.",
    alt="a bipartite graph with a maximal matching and an alternating path, and the corresponding flow network with "
        "a maximum flow of value 3")
save("a11-matching", html)

# =========================================================================== 3. disjoint-path cover of a dag
PC_V = ["a", "b", "c", "d", "e", "f"]
PC_E = [("a", "c"), ("a", "f"), ("b", "d"), ("c", "d"), ("c", "e"), ("d", "f")]
cap = {("s", u + "♭"): 1 for u in PC_V}
cap.update({(u + "♭", v + "♯"): 1 for u, v in PC_E})
cap.update({(v + "♯", "t"): 1 for v in PC_V})
pv, pf, _ = maxflow(cap, "s", "t")
PM = sorted((u, v) for u, v in PC_E if pf[(u + "♭", v + "♯")])
assert pv == 4 and len(PC_V) - pv == 2
COVER = [["a", "c", "e"], ["b", "d", "f"]]
assert sorted(e for p in COVER for e in zip(p, p[1:])) == PM, PM
W, H = 600, 270
A = Graph(W, H, r=15)
LAB = SVG(W, H)
DP = {"a": (40, 110), "c": (140, 110), "e": (240, 110), "b": (40, 210), "d": (175, 210), "f": (310, 210)}
for v, (x, y) in DP.items():
    A.state("D" + v, x, y, label=v)
for u, v in PC_E:
    if (u, v) in set(zip(COVER[0], COVER[0][1:])):
        st = FLOW
    elif (u, v) in set(zip(COVER[1], COVER[1][1:])):
        st = FLOW2
    else:
        st = PLAIN
    A.edge("D" + u, "D" + v, color=st["color"], width=st["width"], bend=(105 if (u, v) == ("a", "f") else 0))
A.text(175, 252, "cover: a c e and b d f", size=12.5)
A.line(355, 15, 355, 255, color="var(--muted)", width=1, dash="3 4")
for i, v in enumerate(PC_V):
    A.state("F" + v, 430, 30 + 40 * i, label=v + "♭", r=15)
    A.state("S" + v, 550, 30 + 40 * i, label=v + "♯", r=15)
for u, v in PC_E:
    if (u, v) in PM:
        A.uedge("F" + u, "S" + v, color=FLOW["color"], width=3.0)
    else:
        A.uedge("F" + u, "S" + v, color="currentColor", width=1.3)
html = overlay_figure(A, LAB,
    "<strong>A minimum disjoint-path cover from a maximum matching.</strong> Left: a dag <i>G</i> with 6 vertices "
    "and its minimum disjoint-path cover <i>a c e</i>, <i>b d f</i> (colored). Right: the bipartite graph "
    "<i>G</i>′ with an edge <i>u</i>♭<i>v</i>♯ for every edge <i>u</i>→<i>v</i> of <i>G</i>; its maximum "
    "matching (thick) has 4 edges, exactly the 4 edges of the cover, and 6 − 4 = 2 paths. Taking a longest path "
    "first, <i>a c d f</i>, is a mistake: it strands <i>b</i> and <i>e</i>, and the cover needs 3 paths.",
    alt="a six-vertex dag covered by two disjoint paths, and its split bipartite graph with a maximum matching of "
        "four edges")
save("a11-path-cover", html)

# =========================================================================== 4. baseball elimination network
TEAMS = ["NYY", "BAL", "BOS", "TOR"]
WINS = {"NYY": 75, "BAL": 71, "BOS": 69, "TOR": 63}
W_DET, R_DET = 49, 27
GAMES = {("NYY", "BAL"): 3, ("NYY", "BOS"): 8, ("NYY", "TOR"): 7, ("BAL", "BOS"): 2, ("BAL", "TOR"): 7,
         ("BOS", "TOR"): 0}
cap = {}
for (i, j), g in GAMES.items():
    if g:
        cap[("s", i + "-" + j)] = g
        cap[(i + "-" + j, i)] = INF
        cap[(i + "-" + j, j)] = INF
for i in TEAMS:
    cap[(i, "t")] = W_DET + R_DET - WINS[i]
bv, bf, bS = maxflow(cap, "s", "t")
total = sum(GAMES.values())
into_t = sum(W_DET + R_DET - WINS[i] for i in TEAMS)
assert (total, into_t, bv) == (27, 26, 26)
assert set(TEAMS) <= bS  # the minimum cut cuts all four team edges
W, H = 520, 345
A = Graph(W, H, r=16)
LAB = SVG(W, H)
A.state("s", 30, 165, label="s")
A.state("t", 490, 165, label="t")
gnames = [k for k, g in GAMES.items() if g]
for k, (i, j) in enumerate(gnames):
    A.state(i + "-" + j, 175, 35 + 65 * k, label=f"{i}·{j}", shape="rounded", w=74, r=14, italic=False)
TY = {"NYY": 60, "BAL": 130, "BOS": 200, "TOR": 270}
for i in TEAMS:
    A.state(i, 350, TY[i], label=i, shape="rounded", w=50, r=15, italic=False)
for (u, v), c in cap.items():
    if v == "t":
        A.edge(u, v, color=CUT["color"], width=CUT["width"])
    elif u == "s":
        A.edge(u, v, color="currentColor", width=1.5)
    else:
        A.edge(u, v, color="var(--muted)", width=1.2)
SL = {0: (-4, -10), 1: (-2, -8), 2: (0, -11), 3: (2, 8), 4: (4, 10)}
for k, (i, j) in enumerate(gnames):
    x1, y1, x2, y2 = 30, 165, 175 - 37, 35 + 65 * k
    px, py = x1 + 0.62 * (x2 - x1), y1 + 0.62 * (y2 - y1)
    LAB.text(px + SL[k][0], py + SL[k][1], str(GAMES[(i, j)]), size=13, halo=True)
for i in TEAMS:
    x1, y1, x2, y2 = 375, TY[i], 490, 165
    px, py = x1 + 0.45 * (x2 - x1), y1 + 0.45 * (y2 - y1)
    LAB.text(px, py - 9, str(W_DET + R_DET - WINS[i]), size=13, halo=True, color="var(--hi)", weight="600")
LAB.text(40, 333, f"out of s: {total} games", size=12.5, halo=True, anchor="start")
LAB.text(500, 333, f"into t: {' + '.join(str(W_DET + R_DET - WINS[i]) for i in TEAMS)} = {into_t}", size=12.5,
         halo=True, anchor="end", color="var(--hi)")
html = overlay_figure(A, LAB,
    "<strong>The baseball-elimination network for Detroit, August 30, 1996 (the book’s Figure 11.7).</strong> "
    "One vertex per pair of rivals with games left (Boston and Toronto have none) and one per rival team. An edge "
    "from <i>s</i> carries the number of games the pair still plays; the unlabeled edges have infinite capacity; "
    "the edge from a team to <i>t</i> allows 76 minus its current wins, 76 = 49 + 27 being Detroit’s best "
    "possible total. The four highlighted edges form a cut of capacity 26 &lt; 27, so no flow saturates every "
    "edge out of <i>s</i>: Detroit is eliminated.",
    alt="flow network with a source, five game vertices, four team vertices and a target; the four team-to-target "
        "edges form a cut of capacity 26")
save("a11-baseball", html)

# =========================================================================== 5. project selection network
PROFIT = {"A": -2, "B": -3, "C": -5, "D": -8, "p4": 4, "p6": 6, "p2": 2, "p3": 3}
DEPS = [("B", "A"), ("p4", "A"), ("p4", "B"), ("p6", "B"), ("p6", "p2"), ("p2", "C"), ("p3", "C"), ("p3", "D")]
cap = {}
for v, p in PROFIT.items():
    if p > 0:
        cap[("s", v)] = p
    elif p < 0:
        cap[(v, "t")] = -p
for u, v in DEPS:
    cap[(u, v)] = INF
Ppos = sum(p for p in PROFIT.values() if p > 0)
cv, cf, cS = maxflow(cap, "s", "t")
sel = cS - {"s"}
assert (Ppos, cv) == (15, 13) and sel == {"p4", "p6", "p2", "A", "B", "C"} and sum(PROFIT[v] for v in sel) == 2
cut_edges = [(u, v) for (u, v) in cap if u in cS and v not in cS]
assert sorted(cut_edges) == sorted([("A", "t"), ("B", "t"), ("C", "t"), ("s", "p3")])
W, H = 520, 330
A = Graph(W, H, r=16)
LAB = SVG(W, H)
PX = {"A": 80, "B": 200, "C": 320, "D": 440, "p4": 80, "p6": 200, "p2": 320, "p3": 440}
for v in PROFIT:
    y = 120 if PROFIT[v] < 0 else 215
    label = str(PROFIT[v]).replace("-", "−")
    inS = v in cS
    if PROFIT[v] < 0:
        A.state(v, PX[v], y, label=label, shape="rounded", w=34, r=15, italic=False,
                color="var(--accent)" if inS else "currentColor")
    else:
        A.state(v, PX[v], y, label=label, italic=False, color="var(--accent)" if inS else "currentColor")
A.state("s", 260, 305, label="s", color="var(--accent)")
A.state("t", 260, 25, label="t")
for (u, v), c in cap.items():
    if u in cS and v not in cS:
        st = CUT
    elif c == INF:
        st = dict(color="currentColor", width=1.4)
    else:
        st = dict(color="var(--muted)", width=1.3)
    A.edge(u, v, color=st["color"], width=st["width"])
for v, p in PROFIT.items():
    if p < 0:
        x1, y1 = PX[v], 120 - 15
        px, py = x1 + 0.45 * (260 - x1), y1 + 0.45 * (25 - y1)
        LAB.text(px - (8 if x1 < 260 else -8), py, str(-p), size=13, halo=True,
                 color="var(--hi)" if v in cS else "currentColor", weight="600" if v in cS else None)
    else:
        x1, y1 = PX[v], 215 + 16
        px, py = x1 + 0.4 * (260 - x1), y1 + 0.4 * (305 - y1)
        LAB.text(px - (8 if x1 < 260 else -8), py + 4, str(p), size=13, halo=True,
                 color="var(--hi)" if v not in cS else "currentColor", weight="600" if v not in cS else None)
INFL = {("B", "A"): (140, 108), ("p4", "A"): (68, 168), ("p4", "B"): (132, 158), ("p6", "B"): (188, 168),
        ("p6", "p2"): (260, 203), ("p2", "C"): (308, 168), ("p3", "C"): (392, 158), ("p3", "D"): (452, 168)}
for e, (x, y) in INFL.items():
    LAB.text(x, y, "∞", size=12, halo=True)
LAB.text(505, 300, "cut 2 + 3 + 5 + 3 = 13", size=12.5, halo=True, anchor="end", color="var(--hi)")
LAB.text(15, 300, "P = 15, profit 15 − 13 = 2", size=12.5, halo=True, anchor="start")
html = overlay_figure(A, LAB,
    "<strong>Project selection as a minimum cut (the book’s Figures 11.8 and 11.9).</strong> Circles are profitable "
    "projects, boxes costly ones, each labeled with its profit; an edge <i>u</i>→<i>v</i> of capacity ∞ means "
    "<i>u</i> needs <i>v</i>. Edges from <i>s</i> carry the profits, edges into <i>t</i> the costs. The minimum "
    "cut separates the source side (colored: <i>s</i>, the projects 4, 6, 2 and the costs 2, 3, 5) from the rest; "
    "its highlighted edges have capacity 13 — the profit 3 given up and the costs 2 + 3 + 5 paid — so the best "
    "selection earns 15 − 13 = 2.",
    alt="project-selection network with source at the bottom, target at the top, eight projects in two rows and "
        "the four edges of the minimum cut highlighted")
save("a11-projects", html)
