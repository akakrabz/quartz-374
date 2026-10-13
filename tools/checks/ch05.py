#!/usr/bin/env python3
"""Checks for every concrete claim on content/1-models-of-computation/05-context-free-languages.md.

Grammars are compared with brute-force predicates on ALL strings up to a length bound, with CFG.generates
(Earley's algorithm). For the 6-symbol alphabets (expressions, regular expressions) the Earley comparison runs over
all strings up to length 6-7, and the exact languages up to length 9-11 are compared by a least-fixed-point
enumeration of the grammar against an enumeration driven by the predicate. Parse trees are enumerated by a small
chart parser that also handles epsilon-rules (and refuses grammars in which a string has infinitely many trees).
The figures' parse trees and recursive automaton are imported from tools/figs_ch05.py and checked as drawn."""
import os
import re
import sys
import time
from itertools import combinations, product

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
from automata import CFG, strings, first_difference  # noqa: E402
from automata.regex import _Parser  # noqa: E402
import figs_ch05 as FIG  # noqa: E402

FAIL = []


_T = [time.time()]


def check(name, cond, detail=""):
    if os.environ.get("CH05_TIMING"):
        detail = f"{detail} {time.time() - _T[0]:.1f}s".strip()
        _T[0] = time.time()
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAIL.append(name)


B = "01"
N = 12          # length bound for Earley checks of binary grammars
NX = 14         # length bound for the exact fixed-point comparison
BND = f"Earley |w| <= {N}, exact |w| <= {NX}"


def G(text, **kw):
    return CFG.parse(text, **kw)


def agrees(g, pred, alphabet=B, n=N, start=None):
    """Shortest string (|w| <= n) on which the grammar (from `start`) and the predicate disagree, or None.
    Earley's algorithm on every string up to length n; for binary grammars also the exact language (least fixed
    point) up to length NX against the predicate on all strings up to NX."""
    d = first_difference(lambda w: g.generates(w, start), pred, alphabet, n)
    if d is None and alphabet == B and n == N:
        exact = fixlang_cached(g, NX)[start or g.start]
        bad = [w for w in strings(B, NX) if (w in exact) != bool(pred(w))]
        d = min(bad, key=lambda w: (len(w), w)) if bad else None
    return d


def c0(w):
    return w.count("0")


def c1(w):
    return w.count("1")


def zo(w):
    """w in 0*1* ?"""
    return re.fullmatch("0*1*", w) is not None


# ---------------------------------------------------------------- helpers: exact languages up to length n
def fixlang(g, n):
    """Least fixed point, layered by length: {A: set of terminal strings of length <= n derived from A}."""
    nts = list(g.rules)
    byl = {A: [set() for _ in range(n + 1)] for A in nts}

    def seq(r, k):
        if not r:
            return {""} if k == 0 else set()
        X, rest = r[0], r[1:]
        out = set()
        if X in g.rules:
            for k1 in range(k + 1):
                left = byl[X][k1]
                if left:
                    right = seq(rest, k - k1)
                    if right:
                        out |= {u + v for u in left for v in right}
        elif k >= 1:
            out = {X + v for v in seq(rest, k - 1)}
        return out

    for k in range(n + 1):
        changed = True
        while changed:
            changed = False
            for A in nts:
                for r in g.rules[A]:
                    new = seq(r, k) - byl[A][k]
                    if new:
                        byl[A][k] |= new
                        changed = True
    return {A: set().union(*byl[A]) for A in nts}


_FIX = {}


def fixlang_cached(g, n):
    if (id(g), n) not in _FIX:
        _FIX[(id(g), n)] = (g, fixlang(g, n))
    return _FIX[(id(g), n)][1]


# ---------------------------------------------------------------- helpers: parse trees and derivations
class InfinitelyMany(Exception):
    pass


EPS_LEAF = ("ε", ())


def min_yield(g):
    """Length of the shortest terminal string each nonterminal derives (inf if none)."""
    m = {A: float("inf") for A in g.rules}
    changed = True
    while changed:
        changed = False
        for A, rhs in g.rules.items():
            for r in rhs:
                v = sum(m[X] if X in g.rules else 1 for X in r)
                if v < m[A]:
                    m[A] = v
                    changed = True
    return m


def parse_trees(g, w, start=None, cap=20000):
    """All parse trees of w from `start`. Tree = (label, children); terminal leaves (a, ()), ε-leaf ("ε", ()).
    Raises InfinitelyMany if some substring has a cyclic derivation through nullable symbols."""
    start = start or g.start
    memo, busy = {}, set()
    my = min_yield(g)

    def minlen(r):
        return sum(my[X] if X in g.rules else 1 for X in r)

    def T(X, i, j):
        key = (X, i, j)
        if key in memo:
            return memo[key]
        if key in busy:
            raise InfinitelyMany(key)
        busy.add(key)
        out = []
        for r in g.rules[X]:
            if not r:
                if i == j:
                    out.append((X, (EPS_LEAF,)))
                continue
            for kids in S(r, i, j):
                out.append((X, kids))
        if len(out) > cap:
            raise RuntimeError("too many trees")
        busy.discard(key)
        memo[key] = out
        return out

    def S(r, i, j):
        if not r:
            return [()] if i == j else []
        X, rest = r[0], r[1:]
        res = []
        if X not in g.rules:
            if i < j and w[i] == X:
                res = [((X, ()),) + t for t in S(rest, i + 1, j)]
            return res
        rest_min = minlen(rest)
        for k in range(i + my[X], j + 1) if my[X] != float("inf") else ():
            if j - k < rest_min:
                break
            heads = T(X, i, k)
            if heads:
                tails = S(rest, k, j)
                res += [(h,) + t for h in heads for t in tails]
        return res

    return T(start, 0, len(w))


def conv(n):
    """figlib tree ('$A' marks nonterminals) -> parse-tree tuples."""
    lab, kids = n
    if lab.startswith("$"):
        return (lab[1:], tuple(conv(k) for k in kids))
    return (lab, ())


def tree_yield(t):
    lab, kids = t
    if not kids:
        return "" if lab == "ε" else lab
    return "".join(tree_yield(k) for k in kids)


def valid_tree(g, t, root):
    """Root label, and every internal node's children spell one of its rules (ε-leaf for an ε-rule)."""
    if t[0] != root:
        return False

    def ok(n):
        lab, kids = n
        if not kids:
            return True
        if lab not in g.rules:
            return False
        rhs = tuple(k[0] for k in kids)
        if rhs == ("ε",) and kids[0][1] == ():
            rhs = ()
        if rhs not in g.rules[lab]:
            return False
        for k in kids:
            if k[1] and k[0] not in g.rules:
                return False
            if not k[1] and k[0] in g.rules:
                return False   # a nonterminal leaf: unfinished tree
        return all(ok(k) for k in kids)

    return ok(t)


def nt_nodes(t):
    return (1 if t[1] else 0) + sum(nt_nodes(k) for k in t[1])


def leftmost(t):
    """The leftmost derivation that a parse tree determines, as a list of sentential forms (single-char symbols)."""
    form = [t]
    out = ["".join(n[0] for n in form)]
    while any(n[1] for n in form):
        k = next(i for i, n in enumerate(form) if n[1])
        kids = [c for c in form[k][1] if c != EPS_LEAF]
        form = form[:k] + kids + form[k + 1:]
        out.append("".join(n[0] for n in form))
    return out


def is_step(g, x, y, leftmost_only=False):
    """x ⇝ y by one rule application (single-character symbols)."""
    for i, X in enumerate(x):
        if X in g.rules:
            if any(x[:i] + "".join(r) + x[i + 1:] == y for r in g.rules[X]):
                return True
            if leftmost_only:
                return False
    return False


def is_derivation(g, forms, leftmost_only=False):
    return all(is_step(g, a, b, leftmost_only) for a, b in zip(forms, forms[1:]))


def D(s):
    """'S ⇝ A ⇝ 0C' -> ['S', 'A', '0C'] (ε for the empty string)."""
    return [f.strip().replace("ε", "") for f in s.split("⇝")]


# ======================================================================== 5.1 definitions, running example
G0 = G("S -> A | B; A -> 0A | 0C; B -> B1 | C1; C -> ε | 0C1")
langs0 = {"C": lambda w: zo(w) and c0(w) == c1(w), "A": lambda w: zo(w) and c0(w) > c1(w),
          "B": lambda w: zo(w) and c0(w) < c1(w), "S": lambda w: zo(w) and c0(w) != c1(w)}
for X, p in langs0.items():
    d = agrees(G0, p, start=X)
    check(f"running example: L({X}) as stated ({BND})", d is None, f"first difference {d!r}")
der = D("S ⇝ A ⇝ 0C ⇝ 00C1 ⇝ 000C11 ⇝ 00011")
check("derivation S ⇝ A ⇝ 0C ⇝ 00C1 ⇝ 000C11 ⇝ 00011: every step applies one rule", is_derivation(G0, der))
check("00011 = 0^3 1^2 has m = 3 > n = 2, so it is in L(A) ⊆ L(S)", G0.generates("00011", "A") and langs0["A"]("00011"))
LC = {w for w in strings(B, 12) if G0.generates(w, "C")}
check("rules as equations: L(C) = {ε} ∪ 0 L(C) 1 (|w| <= 12)", LC == {""} | {"0" + x + "1" for x in LC if len(x) <= 10})
LA = {w for w in strings(B, 12) if G0.generates(w, "A")}
check("A -> 0A | 0C: a string of A is one or more 0s followed by a string of C (|w| <= 12)",
      LA == {"0" * k + x for x in LC for k in range(1, 13) if len(x) + k <= 12})
LB = {w for w in strings(B, 12) if G0.generates(w, "B")}
check("B -> B1 | C1: a string of B is a string of C followed by one or more 1s (|w| <= 12)",
      LB == {x + "1" * k for x in LC for k in range(1, 13) if len(x) + k <= 12})

# ======================================================================== 5.2 parse trees and ambiguity
tC, tS = conv(FIG.TREE_C_0011), conv(FIG.TREE_S_00011)
check("figure: left tree is a parse tree from C with yield 0011", valid_tree(G0, tC, "C") and tree_yield(tC) == "0011")
check("figure: right tree is a parse tree from S with yield 00011", valid_tree(G0, tS, "S") and tree_yield(tS) == "00011")
check("figure: the highlighted subtree of the right tree is the left tree", conv(FIG.SUB_C_0011) == tC
      and tS[1][0][1][1] == tC)
check("the right tree's leftmost derivation is the derivation of §5.1", leftmost(tS) == der, str(leftmost(tS)))
check("0011 and 00011 have exactly one parse tree each (from C and from S)",
      len(parse_trees(G0, "0011", "C")) == 1 and len(parse_trees(G0, "00011")) == 1)

PLUS = G("S -> 1 | S+S")
cat_nums = [1, 1, 2, 5, 14, 42, 132, 429]
counts = [PLUS.count_parse_trees("+".join("1" * k)) for k in range(1, 9)]
check("S -> 1 | S+S: k = 1..8 ones have 1, 1, 2, 5, 14, 42, 132, 429 parse trees (Catalan numbers)",
      counts == cat_nums, str(counts))
check("own tree enumerator agrees on those counts",
      [len(parse_trees(PLUS, "+".join("1" * k))) for k in range(1, 9)] == cat_nums)
t_l, t_r = conv(FIG.TREE_111_LEFT), conv(FIG.TREE_111_RIGHT)
check("figure: both trees of 1+1+1 are valid, different, and are all its parse trees",
      valid_tree(PLUS, t_l, "S") and valid_tree(PLUS, t_r, "S") and t_l != t_r
      and set(parse_trees(PLUS, "1+1+1")) == {t_l, t_r} and tree_yield(t_l) == tree_yield(t_r) == "1+1+1")
check("figure: highlighted subtrees are 1+1 = the first two 1s (left) and the last two (right)",
      t_l[1][0] == conv(FIG.INNER_L) and t_r[1][2] == conv(FIG.INNER_R) and tree_yield(conv(FIG.INNER_L)) == "1+1")
lm1 = D("S ⇝ S+S ⇝ S+S+S ⇝ 1+S+S ⇝ 1+1+S ⇝ 1+1+1")
lm2 = D("S ⇝ S+S ⇝ 1+S ⇝ 1+S+S ⇝ 1+1+S ⇝ 1+1+1")
check("the two leftmost derivations of 1+1+1 are leftmost derivations, of the left and right tree",
      is_derivation(PLUS, lm1, True) and is_derivation(PLUS, lm2, True) and leftmost(t_l) == lm1
      and leftmost(t_r) == lm2)
d_left, d_right = D("S ⇝ S+S ⇝ 1+S ⇝ 1+1"), D("S ⇝ S+S ⇝ S+1 ⇝ 1+1")
check("1+1: S ⇝ S+S ⇝ 1+S ⇝ 1+1 and S ⇝ S+S ⇝ S+1 ⇝ 1+1 are derivations; 1+1 has one parse tree",
      is_derivation(PLUS, d_left) and is_derivation(PLUS, d_right) and not is_derivation(PLUS, d_right, True)
      and len(parse_trees(PLUS, "1+1")) == 1)
p_plus = lambda w: re.fullmatch(r"(1\+)*1", w) is not None
check("L(S -> 1 | S+S) = {(1+)^k 1 : k >= 0} (all strings over {1,+}, |w| <= 15)", agrees(PLUS, p_plus, "1+", 15) is None)
PLUS_R = G("S -> 1 | 1+S")
check("S -> 1 | 1+S generates the same language (|w| <= 15)", agrees(PLUS_R, p_plus, "1+", 15) is None)
_t = parse_trees(PLUS_R, "1+1+1+1")
check("S -> 1 | 1+S groups from the right: 1+1+1+1 has the single tree 1+(1+(1+1))",
      len(_t) == 1 and [tree_yield(k) for k in _t[0][1]] == ["1", "+", "1+1+1"]
      and [tree_yield(k) for k in _t[0][1][2][1]] == ["1", "+", "1+1"])
check("S -> 1 | 1+S is unambiguous: every string up to length 15 has exactly one parse tree",
      all(PLUS_R.count_parse_trees(w) == 1 for w in strings("1+", 15) if p_plus(w)))

IA = G("S -> XC | AY; X -> aXb | ε; C -> cC | ε; A -> aA | ε; Y -> bYc | ε")
abc = lambda w: re.fullmatch("(a*)(b*)(c*)", w)
p_ia = lambda w: bool(abc(w)) and (len(abc(w)[1]) == len(abc(w)[2]) or len(abc(w)[2]) == len(abc(w)[3]))
check("{a^i b^j c^k : i = j or j = k}: S -> XC | AY, X -> aXb | ε, C -> cC | ε, A -> aA | ε, Y -> bYc | ε "
      "(Earley, all strings over a,b,c with |w| <= 10)", agrees(IA, p_ia, "abc", 10) is None)
check("... X, C, A, Y generate a^i b^i, c*, a*, b^j c^j (|w| <= 8)",
      agrees(IA, lambda w: bool(abc(w)) and not abc(w)[3] and len(abc(w)[1]) == len(abc(w)[2]), "abc", 8, "X") is None
      and agrees(IA, lambda w: set(w) <= {"c"}, "abc", 8, "C") is None
      and agrees(IA, lambda w: set(w) <= {"a"}, "abc", 8, "A") is None
      and agrees(IA, lambda w: bool(abc(w)) and not abc(w)[1] and len(abc(w)[2]) == len(abc(w)[3]), "abc", 8, "Y") is None)
check("... and a^n b^n c^n has exactly two parse trees (n = 0..4), while aabbc and abbcc have one",
      all(len(parse_trees(IA, "a" * n + "b" * n + "c" * n)) == 2 for n in range(5))
      and len(parse_trees(IA, "aabbc")) == 1 and len(parse_trees(IA, "abbcc")) == 1)

# ======================================================================== 5.3 from grammar to language
ok = True
for n in range(0, 11):
    forms = ["0" * k + "C" + "1" * k for k in range(n + 1)] + ["0" * n + "1" * n]
    ok = ok and is_derivation(G0, forms) and forms[-1] == "0" * n + "1" * n
check("Lemma 5.1: C ⇝ 0C1 ⇝ ... ⇝ 0^nC1^n ⇝ 0^n1^n is a derivation, n = 0..10", ok)
check(f"Lemma 5.2: every string in L(C) is 0^n1^n ({BND})", agrees(G0, langs0["C"], start="C") is None)
check("proof of Lemma 5.2: if C ⇝* w via C -> 0C1, then w = 0x1 with x in L(C) (|w| <= 14)",
      all(w[0] == "0" and w[-1] == "1" and G0.generates(w[1:-1], "C")
          for w in strings(B, NX) if len(w) >= 2 and G0.generates(w, "C")))

EQ1 = G("S -> ε | SS | 0S1 | 1S0")
p_eq = lambda w: c0(w) == c1(w)
check(f"Lemma 5.3 grammar S -> ε | SS | 0S1 | 1S0 generates exactly #0 = #1 ({BND})", agrees(EQ1, p_eq) is None)
ok = True
for k in range(0, 7):
    forms = ["S"] + ["SS", "S"] * k + ["0S1", "01"]
    ok = ok and is_derivation(EQ1, forms) and len(forms) - 1 == 2 * k + 2
check("arbitrarily long derivations: S (⇝ SS ⇝ S)^k ⇝ 0S1 ⇝ 01 is a derivation of 01 with 2k+2 steps, k <= 6", ok)
try:
    parse_trees(EQ1, "")
    inf = False
except InfinitelyMany:
    inf = True
fam, t = set(), ("S", (EPS_LEAF,))
for k in range(8):
    fam.add(t) if valid_tree(EQ1, t, "S") and tree_yield(t) == "" else None
    t = ("S", (t, ("S", (EPS_LEAF,))))
check("so even ε has infinitely many parse trees: S -> ε, S -> SS -> εε, ... (8 distinct trees built; "
      "the enumerator also detects the cycle S ⇝ SS ⇝ S)", inf and len(fam) == 8)


def min_deriv_eq1(w):
    """Minimum number of steps of a derivation S ⇝* w[i:j] in S -> ε | SS | 0S1 | 1S0 (Bellman-Ford style)."""
    n = len(w)
    INF = float("inf")
    c = {(i, j): INF for i in range(n + 1) for j in range(i, n + 1)}
    changed = True
    while changed:
        changed = False
        for (i, j) in c:
            best = 1 if i == j else INF
            if j - i >= 2 and w[i] != w[j - 1]:
                best = min(best, 1 + c[(i + 1, j - 1)])
            for k in range(i, j + 1):
                best = min(best, 1 + c[(i, k)] + c[(k, j)])
            if best < c[(i, j)]:
                c[(i, j)] = best
                changed = True
    return c


ok = True
for w in strings(B, 10):
    if w and p_eq(w):
        c = min_deriv_eq1(w)
        n = len(w)
        via_ss = [k for k in range(0, n + 1) if 1 + c[(0, k)] + c[(k, n)] == c[(0, n)]]
        ok = ok and all(0 < k < n for k in via_ss)
check("shortest derivations: when a shortest derivation of w ≠ ε starts with S -> SS, both parts are non-empty "
      "(all balanced w, |w| <= 10)", ok)

MUT = G("S -> 0A1 | ε; A -> 1S0 | ε")
check(f"Lemma 5.4: L(S) = (01)* ({BND})", agrees(MUT, lambda w: re.fullmatch("(01)*", w) is not None) is None)
check(f"Lemma 5.4: L(A) = (10)* ({BND})",
      agrees(MUT, lambda w: re.fullmatch("(10)*", w) is not None, start="A") is None)
check("(01)^n = 0(10)^(n-1)1 and (10)^n = 1(01)^(n-1)0 for n = 1..12",
      all("01" * n == "0" + "10" * (n - 1) + "1" and "10" * n == "1" + "01" * (n - 1) + "0" for n in range(1, 13)))

# ======================================================================== 5.4 more examples (the book's grammars)
PAL = G("S -> 0S0 | 1S1 | 0 | 1 | ε")
check(f"palindromes: S -> 0S0 | 1S1 | 0 | 1 | ε ({BND})", agrees(PAL, lambda w: w == w[::-1]) is None)
NPAL = G("S -> 0S0 | 1S1 | 0Z1 | 1Z0; Z -> ε | 0Z | 1Z")
check(f"non-palindromes: S -> 0S0 | 1S1 | 0Z1 | 1Z0 ({BND})", agrees(NPAL, lambda w: w != w[::-1]) is None)
check(f"non-palindromes: L(Z) = {{0,1}}* ({BND})", agrees(NPAL, lambda w: True, start="Z") is None)
ok = True
for w in strings(B, 12):
    if w != w[::-1]:
        i = next(k for k in range(len(w)) if w[k] != w[-1 - k])
        x, a, b = w[:i], w[i], w[-1 - i]
        z = w[i + 1:len(w) - 1 - i]
        ok = ok and a != b and w == x + a + z + b + x[::-1]
check("every non-palindrome is x a z b x^R with a ≠ b (outermost mismatch), |w| <= 12", ok)
EQ2 = G("S -> 0S1 | 1S0 | SS | ε")
EQ3 = G("S -> 0S1S | 1S0S | ε")
check(f"#0 = #1: S -> 0S1 | 1S0 | SS | ε ({BND})", agrees(EQ2, p_eq) is None)
check(f"#0 = #1: S -> 0S1S | 1S0S | ε ({BND})", agrees(EQ3, p_eq) is None)
ok = True
for w in strings(B, 14):
    if w and p_eq(w):
        k = next(k for k in range(1, len(w) + 1) if p_eq(w[:k]))
        p = w[:k]
        ok = ok and p[0] != p[-1] and p_eq(p[1:-1]) and p_eq(w[k:])
check("shortest non-empty balanced prefix: starts and ends with different symbols, middle and rest balanced "
      "(|w| <= 14)", ok)
check("the figure's string 00111001 = 0·01·1·1001 splits at its first return to 0",
      p_eq("00111001") and next(k for k in range(1, 9) if p_eq("00111001"[:k])) == 4
      and "0" + "01" + "1" + "1001" == "00111001" and p_eq("01") and p_eq("1001"))
check("S -> 0S1S | 1S0S | ε is ambiguous: 0101 has two parse trees (0·ε·1·01 and 0·10·1·ε)",
      len(parse_trees(EQ3, "0101")) == 2)
GE = G("S -> 0S1 | 1S0 | SS | 0 | ε")
check(f"#0 >= #1: S -> 0S1 | 1S0 | SS | 0 | ε ({BND})", agrees(GE, lambda w: c0(w) >= c1(w)) is None)
NE = G("S -> O | I; O -> E0O | E0E; I -> E1I | E1E; E -> 0E1E | 1E0E | ε")
for X, p, txt in (("S", lambda w: c0(w) != c1(w), "#0 ≠ #1"), ("O", lambda w: c0(w) > c1(w), "#0 > #1"),
                  ("I", lambda w: c0(w) < c1(w), "#0 < #1"), ("E", p_eq, "#0 = #1")):
    check(f"#0 ≠ #1 grammar: L({X}) = {{w : {txt}}} ({BND})", agrees(NE, p, start=X) is None)
ok = True
for w in strings(B, 12):
    if c0(w) > c1(w):
        diff = [c0(w[:k]) - c1(w[:k]) for k in range(len(w) + 1)]
        k = diff.index(1)              # first prefix with one more 0 than 1s
        x, y = w[:k - 1], w[k:]
        ok = ok and w[k - 1] == "0" and p_eq(x) and c0(y) >= c1(y)
check("more 0s than 1s: w = x0y at the first prefix with one extra 0; x balanced, #0(y) >= #1(y) (|w| <= 12)", ok)


def balanced(w):
    d = 0
    for ch in w:
        d += 1 if ch == "(" else -1
        if d < 0:
            return False
    return d == 0


PAR1 = G("S -> (S) | SS | ε")
PAR2 = G("S -> (S)S | ε")
check("balanced parentheses: S -> (S) | SS | ε (|w| <= 16)", agrees(PAR1, balanced, "()", 16) is None)
check("balanced parentheses: S -> (S)S | ε (|w| <= 16)", agrees(PAR2, balanced, "()", 16) is None)
check("S -> (S)S | ε is unambiguous: exactly one parse tree for every balanced string, |w| <= 14",
      all(len(parse_trees(PAR2, w)) == 1 for w in strings("()", 14) if balanced(w)))
pair = ("S", (("(", ()), ("S", (EPS_LEAF,)), (")", ())))         # S -> (S) -> ()
tA = ("S", (("S", (pair, pair)), pair))                          # (()())() grouped as (()())()
tB = ("S", (pair, ("S", (pair, pair))))                          # ()(()())
check("S -> (S) | SS | ε is ambiguous: ()()() has the two parse trees SS·S and S·SS",
      valid_tree(PAR1, tA, "S") and valid_tree(PAR1, tB, "S") and tA != tB
      and tree_yield(tA) == tree_yield(tB) == "()()()")
ok = True
eps_trees = set()
t = ("S", (EPS_LEAF,))
for k in range(8):
    ok = ok and valid_tree(PAR1, t, "S") and tree_yield(t) == ""
    eps_trees.add(t)
    t = ("S", (t, ("S", (EPS_LEAF,))))
check("... and ε alone has infinitely many: S -> ε, S -> SS -> εε, ... (8 different trees checked)",
      ok and len(eps_trees) == 8)

EXPR = G("E -> E+T | T; T -> T×F | F; F -> (E) | X | Y")
SIG_E = "XY+×()"


def expr_ok(w):
    """Well-formed arithmetic expressions over X, Y, +, ×, parentheses (left-to-right checker)."""
    want_operand, depth = True, 0
    for ch in w:
        if want_operand:
            if ch in "XY":
                want_operand = False
            elif ch == "(":
                depth += 1
            else:
                return False
        else:
            if ch in "+×":
                want_operand = True
            elif ch == ")" and depth > 0:
                depth -= 1
            else:
                return False
    return not want_operand and depth == 0


def expr_strings(n):
    """Exactly the strings of length <= n accepted by expr_ok (the same checker, run as a generator)."""
    out = set()

    def rec(w, want, d):
        if not want and d == 0:
            out.add(w)
        if len(w) == n:
            return
        for ch in SIG_E:
            if want:
                if ch in "XY":
                    rec(w + ch, False, d)
                elif ch == "(":
                    rec(w + ch, True, d + 1)
            else:
                if ch in "+×":
                    rec(w + ch, True, d)
                elif ch == ")" and d > 0:
                    rec(w + ch, False, d - 1)

    rec("", True, 0)
    return out


check("expressions: E grammar = well-formed expressions, Earley on all strings over X,Y,+,×,(,) with |w| <= 6",
      agrees(EXPR, expr_ok, SIG_E, 6) is None)
check("the generator enumerates exactly the well-formed expressions (vs brute force, |w| <= 6)",
      expr_strings(6) == {w for w in strings(SIG_E, 6) if expr_ok(w)})
LE = fixlang(EXPR, 11)
check("expressions: exact language of E equals the well-formed expressions up to length 11",
      LE["E"] == expr_strings(11), f"{len(LE['E'])} strings")
check("expression grammar is unambiguous: one parse tree for every expression of length <= 9",
      all(EXPR.count_parse_trees(w) == 1 for w in LE["E"] if len(w) <= 9))


def root_split(g, w, start=None):
    (t,) = parse_trees(g, w, start)
    return t[0], tuple(tree_yield(k) for k in t[1])


check("X+Y×X parses as X+(Y×X): root E -> E+T with E ⇝* X and T ⇝* Y×X", root_split(EXPR, "X+Y×X") == ("E", ("X", "+", "Y×X")))
check("X×Y+X parses as (X×Y)+X", root_split(EXPR, "X×Y+X") == ("E", ("X×Y", "+", "X")))
check("X+Y+X parses as (X+Y)+X (left to right)", root_split(EXPR, "X+Y+X") == ("E", ("X+Y", "+", "X")))

# ---------------------------------------------------------------- own design examples
p_ratio = lambda w: zo(w) and c0(w) <= c1(w) <= 2 * c0(w)
D1 = G("S -> 0S1 | T; T -> 0T11 | ε")
check(f"design 1: L(S) = {{0^i1^j : i <= j <= 2i}} ({BND})", agrees(D1, p_ratio) is None)
check(f"design 1: L(T) = {{0^b 1^2b}} ({BND})", agrees(D1, lambda w: zo(w) and c1(w) == 2 * c0(w), start="T") is None)
check("design 1: unambiguous (one parse tree per string, |w| <= 14)",
      all(len(parse_trees(D1, w)) == 1 for w in strings(B, NX) if p_ratio(w)))
check("design 1 is not regular: F = 0*; for i < j <= 14, z = 1^i gives 0^i1^i in L and 0^j1^i not in L",
      all(p_ratio("0" * i + "1" * i) and not p_ratio("0" * j + "1" * i) for i in range(15) for j in range(i + 1, 15)))
check("... (the suffix 1^i does not work when j < i, e.g. 0^2 1^3 is in L, so name the strings with i < j)",
      p_ratio("00111"))
D1A = G("S -> 0S1 | 0S11 | ε")
check(f"design 1: S -> 0S1 | 0S11 | ε generates the same language ({BND})", agrees(D1A, p_ratio) is None)
check("design 1: ... but gives 00111 two parse trees", len(parse_trees(D1A, "00111")) == 2)
check("design 1: 0^i 1^j = 0^a (0^b 1^2b) 1^a with a = 2i - j, b = j - i (all i <= j <= 2i <= 20)",
      all("0" * i + "1" * j == "0" * (2 * i - j) + "0" * (j - i) + "1" * (2 * (j - i)) + "1" * (2 * i - j)
          for i in range(11) for j in range(i, 2 * i + 1)))
W1 = G("S -> 0S1 | 0S11 | 01 | 011")
check(f"design 1, one mistake: S -> 0S1 | 0S11 | 01 | 011 generates the language minus ε ({BND})",
      agrees(W1, lambda w: p_ratio(w) and w != "") is None)
W2 = G("S -> 0S1 | S1 | ε")
check(f"design 1, wrong: S -> 0S1 | S1 | ε generates {{0^i1^j : j >= i}} ({BND}), which contains 0111, 01111, ...",
      agrees(W2, lambda w: zo(w) and c1(w) >= c0(w)) is None
      and all(W2.generates("0" + "1" * k) and not p_ratio("0" + "1" * k) for k in range(3, 10)))
check("design 1 tests: ε, 01, 011, 0011, 00111, 001111 are in; 0, 1, 001, 0111, 0101 are out",
      all(D1.generates(w) for w in ["", "01", "011", "0011", "00111", "001111"])
      and not any(D1.generates(w) for w in ["0", "1", "001", "0111", "0101"]))
D2 = G("S -> A | B | N; A -> 0A | 0C; B -> B1 | C1; C -> ε | 0C1; N -> X10X; X -> ε | 0X | 1X")
not_0n1n = lambda w: not (zo(w) and c0(w) == c1(w))
check(f"design 2: L(S) = {{0,1}}* minus {{0^n1^n}} ({BND})", agrees(D2, not_0n1n) is None)
check(f"design 2: L(N) = strings containing 10 = strings not in 0*1* ({BND})",
      agrees(D2, lambda w: "10" in w, start="N") is None and all(("10" in w) == (not zo(w)) for w in strings(B, NX)))
check(f"design 2: L(X) = {{0,1}}* ({BND})", agrees(D2, lambda w: True, start="X") is None)
check("design 2 tests: 0, 1, 10, 001, 0110 are in; ε, 01, 0011 are out",
      all(D2.generates(w) for w in ["0", "1", "10", "001", "0110"]) and not any(D2.generates(w) for w in ["", "01", "0011"]))
check("design 2: S -> A | B alone (the running example) misses 10, 110, 0110, ... (every string containing 10)",
      not any(G0.generates(w) for w in ["10", "110", "0110"]) and all(D2.generates(w) for w in ["10", "110", "0110"])
      and not any(G0.generates(w) for w in strings(B, 10) if "10" in w))

# ---------------------------------------------------------------- the regular-expression grammars (trap)
SIG_R = "01+*()"
NAIVE = CFG("S", {"S": [("0",), ("1",), ("S", "+", "S"), ("S", "S"), ("S", "*"), ("(", "S", ")")]})
PREC = G("S -> S+T | T; T -> TF | F; F -> F* | (S) | 0 | 1")


def wellformed(w):
    try:
        _Parser(w).parse()
        return w != ""
    except SyntaxError:
        return False


check("naive grammar S -> 0 | 1 | S+S | SS | S* | (S) = well-formed regular expressions over 0, 1 "
      "(Earley, all strings |w| <= 6)", agrees(NAIVE, wellformed, SIG_R, 6) is None)
LN, LP = fixlang(NAIVE, 9)["S"], fixlang(PREC, 9)["S"]
WF7 = {w for w in strings(SIG_R, 7) if wellformed(w)}
check("naive grammar: exact language = well-formed expressions, all strings of length <= 7",
      {w for w in LN if len(w) <= 7} == WF7, f"{len(WF7)} expressions")
check("precedence grammar S -> S+T | T, T -> TF | F, F -> F* | (S) | 0 | 1: same language (exact, |w| <= 9)",
      LP == LN, f"{len(LP)} strings")
check("precedence grammar: Earley agrees with well-formedness on all strings |w| <= 6",
      agrees(PREC, wellformed, SIG_R, 6) is None)
check("0*+1* has 2 parse trees in the naive grammar and 1 in the precedence grammar",
      NAIVE.count_parse_trees("0*+1*") == 2 and PREC.count_parse_trees("0*+1*") == 1)
check("precedence grammar is unambiguous: one parse tree for every expression of length <= 7",
      all(PREC.count_parse_trees(w) == 1 for w in LP if len(w) <= 7))
check("precedence grammar parses 0*+1* as (0*)+(1*): root S -> S+T", root_split(PREC, "0*+1*") == ("S", ("0*", "+", "1*")))
def top_plus(w):
    d = 0
    for ch in w:
        d += (ch == "(") - (ch == ")")
        if ch == "+" and d == 0:
            return True
    return False


def single_atom(w):
    """w = atom followed by stars, atom = 0, 1 or a parenthesized expression whose '(' closes at its last ')'."""
    a = w.rstrip("*")
    if a in ("0", "1"):
        return True
    if len(a) >= 2 and a[0] == "(" and a[-1] == ")" and wellformed(a[1:-1]):
        d = 0
        for k, ch in enumerate(a):
            d += (ch == "(") - (ch == ")")
            if d == 0 and k < len(a) - 1:
                return False
        return True
    return False


FP = fixlang(PREC, 9)
WF9 = {w for w in LN}
check("precedence grammar: L(T) = expressions with no + outside parentheses (exact, |w| <= 9)",
      FP["T"] == {w for w in WF9 if not top_plus(w)})
check("precedence grammar: L(F) = 0, 1 or (expression), followed by zero or more stars (exact, |w| <= 9)",
      FP["F"] == {w for w in WF9 if single_atom(w)})
tg, tb = conv(FIG.TREE_RE_GOOD), conv(FIG.TREE_RE_BAD)
check("figure: the two trees of 0*+1* are valid naive-grammar trees and are all of them",
      valid_tree(NAIVE, tg, "S") and valid_tree(NAIVE, tb, "S") and set(parse_trees(NAIVE, "0*+1*")) == {tg, tb})
check("figure: left tree has root S -> S+S, right tree root S -> S* over 0*+1 (the meaning (0*+1)*)",
      tuple(k[0] for k in tg[1]) == ("S", "+", "S") and tuple(k[0] for k in tb[1]) == ("S", "*")
      and tree_yield(tb[1][0]) == "0*+1" and tree_yield(conv(FIG.OPND_GOOD)) == "1"
      and tree_yield(conv(FIG.OPND_BAD)) == "0*+1")

# ======================================================================== 5.5 regular languages are context-free
def lang_of_regex(t, n):
    """Exact truncated language of an expression tree: ("empty",), ("str", w), ("+", l, r), ("•", l, r), ("*", x)."""
    k = t[0]
    if k == "empty":
        return set()
    if k == "str":
        return {t[1]} if len(t[1]) <= n else set()
    if k == "+":
        return lang_of_regex(t[1], n) | lang_of_regex(t[2], n)
    if k == "•":
        A, Bs = lang_of_regex(t[1], n), lang_of_regex(t[2], n)
        return {x + y for x in A for y in Bs if len(x) + len(y) <= n}
    S, fr = {""}, {""}
    L = lang_of_regex(t[1], n)
    while fr:
        new = {x + y for x in L for y in fr if len(x) + len(y) <= n} - S
        S |= new
        fr = new
    return S


def regex_to_cfg(t, names):
    """The construction of §5.5, one fresh nonterminal per node, named in preorder from `names`."""
    names = iter(names)
    rules = {}

    def build(node):
        X = next(names)
        rules[X] = []
        k = node[0]
        if k == "empty":
            rules[X] = [(X,)]                       # X -> X : derives no string
        elif k == "str":
            rules[X] = [tuple(node[1])]             # X -> w (w = ε gives the empty rule)
        elif k == "+":
            a, b = build(node[1]), build(node[2])
            rules[X] = [(a,), (b,)]
        elif k == "•":
            a, b = build(node[1]), build(node[2])
            rules[X] = [(a, b)]
        else:
            a = build(node[1])
            rules[X] = [(), (a, X)]                 # X -> ε | aX
        return X

    start = build(t)
    return CFG(start, rules, terminals="01")


R4 = ("+", ("str", "0"), ("•", ("str", "1"), ("•", ("*", ("+", ("str", "0"), ("str", "1"))), ("str", "00"))))
G4 = regex_to_cfg(R4, "SABCDEFGHI")
G4_page = G("S -> A | B; A -> 0; B -> CD; C -> 1; D -> EI; E -> ε | FE; F -> G | H; G -> 0; H -> 1; I -> 00")
check("§5.5 table: the construction on 0+1(0+1)*00 gives exactly the grammar on the page",
      {A: set(r) for A, r in G4.rules.items()} == {A: set(r) for A, r in G4_page.rules.items()}, str(G4).replace("\n", "; "))
mult4 = lambda w: w == "0" or (len(w) >= 3 and w[0] == "1" and w.endswith("00"))
check(f"... and it generates exactly L(0+1(0+1)*00) ({BND})", agrees(G4_page, mult4) is None)
check("L(0+1(0+1)*00) = binary numerals of multiples of 4 without leading 0s (|w| <= 14)",
      all(mult4(w) == (w != "" and (w == "0" or w[0] == "1") and int(w, 2) % 4 == 0) for w in strings(B, NX)))
check(f"hand-made grammar S -> 0 | 1X00, X -> ε | 0X | 1X generates the same language ({BND})",
      agrees(G("S -> 0 | 1X00; X -> ε | 0X | 1X"), mult4) is None)


def all_trees(size):
    """All expression trees of the given size over ∅, ε, 0, 1 (strings as single leaves)."""
    if size == 1:
        return [("empty",), ("str", ""), ("str", "0"), ("str", "1")]
    out = [("*", x) for x in all_trees(size - 1)]
    for a in range(1, size - 1):
        for l in all_trees(a):
            for r in all_trees(size - 1 - a):
                out += [("+", l, r), ("•", l, r)]
    return out


ok, cnt = True, 0
for s in range(1, 6):
    for t in all_trees(s):
        cnt += 1
        g = regex_to_cfg(t, [f"N{i}" for i in range(20)])
        ok = ok and fixlang(g, 7)[g.start] == lang_of_regex(t, 7)
check(f"the construction is correct on all {cnt} expression trees of size <= 5 over ∅, ε, 0, 1 (exact, |w| <= 7)", ok)
check("{0^n1^n} is not regular: fooling set 0*, x = 0^i, y = 0^j, z = 1^i (i ≠ j <= 12)",
      all(langs0["C"]("0" * i + "1" * i) and not langs0["C"]("0" * j + "1" * i)
          for i in range(13) for j in range(13) if i != j))

# ======================================================================== 5.6 counting; closure properties
L1 = G("S -> CR; C -> 0C1 | 01; R -> 0R | ε")
L2 = G("S -> PD; P -> 0P | ε; D -> 1D0 | 10")
blocks = lambda w: re.fullmatch("(0*)(1+)(0*)", w)          # unique split when w contains a 1
p1 = lambda w: bool(blocks(w)) and len(blocks(w).group(1)) == len(blocks(w).group(2))
p2 = lambda w: bool(blocks(w)) and len(blocks(w).group(2)) == len(blocks(w).group(3))
p010 = lambda w: w == "" or (bool(blocks(w)) and len(blocks(w).group(1)) == len(blocks(w).group(2))
                             == len(blocks(w).group(3)))
check(f"closure: S -> CR, C -> 0C1 | 01, R -> 0R | ε generates {{0^i 1^i 0^j : i >= 1, j >= 0}} ({BND})",
      agrees(L1, p1) is None and all(p1("0" * i + "1" * i + "0" * j) == (i >= 1) for i in range(6) for j in range(6)))
check(f"closure: S -> PD, P -> 0P | ε, D -> 1D0 | 10 generates {{0^i 1^j 0^j : i >= 0, j >= 1}} ({BND})",
      agrees(L2, p2) is None and all(p2("0" * i + "1" * j + "0" * j) == (j >= 1) for i in range(6) for j in range(6)))
check("their intersection is {0^n 1^n 0^n : n >= 1}, all strings |w| <= 15",
      all((p1(w) and p2(w)) == (p010(w) and w != "") for w in strings(B, 15)))
L1u = G("S -> CR; C -> 0C1 | ε; R -> 0R | ε")
L2u = G("S -> PD; P -> 0P | ε; D -> 1D0 | ε")
check("without the forced 1s, both languages contain every 0^k (k <= 10), so their intersection does too",
      all(L1u.generates("0" * k) and L2u.generates("0" * k) for k in range(11)))
REV = CFG(G0.start, {A: [tuple(reversed(r)) for r in rhs] for A, rhs in G0.rules.items()})
check(f"reversal: reversing every right side of the running example generates {{1^n 0^m : m ≠ n}} ({BND})",
      agrees(REV, lambda w: G0.generates(w[::-1])) is None
      and agrees(REV, lambda w: re.fullmatch("1*0*", w) is not None and c0(w) != c1(w)) is None)

# ======================================================================== 5.7 recursive automata
def ra_succ(mods, conf, w):
    """Successor configurations (i, q, stack) of a configuration: read, ε, call, return."""
    out_edges = {}
    for m in mods.values():
        for p, lab, q in m["edges"]:
            out_edges.setdefault(p, []).append((lab, q))
    accepting = {m["accept"] for m in mods.values()}
    i, q, st = conf
    res = []
    for lab, p in out_edges.get(q, []):
        if lab == "ε":
            res.append((i, p, st))
        elif lab.startswith("$"):
            res.append((i, mods[lab[1:]]["start"], (p,) + st))
        elif i < len(w) and w[i] == lab:
            res.append((i + 1, p, st))
    if q in accepting and st:
        res.append((i, st[0], st[1:]))
    return res


def ra_accepts(mods, main, w, cap):
    """Search all configurations with stack depth <= cap; returns (accepted, cap_was_hit)."""
    init, goal = (0, mods[main]["start"], ()), (len(w), mods[main]["accept"], ())
    seen, todo, hit = {init}, [init], False
    while todo:
        c = todo.pop()
        if c == goal:
            return True, hit
        for d in ra_succ(mods, c, w):
            if len(d[2]) > cap:
                hit = True
                continue
            if d not in seen:
                seen.add(d)
                todo.append(d)
    return False, hit


RA = FIG.RA_MODULES
res = [(w, ra_accepts(RA, "S", w, len(w) + 2)) for w in strings(B, 12)]
check("figure automaton accepts exactly {0^m1^n : m ≠ n} (all strings |w| <= 12)",
      all(acc == langs0["S"](w) for w, (acc, _) in res))
check("... and the search was exhaustive: no configuration needed a stack deeper than |w| + 2",
      not any(hit for _, (_, hit) in res))
check("module E alone accepts exactly {0^n1^n} (|w| <= 12)",
      all(ra_accepts(RA, "E", w, len(w) + 2) == (langs0["C"](w), False) for w in strings(B, 12)))
trace = [("001", "sS", ()), ("01", "a", ()), ("01", "sE", ("tS",)), ("1", "c", ("tS",)), ("1", "sE", ("d", "tS")),
         ("1", "tE", ("d", "tS")), ("1", "d", ("tS",)), ("", "tE", ("tS",)), ("", "tS", ())]
confs = [(3 - len(x), q, st) for x, q, st in trace]
check("trace on 001: every line is one legal transition after the previous one; starts (001, s_S, ε), ends "
      "(ε, t_S, ε)", all(b in ra_succ(RA, a, "001") for a, b in zip(confs, confs[1:]))
      and confs[0] == (0, "sS", ()) and confs[-1] == (3, "tS", ()))


def cfg_to_ra(g):
    """Lemma 5.5: one module per nonterminal, one path s_A -> t_A per rule (an ε-edge for an ε-rule)."""
    mods = {}
    for A, rhs in g.rules.items():
        s, t, edges = f"s{A}", f"t{A}", []
        for k, r in enumerate(rhs):
            if not r:
                edges.append((s, "ε", t))
                continue
            prev = s
            for idx, X in enumerate(r):
                nxt = t if idx == len(r) - 1 else f"{A}.{k}.{idx}"
                edges.append((prev, "$" + X if X in g.rules else X, nxt))
                prev = nxt
        mods[A] = {"start": s, "accept": t, "edges": edges}
    return mods


RA0 = cfg_to_ra(G0)
check("Lemma 5.5 on the running example: the automaton accepts L(S) = {0^m1^n : m ≠ n} (|w| <= 10, stack <= 2|w|+4)",
      all(ra_accepts(RA0, "S", w, 2 * len(w) + 4)[0] == langs0["S"](w) for w in strings(B, 10)))
check("Lemma 5.5: module E of the figure is exactly the construction for E -> 0E1 | ε (states renamed)",
      cfg_to_ra(G("E -> 0E1 | ε"))["E"]["edges"] == [("sE", "0", "E.0.0"), ("E.0.0", "$E", "E.0.1"),
                                                     ("E.0.1", "1", "tE"), ("sE", "ε", "tE")]
      and RA["E"]["edges"] == [("sE", "0", "c"), ("c", "$E", "d"), ("d", "1", "tE"), ("sE", "ε", "tE")])


def ra_to_cfg(mods, main):
    """Lemma 5.6: nonterminal [q] per state; [q] -> a[p], [q] -> [p], [q] -> [s_A][p], [t_A] -> ε."""
    rules = {}

    def Nq(q):
        return f"[{q}]"

    for m in mods.values():
        for p, lab, q in m["edges"]:
            rules.setdefault(Nq(p), [])
            rules.setdefault(Nq(q), [])
            if lab == "ε":
                rules[Nq(p)].append((Nq(q),))
            elif lab.startswith("$"):
                rules[Nq(p)].append((Nq(mods[lab[1:]]["start"]), Nq(q)))
            else:
                rules[Nq(p)].append((lab, Nq(q)))
        rules.setdefault(Nq(m["accept"]), []).append(())
    return CFG(Nq(mods[main]["start"]), rules)


G56 = ra_to_cfg(RA, "S")
page56 = {"[sS]": {("0", "[a]"), ("[sE]", "[b]")}, "[a]": {("0", "[a]"), ("[sE]", "[tS]")},
          "[b]": {("1", "[b]"), ("1", "[tS]")}, "[tS]": {()}, "[sE]": {("0", "[c]"), ("[tE]",)},
          "[c]": {("[sE]", "[d]")}, "[d]": {("1", "[tE]")}, "[tE]": {()}}
check("Lemma 5.6 on the figure: the conversion gives exactly the grammar on the page",
      {A: set(r) for A, r in G56.rules.items()} == page56)
for X, p, txt in (("[sS]", langs0["S"], "0^m1^n, m ≠ n"), ("[a]", lambda w: zo(w) and c0(w) >= c1(w), "0^m1^n, m >= n"),
                  ("[b]", lambda w: w != "" and set(w) == {"1"}, "1^+"), ("[tS]", lambda w: w == "", "ε"),
                  ("[sE]", langs0["C"], "0^n1^n"), ("[c]", lambda w: zo(w) and c1(w) == c0(w) + 1, "0^n1^(n+1)"),
                  ("[d]", lambda w: w == "1", "1"), ("[tE]", lambda w: w == "", "ε")):
    check(f"Lemma 5.6 grammar: L({X}) = {txt} (|w| <= 12)", agrees(G56, p, B, 12, start=X) is None)

PAR_RA = {"M": {"start": "s", "accept": "t",
                "edges": [("s", "0", "s"), ("s", "1", "t"), ("t", "0", "t"), ("t", "1", "s")]}}
GP = ra_to_cfg(PAR_RA, "M")
check("an NFA with no calls (the parity DFA of §3.3) becomes [s] -> 0[s] | 1[t], [t] -> 0[t] | 1[s] | ε",
      {A: set(r) for A, r in GP.rules.items()} == {"[s]": {("0", "[s]"), ("1", "[t]")},
                                                   "[t]": {("0", "[t]"), ("1", "[s]"), ()}})
check(f"... which generates the strings with an odd number of 1s ({BND})", agrees(GP, lambda w: c1(w) % 2 == 1) is None)

# ======================================================================== 5.8 Chomsky normal form
CNF = G("S -> EA | EC | BF | CF | 0 | 1; A -> EA | EC | 0; B -> BF | CF | 1; C -> ED; D -> CF | 1; E -> 0; F -> 1")
check("the book's CNF grammar is in CNF (CFG.is_cnf)", CNF.is_cnf()[0], str(CNF.is_cnf()))
check(f"the book's CNF grammar generates {{0^m1^n : m ≠ n}} ({BND})", agrees(CNF, langs0["S"]) is None)
tc = conv(FIG.TREE_CNF_00011)
check("figure: CNF tree is a valid parse tree of 00011", valid_tree(CNF, tc, "S") and tree_yield(tc) == "00011")
check("figure: it has 9 = 2·5 - 1 nonterminal nodes: 5 of the form A -> a, 4 of the form A -> BC",
      nt_nodes(tc) == 9
      and (lambda f: f(f, tc))(lambda f, n: (1 if len(n[1]) == 1 and not n[1][0][1] else 0)
                               + sum(f(f, k) for k in n[1])) == 5
      and (lambda f: f(f, tc))(lambda f, n: (1 if len(n[1]) == 2 else 0) + sum(f(f, k) for k in n[1])) == 4)
check("figure: it is the only parse tree of 00011", parse_trees(CNF, "00011") == [tc])
ok, total = True, 0
for w in strings(B, 9):
    if w:
        for t in parse_trees(CNF, w):
            total += 1
            ok = ok and nt_nodes(t) == 2 * len(w) - 1
check(f"2n - 1: every parse tree of every string of length 1..9 has 2n - 1 nonterminal nodes ({total} trees)", ok)


def all_derivations_lengths(g, w):
    """Lengths of all derivations S ⇝* w (any order of expansion); g in CNF without ε-rules."""
    from collections import Counter
    lengths = Counter()
    frontier = Counter({g.start: 1})
    steps = 0
    while frontier:
        nxt = Counter()
        for f, mult in frontier.items():
            if f == w:
                lengths[steps] += mult
                continue
            if len(f) > len(w):
                continue
            for i, X in enumerate(f):
                if X in g.rules:
                    for r in g.rules[X]:
                        nxt[f[:i] + "".join(r) + f[i + 1:]] += mult
        frontier = nxt
        steps += 1
        if steps > 4 * len(w) + 4:
            break
    return lengths


lens = all_derivations_lengths(CNF, "00011")
check("every derivation of 00011 in the CNF grammar has exactly 9 steps", set(lens) == {9}, f"{dict(lens)} derivations")


def cyk(g, w):
    n = len(w)
    if n == 0:
        return () in g.rules[g.start]
    can = {}
    for i in range(n):
        can[(i, i + 1)] = {A for A, rhs in g.rules.items() if (w[i],) in rhs}
    for span in range(2, n + 1):
        for i in range(0, n - span + 1):
            j = i + span
            can[(i, j)] = {A for A, rhs in g.rules.items() for r in rhs if len(r) == 2
                           and any(r[0] in can[(i, k)] and r[1] in can[(k, j)] for k in range(i + 1, j))}
    return g.start in can[(0, n)]


check("CYK (dynamic programming) agrees with Earley on the CNF grammar for all strings |w| <= 12",
      first_difference(lambda w: cyk(CNF, w), CNF.generates, B, 12) is None)

# ======================================================================== 5.9 the CNF conversion algorithm
def cnf_convert(g, split_names, term_names, new_start="S'", book_drop=False):
    """Steps 0-6 of §5.9 as described on the page. Returns the list of (step, rules, start) snapshots.
    book_drop=True: drop S' after step 2 whenever S' is not nullable (the book's rule), ignoring whether S is
    on a right side."""
    snaps = []
    S0 = new_start
    rules = {S0: [(g.start,)]}
    rules.update({A: list(r) for A, r in g.rules.items()})
    start = S0
    snaps.append(("0", {A: list(r) for A, r in rules.items()}, start))
    # step 1: split long rules A -> X α (|α| >= 2) into A -> X B, B -> α
    names = iter(split_names)
    changed = True
    while changed:
        changed = False
        for A in list(rules):
            for k, r in enumerate(rules[A]):
                if len(r) >= 3:
                    Bn = next(names)
                    rules[A][k] = (r[0], Bn)
                    rules[Bn] = [tuple(r[1:])]
                    changed = True
    snaps.append(("1", {A: list(r) for A, r in rules.items()}, start))
    # step 2: nullable nonterminals (fixed point); drop S' -> S again if S' is not nullable and S is on no right side
    nul = set()
    ch = True
    while ch:
        ch = False
        for A, rhs in rules.items():
            if A not in nul and any(all(x in nul for x in r) for r in rhs):
                nul.add(A)
                ch = True
    on_right = any(g.start in r for A, rhs in rules.items() if A != S0 for r in rhs)
    if S0 not in nul and (book_drop or not on_right):
        del rules[S0]
        start = g.start
    snaps.append(("2", {A: list(r) for A, r in rules.items()}, start, set(nul)))
    # step 3: add every non-empty variant without some nullable occurrences; delete ε-rules (keep start -> ε)
    new = {}
    for A, rhs in rules.items():
        out = []
        for r in rhs:
            pos = [i for i, x in enumerate(r) if x in nul]
            for m in range(len(pos) + 1):
                for drop in combinations(pos, m):
                    v = tuple(x for i, x in enumerate(r) if i not in drop)
                    if v and v not in out:
                        out.append(v)
        new[A] = out
    if start in nul:
        new[start].append(())
    rules = new
    snaps.append(("3", {A: list(r) for A, r in rules.items()}, start))
    # step 4: merge nonterminals that reach each other by unit rules (strong components of the unit-rule graph)
    unit = {A: {r[0] for r in rhs if len(r) == 1 and r[0] in rules} for A, rhs in rules.items()}

    def reach(A):
        seen, todo = {A}, [A]
        while todo:
            for Bn in unit[todo.pop()]:
                if Bn not in seen:
                    seen.add(Bn)
                    todo.append(Bn)
        return seen

    R = {A: reach(A) for A in rules}
    rep = {}
    for A in rules:
        comp = [Bn for Bn in rules if Bn in R[A] and A in R[Bn]]
        rep[A] = start if start in comp else comp[0]
    merged = {}
    for A, rhs in rules.items():
        tgt = merged.setdefault(rep[A], [])
        for r in rhs:
            v = tuple(rep.get(x, x) for x in r)
            if v != (rep[A],) and v not in tgt:
                tgt.append(v)
    rules = merged
    n_merged = len(set(rep.values())) != len(rep)
    snaps.append(("4", {A: list(r) for A, r in rules.items()}, start, n_merged))
    # step 5: remove unit rules, in reverse topological order of the (now acyclic) unit-rule graph
    unit = {A: [r[0] for r in rhs if len(r) == 1 and r[0] in rules] for A, rhs in rules.items()}
    order, done = [], set()

    def visit(A):
        if A in done:
            return
        done.add(A)
        for Bn in unit[A]:
            visit(Bn)
        order.append(A)                       # every unit-successor of A comes before A

    for A in rules:
        visit(A)
    for A in order:
        out = []
        for r in rules[A]:
            if len(r) == 1 and r[0] in rules:
                out += [x for x in rules[r[0]] if x not in out]
            elif r not in out:
                out.append(r)
        rules[A] = out
    snaps.append(("5", {A: list(r) for A, r in rules.items()}, start))
    # step 6: protect terminals in rules of length 2
    used = sorted({x for rhs in rules.values() for r in rhs if len(r) == 2 for x in r if x not in rules})
    for a in used:
        rules[term_names[a]] = [(a,)]
    for A in list(rules):
        rules[A] = [tuple(term_names[x] if (len(r) == 2 and x in term_names and x not in rules) else x for x in r)
                    for r in rules[A]]
    snaps.append(("6", {A: list(r) for A, r in rules.items()}, start))
    return snaps


def cfg(rules, start):
    return CFG(start, rules)


def same_rules(rules, text, **kw):
    g = G(text, **kw)
    return {A: set(r) for A, r in rules.items()} == {A: set(r) for A, r in g.rules.items()}


snaps = cnf_convert(G0, ["D"], {"0": "E", "1": "F"})
page = {
    "0": "S' -> S; S -> A | B; A -> 0A | 0C; B -> B1 | C1; C -> ε | 0C1",
    "1": "S' -> S; S -> A | B; A -> 0A | 0C; B -> B1 | C1; C -> ε | 0D; D -> C1",
    "2": "S -> A | B; A -> 0A | 0C; B -> B1 | C1; C -> ε | 0D; D -> C1",
    "3": "S -> A | B; A -> 0A | 0C | 0; B -> B1 | C1 | 1; C -> 0D; D -> C1 | 1",
    "4": "S -> A | B; A -> 0A | 0C | 0; B -> B1 | C1 | 1; C -> 0D; D -> C1 | 1",
    "5": "S -> 0A | 0C | B1 | C1 | 0 | 1; A -> 0A | 0C | 0; B -> B1 | C1 | 1; C -> 0D; D -> C1 | 1",
    "6": "S -> EA | EC | BF | CF | 0 | 1; A -> EA | EC | 0; B -> BF | CF | 1; C -> ED; D -> CF | 1; E -> 0; F -> 1",
}
for sn in snaps:
    step, rules, start = sn[0], sn[1], sn[2]
    check(f"CNF step {step}: the algorithm's grammar is the one on the page",
          same_rules(rules, page[step], nonterminals=["S'"]), "; ".join(
              f"{A} -> {' | '.join(''.join(r) or 'ε' for r in rs)}" for A, rs in rules.items()))
    d = agrees(cfg(rules, start), langs0["S"])
    check(f"CNF step {step}: the grammar still generates {{0^m1^n : m ≠ n}} ({BND})", d is None, f"{d!r}")
check("CNF step 2: C is the only nullable nonterminal, so S' -> S is dropped (S is on no right side)",
      snaps[2][3] == {"C"} and "S'" not in snaps[2][1] and snaps[2][2] == "S")
check(f"CNF step 3: no ε-rules remain; L(C) = {{0^n1^n : n >= 1}}, L(D) = {{0^n 1^(n+1)}} ({BND})",
      all(() not in r for r in snaps[3][1].values())
      and agrees(cfg(snaps[3][1], "S"), lambda w: langs0["C"](w) and w != "", start="C") is None
      and agrees(cfg(snaps[3][1], "S"), lambda w: zo(w) and c1(w) == c0(w) + 1, start="D") is None)
check("CNF step 4: no unit-rule cycles, nothing merged", snaps[4][3] is False)
check("CNF step 5: no unit rules remain", all(not (len(r) == 1 and r[0] in snaps[5][1]) for rs in snaps[5][1].values()
                                              for r in rs))
check("CNF step 6 = the book's CNF grammar, and is_cnf", same_rules(snaps[6][1], str(CNF).replace("\n", ";"))
      and cfg(snaps[6][1], "S").is_cnf()[0])
# step 0 (review): S' may be dropped after step 2 only if S' is not nullable AND S is on no right side
RS = G("S -> 0S | 1")
p01 = lambda w: re.fullmatch("0*1", w) is not None
sn_pg = cnf_convert(RS, [f"N{i}" for i in range(9)], {"0": "T0", "1": "T1"})
sn_bk = cnf_convert(RS, [f"N{i}" for i in range(9)], {"0": "T0", "1": "T1"}, book_drop=True)
fin_pg, fin_bk = cfg(sn_pg[-1][1], sn_pg[-1][2]), cfg(sn_bk[-1][1], sn_bk[-1][2])
check("step 0: on S -> 0S | 1 (S on a right side, not nullable) the page's rule keeps S'; the result is in CNF "
      f"and generates 0*1 ({BND})", sn_pg[2][2] == "S'" and fin_pg.is_cnf()[0] and agrees(fin_pg, p01) is None)
check("step 0: the book's rule (drop S' whenever it is not nullable) leaves the start symbol S on a right side "
      "there, so its result is not in CNF", sn_bk[2][2] == "S" and not fin_bk.is_cnf()[0]
      and "start symbol on a right side" in fin_bk.is_cnf()[1])
sn_eq = cnf_convert(EQ1, [f"N{i}" for i in range(9)], {"0": "T0", "1": "T1"})
check("step 3 adds S' -> ε when S' is nullable: on S -> ε | SS | 0S1 | 1S0 the result's only ε-rule is S' -> ε",
      [(A, r) for A, rs in sn_eq[-1][1].items() for r in rs if r == ()] == [("S'", ())]
      and cfg(sn_eq[-1][1], sn_eq[-1][2]).generates(""))
check("step 4 deletes every rule A -> A: there step 3 turns S -> SS into S -> S, and step 4 drops it",
      ("S",) in sn_eq[3][1]["S"] and ("S",) not in sn_eq[4][1]["S"])
# the same algorithm on the other grammars of the page: CNF and the same language
for name, g, pred, alph, n in (("palindromes", PAL, lambda w: w == w[::-1], B, 12),
                               ("#0 = #1 (S -> 0S1 | 1S0 | SS | ε)", EQ2, p_eq, B, 12),
                               ("balanced parentheses (S -> (S)S | ε)", PAR2, balanced, "()", 14),
                               ("Lemma 5.3 grammar", EQ1, p_eq, B, 12),
                               ("#0 ≠ #1", NE, lambda w: c0(w) != c1(w), B, 10),
                               ("expressions", EXPR, expr_ok, SIG_E, 5)):
    sn = cnf_convert(g, [f"N{i}" for i in range(40)], {a: f"T{ord(a)}" for a in g.terminals})
    final = cfg(sn[-1][1], sn[-1][2])
    check(f"the conversion on {name}: CNF, same language (|w| <= {n})",
          final.is_cnf()[0] and agrees(final, pred, alph, n) is None, str(final.is_cnf()))

UG = {"S": [("A",)], "A": [("B",), ("1",)], "B": [("0", "B"), ("0",)]}


def unit_remove(rules, order):
    rules = {A: list(r) for A, r in rules.items()}
    for A in order:
        out = []
        for r in rules[A]:
            src = rules[r[0]] if (len(r) == 1 and r[0] in rules) else [r]
            out += [x for x in src if x not in out]
        rules[A] = out
    return rules


good, bad = unit_remove(UG, ["B", "A", "S"]), unit_remove(UG, ["S", "A", "B"])
check("step 5 order: on S -> A, A -> B | 1, B -> 0B | 0, reverse topological order removes every unit rule, "
      "the wrong order leaves S -> B",
      all(not (len(r) == 1 and r[0] in good) for rs in good.values() for r in rs) and ("B",) in bad["S"]
      and agrees(CFG("S", good), lambda w: w == "1" or (w != "" and set(w) == {"0"})) is None)

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: {FAIL}")
sys.exit(1 if FAIL else 0)
