#!/usr/bin/env python3
"""Checks for every concrete claim on content/practice/04-nondeterministic-automata.md.

Brute-force predicates are written from the problem statements, independently of the answers.
Transformations are implemented as functions of an arbitrary DFA M and tested on random small
DFAs (2-4 states) plus the edge cases (empty language, {eps}, 1*, Sigma*)."""
import itertools
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from automata import DFA, NFA, Regex, EPS, strings, first_difference, thompson  # noqa: E402
from automata.regex import _Parser  # noqa: E402

FAIL = []


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAIL.append(name)


def fs(X):
    return "{" + ",".join(sorted(map(str, X))) + "}" if X else "∅"


def run_sets(N, w):
    """Current-state sets C_0 = eps-reach(s), C_i = eps-reach(delta(C_{i-1}, w_i)), as frozensets."""
    S = N.eps_reach({N.start})
    out = [S]
    for a in w:
        S = N.eps_reach(N.step(S, a))
        out.append(S)
    return out


def same_lang(pred1, pred2, alphabet, maxlen):
    return first_difference(pred1, pred2, alphabet, maxlen) is None


rng = random.Random(374)


def random_dfa(n, alphabet="01", p_acc=0.5):
    Q = list(range(n))
    delta = {(q, a): rng.randrange(n) for q in Q for a in alphabet}
    A = [q for q in Q if rng.random() < p_acc]
    return DFA(alphabet, Q, 0, A, delta)


def edge_dfas(alphabet="01"):
    """Sigma*, empty, {eps}, 1* (for the binary alphabet) -- the rubric's edge cases."""
    out = {
        "Sigma*": DFA(alphabet, [0], 0, [0], {(0, a): 0 for a in alphabet}),
        "empty": DFA(alphabet, [0], 0, [], {(0, a): 0 for a in alphabet}),
        "{eps}": DFA(alphabet, [0, 1], 0, [0], {(q, a): 1 for q in (0, 1) for a in alphabet}),
    }
    if "1" in alphabet:
        out["1*"] = DFA(alphabet, [0, 1], 0, [0], {(q, a): (0 if (q == 0 and a == "1") else 1)
                                                   for q in (0, 1) for a in alphabet})
    return out


def test_dfas(count=300, alphabet="01"):
    ms = list(edge_dfas(alphabet).values())
    for i in range(count):
        ms.append(random_dfa(2 + i % 3, alphabet, p_acc=rng.choice([0.3, 0.5, 0.7])))
    return ms


# ============================================================== 4.1 true or false
print("== 4.1")
# (a) subset construction never has more than 2^n states
ok = True
for i in range(300):
    n = 2 + i % 4
    Q = list(range(n))
    d = {}
    for q in Q:
        for a in "01" + EPS:
            T = {r for r in Q if rng.random() < (0.3 if a else 0.15)}
            if T:
                d[(q, a)] = T
    N = NFA("01", Q, 0, {q for q in Q if rng.random() < 0.4}, d)
    D, _ = N.subset_construction()
    ok = ok and len(D.states) <= 2 ** n
check("(a) incremental subset construction: at most 2^n DFA states (300 random NFAs with eps)", ok)

# (b) one-state NFA, no transitions: L = {eps}; swapping accepting states gives the empty language
N1 = NFA("01", ["s"], "s", {"s"}, {})
N1s = NFA("01", ["s"], "s", set(), {})
check("(b) one-state NFA with no transitions accepts exactly {eps}",
      same_lang(N1.accepts, lambda w: w == "", "01", 8))
check("(b) swapped version accepts nothing, but the complement of {eps} contains 0",
      same_lang(N1s.accepts, lambda w: False, "01", 8) and "0" != "")


# (c) a nonempty NFA language contains a string of length <= n-1
def shortest_accepted(N):
    start = N.eps_reach({N.start})
    seen = {start: ""}
    frontier = [start]
    while frontier:
        nxt = []
        for S in frontier:
            if S & N.accepting:
                return seen[S]
        for S in frontier:
            for a in N.alphabet:
                T = N.eps_reach(N.step(S, a))
                if T not in seen:
                    seen[T] = seen[S] + a
                    nxt.append(T)
        frontier = nxt
    return None


ok, tested = True, 0
for i in range(2000):
    n = 1 + i % 5
    Q = list(range(n))
    d = {}
    for q in Q:
        for a in "01" + EPS:
            T = {r for r in Q if rng.random() < 0.25}
            if T:
                d[(q, a)] = T
    N = NFA("01", Q, 0, {q for q in Q if rng.random() < 0.3}, d)
    w = shortest_accepted(N)
    if w is not None:
        tested += 1
        ok = ok and len(w) <= n - 1
check("(c) nonempty n-state NFA accepts a string of length <= n-1 (random NFAs with eps)", ok and tested > 500,
      f"{tested} nonempty")

# (d) {eps, 0}: no eps-free NFA with exactly one accepting state (exhaustive up to 3 states, alphabet {0,1})
found = False
for n in (1, 2, 3):
    Q = list(range(n))
    subsets = [frozenset(c) for k in range(n + 1) for c in itertools.combinations(Q, k)]
    keys = [(q, a) for q in Q for a in "01"]
    for acc in Q:
        # accepting eps forces acc == start (=0); check all anyway
        for choice in itertools.product(subsets, repeat=len(keys)):
            d = {k: set(T) for k, T in zip(keys, choice) if T}
            N = NFA("01", Q, 0, {acc}, d)
            if N.accepts("") and N.accepts("0") and not N.accepts("00") and not N.accepts("1"):
                found = True
                break
        if found:
            break
check("(d) no eps-free NFA with <= 3 states and one accepting state accepts eps and 0 but not 00", not found)
Ne = NFA("01", ["s", "f"], "s", {"f"}, {("s", EPS): {"f"}, ("s", "0"): {"f"}})
check("(d) with an eps-transition, s -eps-> f, s -0-> f (one accepting state f != s) accepts exactly {eps, 0}",
      same_lang(Ne.accepts, lambda w: w in ("", "0"), "01", 8))

# (e) third symbol from the end is 1: 4-state NFA, minimal DFA has 8 states, length-3 strings are a fooling set
N3 = NFA("01", "sabc", "s", {"c"}, {("s", "0"): {"s"}, ("s", "1"): {"s", "a"}, ("a", "0"): {"b"}, ("a", "1"): {"b"},
                                     ("b", "0"): {"c"}, ("b", "1"): {"c"}})
L3 = lambda w: len(w) >= 3 and w[-3] == "1"
check("(e) 4-state NFA accepts exactly the strings whose third symbol from the end is 1",
      same_lang(N3.accepts, L3, "01", 12))
check("(e) its minimal DFA has 8 states", len(N3.to_dfa().minimize().states) == 8)
ok = True
F3 = list(strings("01", 3, 3))
for x, y in itertools.combinations(F3, 2):
    i = next(k for k in range(3) if x[k] != y[k]) + 1  # first differing position, 1-indexed
    z = "0" * (i - 1)
    ok = ok and (L3(x + z) != L3(y + z))
check("(e) all 8 strings of length 3 pairwise distinguished by 0^(i-1), i = a position where they differ", ok)


# (f) sort((01)*) = {0^n 1^n}
def sort01(w):
    return "0" * w.count("0") + "1" * w.count("1")


img = {sort01(w) for w in strings("01", 14) if Regex("(01)*")(w)}
check("(f) {sort(w) : w in (01)*, |w| <= 14} = {0^n 1^n : n <= 7}", img == {"0" * n + "1" * n for n in range(8)})
L0n1n = lambda w: len(w) % 2 == 0 and w == "0" * (len(w) // 2) + "1" * (len(w) // 2)
check("(f) {0^n1^n} is not regular: x=0^i, y=0^j, z=1^i (i != j <= 9)",
      all(L0n1n("0" * i + "1" * i) and not L0n1n("0" * j + "1" * i) for i in range(10) for j in range(10) if i != j))

# ============================================================== 4.2 running an eps-NFA
print("== 4.2")
N2 = NFA("01", "sabcd", "s", {"d"}, {("s", EPS): {"a"}, ("a", "0"): {"b"}, ("a", EPS): {"c"}, ("b", "1"): {"a"},
                                     ("c", "0"): {"d"}, ("c", "1"): {"b"}, ("d", EPS): {"a"}})
reach2 = {"s": "sac", "a": "ac", "b": "b", "c": "c", "d": "acd"}
for q, R in reach2.items():
    check(f"eps-reach({q}) = {fs(R)}", N2.eps_reach({q}) == frozenset(R), fs(N2.eps_reach({q})))
check("eps: C0 = {s,a,c} has no accepting state, so eps is rejected",
      run_sets(N2, "") == [frozenset("sac")] and not N2.accepts(""))
tr = run_sets(N2, "0110")
check("0110: {s,a,c} -> {a,b,c,d} -> {a,b,c} -> {a,b,c} -> {a,b,c,d}, accepted",
      tr == [frozenset(x) for x in ("sac", "abcd", "abc", "abc", "abcd")] and N2.accepts("0110"),
      " -> ".join(fs(S) for S in tr))
check("0110 steps before closing: delta({s,a,c},0)={b,d}, delta({a,b,c,d},1)={a,b}, delta({a,b,c},1)={a,b}, "
      "delta({a,b,c},0)={b,d}",
      [N2.step(tr[0], "0"), N2.step(tr[1], "1"), N2.step(tr[2], "1"), N2.step(tr[3], "0")]
      == [frozenset("bd"), frozenset("ab"), frozenset("ab"), frozenset("bd")])
tr = run_sets(N2, "1010")
check("1010: {s,a,c} -> {b} -> ∅ -> ∅ -> ∅, rejected",
      tr == [frozenset("sac"), frozenset("b"), frozenset(), frozenset(), frozenset()] and not N2.accepts("1010"),
      " -> ".join(fs(S) for S in tr))


def path_ok(N, path, w):
    """path: list of (from, label, to); labels concatenate to w; ends accepting; starts at start."""
    if path[0][0] != N.start or path[-1][2] not in N.accepting:
        return False
    for (p, a, q), nxt in zip(path, path[1:] + [None]):
        if q not in N.delta(p, a):
            return False
        if nxt is not None and nxt[0] != q:
            return False
    return "".join(a for _, a, _ in path) == w


P = [("s", "", "a"), ("a", "", "c"), ("c", "0", "d"), ("d", "", "a"), ("a", "", "c"), ("c", "1", "b"),
     ("b", "1", "a"), ("a", "", "c"), ("c", "0", "d")]
check("accepting path for 0110: s -e-> a -e-> c -0-> d -e-> a -e-> c -1-> b -1-> a -e-> c -0-> d",
      path_ok(N2, P, "0110"))
P_bad = [("s", "", "a"), ("a", "0", "b"), ("b", "1", "a"), ("a", "", "c"), ("c", "1", "b")]
check("the thread through a -0-> b dies: after s,a -0-> b -1-> a -e-> c -1-> b the next 0 has no edge from b",
      not N2.delta("b", "0"))
lead1 = lambda w: len(w) - len(w.lstrip("1"))
check("remark: L(N) = {w : w ends in 0 and the block of 1s at the start of w has even length}",
      same_lang(N2.accepts, lambda w: w.endswith("0") and lead1(w) % 2 == 0, "01", 14))
check("remark: L(N) = (11)*0 + (11)*0(0+1)*0 exactly", Regex("(11)*0+(11)*0(0+1)*0", "01").equivalent(N2.to_dfa())[0])

# ============================================================== 4.3 NFA design
print("== 4.3")
L43 = lambda w: len(w) >= 1 and w[-1] in w[:-1]
d43 = {}
for a in "012":
    d43[("s", a)] = {"s", "p" + a}
    for b in "012":
        d43[("p" + a, b)] = {"p" + a} | ({"f"} if b == a else set())
N43 = NFA("012", ["s", "p0", "p1", "p2", "f"], "s", {"f"}, d43)
check("5-state NFA accepts exactly the strings whose last symbol appears earlier (|w| <= 9)",
      same_lang(N43.accepts, L43, "012", 9))
check("examples: 0120 and 11 in L; 012, 1, eps not in L",
      all(L43(w) for w in ["0120", "11"]) and not any(L43(w) for w in ["012", "1", ""])
      and all(N43(w) for w in ["0120", "11"]) and not any(N43(w) for w in ["012", "1", ""]))
check("accepting path for 0120: s -0-> p0 -1-> p0 -2-> p0 -0-> f",
      path_ok(N43, [("s", "0", "p0"), ("p0", "1", "p0"), ("p0", "2", "p0"), ("p0", "0", "f")], "0120"))
# independent DFA from the "remember the set of symbols before the last one and the last symbol" algorithm
D43 = DFA.explore("012", (frozenset(), None),
                  lambda q, a: (q[0] | ({q[1]} if q[1] is not None else frozenset()), a),
                  lambda q: q[1] is not None and q[1] in q[0])
check("brute-force DFA (seen-before set, last symbol) is correct", same_lang(D43.accepts, L43, "012", 8))
check("no string of length < 2 is accepted (every path to f reads two symbols)",
      not any(N43.accepts(w) for w in strings("012", 1)))
check("remark: the smallest DFA has 15 states", len(D43.minimize().states) == 15 ==
      len(N43.to_dfa().minimize().states))

# ============================================================== 4.4 find the error: Kleene star
print("== 4.4")


def star_member(M, w):
    reach = [True] + [False] * len(w)
    for j in range(1, len(w) + 1):
        reach[j] = any(reach[i] and M.accepts(w[i:j]) for i in range(j))
    return reach[len(w)]


def student_star(M):
    d = {(q, a): {M.delta(q, a)} for q in M.states for a in M.alphabet}
    for q in M.accepting:
        d.setdefault((q, EPS), set()).add(M.start)
    return NFA(M.alphabet, M.states, M.start, set(M.accepting) | {M.start}, d)


def fixed_star(M):
    new = ("new",)
    d = {(q, a): {M.delta(q, a)} for q in M.states for a in M.alphabet}
    d[(new, EPS)] = {M.start}
    for q in M.accepting:
        d.setdefault((q, EPS), set()).add(M.start)
    return NFA(M.alphabet, [new] + list(M.states), new, set(M.accepting) | {new}, d)


M01 = DFA("01", ["s", "a", "d"], "s", ["a"], {("s", "0"): "s", ("s", "1"): "a", ("a", "0"): "d", ("a", "1"): "d",
                                             ("d", "0"): "d", ("d", "1"): "d"})
check("the DFA M (s, a, d) accepts exactly 0*1", Regex("0*1", "01").equivalent(M01)[0])
check("L(M)* = eps + (0+1)*1 (empty or ends in 1)",
      same_lang(lambda w: star_member(M01, w), lambda w: w == "" or w.endswith("1"), "01", 10))
S01 = student_star(M01)
check("student's NFA accepts 0, but 0 is not in L*", S01.accepts("0") and not star_member(M01, "0"))
check("student's NFA accepts every binary string here (e.g. 0 and 10), |w| <= 12",
      same_lang(S01.accepts, lambda w: True, "01", 12))
check("10 is not in L*", not star_member(M01, "10"))
F01 = fixed_star(M01)
check("fixed NFA on this M: accepts eps, 01, 101; rejects 0, 10",
      all(F01(w) for w in ["", "01", "101"]) and not any(F01(w) for w in ["0", "10"]))
ok_fix, bad_student, ok_noincoming, n_noinc = True, 0, True, 0
for M in test_dfas(300):
    F = fixed_star(M)
    S = student_star(M)
    ok_fix = ok_fix and same_lang(F.accepts, lambda w: star_member(M, w), "01", 8)
    if not same_lang(S.accepts, lambda w: star_member(M, w), "01", 8):
        bad_student += 1
    if all(M.delta(q, a) != M.start for q in M.states for a in M.alphabet):
        n_noinc += 1
        ok_noincoming = ok_noincoming and same_lang(S.accepts, lambda w: star_member(M, w), "01", 8)
check("fixed construction (new accepting start s', s' -e-> s, q -e-> s for q in A) = L* on 304 DFAs (|w| <= 8)",
      ok_fix)
check("student's construction is wrong on many of them", bad_student > 50, f"{bad_student} wrong")
check("student's construction is right whenever no transition enters s", ok_noincoming and n_noinc > 5,
      f"{n_noinc} such DFAs")

# ============================================================== 4.5 subset construction
print("== 4.5")
N5 = NFA("01", "sabcd", "s", {"b", "d"}, {("s", EPS): {"a", "c"}, ("a", "0"): {"a"}, ("a", EPS): {"b"},
                                          ("b", "1"): {"b"}, ("c", "1"): {"c"}, ("c", EPS): {"d"}, ("d", "0"): {"d"}})
L5 = lambda w: Regex("0*1*+1*0*", "01")(w)
check("NFA accepts exactly 0*1* + 1*0*", Regex("0*1*+1*0*", "01").equivalent(N5.to_dfa())[0])
D5, rows5 = N5.subset_construction()
expect5 = [("s", "sabcd", True, "ad", "bc"), ("ad", "abd", True, "ad", "b"), ("bc", "bcd", True, "d", "bc"),
           ("b", "b", True, "", "b"), ("d", "d", True, "d", ""), ("", "", False, "", "")]
got5 = [(S, R, acc, tr["0"], tr["1"]) for S, R, acc, tr in rows5]
check("subset table rows (S, eps-reach, accept?, on 0, on 1) in discovery order",
      got5 == [(frozenset(a), frozenset(b), c, frozenset(d), frozenset(e)) for a, b, c, d, e in expect5],
      "; ".join(f"{fs(S)} {fs(R)} {acc} {fs(x)} {fs(y)}" for S, R, acc, x, y in got5))
check("6 DFA states, 5 accepting (all but ∅)", len(D5.states) == 6 and len(D5.accepting) == 5)
check("the DFA accepts exactly 0*1* + 1*0*", same_lang(D5.accepts, L5, "01", 12))
mean5 = {frozenset("s"): lambda w: w == "", frozenset("ad"): lambda w: w != "" and set(w) == {"0"},
         frozenset("bc"): lambda w: w != "" and set(w) == {"1"},
         frozenset("b"): lambda w: Regex("00*11*", "01")(w), frozenset("d"): lambda w: Regex("11*00*", "01")(w),
         frozenset(): lambda w: not L5(w)}
ok = all(mean5[D5.delta_star(D5.start, w)](w) for w in strings("01", 12))
check("state meanings: {s}=eps, {a,d}=0^+, {b,c}=1^+, {b}=0^+1^+, {d}=1^+0^+, ∅=not in L (|w| <= 12)", ok)
sig_suffixes = ["", "0", "1", "01", "10"]
sig = {S: tuple(int(D5.delta_star(S, z) in D5.accepting) for z in sig_suffixes) for S in D5.states}
expect_sig = {frozenset("s"): (1, 1, 1, 1, 1), frozenset("ad"): (1, 1, 1, 1, 0), frozenset("bc"): (1, 1, 1, 0, 1),
              frozenset("b"): (1, 0, 1, 0, 0), frozenset("d"): (1, 1, 0, 0, 0), frozenset(): (0, 0, 0, 0, 0)}
check("signature table (suffixes eps,0,1,01,10) as stated, rows pairwise different",
      sig == expect_sig and len(set(sig.values())) == 6, str({fs(k): v for k, v in sig.items()}))
FS5 = ["", "0", "1", "01", "10", "010"]
check("{eps,0,1,01,10,010} reach the six different DFA states",
      len({D5.delta_star(D5.start, x) for x in FS5}) == 6)
ok = all(any(L5(x + z) != L5(y + z) for z in strings("01", 4)) for x, y in itertools.combinations(FS5, 2))
check("{eps,0,1,01,10,010} is a fooling set for 0*1* + 1*0*", ok)
check("run of 0011: {s},{a,d},{a,d},{b},{b}, accepted",
      D5.run("0011") == [frozenset(x) for x in ("s", "ad", "ad", "b", "b")] and D5.accepts("0011"))
check("run of 010: {s},{a,d},{b},∅, rejected",
      D5.run("010") == [frozenset("s"), frozenset("ad"), frozenset("b"), frozenset()] and not D5.accepts("010"))
check("watch out: delta(s, 0) without the eps-reach is ∅", not N5.delta("s", "0"))
check("6 of 2^5 = 32 subsets reachable", len(D5.states) == 6 and 2 ** len(N5.states) == 32)
check("hence minimal: Moore's algorithm also gives 6 states", len(D5.minimize().states) == 6)

# ============================================================== 4.6 Thompson
print("== 4.6")


def count_nodes(n):
    """(leaves, eps-leaves, symbol leaves, unions, stars, concatenations)"""
    k = n[0]
    if k == "empty":
        return (1, 0, 0, 0, 0, 0)
    if k == "eps":
        return (1, 1, 0, 0, 0, 0)
    if k == "sym":
        return (1, 0, 1, 0, 0, 0)
    if k == "star":
        c = count_nodes(n[1])
        return c[:4] + (c[4] + 1, c[5])
    l, r = count_nodes(n[1]), count_nodes(n[2])
    s = tuple(x + y for x, y in zip(l, r))
    if k == "union":
        return s[:3] + (s[3] + 1,) + s[4:]
    return s[:5] + (s[5] + 1,)


def thompson_counts(N):
    eps = sum(len(T) for (q, a), T in N._delta.items() if a == EPS)
    sym = sum(len(T) for (q, a), T in N._delta.items() if a != EPS)
    return len(N.states), eps, sym


def random_ast(depth):
    if depth == 0 or rng.random() < 0.25:
        return rng.choice([("sym", "0"), ("sym", "1"), ("sym", "0"), ("sym", "1"), ("eps",), ("empty",)])
    k = rng.choice(["union", "cat", "cat", "star"])
    if k == "star":
        return ("star", random_ast(depth - 1))
    return (k, random_ast(depth - 1), random_ast(depth - 1))


ok = True
for _ in range(500):
    ast = random_ast(5)
    N = thompson(ast, ["0", "1"])
    lv, e, sy, u, st, c = count_nodes(ast)
    ok = ok and thompson_counts(N) == (2 * (lv + u + st), e + c + 4 * u + 4 * st, sy)
check("formula on 500 random expressions: states 2(l+u+k), eps-edges e+c+4u+4k, symbol edges = symbol leaves", ok)
R6 = Regex("(1+01)*0", "01")
N6 = R6.nfa()
check("(1+01)*0: l=4, e=0, u=1, k=1, c=2", count_nodes(R6.ast) == (4, 0, 4, 1, 1, 2), str(count_nodes(R6.ast)))
check("Thompson's NFA for (1+01)*0 has 12 states, 10 eps-transitions, 4 symbol transitions",
      thompson_counts(N6) == (12, 10, 4), str(thompson_counts(N6)))
edges6 = {(0, EPS, 1), (0, EPS, 9), (1, EPS, 2), (1, EPS, 4), (3, EPS, 8), (5, EPS, 6), (7, EPS, 8), (8, EPS, 1),
          (8, EPS, 9), (9, EPS, 10), (2, "1", 3), (4, "0", 5), (6, "1", 7), (10, "0", 11)}
got6 = {(q, a, r) for (q, a), T in N6._delta.items() for r in T}
check("the 14 transitions are exactly as listed (start 0, accepting 11)",
      got6 == edges6 and N6.start == 0 and N6.accepting == {11})
check("eps-reach(0) = {0,1,2,4,9,10}", N6.eps_reach({0}) == frozenset({0, 1, 2, 4, 9, 10}))
check("reading 0: delta(eps-reach(0), 0) = {5, 11}; eps-reach = {5, 6, 11}; contains 11 so 0 is accepted",
      N6.step({0}, "0") == frozenset({5, 11}) and N6.eps_reach(N6.step({0}, "0")) == frozenset({5, 6, 11})
      and N6.accepts("0"))
check("reading 01: set {1,2,4,7,8,9,10}, no 11, so 01 is rejected",
      N6.current_states("01") == frozenset({1, 2, 4, 7, 8, 9, 10}) and not N6.accepts("01"))
check("L((1+01)*0) = strings ending in 0 with no 00",
      same_lang(R6.matches, lambda w: w.endswith("0") and "00" not in w, "01", 14))
D6, rows6 = N6.subset_construction()
check("remark: incremental subset construction on it gives 5 DFA states; minimal DFA has 3",
      len(D6.states) == 5 and len(D6.minimize().states) == 3, f"{len(D6.states)}, {len(D6.minimize().states)}")

# ============================================================== 4.7 state elimination
print("== 4.7")


def par(q, a):
    z, o = q
    if a == "0":
        return ("O" if z == "E" else "E") + o
    return z + ("O" if o == "E" else "E")


M7 = DFA("01", ["EE", "OE", "EO", "OO"], "EE", ["EE"],
         {(q, a): par(q, a) for q in ["EE", "OE", "EO", "OO"] for a in "01"})
check("DFA (parity of 0s, parity of 1s) accepts exactly even #0 and even #1",
      same_lang(M7.accepts, lambda w: w.count("0") % 2 == 0 and w.count("1") % 2 == 0, "01", 12))
check("transitions as tabulated", [M7.delta(q, a) for q in ["EE", "OE", "EO", "OO"] for a in "01"]
      == ["OE", "EO", "EE", "OO", "OO", "EE", "EO", "OE"])


# expression automaton bookkeeping by hand-written formulas, checked step by step as languages
def lang_expr(e):
    return Regex(e, "01")


steps = {
    # after eliminating OE
    "1": {("EE", "EE"): "00", ("EE", "OO"): "01", ("OO", "EE"): "10", ("OO", "OO"): "11",
          ("EE", "EO"): "1", ("EO", "EE"): "1", ("EO", "OO"): "0", ("OO", "EO"): "0"},
    # after eliminating EO
    "2": {("EE", "EE"): "00+11", ("EE", "OO"): "01+10", ("OO", "EE"): "10+01", ("OO", "OO"): "11+00"},
    # after eliminating OO
    "3": {("EE", "EE"): "00+11+(01+10)(00+11)*(10+01)"},
}


def expr_automaton_lang(labels, start="EE", target="EE", maxlen=8):
    """Set of strings (|w| <= maxlen) spelled by walks start -> target whose edges carry the labels."""
    nodes = sorted({p for p, _ in labels} | {r for _, r in labels})
    matchers = {k: lang_expr(v) for k, v in labels.items()}
    # reach[(node, i)] for prefixes of w via DP over all w
    out = set()
    for w in strings("01", maxlen):
        n = len(w)
        reach = {(start, 0)}
        frontier = [(start, 0)]
        while frontier:
            p, i = frontier.pop()
            for (pp, r), m in matchers.items():
                if pp != p:
                    continue
                for j in range(i, n + 1):
                    if (r, j) not in reach and m(w[i:j]):
                        if j == i and r == p:
                            continue
                        reach.add((r, j))
                        frontier.append((r, j))
        if (target, n) in reach:
            out.add(w)
    return out


target_lang = {w for w in strings("01", 8) if M7.accepts(w)}
for k in ["1", "2", "3"]:
    got = expr_automaton_lang(steps[k])
    check(f"after elimination step {k}: walks EE -> EE spell exactly L (|w| <= 8)", got == target_lang)
R7 = Regex("(00+11+(01+10)(00+11)*(01+10))*", "01")
check("final expression (00+11+(01+10)(00+11)*(01+10))* is exactly L(M)", R7.equivalent(M7)[0])
X7 = Regex("00+11+(01+10)(00+11)*(01+10)", "01")
check("0110 and 0101 each match X (one term)", X7("0110") and X7("0101"))
check("every string matching X* has even length (|w| <= 12)",
      all(len(w) % 2 == 0 for w in strings("01", 12) if R7(w)))
R7b = Regex("(00+11+(01+10)(00+11)*(10+01))*", "01")
check("answer as derived, (00+11+(01+10)(00+11)*(10+01))*, is exactly L(M)", R7b.equivalent(M7)[0])
check("0101 and 0110 in L, 011 not", R7("0101") and R7("0110") and not R7("011")
      and M7("0101") and M7("0110") and not M7("011"))

# ============================================================== transformations: helpers
print("== transformations")


def image_check(construct, f, alphabet="01", maxlen=8, count=300, extra=None):
    """construct(M) -> NFA/DFA for {f(w) : w in L(M)}; f is length-preserving here, so preimages of y
    have length |y| and the brute force over all w with |w| <= maxlen is exact for |y| <= maxlen."""
    ok = True
    for M in test_dfas(count, alphabet) + (extra or []):
        img = {f(w) for w in strings(alphabet, maxlen) if M.accepts(w)}
        N = construct(M)
        for y in strings(alphabet, maxlen):
            if N.accepts(y) != (y in img):
                return False, (M, y)
    return ok, None


def preimage_check(construct, f, alphabet="01", maxlen=8, count=300):
    for M in test_dfas(count, alphabet):
        D = construct(M)
        for w in strings(alphabet, maxlen):
            if D.accepts(w) != M.accepts(f(w)):
                return False, (M, w)
    return True, None


# ============================================================== 4.8 rot
print("== 4.8")


def rot(w):
    return w[1:] + w[:1]


check("rot(0110) = 1100, rot(1) = 1, rot(eps) = eps", rot("0110") == "1100" and rot("1") == "1" and rot("") == "")


def rot_pre_dfa(M):
    Q1 = [("s1",)] + [(a, q) for a in M.alphabet for q in M.states]
    d = {}
    for a in M.alphabet:
        d[(("s1",), a)] = (a, M.start)
        for b in M.alphabet:
            for q in M.states:
                d[((a, q), b)] = (a, M.delta(q, b))
    A1 = [(a, q) for a in M.alphabet for q in M.states if M.delta(q, a) in M.accepting]
    if M.start in M.accepting:
        A1.append(("s1",))
    return DFA(M.alphabet, Q1, ("s1",), A1, d)


def rot_img_nfa(M):
    s2, f = ("s2",), ("f",)
    Q2 = [s2, f] + [(a, q) for a in M.alphabet for q in M.states]
    d = {(s2, EPS): {(a, M.delta(M.start, a)) for a in M.alphabet}}
    for a in M.alphabet:
        for q in M.states:
            for b in M.alphabet:
                T = {(a, M.delta(q, b))}
                if b == a and q in M.accepting:
                    T.add(f)
                d[((a, q), b)] = T
    A2 = {f} | ({s2} if M.start in M.accepting else set())
    return NFA(M.alphabet, Q2, s2, A2, d)


for alpha, cnt in (("01", 300), ("012", 100)):
    ok, bad = preimage_check(rot_pre_dfa, rot, alpha, 8 if alpha == "01" else 6, cnt)
    check(f"(a) DFA for {{w : rot(w) in L}} correct on {cnt + len(edge_dfas(alpha))} DFAs over {alpha}", ok, str(bad))
    ok, bad = image_check(rot_img_nfa, rot, alpha, 8 if alpha == "01" else 6, cnt)
    check(f"(b) NFA for {{rot(w) : w in L}} correct on {cnt + len(edge_dfas(alpha))} DFAs over {alpha}", ok, str(bad))
check("(a) |Q1| = 1 + |Sigma||Q|", all(len(rot_pre_dfa(M).states) == 1 + 2 * len(M.states) for M in test_dfas(20)))
S1 = Regex("1(0+1)*", "01").dfa()
check("check: L = 1(0+1)*: {w : rot(w) in L} = 1 + (0+1)1(0+1)*", Regex("1+(0+1)1(0+1)*", "01").equivalent(
    rot_pre_dfa(S1).minimize())[0])
check("check: L = 1(0+1)*: {rot(w) : w in L} = (0+1)*1",
      same_lang(rot_img_nfa(S1).accepts, Regex("(0+1)*1", "01").matches, "01", 10))
Eps = edge_dfas()["{eps}"]
check("{eps}: A1 = {s1} exactly", set(rot_pre_dfa(Eps).accepting) == {("s1",)})


def nfa_reachable(N):
    seen, stack = {N.start}, [N.start]
    while stack:
        q = stack.pop()
        for (p, a), T in N._delta.items():
            if p == q:
                for r in T:
                    if r not in seen:
                        seen.add(r)
                        stack.append(r)
    return seen


def rot_img_bad(M):
    N = rot_img_nfa(M)
    return NFA(M.alphabet, N.states, N.start, {(a, q) for a in M.alphabet for q in M.accepting} | ({("s2",)} if
               M.start in M.accepting else set()), N._delta)


check("watch out: accepting (a, q) with q in A (no move to f) accepts 0 for L = 1(0+1)*, but 0 is not in RotImg(L)",
      rot_img_bad(S1).accepts("0") and not rot_img_nfa(S1).accepts("0") and all(rot(w) != "0" for w in ["0", "1"] if S1(w)))
check("{eps}: the only reachable accepting state of M2 is s2",
      nfa_reachable(rot_img_nfa(Eps)) & rot_img_nfa(Eps).accepting == {("s2",)})
E = edge_dfas()
check("edge cases: empty -> empty, {eps} -> {eps}, Sigma* -> Sigma* (both parts)",
      all(same_lang(rot_pre_dfa(E[k]).accepts, E[k].accepts, "01", 8)
          and same_lang(rot_img_nfa(E[k]).accepts, E[k].accepts, "01", 8) for k in ("empty", "{eps}", "Sigma*")))

# ============================================================== 4.9 off
print("== 4.9")


def off(w):
    i = w.rfind("1")
    return w if i < 0 else w[:i] + "0" + w[i + 1:]


check("off(0110) = 0100, off(1011) = 1010, off(0000) = 0000, off(eps) = eps",
      [off(w) for w in ["0110", "1011", "0000", ""]] == ["0100", "1010", "0000", ""])
check("recursive form: off(eps)=eps, off(x0)=off(x)0, off(x1)=x0 for all |x| <= 10",
      off("") == "" and all(off(x + "0") == off(x) + "0" and off(x + "1") == x + "0" for x in strings("01", 10)))


def off_pre_dfa(M):
    Q1 = [(p, q) for p in M.states for q in M.states]
    d = {}
    for p, q in Q1:
        d[((p, q), "0")] = (M.delta(p, "0"), M.delta(q, "0"))
        d[((p, q), "1")] = (M.delta(p, "1"), M.delta(p, "0"))
    return DFA("01", Q1, (M.start, M.start), [(p, q) for p, q in Q1 if q in M.accepting], d)


def off_pre_nfa(M):
    """the guessing alternative: phases none / some / done"""
    Q1 = [(q, ph) for q in M.states for ph in ("none", "some", "done")]
    d = {}
    for q in M.states:
        for ph in ("none", "some"):
            d[((q, ph), "0")] = {(M.delta(q, "0"), ph)}
            d[((q, ph), "1")] = {(M.delta(q, "1"), "some"), (M.delta(q, "0"), "done")}
        d[((q, "done"), "0")] = {(M.delta(q, "0"), "done")}
    A1 = {(q, ph) for q in M.accepting for ph in ("none", "done")}
    return NFA("01", Q1, (M.start, "none"), A1, d)


def off_img_nfa(M):
    Q2 = [(q, ph) for q in M.states for ph in ("none", "some", "done")]
    d = {}
    for q in M.states:
        for ph in ("none", "some"):
            d[((q, ph), "0")] = {(M.delta(q, "0"), ph), (M.delta(q, "1"), "done")}
            d[((q, ph), "1")] = {(M.delta(q, "1"), "some")}
        d[((q, "done"), "0")] = {(M.delta(q, "0"), "done")}
    A2 = {(q, ph) for q in M.accepting for ph in ("none", "done")}
    return NFA("01", Q2, (M.start, "none"), A2, d)


ok, bad = preimage_check(off_pre_dfa, off)
check("(a) DFA (p, q) = (M on w, M on off(w)) for {w : off(w) in L}: correct on 304 DFAs", ok, str(bad))
ok, bad = preimage_check(off_pre_nfa, off)
check("(a) alternative guessing NFA (none/some/done) also correct on 304 DFAs", ok, str(bad))
ok = all(off_pre_dfa(M).delta_star((M.start, M.start), w) == (M.delta_star(M.start, w), M.delta_star(M.start, off(w)))
         for M in test_dfas(40) for w in strings("01", 8))
check("(a) invariant delta1*(s1, w) = (delta*(s, w), delta*(s, off(w))) on 44 DFAs, |w| <= 8", ok)
ok, bad = image_check(off_img_nfa, off)
check("(b) NFA (none/some/done) for {off(w) : w in L}: correct on 304 DFAs", ok, str(bad))
E = edge_dfas()
check("edge: L = Sigma*: image = eps + (0+1)*0; preimage = Sigma*",
      same_lang(off_img_nfa(E["Sigma*"]).accepts, Regex("ε+(0+1)*0", "01").matches, "01", 10)
      and same_lang(off_pre_dfa(E["Sigma*"]).accepts, lambda w: True, "01", 10))
check("edge: L = 1*: preimage = {eps}; image = eps + 1*0",
      same_lang(off_pre_dfa(E["1*"]).accepts, lambda w: w == "", "01", 10)
      and same_lang(off_img_nfa(E["1*"]).accepts, Regex("ε+1*0", "01").matches, "01", 10))
check("edge: empty -> empty and {eps} -> {eps} (both parts)",
      all(same_lang(off_pre_dfa(E[k]).accepts, E[k].accepts, "01", 8)
          and same_lang(off_img_nfa(E[k]).accepts, E[k].accepts, "01", 8) for k in ("empty", "{eps}")))
def off_img_bad(M):
    N = off_img_nfa(M)
    return NFA("01", N.states, N.start, {(q, ph) for q in M.accepting for ph in ("none", "some", "done")}, N._delta)


check("watch out: accepting (q, some) too accepts 11 for L = 1*", off_img_bad(E["1*"]).accepts("11"))
check("11 is not off(w) for any w (|w| = 2)", all(off(w) != "11" for w in strings("01", 2, 2)))
check("off(w) never ends in 1 (|w| <= 12)", all(not off(w).endswith("1") for w in strings("01", 12)))
check("|Q1| = |Q|^2, |Q2| = 3|Q|", all(len(off_pre_dfa(M).states) == len(M.states) ** 2
                                       and len(off_img_nfa(M).states) == 3 * len(M.states) for M in test_dfas(10)))

# ============================================================== 4.10 back
print("== 4.10")


def back(w):
    k = len(w) - len(w.lstrip("0"))
    return w[k:] + w[:k]


check("back(00101) = 10100, back(0011) = 1100, back(000) = 000, back(110) = 110",
      [back(w) for w in ["00101", "0011", "000", "110"]] == ["10100", "1100", "000", "110"])


def back_pre_dfa(M):
    Q = list(M.states)
    ident = tuple(Q)  # tau as the tuple (tau(q) for q in Q)
    idx = {q: i for i, q in enumerate(Q)}

    def step(state, a):
        if state[0] == "phase1":
            tau = state[1]
            if a == "0":
                return ("phase1", tuple(M.delta(tau[idx[q]], "0") for q in Q))
            return ("phase2", tau, M.delta(M.start, "1"))
        _, tau, q = state
        return ("phase2", tau, M.delta(q, a))

    def acc(state):
        if state[0] == "phase1":
            return state[1][idx[M.start]] in M.accepting
        _, tau, q = state
        return tau[idx[q]] in M.accepting

    return DFA.explore("01", ("phase1", ident), step, acc)


def back_pre_nfa(M):
    """alternative: guess r = delta*(s, x) at the start"""
    s1 = ("s1",)
    Q1 = [s1] + [("z", r, t) for r in M.states for t in M.states] + \
         [("x", r, t, q) for r in M.states for t in M.states for q in M.states]
    d = {(s1, EPS): {("z", r, r) for r in M.states}}
    for r in M.states:
        for t in M.states:
            d[(("z", r, t), "0")] = {("z", r, M.delta(t, "0"))}
            d[(("z", r, t), "1")] = {("x", r, t, M.delta(M.start, "1"))}
            for q in M.states:
                for a in "01":
                    d[(("x", r, t, q), a)] = {("x", r, t, M.delta(q, a))}
    A1 = {("z", M.start, t) for t in M.accepting} | {("x", r, t, r) for r in M.states for t in M.accepting}
    return NFA("01", Q1, s1, A1, d)


def back_img_nfa(M):
    s2 = ("s2",)
    Q2 = [s2] + [("zeros", q) for q in M.states] + [("body", p, q) for p in M.states for q in M.states] + \
         [("tail", p, r) for p in M.states for r in M.states]
    d = {(s2, EPS): {("zeros", M.start)}, (s2, "1"): {("body", p, M.delta(p, "1")) for p in M.states}}
    for q in M.states:
        d[(("zeros", q), "0")] = {("zeros", M.delta(q, "0"))}
    for p in M.states:
        for q in M.states:
            for a in "01":
                d[(("body", p, q), a)] = {("body", p, M.delta(q, a))}
            if q in M.accepting:
                d[(("body", p, q), EPS)] = {("tail", p, M.start)}
            d[(("tail", p, q), "0")] = {("tail", p, M.delta(q, "0"))}
    A2 = {("zeros", q) for q in M.accepting} | {("tail", p, p) for p in M.states}
    return NFA("01", Q2, s2, A2, d)


ok, bad = preimage_check(back_pre_dfa, back)
check("(a) DFA (tau, then (tau, q)) for {w : back(w) in L}: correct on 304 DFAs", ok, str(bad))
ok, bad = preimage_check(back_pre_nfa, back)
check("(a) alternative NFA guessing r = delta*(s, x): correct on 304 DFAs", ok, str(bad))
ok, bad = image_check(back_img_nfa, back)
check("(b) NFA (zeros / body / tail) for {back(w) : w in L}: correct on 304 DFAs", ok, str(bad))
E = edge_dfas()
check("edge: Sigma* -> preimage Sigma*, image 0* + 1(0+1)*",
      same_lang(back_pre_dfa(E["Sigma*"]).accepts, lambda w: True, "01", 10)
      and same_lang(back_img_nfa(E["Sigma*"]).accepts, Regex("0*+1(0+1)*", "01").matches, "01", 10))
check("edge: empty -> empty, {eps} -> {eps}, 1* -> 1* (both parts)",
      all(same_lang(back_pre_dfa(E[k]).accepts, E[k].accepts, "01", 8)
          and same_lang(back_img_nfa(E[k]).accepts, E[k].accepts, "01", 8) for k in ("empty", "{eps}", "1*")))
M10 = Regex("10*", "01").dfa()
check("check: L = 10*: preimage = 0*10* (exactly one 1), image = 10*",
      Regex("0*10*", "01").equivalent(back_pre_dfa(M10).minimize())[0]
      and same_lang(back_img_nfa(M10).accepts, Regex("10*", "01").matches, "01", 10))
M01b = Regex("0*1", "01").dfa()
check("check: L = 0*1: preimage = {1}, image = 10*",
      same_lang(back_pre_dfa(M01b).accepts, lambda w: w == "1", "01", 10)
      and same_lang(back_img_nfa(M01b).accepts, Regex("10*", "01").matches, "01", 10))
check("every image string starts with 1 or is in 0* (304 DFAs, |w| <= 8)",
      all(back(w) == "" or back(w)[0] == "1" or set(back(w)) == {"0"} for w in strings("01", 12)))
check("back(010) = 100", back("010") == "100")


def back_img_nozeros(M):
    N = back_img_nfa(M)
    d = {k: v for k, v in N._delta.items() if k != (("s2",), EPS)}
    return NFA("01", N.states, N.start, N.accepting, d)


M0s = Regex("0*", "01").dfa()
check("watch out: without the zeros branch, L = 0* gives nothing; BackImg(0*) = 0*",
      same_lang(back_img_nozeros(M0s).accepts, lambda w: False, "01", 10)
      and same_lang(back_img_nfa(M0s).accepts, lambda w: set(w) <= {"0"}, "01", 10))
check("|Q1| (reachable part) <= |Q|^|Q| (1 + |Q|)",
      all(len(back_pre_dfa(M).states) <= len(M.states) ** len(M.states) * (1 + len(M.states)) for M in test_dfas(30)))
check("|Q2| = 1 + |Q| + 2|Q|^2", all(len(back_img_nfa(M).states) == 1 + len(M.states) + 2 * len(M.states) ** 2
                                     for M in test_dfas(10)))

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: {FAIL}")
sys.exit(1 if FAIL else 0)
