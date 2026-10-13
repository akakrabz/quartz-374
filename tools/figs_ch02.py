#!/usr/bin/env python3
"""Figures for Chapter 2 (regular languages). Writes tools/figs/<name>.html; then run tools/assemble.py."""
import os
from figlib import SVG, Tree, Tape, MONO, SERIF_IT, SANS

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")
os.makedirs(OUT, exist_ok=True)


def save(name, html):
    with open(os.path.join(OUT, name + ".html"), "w", encoding="utf-8") as f:
        f.write(html + "\n")
    print("wrote", name)


# ---------------------------------------------------------------- expression tree of 0+1(0+1)*00 (size 10)
# The same tree is rebuilt and checked in tools/checks/ch02.py (TREE there).
SUB = ("•", [("*", [("+", [("0", []), ("1", [])])]), ("00", [])])      # the subexpression (0+1)*00
ROOT = ("+", [("0", []), ("•", [("1", []), SUB])])


def ids(n):
    out = {id(n)}
    for k in n[1]:
        out |= ids(k)
    return out


T = Tree(520, 300, font_size=15)
T.text(260, 20, "R = 0+1(0+1)*00", size=15, font=MONO)
pos = T.draw(ROOT, 120, 58, level_h=38, leaf_w=58, circle_internal=True, hi=ids(SUB))
sx, sy = pos[id(SUB)]
T.text(sx + 22, sy - 2, "subexpression (0+1)*00", size=13, anchor="start", color="var(--hi)")
rx, ry = pos[id(ROOT)]
T.text(rx - 22, ry, "root", size=12, anchor="end", color="var(--muted)")
T.text(260, 288, "size 10: five internal nodes (+, •, •, *, +) and five leaves (0, 1, 0, 1, 00)",
       size=12, color="var(--muted)")
save("ch02-expression-tree", T.figure(
    "<strong>The expression tree of 0+1(0+1)*00.</strong> Star binds tightest and + loosest, so the root is the + "
    "and the string 00 is a single leaf. Every subtree is a <em>subexpression</em>; the red one is (0+1)*00. The "
    "substring 0+1(0+1)* is a well-formed expression too, but no subtree spells it, so it is not a subexpression.",
    alt="expression tree with root plus, children 0 and a concatenation of 1 with the concatenation of a star "
        "of 0 plus 1 and the leaf 00"))

# ---------------------------------------------------------------- the five cases of structural induction
S = SVG(640, 178)
cols = [60, 170, 300, 440, 572]
y0 = 46


def node(x, y, lab, r=13, font=MONO):
    S.circle(x, y, r, width=1.3)
    S.text(x, y + 0.5, lab, size=15, font=font, italic=(font == SERIF_IT))


def leaf(x, y, lab, italic=False):
    S.text(x, y, lab, size=17 if italic else 16, font=SERIF_IT if italic else MONO, italic=italic, halo=True)


def subtree(x, y, lab):
    """a triangle hanging from (x, y) labelled with a subexpression name, coloured as 'the hypothesis applies'"""
    w, h = 42, 46
    S.add(f'<path d="M{x},{y} L{x - w / 2},{y + h} L{x + w / 2},{y + h} Z" fill="var(--accent)" fill-opacity="0.12" '
          f'stroke="var(--accent)" stroke-width="1.5" stroke-linejoin="round"/>')
    S.text(x, y + h * 0.64, lab, size=16, font=SERIF_IT, italic=True, color="var(--accent)")


def edge(x1, y1, x2, y2):
    S.line(x1, y1, x2, y2, width=1.2, opacity=0.55)


# ∅ and a string: leaves (base cases)
leaf(cols[0], y0 + 2, "∅", italic=True)
leaf(cols[1], y0 + 2, "w", italic=True)
S.text(cols[1], y0 + 24, "(a string, maybe ε)", size=11, color="var(--muted)")
# S + T and S • T
for x, op in ((cols[2], "+"), (cols[3], "•")):
    node(x, y0, op)
    for dx, lab in ((-30, "S"), (30, "T")):
        edge(x + dx * 0.33, y0 + 10, x + dx, y0 + 38)
        subtree(x + dx, y0 + 38, lab)
# S*
node(cols[4], y0, "*")
edge(cols[4], y0 + 13, cols[4], y0 + 38)
subtree(cols[4], y0 + 38, "S")
labels = ["R = ∅", "R = w", "R = S + T", "R = S • T", "R = S*"]
for x, lab in zip(cols, labels):
    S.text(x, 162, lab, size=14, font=SERIF_IT, italic=True)
S.line(225, 16, 225, 170, color="var(--muted)", width=1, dash="3 4")
S.text(115, 14, "base cases", size=12, color="var(--muted)")
S.text(435, 14, "the hypothesis applies to S and T", size=12, color="var(--accent)")
save("ch02-structural-cases", S.figure(
    "<strong>The five shapes of a regular expression.</strong> The root of an expression tree is a leaf (∅ or a "
    "string) or one of the operators +, • and *. In the last three cases <i>S</i> and <i>T</i> are proper "
    "subexpressions — strictly smaller trees — so a structural induction may assume the claim for them.",
    alt="five small trees: a leaf empty set, a leaf string w, a plus node over S and T, a concatenation node over "
        "S and T, a star node over S"))

# ---------------------------------------------------------------- block decompositions for the design examples
B1 = ["0", "100", "0", "100", "100", "0"]                 # (0+100)*
B2 = ["10", "0", "0", "10", "1"]                          # ((0+10)(0+10))*(ε+1): two pairs and a final 1
T = Tape(600, 204, font_size=15)
cell = 28


def row(y, blocks, x0, colors, labels_below, title):
    w = "".join(blocks)
    T.text(x0 - 14, y + cell / 2, title, size=14, anchor="end", font=SERIF_IT, italic=True)
    T.cells(x0, y, list(w), cell=cell, dots=False)
    k = 0
    for b, col, lab in zip(blocks, colors, labels_below):
        x1, x2 = x0 + k * cell + 3, x0 + (k + len(b)) * cell - 3
        T.path(f"M{x1},{y + cell + 4} L{x1},{y + cell + 10} L{x2},{y + cell + 10} L{x2},{y + cell + 4}",
               color=col, width=1.6)
        T.text((x1 + x2) / 2, y + cell + 24, lab, size=13, font=MONO, color=col)
        k += len(b)
    return x0 + k * cell


A1, A2 = "var(--accent)", "var(--accent2)"
end1 = row(26, B1, 120, [A1 if b == "0" else A2 for b in B1], B1, "w")
T.text(end1 + 16, 26 + cell / 2, "∈ (0+100)*", size=14, anchor="start", font=MONO)
y2 = 134
end2 = row(y2, B2, 120, [A1, A1, A2, A2, "var(--hi)"], ["10", "0", "0", "10", "1"], "w")
T.text(end2 + 16, y2 + cell / 2, "∈ ((0+10)(0+10))*(ε+1)", size=14, anchor="start", font=MONO)
# braces over the pairs of blocks in the second row
for (k1, k2, lab) in ((0, 3, "pair 1"), (3, 6, "pair 2")):
    x1, x2 = 120 + k1 * cell + 3, 120 + k2 * cell - 3
    T.path(f"M{x1},{y2 - 4} L{x1},{y2 - 10} L{x2},{y2 - 10} L{x2},{y2 - 4}", color="var(--muted)", width=1.2)
    T.text((x1 + x2) / 2, y2 - 20, lab, size=12, color="var(--muted)")
T.text(120 + 6.5 * cell, y2 - 20, "final 1", size=12, color="var(--hi)")
save("ch02-blocks", T.figure(
    "<strong>Designing by blocks.</strong> Top: a string in which every 1 is followed by 00 splits uniquely into "
    "blocks 0 and 100, so the language is (0+100)*. Bottom: a string with no 11 splits into blocks 0 and 10, "
    "possibly followed by one final 1; each block holds exactly one 0, so an even number of 0s means an even number "
    "of blocks — they come in pairs.",
    alt="two strings split into blocks: 0 100 0 100 100 0, and 10 0 0 10 followed by a final 1"))

# ---------------------------------------------------------------- Arden's rule on the odd-number-of-1s DFA
from figlib import Automaton  # noqa: E402


def eq_text(S, x, y, parts, size=15, anchor="middle"):
    """One line of math: parts are (text, kind) with kind L (italic L), sub (subscript), mono (symbols), op."""
    out = []
    for txt, kind in parts:
        if kind == "L":
            out.append(f'<tspan style="font-family:{SERIF_IT};font-style:italic">{txt}</tspan>')
        elif kind == "sub":
            out.append(f'<tspan style="font-family:{SERIF_IT};font-style:italic;font-size:{size - 4}px" '
                       f'baseline-shift="sub">{txt}</tspan>')
        elif kind == "mono":
            out.append(f'<tspan style="font-family:{MONO};font-size:{size - 1}px">{txt}</tspan>')
        else:
            out.append(f'<tspan style="font-family:{SERIF_IT}"> {txt} </tspan>')
    S.text(x, y, "".join(out), size=size, anchor=anchor, raw=True)


A = Automaton(560, 172)
A.state("s", 160, 80, start="left")
A.state("t", 400, 80, accepting=True)
A.loop("s", "0", "above")
A.loop("t", "0", "above")
A.edge("s", "t", "1", bend=14)
A.edge("t", "s", "1", bend=14)
eq_text(A, 160, 150, [("L", "L"), ("s", "sub"), ("=", "op"), ("0", "mono"), ("L", "L"), ("s", "sub"), ("∪", "op"),
                      ("1", "mono"), ("L", "L"), ("t", "sub")])
eq_text(A, 400, 150, [("L", "L"), ("t", "sub"), ("=", "op"), ("0", "mono"), ("L", "L"), ("t", "sub"), ("∪", "op"),
                      ("1", "mono"), ("L", "L"), ("s", "sub"), ("∪", "op"), ("{ε}", "L")])
save("ch02-arden-dfa", A.figure(
    "<strong>One equation per state.</strong> <i>L<sub>q</sub></i> is the set of strings that lead from state "
    "<i>q</i> to the accepting state. A non-empty string in <i>L<sub>q</sub></i> starts with 0 or 1 and continues from "
    "the state that symbol leads to; and since <i>t</i> is accepting, ε ∈ <i>L<sub>t</sub></i>. The DFA accepts "
    "<i>L<sub>s</sub></i>, the strings with an odd number of 1s.",
    alt="two-state DFA: start state s loops on 0, accepting state t loops on 0, a 1 moves between them; under each "
        "state its language equation"))
