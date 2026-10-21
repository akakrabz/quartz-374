#!/usr/bin/env python3
"""Figures for Algorithms Chapter 2 (backtracking). Writes tools/figs/a02-*.html; then run tools/assemble.py."""
import os
from figlib import SVG, MONO, SERIF_IT, SANS

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")
os.makedirs(OUT, exist_ok=True)


def save(name, html):
    with open(os.path.join(OUT, name + ".html"), "w", encoding="utf-8") as f:
        f.write(html + "\n")
    print("wrote", name)


def legal(q, r, j):
    """Book's test: may a queen go on row r, column j, given q[0..r-2] for rows 1..r-1?"""
    return all(not (q[i - 1] == j or q[i - 1] == j + r - i or q[i - 1] == j - r + i) for i in range(1, r))


def board(S, x, y, n, cell, queens, stroke="currentColor", width=1.2, qr=None):
    """n x n board with top-left corner (x, y); queens[i] = column (1-based) of the queen in row i+1."""
    for r in range(n):
        for c in range(n):
            if (r + c) % 2 == 1:
                S.rect(x + c * cell, y + r * cell, cell, cell, stroke="none", fill="var(--muted)", fill_opacity=0.28,
                       width=0)
    S.rect(x, y, n * cell, n * cell, stroke=stroke, width=width)
    for r, c in enumerate(queens):
        S.circle(x + (c - 0.5) * cell, y + (r + 0.5) * cell, qr or cell * 0.32, stroke="currentColor",
                 fill="var(--accent)", width=1.0)


# ---------------------------------------------------------------- Gauss's 8-queens solution
G = [5, 7, 1, 4, 2, 8, 6, 3]
cell = 26
S = SVG(360, 252)
x0, y0 = 40, 30
board(S, x0, y0, 8, cell, G)
for c in range(1, 9):
    S.text(x0 + (c - 0.5) * cell, y0 - 12, str(c), size=12, color="var(--muted)")
for r in range(1, 9):
    S.text(x0 - 14, y0 + (r - 0.5) * cell, str(r), size=12, color="var(--muted)")
    S.text(x0 + 8 * cell + 18, y0 + (r - 0.5) * cell, f"Q[{r}] = {G[r - 1]}", size=12, font=MONO, anchor="start")
save("a02-gauss-queens", S.figure(
    "<strong>Gauss's first solution to the 8 queens problem.</strong> One queen per row, so a placement is an array: "
    "<i>Q</i>[<i>i</i>] is the column of the queen in row <i>i</i>; this one is [5, 7, 1, 4, 2, 8, 6, 3]. "
    "No two queens share a column, and no two share a diagonal: |<i>Q</i>[<i>i</i>] − <i>Q</i>[<i>k</i>]| ≠ <i>k</i> − <i>i</i> for all <i>i</i> &lt; <i>k</i>.",
    alt="8 by 8 chessboard with eight non-attacking queens"))

# ---------------------------------------------------------------- 4-queens recursion tree
n = 4


def qtree(q):
    r = len(q) + 1
    kids = [qtree(q + (j,)) for j in range(1, n + 1) if r <= n and legal(q, r, j)]
    return (q, kids)


T = qtree(())
cell = 10
bw = n * cell
slot, lev = 66, 66
S = SVG(440, 352)
pos = {}


def place(t, left, depth):
    q, kids = t
    if not kids:
        x = left + slot / 2
        pos[q] = (x, 18 + depth * lev)
        return x, left + slot
    xs, cur = [], left
    for k in kids:
        kx, cur = place(k, cur, depth + 1)
        xs.append(kx)
    x = (xs[0] + xs[-1]) / 2
    pos[q] = (x, 18 + depth * lev)
    return x, cur


place(T, 22, 0)


def draw_edges(t):
    q, kids = t
    px, py = pos[q]
    for k in kids:
        kx, ky = pos[k[0]]
        S.line(px, py + bw + 2, kx, ky - 2, width=1.4, opacity=0.6)
        draw_edges(k)


draw_edges(T)
for q, (x, y) in pos.items():
    sol = len(q) == n
    board(S, x - bw / 2, y, n, cell, q, stroke="var(--hi)" if sol else "currentColor", width=2.4 if sol else 1.1,
          qr=3.4)
    if sol:
        S.text(x, y + bw + 12, "[" + ",".join(map(str, q)) + "]", size=11, font=MONO, color="var(--hi)")
    elif not any(len(p) == len(q) + 1 and p[:-1] == q for p in pos):   # a leaf that is not a solution
        S.text(x, y + bw + 11, "dead end", size=10, color="var(--muted)")
for d in range(n + 1):
    S.text(8, 18 + d * lev + bw / 2, f"r={d + 1}", size=11, color="var(--muted)", anchor="start")
save("a02-queens-tree", S.figure(
    "<strong>The complete recursion tree of PlaceQueens for 4 queens.</strong> Each node is one call, i.e. a legal "
    "partial solution, and r is the call's argument, the first empty row. 17 calls in all (1, 4, 6, 4, 2 per level). "
    "Four leaves are dead ends — every square of the next row is attacked — and two are the solutions "
    "[2,4,1,3] and [3,1,4,2] (outlined). Backtracking visits this tree in depth-first order, left to right.",
    alt="recursion tree of 17 small 4 by 4 boards"))

# ---------------------------------------------------------------- game tree of the subtraction game
gt = None


def gtree(m, path):
    return (m, path, [gtree(m - t, path + (t,)) for t in (1, 2) if t <= m])


GT = gtree(4, ())
slot, lev = 74, 62
S = SVG(470, 330)
gpos = {}


def gplace(t, left, depth):
    m, path, kids = t
    if not kids:
        x = left + slot / 2
        gpos[path] = (x, 30 + depth * lev)
        return x, left + slot
    xs, cur = [], left
    for k in kids:
        kx, cur = gplace(k, cur, depth + 1)
        xs.append(kx)
    x = (xs[0] + xs[-1]) / 2
    gpos[path] = (x, 30 + depth * lev)
    return x, cur


gplace(GT, 96, 0)


def good(m):
    return m % 3 != 0


visited = {(), (1,), (1, 1), (1, 1, 1), (1, 1, 1, 1), (1, 1, 2), (1, 2), (1, 2, 1)}
R = 16


def gdraw_edges(t):
    m, path, kids = t
    px, py = gpos[path]
    for k in kids:
        km, kpath, _ = k
        kx, ky = gpos[kpath]
        dx, dy = kx - px, ky - py
        L = (dx * dx + dy * dy) ** 0.5
        ux, uy = dx / L, dy / L
        vis = kpath in visited
        win = kpath == (1,)
        S.line(px + ux * R, py + uy * R, kx - ux * (R + 3), ky - uy * (R + 3), arrow=True,
               color="var(--accent)" if win else "currentColor", width=2.6 if win else 1.4,
               dash=None if vis else "4 4", opacity=None if vis else 0.45)
        mx, my = (px + kx) / 2, (py + ky) / 2
        S.text(mx + (-11 if dx < 0 else 11), my - 4, f"−{kpath[-1]}", size=11, font=MONO,
               color="var(--accent)" if win else "var(--muted)", halo=True)
        gdraw_edges(k)


gdraw_edges(GT)


def gdraw_nodes(t):
    m, path, kids = t
    x, y = gpos[path]
    vis = path in visited
    col = "var(--accent2)" if good(m) else "var(--hi)"
    op = None if vis else 0.45
    S.add(f'<g{" opacity=\"0.45\"" if not vis else ""}>')
    S.circle(x, y, R, stroke=col, fill="var(--paper)", width=2.0)
    S.circle(x, y, R - 3, stroke="none", fill=col, fill_opacity=0.14, width=0)
    S.text(x, y + 1, str(m), size=15)
    S.text(x + R + 7, y - 9, "G" if good(m) else "B", size=11, color=col, weight=700, anchor="start")
    S.add("</g>")
    for k in kids:
        gdraw_nodes(k)


gdraw_nodes(GT)
for d in range(5):
    S.text(10, 30 + d * lev, "Alice moves" if d % 2 == 0 else "Bob moves", size=12, color="var(--muted)",
           anchor="start")
save("a02-game-tree", S.figure(
    "<strong>A game tree, labeled by PlayAnyGame.</strong> A pile of 4 tokens; a move takes 1 or 2; whoever takes the "
    "last token wins, so facing 0 tokens means you have lost (a <b>B</b>ad leaf). A node is <b>G</b>ood iff some child "
    "is Bad. From 4, taking 1 (heavy arrow) leaves Bob the Bad state 3. PlayAnyGame tries that move first, gets Bad back, "
    "and returns Good without ever visiting the faded subtree.",
    alt="game tree of the take-1-or-2 game from a pile of 4, nodes labeled good or bad"))

# ---------------------------------------------------------------- LIS: the two decision pictures
A = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5, 8, 9, 7, 9, 3, 2, 3, 8, 4, 6, 2, 6]
chosen = {2, 3, 5, 8}          # 1-based positions of 1, 4, 5, 6
cw, ch = 22, 26
S = SVG(600, 188)


def row(y, bar_after, current, candidates, title):
    x0 = 30
    S.text(x0, y - 14, title, size=13, anchor="start")
    for k, v in enumerate(A, start=1):
        x = x0 + (k - 1) * cw + (10 if k > bar_after else 0)
        past = k <= bar_after
        if past and k in chosen:
            S.rect(x, y, cw, ch, stroke="none", fill="var(--accent)", fill_opacity=0.18, width=0)
            S.text(x + cw / 2, y + ch / 2 + 1, str(v), size=14, weight=700, color="var(--accent)")
        elif past:
            S.text(x + cw / 2, y + ch / 2 + 1, str(v), size=14, color="var(--muted)")
        elif k == current or k in candidates:
            S.rect(x + 1, y + 1, cw - 2, ch - 2, rx=3, stroke="var(--hi)", fill="var(--hi)", fill_opacity=0.10,
                   width=1.4)
            S.text(x + cw / 2 - 2, y + ch / 2 + 1, str(v), size=14, weight=700)
            S.text(x + cw - 5, y + 7, "?", size=10, color="var(--hi)", weight=700)
        else:
            S.text(x + cw / 2, y + ch / 2 + 1, str(v), size=14,
                   color="currentColor" if not candidates else "var(--muted)")
    xb = x0 + bar_after * cw + 5
    S.line(xb, y - 4, xb, y + ch + 4, width=4)
    S.rect(x0, y, len(A) * cw + 10, ch, stroke="currentColor", width=0.8)
    for k in range(1, len(A) + 1):
        S.text(x0 + (k - 1) * cw + (10 if k > bar_after else 0) + cw / 2, y + ch + 10, str(k), size=8,
               color="var(--muted)")


row(34, 11, 12, set(), "Take 1 (§2.6): is A[12] = 8 in? Only prev = 6 matters → LISbigger(8, 12)")
row(128, 8, None, {12, 13, 14, 15, 19}, "Take 2 (§2.7): which later element > 6 comes next? → LISfirst(8)")
save("a02-lis-pictures", S.figure(
    "<strong>The two ways to cut LIS into decisions</strong>, on the book's example (digits of π). Left of the bar: "
    "decisions already made — chosen elements 1, 4, 5, 6 highlighted, rejected ones grayed. Take 1 decides about the "
    "<em>next input element</em> (two options: in or out); take 2 decides which element is <em>next in the output</em> "
    "(one option per larger later element). Small numbers are indices.",
    alt="two rows of the digit sequence 3 1 4 1 5 9 2 6 5 3 5 8 9 7 9 3 2 3 8 4 6 2 6 with a bar separating past decisions"))

# ---------------------------------------------------------------- OBST: balanced vs optimal
F = dict(zip("ABCDEFG", [4, 2, 6, 3, 1, 5, 2]))
S = SVG(640, 300)
R = 18


def tree(nodes, edges, title, sums, cx):
    for a, b in edges:
        (x1, y1), (x2, y2) = nodes[a], nodes[b]
        dx, dy = x2 - x1, y2 - y1
        L = (dx * dx + dy * dy) ** 0.5
        S.line(x1 + dx / L * R, y1 + dy / L * R, x2 - dx / L * R, y2 - dy / L * R, width=1.4, opacity=0.7)
    for k, (x, y) in nodes.items():
        S.circle(x, y, R, stroke="currentColor", fill="var(--paper)", width=1.5)
        S.text(x, y - 5, k, size=14, weight=600)
        S.text(x, y + 9, str(F[k]), size=11, font=MONO, color="var(--accent)")
    S.text(cx, 258, title, size=13, weight=600)
    S.text(cx, 278, sums, size=12, font=MONO, color="var(--muted)")


ys = [36, 96, 156, 216]
bal = {"D": (165, ys[0]), "B": (95, ys[1]), "F": (235, ys[1]), "A": (60, ys[2]), "C": (130, ys[2]),
       "E": (200, ys[2]), "G": (270, ys[2])}
tree(bal, [("D", "B"), ("D", "F"), ("B", "A"), ("B", "C"), ("F", "E"), ("F", "G")],
     "perfectly balanced: cost 56", "3·1 + 7·2 + 13·3 = 56", 165)
opt = {"C": (475, ys[0]), "A": (405, ys[1]), "F": (545, ys[1]), "B": (440, ys[2]), "D": (510, ys[2]),
       "G": (580, ys[2]), "E": (545, ys[3])}
tree(opt, [("C", "A"), ("C", "F"), ("A", "B"), ("F", "D"), ("F", "G"), ("D", "E")],
     "optimal: cost 49", "6·1 + 9·2 + 7·3 + 1·4 = 49", 475)
for d, y in enumerate(ys, start=1):
    S.text(330, y, f"depth {d}", size=11, color="var(--muted)")
save("a02-obst", S.figure(
    "<strong>Two binary search trees for the keys A–G</strong> with search frequencies 4, 2, 6, 3, 1, 5, 2 (the small "
    "number in each node). Cost = Σ frequency × depth, with the root at depth 1; the sums group the nodes by depth. "
    "The optimal tree is the only tree of cost 49 among all 429; it puts the popular key C at the root and is taller "
    "than the balanced tree.",
    alt="balanced binary search tree rooted at D and optimal tree rooted at C"))
