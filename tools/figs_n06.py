#!/usr/bin/env python3
"""Figures for lecture note 6 (filtering and streaming). Writes tools/figs/n06-<name>.html; then run
tools/assemble.py on content/4-lecture-notes/06-filtering-and-streaming.md. The bits and counters drawn here are
computed below; tools/checks/n06.py re-checks them in the figure HTML."""
import os

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


# ---------------------------------------------------------------- 1. Bloom filter
M = 16
H = {"cat": (1, 6, 11), "dog": (3, 6, 14), "emu": (0, 9, 11), "fox": (2, 9, 14), "gnu": (1, 9, 14)}
X = ["cat", "dog", "emu"]
B = [0] * M
for x in X:
    for v in H[x]:
        B[v] = 1

S = SVG(520, 236)
cw, x0, yb = 26, 52, 98
cx = lambda i: x0 + i * cw + cw / 2
item_x = {"cat": 120, "dog": 260, "emu": 400}
query_x = {"fox": 170, "gnu": 350}
# edges first
for x in X:
    for v in H[x]:
        S.line(item_x[x], 42, cx(v), yb - 3, color="var(--accent)", width=1.3, arrow=True)
for q in ("fox", "gnu"):
    for v in H[q]:
        bad = B[v] == 0
        S.line(query_x[q], 190, cx(v), yb + cw + 3,
               color="var(--hi)" if bad else ("var(--muted)" if q == "fox" else "var(--accent2)"),
               width=2.2 if bad else 1.3, arrow=True, dash=None if bad else "5 3")
for i in range(M):
    on = B[i] == 1
    S.rect(x0 + i * cw, yb, cw, cw, stroke="currentColor", width=1.2, fill="var(--accent)" if on else "var(--paper)",
           fill_opacity=0.22 if on else None)
    attr_text(S, cx(i), yb + cw / 2 + 1, str(B[i]), f'data-bit="{i}:{B[i]}"', size=13, weight=700 if on else None)
S.text(x0 - 10, yb + cw / 2, "B", size=15, font=SERIF_IT, italic=True, anchor="end")
for i in (0, 15):
    S.text(cx(i), yb + cw + 12, str(i), size=10, color="var(--muted)")
for x in X:
    S.rect(item_x[x] - 26, 16, 52, 24, rx=6, stroke="var(--accent)", width=1.5)
    S.text(item_x[x], 28.5, x, size=13, font=MONO)
for q, verdict in (("fox", "False"), ("gnu", "Maybe")):
    col = "var(--hi)" if q == "fox" else "var(--accent2)"
    S.rect(query_x[q] - 26, 192, 52, 24, rx=6, stroke=col, width=1.5, dash="4 3")
    S.text(query_x[q], 204.5, q, size=13, font=MONO)
    S.text(query_x[q] + 34, 204, f"→ {verdict}", size=12, anchor="start", color=col if q == "fox" else "currentColor")
S.text(500, 228, "m = 16, k = 3", size=11, anchor="end", color="var(--muted)")
save("n06-bloom", S.figure(
    "<strong>A Bloom filter with <i>m</i> = 16 bits and <i>k</i> = 3 hash functions.</strong> Inserting cat, dog and "
    "emu (hash values (1, 6, 11), (3, 6, 14), (0, 9, 11)) sets 7 bits; bits 6 and 11 are set twice, which is "
    "harmless. Query fox, with hash values (2, 9, 14), meets the 0 in bit 2 and is correctly rejected. Query gnu, "
    "(1, 9, 14), finds three 1s — set by three different items — and gets the answer Maybe: a false positive. "
    "A member is never rejected.",
    alt="sixteen bits, seven of them 1; arrows from three inserted items and two queries to their bits"))

# ---------------------------------------------------------------- 2. count-min sketch
STREAM = list("abacadba")
HC = {"a": (0, 3, 1), "b": (2, 1, 4), "c": (3, 1, 0), "d": (2, 3, 0)}
W, D = 5, 3
C = [[0] * W for _ in range(D)]
for x in STREAM:
    for i in range(D):
        C[i][HC[x][i]] += 1
q = "d"
est = min(C[i][HC[q][i]] for i in range(D))

S = SVG(520, 214)
S.text(20, 22, "stream:", size=12, anchor="start", color="var(--muted)")
for t, x in enumerate(STREAM):
    S.text(82 + t * 20, 22, x, size=14, font=MONO, color="var(--hi)" if x == q else "currentColor",
           weight=700 if x == q else None)
gx, gy, cs = 150, 50, 44
for j in range(W):
    S.text(gx + j * cs + cs / 2, gy - 9, str(j), size=11, color="var(--muted)")
for i in range(D):
    S.text(gx - 12, gy + i * cs + cs / 2, f"h{i + 1}", size=13, font=SERIF_IT, italic=True, anchor="end")
    for j in range(W):
        hit = HC[q][i] == j
        S.rect(gx + j * cs, gy + i * cs, cs, cs, stroke="var(--hi)" if hit else "currentColor",
               width=2.4 if hit else 1.1, fill="var(--hi)" if hit else "none", fill_opacity=0.10 if hit else None)
        attr_text(S, gx + j * cs + cs / 2, gy + i * cs + cs / 2 + 1, str(C[i][j]), f'data-count="{i}:{j}:{C[i][j]}"',
                  size=15, weight=700 if hit else None)
# frequency table on the right
tx = gx + W * cs + 34
S.text(tx, gy - 9, "x", size=12, font=SERIF_IT, italic=True)
S.text(tx + 40, gy - 9, "count", size=12, color="var(--muted)")
S.text(tx + 90, gy - 9, "estimate", size=12, color="var(--muted)")
freq = {x: STREAM.count(x) for x in "abcd"}
for r, x in enumerate("abcd"):
    yy = gy + 12 + r * 28
    e = min(C[i][HC[x][i]] for i in range(D))
    col = "var(--hi)" if e > freq[x] else "currentColor"
    S.text(tx, yy, x, size=14, font=MONO, color=col)
    S.text(tx + 40, yy, str(freq[x]), size=14, color=col)
    S.text(tx + 90, yy, str(e), size=14, color=col, weight=700 if e > freq[x] else None)
S.text(gx + W * cs / 2, gy + D * cs + 20, f"estimate(d) = min({C[0][HC[q][0]]}, {C[1][HC[q][1]]}, {C[2][HC[q][2]]}) "
       f"= {est}", size=13, color="currentColor")
save("n06-countmin", S.figure(
    "<strong>A count-min sketch with <i>d</i> = 3 rows of <i>w</i> = 5 counters</strong> after the stream "
    "a b a c a d b a (<i>N</i> = 8). Each arrival adds 1 to one counter per row, the one its row's hash function "
    "picks: a → (0, 3, 1), b → (2, 1, 4), c → (3, 1, 0), d → (2, 3, 0). The estimate for an item is the smallest "
    "of its <i>d</i> counters. Every counter of d also counts another item (b, a and c respectively), so the "
    "estimate for d is 2 although d occurred once; the estimates for a, b and c are exact. An estimate is never "
    "too small.",
    alt="a 3 by 5 grid of counters; the three counters of item d are highlighted with values 3, 5, 2"))
