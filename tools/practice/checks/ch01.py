#!/usr/bin/env python3
"""Checks for every claim on content/practice/01-strings.md (Practice — Chapter 1: Strings).

Every function follows the recursive definition stated in the problem literally: a string is "" (epsilon) or a
pair a·x (Python + is used only to build that pair). The predicates used as ground truth (substring = "w = xyz",
subsequence = "delete symbols", "all symbols are 1", ...) are written from the problem statements, independently
of the answers. Every identity, every line of every proof, and every example is then checked by brute force over
all short strings (lengths up to 8-12)."""
import os
import sys
from functools import lru_cache
from itertools import combinations

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from automata import strings  # noqa: E402

FAIL = []


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAIL.append(name)


# ---------------------------------------------------------------- Chapter 1 definitions
def cons(a, x):                      # a·x, the pair (a, x)
    assert len(a) == 1
    return a + x


def length(w):                       # |ε| = 0, |ax| = 1 + |x|
    return 0 if w == "" else 1 + length(w[1:])


def cat(w, z):                       # ε•z = z, (ax)•z = a·(x•z)
    return z if w == "" else cons(w[0], cat(w[1:], z))


def rev(w):                          # ε^R = ε, (ax)^R = x^R • a
    return "" if w == "" else cat(rev(w[1:]), w[0])


def bar(a):
    return {"0": "1", "1": "0"}[a]


def comp(w):                         # ε^c = ε, (ax)^c = bar(a)·x^c
    return "" if w == "" else cons(bar(w[0]), comp(w[1:]))


def count(a, w):                     # #(a, ε) = 0, #(a, bx) = [a = b] + #(a, x)
    return 0 if w == "" else (1 if w[0] == a else 0) + count(a, w[1:])


def power(w, n):                     # w^0 = ε, w^n = w • w^(n-1)
    return "" if n == 0 else cat(w, power(w, n - 1))


@lru_cache(maxsize=None)
def is_subseq(z, w):                 # recursive definition of subsequence (§1.5)
    if z == "":
        return True
    if w == "":
        return False
    return is_subseq(z, w[1:]) or (z[0] == w[0] and is_subseq(z[1:], w[1:]))


def by_deletion(w):                  # all strings obtained by deleting zero or more symbols
    n = len(w)
    return {"".join(w[k] for k in S) for r in range(n + 1) for S in combinations(range(n), r)}


def substrings(w):                   # all y with w = x y z
    return {w[i:j] for i in range(len(w) + 1) for j in range(i, len(w) + 1)}


def is_prefix(p, w):
    return w[:len(p)] == p


def is_suffix(s, w):
    return len(s) <= len(w) and w[len(w) - len(s):] == s


B = {n: list(strings("01", n)) for n in range(13)}          # all binary strings of length <= n
NONEMPTY5 = [w for w in B[5] if w]

# ---------------------------------------------------------------- 1.1 / 1.4  rcat
def rcat(x, y):                      # rcat(ε, y) = y, rcat(a·z, y) = rcat(z, a·y)
    return y if x == "" else rcat(x[1:], cons(x[0], y))


chain = [rcat("011", ""), rcat("11", cons("0", "")), rcat("11", "0"), rcat("1", cons("1", "0")), rcat("1", "10"),
         rcat("", cons("1", "10")), rcat("", "110"), "110"]
check("1.1(a) unfolding rcat(011, ε) = rcat(11, 0) = rcat(1, 10) = rcat(ε, 110) = 110", len(set(chain)) == 1, str(chain))
check("1.1(b) rcat(10, 01) = rcat(0, 101) = rcat(ε, 0101) = 0101 = (10)^R • 01",
      rcat("10", "01") == rcat("0", "101") == rcat("", "0101") == "0101" == cat(rev("10"), "01"))
check("1.1(c) the guess: 110 = (011)^R", rev("011") == "110")
check("1.4(a) rcat(x, y) = x^R • y for all |x| <= 9, |y| <= 6",
      all(rcat(x, y) == cat(rev(x), y) for x in B[9] for y in B[6]))
check("1.4(a) ... and over {a,b,c} for |x|, |y| <= 5",
      all(rcat(x, y) == cat(rev(x), y) for x in strings("abc", 5) for y in strings("abc", 4)))
check("1.4(a) base case: rcat(ε, y) = y = ε•y = ε^R•y (|y| <= 8)",
      all(rcat("", y) == y == cat("", y) == cat(rev(""), y) for y in B[8]))
ok = True
for x in B[8]:
    if not x:
        continue
    a, z = x[0], x[1:]
    for y in B[5]:
        lines = [rcat(cons(a, z), y), rcat(z, cons(a, y)), cat(rev(z), cons(a, y)), cat(rev(z), cat(a, y)),
                 cat(cat(rev(z), a), y), cat(rev(cons(a, z)), y)]
        ok = ok and len(set(lines)) == 1 and length(z) < length(x)
check("1.4(a) inductive case: every line rcat(az,y) = rcat(z,ay) = z^R•(a·y) = z^R•(a•y) = (z^R•a)•y = (az)^R•y", ok)
check("1.4(a) the recursive call changes the second argument (a·y ≠ y), so a fixed-y hypothesis does not apply",
      all(cons(a, y) != y for a in "01" for y in B[6]))
check("1.4(b) rcat(x, ε) = x^R and |rcat(x, y)| = |x| + |y| (|x| <= 9, |y| <= 6)",
      all(rcat(x, "") == rev(x) for x in B[9]) and
      all(length(rcat(x, y)) == length(x) + length(y) for x in B[9] for y in B[6]))
check("1.4 check: rcat(011, ε) = 110 = (011)^R and rcat(10, 01) = 0101 = 01•01",
      rcat("011", "") == "110" == rev("011") and rcat("10", "01") == "0101" == cat("01", "01"))
check("1.4 watch out: the special case is not closed under the recursion (rcat(az, ε) calls rcat(z, a), a ≠ ε)",
      all(rcat(cons(a, z), "") == rcat(z, a) for a in "01" for z in B[6]))

# ---------------------------------------------------------------- 1.2 true or false
check("1.2(a) No: 01 is a substring of 0•1 but of neither 0 nor 1",
      "01" in substrings(cat("0", "1")) and "01" not in substrings("0") and "01" not in substrings("1"))
ok = True
for y in B[5]:
    for z in B[5]:
        joined = {cat(u, v) for u in by_deletion(y) for v in by_deletion(z)}
        ok = ok and joined == by_deletion(cat(y, z))
check("1.2(b) Yes: the subsequences of y•z are exactly the u•v with u a subsequence of y and v of z (|y|, |z| <= 5)", ok)
check("1.2(b) the recursive definition of subsequence agrees with deletion (|z|, |w| <= 8)",
      all(is_subseq(z, w) == (z in D) for w in B[8] for D in [by_deletion(w)] for z in B[8]))
check("1.2(c) Yes: p prefix of w implies p^R suffix of w^R (|w| <= 10, every prefix)",
      all(is_suffix(rev(w[:j]), rev(w)) for w in B[10] for j in range(len(w) + 1)))
check("1.2(c) the reason: w = p•x gives w^R = x^R•p^R (|p|, |x| <= 6)",
      all(rev(cat(p, x)) == cat(rev(x), rev(p)) for p in B[6] for x in B[6]))
check("1.2(d) No: 0•00 = 000 = 00•0 but 0 ≠ 00; ε commutes with every y",
      cat("0", "00") == "000" == cat("00", "0") and "0" != "00" and all(cat("", y) == cat(y, "") for y in B[6]))
check("1.2(e) Yes: every string of length n has >= n+1 distinct subsequences (|w| <= 12)",
      all(len(by_deletion(w)) >= len(w) + 1 for w in B[12]))
check("1.2(e) the n+1 prefixes are distinct subsequences; 0^n has exactly n+1 subsequences (n <= 12)",
      all(len({w[:j] for j in range(len(w) + 1)}) == len(w) + 1 and all(is_subseq(w[:j], w) for j in range(len(w) + 1))
          for w in B[10]) and all(len(by_deletion("0" * n)) == n + 1 for n in range(13)))
S0101 = substrings("0101")
check("1.2(f) No: 0101 has exactly 8 distinct substrings: ε, 0, 1, 01, 10, 010, 101, 0101",
      S0101 == {"", "0", "1", "01", "10", "010", "101", "0101"} and len(S0101) == 8, str(sorted(S0101, key=len)))
check("1.2(f) 11 = 4·5/2 + 1 is the bound; 01 starts at positions 1 and 3 of 0101",
      4 * 5 // 2 + 1 == 11 and [i + 1 for i in range(3) if "0101"[i:i + 2] == "01"] == [1, 3])

# ---------------------------------------------------------------- 1.3 find the error
check("1.3 the claim (w^R)^c = (w^c)^R holds (|w| <= 12)", all(comp(rev(w)) == rev(comp(w)) for w in B[12]))
check("1.3 student's base case: (ε^R)^c = ε^c = ε = ε^R = (ε^c)^R",
      comp(rev("")) == comp("") == "" == rev("") == rev(comp("")))
ok = True
for u in NONEMPTY5:
    for v in NONEMPTY5:
        lines = [comp(rev(cat(u, v))), comp(cat(rev(v), rev(u))), cat(comp(rev(v)), comp(rev(u))),
                 cat(rev(comp(v)), rev(comp(u))), rev(cat(comp(u), comp(v))), rev(comp(cat(u, v)))]
        ok = ok and len(set(lines)) == 1 and length(u) < length(cat(u, v)) and length(v) < length(cat(u, v))
check("1.3 student's u•v case: all five equalities hold and |u|, |v| < |w| (u, v non-empty, length <= 5)", ok)
check("1.3 the slip: a string of length 1 is neither ε nor u•v with u, v non-empty",
      all(not (u and v and cat(u, v) == a) for a in "01" for u in B[3] for v in B[3]))
check("1.3 every string of length >= 2 is u•v with u, v non-empty (|w| <= 10)",
      all(any(cat(w[:k], w[k:]) == w for k in range(1, len(w))) for w in B[10] if len(w) >= 2))
check("1.3 repair: a^R = (a·ε)^R = ε^R•a = ε•a = a, and (a^R)^c = a^c = (a^c)^R",
      all(rev(a) == rev(cons(a, "")) == cat(rev(""), a) == cat("", a) == a and comp(rev(a)) == comp(a) == rev(comp(a))
          for a in "01"))
step_ok = all(count("0", cat(u, v)) == count("1", cat(u, v))
              for u in B[5] for v in B[5] if u and v and count("0", u) == count("1", u) and count("0", v) == count("1", v))
check("1.3 why it matters: the two cases 'prove' #(0,w) = #(1,w) (ε satisfies it, the u•v step is valid) "
      "but it fails at w = 0", count("0", "") == count("1", "") and step_ok and count("0", "0") == 1 != count("1", "0"))
check("1.3 the u•v step uses #(a, uv) = #(a,u) + #(a,v) (|u|, |v| <= 6)",
      all(count(a, cat(u, v)) == count(a, u) + count(a, v) for a in "01" for u in B[6] for v in B[6]))

# ---------------------------------------------------------------- 1.5 substrings vs subsequences
ok = True
for a in range(1, 8):
    for b in range(1, 8):
        w = "0" * a + "1" * b
        target = {"0" * p + "1" * q for p in range(a + 1) for q in range(b + 1)}
        ok = ok and substrings(w) == by_deletion(w) == target and len(target) == (a + 1) * (b + 1)
        ok = ok and all(w[a - p:a + q] == "0" * p + "1" * q for p in range(a + 1) for q in range(b + 1))
check("1.5(a) 0^a1^b: substrings = subsequences = {0^p1^q}, (a+1)(b+1) of each; 0^p1^q = w[a-p+1..a+q] (a, b <= 7)", ok)


def two_block_form(w):               # w = 0^i 1^j or w = 1^i 0^j  (from the statement)
    return any(w == "0" * i + "1" * (len(w) - i) or w == "1" * i + "0" * (len(w) - i) for i in range(len(w) + 1))


check("1.5(b) every subsequence of w is a substring iff w = 0^i1^j or 1^i0^j (all w with |w| <= 11)",
      all((by_deletion(w) <= substrings(w)) == two_block_form(w) for w in B[11]))
ok = True
for w in B[11]:
    has10 = any(w[i] == "1" and "0" in w[i + 1:] for i in range(len(w)))
    has01 = any(w[i] == "0" and "1" in w[i + 1:] for i in range(len(w)))
    ok = ok and (not has10) == any(w == "0" * i + "1" * (len(w) - i) for i in range(len(w) + 1))
    ok = ok and (not has01) == any(w == "1" * i + "0" * (len(w) - i) for i in range(len(w) + 1))
check("1.5(b) w is not 0^i1^j iff some 1 comes before some 0; not 1^i0^j iff some 0 comes before some 1 (|w| <= 11)", ok)


def blocks(w, c):                    # lengths of the maximal blocks of consecutive c's
    out, run = [], 0
    for s in w + "#":
        if s == c:
            run += 1
        elif run:
            out.append(run)
            run = 0
    return out


ok = True
for w in B[11]:
    if two_block_form(w):
        continue
    c = w[0]
    bl = blocks(w, c)
    m = max(bl)
    ok = ok and len(bl) >= 2 and count(c, w) >= m + 1 and (c * (m + 1) in by_deletion(w)) \
        and (c * (m + 1) not in substrings(w))
check("1.5(b) 'only if' construction: c = first symbol has >= 2 blocks; with m its longest block, c^(m+1) is a "
      "subsequence but not a substring (every w of neither form, |w| <= 11)", ok)
check("1.5 check: 00 is a subsequence but not a substring of 0110; 0011 has 9 substrings and 9 subsequences",
      "00" in by_deletion("0110") and "00" not in substrings("0110") and not two_block_form("0110")
      and len(substrings("0011")) == 9 == len(by_deletion("0011")))


# ---------------------------------------------------------------- 1.6 rot
def rot(w):                          # rot(w) = w if |w| <= 1; rot(a·b·x) = b·rot(a·x)
    return w if length(w) <= 1 else cons(w[1], rot(cons(w[0], w[2:])))


chain = [rot("STAR"), cons("T", rot("SAR")), cons("T", cons("A", rot("SR"))), cons("T", cons("A", cons("R", rot("S")))),
         "TARS"]
check("1.6(a) rot(STAR) = T·rot(SAR) = T·A·rot(SR) = T·A·R·rot(S) = TARS", len(set(chain)) == 1, str(chain))
check("1.6(b) |rot(w)| = |w| (|w| <= 12 over {0,1}, <= 7 over {a,b,c})",
      all(length(rot(w)) == length(w) for w in B[12] + list(strings("abc", 7))))
ok = True
for w in B[11]:
    if len(w) < 2:
        ok = ok and rot(w) == w
        continue
    a, b, x = w[0], w[1], w[2:]
    ok = ok and length(cons(a, x)) == length(x) + 1 < length(x) + 2 == length(w)
    ok = ok and length(rot(w)) == length(cons(b, rot(cons(a, x)))) == 1 + length(rot(cons(a, x))) \
        == 1 + length(cons(a, x)) == 2 + length(x) == length(w)
check("1.6(b) both cases: rot(w) = w for |w| <= 1; for w = abx, |ax| < |w| and every line of the chain holds", ok)
check("1.6(b) a·x need not be a suffix of a·b·x: SAR is not a suffix of STAR",
      not is_suffix("SAR", "STAR") and cons("S", "AR") == "SAR")
check("1.6(c) rot(a·x) = x•a (all a, |x| <= 11 over {0,1}; |x| <= 6 over {a,b,c})",
      all(rot(cons(a, x)) == cat(x, a) for a in "01" for x in B[11]) and
      all(rot(cons(a, x)) == cat(x, a) for a in "abc" for x in strings("abc", 6)))
check("1.6(c) base: rot(a·ε) = a = ε•a", all(rot(cons(a, "")) == a == cat("", a) for a in "01"))
check("1.6(c) inductive case: rot(a·b·y) = b·rot(a·y) = b·(y•a) = (b·y)•a (|y| <= 9)",
      all(rot(cons(a, cons(b, y))) == cons(b, rot(cons(a, y))) == cons(b, cat(y, a)) == cat(cons(b, y), a)
          for a in "01" for b in "01" for y in B[9]))
check("1.6 check: rot(STAR) = TAR•S, and |x•a| = |x| + 1", rot("STAR") == cat("TAR", "S")
      and all(length(cat(x, a)) == length(x) + 1 for a in "01" for x in B[8]))


# ---------------------------------------------------------------- 1.7 zig
def zig(w):                          # zig(ε) = ε, zig(a·x) = a·(zig(x))^c
    return "" if w == "" else cons(w[0], comp(zig(w[1:])))


check("1.7 examples: zig(0000) = 0101, zig(0110) = 0011", zig("0000") == "0101" and zig("0110") == "0011")
check("1.7 idea: zig complements exactly the symbols in even positions (|w| <= 12)",
      all(zig(w) == "".join(c if i % 2 == 0 else bar(c) for i, c in enumerate(w)) for w in B[12]))
check("1.7(a) zig(w^c) = zig(w)^c (|w| <= 12)", all(zig(comp(w)) == comp(zig(w)) for w in B[12]))
check("1.7(a) base: zig(ε^c) = zig(ε) = ε = ε^c = zig(ε)^c", zig(comp("")) == zig("") == "" == comp("") == comp(zig("")))
ok = True
for w in B[11]:
    if not w:
        continue
    a, x = w[0], w[1:]
    lines = [zig(comp(w)), zig(cons(bar(a), comp(x))), cons(bar(a), comp(zig(comp(x)))), cons(bar(a), comp(comp(zig(x)))),
             comp(cons(a, comp(zig(x)))), comp(zig(cons(a, x)))]
    ok = ok and comp(w) == cons(bar(a), comp(x)) and len(set(lines)) == 1
check("1.7(a) inductive case: zig(w^c) = zig(ā·x^c) = ā·zig(x^c)^c = ā·(zig(x)^c)^c = (a·zig(x)^c)^c = zig(ax)^c", ok)
check("1.7(b) zig(zig(w)) = w (|w| <= 12)", all(zig(zig(w)) == w for w in B[12]))
ok = True
for w in B[11]:
    if not w:
        continue
    a, x = w[0], w[1:]
    lines = [zig(zig(cons(a, x))), zig(cons(a, comp(zig(x)))), cons(a, comp(zig(comp(zig(x))))),
             cons(a, comp(comp(zig(zig(x))))), cons(a, zig(zig(x))), cons(a, x)]
    ok = ok and len(set(lines)) == 1
check("1.7(b) inductive case: zig(zig(ax)) = zig(a·zig(x)^c) = a·zig(zig(x)^c)^c = a·((zig(zig(x)))^c)^c "
      "= a·zig(zig(x)) = a·x", ok)
check("1.7 (y^c)^c = y (|y| <= 12)", all(comp(comp(y)) == y for y in B[12]))
check("1.7 check: zig(0110) = 0011, zig(0011) = 0110; zig(10) = 11 = (00)^c = zig(01)^c",
      zig("0110") == "0011" and zig("0011") == "0110" and zig("10") == "11" == comp("00") == comp(zig("01")))


# ---------------------------------------------------------------- 1.8 inc and val (least significant bit first)
def val(w):                          # val(ε) = 0, val(a·x) = a + 2 val(x)
    return 0 if w == "" else int(w[0]) + 2 * val(w[1:])


def inc(w):                          # inc(ε) = 1, inc(0x) = 1·x, inc(1x) = 0·inc(x)
    if w == "":
        return "1"
    if w[0] == "0":
        return cons("1", w[1:])
    return cons("0", inc(w[1:]))


def all_ones(w):                     # w = 1^n for some n >= 0
    return set(w) <= {"1"}


check("1.8 val is the binary value read least significant bit first (|w| <= 12)",
      all(val(w) == (int(w[::-1], 2) if w else 0) for w in B[12]))
check("1.8 example: val(011) = 0 + 2(1 + 2(1 + 2·0)) = 6", val("011") == 0 + 2 * (1 + 2 * (1 + 2 * 0)) == 6)
check("1.8 example: inc(1101) = 0011, i.e. 11 + 1 = 12", inc("1101") == "0011" and val("1101") == 11 and val("0011") == 12)
check("1.8(a) val(inc(w)) = val(w) + 1 (|w| <= 12)", all(val(inc(w)) == val(w) + 1 for w in B[12]))
check("1.8(a) case ε: val(inc(ε)) = val(1·ε) = 1 + 2 val(ε) = 1 = val(ε) + 1",
      val(inc("")) == val(cons("1", "")) == 1 + 2 * val("") == 1 == val("") + 1)
check("1.8(a) case 0x: val(1·x) = 1 + 2 val(x) = (0 + 2 val(x)) + 1 = val(0x) + 1 (|x| <= 11)",
      all(val(inc(cons("0", x))) == val(cons("1", x)) == 1 + 2 * val(x) == (0 + 2 * val(x)) + 1 == val(cons("0", x)) + 1
          for x in B[11]))
check("1.8(a) case 1x: val(0·inc(x)) = 2 val(inc(x)) = 2(val(x) + 1) = (1 + 2 val(x)) + 1 = val(1x) + 1 (|x| <= 11)",
      all(val(inc(cons("1", x))) == val(cons("0", inc(x))) == 0 + 2 * val(inc(x)) == 2 * (val(x) + 1)
          == (1 + 2 * val(x)) + 1 == val(cons("1", x)) + 1 for x in B[11]))
check("1.8(b) |inc(w)| = |w| + 1 if w = 1^n, |w| otherwise (|w| <= 12)",
      all(length(inc(w)) == length(w) + (1 if all_ones(w) else 0) for w in B[12]))
check("1.8(b) small fact: 1·x is of the form 1^n iff x is; 1^n = 1·1^(n-1) for n >= 1 (|x| <= 11, n <= 12)",
      all(all_ones(cons("1", x)) == all_ones(x) for x in B[11]) and
      all(power("1", n) == cons("1", power("1", n - 1)) for n in range(1, 13)))
check("1.8(b) cases: ε = 1^0 and |inc(ε)| = 1; 0x is never 1^n and |inc(0x)| = |0x|; |inc(1x)| = 1 + |inc(x)|",
      all_ones("") and length(inc("")) == 1 and all(not all_ones(cons("0", x)) and length(inc(cons("0", x))) == length(cons("0", x))
                                                    and length(inc(cons("1", x))) == 1 + length(inc(x)) for x in B[11]))
check("1.8 check: inc(111) = 0001 (7 + 1 = 8, length 4); inc(011) = 111 (6 + 1 = 7, length 3)",
      inc("111") == "0001" and val("111") == 7 and val("0001") == 8 and inc("011") == "111" and val("111") == 7)

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: {FAIL}")
sys.exit(1 if FAIL else 0)
