"""Strings, DFAs and NFAs (with epsilon-transitions), following Erickson's definitions.

DFA  M = (Sigma, Q, s, A, delta),  delta: Q x Sigma -> Q          (total function)
NFA  M = (Sigma, Q, s, A, delta),  delta: Q x (Sigma + {eps}) -> 2^Q

Conventions
-----------
* Symbols are single characters; strings are Python str; EPS = "" labels
  epsilon-transitions.
* A DFA's transition function may be given as a dict {(q, a): q'} or as a
  callable step(q, a) -> q'. ``DFA.explore`` builds the reachable part of a
  machine from a start state and a step function (the "DFAs are algorithms"
  view of Chapter 3: states are the possible values of the program's variables).
* The subset construction is the book's version: DFA states are *sets* S of
  NFA states, s' = {s}, A' = {S : eps-reach(S) meets A},
  delta'(S, a) = union over p in S, r in eps-reach(p) of delta(r, a).
"""
from collections import deque
from itertools import product

EPS = ""


def strings(alphabet, maxlen, minlen=0):
    """All strings over `alphabet` with minlen <= length <= maxlen, shortest first."""
    alphabet = list(alphabet)
    for n in range(minlen, maxlen + 1):
        for t in product(alphabet, repeat=n):
            yield "".join(t)


def language_upto(accepts, alphabet, maxlen):
    """The set of strings of length <= maxlen accepted by the predicate `accepts`."""
    return {w for w in strings(alphabet, maxlen) if accepts(w)}


def first_difference(pred1, pred2, alphabet, maxlen):
    """Shortest string (length <= maxlen) on which two predicates disagree, or None."""
    for w in strings(alphabet, maxlen):
        if bool(pred1(w)) != bool(pred2(w)):
            return w
    return None


# ----------------------------------------------------------------------------- DFA
class DFA:
    def __init__(self, alphabet, states, start, accepting, delta):
        self.alphabet = list(alphabet)
        self.states = list(states)
        self.start = start
        self.accepting = set(accepting)
        if callable(delta):
            self._delta = {(q, a): delta(q, a) for q in self.states for a in self.alphabet}
        else:
            self._delta = dict(delta)
        # validate: total function into Q
        qs = set(self.states)
        if start not in qs:
            raise ValueError(f"start state {start!r} not in Q")
        if not self.accepting <= qs:
            raise ValueError(f"accepting states {self.accepting - qs} not in Q")
        for q in self.states:
            for a in self.alphabet:
                if (q, a) not in self._delta:
                    raise ValueError(f"delta({q!r}, {a!r}) undefined (a DFA needs a total function)")
                if self._delta[(q, a)] not in qs:
                    raise ValueError(f"delta({q!r}, {a!r}) = {self._delta[(q, a)]!r} not in Q")

    # -- construction helpers
    @classmethod
    def explore(cls, alphabet, start, step, accept):
        """Reachable DFA from a start value, a step function and an accept predicate."""
        alphabet = list(alphabet)
        order, seen, delta = [start], {start}, {}
        queue = deque([start])
        while queue:
            q = queue.popleft()
            for a in alphabet:
                r = step(q, a)
                delta[(q, a)] = r
                if r not in seen:
                    seen.add(r)
                    order.append(r)
                    queue.append(r)
        return cls(alphabet, order, start, [q for q in order if accept(q)], delta)

    def delta(self, q, a):
        return self._delta[(q, a)]

    def delta_star(self, q, w):
        for a in w:
            q = self._delta[(q, a)]
        return q

    def run(self, w):
        """The list of states visited on input w (length |w| + 1)."""
        q = self.start
        trace = [q]
        for a in w:
            q = self._delta[(q, a)]
            trace.append(q)
        return trace

    def accepts(self, w):
        return self.delta_star(self.start, w) in self.accepting

    __call__ = accepts

    def reachable(self):
        seen, queue = {self.start}, deque([self.start])
        while queue:
            q = queue.popleft()
            for a in self.alphabet:
                r = self._delta[(q, a)]
                if r not in seen:
                    seen.add(r)
                    queue.append(r)
        return seen

    def trim(self):
        """Remove unreachable states."""
        R = self.reachable()
        sts = [q for q in self.states if q in R]
        return DFA(self.alphabet, sts, self.start, self.accepting & R,
                   {(q, a): self._delta[(q, a)] for q in sts for a in self.alphabet})

    def complement(self):
        return DFA(self.alphabet, self.states, self.start, set(self.states) - self.accepting, self._delta)

    def product(self, other, mode="and"):
        """Product construction (Chapter 3.6). mode: and, or, diff, xor, or a function (bool, bool) -> bool."""
        if list(self.alphabet) != list(other.alphabet):
            raise ValueError("product needs the same alphabet")
        ops = {
            "and": lambda x, y: x and y,
            "or": lambda x, y: x or y,
            "diff": lambda x, y: x and not y,
            "xor": lambda x, y: x != y,
        }
        op = ops[mode] if isinstance(mode, str) else mode
        Q = [(p, q) for p in self.states for q in other.states]
        delta = {((p, q), a): (self._delta[(p, a)], other._delta[(q, a)]) for (p, q) in Q for a in self.alphabet}
        A = [(p, q) for (p, q) in Q if op(p in self.accepting, q in other.accepting)]
        return DFA(self.alphabet, Q, (self.start, other.start), A, delta)

    # -- minimization (Moore's table-filling, Chapter 3.10)
    def distinguishable_pairs(self):
        """Set of frozenset({p, q}) of distinguishable reachable states, by Moore's passes."""
        Q = sorted(self.reachable(), key=self.states.index)
        dist = set()
        for i, p in enumerate(Q):
            for q in Q[i + 1:]:
                if (p in self.accepting) != (q in self.accepting):
                    dist.add(frozenset((p, q)))
        passes = 0
        changed = True
        while changed:
            changed = False
            passes += 1
            for i, p in enumerate(Q):
                for q in Q[i + 1:]:
                    pq = frozenset((p, q))
                    if pq in dist:
                        continue
                    for a in self.alphabet:
                        r, s = self._delta[(p, a)], self._delta[(q, a)]
                        if r != s and frozenset((r, s)) in dist:
                            dist.add(pq)
                            changed = True
                            break
        self._moore_passes = passes
        return dist

    def minimize(self):
        """The minimal DFA (unreachable states removed, equivalent states merged).
        States of the result are frozensets of original states (equivalence classes)."""
        Q = sorted(self.reachable(), key=self.states.index)
        dist = self.distinguishable_pairs()
        classes = []
        for q in Q:
            for c in classes:
                rep = next(iter(c))
                if frozenset((rep, q)) not in dist:
                    c.add(q)
                    break
            else:
                classes.append({q})
        cls_of = {}
        for c in classes:
            fc = frozenset(c)
            for q in c:
                cls_of[q] = fc
        states = [cls_of[q] for q in Q]
        uniq = []
        for s in states:
            if s not in uniq:
                uniq.append(s)
        delta = {(c, a): cls_of[self._delta[(next(iter(c)), a)]] for c in uniq for a in self.alphabet}
        A = [c for c in uniq if next(iter(c)) in self.accepting]
        return DFA(self.alphabet, uniq, cls_of[self.start], A, delta)

    def num_states(self):
        return len(self.states)

    def equivalent(self, other):
        """Exact equivalence. Returns (True, None) or (False, shortest counterexample)."""
        return equivalent(self, other)

    def to_nfa(self):
        return NFA(self.alphabet, self.states, self.start, self.accepting,
                   {(q, a): {self._delta[(q, a)]} for q in self.states for a in self.alphabet})

    def __repr__(self):
        return f"DFA({len(self.states)} states, start={self.start!r}, accepting={sorted(map(str, self.accepting))})"


def equivalent(m1, m2):
    """Exact language equivalence of two DFAs by BFS over the product; returns (bool, witness)."""
    if list(m1.alphabet) != list(m2.alphabet):
        raise ValueError("different alphabets")
    start = (m1.start, m2.start)
    parent = {start: None}
    queue = deque([start])
    while queue:
        p, q = queue.popleft()
        if (p in m1.accepting) != (q in m2.accepting):
            # reconstruct
            w = []
            node = (p, q)
            while parent[node] is not None:
                prev, a = parent[node]
                w.append(a)
                node = prev
            return False, "".join(reversed(w))
        for a in m1.alphabet:
            nxt = (m1.delta(p, a), m2.delta(q, a))
            if nxt not in parent:
                parent[nxt] = ((p, q), a)
                queue.append(nxt)
    return True, None


# ----------------------------------------------------------------------------- NFA
class NFA:
    """NFA with optional epsilon-transitions. delta: {(q, a): set(...)} with a = EPS allowed."""

    def __init__(self, alphabet, states, start, accepting, delta):
        self.alphabet = list(alphabet)
        self.states = list(states)
        self.start = start
        self.accepting = set(accepting)
        self._delta = {}
        for (q, a), targets in dict(delta).items():
            if a != EPS and a not in self.alphabet:
                raise ValueError(f"symbol {a!r} not in the alphabet")
            self._delta.setdefault((q, a), set()).update(targets)
        qs = set(self.states)
        if start not in qs:
            raise ValueError("start state not in Q")
        for (q, a), T in self._delta.items():
            if q not in qs or not set(T) <= qs:
                raise ValueError(f"transition {(q, a)} -> {T} leaves Q")

    def delta(self, q, a):
        return self._delta.get((q, a), set())

    def eps_reach(self, S):
        if not isinstance(S, (set, frozenset, list, tuple)):
            S = {S}
        seen = set(S)
        stack = list(S)
        while stack:
            q = stack.pop()
            for r in self._delta.get((q, EPS), ()):
                if r not in seen:
                    seen.add(r)
                    stack.append(r)
        return frozenset(seen)

    def step(self, S, a):
        """delta(eps-reach(S), a) — one symbol, before closing again."""
        out = set()
        for p in self.eps_reach(S):
            out |= self._delta.get((p, a), set())
        return frozenset(out)

    def current_states(self, w):
        """eps-reach of the set of states the NFA can be in after reading w."""
        S = self.eps_reach({self.start})
        for a in w:
            S = self.eps_reach(self.step(S, a))
        return S

    def accepts(self, w):
        return bool(self.current_states(w) & self.accepting)

    __call__ = accepts

    def has_epsilon(self):
        return any(a == EPS and T for (q, a), T in self._delta.items())

    def num_transitions(self):
        return sum(len(T) for T in self._delta.values())

    def remove_epsilon(self):
        """The book's epsilon-removal: A' = {q : eps-reach(q) meets A}, delta'(q,a) = delta(eps-reach(q), a)."""
        A2 = {q for q in self.states if self.eps_reach({q}) & self.accepting}
        delta = {}
        for q in self.states:
            for a in self.alphabet:
                T = set()
                for r in self.eps_reach({q}):
                    T |= self._delta.get((r, a), set())
                if T:
                    delta[(q, a)] = T
        return NFA(self.alphabet, self.states, self.start, A2, delta)

    def subset_construction(self):
        """Incremental (breadth-first) subset construction, exactly as in the book.

        Returns (dfa, rows) where rows lists, in discovery order, tuples
        (S, eps_reach(S), accepting?, {a: delta'(S, a)}). DFA states are frozensets.
        The empty set appears as a state only if it is reachable."""
        s0 = frozenset({self.start})
        order, seen = [s0], {s0}
        queue = deque([s0])
        delta, rows = {}, []
        while queue:
            S = queue.popleft()
            R = self.eps_reach(S)
            trans = {}
            for a in self.alphabet:
                T = set()
                for r in R:
                    T |= self._delta.get((r, a), set())
                T = frozenset(T)
                delta[(S, a)] = T
                trans[a] = T
                if T not in seen:
                    seen.add(T)
                    order.append(T)
                    queue.append(T)
            rows.append((S, R, bool(R & self.accepting), trans))
        A = [S for S in order if self.eps_reach(S) & self.accepting]
        return DFA(self.alphabet, order, s0, A, delta), rows

    def to_dfa(self):
        return self.subset_construction()[0]

    def reverse(self):
        """Lemma 4.4, proof 2 (for an NFA without epsilon-transitions given as DFA.to_nfa()):
        reverse every edge, new start with eps-edges to the old accepting states, accept only s."""
        new = ("rev-start",)
        delta = {(new, EPS): set(self.accepting)}
        for (p, a), T in self._delta.items():
            for q in T:
                delta.setdefault((q, a), set()).add(p)
        return NFA(self.alphabet, [new] + self.states, new, {self.start}, delta)

    def __repr__(self):
        return f"NFA({len(self.states)} states, {self.num_transitions()} transitions)"
