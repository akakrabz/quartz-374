#!/usr/bin/env python3
"""Figures for Erickson's lecture note 4 (tail inequalities). Writes tools/figs/n04-<name>.html; then run
tools/assemble.py on content/4-lecture-notes/04-tail-inequalities.md. All plotted values are computed here: exact
binomial tails (scipy), the bounds from their formulas, and the exact height distribution of a random treap by the
dynamic program over subtree sizes that tools/checks/n04.py checks against enumeration and simulation."""
import math
import os
from fractions import Fraction as Fr

import numpy as np
from scipy.stats import binom

from figlib import SVG, SERIF_IT

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")
os.makedirs(OUT, exist_ok=True)


SUPMAP = str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻")


def pow10(e):
    return "1" if e == 0 else "10" + str(e).translate(SUPMAP)


def save(name, html):
    with open(os.path.join(OUT, name + ".html"), "w", encoding="utf-8") as f:
        f.write(html + "\n")
    print("wrote", name)


def fmt_frac(f):
    return f"{f.numerator}/{f.denominator}"


# ------------------------------------------------------------------ 1. Markov's inequality, 6 fair coins
d = [Fr(math.comb(6, i), 64) for i in range(7)]
tail = [sum(d[j:]) for j in range(7)]          # Pr[Z >= j]
EZ = sum(i * q for i, q in enumerate(d))
assert EZ == 3 and sum(tail[1:]) == 3
S = SVG(520, 268)
x0, y0, ux, uy = 70, 222, 64, 180              # origin, pixels per unit z, pixels per unit probability
X = lambda z: x0 + z * ux
Y = lambda p: y0 - p * uy
zsel = 4
# light columns: Pr[Z >= z] on (z-1, z]
for z in range(1, 7):
    h = float(tail[z])
    S.rect(X(z - 1), Y(h), ux, h * uy, stroke="none", fill="var(--accent)", fill_opacity=0.16, width=0)
# darker rectangle z * Pr[Z >= z]
hz = float(tail[zsel])
S.rect(X(0), Y(hz), zsel * ux, hz * uy, stroke="var(--accent)", fill="var(--accent)", fill_opacity=0.38, width=1.4)
# staircase outline
pts = []
for z in range(1, 7):
    h = float(tail[z])
    pts += [(X(z - 1), Y(h)), (X(z), Y(h))]
dpath = f"M{X(0)},{Y(float(tail[1]))} " + " ".join(f"L{x:.1f},{y:.1f}" for x, y in pts) + f" L{X(6)},{Y(0)}"
S.path(dpath, color="currentColor", width=2)
# axes
S.line(x0, y0, X(6.6), y0, width=1.2, arrow=True)
S.line(x0, y0, x0, Y(1.12), width=1.2, arrow=True)
for z in range(0, 7):
    S.line(X(z), y0, X(z), y0 + 4, width=1)
    S.text(X(z), y0 + 15, str(z), size=12)
for p in (0, 0.25, 0.5, 0.75, 1):
    S.line(x0 - 4, Y(p), x0, Y(p), width=1)
    S.text(x0 - 8, Y(p), f"{p:g}", size=11.5, anchor="end", color="var(--muted)")
S.text(X(6.6) + 4, y0 + 15, "z", size=14, font=SERIF_IT, italic=True, anchor="end")
S.text(x0 + 6, Y(1.12) + 2, "Pr[Z ≥ z]", size=12.5, anchor="start")
S.text(X(2), Y(hz / 2) + 1, "z · Pr[Z ≥ z] = 4 · 22/64 = 11/8", size=12.5, weight="600")
S.text(X(1.55), Y(0.56), "whole area = E[Z] = 3", size=12.5)
labs = [fmt_frac(Fr(int(t * 64), 64)) if False else f"{int(t * 64)}/64" for t in tail[1:]]
for z in range(1, 7):
    S.text(X(z - 0.5), Y(float(tail[z])) - 9, labs[z - 1], size=11, color="var(--muted)", halo=True)
html = S.figure(
    "<strong>Markov’s inequality as an area (after the note’s figure on p. 1).</strong> <i>Z</i> = the number of "
    "heads in 6 fair coin flips. The staircase is Pr[<i>Z</i> ≥ <i>z</i>]; cutting the region under it into columns "
    "of width 1 shows that its area is Pr[<i>Z</i> ≥ 1] + … + Pr[<i>Z</i> ≥ 6] = 192/64 = E[<i>Z</i>] = 3. The "
    "darker rectangle of width <i>z</i> = 4 and height Pr[<i>Z</i> ≥ 4] = 22/64 fits under the staircase, so its "
    "area, 11/8, is at most 3: Pr[<i>Z</i> ≥ 4] ≤ 3/4. (The true value is 22/64 ≈ 0.34.)",
    alt="a staircase plot of Pr[Z >= z] for six coin flips, with a shaded rectangle under it")
save("n04-markov", html)

# ------------------------------------------------------------------ 2. tail bounds for N = 100 fair coins
N = 100
alphas = np.linspace(0.5, 1.0, 501)


def exact(a):
    return binom.sf(math.ceil(a * N - 1e-9) - 1, N, 0.5)


def kl(a):
    if a >= 1:
        return math.log(2)
    return math.log(2) + a * math.log(a) + (1 - a) * math.log(1 - a)


series = {
    "exact": [exact(a) for a in alphas],
    "Markov": [min(1.0, 1 / (2 * a)) for a in alphas],
    "Chebyshev": [min(1.0, 1 / ((2 * a - 1) ** 2 * N)) if a > 0.5 else 1.0 for a in alphas],
    "Chernoff": [math.exp(-(2 * a - 1) ** 2 * N / 6) for a in alphas],
    "binomial": [min(1.0, math.exp(-kl(a) * N)) for a in alphas],
}
LOGMIN = -32
W, Hh = 616, 340
px0, py0, pw, ph = 60, 30, 400, 270
XA = lambda a: px0 + (a - 0.5) / 0.5 * pw
YL = lambda p: py0 + (0 - math.log10(max(p, 10 ** LOGMIN))) / (-LOGMIN) * ph
S = SVG(W, Hh)
for e in range(0, LOGMIN - 1, -5):
    y = YL(10.0 ** e)
    S.line(px0, y, px0 + pw, y, color="var(--muted)", width=0.6, opacity=0.5)
    S.text(px0 - 6, y, pow10(e), size=11.5, anchor="end", color="var(--muted)")
for a in (0.5, 0.6, 0.7, 0.8, 0.9, 1.0):
    S.line(XA(a), py0 + ph, XA(a), py0 + ph + 4, width=1)
    S.text(XA(a), py0 + ph + 15, f"{a:g}", size=11.5)
S.line(px0, py0 + ph, px0 + pw, py0 + ph, width=1.2)
S.line(px0, py0, px0, py0 + ph, width=1.2)
S.text(px0 + pw / 2, py0 + ph + 32, "α   (threshold αN heads, N = 100)", size=12.5)
style = {
    "exact": dict(color="currentColor", width=2.6, dash=None),
    "Markov": dict(color="var(--muted)", width=1.8, dash="6 4"),
    "Chebyshev": dict(color="var(--accent2)", width=2.0, dash="2 3"),
    "Chernoff": dict(color="var(--accent)", width=2.0, dash=None),
    "binomial": dict(color="var(--hi)", width=2.0, dash="8 3 2 3"),
}
for name, vals in series.items():
    pts = " ".join(f"{XA(a):.1f},{YL(v):.1f}" for a, v in zip(alphas, vals))
    st = style[name]
    da = f' stroke-dasharray="{st["dash"]}"' if st["dash"] else ""
    S.add(f'<polyline points="{pts}" fill="none" stroke="{st["color"]}" stroke-width="{st["width"]}" '
          f'stroke-linejoin="round" stroke-linecap="round"{da}/>')
lab = {
    "Markov": ("Markov", series["Markov"][-1], -3),
    "Chebyshev": ("Chebyshev", series["Chebyshev"][-1], 4),
    "Chernoff": ("Chernoff (simple form)", series["Chernoff"][-1], 0),
    "binomial": ("binomial-coeff. bound", series["binomial"][-1], -9),
}
for name, (txt, v, dy) in lab.items():
    S.text(px0 + pw + 6, YL(v) + dy, txt, size=11.5, anchor="start", color=style[name]["color"]
           if name != "Markov" else "currentColor")
S.text(px0 + pw + 6, YL(series["exact"][-1]) + 9, "exact = 2⁻¹⁰⁰", size=11.5, anchor="start", weight="600")
i75 = int(np.argmin(abs(alphas - 0.75)))
S.circle(XA(0.75), YL(series["exact"][i75]), 3.5, stroke="currentColor", fill="currentColor")
S.text(XA(0.75) - 6, YL(series["exact"][i75]) + 12, "exact 2.8·10⁻⁷ at α = 3/4", size=11.5, anchor="end", halo=True)
S.text(px0 - 4, py0 - 16, "Pr[X ≥ αN]", size=12.5, anchor="start")
html = S.figure(
    "<strong>How good are the bounds? <i>N</i> = 100 fair coins.</strong> The probability of at least α<i>N</i> heads "
    "(log scale; the exact tail is the thick solid curve) and the bounds of §4.6: Markov’s 1/(2α) barely moves; "
    "Chebyshev’s 1/((2α − 1)²<i>N</i>) (with the variance <i>N</i>/4) falls like a polynomial; the simple Chernoff "
    "bound exp(−(2α − 1)²<i>N</i>/6) falls exponentially in <i>N</i>; and the binomial-coefficient bound "
    "(2α<sup>α</sup>(1 − α)<sup>1−α</sup>)<sup>−<i>N</i></sup> hugs the exact tail and meets it at α = 1. At α = 3/4: "
    "exact 2.8·10<sup>−7</sup>, Markov 2/3, Chebyshev 1/25, Chernoff <i>e</i><sup>−100/24</sup> ≈ 0.016, "
    "binomial-coefficient bound <i>e</i><sup>−13.08</sup> ≈ 2.1·10<sup>−6</sup>.",
    alt="log-scale plot of the exact upper tail of 100 coin flips and four upper bounds as functions of alpha")
save("n04-coins", html)


# ------------------------------------------------------------------ 3. height of a random treap, n = 1000
def height_tails(Nmax, Hmax):
    Q = np.zeros((Hmax + 2, Nmax + 1))
    Q[0, 1:] = 1.0
    for hi in range(1, Hmax + 2):
        q = Q[hi - 1]
        conv = np.convolve(q, q)[:Nmax]
        cs = np.cumsum(q)[:Nmax]
        Q[hi, 1:] = (2 * cs - conv) / np.arange(1, Nmax + 1)
    return Q


n = 1000
Q = height_tails(n, 120)
ptail = lambda h: float(Q[math.floor(h) + 1][n])
cs = np.linspace(2.5, 8.0, 551)
ex = [ptail(c * math.log(n)) for c in cs]
note = [min(1.0, 2 / n ** (c * math.log(c) - c)) for c in cs]
corr = [min(1.0, 2 / n ** ((c / 2) * math.log(c / 2) - c / 2)) for c in cs]
LOGMIN = -24
W, Hh = 600, 330
px0, py0, pw, ph = 60, 30, 400, 260
XC = lambda c: px0 + (c - 2.5) / 5.5 * pw
YL = lambda p: py0 + (0 - math.log10(max(p, 10 ** LOGMIN))) / (-LOGMIN) * ph
S = SVG(W, Hh)
for e in range(0, LOGMIN - 1, -4):
    y = YL(10.0 ** e)
    S.line(px0, y, px0 + pw, y, color="var(--muted)", width=0.6, opacity=0.5)
    S.text(px0 - 6, y, pow10(e), size=11.5, anchor="end", color="var(--muted)")
for c in (3, 4, 5, 6, 7, 8):
    S.line(XC(c), py0 + ph, XC(c), py0 + ph + 4, width=1)
    S.text(XC(c), py0 + ph + 15, str(c), size=11.5)
S.line(px0, py0 + ph, px0 + pw, py0 + ph, width=1.2)
S.line(px0, py0, px0, py0 + ph, width=1.2)
S.text(px0 + pw / 2, py0 + ph + 32, "c   (threshold c ln n, n = 1000)", size=12.5)


def poly(vals, color, width, dash=None):
    pts = " ".join(f"{XC(c):.1f},{YL(v):.1f}" for c, v in zip(cs, vals) if v >= 10 ** LOGMIN)
    da = f' stroke-dasharray="{dash}"' if dash else ""
    S.add(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round" '
          f'stroke-linecap="round"{da}/>')


poly(ex, "currentColor", 2.6)
poly(note, "var(--hi)", 2.0, "6 4")
poly(corr, "var(--accent)", 2.0)
c4 = ptail(4 * math.log(n))
S.circle(XC(4), YL(c4), 3.5, stroke="currentColor", fill="currentColor")
S.text(XC(4) + 6, YL(c4) - 9, f"exact {c4:.4f} at c = 4", size=11.5, anchor="start", halo=True)
nb4 = 2 / n ** (4 * math.log(4) - 4)
S.circle(XC(4), YL(nb4), 3.5, stroke="var(--hi)", fill="var(--hi)")
S.text(XC(4) - 6, YL(nb4) + 12, "note: 4.6·10⁻⁵", size=11.5, anchor="end", color="var(--hi)", halo=True)
S.text(px0 + pw + 6, YL(corr[-1]), "corrected bound", size=11.5, anchor="start", color="var(--accent)")
S.text(px0 + pw + 6, YL(ex[-1]), "exact", size=11.5, anchor="start", weight="600")
S.text(px0 + pw + 6, YL(note[-1]), "the note’s bound", size=11.5, anchor="start", color="var(--hi)")
S.text(px0 - 4, py0 - 16, "Pr[height > c ln n]", size=12.5, anchor="start")
assert c4 > nb4
html = S.figure(
    "<strong>The note’s closing bound is too strong. A random treap with <i>n</i> = 1000 nodes.</strong> Thick curve: the "
    "exact probability that its height exceeds <i>c</i> ln <i>n</i> (log scale; computed by a recurrence over subtree "
    "sizes). Dashed (red): the note’s claimed bound 2/<i>n</i><sup><i>c</i> ln <i>c</i> − <i>c</i></sup>, which lies "
    f"below the exact probability for every <i>c</i> from 2.86 on (for smaller <i>c</i> it is close to or above 1) — at <i>c</i> = 4 the true probability is {c4:.4f}, not "
    "at most 4.6·10<sup>−5</sup>. Thin solid (blue): what the proof of Theorem 3 actually gives, "
    "2/<i>n</i><sup>(<i>c</i>/2) ln(<i>c</i>/2) − <i>c</i>/2</sup>, an upper bound for every <i>c</i> that drops below 1 "
    "at <i>c</i> ≈ 5.63 (at 2<i>e</i> ≈ 5.44 as <i>n</i> grows).",
    alt="log-scale plot against c of the exact probability that a 1000-node random treap has height above c ln n, "
        "the note's bound, and the corrected bound")
save("n04-height", html)
assert all(nv < ev for c, nv, ev in zip(cs, note, ex) if c >= 2.86 - 1e-9) and all(nv >= 1 for c, nv in zip(cs, note) if c < 2.815)
assert all(cv >= ev for cv, ev in zip(corr, ex))
c_one = [c for c in np.linspace(5.5, 5.8, 3001) if 2 / n ** ((c / 2) * math.log(c / 2) - c / 2) < 1][0]
assert abs(c_one - 5.63) < 0.005, c_one
