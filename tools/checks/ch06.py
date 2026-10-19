#!/usr/bin/env python3
"""Checks for every concrete claim on content/1-models-of-computation/06-turing-machines.md."""
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from automata import TM, strings  # noqa: E402

FAIL = []


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAIL.append(name)


B = "□"
R, L, S = +1, -1, 0


def rows(spec):
    """Transition table from rows (state, symbols read, next state, symbol written or None = unchanged, move)."""
    d = {}
    for p, syms, q, b, mv in spec:
        for a in syms:
            assert (p, a) not in d, (p, a)
            d[(p, a)] = (q, a if b is None else b, mv)
    return d


def in_L(w):
    """{0^n 1^n 0^n : n >= 0}"""
    n = len(w) // 3
    return len(w) % 3 == 0 and w == "0" * n + "1" * n + "0" * n


def show(conf):
    q, t, i = conf
    t = t + B * max(0, i + 1 - len(t))
    return f"{q}: {t[:i]}[{t[i]}]{t[i + 1:]}"


# ---------------------------------------------------------------- 6.3 our machine for {0^n 1^n 0^n}
ZOZ_SPEC = [
    ("start", "0", "block1", "#", R),
    ("start", B, "accept", None, R),
    ("block1", "0", "block1", None, R),
    ("block1", "1", "block2", None, R),
    ("block2", "1", "block2", None, R),
    ("block2", "0", "block3", None, R),
    ("block3", "0", "block3", None, R),
    ("block3", B, "rewind", None, L),
    ("rewind", "01", "rewind", None, L),
    ("rewind", "#", "seek1", None, R),
    ("seek1", "0x", "seek1", None, R),
    ("seek1", "1", "seek0", "x", R),
    ("seek0", "1x", "seek0", None, R),
    ("seek0", "0", "reset", "x", L),
    ("reset", "01x", "reset", None, L),
    ("reset", "#", "mark0", None, R),
    ("mark0", "0", "seek1", "#", R),
    ("mark0", "x", "verify", None, R),
    ("verify", "x", "verify", None, R),
    ("verify", B, "accept", None, R),
]
ZOZ = rows(ZOZ_SPEC)
M = TM(ZOZ)
check("table has 20 rows (as printed, with 'read 0,1 / unchanged' rows merged) and 25 transitions",
      len(ZOZ_SPEC) == 20 and len(ZOZ) == 25, f"{len(ZOZ_SPEC)} rows, {len(ZOZ)} transitions")
states = {p for p, _ in ZOZ} | {q for q, _, _ in ZOZ.values()}
check("10 working states + accept (+ reject for missing transitions)", len(states - {"accept"}) == 10,
      str(sorted(states)))
check("tape alphabet {0, 1, #, x, □}", {a for _, a in ZOZ} | {b for _, b, _ in ZOZ.values()} == set("01#x" + B))

N = 14
bad, outcomes, maxsteps = [], set(), {}
for w in strings("01", N):
    out, steps, tape, head = M.run(w)
    outcomes.add(out)
    maxsteps[len(w)] = max(maxsteps.get(len(w), 0), steps)
    if (out == "accept") != in_L(w) or out not in ("accept", "reject"):
        bad.append((w, out))
check(f"our machine decides L: accepts exactly L and halts (never crashes) on all {2 ** (N + 1) - 1} inputs, |w| <= {N}",
      not bad, str(bad[:5]))
check("quadratic running time: at most n^2 + 3n + 2 steps on every input of length n <= 14",
      all(maxsteps[n] <= n * n + 3 * n + 2 for n in maxsteps), str(maxsteps))

# missing transitions reject: each one is used by some rejected input
used_missing = set()
for w in strings("01", 10):
    out, steps, tape, head, confs = M.run(w, trace=True)
    if out == "reject":
        q, t, i = confs[-2]
        t = t + B * (i + 1 - len(t))
        used_missing.add((q, t[i]))
check("rejections happen at: start/1, block1/□, block2/□, block3/1, seek1/□, seek0/□, verify/0, verify/1",
      used_missing == {("start", "1"), ("block1", B), ("block2", B), ("block3", "1"), ("seek1", B),
                       ("seek0", B), ("verify", "0"), ("verify", "1")}, str(sorted(used_missing)))

# trace on 010
out, steps, tape, head, confs = M.run("010", trace=True)
expected = [("start", "010", 0), ("block1", "#10", 1), ("block2", "#10", 2), ("block3", "#10", 3),
            ("rewind", "#10", 2), ("rewind", "#10", 1), ("rewind", "#10", 0), ("seek1", "#10", 1),
            ("seek0", "#x0", 2), ("reset", "#xx", 1), ("reset", "#xx", 0), ("mark0", "#xx", 1),
            ("verify", "#xx", 2), ("verify", "#xx", 3), ("accept", "#xx", 4)]
check("trace on 010: the 15 configurations in the table, accept after 14 steps",
      out == "accept" and steps == 14 and confs == expected, " | ".join(show(c) for c in confs))

# 0010: format OK, round 1 succeeds, round 2 finds no unmarked 1
out, steps, tape, head, confs = M.run("0010", trace=True)
check("0010: round 2 marks the second 0, then seek1 reads □ and rejects (tape ##xx)",
      out == "reject" and confs[-2][0] == "seek1" and confs[-2][2] == 4 and confs[-2][1] == "##xx",
      show(confs[-2]))
# 0110: verify finds an unmarked 1
out, steps, tape, head, confs = M.run("0110", trace=True)
check("0110: verify reads an unmarked 1 and rejects", out == "reject" and confs[-2][0] == "verify"
      and (confs[-2][1] + B * 9)[confs[-2][2]] == "1", show(confs[-2]))
# 0101: format check fails in block3
out, steps, tape, head, confs = M.run("0101", trace=True)
check("0101: block3 reads 1 and rejects", out == "reject" and confs[-2][0] == "block3", show(confs[-2]))

# the configuration of the tape figure occurs in the run on 001100
out, steps, tape, head, confs = M.run("001100", trace=True)
check("run on 001100 passes through (reset, #0x1x0, 3) and accepts", ("reset", "#0x1x0", 3) in confs
      and out == "accept", f"{steps} steps")
check("001100 is accepted after 35 steps", steps == 35, str(steps))
fs = {k: M.run("0" * k + "1" * k + "0" * k)[1] for k in range(1, 12)}
check("on 0^k1^k0^k the machine takes 4k^2 + 9k + 1 steps (k = 1..11)",
      all(fs[k] == 4 * k * k + 9 * k + 1 for k in fs), str(fs))

# L is not regular: fooling set 0* with z = 1^i 0^i
check("fooling set 0* for L: z = 1^i0^i distinguishes 0^i and 0^j (i != j <= 9)",
      all(in_L("0" * i + "1" * i + "0" * i) and not in_L("0" * j + "1" * i + "0" * i)
          for i in range(10) for j in range(10) if i != j))

# ---------------------------------------------------------------- 6.3 the book's machine
BOOK = rows([
    ("start", "0", "seek1", "$", R),
    ("start", "x", "verify", "$", R),
    ("seek1", "0x", "seek1", None, R),
    ("seek1", "1", "seek0", "x", R),
    ("seek0", "1x", "seek0", None, R),
    ("seek0", "0", "reset", "x", L),  # the intended left move (the printed table has +1 here)
    ("reset", "01x", "reset", None, L),
    ("reset", "$", "start", None, R),
    ("verify", "x", "verify", "$", R),
    ("verify", B, "accept", None, L),
])
MB = TM(BOOK)
check("book's machine accepts 001010 (not in L)", MB.run("001010")[0] == "accept" and not in_L("001010"))
check("book's machine rejects the empty string (start has no transition on □)",
      MB.run("")[0] == "reject" and ("start", B) not in BOOK and in_L(""))
extra = [w for w in strings("01", 12) if MB.accepts(w) and not in_L(w)]
check("book's machine accepts 18 strings outside L of length <= 12", len(extra) == 18, ", ".join(extra))
check("book's machine accepts every non-empty string of L of length <= 12",
      all(MB.accepts(w) for w in strings("01", 12) if in_L(w) and w))
check("book's machine halts (never crashes) on every input of length <= 12",
      all(MB.run(w)[0] in ("accept", "reject") for w in strings("01", 12)))
check("book's machine accepts 001100 and rejects 00100 (the two traces in the text)",
      MB.accepts("001100") and MB.run("00100")[0] == "reject")
BOOK_PRINTED = dict(BOOK)
BOOK_PRINTED[("seek0", "0")] = ("reset", "x", R)
check("(report only) with the printed +1 the machine rejects 010, which is in L",
      TM(BOOK_PRINTED).run("010")[0] == "reject")

# ---------------------------------------------------------------- 6.4 removing stay-put moves


def stays_used(delta, confs):
    n = 0
    for q, t, i in confs[:-1]:
        a = (t + B * (i + 1 - len(t)))[i]
        if (q, a) in delta and delta[(q, a)][2] == 0:
            n += 1
    return n


def remove_stay(delta, gamma):
    """The book's construction: states Q x {0,1}."""
    Q = {p for p, _ in delta} | {q for q, _, _ in delta.values()} | {"accept", "reject"}
    d = {}
    for (p, a), (q, b, mv) in delta.items():
        d[((p, 0), a)] = ((q, 1), b, +1) if mv == 0 else ((q, 0), b, mv)
    for p in Q:
        for a in gamma:
            d[((p, 1), a)] = ((p, 0), a, -1)
    return d


def compare(delta, gamma, inputs, start="start", limit=400):
    Ms = TM(delta, start=start)
    Mp = TM(remove_stay(delta, gamma), start=(start, 0), accept=("accept", 0), reject=("reject", 0))
    for w in inputs:
        o1, s1, t1, h1, c1 = Ms.run(w, max_steps=limit, trace=True)
        o2, s2, t2, h2 = Mp.run(w, max_steps=2 * limit)
        if o1 == "timeout":
            if o2 in ("accept", "reject", "crash") and s2 <= limit:
                return w, (o1, o2)
            continue
        k = stays_used(delta, c1)
        if (o1, t1) != (o2, t2) or s2 != s1 + k or (o1 != "crash" and h1 != h2):
            return w, (o1, s1, t1, h1, k, o2, s2, t2, h2)
    return None


ZOZ_STAY = dict(ZOZ)
ZOZ_STAY[("start", B)] = ("accept", B, S)
ZOZ_STAY[("verify", B)] = ("accept", B, S)
ZOZ_STAY[("mark0", "x")] = ("verify", "x", S)
check("stay-put variant (start/□ and verify/□ stay put into accept; mark0 hands x to verify in place) decides L",
      all((TM(ZOZ_STAY).run(w)[0] == "accept") == in_L(w) for w in strings("01", 12)))
GAM = "01#x" + B
conv = remove_stay(ZOZ_STAY, GAM)
check("converted machine has 2 x 12 = 24 states", len({p for p, _ in conv} | {q for q, _, _ in conv.values()}
                                                       | {("accept", 0), ("reject", 0)}) == 24)
check("converted machine has no stay-put moves", all(mv != 0 for _, _, mv in conv.values()))
check("stay-put variant vs converted machine: same outcome, tape and head; steps' = steps + #stay moves (|w| <= 12)",
      compare(ZOZ_STAY, GAM, strings("01", 12)) is None)
random.seed(374)
bad = None
for trial in range(300):
    Qs = ["start", "p", "q"]
    d = {}
    for p in Qs:
        for a in "01" + B:
            if random.random() < 0.85:
                d[(p, a)] = (random.choice(Qs + ["accept", "reject"]), random.choice("01" + B), random.choice([L, S, R]))
    r = compare(d, "01" + B, strings("01", 6), limit=300)
    if r:
        bad = (trial, r)
        break
check("the same holds for 300 random 3-state stay-put machines on all inputs of length <= 6", bad is None, str(bad))

# ---------------------------------------------------------------- 6.5 shifting
SHIFT = {("hold0", "0"): ("hold0", "0", R), ("hold0", "1"): ("hold1", "0", R), ("hold0", B): ("halt", "0", R),
         ("hold1", "0"): ("hold0", "1", R), ("hold1", "1"): ("hold1", "1", R), ("hold1", B): ("halt", "1", R)}
SH = TM(SHIFT, start="hold0", halt="halt")
check("shift machine: M(w) = 0w in |w| + 1 steps for every w, |w| <= 12",
      all(SH.run(w) [0] == "halt" and SH.run(w)[2] == "0" + w and SH.run(w)[1] == len(w) + 1
          for w in strings("01", 12)))
out, steps, tape, head, confs = SH.run("101", trace=True)
check("shift trace on 101", confs == [("hold0", "101", 0), ("hold1", "001", 1), ("hold0", "011", 2),
                                     ("hold1", "010", 3), ("halt", "0101", 4)] and tape == "0101",
      " | ".join(show(c) for c in confs))

SHIFT2 = {}
for p in ("00", "01", "10", "11"):          # state = the two symbols still to be written, oldest first
    for a in "01":
        SHIFT2[("h" + p, a)] = ("h" + p[1] + a, p[0], R)
    SHIFT2[("h" + p, B)] = ("e" + p[1], p[0], R)
for c in "01":
    SHIFT2[("e" + c, B)] = ("halt", c, R)
S2 = TM(SHIFT2, start="h00", halt="halt")
check("remembering the last 2 symbols shifts by 2: w -> 00w for every w, |w| <= 10",
      all(S2.run(w)[:3:2] == ("halt", "00" + w) for w in strings("01", 10)))

# ---------------------------------------------------------------- 6.5 increment = shift + carry
INC = dict(SHIFT)
INC[("hold0", B)] = ("halt", "1", R)
INC[("hold1", B)] = ("carry", "0", L)
INC[("carry", "1")] = ("carry", "0", L)
INC[("carry", "0")] = ("halt", "1", R)
check("increment machine: 8 transitions", len(INC) == 8)
IN = TM(INC, start="hold0", halt="halt")


def inc_spec(w):
    v = int(w, 2) if w else 0
    return format(v + 1, f"0{len(w) + 1}b")


bad = [w for w in strings("01", 12) if IN.run(w)[:1] != ("halt",) or IN.run(w)[2] != inc_spec(w)]
check("increment machine: M(w) = val(w)+1 in binary with |w|+1 bits, for every w, |w| <= 12", not bad, str(bad[:5]))
check("examples: 1011 -> 01100, 111 -> 1000, ε -> 1",
      IN.run("1011")[2] == "01100" and IN.run("111")[2] == "1000" and IN.run("")[2] == "1")
check("increment never moves left of cell 0 (the shifted-in 0 stops the carry)",
      all(IN.run(w)[0] != "crash" for w in strings("01", 12)))

# ---------------------------------------------------------------- 6.8 encodings and the universal machine
SYM = {B: "000", "0": "001", "1": "010", "#": "011", "x": "100"}
STATE = {"start": "1111", "reject": "0000", "accept": "0001", "block1": "0010", "block2": "0011",
         "block3": "0100", "rewind": "0101", "seek1": "0110", "seek0": "0111", "reset": "1000",
         "mark0": "1001", "verify": "1010"}
check("|Γ| = 5 needs 3-bit symbol codes, |Q| = 12 needs 4-bit state codes",
      (5 - 1).bit_length() == 3 and (12 - 1).bit_length() == 4 and set(STATE) == states | {"reject"})
check("start = 1111 and reject = 0000; codes distinct", STATE["start"] == "1111" and STATE["reject"] == "0000"
      and len(set(STATE.values())) == 12 and len(set(SYM.values())) == 5)
check("accept = 0001 follows the site's convention 0...01 (needed by U; the book fixes no accept code)",
      STATE["accept"] == "0" * 3 + "1")
MOVE = {-1: "0", +1: "1"}


def block(p, a, q, b, mv):
    return f"[{STATE[p]}•{SYM[a]}|{STATE[q]}•{SYM[b]}•{MOVE[mv]}]"


ENC_DELTA = "[" + "".join(block(p, a, q, b, mv) for (p, a), (q, b, mv) in ZOZ.items() if q != "reject") + "]"
ENC_M = f"[{STATE['reject']}•{SYM[B]}]" + ENC_DELTA
check("block for δ(seek1, 1) = (seek0, x, +1) is [0110•010|0111•100•1]",
      block("seek1", "1", "seek0", "x", R) == "[0110•010|0111•100•1]" and "[0110•010|0111•100•1]" in ENC_M)
check("<M> starts with [0000•000][[ and ends with ]]; [[ and ]] occur once",
      ENC_M.startswith("[0000•000][[") and ENC_M.endswith("]]") and ENC_M.count("[[") == 1 and ENC_M.count("]]") == 1)
check("<δ> has 25 blocks, one per transition of the table", ENC_DELTA.count("|") == 25)
check("every block has the same length (4+3+4+3+1 bits and 6 punctuation marks = 21 symbols)",
      all(len(block(p, a, q, b, mv)) == 21 for (p, a), (q, b, mv) in ZOZ.items()))


def enc_word(w):
    return "[" + "•".join(SYM[a] for a in w) + "]"


check("<010> = [001•010•001]", enc_word("010") == "[001•010•001]")


def enc_conf(q, tape, i):
    t = tape + B * max(0, i + 1 - len(tape))
    return "[" + "".join(f"[{STATE[q] if k == i else STATE['reject']}•{SYM[a]}]" for k, a in enumerate(t)) + "]"


CONF = "[[0000•011][0000•001][0000•100][1000•010][0000•100][0000•001]]"
check("encoded configuration (reset, #0x1x0, 3) as printed", enc_conf("reset", "#0x1x0", 3) == CONF)


def U(enc_m, w, max_steps=5000):
    """String-level universal simulation: the configuration is a list of cell strings '[q•a]'."""
    rej, blank = enc_m[1:5], enc_m[6:9]
    start, acc = "1" * len(rej), rej[:-1] + "1"                     # the conventions 1...1 and 0...01
    delta = enc_m[10:]
    cells = [f"[{rej}•{SYM[a]}]" for a in w] or [f"[{rej}•{blank}]"]
    cells[0] = f"[{start}•{cells[0][6:9]}]"
    for _ in range(max_steps):
        i = next(k for k, c in enumerate(cells) if c[1:5] != rej)    # find the head cell
        key = "[" + cells[i][1:9] + "|"                                # left half of a block
        j = delta.find(key)
        if j < 0:
            return "reject", cells
        q, b, mv = delta[j + 10:j + 14], delta[j + 15:j + 18], delta[j + 19]
        cells[i] = f"[{q}•{b}]"
        if q == acc:
            return "accept", cells
        cells[i] = f"[{rej}•{b}]"
        k = i + (1 if mv == "1" else -1)
        if k < 0:
            return "crash", cells
        if k == len(cells):
            cells.append(f"[{rej}•{blank}]")                         # extend with an encoded blank
        cells[k] = f"[{q}•{cells[k][6:9]}]"
    return "timeout", cells


inv = {v: k for k, v in SYM.items()}
bad = []
for w in strings("01", 9):
    o1, s1, t1, h1 = M.run(w)
    o2, cells = U(ENC_M, w)
    t2 = "".join(inv[c[6:9]] for c in cells).rstrip(B)
    if (o1, t1) != (o2, t2):
        bad.append((w, o1, t1, o2, t2))
check("string-level U run on <M, w> agrees with M (outcome and final tape) for every w, |w| <= 9", not bad, str(bad[:3]))

# a machine that crashes on inputs starting with 0 and accepts those starting with 1: U gives no answer on a crash
CRASHER = {("start", "0"): ("start", "0", L), ("start", "1"): ("accept", "1", R)}
ENC_CR = f"[{STATE['reject']}•{SYM[B]}]" + "[" + "".join(block(p, a, q, b, mv)
                                                          for (p, a), (q, b, mv) in CRASHER.items()) + "]"
check("when M crashes, U neither accepts nor rejects (here: it stops without an answer); otherwise it agrees",
      all((TM(CRASHER).run(w)[0], U(ENC_CR, w)[0]) in {("crash", "crash"), ("accept", "accept"), ("reject", "reject")}
          for w in strings("01", 6, 1)) and U(ENC_CR, "01")[0] == "crash")

# the book's own example (Section 6.8): its table of codes and three of its printed blocks
BOOK_SYM = {"0": "001", "1": "010", "$": "011", "x": "100", B: "000"}
BOOK_ST = {"start": "111", "seek1": "010", "seek0": "011", "reset": "100", "verify": "101", "accept": "110",
           "reject": "000"}
PRINTED = {("start", "0", "seek1", "$", R): "[001•001|010•011•1]",
           ("start", "x", "verify", "$", R): "[001•100|101•011•1]",
           ("reset", "$", "start", "$", R): "[100•011|001•011•1]"}


def book_block(p, a, q, b, mv):
    return f"[{BOOK_ST[p]}•{BOOK_SYM[a]}|{BOOK_ST[q]}•{BOOK_SYM[b]}•{MOVE[mv]}]"


check("(book typo) the book's printed blocks write start as 001, a code its table gives to no state; "
      "with start = 111 from its table they are otherwise identical",
      "001" not in BOOK_ST.values() and BOOK_ST["start"] == "111"
      and all(book_block(*t) == s.replace("001•", "111•", 1) if t[0] == "start" else
              book_block(*t) == s.replace("|001•", "|111•")
              for t, s in PRINTED.items())
      and all(book_block(*t) != s for t, s in PRINTED.items()))

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: {FAIL}")
sys.exit(1 if FAIL else 0)
