#!/usr/bin/env python3
"""Checks for every concrete claim on content/1-models-of-computation/02-regular-languages.md.

Regular expressions are compared EXACTLY (minimal-DFA equivalence) with DFAs built from the intended
predicates, and those DFAs are cross-checked against the predicates by brute force. Identities between
arbitrary languages (Lemmas 2.1-2.3) are checked on truncations L ∩ Σ^{<=N}, which concatenation and star
compute exactly, for every language over a small universe and for random ones."""
import os
import random
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from automata import DFA, Regex, strings, first_difference  # noqa: E402
from automata.regex import size as rsize, to_str  # noqa: E402

FAIL = []


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAIL.append(name)


AB = "01"


def R(text):
    return Regex(text, alphabet=AB)


def same(r1, r2):
    """Exact equivalence of two regular expressions (or a regex and a DFA)."""
    other = R(r2) if isinstance(r2, str) else r2
    return R(r1).equivalent(other)


def val(w):
    return int(w, 2) if w else 0


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


SIG_N = set(strings(AB, N))
U2 = list(strings(AB, 2))                       # ε, 0, 1, 00, 01, 10, 11
ALL2 = [{w for k, w in enumerate(U2) if mask >> k & 1} for mask in range(2 ** len(U2))]   # all 128 languages ⊆ Σ^{<=2}
rng = random.Random(374)
U3 = list(strings(AB, 3))
RAND = [{w for w in U3 if rng.random() < 0.3} for _ in range(400)]

# ---------------------------------------------------------------- 2.1 the three empty things
check("∅•L = ∅ and {ε}•L = L (all 128 languages L ⊆ Σ^{<=2})",
      all(cat(set(), L) == set() == cat(L, set()) and cat({""}, L) == tr(L) == cat(L, {""}) for L in ALL2))
check("∅* = {ε}* = {ε}", star(set()) == {""} == star({""}))
check("as expressions: ∅* ≡ ε ≡ ε*, ∅(0+1)* ≡ ∅, ε(0+11)* ≡ (0+11)*",
      same("∅*", "ε")[0] and same("ε*", "ε")[0] and same("∅(0+1)*", "∅")[0] and same("ε(0+11)*", "(0+11)*")[0])
check("∅ and {ε} differ: ε matches ε but not ∅", R("ε").matches("") and not R("∅").matches(""))

# ---------------------------------------------------------------- 2.2 building languages
A_ = {"HOCUS", "ABRACA"}
B_ = {"POCUS", "DABRA"}
AB_ = {x + y for x in A_ for y in B_}
check("{HOCUS, ABRACA}•{POCUS, DABRA} = {HOCUSPOCUS, HOCUSDABRA, ABRACAPOCUS, ABRACADABRA}",
      AB_ == {"HOCUSPOCUS", "HOCUSDABRA", "ABRACAPOCUS", "ABRACADABRA"}, str(sorted(AB_)))
check("{0, 00}•{0, 00} = {00, 000, 0000}: only 3 strings, not 4", cat({"0", "00"}, {"0", "00"}) == {"00", "000", "0000"})
check("{0, 11}* starts ε, 0, 00, 11, 000, 011, 110 (all its strings of length <= 3)",
      star({"0", "11"}, 3) == {"", "0", "00", "11", "000", "011", "110"}, str(sorted(star({"0", "11"}, 3), key=len)))
check("L* is infinite for every L other than ∅ and {ε} (L ⊆ Σ^{<=2}: L* has strings of length >= 7 among those <= 8)",
      all((L in (set(), {""})) == (max(map(len, star(L, 8))) < 7) for L in ALL2))
check("Σ* is the star of Σ: (0+1)* matches every string (|w| <= 12)",
      first_difference(R("(0+1)*").matches, lambda w: True, AB, 12) is None)
check("L+ = L•L* consists of concatenations of one or more strings of L: {0,11}+ up to length 3",
      plus({"0", "11"}, 3) == {"0", "00", "11", "000", "011", "110"})

TRIPLES = [(rng.choice(RAND), rng.choice(RAND), rng.choice(RAND)) for _ in range(600)]
TRIPLES += [(A, B, C) for A in (set(), {""}, {"0"}, {"", "1"}) for B in (set(), {""}, {"01", "1"}) for C in ({""}, {"0", "11"})]
ok = all(A | B == B | A and (A | B) | C == A | (B | C) for A, B, C in TRIPLES)
check("Lemma 2.1(a,b): ∪ is commutative and associative", ok)
ok = all(cat(set(), A) == cat(A, set()) == set() and cat({""}, A) == cat(A, {""}) == tr(A) for A, B, C in TRIPLES)
check("Lemma 2.1(c,d): ∅ annihilates and {ε} is the identity for concatenation", ok)
ok = all(cat(cat(A, B), C) == cat(A, cat(B, C)) for A, B, C in TRIPLES)
check("Lemma 2.1(e): (A•B)•C = A•(B•C) (600+ triples, truncated at length 7)", ok)
ok = all(cat(A, B | C) == cat(A, B) | cat(A, C) and cat(A | B, C) == cat(A, C) | cat(B, C) for A, B, C in TRIPLES)
check("Lemma 2.1(f,g): concatenation distributes over ∪ on both sides", ok)
check("(0+1)*(0+1)* ≡ (0+1)* (Lemma 2.2(a): L*L* = L*)", same("(0+1)*(0+1)*", "(0+1)*")[0])
check("{HOCUS, ABRACA}•{POCUS, DABRA} has |A|·|B| = 4 strings", len(AB_) == len(A_) * len(B_) == 4)
check("concatenation is not commutative: {0}•{1} ≠ {1}•{0}", cat({"0"}, {"1"}) != cat({"1"}, {"0"}))
check("concatenation does not distribute over ∩: A = {ε, 0}, B = {0}, C = {00} gives A(B∩C) = ∅ ≠ AB∩AC = {00}",
      cat({"", "0"}, {"0"} & {"00"}) == set() and cat({"", "0"}, {"0"}) & cat({"", "0"}, {"00"}) == {"00"})

check("A(B ∩ C) ⊆ AB ∩ AC for all 600+ triples (the inclusion that does hold)",
      all(cat(A, B & C) <= cat(A, B) & cat(A, C) for A, B, C in TRIPLES))
LANGS = ALL2 + RAND[:150]
ok_a = ok_b = ok_c = True
for L in LANGS:
    S, P = star(L), plus(L)
    e = {""}
    ok_a = ok_a and S == e | P == cat(S, S) == star(L | e) == star(L - e) == e | tr(L) | cat(P, P)
    ok_b = ok_b and P == cat(L, S) == cat(S, L) == cat(P, S) == cat(S, P) == tr(L) | cat(P, P)
    ok_c = ok_c and ((P == S) == ("" in L))
check("Lemma 2.2(a): L* = {ε} ∪ L+ = L*L* = (L ∪ {ε})* = (L \\ {ε})* = {ε} ∪ L ∪ L+L+ (278 languages)", ok_a)
check("Lemma 2.2(b): L+ = LL* = L*L = L+L* = L*L+ = L ∪ L+L+", ok_b)
check("Lemma 2.2(c): L+ = L* iff ε ∈ L", ok_c)
check("ε ∈ L+ iff ε ∈ L (278 languages)", all(("" in plus(L)) == ("" in L) for L in LANGS))
check("for L = {0}: L+ is 00* and L* is 0* (up to length 7)",
      plus({"0"}) == {w for w in SIG_N if R("00*").matches(w)} and star({"0"}) == {w for w in SIG_N if R("0*").matches(w)})
check("Arden step 1 distributed: 0*(1L_s ∪ {ε}) = 0*1L_s ∪ 0* (with L_s = (0+10*1)*10*)",
      same("0*(1(0+10*1)*10*+ε)", "0*1(0+10*1)*10*+0*")[0])
check("Arden step 2: 0L_s ∪ 1L_t = 0L_s ∪ 10*1L_s ∪ 10* (with the solved L_s, L_t)",
      same("0(0+10*1)*10*+1(0*(1(0+10*1)*10*+ε))", "0(0+10*1)*10*+10*1(0+10*1)*10*+10*")[0]
      and same("0(0+10*1)*10*+10*1(0+10*1)*10*+10*", "(0+10*1)*10*")[0])


def arden_unique(A, B, n=N):
    """The unique L ⊆ Σ^{<=n} with L = AL ∪ B when ε ∉ A, decided by length (shortest first)."""
    L = set()
    for w in strings(AB, n):
        if w in B or any(x and w.startswith(x) and w[len(x):] in L for x in A):
            L.add(w)
    return L


ok1 = ok2 = True
for A, B, _ in TRIPLES[:400]:
    AsB = cat(star(A), B)
    ok1 = ok1 and cat(A, AsB) | tr(B) == AsB                      # A*B solves the equation (any A)
    if "" not in A:
        ok2 = ok2 and arden_unique(A, B) == AsB                    # and is the only solution when ε ∉ A
check("Lemma 2.3 (Arden): A*B always satisfies L = AL ∪ B (400 pairs A, B)", ok1)
check("Lemma 2.3 (Arden): if ε ∉ A, the only solution is A*B (pairs with ε ∉ A)", ok2)
check("Arden example: L = 0L ∪ {1} forces L = 0*1 (unique solution, |w| <= 12)",
      first_difference(lambda w: w in arden_unique({"0"}, {"1"}, 12), R("0*1").matches, AB, 12) is None)
check("... and 0*1 satisfies it exactly: 0(0*1) + 1 ≡ 0*1", same("0(0*1)+1", "0*1")[0])
check("with ε ∈ A the solution is not unique: for A = {ε, 0}, B = {1} both 0*1 and Σ* solve L = AL ∪ B",
      same("(ε+0)0*1+1", "0*1")[0] and same("(ε+0)(0+1)*+1", "(0+1)*")[0] and not same("0*1", "(0+1)*")[0])
check("A*B for A = ε+0, B = 1 is (ε+0)*1 ≡ 0*1, the smallest solution", same("(ε+0)*1", "0*1")[0])

# Arden on the odd-number-of-1s DFA of §3.3 (states s, t; accept t)
P = DFA(AB, "st", "s", ["t"], {("s", "0"): "s", ("s", "1"): "t", ("t", "0"): "t", ("t", "1"): "s"})
odd1 = lambda w: w.count("1") % 2 == 1
even1 = lambda w: w.count("1") % 2 == 0
check("L_s := {w : δ*(s,w) ∈ A} is 'odd number of 1s' and L_t is 'even number of 1s' (|w| <= 12)",
      all((P.delta_star("s", w) == "t") == odd1(w) and (P.delta_star("t", w) == "t") == even1(w)
          for w in strings(AB, 12)))
check("equations: L_s = 0L_s ∪ 1L_t and L_t = 0L_t ∪ 1L_s ∪ {ε} (|w| <= 12)",
      all(odd1(w) == ((w[:1] == "0" and odd1(w[1:])) or (w[:1] == "1" and even1(w[1:]))) and
          even1(w) == (w == "" or (w[:1] == "0" and even1(w[1:])) or (w[:1] == "1" and odd1(w[1:])))
          for w in strings(AB, 12)))
check("solution: L_s = (0+10*1)*10* exactly", same("(0+10*1)*10*", P)[0])
check("and L_t = 0*(1L_s ∪ {ε}) = 0*(1(0+10*1)*10*+ε) is exactly 'even number of 1s'",
      same("0*(1(0+10*1)*10*+ε)", P.complement())[0])
check("intermediate step: L_s = (0+10*1)L_s ∪ 10* has the solution (0+10*1)*10* (substitute and compare)",
      same("(0+10*1)(0+10*1)*10*+10*", "(0+10*1)*10*")[0])
E0 = DFA.explore(AB, 0, lambda q, a: q ^ (a == "0"), lambda q: q == 0)
check("the same method on the even-0s DFA gives (1+01*0)*, equivalent to the table's 1*(01*01*)*",
      same("(1+01*0)*", E0)[0] and same("(1+01*0)*", "1*(01*01*)*")[0])

# ---------------------------------------------------------------- 2.3 the table of examples (exact)
def dead_or(f):
    return lambda q, a: "D" if q == "D" else f(q, a)


TABLE = [
    ("0*", DFA.explore(AB, 0, dead_or(lambda q, a: 0 if a == "0" else "D"), lambda q: q == 0),
     lambda w: set(w) <= {"0"}),
    ("00000*", DFA.explore(AB, 0, dead_or(lambda q, a: min(q + 1, 4) if a == "0" else "D"), lambda q: q == 4),
     lambda w: set(w) <= {"0"} and len(w) >= 4),
    ("(00000)*", DFA.explore(AB, 0, dead_or(lambda q, a: (q + 1) % 5 if a == "0" else "D"), lambda q: q == 0),
     lambda w: set(w) <= {"0"} and len(w) % 5 == 0),
    ("(0+1)*", DFA.explore(AB, 0, lambda q, a: 0, lambda q: True), lambda w: True),
    ("(ε+1)(01)*(ε+0)", DFA.explore(AB, "", dead_or(lambda q, a: "D" if q == a else a), lambda q: q != "D"),
     lambda w: "00" not in w and "11" not in w),
    ("(0+1)*0000(0+1)*", DFA.explore(AB, 0, lambda q, a: 4 if q == 4 else (q + 1 if a == "0" else 0), lambda q: q == 4),
     lambda w: "0000" in w),
    ("((ε+0+00+000)1)*(ε+0+00+000)",
     DFA.explore(AB, 0, lambda q, a: 4 if q == 4 else (q + 1 if a == "0" else 0), lambda q: q != 4),
     lambda w: "0000" not in w),
    ("((0+1)(0+1))*", DFA.explore(AB, 0, lambda q, a: 1 - q, lambda q: q == 0), lambda w: len(w) % 2 == 0),
    ("1*(01*01*)*", DFA.explore(AB, 0, lambda q, a: q ^ (a == "0"), lambda q: q == 0), lambda w: w.count("0") % 2 == 0),
    ("0+1(0+1)*00",
     DFA.explore(AB, "s", lambda q, a: ("z" if a == "0" else ("n", 1)) if q == "s" else
                 ("D" if q in ("z", "D") else ("n", (2 * q[1] + int(a)) % 4)), lambda q: q == "z" or q == ("n", 0)),
     lambda w: w != "" and (w == "0" or w[0] == "1") and val(w) % 4 == 0),
    ("0*0+0*1(10*1+01*0)*10*",
     DFA.explore(AB, "e", lambda q, a: ((0 if q == "e" else q) * 2 + int(a)) % 3, lambda q: q == 0),
     lambda w: w != "" and val(w) % 3 == 0),
]
for rx, M, pred in TABLE:
    d = first_difference(M.accepts, pred, AB, 14)
    ok, wit = same(rx, M)
    check(f"table: {rx} matches exactly its described language", d is None and ok, f"dfa/pred diff {d!r}, regex witness {wit!r}")
check("table: 0+1(0+1)*00 matches 0, 100, 1000, 1100 and not 00, 0100, 10, ε",
      all(R("0+1(0+1)*00").matches(w) for w in ["0", "100", "1000", "1100"]) and
      not any(R("0+1(0+1)*00").matches(w) for w in ["00", "0100", "10", ""]))
check("table: the multiples-of-3 expression does not match ε but matches 0, 11, 0110, 1001",
      not R("0*0+0*1(10*1+01*0)*10*").matches("") and
      all(R("0*0+0*1(10*1+01*0)*10*").matches(w) for w in ["0", "11", "0110", "1001"]))
# Chapter 4 (book §4.8) derives this expression by state elimination from a DFA with a separate start state s
M3s = DFA(AB, ["s", 0, 1, 2], "s", [0],
          {**{("s", a): int(a) for a in AB}, **{(q, a): (2 * q + int(a)) % 3 for q in range(3) for a in AB}})
M3 = DFA(AB, [0, 1, 2], 0, [0], lambda q, a: (2 * q + int(a)) % 3)
check("multiples of 3: the expression is exactly the 4-state DFA (start s, non-accepting, plus remainder states 0, 1, 2), "
      "and the book's unsimplified 00*+(00*1+1)(10*1+01*0)*10* is equivalent",
      same("0*0+0*1(10*1+01*0)*10*", M3s)[0] and len(M3s.minimize().states) == 4
      and same("00*+(00*1+1)(10*1+01*0)*10*", "0*0+0*1(10*1+01*0)*10*")[0])
check("... while the three remainder states alone (start 0) also accept ε: their language is ε + the expression",
      M3.accepts("") and not same("0*0+0*1(10*1+01*0)*10*", M3)[0] and same("ε+0*0+0*1(10*1+01*0)*10*", M3)[0])

# precedence
check("reading 0+1(0+1)*00 as {0} ∪ ({1}•{0,1}*•{00})", same("0+1(0+1)*00", "0+(1((0+1)*)(00))")[0])
check("10* = {1, 10, 100, ...} and (10)* = {ε, 10, 1010, ...} (all strings of length <= 4)",
      {w for w in strings(AB, 4) if R("10*").matches(w)} == {"1", "10", "100", "1000"} and
      {w for w in strings(AB, 4) if R("(10)*").matches(w)} == {"", "10", "1010"})
check("precedence: 10* ≢ (10)* (ε matches only the second), and 10* ≡ 1(0*)",
      same("10*", "(10)*") == (False, "") and same("10*", "1(0*)")[0])
check("precedence: 0+10 ≡ 0+(10) and 0+10 ≢ (0+1)0", same("0+10", "0+(10)")[0] and not same("0+10", "(0+1)0")[0])
check("precedence: 00000* ≢ (00000)*; 00000* means 0000(0*)", not same("00000*", "(00000)*")[0] and same("00000*", "0000(0*)")[0])
check("precedence: 0+1* is {0} ∪ 1*, not (0+1)*", same("0+1*", "0+(1*)")[0] and not same("0+1*", "(0+1)*")[0])
for e in ["(1+0)*", "(0*1*)*", "(00+01+10+11)*(0+1+ε)"]:
    check(f"{e} ≡ (0+1)*", same(e, "(0+1)*")[0])
check("(00+01+10+11)* alone is only the even-length strings", same("(00+01+10+11)*", "((0+1)(0+1))*")[0]
      and not same("(00+01+10+11)*", "(0+1)*")[0])

# ---------------------------------------------------------------- designing regular expressions (worked examples)
def every1_00(w):
    return all(w[i + 1:i + 3] == "00" for i in range(len(w)) if w[i] == "1")


def step1(q, a):                                  # 0: fine; 1: owe 00; 2: owe 0; D: dead
    if q == "D":
        return "D"
    if q == 0:
        return 0 if a == "0" else 1
    return (2 if q == 1 else 0) if a == "0" else "D"


M1 = DFA.explore(AB, 0, step1, lambda q: q == 0)
check("example 1: the DFA for 'every 1 is immediately followed by 00' is right (|w| <= 14)",
      first_difference(M1.accepts, every1_00, AB, 14) is None)
check("example 1: (0+100)* is exactly 'every 1 is immediately followed by 00'", same("(0+100)*", M1)[0])
IN1, OUT1 = ["", "0", "100", "1000", "0100100"], ["1", "10", "11", "1001"]
check("example 1 lists: ε, 0, 100, 1000, 0100100 in; 1, 10, 11, 1001 out (predicate and expression agree)",
      all(every1_00(w) and R("(0+100)*").matches(w) for w in IN1) and
      not any(every1_00(w) or R("(0+100)*").matches(w) for w in OUT1))
def decompositions(w, blocks):
    """Number of ways to write w as a concatenation of blocks."""
    ways = [1] + [0] * len(w)
    for k in range(1, len(w) + 1):
        ways[k] = sum(ways[k - len(b)] for b in blocks if len(b) <= k and w[k - len(b):k] == b)
    return ways[len(w)]


check("example 1: every string of the language splits into blocks 0 and 100 in exactly one way (|w| <= 14)",
      all(decompositions(w, ["0", "100"]) == (1 if every1_00(w) else 0) for w in strings(AB, 14)))
check("example 1: the block decomposition in the figure, 0|100|0|100|100|0",
      "".join(["0", "100", "0", "100", "100", "0"]) == "010001001000" and every1_00("010001001000"))
ok, wit = same("(0*100)*", M1)
check("example 1, wrong answer (0*100)* misses 0, 00 and 1000 (strings ending in 0s after the last block)",
      all(every1_00(w) and not R("(0*100)*").matches(w) for w in ["0", "00", "1000"]))
check("example 1: (0*100)* is exactly ε plus the strings of the language that end in 100",
      same("(0*100)*", "ε+(0+100)*100")[0])
check("example 1, wrong answer (0*100)*: misses 0, and in fact every 0^n with n >= 1",
      not ok and wit == "0" and all(every1_00("0" * n) and not R("(0*100)*").matches("0" * n) for n in range(1, 13)), wit)


def even0_no11(w):
    return w.count("0") % 2 == 0 and "11" not in w


M2 = DFA.explore(AB, (0, False), lambda q, a: "D" if q == "D" or (q[1] and a == "1") else
                 ((q[0] ^ (a == "0")), a == "1"), lambda q: q != "D" and q[0] == 0)
check("example 2: the DFA for 'even number of 0s and no 11' is right (|w| <= 14)",
      first_difference(M2.accepts, even0_no11, AB, 14) is None)
check("example 2: ((0+10)(0+10))*(ε+1) is exactly 'even number of 0s and no substring 11'",
      same("((0+10)(0+10))*(ε+1)", M2)[0])
check("example 2: a string has no 11 iff it is in (0+10)*(ε+1)", same("(0+10)*(ε+1)",
      DFA.explore(AB, "", dead_or(lambda q, a: "D" if q == "1" and a == "1" else a), lambda q: q != "D"))[0])
check("example 2: in every string without 11, every 1 except a final one is followed by 0 (|w| <= 14)",
      all(all(w[i + 1] == "0" for i in range(len(w) - 1) if w[i] == "1") for w in strings(AB, 14) if "11" not in w))
check("example 2: each block 0 or 10 holds exactly one 0", all(b.count("0") == 1 for b in ["0", "10"]))
IN2, OUT2 = ["", "1", "00", "010", "1001"], ["0", "11", "101", "0110"]
check("example 2 lists: ε, 1, 00, 010, 1001 in; 0, 11, 101, 0110 out (predicate and expression agree)",
      all(even0_no11(w) and R("((0+10)(0+10))*(ε+1)").matches(w) for w in IN2) and
      not any(even0_no11(w) or R("((0+10)(0+10))*(ε+1)").matches(w) for w in OUT2))
check("example 2: the figure's string 10|0|0|10|1 is in the language", even0_no11("100010" + "1")
      and "".join(["10", "0", "0", "10", "1"]) == "1000101")
ok, wit = same("((0+10)(0+10))*", M2)
check("example 2, wrong answer without (ε+1): misses 1, and every 0^(2k)1",
      not ok and wit == "1" and all(even0_no11("0" * (2 * k) + "1") and not R("((0+10)(0+10))*").matches("0" * (2 * k) + "1")
                                    for k in range(7)), wit)
ok, wit = same("(0+10)*(ε+1)", M2)
check("example 2, wrong answer (0+10)*(ε+1) ignores the parity: accepts 0, 000, 00000, ...",
      not ok and wit == "0" and all(R("(0+10)*(ε+1)").matches("0" * (2 * k + 1)) for k in range(7)), wit)

check("true/false: ∅* = ∅ is false; L+ = L* fails for L = {0}; (10)* and 10* are not equivalent",
      star(set()) != set() and plus({"0"}) != star({"0"}) and not same("(10)*", "10*")[0])

L_0n1n = lambda w: len(w) % 2 == 0 and w == "0" * (len(w) // 2) + "1" * (len(w) // 2)
check("a subset of a regular language need not be regular: {0^n1^n} ⊆ L((0+1)*), and 0* is a fooling set for it "
      "(x = 0^i, y = 0^j, z = 1^i: xz in, yz out, for all i ≠ j <= 10)",
      all(R("(0+1)*").matches("0" * n + "1" * n) for n in range(8)) and
      all(L_0n1n("0" * i + "1" * i) and not L_0n1n("0" * j + "1" * i) for i in range(11) for j in range(11) if i != j))
check("regex shorthands: a+ = aa*, a? = ε+a, a{2,3} = aa(a+ε) (as in programming regexen)",
      all(bool(re.fullmatch("0+", w)) == R("00*").matches(w) and bool(re.fullmatch("0?", w)) == R("ε+0").matches(w)
          and bool(re.fullmatch("0{2,3}", w)) == R("00(0+ε)").matches(w) for w in strings(AB, 8)))

# ---------------------------------------------------------------- 2.4 regexen (back-references)
is_square = lambda w: len(w) % 2 == 0 and w[:len(w) // 2] == w[len(w) // 2:]
check("in a programming regex, 0+1 means one or more 0s then 1 (= 00*1), union is 0|1, and [01] is 0+1",
      all(bool(re.fullmatch("0+1", w)) == R("00*1").matches(w) and bool(re.fullmatch("0|1", w)) == R("0+1").matches(w)
          and bool(re.fullmatch("[01]", w)) == R("0+1").matches(w) for w in strings(AB, 8)))
check("the regex (.*)\\1 (back-reference) matches exactly the squares ww (|w| <= 12)",
      all(bool(re.fullmatch(r"(.*)\1", w)) == is_square(w) for w in strings(AB, 12)))
check("{ww} is not regular: F = 0*1, x = 0^i1, y = 0^j1, z = 0^i1 (i ≠ j <= 10)",
      all(is_square("0" * i + "1" + "0" * i + "1") and not is_square("0" * j + "1" + "0" * i + "1")
          for i in range(11) for j in range(11) if i != j))

# ---------------------------------------------------------------- 2.5 expression trees
check("size of 0+1(0+1)*00 is 10 (its string has 11 characters)", rsize(R("0+1(0+1)*00").ast) == 10
      and len("0+1(0+1)*00") == 11)
check("book: size of 0*0+0*1(10*1+01*0)*10* is 29, its length 22",
      rsize(R("0*0+0*1(10*1+01*0)*10*").ast) == 29 and len("0*0+0*1(10*1+01*0)*10*") == 22)

# the figure's tree (same as tools/figs_ch02.py)
SUB = ("•", [("*", [("+", [("0", []), ("1", [])])]), ("00", [])])
TREE = ("+", [("0", []), ("•", [("1", []), SUB])])


def nodes(t):
    return [t] + [m for k in t[1] for m in nodes(k)]


def tree_text(t):
    lab, kids = t
    if not kids:
        return lab
    if lab == "*":
        return "(" + tree_text(kids[0]) + ")*"
    return "(" + tree_text(kids[0]) + (")+(" if lab == "+" else ")(") + tree_text(kids[1]) + ")"


check("figure tree has 10 nodes: internal + • • * +, leaves 0 1 0 1 00",
      len(nodes(TREE)) == 10 and [n[0] for n in nodes(TREE) if n[1]] == ["+", "•", "•", "*", "+"]
      and [n[0] for n in nodes(TREE) if not n[1]] == ["0", "1", "0", "1", "00"])
check("figure tree denotes 0+1(0+1)*00", same(tree_text(TREE), "0+1(0+1)*00")[0], tree_text(TREE))
check("highlighted subtree denotes (0+1)*00", same(tree_text(SUB), "(0+1)*00")[0])


def factors(n, kind):
    return factors(n[1], kind) + factors(n[2], kind) if n[0] == kind else [n]


def canon(n):
    """Library AST -> book tree pieces: unions/concatenations as flat lists, runs of symbols as one string leaf."""
    k = n[0]
    if k == "sym":
        return ("str", n[1])
    if k in ("eps", "empty"):
        return (k,)
    if k == "star":
        return ("star", canon(n[1]))
    if k == "union":
        return ("union", [canon(f) for f in factors(n, "union")])
    out = []
    for f in factors(n, "cat"):
        c = canon(f)
        if c[0] == "str" and out and out[-1][0] == "str":
            out[-1] = ("str", out[-1][1] + c[1])
        else:
            out.append(c)
    return out[0] if len(out) == 1 else ("cat", out)


def show(t, ctx=0):
    """Minimal parentheses: ctx 0 = top/union operand, 1 = concatenation operand, 2 = star operand."""
    k = t[0]
    if k == "str":
        return t[1] if (ctx < 2 or len(t[1]) == 1) else "(" + t[1] + ")"
    if k == "eps":
        return "ε"
    if k == "empty":
        return "∅"
    if k == "star":
        return show(t[1], 2) + "*"
    if k == "cat2":
        s = show(t[1], 1) + show(t[2], 1)
        return "(" + s + ")" if ctx == 2 else s
    s = show(t[1], 0) + "+" + show(t[2], 0)
    return "(" + s + ")" if ctx >= 1 else s


def trees(t):
    """All binary expression trees for t (every bracketing of every union and concatenation)."""
    k = t[0]
    if k in ("str", "eps", "empty"):
        return [t]
    if k == "star":
        return [("star", s) for s in trees(t[1])]
    items = t[1]
    op = "cat2" if k == "cat" else "union2"

    def br(lo, hi):
        if hi - lo == 1:
            return trees(items[lo])
        return [(op, l, r) for m in range(lo + 1, hi) for l in br(lo, m) for r in br(m, hi)]
    return br(0, len(items))


def subexpressions(text):
    out = set()

    def walk(x):
        out.add(show(x))
        for c in x[1:]:
            if isinstance(c, tuple):
                walk(c)
    for tt in trees(canon(R(text).ast)):
        walk(tt)
    return out


SE = subexpressions("0+1(0+1)*00")
check("subexpressions of 0+1(0+1)*00 include (0+1)*00, 1(0+1)*, (0+1)* and 0+1",
      {"(0+1)*00", "1(0+1)*", "(0+1)*", "0+1", "00"} <= SE, str(sorted(SE)))
check("... but not the well-formed substring 0+1(0+1)* (no subtree spells it)", "0+1(0+1)*" not in SE)
check("the two groupings 1•((0+1)*00) and (1(0+1)*)•00 are both trees of 1(0+1)*00",
      {"(0+1)*00", "1(0+1)*"} <= subexpressions("1(0+1)*00"))
check("0+1(0+1)* is a substring of 0+1(0+1)*00 and a well-formed expression",
      "0+1(0+1)*" in "0+1(0+1)*00" and R("0+1(0+1)*") is not None)
SE29 = subexpressions("0*0+0*1(10*1+01*0)*10*")
check("book: 10*1 is a subexpression of 0*0+0*1(10*1+01*0)*10*; 0*0+0*1 and 0*1+01*0 are not",
      "10*1" in SE29 and "0*0+0*1" not in SE29 and "0*1+01*0" not in SE29)
check("every subexpression of 0+1(0+1)*00 (and of the book's 29-node example) is a substring of it",
      all(x in "0+1(0+1)*00" for x in SE) and all(x in "0*0+0*1(10*1+01*0)*10*" for x in SE29))

# ---------------------------------------------------------------- 2.6 / 2.7 Lemmas 2.4 and 2.5 by exhaustive search
def all_asts(maxsize, leaves):
    by = {1: [(x,) if x in ("eps", "empty") else ("sym", x) for x in leaves]}
    for s in range(2, maxsize + 1):
        out = [("star", t) for t in by[s - 1]]
        for k in range(1, s - 1):
            for l in by[k]:
                for r in by[s - 1 - k]:
                    out.append(("union", l, r))
                    out.append(("cat", l, r))
        by[s] = out
    return [t for s in by for t in by[s]]


def empty_lang(text):
    return not R(text).dfa().accepting


free = all_asts(6, ["eps", "0", "1"])
check(f"Lemma 2.4: all {len(free)} ∅-free expressions of size <= 6 over ε, 0, 1 denote non-empty languages",
      all(not empty_lang(to_str(t)) for t in free))
check("the converse fails: ∅* and 0+∅ use ∅ but are not empty", not empty_lang("∅*") and not empty_lang("0+∅"))
check("Lemma 2.5 proof: an expression with a non-empty language (0+∅) can have a subexpression (∅) with an empty one",
      not empty_lang("0+∅") and empty_lang("∅"))
check("Lemma 2.4 proof, star case: ε matches S* for every S (sizes <= 5)",
      all(R(to_str(("star", t))).matches("") for t in all_asts(5, ["empty", "eps", "0", "1"])))


def phi_free(n):
    """The construction in the proof of Lemma 2.5: None if L(n) = ∅, else an equivalent ∅-free expression."""
    k = n[0]
    if k == "empty":
        return None
    if k in ("eps", "sym"):
        return n
    if k == "star":
        s = phi_free(n[1])
        return ("eps",) if s is None else ("star", s)
    l, r = phi_free(n[1]), phi_free(n[2])
    if k == "union":
        return r if l is None else (l if r is None else ("union", l, r))
    return None if (l is None or r is None) else ("cat", l, r)


withempty = all_asts(5, ["empty", "eps", "0", "1"])
ok = True
for t in withempty:
    p = phi_free(t)
    if p is None:
        ok = ok and empty_lang(to_str(t))
    else:
        ok = ok and "∅" not in to_str(p) and same(to_str(t), to_str(p))[0]
check(f"Lemma 2.5: the proof's construction works on all {len(withempty)} expressions of size <= 5 over ∅, ε, 0, 1", ok)
check("Lemma 2.5 examples: ∅* becomes ε, (0+∅)1 becomes 01, 0∅ + 1* becomes 1*",
      to_str(phi_free(R("∅*").ast)) == "ε" and same(to_str(phi_free(R("(0+∅)1").ast)), "01")[0]
      and to_str(phi_free(R("0∅+1*").ast)) == "1*")

# ---------------------------------------------------------------- 2.7 example: reversal by structural recursion
def rev_ast(n):
    """rev(∅) = ∅, rev(w) = w^R, rev(S+T) = rev(S)+rev(T), rev(ST) = rev(T)rev(S), rev(S*) = rev(S)*."""
    k = n[0]
    if k in ("empty", "eps", "sym"):
        return n                       # a single symbol is its own reversal; strings are concatenations of symbols
    if k == "star":
        return ("star", rev_ast(n[1]))
    if k == "union":
        return ("union", rev_ast(n[1]), rev_ast(n[2]))
    return ("cat", rev_ast(n[2]), rev_ast(n[1]))


def reversed_dfa(text):
    """An exact DFA for L(R)^R: reverse the minimal DFA's edges (Lemma 4.4, proof 2) and determinize."""
    return R(text).dfa().to_nfa().reverse().to_dfa()


ok = True
for t in all_asts(5, ["empty", "eps", "0", "1"]):
    ok = ok and R(to_str(rev_ast(t))).equivalent(reversed_dfa(to_str(t)))[0]
check("L(rev(R)) = L(R)^R for every expression of size <= 5 over ∅, ε, 0, 1 (exact)", ok)
for text, expect in [("0+1(0+1)*00", "0+00(0+1)*1"), ("(0+100)*", "(0+001)*"), ("0*1", "10*")]:
    check(f"rev({text}) = {expect}, and it denotes exactly L({text})^R",
          same(to_str(rev_ast(R(text).ast)), expect)[0] and R(expect).equivalent(reversed_dfa(text))[0])
ok = all({w[::-1] for w in A | B} == {w[::-1] for w in A} | {w[::-1] for w in B} and
         {w[::-1] for w in cat(A, B)} == cat({w[::-1] for w in B}, {w[::-1] for w in A}) and
         {w[::-1] for w in star(A)} == star({w[::-1] for w in A}) for A, B, _ in TRIPLES[:300])
check("(A∪B)^R = A^R ∪ B^R, (A•B)^R = B^R•A^R, (A*)^R = (A^R)* (300 pairs, truncated at length 7)", ok)

# ---------------------------------------------------------------- 2.8 counting
from itertools import product  # noqa: E402

ok, seen = True, set()
for k in range(0, 6):
    for digits in product(range(1, 8), repeat=k):
        v = 0
        for d in digits:
            v = 8 * v + d
        ok = ok and v not in seen
        seen.add(v)
check("7 symbols read as base-8 digits 1-7: different strings (length <= 5) get different integers", ok)


def parses(text):
    try:
        Regex(text, alphabet=AB)
        return True
    except SyntaxError:
        return False


check("well-formed expressions over {0,1} are not a regular language: x = (^i, y = (^j, z = 0)^i (i ≠ j <= 8)",
      all(parses("(" * i + "0" + ")" * i) and not parses("(" * j + "0" + ")" * i)
          for i in range(9) for j in range(9) if i != j))
M = 8
langs = set()
for k in range(2 ** M):
    bits = [(k >> (M - 1 - b)) & 1 for b in range(M)]          # alpha = 0.b1 b2 ... b8 in binary
    langs.add(frozenset(n for n in range(M) if bits[n] == 1))   # L_alpha ∩ {1^n : n < 8}
check("L_alpha = {1^n : bit n+1 of alpha is 1}: the 256 reals k/256 give 256 different languages", len(langs) == 2 ** M)
check("a finite language is regular: {ε, 01, 110} = ε+01+110 (exact)",
      R("ε+01+110").equivalent(DFA.explore(AB, "", lambda q, a: q + a if len(q) < 4 else q,
                                         lambda q: q in ("", "01", "110")))[0])

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: {FAIL}")
sys.exit(1 if FAIL else 0)
