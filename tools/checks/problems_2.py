#!/usr/bin/env python3
"""Checks for five worked problems in content/problems/:

  state-elimination-by-hand.md            DFA -> regular expression, every intermediate expression automaton
  proving-what-a-grammar-generates.md     L(S -> 0S11 | 0S | eps) = {0^m 1^2n : m >= n >= 0}, every step of both inductions
  cnf-conversion-step-by-step.md          S -> SS | P | eps, P -> 0S1 to Chomsky normal form, every intermediate grammar
  designing-a-turing-machine.md           a one-tape TM for {w#w}, exhaustive simulation, traces, exact step counts
  undecidability-by-reduction-and-by-rice.md   the machines Y, N, M' (built for toy machines), the 374-step decider,
                                          the bounded look-alike, and the dovetailing acceptor
"""
import os
import random
import re
import sys
from math import comb

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from automata import DFA, NFA, Regex, CFG, TM, thompson, eliminate_states, strings, first_difference, EPS  # noqa: E402
from automata.core import equivalent  # noqa: E402
from automata.regex import to_str, _Parser, _u, _c, _s  # noqa: E402
from automata.tm import BLANK  # noqa: E402

FAIL = []


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAIL.append(name)


def section(title):
    print("\n# " + title)


# =====================================================================================================================
section("1. state elimination by hand")
# L = {w : #(0,w) - #(1,w) is divisible by 3}; state q_i means (#0 - #1) mod 3 = i.
inL1 = lambda w: (w.count("0") - w.count("1")) % 3 == 0
D = DFA("01", ["q0", "q1", "q2"], "q0", ["q0"],
        {("q0", "0"): "q1", ("q0", "1"): "q2", ("q1", "0"): "q2", ("q1", "1"): "q0",
         ("q2", "0"): "q0", ("q2", "1"): "q1"})
check("(a) the DFA accepts exactly L, |w| <= 14", first_difference(D.accepts, inL1, "01", 14) is None)
check("(a) state meanings: delta*(q0, w) = q_i with i = (#0 - #1) mod 3, |w| <= 12",
      all(D.delta_star("q0", w) == f"q{(w.count('0') - w.count('1')) % 3}" for w in strings("01", 12)))
check("(a) the DFA is minimal (3 states)", len(D.minimize().states) == 3)
check("(a) 0011 visits q0, q1, q2, q1, q0 (accept); 011 ends in q2 (reject)",
      D.run("0011") == ["q0", "q1", "q2", "q1", "q0"] and D.run("011")[-1] == "q2" and not D.accepts("011"))


def parse(text):
    return _Parser(text).parse()


def ea_nfa(edges, start="s", target="t"):
    """NFA for an expression automaton {(p, q): label}: one Thompson NFA per edge, glued with epsilon-edges."""
    delta, states = {}, set([start, target])

    def add(p, a, q):
        delta.setdefault((p, a), set()).add(q)

    for (p, q), lab in edges.items():
        states |= {p, q}
        sub = thompson(parse(lab), ["0", "1"])
        tag = (p, q)
        for (u, a), T in sub._delta.items():
            for v in T:
                add((tag, u), a, (tag, v))
        states |= {(tag, u) for u in sub.states}
        add(p, EPS, (tag, sub.start))
        for f in sub.accepting:
            add((tag, f), EPS, q)
    return NFA("01", sorted(states, key=str), start, {target}, delta)


def eliminate(edges, q):
    """One elimination step, R'(p->r) = R(p->r) + R(p->q) R(q->q)* R(q->r), on parsed labels."""
    R = {k: parse(v) for k, v in edges.items()}
    get = lambda p, r: R.get((p, r), ("empty",))
    nodes = {p for p, _ in R} | {r for _, r in R}
    loop = _s(get(q, q))
    out = {}
    for p in nodes - {q}:
        for r in nodes - {q}:
            lab = _u(get(p, r), _c(_c(get(p, q), loop), get(q, r)))
            if lab != ("empty",):
                out[(p, r)] = lab
    return out


def same_labels(mech, hand):
    """Every edge of the mechanical result has the hand-written label (exact regex equivalence), and vice versa."""
    if set(mech) != set(hand):
        return False, f"edges differ: {sorted(set(mech) ^ set(hand))}"
    for k in hand:
        a = Regex(to_str(mech[k]), "01")
        b = Regex(hand[k], "01")
        ok, wit = a.equivalent(b)
        if not ok:
            return False, f"{k}: {to_str(mech[k])} vs {hand[k]} differ on {wit!r}"
    return True, ""


# the expression automata exactly as on the page (order q1, q2, q0)
E0 = {("s", "q0"): "ε", ("q0", "t"): "ε", ("q0", "q1"): "0", ("q1", "q2"): "0", ("q2", "q0"): "0",
      ("q0", "q2"): "1", ("q2", "q1"): "1", ("q1", "q0"): "1"}
E1 = {("s", "q0"): "ε", ("q0", "t"): "ε", ("q0", "q0"): "01", ("q0", "q2"): "1+00", ("q2", "q0"): "0+11",
      ("q2", "q2"): "10"}
E2 = {("s", "q0"): "ε", ("q0", "t"): "ε", ("q0", "q0"): "01+(1+00)(10)*(0+11)"}
FINAL1 = "(01+(1+00)(10)*(0+11))*"
E3 = {("s", "t"): FINAL1}
Ddfa = D
for i, (E, name) in enumerate([(E0, "with s and t"), (E1, "after eliminating q1"), (E2, "after eliminating q2"),
                               (E3, "after eliminating q0")]):
    ok, wit = equivalent(ea_nfa(E).to_dfa(), Ddfa)
    check(f"(b) expression automaton {i} ({name}) accepts exactly L", ok, f"witness {wit!r}" if not ok else "")
for (Ea, q, Eb, nm) in [(E0, "q1", E1, "q1"), (E1, "q2", E2, "q2"), (E2, "q0", E3, "q0")]:
    ok, det = same_labels(eliminate(Ea, q), Eb)
    check(f"(b) eliminating {nm}: every new label is R(p->r) + R(p->q)R(q->q)*R(q->r), as written", ok, det)
check("(b) the library's state elimination in the order q1, q2, q0 prints the same expression",
      to_str(eliminate_states(D, ["q1", "q2", "q0"])) == FINAL1, to_str(eliminate_states(D, ["q1", "q2", "q0"])))
check("(b) final expression is exactly equivalent to the DFA", Regex(FINAL1, "01").equivalent(D)[0])
check("(b) eliminating q1 creates the loops 01 at q0 and 10 at q2 (the p = r cases)",
      E1[("q0", "q0")] == "01" and E1[("q2", "q2")] == "10")

# (c) sanity checks
R1 = Regex(FINAL1, "01")
check("(c) epsilon matches and is in L", R1("") and inL1(""))
for w in ["01", "10", "000", "111", "0011", "0101", "0110", "1001", "1010", "1100"]:
    check(f"(c) {w} is in L and matches", inL1(w) and R1(w))
for w in ["0", "1", "00", "001", "011", "0001", "0111"]:
    check(f"(c) {w} is not in L and does not match", not inL1(w) and not R1(w))
WRONG = Regex("((1+00)(0+11))*", "01")
check("(c) forgetting the p = r loops gives ((1+00)(0+11))*: a subset of L that misses (01)^k for every k >= 1",
      all(inL1(w) for w in strings("01", 12) if WRONG(w)) and all(not WRONG("01" * k) and inL1("01" * k)
                                                                   for k in range(1, 7)))
check("(c) the strings of length 3 in L are exactly 000 and 111",
      [w for w in strings("01", 3, 3) if inL1(w)] == ["000", "111"])
check("(c) the strings of length 4 in L are exactly the six with two 0s and two 1s",
      sorted(w for w in strings("01", 4, 4) if inL1(w)) == sorted(w for w in strings("01", 4, 4) if w.count("0") == 2))
diff = lambda w: w.count("0") - w.count("1")
check("(c) pieces: 1 and 00 contribute -1 and +2 (both = -1 mod 3); 0 and 11 contribute +1 and -2 (both = +1 mod 3); "
      "10 and 01 contribute 0", diff("1") % 3 == 2 and diff("00") % 3 == 2 and diff("0") % 3 == 1 and diff("11") % 3 == 1
      and diff("10") == 0 and diff("01") == 0)
BLOCK = Regex("01+(1+00)(10)*(0+11)", "01")


def first_return(w):
    if not w or D.delta_star("q0", w) != "q0":
        return False
    return all(D.delta_star("q0", w[:i]) != "q0" for i in range(1, len(w)))


check("(c) the block 01+(1+00)(10)*(0+11) matches exactly the walks q0 -> q0 that return to q0 only at the end "
      "(|w| <= 12)", first_difference(BLOCK, first_return, "01", 12) is None)

# (d) the other order: q0 first
A1 = {("s", "q1"): "0", ("s", "q2"): "1", ("s", "t"): "ε", ("q1", "q1"): "10", ("q1", "q2"): "0+11", ("q1", "t"): "1",
      ("q2", "q1"): "1+00", ("q2", "q2"): "01", ("q2", "t"): "0"}
A2 = {("s", "q2"): "1+0(10)*(0+11)", ("s", "t"): "ε+0(10)*1", ("q2", "q2"): "01+(1+00)(10)*(0+11)",
      ("q2", "t"): "0+(1+00)(10)*1"}
FINAL2 = "ε+0(10)*1+(1+0(10)*(0+11))(01+(1+00)(10)*(0+11))*(0+(1+00)(10)*1)"
A3 = {("s", "t"): FINAL2}
for (Ea, q, Eb) in [(E0, "q0", A1), (A1, "q1", A2), (A2, "q2", A3)]:
    ok, det = same_labels(eliminate(Ea, q), Eb)
    check(f"(d) order q0, q1, q2: eliminating {q} gives the labels as written", ok, det)
for i, E in enumerate([A1, A2, A3], 1):
    check(f"(d) order q0, q1, q2: expression automaton after step {i} accepts exactly L",
          equivalent(ea_nfa(E).to_dfa(), D)[0])
check("(d) the library prints the same expression for the order q0, q1, q2",
      to_str(eliminate_states(D, ["q0", "q1", "q2"])) == FINAL2)
check("(d) the long expression is exactly equivalent to the short one",
      Regex(FINAL2, "01").equivalent(Regex(FINAL1, "01"))[0])
nsym = lambda s: sum(ch in "01" for ch in s)
check("(d) symbol counts: 10 for the order q1, q2, q0 and 28 for q0, q1, q2; characters 23 and 65",
      (nsym(FINAL1), nsym(FINAL2), len(FINAL1), len(FINAL2)) == (10, 28, 23, 65),
      f"{nsym(FINAL1)}, {nsym(FINAL2)}, {len(FINAL1)}, {len(FINAL2)}")
MIRROR = "(10+(0+11)(01)*(1+00))*"
check("(d) the order q2, q1, q0 gives the mirror image (10+(0+11)(01)*(1+00))*",
      to_str(eliminate_states(D, ["q2", "q1", "q0"])) == MIRROR and Regex(MIRROR, "01").equivalent(D)[0])
orders = {}
for order in [("q1", "q2", "q0"), ("q2", "q1", "q0"), ("q1", "q0", "q2"), ("q2", "q0", "q1"), ("q0", "q1", "q2"),
              ("q0", "q2", "q1")]:
    e = to_str(eliminate_states(D, list(order)))
    orders[order] = nsym(e)
    check(f"(d) order {', '.join(order)}: result exactly equivalent to the DFA ({nsym(e)} symbols)",
          Regex(e, "01").equivalent(D)[0], e)
check("(d) symbol counts by order: q0 last 10, q0 in the middle 22, q0 first 28",
      orders[("q1", "q2", "q0")] == orders[("q2", "q1", "q0")] == 10
      and orders[("q1", "q0", "q2")] == orders[("q2", "q0", "q1")] == 22
      and orders[("q0", "q1", "q2")] == orders[("q0", "q2", "q1")] == 28, str(orders))

# =====================================================================================================================
section("2. proving what a grammar generates")
G2 = CFG.parse("S -> 0S11 | 0S | ε")


def inL2(w):
    m = re.fullmatch(r"(0*)(1*)", w)
    if not m:
        return False
    a, b = len(m.group(1)), len(m.group(2))
    return b % 2 == 0 and a >= b // 2


check("L(G) = {0^m 1^2n : m >= n >= 0} on all strings of length <= 14",
      first_difference(lambda w: G2.generates(w), inL2, "01", 14) is None)
small = sorted((w for w in strings("01", 6) if G2.generates(w)), key=lambda w: (len(w), w))
check("the strings of L(G) of length <= 6 are as listed",
      small == ["", "0", "00", "000", "011", "0000", "0011", "00000", "00011", "000000", "000011", "001111"],
      str(small))
check("0111 and 01111 are not generated (odd number of 1s; too few 0s)",
      not G2.generates("0111") and not G2.generates("01111") and not inL2("0111") and not inL2("01111"))

# (a) L subset of L(G): the derivation built by the proof, for every (m, n) with m >= n >= 0, m + 2n <= 16
RULES2 = {"S": ["0S11", "0S", ""]}


def derive(m, n):
    """Sentential forms of the derivation built in part (a)."""
    if m == 0:  # then n = 0
        assert n == 0
        return ["S", ""]
    if n == 0:  # S -> 0S, then the derivation of 0^(m-1) inside the context 0_
        return ["S"] + ["0" + f for f in derive(m - 1, 0)]
    return ["S"] + ["0" + f + "11" for f in derive(m - 1, n - 1)]


def valid_derivation(forms, rules):
    for x, y in zip(forms, forms[1:]):
        i = x.find("S")
        if i < 0 or not any(x[:i] + r + x[i + 1:] == y for r in rules["S"]):
            return False
    return "S" not in forms[-1]


ok = True
for m in range(0, 17):
    for n in range(0, m + 1):
        if m + 2 * n > 16:
            continue
        f = derive(m, n)
        ok = ok and valid_derivation(f, RULES2) and f[-1] == "0" * m + "1" * (2 * n) and len(f) - 1 == m + 1
check("(a) the derivation built by the proof is valid and yields 0^m 1^2n (m >= n, m + 2n <= 16), in m + 1 steps", ok)
check("(a) the cases m = 0 / m >= 1, n = 0 / m >= 1, n >= 1 are exhaustive, and m = 0 forces n = 0",
      all((m == 0 and n == 0) or (m >= 1 and n == 0) or (m >= 1 and n >= 1) for m in range(30) for n in range(m + 1)))
check("(a) in the third case (m-1, n-1) again satisfies m-1 >= n-1 >= 0, and 0 . 0^(m-1) 1^(2n-2) . 11 = 0^m 1^2n",
      all(m - 1 >= n - 1 >= 0 and "0" + "0" * (m - 1) + "1" * (2 * n - 2) + "11" == "0" * m + "1" * (2 * n)
          for m in range(1, 30) for n in range(1, m + 1)))
check("(a) derivation of 00011 (m = 3, n = 1): S, 0S11, 00S11, 000S11, 00011",
      derive(3, 1) == ["S", "0S11", "00S11", "000S11", "00011"], str(derive(3, 1)))

# (b) L(G) subset of L: the closure facts used in the cases, and the decomposition
L2_12 = [w for w in strings("01", 12) if inL2(w)]
check("(b) x in L implies 0x11 in L and 0x in L (|x| <= 12)", all(inL2("0" + x + "11") and inL2("0" + x) for x in L2_12))
check("(b) for x = 0^m 1^2n: 0x11 = 0^(m+1) 1^(2(n+1)) and 0x = 0^(m+1) 1^2n",
      all("0" + "0" * m + "1" * (2 * n) + "11" == "0" * (m + 1) + "1" * (2 * (n + 1)) for m in range(12) for n in range(m + 1)))
ok = True
for w in strings("01", 12):
    if G2.generates(w):
        ok = ok and (w == "" or (w[0] == "0" and (G2.generates(w[1:]) or (w.endswith("11") and len(w) >= 3
                                                                        and G2.generates(w[1:-2])))))
check("(b) every non-empty w in L(G) is 0x with x in L(G), or 0x11 with x in L(G) (|w| <= 12)", ok)
check("(b trap) 0011 also has the derivation S, 0S, 00S11, 0011 (its first rule is S -> 0S)",
      valid_derivation(["S", "0S", "00S11", "0011"], RULES2))
check("(b) 011 = 0 . eps . 11: the inner string may be empty", G2.generates("011") and G2.generates(""))
G2bad = CFG.parse("S -> 0S11 | 0S | SS | ε")
check("(trap) adding S -> SS breaks the claim: 0110 is generated but is not in L",
      G2bad.generates("0110") and not inL2("0110"))


# (c) ambiguity: parse trees
def trees_G(w):
    t = 1 if w == "" else 0
    if w.startswith("0"):
        t += trees_G(w[1:])
        if w.endswith("11") and len(w) >= 3:
            t += trees_G(w[1:-2])
    return t


check("(c) 0011 has exactly two parse trees", trees_G("0011") == 2)
check("(c) 0^m 1^2n has exactly C(m, n) parse trees (m + 2n <= 14)",
      all(trees_G("0" * m + "1" * (2 * n)) == comb(m, n) for m in range(15) for n in range(m + 1) if m + 2 * n <= 14))
GU = CFG.parse("S -> 0S | T\nT -> 0T11 | ε")
check("(c) S -> 0S | T, T -> 0T11 | eps generates the same language (|w| <= 14)",
      first_difference(lambda w: GU.generates(w), inL2, "01", 14) is None)


def trees_U_T(w):
    t = 1 if w == "" else 0
    if w.startswith("0") and w.endswith("11") and len(w) >= 3:
        t += trees_U_T(w[1:-2])
    return t


def trees_U_S(w):
    return (trees_U_S(w[1:]) if w.startswith("0") else 0) + trees_U_T(w)


check("(c) ... and every string of the language has exactly one parse tree in it (|w| <= 14)",
      all(trees_U_S(w) == (1 if inL2(w) else 0) for w in strings("01", 14)))

# =====================================================================================================================
section("3. CNF conversion")


def G(text, start):
    """Grammar from 'A -> X Y | a | ε ; B -> ...' with space-separated symbols (names like S', T0 allowed)."""
    rules = {}
    for part in text.split(";"):
        lhs, rhs = part.split("->")
        A = lhs.strip()
        rules[A] = []
        for alt in rhs.split("|"):
            alt = alt.strip()
            rules[A].append(() if alt == "ε" else tuple(alt.split()))
    return CFG(start, rules, terminals=["0", "1"])


def balanced(w):
    h = 0
    for c in w:
        h += 1 if c == "0" else -1
        if h < 0:
            return False
    return h == 0


STAGES = [
    ("original", G("S -> S S | P | ε ; P -> 0 S 1", "S")),
    ("step 0", G("S' -> S ; S -> S S | P | ε ; P -> 0 S 1", "S'")),
    ("step 1", G("S' -> S ; S -> S S | P | ε ; P -> 0 B ; B -> S 1", "S'")),
    ("step 3", G("S' -> S | ε ; S -> S S | S | P ; P -> 0 B ; B -> S 1 | 1", "S'")),
    ("step 4", G("S' -> S | ε ; S -> S S | P ; P -> 0 B ; B -> S 1 | 1", "S'")),
    ("step 5", G("S' -> S S | 0 B | ε ; S -> S S | 0 B ; P -> 0 B ; B -> S 1 | 1", "S'")),
    ("step 5, P deleted", G("S' -> S S | 0 B | ε ; S -> S S | 0 B ; B -> S 1 | 1", "S'")),
    ("step 6", G("S' -> S S | T0 B | ε ; S -> S S | T0 B ; B -> S T1 | 1 ; T0 -> 0 ; T1 -> 1", "S'")),
]
for name, g in STAGES:
    check(f"{name}: generates exactly the balanced strings (|w| <= 12)",
          first_difference(lambda w: g.generates(w), balanced, "01", 12) is None)
g_orig, g1 = STAGES[0][1], STAGES[2][1]
check("original: P generates exactly the strings 0x1 with x balanced (|w| <= 12)",
      all(g_orig.generates(w, "P") == (len(w) >= 2 and w[0] == "0" and w[-1] == "1" and balanced(w[1:-1]))
          for w in strings("01", 12)))
check("step 2: the nullable nonterminals are exactly S and S'", g1.nullable() == {"S", "S'"}, str(g1.nullable()))
g3, g4, g5, g6 = STAGES[3][1], STAGES[4][1], STAGES[5][1], STAGES[7][1]
check("step 3: the only epsilon-rule left is S' -> eps",
      [A for A, rhs in g3.rules.items() for r in rhs if r == ()] == ["S'"])
check("step 3 created the unit rule S -> S (from S -> SS)", ("S",) in g3.rules["S"])
check("step 4: no unit rule S -> S; the unit rules are S' -> S and S -> P",
      sorted((A, r[0]) for A, rhs in g4.rules.items() for r in rhs if len(r) == 1 and r[0] in g4.rules)
      == [("S", "P"), ("S'", "S")])
check("step 5: no unit rules left",
      not any(len(r) == 1 and r[0] in g5.rules for rhs in g5.rules.values() for r in rhs))
check("step 5: P is unreachable from S'", all("P" not in r for A, rhs in g5.rules.items() if A != "P" for r in rhs))
check("step 6: the result is in Chomsky normal form", g6.is_cnf() == (True, None), str(g6.is_cnf()))
for g_name, (name, g) in [("step 5", STAGES[5]), ("step 1", STAGES[2]), ("original", STAGES[0])]:
    check(f"{name} is not yet in Chomsky normal form", not g.is_cnf()[0], str(g.is_cnf()))
check("final grammar: S generates the non-empty balanced strings (|w| <= 12)",
      all(g6.generates(w, "S") == (balanced(w) and w != "") for w in strings("01", 12)))
check("final grammar: B generates the strings x1 with x balanced (|w| <= 12)",
      all(g6.generates(w, "B") == (w.endswith("1") and balanced(w[:-1])) for w in strings("01", 12)))
check("final grammar: 7 nonterminal-free rules count: S' has 3 rules, S 2, B 2, T0 1, T1 1",
      [len(g6.rules[A]) for A in ["S'", "S", "B", "T0", "T1"]] == [3, 2, 2, 1, 1])
# a leftmost derivation of 0011 in the final grammar
FORMS = [["S'"], ["T0", "B"], ["0", "B"], ["0", "S", "T1"], ["0", "T0", "B", "T1"], ["0", "0", "B", "T1"],
         ["0", "0", "1", "T1"], ["0", "0", "1", "1"]]


def leftmost_ok(forms, g):
    for x, y in zip(forms, forms[1:]):
        i = next((k for k, s in enumerate(x) if s in g.rules), None)
        if i is None or not any(x[:i] + list(r) + x[i + 1:] == y for r in g.rules[x[i]]):
            return False
    return all(s not in g.rules for s in forms[-1])


def splits_ok(w):
    # a non-empty balanced w is 0x1 with x balanced, or a concatenation of two non-empty balanced strings
    return (w[0] == "0" and w[-1] == "1" and balanced(w[1:-1])) or any(balanced(w[:i]) and balanced(w[i:])
                                                                       for i in range(1, len(w)))


check("every non-empty balanced string is 0x1 (x balanced) or a concatenation of two non-empty balanced strings "
      "(|w| <= 14)", all(splits_ok(w) for w in strings("01", 14) if w and balanced(w)))
check("a non-empty balanced string with no shorter non-empty balanced prefix is 0x1 with x balanced (|w| <= 14)",
      all(w[0] == "0" and w[-1] == "1" and balanced(w[1:-1]) for w in strings("01", 14)
          if w and balanced(w) and not any(balanced(w[:i]) for i in range(1, len(w)))))
check("final grammar: the leftmost derivation of 0011 shown is valid and has 7 = 2*4 - 1 steps",
      leftmost_ok(FORMS, g6) and len(FORMS) - 1 == 7 and "".join(FORMS[-1]) == "0011")
# traps
g3_noB1 = G("S' -> S | ε ; S -> S S | S | P ; P -> 0 B ; B -> S 1", "S'")
check("(trap) forgetting B -> 1 in step 3 leaves only the empty string (|w| <= 12)",
      [w for w in strings("01", 12) if g3_noB1.generates(w)] == [""])
g5_wrong = G("S' -> S S | P | ε ; S -> S S | 0 B ; P -> 0 B ; B -> S 1 | 1", "S'")
check("(trap) processing S' before S in step 5 leaves the unit rule S' -> P (not CNF), same language",
      not g5_wrong.is_cnf()[0] and first_difference(lambda w: g5_wrong.generates(w), balanced, "01", 10) is None)
g_noprime = G("S -> S S | T0 B | ε ; B -> S T1 | 1 ; T0 -> 0 ; T1 -> 1", "S")
check("(trap) without the new start symbol, S -> eps and S on right sides: not CNF",
      not g_noprime.is_cnf()[0])

# =====================================================================================================================
section("4. a Turing machine for {w#w}")
TMD = {}
TMD[("start", "0")] = ("carry0", "x", +1)
TMD[("start", "1")] = ("carry1", "x", +1)
TMD[("start", "#")] = ("check", "#", +1)
for c in "01":
    TMD[(f"carry{c}", "0")] = (f"carry{c}", "0", +1)
    TMD[(f"carry{c}", "1")] = (f"carry{c}", "1", +1)
    TMD[(f"carry{c}", "#")] = (f"seek{c}", "#", +1)
    TMD[(f"seek{c}", "x")] = (f"seek{c}", "x", +1)
    TMD[(f"seek{c}", c)] = ("backR", "x", -1)
TMD[("backR", "x")] = ("backR", "x", -1)
TMD[("backR", "#")] = ("backL", "#", -1)
TMD[("backL", "0")] = ("backL", "0", -1)
TMD[("backL", "1")] = ("backL", "1", -1)
TMD[("backL", "x")] = ("start", "x", +1)
TMD[("check", "x")] = ("check", "x", +1)
TMD[("check", BLANK)] = ("accept", BLANK, +1)
COPY = TM(TMD)
check("the table has 20 transitions and 8 non-halting states", len(TMD) == 20 and len({p for p, _ in TMD}) == 8)


def in_copy(s):
    if s.count("#") != 1:
        return False
    a, b = s.split("#")
    return a == b


ok, outs, worst = True, {}, {}
for n in range(0, 11):
    for s in strings("01#", n, n):
        out, steps, tape, head = COPY.run(s, max_steps=5000)
        outs[out] = outs.get(out, 0) + 1
        ok = ok and out in ("accept", "reject") and (out == "accept") == in_copy(s)
        worst[n] = max(worst.get(n, 0), steps)
check("decides {w#w}: on all 88573 inputs over {0,1,#} of length <= 10 it accepts exactly the members and rejects "
      "the rest (never crashes, never runs on)", ok and sum(outs.values()) == 88573, str(outs))
check("on every input of length n <= 10 it halts within 2n^2 + 3n + 2 steps (the bound in (d))",
      all(worst[n] <= 2 * n * n + 3 * n + 2 for n in worst), str(worst))
check("exact count: on w#w with |w| = k it takes 2(k+1)^2 steps, for every w with k <= 7",
      all(COPY.run(w + "#" + w)[1] == 2 * (k + 1) ** 2 for k in range(8) for w in strings("01", k, k)))
check("even lengths: on w#w0 (n = 2k + 2) it rejects after 2(k+1)^2 = n^2/2 steps, for every w with k <= 7",
      all(COPY.run(w + "#" + w + "0")[:2] == ("reject", 2 * (k + 1) ** 2) and 2 * (k + 1) ** 2 == (2 * k + 2) ** 2 // 2
          for k in range(8) for w in strings("01", k, k)))
ok = True
for k in range(1, 8):
    for w in strings("01", k, k):
        confs = COPY.run(w + "#" + w, trace=True)[4]
        starts = [t for t, (q, tape, h) in enumerate(confs) if q == "start"]
        ok = ok and starts == [i * (2 * k + 3) for i in range(k + 1)]
check("every round takes exactly 2k + 3 steps (state start is entered at steps 0, 2k+3, 2(2k+3), ...), k <= 7", ok)
check("on 01#01 it accepts after 18 steps; on ε it rejects at once (no #); on # it accepts after 2 steps",
      COPY.run("01#01")[:2] == ("accept", 18) and COPY.run("")[0] == "reject" and COPY.run("#")[:2] == ("accept", 2))


def fmt_conf(q, tape, h):
    cells = list(tape) + [BLANK] * (h + 1 - len(tape))
    return q, "".join(cells[:h]) + "[" + cells[h] + "]" + "".join(cells[h + 1:])


TRACE = ["start [0]1#01", "carry0 x[1]#01", "carry0 x1[#]01", "seek0 x1#[0]1", "backR x1[#]x1", "backL x[1]#x1",
         "backL [x]1#x1", "start x[1]#x1", "carry1 xx[#]x1", "seek1 xx#[x]1", "seek1 xx#x[1]", "backR xx#[x]x",
         "backR xx[#]xx", "backL x[x]#xx", "start xx[#]xx", "check xx#[x]x", "check xx#x[x]", "check xx#xx[□]",
         "accept xx#xx□[□]"]
confs = COPY.run("01#01", trace=True)[4]
got = [" ".join(fmt_conf(*c)) for c in confs]
check("the trace on 01#01 is as in the table (19 configurations)", got == TRACE, " | ".join(got))
out = COPY.run("01#00", trace=True)
check("on 01#00 it rejects in step 11: seek1 reads 0 in cell 4 (no transition)",
      out[0] == "reject" and out[1] == 11 and fmt_conf(*out[4][-2]) == ("seek1", "xx#x[0]"),
      f"{out[:2]} {fmt_conf(*out[4][-2])}")
for s, why in [("0#0#", "check reads the second #"), ("0##0", "seek0 reads #"), ("0#", "seek0 reads a blank"),
               ("01", "carry0 reads a blank"), ("#0", "check reads 0"), ("0#1", "seek0 reads 1")]:
    check(f"rejects {s} ({why})", COPY.run(s)[0] == "reject")

# =====================================================================================================================
section("5. undecidability: the machines on the page")
SYMS = ["0", "1", BLANK]
Y = TM({("start", a): ("accept", a, +1) for a in SYMS})
N = TM({("start", a): ("reject", a, +1) for a in SYMS})
check("Y = M_Accept accepts every string over {0,1} of length <= 8, in one step",
      all(Y.run(w)[:2] == ("accept", 1) for w in strings("01", 8)))
check("N = M_Reject rejects every string over {0,1} of length <= 8, in one step",
      all(N.run(w)[:2] == ("reject", 1) for w in strings("01", 8)))
check("Accept(Y) has at least two strings; Accept(N) is empty", Y.accepts("0") and Y.accepts("1")
      and not any(N.accepts(w) for w in strings("01", 8)))


def build_Mprime(M, w, gamma):
    """The machine M' of part (a), as a real one-tape TM: erase the input x (marking cell 0), write w,
    return to cell 0, then run M; M's accept/reject are M'' accept/reject."""
    mark = lambda c: c + "^"
    d = {}
    for c in ["0", "1", BLANK]:
        d[("pre-mark", c)] = ("pre-erase", mark(c), +1)
    for c in ["0", "1"]:
        d[("pre-erase", c)] = ("pre-erase", BLANK, +1)
    d[("pre-erase", BLANK)] = ("pre-back", BLANK, -1)
    d[("pre-back", BLANK)] = ("pre-back", BLANK, -1)
    first = w[0] if w else BLANK
    nxt = ("pre-write", 1) if len(w) > 1 else "pre-ret"
    for c in ["0", "1", BLANK]:
        d[("pre-back", mark(c))] = (nxt, mark(first), +1)
    for j in range(1, len(w)):
        after = ("pre-write", j + 1) if j + 1 < len(w) else "pre-ret"
        for c in gamma:
            d[(("pre-write", j), c)] = (after, w[j], +1)
    for c in ["0", "1", BLANK]:
        d[("pre-ret", c)] = ("pre-ret", c, -1)
        d[("pre-ret", mark(c))] = ("pre-go", c, +1)
    for c in gamma:
        d[("pre-go", c)] = (("M", M.start), c, -1)
    for (p, a), (q, b, mv) in M.delta.items():
        q2 = "accept" if q == M.accept else "reject" if q == M.reject else ("M", q)
        d[(("M", p), a)] = (q2, b, mv)
    return TM(d, start="pre-mark")


# toy machines over {0,1}
M_loop = TM({("start", a): ("start", a, +1) for a in SYMS})  # runs right forever
M_even = TM({("start", "0"): ("odd", "0", +1), ("start", "1"): ("odd", "1", +1), ("start", BLANK): ("accept", BLANK, +1),
             ("odd", "0"): ("start", "0", +1), ("odd", "1"): ("start", "1", +1), ("odd", BLANK): ("reject", BLANK, +1)})
# accepts strings ending in 0, diverges on strings ending in 1, rejects the empty string
M_mix = TM({("start", "0"): ("last0", "0", +1), ("start", "1"): ("last1", "1", +1), ("start", BLANK): ("reject", BLANK, +1),
            ("last0", "0"): ("last0", "0", +1), ("last0", "1"): ("last1", "1", +1), ("last0", BLANK): ("accept", BLANK, +1),
            ("last1", "0"): ("last0", "0", +1), ("last1", "1"): ("last1", "1", +1), ("last1", BLANK): ("spin", BLANK, +1),
            ("spin", BLANK): ("spin", BLANK, +1)})
CAP = 3000
ok, cases = True, 0
for M in [Y, N, M_loop, M_even, M_mix]:
    for w in ["", "0", "1", "01", "10", "11", "000", "0110"]:
        r = M.run(w, max_steps=CAP)[0]
        Mp = build_Mprime(M, w, SYMS)
        for x in strings("01", 5):
            o = Mp.run(x, max_steps=CAP)[0]
            expect = {"accept": "accept", "reject": "reject", "timeout": "timeout"}[r]
            ok = ok and o == expect
            cases += 1
check(f"M' built from (M, w) for 5 toy machines and 8 strings w: on every input x (|x| <= 5) M' accepts if M accepts "
      f"w, rejects if M rejects w, and runs on if M runs on ({cases} runs)", ok)

# (c) Quick374: does M halt on the empty input within 374 steps?
quick374 = lambda M: M.run("", max_steps=374)[0] in ("accept", "reject")


def walker(k, final="accept"):
    """Walk right for k steps, then halt in `final`."""
    d = {}
    for i in range(k):
        for a in SYMS:
            d[(i, a)] = (i + 1 if i + 1 < k else final, a, +1)
    return TM(d, start=0)


M_slow = walker(400)
check("M_slow accepts every input (|x| <= 6), so Accept(M_slow) = Accept(M_Accept)",
      all(M_slow.accepts(x) for x in strings("01", 6)))
check("on the empty input M_Accept halts after 1 step and M_slow after 400",
      Y.run("")[1] == 1 and M_slow.run("")[:2] == ("accept", 400))
check("so M_Accept is in Quick374 and M_slow is not", quick374(Y) and not quick374(M_slow))
check("boundary: halting at step 374 counts, at step 375 does not",
      quick374(walker(374)) and not quick374(walker(375)) and quick374(walker(374, "reject")))
check("M_loop (runs right forever) is not in Quick374", not quick374(M_loop))

# the bounded look-alike: within t steps the head never reads beyond cell t-1, so acceptance within t steps of a
# string of length >= t depends only on its first t symbols (tested with t = 5 on random small machines)
random.seed(374)
t, ok, tested = 5, True, 0
for _ in range(400):
    states = ["start", "a", "b"]
    d = {}
    for p in states:
        for a in SYMS:
            if random.random() < 0.9:
                q = random.choice(states + ["accept", "reject"])
                d[(p, a)] = (q, random.choice(SYMS), random.choice([-1, +1]))
    M = TM(d)
    within = lambda x: (lambda r: r[0] == "accept" and r[1] <= t)(M.run(x, max_steps=t))
    for x in strings("01", 8, t):
        tested += 1
        ok = ok and within(x) == within(x[:t])
check(f"bounded look-alike: acceptance within {t} steps depends only on the first {t} symbols "
      f"(400 random machines, {tested} strings)", ok)

# (d) dovetailing acceptor for AtLeastTwo
SHORTLEX = list(strings("01", 10))


def dovetail_two(M, rounds):
    """Round t: run M for t steps on each of the first t strings (shortlex). Return the round in which two different
    accepted strings have been seen, or None if that does not happen within `rounds` rounds."""
    for r in range(1, rounds + 1):
        acc = {x for x in SHORTLEX[:r] if (lambda o: o[0] == "accept")(M.run(x, max_steps=r))}
        if len(acc) >= 2:
            return r
    return None


M_loop_eps = TM({("start", BLANK): ("start", BLANK, +1), ("start", "0"): ("accept", "0", +1),
                 ("start", "1"): ("accept", "1", +1)})  # diverges on ε, accepts every non-empty string
M_one = TM({("start", "0"): ("z", "0", +1), ("z", BLANK): ("accept", BLANK, +1)})  # accepts only "0"
check("dovetailing accepts M_Accept (in round 2)", dovetail_two(Y, 50) == 2)
check("dovetailing accepts a machine that diverges on ε but accepts 0 and 1",
      dovetail_two(M_loop_eps, 50) is not None and M_loop_eps.run("", max_steps=10000)[0] == "timeout")
check("dovetailing never accepts M_Reject, M_loop, or a machine accepting only the string 0 (100 rounds)",
      all(dovetail_two(M, 100) is None for M in [N, M_loop, M_one]) and M_one.accepts("0")
      and not any(M_one.accepts(x) for x in strings("01", 8) if x != "0"))

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: {FAIL}")
sys.exit(1 if FAIL else 0)
