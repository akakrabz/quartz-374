#!/usr/bin/env python3
"""Checks for the concrete claims on the toolkit pages that are not already checked on a chapter page:
content/0-toolkit/03-the-big-picture.md, 04-review-regular-and-context-free.md and
05-review-turing-machines-and-undecidability.md.

Everything else on those pages summarizes a chapter page and is checked by tools/checks/chNN.py."""
import os
import random
import sys
from itertools import product

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from automata import CFG, DFA, EPS, NFA, Regex, first_difference, strings  # noqa: E402
from automata.regex import to_str  # noqa: E402

FAIL = []
AB = "01"
rng = random.Random(374)


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail and not cond else ""))
    if not cond:
        FAIL.append(name)


def grammar_is(text, pred, alphabet=AB, maxlen=12):
    G = CFG.parse(text)
    bad = first_difference(G.generates, pred, alphabet, maxlen)
    return bad is None, bad


def fooling(F, z, inL, n=13):
    """F(i) is the i-th string of the fooling set, z(i, j) the suffix for x = F(i), y = F(j); exactly one of
    xz, yz must be in L — here, as in every proof on the pages, xz in L and yz not in L."""
    for i in range(n):
        for j in range(n):
            if i != j:
                x, y, zz = F(i), F(j), z(i, j)
                if not (inL(x + zz) and not inL(y + zz)):
                    return False, (x, y, zz)
    return True, None


# ================================================================ 03 the big picture: the language zoo
pal = lambda w: w == w[::-1]
wwR = lambda w: len(w) % 2 == 0 and pal(w)
eq01 = lambda w: w.count("0") == w.count("1")
on1n = lambda w: any(w == "0" * k + "1" * k for k in range(len(w) // 2 + 1))


def balanced(w):
    d = 0
    for c in w:
        d += 1 if c == "(" else -1
        if d < 0:
            return False
    return d == 0


def mneq(w):
    m = len(w) - len(w.lstrip("0"))
    rest = w[m:]
    return set(rest) <= {"1"} and m != len(rest)


def zoz(w):
    n = len(w) // 3
    return len(w) % 3 == 0 and w == "0" * n + "1" * n + "0" * n


def wsharpw(w):
    if w.count("#") != 1:
        return False
    a, b = w.split("#")
    return a == b


ok, bad = grammar_is("S -> 0S0 | 1S1 | ε", wwR)
check("zoo: S -> 0S0 | 1S1 | ε generates exactly {ww^R} (|w| <= 12)", ok, str(bad))
ok, bad = grammar_is("S -> 0S0 | 1S1 | 0 | 1 | ε", pal)
check("zoo: S -> 0S0 | 1S1 | 0 | 1 | ε generates exactly the palindromes (|w| <= 12)", ok, str(bad))
ok, bad = grammar_is("S -> 0S0 | 1S1 | 0Z1 | 1Z0\nZ -> ε | 0Z | 1Z", lambda w: not pal(w))
check("zoo: the non-palindrome grammar of §5.4 (|w| <= 12)", ok, str(bad))
ok, bad = grammar_is("S -> 0S1 | 1S0 | SS | ε", eq01)
check("zoo: S -> 0S1 | 1S0 | SS | ε generates exactly #0 = #1 (|w| <= 12)", ok, str(bad))
ok, bad = grammar_is("S -> A | B\nA -> 0A | 0C\nB -> B1 | C1\nC -> ε | 0C1", mneq)
check("zoo: the running example of §5.1 generates {0^m 1^n : m != n} (|w| <= 12)", ok, str(bad))
ok, bad = grammar_is("C -> ε | 0C1", on1n)
check("zoo: C -> ε | 0C1 generates {0^n 1^n} (|w| <= 12)", ok, str(bad))
ok, bad = grammar_is("S -> 0S1S | 1S0S | ε", eq01)
check("review: S -> 0S1S | 1S0S | ε generates exactly #0 = #1 (|w| <= 12)", ok, str(bad))
ok, bad = grammar_is("S -> 0S1 | 1S0 | SS | 0 | ε", lambda w: w.count("0") >= w.count("1"))
check("review: S -> 0S1 | 1S0 | SS | 0 | ε generates exactly #0 >= #1 (|w| <= 12)", ok, str(bad))
ok, bad = grammar_is("S -> (S)S | ε", balanced, alphabet="()")
check("zoo: S -> (S)S | ε generates exactly the balanced parentheses (|w| <= 12)", ok, str(bad))
ok, bad = grammar_is("S -> (S) | SS | ε", balanced, alphabet="()")
check("zoo: S -> (S) | SS | ε generates exactly the balanced parentheses (|w| <= 12)", ok, str(bad))

ok, bad = fooling(lambda i: "0" * i, lambda i, j: "1" * i, on1n)
check("fooling set 0* with z = 1^i for {0^n 1^n} (i != j < 13)", ok, str(bad))
ok, bad = fooling(lambda i: "0" * i + "1", lambda i, j: "1" + "0" * i, wwR)
check("fooling set 0*1 with z = 10^i for {ww^R} (i != j < 13)", ok, str(bad))
ok, bad = fooling(lambda i: "0" * i + "1", lambda i, j: "1" + "0" * i, pal)
check("the same fooling set and suffixes work for the palindromes (i != j < 13)", ok, str(bad))
ok, bad = fooling(lambda i: "(" * i, lambda i, j: ")" * i, balanced)
check("fooling set (* with z = )^i for balanced parentheses (i != j < 13)", ok, str(bad))
ok, bad = fooling(lambda i: "0" * i, lambda i, j: "1" * i, eq01)
check("fooling set 0* with z = 1^i for #0 = #1 (i != j < 13)", ok, str(bad))
ok, bad = fooling(lambda i: "0" * i, lambda i, j: "1" * i + "0" * i, zoz)
check("fooling set 0* with z = 1^i 0^i for {0^n 1^n 0^n} (i != j < 13)", ok, str(bad))
ok, bad = fooling(lambda i: "0" * i, lambda i, j: "#" + "0" * i, wsharpw)
check("fooling set 0* with z = #0^i for {w#w} (i != j < 13)", ok, str(bad))
pow2 = lambda w: set(w) <= {"0"} and len(w) > 0 and (len(w) & (len(w) - 1)) == 0
ok, bad = fooling(lambda i: "0" * 2 ** i, lambda i, j: "0" * 2 ** i, pow2, n=9)
check("fooling set {0^(2^n)} with z = 0^(2^i) for {0^(2^n)} (Lemma 3.8; i != j < 9)", ok, str(bad))

# {0^m 1^n : m != n} is not regular by closure: its complement intersected with 0*1* is {0^n 1^n}
in01 = lambda w: "10" not in w
check("closure: complement({0^m 1^n : m != n}) ∩ 0*1* = {0^n 1^n} (|w| <= 14)",
      first_difference(lambda w: (not mneq(w)) and in01(w), on1n, AB, 14) is None)
check("closure: the complement of the non-palindromes is the palindromes (|w| <= 12)",
      all((not (not pal(w))) == pal(w) for w in strings(AB, 12)))
check("zoo: (0+1)*00 = the strings that end in 00 (exact, against a 3-state DFA)",
      Regex("(0+1)*00").equivalent(DFA(AB, [0, 1, 2], 0, [2], lambda q, a: min(q + 1, 2) if a == "0" else 0))[0])
M5 = DFA(AB, range(5), 0, [0], lambda q, a: (2 * q + int(a)) % 5)
check("zoo: the mod-5 DFA accepts the binary multiples of 5 (ε read as 0; |w| <= 14)",
      first_difference(M5.accepts, lambda w: (int(w, 2) if w else 0) % 5 == 0, AB, 14) is None)

# ================================================================ 04 review: the construction formulas
def random_dfa(n=None):
    n = n or rng.choice([1, 2, 3, 4])
    return DFA(AB, range(n), 0, [q for q in range(n) if rng.random() < 0.5],
               {(q, a): rng.randrange(n) for q in range(n) for a in AB})


def random_enfa():
    n = rng.choice([2, 3, 4])
    d = {}
    for q in range(n):
        for a in AB + EPS:
            if a == EPS:
                T = {r for r in range(n) if r != q and rng.random() < 0.25}
            else:
                T = {r for r in range(n) if rng.random() < 0.35}
            if T:
                d[(q, a)] = T
    return NFA(AB, range(n), 0, {q for q in range(n) if rng.random() < 0.4}, d)


DFAS = [random_dfa() for _ in range(150)]
ENFAS = [random_enfa() for _ in range(150)]

# product construction: Q1 x Q2, start (s1, s2), delta componentwise; the accepting set picks the operation
OPS = {"∩": lambda x, y: x and y, "∪": lambda x, y: x or y, "∖": lambda x, y: x and not y, "⊕": lambda x, y: x != y}


def product_dfa(M1, M2, op):
    Q = [(p, q) for p in M1.states for q in M2.states]
    A = [(p, q) for (p, q) in Q if OPS[op](p in M1.accepting, q in M2.accepting)]
    return DFA(AB, Q, (M1.start, M2.start), A, lambda pq, a: (M1.delta(pq[0], a), M2.delta(pq[1], a)))


ok = all(all(product_dfa(M1, M2, op).accepts(w) == OPS[op](M1.accepts(w), M2.accepts(w)) for w in strings(AB, 8))
         for M1, M2 in zip(DFAS[:60], DFAS[60:120]) for op in OPS)
check("product construction: the accepting sets for ∩, ∪, ∖, ⊕ (60 random pairs of DFAs, |w| <= 8)", ok)
ok = all(all(DFA(AB, M.states, M.start, set(M.states) - M.accepting, M._delta).accepts(w) != M.accepts(w)
             for w in strings(AB, 8)) for M in DFAS)
check("complement: accept Q \\ A (150 random DFAs, |w| <= 8)", ok)


def eps_reach(N, S):
    return N.eps_reach(set(S))


def remove_eps(N):
    """A' = {q : ε-reach(q) meets A}; δ'(q, a) = δ(ε-reach(q), a)."""
    A2 = {q for q in N.states if eps_reach(N, {q}) & N.accepting}
    d = {}
    for q in N.states:
        for a in AB:
            T = set()
            for r in eps_reach(N, {q}):
                T |= N.delta(r, a)
            if T:
                d[(q, a)] = T
    return NFA(AB, N.states, N.start, A2, d)


ok = all(all(remove_eps(N).accepts(w) == N.accepts(w) for w in strings(AB, 8)) and not remove_eps(N).has_epsilon()
         for N in ENFAS)
check("ε-removal formula: same states, A' and δ' as on the page (150 random ε-NFAs, |w| <= 8)", ok)


def subset_dfa(N):
    """s' = {s}; A' = {S : ε-reach(S) meets A}; δ'(S, a) = ∪_{p ∈ S} ∪_{r ∈ ε-reach(p)} δ(r, a)."""
    s0 = frozenset({N.start})
    seen, todo, d = {s0}, [s0], {}
    while todo:
        S = todo.pop()
        for a in AB:
            T = set()
            for p in S:
                for r in eps_reach(N, {p}):
                    T |= N.delta(r, a)
            T = frozenset(T)
            d[(S, a)] = T
            if T not in seen:
                seen.add(T)
                todo.append(T)
    return DFA(AB, list(seen), s0, [S for S in seen if eps_reach(N, S) & N.accepting], d)


ok = all(all(subset_dfa(N).accepts(w) == N.accepts(w) for w in strings(AB, 8)) for N in ENFAS)
check("subset construction formula with ε-reach (150 random ε-NFAs, |w| <= 8)", ok)
check("subset construction: at most 2^|Q| reachable subsets", all(len(subset_dfa(N).states) <= 2 ** len(N.states)
                                                                  for N in ENFAS))


# Thompson's algorithm, both star gadgets
def thompson(node, star_back):
    n, d = [0], {}

    def new():
        n[0] += 1
        return n[0] - 1

    def add(p, a, q):
        d.setdefault((p, a), set()).add(q)

    def build(x):
        k = x[0]
        if k == "empty":
            return new(), new()
        if k in ("eps", "sym"):
            s, t = new(), new()
            add(s, EPS if k == "eps" else x[1], t)
            return s, t
        if k == "cat":
            s1, t1 = build(x[1])
            s2, t2 = build(x[2])
            add(t1, EPS, s2)                       # in series: ε-edge from t_S to s_T
            return s1, t2
        if k == "union":
            s = new()
            s1, t1 = build(x[1])
            s2, t2 = build(x[2])
            t = new()
            for p, q in ((s, s1), (s, s2), (t1, t), (t2, t)):
                add(p, EPS, q)
            return s, t
        if k == "star":
            s = new()
            s1, t1 = build(x[1])
            t = new()
            add(s, EPS, s1)
            add(t1, EPS, t)
            add(s, EPS, t)                        # zero copies
            if star_back == "t->s":
                add(t, EPS, s)                    # repeat: back edge between the new states
            else:
                add(t1, EPS, s1)                  # repeat: back edge inside the gadget
            return s, t
        raise ValueError(k)

    s, t = build(node)
    return NFA(AB, range(n[0]), s, {t}, d)


def asts(size):
    if size == 1:
        return [("empty",), ("eps",), ("sym", "0"), ("sym", "1")]
    out = [("star", x) for x in asts(size - 1)]
    for k in range(1, size - 1):
        for x in asts(k):
            for y in asts(size - 1 - k):
                out += [("cat", x, y), ("union", x, y)]
    return out


def count_nodes(x, kinds):
    return (1 if x[0] in kinds else 0) + sum(count_nodes(c, kinds) for c in x[1:] if isinstance(c, tuple))


ALL = [x for s in range(1, 6) for x in asts(s)]
for back in ("t->s", "tS->sS"):
    ok_lang = all(Regex(to_str(x), alphabet=AB).equivalent(thompson(x, back).to_dfa())[0] for x in ALL)
    check(f"Thompson gadgets with the star back edge {back}: L(NFA) = L(R) for all {len(ALL)} expressions of "
          f"size <= 5 (exact)", ok_lang)
ok_shape = all(len(thompson(x, "t->s").accepting) == 1 and thompson(x, "t->s").start not in
               thompson(x, "t->s").accepting for x in ALL)
check("Thompson: exactly one accepting state, different from the start state (Lemma 4.2)", ok_shape)
ok_cnt = all(len(thompson(x, "t->s").states) == 2 * count_nodes(x, {"empty", "eps", "sym", "union", "star"})
             for x in ALL)
check("Thompson: 2 states per leaf, per + and per *; none per concatenation", ok_cnt)
x14 = Regex("(0+10*1)*").ast
check("Thompson: (0+10*1)* has 2 x (4 leaves + 1 union + 2 stars) = 14 states", len(thompson(x14, "t->s").states) == 14)
for back in ("t->s", "tS->sS"):
    D14 = subset_dfa(thompson(x14, back))
    check(f"(0+10*1)*, star edge {back}: 14 NFA states -> 5 DFA states -> 2 after minimization",
          len(D14.states) == 5 and D14.minimize().num_states() == 2, f"{len(D14.states)}")
    x26 = Regex("(0+1)*(00+11)(0+1)*").ast
    N26 = thompson(x26, back)
    D26 = subset_dfa(N26)
    check(f"(0+1)*(00+11)(0+1)*, star edge {back}: 26 literal NFA states -> 9 DFA states (6 accepting) -> minimal 4",
          len(N26.states) == 26 and len(D26.states) == 9 and len(D26.accepting) == 6 and D26.minimize().num_states() == 4,
          f"{len(N26.states)}, {len(D26.states)}, {len(D26.accepting)}")


# state elimination: R'(p -> r) = R(p -> r) + R(p -> q) R(q -> q)* R(q -> r), for every remaining p, r (p = r too)
def elim_expr(M):
    states = list(M.states)
    R = {}

    def u(a, b):
        if a is None:
            return b
        if b is None:
            return a
        return f"{a}+{b}"

    def put(p, q, e):
        R[(p, q)] = u(R.get((p, q)), e)

    for q in states:
        for a in AB:
            put(q, M.delta(q, a), a)
    put("s", M.start, "ε")
    for q in M.accepting:
        put(q, "t", "ε")
    remaining = ["s"] + states + ["t"]
    for q in states:
        loop = R.get((q, q))
        star = f"({loop})*" if loop is not None else "ε"
        for p in remaining:
            for r in remaining:
                if p == q or r == q or R.get((p, q)) is None or R.get((q, r)) is None:
                    continue
                put(p, r, f"({R[(p, q)]}){star}({R[(q, r)]})")
        remaining.remove(q)
        R = {k: v for k, v in R.items() if q not in k}
    return R.get(("s", "t"), "∅")


ok = all(Regex(elim_expr(M), alphabet=AB).equivalent(M)[0] for M in DFAS[:80] if len(M.states) <= 3)
check("state elimination rule (with p = r) gives an equivalent expression (random DFAs with <= 3 states, exact)", ok)


def reverse_nfa(M):
    """Lemma 4.4: Q^R = Q ∪ {s^R}; start s^R; A^R = {s}; δ^R(s^R, ε) = A; δ^R(q, a) = {p : δ(p, a) = q}."""
    d = {("sR", EPS): set(M.accepting)}
    for p in M.states:
        for a in AB:
            d.setdefault((M.delta(p, a), a), set()).add(p)
    return NFA(AB, ["sR"] + list(M.states), "sR", {M.start}, d)


def half_nfa(M):
    """Lemma 4.5: Q' = Q×Q×Q ∪ {s'}; δ'(s', ε) = {(s, h, h) : h ∈ Q}; δ'((p, h, q), a) = {(δ(p, a), h, δ(q, a))};
    A' = {(h, h, q) : h ∈ Q, q ∈ A}."""
    Q3 = [(p, h, q) for p in M.states for h in M.states for q in M.states]
    d = {("s'", EPS): {(M.start, h, h) for h in M.states}}
    for (p, h, q) in Q3:
        for a in AB:
            d[((p, h, q), a)] = {(M.delta(p, a), h, M.delta(q, a))}
    return NFA(AB, ["s'"] + Q3, "s'", {(h, h, q) for h in M.states for q in M.accepting}, d)


check("reversal NFA (Lemma 4.4) accepts w iff M accepts w^R (150 random DFAs, |w| <= 9)",
      all(all(reverse_nfa(M).accepts(w) == M.accepts(w[::-1]) for w in strings(AB, 9)) for M in DFAS))
check("half NFA (Lemma 4.5) accepts w iff M accepts ww (150 random DFAs, |w| <= 6)",
      all(all(half_nfa(M).accepts(w) == M.accepts(w + w) for w in strings(AB, 6)) for M in DFAS))


def rev_ast(x):
    k = x[0]
    if k in ("empty", "eps", "sym"):
        return x
    if k == "union":
        return ("union", rev_ast(x[1]), rev_ast(x[2]))
    if k == "cat":
        return ("cat", rev_ast(x[2]), rev_ast(x[1]))     # order swapped
    return ("star", rev_ast(x[1]))


ok = all(first_difference(Regex(to_str(rev_ast(x)), alphabet=AB).matches,
                          lambda w, x=x: Regex(to_str(x), alphabet=AB).matches(w[::-1]), AB, 7) is None
         for x in ALL if count_nodes(x, {"cat"}) > 0)
check("regular-expression reversal rules (concatenation swapped) on every expression of size <= 5 with a "
      "concatenation (|w| <= 7)", ok)

# ================================================================ 04 review: true/false witnesses
star_ok = [True] + [False] * 40          # star_ok[m]: 0^m ∈ L* for L = {0^(2^n) : n >= 0}
for m in range(1, 41):
    star_ok[m] = any(star_ok[m - k] for k in range(1, m + 1) if pow2("0" * k))
check("{0^(2^n) : n >= 0}* = 0* (every unary string up to length 40), although {0^(2^n)} is not regular",
      all(star_ok) and pow2("0"))
L0s1 = lambda w: w.endswith("1") and set(w[:-1]) <= {"0"}             # 0*1
ww_of = lambda w: len(w) % 2 == 0 and w[:len(w) // 2] == w[len(w) // 2:] and L0s1(w[:len(w) // 2])
ok, bad = fooling(lambda i: "0" * i, lambda i, j: "1" + "0" * i + "1", ww_of)
check("{ww : w ∈ 0*1} = {0^n 1 0^n 1}: fooling set 0* with z = 10^i1 (i != j < 13)", ok, str(bad))
check("{ww : w ∈ 0*1} is exactly {0^n 1 0^n 1} (|w| <= 14)",
      first_difference(ww_of, lambda w: any(w == "0" * n + "1" + "0" * n + "1" for n in range(8)), AB, 14) is None)

print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: {FAIL}")
sys.exit(1 if FAIL else 0)
