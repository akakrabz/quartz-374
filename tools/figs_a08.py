#!/usr/bin/env python3
"""Figures for Algorithms Chapter 8 (shortest paths). Writes tools/figs/a08-<name>.html; then run
tools/assemble.py on the chapter page. Every distance, predecessor and queue label drawn here is computed by running
the algorithms (minimal re-implementations below); tools/checks/a08.py re-checks the figure HTML against its own
transcriptions of the page's pseudocode."""
import math
import os
from collections import deque

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


def fmt_d(x):
    if x == INF:
        return "∞"
    return str(x).replace("-", "−")


# ------------------------------------------------------------------ minimal algorithms (independent of the checks)
def dijkstra(V, E, s):
    adj = {v: [] for v in V}
    for u, v, w in E:
        adj[u].append((v, w))
    dist = {v: INF for v in V}
    pred = {v: None for v in V}
    dist[s] = 0
    pq = {s: 0}
    while pq:
        u = min(pq, key=lambda x: (pq[x], V.index(x)))
        del pq[u]
        for v, w in adj[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                pred[v] = u
                pq[v] = dist[v]
    return dist, pred


def bellman_ford(V, E, s):
    dist = {v: INF for v in V}
    pred = {v: None for v in V}
    dist[s] = 0
    for _ in range(len(V) - 1):
        for u, v, w in E:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                pred[v] = u
    assert not any(dist[u] + w < dist[v] for u, v, w in E)
    return dist, pred


def bfs_phases(V, E, s):
    adj = {v: [] for v in V}
    for u, v in E:
        adj[u].append(v)
    dist = {v: INF for v in V}
    pred = {v: None for v in V}
    dist[s] = 0
    Q = deque([s, "T"])
    pulled, queues = [], []
    while any(x != "T" for x in Q):
        u = Q.popleft()
        pulled.append(u)
        if u == "T":
            queues.append([x for x in Q])
            Q.append("T")
            continue
        for v in adj[u]:
            if dist[v] > dist[u] + 1:
                dist[v] = dist[u] + 1
                pred[v] = u
                Q.append(v)
    return dist, pred, pulled, queues


class Graph(Automaton):
    """Automaton plus undirected edges (no arrowhead) and distance tags."""

    def uedge(self, a, b, label="", color="currentColor", width=1.6, dash=None, ldx=0, ldy=0, lcolor=None):
        A, B = self.states[a], self.states[b]
        dx, dy = B["x"] - A["x"], B["y"] - A["y"]
        sx, sy = self._boundary(A, dx, dy)
        ex, ey = self._boundary(B, -dx, -dy)
        self.edges.append(("raw", f'<line x1="{sx:.1f}" y1="{sy:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" stroke="{color}" '
                                  f'stroke-width="{width}" stroke-linecap="round"'
                                  + (f' stroke-dasharray="{dash}"' if dash else "") + "/>"))
        if label:
            L = math.hypot(dx, dy)
            nx, ny = dy / L, -dx / L
            mx, my = (sx + ex) / 2, (sy + ey) / 2
            self.lab.append((mx + ldx, my + ldy, label, lcolor or "currentColor"))

    def svg(self, alt=""):
        raw = [e for e in self.edges if e[0] == "raw"]
        self.edges = [e for e in self.edges if e[0] != "raw"]
        before = self.items
        self.items = before + [r[1] for r in raw]
        out = super().svg(alt)
        self.items = before
        self.edges += raw
        return out


def tag(S, x, y, s, color="var(--accent)", size=13, anchor="middle", weight="600"):
    S.text(x, y, s, size=size, color=color, halo=True, anchor=anchor, weight=weight)


TREE = dict(color="var(--accent)", width=2.6)
PLAIN = dict(color="currentColor", width=1.3)
MUTED = dict(color="var(--muted)", width=1.2)

# =========================================================================== 1. MST versus shortest-path tree
FAN_V = "sabcd"
FAN_E = [("s", "a", 5), ("s", "b", 6), ("s", "c", 7), ("s", "d", 8), ("a", "b", 2), ("b", "c", 3), ("c", "d", 4)]
# Kruskal
par = {v: v for v in FAN_V}


def find(x):
    while par[x] != x:
        x = par[x]
    return x


mst = []
for u, v, w in sorted(FAN_E, key=lambda e: e[2]):
    if find(u) != find(v):
        par[find(u)] = find(v)
        mst.append((u, v))
UND = [(u, v, w) for u, v, w in FAN_E] + [(v, u, w) for u, v, w in FAN_E]
fdist, fpred = dijkstra(list(FAN_V), UND, "s")
spt = [(fpred[v], v) for v in FAN_V if v != "s"]
w_mst = sum(w for u, v, w in FAN_E if (u, v) in mst or (v, u) in mst)
w_spt = sum(w for u, v, w in FAN_E if (u, v) in spt or (v, u) in spt)
assert sorted(map(sorted, mst)) == [["a", "b"], ["a", "s"], ["b", "c"], ["c", "d"]] and w_mst == 14
assert sorted(spt) == [("s", "a"), ("s", "b"), ("s", "c"), ("s", "d")] and w_spt == 26
assert fdist == {"s": 0, "a": 5, "b": 6, "c": 7, "d": 8}

POS = {"s": (150, 190), "a": (40, 112), "b": (100, 40), "c": (200, 40), "d": (260, 112)}
A = Graph(620, 250, r=16)
LAB = SVG(620, 250)
A.lab = []
for panel, x0 in ((0, 0), (1, 320)):
    for v in FAN_V:
        A.state(f"{v}{panel}", x0 + POS[v][0], POS[v][1], label=v)
    for u, v, w in FAN_E:
        if panel == 0:
            inT = (u, v) in mst or (v, u) in mst
            st = TREE if inT else PLAIN
            A.uedge(f"{u}{panel}", f"{v}{panel}", color=st["color"], width=st["width"])
        else:
            inT = (u, v) in spt
            if inT:
                A.edge(f"{u}{panel}", f"{v}{panel}", color=TREE["color"], width=TREE["width"])
            else:
                A.uedge(f"{u}{panel}", f"{v}{panel}", color=PLAIN["color"], width=PLAIN["width"])
    # weight labels
    WL = {("s", "a"): (-10, 8), ("s", "b"): (-11, 2), ("s", "c"): (11, 2), ("s", "d"): (10, 8),
          ("a", "b"): (-10, -6), ("b", "c"): (0, -11), ("c", "d"): (10, -6)}
    for u, v, w in FAN_E:
        (x1, y1), (x2, y2) = POS[u], POS[v]
        dx, dy = WL[(u, v)]
        LAB.text(x0 + (x1 + x2) / 2 + dx, (y1 + y2) / 2 + dy, str(w), size=13, halo=True)
    if panel == 1:
        for v in FAN_V:
            x, y = POS[v]
            off = {"s": (0, 27), "a": (-27, -6), "b": (-4, -27), "c": (4, -27), "d": (27, -6)}[v]
            tag(LAB, x0 + x + off[0], y + off[1], fmt_d(fdist[v]))
A.text(150, 236, f"minimum spanning tree: weight {w_mst}", size=13, color="currentColor")
A.text(470, 236, f"shortest-path tree from s: weight {w_spt}", size=13, color="currentColor")
A.line(310, 20, 310, 220, color="var(--muted)", width=1, dash="3 4")
html = overlay_figure(A, LAB,
    "<strong>Two optimal spanning trees of the same graph.</strong> Left: the minimum spanning tree uses the "
    "cheap rim edges and one spoke (total weight 14), but its path from <i>s</i> to <i>d</i> has length "
    "5 + 2 + 3 + 4 = 14. Right: the shortest-path tree from <i>s</i> uses the four spokes (total weight 26), and "
    "the label at each vertex is its distance from <i>s</i>. The two trees share only <i>sa</i>, the lightest edge "
    "at <i>s</i>.",
    alt="an undirected fan graph drawn twice, once with its minimum spanning tree and once with its shortest-path tree from s")
save("a08-sp-tree", html)

# =========================================================================== 2. negative cycle; undirected negative edge
NC_E = [("s", "a", 5), ("a", "b", 2), ("b", "c", -8), ("c", "t", 3), ("c", "d", 1), ("d", "a", 4)]
cyc = 2 - 8 + 1 + 4
assert cyc == -1
A = Graph(640, 230, r=16)
A.lab = []
LAB = SVG(640, 230)
P = {"s": (30, 100), "a": (120, 100), "b": (190, 34), "c": (260, 100), "d": (190, 166), "t": (350, 100)}
for v, (x, y) in P.items():
    A.state(v, x, y)
CYC = {("a", "b"), ("b", "c"), ("c", "d"), ("d", "a")}
for u, v, w in NC_E:
    if (u, v) in CYC:
        A.edge(u, v, color="var(--hi)", width=2.4)
    else:
        A.edge(u, v, color="currentColor", width=1.5)
NCL = {("s", "a"): (75, 89), ("a", "b"): (145, 58), ("b", "c"): (238, 58), ("c", "t"): (305, 89),
       ("c", "d"): (238, 143), ("d", "a"): (145, 143)}
for u, v, w in NC_E:
    LAB.text(*NCL[(u, v)], fmt_d(w), size=13, halo=True)
LAB.text(190, 100, f"weight {fmt_d(cyc)}", size=12.5, color="var(--hi)", halo=True)
A.text(190, 212, "a walk can loop around a b c d forever", size=12.5)
A.line(392, 16, 392, 214, color="var(--muted)", width=1, dash="3 4")
# undirected triangle, twice: shortest path to u and to v
TRI = [("s", "u", 1), ("s", "v", 1), ("u", "v", -1)]
for k, (x0, target) in enumerate(((410, "u"), (530, "v"))):
    TP = {"s": (x0 + 50, 40), "u": (x0 + 10, 130), "v": (x0 + 90, 130)}
    for v, (x, y) in TP.items():
        A.state(f"{v}{k}", x, y, label=v, r=14)
    path = ["s", "v", "u"] if target == "u" else ["s", "u", "v"]
    pe = set(zip(path, path[1:]))
    for a, b, w in TRI:
        if (a, b) in pe:
            A.edge(f"{a}{k}", f"{b}{k}", color="var(--accent)", width=2.4)
        elif (b, a) in pe:
            A.edge(f"{b}{k}", f"{a}{k}", color="var(--accent)", width=2.4)
        else:
            A.uedge(f"{a}{k}", f"{b}{k}", color="currentColor", width=1.4)
    for a, b, w in TRI:
        (x1, y1), (x2, y2) = TP[a], TP[b]
        off = {("s", "u"): (-11, -4), ("s", "v"): (11, -4), ("u", "v"): (0, 12)}[(a, b)]
        LAB.text((x1 + x2) / 2 + off[0], (y1 + y2) / 2 + off[1], fmt_d(w), size=13, halo=True)
    LAB.text(x0 + 50, 172, f"to {target}: {' '.join(path)}", size=12.5, halo=True)
    LAB.text(x0 + 50, 190, "length 0", size=12.5, halo=True)
A.text(520, 212, "undirected: no tree of shortest paths", size=12.5)
html = overlay_figure(A, LAB,
    "<strong>Negative edges.</strong> Left (the book’s Figure 8.3): the cycle <i>a</i>→<i>b</i>→<i>c</i>→<i>d</i>→<i>a</i> "
    "has weight 2 − 8 + 1 + 4 = −1, and every walk from <i>s</i> to <i>t</i> passes through it, so each extra lap "
    "shortens the walk by 1 and there is no shortest walk from <i>s</i> to <i>t</i>. Right (the book’s Figure 8.4): "
    "in the undirected triangle the shortest paths from <i>s</i> to <i>u</i> and to <i>v</i> are unique, both of "
    "length 0, but together they use all three edges, so they do not form a tree; the subpath <i>s v</i> of the "
    "first is not a shortest path to <i>v</i>.",
    alt="a directed graph with a negative cycle, and an undirected triangle with one negative edge whose shortest paths do not form a tree")
save("a08-negative", html)

# =========================================================================== 3. relaxing a tense edge
A = Graph(620, 200, r=17)
A.lab = []
LAB = SVG(620, 200)
for k, x0 in enumerate((0, 320)):
    A.state(f"s{k}", x0 + 30, 100, label="s")
    A.state(f"x{k}", x0 + 140, 40, label="x")
    A.state(f"u{k}", x0 + 140, 160, label="u")
    A.state(f"v{k}", x0 + 250, 100, label="v")
    A.edge(f"s{k}", f"x{k}", color="var(--muted)", width=1.4, dash="2 4", bend=-4)
    A.edge(f"s{k}", f"u{k}", color="var(--muted)", width=1.4, dash="2 4", bend=4)
    if k == 0:
        A.edge(f"x{k}", f"v{k}", color=TREE["color"], width=TREE["width"])
        A.edge(f"u{k}", f"v{k}", color="var(--hi)", width=2.2, dash="7 4")
    else:
        A.edge(f"x{k}", f"v{k}", color="currentColor", width=1.4)
        A.edge(f"u{k}", f"v{k}", color=TREE["color"], width=TREE["width"])
    LAB.text(x0 + 205, 58, "2", size=13, halo=True)
    LAB.text(x0 + 205, 144, "4", size=13, halo=True)
    tag(LAB, x0 + 140, 14, "7")
    tag(LAB, x0 + 140, 188, "3")
    tag(LAB, x0 + 30, 72, "0")
    tag(LAB, x0 + 280, 76, "9" if k == 0 else "7", color="var(--hi)" if k == 0 else "var(--accent)")
LAB.text(150, 100, "3 + 4 < 9: tense", size=12.5, color="var(--hi)", halo=True)
LAB.text(470, 100, "Relax(u→v)", size=12.5, color="var(--accent)", halo=True)
A.line(305, 10, 305, 190, color="var(--muted)", width=1, dash="3 4")
html = overlay_figure(A, LAB,
    "<strong>A tense edge and its relaxation.</strong> Numbers in color are the current values of <i>dist</i>; "
    "thick edges are predecessor pointers, dotted curves the tentative paths from <i>s</i>. Left: "
    "<i>dist</i>(<i>u</i>) + <i>w</i>(<i>u</i>→<i>v</i>) = 3 + 4 = 7 &lt; 9 = <i>dist</i>(<i>v</i>), so "
    "<i>u</i>→<i>v</i> is tense: the path to <i>u</i> followed by <i>u</i>→<i>v</i> beats the current path to "
    "<i>v</i> through <i>x</i>. Right: Relax(<i>u</i>→<i>v</i>) sets <i>dist</i>(<i>v</i>) ← 7 and "
    "<i>pred</i>(<i>v</i>) ← <i>u</i>; now no edge into <i>v</i> is tense.",
    alt="two panels: before and after relaxing the tense edge from u to v")
save("a08-relax", html)

# =========================================================================== 4. BFS by layers (book Figure 8.6)
BV = "sabcdefgh"
BE = [tuple(e) for e in "sb sd as cs bc ba dc dg cg cf ae eh eb fe fb gf hf hg".split()]
bdist, bpred, bpulled, bqueues = bfs_phases(list(BV), BE, "s")
assert " ".join(x if x != "T" else "✠" for x in bpulled) == "s ✠ b d ✠ c a g ✠ f e ✠ h"
assert bdist == dict(s=0, b=1, d=1, a=2, c=2, g=2, e=3, f=3, h=4)
assert [" ".join(q) for q in bqueues] == ["b d", "c a g", "f e", "h"]
X = {0: 50, 1: 170, 2: 290, 3: 410, 4: 530}
P = {"s": 170, "b": 110, "d": 230, "a": 55, "c": 170, "g": 285, "e": 110, "f": 230, "h": 170}
A = Graph(590, 395, r=16)
A.lab = []
LAB = SVG(590, 395)
for v in BV:
    A.state(v, X[bdist[v]], P[v])
BEND = {("a", "s"): -24, ("f", "b"): 20, ("h", "g"): 16}
for u, v in BE:
    if bpred[v] == u:
        A.edge(u, v, color=TREE["color"], width=TREE["width"])
    else:
        A.edge(u, v, color="var(--muted)", width=1.3, bend=BEND.get((u, v), 0))
for d in range(5):
    A.text(X[d], 14, f"dist {d}", size=13, color="currentColor", weight="600")
    A.line(X[d] - 50, 25, X[d] + 50, 25, color="var(--muted)", width=0.8)
for i, q in enumerate(bqueues, start=1):
    A.text(X[i], 338, f"end of phase {i}:", size=12)
    A.text(X[i], 355, " ".join(q), size=14, font=SERIF_IT, italic=True)
A.text(X[0], 338, "start:", size=12)
A.text(X[0], 355, "s", size=14, font=SERIF_IT, italic=True)
A.text(295, 384, "pulled from the queue:  s ✠ b d ✠ c a g ✠ f e ✠ h", size=12.5)
html = overlay_figure(A, LAB,
    "<strong>Breadth-first search on the book’s graph (its Figure 8.6), drawn by layers.</strong> Each vertex sits in "
    "the column of its distance from <i>s</i>; thick edges are the final predecessor pointers, a breadth-first "
    "shortest-path tree, and gray edges the rest. No edge skips a column to the right — for every edge "
    "<i>u</i>→<i>v</i>, <i>dist</i>(<i>v</i>) ≤ <i>dist</i>(<i>u</i>) + 1 — while edges may go back any distance. "
    "With every adjacency list in the order used here (<i>b</i> lists <i>c</i> before <i>a</i>), the vertices leave "
    "the queue in the order <i>s</i> ✠ <i>b d</i> ✠ <i>c a g</i> ✠ <i>f e</i> ✠ <i>h</i>, where ✠ is the end-of-phase "
    "token, and at the end of phase <i>i</i> the queue holds exactly the vertices at distance <i>i</i> (Lemma 8.1).",
    alt="the book's nine-vertex directed graph with its vertices arranged in five columns by breadth-first distance")
save("a08-bfs", html)

# =========================================================================== 5. the book's dag (Figures 8.9 and 8.10)
DN = list("sabcdef")
DE = [("s", "a", 3), ("s", "b", 8), ("s", "c", 7), ("a", "b", 6), ("a", "d", 12), ("b", "c", -2), ("b", "d", 5),
      ("b", "e", 0), ("c", "e", 10), ("d", "e", 1), ("d", "f", -3), ("e", "f", 1)]
ddist = {v: INF for v in DN}
dpred = {v: None for v in DN}
ddist["s"] = 0
for u in DN:                          # PushDagSSSP in the topological order s a b c d e f
    for (x, v, w) in DE:
        if x == u and ddist[u] + w < ddist[v]:
            ddist[v] = ddist[u] + w
            dpred[v] = u
assert [ddist[v] for v in DN] == [0, 3, 8, 6, 13, 8, 9]
A = Graph(630, 250, r=16)
A.lab = []
LAB = SVG(630, 250)
DX = {v: 72 + 85 * i for i, v in enumerate(DN)}
Y0 = 112
for v in DN:
    A.state(v, DX[v], Y0)
ARC = {("s", "b"): -36, ("b", "d"): -36, ("d", "f"): -36, ("c", "e"): -36,
       ("s", "c"): 52, ("a", "d"): 52, ("b", "e"): 52}
for u, v, w in DE:
    st = TREE if dpred[v] == u else PLAIN
    b = ARC.get((u, v), 0)
    A.edge(u, v, label=fmt_d(w), bend=b, color=st["color"], width=st["width"], mono=False,
           label_side=-1 if (u, v) == ("b", "c") else 1, label_dist=10 if b else 11)
LAB.text(6, 226, "dist", size=12, color="var(--muted)", anchor="start")
for v in DN:
    A.rect(DX[v] - 19, 214, 38, 22, rx=4, stroke="currentColor", fill="var(--accent)", fill_opacity=0.1, width=1.1)
    A.text(DX[v], 225.5, fmt_d(ddist[v]), size=13)
html = overlay_figure(A, LAB,
    "<strong>Shortest paths in the book’s dag (its Figures 8.9 and 8.10).</strong> The vertices are drawn in "
    "topological order, so every edge points right, and some weights are negative. Relaxing the edges in "
    "topological order — incoming edges of each vertex (DagSSSP) or outgoing edges (PushDagSSSP) — gives the "
    "distances in the boxes; thick edges are the predecessor pointers. On the way, PushDagSSSP sets "
    "<i>dist</i>(<i>d</i>) to 15 before lowering it to 13, and <i>dist</i>(<i>f</i>) to 10 before lowering it to 9.",
    alt="seven-vertex weighted dag drawn on a line with shortest-path distances from s")
save("a08-dag", html)

# =========================================================================== 6. Dijkstra example
JV = list("sabcdt")
JE = [("s", "a", 2), ("s", "b", 5), ("s", "c", 9), ("a", "c", 6), ("a", "d", 9), ("b", "c", 1), ("b", "d", 3),
      ("c", "t", 9), ("d", "c", 3), ("d", "t", 1)]
jdist, jpred = dijkstra(JV, JE, "s")
assert jdist == dict(s=0, a=2, b=5, c=6, d=8, t=9)
A = Graph(520, 270, r=17)
A.lab = []
LAB = SVG(520, 270)
JP = {"s": (45, 150), "a": (180, 85), "b": (180, 235), "c": (340, 85), "d": (340, 235), "t": (475, 160)}
for v, (x, y) in JP.items():
    A.state(v, x, y)
JB = {("s", "c"): 62}
JS = {("a", "d"): (0.3, -1), ("b", "c"): (0.3, 1), ("d", "c"): (0.5, 1), ("s", "b"): (0.5, -1),
      ("b", "d"): (0.5, -1), ("d", "t"): (0.5, -1)}
for u, v, w in JE:
    st = TREE if jpred[v] == u else PLAIN
    pos, side = JS.get((u, v), (0.5, 1))
    A.edge(u, v, label=str(w), bend=JB.get((u, v), 0), color=st["color"], width=st["width"], mono=False,
           label_pos=pos, label_side=side)
JT = {"s": (45, 120), "a": (174, 117), "b": (180, 263), "c": (370, 85), "d": (340, 263), "t": (475, 130)}
for v in JV:
    tag(LAB, *JT[v], fmt_d(jdist[v]))
html = overlay_figure(A, LAB,
    "<strong>A run of Dijkstra’s algorithm.</strong> All weights are non-negative. The colored numbers are the final "
    "distances from <i>s</i>, and the thick edges the shortest-path tree. The vertices leave the priority queue in "
    "the order <i>s a b c d t</i>, in increasing order of distance; the table below the figure shows the queue after "
    "every step.",
    alt="six-vertex weighted directed graph with the shortest-path tree found by Dijkstra's algorithm")
save("a08-dijkstra", html)

# =========================================================================== 7. NonnegativeDijkstra fails with a negative edge
A = Graph(620, 235, r=16)
A.lab = []
LAB = SVG(620, 235)
CP = {"s": (40, 95), "a": (150, 40), "b": (150, 150), "t": (260, 40)}
CW = {("s", "a"): 2, ("s", "b"): 3, ("b", "a"): -2, ("a", "t"): 2}
for k, x0 in enumerate((0, 320)):
    for v, (x, y) in CP.items():
        A.state(f"{v}{k}", x0 + x, y, label=v)
    tree = {("s", "b"), ("b", "a"), ("a", "t")}
    bad = {("a", "t")} if k == 0 else set()
    for (u, v), w in CW.items():
        side = {("s", "a"): 1, ("s", "b"): -1, ("b", "a"): 1, ("a", "t"): 1}[(u, v)]
        if (u, v) in bad:
            st = dict(color="var(--hi)", width=2.2, dash="7 4")
        elif (u, v) in tree:
            st = dict(color=TREE["color"], width=TREE["width"], dash=None)
        else:
            st = dict(color="currentColor", width=1.4, dash=None)
        A.edge(f"{u}{k}", f"{v}{k}", label=fmt_d(w), color=st["color"], width=st["width"], dash=st["dash"],
               mono=False, label_side=side)
    tag(LAB, x0 + 14, 95, "0", anchor="end")
    tag(LAB, x0 + 176, 150, "3", anchor="start")
    tag(LAB, x0 + 124, 40, "1", anchor="end")
    tag(LAB, x0 + 286, 40, "4" if k == 0 else "3", color="var(--hi)" if k == 0 else "var(--accent)", anchor="start")
lines0 = ["extract s 0, a 2 (t ← 4), b 3:", "a ← 1, but a has left the queue;", "t is extracted with 4 — wrong"]
lines1 = ["extract s 0, a 2 (t ← 4), b 3:", "a ← 1 and a is re-inserted;", "a is scanned again: t ← 3"]
for k, (x0, L) in enumerate(((0, lines0), (320, lines1))):
    for j, s_ in enumerate(L):
        A.text(x0 + 150, 186 + 16 * j, s_, size=12.5)
A.text(150, 14, "NonnegativeDijkstra", size=13, weight="600")
A.text(470, 14, "Dijkstra", size=13, weight="600")
A.line(305, 10, 305, 225, color="var(--muted)", width=1, dash="3 4")
html = overlay_figure(A, LAB,
    "<strong>One negative edge breaks NonnegativeDijkstra.</strong> Both versions extract <i>s</i> (0), then <i>a</i> "
    "(2), which sets <i>dist</i>(<i>t</i>) = 4, then <i>b</i> (3), which finds the tense edge <i>b</i>→<i>a</i> and "
    "lowers <i>dist</i>(<i>a</i>) to 1. Left: <i>a</i> has already left the queue, so it is never scanned again; "
    "<i>t</i> is extracted with 4, and the edge <i>a</i>→<i>t</i> (dashed) is still tense at the end. Right: the "
    "book’s Dijkstra re-inserts <i>a</i>, scans it again and lowers <i>dist</i>(<i>t</i>) to the correct 3.",
    alt="the same four-vertex graph with a negative edge, as left by NonnegativeDijkstra and by Dijkstra")
save("a08-dijkstra-negative", html)

# =========================================================================== 8. Bellman-Ford on the book's graph (Figures 8.15, 8.17)
NV = list("sabcdef")
NE = [("s", "a", 3), ("s", "b", 10), ("s", "c", 4), ("a", "b", 6), ("a", "d", 2), ("b", "d", -7), ("b", "f", -5),
      ("c", "b", 8), ("c", "f", 3), ("f", "d", -3), ("f", "e", 1), ("e", "d", -5)]
ndist, npred = bellman_ford(NV, NE, "s")
assert ndist == dict(s=0, a=3, b=9, c=4, d=0, e=5, f=4)
NP = {"s": (210, 300), "a": (90, 240), "c": (330, 240), "b": (210, 175), "d": (90, 110), "f": (330, 110),
      "e": (210, 45)}
A = Graph(420, 345, r=17)
A.lab = []
LAB = SVG(420, 345)
for v, (x, y) in NP.items():
    A.state(v, x, y)
for u, v, w in NE:
    st = TREE if npred[v] == u else PLAIN
    A.edge(u, v, color=st["color"], width=st["width"])
NL = {("s", "a"): (140, 285), ("s", "b"): (222, 245), ("s", "c"): (280, 285), ("a", "b"): (140, 196),
      ("a", "d"): (76, 175), ("b", "d"): (146, 128), ("b", "f"): (276, 128), ("c", "b"): (280, 196),
      ("c", "f"): (344, 175), ("f", "d"): (210, 98), ("f", "e"): (278, 66), ("e", "d"): (142, 66)}
for u, v, w in NE:
    LAB.text(*NL[(u, v)], fmt_d(w), size=13, halo=True)
NT = {"s": (240, 312), "a": (60, 252), "c": (360, 252), "b": (210, 147), "d": (60, 98), "f": (360, 98),
      "e": (240, 30)}
for v in NV:
    tag(LAB, *NT[v], fmt_d(ndist[v]))
html = overlay_figure(A, LAB,
    "<strong>The book’s graph with negative edges (its Figures 8.15 and 8.17).</strong> There are no negative "
    "cycles. The colored numbers are the distances from <i>s</i> and the thick edges the shortest-path tree. The "
    "shortest path to <i>d</i>, <i>s a b f e d</i> of length 3 + 6 − 5 + 1 − 5 = 0, has five edges, so "
    "<i>dist</i><sub>≤<i>i</i></sub>(<i>d</i>) settles only at <i>i</i> = 5 (table below).",
    alt="seven-vertex directed graph with negative edges and its shortest-path tree from s")
save("a08-bellman-ford", html)

# =========================================================================== 9. layered dag for "at most k edges"
LV = list("sabt")
LE = [("s", "a", 1), ("s", "b", 4), ("a", "b", 2), ("b", "a", -3), ("a", "t", 5), ("b", "t", 1)]
K = 3
hd = {(v, i): INF for v in LV for i in range(K + 1)}
hp = {}
hd[("s", 0)] = 0
for i in range(1, K + 1):           # the layered graph is a dag; relax layer by layer (topological order)
    for u, v, w in LE:
        if hd[(u, i - 1)] + w < hd[(v, i)]:
            hd[(v, i)] = hd[(u, i - 1)] + w
            hp[(v, i)] = (u, i - 1)
best_i = min(range(K + 1), key=lambda i: hd[("t", i)])
assert hd[("t", best_i)] == 4 and best_i == 3
path = [("t", 3)]
while path[-1] != ("s", 0):
    path.append(hp[path[-1]])
path = path[::-1]
assert [v for v, i in path] == ["s", "a", "b", "t"]
A = Graph(640, 300, r=15)
A.lab = []
LAB = SVG(640, 300)
GP = {"s": (30, 150), "a": (100, 80), "b": (100, 220), "t": (170, 150)}
for v, (x, y) in GP.items():
    A.state(f"g{v}", x, y, label=v)
GS = {("s", "a"): 1, ("s", "b"): -1, ("a", "b"): 1, ("b", "a"): 1, ("a", "t"): 1, ("b", "t"): -1}
for u, v, w in LE:
    bend = {("a", "b"): 9, ("b", "a"): 9}.get((u, v), 0)
    A.edge(f"g{u}", f"g{v}", label=fmt_d(w), bend=bend, color="currentColor", width=1.4, mono=False,
           label_side=GS[(u, v)])
A.text(100, 268, "G: the cycle a b a", size=12.5)
A.text(100, 285, "has weight −1", size=12.5)
A.line(212, 20, 212, 285, color="var(--muted)", width=1, dash="3 4")
ROW = {"s": 50, "a": 120, "b": 190, "t": 260}
COL = {i: 255 + 112 * i for i in range(K + 1)}
onpath = set(zip(path, path[1:]))
for i in range(K + 1):
    A.text(COL[i], 14, f"layer {i}", size=12.5, weight="600")
    for v in LV:
        reach = hd[(v, i)] < INF
        A.state(f"{v}{i}", COL[i], ROW[v], label=v, color="currentColor" if reach else "var(--muted)")
for i in range(1, K + 1):
    for u, v, w in LE:
        a, b = (u, i - 1), (v, i)
        if hd[a] == INF:
            continue                         # edges out of unreachable vertices are not drawn
        if (a, b) in onpath:
            st = dict(color="var(--accent)", width=2.6)
        else:
            st = dict(color="currentColor", width=1.2)
        A.edge(f"{u}{i - 1}", f"{v}{i}", color=st["color"], width=st["width"])
for i in range(K + 1):
    for v in LV:
        d = hd[(v, i)]
        tag(LAB, COL[i] + 19, ROW[v] - 17, fmt_d(d), size=12, anchor="start",
            color="var(--accent)" if d < INF else "var(--muted)")
html = overlay_figure(A, LAB,
    "<strong>A layered dag.</strong> Left: a graph <i>G</i> with a negative cycle, so shortest walks from <i>s</i> to "
    "<i>t</i> do not exist. Right: the graph <i>H</i> with a copy (<i>v</i>, <i>i</i>) of every vertex for each layer "
    "<i>i</i> = 0, …, 3, and an edge (<i>u</i>, <i>i</i> − 1)→(<i>v</i>, <i>i</i>) of weight "
    "<i>w</i>(<i>u</i>→<i>v</i>) for every edge of <i>G</i> (drawn only out of the vertices that (<i>s</i>, 0) can "
    "reach; the others are gray). Paths from (<i>s</i>, 0) to (<i>v</i>, <i>i</i>) are walks from <i>s</i> to "
    "<i>v</i> with exactly <i>i</i> edges, and <i>H</i> is a dag, so its distances (colored) take one pass. The "
    "shortest walk to <i>t</i> with at most 3 edges is <i>s a b t</i>, of length 4.",
    alt="a four-vertex graph with a negative cycle and the four-layer dag built from it")
save("a08-layered", html)
