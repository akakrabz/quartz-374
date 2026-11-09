#!/usr/bin/env python3
"""Figures for content/4-lecture-notes/98-proof-by-induction.md (Erickson, Appendix I). Writes
tools/figs/n98-<name>.html; then run tools/assemble.py on the page. The tilings drawn here are produced by the two
recursive algorithms of Theorem 5 (the same code as tools/checks/n98.py) and validated before drawing."""
import os

from figlib import SVG, SERIF_IT, SANS

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")
os.makedirs(OUT, exist_ok=True)


def save(name, html):
    with open(os.path.join(OUT, name + ".html"), "w", encoding="utf-8") as f:
        f.write(html + "\n")
    print("wrote", name)


# ------------------------------------------------------------------ the two tiling algorithms (as in the check)
def tile_topdown(n, hole, r0=0, c0=0, depth=0, out=None):
    """List of (triomino, recursion depth) tiling the 2^n board at (r0, c0) minus `hole`."""
    if out is None:
        out = []
    if n == 0:
        return out
    h = 1 << (n - 1)
    quads = [(r0, c0), (r0, c0 + h), (r0 + h, c0), (r0 + h, c0 + h)]
    centre = [(r0 + h - 1, c0 + h - 1), (r0 + h - 1, c0 + h), (r0 + h, c0 + h - 1), (r0 + h, c0 + h)]
    holes, tri = [], []
    for (qr, qc), cc in zip(quads, centre):
        if qr <= hole[0] < qr + h and qc <= hole[1] < qc + h:
            holes.append(hole)
        else:
            holes.append(cc)
            tri.append(cc)
    out.append((frozenset(tri), depth))
    for (qr, qc), hh in zip(quads, holes):
        tile_topdown(n - 1, hh, qr, qc, depth + 1, out)
    return out


def tile_bottomup(n, hole):
    if n == 0:
        return []
    coarse = tile_bottomup(n - 1, (hole[0] // 2, hole[1] // 2))
    out = []
    for T in coarse:
        br, bc = min(b[0] for b in T), min(b[1] for b in T)
        missing = [(br + i, bc + j) for i in (0, 1) for j in (0, 1) if (br + i, bc + j) not in T][0]
        cen = [(2 * br + 1, 2 * bc + 1), (2 * br + 1, 2 * bc + 2), (2 * br + 2, 2 * bc + 1), (2 * br + 2, 2 * bc + 2)]
        cen_in = [c for c in cen if (c[0] // 2, c[1] // 2) != missing]
        out.append(frozenset(cen_in))
        for b in T:
            cells = {(2 * b[0] + i, 2 * b[1] + j) for i in (0, 1) for j in (0, 1)}
            out.append(frozenset(cells - set(cen_in)))
    hb = (hole[0] // 2, hole[1] // 2)
    cells = {(2 * hb[0] + i, 2 * hb[1] + j) for i in (0, 1) for j in (0, 1)}
    out.append(frozenset(cells - {hole}))
    return out


def valid(n, hole, tiles):
    N = 1 << n
    cells = [c for t in tiles for c in t]
    ok_L = all(len(t) == 3 and max(a for a, _ in t) - min(a for a, _ in t) == 1
               and max(b for _, b in t) - min(b for _, b in t) == 1 for t in tiles)
    return ok_L and len(cells) == len(set(cells)) and set(cells) == {(r, c) for r in range(N) for c in range(N)} - {hole}


# ------------------------------------------------------------------ drawing helpers
def draw_board(S, x0, y0, cell, n, owner, hole, fills=None, outline=True, extra_lines=(), coarse=None):
    """owner: dict cell -> tile id (None for uncovered). Thin grid; thick lines between different owners."""
    N = 1 << n
    fills = fills or {}
    for (r, c), col in fills.items():
        S.rect(x0 + c * cell, y0 + r * cell, cell, cell, fill=col[0], fill_opacity=col[1], stroke="none", width=0)
    if hole is not None:
        S.rect(x0 + hole[1] * cell + 1.5, y0 + hole[0] * cell + 1.5, cell - 3, cell - 3, fill="currentColor",
               stroke="none", width=0)
    for i in range(N + 1):
        S.line(x0, y0 + i * cell, x0 + N * cell, y0 + i * cell, color="var(--muted)", width=0.6, opacity=0.55)
        S.line(x0 + i * cell, y0, x0 + i * cell, y0 + N * cell, color="var(--muted)", width=0.6, opacity=0.55)
    if outline:
        for r in range(N):
            for c in range(N):
                if c + 1 < N and owner.get((r, c)) != owner.get((r, c + 1)):
                    S.line(x0 + (c + 1) * cell, y0 + r * cell, x0 + (c + 1) * cell, y0 + (r + 1) * cell, width=1.8)
                if r + 1 < N and owner.get((r, c)) != owner.get((r + 1, c)):
                    S.line(x0 + c * cell, y0 + (r + 1) * cell, x0 + (c + 1) * cell, y0 + (r + 1) * cell, width=1.8)
    for (xa, ya, xb, yb, col, w) in extra_lines:
        S.line(x0 + xa * cell, y0 + ya * cell, x0 + xb * cell, y0 + yb * cell, color=col, width=w)
    S.rect(x0, y0, N * cell, N * cell, fill="none", width=2)


def arrow(S, x1, x2, y):
    S.line(x1, y, x2, y, color="var(--muted)", width=2, arrow=True)


# ------------------------------------------------------------------ figure 1: top-down tiling
n, HOLE, cell = 3, (1, 5), 20
td = tile_topdown(n, HOLE)
assert valid(n, HOLE, [t for t, _ in td]) and len(td) == 21
S = SVG(490, 246)
x1, x2, y0 = 40, 305, 26
B = cell * 8
# panel A: quadrants, the hole, and the central triomino only
centre_tri = [t for t, d in td if d == 0][0]
ownerA = {c: 0 for c in centre_tri}
fillsA = {c: ("var(--hi)", 0.55) for c in centre_tri}
draw_board(S, x1, y0, cell, n, ownerA, HOLE, fills=fillsA, outline=False,
           extra_lines=[(4, 0, 4, 8, "currentColor", 2.4), (0, 4, 8, 4, "currentColor", 2.4)])
for (r, c) in centre_tri:  # outline the triomino itself
    for dr, dc, (xa, ya, xb, yb) in [(0, 1, (c + 1, r, c + 1, r + 1)), (0, -1, (c, r, c, r + 1)),
                                     (1, 0, (c, r + 1, c + 1, r + 1)), (-1, 0, (c, r, c + 1, r))]:
        if (r + dr, c + dc) not in centre_tri:
            S.line(x1 + xa * cell, y0 + ya * cell, x1 + xb * cell, y0 + yb * cell, color="var(--hi)", width=2.6)
S.text(x1 + B / 2, y0 + B + 16, "one triomino covers a square", size=13, color="var(--muted)")
S.text(x1 + B / 2, y0 + B + 32, "in each quadrant without the hole", size=13, color="var(--muted)")
S.text(x1 + B / 2, 13, "the inductive step", size=13, weight=600)
arrow(S, x1 + B + 18, x2 - 18, y0 + B / 2)
S.text((x1 + B + x2) / 2, y0 + B / 2 - 12, "recurse ×4", size=12, color="var(--muted)")
# panel B: the whole tiling; depth 0 in --hi, depth 1 in --accent
ownerB, fillsB = {}, {}
for i, (t, d) in enumerate(td):
    for c in t:
        ownerB[c] = i
        if d == 0:
            fillsB[c] = ("var(--hi)", 0.55)
        elif d == 1:
            fillsB[c] = ("var(--accent)", 0.30)
draw_board(S, x2, y0, cell, n, ownerB, HOLE, fills=fillsB)
S.text(x2 + B / 2, y0 + B + 16, "21 triominos; shaded: the center", size=13, color="var(--muted)")
S.text(x2 + B / 2, y0 + B + 32, "pieces of the first two levels", size=13, color="var(--muted)")
S.text(x2 + B / 2, 13, "the finished tiling", size=13, weight=600)
save("n98-triomino-topdown", S.figure(
    "<strong>Theorem 5, top-down.</strong> The 8 × 8 board minus the solid square. The inductive step puts one "
    "triomino (red) at the center, covering one square of each quadrant that does not contain the hole; now every "
    "quadrant is a 4 × 4 board minus one square, and the induction hypothesis tiles it. Unrolled, the proof is a "
    "recursive algorithm: the shaded pieces are the center triominos placed by the first two levels of recursion "
    "(red at the top level, blue one level down).",
    alt="an 8 by 8 board with one square removed: the central triomino of the inductive step, then the complete "
        "tiling by 21 L-shaped triominos"))

# ------------------------------------------------------------------ figure 2: bottom-up tiling
cell = 16
B = cell * 8
coarse = tile_bottomup(2, (HOLE[0] // 2, HOLE[1] // 2))
fine = tile_bottomup(3, HOLE)
assert valid(2, (HOLE[0] // 2, HOLE[1] // 2), coarse) and valid(3, HOLE, fine) and len(fine) == 21
S = SVG(590, 214)
xs, y0 = [24, 230, 436], 26
hb = (HOLE[0] // 2, HOLE[1] // 2)
hb_cells = {(2 * hb[0] + i, 2 * hb[1] + j) for i in (0, 1) for j in (0, 1)}
# panel A: 2x2 blocks, hole's block shaded
block_lines = [(k, 0, k, 8, "currentColor", 1.8) for k in (2, 4, 6)] + [(0, k, 8, k, "currentColor", 1.8) for k in (2, 4, 6)]
draw_board(S, xs[0], y0, cell, 3, {}, HOLE, fills={c: ("var(--accent2)", 0.35) for c in hb_cells}, outline=False,
           extra_lines=block_lines)
S.text(xs[0] + B / 2, 13, "group into 2 × 2 blocks", size=13, weight=600)
S.text(xs[0] + B / 2, y0 + B + 16, "a 4 × 4 board of blocks", size=13, color="var(--muted)")
S.text(xs[0] + B / 2, y0 + B + 32, "minus the hole's block", size=13, color="var(--muted)")
# panel B: coarse tiling at double size
ownerC = {}
for i, T in enumerate(coarse):
    for b in T:
        for di in (0, 1):
            for dj in (0, 1):
                ownerC[(2 * b[0] + di, 2 * b[1] + dj)] = i
draw_board(S, xs[1], y0, cell, 3, ownerC, None, fills={c: ("var(--accent2)", 0.35) for c in hb_cells})
S.text(xs[1] + B / 2, 13, "induction hypothesis", size=13, weight=600)
S.text(xs[1] + B / 2, y0 + B + 16, "5 double-size triominos", size=13, color="var(--muted)")
S.text(xs[1] + B / 2, y0 + B + 32, "tile the blocks", size=13, color="var(--muted)")
# panel C: split each double-size triomino into four; hole's block minus the hole is one more triomino
ownerF = {}
for i, t in enumerate(fine):
    for c in t:
        ownerF[c] = i
hole_tri = [t for t in fine if t <= hb_cells][0]
coarse_edges = []
for r in range(8):
    for c in range(8):
        if c + 1 < 8 and ownerC.get((r, c), -1) != ownerC.get((r, c + 1), -1):
            coarse_edges.append((c + 1, r, c + 1, r + 1, "var(--accent)", 3))
        if r + 1 < 8 and ownerC.get((r, c), -1) != ownerC.get((r + 1, c), -1):
            coarse_edges.append((c, r + 1, c + 1, r + 1, "var(--accent)", 3))
draw_board(S, xs[2], y0, cell, 3, ownerF, HOLE, fills={c: ("var(--accent2)", 0.35) for c in hole_tri},
           extra_lines=coarse_edges)
S.text(xs[2] + B / 2, 13, "split each into four", size=13, weight=600)
S.text(xs[2] + B / 2, y0 + B + 16, "5 × 4 + 1 = 21 triominos", size=13, color="var(--muted)")
S.text(xs[2] + B / 2, y0 + B + 32, "(blue: the double-size outlines)", size=13, color="var(--muted)")
arrow(S, xs[0] + B + 14, xs[1] - 14, y0 + B / 2)
arrow(S, xs[1] + B + 14, xs[2] - 14, y0 + B / 2)
save("n98-triomino-bottomup", S.figure(
    "<strong>Theorem 5, bottom-up.</strong> Group the squares into 2 × 2 blocks: the 8 × 8 board becomes a 4 × 4 "
    "board of blocks, minus the block that holds the hole (shaded). The induction hypothesis, applied at double size, "
    "tiles the remaining blocks with five double-size triominos; each of those splits into four ordinary triominos, "
    "and the hole's block minus the hole is one more (shaded). The same recursion, run in the other order.",
    alt="three 8 by 8 boards: 2 by 2 blocks with the hole's block shaded; five double-size triominos; the final "
        "tiling with 21 triominos"))

# ------------------------------------------------------------------ figure 3: three ways to take a tree apart
pos = {"a": (0, 0), "b": (-1.0, 1), "c": (1.0, 1), "d": (-1.5, 2), "e": (-0.5, 2), "f": (0.5, 2), "g": (1.5, 2),
       "h": (1.5, 3)}
edges = [("a", "b"), ("a", "c"), ("b", "d"), ("b", "e"), ("c", "f"), ("c", "g"), ("g", "h")]


def draw_tree(S, ox, oy, sx, sy, colour, dashed=(), removed=(), labels=None):
    P = {v: (ox + x * sx, oy + y * sy) for v, (x, y) in pos.items()}
    for u, v in edges:
        (xa, ya), (xb, yb) = P[u], P[v]
        if (u, v) in dashed:
            S.line(xa, ya, xb, yb, color="var(--hi)", width=2, dash="4 4")
        elif u in removed or v in removed:
            S.line(xa, ya, xb, yb, color="var(--muted)", width=1.4, dash="2 4")
        else:
            S.line(xa, ya, xb, yb, color=colour.get(u, "currentColor") if colour.get(u) == colour.get(v)
                   else "currentColor", width=1.8)
    for v, (x, y) in P.items():
        if v in removed:
            S.circle(x, y, 8, stroke="var(--hi)", fill="var(--paper)", width=2)
        else:
            col = colour.get(v)
            if col:
                S.circle(x, y, 8, stroke=col, fill=col, width=1.6, fill_opacity=0.35)
                S.circle(x, y, 8, stroke=col, fill="none", width=1.6)
            else:
                S.circle(x, y, 8, stroke="currentColor", fill="var(--paper)", width=1.6)
    for v, (txt, dx, dy, col) in (labels or {}).items():
        x, y = P[v]
        S.text(x + dx, y + dy, txt, size=15, font=SERIF_IT, italic=True, color=col, halo=True)
    return P


S = SVG(640, 196)
sx, sy, oy = 34, 40, 40
A, Bc, C3 = "var(--accent)", "var(--accent2)", "var(--muted)"
# (1) delete an edge: e = a–c; A = {a,b,d,e}, B = {c,f,g,h}
col1 = {v: A for v in "abde"} | {v: Bc for v in "cfgh"}
P = draw_tree(S, 110, oy, sx, sy, col1, dashed=[("a", "c")])
S.text((P["a"][0] + P["c"][0]) / 2 + 9, (P["a"][1] + P["c"][1]) / 2 - 9, "e", size=15, font=SERIF_IT, italic=True,
       color="var(--hi)", halo=True)
S.text(P["d"][0] - 2, P["d"][1] + 26, "A", size=15, font=SERIF_IT, italic=True, color=A)
S.text(P["h"][0] + 18, P["h"][1], "B", size=15, font=SERIF_IT, italic=True, color=Bc)
S.text(110, 12, "delete an edge: 2 subtrees", size=13, weight=600)
# (2) delete a vertex v = c (degree 3): components {a,b,d,e}, {f}, {g,h}
col2 = {v: A for v in "abde"} | {"f": Bc} | {v: C3 for v in "gh"}
P = draw_tree(S, 320, oy, sx, sy, col2, removed=("c",))
S.text(P["c"][0] + 17, P["c"][1] - 6, "v", size=15, font=SERIF_IT, italic=True, color="var(--hi)", halo=True)
S.text(320, 12, "delete a vertex: deg(v) subtrees", size=13, weight=600)
S.text(320 - 1.0 * sx, oy + 3 * sy, "deg(v) = 3", size=13, color="var(--muted)")
# (3) delete a leaf ℓ = h
col3 = {v: A for v in "abcdefg"}
P = draw_tree(S, 530, oy, sx, sy, col3, removed=("h",))
S.text(P["h"][0] + 17, P["h"][1] - 2, "ℓ", size=15, font=SERIF_IT, italic=True, color="var(--hi)", halo=True)
S.text(530, 12, "delete a leaf: 1 subtree", size=13, weight=600)
S.text(530 - 1.5 * sx - 14, oy + 3.0 * sy, "T − ℓ", size=15, font=SERIF_IT, italic=True, color=A)
save("n98-tree-proofs", S.figure(
    "<strong>Three recursive views of one tree, three induction proofs of Theorem 10.</strong> Left: deleting any edge "
    "<i>e</i> leaves exactly two subtrees <i>A</i> and <i>B</i>, so |<i>E</i>| = |<i>E</i>(<i>A</i>)| + "
    "|<i>E</i>(<i>B</i>)| + 1. Middle: deleting a vertex <i>v</i> of degree <i>d</i> leaves exactly <i>d</i> subtrees, "
    "and <i>v</i> takes <i>d</i> edges with it. Right: deleting a leaf ℓ leaves one subtree with one vertex and one edge "
    "fewer. Each proof applies the induction hypothesis to the colored pieces, which are proper subtrees.",
    alt="the same eight-vertex tree three times: split by deleting an edge into two subtrees, by deleting a "
        "degree-3 vertex into three subtrees, and by deleting a leaf into one subtree"))
