#!/usr/bin/env python3
"""Figures for Extended Dance Remix B (Faster Exponential Algorithms). Writes tools/figs/nb-<name>.html; then run
tools/assemble.py on content/4-lecture-notes/b-fast-exponential-algorithms.md. Every number drawn is computed here
(dominant roots of the characteristic polynomials, brute-force independent sets); tools/checks/nb.py re-checks them."""
import itertools
import math
import os

import numpy as np

from figlib import SVG, SERIF_IT

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")
os.makedirs(OUT, exist_ok=True)
BAR = "̅"  # combining overline: x̅


def save(name, html):
    with open(os.path.join(OUT, name + ".html"), "w", encoding="utf-8") as f:
        f.write(html + "\n")
    print("wrote", name)


def root(coeffs):
    r = [z.real for z in np.roots(coeffs) if abs(z.imag) < 1e-9 and z.real > 0]
    assert len(r) == 1
    return r[0]


lam3 = root([1, -1, -1, -1])
lamF = root([1, 0, -2, -2])
assert f"{lam3:.4f}" == "1.8393" and f"{lamF:.4f}" == "1.7693"

# ====================================================================== the two 3SAT branching rules
S = SVG(640, 268)


def node(x, y, label, sub, hi=False):
    col = "var(--hi)" if hi else "currentColor"
    w = max(46, 11 * len(label.replace(BAR, "")) + 14)
    S.rect(x - w / 2, y - 15, w, 30, rx=15, stroke=col, fill="var(--paper)", width=1.4)
    S.text(x, y + 1, label, size=15, font=SERIF_IT, italic=True, color=col)
    if sub:
        S.text(x, y + 30, sub, size=12.5, color="var(--muted)")


def tree(cx, title, clause, kids, rec):
    S.text(cx, 18, title, size=13.5, weight=600)
    S.text(cx, 40, clause, size=14, font=SERIF_IT, italic=True)
    node(cx, 76, "Φ", "")
    S.text(cx + 30, 76, "n variables", size=12.5, color="var(--muted)", anchor="start")
    for (x, lab, sub, elab) in kids:
        S.line(cx, 91, x, 157, width=1.2, color="currentColor")
        node(x, 172, lab, sub)
    S.text(cx, 236, rec[0], size=13.5, font=SERIF_IT, italic=True)
    S.text(cx, 256, rec[1], size=12.5, color="var(--muted)")


tree(160, "3Sat", f"(x ∨ y ∨ z) ∧ Φ′",
     [(58, "Φ′|x", "≤ n − 1", "x"), (160, f"Φ′|x{BAR}y", "≤ n − 2", f"x{BAR}y"),
      (262, f"Φ′|x{BAR}y{BAR}z", "≤ n − 3", f"x{BAR}y{BAR}z")],
     ("T(n) = T(n−1) + T(n−2) + T(n−3)", f"λ = {lam3:.4f}"))
tree(480, "Faster3Sat (no pure literal)", f"(x ∨ y ∨ z) ∧ (x{BAR} ∨ u ∨ v) ∧ Φ′",
     [(366, "Φ|xu", "≤ n − 2", "xu"), (442, f"Φ|xu{BAR}v", "≤ n − 3", f"xu{BAR}v"),
      (518, f"Φ|x{BAR}y", "≤ n − 2", f"x{BAR}y"), (598, f"Φ|x{BAR}y{BAR}z", "≤ n − 3", f"x{BAR}y{BAR}z")],
     ("T(n) = 2T(n−2) + 2T(n−3)", f"λ = {lamF:.4f}"))
save("nb-3sat", S.figure(
    "<strong>Two branching rules for 3Sat.</strong> Left: the first clause (<i>x</i> ∨ <i>y</i> ∨ <i>z</i>) must be "
    "satisfied by <i>x</i>, or else by <i>y</i> with <i>x</i> false, or else by <i>z</i> with both false; the three "
    "branches fix 1, 2 and 3 variables. Right: when <i>x</i> is not pure, a second clause contains <i>x̅</i>; if "
    "<i>x</i> is true that clause needs <i>u</i> or (<i>u̅</i> and <i>v</i>), so every branch fixes at least 2 variables. "
    "λ is the largest root of the characteristic polynomial, and the running time is <i>O</i>(λ<sup><i>n</i></sup> "
    "poly(<i>n</i>)).",
    alt="two recursion trees: 3Sat with three children losing 1, 2, 3 variables; Faster3Sat with four children losing 2, 3, 2, 3"))

# ====================================================================== independent-set case analysis


def brute_mis(V, E):
    adj = {v: set() for v in V}
    for a, b in E:
        adj[a].add(b)
        adj[b].add(a)
    for k in range(len(V), -1, -1):
        for S_ in itertools.combinations(V, k):
            if all(not (adj[u] & set(S_)) for u in S_):
                return k, set(S_)
    return 0, set()


M = SVG(640, 250)


def draw_graph(pos, E, hi=(), removed=(), chosen=()):
    for a, b in E:
        (x1, y1), (x2, y2) = pos[a], pos[b]
        M.line(x1, y1, x2, y2, width=1.3, color="currentColor")
    for v, (x, y) in pos.items():
        if v in chosen:
            M.circle(x, y, 11, stroke="var(--hi)", fill="var(--hi)", width=1.4)
        elif v in hi:
            M.circle(x, y, 11, stroke="var(--hi)", fill="var(--paper)", width=2.2)
        elif v in removed:
            M.circle(x, y, 11, stroke="var(--accent)", fill="var(--accent)", width=1.4, fill_opacity=0.35)
        else:
            M.circle(x, y, 11, stroke="currentColor", fill="var(--paper)", width=1.4)


# (a) degree <= 1
pa = {"v": (40, 110), "w": (92, 110), "a": (150, 70), "b": (160, 140), "c": (104, 168)}
Ea = [("v", "w"), ("w", "a"), ("w", "b"), ("a", "b"), ("b", "c")]
assert sum(1 for e in Ea if "v" in e) == 1
M.rect(20, 86, 96, 48, rx=24, stroke="var(--accent)", fill="none", width=1.2, dash="4 3")
draw_graph(pa, Ea, hi={"v"}, removed={"w"})
M.text(40, 74, "v", size=15, font=SERIF_IT, italic=True, color="var(--hi)")
M.text(92, 74, "w", size=15, font=SERIF_IT, italic=True)
M.text(100, 18, "deg v ≤ 1: take v", size=13.5, weight=600)
M.text(100, 206, "one call on G ∖ N(v)", size=12.5)
M.text(100, 224, "(at most n − 1 vertices)", size=12.5, color="var(--muted)")

# (b) degree >= 3
pb = {"v": (322, 108), "a": (276, 66), "b": (368, 66), "c": (322, 160), "d": (400, 140), "e": (252, 150)}
Eb = [("v", "a"), ("v", "b"), ("v", "c"), ("a", "b"), ("b", "d"), ("c", "d"), ("c", "e"), ("a", "e")]
assert sum(1 for e in Eb if "v" in e) == 3
draw_graph(pb, Eb, hi={"v"}, removed={"a", "b", "c"})
M.text(340, 124, "v", size=15, font=SERIF_IT, italic=True, color="var(--hi)", halo=True)
M.text(326, 18, "deg v ≥ 3: branch", size=13.5, weight=600)
M.text(326, 206, "with v: G ∖ N(v), ≤ n − 4 vertices", size=12.5)
M.text(326, 224, "without v: G − v, n − 1 vertices", size=12.5)

# (c) all degrees 2: disjoint cycles
c5 = [(480 + 34 * math.cos(math.pi / 2 + 2 * math.pi * k / 5), 104 - 34 * math.sin(math.pi / 2 + 2 * math.pi * k / 5)) for k in range(5)]
c4 = [(575 + 30 * math.cos(math.pi / 4 + math.pi / 2 * k), 108 - 30 * math.sin(math.pi / 4 + math.pi / 2 * k)) for k in range(4)]
pc = {f"p{k}": c5[k] for k in range(5)}
pc.update({f"q{k}": c4[k] for k in range(4)})
Ec = [(f"p{k}", f"p{(k + 1) % 5}") for k in range(5)] + [(f"q{k}", f"q{(k + 1) % 4}") for k in range(4)]
mis, S_ = brute_mis(list(pc), Ec)
assert mis == 5 // 2 + 4 // 2 == 4
chosen = {"p1", "p3", "q0", "q2"}
assert len(chosen) == 4 and all(not (a in chosen and b in chosen) for a, b in Ec)
draw_graph(pc, Ec, chosen=chosen)
M.text(530, 18, "every degree 2: cycles", size=13.5, weight=600)
M.text(530, 206, "⌊5/2⌋ + ⌊4/2⌋ = 4", size=12.5)
M.text(530, 224, "no recursion at all", size=12.5, color="var(--muted)")
M.line(212, 30, 212, 230, color="var(--muted)", width=0.8, dash="2 4")
M.line(436, 30, 436, 230, color="var(--muted)", width=0.8, dash="2 4")
save("nb-mis", M.figure(
    "<strong>The cases of the final MaximumIndSetSize (Figure B.3).</strong> Left: a vertex <i>v</i> of degree 0 or 1 "
    "can always be taken (some maximum independent set contains it), and <i>v</i> and its neighbor <i>w</i> (shaded) "
    "disappear. Middle: a vertex of degree at least 3 is branched on; taking it deletes its closed neighborhood of at "
    "least 4 vertices. Right: if neither applies every vertex has degree 2, the graph is a union of cycles, and a cycle "
    "of length <i>k</i> contributes ⌊<i>k</i>/2⌋ (one optimal choice filled). Worst case: <i>T</i>(<i>n</i>) = "
    "<i>T</i>(<i>n</i>−1) + <i>T</i>(<i>n</i>−4) + poly(<i>n</i>) = <i>O</i>(1.3803<sup><i>n</i></sup>).",
    alt="three small graphs: a degree-one vertex taken greedily, a degree-three vertex branched on, and a 5-cycle plus a 4-cycle"))
assert f"{root([1, -1, 0, 0, -1]):.4f}" == "1.3803"
