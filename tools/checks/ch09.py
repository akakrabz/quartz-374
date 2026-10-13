#!/usr/bin/env python3
"""Checks for the concrete claims on content/1-models-of-computation/09-nondeterministic-turing-machines.md.

Conventions of the small nondeterministic simulator below: a configuration is (state, tape, head); delta(p, a) is an
ordered list of choices (choice 1, 2, ...); an empty choice list moves to the reject state (one step); moving left
from cell 0 crashes, and a crashed branch is treated as rejecting (the page's machines never move left at all, so
this only matters for the random machines, where it is applied identically to every simulation)."""
import os
import random
import sys
from collections import deque
from itertools import product

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
from automata import TM, strings  # noqa: E402
import figs_ch09 as F  # noqa: E402  (figure data; importing does not write figures)

FAIL = []
B = "□"
GAMMA = ["0", "1", B]


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAIL.append(name)


# ---------------------------------------------------------------- nondeterministic machines
def children(delta, conf):
    """The configurations one step after conf, in choice order (empty for halted configurations)."""
    q, tape, head = conf
    if q in ("accept", "reject"):
        return []
    a = tape[head] if head < len(tape) else B
    opts = delta.get((q, a), [])
    if not opts:
        return [("reject", tape, head)]
    out = []
    for p, b, d in opts:
        t = list(tape) + [B] * (head + 1 - len(tape))
        t[head] = b
        nh = head + d
        out.append(("reject", tuple(t), 0) if nh < 0 else (p, tuple(t), nh))   # crash counts as reject
    return out


def start_conf(w):
    return ("start", tuple(w), 0)


def bfs(delta, w, max_depth):
    """Theorem 1's breadth-first simulation, explored to depth max_depth.
    Returns 'accept' (an accepting configuration at depth <= max_depth), 'reject' (the whole tree has depth <=
    max_depth and no accepting leaf), or None (undetermined at this depth). Also the dequeue order."""
    queue = deque([(start_conf(w), 0)])
    order = []
    deeper = False
    while queue:
        conf, d = queue.popleft()
        order.append(conf)
        if conf[0] == "accept":
            return "accept", order
        if conf[0] == "reject":
            continue
        if d == max_depth:
            deeper = True
            continue
        for c in children(delta, conf):
            queue.append((c, d + 1))
    return (None if deeper else "reject"), order


def advice_run(delta, w, x, r):
    """The deterministic machine M of the advice view: at each step it reads the next advice symbol omega in
    {1..r} and takes choice omega (the last choice if there are fewer). Returns (outcome, steps) after at most
    |x| steps; outcome None if it has not halted."""
    conf = start_conf(w)
    for s, om in enumerate(x):
        if conf[0] in ("accept", "reject"):
            return conf[0], s
        ch = children(delta, conf)
        conf = ch[min(int(om), len(ch)) - 1]
    return (conf[0], len(x)) if conf[0] in ("accept", "reject") else (None, len(x))


def dovetail(delta, w, r, max_t):
    """The page's Dovetail(w), run for t = 1, ..., max_t."""
    for t in range(1, max_t + 1):
        done = True
        for x in product("".join(str(i) for i in range(1, r + 1)), repeat=t):
            out, steps = advice_run(delta, w, x, r)
            if out == "accept":
                return "accept", t
            if out is None:
                done = False
        if done:
            return "reject", t
    return None, max_t


def branching(delta):
    return max(len(v) for v in delta.values())


def swap_accept_reject(delta):
    sw = {"accept": "reject", "reject": "accept"}
    return {k: [(sw.get(p, p), b, d) for (p, b, d) in v] for k, v in delta.items()}


has11 = lambda w: "11" in w
N, NP = F.N_DELTA, F.NP_DELTA

# ---------------------------------------------------------------- 9.1 the computation tree in the figure
def tree(delta, w, depth):
    """All configurations to the given depth, keyed by the choice path (a tuple of child indices)."""
    nodes, frontier = {(): start_conf(w)}, [()]
    for _ in range(depth):
        nxt = []
        for path in frontier:
            for i, c in enumerate(children(delta, nodes[path])):
                nodes[path + (i,)] = c
                nxt.append(path + (i,))
        frontier = nxt
    return nodes


T = tree(N, F.TREE_INPUT, 5)
# map figure keys to choice paths
path_of = {}
for k, (q, head, d, par, chl) in F.TREE.items():
    if par is None:
        path_of[k] = ()
    else:
        sibs = [kk for kk, v in F.TREE.items() if v[3] == par]
        path_of[k] = path_of[par] + (sibs.index(k),)
ok = len(T) == len(F.TREE)
for k, (q, head, d, par, chl) in F.TREE.items():
    p = path_of[k]
    conf = T.get(p)
    ok &= conf is not None and conf[0] == q and conf[2] == head and len(p) == d
    if par is not None:
        nkids = len(children(N, T[path_of[par]]))
        ok &= (chl == str(p[-1] + 1)) if nkids > 1 else chl is None
    ok &= "".join(conf[1]).rstrip(B) == F.TREE_INPUT                       # N never changes the tape
check("figure: the computation tree of N on 011 (to depth 5) is exactly the drawn tree, with the drawn choice labels",
      ok, f"{len(T)} nodes")
leaves = [c for c in T.values() if c[0] in ("accept", "reject")]
check("figure: one accepting leaf (depth 3), two rejecting leaves (depth 4)",
      sorted((c[0], c[2]) for c in leaves) == [("accept", 3), ("reject", 4), ("reject", 4)])
check("figure: the loop branch is infinite (loop only moves right and stays in loop)",
      all(N[("loop", a)] == [("loop", a, +1)] for a in GAMMA) and T[path_of["n10"]][0] == "loop")

# ---------------------------------------------------------------- 9.2 acceptance and rejection
ok_acc = ok_neither = ok_dec = ok_rev = True
for w in strings("01", 10):
    res, _ = bfs(N, w, len(w) + 12)
    if has11(w):
        ok_acc &= res == "accept"
    else:
        ok_neither &= res is None          # no accepting leaf, and the loop branch is still running at depth |w|+12
    res2, _ = bfs(NP, w, len(w) + 3)
    ok_dec &= res2 == ("accept" if has11(w) else "reject")
    res3, _ = bfs(swap_accept_reject(NP), w, len(w) + 3)
    ok_rev &= res3 == "accept"
check("N accepts exactly the strings containing 11 (|w| <= 10)", ok_acc)
check("on strings without 11, N neither accepts nor rejects (no accepting leaf; the loop branch never halts)",
      ok_neither)
check("N' (no looping choice) decides 'contains 11': accepts with 11, rejects without (|w| <= 10)", ok_dec)
check("N' with accept and reject swapped accepts every string (|w| <= 10), not the complement", ok_rev)
check("N' on 010: every branch rejects; N on 010: not every branch halts",
      bfs(NP, "010", 10)[0] == "reject" and bfs(N, "010", 30)[0] is None)

# ---------------------------------------------------------------- 9.4 breadth-first versus depth-first
res, order = bfs(N, F.TREE_INPUT, 10)
fig_order = [(F.TREE[k][0], F.TREE[k][1]) for k in F.BFS_ORDER]
check("figure: breadth-first search dequeues the configurations in the drawn order; the 7th accepts",
      res == "accept" and [(c[0], c[2]) for c in order] == fig_order and len(order) == 7)


def dfs_visits(delta, w, limit):
    """Depth-first search, choice 1 first; the first `limit` configurations visited."""
    out, stack = [], [start_conf(w)]
    while stack and len(out) < limit:
        c = stack.pop()
        out.append(c)
        if c[0] == "accept":
            break
        stack.extend(reversed(children(delta, c)))
    return out


vis = dfs_visits(N, F.TREE_INPUT, 2000)
check("depth-first search (choice 1 first) visits 2000 configurations without reaching the accepting leaf",
      len(vis) == 2000 and all(c[0] != "accept" for c in vis) and vis[-1][0] == "loop")
check("figure: the red edges are the first edges depth-first search explores",
      [(c[0], c[2]) for c in vis[:5]] == [(F.TREE[k][0], F.TREE[k][1]) for k in ["n0", "n1", "n2", "n5", "n7"]]
      and [(c[0], c[2]) for c in vis[5:7]] == [(F.TREE[k][0], F.TREE[k][1]) for k in ["n8", "n10"]])

# Theorem 1's counting: at most r^t configurations at depth t
rng = random.Random(9)


def random_ntm(k, r):
    states = ["start"] + [f"q{i}" for i in range(1, k)]
    targets = states + ["accept", "reject"]
    delta = {}
    for q in states:
        for a in GAMMA:
            n = rng.randint(0, r)
            delta[(q, a)] = [(rng.choice(targets), rng.choice(GAMMA), rng.choice([-1, +1, +1])) for _ in range(n)]
    if branching(delta) == 0:
        delta[("start", "0")] = [("accept", "0", +1)]
    return delta


ok_count, worst = True, 0
for _ in range(200):
    d = random_ntm(rng.randint(1, 3), rng.randint(1, 3))
    r = max(1, branching(d))
    for w in strings("01", 3):
        Tr = tree(d, w, 6)
        for t in range(7):
            cnt = sum(1 for p in Tr if len(p) == t)
            ok_count &= cnt <= r ** t
check("Theorem 1 counting: at most r^t configurations at depth t (200 random machines, depth <= 6)", ok_count)

# ---------------------------------------------------------------- 9.5 advice strings and dovetailing
r = branching(N)
acc = [x for x in product("12", repeat=3) if advice_run(N, F.TREE_INPUT, x, r)[0] == "accept"]
check("advice: on 011, the advice strings of length 3 that make M accept are exactly those with second symbol 2",
      sorted("".join(x) for x in acc) == F.ACCEPT_ADVICE and all(x[1] == "2" for x in F.ACCEPT_ADVICE))
ok = True
for w in strings("01", 8):
    for delta in (N, NP):
        T_ = len(w) + 4
        b = bfs(delta, w, T_)[0]
        dv = dovetail(delta, w, branching(delta), T_)[0]
        ok &= b == dv
check("N and N': breadth-first search and dovetailing give identical outcomes (|w| <= 8)", ok)
ok, stats = True, {"accept": 0, "reject": 0, None: 0}
for _ in range(300):
    d = random_ntm(rng.randint(1, 3), rng.randint(1, 3))
    r = max(1, branching(d))
    for w in strings("01", 3):
        b = bfs(d, w, 7)[0]
        dv = dovetail(d, w, r, 7)[0]
        stats[b] += 1
        ok &= b == dv
check("random machines: breadth-first and dovetailing agree on accept / reject / undetermined (300 x 15)", ok,
      str({str(k): v for k, v in stats.items()}))
ok = all(sum(s * r ** s for s in range(1, t + 1)) <= r / (r - 1) * t * r ** t <= 2 * t * r ** t
         for r in range(2, 7) for t in range(1, 41))
check("dovetailing cost: sum_{s<=t} s r^s <= (r/(r-1)) t r^t <= 2 t r^t, so O(t r^t) (r = 2..6, t <= 40)", ok)

# ---------------------------------------------------------------- 9.6 the Cook-Levin formula on a toy verifier
# M reads w, steps onto the first advice cell, overwrites it, walks back to the last input symbol and accepts iff
# that symbol equals the advice symbol. Tape at time 0: w, a blank, the advice. (Uses writes and left moves.)
VD = {("scan", "0"): ("scan", "0", +1), ("scan", "1"): ("scan", "1", +1), ("scan", B): ("adv", B, +1),
      ("adv", "0"): ("back0", "1", -1), ("adv", "1"): ("back1", "0", -1),
      ("back0", B): ("cmp0", B, -1), ("back1", B): ("cmp1", B, -1),
      ("cmp0", "0"): ("accept", "0", +1), ("cmp0", "1"): ("reject", "1", +1),
      ("cmp1", "1"): ("accept", "1", +1), ("cmp1", "0"): ("reject", "0", +1)}
VQ = ["scan", "adv", "back0", "back1", "cmp0", "cmp1", "accept", "reject"]
V = TM(VD, start="scan")


def phi_satisfiable(w, Nn):
    """Evaluate the page's constraints literally. Cells 0..N+2 (0 and N+2 are sentinels), times 0..N. An assignment
    satisfying the boundary, initialization and advice constraints is fixed by the advice symbols; the transition
    constraints are equivalences that then fix every later variable. So Phi is satisfiable iff for some advice the
    forced assignment satisfies the acceptance constraint."""
    n = len(w)
    cells = range(0, Nn + 3)
    adv_cells = list(range(n + 2, Nn + 2))
    sat_count = 0
    for adv in product(GAMMA, repeat=len(adv_cells)):
        Q = {(i, q): False for i in cells for q in VQ}          # time 0
        Tt = {(i, a): False for i in cells for a in GAMMA}
        Q[(1, "scan")] = True
        for i in range(1, n + 1):
            Tt[(i, w[i - 1])] = True
        Tt[(n + 1, B)] = True
        for i, a in zip(adv_cells, adv):
            Tt[(i, a)] = True
        accepted = Q[(1, "accept")]
        # boundary constraints at time 0
        assert not any(Q[(i, q)] or False for i in (0, Nn + 2) for q in VQ)
        for t in range(1, Nn + 1):
            Q2 = {(i, q): False for i in cells for q in VQ}
            T2 = {(i, a): False for i in cells for a in GAMMA}
            for i in range(1, Nn + 2):
                for q in VQ:
                    Q2[(i, q)] = any(Q[(i - 1, p)] and Tt[(i - 1, a)] for (p, a), (qq, _b, d) in VD.items()
                                     if qq == q and d == +1) or \
                                 any(Q[(i + 1, p)] and Tt[(i + 1, a)] for (p, a), (qq, _b, d) in VD.items()
                                     if qq == q and d == -1)
                for bsym in GAMMA:
                    T2[(i, bsym)] = any(Q[(i, p)] and Tt[(i, a)] for (p, a), (_q, bb, _d) in VD.items() if bb == bsym) \
                        or (Tt[(i, bsym)] and not any(Q[(i, q)] for q in VQ))
            Q, Tt = Q2, T2          # sentinel variables stay False (boundary constraints)
            accepted = accepted or any(Q[(i, "accept")] for i in cells)
        sat_count += accepted
    return sat_count > 0


def direct(w, Nn):
    """Does some advice make the verifier accept w-blank-advice within N steps?"""
    n = len(w)
    for adv in product(GAMMA, repeat=max(0, Nn - n)):
        tape = w + B + "".join(adv)
        if V.run(tape, max_steps=Nn)[0] == "accept":
            return True
    return False


ok, cases, sats = True, 0, 0
for Nn in range(1, 8):
    for n in range(0, 3):
        if Nn - n > 5:
            continue
        for w in strings("01", n, n):
            cases += 1
            s = phi_satisfiable(w, Nn)
            sats += s
            ok &= s == direct(w, Nn)
check("Cook-Levin: Phi_w (constraints evaluated literally) is satisfiable iff some advice makes the toy verifier "
      "accept within N steps", ok, f"{cases} (w, N) cases, {sats} satisfiable")


def formula_size(Nn, nq=len(VQ), ng=len(GAMMA)):
    """Number of variables and of literal occurrences in Phi_w for the toy verifier (n = 1), cells 0..N+2."""
    nvars = (Nn + 1) * (Nn + 3) * (nq + ng)
    into = {q: sum(1 for v in VD.values() if v[0] == q) for q in VQ}
    write = {b: sum(1 for v in VD.values() if v[1] == b) for b in GAMMA}
    trans = sum(Nn * (Nn + 1) * (1 + 2 * into[q]) for q in VQ) + \
        sum(Nn * (Nn + 1) * (1 + 2 * write[b] + 1 + nq) for b in GAMMA)
    boundary = (Nn + 1) * 2 * (nq + ng)
    init = (nq + ng) * (Nn + 3)                  # every time-0 variable outside the advice cells is fixed
    advice = (Nn - 1) * (ng + ng * (ng - 1))     # exactly one symbol per advice cell
    accept = (Nn + 1) * (Nn + 3)
    return nvars, trans + boundary + init + advice + accept


v20, s20 = formula_size(20)
v40, s40 = formula_size(40)
check("variables: (N+1)(N+3)(|Q|+|Gamma|) for the window of cells 0..N+2", v20 == 21 * 23 * 11)
check("formula size grows quadratically: size(2N)/size(N) -> 4 (N = 20, 40)", 3.7 < s40 / s20 < 4.1, f"{s40 / s20:.3f}")

# ---------------------------------------------------------------- review additions (R4): the two deviations from the book
# (1) The advice view, rejection half. Page: N rejects w iff for some t, M rejects (w, x) within t steps for EVERY x of
# length t. Book: N rejects w iff M rejects (w, x) for all x in Omega^*. The book's version breaks when the tree has an
# infinite branch and no accepting leaf, whatever M does once its advice is used up.
def page_advice_rejects(delta, w, r, max_t):
    """Some t <= max_t such that every advice string of length t makes M reject within t steps."""
    digits = "".join(str(i) for i in range(1, r + 1))
    return any(all(advice_run(delta, w, x, r)[0] == "reject" for x in product(digits, repeat=t))
               for t in range(1, max_t + 1))


def advice_run_unbounded(delta, w, x, r, on_exhaust, budget=200):
    """M on (w, x) run to the end: when the advice is used up, M either rejects (no transition on a blank advice
    cell) or keeps taking the last option. Returns 'accept', 'reject', or None (still running after budget steps)."""
    conf, s = start_conf(w), 0
    while conf[0] not in ("accept", "reject"):
        if s >= budget:
            return None
        ch = children(delta, conf)
        if s < len(x):
            om = int(x[s])
        elif on_exhaust == "reject":
            return "reject"
        else:
            om = r
        conf = ch[min(om, len(ch)) - 1]
        s += 1
    return conf[0]


ok, tried = True, 0
for delta in (N, NP):
    for w in strings("01", 6):
        tried += 1
        ok &= page_advice_rejects(delta, w, branching(delta), len(w) + 3) == (bfs(delta, w, len(w) + 3)[0] == "reject")
for _ in range(200):
    d = random_ntm(rng.randint(1, 3), rng.randint(1, 3))
    r = max(1, branching(d))
    for w in strings("01", 2):
        tried += 1
        ok &= page_advice_rejects(d, w, r, 6) == (bfs(d, w, 6)[0] == "reject")
check("advice view (page's form): 'some t, every advice of length t rejects within t steps' iff N rejects (BFS)", ok,
      f"{tried} cases")
N_GIVEUP = dict(N)                         # N, but the looping state may also give up: choice 1 loop on, choice 2 reject
N_GIVEUP.update({("loop", a): [("loop", a, +1), ("reject", a, +1)] for a in GAMMA})
w0 = "010"
all_x = [x for t in range(0, 9) for x in product("12", repeat=t)]
book_1 = all(advice_run_unbounded(N, w0, x, 2, "reject") == "reject" for x in all_x)
book_2 = all(advice_run_unbounded(N_GIVEUP, w0, x, 2, "last") == "reject" for x in all_x)
check("the book's form fails on 010: every advice string (|x| <= 8) makes M reject — for N if M rejects when the advice "
      "runs out, for N with a give-up option in 'loop' if M then takes the last option — yet neither machine rejects "
      "010 (each has an infinite branch)",
      book_1 and book_2 and bfs(N, w0, 30)[0] is None and bfs(N_GIVEUP, w0, 30)[0] is None,
      f"N: {book_1}, give-up variant: {book_2}")

# (2) The Cook-Levin cell window. Page: cells 0..N+2 (sentinels 0 and N+2, advice n+2..N+1). Book: cells 0..N+1
# (sentinel at N+1, advice n+2..N, transitions and acceptance for cells 1..N). A verifier that accepts at step N with a
# right move leaves its head on cell N+1, which the book's window cannot represent.
V2D = {("scan", "0"): ("scan", "0", +1), ("scan", "1"): ("scan", "1", +1), ("scan", B): ("adv", B, +1),
       ("adv", "1"): ("accept", "1", +1), ("adv", "0"): ("reject", "0", +1), ("adv", B): ("reject", B, +1)}
V2Q = ["scan", "adv", "accept", "reject"]
V2 = TM(V2D, start="scan")


def phi_window(vd, vq, w, Nn, last):
    """Phi_w evaluated literally on the window of cells 0..last: sentinels 0 and last, transition constraints for
    cells 1..last-1, advice cells n+2..last-1, acceptance over all cells and times 0..N. Satisfiable?"""
    n, cells = len(w), range(0, last + 1)
    adv_cells = list(range(n + 2, last))
    for adv in product(GAMMA, repeat=len(adv_cells)):
        Q = {(i, q): False for i in cells for q in vq}
        Tt = {(i, a): False for i in cells for a in GAMMA}
        Q[(1, "scan")] = True
        for i in range(1, n + 1):
            Tt[(i, w[i - 1])] = True
        if n + 1 < last:
            Tt[(n + 1, B)] = True
        for i, a in zip(adv_cells, adv):
            Tt[(i, a)] = True
        accepted = False
        for t in range(1, Nn + 1):
            Q2 = {(i, q): False for i in cells for q in vq}
            T2 = {(i, a): False for i in cells for a in GAMMA}
            for i in range(1, last):
                for q in vq:
                    Q2[(i, q)] = any(Q[(i - 1, p)] and Tt[(i - 1, a)] for (p, a), (qq, _b, d) in vd.items()
                                     if qq == q and d == +1) or \
                        any(Q[(i + 1, p)] and Tt[(i + 1, a)] for (p, a), (qq, _b, d) in vd.items() if qq == q and d == -1)
                for bsym in GAMMA:
                    T2[(i, bsym)] = any(Q[(i, p)] and Tt[(i, a)] for (p, a), (_q, bb, _d) in vd.items() if bb == bsym) \
                        or (Tt[(i, bsym)] and not any(Q[(i, q)] for q in vq))
            Q, Tt = Q2, T2
            accepted = accepted or any(Q[(i, "accept")] for i in cells)
        if accepted:
            return True
    return False


def direct_any(tm, w, Nn):
    return any(tm.run(w + B + "".join(adv), max_steps=Nn)[0] == "accept" for adv in product(GAMMA, repeat=max(0, Nn - len(w))))


ok_page, ok_toy = True, True
for Nn in range(1, 7):
    for n in range(0, 3):
        if Nn - n > 4:
            continue
        for w in strings("01", n, n):
            ok_page &= phi_window(V2D, V2Q, w, Nn, Nn + 2) == direct_any(V2, w, Nn)
            ok_toy &= phi_window(VD, VQ, w, Nn, Nn + 2) == phi_satisfiable(w, Nn)
r2 = V2.run("0" + B + "1", max_steps=3)
check("page's window 0..N+2: Phi_w agrees with direct simulation for a verifier that accepts with a final right move "
      "(and with the first evaluator on the toy verifier)", ok_page and ok_toy)
check("book's window 0..N+1 misses an accepting run: w = 0, N = 3, the verifier accepts w□1 at step N = 3 with its head "
      "on cell N+1 = 4, but the formula on cells 0..N+1 is unsatisfiable (on cells 0..N+2 it is satisfiable)",
      r2[0] == "accept" and r2[1] == 3 and r2[3] == 3 and not phi_window(V2D, V2Q, "0", 3, 4)
      and phi_window(V2D, V2Q, "0", 3, 5), str(r2[:2]))


# (3) Only the advice cells are constrained to hold exactly one symbol (concepts/cook-levin-theorem). After the verifier
# halts there is no transition, so the transition constraints leave the head's cell empty; a constraint "every cell
# holds exactly one symbol at every time" would therefore make Phi_w unsatisfiable whenever M halts before time N.
def forced_rows(vd, vq, w, Nn, adv):
    """The assignment forced by the page's constraints (cells 0..N+2) for one choice of advice: list of (Q, T) by time."""
    n, last = len(w), Nn + 2
    cells = range(0, last + 1)
    Q = {(i, q): False for i in cells for q in vq}
    Tt = {(i, a): False for i in cells for a in GAMMA}
    Q[(1, "scan")] = True
    for i in range(1, n + 1):
        Tt[(i, w[i - 1])] = True
    Tt[(n + 1, B)] = True
    for i, a in zip(range(n + 2, last), adv):
        Tt[(i, a)] = True
    rows = [(Q, Tt)]
    for _t in range(1, Nn + 1):
        Q2 = {(i, q): False for i in cells for q in vq}
        T2 = {(i, a): False for i in cells for a in GAMMA}
        for i in range(1, last):
            for q in vq:
                Q2[(i, q)] = any(Q[(i - 1, p)] and Tt[(i - 1, a)] for (p, a), (qq, _b, d) in vd.items() if qq == q and d == +1) \
                    or any(Q[(i + 1, p)] and Tt[(i + 1, a)] for (p, a), (qq, _b, d) in vd.items() if qq == q and d == -1)
            for bsym in GAMMA:
                T2[(i, bsym)] = any(Q[(i, p)] and Tt[(i, a)] for (p, a), (_q, bb, _d) in vd.items() if bb == bsym) \
                    or (Tt[(i, bsym)] and not any(Q[(i, q)] for q in vq))
        Q, Tt = Q2, T2
        rows.append((Q, Tt))
    return rows


rows = forced_rows(V2D, V2Q, "0", 4, "111")          # V2 accepts 0□1 at step 3 < N = 4, head on cell 4
accepts_at = [t for t, (Q, _T) in enumerate(rows) if any(Q[(i, "accept")] for i in range(0, 7))]
one_symbol = lambda T, i: sum(T[(i, a)] for a in GAMMA) == 1
check("Cook-Levin: only advice cells need 'exactly one symbol'. For w = 0, N = 4 the forced assignment accepts at time 3, "
      "every cell 1..N+1 holds one symbol at times 0..3, and the head's cell 4 is empty at time 4 (no move after accept)",
      accepts_at == [3] and all(one_symbol(rows[t][1], i) for t in range(4) for i in range(1, 6))
      and not any(rows[4][1][(4, a)] for a in GAMMA))

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: {FAIL}")
sys.exit(1 if FAIL else 0)
