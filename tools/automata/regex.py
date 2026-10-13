"""Regular expressions in the book's syntax, Thompson's algorithm, and state elimination.

Syntax accepted by Regex(text):
    union        R + S
    concatenation  RS            (juxtaposition)
    Kleene star  R*
    grouping     ( R )
    empty string ε  (also accepted: "eps")
    empty set    ∅  (also accepted: "{}")
    symbols      any other single character except whitespace
Precedence: * binds tightest, then concatenation, then +  (Chapter 2.3).

AST: ("empty",), ("eps",), ("sym", a), ("union", L, R), ("cat", L, R), ("star", X)
"""
from .core import DFA, NFA, EPS, equivalent

SPECIAL = set("+*()")


def _tokenize(text):
    text = text.replace("eps", "ε").replace("{}", "∅")
    return [c for c in text if not c.isspace()]


class _Parser:
    def __init__(self, text):
        self.toks = _tokenize(text)
        self.i = 0

    def peek(self):
        return self.toks[self.i] if self.i < len(self.toks) else None

    def eat(self, c=None):
        t = self.peek()
        if c is not None and t != c:
            raise SyntaxError(f"expected {c!r} at position {self.i}, got {t!r}")
        self.i += 1
        return t

    def parse(self):
        node = self.union()
        if self.peek() is not None:
            raise SyntaxError(f"unexpected {self.peek()!r} at position {self.i}")
        return node

    def union(self):
        node = self.cat()
        while self.peek() == "+":
            self.eat("+")
            node = ("union", node, self.cat())
        return node

    def cat(self):
        parts = []
        while self.peek() is not None and self.peek() not in ("+", ")"):
            parts.append(self.star())
        if not parts:
            raise SyntaxError(f"empty expression at position {self.i}")
        node = parts[0]
        for p in parts[1:]:
            node = ("cat", node, p)
        return node

    def star(self):
        node = self.atom()
        while self.peek() == "*":
            self.eat("*")
            node = ("star", node)
        return node

    def atom(self):
        t = self.peek()
        if t == "(":
            self.eat("(")
            node = self.union()
            self.eat(")")
            return node
        if t is None or t in SPECIAL:
            raise SyntaxError(f"unexpected {t!r} at position {self.i}")
        self.eat()
        if t == "ε":
            return ("eps",)
        if t == "∅":
            return ("empty",)
        return ("sym", t)


def size(node):
    """Number of nodes of the expression tree when strings are single leaves (Chapter 2.5)."""
    kind = node[0]
    if kind in ("empty", "eps", "sym"):
        return 1
    if kind == "star":
        return 1 + size(node[1])
    if kind == "cat":
        # merge maximal chains of symbols into one string leaf, as the book does
        flat = _flatten_cat(node)
        n, run = 0, 0
        for f in flat:
            if f[0] == "sym":
                run += 1
            else:
                if run:
                    n += 1
                    run = 0
                n += size(f)
        if run:
            n += 1
        k = sum(1 for _ in _cat_groups(flat))
        return n + (k - 1)
    return 1 + size(node[1]) + size(node[2])


def _flatten_cat(node):
    if node[0] == "cat":
        return _flatten_cat(node[1]) + _flatten_cat(node[2])
    return [node]


def _cat_groups(flat):
    run = False
    for f in flat:
        if f[0] == "sym":
            if not run:
                run = True
                yield "string"
        else:
            run = False
            yield f


def to_str(node, prec=0):
    """Pretty-print with minimal parentheses (prec: 0 union, 1 concat, 2 star)."""
    kind = node[0]
    if kind == "empty":
        return "∅"
    if kind == "eps":
        return "ε"
    if kind == "sym":
        return node[1]
    if kind == "star":
        return to_str(node[1], 2) + "*"
    if kind == "cat":
        s = to_str(node[1], 1) + to_str(node[2], 1)
        return f"({s})" if prec > 1 else s
    s = to_str(node[1], 0) + "+" + to_str(node[2], 0)
    return f"({s})" if prec > 0 else s


def thompson(node, alphabet=None, classes=False):
    """Thompson's algorithm exactly as in Chapter 4.6.

    Base cases: ∅ -> s, t with no transition; ε -> s -ε-> t; a -> s -a-> t.
    S+T: new s, t; s -ε-> s_S, s_T; t_S, t_T -ε-> t.   ST: t_S -ε-> s_T (no new states).
    S*:  new s, t; s -ε-> s_S; t_S -ε-> t; t_S -ε-> s_S; s -ε-> t.
    With classes=True a union of single symbols (like 0+1) becomes one two-state
    gadget with one edge per symbol (how the book draws (0+1)* in its figures).
    Returns an NFA with exactly one accepting state, different from its start state."""
    counter = [0]
    delta = {}

    def new():
        counter[0] += 1
        return counter[0] - 1

    def add(p, a, q):
        delta.setdefault((p, a), set()).add(q)

    def symbols_of_union(n):
        if n[0] == "sym":
            return [n[1]]
        if n[0] == "union":
            l, r = symbols_of_union(n[1]), symbols_of_union(n[2])
            if l is not None and r is not None:
                return l + r
        return None

    def build(n):
        kind = n[0]
        if classes and kind == "union":
            syms = symbols_of_union(n)
            if syms is not None:
                s, t = new(), new()
                for a in syms:
                    add(s, a, t)
                return s, t
        if kind == "empty":
            return new(), new()
        if kind == "eps":
            s, t = new(), new()
            add(s, EPS, t)
            return s, t
        if kind == "sym":
            s, t = new(), new()
            add(s, n[1], t)
            return s, t
        if kind == "cat":
            s1, t1 = build(n[1])
            s2, t2 = build(n[2])
            add(t1, EPS, s2)
            return s1, t2
        if kind == "union":
            s = new()
            s1, t1 = build(n[1])
            s2, t2 = build(n[2])
            t = new()
            add(s, EPS, s1)
            add(s, EPS, s2)
            add(t1, EPS, t)
            add(t2, EPS, t)
            return s, t
        if kind == "star":
            s = new()
            s1, t1 = build(n[1])
            t = new()
            add(s, EPS, s1)
            add(t1, EPS, t)
            add(t1, EPS, s1)
            add(s, EPS, t)
            return s, t
        raise ValueError(n)

    s, t = build(node)
    if alphabet is None:
        alphabet = sorted(_symbols(node))
    return NFA(alphabet, list(range(counter[0])), s, {t}, delta)


def _symbols(node):
    kind = node[0]
    if kind == "sym":
        return {node[1]}
    if kind in ("empty", "eps"):
        return set()
    out = set()
    for child in node[1:]:
        out |= _symbols(child)
    return out


class Regex:
    def __init__(self, text, alphabet=None):
        self.text = text
        self.ast = _Parser(text).parse()
        syms = _symbols(self.ast)
        self.alphabet = sorted(set(alphabet) if alphabet is not None else syms)
        if not syms <= set(self.alphabet):
            raise ValueError(f"expression uses symbols {syms - set(self.alphabet)} outside the alphabet")
        self._nfa = thompson(self.ast, self.alphabet)
        self._dfa = None

    def nfa(self):
        return self._nfa

    def dfa(self):
        if self._dfa is None:
            self._dfa = self._nfa.to_dfa().minimize()
        return self._dfa

    def matches(self, w):
        return self.dfa().accepts(w)

    __call__ = matches

    def equivalent(self, other):
        """Exact equivalence with another Regex or DFA. Returns (bool, shortest counterexample)."""
        o = other.dfa() if isinstance(other, Regex) else other
        if isinstance(o, NFA):
            o = o.to_dfa()
        mine = self.dfa()
        if list(o.alphabet) != list(mine.alphabet):
            raise ValueError("different alphabets")
        return equivalent(mine, o)

    def __str__(self):
        return to_str(self.ast)

    def __repr__(self):
        return f"Regex({self.text!r})"


# ----------------------------------------------------------------------------- state elimination
def _u(a, b):
    if a == ("empty",):
        return b
    if b == ("empty",):
        return a
    if a == b:
        return a
    return ("union", a, b)


def _c(a, b):
    if a == ("empty",) or b == ("empty",):
        return ("empty",)
    if a == ("eps",):
        return b
    if b == ("eps",):
        return a
    return ("cat", a, b)


def _s(a):
    if a in (("empty",), ("eps",)):
        return ("eps",)
    if a[0] == "star":
        return a
    return ("star", a)


def eliminate_states(machine, order=None):
    """State elimination (Chapter 4.8; McNaughton–Yamada) on a DFA or NFA.

    Adds a new start s and target t with epsilon-edges, then removes the old
    states in `order` (default: the machine's state order) with
        R'(p -> r) = R(p -> r) + R(p -> q) R(q -> q)* R(q -> r).
    Returns the AST of the final expression R(s -> t), lightly simplified
    (∅ and ε absorbed, x** = x*)."""
    if isinstance(machine, DFA):
        machine = machine.to_nfa()
    S, T = ("s",), ("t",)
    states = list(machine.states)
    R = {}

    def get(p, q):
        return R.get((p, q), ("empty",))

    def put(p, q, x):
        R[(p, q)] = _u(get(p, q), x)

    for (p, a), targets in machine._delta.items():
        lab = ("eps",) if a == EPS else ("sym", a)
        for q in targets:
            put(p, q, lab)
    put(S, machine.start, ("eps",))
    for q in machine.accepting:
        put(q, T, ("eps",))
    order = list(order) if order is not None else states
    remaining = [S] + states + [T]
    for q in order:
        loop = _s(get(q, q))
        preds = [p for p in remaining if p != q and get(p, q) != ("empty",)]
        succs = [r for r in remaining if r != q and get(q, r) != ("empty",)]
        for p in preds:
            for r in succs:
                put(p, r, _c(_c(get(p, q), loop), get(q, r)))
        remaining.remove(q)
        for k in [k for k in R if q in k]:
            del R[k]
    return get(S, T)
