#!/usr/bin/env python3
"""Checks for every concrete claim on content/practice/05-context-free-languages.md.

Brute-force predicates are written from the problem statements, independently of the answers.
Grammars are compared with those predicates on all strings up to length 10-14 (Earley recognizer of
tools/automata). Parse trees are counted by a DP that allows epsilon-rules (cross-checked against the
library's count_parse_trees on epsilon-free grammars and against an enumeration of leftmost
derivations). The closure construction of 5.1(b) and the DFA-to-grammar construction of 5.1(f) are
implemented as functions and tested on random grammars and DFAs."""
import os
import random
import re
import sys
from collections import deque
from functools import lru_cache

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from automata import CFG, DFA, strings, first_difference  # noqa: E402

FAIL = []


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAIL.append(name)


# ================================================================== helpers
def G(text, nts=None, start=None, terminals=None):
    return CFG.parse(text, start=start, nonterminals=nts, terminals=terminals)


def same(g, pred, alphabet, maxlen, start=None):
    """None if g (from `start`) and pred agree on all strings up to maxlen, else the first difference."""
    return first_difference(lambda w: g.generates(w, start), pred, alphabet, maxlen)


def ok_same(name, g, pred, alphabet, maxlen, start=None):
    d = same(g, pred, alphabet, maxlen, start)
    check(name + f" (all strings up to length {maxlen})", d is None, "" if d is None else f"differs on {d!r}")


def tok(g, s):
    """Tokenize a sentential form: longest nonterminal name first, else one character; ε = nothing."""
    names = sorted(g.rules, key=lambda x: -len(str(x)))
    out, i = [], 0
    while i < len(s):
        if s[i] == "ε":
            i += 1
            continue
        for nm in names:
            if isinstance(nm, str) and s.startswith(nm, i):
                out.append(nm)
                i += len(nm)
                break
        else:
            out.append(s[i])
            i += 1
    return tuple(out)


def is_derivation(g, forms, leftmost=True):
    """Each consecutive pair of sentential forms is one (leftmost) derivation step."""
    fs = [tok(g, f) for f in forms]
    if fs[0] != (g.start,):
        return False
    for a, b in zip(fs, fs[1:]):
        idx = [i for i, x in enumerate(a) if x in g.rules]
        if leftmost:
            idx = idx[:1]
        if not any(a[:i] + tuple(r) + a[i + 1:] == b for i in idx for r in g.rules[a[i]]):
            return False
    return True


class Infinite(Exception):
    pass


def count_trees(g, w, start=None):
    """Number of parse trees of w (epsilon-rules allowed); raises Infinite on a derivation cycle."""
    start = start or g.start
    memo, busy = {}, set()
    nul = g.nullable()

    def cnt(X, i, j):
        if X not in g.rules:
            return 1 if (j == i + 1 and w[i] == X) else 0
        if i == j and X not in nul:
            return 0
        key = (X, i, j)
        if key in memo:
            return memo[key]
        if key in busy:
            raise Infinite(key)
        busy.add(key)
        total = sum(seq(r, 0, i, j) for r in g.rules[X])
        busy.discard(key)
        memo[key] = total
        return total

    def seq(r, k, i, j):
        if k == len(r):
            return 1 if i == j else 0
        if k == len(r) - 1:
            return cnt(r[k], i, j)
        total = 0
        hi = j - sum(1 for x in r[k + 1:] if x not in nul)  # each later non-nullable symbol needs >= 1 symbol
        for m in range(i if r[k] in nul else i + 1, hi + 1):
            c = cnt(r[k], i, m)
            if c:
                total += c * seq(r, k + 1, m, j)
        return total

    return cnt(start, 0, len(w))


def leftmost_derivations(g, w, start=None):
    """Lengths of all leftmost derivations of w (only for grammars where every derivation is finite)."""
    start = start or g.start

    @lru_cache(maxsize=None)
    def go(form):
        terms = sum(1 for x in form if x not in g.rules)
        if terms > len(w):
            return ()
        k = next((i for i, x in enumerate(form) if x in g.rules), None)
        if k is None:
            return (0,) if "".join(form) == w else ()
        if not w.startswith("".join(form[:k])):
            return ()
        out = []
        for r in g.rules[form[k]]:
            out += [n + 1 for n in go(form[:k] + tuple(r) + form[k + 1:])]
        return tuple(out)

    return list(go((start,)))


def rules_set(g):
    return {(A, tuple(r)) for A in g.rules for r in g.rules[A]}


def binval(x):
    return int(x, 2) if x else 0


# ---- library cross-checks of the tree counter (epsilon-free grammars, no unit rules)
rng = random.Random(374)
agree = True
for _ in range(60):
    rules = {}
    for A in "SAB":
        rs = []
        for _k in range(rng.randint(1, 3)):
            if rng.random() < 0.3:
                rs.append((rng.choice("01"),))
            else:
                rs.append(tuple(rng.choice("01SAB") for _m in range(rng.randint(2, 3))))
        rules[A] = rs
    g = CFG("S", rules, terminals="01")
    for w in strings("01", 6):
        if count_trees(g, w) != g.count_parse_trees(w):
            agree = False
check("tree counter agrees with CFG.count_parse_trees on 60 random epsilon-free grammars, |w| <= 6", agree)

# ================================================================== 5.1 true or false
print("\n# 5.1")
# (a) Sigma* is context-free
ok_same("(a) S -> 0S | 1S | ε generates every binary string", G("S -> 0S | 1S | ε"), lambda w: True, "01", 10)


# (c) the complement of {0^n 1^n 0^n} is context-free
def in_0n1n0n(w):
    n = len(w) // 3
    return len(w) % 3 == 0 and w == "0" * n + "1" * n + "0" * n


COMP = G("""S -> N | UZ | ZV
N -> X1X0X1X
X -> 0X | 1X | ε
Z -> 0Z | ε
Y -> 1Y | ε
U -> 0U1 | 0Z | Y1
V -> 1V0 | 1Y | Z0""")
ok_same("(c) S -> N | UZ | ZV generates exactly the complement of {0^n1^n0^n}", COMP, lambda w: not in_0n1n0n(w), "01", 13)
ok_same("(c) N generates exactly the strings not in 0*1*0*", COMP, lambda w: re.fullmatch("0*1*0*", w) is None, "01", 12, "N")
ok_same("(c) U generates {0^a 1^b : a != b}", COMP,
        lambda w: re.fullmatch("0*1*", w) is not None and w.count("0") != w.count("1"), "01", 12, "U")
ok_same("(c) V generates {1^b 0^c : b != c}", COMP,
        lambda w: re.fullmatch("1*0*", w) is not None and w.count("0") != w.count("1"), "01", 12, "V")


# (b) context-free ∩ regular: the triple construction, tested on random grammars and DFAs
def intersect(g, M):
    """Grammar with nonterminals (p, A, q): strings of L(A) that drive M from p to q; start ('start',)."""
    Q = list(M.states)
    rules = {(p, A, q): [] for p in Q for A in g.rules for q in Q}
    for A, rhs in g.rules.items():
        for r in rhs:
            if not r:
                for p in Q:
                    rules[(p, A, p)].append(())
                continue

            def build(k, p, acc, p0, A=A, r=r):
                if k == len(r):
                    rules[(p0, A, p)].append(tuple(acc))
                    return
                X = r[k]
                if X in g.rules:
                    for q in Q:
                        build(k + 1, q, acc + [(p, X, q)], p0)
                else:
                    build(k + 1, M.delta(p, X), acc + [X], p0)

            for p0 in Q:
                build(0, p0, [], p0)
    rules[("start",)] = [((M.start, g.start, f),) for f in M.accepting]
    return CFG(("start",), rules, terminals=M.alphabet)


def random_dfa(rng, alphabet="01"):
    k = rng.randint(1, 3)
    delta = {(q, a): rng.randrange(k) for q in range(k) for a in alphabet}
    acc = [q for q in range(k) if rng.random() < 0.5]
    return DFA(alphabet, range(k), 0, acc, delta)


def random_grammar(rng, eps=True):
    rules = {}
    for A in "SAB":
        rs = []
        for _k in range(rng.randint(1, 3)):
            n = rng.randint(0 if eps else 1, 3)
            rs.append(tuple(rng.choice("01SAB") for _m in range(n)))
        rules[A] = rs
    return CFG("S", rules, terminals="01")


rng = random.Random(5)
bad = None
for t in range(200):
    g, M = random_grammar(rng), random_dfa(rng)
    gi = intersect(g, M)
    for w in strings("01", 6):
        if gi.generates(w) != (g.generates(w) and M.accepts(w)):
            bad = (t, str(g), w)
            break
    if bad:
        break
check("(b) triple construction: L(G') = L(G) ∩ L(M) for 200 random grammars and DFAs (1-3 states), |w| <= 6",
      bad is None, str(bad))

# (d) sanity instance: L = {0^n1^n} is not regular, and neither is its complement (same fooling set 0*)
L01 = lambda w: len(w) % 2 == 0 and w == "0" * (len(w) // 2) + "1" * (len(w) // 2)
check("(d) instance: 0* is a fooling set for the complement of {0^n1^n} too (z = 1^i), i != j <= 10",
      all((not L01("0" * i + "1" * i)) != (not L01("0" * j + "1" * i)) for i in range(11) for j in range(11) if i != j))

# (e) an ambiguous grammar with a finite language
GE = G("S -> A | B; A -> 0; B -> 0")
check("(e) S -> A | B, A -> 0, B -> 0: L = {0}", GE.language(6) == {"0"})
check("(e) ... and 0 has two parse trees (library count)", GE.count_parse_trees("0") == 2)


# (f) DFA -> grammar is unambiguous
def dfa_grammar(M):
    rules = {("q", q): [] for q in M.states}
    for q in M.states:
        for a in M.alphabet:
            rules[("q", q)].append((a, ("q", M.delta(q, a))))
        if q in M.accepting:
            rules[("q", q)].append(())
    return CFG(("q", M.start), rules, terminals=M.alphabet)


rng = random.Random(11)
okf, okc = True, True
for t in range(200):
    M = random_dfa(rng)
    g = dfa_grammar(M)
    for w in strings("01", 7):
        n = count_trees(g, w)
        if n != (1 if M.accepts(w) else 0):
            okf = False
        if t < 40 and len(w) <= 6 and len(leftmost_derivations(g, w)) != n:
            okc = False
check("(f) DFA grammar [q] -> a[δ(q,a)], [q] -> ε (q accepting): every string of L(M) has exactly one parse tree, "
      "none other has one; 200 random DFAs, |w| <= 7", okf)
check("(f) tree counter agrees with the number of leftmost derivations (40 DFAs, |w| <= 6)", okc)

# ================================================================== 5.2 grammar from the mod-3 DFA
print("\n# 5.2")
M3 = DFA("01", [0, 1, 2], 0, [0], lambda q, a: (2 * q + int(a)) % 3)
check("M accepts exactly the binary multiples of 3 (ε read as 0), |w| <= 14",
      first_difference(M3.accepts, lambda w: binval(w) % 3 == 0, "01", 14) is None)
R3 = G("R0 -> 0R0 | 1R1 | ε; R1 -> 0R2 | 1R0; R2 -> 0R1 | 1R2", nts=["R0", "R1", "R2"])
check("the grammar is exactly the DFA construction (rule sets equal)",
      rules_set(R3) == {(f"R{q}", tuple([a, f"R{M3.delta(q, a)}"])) for q in range(3) for a in "01"} | {("R0", ())})
for q in range(3):
    ok_same(f"L(R{q}) = {{x : {q}*2^|x| + val(x) ≡ 0 mod 3}}", R3,
            lambda x, q=q: (q * 2 ** len(x) + binval(x)) % 3 == 0, "01", 12, start=f"R{q}")
ok_same("L(R1) = {x : 1x is a multiple of 3}", R3, lambda x: binval("1" + x) % 3 == 0, "01", 12, "R1")
ok_same("L(R2) = {x : 10x is a multiple of 3}", R3, lambda x: binval("10" + x) % 3 == 0, "01", 12, "R2")
check("1001 = 9", binval("1001") == 9)
check("derivation R0 ~> 1R1 ~> 10R2 ~> 100R1 ~> 1001R0 ~> 1001 is a valid derivation",
      is_derivation(R3, ["R0", "1R1", "10R2", "100R1", "1001R0", "1001"]))
check("M's run on 1001 visits 0,1,2,1,0", M3.run("1001") == [0, 1, 2, 1, 0])
check("11 (=3) via R0 ~> 1R1 ~> 11R0 ~> 11", is_derivation(R3, ["R0", "1R1", "11R0", "11"]))
check("10 (=2) is not generated; R2 does not generate ε", not R3.generates("10") and not R3.generates("", "R2"))
check("ε is generated (0 is a multiple of 3)", R3.generates(""))
check("every string of L has exactly one parse tree, |w| <= 12",
      all(count_trees(R3, w) == (1 if binval(w) % 3 == 0 else 0) for w in strings("01", 12)))
R3x = G("R0 -> 0R0 | 1R1; R1 -> 0R2 | 1R0; R2 -> 0R1 | 1R2", nts=["R0", "R1", "R2"])
check("watch out: without R0 -> ε the grammar generates nothing (|w| <= 10)", R3x.language(10) == set())
R3y = G("R0 -> 0R0 | 1R1 | ε; R1 -> 0R2 | 1R0 | ε; R2 -> 0R1 | 1R2", nts=["R0", "R1", "R2"])
check("watch out: with R1 -> ε added, the grammar generates 1 (not a multiple of 3)", R3y.generates("1") and binval("1") % 3 != 0)

# ================================================================== 5.3 find the error
print("\n# 5.3")


def L53(w):
    n0, n1 = w.count("0"), w.count("1")
    return w == "0" * n0 + "1" * n1 and (n1 == n0 or n1 == 2 * n0)


STU = G("S -> 0S1 | 0S11 | ε")
ok_same("student's grammar generates {0^n 1^m : n <= m <= 2n}", STU,
        lambda w: w == "0" * w.count("0") + "1" * w.count("1") and w.count("0") <= w.count("1") <= 2 * w.count("0"),
        "01", 14)
check("student's grammar misses nothing: L ⊆ L(S) (|w| <= 14)", all(STU.generates(w) for w in strings("01", 14) if L53(w)))
extra = sorted((w for w in STU.language(9) if not L53(w)), key=lambda w: (len(w), w))
check("shortest wrong string is 00111, and it is the only wrong one of length 5", extra[0] == "00111"
      and [w for w in extra if len(w) == 5] == ["00111"], str(extra[:4]))
check("derivation S ~> 0S1 ~> 00S111 ~> 00111", is_derivation(STU, ["S", "0S1", "00S111", "00111"]))
check("infinitely many wrong strings: 0^n 1^(n+1) generated and not in L for n = 2..8",
      all(STU.generates("0" * n + "1" * (n + 1)) and not L53("0" * n + "1" * (n + 1)) for n in range(2, 9)))
FIX = G("S -> A | B; A -> 0A1 | ε; B -> 0B11 | ε")
ok_same("fixed grammar S -> A | B generates L", FIX, L53, "01", 14)
ok_same("L(A) = {0^n1^n}", FIX, lambda w: L01(w), "01", 12, "A")
ok_same("L(B) = {0^n1^2n}", FIX, lambda w: w == "0" * (len(w) // 3) + "1" * (2 * len(w) // 3) and len(w) % 3 == 0,
        "01", 12, "B")
check("fixed grammar: 00111 not generated; 011, 0011 generated", not FIX.generates("00111") and FIX.generates("011")
      and FIX.generates("0011"))
check("fixed grammar: ε has two parse trees (ambiguous), 0011 and 011 one each",
      count_trees(FIX, "") == 2 and count_trees(FIX, "0011") == 1 and count_trees(FIX, "011") == 1)
ok_same("the student's grammar is a correct grammar for {0^i1^j : i <= j <= 2i} (§5.4 Example 1)", STU,
        lambda w: w == "0" * w.count("0") + "1" * w.count("1") and w.count("0") <= w.count("1") <= 2 * w.count("0"),
        "01", 12)

# ================================================================== 5.4 recursive automaton -> grammar
print("\n# 5.4")
SIG4 = "1+()"
MODULES = {  # name: (start, accept, edges (q, label, p)); label '' = ε, a module name = call
    "E": ("sE", "tE", [("sE", "T", "x"), ("x", "+", "sE"), ("x", "", "tE")]),
    "T": ("sT", "tT", [("sT", "1", "tT"), ("sT", "(", "y"), ("y", "E", "z"), ("z", ")", "tT")]),
}
MAIN = "E"
ACCEPT_OF = {MODULES[A][1]: A for A in MODULES}


def ra_accepts(w, modules=MODULES, main=MAIN):
    """Configurations (i, q, stack); BFS with the stack depth bounded by 2|w| + 4."""
    edges = {}
    for A, (s, t, es) in modules.items():
        for (q, lab, p) in es:
            edges.setdefault(q, []).append((lab, p))
    start = (0, modules[main][0], ())
    goal = (len(w), modules[main][1], ())
    seen, queue = {start}, deque([start])
    bound = 2 * len(w) + 4
    while queue:
        i, q, st = queue.popleft()
        if (i, q, st) == goal:
            return True
        nxt = []
        for lab, p in edges.get(q, []):
            if lab == "":
                nxt.append((i, p, st))
            elif lab in modules:
                if len(st) < bound:
                    nxt.append((i, modules[lab][0], (p,) + st))
            elif i < len(w) and w[i] == lab:
                nxt.append((i + 1, p, st))
        if q in ACCEPT_OF and st:
            nxt.append((i, st[0], st[1:]))
        for c in nxt:
            if c not in seen:
                seen.add(c)
                queue.append(c)
    return False


def ra_to_cfg(modules, main):
    """Lemma 5.6: [q] -> a[p], [q] -> [p], [q] -> [s_A][p], [t_A] -> ε; start [s_main]."""
    rules = {}
    for A, (s, t, es) in modules.items():
        for q in {s, t} | {e[0] for e in es} | {e[2] for e in es}:
            rules.setdefault(f"[{q}]", [])
        for (q, lab, p) in es:
            if lab == "":
                rules[f"[{q}]"].append((f"[{p}]",))
            elif lab in modules:
                rules[f"[{q}]"].append((f"[{modules[lab][0]}]", f"[{p}]"))
            else:
                rules[f"[{q}]"].append((lab, f"[{p}]"))
        rules[f"[{t}]"].append(())
    return CFG(f"[{modules[main][0]}]", rules, terminals=SIG4)


RAG = ra_to_cfg(MODULES, MAIN)
PAGE_RAG = {  # the grammar as written in the solution
    "[sE]": [("[sT]", "[x]")],
    "[x]": [("+", "[sE]"), ("[tE]",)],
    "[tE]": [()],
    "[sT]": [("1", "[tT]"), ("(", "[y]")],
    "[y]": [("[sE]", "[z]")],
    "[z]": [(")", "[tT]")],
    "[tT]": [()],
}
check("Lemma 5.6 grammar of the automaton = the grammar on the page (7 nonterminals, 9 rules)",
      rules_set(RAG) == {(A, r) for A, rs in PAGE_RAG.items() for r in rs} and len(RAG.rules) == 7
      and len(rules_set(RAG)) == 9)


def parse_T(w, i):
    if i < len(w) and w[i] == "1":
        return i + 1
    if i < len(w) and w[i] == "(":
        j = parse_E(w, i + 1)
        if j is not None and j < len(w) and w[j] == ")":
            return j + 1
    return None


def parse_E(w, i):
    i = parse_T(w, i)
    while i is not None and i < len(w) and w[i] == "+":
        i = parse_T(w, i + 1)
    return i


expr = lambda w: parse_E(w, 0) == len(w)
term = lambda w: parse_T(w, 0) == len(w)
check("the automaton accepts exactly the expressions (sums of terms 1 or (expression)), |w| <= 8",
      first_difference(ra_accepts, expr, SIG4, 8) is None)
DESC = {"[sE]": expr, "[x]": lambda w: w == "" or (w[0] == "+" and expr(w[1:])), "[tE]": lambda w: w == "",
        "[sT]": term, "[y]": lambda w: w[-1:] == ")" and expr(w[:-1]), "[z]": lambda w: w == ")",
        "[tT]": lambda w: w == ""}
for A, pred in DESC.items():
    ok_same(f"L({A}) as described", RAG, pred, SIG4, 7, start=A)
SIMP = CFG("E", {"E": [("T",), ("T", "+", "E")], "T": [("1",), ("(", "E", ")")]}, terminals=SIG4)
ok_same("simplified grammar E -> T | T+E, T -> 1 | (E) generates the expressions", SIMP, expr, SIG4, 8)
check("(1+1)+1 accepted; 1+ and () rejected (automaton, both grammars, predicate)",
      all(f("(1+1)+1") for f in (ra_accepts, RAG.generates, SIMP.generates, expr))
      and not any(f(s) for s in ("1+", "()") for f in (ra_accepts, RAG.generates, SIMP.generates, expr)))
check("derivation of (1+1)+1 in the simplified grammar",
      is_derivation(SIMP, ["E", "T+E", "(E)+E", "(T+E)+E", "(1+E)+E", "(1+T)+E", "(1+1)+E", "(1+1)+T", "(1+1)+1"]))

# ================================================================== 5.5 two grammars with a separator
print("\n# 5.5")
SIG5 = "01#"


def split1(w):
    return w.split("#") if w.count("#") == 1 else None


def La(w):
    s = split1(w)
    return s is not None and s[0].count("1") == s[1].count("1")


def Lb(w):
    s = split1(w)
    return s is not None and s[1] in s[0][::-1]


GA = G("S -> 0S | S0 | 1S1 | #")
ok_same("(a) S -> 0S | S0 | 1S1 | # generates L_a", GA, La, SIG5, 10)
check("(a) examples: 1#01 and 01#1 in, 1#0 out; derivation S ~> 1S1 ~> 1S01 ~> 1#01",
      La("1#01") and La("01#1") and not La("1#0") and is_derivation(GA, ["S", "1S1", "1S01", "1#01"]))
GB = G("S -> ZT; T -> 0T0 | 1T1 | Z#; Z -> 0Z | 1Z | ε")
ok_same("(b) S -> ZT, T -> 0T0 | 1T1 | Z#, Z -> 0Z | 1Z | ε generates L_b", GB, Lb, SIG5, 10)
ok_same("(b) L(T) = {x#y : y^R is a prefix of x}", GB,
        lambda w: split1(w) is not None and split1(w)[0].startswith(split1(w)[1][::-1]), SIG5, 10, "T")
ok_same("(b) ... = {x#y : y is a suffix of x^R}", GB,
        lambda w: split1(w) is not None and split1(w)[0][::-1].endswith(split1(w)[1]), SIG5, 10, "T")
ok_same("(b) L(Z) = {0,1}*", GB, lambda w: "#" not in w, SIG5, 9, "Z")
check("(b) statement examples: 0110#1 and 01#10 in L_b, 01#01 not; # in, #0 not",
      Lb("0110#1") and Lb("01#10") and not Lb("01#01") and Lb("#") and not Lb("#0"))
check("(b) derivation S ~> T ~> 0T0 ~> 01T10 ~> 01Z#10 ~> 01#10 (Z = ε first)",
      is_derivation(GB, ["S", "ZT", "T", "0T0", "01T10", "01Z#10", "01#10"]))
GBw = G("S -> ZT; T -> 0T0 | 1T1 | #; Z -> 0Z | 1Z | ε")
ok_same("(b) watch out: without the middle Z, the grammar generates {x#y : y is a prefix of x^R}", GBw,
        lambda w: split1(w) is not None and split1(w)[0][::-1].startswith(split1(w)[1]), SIG5, 9)
check("(b) ... and misses 10#1 (1 is a substring, not a prefix, of 01)", Lb("10#1") and not GBw.generates("10#1"))

# ================================================================== 5.6 dangling else
print("\n# 5.6")


def bal(x):
    return x.count("0") - x.count("1")


def P(w):
    return all(bal(w[:k]) >= 0 for k in range(len(w) + 1))


def dyck(w):
    return P(w) and bal(w) == 0


GD = G("S -> 0S1S | 0S | ε")
ok_same("G: S -> 0S1S | 0S | ε generates P", GD, P, "01", 14)
check("001 has exactly two parse trees", count_trees(GD, "001") == 2)
check("strings of length <= 2 have at most one parse tree (0, 00, 01 exactly one)",
      all(count_trees(GD, w) <= 1 for w in strings("01", 2)) and all(count_trees(GD, w) == 1 for w in ("0", "00", "01")))
check("001 is the only string of length 3 with two parse trees",
      [w for w in strings("01", 3, 3) if count_trees(GD, w) > 1] == ["001"])
check("the two leftmost derivations of 001 are valid and different",
      is_derivation(GD, ["S", "0S1S", "00S1S", "001S", "001"]) and is_derivation(GD, ["S", "0S", "00S1S", "001S", "001"]))
check("tree counts of G agree with leftmost-derivation counts, |w| <= 8",
      all(count_trees(GD, w) == len(leftmost_derivations(GD, w)) for w in strings("01", 8)))
GU = G("S -> 0S | 0M1S | ε; M -> 0M1M | ε")
ok_same("unambiguous grammar S -> 0S | 0M1S | ε, M -> 0M1M | ε generates P", GU, P, "01", 14)
ok_same("L(M) = balanced strings (equal counts, every prefix >= 0)", GU, dyck, "01", 14, "M")
check("every string of P has exactly one parse tree in the new grammar, |w| <= 12",
      all(count_trees(GU, w) == (1 if P(w) else 0) for w in strings("01", 12)))
check("... and M is unambiguous too, |w| <= 12", all(count_trees(GU, w, "M") == (1 if dyck(w) else 0) for w in strings("01", 12)))
check("new grammar: tree counts = leftmost-derivation counts, |w| <= 8",
      all(count_trees(GU, w) == len(leftmost_derivations(GU, w)) for w in strings("01", 8)))
check("new grammar: the derivation S ~> 0S ~> 00M1S ~> 001S ~> 001", is_derivation(GU, ["S", "0S", "00M1S", "001S", "001"]))
check("test strings 0101 and 0010 are in P and generated by the new grammar",
      all(P(w) and GU.generates(w) for w in ("0101", "0010")))
GU2 = G("S -> M | M0S; M -> 0M1M | ε")
ok_same("alternative S -> M | M0S, M -> 0M1M | ε generates P", GU2, P, "01", 14)
check("... and is unambiguous, |w| <= 12", all(count_trees(GU2, w) == (1 if P(w) else 0) for w in strings("01", 12)))


# the unambiguity argument: for nonempty w in P the rule and the split are forced
def shortest_bal_prefix(w):
    return next((k for k in range(1, len(w) + 1) if bal(w[:k]) == 0), None)


okarg = True
for w in strings("01", 12):
    if w and P(w):
        k = shortest_bal_prefix(w)
        if k is not None:
            okarg &= w[0] == "0" and w[k - 1] == "1" and dyck(w[1:k - 1]) and P(w[k:])
        else:
            okarg &= w[0] == "0" and P(w[1:]) and all(bal(w[:j]) >= 1 for j in range(1, len(w) + 1))
check("argument: nonempty w in P with a balanced nonempty prefix = 0m1s at the shortest one (m balanced, s in P); "
      "otherwise every nonempty prefix has more 0s, |w| <= 12", okarg)

# ================================================================== 5.7 CNF conversion
print("\n# 5.7")
NT7 = ["S'", "T0", "T1", "S", "A", "B", "C"]
G7 = {
    "orig": G("S -> 0S1 | AB; A -> 0A | ε; B -> 1B | ε", nts=NT7),
    "0": G("S' -> S; S -> 0S1 | AB; A -> 0A | ε; B -> 1B | ε", nts=NT7),
    "1": G("S' -> S; S -> 0C | AB; C -> S1; A -> 0A | ε; B -> 1B | ε", nts=NT7),
    "3": G("S' -> S | ε; S -> 0C | AB | A | B; C -> S1 | 1; A -> 0A | 0; B -> 1B | 1", nts=NT7),
    "5": G("S' -> 0C | AB | 0A | 0 | 1B | 1 | ε; S -> 0C | AB | 0A | 0 | 1B | 1; C -> S1 | 1; A -> 0A | 0; B -> 1B | 1",
           nts=NT7),
    "6": G("S' -> T0C | AB | T0A | T1B | 0 | 1 | ε; S -> T0C | AB | T0A | T1B | 0 | 1; C -> ST1 | 1; "
           "A -> T0A | 0; B -> T1B | 1; T0 -> 0; T1 -> 1", nts=NT7),
}
in01 = lambda w: re.fullmatch("0*1*", w) is not None
for k, g in G7.items():
    ok_same(f"grammar after step {k} generates 0*1*", g, in01, "01", 12)
ok_same("original: L(A) = 0*", G7["orig"], lambda w: "1" not in w, "01", 10, "A")
ok_same("original: L(B) = 1*", G7["orig"], lambda w: "0" not in w, "01", 10, "B")
check("step 2: the nullable nonterminals are exactly S', S, A, B", G7["1"].nullable() == {"S'", "S", "A", "B"},
      str(G7["1"].nullable()))
ok_same("after step 3, S generates 0*1* without ε", G7["3"], lambda w: in01(w) and w != "", "01", 12, "S")
check("final grammar is in Chomsky normal form", G7["6"].is_cnf()[0], str(G7["6"].is_cnf()[1]))
check("final grammar: S' generates ε, 0, 1, 0011 but not 10",
      all(G7["6"].generates(w) for w in ("", "0", "1", "0011")) and not G7["6"].generates("10"))
check("the original start S is not allowed as CNF start (it is on a right side)",
      not CFG("S", G7["6"].rules).is_cnf()[0])


# independent implementation of the book's algorithm, compared with the page's final grammar
def to_cnf(g, new_start="S'", names=iter("CDEFGHIJ")):
    R = {A: [list(r) for r in rs] for A, rs in g.rules.items()}
    R = {new_start: [[g.start]], **R}
    # step 1: split long rules A -> X alpha into A -> X B, B -> alpha
    changed = True
    while changed:
        changed = False
        for A in list(R):
            for r in R[A]:
                if len(r) > 2:
                    B = next(names)
                    R[B] = [r[1:]]
                    del r[1:]
                    r.append(B)
                    changed = True
    # step 2: nullable
    nul = set()
    ch = True
    while ch:
        ch = False
        for A, rs in R.items():
            if A not in nul and any(all(x in nul for x in r) for r in rs):
                nul.add(A)
                ch = True
    # step 3: remove ε-rules, add variants with one nullable occurrence removed (rules have length <= 2)
    R3 = {}
    for A, rs in R.items():
        out = []
        for r in rs:
            if r and r not in out:
                out.append(r)
            for i, x in enumerate(r):
                if x in nul:
                    v = r[:i] + r[i + 1:]
                    if v and v not in out:
                        out.append(v)
        R3[A] = out
    if new_start in nul:
        R3[new_start].append([])
    # step 4: no unit cycles here (asserted)
    unit = {(A, r[0]) for A, rs in R3.items() for r in rs if len(r) == 1 and r[0] in R3}
    reach = {A: {B for (X, B) in unit if X == A} for A in R3}
    for _ in range(len(R3)):
        for A in R3:
            reach[A] |= set().union(*[reach[B] for B in reach[A]]) if reach[A] else set()
    assert all(A not in reach[A] for A in R3), "unit cycle"
    # step 5: copy rules in reverse topological order of the unit graph
    order = sorted(R3, key=lambda A: len(reach[A]))
    for A in order:
        new = []
        for r in R3[A]:
            if len(r) == 1 and r[0] in R3:
                for s in R3[r[0]]:
                    if s not in new:
                        new.append(s)
            elif r not in new:
                new.append(r)
        R3[A] = new
    # step 6: protect terminals in rules of length 2
    for A in list(R3):
        R3[A] = [[("T" + x if x in "01" else x) for x in r] if len(r) == 2 else r for r in R3[A]]
    R3["T0"], R3["T1"] = [["0"]], [["1"]]
    return CFG(new_start, {A: [tuple(r) for r in rs] for A, rs in R3.items()})


AUTO = to_cnf(G7["orig"])
check("an independent implementation of steps 0-6 produces exactly the page's final grammar (same rules)",
      rules_set(AUTO) == rules_set(G7["6"]), str(sorted(rules_set(AUTO) ^ rules_set(G7["6"]))))
FINAL_NE = CFG("S'", {A: [r for r in rs if r] for A, rs in G7["6"].rules.items()})
lens = leftmost_derivations(FINAL_NE, "0011")
check("every derivation of 0011 in the final grammar has 2*4 - 1 = 7 steps", lens and set(lens) == {7}, str(lens))
check("0011 has 3 parse trees in the final grammar (library count), as in the original grammar",
      FINAL_NE.count_parse_trees("0011") == 3, str(FINAL_NE.count_parse_trees("0011")))
check("0011 has 3 parse trees in the original grammar", count_trees(G7["orig"], "0011") == 3, str(count_trees(G7["orig"], "0011")))
check("derivation S' ~> T0C ~> 0C ~> 0ST1 ~> 0T0CT1 ~> 00CT1 ~> 001T1 ~> 0011 (7 steps, leftmost)",
      is_derivation(G7["6"], ["S'", "T0C", "0C", "0ST1", "0T0CT1", "00CT1", "001T1", "0011"]))
check("derivation S' ~> AB ~> T0AB ~> 0AB ~> 00B ~> 00T1B ~> 001B ~> 0011 (7 steps, leftmost)",
      is_derivation(G7["6"], ["S'", "AB", "T0AB", "0AB", "00B", "00T1B", "001B", "0011"]))
check("watch out: copying the ORIGINAL rules of A, B (with ε) into S would put S -> ε back",
      () in G7["orig"].rules["A"] and () in G7["orig"].rules["B"])

# ================================================================== 5.8 enough 1s at the end
print("\n# 5.8")


def L8(w):
    k = w.count("0")
    return w.endswith("1" * k)


check("statement examples: 0011, 101, 11 in L; 0101, 10 not", L8("0011") and L8("101") and L8("11")
      and not L8("0101") and not L8("10"))
G8 = G("S -> 0S1 | 1S | ε")
ok_same("S -> 0S1 | 1S | ε generates L", G8, L8, "01", 14)
R = range(0, 16)
check("fooling set 0*: for i < j, z = 1^i: 0^i 1^i in L and 0^j 1^i not in L (0 <= i < j <= 15)",
      all(L8("0" * i + "1" * i) and not L8("0" * j + "1" * i) for i in R for j in R if i < j))
check("the last j symbols of 0^j 1^i (i < j) contain a 0", all("0" in ("0" * j + "1" * i)[-j:] for i in R for j in R if i < j))
okw = True
for w in strings("01", 12):
    okw &= L8(w) == L8("1" + w)                       # a leading 1 changes nothing
    okw &= L8("0" + w + "1") == L8(w)                  # wrapping in 0...1
    if L8(w) and w.startswith("0"):
        okw &= w.endswith("1")
check("facts used: x in L <=> 1x in L; x in L <=> 0x1 in L; strings of L that start with 0 end with 1 (|x| <= 12)", okw)
check("derivations of 0011 and 101", is_derivation(G8, ["S", "0S1", "00S11", "0011"]) and is_derivation(G8, ["S", "1S", "10S1", "101"]))
check("0101 = 0x1 with x = 10 not in L, so 0101 is not generated", not L8("10") and not G8.generates("0101"))
G8w = G("S -> 0S1 | S1 | ε")
ok_same("watch out: S -> 0S1 | S1 | ε generates only {0^m 1^n : n >= m}", G8w,
        lambda w: w == "0" * w.count("0") + "1" * w.count("1") and w.count("1") >= w.count("0"), "01", 12)
check("... so it misses 1^k 01 for every k >= 1 (all in L)", all(L8("1" * k + "01") and not G8w.generates("1" * k + "01")
                                                                 for k in range(1, 9)))

# ================================================================== 5.9 a 1 in the first half
print("\n# 5.9")


def L9(w):
    return len(w) % 2 == 0 and "1" in w[:len(w) // 2]


check("statement examples: 10, 0100, 1000 in L; 01, 0010, 101 not",
      L9("10") and L9("0100") and L9("1000") and not L9("01") and not L9("0010") and not L9("101"))
G9 = G("S -> XSX | 1O; O -> X | XXO; X -> 0 | 1")
ok_same("S -> XSX | 1O, O -> X | XXO, X -> 0 | 1 generates L", G9, L9, "01", 14)
ok_same("L(O) = odd-length strings", G9, lambda w: len(w) % 2 == 1, "01", 12, "O")
ok_same("L(X) = {0, 1}", G9, lambda w: len(w) == 1, "01", 6, "X")


def u1v(w):
    return any(w[k] == "1" and (len(w) - 1 - 2 * k) % 2 == 1 and len(w) - 1 - 2 * k >= 1 for k in range(len(w)))


check("L = {u1v : |v| - |u| odd and >= 1} (|w| <= 14)", first_difference(L9, u1v, "01", 14) is None)
R = range(0, 16)
check("fooling set 0*: for i < j, z = 1 0^(i+1): xz in L, yz not in L (0 <= i < j <= 15)",
      all(L9("0" * i + "1" + "0" * (i + 1)) and not L9("0" * j + "1" + "0" * (i + 1)) for i in R for j in R if i < j))
check("for i < j with i + j even: j >= i + 2 and the first half of yz has length (i+j)/2 + 1 <= j",
      all(j >= i + 2 and (i + j) // 2 + 1 <= j for i in R for j in R if i < j and (i + j) % 2 == 0))
check("derivation S ~> 0S0 ~> 01O0 ~> 01X0 ~> 0100", is_derivation(G9, ["S", "XSX", "0SX", "01OX", "01XX", "010X", "0100"]))
G9a = G("S -> XSX | 1X; X -> 0 | 1")
check("watch out: S -> XSX | 1X generates only strings of L ...", all(L9(w) for w in G9a.language(10)))
ok_same("... namely the even-length strings whose first half ENDS with 1", G9a,
        lambda w: len(w) % 2 == 0 and len(w) > 0 and w[len(w) // 2 - 1] == "1", "01", 12)
check("... so it misses 1000, 1010 and 1 0^(2k-1) for every k >= 2", L9("1000") and L9("1010")
      and not G9a.generates("1000") and not G9a.generates("1010")
      and all(L9("1" + "0" * (2 * k - 1)) and not G9a.generates("1" + "0" * (2 * k - 1)) for k in range(2, 7)))
G9b = G("S -> XSX | 1Z; Z -> XZ | ε; X -> 0 | 1")
check("watch out: S -> XSX | 1Z, Z -> XZ | ε generates 1 and 100 (odd length)", G9b.generates("1") and G9b.generates("100"))
check("1000 = 1O with O ~>* 000; 0010 has its only 1 at position 3 of 4 and is not generated",
      G9.generates("000", "O") and is_derivation(G9, ["S", "1O", "1XXO", "10XO", "100O", "100X", "1000"])
      and "0010".index("1") == 2 and not G9.generates("0010"))

# ================================================================== 5.10 the proof
print("\n# 5.10")
ok_same("L(G) = P for G: S -> 0S1S | 0S | ε", GD, P, "01", 14)
check("check line: ε, 0, 01, 001, 0011, 010 in P; 1, 10, 011 not",
      all(P(w) for w in ["", "0", "01", "001", "0011", "010"]) and not any(P(w) for w in ["1", "10", "011"]))
ok_case = True
for w in strings("01", 12):
    if not P(w) or not w:
        continue
    ok_case &= w[0] == "0"
    k = shortest_bal_prefix(w)
    if k is not None:
        x, y = w[1:k - 1], w[k:]
        ok_case &= k >= 2 and bal(w[:k - 1]) == 1 and w[k - 1] == "1" and P(x) and P(y)
        ok_case &= all(bal("0" + x[:m]) >= 1 for m in range(len(x) + 1))
    else:
        ok_case &= P(w[1:]) and all(bal(w[:m]) >= 1 for m in range(1, len(w) + 1))
check("proof of P ⊆ L(G): first symbol 0; case A (shortest balanced prefix p = 0x1, x and y in P); "
      "case B (w = 0x, x in P); all w in P, |w| <= 12", ok_case)
ok_inc = True
for x in strings("01", 7):
    for y in strings("01", 7 - len(x)):
        if P(x) and P(y):
            ok_inc &= P("0" + x + "1" + y)
    if P(x):
        ok_inc &= P("0" + x)
check("proof of L(G) ⊆ P: x, y in P => 0x1y in P and 0x in P (|x| + |y| <= 7)", ok_inc)
check("watch out: with the LONGEST balanced prefix, 0101 = 0·10·1 and 10 is not in P",
      P("0101") and bal("0101") == 0 and not P("10"))
check("011 is not generated (not in P)", not GD.generates("011"))
check("010 = 0·ε·1·0: shortest balanced prefix 01, x = ε, y = 0; derivation S ~> 0S1S ~> 01S ~> 010S ~> 010",
      shortest_bal_prefix("010") == 2 and is_derivation(GD, ["S", "0S1S", "01S", "010S", "010"]))

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: {FAIL}")
sys.exit(1 if FAIL else 0)
