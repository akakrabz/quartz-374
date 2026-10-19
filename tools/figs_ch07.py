#!/usr/bin/env python3
"""Figures for Chapter 7 (undecidability). Writes tools/figs/<name>.html; then run tools/assemble.py.

The data behind the figures (the diagonal table, the never-left machine and its run) live at module level so that
tools/checks/ch07.py can import and verify them; the figures are written only when the script is run directly."""
import os
from figlib import SVG, Tape, MONO, SERIF_IT, SANS, esc

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")

# ---------------------------------------------------------------- data checked by tools/checks/ch07.py
# diagonal table: entry [i][j] = outcome of machine M_(i+1) on input <M_(j+1)>
DIAG = [
    ["acc", "rej", "∞", "acc", "rej", "acc"],
    ["rej", "rej", "acc", "∞", "acc", "rej"],
    ["∞", "acc", "∞", "rej", "rej", "acc"],
    ["acc", "acc", "rej", "rej", "∞", "rej"],
    ["rej", "∞", "acc", "acc", "acc", "∞"],
    ["∞", "rej", "rej", "acc", "∞", "rej"],
]
SR_ROW = ["rej", "acc", "rej", "acc", "rej", "acc"]   # what a decider for SelfReject must answer on <M_j>

# a machine that never moves left (Theorem 19 figure): states start, p, q, r
BLANK = "□"
NL_DELTA = {
    ("start", "0"): ("start", "0", +1), ("start", "1"): ("p", "1", +1), ("start", BLANK): ("q", BLANK, +1),
    ("p", "0"): ("start", "0", +1), ("p", "1"): ("p", "1", +1), ("p", BLANK): ("q", BLANK, +1),
    ("q", BLANK): ("r", BLANK, +1), ("r", BLANK): ("q", BLANK, +1),
}
NL_INPUT = "011"
NL_STATES = ["start", "start", "p", "p", "q", "r", "q", "r"]   # state in which the head reads cells 0, 1, 2, ...


def save(name, html):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name + ".html"), "w", encoding="utf-8") as f:
        f.write(html + "\n")
    print("wrote", name)


def rich(S, x, y, parts, size=14, anchor="middle", color="currentColor", weight=None):
    """One line of mixed text: parts are (text, kind), kind in sf (sans, for named languages and machines),
    it (serif italic), rm (serif upright), mono, sub (italic subscript), subrm (upright subscript)."""
    out = []
    for txt, kind in parts:
        t = esc(txt)
        if kind == "sf":
            out.append(f'<tspan style="font-family:{SANS}">{t}</tspan>')
        elif kind == "it":
            out.append(f'<tspan style="font-family:{SERIF_IT};font-style:italic">{t}</tspan>')
        elif kind == "rm":
            out.append(f'<tspan style="font-family:{SERIF_IT}">{t}</tspan>')
        elif kind == "mono":
            out.append(f'<tspan style="font-family:{MONO};font-size:{size - 1}px">{t}</tspan>')
        elif kind == "sup":
            out.append(f'<tspan style="font-family:{SERIF_IT};font-style:italic;font-size:{size - 4}px" baseline-shift="super">{t}</tspan>')
        elif kind in ("sub", "subrm"):
            it = "font-style:italic;" if kind == "sub" else ""
            out.append(f'<tspan style="font-family:{SERIF_IT};{it}font-size:{size - 4}px" baseline-shift="sub">{t}</tspan>')
        else:
            raise ValueError(kind)
    style_w = f"font-weight:{weight};" if weight else ""
    S.add(f'<text x="{x}" y="{y}" text-anchor="{anchor}" dominant-baseline="central" fill="{color}" '
          f'style="font-size:{size}px;font-family:{SANS};{style_w}">{"".join(out)}</text>')


def lang(name, arg="M"):
    """[(name, sf), ('(', rm), (arg, it), (')', rm)] — e.g. Accept(M)."""
    return [(name, "sf"), ("(", "rm"), (arg, "it"), (")", "rm")]


def brace(S, x1, x2, y, color="currentColor", up=True, h=6):
    d = -h if up else h
    S.path(f"M{x1},{y} L{x1},{y + d} L{x2},{y + d} L{x2},{y}", color=color, width=1.3)


def main():
    # ------------------------------------------------------------ 7.1 the four languages of a machine
    S = SVG(640, 176)
    x0, x1, x2, x3 = 150, 320, 460, 620
    y1, h = 40, 34
    S.rect(x0, y1, x1 - x0, h, fill="var(--accent)", fill_opacity=0.16, stroke="currentColor", width=1.3)
    S.rect(x1, y1, x2 - x1, h, fill="var(--accent2)", fill_opacity=0.16, stroke="currentColor", width=1.3)
    S.rect(x2, y1, x3 - x2, h, fill="var(--muted)", fill_opacity=0.16, stroke="currentColor", width=1.3, dash="5 3")
    rich(S, (x0 + x1) / 2, y1 + h / 2, lang("Accept"))
    rich(S, (x1 + x2) / 2, y1 + h / 2, lang("Reject"))
    rich(S, (x2 + x3) / 2, y1 + h / 2, lang("Diverge"))
    brace(S, x0 + 2, x2 - 2, y1 - 5)
    rich(S, (x0 + x2) / 2, y1 - 22, lang("Halt"), size=13)
    rich(S, x0 - 14, y1 + h / 2, [("any machine ", "sf"), ("M", "it")], size=13, anchor="end")
    y2 = 110
    xm = 400
    S.rect(x0, y2, xm - x0, h, fill="var(--accent)", fill_opacity=0.16, stroke="currentColor", width=1.3)
    S.rect(xm, y2, x3 - xm, h, fill="var(--accent2)", fill_opacity=0.16, stroke="currentColor", width=1.3)
    rich(S, (x0 + xm) / 2, y2 + h / 2, lang("Accept") + [(" = ", "rm"), ("L", "it")])
    rich(S, (xm + x3) / 2, y2 + h / 2, lang("Reject") + [(" = Σ* ∖ ", "rm"), ("L", "it")])
    rich(S, x0 - 14, y2 + h / 2, [("M", "it"), (" decides ", "sf"), ("L", "it")], size=13, anchor="end")
    rich(S, (x0 + x3) / 2, y2 + h + 18, lang("Diverge") + [(" = ∅", "rm"), (": every input gets an answer", "sf")],
         size=13, color="var(--muted)")
    save("ch07-four-languages", S.figure(
        "<strong>Where the inputs go.</strong> Every input string lands in exactly one of Accept(<i>M</i>), "
        "Reject(<i>M</i>) and Diverge(<i>M</i>); the first two together form Halt(<i>M</i>). A machine that "
        "<em>accepts</em> <i>L</i> only has to get the first set right. A machine that <em>decides</em> <i>L</i> "
        "has nothing in the third set, so it rejects exactly the strings not in <i>L</i>.",
        alt="two bars: the inputs of an arbitrary machine split into Accept, Reject and Diverge; the inputs of a "
            "decider split into Accept = L and Reject = complement of L"))

    # ------------------------------------------------------------ 7.5 the diagonal table
    S = SVG(560, 336)
    n = len(DIAG)
    cw, ch = 60, 28
    gx, gy = 118, 46          # top-left of the grid
    for j in range(n):
        rich(S, gx + j * cw + cw / 2, gy - 15, [("⟨", "rm"), ("M", "it"), (str(j + 1), "subrm"), ("⟩", "rm")], size=14)
    S.text(gx + n * cw + 20, gy - 15, "⋯", size=15)
    rich(S, gx + n * cw / 2, gy - 36, [("input", "sf")], size=12, color="var(--muted)")
    for i in range(n):
        y = gy + i * ch
        rich(S, gx - 12, y + ch / 2, [("M", "it"), (str(i + 1), "subrm")], size=14, anchor="end")
        for j in range(n):
            x = gx + j * cw
            diag = i == j
            S.rect(x, y, cw, ch, stroke="var(--muted)", width=1,
                   fill="var(--hi)" if diag else "none", fill_opacity=0.12 if diag else None)
            S.text(x + cw / 2, y + ch / 2 + 1, DIAG[i][j], size=13, font=MONO,
                   color="var(--hi)" if diag else "currentColor", weight=600 if diag else None)
        S.text(gx + n * cw + 20, y + ch / 2, "⋯", size=15, color="var(--muted)")
    for j in range(n):
        S.text(gx + j * cw + cw / 2, gy + n * ch + 11, "⋮", size=14, color="var(--muted)")
    S.text(gx - 22, gy + n * ch / 2, "", size=12)
    # the row a decider SR for SelfReject would need
    ys = gy + n * ch + 34
    for j in range(n):
        x = gx + j * cw
        S.rect(x, ys, cw, ch, stroke="var(--hi)", width=1.6)
        S.text(x + cw / 2, ys + ch / 2 + 1, SR_ROW[j], size=13, font=MONO, color="var(--hi)", weight=600)
    rich(S, gx - 12, ys + ch / 2, [("SR", "sf")], size=14, anchor="end", color="var(--hi)")
    rich(S, gx + n * cw / 2, ys + ch + 18,
         [("flip the diagonal: ", "sf"), ("rej", "mono"), (" → ", "rm"), ("acc", "mono"), ("; ", "sf"),
          ("acc", "mono"), (" or ", "sf"), ("∞", "mono"), (" → ", "rm"), ("rej", "mono")],
         size=13, color="var(--hi)")
    rich(S, gx + n * cw / 2, ys + ch + 40,
         [("so the row ", "sf"), ("SR", "sf"), (" differs from row ", "sf"), ("M", "it"), ("i", "sub"),
          (" in column ", "sf"), ("i", "it"), (", for every ", "sf"), ("i", "it")], size=13, color="var(--muted)")
    save("ch07-diagonal-table", S.figure(
        "<strong>Diagonalization as a table.</strong> Row <i>M<sub>i</sub></i> lists what machine <i>M<sub>i</sub></i> "
        "does on each machine encoding: accept, reject, or run forever (∞). A decider SR for SelfReject would need the "
        "red row at the bottom: it must accept ⟨<i>M<sub>j</sub></i>⟩ exactly when the diagonal entry is <tt>rej</tt>. "
        "That row disagrees with every row of the table on the diagonal — yet every Turing machine, SR included, "
        "is one of the rows.",
        alt="six by six table of outcomes acc, rej, infinity with the diagonal highlighted, and below it the flipped "
            "diagonal as the row a SelfReject decider would need"))

    # ------------------------------------------------------------ 7.8 the class picture
    S = SVG(620, 316)
    S.rect(8, 8, 604, 300, rx=10, stroke="var(--muted)", width=1.2)
    S.text(22, 24, "all languages", size=12, anchor="start", color="var(--muted)")
    cxl, cxr, cy, rx, ry = 235, 385, 160, 185, 108
    S.add(f'<ellipse cx="{cxl}" cy="{cy}" rx="{rx}" ry="{ry}" fill="var(--accent)" fill-opacity="0.07" '
          f'stroke="var(--accent)" stroke-width="1.6"/>')
    S.add(f'<ellipse cx="{cxr}" cy="{cy}" rx="{rx}" ry="{ry}" fill="var(--accent2)" fill-opacity="0.07" '
          f'stroke="var(--accent2)" stroke-width="1.6"/>')
    S.text(120, 40, "acceptable", size=15, color="var(--accent)", weight=700)
    S.text(500, 34, "co-acceptable", size=15, color="var(--accent2)", weight=700)
    S.text(500, 50, "(complement acceptable)", size=11, color="var(--accent2)")
    S.text(310, 92, "decidable", size=15, weight=700)
    S.text(310, 109, "= both (Lemma 5)", size=11, color="var(--muted)")
    left = ["SelfReject", "SelfAccept", "SelfHalt", "Accept, Halt", "LeftThree"]
    right = ["SelfDiverge", "Diverge", "NeverAccept"]
    for k, s_ in enumerate(left):
        S.text(130, 114 + 22 * k, s_, size=14)
    for k, s_ in enumerate(right):
        S.text(490, 134 + 26 * k, s_, size=14)
    rich(S, 310, 134, [("regular languages", "sf")], size=14)
    rich(S, 310, 157, [("{", "rm"), ("0", "mono"), ("n", "sup"), ("1", "mono"), ("n", "sup"), ("0", "mono"),
                       ("n", "sup"), ("}", "rm")], size=15)
    S.text(310, 180, "NeverLeft", size=14)
    S.text(310, 203, "ThisIsSparta", size=14)
    rich(S, 310, 290, [("neither: ", "sf"), ("{⟨", "rm"), ("M", "it"), ("⟩ : ", "rm")] + lang("Accept") +
         [(" is finite}, ", "sf"), ("{⟨", "rm"), ("M", "it"), ("⟩ : ", "rm")] + lang("Accept") +
         [(" is regular}", "sf")], size=13)
    save("ch07-classes", S.figure(
        "<strong>Acceptable, co-acceptable, decidable.</strong> A language is decidable exactly when both it and its "
        "complement are acceptable (Lemma 5). SelfReject, SelfAccept, SelfHalt, Accept, Halt and LeftThree sit in the "
        "left lune: acceptable but undecidable, so their complements (such as SelfDiverge and Diverge) are not "
        "acceptable. NeverAccept is co-acceptable but not acceptable. Some languages are neither, such as the two at "
        "the bottom (Corollary 18).",
        alt="Venn diagram of acceptable and co-acceptable languages; their intersection is the decidable languages; "
            "example languages in each region"))

    # ------------------------------------------------------------ 7.9 a reduction as nested boxes
    S = SVG(660, 214)
    S.rect(74, 26, 520, 172, rx=8, stroke="currentColor", width=1.8)
    S.text(88, 44, "DecideAccept", size=15, anchor="start", weight=700)
    S.line(12, 112, 72, 112, arrow=True)
    rich(S, 40, 98, [("⟨", "rm"), ("M", "it"), (", ", "rm"), ("w", "it"), ("⟩", "rm")], size=14)
    # build <M'>
    S.rect(96, 60, 236, 124, rx=6, stroke="currentColor", width=1.3)
    rich(S, 214, 76, [("write down ", "sf"), ("⟨", "rm"), ("M′", "it"), ("⟩", "rm")], size=13)
    S.rect(110, 90, 208, 84, rx=5, stroke="var(--muted)", width=1.3, dash="5 4")
    rich(S, 122, 106, [("M′", "it"), ("(", "rm"), ("x", "it"), ("):", "rm")], size=14, anchor="start")
    rich(S, 138, 126, [("ignore ", "sf"), ("x", "it")], size=13, anchor="start")
    rich(S, 138, 144, [("run ", "sf"), ("M", "it"), (" on ", "sf"), ("w", "it")], size=13, anchor="start")
    rich(S, 138, 162, [("then … (depends on ", "sf"), ("L", "it"), (")", "sf")], size=13, anchor="start")
    S.text(306, 102, "never run", size=11, anchor="end", color="var(--muted)")
    # arrow <M'> to DecideL
    S.line(334, 120, 398, 120, arrow=True)
    rich(S, 366, 106, [("⟨", "rm"), ("M′", "it"), ("⟩", "rm")], size=14)
    S.rect(400, 80, 128, 80, rx=6, stroke="var(--accent)", fill="var(--accent)", fill_opacity=0.12, width=1.6)
    S.text(464, 112, "DecideL", size=15, weight=700, color="var(--accent)")
    S.text(464, 134, "(hypothetical)", size=11, color="var(--accent)")
    S.line(528, 100, 648, 100, arrow=True)
    S.line(528, 140, 648, 140, arrow=True)
    S.text(620, 88, "accept", size=13)
    S.text(620, 154, "reject", size=13)
    save("ch07-reduction", S.figure(
        "<strong>A reduction from Accept to <i>L</i>.</strong> DecideAccept turns its input ⟨<i>M</i>, <i>w</i>⟩ into "
        "the encoding of a new machine <i>M′</i> and returns whatever the hypothetical decider DecideL says about "
        "⟨<i>M′</i>⟩. Writing down ⟨<i>M′</i>⟩ always terminates, because <i>M′</i> is never run (dashed box). If "
        "⟨<i>M′</i>⟩ ∈ <i>L</i> exactly when <i>M</i> accepts <i>w</i>, then DecideAccept decides Accept — "
        "impossible, so DecideL cannot exist.",
        alt="box DecideAccept containing a box that writes down the encoding of M prime and a box DecideL; the "
            "encoding flows into DecideL, whose accept and reject are DecideAccept's answers"))

    # ------------------------------------------------------------ 7.13 a machine that never moves left
    T = Tape(560, 186, font_size=15)
    cell, tx, ty = 44, 70, 70
    syms = list(NL_INPUT) + [BLANK] * (len(NL_STATES) - len(NL_INPUT))
    T.cells(tx, ty, syms, cell=cell, dots=True)
    for i, q in enumerate(NL_STATES):
        hot = i in (4, 6)
        T.text(tx + i * cell + cell / 2, ty - 16, q, size=14, font=SERIF_IT, italic=True,
               color="var(--hi)" if hot else "currentColor")
    for i in range(len(NL_STATES) - 1):
        xa, xb = tx + i * cell + cell / 2 + 9, tx + (i + 1) * cell + cell / 2 - 9
        T.path(f"M{xa},{ty - 30} Q{(xa + xb) / 2},{ty - 42} {xb},{ty - 30}", width=1.1, arrow=True,
               color="var(--muted)")
    for i in (4, 6):
        T.rect(tx + i * cell + 3, ty + 3, cell - 6, cell - 6, stroke="var(--hi)", width=1.6)
    xq1, xq2 = tx + 4 * cell + cell / 2, tx + 6 * cell + cell / 2
    T.path(f"M{xq1},{ty + cell + 8} Q{(xq1 + xq2) / 2},{ty + cell + 34} {xq2},{ty + cell + 8}", color="var(--hi)",
           width=1.4)
    T.text((xq1 + xq2) / 2, ty + cell + 40, "same state, same symbol ⇒ the run repeats forever", size=12,
           color="var(--hi)")
    brace(T, tx + 3, tx + 3 * cell - 3, ty + cell + 6, up=False)
    rich(T, tx + 1.5 * cell, ty + cell + 26, [("input ", "sf"), ("w", "it")], size=13)
    T.text(tx + 4 * cell, ty - 56, "states while reading each cell (the head moves right every step)", size=12,
           color="var(--muted)")
    save("ch07-neverleft", T.figure(
        "<strong>Why NeverLeft is decidable.</strong> A machine that never moves left reads each cell once. Past "
        "the input it reads only blanks, so each move depends on its state alone. Here the state <i>q</i> "
        "repeats on a blank, and from then on the run cycles <i>q</i>, <i>r</i>, <i>q</i>, <i>r</i>, … to the right "
        "forever. Among |<i>Q</i>| + 1 blank reads some state must repeat, so a simulation can stop there.",
        alt="tape 0 1 1 followed by blanks, with the state at each cell: start, start, p, p, q, r, q, r; the two "
            "q's are highlighted"))


if __name__ == "__main__":
    main()
