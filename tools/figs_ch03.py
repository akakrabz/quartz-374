#!/usr/bin/env python3
"""Figures for Chapter 3 (finite-state machines). Writes tools/figs/<name>.html; then run tools/assemble.py."""
import os
from figlib import Automaton, SVG, MONO, SERIF_IT

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")
os.makedirs(OUT, exist_ok=True)


def save(name, html):
    with open(os.path.join(OUT, name + ".html"), "w", encoding="utf-8") as f:
        f.write(html + "\n")
    print("wrote", name)


# ---------------------------------------------------------------- mod-5 DFA
A = Automaton(640, 232)
A.state("0", 70, 115, accepting=True, start="left", italic=False)
A.state("1", 210, 50, italic=False)
A.state("2", 330, 180, italic=False)
A.state("3", 450, 50, italic=False)
A.state("4", 570, 115, italic=False)
A.loop("0", "0", "below")
A.edge("0", "1", "1")
A.edge("1", "3", "1", bend=12)
A.edge("3", "1", "0", bend=12)
A.edge("1", "2", "0")
A.edge("3", "2", "1")
A.edge("2", "0", "1")
A.edge("2", "4", "0")
A.edge("4", "3", "0")
A.loop("4", "1", "below")
save("ch03-mod5-dfa", A.figure(
    "<strong>Binary multiples of 5.</strong> State <i>q</i> is the value of the prefix read so far, mod 5; "
    "reading the bit <i>a</i> moves to (2<i>q</i> + <i>a</i>) mod 5. The start state 0 is the only accepting state.",
    alt="DFA with states 0 to 4 for binary multiples of 5"))

# ---------------------------------------------------------------- parity of 1s
A = Automaton(400, 150)
A.state("s", 110, 75, start="left")
A.state("t", 290, 75, accepting=True)
A.loop("s", "0", "above")
A.loop("t", "0", "above")
A.edge("s", "t", "1", bend=14)
A.edge("t", "s", "1", bend=14)
save("ch03-parity-dfa", A.figure(
    "<strong>An odd number of 1s.</strong> <i>s</i> means “even so far”, <i>t</i> means “odd so far”. "
    "A 0 never changes the parity; a 1 always flips it.",
    alt="two-state DFA for strings with an odd number of 1s"))

# ---------------------------------------------------------------- contains 11
A = Automaton(470, 160)
A.state("s", 80, 95, start="left")
A.state("a", 230, 95)
A.state("b", 380, 95, accepting=True)
A.loop("s", "0", "above")
A.edge("s", "a", "1", bend=13)
A.edge("a", "s", "0", bend=13)
A.edge("a", "b", "1")
A.loop("b", "0,1", "above")
save("ch03-contains-11-dfa", A.figure(
    "<strong>Strings containing 11, minimal DFA.</strong> <i>s</i>: no 11 yet and the last symbol (if any) is not 1; "
    "<i>a</i>: no 11 yet and the last symbol is 1; <i>b</i>: 11 has appeared (a sink: it never leaves).",
    alt="three-state DFA for strings containing 11"))

# ---------------------------------------------------------------- product: even #0 and odd #1
A = Automaton(560, 268, r=24)
# grid: rows = parity of 0s (E top, O bottom), cols = parity of 1s (E left, O right)
xs, ys = {"E": 170, "O": 400}, {"E": 60, "O": 200}
for z in "EO":
    for o in "EO":
        A.state(f"{z}{o}", xs[o], ys[z], label=f"{z.lower()}{o.lower()}" if False else f"({z},{o})",
                 accepting=(z == "E" and o == "O"), start=("left" if (z, o) == ("E", "E") else None),
                 shape="rounded", w=58, italic=False, r=19)
# 1 flips the second component (horizontal), 0 flips the first (vertical)
for z in "EO":
    A.edge(f"{z}E", f"{z}O", "1", bend=10)
    A.edge(f"{z}O", f"{z}E", "1", bend=10)
for o in "EO":
    A.edge(f"E{o}", f"O{o}", "0", bend=10)
    A.edge(f"O{o}", f"E{o}", "0", bend=10)
A.text(285, 256, "(parity of 0s, parity of 1s)", size=13, color="var(--muted)")
save("ch03-product-dfa", A.figure(
    "<strong>The product of two parity DFAs.</strong> The first component tracks the parity of 0s (E/O), the second "
    "the parity of 1s. A 0 moves vertically, a 1 horizontally. With accepting set {(E, O)} the product accepts "
    "“even number of 0s <em>and</em> odd number of 1s”; other accepting sets give ∪, \\, ⊕ of the same two languages.",
    alt="four-state product DFA arranged in a 2 by 2 grid"))

# ---------------------------------------------------------------- why fooling sets work
S = SVG(600, 170)
S.add('<defs><marker id="ARR2" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs>')
# start
S.circle(70, 85, 19)
S.text(70, 86, "s", size=15, font=SERIF_IT, italic=True)
S.line(20, 85, 48, 85, arrow=True)
# q
S.circle(300, 85, 19, stroke="var(--hi)")
S.text(300, 86, "q", size=15, font=SERIF_IT, italic=True, color="var(--hi)")
# r
S.circle(520, 85, 19)
S.circle(520, 85, 23)
S.text(520, 86, "r", size=15, font=SERIF_IT, italic=True)
S.path("M88,76 C150,20 230,20 284,72", arrow=True, dash="5 4")
S.path("M88,94 C150,150 230,150 284,98", arrow=True, dash="5 4")
S.text(185, 26, "x", size=15, font=MONO, halo=True)
S.text(185, 146, "y", size=15, font=MONO, halo=True)
S.path("M321,85 L494,85", arrow=True, dash="5 4")
S.text(408, 72, "z", size=15, font=MONO, halo=True)
S.text(300, 128, "same state", size=12, color="var(--hi)")
save("ch03-fooling-idea", S.figure(
    "<strong>Why a distinguishing suffix forces two states.</strong> If <i>x</i> and <i>y</i> led to the same state "
    "<i>q</i>, then <i>xz</i> and <i>yz</i> would end in the same state <i>r</i>, so the DFA would accept both or "
    "neither. A suffix <i>z</i> with exactly one of <i>xz</i>, <i>yz</i> in <i>L</i> rules that out.",
    alt="schematic: strings x and y reach the same state q, then z leads to r"))

# ---------------------------------------------------------------- mod-6 counter and its minimization
import math
A = Automaton(620, 262)
cx, cy, R = 150, 138, 78
for i in range(6):
    ang = math.radians(90 - 60 * i)
    A.state(str(i), cx + R * math.cos(ang), cy - R * math.sin(ang), accepting=(i % 3 == 0),
            start=("above" if i == 0 else None), italic=False, r=17)
for i in range(6):
    A.edge(str(i), str((i + 1) % 6), "1", bend=7, label_dist=12)
# merged
mx = 470
pos = {"{0,3}": (mx, 73), "{1,4}": (mx + 80, 193), "{2,5}": (mx - 80, 193)}
for k, (x, y) in pos.items():
    A.state(k, x, y, accepting=(k == "{0,3}"), start=("left" if k == "{0,3}" else None),
            shape="rounded", w=46, italic=False, r=17)
A.edge("{0,3}", "{1,4}", "1", bend=8)
A.edge("{1,4}", "{2,5}", "1", bend=8)
A.edge("{2,5}", "{0,3}", "1", bend=8)
A.text(310, 138, "⟹", size=26)
A.text(150, 248, "6 states (count of 1s mod 6)", size=12, color="var(--muted)")
A.text(470, 248, "3 states after merging", size=12, color="var(--muted)")
save("ch03-mod6-minimize", A.figure(
    "<strong>Minimizing a wasteful DFA.</strong> Counting 1s mod 6 decides “the number of 1s is a multiple of 3”, "
    "but states <i>i</i> and <i>i</i>+3 can never be distinguished, so Moore's algorithm merges them. "
    "(Every state also loops on 0; those loops are omitted.)",
    alt="six-state ring DFA and the three-state DFA after merging equivalent states"))
