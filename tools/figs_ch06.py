#!/usr/bin/env python3
"""Figures for Chapter 6 (Turing machines). Writes tools/figs/<name>.html; then run tools/assemble.py."""
import os
from figlib import Automaton, SVG, Tape, MONO, SERIF_IT, SANS

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")
os.makedirs(OUT, exist_ok=True)


def save(name, html):
    with open(os.path.join(OUT, name + ".html"), "w", encoding="utf-8") as f:
        f.write(html + "\n")
    print("wrote", name)


# ---------------------------------------------------------------- a configuration: (reset, #0x1x0, 3)
T = Tape(560, 150, font_size=17)
x0, y0, cell = 40, 34, 34
syms = ["#", "0", "x", "1", "x", "0", "□", "□"]
T.cells(x0, y0, syms, cell=cell, head=3)
for i in range(len(syms)):
    T.text(x0 + i * cell + cell / 2, y0 - 12, str(i), size=11, color="var(--muted)")
# finite control under the head
hx = x0 + 3 * cell + cell / 2
T.rect(hx - 32, y0 + cell + 31, 64, 26, rx=13, stroke="var(--hi)", width=1.5)
T.text(hx, y0 + cell + 44, "reset", size=16, font=SERIF_IT, italic=True, color="var(--hi)")
T.text(445, 52, "configuration", size=13, color="var(--muted)")
T.add(f'<text x="445" y="80" text-anchor="middle" dominant-baseline="central" fill="currentColor" '
      f'style="font-size:15px;font-family:{MONO};">(<tspan style="font-family:{SERIF_IT};font-style:italic;'
      f'font-size:16px">reset</tspan>, #0x1x0, 3)</text>')
save("ch06-configuration", T.figure(
    "<strong>A configuration.</strong> The machine of §6.3 on input 001100, one round in: state <i>reset</i>, "
    "tape <code>#0x1x0</code> followed by infinitely many blanks, head on cell 3. Cells are numbered from 0; a move left "
    "from cell 0 crashes the machine.",
    alt="tape with cells # 0 x 1 x 0 blank blank, the head in state reset on cell 3"))

# ---------------------------------------------------------------- the machine for {0^n 1^n 0^n}
A = Automaton(680, 400, r=16, font_size=14)


def st(name, x, y, **kw):
    A.state(name, x, y, shape="rounded", w=14 + 8 * len(name), **kw)


st("start", 65, 80, start="left")
st("block1", 185, 80)
st("block2", 305, 80)
st("block3", 425, 80)
st("rewind", 555, 80)
st("accept", 80, 200, accepting=True)
st("verify", 240, 200)
st("mark0", 400, 200)
st("seek1", 555, 200)
st("reset", 400, 315)
st("seek0", 555, 315)
A.edge("start", "block1", "0/#,+1")
A.edge("start", "accept", "□;+1", label_side=-1)
A.loop("block1", "0;+1", "above", size=0.8)
A.edge("block1", "block2", "1;+1")
A.loop("block2", "1;+1", "above", size=0.8)
A.edge("block2", "block3", "0;+1")
A.loop("block3", "0;+1", "above", size=0.8)
A.edge("block3", "rewind", "□;−1")
A.loop("rewind", "0,1;−1", "above", size=0.8)
A.edge("rewind", "seek1", "#;+1")
A.loop("seek1", "", "right", size=0.8)
A.text(672, 200, "0,x;+1", size=13, font=MONO, halo=True, anchor="end")
A.edge("seek1", "seek0", "1/x,+1", label_side=-1, label_dist=27)
A.loop("seek0", "", "right", size=0.8)
A.text(672, 315, "1,x;+1", size=13, font=MONO, halo=True, anchor="end")
A.edge("seek0", "reset", "0/x,−1", label_side=-1)
A.loop("reset", "0,1,x;−1", "below", size=0.8)
A.edge("reset", "mark0", "#;+1", label_dist=18)
A.edge("mark0", "seek1", "0/#,+1")
A.edge("mark0", "verify", "x;+1", label_side=-1)
A.loop("verify", "x;+1", "below", size=0.8)
A.edge("verify", "accept", "□;+1", label_side=-1)
A.text(110, 375, "missing transitions go to reject", size=12, color="var(--muted)")
save("ch06-zoz-machine", A.figure(
    "<strong>A Turing machine that decides {0<sup><i>n</i></sup>1<sup><i>n</i></sup>0<sup><i>n</i></sup>}.</strong> "
    "Top row: one pass checks the format, then <i>rewind</i> returns to the # in cell 0. The cycle "
    "<i>seek1</i> → <i>seek0</i> → <i>reset</i> → <i>mark0</i> marks one symbol of each block per round. "
    "A label <code>a/b,±1</code> means read <code>a</code>, write <code>b</code>, move; a label like "
    "<code>0,x;+1</code> means read 0 or x, leave it unchanged, move.",
    alt="state diagram with eleven states: start, block1, block2, block3, rewind, seek1, seek0, reset, mark0, verify, accept"))

# ---------------------------------------------------------------- removing a stay-put move
A = Automaton(640, 112, r=17, font_size=14)
A.state("p", 55, 44)
A.state("q", 195, 44)
A.edge("p", "q", "a/b,0")
A.text(125, 92, "in M: stay put", size=12, color="var(--muted)")
A.text(262, 46, "⟹", size=26)
A.state("p0", 345, 44, label="(p,0)", shape="rounded", w=50, italic=False, font=SERIF_IT)
A.state("q1", 465, 44, label="(q,1)", shape="rounded", w=50, italic=False, font=SERIF_IT, hi=True)
A.state("q0", 585, 44, label="(q,0)", shape="rounded", w=50, italic=False, font=SERIF_IT)
A.edge("p0", "q1", "a/b,+1")
A.edge("q1", "q0", "c;−1")
A.text(465, 92, "in M′: step right, then step back left", size=12, color="var(--muted)")
save("ch06-stay-put", A.figure(
    "<strong>Removing a stay-put move.</strong> A transition δ(<i>p</i>, <i>a</i>) = (<i>q</i>, <i>b</i>, 0) "
    "of <i>M</i> becomes a move right into the new state (<i>q</i>, 1), which moves back left without changing "
    "the tape, whatever symbol <i>c</i> it reads. Transitions that move ±1 are copied between the states "
    "(<i>p</i>, 0) and (<i>q</i>, 0). Each stay-put step of <i>M</i> costs <i>M</i>′ one extra step.",
    alt="a stay-put transition from p to q replaced by two transitions through the state (q,1)"))

# ---------------------------------------------------------------- two tapes as four tracks
S = Tape(640, 200, font_size=15)
c = 26
t1, h1 = ["a", "b", "b", "a", "□"], 1
t2, h2 = ["1", "0", "0", "1", "1", "□"], 4
S.text(30, 41, "tape 1", size=12, color="var(--muted)")
S.cells(62, 28, t1, cell=c, head=h1)
S.text(30, 121, "tape 2", size=12, color="var(--muted)")
S.cells(62, 108, t2, cell=c, head=h2)
S.text(305, 100, "⟹", size=26)
# one tape, four tracks
X0, Y0, cw, rh = 400, 46, 28, 24
labels = ["tape 1", "head 1", "tape 2", "head 2"]
n = 7
for r, lab in enumerate(labels):
    S.text(X0 - 8, Y0 + r * rh + rh / 2, lab, size=11, color="var(--muted)", anchor="end")
for i in range(n):
    S.rect(X0 + i * cw, Y0, cw, 4 * rh, width=1.2)
    for r in range(1, 4):
        S.line(X0 + i * cw, Y0 + r * rh, X0 + (i + 1) * cw, Y0 + r * rh, width=0.6, opacity=0.5)
    vals = [t1[i] if i < len(t1) else "□", "▲" if i == h1 else "",
            t2[i] if i < len(t2) else "□", "▲" if i == h2 else ""]
    for r, v in enumerate(vals):
        if not v:
            continue
        if v == "▲":
            S.text(X0 + i * cw + cw / 2, Y0 + r * rh + rh / 2 + 1, v, size=12, color="var(--hi)")
        else:
            S.text(X0 + i * cw + cw / 2, Y0 + r * rh + rh / 2 + 1, v, size=14,
                   font=SERIF_IT if v == "□" else MONO)
S.text(X0 + n * cw + 14, Y0 + 2 * rh, "⋯", size=15)
S.text(X0 + n * cw / 2, Y0 + 4 * rh + 22, "one tape over a 4-track alphabet", size=12, color="var(--muted)")
save("ch06-two-tapes", S.figure(
    "<strong>Two tapes on one.</strong> Each cell of the single tape holds four things: the cell of tape 1, "
    "a mark if head 1 is there, the cell of tape 2, and a mark if head 2 is there. One step of the two-tape "
    "machine becomes a sweep across the used part of the tape to read the marked symbols, and a sweep back to "
    "write them and move the marks.",
    alt="two tapes with their heads, and the same information on one tape with four tracks"))
