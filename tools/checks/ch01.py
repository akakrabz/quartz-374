#!/usr/bin/env python3
"""Checks for every concrete claim on content/1-models-of-computation/01-strings.md.

Every function below follows the page's recursive definition literally: a string is either "" (epsilon) or a
pair a·x of a first symbol and a shorter string; Python's + is used only to build the pair a·x (cons). The
lemmas and facts are then checked by brute force over all strings up to the stated lengths."""
import os
import sys
from functools import lru_cache
from itertools import combinations, product

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from automata import strings  # noqa: E402

FAIL = []


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAIL.append(name)


# ---------------------------------------------------------------- the recursive definitions on the page
def cons(a, x):
    """a·x: the pair (a, x) — one symbol in front of a string (the small dot)."""
    assert len(a) == 1
    return a + x


def length(w):                       # |ε| = 0, |ax| = 1 + |x|
    return 0 if w == "" else 1 + length(w[1:])


def cat(w, z):                       # ε•z = z, (ax)•z = a·(x•z)
    return z if w == "" else cons(w[0], cat(w[1:], z))


def count(a, w):                     # #(a, ε) = 0, #(a, bx) = [a = b] + #(a, x)
    return 0 if w == "" else (1 if w[0] == a else 0) + count(a, w[1:])


def rev(w):                          # ε^R = ε, (ax)^R = x^R • a
    return "" if w == "" else cat(rev(w[1:]), w[0])


def power(w, n):                     # w^0 = ε, w^n = w • w^(n-1)
    return "" if n == 0 else cat(w, power(w, n - 1))


def comp(w):                         # ε^c = ε, (0x)^c = 1·x^c, (1x)^c = 0·x^c
    return "" if w == "" else cons({"0": "1", "1": "0"}[w[0]], comp(w[1:]))


def swap(w):                         # swap(ε) = ε, swap(a) = a, swap(abx) = b·a·swap(x)
    if len(w) <= 1:
        return w
    return cons(w[1], cons(w[0], swap(w[2:])))


def index(w, i):                     # w_i := a if w = ax and i = 1; x_(i-1) if w = ax and i > 1
    if w == "" or i < 1:
        return None                  # undefined
    return w[0] if i == 1 else index(w[1:], i - 1)


def sub(w, i, j):                    # w[i..j] := ε if j < i; w_i · w[i+1..j] otherwise
    if j < i:
        return ""
    a = index(w, i)
    rest = sub(w, i + 1, j)
    if a is None or rest is None:
        return None
    return cons(a, rest)


@lru_cache(maxsize=None)
def is_subseq(z, w):
    """z is a subsequence of w iff z = ε; or w = ax and z is a subsequence of x;
    or w = ax, z = ay and y is a subsequence of x."""
    if z == "":
        return True
    if w == "":
        return False
    return is_subseq(z, w[1:]) or (z[0] == w[0] and is_subseq(z[1:], w[1:]))


def by_deletion(w):
    """All strings obtained from w by deleting zero or more symbols (any positions)."""
    n = len(w)
    return {"".join(w[k] for k in S) for r in range(n + 1) for S in combinations(range(n), r)}


def is_substring(y, w):              # w = x y z for some strings x, z
    return any(cat(cat(w[:i], y), w[i + len(y):]) == w and w[i:i + len(y)] == y for i in range(len(w) - len(y) + 1))


def is_prefix(p, w):                 # p x = w for some x
    return any(cat(p, x) == w for x in [w[len(p):]]) and w[:len(p)] == p


def is_suffix(s, w):                 # x s = w for some x
    return len(s) <= len(w) and cat(w[:len(w) - len(s)], s) == w


B8 = list(strings("01", 8))
B7 = list(strings("01", 7))
B6 = list(strings("01", 6))
B5 = list(strings("01", 5))
B4 = list(strings("01", 4))
T6 = list(strings("abc", 6))

# ---------------------------------------------------------------- 1.1 strings as nested pairs
def nested(w):
    return "ε" if w == "" else f"({w[0]}, {nested(w[1:])})"


check("STRING = (S, (T, (R, (I, (N, (G, ε))))))", nested("STRING") == "(S, (T, (R, (I, (N, (G, ε))))))",
      nested("STRING"))
check("the suffixes drawn under the pairs: STRING, TRING, RING, ING, NG, G, ε",
      [("STRING")[k:] for k in range(7)] == ["STRING", "TRING", "RING", "ING", "NG", "G", ""])
check("0ε1 is the string 01 (ε contributes nothing)", cat(cat("0", ""), "1") == "01")

# ---------------------------------------------------------------- 1.2 length and concatenation
check("recursive |w| agrees with the number of symbols, |w| <= 8 over {0,1} and <= 6 over {a,b,c}",
      all(length(w) == len(w) for w in B8 + T6))
check("recursive w•z agrees with juxtaposition for all w, z with |w|, |z| <= 8 over {0,1}",
      all(cat(w, z) == w + z for w in B8 for z in B8))
check("NOW•HERE = NOWHERE, HERE•NOW = HERENOW (concatenation is not commutative)",
      cat("NOW", "HERE") == "NOWHERE" and cat("HERE", "NOW") == "HERENOW")
chain = [cat("NOW", "HERE"), cons("N", cat("OW", "HERE")), cons("N", cons("O", cat("W", "HERE"))),
         cons("N", cons("O", cons("W", cat("", "HERE")))), "NOWHERE"]
check("unfolding NOW•HERE = N·(OW•HERE) = N·(O·(W•HERE)) = N·(O·(W·(ε•HERE))) = NOWHERE",
      len(set(chain)) == 1, str(chain))
check("figure: NOW•HERE makes one new pair per symbol of NOW and then reuses HERE",
      cat("NOW", "HERE")[3:] == "HERE" and length("NOW") == 3)

# ---------------------------------------------------------------- 1.3 Lemmas 1.1–1.3 and their proofs
check("Lemma 1.1: w•ε = w for |w| <= 8 over {0,1} and |w| <= 6 over {a,b,c}",
      all(cat(w, "") == w for w in B8 + T6))
check("Lemma 1.2: |w•x| = |w| + |x| for all |w|, |x| <= 8 over {0,1}",
      all(length(cat(w, x)) == length(w) + length(x) for w in B8 for x in B8))
check("Lemma 1.3: (w•x)•y = w•(x•y) for all |w|, |x|, |y| <= 5 over {0,1}",
      all(cat(cat(w, x), y) == cat(w, cat(x, y)) for w in B5 for x in B5 for y in B5))
ok = True
for w in B6:
    for x in B6:
        if w == "":
            steps = [length(cat(w, x)), length(cat("", x)), length(x), 0 + length(x), length("") + length(x),
                     length(w) + length(x)]
        else:
            a, y = w[0], w[1:]
            steps = [length(cat(w, x)), length(cat(cons(a, y), x)), length(cons(a, cat(y, x))), 1 + length(cat(y, x)),
                     1 + length(y) + length(x), length(cons(a, y)) + length(x), length(w) + length(x)]
        ok = ok and len(set(steps)) == 1
check("model proof of Lemma 1.2: every line of both cases is an equality (|w|, |x| <= 6)", ok)
ok = all(cat("", "") == "" for _ in [0]) and all(
    cat(cons(w[0], w[1:]), "") == cons(w[0], cat(w[1:], "")) == cons(w[0], w[1:]) == w for w in B8 if w)
check("proof of Lemma 1.1: (ax)•ε = a·(x•ε) = a·x (|w| <= 8)", ok)
ok = True
for w in B5:
    for x in B4:
        for y in B4:
            if w == "":
                ok = ok and cat(cat("", x), y) == cat(x, y) == cat("", cat(x, y))
            else:
                a, z = w[0], w[1:]
                s = [cat(cat(w, x), y), cat(cons(a, cat(z, x)), y), cons(a, cat(cat(z, x), y)),
                     cons(a, cat(z, cat(x, y))), cat(cons(a, z), cat(x, y))]
                ok = ok and len(set(s)) == 1
check("proof of Lemma 1.3 (standard): every line is an equality (|w| <= 5, |x|, |y| <= 4)", ok)

# ---------------------------------------------------------------- 1.4 the three-case decomposition
ok = True
for w in B8:
    if w == "":
        continue
    single = length(w) == 1
    splits = [(w[:k], w[k:]) for k in range(1, len(w))]
    ok = ok and (single or len(splits) > 0)
    ok = ok and all(cat(u, v) == w and 1 <= length(u) < length(w) and 1 <= length(v) < length(w) for u, v in splits)
    if single:
        ok = ok and splits == []
check("every non-empty w is a single symbol or u•v with u, v non-empty and |u|, |v| < |w| (|w| <= 8)", ok)
check("a single symbol is never u•v with u, v both non-empty (so w = a is a second base case)",
      all(not (cat(u, v) == a and u and v) for a in "01" for u in B4 for v in B4))
check("a single symbol as a string: a•z = (a·ε)•z = a·(ε•z) = a·z (|z| <= 8)",
      all(cat(a, z) == cat(cons(a, ""), z) == cons(a, cat("", z)) == cons(a, z) for a in "01" for z in B8))
check("§1.4 case w = a: (a•x)•y = (a·x)•y = a·(x•y) = a•(x•y) (|x|, |y| <= 6)",
      all(cat(cat(a, x), y) == cat(cons(a, x), y) == cons(a, cat(x, y)) == cat(a, cat(x, y))
          for a in "01" for x in B6 for y in B6))
check("peeling the last symbol: every non-empty w is x•a with |x| = |w| - 1 (|w| <= 8)",
      all(cat(w[:-1], w[-1]) == w and length(w[:-1]) == length(w) - 1 for w in B8 if w))
check("figure: STRING = S·TRING = STR•ING", cons("S", "TRING") == "STRING" == cat("STR", "ING"))
ok = True
for u in B4:
    for v in B4:
        if not u or not v:
            continue
        for x in list(strings("01", 3)):
            for y in list(strings("01", 3)):
                w = cat(u, v)
                s = [cat(cat(w, x), y), cat(cat(u, cat(v, x)), y), cat(u, cat(cat(v, x), y)), cat(u, cat(v, cat(x, y))),
                     cat(cat(u, v), cat(x, y)), cat(w, cat(x, y))]
                ok = ok and len(set(s)) == 1
check("§1.4 proof of Lemma 1.3: the four uses of the hypothesis chain correctly (|u|, |v| <= 4, |x|, |y| <= 3)", ok)
check("§1.4 trap: only the third step, (v•x)•y = v•(x•y), has the fixed second and third arguments x and y",
      [t[1:] == ("x", "y") for t in [("u", "v", "x"), ("u", "v•x", "y"), ("v", "x", "y"), ("u", "v", "x•y")]]
      == [False, False, True, False])

# ---------------------------------------------------------------- 1.5 indices, substrings, prefixes, suffixes
check("recursive index w_i agrees with the i-th symbol for 1 <= i <= |w| (|w| <= 8), undefined at 0 and |w|+1",
      all(index(w, i) == w[i - 1] for w in B8 for i in range(1, len(w) + 1))
      and all(index(w, 0) is None and index(w, len(w) + 1) is None for w in B8))
check("recursive w[i..j] agrees with symbols i..j for 1 <= i <= j+1 <= |w|+1 (|w| <= 8)",
      all(sub(w, i, j) == w[i - 1:j] for w in B8 for i in range(1, len(w) + 2) for j in range(i - 1, len(w) + 1)))
ok = all(is_substring(y, w) == any(sub(w, i, j) == y for i in range(1, len(w) + 2) for j in range(i - 1, len(w) + 1))
         for w in B6 for y in B6)
check("y is a substring of w (w = xyz) iff y = w[i..j] for some i, j (|w|, |y| <= 6)", ok)
check("p is a prefix of w iff p = w[1..j] for some 0 <= j <= |w|; s is a suffix iff s = w[i..|w|] (|w|, |p| <= 6)",
      all(is_prefix(p, w) == any(sub(w, 1, j) == p for j in range(0, len(w) + 1)) and
          is_suffix(p, w) == any(sub(w, i, len(w)) == p for i in range(1, len(w) + 2)) for w in B6 for p in B6))
W = "HEADACHE"
check("HEADACHE: HE = w[1..2] is a proper prefix and HE = w[7..8] a proper suffix",
      sub(W, 1, 2) == "HE" == sub(W, 7, 8) and is_prefix("HE", W) and is_suffix("HE", W) and W != "HE")
check("HEADACHE: w[3..5] = ADA", sub(W, 3, 5) == "ADA")
M = "MEATBALL"
pos = [1, 2, 4, 6, 7]
check("METAL = symbols 1, 2, 4, 6, 7 of MEATBALL", "".join(index(M, i) for i in pos) == "METAL")
check("deleting A, B and one L (positions 3, 5, 8) from MEATBALL leaves METAL",
      "".join(c for k, c in enumerate(M, 1) if k not in (3, 5, 8)) == "METAL")
check("METAL is a subsequence but not a substring of MEATBALL", is_subseq("METAL", M) and not is_substring("METAL", M))
check("recursive subsequence definition = 'delete zero or more symbols' (all z, w with |z|, |w| <= 8 over {0,1})",
      all(is_subseq(z, w) == (z in D) for w in B8 for D in [by_deletion(w)] for z in B8))
check("... and the same over {a,b,c} for |z|, |w| <= 6",
      all(is_subseq(z, w) == (z in D) for w in T6 for D in [by_deletion(w)] for z in T6))
check("every substring is a subsequence (|w| <= 8)",
      all(is_subseq(w[i:j], w) for w in B8 for i in range(len(w) + 1) for j in range(i, len(w) + 1)))
check("0110 has 00 as a subsequence but not as a substring", is_subseq("00", "0110") and not is_substring("00", "0110"))
ok = True
for w in B8 + T6:
    n = len(w)
    prefixes = {sub(w, 1, j) for j in range(n + 1)}
    suffixes = {sub(w, i, n) for i in range(1, n + 2)}
    subs = {w[i:j] for i in range(n + 1) for j in range(i, n + 1)}
    ok = ok and len(prefixes) == n + 1 and len(suffixes) == n + 1
    ok = ok and len(subs - {""}) <= n * (n + 1) // 2 and len(by_deletion(w)) <= 2 ** n
check("length n: exactly n+1 prefixes and n+1 suffixes; at most n(n+1)/2 non-empty substrings; at most 2^n "
      "subsequences", ok)
ok = True
for n in range(0, 9):
    w = "abcdefgh"[:n]
    subs = {w[i:j] for i in range(n + 1) for j in range(i, n + 1)}
    ok = ok and len(subs - {""}) == n * (n + 1) // 2 and len(by_deletion(w)) == 2 ** n
check("with n distinct symbols both bounds are attained (n <= 8)", ok)
check("0000: its distinct substrings and its distinct subsequences are the same five strings ε, 0, 00, 000, 0000",
      {"0000"[i:j] for i in range(5) for j in range(i, 5)} == by_deletion("0000") == {"", "0", "00", "000", "0000"})

# ---------------------------------------------------------------- more recursive functions
check("recursive reversal agrees with reading backwards (|w| <= 8)", all(rev(w) == w[::-1] for w in B8))
check("#(a, x•y) = #(a, x) + #(a, y) for a in {0,1}, |x|, |y| <= 7",
      all(count(a, cat(x, y)) == count(a, x) + count(a, y) for a in "01" for x in B7 for y in B7))
check("|w| = #(0, w) + #(1, w) over {0,1} (|w| <= 8)", all(length(w) == count("0", w) + count("1", w) for w in B8))
check("|w| = #(a, w) + #(b, w) + #(c, w) over {a,b,c} (|w| <= 6)",
      all(length(w) == sum(count(a, w) for a in "abc") for w in T6))
check("|w^R| = |w| and (w^R)^R = w (|w| <= 8, both alphabets)",
      all(length(rev(w)) == length(w) and rev(rev(w)) == w for w in B8 + T6))
check("(w•x)^R = x^R • w^R for |w|, |x| <= 7", all(rev(cat(w, x)) == cat(rev(x), rev(w)) for w in B7 for x in B7))
check("#(a, w^R) = #(a, w) (|w| <= 8)", all(count(a, rev(w)) == count(a, w) for a in "01" for w in B8))
check("the tempting (w•x)^R = w^R • x^R is false: w = 0, x = 1 gives 10 vs 01",
      rev(cat("0", "1")) == "10" and cat(rev("0"), rev("1")) == "01")
ok = True
for w in B8:
    for x in B6:
        if w == "":
            s = [rev(cat(w, x)), rev(x), cat(rev(x), ""), cat(rev(x), rev("")), cat(rev(x), rev(w))]
        else:
            a, y = w[0], w[1:]
            s = [rev(cat(w, x)), rev(cons(a, cat(y, x))), cat(rev(cat(y, x)), a), cat(cat(rev(x), rev(y)), a),
                 cat(rev(x), cat(rev(y), a)), cat(rev(x), rev(cons(a, y))), cat(rev(x), rev(w))]
        ok = ok and len(set(s)) == 1
check("model proof of (w•x)^R = x^R•w^R: every line of both cases is an equality (|w| <= 8, |x| <= 6)", ok)
ok = all(rev(rev(cons(a, x))) == rev(cat(rev(x), a)) == cat(rev(a), rev(rev(x))) == cat(a, x) == cons(a, x)
         for a in "01" for x in B7) and all(rev(a) == a for a in "01")
check("(w^R)^R = w from the reversal fact: ((ax)^R)^R = (x^R•a)^R = a^R•(x^R)^R = a•x (|x| <= 7)", ok)
check("swap: recursive definition swaps adjacent pairs; swap(0110) = 1001, swap(011) = 101",
      all(swap(w) == "".join(w[k + 1] + w[k] for k in range(0, len(w) - 1, 2)) + (w[-1] if len(w) % 2 else "")
          for w in B8) and swap("0110") == "1001" and swap("011") == "101")
check("|swap(w)| = |w| and swap(swap(w)) = w (|w| <= 8, both alphabets)",
      all(length(swap(w)) == length(w) and swap(swap(w)) == w for w in B8 + T6))
check("swap(abx) applies the hypothesis to x with |x| = |w| - 2",
      all(swap(w) == cons(w[1], cons(w[0], swap(w[2:]))) and length(w[2:]) == length(w) - 2 for w in B8 if len(w) >= 2))
ok = all(cat(power(w, m), power(w, n)) == power(w, m + n) for w in B4 for m in range(6) for n in range(6))
check("w^m • w^n = w^(m+n) (|w| <= 4, m, n <= 5)", ok)
check("|w^n| = n|w|, #(a, w^n) = n·#(a, w), (w^R)^n = (w^n)^R (|w| <= 4, n <= 6)",
      all(length(power(w, n)) == n * length(w) and all(count(b, power(w, n)) == n * count(b, w) for b in "01")
          and power(rev(w), n) == rev(power(w, n)) for w in B4 for n in range(7)))
check("complement: |w^c| = |w|, (w^c)^c = w, #(1, w) = #(0, w^c), (w^R)^c = (w^c)^R (|w| <= 8)",
      all(length(comp(w)) == length(w) and comp(comp(w)) == w and count("1", w) == count("0", comp(w))
          and comp(rev(w)) == rev(comp(w)) for w in B8))
check("(x•y)^c = x^c • y^c (|x|, |y| <= 7)", all(comp(cat(x, y)) == cat(comp(x), comp(y)) for x in B7 for y in B7))
check("cancellation: x•z = y•z implies x = y, and x•y = x•z implies y = z (|x|, |y|, |z| <= 4)",
      all((cat(x, z) != cat(y, z) or x == y) and (cat(x, y) != cat(x, z) or y == z) for x in B4 for y in B4 for z in B4))
check("powers recurse on n: 01^3 = 010101 and (01)^0 = ε", power("01", 3) == "010101" and power("01", 0) == "")
check("example values: #(0, 0110) = 2, (0110)^R = 0110, (001)^R = 100, (001)^c = 110",
      count("0", "0110") == 2 and rev("0110") == "0110" and rev("001") == "100" and comp("001") == "110")

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: {FAIL}")
sys.exit(1 if FAIL else 0)
