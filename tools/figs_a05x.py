#!/usr/bin/env python3
"""Figures for the Chapter 5 exercises page (content/2-algorithms/05-basic-graph-algorithms-exercises.md).
Writes tools/figs/a05x-<name>.html; then run tools/assemble.py on the page. Every path, distance and count drawn here
is computed below by BFS; tools/checks/a05x.py re-derives the numbers in the captions independently."""
import math
import os
from collections import deque
from figlib import SVG, MONO, SERIF_IT, SANS

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")
os.makedirs(OUT, exist_ok=True)


def save(name, html):
    with open(os.path.join(OUT, name + ".html"), "w", encoding="utf-8") as f:
        f.write(html + "\n")
    print("wrote", name)


def bfs(adj, s):
    dist, par, Q = {s: 0}, {s: None}, deque([s])
    while Q:
        v = Q.popleft()
        for w in adj[v]:
            if w not in dist:
                dist[w], par[w] = dist[v] + 1, v
                Q.append(w)
    return dist, par


def arrow_arc(S, p, q, bend, color, shorten=13, width=2.2):
    """Quadratic arrow from p to q, bowed by `bend` px to the left of travel, ends pulled back by `shorten`."""
    (x1, y1), (x2, y2) = p, q
    L = math.hypot(x2 - x1, y2 - y1)
    ux, uy = (x2 - x1) / L, (y2 - y1) / L
    nx, ny = uy, -ux  # left of travel in screen coordinates
    cx, cy = (x1 + x2) / 2 + nx * bend, (y1 + y2) / 2 + ny * bend
    sx, sy = x1 + ux * shorten + nx * bend * 0.35, y1 + uy * shorten + ny * bend * 0.35
    ex, ey = x2 - ux * shorten + nx * bend * 0.35, y2 - uy * shorten + ny * bend * 0.35
    S.path(f"M{sx:.1f},{sy:.1f} Q{cx:.1f},{cy:.1f} {ex:.1f},{ey:.1f}", color=color, width=width, arrow=True)
    # point on the curve at t = 1/2 (for a step label)
    return 0.25 * sx + 0.5 * cx + 0.25 * ex, 0.25 * sy + 0.5 * cy + 0.25 * ey


# =========================================================================== 1. number maze (Figure 5.14)
M = [[3, 5, 7, 4, 6], [5, 3, 1, 5, 3], [2, 8, 3, 1, 4], [4, 5, 7, 2, 3], [3, 1, 3, 2, None]]
n = 5
adj = {}
for i in range(n):
    for j in range(n):
        k = M[i][j] or 0
        adj[(i, j)] = [(i + k * di, j + k * dj) for di, dj in ((-1, 0), (1, 0), (0, -1), (0, 1))
                       if k and 0 <= i + k * di < n and 0 <= j + k * dj < n]
dist, par = bfs(adj, (0, 0))
path = [(4, 4)]
while par[path[-1]] is not None:
    path.append(par[path[-1]])
path.reverse()
assert len(path) - 1 == 8
UNREACH = sorted((i, j) for i in range(n) for j in range(n) if (i, j) not in dist)
CELL, GAP, TOP = 56, 50, 30
S = SVG(2 * n * CELL + GAP + 16, n * CELL + TOP + 10)
for panel in range(2):
    ox, oy = 8 + panel * (n * CELL + GAP), TOP
    S.text(ox + n * CELL / 2, 13, "the maze and a shortest solution" if panel == 0 else "BFS distance from the start",
           size=13, color="var(--muted)")
    for i in range(n):
        for j in range(n):
            x, y = ox + j * CELL, oy + i * CELL
            if panel == 1 and (i, j) in path:
                S.rect(x, y, CELL, CELL, stroke="none", fill="var(--accent)", fill_opacity=0.13, width=0)
            S.rect(x, y, CELL, CELL, stroke="currentColor", fill="none", width=0.8)
            cx, cy = x + CELL / 2, y + CELL / 2
            if panel == 0:
                if (i, j) == (4, 4):
                    S.text(cx, cy + 1, "★", size=22, color="var(--hi)")
                else:
                    S.text(x + 12, y + 13, str(M[i][j]), size=15, weight=600)
            else:
                if (i, j) in dist:
                    S.text(cx, cy + 1, str(dist[(i, j)]), size=17, color="var(--accent)", weight=600)
                else:
                    S.text(cx, cy + 1, "–", size=17, color="var(--muted)")
    S.rect(ox, oy, n * CELL, n * CELL, stroke="currentColor", fill="none", width=1.6)
    if panel == 0:
        S.rect(ox + 2, oy + 2, CELL - 4, CELL - 4, stroke="var(--hi)", fill="none", width=2)
        C = lambda v: (ox + v[1] * CELL + CELL / 2, oy + v[0] * CELL + CELL / 2)
        # bows chosen so that the two pairs of overlapping horizontal moves separate
        bends = [-10, -8, 12, 3, 8, 12, 4, -8]
        for step, (u, v) in enumerate(zip(path, path[1:]), 1):
            lx, ly = arrow_arc(S, C(u), C(v), bends[step - 1], "var(--hi)", shorten=7, width=1.9)
            S.circle(lx, ly, 8, stroke="var(--hi)", fill="var(--paper)", width=1.2)
            S.text(lx, ly + 0.5, str(step), size=11, color="var(--hi)", weight=600)
save("a05x-number-maze", S.figure(
    "<strong>Exercise 5.11: the maze of Figure 5.14.</strong> Left: the book's number maze (labels in the corners; "
    "start framed, goal ★) with a shortest solution "
    "found by BFS (moves numbered 1–8: right 3, down 4, left 2, right 1, up 3, left 1, right 3, down 3). Right: the "
    "BFS distance of every square from the top-left one in the move graph; the shaded squares are the solution's. "
    f"{len(UNREACH)} squares (–) cannot be reached at all.",
    alt="a five by five number maze with an eight-move solution, and a grid of BFS distances"))

# =========================================================================== 2. red and blue walk (Exercise 5.15)
P15 = {"s": (60, 52), "a": (190, 52), "b": (320, 52), "c": (60, 182), "d": (190, 182), "t": (320, 182)}
RED = [("s", "a"), ("a", "b"), ("b", "t"), ("t", "d"), ("d", "c"), ("c", "s")]
BLUE = [("c", "a"), ("d", "s"), ("b", "d"), ("t", "a")]
WALK = ["s", "a", "b", "d", "c", "a", "b", "t"]
R = 17
S = SVG(600, 236)


def straight(S, a, b, color, dash=None, width=1.8, off=0):
    (x1, y1), (x2, y2) = P15[a], P15[b]
    L = math.hypot(x2 - x1, y2 - y1)
    ux, uy = (x2 - x1) / L, (y2 - y1) / L
    nx, ny = uy, -ux
    x1, y1, x2, y2 = x1 + nx * off, y1 + ny * off, x2 + nx * off, y2 + ny * off
    S.line(x1 + ux * R, y1 + uy * R, x2 - ux * (R + 2.5), y2 - uy * (R + 2.5), color=color, width=width, arrow=True,
           dash=dash)


for a, b in RED:
    straight(S, a, b, "var(--hi)")
for a, b in BLUE:
    straight(S, a, b, "var(--accent)", dash="6 4", off=0)
for v, (x, y) in P15.items():
    S.circle(x, y, R, stroke="var(--hi)" if v in "st" else "currentColor", fill="var(--paper)", width=1.6)
    S.text(x, y + 1, v, size=17, font=SERIF_IT, italic=True)
# legend
S.line(32, 222, 62, 222, color="var(--hi)", width=1.8)
S.text(68, 222, "red", size=13, anchor="start")
S.line(112, 222, 142, 222, color="var(--accent)", width=1.8, dash="6 4")
S.text(148, 222, "blue", size=13, anchor="start")
# the walk as a table of steps
col = {e: "R" for e in RED}
col.update({e: "B" for e in BLUE})
colors = [col[(u, v)] for u, v in zip(WALK, WALK[1:])]
assert "".join(colors) == "RRBRBRR"
S.text(395, 28, "the shortest legal walk", size=13, color="var(--muted)", anchor="start")
for k, ((u, v), c) in enumerate(zip(zip(WALK, WALK[1:]), colors)):
    y = 54 + k * 22
    S.text(400, y, f"{k + 1}.", size=13, anchor="start", color="var(--muted)")
    S.text(424, y, u, size=15, font=SERIF_IT, italic=True, anchor="start")
    S.line(438, y, 470, y, color="var(--hi)" if c == "R" else "var(--accent)", width=1.8, arrow=True,
           dash=None if c == "R" else "6 4")
    S.text(478, y, v, size=15, font=SERIF_IT, italic=True, anchor="start")
    S.text(500, y, "red" if c == "R" else "blue", size=13, anchor="start",
           color="var(--hi)" if c == "R" else "var(--accent)")
save("a05x-red-blue", S.figure(
    "<strong>Exercise 5.15: the book's example.</strong> The red edges (solid) form the directed cycle "
    "<i>s</i>→<i>a</i>→<i>b</i>→<i>t</i>→<i>d</i>→<i>c</i>→<i>s</i>; the blue edges (dashed) are "
    "<i>c</i>→<i>a</i>, <i>d</i>→<i>s</i>, <i>b</i>→<i>d</i> and <i>t</i>→<i>a</i>. The obvious walk "
    "<i>s</i>→<i>a</i>→<i>b</i>→<i>t</i> uses three reds in a row; the shortest legal walk (right) has 7 edges, "
    "colored red, red, blue, red, blue, red, red.",
    alt="a six-vertex directed graph with red and blue edges and the seven-step walk from s to t"))

# =========================================================================== 3. Three Seashells (Figure 5.17)
PS = {"a": (0, 0), "b": (1, 0), "c": (2, 0), "p": (0, 1), "q": (1, 1), "r": (2, 1), "x": (0, 2), "y": (1, 2),
      "z": (2, 2)}
E_DRAWN = [("a", "b"), ("b", "c"), ("a", "p"), ("b", "q"), ("p", "q"), ("q", "r"), ("q", "x"), ("q", "y"), ("r", "z")]
E_FIXED = [e for e in E_DRAWN if e != ("q", "x")] + [("p", "x")]


def triples_bfs(E):
    A = {v: [] for v in PS}
    for u, v in E:
        A[u].append(v)
        A[v].append(u)
    import itertools
    adj = {t: [(a, b, c) for a in A[t[0]] for b in A[t[1]] for c in A[t[2]] if len({a, b, c}) == 3]
           for t in itertools.permutations(PS, 3)}
    d, _ = bfs(adj, ("a", "b", "c"))
    goals = [d[g] for g in itertools.permutations("xyz") if g in d]
    return min(goals) if goals else None


T_DRAWN, T_FIXED = triples_bfs(E_DRAWN), triples_bfs(E_FIXED)
assert T_DRAWN is None and T_FIXED == 4
SP, PW, R = 70, 250, 15
S = SVG(2 * PW + 20, 222)
for panel, (E, title) in enumerate([(E_DRAWN, "as drawn: no solution"), (E_FIXED, "x moved to p: 4 turns")]):
    ox, oy = 55 + panel * (PW + 20), 46
    P = lambda v: (ox + PS[v][0] * SP, oy + PS[v][1] * SP)
    S.text(ox + SP, 16, title, size=13, color="var(--muted)")
    for u, v in E:
        (x1, y1), (x2, y2) = P(u), P(v)
        L = math.hypot(x2 - x1, y2 - y1)
        ux, uy = (x2 - x1) / L, (y2 - y1) / L
        special = (panel == 0 and "x" in (u, v) and "q" in (u, v)) or (panel == 0 and set((u, v)) == {"q", "y"})
        moved = panel == 1 and set((u, v)) == {"p", "x"}
        S.line(x1 + ux * R, y1 + uy * R, x2 - ux * R, y2 - uy * R,
               color="var(--hi)" if special else ("var(--accent)" if moved else "currentColor"),
               width=2.6 if (special or moved) else 1.5, dash="5 4" if moved else None)
    for v in PS:
        x, y = P(v)
        goal = v in "xyz"
        if goal:
            S.circle(x, y, R + 4, stroke="currentColor", fill="var(--paper)", width=1.5)
        S.circle(x, y, R, stroke="currentColor", fill="var(--accent)" if v in "abc" else "var(--paper)",
                 width=1.5, fill_opacity=0.18 if v in "abc" else None)
        S.text(x, y + 1, v, size=16, font=SERIF_IT, italic=True)
save("a05x-seashells", S.figure(
    "<strong>Exercise 5.18: the puzzle of Figure 5.17.</strong> Tokens start on the shaded vertices <i>a</i>, "
    "<i>b</i>, <i>c</i> and must end on the double circles <i>x</i>, <i>y</i>, <i>z</i> (the book leaves the "
    "middle row unnamed; here <i>p</i>, <i>q</i>, <i>r</i>). Left, as printed: <i>x</i> and <i>y</i> are leaves "
    "of the same vertex <i>q</i>, so in the last turn two tokens would have to arrive from <i>q</i> at once — "
    "there is no solution, although the book shows \"the first two turns of a solution\". Right: with the edge "
    "<i>qx</i> replaced by <i>px</i>, the shortest solution has 4 turns and begins with the book's two.",
    alt="the Three Seashells graph as printed and with one edge moved"))
