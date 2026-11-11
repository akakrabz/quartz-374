#!/usr/bin/env python3
"""Checks for content/3-homework-and-exams/lab-12b.md (Lab 12b, CS/ECE 374 A Fall 2026; no official solutions).

A CNF formula is a list of clauses; a clause is a tuple of nonzero integers (v for the variable x_v, -v for its
negation).  Ground truth is exhaustive search over all assignments wherever the formula is small enough, and a small
DPLL solver (itself validated against exhaustive search on thousands of random formulas) for the larger formulas that
the reductions build.  Every reduction is implemented exactly as the page states it and run on random instances of
the source problem, satisfiable and unsatisfiable: YES must map to YES and NO to NO, the built formula must have the
promised shape and size, and the two certificate translations of each proof are executed.

Problem 1 (3Sat -> 4Sat): one new variable per clause, two clauses per clause; the shared-variable variant; the two
      wrong paddings (repeat a literal; add only C or z) are shown to fail.
Problem 2 (Sat -> BalancedSat): y_i forced to be the opposite of x_i; every satisfying assignment of the built
      formula is balanced; the free-padding variant; the identity map is not a reduction.
Problem 3 (3Sat -> Exact3Sat, one-in-three): the three-clause gadget's truth table (which values of a, b, c extend),
      the whole reduction; an ordinary satisfying assignment need not be one-in-three.
Problem 4 (3Sat -> (<=3,<=3)-Sat): copies joined by a cycle of implications; shape, size, equisatisfiability.
Problem 5 ((<=3,<=3)-Sat -> (3,<=4)-Sat): the five-clause enforcer forces its variable to be False and uses it three
      times; shape (three distinct literals per clause, at most four occurrences per variable), size,
      equisatisfiability, also composed with Problem 4; the footnote: random (3,<=3) formulas are always satisfiable,
      by matching each clause to a variable of its own (Hall's theorem), and the two-clause counterexample when a
      clause may repeat a variable.
Problem 6 (XorSat): Gaussian elimination over GF(2) against exhaustive search, with the number of row operations;
      the page's two examples.
Every example on the page is recomputed here."""
import itertools
import random
import sys

sys.setrecursionlimit(10000)
random.seed(11132026)
FAIL = []


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail != "" else ""))
    if not cond:
        FAIL.append(name)


# ============================================================================ helpers
def variables(phi):
    return sorted({abs(l) for c in phi for l in c})


def lit_true(l, a):
    return a[abs(l)] if l > 0 else not a[abs(l)]


def satisfies(phi, a):
    return all(any(lit_true(l, a) for l in c) for c in phi)


def all_assignments(vs):
    for bits in itertools.product([False, True], repeat=len(vs)):
        yield dict(zip(vs, bits))


def brute_sat(phi, vs=None):
    vs = variables(phi) if vs is None else vs
    for a in all_assignments(vs):
        if satisfies(phi, a):
            return a
    return None


def dpll(phi):
    """A satisfying assignment (dict over the variables of phi) or None."""
    def simplify(cls, l):
        out = []
        for c in cls:
            if l in c:
                continue
            if -l in c:
                c = tuple(x for x in c if x != -l)
                if not c:
                    return None
            out.append(c)
        return out

    def go(cls, a):
        while True:
            unit = next((c[0] for c in cls if len(c) == 1), None)
            if unit is None:
                break
            a[abs(unit)] = unit > 0
            cls = simplify(cls, unit)
            if cls is None:
                return None
        if not cls:
            return a
        m = min(len(c) for c in cls)          # branch on the literal that occurs most often in the shortest clauses
        cnt = {}
        for c in cls:
            if len(c) == m:
                for x in c:
                    cnt[x] = cnt.get(x, 0) + 1
        l = max(cnt, key=lambda x: (cnt[x] + cnt.get(-x, 0), cnt[x]))
        for choice in (l, -l):
            b = dict(a)
            b[abs(choice)] = choice > 0
            c2 = simplify(cls, choice)
            if c2 is not None:
                r = go(c2, b)
                if r is not None:
                    return r
        return None

    cls = [tuple(dict.fromkeys(c)) for c in phi]
    if any(len(c) == 0 for c in cls):
        return None
    r = go(cls, {})
    if r is None:
        return None
    for v in variables(phi):
        r.setdefault(v, False)
    return r


def random_3cnf(n, k, allow_both_signs=True):
    """k clauses, each with exactly three distinct literals over x_1 .. x_n."""
    lits = [v for v in range(1, n + 1)] + [-v for v in range(1, n + 1)]
    phi = []
    while len(phi) < k:
        c = tuple(random.sample(lits, 3))
        if not allow_both_signs and len({abs(l) for l in c}) < 3:
            continue
        phi.append(c)
    return phi


def random_cnf(n, k, maxlen=4):
    lits = [v for v in range(1, n + 1)] + [-v for v in range(1, n + 1)]
    return [tuple(random.sample(lits, random.randint(1, min(maxlen, 2 * n)))) for _ in range(k)]


# the DPLL solver is validated first
ok = True
ns = nu = 0
for _ in range(4000):
    n = random.randint(1, 6)
    phi = random_cnf(n, random.randint(1, 14), maxlen=3)
    b = brute_sat(phi)
    d = dpll(phi)
    ok &= (b is None) == (d is None) and (d is None or satisfies(phi, d))
    ns += b is not None
    nu += b is None
check(f"the DPLL solver agrees with exhaustive search on 4000 random formulas ({ns} satisfiable, {nu} not)",
      ok and ns > 500 and nu > 500)

SOURCE = []           # 3CNF instances used as inputs of the reductions from 3Sat
for _ in range(700):
    n = random.randint(3, 5)
    r = random.random()
    if r < 0.4:        # few clauses: mostly satisfiable
        phi = random_3cnf(n, random.randint(1, 3 * n), allow_both_signs=random.random() < 0.3)
    elif r < 0.7:      # many clauses: a natural mix
        phi = random_3cnf(n, random.randint(4 * n, 7 * n), allow_both_signs=False)
    else:              # planted: all eight sign patterns on three of the variables, plus a few random clauses
        a, b, c = random.sample(range(1, n + 1), 3)
        phi = [(s1 * a, s2 * b, s3 * c) for s1 in (1, -1) for s2 in (1, -1) for s3 in (1, -1)]
        if random.random() < 0.5:
            phi.pop(random.randrange(8))      # one pattern missing: satisfiable again, but barely
        phi += random_3cnf(n, random.randint(0, 3), allow_both_signs=False)
        random.shuffle(phi)
    SOURCE.append(phi)
SAT3 = [brute_sat(p) is not None for p in SOURCE]
check(f"test inputs: 700 3CNF formulas with three distinct literals per clause, on 3-5 variables and up to 35 "
      f"clauses ({sum(SAT3)} satisfiable, {len(SAT3) - sum(SAT3)} not)", 200 < sum(SAT3) < 500)


def distinct_literals(phi, r):
    return all(len(c) == r and len(set(c)) == r for c in phi)


# ============================================================================ Problem 1: 3Sat -> 4Sat
def to_4sat(phi):
    """Page: for the j-th clause (a or b or c), a new variable z_j and the two clauses (a b c z_j), (a b c not z_j)."""
    n = max(variables(phi))
    out = []
    for j, c in enumerate(phi):
        z = n + 1 + j
        out.append(c + (z,))
        out.append(c + (-z,))
    return out


def to_4sat_shared(phi):
    z = max(variables(phi)) + 1
    return [c + (s * z,) for c in phi for s in (1, -1)]


ok_shape = ok_iff = ok_fw = ok_bw = ok_shared = True
for phi, sat in zip(SOURCE, SAT3):
    psi = to_4sat(phi)
    n, k = max(variables(phi)), len(phi)
    ok_shape &= distinct_literals(psi, 4) and len(psi) == 2 * k and max(variables(psi)) == n + k
    d = dpll(psi)
    ok_iff &= (d is not None) == sat
    if sat:
        a = brute_sat(phi, list(range(1, n + 1)))
        for _ in range(3):                    # => : any values of the new variables
            ext = dict(a)
            ext.update({n + 1 + j: random.random() < 0.5 for j in range(k)})
            ok_fw &= satisfies(psi, ext)
        ok_bw &= satisfies(phi, d)            # <= : restrict to the old variables
    psi2 = to_4sat_shared(phi)
    ok_shared &= distinct_literals(psi2, 4) and (dpll(psi2) is not None) == sat
check("1 the built formula has exactly four distinct literals per clause, 2k clauses and n + k variables", ok_shape)
check("1 Phi is satisfiable iff the 4CNF formula is (700 inputs)", ok_iff)
check("1 =>: a satisfying assignment of Phi with ANY values of the new variables satisfies the 4CNF formula", ok_fw)
check("1 <=: a satisfying assignment of the 4CNF formula, restricted to the old variables, satisfies Phi", ok_bw)
check("1 variant: one new variable shared by all clauses also works", ok_shared)
UNSAT8 = [(s1 * 1, s2 * 2, s3 * 3) for s1 in (1, -1) for s2 in (1, -1) for s3 in (1, -1)]
check("1 the eight clauses on x1, x2, x3 with all sign patterns are unsatisfiable", brute_sat(UNSAT8) is None)
check("1 trap: adding only (C or z) for each clause, without (C or not z), turns this unsatisfiable formula into a "
      "satisfiable one (all z True)", dpll([c + (4 + j,) for j, c in enumerate(UNSAT8)]) is not None)
check("1 trap: repeating a literal, (a or b or c or c), does not give four DISTINCT literals",
      not distinct_literals([(1, 2, 3, 3)], 4))
ex1 = to_4sat([(1, -2, 3)])
check("1 example: (x1 or not x2 or x3) becomes (x1, not x2, x3, z) and (x1, not x2, x3, not z)",
      ex1 == [(1, -2, 3, 4), (1, -2, 3, -4)])

# ============================================================================ Problem 2: Sat -> BalancedSat
def balanced_sat(phi):
    vs = variables(phi)
    if len(vs) % 2:
        return None
    for a in all_assignments(vs):
        if sum(a.values()) * 2 == len(vs) and satisfies(phi, a):
            return a
    return None


def to_balanced(phi):
    """Page: variables x_1 .. x_n; new y_i = x_{n+i}; add (x_i or y_i) and (not x_i or not y_i) for every i."""
    vs = variables(phi)
    n = max(vs)
    out = list(phi)
    for v in vs:
        out.append((v, n + v))
        out.append((-v, -(n + v)))
    return out


def to_balanced_padding(phi):
    """Variant: new variables y_i that occur only in the always-true clauses (y_i or not y_i)."""
    vs = variables(phi)
    n = max(vs)
    return list(phi) + [(n + v, -(n + v)) for v in vs]


ok_iff = ok_all_bal = ok_fw = ok_bw = ok_pad = ok_size = True
nsat = nunsat = 0
for _ in range(600):
    n = random.randint(1, 5)
    phi = random_cnf(n, random.randint(1, 3 * n + 2), maxlen=3)
    vs = variables(phi)
    sat = brute_sat(phi)
    nsat += sat is not None
    nunsat += sat is None
    psi = to_balanced(phi)
    ok_size &= len(variables(psi)) == 2 * len(vs) and len(psi) == len(phi) + 2 * len(vs)
    bal = balanced_sat(psi)
    ok_iff &= (bal is not None) == (sat is not None)
    for a in all_assignments(variables(psi)):
        if satisfies(psi, a):
            ok_all_bal &= sum(a.values()) == len(vs)
    if sat is not None:
        ext = dict(sat)
        ext.update({max(vs) + v: not sat[v] for v in vs})
        ok_fw &= satisfies(psi, ext) and sum(ext.values()) * 2 == len(ext)
        ok_bw &= satisfies(phi, bal)
    ok_pad &= (balanced_sat(to_balanced_padding(phi)) is not None) == (sat is not None)
check(f"2 Phi is satisfiable iff the built formula has a balanced satisfying assignment (600 random CNF formulas, "
      f"{nsat} satisfiable, {nunsat} not)", ok_iff and nsat > 100 and nunsat > 100)
check("2 the built formula has 2n variables and k + 2n clauses", ok_size)
check("2 EVERY satisfying assignment of the built formula makes exactly n of its 2n variables True", ok_all_bal)
check("2 =>: a satisfying assignment of Phi with y_i = not x_i is a balanced satisfying assignment", ok_fw)
check("2 <=: a balanced satisfying assignment, restricted to the x's, satisfies Phi", ok_bw)
check("2 variant: n new variables that occur only in clauses (y_i or not y_i) also works", ok_pad)
check("2 the identity is not a reduction: (x1) and (x2) is satisfiable but has no balanced satisfying assignment; "
      "(x1 or x2 or x3) is satisfiable and has an odd number of variables",
      brute_sat([(1,), (2,)]) is not None and balanced_sat([(1,), (2,)]) is None
      and brute_sat([(1, 2, 3)]) is not None and balanced_sat([(1, 2, 3)]) is None)
check("2 example: (x1) and (x2) becomes a formula on x1, x2, y1, y2 whose only satisfying assignment is "
      "x1 = x2 = True, y1 = y2 = False",
      [a for a in all_assignments([1, 2, 3, 4]) if satisfies(to_balanced([(1,), (2,)]), a)]
      == [{1: True, 2: True, 3: False, 4: False}])

# ============================================================================ Problem 3: 3Sat -> Exact3Sat
def one_in_three(phi, a):
    return all(sum(lit_true(l, a) for l in c) == 1 for c in phi)


def exact3_brute(phi):
    for a in all_assignments(variables(phi)):
        if one_in_three(phi, a):
            return a
    return None


def exact3_as_cnf(phi):
    """Exactly one of a, b, c:  (a or b or c), (not a or not b), (not a or not c), (not b or not c)."""
    out = []
    for (a, b, c) in phi:
        out += [(a, b, c), (-a, -b), (-a, -c), (-b, -c)]
    return out


def exact3_solve(phi):
    r = dpll(exact3_as_cnf(phi))
    return r


ok = True
for _ in range(1500):
    n = random.randint(3, 6)
    phi = random_3cnf(n, random.randint(1, 7), allow_both_signs=random.random() < 0.3)
    b = exact3_brute(phi)
    d = exact3_solve(phi)
    ok &= (b is None) == (d is None) and (d is None or one_in_three(phi, d))
check("3 (tool) the one-in-three solver (DPLL on 'at least one' plus 'no two') agrees with exhaustive search on "
      "1500 random instances", ok)


def to_exact3(phi):
    """Page: clause j = (a or b or c) becomes (not a, u, v), (b, v, w), (not c, w, t) with four new variables."""
    n = max(variables(phi))
    out = []
    for j, (a, b, c) in enumerate(phi):
        u, v, w, t = (n + 4 * j + i for i in (1, 2, 3, 4))
        out += [(-a, u, v), (b, v, w), (-c, w, t)]
    return out


# the gadget's truth table
table = {}
for a, b, c in itertools.product([False, True], repeat=3):
    cnt = 0
    for u, v, w, t in itertools.product([False, True], repeat=4):
        asg = {1: a, 2: b, 3: c, 4: u, 5: v, 6: w, 7: t}
        cnt += one_in_three([(-1, 4, 5), (2, 5, 6), (-3, 6, 7)], asg)
    table[(a, b, c)] = cnt
check("3 gadget: the three clauses (not a, u, v), (b, v, w), (not c, w, t) can be completed to one True literal "
      "each iff a or b or c", all((table[k] > 0) == any(k) for k in table), table)
check("3 gadget: number of completions (u, v, w, t) per (a, b, c): FFF 0, FFT 1, FTF 1, FTT 1, TFF 1, TFT 2, "
      "TTF 1, TTT 1",
      [table[k] for k in sorted(table)] == [0, 1, 1, 1, 1, 2, 1, 1], [table[k] for k in sorted(table)])
def completion(a, b, c):
    """The page's rule for the new variables, given the values of a, b, c (not all False)."""
    if b:
        return (a, False, False, c)           # u = a, v = w = False, t = c
    if a and c:
        return (False, True, False, True)     # v = True, t = True
    if a:
        return (False, True, False, False)    # a only: v = True
    return (False, False, True, False)        # c only: w = True
check("3 gadget: the page's completion rule (b: u = a, t = c; a and c: v, t; a only: v; c only: w) works in all "
      "seven cases", all(one_in_three([(-1, 4, 5), (2, 5, 6), (-3, 6, 7)],
                                      dict(zip(range(1, 8), k + completion(*k)))) for k in table if any(k)))
ok_shape = ok_iff = ok_fw = ok_bw = True
for phi, sat in zip(SOURCE, SAT3):
    psi = to_exact3(phi)
    n, k = max(variables(phi)), len(phi)
    ok_shape &= distinct_literals(psi, 3) and len(psi) == 3 * k and max(variables(psi)) == n + 4 * k
    d = exact3_solve(psi)
    ok_iff &= (d is not None) == sat
    if sat:
        a = brute_sat(phi, list(range(1, n + 1)))
        ext = dict(a)
        for j, cl in enumerate(phi):
            vals = completion(*[lit_true(l, a) for l in cl])
            ext.update({n + 4 * j + i + 1: vals[i] for i in range(4)})
        ok_fw &= one_in_three(psi, ext)
        ok_bw &= satisfies(phi, d) and one_in_three(psi, d)
check("3 the built formula has three distinct literals per clause, 3k clauses and n + 4k variables", ok_shape)
check("3 Phi is satisfiable iff the built formula has a one-in-three assignment (700 inputs)", ok_iff)
check("3 =>: a satisfying assignment of Phi, completed clause by clause by the page's rule, is one-in-three", ok_fw)
check("3 <=: a one-in-three assignment of the built formula, restricted to the old variables, satisfies Phi", ok_bw)
check("3 a satisfying assignment need not be one-in-three: (x1 or x2 or x3) and (not x1 or x2 or x3) and "
      "(x1 or not x2 or x3) and (x1 or x2 or not x3) is satisfiable (all True) but has no one-in-three assignment",
      brute_sat([(1, 2, 3), (-1, 2, 3), (1, -2, 3), (1, 2, -3)]) is not None
      and exact3_brute([(1, 2, 3), (-1, 2, 3), (1, -2, 3), (1, 2, -3)]) is None)

# ============================================================================ Problem 4: 3Sat -> (<=3,<=3)-Sat
def occurrences(phi):
    occ = {}
    for i, c in enumerate(phi):
        for v in {abs(l) for l in c}:
            occ.setdefault(v, set()).add(i)
    return occ


def at_most(phi, maxlen, maxocc):
    """Every clause has at most maxlen literals (all distinct); every variable appears in at most maxocc clauses."""
    return (all(1 <= len(c) <= maxlen and len(set(c)) == len(c) for c in phi)
            and all(len(s) <= maxocc for s in occurrences(phi).values()))


def to_33(phi):
    """Page: for every variable x with r > 3 occurrences (counted with multiplicity), replace the j-th occurrence by
    a new variable x^j (same sign) and add the clauses (not x^j or x^{j+1}), j = 1 .. r, indices modulo r."""
    nxt = max(variables(phi)) + 1
    count = {}
    for c in phi:
        for l in c:
            count[abs(l)] = count.get(abs(l), 0) + 1
    copies = {}
    seen = {}
    out = []
    for c in phi:
        new = []
        for l in c:
            v = abs(l)
            if count[v] <= 3:
                new.append(l)
                continue
            j = seen.get(v, 0)
            seen[v] = j + 1
            copies.setdefault(v, []).append(nxt)
            new.append(nxt if l > 0 else -nxt)
            nxt += 1
        out.append(tuple(new))
    for v, cs in copies.items():
        r = len(cs)
        for j in range(r):
            out.append((-cs[j], cs[(j + 1) % r]))
    return out, copies


ok_shape = ok_iff = ok_fw = ok_bw = ok_size = True
nsplit = 0
for phi, sat in zip(SOURCE, SAT3):
    psi, copies = to_33(phi)
    k = len(phi)
    nsplit += bool(copies)
    ok_shape &= at_most(psi, 3, 3)
    ok_size &= len(psi) <= 4 * k and len(variables(psi)) <= 3 * k
    d = dpll(psi)
    ok_iff &= (d is not None) == sat
    if sat:
        a = brute_sat(phi)
        ext = dict(a)
        for v, cs in copies.items():
            ext.update({c: a[v] for c in cs})
        ok_fw &= satisfies(psi, {v: ext.get(v, False) for v in variables(psi)})
        # <= : all copies of a variable are equal; give x that common value
        ok_bw &= all(len({d[c] for c in cs}) == 1 for cs in copies.values())
        back = {v: (d[copies[v][0]] if v in copies else d.get(v, False)) for v in variables(phi)}
        ok_bw &= satisfies(phi, back)
check(f"4 the built formula has at most three literals per clause and every variable in at most three clauses "
      f"({nsplit} of 700 inputs needed copies)", ok_shape and nsplit > 400)
check("4 size: at most 4k clauses and 3k variables", ok_size)
check("4 Phi is satisfiable iff the built formula is (700 inputs)", ok_iff)
check("4 =>: give every copy the value of its variable", ok_fw)
check("4 <=: in a satisfying assignment all copies of a variable are equal, and that value satisfies Phi", ok_bw)
check("4 the cycle (not x1 or x2), (not x2 or x3), (not x3 or x4), (not x4 or x1) has exactly two satisfying "
      "assignments, all False and all True",
      [tuple(a.values()) for a in all_assignments([1, 2, 3, 4])
       if satisfies([(-1, 2), (-2, 3), (-3, 4), (-4, 1)], a)] == [(False,) * 4, (True,) * 4])
ex4 = [(1, 2, 3), (-1, 2, 4), (1, -3, 4), (-1, -2, -4)]
psi4, cp4 = to_33(ex4)
check("4 example: in (x1 x2 x3)(-x1 x2 x4)(x1 -x3 x4)(-x1 -x2 -x4) only x1 occurs four times; the result has "
      "4 + 4 = 8 clauses, and each copy of x1 is in one old clause and two cycle clauses",
      list(cp4) == [1] and len(cp4[1]) == 4 and len(psi4) == 8 and at_most(psi4, 3, 3)
      and all(len(occurrences(psi4)[c]) == 3 for c in cp4[1]), psi4)

# ============================================================================ Problem 5: (<=3,<=3)-Sat -> (3,<=4)-Sat
def enforcer(z, p, q, r):
    """Five clauses that force z to be False (page): (-z -p q) (-z -q r) (-z -r p) (p q r) (-p -q -r)."""
    return [(-z, -p, q), (-z, -q, r), (-z, -r, p), (p, q, r), (-p, -q, -r)]


sols = [a for a in all_assignments([1, 2, 3, 4]) if satisfies(enforcer(1, 2, 3, 4), a)]
check("5 enforcer: every satisfying assignment has z = False, and there are six of them (p, q, r not all equal)",
      len(sols) == 6 and all(not a[1] for a in sols)
      and all(len({a[2], a[3], a[4]}) == 2 for a in sols), len(sols))
check("5 enforcer: z = False, p = True, q = r = False satisfies it",
      satisfies(enforcer(1, 2, 3, 4), {1: False, 2: True, 3: False, 4: False}))
occE = {}
for c in enforcer(1, 2, 3, 4):
    for l in c:
        occE[abs(l)] = occE.get(abs(l), 0) + 1
check("5 enforcer: z occurs in three of its clauses, p, q and r in four each; every clause has three distinct "
      "variables", occE == {1: 3, 2: 4, 3: 4, 4: 4}
      and all(len({abs(l) for l in c}) == 3 for c in enforcer(1, 2, 3, 4)), occE)
check("5 enforcer: with z = True the three implications p -> q -> r -> p force p = q = r, which the last two "
      "clauses forbid", all(not satisfies(enforcer(1, 2, 3, 4), {1: True, 2: p, 3: q, 4: r})
                            for p, q, r in itertools.product([False, True], repeat=3)))


def to_34(psi):
    """Page: a clause with three literals is kept; (a or b) becomes (a or b or z) plus an enforcer for z;
    (a) becomes (a or z or z') plus an enforcer for each of z and z'."""
    nxt = [max(variables(psi)) + 1]

    def fresh_forced():
        z, p, q, r = nxt[0], nxt[0] + 1, nxt[0] + 2, nxt[0] + 3
        nxt[0] += 4
        return z, enforcer(z, p, q, r)
    out = []
    forced = []
    for c in psi:
        c = tuple(dict.fromkeys(c))
        pad = []
        while len(c) + len(pad) < 3:
            z, E = fresh_forced()
            pad.append(z)
            forced.append((z, E))
        out.append(c + tuple(pad))
    for z, E in forced:
        out += E
    return out, forced


def random_le3le3(n, k):
    """A random formula with clauses of 1-3 distinct literals in which every variable occurs in at most 3 clauses."""
    left = {v: 3 for v in range(1, n + 1)}
    phi = []
    for _ in range(k):
        avail = [v for v in left if left[v] > 0]
        if not avail:
            break
        size = min(random.choice([1, 2, 2, 3, 3, 3]), len(avail))
        vs = random.sample(avail, size)
        for v in vs:
            left[v] -= 1
        phi.append(tuple(v if random.random() < 0.5 else -v for v in vs))
    return phi


def shape34(phi):
    return (all(len(c) == 3 and len(set(c)) == 3 for c in phi)
            and all(len(s) <= 4 for s in occurrences(phi).values()))


ok_shape = ok_iff = ok_fw = ok_bw = ok_size = True
ns = nu = 0
tests5 = []
for _ in range(900):
    n = random.randint(1, 7)
    tests5.append(random_le3le3(n, random.randint(1, 3 * n)))
tests5 = [p for p in tests5 if p]
for psi in tests5:
    assert at_most(psi, 3, 3)
    sat = brute_sat(psi)
    ns += sat is not None
    nu += sat is None
    out, forced = to_34(psi)
    short1 = sum(len(c) == 1 for c in psi)
    short2 = sum(len(c) == 2 for c in psi)
    ok_shape &= shape34(out)
    ok_size &= len(forced) == 2 * short1 + short2 and len(out) == len(psi) + 5 * len(forced) \
        and len(variables(out)) == len(variables(psi)) + 4 * len(forced)
    d = dpll(out)
    ok_iff &= (d is not None) == (sat is not None)
    if sat is not None:
        ext = dict(sat)
        for z, E in forced:
            ext.update({z: False, z + 1: True, z + 2: False, z + 3: False})
        ok_fw &= satisfies(out, ext)
        ok_bw &= all(not d[z] for z, E in forced) and satisfies(psi, d)
check(f"5 the built formula has exactly three distinct literals per clause and every variable in at most four "
      f"clauses ({len(tests5)} random (<=3,<=3) formulas, {ns} satisfiable, {nu} not)", ok_shape and ns > 150 and nu > 100)
check("5 size: one padding variable per 2-literal clause and two per 1-literal clause; five clauses and four "
      "variables per padding variable", ok_size)
check("5 Psi is satisfiable iff the built formula is", ok_iff)
check("5 =>: padding variables False and (p, q, r) = (True, False, False)", ok_fw)
check("5 <=: every padding variable is False in every satisfying assignment found, and the rest satisfies Psi", ok_bw)
ok_chain = ok_chain_shape = True
chain = [(phi, sat) for phi, sat in zip(SOURCE, SAT3) if len(phi) <= 15]
for phi, sat in chain:
    mid, _ = to_33(phi)
    out, _ = to_34(mid)
    ok_chain_shape &= shape34(out)
    ok_chain &= (dpll(out) is not None) == sat
nchain_unsat = sum(not sat for _, sat in chain)
check(f"5 composed with Problem 4: 3Sat -> (<=3,<=3)-Sat -> (3,<=4)-Sat preserves the answer and gives the right "
      f"shape (the {len(chain)} inputs with at most 15 clauses, {nchain_unsat} of them unsatisfiable)",
      ok_chain and ok_chain_shape and nchain_unsat > 60 and len(chain) - nchain_unsat > 60)
ex5, f5 = to_34([(1, -2)])
check("5 example: (x1 or not x2) becomes (x1, not x2, z) plus the five enforcer clauses: 6 clauses, 6 variables; "
      "z occurs four times", len(ex5) == 6 and len(variables(ex5)) == 6 and ex5[0] == (1, -2, 3)
      and len(occurrences(ex5)[3]) == 4, ex5)
check("5 trap: padding (a or b) as (a, b, z), (a, b, not z) doubles the occurrences of a and b: a variable in "
      "three 2-literal clauses would occur six times", 2 * 3 == 6 and 6 > 4)


# footnote: (3,<=3)-Sat is always satisfiable
def matching_assignment(phi):
    """Match every clause to a variable of its own by augmenting paths; set that variable to satisfy the clause."""
    owner = {}

    def try_clause(i, seen):
        for l in phi[i]:
            v = abs(l)
            if v in seen:
                continue
            seen.add(v)
            if v not in owner or try_clause(owner[v], seen):
                owner[v] = i
                return True
        return False
    for i in range(len(phi)):
        if not try_clause(i, set()):
            return None
    a = {v: False for v in variables(phi)}
    for v, i in owner.items():
        a[v] = any(l == v for l in phi[i])
    return a


def random_3le3(n):
    """Clauses with three distinct variables; every variable in at most three clauses; as many clauses as fit."""
    left = {v: 3 for v in range(1, n + 1)}
    phi = []
    while True:
        avail = [v for v in left if left[v] > 0]
        if len(avail) < 3:
            return phi
        vs = random.sample(avail, 3)
        for v in vs:
            left[v] -= 1
        phi.append(tuple(v if random.random() < 0.5 else -v for v in vs))


ok = True
m = 0
for _ in range(400):
    phi = random_3le3(random.randint(3, 12))
    if not phi:
        continue
    m += 1
    a = matching_assignment(phi)
    ok &= a is not None and satisfies(phi, a) and dpll(phi) is not None
check(f"5 footnote: {m} random formulas with three distinct variables per clause and every variable in at most "
      "three clauses are all satisfiable, by matching each clause to a variable of its own", ok and m > 300)
check("5 footnote needs distinct variables: (x or x or x) and (not x or not x or not x) is unsatisfiable",
      brute_sat([(1, 1, 1), (-1, -1, -1)]) is None)

# ============================================================================ Problem 6: XorSat
def xor_satisfies(phi, a):
    return all(sum(lit_true(l, a) for l in c) % 2 == 1 for c in phi)


def xorsat_brute(phi, vs):
    for a in all_assignments(vs):
        if xor_satisfies(phi, a):
            return a
    return None


def xorsat(phi, n):
    """Page: clause -> equation over GF(2): the sum of its variables (each as often as it occurs) equals
    1 + (number of negated literals); Gaussian elimination; free variables False.  Returns (assignment or None,
    number of row additions)."""
    rows = []
    for c in phi:
        row = [0] * (n + 1)
        rhs = 1
        for l in c:
            row[abs(l) - 1] ^= 1
            if l < 0:
                rhs ^= 1
        row[n] = rhs
        rows.append(row)
    ops = 0
    piv = []
    r = 0
    for col in range(n):
        p = next((i for i in range(r, len(rows)) if rows[i][col]), None)
        if p is None:
            continue
        rows[r], rows[p] = rows[p], rows[r]
        for i in range(len(rows)):
            if i != r and rows[i][col]:
                rows[i] = [x ^ y for x, y in zip(rows[i], rows[r])]
                ops += 1
        piv.append(col)
        r += 1
    if any(row[n] and not any(row[:n]) for row in rows):
        return None, ops
    a = {v: False for v in range(1, n + 1)}
    for i, col in enumerate(piv):
        a[col + 1] = bool(rows[i][n])
    return a, ops


def random_xcnf(n, k):
    lits = [v for v in range(1, n + 1)] + [-v for v in range(1, n + 1)]
    return [tuple(random.choice(lits) for _ in range(random.randint(1, 4))) for _ in range(k)]


ok = ok_ops = True
ns = nu = 0
for _ in range(3000):
    n = random.randint(1, 6)
    phi = random_xcnf(n, random.randint(1, 8))
    vs = list(range(1, n + 1))
    b = xorsat_brute(phi, vs)
    a, ops = xorsat(phi, n)
    ok &= (a is None) == (b is None) and (a is None or xor_satisfies(phi, a))
    ok_ops &= ops <= len(phi) * min(len(phi), n)
    ns += b is not None
    nu += b is None
check(f"6 Gaussian elimination over GF(2) decides XorSat and returns a satisfying assignment (3000 random XCNF "
      f"formulas, repeated variables allowed; {ns} satisfiable, {nu} not)", ok and ns > 500 and nu > 500)
check("6 at most m * min(m, n) row additions", ok_ops)
tri = [(1, 2), (2, 3), (1, 3)]
check("6 example: (x1 xor x2), (x2 xor x3), (x1 xor x3) is unsatisfiable: the three equations add up to 0 = 1",
      xorsat(tri, 3)[0] is None and xorsat_brute(tri, [1, 2, 3]) is None)
check("6 example: as ordinary Or-clauses, (x1 or x2), (x2 or x3), (x1 or x3) are satisfiable",
      brute_sat(tri) is not None)
ex6 = [(1, -2, 3), (2, 3), (-1, -3)]
a6, _ = xorsat(ex6, 3)
check("6 example: (x1 xor not x2 xor x3), (x2 xor x3), (not x1 xor not x3) becomes x1+x2+x3 = 0, x2+x3 = 1, "
      "x1+x3 = 1; the unique solution is x1 = True, x2 = True, x3 = False",
      a6 == {1: True, 2: True, 3: False}
      and [a for a in all_assignments([1, 2, 3]) if xor_satisfies(ex6, a)] == [a6], a6)
check("6 a negated literal flips the right-hand side: (not x) is the equation x = 0, and (x xor x) is 0 = 1",
      xorsat([(-1,)], 1)[0] == {1: False} and xorsat([(1, 1)], 1)[0] is None)

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: {FAIL}")
