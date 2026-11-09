#!/usr/bin/env python3
"""Figures for Erickson's note J (Approximation Algorithms). Writes tools/figs/nj-<name>.html; then run
tools/assemble.py on content/4-lecture-notes/j-approximation-algorithms.md. Everything drawn is computed here by
running the page's algorithms (GreedyLoadBalance, GreedySetCover, MST + depth-first shortcutting, Christofides with a
brute-force minimum matching, GonzalezKCenter); tools/checks/nj.py recomputes the same numbers and compares them with
the captions on the page."""
import itertools
import math
import os
import random

from figlib import SVG, SERIF_IT, SANS, esc

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")
os.makedirs(OUT, exist_ok=True)


def save(name, svg, caption, alt):
    html = svg.figure(caption, alt=alt)
    with open(os.path.join(OUT, name + ".html"), "w", encoding="utf-8") as f:
        f.write(html + "\n")
    print("wrote", name)


def it(s):
    return f"<i>{esc(s)}</i>"


# ============================================================================ load balancing
def greedy(T, m):
    Tot = [0] * m
    A = []
    for t in T:
        i = Tot.index(min(Tot))
        A.append(i)
        Tot[i] += t
    return A, Tot


T_LB = [2, 3, 4, 1, 1, 6, 1]
M_LB = 3
OPT_LB = 6


def lb_panel(S, x0, y0, T, A, title, unit=19, colw=46, gap=18, mark=True):
    m = M_LB
    base = y0
    w = m * colw + (m - 1) * gap
    final = [sum(T[q] for q in range(len(T)) if A[q] == i) for i in range(m)]
    yo = base - OPT_LB * unit
    S.line(x0 - 14, yo, x0 + w + 8, yo, color="var(--accent2)", width=1.3, dash="5 4")
    S.text(x0 + w + 12, yo, "OPT = avg = 6", size=12, anchor="start", color="var(--accent2)")
    mk = max(final)
    if mk > OPT_LB:
        ym = base - mk * unit
        S.line(x0 - 14, ym, x0 + w + 8, ym, color="var(--hi)", width=1.3, dash="2 3")
        S.text(x0 + w + 12, ym, f"makespan {mk}", size=12, anchor="start", color="var(--hi)")
    loads = [0] * m
    for j, (t, i) in enumerate(zip(T, A)):
        x = x0 + i * (colw + gap)
        top = base - (loads[i] + t) * unit
        last = mark and j == max(jj for jj in range(len(T)) if A[jj] == i) and i == max(range(m), key=lambda k: sum(
            T[q] for q in range(len(T)) if A[q] == k))
        S.rect(x, top, colw, t * unit, rx=4, stroke="none", fill="var(--paper)", width=0)
        S.rect(x, top, colw, t * unit, rx=4, stroke="var(--hi)" if last else "currentColor",
               fill="var(--hi)" if last else "var(--accent)", fill_opacity=0.25 if last else 0.12, width=2 if last else 1.2)
        S.text(x + colw / 2, top + t * unit / 2 + (unit if t == 6 else 0), f"{t}", size=12.5 if t > 1 else 11.5)
        S.text(x - 3, top + t * unit / 2 + (unit if t == 6 else 0), f"{j + 1}", size=9.5, anchor="end", color="var(--muted)")
        loads[i] += t
    S.line(x0 - 14, base, x0 + w + 8, base, width=1.4)
    for i in range(m):
        S.text(x0 + i * (colw + gap) + colw / 2, base + 13, f"M{i + 1}", size=12.5)
    S.text(x0 + w / 2, y0 - 9.6 * unit - 8, title, size=13.5, weight=600)


S = SVG(640, 250)
A1, Tot1 = greedy(T_LB, M_LB)
srt = sorted(T_LB, reverse=True)
A2, Tot2 = greedy(srt, M_LB)
lb_panel(S, 40, 215, T_LB, A1, "GreedyLoadBalance (input order)")
lb_panel(S, 365, 215, srt, A2, "SortedGreedyLoadBalance", mark=False)
assert max(Tot1) == 9 and max(Tot2) == 6 and sum(T_LB) == 18
save("nj-load-balance", S,
     "<strong>Greedy load balancing on three machines.</strong> The jobs 2, 3, 4, 1, 1, 6, 1 (small numbers: the "
     "order of assignment) go one by one to the least-loaded machine (lowest index on ties). In input order the "
     "busiest machine M2 reaches 9: its last job <i>j</i> (length 6, highlighted) is at most OPT, and the load "
     "under it, 3, was the smallest load when <i>j</i> arrived, so it is at most the average 18/3 = 6 ≤ OPT — "
     "the two halves of the proof of Theorem J.1. Sorted in decreasing order the same jobs give makespan 6, "
     "which is optimal.",
     alt="two stacked bar charts of three machines; greedy makespan 9, sorted greedy makespan 6, optimum 6")


# ============================================================================ set cover
K_SC = 4


def gsc(X, Fam):
    X = set(X)
    C = []
    while X:
        s = max(range(len(Fam)), key=lambda i: (len(Fam[i] & X), -i))
        C.append((s, len(Fam[s] & X)))
        X -= Fam[s]
    return C


blocks, nxt = [], 0
for i in range(1, K_SC + 1):
    blocks.append(list(range(nxt, nxt + 2 ** i)))
    nxt += 2 ** i
top = {e for B in blocks for e in B[: len(B) // 2]}
bot = {e for B in blocks for e in B[len(B) // 2:]}
Fam = [top, bot] + [set(B) for B in blocks]
steps = gsc(set(range(nxt)), Fam)
assert [s for s, _ in steps] == [5, 4, 3, 2] and [c for _, c in steps] == [16, 8, 4, 2]

S = SVG(640, 205)
cw, x0, y_top, y_bot = 30, 52, 74, 112
xpos = {}
col = 0
gx = x0
for bi, B in enumerate(blocks):
    half = len(B) // 2
    bx0 = gx
    for k in range(half):
        xpos[B[k]] = (gx + k * cw, y_top)
        xpos[B[half + k]] = (gx + k * cw, y_bot)
    bx1 = gx + (half - 1) * cw
    step = [s for s, _ in steps].index(2 + bi) + 1
    S.rect(bx0 - 13, y_top - 22, bx1 - bx0 + 26, y_bot - y_top + 44, rx=10, stroke="var(--hi)", fill="var(--hi)",
           fill_opacity=0.06, width=1.6)
    S.text((bx0 + bx1) / 2, y_bot + 36, f"C{bi + 1}: {len(B)}", size=12.5, color="var(--hi)")
    S.text((bx0 + bx1) / 2, y_top - 36, f"step {step}", size=12, color="var(--hi)", weight=600)
    gx = bx1 + cw + 16
xr = gx - cw - 16
for y, lab in ((y_top, "R1"), (y_bot, "R2")):
    S.rect(x0 - 20, y - 12, xr - x0 + 40, 24, rx=12, stroke="var(--accent2)", width=1.4, dash="5 4")
    S.text(x0 - 30, y, lab, size=12.5, anchor="end", color="var(--accent2)")
for e, (x, y) in xpos.items():
    S.circle(x, y, 5.5, stroke="currentColor", fill="var(--paper)", width=1.3)
S.text(320, 192, "greedy: C4, C3, C2, C1 (new elements 16, 8, 4, 2; a row would give 15, 7, 3, 1)  ·  optimum: R1, R2",
       size=12.5)
save("nj-setcover", S,
     "<strong>Greedy set cover is not an O(log |<i>F</i>|)-approximation.</strong> Thirty elements in blocks of "
     "2, 4, 8, 16, each split between two rows. The family has |<i>F</i>| = 6 sets: the two rows R1, R2 (15 elements "
     "each) and the four blocks C1–C4. Greedy takes C4 first (16 new elements, one more than a row), then C3, C2, "
     "C1 — four sets — while the two rows cover everything. With <i>k</i> blocks greedy takes <i>k</i> sets against "
     "2, a ratio of <i>k</i>/2 with only <i>k</i> + 2 sets; it is the ground set, of size 2<sup><i>k</i>+1</sup> − 2, "
     "that the ratio is logarithmic in.",
     alt="thirty dots in two rows, grouped into four blocks; greedy picks the four blocks, the two rows suffice")


# ============================================================================ metric TSP instance (the note's tree)
NAMES = ["c", "L", "R", "B", "UR", "T", "TL"]
PTS = {"TL": (0, 0), "T": (3, 0), "c": (5, 3), "L": (1, 8), "B": (8, 10), "UR": (11, 4), "R": (8, 4)}
LAB = {"c": "a", "L": "b", "R": "c", "B": "d", "UR": "e", "T": "f", "TL": "g"}  # names on the page
TREE = [("TL", "T"), ("T", "c"), ("c", "L"), ("c", "R"), ("R", "UR"), ("R", "B")]
MATCH = [("TL", "c"), ("L", "B"), ("UR", "R")]
D = {(a, b): math.dist(PTS[a], PTS[b]) for a in NAMES for b in NAMES}


def tl(t):
    return sum(D[t[i], t[(i + 1) % len(t)]] for i in range(len(t)))


DT_WALK = ["c", "L", "c", "R", "B", "R", "UR", "R", "c", "T", "TL", "T", "c"]
DT_TOUR = ["c", "L", "R", "B", "UR", "T", "TL"]
CH_CIRC = ["c", "L", "B", "R", "UR", "R", "c", "TL", "T", "c"]
CH_TOUR = ["c", "L", "B", "R", "UR", "TL", "T"]
OPT_TOUR = min((["c"] + list(p) for p in itertools.permutations(NAMES[1:])), key=tl)
mst = sum(D[a, b] for a, b in TREE)
mom = sum(D[a, b] for a, b in MATCH)
assert sorted(sorted(DT_WALK[i:i + 2]) for i in range(12)) == sorted(sorted(e) for e in TREE + TREE)


def word(seq):
    return " ".join(LAB[v] for v in seq)


def place(ox, oy, sc=15.5):
    return {v: (ox + x * sc, oy + y * sc) for v, (x, y) in PTS.items()}


def draw_vertices(S, P, odd=(), r=10.5):
    for v in NAMES:
        x, y = P[v]
        if v in odd:
            S.circle(x, y, r, stroke="currentColor", fill="var(--accent)", fill_opacity=0.35, width=1.5)
        else:
            S.circle(x, y, r, stroke="currentColor", fill="var(--paper)", width=1.5)
        S.text(x, y + 0.5, LAB[v], size=14, font=SERIF_IT, italic=True)


def seg(S, P, a, b, r=10.5, off=0.0, **kw):
    (x1, y1), (x2, y2) = P[a], P[b]
    L = math.dist((x1, y1), (x2, y2))
    ux, uy = (x2 - x1) / L, (y2 - y1) / L
    nx_, ny_ = -uy * off, ux * off
    S.line(x1 + ux * r + nx_, y1 + uy * r + ny_, x2 - ux * (r + 1.5) + nx_, y2 - uy * (r + 1.5) + ny_, **kw)


def curve(S, P, a, b, bend, r=10.5, **kw):
    (x1, y1), (x2, y2) = P[a], P[b]
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    L = math.dist((x1, y1), (x2, y2))
    nx_, ny_ = -(y2 - y1) / L, (x2 - x1) / L
    cx, cy = mx + nx_ * bend, my + ny_ * bend

    def trim(px, py, qx, qy, extra=0.0):
        d = math.dist((px, py), (qx, qy))
        return px + (qx - px) / d * (r + extra), py + (qy - py) / d * (r + extra)
    sx, sy = trim(x1, y1, cx, cy)
    ex, ey = trim(x2, y2, cx, cy, 1.5)
    S.path(f"M{sx:.1f},{sy:.1f} Q{cx:.1f},{cy:.1f} {ex:.1f},{ey:.1f}", **kw)


def in_graph(a, b, E):
    return (a, b) in E or (b, a) in E


W3, H3 = 640, 238
OX = [26 + 212 * k for k in range(3)]


def frame(titles):
    S = SVG(W3, H3)
    for k in range(3):
        S.text(OX[k] + 85, 14, titles[k], size=13, weight=600)
    return S, [place(OX[k], 34) for k in range(3)]


S, pan = frame(["minimum spanning tree T", "walk around T (each edge twice)", "shortcut tour"])
for a, b in TREE:
    seg(S, pan[0], a, b, width=2.2)
draw_vertices(S, pan[0])
for i in range(len(DT_WALK) - 1):
    seg(S, pan[1], DT_WALK[i], DT_WALK[i + 1], off=4, width=1.4, arrow=True)
draw_vertices(S, pan[1])
for i in range(7):
    a, b = DT_TOUR[i], DT_TOUR[(i + 1) % 7]
    t = in_graph(a, b, TREE)
    seg(S, pan[2], a, b, color="currentColor" if t else "var(--hi)", width=1.6 if t else 2.4, arrow=True)
draw_vertices(S, pan[2])
S.text(W3 / 2, H3 - 10,
       f"MST {mst:.2f}   ·   walk 2·MST = {2 * mst:.2f}   ·   tour {tl(DT_TOUR):.2f}   ·   optimal tour {tl(OPT_TOUR):.2f}",
       size=12.5)
short_dt = sum(1 for i in range(7) if not in_graph(DT_TOUR[i], DT_TOUR[(i + 1) % 7], TREE))
save("nj-tsp-double", S,
     "<strong>Tree doubling on seven points in the plane (the note’s tree, given coordinates).</strong> Left: the "
     "minimum spanning tree. Middle: the depth-first walk from <i>a</i> (children in alphabetical order), "
     f"<i>{word(DT_WALK)}</i>, uses every tree edge twice; the vertices are named in preorder. Right: visiting the "
     f"vertices in preorder, <i>{word(DT_TOUR)} {LAB[DT_TOUR[0]]}</i>, skips the repeats; the {short_dt} shortcuts "
     "(thick) are no longer than the parts of the walk they replace, by the triangle inequality. The tour is "
     f"{tl(DT_TOUR) / tl(OPT_TOUR):.2f} times the optimum, within the guaranteed factor 2.",
     alt="three panels: a seven-vertex spanning tree, the walk around it, and the shortcut tour")

deg = {v: sum(v in e for e in TREE) for v in NAMES}
odd = [v for v in NAMES if deg[v] % 2]
S, pan = frame(["T and matching M of odd vertices", "Euler circuit of T ∪ M", "shortcut tour"])
for a, b in TREE:
    if (a, b) == ("R", "UR"):
        curve(S, pan[0], a, b, -7, width=2.2)
    else:
        seg(S, pan[0], a, b, width=2.2)
for a, b in MATCH:
    if (a, b) == ("UR", "R"):
        curve(S, pan[0], a, b, -7, color="var(--hi)", width=2.4, dash="6 4")
    else:
        seg(S, pan[0], a, b, color="var(--hi)", width=2.4, dash="6 4")
draw_vertices(S, pan[0], odd=odd)
used_tree_ru = False
for i in range(len(CH_CIRC) - 1):
    a, b = CH_CIRC[i], CH_CIRC[i + 1]
    ism = in_graph(a, b, MATCH) and not (in_graph(a, b, TREE) and not used_tree_ru)
    if in_graph(a, b, [("R", "UR")]):
        # the doubled edge: first traversal along the tree copy, second along the matching copy
        if not used_tree_ru:
            curve(S, pan[1], "R", "UR", -7, width=1.5, arrow=(a, b) == ("R", "UR"))
            if (a, b) != ("R", "UR"):
                curve(S, pan[1], "UR", "R", 7, width=1.5, arrow=True)
            used_tree_ru = True
        else:
            curve(S, pan[1], a, b, -7, color="var(--hi)", width=1.5, dash="6 4", arrow=True)
        continue
    seg(S, pan[1], a, b, color="var(--hi)" if in_graph(a, b, MATCH) else "currentColor", width=1.5,
        dash="6 4" if in_graph(a, b, MATCH) else None, arrow=True)
draw_vertices(S, pan[1])
for i in range(7):
    a, b = CH_TOUR[i], CH_TOUR[(i + 1) % 7]
    t = in_graph(a, b, TREE + MATCH)
    seg(S, pan[2], a, b, color="currentColor" if t else "var(--hi)", width=1.6 if t else 2.4, arrow=True)
draw_vertices(S, pan[2])
S.text(W3 / 2, H3 - 10,
       f"MST {mst:.2f} + matching {mom:.2f} = {mst + mom:.2f}   ·   tour {tl(CH_TOUR):.2f}   ·   optimal tour {tl(OPT_TOUR):.2f}",
       size=12.5)
short_ch = sum(1 for i in range(7) if not in_graph(CH_TOUR[i], CH_TOUR[(i + 1) % 7], TREE + MATCH))
save("nj-christofides", S,
     "<strong>Christofides on the same seven points.</strong> Left: the tree has six odd-degree vertices "
     "(shaded); the minimum-cost perfect matching on them, "
     + ", ".join(f"<i>{''.join(sorted(LAB[x] + LAB[y]))}</i>" for x, y in MATCH)
     + " (dashed), doubles the tree edge <i>ce</i>. Middle: every degree of <i>T</i> ∪ <i>M</i> is even, and an "
     f"Euler circuit is <i>{word(CH_CIRC)}</i>. Right: skipping repeated vertices gives the tour "
     f"<i>{word(CH_TOUR)} {LAB[CH_TOUR[0]]}</i> ({short_ch} shortcut, thick). Its length {tl(CH_TOUR):.2f} is at "
     f"most MST + matching = {mst + mom:.2f}, and only {tl(CH_TOUR) / tl(OPT_TOUR):.2f} times the optimum "
     f"{tl(OPT_TOUR):.2f} (tree doubling gave {tl(DT_TOUR):.2f}).",
     alt="three panels: the tree with a matching of its odd vertices, an Euler circuit, and the tour")


# ============================================================================ k-center
def gonzalez(P, k):
    n = len(P)
    d = [float("inf")] * n
    c = [0]
    r = []
    for j in range(k):
        rj, nxt = 0, None
        for i in range(n):
            d[i] = min(d[i], math.dist(P[i], P[c[j]]))
            if rj < d[i]:
                rj, nxt = d[i], i
        r.append(rj)
        c.append(nxt)
    return c, r


def mec(pts):
    """Minimum enclosing circle (radius, center), brute force over pairs and triples."""
    if len(pts) == 1:
        return 0.0, pts[0]
    cands = [((p[0] + q[0]) / 2, (p[1] + q[1]) / 2) for p, q in itertools.combinations(pts, 2)]
    for A, B, C in itertools.combinations(pts, 3):
        dd = 2 * (A[0] * (B[1] - C[1]) + B[0] * (C[1] - A[1]) + C[0] * (A[1] - B[1]))
        if abs(dd) > 1e-12:
            ux = ((A[0] ** 2 + A[1] ** 2) * (B[1] - C[1]) + (B[0] ** 2 + B[1] ** 2) * (C[1] - A[1]) + (C[0] ** 2 + C[1] ** 2) * (A[1] - B[1])) / dd
            uy = ((A[0] ** 2 + A[1] ** 2) * (C[0] - B[0]) + (B[0] ** 2 + B[1] ** 2) * (A[0] - C[0]) + (C[0] ** 2 + C[1] ** 2) * (B[0] - A[0])) / dd
            cands.append((ux, uy))
    return min((max(math.dist(cc, q) for q in pts), cc) for cc in cands)


KC_PTS = [(1, 2), (2, 1), (3, 3), (1, 4), (11, 2), (12, 4), (10, 4), (13, 2), (6, 10), (7, 12), (5, 11), (8, 11)]
KC_K = 3
c, r = gonzalez(KC_PTS, KC_K)
CLUSTERS = [KC_PTS[0:4], KC_PTS[4:8], KC_PTS[8:12]]  # the optimal clustering (verified in tools/checks/nj.py)
OPT_KC = [mec(C) for C in CLUSTERS]
opt_r = max(rad for rad, _ in OPT_KC)
S = SVG(640, 300)
sc = 13.5


def pp(p, ox):
    return ox + p[0] * sc, 60 + p[1] * sc


def lab(S, x, y, text, color="currentColor", others=()):
    # put the label where it is farthest from the other points
    best = max(((dx, dy) for dx in (-15, 15) for dy in (-13, 13)),
               key=lambda o: min([math.dist((x + o[0], y + o[1]), q) for q in others] + [99]))
    S.text(x + best[0], y + best[1], text, size=12.5, weight=600, color=color, halo=True)


for panel, ox in ((0, 62), (1, 382)):
    S.text(ox + 6.5 * sc, 12, ["Gonzalez: 3 centers, radius r3", "optimal: radius OPT"][panel], size=13, weight=600)
    allp = [pp(q, ox) for q in KC_PTS]
    if panel == 0:
        for j in range(KC_K):
            x, y = pp(KC_PTS[c[j]], ox)
            S.circle(x, y, r[-1] * sc, stroke="var(--accent)", fill="var(--accent)", fill_opacity=0.07, width=1.2)
    else:
        for rad, cc in OPT_KC:
            x, y = pp(cc, ox)
            S.circle(x, y, rad * sc, stroke="var(--accent2)", fill="var(--accent2)", fill_opacity=0.08, width=1.2)
            S.circle(x, y, 2.2, stroke="var(--accent2)", fill="var(--accent2)", width=1)
    for i, q in enumerate(KC_PTS):
        x, y = pp(q, ox)
        if panel == 0 and i in c[:KC_K]:
            S.circle(x, y, 5.5, stroke="currentColor", fill="var(--accent)", width=1.4)
            lab(S, x, y, f"c{c.index(i) + 1}", others=[t for t in allp if t != (x, y)])
        elif panel == 0 and i == c[KC_K]:
            S.circle(x, y, 5.5, stroke="var(--hi)", fill="var(--hi)", width=1.4, fill_opacity=0.5)
            lab(S, x, y, f"c{KC_K + 1}", color="var(--hi)", others=[t for t in allp if t != (x, y)])
        else:
            S.circle(x, y, 3.6, stroke="currentColor", fill="var(--paper)", width=1.3)
    if panel == 0:
        q = KC_PTS[c[KC_K]]
        near = min(range(KC_K), key=lambda j: math.dist(q, KC_PTS[c[j]]))
        a_, b_ = pp(q, ox), pp(KC_PTS[c[near]], ox)
        S.line(a_[0], a_[1], b_[0], b_[1], color="var(--hi)", width=1.8, dash="4 3")
S.text(62 + 6.5 * sc, 290, f"r3 = {r[-1]:.2f}", size=12.5, color="var(--hi)")
S.text(382 + 6.5 * sc, 290, f"OPT = {opt_r:.2f}", size=12.5, color="var(--accent2)")
save("nj-k-center", S,
     "<strong>GonzalezKCenter with <i>k</i> = 3 on twelve points.</strong> Left: the first center "
     "<i>c</i><sub>1</sub> is the first input point; each next center is the point farthest from the centers chosen "
     "so far (<i>c</i><sub>2</sub>, then <i>c</i><sub>3</sub>). After three centers the farthest point, "
     f"<i>c</i><sub>4</sub>, is at distance <i>r</i><sub>3</sub> = {r[-1]:.2f} from its nearest center (dashed), "
     "and disks of that radius around <i>c</i><sub>1</sub>, <i>c</i><sub>2</sub>, <i>c</i><sub>3</sub> cover every "
     "point. Right: the optimal three disks have radius "
     f"{opt_r:.2f} = √13/2, so here <i>r</i><sub>3</sub> = 2·OPT exactly: <i>c</i><sub>2</sub> and "
     "<i>c</i><sub>4</sub> are both in the right-hand cluster, at opposite ends of the diameter of its disk.",
     alt="two panels of twelve points in three clusters: Gonzalez's centers with disks of radius 3.61, and the optimal disks of radius 1.80")
print("k-center centers", [KC_PTS[i] for i in c], "radii", [round(x, 3) for x in r])
print("tsp: mst %.3f mom %.3f dt %.3f ch %.3f opt %.3f" % (mst, mom, tl(DT_TOUR), tl(CH_TOUR), tl(OPT_TOUR)), OPT_TOUR)
