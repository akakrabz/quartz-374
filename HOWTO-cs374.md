# CS/ECE 374 notes site — how to build, preview, host and extend

This folder is a **Quartz 5** site (`quartz.config.yaml`, `quartz.ts`, `content/`, `quartz/styles/custom.scss`) — the same setup as the ECE 329 site.
The notes are plain Markdown with Obsidian-style wikilinks and callouts, so `content/` also opens directly as an Obsidian vault.

## 1. Build and preview (first time)

Requirements: Node ≥ 22, npm ≥ 10.9, internet access for the two install steps.

```bash
cd ~/"Nextcloud/Notes/CS 374/quartz-374"
npm ci                        # Quartz's own dependencies
npx quartz plugin install --from-config   # clones + builds the plugins listed in quartz.config.yaml, writes quartz.lock.json
npx quartz build --serve      # http://localhost:8080  (rebuilds on save)
```

`npx quartz build` alone writes the static site to `public/`; add `-c $(nproc)` to parse with every core. Plain `npx quartz plugin install` only reinstalls from `quartz.lock.json`, which git does not track, so on a fresh clone it prints a warning and installs nothing — the build then fails with `Could not resolve "./.quartz/plugins"`. Use `--from-config` as above (or `npm run install-plugins`, which is what the Docker builder runs).

## 2. Hosting

### Docker / Portainer (what `docker-compose.yml` does)

Two services, exactly as for the 329 site:

- **builder** (`node:22-bookworm`) clones `https://github.com/akakrabz/quartz-374.git` into a volume, checks `master` every `SYNC_INTERVAL` (300 s), and rebuilds whenever the branch moves. It builds into a staging folder and swaps it in, so a failed build leaves the previous site serving (on the very first deploy there is no previous site).
- **web** (`nginx:1-alpine`) serves the built site on **port 8374** with the one rewrite rule Quartz needs.

Deploy: Portainer › Stacks › Add stack › paste `docker-compose.yml` (or `docker compose up -d`), and point the reverse proxy for `quartz-374.vops.ch` at port 8374. Publishing is then just `git push`. Needs Docker Compose ≥ 2.23.1 (inline `configs.content`).

### Any static web server

Quartz emits `page.html` files but links to them **without** the extension, and folders with a trailing slash. The server must try `$uri`, then `$uri.html`, then `$uri/`:

```nginx
location / {
    try_files $uri $uri.html $uri/ =404;
}
error_page 404 /404.html;
```

Opening `public/index.html` from disk (file://) does not work — search, graph and previews fetch JSON over HTTP. `configuration.baseUrl` in `quartz.config.yaml` is `quartz-374.vops.ch` (used only for the sitemap and social previews). External requests at page load: Google Fonts and jsdelivr (KaTeX CSS); analytics are off.

## 3. Layout

```
content/index.md                       home
content/0-toolkit/                     notation, proof templates, big picture, three exam reviews (Ch 1–5, Ch 6–9, Midterm 2 algorithms), grading, errata
content/1-models-of-computation/       one page per book chapter (01-strings … 09-nondeterministic-turing-machines)
content/2-algorithms/                  Part 2: one page per book chapter (01-recursion … 12-np-hardness) and its solved exercises (01-recursion-exercises …)
content/3-homework-and-exams/          the course's own problems worked out: Midterm 1 and 2 practice tests, labs 6a–12b (`tools/SPEC-labs.md`, checks `labs_06`–`labs_12b`), homework write-ups HW6–HW9 (checks `hw7`, `hw8`, `hw9`) and the HW10 study guide (check `hw10`)
content/4-lecture-notes/               Part 3: one info page per Erickson lecture note not in the books (01 … 13, 98, 99, a … j; `tools/SPEC-notes.md`, checks `n01`–`n13`, `n98`, `n99`, `na`–`nj`)
content/5-lecture-log/                 what was covered in class: one page per lecture day (`YYYY-MM-DD.md`), built from the recording transcripts, and a hub (`index.md`); see §8
content/concepts/                      95 glossary pages (32 for Part 1, 43 for Part 2, 20 for Part 3)
content/problems/                      11 worked exam-style problems
content/practice/                      7 practice pages (generated hub, easy/medium/hard and topic lists)
tools/                                 specs, checkers, figure generators, automata library (see §5)
```

The Explorer orders files by name (numeric prefixes), see `quartz.ts`; titles stay clean.

## 4. Writing conventions (so new pages match)

`tools/SPEC.md` is the full writing spec every page was written to, and `tools/SPEC-algorithms.md` adds the Part 2 rules (pseudocode in `text` blocks with `←`, the rubric write-up formats, the solved-exercises page format, checks `tools/checks/a0N.py` and `a0Nx.py`); the short version:

- **Chapter pages** keep the book's `##` section headings (`## 4.5 NFA to DFA: the subset construction`) — other pages link to those anchors. Frontmatter `title`, `description`, `tags` (`chapter`, topic tags, `midterm-1` for Ch 1–5), `chapter: N`. First line is the italic meta line (book pages, chapter PDF, prev/next); the practice link on it is added by the build script.
- **Concept pages** (`content/concepts/<slug>.md`): definition or key box, why it works, recipe or template, traps, one checked example, "Where it appears" with exact anchors, and `Related:` as the last line (the build script inserts the **Practice.** line just above it). Aliases must be unique across the site.
- **Math**: `$…$` inline, `$$…$$` on their own lines (prefixed with `> ` inside callouts). Explicit symbols in `\mathtt{…}`, named languages in `\textsf{…}`, `\varepsilon`, `\varnothing`, `\langle M\rangle`, `\rightsquigarrow`. No macros (the vault must render in Obsidian), no `\textsc`, never a literal `$` inside math or near it in running text (write "dollar sign"); inside tables use `\lvert…\rvert` and `\mid`, never a bare `|`.
- **Links** with full paths: `[[1-models-of-computation/04-nondeterministic-automata#45-nfa-to-dfa-the-subset-construction|§4.5]]`, `[[concepts/fooling-sets]]`. Inside tables escape the pipe: `[[concepts/dfa\|DFA]]`.
- **Callouts**: `definition`, `key`, `template`, `recipe`, `trap`, `exam`, `intuition`, `proof` (folded with `-`), `derivation`, `example`, plus the standard Obsidian ones; the practice pages add `easy`, `medium`, `hard`, `hint`, `solution`. Styles in `quartz/styles/custom.scss`. Never a blank line inside a callout.
- **Figures**: inline SVG blocks (`<figure class="cs-fig">…</figure>`, no blank lines inside), generated by `tools/figs_*.py` with `tools/figlib.py` (automata, trees, tapes). Strokes use `currentColor` and the variables `--accent`, `--accent2`, `--hi`, `--muted`, `--paper`, so dark mode works. A page marks a figure with `<!-- fig:NAME -->`; `python3 tools/assemble.py content/<page>.md` inlines it on the next line.

## 5. Checking without building

```bash
python3 tools/check.py content node_modules/katex/dist/katex.min.js   # links, anchors, KaTeX (strict), frontmatter, callouts, tables
python3 tools/checks/ch04.py                                          # every claim on the Chapter 4 page (likewise ch01–ch09, concepts_*, problems_*, toolkit_2; Part 2: a01–a12, a01x–a12x, master_theorem; labs_06–labs_12b; hw7, hw8, hw9, hw10; exams_mt1 and exams_mt2 for the practice tests; lectures "<course folder>/Transcripts" for the lecture log)
python3 tools/practice/checks/ch03.py                                 # every answer in the Chapter 3 practice set
for f in tools/figs_*.py; do python3 "$f"; done; python3 tools/assemble.py   # regenerate and re-inline all figures
```

`tools/check.py` needs PyYAML and a KaTeX copy (present after `npm ci`). Every check script ends with `ALL OK`; the last outputs are saved next to them (`*.out`). They use `tools/automata/`, a small dependency-free library (DFA, NFA with ε-moves, regular expressions with exact equivalence, Thompson's construction, state elimination, context-free grammars with Earley parsing, Turing machines) — every regular expression, automaton, grammar, machine, trace, state count and fooling-set suffix on the site is compared with a brute-force definition of its language.

`tools/REVIEW-SPEC.md` is the independent-review procedure; the reviewers' logs are in `tools/review/`.

## 6. What's here (build 7, 2026-11-10 — Parts 1–3 complete, labs 6a–12b, HW6–9, HW10 study guide, Midterm 2 review, lecture log Oct 20 – Nov 10)

- **Part 1 · Models of Computation:** all nine chapters of Erickson's book, one page each (49 figures across the site).
- **32 concept pages**, **7 toolkit pages** (notation, proof templates, the big picture, review of Ch 1–5, review of Ch 6–9, how exams are graded, errata in the book), **11 worked problems**, and **60 practice problems** for Chapters 1–7 (24 easy, 20 medium, 16 hard), each with a folded hint and a worked solution.
- **Verification:** 22 check scripts, about 1,650 checks, all passing; `tools/check.py` passes on all 77 pages (1,745 links and anchors, 14,680 KaTeX expressions). Every chapter page, concept page and worked problem was then reviewed independently against the book PDFs; the reviews fixed about 30 statements (none changed a final answer) and found the book slips listed on the errata page.
- **Not done here:** the Quartz build itself (the npm registry was not reachable from the machine that wrote the site) — run §1 once before relying on the deployment.
- **Part 2 · Algorithms (build 2):** Chapters 1–3 of Erickson's *Algorithms* (recursion, backtracking, dynamic programming), one page each, plus a page of solved book exercises per chapter (13, 6 and 10 exercises; ♥ problems and anything equivalent to open homework skipped), 12 concept pages, 12 figures, and the recursive-algorithm and dynamic-programming rubrics and templates on the toolkit pages. Six check scripts (`a01`–`a03`, `a01x`–`a03x`), 611 checks, all passing; `tools/check.py` passes on all 95 pages (2,068 links and anchors, 19,314 KaTeX expressions). Each chapter and its exercises were reviewed independently (`tools/review/R7`–`R9`); the book slips found are on the errata page. Chapters 4–12 are listed as planned on the unit page.
- **Part 2, build 3:** Chapters 4–6 (greedy algorithms, basic graph algorithms, depth-first search) with solved exercises (9, 19 and 14), 11 more concept pages and a master-theorem page, the graph-reduction rubric (grading page §13) and the greedy and graph-reduction templates (proof templates §21–22), and the errata for Chapters 4–6. Checks `a04`–`a06`, `a04x`–`a06x` and `master_theorem` add about 600 checks; all 29 check scripts pass (about 2,450 checks), and `tools/check.py` passes on all 118 pages. Reviews: `tools/review/R10`–`R12`.
- **Part 2, build 4:** Chapters 7–9 (minimum spanning trees, shortest paths, all-pairs shortest paths) with solved exercises (10, 16 and 10), 9 more concept pages, figures on every page, errata for Chapters 7–9; checks `a07`–`a09`, `a07x`–`a09x`; reviews `tools/review/R15`–`R17`. Also the lab pages 6a–9b (`content/3-homework-and-exams/lab-*.md`, reviews R13–R14).
- **Part 2, build 5:** Chapters 10–12 (maximum flows and minimum cuts, applications of flows and cuts, NP-hardness) with solved exercises (10, 10 and 13), 10 more concept pages, figures, errata for Chapters 10–12 (including a 3SAT → Hamiltonian-cycle reduction that is wrong as printed, repaired on the page); checks `a10`–`a12`, `a10x`–`a12x`, `a12c`; reviews `tools/review/R20`–`R23`. The **Midterm 2 review** (`0-toolkit/08-review-algorithms.md`, checks `review_mt2`, review R19), the official Midterm 2 scope on the grading page and in every chapter's exam box, the NP-hardness rubric (grading §14) and template (proof templates §23), and the HW7 write-up (check `hw7`). Flows are marked as not part of CS 374 this semester; NP-hardness as final-only.
- **Part 3, build 6:** 25 info pages for Erickson's lecture notes outside the two books — Director's Cut 1–13, Appendices I–II (induction, recurrences), Extended Dance Remix A–J — and 20 concept pages, written to `tools/SPEC-notes.md` (sources and facts in `/home/claude/work/notes/`). The notes are rougher than the books: every page lists the errors found in its note (well over a hundred in all, the substantive ones collected on the errata page), each checked by its script `tools/checks/n<id>.py`; reviews `tools/review/R24`–`R36`.
- **Build 7 (2026-11-10):** additions from new course material. (1) **Lab pages 11, 12a and 12b** (`content/3-homework-and-exams/lab-11.md`, `lab-12a.md`, `lab-12b.md`; no official solutions in the folder, so the solutions are ours): Lab 11 solves two problems both as a dynamic program and as a graph reduction (its example dag is transcribed from the handout's figure: 14 vertices, 27 edges); Lab 12a turns decision boxes into optimization and search algorithms; Lab 12b proves five variants of Sat NP-hard and solves XorSat; checks `labs_11` (30 checks), `labs_12a` (45) and `labs_12b` (55), all passing; not yet reviewed independently. (1b) **Homework pages HW8 and HW9** (`hw8-graph-algorithms.md`, `hw9-more-graph-algorithms.md`), written from the student's own submitted solutions (`workspace/hw8 (1).pdf`, `workspace/hw9 (1).pdf`) in the walkthrough format of HW6–7: each solution re-derived, checked by `hw8` (25 checks) and `hw9` (22 checks), and followed by a box "Changed from the submitted version" that says what was corrected. Their handouts are not in the course folder; the statements are paraphrased from the handouts on the course website (`…/cs374al1/fa2026/homeworks/hw8.pdf`, `hw9.pdf`), and the posted solutions there (`…/solutions/hw8-sol.pdf`, `hw9-sol.pdf`) were used for comparison. `workspace/hw7.pdf` (the submitted HW7) agrees in substance with the existing HW7 page, which was left unchanged. (2) **Homework 10** was open (due November 17, no solutions posted), so `hw10-np-hardness.md` is a **study guide without solutions** to Problems 1 and 2 — what each part practices, its rubric, a checklist, test instances and links to parallel problems on the site — with the handout's own solved problem explained; check `hw10` verifies only the definitions, the handout's examples and the handout's published reduction. Replace it by a worked write-up once the deadline has passed. (3) **The lecture log** (`content/5-lecture-log/`): one page per lecture day for the six recording transcripts in `Transcripts/` — `686987472…` = Tue Oct 20, `687888532…` = Thu Oct 22, `689453872…` = Tue Oct 27, `690425642…` = Thu Oct 29, `692290403…` = Tue Nov 3, `694494693…` = Tue Nov 10 — and a hub; format in §8. These six are all the transcripts used so far. Check `lectures` (50 checks; run it with the transcripts folder as its argument) confirms that every quotation on those pages occurs word for word in its transcript and that dates, weekdays and previous/next links agree. `tools/check.py` passes on all 226 pages (4,821 links and anchors, 54,740 KaTeX expressions).

## 7. The practice bank: adding or changing problems

Each page is `content/practice/0N-<chapter-slug>.md`; problems are numbered `C.1 … C.n`, easy first, then medium, then hard. Every problem is exactly:

```markdown
### 3.1 Short title

> [!easy] Easy · fooling sets · true or false
> (statement)
>
> *Source: original.*

> [!hint]- Hint
> (required for medium and hard)

> [!solution]- Solution
> (setup, work, check)
>
> **Answer.** (final answer)
```

Tags come from a fixed vocabulary (`tools/practice/SPEC.md` §4); a new tag must be added to `RULES` in `tools/practice/build_practice.py`. After editing:

```bash
python3 tools/practice/build_practice.py           # validate only
python3 tools/practice/build_practice.py --write   # regenerate hub, easy/medium/hard, topics; refresh practice links on chapter, unit and concept pages
```

The expected counts per chapter are in `EXPECT` at the top of the script. To add Part 2 practice later, add its chapters to `CHAPTERS` and its unit index to `UNIT_INDEXES`.

## 8. The lecture log: adding a lecture day

`content/5-lecture-log/` records **what was covered in class**, one page per lecture day, from the automatic transcripts of the lecture recordings (`Transcripts/<recording number> - <id> - PID <n>.txt` in the course folder; one long line each, no dates inside). A page is a record of the day, not a re-teaching: it links to the chapter, concept and lab pages for the explanations.

- **File:** `content/5-lecture-log/YYYY-MM-DD.md`; the Explorer sorts by file name, so the days stay in order. Frontmatter `title` (`"Tue Oct 20 — three or four topics"`), `description`, `tags: [lecture, algorithms, <topic>]` (plus `midterm-2` for material that exam covered), `lecture: "YYYY-MM-DD"`.
- **The date** comes from the opening announcements (which homework is due "today", which lab is "tomorrow"), cross-checked with the lab and homework dates already on the site; say how in the page's sources, and say so if it is uncertain. §6 lists which transcript file is which day — a transcript not listed there is new.
- **Sections, in this order:** the italic meta line (date, book chapter, previous/next day, hub link); `> [!abstract] The day in one breath`; `## Announcements`; `## What was covered, in order` (a numbered list, each item ending with `→` links to the exact chapter section and concept page); `## Examples and problems worked in class` (a reduction worked in class is recorded in the rubric's parts, as given in class); `## What the instructor said about …` (`[!quote]` boxes and one `[!exam]` box); `## Where this is on the site` (a table: topic, explained in, practice); `### Sources for this page`.
- **Quotations** — whole sentences in `[!quote]` callouts, short phrases in quotation marks in the text — are the transcript's own words, and quotation marks are used for nothing else on these pages; only punctuation and capitalization are added, and a word in [square brackets] replaces an obvious transcription error (name it in the sources). Never reconstruct a quotation; summarize instead. The slides are not in a transcript: describe a figure only as far as it was described aloud.
- **After adding a day:** set `next:`/`previous:` on the neighboring pages, add a row to the tables of `content/5-lecture-log/index.md` (the day, and anything announced), add the day to the list on `content/index.md`, add the transcript-to-date line to §6, and run `tools/check.py` and `python3 tools/checks/lectures.py "<course folder>/Transcripts" | tee tools/checks/lectures.out` (every quoted string must be in the transcript named in the page's sources as ``(file `…txt`)``).

**Homework pages from the student's own solutions** (HW8, HW9) follow the HW6–7 walkthrough format: the statement, "what has to be remembered", the answer in its rubric's parts, why it is correct, the time, an example, the traps — and after each part a `> [!note] Changed from the submitted version` box listing every difference from what was handed in (or "nothing"). Present the submitted approach; correct it where it is wrong; never silently replace it. If the handout is not in the course folder, take the statement from the course website and say so in the sources.

Homework that is still open (due date not passed, no official solutions in the course folder) gets a **study guide** in `content/3-homework-and-exams/` — the statements, what each part practices, the rubric, a checklist, test instances and links to parallel problems on the site — and no solutions; its check script must not contain a solution either.
