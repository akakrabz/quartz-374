#!/usr/bin/env python3
"""Checks for every claim on content/practice/02-regular-languages.md (Practice — Chapter 2: Regular languages).

Method: every language described in English gets (1) a brute-force predicate written from the problem statement and
(2) a small DFA built from a "what must I remember" step function; the DFA is cross-checked against the predicate on
all strings up to length 14, and then every regular expression on the page is compared with the DFA EXACTLY
(minimal-DFA equivalence). Identities between arbitrary languages are checked on truncations L ∩ Σ^{<=N}, which
concatenation and star compute exactly. The structural recursion of 2.8 is run on every ∅-free expression up to
size 6 and compared exactly with the prefix language computed from the expression's DFA."""
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from automata import DFA, Regex, strings, first_difference  # noqa: E402
from automata.regex import to_str  # noqa: E402

FAIL = []


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAIL.append(name)


AB = "01"
_cache = {}


def R(text):
    if text not in _cache:
        _cache[text] = Regex(text, alphabet=AB)
    return _cache[text]


def same(r1, r2):
    """Exact equivalence of a regular expression with another expression or a DFA: (bool, shortest witness)."""
    other = R(r2) if isinstance(r2, str) else r2
    return R(r1).equivalent(other)


def upto(rx, n):
    return {w for w in strings(AB, n) if R(rx).matches(w)}


def dfa_ok(M, pred, n=14):
    return first_difference(M.accepts, pred, AB, n) is None


def subset(r1, r2):
    """L(r1) ⊆ L(r2), exactly: r1 + r2 ≡ r2."""
    return same(f"({r1})+({r2})", r2)[0]


DEAD = "D"


def explore(start, step, accept):
    return DFA.explore(AB, start, lambda q, a: DEAD if q == DEAD else step(q, a), lambda q: q != DEAD and accept(q))


# ---------------------------------------------------------------- truncated languages (exact up to length N)
N = 7


def tr(L, n=N):
    return {w for w in L if len(w) <= n}


def cat(A, B, n=N):
    return {x + y for x in A for y in B if len(x) + len(y) <= n}


def star(L, n=N):
    S, frontier = {""}, {""}
    while frontier:
        new = {x + y for x in L for y in frontier if len(x) + len(y) <= n} - S
        S |= new
        frontier = new
    return S


def plus(L, n=N):
    return cat(L, star(L, n), n)


U2 = list(strings(AB, 2))
ALL2 = [{w for k, w in enumerate(U2) if mask >> k & 1} for mask in range(2 ** len(U2))]   # all 128 L ⊆ Σ^{<=2}
rng = random.Random(374)
U3 = list(strings(AB, 3))
RAND = [{w for w in U3 if rng.random() < 0.3} for _ in range(300)]
LANGS = ALL2 + RAND

# ---------------------------------------------------------------- 2.1 true or false
check("2.1(a) No: ∅•{ε} = ∅ ≠ {ε}", cat(set(), {""}) == set() != {""})
P = cat({"0", "01"}, {"1", "11"})
check("2.1(b) No: {0, 01}•{1, 11} = {01, 011, 0111}, three strings, since 0•11 = 01•1 = 011",
      P == {"01", "011", "0111"} and "0" + "11" == "01" + "1" == "011", str(sorted(P)))
check("2.1(c) Yes: (L*)* = L* (all 128 languages ⊆ Σ^{<=2} and 300 random ones ⊆ Σ^{<=3}, truncated at 7)",
      all(star(star(L)) == star(L) for L in LANGS))
check("2.1(c) reason: L ⊆ L* for every L", all(tr(L) <= star(L) for L in LANGS))
A0, B1 = {"0"}, {"1"}
check("2.1(d) No: A = {0}, B = {1}: 01 ∈ (A∪B)* but 01 ∉ A* ∪ B*",
      "01" in star(A0 | B1) and "01" not in star(A0) | star(B1))
check("2.1(d) only A* ∪ B* ⊆ (A∪B)* holds (random pairs)",
      all(star(A) | star(B) <= star(A | B) for A, B in zip(RAND[:150], RAND[150:])))
check("2.1(e) Yes: ∅+ = ∅•∅* = ∅•{ε} = ∅, while ∅* = {ε}", plus(set()) == cat(set(), star(set())) == set()
      and star(set()) == {""})
L01 = {"", "0"}
check("2.1(f) No: L = {ε, 0} contains ε but L•L = {ε, 0, 00} ≠ L", cat(L01, L01) == {"", "0", "00"} != L01)
check("2.1(f) what holds: ε ∈ L implies L ⊆ L•L (all test languages containing ε)",
      all(tr(L) <= cat(L, L) for L in LANGS if "" in L))

# ---------------------------------------------------------------- 2.2 reading expressions
# (a) every 0 is immediately followed by a 1
pa = lambda w: all(w[i + 1:i + 2] == "1" for i in range(len(w)) if w[i] == "0")
Da = explore("ok", lambda q, a: ("p" if a == "0" else "ok") if q == "ok" else (DEAD if a == "0" else "ok"),
             lambda q: q == "ok")
check("2.2(a) DFA for 'every 0 is immediately followed by a 1' matches its predicate (|w| <= 14)", dfa_ok(Da, pa))
check("2.2(a) (1+01)* is exactly 'every 0 is immediately followed by a 1'", same("(1+01)*", Da)[0])
check("2.2(a) ... equivalently: no 00 and does not end in 0 (|w| <= 14)",
      all(pa(w) == ("00" not in w and not w.endswith("0")) for w in strings(AB, 14)))
check("2.2(a) length <= 2: ε, 1, 01, 11", upto("(1+01)*", 2) == {"", "1", "01", "11"})
# (b) ε, or an even positive number of 1s
pb = lambda w: w == "" or (w.count("1") % 2 == 0 and w.count("1") > 0)
Db = explore((False, False, 0), lambda q, a: (True, q[1] or a == "1", q[2] ^ (a == "1")),
             lambda q: (not q[0]) or (q[1] and q[2] == 0))
check("2.2(b) DFA for 'ε or an even, positive number of 1s' matches its predicate", dfa_ok(Db, pb))
check("2.2(b) (0*10*10*)* is exactly ε plus the strings with an even, positive number of 1s",
      same("(0*10*10*)*", Db)[0])
check("2.2(b) watch out: 0, 00, 000 have an even number (zero) of 1s but do not match",
      not any(R("(0*10*10*)*").matches("0" * k) for k in range(1, 9)))
check("2.2(b) length <= 2: ε, 11", upto("(0*10*10*)*", 2) == {"", "11"})
# (c) 0^n with n != 1
pc = lambda w: set(w) <= {"0"} and len(w) != 1
Dc = explore(0, lambda q, a: min(q + 1, 2) if a == "0" else DEAD, lambda q: q != 1)
check("2.2(c) DFA for {0^n : n ≠ 1} matches its predicate", dfa_ok(Dc, pc))
check("2.2(c) (00+000)* is exactly {0^n : n ≠ 1}, and equivalent to ε+000*",
      same("(00+000)*", Dc)[0] and same("(00+000)*", "ε+000*")[0])
check("2.2(c) every n ≠ 1 is 2i + 3j", all(any(2 * i + 3 * j == n for i in range(n + 1) for j in range(n + 1))
                                           for n in range(40) if n != 1))
check("2.2(c) length <= 2: ε, 00", upto("(00+000)*", 2) == {"", "00"})
# (d) ∅ inside expressions
pd = lambda w: len(w) >= 1 and w[-1] == "1" and set(w[:-1]) <= {"0"}
Dd = explore("s", lambda q, a: ("s" if a == "0" else "t") if q == "s" else DEAD, lambda q: q == "t")
check("2.2(d) DFA for 0^k1 matches its predicate", dfa_ok(Dd, pd))
check("2.2(d) (0+∅)*1∅* ≡ 0*1 exactly; L(0+∅) = {0}, L(∅*) = {ε}",
      same("(0+∅)*1∅*", Dd)[0] and same("(0+∅)*1∅*", "0*1")[0] and same("0+∅", "0")[0] and same("∅*", "ε")[0])
check("2.2(d) length <= 2: 1, 01", upto("(0+∅)*1∅*", 2) == {"1", "01"})

# ---------------------------------------------------------------- 2.3 find the error
p3 = lambda w: all("1" in w[i + 1:] for i in range(len(w)) if w[i] == "0")
D3 = explore(False, lambda q, a: a == "0" if a == "0" else False, lambda q: not q)
check("2.3 DFA for 'every 0 is followed somewhere later by a 1' matches its predicate", dfa_ok(D3, p3))
check("2.3 the language is {ε} ∪ {strings ending in 1} (|w| <= 14)",
      all(p3(w) == (w == "" or w.endswith("1")) for w in strings(AB, 14)))
NONEMPTY = explore(0, lambda q, a: 1, lambda q: q == 1)
check("2.3 the student's (0+1)*1 is exactly L minus ε: it misses ε and nothing else",
      same("(0+1)*1", D3.product(NONEMPTY, "and"))[0] and p3("") and not R("(0+1)*1").matches(""))
check("2.3 fixes: ε+(0+1)*1 and (0*1)* are both exactly L", same("ε+(0+1)*1", D3)[0] and same("(0*1)*", D3)[0])

# ---------------------------------------------------------------- 2.4 writing expressions
# (a) contains both 00 and 11
p4a = lambda w: "00" in w and "11" in w
D4a = explore(("", False, False), lambda q, a: (a, q[1] or q[0] + a == "00", q[2] or q[0] + a == "11"),
              lambda q: q[1] and q[2])
R4a = "(0+1)*00(0+1)*11(0+1)*+(0+1)*11(0+1)*00(0+1)*"
check("2.4(a) DFA for 'contains 00 and 11' matches its predicate", dfa_ok(D4a, p4a))
check("2.4(a) the expression is exactly 'contains both 00 and 11'", same(R4a, D4a)[0])
check("2.4(a) occurrences of 00 and 11 never overlap (|w| <= 12)",
      all(not (w[i:i + 2] == "00" and w[j:j + 2] == "11" and abs(i - j) < 2)
          for w in strings(AB, 12) for i in range(len(w)) for j in range(len(w))))
check("2.4(a) checks: 0011, 1100, 10011 match; 0110, 0101, ε do not",
      all(R(R4a).matches(w) for w in ["0011", "1100", "10011"]) and
      not any(R(R4a).matches(w) for w in ["0110", "0101", ""]))


# (b) the number of 0s between any two consecutive 1s is even
def p4b(w):
    ones = [i for i, c in enumerate(w) if c == "1"]
    return all((ones[k + 1] - ones[k] - 1) % 2 == 0 for k in range(len(ones) - 1))


D4b = explore((False, 0), lambda q, a: (q[0], q[1] ^ 1) if a == "0" else (DEAD if q[0] and q[1] else (True, 0)),
              lambda q: True)
R4b = "0*+0*1((00)*1)*0*"
check("2.4(b) DFA for 'even number of 0s between consecutive 1s' matches its predicate", dfa_ok(D4b, p4b))
check("2.4(b) 0* + 0*1((00)*1)*0* is exactly that language", same(R4b, D4b)[0])
check("2.4(b) checks: ε, 000, 0110, 1001, 01001100 match; 101, 10001, 11011 do not",
      all(R(R4b).matches(w) and p4b(w) for w in ["", "000", "0110", "1001", "01001100"]) and
      not any(R(R4b).matches(w) or p4b(w) for w in ["101", "10001", "11011"]))
check("2.4(b) watch out: 0*(1(00)*)* misses 10 and every 10^(2k+1) (k <= 6), all in the language",
      all(p4b("1" + "0" * (2 * k + 1)) and not R("0*(1(00)*)*").matches("1" + "0" * (2 * k + 1)) for k in range(7)))
# (c) w_i = 0 at every position divisible by 3
p4c = lambda w: all(w[i - 1] == "0" for i in range(3, len(w) + 1, 3))
D4c = explore(0, lambda q, a: DEAD if (q == 2 and a == "1") else (q + 1) % 3, lambda q: True)
R4c = "((0+1)(0+1)0)*(ε+0+1)(ε+0+1)"
check("2.4(c) DFA for 'w_i = 0 whenever 3 divides i' matches its predicate", dfa_ok(D4c, p4c))
check("2.4(c) ((0+1)(0+1)0)*(ε+0+1)(ε+0+1) is exactly that language", same(R4c, D4c)[0])
check("2.4(c) (ε+0+1)(ε+0+1) is exactly the strings of length <= 2", upto("(ε+0+1)(ε+0+1)", 6) == set(strings(AB, 2)))
check("2.4(c) checks: ε, 11, 110, 11011 match; 111, 000001 do not",
      all(R(R4c).matches(w) and p4c(w) for w in ["", "11", "110", "11011"]) and
      not any(R(R4c).matches(w) or p4c(w) for w in ["111", "000001"]))
LEN3 = explore(0, lambda q, a: (q + 1) % 3, lambda q: q == 0)
check("2.4(c) watch out: ((0+1)(0+1)0)* alone is the language restricted to lengths divisible by 3",
      same("((0+1)(0+1)0)*", D4c.product(LEN3, "and"))[0] and p4c("1") and not R("((0+1)(0+1)0)*").matches("1"))

# ---------------------------------------------------------------- 2.5 equivalent or not
contains01 = explore(0, lambda q, a: 2 if q == 2 else (1 if a == "0" else (2 if q == 1 else 0)), lambda q: q == 2)
check("2.5(a) DFA for 'contains 01' matches its predicate", dfa_ok(contains01, lambda w: "01" in w))
check("2.5(a) equivalent: (0+1)*0(0+1)*1(0+1)* ≡ (0+1)*01(0+1)* ≡ 'contains 01'",
      same("(0+1)*0(0+1)*1(0+1)*", "(0+1)*01(0+1)*")[0] and same("(0+1)*01(0+1)*", contains01)[0])
check("2.5(a) reason: if w has a 0 before a 1, the first 1 after that 0 is immediately preceded by a 0 (|w| <= 12)",
      all(("01" in w) == any(w[i] == "0" and "1" in w[i + 1:] for i in range(len(w))) for w in strings(AB, 12)))
check("2.5(b) equivalent: 1(01)* ≡ (10)*1", same("1(01)*", "(10)*1")[0])
check("2.5(b) 1(01)^n = (10)^n1 for n <= 10, the alternating string of length 2n+1",
      all("1" + "01" * n == "10" * n + "1" for n in range(11)))
ok_c, wit_c = same("(01+10)*", "(01)*(10)*")
check("2.5(c) not equivalent; shortest witness 1001, matched only by (01+10)*",
      not ok_c and wit_c == "1001" and R("(01+10)*").matches("1001") and not R("(01)*(10)*").matches("1001"), wit_c)
check("2.5(c) L((01)*(10)*) ⊊ L((01+10)*)", subset("(01)*(10)*", "(01+10)*"))
check("2.5(c) length 4: left 0101, 0110, 1001, 1010; right 0101, 0110, 1010; lengths <= 3 agree",
      {w for w in upto("(01+10)*", 4) if len(w) == 4} == {"0101", "0110", "1001", "1010"} and
      {w for w in upto("(01)*(10)*", 4) if len(w) == 4} == {"0101", "0110", "1010"} and
      upto("(01+10)*", 3) == upto("(01)*(10)*", 3) == {"", "01", "10"})
ok_d, wit_d = same("(0+01)*", "0*(01)*")
check("2.5(d) not equivalent; shortest witness 010, matched only by (0+01)*",
      not ok_d and wit_d == "010" and R("(0+01)*").matches("010") and not R("0*(01)*").matches("010"), wit_d)
check("2.5(d) L(0*(01)*) ⊊ L((0+01)*); 010 is the only witness of length <= 3",
      subset("0*(01)*", "(0+01)*") and upto("(0+01)*", 3) - upto("0*(01)*", 3) == {"010"}
      and not (upto("0*(01)*", 3) - upto("(0+01)*", 3)))

# ---------------------------------------------------------------- 2.6 Arden's rule
X, Y, Z = "(0+10)*1*", "0(0+10)*1*+1*", "1*"
check("2.6 Z = 1* solves Z = 1Z ∪ {ε}", same(f"1({Z})+ε", Z)[0])
check("2.6 1 1* ∪ {ε} = 1*", same("11*+ε", "1*")[0])
check("2.6 Y = 0X ∪ 1* solves Y = 0X ∪ 1Z ∪ {ε} (with the solved X, Z)",
      same(f"0({X})+1({Z})+ε", Y)[0] and same(f"0({X})+1*", Y)[0])
check("2.6 X = (0+10)*1* solves X = 0X ∪ 1Y ∪ {ε}", same(f"0({X})+1({Y})+ε", X)[0])
check("2.6 X solves X = (0+10)X ∪ 1*", same(f"(0+10)({X})+1*", X)[0])
ok = True
for Xs in RAND[:200]:                                 # the substitution step, for arbitrary X (distributivity)
    lhs = cat({"0"}, Xs) | cat({"1"}, cat({"0"}, Xs) | {w for w in strings(AB, N) if set(w) <= {"1"}}) | {""}
    rhs = cat({"0", "10"}, Xs) | {w for w in strings(AB, N) if set(w) <= {"1"}}
    ok = ok and lhs == rhs
check("2.6 substitution: 0X ∪ 1(0X ∪ 1*) ∪ {ε} = (0 ∪ 10)X ∪ 1* for arbitrary X (200 random X, truncated)", ok)
# the system has exactly one solution: membership of w is decided by shorter strings (no coefficient contains ε)
SX, SY, SZ = set(), set(), set()
for w in strings(AB, 12):
    if w == "" or (w[0] == "0" and w[1:] in SX) or (w[0] == "1" and w[1:] in SY):
        SX.add(w)
    if w == "" or (w[0] == "0" and w[1:] in SX) or (w[0] == "1" and w[1:] in SZ):
        SY.add(w)
    if w == "" or (w[0] == "1" and w[1:] in SZ):
        SZ.add(w)
check("2.6 the unique solution of the system (computed length by length) equals X, Y, Z (|w| <= 12)",
      SX == upto(X, 12) and SY == upto(Y, 12) and SZ == upto(Z, 12))
no110 = explore("", lambda q, a: DEAD if q + a == "110" or (q == "11" and a == "0") else
                ("11" if (q in ("1", "11") and a == "1") else a), lambda q: True)
check("2.6 DFA for 'no substring 110' matches its predicate", dfa_ok(no110, lambda w: "110" not in w))
check("2.6(b) X = (0+10)*1* is exactly the strings with no substring 110", same(X, no110)[0])
DY = DFA(AB, no110.states, no110.delta(no110.start, "1"), no110.accepting, {(q, a): no110.delta(q, a)
                                                                            for q in no110.states for a in AB})
DZ = DFA(AB, no110.states, no110.delta_star(no110.start, "11"), no110.accepting, {(q, a): no110.delta(q, a)
                                                                                 for q in no110.states for a in AB})
check("2.6 Y = {y : 1y has no 110} and Z = {z : 11z has no 110}, exactly",
      dfa_ok(DY, lambda y: "110" not in "1" + y) and dfa_ok(DZ, lambda z: "110" not in "11" + z)
      and same(Y, DY)[0] and same(Z, DZ)[0])
check("2.6 checks: 0, 1011, 0101, 111 ∈ X; 110, 01101 ∉ X",
      all(R(X).matches(w) for w in ["0", "1011", "0101", "111"]) and not any(R(X).matches(w) for w in ["110", "01101"]))
check("2.6 (0+10)* is the strings in which every 1 is immediately followed by a 0",
      same("(0+10)*", explore("ok", lambda q, a: ("p" if a == "1" else "ok") if q == "ok" else
                              (DEAD if a == "1" else "ok"), lambda q: q == "ok"))[0])
check("2.6 coefficients 1 and 0+10 do not contain ε", not R("1").matches("") and not R("0+10").matches(""))

# ---------------------------------------------------------------- 2.7 two careful expressions
occ11 = lambda w: sum(1 for i in range(len(w) - 1) if w[i:i + 2] == "11")
D7a = explore(("", 0), lambda q, a: (a, min(2, q[1] + (q[0] == "1" and a == "1"))), lambda q: q[1] == 1)
R7a = "(0+10)*11(0+01)*"
check("2.7(a) DFA for 'exactly one occurrence of 11' matches its predicate", dfa_ok(D7a, lambda w: occ11(w) == 1))
check("2.7(a) (0+10)*11(0+01)* is exactly 'contains 11 exactly once'", same(R7a, D7a)[0])
check("2.7(a) 111 contains 11 twice", occ11("111") == 2)
check("2.7(a) (0+10)* = no 11, and empty or ending in 0; (0+01)* = no 11, and empty or starting with 0 (|w| <= 12)",
      upto("(0+10)*", 12) == {w for w in strings(AB, 12) if "11" not in w and not w.endswith("1")} and
      upto("(0+01)*", 12) == {w for w in strings(AB, 12) if "11" not in w and not w.startswith("1")})
check("2.7(a) test: of the strings of length <= 3, exactly 11, 011, 110 match, and they are the language",
      upto(R7a, 3) == {"11", "011", "110"} == {w for w in strings(AB, 3) if occ11(w) == 1})
check("2.7(a) wrong answer (0+1)*11(0+1)* matches 111 and every 1^k with k >= 3 (two or more occurrences)",
      all(R("(0+1)*11(0+1)*").matches("1" * k) and occ11("1" * k) >= 2 for k in range(3, 12)))
check("2.7(a) wrong answer (0+10)*11(0+10)*: matches 1110 (two occurrences), misses 11(01)^k (k = 1..6, one occurrence)",
      R("(0+10)*11(0+10)*").matches("1110") and occ11("1110") == 2 and
      all(occ11("11" + "01" * k) == 1 and not R("(0+10)*11(0+10)*").matches("11" + "01" * k) for k in range(1, 7)))


def p7b(w):                          # every 0 has a neighbor that is a 1
    return all((i > 0 and w[i - 1] == "1") or (i + 1 < len(w) and w[i + 1] == "1")
               for i in range(len(w)) if w[i] == "0")


def step7b(q, a):                    # q = (last symbol, last symbol is a 0 that still needs a 1 on its right)
    last, pending = q
    if pending and a == "0":
        return DEAD
    return (a, a == "0" and last != "1")


D7b = explore(("", False), step7b, lambda q: not q[1])
R7b = "ε+(ε+0)1(1+01+001)*(ε+0)"
check("2.7(b) DFA for 'every 0 has a 1 as a neighbor' matches its predicate", dfa_ok(D7b, p7b))
check("2.7(b) ε+(ε+0)1(1+01+001)*(ε+0) is exactly that language", same(R7b, D7b)[0])
IN7b = {"", "1", "01", "10", "11", "010", "011", "101", "110", "111"}
check("2.7(b) test: of the strings of length <= 3 it matches exactly ε, 1, 01, 10, 11, 010, 011, 101, 110, 111",
      upto(R7b, 3) == IN7b == {w for w in strings(AB, 3) if p7b(w)})
check("2.7(b) rejected: 0, 00, 000, 001, 100; 1001 matches, 10001 does not",
      set(strings(AB, 3)) - IN7b == {"0", "00", "000", "001", "100"} and R(R7b).matches("1001")
      and not R(R7b).matches("10001") and p7b("1001") and not p7b("10001"))
check("2.7(b) a non-empty string with no 1 is never in the language", all(not p7b("0" * k) for k in range(1, 12)))
check("2.7(b) forgetting ε loses exactly one string",
      same("(ε+0)1(1+01+001)*(ε+0)", D7b.product(NONEMPTY, "and"))[0])
check("2.7(b) allowing 00 at an end is wrong on infinitely many strings: 001^k and 1^k00 (k = 1..8) match but are out",
      all(R("ε+(ε+0+00)1(1+01+001)*(ε+0+00)").matches(s) and not p7b(s)
          for k in range(1, 9) for s in ["00" + "1" * k, "1" * k + "00"]))


# ---------------------------------------------------------------- 2.8 prefixes by structural recursion
def as_string(n):
    """The string a subtree spells if it is a concatenation of single symbols and ε (a string leaf), else None."""
    if n[0] == "sym":
        return n[1]
    if n[0] == "eps":
        return ""
    if n[0] == "cat":
        left, right = as_string(n[1]), as_string(n[2])
        if left is not None and right is not None:
            return left + right
    return None


def pre(n):
    """The page's definition, returned as expression text (pre(∅) := ∅ is the extension of part (c))."""
    w = as_string(n)
    if w is not None:                                        # string leaf: ε + w1 + w1w2 + ... + w
        return "+".join(["ε"] + [w[:j] for j in range(1, len(w) + 1)])
    k = n[0]
    if k == "empty":
        return "∅"
    if k == "union":
        return f"({pre(n[1])})+({pre(n[2])})"
    if k == "cat":
        return f"({pre(n[1])})+({to_str(n[1])})({pre(n[2])})"
    if k == "star":
        return f"({to_str(n[1])})*({pre(n[1])})"
    raise ValueError(n)


def prefix_language(rx):
    """Exact DFA for Pre(L(rx)): the DFA of rx, accepting every state from which an accepting state is reachable."""
    d = R(rx).dfa()
    back = {}
    for q in d.states:
        for a in AB:
            back.setdefault(d.delta(q, a), set()).add(q)
    good, stack = set(d.accepting), list(d.accepting)
    while stack:
        q = stack.pop()
        for p in back.get(q, ()):
            if p not in good:
                good.add(p)
                stack.append(p)
    return DFA(AB, d.states, d.start, good, {(q, a): d.delta(q, a) for q in d.states for a in AB})


def all_asts(maxsize, leaves):
    by = {1: [(x,) if x in ("eps", "empty") else ("sym", x) for x in leaves]}
    for s in range(2, maxsize + 1):
        out = [("star", t) for t in by[s - 1]]
        for k in range(1, s - 1):
            for left in by[k]:
                for right in by[s - 1 - k]:
                    out.append(("union", left, right))
                    out.append(("cat", left, right))
        by[s] = out
    return [t for s in by for t in by[s]]


for rx in ["(01)*1", "0(0+1)*1", "(0+10)*11(0+01)*", "1*0"]:   # cross-check prefix_language by brute force
    M = prefix_language(rx)
    ok = all(M.accepts(x) == any(R(rx).matches(x + y) for y in strings(AB, 6)) for x in strings(AB, 7))
    check(f"2.8 the exact prefix language of {rx} agrees with brute force (|x| <= 7, completions |y| <= 6)", ok)

FREE = all_asts(6, ["eps", "0", "1"])
bad = [to_str(t) for t in FREE if not R(pre(t)).equivalent(prefix_language(to_str(t)))[0]]
check(f"2.8(b) L(pre(R)) = Pre(L(R)) exactly for all {len(FREE)} ∅-free expression trees of size <= 6 over ε, 0, 1",
      not bad, str(bad[:5]))
MORE = ["(01)*1", "0+1(0+1)*00", "(0+100)*", "((0+10)(0+10))*(ε+1)", "(0+10)*11(0+01)*", "0*1(10*1+01*0)*10*",
        "(ε+0)1(1+01+001)*(ε+0)", "((0+1)(0+1)0)*(ε+0+1)(ε+0+1)", "(1*01*01*)*1", "(00+11)*(01+10)"]
bad = [rx for rx in MORE if not R(pre(R(rx).ast)).equivalent(prefix_language(rx))[0]]
check("2.8(b) ... and for ten larger expressions (including strings longer than one symbol)", not bad, str(bad))
pa8 = pre(R("(01)*1").ast)
check("2.8(a) pre((01)*1) = (01)*(ε+0+01) + (01)*(ε+1), equivalent to (01)*(ε+0+1) and exactly Pre(L((01)*1))",
      same(pa8, "(01)*(ε+0+01)+(01)*(ε+1)")[0] and same(pa8, "(01)*(ε+0+1)")[0]
      and R("(01)*(ε+0+1)").equivalent(prefix_language("(01)*1"))[0], pa8)
check("2.8 check: strings of length <= 3 of Pre(L((01)*1)): ε, 0, 1, 01, 010, 011",
      upto("(01)*(ε+0+1)", 3) == {"", "0", "1", "01", "010", "011"} ==
      {x for x in strings(AB, 3) if any(R("(01)*1").matches(x + y) for y in strings(AB, 5))})
check("2.8 check: those are the prefixes of length <= 3 of 1, 011, 01011; longer strings of L((01)*1) add none",
      {w[:j] for w in ["1", "011", "01011"] for j in range(min(3, len(w)) + 1)} == {"", "0", "1", "01", "010", "011"}
      and all({w[:j] for j in range(4)} <= {"", "0", "1", "01", "010", "011"}
              for w in upto("(01)*1", 13) if len(w) > 5))
check("2.8 (01)*01 ⊆ (01)*, so (01)*(ε+0+01) ≡ (01)*(ε+0)", same("(01)*(ε+0+01)", "(01)*(ε+0)")[0])
# part (c): where ∅ breaks it
for rx, wrong, right in [("0∅", "ε+0", "∅"), ("∅*", "∅", "ε")]:
    got = pre(R(rx).ast)
    check(f"2.8(c) with pre(∅) := ∅: pre({rx}) ≡ {wrong}, but Pre(L({rx})) = L({right})",
          same(got, wrong)[0] and R(right).equivalent(prefix_language(rx))[0] and not same(got, right)[0], got)
WITH = all_asts(5, ["empty", "eps", "0", "1"])
fails = [to_str(t) for t in WITH if not R(pre(t)).equivalent(prefix_language(to_str(t)))[0]]
check("2.8(c) with ∅ allowed the construction fails on some expressions (all of them use ∅)",
      bool(fails) and all("∅" in f for f in fails), f"{len(fails)} failures, e.g. {fails[:4]}")
# the language identities used in the proof, on finite languages (exact, no truncation needed)
FIN = [set(L) for L in ALL2] + [{w for w in U3 if rng.random() < 0.3} for _ in range(120)]


def Pre(L):
    return {w[:j] for w in L for j in range(len(w) + 1)}


ok_u = all(Pre(A | B) == Pre(A) | Pre(B) for A, B in zip(FIN, FIN[::-1]))
ok_c = all(Pre({x + y for x in A for y in B}) == Pre(A) | {x + p for x in A for p in Pre(B)}
           for A, B in zip(FIN, FIN[7:] + FIN[:7]) if B)
ok_s = all(tr(Pre(star(A, 10)), 7) == tr(cat(star(A), Pre(A)), 7) for A in FIN if A)
check("2.8(b) proof identities: Pre(A∪B) = Pre(A)∪Pre(B); Pre(AB) = Pre(A) ∪ A·Pre(B) when B ≠ ∅; "
      "Pre(A*) = A*·Pre(A) when A ≠ ∅", ok_u and ok_c and ok_s)
check("2.8(c) the concatenation identity fails when B = ∅ (A = {0}: Pre(A∅) = ∅ but Pre(A) = {ε, 0})",
      Pre(set()) == set() and Pre({"0"}) | {x + p for x in {"0"} for p in Pre(set())} == {"", "0"})
check("2.8(b) Lemma 2.4 is what the proof needs: every ∅-free expression of size <= 6 has a non-empty language",
      all(R(to_str(t)).dfa().accepting for t in FREE))

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: {FAIL}")
sys.exit(1 if FAIL else 0)
