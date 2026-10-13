#!/usr/bin/env python3
"""Figures for Chapter 8 (universal models). Writes tools/figs/<name>.html; then run tools/assemble.py."""
import os
from figlib import SVG, MONO, SERIF_IT

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")
os.makedirs(OUT, exist_ok=True)


def save(name, html):
    with open(os.path.join(OUT, name + ".html"), "w", encoding="utf-8") as f:
        f.write(html + "\n")
    print("wrote", name)


def sym(S, x, y, s, size=16):
    S.text(x, y, s, size=size, font=SERIF_IT if s == "□" else MONO)


# ---------------------------------------------------------------- a tape is two stacks
S = SVG(480, 262, font_size=16)
x0, y0, c = 70, 52, 34
tape = ["#", "0", "x", "1", "x", "0", "□", "□"]
head = 3
for i, a in enumerate(tape):
    S.rect(x0 + i * c, y0, c, c, width=1.2, fill="var(--accent)" if i == head else "none",
           fill_opacity=0.12 if i == head else None)
    sym(S, x0 + i * c + c / 2, y0 + c / 2 + 1, a)
S.text(x0 + len(tape) * c + 14, y0 + c / 2, "⋯", size=16)
hx = x0 + head * c + c / 2
S.text(hx, 13, "reset", size=15, font=SERIF_IT, italic=True, color="var(--hi)")
S.line(hx, 22, hx, y0 - 4, arrow=True, color="var(--hi)", width=1.8)
cut = x0 + head * c
S.line(cut, y0 - 10, cut, y0 + c + 14, color="var(--hi)", width=1.4, dash="4 3")
S.text((x0 + cut) / 2, y0 + c + 16, "left of the head", size=12, color="var(--muted)")
S.text(cut + 3 * c / 2 + 34, y0 + c + 16, "head cell and to its right", size=12, color="var(--muted)")


def stack(S, cx, items, label):
    """items listed top first; open-topped box"""
    top = 132
    n = len(items)
    for k, a in enumerate(items):
        S.rect(cx - c / 2, top + k * 26, c, 26, width=1.0, fill="var(--accent)" if k == 0 else "none",
               fill_opacity=0.12 if k == 0 else None)
        sym(S, cx, top + k * 26 + 14, a, size=15)
    bot = top + n * 26
    S.path(f"M{cx - c / 2 - 5},{top - 6} L{cx - c / 2 - 5},{bot + 5} L{cx + c / 2 + 5},{bot + 5} L{cx + c / 2 + 5},{top - 6}",
           width=1.8)
    S.text(cx, bot + 24, label, size=13, color="var(--muted)")
    return top


t = stack(S, 125, ["x", "0", "#"], "left stack")
S.text(125 - c / 2 - 12, t + 13, "top", size=11, color="var(--muted)", anchor="end")
t = stack(S, 305, ["1", "x", "0"], "right stack")
S.text(305 + c / 2 + 12, t + 13, "top = head cell", size=11, color="var(--muted)", anchor="start")
save("ch08-two-stacks", S.figure(
    "<strong>A tape is two stacks.</strong> Cut the tape at the head. The left stack holds the cells left of the "
    "head, nearest cell on top; the right stack holds the head cell and everything to its right, head cell on top "
    "(an empty right stack reads as a blank). A move right pops the right stack and pushes the written symbol onto "
    "the left stack. A move left pops the right stack, pushes the written symbol back onto it, and then moves the top "
    "of the left stack over to the right stack.",
    alt="the tape #0x1x0 cut at the head into a left stack x,0,# and a right stack 1,x,0"))

# ---------------------------------------------------------------- PCP: the solution c b c a
S = SVG(620, 176, font_size=15)
dom = {"a": ("0", "100"), "b": ("01", "00"), "c": ("110", "11")}
for k, (name, (top, bot)) in enumerate(dom.items()):
    x = 22 + k * 64
    S.rect(x, 40, 54, 70, rx=5, width=1.4)
    S.line(x, 75, x + 54, 75, width=1.0, opacity=0.6)
    S.text(x + 27, 58, top, size=15, font=MONO)
    S.text(x + 27, 93, bot, size=15, font=MONO)
    S.text(x + 27, 128, name, size=15, font=SERIF_IT, italic=True)
S.text(108, 160, "the three dominoes", size=12, color="var(--muted)")
seq = "cbca"
top = "".join(dom[d][0] for d in seq)
bot = "".join(dom[d][1] for d in seq)
assert top == bot == "110011100"
X0, cw = 300, 26
yt, yb = 66, 108
for i, ch in enumerate(top):
    S.text(X0 + i * cw + cw / 2, yt, ch, size=16, font=MONO)
    S.text(X0 + i * cw + cw / 2, yb, ch, size=16, font=MONO)
pt = pb = 0
for k, d in enumerate(seq):
    lt, lb = len(dom[d][0]), len(dom[d][1])
    shade = "var(--accent)" if k % 2 == 0 else "var(--accent2)"
    S.rect(X0 + pt * cw + 2, yt - 15, lt * cw - 4, 30, rx=4, fill=shade, fill_opacity=0.12, width=1.2)
    S.rect(X0 + pb * cw + 2, yb - 15, lb * cw - 4, 30, rx=4, fill=shade, fill_opacity=0.12, width=1.2)
    S.text(X0 + (pt + lt / 2) * cw, yt - 28, d, size=15, font=SERIF_IT, italic=True)
    S.text(X0 + (pb + lb / 2) * cw, yb + 28, d, size=15, font=SERIF_IT, italic=True)
    pt, pb = pt + lt, pb + lb
S.text(X0 - 14, yt, "top", size=12, color="var(--muted)", anchor="end")
S.text(X0 - 14, yb, "bottom", size=12, color="var(--muted)", anchor="end")
S.text(X0 + 9 * cw / 2, 160, "c, b, c, a: both rows spell 110011100", size=12, color="var(--muted)")
save("ch08-pcp", S.figure(
    "<strong>A solution of a correspondence instance.</strong> With the dominoes <i>a</i> = (0 / 100), "
    "<i>b</i> = (01 / 00) and <i>c</i> = (110 / 11), the sequence <i>c</i>, <i>b</i>, <i>c</i>, <i>a</i> spells "
    "<code>110011100</code> on both rows. The boxes show where each domino’s top and bottom strings land: the "
    "seams do not line up until the very end, which is what makes the problem hard.",
    alt="dominoes c b c a laid out so that top and bottom rows both read 110011100"))
