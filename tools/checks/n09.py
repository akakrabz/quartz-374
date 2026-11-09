#!/usr/bin/env python3
"""Checks for content/4-lecture-notes/09-amortized-analysis.md (Erickson, Director's Cut 9, Amortized Analysis) and the
concept page content/concepts/amortized-analysis.md.

Every algorithm of the note is implemented line for line — Increment, the double binary counter's Increment and
Decrement, the binary reflected Gray code and Ehrlich's loopless Gray increment — and every amortized claim is tested
against the actual total cost: exactly (closed forms) for counting from 0 to n, exhaustively over all operation
sequences up to length 14 for the double counter, and on long random and adversarial sequences. Each accounting scheme
of the note (two tax schedules, the charging scheme, the potential function) is simulated literally with exact
fractions, bit by bit. The note's examples (the double-counter trace, the Gray code list, Ehrlich's G/F table) are
recomputed; the note's invariant for Ehrlich's focus array is tested (it fails) and the corrected one is verified. The
concept page's examples (a base-b counter, a doubling array) are checked the same way. Finally, numbers printed on the
pages and drawn in the figures are compared with the computed ones."""
import itertools
import math
import os
import random
import re
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
PAGE = os.path.join(ROOT, "content", "4-lecture-notes", "09-amortized-analysis.md")
CONCEPT = os.path.join(ROOT, "content", "concepts", "amortized-analysis.md")
FIGS = os.path.join(HERE, "..", "figs")
FAIL = []
random.seed(9374)


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAIL.append(name)


def read(path):
    return open(path, encoding="utf-8").read() if os.path.exists(path) else ""


def popcount(n):
    return bin(n).count("1")


# =====================================================================================================
print("== 9.1–9.2  The binary counter")


def increment(B):
    """Increment(B[0..∞]) exactly as in the note; returns the list of (index, new value) bit flips."""
    flips = []
    i = 0
    while B[i] == 1:
        B[i] = 0
        flips.append((i, 0))
        i += 1
    B[i] = 1
    flips.append((i, 1))
    return flips


W = 64
B = [0] * W
flips_per_bit = [0] * W
total = 0
ok_value = ok_exact = ok_perbit = ok_cost = ok_amort = ok_sum = True
history = []                 # history[k-1] = flips of the k-th increment
for n in range(1, 1 << 13):
    before = popcount(n - 1)
    fl = increment(B)
    history.append(fl)
    c = len(fl)
    total += c
    for (i, v) in fl:
        flips_per_bit[i] += 1
    # cost of incrementing n-1 = (trailing ones of n-1) + 1
    t = 0
    while (n - 1) >> t & 1:
        t += 1
    ok_cost &= (c == t + 1)
    ok_value &= (sum(b << i for i, b in enumerate(B)) == n)
    ok_exact &= (total == 2 * n - popcount(n))
    ok_perbit &= all(flips_per_bit[i] == n >> i for i in range(W))
    # potential: Phi = number of 1 bits; amortized cost c + dPhi is exactly 2
    ok_amort &= (c + popcount(n) - before == 2)
    ok_sum &= (sum(n >> i for i in range(n.bit_length())) < 2 * n)
check("Increment computes n+1 (all n < 2^13)", ok_value)
check("the k-th Increment flips (trailing ones of k-1) + 1 bits", ok_cost)
check("n Increments from 0 flip B[i] exactly floor(n/2^i) times", ok_perbit)
check("sum_{i=0}^{floor(lg n)} floor(n/2^i) < 2n", ok_sum)
check("total flips counting 0 -> n is exactly 2n - #1(n)", ok_exact)
check("potential Phi = #1 bits: every Increment has amortized cost exactly 2", ok_amort)
check("worked numbers: 0 -> 16 costs 31 flips, 0 -> 1000 costs 1994 (#1(1000) = 6)",
      sum(len(h) for h in history[:16]) == 31 and sum(len(h) for h in history[:1000]) == 1994 and popcount(1000) == 6)
check("Increment of 2^k - 1 flips k + 1 bits (k = 0..12); binary length of n is floor(lg n) + 1",
      all(len(history[(1 << k) - 1]) == k + 1 for k in range(13))
      and all(n.bit_length() == math.floor(math.log2(n)) + 1 for n in range(1, 5000)))
# from an arbitrary start v, n increments cost exactly 2n + #1(v) - #1(v+n)
ok = True
for _ in range(300):
    v = random.randrange(0, 1 << 20)
    n = random.randrange(1, 3000)
    BB = [(v >> i) & 1 for i in range(W)]
    cost = sum(len(increment(BB)) for _ in range(n))
    ok &= cost == 2 * n + popcount(v) - popcount(v + n)
check("from any start v, n Increments cost exactly 2n + #1(v) - #1(v+n) <= 2n + #1(v)", ok)

# --- taxation method 1: $2 per 0->1 change, $1 stored on the bit
ok = True
B = [0] * W
bank = [0] * W
for k in range(1, 5000):
    for (i, v) in increment(B):
        if v == 1:
            bank[i] += 2 - 1           # pay 2, spend 1, store 1 on the bit
        else:
            bank[i] -= 1               # clearing is paid by the stored dollar
            ok &= bank[i] >= 0
    ok &= all(bank[i] == B[i] for i in range(W))
check("taxation 1: $2 per 0->1 change; every 1 bit holds exactly the $1 that pays for clearing it", ok)

# --- taxation method 2: bit i charges 2^-i per Increment, pays $1 per flip
ok_bank = ok_zero = True
B = [0] * W
bank = [Fr(0)] * 20
for k in range(1, 1 << 12):
    for i in range(20):
        bank[i] += Fr(1, 2 ** i)
    for (i, v) in increment(B):
        bank[i] -= 1
        ok_zero &= bank[i] == 0          # it has collected exactly $1 since its last flip
    ok_bank &= all(b >= 0 for b in bank)
check("taxation 2: bit i collects 2^-i per Increment, never goes into debt, and has exactly $1 at each flip",
      ok_bank and ok_zero)
check("taxation 2: total tax per Increment sum_{i>=0} 2^-i = 2 (partial sums < 2, -> 2)",
      sum(Fr(1, 2 ** i) for i in range(30)) < 2 and 2 - sum(Fr(1, 2 ** i) for i in range(30)) == Fr(1, 2 ** 29))

# --- charging: each clearing of B[j] in increment k is charged to increment k - 2^j, which set B[j]
ok_target = ok_nearest = ok_two = True
charges = [0] * (len(history) + 1)
for k, fl in enumerate(history[:4096], start=1):
    for (j, v) in fl:
        if v == 0:
            src = k - 2 ** j
            ok_target &= src >= 1 and (j, 1) in history[src - 1] and history[src - 1][-1] == (j, 1)
            # nearest stack to the left that reaches level j is stack src (stacks between are lower)
            ok_nearest &= all(len(history[m - 1]) <= j for m in range(src + 1, k))
            charges[src] += 1
for k, fl in enumerate(history[:4096], start=1):
    ok_two &= 1 + charges[k] <= 2
check("charging: each 1->0 flip of B[j] in Increment k is charged to Increment k - 2^j, the last one to set B[j]",
      ok_target)
check("charging: that block is the first block at height j to the left (the stacks in between are lower)", ok_nearest)
check("charging: after moving, every stack has at most two blocks (its own 0->1 flip + at most one charge)", ok_two)

# --- standard counter cannot also decrement cheaply
def decrement_std(B):
    flips = 0
    i = 0
    while B[i] == 0:
        B[i] = 1
        flips += 1
        i += 1
    B[i] = 0
    return flips + 1


ok = True
for k in range(1, 12):
    BB = [((2 ** k) >> i) & 1 for i in range(W)]
    for r in range(6):
        ok &= decrement_std(BB) == k + 1
        ok &= len(increment(BB)) == k + 1
check("standard binary counter alternating 2^k <-> 2^k - 1: every operation flips k + 1 bits", ok)

# =====================================================================================================
print("== 9.3  The double binary counter")


def dinc(P, N):
    i = 0
    fl = []
    while P[i] == 1:
        P[i] = 0
        fl.append(("P", i, 0))
        i += 1
    if N[i] == 1:
        N[i] = 0
        fl.append(("N", i, 0))
    else:
        P[i] = 1
        fl.append(("P", i, 1))
    return fl


def ddec(P, N):
    i = 0
    fl = []
    while N[i] == 1:
        N[i] = 0
        fl.append(("N", i, 0))
        i += 1
    if P[i] == 1:
        P[i] = 0
        fl.append(("P", i, 0))
    else:
        N[i] = 1
        fl.append(("N", i, 1))
    return fl


def val(X):
    return sum(b << i for i, b in enumerate(X))


def bits_from(s, w=W):
    return [int(ch) for ch in reversed(s)] + [0] * (w - len(s))


def to_str(X, w):
    return "".join(str(X[i]) for i in reversed(range(w)))


# the note's trace
P, N = bits_from("10001"), bits_from("01100")
trace = [(to_str(P, 5), to_str(N, 5), val(P) - val(N))]
for op in "+++--+":
    (dinc if op == "+" else ddec)(P, N)
    trace.append((to_str(P, 5), to_str(N, 5), val(P) - val(N)))
NOTE_TRACE = [("10001", "01100", 5), ("10010", "01100", 6), ("10011", "01100", 7), ("10000", "01000", 8),
              ("10000", "01001", 7), ("10000", "01010", 6), ("10001", "01010", 7)]
check("the note's double-counter trace (++ ++ ++ -- -- ++ from P=10001, N=01100) is reproduced exactly",
      trace == NOTE_TRACE, str(trace))
check("zero has exactly one representation (0,0) among all pairs of 7-bit strings with P AND N = 0",
      [(p, q) for p in range(128) for q in range(128) if p & q == 0 and p - q == 0] == [(0, 0)])
reps = {x: [sum(1 for p in range(1 << w) for q in range(1 << w) if p & q == 0 and p - q == x) for w in (3, 5, 7)]
        for x in (-3, -1, 1, 6)}
check("nonzero values have more and more representations as the width grows (infinitely many)",
      all(a < b < c for a, b, c in reps.values()), str(reps))


def run_double(ops, P=None, N=None, w=W):
    P = P or [0] * w
    N = N or [0] * w
    out = []
    for op in ops:
        fl = (dinc if op == "+" else ddec)(P, N)
        out.append(fl)
    return out, P, N


ok_inv = ok_val = ok_one_set = ok_amort = ok_total = True
ok_setreset = ok_spacing = ok_tax = True
count = 0


def analyze(ops):
    global ok_inv, ok_val, ok_one_set, ok_amort, ok_total, ok_setreset, ok_spacing, ok_tax, count
    P, N = [0] * 24, [0] * 24
    v = 0
    tot = 0
    phi = 0
    last = {}
    bank = {}
    for t, op in enumerate(ops, start=1):
        fl = (dinc if op == "+" else ddec)(P, N)
        v += 1 if op == "+" else -1
        ok_inv &= all(not (P[i] and N[i]) for i in range(24))
        ok_val &= val(P) - val(N) == v
        sets = sum(1 for f in fl if f[2] == 1)
        ok_one_set &= sets <= 1
        c = len(fl)
        newphi = sum(P) + sum(N)
        ok_amort &= c + newphi - phi == 2 * sets <= 2
        phi = newphi
        tot += c
        for key in [(s, i) for s in "PN" for i in range(12)]:
            bank[key] = bank.get(key, Fr(0)) + Fr(1, 2 ** key[1])
        for (s, i, nv) in fl:
            key = (s, i)
            if key in last:
                lt, lv = last[key]
                if lv == 1 and nv == 0:
                    ok_setreset &= t - lt >= 2 ** i
                ok_spacing &= t - lt >= 2 ** i
            else:
                ok_spacing &= t >= 2 ** i
            last[key] = (t, nv)
            bank[key] -= 1
            ok_tax &= bank[key] >= 0
    ok_total &= tot <= 2 * len(ops)
    count += 1


for L in range(1, 15):
    for ops in itertools.product("+-", repeat=L):
        analyze(ops)
for _ in range(60):
    L = random.randrange(100, 3000)
    analyze([random.choice("+-") for _ in range(L)])
for k in range(1, 9):   # adversarial: climb to 2^k - 1, then alternate around 2^k
    analyze(["+"] * (2 ** k - 1) + ["+", "-"] * 300)
    analyze(["-"] * (2 ** k - 1) + ["-", "+"] * 300)
    analyze((["+"] * (2 ** k) + ["-"] * (2 ** k)) * 20)
check(f"P AND N = 0 is maintained and P - N equals the count ({count} sequences: all of length <= 14, "
      f"plus long random and adversarial ones)", ok_inv and ok_val)
check("every Increment/Decrement sets at most one bit to 1", ok_one_set)
check("potential = #1 bits in P and N: amortized cost = 2 x (#bits set) <= 2 for every operation", ok_amort)
check("total actual cost of n operations from (0,0) is at most 2n", ok_total)
check("the note's lemma: after P[i] or N[i] is set to 1, at least 2^i operations pass before it is reset",
      ok_setreset)
check("stronger: any two flips of the same bit P[i] or N[i] are >= 2^i operations apart, the first at time >= 2^i",
      ok_spacing)
check("taxation: every bit P[i], N[i] collecting 2^-i per operation pays for all its own flips (amortized <= 4)",
      ok_tax)
# worst case: one operation can cost Theta(log n)
ops, P, N = run_double(["+"] * 1023 + ["+"])
check("worst case: after 1023 Increments from (0,0), the 1024th flips 11 bits", len(ops[-1]) == 11)

# =====================================================================================================
print("== 9.4  Gray codes and Ehrlich's algorithm")


def gray(k):
    return k ^ (k >> 1)


NOTE_GRAY = "0000, 0001, 0011, 0010, 0110, 0111, 0101, 0100, 1100, 1101, 1111, 1110, 1010, 1011, 1001, 1000".split(", ")
check("the note's 4-bit list is the binary reflected Gray code g(k) = k XOR floor(k/2)",
      NOTE_GRAY == [format(gray(k), "04b") for k in range(16)])
ok = True
for n in range(1, 13):
    for k in range((1 << n) - 1):
        d = gray(k) ^ gray(k + 1)
        t = 0
        while (k >> t) & 1:
            t += 1
        ok &= d == 1 << t       # one bit, the one a binary counter sets from 0 to 1
check("successive Gray codes differ in exactly one bit: the bit a binary counter sets from 0 to 1 (n <= 12)", ok)


def naive_gray_increment(G, parity):
    """Find the bit to flip from G alone: bit 0 if parity even, else the bit left of the lowest 1. Returns cost."""
    if parity == 0:
        G[0] ^= 1
        return 1
    i = 0
    while G[i] == 0:
        i += 1
    G[i + 1] ^= 1
    return i + 2


G = [0] * 20
tot = 0
ok = True
for k in range(1, 1 << 12):
    tot += naive_gray_increment(G, (k - 1) & 1)
    ok &= val(G) == gray(k)
check("naive Gray increment (scan for the lowest 1): correct, Theta(log n) worst case, O(1) amortized "
      "(total <= 2n + n/2 over 0 -> n)", ok and tot <= 2.5 * ((1 << 12) - 1), str(tot))


def naive_gray_decrement(G, parity):
    """Inverse of the increment: bit 0 if parity odd, else the bit left of the lowest 1. Returns cost."""
    if parity == 1:
        G[0] ^= 1
        return 1
    i = 0
    while G[i] == 0:
        i += 1
    G[i + 1] ^= 1
    return i + 2


# review R33: naive Gray inc/dec alternating 2^k - 1 <-> 2^k
ok = True
for k in range(2, 13):
    G = [(gray((1 << k) - 1) >> i) & 1 for i in range(20)]
    for rep in range(10):
        c1 = naive_gray_increment(G, sum(G) & 1)
        ok &= val(G) == gray(1 << k)
        c2 = naive_gray_decrement(G, sum(G) & 1)
        ok &= val(G) == gray((1 << k) - 1)
        ok &= c1 == k + 1 and c2 == k + 1
check("naive Gray increment/decrement alternating between 2^k - 1 and 2^k: every operation scans k + 1 bits "
      "(Theta(log n) amortized, like the binary counter)", ok)


def ehrlich_init(n):
    return [0] * n, list(range(n + 1))


def ehrlich_increment(n, G, F):
    j = F[0]
    F[0] = 0
    if j == n:
        G[n - 1] = 1 - G[n - 1]
    else:
        G[j] = 1 - G[j]
        F[j] = F[j + 1]
        F[j + 1] = j + 1


n = 4
G, F = ehrlich_init(n)
gs, fs = [], []
for k in range(16):
    gs.append("".join(str(G[i]) for i in reversed(range(n))))
    fs.append("".join(str(F[i]) for i in reversed(range(n))))
    if k < 15:
        ehrlich_increment(n, G, F)
NOTE_F = "3210, 3211, 3220, 3212, 3310, 3311, 3230, 3213, 4210, 4211, 4220, 4212, 3410, 3411, 3240, 3214".split(", ")
check("Ehrlich n = 4: G row of the note's table reproduced", gs == NOTE_GRAY)
check("Ehrlich n = 4: F row of the note's table reproduced (it shows F[3..0]; F[4] = 4 throughout)", fs == NOTE_F)
EHR = list(zip(range(16), gs, fs))


def binbits(k, n):
    return [(k >> i) & 1 for i in range(n + 1)]


ok_gray = ok_cycle = ok_fix = True
note_fail_first = None
for n in range(1, 11):
    G, F = ehrlich_init(n)
    for k in range(1 << n):
        ok_gray &= val(G) == gray(k)
        B = binbits(k, n)
        Bx = lambda i: B[i] if 0 <= i <= n else 0
        for j in range(n + 1):
            # the note's invariant
            if Bx(j) == 0 and j >= 1 and Bx(j - 1) == 1:
                want_note = min(m for m in range(j + 1, n + 2) if Bx(m) == 1 or m == n + 1)
            else:
                want_note = j
            if F[j] != want_note and note_fail_first is None:
                note_fail_first = (n, k, j, F[j], want_note)
            # corrected: B[j] = 1 and B[j-1] = 0 (B[-1] = 0) -> smallest m > j with B[m] = 0
            if Bx(j) == 1 and (j == 0 or Bx(j - 1) == 0):
                want = min(m for m in range(j + 1, n + 1) if Bx(m) == 0)
            else:
                want = j
            ok_fix &= F[j] == want
        ok_gray &= F[n] == n
        ehrlich_increment(n, G, F)
    ok_cycle &= (G, F) == ehrlich_init(n)
check("Ehrlich: after k increments G = g(k) for every k < 2^n (n <= 10), F[n] = n always", ok_gray)
check("Ehrlich: the 2^n-th increment (the j = n branch) flips G[n-1] back and restores the initial state", ok_cycle)
check("the note's invariant for F (B[j] = 0, B[j-1] = 1 -> F[j] = smallest k > j with B[k] = 1) FAILS",
      note_fail_first is not None and note_fail_first[:3] == (1, 1, 0), str(note_fail_first))
G, F = ehrlich_init(4)
ehrlich_increment(4, G, F)
f1 = F[:]
ehrlich_increment(4, G, F)
check("... first failures: after 1 increment F[0] = 1 (note: 0); after 2 increments (binary 10) F[1] = 2 (note: 1)",
      f1[0] == 1 and F[1] == 2)
check("corrected invariant: if B[j] = 1 and B[j-1] = 0 (B[-1] = 0), F[j] = smallest k > j with B[k] = 0; "
      "otherwise F[j] = j (all states, n <= 10)", ok_fix)
check("in particular F[0] is always the index of the lowest 0 bit of the count (the bit to flip next)", ok_fix)

# =====================================================================================================
print("== Concept page: base-b counters and a doubling array")


def base_b_increment(D, b):
    i = 0
    c = 0
    while D[i] == b - 1:
        D[i] = 0
        c += 1
        i += 1
    D[i] += 1
    return c + 1


def digit_sum(n, b):
    s = 0
    while n:
        s += n % b
        n //= b
    return s


ok_total = ok_amort = True
for b in range(2, 11):
    D = [0] * 40
    tot = 0
    for n in range(1, 3001):
        before = Fr(sum(D), b - 1)
        c = base_b_increment(D, b)
        tot += c
        ok_amort &= c + Fr(sum(D), b - 1) - before == Fr(b, b - 1)
        ok_total &= tot * (b - 1) == b * n - digit_sum(n, b)
check("base-b counter: 0 -> n changes exactly (bn - s_b(n))/(b-1) digits (b = 2..10, n <= 3000)", ok_total)
check("base-b counter: potential (digit sum)/(b-1) makes every increment cost exactly b/(b-1) amortized", ok_amort)
D = [0] * 10
odo = sum(base_b_increment(D, 10) for _ in range(1000))
check("odometer example: counting 0 -> 1000 in decimal changes 1111 digits = 1000 + 100 + 10 + 1 < 10/9 * 1000",
      odo == 1111 and (10 * 1000 - 1) // 9 == 1111 and odo < Fr(10000, 9))
D = [0] * 10
odo999 = [base_b_increment(D, 10) for _ in range(1000)]
check("odometer example: the step 999 -> 1000 alone changes 4 digits", odo999[-1] == 4)

# doubling array
ok_amort = ok_total = ok_valid = True
size, cap = 0, 1
phi0 = 2 * size - cap
phi = phi0
tot = 0
for n in range(1, 100001):
    if size == cap:
        c = size + 1
        cap *= 2
    else:
        c = 1
    size += 1
    newphi = 2 * size - cap
    ok_amort &= c + newphi - phi == 3
    ok_valid &= newphi >= phi0
    phi = newphi
    tot += c
    ok_total &= tot <= 3 * n and tot == 3 * n - (phi - phi0)
check("doubling array: potential 2*size - capacity gives every append amortized cost exactly 3", ok_amort)
check("doubling array: the potential never drops below its initial value (valid), so n appends cost <= 3n",
      ok_valid and ok_total)

# =====================================================================================================
print("== Pages and figures")
page = read(PAGE)
cpage = read(CONCEPT)


def onpage(s, text=None):
    return s in (page if text is None else text)


check("page: the headings are the note's sections, in order",
      re.findall(r"^## (.*)$", page, re.M) ==
      ["9.1 Incrementing a binary counter", "9.2 Counting from 0 to n", "9.3 Incrementing and decrementing",
       "9.4 Gray codes", "9.5 Generalities and warnings", "Summary"])
check("page: the four subsections of 9.2", re.findall(r"^### (9\.2\.\d .*)$", page, re.M) ==
      ["9.2.1 Summation", "9.2.2 Taxation", "9.2.3 Charging", "9.2.4 Potential"])
check("page: numbers 2n - #1(n), 31 flips for 16, 1994 for 1000",
      onpage("$2n - \\#_1(n)$") and onpage("31") and onpage("1994"))
check("page: naive Gray search is O(1) amortized for increments alone, Theta(log n) when inc/dec alternate",
      onpage("$O(1)$ amortized for increments alone, but $\\Theta(\\log n)$ per operation when increments and "
             "decrements alternate"))
for P_, N_, v_ in NOTE_TRACE:
    check(f"page: double-counter trace row P = {P_}, N = {N_}, value {v_}",
          onpage(f"`{P_}` | `{N_}` | {v_}"))
for k, g, f in EHR:
    check(f"page: Ehrlich table column k = {k}: G = {g}, F = {f}", onpage(f"{g}") and onpage(f"{f}"))
check("page: from an arbitrary start v, exactly 2n + #1(v) - #1(v+n) flips",
      onpage("$2n + \\#_1(v) - \\#_1(v + n)$"))
check("page: the 1024th Increment from (0,0) flips 11 bits; Gray example k = 3, F[0] = 2, flips G[2]",
      onpage("the 1024th Increment from $(0,0)$ flips 11 bits") and onpage("at $k = 3$ (binary `0011`) $F[0] = 2$")
      and EHR[3][2][-1] == "2" and NOTE_GRAY[4] == "0110")
check("page: the note's invariant fails after the first increment (F[0] = 1) and at count 2 (F[1] = 2)",
      onpage("($B = 1$, but $F[0] = 1$, not 0) and again at count 2 ($F[1] = 2$)"))
check("concept page: odometer numbers 1111 and 10/9", onpage("1111", cpage) and onpage("10/9", cpage))


def fig_texts(name):
    html = read(os.path.join(FIGS, name + ".html"))
    return html, [re.sub(r"<[^>]+>", "", t) for t in re.findall(r"<text[^>]*>(.*?)</text>", html)]


html, ft = fig_texts("n09-charging")
nwhite = len(re.findall(r'data-b="set"', html))
nshade = len(re.findall(r'data-b="clear"', html))
narrow = len(re.findall(r'data-b="charge"', html))
tot16 = sum(len(h) for h in history[:16])
check("n09-charging: 16 stacks, 16 white (0->1) and 15 shaded (1->0) blocks, 15 charge arrows; 31 = 2*16 - 1",
      nwhite == 16 and nshade == 15 and narrow == 15 and tot16 == 31 and
      [x for x in ft if x.isdigit()][:16] == [str(k) for k in range(1, 17)])
html, ft = fig_texts("n09-gray")
cells = re.findall(r'data-g="(\w)(\d)(\d)"', html)   # k-index (hex), bit, value
check("n09-gray: the 16 columns show the 4-bit Gray code, highlighted cell = the bit just flipped, F row correct",
      len(cells) == 64 and all(int(v) == (gray(int(k, 16)) >> int(i)) & 1 for k, i, v in
                               [(c[0], c[1], c[2]) for c in cells])
      and [x for x in ft if re.fullmatch(r"\d{4}", x) and x in NOTE_F] == NOTE_F
      and len(re.findall(r'data-flip="(\w)(\d)"', html)) == 15
      and all((gray(int(k, 16)) ^ gray(int(k, 16) - 1)) == 1 << int(i)
              for k, i in re.findall(r'data-flip="(\w)(\d)"', html)))
for nm in ("n09-charging", "n09-gray"):
    h = read(os.path.join(FIGS, nm + ".html"))
    check(f"{nm}: inlined on the page and colored only through currentColor / CSS variables",
          f"<!-- fig:{nm} -->\n{h.strip()}" in page and not re.search(r'(fill|stroke)="#[0-9a-fA-F]{3,6}"', h))

allal = []
for root_, _, files in os.walk(os.path.join(ROOT, "content")):
    for fn in files:
        if fn.endswith(".md"):
            m = re.search(r"^aliases: \[(.*)\]$", read(os.path.join(root_, fn)), re.M)
            if m:
                allal += [a.strip().strip('"').lower() for a in m.group(1).split(",")]
dups = sorted({a for a in allal if allal.count(a) > 1})
check("aliases are unique site-wide (case-insensitive)", not dups, str(dups))

print()
if FAIL:
    print(f"{len(FAIL)} FAILED:", *FAIL, sep="\n  ")
    sys.exit(1)
print("ALL OK")
