#!/usr/bin/env python3
"""Figures for the toolkit pages (content/0-toolkit/03–05). Writes tools/figs/tk-<name>.html; then run
tools/assemble.py on the toolkit pages."""
import os
from figlib import SVG, MONO, SERIF_IT, SANS, esc

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")


def save(name, html):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name + ".html"), "w", encoding="utf-8") as f:
        f.write(html + "\n")
    print("wrote", name)


def rich(S, x, y, parts, size=13, anchor="start"):
    """One line of mixed text. parts: (text, kind[, color]); kind in sf (sans), cls (sans bold), it (serif italic),
    rm (serif upright), mono, sup (italic superscript), model (sans, lighter), note (sans italic, lighter)."""
    out = []
    for p in parts:
        txt, kind = p[0], p[1]
        fill = f' fill="{p[2]}"' if len(p) > 2 else ""
        t = esc(txt)
        if kind == "sf":
            st = f"font-family:{SANS}"
        elif kind == "cls":
            st = f"font-family:{SANS};font-weight:700;font-size:{size + 1}px"
        elif kind == "it":
            st = f"font-family:{SERIF_IT};font-style:italic;font-size:{size + 1}px"
        elif kind == "rm":
            st = f"font-family:{SERIF_IT};font-size:{size + 1}px"
        elif kind == "mono":
            st = f"font-family:{MONO};font-size:{size - 1}px"
        elif kind == "model":
            st = f"font-family:{SANS};fill-opacity:0.72"
        elif kind == "note":
            st = f"font-family:{SANS};font-style:italic;fill-opacity:0.62"
        elif kind == "sup":
            out.append(f'<tspan{fill} style="font-family:{SERIF_IT};font-style:italic;font-size:{size - 3}px" '
                       f'baseline-shift="super">{t}</tspan>')
            continue
        else:
            raise ValueError(kind)
        out.append(f'<tspan{fill} style="{st}">{t}</tspan>')
    S.add(f'<text x="{x}" y="{y}" text-anchor="{anchor}" dominant-baseline="central" fill="currentColor" '
          f'style="font-size:{size}px;font-family:{SANS};">{"".join(out)}</text>')


HI = "var(--hi)"
ACC = "var(--accent)"
MUT = "var(--muted)"


def lang_0n1n(color=None, third=False):
    c = (color,) if color else ()
    out = [("{", "rm") + c, ("0", "mono") + c, ("n", "sup") + c, ("1", "mono") + c, ("n", "sup") + c]
    if third:
        out += [("0", "mono") + c, ("n", "sup") + c]
    return out + [("}", "rm") + c]


def hierarchy():
    W, H = 640, 316
    S = SVG(W, H)
    bands = [
        # (class name, model, note at the right, example line)
        ("all languages", "", "not acceptable: Theorem 9 · Lemma 5 · Lemma 17",
         [("SelfDiverge", "sf", HI), (", NeverAccept, Diverge, {⟨", "sf"), ("M", "it"), ("⟩ : Accept(", "sf"),
          ("M", "it"), (") is finite}", "sf")]),
        ("acceptable", "  Turing machines", "undecidable: diagonalization · reduction · Rice",
         [("Halt", "sf", HI), (", Accept, SelfReject, SelfAccept, Post's correspondence problem", "sf")]),
        ("decidable", "  Turing machines that halt on every input", "not context-free: beyond this course",
         lang_0n1n(HI, third=True) + [(", {", "sf"), ("0", "mono"), ("p", "sup"), (" : ", "sf"), ("p", "it"),
                                      (" prime}, {", "sf"), ("w", "it"), ("#", "mono"), ("w", "it"), ("}", "sf")]),
        ("context-free", "  grammars, recursive automata", "not regular: an infinite fooling set",
         lang_0n1n(HI) + [(", palindromes, balanced parentheses, #(", "sf"), ("0", "mono"), (", ", "sf"),
                          ("w", "it"), (") = #(", "sf"), ("1", "mono"), (", ", "sf"), ("w", "it"), (")", "sf")]),
        ("regular", "  regular expressions, DFAs, NFAs", "",
         [("every finite language, ", "sf"), ("(0+1)*00", "mono"), (", binary multiples of 5", "sf")]),
    ]
    top, dy, side, bot = 6, 52, 16, 10
    for k, (name, model, note, ex) in enumerate(bands):
        x0, x1 = 6 + side * k, W - 6 - side * k
        y0, y1 = top + dy * k, H - 6 - bot * k
        if k == 0:
            S.rect(x0, y0, x1 - x0, y1 - y0, rx=12, stroke=MUT, width=1.2)
        else:
            S.rect(x0, y0, x1 - x0, y1 - y0, rx=12, stroke=ACC, fill=ACC, fill_opacity=0.055, width=1.4)
        rich(S, x0 + 12, y0 + 17, [(name, "cls", ACC if k else "currentColor")] +
             ([(model, "model")] if model else []), size=13)
        if note:
            rich(S, x1 - 12, y0 + 17, [(note, "note")], size=12, anchor="end")
        rich(S, x0 + 12, y0 + 37, ex, size=13)
    save("tk-hierarchy", S.figure(
        "<strong>Five nested classes.</strong> Each band holds languages that belong to its class but not to the "
        "class inside it; the first language of each band (in red) is the standard witness that the inclusion is "
        "strict. The note at the right of a band names the tools that prove a language lies outside the inner "
        "class. The models that define each class are next to its name.",
        alt="five nested rounded rectangles: regular inside context-free inside decidable inside acceptable inside "
            "all languages, each with example languages"))


def main():
    hierarchy()


if __name__ == "__main__":
    main()
