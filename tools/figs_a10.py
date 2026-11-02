#!/usr/bin/env python3
"""Figures for Algorithms Chapter 10 (maximum flows and minimum cuts). Writes tools/figs/a10-<name>.html; then run
tools/assemble.py on the chapter page. Every flow value, residual capacity and cut capacity drawn here is computed
below from the networks (minimal re-implementations); tools/checks/a10.py re-checks the figure HTML independently."""
import math
import os
from itertools import combinations

from figlib import SVG, Automaton, SERIF_IT

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")
os.makedirs(OUT, exist_ok=True)


def save(name, html):
    with open(os.path.join(OUT, name + ".html"), "w", encoding="utf-8") as f:
        f.write(html + "\n")
    print("wrote", name)


def overlay_figure(A, overlay, caption, alt, under=None):
    """A.figure(), with `under` drawn below everything and `overlay` on top of the edges and states."""
    svg = A.svg(alt)
    if under is not None:
        head, rest = svg.split("</defs>", 1)
        svg = head + "</defs>" + "".join(under.items) + rest
    svg = svg.replace("</svg>", "".join(overlay.items) + "</svg>")
    out = f'<figure class="cs-fig">{svg}<figcaption>{caption}</figcaption></figure>'
    assert "\n\n" not in out
    return out.replace("\n", " ")


# ------------------------------------------------------------------ minimal flow helpers
def value(E, f, s):
    return sum(f[e] for e in E if e[0] == s) - sum(f[e] for e in E if e[1] == s)


def conserved(V, E, f, s, t):
    return all(sum(f[e] for e in E if e[1] == v) == sum(f[e] for e in E if e[0] == v) for v in V if v not in (s, t))


def residual(E, c, f):
    """Residual capacities of a reduced network: dict (u, v) -> positive residual capacity."""
    r = {}
    for (u, v) in E:
        if c[(u, v)] - f[(u, v)] > 0:
            r[(u, v)] = c[(u, v)] - f[(u, v)]
        if f[(u, v)] > 0:
            r[(v, u)] = f[(u, v)]
    return r


def reach(V, r, s):
    seen, stack = {s}, [s]
    while stack:
        u = stack.pop()
        for (a, b) in r:
            if a == u and b not in seen:
                seen.add(b)
                stack.append(b)
    return seen


def cut_cap(E, c, S):
    return sum(c[e] for e in E if e[0] in S and e[1] not in S)


def min_cut(V, E, c, s, t):
    others = [v for v in V if v not in (s, t)]
    best = None
    for k in range(len(others) + 1):
        for X in combinations(others, k):
            S = {s, *X}
            cap = cut_cap(E, c, S)
            if best is None or cap < best[0]:
                best = (cap, S)
    return best


class Net(Automaton):
    """Automaton plus labels placed beside straight or curved edges, collected in self.LAB (drawn on top)."""

    def __init__(self, w, h, r=16):
        super().__init__(w, h, r=r)
        self.LAB = SVG(w, h)

    def arc(self, u, v, label="", bend=0, off=11, side=1, t=0.5, color="currentColor", width=1.5, dash=None,
            lcolor="currentColor", ldx=0, ldy=0, weight=None, size=13):
        self.edge(u, v, bend=bend, color=color, width=width, dash=dash)
        if not label:
            return
        A, B = self.states[u], self.states[v]
        x1, y1, x2, y2 = A["x"], A["y"], B["x"], B["y"]
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy)
        nx, ny = dy / L, -dx / L  # figlib's bend direction
        px, py = x1 + dx * t, y1 + dy * t
        bulge = bend * 2 * 2 * t * (1 - t)  # quadratic Bezier offset at parameter t
        sgn = 1 if bend >= 0 else -1
        lx = px + nx * (bulge + sgn * off * side)
        ly = py + ny * (bulge + sgn * off * side)
        self.LAB.text(lx + ldx, ly + ldy, label, size=size, color=lcolor, halo=True, weight=weight)


# =========================================================================== the book's network (Figures 10.2–10.6)
V = ["s", "a", "b", "c", "d", "t"]
E = [("s", "a"), ("s", "c"), ("a", "b"), ("a", "c"), ("b", "c"), ("d", "b"), ("b", "t"), ("c", "d"), ("d", "t")]
cap = dict(zip(E, [20, 10, 5, 10, 15, 10, 15, 10, 20]))
flow = dict(zip(E, [10, 0, 0, 10, 0, 5, 5, 10, 5]))
assert conserved(V, E, flow, "s", "t") and value(E, flow, "s") == 10
assert all(0 <= flow[e] <= cap[e] for e in E)
R = residual(E, cap, flow)
assert R == {("s", "a"): 10, ("a", "s"): 10, ("s", "c"): 10, ("a", "b"): 5, ("c", "a"): 10, ("b", "c"): 15,
             ("d", "b"): 5, ("b", "d"): 5, ("b", "t"): 10, ("t", "b"): 5, ("d", "c"): 10, ("d", "t"): 15,
             ("t", "d"): 5}
PATH = ["s", "c", "a", "b", "d", "t"]
PE = list(zip(PATH, PATH[1:]))
F = min(R[e] for e in PE)
assert F == 5
flow2 = dict(flow)
for (u, v) in PE:
    if (u, v) in cap:
        flow2[(u, v)] += F
    else:
        flow2[(v, u)] -= F
assert conserved(V, E, flow2, "s", "t") and value(E, flow2, "s") == 15
assert all(0 <= flow2[e] <= cap[e] for e in E)
R2 = residual(E, cap, flow2)
S2 = reach(V, R2, "s")
assert S2 == {"s", "a", "c"} and cut_cap(E, cap, S2) == 15
assert min_cut(V, E, cap, "s", "t") == (15, {"s", "a", "c"})

POS = {"s": (40, 125), "a": (165, 45), "b": (315, 45), "c": (165, 205), "d": (315, 205), "t": (440, 125)}
# label offsets (dx, dy) from the edge midpoint, for the flow figures
FL = {("s", "a"): (-14, -10), ("s", "c"): (-14, 10), ("a", "b"): (0, -13), ("a", "c"): (-20, 0),
      ("b", "c"): (17, -14), ("d", "b"): (21, 0), ("b", "t"): (15, -10), ("c", "d"): (0, 13), ("d", "t"): (15, 10)}


def flow_net(fl, hi_edges=(), avoid=(), w=480, h=250, extra_h=0, override=None):
    A = Net(w, h + extra_h)
    off = {**FL, **(override or {})}
    for v, (x, y) in POS.items():
        A.state(v, x, y, start="left" if v == "s" else None)
    for e in E:
        if e in hi_edges:
            A.arc(*e, color="var(--hi)", width=2.6)
        elif e in avoid:
            A.arc(*e, color="var(--muted)", width=1.5, dash="5 4")
        else:
            A.arc(*e, color="currentColor", width=1.5)
        (x1, y1), (x2, y2) = POS[e[0]], POS[e[1]]
        dx, dy = off[e]
        col = "var(--hi)" if e in hi_edges else "currentColor"
        A.LAB.text((x1 + x2) / 2 + dx, (y1 + y2) / 2 + dy, f"{fl[e]}/{cap[e]}", size=13, halo=True, color=col,
                   weight="600" if e in hi_edges else None)
    # outgoing arrow at t
    tx, ty = POS["t"]
    A.line(tx + 16 + 2, ty, tx + 42, ty, arrow=True, width=1.6)
    return A


# --------------------------------------------------------------------------- 1. a flow of value 10 (Figure 10.2)
A = flow_net(flow, h=235)
html = overlay_figure(A, A.LAB,
    "<strong>A feasible flow of value 10 (the book’s Figure 10.2, vertex names added).</strong> Each edge is labeled "
    "<i>flow</i>/<i>capacity</i>. Flow is conserved at <i>a</i>, <i>b</i>, <i>c</i>, <i>d</i> (at <i>d</i>: 10 in, "
    "5 + 5 out); the value is the net flow out of <i>s</i>, 10 + 0 = 10, which is also the net flow into <i>t</i>, "
    "5 + 5. The flow saturates <i>a</i>→<i>c</i> and <i>c</i>→<i>d</i> and avoids <i>s</i>→<i>c</i>, "
    "<i>a</i>→<i>b</i> and <i>b</i>→<i>c</i>.",
    alt="a flow network with six vertices; each edge carries a flow/capacity label; the flow has value 10")
save("a10-flow", html)

# --------------------------------------------------------------------------- 2. residual graph + augmenting path
A = Net(480, 250)
for v, (x, y) in POS.items():
    A.state(v, x, y)
PAIR_BEND = 9
# (edge, label offset side) for drawing; pairs get opposite bends
for (u, v), rc in R.items():
    on = (u, v) in PE
    pair = (v, u) in R
    col = "var(--hi)" if on else "currentColor"
    wid = 2.6 if on else 1.4
    lab = str(rc)
    if pair:
        A.arc(u, v, lab, bend=PAIR_BEND, off=10, color=col, width=wid, lcolor=col, weight="600" if on else None)
    else:
        side = {("s", "c"): -1, ("a", "b"): 1, ("c", "a"): -1, ("b", "c"): -1, ("d", "c"): -1}[(u, v)]
        A.arc(u, v, lab, off=11, side=side, color=col, width=wid, lcolor=col, weight="600" if on else None,
              t=0.42 if (u, v) == ("b", "c") else 0.5)
html = overlay_figure(A, A.LAB,
    "<strong>The residual graph of that flow, and an augmenting path (the book’s Figures 10.5 and 10.6).</strong> "
    "An edge <i>u</i>→<i>v</i> with flow <i>f</i> and capacity <i>c</i> gives a forward residual edge of capacity "
    "<i>c</i> − <i>f</i> (if positive) and a backward one, <i>v</i>→<i>u</i>, of capacity <i>f</i> (if positive). "
    "The path <i>s</i>→<i>c</i>→<i>a</i>→<i>b</i>→<i>d</i>→<i>t</i> has residual capacities 10, 10, 5, 5, 15, so "
    "it can carry <i>F</i> = 5 more units; two of its edges, <i>c</i>→<i>a</i> and <i>b</i>→<i>d</i>, are "
    "backward edges, so augmenting along it <em>removes</em> 5 units from <i>a</i>→<i>c</i> and from "
    "<i>d</i>→<i>b</i>.",
    alt="the residual graph of the flow of value 10, with the augmenting path s c a b d t highlighted")
save("a10-residual", html)

# --------------------------------------------------------------------------- 3. maximum flow and minimum cut
cut_edges = [e for e in E if e[0] in S2 and e[1] not in S2]
back_edges = [e for e in E if e[1] in S2 and e[0] not in S2]
assert cut_edges == [("a", "b"), ("c", "d")] and back_edges == [("b", "c")]
assert all(flow2[e] == cap[e] for e in cut_edges) and all(flow2[e] == 0 for e in back_edges)
under = SVG(480, 265)
under.rect(8, 8, 222, 232, rx=14, stroke="var(--accent)", fill="var(--accent)", fill_opacity=0.08, width=1.2, dash="5 4")
under.rect(250, 8, 222, 232, rx=14, stroke="var(--accent2)", fill="var(--accent2)", fill_opacity=0.08, width=1.2,
           dash="5 4")
A = flow_net(flow2, hi_edges=cut_edges, avoid=back_edges, h=265,
             override={("a", "b"): (38, -13), ("c", "d"): (38, 13), ("b", "c"): (-46, 24)})
A.LAB.text(22, 226, "S", size=16, color="var(--accent)", font=SERIF_IT, italic=True, anchor="start")
A.LAB.text(458, 226, "T", size=16, color="var(--accent2)", font=SERIF_IT, italic=True, anchor="end")
A.text(240, 256, f"|f| = {value(E, flow2, 's')} = ‖S, T‖ = {cap[cut_edges[0]]} + {cap[cut_edges[1]]}", size=13)
html = overlay_figure(A, A.LAB,
    "<strong>The augmented flow is maximum, and the cut proves it (the book’s Figures 10.3 and 10.6).</strong> "
    "After augmenting, the flow has value 15. The vertices reachable from <i>s</i> in its residual graph are "
    "<i>S</i> = {<i>s</i>, <i>a</i>, <i>c</i>}: both edges from <i>S</i> to <i>T</i> are saturated (5/5 and "
    "10/10, thick) and the only edge from <i>T</i> to <i>S</i>, <i>b</i>→<i>c</i>, is avoided (0/15, dashed). By "
    "Lemma 10.1 the flow’s value equals the cut’s capacity, 5 + 10 = 15, so the flow is a maximum flow and the cut "
    "is a minimum cut — here the only one.",
    alt="the maximum flow of value 15 with the minimum cut S = {s, a, c} shaded; the two cut edges are saturated",
    under=under)
save("a10-mincut", html)

# --------------------------------------------------------------------------- 4. Edmonds and Karp's bad example
BV = ["s", "u", "v", "t"]
A = Net(500, 210)
for k, x0 in enumerate((0, 260)):
    P = {"s": (x0 + 30, 95), "u": (x0 + 120, 165), "v": (x0 + 120, 25), "t": (x0 + 210, 95)}
    for n, (x, y) in P.items():
        A.state(f"{n}{k}", x, y, label=n, r=15)
    if k == 0:
        on = [("s", "u"), ("u", "v"), ("v", "t")]
        labs = {("s", "v"): "X", ("s", "u"): "X", ("u", "v"): "1", ("v", "t"): "X", ("u", "t"): "X"}
        for (a, b), lab in labs.items():
            hi = (a, b) in on
            A.arc(f"{a}{k}", f"{b}{k}", lab, off=11, side=(-1 if (a, b) in (("s", "u"), ("u", "v")) else 1)
                  if (a, b) != ("u", "t") else -1,
                  color="var(--hi)" if hi else "currentColor", width=2.4 if hi else 1.4,
                  lcolor="var(--hi)" if hi else "currentColor")
        A.text(x0 + 120, 200, "first: s→u→v→t, 1 unit", size=12.5, color="var(--hi)")
    else:
        on = [("s", "v"), ("v", "u"), ("u", "t")]
        # residual after pushing 1 along s u v t
        res = {("s", "v"): "X", ("s", "u"): "X−1", ("u", "s"): "1", ("v", "u"): "1", ("v", "t"): "X−1",
               ("t", "v"): "1", ("u", "t"): "X"}
        for (a, b), lab in res.items():
            hi = (a, b) in on
            pair = (b, a) in res
            if pair:
                A.arc(f"{a}{k}", f"{b}{k}", lab, bend=11, off=13, color="var(--hi)" if hi else "currentColor",
                      width=2.4 if hi else 1.4, lcolor="var(--hi)" if hi else "currentColor")
            else:
                side = {("s", "v"): 1, ("v", "u"): -1, ("u", "t"): -1}[(a, b)]
                A.arc(f"{a}{k}", f"{b}{k}", lab, off=11, side=side, color="var(--hi)" if hi else "currentColor",
                      width=2.4 if hi else 1.4, lcolor="var(--hi)" if hi else "currentColor")
        A.text(x0 + 120, 200, "then: s→v→u→t in the residual graph", size=12.5, color="var(--hi)")
A.line(250, 10, 250, 185, color="var(--muted)", width=1, dash="3 4")
html = overlay_figure(A, A.LAB,
    "<strong>Edmonds and Karp’s bad example for Ford–Fulkerson (the book’s Figure 10.7).</strong> Left: the "
    "network, with a large integer <i>X</i>; its maximum flow is 2<i>X</i>. If the first augmenting path is "
    "<i>s</i>→<i>u</i>→<i>v</i>→<i>t</i>, it carries only 1 unit (the middle edge). Right: the residual graph "
    "then contains the backward edge <i>v</i>→<i>u</i>, and the path <i>s</i>→<i>v</i>→<i>u</i>→<i>t</i> again "
    "carries 1 unit, cancelling the flow on <i>u</i>→<i>v</i>. Alternating the two paths, Ford–Fulkerson makes "
    "2<i>X</i> augmentations; choosing <i>s</i>→<i>u</i>→<i>t</i> and <i>s</i>→<i>v</i>→<i>t</i> instead takes 2.",
    alt="a four-vertex network with four edges of capacity X and a middle edge of capacity 1, and its residual graph after one bad augmentation")
save("a10-bad-example", html)

# --------------------------------------------------------------------------- 5. Zwick's network (Figure 10.8)
ZE = [("s", "a"), ("s", "b"), ("s", "d"), ("b", "a"), ("b", "c"), ("d", "c"), ("a", "t"), ("c", "t"), ("d", "t")]
ZL = {("s", "a"): "X", ("s", "b"): "X", ("s", "d"): "X", ("b", "a"): "1", ("b", "c"): "1", ("d", "c"): "φ",
      ("a", "t"): "X", ("c", "t"): "X", ("d", "t"): "X"}
ZPATHS = {"central": "sbct", "A": "sabct", "B": "sdcbat", "C": "sbcdt"}
A = Net(600, 330, r=15)
LAB = A.LAB
ZP = {"s": (150, 30), "a": (40, 120), "b": (115, 120), "c": (185, 120), "d": (260, 120), "t": (150, 210)}
ZP = {k: (x, y + 25) for k, (x, y) in ZP.items()}
for n, (x, y) in ZP.items():
    A.state(n, x, y)
cen = list(zip(ZPATHS["central"], ZPATHS["central"][1:]))
ZOFF = {("s", "a"): (-14, -12), ("s", "b"): (12, -2), ("s", "d"): (14, -12), ("b", "a"): (0, -12),
        ("b", "c"): (0, -12), ("d", "c"): (0, -12), ("a", "t"): (-14, 12), ("c", "t"): (12, 2), ("d", "t"): (14, 12)}
for e in ZE:
    hi = e in cen
    A.arc(*e, color="var(--hi)" if hi else "currentColor", width=2.4 if hi else 1.4)
    (x1, y1), (x2, y2) = ZP[e[0]], ZP[e[1]]
    LAB.text((x1 + x2) / 2 + ZOFF[e][0], (y1 + y2) / 2 + ZOFF[e][1], ZL[e], size=13, halo=True,
             color="var(--hi)" if hi else "currentColor")
A.text(150, 275, "central path s→b→c→t first", size=12.5, color="var(--hi)")
# three small panels with the paths A, B, C
mini = {"s": (0, -36), "a": (-48, 0), "b": (-16, 0), "c": (16, 0), "d": (48, 0), "t": (0, 36)}
for k, name in enumerate("ABC"):
    cx, cy = 395, 50 + 112 * k
    for n, (dx, dy) in mini.items():
        A.state(f"{n}{name}", cx + dx, cy + dy, label="", r=5)
    p = ZPATHS[name]
    pe = list(zip(p, p[1:]))
    for (u, v) in ZE:
        if (u, v) in pe:
            A.arc(f"{u}{name}", f"{v}{name}", color="var(--hi)", width=2.2)
        elif (v, u) in pe:
            pass
        else:
            A.arc(f"{u}{name}", f"{v}{name}", color="var(--muted)", width=1.0)
    for (u, v) in pe:
        if (u, v) not in ZE:  # backward residual edge
            A.arc(f"{u}{name}", f"{v}{name}", color="var(--hi)", width=2.2)
    A.text(cx + 70, cy - 6, f"path {name}", size=13, anchor="start", weight="600")
    A.text(cx + 70, cy + 12, " ".join(p), size=13, anchor="start", font=SERIF_IT, italic=True)
A.line(320, 10, 320, 318, color="var(--muted)", width=1, dash="3 4")
html = overlay_figure(A, LAB,
    "<strong>Zwick’s network, on which Ford–Fulkerson need not halt (the book’s Figure 10.8, vertex names "
    "added).</strong> Six edges have a large capacity <i>X</i>; the three horizontal edges <i>b</i>→<i>a</i>, "
    "<i>b</i>→<i>c</i>, <i>d</i>→<i>c</i> have capacities 1, 1 and φ = (√5 − 1)/2. After the central path, the "
    "augmenting paths A, B, C (right; thick edges, including the backward residual edges <i>a</i>→<i>b</i>, "
    "<i>c</i>→<i>b</i>, <i>c</i>→<i>d</i>) can be repeated in the order B, C, B, A forever, each round of four "
    "pushing smaller powers of φ than the round before.",
    alt="Zwick's six-vertex network with capacities X, 1, 1 and phi, and three small copies showing augmenting paths A, B and C")
save("a10-zwick", html)

# --------------------------------------------------------------------------- 6. flow decomposition (Figure 10.9)
DF = dict(zip(E, [9, 6, 4, 5, 3, 3, 4, 14, 11]))
assert conserved(V, E, DF, "s", "t") and value(E, DF, "s") == 15
PIECES = [("path", "sabt", 4), ("path", "sacdt", 5), ("path", "scdt", 6), ("cycle", "cdbc", 3)]
tot = {e: 0 for e in E}
for kind, p, w in PIECES:
    for e in zip(p, p[1:]):
        tot[e] += w
assert tot == DF
COLORS = ["var(--hi)", "var(--accent2)", "var(--accent)", "currentColor"]
A = Net(620, 390, r=15)
LAB = A.LAB
SC = 1.0
BP = {"s": (40, 115), "a": (160, 40), "b": (300, 40), "c": (160, 190), "d": (300, 190), "t": (420, 115)}
for n, (x, y) in BP.items():
    A.state(n, x, y)
DOFF = {("s", "a"): (-12, -10), ("s", "c"): (-12, 10), ("a", "b"): (0, -12), ("a", "c"): (-12, 0),
        ("b", "c"): (14, -12), ("d", "b"): (12, 0), ("b", "t"): (12, -10), ("c", "d"): (0, 12), ("d", "t"): (12, 10)}
for e in E:
    A.arc(*e, width=1.4)
    (x1, y1), (x2, y2) = BP[e[0]], BP[e[1]]
    LAB.text((x1 + x2) / 2 + DOFF[e][0], (y1 + y2) / 2 + DOFF[e][1], str(DF[e]), size=13, halo=True)
A.text(530, 70, "value 15", size=13, weight="600")
A.text(530, 92, "9 edges carry flow", size=12.5)
A.text(530, 110, "= 3 paths + 1 cycle", size=12.5)
mini = {"s": (0, 30), "a": (36, 0), "b": (84, 0), "c": (36, 60), "d": (84, 60), "t": (120, 30)}
for k, (kind, p, w) in enumerate(PIECES):
    x0, y0 = 20 + 152 * k, 268
    pe = list(zip(p, p[1:]))
    for n, (dx, dy) in mini.items():
        A.state(f"{n}{k}", x0 + dx, y0 + dy, label="", r=5)
    for e in E:
        if e in pe:
            A.arc(f"{e[0]}{k}", f"{e[1]}{k}", color=COLORS[k], width=2.4)
        else:
            A.arc(f"{e[0]}{k}", f"{e[1]}{k}", color="var(--muted)", width=0.9)
    A.text(x0 + 60, y0 + 86, f"{kind} {' '.join(p)}: {w}", size=12.5, color="currentColor")
A.line(10, 245, 610, 245, color="var(--muted)", width=1, dash="3 4")
html = overlay_figure(A, LAB,
    "<strong>A flow decomposition (the flow of the book’s Figure 10.9).</strong> Top: a flow of value 15 (edge labels "
    "are flow values only). Bottom: it is the sum of three <i>s</i>–<i>t</i> path flows, with weights 4, 5 and 6, "
    "and one cycle flow around <i>c</i>→<i>d</i>→<i>b</i>→<i>c</i> with weight 3; for example <i>c</i>→<i>d</i> "
    "carries 5 + 6 + 3 = 14. The paths carry the value, 4 + 5 + 6 = 15; the cycle carries none. Four pieces, "
    "within the theorem’s bound of one per edge with positive flow (9).",
    alt="a flow of value 15 and its decomposition into three weighted paths and one weighted cycle")
save("a10-decomposition", html)
