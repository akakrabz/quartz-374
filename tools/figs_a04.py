#!/usr/bin/env python3
"""Figures for Algorithms Chapter 4 (greedy algorithms). Writes tools/figs/a04-<name>.html; then run
tools/assemble.py on the chapter page. Every drawn fact is computed here (greedy picks, tree weights,
the Gale-Shapley run) and re-checked by tools/checks/a04.py."""
import os
from figlib import SVG, MONO, SERIF_IT, SANS

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")
os.makedirs(OUT, exist_ok=True)


def save(name, html):
    with open(os.path.join(OUT, name + ".html"), "w", encoding="utf-8") as f:
        f.write(html + "\n")
    print("wrote", name)


# ============================================================ 1. scheduling classes
CLASSES = [("a", 1, 3), ("b", 0, 8), ("c", 7, 9), ("d", 6, 11), ("e", 4, 13),
           ("f", 14, 16), ("g", 10, 17), ("h", 15, 18), ("i", 19, 24)]


def greedy_schedule(cls):
    order = sorted(cls, key=lambda c: c[2])
    X = [order[0]]
    for c in order[1:]:
        if c[1] > X[-1][2]:
            X.append(c)
    return X


picks = greedy_schedule(CLASSES)
assert [c[0] for c in picks] == ["a", "c", "f", "i"]
S = SVG(600, 262)
U, X0, Y0, RH, BH = 22, 46, 14, 22, 13      # unit px, origin, row height, bar height
rows = sorted(CLASSES, key=lambda c: c[2])
chosen = {c[0] for c in picks}
for k, (name, s, f) in enumerate(rows):
    y = Y0 + k * RH
    on = name in chosen
    S.text(X0 - 22, y + BH / 2, name, size=14, font=SERIF_IT, italic=True,
           color="currentColor" if on else "var(--muted)")
    if on:
        S.rect(X0 + s * U, y, (f - s) * U, BH, rx=3, stroke="var(--accent)", fill="var(--accent)",
               fill_opacity=0.25, width=1.6)
    else:
        S.rect(X0 + s * U, y, (f - s) * U, BH, rx=3, stroke="currentColor", fill="none", width=1.1)
# dashed cut lines: from a pick down to the next pick's row
ridx = {c[0]: k for k, c in enumerate(rows)}
for p, q in zip(picks, picks[1:]):
    x = X0 + p[2] * U
    S.line(x, Y0 + ridx[p[0]] * RH - 3, x, Y0 + ridx[q[0]] * RH + BH + 3, color="var(--hi)", width=1.3, dash="4 3")
# axis
ya = Y0 + len(rows) * RH + 8
S.line(X0, ya, X0 + 24 * U, ya, width=1.1)
for t in range(0, 25, 2):
    S.line(X0 + t * U, ya, X0 + t * U, ya + 4, width=1.1)
    S.text(X0 + t * U, ya + 14, str(t), size=11, color="var(--muted)")
S.text(X0 + 24 * U + 4, ya + 30, "time", size=12, anchor="end", color="var(--muted)")
save("a04-schedule", S.figure(
    "<strong>GreedySchedule on nine classes, sorted by finish time.</strong> Scanning top to bottom, the "
    "algorithm takes a class (filled) whenever it starts strictly after the last class taken finishes; the "
    "dashed line marks that finish time, and every class that starts at or before it is skipped. Result: "
    "<i>a</i>, <i>c</i>, <i>f</i>, <i>i</i> — four classes, the maximum. Another maximum schedule is "
    "<i>a</i>, <i>d</i>, <i>h</i>, <i>i</i>.",
    alt="nine classes drawn as bars on a time axis from 0 to 24; the greedy picks a, c, f, i are filled"))


# ============================================================ 2. the book's Huffman tree for Sallows' sentence
def L(ch, w):
    return (w, ch, [])


def N(a, b):
    return (a[0] + b[0], None, [a, b])


six_ac = N(L("A", 3), L("C", 3))
six_g = N(L("G", 3), N(L("D", 2), L("Z", 1)))
n12 = N(six_ac, six_g)
n25 = N(n12, L("I", 13))
n47 = N(L("T", 22), n25)
n53 = N(L("E", 26), L("S", 27))
n100 = N(n47, n53)
n8 = N(L("X", 4), N(L("L", 2), L("U", 2)))
n17 = N(n8, L("O", 9))
n21 = N(N(L("F", 5), L("V", 5)), N(L("Y", 5), L("R", 6)))
n38 = N(n17, n21)
n32 = N(L("N", 16), N(L("H", 8), L("W", 8)))
n70 = N(n38, n32)
ROOT = N(n70, n100)
assert ROOT[0] == 170


def leaves(t, d=0):
    w, ch, kids = t
    return [(ch, w, d)] if not kids else [x for k in kids for x in leaves(k, d + 1)]


def internal_sum(t):
    w, ch, kids = t
    return 0 if not kids else w + sum(internal_sum(k) for k in kids)


LV = leaves(ROOT)
assert len(LV) == 20 and sum(w * d for _, w, d in LV) == 649 == internal_sum(ROOT)
T = SVG(640, 336, font_size=12)
SLOT, LX0, LY0, LH = 30, 20, 20, 39
pos = {}


def place(t, left, depth):
    w, ch, kids = t
    if not kids:
        pos[id(t)] = (left + SLOT / 2, LY0 + depth * LH)
        return left + SLOT / 2, left + SLOT
    xs, cur = [], left
    for k in kids:
        kx, cur = place(k, cur, depth + 1)
        xs.append(kx)
    pos[id(t)] = ((xs[0] + xs[-1]) / 2, LY0 + depth * LH)
    return pos[id(t)][0], cur


place(ROOT, LX0, 0)
PATH_A = [ROOT, n100, n47, n25, n12, six_ac, six_ac[2][0]]
on_path = {(id(a), id(b)) for a, b in zip(PATH_A, PATH_A[1:])}
R_INT, LW, LHT = 11, 22, 30


def draw_edges(t):
    w, ch, kids = t
    px, py = pos[id(t)]
    for j, k in enumerate(kids):
        kx, ky = pos[id(k)]
        hi = (id(t), id(k)) in on_path
        top = ky - (LHT / 2 if not k[2] else R_INT)
        T.line(px, py + R_INT, kx, top, width=1.8 if hi else 1.1,
               color="var(--accent)" if hi else "currentColor", opacity=None if hi else 0.55)
        if hi or t is ROOT:
            mx, my = (px + kx) / 2, (py + R_INT + top) / 2
            T.text(mx + (-9 if j == 0 else 9), my - 4, str(j), size=11, font=MONO, weight=600 if hi else None,
                   color="var(--accent)" if hi else "var(--muted)", halo=True)
        draw_edges(k)


draw_edges(ROOT)
def draw_nodes(t):
    w, ch, kids = t
    x, y = pos[id(t)]
    if kids:
        T.circle(x, y, R_INT, stroke="var(--muted)", fill="var(--paper)", width=1.1)
        T.text(x, y + 0.5, str(w), size=10, color="currentColor")
        for k in kids:
            draw_nodes(k)
    else:
        hi = t is six_ac[2][0]
        T.rect(x - LW / 2, y - LHT / 2, LW, LHT, rx=4, stroke="var(--accent)" if hi else "currentColor",
               fill="var(--accent)" if hi else "var(--paper)", fill_opacity=0.2 if hi else None, width=1.5 if hi else 1.2)
        T.text(x, y - 6, ch, size=12, font=MONO, weight=600)
        T.text(x, y + 7, str(w), size=10, color="var(--muted)")


draw_nodes(ROOT)
save("a04-huffman-tree", T.figure(
    "<strong>One Huffman code tree for Sallows' sentence</strong> (the book's). Leaves show a letter and its "
    "frequency; each internal node shows the total frequency of its leaves, so the root holds the 170 letters. "
    "Left edges mean 0 and right edges 1; the highlighted path spells the codeword 101000 of A. The codeword "
    "length of a letter is the depth of its leaf, and the encoded sentence has "
    "Σ <i>f</i>[<i>i</i>]·depth(<i>i</i>) = 649 bits — also the sum of the 19 numbers in the internal nodes.",
    alt="Huffman code tree with 20 leaves for the letters of Sallows' sentence; the path to A is highlighted"))


# ============================================================ 3. a Gale-Shapley run (the book's 4 x 4 example)
HPREF = {"A": "tsrq", "B": "rtqs", "C": "trsq", "D": "srqt"}
DPREF = {"q": "ABCD", "r": "ADCB", "s": "BACD", "t": "DBCA"}
ORDER = ["A", "B", "C", "D", "A", "D", "B", "C", "C", "C"]   # who offers in steps 1..10


def run(order):
    nxt = {h: 0 for h in HPREF}
    match = {}                       # doctor -> hospital
    offers = []                      # (step, hospital, doctor, accepted, dropped)
    for step, h in enumerate(order, 1):
        assert h not in match.values()
        d = HPREF[h][nxt[h]]
        nxt[h] += 1
        cur = match.get(d)
        if cur is None:
            match[d] = h
            offers.append((step, h, d, True, None))
        elif DPREF[d].index(h) < DPREF[d].index(cur):
            match[d] = h
            offers.append((step, h, d, True, cur))
        else:
            offers.append((step, h, d, False, None))
    assert len(match) == 4
    return offers, match


OFFERS, MATCH = run(ORDER)
assert {h + d for d, h in MATCH.items()} == {"As", "Bt", "Cq", "Dr"}
final = {(h, d) for d, h in MATCH.items()}
offered = {(h, d): st for st, h, d, _, _ in OFFERS}
G = SVG(560, 214, font_size=13)
BW_, BH_, GAP = 36, 28, 6


def panel(x0, title, rows, prefs, key):
    G.text(x0 + 22 + 2 * (BW_ + GAP), 14, title, size=12, color="var(--muted)")
    for c, lab in enumerate(["1st", "2nd", "3rd", "4th"]):
        G.text(x0 + 30 + c * (BW_ + GAP) + BW_ / 2, 34, lab, size=10, color="var(--muted)")
    for r, who in enumerate(rows):
        y = 46 + r * (BH_ + 10)
        G.text(x0 + 10, y + BH_ / 2, who, size=14, font=SERIF_IT, italic=True)
        for c, other in enumerate(prefs[who]):
            pair = key(who, other)
            x = x0 + 30 + c * (BW_ + GAP)
            if pair in final:
                G.rect(x, y, BW_, BH_, rx=4, stroke="var(--accent)", fill="var(--accent)", fill_opacity=0.25, width=1.7)
                col = "currentColor"
            elif pair in offered:
                G.rect(x, y, BW_, BH_, rx=4, stroke="currentColor", fill="none", width=1.1)
                G.line(x + 4, y + BH_ - 4, x + BW_ - 4, y + 4, color="var(--hi)", width=1.3)
                col = "currentColor"
            else:
                G.rect(x, y, BW_, BH_, rx=4, stroke="var(--muted)", fill="none", width=0.9, dash="2 2")
                col = "var(--muted)"
            G.text(x + 12, y + BH_ / 2, other, size=14, font=SERIF_IT, italic=True, color=col)
            if pair in offered:
                G.text(x + BW_ - 9, y + BH_ / 2 + 5, str(offered[pair]), size=10, color="var(--hi)", weight=600)


panel(4, "hospitals' lists: offers made", "ABCD", HPREF, lambda h, d: (h, d))
panel(292, "doctors' lists: offers received", "qrst", DPREF, lambda d, h: (h, d))
save("a04-gale-shapley", G.figure(
    "<strong>The book's Gale–Shapley run.</strong> Each hospital walks down its own list; the small red number "
    "is the step at which that offer was made. Struck boxes are offers that were rejected at once or dropped "
    "later; filled boxes are the final matching {<i>As</i>, <i>Bt</i>, <i>Cq</i>, <i>Dr</i>}; dotted boxes "
    "never saw an offer. On the right, every doctor ends with the best offer she received, and County ("
    "<i>C</i>) ends with its last choice.",
    alt="two preference tables; offers numbered 1 to 10; final matches As, Bt, Cq, Dr highlighted"))
