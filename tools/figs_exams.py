#!/usr/bin/env python3
"""Figures for the practice-exam pages (content/3-homework-and-exams/). Writes tools/figs/exam-<name>.html;
then run tools/assemble.py on the exam pages. Every machine drawn here is verified in tools/checks/exams_mt1.py.

Each writer appends a clearly marked section for their test (figure names exam-mt1pN-*)."""
import os
from figlib import Automaton, MONO

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")
os.makedirs(OUT, exist_ok=True)


def save(name, html):
    with open(os.path.join(OUT, name + ".html"), "w", encoding="utf-8") as f:
        f.write(html + "\n")
    print("wrote", name)


def subs(html):
    """State labels like N§0 get a real subscript digit (the Unicode subscript 0 looks like an o)."""
    for d in "012":
        html = html.replace(f"§{d}", f'<tspan dy="4" style="font-size:10px">{d}</tspan>')
    return html


# =====================================================================================================
# Practice test 1 (exam-mt1p1-*)
# =====================================================================================================

# ---------------------------------------------------------------- 5(a): no subsequence 010
A = Automaton(400, 128)
A.state("e", 70, 80, label="ε", accepting=True, start="left")
A.state("z", 200, 80, label="0", accepting=True, italic=False, font=MONO)
A.state("zo", 330, 80, label="01", accepting=True, italic=False, font=MONO)
A.loop("e", "1", "above")
A.loop("z", "0", "above")
A.loop("zo", "1", "above")
A.edge("e", "z", "0")
A.edge("z", "zo", "1")
save("exam-mt1p1-no-010-subsequence", A.figure(
    "<strong>No subsequence 010.</strong> Each state is named after the longest prefix of 010 that occurs in the "
    "input so far as a subsequence: ε (no 0 yet), 0 (a 0, but no 1 after it), 01 (a 0 followed later by a 1). "
    "All three accept. The missing transition, a 0 read in state 01, leads to a hidden dump state: the input "
    "contains 010.",
    alt="three accepting states in a row, named epsilon, 0 and 01, with loops 1, 0, 1 and edges 0 then 1"))

# ---------------------------------------------------------------- 5(b): at least two even-length runs of 1s
A = Automaton(640, 262, r=20)
top, bot = 78, 206
A.state("N0", 190, top, label="N§0", start="left")
A.state("O0", 340, top, label="O§0")
A.state("E0", 490, top, label="E§0")
A.state("N1", 490, bot, label="N§1")
A.state("O1", 340, bot, label="O§1")
A.state("E1", 190, bot, label="E§1", accepting=True)
A.state("D", 62, bot, label="done", accepting=True, shape="rounded", w=56, italic=False)
A.loop("N0", "0", "above")
A.edge("N0", "O0", "1", bend=12)
A.edge("O0", "N0", "0", bend=12)
A.edge("O0", "E0", "1", bend=12)
A.edge("E0", "O0", "1", bend=12)
A.edge("E0", "N1", "0", label_side=-1)
A.loop("N1", "0", "right")
A.edge("N1", "O1", "1", bend=12)
A.edge("O1", "N1", "0", bend=12)
A.edge("O1", "E1", "1", bend=12)
A.edge("E1", "O1", "1", bend=12)
A.edge("E1", "D", "0")
A.loop("D", "0,1", "above")
save("exam-mt1p1-two-even-runs", subs(A.figure(
    "<strong>At least two even-length runs of 1s.</strong> The subscript <i>k</i> counts the <em>finished</em> "
    "runs of 1s (a 0 has been read after them) that have even length. <i>N</i>: the input is empty or ends with 0; "
    "<i>O</i>, <i>E</i>: it ends with a run of 1s of odd, even length so far. A 0 read in <i>E</i> finishes an "
    "even run, and <i>E</i>₁ accepts because an input that ends there ends with a second even run. "
    "<i>done</i> is a permanent accepting state.",
    alt="seven-state DFA: top row N0, O0, E0; bottom row done, E1, O1, N1; a 0 from E0 drops to N1 and a 0 "
        "from E1 leads to done")))


# =====================================================================================================
# Practice test 3 (exam-mt1p3-*)   (uses the shared save() and subs() above)
# =====================================================================================================

# ---------------------------------------------------------------- 3.5(a): runs of 1s even, runs of 0s odd
A = Automaton(640, 276, r=21)
A.state("E1", 80, 62, label="E,1", italic=False, accepting=True, start="left")
A.state("O1", 400, 62, label="O,1", italic=False)
A.state("O0", 240, 222, label="O,0", italic=False, accepting=True)
A.state("E0", 560, 222, label="E,0", italic=False)
A.edge("E1", "O1", "1", bend=10)
A.edge("O1", "E1", "1", bend=10)
A.edge("E1", "O0", "0", label_side=-1)
A.edge("O0", "O1", "1", label_side=-1)
A.edge("O0", "E0", "0", bend=10)
A.edge("E0", "O0", "0", bend=10)
save("exam-mt1p3-runs-dfa", A.figure(
    "<strong>Every run of 1s even, every run of 0s odd.</strong> A state names the symbol of the current run and "
    "the parity (E/O) of its length so far; every earlier run already has the right parity. E,1 is also the start "
    "state (the empty input has no runs). The two missing transitions — a 0 in O,1 and a 1 in E,0 — end a run of "
    "the wrong parity and lead to a hidden dump state.",
    alt="four-state DFA: E,1 (start, accepting) and O,1 exchange on 1; E,1 goes to O,0 on 0; O,0 (accepting) goes "
        "to O,1 on 1 and exchanges with E,0 on 0"))

# ---------------------------------------------------------------- 3.5(b): 0*10* with length a multiple of 3
A = Automaton(500, 300, r=20)
xs = [80, 250, 420]
for i, x in enumerate(xs):
    A.state(f"N{i}", x, 92, label=f"N§{i}", start=("left" if i == 0 else None))
    j = (i + 1) % 3
    A.state(f"Y{j}", x, 212, label=f"Y§{j}", accepting=(j == 0))
A.edge("N0", "N1", "0")
A.edge("N1", "N2", "0")
A.edge("N2", "N0", "0", bend=-42, label_dist=10)
A.edge("Y1", "Y2", "0")
A.edge("Y2", "Y0", "0")
A.edge("Y0", "Y1", "0", bend=42, label_dist=10)
A.edge("N0", "Y1", "1", label_side=-1)
A.edge("N1", "Y2", "1", label_side=-1)
A.edge("N2", "Y0", "1", label_side=-1)
save("exam-mt1p3-mod3-dfa", subs(A.figure(
    "<strong>One 1, and length a multiple of 3.</strong> The subscript is the length of the input so far, mod 3. "
    "Top row N: no 1 read yet; bottom row Y: exactly one 1 read. Each 0 moves one step along its row (and wraps "
    "around after 2); the 1 drops from N<sub><i>i</i></sub> to Y<sub><i>i</i>+1</sub>. Only Y<sub>0</sub> accepts. "
    "A second 1 (missing transitions out of the Y row) leads to a hidden dump state.",
    alt="six-state DFA in two rows of three: N0, N1, N2 cycle on 0; Y1, Y2, Y0 cycle on 0; vertical 1-edges from "
        "N0 to Y1, N1 to Y2 and N2 to Y0; Y0 is accepting")))


# =====================================================================================================
# Practice test 2 (exam-mt1p2-*)
# =====================================================================================================

# ---------------------------------------------------------------- 2(b): at least 374 consecutive 1s
A = Automaton(640, 180)
xs = {"0": 60, "1": 160, "2": 260, "373": 420, "374": 540}
for n, x in xs.items():
    A.state(n, x, 68, label=n, accepting=(n == "374"), start=("left" if n == "0" else None),
            shape="rounded", w=48, italic=False)
A.loop("0", "0", "above")
A.edge("0", "1", "1")
A.edge("1", "2", "1")
A.edge("373", "374", "1")
A.loop("374", "0,1", "above")
# the gap 2 -> ... -> 373: two dashed stubs and an ellipsis
A.path("M286,68 L316,68", dash="4 4")
A.text(340, 69, "⋯", size=18)
A.path("M364,68 L393.5,68", dash="4 4", arrow=True)
A.text(340, 48, "1", size=13, font=MONO)
# every 0 before the 374th 1 goes back to 0 (drawn below the chain)
A.edge("1", "0", "0", bend=20, label_dist=10)
A.edge("2", "0", "0", bend=32, label_dist=10)
A.edge("373", "0", "0", bend=46, label_dist=10)
save("exam-mt1p2-run-of-ones", A.figure(
    "<strong>At least 374 consecutive 1s.</strong> State <i>i</i> &lt; 374 means the input has no run of 374 1s yet "
    "and ends with exactly <i>i</i> consecutive 1s; a 1 moves one step right, a 0 resets to state 0. State 374 means "
    "a run of 374 1s has been seen, and it absorbs everything. 375 states, and Problem 2(c) shows no DFA does better.",
    alt="a chain of states 0, 1, 2, ..., 373, 374 joined by 1-edges, with 0-edges back to state 0 and an absorbing "
        "accepting state 374"))
