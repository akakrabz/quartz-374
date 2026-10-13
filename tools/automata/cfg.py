"""Context-free grammars: membership (Earley), languages up to a length, parse-tree counts.

Grammar notation accepted by CFG.parse:

    S -> A | B
    A -> 0A | 0C
    C -> ε | 0C1

* Nonterminals are the names on the left-hand sides. By default every
  left-hand side is a single character; multi-character names (S0, A') are
  allowed if listed in `nonterminals=`; right-hand sides are then tokenized
  greedily, longest name first.
* ε (or "eps") is the empty right-hand side. Terminals are single characters.
"""
from functools import lru_cache
from .core import strings


class CFG:
    def __init__(self, start, rules, terminals=None):
        """rules: {A: [tuple_of_symbols, ...]} (empty tuple = ε)."""
        self.start = start
        self.rules = {A: [tuple(r) for r in rhs] for A, rhs in rules.items()}
        self.nonterminals = list(self.rules)
        nts = set(self.nonterminals)
        found = {x for rhs in self.rules.values() for r in rhs for x in r if x not in nts}
        self.terminals = sorted(found if terminals is None else set(terminals))
        for A, rhs in self.rules.items():
            for r in rhs:
                for x in r:
                    if x not in nts and x not in self.terminals:
                        raise ValueError(f"symbol {x!r} in rule {A} -> {''.join(r)} is not a terminal")
        if start not in nts:
            raise ValueError("start symbol has no rules")

    # ----------------------------------------------------------------- parsing the notation
    @classmethod
    def parse(cls, text, start=None, nonterminals=None, terminals=None):
        lines = [ln.strip() for ln in text.replace(";", "\n").splitlines() if ln.strip()]
        lhs_names = [ln.split("->")[0].strip() for ln in lines]
        names = sorted(set(nonterminals or []) | set(lhs_names), key=len, reverse=True)
        rules = {}
        for ln in lines:
            left, right = ln.split("->")
            A = left.strip()
            for alt in right.split("|"):
                alt = alt.strip().replace("eps", "ε")
                if alt in ("ε", ""):
                    rules.setdefault(A, []).append(())
                    continue
                toks, i = [], 0
                alt = alt.replace(" ", "")
                while i < len(alt):
                    for nm in names:
                        if alt.startswith(nm, i):
                            toks.append(nm)
                            i += len(nm)
                            break
                    else:
                        if alt[i] == "ε":
                            i += 1
                            continue
                        toks.append(alt[i])
                        i += 1
                rules.setdefault(A, []).append(tuple(toks))
        return cls(start or lhs_names[0], rules, terminals)

    def __str__(self):
        out = []
        for A in self.nonterminals:
            alts = ["".join(r) if r else "ε" for r in self.rules[A]]
            out.append(f"{A} -> {' | '.join(alts)}")
        return "\n".join(out)

    def is_nonterminal(self, x):
        return x in self.rules

    # ----------------------------------------------------------------- Earley recognizer
    def generates(self, w, start=None):
        """True iff start =>* w. Earley's algorithm (handles ε-rules and left recursion)."""
        start = start or self.start
        n = len(w)
        nullable = self.nullable()
        # item: (A, rhs_index, dot, origin)
        chart = [set() for _ in range(n + 1)]
        root = ("$ROOT", 0, 0, 0)
        rules = dict(self.rules)
        rules["$ROOT"] = [(start,)]
        chart[0].add(root)
        for i in range(n + 1):
            agenda = list(chart[i])
            while agenda:
                A, ri, dot, org = agenda.pop()
                rhs = rules[A][ri]
                if dot < len(rhs):
                    X = rhs[dot]
                    if X in rules:  # predict
                        for k in range(len(rules[X])):
                            it = (X, k, 0, i)
                            if it not in chart[i]:
                                chart[i].add(it)
                                agenda.append(it)
                        if X in nullable:  # Aycock–Horspool fix for nullable symbols
                            it = (A, ri, dot + 1, org)
                            if it not in chart[i]:
                                chart[i].add(it)
                                agenda.append(it)
                    elif i < n and w[i] == X:  # scan
                        chart[i + 1].add((A, ri, dot + 1, org))
                else:  # complete
                    for (B, rj, d2, o2) in list(chart[org]):
                        r2 = rules[B][rj]
                        if d2 < len(r2) and r2[d2] == A:
                            it = (B, rj, d2 + 1, o2)
                            if it not in chart[i]:
                                chart[i].add(it)
                                agenda.append(it)
        return ("$ROOT", 0, 1, 0) in chart[n]

    __call__ = generates

    def language(self, maxlen, start=None, alphabet=None):
        """All strings of length <= maxlen generated from `start` (default S)."""
        alphabet = alphabet or self.terminals
        return {w for w in strings(alphabet, maxlen) if self.generates(w, start)}

    def nullable(self):
        nul = set()
        changed = True
        while changed:
            changed = False
            for A, rhs in self.rules.items():
                if A in nul:
                    continue
                if any(all(x in nul for x in r) for r in rhs):
                    nul.add(A)
                    changed = True
        return nul

    # ----------------------------------------------------------------- parse trees
    def count_parse_trees(self, w, start=None, limit=10**9):
        """Number of parse trees of w (exact for grammars without ε-rules and unit cycles)."""
        start = start or self.start
        if any(r == () for rhs in self.rules.values() for r in rhs):
            raise ValueError("count_parse_trees needs an ε-free grammar")

        @lru_cache(maxsize=None)
        def count(X, i, j, depth=0):
            if X not in self.rules:
                return 1 if (j - i == 1 and w[i] == X) else 0
            if depth > len(w) * max(1, len(self.rules)) + 5:
                return 0  # unit-rule cycle guard
            total = 0
            for r in self.rules[X]:
                total += seq(r, i, j, depth)
            return min(total, limit)

        @lru_cache(maxsize=None)
        def seq(r, i, j, depth):
            if len(r) == 1:
                return count(r[0], i, j, depth + 1)
            total = 0
            for k in range(i + 1, j - len(r) + 2):
                left = count(r[0], i, k, depth + 1)
                if left:
                    total += left * seq(r[1:], k, j, depth)
            return total

        return count(start, 0, len(w))

    def is_cnf(self):
        """Chomsky normal form: S on no right side; S -> ε allowed; else A -> BC or A -> a."""
        for A, rhs in self.rules.items():
            for r in rhs:
                if r == ():
                    if A != self.start:
                        return False, f"{A} -> ε"
                    continue
                if any(x == self.start for x in r):
                    return False, f"start symbol on a right side: {A} -> {''.join(r)}"
                if len(r) == 1 and r[0] in self.terminals:
                    continue
                if len(r) == 2 and all(x in self.rules for x in r):
                    continue
                return False, f"{A} -> {''.join(r)}"
        return True, None
