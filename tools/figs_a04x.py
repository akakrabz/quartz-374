#!/usr/bin/env python3
"""Figures for the Chapter 4 solved-exercises page (greedy algorithms). Writes tools/figs/a04x-<name>.html; then run
tools/assemble.py on content/2-algorithms/04-greedy-algorithms-exercises.md. Every highlighted interval is computed
here by the page's algorithms (and the same data are checked by tools/checks/a04x.py)."""
import math
import os
from figlib import SVG, MONO, SANS

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")
os.makedirs(OUT, exist_ok=True)


def save(name, html):
    with open(os.path.join(OUT, name + ".html"), "w", encoding="utf-8") as f:
        f.write(html + "\n")
    print("wrote", name)


def conflict(a, b):
    return not (a[0] > b[1] or b[0] > a[1])


def bar(S, x1, x2, y, h, kind="plain", label=None, size=10.5):
    """kind: plain | opt (filled accent) | hot (filled --hi) | gone (dashed --hi outline)."""
    if kind == "opt":
        S.rect(x1, y, x2 - x1, h, rx=3, stroke="var(--accent)", fill="var(--accent)", fill_opacity=0.25, width=1.6)
    elif kind == "hot":
        S.rect(x1, y, x2 - x1, h, rx=3, stroke="var(--hi)", fill="var(--hi)", fill_opacity=0.2, width=1.8)
    elif kind == "gone":
        S.rect(x1, y, x2 - x1, h, rx=3, stroke="var(--hi)", fill="none", width=1.6, dash="4 3")
    else:
        S.rect(x1, y, x2 - x1, h, rx=3, stroke="currentColor", fill="none", width=1.1)
    if label:
        col = "var(--hi)" if kind in ("hot", "gone") else "currentColor"
        S.text((x1 + x2) / 2, y + h / 2 + 0.5, label, size=size, color=col)


# =========================================================================== 1. Exercise 4.1 counterexamples
def rows_of(ivs):
    """Pack intervals into rows of pairwise disjoint ones (first fit by start time)."""
    rows = []
    for iv in sorted(ivs):
        for r in rows:
            if all(not conflict(iv, o) for o in r):
                r.append(iv)
                break
        else:
            rows.append([iv])
    return rows


PANELS = [
    # title, intervals (rows given explicitly: first row = an optimal schedule), hot interval, kind, range, verdict
    ("(a) ends last, (b) starts first", [[(1, 2), (3, 4)], [(0, 5)]], (0, 5), "hot", 5, "rule 1 · optimum 2"),
    ("(d) shortest duration", [[(0, 4), (5, 9)], [(3, 6)]], (3, 6), "hot", 9, "rule 1 · optimum 2"),
    ("(f) discard the longest", [[(0, 6), (7, 9)], [(8, 10)]], (0, 6), "gone", 10, "rule 1 · optimum 2"),
    ("(e) fewest conflicts", [[(0, 4), (6, 10), (12, 16), (18, 22)], [(2, 7), (9, 13), (14, 19)], [(3, 7), (15, 19)],
                              [(3, 8), (15, 20)]], (9, 13), "hot", 22, "rule 3 · optimum 4"),
    ("(g) discard most conflicts", [[(0, 3), (6, 14), (17, 20)], [(2, 7), (12, 19)], [(1, 8), (13, 18)]],
     (6, 14), "gone", 20, "rule 2 · optimum 3"),
]
W, COLW = 640, 300
RH, BH = 22, 16
S = SVG(W, 312, font_size=13)


def panel(x0, y0, title, rows, hot, kind, rng, verdict):
    S.text(x0, y0 + 7, title, anchor="start", size=13, weight="600")
    S.text(x0 + COLW, y0 + 7, verdict, anchor="end", size=11.5, color="var(--muted)")
    scale = (COLW - 4) / rng
    y = y0 + 20
    for r_i, row in enumerate(rows):
        for (a, b) in row:
            k = kind if (a, b) == hot else ("opt" if r_i == 0 else "plain")
            bar(S, x0 + 2 + a * scale, x0 + 2 + b * scale, y, BH, kind=k, label=f"[{a},{b}]")
        y += RH
    # axis
    S.line(x0 + 2, y + 1, x0 + 2 + rng * scale, y + 1, width=0.9, color="var(--muted)")
    for t in range(rng + 1):
        S.line(x0 + 2 + t * scale, y + 1, x0 + 2 + t * scale, y + 4, width=0.9, color="var(--muted)")
    return y + 22


y = 6
for p in PANELS[:3]:
    y = panel(10, y, *p)
yl = y
y = 6
for p in PANELS[3:]:
    y = panel(330, y, *p)
S.h = max(yl, y) - 6
# sanity: the first row of each panel is pairwise disjoint, and every hot interval exists
for _, rows, hot, _, _, _ in PANELS:
    assert all(not conflict(a, b) for i, a in enumerate(rows[0]) for b in rows[0][i + 1:])
    assert any(hot in r for r in rows)
save("a04x-ex1", S.figure(
    "<strong>Counterexamples for Exercise 4.1.</strong> Classes are closed intervals [start, finish]; the top row of "
    "each panel (filled) is a largest schedule. Red marks the rule's first move: the class it <em>chooses</em> in (a), "
    "(b), (d), (e), or the class it <em>discards</em> (dashed) in (f), (g). After that move every run of the rule, "
    "however ties are broken, ends with fewer classes than the optimum.",
    alt="five small sets of intervals, each with an optimal schedule and the first move of a wrong greedy rule"))

# =========================================================================== 2. Exercise 4.3 the book's cover figure
# 16 intervals measured from the book's figure (p. 178) at 300 dpi; units = pixels x 2; listed row by row.
COVER_ROWS = [[(117, 605), (867, 1317), (1355, 1842), (1917, 2049)],
              [(192, 529), (679, 1129), (1485, 1879)],
              [(361, 1185), (1242, 1692), (1955, 2142)],
              [(285, 585), (961, 1335), (1561, 2011)],
              [(249, 849), (923, 1073), (1411, 2085)]]


def smallest_cover(ivs):
    iv = sorted(ivs)
    n = len(iv)
    reach, i, chosen = -math.inf, 0, []
    while i < n:
        if iv[i][1] <= reach:
            i += 1
            continue
        t = max(reach, iv[i][0])
        best = iv[i]
        while i < n and iv[i][0] <= t:
            if iv[i][1] > best[1]:
                best = iv[i]
            i += 1
        chosen.append(best)
        reach = best[1]
    return chosen


ALL = [iv for r in COVER_ROWS for iv in r]
picks = smallest_cover(ALL)
assert len(picks) == 6
U0, U1 = 117, 2142
X0, XW = 14, 612


def sx(u):
    return X0 + (u - U0) * XW / (U1 - U0)


S = SVG(640, 5 * 26 + 44, font_size=13)
for r_i, row in enumerate(COVER_ROWS):
    yy = 8 + r_i * 26
    for iv in row:
        if iv in picks:
            bar(S, sx(iv[0]), sx(iv[1]), yy, 18, kind="opt", label=str(picks.index(iv) + 1), size=12)
        else:
            bar(S, sx(iv[0]), sx(iv[1]), yy, 18)
yb = 8 + 5 * 26 + 4
S.line(sx(U0), yb, sx(U1), yb, width=2.2, color="var(--accent)")
S.text(sx(U0), yb + 14, "union: one interval", anchor="start", size=11.5, color="var(--muted)")
reaches = [p[1] for p in picks]
for k, r in enumerate(reaches):
    S.line(sx(r), yb - 3, sx(r), yb + 3, width=1.4, color="var(--accent)")
save("a04x-cover", S.figure(
    "<strong>SmallestCover on the book's example (Exercise 4.3).</strong> The 16 intervals of the book's figure, in "
    "the same rows. Sweeping left to right, the algorithm takes the filled intervals in the order numbered: each one "
    "starts inside the part already covered and reaches farthest to the right (ticks on the axis). Six intervals "
    "suffice; the cover shaded in the book has seven, so it is not a smallest one.",
    alt="sixteen intervals in five rows; six of them, numbered 1 to 6, form a cover of the union"))

# =========================================================================== 3. Exercises 4.4-4.5 stabbing
STAB_ROWS = [[(117, 605), (867, 1279), (1355, 1842), (1899, 2049)],
             [(192, 529), (679, 1167), (1485, 1861)],
             [(361, 1185), (1279, 1692), (1955, 2141)],
             [(285, 585), (961, 1335), (1561, 2011)],
             [(249, 849), (923, 1073), (1411, 2085)]]
ALL = [iv for r in STAB_ROWS for iv in r]
pts, trig, p = [], [], -math.inf
for L, R in sorted(ALL, key=lambda t: t[1]):
    if L > p:
        p = R
        pts.append(R)
        trig.append((L, R))
assert pts == [529, 1073, 1692, 2049]
assert all(not conflict(a, b) for i, a in enumerate(trig) for b in trig[i + 1:])
assert sum(L <= pts[0] <= R for L, R in ALL) == 5
S = SVG(640, 5 * 26 + 48, font_size=13)
for k, x in enumerate(pts):
    S.line(sx(x), 2, sx(x), 8 + 5 * 26 + 2, width=2.2, color="var(--hi)")
    S.text(sx(x), 8 + 5 * 26 + 16, f"p{k + 1}", size=12.5, color="var(--hi)", weight="600")
for r_i, row in enumerate(STAB_ROWS):
    yy = 8 + r_i * 26
    for iv in row:
        bar(S, sx(iv[0]), sx(iv[1]), yy, 18, kind="opt" if iv in trig else "plain")
S.text(sx(pts[0]) + 8, 8 + 5 * 26 + 30, "p1 lies in 5 intervals", anchor="start", size=11.5, color="var(--muted)")
save("a04x-stab", S.figure(
    "<strong>StabIntervals on the book's example (Exercise 4.4).</strong> Scanning by right endpoint, each point "
    "p<sub>k</sub> is the right end of the first interval not yet stabbed (filled). The four filled intervals are "
    "pairwise disjoint, so no three points can stab them all: four is optimal. The point p<sub>1</sub> lies in five "
    "intervals, so the book's five-color coloring in Exercise 4.5 is optimal too.",
    alt="sixteen intervals in five rows, four vertical lines through them at the greedy points"))

# =========================================================================== 4. Exercise 4.6 deepest Huffman tree
from figlib import Tree  # noqa: E402

freqs = [1, 1, 1, 3, 4, 7]
node = (str(freqs[0]), [])
tot = freqs[0]
merged = []
node = ("2", [("1", []), ("1", [])])
tot = 2
for f in freqs[2:]:
    tot += f
    merged.append(tot)
    node = (str(tot), [node, (str(f), [])])
assert merged == [3, 6, 10, 17]
T = Tree(300, 236, font_size=14)
T.draw(node, 14, 22, level_h=40, leaf_w=44, circle_internal=True)
T.text(296, 22, "depth 5", anchor="end", size=12, color="var(--muted)")
save("a04x-huffman", T.figure(
    "<strong>The deepest Huffman tree with the smallest frequencies, n = 6.</strong> Leaves 1, 1, 1, 3, 4, 7; each "
    "internal node shows its weight. Every subtree weighs less than the leaf two places further in sorted order "
    "(2 &lt; 3, 3 &lt; 4, 6 &lt; 7), so no tie-breaking lets Huffman merge two leaves instead, and every Huffman "
    "tree is this caterpillar of depth n &minus; 1 = 5.",
    alt="a caterpillar binary tree with leaves 1,1,1,3,4,7 and internal weights 2,3,6,10,17"))
