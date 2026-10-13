#!/usr/bin/env python3
"""Checks for six worked problems in content/problems/:

  1. induction-on-a-recursive-string-function.md   (sort: |sort(w)| = |w|, sort(sort(w)) = sort(w))
  2. regular-expression-and-dfa-for-one-language.md (the substring 01 occurs exactly twice)
  3. fooling-set-and-grammar-for-one-language.md   ({0^i 1^j 0^k : j = i + k})
  4. two-language-transformations.md               (Insert1 and Delete1)
  5. a-product-construction-written-formally.md    (#1 divisible by 3, and no 00)
  6. subset-construction-by-hand.md                (an NFA for 0*(01)*1*)

Every predicate below is written from the problem statement, independently of the answers on the pages.
Regular languages are compared exactly (DFA equivalence); everything else by brute force over all short strings."""
import os
import random
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from automata import CFG, DFA, EPS, NFA, Regex, first_difference, strings  # noqa: E402

FAIL = []


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAIL.append(name)


AB = "01"


def R(text):
    return Regex(text, alphabet=AB)


def same(expr, machine):
    """Exact equivalence of a regular expression with a DFA or NFA: (bool, shortest counterexample)."""
    return R(expr).equivalent(machine)


def shortest_suffix(x, y, L, maxlen=8):
    for z in strings(AB, maxlen):
        if L(x + z) != L(y + z):
            return z
    return None


def fmt(S):
    return "∅" if not S else "{" + ",".join(sorted(map(str, S))) + "}"


# =============================================================================================== problem 1
print("== Problem 1: sort")


def cons(a, x):                      # a·x
    assert len(a) == 1
    return a + x


def cat(w, z):                       # ε•z = z, (ax)•z = a·(x•z)
    return z if w == "" else cons(w[0], cat(w[1:], z))


def length(w):                       # |ε| = 0, |ax| = 1 + |x|
    return 0 if w == "" else 1 + length(w[1:])


def srt(w):                          # sort(ε) = ε, sort(0x) = 0·sort(x), sort(1x) = sort(x)•1
    if w == "":
        return ""
    a, x = w[0], w[1:]
    return cons("0", srt(x)) if a == "0" else cat(srt(x), "1")


N1 = 14
ALL1 = list(strings(AB, N1))
check("examples: sort(0110) = 0011, sort(1010) = 0011, sort(101) = 011, sort(111) = 111, sort(ε) = ε",
      srt("0110") == "0011" and srt("1010") == "0011" and srt("101") == "011" and srt("111") == "111" and srt("") == "")
check("unfolding sort(101): sort(1) = 1, sort(01) = 01, sort(101) = sort(01)•1 = 011",
      srt("1") == "1" and srt("01") == "01" and srt("101") == cat(srt("01"), "1") == "011")
check(f"(a) |sort(w)| = |w| for all |w| <= {N1}", all(length(srt(w)) == length(w) for w in ALL1))
check(f"Lemma: sort(y•1) = sort(y)•1 for all |y| <= {N1}", all(srt(cat(y, "1")) == cat(srt(y), "1") for y in ALL1))
check(f"(b) sort(sort(w)) = sort(w) for all |w| <= {N1}", all(srt(srt(w)) == srt(w) for w in ALL1))
check(f"closed form: sort(w) = 0^#(0,w) 1^#(1,w) for all |w| <= {N1}",
      all(srt(w) == "0" * w.count("0") + "1" * w.count("1") for w in ALL1))
check("trap: for w = 1x the string sort(x)•1 is as long as w (the hypothesis does not cover it), |w| <= 12",
      all(length(cat(srt(w[1:]), "1")) == length(w) for w in strings(AB, 12) if w[:1] == "1"))
check("for w = 1x the lemma is used with y = sort(x), which is shorter than w (|sort(x)| = |w| - 1), on the string "
      "sort(x)•1, which is exactly as long as w, |w| <= 12",
      all(length(srt(w[1:])) == length(w) - 1 and length(cat(srt(w[1:]), "1")) == length(w)
          for w in strings(AB, 12) if w[:1] == "1"))
check("the first symbol of sort(x)•1 is the attached 1 only when x = ε (otherwise it is the first symbol of sort(x)), "
      "|x| <= 12",
      cat(srt(""), "1") == "1" and all(len(srt(x)) >= 1 and cat(srt(x), "1")[0] == srt(x)[0]
                                       for x in strings(AB, 12) if x))
check("trap: the look-alike 'sort(y•0) = sort(y)•0' fails at y = 1 (sort(10) = 01, sort(1)•0 = 10)",
      srt(cat("1", "0")) == "01" and cat(srt("1"), "0") == "10")
check("trap: sort does not distribute over •: sort(1•0) = 01 but sort(1)•sort(0) = 10",
      srt("10") == "01" and cat(srt("1"), srt("0")) == "10")

# =============================================================================================== problem 2
print("== Problem 2: the substring 01 occurs exactly twice")


def occ(u, w):
    return sum(1 for i in range(len(w) - len(u) + 1) if w[i:i + len(u)] == u)


L2 = lambda w: occ("01", w) == 2  # noqa: E731
ST2 = ["ones0", "zeros0", "ones1", "zeros1", "ones2", "zeros2", "dead"]
d2 = {("dead", "0"): "dead", ("dead", "1"): "dead"}
for k in range(3):
    d2[(f"ones{k}", "0")] = f"zeros{k}"
    d2[(f"ones{k}", "1")] = f"ones{k}"
    d2[(f"zeros{k}", "0")] = f"zeros{k}"
    d2[(f"zeros{k}", "1")] = f"ones{k + 1}" if k < 2 else "dead"
M2 = DFA(AB, ST2, "ones0", ["ones2", "zeros2"], d2)
check("DFA accepts exactly the strings with exactly two occurrences of 01, |w| <= 14",
      first_difference(M2.accepts, L2, AB, 14) is None)


def meaning2(w):
    k = occ("01", w)
    if k >= 3:
        return "dead"
    return (f"zeros{k}" if w.endswith("0") else f"ones{k}")


check("every state means what the table says (count of 01 so far, last symbol 0 or not), |w| <= 12",
      all(M2.delta_star("ones0", w) == meaning2(w) for w in strings(AB, 12)))
# an independent DFA straight from the statement: (count capped at 3, last symbol)
Pred2 = DFA.explore(AB, (0, ""), lambda q, a: (min(3, q[0] + (q[1] == "0" and a == "1")), a), lambda q: q[0] == 2)
check("DFA is exactly equivalent to the counting machine built from the statement", M2.equivalent(Pred2)[0])
RE2 = "1*00*11*00*11*0*"
check(f"regular expression {RE2} is exactly equivalent to the DFA", same(RE2, M2)[0])
check("the 7-state DFA is minimal", len(M2.minimize().states) == 7)
F2 = ["", "0", "01", "010", "0101", "01010", "010101"]
check("representatives ε, 0, 01, 010, 0101, 01010, 010101 reach the seven states in order",
      [M2.delta_star("ones0", x) for x in F2] == ST2)
rows = []
ok = True
for i, x in enumerate(F2):
    for y in F2[i + 1:]:
        z = shortest_suffix(x, y, L2)
        ok = ok and z is not None
        rows.append(f"{x or 'ε'}/{y}:{z!r}")
check("they form a fooling set (every pair has a distinguishing suffix)", ok, "; ".join(rows))
check("in L: 0101, 01010, 1001101, 00110011; not in L: ε, 01, 0110, 1100, 010101",
      all(L2(w) and M2(w) for w in ["0101", "01010", "1001101", "00110011"])
      and not any(L2(w) or M2(w) for w in ["", "01", "0110", "1100", "010101"]))
check("run on 1001101: ones0 ones0 zeros0 zeros0 ones1 ones1 zeros1 ones2 (accept)",
      M2.run("1001101") == ["ones0", "ones0", "zeros0", "zeros0", "ones1", "ones1", "zeros1", "ones2"])
check("run on 010101 ends in dead; ε stays in ones0 (reject)", M2.run("010101")[-1] == "dead" and not M2(""))
check("trap: 0110 has two symbol switches but only one occurrence of 01",
      sum(1 for i in range(3) if "0110"[i] != "0110"[i + 1]) == 2 and occ("01", "0110") == 1)
cnt = lambda acc: DFA.explore(AB, (0, ""), lambda q, a: (min(3, q[0] + (q[1] == "0" and a == "1")), a), acc)  # noqa: E731
check("what the wrong answers describe, exactly: at least two / at most two / L and starts with 0 / L and ends in 1",
      same("(0+1)*01(0+1)*01(0+1)*", cnt(lambda q: q[0] >= 2))[0] and same("1*0*1*0*1*0*", cnt(lambda q: q[0] <= 2))[0]
      and same("00*11*00*11*0*", M2.product(DFA.explore(AB, "", lambda q, a: q or a, lambda q: q == "0"), "and"))[0]
      and same("1*00*11*00*11*", M2.product(DFA.explore(AB, "", lambda q, a: a, lambda q: q == "1"), "and"))[0])
WRONG2 = {
    "(0+1)*01(0+1)*01(0+1)*": ("010101", lambda n: "01" * n, range(3, 8)),       # at least two
    "1*0*1*0*1*0*": ("", lambda n: "1" * n, range(0, 6)),                         # at most two
    "00*11*00*11*0*": ("10101", lambda n: "1" * n + "0101", range(1, 6)),          # no leading 1s
    "1*00*11*00*11*": ("01010", lambda n: "0101" + "0" * n, range(1, 6)),          # no trailing 0s
}
for expr, (wit, fam, rng_) in WRONG2.items():
    eq, cex = same(expr, M2)
    inf = all(R(expr)(fam(n)) != L2(fam(n)) for n in rng_)
    check(f"wrong answer {expr}: shortest counterexample {wit!r}, and wrong on a whole infinite family",
          (not eq) and cex == wit and inf, f"cex={cex!r}")

# =============================================================================================== problem 3
print("== Problem 3: {0^i 1^j 0^k : j = i + k}")


def L3(w):
    """Exists i, j, k >= 0 with j = i + k and w = 0^i 1^j 0^k (all decompositions tried)."""
    n = len(w)
    for i in range(n + 1):
        for k in range(n + 1 - i):
            j = i + k
            if i + j + k == n and w == "0" * i + "1" * j + "0" * k:
                return True
    return False


G3 = CFG.parse("S -> AB\nA -> 0A1 | eps\nB -> 1B0 | eps")
N3 = 12
check(f"grammar S -> AB, A -> 0A1 | ε, B -> 1B0 | ε generates exactly L, all |w| <= {N3}",
      first_difference(G3.generates, L3, AB, N3) is None)
check(f"L(A) = {{0^n 1^n}} and L(B) = {{1^n 0^n}}, |w| <= {N3}",
      first_difference(lambda w: G3.generates(w, "A"), lambda w: w == "0" * (len(w) // 2) + "1" * (len(w) // 2)
                       and len(w) % 2 == 0, AB, N3) is None
      and first_difference(lambda w: G3.generates(w, "B"), lambda w: w == "1" * (len(w) // 2) + "0" * (len(w) // 2)
                           and len(w) % 2 == 0, AB, N3) is None)
check("examples in L: ε, 01, 10, 0110, 001110; not in L: 0, 1, 0101, 1001",
      all(L3(w) for w in ["", "01", "10", "0110", "001110"]) and not any(L3(w) for w in ["0", "1", "0101", "1001"]))
check("001110 = (0011)(10) with A =>* 0011 and B =>* 10", G3.generates("0011", "A") and G3.generates("10", "B"))
check("every string in L has equally many 0s and 1s (|w| <= 14)",
      all(w.count("0") == w.count("1") for w in strings(AB, 14) if L3(w)))
check("fooling set 0*: x = 0^m, y = 0^n (m != n, 0..18), z = 1^m: xz in L, yz not",
      all(L3("0" * m + "1" * m) and not L3("0" * n + "1" * m) for m in range(19) for n in range(19) if m != n))
check("edge case m = 0: yz = 0^n (n >= 1) is not in L, although it splits as 0^i 1^0 0^k in n+1 ways",
      all(not L3("0" * n) for n in range(1, 15)))
check("trap: the finite set {ε, 0, 00} is a fooling set for L (every pair has a distinguishing suffix)",
      all(shortest_suffix(x, y, L3) is not None for x, y in [("", "0"), ("", "00"), ("0", "00")]))
check("closure: L ∩ 0*1* = {0^n 1^n}, |w| <= 14",
      all((L3(w) and re.fullmatch("0*1*", w) is not None) == (w == "0" * (len(w) // 2) + "1" * (len(w) // 2)
                                                             and len(w) % 2 == 0) for w in strings(AB, 14)))
W3a = CFG.parse("S -> 0S1 | T\nT -> 1T0 | eps")
check("wrong grammar S -> 0S1 | T, T -> 1T0 | ε (nested): generates 0101 not in L, misses 0110 in L",
      W3a.generates("0101") and not L3("0101") and not W3a.generates("0110") and L3("0110")
      and all(W3a.generates("0" * n + "10" + "1" * n) and not L3("0" * n + "10" + "1" * n) for n in range(1, 6)))
W3b = CFG.parse("S -> AB\nA -> 0A1 | 01\nB -> 1B0 | 10")
check("wrong grammar A -> 0A1 | 01, B -> 1B0 | 10: misses ε, 01, 10 and every 0^n1^n",
      not any(W3b.generates(w) for w in ["", "01", "10"]) and not any(W3b.generates("0" * n + "1" * n)
                                                                       for n in range(0, 6)))
W3c = CFG.parse("S -> 0S1 | 1S0 | SS | eps")
check("wrong grammar S -> 0S1 | 1S0 | SS | ε (all strings with #0 = #1): generates 1001 and 0101, not in L",
      W3c.generates("1001") and W3c.generates("0101") and not L3("1001"))

# =============================================================================================== problem 4
print("== Problem 4: Insert1 and Delete1")


def insert1(M):
    """Q' = Q x {0,1}; s' = (s,0); A' = A x {1};
    d'((q,0),a) = {(d(q,a),0)} plus (q,1) when a = 1;  d'((q,1),a) = {(d(q,a),1)}; no ε-moves."""
    Q = [(q, f) for f in (0, 1) for q in M.states]
    delta = {}
    for q in M.states:
        for a in AB:
            delta[((q, 0), a)] = {(M.delta(q, a), 0)}
            delta[((q, 1), a)] = {(M.delta(q, a), 1)}
        delta[((q, 0), "1")].add((q, 1))
    return NFA(AB, Q, (M.start, 0), [(q, 1) for q in M.accepting], delta)


def delete1(M):
    """Q' = Q x {0,1}; s' = (s,0); A' = A x {1};
    d'((q,f),a) = {(d(q,a),f)};  d'((q,0),ε) = {(d(q,1),1)};  d'((q,1),ε) = ∅."""
    Q = [(q, f) for f in (0, 1) for q in M.states]
    delta = {}
    for q in M.states:
        for a in AB:
            delta[((q, 0), a)] = {(M.delta(q, a), 0)}
            delta[((q, 1), a)] = {(M.delta(q, a), 1)}
        delta[((q, 0), EPS)] = {(M.delta(q, "1"), 1)}
    return NFA(AB, Q, (M.start, 0), [(q, 1) for q in M.accepting], delta)


def ins_def(Lw):
    """Insert1 of a finite set of strings, straight from the definition {x1y : xy in L}."""
    return {w[:i] + "1" + w[i:] for w in Lw for i in range(len(w) + 1)}


def del_def(Lw):
    """Delete1 of a finite set, straight from the definition {xy : x1y in L}."""
    return {w[:i] + w[i + 1:] for w in Lw for i in range(len(w)) if w[i] == "1"}


N4 = 8
ALL4 = list(strings(AB, N4))


def agrees(nfa, M, kind):
    """Compare the NFA with the definition on all strings of length <= N4 (exact: Insert1(L) up to length N4
    comes from L up to N4 - 1, Delete1(L) up to N4 from L up to N4 + 1)."""
    if kind == "ins":
        truth = ins_def({w for w in strings(AB, N4 - 1) if M(w)})
    else:
        truth = {v for v in del_def({w for w in strings(AB, N4 + 1) if M(w)}) if len(v) <= N4}
    for w in ALL4:
        if nfa(w) != (w in truth):
            return w
    return None


rng = random.Random(374)


def random_dfa(n):
    sts = list(range(n))
    return DFA(AB, sts, 0, [q for q in sts if rng.random() < 0.5],
               {(q, a): rng.randrange(n) for q in sts for a in AB})


RAND4 = [random_dfa(rng.randint(2, 4)) for _ in range(300)]
bad_i = [i for i, M in enumerate(RAND4) if agrees(insert1(M), M, "ins") is not None]
bad_d = [i for i, M in enumerate(RAND4) if agrees(delete1(M), M, "del") is not None]
check(f"Insert1 construction matches the definition on 300 random DFAs (2-4 states), all |w| <= {N4}", not bad_i,
      str(bad_i[:5]))
check(f"Delete1 construction matches the definition on 300 random DFAs (2-4 states), all |w| <= {N4}", not bad_d,
      str(bad_d[:5]))


def dfa_from(table, start, acc):
    sts = sorted({q for q, _ in table} | set(table.values()))
    return DFA(AB, sts, start, acc, table)


EMPTY = dfa_from({("x", "0"): "x", ("x", "1"): "x"}, "x", [])
EPSL = dfa_from({("s", "0"): "t", ("s", "1"): "t", ("t", "0"): "t", ("t", "1"): "t"}, "s", ["s"])
ONES = dfa_from({("s", "0"): "t", ("s", "1"): "s", ("t", "0"): "t", ("t", "1"): "t"}, "s", ["s"])
ZEROS = dfa_from({("s", "0"): "s", ("s", "1"): "t", ("t", "0"): "t", ("t", "1"): "t"}, "s", ["s"])
ALLS = dfa_from({("s", "0"): "s", ("s", "1"): "s"}, "s", ["s"])
ELEVEN = dfa_from({("s", "1"): "a", ("a", "1"): "b", ("s", "0"): "t", ("a", "0"): "t", ("b", "0"): "t",
                   ("b", "1"): "t", ("t", "0"): "t", ("t", "1"): "t"}, "s", ["b"])
EDGE = [("∅", EMPTY, "∅", "∅"), ("{ε}", EPSL, "1", "∅"), ("1*", ONES, "11*", "1*"),
        ("Σ*", ALLS, "(0+1)*1(0+1)*", "(0+1)*"), ("0*", ZEROS, "0*10*", "∅")]
for name, M, ins_re, del_re in EDGE:
    check(f"edge case L = {name}: Insert1(L) = {ins_re} and Delete1(L) = {del_re} (exact)",
          same(ins_re, insert1(M))[0] and same(del_re, delete1(M))[0])
# the worked example in the figure: L = odd number of 1s
ODD1 = dfa_from({("E", "0"): "E", ("E", "1"): "O", ("O", "0"): "O", ("O", "1"): "E"}, "E", ["O"])
check("example: Insert1(odd number of 1s) = even and positive number of 1s = 0*10*1(0*10*1)*0* (exact)",
      same("0*10*1(0*10*1)*0*", insert1(ODD1))[0])
check("example: Delete1(odd number of 1s) = even number of 1s = (0*10*1)*0* (exact)",
      same("(0*10*1)*0*", delete1(ODD1))[0])
check("example: Insert1(odd number of 1s) on 0110: guess the second 1 -> path (E,0),(E,0),(O,0),(O,1),(O,1)",
      insert1(ODD1)("0110") and ("O", 1) in insert1(ODD1).delta(("O", 0), "1"))


def variant(M, kind):
    """Classic wrong constructions, to make sure each trap really changes the language."""
    Q = [(q, f) for f in (0, 1) for q in M.states]
    delta = {}
    acc = [(q, 1) for q in M.accepting]
    for q in M.states:
        for a in AB:
            delta[((q, 0), a)] = {(M.delta(q, a), 0)}
            delta[((q, 1), a)] = {(M.delta(q, a), 1)}
    if kind == "ins-accept-phase0":
        for q in M.states:
            delta[((q, 0), "1")].add((q, 1))
        acc += [(q, 0) for q in M.accepting]
    elif kind == "ins-any-symbol":
        for q in M.states:
            for a in AB:
                delta[((q, 0), a)].add((q, 1))
    elif kind == "del-no-advance":
        for q in M.states:
            delta[((q, 0), EPS)] = {(q, 1)}
    elif kind == "del-reads-the-1":
        for q in M.states:
            delta[((q, 0), "1")].add((M.delta(q, "1"), 1))
    elif kind == "del-no-flag":           # one copy of M, an ε-move feeding M a 1 from every state
        d1 = {}
        for q in M.states:
            for a in AB:
                d1[(q, a)] = {M.delta(q, a)}
            d1[(q, EPS)] = {M.delta(q, "1")}
        return NFA(AB, M.states, M.start, M.accepting, d1)
    elif kind == "ins-no-flag":           # one copy of M, a 1-loop that does not move M
        d1 = {}
        for q in M.states:
            for a in AB:
                d1[(q, a)] = {M.delta(q, a)}
            d1[(q, "1")].add(q)
        return NFA(AB, M.states, M.start, M.accepting, d1)
    return NFA(AB, Q, (M.start, 0), acc, delta)


TRAPS = [("ins-accept-phase0", EPSL, "ins", ""), ("ins-any-symbol", EPSL, "ins", "0"),
         ("del-reads-the-1", EPSL, "ins", "1"),
         ("ins-no-flag", EPSL, "ins", ""), ("del-no-advance", EPSL, "del", ""),
         ("del-reads-the-1", ONES, "del", ""), ("del-no-flag", ELEVEN, "del", "")]
for kind, M, side, wit in TRAPS:
    w = agrees(variant(M, kind), M, side)
    check(f"trap {kind}: wrong already on a small edge case, first wrong string {wit!r}", w == wit, f"got {w!r}")

check("trap languages, exactly: no-flag insertion on {ε} gives 1*; reading the 1 on 1* gives 11*; "
      "not feeding the 1 on {ε} gives {ε}; no-flag deletion on {11} gives {ε, 1, 11}",
      same("1*", variant(EPSL, "ins-no-flag"))[0] and same("11*", variant(ONES, "del-reads-the-1"))[0]
      and same("ε", variant(EPSL, "del-no-advance"))[0] and same("ε+1+11", variant(ELEVEN, "del-no-flag"))[0])
check("Delete1(Insert1({01})) = {01, 10}, which is more than {01}", del_def(ins_def({"01"})) == {"01", "10"})
check("trap: showing the inserted 1 to M (as an Insert1 construction) accepts nothing for L = {ε}",
      same("∅", variant(EPSL, "del-reads-the-1"))[0])


def contains1(M):
    return M.product(DFA(AB, ["n", "y"], "n", ["y"], {("n", "0"): "n", ("n", "1"): "y", ("y", "0"): "y",
                                                     ("y", "1"): "y"}), "and")


check("trap languages on all 300 random DFAs (exact): not feeding the 1 gives L; reading the 1 gives L ∩ (contains 1)",
      all(variant(M, "del-no-advance").to_dfa().equivalent(M)[0]
          and variant(M, "del-reads-the-1").to_dfa().equivalent(contains1(M))[0] for M in RAND4))


def inv_ok(M):
    """The invariants in 'Why it works': which pairs (q, f) the NFAs can be in after reading w."""
    I, D = insert1(M), delete1(M)
    for w in strings(AB, 6):
        exp_i = {(M.delta_star(M.start, w), 0)} | {(M.delta_star(M.start, w[:k] + w[k + 1:]), 1)
                                                   for k in range(len(w)) if w[k] == "1"}
        exp_d = {(M.delta_star(M.start, w), 0)} | {(M.delta_star(M.start, w[:k] + "1" + w[k:]), 1)
                                                   for k in range(len(w) + 1)}
        if set(I.current_states(w)) != exp_i or set(D.current_states(w)) != exp_d:
            return False
    return True


check("'why it works' invariants for both NFAs hold on 100 random DFAs, all |w| <= 6", all(inv_ok(M) for M in RAND4[:100]))
check("Delete1(Insert1(L)) ⊇ L on the 300 random languages (strings of length <= 5)",
      all({w for w in strings(AB, 5) if M(w)} <= del_def(ins_def({w for w in strings(AB, 5) if M(w)}))
          for M in RAND4))

# =============================================================================================== problem 5
print("== Problem 5: #(1,w) divisible by 3, and no 00")
M51 = DFA(AB, [0, 1, 2], 0, [0], lambda r, a: (r + (a == "1")) % 3)
T52 = {("safe", "0"): "zero", ("safe", "1"): "safe", ("zero", "0"): "dead", ("zero", "1"): "safe",
       ("dead", "0"): "dead", ("dead", "1"): "dead"}
M52 = DFA(AB, ["safe", "zero", "dead"], "safe", ["safe", "zero"], T52)
L5 = lambda w: w.count("1") % 3 == 0 and "00" not in w  # noqa: E731
check("M1 (count of 1s mod 3) is correct, and delta1*(0,w) = #(1,w) mod 3, |w| <= 14",
      all(M51.delta_star(0, w) == w.count("1") % 3 for w in strings(AB, 14))
      and first_difference(M51.accepts, lambda w: w.count("1") % 3 == 0, AB, 14) is None)


def meaning52(w):
    if "00" in w:
        return "dead"
    return "zero" if w.endswith("0") else "safe"


check("M2 (no 00) is correct and its states mean safe / zero / dead, |w| <= 14",
      all(M52.delta_star("safe", w) == meaning52(w) for w in strings(AB, 14))
      and first_difference(M52.accepts, lambda w: "00" not in w, AB, 14) is None)
P5 = M51.product(M52, "and")
check("product (intersection) accepts exactly L, |w| <= 14", first_difference(P5.accepts, L5, AB, 14) is None)
PAGE5 = {  # the transition table on the page: state -> (on 0, on 1)
    (0, "safe"): ((0, "zero"), (1, "safe")), (1, "safe"): ((1, "zero"), (2, "safe")),
    (2, "safe"): ((2, "zero"), (0, "safe")), (0, "zero"): ((0, "dead"), (1, "safe")),
    (1, "zero"): ((1, "dead"), (2, "safe")), (2, "zero"): ((2, "dead"), (0, "safe")),
    (0, "dead"): ((0, "dead"), (1, "dead")), (1, "dead"): ((1, "dead"), (2, "dead")),
    (2, "dead"): ((2, "dead"), (0, "dead")),
}
check("the page's 9-row transition table is the product's transition function",
      set(P5.states) == set(PAGE5) and all((P5.delta(q, "0"), P5.delta(q, "1")) == v for q, v in PAGE5.items()))
check("start (0, safe); accepting {(0, safe), (0, zero)}",
      P5.start == (0, "safe") and P5.accepting == {(0, "safe"), (0, "zero")})
check("all 9 product states are reachable; 1^r 00 reaches (r, dead)", len(P5.reachable()) == 9
      and all(P5.delta_star(P5.start, "1" * r + "00") == (r, "dead") for r in range(3)))
D5 = P5.distinguishable_pairs()
deads = [(r, "dead") for r in range(3)]
check("the three (r, dead) states are pairwise equivalent; every other pair is distinguishable",
      all(frozenset((p, q)) not in D5 for p in deads for q in deads if p != q)
      and all(frozenset((p, q)) in D5 for p in P5.states for q in P5.states
              if p != q and not (p in deads and q in deads)))
check("the minimal DFA for L has 7 states", len(P5.minimize().states) == 7)
F5 = ["", "1", "11", "0", "10", "110", "00"]
check("fooling-set strings reach (0,safe), (1,safe), (2,safe), (0,zero), (1,zero), (2,zero), (·,dead)",
      [P5.delta_star(P5.start, x) for x in F5][:6] == [(0, "safe"), (1, "safe"), (2, "safe"), (0, "zero"),
                                                        (1, "zero"), (2, "zero")]
      and P5.delta_star(P5.start, "00")[1] == "dead")


def page_suffix(x, y):
    """The suffix rule on the page (three cases)."""
    if y == "00":
        return "1" * ((3 - x.count("1")) % 3)
    if x.count("1") != y.count("1"):
        return "1" * ((3 - x.count("1")) % 3)
    # same count: x ends in 1 or is empty, y ends in 0
    return "0" + "1" * ((3 - x.count("1")) % 3)


ok, rows = True, []
for i, x in enumerate(F5):
    for y in F5[i + 1:]:
        a, b = (x, y)
        if a == "00":
            a, b = b, a
        if a.count("1") == b.count("1") and a.endswith("0") and not b.endswith("0"):
            a, b = b, a
        z = page_suffix(a, b)
        good = L5(a + z) and not L5(b + z)
        ok = ok and good
        rows.append(f"{a or 'ε'}/{b}:{z or 'ε'}")
check("page's suffix rule: for every pair, x z in L and y z not in L (21 pairs)", ok, "; ".join(rows))
check("examples: ε, 0, 111, 10101, 0111 in L; 1, 00, 1001, 11 not in L",
      all(L5(w) for w in ["", "0", "111", "10101", "0111"]) and not any(L5(w) for w in ["1", "00", "1001", "11"]))
check("run on 0111: (0,safe) (0,zero) (1,safe) (2,safe) (0,safe) — accept",
      P5.run("0111") == [(0, "safe"), (0, "zero"), (1, "safe"), (2, "safe"), (0, "safe")] and P5("0111"))
check("run on 1001: (0,safe) (1,safe) (1,zero) (1,dead) (2,dead) — reject",
      P5.run("1001") == [(0, "safe"), (1, "safe"), (1, "zero"), (1, "dead"), (2, "dead")] and not P5("1001"))
check("1^r reaches (r,safe) and 1^r 0 reaches (r,zero)",
      all(P5.delta_star(P5.start, "1" * r) == (r, "safe") and P5.delta_star(P5.start, "1" * r + "0") == (r, "zero")
          for r in range(3)))
check("trap: the union accepting set accepts 1, which is not in L", M51.product(M52, "or")("1") and not L5("1"))
check("safe and zero differ on the suffix 0", M52.accepts("0") and not M52.accepts("00")
      and M52.delta_star("safe", "0") == "zero" and M52.delta_star("zero", "0") == "dead")
check("both factors are minimal (3 states each)", len(M51.minimize().states) == 3 == len(M52.minimize().states))
for mode in ["or", "diff", "xor"]:
    check(f"for mode {mode} the 9-state product is already minimal", len(M51.product(M52, mode).minimize().states) == 9)
check("L2 \\ L1 and the complement of L1 ∩ L2 need only 7 states (their dead states merge too)",
      len(M51.product(M52, lambda x, y: y and not x).minimize().states) == 7
      and len(M51.product(M52, lambda x, y: not (x and y)).minimize().states) == 7)

# =============================================================================================== problem 6
print("== Problem 6: subset construction for an NFA of 0*(01)*1*")
N6 = NFA(AB, ["s", "p", "q", "t"], "s", ["t"],
         {("s", "0"): {"s"}, ("s", EPS): {"p"}, ("p", "0"): {"q"}, ("q", "1"): {"p"}, ("p", EPS): {"t"},
          ("t", "1"): {"t"}})


def f6(S):
    return "∅" if not S else "{" + ",".join(sorted(S, key="spqt".index)) + "}"


def L6(w):
    """w = 0^i (01)^j 1^k for some i, j, k >= 0 (tried exhaustively)."""
    n = len(w)
    for i in range(n + 1):
        for j in range(n // 2 + 1):
            k = n - i - 2 * j
            if k >= 0 and w == "0" * i + "01" * j + "1" * k:
                return True
    return False


check("the NFA accepts exactly 0^i (01)^j 1^k, |w| <= 12", first_difference(N6.accepts, L6, AB, 12) is None)
check("the NFA is exactly equivalent to 0*(01)*1*", same("0*(01)*1*", N6)[0])
check("epsilon-reach: s -> {s,p,t}, p -> {p,t}, q -> {q}, t -> {t}",
      [f6(N6.eps_reach({q})) for q in "spqt"] == ["{s,p,t}", "{p,t}", "{q}", "{t}"])
check("row 1 in full: delta(s,0), delta(p,0), delta(t,0) = {s}, {q}, ∅ and delta(s,1), delta(p,1), delta(t,1) = ∅, ∅, {t}",
      [f6(N6.delta(r, "0")) for r in "spt"] == ["{s}", "{q}", "∅"] and [f6(N6.delta(r, "1")) for r in "spt"] == ["∅", "∅", "{t}"])
D6, rows6 = N6.subset_construction()
PAGE6 = [  # S, eps-reach(S), accepting?, on 0, on 1 — in discovery order, as on the page
    ("{s}", "{s,p,t}", True, "{s,q}", "{t}"),
    ("{s,q}", "{s,p,q,t}", True, "{s,q}", "{p,t}"),
    ("{t}", "{t}", True, "∅", "{t}"),
    ("{p,t}", "{p,t}", True, "{q}", "{t}"),
    ("∅", "∅", False, "∅", "∅"),
    ("{q}", "{q}", False, "∅", "{p}"),
    ("{p}", "{p,t}", True, "{q}", "{t}"),
]
got6 = [(f6(S), f6(Rr), acc, f6(tr["0"]), f6(tr["1"])) for S, Rr, acc, tr in rows6]
check("incremental subset construction: the page's 7-row table, row by row, in discovery order", got6 == PAGE6,
      " | ".join(" ".join(map(str, r)) for r in got6))
check("the DFA has 7 states (of 2^4 = 16 subsets), 5 of them accepting",
      len(D6.states) == 7 and len(D6.accepting) == 5)
check("the DFA is exactly equivalent to 0*(01)*1*", same("0*(01)*1*", D6)[0])
run = D6.run("0011")
check("run on 0011: {s}, {s,q}, {s,q}, {p,t}, {t} — accept",
      [f6(S) for S in run] == ["{s}", "{s,q}", "{s,q}", "{p,t}", "{t}"] and D6("0011"))
check("run on 010: {s}, {s,q}, {p,t}, {q} — reject; run on 10 ends in ∅",
      [f6(S) for S in D6.run("010")] == ["{s}", "{s,q}", "{p,t}", "{q}"] and not D6("010")
      and f6(D6.run("10")[-1]) == "∅")
mn6 = D6.minimize()
merged = [{f6(S) for S in c} for c in mn6.states if len(c) > 1]
check("minimal DFA has 6 states: only {p} and {p,t} merge", len(mn6.states) == 6 and merged == [{"{p,t}", "{p}"}],
      str(merged))
F6 = ["", "0", "1", "01", "10", "010"]
check("representatives ε, 0, 1, 01, 10, 010 reach {s}, {s,q}, {t}, {p,t}, ∅, {q}",
      [f6(D6.delta_star(D6.start, x)) for x in F6] == ["{s}", "{s,q}", "{t}", "{p,t}", "∅", "{q}"])
PAGE6_SUFFIX = {  # the page's table of distinguishing suffixes (row string, column string) -> suffix
    ("", "0"): "101", ("", "1"): "0", ("", "01"): "0", ("", "10"): "", ("", "010"): "",
    ("0", "1"): "0", ("0", "01"): "0", ("0", "10"): "", ("0", "010"): "",
    ("1", "01"): "01", ("1", "10"): "", ("1", "010"): "",
    ("01", "10"): "", ("01", "010"): "",
    ("10", "010"): "1",
}
check("the page's suffix table distinguishes all 15 pairs (exactly one of xz, yz in L)",
      len(PAGE6_SUFFIX) == 15 and all(L6(x + z) != L6(y + z) for (x, y), z in PAGE6_SUFFIX.items()))
check("each table entry is a shortest distinguishing suffix",
      all(len(shortest_suffix(x, y, L6)) == len(z) for (x, y), z in PAGE6_SUFFIX.items()))
# traps
wrongA = DFA(AB, D6.states, D6.start, [S for S in D6.states if S & N6.accepting], D6._delta)
check("trap: accepting S when S itself meets A (no ε-reach) rejects ε, 0, 00 and 0101, all in L — wrong",
      not any(wrongA(w) for w in ["", "0", "00", "0101"]) and all(L6(w) for w in ["", "0", "00", "0101"])
      and set(wrongA.accepting) == {frozenset("t"), frozenset("pt")})


def subset_no_reach(nfa):
    """Wrong: delta'(S,a) = union of delta(p,a) over p in S only (no ε-reach), accepting by ε-reach."""
    start = frozenset({nfa.start})
    seen, order, delta = {start}, [start], {}
    i = 0
    while i < len(order):
        S = order[i]
        i += 1
        for a in AB:
            T = frozenset(r for p in S for r in nfa.delta(p, a))
            delta[(S, a)] = T
            if T not in seen:
                seen.add(T)
                order.append(T)
    return DFA(AB, order, start, [S for S in order if nfa.eps_reach(S) & nfa.accepting], delta)


wrongB = subset_no_reach(N6)
check("trap: forgetting ε-reach before reading a symbol loses 0*(01)*1*'s middle and end (rejects 1 and 01)",
      not wrongB("1") and not wrongB("01") and same("0*(01)*1*", wrongB)[1] == "1"
      and not wrongB.delta_star(wrongB.start, "1") and not wrongB.delta_star(wrongB.start, "01"))


def subset_closed(nfa):
    """The other textbooks' convention: DFA states are ε-closed sets, start = ε-reach({s})."""
    start = nfa.eps_reach({nfa.start})
    seen, order, delta = {start}, [start], {}
    i = 0
    while i < len(order):
        S = order[i]
        i += 1
        for a in AB:
            T = nfa.eps_reach(frozenset(r for p in S for r in nfa.delta(p, a)))
            delta[(S, a)] = T
            if T not in seen:
                seen.add(T)
                order.append(T)
    return DFA(AB, order, start, [S for S in order if S & nfa.accepting], delta)


def subset_full(nfa):
    """The book's formal definition with Q' = all 2^|Q| subsets (not only the reachable ones)."""
    from itertools import combinations
    sts = [frozenset(c) for k in range(len(nfa.states) + 1) for c in combinations(nfa.states, k)]
    delta = {(S, a): frozenset(r for p in nfa.eps_reach(S) for r in nfa.delta(p, a)) for S in sts for a in AB}
    return DFA(AB, sts, frozenset({nfa.start}), [S for S in sts if nfa.eps_reach(S) & nfa.accepting], delta)


FULL6 = subset_full(N6)
check("trap: tabulating all 16 subsets still gives a correct DFA for 0*(01)*1*, with 9 unreachable states",
      len(FULL6.states) == 16 and same("0*(01)*1*", FULL6)[0] and len(FULL6.reachable()) == 7)
C6 = subset_closed(N6)
check("closed-sets convention: 6 states, the same language (rows {p} and {p,t} coincide there)",
      len(C6.states) == 6 and same("0*(01)*1*", C6)[0])

check("the example memberships: 0011, 0, 1, ε in L; 010, 10 not in L",
      all(L6(w) for w in ["0011", "0", "1", ""]) and not any(L6(w) for w in ["010", "10"]))
check("rows 4 and 7 ({p,t} and {p}) are identical: both accepting, 0 -> {q}, 1 -> {t}",
      got6[3][2:] == got6[6][2:] == (True, "{q}", "{t}"))

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: {FAIL}")
sys.exit(1 if FAIL else 0)
