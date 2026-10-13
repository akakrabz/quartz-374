#!/usr/bin/env python3
"""Figures for Chapter 5 (context-free languages). Writes tools/figs/ch05-*.html; then run tools/assemble.py.

The parse trees and the recursive automaton are plain data at module level; tools/checks/ch05.py imports this
module and verifies exactly what is drawn (valid parse trees with the right yields, the automaton's language).
Importing does not write anything; running the script does."""
import os
from figlib import Automaton, SVG, Tree, MONO, SERIF_IT, SANS

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")


def nt(name, *kids):
    """Internal node labelled with a nonterminal ('$' marks nonterminals for figlib.Tree)."""
    return ("$" + name, list(kids))


def lf(sym):
    """Leaf: a terminal symbol or ε."""
    return (sym, [])


# ---------------------------------------------------------------- parse trees (checked in tools/checks/ch05.py)
# running example  S -> A | B,  A -> 0A | 0C,  B -> B1 | C1,  C -> ε | 0C1
TREE_C_0011 = nt("C", lf("0"), nt("C", lf("0"), nt("C", lf("ε")), lf("1")), lf("1"))
SUB_C_0011 = nt("C", lf("0"), nt("C", lf("0"), nt("C", lf("ε")), lf("1")), lf("1"))
TREE_S_00011 = nt("S", nt("A", lf("0"), SUB_C_0011))
# S -> 1 | S+S : the two parse trees of 1+1+1
INNER_L = nt("S", nt("S", lf("1")), lf("+"), nt("S", lf("1")))
INNER_R = nt("S", nt("S", lf("1")), lf("+"), nt("S", lf("1")))
TREE_111_LEFT = nt("S", INNER_L, lf("+"), nt("S", lf("1")))      # (1+1)+1
TREE_111_RIGHT = nt("S", nt("S", lf("1")), lf("+"), INNER_R)     # 1+(1+1)
# naive regular-expression grammar S -> 0 | 1 | S+S | SS | S* | (S) : two parse trees of 0*+1*
OPND_GOOD = nt("S", lf("1"))                                      # what the last * applies to
TREE_RE_GOOD = nt("S", nt("S", nt("S", lf("0")), lf("*")), lf("+"), nt("S", OPND_GOOD, lf("*")))
OPND_BAD = nt("S", nt("S", nt("S", lf("0")), lf("*")), lf("+"), nt("S", lf("1")))
TREE_RE_BAD = nt("S", OPND_BAD, lf("*"))
# the book's CNF grammar  S -> EA | EC | BF | CF | 0 | 1, A -> EA | EC | 0, B -> BF | CF | 1, C -> ED,
# D -> CF | 1, E -> 0, F -> 1 : the parse tree of 00011
TREE_CNF_00011 = nt("S", nt("E", lf("0")),
                    nt("C", nt("E", lf("0")),
                       nt("D", nt("C", nt("E", lf("0")), nt("D", lf("1"))), nt("F", lf("1")))))

# ---------------------------------------------------------------- recursive automaton for {0^m 1^n : m != n}
# edge labels: a terminal symbol, "ε", or "$X" = call module X.
RA_MAIN = "S"
RA_MODULES = {
    "S": {"start": "sS", "accept": "tS",
          "edges": [("sS", "0", "a"), ("a", "0", "a"), ("a", "$E", "tS"),
                    ("sS", "$E", "b"), ("b", "1", "b"), ("b", "1", "tS")]},
    "E": {"start": "sE", "accept": "tE",
          "edges": [("sE", "0", "c"), ("c", "$E", "d"), ("d", "1", "tE"), ("sE", "ε", "tE")]},
}


def ids(n):
    out = {id(n)}
    for k in n[1]:
        out |= ids(k)
    return out


def save(name, html):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name + ".html"), "w", encoding="utf-8") as f:
        f.write(html + "\n")
    print("wrote", name)


def mixed(S, x, y, parts, size=14, anchor="middle", color="currentColor"):
    """One line of mixed text: parts are (text, kind), kind in it (serif italic), mono, sans, sup."""
    out = []
    for txt, kind in parts:
        if kind == "it":
            out.append(f'<tspan style="font-family:{SERIF_IT};font-style:italic;font-size:{size + 1}px">{txt}</tspan>')
        elif kind == "mono":
            out.append(f'<tspan style="font-family:{MONO};font-size:{size - 1}px">{txt}</tspan>')
        elif kind == "sup":
            out.append(f'<tspan dy="-5" style="font-size:{size - 4}px">{txt}</tspan><tspan dy="5"> </tspan>')
        else:
            out.append(f'<tspan style="font-family:{SANS}">{txt}</tspan>')
    S.text(x, y, "".join(out), size=size, anchor=anchor, color=color, raw=True)


class RAFigure(Automaton):
    """Automaton whose edge labels starting with '$' are module names (serif italic), with an overlay layer
    drawn on top of the states (for subscripted state names)."""

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.overlay = []

    def _label(self, x, y, label, color, mono):
        if label.startswith("$"):
            self.text(x, y, label[1:], size=self.font_size + 2, color=color, font=SERIF_IT, italic=True, halo=True)
        else:
            super()._label(x, y, label, color, mono)

    def sub_label(self, name, base, sub, color="currentColor"):
        st = self.states[name]
        body = (f'<tspan style="font-family:{SERIF_IT};font-style:italic;font-size:16px">{base}</tspan>'
                f'<tspan dy="4" style="font-family:{SERIF_IT};font-style:italic;font-size:11px">{sub}</tspan>')
        saved, self.items = self.items, []
        self.text(st["x"] - 1, st["y"] - 1, body, color=color, raw=True)
        self.overlay += self.items
        self.items = saved

    def svg(self, alt=""):
        body_before = self.items
        self.items = []
        for e in self.edges:
            if e[0] == "edge":
                self._draw_edge(e)
            else:
                self._draw_loop(e)
        edges = self.items
        self.items = []
        for n in self.states:
            self._draw_state(n)
        states = self.items
        self.items = body_before + edges + states + self.overlay
        out = SVG.svg(self, alt)
        self.items = body_before
        return out


def main():
    # ------------------------------------------------------------ parse trees in the running example
    T = Tree(560, 300, font_size=15)
    T.draw(TREE_C_0011, 40, 46, level_h=40, leaf_w=40)
    T.draw(TREE_S_00011, 304, 46, level_h=40, leaf_w=40, hi=ids(SUB_C_0011))
    mixed(T, 140, 282, [("parse tree of ", "sans"), ("0011", "mono"), (" from ", "sans"), ("C", "it")])
    mixed(T, 424, 282, [("parse tree of ", "sans"), ("00011", "mono"), (" from ", "sans"), ("S", "it")])
    save("ch05-parse-trees", T.figure(
        "<strong>Parse trees in the running example.</strong> Left: <i>C</i> → 0<i>C</i>1 twice, then <i>C</i> → ε; "
        "the leaves, read left to right, spell 0011 (ε is the empty string). Right: <i>S</i> → <i>A</i>, then "
        "<i>A</i> → 0<i>C</i> adds one extra 0, and the red subtree is exactly the tree on the left.",
        alt="two parse trees: C over 0, C, 1 nested twice with C to epsilon in the middle; and S over A over 0 "
            "and the same C tree"))

    # ------------------------------------------------------------ the two parse trees of 1+1+1
    T = Tree(500, 236, font_size=15)
    T.draw(TREE_111_LEFT, 36, 40, level_h=44, leaf_w=36, hi=ids(INNER_L))
    T.draw(TREE_111_RIGHT, 284, 40, level_h=44, leaf_w=36, hi=ids(INNER_R))
    mixed(T, 126, 218, [("(1+1)+1", "mono")], size=15)
    mixed(T, 374, 218, [("1+(1+1)", "mono")], size=15)
    save("ch05-ambiguous-111", T.figure(
        "<strong>One string, two parse trees.</strong> With <i>S</i> → 1 | <i>S</i>+<i>S</i>, the string 1+1+1 can "
        "be split as <i>S</i>+<i>S</i> after its first + or after its second; the red subtree shows which two 1s "
        "are added first. So the grammar is ambiguous.",
        alt="two parse trees for 1+1+1 under S to 1 or S+S, one grouping the first two 1s, one the last two"))

    # ------------------------------------------------------------ 0*+1* in the naive regular-expression grammar
    T = Tree(540, 262, font_size=15)
    T.draw(TREE_RE_GOOD, 40, 46, level_h=42, leaf_w=38, hi=ids(OPND_GOOD))
    T.draw(TREE_RE_BAD, 310, 46, level_h=42, leaf_w=38, hi=ids(OPND_BAD))
    mixed(T, 135, 18, [("intended: ", "sans"), ("(0*)+(1*)", "mono")])
    mixed(T, 405, 18, [("also possible: ", "sans"), ("(0*+1)*", "mono")], color="var(--hi)")
    save("ch05-regex-trees", T.figure(
        "<strong>Right strings, wrong structure.</strong> The grammar <i>S</i> → 0 | 1 | <i>S</i>+<i>S</i> | "
        "<i>SS</i> | <i>S</i>* | (<i>S</i>) generates exactly the regular expressions over 0 and 1 that use "
        "neither ∅ nor ε, but gives "
        "0*+1* two parse trees. In red: what the last * applies to — just the 1 on the left, the whole of 0*+1 on "
        "the right, which is the meaning (0*+1)*.",
        alt="two parse trees for 0*+1*: one with plus at the root, one with star at the root over 0*+1"))

    # ------------------------------------------------------------ recursive automaton for {0^m 1^n : m != n}
    A = RAFigure(640, 300)
    A.rect(6, 22, 306, 272, rx=16, stroke="var(--muted)", width=1.2, dash="5 4")
    A.rect(328, 22, 306, 272, rx=16, stroke="var(--muted)", width=1.2, dash="5 4")
    mixed(A, 20, 40, [("module ", "sans"), ("S", "it"), ("  (main)", "sans")], size=13, anchor="start",
          color="var(--muted)")
    mixed(A, 342, 40, [("module ", "sans"), ("E", "it")], size=13, anchor="start", color="var(--muted)")
    pos = {"sS": (64, 158), "a": (164, 100), "b": (164, 214), "tS": (264, 158),
           "sE": (392, 214), "c": (440, 104), "d": (556, 104), "tE": (590, 214)}
    for m in RA_MODULES.values():
        for q in sorted({m["start"], m["accept"]} | {e[0] for e in m["edges"]} | {e[2] for e in m["edges"]}):
            x, y = pos[q]
            A.state(q, x, y, label="" if q in ("sS", "tS", "sE", "tE") else q,
                    accepting=(q == m["accept"]), start=("left" if q == m["start"] else None))
    call = dict(color="var(--accent)", label_color="var(--accent)")
    A.edge("sS", "a", "0", label_side=1)
    A.loop("a", "0", "above")
    A.edge("a", "tS", "$E", label_side=1, **call)
    A.edge("sS", "b", "$E", label_side=-1, **call)
    A.loop("b", "1", "below")
    A.edge("b", "tS", "1", label_side=-1)
    A.edge("sE", "c", "0", label_side=1)
    A.edge("c", "d", "$E", label_side=1, **call)
    A.edge("d", "tE", "1", label_side=1)
    A.edge("sE", "tE", "ε", label_side=-1)
    for q, base, sub in (("sS", "s", "S"), ("tS", "t", "S"), ("sE", "s", "E"), ("tE", "t", "E")):
        A.sub_label(q, base, sub)
    save("ch05-recursive-automaton", A.figure(
        "<strong>A recursive automaton for {0<sup><i>m</i></sup>1<sup><i>n</i></sup> | <i>m</i> ≠ <i>n</i>}.</strong> "
        "Each module is an NFA whose edges may also carry a module name (blue): following such an edge "
        "<em>calls</em> that module, which must run from its start state to its accepting state before control "
        "returns to the edge's target. Module <i>E</i> accepts {0<sup><i>n</i></sup>1<sup><i>n</i></sup>}, one "
        "path per rule of <i>E</i> → 0<i>E</i>1 | ε; the main module <i>S</i> accepts extra 0s followed by a "
        "call of <i>E</i>, or a call of <i>E</i> followed by extra 1s.",
        alt="two modules: S with states s_S, a, b, t_S; E with states s_E, c, d, t_E; edges labelled E call "
            "module E"))

    # ------------------------------------------------------------ a CNF parse tree: 2n-1 nonterminal nodes
    T = Tree(480, 296, font_size=15)
    leaf_parents = set()

    def collect(n):
        lab, kids = n
        if lab.startswith("$") and len(kids) == 1 and not kids[0][1]:
            leaf_parents.add(id(n))
        for k in kids:
            collect(k)

    collect(TREE_CNF_00011)
    T.draw(TREE_CNF_00011, 140, 24, level_h=38, leaf_w=40, hi=leaf_parents)
    # Tree.draw colours `hi` nodes var(--hi); for this figure use the accent colour instead
    T.items = [it.replace("var(--hi)", "var(--accent)") for it in T.items]
    mixed(T, 240, 258, [("5 leaves", "sans"), ("  ·  ", "sans"), ("5 blue nodes ", "sans"), ("A", "it"),
                        (" → ", "sans"), ("a", "it"), ("  ·  ", "sans"), ("4 black nodes ", "sans"), ("A", "it"),
                        (" → ", "sans"), ("BC", "it")], size=13)
    mixed(T, 240, 280, [("9 = 2·5 − 1 nonterminal nodes, so every derivation of ", "sans"), ("00011", "mono"),
                        (" takes 9 steps", "sans")], size=13, color="var(--muted)")
    save("ch05-cnf-tree", T.figure(
        "<strong>A parse tree in Chomsky normal form.</strong> The tree of 00011 in the CNF grammar of §5.9. "
        "Each leaf hangs below its own node <i>A</i> → <i>a</i> (blue), and the nodes <i>A</i> → <i>BC</i> form a "
        "full binary tree with those <i>n</i> nodes as its leaves, so there are <i>n</i> − 1 of them: "
        "2<i>n</i> − 1 nonterminal nodes in all.",
        alt="binary parse tree of 00011 with root S, children E over 0 and C, and so on"))


if __name__ == "__main__":
    main()
