#!/usr/bin/env python3
"""Checks for content/4-lecture-notes/01-discrete-probability.md (Erickson, Director's Cut 1, "Discrete Probability")
and for the concept page content/concepts/discrete-probability.md.

Probabilities and expectations are computed EXACTLY with Fractions by enumerating sample spaces (36 dice outcomes,
all coin sequences of a given length, all n^m purchase sequences, all n! permutations, all random-choice sequences of
the shuffles). Infinite sums (geometric tails, coupon-collector expectation) are checked against closed forms; only the
rejection-sampling FisherYates and the full 52-card deck are simulated, with stated tolerances."""
import itertools
import math
import os
import random
import sys
from collections import Counter
from fractions import Fraction as F
from functools import lru_cache

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import figs_n01 as FIG  # noqa: E402

FAIL = []


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAIL.append(name)


rng = random.Random(374)


_H = [F(0)]


def H(n):
    while len(_H) <= n:
        _H.append(_H[-1] + F(1, len(_H)))
    return _H[n]


# =====================================================================================================
# 1.1 Discrete probability spaces
# =====================================================================================================
loaded = {w: F(w, 21) for w in range(1, 7)}
check("1.1 loaded die Pr[w] = w/21 is a probability space (sums to 1), Pr[4] = 4/21",
      sum(loaded.values()) == 1 and loaded[4] == F(4, 21))

OMEGA = [(r, b) for r in range(1, 7) for b in range(1, 7)]


def P(pred):
    return F(sum(1 for w in OMEGA if pred(w)), 36)


def Pc(a, b):
    return P(lambda w: a(w) and b(w)) / P(b)


red5 = lambda w: w[0] == 5
blue5 = lambda w: w[1] == 5
red6 = lambda w: w[0] == 6
two5 = lambda w: red5(w) and blue5(w)
least1 = lambda w: red5(w) or blue5(w)
most1 = lambda w: not two5(w)
no5 = lambda w: not least1(w)
exactly1 = lambda w: red5(w) != blue5(w)
b_imp_r = lambda w: (not blue5(w)) or red5(w)
r_imp_b = lambda w: (not red5(w)) or blue5(w)
total = lambda s: (lambda w: w[0] + w[1] == s)

vals = [
    ("two 5s", P(two5), F(1, 36)), ("total 6", P(total(6)), F(5, 36)), ("red 5", P(red5), F(1, 6)),
    ("at least one 5", P(least1), F(11, 36)), ("red < blue", P(lambda w: w[0] < w[1]), F(5, 12)),
    ("at most one 5", P(most1), F(35, 36)), ("no 5s", P(no5), F(25, 36)), ("exactly one 5", P(exactly1), F(5, 18)),
    ("blue 5 => red 5", P(b_imp_r), F(31, 36)),
]
for name, got, want in vals:
    check(f"1.1 two dice: Pr[{name}] = {want}", got == want, got)
check("1.1 red < blue has 15 outcomes", sum(1 for w in OMEGA if w[0] < w[1]) == 15)
check("1.1 Pr[at most one 5] = 1 - Pr[two 5s], Pr[no 5s] = 1 - Pr[at least one 5]",
      P(most1) == 1 - P(two5) and P(no5) == 1 - P(least1))

conds = [
    ("blue 5 | red 5", Pc(blue5, red5), F(1, 6)), ("two 5s | red 5", Pc(two5, red5), F(1, 6)),
    ("at most one 5 | red 5", Pc(most1, red5), F(5, 6)), ("exactly one 5 | red 5", Pc(exactly1, red5), F(5, 6)),
    ("at least one 5 | at most one 5", Pc(least1, most1), F(2, 7)),
    ("at most one 5 | at least one 5", Pc(most1, least1), F(10, 11)),
    ("red 5 | at least one 5", Pc(red5, least1), F(6, 11)), ("red 5 | at most one 5", Pc(red5, most1), F(1, 7)),
    ("blue 5 | blue5=>red5", Pc(blue5, b_imp_r), F(1, 31)), ("red 5 | blue5=>red5", Pc(red5, b_imp_r), F(6, 31)),
    ("blue5=>red5 | blue 5", Pc(b_imp_r, blue5), F(1, 6)), ("blue5=>red5 | red 5", Pc(b_imp_r, red5), F(1)),
    ("blue5=>red5 | red5=>blue5", Pc(b_imp_r, r_imp_b), F(26, 31)), ("red 5 | total 6", Pc(red5, total(6)), F(1, 5)),
]
for name, got, want in conds:
    check(f"1.1.2 Pr[{name}] = {want}", got == want, got)

disj = lambda a, b: not any(a(w) and b(w) for w in OMEGA)
check("1.1.2 ERROR in the note (p. 3): 'red 5', 'blue 5', 'total 5' are NOT pairwise disjoint — (5,5) is in both "
      "red 5 and blue 5; red 5 and blue 5 are each disjoint from total 5",
      not disj(red5, blue5) and disj(red5, total(5)) and disj(blue5, total(5)))
check("1.1.2 corrected example: 'red 5', 'red 6', 'total 5' are pairwise disjoint",
      disj(red5, red6) and disj(red5, total(5)) and disj(red6, total(5)))
indep = lambda a, b: P(lambda w: a(w) and b(w)) == P(a) * P(b)
check("1.1.2 red 5 and blue 5 are independent; red 5 and total 5 are not",
      indep(red5, blue5) and not indep(red5, total(5)))
t7 = total(7)
check("1.1.2 red 5, blue 5, total 7: pairwise independent but not mutually independent",
      indep(red5, blue5) and indep(red5, t7) and indep(blue5, t7)
      and P(lambda w: red5(w) and blue5(w) and t7(w)) == 0 != P(red5) * P(blue5) * P(t7))
bart = {"rock": F(1), "paper": F(0), "scissors": F(0)}
check("1.1.2 Bart: 'plays paper' and 'does not play rock' are not disjoint, yet Pr[both] = 0",
      bart["paper"] == 0 and "paper" in {"paper", "scissors"})


# ---- identities on random finite spaces
def random_space(m):
    ws = [rng.randint(1, 9) for _ in range(m)]
    s = sum(ws)
    return [F(x, s) for x in ws]


ok_ub = ok_ie = ok_du = ok_bayes = True
for trial in range(200):
    m = rng.randint(2, 9)
    pr = random_space(m)
    n = rng.randint(1, 4)
    ev = [frozenset(i for i in range(m) if rng.random() < 0.5) for _ in range(n)]
    Pe = lambda S: sum((pr[i] for i in S), F(0))
    union = frozenset().union(*ev)
    ok_ub &= Pe(union) <= sum(Pe(A) for A in ev)
    ie = 1 - sum(((-1) ** len(I)) * Pe(frozenset(range(m)).intersection(*[ev[i] for i in I]))
                 for k in range(0, n + 1) for I in itertools.combinations(range(n), k))
    ok_ie &= ie == Pe(union)
    # disjoint: assign each atom to at most one event
    lab = [rng.randint(-1, n - 1) for _ in range(m)]
    dev = [frozenset(i for i in range(m) if lab[i] == k) for k in range(n)]
    ok_du &= Pe(frozenset().union(*dev)) == sum(Pe(A) for A in dev)
    A, B = ev[0], ev[-1]
    if Pe(A) > 0 and Pe(B) > 0:
        pab = Pe(A & B)
        ok_bayes &= (pab / Pe(B)) * Pe(B) == (pab / Pe(A)) * Pe(A) == pab
        ok_bayes &= (pab / Pe(B)) / Pe(A) == pab / (Pe(A) * Pe(B)) == (pab / Pe(A)) / Pe(B)
ok_std = True
for trial in range(200):
    m = rng.randint(2, 8)
    pr = random_space(m)
    n = rng.randint(1, 4)
    ev = [frozenset(i for i in range(m) if rng.random() < 0.5) for _ in range(n)]
    Pe = lambda S: sum((pr[i] for i in S), F(0))
    std = sum(((-1) ** (k + 1)) * Pe(frozenset(range(m)).intersection(*[ev[i] for i in I]))
              for k in range(1, n + 1) for I in itertools.combinations(range(n), k))
    ok_std &= std == Pe(frozenset().union(*ev))
check("1.1.3 inclusion-exclusion, standard form: sum over non-empty I of (-1)^(|I|+1) Pr[AND_I A_i]", ok_std)
check("1.1.3 union bound on 200 random finite spaces and events", ok_ub)
check("1.1.3 inclusion-exclusion as the note writes it, 1 - sum over ALL I ⊆ [1..n] (empty I gives Pr[Ω] = 1)", ok_ie)
check("1.1.3 disjoint union: equality", ok_du)
check("1.1.3 Bayes: Pr[A|B]Pr[B] = Pr[A∧B] = Pr[B|A]Pr[A], and Pr[A|B]/Pr[A] = Pr[A∧B]/(Pr[A]Pr[B]) = Pr[B|A]/Pr[B]",
      ok_bayes)
a, b = red5, total(6)
lhs = Pc(a, b) / P(a)
check("1.1.3 ERROR in the note (p. 5): Pr[A|B]/Pr[A] = Pr[A∧B] is false; with A = red 5, B = total 6 the left side is "
      "6/5 and Pr[A∧B] = 1/36; correct middle term Pr[A∧B]/(Pr[A]Pr[B]) = 6/5",
      lhs == F(6, 5) and P(lambda w: a(w) and b(w)) == F(1, 36) and lhs == F(1, 36) / (P(a) * P(b)))
ok = True
for trial in range(100):
    n = rng.randint(1, 5)
    ps = [F(rng.randint(0, 6), 6) for _ in range(n)]
    # product space of n independent bits; A_i = bit i is 1
    pu = F(0)
    for bits in itertools.product((0, 1), repeat=n):
        w = F(1)
        for bit, p in zip(bits, ps):
            w *= p if bit else 1 - p
        if any(bits):
            pu += w
    prod = F(1)
    for p in ps:
        prod *= 1 - p
    ok &= pu == 1 - prod
    if n >= 2:
        ok &= (ps[0] + ps[1] - ps[0] * ps[1]) == 1 - (1 - ps[0]) * (1 - ps[1])
check("1.1.3 independent union: Pr[A_1 ∨ ... ∨ A_n] = 1 - prod (1 - Pr[A_i]) for mutually independent events", ok)
# reviewer (R25): which side of the union bound counts what; the note (p. 4) swaps left and right
ok = True
for trial in range(200):
    m = rng.randint(2, 9)
    pr = random_space(m)
    ev = [frozenset(i for i in range(m) if rng.random() < 0.5) for _ in range(rng.randint(2, 4))]
    union = frozenset().union(*ev)
    left = sum((pr[i] for i in union), F(0))
    right = sum((pr[i] * sum(1 for A in ev if i in A) for i in range(m)), F(0))
    ok &= left == sum((pr[i] for i in range(m) if any(i in A for A in ev)), F(0))   # each atom once
    ok &= right == sum(sum((pr[i] for i in A), F(0)) for A in ev)                     # once per event
check("1.1.3 ERROR in the note (p. 4): the LEFT side Pr[∨A_i] counts each atom of the union once, the RIGHT side "
      "sum_i Pr[A_i] counts it once per event containing it (200 random spaces)", ok)
# reviewer (R25): mutual independence must hold for every finite subfamily, not only the whole family
A3, B3, C3 = (lambda w: w[0] <= 3), (lambda w: w[0] in (3, 4, 5)), total(9)
check("1.1.2 ERROR in the note (p. 4): the product rule for the whole family only is too weak — 'red <= 3', "
      "'red in {3,4,5}', 'total 9': Pr[all three] = 1/36 = 1/2·1/2·1/9, yet the first two are dependent (1/6 ≠ 1/4)",
      P(lambda w: A3(w) and B3(w) and C3(w)) == F(1, 36) == P(A3) * P(B3) * P(C3)
      and P(A3) == P(B3) == F(1, 2) and P(C3) == F(1, 9) and not indep(A3, B3)
      and P(lambda w: A3(w) and B3(w)) == F(1, 6))

# =====================================================================================================
# 1.2 Random variables and expectation (red die R, blue die B, S = R+B, R' = 7-R)
# =====================================================================================================
R = lambda w: w[0]
Bv = lambda w: w[1]
S = lambda w: w[0] + w[1]
Rb = lambda w: 7 - w[0]


def E(f, cond=lambda w: True):
    ws = [w for w in OMEGA if cond(w)]
    return F(sum(f(w) for w in ws), len(ws))


def indep_rv(X, Y):
    for x in set(map(X, OMEGA)):
        for y in set(map(Y, OMEGA)):
            if P(lambda w: X(w) == x and Y(w) == y) != P(lambda w: X(w) == x) * P(lambda w: Y(w) == y):
                return False
    return True


names = {"R": R, "B": Bv, "S": S, "R'": Rb}
pairs_ind = sorted(f"{a}-{b}" for a, b in itertools.combinations(names, 2) if indep_rv(names[a], names[b]))
check("1.2.3 of R, B, S = R+B, R' = 7-R exactly the pairs (R,B) and (R',B) are independent", pairs_ind == ["B-R'", "R-B"],
      pairs_ind)
ex = [
    ("E[R] = E[B] = E[R'] = 7/2", E(R) == E(Bv) == E(Rb) == F(7, 2)),
    ("E[R+B] = 7", E(S) == 7),
    ("E[R+R'] = 7 (R + R' = 7 always)", E(lambda w: R(w) + Rb(w)) == 7 and all(R(w) + Rb(w) == 7 for w in OMEGA)),
    ("E[R+B+R'] = 21/2", E(lambda w: R(w) + Bv(w) + Rb(w)) == F(21, 2)),
    ("E[RB] = 49/4 = E[R]E[B]", E(lambda w: R(w) * Bv(w)) == F(49, 4) == E(R) * E(Bv)),
    ("E[R R'] = (1·6+2·5+3·4)/3 = 28/3 ≠ E[R]E[R'] = 49/4",
     E(lambda w: R(w) * Rb(w)) == F(1 * 6 + 2 * 5 + 3 * 4, 3) == F(28, 3) != E(R) * E(Rb)),
    ("E[R^2] = 91/6", E(lambda w: R(w) ** 2) == F(91, 6)),
    ("E[(R+B)^2] = E[R^2] + 2E[RB] + E[B^2] = 329/6", E(lambda w: S(w) ** 2) == F(91, 6) * 2 + 2 * F(49, 4) == F(329, 6)),
    ("E[R+B | R=6] = 6 + E[B] = 19/2", E(S, lambda w: R(w) == 6) == F(19, 2)),
    ("E[R | R+B=6] = 3", E(R, lambda w: S(w) == 6) == 3),
    ("E[R^2 | R+B=6] = 11", E(lambda w: R(w) ** 2, lambda w: S(w) == 6) == 11),
    ("E[R+B | RB=6] = 6", E(S, lambda w: R(w) * Bv(w) == 6) == 6),
    ("E[RB | R+B=6] = 7", E(lambda w: R(w) * Bv(w), lambda w: S(w) == 6) == 7),
]
for name, cond in ex:
    check("1.2.3 " + name, cond)

# expectation of integer random variables: the note's tail formula vs the correct one
die = {x: F(1, 6) for x in range(1, 7)}


def tail_note(d):
    lo, hi = min(d), max(d)
    return (sum(sum(p for v, p in d.items() if v >= x) for x in range(0, hi + 1))
            - sum(sum(p for v, p in d.items() if v <= x) for x in range(lo, 1)))


def tail_fixed(d):
    lo, hi = min(d), max(d)
    return (sum(sum(p for v, p in d.items() if v >= x) for x in range(1, hi + 1))
            - sum(sum(p for v, p in d.items() if v <= x) for x in range(lo, 0)))


mean = lambda d: sum(v * p for v, p in d.items())
check("1.2.2 ERROR in the note (p. 6): sum_(x>=0) Pr[X>=x] - sum_(x<=0) Pr[X<=x] gives 9/2 for a fair die, not 7/2",
      tail_note(die) == F(9, 2) and mean(die) == F(7, 2))
ok = True
for trial in range(300):
    vs = rng.sample(range(-6, 7), rng.randint(1, 6))
    ws = [rng.randint(1, 5) for _ in vs]
    d = {v: F(w, sum(ws)) for v, w in zip(vs, ws)}
    ok &= tail_fixed(d) == mean(d)
    ok &= tail_note(d) - mean(d) == sum(p for v, p in d.items() if v > 0) - sum(p for v, p in d.items() if v < 0)
check("1.2.2 corrected tail formula E[X] = sum_(x>=1) Pr[X>=x] - sum_(x<=-1) Pr[X<=x] on 300 random integer "
      "distributions; the note's version is off by Pr[X>0] - Pr[X<0]", ok)
# total expectation, independence and products
ok = True
ok &= E(R) == E(R, red5) * P(red5) + E(R, lambda w: not red5(w)) * (1 - P(red5))
ok &= E(R) == sum(E(R, lambda w, y=y: S(w) == y) * P(lambda w, y=y: S(w) == y) for y in range(2, 13))
check("1.2.2 E[X] = E[X|A]Pr[A] + E[X|¬A]Pr[¬A] and E[X] = sum_y E[X|Y=y]Pr[Y=y] (X = R, A = red 5, Y = S)", ok)
X3 = {-1: F(1, 3), 0: F(1, 3), 1: F(1, 3)}
EXY = sum(p * x * x * x for x, p in X3.items())
EX = sum(p * x for x, p in X3.items())
EY = sum(p * x * x for x, p in X3.items())
check("1.2.2 E[XY] = E[X]E[Y] does not imply independence: X uniform on {-1,0,1}, Y = X^2 (both sides 0, but "
      "Pr[X=0 ∧ Y=1] = 0 ≠ 1/3 · 2/3)", EXY == EX * EY == 0 and F(0) != F(1, 3) * F(2, 3))
check("1.2.2 'always well-defined' fails on infinite spaces: Pr[X = 2^k] = 2^-k (k >= 1) sums to 1 but its "
      "expectation's partial sums are 1, 2, 3, ... (diverge)",
      sum(F(1, 2 ** k) for k in range(1, 60)) == 1 - F(1, 2 ** 59)
      and [sum(2 ** k * F(1, 2 ** k) for k in range(1, K + 1)) for K in (1, 2, 3)] == [1, 2, 3])
ok = True
for trial in range(100):
    # dependent X1..X3 on a random space; random weights
    m = rng.randint(2, 8)
    pr = random_space(m)
    Xs = [[rng.randint(-5, 5) for _ in range(m)] for _ in range(3)]
    al = [F(rng.randint(-4, 4), rng.randint(1, 3)) for _ in range(3)]
    lhs = sum(pr[i] * sum(al[k] * Xs[k][i] for k in range(3)) for i in range(m))
    rhs = sum(al[k] * sum(pr[i] * Xs[k][i] for i in range(m)) for k in range(3))
    ok &= lhs == rhs
check("1.2.2 linearity of expectation for arbitrary (dependent) variables and coefficients, 100 random instances", ok)

# =====================================================================================================
# 1.3 Common distributions
# =====================================================================================================
ok = True
for n in range(1, 11):
    ok &= sum(F(x, n) for x in range(1, n + 1)) == F(n + 1, 2)
check("1.3 uniform on [1..n]: E = (n+1)/2", ok)
ok = True
for p in (F(0), F(1, 3), F(2, 5), F(1, 2), F(1)):
    ok &= 0 * (1 - p) + 1 * p == p
    for n in range(0, 11):
        pmf = {x: math.comb(n, x) * p ** x * (1 - p) ** (n - x) for x in range(n + 1)}
        ok &= sum(pmf.values()) == 1 and sum(x * q for x, q in pmf.items()) == n * p
        # sum of n independent Bernoulli(p)
        conv = Counter({0: F(1)})
        for _ in range(n):
            nxt = Counter()
            for v, q in conv.items():
                nxt[v] += q * (1 - p)
                nxt[v + 1] += q * p
            conv = nxt
        ok &= all(conv[x] == pmf[x] for x in pmf)
check("1.3 Bernoulli mean p; binomial pmf sums to 1, mean np, equals the sum of n independent Bernoulli(p) "
      "(exact, n <= 10)", ok)
ok = True
for p in (F(1, 3), F(1, 2), F(9, 10), F(1, 10)):
    N = 400
    geo = [(1 - p) ** x * p for x in range(N)]
    ok &= sum(geo) == 1 - (1 - p) ** N
    pf = float(p)
    mean_f = math.fsum(x * (1 - pf) ** x * pf for x in range(20000))
    ok &= abs(mean_f - (1 - pf) / pf) < 1e-9
    for n in range(1, 5):
        conv = [F(1)] + [F(0)] * 40
        for _ in range(n):
            conv = [sum(conv[y] * geo[x - y] for y in range(x + 1)) for x in range(41)]
        nb = [math.comb(n + x - 1, x) * (1 - p) ** x * p ** n for x in range(41)]
        ok &= conv == nb
        mean_nb = math.fsum(math.comb(n + x - 1, x) * (1 - pf) ** x * pf ** n * x for x in range(6000))
        ok &= abs(mean_nb - n * (1 - pf) / pf) < 1e-7
check("1.3 geometric pmf (1-p)^x p sums to 1 (exact partial sums 1-(1-p)^N), mean (1-p)/p; negative binomial pmf = "
      "convolution of n geometrics (exact, x <= 40), mean n(1-p)/p", ok)
check("1.3 trials up to and including the first success = 1 + geometric: mean 1 + (1-p)/p = 1/p",
      all(1 + (1 - p) / p == 1 / p for p in (F(1, 3), F(2, 7), F(1))))

# =====================================================================================================
# 1.4 Coin flips
# =====================================================================================================
for p in (F(1, 3), F(1, 2), F(1, 5), F(7, 10)):
    q = 1 - p
    # enumerate all flip sequences of up to K rounds
    K = 7
    out1 = out0 = F(0)
    flips = F(0)
    for k in range(1, K + 1):
        # rounds 1..k-1 repeat (xx equal), round k differs
        rep = (p * p + q * q) ** (k - 1)
        out1 += rep * p * q
        out0 += rep * q * p
        flips += rep * 2 * p * q * 2 * k
    # brute force over all sequences of 2K flips (as bit strings) to confirm the round structure
    tot1 = tot0 = F(0)
    for bits in itertools.product((0, 1), repeat=2 * 5):
        w = F(1)
        for bt in bits:
            w *= p if bt else q
        for r in range(5):
            x, y = bits[2 * r], bits[2 * r + 1]
            if x != y:
                if x == 1:
                    tot1 += w
                else:
                    tot0 += w
                break
    ok = out1 == out0 and tot1 == tot0 and tot1 == sum((p * p + q * q) ** (k - 1) * p * q for k in range(1, 6))
    # E[T] = 1/(pq): partial sums approach it, and the equation E = 2·2pq + (2+E)(1-2pq) has that solution
    Et = 1 / (p * q)
    ok &= Et == 2 * 2 * p * q + (2 + Et) * (1 - 2 * p * q)
    pf, qf = float(p), float(q)
    series = math.fsum(2 * k * (1 - 2 * pf * qf) ** (k - 1) * 2 * pf * qf for k in range(1, 5000))
    ok &= abs(series - 1 / (pf * qf)) < 1e-9
    ok &= 1 / (2 * p * q) - 1 == (1 - 2 * p * q) / (2 * p * q)        # unsuccessful rounds: geometric mean
    check(f"1.4.1 VonNeumannCoin, p = {p}: returns 1 and 0 with equal probability in every round (exact, all 2^10 "
          f"sequences), E[T] = 1/(pq) = {Et}", ok)
check("1.4.1 p = 1/3: E[T] = 9/2 flips; fair coin: 4", 1 / (F(1, 3) * F(2, 3)) == F(9, 2) and 1 / F(1, 4) == 4)
# simulation sanity: the actual recursive algorithm
sim = random.Random(1)
cnt = 0
ones = 0
runs = 200000
for _ in range(runs):
    while True:
        x = sim.random() < 0.3
        y = sim.random() < 0.3
        cnt += 2
        if x != y:
            ones += x
            break
check("1.4.1 simulation of VonNeumannCoin with p = 0.3 (200,000 runs): fraction of 1s within 0.005 of 1/2, mean flips "
      "within 1% of 1/0.21", abs(ones / runs - 0.5) < 0.005 and abs(cnt / runs / (1 / 0.21) - 1) < 0.01,
      f"{ones / runs:.4f}, {cnt / runs:.3f}")
p, q = F(1, 3), F(2, 3)          # Pr[BiasedCoin(1/3) = 1] = 1/3, as in the note (heads = 1, p = Pr[heads])
pr = {(x, y): (p if x else q) * (p if y else q) for x in (0, 1) for y in (0, 1)}
check("1.4.2 with Pr[1] = 1/3: Pr[x≠y] = 4/9 = Pr[x=y=0], Pr[x=y=1] = 1/9",
      pr[(0, 1)] + pr[(1, 0)] == F(4, 9) == pr[(0, 0)] and pr[(1, 1)] == F(1, 9))
printed = pr[(1, 1)] / (pr[(1, 1)] + pr[(0, 1)] + pr[(1, 0)])
fixed = pr[(0, 0)] / (pr[(0, 0)] + pr[(0, 1)] + pr[(1, 0)])
check("1.4.2 ERROR in the note (p. 11): the pseudocode returns 1 on x = y = 1 (labeled 4/9, really 1/9) and would "
      "output 1 with probability 1/5; returning 1 on x = y = 0 (as the text says) gives exactly 1/2",
      printed == F(1, 5) and fixed == F(1, 2))
Et = F(2) / (1 - pr[(1, 1)])
check("1.4.2 corrected FairCoin: E[T] = 2 + (1/9)E[T] gives 9/4, half of von Neumann's 9/2",
      Et == 2 + F(1, 9) * Et == F(9, 4) and F(9, 2) / Et == 2)

# =====================================================================================================
# 1.5 Pokemon collecting (coupon collector)
# =====================================================================================================
ok = True
for n in range(1, 6):
    for m in range(0, 6):
        tot = F(0)
        for seq in itertools.product(range(n), repeat=m):
            tot += len(set(seq))
        tot /= n ** m
        ok &= tot == n * (1 - F(n - 1, n) ** m)
check("1.5.1 after m purchases the expected number of distinct types is n(1 - (1-1/n)^m) (exact over all n^m "
      "sequences, n, m <= 5)", ok)
c1 = 1 - math.exp(-1)
check("1.5.1 (1-1/n)^n -> 1/e; 1 - 1/e = 0.63212", round(c1, 5) == 0.63212 and abs((1 - 1 / 10 ** 6) ** 10 ** 6 - math.exp(-1)) < 1e-6)
fr = [1 - math.exp(-c) for c in (2, 3, 4)]
check("1.5.1 after 2n, 3n, 4n cards: about 86%, 95%, 98% (1 - e^-c = 0.8647, 0.9502, 0.9817)",
      [round(100 * x) for x in fr] == [86, 95, 98], [round(x, 4) for x in fr])
check("1.5.1 the same for n = 150 exactly: 1-(149/150)^(cn) = 0.6334, 0.8656, 0.9507, 0.9819 (c = 1, 2, 3, 4)",
      [round(1 - (149 / 150) ** (150 * c), 4) for c in (1, 2, 3, 4)] == [0.6334, 0.8656, 0.9507, 0.9819])
ok = True
for n in range(1, 41):
    # E[T] = sum_{t>=0} Pr[T > t], Pr[T > t] by inclusion-exclusion; sum_t (1-k/n)^t = n/k
    ie = sum(((-1) ** (k + 1)) * math.comb(n, k) * F(n, k) for k in range(1, n + 1))
    ok &= ie == n * H(n) == sum(F(n, n - i + 1) for i in range(1, n + 1))
check("1.5.2 E[T(n)] = sum_i n/(n-i+1) = nH_n, confirmed independently by inclusion-exclusion "
      "sum_k (-1)^(k+1) C(n,k) n/k, n <= 40", ok)
# exact distribution of T for n = 3 by enumerating every purchase sequence of length <= 11
n = 3
pt = Counter()
for L in range(1, 12):
    for seq in itertools.product(range(n), repeat=L):
        if len(set(seq)) == n and len(set(seq[:-1])) == n - 1:
            pt[L] += F(1, n ** L)
# exact phase-model distribution of T for n = 3: convolution of geometric waits with success probs 1, 2/3, 1/3
ph = Counter({0: F(1)})
for s in (F(1), F(2, 3), F(1, 3)):
    nxt = Counter()
    for v, q in ph.items():
        for k in range(1, 13):
            nxt[v + k] += q * (1 - s) ** (k - 1) * s
    ph = nxt
check("1.5.2 n = 3: the exact distribution of T from all purchase sequences equals the sum of independent geometric "
      "phases (success probabilities 3/3, 2/3, 1/3), t <= 11", all(pt[t] == ph[t] for t in range(1, 12)))
sim = random.Random(2)
tot = 0
R10 = 100000
for _ in range(R10):
    seen = set()
    t = 0
    while len(seen) < 10:
        seen.add(sim.randrange(10))
        t += 1
    tot += t
check("1.5.2 simulation, n = 10 (100,000 runs): mean within 1% of 10·H_10 = 7381/252 ≈ 29.29",
      abs(tot / R10 / float(10 * H(10)) - 1) < 0.01 and 10 * H(10) == F(7381, 252), round(tot / R10, 3))
ok = all(math.log(n + 1) <= float(H(n)) <= math.log(n) + 1 for n in range(1, 2001))
Hf = 0.0
for n in range(1, 100001):
    Hf += 1.0 / n
    if n > 2000 and not (math.log(n + 1) <= Hf <= math.log(n) + 1):
        ok = False
check("1.5.2 ln(n+1) <= H_n <= ln(n) + 1 for n <= 100,000", ok)
v150 = 150 * H(150)
Hb = math.fsum(1.0 / k for k in range(1, 9185))
check("1.5.2 150·H_150 ≈ 838.67709 and 9184·H_9184 ≈ 89107.65186",
      f"{float(v150):.5f}" == "838.67709" and f"{9184 * Hb:.5f}" == "89107.65186", f"{float(v150):.5f}, {9184 * Hb:.5f}")
ok = all(abs(float(n * (H(n) - H(n // 2))) / (n * math.log(2)) - 1) < 0.03 for n in range(40, 2001, 40))
check("1.5.2 trap: the first n/2 types take n(H_n - H_(n/2)) ≈ n ln 2 purchases (within 3% for n >= 40)", ok)
cn = FIG.COUPON_N
bars = [F(cn, cn - i + 1) for i in range(1, cn + 1)]
check("figure coupon: bars n/(n-i+1) for n = 10 sum to 7381/252 ≈ 29.29; first five ≈ 6.46; last three ≈ 18.33",
      sum(bars) == F(7381, 252) and round(float(sum(bars[:5])), 2) == 6.46 and round(float(sum(bars[-3:])), 2) == 18.33)

# =====================================================================================================
# 1.6 Random permutations
# =====================================================================================================
def draw_lots(choices, L):
    L = list(L)
    R = []
    for c in choices:              # c = index (1-based) of the lot drawn from the remaining bag
        R.append(L.pop(c - 1))
    return tuple(R)


def selection_shuffle(choices, A):
    A = list(A)
    n = len(A)
    for i, r in zip(range(n, 0, -1), choices):
        A[i - 1], A[r - 1] = A[r - 1], A[i - 1]
    return tuple(A)


def insertion_shuffle(choices, A):
    A = list(A)
    n = len(A)
    for i, r in zip(range(1, n + 1), choices):
        A[i - 1], A[r - 1] = A[r - 1], A[i - 1]
    return tuple(A)


for n in range(1, 8):
    base = tuple(range(1, n + 1))
    down = list(itertools.product(*[range(1, i + 1) for i in range(n, 0, -1)]))   # Random(n), ..., Random(1)
    up = list(itertools.product(*[range(1, i + 1) for i in range(1, n + 1)]))     # Random(1), ..., Random(n)
    all_perms = set(itertools.permutations(base))
    dl = Counter(draw_lots(c, base) for c in down)
    ss = Counter(selection_shuffle(c, base) for c in down)
    ins = Counter(insertion_shuffle(c, base) for c in up)
    check(f"1.6 n = {n}: DrawLots, SelectionShuffle and InsertionShuffle map their n! = {math.factorial(n)} equally likely "
          f"choice sequences one-to-one onto the permutations",
          all(set(c) == all_perms and set(c.values()) == {1} for c in (dl, ss, ins)))
# InsertionShuffle: prefix uniformly shuffled after each iteration
ok = True
n = 5
for i in range(1, n + 1):
    cnt = Counter()
    for c in itertools.product(*[range(1, k + 1) for k in range(1, i + 1)]):
        A = list(range(1, n + 1))
        for k, r in zip(range(1, i + 1), c):
            A[k - 1], A[r - 1] = A[r - 1], A[k - 1]
        cnt[tuple(A[:i])] += 1
    ok &= set(cnt) == set(itertools.permutations(range(1, i + 1))) and len(set(cnt.values())) == 1
check("1.6 InsertionShuffle: after iteration i the prefix A[1..i] is a uniform permutation of the first i items (n = 5)",
      ok)
# SelectionShuffle as lot-casting: after iteration i, A[i..n] holds the drawn lots (in order of drawing, right to left)
ok = True
for c in itertools.product(*[range(1, i + 1) for i in range(5, 0, -1)]):
    A = list("ABCDE")
    bag = list("ABCDE")
    for i, r in zip(range(5, 0, -1), c):
        A[i - 1], A[r - 1] = A[r - 1], A[i - 1]
        ok &= sorted(A[:i - 1]) == sorted(set("ABCDE") - set(A[i - 1:]))
check("1.6 SelectionShuffle: after each iteration the suffix A[i..n] is the set of chosen lots and the prefix the "
      "unchosen ones", ok)
tr = FIG.selection_shuffle_trace(FIG.SHUFFLE_START, FIG.SHUFFLE_CHOICES)
check("figure shuffle: choices 2, 4, 1, 1, 1 turn A B C D E into A E C D B, A E C D B, C E A D B, E C A D B, E C A D B",
      ["".join(s) for _, _, s in tr] == ["AECDB", "AECDB", "CEADB", "ECADB", "ECADB"]
      and tuple(tr[-1][2]) == selection_shuffle(FIG.SHUFFLE_CHOICES, "ABCDE"))


def fisher_yates(L, rnd):
    n = len(L)
    chosen = [False] * (n + 1)
    R = [None] * (n + 1)
    calls = 0
    for i in range(n, 0, -1):
        while True:
            r = rnd(n)
            calls += 1
            if not chosen[r]:
                break
        R[i] = L[r - 1]
        chosen[r] = True
    return tuple(R[1:]), calls


sim = random.Random(3)
rnd = lambda k: sim.randint(1, k)
tot = 0
RUNS = 100000
for _ in range(RUNS):
    tot += fisher_yates(list(range(8)), rnd)[1]
check("1.6 FisherYates (rejection version), n = 8, 100,000 runs: mean number of Random calls within 1% of "
      "8·H_8 = 761/35 ≈ 21.74", abs(tot / RUNS / float(8 * H(8)) - 1) < 0.01 and 8 * H(8) == F(761, 35),
      round(tot / RUNS, 3))
cnt = Counter(fisher_yates(list(range(4)), rnd)[0] for _ in range(240000))
check("1.6 FisherYates output, n = 4, 240,000 runs: all 24 permutations, each within 4% of 10,000",
      len(cnt) == 24 and all(abs(v / 10000 - 1) < 0.04 for v in cnt.values()), (min(cnt.values()), max(cnt.values())))

# =====================================================================================================
# 1.7 Properties of random permutations (unfinished in the note)
# =====================================================================================================
n = 6
perms = list(itertools.permutations(range(1, n + 1)))
ok = True
for idx in [(1, 4), (0, 2, 5), (3,), (0, 1, 2, 3)]:
    c = Counter(tuple(p[i] for i in idx) for p in perms)        # ordered tuple of values at those indices
    ok &= len(set(c.values())) == 1 and len(c) == math.perm(n, len(idx))
for vals_ in [(2, 5), (1, 3, 6)]:
    c = Counter(tuple(p.index(v) for v in vals_) for p in perms)
    ok &= len(set(c.values())) == 1 and len(c) == math.perm(n, len(vals_))
check("1.7 n = 6: the values at any fixed set of positions (as an ordered tuple) are uniform over all ordered "
      "choices — so the set is uniform and its order is uniform and independent; same for the positions of fixed values",
      ok)
face = [(r, s) for r in "JQK" for s in "SHDC"]
tot = F(0)
cntt = 0
for tup in itertools.permutations(face, 5):
    tot += sum(1 for c in tup if c[1] == "H")
    cntt += 1
check("1.7 expected hearts among the first 5 face cards = 5·(3/12) = 5/4 (exact over all 95,040 ordered 5-tuples)",
      tot / cntt == F(5, 4) and cntt == 95040)
deck = [(r, s) for r in range(1, 14) for s in "SHDC"]
sim = random.Random(4)
hs = 0
RUNS = 100000
for _ in range(RUNS):
    sim.shuffle(deck)
    fc = [c for c in deck if c[0] >= 11][:5]
    hs += sum(1 for c in fc if c[1] == "H")
check("1.7 simulation with full 52-card decks (100,000 shuffles): mean within 1.5% of 5/4",
      abs(hs / RUNS / 1.25 - 1) < 0.015, round(hs / RUNS, 4))


# ---- fixed points and cycles (page extra + concept page example)
def cycles(p):
    n = len(p)
    seen = [False] * n
    c = 0
    for i in range(n):
        if not seen[i]:
            c += 1
            j = i
            while not seen[j]:
                seen[j] = True
                j = p[j] - 1
    return c


ok_fp = ok_cy = True
for n in range(1, 9):
    ps = list(itertools.permutations(range(1, n + 1)))
    fp = F(sum(sum(1 for i, v in enumerate(p, start=1) if i == v) for p in ps), len(ps))
    cy = F(sum(cycles(p) for p in ps), len(ps))
    ok_fp &= fp == 1
    ok_cy &= cy == H(n)
check("extra: expected number of fixed points of a uniform random permutation is 1 for every n <= 8", ok_fp)
check("extra: expected number of cycles is H_n for every n <= 8", ok_cy)
fp3 = {p: sum(1 for i, v in enumerate(p, start=1) if i == v) for p in itertools.permutations((1, 2, 3))}
check("concept example: n = 3: fixed points 3, 1, 1, 0, 0, 1 (123, 132, 213, 231, 312, 321), total 6, mean 1",
      [fp3[p] for p in sorted(fp3)] == [3, 1, 1, 0, 0, 1] and sum(fp3.values()) == 6)
ders = sum(1 for p in itertools.permutations(range(1, 9)) if all(i != v for i, v in enumerate(p, start=1)))
check("extra: Pr[no fixed point] for n = 8 is 14833/40320 ≈ 0.3679 ≈ 1/e", ders == 14833 and
      abs(ders / 40320 - math.exp(-1)) < 1e-4, ders)
ok = True
n = 6
ps = list(itertools.permutations(range(1, n + 1)))
for k in range(1, n + 1):
    cntk = 0
    for p in ps:
        j, L = 0, 0
        while True:
            j = p[j] - 1
            L += 1
            if j == 0:
                break
        cntk += L == k
    ok &= F(cntk, len(ps)) == F(1, n)
check("extra: element 1 lies on a cycle of length k with probability exactly 1/n for each k (n = 6), so "
      "E[#cycles] = sum_i sum_k (1/n)(1/k) = H_n", ok)

# ---- concept page: the dice example of linearity with dependent variables
check("concept: E[number of 5s on two dice] = 1/6 + 1/6 = 1/3 by indicators",
      E(lambda w: (w[0] == 5) + (w[1] == 5)) == F(1, 3))

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: " + "; ".join(FAIL))
