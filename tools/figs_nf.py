#!/usr/bin/env python3
"""Figures for lecture note F (Balances and Pseudoflows). Writes tools/figs/nf-<name>.html; then run
tools/assemble.py on content/4-lecture-notes/f-balances-and-pseudoflows.md. Every number drawn is recomputed here
from the note's network (vertex names a..f added); tools/checks/nf.py checks the same numbers independently."""
import math
import os

from figlib import SVG, Automaton

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")
os.makedirs(OUT, exist_ok=True)


def save(name, html):
    with open(os.path.join(OUT, name + ".html"), "w", encoding="utf-8") as f:
        f.write(html + "\n")
    print("wrote", name)


def overlay_figure(A, overlay, caption, alt):
    svg = A.svg(alt)
    svg = svg.replace("</svg>", "".join(overlay.items) + "</svg>")
    out = f'<figure class="cs-fig">{svg}<figcaption>{caption}</figcaption></figure>'
    assert "\n\n" not in out
    return out.replace("\n", " ")


class Net(Automaton):
    """Automaton plus edge labels collected in self.LAB (drawn on top of edges and states)."""

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
        nx, ny = dy / L, -dx / L
        px, py = x1 + dx * t, y1 + dy * t
        bulge = bend * 2 * 2 * t * (1 - t)
        sgn = 1 if bend >= 0 else -1
        lx = px + nx * (bulge + sgn * off * side)
        ly = py + ny * (bulge + sgn * off * side)
        self.LAB.text(lx + ldx, ly + ldy, label, size=size, color=lcolor, halo=True, weight=weight)


# ------------------------------------------------------------------ the note's network
V = list("abcdef")
E = [("a", "b"), ("b", "c"), ("b", "f"), ("c", "f"), ("c", "d"), ("e", "c"), ("d", "e"), ("f", "e"), ("f", "a")]
cap = dict(zip(E, [20, 5, 10, 15, 15, 10, 20, 10, 10]))
bal = {"a": -5, "b": 2, "c": -1, "d": 6, "e": -4, "f": 2}
flow = dict(zip(E, [10, 5, 3, 9, 7, 10, 1, 5, 5]))
psi = dict(zip(E, [5, 0, 3, 4, 7, 10, 1, 0, 5]))


def netin(f, v):
    return sum(f[e] for e in E if e[1] == v) - sum(f[e] for e in E if e[0] == v)


assert sum(bal.values()) == 0
assert all(0 <= flow[e] <= cap[e] for e in E) and all(netin(flow, v) == bal[v] for v in V)
bpsi = {v: bal[v] - netin(psi, v) for v in V}
assert bpsi == {"a": -5, "b": 0, "c": 0, "d": 0, "e": 5, "f": 0}

POS = {"a": (60, 125), "b": (140, 45), "c": (300, 45), "d": (380, 125), "e": (300, 205), "f": (140, 205)}
# label offsets from the edge midpoint
OFF = {("a", "b"): (-16, -8), ("b", "c"): (0, -12), ("b", "f"): (-17, 0), ("c", "f"): (-20, -10),
       ("c", "d"): (16, -8), ("e", "c"): (17, 0), ("d", "e"): (16, 8), ("f", "e"): (0, 12), ("f", "a"): (-16, 8)}
BOFF = {"a": (-30, 0), "b": (-22, -20), "c": (22, -20), "d": (30, 0), "e": (22, 20), "f": (-22, 20)}


def bal_label(S, v, x, y, val, size=13):
    if val == 0:
        return
    col = "var(--accent2)" if val < 0 else "var(--accent)"
    S.text(x, y, f"{val:+d}".replace("-", "−"), size=size, color=col, weight="600", halo=True)


# ------------------------------------------------------------------ 1. the network and a feasible flow
A = Net(440, 250)
for v, (x, y) in POS.items():
    A.state(v, x, y)
for e in E:
    A.arc(*e)
    (x1, y1), (x2, y2) = POS[e[0]], POS[e[1]]
    dx, dy = OFF[e]
    A.LAB.text((x1 + x2) / 2 + dx, (y1 + y2) / 2 + dy, f"{flow[e]}/{cap[e]}", size=13, halo=True)
for v, (x, y) in POS.items():
    dx, dy = BOFF[v]
    bal_label(A.LAB, v, x + dx, y + dy, bal[v])
html = overlay_figure(A, A.LAB,
    "<strong>A network with balances, and a feasible flow (the note’s figures on pp. 2–3, vertex names added).</strong> "
    "The colored number beside each vertex is its balance <i>b</i>(<i>v</i>) = flow in − flow out: negative is supply "
    "(<i>a</i>, <i>c</i>, <i>e</i> supply 5, 1, 4), positive is demand (<i>b</i>, <i>d</i>, <i>f</i> absorb 2, 6, 2). "
    "Each edge is labeled <i>flow</i>/<i>capacity</i>; at <i>c</i>, for instance, 5 + 10 units enter and 9 + 7 leave, "
    "a net inflow of −1.",
    alt="six vertices a to f in a hexagon with balances -5, +2, -1, +6, -4, +2 and a feasible flow on nine edges")
save("nf-network", html)

# ------------------------------------------------------------------ 2. the transformed network G'
P2 = {"s": (40, 150), "a": (120, 150), "b": (195, 75), "c": (345, 75), "d": (420, 150), "e": (345, 225),
      "f": (195, 225), "t": (520, 150)}
A = Net(565, 300)
for v, (x, y) in P2.items():
    A.state(v, x, y, hi=False)
for e in E:
    A.arc(*e)
    (x1, y1), (x2, y2) = P2[e[0]], P2[e[1]]
    dx, dy = OFF[e]
    A.LAB.text((x1 + x2) / 2 + dx, (y1 + y2) / 2 + dy, str(cap[e]), size=13, halo=True)
S_COL, T_COL = "var(--accent2)", "var(--accent)"
A.arc("s", "a", color=S_COL, width=2)
A.LAB.text(80, 140, "5", color=S_COL, weight="600", halo=True)
# curved supply / demand edges, drawn as raw paths so that they can loop around the hexagon
A.path("M50,135 C70,20 250,12 330,62", color=S_COL, width=2, arrow=True)
A.LAB.text(150, 28, "1", color=S_COL, weight="600", halo=True)
A.path("M50,165 C70,280 250,288 330,238", color=S_COL, width=2, arrow=True)
A.LAB.text(150, 272, "4", color=S_COL, weight="600", halo=True)
A.path("M210,62 C290,12 470,20 512,135", color=T_COL, width=2, arrow=True)
A.LAB.text(420, 28, "2", color=T_COL, weight="600", halo=True)
A.arc("d", "t", color=T_COL, width=2)
A.LAB.text(470, 140, "6", color=T_COL, weight="600", halo=True)
A.path("M210,238 C290,288 470,280 512,165", color=T_COL, width=2, arrow=True)
A.LAB.text(420, 272, "2", color=T_COL, weight="600", halo=True)
html = overlay_figure(A, A.LAB,
    "<strong>The reduction to maximum flow (the note’s figure on p. 2).</strong> A new source <i>s</i> gets an edge "
    "to every supply vertex, with capacity equal to its supply (5, 1, 4), and every demand vertex gets an edge "
    "to a new target <i>t</i>, with capacity equal to its demand (2, 6, 2). The original network has a "
    "feasible flow if and only if this one has an (<i>s</i>, <i>t</i>)-flow that saturates all six new edges, that "
    "is, a flow of value 10; the flow of the previous figure, extended by saturating the new edges, is one.",
    alt="the hexagon network with a new source s feeding a, c, e and a new target t fed by b, d, f")
save("nf-reduction", html)

# ------------------------------------------------------------------ 3. residual graph of the pseudoflow
R = {}
for (u, v) in E:
    if cap[(u, v)] - psi[(u, v)] > 0:
        R[(u, v)] = cap[(u, v)] - psi[(u, v)]
    if psi[(u, v)] > 0:
        R[(v, u)] = psi[(u, v)]
PATH = [("a", "b"), ("b", "f"), ("f", "c"), ("c", "e")]
Rpush = min([-bpsi["a"], bpsi["e"]] + [R[e] for e in PATH])
assert [R[e] for e in PATH] == [15, 7, 4, 10] and Rpush == 4
A = Net(440, 260)
for v, (x, y) in POS.items():
    A.state(v, x, y + 5, hi=v in ("a", "e"))
SIDE = {("b", "c"): 1, ("c", "e"): 1, ("f", "e"): 1}
for (u, v), rc in R.items():
    on = (u, v) in PATH
    col = "var(--hi)" if on else "currentColor"
    wid = 2.6 if on else 1.4
    if (v, u) in R:
        A.arc(u, v, str(rc), bend=8, off=9, color=col, width=wid, lcolor=col, weight="600" if on else None)
    else:
        A.arc(u, v, str(rc), off=11, side=SIDE[(u, v)], color=col, width=wid, lcolor=col,
              weight="600" if on else None)
bal_label(A.LAB, "a", POS["a"][0] - 32, POS["a"][1] + 5, -5)
bal_label(A.LAB, "e", POS["e"][0] + 24, POS["e"][1] + 26, 5)
html = overlay_figure(A, A.LAB,
    "<strong>A pseudoflow’s residual graph and an augmenting path (the note’s figure on p. 5).</strong> The "
    "pseudoflow ψ puts 5, 0, 3, 4, 7, 10, 1, 0, 5 on <i>a</i>→<i>b</i>, <i>b</i>→<i>c</i>, <i>b</i>→<i>f</i>, "
    "<i>c</i>→<i>f</i>, <i>c</i>→<i>d</i>, <i>e</i>→<i>c</i>, <i>d</i>→<i>e</i>, <i>f</i>→<i>e</i>, <i>f</i>→<i>a</i>. "
    "Every vertex is balanced except <i>a</i> (residual balance −5, an excess) and <i>e</i> (+5, a deficit). The "
    "residual capacities are drawn as usual: <i>c</i> − ψ forward, ψ backward. The highlighted path "
    "<i>a</i>→<i>b</i>→<i>f</i>→<i>c</i>→<i>e</i> has residual capacities 15, 7, 4, 10, so 4 units can be pushed; "
    "its last two edges are backward, so the push lowers ψ(<i>c</i>→<i>f</i>) to 0 and ψ(<i>e</i>→<i>c</i>) to 6.",
    alt="residual graph of the pseudoflow with residual balances -5 at a and +5 at e; augmenting path a b f c e")
save("nf-residual", html)

# ------------------------------------------------------------------ 4. the vertex z for maximum flow with balances
A = Net(470, 210)
Pz = {"s": (60, 70), "t": (250, 70), "v": (410, 70), "z": (155, 165)}
for v, (x, y) in Pz.items():
    A.state(v, x, y)
A.arc("s", "t", "10", off=12)
A.arc("t", "v", "20", off=12)
A.arc("t", "z", "∞", bend=10, off=10)
A.arc("z", "s", "∞", bend=10, off=10)
A.arc("z", "t", "∞", bend=10, off=10, color="var(--hi)", width=2.2, lcolor="var(--hi)", weight="600")
A.arc("s", "z", "∞", bend=10, off=10, color="var(--hi)", width=2.2, lcolor="var(--hi)", weight="600")
A.LAB.text(410, 103, "+15", color="var(--accent)", weight="600", halo=True)
A.LAB.text(155, 195, "−15", color="var(--accent2)", weight="600", halo=True)
html = overlay_figure(A, A.LAB,
    "<strong>The vertex <i>z</i> for a maximum flow with balances, on a small counterexample.</strong> Vertex "
    "<i>v</i> must absorb 15 units, which can only come from <i>t</i>; <i>s</i> and <i>t</i> are exempt from "
    "balance constraints. The note adds <i>z</i> (balance −15) with uncapacitated edges <i>t</i>→<i>z</i> and "
    "<i>z</i>→<i>s</i> only; then <i>t</i> must pass its net inflow on to <i>z</i>, and that net inflow is "
    "negative here (at most 10 in, 15 out), so the new network has no feasible flow although the original has (<i>s</i>, "
    "<i>t</i>)-flows, with maximum value 10. The highlighted reverse edges <i>z</i>→<i>t</i> and <i>s</i>→<i>z</i> "
    "repair the construction.",
    alt="vertices s, t, v, z; edges s to t (10), t to v (20), and uncapacitated edges between z and both s and t")
save("nf-zvertex", html)
