#!/usr/bin/env python3
"""Figures for the Chapter 8 exercises page (content/2-algorithms/08-shortest-paths-exercises.md). Writes
tools/figs/a08x-<name>.html; then run tools/assemble.py on the page. Every number drawn here is computed below by
running the page's algorithm (Dijkstra, the layered Dijkstra of 8.2(b), the bypass sweep of 8.4(a), the looped-tree
formula of 8.1, Ford's relaxations for the counterexamples of 8.8); tools/checks/a08x.py re-derives the same facts
independently by brute force."""
import heapq
import math
import os
from figlib import SVG, Automaton, SERIF_IT, SANS, MONO

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")
os.makedirs(OUT, exist_ok=True)
INF = math.inf


def save(name, html):
    with open(os.path.join(OUT, name + ".html"), "w", encoding="utf-8") as f:
        f.write(html + "\n")
    print("wrote", name)


def neg(x):
    return "∞" if x == INF else str(x).replace("-", "−")


def dijkstra(V, E, s, init=None):
    """E: dict (u, v) -> w >= 0. init: optional dict of starting labels (multi-source)."""
    dist = {v: INF for v in V}
    pq = []
    for v, d in (init or {s: 0}).items():
        dist[v] = d
        pq.append((d, v))
    heapq.heapify(pq)
    done = set()
    while pq:
        d, u = heapq.heappop(pq)
        if u in done:
            continue
        done.add(u)
        for (a, b), w in E.items():
            if a == u and d + w < dist[b]:
                dist[b] = d + w
                heapq.heappush(pq, (dist[b], b))
    return dist


def it(s):
    return f"<i>{s}</i>"


# =========================================================================== 1. Exercise 8.0(a): tight cycle
A = Automaton(560, 168, r=17)
P1 = {"s": (70, 70), "a": (250, 70), "b": (430, 70)}
for v, (x, y) in P1.items():
    A.state(v, x, y)
E1 = {("s", "a"): 1, ("a", "b"): 1, ("b", "a"): -1}
lab = {"s": 0, "a": 0, "b": 1}
true = {"s": 0, "a": 1, "b": 2}
for (u, v), w in E1.items():
    tight = lab[u] + w == lab[v]
    assert not lab[u] + w < lab[v]                 # nothing is tense
    bend = 0 if (u, v) == ("s", "a") else 16
    A.edge(u, v, neg(w), bend=bend, color="var(--hi)" if tight else "var(--muted)", width=2.4 if tight else 1.5,
           dash=None if tight else "5 4", label_dist=12)
assert [(u, v) for (u, v), w in E1.items() if lab[u] + w == lab[v]] == [("a", "b"), ("b", "a")]
for v, (x, y) in P1.items():
    A.text(x, y + 44, f"stored {lab[v]}", size=13, color="var(--hi)" if lab[v] != true[v] else "currentColor",
           weight=600)
    A.text(x, y + 62, f"true {true[v]}", size=13, color="var(--muted)")
A.text(160, 88, "slack 1", size=12, color="var(--muted)")
save("a08x-tight-cycle", A.figure(
    "<strong>Tight incoming edges are not enough.</strong> With the stored labels 0, 0, 1 no edge is tense, and "
    "both <i>a</i> and <i>b</i> have a tight incoming edge (red: <i>dist</i>(<i>u</i>) + <i>w</i> = "
    "<i>dist</i>(<i>v</i>)). But the two tight edges only form a cycle among themselves; <i>s</i>→<i>a</i> has "
    "slack 1, so no tight path leads from <i>s</i> to <i>a</i> or <i>b</i>. The true distances are 0, 1, 2, and "
    "the test of Exercise 8.0(a) — every finite label reachable from <i>s</i> along tight edges — rejects the labels.",
    alt="three vertices s, a, b; a and b joined by a red two-cycle of tight edges; s to a dashed"))

# =========================================================================== 2. Exercise 8.1: the looped tree
TREE = [("r", "a", 5), ("r", "b", 8), ("a", "c", 17), ("a", "d", 0), ("c", "e", 23), ("b", "f", 1), ("f", "g", 9),
        ("f", "h", 14)]
LOOP = {"e": 4, "d": 16, "g": 7, "h": 42}
kids = {}
par = {}
W = {}
for u, v, w in TREE:
    kids.setdefault(u, []).append(v)
    par[v] = u
    W[(u, v)] = w
D = {"r": 0}
for u, v, w in TREE:                 # parents are listed before children
    D[v] = D[u] + w
L = {}
for v in ["e", "d", "g", "h", "c", "f", "a", "b", "r"]:
    L[v] = LOOP[v] if v in LOOP else min(W[(v, c)] + L[c] for c in kids[v])
assert (L["a"], D["h"], L["a"] + D["h"]) == (16, 23, 39)
# Dijkstra cross-check of the highlighted query
ALL = {(u, v): w for u, v, w in TREE} | {(l, "r"): w for l, w in LOOP.items()}
assert dijkstra(list(D), ALL, "a")["h"] == 39
POS = {"r": (310, 62), "a": (230, 128), "b": (390, 128), "c": (175, 194), "d": (285, 194), "f": (440, 194),
       "e": (145, 260), "g": (395, 260), "h": (485, 260)}
QUERY_TREE = {("a", "d"), ("r", "b"), ("b", "f"), ("f", "h")}
A = Automaton(620, 330, r=14, font_size=14)
for v, (x, y) in POS.items():
    A.state(v, x, y, label=v)
for u, v, w in TREE:
    on = (u, v) in QUERY_TREE
    side = -1 if POS[v][0] < POS[u][0] else 1
    A.edge(u, v, str(w), color="var(--hi)" if on else "currentColor", width=2.4 if on else 1.5, label_side=side,
           label_dist=11)


def ortho(S, pts, color, width, label=None, lpos=None, r=10):
    """Polyline with rounded corners and an arrow at the end."""
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for i in range(1, len(pts) - 1):
        (x0, y0), (x1, y1), (x2, y2) = pts[i - 1], pts[i], pts[i + 1]
        l1, l2 = math.hypot(x1 - x0, y1 - y0), math.hypot(x2 - x1, y2 - y1)
        rr = min(r, l1 / 2, l2 / 2)
        ax, ay = x1 - (x1 - x0) / l1 * rr, y1 - (y1 - y0) / l1 * rr
        bx, by = x1 + (x2 - x1) / l2 * rr, y1 + (y2 - y1) / l2 * rr
        d += f" L{ax:.1f},{ay:.1f} Q{x1:.1f},{y1:.1f} {bx:.1f},{by:.1f}"
    d += f" L{pts[-1][0]:.1f},{pts[-1][1]:.1f}"
    S.path(d, color=color, width=width, arrow=True)


rx, ry, rr = POS["r"][0], POS["r"][1], 14


def hit(y, side):
    return rx + side * (math.sqrt(rr * rr - (y - ry) ** 2) + 2.5), y


LOOPS = {   # leaf: polyline points (last point on the root's outline)
    "e": [(POS["e"][0] - 14, POS["e"][1]), (78, POS["e"][1]), (78, ry + 4), hit(ry + 4, -1)],
    "d": [(POS["d"][0], POS["d"][1] + 14), (POS["d"][0], 306), (44, 306), (44, ry - 7), hit(ry - 7, -1)],
    "g": [(POS["g"][0], POS["g"][1] + 14), (POS["g"][0], 306), (580, 306), (580, ry - 7), hit(ry - 7, 1)],
    "h": [(POS["h"][0] + 14, POS["h"][1]), (548, POS["h"][1]), (548, ry + 4), hit(ry + 4, 1)],
}
LOOP_LABEL = {"e": (66, 170), "d": (32, 190), "g": (592, 190), "h": (560, 170)}
for leaf, pts in LOOPS.items():
    on = leaf == "d"
    ortho(A, pts, "var(--hi)" if on else "var(--accent)", 2.4 if on else 1.5)
    x, y = LOOP_LABEL[leaf]
    A.text(x, y, str(LOOP[leaf]), size=13, font=MONO, color="var(--hi)" if on else "var(--accent)", halo=True)
OFF = {"r": (0, -24), "a": (-40, -6), "b": (40, -6), "c": (-40, -4), "d": (36, -10), "f": (40, -8),
       "e": (0, 26), "g": (-38, 6), "h": (0, 26)}
for v, (x, y) in POS.items():
    dx, dy = OFF[v]
    A.text(x + dx, y + dy, f"{D[v]}/{L[v]}", size=12, font=MONO, color="var(--muted)", halo=True)
save("a08x-looped-tree", A.figure(
    "<strong>The book's looped tree, labeled <i>D</i>/<i>L</i>.</strong> <i>D</i>(<i>x</i>) is the length of the "
    "tree path from the root <i>r</i> to <i>x</i>; <i>L</i>(<i>x</i>) is the cheapest way from <i>x</i> back to "
    "<i>r</i> — down to a leaf of <i>x</i>'s subtree, then that leaf's loop edge (blue). A walk can leave the "
    "subtree of <i>u</i> only through a loop edge, so δ(<i>u</i>, <i>v</i>) = <i>D</i>(<i>v</i>) − <i>D</i>(<i>u</i>) "
    "if <i>u</i> is an ancestor of <i>v</i>, and <i>L</i>(<i>u</i>) + <i>D</i>(<i>v</i>) otherwise. Red: "
    "δ(<i>a</i>, <i>h</i>) = 16 + 23 = 39, along <i>a</i>→<i>d</i>→<i>r</i>→<i>b</i>→<i>f</i>→<i>h</i>.",
    alt="binary tree with nine nodes, four loop edges from the leaves back to the root, and D/L labels"))

# =========================================================================== 3. Exercise 8.2(b): layered graph
VL = ["s", "a", "b", "c", "t"]
PLUS = {("s", "a"): 1, ("a", "c"): 2, ("b", "c"): 2, ("s", "t"): 2}
NEG = {("a", "b"): -3, ("c", "t"): -2}
k = len(NEG)
delta = [dijkstra(VL, PLUS, "s")]
for i in range(1, k + 2):
    c = {}
    for (x, y), w in NEG.items():
        if delta[i - 1][x] < INF:
            c[y] = min(c.get(y, INF), delta[i - 1][x] + w)
    if not c:
        delta.append({v: INF for v in VL})
        continue
    m = min(c.values())
    dd = dijkstra(VL, PLUS, None, init={y: cy - m for y, cy in c.items()})
    delta.append({v: dd[v] + m for v in VL})
assert [delta[i]["t"] for i in range(3)] == [2, 1, -2] and all(x == INF for x in delta[3].values())
assert [delta[0][v] for v in VL] == [0, 1, INF, 3, 2]
assert [delta[1][v] for v in VL] == [INF, INF, -2, 0, 1]
assert [delta[2][v] for v in VL] == [INF, INF, INF, INF, -2]
XS = {"s": 120, "a": 230, "c": 340, "b": 450, "t": 560}
YS = [86, 210, 334]
PATH = {(("s", 0), ("a", 0)), (("a", 0), ("b", 1)), (("b", 1), ("c", 1)), (("c", 1), ("t", 2))}
A = Automaton(640, 396, r=15)
for i, y in enumerate(YS):
    for v in VL:
        A.state(f"{v}{i}", XS[v], y, label=v, color="currentColor" if delta[i][v] < INF else "var(--muted)")
    A.text(14, y, f"layer {i}", size=13, anchor="start", color="var(--muted)")
    for (u, v), w in PLUS.items():
        on = ((u, i), (v, i)) in PATH
        live = delta[i][u] < INF
        bend = {("s", "t"): 38}.get((u, v), 0)
        A.edge(f"{u}{i}", f"{v}{i}", str(w), bend=bend, label_dist=10,
               color="var(--hi)" if on else ("currentColor" if live else "var(--muted)"),
               width=2.5 if on else (1.5 if live else 1.1), dash=None if live else "3 3")
    if i + 1 < len(YS):
        for (u, v), w in NEG.items():
            on = ((u, i), (v, i + 1)) in PATH
            live = delta[i][u] < INF
            A.edge(f"{u}{i}", f"{v}{i + 1}", neg(w), label_dist=12, label_side=-1, label_pos=0.3,
                   color="var(--hi)" if on else ("var(--accent)" if live else "var(--muted)"),
                   width=2.5 if on else (1.6 if live else 1.1), dash=None if live else "3 3")
    for v in VL:
        A.text(XS[v] + 2, y + 27, neg(delta[i][v]), size=13, font=MONO, halo=True,
               color="var(--hi)" if (v == "t" and i == 2) else ("currentColor" if delta[i][v] < INF else "var(--muted)"),
               weight=600 if delta[i][v] < INF else None)
A.text(340, 384, "layer 3 (the check layer): every label ∞, so no negative cycle is reachable", size=12.5,
       color="var(--muted)")
save("a08x-layers", A.figure(
    "<strong>Layers count the negative edges used.</strong> <i>G</i> has the nonnegative edges <i>s</i>→<i>a</i>, "
    "<i>a</i>→<i>c</i>, <i>b</i>→<i>c</i>, <i>s</i>→<i>t</i> (copied into every layer) and <i>k</i> = 2 negative "
    "edges, <i>a</i>→<i>b</i> (−3) and <i>c</i>→<i>t</i> (−2), which lead from each layer to the next (blue). "
    "Under each vertex: <i>D<sub>i</sub></i>(<i>v</i>), the length of a shortest walk from <i>s</i> to <i>v</i> that "
    "uses exactly <i>i</i> negative edges — one Dijkstra per layer. δ(<i>s</i>, <i>t</i>) = min(2, 1, −2) = −2, "
    "along the red path (<i>s</i>,0)→(<i>a</i>,0)→(<i>b</i>,1)→(<i>c</i>,1)→(<i>t</i>,2). Grey: unreachable.",
    alt="three rows of five vertices s a b c t; negative edges lead diagonally from one row to the next"))

# =========================================================================== 4. Exercise 8.4(a): bypasses
PV = ["s", "a", "b", "c", "d", "t"]
PW = [2, 1, 3, 1, 2]
EXTRA = {("s", "b"): 6, ("a", "d"): 6, ("b", "t"): 8, ("c", "t"): 5}
pos = {v: i for i, v in enumerate(PV)}
Dp = [0]
for w in PW:
    Dp.append(Dp[-1] + w)
total = Dp[-1]
keys = {}
for (u, v), w in EXTRA.items():
    if pos[u] < pos[v]:
        keys[(u, v)] = Dp[pos[u]] + w + total - Dp[pos[v]]
answers = []
for i in range(len(PW)):
    cover = [kk for (u, v), kk in keys.items() if pos[u] <= i < pos[v]]
    answers.append(min(cover) if cover else INF)
assert keys == {("s", "b"): 12, ("a", "d"): 10, ("b", "t"): 11, ("c", "t"): 11}, keys
assert answers == [12, 10, 10, 10, 11], answers
# Dijkstra cross-check: P is a shortest path and every answer is right
EP = {(PV[i], PV[i + 1]): PW[i] for i in range(5)} | EXTRA
assert dijkstra(PV, EP, "s")["t"] == total == 9
for i in range(5):
    E2 = dict(EP)
    del E2[(PV[i], PV[i + 1])]
    assert dijkstra(PV, E2, "s")["t"] == answers[i]
X0, DX, Y = 52, 106, 150
A = Automaton(640, 300, r=15)
for v in PV:
    A.state(v, X0 + pos[v] * DX, Y, label=v)
for i in range(5):
    A.edge(PV[i], PV[i + 1], str(PW[i]), label_dist=10, width=2.2)
    A.text(X0 + (i + 0.5) * DX, Y + 104, str(answers[i]), size=15, font=MONO, color="var(--hi)", weight=700)
HEIGHT = {("s", "b"): -46, ("c", "t"): -46, ("a", "d"): 74, ("b", "t"): 124}
for (u, v), w in EXTRA.items():
    x1, x2 = X0 + pos[u] * DX, X0 + pos[v] * DX
    h = HEIGHT[(u, v)]
    sg = 1 if h > 0 else -1
    a = math.radians(72)
    sx, sy = x1 + 15 * math.cos(a), Y - sg * 15 * math.sin(a)
    ex, ey = x2 - 17.5 * math.cos(a), Y - sg * 17.5 * math.sin(a)
    A.path(f"M{sx:.1f},{sy:.1f} C{x1 + 0.12 * (x2 - x1):.1f},{Y - h * 1.33:.1f} "
           f"{x2 - 0.12 * (x2 - x1):.1f},{Y - h * 1.33:.1f} {ex:.1f},{ey:.1f}",
           arrow=True, width=1.6, color="var(--accent)")
    mx, my = (x1 + x2) / 2 + (52 if (u, v) == ("a", "d") else 0), Y - h - sg * 12
    A.text(mx, my, f"{w}  (key {keys[(u, v)]})", size=12.5, color="var(--accent)", halo=True)
A.text(X0 + 2.5 * DX, Y + 128, "δ(s, t) after deleting the path edge above it (any other edge: 9)", size=12.5,
       color="var(--hi)")
save("a08x-replacement", A.figure(
    "<strong>Replacement paths when the shortest path visits every vertex.</strong> The shortest path "
    "<i>s</i>→<i>a</i>→<i>b</i>→<i>c</i>→<i>d</i>→<i>t</i> has length 9. Each forward edge off the path (blue arc) "
    "is a <i>bypass</i> of the path edges it spans, with key = (prefix length to its tail) + (its weight) + "
    "(suffix length from its head). Deleting a path edge leaves exactly the bypasses spanning it, and the new distance "
    "(red) is the smallest key among them: 12, 10, 10, 10, 11. (A backward edge, from a later to an earlier path "
    "vertex, would bypass nothing.)",
    alt="a six-vertex path drawn left to right with two weighted arcs above it and two below"))

# =========================================================================== 5. Exercise 8.8: counterexamples
A = Automaton(640, 250, r=15)
TOP = 30
# panel (a)
A.text(105, TOP - 8, "(a) pred(s) changes", size=13, weight=600)
A.state("sa", 40, 120, label="s")
A.state("aa", 130, 120, label="a")
A.state("ba", 170, 200, label="b")
A.edge("sa", "aa", "0", bend=-16, label_dist=11)
A.edge("aa", "sa", "100", bend=-16, label_dist=12)
A.edge("aa", "ba", "−1", bend=12, label_dist=11, color="var(--hi)", width=2.2)
A.edge("ba", "aa", "−1", bend=12, label_dist=11, color="var(--hi)", width=2.2)
A.text(105, 236, "negative cycle a⇄b avoids s", size=12, color="var(--muted)")
# panel (b)
ox = 220
A.text(ox + 100, TOP - 8, "(b) pred(s) never changes", size=13, weight=600)
A.state("sb", ox + 40, 120, label="s")
A.state("ab", ox + 40, 200, label="a")
A.state("bb", ox + 130, 120, label="b")
A.state("cb", ox + 170, 200, label="c")
A.edge("sb", "ab", "1", bend=-14, label_dist=11, color="var(--hi)", width=2.2)
A.edge("ab", "sb", "−2", bend=-14, label_dist=12, color="var(--hi)", width=2.2)
A.edge("sb", "bb", "0", label_dist=11)
A.edge("bb", "cb", "−1", bend=12, label_dist=11, color="var(--accent)", width=2.0)
A.edge("cb", "bb", "0", bend=12, label_dist=11, color="var(--accent)", width=2.0)
A.text(ox + 100, 236, "relax b→c, c→b forever", size=12, color="var(--muted)")
# panel (d)
ox = 450
A.text(ox + 95, TOP - 8, "(d) R gets a cycle", size=13, weight=600)
A.state("sd", ox + 40, 125, label="s")
A.state("ud", ox + 150, 70, label="u")
A.state("vd", ox + 150, 180, label="v")
ORDER_D = [("sd", "ud", "10", 0), ("ud", "vd", "1", 14), ("sd", "vd", "0", 0), ("vd", "ud", "1", 14)]
for j, (u, v, w, b) in enumerate(ORDER_D, start=1):
    A.edge(u, v, "", bend=b, color="var(--hi)" if u != "sd" else "currentColor", width=2.2 if u != "sd" else 1.5)
WL = [(538, 86, "10"), (538, 165, "0"), (628, 125, "1"), (572, 125, "1")]
for x, y, w in WL:
    A.text(x, y, w, size=13, font=MONO, halo=True)
A.text(ox + 95, 236, "relax s→u, u→v, s→v, v→u", size=12, color="var(--muted)")
# Ford replays (assertions mirror the checks)


def ford_replay(E, s, seq):
    dist = {v: INF for e in E for v in e[:2]}
    pred = {v: None for v in dist}
    dist[s] = 0
    for (u, v) in seq:
        w = E[(u, v)]
        assert dist[u] + w < dist[v]
        dist[v], pred[v] = dist[u] + w, u
    return dist, pred


Ea = {("s", "a"): 0, ("a", "b"): -1, ("b", "a"): -1, ("a", "s"): 100}
seq = [("s", "a")] + [("a", "b"), ("b", "a")] * 51 + [("a", "s")]
da, pa = ford_replay({k2: v2 for k2, v2 in Ea.items()}, "s", seq)
assert pa["s"] == "a"
Ed = {("s", "u"): 10, ("u", "v"): 1, ("s", "v"): 0, ("v", "u"): 1}
dd, pd = ford_replay(Ed, "s", [("s", "u"), ("u", "v"), ("s", "v"), ("v", "u")])
assert dd == {"s": 0, "u": 1, "v": 0}
save("a08x-ford-counterexamples", A.figure(
    "<strong>Three small runs of Ford's algorithm.</strong> (a) Relax <i>s</i>→<i>a</i>, then <i>a</i>→<i>b</i> "
    "and <i>b</i>→<i>a</i> alternately until <i>dist</i>(<i>a</i>) &lt; −100 (51 rounds), then <i>a</i>→<i>s</i>: "
    "<i>pred</i>(<i>s</i>) changes, yet the only cycle through <i>s</i> weighs +100 — the negative cycle (red) "
    "merely lies on a closed walk through <i>s</i>. (b) <i>s</i>→<i>a</i>→<i>s</i> weighs −1, but after "
    "<i>s</i>→<i>a</i> and <i>s</i>→<i>b</i> the algorithm may relax <i>b</i>→<i>c</i>, <i>c</i>→<i>b</i> forever "
    "(always tense), so <i>a</i>→<i>s</i> is never chosen. (d) Relaxing <i>s</i>→<i>u</i>, <i>u</i>→<i>v</i>, <i>s</i>→<i>v</i>, <i>v</i>→<i>u</i> (each tense when relaxed) puts both <i>u</i>→<i>v</i> "
    "and <i>v</i>→<i>u</i> into <i>R</i>, although every cycle is positive.",
    alt="three small directed graphs illustrating Exercise 8.8 (a), (b) and (d)"))

# =========================================================================== 6. Exercises 8.12/8.13: Figure 8.18
GN = ["s", "a", "b", "c", "d", "e", "f", "g", "t"]
GRID = {"s": (0, 0), "a": (1, 0), "b": (2, 0), "c": (0, 1), "d": (1, 1), "e": (2, 1), "f": (0, 2), "g": (1, 2),
        "t": (2, 2)}
E818 = {("s", "a"): 2, ("a", "b"): 1, ("s", "t"): 14, ("c", "s"): 2, ("a", "c"): 4, ("a", "d"): 3, ("b", "d"): 2,
        ("b", "e"): 1, ("d", "c"): 1, ("e", "d"): 1, ("c", "f"): 2, ("f", "d"): 3, ("d", "g"): 5, ("t", "d"): 3,
        ("t", "e"): 5, ("f", "g"): 2, ("g", "t"): 4}
dist818 = dijkstra(GN, E818, "s")
tight = {e for e, w in E818.items() if dist818[e[0]] + w == dist818[e[1]]}
order = sorted(GN, key=lambda v: dist818[v])
N = {v: 0 for v in GN}
N["s"] = 1
for v in order[1:]:
    N[v] = sum(N[u] for (u, x) in tight if x == v)
assert [dist818[v] for v in GN] == [0, 2, 3, 6, 5, 4, 8, 10, 14]
assert [N[v] for v in GN] == [1, 1, 1, 4, 3, 1, 4, 7, 8]
assert set(E818) - tight == {("c", "s"), ("f", "d"), ("t", "d"), ("t", "e")}
X0, Y0, DXG = 90, 70, 150
A = Automaton(560, 432, r=16)
for v in GN:
    c, r = GRID[v]
    A.state(v, X0 + c * DXG, Y0 + r * DXG, label=v, color="var(--hi)" if v in ("s", "t") else "currentColor")
LS = {("a", "c"): -1, ("b", "d"): -1, ("f", "d"): -1, ("t", "d"): 1, ("a", "d"): 1, ("e", "d"): -1, ("d", "c"): -1,
      ("c", "s"): 1, ("c", "f"): -1, ("d", "g"): 1, ("t", "e"): -1, ("b", "e"): 1}
for (u, v), w in E818.items():
    if (u, v) == ("s", "t"):
        continue
    t_ = (u, v) in tight
    A.edge(u, v, str(w), label_dist=11, label_side=LS.get((u, v), 1),
           color="currentColor" if t_ else "var(--muted)", width=1.8 if t_ else 1.2, dash=None if t_ else "4 3")
# s -> t: big arc over the top and down the right side, as in the book
sx, sy = X0, Y0
tx, ty = X0 + 2 * DXG, Y0 + 2 * DXG
A.path(f"M{sx + 11:.1f},{sy - 12:.1f} C{sx + 60:.1f},{sy - 62:.1f} {tx + 70:.1f},{sy - 62:.1f} "
       f"{tx + 66:.1f},{sy + 60:.1f} S{tx + 50:.1f},{ty - 40:.1f} {tx + 15:.1f},{ty - 10:.1f}",
       color="var(--hi)", width=2.6, arrow=True)
A.text(tx + 82, Y0 + 40, "14", size=13, font=MONO, color="var(--hi)", halo=True)
LOFF = {"s": (-38, 0), "a": (0, -30), "b": (34, -26), "c": (-40, 0), "d": (-28, -24), "e": (40, 16),
        "f": (-40, 0), "g": (0, 30), "t": (-6, 34)}
for v in GN:
    c, r = GRID[v]
    dx, dy = LOFF[v]
    A.text(X0 + c * DXG + dx, Y0 + r * DXG + dy, f"{dist818[v]}/{N[v]}", size=12.5, font=MONO, halo=True,
           color="var(--accent)", weight=600)
save("a08x-best-paths", A.figure(
    "<strong>The graph of the book's Figure 8.18, with distances and path counts.</strong> Each vertex <i>v</i> is "
    "labeled δ(<i>v</i>)/NumPaths(<i>v</i>): its distance from <i>s</i> and its number of shortest paths. Solid edges "
    "are tight (δ(<i>u</i>) + <i>w</i> = δ(<i>v</i>)); the four dashed ones lie on no shortest path. The tight "
    "edges form a dag. Breadth-first search in it finds the best path to <i>t</i> — the single edge <i>s</i>→<i>t</i> "
    "(red) — and the counts add up along tight edges: NumPaths(<i>t</i>) = NumPaths(<i>s</i>) + NumPaths(<i>g</i>) "
    "= 1 + 7 = 8 shortest paths of length 14.",
    alt="three by three grid graph with weighted edges, a long arc from the top-left to the bottom-right vertex, "
        "and dist/count labels"))

# =========================================================================== 7. Exercise 8.16: mod-3 layers
E16 = [("s", "w"), ("w", "t"), ("w", "y"), ("y", "x"), ("x", "s"), ("y", "z"), ("z", "t")]
COLS = ["x", "s", "w", "y", "z", "t"]
LE = {((u, i), (v, (i + 1) % 3)): 1 for u, v in E16 for i in range(3)}
LV = [(v, i) for v in COLS for i in range(3)]
d16 = dijkstra(LV, LE, ("s", 0))
assert d16[("t", 0)] == 6
WALK = [("s", 0), ("w", 1), ("y", 2), ("x", 0), ("s", 1), ("w", 2), ("t", 0)]
assert all((WALK[j], WALK[j + 1]) in LE for j in range(6))
DXc, X0c, Yr = 92, 120, [44, 124, 204, 284]
A = Automaton(640, 346, r=14)
ROWNAME = ["layer 0", "layer 1", "layer 2", "layer 0 again"]
for row, y in enumerate(Yr):
    A.text(12, y, ROWNAME[row], size=12.5, anchor="start", color="var(--muted)")
    for j, v in enumerate(COLS):
        on = (v, row % 3) in WALK and not (row == 3 and v == "s")
        A.state(f"{v}{row}", X0c + j * DXc, y, label=v)
hl = set()
for j in range(6):
    (u, i), (v, i2) = WALK[j], WALK[j + 1]
    hl.add((u, i, v))
for u, v in E16:
    for i in range(3):
        on = (u, i, v) in hl
        A.edge(f"{u}{i}", f"{v}{i + 1}", "", color="var(--hi)" if on else "var(--muted)",
               width=2.6 if on else 1.1)
A.circle(X0c + COLS.index("s") * DXc, Yr[0], 19, stroke="var(--hi)", fill="none", width=1.4)
A.circle(X0c + COLS.index("t") * DXc, Yr[3], 19, stroke="var(--hi)", fill="none", width=1.4)
A.text(X0c + COLS.index("x") * DXc, Yr[3] + 28, "= (x, 0) above", size=11.5, color="var(--hi)")
A.text(X0c + 2.5 * DXc, 334, "every edge weighs 1 in the book's example; δ((s,0), (t,0)) = 6", size=12.5,
       color="var(--muted)")
save("a08x-mod3", A.figure(
    "<strong>The book's example for Exercise 8.16, unrolled.</strong> Vertex (<i>v</i>, <i>i</i>) means "
    "“at <i>v</i> after a number of edges ≡ <i>i</i> (mod 3)”; every edge <i>u</i>→<i>v</i> of <i>G</i> becomes three "
    "edges (<i>u</i>, <i>i</i>)→(<i>v</i>, <i>i</i>+1 mod 3), drawn from each row to the next (the bottom row is "
    "layer 0 again). A shortest path from (<i>s</i>, 0) to (<i>t</i>, 0) (circled) has length 6: (<i>s</i>,0)→"
    "(<i>w</i>,1)→(<i>y</i>,2)→(<i>x</i>,0), then from (<i>x</i>,0) at the top →(<i>s</i>,1)→(<i>w</i>,2)→(<i>t</i>,0) "
    "(red) — the walk <i>s</i>→<i>w</i>→<i>y</i>→<i>x</i>→<i>s</i>→<i>w</i>→<i>t</i>.",
    alt="four rows of six vertices; edges lead from each row to the next; a red walk crosses the rows twice"))
