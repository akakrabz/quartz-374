#!/usr/bin/env python3
"""Figures for five worked problems (state elimination, the w#w Turing machine).
Writes tools/figs/prob2-<name>.html; then run tools/assemble.py on the problem pages."""
import os
from figlib import Automaton

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")
os.makedirs(OUT, exist_ok=True)


def save(name, html):
    with open(os.path.join(OUT, name + ".html"), "w", encoding="utf-8") as f:
        f.write(html + "\n")
    print("wrote", name)


Q = {"q0": "q₀", "q1": "q₁", "q2": "q₂"}

# ---------------------------------------------------------------- the DFA as an expression automaton (step 0)
A = Automaton(440, 250)
A.state("s", 40, 62, start="above")
A.state("t", 40, 192, accepting=True)
A.state("q0", 150, 127, label=Q["q0"])
A.state("q1", 340, 45, label=Q["q1"])
A.state("q2", 340, 209, label=Q["q2"])
A.edge("s", "q0", "ε")
A.edge("q0", "t", "ε", label_side=-1)
A.edge("q0", "q1", "0", bend=13)
A.edge("q1", "q0", "1", bend=13)
A.edge("q1", "q2", "0", bend=13)
A.edge("q2", "q1", "1", bend=13)
A.edge("q2", "q0", "0", bend=13)
A.edge("q0", "q2", "1", bend=13)
save("prob2-elim-start", A.figure(
    "<strong>Step 0: the DFA as an expression automaton.</strong> State <i>q<sub>i</sub></i> means "
    "“#0 − #1 ≡ <i>i</i> (mod 3)”: a 0 moves one step around the triangle, a 1 one step back. "
    "The new start <i>s</i> and target <i>t</i> are joined to <i>q</i><sub>0</sub> by ε-edges, "
    "so no edge enters <i>s</i> and none leaves <i>t</i>.",
    alt="expression automaton: s, epsilon to q0, triangle q0 q1 q2 with 0-edges one way and 1-edges the other, q0 epsilon to t"))

# ---------------------------------------------------------------- the three eliminations, side by side
A = Automaton(690, 215, r=17)
# panel 1: after eliminating q1
A.state("1s", 24, 112, label="s", start=None)
A.state("1q0", 92, 112, label=Q["q0"])
A.state("1q2", 210, 112, label=Q["q2"])
A.state("1t", 92, 192, label="t", accepting=True)
A.edge("1s", "1q0", "ε")
A.loop("1q0", "01", "above", size=0.75)
A.loop("1q2", "10", "above", size=0.75)
A.edge("1q0", "1q2", "1+00", bend=12)
A.edge("1q2", "1q0", "0+11", bend=12)
A.edge("1q0", "1t", "ε", label_side=-1)
# panel 2: after eliminating q2
A.state("2s", 280, 112, label="s")
A.state("2q0", 380, 112, label=Q["q0"])
A.state("2t", 480, 112, label="t", accepting=True)
A.edge("2s", "2q0", "ε")
A.edge("2q0", "2t", "ε")
A.loop("2q0", "01+(1+00)(10)*(0+11)", "above", size=0.75)
# panel 3: after eliminating q0
A.state("3s", 548, 112, label="s")
A.state("3t", 662, 112, label="t", accepting=True)
A.edge("3s", "3t", "", )
for x, title in [(125, "after eliminating q₁"), (380, "after eliminating q₂"), (605, "after eliminating q₀")]:
    A.text(x, 14, title, size=13, color="var(--muted)")
A.text(605, 140, "(01+(1+00)(10)*(0+11))*", size=11.5, font="'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace",
       halo=True)
for x in (250, 520):
    A.line(x, 30, x, 205, color="var(--muted)", width=1, dash="3 4", opacity=0.6)
save("prob2-elim-steps", A.figure(
    "<strong>Steps 1–3: one state fewer each time.</strong> Eliminating <i>q</i><sub>1</sub> turns every detour "
    "through it into an edge label — including the round trips <i>q</i><sub>0</sub> → <i>q</i><sub>1</sub> → "
    "<i>q</i><sub>0</sub> (the loop 01) and <i>q</i><sub>2</sub> → <i>q</i><sub>1</sub> → <i>q</i><sub>2</sub> "
    "(the loop 10). Eliminating <i>q</i><sub>2</sub> folds its loop into a star; eliminating <i>q</i><sub>0</sub> "
    "leaves one edge, whose label is the answer.",
    alt="three expression automata: after eliminating q1, after eliminating q2, after eliminating q0"))

# ---------------------------------------------------------------- the Turing machine for w#w
A = Automaton(690, 396, r=16, font_size=14)


def st(name, x, y, **kw):
    A.state(name, x, y, shape="rounded", w=14 + 8 * len(name), **kw)


st("start", 78, 174, start="left")
st("carry0", 228, 76)
st("seek0", 418, 76)
st("carry1", 228, 276)
st("seek1", 418, 276)
st("backL", 330, 174)
st("backR", 590, 174)
st("check", 92, 364)
st("accept", 262, 364, accepting=True)
A.edge("start", "carry0", "0/x,+1")
A.edge("start", "carry1", "1/x,+1", label_side=-1)
A.edge("start", "check", "#;+1", label_side=-1)
A.loop("carry0", "0,1;+1", "above", size=0.7)
A.loop("carry1", "0,1;+1", "below", size=0.7)
A.edge("carry0", "seek0", "#;+1")
A.edge("carry1", "seek1", "#;+1", label_side=-1)
A.loop("seek0", "x;+1", "above", size=0.7)
A.loop("seek1", "x;+1", "below", size=0.7)
A.edge("seek0", "backR", "0/x,−1")
A.edge("seek1", "backR", "1/x,−1", label_side=-1)
A.loop("backR", "x;−1", "right", size=0.7)
A.edge("backR", "backL", "#;−1", label_side=-1)
A.loop("backL", "0,1;−1", "above", size=0.6)
A.edge("backL", "start", "x;+1", label_side=-1)
A.loop("check", "x;+1", "left", size=0.6)
A.edge("check", "accept", "□;+1")
A.text(520, 366, "missing transitions go to reject", size=12, color="var(--muted)")
save("prob2-copy-machine", A.figure(
    "<strong>A Turing machine that decides {<i>w</i>#<i>w</i>}.</strong> Each round crosses off the next symbol "
    "of the left half (<i>start</i>), carries it across the # in the state (<i>carry0</i>/<i>carry1</i>), "
    "crosses off the matching symbol of the right half (<i>seek0</i>/<i>seek1</i>), and walks back "
    "(<i>backR</i>, then <i>backL</i>). A label <code>a/b,±1</code> means read <code>a</code>, write "
    "<code>b</code>, move; <code>0,1;−1</code> means read 0 or 1, leave it, move left.",
    alt="state diagram with states start, carry0, carry1, seek0, seek1, backR, backL, check, accept"))
