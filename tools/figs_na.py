#!/usr/bin/env python3
"""Figures for Extended Dance Remix A (Fast Fourier Transforms). Writes tools/figs/na-<name>.html; then run
tools/assemble.py on content/4-lecture-notes/a-fast-fourier-transforms.md. Every number drawn is computed here
(minimal radix-2 FFT); tools/checks/na.py re-checks the same values independently."""
import cmath
import math
import os

from figlib import SVG, SERIF_IT, MONO

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")
os.makedirs(OUT, exist_ok=True)


def save(name, html):
    with open(os.path.join(OUT, name + ".html"), "w", encoding="utf-8") as f:
        f.write(html + "\n")
    print("wrote", name)


def omega(n, k=1):
    return cmath.exp(2j * math.pi * k / n)


def fft(P):
    n = len(P)
    if n == 1:
        return list(P)
    U, V = fft(P[0::2]), fft(P[1::2])
    out = [0] * n
    for j in range(n // 2):
        t = omega(n, j) * V[j]
        out[j], out[j + n // 2] = U[j] + t, U[j] - t
    return out


def ifft(Ps):
    n = len(Ps)
    return [z.conjugate() / n for z in fft([complex(w).conjugate() for w in Ps])]


def cfmt(z):
    """Gaussian integer as text: 3, -2, 1+2i, -5-10i, i, -i."""
    a, b = round(z.real), round(z.imag)
    assert abs(z.real - a) < 1e-9 and abs(z.imag - b) < 1e-9
    a, b = int(a), int(b)
    if b == 0:
        return str(a).replace("-", "−")
    bi = ("" if abs(b) == 1 else str(abs(b))) + "i"
    if a == 0:
        return ("−" if b < 0 else "") + bi
    return f"{a}{'−' if b < 0 else '+'}{bi}".replace("-", "−")


SUP = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")

# ====================================================================== roots of unity, collapsing
S = SVG(640, 248)
COLS = ["var(--accent)", "var(--accent2)", "var(--hi)", "currentColor"]
centers = [(84, 134), (250, 134), (416, 134), (566, 134)]
R = 48
levels = [8, 4, 2, 1]
for (cx, cy), n in zip(centers, levels):
    S.line(cx - R - 12, cy, cx + R + 12, cy, color="var(--muted)", width=0.8)
    S.line(cx, cy - R - 12, cx, cy + R + 12, color="var(--muted)", width=0.8)
    S.circle(cx, cy, R, stroke="currentColor", fill="none", width=1.0)
    # dashed diameters joining x and -x (they have the same square)
    if n > 1:
        for k in range(n // 2):
            z1, z2 = omega(n, k), omega(n, k + n // 2)
            assert abs(z1 * z1 - z2 * z2) < 1e-12
            S.line(cx + R * z1.real, cy - R * z1.imag, cx + R * z2.real, cy - R * z2.imag,
                   color="var(--muted)", width=1.0, dash="3 3")
    for k in range(n):
        z = omega(n, k)
        x, y = cx + R * z.real, cy - R * z.imag
        # colour = which 8th-root pair it comes from (level 8: k mod 4; level 4: k; levels 2, 1: neutral)
        col = COLS[k % 4] if n == 8 else COLS[k] if n == 4 else "currentColor"
        S.circle(x, y, 5.2, stroke=col, fill=col, width=1)
        if n == 8:
            lab = "ω" + str(k).translate(SUP)
        else:
            lab = {1: "1", -1: "−1"}.get(round(z.real) if abs(z.imag) < 1e-9 else None) or ("i" if z.imag > 0 else "−i")
        lx, ly = cx + (R + 17) * z.real, cy - (R + 15) * z.imag
        S.text(lx, ly, lab, size=14, font=SERIF_IT, italic=True, halo=True)
    S.text(cx, cy + R + 34, f"X{str(n).translate(SUB)}", size=15, font=SERIF_IT, italic=True)
for i in range(3):
    x1 = centers[i][0] + 34
    x2 = centers[i + 1][0] - 34
    S.path(f"M{x1},{62} Q{(x1 + x2) / 2},{30} {x2},{62}", arrow=True, width=1.3)
    S.text((x1 + x2) / 2, 30, "square", size=12.5, color="var(--muted)", halo=True)
# check the colour story: squares of omega_8^k and omega_8^{k+4} are omega_4^k
for k in range(4):
    assert abs(omega(8, k) ** 2 - omega(4, k)) < 1e-12 and abs(omega(8, k + 4) ** 2 - omega(4, k)) < 1e-12
save("na-roots", S.figure(
    "<strong>The roots of unity are a collapsing set.</strong> Left: the eighth roots of unity "
    "ω<sup>k</sup> = <i>e</i><sup>2π<i>ik</i>/8</sup>. Opposite points (joined by dashed diameters, same color) are "
    "<i>x</i> and −<i>x</i>, so they have the same square: squaring maps the 8 points two-to-one onto the 4 fourth roots "
    "(each drawn in the color of the pair it comes from), those onto the 2 square roots of 1, and those onto {1}. "
    "This is why each level of the radix-2 FFT needs only half as many sample points.",
    alt="four unit circles: the eighth, fourth and second roots of unity and the number 1, with squaring arrows between them"))

# ====================================================================== butterfly network, n = 8
n = 8
bits = 3


def rev(k):
    return int(format(k, "03b")[::-1], 2)


order = [k for _, k in sorted((rev(k), k) for k in range(n))]
assert order == [0, 4, 2, 6, 1, 5, 3, 7]
B = SVG(640, 336)
y0, dy = 58, 36
ys = [y0 + dy * r for r in range(n)]
xin, xout = 78, 562
stages = [(118, 208), (262, 352), (406, 496)]
# horizontal wires
B.line(xin, 0, xin, 0)  # no-op keeps ordering simple
for y in ys:
    B.line(xin, y, xout, y, width=1.2)
for r, k in enumerate(order):
    B.text(xin - 8, ys[r], f"P[{k}]", size=13, anchor="end", font=SERIF_IT, italic=True)
    B.text(xout + 8, ys[r], f"P*[{r}]", size=13, anchor="start", font=SERIF_IT, italic=True)
# simulate symbolically to make sure the drawn network computes the DFT
P = [complex(v) for v in (1, 2, 3, 4, 5, 6, 7, 8)]
A = [P[k] for k in order]
for s, (xa, xb) in enumerate(stages, start=1):
    m = 2 ** s
    half = m // 2
    B.text((xa + xb) / 2, 22, f"stage {s}", size=13, weight=600)
    B.text((xa + xb) / 2, 38, f"{m}-point DFTs", size=12, color="var(--muted)")
    for b in range(0, n, m):
        for j in range(half):
            t, u = b + j, b + j + half
            B.line(xa, ys[t], xb, ys[u], width=1.2)
            B.line(xa, ys[u], xb, ys[t], width=1.2)
            for (x, y) in ((xa, ys[t]), (xa, ys[u]), (xb, ys[t]), (xb, ys[u])):
                B.circle(x, y, 2.6, stroke="currentColor", fill="currentColor", width=0.8)
            e = j * (n // m)  # omega_m^j = omega_8^(j * 8/m)
            lab = "ω" + str(e).translate(SUP)
            B.text(xa - 15, ys[u] - 10, lab, size=12.5, font=SERIF_IT, italic=True, color="var(--accent)", halo=True)
            uu, tt = A[t], omega(m, j) * A[u]
            A[t], A[u] = uu + tt, uu - tt
            B.text(xb + 9, ys[u] + 10, "−", size=13, color="var(--hi)", halo=True)
dft = [sum(P[k] * omega(n, j * k) for k in range(n)) for j in range(n)]
assert all(abs(a - d) < 1e-9 for a, d in zip(A, dft))
B.text(xin - 30, ys[-1] + 34, "bit-reversed order", size=12, color="var(--muted)")
B.text(xout + 26, ys[-1] + 34, "natural order", size=12, color="var(--muted)")
save("na-butterfly", B.figure(
    "<strong>The radix-2 FFT unrolled, <i>n</i> = 8.</strong> The inputs enter in bit-reversed order "
    "(<i>P</i>[3] = <i>P</i>[011₂] sits in row 110₂ = 6). Each stage is a column of <em>butterflies</em>: the lower "
    "input is multiplied by the twiddle factor shown (ω = ω<sub>8</sub>, so ω<sup>2</sup> = <i>i</i>), then the upper "
    "output is the sum and the lower output (marked −) the difference. Stage <i>s</i> combines pairs of "
    "2<sup><i>s</i>−1</sup>-point DFTs into 2<sup><i>s</i></sup>-point DFTs; after lg 8 = 3 stages of 4 butterflies the "
    "outputs <i>P</i>*[0..7] come out in natural order — (<i>n</i>/2) lg <i>n</i> multiplications in all.",
    alt="an eight-row butterfly network with three stages of crossing wires, inputs in bit-reversed order on the left"))

# ====================================================================== FFTMultiply as a commutative square
p, q = [1, 2, 0, 0], [3, 4, 0, 0]
ps, qs = fft([complex(v) for v in p]), fft([complex(v) for v in q])
rs = [a * b for a, b in zip(ps, qs)]
r = ifft(rs)
assert [cfmt(z) for z in ps] == ["3", "1+2i", "−1", "1−2i"]
assert [cfmt(z) for z in qs] == ["7", "3+4i", "−1", "3−4i"]
assert [cfmt(z) for z in rs] == ["21", "−5+10i", "1", "−5−10i"]
assert [cfmt(z) for z in r] == ["3", "10", "8", "0"]
D = SVG(640, 262)
bw, bh = 236, 66
boxes = {"tl": (18, 30), "tr": (386, 30), "bl": (18, 170), "br": (386, 170)}


def box(key, title, lines):
    x, y = boxes[key]
    D.rect(x, y, bw, bh, rx=8, stroke="currentColor", fill="var(--paper)", width=1.3)
    D.text(x + 10, y + 14, title, size=12, anchor="start", color="var(--muted)")
    for i, ln in enumerate(lines):
        D.text(x + 10, y + 34 + 18 * i, ln, size=13, anchor="start", font=MONO)


def vec(v):
    return "[" + ", ".join(cfmt(complex(z)) for z in v) + "]"


box("tl", "coefficients (padded to n = 4)", ["p = " + vec(p), "q = " + vec(q)])
box("tr", "coefficients of the product", ["r = " + vec(r)])
box("bl", "samples at 1, i, −1, −i", ["p* = " + vec(ps), "q* = " + vec(qs)])
box("br", "samples of the product", ["r* = " + vec(rs)])
# arrows
D.line(18 + bw + 8, 63, 386 - 8, 63, arrow=True, dash="5 4", color="var(--muted)", width=1.4)
D.text((18 + bw + 386) / 2, 50, "Multiply: Θ(n²)", size=12.5, color="var(--muted)")
D.line(18 + bw + 8, 203, 386 - 8, 203, arrow=True, color="var(--accent)", width=1.8)
D.text((18 + bw + 386) / 2, 190, "pointwise ×: O(n)", size=12.5, color="var(--accent)", weight=600)
D.line(136, 30 + bh + 6, 136, 170 - 6, arrow=True, color="var(--accent)", width=1.8)
D.text(146, 133, "FFT: O(n log n)", size=12.5, anchor="start", color="var(--accent)", weight=600)
D.line(504, 170 - 6, 504, 30 + bh + 6, arrow=True, color="var(--accent)", width=1.8)
D.text(494, 133, "inverse FFT: O(n log n)", size=12.5, anchor="end", color="var(--accent)", weight=600)
save("na-pipeline", D.figure(
    "<strong>FFTMultiply on (1 + 2<i>x</i>)(3 + 4<i>x</i>).</strong> The direct route across the top costs "
    "Θ(<i>n</i>²). The detour goes down to the sample representation with two FFTs (evaluating at the fourth roots "
    "of unity), multiplies the samples one by one, and comes back with one inverse FFT: "
    "3 + 10<i>x</i> + 8<i>x</i>². Length 4 suffices because the product has only 3 coefficients; with fewer samples "
    "than coefficients the high terms would wrap around onto the low ones.",
    alt="a commutative square: coefficient vectors on top, sample vectors below, FFT down, pointwise product across, inverse FFT up"))
