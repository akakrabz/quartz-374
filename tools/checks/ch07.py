#!/usr/bin/env python3
"""Checks for the concrete claims on content/1-models-of-computation/07-undecidability.md.

Chapter 7 is mostly proofs; what can be checked by computation is checked here: the diagonal argument on finite
tables (including the figure's), Cantor's theorem on small sets, the binary expansion of pi used in 7.2, the
constructions of Lemma 1 and the parallel simulations of Lemmas 4 and 5 on real Turing machines, the witness machines
for Rice's theorem, the ThisIsSparta example, the NeverLeft decider (against long simulations of random machines),
the figure's never-left run, and the LeftThree construction of Theorem 20."""
import itertools
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
from automata import TM, strings  # noqa: E402
import figs_ch07 as F  # noqa: E402  (figure data; importing does not write figures)

FAIL = []
B = "□"
GAMMA = ["0", "1", B]


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAIL.append(name)


# ---------------------------------------------------------------- a step-by-step runner (same rules as automata.TM)
class Run:
    """One run of a single-tape TM, advanced one transition at a time. Missing transitions reject (without moving),
    moving left from cell 0 crashes — exactly the conventions of tools/automata/tm.py (validated below)."""

    def __init__(self, tm, w):
        self.tm, self.tape, self.head, self.q, self.steps = tm, list(w), 0, tm.start, 0
        self.moves, self.read_states = [], []
        self.status = self._halted()

    def _halted(self):
        return "accept" if self.q == self.tm.accept else "reject" if self.q == self.tm.reject else None

    def step(self):
        if self.status:
            return self.status
        while self.head >= len(self.tape):
            self.tape.append(self.tm.blank)
        a = self.tape[self.head]
        self.read_states.append(self.q)
        self.steps += 1
        if (self.q, a) not in self.tm.delta:
            self.q = self.tm.reject
            self.status = "reject"
            return self.status
        p, b, d = self.tm.delta[(self.q, a)]
        self.tape[self.head], self.q = b, p
        self.head += d
        self.moves.append(d)
        if self.head < 0:
            self.status = "crash"
            return self.status
        self.status = self._halted()
        return self.status

    def run(self, budget):
        while not self.status and self.steps < budget:
            self.step()
        return self.status or "timeout"


def random_tm(rng, k, p_right=0.5, p_missing=0.1, p_halt=0.25):
    states = ["start"] + [f"q{i}" for i in range(1, k)]
    delta = {}
    for q in states:
        for a in GAMMA:
            if rng.random() < p_missing:
                continue
            r = rng.random()
            tgt = ("accept" if rng.random() < 0.5 else "reject") if r < p_halt else rng.choice(states)
            delta[(q, a)] = (tgt, rng.choice(GAMMA), +1 if rng.random() < p_right else -1)
    return TM(delta), states


def complete(tm, states):
    """Make the 'missing transitions reject' convention explicit (same outcome and step count)."""
    d = dict(tm.delta)
    for q in states:
        for a in GAMMA:
            d.setdefault((q, a), (tm.reject, a, +1))
    return d


def absorbing_right(delta, q):
    """q only ever moves right and stays in q: once entered, the machine runs forever (never crashes)."""
    return all(delta.get((q, a)) == (q, a, +1) for a in GAMMA)


rng = random.Random(374)

# ---------------------------------------------------------------- the runner agrees with automata.TM
ok, n = True, 0
for _ in range(300):
    M, _st = random_tm(rng, rng.randint(1, 4))
    for w in strings("01", 4):
        n += 1
        a = M.run(w, max_steps=300)
        r = Run(M, w)
        b = r.run(300)
        if (a[0], a[1]) != (b, r.steps):
            ok = False
check("step-by-step runner = automata.TM on 300 random machines x 31 inputs (outcome and step count)", ok, f"{n} runs")

# ---------------------------------------------------------------- 7.2 the binary expansion of pi
def pi_floor_times_2_to(nbits, guard=40):
    """floor(pi * 2^nbits) by Machin's formula pi = 16 atan(1/5) - 4 atan(1/239), in integer arithmetic."""
    P = nbits + guard
    one = 1 << P

    def atan_inv(x):
        total, t, k, sign = 0, one // x, 1, 1
        while t:
            total += sign * (t // k)
            t //= x * x
            k += 2
            sign = -sign
        return total

    return (16 * atan_inv(5) - 4 * atan_inv(239)) >> guard


bits = bin(pi_floor_times_2_to(4000))[2:]
intpart, frac = bits[:2], bits[2:]
hexfrac = "".join(f"{int(h, 16):04b}" for h in "243F6A8885A308D313198A2E03707344")
check("pi computation matches the known hex expansion 3.243F6A8885A308D313198A2E03707344...",
      intpart == "11" and frac.startswith(hexfrac))
check("pi = 11.0010010000111111011..._2", bits.startswith("110010010000111111011"))
first6 = frac.find("111111") + 1
check("the run 1^6 occupies fraction bits 11-16 (so every string of length <= 6 is in Pi)",
      first6 == 11 and frac[16] == "0", f"first 111111 at bit {first6}")
longest = max(len(r) for r in frac[:4000].split("0"))
check("the first 4000 fraction bits contain a run of ten 1s, but none longer", longest == 10, f"{longest}")

# ---------------------------------------------------------------- Lemma 1: M^R, M^A, M^H on random machines
ok_r = ok_a = ok_h = True
cnt = {"accept": 0, "reject": 0, "crash": 0, "timeout": 0}
for _ in range(300):
    M, states = random_tm(rng, rng.randint(1, 4))
    d = complete(M, states)
    swap = {"accept": "reject", "reject": "accept"}
    MR = TM({k: (swap.get(q, q), b, m) for k, (q, b, m) in d.items()})
    dA = {k: ("hang" if q == "reject" else q, b, m) for k, (q, b, m) in d.items()}
    dA.update({("hang", a): ("hang", a, +1) for a in GAMMA})
    MA = TM(dA)
    MH = TM({k: ("accept" if q == "reject" else q, b, m) for k, (q, b, m) in d.items()})
    for w in strings("01", 4):
        o = Run(M, w).run(200)
        cnt[o] += 1
        rR, rA, rH = Run(MR, w), Run(MA, w), Run(MH, w)
        oR, oA, oH = rR.run(200), rA.run(200), rH.run(200)
        # M^R: accept and reject swapped, everything else unchanged
        ok_r &= oR == {"accept": "reject", "reject": "accept"}.get(o, o)
        # M^A: same acceptances; where M rejects, M^A enters 'hang' (absorbing, moves right forever)
        if o == "reject":
            ok_a &= oA == "timeout" and rA.q == "hang" and absorbing_right(MA.delta, "hang")
        else:
            ok_a &= oA == o
        # M^H: accepts exactly where M halts
        ok_h &= oH == ("accept" if o in ("accept", "reject") else o)
check("Lemma 1(a): M^R (swap accept/reject) has Accept = Reject(M) and Reject = Accept(M)", ok_r, str(cnt))
check("Lemma 1(b): M^A (reject -> looping state) has Accept = Accept(M) and rejects nothing", ok_a)
check("Lemma 1(c): M^H (reject -> accept) has Accept = Halt(M) and rejects nothing", ok_h)

# ---------------------------------------------------------------- Lemma 4 example: union needs parallel simulation
loop = {("loop", a): ("loop", a, +1) for a in GAMMA}
M1 = TM({("start", "1"): ("accept", "1", +1), ("start", "0"): ("loop", "0", +1), ("start", B): ("loop", B, +1),
         **loop})                                                      # accepts 1Σ*, runs forever otherwise
M2 = TM({("start", "0"): ("z", "0", +1), ("start", "1"): ("start", "1", +1), ("start", B): ("reject", B, +1),
         ("z", "0"): ("z", "0", +1), ("z", "1"): ("start", "1", +1), ("z", B): ("accept", B, +1)})  # decides Σ*0
L1 = lambda w: w.startswith("1")
L2 = lambda w: w.endswith("0")
ok1 = all((Run(M1, w).run(1000) == "accept") == L1(w) for w in strings("01", 9))
ok1 &= all(Run(M1, w).run(1000) == "timeout" for w in strings("01", 9) if not L1(w))
check("example M accepts exactly the strings starting with 1 and runs forever on the others (|w| <= 9)",
      ok1 and absorbing_right(M1.delta, "loop"))
check("example M' decides the strings ending with 0 (|w| <= 9)",
      all(Run(M2, w).run(1000) == ("accept" if L2(w) else "reject") for w in strings("01", 9)))
r = Run(M1, "00")
r.run(1000)
check("serial union fails: M never finishes on 00 (it enters its endless loop), although 00 ends with 0",
      r.q == "loop" and L2("00"))


def parallel(Ma, Mb, w, budget, on_a="accept", on_b="accept"):
    """Run Ma and Mb in lockstep, one step each; report (who accepted first, steps) or None."""
    ra, rb = Run(Ma, w), Run(Mb, w)
    for t in range(budget):
        if ra.status == "accept":
            return on_a, t
        if rb.status == "accept":
            return on_b, t
        if ra.status and rb.status:            # both halted without accepting
            return "reject", t
        ra.step()
        rb.step()
    return None, budget


ok = True
for w in strings("01", 9):
    res, _t = parallel(M1, M2, w, 2000)
    ok &= (res == "accept") == (L1(w) or L2(w))
check("parallel simulation accepts exactly L(M) ∪ L(M') (|w| <= 9)", ok)

# ---------------------------------------------------------------- Lemma 5 example: L and its complement in parallel
def parity_acceptor(accept_even):
    d = {("e", "0"): ("e", "0", +1), ("e", "1"): ("o", "1", +1), ("o", "0"): ("o", "0", +1), ("o", "1"): ("e", "1", +1),
         ("e", B): ("accept" if accept_even else "loop", B, +1), ("o", B): ("loop" if accept_even else "accept", B, +1),
         **loop}
    return TM(d, start="e")


A_even, A_odd = parity_acceptor(True), parity_acceptor(False)
even = lambda w: w.count("1") % 2 == 0
ok = all((Run(A_even, w).run(500) == "accept") == even(w) and (Run(A_odd, w).run(500) == "accept") != even(w)
         for w in strings("01", 10))
ok &= all(Run(A_even, w).run(500) == "timeout" for w in strings("01", 10) if not even(w))
check("toy acceptors: one accepts 'even number of 1s', the other its complement; each runs forever otherwise", ok)
ok, worst = True, 0
for w in strings("01", 10):
    res, t = parallel(A_even, A_odd, w, 10000, on_a="accept", on_b="reject")
    ok &= res == ("accept" if even(w) else "reject")
    worst = max(worst, t - len(w))
check("Lemma 5: the two acceptors in parallel halt on every input with the right answer (|w| <= 10)", ok,
      f"halts within |w| + {worst} rounds")
# and on random machines: if Ma accepts L and Mb accepts exactly the complement (on the inputs tried), parallel decides
ok, tried = True, 0
for _ in range(400):
    Ma, _s = random_tm(rng, rng.randint(1, 3))
    outs = {w: Run(Ma, w).run(300) for w in strings("01", 4)}
    if "timeout" in outs.values() or "crash" in outs.values():
        continue
    # turn Ma (which halts on these inputs) into acceptors for Accept(Ma) and Reject(Ma) via Lemma 1
    d = complete(Ma, _s)
    dA = {k: ("hang" if q == "reject" else q, b, m) for k, (q, b, m) in d.items()}
    dA.update({("hang", a): ("hang", a, +1) for a in GAMMA})
    sw = {"accept": "hang", "reject": "accept"}
    dB = {k: (sw.get(q, q), b, m) for k, (q, b, m) in d.items()}
    dB.update({("hang", a): ("hang", a, +1) for a in GAMMA})
    for w, o in outs.items():
        tried += 1
        res, _t = parallel(TM(dA), TM(dB), w, 2000, on_a="accept", on_b="reject")
        ok &= res == o
check("Lemma 5 on random halting machines: acceptors for Accept(M), Reject(M) in parallel reproduce M", ok,
      f"{tried} runs")

# ---------------------------------------------------------------- 7.5 / 7.6 diagonalization
flip = lambda e: "acc" if e == "rej" else "rej"
check("figure: the SR row is the flipped diagonal of the table", F.SR_ROW == [flip(F.DIAG[j][j]) for j in range(6)])
check("figure: the SR row differs from every row M_i in column i",
      all(F.SR_ROW[i] != F.DIAG[i][i] for i in range(6)))
check("figure: the table uses all three outcomes on the diagonal", {F.DIAG[i][i] for i in range(6)} == {"acc", "rej", "∞"})
ok = True
for _ in range(2000):
    n = rng.randint(1, 12)
    T = [[rng.choice(["acc", "rej", "∞"]) for _ in range(n)] for _ in range(n)]
    f = [flip(T[j][j]) for j in range(n)]
    ok &= all(f != T[i] for i in range(n)) and all(f[i] != T[i][i] for i in range(n))
check("random tables (2000, up to 12 x 12): the flipped diagonal differs from every row", ok)

ok, nf = True, 0
for n in range(0, 5):
    X = list(range(n))
    subsets = [frozenset(c) for k in range(n + 1) for c in itertools.combinations(X, k)]
    for f in itertools.product(subsets, repeat=n):
        nf += 1
        Y = frozenset(x for x in X if x not in f[x])
        ok &= Y not in f
check("Cantor's theorem: for every f: X -> 2^X with |X| <= 4, the 'sad' set Y is not in the image", ok,
      f"{nf} functions")

# ---------------------------------------------------------------- 7.11 Rice's theorem: the witness machines
M_acc = TM({("start", a): ("accept", a, +1) for a in GAMMA})
M_rej = TM({})
M_div = TM({("start", a): ("start", a, +1) for a in GAMMA})
ok = all(Run(M_acc, w).run(10) == "accept" and Run(M_rej, w).run(10) == "reject" and Run(M_div, w).run(500) == "timeout"
         for w in strings("01", 8))
check("M_Accept accepts every input, M_Reject rejects every input, M_Diverge runs forever (|w| <= 8)",
      ok and absorbing_right(M_div.delta, "start"))

# ThisIsSparta: two machines with the same language, one in the language and one not
SP = list("SPART") + [B]


def counter(k):
    names = ["start"] + [f"c{i}" for i in range(1, k)]
    d = {}
    for i, q in enumerate(names):
        for a in SP:
            d[(q, a)] = (names[i + 1] if i + 1 < k else "accept", a, +1)
    return TM(d)


C300, C301 = counter(300), counter(301)
o300, o301 = C300.run("SPARTA"), C301.run("SPARTA")
check("a machine that accepts every input after exactly 300 steps accepts SPARTA at step 300",
      o300[0] == "accept" and o300[1] == 300)
check("... and a 301-step variant accepts SPARTA at step 301 (same language, not in ThisIsSparta)",
      o301[0] == "accept" and o301[1] == 301)
check("both accept every string over {S,P,A,R,T} of length <= 4",
      all(C300.accepts(w) and C301.accepts(w) for w in strings("SPART", 4)))

# ---------------------------------------------------------------- 7.13 NeverLeft (Theorem 19)
def num_states(tm):
    qs = {tm.start, tm.accept, tm.reject}
    for (p, _a), (q, _b, _m) in tm.delta.items():
        qs |= {p, q}
    return len(qs)


def never_left(tm, w):
    """Theorem 19's decider: simulate; reject at the first left move; accept if M halts, or once M has read more
    than |Q| blanks (it has then moved right over blanks in a cycle forever). Returns (answer, steps simulated)."""
    Q = num_states(tm)
    run, blanks = Run(tm, w), 0
    while True:
        if run.status in ("accept", "reject"):
            return True, run.steps
        if run.head >= len(w):
            blanks += 1
            if blanks > Q:
                return True, run.steps
        run.step()
        if run.moves and run.moves[-1] == -1:
            return False, run.steps


nl = TM(F.NL_DELTA)
r = Run(nl, F.NL_INPUT)
r.run(len(F.NL_STATES))
check("figure: the never-left machine reads cells 0, 1, 2, ... in states start, start, p, p, q, r, q, r",
      r.read_states == F.NL_STATES and all(m == +1 for m in r.moves), str(r.read_states))
check("figure: the first repeated state on a blank is q (cells 4 and 6)",
      F.NL_STATES[4] == F.NL_STATES[6] == "q" and len(set(F.NL_STATES[3:6])) == 3)
check("figure machine: the decider accepts <M, 011> (|Q| = 6) and long simulation never moves left",
      never_left(nl, "011")[0] and Run(nl, "011").run(5000) == "timeout" and num_states(nl) == 6)

agree, by_rule, total, maxsteps = True, 0, 0, 0
for _ in range(400):
    M, _st = random_tm(rng, rng.randint(1, 4), p_right=0.85, p_halt=0.15)
    Q = num_states(M)
    for w in strings("01", 3):
        total += 1
        ans, steps = never_left(M, w)
        maxsteps = max(maxsteps, steps - len(w) - Q)
        long = Run(M, w)
        long.run(4000)
        left = -1 in long.moves
        agree &= ans == (not left)
        if ans and long.status is None:          # accepted by the |Q|-blanks rule: must loop right forever
            by_rule += 1
            agree &= all(m == +1 for m in long.moves)
check("NeverLeft decider agrees with 4000-step simulations on 400 random machines x 15 inputs", agree,
      f"{total} runs, {by_rule} decided by the |Q|-blanks rule")
check("the decider always stops within |w| + |Q| simulated steps", maxsteps <= 0, f"max excess {maxsteps}")

# ---------------------------------------------------------------- Theorem 20: the LeftThree construction
def left_three_version(tm, states):
    """M': simulate M, but after every step move right and back left (so never three lefts in a row), and just
    before accepting move right three times and left three times."""
    d = complete(tm, states)
    out = {}
    for (p, a), (q, b, m) in d.items():
        if q == tm.accept:
            out[(p, a)] = (("acc", 1), b, m)
        elif q == tm.reject:
            out[(p, a)] = (tm.reject, b, m)
        else:
            out[(p, a)] = ((q, "w1"), b, m)
    for q in states:
        for c in GAMMA:
            out[((q, "w1"), c)] = ((q, "w2"), c, +1)
            out[((q, "w2"), c)] = (q, c, -1)
    chain = [("acc", i) for i in range(1, 7)] + [tm.accept]
    for i in range(6):
        for c in GAMMA:
            out[(chain[i], c)] = (chain[i + 1], c, +1 if i < 3 else -1)
    return TM(out)


def max_left_run(moves):
    best = cur = 0
    for m in moves:
        cur = cur + 1 if m == -1 else 0
        best = max(best, cur)
    return best


ok, stats = True, {"accept": 0, "reject": 0, "crash": 0, "timeout": 0}
for _ in range(400):
    M, states = random_tm(rng, rng.randint(1, 4))
    Mp = left_three_version(M, states)
    for w in strings("01", 3):
        o = Run(M, w).run(300)
        stats[o] += 1
        rp = Run(Mp, w)
        op = rp.run(3 * 300 if o == "timeout" else 3 * 300 + 10)
        lll = max_left_run(rp.moves) >= 3
        if o == "accept":
            ok &= op == "accept" and lll and rp.moves[-3:] == [-1, -1, -1] and max_left_run(rp.moves[:-3]) <= 2
        else:
            ok &= op == o and not lll
check("Theorem 20: M' moves left three times in a row iff M accepts (400 random machines x 15 inputs)", ok, str(stats))

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: {FAIL}")
sys.exit(1 if FAIL else 0)
