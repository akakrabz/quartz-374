#!/usr/bin/env python3
"""Figures for the Chapter 10 exercises page (content/2-algorithms/10-maximum-flows-and-minimum-cuts-exercises.md).
Writes tools/figs/a10x-<name>.html; then run tools/assemble.py on the page. Every number drawn here (cut
capacities, residual capacities, BFS levels, level-cut sizes, flow values) is computed below by brute force over
all cuts or by direct construction; tools/checks/a10x.py re-derives the same facts independently."""
import itertools
import os
from collections import deque

from figlib import SVG, Automaton, SERIF_IT, SANS, MONO

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")
os.makedirs(OUT, exist_ok=True)


def save(name, html):
    with open(os.path.join(OUT, name + ".html"), "w", encoding="utf-8") as f:
        f.write(html + "\n")
    print("wrote", name)


def it(s):
    return f"<i>{s}</i>"


def cut_cap(E, S):
    return sum(c for u, v, c in E if u in S and v not in S)


def min_cuts(V, E, s, t):
    others = [v for v in V if v not in (s, t)]
    caps = {}
    for r in range(len(others) + 1):
        for sub in itertools.combinations(others, r):
            S = frozenset((s,) + sub)
            caps[S] = cut_cap(E, S)
    lam = min(caps.values())
    return lam, [S for S, c in caps.items() if c == lam], caps


# =========================================================================== 1. Exercise 10.4: G and G'
G = [("s", "u", 1), ("u", "v", 7), ("v", "u", 10), ("v", "t", 1)]
m = min(7, 10)
Gp = [("s", "u", 1), ("v", "u", 10 - m), ("v", "t", 1)]
V4 = ["s", "u", "v", "t"]
lamG, cutsG, capsG = min_cuts(V4, G, "s", "t")
lamGp, cutsGp, capsGp = min_cuts(V4, Gp, "s", "t")
assert (lamG, lamGp) == (1, 0)
assert sorted(map(sorted, cutsG)) == [["s"], ["s", "u", "v"]] and [sorted(S) for S in cutsGp] == [["s", "u"]]
assert capsG[frozenset({"s", "u"})] == 7

A = Automaton(580, 262, r=17)
X = {"s": 70, "u": 210, "v": 370, "t": 510}
Y1, Y2 = 74, 196
for v in V4:
    A.state(v, X[v], Y1)
    A.state(v + "'", X[v], Y2, label=v)
A.edge("s", "u", "1", label_dist=12)
A.edge("u", "v", "7", bend=18, label_dist=11)
A.edge("v", "u", "10", bend=18, label_dist=11)
A.edge("v", "t", "1", label_dist=12)
A.edge("s'", "u'", "1", label_dist=12)
A.edge("v'", "u'", "3", label_dist=12)
A.edge("v'", "t'", "1", label_dist=12)
A.text(22, Y1, "G", size=17, font=SERIF_IT, italic=True)
A.text(22, Y2, "G′", size=17, font=SERIF_IT, italic=True)
for x, lab in ((174, "{s}: 1"), (474, "{s, u, v}: 1")):
    A.line(x, Y1 - 46, x, Y1 + 40, color="var(--hi)", width=1.6, dash="5 4")
    A.text(x, Y1 - 56, lab, size=13, color="var(--hi)", weight=600)
A.line(252, Y2 - 40, 252, Y2 + 40, color="var(--hi)", width=1.6, dash="5 4")
A.text(252, Y2 + 52, "{s, u}: 0", size=13, color="var(--hi)", weight=600)
A.text(92, Y1 + 42, "max flow 1", size=13, color="var(--muted)")
A.text(92, Y2 + 42, "max flow 0", size=13, color="var(--muted)")
save("a10x-opposing", A.figure(
    "<strong>Exercise 10.4 is false as printed.</strong> Top: <i>G</i>, with the opposing pair <i>u</i>→<i>v</i> (7) "
    "and <i>v</i>→<i>u</i> (10). Its maximum flow is 1, and its minimum cuts (dashed, labeled <i>S</i>: capacity) "
    "are {<i>s</i>} and {<i>s</i>, <i>u</i>, <i>v</i>}. Bottom: <i>G</i>′, where both capacities drop by 7, so only "
    "<i>v</i>→<i>u</i> survives, with capacity 3. Now <i>t</i> is unreachable, the maximum flow is 0, and the only "
    "minimum cut is {<i>s</i>, <i>u</i>}, which costs 7 in <i>G</i>. Every cut that separates <i>u</i> from "
    "<i>v</i> gets 7 cheaper; the others keep their capacity.",
    alt="two four-vertex networks s, u, v, t; top with an opposing pair 7 and 10, bottom with a single edge v to u "
        "of capacity 3; dashed minimum cuts"))

# =========================================================================== 2. Exercise 10.5: residual cycle
E5 = [("s", "a", 1), ("a", "b", 2), ("b", "t", 2), ("a", "t", 2)]
f5 = {("s", "a"): 1, ("a", "b"): 0, ("b", "t"): 0, ("a", "t"): 1}
V5 = ["s", "a", "b", "t"]
lam5, cuts5, caps5 = min_cuts(V5, E5, "s", "t")
assert lam5 == 1 and cuts5 == [frozenset({"s"})]
assert sum(x for (u, v), x in f5.items() if u == "s") == lam5
res = {}
for u, v, c in E5:
    if f5[(u, v)] < c:
        res[(u, v)] = c - f5[(u, v)]
    if f5[(u, v)] > 0:
        res[(v, u)] = f5[(u, v)]
assert res == {("a", "s"): 1, ("a", "b"): 2, ("b", "t"): 2, ("a", "t"): 1, ("t", "a"): 1}
CYC = [("a", "b"), ("b", "t"), ("t", "a")]
eps = min(res[e] for e in CYC)
f5b = dict(f5)
for (x, y) in CYC:
    if (x, y) in f5b:
        f5b[(x, y)] += eps
    else:
        f5b[(y, x)] -= eps
assert f5b == {("s", "a"): 1, ("a", "b"): 1, ("b", "t"): 1, ("a", "t"): 0}


# who reaches t in G_f, who is reached from s
def reach(pairs, src, rev=False):
    seen, Q = {src}, deque([src])
    while Q:
        x = Q.popleft()
        for a, b in pairs:
            if rev:
                a, b = b, a
            if a == x and b not in seen:
                seen.add(b)
                Q.append(b)
    return seen


assert reach(res, "s") == {"s"} and reach(res, "t", rev=True) == {"a", "b", "t"}

A = Automaton(620, 205, r=16)
P = {"s": (40, 130), "a": (150, 130), "b": (220, 50), "t": (290, 130)}
OFF = 310
for v, (x, y) in P.items():
    A.state(v, x, y)
    A.state(v + "'", x + OFF, y, label=v)
for u, v, c in E5:
    side = -1 if (u, v) == ("a", "b") else 1
    A.edge(u, v, f"{f5[(u, v)]}/{c}", label_dist=13, label_side=side)
for (u, v), r in res.items():
    on = (u, v) in CYC
    bend = 14 if {u, v} == {"a", "t"} else 0
    A.edge(u + "'", v + "'", str(r), bend=bend, hi=on, width=2.4 if on else 1.6, label_dist=11,
           label_side=-1 if (u, v) == ("a", "b") else 1)
A.text(165, 190, "a maximum flow (flow/capacity)", size=13, color="var(--muted)")
A.text(165 + OFF, 190, "residual graph", size=13, color="var(--muted)")
save("a10x-residual", A.figure(
    "<strong>The uniqueness test of Exercise 10.5(a) on the network of 10.5(d).</strong> Left: a maximum flow of "
    "value 1. Right: its residual graph. The edge <i>a</i>→<i>t</i> is half full, so the residual graph contains "
    "both <i>a</i>→<i>t</i> and <i>t</i>→<i>a</i>; such two-vertex cycles come from a single edge and do not "
    "count. The red cycle <i>a</i>→<i>b</i>→<i>t</i>→<i>a</i> has three vertices: pushing 1 unit around it gives "
    "a second maximum flow, along <i>s</i>→<i>a</i>→<i>b</i>→<i>t</i>. The minimum cut is unique, as 10.5(b) "
    "predicts: <i>s</i> reaches nothing, and every other vertex reaches <i>t</i>.",
    alt="left: four-vertex network with flow labels; right: its residual graph with a red three-vertex cycle"))

# =========================================================================== 3. Exercise 10.7: BFS level cuts
V7 = ["s", "a", "b", "c", "d", "e", "f", "g", "t"]
FWD = [("s", "a"), ("s", "b"), ("a", "c"), ("a", "d"), ("b", "d"), ("b", "e"), ("c", "f"), ("d", "f"), ("e", "g"),
       ("f", "t"), ("g", "t")]
OTHER = [("d", "a"), ("c", "d"), ("g", "e")]
E7 = [(u, v, 1) for u, v in FWD + OTHER]
dist = {"s": 0}
Q = deque(["s"])
while Q:
    x = Q.popleft()
    for u, v, _ in E7:
        if u == x and v not in dist:
            dist[v] = dist[x] + 1
            Q.append(v)
d = dist["t"]
assert d == 4 and all(dist[v] == dist[u] + 1 for u, v in FWD) and all(dist[v] <= dist[u] for u, v in OTHER)
sizes = []
for i in range(d):
    S = {v for v in V7 if dist[v] <= i}
    cross = [(u, v) for u, v, _ in E7 if u in S and v not in S]
    assert all(dist[u] == i and dist[v] == i + 1 for u, v in cross)
    sizes.append(len(cross))
assert sizes == [2, 4, 3, 2]
lam7, _, _ = min_cuts(V7, E7, "s", "t")
assert lam7 == 2 and lam7 * d <= len(E7) and lam7 * d * d <= len(V7) ** 2
L = [sum(1 for v in V7 if dist[v] == i) for i in range(d + 1)]
assert L == [1, 2, 3, 2, 1]

A = Automaton(560, 250, r=15)
P = {"s": (45, 115), "a": (155, 65), "b": (155, 165), "c": (265, 40), "d": (265, 115), "e": (265, 190),
     "f": (375, 75), "g": (375, 165), "t": (485, 115)}
for v, (x, y) in P.items():
    A.state(v, x, y)
for u, v in FWD:
    A.edge(u, v, "", width=1.6)
for u, v in OTHER:
    A.edge(u, v, "", color="var(--muted)", dash="4 3", width=1.4, bend=0 if (u, v) == ("c", "d") else 14)
for i, x in enumerate((100, 210, 320, 430)):
    A.line(x, 22, x, 212, color="var(--hi)", width=1.5, dash="5 4")
    A.text(x, 12, f"{sizes[i]} edges", size=12.5, color="var(--hi)", weight=600)
for i in range(d + 1):
    A.text(45 + 110 * i, 234, f"level {i}", size=12.5, color="var(--muted)")
save("a10x-levels", A.figure(
    "<strong>Level cuts in Exercise 10.7.</strong> Breadth-first levels from <i>s</i>, here with "
    "dist(<i>s</i>, <i>t</i>) = 4. An edge climbs at most one level, so the only edges leaving "
    "<i>S<sub>i</sub></i> = level 0 ∪ ⋯ ∪ level <i>i</i> run from level <i>i</i> to level <i>i</i> + 1 (black); "
    "edges inside a level or back down (dashed gray) never cross a cut forward. The four dashed (<i>s</i>, "
    "<i>t</i>)-cuts therefore have disjoint sets of crossing edges, of sizes 2, 4, 3, 2 — at most <i>E</i> in "
    "total, so one of the <i>d</i> cuts has at most <i>E</i>/<i>d</i> edges. With unit capacities the maximum "
    "flow is 2.",
    alt="nine vertices in five BFS levels with four dashed vertical cuts between consecutive levels"))
