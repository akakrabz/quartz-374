#!/usr/bin/env python3
"""Figures for lecture note G (Minimum-Cost Flows). Writes tools/figs/ng-<name>.html; then run tools/assemble.py on
content/4-lecture-notes/g-minimum-cost-flows.md. The example network and its numbers are original; every number drawn
is recomputed here, and tools/checks/ng.py checks them independently (LP, networkx, brute force)."""
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


# ------------------------------------------------------------------ the example network
V = ["s", "a", "b", "t"]
E = [("s", "a"), ("s", "b"), ("a", "b"), ("a", "t"), ("b", "t")]
cap = dict(zip(E, [2, 2, 2, 2, 3]))
cost = dict(zip(E, [1, 3, 1, 4, 1]))
bal = {"s": -4, "a": 0, "b": 0, "t": 4}
f18 = dict(zip(E, [2, 2, 0, 2, 2]))
f16 = dict(zip(E, [2, 2, 1, 1, 3]))


def netin(f, v):
    return sum(f[e] for e in E if e[1] == v) - sum(f[e] for e in E if e[0] == v)


for f in (f18, f16):
    assert all(0 <= f[e] <= cap[e] for e in E) and all(netin(f, v) == bal[v] for v in V)
assert sum(cost[e] * f18[e] for e in E) == 18 and sum(cost[e] * f16[e] for e in E) == 16

POS = {"s": (50, 120), "a": (200, 45), "b": (200, 195), "t": (350, 120)}
OFF = {("s", "a"): (-14, -12), ("s", "b"): (-14, 12), ("a", "b"): (-28, 0), ("a", "t"): (14, -12),
       ("b", "t"): (14, 12)}
COSTC = "var(--accent)"


def label2(S, x, y, a, bracket, col="currentColor", bold=False):
    """'a [k]' with the bracketed cost in the accent colour."""
    w = "font-weight:600;" if bold else ""
    S.add(f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" dominant-baseline="central" fill="{col}" '
          f'style="font-size:13px;font-family:\'Source Sans 3\',\'Source Sans Pro\',system-ui,sans-serif;{w}'
          f'paint-order:stroke;stroke:var(--paper);stroke-width:5px;stroke-linejoin:round;">{a} '
          f'<tspan fill="{COSTC if col == "currentColor" else col}">[{str(bracket).replace("-", "−")}]</tspan></text>')


A = Net(400, 240)
for v, (x, y) in POS.items():
    A.state(v, x, y)
for e in E:
    A.arc(*e)
    (x1, y1), (x2, y2) = POS[e[0]], POS[e[1]]
    dx, dy = OFF[e]
    label2(A.LAB, (x1 + x2) / 2 + dx, (y1 + y2) / 2 + dy, f"{f16[e]}/{cap[e]}", cost[e])
A.LAB.text(50, 152, "−4", color="var(--accent2)", weight="600", halo=True)
A.LAB.text(350, 152, "+4", color="var(--accent2)", weight="600", halo=True)
html = overlay_figure(A, A.LAB,
    "<strong>The running example, with its minimum-cost flow.</strong> Four units must travel from <i>s</i> "
    "(balance −4) to <i>t</i> (balance +4). Each edge is labeled <i>flow</i>/<i>capacity</i> [<i>cost per "
    "unit</i>]. The flow shown costs 2·1 + 2·3 + 1·1 + 1·4 + 3·1 = 16, the minimum: both edges out of <i>s</i> are "
    "full, <i>b</i>→<i>t</i> is full, and only one unit can take the cheap route <i>s</i>→<i>a</i>→<i>b</i>→<i>t</i> "
    "next to the two that enter <i>b</i> directly.",
    alt="network s, a, b, t with capacities and costs; minimum-cost flow of cost 16")
save("ng-network", html)

# ------------------------------------------------------------------ residual graph of the 18-flow
R = []
for e in E:
    u, v = e
    if cap[e] - f18[e] > 0:
        R.append((u, v, cap[e] - f18[e], cost[e]))
    if f18[e] > 0:
        R.append((v, u, f18[e], -cost[e]))
CYC = [("a", "b"), ("b", "t"), ("t", "a")]
Rd = {(u, v): (c, k) for (u, v, c, k) in R}
assert sorted(Rd) == sorted([("a", "s"), ("b", "s"), ("a", "b"), ("t", "a"), ("b", "t"), ("t", "b")])
assert sum(Rd[e][1] for e in CYC) == -2 and min(Rd[e][0] for e in CYC) == 1
A = Net(400, 250)
for v, (x, y) in POS.items():
    A.state(v, x, y + 5)
for (u, v), (c, k) in Rd.items():
    on = (u, v) in CYC
    col = "var(--hi)" if on else "currentColor"
    wid = 2.6 if on else 1.4
    pair = (v, u) in Rd
    A.edge(u, v, bend=9 if pair else 0, color=col, width=wid)
    (x1, y1), (x2, y2) = POS[u], POS[v]
    y1 += 5
    y2 += 5
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    nx, ny = dy / L, -dx / L
    off = (9 * 2 * 0.5 + 12) if pair else 13
    side = 1 if pair else {("a", "s"): -1, ("b", "s"): 1, ("a", "b"): 1}.get((u, v), 1)
    if (u, v) == ("a", "b"):
        lx, ly = x1 - 30, (y1 + y2) / 2
    else:
        lx, ly = (x1 + x2) / 2 + nx * off * side, (y1 + y2) / 2 + ny * off * side
    label2(A.LAB, lx, ly, str(c), k, col=col if on else "currentColor", bold=on)
html = overlay_figure(A, A.LAB,
    "<strong>The residual graph of a feasible flow of cost 18, and a negative cycle.</strong> The flow sends 2 units "
    "along <i>s</i>→<i>a</i>→<i>t</i> and 2 along <i>s</i>→<i>b</i>→<i>t</i>. Residual edges are labeled "
    "<i>residual capacity</i> [<i>residual cost</i>]; a backward edge costs minus the cost of its edge. The cycle "
    "<i>a</i>→<i>b</i>→<i>t</i>→<i>a</i> costs 1 + 1 − 4 = −2 and can carry 1 unit (the spare capacity of "
    "<i>b</i>→<i>t</i>): reroute one unit from <i>a</i>→<i>t</i> through <i>b</i>, and the cost drops to 16.",
    alt="residual graph of the flow of cost 18 with the negative cycle a b t highlighted")
save("ng-residual", html)

# ------------------------------------------------------------------ Fulkerson's gadget
A = Net(520, 215, r=18)
A.state("u", 70, 45)
A.state("v", 450, 45)
A.state("u2", 70, 165, label="u")
A.state("z", 260, 165, label="z", italic=True)
A.state("v2", 450, 165, label="v")
A.arc("u", "v")
A.LAB.text(260, 30, "ℓ ≤ f ≤ c,  cost k", size=13, halo=True)
A.arc("u2", "z")
A.LAB.text(165, 150, "f − ℓ ≥ 0", size=13, halo=True)
A.LAB.text(165, 182, "cost k", size=13, halo=True, color=COSTC)
A.arc("v2", "z")
A.LAB.text(355, 150, "c − f ≥ 0", size=13, halo=True)
A.LAB.text(355, 182, "cost 0", size=13, halo=True, color=COSTC)
A.LAB.text(70, 82, "b(u)", size=13, halo=True, color="var(--accent2)")
A.LAB.text(450, 82, "b(v)", size=13, halo=True, color="var(--accent2)")
A.LAB.text(70, 202, "b(u) + ℓ", size=13, halo=True, color="var(--accent2)")
A.LAB.text(260, 202, "c − ℓ", size=13, halo=True, color="var(--accent2)")
A.LAB.text(450, 202, "b(v) − c", size=13, halo=True, color="var(--accent2)")
A.path("M260,82 L260,118", color="var(--muted)", width=2.2, arrow=True)
html = overlay_figure(A, A.LAB,
    "<strong>Removing the bounds from one edge (Fulkerson; the note’s figure on p. 11).</strong> The edge "
    "<i>u</i>→<i>v</i> with bounds ℓ ≤ <i>f</i> ≤ <i>c</i> and cost <i>k</i> becomes a new vertex <i>z</i> with two "
    "uncapacitated edges into it, <i>u</i>→<i>z</i> carrying <i>f</i> − ℓ at cost <i>k</i> and <i>v</i>→<i>z</i> "
    "carrying <i>c</i> − <i>f</i> at cost 0. Balances (flow in − flow out) are written below the vertices: <i>z</i> "
    "absorbs exactly <i>c</i> − ℓ, so both new flows are non-negative exactly when ℓ ≤ <i>f</i> ≤ <i>c</i>, and every "
    "cost drops by the constant ℓ<i>k</i>.",
    alt="an edge u to v with bounds and cost, replaced by a vertex z with edges from u and from v")
save("ng-gadget", html)
