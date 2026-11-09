#!/usr/bin/env python3
"""Figures for lecture note 5 (hash tables). Writes tools/figs/n05-<name>.html; then run tools/assemble.py on
content/4-lecture-notes/05-hashing.md. Every hash value, cell position and probe rank drawn here is computed below;
tools/checks/n05.py re-checks the numbers in the figure HTML."""
import math
import os
import random

import numpy as np

from figlib import SVG, SERIF_IT, MONO, esc

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")
os.makedirs(OUT, exist_ok=True)


def save(name, html):
    with open(os.path.join(OUT, name + ".html"), "w", encoding="utf-8") as f:
        f.write(html + "\n")
    print("wrote", name)


def attr_text(S, x, y, s, attr, size=13, font=MONO, color="currentColor", weight=None):
    w = f"font-weight:{weight};" if weight else ""
    S.add(f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" dominant-baseline="central" fill="{color}" '
          f'style="font-size:{size}px;font-family:{font};{w}" {attr}>{esc(s)}</text>')


# ---------------------------------------------------------------- the running example
KEYS = [12, 23, 31, 44, 58, 67, 75, 89]
P, M, A, B = 101, 8, 23, 8
h = {x: ((A * x + B) % P) % M for x in KEYS}
buckets = {i: [x for x in KEYS if h[x] == i] for i in range(M)}

# ---------------------------------------------------------------- 1. chained hash table
S = SVG(480, 228)
cw, ch, x0, y0 = 50, 30, 40, 34
for i in range(M):
    x = x0 + i * cw
    S.text(x + cw / 2, y0 - 14, str(i), size=12, color="var(--muted)")
    S.rect(x, y0, cw, ch, stroke="currentColor", width=1.3,
           fill="var(--accent)" if buckets[i] else "none", fill_opacity=0.10 if buckets[i] else None)
    if not buckets[i]:
        S.text(x + cw / 2, y0 + ch / 2 + 1, "∅", size=15, font=SERIF_IT, color="var(--muted)")
        continue
    S.circle(x + cw / 2, y0 + ch / 2, 3, stroke="currentColor", fill="currentColor")
    prev_y = y0 + ch / 2
    for d, key in enumerate(buckets[i]):
        ny = y0 + ch + 22 + d * 46
        S.line(x + cw / 2, prev_y + (3 if d == 0 else 12), x + cw / 2, ny - 1.5, arrow=True, width=1.3)
        hi = len(buckets[i]) == 3
        S.rect(x + 5, ny, cw - 10, 24, rx=5, stroke="var(--hi)" if hi else "currentColor", width=1.4)
        S.text(x + cw / 2, ny + 12.5, str(key), size=13, font=MONO, color="currentColor")
        prev_y = ny + 12
S.text(10, y0 + ch / 2, "T", size=15, font=SERIF_IT, italic=True, anchor="start")
S.text(450, 196, "n = m = 8,  α = 1", size=13, anchor="end", color="var(--muted)")
save("n05-chained", S.figure(
    "<strong>A chained hash table.</strong> The eight keys 12, 23, 31, 44, 58, 67, 75, 89 hashed into "
    "<i>m</i> = 8 slots by <i>h</i>(<i>x</i>) = ((23<i>x</i> + 8) mod 101) mod 8, a function of the universal "
    "family of §5.5.2. Each slot points to the list of the keys that hash to it. With load factor α = 1, three "
    "slots are empty and one list has three keys: random hashing is not an even spread. A search for "
    "<i>x</i> costs <i>O</i>(1 + ℓ(<i>x</i>)), where ℓ(<i>x</i>) is the length of the list <i>T</i>[<i>h</i>(<i>x</i>)].",
    alt="eight slots; slot 0 holds 23 and 75, slot 2 holds 12, 44, 67, slots 3, 5, 6 hold 89, 58, 31; "
        "slots 1, 4, 7 are empty"))

# ---------------------------------------------------------------- 2. two-level (perfect) hashing
rng = random.Random(374)
SEC = {}
for i, b in buckets.items():
    if not b:
        continue
    size = 2 * len(b) ** 2
    tries = 0
    while True:
        tries += 1
        a2, b2 = rng.randrange(1, P), rng.randrange(P)
        pos = {x: ((a2 * x + b2) % P) % size for x in b}
        if len(set(pos.values())) == len(b):
            break
    SEC[i] = (a2, b2, size, pos, tries)
print("secondary salts:", {i: (v[0], v[1], v[2], v[3], v[4]) for i, v in SEC.items()})

rowh, cell = 30, 19
W = 600
S = SVG(W, 30 + M * rowh + 6)
px, py = 36, 26
S.text(px + 20, py - 13, "T", size=14, font=SERIF_IT, italic=True)
sx = px + 80
for i in range(M):
    y = py + i * rowh
    S.text(px - 14, y + 12, str(i), size=12, color="var(--muted)")
    S.rect(px, y, 40, 24, stroke="currentColor", width=1.3,
           fill="var(--accent)" if buckets[i] else "none", fill_opacity=0.10 if buckets[i] else None)
    if not buckets[i]:
        S.text(px + 20, y + 13, "∅", size=14, font=SERIF_IT, color="var(--muted)")
        continue
    a2, b2, size, pos, _ = SEC[i]
    S.text(px + 20, y + 12.5, f"n={len(buckets[i])}", size=11, color="var(--muted)")
    S.line(px + 42, y + 12, sx - 4, y + 12, arrow=True, width=1.2)
    for c in range(size):
        cx = sx + c * cell
        S.rect(cx, y + 2, cell, 20, stroke="currentColor", width=1.0)
    for x, c in pos.items():
        cx = sx + c * cell
        S.rect(cx, y + 2, cell, 20, stroke="currentColor", width=1.0, fill="var(--accent2)", fill_opacity=0.18)
        attr_text(S, cx + cell / 2, y + 12.5, str(x), f'data-cell="{i}:{x}:{c}"', size=10.5)
    S.text(sx + size * cell + 8, y + 12, f"size {size}:  a = {a2}, b = {b2}", size=11, anchor="start",
           color="var(--muted)")
save("n05-perfect", S.figure(
    "<strong>Two-level (perfect) hashing of the same keys.</strong> The primary table is the one above "
    "(<i>m</i> = <i>n</i> = 8, Σ<i>n</i><sub><i>j</i></sub><sup>2</sup> = 16). Slot <i>j</i> gets its own table of "
    "size 2<i>n</i><sub><i>j</i></sub><sup>2</sup> with its own salt (<i>a</i>, <i>b</i>), drawn at random and "
    "redrawn until its keys land in distinct cells; key <i>x</i> goes to cell ((<i>ax</i> + <i>b</i>) mod 101) mod "
    "2<i>n</i><sub><i>j</i></sub><sup>2</sup>. A search costs two hash evaluations and one comparison, in the worst "
    "case. Total size: 8 primary cells and 8 + 18 + 2 + 2 + 2 = 32 secondary cells.",
    alt="primary table of 8 slots; slots 0 and 2 have secondary tables of size 8 and 18, slots 3, 5, 6 of size 2"))

# ---------------------------------------------------------------- 3. binary multiplicative hashing
w, l, a, x = 8, 3, 0b10110101, 0b00101011
prod = a * x
hval = ((a * x) % (1 << w)) >> (w - l)
S = SVG(520, 196)
cs = 21
right = 430


def bits_row(y, bits, label, hi_range=None, faint_range=None):
    n = len(bits)
    for k, bch in enumerate(bits):
        cx = right - (n - k) * cs
        idx = n - 1 - k   # bit index, 0 = least significant
        fill, op = "none", None
        if hi_range and hi_range[0] <= idx <= hi_range[1]:
            fill, op = "var(--hi)", 0.18
        S.rect(cx, y, cs, cs, stroke="currentColor", width=1.0, fill=fill, fill_opacity=op)
        col = "var(--muted)" if faint_range and faint_range[0] <= idx <= faint_range[1] else "currentColor"
        S.text(cx + cs / 2, y + cs / 2 + 1, bch, size=12, font=MONO, color=col)
    S.text(right + 12, y + cs / 2, label, size=14, anchor="start", font=SERIF_IT, italic=True)


bits_row(16, format(x, "08b"), f"x = {x}")
bits_row(48, format(a, "08b"), f"a = {a}")
bits_row(92, format(prod, "016b"), "a · x", hi_range=(w - l, w - 1), faint_range=(w, 2 * w - 1))
bits_row(152, format(hval, "03b"), f"h(x) = {hval}", hi_range=(0, 2))
# braces / annotations
yb = 92 + cs + 6
S.line(right - 16 * cs, yb, right - 8 * cs - 2, yb, color="var(--muted)", width=1.0)
S.text(right - 12 * cs, yb + 9, "high word (discarded)", size=11, color="var(--muted)")
S.line(right - 8 * cs + 2, yb, right, yb, color="var(--muted)", width=1.0)
S.text(right - 4 * cs, yb + 9, "a·x mod 2⁸", size=11, color="var(--muted)")
S.line(right - 8 * cs + cs * 1.5, 92 + cs + 18, right - cs * 1.5, 150, arrow=True, color="var(--hi)", width=1.4)
save("n05-binary-mult", S.figure(
    "<strong>Binary multiplicative hashing with <i>w</i> = 8 and ℓ = 3.</strong> The salt <i>a</i> = 181 "
    "(10110101) is odd. The product <i>a</i>·<i>x</i> = 181 · 43 = 7783 has 2<i>w</i> = 16 bits; the hash value "
    "is the top ℓ bits of its low word, (<i>a</i>·<i>x</i> mod 2<sup>8</sup>) div 2<sup>5</sup> = 011 = 3 — one "
    "multiplication and one shift.",
    alt="bit strings of x = 43, a = 181, their 16-bit product 7783, and the hash value 011 = 3"))

# ---------------------------------------------------------------- 4. binary probing: probe order and uncle blocks
m, hx = 16, 5
order = [hx ^ i for i in range(m)]
rank = {j: i for i, j in enumerate(order)}
S = SVG(500, 178)
cw2, X0, Y0 = 28, 26, 30
for j in range(m):
    cx = X0 + j * cw2
    S.text(cx + cw2 / 2, Y0 - 12, str(j), size=11, color="var(--muted)")
    is_h = j == hx
    S.rect(cx, Y0, cw2, 28, stroke="var(--hi)" if is_h else "currentColor", width=2.0 if is_h else 1.1,
           fill="var(--hi)" if is_h else "none", fill_opacity=0.15 if is_h else None)
    attr_text(S, cx + cw2 / 2, Y0 + 14.5, str(rank[j]), f'data-rank="{j}:{rank[j]}"', size=13,
              weight=700 if is_h else None)
S.text(X0 - 10, Y0 + 14, "i", size=14, font=SERIF_IT, anchor="end")
levels = [(0, "B′₀"), (1, "B′₁"), (2, "B′₂"), (3, "B′₃")]
for k, lab in levels:
    c = (hx >> k) ^ 1
    lo, hi_ = c << k, ((c + 1) << k) - 1
    yy = Y0 + 44 + k * 26
    xa, xb = X0 + lo * cw2 + 3, X0 + (hi_ + 1) * cw2 - 3
    S.path(f"M{xa},{yy - 6} L{xa},{yy} L{xb},{yy} L{xb},{yy - 6}", color="var(--accent)", width=1.6)
    rng_lab = "probe 1" if k == 0 else f"probes {1 << k}–{(2 << k) - 1}"
    S.text((xa + xb) / 2, yy + 10, f"{lab}(x): {rng_lab}", size=11, color="currentColor", halo=True)
save("n05-binary-probing", S.figure(
    "<strong>Binary probing in a table of size 16, for a key with <i>h</i>(<i>x</i>) = 5 = 0101.</strong> Probe "
    "<i>i</i> looks at cell 5 ⊕ <i>i</i>; the number in each cell is the probe at which it is reached. After the home "
    "cell, the probes sweep the uncle blocks <i>B</i>′<sub>0</sub>(<i>x</i>) = {4}, <i>B</i>′<sub>1</sub>(<i>x</i>) = "
    "{6, 7}, <i>B</i>′<sub>2</sub>(<i>x</i>) = {0, …, 3}, <i>B</i>′<sub>3</sub>(<i>x</i>) = {8, …, 15} — each the "
    "sibling of the aligned block of size 2<sup><i>k</i></sup> around the home cell, so every aligned block (a "
    "cache line) is finished before the next is touched.",
    alt="sixteen cells numbered 0 to 15 with probe ranks; brackets mark the uncle blocks of cell 5"))

# ---------------------------------------------------------------- 5. probes vs load factor (chart)
def lp_unsuccessful(m, n, rng):
    occ = np.zeros(m, dtype=bool)
    for hh in rng.integers(0, m, n):
        while occ[hh]:
            hh = (hh + 1) % m
        occ[hh] = True
    d, dist = 0, np.zeros(m, dtype=np.int64)
    for j in list(range(m - 1, -1, -1)) * 2:
        d = 0 if not occ[j] else d + 1
        dist[j] = d
    return float(np.mean(dist + 1))


rng_np = np.random.default_rng(5)
pts = []
for alpha in (0.2, 0.4, 0.5, 0.6, 0.7, 0.75, 0.8, 0.85):
    mm = 4001
    vals = [lp_unsuccessful(mm, int(alpha * mm), rng_np) for _ in range(8)]
    pts.append((alpha, float(np.mean(vals))))
print("linear probing simulated:", [(a_, round(v, 2)) for a_, v in pts])

W, H = 520, 270
S = SVG(W, H, font_size=12)
L, R, T, Bm = 52, 150, 16, 40
ymax, xmax = 25, 0.9
X = lambda a_: L + a_ / xmax * (W - L - R)
Y = lambda v: H - Bm - v / ymax * (H - T - Bm)
for v in (0, 5, 10, 15, 20, 25):
    S.line(L, Y(v), W - R, Y(v), color="var(--muted)", width=0.6, opacity=0.35)
    S.text(L - 8, Y(v), str(v), size=11, anchor="end", color="var(--muted)")
for a_ in (0, 0.2, 0.4, 0.6, 0.8):
    S.text(X(a_), H - Bm + 14, f"{a_:.1f}", size=11, color="var(--muted)")
S.line(L, H - Bm, W - R, H - Bm, color="var(--muted)", width=1.0)
S.text((L + W - R) / 2, H - 8, "load factor α = n/m", size=12, color="var(--muted)")
S.text(14, (T + H - Bm) / 2, "expected probes", size=12, color="var(--muted)", anchor="middle")
S.items[-1] = S.items[-1].replace("<text ", f'<text transform="rotate(-90 14 {(T + H - Bm) / 2:.1f})" ', 1)


def curve(f, a_max, color, dash=None):
    xs = np.linspace(0, a_max, 120)
    d = "M" + " L".join(f"{X(a_):.1f},{Y(min(f(a_), ymax)):.1f}" for a_ in xs)
    S.path(d, color=color, width=2, dash=dash)


uni = lambda a_: 1 / (1 - a_)
knuth = lambda a_: 0.5 * (1 + 1 / (1 - a_) ** 2)
curve(uni, 0.9, "var(--accent)")
a_cut = 1 - 1 / math.sqrt(2 * ymax - 1)   # where knuth = ymax
curve(knuth, a_cut, "var(--accent2)", dash="6 4")
for a_, v in pts:
    S.add(f'<g><title>linear probing, α = {a_}: simulated {v:.2f} probes (Knuth: {knuth(a_):.2f})</title>'
          f'<circle cx="{X(a_):.1f}" cy="{Y(v):.1f}" r="4.5" fill="var(--accent2)" stroke="var(--paper)" '
          f'stroke-width="2"/></g>')
S.text(W - R + 8, Y(uni(0.9)) + 2, "uniform hashing", size=12, anchor="start")
S.text(W - R + 8, Y(uni(0.9)) + 17, "1/(1 − α)", size=12, anchor="start", color="var(--muted)")
S.text(X(a_cut) + 8, Y(ymax) + 6, "linear probing", size=12, anchor="start")
S.text(X(a_cut) + 8, Y(ymax) + 21, "(1 + 1/(1 − α)²)/2", size=12, anchor="start", color="var(--muted)")
save("n05-probes", S.figure(
    "<strong>Unsuccessful search in an open-addressed table: expected number of probes.</strong> Solid: the bound "
    "1/(1 − α) of §5.8 for ideal random probe sequences. Dashed: Knuth's estimate for linear probing (not in the "
    "note), with simulated averages (dots; 8 tables of size 4001 per point). Linear probing pays for its clusters: "
    "8.5 probes at α = 3/4 against 4, and 50.5 at α = 0.9 against 10.",
    alt="two curves of expected probes against load factor; linear probing rises much faster than uniform hashing"))
