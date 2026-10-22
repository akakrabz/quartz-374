#!/usr/bin/env python3
"""Figures for the lab pages (content/3-homework-and-exams/lab-*.md). Writes tools/figs/lab-*.html; then run
tools/assemble.py on the page. Each lab has its own clearly marked, self-contained section below."""

# ==================================================================================================== Lab 8 (8a, 8b)
# Figures for content/3-homework-and-exams/lab-08a.md and lab-08b.md.  Every jump set, total and node value drawn here
# is recomputed below by brute force; tools/checks/labs_08.py checks the same numbers independently.
def _lab8_figures():
    import itertools as _it
    import os as _os
    import sys as _sys
    _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
    from figlib import SVG as _SVG, Tree as _Tree, MONO as _MONO, SERIF_IT as _SERIF

    out = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "figs")
    _os.makedirs(out, exist_ok=True)

    def save(name, html):
        with open(_os.path.join(out, name + ".html"), "w", encoding="utf-8") as f:
            f.write(html + "\n")
        print("wrote", name)

    # ------------------------------------------------------------------ 8a: the ramps example
    R = [2, 4, 7, 12, 15, 19, 23]
    L = [3, 5, 4, 2, 6, 9, 1]
    n = len(R)

    def ok(S):
        land = float("-inf")
        for s in sorted(S):
            if not R[s] > land:
                return False
            land = R[s] + L[s]
        return True

    def best_one(k=None):
        best = (0, ())
        for r in range(n + 1):
            if k is not None and r > k:
                break
            for S in _it.combinations(range(n), r):
                if ok(S) and sum(L[s] for s in S) > best[0]:
                    best = (sum(L[s] for s in S), S)
        return best

    def best_two(k):
        best = (0, None)
        for a in _it.product((0, 1, 2), repeat=n):
            A = tuple(s for s in range(n) if a[s] == 1)
            B = tuple(s for s in range(n) if a[s] == 2)
            if len(A) <= k and len(B) <= k and ok(A) and ok(B):
                v = sum(L[s] for s in A + B)
                if v > best[0] or (v == best[0] and best[1] and (A, B) < best[1]):
                    best = (v, (A, B))
        return best

    v1, S1 = best_one()
    assert (v1, S1) == (18, (0, 2, 3, 5))
    land, G = float("-inf"), []
    for i in range(n):
        if R[i] > land:
            G.append(i)
            land = R[i] + L[i]
    assert G == [0, 2, 3, 4, 6] and sum(L[g] for g in G) == 16
    v2, (A2, B2) = best_two(2)
    assert v2 == 24 and (A2, B2) == ((1, 4), (2, 5))  # Amy {2, 5}, Banjin {3, 6}

    W, X0, U = 640, 112, 17.5   # x of position p: X0 + p * U  (p up to 29)
    tracks = [
        ("one sledder", "best: 18", S1, "var(--accent)"),
        ("jump whenever", "you can: 16", tuple(G), "var(--muted)"),
        ("Amy", "(k = 2)", A2, "var(--accent)"),
        ("Banjin", "(k = 2)", B2, "var(--accent2)"),
    ]
    top, gap = 40, 74
    ybase = [top + 40 + gap * t for t in range(len(tracks))]
    H = ybase[-1] + 34
    S = _SVG(W, H, font_size=13)

    def X(p):
        return X0 + p * U

    # ramp numbers on top, positions at the bottom
    for i in range(n):
        S.text(X(R[i]), 14, str(i + 1), size=12, font=_MONO, weight="600")
        S.line(X(R[i]), 22, X(R[i]), ybase[-1] + 4, color="var(--muted)", width=0.6, dash="2 3", opacity=0.6)
    for p in range(0, 30, 5):
        S.text(X(p), ybase[-1] + 20, str(p), size=10.5, color="var(--muted)")
    S.text(14, 14, "ramp", size=11, color="var(--muted)", anchor="start")
    S.text(14, ybase[-1] + 20, "position", size=11, color="var(--muted)", anchor="start")

    for t, (name, sub, jumps, col) in enumerate(tracks):
        y = ybase[t]
        if t == 2:
            S.line(14, y - 52, W - 14, y - 52, color="var(--muted)", width=0.8, opacity=0.7)
        S.text(14, y - 22, name, size=12.5, anchor="start", weight="600")
        S.text(14, y - 7, sub, size=11.5, anchor="start", color="var(--muted)")
        S.line(X(0), y, X(29), y, width=1.0, opacity=0.7)
        for i in range(n):
            x = X(R[i])
            used = i in jumps
            flown = any(R[j] < R[i] <= R[j] + L[j] for j in jumps)
            c = col if used else "currentColor"
            op = 0.35 if flown else (1 if used else 0.75)
            S.add(f'<path d="M{x - 7:.1f},{y:.1f} L{x + 2:.1f},{y:.1f} L{x + 2:.1f},{y - 7:.1f} z" fill="{c}" '
                  f'stroke="{c}" stroke-width="1" opacity="{op}"/>')
        for j in jumps:
            x1, x2 = X(R[j]) + 2, X(R[j] + L[j])
            h = 10 + 2.6 * L[j]
            S.path(f"M{x1:.1f},{y - 7:.1f} Q{(x1 + x2) / 2:.1f},{y - 7 - 2 * h:.1f} {x2:.1f},{y - 1:.1f}",
                   color=col, width=2.0, arrow=True)
            S.text((x1 + x2) / 2, y - 7 - h - 6, str(L[j]), size=11.5, color=col, halo=True, weight="600")
    save("lab-08a-ramps", S.figure(
        "<strong>The example: ramps at 2, 4, 7, 12, 15, 19, 23 with jump lengths 3, 5, 4, 2, 6, 9, 1.</strong> "
        "Faded ramps are flown over. Top: the best single run (ramps 1, 3, 4, 6; 18 in the air). "
        "Jumping at every ramp you reach gets only 16, because the jump at ramp 5 flies over the long jump at ramp 6. "
        "Bottom: two sledders with at most two jumps each and no shared ramp (Amy 2 and 5, Banjin 3 and 6; 24 in total). "
        "Alone, each could get 14 with ramps 2 and 6, but ramp 6 can be used only once.",
        alt="four rows of ramps along a hill with jump arcs for the optimal solutions"))

    # ------------------------------------------------------------------ 8b: expression tree for 14 with eight 1s
    def T(op, *kids):
        return (op, list(kids))

    one = ("1", [])

    def leaf():
        return ("1", [])

    two = lambda: T("+", leaf(), leaf())
    three = T("+", two(), leaf())
    seven = T("+", T("×", three, two()), leaf())
    root = T("×", two(), seven)

    def val(nd):
        lab, kids = nd
        if not kids:
            return 1
        a, b = val(kids[0]), val(kids[1])
        return a + b if lab == "+" else a * b

    def ones(nd):
        return 1 if not nd[1] else sum(ones(k) for k in nd[1])

    assert val(root) == 14 and ones(root) == 8
    Tr = _Tree(420, 266, font_size=14)
    pos = Tr.draw(root, 60, 30, level_h=44, leaf_w=36, circle_internal=True)

    def annotate(nd):
        lab, kids = nd
        if kids:
            x, y = pos[id(nd)]
            Tr.text(x + 16, y - 12, f"{val(nd)}", size=11.5, anchor="start", color="var(--accent)", weight="600",
                    halo=True)
            for k in kids:
                annotate(k)

    annotate(root)
    Tr.text(410, 26, "value at each operator", size=11, anchor="end", color="var(--accent)")
    save("lab-08b-tree14", Tr.figure(
        "<strong>The expression tree of (1+1)×(((1+1+1)×(1+1))+1).</strong> Leaves are the eight 1s; each operator "
        "is labeled with the value of its subtree. The root splits 14 as 2 × 7, so its cost is MinOnes(2) + MinOnes(7) "
        "= 2 + 6; the + below it splits 7 as 6 + 1. Parentheses are only how the tree is written down, and they "
        "cost nothing.",
        alt="binary expression tree with eight leaves equal to 1 and value 14 at the root"))

    # ------------------------------------------------------------------ 8b: the maximum 21 for 1+3-2-5+1-6+7
    def N(x):
        return (str(x), [])

    plus13 = T("+", N(1), N(3))
    inner = T("−", T("−", N(2), T("+", N(5), N(1))), T("+", N(6), N(7)))
    root2 = T("−", plus13, inner)

    def val2(nd):
        lab, kids = nd
        if not kids:
            return int(lab)
        a, b = val2(kids[0]), val2(kids[1])
        return a + b if lab == "+" else a - b

    assert val2(root2) == 21 and val2(inner) == -17 and val2(plus13) == 4
    Tr2 = _Tree(400, 222, font_size=14)
    pos2 = Tr2.draw(root2, 66, 30, level_h=44, leaf_w=38, circle_internal=True, hi={id(inner)})

    def annotate2(nd):
        lab, kids = nd
        if kids:
            x, y = pos2[id(nd)]
            col = "var(--hi)" if nd is inner else "var(--accent)"
            Tr2.text(x + 16, y - 12, f"{val2(nd)}", size=11.5, anchor="start", color=col, weight="600", halo=True)
            for k in kids:
                annotate2(k)

    annotate2(root2)
    save("lab-08b-max21", Tr2.figure(
        "<strong>A best parenthesization of 1+3−2−5+1−6+7: (1+3) − (2 − (5+1) − (6+7)) = 21.</strong> "
        "The root subtracts the right part, so the right part 2−5+1−6+7 must be made as <em>small</em> as possible "
        "(−17, its minimum; red), while the left part 1+3 is made as large as possible (4). This is why the "
        "recurrence for MaxVal needs MinVal.",
        alt="expression tree with root minus, left subtree 1+3 and right subtree of value minus 17"))


_lab8_figures()
# ==================================================================================================== end of Lab 8


# ==================================================================================================== Lab 6 (6a, 6b)
# Figures for content/3-homework-and-exams/lab-06a.md and lab-06b.md (self-contained: own imports and helpers,
# module-level names carry a 6). The numbers drawn are the handout examples; tools/checks/labs_06.py checks them.
import os as _os6
import sys as _sys6

_sys6.path.insert(0, _os6.path.dirname(_os6.path.abspath(__file__)))
from figlib import SVG as _SVG6, SANS as _SANS6, SERIF_IT as _SERIF6  # noqa: E402

_OUT6 = _os6.path.join(_os6.path.dirname(_os6.path.abspath(__file__)), "figs")


def _save6(name, html):
    _os6.makedirs(_OUT6, exist_ok=True)
    with open(_os6.path.join(_OUT6, name + ".html"), "w", encoding="utf-8") as f:
        f.write(html + "\n")
    print("wrote", name)


def _lab06a_median_fig():
    """Lab 6a, Problem 3: one step of the two-array median on the handout's example (n = 8, m = 4)."""
    A = [0, 1, 6, 9, 12, 13, 18, 20]
    B = [2, 4, 5, 8, 17, 19, 21, 23]
    W, H = 620, 228
    S = _SVG6(W, H, font_size=14)
    x0, cw, ch = 92, 46, 32
    yA, yB = 58, 138
    S.text(x0 - 30, yA + ch / 2, "A", size=16, font=_SERIF6, italic=True)
    S.text(x0 - 30, yB + ch / 2, "B", size=16, font=_SERIF6, italic=True)
    for i in range(8):
        S.text(x0 + cw * i + cw / 2, yA - 12, str(i + 1), size=11.5, color="var(--muted)")
    for row, vals, y in (("A", A, yA), ("B", B, yB)):
        for i, v in enumerate(vals):
            x = x0 + cw * i
            gone = (row == "A" and i >= 4) or (row == "B" and i < 4)
            if gone:
                S.rect(x, y, cw, ch, stroke="var(--muted)", fill="var(--muted)", fill_opacity=0.16, width=1.1)
                S.text(x + cw / 2, y + ch / 2 + 0.5, str(v), size=14, color="var(--muted)")
            else:
                S.rect(x, y, cw, ch, stroke="currentColor", fill="var(--paper)", width=1.2)
                S.text(x + cw / 2, y + ch / 2 + 0.5, str(v), size=14)
    # the compared pair (column 4)
    xc = x0 + cw * 3
    S.rect(xc + 1.5, yA + 1.5, cw - 3, ch - 3, stroke="var(--accent)", width=2.4)
    S.rect(xc + 1.5, yB + 1.5, cw - 3, ch - 3, stroke="var(--accent)", width=2.4)
    S.text(xc + cw / 2, (yA + ch + yB) / 2, "9 > 8", size=13.5, color="var(--accent)", weight=700, halo=True)
    # braces for the discarded parts
    xr0, xr1 = x0 + cw * 4, x0 + cw * 8
    S.path(f"M{xr0 + 3},{yA - 22} L{xr0 + 3},{yA - 27} L{xr1 - 3},{yA - 27} L{xr1 - 3},{yA - 22}",
           color="var(--hi)", width=1.4)
    S.text((xr0 + xr1) / 2, yA - 37, "all above the median: drop", size=12.5, color="var(--hi)", weight=600)
    xl0, xl1 = x0, x0 + cw * 4
    S.path(f"M{xl0 + 3},{yB + ch + 6} L{xl0 + 3},{yB + ch + 11} L{xl1 - 3},{yB + ch + 11} L{xl1 - 3},{yB + ch + 6}",
           color="var(--hi)", width=1.4)
    S.text((xl0 + xl1) / 2, yB + ch + 24, "all below the median: drop", size=12.5, color="var(--hi)", weight=600)
    # what is kept
    xk = x0 + cw * 8 + 14
    S.text(xk, yA + ch / 2, "keep A[1..4]", size=12.5, anchor="start", color="var(--accent2)", weight=600)
    S.text(xk, yB + ch / 2, "keep B[5..8]", size=12.5, anchor="start", color="var(--accent2)", weight=600)
    return S.figure(
        "<strong>One step of the two-array median.</strong> With <i>n</i> = 8 compare the middle entries "
        "<i>A</i>[4] = 9 and <i>B</i>[4] = 8. Since 9 &gt; 8, seven elements (<i>A</i>[1..3] and <i>B</i>[1..4]) are "
        "smaller than <i>A</i>[4], so it is at least the 8th smallest and everything after it in <i>A</i> is above the "
        "median; every element of <i>B</i>[1..4] has at least nine larger elements, so all four are below it. Dropping "
        "four from each side leaves two sorted arrays of length 4 whose median (4th smallest) is still 9.",
        alt="two sorted arrays of eight numbers; the compared middle pair 9 and 8 is highlighted, the last four of A "
            "and the first four of B are greyed out as dropped")


def _sup6(base, exp, tail=""):
    return (f'{base}<tspan dy="-6" style="font-size:10px">{exp}</tspan>'
            + (f'<tspan dy="6">{tail}</tspan>' if tail else '<tspan dy="6"> </tspan>'))


def _tree_row6(S, y0, title_html, levels, sums_html, verdict_html, note):
    S.add(f'<text x="14" y="{y0}" text-anchor="start" dominant-baseline="central" fill="currentColor" '
          f'style="font-size:13px;font-family:{_SANS6};font-weight:600;">{title_html}</text>')
    S.add(f'<text x="486" y="{y0}" text-anchor="start" dominant-baseline="central" fill="var(--hi)" '
          f'style="font-size:13.5px;font-family:{_SANS6};font-weight:700;">{verdict_html}</text>')
    left, right = 18, 440
    ys = [y0 + 30 + 31 * d for d in range(len(levels))]
    xs = []
    for d, lab in enumerate(levels):
        k = len(lab)
        xs.append([left + (right - left) * (i + 0.5) / k for i in range(k)])
    for d in range(1, len(levels)):
        per = len(levels[d]) // len(levels[d - 1])
        for i, x in enumerate(xs[d]):
            px = xs[d - 1][i // per]
            S.line(px, ys[d - 1] + 9, x, ys[d] - 9, width=1.1, opacity=0.5)
    for d, lab in enumerate(levels):
        w = 30 if d == 0 else 36
        for x, t in zip(xs[d], lab):
            S.rect(x - w / 2, ys[d] - 9, w, 18, rx=4, stroke="currentColor", fill="var(--paper)", width=1.1)
            S.text(x, ys[d] + 0.5, t, size=12.5, font=_SERIF6, italic=True)
    S.line(466, ys[0] - 12, 466, ys[-1] + 12, width=1, color="var(--muted)", dash="3 3")
    for d, s in enumerate(sums_html):
        S.add(f'<text x="486" y="{ys[d] + 0.5}" text-anchor="start" dominant-baseline="central" fill="var(--accent)" '
              f'style="font-size:13px;font-family:{_SERIF6};font-style:italic;">{s}</text>')
    S.text(486, ys[-1] + 24, note, anchor="start", size=12.5, color="var(--accent)")


def _lab06b_trees_fig():
    W, H = 640, 468
    S = _SVG6(W, H, font_size=13)
    S.text(486, 14, "level sums", anchor="start", size=12, color="var(--muted)")
    N = _sup6("n", "lg 3")
    _tree_row6(S, 40, "Problem 1:  T(n) = T(n/2) + " + _sup6("n", "lg 3", "  (Piṅgala)"),
               [["n"], ["n/2"], ["n/4"]],
               [N, _sup6("n", "lg 3", "/3"), _sup6("n", "lg 3", "/9")],
               "Θ(" + _sup6("n", "lg 3", ")"), "root dominates")
    _tree_row6(S, 186, "Problem 2:  T(n) = 3T(n/2) + " + _sup6("n", "lg 3", "  (three calls)"),
               [["n"], ["n/2"] * 3, ["n/4"] * 9],
               [N, N, N],
               "Θ(" + _sup6("n", "lg 3", " log n)"), "× (lg n + 1) levels")
    _tree_row6(S, 332, "Problem 3:  T(n) = 2T(n/2) + " + _sup6("n", "lg 3", "  (two calls)"),
               [["n"], ["n/2"] * 2, ["n/4"] * 4],
               [N, "(2/3) " + N, "(4/9) " + N],
               "Θ(" + _sup6("n", "lg 3", ")"), "root dominates")
    return S.figure(
        "<strong>Three recursion trees for Lab 6b.</strong> Every node is a call on the size shown (in bits); its own "
        "work is one Karatsuba multiplication of numbers with a proportional number of digits, (size)<sup>lg 3</sup>, "
        "and halving the size divides that by 2<sup>lg 3</sup> = 3. A path (Problem 1) and two children per node "
        "(Problem 3) make the level sums shrink, so the root's multiplication dominates; three children per node "
        "(Problem 2: <i>a</i>, 2<sup><i>n</i>/2</sup> and <i>b</i>) exactly cancel the factor 3, so all lg <i>n</i> + 1 "
        "levels cost the same.",
        alt="three recursion trees: a path, a ternary tree and a binary tree, with level sums n^lg3 shrinking by 3, "
            "constant, and shrinking by 2/3")


def _lab6_figures():
    _save6("lab-06a-median-step", _lab06a_median_fig())
    _save6("lab-06b-trees", _lab06b_trees_fig())


_lab6_figures()
# ==================================================================================================== end of Lab 6



# ======================================================================================================== Lab 7
# Lab 7 (lab-07a / lab-07b): written by the Lab 7 page author; self-contained (own imports, l7_ names only).
# Figures: lab-07b-dependencies (memo tables, dependencies, evaluation orders) and lab-07b-zigzag (turning points).
# Every number drawn is computed here; tools/checks/labs_07.py re-checks the zigzag's points.
def l7_figures():
    import os as l7_os
    from figlib import SVG as L7SVG, SERIF_IT as L7_SERIF, MONO as L7_MONO

    out_dir = l7_os.path.join(l7_os.path.dirname(l7_os.path.abspath(__file__)), "figs")
    l7_os.makedirs(out_dir, exist_ok=True)

    def save(name, html):
        with open(l7_os.path.join(out_dir, name + ".html"), "w", encoding="utf-8") as f:
            f.write(html + "\n")
        print("wrote", name)

    # ------------------------------------------------------------------ 1. dependencies and evaluation orders
    S = L7SVG(640, 412)
    cs, G = 18, 6

    def grid(x0, y0, used, base=()):
        for r in range(G):
            for c in range(G):
                if (r, c) in base:
                    S.rect(x0 + c * cs, y0 + r * cs, cs, cs, stroke="none", fill="var(--muted)", fill_opacity=0.35, width=0)
                if used(r, c):
                    S.rect(x0 + c * cs, y0 + r * cs, cs, cs, stroke="currentColor", fill="none", width=0.5)
        S.rect(x0, y0, G * cs, G * cs, stroke="currentColor", fill="none", width=1.2)

    def cell(x0, y0, r, c, kind):
        if kind == "target":
            S.rect(x0 + c * cs, y0 + r * cs, cs, cs, stroke="var(--hi)", fill="var(--hi)", fill_opacity=0.35, width=1.6)
        else:
            S.rect(x0 + c * cs, y0 + r * cs, cs, cs, stroke="var(--accent)", fill="var(--accent)", fill_opacity=0.25,
                   width=1.2)

    def ctr(x0, y0, r, c):
        return x0 + c * cs + cs / 2, y0 + r * cs + cs / 2

    def axes(x0, y0, rlab, clab):
        S.line(x0, y0 - 9, x0 + G * cs, y0 - 9, width=1.0, arrow=True)
        S.text(x0 + G * cs / 2, y0 - 18, clab, size=13, font=L7_SERIF, italic=True)
        S.line(x0 - 9, y0, x0 - 9, y0 + G * cs, width=1.0, arrow=True)
        S.text(x0 - 19, y0 + G * cs / 2, rlab, size=13, font=L7_SERIF, italic=True)

    def outer(x1, y1, x2, y2):
        S.line(x1, y1, x2, y2, width=4.2, color="var(--accent2)", arrow=True)

    def inner(x1, y1, x2, y2, both=False):
        if both:
            S.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="var(--accent2)" '
                  f'stroke-width="1.3" stroke-linecap="round" marker-start="url(#ARR)" marker-end="url(#ARR)"/>')
        else:
            S.line(x1, y1, x2, y2, width=1.3, color="var(--accent2)", arrow=True)

    def dep_arrow(r0, c0, r1, c1, x0, y0):
        sx, sy = ctr(x0, y0, r0, c0)
        tx, ty = ctr(x0, y0, r1, c1)
        dx, dy = tx - sx, ty - sy
        S.line(sx + dx * 0.25, sy + dy * 0.25, tx - dx * 0.38, ty - dy * 0.38, width=1.4, color="var(--hi)", arrow=True)

    TOP, BOT = 66, 236
    cols = [62, 272, 482]
    titles = [("LDSsmaller[i, j]", "also LASabove, LASbelow"), ("LXS[i, j]", "convex, Problem 3"),
              ("LPS[i, j]", "also SPS")]
    for x, (t, sub) in zip(cols, titles):
        S.text(x + G * cs / 2, 13, t, size=13, font=L7_MONO)
        S.text(x + G * cs / 2, 30, sub, size=12, color="var(--muted)")

    # panel A: rows i = 0..5, columns j = 1..6 (6 = n + 1, the base column); used where i < j
    xa = cols[0]
    for y0 in (TOP, BOT):
        grid(xa, y0, lambda r, c: r <= c, {(r, 5) for r in range(G)})
        axes(xa, y0, "i", "j")
    cell(xa, TOP, 1, 2, "target")            # (i, j) = (1, 3)
    cell(xa, TOP, 1, 3, "dep")               # (i, j + 1) = (1, 4)
    cell(xa, TOP, 3, 3, "dep")               # (j, j + 1) = (3, 4)
    dep_arrow(1, 3, 1, 2, xa, TOP)
    ax, ay = ctr(xa, TOP, 1, 2)
    cx_, cy_ = ctr(xa, TOP, 3, 3)
    S.path(f"M{cx_ - 3},{cy_ - 6} Q{ax + 2},{cy_ - 4} {ax + 1},{ay + 7}", color="var(--hi)", width=1.4, arrow=True)
    outer(xa + G * cs - 4, BOT + G * cs + 14, xa + 8, BOT + G * cs + 14)
    for c in (4, 3, 2, 1):
        x = xa + c * cs + cs / 2
        inner(x, BOT + 5, x, BOT + (c + 1) * cs - 5, both=True)

    # panel B: LXS, rows i = 1..6, columns j = 1..6; used where i < j; no base cells (the value 2 is the default)
    xb = cols[1]
    for y0 in (TOP, BOT):
        grid(xb, y0, lambda r, c: r < c)
        axes(xb, y0, "i", "j")
    cell(xb, TOP, 1, 2, "target")            # (i, j) = (2, 3)
    for c in (3, 4, 5):                      # (j, k) = (3, 4), (3, 5), (3, 6)
        cell(xb, TOP, 2, c, "dep")
    tx, ty = ctr(xb, TOP, 1, 2)
    sx, sy = ctr(xb, TOP, 2, 3)
    S.line(sx - 6, sy - 3, tx + 4, ty + 6, width=1.4, color="var(--hi)", arrow=True)
    outer(xb + G * cs + 14, BOT + G * cs - 4, xb + G * cs + 14, BOT + 4)
    for r in (4, 3, 2, 1, 0):
        y = BOT + r * cs + cs / 2
        inner(xb + (r + 1) * cs + 4, y, xb + G * cs - 4, y, both=True)

    # panel C: LPS, rows i = 1..6 (6 = n + 1), columns j = 0..5; used where j >= i - 1; base: j = i - 1 and j = i
    xc = cols[2]
    for y0 in (TOP, BOT):
        grid(xc, y0, lambda r, c: c >= r, {(r, r) for r in range(G)} | {(r, r + 1) for r in range(G - 1)})
        axes(xc, y0, "i", "j")
    cell(xc, TOP, 1, 4, "target")            # (i, j) = (2, 4)
    for (r, c) in ((2, 4), (1, 3), (2, 3)):  # (i + 1, j), (i, j - 1), (i + 1, j - 1)
        cell(xc, TOP, r, c, "dep")
        dep_arrow(r, c, 1, 4, xc, TOP)
    outer(xc + G * cs + 14, BOT + G * cs - 4, xc + G * cs + 14, BOT + 4)
    for r in (4, 3, 2, 1, 0):
        y = BOT + r * cs + cs / 2
        inner(xc + r * cs + 4, y, xc + G * cs - 4, y)

    notes = [("reads column j + 1:", "columns right to left"), ("reads row j, right of it:", "rows bottom up"),
             ("reads three neighbors:", "rows bottom up, left to right")]
    for x, (a, b) in zip(cols, notes):
        S.text(x + G * cs / 2, BOT + G * cs + 40, a, size=12, color="var(--muted)")
        S.text(x + G * cs / 2, BOT + G * cs + 56, b, size=12, color="var(--muted)")
    save("lab-07b-dependencies", S.figure(
        "<strong>The three table shapes of Lab 7b.</strong> Top: the entry being computed (red) and the entries it "
        "reads (blue); gray cells are base cases, blank cells are never used. Bottom: a valid evaluation order — the "
        "thick arrow is the outer loop, thin arrows the inner loop (double-headed: any direction). "
        "<i>LDSsmaller</i>[<i>i</i>, <i>j</i>] (and both alternating tables) reads only column <i>j</i> + 1; "
        "<i>LXS</i>[<i>i</i>, <i>j</i>] reads the entries (<i>j</i>, <i>k</i>), <i>k</i> &gt; <i>j</i>, of a lower row; "
        "<i>LPS</i>[<i>i</i>, <i>j</i>] and <i>SPS</i>[<i>i</i>, <i>j</i>] read the entry below, the one to the left "
        "and the one diagonally between them.",
        alt="three small tables showing which entries each Lab 7b dynamic program reads, and the order to fill them"))

    # ------------------------------------------------------------------ 2. turning points of the handout's array
    A = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5, 8, 9, 7, 9, 3, 2, 3, 8, 4, 6, 2, 7]
    n = len(A)
    C = [float("-inf")] + A                   # no equal neighbors in A, so C needs no collapsing
    assert all(A[i] != A[i + 1] for i in range(n - 1))
    turn = [k for k in range(1, n) if C[k] > max(C[k - 1], C[k + 1]) or C[k] < min(C[k - 1], C[k + 1])] + [n]
    assert len(turn) == 17
    S = L7SVG(620, 222)
    x0, dx = 74, 23.5
    X = lambda k: x0 + (k - 1) * dx
    Y = lambda v: 168 - 15 * v
    row = 196
    pts = " ".join(f"{X(k):.1f},{Y(A[k - 1]):.1f}" for k in range(1, n + 1))
    S.add(f'<polyline points="{pts}" fill="none" stroke="var(--muted)" stroke-width="1.6" stroke-linejoin="round"/>')
    S.line(38, row - 14, X(1) - 3, Y(A[0]) + 4, color="var(--muted)", width=1.4, dash="4 3")
    S.text(34, row, "−∞", size=13, color="var(--muted)")
    S.text(26, Y(9) - 14, "value", size=12, color="var(--muted)")
    S.line(26, Y(1) + 6, 26, Y(9) - 4, width=1.0, color="var(--muted)", arrow=True)
    for k in range(1, n + 1):
        v = A[k - 1]
        if k in turn:
            S.circle(X(k), Y(v), 5.2, stroke="var(--accent)", fill="var(--accent)", width=1.4)
            S.text(X(k), row, str(v), size=13, color="var(--accent)", weight=700)
        else:
            S.circle(X(k), Y(v), 4.6, stroke="var(--muted)", fill="var(--paper)", width=1.4)
            S.text(X(k), row, str(v), size=13, color="var(--muted)")
    S.text(X(12), 14, "17 turning points (filled) after the sentinel −∞", size=12, color="var(--muted)")
    save("lab-07b-zigzag", S.figure(
        "<strong>Counting turning points.</strong> The handout's array as a profile (position left to right, value "
        "upward) with the sentinel −∞ in front. The filled points are the turning points after the sentinel: every "
        "peak and valley, plus the last element (the first element is a peak because of the sentinel). Read left to "
        "right they form an alternating subsequence of length 17 — 3, 1, 4, 1, 9, 2, 6, 3, 9, 7, 9, 2, 8, 4, 6, 2, 7 — "
        "and no alternating subsequence is longer. The hollow points lie on monotone stretches and are never needed.",
        alt="the example array plotted as a zigzag line with its 17 turning points highlighted"))


l7_figures()
# ======================================================================================================== end of Lab 7


# ==================================================================================================== Lab 9a
# Figures for content/3-homework-and-exams/lab-09a.md (number-maze variants).  The 10-move solution, the forced first
# and last moves and the palindromic examples are recomputed below by search; tools/checks/labs_09a.py checks the same
# claims independently.
def _lab9a_figures():
    import math as _math
    import os as _os
    import sys as _sys
    from collections import deque as _deque
    _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
    from figlib import SVG as _SVG, SERIF_IT as _SERIF

    out = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "figs")
    _os.makedirs(out, exist_ok=True)

    def save(name, html):
        with open(_os.path.join(out, name + ".html"), "w", encoding="utf-8") as f:
            f.write(html + "\n")
        print("wrote", name)

    D4 = {"U": (-1, 0), "D": (1, 0), "L": (0, -1), "R": (0, 1)}
    M = [[3, 5, 7, 4, 6], [5, 3, 1, 5, 3], [2, 8, 3, 1, 4], [4, 5, 7, 2, 3], [3, 1, 3, 2, 5]]  # goal: star, no moves
    n = 5
    G = (n - 1, n - 1)

    def moves(p):
        k = M[p[0]][p[1]]
        for d, (di, dj) in D4.items():
            q = (p[0] + k * di, p[1] + k * dj)
            if 0 <= q[0] < n and 0 <= q[1] < n:
                yield d, k, q

    # the 10-move solution of problem 3: BFS over (square, moves mod 5), then the path
    s0 = ((0, 0), 0)
    par, Q = {s0: None}, _deque([s0])
    while Q:
        u = Q.popleft()
        for d, k, q in moves(u[0]):
            v = (q, (u[1] + 1) % 5)
            if v not in par:
                par[v] = (u, f"{d}{k}")
                Q.append(v)
    v, steps = (G, 0), []
    while par[v] is not None:
        v, mv = par[v]
        steps.append((v[0], mv))
    steps.reverse()
    path10 = [p for p, _ in steps] + [G]
    assert len(steps) == 10 and " ".join(m for _, m in steps) == "R3 D4 L2 R1 U3 L1 R3 L3 R3 D3", steps
    into = lambda b: sorted((p, d, k) for p in [(i, j) for i in range(n) for j in range(n)]
                            for d, k, q in moves(p) if q == b)
    assert into(G) == [((1, 4), "D", 3)] and into((1, 4)) == [((1, 1), "R", 3)]
    assert into((1, 1)) == [((1, 2), "L", 1), ((1, 4), "L", 3)]
    assert sorted(q for _, _, q in moves((0, 0))) == [(0, 3), (3, 0)] and M[0][3] == M[3][0] == 4

    def arc(S, p, q, bend, color, shorten=7, width=1.9, dash=None):
        (x1, y1), (x2, y2) = p, q
        L = _math.hypot(x2 - x1, y2 - y1)
        ux, uy = (x2 - x1) / L, (y2 - y1) / L
        nx, ny = uy, -ux  # left of travel on screen
        cx, cy = (x1 + x2) / 2 + nx * bend, (y1 + y2) / 2 + ny * bend
        sx, sy = x1 + ux * shorten + nx * bend * 0.35, y1 + uy * shorten + ny * bend * 0.35
        ex, ey = x2 - ux * shorten + nx * bend * 0.35, y2 - uy * shorten + ny * bend * 0.35
        S.path(f"M{sx:.1f},{sy:.1f} Q{cx:.1f},{cy:.1f} {ex:.1f},{ey:.1f}", color=color, width=width, arrow=True,
               dash=dash)
        return 0.25 * sx + 0.5 * cx + 0.25 * ex, 0.25 * sy + 0.5 * cy + 0.25 * ey

    def tag(S, x, y, s, color):
        S.circle(x, y, 8, stroke=color, fill="var(--paper)", width=1.2)
        S.text(x, y + 0.5, s, size=11, color=color, weight=600)

    CELL, TOP = 60, 8
    S = _SVG(n * CELL + 16, n * CELL + TOP + 8)
    ox, oy = 8, TOP
    C = lambda v: (ox + v[1] * CELL + CELL / 2, oy + v[0] * CELL + CELL / 2)
    for i in range(n):
        for j in range(n):
            x, y = ox + j * CELL, oy + i * CELL
            if (i, j) in ((0, 3), (3, 0)):
                S.rect(x, y, CELL, CELL, stroke="none", fill="var(--accent)", fill_opacity=0.16, width=0)
            if (i, j) in ((1, 1), (1, 4)):
                S.rect(x, y, CELL, CELL, stroke="none", fill="var(--hi)", fill_opacity=0.10, width=0)
            S.rect(x, y, CELL, CELL, stroke="currentColor", fill="none", width=0.8)
            if (i, j) == G:
                S.text(x + CELL / 2, y + CELL / 2 + 1, "★", size=22, color="var(--hi)")
            else:
                S.text(x + 12, y + 13, str(M[i][j]), size=15, weight=600)
    S.rect(ox, oy, n * CELL, n * CELL, stroke="currentColor", fill="none", width=1.6)
    S.rect(ox + 2, oy + 2, CELL - 4, CELL - 4, stroke="var(--hi)", fill="none", width=2)
    for q in ((0, 3), (3, 0)):  # the two first moves
        lx, ly = arc(S, C((0, 0)), C(q), -6 if q == (0, 3) else 6, "var(--accent)")
        tag(S, lx, ly, "3", "var(--accent)")
    for p, b in (((1, 2), 10), ((1, 4), 20)):  # the moves into (2,2): both go left
        lx, ly = arc(S, C(p), C((1, 1)), b, "var(--accent2)", dash="5 4", width=1.7)
        tag(S, lx, ly, str(M[p[0]][p[1]]), "var(--accent2)")
    lx, ly = arc(S, C((1, 1)), C((1, 4)), 8, "var(--hi)")  # right 3, then down 3 into the goal
    tag(S, lx, ly, "3", "var(--hi)")
    lx, ly = arc(S, C((1, 4)), C(G), 8, "var(--hi)")
    tag(S, lx, ly, "3", "var(--hi)")
    save("lab-09a-example", S.figure(
        "<strong>Why four variants fail on the handout's maze.</strong> Every solution starts with a move of length 3 "
        "onto a square labeled 4 (blue), so its second move has length 4. It ends with down 3 from (2,5) into the goal "
        "and first reaches (2,5) by right 3 from (2,2) (red): those are the only moves into the goal and into (2,5), "
        "apart from up 3 out of the goal if the goal were labeled 3. Both moves into (2,2) go left "
        "(green, dashed; lengths 1 and 3). Hence no solution alternates (Problem 2) or avoids U-turns (Problem 4): left is "
        "followed by right. None has increasing lengths (Problem 5): after 3, 4 nothing longer than 4 fits on the "
        "board. None is a palindrome (Problem 6): its second length, 4, would have to equal its second-to-last, 3. "
        "Labels sit in the top-left corners; the start is framed and the goal is ★.",
        alt="the five by five number maze with the two possible first moves and the forced last two moves"))

    # ------------------------------------------------------------------ problem 6: two tokens meet in the middle
    def sub(name, idx, size=15):
        return (f'<tspan font-style="italic">{name}</tspan>'
                f'<tspan dy="4" font-size="{size - 4}">{idx}</tspan>')

    def pair(a, b):
        return ("(" + sub("p", a, 13) + '<tspan dy="-4">,</tspan>' + sub("p", b, 13)
                + '<tspan dy="-4">)</tspan>')

    W, H = 640, 372
    S = _SVG(W, H)
    rows = [(6, [2, 1, 3, 3, 1, 2], 112, "6 moves: the tokens meet on a square"),
            (5, [2, 1, 4, 1, 2], 300, "5 moves: a middle move joins them")]
    for m, ls, y, title in rows:
        assert ls == ls[::-1]
        x0, dx = 70, 78 if m == 6 else 92
        xs = [x0 + k * dx for k in range(m + 1)]
        S.text(18, y - 104, title, size=13, color="var(--muted)", anchor="start")
        h = m // 2
        # rainbow arcs: the vertices (p_k, p_{m-k}) of the pair graph
        for k in range(h + 1):
            a, b = xs[k], xs[m - k]
            if a == b:
                continue
            top = y - 18 - (h - k) * 27 - 10
            S.path(f"M{a:.1f},{y - 12:.1f} C{a:.1f},{top:.1f} {b:.1f},{top:.1f} {b:.1f},{y - 12:.1f}",
                   color="var(--muted)", width=1.2, dash="3 3")
            S.text((a + b) / 2, top + 0.25 * (y - 12 - top) - 1, pair(k, m - k), size=13, raw=True, halo=True)
        for k in range(m):
            if m % 2 == 1 and k == h:
                col = "var(--hi)"
            elif k < h:
                col = "var(--accent)"
            else:
                col = "var(--accent2)"
            S.line(xs[k] + 9, y, xs[k + 1] - 10, y, color=col, width=2.2, arrow=True)
            S.text((xs[k] + xs[k + 1]) / 2, y + 16, str(ls[k]), size=14, color=col, weight=600)
        for k, x in enumerate(xs):
            meet = m % 2 == 0 and k == h
            S.circle(x, y, 6, stroke="var(--hi)" if meet else "currentColor", fill="var(--paper)", width=1.6)
            S.text(x, y + 36, sub("p", k), size=15, raw=True)
        if m % 2 == 0:
            S.text(xs[h], y - 22, pair(h, h), size=13, raw=True,
                   color="var(--hi)", halo=True)
        else:
            S.text((xs[h] + xs[h + 1]) / 2, y + 54, "middle move: any length", size=12, color="var(--hi)")
        S.text(xs[0] - 4, y + 54, "front token →", size=12, color="var(--accent)", anchor="start")
        S.text(xs[-1] + 4, y + 54, "← back token", size=12, color="var(--accent2)", anchor="end")
    save("lab-09a-palindrome", S.figure(
        "<strong>Problem 6: checking a palindrome from both ends.</strong> A solution <i>p</i><sub>0</sub> = (1,1), "
        "…, <i>p</i><sub>m</sub> = (<i>n</i>,<i>n</i>) with its move lengths underneath. The front token replays it "
        "from the start (blue), the back token backward from the goal (green), one move each per step, and each "
        "step must use two moves of equal length. After <i>k</i> steps the tokens are on "
        "(<i>p</i><sub><i>k</i></sub>, <i>p</i><sub><i>m</i>−<i>k</i></sub>) — one vertex of the pair graph per "
        "dashed arc. With an even number of moves they end on the same square; with an odd number they end one "
        "move apart, and that middle move (red) is paired with itself, so its length is free.",
        alt="two rows of squares joined by moves with palindromic lengths and nested arcs pairing the k-th square "
            "from the front with the k-th from the back"))


_lab9a_figures()
# ==================================================================================================== end of Lab 9a

# ======================================================================================================== Lab 9b
# Lab 9b (Judy's tour): the example instance of content/3-homework-and-exams/lab-09b.md, drawn with x = D, and the
# best tours of Problems 2 and 4.  The tours drawn are re-checked by tools/checks/labs_09b.py (same instance).


def _l9b_figures():
    import math as _m
    import os as _os
    from figlib import SVG as _S, SERIF_IT as _SERIF

    out_dir = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "figs")
    _os.makedirs(out_dir, exist_ok=True)
    D = {"s": 0, "a": 1, "b": 3, "c": 4, "d": 5, "e": 6, "f": 7, "g": 8, "h": 9}
    row = {"s": 1, "c": 1, "g": 1, "h": 1, "b": 0, "e": 0, "a": 2, "d": 2, "f": 2}
    ways = ["sc", "sh", "cg", "cb", "gf", "gh", "fd", "da", "he", "ha"]
    R = 15
    W = 640
    X = lambda v: 46 + 62 * D[v]
    PANEL = 258

    def Y(v, k):
        return 72 + 62 * row[v] + k * PANEL

    # curved teleport-ways: control-point offsets (dx, dy) from the midpoint
    curve = {"sh": (0, -216), "ha": (40, 124)}

    def geom(u, v, k, side=0):
        x1, y1, x2, y2 = X(u), Y(u, k), X(v), Y(v, k)
        key = u + v if u + v in curve else v + u
        if key in curve:
            dx, dy = curve[key]
            cx, cy = (x1 + x2) / 2 + dx, (y1 + y2) / 2 + dy
            return x1, y1, x2, y2, cx, cy
        if side:
            L = _m.hypot(x2 - x1, y2 - y1)
            nx, ny = -(y2 - y1) / L, (x2 - x1) / L
            return x1, y1, x2, y2, (x1 + x2) / 2 + nx * side, (y1 + y2) / 2 + ny * side
        return x1, y1, x2, y2, None, None

    def draw_way(S, u, v, k, color="var(--muted)", width=1.3, arrow=False, dash=None, opacity=None, side=0):
        """Line or curve from u to v, trimmed at both circles; arrow at v."""
        x1, y1, x2, y2, cx, cy = geom(u, v, k, side)
        if cx is None:
            L = _m.hypot(x2 - x1, y2 - y1)
            ux, uy = (x2 - x1) / L, (y2 - y1) / L
            sx, sy = x1 + ux * R, y1 + uy * R
            ex, ey = x2 - ux * (R + (2.5 if arrow else 0)), y2 - uy * (R + (2.5 if arrow else 0))
            S.path(f"M{sx:.1f},{sy:.1f} L{ex:.1f},{ey:.1f}", color=color, width=width, arrow=arrow, dash=dash,
                   opacity=opacity)
        else:
            a1 = _m.atan2(cy - y1, cx - x1)
            a2 = _m.atan2(cy - y2, cx - x2)
            sx, sy = x1 + _m.cos(a1) * R, y1 + _m.sin(a1) * R
            off = R + (2.5 if arrow else 0)
            ex, ey = x2 + _m.cos(a2) * off, y2 + _m.sin(a2) * off
            S.path(f"M{sx:.1f},{sy:.1f} Q{cx:.1f},{cy:.1f} {ex:.1f},{ey:.1f}", color=color, width=width, arrow=arrow,
                   dash=dash, opacity=opacity)

    def panel(S, k, title, steps, missed):
        """steps: list of (u, v, kind) with kind in away / paid / home."""
        S.text(16, 14 + k * PANEL, title, size=13, anchor="start", weight=600)
        used = {frozenset((u, v)) for u, v, _ in steps}
        both = {frozenset((u, v)) for u, v, kind in steps if kind == "paid"} & \
            {frozenset((u, v)) for u, v, kind in steps if kind == "away"}
        for w in ways:
            if frozenset(w) not in used:
                draw_way(S, w[0], w[1], k)
        drawn = set()
        for u, v, kind in steps:
            if (u, v) in drawn:
                continue
            drawn.add((u, v))
            if kind == "away":
                draw_way(S, u, v, k, color="var(--accent)", width=2.4, arrow=True)
            elif kind == "paid":
                draw_way(S, u, v, k, color="var(--accent2)", width=2.2, arrow=True, dash="6 4",
                         side=17 if frozenset((u, v)) in both else 0)
            else:
                draw_way(S, u, v, k, color="var(--accent2)", width=2.2, arrow=True)
        for v in D:
            on = any(v in (a, b) for a, b, _ in steps)
            if v in missed:
                S.circle(X(v), Y(v, k), R, stroke="var(--muted)", fill="var(--paper)", width=1.4)
                S.text(X(v), Y(v, k) + 1, v, size=15, font=_SERIF, italic=True, color="var(--muted)")
            else:
                S.circle(X(v), Y(v, k), R, stroke="currentColor", fill="var(--paper)", width=1.6)
                if on:
                    S.circle(X(v), Y(v, k), R, stroke="currentColor", fill="var(--accent)", width=1.6,
                             fill_opacity=0.16)
                S.text(X(v), Y(v, k) + 1, v, size=15, font=_SERIF, italic=True)

    S = _S(W, 2 * PANEL + 46, font_size=13)
    tour2 = [("s", "c", "away"), ("c", "g", "away"), ("g", "h", "away"), ("h", "s", "home")]
    word4 = "scghehadfghs"
    kinds = []
    for u, v in zip(word4, word4[1:]):
        kinds.append((u, v, "home" if v == "s" else ("away" if D[v] > D[u] else "paid")))
    panel(S, 0, "Problem 2 — the best tour, 4 galaxies", tour2, missed=set("abdef"))
    panel(S, 1, "Problem 4 — a best tour with two paid teleports, 8 distinct galaxies", kinds, missed={"b"})
    # distance axis
    ya = 2 * PANEL + 4
    S.line(X("s"), ya, X("h"), ya, color="var(--muted)", width=1.2)
    for d in range(10):
        x = 46 + 62 * d
        S.line(x, ya - 4, x, ya + 4, color="var(--muted)", width=1.2)
        S.text(x, ya + 15, str(d), size=12, color="var(--muted)")
    S.text((X("s") + X("h")) / 2, ya + 34, "distance from home, D", size=12, color="var(--muted)")
    for k in range(2):
        for v in D:
            S.line(X(v), Y(v, k) + R + 2, X(v), (k + 1) * PANEL - 6 if k == 0 else ya - 6,
                   color="var(--muted)", width=0.8, dash="2 3", opacity=0.45)
    html = S.figure(
        "<strong>The example instance, each galaxy drawn at horizontal position D.</strong> Nine galaxies and ten "
        "teleport-ways; a teleport away from home always points right. Top: the best tour of Problem 2, s → c → g → "
        "h → s, climbs (blue) to h, a neighbor of s, and teleports home (green). Bottom: a best tour of Problem 4, "
        "s → c → g → h ⇢ e → h ⇢ a → d → f → g → h → s; the dashed arrows are the two paid teleports. Galaxies a, "
        "b and e have no closer neighbor, so each one costs a paid teleport, and b (gray) is missed. Problem 3 "
        "instead repeats h ⇢ a → d → f → g → h twice, for 14 visits.",
        alt="nine galaxies placed by distance from home, with the best tours of Problems 2 and 4 highlighted")
    with open(_os.path.join(out_dir, "lab-09b-galaxies.html"), "w", encoding="utf-8") as f:
        f.write(html + "\n")
    print("wrote lab-09b-galaxies")


_l9b_figures()
# ======================================================================================================== end of Lab 9b
