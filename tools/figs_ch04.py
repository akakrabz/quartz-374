#!/usr/bin/env python3
"""Figures for Chapter 4 (nondeterministic automata). Writes tools/figs/<name>.html; then run tools/assemble.py."""
import os
from figlib import Automaton, SVG, MONO, SERIF_IT, SANS

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")
os.makedirs(OUT, exist_ok=True)


def save(name, html):
    with open(os.path.join(OUT, name + ".html"), "w", encoding="utf-8") as f:
        f.write(html + "\n")
    print("wrote", name)


def math(svg, x, y, s, size=15, color="currentColor", anchor="middle", halo=True):
    """A serif-italic (math-style) label."""
    svg.text(x, y, s, size=size, font=SERIF_IT, italic=True, color=color, anchor=anchor, halo=halo)


def note(svg, x, y, s, size=12, anchor="middle", color="var(--muted)"):
    svg.text(x, y, s, size=size, color=color, anchor=anchor)


# ====================================================================== 4.1 contains 00 or 11
A = Automaton(470, 210)
A.state("s", 80, 110, start="left")
A.state("a", 235, 48)
A.state("b", 235, 172)
A.state("c", 390, 110, accepting=True)
A.loop("s", "0,1", "above")
A.loop("c", "0,1", "above")
A.edge("s", "a", "0", label_side=1)
A.edge("s", "b", "1", label_side=-1)
A.edge("a", "c", "0", label_side=1)
A.edge("b", "c", "1", label_side=-1)
save("ch04-nfa-00-11", A.figure(
    "<strong>An NFA for the strings that contain 00 or 11.</strong> On each symbol, <i>s</i> may stay put or guess "
    "that this symbol starts the pair: a 0 may move to <i>a</i>, a 1 to <i>b</i>. State <i>a</i> has no transition "
    "on 1 and <i>b</i> none on 0, so a wrong guess simply dies. State <i>c</i> means “pair found”; it accepts and "
    "never leaves.",
    alt="four-state NFA: s loops on 0 and 1, s to a on 0, s to b on 1, a to c on 0, b to c on 1, c accepting with a loop"))

# ====================================================================== 4.4 the cycle of conversions
S = SVG(640, 250)
BW, BH = 196, 42
boxes = {"re": (128, 46, "regular expression"), "enfa": (512, 46, "NFA with ε-transitions"),
         "nfa": (512, 192, "NFA"), "dfa": (128, 192, "DFA")}
for key, (x, y, label) in boxes.items():
    S.rect(x - BW / 2, y - BH / 2, BW, BH, rx=10, stroke="currentColor", fill="var(--accent)", fill_opacity=0.08,
           width=1.5)
    S.text(x, y + 1, label, size=15)
# top: expression -> eps-NFA
S.line(228, 46, 410, 46, arrow=True, color="var(--accent)", width=1.8)
S.text(319, 30, "Thompson's algorithm", size=13, weight=600)
S.text(319, 62, "§4.6 · linear size", size=12, color="var(--muted)")
# right: eps-NFA -> NFA
S.line(512, 69, 512, 167, arrow=True, color="var(--accent)", width=1.8)
S.text(500, 110, "remove ε-transitions", size=13, anchor="end", weight=600)
S.text(500, 128, "§4.3 · same states", size=12, color="var(--muted)", anchor="end")
# bottom: NFA -> DFA
S.line(410, 192, 228, 192, arrow=True, color="var(--accent)", width=1.8)
S.text(319, 176, "subset construction", size=13, weight=600)
S.text(319, 208, "§4.5 · up to 2ⁿ states", size=12, color="var(--muted)")
# left: DFA -> expression
S.line(128, 169, 128, 71, arrow=True, color="var(--accent)", width=1.8)
S.text(140, 110, "state elimination", size=13, anchor="start", weight=600)
S.text(140, 128, "§4.8 · length up to Θ(4ⁿ)", size=12, color="var(--muted)", anchor="start")
note(S, 320, 238, "Free in the other direction: a DFA is an NFA, and an NFA is an NFA with ε-transitions.")
save("ch04-kleene-cycle", S.figure(
    "<strong>Kleene's theorem as a cycle of conversions.</strong> Following the arrows turns any of the four "
    "descriptions into any other, so all four describe exactly the regular languages. The grey notes give the size "
    "of the result for an input of size <i>n</i>. The subset construction also accepts ε-transitions directly, and "
    "state elimination works on any NFA, so the right-hand arrow is optional.",
    alt="four boxes in a cycle: regular expression, NFA with epsilon-transitions, NFA, DFA"))

# ====================================================================== 4.6 Thompson's gadgets
A = Automaton(640, 372)
DASH = "4 3"


def sub(x0, yc, x1, label, prefix):
    """A dashed box standing for the NFA of a subexpression; only its start and accepting states are drawn."""
    A.rect(x0, yc - 21, x1 - x0, 42, rx=13, stroke="var(--muted)", dash=DASH, width=1.3)
    math(A, (x0 + x1) / 2, yc + 1, label, size=17, halo=False)
    A.state(prefix + "s", x0 + 21, yc, label="", r=10)
    A.state(prefix + "t", x1 - 21, yc, label="", r=10)


def title(x, y, s):
    math(A, x, y, s, size=14, halo=False)


# base cases
for k, (x, lab, ttl) in enumerate(((52, None, "R = ∅"), (270, "ε", "R = ε"), (488, "a", "R = a"))):
    A.state(f"b{k}s", x, 40, label="s", start="left")
    A.state(f"b{k}t", x + 92, 40, label="t", accepting=True)
    if lab == "ε":
        A.edge(f"b{k}s", f"b{k}t", "ε")
    elif lab:
        A.edge(f"b{k}s", f"b{k}t", "")
        math(A, x + 46, 28, lab)
    title(x + 46, 84, ttl)
A.line(16, 104, 624, 104, color="var(--muted)", width=1, dash="2 4")
# S + T
YC = 196
A.state("us", 44, YC, label="s", start="left")
sub(84, YC - 42, 228, "S", "uS")
sub(84, YC + 42, 228, "T", "uT")
A.state("ut", 270, YC, label="t", accepting=True)
A.edge("us", "uSs", "ε", label_side=1)
A.edge("us", "uTs", "ε", label_side=-1)
A.edge("uSt", "ut", "ε", label_side=1)
A.edge("uTt", "ut", "ε", label_side=-1)
title(156, 284, "R = S + T  (parallel)")
A.line(318, 116, 318, 290, color="var(--muted)", width=1, dash="2 4")
# S*  (the book's gadget: t -> s goes back for another copy, s -> t skips)
A.state("ks", 362, YC, label="s", start="left")
sub(408, YC, 552, "S", "kS")
A.state("kt", 600, YC, label="t", accepting=True)
A.edge("ks", "kSs", "ε")
A.edge("kSt", "kt", "ε")
A.edge("ks", "kt", "ε", bend=-42)      # zero copies of S (below)
A.edge("kt", "ks", "ε", bend=-64)      # another copy of S (above)
title(481, 284, "R = S*")
A.line(16, 302, 624, 302, color="var(--muted)", width=1, dash="2 4")
# ST
sub(196, 340, 336, "S", "cS")
sub(386, 340, 526, "T", "cT")
A.states["cSs"]["start"] = "left"
A.states["cTt"]["accepting"] = True
A.edge("cSt", "cTs", "ε")
title(96, 340, "R = ST  (series)")
save("ch04-thompson-gadgets", A.figure(
    "<strong>Thompson's algorithm, the book's gadgets.</strong> Top: the base cases, each with a start state "
    "<i>s</i> and a different accepting state <i>t</i>. Below: the NFAs for <i>S</i> and <i>T</i> (dashed boxes; only "
    "their start and accepting states are drawn, and these stop being start or accepting) glued with new "
    "ε-transitions — in parallel for <i>S</i> + <i>T</i>; around a loop for <i>S</i>*, where the lower edge skips "
    "<i>S</i> and the upper edge goes back for another copy; in series for <i>ST</i>, which adds no states.",
    alt="Thompson's construction: base cases for the empty set, epsilon and a symbol; gadgets for union, star and concatenation"))

# ====================================================================== 4.6 Thompson's NFA for (0+10*1)*
A = Automaton(640, 304, r=15)
YM, YT, YB = 150, 80, 205
A.state("s", 40, YM, start="left")
A.state("a", 92, YM)
A.state("j", 246, YT)
A.state("k", 396, YT)
for name, x in zip("bcdefghi", range(150, 520, 47)):
    A.state(name, x, YB)
A.state("l", 548, YM)
A.state("m", 604, YM, accepting=True)
A.edge("s", "a", "ε")
A.edge("a", "j", "ε")
A.edge("a", "b", "ε", label_side=-1)
A.edge("j", "k", "0", hi=True)
A.edge("k", "l", "ε")
A.edge("b", "c", "1", hi=True)
A.edge("c", "d", "ε")
A.edge("d", "e", "ε")
A.edge("e", "f", "0", hi=True)
A.edge("f", "g", "ε")
A.edge("g", "h", "ε")
A.edge("h", "i", "1", hi=True)
A.edge("i", "l", "ε", label_side=-1)
A.edge("l", "m", "ε")
A.edge("g", "d", "ε", bend=-24)     # inner star: back for another 0 (above)
A.edge("d", "g", "ε", bend=-24)     # inner star: skip (below)
A.edge("s", "m", "ε", bend=-130)    # outer star: skip (below everything)
A.edge("m", "s", "ε", bend=-112)    # outer star: back for another block (above everything)
save("ch04-thompson-example", A.figure(
    "<strong>Thompson's NFA for (0 + 10*1)*, with the book's state names.</strong> 14 states, 14 ε-transitions and "
    "four symbol transitions (in red). The outer star is <i>s</i>, <i>m</i>; the union is <i>a</i>, <i>l</i>; its "
    "upper branch <i>j</i>→<i>k</i> reads a 0; its lower branch <i>b</i>…<i>i</i> reads a 1, then 0* (the star "
    "<i>d</i>, <i>g</i> around <i>e</i>→<i>f</i>), then a 1.",
    alt="14-state Thompson NFA for (0+10*1)* with states s and a through m"))

# ====================================================================== 4.8 the elimination rule
A = Automaton(600, 196)
A.state("p", 52, 140)
A.state("q", 160, 70, hi=True)
A.state("r", 268, 140)
A.edge("p", "q")
A.edge("q", "r")
A.edge("p", "r")
A.loop("q", "", "above")
math(A, 94, 92, "X")
math(A, 228, 92, "Z")
math(A, 160, 155, "W")
math(A, 160, 12, "Y")
A.text(320, 116, "⟹", size=26)
A.state("P", 382, 140, label="p")
A.state("R", 560, 140, label="r")
A.edge("P", "R")
A.text(471, 124, 'W + XY<tspan dy="-6" font-size="11">*</tspan><tspan dy="6">Z</tspan>', size=15, font=SERIF_IT,
       italic=True, halo=True, raw=True)
note(A, 160, 184, "before: q is still there")
note(A, 471, 184, "after eliminating q")
save("ch04-elimination-rule", A.figure(
    "<strong>Eliminating a state <i>q</i>.</strong> A walk from <i>p</i> to <i>r</i> either avoids <i>q</i> "
    "(label <i>W</i>) or enters <i>q</i>, loops there zero or more times, and leaves (<i>XY</i>*<i>Z</i>). The rule "
    "is applied to <em>every</em> pair <i>p</i>, <i>r</i> of remaining states, including <i>p</i> = <i>r</i>; a "
    "missing edge has label ∅, and a missing loop makes <i>Y</i>* = ∅* = ε.",
    alt="state elimination: p to q labeled X, loop Y at q, q to r labeled Z, p to r labeled W, becomes p to r labeled W + XY*Z"))

# ====================================================================== 4.9 half(L): guess the middle state
S = SVG(640, 286)
HI = "var(--hi)"


def circ(x, y, lab, color="currentColor", accepting=False):
    if accepting:
        S.circle(x, y, 23, stroke=color)
    S.circle(x, y, 19, stroke=color)
    math(S, x, y + 1, lab, color=color, halo=False)


# top: M on ww
S.text(18, 22, "M reads ww:", size=13, anchor="start", color="var(--muted)")
circ(150, 52, "s")
circ(330, 52, "h", HI)
circ(510, 52, "q", accepting=True)
S.line(108, 52, 128, 52, arrow=True)
S.path("M171,52 L307,52", arrow=True, dash="5 4")
S.path("M351,52 L483,52", arrow=True, dash="5 4")
math(S, 240, 38, "w")
math(S, 420, 38, "w")
S.text(330, 88, "the middle state h = δ*(s, w)", size=12, color=HI)
S.text(510, 88, "q ∈ A", size=12, color="var(--muted)")
S.line(16, 108, 624, 108, color="var(--muted)", width=1, dash="2 4")
# bottom: M' reads w once
S.text(18, 130, "M′ reads w once:", size=13, anchor="start", color="var(--muted)")
S.circle(56, 208, 19)
math(S, 56, 209, "s′", halo=False)
S.line(56, 160, 56, 186, arrow=True)
CW, CH = 46, 32
rows_y = (174, 208, 242)


def triple(xc, labels, colors):
    for (y, lab, col) in zip(rows_y, labels, colors):
        S.rect(xc - CW / 2, y - CH / 2, CW, CH, rx=5, stroke="currentColor", width=1.3,
               fill="var(--accent)", fill_opacity=0.07)
        math(S, xc, y + 1, lab, color=col, halo=False)


triple(186, ("s", "h", "h"), ("currentColor", HI, HI))
triple(540, ("h", "h", "q"), (HI, HI, "currentColor"))
S.rect(540 - CW / 2 - 5, rows_y[0] - CH / 2 - 5, CW + 10, 3 * CH + 2 * 2 + 10, rx=8, stroke="currentColor",
       width=1.3)
S.line(77, 208, 158, 208, arrow=True)
math(S, 118, 194, "ε")
for y, txt in zip(rows_y, ("copy 1 of M: from s, reads w", "the guess h never changes",
                           "copy 2 of M: from h, reads w")):
    half_w = len(txt) * 3.3 + 6
    S.path(f"M212,{y} L{362 - half_w:.1f},{y}", dash="5 4")
    S.path(f"M{362 + half_w:.1f},{y} L512,{y}", arrow=True, dash="5 4")
    S.text(362, y, txt, size=12)
note(S, 186, 276, "start: (s, h, h), for every h ∈ Q")
note(S, 540, 276, "accept: first = h, third ∈ A")
save("ch04-half", S.figure(
    "<strong>Lemma 4.5 in a picture.</strong> On input <i>ww</i>, the DFA <i>M</i> passes through some state "
    "<i>h</i> at the midpoint. <i>M</i>′ reads <i>w</i> only once, so it guesses <i>h</i> with an ε-move and "
    "runs two copies of <i>M</i> side by side: one from <i>s</i>, playing the first copy of <i>w</i>, and one from "
    "<i>h</i>, playing the second. It accepts only if the first copy ends exactly at the guessed <i>h</i> and the "
    "second ends in an accepting state.",
    alt="schematic of the half(L) construction: a guessed middle state h, triples (s,h,h) running to (h,h,q)"))
