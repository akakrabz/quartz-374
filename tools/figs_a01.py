#!/usr/bin/env python3
"""Figures for Algorithms Chapter 1 (recursion). Writes tools/figs/a01-<name>.html; then run tools/assemble.py
with the chapter page. The data of the median-of-medians grid is imported by tools/checks/a01.py."""
import os
from figlib import SVG, SANS, SERIF_IT, MONO

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")

# ---------------------------------------------------------------- data for the median-of-medians grid
# 50 inputs = 10 blocks of 5. MOM_GRID: the blocks drawn as columns, each sorted top (small) to bottom (large),
# columns ordered by their medians. Chosen so that the bound is tight: exactly 14 values lie below mom = 15.
MOM_GRID = [
    [5, 8, 10, 21, 40],
    [1, 7, 11, 30, 47],
    [2, 9, 13, 25, 26],
    [4, 12, 14, 27, 32],
    [3, 6, 15, 44, 45],
    [16, 22, 24, 46, 48],
    [18, 20, 31, 42, 43],
    [17, 29, 33, 34, 49],
    [19, 23, 36, 38, 41],
    [28, 35, 37, 39, 50],
]
# the same blocks in input order (the algorithm sees these, unsorted)
MOM_INPUT_BLOCKS = [
    [31, 43, 18, 42, 20],
    [26, 2, 13, 9, 25],
    [37, 28, 50, 35, 39],
    [44, 3, 15, 45, 6],
    [10, 40, 5, 21, 8],
    [49, 33, 17, 34, 29],
    [11, 47, 1, 30, 7],
    [24, 48, 16, 46, 22],
    [41, 19, 38, 23, 36],
    [12, 32, 27, 4, 14],
]


def save(name, html):
    with open(os.path.join(OUT, name + ".html"), "w", encoding="utf-8") as f:
        f.write(html + "\n")
    print("wrote", name)


# ---------------------------------------------------------------- Tower of Hanoi: the recursion
def hanoi_fig():
    W, H = 660, 196
    S = SVG(W, H, font_size=13)
    PW, GAP = 146, 18
    base_y = 112
    widths = {1: 18, 2: 27, 3: 36, 4: 46}
    dh = 12
    states = [
        {0: [4, 3, 2, 1], 1: [], 2: []},
        {0: [4], 1: [3, 2, 1], 2: []},
        {0: [], 1: [3, 2, 1], 2: [4]},
        {0: [], 1: [], 2: [4, 3, 2, 1]},
    ]
    line1 = ["start", "Hanoi(n−1, src, tmp, dst)", "move disk n: src → dst", "Hanoi(n−1, tmp, dst, src)"]
    line2 = ["n = 4 disks on src", "recursion: 7 moves", "1 move", "recursion: 7 moves"]
    for p, st in enumerate(states):
        x0 = 10 + p * (PW + GAP)
        pegx = [x0 + 27, x0 + PW / 2, x0 + PW - 27]
        S.line(x0 + 2, base_y, x0 + PW - 2, base_y, width=2)
        for i, px in enumerate(pegx):
            S.line(px, base_y - 66, px, base_y, width=2.4, color="var(--muted)")
            S.text(px, base_y + 13, ["src", "tmp", "dst"][i], size=11.5, color="var(--muted)", font=MONO)
        for peg, disks in st.items():
            for h, d in enumerate(disks):
                w = widths[d]
                y = base_y - (h + 1) * dh - 1
                big = d == 4
                S.rect(pegx[peg] - w / 2, y, w, dh - 1.5, rx=3,
                       stroke="var(--accent)" if big else "currentColor",
                       fill="var(--accent)" if big else "currentColor",
                       fill_opacity=0.35 if big else 0.10, width=1.3)
        S.text(x0 + PW / 2, base_y + 38, line1[p], size=12.5, weight=600 if p in (1, 3) else None)
        S.text(x0 + PW / 2, base_y + 56, line2[p], size=12, color="var(--muted)")
        if p < 3:
            ax = x0 + PW + 2
            S.line(ax, 62, ax + GAP - 4, 62, arrow=True, width=1.6)
        # phase number
        if p > 0:
            S.circle(x0 + 12, 22, 9, stroke="var(--hi)", fill="var(--paper)", width=1.3)
            S.text(x0 + 12, 22.5, str(p), size=11.5, color="var(--hi)", weight=700)
    S.text(W / 2, H - 12, "n = 4:  7 + 1 + 7 = 15 = 2⁴ − 1 moves", size=12.5, color="var(--accent)")
    return S.figure(
        "<strong>The Tower of Hanoi recursion.</strong> To move <i>n</i> disks from src to dst: (1) recursively move "
        "the <i>n</i> − 1 smaller disks out of the way to tmp, (2) move the largest disk (shaded) to dst, (3) recursively "
        "move the <i>n</i> − 1 smaller disks from tmp onto it. Only the largest disk matters at this level; the "
        "Recursion Fairy handles the rest. Moves: <i>T</i>(<i>n</i>) = 2<i>T</i>(<i>n</i> − 1) + 1 = 2<sup><i>n</i></sup> − 1.",
        alt="four snapshots of a 4-disk Tower of Hanoi: start, after moving 3 disks to the middle peg, after moving the "
            "largest disk, finished")


# ---------------------------------------------------------------- recursion trees: the three cases
def tree_row(S, y0, title, source, levels, sums, verdict, note, node_w):
    """levels: list of lists of labels; draws a layered tree (children evenly split under parents)."""
    S.text(14, y0, title, anchor="start", size=13, weight=600)
    S.text(14 + 7.1 * len(title), y0, source, anchor="start", size=12.5, color="var(--muted)")
    S.add(f'<text x="470" y="{y0}" text-anchor="start" dominant-baseline="central" fill="var(--hi)" '
          f'style="font-size:13.5px;font-family:{SANS};font-weight:700;">{verdict}</text>')
    left, right = 18, 430
    ys = [y0 + 30 + 31 * d for d in range(len(levels))]
    xs = []
    for d, lab in enumerate(levels):
        k = len(lab)
        span = right - left
        xs.append([left + span * (i + 0.5) / k for i in range(k)])
    for d in range(1, len(levels)):
        per = len(levels[d]) // len(levels[d - 1])
        for i, x in enumerate(xs[d]):
            px = xs[d - 1][i // per]
            S.line(px, ys[d - 1] + 9, x, ys[d] - 9, width=1.1, opacity=0.5)
    for d, lab in enumerate(levels):
        w = node_w[d]
        for x, t in zip(xs[d], lab):
            S.rect(x - w / 2, ys[d] - 9, w, 18, rx=4, stroke="currentColor", fill="var(--paper)", width=1.1)
            S.text(x, ys[d] + 0.5, t, size=12.5, font=SERIF_IT, italic=True)
    # level sums
    S.line(452, ys[0] - 12, 452, ys[-1] + 12, width=1, color="var(--muted)", dash="3 3")
    for d, s in enumerate(sums):
        S.text(470, ys[d] + 0.5, s, anchor="start", size=13, font=SERIF_IT, italic=True, color="var(--accent)")
    S.text(470, ys[-1] + 24, note, anchor="start", size=12.5, color="var(--accent)")


def three_cases_fig():
    W, H = 640, 468
    S = SVG(W, H, font_size=13)
    S.text(470, 14, "level sums", anchor="start", size=12, color="var(--muted)")
    tree_row(S, 40, "Decreasing:  T(n) = T(n/5) + T(7n/10) + n", "  (MomSelect)",
             [["n"], ["n/5", "7n/10"], ["n/25", "7n/50", "7n/50", "49n/100"]],
             ["n", "9n/10", "81n/100"], "Θ(n)", "root dominates", [30, 48, 58])
    tree_row(S, 186, "Equal:  T(n) = 2T(n/2) + n", "  (MergeSort)",
             [["n"], ["n/2", "n/2"], ["n/4"] * 4],
             ["n", "n", "n"], "Θ(n log n)", "× (lg n + 1) levels", [30, 36, 36])
    tree_row(S, 332, "Increasing:  T(n) = 3T(n/2) + n", "  (Karatsuba)",
             [["n"], ["n/2"] * 3, ["n/4"] * 9],
             ["n", "3n/2", "9n/4"],
             'Θ(n<tspan dy="-6" style="font-size:10.5px">lg 3</tspan><tspan dy="6">)</tspan>',
             "leaves dominate", [30, 36, 36])
    return S.figure(
        "<strong>The three easy cases of a recursion tree.</strong> Each node holds the non-recursive work of one "
        "subproblem; the running time is the sum over all nodes, added level by level (right). If the level sums "
        "shrink geometrically, the root's term dominates; if they are all equal, multiply by the number of levels; if "
        "they grow geometrically, the leaves dominate — and there are <i>n</i><sup>lg 3</sup> of them for Karatsuba. "
        "Unbalanced trees (top) need no special treatment.",
        alt="three recursion trees with three levels each and their level sums: decreasing, equal and increasing")


# ---------------------------------------------------------------- median of medians grid
def mom_grid_fig():
    W, H = 640, 232
    S = SVG(W, H, font_size=13)
    cw, ch = 34, 28
    gx, gy = 92, 34
    mom_col = 4
    for c, col in enumerate(MOM_GRID):
        for r, v in enumerate(col):
            x, y = gx + c * cw, gy + r * ch
            below = (c < mom_col and r < 3) or (c == mom_col and r < 2)
            above = (c > mom_col and r > 1) or (c == mom_col and r > 2)
            if below:
                S.rect(x, y, cw, ch, fill="var(--accent)", fill_opacity=0.22, stroke="none", width=0)
            if above:
                S.rect(x, y, cw, ch, fill="var(--accent2)", fill_opacity=0.22, stroke="none", width=0)
            S.rect(x, y, cw, ch, stroke="currentColor", width=0.8)
            is_mom = (c == mom_col and r == 2)
            S.text(x + cw / 2, y + ch / 2 + 0.5, str(v), size=13, font=MONO,
                   color="var(--hi)" if is_mom else "currentColor", weight=700 if is_mom else None)
    # medians row outline and mom cell
    S.rect(gx, gy + 2 * ch, 10 * cw, ch, stroke="currentColor", width=2.2)
    S.rect(gx + mom_col * cw + 1.5, gy + 2 * ch + 1.5, cw - 3, ch - 3, stroke="var(--hi)", width=2.4)
    # annotations
    S.text(gx - 10, gy + 2 * ch + ch / 2, "medians", anchor="end", size=12, color="var(--muted)")
    S.line(22, gy + 4, 22, gy + 5 * ch - 4, arrow=True, color="var(--muted)", width=1.3)
    S.text(22, gy - 8, "small", size=11, color="var(--muted)")
    S.text(22, gy + 5 * ch + 10, "large", size=11, color="var(--muted)")
    S.text(gx + 5 * cw, gy - 16, "10 blocks of 5, each drawn sorted; blocks ordered by their medians →", size=12,
           color="var(--muted)")
    S.text(gx + mom_col * cw + cw / 2, gy + 5 * ch + 16, "mom = 15", size=12.5, color="var(--hi)", weight=700)
    # legend
    lx, ly = gx + 10 * cw + 22, gy + 8
    S.rect(lx, ly, 16, 14, fill="var(--accent)", fill_opacity=0.35, stroke="currentColor", width=0.8)
    S.text(lx + 24, ly + 7, "14 values surely < mom", anchor="start", size=12.5)
    S.rect(lx, ly + 28, 16, 14, fill="var(--accent2)", fill_opacity=0.35, stroke="currentColor", width=0.8)
    S.text(lx + 24, ly + 35, "17 values surely > mom", anchor="start", size=12.5)
    S.text(lx, ly + 70, "k > 15: recurse on the", anchor="start", size=12.5)
    S.text(lx, ly + 87, "35 = 7n/10 values > mom", anchor="start", size=12.5)
    S.text(lx, ly + 110, "k < 15: recurse on at most", anchor="start", size=12.5)
    S.text(lx, ly + 127, "50 − 17 − 1 = 32 values", anchor="start", size=12.5)
    return S.figure(
        "<strong>Why the median of medians is a good pivot</strong> (<i>n</i> = 50, <i>m</i> = 10 blocks). Picture each "
        "block as a column sorted top to bottom and the columns ordered by their medians — the algorithm never does "
        "this sorting. Mom, the 5th smallest median, is above the top-left block of shaded cells and below the "
        "bottom-right block, so at least 3⌊<i>m</i>/2⌋ − 1 ≈ 3<i>n</i>/10 values lie on each side. In this input the "
        "bound is tight: exactly 14 values are smaller than mom.",
        alt="5 by 10 grid of the numbers 1 to 50 with mom = 15 in the center row; shaded regions show values certainly "
            "smaller and certainly larger than mom")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    save("a01-hanoi", hanoi_fig())
    save("a01-three-cases", three_cases_fig())
    save("a01-mom-grid", mom_grid_fig())
