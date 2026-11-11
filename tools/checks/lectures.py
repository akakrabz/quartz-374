#!/usr/bin/env python3
"""Checks for the lecture log, content/5-lecture-log/YYYY-MM-DD.md.

usage: python3 tools/checks/lectures.py "<course folder>/Transcripts"

For every lecture-day page:
  * the transcript file named in its "Sources for this page" paragraph exists in the given folder;
  * every string in double quotation marks in the page body (quote boxes and inline phrases) occurs in that
    transcript word for word, ignoring case and punctuation; text in [square brackets] inside a quotation is an
    editorial replacement and is skipped;
  * the page's file name, its `lecture:` frontmatter and the date in its meta line agree, and the weekday in the
    title is the weekday of that date;
  * the previous/next links in the meta line point to the neighboring lecture days;
  * the hub page links every lecture-day page.
The transcripts are outside the repository, so this script needs their folder as its argument."""
import datetime
import glob
import os
import re
import sys

FAIL = []


def check(name, cond, detail=""):
    print(("OK   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail != "" else ""))
    if not cond:
        FAIL.append(name)


def norm(s):
    s = s.lower().replace("’", "'")
    s = re.sub(r"[^a-z0-9' ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


if len(sys.argv) < 2:
    sys.exit(__doc__)
TDIR = sys.argv[1]
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "content", "5-lecture-log")
pages = sorted(glob.glob(os.path.join(ROOT, "[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].md")))
days = [os.path.basename(p)[:-3] for p in pages]
check(f"{len(pages)} lecture-day pages found", len(pages) >= 1, ", ".join(days))
hub = open(os.path.join(ROOT, "index.md"), encoding="utf-8").read()
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December"]
total = 0
for k, p in enumerate(pages):
    day = days[k]
    text = open(p, encoding="utf-8").read()
    fm = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    body, _, sources = text[fm.end():].partition("### Sources for this page")
    d = datetime.date.fromisoformat(day)
    title = re.search(r'^title: "(.*)"$', fm.group(1), re.M).group(1)
    check(f"{day}: frontmatter lecture date equals the file name", f'lecture: "{day}"' in fm.group(1))
    check(f"{day}: the title starts with the right weekday and date ({d.strftime('%a %b')} {d.day})",
          title.startswith(f"{d.strftime('%a %b')} {d.day} "), title[:20])
    long_date = f"{d.strftime('%A')}, {MONTHS[d.month - 1]} {d.day}, {d.year}"
    meta = body.strip().splitlines()[0]
    check(f"{day}: the meta line gives the date as {long_date}", long_date in meta)
    prev_ok = (k == 0 and "previous:" not in meta) or (k > 0 and f"previous: [[5-lecture-log/{days[k - 1]}|" in meta)
    next_ok = (k == len(days) - 1 and "next:" not in meta) or (k < len(days) - 1 and f"next: [[5-lecture-log/{days[k + 1]}|" in meta)
    check(f"{day}: previous/next links point to the neighboring lecture days", prev_ok and next_ok)
    check(f"{day}: linked from the hub page", f"[[5-lecture-log/{day}\\|" in hub or f"[[5-lecture-log/{day}|" in hub)
    m = re.search(r"\(file `([^`]+\.txt)`\)", sources)
    path = os.path.join(TDIR, m.group(1)) if m else ""
    found = bool(m) and os.path.isfile(path)
    check(f"{day}: the transcript named in the sources exists", found, m.group(1) if m else "no file named")
    if not found:
        continue
    tr = norm(open(path, encoding="utf-8").read())
    quotes = re.findall(r'"([^"\n]+)"', body)
    missing = []
    for q in quotes:
        pieces = [x for x in re.split(r"\[[^\]]*\]", q) if x.strip()]
        if not all(norm(x) in tr for x in pieces):
            missing.append(q[:80])
    total += len(quotes)
    check(f"{day}: all {len(quotes)} quoted strings occur word for word in the transcript", not missing, missing)
    src_quotes = [q for q in re.findall(r'"([^"\n]+)"', sources)]
    miss2 = [q[:60] for q in src_quotes if norm(q) not in tr]
    check(f"{day}: the {len(src_quotes)} transcript phrases cited in the sources occur in the transcript", not miss2,
          miss2)
check(f"{total} quotations checked in all", total > 0)

print()
print("ALL OK" if not FAIL else f"{len(FAIL)} FAILED: {FAIL}")
