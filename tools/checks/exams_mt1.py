#!/usr/bin/env python3
"""Checks for the Midterm 1 practice-test pages (content/3-homework-and-exams/midterm-1-practice-N.md).

One shared script: each writer appends a clearly marked section for their test, using check(name, cond, detail).
Every predicate is written from the problem statement, independently of the answers on the pages. Regular
languages are compared exactly (DFA equivalence) where possible; everything else by brute force over all short
strings. Run:  python3 tools/checks/exams_mt1.py | tee tools/checks/exams_mt1.out   — it must end with ALL OK."""
import atexit
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from automata import CFG, DFA, EPS, NFA, Regex, first_difference, strings  # noqa: E402

FAIL = []


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAIL.append(name)


def _summary():
    """Printed after every section has run (so sections can be appended in any order)."""
    print()
    if FAIL:
        print(f"{len(FAIL)} FAILED: " + ", ".join(FAIL))
        os._exit(1)
    print("ALL OK")


atexit.register(_summary)


AB = "01"


def R(text):
    return Regex(text, alphabet=AB)


def random_dfa(rng, n):
    """A random DFA with n states over {0,1}: start state 0, every state accepting with probability 1/2."""
    delta = {(q, a): rng.randrange(n) for q in range(n) for a in AB}
    acc = [q for q in range(n) if rng.random() < 0.5]
    return DFA(AB, list(range(n)), 0, acc, delta)


def runs(w):
    """The maximal runs of w as (symbol, length) pairs."""
    out = []
    for c in w:
        if out and out[-1][0] == c:
            out[-1][1] += 1
        else:
            out.append([c, 1])
    return [(c, k) for c, k in out]


# =====================================================================================================
# Practice test 1  (content/3-homework-and-exams/midterm-1-practice-1.md)
# =====================================================================================================
print("---- Practice test 1")

# ------------------------------------------------------------------ Problem 1: true/false
zero_n_one_n = lambda w: w == "0" * (len(w) // 2) + "1" * (len(w) // 2)  # noqa: E731

# (a)/(c)/(f): 0^n1^n is not regular — fooling set 0^* with suffix 1^i; the empty set is a subset of it.
check("P1(a) 0^n1^n: 0^i and 0^j are distinguished by 1^i (i != j <= 9)",
      all(zero_n_one_n("0" * i + "1" * i) and not zero_n_one_n("0" * j + "1" * i)
          for i in range(10) for j in range(10) if i != j))
check("P1(a) 0^n1^n is infinite", all(zero_n_one_n("0" * n + "1" * n) for n in range(12)))
# (b): the expression parses as a regular expression, so its language is regular (and hence context-free).
rb = R("(0+1(01*0)*1)*")
check("P1(b) (0+1(01*0)*1)* is a regular expression; its minimal DFA has a few states",
      rb.dfa().num_states() <= 8, f"{rb.dfa().num_states()} states")
# (d): {0^a 1^b : m | a-b} = union_r (0^m)* 0^r 1^r (1^m)*  — exact for small m, brute force for m = 374
def div_lang(m):
    def pred(w):
        a = len(w) - len(w.lstrip("0"))
        return w == "0" * a + "1" * (len(w) - a) and (a - (len(w) - a)) % m == 0
    return pred


def div_union(m):
    return "+".join(f"(0{'0' * (m - 1)})*{'0' * r}{'1' * r}(1{'1' * (m - 1)})*" for r in range(m))


for m in (1, 2, 3, 4, 5):
    dfa_m = DFA.explore(AB, ("zeros", 0), lambda q, a, m=m: (("zeros", (q[1] + 1) % m) if a == "0" and q[0] == "zeros"
                                                            else ("ones", (q[1] - 1) % m) if a == "1" and q[0] != "dead"
                                                            else ("dead", 0)),
                        lambda q: q[0] != "dead" and q[1] == 0)
    check(f"P1(d) m={m}: DFA for {{0^a1^b : m | a-b}} matches the definition up to length 12",
          first_difference(dfa_m, div_lang(m), AB, 12) is None)
    eq, cex = R(div_union(m)).equivalent(dfa_m)
    check(f"P1(d) m={m}: union_r (0^m)* 0^r 1^r (1^m)* equals that language exactly", eq, str(cex))
check("P1(d) m=374: up to length 14 the language is {0^r 1^r : r <= 7}, as the union predicts (p = q = 0)",
      first_difference(div_lang(374), lambda w: any(w == "0" * r + "1" * r for r in range(374)), AB, 14) is None)
# (g): complementing a DFA keeps its state count
rng = random.Random(374)
check("P1(g) complement of a DFA has the same number of states and the complementary language",
      all((d.complement().num_states() == d.num_states()
           and first_difference(d.complement(), lambda w, d=d: not d(w), AB, 8) is None)
          for d in (random_dfa(rng, rng.randrange(2, 6)) for _ in range(20))))
# (h): 10 and 1100 are not distinguished by any suffix for L = {1^i 0^(i+j) 1^j}
def ioj(w):
    """{1^i 0^(i+j) 1^j}: at most three runs, 1s then 0s then 1s, with #0 = #1 overall."""
    rs = runs(w)
    pattern = "".join(c for c, n in rs)
    return pattern in ("", "1", "0", "10", "01", "101") and w.count("0") == w.count("1") and (
        pattern != "0" or w == "")


def ioj_def(w):
    return any(w == "1" * i + "0" * (i + j) + "1" * j for i in range(len(w) + 1) for j in range(len(w) + 1))


check("P1(h) the run-based predicate for {1^i 0^(i+j) 1^j} agrees with the definition up to length 12",
      first_difference(ioj, ioj_def, AB, 12) is None)
check("P1(h) no suffix z (|z| <= 10) distinguishes 10 and 1100",
      all(ioj("10" + z) == ioj("1100" + z) for z in strings(AB, 10)))
check("P1(h) 10z in L iff z = 0^j1^j (|z| <= 10)",
      all(ioj("10" + z) == zero_n_one_n(z) for z in strings(AB, 10)))
check("P1(h) but 1^*0^* is not trivially a fooling set: some pairs ARE distinguished (1 vs 11 by 0)",
      ioj("1" + "0") != ioj("11" + "0"))
# (i): adding an unreachable accepting state does not change the language
def add_unreachable(d):
    new = ("extra",)
    delta = dict(d._delta)
    delta[(new, "0")] = new
    delta[(new, "1")] = new
    return DFA(AB, d.states + [new], d.start, list(d.accepting) + [new], delta)


check("P1(i) adding an unreachable accepting state with self-loops keeps the language",
      all(add_unreachable(d).equivalent(d) and len(add_unreachable(d).accepting) == len(d.accepting) + 1
          for d in (random_dfa(rng, rng.randrange(2, 6)) for _ in range(20))))
# (j): the grammar generates exactly the strings with an even number of 0s
Gj = CFG.parse("S -> ε | 0A | 1S\nA -> 0S | 1A")
check("P1(j) S -> ε | 0A | 1S, A -> 0S | 1A generates exactly the strings with an even number of 0s (<= 12)",
      first_difference(Gj, lambda w: w.count("0") % 2 == 0, AB, 12) is None)
check("P1(j) A generates exactly the strings with an odd number of 0s (<= 12)",
      first_difference(lambda w: Gj.generates(w, "A"), lambda w: w.count("0") % 2 == 1, AB, 12) is None)

# ------------------------------------------------------------------ Problem 2: Inserted1st / Deleted1st
def delete1st(w):
    assert w != ""
    return w.lstrip(w[0])


def other(a):
    return "1" if a == "0" else "0"


def inserted1st_dfa(M):
    """The DFA of answer (a), built from an arbitrary DFA M = (Q, s, A, delta)."""
    S, F0, F1 = ("s'",), ("f", "0"), ("f", "1")
    Q = [S, F0, F1] + list(M.states)
    acc = set(M.accepting) | ({F0, F1} if M.start in M.accepting else set())
    delta = {}
    for a in AB:
        fa = ("f", a)
        delta[(S, a)] = fa
        delta[(fa, a)] = fa
        delta[(fa, other(a))] = M.delta(M.start, other(a))
        for q in M.states:
            delta[(q, a)] = M.delta(q, a)
    return DFA(AB, Q, S, acc, delta)


def deleted1st_nfa(M):
    """The NFA of answer (b), built from an arbitrary DFA M."""
    S = ("s'",)
    Q = [S] + [(q, a) for q in M.states for a in AB] + list(M.states)
    acc = {(q, a) for q in M.accepting for a in AB} | set(M.accepting)
    delta = {}
    delta[(S, EPS)] = {(M.delta(M.start, a), a) for a in AB}
    for q in M.states:
        for a in AB:
            delta[((q, a), EPS)] = {(M.delta(q, a), a)}
            delta[((q, a), other(a))] = {M.delta(q, other(a))}
            delta[(q, a)] = {M.delta(q, a)}
    return NFA(AB, Q, S, acc, delta)


def inserted1st_def(L, maxlen):
    return lambda w: w != "" and L(delete1st(w))


def deleted1st_def(L, maxlen):
    # Delete1st(w) for w in L, w != ε, |w| <= maxlen + 1 covers every u of length <= maxlen?  No: the deleted run
    # may be arbitrarily long, so check |w| <= maxlen + extra. With |Q| <= 5, a^k for k > 5 repeats states
    # (pigeonhole on the states reached by a^k), so k <= |Q| + 1 suffices; we use extra = 8 to be safe.
    def pred(u):
        return any(L(a * k + u) for a in AB for k in range(1, 9) if u == "" or u[0] != a)
    return pred


rng = random.Random(2026)
ok_a = ok_b = True
bad_a = bad_b = None
for trial in range(300):
    M = random_dfa(rng, rng.randrange(1, 5))
    cx = first_difference(inserted1st_dfa(M), inserted1st_def(M, 8), AB, 8)
    if cx is not None:
        ok_a, bad_a = False, (M, cx)
    cx = first_difference(deleted1st_nfa(M), deleted1st_def(M, 8), AB, 8)
    if cx is not None:
        ok_b, bad_b = False, (M, cx)
check("P2(a) Inserted1st construction equals the definition on 300 random DFAs (1-4 states), |w| <= 8",
      ok_a, str(bad_a))
check("P2(b) Deleted1st construction equals the definition on 300 random DFAs (1-4 states), |u| <= 8",
      ok_b, str(bad_b))
check("P2 Delete1st(100110) = 00110", delete1st("100110") == "00110")
# edge cases named in the exam note
eps_dfa = DFA(AB, ["s", "d"], "s", ["s"], {("s", "0"): "d", ("s", "1"): "d", ("d", "0"): "d", ("d", "1"): "d"})
eq, cex = R("00*+11*").equivalent(inserted1st_dfa(eps_dfa))
check("P2(a) Inserted1st({ε}) = 0^+ + 1^+", eq, str(cex))
check("P2(b) Deleted1st({ε}) = ∅", first_difference(deleted1st_nfa(eps_dfa), lambda w: False, AB, 8) is None)
empty_dfa = DFA(AB, ["d"], "d", [], {("d", "0"): "d", ("d", "1"): "d"})
check("P2 both constructions give ∅ for L = ∅",
      first_difference(inserted1st_dfa(empty_dfa), lambda w: False, AB, 8) is None
      and first_difference(deleted1st_nfa(empty_dfa), lambda w: False, AB, 8) is None)
ones_dfa = R("1*").dfa()
check("P2(a) Inserted1st(1*) = 0^+ + 1^+ 0^+ ... i.e. w != ε with Delete1st(w) in 1*: exact check",
      first_difference(inserted1st_dfa(ones_dfa), lambda w: w != "" and set(delete1st(w)) <= {"1"}, AB, 10) is None)
check("P2(b) Deleted1st(1*) = {ε}", first_difference(deleted1st_nfa(ones_dfa), lambda w: w == "", AB, 10) is None)
sigma_dfa = R("(0+1)*").dfa()
check("P2 for L = Σ*: Inserted1st = Σ^+ and Deleted1st = Σ*",
      first_difference(inserted1st_dfa(sigma_dfa), lambda w: w != "", AB, 10) is None
      and first_difference(deleted1st_nfa(sigma_dfa), lambda w: True, AB, 10) is None)

# ------------------------------------------------------------------ Problem 3: squish
def squish(w):
    if len(w) <= 1:
        return w
    return ("0" if w[0] == w[1] else "1") + squish(w[2:])


ones = lambda w: w.count("1")  # noqa: E731
check("P3(a) #1(squish(w)) <= #1(w) for all |w| <= 12", all(ones(squish(w)) <= ones(w) for w in strings(AB, 12)))
check("P3(b) #1(squish(w)) mod 2 = #1(w) mod 2 for all |w| <= 12",
      all(ones(squish(w)) % 2 == ones(w) % 2 for w in strings(AB, 12)))
check("P3 the three cases of the definition are exhaustive and exclusive (checked on the recursion above)",
      squish("00") == "0" and squish("11") == "0" and squish("01") == "1" and squish("10") == "1"
      and squish("") == "" and squish("0") == "0" and squish("1") == "1")
check("P3 the inequality in (a) can be strict (so <= is the right claim)", ones(squish("11")) < ones("11"))

# ------------------------------------------------------------------ Problem 4: shorter run of 1s after every run of 0s
def in_L4(w):
    rs = runs(w)
    for k, (c, n) in enumerate(rs):
        if c == "0":
            if k + 1 >= len(rs):
                return False
            if not (1 <= rs[k + 1][1] < n):
                return False
    return True


check("P4 sanity: ε, 1, 111, 001, 10001, 1000110001, 0001001 in L; 0, 01, 0011, 10, 000100, 00010011 not",
      all(in_L4(w) for w in ("", "1", "111", "001", "10001", "1000110001", "0001001"))
      and not any(in_L4(w) for w in ("0", "01", "0011", "10", "000100", "00010011")))
check("P4(a) fooling set 0^+ with z = 1^i: 0^i1^i not in L and 0^j1^i in L for all 1 <= i < j <= 9",
      all((not in_L4("0" * i + "1" * i)) and in_L4("0" * j + "1" * i) for i in range(1, 10) for j in range(i + 1, 10)))
check("P4(a) the suffix works in both directions (i > j too, with z = 1^min)",
      all(in_L4("0" * i + "1" * j) and not in_L4("0" * j + "1" * j) for j in range(1, 10) for i in range(j + 1, 10)))
check("P4(a) note: with F = 0^* and i = 0, xz = ε in L and yz = 0^j not in L (roles flip)",
      in_L4("") and not any(in_L4("0" * j) for j in range(1, 8)))
G4 = CFG.parse("S -> 1S | T\nT -> ε | RT\nR -> 0R1 | 0Z1\nZ -> 0 | 0Z")
check("P4(b) the grammar generates exactly L (all strings up to length 12)",
      first_difference(G4, in_L4, AB, 12) is None, str(first_difference(G4, in_L4, AB, 12)))
block = lambda w: (len(runs(w)) == 2 and runs(w)[0][0] == "0" and 1 <= runs(w)[1][1] < runs(w)[0][1])  # noqa: E731
check("P4(b) R generates exactly the blocks 0^a1^b with 1 <= b < a (<= 12)",
      first_difference(lambda w: G4.generates(w, "R"), block, AB, 12) is None)
check("P4(b) Z generates exactly 0^+ (<= 12)",
      first_difference(lambda w: G4.generates(w, "Z"), lambda w: w != "" and set(w) == {"0"}, AB, 12) is None)
check("P4(b) T generates exactly the strings of L that do not start with 1 (<= 12)",
      first_difference(lambda w: G4.generates(w, "T"), lambda w: in_L4(w) and not w.startswith("1"), AB, 12) is None)

# ------------------------------------------------------------------ Problem 5: DFAs and regular expressions
# (a) no subsequence 010
def has_subseq(w, p):
    i = 0
    for c in w:
        if i < len(p) and c == p[i]:
            i += 1
    return i == len(p)


D5a = DFA(AB, ["e", "0", "01", "dead"], "e", ["e", "0", "01"],
          {("e", "1"): "e", ("e", "0"): "0", ("0", "0"): "0", ("0", "1"): "01", ("01", "1"): "01", ("01", "0"): "dead",
           ("dead", "0"): "dead", ("dead", "1"): "dead"})
check("P5(a) the 3-state DFA (+ dump) accepts exactly the strings without the subsequence 010 (<= 10)",
      first_difference(D5a, lambda w: not has_subseq(w, "010"), AB, 10) is None)
eq, cex = R("1*0*1*").equivalent(D5a)
check("P5(a) 1*0*1* equals the DFA exactly", eq, str(cex))
check("P5(a) the DFA is minimal with its dump state: 4 states", D5a.minimize().num_states() == 4)
check("P5(a) state meanings: the state after w is the longest prefix of 010 that is a subsequence of w",
      all(D5a.delta_star("e", w) == {0: "e", 1: "0", 2: "01", 3: "dead"}[max(k for k in range(4) if has_subseq(w, "010"[:k]))]
          for w in strings(AB, 10)))

# (b) at least two even-length runs of 1s
def two_even_runs(w):
    return sum(1 for c, n in runs(w) if c == "1" and n % 2 == 0) >= 2


states5b = ["N0", "O0", "E0", "N1", "O1", "E1", "done"]
d5b = {("N0", "0"): "N0", ("N0", "1"): "O0", ("O0", "0"): "N0", ("O0", "1"): "E0", ("E0", "1"): "O0", ("E0", "0"): "N1",
       ("N1", "0"): "N1", ("N1", "1"): "O1", ("O1", "0"): "N1", ("O1", "1"): "E1", ("E1", "1"): "O1", ("E1", "0"): "done",
       ("done", "0"): "done", ("done", "1"): "done"}
D5b = DFA(AB, states5b, "N0", ["E1", "done"], d5b)
check("P5(b) the 7-state DFA accepts exactly the strings with >= 2 even-length runs of 1s (<= 12)",
      first_difference(D5b, two_even_runs, AB, 12) is None, str(first_difference(D5b, two_even_runs, AB, 12)))
re5b = "(ε+(0+1)*0)11(11)*0(ε+(0+1)*0)11(11)*(ε+0(0+1)*)"
eq, cex = R(re5b).equivalent(D5b)
check("P5(b) the regular expression equals the DFA exactly", eq, str(cex))
check("P5(b) the DFA is minimal: 7 states", D5b.minimize().num_states() == 7)


def meaning5b(w):
    rs = runs(w)
    finished = [n for k, (c, n) in enumerate(rs) if c == "1" and k + 1 < len(rs)]
    k = sum(1 for n in finished if n % 2 == 0)
    if k >= 2:
        return "done"
    if w == "" or w[-1] == "0":
        return f"N{k}"
    return f"{'E' if rs[-1][1] % 2 == 0 else 'O'}{k}"


check("P5(b) state meanings: N/O/E and the subscript k as described (<= 12)",
      all(D5b.delta_star("N0", w) == meaning5b(w) for w in strings(AB, 12)))
check("P5(b) sanity: 110110 and 11011 accepted; 11, 1101, 1111 rejected",
      D5b("110110") and D5b("11011") and not D5b("11") and not D5b("1101") and not D5b("1111"))

# =====================================================================================================
# (end of Practice test 1 — later sections are appended below; the summary line is printed at exit)
# =====================================================================================================


# =====================================================================================================
# Practice test 2 — content/3-homework-and-exams/midterm-1-practice-2.md
# =====================================================================================================
print("\n--- practice test 2 ---")
from automata import language_upto  # noqa: E402
RNG2 = random.Random(374_2)


def p2_compress0s(w):
    out, i = [], 0
    while i < len(w):
        if w[i] == "1":
            out.append("1")
            i += 1
        else:
            j = i
            while j < len(w) and w[j] == "0":
                j += 1
            out.append("0" * ((j - i + 1) // 2))
            i = j
    return "".join(out)


check("P2.1 example: compress0s(00000110001) = 00011001", p2_compress0s("00000110001") == "00011001")
check("P2.1 compress0s halves runs: ceil(k/2) for k = 1..9",
      all(p2_compress0s("0" * k + "1") == "0" * ((k + 1) // 2) + "1" for k in range(1, 10)))


def p2_decompressed(M):
    """P2.1(a): the DFA M' built from an arbitrary DFA M."""
    Q = [(q, p) for q in M.states for p in (0, 1)]

    def d(st, a):
        q, p = st
        if a == "1":
            return (M.delta(q, "1"), 0)
        return (M.delta(q, "0"), 1) if p == 0 else (q, 0)
    return DFA(M.alphabet, Q, (M.start, 0), [(q, p) for q in M.accepting for p in (0, 1)], d)


def p2_compressed(M):
    """P2.1(b): the NFA M' (no ε-transitions) built from an arbitrary DFA M."""
    Q = [(q, b) for q in M.states for b in (False, True)]
    delta = {}
    for q in M.states:
        d0 = M.delta(q, "0")
        d00 = M.delta(d0, "0")
        delta[((q, False), "0")] = {(d0, True), (d00, True)}
        delta[((q, True), "0")] = {(d00, True)}
        for b in (False, True):
            delta[((q, b), "1")] = {(M.delta(q, "1"), False)}
    return NFA(M.alphabet, Q, (M.start, False), [(q, b) for q in M.accepting for b in (False, True)], delta)


ok_a = ok_b = True
bad_a = bad_b = ""
for trial in range(120):
    M = random_dfa(RNG2, RNG2.choice([2, 3, 4]))
    # (a) Decompressed(L) = {w : compress0s(w) in L}, exactly on |w| <= 8
    d = first_difference(p2_decompressed(M).accepts, lambda w: M.accepts(p2_compress0s(w)), "01", 8)
    if d is not None:
        ok_a, bad_a = False, f"trial {trial}: {d!r}"
    # (b) Compressed(L) = {compress0s(w) : w in L}; |compress0s(w)| >= |w|/2, so w up to 14 covers every u, |u| <= 7
    target = {p2_compress0s(w) for w in strings("01", 14) if M.accepts(w)}
    got = language_upto(p2_compressed(M).accepts, "01", 7)
    target = {u for u in target if len(u) <= 7}
    if got != target:
        ok_b, bad_b = False, f"trial {trial}: {sorted(got ^ target)[:3]}"
check("P2.1(a) Decompressed construction correct on 120 random DFAs (2-4 states), |w| <= 8", ok_a, bad_a)
check("P2.1(b) Compressed construction correct on 120 random DFAs (2-4 states), |u| <= 7", ok_b, bad_b)
check("P2.1(b) the NFA has no ε-transitions", not p2_compressed(random_dfa(RNG2, 3)).has_epsilon())
# edge cases the graders try: L = ∅, {ε}, 1*, Σ*, 0*
p2_EMPTY = DFA("01", [0], 0, [], lambda q, a: 0)
p2_EPSL = DFA("01", [0, 1], 0, [0], lambda q, a: 1)
p2_ONES = DFA("01", [0, 1], 0, [0], lambda q, a: 0 if (q == 0 and a == "1") else 1)
p2_ALL = DFA("01", [0], 0, [0], lambda q, a: 0)
p2_ZEROS = DFA("01", [0, 1], 0, [0], lambda q, a: 0 if (q == 0 and a == "0") else 1)
for nm, M, dec, com in [("∅", p2_EMPTY, lambda w: False, lambda u: False),
                        ("{ε}", p2_EPSL, lambda w: w == "", lambda u: u == ""),
                        ("1*", p2_ONES, lambda w: "0" not in w, lambda u: "0" not in u),
                        ("Σ*", p2_ALL, lambda w: True, lambda u: True),
                        ("0*", p2_ZEROS, lambda w: "1" not in w, lambda u: "1" not in u)]:
    check(f"P2.1 edge case L = {nm}: Decompressed and Compressed as expected",
          first_difference(p2_decompressed(M).accepts, dec, "01", 8) is None
          and first_difference(p2_compressed(M).accepts, com, "01", 8) is None)
check("P2.1(a) is a DFA: Decompressed(L) for L = 0* contains 0^k for every k (compress0s(0^k) ∈ 0*)",
      all(p2_decompressed(p2_ZEROS).accepts("0" * k) for k in range(12)))

# ---------------------------------------------------------------- 2.2 at least 374 consecutive 1s (parameter k)
def p2_run_dfa(k):
    Q = list(range(k + 1))

    def d(i, a):
        if i == k:
            return k
        return i + 1 if a == "1" else 0
    return DFA("01", Q, 0, [k], d)


for k in range(1, 7):
    has = lambda w, k=k: "1" * k in w
    R = Regex("(0+1)*" + "1" * k + "(0+1)*")
    D = p2_run_dfa(k)
    check(f"P2.2(a) regex (0+1)* 1^{k} (0+1)* matches 'contains 1^{k}', |w| <= 12",
          first_difference(R.matches, has, "01", 12) is None)
    check(f"P2.2(b) DFA with {k + 1} states accepts 'contains 1^{k}', |w| <= 12",
          first_difference(D.accepts, has, "01", 12) is None)
    check(f"P2.2(a,b) regex and DFA equivalent (exact), k = {k}", R.equivalent(D)[0])
    check(f"P2.2(c) minimal DFA for k = {k} has exactly {k + 1} states", len(D.minimize().states) == k + 1)
    F = ["1" * i for i in range(k + 1)]
    ok = True
    for i in range(k + 1):
        for j in range(i + 1, k + 1):
            z = "1" * (k - j)
            if not (has(F[j] + z) and not has(F[i] + z)):
                ok = False
    check(f"P2.2(c) F = {{1^i : 0 <= i <= {k}}} is a fooling set with suffix 1^({k}-j)", ok)
    check(f"P2.2(c) the {k + 1} strings of F end in {k + 1} distinct states of the DFA",
          len({D.delta_star(0, x) for x in F}) == k + 1)
p2_D374 = p2_run_dfa(374)
check("P2.2(b) the DFA for k = 374 has 375 states", len(p2_D374.states) == 375)
check("P2.2(b) k = 374: accepts 1^374, 0 1^374 0, 1^373 0 1^374; rejects 1^373, 1^373 0 1^373, (01)^400",
      p2_D374.accepts("1" * 374) and p2_D374.accepts("0" + "1" * 374 + "0") and p2_D374.accepts("1" * 373 + "0" + "1" * 374)
      and not p2_D374.accepts("1" * 373) and not p2_D374.accepts("1" * 373 + "0" + "1" * 373) and not p2_D374.accepts("01" * 400))
check("P2.2(c) k = 374: the DFA is minimal (375 states after minimization)", len(p2_D374.minimize().states) == 375)
check("P2.2(c) k = 374: 1^i for 0 <= i <= 374 reach 375 distinct states",
      len({p2_D374.delta_star(0, "1" * i) for i in range(375)}) == 375)
check("P2.2(c) k = 374: z = 1^(374-j) distinguishes 1^i from 1^j for 20 random pairs i < j",
      all((lambda i, j: p2_D374.accepts("1" * j + "1" * (374 - j)) and not p2_D374.accepts("1" * i + "1" * (374 - j)))
          (*sorted(RNG2.sample(range(375), 2))) for _ in range(20)))

# ---------------------------------------------------------------- 2.3 Bond
def p2_bond(w):
    if w == "":
        return ""
    return ("00" if w[0] == "0" else "1") + p2_bond(w[1:])


check("P2.3 Bond doubles every run of 0s (reference definition), e.g. Bond(0110) = 001100",
      p2_bond("0110") == "001100" and p2_bond("") == "" and p2_bond("000") == "000000")
check("P2.3(a) |Bond(w)| >= |w| for all |w| <= 10", all(len(p2_bond(w)) >= len(w) for w in strings("01", 10)))
check("P2.3(a) the inequality is strict exactly when w contains a 0, |w| <= 10",
      all((len(p2_bond(w)) > len(w)) == ("0" in w) for w in strings("01", 10)))
check("P2.3(b) Bond(x•y) = Bond(x)•Bond(y) for all |x|, |y| <= 6",
      all(p2_bond(x + y) == p2_bond(x) + p2_bond(y) for x in strings("01", 6) for y in strings("01", 6)))
check("P2.3 Bond(ε) = ε and Bond(0x) = 00·Bond(x), Bond(1x) = 1·Bond(x) (the three cases), |x| <= 8",
      all(p2_bond("0" + x) == "00" + p2_bond(x) and p2_bond("1" + x) == "1" + p2_bond(x) for x in strings("01", 8)))

# ---------------------------------------------------------------- 2.4 0^a 1^b 0^c with a = b or a = c or b = c
def p2_in_L4(w):
    # every way to write w as 0^a 1^b 0^c
    n = len(w)
    for a in range(n + 1):
        if w[:a] != "0" * a:
            break
        rest = w[a:]
        for b in range(len(rest) + 1):
            if rest[:b] != "1" * b:
                break
            c = len(rest) - b
            if rest[b:] == "0" * c and (a == b or a == c or b == c):
                return True
    return False


check("P2.4 sanity: 0011, 010, 10, 0110, 0100, 0, ε ∈ L; 100, 001, 0001, 0111, 0101 ∉ L",
      all(p2_in_L4(w) for w in ["0011", "010", "10", "0110", "0100", "0", ""])
      and not any(p2_in_L4(w) for w in ["100", "001", "0001", "0111", "0101"]))
ok = True
for i in range(1, 13):
    for j in range(1, 13):
        if i == j:
            continue
        z = "1" * i
        if not (p2_in_L4("0" * i + z) and not p2_in_L4("0" * j + z)):
            ok = False
check("P2.4(a) F = 0^+ with suffix z = 1^i: 0^i 1^i ∈ L and 0^j 1^i ∉ L for all 1 <= i != j <= 12", ok)
check("P2.4(a) why n >= 1: with i = 0 the suffix is ε and 0^j ∈ L, so ε is not distinguished that way",
      all(p2_in_L4("0" * j) for j in range(1, 10)))
p2_G4 = CFG.parse("""S -> EZ | M | ZF
E -> ε | 0E1
F -> ε | 1F0
M -> 0M0 | U
U -> ε | 1U
Z -> ε | 0Z""")
check("P2.4(b) grammar generates L on all strings of length <= 12",
      first_difference(p2_G4.generates, p2_in_L4, "01", 12) is None)
check("P2.4(b) L(E) = {0^n 1^n}", first_difference(lambda w: p2_G4.generates(w, "E"),
      lambda w: w == "0" * (len(w) // 2) + "1" * (len(w) // 2), "01", 12) is None)
check("P2.4(b) L(F) = {1^n 0^n}", first_difference(lambda w: p2_G4.generates(w, "F"),
      lambda w: w == "1" * (len(w) // 2) + "0" * (len(w) // 2), "01", 12) is None)
check("P2.4(b) L(M) = {0^n 1^m 0^n}", first_difference(lambda w: p2_G4.generates(w, "M"),
      lambda w: any(w == "0" * n + "1" * (len(w) - 2 * n) + "0" * n for n in range(len(w) // 2 + 1)), "01", 12) is None)
check("P2.4(b) L(U) = 1*, L(Z) = 0*",
      first_difference(lambda w: p2_G4.generates(w, "U"), lambda w: "0" not in w, "01", 10) is None
      and first_difference(lambda w: p2_G4.generates(w, "Z"), lambda w: "1" not in w, "01", 10) is None)
check("P2.4(b) L(EZ) = {a = b}, L(M) = {a = c}, L(ZF) = {b = c}",
      first_difference(lambda w: any(p2_G4.generates(w[:i], "E") and p2_G4.generates(w[i:], "Z") for i in range(len(w) + 1)),
                       lambda w: any(w == "0" * a + "1" * a + "0" * c for a in range(len(w) + 1) for c in range(len(w) + 1)),
                       "01", 10) is None
      and first_difference(lambda w: any(p2_G4.generates(w[:i], "Z") and p2_G4.generates(w[i:], "F") for i in range(len(w) + 1)),
                           lambda w: any(w == "0" * a + "1" * b + "0" * b for a in range(len(w) + 1) for b in range(len(w) + 1)),
                           "01", 10) is None)
check("P2.4(b) the grammar is ambiguous: ε comes from EZ, M and ZF; 0 from EZ (E=ε, Z=0) and from ZF (Z=0, F=ε)",
      all(p2_G4.generates("", X) for X in "EZMF")
      and p2_G4.generates("0", "Z") and p2_G4.generates("", "E") and p2_G4.generates("", "F"))

# ---------------------------------------------------------------- 2.5 true/false
p2_L5b = lambda w: any(w == "0" * n + "1" + "0" * n for n in range(1, len(w)))  # 0^n 1 0^n, n > 0
check("P2.5(b) {0^n : n > 0} is a fooling set for {0^n 1 0^n}: suffix 1 0^i, all 1 <= i != j <= 12",
      all(p2_L5b("0" * i + "1" + "0" * i) and not p2_L5b("0" * j + "1" + "0" * i)
          for i in range(1, 13) for j in range(1, 13) if i != j))
check("P2.5(b) the given set {0^n 1 : n > 0} is a fooling set too (suffix 0^i)",
      all(p2_L5b("0" * i + "1" + "0" * i) and not p2_L5b("0" * j + "1" + "0" * i)
          for i in range(1, 13) for j in range(1, 13) if i != j))
p2_G5c = CFG.parse("S -> 010 | 0S0")
check("P2.5(c) S -> 010 | 0S0 generates {0^n 1 0^n : n > 0}, |w| <= 13",
      first_difference(p2_G5c.generates, p2_L5b, "01", 13) is None)
p2_G5d = CFG.parse("S -> 00S | S11 | 01")
check("P2.5(d) S -> 00S | S11 | 01 generates 0001 but not ε, and 0001 ∉ {0^n 1^n}",
      p2_G5d.generates("0001") and not p2_G5d.generates("") and "0001" != "0" * 2 + "1" * 2)
check("P2.5(d) that grammar generates exactly {0^(2i+1) 1^(2j+1)}, which is not {0^n 1^n}",
      first_difference(p2_G5d.generates, lambda w: any(w == "0" * (2 * i + 1) + "1" * (2 * j + 1)
                                                    for i in range(6) for j in range(6)), "01", 12) is None)
# (e) no DFA with exactly one accepting state accepts {ε, 0}: exhaustive over DFAs with <= 3 states
from itertools import product as _p2_product  # noqa: E402
target_e = {"", "0"}
found = False
for n in range(1, 4):
    for tbl in _p2_product(range(n), repeat=2 * n):
        for acc in range(n):
            delta = {(q, a): tbl[2 * q + (0 if a == "0" else 1)] for q in range(n) for a in "01"}
            D = DFA("01", range(n), 0, [acc], delta)
            if language_upto(D.accepts, "01", 4) == target_e:
                found = True
check("P2.5(e) no DFA with <= 3 states and exactly one accepting state accepts {ε, 0}", not found)
check("P2.5(e) the argument: s accepting and δ(s,0) = s force 00 to be accepted",
      all(D.accepts("00") for D in [DFA("01", [0, 1], 0, [0], {(0, "0"): 0, (0, "1"): 1, (1, "0"): 1, (1, "1"): 1})]))
# (g) swapping the 0- and 1-transitions of a DFA for L gives a DFA for {y^c : y ∈ L}
p2_comp = lambda w: w.translate(str.maketrans("01", "10"))
ok = True
for _ in range(60):
    M = random_dfa(RNG2, RNG2.choice([2, 3, 4]))
    Mc = DFA("01", M.states, M.start, M.accepting, lambda q, a, M=M: M.delta(q, p2_comp(a)))
    if first_difference(Mc.accepts, lambda w, M=M: M.accepts(p2_comp(w)), "01", 9) is not None:
        ok = False
check("P2.5(g) swapped DFA accepts exactly {y^c : y ∈ L}, 60 random DFAs, |w| <= 9", ok)
# (h) L = 0* gives {0^n 1^n}
check("P2.5(h) {w w^c : w ∈ 0*} = {0^n 1^n : n >= 0}",
      {"0" * n + p2_comp("0" * n) for n in range(8)} == {"0" * n + "1" * n for n in range(8)})
check("P2.5(h) {0^n 1^n} is not regular: 0* is a fooling set with suffix 1^i (i != j <= 12)",
      all(("0" * i + "1" * i == "0" * i + "1" * i) and ("0" * j + "1" * i) != "0" * j + "1" * j
          for i in range(13) for j in range(13) if i != j))
p2_R5i = Regex("(00+11)*")
check("P2.5(i) 01 has even length but is not in (00+11)*", not p2_R5i.matches("01") and len("01") % 2 == 0)
check("P2.5(i) (00+11)* is a proper subset of the even-length strings, |w| <= 10",
      all(len(w) % 2 == 0 for w in strings("01", 10) if p2_R5i.matches(w)) and not p2_R5i.matches("0110"))


# =====================================================================================================
# Practice test 3  (content/3-homework-and-exams/midterm-1-practice-3.md)
# =====================================================================================================
print()
print("---- Practice test 3")
rng3 = random.Random(374)

# ---------------------------------------------------------------- 3.1 true/false
# (b) {0^m 1^n : m + n <= 374} is finite, hence regular: the same shape with 4 instead of 374 is an explicit union
L_b = lambda w: w == "0" * w.count("0") + "1" * w.count("1") and len(w) <= 4
R_b = Regex("+".join("0" * m + "1" * n if m + n else "ε" for m in range(5) for n in range(5 - m)), "01")
check("T3 1(b) {0^m1^n : m+n <= 4} is a finite union, hence a regular expression",
      first_difference(R_b.matches, L_b, "01", 10) is None)

# (c) 0^* is a fooling set for {0^m 1^n : m - n <= 374}, suffix 0^374 1^i (checked with 374 and with the small 3)
for K in (3, 374):
    L_c = lambda w, K=K: w == "0" * w.count("0") + "1" * w.count("1") and w.count("0") - w.count("1") <= K
    check(f"T3 1(c) x=0^i, y=0^j (i<j), z=0^{K}1^i: xz in L, yz not in L, all i<j<=8",
          all(L_c("0" * (K + i) + "1" * i) and not L_c("0" * (K + j) + "1" * i)
              for i in range(9) for j in range(i + 1, 9)))

# (d) L = {#0 = #1}: contains ε, closed under concatenation, so L* = L
L_eq = lambda w: w.count("0") == w.count("1")
check("T3 1(d) ε in L and L closed under concatenation (all pairs with |x|,|y| <= 6)",
      L_eq("") and all(L_eq(x + y) for x in strings("01", 6) for y in strings("01", 6) if L_eq(x) and L_eq(y)))


def star_upto(L, alphabet, maxlen):
    """Brute-force membership in L* for strings up to maxlen."""
    mem = {"": True}
    for w in strings(alphabet, maxlen):
        if w not in mem:
            mem[w] = any(L(w[:k]) and mem[w[k:]] for k in range(1, len(w) + 1))
    return lambda w: mem[w]


check("T3 1(d) L* = L for |w| <= 10", first_difference(star_upto(L_eq, "01", 10), L_eq, "01", 10) is None)
check("T3 1(d) L is not regular: 0^i, 0^j distinguished by 1^i",
      all(L_eq("0" * i + "1" * i) and not L_eq("0" * j + "1" * i) for i in range(9) for j in range(9) if i != j))

# (e) ∅* = {ε}
check("T3 1(e) ∅* = {ε}", Regex("∅*", "01").equivalent(Regex("ε", "01"))[0])

# (f) swapping accepting states of a DFA complements its language (random DFAs)
ok = True
for _ in range(50):
    M = random_dfa(rng3, rng3.randint(1, 5))
    ok = ok and first_difference(M.complement().accepts, lambda w, M=M: not M.accepts(w), "01", 8) is None
check("T3 1(f) swapping accepting and non-accepting states gives a DFA for the complement (50 random DFAs)", ok)

# (g) 0^n1^n and its complement are disjoint, and the complement is not regular (same fooling set, same suffix)
L_0n1n = lambda w: w == "0" * (len(w) // 2) + "1" * (len(w) // 2) and len(w) % 2 == 0
L_g = lambda w: not L_0n1n(w)
check("T3 1(g) L and L' are disjoint, |w| <= 12", all(not (L_g(w) and L_0n1n(w)) for w in strings("01", 12)))
check("T3 1(g) complement of 0^n1^n is not regular: 0^i, 0^j distinguished by 1^i",
      all(not L_g("0" * i + "1" * i) and L_g("0" * j + "1" * i) for i in range(9) for j in range(9) if i != j))

# (h) adding 374 unreachable accepting states with self-loops does not change the language
ok = True
for _ in range(20):
    M = random_dfa(rng3, rng3.randint(1, 4))
    new = [("new", k) for k in range(374)]
    delta = dict(M._delta)
    for n in new:
        for a in "01":
            delta[(n, a)] = n
    M2 = DFA("01", M.states + new, M.start, list(M.accepting) + new, delta)
    ok = ok and len(M2.accepting) >= 374 and M2.equivalent(M)[0]
check("T3 1(h) DFA + 374 unreachable accepting states (self-loops) accepts the same language (20 random DFAs)", ok)

# (i) one accepting state suffices for an NFA: ε-transitions from the old accepting states into a new one
ok = True
for _ in range(20):
    M = random_dfa(rng3, rng3.randint(1, 5))
    delta = {(q, a): {M.delta(q, a)} for q in M.states for a in "01"}
    for q in M.accepting:
        delta[(q, EPS)] = {"acc"}
    N = NFA("01", M.states + ["acc"], M.start, ["acc"], delta)
    ok = ok and len(N.accepting) == 1 and first_difference(N.accepts, M.accepts, "01", 8) is None
check("T3 1(i) NFA with one accepting state (ε-moves from the old accepting states) accepts the same language", ok)

# (j) a language with a k-state DFA has no fooling set of more than k strings: strings that reach the same state
#     are never distinguished, so any k+1 strings contain two that are not distinguishable
ok = True
for _ in range(20):
    M = random_dfa(rng3, rng3.randint(1, 5))
    for x in strings("01", 4):
        for y in strings("01", 4):
            if M.delta_star(M.start, x) == M.delta_star(M.start, y):
                ok = ok and all(M.accepts(x + z) == M.accepts(y + z) for z in strings("01", 6))
check("T3 1(j) strings reaching the same DFA state are indistinguishable by every suffix (pigeonhole: |F| <= k)", ok)
C3 = DFA("01", range(3), 0, [0], lambda q, a: (q + (a == "1")) % 3)
reach = {C3.delta_star(0, w) for w in strings("01", 4)}
check("T3 1(j) example: the 3-state 'number of 1s mod 3' DFA, every set of 4 strings has two in the same state",
      len(reach) == 3 and C3.minimize().num_states() == 3)

# ---------------------------------------------------------------- 3.2 parity


def parity(w):
    """The recursive definition of Problem 2(a), as written."""
    if w == "":
        return "0"
    if w[0] == "0":
        return parity(w[1:])
    return "1" if parity(w[1:]) == "0" else "0"


check("T3 2(a) recursive parity(w) = number of 1s mod 2, |w| <= 12",
      all(parity(w) == str(w.count("1") % 2) for w in strings("01", 12)))
check("T3 2(a) examples: parity(ε)=0, parity(1)=1, parity(0110)=0, parity(10101)=1",
      (parity(""), parity("1"), parity("0110"), parity("10101")) == ("0", "1", "0", "1"))


def odd_parity_dfa(M, accept_parity="1"):
    """Problem 2(b): the product of M with the two-state parity DFA; accepting A x {accept_parity}."""
    Q = [(q, p) for q in M.states for p in "01"]
    delta = {}
    for q in M.states:
        for p in "01":
            delta[((q, p), "0")] = (M.delta(q, "0"), p)
            delta[((q, p), "1")] = (M.delta(q, "1"), "1" if p == "0" else "0")
    return DFA("01", Q, (M.start, "0"), [(q, p) for q in M.accepting for p in "01" if p == accept_parity], delta)


ok_b = ok_c = ok_e = True
for _ in range(100):
    M = random_dfa(rng3, rng3.randint(1, 4))
    Mo = odd_parity_dfa(M, "1")
    Me = odd_parity_dfa(M, "0")
    ok_b = ok_b and first_difference(Mo.accepts, lambda w, M=M: M.accepts(w) and parity(w) == "1", "01", 9) is None
    ok_e = ok_e and first_difference(Me.accepts, lambda w, M=M: M.accepts(w) and parity(w) == "0", "01", 9) is None
    add = {parity(w) + w for w in strings("01", 8) if M.accepts(w)}
    rhs = {"0" + w for w in strings("01", 8) if Me.accepts(w)} | {"1" + w for w in strings("01", 8) if Mo.accepts(w)}
    ok_c = ok_c and add == rhs
check("T3 2(b) product DFA accepts exactly OddParity(L), 100 random DFAs with 1-4 states, |w| <= 9", ok_b)
check("T3 2(c) the same DFA with accepting states A x {0} accepts EvenParity(L)", ok_e)
check("T3 2(c) AddParity(L) = {0}·EvenParity(L) ∪ {1}·OddParity(L), 100 random DFAs, |w| <= 8", ok_c)
check("T3 2(b) state meaning: delta'*((s,0), w) = (delta*(s,w), parity(w)) for |w| <= 8",
      all(odd_parity_dfa(C3).delta_star((0, "0"), w) == (C3.delta_star(0, w), parity(w)) for w in strings("01", 8)))

# ---------------------------------------------------------------- 3.3 w 0^n w^R


def in_L3(u):
    """u = w 0^n w^R for some w and some n > 0?"""
    for k in range(len(u) // 2 + 1):
        w = u[:k]
        if u.endswith(w[::-1]) and len(u) >= 2 * k + 1:
            mid = u[k:len(u) - k] if k else u
            if mid and set(mid) == {"0"}:
                return True
    return False


check("T3 3 membership sanity: 0, 00, 101, 1001, 10001, 01010 in L; ε, 1, 11, 010, 110, 0100 not",
      all(in_L3(u) for u in ["0", "00", "101", "1001", "10001", "01010"])
      and not any(in_L3(u) for u in ["", "1", "11", "010", "110", "0100"]))
check("T3 3(a) F = 1*: x=1^i, y=1^j, z=01^i: xz in L, yz not in L, all i != j <= 8",
      all(in_L3("1" * i + "0" + "1" * i) and not in_L3("1" * j + "0" + "1" * i)
          for i in range(9) for j in range(9) if i != j))
check("T3 3(a) counting: a string with exactly one 0 is in L iff it is 1^k 0 1^k, |u| <= 13",
      all(in_L3(u) == (u == "1" * (len(u) // 2) + "0" + "1" * (len(u) // 2))
          for u in strings("01", 13) if u.count("0") == 1))
G3 = CFG.parse("S -> 0S0 | 1S1 | Z ; Z -> 0 | 0Z")
check("T3 3(b) grammar S -> 0S0 | 1S1 | Z, Z -> 0 | 0Z generates exactly L, |u| <= 10",
      first_difference(lambda u: G3.generates(u), in_L3, "01", 10) is None)
check("T3 3(b) Z generates exactly 0^+", first_difference(lambda u: G3.generates(u, "Z"),
                                                          lambda u: u != "" and set(u) == {"0"}, "01", 10) is None)

# ---------------------------------------------------------------- 3.4 take2skip2


def take2skip2(w):
    return "".join(c for p, c in enumerate(w, 1) if (p - 1) % 4 in (0, 1))


check("T3 4 example: take2skip2(0100111100011) = 0111001", take2skip2("0100111100011") == "0111001")


def took2added2_dfa(M):
    """Problem 4(a)."""
    Q = [(q, i) for q in M.states for i in range(4)]
    delta = {}
    for q in M.states:
        for i in range(4):
            for a in "01":
                delta[((q, i), a)] = (M.delta(q, a), i + 1) if i in (0, 1) else (q, (i + 1) % 4)
    return DFA("01", Q, (M.start, 0), [(q, i) for q in M.accepting for i in range(4)], delta)


def took2skipped2_nfa(M):
    """Problem 4(b)."""
    Q = [(q, i) for q in M.states for i in range(4)]
    delta = {}
    for q in M.states:
        for i in (0, 1):
            for a in "01":
                delta[((q, i), a)] = {(M.delta(q, a), i + 1)}
        for i in (2, 3):
            delta[((q, i), EPS)] = {(M.delta(q, b), (i + 1) % 4) for b in "01"}
    return NFA("01", Q, (M.start, 0), [(q, i) for q in M.accepting for i in range(4)], delta)


ok_a = ok_b = True
for _ in range(60):
    M = random_dfa(rng3, rng3.randint(1, 4))
    ok_a = ok_a and first_difference(took2added2_dfa(M).accepts, lambda w, M=M: M.accepts(take2skip2(w)),
                                     "01", 10) is None
    # |u| <= 7  iff  |w| <= 14, so the image of L restricted to |w| <= 14 is exact on all u with |u| <= 7
    image = {take2skip2(w) for w in strings("01", 14) if M.accepts(w)}
    N = took2skipped2_nfa(M)
    ok_b = ok_b and all(N.accepts(u) == (u in image) for u in strings("01", 7))
check("T3 4(a) DFA accepts exactly {w : take2skip2(w) in L}, 60 random DFAs with 1-4 states, |w| <= 10", ok_a)
check("T3 4(b) ε-NFA accepts exactly {take2skip2(w) : w in L}, 60 random DFAs, |u| <= 7 (|w| <= 14)", ok_b)
check("T3 4(a) state meaning: delta'*((s,0), x) = (delta*(s, take2skip2(x)), |x| mod 4), |x| <= 10",
      all(took2added2_dfa(C3).delta_star((0, 0), x) == (C3.delta_star(0, take2skip2(x)), len(x) % 4)
          for x in strings("01", 10)))
# the kind matters: for L = 1* (M accepts 1*), Took2Added2 is 'taken symbols all 1', Took2Skipped2 is 1*
Ones = DFA("01", "ab", "a", ["a"], {("a", "0"): "b", ("a", "1"): "a", ("b", "0"): "b", ("b", "1"): "b"})
check("T3 4 edge case L = 1*: Took2Added2(1*) = {w : taken symbols all 1}, Took2Skipped2(1*) = 1*",
      first_difference(took2added2_dfa(Ones).accepts, lambda w: set(take2skip2(w)) <= {"1"}, "01", 10) is None
      and first_difference(took2skipped2_nfa(Ones).accepts, lambda u: set(u) <= {"1"}, "01", 10) is None)

# ---------------------------------------------------------------- 3.5(a) runs of 1s even, runs of 0s odd
L5a_t3 = lambda w: all((n % 2 == 0) if c == "1" else (n % 2 == 1) for c, n in runs(w))
D5a_t3 = DFA("01", ["E1", "O1", "O0", "E0", "dump"], "E1", ["E1", "O0"],
             {("E1", "1"): "O1", ("O1", "1"): "E1", ("E1", "0"): "O0", ("O0", "1"): "O1", ("O0", "0"): "E0",
              ("E0", "0"): "O0", ("O1", "0"): "dump", ("E0", "1"): "dump", ("dump", "0"): "dump",
              ("dump", "1"): "dump"})
check("T3 5(a) DFA (4 states + dump) accepts exactly 'runs of 1s even, runs of 0s odd', |w| <= 14",
      first_difference(D5a_t3.accepts, L5a_t3, "01", 14) is None)
check("T3 5(a) DFA is minimal as drawn: 5 states including the dump", D5a_t3.minimize().num_states() == 5)
R5a_t3 = Regex("(11)*(0(00)*11(11)*)*(ε+0(00)*)", "01")
eq, cex = R5a_t3.equivalent(D5a_t3)
check("T3 5(a) regex (11)*(0(00)*11(11)*)*(ε+0(00)*) is equivalent to the DFA", eq, repr(cex))
check("T3 5(a) examples: ε, 0, 11, 011, 0110, 11000 in; 1, 00, 010, 0111 out",
      all(L5a_t3(w) for w in ["", "0", "11", "011", "0110", "11000"])
      and not any(L5a_t3(w) for w in ["1", "00", "010", "0111"]))
ends_run = lambda w, c, par: bool(w) and w[-1] == c and runs(w)[-1][1] % 2 == par
mean_t3 = {"E1": lambda w: w == "" or ends_run(w, "1", 0), "O1": lambda w: ends_run(w, "1", 1),
           "O0": lambda w: ends_run(w, "0", 1), "E0": lambda w: ends_run(w, "0", 0)}
check("T3 5(a) state meanings hold for every input that has not hit the dump, |w| <= 12",
      all(mean_t3[q](w) for w in strings("01", 12) for q in [D5a_t3.delta_star("E1", w)] if q != "dump"))

# ---------------------------------------------------------------- 3.5(b) 0*10* with length a multiple of 3
L5b_t3 = lambda w: w.count("1") == 1 and len(w) % 3 == 0
Q5b_t3 = [f"N{i}" for i in range(3)] + [f"Y{i}" for i in range(3)] + ["dump"]
d5b_t3 = {}
for i in range(3):
    d5b_t3[(f"N{i}", "0")] = f"N{(i + 1) % 3}"
    d5b_t3[(f"Y{i}", "0")] = f"Y{(i + 1) % 3}"
    d5b_t3[(f"N{i}", "1")] = f"Y{(i + 1) % 3}"
    d5b_t3[(f"Y{i}", "1")] = "dump"
d5b_t3[("dump", "0")] = d5b_t3[("dump", "1")] = "dump"
D5b_t3 = DFA("01", Q5b_t3, "N0", ["Y0"], d5b_t3)
check("T3 5(b) DFA (6 states + dump) accepts exactly '0*10* with |w| a multiple of 3', |w| <= 14",
      first_difference(D5b_t3.accepts, L5b_t3, "01", 14) is None)
check("T3 5(b) DFA is minimal as drawn: 7 states including the dump", D5b_t3.minimize().num_states() == 7)
R5b_t3 = Regex("(000)*(100+010+001)(000)*", "01")
eq, cex = R5b_t3.equivalent(D5b_t3)
check("T3 5(b) regex (000)*(100+010+001)(000)* is equivalent to the DFA", eq, repr(cex))
check("T3 5(b) (a mod 3, b mod 3) in {(0,2),(1,1),(2,0)} iff a+b+1 is a multiple of 3, a,b <= 12",
      all(((a + b + 1) % 3 == 0) == ((a % 3, b % 3) in {(0, 2), (1, 1), (2, 0)}) for a in range(13) for b in range(13)))
check("T3 5(b) state meanings: N_i / Y_i = (#1 so far, |x| mod 3), |x| <= 12",
      all(D5b_t3.delta_star("N0", x) == ("dump" if x.count("1") > 1 else f"{'NY'[x.count('1')]}{len(x) % 3}")
          for x in strings("01", 12)))
check("T3 5 ε test: ε is in (a) and not in (b)", L5a_t3("") and not L5b_t3(""))

# =====================================================================================================
# (end of Practice test 3)
# =====================================================================================================

