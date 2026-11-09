#!/usr/bin/env python3
"""Figures for Erickson's lecture note 2 (Nuts and Bolts). Writes tools/figs/n02-<name>.html; then run
tools/assemble.py with content/4-lecture-notes/02-nuts-and-bolts.md. PIVOT_ORDER and MATRIX_N are imported by
tools/checks/n02.py."""
import os
from fractions import Fraction
from figlib import SVG, SANS, SERIF_IT, MONO

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")

N_TREE = 7
PIVOT_ORDER = [3, 6, 1, 5, 2, 7, 4]      # ranks of the pivot bolts, in the order they are chosen
MATRIX_N = 8


def save(name, html):
    with open(os.path.join(OUT, name + ".html"), "w", encoding="utf-8") as f:
        f.write(html + "\n")
    print("wrote", name)


def iterative_tree(n, order):
    """Run the iterative partitioning with the given pivot order. Returns the list of nodes
    (subset, pivot, step, parent_index, side) in the order they are partitioned."""
    nodes = []
    blocks = [(tuple(range(1, n + 1)), None, None)]   # (subset, parent node index, side)
    for step, p in enumerate(order, start=1):
        k = next(i for i, b in enumerate(blocks) if p in b[0])
        sub, par, side = blocks.pop(k)
        idx = len(nodes)
        nodes.append((sub, p, step, par, side))
        left = tuple(x for x in sub if x < p)
        right = tuple(x for x in sub if x > p)
        if left:
            blocks.append((left, idx, "L"))
        if right:
            blocks.append((right, idx, "R"))
    return nodes


# ---------------------------------------------------------------- the recursion tree (the note's missing figure)
def tree_fig():
    nodes = iterative_tree(N_TREE, PIVOT_ORDER)
    W, H = 600, 312
    S = SVG(W, H, font_size=13)
    cw, ch = 20, 24
    pos = {}
    # hand layout by depth / side
    layout = {0: (300, 34)}
    for i, (sub, p, step, par, side) in enumerate(nodes):
        if par is None:
            continue
        px, py = layout[par]
        spread = {1: 150, 2: 78, 3: 48}
        depth = 1
        q = par
        while nodes[q][3] is not None:
            depth += 1
            q = nodes[q][3]
        dx = spread.get(depth, 40)
        layout[i] = (px - dx if side == "L" else px + dx, py + 80)
    for i, (sub, p, step, par, side) in enumerate(nodes):
        x, y = layout[i]
        w = cw * len(sub)
        if par is not None:
            px, py = layout[par]
            S.line(px + (-30 if side == "L" else 30) * (len(nodes[par][0]) > 2), py + ch / 2 + 21, x,
                   y - ch / 2 - 2, width=1.2, opacity=0.6)
        S.rect(x - w / 2, y - ch / 2, w, ch, rx=4, width=1.2, fill="var(--paper)")
        for j, v in enumerate(sub):
            cx = x - w / 2 + cw * (j + 0.5)
            isp = v == p
            if isp:
                S.circle(cx, y, 9.5, stroke="var(--hi)", fill="none", width=1.6)
            S.text(cx, y + 1, str(v), font=MONO, size=13, color="var(--hi)" if isp else "currentColor",
                   weight=700 if isp else None)
        tests = 2 * len(sub) - 1
        ordinal = {1: "1st", 2: "2nd", 3: "3rd"}.get(step, f"{step}th")
        S.text(x, y + ch / 2 + 13, f"{ordinal} pivot · {tests} test" + ("s" if tests > 1 else ""), size=12,
               color="var(--muted)")
    total = sum(2 * len(sub) - 1 for sub, *_ in nodes)
    S.text(12, 22, "pivot order 3, 6, 1, 5, 2, 7, 4", size=13, anchor="start")
    S.text(12, 42, f"total {total} tests", size=13, anchor="start")
    cap = ("<strong>The recursion tree of one run on 7 pairs (the note has only a placeholder here).</strong> Each box is a "
           "subproblem, listing the ranks of its bolts; the circled rank is its pivot bolt, which is compared with "
           "every nut in the box, and then its nut with every other bolt: 2<i>m</i> − 1 tests for <i>m</i> pairs. "
           "Any order that partitions a box after its parent gives the same tests — here the pivots were drawn in "
           "the order 3, 6, 1, 5, 2, 7, 4. Bolt 2 and nut 5 are never compared: the first pivot drawn from "
           "{2, 3, 4, 5} is 3, which separates them. Bolt 4 and nut 5 are: the first pivot drawn from {4, 5} is 5. "
           "This run uses 29 tests; the expectation for 7 pairs is about 33.97.")
    return S.figure(cap, alt="recursion tree of randomized nuts-and-bolts matching on seven pairs")


# ---------------------------------------------------------------- comparison probabilities
def matrix_fig():
    n = MATRIX_N
    W, H = 600, 300
    S = SVG(W, H, font_size=12)
    c, x0, y0 = 30, 50, 36
    for i in range(1, n + 1):
        for j in range(1, n + 1):
            pr = Fraction(2, abs(i - j) + 1) if i != j else Fraction(1)
            x, y = x0 + (j - 1) * c, y0 + (i - 1) * c
            S.rect(x, y, c, c, fill="var(--accent)", fill_opacity=round(0.08 + 0.55 * float(pr), 2), stroke="none",
                   width=0)
            lab = "1" if pr == 1 else f"{pr.numerator}/{pr.denominator}"
            S.text(x + c / 2, y + c / 2 + 1, lab, size=11 if len(lab) > 3 else 12)
    for k in range(n + 1):
        S.line(x0, y0 + k * c, x0 + n * c, y0 + k * c, width=0.8, opacity=0.35)
        S.line(x0 + k * c, y0, x0 + k * c, y0 + n * c, width=0.8, opacity=0.35)
    for k in range(1, n + 1):
        S.text(x0 + (k - 0.5) * c, y0 - 12, f"N{k}", size=12)
        S.text(x0 - 14, y0 + (k - 0.5) * c, f"B{k}", size=12, anchor="end")
    lx = x0 + n * c + 22
    S.text(lx, y0 + 20, "Pr[ Bᵢ is compared with Nⱼ ]", size=13, anchor="start")
    S.text(lx, y0 + 44, "= 2 / (|i − j| + 1),  1 on the diagonal", size=13, anchor="start")
    S.text(lx, y0 + 90, "sum of all 64 entries:", size=13, anchor="start")
    S.text(lx, y0 + 112, "36·H₈ − 56 ≈ 41.84 expected tests", size=13, anchor="start")
    S.text(lx, y0 + 146, "worst case: 8² = 64 tests", size=13, anchor="start", color="var(--muted)")
    cap = ("<strong>Every comparison probability for 8 pairs.</strong> Bolt <i>B<sub>i</sub></i> (the "
           "<i>i</i>-th smallest) meets nut <i>N<sub>j</sub></i> exactly when the first pivot drawn from the ranks "
           "between <i>i</i> and <i>j</i> is <i>i</i> or <i>j</i>, which has probability 2/(|<i>i</i> − <i>j</i>| + 1). "
           "Neighbors in size are always compared; far-apart sizes rarely are. By linearity of expectation the "
           "expected number of tests is the sum of the table, 4<i>nH<sub>n</sub></i> − 7<i>n</i> + "
           "4<i>H<sub>n</sub></i> = 36<i>H</i><sub>8</sub> − 56 = 2929/70 ≈ 41.84.")
    return S.figure(cap, alt="eight by eight table of comparison probabilities, largest along the diagonal")


if __name__ == "__main__":
    save("n02-tree", tree_fig())
    save("n02-matrix", matrix_fig())
