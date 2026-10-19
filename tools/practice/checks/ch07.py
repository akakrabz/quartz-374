#!/usr/bin/env python3
"""Checks for every checkable claim on content/practice/07-undecidability.md.

Undecidability itself cannot be tested, so this script checks everything concrete around the proofs:
the witness machines Y and N of every Rice argument and the machines in the "Rice does not apply"
arguments (simulated on all short inputs, with divergence proved by a repeated configuration or an
endless walk right over blanks); the bounded-simulation decider of 7.5(a) against long simulations of
random machines, with the configuration bound; the transformation of 7.5(b) on random machines; the
dovetailing acceptor of 7.6 against the serial search it replaces; the case analysis of the diagonal
argument in 7.7 (and the failure of the 'flip' wrapper); and the split-and-test decider of 7.1(c)."""
import itertools
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from automata import TM, strings  # noqa: E402

FAIL = []
B = "□"


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAIL.append(name)


def fate(M, w, limit=3000):
    """accept / reject / crash, or 'diverge' with a proof -- a repeated configuration, or the head beyond
    every non-blank cell in a state whose blank-only walk (all moves right) cycles -- else 'unknown'."""
    tape, q, h, seen = list(w), M.start, 0, set()
    for _ in range(limit):
        if q == M.accept:
            return "accept"
        if q == M.reject:
            return "reject"
        last = len(tape) - 1
        while last >= 0 and tape[last] == B:
            last -= 1
        if h > last:
            p, vis = q, set()
            while p not in (M.accept, M.reject) and (p, B) in M.delta and M.delta[(p, B)][2] == 1:
                if p in vis:
                    return "diverge"
                vis.add(p)
                p = M.delta[(p, B)][0]
        key = (q, h, tuple(tape[:last + 1]))
        if key in seen:
            return "diverge"
        seen.add(key)
        while h >= len(tape):
            tape.append(B)
        c = tape[h]
        if (q, c) not in M.delta:
            q = M.reject
            continue
        p, b, mv = M.delta[(q, c)]
        tape[h] = b
        h += mv
        q = p
        if h < 0:
            return "crash"
    return "unknown"


def sets(M, alphabet="01", n=8):
    acc, rej, div = set(), set(), set()
    for w in strings(alphabet, n):
        f = fate(M, w)
        assert f != "unknown", (w, f)
        {"accept": acc, "reject": rej}.get(f, div).add(w)
    return acc, rej, div


ALL = set(strings("01", 8))
GAM = ["0", "1", B]
M_ACCEPT = TM({("start", a): ("accept", a, 1) for a in GAM})
M_REJECT = TM({("start", a): ("reject", a, 1) for a in GAM})
M_DIVERGE = TM({("start", a): ("start", a, 1) for a in GAM})
a, r, d = sets(M_ACCEPT)
check("M_Accept accepts every input (|w| <= 8)", a == ALL and not r and not d)
a, r, d = sets(M_REJECT)
check("M_Reject rejects every input", r == ALL and not a and not d)
a, r, d = sets(M_DIVERGE)
check("M_Diverge runs forever on every input (moves right forever)", d == ALL and not a and not r)

# ====================================================================== 7.4 Rice
N01 = TM({("start", "0"): ("saw0", "0", 1), ("saw0", "1"): ("saw01", "1", 1), ("saw01", B): ("accept", B, 1)})
a, r, d = sets(N01, n=10)
check("7.4(a) N accepts exactly {01} and rejects everything else (|w| <= 10)",
      a == {"01"} and r == set(strings("01", 10)) - {"01"} and not d)
check("7.4(a) Accept(N) = {01} is not closed under reversal: 01 in, 10 out", "01" in a and "10" not in a)
for name, M in [("M_Accept", M_ACCEPT), ("M_Reject", M_REJECT)]:
    acc = sets(M)[0]
    check(f"7.4(a) Accept({name}) is closed under reversal (|w| <= 8)", all(w[::-1] in acc for w in acc))
Y1 = TM({("start", B): ("reject", B, 1), ("start", "0"): ("accept", "0", 1), ("start", "1"): ("accept", "1", 1)})
a, r, d = sets(Y1)
check("7.4(b) Y rejects exactly one string (epsilon) and accepts all others", r == {""} and a == ALL - {""} and not d)
check("7.4(b) N = M_Accept rejects no string: Reject(N) has 0 elements, not 1", not sets(M_ACCEPT)[1])
Y1L = TM({("start", B): ("start", B, 1), ("start", "0"): ("accept", "0", 1), ("start", "1"): ("accept", "1", 1)})
a2, r2, d2 = sets(Y1L)
check("7.4(b) watch out: Y' = same accepted language as Y, but diverges on epsilon, so rejects nothing",
      a2 == a and not r2 and d2 == {""})
check("7.4(c) Y = M_Diverge: Accept = Reject = empty; N = M_Accept: Accept = Sigma* != Reject = empty",
      sets(M_DIVERGE)[0] == sets(M_DIVERGE)[1] == set() and sets(M_ACCEPT)[0] != sets(M_ACCEPT)[1])

rng = random.Random(7)


def random_tm(nstates, gamma, p_missing=0.15, moves=(-1, 1)):
    states = ["start"] + [f"q{i}" for i in range(nstates - 1)]
    d = {}
    for q in states:
        for c in gamma:
            if rng.random() > p_missing:
                d[(q, c)] = (rng.choice(states + ["accept", "reject"]), rng.choice(gamma), rng.choice(moves))
    return TM(d), states


ok = True
for _ in range(300):
    M, _s = random_tm(rng.randint(1, 3), GAM)
    outs = [M.run(w, max_steps=300)[0] for w in strings("01", 4)]
    acc = {w for w, o in zip(strings("01", 4), outs) if o == "accept"}
    rej = {w for w, o in zip(strings("01", 4), outs) if o == "reject"}
    ok = ok and not (acc & rej) and ((acc == rej) == (not acc and not rej))
check("7.4(c) on 300 random machines, Accept and Reject are disjoint, so Accept = Reject only when both are empty", ok)


# ====================================================================== 7.5(a) visiting cell k: bounded simulation
def visits_cell(M, states, gamma, w, k, limit):
    """Simulate until the head is on cell k (True), M halts/crashes (False), or a configuration restricted to
    cells 0..k-1 repeats (False: the run is periodic and never gets there). Returns (answer, steps, reason)."""
    tape = list(w)
    q, h, t = M.start, 0, 0
    seen = set()
    while True:
        if h == k:
            return True, t, "visit"
        if q in (M.accept, M.reject):
            return False, t, "halt"
        key = (q, h, tuple(tape[:k]))
        if key in seen:
            return False, t, "repeat"
        seen.add(key)
        if t >= limit:
            return None, t, "limit"
        while h >= len(tape):
            tape.append(B)
        c = tape[h]
        t += 1
        if (q, c) not in M.delta:
            q = M.reject
            continue
        p, b, mv = M.delta[(q, c)]
        tape[h] = b
        h += mv
        q = p
        if h < 0:
            return False, t, "crash"


def long_run_visits(M, w, k, steps):
    tape = list(w)
    q, h = M.start, 0
    for t in range(steps + 1):
        if h == k:
            return True, t
        if q in (M.accept, M.reject):
            return False, t
        while h >= len(tape):
            tape.append(B)
        c = tape[h]
        if (q, c) not in M.delta:
            return False, t + 1
        p, b, mv = M.delta[(q, c)]
        tape[h] = b
        h += mv
        q = p
        if h < 0:
            return False, t + 1
    return False, steps


ok_bound, ok_agree, nvisit, nrepeat, worst = True, True, 0, 0, 0.0
for trial in range(400):
    k = rng.randint(2, 4)
    gamma = GAM + (["x"] if rng.random() < 0.5 else [])
    M, states = random_tm(rng.randint(1, 3), gamma)
    bound = len(states) * k * len(gamma) ** k
    for w in strings("01", 6):
        ans, t, why = visits_cell(M, states, gamma, w, k, bound + 1)
        if ans is None or t > bound:
            ok_bound = False
        truth, tt = long_run_visits(M, w, k, 20000)
        if ans != truth:
            ok_agree = False
        nvisit += why == "visit"
        nrepeat += why == "repeat"
        worst = max(worst, t / bound)
check("7.5(a) on 400 random machines (k = 2..4, inputs |w| <= 6, some longer than k): every run visits cell k, "
      "halts, crashes, or repeats a configuration of cells 0..k-1 within |Q| k |Gamma|^k steps", ok_bound,
      f"largest t/bound = {worst:.3f}")
check("7.5(a) the bounded decider agrees with 20000-step simulations", ok_agree,
      f"{nvisit} visits, {nrepeat} decided by a repeated configuration")


# ====================================================================== 7.5(b) writing #: the reduction from Accept
def dollar_version(M, gamma):
    """M': rename # to a fresh symbol %; redirect every transition into accept to a new state fin;
    from fin, on every symbol, write #, move right and accept."""
    ren = lambda c: "%" if c == "#" else c
    d = {}
    for (p, c), (q, b, mv) in M.delta.items():
        d[(p, ren(c))] = ("fin" if q == M.accept else q, ren(b), mv)
    for c in [ren(x) for x in gamma]:
        d[("fin", c)] = (M.accept, "#", 1)
    return TM(d)


def run_track_dollar(M, w, limit):
    tape = list(w)
    q, h, t, wrote = M.start, 0, 0, False
    while q not in (M.accept, M.reject):
        if t >= limit:
            return "timeout", t, wrote
        while h >= len(tape):
            tape.append(B)
        c = tape[h]
        t += 1
        if (q, c) not in M.delta:
            q = M.reject
            continue
        p, b, mv = M.delta[(q, c)]
        tape[h] = b
        wrote = wrote or b == "#"
        h += mv
        q = p
        if h < 0:
            return "crash", t, wrote
    return q, t, wrote


ok, cnt, cnt_acc, cnt_edge = True, 0, 0, 0
for trial in range(400):
    gamma = GAM + ["#"] if rng.random() < 0.6 else GAM
    M, states = random_tm(rng.randint(1, 4), gamma)
    M2 = dollar_version(M, gamma)
    for w in strings("01", 5):
        o1, t1, _ = run_track_dollar(M, w, 500)
        o2, t2, wrote = run_track_dollar(M2, w, 501)
        cnt += 1
        if o1 == "accept":
            cnt_acc += 1
            ok = ok and o2 == "accept" and t2 == t1 + 1 and wrote
        else:
            ok = ok and (o2, t2) == (o1, t1 if o1 != "timeout" else 501) and not wrote
        cnt_edge += o1 == "crash" and any(q == "accept" and mv == -1 for (q, b, mv) in M.delta.values())
check("7.5(b) on 400 random machines (60% of them using # themselves): M' behaves like M (one extra step when "
      "M accepts) and writes # exactly when M accepts -- including machines whose step into accept would crash",
      ok, f"{cnt} runs, {cnt_acc} accepting")
# the naive version (write # in the step into accept) is wrong when that step moves left from cell 0
NAIVE = TM({("start", "0"): ("accept", "#", -1)})
o, t, wrote = run_track_dollar(NAIVE, "0", 10)
check("7.5(b) watch out: writing # in the step into accept fails when that step moves left off cell 0 "
      "(the machine crashes, never accepts, but the # was written)", o == "crash" and wrote)


# ====================================================================== 7.6 dovetailing
M1 = TM({("start", B): ("start", B, 1), ("start", "0"): ("accept", "0", 1), ("start", "1"): ("reject", "1", 1)})
check("7.6 example: M1 runs forever on epsilon, accepts 0", fate(M1, "") == "diverge" and fate(M1, "0") == "accept")
order = list(strings("01", 6))


def serial(M1, M2, budget):
    """for x in order: run M1 on x to completion, then M2 -- with a total step budget."""
    used = 0
    for x in order:
        o1, t1, _, _ = M1.run(x, max_steps=budget - used)
        used += t1
        if o1 == "timeout":
            return None
        if o1 == "accept":
            o2, t2, _, _ = M2.run(x, max_steps=budget - used)
            used += t2
            if o2 == "timeout":
                return None
            if o2 == "accept":
                return x
    return "none"


def dovetail(M1, M2, rounds):
    for t in range(1, rounds + 1):
        for x in order[:t]:
            if M1.run(x, max_steps=t)[0] == "accept" and M2.run(x, max_steps=t)[0] == "accept":
                return x, t
    return None, None


check("7.6 serial search (M1 on epsilon first) is still stuck after 100000 steps", serial(M1, M_ACCEPT, 100000) is None)
check("7.6 dovetailing finds the common string 0 in round 2", dovetail(M1, M_ACCEPT, 10) == ("0", 2))
ok, found = True, 0
for trial in range(300):
    A, _ = random_tm(rng.randint(1, 3), GAM)
    Bm, _ = random_tm(rng.randint(1, 3), GAM)
    common = []
    for i, x in enumerate(order[:15]):
        oa, ta, _, _ = A.run(x, max_steps=60)
        ob, tb, _, _ = Bm.run(x, max_steps=60)
        if oa == ob == "accept":
            common.append((i, x, ta, tb))
    x, t = dovetail(A, Bm, 61)
    if common:
        found += 1
        i, cx, ta, tb = common[0]
        best = min(max(i + 1, ta, tb) for i, cx, ta, tb in common)
        if x is None or t > best or not (A.accepts(x) and Bm.accepts(x)):
            ok = False
check("7.6 on 300 random pairs: dovetailing finds a common accepted string, by round max(i+1, t1, t2) for the "
      "first string the pair has in common, and only real common strings", ok, f"{found} pairs with a common string")

# ====================================================================== 7.7 the diagonal argument
# W(eps) = accept; W(<M>) = D's answer on <M>. L = {<M> : M accepts eps and M rejects <M>}.
contradictions = []
for D_on_W in ("accept", "reject"):
    W_on_W = D_on_W                      # W copies D's answer on encodings
    W_accepts_eps = True
    in_L = W_accepts_eps and W_on_W == "reject"
    contradictions.append(in_L != (D_on_W == "accept"))
check("7.7(a) copying wrapper: both answers of D on <W> contradict 'D decides L'", all(contradictions))
consistent = []
for D_on_W in ("accept", "reject"):
    W_on_W = "reject" if D_on_W == "accept" else "accept"   # the 'flip' reflex
    in_L = True and W_on_W == "reject"
    consistent.append(in_L == (D_on_W == "accept"))
check("7.7 watch out: the flipping wrapper gives no contradiction in either case", all(consistent))
consistent = []
for D_on_W in ("accept", "reject"):
    W_on_W = D_on_W
    for W_accepts_eps in (False,):     # a wrapper that forgets to accept eps
        in_L = W_accepts_eps and W_on_W == "reject"
        consistent.append(in_L == (D_on_W == "accept"))
check("7.7 watch out: a copying wrapper that does not accept eps is consistent with D rejecting <W>",
      consistent == [False, True])
ENC = ["0", "1", "[", "]", "|"]
GE = ENC + [B]
A1 = TM({**{("start", c): ("reject", c, 1) for c in ENC}, ("start", B): ("accept", B, 1)})
A2 = TM({**{("start", c): ("loop", c, 1) for c in ENC}, ("start", B): ("accept", B, 1),
         **{("loop", c): ("loop", c, 1) for c in GE}})
A4 = TM({**{("start", c): ("reject", c, 1) for c in ENC}, ("start", B): ("loop", B, 1),
         **{("loop", c): ("loop", c, 1) for c in GE}})
U = set(strings("01[]|", 5))
s1, s2, s4 = sets(A1, "01[]|", 5), sets(A2, "01[]|", 5), sets(A4, "01[]|", 5)
check("7.7(d) M1 accepts only eps and rejects every non-empty string (strings over 0 1 [ ] | up to length 5)",
      s1[0] == {""} and s1[1] == U - {""})
check("7.7(d) M2: same accepted language {eps}, but runs forever on every non-empty string",
      s2[0] == {""} and not s2[1] and s2[2] == U - {""})
check("7.7(d) M4: same rejected language as M1, but runs forever on eps (so does not accept it)",
      s4[1] == s1[1] and not s4[0] and s4[2] == {""})
MA_ENC = TM({("start", c): ("accept", c, 1) for c in GE})
sa = sets(MA_ENC, "01[]|", 5)
check("7.7(d) M1 and M_Accept both halt on every input (same Halt, same empty Diverge); M_Accept accepts every "
      "string, so it rejects no encoding, its own included", s1[0] | s1[1] == U and sa[0] == U and not s1[2] and not sa[2])

# ====================================================================== 7.8 both infinite: Rice does not apply
EVEN_ACC = TM({("even", "0"): ("odd", "0", 1), ("even", "1"): ("odd", "1", 1), ("even", B): ("accept", B, 1),
               ("odd", "0"): ("even", "0", 1), ("odd", "1"): ("even", "1", 1), ("odd", B): ("reject", B, 1)},
              start="even")
EVEN_LOOP = TM({("even", "0"): ("odd", "0", 1), ("even", "1"): ("odd", "1", 1), ("even", B): ("accept", B, 1),
                ("odd", "0"): ("even", "0", 1), ("odd", "1"): ("even", "1", 1), ("odd", B): ("odd", B, 1)},
               start="even")
ODD_REJ = TM({("even", "0"): ("odd", "0", 1), ("even", "1"): ("odd", "1", 1), ("even", B): ("even", B, 1),
              ("odd", "0"): ("even", "0", 1), ("odd", "1"): ("even", "1", 1), ("odd", B): ("reject", B, 1)},
             start="even")
ALL10 = set(strings("01", 10))
ev = {w for w in ALL10 if len(w) % 2 == 0}
od = ALL10 - ev
s_a, s_l, s_o = sets(EVEN_ACC, n=10), sets(EVEN_LOOP, n=10), sets(ODD_REJ, n=10)
check("7.8(a) P accepts the even-length strings and rejects the odd-length ones (both infinite: P in BothInf)",
      s_a[0] == ev and s_a[1] == od and not s_a[2])
check("7.8(a) P' accepts the even-length strings and runs forever on the odd-length ones (Reject empty)",
      s_l[0] == ev and not s_l[1] and s_l[2] == od)
check("7.8(a) P'' rejects the odd-length strings and runs forever on the even-length ones (Accept empty)",
      not s_o[0] and s_o[1] == od and s_o[2] == ev)
check("7.8(a) so Accept(P) = Accept(P') and Reject(P) = Reject(P''), with P in BothInf and P', P'' not",
      s_a[0] == s_l[0] and s_a[1] == s_o[1])

# ====================================================================== 7.1(c) concatenation by trying every split
PALTM = TM({("start", "0"): ("have0", B, 1), ("start", "1"): ("have1", B, 1), ("start", B): ("accept", B, 1),
            ("have0", "0"): ("have0", "0", 1), ("have0", "1"): ("have0", "1", 1), ("have0", B): ("last0", B, -1),
            ("have1", "0"): ("have1", "0", 1), ("have1", "1"): ("have1", "1", 1), ("have1", B): ("last1", B, -1),
            ("last0", "0"): ("back", B, -1), ("last0", B): ("accept", B, 1),
            ("last1", "1"): ("back", B, -1), ("last1", B): ("accept", B, 1),
            ("back", "0"): ("back", "0", -1), ("back", "1"): ("back", "1", -1), ("back", B): ("start", B, 1)})
dec1 = lambda x: PALTM.run(x)[0] == "accept"
dec2 = lambda y: len(y) % 2 == 0 and y == "0" * (len(y) // 2) + "1" * (len(y) // 2)
split_decider = lambda w: any(dec1(w[:i]) and dec2(w[i:]) for i in range(len(w) + 1))
L1 = [x for x in strings("01", 8) if x == x[::-1]]
L2 = ["0" * n + "1" * n for n in range(5)]
concat = {x + y for x in L1 for y in L2 if len(x + y) <= 8}
check("7.1(c) 'try all |w|+1 splits' decides PAL . {0^n1^n} on every |w| <= 8 (vs enumerating the pairs)",
      all(split_decider(w) == (w in concat) for w in strings("01", 8)))

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: {FAIL}")
sys.exit(1 if FAIL else 0)
