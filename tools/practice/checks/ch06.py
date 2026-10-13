#!/usr/bin/env python3
"""Checks for every concrete claim on content/practice/06-turing-machines.md.

Brute-force predicates are written from the problem statements, independently of the machines.
One-tape machines run on tools/automata's TM (missing transitions reject, a left move from cell 0
crashes); a small k-tape simulator, a two-way-infinite-tape simulator and the constructions behind
the true-or-false reasons (right-only machines are DFAs, stay-put removal, folding a two-way tape)
are implemented here and tested on random machines."""
import os
import random
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from automata import TM, DFA, strings  # noqa: E402

FAIL = []
B = "□"


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAIL.append(name)


def outcome(M, w, limit=20000):
    """accept / reject / crash / halt, or 'loop' when a configuration repeats (a proof of divergence),
    or 'timeout'."""
    tape, q, h, seen = list(w), M.start, 0, set()
    for _ in range(limit):
        if q in (M.accept, M.reject) or q == M.halt:
            return {M.accept: "accept", M.reject: "reject"}.get(q, "halt")
        last = len(tape) - 1
        while last >= 0 and tape[last] == B:
            last -= 1
        key = (q, h, tuple(tape[:last + 1]))
        if key in seen:
            return "loop"
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
    return "timeout"


def runs_right_forever(M, w, state, limit=400):
    """True if the run reaches `state` on a blank beyond all non-blank cells and delta(state, blank)
    = (state, blank, +1): from then on it reads only blanks and moves right forever."""
    out, steps, tape, head, confs = M.run(w, max_steps=limit, trace=True)
    for q, x, i in confs:
        if q == state and i >= len(x) and M.delta.get((q, B)) == (state, B, 1):
            return True
    return False


# ====================================================================== 6.2 the four outcomes
T = TM({("start", "0"): ("look", "1", 1), ("start", "1"): ("look", "1", -1),
        ("look", "0"): ("look", "0", -1), ("look", "1"): ("start", "1", 1), ("look", B): ("accept", "1", -1)})
out, steps, tape, head, confs = T.run("000", trace=True)
exp = [("start", "000", 0), ("look", "100", 1), ("look", "100", 0), ("start", "100", 1), ("look", "110", 2),
       ("look", "110", 1), ("start", "110", 2), ("look", "111", 3), ("accept", "1111", 2)]
check("6.2(a) run on 000: the nine configurations of the solution, accept after 8 steps",
      out == "accept" and steps == 8 and confs == exp, str(confs))
out, steps, tape, head, confs = T.run("", trace=True)
check("6.2(b) epsilon: start reads blank, no transition: reject after 1 step", out == "reject" and steps == 1)
out, steps, tape, head = T.run("1")
check("6.2(b) 1: start reads 1 at cell 0 and moves left: crash after 1 step", out == "crash" and steps == 1)
out, steps, tape, head, confs = T.run("01", trace=True)
check("6.2(b) 01: (start,01,0) => (look,11,1) => (start,11,2) => reject",
      out == "reject" and steps == 3 and confs[:3] == [("start", "01", 0), ("look", "11", 1), ("start", "11", 2)],
      str(confs))
out, steps, tape, head, confs = T.run("011", max_steps=50, trace=True)
check("6.2(b) 011: (start,011,0) => (look,111,1) => (start,111,2) => (look,111,1) repeats: runs forever",
      confs[:4] == [("start", "011", 0), ("look", "111", 1), ("start", "111", 2), ("look", "111", 1)]
      and out == "timeout", str(confs[:5]))
# going further: the complete classification, regular expressions from the solution
RX = {"accept": r"(0|01)*0", "reject": r"(0|01)*01|", "crash": r"1[01]*", "loop": r"(0|01)*011[01]*"}
bad = []
for w in strings("01", 12):
    kinds = [k for k, rx in RX.items() if re.fullmatch(rx, w)]
    o = outcome(T, w, 3000)
    if kinds != [o]:
        bad.append((w, o, kinds))
check("6.2 going further: Accept = (0+01)*0, Reject = eps+(0+01)*01, crash = 1(0+1)*, loop = (0+01)*011(0+1)* "
      "(a partition; every run on |w| <= 12)", not bad, str(bad[:4]))
check("6.2(c) M accepts 000 and 010 (so Accept(M) is not just 0+)",
      T.accepts("000") and T.accepts("010"))

# ====================================================================== 6.3 find the error, #0 = #1
def eq_delta(slip):
    d = {("start", "0"): ("seek1", "⊢", 1), ("start", "1"): ("seek0", "⊢", 1), ("start", B): ("accept", B, 1),
         ("seek1", "0"): ("seek1", "0", 1), ("seek1", "x"): ("seek1", "x", 1), ("seek1", "1"): ("rewind", "x", -1),
         ("seek0", "1"): ("seek0", "1", 1), ("seek0", "x"): ("seek0", "x", 1), ("seek0", "0"): ("rewind", "x", -1),
         ("rewind", "0"): ("rewind", "0", -1), ("rewind", "1"): ("rewind", "1", -1), ("rewind", "x"): ("rewind", "x", -1),
         ("rewind", "⊢"): ("next", "⊢", 1),
         ("next", "x"): ("next", "x", 1), ("next", "0"): ("seek1", "x", 1), ("next", "1"): ("seek0", "x", 1),
         ("next", B): ("accept", B, 1)}
    if slip:
        d[("seek1", B)] = ("seek1", B, 1)
    return d


E = lambda w: w.count("0") == w.count("1")
student, fixed = TM(eq_delta(True)), TM(eq_delta(False))
check("6.3 fixed machine (delete the seek1-blank entry) decides E: accepts E, rejects the rest, |w| <= 12",
      all(fixed.run(w, 20000)[0] == ("accept" if E(w) else "reject") for w in strings("01", 12)))
out, steps, tape, head, confs = student.run("100", max_steps=12, trace=True)
check("6.3(a) student on 100: (start,100,0) => (seek0,⊢00,1) => (rewind,⊢x0,0) => (next,⊢x0,1) => (next,⊢x0,2) "
      "=> (seek1,⊢xx,3) => (seek1,⊢xx,4) => ...",
      confs[:7] == [("start", "100", 0), ("seek0", "⊢00", 1), ("rewind", "⊢x0", 0), ("next", "⊢x0", 1),
                    ("next", "⊢x0", 2), ("seek1", "⊢xx", 3), ("seek1", "⊢xx", 4)], str(confs[:7]))
check("6.3(a) ... and it then moves right over blanks in seek1 forever", runs_right_forever(student, "100", "seek1"))
res = {w: student.run(w, 600)[0] for w in strings("01", 11)}
check("6.3(d) student's machine: Accept = E exactly (|w| <= 11)", all((res[w] == "accept") == E(w) for w in res))
check("6.3(d) it rejects exactly the strings with more 1s than 0s",
      all((res[w] == "reject") == (w.count("1") > w.count("0")) for w in res))
more0 = [w for w in res if w.count("0") > w.count("1")]
check("6.3(d) it runs forever on exactly the strings with more 0s (each reaches seek1 on a blank and walks right)",
      all(res[w] == "timeout" for w in more0) and all(runs_right_forever(student, w, "seek1") for w in more0),
      f"{len(more0)} strings")
check("6.3 never crashes (the ⊢ in cell 0 stops rewind)", all(res[w] != "crash" for w in res))

# ====================================================================== 6.4 palindromes
PAL = TM({("start", "0"): ("have0", B, 1), ("start", "1"): ("have1", B, 1), ("start", B): ("accept", B, 1),
          ("have0", "0"): ("have0", "0", 1), ("have0", "1"): ("have0", "1", 1), ("have0", B): ("last0", B, -1),
          ("have1", "0"): ("have1", "0", 1), ("have1", "1"): ("have1", "1", 1), ("have1", B): ("last1", B, -1),
          ("last0", "0"): ("back", B, -1), ("last0", B): ("accept", B, 1),
          ("last1", "1"): ("back", B, -1), ("last1", B): ("accept", B, 1),
          ("back", "0"): ("back", "0", -1), ("back", "1"): ("back", "1", -1), ("back", B): ("start", B, 1)})
ispal = lambda w: w == w[::-1]
check("6.4 machine decides the palindromes: accept/reject correct on every |w| <= 14",
      all(PAL.run(w)[0] == ("accept" if ispal(w) else "reject") for w in strings("01", 14)))
check("6.4 exactly (n+1)(n+2)/2 steps on every palindrome of length n <= 14",
      all(PAL.run(w)[1] == (len(w) + 1) * (len(w) + 2) // 2 for w in strings("01", 14) if ispal(w)))
check("6.4 at most (n+1)(n+2)/2 steps on every input of length n <= 12 (so O(n^2))",
      all(PAL.run(w)[1] <= (len(w) + 1) * (len(w) + 2) // 2 for w in strings("01", 12)))
out, steps, tape, head, confs = PAL.run("0110", trace=True)
check("6.4 check: 0110 accepted after 15 steps", out == "accept" and steps == 15)
out, steps, tape, head, confs = PAL.run("0100", trace=True)
check("6.4 check: 0100: round 1 erases both 0s, then last1 reads 0 and rejects after 13 steps",
      out == "reject" and steps == 13 and confs[-2] == ("last1", "□□0", 2), str(confs[-3:]))
out, steps, tape, head = PAL.run("010")
check("6.4 check: 010 (odd length) accepted via last1 reading a blank, 10 steps", out == "accept" and steps == 10)
out, steps, tape, head = PAL.run("")
check("6.4 check: epsilon accepted in 1 step", out == "accept" and steps == 1)


# ====================================================================== k-tape simulator (6.5, 6.1(f))
def run_k(delta, w, k=2, start="start", max_steps=100000):
    """delta[(q, (a1..ak))] = (p, (b1..bk), (d1..dk)), d in {-1, 0, +1}; missing -> reject."""
    tapes = [list(w)] + [[] for _ in range(k - 1)]
    heads = [0] * k
    q, steps = start, 0
    while q not in ("accept", "reject"):
        if steps >= max_steps:
            return "timeout", steps
        for t, h in zip(tapes, heads):
            while h >= len(t):
                t.append(B)
        reads = tuple(t[h] for t, h in zip(tapes, heads))
        steps += 1
        if (q, reads) not in delta:
            q = "reject"
            continue
        p, writes, moves = delta[(q, reads)]
        for t, h, b in zip(tapes, heads, writes):
            t[h] = b
        heads = [h + d for h, d in zip(heads, moves)]
        q = p
        if min(heads) < 0:
            return "crash", steps
    return q, steps


Z2 = {("start", ("0", B)): ("copy", ("0", "⊢"), (1, 1)),
      ("start", (B, B)): ("accept", (B, B), (1, 1)),
      ("copy", ("0", B)): ("copy", ("0", "x"), (1, 1)),
      ("copy", ("1", B)): ("match1", ("1", B), (0, -1)),
      ("match1", ("1", "x")): ("match1", ("1", "x"), (1, -1)),
      ("match1", ("1", "⊢")): ("match0", ("1", "⊢"), (1, 0)),
      ("match0", ("0", "⊢")): ("match0", ("0", "⊢"), (1, 1)),
      ("match0", ("0", "x")): ("match0", ("0", "x"), (1, 1)),
      ("match0", (B, B)): ("accept", (B, B), (1, 1))}


def inZ(w):
    m = re.fullmatch(r"(0*)(1*)(0*)", w)
    return bool(m) and len(m.group(1)) == len(m.group(2)) == len(m.group(3))


res = {w: run_k(Z2, w) for w in strings("01", 14)}
check("6.5(a) two-tape machine decides Z = {0^n 1^n 0^n}: correct on every |w| <= 14",
      all(res[w][0] == ("accept" if inZ(w) else "reject") for w in res))
check("6.5(a) it halts within n + 2 steps on every input of length n <= 14 (linear time)",
      all(res[w][1] <= len(w) + 2 for w in res))
check("6.5(b) exactly 3k + 2 steps on 0^k 1^k 0^k for 1 <= k <= 30, and 1 step on epsilon",
      all(run_k(Z2, "0" * k + "1" * k + "0" * k)[1] == 3 * k + 2 for k in range(1, 31)) and run_k(Z2, "")[1] == 1)
check("6.5 trace 010: 5 steps; 0110: rejected (match0 reads 1); 00110: rejected (match0 reads blank and x)",
      run_k(Z2, "010") == ("accept", 5) and run_k(Z2, "0110")[0] == "reject" and run_k(Z2, "00110")[0] == "reject")

# the one-tape machine of the chapter page (Section 6.3), for the comparison in 6.5(b)
ch = {("start", "0"): ("block1", "#", 1), ("start", B): ("accept", B, 1),
      ("block1", "0"): ("block1", "0", 1), ("block1", "1"): ("block2", "1", 1),
      ("block2", "1"): ("block2", "1", 1), ("block2", "0"): ("block3", "0", 1),
      ("block3", "0"): ("block3", "0", 1), ("block3", B): ("rewind", B, -1),
      ("rewind", "0"): ("rewind", "0", -1), ("rewind", "1"): ("rewind", "1", -1), ("rewind", "#"): ("seek1", "#", 1),
      ("seek1", "0"): ("seek1", "0", 1), ("seek1", "x"): ("seek1", "x", 1), ("seek1", "1"): ("seek0", "x", 1),
      ("seek0", "1"): ("seek0", "1", 1), ("seek0", "x"): ("seek0", "x", 1), ("seek0", "0"): ("reset", "x", -1),
      ("reset", "0"): ("reset", "0", -1), ("reset", "1"): ("reset", "1", -1), ("reset", "x"): ("reset", "x", -1),
      ("reset", "#"): ("mark0", "#", 1),
      ("mark0", "0"): ("seek1", "#", 1), ("mark0", "x"): ("verify", "x", 1),
      ("verify", "x"): ("verify", "x", 1), ("verify", B): ("accept", B, 1)}
C1 = TM(ch)
check("6.5(b) the chapter's one-tape machine decides Z (|w| <= 12) and takes 4k^2 + 9k + 1 steps on 0^k1^k0^k",
      all(C1.run(w)[0] == ("accept" if inZ(w) else "reject") for w in strings("01", 12))
      and all(C1.run("0" * k + "1" * k + "0" * k)[1] == 4 * k * k + 9 * k + 1 for k in range(0, 20)))
check("6.5(b) k = 100: two tapes 302 steps, one tape 40901 steps",
      run_k(Z2, "0" * 100 + "1" * 100 + "0" * 100)[1] == 302 and 4 * 100 ** 2 + 9 * 100 + 1 == 40901)

# ====================================================================== 6.6 the copier
COPY = TM({("next", "0"): ("carry0", "A", 1), ("next", "1"): ("carry1", "B", 1),
           ("next", "a"): ("clean", "0", 1), ("next", "b"): ("clean", "1", 1), ("next", B): ("halt", B, 1),
           **{("carry0", s): ("carry0", s, 1) for s in "01ab"}, ("carry0", B): ("back", "a", -1),
           **{("carry1", s): ("carry1", s, 1) for s in "01ab"}, ("carry1", B): ("back", "b", -1),
           **{("back", s): ("back", s, -1) for s in "01ab"},
           ("back", "A"): ("next", "0", 1), ("back", "B"): ("next", "1", 1),
           ("clean", "a"): ("clean", "0", 1), ("clean", "b"): ("clean", "1", 1), ("clean", B): ("halt", B, 1)},
          start="next", halt="halt")
r = {w: COPY.run(w) for w in strings("01", 12)}
check("6.6 copier halts with output ww on every w, |w| <= 12 (and never crashes)",
      all(r[w][0] == "halt" and r[w][2] == w + w for w in r))
check("6.6(d) exactly 2n^2 + 2n + 1 steps on every input of length n <= 12",
      all(r[w][1] == 2 * len(w) ** 2 + 2 * len(w) + 1 for w in r))
out, steps, tape, head, confs = COPY.run("10", trace=True)
check("6.6(c) run on 10: 13 steps; next is entered at (next,10,0), (next,10b,1), (next,10ba,2); halts as (halt,1010,5)",
      steps == 13 and [c for c in confs if c[0] == "next"] == [("next", "10", 0), ("next", "10b", 1), ("next", "10ba", 2)]
      and confs[-1] == ("halt", "1010", 5), str(confs))
check("6.6(c) full trace on 10 as printed in the solution",
      confs == [("next", "10", 0), ("carry1", "B0", 1), ("carry1", "B0", 2), ("back", "B0b", 1), ("back", "B0b", 0),
                ("next", "10b", 1), ("carry0", "1Ab", 2), ("carry0", "1Ab", 3), ("back", "1Aba", 2),
                ("back", "1Aba", 1), ("next", "10ba", 2), ("clean", "101a", 3), ("clean", "1010", 4),
                ("halt", "1010", 5)], str(confs))
check("6.6 at most one cell is ever marked A/B (the pointer), so back never needs the left end",
      all(sum(c[1].count(s) for s in "AB") <= 1 for w in strings("01", 8) for c in COPY.run(w, trace=True)[4]))
# watch out: marking every copied symbol and unmarking right-to-left at the end crashes at cell 0
BADC = TM({("next", "0"): ("carry0", "A", 1), ("next", "1"): ("carry1", "B", 1),
           ("next", "a"): ("fin", "a", -1), ("next", "b"): ("fin", "b", -1), ("next", B): ("halt", B, 1),
           **{("carry0", s): ("carry0", s, 1) for s in "01ab"}, ("carry0", B): ("back", "a", -1),
           **{("carry1", s): ("carry1", s, 1) for s in "01ab"}, ("carry1", B): ("back", "b", -1),
           **{("back", s): ("back", s, -1) for s in "01ab"},
           ("back", "A"): ("next", "A", 1), ("back", "B"): ("next", "B", 1),
           ("fin", "A"): ("fin", "0", -1), ("fin", "B"): ("fin", "1", -1)},
          start="next", halt="halt")
check("6.6 watch out: a copier that keeps every original marked and unmarks them walking left crashes on every w != eps",
      all(BADC.run(w)[0] == "crash" for w in strings("01", 8, minlen=1)))

# watch out: copies written as plain 0/1 -- the machine copies its own copies and never halts
PLAIN = TM({("next", "0"): ("carry0", "A", 1), ("next", "1"): ("carry1", "B", 1), ("next", B): ("halt", B, 1),
            **{("carry0", s): ("carry0", s, 1) for s in "01"}, ("carry0", B): ("back", "0", -1),
            **{("carry1", s): ("carry1", s, 1) for s in "01"}, ("carry1", B): ("back", "1", -1),
            **{("back", s): ("back", s, -1) for s in "01"},
            ("back", "A"): ("next", "0", 1), ("back", "B"): ("next", "1", 1)}, start="next", halt="halt")
grow = True
for w in strings("01", 6, minlen=1):
    o1, t1, x1, _ = PLAIN.run(w, max_steps=2000)
    o2, t2, x2, _ = PLAIN.run(w, max_steps=8000)
    grow = grow and o1 == o2 == "timeout" and len(x2) > len(x1) > 2 * len(w)
check("6.6 watch out: with copies written as plain 0/1 the machine keeps copying its own copies: still running, "
      "tape still growing, on every w != eps (|w| <= 6)", grow)

# ====================================================================== 6.1 true or false
rng = random.Random(374)


# (a) a machine that never moves left accepts a regular language: build the DFA and compare
def right_only_dfa(M, states, gamma, sigma):
    def from_blank(q):  # fate of state q reading blanks forever (depends only on q)
        seen = set()
        while q not in ("accept", "reject"):
            if q in seen:
                return False
            seen.add(q)
            if (q, B) not in M.delta:
                return False
            q = M.delta[(q, B)][0]
        return q == "accept"
    Q = list(states) + ["ACC", "REJ"]

    def step(q, a):
        if q in ("ACC", "REJ"):
            return q
        if (q, a) not in M.delta:
            return "REJ"
        p = M.delta[(q, a)][0]
        return {"accept": "ACC", "reject": "REJ"}.get(p, p)
    acc = ["ACC"] + [q for q in states if from_blank(q)]
    return DFA(sigma, Q, "start", acc, step)


ok, n = True, 0
for trial in range(300):
    states = ["start"] + [f"q{i}" for i in range(rng.randint(0, 3))]
    gamma = ["0", "1", "x", B]
    d = {}
    for q in states:
        for a in gamma:
            if rng.random() < 0.85:
                d[(q, a)] = (rng.choice(states + ["accept", "reject"]), rng.choice(gamma), 1)
    M = TM(d)
    D = right_only_dfa(M, states, gamma, "01")
    for w in strings("01", 8):
        if M.accepts(w, max_steps=len(w) + len(states) + 5) != D.accepts(w):
            ok = False
    n += 1
check("6.1(a) 300 random right-moving machines: the DFA (states Q + 2 sinks; accepting = ACC and the states whose "
      "blank walk accepts) agrees on every |w| <= 8", ok, f"{n} machines")
# (b) the machine that accepts at once halts on every input and accepts every string of {eps}, yet decides Sigma*
MA = TM({("start", a): ("accept", a, 1) for a in "01" + B})
check("6.1(b) counterexample: M_Accept halts on every input and accepts eps, but also accepts 0 (not in {eps})",
      all(MA.run(w)[0] == "accept" for w in strings("01", 6)))


# (d) stay-put removal (the chapter's construction): same outcome, at most 2t steps
def remove_stay(M, states, gamma):
    d = {}
    for (p, a), (q, b, mv) in M.delta.items():
        d[((p, 0), a)] = ((q, 1), b, 1) if mv == 0 else ((q, 0), b, mv)
    for p in states + ["accept", "reject"]:
        for a in gamma:
            d[((p, 1), a)] = ((p, 0), a, -1)
    return TM(d, start=("start", 0), accept=("accept", 0), reject=("reject", 0))


ok, maxratio = True, 0
for trial in range(300):
    states = ["start"] + [f"q{i}" for i in range(rng.randint(0, 3))]
    gamma = ["0", "1", B]
    d = {(q, a): (rng.choice(states + ["accept", "reject"]), rng.choice(gamma), rng.choice([-1, 0, 1]))
         for q in states for a in gamma if rng.random() < 0.85}
    M, M2 = TM(d), remove_stay(TM(d), states, gamma)
    for w in strings("01", 5):
        o1, t1, x1, _ = M.run(w, max_steps=400)
        o2, t2, x2, _ = M2.run(w, max_steps=800)
        if o1 == "timeout":
            continue
        if o1 != o2 or t2 > 2 * t1 or (o1 != "crash" and x1 != x2):
            ok = False
        if t1:
            maxratio = max(maxratio, t2 / t1)
check("6.1(d) stay-put removal on 300 random machines: same outcome and tape, at most 2t steps", ok,
      f"max ratio {maxratio:.2f}")


# (e) a two-way infinite tape folded onto two tracks: same outcome, at most 2t + 2 steps
def run_twoway(d, w, max_steps):
    tape = {i: a for i, a in enumerate(w)}
    q, h, t = "start", 0, 0
    while q not in ("accept", "reject"):
        if t >= max_steps:
            return "timeout", t
        a = tape.get(h, B)
        t += 1
        if (q, a) not in d:
            q = "reject"
            continue
        p, b, mv = d[(q, a)]
        tape[h] = b
        h += mv
        q = p
    return q, t


def fold(d, states, gamma):
    """Standard machine: cell i holds the pair (cell i, cell -i-1); cell 0's pair is marked '*'.
    A plain symbol a (never touched) is read as the pair (a, blank)."""
    S = {}

    def cells():
        for u in gamma:
            for v in gamma:
                for m in ("", "*"):
                    yield (u, v, m), u + "|" + v + m
    plain = {a: (a, B, "") for a in gamma}
    for a in gamma:   # initialisation: mark cell 0, step right and back
        S[("init", a)] = ("init2", a + "|" + B + "*", 1)
        for sym in [c for _, c in cells()] + list(gamma):
            S[("init2", sym)] = (("start", "U"), sym, -1)
    for q in states:
        for track in "UD":
            for (u, v, m), sym in list(cells()) + [(plain[a], a) for a in gamma]:
                r = u if track == "U" else v
                if (q, r) not in d:
                    S[((q, track), sym)] = ("reject", sym, 1)
                    continue
                p, b, mv = d[(q, r)]
                new = (b + "|" + v if track == "U" else u + "|" + b) + m
                if p in ("accept", "reject"):
                    S[((q, track), sym)] = (p, new, 1)
                    continue
                if track == "U":
                    if mv == 1:
                        S[((q, track), sym)] = ((p, "U"), new, 1)
                    elif m == "":
                        S[((q, track), sym)] = ((p, "U"), new, -1)
                    else:                    # from cell 0 to cell -1: switch tracks at real cell 0
                        S[((q, track), sym)] = (("turn", p, "D"), new, 1)
                else:
                    if mv == -1:
                        S[((q, track), sym)] = ((p, "D"), new, 1)
                    elif m == "":
                        S[((q, track), sym)] = ((p, "D"), new, -1)
                    else:                    # from cell -1 to cell 0
                        S[((q, track), sym)] = (("turn", p, "U"), new, 1)
        for p in states:
            for tr in "UD":
                for (u, v, m), sym in list(cells()) + [(plain[a], a) for a in gamma]:
                    S[(("turn", p, tr), sym)] = ((p, tr), sym, -1)
    return TM(S, start="init")


ok, maxratio, cnt = True, 0, 0
for trial in range(250):
    states = ["start"] + [f"q{i}" for i in range(rng.randint(1, 3))]
    gamma = ["0", "1", B]
    d = {(q, a): (rng.choice(states + ["accept", "reject"]), rng.choice(gamma), rng.choice([-1, 1]))
         for q in states for a in gamma if rng.random() < 0.9}
    S = fold(d, states, gamma)
    for w in strings("01", 4):
        o1, t1 = run_twoway(d, w, 300)
        if o1 == "timeout":
            continue
        o2, t2, _, _ = S.run(w, max_steps=1000)
        cnt += 1
        if o1 != o2 or t2 > 2 * t1 + 2:
            ok = False
        maxratio = max(maxratio, (t2 - 2) / t1)
check("6.1(e) two-track folding on 250 random two-way machines: same outcome, never crashes, at most 2t + 2 steps",
      ok, f"{cnt} halting runs, max (t'-2)/t = {maxratio:.2f}")

# (f) marked palindromes w#w^R: two tapes, O(n)
MP = {("start", (a, B)): ("copy", (a, "⊢"), (0, 1)) for a in "01#"}
for a in "01":
    MP[("copy", (a, B))] = ("copy", (a, a), (1, 1))
    MP[("cmp", (a, a))] = ("cmp", (a, a), (1, -1))
MP[("copy", ("#", B))] = ("cmp", ("#", B), (1, -1))
MP[("cmp", (B, "⊢"))] = ("accept", (B, "⊢"), (1, 1))
inMP = lambda w: w.count("#") == 1 and w.split("#")[0] == w.split("#")[1][::-1]
rr = {w: run_k(MP, w) for w in strings("01#", 9)}
check("6.1(f) a two-tape machine decides {w#w^R} within n + 2 steps (all strings over {0,1,#} of length <= 9)",
      all(rr[w][0] == ("accept" if inMP(w) else "reject") and rr[w][1] <= len(w) + 2 for w in rr))

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: {FAIL}")
sys.exit(1 if FAIL else 0)
