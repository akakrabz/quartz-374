#!/usr/bin/env python3
"""Checks for every concrete claim on content/2-algorithms/12-np-hardness.md and the concept pages np-hardness,
polynomial-time-reductions and satisfiability (plus the Chapter 12 lines added to cook-levin-theorem and subset-sum).

Every reduction on the page is implemented exactly as the page states it, and checked by brute force on all (or many
random) small instances: YES maps to YES and NO maps to NO.
  * CircuitSat -> Sat (transcription) and CircuitSat -> 3Sat (binarize, transcribe, CNF per gate, pad to 3 literals):
    the three gate rules and the two padding rules are checked exhaustively; random circuits are equisatisfiable with
    their formulas (brute force over inputs, a small DPLL solver validated against brute force); certificates are
    transformed both ways. The book's circuit (Figures 12.2/12.5), its printed 46-clause 3CNF formula (transcribed
    from the PDF) and the page's small NAND example are recomputed.
  * 3Sat -> MaxIndSet (one triangle per clause, negation edges): max independent set = #clauses iff satisfiable.
  * IndependentSet / Clique / VertexCover: complement relations on every graph with at most 5 vertices + random ones.
  * 3Sat -> 3Color (truth, variable and clause gadgets): 3-colorable iff satisfiable; the half-gadget and the clause
    gadget are checked exhaustively.
  * VertexCover -> DirectedHamCycle (edge gadgets, vertex chains, k cover vertices): Hamiltonian iff a vertex cover of
    size at most k exists, whenever k is at most the number of non-isolated vertices; the edge case outside that
    range fails as the page says.
  * 3Sat -> DirectedHamCycle: the book's construction (both readings: rows (i,0..2k) as in the text, rows of 2k
    vertices as in Figures 12.19-12.20) has Hamiltonian cycles for unsatisfiable formulas (random small CNFs and the
    page's eight-clause 3CNF counterexample, whose spliced cycle is checked edge by edge); the repaired construction on
    the page (spacer vertices and hub vertices) is correct on every random instance.
  * VertexCover -> SubsetSum (base-4 digits): no carries, YES iff YES on random graphs; the book's example numbers.
Then every number in the page's examples and figures is recomputed and compared with the page text."""
import itertools
import os
import random
import re
import sys

sys.setrecursionlimit(20000)
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
PAGE = os.path.join(ROOT, "content", "2-algorithms", "12-np-hardness.md")
CONCEPTS = os.path.join(ROOT, "content", "concepts")
FIGS = os.path.join(HERE, "..", "figs")
FAIL = []
random.seed(12374)


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAIL.append(name)


def read(path):
    return open(path, encoding="utf-8").read()


# =====================================================================================================
# Boolean formulas. A literal is (variable, positive?); a clause is a list of literals; a CNF is a list of clauses.
def lit(s):
    """'a' -> ('a', True); '~a' -> ('a', False)."""
    return (s[1:], False) if s.startswith("~") else (s, True)


def C(*ss):
    return [lit(s) for s in ss]


def variables(cnf):
    out = []
    for cl in cnf:
        for v, _ in cl:
            if v not in out:
                out.append(v)
    return out


def holds(cnf, asg):
    return all(any(asg[v] == p for v, p in cl) for cl in cnf)


def brute_sat(cnf, fixed=None):
    vs = [v for v in variables(cnf) if not fixed or v not in fixed]
    for bits in itertools.product([False, True], repeat=len(vs)):
        asg = dict(zip(vs, bits))
        if fixed:
            asg.update(fixed)
        if holds(cnf, asg):
            return asg
    return None


def dpll(cnf, asg=None):
    """Tiny DPLL with unit propagation; returns a satisfying assignment (dict) or None."""
    asg = dict(asg or {})
    cls = [list(c) for c in cnf]
    while True:
        new, unit = [], None
        for cl in cls:
            if any(v in asg and asg[v] == p for v, p in cl):
                continue
            rest = [(v, p) for v, p in cl if v not in asg]
            if not rest:
                return None
            if len(rest) == 1 and unit is None:
                unit = rest[0]
            new.append(rest)
        cls = new
        if not cls:
            for v in variables(cnf):
                asg.setdefault(v, False)
            return asg
        if unit is None:
            break
        asg[unit[0]] = unit[1]
    v = cls[0][0][0]
    for val in (True, False):
        r = dpll(cls, {**asg, v: val})
        if r is not None:
            for w in variables(cnf):
                r.setdefault(w, False)
            return r
    return None


def random_cnf(n, k, lo=3, hi=3):
    vs = [f"v{i}" for i in range(1, n + 1)]
    out = []
    for _ in range(k):
        size = random.randint(lo, hi)
        chosen = random.sample(vs, min(size, n))
        out.append([(v, random.random() < 0.5) for v in chosen])
    return out


# --- validate the SAT solver
bad = 0
for _ in range(1500):
    f = random_cnf(random.randint(1, 5), random.randint(1, 9), 1, 3)
    a, b = brute_sat(f), dpll(f)
    if (a is None) != (b is None) or (b is not None and not holds(f, b)):
        bad += 1
check("DPLL helper agrees with brute force on 1500 random CNF formulas", bad == 0)

# =====================================================================================================
# 12.5-12.6  Circuits. A circuit: inputs (list), gates [(out, op, [ins])] in topological order, output wire.
OPS = {"and": lambda xs: all(xs), "or": lambda xs: any(xs), "not": lambda xs: not xs[0]}


def evaluate(inputs, gates, out, xs):
    val = dict(zip(inputs, xs))
    for w, op, ins in gates:
        val[w] = OPS[op]([val[i] for i in ins])
    return val[out], val


def binarize(gates, fresh):
    """Replace each and/or gate with k > 2 inputs by a left-deep chain of k-1 binary gates (the last one keeps the
    gate's output name); `fresh` yields new wire names. The book allows any binary tree."""
    out = []
    for w, op, ins in gates:
        if op != "not" and len(ins) > 2:
            cur = ins[0]
            for j in range(1, len(ins)):
                nw = w if j == len(ins) - 1 else next(fresh)
                out.append((nw, op, [cur, ins[j]]))
                cur = nw
        else:
            out.append((w, op, ins))
    return out


def transcribe_sat(gates, out):
    """Phi of 12.5: one equation per gate, and the output wire. Returned as a predicate on assignments."""
    def phi(asg):
        return all(asg[w] == OPS[op]([asg[i] for i in ins]) for w, op, ins in gates) and asg[out]
    return phi


def gate_cnf(w, op, ins):
    """The three rules of 12.6:  a = b AND c, a = b OR c, a = NOT b."""
    a = w
    if op == "and":
        b, c = ins
        return [[(a, True), (b, False), (c, False)], [(a, False), (b, True)], [(a, False), (c, True)]]
    if op == "or":
        b, c = ins
        return [[(a, False), (b, True), (c, True)], [(a, True), (b, False)], [(a, True), (c, False)]]
    (b,) = ins
    return [[(a, True), (b, True)], [(a, False), (b, False)]]


def pad(cnf, fresh):
    """Two-literal clause -> two clauses with one new variable; one-literal clause -> four with two new variables."""
    out = []
    for cl in cnf:
        if len(cl) == 3:
            out.append(cl)
        elif len(cl) == 2:
            x = next(fresh)
            out += [cl + [(x, True)], cl + [(x, False)]]
        elif len(cl) == 1:
            x, y = next(fresh), next(fresh)
            out += [cl + [(x, sx), (y, sy)] for sy in (True, False) for sx in (True, False)]
        else:
            raise ValueError(cl)
    return out


def counter(prefix):
    i = 0
    while True:
        i += 1
        yield f"{prefix}{i}"


def circuit_to_3cnf(inputs, gates, out):
    K1 = binarize(gates, counter("w"))
    phi2 = [cl for g in K1 for cl in gate_cnf(*g)] + [[(out, True)]]
    return K1, phi2, pad(phi2, counter("z"))


# --- the gate rules and padding rules, exhaustively
for op in ("and", "or", "not"):
    ins = ["b", "c"] if op != "not" else ["b"]
    good = True
    for bits in itertools.product([False, True], repeat=len(ins) + 1):
        asg = dict(zip(["a"] + ins, bits))
        eq = asg["a"] == OPS[op]([asg[i] for i in ins])
        good &= holds(gate_cnf("a", op, ins), asg) == eq
    check(f"12.6 gate rule for {op}: the CNF holds exactly when the gate equation holds", good)
good = True
for a, b in itertools.product([False, True], repeat=2):
    two = [[("a", True), ("b", True)]]
    p = pad(two, iter(["x"]))
    good &= (a or b) == any(holds(p, {"a": a, "b": b, "x": x}) for x in (False, True))
    good &= (a or b) == all(holds(p, {"a": a, "b": b, "x": x}) for x in (False, True))
for zv in (False, True):
    p = pad([[("z", True)]], iter(["x", "y"]))
    good &= len(p) == 4 and zv == any(holds(p, {"z": zv, "x": x, "y": y}) for x in (0, 1) for y in (0, 1))
    good &= zv == all(holds(p, {"z": zv, "x": x, "y": y}) for x in (0, 1) for y in (0, 1))
check("12.6 padding: a OR b and z are each equivalent to their padded clauses, for every value of the new variables",
      good)


def random_circuit(ni, ng):
    inputs = [f"x{i}" for i in range(1, ni + 1)]
    wires = list(inputs)
    gates = []
    for g in range(1, ng + 1):
        op = random.choice(["and", "or", "not"])
        if op == "not":
            ins = [random.choice(wires)]
        else:
            ins = random.sample(wires, min(len(wires), random.choice([2, 2, 3])))
            if len(ins) < 2:
                ins = ins * 2
        w = f"y{g}"
        gates.append((w, op, ins))
        wires.append(w)
    return inputs, gates, gates[-1][0]


stats = {"sat": 0, "unsat": 0}
bad = []
for trial in range(400):
    inputs, gates, out = random_circuit(random.randint(1, 4), random.randint(1, 5))
    sat_inputs = [xs for xs in itertools.product([False, True], repeat=len(inputs))
                  if evaluate(inputs, gates, out, xs)[0]]
    K1, phi2, phi3 = circuit_to_3cnf(inputs, gates, out)
    # K' equivalent to K
    same = all(evaluate(inputs, gates, out, xs)[0] == evaluate(inputs, K1, out, xs)[0]
               for xs in itertools.product([False, True], repeat=len(inputs)))
    # Sat transcription: satisfiable iff circuit satisfiable (brute force over all wire values)
    phi = transcribe_sat(gates, out)
    wires = inputs + [g[0] for g in gates]
    phi_sat = any(phi(dict(zip(wires, bits))) for bits in itertools.product([False, True], repeat=len(wires)))
    s3 = dpll(phi3)
    ok = same and phi_sat == bool(sat_inputs) and (s3 is not None) == bool(sat_inputs)
    ok &= all(len(cl) == 3 for cl in phi3)
    ok &= len(phi3) <= 5 * sum(1 for g in K1 if g[1] != "not") + 4 * sum(1 for g in K1 if g[1] == "not") + 4
    # certificate K -> Phi3: trace the input through K', give the padding variables arbitrary (random) values
    for xs in sat_inputs:
        _, val = evaluate(inputs, K1, out, xs)
        asg = {v: val.get(v, random.random() < 0.5) for v in variables(phi3)}
        ok &= holds(phi3, asg)
    # certificate Phi3 -> K: keep the input variables
    if s3 is not None:
        ok &= evaluate(inputs, gates, out, tuple(s3.get(x, False) for x in inputs))[0]
    stats["sat" if sat_inputs else "unsat"] += 1
    if not ok:
        bad.append((inputs, gates))
check("12.5/12.6 on 400 random circuits (≤ 4 inputs, ≤ 5 gates, fan-in 1-3): K' ≡ K, Phi satisfiable iff K is, "
      "Phi3 is 3CNF, at most 5 clauses per binary gate, 4 per NOT gate, +4, satisfiable iff K is, and certificates "
      "transform both ways", not bad and stats["unsat"] > 30, f"{stats}")

# --- the book's circuit (Figures 12.2 and 12.5)
BOOK_IN = ["x1", "x2", "x3", "x4", "x5"]
BOOK_GATES = [("y1", "and", ["x1", "x4"]), ("y2", "not", ["x4"]), ("y3", "and", ["x3", "y2"]),
              ("y4", "or", ["y1", "x2"]), ("y5", "not", ["x2"]), ("y6", "not", ["x5"]),
              ("y7", "or", ["y3", "y5"]), ("z", "and", ["y4", "y7", "y6"])]
book_sat = [xs for xs in itertools.product([0, 1], repeat=5) if evaluate(BOOK_IN, BOOK_GATES, "z", xs)[0]]
check("book circuit: exactly 4 of the 32 inputs turn the light on: x5 = 0 and (x2,x3,x4) = (1,1,0) or (x1,x2,x4) = (1,0,1)",
      sorted(book_sat) == sorted([(x1, 1, 1, 0, 0) for x1 in (0, 1)] + [(1, 0, x3, 1, 0) for x3 in (0, 1)]),
      f"{book_sat}")
xs = (0, 1, 1, 0, 0)
_, val = evaluate(BOOK_IN, BOOK_GATES, "z", xs)
check("book circuit on x = 01100: y1..y7, z = 0,1,1,1,0,1,1,1",
      [int(val[w]) for w in ["y1", "y2", "y3", "y4", "y5", "y6", "y7", "z"]] == [0, 1, 1, 1, 0, 1, 1, 1])

# the book's printed 3CNF (p. 390), transcribed from the PDF: y8 = y4 AND y7, y9 = y8 AND y6, output y9
BOOK_3CNF_TXT = """
y1 ~x1 ~x4 | ~y1 x1 z1 | ~y1 x1 ~z1 | ~y1 x4 z2 | ~y1 x4 ~z2
y2 x4 z3 | y2 x4 ~z3 | ~y2 ~x4 z4 | ~y2 ~x4 ~z4
y3 ~x3 ~y2 | ~y3 x3 z5 | ~y3 x3 ~z5 | ~y3 y2 z6 | ~y3 y2 ~z6
~y4 y1 x2 | y4 ~x2 z7 | y4 ~x2 ~z7 | y4 ~y1 z8 | y4 ~y1 ~z8
y5 x2 z9 | y5 x2 ~z9 | ~y5 ~x2 z10 | ~y5 ~x2 ~z10
y6 x5 z11 | y6 x5 ~z11 | ~y6 ~x5 z12 | ~y6 ~x5 ~z12
~y7 y3 y5 | y7 ~y3 z13 | y7 ~y3 ~z13 | y7 ~y5 z14 | y7 ~y5 ~z14
y8 ~y4 ~y7 | ~y8 y4 z15 | ~y8 y4 ~z15 | ~y8 y7 z16 | ~y8 y7 ~z16
y9 ~y8 ~y6 | ~y9 y8 z17 | ~y9 y6 z18 | ~y9 y6 ~z18 | ~y9 y8 ~z17
y9 z19 z20 | y9 ~z19 z20 | y9 z19 ~z20 | y9 ~z19 ~z20
"""
BOOK_3CNF = [C(*part.split()) for line in BOOK_3CNF_TXT.strip().split("\n") for part in line.split("|")]
K1, phi2, phi3 = circuit_to_3cnf(BOOK_IN, BOOK_GATES, "z")
ren = {"w1": "y8", "z": "y9"}          # our fresh wire and the output, in the book's names


def canon(cnf, rename=None, pad_prefix="z"):
    """Clauses as sorted tuples; padding variables replaced by their sign only."""
    rename = rename or {}
    out = []
    for cl in cnf:
        c = []
        for v, p in cl:
            v = rename.get(v, v)
            c.append(("PAD", p) if re.fullmatch(pad_prefix + r"\d+", v) else (v, p))
        out.append(tuple(sorted(c)))
    return sorted(out)


check("book 3CNF (p. 390): 46 clauses, 34 variables (5 inputs, 9 wires, 20 padding), all with 3 literals",
      len(BOOK_3CNF) == 46 and len(variables(BOOK_3CNF)) == 34 and all(len(c) == 3 for c in BOOK_3CNF))
check("our Tseitin implementation reproduces the book's printed 3CNF clause for clause (up to padding names)",
      canon(phi3, ren) == canon(BOOK_3CNF) and len(phi3) == 46)
check("K' of the book's circuit: 9 gates (6 binary, 3 NOT), so 6*5 + 3*4 + 4 = 46 clauses",
      len(K1) == 9 and sum(g[1] == "not" for g in K1) == 3 and 6 * 5 + 3 * 4 + 4 == 46)
good = True
for xs in itertools.product([False, True], repeat=5):
    fixed = dict(zip(BOOK_IN, xs))
    good &= (dpll(BOOK_3CNF, fixed) is not None) == evaluate(BOOK_IN, BOOK_GATES, "z", xs)[0]
check("book 3CNF with the inputs fixed is satisfiable exactly for the 4 satisfying inputs of the circuit", good)

# --- the page's small example: z = NOT(x1 AND x2), the NAND circuit
NAND_IN = ["x1", "x2"]
NAND_G = [("y", "and", ["x1", "x2"]), ("z", "not", ["y"])]
K1n, phi2n, phi3n = circuit_to_3cnf(NAND_IN, NAND_G, "z")
check("NAND example: Phi2 has 3 + 2 + 1 = 6 clauses, Phi3 has 1 + 2*2 + 2*2 + 4 = 13 clauses",
      len(phi2n) == 6 and len(phi3n) == 13 and len(variables(phi3n)) == 4 + 6)
NAND_PHI3 = [C("y", "~x1", "~x2"), C("~y", "x1", "p1"), C("~y", "x1", "~p1"), C("~y", "x2", "p2"),
             C("~y", "x2", "~p2"), C("z", "y", "p3"), C("z", "y", "~p3"), C("~z", "~y", "p4"),
             C("~z", "~y", "~p4"), C("z", "p5", "p6"), C("z", "~p5", "p6"), C("z", "p5", "~p6"), C("z", "~p5", "~p6")]
check("NAND example: the page's 13 clauses equal our construction (padding variables p1..p6)",
      canon(NAND_PHI3, pad_prefix="p") == canon(phi3n))
nsat = sum(holds(NAND_PHI3, dict(zip(variables(NAND_PHI3), bits)))
           for bits in itertools.product([False, True], repeat=len(variables(NAND_PHI3))))
check("NAND example: 3 of 4 inputs satisfy the circuit; Phi3 has 3 * 2^6 = 192 satisfying assignments of 2^10",
      sum(evaluate(NAND_IN, NAND_G, "z", xs)[0] for xs in itertools.product([0, 1], repeat=2)) == 3 and nsat == 192,
      f"{nsat}")

# =====================================================================================================
# Graphs: vertices list, edges set of frozensets.
def max_indep(V, E):
    """Largest independent set by branching on a vertex of maximum degree; returns a set."""
    adj = {v: set() for v in V}
    for e in E:
        u, w = tuple(e)
        adj[u].add(w)
        adj[w].add(u)

    def rec(cand):
        if not cand:
            return set()
        v = max(cand, key=lambda x: len(adj[x] & cand))
        if not adj[v] & cand:
            return {v} | rec(cand - {v})
        a = {v} | rec(cand - {v} - adj[v])
        b = rec(cand - {v})
        return a if len(a) >= len(b) else b
    return rec(set(V))


def is_indep(S, E):
    return not any(e <= S for e in E)


def complement(V, E):
    return {frozenset((u, w)) for u, w in itertools.combinations(V, 2)} - E


def is_clique(S, E):
    return all(frozenset((u, w)) in E for u, w in itertools.combinations(S, 2))


def is_cover(S, E):
    return all(e & S for e in E)


# --- 12.7  3Sat -> MaxIndSet
def sat_to_is(cnf):
    V = [(j, t) for j in range(len(cnf)) for t in range(len(cnf[j]))]
    E = set()
    for (j, t), (j2, t2) in itertools.combinations(V, 2):
        (v, p), (v2, p2) = cnf[j][t], cnf[j2][t2]
        if j == j2 or (v == v2 and p != p2):
            E.add(frozenset(((j, t), (j2, t2))))
    return V, E


stats = {True: 0, False: 0}
bad = 0
for trial in range(600):
    n = random.randint(3, 4)
    k = random.randint(1, 10 if n == 3 else 12)
    f = random_cnf(n, k)
    if trial % 10 == 0:          # make sure there are unsatisfiable instances: all 8 clauses on three variables
        f = [[(f"v{i}", s) for i, s in zip((1, 2, 3), signs)] for signs in itertools.product([True, False], repeat=3)]
        random.shuffle(f)
    V, E = sat_to_is(f)
    S = max_indep(V, E)
    s = dpll(f) is not None
    stats[s] += 1
    ok = len(S) <= len(f) and (len(S) == len(f)) == s and len(V) == 3 * len(f)
    if s:   # certificate: one true literal per clause is an independent set of size k
        asg = dpll(f)
        pick = {(j, next(t for t in range(3) if asg[f[j][t][0]] == f[j][t][1])) for j in range(len(f))}
        ok &= is_indep(pick, E) and len(pick) == len(f)
    if len(S) == len(f):   # and back: make the chosen literals true
        asg = {}
        for (j, t) in S:
            v, p = f[j][t]
            ok &= asg.get(v, p) == p
            asg[v] = p
        ok &= holds(f, {v: asg.get(v, False) for v in variables(f)})
    bad += not ok
check("12.7 3Sat -> MaxIndSet on 600 random 3CNF formulas: 3k vertices, alpha(G) ≤ k, alpha(G) = k iff satisfiable, "
      "certificates both ways", bad == 0 and stats[False] >= 60, f"{stats}")

BOOK_PHI = [C("a", "b", "c"), C("b", "~c", "~d"), C("~a", "c", "d"), C("a", "~b", "~d")]
V, E = sat_to_is(BOOK_PHI)
neg_edges = [e for e in E if len({j for j, t in e}) == 2]
S = max_indep(V, E)
book_S = {(0, 0), (1, 2), (2, 1), (3, 0)}   # a in clause 1, ~d in clause 2, c in clause 3, a in clause 4
check("book formula (Figure 12.8): 12 vertices, 12 triangle edges + 8 negation edges, alpha = 4",
      len(V) == 12 and len(E) == 20 and len(neg_edges) == 8 and len(S) == 4)
check("Figure 12.8's independent set {a, ~d, c, a} is independent; it sets a = c = True, d = False (b free)",
      is_indep(book_S, E) and all(holds(BOOK_PHI, {"a": 1, "b": b, "c": 1, "d": 0}) for b in (0, 1)))
check("book formula is satisfied by a = c = True, b = d = False and by a = b = d = True, c = False",
      holds(BOOK_PHI, dict(a=1, b=0, c=1, d=0)) and holds(BOOK_PHI, dict(a=1, b=1, c=0, d=1)))
n_book_sat = sum(holds(BOOK_PHI, dict(zip("abcd", bits))) for bits in itertools.product([0, 1], repeat=4))
check("book formula has exactly 8 satisfying assignments of 16", n_book_sat == 8, f"{n_book_sat}")
tau = len(V) - len(S)
Vc, Ec = V, complement(V, E)
check("12.9 on the Figure 12.8 graph: smallest vertex cover 12 - 4 = 8, largest clique of the complement 4",
      tau == 8 and len(max_indep(Vc, complement(Vc, Ec))) == 4 and is_clique(book_S, Ec)
      and is_cover(set(V) - book_S, E))

# --- 12.9  the three relations on every graph with at most 5 vertices, and random graphs with 6-7
good = True
count = 0
for n in range(1, 6):
    Vn = list(range(n))
    pairs = list(itertools.combinations(Vn, 2))
    for mask in range(1 << len(pairs)):
        En = {frozenset(pairs[i]) for i in range(len(pairs)) if mask >> i & 1}
        Ecn = complement(Vn, En)
        for r in range(n + 1):
            for Sset in itertools.combinations(Vn, r):
                Ss = set(Sset)
                good &= is_indep(Ss, En) == is_clique(Ss, Ecn) == is_cover(set(Vn) - Ss, En)
        a = len(max_indep(Vn, En))
        om = max(r for r in range(n + 1) for Sset in itertools.combinations(Vn, r) if is_clique(set(Sset), En)) \
            if n else 0
        ta = min(r for r in range(n + 1) for Sset in itertools.combinations(Vn, r) if is_cover(set(Sset), En))
        good &= om == len(max_indep(Vn, Ecn)) and ta == n - a
        count += 1
for _ in range(200):
    n = random.randint(6, 7)
    Vn = list(range(n))
    En = {frozenset(p) for p in itertools.combinations(Vn, 2) if random.random() < 0.45}
    a = len(max_indep(Vn, En))
    ta = min(r for r in range(n + 1) for Sset in itertools.combinations(Vn, r) if is_cover(set(Sset), En))
    om = max(r for r in range(n + 1) for Sset in itertools.combinations(Vn, r) if is_clique(set(Sset), En))
    good &= ta == n - a and om == len(max_indep(Vn, complement(Vn, En)))
check(f"12.9: S independent in G iff S is a clique in the complement iff V - S is a vertex cover; alpha(G) = "
      f"omega(complement) and tau(G) = n - alpha(G) — all {count} labeled graphs on ≤ 5 vertices + 200 random", good)


# =====================================================================================================
# 12.10  3Sat -> 3Color
def three_colorable(V, E, fixed=None):
    """Backtracking 3-coloring; returns a coloring dict or None."""
    adj = {v: set() for v in V}
    for e in E:
        u, w = tuple(e)
        adj[u].add(w)
        adj[w].add(u)
    col = dict(fixed or {})
    order = []
    seen = set(col)
    # order: repeatedly the uncolored vertex with most colored neighbors
    rest = [v for v in V if v not in seen]
    while rest:
        v = max(rest, key=lambda x: (len(adj[x] & seen), len(adj[x])))
        order.append(v)
        seen.add(v)
        rest.remove(v)

    def rec(i):
        if i == len(order):
            return True
        v = order[i]
        used = {col[w] for w in adj[v] if w in col}
        for c in range(3):
            if c not in used:
                col[v] = c
                if rec(i + 1):
                    return True
                del col[v]
        return False
    for e in E:
        u, w = tuple(e)
        if u in col and w in col and col[u] == col[w]:
            return None
    return dict(col) if rec(0) else None


def brute_colorable(V, E):
    for cols in itertools.product(range(3), repeat=len(V)):
        c = dict(zip(V, cols))
        if all(c[u] != c[w] for u, w in (tuple(e) for e in E)):
            return True
    return False


good = True
for _ in range(300):
    n = random.randint(1, 7)
    Vn = list(range(n))
    En = {frozenset(p) for p in itertools.combinations(Vn, 2) if random.random() < 0.5}
    good &= (three_colorable(Vn, En) is not None) == brute_colorable(Vn, En)
check("3-coloring helper agrees with brute force on 300 random graphs", good)

TRUE, FALSE, OTHER = 0, 1, 2


def sat_to_3color(cnf):
    V = ["T", "F", "X"]
    E = {frozenset(("T", "F")), frozenset(("F", "X")), frozenset(("T", "X"))}
    for v in variables(cnf):
        V += [(v, True), (v, False)]
        E |= {frozenset(((v, True), (v, False))), frozenset(((v, True), "X")), frozenset(((v, False), "X"))}
    for j, cl in enumerate(cnf):
        a, b, c = cl
        p, q, r, s, t = [("g", j, i) for i in range(5)]
        V += [p, q, r, s, t]
        E |= {frozenset(x) for x in [(a, p), (b, q), (p, q), (p, r), (q, r), (r, s), (c, t), (s, t), (s, "T"),
                                     (t, "T")]}
    return V, E


# the half-gadget: inputs a, b; a-p, b-q, triangle p q r
HV = ["a", "b", "p", "q", "r"]
HE = {frozenset(x) for x in [("a", "p"), ("b", "q"), ("p", "q"), ("p", "r"), ("q", "r")]}
good = True
total = 0
for ca, cb in itertools.product(range(3), repeat=2):
    outs = []
    for cp, cq, cr in itertools.product(range(3), repeat=3):
        c = dict(a=ca, b=cb, p=cp, q=cq, r=cr)
        if all(c[u] != c[w] for u, w in (tuple(e) for e in HE)):
            outs.append(cr)
    total += len(outs)
    if ca == cb:
        good &= sorted(outs) == [ca, ca]
    else:
        good &= sorted(outs) == [0, 1, 2]
check("12.10 half-gadget ('majority gate'): equal input colors force that color at the output (2 colorings); "
      "different input colors allow each output color (3 colorings); 5 with fixed inputs, 24 in all",
      good and total == 9 * 0 + 3 * 2 + 6 * 3 == 24)
# Figure 12.14 draws 5 = 2 + 3 (one equal and one different input pair); up to permuting colors there are only 4
allcol = [c for c in itertools.product(range(3), repeat=5)
          if all(c[HV.index(u)] != c[HV.index(w)] for u, w in (tuple(e) for e in HE))]
orbits = {min(tuple(pm[x] for x in c) for pm in itertools.permutations(range(3))) for c in allcol}
check("12.10 Figure 12.14: the 24 half-gadget colorings fall into 4 classes up to permuting the colors (the book "
      "draws 5: its two equal-input drawings differ only by swapping the other two colors)",
      len(allcol) == 24 and len(orbits) == 4)

# the clause gadget alone, literal nodes colored True/False, T/F/X fixed
good = True
for vals in itertools.product([TRUE, FALSE], repeat=3):
    Vg = ["T", "F", "X", "l1", "l2", "l3"] + [f"g{i}" for i in range(5)]
    p, q, r, s, t = [f"g{i}" for i in range(5)]
    Eg = {frozenset(x) for x in [("T", "F"), ("F", "X"), ("T", "X"), ("l1", p), ("l2", q), (p, q), (p, r), (q, r),
                                 (r, s), ("l3", t), (s, t), (s, "T"), (t, "T")]}
    fixed = {"T": TRUE, "F": FALSE, "X": OTHER, "l1": vals[0], "l2": vals[1], "l3": vals[2]}
    good &= (three_colorable(Vg, Eg, fixed) is not None) == (TRUE in vals)
check("12.10 clause gadget: extends to a 3-coloring iff some literal node is colored True (all 8 cases); "
      "5 new vertices, 10 edges", good and len(Eg) - 3 == 10)

stats = {True: 0, False: 0}
bad = 0
for trial in range(250):
    n = random.randint(3, 4)
    f = random_cnf(n, random.randint(1, 9 if n == 3 else 11))
    if trial % 8 == 0:
        f = [[(f"v{i}", s) for i, s in zip((1, 2, 3), signs)] for signs in itertools.product([True, False], repeat=3)]
        random.shuffle(f)
    V, E = sat_to_3color(f)
    col = three_colorable(V, E, {"T": TRUE, "F": FALSE, "X": OTHER})
    s = dpll(f)
    stats[s is not None] += 1
    ok = (col is not None) == (s is not None)
    ok &= len(V) == 3 + 2 * len(variables(f)) + 5 * len(f) and len(E) == 3 + 3 * len(variables(f)) + 10 * len(f)
    if col is not None:   # extract the assignment: a node colored True
        asg = {v: col[(v, True)] == TRUE for v in variables(f)}
        ok &= holds(f, asg)
    if s is not None:     # and forward: color the literal nodes by the assignment, then extend
        fixed = {"T": TRUE, "F": FALSE, "X": OTHER}
        for v in variables(f):
            fixed[(v, True)] = TRUE if s[v] else FALSE
            fixed[(v, False)] = FALSE if s[v] else TRUE
        ok &= three_colorable(V, E, fixed) is not None
    bad += not ok
check("12.10 3Sat -> 3Color on 250 random 3CNF formulas: 3 + 2n + 5k vertices, 3 + 3n + 10k edges, 3-colorable iff "
      "satisfiable, certificates both ways", bad == 0 and stats[False] >= 30, f"{stats}")
V, E = sat_to_3color(BOOK_PHI)
fixed = {"T": TRUE, "F": FALSE, "X": OTHER}
for v, val in dict(a=1, b=0, c=1, d=0).items():
    fixed[(v, True)], fixed[(v, False)] = (TRUE, FALSE) if val else (FALSE, TRUE)
check("book formula (Figure 12.15): 31 vertices, 55 edges; the coloring for a = c = True, b = d = False extends",
      len(V) == 31 and len(E) == 55 and three_colorable(V, E, fixed) is not None)
# the page's figure: clause gadget for (a or b or ~c) with a = True, b = False, c = True
Vg, Eg = sat_to_3color([C("a", "b", "~c")])
fixed = {"T": TRUE, "F": FALSE, "X": OTHER, ("a", True): TRUE, ("a", False): FALSE, ("b", True): FALSE,
         ("b", False): TRUE, ("c", True): TRUE, ("c", False): FALSE}
FIG_COLORING = three_colorable(Vg, Eg, fixed)
check("figure: the clause gadget for (a ∨ b ∨ ~c) with a = c = True, b = False has a 3-coloring",
      FIG_COLORING is not None)


# =====================================================================================================
# Hamiltonian cycles (directed): DFS with pruning, validated against brute force.
def ham_cycle(V, E, count=False, limit=10 ** 9):
    n = len(V)
    if n < 2:
        return 0 if count else None
    idx = {v: i for i, v in enumerate(V)}
    outm, inm = [0] * n, [0] * n
    for u, v in E:
        if u != v:
            outm[idx[u]] |= 1 << idx[v]
            inm[idx[v]] |= 1 << idx[u]
    if any(outm[i] == 0 or inm[i] == 0 for i in range(n)):
        return 0 if count else None
    s = min(range(n), key=lambda i: bin(inm[i]).count("1"))
    sbit = 1 << s
    path = [s]
    found = []

    def dfs(cur, unvis):
        if unvis == 0:
            if outm[cur] & sbit:
                found.append(list(path))
                return not count or len(found) >= limit
            return False
        curbit = 1 << cur
        avail_in, avail_out = unvis | curbit, unvis | sbit
        forced = -1
        m = unvis
        while m:
            b = m & -m
            m ^= b
            w = b.bit_length() - 1
            a = inm[w] & avail_in
            if a == 0 or (outm[w] & avail_out) == 0:
                return False
            if a == curbit:
                if forced >= 0:
                    return False
                forced = w
        if forced >= 0:
            cands = [forced]
        else:
            c, cands = outm[cur] & unvis, []
            while c:
                b = c & -c
                c ^= b
                cands.append(b.bit_length() - 1)
        for w in cands:
            path.append(w)
            if dfs(w, unvis & ~(1 << w)):
                return True
            path.pop()
        return False
    dfs(s, ((1 << n) - 1) & ~sbit)
    if count:
        return len(found)
    return [V[i] for i in found[0]] if found else None


def brute_ham(V, E):
    if len(V) < 2:
        return 0
    s, cnt = V[0], 0
    for perm in itertools.permutations(V[1:]):
        cyc = [s] + list(perm)
        cnt += all((cyc[i], cyc[(i + 1) % len(cyc)]) in E for i in range(len(cyc)))
    return cnt


good = True
for _ in range(800):
    n = random.randint(1, 7)
    Vn = list(range(n))
    En = {(u, w) for u in Vn for w in Vn if u != w and random.random() < 0.4}
    good &= ham_cycle(Vn, En, count=True) == brute_ham(Vn, En)
    hc = ham_cycle(Vn, En)
    good &= (hc is not None) == (brute_ham(Vn, En) > 0)
check("Hamiltonian-cycle helper (existence and count) agrees with brute force on 800 random digraphs", good)


def is_ham(V, E, cyc):
    return sorted(map(repr, cyc)) == sorted(map(repr, V)) and all(
        (cyc[i], cyc[(i + 1) % len(cyc)]) in E for i in range(len(cyc)))


# --- 12.11 (a)  VertexCover -> DirectedHamCycle, as in the book
def vc_to_ham(Vg, Eg, k):
    nbrs = {u: [] for u in Vg}
    for u, v in Eg:
        nbrs[u].append(v)
        nbrs[v].append(u)
    V, E = [], set()
    for u, v in Eg:
        V += [(u, v, "in"), (u, v, "out"), (v, u, "in"), (v, u, "out")]
        E |= {((u, v, "in"), (u, v, "out")), ((u, v, "in"), (v, u, "in")), ((v, u, "in"), (u, v, "in")),
              ((v, u, "in"), (v, u, "out")), ((u, v, "out"), (v, u, "out")), ((v, u, "out"), (u, v, "out"))}
    for u in Vg:
        for i in range(len(nbrs[u]) - 1):
            E.add(((u, nbrs[u][i], "out"), (u, nbrs[u][i + 1], "in")))
    for i in range(1, k + 1):
        V.append(("cover", i))
        for u in Vg:
            if nbrs[u]:
                E.add((("cover", i), (u, nbrs[u][0], "in")))
                E.add(((u, nbrs[u][-1], "out"), ("cover", i)))
    return V, E, nbrs


def min_cover(Vg, Eg):
    for r in range(len(Vg) + 1):
        for S in itertools.combinations(Vg, r):
            if all(u in S or v in S for u, v in Eg):
                return r
    return len(Vg)


good, tested, outside_fail = True, 0, 0
for trial in range(350):
    n = random.randint(2, 5)
    Vg = list("uvwxy"[:n])
    pairs = list(itertools.combinations(Vg, 2))
    Eg = [p for p in pairs if random.random() < 0.5][:6]
    random.shuffle(Eg)
    nonisolated = len({x for e in Eg for x in e})
    tau = min_cover(Vg, Eg)
    for k in range(0, n + 1):
        V, E, _ = vc_to_ham(Vg, Eg, k)
        h = ham_cycle(V, E) is not None
        yes = tau <= k
        if k <= nonisolated and nonisolated > 0:
            good &= h == yes
            tested += 1
            if h:   # the cycle describes a cover: chains entered from cover vertices
                cyc = ham_cycle(V, E)
                cover = {cyc[(i + 1) % len(cyc)][0] for i, x in enumerate(cyc) if x[0] == "cover"}
                good &= len(cover) == k and all(u in cover or v in cover for u, v in Eg)
        elif yes and not h:
            outside_fail += 1
check(f"12.11 VertexCover -> DirectedHamCycle: H has a Hamiltonian cycle iff G has a vertex cover of size ≤ k, on "
      f"{tested} random (G, k) with 1 ≤ #non-isolated vertices and k ≤ that number; the cycle's chains form a cover of "
      f"size exactly k", good and tested > 600)
check("12.11: outside that range the book's reduction fails (YES instance, no Hamiltonian cycle) — so the page "
      "first answers k ≥ #non-isolated vertices directly", outside_fail > 0, f"{outside_fail} cases")
V, E, _ = vc_to_ham(["u", "v", "w", "x"], [("u", "v")], 3)
check("12.11 edge case: G = the edge uv plus isolated w and x, k = 3: G has a cover of size 1 ≤ 3, but H (3 cover "
      "vertices, 2 vertex chains) has no Hamiltonian cycle", ham_cycle(V, E) is None and
      min_cover(["u", "v", "w", "x"], [("u", "v")]) == 1)

BOOK_G = ["u", "v", "w", "x"]
BOOK_GE = [("u", "v"), ("u", "w"), ("u", "x"), ("v", "x"), ("w", "x")]
V, E, nb = vc_to_ham(BOOK_G, BOOK_GE, 2)
covers2 = [S for S in itertools.combinations(BOOK_G, 2) if all(u in S or v in S for u, v in BOOK_GE)]
nham = ham_cycle(V, E, count=True)
check("Figure 12.17 graph (edges uv uw ux vx wx), k = 2: H has 4*5 + 2 = 22 vertices and 30 + 6 + 16 = 52 edges",
      len(V) == 22 and len(E) == 52, f"{len(V)} {len(E)}")
check("Figure 12.17: the only vertex cover of size 2 is {u, x}, and H has exactly 2 Hamiltonian cycles "
      "(the two ways to assign x1, x2 to the chains of u and x)", covers2 == [("u", "x")] and nham == 2, f"{nham}")
# the edge gadget: the only ways a Hamiltonian cycle can cross it (4 vertices with outside in- and out-edges)
GV = [("u", "v", "in"), ("u", "v", "out"), ("v", "u", "in"), ("v", "u", "out")]
GE = {(("u", "v", "in"), ("u", "v", "out")), (("u", "v", "in"), ("v", "u", "in")), (("v", "u", "in"), ("u", "v", "in")),
      (("v", "u", "in"), ("v", "u", "out")), (("u", "v", "out"), ("v", "u", "out")), (("v", "u", "out"), ("u", "v", "out"))}
# path covers of the gadget whose paths start at "in" vertices and end at "out" vertices
covers = []
for S in itertools.product([0, 1], repeat=len(GE)):
    es = [e for e, b in zip(sorted(GE), S) if b]
    outdeg = {v: sum(e[0] == v for e in es) for v in GV}
    indeg = {v: sum(e[1] == v for e in es) for v in GV}
    if any(d > 1 for d in outdeg.values()) or any(d > 1 for d in indeg.values()):
        continue
    starts = [v for v in GV if indeg[v] == 0]
    ends = [v for v in GV if outdeg[v] == 0]
    # every path must enter at an "in" vertex (from outside) and leave at an "out" vertex; no cycles
    if all(v[2] == "in" for v in starts) and all(v[2] == "out" for v in ends) and len(starts) == len(ends) \
            and len(starts) >= 1 and len(es) == 4 - len(starts):
        covers.append(sorted(es))
check("Figure 12.16: an edge gadget can be covered by paths from 'in' to 'out' vertices in exactly 3 ways: straight "
      "through on both sides, or one detour (u,v,in)→(v,u,in)→(v,u,out)→(u,v,out) or its mirror", len(covers) == 3)


# --- 12.11 (b)  3Sat -> DirectedHamCycle
def sat_to_ham_book(cnf, nvars_order, reading):
    """The book's construction. reading 'text': rows (i,0..2k); 'figure': rows of 2k vertices (i,1..2k).
    Connectors (i,a)->(i+1,b) for a, b in {first, last}, cyclically; clause j: positive x_i: (i,2j-1)->[j]->(i,2j),
    negative: (i,2j)->[j]->(i,2j-1)."""
    k, n = len(cnf), len(nvars_order)
    lo = 0 if reading == "text" else 1
    V, E = [], set()
    for i in range(1, n + 1):
        V += [(i, j) for j in range(lo, 2 * k + 1)]
        for j in range(lo + 1, 2 * k + 1):
            E |= {((i, j - 1), (i, j)), ((i, j), (i, j - 1))}
    for i in range(1, n + 1):
        i2 = i % n + 1
        for a in (lo, 2 * k):
            for b in (lo, 2 * k):
                E.add(((i, a), (i2, b)))
    num = {v: i + 1 for i, v in enumerate(nvars_order)}
    for j, cl in enumerate(cnf, start=1):
        V.append(("c", j))
        for v, p in cl:
            i = num[v]
            if p:
                E |= {((i, 2 * j - 1), ("c", j)), (("c", j), (i, 2 * j))}
            else:
                E |= {((i, 2 * j), ("c", j)), (("c", j), (i, 2 * j - 1))}
    return V, E


def sat_to_ham_fixed(cnf, nvars_order):
    """The page's repaired construction: rows (i,0..3k); clause j uses (i,3j-2), (i,3j-1); (i,3j) are spacers;
    hub vertices h_i with h_i -> (i,0), h_i -> (i,3k), (i,0) -> h_{i+1}, (i,3k) -> h_{i+1}."""
    k, n = len(cnf), len(nvars_order)
    V, E = [], set()
    for i in range(1, n + 1):
        V.append(("h", i))
        V += [(i, j) for j in range(0, 3 * k + 1)]
        for j in range(1, 3 * k + 1):
            E |= {((i, j - 1), (i, j)), ((i, j), (i, j - 1))}
        i2 = i % n + 1
        E |= {(("h", i), (i, 0)), (("h", i), (i, 3 * k)), ((i, 0), ("h", i2)), ((i, 3 * k), ("h", i2))}
    num = {v: i + 1 for i, v in enumerate(nvars_order)}
    for j, cl in enumerate(cnf, start=1):
        V.append(("c", j))
        for v, p in cl:
            i = num[v]
            if p:
                E |= {((i, 3 * j - 2), ("c", j)), (("c", j), (i, 3 * j - 1))}
            else:
                E |= {((i, 3 * j - 1), ("c", j)), (("c", j), (i, 3 * j - 2))}
    return V, E


def fixed_cycle(cnf, order, asg):
    """The (=>) direction of the page: the cycle that encodes a satisfying assignment."""
    k, n = len(cnf), len(order)
    num = {v: i + 1 for i, v in enumerate(order)}
    chosen = {}
    for j, cl in enumerate(cnf, start=1):
        v, p = next((v, p) for v, p in cl if asg[v] == p)
        chosen[(num[v], j)] = True
    cyc = []
    for i in range(1, n + 1):
        cyc.append(("h", i))
        right = asg[order[i - 1]]
        cols = range(0, 3 * k + 1) if right else range(3 * k, -1, -1)
        for jj in cols:
            cyc.append((i, jj))
            j = (jj + 2) // 3
            if right and jj == 3 * j - 2 and (i, j) in chosen:
                cyc.append(("c", j))
            if not right and jj == 3 * j - 1 and (i, j) in chosen:
                cyc.append(("c", j))
    return cyc


bad_book = {"text": 0, "figure": 0}
bad_fixed, stats = 0, {True: 0, False: 0}
for trial in range(1200):
    n = random.randint(1, 3)
    k = random.randint(1, 4)
    f = random_cnf(n, k, 1, 3)
    order = [f"v{i}" for i in range(1, n + 1)]
    f = [[(v, p) for v, p in cl] for cl in f]
    s = brute_sat(f + [[(v, True), (v, False)] for v in order])   # assignment over all n variables
    stats[s is not None] += 1
    for reading in ("text", "figure"):
        V, E = sat_to_ham_book(f, order, reading)
        bad_book[reading] += (ham_cycle(V, E) is not None) != (s is not None)
    V, E = sat_to_ham_fixed(f, order)
    h = ham_cycle(V, E)
    ok = (h is not None) == (s is not None)
    ok &= len(V) == n * (3 * k + 2) + k
    if s is not None:
        ok &= is_ham(V, E, fixed_cycle(f, order, s))
    if h is not None:   # (<=): read the assignment off the row directions, check it
        pos = {x: t for t, x in enumerate(h)}
        asg = {}
        for i, v in enumerate(order, start=1):
            a0, a1 = pos[(i, 0)], pos[(i, 1)]
            asg[v] = (a1 - a0) % len(h) in (1, 2)   # (i,0) then (i,1) (possibly via a clause vertex): left to right
        ok &= holds(f, asg)
    bad_fixed += not ok
check("12.11 the book's 3Sat -> DirectedHamCycle (text reading, rows (i,0..2k)) gives Hamiltonian cycles for some "
      "unsatisfiable formulas (1200 random small CNFs)", bad_book["text"] > 0, f"{bad_book['text']} wrong answers")
check("12.11 the book's construction as drawn in Figures 12.19-12.20 (rows of 2k vertices) fails too",
      bad_book["figure"] > 0, f"{bad_book['figure']} wrong answers")
check("12.11 the page's repaired construction (spacers + hubs): Hamiltonian iff satisfiable on all 1200 random CNFs "
      "(1-3 variables, 1-4 clauses of 1-3 literals); n(3k+2) + k vertices; the (=>) cycle is Hamiltonian; row "
      "directions of any Hamiltonian cycle give a satisfying assignment", bad_fixed == 0 and stats[False] > 100,
      f"{stats}")

# the page's 3CNF counterexample: all eight clauses on a, b, c, with (~a or b or c) last
CE = [[("a", s1), ("b", s2), ("c", s3)] for s1, s2, s3 in itertools.product([True, False], repeat=3)
      if (s1, s2, s3) != (False, True, True)] + [C("~a", "b", "c")]
check("counterexample formula: 8 distinct clauses on a, b, c, unsatisfiable; a = True, b = c = False satisfies all "
      "but the last", brute_sat(CE) is None and len({tuple(c) for c in CE}) == 8
      and holds(CE[:-1], dict(a=1, b=0, c=0)) and not holds(CE[-1:], dict(a=1, b=0, c=0)))
for reading in ("text", "figure"):
    V, E = sat_to_ham_book(CE, ["a", "b", "c"], reading)
    lo, k = (0 if reading == "text" else 1), 8
    asg = dict(a=True, b=False, c=False)
    cyc = []
    for i, v in enumerate(["a", "b", "c"], start=1):
        cols = list(range(lo, 2 * k + 1)) if asg[v] else list(range(2 * k, lo - 1, -1))
        for jj in cols:
            cyc.append((i, jj))
            for j in range(1, k):          # clauses 1..7: splice each at its first true literal
                cl = CE[j - 1]
                first = next((vv, p) for vv, p in cl if asg[vv] == p)
                if first[0] == v and ((asg[v] and jj == 2 * j - 1) or (not asg[v] and jj == 2 * j)):
                    cyc.append(("c", j))
        if i == 1:
            cyc.append(("c", 8))          # the splice: (1,2k) -> [k] -> (2,2k) replaces the connector
    check(f"counterexample ({reading} reading): the cycle of a = True, b = c = False with (1,2k)→[k]→(2,2k) in place "
          f"of the connector (1,2k)→(2,2k) is a Hamiltonian cycle of H", is_ham(V, E, cyc),
          f"{len(V)} vertices")
V, E = sat_to_ham_fixed(BOOK_PHI, ["a", "b", "c", "d"])
check("repaired construction on the book's formula: 4*(3*4+2) + 4 = 60 vertices; the cycle for a = b = d = True, "
      "c = False is Hamiltonian", len(V) == 60 and is_ham(V, E, fixed_cycle(BOOK_PHI, list("abcd"),
                                                                            dict(a=1, b=1, c=0, d=1))))
FIG_HAM = [C("a", "b"), C("~a", "~b")]
V, E = sat_to_ham_fixed(FIG_HAM, ["a", "b"])
cyc = fixed_cycle(FIG_HAM, ["a", "b"], dict(a=True, b=False))
check("figure: (a ∨ b) ∧ (~a ∨ ~b), rows of 7 vertices, 2 hubs, 2 clause vertices = 18 vertices; the cycle for "
      "a = True, b = False is Hamiltonian; H has exactly 2 Hamiltonian cycles (the two satisfying assignments)",
      len(V) == 18 and is_ham(V, E, cyc) and ham_cycle(V, E, count=True) == 2)
FIG_HAM_CYCLE = cyc



# clause gadget: the page's explicit extensions
def gadget_ok(l1, l2, l3, r, s_, t, p_=None, q=None):
    cols = {"T": TRUE, "l1": l1, "l2": l2, "l3": l3, "r": r, "s": s_, "t": t}
    Eg2 = [("r", "s"), ("l3", "t"), ("s", "t"), ("s", "T"), ("t", "T")]
    if any(cols[u] == cols[w] for u, w in Eg2):
        return False
    # p, q must exist for the majority triangle with inputs l1, l2 and tip r
    return any(pp != l1 and qq != l2 and pp != qq and pp != r and qq != r
               for pp in range(3) for qq in range(3))


good = True
for l1, l2, l3 in itertools.product([TRUE, FALSE], repeat=3):
    if TRUE not in (l1, l2, l3):
        continue
    if TRUE in (l1, l2):
        good &= any(gadget_ok(l1, l2, l3, TRUE, s_, t) for s_ in range(3) for t in range(3))
    else:
        good &= gadget_ok(l1, l2, l3, FALSE, OTHER, FALSE)
check("12.10 page's extension rule: r = True when l1 or l2 is True; otherwise r = False, s = Other, t = False", good)

# edge counts of the two Hamiltonian-cycle constructions
good = True
for _ in range(60):
    n = random.randint(2, 6)
    Vg = list(range(n))
    Eg = [p for p in itertools.combinations(Vg, 2) if random.random() < 0.5]
    if len({x for e in Eg for x in e}) < n or not Eg:
        continue
    k = random.randint(0, n - 1)
    V, E, _ = vc_to_ham(Vg, Eg, k)
    good &= len(V) == 4 * len(Eg) + k and len(E) == 6 * len(Eg) + (2 * len(Eg) - n) + 2 * k * n
for _ in range(60):
    n, k = random.randint(3, 5), random.randint(1, 5)
    f = random_cnf(n, k)
    V, E = sat_to_ham_fixed(f, [f"v{i}" for i in range(1, n + 1)])
    good &= len(V) == n * (3 * k + 2) + k and len(E) == 6 * k * n + 4 * n + 6 * k
check("12.11 sizes: VertexCover -> HamCycle has 4E + k vertices and 6E + (2E - V) + 2kV edges (no isolated "
      "vertices); 3Sat -> HamCycle (repaired) has n(3k+2) + k vertices and 6kn + 4n + 6k edges", good)
# a repeated literal makes clause edges coincide: (a or a or b) has fewer than 6kn + 4n + 6k edges
V, E = sat_to_ham_fixed([[("a", True), ("a", True), ("b", True)]], ["a", "b"])
check("12.11 sizes: with a repeated literal, (a ∨ a ∨ b) gives fewer than 6kn + 4n + 6k edges (hence 'at most')",
      len(E) == 6 * 1 * 2 + 4 * 2 + 6 - 2, f"{len(E)}")
# the page's handling of VertexCover -> DirectedHamCycle: drop isolated vertices; if k >= n' output a triangle
good, tested = True, 0
for trial in range(250):
    n = random.randint(1, 5)
    Vg = list("uvwxy"[:n])
    Eg = [p for p in itertools.combinations(Vg, 2) if random.random() < 0.5][:6]
    tau = min_cover(Vg, Eg)
    Vn = [x for x in Vg if any(x in e for e in Eg)]
    for k in range(0, n + 1):
        if k >= len(Vn):
            h = True      # a fixed Hamiltonian graph, e.g. a directed triangle
        else:
            V, E, _ = vc_to_ham(Vn, Eg, k)
            h = ham_cycle(V, E) is not None
        good &= h == (tau <= k)
        tested += 1
check(f"12.11 the page's version (isolated vertices removed, k ≥ n' answered by a fixed Hamiltonian graph) is correct "
      f"on {tested} random (G, 0 ≤ k ≤ V), including graphs with isolated vertices and no edges", good)

# =====================================================================================================
# 12.12  VertexCover -> SubsetSum
def vc_to_subsetsum(Vg, Eg, k):
    m = len(Eg)
    b = [4 ** i for i in range(m)]
    a = {v: 4 ** m + sum(4 ** i for i, e in enumerate(Eg) if v in e) for v in Vg}
    T = k * 4 ** m + sum(2 * 4 ** i for i in range(m))
    return a, b, T


def subset_sums_hit(nums, T):
    reach = {0}
    for x in nums:
        reach |= {r + x for r in reach if r + x <= T}
    return T in reach


good, tested, nocarry = True, 0, True
for trial in range(400):
    n = random.randint(1, 6)
    Vg = list(range(n))
    Eg = [p for p in itertools.combinations(Vg, 2) if random.random() < 0.45]
    random.shuffle(Eg)
    tau = min_cover(Vg, Eg)
    for k in range(0, n + 1):
        a, b, T = vc_to_subsetsum(Vg, Eg, k)
        nums = list(a.values()) + b
        good &= subset_sums_hit(nums, T) == (tau <= k)
        tested += 1
    # no carries: in every sub-multiset, each low digit sums to at most 3
    m = len(Eg)
    for i in range(m):
        nocarry &= sum((x // 4 ** i) % 4 for x in list(vc_to_subsetsum(Vg, Eg, 0)[0].values()) + b) == 3
check(f"12.12 VertexCover -> SubsetSum (X a multiset): subset sums to T iff a vertex cover of size ≤ k exists, "
      f"on {tested} random (G, 0 ≤ k ≤ V)", good)
check("12.12 no carries: for every edge i exactly three numbers of X have digit i equal to 1 (b_i and the two endpoints)",
      nocarry)
a, b, T = vc_to_subsetsum(["u", "v"], [("u", "v")], 1)
check("12.12 X can have repeated values: the edge uv alone gives a_u = a_v = 5 (so X must be a multiset, an array "
      "as in Chapter 2)", a["u"] == a["v"] == 5 and T == 6)
a, b, T = vc_to_subsetsum(["u", "v"], [("u", "v")], 2)
check("12.12 read as a set, X would give wrong answers: edge uv, k = 2 (cover {u, v}) gives the multiset {5, 5, 1} "
      "with 5 + 5 = 10 = T, but the set {5, 1} cannot reach 10",
      T == 10 and subset_sums_hit(list(a.values()) + b, T) and not subset_sums_hit(sorted(set(a.values()) | set(b)), T))
good = True
for trial in range(200):
    n = random.randint(1, 6)
    Vg = list(range(n))
    Eg = [p for p in itertools.combinations(Vg, 2) if random.random() < 0.45]
    for k in range(1, n + 1):
        good &= vc_to_subsetsum(Vg, Eg, k)[2] >= 4 ** len(Eg)
check("12.12 Caveat: T ≥ 4^E whenever k ≥ 1 (200 random graphs, every 1 ≤ k ≤ V; equality only for E = 0, k = 1)",
      good and vc_to_subsetsum([0], [], 1)[2] == 1)

BOOK_SV = ["u", "v", "w", "x"]
BOOK_SE = [("u", "v"), ("u", "w"), ("v", "w"), ("v", "x"), ("w", "x")]
# the book numbers the edges so that uv is the most significant edge digit: edge i = BOOK_SE[E-1-i]
a, b, T = vc_to_subsetsum(BOOK_SV, list(reversed(BOOK_SE)), 2)
check("12.12 book example: a_u, a_v, a_w, a_x = 1344, 1300, 1105, 1029; b_uv..b_wx = 256, 64, 16, 4, 1; T = 2730",
      [a[v] for v in BOOK_SV] == [1344, 1300, 1105, 1029] and sorted(b, reverse=True) == [256, 64, 16, 4, 1]
      and T == 2730)


def base4(x, digits=6):
    s = ""
    for _ in range(digits):
        s = str(x % 4) + s
        x //= 4
    return s


check("12.12 base-4 digits: 111000, 110110, 101101, 100011; 010000, 001000, 000100, 000010, 000001; T = 222222",
      [base4(a[v]) for v in BOOK_SV] == ["111000", "110110", "101101", "100011"]
      and [base4(x) for x in sorted(b, reverse=True)] == ["010000", "001000", "000100", "000010", "000001"]
      and base4(T) == "222222")
check("12.12 cover {v, w}: a_v + a_w + b_uv + b_uw + b_vx + b_wx = 1300 + 1105 + 256 + 64 + 4 + 1 = 2730",
      1300 + 1105 + 256 + 64 + 4 + 1 == 2730 and min_cover(BOOK_SV, BOOK_SE) == 2)
covers2 = [S for S in itertools.combinations(BOOK_SV, 2) if all(u in S or v in S for u, v in BOOK_SE)]
nums = [a[v] for v in BOOK_SV] + b
subs = [S for r in range(len(nums) + 1) for S in itertools.combinations(range(len(nums)), r)
        if sum(nums[i] for i in S) == T]
check("12.12 book example: {v, w} is the only vertex cover of size 2, and exactly one subset of X sums to 2730",
      covers2 == [("v", "w")] and len(subs) == 1)
a1, b1, T1 = vc_to_subsetsum(BOOK_SV, list(reversed(BOOK_SE)), 1)
check("12.12 with k = 1 (T = 1*4^5 + 682 = 1706) no subset works, since the graph has no cover of size 1",
      T1 == 1706 and not subset_sums_hit([a1[v] for v in BOOK_SV] + b1, T1))
check("12.12 the target is exponential in the input: T > 4^E, so the O(nT) table has more than n*4^E entries",
      T > 4 ** 5)

# =====================================================================================================
# Concept-page examples
# np-hardness: the 5-cycle needs three colors; a 3-coloring certificate checks in O(V+E)
C5 = list(range(5))
C5E = {frozenset((i, (i + 1) % 5)) for i in range(5)}
two_col = any(all(c[u] != c[w] for u, w in (tuple(e) for e in C5E)) for c in itertools.product(range(2), repeat=5))
cert = {0: 0, 1: 1, 2: 0, 3: 1, 4: 2}
check("np-hardness example: the 5-cycle is not 2-colorable; the coloring 0,1,0,1,2 is a proper 3-coloring",
      not two_col and all(cert[u] != cert[w] for u, w in (tuple(e) for e in C5E)))
# polynomial-time-reductions example: IndependentSet -> Clique on the 5-cycle: alpha = 2, complement is a 5-cycle
C5c = complement(C5, C5E)
check("reductions example: the complement of the 5-cycle 01234 is the 5-cycle 02413; alpha(C5) = 2 = omega(complement); "
      "{0, 2} is independent in C5 and a clique in the complement",
      C5c == {frozenset((0, 2)), frozenset((2, 4)), frozenset((4, 1)), frozenset((1, 3)), frozenset((3, 0))}
      and len(max_indep(C5, C5E)) == 2 and is_indep({0, 2}, C5E) and is_clique({0, 2}, C5c)
      and max(r for r in range(6) for S in itertools.combinations(C5, r) if is_clique(set(S), C5c)) == 2)
# satisfiability example: z = x1 OR x2
OR_IN, OR_G = ["x1", "x2"], [("z", "or", ["x1", "x2"])]
_, phi2o, phi3o = circuit_to_3cnf(OR_IN, OR_G, "z")
nv = variables(phi3o)
nsat = [dict(zip(nv, bits)) for bits in itertools.product([False, True], repeat=len(nv))
        if holds(phi3o, dict(zip(nv, bits)))]
check("satisfiability example: z = x1 ∨ x2 gives 1 + 2 + 2 + 4 = 9 clauses on 7 variables; 48 of the 128 "
      "assignments satisfy it, all with z = True and (x1, x2) ≠ (False, False)",
      len(phi3o) == 9 and len(nv) == 7 and len(nsat) == 48
      and all(s["z"] and (s["x1"] or s["x2"]) for s in nsat))
check("satisfiability example: 2SAT-style (x∨y)∧(~x∨y)∧(x∨~y)∧(~x∨~y) is unsatisfiable; dropping any clause makes "
      "it satisfiable", brute_sat([C("x", "y"), C("~x", "y"), C("x", "~y"), C("~x", "~y")]) is None and all(
          brute_sat([c for t, c in enumerate([C("x", "y"), C("~x", "y"), C("x", "~y"), C("~x", "~y")]) if t != d])
          for d in range(4)))

# =====================================================================================================
# The page text and figures (only once the page exists)
if os.path.exists(PAGE):
    page = read(PAGE)
    concepts = {n: read(os.path.join(CONCEPTS, n + ".md")) for n in
                ("np-hardness", "polynomial-time-reductions", "satisfiability", "cook-levin-theorem", "subset-sum")}

    def has(s, *subs):
        return all(x in s for x in subs)

    # the 16 fixed headings + Summary, in order
    heads = re.findall(r"^## (.+)$", page, re.M)
    want = ["12.1 A game you can't win", "12.2 P versus NP", "12.3 NP-hard, NP-easy and NP-complete",
            "12.4 Formal definitions", "12.5 Reductions and SAT", "12.6 3SAT (from CircuitSat)",
            "12.7 Maximum independent set (from 3SAT)", "12.8 The general pattern",
            "12.9 Clique and vertex cover (from independent set)", "12.10 Graph coloring (from 3SAT)",
            "12.11 Hamiltonian cycle", "12.12 Subset sum (from vertex cover)", "12.13 Other useful NP-hard problems",
            "12.14 Choosing the right problem", "12.15 A frivolous real-world example", "12.16 On beyond zebra",
            "Summary"]
    check("page: the 16 fixed section headings and Summary, in order", heads == want, f"{heads}")
    check("page: no 'clearly', 'obviously', 'trivially'",
          not re.search(r"\\b(clearly|obviously|trivially)\\b", page, re.I))
    # the book circuit's transcription, as displayed
    disp = re.search(r"\(y_1 = x_1\\land x_4\).*?\\land z\.", page, re.S).group(0)
    eqs = re.findall(r"\((\w+(?:_\d)?) = ([^)]*)\)", disp)
    def parse_eq(lhs, rhs):
        lhs = lhs.replace("_", "")
        if rhs.startswith("\\bar"):
            return (lhs, "not", [rhs.split()[-1].replace("_", "")])
        op = "and" if "land" in rhs else "or"
        return (lhs, op, [t.replace("_", "") for t in re.split(r"\\land|\\lor", rhs) if t.strip()])
    parsed = [parse_eq(l, r) for l, r in eqs]
    parsed = [(w, op, [i.strip() for i in ins]) for w, op, ins in parsed]
    check("page: the displayed transcription of the book's circuit is exactly its gate list",
          parsed == BOOK_GATES, f"{parsed}")
    check("page: wire values for x = 01100 and the counts 46 clauses / 34 variables / 6*5 + 3*4 + 4",
          has(page, "$y_1, \\dots, y_7, z = 0, 1, 1, 1, 0, 1, 1, 1$", "6\\cdot 5 + 3\\cdot 4 + 4 = 46",
              "46$ clauses over 34 variables", "5 inputs, 9 wires and 20 padding"))
    # the NAND display
    m = re.search(r"\\Phi_3 ={}&(.*?)\\end\{aligned\}", page, re.S).group(1)
    clauses = re.findall(r"\(([^()]*)\)", m)
    def lit_tex(t):
        t = t.strip()
        neg = t.startswith("\\bar")
        v = t.replace("\\bar", "").replace("_", "").replace(" ", "")
        return (v, not neg)
    page_phi3 = [[lit_tex(t) for t in c.split("\\lor")] for c in clauses]
    check("page: the 13 displayed clauses of Phi3 for z = NOT(x1 AND x2) equal our construction",
          len(page_phi3) == 13 and canon(page_phi3, pad_prefix="p") == canon(phi3n), f"{len(page_phi3)}")
    check("page: 3Sat -> MaxIndSet / complement example numbers (12 vertices, alpha 4, cover 12 - 4 = 8, clique 4)",
          has(page, "$12 - 4 = 8$", "largest clique of 4 vertices"))
    check("page: 3Color sizes 3 + 2n + 5k, 3 + 3n + 10k; book example 31 vertices and 55 edges",
          has(page, "$3 + 2n + 5k$ vertices and $3 + 3n + 10k$ edges", "$3 + 8 + 20 = 31$", "$3 + 12 + 40 = 55$"))
    check("page: VertexCover -> HamCycle sizes and the Figure 12.17 numbers (22 vertices, 52 edges, two cycles)",
          has(page, "$4E + k$ vertices and $6E + (2E - V) + 2kV$ edges", "$4\\cdot 5 + 2 = 22$",
              "$30 + 6 + 16 = 52$", "exactly two Hamiltonian cycles"))
    check("page: repaired 3Sat -> HamCycle sizes n(3k+2) + k and 6kn + 4n + 6k; the book example's 60 vertices",
          has(page, "$n(3k+2) + k$ vertices and at most $6kn + 4n + 6k$ edges", "$4\\cdot 14 + 4 = 60$"))
    # subset-sum table
    rows = re.findall(r"^\| \$([ab])_\{?(\w+)\}?\$ \| (\d) \| (\d) \| (\d) \| (\d) \| (\d) \| (\d) \| (\d+) \| ?(✓?) ?\|$",
                      page, re.M)
    a, b, T = vc_to_subsetsum(BOOK_SV, list(reversed(BOOK_SE)), 2)
    bmap = dict(zip(["wx", "vx", "vw", "uw", "uv"], b))
    ok = len(rows) == 9
    chosen = 0
    for kind, name, *digits, value, mark in rows:
        num = a[name] if kind == "a" else bmap[name]
        ok &= base4(num) == "".join(digits) and int(value) == num
        chosen += num if mark else 0
    ok &= chosen == T == 2730 and "| $T$ | 2 | 2 | 2 | 2 | 2 | 2 | 2730 |" in page
    check("page: the subset-sum table (9 numbers, digits, values, the ✓ subset summing to T = 2730)", ok,
          f"{len(rows)} rows")
    check("page: subset-sum text numbers (1300 + 1105 + 256 + 64 + 4 + 1 = 2730; k = 1 target 1706)",
          has(page, "$1300 + 1105 + 256 + 64 + 4 + 1 = 2730$", "$1\\cdot 4^5 + 682 = 1706$"))
    check("page: the counterexample is stated with (ā ∨ b ∨ c) last and the splice (1,2k)→[8]→(2,2k)",
          has(page, "with $(\\bar a\\lor b\\lor c)$ last", "$(1,2k)\\to[8]\\to(2,2k)$"))
    check("page: exam facts (Nov 10–19, HW10 Nov 17, HW11 Dec 1, final Dec 11, not Midterm 2, labs 12a–13b, "
          "rubric 1/2/2/2/2/1, at most 5, at most 1)",
          has(page, "November 10–19", "Homework 10 (due November 17)", "Homework 11 (due December 1)",
              "final exam (December 11)", "not on Midterm 2", "Labs 12a–13b", "at most 5",
              "wrong direction at most 1"))
    # figures
    figs = {n: read(os.path.join(FIGS, f"a12-{n}.html")) for n in
            ("reduction", "circuit", "tseitin", "indset", "coloring", "vc-gadget", "ham-3sat")}
    check("page: all seven figures are placed and inlined",
          all(f"<!-- fig:a12-{n} -->" in page and figs[n].strip() in page for n in figs))
    check("figure circuit: caption says 4 of 32 inputs; input digits 0 1 1 0 0 drawn",
          "Exactly 4 of the 32 inputs" in figs["circuit"] and len(book_sat) == 4)
    letters = re.findall(r'font-weight:700;">([TFO])</text>', figs["coloring"])
    col5 = dict(zip("pqrst", ["TFO".index(x) for x in letters[:5]]))
    cg = {"a": TRUE, "b": FALSE, "cbar": FALSE, "T": TRUE, **col5}
    CEd = [("a", "p"), ("b", "q"), ("p", "q"), ("p", "r"), ("q", "r"), ("r", "s"), ("cbar", "t"), ("s", "t"),
           ("s", "T"), ("t", "T")]
    check("figure coloring: the drawn colors of p, q, r, s, t form a proper coloring with a True, b and c̄ False",
          len(letters) == 5 and all(cg[u] != cg[w] for u, w in CEd), f"{letters}")
    check("figure indset / tseitin / ham captions: 12 + 8 edges; 13-clause, 2^6; rows of 7, exactly two cycles",
          "12 + 8 edges" in figs["indset"] and "13-clause" in figs["tseitin"] and "2<sup>6</sup>" in figs["tseitin"]
          and "3<i>k</i> + 1 = 7" in figs["ham-3sat"] and "exactly two Hamiltonian cycles" in figs["ham-3sat"])
    # concept pages
    check("concept pages: Related is the last line; examples present (5-cycle coloring 0,1,0,1,2; complement "
          "0 2 4 1 3; 9 clauses / 7 variables / 48 of 128)",
          all(c.strip().split("\n")[-1].startswith("Related:") for c in concepts.values())
          and has(concepts["np-hardness"], "$0, 1, 0, 1, 2$")
          and has(concepts["polynomial-time-reductions"], "$0\\,2\\,4\\,1\\,3$")
          and has(concepts["satisfiability"], "$1 + 2 + 2 + 4 = 9$ clauses on 7 variables", "48 of its 128",
                  "$3\\cdot 2^4 = 48$"))
    check("cook-levin-theorem and subset-sum link §12.3/§12.5 and §12.12, and np-hardness in Related",
          "#123-np-hard-np-easy-and-np-complete" in concepts["cook-levin-theorem"]
          and "#1212-subset-sum-from-vertex-cover" in concepts["subset-sum"]
          and all("[[concepts/np-hardness]]" in concepts[n].strip().split("\n")[-1]
                  for n in ("cook-levin-theorem", "subset-sum")))
    al = {}
    dup = []
    for root, _, files in os.walk(os.path.join(ROOT, "content")):
        for fn in files:
            if fn.endswith(".md"):
                mm = re.search(r"^aliases: \[(.*)\]$", read(os.path.join(root, fn)), re.M)
                if mm:
                    for x in re.findall(r'"([^"]+)"', mm.group(1)):
                        if x.lower() in al:
                            dup.append(x)
                        al[x.lower()] = fn
    check("aliases are unique site-wide (case-insensitive)", not dup, f"{dup}")

print()
if FAIL:
    print(f"{len(FAIL)} FAILED:")
    for f in FAIL:
        print("  -", f)
    sys.exit(1)
print("ALL OK")
