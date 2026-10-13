#!/usr/bin/env python3
"""Checks for every concrete claim on content/1-models-of-computation/08-universal-models.md."""
import os
import random
import sys
from collections import deque
from fractions import Fraction
from itertools import product

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from automata import TM, strings  # noqa: E402

FAIL = []


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAIL.append(name)


B = "□"
R, L = +1, -1


def rows(spec):
    d = {}
    for p, syms, q, b, mv in spec:
        for a in syms:
            d[(p, a)] = (q, a if b is None else b, mv)
    return d


# the machine of Chapter 6, section 6.3 (decides {0^n 1^n 0^n})
ZOZ = rows([
    ("start", "0", "block1", "#", R), ("start", B, "accept", None, R),
    ("block1", "0", "block1", None, R), ("block1", "1", "block2", None, R),
    ("block2", "1", "block2", None, R), ("block2", "0", "block3", None, R),
    ("block3", "0", "block3", None, R), ("block3", B, "rewind", None, L),
    ("rewind", "01", "rewind", None, L), ("rewind", "#", "seek1", None, R),
    ("seek1", "0x", "seek1", None, R), ("seek1", "1", "seek0", "x", R),
    ("seek0", "1x", "seek0", None, R), ("seek0", "0", "reset", "x", L),
    ("reset", "01x", "reset", None, L), ("reset", "#", "mark0", None, R),
    ("mark0", "0", "seek1", "#", R), ("mark0", "x", "verify", None, R),
    ("verify", "x", "verify", None, R), ("verify", B, "accept", None, R),
])
M = TM(ZOZ)
INPUTS = list(strings("01", 10))

# ---------------------------------------------------------------- 8.2 two stacks


def two_stack_run(delta, w, max_steps=100000, ops=None):
    """ops, if given, collects (move, pops, pushes) for every simulated step."""
    left = []                      # cells left of the head, top = nearest the head
    right = list(reversed(w))      # head cell and everything to its right, top = head cell
    q = "start"
    for _ in range(max_steps):
        if q in ("accept", "reject"):
            break
        a = right.pop() if right else B          # pop the head symbol (empty stack = blank)
        if (q, a) not in delta:
            right.append(a)
            q = "reject"
            break
        q, b, mv = delta[(q, a)]
        if mv == +1:
            left.append(b)                       # written symbol ends up left of the head
            if ops is not None:
                ops.append((mv, 1, 1))
        else:
            right.append(b)                      # written symbol is now right of the head
            if not left:
                return "crash", None
            right.append(left.pop())             # the new head cell moves to the right stack
            if ops is not None:
                ops.append((mv, 2, 2))
    tape = "".join(left) + "".join(reversed(right))
    return q, tape.rstrip(B)


bad = [w for w in INPUTS if (M.run(w)[0], M.run(w)[2]) != two_stack_run(ZOZ, w)]
check("two-stack simulation of the 0^n1^n0^n machine: same outcome and final tape for every w, |w| <= 10",
      not bad, str(bad[:3]))
OPS = []
for w in INPUTS:
    two_stack_run(ZOZ, w, ops=OPS)
check("one step = a pop and a push (move right), plus moving one symbol from the left stack to the right stack "
      "(move left: two pops, two pushes)", {o for o in OPS} == {(+1, 1, 1), (-1, 2, 2)})
out, steps, tape, head, confs = M.run("001100", trace=True)
check("figure: configuration (reset, #0x1x0, 3) = left stack #,0,x (top x) and right stack 1,x,0 (top 1)",
      ("reset", "#0x1x0", 3) in confs and list("#0x1x0"[:3]) == ["#", "0", "x"] and list("#0x1x0"[3:]) == ["1", "x", "0"])

# ---------------------------------------------------------------- 8.3 counter machines
GAM = [B, "0", "1", "#", "x"]          # digit values 0..4; blank = 0 so trailing blanks cost nothing
DIG = {a: i for i, a in enumerate(GAM)}
BETA = len(GAM)


def numbers_run(delta, w, max_steps=100000):
    """The tape as two numbers: left half (nearest cell least significant, plus a leading sentinel digit 1)
    and right half (head cell least significant)."""
    Lnum = 1
    Rnum = sum(DIG[a] * BETA ** i for i, a in enumerate(w))
    q = "start"
    for _ in range(max_steps):
        if q in ("accept", "reject"):
            break
        a = GAM[Rnum % BETA]
        if (q, a) not in delta:
            q = "reject"
            break
        q, b, mv = delta[(q, a)]
        Rnum = Rnum - DIG[a] + DIG[b]
        if mv == +1:
            Lnum, Rnum = BETA * Lnum + Rnum % BETA, Rnum // BETA
        else:
            if Lnum == 1:
                return "crash", None
            Lnum, Rnum = Lnum // BETA, BETA * Rnum + Lnum % BETA
    left = []
    while Lnum > 1:
        left.append(GAM[Lnum % BETA])
        Lnum //= BETA
    right = []
    while Rnum:
        right.append(GAM[Rnum % BETA])
        Rnum //= BETA
    return q, ("".join(reversed(left)) + "".join(right)).rstrip(B)


bad = [w for w in INPUTS if (M.run(w)[0], M.run(w)[2]) != numbers_run(ZOZ, w)]
check("tape-as-two-numbers simulation (base |Γ| = 5) agrees with the machine for every w, |w| <= 10", not bad, str(bad[:3]))


def counter_run(prog, start, counters, max_steps=10 ** 6):
    """k-counter machine: prog[(state, zero-pattern)] = (next state, increments); halts in state 'halt*'."""
    c = list(counters)
    q = start
    for _ in range(max_steps):
        if q.startswith("halt"):
            return q, c
        z = tuple(x == 0 for x in c)
        q, inc = prog[(q, z)]
        c = [x + d for x, d in zip(c, inc)]
        assert min(c) >= 0
    return "timeout", c


def all_patterns(k):
    return list(product([True, False], repeat=k))


def prog_mul(k):
    """(n, 0) -> (k n, 0) using only +-1 and zero tests."""
    P = {}
    for z in all_patterns(2):
        # take: move one unit from counter 0 to counter 1, as k increments
        P[("take", z)] = ("halt", (0, 0)) if z[0] and z[1] else (("back", (0, 0)) if z[0] else ("add1", (-1, 0)))
        for j in range(1, k):
            P[(f"add{j}", z)] = (f"add{j + 1}", (0, 1))
        P[(f"add{k}", z)] = ("take", (0, 1))
        P[("back", z)] = ("halt", (0, 0)) if z[1] else ("back", (1, -1))
    return P


def prog_divmod(k):
    """(n, 0): if k divides n, end in 'halt-yes' with (n/k, 0); otherwise 'halt-no' with (n, 0)."""
    P = {}
    for z in all_patterns(2):
        # sub_j: j units of the current group of k already moved; count groups in counter 1 (one unit per group)
        for j in range(k):
            if z[0]:
                P[(f"sub{j}", z)] = ("yes", (0, 0)) if j == 0 else (f"undo{j}", (0, 0))
            else:
                P[(f"sub{j}", z)] = (f"sub{j + 1}", (-1, 0)) if j + 1 < k else ("sub0", (-1, 1))
        # divisible: counter 1 holds n/k; move it to counter 0
        P[("yes", z)] = ("halt-yes", (0, 0)) if z[1] else ("yes", (1, -1))
        # not divisible: put back the j units and k units per counted group
        for j in range(1, k):
            P[(f"undo{j}", z)] = (f"undo{j - 1}", (1, 0)) if j > 1 else ("regroup", (1, 0))
        P[("regroup", z)] = ("halt-no", (0, 0)) if z[1] else ("put1", (0, -1))
        for j in range(1, k):
            P[(f"put{j}", z)] = (f"put{j + 1}", (1, 0))
        P[(f"put{k}", z)] = ("regroup", (1, 0))
    return P


def prog_divrem(k):
    """(n, 0) -> (n // k, 0), ending in state 'halt-r<n mod k>' (the remainder is remembered by the state)."""
    P = {}
    for z in all_patterns(2):
        for j in range(k):
            if z[0]:
                P[(f"sub{j}", z)] = (f"move{j}", (0, 0))
            else:
                P[(f"sub{j}", z)] = (f"sub{j + 1}", (-1, 0)) if j + 1 < k else ("sub0", (-1, 1))
            P[(f"move{j}", z)] = (f"halt-r{j}", (0, 0)) if z[1] else (f"move{j}", (1, -1))
    return P


ok = all(counter_run(prog_divrem(k), "sub0", (n, 0)) == (f"halt-r{n % k}", [n // k, 0])
         for k in (2, 3, 5) for n in range(301))
check("two-counter program divides by k and leaves the remainder in the state (k = 2, 3, 5, n <= 300)", ok)

ok = True
for k in (2, 3, 5):
    Pm, Pd = prog_mul(k), prog_divmod(k)
    for n in range(0, 301):
        if counter_run(Pm, "take", (n, 0)) != ("halt", [k * n, 0]):
            ok = False
        want = ("halt-yes", [n // k, 0]) if n % k == 0 else ("halt-no", [n, 0])
        if counter_run(Pd, "sub0", (n, 0)) != want:
            ok = False
check("two-counter programs (only +-1 and zero tests) multiply by k and divide by k with a divisibility test, "
      "k = 2, 3, 5, n <= 300", ok)
ok = all(2 ** a * 3 ** (b + 1) * 5 ** c == 3 * (2 ** a * 3 ** b * 5 ** c)
         and ((2 ** a * 3 ** b * 5 ** c) % 5 == 0) == (c > 0)
         and (c == 0 or 2 ** a * 3 ** b * 5 ** (c - 1) == (2 ** a * 3 ** b * 5 ** c) // 5)
         for a in range(8) for b in range(8) for c in range(8))
check("2^a3^b5^c: b+1 is x3, c-1 is /5, and c = 0 iff 5 does not divide (a,b,c < 8)", ok)

# ---------------------------------------------------------------- 8.4 FRACTRAN


def fractran(prog, n, max_steps=10 ** 5):
    prog = [Fraction(f) for f in prog]
    for steps in range(max_steps):
        for f in prog:
            if (n * f).denominator == 1:
                n = int(n * f)
                break
        else:
            return n, steps
    return None, max_steps


check("[3/2] turns 2^a 3^b into 3^(a+b) in a steps (a, b <= 12)",
      all(fractran(["3/2"], 2 ** a * 3 ** b) == (3 ** (a + b), a) for a in range(13) for b in range(13)))
MULT = ["455/33", "11/13", "1/11", "3/7", "11/2", "1/3"]
check("the program [455/33, 11/13, 1/11, 3/7, 11/2, 1/3] turns 2^a 3^b into 5^(ab) (a, b <= 6)",
      all(fractran(MULT, 2 ** a * 3 ** b)[0] == 5 ** (a * b) for a in range(7) for b in range(7)))
random.seed(8)
ok = True
for _ in range(2000):
    prog = [Fraction(random.randint(1, 12), random.randint(1, 12)) for _ in range(random.randint(1, 5))]
    has_int = any(f.denominator == 1 for f in prog)
    res, steps = fractran(prog, 1, max_steps=500)
    if has_int and res is not None:
        ok = False
    if not has_int and (res, steps) != (1, 0):
        ok = False
check("started at 1, a program halts at once (output 1) if no fraction is an integer, else runs forever "
      "(2000 random programs, 500 steps)", ok)

# ---------------------------------------------------------------- 8.5 PCP
DOM = {"a": ("0", "100"), "b": ("01", "00"), "c": ("110", "11")}


def rows_of(seq):
    return "".join(DOM[d][0] for d in seq), "".join(DOM[d][1] for d in seq)


check("cbca: both rows spell 110011100", rows_of("cbca") == ("110011100", "110011100"))
check("c·b·c·a top = 110|01|110|0, bottom = 11|00|11|100",
      [DOM[d][0] for d in "cbca"] == ["110", "01", "110", "0"] and [DOM[d][1] for d in "cbca"] == ["11", "00", "11", "100"])
sols = {n: [s for s in map("".join, product("abc", repeat=n)) if rows_of(s)[0] == rows_of(s)[1]] for n in range(1, 9)}
check("no solution with 1, 2 or 3 dominoes; cbca is the only solution with 4", not sols[1] and not sols[2]
      and not sols[3] and sols[4] == ["cbca"], str({n: len(v) for n, v in sols.items()}))
check("every solution starts with c (a and b mismatch in their first symbol)",
      all(s[0] == "c" for n in sols for s in sols[n]) and DOM["a"][0][0] != DOM["a"][1][0] and DOM["b"][0][1] != DOM["b"][1][1])
check("concatenating solutions gives solutions: cbcacbca", rows_of("cbcacbca")[0] == rows_of("cbcacbca")[1])
check("(book typo) the book's printed 110110100 is not what c, b, c, a spells", rows_of("cbca")[0] != "110110100")


def pcp_shortest(doms, max_len):
    """Complete breadth-first search for a shortest solution with at most max_len dominoes; returns the index
    sequence or None. A state is (side ahead, unmatched overhang). An overhang longer than (dominoes left) x (the
    most one domino can shorten it) cannot be cancelled in time, so pruning it loses no solution."""
    shrink = (max(len(y) - len(x) for x, y in doms),      # top ahead
              max(len(x) - len(y) for x, y in doms))      # bottom ahead
    layer, parent = [(0, "")], {(0, ""): None}
    for d in range(1, max_len + 1):
        nxt = []
        for st in layer:
            side, over = st
            for i, (x, y) in enumerate(doms):
                top, bot = (over + x, y) if side == 0 else (x, over + y)
                if top.startswith(bot):
                    new = (0, top[len(bot):])
                elif bot.startswith(top):
                    new = (1, bot[len(top):])
                else:
                    continue
                if new[1] == "":
                    seq, cur = [i], st
                    while parent[cur] is not None:
                        cur, j = parent[cur]
                        seq.append(j)
                    return seq[::-1]
                if len(new[1]) > (max_len - d) * shrink[new[0]] or new in parent:
                    continue
                parent[new] = (st, i)
                nxt.append(new)
        layer = nxt
    return None


LONG = [("0", "001"), ("001", "1"), ("1", "0")]
sol = pcp_shortest(LONG, 75)
check("the book's instance (0/001), (001/1), (1/0): no solution with at most 74 dominoes, a solution with 75 "
      "(complete search)", pcp_shortest(LONG, 74) is None and sol is not None and len(sol) == 75
      and "".join(LONG[i][0] for i in sol) == "".join(LONG[i][1] for i in sol),
      f"{len(sol) if sol else None} dominoes")

# ---------------------------------------------------------------- 8.6 matrix mortality


def mul(X, Y):
    n = len(X)
    return tuple(tuple(sum(X[i][k] * Y[k][j] for k in range(n)) for j in range(n)) for i in range(n))


def power(X, k):
    n = len(X)
    P = tuple(tuple(int(i == j) for j in range(n)) for i in range(n))
    for _ in range(k):
        P = mul(P, X)
    return P


def zero(X):
    return all(v == 0 for r in X for v in r)


MA = ((1, 0), (0, 0))
MB = ((0, 0), (1, 1))
check("A = [[1,0],[0,0]], B = [[0,0],[1,1]]: AB = 0, BA = [[0,0],[1,0]], A^2 = A, B^2 = B (so no power of A or B is 0)",
      zero(mul(MA, MB)) and mul(MB, MA) == ((0, 0), (1, 0)) and mul(MA, MA) == MA and mul(MB, MB) == MB)
random.seed(6)
ok = True
for _ in range(3000):
    n = random.choice([2, 3])
    X = tuple(tuple(random.randint(-2, 2) for _ in range(n)) for _ in range(n))
    if random.random() < 0.3:      # strictly upper triangular matrices are nilpotent: include some
        X = tuple(tuple(X[i][j] if j > i else 0 for j in range(n)) for i in range(n))
    some = any(zero(power(X, k)) for k in range(1, 12))
    if some != zero(power(X, n)):
        ok = False
check("one matrix: some power of an n x n matrix is 0 iff its n-th power is (3000 random 2x2, 3x3)", ok)

# ---------------------------------------------------------------- 8.9 combinators


def parse(s):
    pos = 0

    def atom():
        nonlocal pos
        if s[pos] == "(":
            pos += 1
            t = seq()
            assert s[pos] == ")"
            pos += 1
            return t
        pos += 1
        return s[pos - 1]

    def seq():
        t = atom()
        while pos < len(s) and s[pos] != ")":
            t = (t, atom())
        return t

    t = seq()
    assert pos == len(s)
    return t


def fmt(t):
    if isinstance(t, str):
        return t
    f, a = t
    return fmt(f) + (fmt(a) if isinstance(a, str) else "(" + fmt(a) + ")")


def kind(t):
    if isinstance(t, tuple):
        if t[0] == "I":
            return "I"
        if isinstance(t[0], tuple) and t[0][0] == "K":
            return "K"
        if isinstance(t[0], tuple) and isinstance(t[0][0], tuple) and t[0][0][0] == "S":
            return "S"
    return None


def contract(t):
    k = kind(t)
    if k == "I":
        return t[1]
    if k == "K":
        return t[0][1]
    x, y, z = t[0][0][1], t[0][1], t[1]
    return ((x, z), (y, z))


def redexes(t, path=()):
    """All redex positions in pre-order (= leftmost-outermost first)."""
    out = [(path, kind(t))] if kind(t) else []
    if isinstance(t, tuple):
        out += redexes(t[0], path + (0,)) + redexes(t[1], path + (1,))
    return out


def replace(t, path, new):
    if not path:
        return new
    f, a = t
    return (replace(f, path[1:], new), a) if path[0] == 0 else (f, replace(a, path[1:], new))


def get(t, path):
    for i in path:
        t = t[i]
    return t


def step(t, strategy):
    rs = redexes(t)
    if not rs:
        return None
    if strategy == "normal":
        path = rs[0][0]
    else:  # "IK-first": leftmost I- or K-redex if any, else the leftmost S-redex
        ik = [p for p, k in rs if k in "IK"]
        path = ik[0] if ik else rs[0][0]
    return replace(t, path, contract(get(t, path)))


def run(s, strategy, n):
    t, seq = parse(s), [s]
    for _ in range(n):
        t = step(t, strategy)
        if t is None:
            break
        seq.append(fmt(t))
    return seq


check("parser/printer round trip: SKK(IS) is (((S,K),K),(I,S))", parse("SKK(IS)") == ((("S", "K"), "K"), ("I", "S"))
      and fmt(parse("SKK(IS)")) == "SKK(IS)")
want_R = ["S(K(SI))Kxy", "K(SI)x(Kx)y", "SI(Kx)y", "Iy(Kxy)", "y(Kxy)", "yx"]
check("R = S(K(SI))K: Rxy reduces to yx in 5 leftmost-outermost steps, through the listed terms",
      run("S(K(SI))Kxy", "normal", 10) == want_R, " -> ".join(run("S(K(SI))Kxy", "normal", 10)))
check("same sequence with the I/K-first order", run("S(K(SI))Kxy", "IK-first", 10) == want_R)
check("SKKx -> Kx(Kx) -> x: SKK behaves like I", run("SKKx", "normal", 5) == ["SKKx", "Kx(Kx)", "x"])
want_loop = ["SII(S(KI)(SII))", "I(S(KI)(SII))(I(S(KI)(SII)))", "S(KI)(SII)(I(S(KI)(SII)))",
             "S(KI)(SII)(S(KI)(SII))", "KI(S(KI)(SII))(SII(S(KI)(SII)))", "I(SII(S(KI)(SII)))", "SII(S(KI)(SII))"]
check("SII(S(KI)(SII)) returns to itself after 6 steps (I/K-first order), through the listed terms",
      run("SII(S(KI)(SII))", "IK-first", 6) == want_loop, " -> ".join(run("SII(S(KI)(SII))", "IK-first", 6)))
# leftmost-outermost: SII(I^k T) -> SII(I^(k+1) T) in k + 5 steps, never a normal form
T = "S(KI)(SII)"


def nest(k):
    s = T
    for _ in range(k):
        s = "I(" + s + ")"
    return "SII(" + s + ")" if k else "SII(" + T + ")"


ok, t = True, parse(nest(0))
for k in range(0, 15):
    for _ in range(k + 5):
        t = step(t, "normal")
    if fmt(t) != nest(k + 1):
        ok = False
check("leftmost-outermost order: SII(T), SII(IT), SII(I(IT)), ... each reached from the previous in k+5 steps "
      "(k <= 14); the term never returns to itself", ok, f"{nest(2)}")
t, n = parse(nest(0)), 0
while t is not None and n < 3000:
    t, n = step(t, "normal"), n + 1
check("no normal form within 3000 leftmost-outermost steps", t is not None)

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: {FAIL}")
sys.exit(1 if FAIL else 0)
