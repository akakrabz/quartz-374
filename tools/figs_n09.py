#!/usr/bin/env python3
"""Figures for lecture note 9 (Amortized analysis). Writes tools/figs/n09-<name>.html; then run tools/assemble.py on
content/4-lecture-notes/09-amortized-analysis.md. Everything drawn is computed here from minimal re-implementations of
the note's algorithms; tools/checks/n09.py re-checks the HTML (data-* attributes and text) independently."""
import os

from figlib import SVG, MONO

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")
os.makedirs(OUT, exist_ok=True)


def save(name, html):
    with open(os.path.join(OUT, name + ".html"), "w", encoding="utf-8") as f:
        f.write(html + "\n")
    print("wrote", name)


# ------------------------------------------------------------------ charging scheme for the binary counter
def increment(B):
    flips, i = [], 0
    while B[i] == 1:
        B[i] = 0
        flips.append((i, 0))
        i += 1
    B[i] = 1
    flips.append((i, 1))
    return flips


K = 16
B = [0] * 10
stacks = [increment(B) for _ in range(K)]
assert sum(len(s) for s in stacks) == 2 * K - 1

bw, bh, gap = 18, 13, 32
x0, ybase = 26, 112
S = SVG(x0 + K * gap + 4, 150, font_size=12)


def bx(k):              # left x of stack k (1-based)
    return x0 + (k - 1) * gap


def by(j):              # top y of block at height j
    return ybase - (j + 1) * bh


for k, fl in enumerate(stacks, start=1):
    for (j, v) in fl:
        x, y = bx(k), by(j)
        if v == 1:
            S.add(f'<rect data-b="set" x="{x}" y="{y}" width="{bw}" height="{bh}" fill="var(--paper)" '
                  f'stroke="currentColor" stroke-width="1.2"/>')
        else:
            S.add(f'<rect data-b="clear" x="{x}" y="{y}" width="{bw}" height="{bh}" fill="var(--muted)" '
                  f'fill-opacity="0.55" stroke="currentColor" stroke-width="1.2"/>')
    S.text(bx(k) + bw / 2, ybase + 12, str(k), size=11)
# charge arrows: shaded block at height j in stack k -> white block at height j in stack k - 2^j
for k, fl in enumerate(stacks, start=1):
    for (j, v) in fl:
        if v == 0:
            src = k - 2 ** j
            assert stacks[src - 1][-1] == (j, 1)
            assert all(len(stacks[m - 1]) <= j for m in range(src + 1, k))
            y = by(j) + bh / 2
            S.add(f'<line data-b="charge" x1="{bx(k) + 4}" y1="{y}" x2="{bx(src) + bw + 2}" y2="{y}" '
                  f'stroke="var(--hi)" stroke-width="1.4" marker-end="url(#ARR)"/>')
S.text(x0 + K * gap / 2, 140, "Increment number k", size=11, color="var(--muted)")
cap = ("<strong>Charging scheme for a binary counter.</strong> Increment <i>k</i> is a stack of blocks, one per bit "
       "flip, with the flip of <i>B</i>[0] at the bottom: the white block on top sets a bit from 0 to 1, the shaded "
       "blocks clear bits from 1 to 0. Each shaded block at height <i>j</i> is charged (arrow) to the white block at "
       "height <i>j</i> in stack <i>k</i> − 2<sup><i>j</i></sup>, the increment that set that bit. After the move every "
       "stack has at most two blocks: 16 increments, 31 = 2·16 − 1 flips.")
save("n09-charging", S.figure(cap, alt="Stacks of bit flips for increments 1 to 16 with charging arrows"))


# ------------------------------------------------------------------ Ehrlich's loopless Gray code, n = 4
def ehrlich(n, steps):
    G, F = [0] * n, list(range(n + 1))
    out = [(G[:], F[:], None)]
    for _ in range(steps):
        j = F[0]
        F[0] = 0
        if j == n:
            G[n - 1] ^= 1
            flipped = n - 1
        else:
            G[j] ^= 1
            F[j] = F[j + 1]
            F[j + 1] = j + 1
            flipped = j
        out.append((G[:], F[:], flipped))
    return out


n = 4
seq = ehrlich(n, 15)
for k, (G, F, fl) in enumerate(seq):
    assert sum(b << i for i, b in enumerate(G)) == k ^ (k >> 1) and F[n] == n
cw, ch, colw = 22, 18, 33
left = 62
top = 30
G2 = SVG(left + 16 * colw + 6, top + 4 * ch + 66, font_size=12)
G2.text(left - 10, top - 14, "k", anchor="end", size=11, color="var(--muted)")
for i in range(n):
    G2.text(left - 10, top + (n - 1 - i) * ch + ch / 2, f"G[{i}]", anchor="end", size=11, color="var(--muted)",
            font=MONO)
yb = top + n * ch + 16
yf = yb + 20
G2.text(left - 10, yb, "binary", anchor="end", size=11, color="var(--muted)")
G2.text(left - 10, yf, "F[3..0]", anchor="end", size=11, color="var(--muted)", font=MONO)
for k, (G, F, fl) in enumerate(seq):
    cx = left + k * colw + (colw - cw) / 2
    G2.text(cx + cw / 2, top - 14, str(k), size=11)
    for i in range(n):
        y = top + (n - 1 - i) * ch
        hot = (fl == i)
        extra = f' data-flip="{k:x}{i}"' if hot else ""
        fill = 'fill="var(--hi)" fill-opacity="0.22"' if hot else 'fill="none"'
        stroke = "var(--hi)" if hot else "currentColor"
        sw = 1.8 if hot else 0.8
        G2.add(f'<rect data-g="{k:x}{i}{G[i]}"{extra} x="{cx}" y="{y}" width="{cw}" height="{ch}" {fill} '
               f'stroke="{stroke}" stroke-width="{sw}"/>')
        G2.text(cx + cw / 2, y + ch / 2 + 1, str(G[i]), size=12, font=MONO,
                color="var(--hi)" if hot else "currentColor", weight="bold" if hot else None)
    G2.text(cx + cw / 2, yb, format(k, "04b"), size=9.5, font=MONO, color="var(--muted)")
    G2.text(cx + cw / 2, yf, "".join(str(F[i]) for i in reversed(range(n))), size=10, font=MONO)
cap = ("<strong>Ehrlich’s loopless Gray counter, <i>n</i> = 4.</strong> Column <i>k</i> is the state after "
       "<i>k</i> increments: the Gray code <i>G</i> (with <i>G</i>[3] on top), then the binary count <i>k</i> and the "
       "focus array <i>F</i>[3..0] (<i>F</i>[4] = 4 throughout). The highlighted cell is the one bit the <i>k</i>-th "
       "increment flipped — always the bit that a binary counter would set from 0 to 1, and always <i>F</i>[0] of "
       "the previous column.")
save("n09-gray", G2.figure(cap, alt="Sixteen states of Ehrlich's Gray code counter with focus array"))
