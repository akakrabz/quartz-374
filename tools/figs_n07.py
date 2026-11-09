#!/usr/bin/env python3
"""Figures for Director's Cut note 7 (string matching). Writes tools/figs/n07-<name>.html; then run tools/assemble.py
on content/4-lecture-notes/07-string-matching.md. Every failure value and transition drawn here is computed below;
tools/checks/n07.py checks the same values independently."""
import math
import os

from figlib import SVG, Automaton, MONO, SERIF_IT

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")
os.makedirs(OUT, exist_ok=True)


def save(name, html):
    with open(os.path.join(OUT, name + ".html"), "w", encoding="utf-8") as f:
        f.write(html + "\n")
    print("wrote", name)


def compute_failure(P):
    m = len(P)
    P1 = " " + P
    fail = [None] * (m + 1)
    j = 0
    for i in range(1, m + 1):
        fail[i] = j
        while j > 0 and P1[i] != P1[j]:
            j = fail[j]
        j += 1
    return fail


def optimize(P, fail):
    P1 = " " + P
    f = list(fail)
    for i in range(2, len(P) + 1):
        if P1[i] == P1[f[i]]:
            f[i] = f[f[i]]
    return f


# =========================================================================== 1. redundant comparisons (HOCUSPOCUS)
T = "HOCUSPOCUSABRABRACADABRA"
P = "ABRACADABRA"
assert T.find(P) + 1 == 14
CW, X0, Y0, RH = 21, 78, 30, 27
S = SVG(X0 + (len(T) + 2) * CW + 6, Y0 + 5 * RH + 26, font_size=14)
# column numbers 10..16 and the text row
for k in range(1, len(T) + 1):
    x = X0 + (k - 1) * CW
    if 9 <= k <= 16:
        S.text(x + CW / 2, Y0 - 13, str(k), size=10.5, color="var(--muted)")
    S.rect(x, Y0, CW, RH - 4, stroke="currentColor", width=0.8, fill="none")
    S.text(x + CW / 2, Y0 + (RH - 4) / 2 + 1, T[k - 1], size=14, font=MONO)
S.text(X0 + len(T) * CW + 12, Y0 + (RH - 4) / 2, "⋯", size=14)
S.text(X0 - 10, Y0 + (RH - 4) / 2, "T", size=15, anchor="end", font=SERIF_IT, italic=True)
ROWS = [(11, 5), (12, 1), (13, 1), (14, None)]  # (shift, position of the mismatch or None for a full match)
for r, (s, mis) in enumerate(ROWS):
    y = Y0 + (r + 1) * RH + 4
    S.text(X0 - 10, y + (RH - 4) / 2, f"s = {s}", size=13, anchor="end")
    for i in range(1, len(P) + 1):
        x = X0 + (s + i - 2) * CW
        if mis is None:
            col, fill, op = "var(--accent2)", "var(--accent2)", 0.16
        elif i < mis:
            col, fill, op = "currentColor", "none", None
        elif i == mis:
            col, fill, op = "var(--hi)", "var(--hi)", 0.14
        else:
            col, fill, op = "var(--muted)", "none", None
        S.rect(x + 1, y, CW - 2, RH - 6, rx=3, stroke=col if (mis is None or i <= mis) else "none",
               fill=fill, fill_opacity=op, width=1.0)
        S.text(x + CW / 2, y + (RH - 6) / 2 + 1, P[i - 1], size=14, font=MONO,
               color="var(--muted)" if (mis is not None and i > mis) else "currentColor")
        if i == mis:
            S.line(x + 4, y + RH - 9, x + CW - 4, y + 3, color="var(--hi)", width=1.6)
# the vertical bar after T[14]: everything to its left has been read
bx = X0 + 14 * CW
S.line(bx, Y0 - 4, bx, Y0 + 5 * RH - 2, color="var(--hi)", width=1.3, dash="4 3")
S.text(bx + 4, Y0 + 5 * RH + 10, "first mismatch: T[15] = B, not C", size=11.5, anchor="start", color="var(--hi)")
html = S.figure(
    "<strong>Shifts that a mismatch already rules out.</strong> At shift 11 the text matches <code>ABRA</code> and "
    "fails at the fifth character (<i>T</i>[15] = <code>B</code>, not <code>C</code>). The characters already read "
    "decide the next two shifts without looking: shifts 12 and 13 put <code>A</code> under <i>T</i>[12] = "
    "<code>B</code> and <i>T</i>[13] = <code>R</code>. Shift 14 is consistent with everything read "
    "(<i>T</i>[14] = <i>P</i>[4] = <code>A</code>), so the comparison can resume at <i>T</i>[15] against "
    "<i>P</i>[2] — and here shift 14 is a match. Grey letters were never compared.",
    alt="the text HOCUSPOCUSABRABRACADABRA with the pattern ABRACADABRA aligned at shifts 11 to 14")
save("n07-shifts", html)

# =========================================================================== 2. the KMP machine for ABRACADABRA
fail = compute_failure(P)
opt = optimize(P, fail)
assert fail[1:] == [0, 1, 1, 1, 2, 1, 2, 1, 2, 3, 4]
assert opt[1:] == [0, 1, 1, 0, 2, 0, 2, 0, 1, 1, 0]
m = len(P)
DX, XS, YM = 43, 34, 80
W = XS * 2 + (m + 1) * DX
A = SVG(W, 196, font_size=14)
xs = {j: XS + j * DX for j in range(0, m + 2)}     # 0 = $, 1..m = pattern nodes, m+1 = !
R = 14
# spread the arrowheads of the arcs that end at the same node
ins_up = {k: sorted(j for j in range(1, m + 1) if fail[j] == k) for k in range(m + 1)}
ins_dn = {k: sorted(j for j in range(1, m + 1) if opt[j] == k) for k in range(m + 1)}


def arc(j, k, above, color, width=1.2):
    x1, x2 = xs[j], xs[k]
    span = j - k
    h = 6 + 6.2 * span
    sgn = -1 if above else 1
    group = (ins_up if above else ins_dn)[k]
    t = group.index(j)
    spread = 0 if len(group) == 1 else (t / (len(group) - 1) - 0.5) * 2 * 9
    ex = x2 + spread
    sx = x1 - 3
    ang_s = math.asin(max(-1, min(1, (sx - x1) / R)))
    ang_e = math.asin(max(-1, min(1, (ex - x2) / (R + 2.5))))
    sy = YM + sgn * R * math.cos(ang_s)
    ey = YM + sgn * (R + 2.5) * math.cos(ang_e)
    cx, cy = (sx + ex) / 2, YM + sgn * (R + 2 * h)
    A.path(f"M{sx:.1f},{sy:.1f} Q{cx:.1f},{cy:.1f} {ex:.1f},{ey:.1f}", color=color, width=width, arrow=True)


for j in range(1, m + 1):
    arc(j, fail[j], True, "var(--accent)")
    arc(j, opt[j], False, "var(--accent2)")
for j in range(0, m + 1):
    A.line(xs[j] + R + 1, YM, xs[j + 1] - R - 3, YM, width=2.4, arrow=True)
for j in range(0, m + 2):
    lab = "&#36;" if j == 0 else ("!" if j == m + 1 else P[j - 1])
    A.circle(xs[j], YM, R, width=1.6 if 1 <= j <= m else 2.2)
    A.text(xs[j], YM + 1, lab, size=14, font=MONO, weight="600" if j in (0, m + 1) else None, raw=True)
A.text(W - 8, 14, "fail (unoptimized)", size=12.5, anchor="end", color="var(--accent)", weight="600")
A.text(W - 8, 186, "optimized fail", size=12.5, anchor="end", color="var(--accent2)", weight="600")
html = A.figure(
    "<strong>The string-matching machine for <code>ABRACADABRA</code>.</strong> Thick arrows are success edges: on "
    "a match, move right and read the next text character. Above the row, the failure edges <i>j</i> → "
    "<i>fail</i>[<i>j</i>] (0 1 1 1 2 1 2 1 2 3 4); below, the optimized ones (0 1 1 0 2 0 2 0 1 1 0), which skip "
    "every node carrying the same letter as <i>j</i>. A failure edge reads no input. The start node "
    "<code>&#36;</code> is node 0 and always succeeds; node <i>j</i> holds <i>P</i>[<i>j</i>]; reaching the final "
    "node <code>!</code> means the pattern was found.",
    alt="thirteen nodes in a row, a start node, the letters A B R A C A D A B R A and a final node, with "
        "failure arcs above (unoptimized) and below (optimized)")
save("n07-kmp-machine", html)

# =========================================================================== 3. the KMP DFA for ABAB over {A, B}
P2 = "ABAB"
f2 = compute_failure(P2)


def step(k, a):
    while True:
        if k < len(P2) and P2[k] == a:
            return k + 1
        if k == 0:
            return 0
        k = f2[k + 1] - 1


D = {(k, a): (4 if k == 4 else step(k, a)) for k in range(5) for a in "AB"}
assert [(D[(k, "A")], D[(k, "B")]) for k in range(5)] == [(1, 0), (1, 2), (3, 0), (1, 4), (4, 4)]
M = Automaton(560, 190, r=19)
names = ["ε", "A", "AB", "ABA", "ABAB"]
for k in range(5):
    M.state(k, 50 + k * 112, 92, label=names[k], accepting=(k == 4), start="left" if k == 0 else None,
            shape="circle" if k < 2 else "rounded", w=[0, 0, 40, 50, 60][k], italic=(k == 0),
            font=None if k == 0 else MONO)
M.edge(0, 1, "A")
M.edge(1, 2, "B")
M.edge(2, 3, "A")
M.edge(3, 4, "B")
M.loop(0, "B", 90)
M.loop(1, "A", 128, size=0.8)
M.loop(4, "A,B", "above")
M.edge(2, 0, "B", bend=26, label_dist=9)
M.edge(3, 1, "A", bend=-30, label_dist=9)
html = M.figure(
    "<strong>The same idea as a DFA: strings containing <code>ABAB</code>.</strong> Each state is named by the "
    "longest suffix of the input read so far that is a prefix of the pattern; state <i>k</i> is the prefix of "
    "length <i>k</i>. "
    "A match moves right; a mismatch from <i>k</i> follows failure edges until some state can read the symbol — "
    "<i>fail</i> = 0 1 1 2 gives <code>AB</code> −<code>B</code>→ ε and <code>ABA</code> −<code>A</code>→ <code>A</code>. "
    "The last state absorbs. The machine has "
    "<i>m</i> + 1 = 5 states and is minimal.",
    alt="a five-state DFA over A and B for strings containing ABAB")
save("n07-kmp-dfa", html)
