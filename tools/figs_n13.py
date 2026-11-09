#!/usr/bin/env python3
"""Figures for lecture note 13 (Adversary arguments). Writes tools/figs/n13-<name>.html; then run tools/assemble.py on
content/4-lecture-notes/13-adversary-arguments.md. Both pictures are states of the page's adversaries, produced by
running them (Hide01 with the corrected parity test; HideConnectedness) on the probe sequences named in the
captions; tools/checks/n13.py replays the same sequences."""
import itertools
import math
import os

from figlib import SVG, SERIF_IT, SANS, MONO, fmt

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")
os.makedirs(OUT, exist_ok=True)


def save(name, html):
    with open(os.path.join(OUT, name + ".html"), "w", encoding="utf-8") as f:
        f.write(html + "\n")
    print("wrote", name)


# ================================================================== 1. Hide01
class Hide01:
    def __init__(self, n):
        self.n, self.l, self.r, self.B = n, 0, n + 1, {}

    def probe(self, i):
        if i <= self.l:
            b = 1
        elif i >= self.r:
            b = 0
        elif (i - self.l) % 2 == 1:
            b, self.r = 0, i
        else:
            b, self.l = 1, i
        self.B[i] = b
        return b


A = Hide01(10)
answers = [A.probe(i) for i in (4, 9, 1, 10)]
assert answers == [1, 0, 1, 0] and (A.l, A.r) == (4, 9)
S = SVG(520, 132)
cell, x0, y0 = 40, 60, 34
for i in range(1, 11):
    x = x0 + (i - 1) * cell
    examined = i in A.B
    gap = A.l < i < A.r
    S.rect(x, y0, cell, cell, stroke="currentColor", fill="var(--accent)" if examined else "none",
           fill_opacity=0.16 if examined else None, width=1.2)
    S.text(x + cell / 2, y0 - 12, str(i), size=11.5, color="var(--muted)")
    if gap:
        S.text(x + cell / 2, y0 + cell / 2 + 1, "?", size=17, color="var(--hi)", weight="600")
    else:
        sym = str(A.B[i]) if examined else ("1" if i <= A.l else "0")
        S.text(x + cell / 2, y0 + cell / 2 + 1, sym, size=17, font=MONO,
               color="currentColor" if examined else "var(--muted)", weight="600" if examined else None)
for idx, lab in ((A.l, "ℓ"), (A.r, "r")):
    x = x0 + (idx - 1) * cell + cell / 2
    S.line(x, y0 + cell + 30, x, y0 + cell + 5, color="var(--hi)", width=1.8, arrow=True)
    S.text(x, y0 + cell + 42, f"{lab} = {idx}", size=13, color="var(--hi)", font=SANS)
S.text(x0 - 10, y0 + cell / 2, "B", size=15, font=SERIF_IT, italic=True, anchor="end")
save("n13-hide01", S.figure(
    "<strong>What the Hide01 adversary is thinking</strong> (<i>n</i> = 10, after the algorithm has probed "
    "positions 4, 9, 1, 10 and seen 1, 0, 1, 0). Shaded cells have been examined. The adversary pretends the input "
    "is 1s up to ℓ = 4 and 0s from <i>r</i> = 9 on; the 4 bits strictly between are undecided, and their number "
    "<i>r</i> − ℓ − 1 is kept even. Until every bit is probed, a 01 can still be planted (in the gap, or by turning "
    "an unexamined 1 into 0 or an unexamined 0 into 1) or avoided.",
    alt="ten cells: 1 1 1 1 ? ? ? ? 0 0, with cells 1, 4, 9, 10 shaded and pointers l = 4 and r = 9"))


# ================================================================== 2. HideConnectedness on K5
def connected(n, E):
    adj = {v: set() for v in range(1, n + 1)}
    for u, v in E:
        adj[u].add(v)
        adj[v].add(u)
    seen, bag = set(), [1]
    while bag:
        v = bag.pop()
        if v not in seen:
            seen.add(v)
            bag.extend(adj[v])
    return len(seen) == n


n = 5
E = list(itertools.combinations(range(1, n + 1), 2))
M, Y, removed = set(E), set(), []
order = E[:7]
for e in order:
    if connected(n, M - {e}):
        M.discard(e)
        removed.append(e)
    else:
        Y.add(e)
assert Y == {(1, 5), (2, 5)} and removed == [(1, 2), (1, 3), (1, 4), (2, 3), (2, 4)]
assert connected(n, M) and not connected(n, Y)
S = SVG(330, 250)
cx, cy, R = 165, 128, 92
P = {v: (cx + R * math.sin(2 * math.pi * (v - 1) / n), cy - R * math.cos(2 * math.pi * (v - 1) / n))
     for v in range(1, n + 1)}
for (u, v) in E:
    (x1, y1), (x2, y2) = P[u], P[v]
    if (u, v) in Y:
        S.line(x1, y1, x2, y2, color="var(--hi)", width=3.4)
    elif (u, v) in M:
        S.line(x1, y1, x2, y2, color="currentColor", width=1.5)
    else:
        S.line(x1, y1, x2, y2, color="var(--muted)", width=1.2, dash="4 4")
for v, (x, y) in P.items():
    S.circle(x, y, 14, stroke="currentColor", fill="var(--paper)", width=1.5)
    S.text(x, y + 1, str(v), size=15, font=SERIF_IT, italic=True)
save("n13-connectedness", S.figure(
    "<strong>HideConnectedness on five vertices</strong>, after the algorithm has asked about the edges "
    "12, 13, 14, 15, 23, 24, 25 in that order. The adversary said “no” to 12, 13, 14, 23, 24 (dashed: deleted from "
    "<i>M</i>, which stayed connected) and “yes” to 15 and 25 (thick: the graph <i>Y</i>), because deleting either "
    "would have cut vertex 1 or 2 off. Thin edges are unexamined. <i>M</i> = <i>Y</i> plus the thin edges is connected, "
    "<i>Y</i> is not, and both agree with every answer so far.",
    alt="five vertices on a pentagon; edges 15 and 25 thick, 34 35 45 thin, the other five dashed"))
