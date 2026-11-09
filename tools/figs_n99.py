#!/usr/bin/env python3
"""Figures for the lecture-notes page 4-lecture-notes/99-solving-recurrences.md (Erickson, Appendix II).
Writes tools/figs/n99-<name>.html; then run tools/assemble.py with the page.
The numbers in the figure are checked in tools/checks/n99.py (§3 lopsided trees)."""
import os
from figlib import SVG, SANS, SERIF_IT

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")


def save(name, html):
    with open(os.path.join(OUT, name + ".html"), "w", encoding="utf-8") as f:
        f.write(html + "\n")
    print("wrote", name)


def sub(base, s, tail=""):
    """base with subscript s, then tail (raw SVG tspans)."""
    return f'{base}<tspan dy="4" style="font-size:9.5px">{s}</tspan><tspan dy="-4">{tail}</tspan>'


def panel(S, x0, title, labels, sums_top, sum_more, sum_part, shallow, deep, verdict1, verdict2):
    """One lopsided recursion tree: three drawn levels, then the outline of the rest of the tree.
    labels: three lists of node labels (1, 2, 4 nodes); sums_top: three level sums."""
    tw = 222                       # width of the tree area
    sx = x0 + tw + 18              # level-sum column
    S.text(x0 + 4, 16, title, anchor="start", size=13, weight=600)
    S.text(sx, 38, "level sum", anchor="start", size=11, color="var(--muted)")
    ys = [56, 88, 120]
    xs = [[x0 + tw * (i + 0.5) / k for i in range(k)] for k in (1, 2, 4)]
    widths = [28, 40, 44]
    # the rest of the tree: complete part (down to the shallowest leaf), then the ragged part
    top, ysh, ydp = 134, 196, 262
    xl, xr = x0 + 6, x0 + tw - 6
    # x of the right edge at the depth of the shallowest leaf (the right edge runs (xr-14, top) -> (xr, ydp))
    xr_sh = xr - 14 + 14 * (ysh - top) / (ydp - top)
    S.add(f'<path d="M{xl + 14},{top} L{xl},{ysh} L{xr_sh:.1f},{ysh} L{xr - 14},{top} Z" fill="var(--accent)" '
          f'fill-opacity="0.16" stroke="none"/>')
    S.add(f'<path d="M{xl},{ysh} L{xr - 30},{ydp} L{xr},{ydp} L{xr_sh:.1f},{ysh} Z" fill="var(--muted)" '
          f'fill-opacity="0.13" stroke="none"/>')
    S.path(f"M{xl + 14},{top} L{xl},{ysh} L{xr - 30},{ydp} L{xr},{ydp} L{xr - 14},{top}",
           color="var(--accent)", width=1.2)
    S.line(xl - 4, ysh, sx + 58, ysh, color="var(--hi)", width=1.2, dash="4 3")
    S.line(xr, ydp, sx + 58, ydp, color="var(--muted)", width=1.0, dash="2 3")
    S.text(x0 + tw / 2, 158, "complete levels", size=12, color="var(--accent)")
    S.text(x0 + tw / 2 + 52, 236, "ragged levels", size=12, color="var(--muted)")
    S.text(x0 + tw / 2 + 4, ysh - 11, shallow, size=11.5, color="var(--hi)", raw=True, halo=True)
    S.text(xr, ydp + 14, deep, anchor="end", size=11.5, color="var(--muted)", raw=True)
    # edges and nodes
    for d in (1, 2):
        for i, x in enumerate(xs[d]):
            px = xs[d - 1][i // 2]
            S.line(px, ys[d - 1] + 9, x, ys[d] - 9, width=1.1, opacity=0.55)
    for i, x in enumerate(xs[2]):
        S.line(x, ys[2] + 9, x - 7, top + 1, width=1.0, opacity=0.35)
        S.line(x, ys[2] + 9, x + 7, top + 1, width=1.0, opacity=0.35)
    for d in range(3):
        w = widths[d]
        for x, t in zip(xs[d], labels[d]):
            S.rect(x - w / 2, ys[d] - 9, w, 18, rx=4, stroke="currentColor", fill="var(--paper)", width=1.1)
            S.text(x, ys[d] + 0.5, t, size=12, font=SERIF_IT, italic=True)
    for y, s in zip(ys, sums_top):
        S.text(sx, y + 0.5, s, anchor="start", size=12.5, font=SERIF_IT, italic=True, color="var(--accent)")
    S.text(sx, 162, sum_more, anchor="start", size=12.5, font=SERIF_IT, italic=True, color="var(--accent)", raw=True)
    S.text(sx, 232, sum_part, anchor="start", size=12.5, font=SERIF_IT, italic=True, color="var(--muted)", raw=True)
    S.text(x0 + 4, 298, verdict1, anchor="start", size=12, raw=True)
    S.text(x0 + 4, 317, verdict2, anchor="start", size=12, weight=600, color="var(--hi)", raw=True)


def lopsided_fig():
    W, H = 640, 328
    S = SVG(W, H, font_size=13)
    panel(S, 6, "T(n) = T(n/4) + T(3n/4) + n",
          [["n"], ["n/4", "3n/4"], ["n/16", "3n/16", "3n/16", "9n/16"]],
          ["n", "n", "n"], "n each", "&lt; n each",
          "depth " + sub("log", "4", " n: shallowest leaf"),
          "depth " + sub("log", "4/3", " n: deepest"),
          "n " + sub("log", "4", " n") + " ≤ T(n) ≤ n(" + sub("log", "4/3", " n") + " + 1)",
          "so T(n) = Θ(n log n)")
    S.line(321, 30, 321, 256, color="var(--muted)", width=0.8, dash="2 4")
    panel(S, 330, "T(n) = T(n/2) + T(n/4) + 1",
          [["n"], ["n/2", "n/4"], ["n/4", "n/8", "n/8", "n/16"]],
          ["1", "2", "4"], '2<tspan dy="-5" style="font-size:9.5px">i</tspan><tspan dy="5"> each</tspan>',
          '&lt; 2<tspan dy="-5" style="font-size:9.5px">i</tspan><tspan dy="5"> each</tspan>',
          "depth " + sub("log", "4", " n: shallowest leaf"),
          "depth " + sub("log", "2", " n: deepest"),
          "√n ≤ T(n) ≤ 2n: the levels alone do not decide",
          'T(n) = Θ(n<tspan dy="-5" style="font-size:9.5px">lg φ</tspan><tspan dy="5">) by §4 or §6</tspan>')
    return S.figure(
        "<strong>Lopsided recursion trees.</strong> With unequal pieces the leaves sit at different depths: the "
        "all-left path is the shortest, the all-right path the longest. Every level above the shallowest leaf is "
        "<em>complete</em>, and below it the levels thin out. Left (randomized quicksort’s split): complete levels sum "
        "to exactly <i>n</i> and no level exceeds <i>n</i>, so counting the complete levels gives the lower bound and "
        "extending every level to the deepest leaf gives the upper bound — both Θ(<i>n</i> log <i>n</i>). Right "
        "(ham-sandwich trees): complete levels double, so the leaves dominate, but the number of leaves is only pinned "
        "between 2<sup>log<sub>4</sub> <i>n</i></sup> = √<i>n</i> and <i>n</i>; Akra–Bazzi or the domain "
        "transformation <i>t</i>(<i>k</i>) = <i>T</i>(2<sup><i>k</i></sup>) settles it.",
        alt="two recursion trees drawn three levels deep, each continuing as a shaded region whose left side stops at "
            "depth log base 4 of n and whose right side reaches the deepest leaf; level sums shown at the right")


if __name__ == "__main__":
    save("n99-lopsided", lopsided_fig())
