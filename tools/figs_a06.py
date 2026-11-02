#!/usr/bin/env python3
"""Figures for Algorithms Chapter 6 (depth-first search). Writes tools/figs/a06-<name>.html; then run
tools/assemble.py on the chapter page. Every label drawn (pre/post times, edge classes, LLP values, strong
components) is computed here by running the algorithms the page states; tools/checks/a06.py re-checks the
figure HTML against its own computation."""
import math
import os
import sys

from figlib import SVG, Automaton, SANS, SERIF_IT

sys.setrecursionlimit(10000)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")
os.makedirs(OUT, exist_ok=True)
NEG = -math.inf


def save(name, html):
    with open(os.path.join(OUT, name + ".html"), "w", encoding="utf-8") as f:
        f.write(html + "\n")
    print("wrote", name)


def overlay_figure(A, overlay, caption, alt):
    """A.figure(), with the SVG items of `overlay` drawn on top of the edges and states."""
    svg = A.svg(alt).replace("</svg>", "".join(overlay.items) + "</svg>")
    out = f'<figure class="cs-fig">{svg}<figcaption>{caption}</figcaption></figure>'
    assert "\n\n" not in out
    return out.replace("\n", " ")


def graph(vertices, edges):
    G = {v: [] for v in vertices}
    for e in edges.split():
        G[e[0]].append(e[1])
    return G


def dfsall(G, order=None):
    """DFSAll with the clock: pre, post, parent."""
    pre, post, parent = {}, {}, {}
    clock = 0

    def dfs(v):
        nonlocal clock
        clock += 1
        pre[v] = clock
        for w in G[v]:
            if w not in pre:
                parent[w] = v
                dfs(w)
        clock += 1
        post[v] = clock

    for v in (order or list(G)):
        if v not in pre:
            parent[v] = None
            dfs(v)
    return pre, post, parent


def classify(pre, post, parent, u, v):
    if pre[u] < pre[v] < post[v] < post[u]:
        return "tree" if parent[v] == u else "forward"
    if pre[v] <= pre[u] < post[u] <= post[v]:
        return "back"
    return "cross"


# The book's example graph (Figures 6.4, 6.13, 6.14, 6.17): vertices a..p on a 4x4 grid, adjacency lists in
# alphabetical order, DFSAll considers the vertices in alphabetical order.
V16 = "abcdefghijklmnop"
G16 = graph(V16, "ab bf fg fl ga gc gk ch dc hd hl kh kl lo lp ok ef ei in jk jm mi nj no")
for v in G16:
    G16[v].sort()
GRID = {v: (i % 4, i // 4) for i, v in enumerate(V16)}
pre, post, parent = dfsall(G16)
assert "".join(sorted(V16, key=pre.get)) == "abfgchdlokpeinjm"
assert "".join(sorted(V16, key=post.get)) == "dkoplhcgfbamjnie"

STYLE = {
    "tree": dict(color="var(--accent)", width=2.4, dash=None),
    "forward": dict(color="var(--accent2)", width=1.7, dash="7 4"),
    "back": dict(color="var(--hi)", width=1.7, dash="7 3 2 3"),
    "cross": dict(color="var(--muted)", width=1.7, dash="2 3"),
}

# =========================================================================== 1. DFS forest with pre/post labels
DX, DY, X0, Y0 = 140, 100, 60, 52
A = Automaton(560, 452, r=17)
for v in V16:
    c, r = GRID[v]
    A.state(v, X0 + c * DX, Y0 + r * DY, start="left" if parent[v] is None else None)
BEND = {("g", "a"): -8}
counts = {}
for u in G16:
    for v in G16[u]:
        k = classify(pre, post, parent, u, v)
        counts[k] = counts.get(k, 0) + 1
        st = STYLE[k]
        A.edge(u, v, bend=BEND.get((u, v), 0), color=st["color"], width=st["width"], dash=st["dash"])
assert counts == {"tree": 14, "forward": 2, "back": 5, "cross": 3}, counts
# pre/post label placement (dx, dy) chosen to avoid the edges at each vertex
OFF = {"a": (0, -29), "b": (0, -29), "c": (0, -29), "d": (0, -29),
       "e": (0, -29), "f": (0, 30), "g": (37, -12), "h": (37, 0),
       "i": (-37, 0), "j": (0, -29), "k": (-34, 24), "l": (37, 0),
       "m": (0, 30), "n": (0, 30), "o": (0, 30), "p": (0, 30)}
LAB = SVG(560, 452)
for v in V16:
    c, r = GRID[v]
    dx, dy = OFF[v]
    LAB.text(X0 + c * DX + dx, Y0 + r * DY + dy, f"{pre[v]}/{post[v]}", size=12, halo=True)
# legend
lx, ly = 30, 432
for k in ["tree", "forward", "back", "cross"]:
    st = STYLE[k]
    A.line(lx, ly, lx + 34, ly, color=st["color"], width=st["width"], dash=st["dash"])
    A.text(lx + 42, ly, f"{k} ({counts[k]})", size=13, anchor="start")
    lx += 132
save("a06-dfs-forest", overlay_figure(A, LAB, 
    "<strong>A depth-first forest of the book’s example graph.</strong> DFSAll considers the vertices, and every "
    "vertex its edges, in alphabetical order; the two roots <i>a</i> and <i>e</i> have entry arrows, and each "
    "vertex is labeled <i>pre</i>/<i>post</i>. Preorder <i>abfgchdlokpeinjm</i>, postorder "
    "<i>dkoplhcgfbamjnie</i>. Of the 24 edges, 14 are tree edges (16 vertices minus 2 roots), 2 forward, 5 back "
    "and 3 cross. The back edges <i>g</i>→<i>a</i>, <i>d</i>→<i>c</i>, <i>k</i>→<i>h</i>, <i>k</i>→<i>l</i> and "
    "<i>m</i>→<i>i</i> are exactly the edges <i>u</i>→<i>v</i> with <i>u.post</i> &lt; <i>v.post</i>.",
    alt="directed graph on a four by four grid with its depth-first forest, edge classes and pre/post times"))

# =========================================================================== 2. active intervals
depth = {}
for v in sorted(V16, key=pre.get):
    depth[v] = 0 if parent[v] is None else depth[parent[v]] + 1
S = SVG(600, 250)
step, x0, top, rowh = 17.2, 28, 14, 22
X = lambda t: x0 + (t - 1) * step
for v in V16:
    y = top + depth[v] * rowh
    S.rect(X(pre[v]), y, X(post[v]) - X(pre[v]), rowh - 4, rx=3, stroke="currentColor",
           fill="var(--accent)", fill_opacity=0.14, width=1.1)
    S.text((X(pre[v]) + X(post[v])) / 2, y + (rowh - 4) / 2 + 0.5, v, size=13, font=SERIF_IT, italic=True)
ay = top + 9 * rowh + 8
S.line(X(1) - 10, ay, X(32) + 14, ay, width=1.2, arrow=True)
for t in range(1, 33):
    S.line(X(t), ay - 4, X(t), ay + 4, width=1)
    S.line(X(t), top, X(t), ay - 4, width=0.6, dash="2 3", opacity=0.35)
    S.text(X(t), ay + 14, str(t), size=10.5)
S.text(X(1) - 14, ay + 14, "", size=10)
save("a06-intervals", S.figure(
    "<strong>The active intervals of the same traversal.</strong> Vertex <i>v</i> occupies "
    "[<i>v.pre</i>, <i>v.post</i>], drawn one row below its parent. Any two intervals are nested or disjoint, and "
    "nested exactly when one vertex is an ancestor of the other; reading the left ends gives the preorder, the "
    "right ends the postorder. The active vertices at any moment are the intervals stacked above that time: a "
    "path of tree edges.",
    alt="active intervals of the sixteen vertices drawn as nested bars over a time axis from 1 to 32"))

# =========================================================================== 3. longest path in a dag
WD = graph("saxbcdt", "sa sb ab ac ax bc bd cd ct dt")
W = {("s", "a"): 2, ("s", "b"): 5, ("a", "b"): 4, ("a", "c"): 3, ("a", "x"): 7, ("b", "c"): 1,
     ("b", "d"): 2, ("c", "d"): 2, ("c", "t"): 5, ("d", "t"): 4}
wpre, wpost, wpar = dfsall(WD, ["s"])
post_order = sorted(WD, key=wpost.get)
assert "".join(post_order) == "tdcbxas"
topo = post_order[::-1]
LLP = {}
for v in post_order:
    LLP[v] = 0 if v == "t" else max([W[(v, w)] + LLP[w] for w in WD[v]], default=NEG)
assert [LLP[v] for v in topo] == [13, 11, NEG, 7, 6, 4, 0]
best_edges = {("s", "a"), ("a", "b"), ("b", "c"), ("c", "d"), ("d", "t")}
assert sum(W[e] for e in best_edges) == 13
P = Automaton(610, 212, r=17)
xs = {v: 66 + i * 84 for i, v in enumerate(topo)}
YL = 100
for v in topo:
    P.state(v, xs[v], YL)
ARC = {("a", "b"): 28, ("a", "c"): 48, ("c", "t"): 28, ("s", "b"): -40, ("b", "d"): -28}
SIDE = {("a", "x"): -1}
for (u, v), w in W.items():
    hi = (u, v) in best_edges
    col = "var(--accent)" if hi else "currentColor"
    wid = 2.6 if hi else 1.4
    P.edge(u, v, label=str(w), bend=ARC.get((u, v), 0), color=col, width=wid, label_color="currentColor",
           mono=False, label_dist=10, label_side=SIDE.get((u, v), 1))
BY = 176
for v in topo:
    val = "−∞" if LLP[v] == NEG else str(LLP[v])
    P.rect(xs[v] - 19, BY, 38, 22, rx=4, stroke="currentColor", fill="var(--accent)", fill_opacity=0.10, width=1.1)
    P.text(xs[v], BY + 11.5, val, size=13)
P.text(4, BY + 11.5, "LLP", size=12, anchor="start", color="var(--muted)")
save("a06-longest-path", P.figure(
    "<strong>A weighted dag in topological order, with LLP(<i>v</i>) = length of the longest path from <i>v</i> "
    "to <i>t</i>.</strong> The order <i>s a x b c d t</i> is the reverse of the postorder <i>t d c b x a s</i> of "
    "DFS(<i>s</i>) with the edges taken in the order <i>s</i>: <i>a, b</i>; <i>a</i>: <i>b, c, x</i>; <i>b</i>: "
    "<i>c, d</i>; <i>c</i>: <i>d, t</i>, so every edge points right. The values are computed right to left "
    "(postorder); <i>x</i> cannot reach <i>t</i>, so LLP(<i>x</i>) = −∞. The longest path, in color, is "
    "<i>s a b c d t</i> of length 13; always taking the heaviest edge gives <i>s b d t</i> of length 11.",
    alt="seven-vertex weighted dag drawn on a line in topological order with longest-path values"))

# =========================================================================== 4. strong components and scc(G)
REACH = {}
for v in V16:
    seen, stack = {v}, [v]
    while stack:
        u = stack.pop()
        for w in G16[u]:
            if w not in seen:
                seen.add(w)
                stack.append(w)
    REACH[v] = seen
COMP = {v: frozenset(u for u in V16 if u in REACH[v] and v in REACH[u]) for v in V16}
comps = sorted(set(COMP.values()), key=lambda c: min(c))
assert sorted("".join(sorted(c)) for c in comps) == ["abfg", "cdhklo", "e", "ijmn", "p"]
CDAG = {(COMP[u], COMP[v]) for u in V16 for v in G16[u] if COMP[u] != COMP[v]}
assert {("".join(sorted(a)), "".join(sorted(b))) for a, b in CDAG} == \
    {("e", "abfg"), ("e", "ijmn"), ("abfg", "cdhklo"), ("ijmn", "cdhklo"), ("cdhklo", "p")}
CCOL = {"abfg": "var(--accent)", "cdhklo": "var(--accent2)", "ijmn": "var(--hi)", "e": "var(--muted)",
        "p": "var(--muted)"}
C = Automaton(640, 372, r=16)
DX2, DY2, X2, Y2 = 92, 92, 44, 44
pos = {v: (X2 + GRID[v][0] * DX2, Y2 + GRID[v][1] * DY2) for v in V16}
# blobs: thick translucent strokes along grid-adjacent pairs inside each component
for comp in comps:
    name = "".join(sorted(comp))
    col = CCOL[name]
    members = sorted(comp)
    if len(members) == 1:
        x, y = pos[members[0]]
        C.add(f'<circle cx="{x}" cy="{y}" r="27" fill="{col}" fill-opacity="0.16" stroke="none"/>')
        continue
    segs = []
    for a in members:
        for b in members:
            (ca, ra), (cb, rb) = GRID[a], GRID[b]
            if a < b and abs(ca - cb) + abs(ra - rb) == 1:
                segs.append((a, b))
    d = " ".join(f"M{pos[a][0]},{pos[a][1]} L{pos[b][0]},{pos[b][1]}" for a, b in segs)
    # fill 2x2 blocks of the grid that lie entirely inside the component (no hole in the middle)
    cells = {GRID[v]: v for v in members}
    for (cc, rr) in list(cells):
        if all((cc + i, rr + j) in cells for i in (0, 1) for j in (0, 1)):
            d += f" M{pos[cells[(cc, rr)]][0]},{pos[cells[(cc, rr)]][1]} h{DX2} v{DY2} h{-DX2} z"
    C.add(f'<g opacity="0.16"><path d="{d}" fill="{col}" stroke="{col}" stroke-width="54" '
          f'stroke-linecap="round" stroke-linejoin="round"/></g>')
for v in V16:
    C.state(v, *pos[v])
for u in V16:
    for v in G16[u]:
        inter = COMP[u] != COMP[v]
        C.edge(u, v, bend=(-6 if (u, v) == ("g", "a") else 0), color="currentColor",
               width=1.4, dash="5 3" if inter else None)
# the component graph
CX = {"e": (408, 186), "abfg": (494, 92), "ijmn": (494, 280), "cdhklo": (590, 186), "p": (590, 318)}
for name, (x, y) in CX.items():
    w = {"e": 36, "p": 36, "abfg": 74, "ijmn": 74, "cdhklo": 92}[name]
    C.state("C" + name, x, y, label=" ".join(name), shape="rounded" if len(name) > 1 else "circle", w=w, r=17)
for a, b in [("e", "abfg"), ("e", "ijmn"), ("abfg", "cdhklo"), ("ijmn", "cdhklo"), ("cdhklo", "p")]:
    C.edge("C" + a, "C" + b, width=1.6)
for name, (x, y) in CX.items():
    w = {"e": 36, "p": 36, "abfg": 74, "ijmn": 74, "cdhklo": 92}[name]
    C.add(f'<rect x="{x - w / 2 - 5}" y="{y - 22}" width="{w + 10}" height="44" rx="21" fill="{CCOL[name]}" '
          f'fill-opacity="0.16" stroke="none"/>')
C.text(500, 18, "scc(G)", size=14, font=SERIF_IT, italic=True)
save("a06-scc", C.figure(
    "<strong>The strong components of the book’s example graph, and its strong component graph.</strong> Left: "
    "the five components {<i>a, b, f, g</i>}, {<i>c, d, h, k, l, o</i>}, {<i>e</i>}, {<i>i, j, m, n</i>} and "
    "{<i>p</i>}; dashed edges join different components. Right: contracting each component to a vertex and "
    "collapsing parallel edges gives scc(<i>G</i>), a dag with source {<i>e</i>} and sink {<i>p</i>}.",
    alt="the sixteen-vertex graph with its five strong components shaded, and the five-vertex component dag"))
