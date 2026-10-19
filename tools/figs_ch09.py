#!/usr/bin/env python3
"""Figures for Chapter 9 (nondeterministic Turing machines). Writes tools/figs/<name>.html; then run
tools/assemble.py.

The machine N and the computation tree drawn in the figures are module-level data, verified by
tools/checks/ch09.py; the figures are written only when the script is run directly."""
import os
from figlib import SVG, MONO, SERIF_IT, SANS, esc

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")
B = "□"

# ---------------------------------------------------------------- data checked by tools/checks/ch09.py
# N guesses where the substring 11 starts. delta(p, a) is an ordered list of choices (choice 1, choice 2, ...).
N_DELTA = {
    ("start", "0"): [("start", "0", +1)],
    ("start", "1"): [("start", "1", +1), ("got1", "1", +1)],      # 1: keep scanning; 2: guess "11 starts here"
    ("start", B): [("reject", B, +1), ("loop", B, +1)],           # 1: give up; 2: loop forever
    ("got1", "1"): [("accept", "1", +1)],
    ("got1", "0"): [("reject", "0", +1)],
    ("got1", B): [("reject", B, +1)],
    ("loop", "0"): [("loop", "0", +1)], ("loop", "1"): [("loop", "1", +1)], ("loop", B): [("loop", B, +1)],
}
# N' = N without the looping choice: it decides "contains 11"
NP_DELTA = dict(N_DELTA)
NP_DELTA[("start", B)] = [("reject", B, +1)]

TREE_INPUT = "011"
# the computation tree of N on 011, cut below depth 5: key -> (state, head, depth, parent, choice label or None)
TREE = {
    "n0": ("start", 0, 0, None, None),
    "n1": ("start", 1, 1, "n0", None),
    "n2": ("start", 2, 2, "n1", "1"),
    "n3": ("got1", 2, 2, "n1", "2"),
    "n4": ("accept", 3, 3, "n3", None),
    "n5": ("start", 3, 3, "n2", "1"),
    "n6": ("got1", 3, 3, "n2", "2"),
    "n7": ("reject", 4, 4, "n5", "1"),
    "n8": ("loop", 4, 4, "n5", "2"),
    "n9": ("reject", 4, 4, "n6", None),
    "n10": ("loop", 5, 5, "n8", None),
}
BFS_ORDER = ["n0", "n1", "n2", "n3", "n5", "n6", "n4"]     # dequeued in this order; n4 accepts
DFS_EDGES = [("n0", "n1"), ("n1", "n2"), ("n2", "n5"), ("n5", "n7"), ("n5", "n8"), ("n8", "n10")]
ACCEPT_ADVICE = ["121", "122", "221", "222"]   # advice strings of length 3 that reach the accepting leaf: 2nd symbol 2

XPOS = {"n0": 350, "n1": 350, "n2": 260, "n3": 460, "n4": 460, "n5": 190, "n6": 330,
        "n7": 120, "n8": 230, "n9": 330, "n10": 230}


def save(name, html):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name + ".html"), "w", encoding="utf-8") as f:
        f.write(html + "\n")
    print("wrote", name)


def rich(S, x, y, parts, size=14, anchor="middle", color="currentColor"):
    out = []
    for txt, kind in parts:
        t = esc(txt)
        if kind == "sf":
            out.append(f'<tspan style="font-family:{SANS}">{t}</tspan>')
        elif kind == "it":
            out.append(f'<tspan style="font-family:{SERIF_IT};font-style:italic">{t}</tspan>')
        elif kind == "rm":
            out.append(f'<tspan style="font-family:{SERIF_IT}">{t}</tspan>')
        elif kind == "mono":
            out.append(f'<tspan style="font-family:{MONO};font-size:{size - 1}px">{t}</tspan>')
        elif kind == "sub":
            out.append(f'<tspan style="font-family:{SERIF_IT};font-style:italic;font-size:{size - 4}px" '
                       f'baseline-shift="sub">{t}</tspan>')
        else:
            raise ValueError(kind)
    S.add(f'<text x="{x}" y="{y}" text-anchor="{anchor}" dominant-baseline="central" fill="{color}" '
          f'style="font-size:{size}px;font-family:{SANS}">{"".join(out)}</text>')


def tape_of(head):
    t = TREE_INPUT
    return t + B * max(0, head + 1 - len(t))


def main():
    # ------------------------------------------------------------ 9.1 the computation tree of N on 011
    S = SVG(560, 418)
    ylev = lambda d: 32 + 66 * d
    W, H = 88, 38
    for d in range(6):
        S.text(18, ylev(d), f"t = {d}", size=12, anchor="start", color="var(--muted)")
    for k, (q, head, d, par, ch) in TREE.items():
        if par is None:
            continue
        x1, y1 = XPOS[par], ylev(TREE[par][2]) + H / 2
        x2, y2 = XPOS[k], ylev(d) - H / 2
        S.line(x1, y1, x2, y2 - 2, width=1.3, arrow=True)
        if ch:
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            S.text(mx + (-9 if x2 < x1 else 9 if x2 > x1 else 9), my, ch, size=12, font=MONO, color="var(--accent)",
                   halo=True)
    xl, yl = XPOS["n10"], ylev(5) + H / 2
    S.line(xl, yl, xl, yl + 16, width=1.3, dash="3 3")
    S.text(xl, yl + 26, "⋮ forever", size=12, color="var(--muted)")
    for k, (q, head, d, par, ch) in TREE.items():
        x, y = XPOS[k], ylev(d)
        if q == "accept":
            S.rect(x - W / 2 - 3, y - H / 2 - 3, W + 6, H + 6, rx=9, stroke="var(--accent)", fill="var(--paper)",
                   width=1.6)
            S.rect(x - W / 2, y - H / 2, W, H, rx=7, stroke="var(--accent)", fill="var(--accent)", fill_opacity=0.12,
                   width=1.6)
        elif q == "reject":
            S.rect(x - W / 2, y - H / 2, W, H, rx=7, stroke="var(--muted)", fill="var(--paper)", width=1.6)
        else:
            S.rect(x - W / 2, y - H / 2, W, H, rx=7, stroke="currentColor", fill="var(--paper)", width=1.4,
                   dash="4 3" if q == "loop" else None)
        col = "var(--accent)" if q == "accept" else "var(--muted)" if q == "reject" else "currentColor"
        S.text(x, y - 8, q, size=13, font=SERIF_IT, italic=True, color=col)
        tape = tape_of(head)
        cw = 9.4
        x0 = x - cw * len(tape) / 2
        for i, a in enumerate(tape):
            hot = i == head
            S.text(x0 + cw * (i + 0.5), y + 8, a, size=13, font=SERIF_IT if a == B else MONO,
                   color="var(--hi)" if hot else col, weight=700 if hot else None)
            if hot:
                S.line(x0 + cw * i + 1, y + 16, x0 + cw * (i + 1) - 1, y + 16, color="var(--hi)", width=1.4)
    save("ch09-computation-tree", S.figure(
        "<strong>The computation tree of <i>N</i> on input 011.</strong> Each node is a configuration: the state, "
        "and the tape with the head's cell in red. On a 1, <i>N</i> may keep scanning (choice 1) or guess that this "
        "1 begins 11 (choice 2); at the blank after the input it may reject (1) or loop forever (2). One leaf "
        "accepts, so <i>N</i> accepts 011 — although two branches reject and one runs forever.",
        alt="tree of configurations of N on input 011 with one accepting leaf at depth 3, two rejecting leaves at "
            "depth 4 and an infinite looping branch"))

    # ------------------------------------------------------------ 9.4 breadth-first versus depth-first
    S = SVG(600, 336)
    ylev = lambda d: 30 + 50 * d
    r = 13
    dfs = set(DFS_EDGES)
    for k, (q, head, d, par, ch) in TREE.items():
        if par is None:
            continue
        hot = (par, k) in dfs
        x1, y1, x2, y2 = XPOS[par], ylev(TREE[par][2]), XPOS[k], ylev(d)
        import math
        L = math.hypot(x2 - x1, y2 - y1)
        ux, uy = (x2 - x1) / L, (y2 - y1) / L
        S.line(x1 + ux * r, y1 + uy * r, x2 - ux * (r + 2), y2 - uy * (r + 2), width=2.0 if hot else 1.2,
               color="var(--hi)" if hot else "currentColor", arrow=True, dash=None)
        if ch:
            S.text((x1 + x2) / 2 + (-9 if x2 < x1 else 9), (y1 + y2) / 2, ch, size=11, font=MONO,
                   color="var(--accent)", halo=True)
    xl, yl = XPOS["n10"], ylev(5) + r
    S.line(xl, yl, xl, yl + 22, width=2.0, color="var(--hi)", dash="3 3")
    S.text(xl + 12, yl + 30, "depth-first search goes down here forever", size=12, anchor="start",
           color="var(--hi)")
    order = {k: i + 1 for i, k in enumerate(BFS_ORDER)}
    for k, (q, head, d, par, ch) in TREE.items():
        x, y = XPOS[k], ylev(d)
        if q == "accept":
            S.circle(x, y, r + 4, stroke="var(--accent)", fill="var(--paper)")
            S.circle(x, y, r, stroke="var(--accent)", fill="var(--accent)", fill_opacity=0.15)
        elif q == "reject":
            S.circle(x, y, r, stroke="var(--muted)", fill="var(--paper)")
        else:
            S.circle(x, y, r, stroke="currentColor", fill="var(--paper)", width=1.4)
        if k in order:
            S.text(x, y + 1, str(order[k]), size=13, weight=700,
                   color="var(--accent)" if q == "accept" else "currentColor")
        lab = {"accept": "accept", "reject": "reject", "loop": "loop"}.get(q)
        if lab:
            S.text(x + r + 8, y, lab, size=12, anchor="start",
                   color="var(--accent)" if q == "accept" else "var(--muted)")
    for d in range(6):
        S.text(18, ylev(d), f"t = {d}", size=12, anchor="start", color="var(--muted)")
    S.text(430, 24, "numbers: breadth-first order", size=12, anchor="start", color="currentColor")
    S.text(430, 42, "red: depth-first, choice 1 first", size=12, anchor="start", color="var(--hi)")
    save("ch09-bfs-dfs", S.figure(
        "<strong>Breadth-first, not depth-first.</strong> The same tree as above. Depth-first search (red) tries "
        "choice 1 first: it finds a rejecting leaf, backs up, and then follows the looping branch forever, never "
        "reaching the accepting leaf. Breadth-first search visits the tree level by level and dequeues the accepting "
        "configuration seventh.",
        alt="the computation tree drawn with small circles numbered 1 to 7 in breadth-first order; the depth-first "
            "path is drawn in red and continues down the infinite branch"))

    # ------------------------------------------------------------ 9.6 the Cook-Levin tableau
    S = SVG(640, 300)
    cols = ["sent", "0", "1", B, "?", "?", "?", "dots", "?", "sent"]
    rows = ["0", "1", "2", "3", "vdots", "N"]
    cw, ch = 40, 30
    gx, gy = 92, 46
    win_row, win_col = 2, 5
    for ri, rl in enumerate(rows):
        y = gy + ri * ch
        if rl == "vdots":
            for ci in range(len(cols)):
                S.text(gx + ci * cw + cw / 2, y + ch / 2, "⋮", size=13, color="var(--muted)")
            S.text(gx - 14, y + ch / 2, "⋮", size=13, anchor="end", color="var(--muted)")
            continue
        rich(S, gx - 14, y + ch / 2, [("t", "it"), (" = ", "rm"), (rl, "it" if rl == "N" else "rm")], size=13,
             anchor="end")
        for ci, c in enumerate(cols):
            x = gx + ci * cw
            if c == "dots":
                S.text(x + cw / 2, y + ch / 2, "⋯", size=13, color="var(--muted)")
                continue
            fill, fo = "none", None
            if c == "sent":
                fill, fo = "var(--muted)", 0.25
            elif ri == win_row and ci in (win_col - 1, win_col, win_col + 1):
                fill, fo = "var(--accent)", 0.18
            S.rect(x, y, cw, ch, stroke="var(--muted)", width=1, fill=fill, fill_opacity=fo)
            if ri == 0 and c not in ("sent",):
                if c == B:
                    S.text(x + cw / 2, y + ch / 2 + 1, B, size=14, font=SERIF_IT)
                elif c == "?":
                    S.text(x + cw / 2, y + ch / 2 + 1, "?", size=14, color="var(--accent2)", weight=700)
                else:
                    S.text(x + cw / 2, y + (ch / 2 - 4 if ci == 1 else ch / 2 + 1), c, size=14, font=MONO)
            if ri == 0 and ci == 1:
                S.rect(x + 2, y + 2, cw - 4, ch - 4, stroke="var(--hi)", width=1.6)
                S.text(x + cw / 2, y + ch - 7, "start", size=9, color="var(--hi)", font=SERIF_IT, italic=True)
    # the window: row t-1 cells i-1, i, i+1 determine row t cell i
    yw = gy + win_row * ch
    xc = gx + win_col * cw + cw / 2
    S.rect(gx + win_col * cw + 2, yw + ch + 2, cw - 4, ch - 4, stroke="var(--hi)", width=1.8)
    S.rect(gx + (win_col - 1) * cw + 1, yw + 1, 3 * cw - 2, ch - 2, stroke="var(--hi)", width=1.4, dash="4 3")
    # group labels above row 0
    def over(c1, c2, parts, color="currentColor"):
        x1, x2 = gx + c1 * cw + 3, gx + (c2 + 1) * cw - 3
        S.path(f"M{x1},{gy - 4} L{x1},{gy - 9} L{x2},{gy - 9} L{x2},{gy - 4}", color=color, width=1.2)
        rich(S, (x1 + x2) / 2, gy - 20, parts, size=12, color=color)
    over(1, 2, [("input ", "sf"), ("w", "it")])
    over(3, 3, [("blank", "sf")])
    over(4, 8, [("advice ", "sf"), ("x", "it"), (" (unknown)", "sf")], color="var(--accent2)")
    rich(S, gx + cw / 2, gy - 20, [("sentinel", "sf")], size=11, color="var(--muted)")
    rich(S, gx + 9.5 * cw, gy - 20, [("sentinel", "sf")], size=11, color="var(--muted)")
    yb = gy + len(rows) * ch + 22
    rich(S, gx - 40, yb, [("Q", "it"), ("t,i,q", "sub"), (": after ", "sf"), ("t", "it"),
                          (" steps the head is on cell ", "sf"), ("i", "it"), (" in state ", "sf"), ("q", "it")],
         size=13, anchor="start")
    rich(S, gx - 40, yb + 22, [("T", "it"), ("t,i,a", "sub"), (": after ", "sf"), ("t", "it"),
                               (" steps cell ", "sf"), ("i", "it"), (" holds the symbol ", "sf"), ("a", "it")],
         size=13, anchor="start")
    xa = gx + len(cols) * cw + 12
    rich(S, xa, yw + 2, [("each cell of row ", "sf"), ("t", "it")], size=12, anchor="start", color="var(--hi)")
    rich(S, xa, yw + 18, [("is determined by the", "sf")], size=12, anchor="start", color="var(--hi)")
    rich(S, xa, yw + 34, [("three cells above it", "sf")], size=12, anchor="start", color="var(--hi)")
    rich(S, xa, yw + 50, [("in row ", "sf"), ("t", "it"), (" − 1", "rm")], size=12, anchor="start", color="var(--hi)")
    save("ch09-tableau", S.figure(
        "<strong>The Cook–Levin tableau.</strong> Row <i>t</i> is the configuration after <i>t</i> steps of the "
        "verifier <i>M</i>; the head starts on cell 1 in state <i>start</i>. Row 0 is fixed except for the advice "
        "cells, which the satisfying assignment chooses. Each entry of row <i>t</i> is determined by the three "
        "entries above it, so every transition constraint has constant size; with <i>O</i>(<i>N</i>) rows and "
        "columns, the formula has size <i>O</i>(<i>N</i><sup>2</sup>).",
        alt="grid of time steps by tape cells: row 0 holds a sentinel, the input 0 1, a blank, unknown advice cells "
            "and a sentinel; a highlighted window shows three cells of one row determining one cell of the next"))


if __name__ == "__main__":
    main()
