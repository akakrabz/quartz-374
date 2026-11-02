#!/usr/bin/env python3
"""Figures for the Chapter 9 exercises page (Erickson, Algorithms). Writes tools/figs/a09x-<name>.html; then run
tools/assemble.py on content/2-algorithms/09-all-pairs-shortest-paths-exercises.md. Every number drawn here is
computed by running the page's algorithm (LeyzorekAPSP and FloydWarshall with predecessors, Johnson's reweighting,
vertex elimination, the divide-and-conquer closure); tools/checks/a09x.py re-derives the same facts."""
import math
import os
from figlib import SVG, Automaton, SERIF_IT, SANS, MONO

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")
os.makedirs(OUT, exist_ok=True)
INF = math.inf


def save(name, html):
    with open(os.path.join(OUT, name + ".html"), "w", encoding="utf-8") as f:
        f.write(html + "\n")
    print("wrote", name)


def neg(x):
    """Typographic minus for labels."""
    return str(x).replace("-", "−")


# =========================================================================== shared algorithms
def init_tables(n, E):
    dist = [[0 if u == v else E.get((u, v), INF) for v in range(n)] for u in range(n)]
    pred = [[u if (u != v and (u, v) in E) else None for v in range(n)] for u in range(n)]
    return dist, pred


def leyzorek(n, E):
    dist, pred = init_tables(n, E)
    for _ in range(math.ceil(math.log2(n))):
        for u in range(n):
            for v in range(n):
                for x in range(n):
                    if dist[u][v] > dist[u][x] + dist[x][v]:
                        dist[u][v] = dist[u][x] + dist[x][v]
                        pred[u][v] = pred[x][v]
    return dist, pred


def floyd_warshall(n, E):
    dist, pred = init_tables(n, E)
    for r in range(n):
        for u in range(n):
            for v in range(n):
                if dist[u][v] > dist[u][r] + dist[r][v]:
                    dist[u][v] = dist[u][r] + dist[r][v]
                    pred[u][v] = pred[r][v]
    return dist, pred


# =========================================================================== 1. Leyzorek's pointer cycle
# a=0, b=1, c=2, d=3 (the loops run in the order a, b, c, d)
CE = {(3, 2): 1, (2, 1): 1, (1, 0): 1, (0, 1): -1}
dL, pL = leyzorek(4, CE)
dF, pF = floyd_warshall(4, CE)
assert dL[3] == dF[3] == [3, 2, 1, 0]
assert pL[3][:3] == [1, 0, 3] and pF[3][:3] == [1, 2, 3]
NAMES = "abcd"
A = Automaton(600, 236, r=15)
XS = {"d": 70, "c": 190, "b": 310, "a": 430}
for row, (y, P, title) in enumerate([(70, pL, "LeyzorekAPSP, plain update"),
                                     (180, pF, "FloydWarshall (or Leyzorek with pairs)")]):
    for v in "dcba":
        A.state(f"{v}{row}", XS[v], y, label=v, hi=False)
    ptr = {(NAMES[P[3][x]], NAMES[x]) for x in range(3)}        # pointer edges p -> x of row d
    for (u, v), w in CE.items():
        nu, nv = NAMES[u], NAMES[v]
        on = (nu, nv) in ptr
        bend = 0
        if {nu, nv} == {"a", "b"}:
            bend = 14 if nu == "b" else 14
        A.edge(f"{nu}{row}", f"{nv}{row}", neg(w), bend=bend, color="var(--hi)" if on else "currentColor",
               width=2.6 if on else 1.4, label_dist=11)
    for v in "dcba":
        A.text(XS[v], y + 30, f"{dL[3][NAMES.index(v)]}", size=12, font=MONO, color="var(--muted)")
    A.text(500, y, title if row == 0 else "", size=13, anchor="start", color="currentColor")
A.text(500, 180, "FloydWarshall", size=13, anchor="start")
A.text(500, 197, "(or Leyzorek", size=13, anchor="start", color="var(--muted)")
A.text(500, 214, "with pairs)", size=13, anchor="start", color="var(--muted)")
A.items = [it for it in A.items if "LeyzorekAPSP, plain" not in it]
A.text(500, 62, "LeyzorekAPSP,", size=13, anchor="start")
A.text(500, 79, "plain update", size=13, anchor="start", color="var(--muted)")
save("a09x-pointer-cycle", A.figure(
    "<strong>The plain predecessor update can close a zero-length pointer cycle.</strong> Edges <i>d</i>→<i>c</i>→"
    "<i>b</i>→<i>a</i> of weight 1 and <i>a</i>→<i>b</i> of weight −1; the cycle <i>a</i>→<i>b</i>→<i>a</i> has "
    "length 0. The grey numbers are the (correct) distances from <i>d</i>; red edges are the pointer edges "
    "<i>pred</i>[<i>d</i>, <i>x</i>]→<i>x</i>. Top: LeyzorekAPSP sets <i>pred</i>[<i>d</i>, <i>a</i>] = <i>b</i>, "
    "then reaches <i>b</i> through <i>a</i> (length 2, a tie with the path through <i>c</i>, which therefore never "
    "replaces it) and sets <i>pred</i>[<i>d</i>, <i>b</i>] = <i>a</i>: "
    "following the pointers from <i>a</i> never gets back to <i>d</i>. Bottom: the correct pointers.",
    alt="two copies of a four-vertex path graph with a two-cycle; the top copy has a cycle of red pointer edges"))

# =========================================================================== 2. zero cycles (Exercise 4)
V4 = "abcdef"
FIG4 = {(0, 1): 2, (1, 2): -3, (2, 0): 1, (1, 3): -1, (3, 4): 2, (4, 3): -2, (2, 5): 1, (5, 4): 0, (4, 1): 3}
# prices: Bellman-Ford from an artificial source with 0-edges (plain iteration to a fixpoint suffices here)
pi = [0] * 6
for _ in range(7):
    for (u, v), w in FIG4.items():
        pi[v] = min(pi[v], pi[u] + w)
red = {(u, v): pi[u] + w - pi[v] for (u, v), w in FIG4.items()}
assert pi == [-2, 0, -3, -4, -2, -2], pi
assert all(r >= 0 for r in red.values())
Z = {e for e, r in red.items() if r == 0}
H = {(0, 1), (1, 2), (2, 0), (3, 4), (4, 3)}
assert Z == H | {(2, 5), (5, 4)}
POS4 = {"a": (40, 62), "b": (150, 62), "c": (95, 160), "d": (262, 62), "e": (262, 160), "f": (178, 160)}
A = Automaton(640, 238, r=15)
for panel, ox in enumerate((0, 330)):
    for v in V4:
        x, y = POS4[v]
        A.state(f"{v}{panel}", x + ox, y, label=v)
    for (u, v), w in FIG4.items():
        nu, nv = V4[u], V4[v]
        bend = 12 if {nu, nv} == {"d", "e"} else 0
        lside = 1
        if panel == 0:
            A.edge(f"{nu}{panel}", f"{nv}{panel}", neg(w), bend=bend, width=1.4, label_side=lside)
        else:
            if (u, v) in H:
                A.edge(f"{nu}{panel}", f"{nv}{panel}", "0", bend=bend, color="var(--hi)", width=2.6, label_side=lside)
            elif (u, v) in Z:
                A.edge(f"{nu}{panel}", f"{nv}{panel}", "0", bend=bend, color="var(--accent)", width=2.4,
                       label_side=lside)
            else:
                A.edge(f"{nu}{panel}", f"{nv}{panel}", str(red[(u, v)]), bend=bend, color="var(--muted)",
                       width=1.2, dash="4 3", label_side=lside)
PIL = {"a": (-4, -26), "b": (0, -26), "c": (0, 28), "d": (0, -26), "e": (0, 28), "f": (0, 28)}
for v in V4:
    x, y = POS4[v]
    dx, dy = PIL[v]
    A.text(x + dx, y + dy, "π=" + neg(pi[V4.index(v)]), size=12, font=MONO, color="var(--muted)")
A.text(150, 222, "weights w and prices π = dist(s, ·)", size=12, color="var(--muted)")
A.text(480, 222, "reduced weights w′ ≥ 0", size=12, color="var(--muted)")
save("a09x-zero", A.figure(
    "<strong>Zero cycles become cycles of zero-weight edges.</strong> Left: a graph with negative edges but no "
    "negative cycle, with Bellman–Ford prices π(<i>v</i>) from an artificial source. Right: the reduced weights "
    "<i>w</i>′(<i>u</i>→<i>v</i>) = π(<i>u</i>) + <i>w</i>(<i>u</i>→<i>v</i>) − π(<i>v</i>). The zero-weight "
    "edges form <i>Z</i> (solid); <i>H</i> keeps the ones inside a strong component of <i>Z</i> (red): exactly the "
    "two zero cycles <i>a</i>→<i>b</i>→<i>c</i>→<i>a</i> and <i>d</i>→<i>e</i>→<i>d</i>. The blue edges "
    "<i>c</i>→<i>f</i>→<i>e</i> have reduced weight 0 but lie on no cycle of <i>Z</i>.",
    alt="the same six-vertex graph twice: original weights with prices, and reduced weights with the zero cycles in red"))

# =========================================================================== 3. deleting a vertex (Exercise 8)
U = ["u1", "u2", "v", "x1", "x2"]
FIG8 = {(0, 2): 2, (1, 2): -1, (2, 3): 3, (2, 4): 1, (0, 3): 4, (4, 1): 2}
W8 = {}
for a in (0, 1, 3, 4):
    for b in (0, 1, 3, 4):
        if a != b:
            c = min(FIG8.get((a, b), INF), FIG8.get((a, 2), INF) + FIG8.get((2, b), INF))
            if c < INF:
                W8[(a, b)] = c
assert W8 == {(0, 3): 4, (0, 4): 3, (1, 3): 2, (1, 4): 0, (4, 1): 2}
LAB = {"u1": "u₁", "u2": "u₂", "v": "v", "x1": "x₁", "x2": "x₂"}
P8 = {"u1": (40, 52), "u2": (40, 172), "v": (150, 112), "x1": (260, 52), "x2": (260, 172)}
A = Automaton(620, 236, r=15)
for panel, ox in enumerate((0, 330)):
    for k, name in enumerate(U):
        if panel == 1 and name == "v":
            continue
        x, y = P8[name]
        A.state(f"{name}{panel}", x + ox, y, label=LAB[name], hi=(name == "v"))
ED = {0: FIG8, 1: W8}
for panel in (0, 1):
    for (a, b), w in ED[panel].items():
        na, nb = U[a], U[b]
        bend = 0
        if (na, nb) == ("u1", "x1"):
            bend = 14
        if {na, nb} == {"u2", "x2"}:
            bend = -14
        new = panel == 1 and (a, b) not in FIG8
        lpos = 0.5
        if panel == 1 and (na, nb) in (("u1", "x2"), ("u2", "x1")):
            lpos = 0.25
        A.edge(f"{na}{panel}", f"{nb}{panel}", neg(w), bend=bend, label_pos=lpos,
               color="var(--accent)" if new else ("var(--hi)" if panel == 0 and "v" in (na, nb) else "currentColor"),
               width=2.2 if new else 1.4)
A.text(150, 222, "G", size=14, font=SERIF_IT, italic=True)
A.text(480, 222, "G′ on V ∖ {v}", size=14, font=SERIF_IT, italic=True)
save("a09x-eliminate", A.figure(
    "<strong>Deleting a vertex without changing distances.</strong> Left: the four edges at <i>v</i> (red) and two "
    "other edges. Right: <i>G</i>′ on the remaining vertices; every in-neighbor <i>u</i> and out-neighbor "
    "<i>x</i> of <i>v</i> get an edge <i>u</i>→<i>x</i> of weight min{<i>w</i>(<i>u</i>→<i>x</i>), "
    "<i>w</i>(<i>u</i>→<i>v</i>) + <i>w</i>(<i>v</i>→<i>x</i>)}. Three new edges (blue) replace detours through "
    "<i>v</i>; <i>u</i>₁→<i>x</i>₁ keeps its weight 4 &lt; 2 + 3, and <i>x</i>₂→<i>u</i>₂ is unchanged.",
    alt="a five-vertex graph and the four-vertex graph obtained by deleting its middle vertex"))

# =========================================================================== 4. closure of a dag by blocks (10b)
N = 8
DAG = [(0, 1), (0, 2), (1, 3), (2, 3), (3, 4), (2, 5), (4, 6), (5, 6), (6, 7), (1, 6)]
assert all(u < v for u, v in DAG)
R = [[i == j for j in range(N)] for i in range(N)]
for (u, v) in DAG:
    R[u][v] = True
for k in range(N):
    for i in range(N):
        for j in range(N):
            if R[i][k] and R[k][j]:
                R[i][j] = True
h = N // 2
# the block identity R_XY = R_X A_XY R_Y
AXY = [[(i, h + j) in DAG for j in range(h)] for i in range(h)]
T1 = [[any(R[i][k] and AXY[k][j] for k in range(h)) for j in range(h)] for i in range(h)]
RXY = [[any(T1[i][k] and R[h + k][h + j] for k in range(h)) for j in range(h)] for i in range(h)]
assert all(RXY[i][j] == R[i][h + j] for i in range(h) for j in range(h))
assert not any(R[h + i][j] for i in range(h) for j in range(h))
S = SVG(640, 236)
# left: the dag in topological order
X0, DX, Y0 = 22, 36, 140
for (u, v) in DAG:
    x1, x2 = X0 + u * DX, X0 + v * DX
    cross = u < h <= v
    col = "var(--hi)" if cross else "currentColor"
    if v == u + 1:
        S.line(x1 + 11, Y0, x2 - 13.5, Y0, color=col, width=1.6 if not cross else 2.2, arrow=True)
    else:
        hgt = 16 + 16 * (v - u - 1)
        a = math.radians(60)
        sx, sy = x1 + 11 * math.cos(a), Y0 - 11 * math.sin(a)
        ex, ey = x2 - 13.5 * math.cos(a), Y0 - 13.5 * math.sin(a)
        S.path(f"M{sx:.1f},{sy:.1f} C{x1 + 0.2 * (x2 - x1):.1f},{Y0 - hgt * 1.3:.1f} "
               f"{x2 - 0.2 * (x2 - x1):.1f},{Y0 - hgt * 1.3:.1f} {ex:.1f},{ey:.1f}", color=col,
               width=1.3 if not cross else 2.0, arrow=True)
for v in range(N):
    S.circle(X0 + v * DX, Y0, 11, width=1.4)
    S.text(X0 + v * DX, Y0 + 1, str(v + 1), size=13, font=SANS)
sep = X0 + (h - 0.5) * DX
S.line(sep, 30, sep, 176, dash="4 3", color="var(--muted)", width=1.2)
S.text(X0 + 1.5 * DX, 174, "X", size=15, font=SERIF_IT, italic=True, color="var(--muted)")
S.text(X0 + 5.5 * DX, 174, "Y", size=15, font=SERIF_IT, italic=True, color="var(--muted)")
S.text(X0 + 3.5 * DX, 206, "vertices in topological order", size=12, color="var(--muted)")
# right: the reachability matrix
MX, MY, C = 316, 34, 19
for i in range(N):
    S.text(MX - 9, MY + i * C + C / 2, str(i + 1), size=10, color="var(--muted)")
    S.text(MX + i * C + C / 2, MY - 9, str(i + 1), size=10, color="var(--muted)")
for i in range(N):
    for j in range(N):
        if R[i][j]:
            blk_hi = i < h <= j
            S.rect(MX + j * C + 3, MY + i * C + 3, C - 6, C - 6, rx=2, stroke="none",
                   fill="var(--hi)" if blk_hi else "var(--accent)", fill_opacity=0.75 if blk_hi else 0.55, width=0)
S.rect(MX, MY, N * C, N * C, stroke="currentColor", width=1.4)
S.line(MX + h * C, MY, MX + h * C, MY + N * C, width=1.4)
S.line(MX, MY + h * C, MX + N * C, MY + h * C, width=1.4)
S.text(MX + h * C / 2, MY + 1.5 * h * C, "0", size=22, font=SANS, color="var(--muted)")


def sym(base, sub):
    return (f'<tspan font-family="{SERIF_IT}" font-style="italic">{base}</tspan>'
            f'<tspan font-family="{SERIF_IT}" font-style="italic" font-size="10" dy="4">{sub}</tspan>'
            f'<tspan dy="-4"> </tspan>')


TX = MX + N * C + 14
S.text(TX, MY + h * C / 2 - 10, "rows of X:", size=12, anchor="start", color="var(--muted)")
for (yy, left, right) in ((MY + h * C / 2 + 11, sym("R", "X"),
                            sym("R", "X") + "·" + sym("A", "XY") + "·" + sym("R", "Y")),
                           (MY + 1.5 * h * C + 11, "0", sym("R", "Y"))):
    S.text(TX + 8, yy, left, size=15, anchor="middle", raw=True)
    S.text(TX + 30, yy, "|", size=15, anchor="middle", color="var(--muted)")
    S.text(TX + 42, yy, right, size=15, anchor="start", raw=True)
S.text(TX, MY + 1.5 * h * C - 10, "rows of Y:", size=12, anchor="start", color="var(--muted)")
S.text(MX + N * C / 2, MY + N * C + 20, "R*[i, j] = 1 iff i reaches j", size=12, color="var(--muted)")
save("a09x-dag-blocks", S.figure(
    "<strong>The closure of a topologically sorted dag, by blocks.</strong> Left: an 8-vertex dag; every edge goes "
    "right, and the three red edges cross from the first half <i>X</i> to the second half <i>Y</i>. Right: its "
    "reflexive reachability matrix. No path goes from <i>Y</i> back to <i>X</i> (zero block); paths inside "
    "<i>X</i> or inside <i>Y</i> stay there (two recursive closures); and every path from <i>X</i> to <i>Y</i> "
    "crosses exactly one red edge, so the red block is the boolean product <i>R<sub>X</sub></i> · "
    "<i>A<sub>XY</sub></i> · <i>R<sub>Y</sub></i>.",
    alt="a dag drawn on a line split into two halves, and its 8 by 8 reachability matrix split into four blocks"))
