#!/usr/bin/env python3
"""Figures for Chapter 1 (strings). Writes tools/figs/<name>.html; then run tools/assemble.py."""
import os
from figlib import SVG, Tape, MONO, SERIF_IT, SANS

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")
os.makedirs(OUT, exist_ok=True)


def save(name, html):
    with open(os.path.join(OUT, name + ".html"), "w", encoding="utf-8") as f:
        f.write(html + "\n")
    print("wrote", name)


def cons_cell(S, x, y, sym, w=56, h=30, color="currentColor", fill="none", fill_opacity=None):
    """A pair (a, x): the symbol on the left, a pointer to the rest of the string on the right."""
    S.rect(x, y, w, h, rx=3, stroke=color, fill=fill, fill_opacity=fill_opacity, width=1.4)
    S.line(x + w / 2, y, x + w / 2, y + h, color=color, width=1.2)
    S.text(x + w / 4, y + h / 2 + 1, sym, size=15, font=MONO, color=color)
    S.circle(x + 3 * w / 4, y + h / 2, 3, stroke=color, fill=color)


def pointer(S, x1, y, x2, color="currentColor"):
    S.line(x1, y, x2 - 2, y, color=color, width=1.4, arrow=True)


def bracket(S, x1, x2, y, label, color="currentColor", down=True, size=13, italic=True, font=SERIF_IT, gap=15):
    """Square bracket under (down=True) or over a range of cells, with a label."""
    d = 6 if down else -6
    S.path(f"M{x1},{y} L{x1},{y + d} L{x2},{y + d} L{x2},{y}", color=color, width=1.3)
    S.text((x1 + x2) / 2, y + d + (gap if down else -gap + 2), label, size=size, font=font, italic=italic, color=color)


# ---------------------------------------------------------------- STRING as nested pairs
S = SVG(600, 132)
S.text(300, 20, "STRING = (S, (T, (R, (I, (N, (G, ε))))))", size=15, font=MONO)
word = "STRING"
x0, y0, pitch = 24, 50, 86
for i, a in enumerate(word):
    x = x0 + i * pitch
    cons_cell(S, x, y0, a)
    nxt = x + pitch if i < len(word) - 1 else x + pitch - 10
    pointer(S, x + 42, y0 + 15, nxt)
    S.text(x + 28, y0 + 52, word[i:], size=12, font=MONO, color="var(--muted)")
S.text(x0 + len(word) * pitch - 2, y0 + 16, "ε", size=17, font=SERIF_IT, italic=True)
S.text(x0 + len(word) * pitch - 2, y0 + 52, "ε", size=13, font=SERIF_IT, italic=True, color="var(--muted)")
save("ch01-string-pairs", S.figure(
    "<strong>A string is a symbol paired with a (shorter) string.</strong> Each box is one pair (<i>a</i>, <i>x</i>): "
    "the symbol on the left, the rest of the string on the right. The grey label under each box is the string that "
    "starts there; the last pair points to the empty string ε. The length is the number of boxes.",
    alt="the string STRING drawn as six linked pairs ending in epsilon"))

# ---------------------------------------------------------------- concatenation copies its left argument
S = SVG(620, 196)
pitch = 74
# top row: w = NOW
S.text(30, 36, "w", size=16, font=SERIF_IT, italic=True)
for i, a in enumerate("NOW"):
    x = 60 + i * pitch
    cons_cell(S, x, 21, a)
    pointer(S, x + 42, 36, x + pitch if i < 2 else x + pitch - 12)
S.text(60 + 3 * pitch - 4, 37, "ε", size=17, font=SERIF_IT, italic=True)
# bottom row: copies of N, O, W (highlighted) followed by z = HERE itself
yb = 128
S.text(30, yb + 15, "w•z", size=15, font=SERIF_IT, italic=True)
for i, a in enumerate("NOW"):
    x = 60 + i * pitch
    cons_cell(S, x, yb, a, color="var(--hi)")
    pointer(S, x + 42, yb + 15, x + pitch, color="var(--hi)")
    S.line(x + 14, 54, x + 14, yb - 4, dash="4 4", arrow=True, color="var(--hi)", width=1.2)
for i, a in enumerate("HERE"):
    x = 60 + (3 + i) * pitch
    cons_cell(S, x, yb, a)
    pointer(S, x + 42, yb + 15, x + pitch if i < 3 else x + pitch - 12)
S.text(60 + 7 * pitch - 4, yb + 16, "ε", size=17, font=SERIF_IT, italic=True)
S.text(60 + 2 * pitch + 30, 91, "one new pair per symbol of w", size=12, anchor="start", color="var(--hi)")
bracket(S, 60 + 3 * pitch, 60 + 7 * pitch - 18, yb + 38, "z = HERE, reused unchanged", size=12, italic=False, font=SANS)
save("ch01-concat-copy", S.figure(
    "<strong>Concatenation recurses on its left argument.</strong> Computing NOW • HERE peels N, O, W off the left "
    "argument one at a time and rebuilds a pair for each (red); when the left argument has shrunk to ε, the base case "
    "returns <i>z</i> = HERE as it is. The right argument is never taken apart, so induction on <i>w</i> is the natural "
    "way to prove things about <i>w</i> • <i>z</i>.",
    alt="the pairs N, O, W are copied and the last copy points to the unchanged string HERE"))

# ---------------------------------------------------------------- two ways to take a string apart
T = Tape(560, 156, font_size=15)
cell = 30
xs = 210
word = "STRING"
rows = [(14, "standard:", "w = a·x", [(0, 1, "a"), (1, 6, "x")], "|x| = |w| − 1"),
        (92, "§1.4:", "w = u•v", [(0, 3, "u"), (3, 6, "v")], "1 ≤ |u|, |v| < |w|")]
for y, tag, eq, parts, note in rows:
    T.text(20, y + cell / 2, tag, size=13, anchor="start", color="var(--muted)")
    T.text(92, y + cell / 2, eq, size=16, anchor="start", font=SERIF_IT, italic=True)
    T.cells(xs, y, list(word), cell=cell, dots=False)
    for (i, j, lab) in parts:
        bracket(T, xs + i * cell + 3, xs + j * cell - 3, y + cell + 4, lab, size=15)
    T.text(xs + 6 * cell + 22, y + cell / 2, note, size=13, anchor="start", font=SANS, color="var(--muted)")
save("ch01-decompositions", T.figure(
    "<strong>Two ways to take a non-empty string apart.</strong> The standard proof peels off the first symbol, so "
    "the induction hypothesis applies to <i>x</i>. The proof of §1.4 splits <i>w</i> anywhere into two non-empty "
    "pieces (here after STR); both are shorter than <i>w</i>, so the hypothesis applies to each. That split needs "
    "two base cases: <i>w</i> = ε and <i>w</i> = a single symbol.",
    alt="the string STRING split as S and TRING, and as STR and ING"))

# ---------------------------------------------------------------- substrings, prefixes, suffixes, subsequences
T = Tape(560, 222, font_size=16)
cell = 36
xa = 136
# HEADACHE with indices
ya = 30
T.text(xa - 16, ya + cell / 2, "w", size=17, anchor="end", font=SERIF_IT, italic=True)
T.cells(xa, ya, list("HEADACHE"), cell=cell, dots=False, highlight=())
for i in range(8):
    T.text(xa + i * cell + cell / 2, ya - 11, str(i + 1), size=11, color="var(--muted)")
bracket(T, xa + 3, xa + 2 * cell - 3, ya + cell + 4, "prefix HE", size=13, italic=False, font=SANS, gap=16)
bracket(T, xa + 2 * cell + 3, xa + 5 * cell - 3, ya + cell + 4, "w[3..5] = ADA", size=13, italic=False, font=SANS,
        gap=16)
bracket(T, xa + 6 * cell + 3, xa + 8 * cell - 3, ya + cell + 4, "suffix HE", size=13, italic=False, font=SANS, gap=16)
# MEATBALL with the subsequence METAL highlighted
yb = 140
T.text(xa - 16, yb + cell / 2, "w", size=17, anchor="end", font=SERIF_IT, italic=True)
pos = [0, 1, 3, 5, 6]  # 0-based positions of M, E, T, A, L
T.cells(xa, yb, list("MEATBALL"), cell=cell, dots=False, highlight=pos)
for i in range(8):
    T.text(xa + i * cell + cell / 2, yb - 11, str(i + 1), size=11, color="var(--muted)")
for k, p in enumerate(pos):
    T.add(f'<rect x="{xa + p * cell + 2}" y="{yb + 2}" width="{cell - 4}" height="{cell - 4}" fill="none" '
          f'stroke="var(--hi)" stroke-width="1.6"/>')
T.text(xa + 4 * cell, yb + cell + 22, "METAL = symbols 1, 2, 4, 6, 7: a subsequence, not a substring",
       size=13, color="var(--hi)")
save("ch01-substrings", T.figure(
    "<strong>Substrings are contiguous; subsequences need not be.</strong> In HEADACHE, HE is both a proper prefix "
    "(<i>w</i>[1..2]) and a proper suffix (<i>w</i>[7..8]), and <i>w</i>[3..5] = ADA is a substring. Deleting "
    "A, B and one L from MEATBALL leaves METAL, so METAL is a subsequence of MEATBALL — but its symbols are not "
    "adjacent, and METAL is not a substring.",
    alt="the strings HEADACHE and MEATBALL in indexed cells, with a prefix, suffix, substring and subsequence marked"))
