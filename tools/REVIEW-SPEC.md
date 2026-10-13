# Independent review — CS/ECE 374 site (Models of Computation)

You review pages that other writers wrote. You did not write them, so treat nothing as right until you have
checked it yourself. The reader uses this site to study for exams: a wrong statement is worse than a missing one.

## Sources

- Erickson's chapter PDFs (URLs in `/home/claude/work/book-facts.md`). Read them with WebFetch; direct downloads
  (curl, Python) are blocked by the proxy. Ask WebFetch focused questions ("What exactly does Lemma 4.5 state?",
  "Quote the definition of …") rather than for a whole-chapter summary.
- `/home/claude/work/moc-notes.tex` (chapter notes written earlier for this student) and
  `/home/claude/work/book-facts.md` (verified section titles, theorem numbers, course and rubric facts).
- `tools/SPEC.md` — the rules the writers followed (layout, notation, callouts, links, style).

## What to check on every assigned page

1. **Mathematics.** Every definition, statement, proof and proof sketch, example, table entry, trap and figure
   caption. Re-derive it; do not trust it. Hot spots: quantifiers (some/every), the direction of a reduction,
   "rejects" versus "does not accept", ε and ∅ edge cases, off-by-one counts, accepting-state sets of constructions,
   decidable/acceptable classifications, closure claims, which machine is run on what.
2. **Agreement with the book.** Section numbers and titles, theorem/lemma numbers and statements, definitions.
   A deviation from the book is fine only if it is correct and the page says so (e.g. a fixed book typo).
3. **The check script really checks the page.** Open the page's check script (`tools/checks/…`), confirm that 5–10
   of the most important concrete claims are checked as stated on the page (same automaton, same expression, same
   predicate), and run it. It must still end with `ALL OK`.
4. **Consistency with the site.** Notation (SPEC §5), names of languages and machines, cross-links pointing at the
   right section, and no contradiction with other pages you have read.
5. **Exam usefulness.** Definitions and templates precise enough to copy onto a cheat sheet; no misleading
   simplification; traps that are really traps.
6. **License and style.** No sentence copied from the book (paraphrase is fine). No "clearly", "obviously",
   "trivially" in proofs. No mention of the notes, the spec or the checks outside "Sources for this page".

## What to do

- **Fix clear errors in place with minimal edits.** Do not restyle, restructure or shorten pages. If a fix changes a
  claim that the check script covers, adjust or add the check and re-run the script (save the `.out`). If a figure
  is wrong, fix the data in its figure script, regenerate, and run `python3 tools/assemble.py <that page>` only.
- Edit only the pages assigned to you (and their check/figure scripts). Never edit `tools/automata/*`,
  `tools/figlib.py`, `tools/check.py`, `tools/assemble.py`, the SPEC files, `quartz/*`, or pages of other reviewers.
  Other agents are working in the same repository at the same time.
- After editing, run
  `python3 tools/check.py content /opt/npm-tools/node_modules/katex/dist/katex.min.js --only <your page prefixes>`.
  The only acceptable errors are "wikilink target not found" for pages that are still being written
  (`0-toolkit/*`, `1-models-of-computation/04-nondeterministic-automata`, `practice/index|easy|medium|hard`,
  `2-algorithms/index`).
- Screenshots are needed only if you change a figure or a complicated display; then look at that part in light mode
  (`python3 /home/claude/work/preview/pageshot.py content/<page>.md /tmp/x.png light`).
- Keep a log in `tools/review/<your-log-name>.md`: per page, what you checked, every change (before → after, and
  why), and every remaining doubt. Factual and short.
- **Final message:** per page, the changes you made and why; anything you are unsure about; and any statement you
  fixed that also appears on a page you were not assigned (so the coordinator can propagate it).
