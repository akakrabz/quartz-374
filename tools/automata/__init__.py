"""Small, dependency-free automata toolkit used to verify every example on the site.

    from automata import DFA, NFA, Regex, CFG, TM, strings

Strings are Python str over single-character symbols. The empty string is "".
Every construction follows the textbook (Erickson, *Models of Computation*)
exactly, so state counts printed by the checks match the book.
"""
from .core import (
    EPS,
    DFA,
    NFA,
    strings,
    first_difference,
    language_upto,
)
from .regex import Regex, thompson, eliminate_states
from .cfg import CFG
from .tm import TM

__all__ = [
    "EPS",
    "DFA",
    "NFA",
    "Regex",
    "thompson",
    "eliminate_states",
    "CFG",
    "TM",
    "strings",
    "first_difference",
    "language_upto",
]
