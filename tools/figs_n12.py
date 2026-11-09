#!/usr/bin/env python3
"""Figures for lecture note 12 (Lower bounds). Writes tools/figs/n12-<name>.html; then run tools/assemble.py on
content/4-lecture-notes/12-lower-bounds.md. The dictionary decision tree is the same nested tuple that
tools/checks/n12.py runs on every query; the sorting tree is read off insertion sort's comparisons on all six
orders of three elements."""
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


def box(S, x, y, label, w=None, hi=False, size=12.5):
    w = w or (7.0 * len(label) + 14)
    col = "var(--hi)" if hi else "currentColor"
    S.rect(x - w / 2, y - 11, w, 22, rx=11, stroke=col, fill="var(--paper)", width=1.3)
    S.text(x, y + 1, label, size=size, color=col)


def edge(S, a, b, label, side, ra=11, rb=11, hi=False, lab_size=10.5):
    (x1, y1), (x2, y2) = a, b
    S.line(x1, y1 + ra, x2, y2 - rb,
           color="var(--hi)" if hi else "currentColor", width=1.8 if hi else 1.1, opacity=None if hi else 0.7)
    mx, my = (x1 + x2) / 2, (y1 + ra + y2 - rb) / 2
    S.text(mx + (-9 if side == "L" else 9), my - 3, label, size=lab_size, color="var(--muted)",
           anchor="end" if side == "L" else "start")


# ================================================================== 1. dictionary problem, first eight primes
PRIMES = [2, 3, 5, 7, 11, 13, 17, 19]
DT = ("<", 11, ("<", 5, ("<", 3, ("=", 1), ("=", 2)), ("<", 7, ("=", 3), ("=", 4))),
      ("<", 17, ("<", 13, ("=", 5), ("=", 6)), ("<", 19, ("=", 7), ("=", 8))))
W, H = 640, 250
S = SVG(W, H)
leafw = (W - 20) / 16
ys = [24, 76, 128, 180, 228]
path = []  # highlight the search for x = 13


def walk(t, lo, hi, depth, x=13, on=True):
    cx = (lo + hi) / 2
    if t[0] == "<":
        go_left = x < t[1]
        mid = (lo + hi) / 2
        a = walk(t[2], lo, mid, depth + 1, x, on and go_left)
        b = walk(t[3], mid, hi, depth + 1, x, on and not go_left)
        edge(S, (cx, ys[depth]), a, "Y", "L", hi=on and go_left)
        edge(S, (cx, ys[depth]), b, "N", "R", hi=on and not go_left)
        box(S, cx, ys[depth], f"x<{t[1]}?", hi=on)
    else:
        i = t[1]
        hit = x == PRIMES[i - 1]
        mid = (lo + hi) / 2
        a, b = ((lo + mid) / 2, ys[depth + 1]), ((mid + hi) / 2, ys[depth + 1])
        edge(S, (cx, ys[depth]), a, "Y", "L", rb=8, hi=on and hit)
        edge(S, (cx, ys[depth]), b, "N", "R", rb=8, hi=on and not hit)
        box(S, cx, ys[depth], f"x={PRIMES[i - 1]}?", hi=on, size=11.5)
        S.text(a[0], a[1] + 1, str(i), size=13, color="var(--hi)" if on and hit else "currentColor",
               weight="600" if on and hit else None)
        S.text(b[0], b[1] + 1, "–", size=13, color="currentColor")
    return cx, ys[depth]


walk(DT, 10, W - 10, 0)
save("n12-dictionary", S.figure(
    "<strong>A binary decision tree for the dictionary problem</strong> on the first eight primes (the note’s figure "
    "on p. 3). Each internal node asks one yes/no question; a leaf outputs the index of <i>x</i>, or – for "
    "“none”. Every search asks exactly 4 questions, and no binary tree can do better: there are 9 possible outputs, "
    "so at least ⌈lg 9⌉ = 4 levels are needed. Highlighted: the search for <i>x</i> = 13, which answers 6.",
    alt="decision tree with comparison nodes x<11?, x<5?, x<17? and so on, equality tests at the bottom, and "
        "sixteen leaves"))


# ================================================================== 2. insertion sort on three elements
def insertion_trace(p):
    trace, srt = [], [0]
    for i in (1, 2):
        pos = len(srt)
        while pos > 0:
            j = srt[pos - 1]
            trace.append((min(i, j), max(i, j), p[min(i, j)] < p[max(i, j)]))
            if p[i] < p[j]:
                pos -= 1
            else:
                break
        srt.insert(pos, i)
    return tuple(trace), "".join(str(k + 1) for k in srt)


paths = dict(insertion_trace(p) for p in itertools.permutations(range(3)))
assert len(paths) == 6


def build(prefix):
    """Tree from the recorded paths: ('cmp', i, j, lt-subtree, gt-subtree) or ('leaf', order)."""
    nxt = {t[len(prefix)] for t in paths if t[:len(prefix)] == prefix and len(t) > len(prefix)}
    leaf = [o for t, o in paths.items() if t == prefix]
    if leaf:
        return ("leaf", leaf[0])
    (i, j, _), = {(a, b, True) for a, b, _ in nxt}
    return ("cmp", i, j, build(prefix + ((i, j, True),)), build(prefix + ((i, j, False),)))


TREE = build(())
S = SVG(520, 205)
ys = [24, 82, 140, 188]


def nleaves(t):
    return 1 if t[0] == "leaf" else nleaves(t[3]) + nleaves(t[4])


def draw(t, lo, hi, d):
    if t[0] == "leaf":
        x = (lo + hi) / 2
        lab = "<".join(f"x{c}" for c in t[1])
        lab = lab.replace("x1", "x₁").replace("x2", "x₂").replace("x3", "x₃")
        S.text(x, ys[d] + 1, lab, size=15, font=SERIF_IT, italic=True)
        return x, ys[d]
    x = (lo + hi) / 2
    nl, nr = nleaves(t[3]), nleaves(t[4])
    mid = lo + (hi - lo) * nl / (nl + nr)
    a = draw(t[3], lo, mid, d + 1)
    b = draw(t[4], mid, hi, d + 1)
    edge(S, (x, ys[d]), a, "<", "L", rb=10 if t[3][0] == "leaf" else 11, lab_size=13)
    edge(S, (x, ys[d]), b, ">", "R", rb=10 if t[4][0] == "leaf" else 11, lab_size=13)
    box(S, x, ys[d], f"x{t[1] + 1}:x{t[2] + 1}".replace("x1", "x₁").replace("x2", "x₂").replace("x3", "x₃"), w=58,
        size=14)
    return x, ys[d]


draw(TREE, 10, 510, 0)
save("n12-sort3", S.figure(
    "<strong>Insertion sort on three elements, as a comparison tree.</strong> Each node compares two inputs; each "
    "leaf is one of the 3! = 6 orders. Some path must have length ⌈lg 6⌉ = 3, so no comparison sort handles every "
    "input of size 3 in two comparisons; insertion sort needs 3 on four of the six orders and 2 on the other two.",
    alt="binary tree with root x1:x2, internal nodes comparing pairs, and six leaves listing the orders"))
