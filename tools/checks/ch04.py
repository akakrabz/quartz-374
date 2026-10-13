#!/usr/bin/env python3
"""Checks for every concrete claim on content/1-models-of-computation/04-nondeterministic-automata.md.

Notes
* Thompson's algorithm is implemented here with the book's star gadget (new s and t; s -ε-> s_S, t_S -ε-> t,
  s -ε-> t, and the loop t -ε-> s). It reproduces the book's subset tables, including s in ε-reach({k}); the
  library's gadget (loop t_S -ε-> s_S, the common textbook form) is checked to be correct as well.
* Every transformation of §4.9 is implemented as a function of an arbitrary DFA and compared with the definition
  of the transformed language on 300 random DFAs with 2-4 states and on DFAs for ∅, {ε}, 1*, Σ*.
"""
import os
import random
import sys
from itertools import combinations, permutations, product

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from automata import DFA, NFA, EPS, Regex, eliminate_states, strings, first_difference  # noqa: E402
from automata.core import equivalent  # noqa: E402
from automata.regex import _Parser, to_str, _u, _c, _s  # noqa: E402

FAIL = []


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAIL.append(name)


AB = "01"


def R(text):
    return Regex(text, alphabet=AB)


def same(a, b):
    return R(a).equivalent(R(b))[0]


def nm(S):
    """A set of letter-named states as the page writes it (s first, then alphabetical); ∅ for the empty set."""
    return "".join(sorted(S, key=lambda c: (c != "s", c))) or "∅"


def agrees(machine, pred, n=12):
    return first_difference(machine.accepts, pred, AB, n) is None


def run_sets(N, w, start=None):
    """The sets of current states (ε-closed) after each prefix of w."""
    S = N.eps_reach({N.start if start is None else start})
    out = [S]
    for a in w:
        S = N.eps_reach(N.step(S, a))
        out.append(S)
    return out


def val(w):
    return int(w, 2) if w else 0


has_pair = lambda w: "00" in w or "11" in w

# =============================================================== 4.1 the NFA for "contains 00 or 11"
N41 = NFA(AB, "sabc", "s", ["c"], {("s", "0"): {"s", "a"}, ("s", "1"): {"s", "b"}, ("a", "0"): {"c"},
                                   ("b", "1"): {"c"}, ("c", "0"): {"c"}, ("c", "1"): {"c"}})
check("4.1 the NFA s, a, b, c accepts exactly the strings that contain 00 or 11 (|w| <= 14)", agrees(N41, has_pair, 14))
check("4.1 two transitions out of s for each symbol; a has none on 1, b none on 0; c loops on both",
      N41.delta("s", "0") == {"s", "a"} and N41.delta("s", "1") == {"s", "b"} and N41.delta("a", "1") == set()
      and N41.delta("b", "0") == set() and N41.delta("c", "0") == N41.delta("c", "1") == {"c"})


def legal_walk(N, w, walk):
    return len(walk) == len(w) + 1 and walk[0] == N.start and all(walk[i + 1] in N.delta(walk[i], a)
                                                                    for i, a in enumerate(w))


check("4.1 0110: the walk s,s,b,c,c is legal and accepts; the walk that stays in s ends in s; s -0-> a gets stuck",
      legal_walk(N41, "0110", "ssbcc") and "c" in N41.accepting and legal_walk(N41, "0110", "sssss")
      and N41.delta("a", "1") == set())


def dstar(N, q, w):
    """The book's recursive δ* without ε: {q} if w = ε, else the union of δ*(r, x) over r in δ(q, a)."""
    if not w:
        return {q}
    out = set()
    for r in N.delta(q, w[0]):
        out |= dstar(N, r, w[1:])
    return out


check("4.1 the recursive δ*(s, w) equals the set C obtained by tracking current states (|w| <= 10)",
      all(dstar(N41, "s", w) == set(N41.current_states(w)) for w in strings(AB, 10)))
t1 = [nm(S) for S in run_sets(N41, "10010")]
t2 = [nm(S) for S in run_sets(N41, "0101")]
check("4.1 run on 10010: {s}, {s,b}, {s,a}, {s,a,c}, {s,b,c}, {s,a,c}; accepted",
      t1 == ["s", "sb", "sa", "sac", "sbc", "sac"] and N41.accepts("10010"), str(t1))
check("4.1 run on 0101: {s}, {s,a}, {s,b}, {s,a}, {s,b}; rejected",
      t2 == ["s", "sa", "sb", "sa", "sb"] and not N41.accepts("0101"), str(t2))
check("4.1 the thread in b dies on the second symbol of 10010 (δ(b,0) = ∅)", N41.delta("b", "0") == set())
SW = NFA(AB, "sabc", "s", ["s", "a", "b"], N41._delta)
check("4.1 trap: with A = {s,a,b} the NFA accepts every string (|w| <= 12), not the complement",
      all(SW.accepts(w) for w in strings(AB, 12)) and SW.accepts("00"))

# =============================================================== 4.2 proofs as oracle strings
QS = "sabc"


def verifier(w, omega):
    """DFA over Σ×Q: from q, the pair (a, r) leads to r if r ∈ δ(q,a), else to a dump state (None)."""
    q = "s"
    for a, r in zip(w, omega):
        q = r if (q is not None and r in N41.delta(q, a)) else None
    return q is not None and q in N41.accepting


check("4.2 M accepts w iff some ω ∈ Q^|w| makes the verifier DFA over Σ×Q accept (|w| <= 6)",
      all(N41.accepts(w) == any(verifier(w, om) for om in product(QS, repeat=len(w))) for w in strings(AB, 6)))
check("4.2 the proof for 0110 is ω = s b c c", verifier("0110", "sbcc"))

# =============================================================== 4.3 ε-transitions: the NFA E for 0*1*0*
E = NFA(AB, "pqr", "p", ["r"], {("p", "0"): {"p"}, ("p", EPS): {"q"}, ("q", "1"): {"q"}, ("q", EPS): {"r"},
                                ("r", "0"): {"r"}})
one_block = lambda w: "0" not in w.strip("0")
check("4.3 E accepts exactly the strings whose 1s form a single block (|w| <= 14)", agrees(E, one_block, 14))
check("4.3 L(E) = 0*1*0* (exact)", R("0*1*0*").equivalent(E.to_dfa())[0])
check("4.3 ε-reach(p) = {p,q,r}, ε-reach(q) = {q,r}, ε-reach(r) = {r}",
      E.eps_reach("p") == set("pqr") and E.eps_reach("q") == set("qr") and E.eps_reach("r") == {"r"})


_MEMO = {}


def dstar_eps(N, p, w):
    """δ*(p, ε) = ε-reach(p); δ*(p, ax) = union over r ∈ ε-reach(p), q ∈ δ(r, a) of δ*(q, x).
    (The book's recursive definition, memoized so that dense random NFAs stay fast.)"""
    key = (id(N), p, w)
    if key in _MEMO:
        return set(_MEMO[key])
    if not w:
        out = set(N.eps_reach(p))
    else:
        out = set()
        for r in N.eps_reach(p):
            for q in N.delta(r, w[0]):
                out |= dstar_eps(N, q, w[1:])
    _MEMO[key] = frozenset(out)
    return out


check("4.3 the recursive δ* with ε-reach equals set tracking from every state (|w| <= 10)",
      all(dstar_eps(E, q, w) == set(run_sets(E, w, q)[-1]) for q in "pqr" for w in strings(AB, 10)))
r1 = [nm(S) for S in run_sets(E, "0010")]
r2 = [nm(S) for S in run_sets(E, "01010")]
check("4.3 on 0010 the sets are {p,q,r}, {p,q,r}, {p,q,r}, {q,r}, {r}: accepted",
      r1 == ["pqr", "pqr", "pqr", "qr", "r"] and E.accepts("0010"), str(r1))
check("4.3 on 01010 the set becomes empty after the second 1", r2[:4] == ["pqr", "pqr", "qr", "r"]
      and r2[4] == r2[5] == "∅" and not E.accepts("01010"), str(r2))


def remove_eps(N):
    """A' = {q : ε-reach(q) meets A}; δ'(q, a) = union of δ(r, a) over r ∈ ε-reach(q)."""
    A2 = {q for q in N.states if N.eps_reach(q) & N.accepting}
    d = {}
    for q in N.states:
        for a in N.alphabet:
            T = set()
            for r in N.eps_reach(q):
                T |= N.delta(r, a)
            if T:
                d[(q, a)] = T
    return NFA(N.alphabet, N.states, N.start, A2, d)


E2 = remove_eps(E)
tab = {(q, a): nm(E2.delta(q, a)) for q in "pqr" for a in AB}
check("4.3 ε-removal on E: A' = {p,q,r}", E2.accepting == set("pqr"))
check("4.3 ε-removal table: δ'(p,0) = {p,r}, δ'(p,1) = {q}, δ'(q,0) = {r}, δ'(q,1) = {q}, δ'(r,0) = {r}, δ'(r,1) = ∅",
      tab == {("p", "0"): "pr", ("p", "1"): "q", ("q", "0"): "r", ("q", "1"): "q", ("r", "0"): "r", ("r", "1"): "∅"},
      str(tab))
check("4.3 the new edges are exactly p -1-> q, p -0-> r, q -0-> r",
      {(q, a, t) for (q, a), T in E2._delta.items() for t in T} - {(q, a, t) for (q, a), T in E._delta.items()
                                                                   for t in T}
      == {("p", "1", "q"), ("p", "0", "r"), ("q", "0", "r")})
check("4.3 E' has no ε-transitions and accepts the same language (exact); the library's remove_epsilon agrees",
      not E2.has_epsilon() and equivalent(E2.to_dfa(), E.to_dfa())[0]
      and E.remove_epsilon().accepting == E2.accepting
      and {k: v for k, v in E.remove_epsilon()._delta.items() if v} == {k: v for k, v in E2._delta.items() if v})


def dstar_plain(N, q, w):
    S = {q}
    for a in w:
        S = set().union(*(N.delta(r, a) for r in S)) if S else set()
    return S


def removal_claim(N, n=9):
    N2 = remove_eps(N)
    return all(set(N.eps_reach(dstar_plain(N2, q, w))) == dstar_eps(N, q, w) for q in N.states
               for w in strings(N.alphabet, n))


rng = random.Random(4)


def random_eps_nfa(n):
    d = {}
    for q in range(n):
        for a in (*AB, EPS):
            T = {r for r in range(n) if rng.random() < 0.3}
            if T:
                d[(q, a)] = T
    return NFA(AB, range(n), 0, {q for q in range(n) if rng.random() < 0.4}, d)


RANDE = [random_eps_nfa(rng.choice([2, 3, 4])) for _ in range(60)]
check("4.3 proof claim ε-reach(δ'*(q,w)) = δ*(q,w) for every q (E and 60 random ε-NFAs, |w| <= 9 / 7)",
      removal_claim(E) and all(removal_claim(N, 7) for N in RANDE))
check("4.3 ε-removal preserves the language of 60 random ε-NFAs (exact)",
      all(equivalent(remove_eps(N).to_dfa(), N.to_dfa())[0] for N in RANDE))
E_bad = NFA(AB, "pqr", "p", ["r"], E2._delta)
check("4.3 trap: keeping A' = A = {r} rejects ε, 1 and 01 (all in L(E)) but still accepts 0",
      not any(E_bad.accepts(w) for w in ("", "1", "01")) and all(one_block(w) for w in ("", "1", "01"))
      and E_bad.accepts("0"))

# =============================================================== 4.5 subset construction
D, rows = E.subset_construction()
got = [(nm(S), nm(Rr), acc, nm(t["0"]), nm(t["1"])) for S, Rr, acc, t in rows]
want = [("p", "pqr", True, "pr", "q"), ("pr", "pqr", True, "pr", "q"), ("q", "qr", True, "r", "q"),
        ("r", "r", True, "r", "∅"), ("∅", "∅", False, "∅", "∅")]
check("4.5 incremental table for E: rows {p}, {p,r}, {q}, {r}, ∅ exactly as printed", got == want, str(got))
check("4.5 5 of the 2^3 = 8 subsets are reachable, and the DFA accepts 0*1*0* (|w| <= 14)",
      len(D.states) == 5 and agrees(D, one_block, 14))
meaning45 = {"p": lambda w: w == "", "pr": lambda w: w != "" and set(w) == {"0"},
             "q": lambda w: R("0*11*")(w), "r": lambda w: R("0*11*00*")(w), "∅": lambda w: not one_block(w)}
check("4.5 'reached by' column: ε, 0+, 0*1+, 0*1+0+, and every string outside 0*1*0* (|w| <= 12)",
      all(meaning45[nm(D.delta_star(D.start, w))](w) and sum(f(w) for f in meaning45.values()) == 1
          for w in strings(AB, 12)))
Dm = D.minimize()
check("4.5 {p} and {p,r} have the same ε-reach; the minimal DFA has 4 states and merges exactly these two",
      E.eps_reach({"p"}) == E.eps_reach({"p", "r"}) and len(Dm.states) == 4
      and [sorted(nm(x) for x in c) for c in Dm.states if len(c) > 1] == [["p", "pr"]])
D41, rows41 = N41.subset_construction()
check("4.5 the 4.1 NFA: subsets {s}, {s,a}, {s,b}, {s,a,c}, {s,b,c} (5 of 16); the two accepting ones merge: 4 states",
      [nm(r[0]) for r in rows41] == ["s", "sa", "sb", "sac", "sbc"] and 2 ** 4 == 16
      and [r[2] for r in rows41] == [False, False, False, True, True] and len(D41.minimize().states) == 4
      and [sorted(nm(x) for x in c) for c in D41.minimize().states if len(c) > 1] == [["sac", "sbc"]])


def subset_lemma(N, n=8):
    """ε-reach(δ'*(S, w)) = union over p ∈ S of δ*(p, w), for EVERY subset S."""
    Dn, _ = N.subset_construction()

    def dprime_star(S, w):
        for a in w:
            T = set()
            for p in S:
                for r in N.eps_reach(p):
                    T |= N.delta(r, a)
            S = frozenset(T)
        return S

    subsets = [frozenset(c) for k in range(len(N.states) + 1) for c in combinations(N.states, k)]
    return all(set(N.eps_reach(dprime_star(S, w))) == set().union(*[set(run_sets(N, w, p)[-1]) for p in S])
               for S in subsets for w in strings(AB, n))


check("4.5 proof claim for every subset S: ε-reach(δ'*(S,w)) = union of δ*(p,w) over p ∈ S (E, the 4.1 NFA; |w| <= 8)",
      subset_lemma(E) and subset_lemma(N41))
check("4.5 the subset DFA of 60 random ε-NFAs is equivalent to the NFA and has at most 2^n states",
      all(equivalent(N.to_dfa(), remove_eps(N).to_dfa())[0] and len(N.to_dfa().states) <= 2 ** len(N.states)
          for N in RANDE))

# ---- the k-th symbol from the end
for k in range(1, 9):
    d = {(0, "0"): {0}, (0, "1"): {0, 1}}
    for i in range(1, k):
        d[(i, "0")] = {i + 1}
        d[(i, "1")] = {i + 1}
    Nk = NFA(AB, range(k + 1), 0, [k], d)
    pk = lambda w, k=k: len(w) >= k and w[-k] == "1"
    Dk, _ = Nk.subset_construction()
    subsets_with_0 = {frozenset({0} | set(c)) for j in range(k + 1) for c in combinations(range(1, k + 1), j)}
    Fk = list(strings(AB, k, k))
    fool = all(pk(x + "0" * i) != pk(y + "0" * i) for x, y in combinations(Fk, 2) for i in range(k)
               if x[i] != y[i])
    check(f"4.5 k = {k}: the {k + 1}-state NFA accepts 'k-th symbol from the end is 1'; the subset construction builds "
          f"exactly the {2 ** k} subsets containing 0, none redundant; Σ^{k} with z = 0^(i-1) is a fooling set",
          len(Nk.states) == k + 1 and agrees(Nk, pk, max(12, k + 4)) and set(Dk.states) == subsets_with_0
          and len(Dk.minimize().states) == 2 ** k and fool)
    if k <= 5:
        check(f"4.5 L_{k} = (0+1)*1(0+1)^{k - 1}: the expression is equivalent to the NFA (exact)",
              R("(0+1)*1" + "(0+1)" * (k - 1)).equivalent(Nk.to_dfa())[0])


# =============================================================== 4.6 Thompson's algorithm
def thompson_v(node, star="book", merge=False, shortcut=False, classes=False):
    """Thompson's algorithm with
         star='book':  new s, t; s-ε->s_S, t_S-ε->t, s-ε->t and the loop t-ε->s   (the book's gadget)
         star='lib':   the same, but the loop is t_S-ε->s_S                         (common textbook form)
       merge:    identify t_S with s_T for ST instead of adding an ε-edge         (a broken 'optimization')
       shortcut: S* without new states: ε-edges s_S -> t_S and t_S -> s_S          (a broken 'optimization')
       classes:  draw a union of single symbols as one two-state gadget (one edge per symbol)."""
    n, delta, parent = [0], {}, {}

    def new():
        n[0] += 1
        return n[0] - 1

    def add(p, a, q):
        delta.setdefault((p, a), set()).add(q)

    def syms(x):
        if x[0] == "sym":
            return [x[1]]
        if x[0] == "union":
            l, r = syms(x[1]), syms(x[2])
            if l is not None and r is not None:
                return l + r
        return None

    def build(x):
        k = x[0]
        if classes and k == "union" and syms(x) is not None:
            s, t = new(), new()
            for a in syms(x):
                add(s, a, t)
            return s, t
        if k == "empty":
            return new(), new()
        if k in ("eps", "sym"):
            s, t = new(), new()
            add(s, EPS if k == "eps" else x[1], t)
            return s, t
        if k == "cat":
            s1, t1 = build(x[1])
            s2, t2 = build(x[2])
            if merge:
                parent[t1] = s2
            else:
                add(t1, EPS, s2)
            return s1, t2
        if k == "union":
            s = new()
            s1, t1 = build(x[1])
            s2, t2 = build(x[2])
            t = new()
            for e in ((s, s1), (s, s2), (t1, t), (t2, t)):
                add(e[0], EPS, e[1])
            return s, t
        if k == "star":
            if shortcut:
                s1, t1 = build(x[1])
                add(s1, EPS, t1)
                add(t1, EPS, s1)
                return s1, t1
            s = new()
            s1, t1 = build(x[1])
            t = new()
            add(s, EPS, s1)
            add(t1, EPS, t)
            add(s, EPS, t)
            if star == "book":
                add(t, EPS, s)
            else:
                add(t1, EPS, s1)
            return s, t
        raise ValueError(x)

    s, t = build(node)

    def f(q):
        while q in parent:
            q = parent[q]
        return q

    d2 = {}
    for (p, a), T in delta.items():
        for q in T:
            d2.setdefault((f(p), a), set()).add(f(q))
    return NFA(AB, sorted({f(q) for q in range(n[0])}), f(s), {f(t)}, d2)


def asts(size):
    """All expression trees with exactly `size` nodes over the leaves ∅, ε, 0, 1."""
    if size == 1:
        return [("empty",), ("eps",), ("sym", "0"), ("sym", "1")]
    out = [("star", x) for x in asts(size - 1)]
    for k in range(1, size - 1):
        for x in asts(k):
            for y in asts(size - 1 - k):
                out += [("cat", x, y), ("union", x, y)]
    return out


def count_nodes(x, kinds):
    return (x[0] in kinds) + sum(count_nodes(c, kinds) for c in x[1:] if isinstance(c, tuple))


ALL5 = [x for k in range(1, 6) for x in asts(k)]
ok_lang = ok_shape = ok_count = ok_lib = True
for x in ALL5:
    Rx = R(to_str(x))
    N = thompson_v(x)
    ok_lang = ok_lang and Rx.equivalent(N.to_dfa())[0]
    ok_shape = ok_shape and len(N.accepting) == 1 and N.start not in N.accepting
    ok_count = ok_count and len(N.states) == 2 * count_nodes(x, ("empty", "eps", "sym", "union", "star"))
    ok_lib = ok_lib and Rx.equivalent(thompson_v(x, star="lib").to_dfa())[0]
check(f"4.6 Lemma 4.2 with the book's gadgets: L(NFA) = L(R) for all {len(ALL5)} expressions of size <= 5 over ∅, ε, 0, 1",
      ok_lang)
check("4.6 every one of them has exactly one accepting state, different from its start state", ok_shape)
check("4.6 two states per leaf, + and *, none per concatenation (all of them)", ok_count)
check("4.6 the common variant (loop t_S -> s_S) is correct too (same expressions)", ok_lib)

# ---- (0+10*1)* with the book's state names
ast46 = _Parser("(0+10*1)*").parse()
T46 = thompson_v(ast46)
name46 = dict(zip(range(14), "sajkbcdefghilm"))
named = {(name46[p], a): {name46[q] for q in T} for (p, a), T in T46._delta.items()}
eps_edges = {(p, q) for (p, a), T in named.items() if a == EPS for q in T}
sym_edges = {(p, a, q) for (p, a), T in named.items() if a != EPS for q in T}
FIG_EPS = {("s", "a"), ("s", "m"), ("m", "s"), ("a", "j"), ("a", "b"), ("k", "l"), ("i", "l"), ("l", "m"),
           ("c", "d"), ("d", "e"), ("d", "g"), ("g", "d"), ("f", "g"), ("g", "h")}
FIG_SYM = {("j", "0", "k"), ("b", "1", "c"), ("e", "0", "f"), ("h", "1", "i")}
check("4.6 (0+10*1)*: 4 symbols, one +, two stars -> 2(4+1+2) = 14 states; 14 ε-transitions and 4 symbol "
      "transitions, exactly the edges of the figure", len(T46.states) == 14 == 2 * (4 + 1 + 2)
      and eps_edges == FIG_EPS and sym_edges == FIG_SYM and name46[T46.start] == "s"
      and {name46[q] for q in T46.accepting} == {"m"})
N46 = NFA(AB, "sabcdefghijklm", "s", ["m"], named)
D46, rows46 = N46.subset_construction()
got46 = [(nm(S), nm(Rr), acc, nm(t["0"]), nm(t["1"])) for S, Rr, acc, t in rows46]
want46 = [("s", "sabjm", True, "k", "c"), ("k", "sabjklm", True, "k", "c"), ("c", "cdegh", False, "f", "i"),
          ("f", "defgh", False, "f", "i"), ("i", "sabijlm", True, "k", "c")]
check("4.6 the incremental table for (0+10*1)* exactly as printed (the book's table)", got46 == want46, str(got46))
check("4.6 5 DFA states instead of up to 2^14 = 16384; the DFA accepts the strings with an even number of 1s",
      len(D46.states) == 5 and 2 ** 14 == 16384 and agrees(D46, lambda w: w.count("1") % 2 == 0, 14)
      and R("(0+10*1)*").equivalent(D46)[0])
check("4.6 minimization merges {s},{k},{i} (even number of 1s so far) and {c},{f} (odd): 2 states",
      sorted(sorted(nm(S) for S in c) for c in D46.minimize().states) == [["c", "f"], ["i", "k", "s"]]
      and all((nm(D46.delta_star(D46.start, w)) in ("s", "k", "i")) == (w.count("1") % 2 == 0)
              for w in strings(AB, 12)))
Tlib = thompson_v(ast46, star="lib")
Nlib = NFA(AB, "sabcdefghijklm", "s", ["m"],
           {(name46[p], a): {name46[q] for q in T} for (p, a), T in Tlib._delta.items()})
Dl, rowsl = Nlib.subset_construction()
gotl = [(nm(S), nm(Rr), acc, nm(t["0"]), nm(t["1"])) for S, Rr, acc, t in rowsl]
check("4.6 with the common loop t_S -> s_S: same rows, acceptance and transitions; only the ε-reaches of {k}, {f}, {i} "
      "lose s or d", [g[:1] + g[2:] for g in gotl] == [g[:1] + g[2:] for g in want46]
      and [g[1] for g in gotl] == ["sabjm", "abjklm", "cdegh", "efgh", "abijlm"], str(gotl))
a01 = _Parser("0*1*").parse()
Nm = thompson_v(a01, merge=True)
check("4.6 trap: identifying t_S with s_T makes the NFA for 0*1* accept 10 (not in 0*1*)",
      Nm.accepts("10") and not R("0*1*")("10") and len(Nm.states) == len(thompson_v(a01).states) - 1)
Ns = thompson_v(_Parser("(0*1)*").parse(), shortcut=True)
check("4.6 trap: the star without new states (ε-edges s_S <-> t_S) makes the NFA for (0*1)* accept 0",
      Ns.accepts("0") and not R("(0*1)*")("0"))

# =============================================================== 4.7 (0+1)*(00+11)(0+1)*
ast47 = _Parser("(0+1)*(00+11)(0+1)*").parse()
N26 = thompson_v(ast47)
N18 = thompson_v(ast47, classes=True)
res = []
for N in (N26, N18, thompson_v(ast47, star="lib"), R("(0+1)*(00+11)(0+1)*").nfa()):
    Dx, rx = N.subset_construction()
    res.append((len(N.states), len(Dx.states), sum(r[2] for r in rx), len(Dx.minimize().states), agrees(Dx, has_pair)))
check("4.7 the literal construction has 2(8+3+2) = 26 states; with each 0+1 as one two-state gadget, 18",
      res[0][0] == 26 == 2 * (8 + 3 + 2) and res[1][0] == 18, str(res))
check("4.7 every version: a 9-state DFA with 6 accepting states, minimal DFA 4 states, correct language",
      all(r[1:] == (9, 6, 4, True) for r in res), str(res))
check("4.7 same language as the 4.1 NFA (exact), which has only 4 states",
      R("(0+1)*(00+11)(0+1)*").equivalent(N41.to_dfa())[0] and len(N41.states) == 4)
name47 = dict(zip(range(26), "sabcdefghijklmnopqrtuvwxyz"))
N47 = NFA(AB, "abcdefghijklmnopqrstuvwxyz", "s", [name47[t] for t in N26.accepting],
          {(name47[p], a): {name47[q] for q in T} for (p, a), T in N26._delta.items()})
D47, rows47 = N47.subset_construction()
got47 = [(nm(S), acc, nm(t["0"]), nm(t["1"])) for S, Rr, acc, t in rows47]
want47 = [("s", False, "cj", "en"), ("cj", False, "cjl", "en"), ("en", False, "cj", "enp"),
          ("cjl", True, "cjlv", "enx"), ("enp", True, "cjv", "enpx"), ("cjlv", True, "cjlv", "enx"),
          ("enx", True, "cjv", "enpx"), ("cjv", True, "cjlv", "enx"), ("enpx", True, "cjv", "enpx")]
check("4.7 the DFA's states, acceptance and transitions with the book's names, in the book's order", got47 == want47,
      str(got47))
check("4.7 letters: c, e entered by 0, 1 in the first (0+1)*; j, l by the 0s of 00; n, p by the 1s of 11; "
      "v, x by 0, 1 in the last (0+1)*",
      {(p, a, q) for (p, a), T in N47._delta.items() if a != EPS for q in T} ==
      {("b", "0", "c"), ("d", "1", "e"), ("i", "0", "j"), ("k", "0", "l"), ("m", "1", "n"), ("o", "1", "p"),
       ("u", "0", "v"), ("w", "1", "x")})
pre = lambda w: has_pair(w[:-1])
meaning47 = {"s": lambda w: w == "",
             "cj": lambda w: w.endswith("0") and not has_pair(w),
             "en": lambda w: w.endswith("1") and not has_pair(w),
             "cjl": lambda w: w.endswith("00") and not pre(w),
             "enp": lambda w: w.endswith("11") and not pre(w),
             "cjlv": lambda w: w.endswith("00") and pre(w),
             "cjv": lambda w: w.endswith("10") and pre(w),
             "enx": lambda w: w.endswith("01") and pre(w),
             "enpx": lambda w: w.endswith("11") and pre(w)}
check("4.7 the 'strings that reach S' column holds exactly (|w| <= 11)",
      all(meaning47[nm(D47.delta_star(D47.start, w))](w) and sum(f(w) for f in meaning47.values()) == 1
          for w in strings(AB, 11)))
check("4.7 minimization merges exactly the six accepting states",
      sorted(len(c) for c in D47.minimize().states) == [1, 1, 1, 6]
      and all(len(c) == 1 or all(x in D47.accepting for x in c) for c in D47.minimize().states))


# =============================================================== 4.8 state elimination
def elim(Rd, nodes, order):
    """R'(p->r) = R(p->r) + R(p->q) R(q->q)* R(q->r) for every remaining p, r; returns the changed labels per step."""
    steps, remaining = [], list(nodes)
    for q in order:
        raw = Rd.get((q, q), ("empty",))
        loop = _s(raw)
        preds = [p for p in remaining if p != q and Rd.get((p, q), ("empty",)) != ("empty",)]
        succs = [r for r in remaining if r != q and Rd.get((q, r), ("empty",)) != ("empty",)]
        new = {}
        for p in preds:
            for r in succs:
                Rd[(p, r)] = _u(Rd.get((p, r), ("empty",)), _c(_c(Rd[(p, q)], loop), Rd[(q, r)]))
                new[(p, r)] = to_str(Rd[(p, r)])
        remaining.remove(q)
        for key in [key for key in Rd if q in key]:
            del Rd[key]
        steps.append((to_str(raw), new))
    return steps


def labels(M, start_edge=None):
    Rd = {}
    for q in M.states:
        for a in AB:
            Rd[(q, M.delta(q, a))] = _u(Rd.get((q, M.delta(q, a)), ("empty",)), ("sym", a))
    for q in M.accepting:
        Rd[(q, "t")] = ("eps",)
    if start_edge:
        Rd[(start_edge, M.start)] = ("eps",)
    return Rd


M3s = DFA(AB, ["s", 0, 1, 2], "s", [0], lambda q, a: (int(a) if q == "s" else (2 * q + int(a)) % 3))
check("4.8 the book's DFA (start s, states 0, 1, 2, accepting 0) accepts exactly the non-empty binary multiples of 3 "
      "(|w| <= 14)", first_difference(M3s.accepts, lambda w: w != "" and val(w) % 3 == 0, AB, 14) is None)
check("4.8 its transition table: s -> 0, 1; 0 -> 0, 1; 1 -> 2, 0; 2 -> 1, 2; s has no incoming edges",
      [(M3s.delta(q, "0"), M3s.delta(q, "1")) for q in ["s", 0, 1, 2]] == [(0, 1), (0, 1), (2, 0), (1, 2)]
      and all(M3s.delta(q, a) != "s" for q in M3s.states for a in AB))
st = elim(labels(M3s), ["s", 0, 1, 2, "t"], [2, 0, 1])
check("4.8 step 1, eliminate 2 (loop 1): R(1->1) = 01*0", st[0] == ("1", {(1, 1): "01*0"}), str(st[0]))
check("4.8 step 2, eliminate 0 (loop 0): R(s->1) = 1+00*1, R(s->t) = 00*, R(1->1) = 01*0+10*1, R(1->t) = 10*",
      st[1] == ("0", {("s", 1): "1+00*1", ("s", "t"): "00*", (1, 1): "01*0+10*1", (1, "t"): "10*"}), str(st[1]))
final = "00*+(1+00*1)(01*0+10*1)*10*"
check("4.8 step 3, eliminate 1 (loop 01*0+10*1): R(s->t) = 00*+(1+00*1)(01*0+10*1)*10*",
      st[2] == ("01*0+10*1", {("s", "t"): final}), str(st[2]))
check("4.8 the library's eliminate_states (same order) gives the same expression",
      to_str(eliminate_states(M3s, order=[2, 0, 1, "s"])) == final)
check("4.8 the result is equivalent to the DFA (exact)", R(final).equivalent(M3s)[0])
check("4.8 it is the book's 00*+(00*1+1)(10*1+01*0)*10* with the terms of two unions swapped (exact)",
      same(final, "00*+(00*1+1)(10*1+01*0)*10*")
      and sorted(["1", "00*1"]) == sorted(["00*1", "1"]) and sorted(["01*0", "10*1"]) == sorted(["10*1", "01*0"]))
check("4.8 00* = 0*0 and 1+00*1 = 0*1, so the result equals §2.3's 0*0+0*1(10*1+01*0)*10* (exact)",
      same("00*", "0*0") and same("1+00*1", "0*1") and same(final, "0*0+0*1(10*1+01*0)*10*"))
check("4.8 neither expression matches ε", not R(final)("") and not R("0*0+0*1(10*1+01*0)*10*")(""))
M3 = DFA(AB, [0, 1, 2], 0, [0], lambda q, a: (2 * q + int(a)) % 3)
check("4.8 trap: the 3-state DFA (start = accepting state 0) accepts ε and every multiple of 3 (|w| <= 14)",
      M3.accepts("") and first_difference(M3.accepts, lambda w: val(w) % 3 == 0, AB, 14) is None)
e201 = elim(labels(M3, "S"), ["S", 0, 1, 2, "t"], [2, 0, 1])[-1][1][("S", "t")]
e210 = elim(labels(M3, "S"), ["S", 0, 1, 2, "t"], [2, 1, 0])[-1][1][("S", "t")]
check("4.8 trap: with a new start, order 2,0,1 gives 0*+0*1(01*0+10*1)*10* and order 2,1,0 gives (0+1(01*0)*1)*",
      e201 == "0*+0*1(01*0+10*1)*10*" and e210 == "(0+1(01*0)*1)*", f"{e201} | {e210}")
check("4.8 trap: both are equivalent to the 3-state DFA and to ε + 0*0+0*1(10*1+01*0)*10* (exact)",
      R(e201).equivalent(M3)[0] and R(e210).equivalent(M3)[0] and same(e201, "ε+0*0+0*1(10*1+01*0)*10*"))
nsym = {}
for order in permutations([0, 1, 2]):
    x = elim(labels(M3s), ["s", 0, 1, 2, "t"], list(order))[-1][1][("s", "t")]
    check(f"4.8 order {order}: the result is equivalent to the DFA (exact)", R(x).equivalent(M3s)[0])
    nsym[order] = x.count("0") + x.count("1")
check("4.8 the six orders give expressions with 12 to 31 symbol occurrences; the order 2,0,1 gives 14",
      min(nsym.values()) == 12 and max(nsym.values()) == 31 and nsym[(2, 0, 1)] == 14, str(nsym))
# ---- growth: complete automata with distinct labels
lens = []
SYMS = [chr(c) for c in range(0x41, 0x41 + 26)] + [chr(c) for c in range(0x61, 0x61 + 26)]
for n in range(2, 7):
    it = iter(SYMS)
    d = {(p, next(it)): {q} for p in range(n) for q in range(n)}
    Nc = NFA(sorted({a for (_, a) in d}), range(n), 0, [n - 1], d)
    lens.append(len(to_str(eliminate_states(Nc))))
ratios = [lens[i + 1] / lens[i] for i in range(len(lens) - 1)]
check("4.8 growth: on complete automata with distinct labels the length grows by a factor approaching 4 per state",
      all(3.9 < r < 4.5 for r in ratios[1:]) and abs(ratios[-1] - 4) < abs(ratios[1] - 4),
      f"lengths {lens}, ratios {[round(r, 2) for r in ratios]}")

# =============================================================== 4.9 transformations
rng = random.Random(374)


def random_dfa():
    n = rng.choice([2, 3, 4])
    return DFA(AB, range(n), 0, [q for q in range(n) if rng.random() < 0.5],
               {(q, a): rng.randrange(n) for q in range(n) for a in AB})


RAND = [random_dfa() for _ in range(300)]
EDGE = {"∅": DFA(AB, [0], 0, [], lambda q, a: 0),
        "{ε}": DFA(AB, [0, 1], 0, [0], lambda q, a: 1),
        "1*": DFA(AB, [0, 1], 0, [0], lambda q, a: q if a == "1" else 1),
        "Σ*": DFA(AB, [0], 0, [0], lambda q, a: 0)}
TESTS = RAND + list(EDGE.values())
check("4.9 test set: 300 random DFAs with 2-4 states plus DFAs for ∅, {ε}, 1*, Σ*",
      len(RAND) == 300 and all(2 <= len(M.states) <= 4 for M in RAND)
      and R("∅").equivalent(EDGE["∅"])[0] and R("ε").equivalent(EDGE["{ε}"])[0]
      and R("1*").equivalent(EDGE["1*"])[0] and R("(0+1)*").equivalent(EDGE["Σ*"])[0])


# ---- Lemma 4.4, proof 1: reversing an expression
def rev(x):
    k = x[0]
    if k in ("empty", "eps", "sym"):
        return x
    if k == "union":
        return ("union", rev(x[1]), rev(x[2]))
    if k == "cat":
        return ("cat", rev(x[2]), rev(x[1]))
    return ("star", rev(x[1]))


ok_rev = all(first_difference(R(to_str(rev(x))), lambda w, Rx=R(to_str(x)): Rx(w[::-1]), AB, 8) is None for x in ALL5)
check(f"4.9 Lemma 4.4 proof 1: L(rev(R)) = L(R)^R for all {len(ALL5)} expressions of size <= 5 (|w| <= 8)", ok_rev)
check("4.9 §2.7's example: rev(0+1(0+1)*00) = 0+00(0+1)*1",
      to_str(rev(_Parser("0+1(0+1)*00").parse())) == "0+00(0+1)*1"
      and first_difference(R("0+00(0+1)*1"), lambda w: R("0+1(0+1)*00")(w[::-1]), AB, 12) is None)


# ---- Lemma 4.4, proof 2: the reversed NFA
def reverse_nfa(M):
    """Q^R = Q ∪ {s^R}, start s^R, A^R = {s}, δ^R(s^R, ε) = A, δ^R(q, a) = {p : δ(p, a) = q}."""
    sR = "sR"
    d = {(sR, EPS): set(M.accepting)}
    for p in M.states:
        for a in AB:
            d.setdefault((M.delta(p, a), a), set()).add(p)
    return NFA(AB, [sR] + list(M.states), sR, {M.start}, d)


check(f"4.9 Lemma 4.4 proof 2: M^R accepts w iff M accepts w^R ({len(TESTS)} DFAs, |w| <= 10)",
      all(all(reverse_nfa(M).accepts(w) == M.accepts(w[::-1]) for w in strings(AB, 10)) for M in TESTS))
check("4.9 M^R has |Q|+1 states, ε-transitions only out of s^R, and no symbol transitions out of s^R",
      all(len(reverse_nfa(M).states) == len(M.states) + 1
          and all(p == "sR" for (p, a), T in reverse_nfa(M)._delta.items() if a == EPS and T)
          and not any(p == "sR" for (p, a), T in reverse_nfa(M)._delta.items() if a != EPS and T) for M in TESTS))
check("4.9 'why': M^R has a walk from q to p labeled x^R iff δ*(p, x) = q (60 DFAs, |x| <= 6)",
      all((p in dstar_plain(reverse_nfa(M), q, x[::-1])) == (M.delta_star(p, x) == q)
          for M in RAND[:60] for p in M.states for q in M.states for x in strings(AB, 6)))
check("4.9 reversing the edges of a DFA is not a DFA in general (some state has 0 or 2+ incoming a-edges)",
      any(len(reverse_nfa(M).delta(q, a)) != 1 for M in RAND[:5] for q in M.states for a in AB))


# ---- Lemma 4.5: half(L)
def half_nfa(M):
    """Q' = {s'} ∪ Q^3; δ'(s', ε) = {(s,h,h)}; δ'((p,h,q), a) = {(δ(p,a), h, δ(q,a))}; A' = {(h,h,q) : q ∈ A}."""
    s1 = "s'"
    Q3 = [(p, h, q) for p in M.states for h in M.states for q in M.states]
    d = {(s1, EPS): {(M.start, h, h) for h in M.states}}
    for (p, h, q) in Q3:
        for a in AB:
            d[((p, h, q), a)] = {(M.delta(p, a), h, M.delta(q, a))}
    return NFA(AB, [s1] + Q3, s1, {(h, h, q) for h in M.states for q in M.accepting}, d)


check(f"4.9 Lemma 4.5: M' accepts w iff M accepts ww ({len(TESTS)} DFAs, |w| <= 7)",
      all(all(half_nfa(M).accepts(w) == M.accepts(w + w) for w in strings(AB, 7)) for M in TESTS))
check("4.9 half: |Q|^3 + 1 states; the middle component never changes; only the first move is nondeterministic",
      all(len(half_nfa(M).states) == len(M.states) ** 3 + 1 for M in TESTS)
      and all(q[1] == p[1] and len(T) == 1 for M in RAND[:40] for (p, a), T in half_nfa(M)._delta.items()
              if a != EPS for q in T))
check("4.9 half 'why': after w, M' can be in (p,h,q) iff p = δ*(s,w) and q = δ*(h,w) (60 DFAs, |w| <= 5)",
      all(set(half_nfa(M).current_states(w)) - {"s'"} ==
          {(M.delta_star(M.start, w), h, M.delta_star(h, w)) for h in M.states}
          for M in RAND[:60] for w in strings(AB, 5) if w))


# ---- {w : double(w) ∈ L}
def double(w):
    return "".join(a + a for a in w)


def double_dfa(M):
    """Same Q, s, A; δ'(q, a) = δ(δ(q, a), a)."""
    return DFA(AB, M.states, M.start, M.accepting, lambda q, a: M.delta(M.delta(q, a), a))


check("4.9 double(011) = 001111", double("011") == "001111")
check(f"4.9 double: the DFA accepts w iff M accepts double(w) ({len(TESTS)} DFAs, |w| <= 9)",
      all(all(double_dfa(M).accepts(w) == M.accepts(double(w)) for w in strings(AB, 9)) for M in TESTS))
D3 = double_dfa(M3)
check("4.9 double, mod-3 example: δ'(q, a) = (4q+3a) mod 3 = q for every q, a; M' accepts every string",
      all(D3.delta(q, a) == q == (4 * q + 3 * int(a)) % 3 for q in range(3) for a in AB)
      and all(D3.accepts(w) for w in strings(AB, 10)))
check("4.9 double(w) read in binary is 3 times w read in base 4 (|w| <= 12)",
      all(val(double(w)) == 3 * (int(w, 4) if w else 0) for w in strings(AB, 12)))


# ---- ones(L) = {1^|w| : w ∈ L}
def ones_nfa(M):
    """Same Q, s, A; δ'(q, 1) = {δ(q, 0), δ(q, 1)}, δ'(q, 0) = ∅, no ε-transitions."""
    return NFA(AB, M.states, M.start, M.accepting, {(q, "1"): {M.delta(q, "0"), M.delta(q, "1")} for q in M.states})


def in_ones_image(M, y):
    return set(y) <= {"1"} and any(M.accepts(w) for w in strings(AB, len(y), len(y)))


check(f"4.9 ones: the NFA accepts y iff y = 1^|w| for some w ∈ L ({len(TESTS)} DFAs, |y| <= 8)",
      all(all(ones_nfa(M).accepts(y) == in_ones_image(M, y) for y in strings(AB, 8)) for M in TESTS))
check("4.9 ones 'why': after 1^i, M' can be in q iff some string of length i leads M from s to q (60 DFAs, i <= 6)",
      all(set(ones_nfa(M).current_states("1" * i)) == {M.delta_star(M.start, w) for w in strings(AB, i, i)}
          for M in RAND[:60] for i in range(7)))
check("4.9 ones maps ∅, {ε}, 1*, Σ* to ∅, {ε}, 1*, 1*; and (01)* to (11)* (exact)",
      R("∅").equivalent(ones_nfa(EDGE["∅"]).to_dfa())[0] and R("ε").equivalent(ones_nfa(EDGE["{ε}"]).to_dfa())[0]
      and R("1*").equivalent(ones_nfa(EDGE["1*"]).to_dfa())[0] and R("1*").equivalent(ones_nfa(EDGE["Σ*"]).to_dfa())[0]
      and R("(11)*").equivalent(ones_nfa(R("(01)*").dfa()).to_dfa())[0])
check("4.9 edge cases: reversal, half and the double-preimage map ∅, {ε}, 1*, Σ* to themselves (exact)",
      all(equivalent(reverse_nfa(M).to_dfa(), M)[0] and equivalent(half_nfa(M).to_dfa(), M)[0]
          and equivalent(double_dfa(M), M)[0] for M in EDGE.values()))

# ---- traps
check("4.9 trap: for L = Σ*, {w : double(w) ∈ L} = Σ* but {double(w) : w ∈ L} = (00+11)* (|y| <= 12)",
      equivalent(double_dfa(EDGE["Σ*"]), EDGE["Σ*"])[0]
      and all((y in {double(w) for w in strings(AB, len(y) // 2, len(y) // 2)}) == R("(00+11)*")(y)
              for y in strings(AB, 12)))
ww01 = lambda y: any(y == x + x for x in ["0" * n + "1" for n in range(len(y) // 2 + 1)])
check("4.9 trap: {ww : w ∈ 0*1} = {0^n 1 0^n 1 : n >= 0} (|y| <= 14)",
      all(ww01(y) == any(y == "0" * n + "1" + "0" * n + "1" for n in range(len(y))) for y in strings(AB, 14)))
check("4.9 trap: 0* is a fooling set for it: the suffix 1 0^i 1 puts 0^i·10^i1 in and 0^j·10^i1 out (i != j <= 12)",
      all(ww01("0" * i + "1" + "0" * i + "1") and not ww01("0" * j + "1" + "0" * i + "1")
          for i in range(13) for j in range(13) if i != j))
check("4.9 trap: half(0*1) is regular although {ww : w ∈ 0*1} is not — half(0*1) = ∅ (exact)",
      R("∅").equivalent(half_nfa(R("0*1").dfa()).to_dfa())[0])

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: {FAIL}")
sys.exit(1 if FAIL else 0)
