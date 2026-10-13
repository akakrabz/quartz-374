#!/usr/bin/env python3
"""Figures for six worked problems (content/problems/). Writes tools/figs/prob1-<name>.html; then run
tools/assemble.py on the problem pages. Every machine drawn here is verified in tools/checks/problems_1.py."""
import os
from figlib import Automaton, Tree

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")
os.makedirs(OUT, exist_ok=True)


def save(name, html):
    with open(os.path.join(OUT, name + ".html"), "w", encoding="utf-8") as f:
        f.write(html + "\n")
    print("wrote", name)


def subs(html):
    """State labels like ones§0 get a real subscript digit (the Unicode subscript 0 looks like an o)."""
    for d in "012":
        html = html.replace(f"§{d}", f'<tspan dy="4" style="font-size:10px">{d}</tspan>')
    return html

# ---------------------------------------------------------------- problem 2: exactly two occurrences of 01
A = Automaton(640, 236)
xs = [70, 172, 274, 376, 478, 580]
names = []
for k in range(3):
    names += [f"ones{k}", f"zeros{k}"]
for i, n in enumerate(names):
    lab = ("ones" if n.startswith("ones") else "zeros") + "§" + n[-1]
    A.state(n, xs[i], 92, label=lab, accepting=n.endswith("2"), start=("left" if i == 0 else None),
            shape="rounded", w=58, italic=False)
A.state("dead", 580, 196, label="dead", shape="rounded", w=52, italic=False)
for i, n in enumerate(names):
    A.loop(n, "1" if n.startswith("ones") else "0", "above")
    if i + 1 < len(names):
        A.edge(n, names[i + 1], "0" if n.startswith("ones") else "1", label_dist=10)
A.edge("zeros2", "dead", "1", label_side=-1)
A.loop("dead", "0,1", "left")
save("prob1-two01-dfa", subs(A.figure(
    "<strong>Exactly two occurrences of 01.</strong> The subscript counts the occurrences of 01 read so far; "
    "<i>ones</i> means the input so far is empty or ends in 1, <i>zeros</i> that it ends in 0. A 0 moves from "
    "<i>ones</i> to <i>zeros</i>, and a 1 after a 0 completes one more 01. The accepting states are the two with "
    "subscript 2; a third 01 leads to the dump state <i>dead</i>.",
    alt="seven-state DFA drawn as a chain: ones0, zeros0, ones1, zeros1, ones2, zeros2, then dead")))

# ---------------------------------------------------------------- problem 3: a parse tree for 001110
T = Tree(380, 222)
leaf = lambda s: (s, [])  # noqa: E731
tree = ("$S", [("$A", [leaf("0"), ("$A", [leaf("0"), ("$A", [leaf("ε")]), leaf("1")]), leaf("1")]),
               ("$B", [leaf("1"), ("$B", [leaf("ε")]), leaf("0")])])
pos = T.draw(tree, 40, 22, level_h=38, leaf_w=36)
# braces under the two halves
T.path("M44,180 L44,186 L216,186 L216,180")
T.text(130, 204, "A ⇝* 0011 = 0²1²", size=13, color="var(--muted)")
T.path("M224,180 L224,186 L324,186 L324,180")
T.text(274, 204, "B ⇝* 10 = 1¹0¹", size=13, color="var(--muted)")
save("prob1-cfg-parse-tree", T.figure(
    "<strong>The parse tree of 001110 = 0²1³0¹.</strong> <i>S</i> → <i>AB</i> cuts the string into "
    "0<sup><i>i</i></sup>1<sup><i>i</i></sup> = 0011 (from <i>A</i>) and 1<sup><i>k</i></sup>0<sup><i>k</i></sup> = 10 "
    "(from <i>B</i>); the middle run 111 is shared between the two halves. Leaves read left to right spell the string "
    "(ε contributes nothing).",
    alt="parse tree: S with children A and B; A derives 0 0 epsilon 1 1, B derives 1 epsilon 0"))

# ---------------------------------------------------------------- problem 4: Insert1 and Delete1 on a parity DFA
A = Automaton(640, 276, r=21)
A.text(165, 16, "Insert1: skip one input 1", size=13, color="var(--muted)")
A.text(495, 16, "Delete1: feed M one extra 1", size=13, color="var(--muted)")
for (ox, tag) in [(0, "I"), (330, "D")]:
    ex, ox_ = 95 + ox, 235 + ox
    for f, y in [(0, 100), (1, 232)]:
        A.state(f"{tag}E{f}", ex, y, label=f"E,{f}", italic=False, start=("left" if (f == 0) else None))
        A.state(f"{tag}O{f}", ox_, y, label=f"O,{f}", italic=False, accepting=(f == 1))
        A.edge(f"{tag}E{f}", f"{tag}O{f}", "1", bend=10)
        A.edge(f"{tag}O{f}", f"{tag}E{f}", "1", bend=10)
        A.loop(f"{tag}O{f}", "0", "right")
        A.loop(f"{tag}E{f}", "0", "above" if f == 0 else "left")
A.edge("IE0", "IE1", "1", hi=True, label_side=1)
A.edge("IO0", "IO1", "1", hi=True, label_side=-1)
A.edge("DE0", "DO1", "ε", hi=True, label_pos=0.36, label_dist=12, mono=False, label_side=-1)
A.edge("DO0", "DE1", "ε", hi=True, label_pos=0.36, label_dist=12, mono=False, label_side=1)
save("prob1-insert-delete", A.figure(
    "<strong>Two copies of <i>M</i>, one guess.</strong> Here <i>M</i> accepts the strings with an odd number of 1s "
    "(E/O: even/odd so far). Top row: phase 0, the extra 1 has not been handled yet; bottom row: phase 1, it has. "
    "Left: reading a 1 may drop to phase 1 <em>without moving M</em> — that 1 is the inserted one. Right: an "
    "ε-move drops to phase 1 while <em>M reads a 1 that is not in the input</em> (so E,0 drops to O,1). Only (O, 1) "
    "accepts. The left machine accepts an even, positive number of 1s; the right one an even number of 1s.",
    alt="two NFAs, each two copies of a two-state parity DFA, joined by highlighted 1-edges (left) and "
        "epsilon-edges (right)"))

# ---------------------------------------------------------------- problem 5: the two factor DFAs
A = Automaton(640, 178)
A.text(160, 14, "M₁: number of 1s mod 3", size=13, color="var(--muted)")
A.text(490, 14, "M₂: no 00", size=13, color="var(--muted)")
for r, x in zip(range(3), [66, 166, 266]):
    A.state(f"r{r}", x, 92, label=str(r), italic=False, accepting=(r == 0), start=("left" if r == 0 else None))
    A.loop(f"r{r}", "0", "above")
A.edge("r0", "r1", "1")
A.edge("r1", "r2", "1")
A.edge("r2", "r0", "1", bend=22, label_dist=10)
A.state("safe", 380, 92, label="safe", accepting=True, start="below", shape="rounded", w=50, italic=False)
A.state("zero", 490, 92, label="zero", accepting=True, shape="rounded", w=50, italic=False)
A.state("dead", 592, 92, label="dead", shape="rounded", w=50, italic=False)
A.loop("safe", "1", "above")
A.edge("safe", "zero", "0", bend=9)
A.edge("zero", "safe", "1", bend=9)
A.edge("zero", "dead", "0")
A.loop("dead", "0,1", "above")
save("prob1-product-factors", A.figure(
    "<strong>The two factors.</strong> <i>M</i>₁ keeps the number of 1s mod 3 and accepts 0. <i>M</i>₂ keeps "
    "<i>safe</i> (no 00 yet, and the input is empty or ends in 1), <i>zero</i> (no 00 yet, ends in 0) or "
    "<i>dead</i> (00 has appeared, a dump state); it accepts <i>safe</i> and <i>zero</i>. "
    "The product's states are the nine pairs (<i>r</i>, <i>p</i>).",
    alt="left: three-state cycle counting 1s mod 3; right: three-state DFA safe, zero, dead"))

# ---------------------------------------------------------------- problem 6: the NFA
A = Automaton(460, 228)
A.state("s", 70, 86, start="left")
A.state("p", 220, 86)
A.state("t", 370, 86, accepting=True)
A.state("q", 220, 192)
A.loop("s", "0", "above")
A.loop("t", "1", "above")
A.edge("s", "p", "ε", mono=False)
A.edge("p", "t", "ε", mono=False)
A.edge("p", "q", "0", bend=-12)
A.edge("q", "p", "1", bend=-12)
save("prob1-subset-nfa", A.figure(
    "<strong>An NFA for 0*(01)*1*.</strong> <i>s</i> reads the leading 0s, the cycle <i>p</i> → <i>q</i> → <i>p</i> "
    "reads one block 01, and <i>t</i> reads the trailing 1s. The two ε-transitions move from one phase to the next "
    "without reading anything. Missing transitions lead nowhere (the thread dies).",
    alt="NFA with states s, p, q, t; epsilon edges s to p and p to t; p to q on 0 and q to p on 1"))

# ---------------------------------------------------------------- problem 6: the DFA from the subset construction
A = Automaton(560, 290)
P = {"S": (58, 110), "SQ": (172, 110), "PT": (300, 48), "P": (300, 176), "Q": (430, 110), "T": (172, 238),
     "E": (430, 238)}
LAB = {"S": "{s}", "SQ": "{s,q}", "PT": "{p,t}", "P": "{p}", "Q": "{q}", "T": "{t}", "E": "∅"}
ACC = {"S", "SQ", "PT", "P", "T"}
for k, (x, y) in P.items():
    A.state(k, x, y, label=LAB[k], accepting=k in ACC, start=("left" if k == "S" else None), shape="rounded",
            w=48, italic=False, hi=(k in ("PT", "P")))
A.edge("S", "SQ", "0")
A.edge("S", "T", "1", label_side=-1)
A.loop("SQ", "0", "above")
A.edge("SQ", "PT", "1")
A.edge("PT", "Q", "0")
A.edge("PT", "T", "1", label_pos=0.62, label_side=-1)
A.edge("P", "Q", "0", bend=7)
A.edge("Q", "P", "1", bend=7)
A.edge("P", "T", "1", label_side=-1)
A.edge("Q", "E", "0", label_side=-1)
A.edge("T", "E", "0")
A.loop("T", "1", "left")
A.loop("E", "0,1", "right")
save("prob1-subset-dfa", A.figure(
    "<strong>The DFA found by the subset construction.</strong> Seven of the 16 subsets are reachable; five are "
    "accepting because their ε-reach contains <i>t</i>. ∅ is the dump state. The two highlighted states {p,t} and "
    "{p} have the same ε-reach {p,t}, hence identical rows: they are equivalent, and merging them gives the "
    "6-state minimal DFA.",
    alt="seven-state DFA whose states are sets of NFA states"))
