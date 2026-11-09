#!/usr/bin/env python3
"""Figures for Erickson's lecture note 1 (Discrete Probability). Writes tools/figs/n01-<name>.html; then run
tools/assemble.py with content/4-lecture-notes/01-discrete-probability.md. The data below (shuffle choices,
coupon-collector n) is imported by tools/checks/n01.py."""
import os
from fractions import Fraction
from figlib import SVG, SANS, SERIF_IT, MONO

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")

# SelectionShuffle trace: A = A B C D E, and Random(i) for i = 5, 4, 3, 2, 1
SHUFFLE_START = list("ABCDE")
SHUFFLE_CHOICES = [2, 4, 1, 1, 1]
COUPON_N = 10


def save(name, html):
    with open(os.path.join(OUT, name + ".html"), "w", encoding="utf-8") as f:
        f.write(html + "\n")
    print("wrote", name)


def selection_shuffle_trace(A, choices):
    """States after each iteration of SelectionShuffle with the given Random(i) results (1-indexed)."""
    A = list(A)
    n = len(A)
    states = []
    for i, r in zip(range(n, 0, -1), choices):
        A[i - 1], A[r - 1] = A[r - 1], A[i - 1]
        states.append((i, r, list(A)))
    return states


# ---------------------------------------------------------------- two dice
def dice_fig():
    W, H = 540, 300
    S = SVG(W, H, font_size=13)
    c = 34
    x0, y0 = 116, 58
    # shading: red 5 row, blue 5 column
    S.rect(x0, y0 + 4 * c, 6 * c, c, fill="var(--accent)", fill_opacity=0.20, stroke="none", width=0)
    S.rect(x0 + 4 * c, y0, c, 6 * c, fill="var(--accent2)", fill_opacity=0.22, stroke="none", width=0)
    for i in range(7):
        S.line(x0, y0 + i * c, x0 + 6 * c, y0 + i * c, width=1, opacity=0.45)
        S.line(x0 + i * c, y0, x0 + i * c, y0 + 6 * c, width=1, opacity=0.45)
    for r in range(1, 7):
        for b in range(1, 7):
            cx, cy = x0 + (b - 0.5) * c, y0 + (r - 0.5) * c
            if r + b == 6:
                S.rect(cx - c / 2 + 3, cy - c / 2 + 3, c - 6, c - 6, rx=5, stroke="var(--hi)", width=2)
                S.text(cx, cy, str(r + b), size=12, color="var(--hi)", weight=700)
            else:
                S.text(cx, cy, str(r + b), size=12, color="var(--muted)")
    for k in range(1, 7):
        S.text(x0 + (k - 0.5) * c, y0 - 12, str(k), size=13)
        S.text(x0 - 13, y0 + (k - 0.5) * c, str(k), size=13)
    S.text(x0 + 3 * c, y0 - 34, "blue die", size=13)
    S.text(x0 - 30, y0 + 3 * c, "red die", size=13, anchor="end")
    # legend
    lx, ly = 352, 92
    S.rect(lx, ly - 9, 18, 18, fill="var(--accent)", fill_opacity=0.25, stroke="none", width=0)
    S.text(lx + 28, ly, "red 5: 6 cells, 6/36", anchor="start")
    S.rect(lx, ly + 31, 18, 18, fill="var(--accent2)", fill_opacity=0.28, stroke="none", width=0)
    S.text(lx + 28, ly + 40, "blue 5: 6 cells, 6/36", anchor="start")
    S.rect(lx + 1, ly + 72, 16, 16, rx=4, stroke="var(--hi)", width=2)
    S.text(lx + 28, ly + 80, "total 6: 5 cells, 5/36", anchor="start")
    S.text(lx, ly + 122, "at least one 5: 11 cells", anchor="start")
    S.text(lx, ly + 142, "two 5s: 1 cell", anchor="start")
    cap = ("<strong>The sample space of two fair dice.</strong> Each of the 36 cells (red value, blue value) has "
           "probability 1/36 and shows the total. An event is a set of cells and its probability is its number of "
           "cells over 36. The row “red 5” and the column “blue 5” overlap in the cell (5, 5), so they are not "
           "disjoint: Pr[red 5 ∨ blue 5] = (6 + 6 − 1)/36 = 11/36. Conditioning on “total 6” keeps only its "
           "five outlined cells, one of which has red 5: Pr[red 5 | total 6] = 1/5.")
    return S.figure(cap, alt="six by six grid of dice outcomes; the red-5 row and blue-5 column are shaded, the "
                             "five cells with total 6 are outlined")


# ---------------------------------------------------------------- von Neumann's coin
def vonneumann_fig():
    W, H = 560, 250
    S = SVG(W, H, font_size=13)
    root = (40, 136)
    f1 = {1: (190, 80), 0: (190, 192)}
    leaves = {(1, 1): (360, 50), (1, 0): (360, 110), (0, 1): (360, 162), (0, 0): (360, 222)}
    S.circle(*root, 7, fill="currentColor")
    S.text(root[0], root[1] + 22, "start", size=12, color="var(--muted)")
    for x, (px, py) in f1.items():
        S.line(root[0] + 8, root[1] + (-4 if x else 4), px - 16, py + (6 if x else -6), width=1.4, arrow=True)
        S.circle(px, py, 14)
        S.text(px, py + 1, str(x), font=MONO, size=13)
        S.text((root[0] + px) / 2 - 6, (root[1] + py) / 2 + (-12 if x else 12), "p" if x else "q",
               font=SERIF_IT, italic=True, size=15, halo=True)
    S.text(190, 16, "first flip x", size=12, color="var(--muted)")
    for (x, y), (lx, ly) in leaves.items():
        px, py = f1[x]
        S.line(px + 15, py + (-4 if y else 4) * (1 if True else 1), lx - 16, ly, width=1.4, arrow=True)
        ret = x != y
        col = "var(--hi)" if ret else "currentColor"
        S.circle(lx, ly, 14, stroke=col, width=2 if ret else 1.6)
        S.text(lx, ly + 1, str(y), font=MONO, size=13, color=col)
        S.text((px + lx) / 2 + 2, (py + ly) / 2 + (-10 if y else 10), "p" if y else "q",
               font=SERIF_IT, italic=True, size=15, halo=True)
        prob = {(1, 1): "p²", (1, 0): "pq", (0, 1): "qp", (0, 0): "q²"}[(x, y)]
        S.text(lx + 26, ly, prob, font=SERIF_IT, italic=True, size=15, anchor="start", color=col)
        msg = f"return {x}" if ret else "flip both again"
        S.text(lx + 64, ly, msg, size=13, anchor="start", color=col, weight=600 if ret else None)
    S.text(360, 16, "second flip y", size=12, color="var(--muted)")
    cap = ("<strong>One round of von Neumann’s coin.</strong> Two independent flips of a coin that shows 1 with "
           "unknown probability <i>p</i> (and 0 with probability <i>q</i> = 1 − <i>p</i>). The outcomes 10 and 01 "
           "have the same probability <i>pq</i>, so a round that stops returns 1 or 0 with probability 1/2 each. A "
           "round stops with probability 2<i>pq</i>, so the number of rounds is geometric with mean 1/(2<i>pq</i>) "
           "and the expected number of flips is 1/(<i>pq</i>): 9/2 for <i>p</i> = 1/3, and 4 for a fair coin.")
    return S.figure(cap, alt="probability tree of two biased coin flips; outcomes 10 and 01 return a bit, 11 and 00 "
                             "start over")


# ---------------------------------------------------------------- coupon collector phases
def coupon_fig():
    n = COUPON_N
    W, H = 560, 250
    S = SVG(W, H, font_size=13)
    x0, y0, bw, gap = 64, 206, 36, 10
    scale = 15.0  # px per purchase
    S.line(x0 - 6, y0, x0 + n * (bw + gap) + 4, y0, width=1.2)
    for v in (2, 4, 6, 8, 10):
        y = y0 - v * scale
        S.line(x0 - 6, y, x0 + n * (bw + gap) + 4, y, width=0.8, opacity=0.25, dash="3 4")
        S.text(x0 - 12, y, str(v), size=12, anchor="end", color="var(--muted)")
    for i in range(1, n + 1):
        e = Fraction(n, n - i + 1)
        h = float(e) * scale
        x = x0 + (i - 1) * (bw + gap) + gap / 2
        last = i > n - 3
        S.rect(x, y0 - h, bw, h, fill="var(--hi)" if last else "var(--accent)", fill_opacity=0.55 if last else 0.4,
               stroke="var(--hi)" if last else "var(--accent)", width=1.2)
        lab = f"{float(e):.2f}".rstrip("0").rstrip(".")
        S.text(x + bw / 2, y0 - h - 10, lab, size=12, halo=True)
        S.text(x + bw / 2, y0 + 14, str(i), size=12)
    S.text(x0 + n * (bw + gap) / 2, y0 + 34, "phase i (waiting for the i-th new type)", size=12, color="var(--muted)")
    S.text(x0 - 40, y0 - 10.8 * scale - 4, "expected cards", size=12, color="var(--muted)", anchor="start")
    S.text(x0 + 120, 22, "total 10·H₁₀ ≈ 29.29; the last three phases ≈ 18.33 of it", size=13, anchor="start")
    cap = ("<strong>Where the time goes when collecting <i>n</i> = 10 types.</strong> In phase <i>i</i> you already "
           "own <i>i</i> − 1 types, each purchase is new with probability (<i>n</i> − <i>i</i> + 1)/<i>n</i>, and the "
           "phase lasts <i>n</i>/(<i>n</i> − <i>i</i> + 1) purchases on average (the bar heights). The first five "
           "types arrive within about 6.5 purchases on average; the last type alone takes 10. The sum is "
           "<i>n</i>·<i>H<sub>n</sub></i> = 7381/252 ≈ 29.29.")
    return S.figure(cap, alt="bar chart of expected purchases in each of ten phases, rising from 1 to 10")


# ---------------------------------------------------------------- SelectionShuffle trace
def shuffle_fig():
    states = selection_shuffle_trace(SHUFFLE_START, SHUFFLE_CHOICES)
    n = len(SHUFFLE_START)
    W, H = 560, 252
    S = SVG(W, H, font_size=13)
    c, x0, y0, rh = 30, 218, 22, 38
    rows = [("start", None, None, list(SHUFFLE_START))] + [
        (f"i = {i}:  Random({i}) = {r}", i, r, st) for i, r, st in states]
    for k, (lab, i, r, st) in enumerate(rows):
        y = y0 + k * rh
        S.text(x0 - 16, y + c / 2, lab, size=13, anchor="end", font=MONO if i else SANS)
        for j, ch in enumerate(st, start=1):
            inR = i is not None and j >= i
            S.rect(x0 + (j - 1) * c, y, c, c, fill="var(--accent)" if inR else "none",
                   fill_opacity=0.18 if inR else None, width=1.1)
            hit = i is not None and j in (i, r)
            S.text(x0 + (j - 1) * c + c / 2, y + c / 2 + 1, ch, font=MONO, size=14,
                   color="var(--hi)" if hit else "currentColor", weight=700 if hit else None)
        if i is not None and i != r:
            a, b = sorted((i, r))
            xa, xb = x0 + (a - 0.5) * c, x0 + (b - 0.5) * c
            S.path(f"M{xa},{y - 1} Q{(xa + xb) / 2},{y - 13} {xb},{y - 1}", color="var(--hi)", width=1.3)
    S.text(x0 + n * c + 16, y0 + 1 * rh + c / 2, "L = A[1 .. i − 1]: not yet chosen", size=12, anchor="start",
           color="var(--muted)")
    S.text(x0 + n * c + 16, y0 + 2 * rh + c / 2, "R = A[i .. n] (shaded): chosen", size=12, anchor="start",
           color="var(--muted)")
    S.text(x0 + n * c + 16, y0 + 5 * rh + c / 2, "output: a uniformly random", size=12, anchor="start",
           color="var(--muted)")
    S.text(x0 + n * c + 16, y0 + 5 * rh + c / 2 + 16, "permutation of A B C D E", size=12, anchor="start",
           color="var(--muted)")
    cap = ("<strong>SelectionShuffle on A B C D E.</strong> Iteration <i>i</i> (from <i>n</i> down to 1) swaps "
           "<i>A</i>[<i>i</i>] with <i>A</i>[Random(<i>i</i>)], a uniformly random position among the "
           "<i>i</i> not yet chosen (the arc marks the swap). The chosen element lands in position <i>i</i> and the "
           "shaded suffix grows by one: it is the list <i>R</i> of drawn lots, the prefix is the bag <i>L</i>. "
           "These choices (2, 4, 1, 1, 1) produce E C A D B; each of the 5! = 120 choice sequences gives a "
           "different permutation.")
    return S.figure(cap, alt="five rows showing the array after each swap of SelectionShuffle")


if __name__ == "__main__":
    save("n01-dice", dice_fig())
    save("n01-vonneumann", vonneumann_fig())
    save("n01-coupon", coupon_fig())
    save("n01-shuffle", shuffle_fig())
