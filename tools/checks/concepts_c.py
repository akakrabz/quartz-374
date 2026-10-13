#!/usr/bin/env python3
"""Checks for the concrete examples on the concept pages of group C (Chapters 6-9):
turing-machines, universal-turing-machine, church-turing-thesis, acceptable-and-decidable,
diagonalization, rices-theorem, undecidability-reductions, nondeterministic-turing-machines,
cook-levin-theorem. (halting-problem has no concrete object to check.)"""
import itertools
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from automata import TM, strings  # noqa: E402
from automata.tm import BLANK as B  # noqa: E402

FAIL = []


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAIL.append(name)


# ---------------------------------------------------------------- turing-machines: a decider for 0^n 1^n
D = TM({("start", "0"): ("skip0", B, +1), ("start", B): ("accept", B, +1),
        ("skip0", "0"): ("skip0", "0", +1), ("skip0", "1"): ("skip1", "1", +1), ("skip0", B): ("erase1", B, -1),
        ("skip1", "1"): ("skip1", "1", +1), ("skip1", B): ("erase1", B, -1),
        ("erase1", "1"): ("back", B, -1),
        ("back", "0"): ("back", "0", -1), ("back", "1"): ("back", "1", -1), ("back", B): ("start", B, +1)})


def in_0n1n(w):
    k = len(w) // 2
    return len(w) % 2 == 0 and w == "0" * k + "1" * k


runs = {w: D.run(w) for w in strings("01", 14)}
check("0^n1^n decider: 11 transitions, as in the table", len(D.delta) == 11)
check("halts on every input of length <= 14 (never crashes, never times out)",
      all(r[0] in ("accept", "reject") for r in runs.values()),
      str({r[0] for r in runs.values()}))
check("accepts exactly {0^n 1^n}, |w| <= 14", all((r[0] == "accept") == in_0n1n(w) for w, r in runs.items()))
check("near-miss 0110 rejected", D.run("0110")[0] == "reject")
check("on 0011: accepts after 15 steps", D.run("0011")[:2] == ("accept", 15), str(D.run("0011")[:2]))
out, steps, tape, head, confs = D.run("0101", trace=True)
q_before, t_before, h_before = confs[-2]
check("on 0101: rejects when skip1 reads a 0",
      out == "reject" and q_before == "skip1" and (t_before + B * 20)[h_before] == "0", str(confs[-2]))
ok_passes = True
for k in range(0, 31):
    out, steps, tape, head, confs = D.run("0" * k + "1" * k, trace=True)
    starts = [i for i, c in enumerate(confs) if c[0] == "start"]
    lens = [b - a for a, b in zip(starts, starts[1:])]
    if not (out == "accept" and len(lens) == k and all(L <= 4 * k + 1 for L in lens)
            and steps == 2 * k * k + 3 * k + 1):
        ok_passes = False
        print("   k =", k, out, steps, lens)
check("on 0^k1^k (k <= 30): k passes of at most 4k+1 steps; 2k^2+3k+1 steps in all (O(n^2))", ok_passes)
check("back never moves off cell 0: no crash on any input of length <= 14",
      all(r[0] != "crash" for r in runs.values()))

# ---------------------------------------------------------------- universal-turing-machine: encoding + a string-level U
DOT = "•"


def enc_string(w, sym):
    return "[" + DOT.join(sym[c] for c in w) + "]"


def enc_machine(tm, sym, st):
    blocks = "".join(f"[{st[p]}{DOT}{sym[a]}|{st[q]}{DOT}{sym[b]}{DOT}{'1' if d == 1 else '0'}]"
                     for (p, a), (q, b, d) in tm.delta.items() if q != tm.reject)
    return f"[{st[tm.reject]}{DOT}{sym[B]}]" + "[" + blocks + "]"


def initial_config(w, sym, st):
    # the book's recipe: '[' -> '[[<start>.', '.' -> '][<reject>.', ']' -> ']]'
    e = enc_string(w, sym)
    out = ""
    for c in e:
        out += {"[": "[[" + st["start"] + DOT, DOT: "][" + st["reject"] + DOT, "]": "]]"}.get(c, c)
    return out


def U(machine_code, config, accept_code, max_steps=10000):
    """Simulate an encoded machine on an encoded configuration, as in Section 6.8. Returns (outcome, steps)."""
    head_part, table = machine_code.split("][", 1)          # '[R.B' and '[blocks]]'
    R, Bc = head_part[1:].split(DOT)
    blocks = table[1:-2].split("][")                        # strip the outer '[' ... ']]'
    blocks[0] = blocks[0].lstrip("[")
    lookup = {}
    for blk in blocks:
        left, right = blk.split("|")
        q, b, d = right.split(DOT)
        lookup[left] = (q, b, d)
    cells = [tuple(c.split(DOT)) for c in config[2:-2].split("][")]
    for step in range(1, max_steps + 1):
        h = next(i for i, (q, a) in enumerate(cells) if q != R)
        q, a = cells[h]
        key = q + DOT + a
        if key not in lookup:
            return "reject", step
        q2, b, d = lookup[key]
        if q2 == accept_code:
            return "accept", step
        cells[h] = (R, b)
        h2 = h + (1 if d == "1" else -1)
        if h2 < 0:
            return "crash", step
        if h2 == len(cells):
            cells.append((R, Bc))
        cells[h2] = (q2, cells[h2][1])
    return "timeout", max_steps


# the page's example: accept iff the input begins with 1
M1 = TM({("start", "1"): ("accept", "1", +1)})
sym2 = {B: "00", "0": "01", "1": "10"}
st2 = {"start": "11", "accept": "01", "reject": "00"}
check("example codes follow the conventions: start = 1...1, reject = 0...0, accept = 0...01 (2 bits for 3 states)",
      st2["start"] == "11" and st2["reject"] == "00" and st2["accept"] == "01" and (3 - 1).bit_length() == 2)
code = enc_machine(M1, sym2, st2)
check("<M> = [00•00][[11•10|01•10•1]]", code == "[00•00][[11•10|01•10•1]]", code)
check("<10> = [10•01]", enc_string("10", sym2) == "[10•01]")
c10, c01 = initial_config("10", sym2, st2), initial_config("01", sym2, st2)
check("initial configuration on 10 is [[11•10][00•01]]", c10 == "[[11•10][00•01]]", c10)
check("initial configuration on 01 is [[11•01][00•10]]", c01 == "[[11•01][00•10]]", c01)
check("U accepts <M,10> after one simulated step", U(code, c10, "01") == ("accept", 1), str(U(code, c10, "01")))
check("U rejects <M,01> (no block begins 11•01)", U(code, c01, "01")[0] == "reject" and "[11•01|" not in code)
check("U agrees with M on every non-empty input of length <= 8",
      all(U(code, initial_config(w, sym2, st2), "01")[0] == M1.run(w)[0] for w in strings("01", 8, 1)))
# cross-check the encoder and U on the 0^n1^n decider (7 states -> 3 bits)
st3 = {"start": "111", "reject": "000", "accept": "110", "skip0": "001", "skip1": "010", "erase1": "011",
       "back": "100"}
codeD = enc_machine(D, sym2, st3)
check("U agrees with the 0^n1^n decider on every non-empty input of length <= 8",
      all(U(codeD, initial_config(w, sym2, st3), "110")[0] == D.run(w)[0] for w in strings("01", 8, 1)))
MDiv = TM({("start", a): ("start", a, +1) for a in "01" + B})
codeDiv = enc_machine(MDiv, sym2, st2)
check("U runs forever when M does (M_Diverge: no halt within 2000 simulated steps)",
      U(codeDiv, initial_config("01", sym2, st2), "01", 2000)[0] == "timeout")

# ---------------------------------------------------------------- church-turing-thesis: dovetailing
ALL = list(strings("01", 9))                                 # length-lexicographic order: eps, 0, 1, 00, ...
check("strings() lists eps, 0, 1, 00, 01 first (length-lexicographic)", ALL[:5] == ["", "0", "1", "00", "01"])


def dovetail(machine, rounds):
    for k in range(1, rounds + 1):
        for j in range(1, k + 1):
            outcome, s = machine[j - 1]
            if outcome == "accept" and s <= k:
                return k
    return None


rng = random.Random(374)
ok_bound, ok_never = True, True
ROUNDS = 100
for trial in range(400):
    machine = []                      # behavior on the first ROUNDS strings: (outcome, steps)
    for j in range(ROUNDS):
        u = rng.random()
        machine.append(("accept", rng.randint(1, 120)) if u < 0.03 else
                       ("reject", rng.randint(1, 120)) if u < 0.5 else ("diverge", None))
    acc = [(j + 1, s) for j, (o, s) in enumerate(machine) if o == "accept"]
    got = dovetail(machine, ROUNDS)
    reachable = [max(j, s) for j, s in acc if max(j, s) <= ROUNDS]
    if reachable:
        # first accepting round is exactly min over accepted strings of max{j, s}, hence <= max{j, s} for each
        if got != min(reachable):
            ok_bound = False
    elif got is not None:
        ok_never = False
check("dovetailing accepts by round max{j, s} for every accepted j-th string (400 random toy machines)", ok_bound)
check("dovetailing never accepts when no string is accepted", ok_never)
toy = [("diverge", None), ("accept", 3)]
check("running one string at a time to completion gets stuck: toy machine diverges on string 1, accepts string 2",
      toy[0][0] == "diverge" and dovetail(toy, 10) == 3)

# ---------------------------------------------------------------- acceptable-and-decidable: the table is consistent
T = {  # name: (acceptable, decidable, complement)
    "Accept": (True, False, "coAccept"), "coAccept": (False, False, "Accept"),
    "Halt": (True, False, "Diverge"), "Diverge": (False, False, "Halt"),
    "SelfAccept": (True, False, "coSelfAccept"), "coSelfAccept": (False, False, "SelfAccept"),
    "SelfReject": (True, False, "coSelfReject"), "coSelfReject": (False, False, "SelfReject"),
    "SelfHalt": (True, False, "SelfDiverge"), "SelfDiverge": (False, False, "SelfHalt"),
    "NeverAccept": (False, False, "coNeverAccept"), "coNeverAccept": (True, False, "NeverAccept"),
    "ThisIsSparta": (True, True, "coThisIsSparta"), "coThisIsSparta": (True, True, "ThisIsSparta"),
}
check("table: decidable implies acceptable", all(a or not d for a, d, _ in T.values()))
check("table: decidable languages are closed under complement", all(T[c][1] == d for a, d, c in T.values()))
check("table: Lemma 5 — acceptable and co-acceptable iff decidable",
      all((a and T[c][0]) == d for a, d, c in T.values()))
check("table: Lemma 4 — SelfHalt = SelfAccept ∪ SelfReject is acceptable",
      T["SelfAccept"][0] and T["SelfReject"][0] and T["SelfHalt"][0])

# ---------------------------------------------------------------- diagonalization: Cantor on all f: X -> 2^X, |X| = 3
X = [0, 1, 2]
subsets = [frozenset(c) for r in range(4) for c in itertools.combinations(X, r)]
ok = True
for img in itertools.product(subsets, repeat=3):
    Y = frozenset(x for x in X if x not in img[x])
    if any(Y == img[y] for y in X) or not all((y in Y) != (y in img[y]) for y in X):
        ok = False
check("Cantor: for all 512 functions f: X -> 2^X (|X| = 3), the sad set differs from each f(y) at y", ok)

# ---------------------------------------------------------------- rices-theorem: the witness machines
MAcc = TM({("start", a): ("accept", a, +1) for a in "01" + B})
MRej = TM({("start", a): ("reject", a, +1) for a in "01" + B})
W8 = list(strings("01", 8))
check("M_Accept accepts every input (|w| <= 8)", all(MAcc.run(w)[0] == "accept" for w in W8))
check("M_Reject rejects every input (|w| <= 8)", all(MRej.run(w)[0] == "reject" for w in W8))
check("M_Diverge never enters accept or reject, so it halts on nothing",
      all(q not in ("accept", "reject") for (q, b, d) in MDiv.delta.values()) and
      all(MDiv.run(w, 2000)[0] == "timeout" for w in W8))
check("M_Reject and M_Diverge accept the same language (empty) but only M_Reject halts everywhere",
      all(MRej.run(w)[0] != "accept" and MDiv.run(w, 2000)[0] != "accept" for w in W8))

# ---------------------------------------------------------------- undecidability-reductions: the input as a step budget
def m_prime(M, w):
    return lambda x: M.run(w, max_steps=len(x))[0] in ("accept", "reject")


s0011 = D.run("0011")[1]
Mp = m_prime(D, "0011")
check("M halts on w after s = 15 steps -> Accept(M') = {x : |x| >= 15} (all x, |x| <= 18)",
      s0011 == 15 and all(Mp(x) == (len(x) >= 15) for x in strings("01", 18)))
Mp_div = m_prime(MDiv, "0011")
check("M never halts on w -> Accept(M') is empty (|x| <= 14)", not any(Mp_div(x) for x in strings("01", 14)))

# ---------------------------------------------------------------- nondeterministic-turing-machines: composite by guessing a divisor
def composite(n):
    return n >= 4 and any(n % p == 0 for p in range(2, int(n ** 0.5) + 1))


check("1^n composite iff some d with 2 <= d <= n-1 divides n (n < 500)",
      all(composite(n) == any(n % d == 0 for d in range(2, n)) for n in range(500)))

# ---------------------------------------------------------------- cook-levin-theorem: the two formulas
def sat(clauses):
    return [(a, b) for a, b in itertools.product([True, False], repeat=2) if all(c(a, b) for c in clauses)]


phi = [lambda a, b: a or b, lambda a, b: (not a) or (not b), lambda a, b: a or (not b)]
check("(a ∨ b) ∧ (¬a ∨ ¬b) ∧ (a ∨ ¬b): the only satisfying assignment is a = True, b = False",
      sat(phi) == [(True, False)], str(sat(phi)))
check("adding (¬a ∨ b) makes it unsatisfiable", sat(phi + [lambda a, b: (not a) or b]) == [])

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: {FAIL}")
sys.exit(1 if FAIL else 0)
