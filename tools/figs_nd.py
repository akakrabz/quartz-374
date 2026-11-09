#!/usr/bin/env python3
"""Figures for lecture note D (advanced dynamic programming).
Writes tools/figs/nd-*.html; then run tools/assemble.py on the page. Numbers are recomputed here and checked
again in tools/checks/nd.py."""
import math
import os
from figlib import SVG, MONO, SERIF_IT, SANS

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")
os.makedirs(OUT, exist_ok=True)


def save(name, html):
    with open(os.path.join(OUT, name + ".html"), "w", encoding="utf-8") as f:
        f.write(html + "\n")
    print("wrote", name)


def edit_table(A, B):
    m, n = len(A), len(B)
    E = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        for j in range(n + 1):
            E[i][j] = j if i == 0 else i if j == 0 else min(E[i][j - 1] + 1, E[i - 1][j] + 1,
                                                            E[i - 1][j - 1] + (A[i - 1] != B[j - 1]))
    return E


def half(A, B):
    m, n = len(A), len(B)
    E = edit_table(A, B)
    mid = m // 2
    H = [[None] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        for j in range(n + 1):
            if i < mid:
                H[i][j] = None
            elif i == mid:
                H[i][j] = j
            elif E[i][j] == E[i - 1][j] + 1:
                H[i][j] = H[i - 1][j]
            elif j > 0 and E[i][j] == E[i][j - 1] + 1:
                H[i][j] = H[i][j - 1]
            else:
                H[i][j] = H[i - 1][j - 1]
    return H[m][n]


def small_path(A, B, i0, j0):
    E = edit_table(A, B)
    i, j, pts = len(A), len(B), []
    while i > 0 or j > 0:
        pts.append((i0 + i, j0 + j))
        if i > 0 and j > 0 and E[i][j] == E[i - 1][j - 1] + (A[i - 1] != B[j - 1]):
            i, j = i - 1, j - 1
        elif i > 0 and E[i][j] == E[i - 1][j] + 1:
            i -= 1
        else:
            j -= 1
    pts.append((i0, j0))
    return pts[::-1]


RECTS = []


def hirsch(A, B, i0, j0, depth):
    RECTS.append((depth, i0, i0 + len(A), j0, j0 + len(B)))
    if len(A) <= 1 or len(B) <= 1:
        return small_path(A, B, i0, j0)
    mid = len(A) // 2
    h = half(A, B)
    p1 = hirsch(A[:mid], B[:h], i0, j0, depth + 1)
    p2 = hirsch(A[mid:], B[h:], i0 + mid, j0 + h, depth + 1)
    return p1 + p2[1:]


# =========================================================================== 1. Hirschberg
A, B = "ALTRUISTIC", "ALGORITHM"
m, n = len(A), len(B)
E = edit_table(A, B)
path = hirsch(A, B, 0, 0, 0)
assert path[0] == (0, 0) and path[-1] == (m, n) and (5, 5) in path
cw, ch = 34, 26
X0, Y0 = 48, 50
S = SVG(X0 + (n + 1) * cw + 150, Y0 + (m + 1) * ch + 16)
# the middle row of the first sweep
S.rect(X0, Y0 + 5 * ch, (n + 1) * cw, ch, stroke="none", fill="var(--accent2)", fill_opacity=0.14, width=0)
for depth, i0, i1, j0, j1 in RECTS:
    if depth == 0 or depth > 2:
        continue
    pad = 3 if depth == 1 else 6
    col = "var(--accent)" if depth == 1 else "var(--accent2)"
    S.rect(X0 + j0 * cw + pad, Y0 + i0 * ch + pad, (j1 - j0 + 1) * cw - 2 * pad, (i1 - i0 + 1) * ch - 2 * pad,
           rx=5, stroke=col, fill="none", width=2.0 if depth == 1 else 1.3, dash=None if depth == 1 else "5 3")
S.rect(X0, Y0, (n + 1) * cw, (m + 1) * ch, stroke="currentColor", fill="none", width=1.0)
for j in range(1, n + 1):
    S.text(X0 + j * cw + cw / 2, Y0 - 12, B[j - 1], size=14, font=MONO)
for i in range(1, m + 1):
    S.text(X0 - 14, Y0 + i * ch + ch / 2, A[i - 1], size=14, font=MONO)
for (i1, j1), (i2, j2) in zip(path, path[1:]):
    x1, y1 = X0 + j1 * cw + cw / 2, Y0 + i1 * ch + ch / 2
    x2, y2 = X0 + j2 * cw + cw / 2, Y0 + i2 * ch + ch / 2
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    S.line(x1 + dx / L * 9, y1 + dy / L * 8, x2 - dx / L * 10, y2 - dy / L * 9, width=1.6, color="var(--hi)",
           arrow=True)
for i in range(m + 1):
    for j in range(n + 1):
        match = i > 0 and j > 0 and A[i - 1] == B[j - 1]
        S.text(X0 + j * cw + cw / 2, Y0 + i * ch + ch / 2 + 1, str(E[i][j]), size=13,
               weight=700 if (i, j) in path else None,
               color="currentColor" if (i, j) in path else "var(--muted)", font=SANS)
# split cell
S.circle(X0 + 5 * cw + cw / 2, Y0 + 5 * ch + ch / 2, 11, stroke="var(--hi)", fill="none", width=1.8)
LX = X0 + (n + 1) * cw + 14
S.text(LX, Y0 + 5 * ch + ch / 2, "row m/2 = 5", size=12, anchor="start", color="var(--accent2)")
S.text(LX, Y0 + 5 * ch + ch / 2 + 16, "split h = Half(10, 9) = 5", size=12, anchor="start", color="var(--hi)")
S.rect(LX, Y0 + 20, 22, 12, rx=3, stroke="var(--accent)", fill="none", width=2.0)
S.text(LX + 28, Y0 + 26, "level 1", size=12, anchor="start", color="var(--muted)")
S.rect(LX, Y0 + 40, 22, 12, rx=3, stroke="var(--accent2)", fill="none", width=1.3, dash="5 3")
S.text(LX + 28, Y0 + 46, "level 2", size=12, anchor="start", color="var(--muted)")
save("nd-hirschberg", S.figure(
    "<strong>Hirschberg's recursion on the note's example.</strong> Rows: <i>A</i> = ALTRUISTIC; columns: "
    "<i>B</i> = ALGORITHM; the numbers are <i>Edit</i>(<i>i</i>, <i>j</i>). One linear-space sweep finds the "
    "distance 6 and the column <i>h</i> = 5 where an optimal path crosses the middle row (circled). The problem "
    "splits into ALTRU → ALGOR and ISTIC → ITHM (solid boxes), each split again in the same way (dashed boxes), "
    "and so on until one string has length at most 1. The boxes of each level have about half the total area of the "
    "level above, which is why the recursion costs about as much as the first sweep. The arrows are the "
    "alignment it returns: AL-TRUISTIC over ALGOR-I-THM.",
    alt="edit distance grid with nested recursion rectangles and the optimal path"))

# =========================================================================== 2. sparse LCS
RA, CB = "ALTRUISTIC", "ALGORITHMS"
rows = "«" + RA + "»"
cols = "«" + CB + "»"
M_, N_ = len(RA), len(CB)
L = [[0] * (N_ + 2) for _ in range(M_ + 2)]
for i in range(1, M_ + 2):
    for j in range(1, N_ + 2):
        L[i][j] = L[i - 1][j - 1] + 1 if rows[i] == cols[j] else max(L[i - 1][j], L[i][j - 1])
matches = [(i, j) for i in range(M_ + 2) for j in range(N_ + 2) if rows[i] == cols[j]]
assert len(matches) == 10
chain = [(0, 0), (1, 1), (2, 2), (4, 5), (6, 6), (7, 10), (11, 11)]
assert all(L[b[0]][b[1]] == L[a[0]][a[1]] + 1 for a, b in zip(chain, chain[1:])) and L[11][11] == 6
cw = ch = 28
X0, Y0 = 44, 46
S = SVG(X0 + 12 * cw + 20, Y0 + 12 * ch + 14)
S.rect(X0, Y0, 12 * cw, 12 * ch, stroke="currentColor", fill="none", width=1.0)
for k in range(1, 12):
    S.line(X0 + k * cw, Y0, X0 + k * cw, Y0 + 12 * ch, width=0.5, opacity=0.25)
    S.line(X0, Y0 + k * ch, X0 + 12 * cw, Y0 + k * ch, width=0.5, opacity=0.25)
for j in range(12):
    S.text(X0 + j * cw + cw / 2, Y0 - 12, cols[j], size=14, font=MONO)
for i in range(12):
    S.text(X0 - 14, Y0 + i * ch + ch / 2, rows[i], size=14, font=MONO)
for a, b in zip(chain, chain[1:]):
    x1, y1 = X0 + a[1] * cw + cw / 2, Y0 + a[0] * ch + ch / 2
    x2, y2 = X0 + b[1] * cw + cw / 2, Y0 + b[0] * ch + ch / 2
    dx, dy = x2 - x1, y2 - y1
    Ln = math.hypot(dx, dy)
    S.line(x1 + dx / Ln * 12, y1 + dy / Ln * 12, x2 - dx / Ln * 13, y2 - dy / Ln * 13, width=1.6,
           color="var(--hi)", arrow=True)
for (i, j) in matches:
    x, y = X0 + j * cw + cw / 2, Y0 + i * ch + ch / 2
    on = (i, j) in chain
    S.circle(x, y, 10.5, stroke="var(--hi)" if on else "currentColor", fill="var(--paper)", width=1.6 if on else 1.1)
    S.text(x, y + 1, str(L[i][j]), size=13, weight=700 if on else None,
           color="var(--hi)" if on else "currentColor")
save("nd-sparse-lcs", S.figure(
    "<strong>Only the match points matter.</strong> The LCS table of Figure D.1 (rows ALTRUISTIC, columns "
    "ALGORITHMS, sentinels « and ») reduced to its 8 match points and 2 sentinels, each labeled with its value "
    "<i>LCS</i>(<i>i</i>, <i>j</i>) = 1 + the largest value at a match point strictly above and to the left. "
    "A longest chain of match points, each strictly below and to the right of the previous one, is a longest "
    "common subsequence: A L R I S (red), so <i>LCS</i>(<i>m</i> + 1, <i>n</i> + 1) − 1 = 6 − 1 = 5.",
    alt="12 by 12 grid with circles at the match points and a highlighted chain"))

# =========================================================================== 3. monotone vs totally monotone
X1 = [[12, 21, 38, 76, 27], [74, 14, 14, 29, 60], [21, 8, 25, 10, 71], [68, 45, 29, 15, 76], [97, 8, 12, 2, 6]]
X2 = [[12, 21, 38, 76, 89], [47, 14, 14, 29, 60], [21, 8, 20, 10, 71], [68, 16, 29, 15, 76], [97, 8, 12, 2, 6]]


def lm(row):
    return min(range(len(row)), key=lambda c: (row[c], c))


cw, ch = 40, 28
S = SVG(600, 236)
for k, (X, x0, title) in enumerate([(X1, 30, "monotone, not totally monotone"), (X2, 330, "totally monotone")]):
    y0 = 40
    S.text(x0 + 2.5 * cw, 18, title, size=13, color="var(--muted)")
    for i in range(5):
        for j in range(5):
            gray = (k == 0 and i in (0, 2) and j in (2, 4))
            ism = (j == lm(X[i]))
            if ism:
                S.rect(x0 + j * cw + 2, y0 + i * ch + 2, cw - 4, ch - 4, rx=4, stroke="none", fill="var(--accent)",
                       fill_opacity=0.25, width=0)
            if gray:
                S.rect(x0 + j * cw + 2, y0 + i * ch + 2, cw - 4, ch - 4, rx=4, stroke="var(--hi)", fill="none",
                       width=1.6, dash="4 3")
            S.text(x0 + j * cw + cw / 2, y0 + i * ch + ch / 2 + 1, str(X[i][j]), size=14,
                   weight=700 if ism else None)
    # brackets
    S.path(f"M{x0 - 4},{y0} L{x0 - 9},{y0} L{x0 - 9},{y0 + 5 * ch} L{x0 - 4},{y0 + 5 * ch}", width=1.3)
    S.path(f"M{x0 + 5 * cw + 4},{y0} L{x0 + 5 * cw + 9},{y0} L{x0 + 5 * cw + 9},{y0 + 5 * ch} "
           f"L{x0 + 5 * cw + 4},{y0 + 5 * ch}", width=1.3)
    S.text(x0 + 2.5 * cw, y0 + 5 * ch + 20, "leftmost minima in columns 1, 2, 2, 4, 4", size=12, color="var(--muted)")
S.text(30, 222, "dashed: rows 1, 3 × columns 3, 5 — row 1 prefers column 5, row 3 prefers column 3", size=12,
       anchor="start", color="var(--hi)")
save("nd-monotone", S.figure(
    "<strong>Monotone versus totally monotone (the note's two examples).</strong> Shaded: the leftmost minimum of "
    "each row. In both arrays these move weakly to the right going down, so both are monotone. The left array is "
    "not totally monotone: in the 2 × 2 subarray of rows 1, 3 and columns 3, 5 (38, 27 over 25, 71) the top row's "
    "minimum is on the right and the bottom row's on the left. The right array has no such 2 × 2 subarray.",
    alt="two 5 by 5 arrays with row minima shaded and a violating 2 by 2 subarray marked"))

# =========================================================================== 4. Monge's geometric example
S = SVG(520, 236)
yt, yb = 40, 170
S.line(30, yt, 490, yt, width=1.3)
S.line(30, yb, 490, yb, width=1.3)
S.text(500, yt, "ℓ", size=16, font=SERIF_IT, italic=True, anchor="start")
S.text(500, yb, "ℓ′", size=16, font=SERIF_IT, italic=True, anchor="start")
pi, pi2, qj, qj2 = (110, yt), (330, yt), (170, yb), (420, yb)
# straight pairs
S.line(*pi, *qj, width=2.2, color="var(--accent)")
S.line(*pi2, *qj2, width=2.2, color="var(--accent)")
# crossing pairs
S.line(*pi, *qj2, width=1.6, color="var(--hi)", dash="6 4")
S.line(*pi2, *qj, width=1.6, color="var(--hi)", dash="6 4")
# intersection x
(x1, y1), (x2, y2), (x3, y3), (x4, y4) = pi, qj2, pi2, qj
den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
ix, iy = x1 + t * (x2 - x1), y1 + t * (y2 - y1)
S.circle(ix, iy, 3.5, stroke="currentColor", fill="currentColor")
S.text(ix + 14, iy + 1, "x", size=16, font=SERIF_IT, italic=True, halo=True)
for (px, py), base, sub, dy in [(pi, "p", "i", -18), (pi2, "p", "i′", -18), (qj, "q", "j", 20), (qj2, "q", "j′", 20)]:
    S.circle(px, py, 4.5, stroke="currentColor", fill="var(--paper)", width=1.6)
    S.text(px - 3, py + dy, base, size=17, font=SERIF_IT, italic=True)
    S.text(px + 4, py + dy + 6, sub, size=12, font=SERIF_IT, italic=True, anchor="start")
S.text(260, 222, "solid: M[i, j] + M[i′, j′]   ·   dashed: M[i, j′] + M[i′, j]", size=12, color="var(--muted)")
save("nd-monge", S.figure(
    "<strong>Why distances between two parallel lines are Monge.</strong> With <i>i</i> &lt; <i>i</i>′ and "
    "<i>j</i> &lt; <i>j</i>′ (points numbered in the same direction on both lines), the crossing segments "
    "<i>p<sub>i</sub>q<sub>j′</sub></i> and <i>p<sub>i′</sub>q<sub>j</sub></i> (dashed) meet at a point <i>x</i>. "
    "Splitting them at <i>x</i> and regrouping the four pieces gives two paths from <i>p<sub>i</sub></i> to "
    "<i>q<sub>j</sub></i> and from <i>p<sub>i′</sub></i> to <i>q<sub>j′</sub></i>, which by the triangle inequality "
    "are at least as long as the solid segments: the non-crossing pairs never cost more than the crossing pairs.",
    alt="two parallel lines with two solid parallel segments and two dashed crossing segments meeting at x"))
