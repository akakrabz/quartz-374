#!/usr/bin/env python3
"""Checks for every concrete claim on content/1-models-of-computation/03-finite-state-machines.md."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from automata import DFA, strings, first_difference  # noqa: E402

FAIL = []


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAIL.append(name)


def val(w):
    return int(w, 2) if w else 0


# ---------------------------------------------------------------- 3.1 mod-5 DFA
M5 = DFA("01", range(5), 0, [0], lambda q, a: (2 * q + int(a)) % 5)
check("mod-5 DFA accepts exactly the binary multiples of 5 (ε counts as 0), |w| <= 14",
      first_difference(M5.accepts, lambda w: val(w) % 5 == 0, "01", 14) is None)
trace = M5.run("00101110110")
check("374 = 00101110110 in binary", val("00101110110") == 374)
check("run on 374 visits 0,0,0,1,2,0,1,3,1,3,2,4 and rejects", trace == [0, 0, 0, 1, 2, 0, 1, 3, 1, 3, 2, 4]
      and not M5.accepts("00101110110"), str(trace))

# ---------------------------------------------------------------- 3.3 parity DFA, and the stronger claim
P = DFA("01", "st", "s", ["t"], {("s", "0"): "s", ("s", "1"): "t", ("t", "0"): "t", ("t", "1"): "s"})
check("parity DFA accepts exactly the strings with an odd number of 1s",
      first_difference(P.accepts, lambda w: w.count("1") % 2 == 1, "01", 14) is None)
ok = all((P.delta_star("s", w), P.delta_star("t", w)) == (("s", "t") if w.count("1") % 2 == 0 else ("t", "s"))
         for w in strings("01", 12))
check("stronger claim: delta*(s,w), delta*(t,w) as stated for every w, |w| <= 12", ok)

# ---------------------------------------------------------------- 3.5 contains 11
def step2(q, a):
    found, last2 = q
    l2 = (last2 + a)[-2:]
    return (found or l2 == "11", l2)


B = DFA.explore("01", (False, ""), step2, lambda q: q[0])
check("brute force (found, last two symbols): 2 x 7 = 14 possible states, 10 reachable", len(B.states) == 10,
      f"{len(B.states)} reachable")
check("brute-force DFA is correct", first_difference(B.accepts, lambda w: "11" in w, "01", 14) is None)


def step1(q, a):
    found, last = q
    return (found or (last == "1" and a == "1"), a)


B1 = DFA.explore("01", (False, ""), step1, lambda q: q[0])
check("remembering only the last symbol: 5 reachable states", len(B1.states) == 5, f"{len(B1.states)}")
C11 = DFA("01", "sab", "s", ["b"], {("s", "0"): "s", ("s", "1"): "a", ("a", "0"): "s", ("a", "1"): "b",
                                   ("b", "0"): "b", ("b", "1"): "b"})
check("3-state DFA for 'contains 11' is correct", first_difference(C11.accepts, lambda w: "11" in w, "01", 14) is None)
check("minimal DFA for 'contains 11' has 3 states", len(B.minimize().states) == 3 == len(C11.minimize().states))

# ---------------------------------------------------------------- 3.6 product
E0 = DFA("01", "EO", "E", ["E"], lambda q, a: q if a == "1" else ("O" if q == "E" else "E"))  # even #0
O1 = DFA("01", "EO", "E", ["O"], lambda q, a: q if a == "0" else ("O" if q == "E" else "E"))  # odd #1
Pr = E0.product(O1, "and")
check("product has 4 states", len(Pr.states) == 4)
check("product accepting set is {(E,O)}", set(Pr.accepting) == {("E", "O")})
ev0 = lambda w: w.count("0") % 2 == 0
od1 = lambda w: w.count("1") % 2 == 1
for mode, f in [("and", lambda w: ev0(w) and od1(w)), ("or", lambda w: ev0(w) or od1(w)),
                ("diff", lambda w: ev0(w) and not od1(w)), ("xor", lambda w: ev0(w) != od1(w))]:
    check(f"product with mode {mode} is correct", first_difference(E0.product(O1, mode).accepts, f, "01", 12) is None)
check("product lemma delta*((p,q),w) = (delta1*(p,w), delta2*(q,w)) for |w| <= 10",
      all(Pr.delta_star(("E", "E"), w) == (E0.delta_star("E", w), O1.delta_star("E", w)) for w in strings("01", 10)))

# ---------------------------------------------------------------- 3.8 fooling set for mod 5
L5 = lambda w: val(w) % 5 == 0
F5 = ["0", "1", "10", "11", "100"]


def dist_suffix(x, y, L, alphabet="01", maxlen=6):
    for z in strings(alphabet, maxlen):
        if L(x + z) != L(y + z):
            return z
    return None


ok = True
rows = []
for i, x in enumerate(F5):
    for y in F5[i + 1:]:
        z = dist_suffix(x, y, L5)
        rows.append((x, y, z))
        ok = ok and z is not None
check("{0,1,10,11,100} is a fooling set for multiples of 5", ok, "; ".join(f"{x}/{y}:{z!r}" for x, y, z in rows))
check("01 distinguishes 1 and 11 (101 = 5 in L, 1101 = 13 not)", L5("101") and not L5("1101"))

# ---------------------------------------------------------------- 3.8 standard fooling sets
R = range(0, 9)
L_0n1n = lambda w: len(w) % 2 == 0 and w == "0" * (len(w) // 2) + "1" * (len(w) // 2)
check("Lemma 3.6: x=0^i, y=0^j, z=1^i: xz in L, yz not",
      all(L_0n1n("0" * i + "1" * i) and not L_0n1n("0" * j + "1" * i) for i in R for j in R if i != j))
L_pal = lambda w: len(w) % 2 == 0 and w == w[::-1]
check("Lemma 3.7: x=0^i1, y=0^j1, z=10^i: xz = 0^i 11 0^i in L, yz not",
      all(L_pal("0" * i + "1" + "1" + "0" * i) and not L_pal("0" * j + "1" + "1" + "0" * i)
          for i in R for j in R if i != j))
is_pow2 = lambda n: n > 0 and n & (n - 1) == 0
L_pow = lambda w: set(w) <= {"0"} and is_pow2(len(w))
check("Lemma 3.8: x=0^(2^i), y=0^(2^j), z=0^(2^i): xz in L, yz not",
      all(L_pow("0" * (2 ** i + 2 ** i)) and not L_pow("0" * (2 ** j + 2 ** i)) for i in R for j in R if i != j))
L_eq = lambda w: w.count("0") == w.count("1")
check("#0 = #1: x=0^i, y=0^j, z=1^i", all(L_eq("0" * i + "1" * i) and not L_eq("0" * j + "1" * i)
                                          for i in R for j in R if i != j))
L_012 = lambda w: len(w) % 3 == 0 and w == "0" * (len(w) // 3) + "1" * (len(w) // 3) + "2" * (len(w) // 3)
check("0^n1^n2^n: x=0^i, y=0^j, z=1^i 2^i", all(L_012("0" * i + "1" * i + "2" * i) and not L_012("0" * j + "1" * i + "2" * i)
                                                for i in R for j in R if i != j))
check("closure: {#0 = #1} ∩ 0*1* = {0^n1^n} (|w| <= 14)",
      all((L_eq(w) and w == "0" * w.count("0") + "1" * w.count("1")) == L_0n1n(w) for w in strings("01", 14)))

# ---------------------------------------------------------------- 3.9 Myhill–Nerode on the mod-5 DFA
check("mod-5 language: minimal DFA has 5 states (= max fooling set size)", len(M5.minimize().states) == 5)

# ---------------------------------------------------------------- 3.10 Moore on the mod-6 counter
C6 = DFA("01", range(6), 0, [0, 3], lambda q, a: (q + (a == "1")) % 6)
check("mod-6 counter decides 'number of 1s divisible by 3'",
      first_difference(C6.accepts, lambda w: w.count("1") % 3 == 0, "01", 14) is None)
init = {frozenset((p, q)) for p in range(6) for q in range(p + 1, 6) if (p in (0, 3)) != (q in (0, 3))}
check("initial marks: 8 accepting/non-accepting pairs", len(init) == 8)
D = C6.distinguishable_pairs()
pass1 = {frozenset(p) for p in [(1, 2), (1, 5), (2, 4), (4, 5)]}
check("pass 1 marks exactly (1,2), (1,5), (2,4), (4,5)", D == init | pass1, str(sorted(tuple(sorted(x)) for x in D - init)))
check("pass 2 marks nothing: 2 passes in all", C6._moore_passes == 2)
mn = C6.minimize()
check("merging gives the classes {0,3}, {1,4}, {2,5}",
      sorted(sorted(c) for c in mn.states) == [[0, 3], [1, 4], [2, 5]])

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: {FAIL}")
sys.exit(1 if FAIL else 0)
