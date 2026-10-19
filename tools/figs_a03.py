#!/usr/bin/env python3
"""Figures for Algorithms Chapter 3 (dynamic programming). Writes tools/figs/a03-<name>.html; then run
tools/assemble.py on the chapter page. Every number drawn is computed here by the same recurrences the page
states (and re-checked against the figure HTML by tools/checks/a03.py)."""
import os
from figlib import SVG, MONO, SERIF_IT, SANS

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")
os.makedirs(OUT, exist_ok=True)


def save(name, html):
    with open(os.path.join(OUT, name + ".html"), "w", encoding="utf-8") as f:
        f.write(html + "\n")
    print("wrote", name)


def fsub(i, size=13, color="currentColor"):
    """Raw SVG text body 'F' with subscript i."""
    return (f'F<tspan dy="3" style="font-size:{size - 3}px;font-style:normal;font-family:{SANS}">{i}</tspan>')


# =========================================================================== 1. Fibonacci recursion tree
N = 6


def rec_tree(n):
    """(n, [children]) recursion tree of RecFibo(n)."""
    return (n, [] if n <= 1 else [rec_tree(n - 1), rec_tree(n - 2)])


def mem_visit(tree):
    """Simulate MemFibo on the recursion tree: returns {id(node): kind} for the nodes MemFibo actually calls,
    kind in {'computed', 'lookup', 'base'}; the other nodes are never called."""
    memo = set()
    kinds = {}

    def go(t):
        n, kids = t
        if n <= 1:
            kinds[id(t)] = "base"
            return
        if n in memo:
            kinds[id(t)] = "lookup"
            return
        kinds[id(t)] = "computed"
        go(kids[0])
        go(kids[1])
        memo.add(n)

    go(tree)
    return kinds


root = rec_tree(N)
kinds = mem_visit(root)
S = SVG(600, 300)
leaf_w, level_h, x0, y0 = 44, 44, 14, 26
pos = {}


def place(t, left, depth):
    n, kids = t
    if not kids:
        x = left + leaf_w / 2
        pos[id(t)] = (x, y0 + depth * level_h)
        return x, left + leaf_w
    xs, cur = [], left
    for k in kids:
        kx, cur = place(k, cur, depth + 1)
        xs.append(kx)
    pos[id(t)] = ((xs[0] + xs[-1]) / 2, y0 + depth * level_h)
    return pos[id(t)][0], cur


place(root, x0, 0)
BW, BH = 30, 20


def edges(t):
    n, kids = t
    px, py = pos[id(t)]
    for k in kids:
        kx, ky = pos[id(k)]
        on = id(k) in kinds
        S.line(px + (kx - px) * 0.0, py + BH / 2, kx, ky - BH / 2 - 2.5, width=1.2, arrow=True,
               color="currentColor", opacity=None if on else 0.25)
        edges(k)


edges(root)
count_all = count_mem = 0


def nodes(t):
    global count_all, count_mem
    n, kids = t
    x, y = pos[id(t)]
    kind = kinds.get(id(t))
    count_all += 1
    if kind:
        count_mem += 1
    if kind == "computed":
        S.rect(x - BW / 2, y - BH / 2, BW, BH, rx=5, stroke="var(--accent)", fill="var(--accent)", fill_opacity=0.18, width=1.6)
        S.rect(x - BW / 2, y - BH / 2, BW, BH, rx=5, stroke="var(--accent)", fill="none", width=1.6)
    elif kind == "lookup":
        S.rect(x - BW / 2, y - BH / 2, BW, BH, rx=5, stroke="var(--hi)", fill="var(--paper)", width=1.6, dash="3 2")
    elif kind == "base":
        S.rect(x - BW / 2, y - BH / 2, BW, BH, rx=5, stroke="currentColor", fill="var(--paper)", width=1.3)
    else:
        S.rect(x - BW / 2, y - BH / 2, BW, BH, rx=5, stroke="var(--muted)", fill="var(--paper)", width=1.0)
    col = {"lookup": "var(--hi)", None: "var(--muted)"}.get(kind, "currentColor")
    S.text(x - 1, y, fsub(n), size=13, font=SERIF_IT, italic=True, raw=True, color=col)
    for k in kids:
        nodes(k)


nodes(root)
assert count_all == 25 and count_mem == 11
# legend
ly = 282
items = [("computed and stored", "computed"), ("read from the table", "lookup"), ("base case", "base"),
         ("not called by MemFibo", None)]
lx = 22
for label, kind in items:
    if kind == "computed":
        S.rect(lx, ly - 7, 18, 14, rx=4, stroke="var(--accent)", fill="var(--accent)", fill_opacity=0.18, width=1.4)
    elif kind == "lookup":
        S.rect(lx, ly - 7, 18, 14, rx=4, stroke="var(--hi)", fill="none", width=1.4, dash="3 2")
    elif kind == "base":
        S.rect(lx, ly - 7, 18, 14, rx=4, stroke="currentColor", fill="none", width=1.3)
    else:
        S.rect(lx, ly - 7, 18, 14, rx=4, stroke="var(--muted)", fill="none", width=1.0)
    S.text(lx + 24, ly, label, size=12, anchor="start", color="currentColor" if kind is not None else "var(--muted)")
    lx += 24 + 6.1 * len(label) + 22
save("a03-fib-tree", S.figure(
    "<strong>The recursion tree of RecFibo(6), trimmed by memoization.</strong> RecFibo makes all "
    "25 = 2<i>F</i><sub>7</sub> − 1 calls; the 13 leaves are the <i>F</i><sub>6</sub> = 8 calls on 1 and the "
    "<i>F</i><sub>5</sub> = 5 calls on 0. MemFibo makes only the 11 = 2·6 − 1 calls in color: it computes "
    "<i>F</i><sub>2</sub>, …, <i>F</i><sub>6</sub> once each, bottom up along the left spine, and the second "
    "recursive call of each of them is answered at once.",
    alt="recursion tree for the sixth Fibonacci number with the memoized calls highlighted"))

# =========================================================================== 2. dependency pictures
S = SVG(640, 400)
cs = 18
G = 6  # grid size


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
        S.rect(x0 + c * cs, y0 + r * cs, cs, cs, stroke="var(--accent)", fill="var(--accent)", fill_opacity=0.25, width=1.2)


def ctr(x0, y0, r, c):
    return x0 + c * cs + cs / 2, y0 + r * cs + cs / 2


def axes(x0, y0, rlab, clab):
    S.line(x0, y0 - 9, x0 + G * cs, y0 - 9, width=1.0, arrow=True)
    S.text(x0 + G * cs / 2, y0 - 18, clab, size=13, font=SERIF_IT, italic=True)
    S.line(x0 - 9, y0, x0 - 9, y0 + G * cs, width=1.0, arrow=True)
    S.text(x0 - 19, y0 + G * cs / 2, rlab, size=13, font=SERIF_IT, italic=True)


def dbl_arrow(x1, y1, x2, y2):
    """Outer-loop arrow: a thick hollow-looking arrow (two strokes)."""
    S.line(x1, y1, x2, y2, width=4.2, color="var(--accent2)", arrow=True)


def thin_arrow(x1, y1, x2, y2, both=False):
    if both:
        S.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="var(--accent2)" stroke-width="1.3" '
              f'stroke-linecap="round" marker-start="url(#ARR)" marker-end="url(#ARR)"/>')
    else:
        S.line(x1, y1, x2, y2, width=1.3, color="var(--accent2)", arrow=True)


TOP, BOT = 52, 222
cols = [56, 270, 484]
titles = ["LISbigger[i, j]", "Edit[i, j]", "OptCost[i, k]"]
for x, t in zip(cols, titles):
    S.text(x + G * cs / 2, 14, t, size=13, font=MONO)

# --- panel A: LISbigger, rows i = 0..5, columns j = 1..6 (6 = n+1, base column); used where i < j
xa = cols[0]
usedA = lambda r, c: r < c + 1
baseA = {(r, 5) for r in range(G)}
for y0 in (TOP, BOT):
    grid(xa, y0, usedA, baseA)
    axes(xa, y0, "i", "j")
ti, tj = 1, 2            # target row i = 1, column j = 3 (c = j - 1)
cell(xa, TOP, 1, 2, "target")
cell(xa, TOP, 1, 3, "dep")
cell(xa, TOP, 3, 3, "dep")
ax, ay = ctr(xa, TOP, 1, 2)
bx, by = ctr(xa, TOP, 1, 3)
cx_, cy_ = ctr(xa, TOP, 3, 3)
S.line(bx - 4, by, ax + 6, ay, width=1.4, color="var(--hi)", arrow=True)
S.path(f"M{cx_ - 3},{cy_ - 6} Q{ax + 2},{cy_ - 4} {ax + 1},{ay + 7}", color="var(--hi)", width=1.4, arrow=True)
# order: columns right to left (outer), any order within a column (inner)
dbl_arrow(xa + G * cs - 4, BOT + G * cs + 14, xa + 8, BOT + G * cs + 14)
for c in (4, 3, 2, 1):
    x = xa + c * cs + cs / 2
    thin_arrow(x, BOT + 5, x, BOT + (c + 1) * cs - 5, both=True)

# --- panel B: Edit, rows i, columns j; everything used
xb = cols[1]
usedB = lambda r, c: True
baseB = {(0, c) for c in range(G)} | {(r, 0) for r in range(G)}
for y0 in (TOP, BOT):
    grid(xb, y0, usedB, baseB)
    axes(xb, y0, "i", "j")
cell(xb, TOP, 3, 3, "target")
for (r, c) in ((2, 3), (3, 2), (2, 2)):
    cell(xb, TOP, r, c, "dep")
tx, ty = ctr(xb, TOP, 3, 3)
for (r, c) in ((2, 3), (3, 2), (2, 2)):
    sx, sy = ctr(xb, TOP, r, c)
    dx, dy = tx - sx, ty - sy
    S.line(sx + dx * 0.25, sy + dy * 0.25, tx - dx * 0.38, ty - dy * 0.38, width=1.4, color="var(--hi)", arrow=True)
# order: rows top to bottom (outer), each row left to right (inner)
dbl_arrow(xb + G * cs + 14, BOT + 4, xb + G * cs + 14, BOT + G * cs - 4)
for r in (1, 2, 3, 4, 5):
    y = BOT + r * cs + cs / 2
    thin_arrow(xb + 4, y, xb + G * cs - 4, y)

# --- panel C: OptCost, rows i = 1..6, columns k = 0..5; used where k >= i - 1, base cases k = i - 1
xc = cols[2]
usedC = lambda r, c: c >= r
baseC = {(r, r) for r in range(G)}
for y0 in (TOP, BOT):
    grid(xc, y0, usedC, baseC)
    axes(xc, y0, "i", "k")
# target (i=2, k=4) -> r = 1, c = 4; deps: row 1 columns 1..3 (k = r-1 for r = 2..4) and column 4 rows 2..4
cell(xc, TOP, 1, 4, "target")
for c in (1, 2, 3):
    cell(xc, TOP, 1, c, "dep")
for r in (2, 3, 4):
    cell(xc, TOP, r, 4, "dep")
tx, ty = ctr(xc, TOP, 1, 4)
sx, sy = ctr(xc, TOP, 1, 1)
S.line(sx - 3, sy, tx - 7, ty, width=1.4, color="var(--hi)", arrow=True)
sx, sy = ctr(xc, TOP, 4, 4)
S.line(sx, sy + 3, tx, ty + 7, width=1.4, color="var(--hi)", arrow=True)
# order: diagonals d = k - i = 0, 1, 2, ... (outer), inner any order
for d in (1, 2, 3, 4):
    r1, c1 = 0, d
    r2, c2 = G - 1 - d, G - 1
    x1, y1 = xc + c1 * cs + 3, BOT + r1 * cs + 3
    x2, y2 = xc + (c2 + 1) * cs - 3, BOT + (r2 + 1) * cs - 3
    thin_arrow(x2, y2, x1, y1, both=True)
dbl_arrow(xc + 2 * cs, BOT + 3 * cs + 4, xc + 3 * cs + 10, BOT + 2 * cs - 6)
notes = [("column j + 1;", "columns right to left"), ("three neighbors;", "rows top down, left to right"),
         ("left in row, below in column;", "diagonals, shortest first")]
for x, (a, b) in zip(cols, notes):
    S.text(x + G * cs / 2, BOT + G * cs + 38, a, size=12, color="var(--muted)")
    S.text(x + G * cs / 2, BOT + G * cs + 54, b, size=12, color="var(--muted)")
save("a03-dependencies", S.figure(
    "<strong>Dependencies and evaluation orders.</strong> Top: the entry being computed (red) and the entries it "
    "reads (blue); gray cells are base cases, blank cells are never used. Bottom: a valid evaluation order — the "
    "thick arrow is the outer loop, thin arrows the inner loop. <i>LISbigger</i> (§3.6) only needs column "
    "<i>j</i> + 1, so any order within a column works; <i>Edit</i> (§3.7) can go row by row; <i>OptCost</i> (§3.9) "
    "reads whole partial rows and columns, so it goes by diagonals (rows bottom-up or columns left-to-right also work).",
    alt="three small tables showing which entries each dynamic program reads, and the order in which to fill them"))

# =========================================================================== 3. edit-distance table
A, B = "ALGORITHM", "ALTRUISTIC"
m, n = len(A), len(B)
E = [[0] * (n + 1) for _ in range(m + 1)]
for j in range(n + 1):
    E[0][j] = j
for i in range(1, m + 1):
    E[i][0] = i
    for j in range(1, n + 1):
        E[i][j] = min(E[i][j - 1] + 1, E[i - 1][j] + 1, E[i - 1][j - 1] + (A[i - 1] != B[j - 1]))

# moves on optimal paths from (0,0) to (m,n): edge (p -> q) is "defining" and q lies on a path to (m,n)
def preds(i, j):
    out = []
    if i > 0 and j > 0 and E[i][j] == E[i - 1][j - 1] + (A[i - 1] != B[j - 1]):
        out.append((i - 1, j - 1))
    if j > 0 and E[i][j] == E[i][j - 1] + 1:
        out.append((i, j - 1))
    if i > 0 and E[i][j] == E[i - 1][j] + 1:
        out.append((i - 1, j))
    return out


on_path, path_edges, stack = {(m, n)}, set(), [(m, n)]
while stack:
    q = stack.pop()
    for p in preds(*q):
        path_edges.add((p, q))
        if p not in on_path:
            on_path.add(p)
            stack.append(p)
assert (0, 0) in on_path

cw, ch = 38, 30
X0, Y0 = 66, 56
S = SVG(X0 + (n + 1) * cw + 20, Y0 + (m + 1) * ch + 18)
for (i, j) in on_path:
    S.rect(X0 + j * cw + 2, Y0 + i * ch + 2, cw - 4, ch - 4, rx=4, stroke="none", fill="var(--accent)", fill_opacity=0.16, width=0)
S.rect(X0, Y0, (n + 1) * cw, (m + 1) * ch, stroke="currentColor", fill="none", width=1.0)
for j in range(1, n + 1):
    S.text(X0 + j * cw + cw / 2, Y0 - 12, B[j - 1], size=14, font=MONO)
for i in range(1, m + 1):
    S.text(X0 - 14, Y0 + i * ch + ch / 2, A[i - 1], size=14, font=MONO)
S.text(X0 + (n + 1) * cw / 2, Y0 - 36, "B = ALTRUISTIC, column j →", size=12, color="var(--muted)")
S.text(14, Y0 + (m + 1) * ch / 2, "A = ALGORITHM, row i ↓", size=12, color="var(--muted)", raw=False)
# rotate the row label: emulate by a separate rotated text element
S.items[-1] = (f'<text x="16" y="{Y0 + (m + 1) * ch / 2}" text-anchor="middle" dominant-baseline="central" '
               f'fill="var(--muted)" transform="rotate(90 16 {Y0 + (m + 1) * ch / 2})" '
               f'style="font-size:12px;font-family:{SANS};">A = ALGORITHM, row i →</text>')
for (p, q) in sorted(path_edges):
    (i1, j1), (i2, j2) = p, q
    x1, y1 = X0 + j1 * cw + cw / 2, Y0 + i1 * ch + ch / 2
    x2, y2 = X0 + j2 * cw + cw / 2, Y0 + i2 * ch + ch / 2
    free = (i2 == i1 + 1 and j2 == j1 + 1 and A[i2 - 1] == B[j2 - 1])
    dx, dy = x2 - x1, y2 - y1
    if dy == 0:
        s, e = 10, 10
        S.line(x1 + s, y1, x2 - e, y2, width=1.5, color="var(--accent)", arrow=True)
    elif dx == 0:
        S.line(x1, y1 + 8, x2, y2 - 9, width=1.5, color="var(--accent)", arrow=True)
    else:
        S.line(x1 + 8, y1 + 6, x2 - 9, y2 - 7, width=1.7 if free else 1.5,
               color="var(--hi)" if free else "var(--accent)", arrow=True)
for i in range(m + 1):
    for j in range(n + 1):
        match = i > 0 and j > 0 and A[i - 1] == B[j - 1]
        S.text(X0 + j * cw + cw / 2, Y0 + i * ch + ch / 2 + 1, str(E[i][j]), size=14,
               weight=700 if match else None, color="var(--hi)" if match else "currentColor",
               font=SANS)
save("a03-edit-table", S.figure(
    "<strong>The memoization table for ALGORITHM and ALTRUISTIC.</strong> Entry (<i>i</i>, <i>j</i>) is "
    "<i>Edit</i>(<i>i</i>, <i>j</i>); bold red numbers mark equal letters <i>A</i>[<i>i</i>] = <i>B</i>[<i>j</i>]. "
    "The shaded cells and arrows are every optimal path from the top left to the bottom right: a horizontal arrow is "
    "an insertion, a vertical arrow a deletion, a diagonal arrow a substitution (red when free). Exactly three paths, "
    "so exactly three optimal alignments, each with six edits. (The book prints the same table transposed.)",
    alt="edit distance table for ALGORITHM and ALTRUISTIC with the optimal paths highlighted"))

# =========================================================================== 4. independent set in a tree
TREE = {"r": None, "a": "r", "b": "r", "c": "r", "d": "a", "e": "a", "f": "d", "g": "d", "h": "d", "i": "e", "j": "e"}
kids = {v: [w for w, p in TREE.items() if p == v] for v in TREE}
yes, no = {}, {}


def post(v):
    yes[v], no[v] = 1, 0
    for w in kids[v]:
        post(w)
        no[v] += max(yes[w], no[w])
        yes[v] += no[w]


post("r")
chosen = set()


def pick(v, allowed):
    take = allowed and yes[v] > no[v]
    if take:
        chosen.add(v)
    for w in kids[v]:
        pick(w, not take)


pick("r", True)
assert len(chosen) == max(yes["r"], no["r"]) == 8
P = {"r": (300, 34), "a": (190, 104), "b": (390, 104), "c": (480, 104), "d": (120, 174), "e": (290, 174),
     "f": (50, 244), "g": (120, 244), "h": (190, 244), "i": (255, 244), "j": (325, 244)}
S = SVG(560, 290)
for v, p in TREE.items():
    if p:
        (x1, y1), (x2, y2) = P[p], P[v]
        S.line(x1, y1 + 13, x2, y2 - 13, width=1.3, opacity=0.7)
for v in TREE:
    x, y = P[v]
    if v in chosen:
        S.rect(x - 24, y - 13, 48, 26, rx=13, stroke="var(--accent)", fill="var(--accent)", fill_opacity=0.25, width=1.8)
    else:
        S.rect(x - 24, y - 13, 48, 26, rx=13, stroke="currentColor", fill="var(--paper)", width=1.3)
    S.text(x, y + 1, f"{yes[v]} / {no[v]}", size=14, font=SANS)
S.text(560 - 8, 276, "label: MISyes / MISno", size=12, anchor="end", color="var(--muted)")
S.text(8, 276, "shaded: a largest independent set (8 vertices)", size=12, anchor="start", color="var(--muted)")
save("a03-tree-mis", S.figure(
    "<strong>Independent sets in a tree, bottom up.</strong> Each vertex shows <i>MISyes</i>(<i>v</i>) / "
    "<i>MISno</i>(<i>v</i>), computed in post-order: a leaf is 1 / 0; <i>MISyes</i> adds the children's "
    "<i>MISno</i> to 1, <i>MISno</i> adds the larger value of each child. At the root max{6, 8} = 8. Walking down "
    "from the root — exclude it (8 &gt; 6), take the left child (6 &gt; 5), and so on — recovers a largest "
    "independent set, shaded; it contains an internal vertex, not just leaves.",
    alt="tree with two numbers at each vertex and a maximum independent set shaded"))
