#!/usr/bin/env python3
"""Figures for lecture note C (dynamic programming for formal languages and automata).
Writes tools/figs/nc-*.html; then run tools/assemble.py on the page. Numbers are recomputed here and checked
again in tools/checks/nc.py."""
import os
from figlib import Automaton, SVG, MONO, SERIF_IT, SANS

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")
os.makedirs(OUT, exist_ok=True)


def save(name, html):
    with open(os.path.join(OUT, name + ".html"), "w", encoding="utf-8") as f:
        f.write(html + "\n")
    print("wrote", name)


# =========================================================================== 1. NFA and its Accepts? table
Q = ["s", "a", "b", "c"]
DL = {("s", "0"): {"s", "a"}, ("s", "1"): {"s", "b"}, ("a", "0"): {"c"}, ("a", "1"): set(),
      ("b", "0"): set(), ("b", "1"): {"c"}, ("c", "0"): {"c"}, ("c", "1"): {"c"}}
ACC = {"c"}
w = "0110"
n = len(w)
T = {(q, n + 1): q in ACC for q in Q}
for i in range(n, 0, -1):
    for q in Q:
        T[(q, i)] = any(T[(r, i + 1)] for r in DL[(q, w[i - 1])])
assert T[("s", 1)]

A = Automaton(640, 230, r=17)
A.state("s", 60, 115, start="left")
A.state("a", 170, 52)
A.state("b", 170, 178)
A.state("c", 280, 115, accepting=True)
A.loop("s", "0,1", "above", size=0.8)
A.loop("c", "0,1", "above", size=0.8)
A.edge("s", "a", "0")
A.edge("s", "b", "1", label_side=-1)
A.edge("a", "c", "0")
A.edge("b", "c", "1", label_side=-1)
# table on the right
X0, Y0, cw, ch = 390, 52, 44, 32
A.text(X0 + 2.5 * cw + cw / 2 - 22, 18, "Accepts?[q, i] for w = 0110", size=13, color="var(--muted)")
for i in range(1, n + 2):
    x = X0 + (i - 1) * cw + cw / 2
    A.text(x, Y0 - 16, str(i), size=13, font=SANS, color="var(--muted)")
    if i <= n:
        A.text(x, Y0 + 4 * ch + 16, w[i - 1], size=14, font=MONO)
A.text(X0 - 14, Y0 + 4 * ch + 16, "w[i]", size=12, anchor="end", color="var(--muted)")
A.text(X0 - 14, Y0 - 16, "i", size=13, anchor="end", font=SERIF_IT, italic=True, color="var(--muted)")
for r, q in enumerate(Q):
    y = Y0 + r * ch + ch / 2
    A.text(X0 - 14, y, q, size=15, anchor="end", font=SERIF_IT, italic=True)
    for i in range(1, n + 2):
        x = X0 + (i - 1) * cw
        val = T[(q, i)]
        hi = (q == "s" and i == 1)
        A.rect(x + 2, Y0 + r * ch + 2, cw - 4, ch - 4, rx=4, stroke="none",
               fill="var(--accent)" if val else "none", fill_opacity=0.18 if val else None, width=0)
        A.text(x + cw / 2, y + 1, "T" if val else "F", size=14, font=SANS, weight=700 if hi else None,
               color="var(--hi)" if hi else ("currentColor" if val else "var(--muted)"))
A.rect(X0, Y0, (n + 1) * cw, 4 * ch, stroke="currentColor", fill="none", width=1.0)
A.line(X0 + n * cw, Y0, X0 + n * cw, Y0 + 4 * ch, width=1.0, dash="3 3")
A.text(X0 + (n + 1) * cw / 2, Y0 + 4 * ch + 40, "filled right to left: column i reads column i + 1", size=12,
       color="var(--muted)")
save("nc-nfa-table", A.figure(
    "<strong>NFA acceptance as a table.</strong> Left: the NFA of Chapter 4 for the strings that contain "
    "<code>00</code> or <code>11</code>. Right: the dynamic program on <i>w</i> = <code>0110</code>. Column "
    "<i>n</i> + 1 = 5 is the base case (only the accepting state <i>c</i> accepts the empty suffix); entry "
    "(<i>q</i>, <i>i</i>) is T if some transition from <i>q</i> on <i>w</i>[<i>i</i>] leads to a state that is T "
    "in column <i>i</i> + 1. For example (<i>b</i>, 2) is T because <i>b</i> reads <code>1</code> into <i>c</i>. "
    "The answer is the entry (<i>s</i>, 1), red: <code>0110</code> is accepted.",
    alt="four-state NFA and a 4 by 5 table of T and F values for the input 0110"))

# =========================================================================== 2. CYK table for (())()
G = {"S": [(), ("A", "A"), ("L", "R"), ("L", "B")], "A": [("A", "A"), ("L", "R"), ("L", "B")],
     "B": [("A", "R")], "L": [("(",)], "R": [(")",)]}
order = ["S", "A", "B", "L", "R"]
w = "(())()"
n = len(w)
gen = {}
for i in range(1, n + 1):
    gen[(i, i)] = {X for X in G if (w[i - 1],) in G[X]}
for j in range(1, n + 1):
    for i in range(j - 1, 0, -1):
        gen[(i, j)] = {X for X in G for r in G[X] if len(r) == 2 for k in range(i, j)
                       if r[0] in gen[(i, k)] and r[1] in gen[(k + 1, j)]}
assert "S" in gen[(1, n)]
cw, ch = 74, 40
X0, Yb = 34, 300
S = SVG(2 * X0 + n * cw, Yb + 66)
hi_cells = {(1, 6), (1, 4), (5, 6)}
for ln in range(1, n + 1):
    for i in range(1, n - ln + 2):
        j = i + ln - 1
        x = X0 + (i - 1) * cw + (ln - 1) * cw / 2
        y = Yb - ln * ch
        cell = gen[(i, j)]
        hi = (i, j) in hi_cells
        S.rect(x + 2, y + 2, cw - 4, ch - 4, rx=5, stroke="var(--hi)" if hi else "currentColor",
               fill="var(--accent)" if cell else "none", fill_opacity=0.16 if cell else None,
               width=1.8 if hi else 0.9)
        label = ", ".join(X for X in order if X in cell) if cell else "–"
        S.text(x + cw / 2, y + ch / 2 + 1, label, size=15 if cell else 13, font=SERIF_IT if cell else SANS,
               italic=bool(cell), color="currentColor" if cell else "var(--muted)")
for i in range(1, n + 1):
    x = X0 + (i - 1) * cw + cw / 2
    S.text(x, Yb + 16, w[i - 1], size=17, font=MONO)
    S.text(x, Yb + 38, str(i), size=12, color="var(--muted)")
S.text(X0 + n * cw / 2, Yb - n * ch - 14, "[1 .. 6]: A A at k = 4", size=12, color="var(--hi)")
S.text(X0 + 2, Yb + 56, "a cell sits above the substring it covers; – means no nonterminal derives it", size=11,
       anchor="start", color="var(--muted)")
save("nc-cyk-table", S.figure(
    "<strong>The CYK table for <code>(())()</code>.</strong> Grammar: <i>S</i> → ε | <i>AA</i> | <i>LR</i> | "
    "<i>LB</i>, <i>A</i> → <i>AA</i> | <i>LR</i> | <i>LB</i>, <i>B</i> → <i>AR</i>, <i>L</i> → <code>(</code>, "
    "<i>R</i> → <code>)</code>. The bottom row holds the nonterminals that derive each symbol; a cell for "
    "<i>w</i>[<i>i</i> .. <i>j</i>] collects every <i>X</i> with a rule <i>X</i> → <i>YZ</i> and a split "
    "<i>i</i> ≤ <i>k</i> &lt; <i>j</i> such that <i>Y</i> is in the cell for <i>w</i>[<i>i</i> .. <i>k</i>] and "
    "<i>Z</i> in the cell for <i>w</i>[<i>k</i>+1 .. <i>j</i>]. The top cell contains <i>S</i>, so the string is "
    "balanced; the only way in is <i>A A</i> with <code>(())</code> and <code>()</code> (red).",
    alt="triangular CYK table for the string (())() with nonterminal sets in each cell"))
