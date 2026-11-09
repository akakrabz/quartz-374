#!/usr/bin/env python3
"""Figures for lecture note E (Matroids). Writes tools/figs/ne-<name>.html; then run tools/assemble.py on
content/4-lecture-notes/e-matroids.md. Both examples are original; the forests, the exchange and the schedule are
recomputed here, and tools/checks/ne.py checks the schedule independently."""
import itertools
import os

from figlib import SVG, Automaton

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")
os.makedirs(OUT, exist_ok=True)


def save(name, html):
    with open(os.path.join(OUT, name + ".html"), "w", encoding="utf-8") as f:
        f.write(html + "\n")
    print("wrote", name)


def components(Vs, Es):
    p = {v: v for v in Vs}

    def find(x):
        while p[x] != x:
            x = p[x]
        return x
    for (u, v) in Es:
        p[find(u)] = find(v)
    return len({find(v) for v in Vs})


def acyclic(Vs, Es):
    return components(Vs, Es) == len(Vs) - len(Es)


# ------------------------------------------------------------------ 1. exchange in the graphic matroid
Vg = ["p", "q", "r", "u", "v", "w"]
POS = {"p": (70, 70), "q": (220, 35), "r": (370, 70), "u": (70, 185), "v": (220, 200), "w": (370, 185)}
Y = [("p", "q"), ("q", "r")]
X = [("p", "r"), ("q", "v"), ("r", "w")]
OTHER = [("p", "u"), ("u", "v"), ("v", "w")]
assert acyclic(Vg, X) and acyclic(Vg, Y) and len(X) > len(Y)
good = [x for x in X if x not in Y and acyclic(Vg, Y + [x])]
bad = [x for x in X if x not in Y and not acyclic(Vg, Y + [x])]
assert good == [("q", "v"), ("r", "w")] and bad == [("p", "r")]

A = Automaton(440, 240, r=16)
for v, (x, y) in POS.items():
    A.state(v, x, y)
for e in OTHER:
    A.edge(*e, color="var(--muted)", width=1.3, dash="4 4")
for e in Y:
    A.edge(*e, color="var(--accent2)", width=3)
for e in good:
    A.edge(*e, color="var(--accent)", width=3)
for e in bad:
    A.edge(*e, color="var(--hi)", width=2.2, dash="7 5")
svg = A.svg("graph on six vertices with a forest Y of two edges and a forest X of three edges")
# arrowheads are not wanted for undirected edges: strip the markers
svg = svg.replace(' marker-end="url(#ARR)"', "")
L = SVG(440, 240)
L.text(140, 40, "Y", color="var(--accent2)", weight="700", size=15, halo=True)
L.text(300, 86, "pr", color="var(--hi)", size=13, halo=True)
L.text(232, 120, "qv", color="var(--accent)", size=13, halo=True)
L.text(392, 128, "rw", color="var(--accent)", size=13, halo=True)
svg = svg.replace("</svg>", "".join(L.items) + "</svg>")
cap = ("<strong>The exchange property in a graphic matroid.</strong> "
       "<i>Y</i> = {<i>pq</i>, <i>qr</i>} (thick, two edges) and <i>X</i> = {<i>pr</i>, <i>qv</i>, <i>rw</i>} (three "
       "edges) are forests, so both are independent in <i>M</i>(<i>G</i>); dashed grey edges are the rest of the graph. "
       "Adding <i>pr</i> to <i>Y</i> closes the cycle <i>p q r</i>, but <i>qv</i> and <i>rw</i> each join two different "
       "trees of <i>Y</i>, so <i>Y</i> + <i>qv</i> and <i>Y</i> + <i>rw</i> are forests. Some edge of <i>X</i> always "
       "works: a forest with more edges has fewer trees, so its edges cannot all stay inside the trees of <i>Y</i>.")
html = f'<figure class="cs-fig">{svg}<figcaption>{cap}</figcaption></figure>'
save("ne-exchange", html.replace("\n", " "))

# ------------------------------------------------------------------ 2. scheduling with deadlines
D = {"a": 2, "b": 1, "c": 2, "d": 3, "e": 1, "f": 4}
P = {"a": 9, "b": 8, "c": 7, "d": 5, "e": 4, "f": 2}
n = 6


def realistic(X):
    return all(sum(1 for x in X if D[x] <= t) <= t for t in range(n + 1))


order = sorted(D, key=lambda x: -P[x])
X, dec = [], []
for x in order:
    ok = realistic(X + [x])
    dec.append(ok)
    if ok:
        X.append(x)
canon = sorted(X, key=lambda x: D[x]) + sorted(set(D) - set(X))
assert order == list("abcdef") and dec == [True, True, False, True, False, True] and canon == list("badfce")
late = [x for i, x in enumerate(canon) if i + 1 > D[x]]
assert late == ["c", "e"] and sum(P[x] for x in late) == 11

S = SVG(600, 230)
S.text(20, 22, "greedy, by decreasing penalty:", anchor="start", size=13, color="var(--muted)")
for i, x in enumerate(order):
    x0 = 30 + i * 92
    col = "var(--accent)" if dec[i] else "var(--hi)"
    S.rect(x0, 38, 76, 50, rx=8, stroke=col, fill=col, fill_opacity=0.08, width=1.6)
    S.text(x0 + 38, 55, x, size=16, italic=True, font="'STIX Two Math','Latin Modern Math','Times New Roman',serif")
    S.text(x0 + 38, 76, f"P {P[x]} · D {D[x]}", size=12)
    S.text(x0 + 66, 47, "✓" if dec[i] else "✗", size=13, color=col, weight="700")
S.text(20, 122, "canonical schedule:", anchor="start", size=13, color="var(--muted)")
for d, x in enumerate(canon, start=1):
    x0 = 30 + (d - 1) * 92
    on = d <= D[x]
    col = "var(--accent)" if on else "var(--hi)"
    S.rect(x0, 138, 76, 44, rx=4, stroke=col, fill=col, fill_opacity=0.08, width=1.6, dash=None if on else "5 4")
    S.text(x0 + 38, 154, x, size=16, italic=True, font="'STIX Two Math','Latin Modern Math','Times New Roman',serif")
    S.text(x0 + 38, 172, "on time" if on else f"late, pay {P[x]}", size=12, color="currentColor")
    S.text(x0 + 38, 200, f"day {d}", size=12, color="var(--muted)")
S.line(30, 214, 30 + 6 * 92 - 16, 214, color="var(--muted)", width=1.2)
html = S.figure(
    "<strong>Scheduling six unit tasks (an original example).</strong> Top: the tasks in order of decreasing penalty "
    "<i>P</i>, with deadlines <i>D</i>; greedy keeps a task if the kept set stays realistic (|<i>X</i>(<i>t</i>)| ≤ "
    "<i>t</i> for every day <i>t</i>). It rejects <i>c</i>, because <i>a</i>, <i>b</i>, <i>c</i> all have deadline "
    "≤ 2, and <i>e</i>, because <i>b</i>, <i>e</i> both have deadline 1. Bottom: the canonical schedule runs the kept "
    "tasks by deadline, then the rest; the total penalty is 7 + 4 = 11, the minimum over all 720 schedules.",
    alt="six tasks with penalties and deadlines; greedy keeps a, b, d, f; the schedule is b, a, d, f, c, e")
save("ne-schedule", html)
