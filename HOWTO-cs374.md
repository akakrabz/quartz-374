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
content/0-toolkit/                     notation, proof templates, big picture, two exam reviews, grading, errata
content/1-models-of-computation/       one page per book chapter (01-strings … 09-nondeterministic-turing-machines)
content/2-algorithms/                  Part 2: one page per book chapter (01-recursion …) and its solved exercises (01-recursion-exercises …)
content/3-homework-and-exams/          the course's own problems worked out: Midterm 1 practice tests 1–3, homework write-ups (HW6)
content/concepts/                      56 glossary pages (32 for Part 1, 24 for Part 2)
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
python3 tools/checks/ch04.py                                          # every claim on the Chapter 4 page (likewise ch01–ch09, concepts_*, problems_*, toolkit_2; Part 2: a01–a06, a01x–a06x, master_theorem; exams_mt1 for the practice tests)
python3 tools/practice/checks/ch03.py                                 # every answer in the Chapter 3 practice set
for f in tools/figs_*.py; do python3 "$f"; done; python3 tools/assemble.py   # regenerate and re-inline all figures
```

`tools/check.py` needs PyYAML and a KaTeX copy (present after `npm ci`). Every check script ends with `ALL OK`; the last outputs are saved next to them (`*.out`). They use `tools/automata/`, a small dependency-free library (DFA, NFA with ε-moves, regular expressions with exact equivalence, Thompson's construction, state elimination, context-free grammars with Earley parsing, Turing machines) — every regular expression, automaton, grammar, machine, trace, state count and fooling-set suffix on the site is compared with a brute-force definition of its language.

`tools/REVIEW-SPEC.md` is the independent-review procedure; the reviewers' logs are in `tools/review/`.

## 6. What's here (build 3, 2026-10-20 — Part 1 complete, Part 2 Chapters 1–6)

- **Part 1 · Models of Computation:** all nine chapters of Erickson's book, one page each (49 figures across the site).
- **32 concept pages**, **7 toolkit pages** (notation, proof templates, the big picture, review of Ch 1–5, review of Ch 6–9, how exams are graded, errata in the book), **11 worked problems**, and **60 practice problems** for Chapters 1–7 (24 easy, 20 medium, 16 hard), each with a folded hint and a worked solution.
- **Verification:** 22 check scripts, about 1,650 checks, all passing; `tools/check.py` passes on all 77 pages (1,745 links and anchors, 14,680 KaTeX expressions). Every chapter page, concept page and worked problem was then reviewed independently against the book PDFs; the reviews fixed about 30 statements (none changed a final answer) and found the book slips listed on the errata page.
- **Not done here:** the Quartz build itself (the npm registry was not reachable from the machine that wrote the site) — run §1 once before relying on the deployment.
- **Part 2 · Algorithms (build 2):** Chapters 1–3 of Erickson's *Algorithms* (recursion, backtracking, dynamic programming), one page each, plus a page of solved book exercises per chapter (13, 6 and 10 exercises; ♥ problems and anything equivalent to open homework skipped), 12 concept pages, 12 figures, and the recursive-algorithm and dynamic-programming rubrics and templates on the toolkit pages. Six check scripts (`a01`–`a03`, `a01x`–`a03x`), 611 checks, all passing; `tools/check.py` passes on all 95 pages (2,068 links and anchors, 19,314 KaTeX expressions). Each chapter and its exercises were reviewed independently (`tools/review/R7`–`R9`); the book slips found are on the errata page. Chapters 4–12 are listed as planned on the unit page.
- **Part 2, build 3:** Chapters 4–6 (greedy algorithms, basic graph algorithms, depth-first search) with solved exercises (9, 19 and 14), 11 more concept pages and a master-theorem page, the graph-reduction rubric (grading page §13) and the greedy and graph-reduction templates (proof templates §21–22), and the errata for Chapters 4–6. Checks `a04`–`a06`, `a04x`–`a06x` and `master_theorem` add about 600 checks; all 29 check scripts pass (about 2,450 checks), and `tools/check.py` passes on all 118 pages. Reviews: `tools/review/R10`–`R12`.

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
