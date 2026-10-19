#!/usr/bin/env python3
"""Checks for every concrete claim on content/practice/03-finite-state-machines.md.

Every predicate below is written from the problem statement, independently of the answers.
Regular languages are compared exactly: each answer DFA or expression against an independent DFA
built from the predicate alone (Myhill–Nerode classes of prefixes, see mn_dfa), plus brute force.
"""
import os
import random
import sys
from collections import deque

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from automata import DFA, Regex, strings, first_difference  # noqa: E402

FAIL = []


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAIL.append(name)


def occ(u, w):
    """Number of (possibly overlapping) occurrences of u in w as a substring."""
    return sum(1 for i in range(len(w) - len(u) + 1) if w[i:i + len(u)] == u)


def mn_dfa(pred, alphabet="01", K=8, cap=64):
    """A DFA built from the predicate alone: its states are the classes of prefixes, where two prefixes
    are in the same class when no suffix of length <= K tells them apart (Myhill–Nerode). It is the
    minimal DFA of the language whenever every two inequivalent prefixes differ on a suffix of length
    <= K (true for a regular language whose minimal DFA has at most K + 2 states)."""
    suffixes = list(strings(alphabet, K))

    def sig(p):
        return tuple(bool(pred(p + z)) for z in suffixes)

    s0 = sig("")
    rep, order, delta = {s0: ""}, [s0], {}
    queue = deque([s0])
    while queue:
        S = queue.popleft()
        for a in alphabet:
            T = sig(rep[S] + a)
            if T not in rep:
                rep[T] = rep[S] + a
                order.append(T)
                queue.append(T)
                if len(order) > cap:
                    raise ValueError("too many classes: not regular, or K too small")
            delta[(S, a)] = T
    return DFA(alphabet, order, s0, [S for S in order if pred(rep[S])], delta)


def exact(dfa, pred, maxlen=14, name=""):
    """Brute force up to maxlen, and exact equivalence with the independent DFA from the predicate."""
    w = first_difference(dfa.accepts, pred, dfa.alphabet, maxlen)
    check(f"{name}: agrees with the predicate on all strings of length <= {maxlen}", w is None, f"first difference {w!r}")
    ok, wit = dfa.equivalent(mn_dfa(pred, "".join(dfa.alphabet)))
    check(f"{name}: exactly equivalent to the predicate's own DFA", ok, f"witness {wit!r}")


def table(rows, start, acc, alphabet="01"):
    """DFA from {state: (next on 0, next on 1)}."""
    states = list(rows)
    return DFA(alphabet, states, start, acc,
               {(q, a): rows[q][k] for q in states for k, a in enumerate(alphabet)})


def dist_suffix(x, y, L, alphabet="01", maxlen=8):
    for z in strings(alphabet, maxlen):
        if L(x + z) != L(y + z):
            return z
    return None


def is_fooling(F, L, alphabet="01", maxlen=8):
    return all(dist_suffix(x, y, L, alphabet, maxlen) is not None for i, x in enumerate(F) for y in F[i + 1:])


def distinguishes(z, x, y, L):
    return L(x + z) != L(y + z)


# ====================================================================== 3.1 true or false
print("--- 3.1")
L0n1n = lambda w: len(w) % 2 == 0 and w == "0" * (len(w) // 2) + "1" * (len(w) // 2)
# (a) L = L' = {0^n1^n}: L xor L' is empty
check("3.1(a) {0^n1^n} xor {0^n1^n} is empty (|w| <= 14)", not any(L0n1n(w) != L0n1n(w) for w in strings("01", 14)))
check("3.1(a) {0^n1^n} is not regular: 0^i / 0^j distinguished by 1^i (i != j <= 12)",
      all(distinguishes("1" * i, "0" * i, "0" * j, L0n1n) for i in range(13) for j in range(13) if i != j))
# (b) L2 = L1 xor (L1 xor L2), on random sets of short strings
universe = list(strings("01", 6))
rng = random.Random(374)
ok = True
for _ in range(300):
    L1 = {w for w in universe if rng.random() < 0.5}
    L2 = {w for w in universe if rng.random() < 0.5}
    ok = ok and (L1 ^ (L1 ^ L2)) == L2
check("3.1(b) L2 = L1 xor (L1 xor L2) for 300 random pairs of languages", ok)
# (c) L = {0^n1^n}, L' = complement: L' not regular (0^* fools it too), and L cap L' = empty
Lc_ = lambda w: not L0n1n(w)
check("3.1(c) complement of {0^n1^n}: 0^i / 0^j distinguished by 1^i (i != j <= 12)",
      all(distinguishes("1" * i, "0" * i, "0" * j, Lc_) for i in range(13) for j in range(13) if i != j))
check("3.1(c) L cap complement(L) is empty (|w| <= 14)", not any(L0n1n(w) and Lc_(w) for w in strings("01", 14)))
# (d) {w : |w| = 5}: fooling set {0^0..0^6} with z = 0^(5-i), and a 7-state DFA
L5 = lambda w: len(w) == 5
check("3.1(d) for 0 <= i < j <= 6, z = 0^(5-i): |0^i z| = 5 in L, 0^j z not",
      all(L5("0" * i + "0" * (5 - i)) and not L5("0" * j + "0" * (5 - i)) for i in range(7) for j in range(i + 1, 7)))
M5 = DFA.explore("01", 0, lambda q, a: min(q + 1, 6), lambda q: q == 5)
exact(M5, L5, 14, "3.1(d) length-counter DFA for |w| = 5")
check("3.1(d) that DFA has 7 states and is minimal", len(M5.states) == 7 and len(M5.minimize().states) == 7)
# (e) L = {0^(2^n)}: not regular (Lemma 3.8, checked in tools/checks/ch03.py), contains 0, L* = 0*
Lpow = lambda w: set(w) <= {"0"} and len(w) > 0 and (len(w) & (len(w) - 1)) == 0
check("3.1(e) 0 = 0^(2^0) is in L", Lpow("0"))
reach = [True] + [False] * 80
for m in range(1, 81):
    reach[m] = any(reach[m - (1 << k)] for k in range(7) if (1 << k) <= m)
check("3.1(e) every 0^m (m <= 80) is a concatenation of strings of L, so L* = 0*", all(reach))
# (f) a DFA with n states that accepts something accepts a string of length < n
rng = random.Random(3)
ok, tested = True, 0
for _ in range(3000):
    n = rng.randint(1, 5)
    Q = list(range(n))
    A = [q for q in Q if rng.random() < 0.3]
    M = DFA("01", Q, 0, A, {(q, a): rng.randrange(n) for q in Q for a in "01"})
    acc = [w for w in strings("01", 12) if M.accepts(w)]
    if acc:
        tested += 1
        ok = ok and len(acc[0]) < n            # strings() lists shortest first
check(f"3.1(f) in {tested} random DFAs (1-5 states) accepting something, the shortest accepted string has length < n", ok)

# ====================================================================== 3.2 bounded counter
print("--- 3.2")


def L32(w):
    """every prefix p has |#0(p) - #1(p)| <= 2"""
    return all(abs(w[:k].count("0") - w[:k].count("1")) <= 2 for k in range(len(w) + 1))


for w, want in [("0101", True), ("001101", True), ("0001", False), ("000", False), ("", True)]:
    check(f"3.2 example {w!r} in L is {want}", L32(w) == want)
D32 = table({"d-2": ("d-1", "dead"), "d-1": ("d0", "d-2"), "d0": ("d1", "d-1"), "d1": ("d2", "d0"),
             "d2": ("dead", "d1"), "dead": ("dead", "dead")}, "d0", ["d-2", "d-1", "d0", "d1", "d2"])
exact(D32, L32, 16, "3.2 six-state counter DFA")
check("3.2 the counter DFA is minimal (6 states)", len(D32.minimize().states) == 6)
ok = all(D32.delta_star("d0", w) == ("dead" if not L32(w) else
                                       "d" + str(w.count("0") - w.count("1")))
         for w in strings("01", 12))
check("3.2 state meanings: d_k iff all prefixes fine and #0 - #1 = k; dead iff some prefix failed (|w| <= 12)", ok)
check("3.2 run on 001101: d0 d1 d2 d1 d0 d1 d0", D32.run("001101") == ["d0", "d1", "d2", "d1", "d0", "d1", "d0"])
check("3.2 run on 0001: d0 d1 d2 dead dead", D32.run("0001") == ["d0", "d1", "d2", "dead", "dead"])
Leq = lambda w: w.count("0") == w.count("1")
check("3.2(b) {#0 = #1}: 0^i / 0^j distinguished by 1^i (i != j <= 12)",
      all(distinguishes("1" * i, "0" * i, "0" * j, Leq) for i in range(13) for j in range(13) if i != j))

# ====================================================================== 3.3 prefixes of 0110
print("--- 3.3")
L33 = lambda w: "0110" in w
P = "0110"
F33 = ["", "0", "01", "011", "0110"]
ok = True
for i in range(5):
    for j in range(i + 1, 5):
        z = P[j:]                                     # the last 4 - j symbols of P
        ok = ok and L33(F33[j] + z) and not L33(F33[i] + z) and len(F33[i] + z) < 4
check("3.3(a) prefixes of 0110: for |x| < |y|, z = rest of 0110 after y; yz = 0110 in L, |xz| < 4 so xz not", ok)
check("3.3(a) example: z = 10 distinguishes 0 and 01 (010 not in L, 0110 in L)", not L33("010") and L33("0110"))
K33 = table({"e": ("0", "e"), "0": ("0", "01"), "01": ("0", "011"), "011": ("found", "e"),
             "found": ("found", "found")}, "e", ["found"])
exact(K33, L33, 16, "3.3 five-state DFA for 'contains 0110'")
check("3.3 minimal DFA for 'contains 0110' has 5 states", len(K33.minimize().states) == 5)
check("3.3(b) 0110 and 01101: every extension of both is in L (|z| <= 10), so no suffix distinguishes them",
      all(L33("0110" + z) and L33("01101" + z) for z in strings("01", 10)))
check("3.3(b) no 6-string fooling set: the 6 strings of (b) are not a fooling set",
      not is_fooling(F33 + ["01101"], L33, maxlen=10))

# ====================================================================== 3.4 the forgotten branch
print("--- 3.4")


def L34(w):
    a = len(w) - len(w.lstrip("0"))
    rest = w[a:]
    if set(rest) - {"1"}:
        return False
    b = len(rest)
    return b == a or b == 2 * a


check("3.4(a) x = 00, y = 0, z = 11: 0011 in L and 011 in L", L34("0011") and L34("011"))
fails = [(i, j) for i in range(0, 31) for j in range(0, 31)
         if i != j and not distinguishes("1" * i, "0" * i, "0" * j, L34)]
check("3.4(a) z = 1^i fails exactly for the pairs with i = 2j (i != j <= 30)",
      bool(fails) and all(i == 2 * j for i, j in fails) and len(fails) == len([j for j in range(1, 16)]), str(fails[:4]))
check("3.4(a) xz = 0^i 1^i is always in L", all(L34("0" * i + "1" * i) for i in range(31)))
odd = [i for i in range(1, 32, 2)]
check("3.4(b) fix 1: F = 0(00)*, z = 1^i: xz in L and yz not, for all odd i != j <= 31",
      all(L34("0" * i + "1" * i) and not L34("0" * j + "1" * i) for i in odd for j in odd if i != j))
ok = True
for i in range(31):
    for j in range(31):
        if i == j:
            continue
        if i != 2 * j:
            ok = ok and L34("0" * i + "1" * i) and not L34("0" * j + "1" * i)
        else:
            ok = ok and j >= 1 and L34("0" * j + "1" * j) and not L34("0" * i + "1" * j)
check("3.4(b) fix 2: F = 0*, z = 1^i unless i = 2j, then z = 1^j (all i != j <= 30)", ok)
check("3.4 x = 00, y = 0 are still distinguishable (by z = 1: 001 not in L, 01 in L)",
      not L34("001") and L34("01"))

# ====================================================================== 3.5 DFA proof, #01 even
print("--- 3.5")
L35 = lambda w: occ("01", w) % 2 == 0
M35 = table({"A": ("B", "A"), "B": ("B", "C"), "C": ("D", "C"), "D": ("D", "A")}, "A", ["A", "B"])
exact(M35, L35, 16, "3.5 the given DFA vs {#(01,w) even}")


def meaning35(w):
    even = occ("01", w) % 2 == 0
    end0 = w.endswith("0")
    return {(True, False): "A", (True, True): "B", (False, False): "C", (False, True): "D"}[(even, end0)]


check("3.5 meanings: delta*(A,w) is the state whose property w has (|w| <= 14)",
      all(M35.delta_star("A", w) == meaning35(w) for w in strings("01", 14)))
check("3.5 fact: #(01,xa) = #(01,x) + [x ends in 0 and a = 1] (|x| <= 12)",
      all(occ("01", x + a) == occ("01", x) + (x.endswith("0") and a == "1") for x in strings("01", 12) for a in "01"))
ok = True
for q, rep in [("A", ""), ("A", "1"), ("B", "0"), ("C", "01"), ("D", "010")]:
    for a in "01":
        ok = ok and meaning35(rep) == q and M35.delta(q, a) == meaning35(rep + a)
check("3.5 the eight cases of the table (representatives of each property)", ok)
check("3.5 additivity fails at the seam: #(01, 0.1) = 1 > 0 + 0", occ("01", "01") == 1 > occ("01", "0") + occ("01", "1"))
check("3.5 check: 00110 has one 01, run A B B C C D, reject",
      occ("01", "00110") == 1 and M35.run("00110") == list("ABBCCD") and not M35.accepts("00110"))
check("3.5 check: 0101 has two 01s, run A B C D A, accept",
      occ("01", "0101") == 2 and M35.run("0101") == list("ABCDA") and M35.accepts("0101"))

# ====================================================================== 3.6 product construction
print("--- 3.6")
L1 = lambda w: w.startswith("1")
L2 = lambda w: w.count("1") % 2 == 0
M1 = table({"new": ("bad", "good"), "good": ("good", "good"), "bad": ("bad", "bad")}, "new", ["good"])
M2 = table({"even": ("even", "odd"), "odd": ("odd", "even")}, "even", ["even"])
exact(M1, L1, 14, "3.6 M1 (starts with 1)")
exact(M2, L2, 14, "3.6 M2 (even number of 1s)")
Pr = M1.product(M2, "and")
exact(Pr, lambda w: L1(w) and L2(w), 14, "3.6 product with A = {(good, even)}")
check("3.6 product: Q has 6 states, accepting set {(good, even)}",
      len(Pr.states) == 6 and Pr.accepting == {("good", "even")})
check("3.6 reachable: 5 states, (new, odd) is the unreachable one",
      len(Pr.reachable()) == 5 and set(Pr.states) - Pr.reachable() == {("new", "odd")})
expect_rows = {("new", "even"): (("bad", "even"), ("good", "odd")),
               ("good", "even"): (("good", "even"), ("good", "odd")),
               ("good", "odd"): (("good", "odd"), ("good", "even")),
               ("bad", "even"): (("bad", "even"), ("bad", "odd")),
               ("bad", "odd"): (("bad", "odd"), ("bad", "even"))}
check("3.6 the transition table of the reachable part",
      all((Pr.delta(q, "0"), Pr.delta(q, "1")) == r for q, r in expect_rows.items()))
check("3.6 run on 1001 ends in (good, even), accept",
      Pr.run("1001") == [("new", "even"), ("good", "odd"), ("good", "odd"), ("good", "odd"), ("good", "even")]
      and Pr.accepts("1001"))
check("3.6 run on 0110 ends in (bad, even), reject",
      Pr.run("0110") == [("new", "even"), ("bad", "even"), ("bad", "odd"), ("bad", "even"), ("bad", "even")]
      and not Pr.accepts("0110"))
check("3.6 epsilon ends in (new, even) and is rejected", not Pr.accepts("") and not L1(""))
Aun = [("new", "even"), ("good", "even"), ("good", "odd"), ("bad", "even")]
Pun = DFA("01", Pr.states, Pr.start, Aun, Pr._delta)
exact(Pun, lambda w: L1(w) or L2(w), 14, "3.6(c) union accepting set as listed")
check("3.6(c) the listed union set equals {(p,q) : p = good or q = even}",
      set(Aun) == {(p, q) for (p, q) in Pr.states if p == "good" or q == "even"})
Pdf = DFA("01", Pr.states, Pr.start, [("good", "odd")], Pr._delta)
exact(Pdf, lambda w: L1(w) and not L2(w), 14, "3.6(c) difference accepting set {(good, odd)}")
mn = Pr.minimize()
classes = sorted(sorted(map(str, c)) for c in mn.states)
check("3.6(d) Moore merges exactly (bad, even) with (bad, odd); 4 states remain",
      len(mn.states) == 4 and [c for c in mn.states if len(c) > 1] == [frozenset({("bad", "even"), ("bad", "odd")})],
      str(classes))
check("3.6(d) for the union the two bad states are distinguishable (epsilon)",
      ("bad", "even") in Pun.accepting and ("bad", "odd") not in Pun.accepting)

# ====================================================================== 3.7 {ww}
print("--- 3.7")
Lww = lambda w: len(w) % 2 == 0 and w[:len(w) // 2] == w[len(w) // 2:]
R = range(0, 16)
check("3.7 F = 0*1, z = x: xz = (0^i 1)^2 in L, yz = 0^j 1 0^i 1 not in L (all i != j <= 15)",
      all(Lww(("0" * i + "1") * 2) and not Lww("0" * j + "1" + "0" * i + "1") for i in R for j in R if i != j))
check("3.7 check: 0101 in L; 00101 and 000101 not", Lww("0101") and not Lww("00101") and not Lww("000101"))
bad = [(i, j) for i in R for j in R if i != j and not distinguishes("0" * i, "0" * i, "0" * j, Lww)]
check("3.7 watch out: with F = 0* and z = x, the suffix fails exactly when i + j is even",
      bool(bad) and all((i + j) % 2 == 0 for i, j in bad) and len(bad) == sum(1 for i in R for j in R if i != j and (i + j) % 2 == 0))
check("3.7 watch out: F = 0* with z = 1 0^i 1 works (all i != j <= 15)",
      all(Lww("0" * i + "1" + "0" * i + "1") and not Lww("0" * j + "1" + "0" * i + "1") for i in R for j in R if i != j))
check("3.7 a string of L with exactly two 1s and ending in 1 is 0^k 1 0^k 1 (|w| <= 16)",
      all(w == ("0" * ((len(w) - 2) // 2) + "1") * 2 for w in strings("01", 16)
          if Lww(w) and w.count("1") == 2 and w.endswith("1")))

# ====================================================================== 3.8 no 00 after an 11
print("--- 3.8")


def L38(w):
    """no substring 11 x 00: no 00 starting at least two positions after the start of a 11"""
    starts11 = [p for p in range(len(w) - 1) if w[p:p + 2] == "11"]
    starts00 = [q for q in range(len(w) - 1) if w[q:q + 2] == "00"]
    return not any(q >= p + 2 for p in starts11 for q in starts00)


for w, want in [("0010110", True), ("110101", True), ("0110100", False), ("", True), ("110", True), ("1100", False)]:
    check(f"3.8 example {w!r} in L is {want}", L38(w) == want)
M38 = table({"before": ("before", "before1"), "before1": ("before", "after1"), "after1": ("after0", "after1"),
             "after0": ("dead", "after1"), "dead": ("dead", "dead")}, "before",
            ["before", "before1", "after1", "after0"])
exact(M38, L38, 16, "3.8(a) five-state DFA")
check("3.8(a) the DFA is minimal (5 states)", len(M38.minimize().states) == 5)


def meaning38(w):
    if not L38(w):
        return "dead"
    if "11" not in w:
        return "before1" if w.endswith("1") else "before"
    return "after1" if w.endswith("1") else "after0"


check("3.8(a) state meanings hold for every w with |w| <= 14",
      all(M38.delta_star("before", w) == meaning38(w) for w in strings("01", 14)))
check("3.8(a) run on 0010110 ends in after0, accept", M38.run("0010110")[-1] == "after0" and M38.accepts("0010110"))
check("3.8(a) run on 0110100: before before before1 after1 after0 after1 after0 dead",
      M38.run("0110100") == ["before", "before", "before1", "after1", "after0", "after1", "after0", "dead"])
R38 = Regex("(0+10)*(1+01)*(ε+0)", "01")
ok, wit = R38.equivalent(M38)
check("3.8(b) (0+10)*(1+01)*(ε+0) is equivalent to the DFA", ok, f"witness {wit!r}")
ok, wit = R38.equivalent(Regex("(0+1)*11(0+1)*00(0+1)*", "01").dfa().complement())
check("3.8(b) the expression equals the complement of (0+1)*11(0+1)*00(0+1)*", ok, f"witness {wit!r}")
exact(R38.dfa(), L38, 14, "3.8(b) the expression vs the predicate")
check("3.8(b) the parts: (0+10)* = no 11 and not ending in 1 (|w| <= 12)",
      first_difference(Regex("(0+10)*", "01").matches, lambda w: "11" not in w and not w.endswith("1"), "01", 12) is None)
check("3.8(b) the parts: (1+01)*(ε+0) = no 00 (|w| <= 12)",
      first_difference(Regex("(1+01)*(ε+0)", "01").matches, lambda w: "00" not in w, "01", 12) is None)
W38 = Regex("(0+10)*(1+01)*", "01")
missed = [("1" * k + "0") for k in range(2, 12) if L38("1" * k + "0") and not W38.matches("1" * k + "0")]
check("3.8 watch out: (0+10)*(1+01)* misses 110, 1110, ... (infinitely many: 1^k 0 for every k >= 2)",
      len(missed) == 10 and missed[0] == "110")
check("3.8 the decomposition of 0010110 (0010 . 11 . 0) and 110101 (eps . 110101 . eps)",
      Regex("(0+10)*", "01").matches("0010") and Regex("(1+01)*", "01").matches("11")
      and Regex("(1+01)*", "01").matches("110101"))
check("3.8 the expression matches 0010110 and 110101 but not 0110100",
      R38.matches("0010110") and R38.matches("110101") and not R38.matches("0110100"))
check("3.8 the DFA is in after1 after reading 011 (of 0110100)", M38.delta_star("before", "011") == "after1")

# ====================================================================== 3.9 three look-alike languages
print("--- 3.9")
check("3.9 #(00, 000) = 2 (overlapping occurrences count)", occ("00", "000") == 2)
La = lambda w: occ("00", w) == occ("11", w)
Lb = lambda w: occ("01", w) == occ("10", w)
Lcc = lambda w: occ("01", w) == occ("11", w)
in01 = lambda w: w == "0" * w.count("0") + "1" * w.count("1")
check("3.9(a) La cap 0*1* = {0^n1^n} + {0, 1} (|w| <= 16)",
      all((La(w) and in01(w)) == (L0n1n(w) or w in ("0", "1")) for w in strings("01", 16)))
check("3.9(a) in 0^a 1^b: #00 = max(a-1,0), #11 = max(b-1,0) (a, b <= 12)",
      all(occ("00", "0" * a + "1" * b) == max(a - 1, 0) and occ("11", "0" * a + "1" * b) == max(b - 1, 0)
          for a in range(13) for b in range(13)))
check("3.9(a) aside: F = 0*, z = 1^i fails for x = eps, y = 0 (both in La)", La("") and La("0"))
check("3.9(a) aside: F = {0^i : i >= 1}, z = 1^i works (all i != j in 1..14)",
      all(La("0" * i + "1" * i) and not La("0" * j + "1" * i) for i in range(1, 15) for j in range(1, 15) if i != j))
Rb = Regex("ε+0+1+0(0+1)*0+1(0+1)*1", "01")
exact(Rb.dfa(), Lb, 16, "3.9(b) ε+0+1+0(0+1)*0+1(0+1)*1 vs #01 = #10")
check("3.9(b) #01 = #10 iff w is empty or starts and ends with the same symbol (|w| <= 16)",
      all(Lb(w) == (w == "" or w[0] == w[-1]) for w in strings("01", 16)))


def runs(w):
    r = []
    for c in w:
        if r and r[-1][0] == c:
            r[-1] += c
        else:
            r.append(c)
    return r


check("3.9(b) the 01/10 occurrences are exactly the k-1 seams between runs, alternating (|w| <= 14)",
      all(occ("01", w) + occ("10", w) == len(runs(w)) - 1 and abs(occ("01", w) - occ("10", w)) <= 1
          for w in strings("01", 14, 1)))
check("3.9(b) check: 0110 has one 01 and one 10 (in L_b); 011 has one 01 and no 10 (not in L_b)",
      (occ("01", "0110"), occ("10", "0110")) == (1, 1) and (occ("01", "011"), occ("10", "011")) == (1, 0)
      and Lb("0110") and not Lb("011"))
check("3.9(b) runs of 0110 are 0 . 11 . 0", runs("0110") == ["0", "11", "0"])
ok = True
for i in range(1, 15):
    for j in range(1, 15):
        if i != j:
            z = "01" * (i - 1)
            x, y = "1" * i, "1" * j
            ok = ok and Lcc(x + z) and not Lcc(y + z) and occ("11", y + z) == j - 1 and occ("01", y + z) == i - 1
check("3.9(c) F = 1^+, z = (01)^(i-1): xz has i-1 of each, yz has j-1 11s and i-1 01s (i != j in 1..14)", ok)
check("3.9(c) 0^i and 0^j (1 <= i, j <= 6) are not distinguished by any suffix of length <= 10",
      all(Lcc("0" * i + z) == Lcc("0" * j + z) for i in range(1, 7) for j in range(1, 7) for z in strings("01", 10)))
check("3.9(c) the extra 0s change neither count: #01, #11 of 0^i z equal those of 0z (i <= 5, |z| <= 8)",
      all((occ("01", "0" * i + z), occ("11", "0" * i + z)) == (occ("01", "0" + z), occ("11", "0" + z))
          for i in range(1, 6) for z in strings("01", 8)))
check("3.9(c) check: 1101 has one 11 and one 01; 11101 has two 11s and one 01",
      (occ("11", "1101"), occ("01", "1101")) == (1, 1) and (occ("11", "11101"), occ("01", "11101")) == (2, 1))

# ====================================================================== 3.10 Moore's algorithm
print("--- 3.10")
M10 = table({"A": ("D", "B"), "B": ("C", "B"), "C": ("D", "E"), "D": ("A", "B"), "E": ("G", "E"),
             "G": ("G", "E"), "H": ("A", "C")}, "A", ["E", "G"])
check("3.10(a) the reachable states are A, B, C, D, E, G; H is unreachable",
      M10.reachable() == set("ABCDEG"))
check("3.10(a) no transition enters H", all(M10.delta(q, a) != "H" for q in M10.states for a in "01"))


def moore_jacobi(M, states):
    """Moore's passes as stated on the page: pass k uses only marks made before pass k began."""
    pairs = [frozenset((p, q)) for i, p in enumerate(states) for q in states[i + 1:]]
    marked = {pq for pq in pairs if len({x in M.accepting for x in pq}) == 2}
    passes = [set(marked)]
    while True:
        new = set()
        for pq in pairs:
            if pq in marked:
                continue
            p, q = sorted(pq)
            if any(M.delta(p, a) != M.delta(q, a) and frozenset((M.delta(p, a), M.delta(q, a))) in marked
                   for a in M.alphabet):
                new.add(pq)
        passes.append(new)
        if not new:
            return passes, marked
        marked |= new


def names(S):
    return sorted("".join(sorted(pq)) for pq in S)


passes, marked = moore_jacobi(M10, list("ABCDEG"))
check("3.10(b) initial marks: the 8 pairs between {A,B,C,D} and {E,G}",
      names(passes[0]) == sorted(x + y for x in "ABCD" for y in "EG"), str(names(passes[0])))
check("3.10(b) pass 1 marks AC, BC, CD", names(passes[1]) == ["AC", "BC", "CD"], str(names(passes[1])))
check("3.10(b) pass 2 marks AB, BD", names(passes[2]) == ["AB", "BD"], str(names(passes[2])))
check("3.10(b) pass 3 marks nothing, and it is the last pass", len(passes) == 4 and not passes[3])
check("3.10(b) unmarked at the end: AD and EG",
      sorted("".join(sorted(pq)) for pq in {frozenset((p, q)) for i, p in enumerate("ABCDEG") for q in "ABCDEG"[i + 1:]} - marked)
      == ["AD", "EG"])


def shortest_dist(M, p, q):
    """BFS over pairs for the shortest string that leads exactly one of p, q to acceptance."""
    seen, queue = {(p, q): ""}, deque([(p, q)])
    while queue:
        r, s = queue.popleft()
        if (r in M.accepting) != (s in M.accepting):
            return seen[(r, s)]
        for a in M.alphabet:
            nxt = (M.delta(r, a), M.delta(s, a))
            if nxt not in seen:
                seen[nxt] = seen[(r, s)] + a
                queue.append(nxt)
    return None


ok = True
for k, S in enumerate(passes):
    for pq in S:
        p, q = sorted(pq)
        z = shortest_dist(M10, p, q)
        ok = ok and z is not None and len(z) == k
check("3.10(b) pass k marks exactly the pairs whose shortest distinguishing string has length k", ok)
check("3.10(b) AD and EG are indistinguishable", shortest_dist(M10, "A", "D") is None and shortest_dist(M10, "E", "G") is None)
check("3.10 check: '1' distinguishes A and C; '01' distinguishes A and B and no single symbol does",
      shortest_dist(M10, "A", "C") == "1" and M10.delta_star("A", "01") == "B" and M10.delta_star("B", "01") == "E"
      and len(shortest_dist(M10, "A", "B")) == 2)
mn10 = M10.minimize()
check("3.10(c) the library's minimization gives the classes {A,D}, {B}, {C}, {E,G}",
      sorted(sorted(c) for c in mn10.states) == [["A", "D"], ["B"], ["C"], ["E", "G"]])
Min10 = table({"AD": ("AD", "B"), "B": ("C", "B"), "C": ("AD", "EG"), "EG": ("EG", "EG")}, "AD", ["EG"])
ok, wit = Min10.equivalent(M10)
check("3.10(c) the 4-state table is equivalent to M", ok, f"witness {wit!r}")
L101 = lambda w: "101" in w
exact(M10, L101, 14, "3.10(c) M accepts exactly the strings containing 101")


def meaning10(w):
    if "101" in w:
        return "EG"
    if w.endswith("1"):
        return "B"
    if w.endswith("10"):
        return "C"
    return "AD"


check("3.10(c) meanings of AD, B, C, EG (|w| <= 14)", all(Min10.delta_star("AD", w) == meaning10(w) for w in strings("01", 14)))
S10 = ["", "1", "10", "101"]
sufs = {("", "1"): "01", ("", "10"): "1", ("1", "10"): "1", ("", "101"): "", ("1", "101"): "", ("10", "101"): ""}
check("3.10(d) the listed suffixes distinguish all 6 pairs of {eps, 1, 10, 101} (yz in L, xz not)",
      all(L101(y + z) and not L101(x + z) for (x, y), z in sufs.items()))
check("3.10(d) {eps, 1, 10, 101} is a fooling set, and 4 = minimal number of states",
      is_fooling(S10, L101) and len(mn10.states) == 4)


def moore_gauss_seidel(M, states):
    """Variant: marks made earlier in the same pass count immediately (pairs in alphabetical order)."""
    pairs = [frozenset((p, q)) for i, p in enumerate(states) for q in states[i + 1:]]
    marked = {pq: 0 for pq in pairs if len({x in M.accepting for x in pq}) == 2}
    k = 0
    while True:
        k += 1
        changed = False
        for pq in pairs:
            if pq in marked:
                continue
            p, q = sorted(pq)
            if any(M.delta(p, a) != M.delta(q, a) and frozenset((M.delta(p, a), M.delta(q, a))) in marked
                   for a in M.alphabet):
                marked[pq] = k
                changed = True
        if not changed:
            return marked


gs = moore_gauss_seidel(M10, list("ABCDEG"))
check("3.10 watch out: counting same-pass marks, {B,D} is marked in pass 1 (alphabetical order)",
      gs[frozenset("BD")] == 1)
check("3.10 watch out: ... but the final partition is the same",
      set(gs) == marked)
passes_all, marked_all = moore_jacobi(M10, list("ABCDEGH"))
unm = {frozenset((p, q)) for i, p in enumerate("ABCDEGH") for q in "ABCDEGH"[i + 1:]} - marked_all
check("3.10 watch out: without deleting H, H is equivalent to no state (5 classes instead of 4)",
      all("H" not in pq for pq in unm) and sorted("".join(sorted(pq)) for pq in unm) == ["AD", "EG"])

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: {FAIL}")
sys.exit(1 if FAIL else 0)
