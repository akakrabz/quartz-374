#!/usr/bin/env python3
"""Checks for content/4-lecture-notes/c-dynamic-programming-for-automata.md (Erickson, Extended Dance Remix C)
and the concept page content/concepts/cyk-algorithm.md.

Every recurrence and pseudocode block is implemented as printed in the note (with tables that refuse reads of
unwritten entries and out-of-range indices), then as corrected on the page, and compared with independent brute
force: walk enumeration and the automata library's set simulation for NFAs, strings up to length n for DFA state
equivalence, and the library's Earley recognizer (plus direct predicates) for grammars."""
import itertools
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
from automata import DFA, NFA, CFG, strings  # noqa: E402

FAIL = []
random.seed(374)


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAIL.append(name)


class Unwritten(Exception):
    pass


class Table:
    """Dict-backed array: reading an unwritten entry or an index outside the declared ranges raises."""

    def __init__(self, *ranges, default=None):
        self.ranges = ranges
        self.d = {}
        self.default = default

    def _ok(self, key):
        key = key if isinstance(key, tuple) else (key,)
        for k, r in zip(key, self.ranges):
            if r is not None and k not in r:
                raise IndexError(f"index {key} outside {self.ranges}")
        return key

    def __getitem__(self, key):
        key = self._ok(key)
        if key not in self.d:
            if self.default is not None:
                return self.default
            raise Unwritten(f"read of unwritten entry {key}")
        return self.d[key]

    def __setitem__(self, key, v):
        self.d[self._ok(key)] = v


# =====================================================================================================
# C.2 NFA acceptance
# =====================================================================================================
def random_nfa(nq, sigma="01", p=0.35, pacc=0.4):
    Q = list(range(1, nq + 1))
    delta = {(q, a): {r for r in Q if random.random() < p} for q in Q for a in sigma}
    A = {q for q in Q if random.random() < pacc}
    return Q, A, delta


def accepts_walks(Q, A, delta, s, w):
    """Brute force: list every walk from s labeled w (depth-first) and test whether one ends in A."""
    walks = [[s]]
    for a in w:
        walks = [wk + [r] for wk in walks for r in sorted(delta[(wk[-1], a)])]
    return any(wk[-1] in A for wk in walks)


def delta_star(delta, q, w):
    """The note's recursive extension delta*: Q x Sigma* -> 2^Q (p. 2)."""
    if w == "":
        return {q}
    a, x = w[0], w[1:]
    out = set()
    for r in delta[(q, a)]:
        out |= delta_star(delta, r, x)
    return out


def accepts_q_w(A, delta, q, w):
    """The note's Accepts?(q, w) (p. 2)."""
    if w == "":
        return q in A
    a, x = w[0], w[1:]
    return any(accepts_q_w(A, delta, r, x) for r in delta[(q, a)])


def make_delta_array(Q, sigma, delta, literal=False):
    """delta[p, a, q] as a boolean array. Corrected reading: True iff q in delta(p, a).
    Literal reading of the note's p. 3 bullet: True iff p in delta(q, a)."""
    arr = {}
    for p in Q:
        for a in sigma:
            for q in Q:
                arr[(p, a, q)] = (p in delta[(q, a)]) if literal else (q in delta[(p, a)])
    return arr


CALLS = [0]


def backtrack_accepts(Aarr, darr, Q, w, q, i):
    """The note's backtracking Accepts?(q, i) (p. 3), 1-indexed w."""
    CALLS[0] += 1
    n = len(w)
    if i > n:
        return Aarr[q]
    for r in Q:
        if darr[(q, w[i - 1], r)] and backtrack_accepts(Aarr, darr, Q, w, r, i + 1):
            return True
    return False


def nfa_accepts_dp(Aarr, darr, Q, w):
    """The note's NFAaccepts? (p. 4), loop for loop; start state is state 1."""
    n = len(w)
    Acc = Table(range(1, len(Q) + 1), range(1, n + 2))
    DPWORK[0] = 0
    for q in Q:
        Acc[q, n + 1] = Aarr[q]
    for i in range(n, 0, -1):
        for q in Q:
            Acc[q, i] = False
            for r in Q:
                DPWORK[0] += 1
                if darr[(q, w[i - 1], r)] and Acc[r, i + 1]:
                    Acc[q, i] = True
    return Acc[1, 1], Acc


DPWORK = [0]


ok_rec = ok_dstar = ok_bt = ok_dp = ok_lib = ok_work = True
lit_wrong = 0
trials = 0
for trial in range(300):
    nq = random.randint(1, 4)
    Q, A, delta = random_nfa(nq)
    Aarr = {q: (q in A) for q in Q}
    darr = make_delta_array(Q, "01", delta)
    lit = make_delta_array(Q, "01", delta, literal=True)
    lib = NFA("01", Q, 1, A, {k: v for k, v in delta.items()})
    for w in strings("01", 6):
        truth = accepts_walks(Q, A, delta, 1, w)
        trials += 1
        ok_dstar &= (bool(delta_star(delta, 1, w) & A) == truth)
        ok_rec &= (accepts_q_w(A, delta, 1, w) == truth)
        ok_bt &= (backtrack_accepts(Aarr, darr, Q, w, 1, 1) == truth)
        res, _ = nfa_accepts_dp(Aarr, darr, Q, w)
        ok_dp &= (res == truth)
        ok_work &= (DPWORK[0] == len(w) * nq * nq)
        ok_lib &= (lib.accepts(w) == truth)
        r2, _ = nfa_accepts_dp(Aarr, lit, Q, w)
        lit_wrong += (r2 != truth)
check("C.2: delta* recurrence (p. 2) matches walk enumeration (300 random NFAs, |Q|<=4, all w up to length 6)", ok_dstar,
      f"{trials} cases")
check("C.2: Accepts?(q, w) recurrence matches walk enumeration", ok_rec)
check("C.2: backtracking Accepts?(q, i) (with delta[q,a,r] meaning r in delta(q,a)) is correct", ok_bt)
check("C.2: NFAaccepts? dynamic program, as printed, is correct; every read is of a written entry", ok_dp)
check("C.2: library set simulation agrees (independent brute force)", ok_lib)
check("C.2 note error p. 3: literal reading 'delta[p,a,q] iff p in delta(q,a)' makes NFAaccepts? wrong on some inputs",
      lit_wrong > 0, f"{lit_wrong} wrong answers")

# backtracking worst case: complete NFA, no accepting state: calls = 1 + |Q| + ... + |Q|^n
for nq, n in [(2, 8), (3, 6), (4, 5)]:
    Q = list(range(1, nq + 1))
    delta = {(q, a): set(Q) for q in Q for a in "01"}
    Aarr = {q: False for q in Q}
    darr = make_delta_array(Q, "01", delta)
    CALLS[0] = 0
    backtrack_accepts(Aarr, darr, Q, "0" * n, 1, 1)
    check(f"C.2: backtracking makes sum_k |Q|^k calls on a complete rejecting NFA (|Q|={nq}, n={n}): Theta(|Q|^n)",
          CALLS[0] == sum(nq ** k for k in range(n + 1)), str(CALLS[0]))

check("C.2: NFAaccepts? runs its innermost test exactly n|Q|^2 times (O(n|Q|^2))", ok_work)

# The example on the page: the NFA of Ch 4 §4.1 for 'contains 00 or 11', states s,a,b,c
QX = ["s", "a", "b", "c"]
DX = {("s", "0"): {"s", "a"}, ("s", "1"): {"s", "b"}, ("a", "0"): {"c"}, ("a", "1"): set(),
      ("b", "0"): set(), ("b", "1"): {"c"}, ("c", "0"): {"c"}, ("c", "1"): {"c"}}
AX = {"c"}
idx = {q: k + 1 for k, q in enumerate(QX)}
Qn = [1, 2, 3, 4]
Dn = {(idx[q], a): {idx[r] for r in T} for (q, a), T in DX.items()}
An = {idx["c"]}
w = "0110"
res, Acc = nfa_accepts_dp({q: q in An for q in Qn}, make_delta_array(Qn, "01", Dn), Qn, w)
table = {q: "".join("T" if Acc[idx[q], i] else "F" for i in range(1, 6)) for q in QX}
check("C.2 example: Accepts? table for 0110, columns i = 1..5",
      table == {"s": "TTFFF", "a": "TFFTF", "b": "FTTFF", "c": "TTTTT"}, str(table))
check("C.2 example: 0110 accepted (Accepts?[s,1] = T)", res)
res2, Acc2 = nfa_accepts_dp({q: q in An for q in Qn}, make_delta_array(Qn, "01", Dn), Qn, "0101")
table2 = {q: "".join("T" if Acc2[idx[q], i] else "F" for i in range(1, 6)) for q in QX}
check("C.2 example: 0101 rejected; table", not res2 and table2 == {"s": "FFFFF", "a": "TFTFF", "b": "FTFTF", "c": "TTTTT"},
      str(table2))
# forward simulation (the site's §4.1 'running an NFA by hand') reaches the same verdicts
lib = NFA("01", QX, "s", AX, DX)
check("C.2 example: forward set simulation agrees on 0110 and 0101", lib.accepts("0110") and not lib.accepts("0101"))
# Accepts?[q, i] = True iff delta*(q, w[i..n]) meets A — the table is acceptance of every suffix from every state
okt = all((Acc[idx[q], i]) == bool(delta_star(DX, q, w[i - 1:]) & AX) for q in QX for i in range(1, 6))
check("C.2 example: every table entry equals [delta*(q, w[i..n]) meets A]", okt)

# =====================================================================================================
# C.1 (extra on the page): Moore's algorithm as a layered dynamic program
# =====================================================================================================
def moore_layers(dfa):
    """Dist(k, p, q) layer by layer; returns list of layers (sets of frozenset pairs)."""
    Q = dfa.states
    L0 = {frozenset((p, q)) for p in Q for q in Q if p != q and ((p in dfa.accepting) != (q in dfa.accepting))}
    layers = [L0]
    while True:
        prev = layers[-1]
        cur = set(prev)
        for i, p in enumerate(Q):
            for q in Q[i + 1:]:
                if frozenset((p, q)) in prev:
                    continue
                for a in dfa.alphabet:
                    r, s = dfa.delta(p, a), dfa.delta(q, a)
                    if r != s and frozenset((r, s)) in prev:
                        cur.add(frozenset((p, q)))
                        break
        if cur == prev:
            return layers
        layers.append(cur)


def acc_vector(dfa, q, k):
    return [dfa.delta_star(q, z) in dfa.accepting for z in strings(dfa.alphabet, k)]


def dist_brute(vec, p, q, k, sigma):
    """Some string of length <= k distinguishes p and q (vectors list strings shortest first)."""
    m = sum(sigma ** t for t in range(k + 1))
    return vec[p][:m] != vec[q][:m]


ok_layers = ok_final = ok_rounds = ok_count = ok_inplace = True
max_rounds_ratio = 0
for trial in range(400):
    n = random.randint(2, 7)
    sig = "01" if trial % 2 else "012"
    Q = list(range(n))
    dl = {(q, a): random.randrange(n) for q in Q for a in sig}
    A = [q for q in Q if random.random() < 0.5]
    M = DFA(sig, Q, 0, A, dl)
    layers = moore_layers(M)
    vec = {q: acc_vector(M, q, n) for q in Q}
    for k in range(min(n, 5)):
        Lk = layers[min(k, len(layers) - 1)]
        for i, p in enumerate(Q):
            for q in Q[i + 1:]:
                if (frozenset((p, q)) in Lk) != dist_brute(vec, p, q, k, len(sig)):
                    ok_layers = False
    last = layers[-1]
    for i, p in enumerate(Q):
        for q in Q[i + 1:]:
            if (frozenset((p, q)) in last) != dist_brute(vec, p, q, n, len(sig)):
                ok_final = False
    # number of layers computed beyond layer 0 before stabilizing
    rounds = len(layers) - 1
    if rounds > max(n - 2, 0):
        ok_rounds = False
    # merging the unmarked classes of the reachable part gives the library's minimal DFA
    R = M.reachable()
    classes = set()
    for p in R:
        classes.add(frozenset(q for q in R if q == p or frozenset((p, q)) not in last))
    if len(classes) != len(M.minimize().states):
        ok_count = False
    # in-place table filling (the library's Moore passes, on the reachable part) never needs more rounds
    Rl = sorted(R)
    Mr = DFA(sig, Rl, 0, [q for q in A if q in R], {(q, a): dl[(q, a)] for q in Rl for a in sig})
    Mr.distinguishable_pairs()
    if Mr._moore_passes - 1 > len(moore_layers(Mr)) - 1:
        ok_inplace = False
check("C.1 extra: Dist(k,p,q) layers equal 'some string of length <= k distinguishes p,q' (k <= 4, 400 random DFAs)",
      ok_layers)
check("C.1 extra: the stable layer marks exactly the distinguishable pairs (strings up to length n)", ok_final)
check("C.1 extra: the layers stop changing after at most n - 2 rounds (so at most n layers are ever computed)", ok_rounds)
# tightness: the chain 0 -> 1 -> ... -> n-1 (accepting, self-loop) changes in n - 2 rounds, so the stop is at layer n - 1
ok_tight = True
for n in range(3, 9):
    Mc = DFA("0", list(range(n)), 0, [n - 1], {(q, "0"): min(q + 1, n - 1) for q in range(n)})
    ok_tight &= (len(moore_layers(Mc)) - 1 == n - 2)
check("C.1 extra: the n - 2 bound is attained (chain DFAs, n = 3..8): the first repeated layer can be layer n - 1",
      ok_tight)
check("C.1 extra: merging unmarked reachable states gives the minimal DFA's state count", ok_count)
check("C.1 extra: in-place table filling (Ch 3 §3.10) needs at most as many marking passes as the layered DP has rounds",
      ok_inplace)

# =====================================================================================================
# C.4 CFG parsing
# =====================================================================================================
def gen_rec(G, A, x, memo=None):
    """The note's Gen?(A, x) (p. 5) for a CNF grammar given as dict A -> list of tuples (memoized)."""
    memo = {} if memo is None else memo
    if (A, x) in memo:
        return memo[(A, x)]
    if len(x) <= 1:
        v = tuple(x) in [tuple(r) for r in G[A] if len(r) == len(x) and all(s not in G for s in r)]
    else:
        v = any(gen_rec(G, r[0], x[:k], memo) and gen_rec(G, r[1], x[k:], memo)
                for r in G[A] if len(r) == 2 for k in range(1, len(x)))
    memo[(A, x)] = v
    return v


def gen_idx(G, w, memo, A, i, j):
    """The note's Gen?(A, i, j) (p. 6), memoized; 1-indexed substring w[i..j]."""
    key = (A, i, j)
    if key in memo:
        return memo[key]
    if i == j:
        v = (w[i - 1],) in [tuple(r) for r in G[A]]
    else:
        v = any(gen_idx(G, w, memo, r[0], i, k) and gen_idx(G, w, memo, r[1], k + 1, j)
                for r in G[A] if len(r) == 2 for k in range(i, j))
    memo[key] = v
    return v


def cyk_printed(G, S, w, default=None):
    """CYKParse exactly as printed (p. 6), including 'for i <- n down to j + 1'."""
    n = len(w)
    if n == 0:
        return () in G[S]
    NT = list(G)
    Gen = Table(None, range(1, n + 1), range(1, n + 1), default=default)
    for i in range(1, n + 1):
        for A in NT:
            Gen[A, i, i] = (w[i - 1],) in G[A]
    for j in range(1, n + 1):
        for i in range(n, j, -1):
            for A in NT:
                Gen[A, i, j] = False
            for A in NT:
                for r in G[A]:
                    if len(r) == 2:
                        B, C = r
                        for k in range(i, j):
                            if Gen[B, i, k] and Gen[C, k + 1, j]:
                                Gen[A, i, j] = True
    return Gen[S, 1, n]


WORK = [0]


def cyk(G, S, w):
    """CYKParse corrected: for j <- 1 to n, for i <- j - 1 down to 1."""
    n = len(w)
    if n == 0:
        return () in G[S], None
    NT = list(G)
    Gen = Table(None, range(1, n + 1), range(1, n + 1))
    for i in range(1, n + 1):
        for A in NT:
            Gen[A, i, i] = (w[i - 1],) in G[A]
    for j in range(1, n + 1):
        for i in range(j - 1, 0, -1):
            for A in NT:
                Gen[A, i, j] = False
            for A in NT:
                for r in G[A]:
                    if len(r) == 2:
                        B, C = r
                        for k in range(i, j):
                            WORK[0] += 1
                            if Gen[B, i, k] and Gen[C, k + 1, j]:
                                Gen[A, i, j] = True
    return Gen[S, 1, n], Gen


def random_cnf(nts=("S", "A", "B", "C"), sig="01"):
    G = {X: [] for X in nts}
    body = [X for X in nts if X != "S"]
    for X in nts:
        for B in body:
            for C in body:
                if random.random() < 0.18:
                    G[X].append((B, C))
        for a in sig:
            if random.random() < 0.4:
                G[X].append((a,))
    if random.random() < 0.5:
        G["S"].append(())
    return G


ok_cyk = ok_rec = ok_idx = ok_work = True
printed_fail = 0
printed_default_wrong = 0
note_A_wrong = 0
n_cases = n_long = 0
for trial in range(250):
    G = random_cnf()
    lib = CFG("S", G)
    assert lib.is_cnf()[0]
    for w in strings("01", 7):
        truth = lib.generates(w)
        n_cases += 1
        WORK[0] = 0
        got, Gen = cyk(G, "S", w)
        ok_cyk &= (got == truth)
        n = len(w)
        nbin = sum(1 for X in G for r in G[X] if len(r) == 2)
        if n >= 1 and WORK[0] != nbin * (n ** 3 - n) // 6:
            ok_work = False
        if n >= 1:
            ok_rec &= (gen_rec(G, "S", w) == truth)
            ok_idx &= (gen_idx(G, w, {}, "S", 1, n) == truth)
            # the note's final sentence says Gen?(A, 1, n) — 'some' nonterminal A
            if any(gen_idx(G, w, {}, A, 1, n) for A in G) != truth:
                note_A_wrong += 1
        else:
            ok_rec &= ((() in G["S"]) == truth)
        if n >= 2:
            n_long += 1
            try:
                cyk_printed(G, "S", w)
            except Unwritten:
                printed_fail += 1
            if truth and not cyk_printed(G, "S", w, default=False):
                printed_default_wrong += 1
check("C.4: corrected CYKParse agrees with the Earley recognizer (250 random CNF grammars, all w up to length 7)",
      ok_cyk, f"{n_cases} cases")
check("C.4: corrected CYKParse never reads an unwritten entry (order: j increasing, i decreasing)", ok_cyk)
check("C.4: Gen?(A, x) string recurrence (p. 5) is correct", ok_rec)
check("C.4: Gen?(A, i, j) index recurrence (p. 6) is correct with S as the answer", ok_idx)
check("C.4: innermost test runs exactly (#binary rules) * (n^3 - n)/6 times: O(n^3 L)", ok_work)
check("C.4 note error p. 6: printed loop 'for i <- n down to j+1' never fills Gen[S,1,n] (read of unwritten entry, every"
      " w with n >= 2)", printed_fail == n_long, f"{printed_fail} of {n_long}")
check("C.4 note error p. 6: with all-False initialization the printed CYKParse rejects members of length >= 2",
      printed_default_wrong > 0, f"{printed_default_wrong} members rejected")
check("C.4 note error p. 6: 'Gen?(A,1,n) for some A' (instead of S) accepts non-members", note_A_wrong > 0,
      f"{note_A_wrong} disagreements")

# printed CYK on a specific member, to cite: grammar below, w = ()
# ---- the note's balanced-parentheses grammar (p. 5, flagged 'This is incorrect.' by the author)
note_g = CFG.parse("S -> eps | AA | BC\nA -> AA | BC\nB -> LA\nC -> RA\nL -> (\nR -> )")
lang = note_g.language(10)
check("C.4: the note's parenthesis grammar generates only the empty string (strings up to length 10)", lang == {""},
      str(sorted(lang)))
for X in "ABC":
    check(f"C.4: in the note's grammar, {X} generates no string of length <= 10", note_g.language(10, start=X) == set())


def balanced(w):
    d = 0
    for c in w:
        d += 1 if c == "(" else -1
        if d < 0:
            return False
    return d == 0


fix = {"S": [(), ("A", "A"), ("L", "R"), ("L", "B")], "A": [("A", "A"), ("L", "R"), ("L", "B")],
       "B": [("A", "R")], "L": [("(",)], "R": [(")",)]}
fixg = CFG("S", fix)
check("C.4 page: corrected grammar is in CNF", fixg.is_cnf()[0], str(fixg.is_cnf()))
okb = all(fixg.generates(w) == balanced(w) for w in strings("()", 12))
check("C.4 page: corrected grammar generates exactly the balanced strings (Earley, all strings up to length 12)", okb)
okb2 = all(cyk(fix, "S", w)[0] == balanced(w) for w in strings("()", 12))
check("C.4 page: CYK on the corrected grammar = balanced, all strings up to length 12", okb2)
okA = all(fixg.generates(w, start="A") == (balanced(w) and w != "") for w in strings("()", 12))
check("C.4 page: A generates the non-empty balanced strings", okA)
okB = all(fixg.generates(w, start="B") == (w.endswith(")") and balanced(w[:-1]) and w[:-1] != "")
          for w in strings("()", 12))
check("C.4 page: B generates x) with x non-empty balanced", okB)

# the CYK table on the page: w = (())()
w = "(())()"
_, Gen = cyk(fix, "S", w)
cells = {}
for i in range(1, 7):
    for j in range(i, 7):
        cells[(i, j)] = "".join(X for X in ["S", "A", "B", "L", "R"] if Gen[X, i, j])
expect = {(1, 1): "L", (2, 2): "L", (3, 3): "R", (4, 4): "R", (5, 5): "L", (6, 6): "R",
          (2, 3): "SA", (5, 6): "SA", (2, 4): "B", (1, 4): "SA", (1, 6): "SA", (3, 5): "", (1, 3): "", (4, 6): "",
          (1, 2): "", (3, 4): "", (4, 5): "", (1, 5): "", (2, 5): "", (2, 6): "", (3, 6): ""}
check("C.4 page example: CYK table for (())() (nonempty cells: L,L,R,R,L,R; [2..3],[5..6] = S,A; [2..4] = B;"
      " [1..4],[1..6] = S,A)", cells == expect, str({k: v for k, v in cells.items() if v}))
check("C.4 page example: (())() is accepted", Gen["S", 1, 6])
# split points that put S/A into cell [1..6]: k = 4 (A A)
splits = [k for k in range(1, 6) if Gen["A", 1, k] and Gen["A", k + 1, 6]]
check("C.4 page example: the only rule/split for [1..6] is A A at k = 4", splits == [4] and not any(
    Gen["L", 1, k] and (Gen["R", k + 1, 6] or Gen["B", k + 1, 6]) for k in range(1, 6)), str(splits))
# =====================================================================================================
# concept page cyk-algorithm: grammar for {0^n 1^n : n >= 1} in CNF and the table for 0011
# =====================================================================================================
g01 = {"S": [("Z", "O"), ("Z", "T")], "T": [("X", "O")], "X": [("Z", "O"), ("Z", "T")], "Z": [("0",)], "O": [("1",)]}
cg = CFG("S", g01)
check("concept: grammar S -> ZO|ZT, T -> XO, X -> ZO|ZT, Z -> 0, O -> 1 is CNF", cg.is_cnf()[0])
ok01 = all(cyk(g01, "S", w)[0] == (len(w) >= 2 and w == "0" * (len(w) // 2) + "1" * (len(w) // 2))
           for w in strings("01", 12))
check("concept: it generates exactly {0^n 1^n : n >= 1} (CYK, all strings up to length 12)", ok01)
ok01e = all(cg.generates(w) == cyk(g01, "S", w)[0] for w in strings("01", 10))
check("concept: Earley agrees (up to length 10)", ok01e)
_, Gc = cyk(g01, "S", "0011")
cells = {(i, j): "".join(X for X in ["S", "T", "X", "Z", "O"] if Gc[X, i, j]) for i in range(1, 5) for j in range(i, 5)}
check("concept example: table for 0011: [1..1],[2..2] = Z; [3..3],[4..4] = O; [2..3] = S,X; [2..4] = T; "
      "[1..4] = S,X; all other cells empty",
      cells == {(1, 1): "Z", (2, 2): "Z", (3, 3): "O", (4, 4): "O", (1, 2): "", (2, 3): "SX", (3, 4): "",
                (1, 3): "", (2, 4): "T", (1, 4): "SX"}, str(cells))
_, Gd = cyk(g01, "S", "0101")
check("concept example: 0101 is rejected; [1..2] and [3..4] contain S,X but no rule joins them",
      not Gd["S", 1, 4] and Gd["S", 1, 2] and Gd["X", 3, 4])

# counting parse trees by replacing OR/AND with +/x, and recovering a parse tree from stored rule/split
def cyk_count(G, w):
    n = len(w)
    N = {}
    for i in range(1, n + 1):
        for A in G:
            N[(A, i, i)] = 1 if (w[i - 1],) in G[A] else 0
    for ln in range(2, n + 1):
        for i in range(1, n - ln + 2):
            j = i + ln - 1
            for A in G:
                N[(A, i, j)] = sum(N[(r[0], i, k)] * N[(r[1], k + 1, j)] for r in G[A] if len(r) == 2
                                   for k in range(i, j))
    return N


def cyk_tree(G, w):
    n = len(w)
    ok, Gen = cyk(G, "S", w)
    if not ok:
        return None

    def build(A, i, j):
        if i == j:
            return (A, w[i - 1])
        for r in G[A]:
            if len(r) == 2:
                for k in range(i, j):
                    if Gen[r[0], i, k] and Gen[r[1], k + 1, j]:
                        return (A, build(r[0], i, k), build(r[1], k + 1, j))
    return build("S", 1, n)


def tree_ok(G, t):
    if len(t) == 2:
        return (t[1],) in G[t[0]], t[1]
    okl, yl = tree_ok(G, t[1])
    okr, yr = tree_ok(G, t[2])
    return okl and okr and (t[1][0], t[2][0]) in G[t[0]], yl + yr


ok_count = ok_tree = True
for trial in range(150):
    G = random_cnf()
    G2 = {X: [r for r in rs if r != ()] for X, rs in G.items()}
    lib = CFG("S", {X: (rs if rs else [("0", "0", "0", "0", "0", "0", "0", "0", "0")]) for X, rs in G2.items()})
    for w in strings("01", 6, minlen=1):
        N = cyk_count(G2, w)
        try:
            ok_count &= (N[("S", 1, len(w))] == lib.count_parse_trees(w))
        except ValueError:
            pass
        t = cyk_tree(G2, w)
        if t is not None:
            good, y = tree_ok(G2, t)
            ok_tree &= good and y == w
check("concept: counting version (+ and x) equals the number of parse trees (library count, 150 random CNF grammars,"
      " all strings of length 1..6)", ok_count)
check("concept: walking down stored rule/split choices from (S,1,n) gives a valid parse tree of w", ok_tree)

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: {FAIL}")
sys.exit(1 if FAIL else 0)
