#!/usr/bin/env python3
"""Checks for every concrete example on the concept pages (group A) in content/concepts/:
strings, induction-on-strings, languages, regular-expressions, regular-languages, dfa, nfa,
product-construction, subset-construction, thompsons-algorithm, state-elimination, kleenes-theorem.

Automata are checked against brute-force predicates (all strings up to length 12-14), regular
expressions exactly (minimal-DFA equivalence), and Thompson's algorithm against an independent
re-implementation and an independent backtracking matcher."""
import os
import sys
from functools import lru_cache
from itertools import combinations

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from automata import DFA, NFA, Regex, thompson, eliminate_states, strings, first_difference, EPS  # noqa: E402
from automata.regex import to_str  # noqa: E402

FAIL = []


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAIL.append(name)


AB = "01"


def R(text):
    return Regex(text, alphabet=AB)


def same(r1, r2):
    """Exact equivalence of two regular expressions (texts), or of an expression and a DFA."""
    other = R(r2) if isinstance(r2, str) else r2
    return R(r1).equivalent(other)[0]


def val(w):
    return int(w, 2) if w else 0


def fs(*xs):
    return frozenset(xs)


# ====================================================================== strings
print("--- strings")


def length(w):                      # |ε| = 0, |ax| = 1 + |x|
    return 0 if w == "" else 1 + length(w[1:])


def cat(w, z):                      # ε•z = z, (ax)•z = a·(x•z)
    return z if w == "" else w[0] + cat(w[1:], z)


def rev(w):                         # ε^R = ε, (ax)^R = x^R • a
    return "" if w == "" else cat(rev(w[1:]), w[0])


check("ba•na unfolds: b·(a•na), a•na = a·(ε•na), ε•na = na; result bana",
      cat("ba", "na") == "b" + cat("a", "na") and cat("a", "na") == "a" + cat("", "na")
      and cat("", "na") == "na" and cat("ba", "na") == "bana")
W = "banana"
subs = {W[i:j] for i in range(len(W) + 1) for j in range(i, len(W) + 1)}
subseq = {"".join(W[k] for k in S) for r in range(len(W) + 1) for S in combinations(range(len(W)), r)}
check("|banana| = 6, with 7 prefixes and 7 suffixes",
      length(W) == 6 and len({W[:j] for j in range(7)}) == 7 and len({W[i:] for i in range(7)}) == 7)
check("banana: 15 distinct non-empty substrings (6·7/2 = 21 positions)",
      len(subs - {""}) == 15 and 6 * 7 // 2 == 21, str(len(subs - {""})))
check("banana: 'ana' starts at positions 2 and 4", [i + 1 for i in range(len(W)) if W.startswith("ana", i)] == [2, 4])
check("banana: 40 distinct subsequences (counting ε and itself), not 2^6 = 64", len(subseq) == 40, str(len(subseq)))
check("bnn is a subsequence of banana but not a substring", "bnn" in subseq and "bnn" not in subs)
B6 = list(strings("01", 6))
check("Lemmas 1.1-1.3 by brute force (|w|,|x|,|y| <= 4)",
      all(cat(w, "") == w for w in B6)
      and all(length(cat(w, x)) == length(w) + length(x) for w in strings("01", 4) for x in strings("01", 4))
      and all(cat(cat(w, x), y) == cat(w, cat(x, y)) for w in strings("01", 3) for x in strings("01", 3)
              for y in strings("01", 3)))
check("(wx)^R = x^R w^R for |w|,|x| <= 5; w^R x^R fails already for w = 0, x = 1",
      all(rev(cat(w, x)) == cat(rev(x), rev(w)) for w in strings("01", 5) for x in strings("01", 5))
      and rev(cat("0", "1")) == "10" and cat(rev("0"), rev("1")) == "01")
check("substring vs subsequence: 0110 contains 00 as a subsequence, not as a substring",
      "00" not in "0110" and any("".join("0110"[k] for k in S) == "00" for S in combinations(range(4), 2)))

# ====================================================================== induction-on-strings
print("--- induction-on-strings")
T = list(strings("012", 7))
check("|w^R| = |w| for every w over {0,1,2}, |w| <= 7", all(length(rev(w)) == length(w) for w in T))
ok = True
for w in T:
    if w:
        a, x = w[0], w[1:]
        ok &= rev(a + x) == cat(rev(x), a)                            # definition of R
        ok &= length(cat(rev(x), a)) == length(rev(x)) + length(a)    # Lemma 1.2
        ok &= length(a) == 1 and length(rev(x)) == length(x)          # |a| = 1, induction hypothesis
        ok &= length(rev(x)) + 1 == length(a + x)                     # definition of |.|
check("each step of the case w = ax: |(ax)^R| = |x^R•a| = |x^R| + |a| = |x| + 1 = |ax|", ok)
check("case w = ε: ε^R = ε", rev("") == "" and length(rev("")) == length(""))

# ====================================================================== languages
print("--- languages")
N = 7


def lcat(A, B, n=N):
    return {x + y for x in A for y in B if len(x) + len(y) <= n}


def lstar(L, n=N):
    S, frontier = {""}, {""}
    while frontier:
        new = {x + y for x in L for y in frontier if len(x) + len(y) <= n} - S
        S |= new
        frontier = new
    return S


A, B = {"0", "01"}, {"1", "11"}
check("AB = {01, 011, 0111} (three strings: 0•11 = 01•1)", lcat(A, B) == {"01", "011", "0111"} and "0" + "11" == "01" + "1")
check("BA = {10, 101, 110, 1101}, so AB != BA", lcat(B, A) == {"10", "101", "110", "1101"} and lcat(A, B) != lcat(B, A))
check("A* up to length 3 is ε, 0, 00, 01, 000, 001, 010",
      sorted((w for w in lstar(A) if len(w) <= 3), key=lambda s: (len(s), s)) == ["", "0", "00", "01", "000", "001", "010"])
pre0 = DFA("01", ["ok", "last0", "dead"], "ok", ["ok", "last0"],
           {("ok", "0"): "last0", ("ok", "1"): "dead", ("last0", "0"): "last0", ("last0", "1"): "ok",
            ("dead", "0"): "dead", ("dead", "1"): "dead"})
every1 = lambda w: all(i > 0 and w[i - 1] == "0" for i in range(len(w)) if w[i] == "1")
check("A* = strings in which every 1 is immediately preceded by 0 (exact; DFA vs predicate |w| <= 14)",
      same("(0+01)*", pre0) and first_difference(pre0, every1, AB, 14) is None
      and lstar(A) == {w for w in strings(AB, N) if every1(w)})
L01 = {"0", "1"}
check("L = {0,1}: LL has four strings, {ww : w in L} = {00, 11}",
      lcat(L01, L01) == {"00", "01", "10", "11"} and {w + w for w in L01} == {"00", "11"})
U2 = list(strings(AB, 2))
ALL2 = [{w for k, w in enumerate(U2) if mask >> k & 1} for mask in range(2 ** len(U2))]
check("∅L = L∅ = ∅ and {ε}L = L{ε} = L (all 128 L ⊆ Σ^{<=2})",
      all(lcat(set(), L) == set() == lcat(L, set()) and lcat({""}, L) == L == lcat(L, {""}) for L in ALL2))
check("L+ = L* iff ε ∈ L (all 128 L ⊆ Σ^{<=2}, truncated at length 7)",
      all((lcat(L, lstar(L)) == lstar(L)) == ("" in L) for L in ALL2))
check("∅* = {ε}* = {ε}; every other L* has arbitrarily long strings (truncation reaches length >= 6)",
      lstar(set()) == {""} == lstar({""}) and all(max(map(len, lstar(L))) >= 6 for L in ALL2 if L - {""}))
RAND3 = [ALL2[i] for i in range(0, 128, 9)]
check("concatenation is associative and distributes over ∪ (15 x 15 x 15 small languages, truncated)",
      all(lcat(lcat(X, Y), Z) == lcat(X, lcat(Y, Z)) and lcat(X, Y | Z) == lcat(X, Y) | lcat(X, Z)
          and lcat(Y | Z, X) == lcat(Y, X) | lcat(Z, X) for X in RAND3 for Y in RAND3 for Z in RAND3))
check("concatenation does not distribute over ∩: {ε,0}({0} ∩ {00}) = ∅ but {ε,0}{0} ∩ {ε,0}{00} = {00}",
      lcat({"", "0"}, set()) == set() and lcat({"", "0"}, {"0"}) & lcat({"", "0"}, {"00"}) == {"00"})

# ====================================================================== regular-expressions
print("--- regular-expressions")
no00 = DFA("01", ["s", "z", "dead"], "s", ["s", "z"],
           {("s", "0"): "z", ("s", "1"): "s", ("z", "0"): "dead", ("z", "1"): "s",
            ("dead", "0"): "dead", ("dead", "1"): "dead"})
p_no00 = lambda w: "00" not in w
check("no-00 DFA is correct (|w| <= 14)", first_difference(no00, p_no00, AB, 14) is None)
check("(1+01)*(ε+0) = binary strings with no 00 (exact)", same("(1+01)*(ε+0)", no00))
check("(ε+0)(1+10)* is equivalent (exact)", same("(ε+0)(1+10)*", "(1+01)*(ε+0)"))
E1 = R("(1+01)*(ε+0)")
check("matches ε, 0, 10, 0101, 0110; not 00, 100, 1001",
      all(E1(w) for w in ["", "0", "10", "0101", "0110"]) and not any(E1(w) for w in ["00", "100", "1001"]))
W1 = R("(1+01)*")
check("wrong answer (1+01)* misses exactly the no-00 strings that end in 0 (|w| <= 14)",
      all((p_no00(w) and not W1(w)) == (p_no00(w) and w.endswith("0")) for w in strings(AB, 14))
      and all(p_no00("1" * n + "0") and not W1("1" * n + "0") for n in range(20)))
check("precedence: 10* is not (10)* (witness 100) and 0+1* is not (0+1)* (witness 01)",
      not same("10*", "(10)*") and R("10*")("100") and not R("(10)*")("100")
      and not same("0+1*", "(0+1)*") and not R("0+1*")("01") and R("(0+1)*")("01"))
check("L(∅*) = {ε}: ∅* ≡ ε", same("∅*", "ε"))

# ====================================================================== regular-languages
print("--- regular-languages")
in_0s1s = lambda w: w == "0" * w.count("0") + "1" * w.count("1")
L_neq = lambda w: in_0s1s(w) and w.count("0") != w.count("1")
L_eq = lambda w: in_0s1s(w) and w.count("0") == w.count("1")
check("complement of {0^m1^n : m != n} intersected with 0*1* is {0^n1^n} (|w| <= 14)",
      all(((not L_neq(w)) and in_0s1s(w)) == L_eq(w) for w in strings(AB, 14)))
check("{0^n1^n} not regular (Lemma 3.6): x=0^i, y=0^j, z=1^i (i != j <= 9)",
      all(L_eq("0" * i + "1" * i) and not L_eq("0" * j + "1" * i) for i in range(10) for j in range(10) if i != j))
M5 = DFA("01", range(5), 0, [0], lambda q, a: (2 * q + int(a)) % 5)
check("the mod-5 DFA of §3.1 accepts the MSB-first multiples of 5 (|w| <= 14)",
      first_difference(M5, lambda w: val(w) % 5 == 0, AB, 14) is None)
M5R = M5.to_nfa().reverse()
check("its reversal (Lemma 4.4, proof 2) accepts exactly the LSB-first numerals of multiples of 5 (|w| <= 14)",
      first_difference(M5R, lambda w: val(w[::-1]) % 5 == 0, AB, 14) is None)
fin = "+".join("0" * n + "1" * n if n else "ε" for n in range(6))
check("a finite language is regular: {0^n1^n : n <= 5} as a union of one-string expressions (exact)",
      first_difference(R(fin), lambda w: L_eq(w) and len(w) <= 10, AB, 14) is None)
check("L ∩ ∅ = ∅ and L ∪ complement(L) = Σ* are regular for every L (so these say nothing about L)",
      all((L_eq(w) and False) is False and (L_eq(w) or not L_eq(w)) for w in strings(AB, 10)))

# ====================================================================== dfa
print("--- dfa")


def longest_progress(w, pat="01"):
    for k in range(len(pat), -1, -1):
        if k <= len(w) and w[len(w) - k:] == pat[:k]:
            return pat[:k]


D01 = DFA("01", ["", "0", "01"], "", ["01"],
          {("", "0"): "0", ("", "1"): "", ("0", "0"): "0", ("0", "1"): "01", ("01", "0"): "0", ("01", "1"): ""})
ends01 = lambda w: w.endswith("01")
check("table DFA (states ε, 0, 01) accepts exactly the strings ending in 01 (|w| <= 14)",
      first_difference(D01, ends01, AB, 14) is None)
check("state = longest suffix of the input that is a prefix of 01 (|w| <= 12)",
      all(D01.delta_star("", w) == longest_progress(w) for w in strings(AB, 12)))
check("run on 1001: ε, ε, 0, 0, 01 — accept", D01.run("1001") == ["", "", "0", "0", "01"] and D01("1001"))
check("fooling set {ε, 0, 01}: suffix 1 separates ε and 0; suffix ε separates 01 from ε and from 0",
      ends01("" + "1") != ends01("0" + "1") and ends01("" + "") != ends01("01" + "")
      and ends01("0" + "") != ends01("01" + ""))
check("minimal DFA has 3 states", len(D01.minimize().states) == 3)
check("delta*(q,xy) = delta*(delta*(q,x),y) and delta*(q,xa) = delta(delta*(q,x),a) (all q, |x|,|y| <= 5)",
      all(D01.delta_star(q, x + y) == D01.delta_star(D01.delta_star(q, x), y)
          for q in D01.states for x in strings(AB, 5) for y in strings(AB, 5))
      and all(D01.delta_star(q, x + a) == D01.delta(D01.delta_star(q, x), a)
              for q in D01.states for x in strings(AB, 6) for a in AB))
check("swapping accepting states of a DFA complements it (|w| <= 12)",
      first_difference(D01.complement(), lambda w: not ends01(w), AB, 12) is None)

# ====================================================================== nfa
print("--- nfa")
N01 = NFA("01", ["s", "a", "b"], "s", ["b"], {("s", "0"): {"s", "a"}, ("s", "1"): {"s"}, ("a", "1"): {"b"}})
check("NFA s, a, b accepts exactly the strings ending in 01 (|w| <= 14)", first_difference(N01, ends01, AB, 14) is None)
S, trace = N01.eps_reach({"s"}), []
trace.append(S)
for a in "1001":
    S = N01.eps_reach(N01.step(S, a))
    trace.append(S)
check("on 1001 the current-state sets are {s},{s},{s,a},{s,a},{s,b}; the last meets A",
      trace == [fs("s"), fs("s"), fs("s", "a"), fs("s", "a"), fs("s", "b")] and N01("1001"), str([sorted(x) for x in trace]))
Nsw = NFA("01", ["s", "a", "b"], "s", ["s", "a"], N01._delta)
check("making s and a accepting does not complement it: the result accepts 01", Nsw("01") and ends01("01"))
Eps = NFA("01", ["p", "q"], "p", ["q"], {("p", "0"): {"p"}, ("q", "1"): {"q"}, ("p", EPS): {"q"}})
check("ε-NFA p (loop 0) -ε-> q (loop 1, accepting) accepts exactly 0*1* (|w| <= 14)",
      first_difference(Eps, in_0s1s, AB, 14) is None)


def delta_star(M, q, w):
    """The page's formula: δ*(q,ε) = ε-reach(q); δ*(q,ax) = ∪_{r ∈ ε-reach(q)} ∪_{p ∈ δ(r,a)} δ*(p,x)."""
    if w == "":
        return set(M.eps_reach({q}))
    out = set()
    for r in M.eps_reach({q}):
        for p in M.delta(r, w[0]):
            out |= delta_star(M, p, w[1:])
    return out


TH = R("(0+10*1)*").nfa()
check("the page's recursive δ* agrees with the set-of-threads simulation (two ε-NFAs, |w| <= 8)",
      all(bool(delta_star(M, M.start, w) & M.accepting) == M.accepts(w) for M in (Eps, TH, N01) for w in strings(AB, 8)))


def remove_eps(M):
    """The page's ε-removal: same Q and s; q accepting iff ε-reach(q) meets A; δ'(q,a) = ∪_{r∈ε-reach(q)} δ(r,a)."""
    A2 = {q for q in M.states if M.eps_reach({q}) & M.accepting}
    d = {}
    for q in M.states:
        for a in M.alphabet:
            T_ = set()
            for r in M.eps_reach({q}):
                T_ |= M.delta(r, a)
            if T_:
                d[(q, a)] = T_
    return NFA(M.alphabet, M.states, M.start, A2, d)


ok = True
for M in (Eps, TH):
    M2 = remove_eps(M)
    ok &= not M2.has_epsilon() and len(M2.states) == len(M.states)
    ok &= first_difference(M, M2, AB, 12) is None
check("ε-removal keeps the states, removes every ε-transition and keeps the language (two ε-NFAs)", ok)

# ====================================================================== product-construction
print("--- product-construction")
PAR = DFA("01", ["E", "O"], "E", ["E"], lambda q, a: "O" if q == "E" else "E")    # even length
check("parity-of-length DFA accepts exactly the even-length strings", first_difference(PAR, lambda w: len(w) % 2 == 0, AB, 14) is None)
expected = {
    "and": {("01", "E")},
    "or": {("", "E"), ("0", "E"), ("01", "E"), ("01", "O")},
    "diff": {("01", "O")},
    "xor": {("", "E"), ("0", "E"), ("01", "O")},
}
preds = {
    "and": lambda w: ends01(w) and len(w) % 2 == 0,
    "or": lambda w: ends01(w) or len(w) % 2 == 0,
    "diff": lambda w: ends01(w) and len(w) % 2 == 1,
    "xor": lambda w: ends01(w) != (len(w) % 2 == 0),
}
for mode in ["and", "or", "diff", "xor"]:
    P = D01.product(PAR, mode)
    check(f"product ({mode}): accepting pairs {sorted(expected[mode])} and the right language (|w| <= 14)",
          set(P.accepting) == expected[mode] and first_difference(P, preds[mode], AB, 14) is None)
P = D01.product(PAR, "and")
check("all six pairs are reachable", len(P.states) == 6 and len(P.reachable()) == 6)
check("run on 1101: (ε,E),(ε,O),(ε,E),(0,O),(01,E) — accepted by the ∩ machine",
      P.run("1101") == [("", "E"), ("", "O"), ("", "E"), ("0", "O"), ("01", "E")] and P("1101"))
check("Lemma 3.1 on this product: δ*((p,q),w) = (δ1*(p,w), δ2*(q,w)) (all pairs, |w| <= 8)",
      all(P.delta_star((p, q), w) == (D01.delta_star(p, w), PAR.delta_star(q, w))
          for p in D01.states for q in PAR.states for w in strings(AB, 8)))
check("A1 × A2 alone gives only ∩: (01,O) must also accept for ∪ (string 001)",
      ("01", "O") in expected["or"] and preds["or"]("001") and not preds["and"]("001"))
# an incomplete factor loses strings of the union
D01_partial = NFA("01", ["", "0", "01"], "", ["01"], {("", "0"): {"0"}, ("0", "0"): {"0"}, ("0", "1"): {"01"},
                                                     ("01", "0"): {"0"}})    # missing transitions on 1 from ε, 01
PARn = PAR.to_nfa()


def nfa_product(M1, M2, op):
    Q = [(p, q) for p in M1.states for q in M2.states]
    d = {}
    for (p, q) in Q:
        for a in M1.alphabet:
            T_ = {(r, s_) for r in M1.delta(p, a) for s_ in M2.delta(q, a)}
            if T_:
                d[((p, q), a)] = T_
    A_ = [(p, q) for (p, q) in Q if op(p in M1.accepting, q in M2.accepting)]
    return NFA(M1.alphabet, Q, (M1.start, M2.start), A_, d)


Pu = nfa_product(D01_partial, PARn, lambda x, y: x or y)
check("with a missing transition in one factor the 'union' product loses strings: it rejects 11 (even length)",
      not Pu("11") and preds["or"]("11"))

# ====================================================================== subset-construction
print("--- subset-construction")
dE, rowsE = Eps.subset_construction()
want = [(fs("p"), fs("p", "q"), True, {"0": fs("p"), "1": fs("q")}),
        (fs("q"), fs("q"), True, {"0": fs(), "1": fs("q")}),
        (fs(), fs(), False, {"0": fs(), "1": fs()})]
check("ε example: rows {p}|{p,q}|yes|{p}|{q}; {q}|{q}|yes|∅|{q}; ∅|∅|no|∅|∅", rowsE == want,
      str([(sorted(S), sorted(Rr), acc, {a: sorted(t) for a, t in tr.items()}) for S, Rr, acc, tr in rowsE]))
check("the 3-state DFA accepts exactly 0*1* (|w| <= 14)", len(dE.states) == 3 and first_difference(dE, in_0s1s, AB, 14) is None)
d01, rows01 = N01.subset_construction()
check("ends-in-01 NFA: subsets {s}, {s,a}, {s,b} (3 of 2^3 = 8), accepting {s,b}",
      d01.states == [fs("s"), fs("s", "a"), fs("s", "b")] and set(d01.accepting) == {fs("s", "b")})
iso = {fs("s"): "", fs("s", "a"): "0", fs("s", "b"): "01"}
check("... and it is the 3-state DFA of the DFA page under {s}->ε, {s,a}->0, {s,b}->01",
      all(iso[d01.delta(S_, a)] == D01.delta(iso[S_], a) for S_ in d01.states for a in AB))
dT, rowsT = TH.subset_construction()
check("Thompson's 14-state NFA for (0+10*1)*: 5 DFA states, not 2^14 = 16384",
      len(TH.states) == 14 and len(dT.states) == 5 and 2 ** 14 == 16384)
check("invariant: ε-reach((δ')*({s}, w)) = the set of states the NFA can be in after w (Thompson NFA, |w| <= 10)",
      all(TH.eps_reach(dT.delta_star(dT.start, w)) == TH.current_states(w) for w in strings(AB, 10)))
ok, sizes = True, []
for k in range(1, 9):
    d = {(0, "0"): {0}, (0, "1"): {0, 1}}
    for i in range(1, k):
        d[(i, "0")] = {i + 1}
        d[(i, "1")] = {i + 1}
    Nk = NFA("01", range(k + 1), 0, {k}, d)
    kth = lambda w, k=k: len(w) >= k and w[-k] == "1"
    ok &= first_difference(Nk, kth, AB, k + 6) is None
    Dk = Nk.to_dfa()
    sizes.append((k, len(Nk.states), len(Dk.states), len(Dk.minimize().states)))
    ok &= len(Nk.states) == k + 1 and len(Dk.states) == 2 ** k and len(Dk.minimize().states) == 2 ** k
    if k <= 7:
        Fk = list(strings(AB, k, k))
        for x, y in combinations(Fk, 2):
            i = next(j for j in range(k) if x[j] != y[j]) + 1
            z = "0" * (i - 1)
            ok &= kth(x + z) != kth(y + z)
check("kth symbol from the end is 1: (k+1)-state NFA, subset construction and minimal DFA both 2^k (k = 1..8);"
      " strings of length k form a fooling set with suffix 0^(i-1) (k <= 7)", ok, str(sizes))

# ====================================================================== thompsons-algorithm
print("--- thompsons-algorithm")


@lru_cache(maxsize=None)
def matches(node, w):
    """Independent backtracking matcher for expression ASTs."""
    k = node[0]
    if k == "empty":
        return False
    if k == "eps":
        return w == ""
    if k == "sym":
        return w == node[1]
    if k == "union":
        return matches(node[1], w) or matches(node[2], w)
    if k == "cat":
        return any(matches(node[1], w[:i]) and matches(node[2], w[i:]) for i in range(len(w) + 1))
    return w == "" or any(matches(node[1], w[:i]) and matches(node, w[i:]) for i in range(1, len(w) + 1))


def my_thompson(node):
    """The page's gadgets, re-implemented with a record of every gadget (start, accept, its states)."""
    states, delta, gadgets = [], {}, []

    def new():
        states.append(len(states))
        return states[-1]

    def add(p, a, q):
        delta.setdefault((p, a), set()).add(q)

    def build(n):
        k, before = n[0], len(states)
        if k in ("empty", "eps", "sym"):
            s, t = new(), new()
            if k == "eps":
                add(s, EPS, t)
            if k == "sym":
                add(s, n[1], t)
        elif k == "cat":
            s, t1 = build(n[1])
            s2, t = build(n[2])
            add(t1, EPS, s2)
        elif k == "union":
            s = new()
            s1, t1 = build(n[1])
            s2, t2 = build(n[2])
            t = new()
            add(s, EPS, s1), add(s, EPS, s2), add(t1, EPS, t), add(t2, EPS, t)
        else:
            s = new()
            s1, t1 = build(n[1])
            t = new()
            add(s, EPS, s1), add(t1, EPS, s1), add(t1, EPS, t), add(s, EPS, t)
        gadgets.append((s, t, set(range(before, len(states)))))
        return s, t

    s, t = build(node)
    return NFA("01", states, s, {t}, delta), gadgets


def exprs(n):
    if n == 1:
        return [("empty",), ("eps",), ("sym", "0"), ("sym", "1")]
    out = [("star", e) for e in exprs(n - 1)]
    for k in range(1, n - 1):
        for l_ in exprs(k):
            for r_ in exprs(n - 1 - k):
                out += [("union", l_, r_), ("cat", l_, r_)]
    return out


def counts(node):
    k = node[0]
    if k in ("empty", "eps", "sym"):
        return 1
    return sum(counts(c) for c in node[1:]) + (k in ("union", "star"))


ALL5 = [e for n in range(1, 6) for e in exprs(n)]
ok_same = ok_lang = ok_inv = ok_count = ok_one = True
for e in ALL5:
    mine, gadgets = my_thompson(e)
    lib = thompson(e, "01")
    ok_same &= mine._delta == lib._delta and mine.start == lib.start and mine.accepting == lib.accepting
    ok_lang &= all(mine.accepts(w) == matches(e, w) for w in strings(AB, 5))
    edges = [(p, a, q) for (p, a), Tq in mine._delta.items() for q in Tq]
    for (s, t, Sg) in gadgets:
        ok_inv &= all(q == s for (p, a, q) in edges if q in Sg and p not in Sg)
        ok_inv &= all(p == t for (p, a, q) in edges if p in Sg and q not in Sg)
    t_ = next(iter(mine.accepting))
    ok_one &= len(mine.accepting) == 1 and t_ != mine.start
    ok_one &= not any(q == mine.start for (p, a, q) in edges) and not any(p == t_ for (p, a, q) in edges)
    ok_count &= len(mine.states) == 2 * counts(e) <= 2 * len(to_str(e))
check(f"my re-implementation of the gadgets builds exactly the library's NFA ({len(ALL5)} expressions of size <= 5)", ok_same)
check("Thompson's NFA accepts exactly L(R) (independent matcher, |w| <= 5, all those expressions)", ok_lang)
check("every gadget is entered only at its start state and left only from its accepting state", ok_inv)
check("Lemma 4.2: one accepting state t != s; s has no incoming and t no outgoing edges", ok_one)
check("states = 2 x (leaves + unions + stars) <= 2 x length of the expression", ok_count)
e01 = R("(0+10*1)*")
check("(0+10*1)*: 2 x (4 + 1 + 2) = 14 states", len(e01.nfa().states) == 14 == 2 * counts(e01.ast) and counts(e01.ast) == 7)
z1 = R("0*1").nfa()
eps_n = sum(len(Tq) for (q, a), Tq in z1._delta.items() if a == EPS)
sym_n = sum(len(Tq) for (q, a), Tq in z1._delta.items() if a != EPS)
dz = z1.to_dfa()
check("0*1: 6 states, 5 ε-transitions, 2 symbol transitions", len(z1.states) == 6 and eps_n == 5 and sym_n == 2)
check("0*1: subset construction gives 4 states including the dump ∅; minimal DFA has 3",
      len(dz.states) == 4 and fs() in dz.states and len(dz.minimize().states) == 3)
# star gadget without the bypass edge s -ε-> t
nb_s = NFA("01", [0, 1, 2, 3], 0, {3}, {(1, "0"): {2}, (0, EPS): {1}, (2, EPS): {1, 3}})
check("star gadget for 0 without the bypass s -ε-> t rejects ε (and still accepts 0, 00)",
      not nb_s("") and nb_s("0") and nb_s("00"))
ok = True
for e in [x for n in range(1, 5) for x in exprs(n)]:
    inner, _ = my_thompson(e)
    k = len(inner.states)
    d = {key: set(v) for key, v in inner._delta.items()}
    ti = next(iter(inner.accepting))
    d.setdefault((k, EPS), set()).add(inner.start)            # s -ε-> s_S
    d.setdefault((ti, EPS), set()).update({inner.start, k + 1})  # t_S -ε-> s_S, t_S -ε-> t   (no s -ε-> t)
    nb = NFA("01", list(range(k + 2)), k, {k + 1}, d)
    ok &= all(nb.accepts(w) == (matches(("cat", e, ("star", e)), w)) for w in strings(AB, 5))
    ok &= nb.accepts("") == matches(e, "")
check("in general the star gadget without the bypass accepts L(S)L(S)* = L(S)^+, so it accepts ε iff ε ∈ L(S) (size <= 4)", ok)
# the shortcut star on the two-state NFA of 0*1
base = {("s", "0"): {"s"}, ("s", "1"): {"t"}}
N0s1 = NFA("01", ["s", "t"], "s", ["t"], base)
check("two-state NFA (s loops on 0, s -1-> t) accepts exactly 0*1", same("0*1", N0s1.to_dfa()))
short = NFA("01", ["s", "t"], "s", ["s", "t"], {**base, ("t", EPS): {"s"}})
check("shortcut star (s accepting, t -ε-> s, no new states) accepts 0, which is not in (0*1)*",
      short("0") and not R("(0*1)*")("0"))
gad = NFA("01", ["S", "s", "t", "T"], "S", ["T"],
          {**base, ("S", EPS): {"s", "T"}, ("t", EPS): {"s", "T"}})
check("Thompson's star gadget around the same NFA accepts exactly (0*1)*", same("(0*1)*", gad.to_dfa()))

# ====================================================================== state-elimination
print("--- state-elimination")
EVEN = DFA("01", ["E", "O"], "E", ["E"], {("E", "0"): "E", ("E", "1"): "O", ("O", "0"): "O", ("O", "1"): "E"})
even1 = lambda w: w.count("1") % 2 == 0
check("parity DFA E/O accepts exactly the strings with an even number of 1s", first_difference(EVEN, even1, AB, 14) is None)


def elim_steps(edges, order):
    """State elimination by hand: edges {(p, r): expression text}; returns the edge table after each step."""
    Rt, snaps = dict(edges), []
    for q in order:
        loop = Rt.get((q, q))
        preds = [p for (p, x) in Rt if x == q and p != q]
        succs = [r for (x, r) in Rt if x == q and r != q]
        for p in preds:
            for r in succs:
                term = f"({Rt[(p, q)]})" + (f"({loop})*" if loop else "") + f"({Rt[(q, r)]})"
                Rt[(p, r)] = f"({Rt[(p, r)]})+{term}" if (p, r) in Rt else term
        Rt = {k: v for k, v in Rt.items() if q not in k}
        snaps.append(dict(Rt))
    return snaps


EDGES = {("s", "E"): "ε", ("E", "t"): "ε", ("E", "E"): "0", ("E", "O"): "1", ("O", "O"): "0", ("O", "E"): "1"}
s1, s2 = elim_steps(EDGES, ["O", "E"])
check("eliminating O changes only the loop at E: R'(E->E) = 0+10*1",
      set(s1) == {("s", "E"), ("E", "t"), ("E", "E")} and s1[("s", "E")] == "ε" and s1[("E", "t")] == "ε"
      and same(s1[("E", "E")], "0+10*1"), str(s1))
check("eliminating E then leaves R(s->t) ≡ (0+10*1)*", set(s2) == {("s", "t")} and same(s2[("s", "t")], "(0+10*1)*"))
check("library state elimination, order O then E: exactly (0+10*1)*", to_str(eliminate_states(EVEN, ["O", "E"])) == "(0+10*1)*")
other = to_str(eliminate_states(EVEN, ["E", "O"]))
check("the other order gives 0*+0*1(0+10*1)*10*, equivalent", other == "0*+0*1(0+10*1)*10*"
      and same(other, "(0+10*1)*") and same(other, EVEN), other)
t1, t2 = elim_steps(EDGES, ["E", "O"])
check("hand elimination in the other order agrees", same(t2[("s", "t")], "0*+0*1(0+10*1)*10*"))

M3 = DFA("01", ["s", 0, 1, 2], "s", [0],
         {("s", "0"): 0, ("s", "1"): 1, **{(q, a): (2 * q + int(a)) % 3 for q in range(3) for a in AB}})
check("remainder-mod-3 DFA with a separate start state accepts the non-empty multiples of 3 (|w| <= 14)",
      first_difference(M3, lambda w: w != "" and val(w) % 3 == 0, AB, 14) is None)
book3 = "0*0+0*1(10*1+01*0)*10*"
ok = same("00*+(00*1+1)(01*0+10*1)*10*", book3) and same(book3, M3)
for order in [[2, 0, 1, "s"], [2, 1, 0, "s"], ["s", 0, 1, 2], [1, 2, 0, "s"]]:     # any order works
    ok &= same(to_str(eliminate_states(M3, order)), book3)
check("state elimination on that DFA gives expressions equivalent to the §2.3 expression 0*0+0*1(10*1+01*0)*10*"
      " (book's raw result 00*+(00*1+1)(01*0+10*1)*10* included)", ok)

# ====================================================================== kleenes-theorem
print("--- kleenes-theorem")
dK = dT
accK = [S_ for S_ in dK.states if S_ in dK.accepting]
mK = dK.minimize()
check("(0+10*1)* is the language of strings with an even number of 1s (exact)", same("(0+10*1)*", EVEN))
check("cycle: Thompson 14 states -> subset construction 5 states (3 accepting, 2 not) -> minimal 2",
      len(TH.states) == 14 and len(dK.states) == 5 and len(accK) == 3 and len(mK.states) == 2)
check("the minimal DFA is the parity DFA (exactly equivalent)", mK.equivalent(EVEN)[0])
rej = [c for c in mK.states if c not in mK.accepting]
acc = [c for c in mK.states if c in mK.accepting]
check("state elimination on the minimal DFA, rejecting state first, gives back (0+10*1)*",
      to_str(eliminate_states(mK, rej + acc)) == "(0+10*1)*")
r47 = Regex("(0+1)*(00+11)(0+1)*", alphabet=AB)
n47, n47c = r47.nfa(), thompson(r47.ast, AB, classes=True)
d47, d47c = n47.to_dfa(), n47c.to_dfa()
check("§4.7: (0+1)*(00+11)(0+1)*: 26 states built literally, 18 with each 0+1 as one gadget; 9-state DFA; minimal 4",
      len(n47.states) == 26 and len(n47c.states) == 18 and len(d47.states) == 9 == len(d47c.states)
      and len(d47.minimize().states) == 4 == len(d47c.minimize().states),
      f"{len(n47.states)}, {len(n47c.states)}, {len(d47.states)}, {len(d47c.states)}")
check("... and both NFAs accept exactly the strings containing 00 or 11 (|w| <= 12)",
      first_difference(n47, lambda w: "00" in w or "11" in w, AB, 12) is None
      and first_difference(n47c, lambda w: "00" in w or "11" in w, AB, 12) is None)
check("DFA -> NFA is trivial: δ'(q,a) = {δ(q,a)} accepts the same language",
      first_difference(EVEN.to_nfa(), EVEN, AB, 12) is None and first_difference(D01.to_nfa(), D01, AB, 12) is None)
check("ε-removal on Thompson's NFA keeps its 14 states and its language",
      len(remove_eps(TH).states) == 14 and first_difference(remove_eps(TH), TH, AB, 12) is None)

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: {FAIL}")
sys.exit(1 if FAIL else 0)
