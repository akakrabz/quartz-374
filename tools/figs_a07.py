#!/usr/bin/env python3
"""Figures for Algorithms Chapter 7 (minimum spanning trees). Writes tools/figs/a07-<name>.html; then run
tools/assemble.py on the chapter page. Every safe, useless and tree edge drawn here is computed by running the
page's algorithms (Borůvka with AddAllSafeEdges, Jarník, Kruskal with the labeling union-find) on the book's
example graph; every drawn edge carries data-p (panel), data-e (edge) and data-r (role) attributes, which
tools/checks/a07.py compares with its own computation."""
import math
import os

from figlib import SVG, SERIF_IT, SANS, esc, fmt

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")
os.makedirs(OUT, exist_ok=True)


def save(name, html):
    with open(os.path.join(OUT, name + ".html"), "w", encoding="utf-8") as f:
        f.write(html + "\n")
    print("wrote", name)


# =========================================================================== the book's example graph (Fig 7.1)
VS = "abcdefg"
W = {"ab": 8, "ac": 5, "bc": 10, "bd": 2, "cd": 3, "be": 18, "de": 12, "df": 30, "cf": 16, "dg": 14, "eg": 4,
     "fg": 26}
EDGES = sorted(W, key=lambda e: W[e])
UNIT = {"a": (0, -1), "b": (-0.857, -0.5), "c": (0.857, -0.5), "d": (0, 0), "e": (-0.857, 0.5),
        "f": (0.857, 0.5), "g": (0, 1)}
# side of each edge on which its weight is written (a direction hint; the label goes on that side)
HINT = {"ab": (-1, -1), "ac": (1, -1), "bc": (0, -1), "bd": (-0.25, 1), "cd": (0.25, 1), "be": (-1, 0),
        "cf": (1, 0), "de": (-0.25, -1), "df": (0.25, -1), "dg": (-1, 0), "eg": (-1, 1), "fg": (1, 1)}
assert len(W) == 12 and len(set(W.values())) == 12


def comps_of(F):
    """Components of the forest (VS, F) as a dict vertex -> frozenset (whatever-first search)."""
    adj = {v: [] for v in VS}
    for e in F:
        adj[e[0]].append(e[1])
        adj[e[1]].append(e[0])
    comp = {}
    for s in VS:
        if s in comp:
            continue
        seen, bag = set(), [s]
        while bag:
            v = bag.pop()
            if v not in seen:
                seen.add(v)
                bag.extend(adj[v])
        for v in seen:
            comp[v] = frozenset(seen)
    return comp


def classify(F):
    """safe edges with the component(s) they are safe for, useless edges, undecided edges."""
    comp = comps_of(F)
    safe_for = {}
    for C in set(comp.values()):
        out = [e for e in W if (e[0] in C) != (e[1] in C)]
        if out:
            e = min(out, key=lambda x: W[x])
            safe_for.setdefault(e, []).append(C)
    useless = [e for e in W if e not in F and comp[e[0]] == comp[e[1]]]
    undecided = [e for e in W if e not in F and e not in safe_for and e not in useless]
    return safe_for, useless, undecided


MST = {"ac", "bd", "cd", "cf", "de", "eg"}
assert sum(W[e] for e in MST) == 42


# =========================================================================== drawing helpers
class Panel:
    def __init__(self, S, pid, cx, cy, H, r=11, wsize=12, vsize=15, wdist=9):
        self.S, self.pid, self.cx, self.cy, self.H, self.r = S, pid, cx, cy, H, r
        self.wsize, self.vsize, self.wdist = wsize, vsize, wdist

    def P(self, v):
        ux, uy = UNIT[v]
        return self.cx + ux * self.H, self.cy + uy * self.H

    def seg(self, e, role, color, width, dash=None, opacity=None, t0=0.0, t1=1.0, arrow=False):
        (x1, y1), (x2, y2) = self.P(e[0]), self.P(e[1])
        L = math.hypot(x2 - x1, y2 - y1)
        ux, uy = (x2 - x1) / L, (y2 - y1) / L
        r = self.r
        sx, sy = x1 + ux * r, y1 + uy * r
        ex, ey = x2 - ux * r, y2 - uy * r
        ax, ay = sx + (ex - sx) * t0, sy + (ey - sy) * t0
        bx, by = sx + (ex - sx) * t1, sy + (ey - sy) * t1
        extra = ""
        if dash:
            extra += f' stroke-dasharray="{dash}"'
        if opacity is not None:
            extra += f' opacity="{opacity}"'
        if arrow:
            extra += ' marker-end="url(#ARR)"'
        self.S.add(f'<line data-p="{self.pid}" data-e="{e}" data-r="{role}" x1="{fmt(ax)}" y1="{fmt(ay)}" '
                   f'x2="{fmt(bx)}" y2="{fmt(by)}" stroke="{color}" stroke-width="{width}" '
                   f'stroke-linecap="round"{extra}/>')

    def edge(self, e, role, arrows_from=(), label=True):
        style = {
            "plain": ("currentColor", 1.3, None, 0.85),
            "undecided": ("currentColor", 1.3, None, 0.85),
            "tree": ("var(--accent)", 3.6, None, None),
            "new": ("var(--hi)", 3.6, None, None),
            "safe": ("var(--hi)", 2.2, None, None),
            "useless": ("var(--muted)", 1.4, "4 3", None),
            "removed": ("var(--muted)", 1.4, "4 3", None),
            "e": ("var(--hi)", 2.6, "6 4", None),
            "e1": ("var(--hi)", 3.6, None, None),
        }[role]
        color, width, dash, op = style
        if arrows_from:
            # one arrowhead at the midpoint for each component the edge is safe for
            # arrowheads well away from the midpoint, where the weight is written
            t1 = 0.42 if len(arrows_from) == 1 else 0.36
            for v in arrows_from:
                self.seg(e if v == e[0] else e[::-1], role, color, width, t0=0.0, t1=t1, arrow=True)
            f = e if arrows_from[0] == e[0] else e[::-1]
            self.seg(f, role, color, width, t0=t1 - 0.02, t1=1.0 if len(arrows_from) == 1 else 1 - t1 + 0.02)
        else:
            self.seg(e, role, color, width, dash=dash, opacity=op)
        if label:
            self.weight(e, emph=role in ("tree", "new", "safe", "e", "e1"))

    def weight(self, e, emph=False):
        (x1, y1), (x2, y2) = self.P(e[0]), self.P(e[1])
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        L = math.hypot(x2 - x1, y2 - y1)
        nx, ny = -(y2 - y1) / L, (x2 - x1) / L
        hx, hy = HINT[e]
        if nx * hx + ny * hy < 0:
            nx, ny = -nx, -ny
        d = self.wdist + (2 if len(str(W[e])) > 1 else 0)
        self.S.text(mx + nx * d, my + ny * d, str(W[e]), size=self.wsize, halo=True,
                    weight="600" if emph else None)

    def vertex(self, v, filled=False, ring=False):
        x, y = self.P(v)
        if ring:
            self.S.circle(x, y, self.r + 3.5, stroke="currentColor", fill="var(--paper)", width=1.2)
        self.S.circle(x, y, self.r, stroke="currentColor", fill="var(--paper)", width=1.5)
        if filled:
            self.S.circle(x, y, self.r, stroke="currentColor", fill="var(--accent)", width=1.5, fill_opacity=0.28)
        self.S.text(x, y + 1, v, size=self.vsize, font=SERIF_IT, italic=True)

    def vertices(self, filled=(), ring=()):
        for v in VS:
            self.vertex(v, filled=v in filled, ring=v in ring)


def legend(S, x, y, items, gap=24):
    """items: (role, text); draws a short sample line and the text, left to right."""
    sty = {"tree": ("var(--accent)", 3.6, None), "safe": ("var(--hi)", 2.2, None), "new": ("var(--hi)", 3.6, None),
           "useless": ("var(--muted)", 1.4, "4 3"), "undecided": ("currentColor", 1.3, None),
           "e": ("var(--hi)", 2.6, "6 4")}
    for role, text in items:
        c, w, d = sty[role]
        S.line(x, y, x + 26, y, color=c, width=w, dash=d, arrow=role == "safe")
        S.text(x + 32, y, text, size=12.5, anchor="start")
        x += 32 + 6.4 * len(text) + gap
    return x


def figure(S, caption, alt):
    return S.figure(caption, alt=alt)


# =========================================================================== 1. the example and a partial forest
F1 = {"bd", "cd", "cf", "eg"}
safe1, useless1, undecided1 = classify(F1)
assert {e: sorted("".join(sorted(C)) for C in Cs) for e, Cs in safe1.items()} == \
    {"ac": ["a", "bcdf"], "de": ["eg"]}
assert sorted(useless1) == ["bc", "df"] and sorted(undecided1) == ["ab", "be", "dg", "fg"]
assert F1 <= MST
S = SVG(640, 300)
L = Panel(S, 1, 160, 148, 102, r=12, wsize=12.5)
R = Panel(S, 2, 480, 148, 102, r=12, wsize=12.5)
S.text(160, 16, "G and its minimum spanning tree", size=13.5)
S.text(480, 16, "a forest F inside the MST", size=13.5)
for e in W:
    L.edge(e, "tree" if e in MST else "plain")
L.vertices()
for e in W:
    if e in F1:
        R.edge(e, "tree")
    elif e in safe1:
        # arrows point along the edge, away from each component it is safe for
        froms = []
        for C in safe1[e]:
            froms.append(e[0] if e[0] in C else e[1])
        R.edge(e, "safe", arrows_from=froms)
    elif e in useless1:
        R.edge(e, "useless")
    else:
        R.edge(e, "undecided")
R.vertices()
legend(S, 120, 282, [("tree", "MST / F"), ("safe", "safe"), ("useless", "useless"), ("undecided", "undecided")])
save("a07-example", figure(
    S,
    "<strong>The book's example graph and the three kinds of edges.</strong> Left: the 7 vertices and 12 edges "
    "of the book's Figure 7.1 (vertex names added) and its minimum spanning tree, of weight 2 + 3 + 4 + 5 + 12 + "
    "16 = 42. Right: an intermediate forest <i>F</i> = {<i>bd</i>, <i>cd</i>, <i>cf</i>, <i>eg</i>} with "
    "components {<i>a</i>}, {<i>b</i>, <i>c</i>, <i>d</i>, <i>f</i>} and {<i>e</i>, <i>g</i>}. Each arrow "
    "leaves a component along its safe edge: <i>ac</i> (5) is safe for both {<i>a</i>} and {<i>b</i>, "
    "<i>c</i>, <i>d</i>, <i>f</i>}, <i>de</i> (12) for {<i>e</i>, <i>g</i>}. The dashed edges <i>bc</i> and "
    "<i>df</i> are useless; the other four are undecided.",
    alt="a seven-vertex weighted graph with its minimum spanning tree, and a partial forest with safe, useless "
        "and undecided edges"))

# =========================================================================== 2. the cut exchange (Lemma 7.2)
T = {"ab", "ac", "cf", "fg", "eg", "bd"}
SC = set("abcd")
crossing = [e for e in W if (e[0] in SC) != (e[1] in SC)]
e_ = min(crossing, key=lambda x: W[x])
assert sorted(crossing) == ["be", "cf", "de", "df", "dg"] and e_ == "de"


def tree_path(Tset, s, t):
    adj = {v: [] for v in VS}
    for x in Tset:
        adj[x[0]].append(x[1])
        adj[x[1]].append(x[0])
    par, bag = {s: None}, [s]
    while bag:
        v = bag.pop()
        for u in adj[v]:
            if u not in par:
                par[u] = v
                bag.append(u)
    path = [t]
    while path[-1] != s:
        path.append(par[path[-1]])
    return path[::-1]


assert len(comps_of(T)["a"]) == 7 and len(T) == 6
path = tree_path(T, "d", "e")
pedges = ["".join(sorted(p)) for p in zip(path, path[1:])]
cross_on_path = [x for x in pedges if (x[0] in SC) != (x[1] in SC)]
assert "".join(path) == "dbacfge" and cross_on_path == ["cf"]
e1 = cross_on_path[0]
T2 = (T - {e1}) | {e_}
wT, wT2 = sum(W[x] for x in T), sum(W[x] for x in T2)
assert (wT, wT2) == (61, 57) and T2 != MST


def blob(S, pts, pad=19):
    """A rounded hull around the points: a wide round-joined stroke under group opacity."""
    d = "M" + " L".join(f"{fmt(x)},{fmt(y)}" for x, y in pts) + " Z"
    S.add(f'<g opacity="0.13"><path d="{d}" fill="var(--accent)" stroke="var(--accent)" '
          f'stroke-width="{2 * pad}" stroke-linejoin="round"/></g>')


S = SVG(640, 300)
L = Panel(S, 1, 160, 150, 102, r=12, wsize=12.5)
R = Panel(S, 2, 480, 150, 102, r=12, wsize=12.5)
for P_ in (L, R):
    blob(S, [P_.P(v) for v in "acdb"])
    S.text(P_.cx - 78, P_.cy - 88, "S", size=17, font=SERIF_IT, italic=True, color="var(--accent)")
S.text(160, 16, f"T, weight {wT}", size=13.5)
S.text(480, 16, f"T′ = T − e′ + e, weight {wT2}", size=13.5)
for e in W:
    if e == e_:
        L.edge(e, "e")
    elif e == e1:
        L.edge(e, "e1")
    elif e in T:
        L.edge(e, "tree")
    else:
        L.edge(e, "plain", label=True)
L.vertices(filled=SC)
for e in W:
    if e in T2:
        R.edge(e, "tree")
    elif e == e1:
        R.edge(e, "removed")
    else:
        R.edge(e, "plain")
R.vertices(filled=SC)
# names of e and e'
for P_, lab_e, lab_e1 in ((L, True, True), (R, True, True)):
    x1, y1 = P_.P("d")
    x2, y2 = P_.P("e")
    S.text((x1 + x2) / 2 + 9, (y1 + y2) / 2 + 13, "e", size=15, font=SERIF_IT, italic=True, color="var(--hi)",
           halo=True)
    x1, y1 = P_.P("c")
    x2, y2 = P_.P("f")
    S.text(x1 - 13, (y1 + y2) / 2 + 2, "e′", size=15, font=SERIF_IT, italic=True, color="var(--hi)", halo=True)
legend(S, 150, 284, [("tree", "spanning tree"), ("e", "e, not in T"), ("useless", "e′ removed")])
save("a07-cut-exchange", figure(
    S,
    f"<strong>The exchange behind Lemma 7.2.</strong> Left: a spanning tree <i>T</i> of weight {wT} and the "
    "vertex set <i>S</i> = {<i>a</i>, <i>b</i>, <i>c</i>, <i>d</i>} (shaded). Five edges have exactly one "
    "endpoint in <i>S</i> — <i>de</i> (12), <i>dg</i> (14), <i>cf</i> (16), <i>be</i> (18), <i>df</i> (30) — "
    "and the lightest, <i>e</i> = <i>de</i>, is not in <i>T</i>. The path from <i>d</i> to <i>e</i> in <i>T</i>, "
    "<i>d</i>–<i>b</i>–<i>a</i>–<i>c</i>–<i>f</i>–<i>g</i>–<i>e</i>, leaves <i>S</i> along <i>e</i>′ = "
    f"<i>cf</i> (16). Right: swapping <i>e</i>′ for <i>e</i> gives a spanning tree lighter by 16 − 12 = 4, "
    f"of weight {wT2}. Two more exchanges of the same kind, <i>cd</i> for <i>ab</i> and <i>cf</i> for "
    "<i>fg</i>, reach the minimum spanning tree, of weight 42.",
    alt="a spanning tree with a shaded vertex set, the lightest crossing edge dashed, and the tree after the exchange"))


# =========================================================================== 3. Borůvka
def boruvka_phases():
    F = set()
    phases = []
    while True:
        comp = comps_of(F)
        if len(set(comp.values())) == 1:
            break
        safe_for, useless, _ = classify(F)
        phases.append((set(F), {e: list(Cs) for e, Cs in safe_for.items()}, set(useless)))
        F |= set(safe_for)
    return phases, F


PH, FB = boruvka_phases()
assert len(PH) == 2 and FB == MST
assert sorted(PH[0][1]) == ["ac", "bd", "cd", "cf", "eg"] and sorted(PH[1][1]) == ["de"]
assert sorted(PH[1][2]) == ["ab", "bc", "df"]
S = SVG(660, 252)
xs = [110, 330, 550]
titles = ["phase 1: 7 components", "phase 2: 2 components", "done: the MST"]
for k in range(3):
    P_ = Panel(S, k + 1, xs[k], 128, 78, r=10, wsize=11.5, vsize=13.5, wdist=8)
    S.text(xs[k], 16, titles[k], size=13.5)
    if k < 2:
        Fk, safe_for, useless = PH[k]
    else:
        Fk, safe_for, useless = FB, {}, {e for e in W if e not in FB}
    for e in W:
        if e in Fk:
            P_.edge(e, "tree")
        elif e in safe_for:
            froms = [e[0] if e[0] in C else e[1] for C in safe_for[e]]
            P_.edge(e, "safe", arrows_from=froms)
        elif e in useless:
            P_.edge(e, "useless")
        else:
            P_.edge(e, "undecided")
    P_.vertices()
for x in (220, 440):
    S.line(x - 14, 128, x + 14, 128, color="var(--muted)", width=2.2, arrow=True)
legend(S, 170, 236, [("tree", "F"), ("safe", "safe"), ("useless", "useless")])
save("a07-boruvka", figure(
    S,
    "<strong>Borůvka's algorithm on the example.</strong> Phase 1: each of the 7 one-vertex components picks "
    "its lightest edge (arrows); <i>bd</i> and <i>eg</i> are picked from both ends, so 5 distinct safe edges "
    "are added. Phase 2: the two remaining components, {<i>a</i>, <i>b</i>, <i>c</i>, <i>d</i>, <i>f</i>} and "
    "{<i>e</i>, <i>g</i>}, both pick <i>de</i> (12); <i>ab</i>, <i>bc</i> and <i>df</i> have become useless. "
    "After two phases <i>F</i> is the minimum spanning tree (the book's Figure 7.3).",
    alt="three snapshots of Boruvka's algorithm: all vertices pick their lightest edge, two components pick the "
        "same edge, the final tree"))


# =========================================================================== 4. Jarník from g
def jarnik_steps(s):
    Tv, Te = {s}, set()
    steps = []
    while len(Tv) < len(VS):
        out = [e for e in W if (e[0] in Tv) != (e[1] in Tv)]
        e = min(out, key=lambda x: W[x])
        useless = {x for x in W if x not in Te and x[0] in Tv and x[1] in Tv}
        frm = e[0] if e[0] in Tv else e[1]
        steps.append((set(Tv), set(Te), e, frm, useless))
        Tv.add(e[1] if frm == e[0] else e[0])
        Te.add(e)
    return steps, Te


JS, JT = jarnik_steps("g")
assert [st[2] for st in JS] == ["eg", "de", "bd", "cd", "ac", "cf"] and JT == MST
S = SVG(660, 436)
for k, (Tv, Te, e, frm, useless) in enumerate(JS):
    col, row = k % 3, k // 3
    cx, cy = 110 + 220 * col, 112 + 208 * row
    P_ = Panel(S, k + 1, cx, cy, 70, r=10, wsize=11.5, vsize=13.5, wdist=8)
    S.text(cx, cy - 92, f"step {k + 1}: add {e} ({W[e]})", size=13.5)
    for x in W:
        if x in Te:
            P_.edge(x, "tree")
        elif x == e:
            P_.edge(x, "safe", arrows_from=[frm])
        elif x in useless:
            P_.edge(x, "useless")
        else:
            P_.edge(x, "undecided")
    P_.vertices(filled=Tv, ring={"g"})
legend(S, 160, 422, [("tree", "T"), ("safe", "T's safe edge"), ("useless", "useless")])
save("a07-jarnik", figure(
    S,
    "<strong>Jarník's algorithm on the example, from <i>g</i>.</strong> The tree <i>T</i> (shaded vertices) "
    "grows from the start vertex <i>g</i> (double circle) by one vertex per step, always along the lightest edge "
    "with exactly one endpoint in <i>T</i> (arrow). The edges are added in the order <i>eg</i>, <i>de</i>, "
    "<i>bd</i>, <i>cd</i>, <i>ac</i>, <i>cf</i> — not in order of weight. Edges with both endpoints in <i>T</i> "
    "become useless (dashed); after step 6, <i>df</i> and <i>fg</i> join them (the book's Figure 7.4).",
    alt="six snapshots of Jarnik's algorithm growing one tree from the bottom vertex"))


# =========================================================================== 5. Kruskal with the labeling union-find
def kruskal_trace():
    label = {v: v for v in VS}
    members = {v: [v] for v in VS}
    F, rows = set(), []
    for e in EDGES:
        u, v = e[0], e[1]
        x, y = label[u], label[v]
        if x != y:
            if len(members[x]) < len(members[y]):
                x, y = y, x
            moved = list(members[y])
            for z in moved:
                label[z] = x
            members[x] += members.pop(y)
            F.add(e)
            rows.append((e, "add", sorted(moved), {k: sorted(m) for k, m in members.items()}))
        else:
            rows.append((e, "skip", [], None))
    return rows, F


KR, KF = kruskal_trace()
assert KF == MST
unions = [i for i, r in enumerate(KR) if r[1] == "add"]
assert [KR[i][0] for i in unions] == ["bd", "cd", "eg", "ac", "de", "cf"]
S = SVG(660, 480)
skipped_before = []
prev = -1
for k, i in enumerate(unions):
    e, _, moved, sets = KR[i]
    skipped = [KR[j][0] for j in range(prev + 1, i) if KR[j][1] == "skip"]
    prev = i
    col, row = k % 3, k // 3
    cx, cy = 110 + 220 * col, 124 + 230 * row
    P_ = Panel(S, k + 1, cx, cy, 66, r=10, wsize=11.5, vsize=13.5, wdist=8)
    S.text(cx, cy - 106, f"union {k + 1}: {e} ({W[e]})", size=13.5)
    Fk = {KR[j][0] for j in unions[:k]}
    skipped_before += skipped
    for x in W:
        if x in Fk:
            P_.edge(x, "tree")
        elif x == e:
            P_.edge(x, "new")
        elif x in skipped_before:
            P_.edge(x, "useless")
        else:
            P_.edge(x, "undecided")
    P_.vertices()
    if skipped:
        S.text(cx, cy - 89, "skipped: " + ", ".join(f"{x} ({W[x]})" for x in skipped), size=11.5,
               color="var(--muted)")
    # the partition after the union; the label of each set (its Find value) first, in bold
    parts = sorted(sets.items(), key=lambda kv: (-len(kv[1]), kv[0]))
    txt = "  ".join("{" + "<tspan font-weight=\"700\">" + esc(lab) + "</tspan>" +
                    "".join(" " + esc(m) for m in mem if m != lab) + "}" for lab, mem in parts)
    S.text(cx, cy + 88, txt, size=13, font=SERIF_IT, italic=True, raw=True)
legend(S, 120, 466, [("tree", "F"), ("new", "added edge"), ("useless", "skipped (useless)")])
save("a07-kruskal", figure(
    S,
    "<strong>Kruskal's algorithm on the example.</strong> The 12 edges are scanned by increasing weight; the six "
    "that join two different sets are added (thick), and the six whose endpoints already have the same label "
    "are skipped (dashed) — <i>ab</i>, <i>bc</i>, <i>dg</i>, and after the last union <i>be</i>, <i>fg</i>, "
    "<i>df</i>. Under each panel: the union-find sets after the union, each led by its label in bold (the "
    "value of Find); in each union the smaller set takes the label of the larger (the book's Figure 7.6).",
    alt="six snapshots of Kruskal's algorithm with the union-find sets after each union"))
