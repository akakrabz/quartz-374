#!/usr/bin/env python3
"""Practice-bank tool: validate the practice pages, generate the hub and list
pages, and (re)insert the practice links on chapter, unit and concept pages.

usage:
    python3 tools/practice/build_practice.py [--src CONTENT_DIR] [--write]

    without --write: parse and validate only (prints one line per page).
    with    --write: also regenerate practice/index.md, easy.md, medium.md,
                     hard.md, topics.md and update the links elsewhere.
                     Safe to run repeatedly (every insertion is idempotent).

CONTENT_DIR defaults to ../../content relative to this script.

Problem block (tools/practice/SPEC.md §4):
    ### C.N Short title
    <blank>
    > [!easy] Easy · tag · tag          (or medium / hard)
    > statement ...
    > *Source: ....*
    <blank>
    > [!hint]- Hint                      (required for medium/hard)
    ...
    > [!solution]- Solution
    > ...
    > **Answer.** ...
"""
import collections
import os
import re
import sys
import unicodedata

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, "..", "..", "content"))
if "--src" in sys.argv:
    SRC = sys.argv[sys.argv.index("--src") + 1]
PDIR = os.path.join(SRC, "practice")

CHAPTERS = {
    1: ("1-models-of-computation/01-strings", "Strings"),
    2: ("1-models-of-computation/02-regular-languages", "Regular languages"),
    3: ("1-models-of-computation/03-finite-state-machines", "Finite-state machines"),
    4: ("1-models-of-computation/04-nondeterministic-automata", "Nondeterministic automata"),
    5: ("1-models-of-computation/05-context-free-languages", "Context-free languages"),
    6: ("1-models-of-computation/06-turing-machines", "Turing machines"),
    7: ("1-models-of-computation/07-undecidability", "Undecidability"),
}
UNIT_INDEXES = ["1-models-of-computation/index.md"]
LEVELS = ["easy", "medium", "hard"]
EXPECT = {1: (3, 3, 2), 2: (3, 3, 2), 3: (4, 3, 3), 4: (4, 3, 3), 5: (4, 3, 3), 6: (3, 2, 1), 7: (3, 3, 2)}

# ------------------------------------------------------------------ topics
TYPES = [("tf", "Quick checks: true or false and multiple choice"), ("fte", "Find the error")]
TOPICS = [
    ("induction", "Induction on strings and recursive functions"),
    ("languages", "Languages and their operations"),
    ("regex", "Regular expressions"),
    ("structural", "Structural induction on regular expressions"),
    ("dfa", "Designing and proving DFAs"),
    ("product", "Product construction and closure properties"),
    ("fooling", "Fooling sets and non-regularity"),
    ("minimization", "Myhill–Nerode and minimal DFAs"),
    ("nfa", "NFAs and epsilon-transitions"),
    ("kleene", "Conversions: subset construction, Thompson, state elimination"),
    ("transform", "Regular language transformations"),
    ("cfg", "Designing context-free grammars"),
    ("cfgproof", "Proving what a grammar generates"),
    ("parse", "Parse trees, ambiguity and Chomsky normal form"),
    ("tm", "Turing machines: design, variants, simulation"),
    ("decidable", "Acceptable and decidable languages"),
    ("diagonal", "Diagonalization"),
    ("reduction", "Undecidability by reduction"),
    ("rice", "Rice's theorem and machine behavior"),
]
TOPIC_TITLE = dict(TYPES + TOPICS)

# tag -> list of topic keys. Every tag used on a practice page must appear here (or in IGNORE).
RULES = {
    "true or false": ["tf"], "multiple choice": ["tf"], "find the error": ["fte"],
    "string induction": ["induction"], "recursive functions": ["induction"],
    "substrings and subsequences": ["induction"],
    "languages": ["languages"], "Kleene star": ["languages"], "Arden's rule": ["languages", "regex"],
    "regular expressions": ["regex"], "regex induction": ["structural"],
    "DFA design": ["dfa"], "DFA proof": ["dfa"],
    "product construction": ["product"], "closure properties": ["product"],
    "fooling sets": ["fooling"], "non-regularity": ["fooling"],
    "Myhill–Nerode": ["minimization"], "minimization": ["minimization"],
    "NFA design": ["nfa"], "epsilon-transitions": ["nfa"],
    "subset construction": ["kleene"], "Thompson's algorithm": ["kleene"], "state elimination": ["kleene"],
    "language transformations": ["transform"],
    "grammar design": ["cfg"], "grammar proof": ["cfgproof"], "parse trees": ["parse"], "ambiguity": ["parse"],
    "Chomsky normal form": ["parse"], "recursive automata": ["cfg"], "context-free closure": ["cfg"],
    "Turing machine design": ["tm"], "TM variants": ["tm"], "TM simulation": ["tm"],
    "acceptable vs decidable": ["decidable"], "closure of decidable languages": ["decidable"],
    "diagonalization": ["diagonal"], "reductions": ["reduction"],
    "Rice's theorem": ["rice"], "TM behavior": ["rice"],
}
IGNORE = set()

# concept page -> topics whose problems it should point to
CONCEPT_TOPICS = {
    "induction-on-strings": ["induction"], "strings": ["induction"], "languages": ["languages"],
    "regular-expressions": ["regex"], "regular-languages": ["structural", "regex"],
    "dfa": ["dfa"], "product-construction": ["product"], "closure-properties": ["product"],
    "fooling-sets": ["fooling"], "myhill-nerode-theorem": ["minimization"], "dfa-minimization": ["minimization"],
    "nfa": ["nfa"], "subset-construction": ["kleene"], "thompsons-algorithm": ["kleene"],
    "state-elimination": ["kleene"], "kleenes-theorem": ["kleene"],
    "language-transformations": ["transform"], "context-free-grammars": ["cfg", "cfgproof"],
    "parse-trees-and-ambiguity": ["parse"], "chomsky-normal-form": ["parse"],
    "turing-machines": ["tm"], "acceptable-and-decidable": ["decidable"], "diagonalization": ["diagonal"],
    "halting-problem": ["reduction"], "undecidability-reductions": ["reduction"], "rices-theorem": ["rice"],
}
# chapter to draw a concept page's example problems from (default: where its first topic has most problems)
CONCEPT_HOME = {}


def gh_slug(s):
    s = s.lower()
    out = []
    for ch in s:
        if ch == " ":
            out.append("-")
        elif ch in "-_":
            out.append(ch)
        elif unicodedata.category(ch)[0] in ("L", "N") or unicodedata.category(ch) in ("Mn", "Mc"):
            out.append(ch)
    return "".join(out)


HEAD_RE = re.compile(r"^### (\d+)\.(\d+) (.+?)\s*$")
DIFF_RE = re.compile(r"^> \[!(easy|medium|hard)\] (Easy|Medium|Hard)((?: · [^·]+?)+)\s*$")
CALLOUT_RE = re.compile(r"^> \[!([a-z]+)\]([-+]?) ?(.*)$")


def parse_page(path):
    text = open(path, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    fm = yaml.safe_load(m.group(1)) if m else {}
    lines = text.split("\n")
    errs, probs = [], []
    section = None
    i = 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("## "):
            section = ln[3:].strip().lower()
        h = HEAD_RE.match(ln)
        if h:
            C, N, title = int(h.group(1)), int(h.group(2)), h.group(3)
            p = {"C": C, "N": N, "id": f"{C}.{N}", "title": title, "line": i + 1, "section": section,
                 "anchor": gh_slug(f"{C}.{N} {title}"), "level": None, "tags": [], "source": "", "answer": ""}
            j = i + 1
            block = []
            while j < len(lines) and not re.match(r"^#{1,3} ", lines[j]):
                block.append(lines[j])
                j += 1
            nb = [b for b in block if b.strip()]
            if not nb:
                errs.append(f"{C}.{N}: empty block")
                probs.append(p)
                i = j
                continue
            d = DIFF_RE.match(nb[0])
            if not d:
                errs.append(f"{C}.{N}: first line is not a difficulty callout: {nb[0][:80]!r}")
            else:
                p["level"] = d.group(1)
                if d.group(2).lower() != d.group(1):
                    errs.append(f"{C}.{N}: callout type {d.group(1)} but title word {d.group(2)}")
                p["tags"] = [t.strip() for t in d.group(3).split(" · ") if t.strip()]
                if not 1 <= len(p["tags"]) <= 3:
                    errs.append(f"{C}.{N}: {len(p['tags'])} tags")
            seq = []
            for k, b in enumerate(block):
                c = CALLOUT_RE.match(b)
                if c:
                    seq.append((c.group(1), c.group(2), k))
            kinds = [s[0] for s in seq]
            if kinds.count("solution") != 1:
                errs.append(f"{C}.{N}: {kinds.count('solution')} solution callouts")
            if p["level"] in ("medium", "hard") and "hint" not in kinds:
                errs.append(f"{C}.{N}: no hint ({p['level']})")
            for kind, fold, _ in seq:
                if kind in ("hint", "solution") and fold != "-":
                    errs.append(f"{C}.{N}: {kind} callout not folded")
            exp_order = [p["level"]] + (["hint"] if "hint" in kinds else []) + ["solution"]
            if kinds != exp_order:
                errs.append(f"{C}.{N}: callouts {kinds}, expected {exp_order}")
            in_callout = False
            for b in block:
                if CALLOUT_RE.match(b):
                    in_callout = True
                    continue
                if in_callout and b.startswith(">"):
                    continue
                if in_callout and b.strip() == "":
                    in_callout = False
                    continue
                if in_callout:
                    errs.append(f"{C}.{N}: unprefixed line inside callout: {b[:60]!r}")
                    in_callout = False
                elif b.strip():
                    errs.append(f"{C}.{N}: text outside callouts: {b[:60]!r}")
            if seq:
                k0 = seq[0][2]
                k1 = seq[1][2] if len(seq) > 1 else len(block)
                stmt = [b for b in block[k0:k1] if b.startswith(">")]
                src = [b for b in stmt if b.startswith("> *Source:")]
                if not src:
                    errs.append(f"{C}.{N}: no *Source:* line")
                else:
                    p["source"] = src[-1][len("> *Source:"):].strip().rstrip("*").strip()
                    if stmt[-1] != src[-1]:
                        errs.append(f"{C}.{N}: *Source:* is not the last statement line")
            sol = [s for s in seq if s[0] == "solution"]
            if sol:
                ans = [b for b in block[sol[0][2]:] if b.startswith("> **Answer.**")]
                if not ans:
                    errs.append(f"{C}.{N}: no **Answer.** line in solution")
                p["answer"] = ans[-1] if ans else ""
            probs.append(p)
            i = j
            continue
        i += 1
    return fm, probs, errs


def topics_of(p):
    keys, unknown = [], []
    for t in p["tags"]:
        if t in IGNORE and t not in RULES:
            continue
        rule = RULES.get(t)
        if rule is None:
            unknown.append(t)
            continue
        for k in rule:
            if k not in keys:
                keys.append(k)
    return keys, unknown


def load_all():
    pages = []
    if not os.path.isdir(PDIR):
        return pages
    for fn in sorted(os.listdir(PDIR)):
        m = re.match(r"^(\d\d)-.*\.md$", fn)
        if not m:
            continue
        C = int(m.group(1))
        fm, probs, errs = parse_page(os.path.join(PDIR, fn))
        slug = "practice/" + fn[:-3]
        if fm.get("chapter") != C:
            errs.append(f"frontmatter chapter={fm.get('chapter')} for file {fn}")
        if C not in CHAPTERS:
            errs.append(f"chapter {C} missing from CHAPTERS table")
        nums = [(p["C"], p["N"]) for p in probs]
        if nums != [(C, n) for n in range(1, len(probs) + 1)]:
            errs.append(f"numbering {nums}")
        counts = tuple(sum(1 for p in probs if p["level"] == lv) for lv in LEVELS)
        if C in EXPECT and counts != EXPECT[C]:
            errs.append(f"counts {counts}, expected {EXPECT[C]}")
        order = [LEVELS.index(p["level"]) if p["level"] in LEVELS else 9 for p in probs]
        if order != sorted(order):
            errs.append("difficulties not in easy→medium→hard order")
        for p in probs:
            if p["section"] != p["level"]:
                errs.append(f"{p['id']}: under section '{p['section']}' but tagged {p['level']}")
            p["slug"] = slug
            p["topics"], unknown = topics_of(p)
            for t in unknown:
                errs.append(f"{p['id']}: tag {t!r} has no topic rule (add it to RULES or IGNORE)")
            if not [k for k in p["topics"] if k not in ("tf", "fte")]:
                errs.append(f"{p['id']}: no subject topic (tags {p['tags']})")
        desc = fm.get("description", "")
        mm = re.search(r"(\d+) practice problems \((\d+) easy, (\d+) medium, (\d+) hard\)", desc)
        if not mm:
            errs.append("description lacks 'N practice problems (a easy, b medium, c hard)'")
        elif (int(mm.group(1)),) + tuple(int(x) for x in mm.group(2, 3, 4)) != (len(probs),) + counts:
            errs.append(f"description counts {mm.group(0)!r} disagree with {len(probs)} {counts}")
        anchors = [p["anchor"] for p in probs]
        if len(set(anchors)) != len(anchors):
            errs.append("duplicate anchors")
        pages.append({"C": C, "file": fn, "slug": slug, "fm": fm, "probs": probs, "errs": errs, "counts": counts})
    return pages


# ------------------------------------------------------------------ generation helpers
def chip(level):
    return f'<span class="diff {level}">{level}</span>'


def plink(p, text=None, table=False):
    bar = "\\|" if table else "|"
    return f"[[{p['slug']}#{p['anchor']}{bar}{text or (p['id'] + ' ' + p['title'])}]]"


def ch_heading(C):
    return f"Chapter {C} · {CHAPTERS[C][1]}"


def write(path, text):
    full = os.path.join(SRC, path)
    old = open(full, encoding="utf-8").read() if os.path.exists(full) else None
    if old != text:
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(text)
        print("  wrote", path)


NAV = "*[[practice/index|Practice hub]] · by difficulty: {e} · {m} · {h} · [[practice/topics|by topic]]*"


def nav(current=None):
    def one(lv):
        return chip(lv) if lv == current else f"[[practice/{lv}|{lv}]]"
    return NAV.format(e=one("easy"), m=one("medium"), h=one("hard"))


RUBRIC = {
    "easy": "one definition or one idea: a true-or-false item with a one-sentence reason, a short regular expression or DFA, a single induction step, or spotting one error",
    "medium": "a standard exam part: a DFA or grammar with state or nonterminal meanings, a full fooling-set proof, a short induction proof, or one construction carried out by hand",
    "hard": "a full exam problem: a language transformation with a formal construction, a two-part regular-and-context-free problem, a complete proof about a recursive function, or an undecidability proof",
}
TIME = {"easy": "2–5 min", "medium": "10–15 min", "hard": "20–30 min"}


def gen_level_page(pages, level):
    allp = [p for pg in pages for p in pg["probs"] if p["level"] == level]
    n = len(allp)
    Cs = [pg["C"] for pg in pages]
    out = ["---",
           f'title: "{level.capitalize()} problems"',
           f'description: "All {n} {level} practice problems for Chapters {Cs[0]}–{Cs[-1]}, by chapter. {level.capitalize()} = {RUBRIC[level].split(":")[0]}; about {TIME[level]} each."',
           "tags: [practice]", "---", "", nav(level), ""]
    intro = {
        "easy": "Start here. These build the reflexes the longer problems rely on — a good first pass right after reading a chapter, or a warm-up the night before an exam.",
        "medium": "Each of these is the size of one part of an exam problem. The hint names the key idea; try to find it yourself first.",
        "hard": "Exam-length problems: write the boilerplate first, then fill it in, and check your answer on a few small strings before you read the solution. Exam problems get about 20 minutes each.",
    }[level]
    out += [f"**{level.capitalize()}** ({TIME[level]}): {RUBRIC[level]}. {intro}", ""]
    for pg in pages:
        ps = [p for p in pg["probs"] if p["level"] == level]
        if not ps:
            continue
        out += [f"## {ch_heading(pg['C'])}", ""]
        for p in ps:
            out.append(f"- {plink(p)} — {' · '.join(p['tags'])}")
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def gen_topics_page(pages):
    allp = [p for pg in pages for p in pg["probs"]]
    by = collections.OrderedDict((k, []) for k, _ in TYPES + TOPICS)
    for p in allp:
        for k in p["topics"]:
            by[k].append(p)
    out = ["---", 'title: "Problems by topic"',
           f'description: "The {len(allp)} practice problems grouped by topic across chapters, plus the quick true-or-false and multiple-choice checks and the find-the-error items."',
           "tags: [practice]", "---", "", nav(), "",
           "Topics cut across chapters: induction proofs run from strings (Chapter 1) to grammars (Chapter 5), and the same closure arguments return for decidable languages in Chapter 7. Each problem is listed under every topic its tags belong to, in chapter order, with its level.", ""]
    for k, title in TYPES + TOPICS:
        ps = by[k]
        if not ps:
            continue
        out += [f"## {title}", ""]
        if k == "tf":
            out += ["Two-minute checks in the style of the exams' true-or-false problem: decide, then give the one-sentence reason (that reason is where the points are). Every option is explained in the solution.", ""]
        elif k == "fte":
            out += ["A short student answer with one classic slip — a missing ε, a fooling set that is not infinite, a hypothesis applied to a string that is not shorter, a reduction in the wrong direction. Spotting it is the skill that saves points.", ""]
        for p in ps:
            out.append(f"- {plink(p)} {chip(p['level'])}")
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def gen_hub(pages):
    allp = [p for pg in pages for p in pg["probs"]]
    tot = len(allp)
    c = {lv: sum(1 for p in allp if p["level"] == lv) for lv in LEVELS}
    Cs = [pg["C"] for pg in pages]
    out = ["---", 'title: "Practice problems"',
           f'description: "{tot} practice problems for Chapters {Cs[0]}–{Cs[-1]} of Models of Computation — {c["easy"]} easy, {c["medium"]} medium, {c["hard"]} hard — each with a folded hint and a worked solution, and every automaton, expression and grammar machine-checked. Browse by chapter, by difficulty or by topic."',
           "tags: [practice]", "---", "",
           f"Knowing the definitions and being able to *produce* a DFA, a fooling set or a reduction under time pressure are different skills, and only the second one is tested. This bank has **{tot} problems for Chapters {Cs[0]}–{Cs[-1]}**: quick true-or-false checks, standard exam parts, and full exam-length problems in the formats of the course's exams. None of them is copied from a course exam or homework.",
           "",
           "> [!recipe] How to use the bank",
           "> 1. Pick a chapter you have read and do its **easy** problems first — a few minutes each, one idea per problem.",
           "> 2. Work on paper, the way you will on the exam. Open the **hint** only after you have been stuck for a few minutes, and the **solution** only once you have an answer you would hand in.",
           "> 3. Compare with the **Answer.** line, then read the solution's *Check*: it shows how to test your own answer (run the DFA on a few strings, try $\\varepsilon$, try the shortest strings in and out of the language).",
           "> 4. Move on to **medium** (one exam part), then **hard** (a whole exam problem, about 20 minutes).",
           "> 5. A day later, redo every problem you got wrong, without looking.",
           "",
           "> [!tip] Before the final",
           "> Go chapter by chapter: read the chapter's *definition*, *template* and *trap* boxes, then do its easy problems and one medium. Leave the hard problems for a second pass, and write your handwritten cheat sheet from the [[0-toolkit/02-proof-templates|proof templates]] and the [[0-toolkit/04-review-regular-and-context-free|exam review]] pages.",
           "",
           "## The tag system",
           "",
           "Every problem's title bar carries one **difficulty tag** and one to three **topic tags**, for example",
           "",
           "> [!easy] Easy · fooling sets · true or false",
           "> The problem statement sits in this box; the folded *Hint* and *Solution* boxes below it open with a click.",
           "",
           "| difficulty | what it means | time |",
           "|---|---|---|"]
    for lv in LEVELS:
        out.append(f"| {chip(lv)} | {RUBRIC[lv]} | {TIME[lv]} |")
    out += ["",
            f"Browse: [[practice/easy|all {c['easy']} easy]] · [[practice/medium|all {c['medium']} medium]] · [[practice/hard|all {c['hard']} hard]] · [[practice/topics|by topic]] — {len(TOPICS)} topics that cut across chapters, plus the true-or-false checks and the find-the-error items.",
            "",
            "## By chapter",
            "",
            "| ch | chapter | practice | easy | medium | hard |",
            "|---|---|---|---|---|---|"]
    for pg in pages:
        C = pg["C"]
        sec = gh_slug(ch_heading(C))
        e, m, h = pg["counts"]
        out.append(f"| {C} | [[{CHAPTERS[C][0]}\\|{CHAPTERS[C][1]}]] | [[{pg['slug']}\\|{len(pg['probs'])} problems]] | "
                   f"[[practice/easy#{sec}\\|{e}]] | [[practice/medium#{sec}\\|{m}]] | [[practice/hard#{sec}\\|{h}]] |")
    out.append(f"| | **total** | **{tot}** | **{c['easy']}** | **{c['medium']}** | **{c['hard']}** |")
    out += ["",
            "Chapters 1–5 were the scope of Midterm 1; Chapters 6–7 (Turing machines and undecidability) are on the final. Chapters 8 and 9 have no practice pages: their material is mostly conceptual and is exercised by the true-or-false items of Chapters 6–7.",
            "",
            "## How the answers were checked",
            "",
            "Every regular expression, DFA, NFA, grammar and Turing machine in a solution is checked by a script against a brute-force definition of the language, over all strings up to length 10–14 (and exactly, by DFA equivalence, wherever the language is regular). Constructions such as language transformations are checked on many random DFAs. Induction proofs were checked step by step, and every claim they prove was tested on all short strings. Every solution was also proofread in the rendered page with its hint and solution unfolded. The scripts are in `tools/practice/checks/`.",
            ""]
    return "\n".join(out).rstrip() + "\n"


# ------------------------------------------------------------------ link injection
def inject_chapter_pages(pages):
    for pg in pages:
        C = pg["C"]
        path = CHAPTERS[C][0] + ".md"
        full = os.path.join(SRC, path)
        if not os.path.exists(full):
            print("  WARN missing chapter page", path)
            continue
        text = open(full, encoding="utf-8").read()
        lines = text.split("\n")
        n = len(pg["probs"])
        e, m, h = pg["counts"]
        first = pg["probs"][0]
        for i, ln in enumerate(lines):
            if ln.startswith(f"*Chapter {C} ·"):
                ln = re.sub(r" · practice: \[\[practice/[^\]]+\]\]", "", ln)
                assert ln.endswith("*"), path
                lines[i] = ln[:-1] + f" · practice: [[{pg['slug']}|{n} problems]]*"
                break
        else:
            raise SystemExit(f"no meta line in {path}")
        text = "\n".join(lines)
        text = re.sub(r"\n> \[!tip\] Practice this chapter\n(?:>.*\n)*\n", "\n", text)
        block = ("> [!tip] Practice this chapter\n"
                 f"> [[{pg['slug']}|{n} practice problems]] — {e} easy, {m} medium, {h} hard — each with a folded hint and a worked solution. "
                 f"Start with {plink(first)}; the [[practice/index|practice hub]] has the whole bank by difficulty and by topic.\n\n")
        k = text.find("### Sources for this page")
        if k < 0:
            text = text.rstrip("\n") + "\n\n" + block.rstrip("\n") + "\n"
        else:
            text = text[:k] + block + text[k:]
        write(path, text)


def inject_unit_indexes(pages):
    byC = {pg["C"]: pg for pg in pages}
    for path in UNIT_INDEXES:
        full = os.path.join(SRC, path)
        if not os.path.exists(full):
            print("  WARN missing unit index", path)
            continue
        lines = open(full, encoding="utf-8").read().split("\n")
        for i, ln in enumerate(lines):
            if ln.startswith("| # | page | one line |"):
                if not ln.rstrip().endswith("practice |"):
                    lines[i] = ln.rstrip() + " practice |"
                    lines[i + 1] = lines[i + 1].rstrip() + "---|"
                j = i + 2
                while j < len(lines) and lines[j].startswith("| "):
                    row = lines[j].rstrip()
                    cells = row.split(" | ")
                    mm = re.match(r"^\| (\d+) \|", row)
                    C = int(mm.group(1)) if mm else None
                    # drop an existing practice cell (the last cell) if the header already had it
                    ncols = lines[i].count("|") - 1
                    if row.count("|") - row.count("\\|") - 1 >= ncols:
                        row = re.sub(r" (\[\[practice/[^\]]*\]\]|—) \|$", "", row)
                    cell = f"[[{byC[C]['slug']}\\|{len(byC[C]['probs'])} problems]]" if C in byC else "—"
                    lines[j] = row + f" {cell} |"
                    j += 1
                break
        write(path, "\n".join(lines))


def inject_concepts(pages):
    allp = [p for pg in pages for p in pg["probs"]]
    for concept, keys in CONCEPT_TOPICS.items():
        path = f"concepts/{concept}.md"
        full = os.path.join(SRC, path)
        if not os.path.exists(full):
            print("  WARN missing concept page", path)
            continue
        text = open(full, encoding="utf-8").read()
        lines = [ln for ln in text.rstrip("\n").split("\n") if not ln.startswith("**Practice.**")]
        ps = [p for p in allp if set(p["topics"]) & set(keys)]
        if not ps:
            continue
        tl = " · ".join(f"[[practice/topics#{gh_slug(TOPIC_TITLE[k])}|{TOPIC_TITLE[k]}]] ({sum(1 for p in allp if k in p['topics'])} problems)"
                        for k in keys if any(k in p["topics"] for p in allp))
        home = CONCEPT_HOME.get(concept) or collections.Counter(
            p["C"] for p in allp if keys[0] in p["topics"]).most_common(1)[0][0] if any(keys[0] in p["topics"] for p in allp) else ps[0]["C"]
        ex = []
        for lv in LEVELS:
            q = [p for p in ps if p["level"] == lv]
            if q:
                q.sort(key=lambda p: (abs(p["C"] - home), p["C"], p["N"]))
                ex.append(f"{plink(q[0])} ({lv})")
        line = f"**Practice.** {tl} — for example " + ", ".join(ex) + "."
        idx = max((i for i, ln in enumerate(lines) if ln.startswith("Related:")), default=None)
        if idx is None:
            lines += ["", line]
        else:
            lines[idx:idx] = [line, ""]
        new = "\n".join(lines) + "\n"
        new = re.sub(r"\n{3,}", "\n\n", new)
        write(path, new)


def inject_practice_pages(pages):
    for i, pg in enumerate(pages):
        path = pg["slug"] + ".md"
        full = os.path.join(SRC, path)
        text = open(full, encoding="utf-8").read()
        lines = text.rstrip("\n").split("\n")
        for k, ln in enumerate(lines):
            if ln.startswith("*Practice for ") and "[[practice/topics" not in ln:
                lines[k] = ln[:-1] + " · [[practice/topics|by topic]]*"
                break
        while lines and (lines[-1].startswith("*Previous:") or lines[-1].startswith("*Next:") or lines[-1] == ""):
            lines.pop()
        parts = []
        if i > 0:
            parts.append(f"Previous: [[{pages[i-1]['slug']}|Chapter {pages[i-1]['C']} practice]]")
        if i + 1 < len(pages):
            parts.append(f"{'next' if parts else 'Next'}: [[{pages[i+1]['slug']}|Chapter {pages[i+1]['C']} practice]]")
        parts.append("[[practice/index|all practice]]")
        lines += ["", "*" + " · ".join(parts) + "*"]
        write(path, "\n".join(lines) + "\n")


if __name__ == "__main__":
    pages = load_all()
    total = bad = 0
    for pg in pages:
        total += len(pg["probs"])
        print(f"C{pg['C']:02d} {pg['file']:<48} {len(pg['probs']):>2} {pg['counts']}  errors={len(pg['errs'])}")
        for e in pg["errs"]:
            print("    ERR", e)
            bad += 1
    print("problems:", total, "errors:", bad)
    if "--write" in sys.argv:
        if bad:
            sys.exit("not writing: fix the errors first")
        write("practice/index.md", gen_hub(pages))
        for lv in LEVELS:
            write(f"practice/{lv}.md", gen_level_page(pages, lv))
        write("practice/topics.md", gen_topics_page(pages))
        inject_practice_pages(pages)
        inject_chapter_pages(pages)
        inject_unit_indexes(pages)
        inject_concepts(pages)
        cnt = collections.Counter(k for pg in pages for p in pg["probs"] for k in p["topics"])
        print("topics:", ", ".join(f"{k}={cnt[k]}" for k, _ in TYPES + TOPICS))
