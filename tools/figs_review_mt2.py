#!/usr/bin/env python3
"""Figures for content/0-toolkit/08-review-algorithms.md (the Midterm 2 review).
Writes tools/figs/rmt2-<name>.html; then run tools/assemble.py on that page only.

rmt2-drill-dag: the dag of drill group D (vertices a..g, 9 edges). The graph is drawn without any answer on it;
tools/checks/review_mt2.py rebuilds the same edge list from this file's EDGES and checks every drill answer."""
import os

from figlib import Automaton

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")
os.makedirs(OUT, exist_ok=True)

# the drill dag (also imported by the check script)
EDGES = "ab ad ae bc be cf de ef gd".split()
POS = {"a": (60, 120), "b": (190, 45), "c": (340, 45), "e": (340, 120), "f": (470, 120),
       "d": (190, 195), "g": (60, 195)}


def save(name, html):
    with open(os.path.join(OUT, name + ".html"), "w", encoding="utf-8") as f:
        f.write(html + "\n")
    print("wrote", name)


def drill_dag():
    A = Automaton(530, 240, r=18)
    for v, (x, y) in POS.items():
        A.state(v, x, y)
    for e in EDGES:
        A.edge(e[0], e[1])
    return A.figure(
        "<strong>The drill graph.</strong> A dag with 7 vertices and 9 edges: "
        "a→b, a→d, a→e, b→c, b→e, c→f, d→e, e→f, g→d. Every adjacency list is in alphabetical order, "
        "and DFSAll tries the start vertices in alphabetical order.",
        alt="a directed acyclic graph on the vertices a to g")


if __name__ == "__main__":
    save("rmt2-drill-dag", drill_dag())
