# R27 — review of Part 3, notes A (FFT) and B (faster exponential algorithms)

Sources: `/home/claude/work/notes/A-fft.pdf`, `B-fastexpo.pdf`, every page rendered (100–500 dpi) and read; every
formula, figure and pseudocode compared with the page. Checks re-run: `tools/checks/na.py` (70 OK, ALL OK),
`tools/checks/nb.py` (66 OK, ALL OK, about 2 min). `tools/check.py --only` the four pages: OK.

## content/4-lecture-notes/a-fast-fourier-transforms.md

Checked: Horner/Evaluate counts (n vs 2n+2), table of representations, Lagrange formula, Vandermonde, collapsing sets
and X_1…X_8, root-of-unity properties, DFT, Radix2FFT vs Figure A.1, its correctness argument and operation counts,
T(n) = 2T(n/2)+Θ(n), DFT of [1,2,3,4], the factoring derivation (re-derived by hand: inner sum over j<q is order q,
outer over k<p is order p), corrected FactorFFT (re-derived: P*[s+tp] = Σ_k (Σ_j P[jq+k] ω_p^{sj}) ω_pq^{sk} ω_q^{tk}),
radix-2 as p = n/2, q = 2, T(pq) = qT(p)+pT(q)+O(pq), Lemma A.1 and proof, V for n = 4, both inverse algorithms vs
Figure A.3, FFTMultiply vs Figure A.4, (1+2x)(3+4x), 12×34, padding trap, bit reversal for n = 8, Figure A.5 (all 64
labels re-derived by hand: only row 1100 col 4 wrong), butterfly figure twiddles (ω^0; ω^0,ω^2; ω^0..ω^3), the added
IterativeFFT, the "skip bit reversal" claim (na.py: DIF without permutation + DIT inverse without permutation, exact on
200 pairs — a real check), exercises list, copying (7-gram overlap: only pseudocode and short phrases), aliases (unique).

Changes:
- §A.7: added the note error the writer missed — Figure A.3's generic InverseFFT prints `P ← FFT(P*)` (no conjugation
  of the input) and conjugates only the output, which computes conj(V)·conj(P*)/n: right only for real P*, and for a
  real polynomial returns the cyclically reversed coefficients ([3,0,8,10] instead of [3,10,8,0] on the page's
  example). The page's pseudocode was already correct; now the deviation is stated. Added to Sources error list and
  description ("inverse-FFT pseudocode").
- na.py: new check `A.7 ERROR p. 12 (Figure A.3, generic InverseFFT as printed …)`; docstring of the page's InverseFFT no
  longer claims it is the figure as printed.
- Summary: exercise 4 "in-place bit reversal" → "bit reversal in O(n) time" (the exercise asks for O(n) time, not in place).
- Exam box: "the course neither assigns this note nor covers the FFT" → "the note is not assigned this semester, and the
  textbook chapters the course follows do not develop the FFT" (course coverage of FFT is not in the course facts).
- Sources "Precision added": p. 2 says the sum of two degree-n polynomials "also has degree n" (at most n).

Writer's reported note errors: all confirmed (p. 4 Lagrange to n−1; p. 9 first-line summand; p. 10 "order q" for the
outer sum; p. 10 Figure A.2 P[jp+k], P*[j+kq], B[·,k], undefined C; p. 12 base case returns P; p. 13 row 1100 → 0011;
p. 15 hint "+1" → "+x^7"; p. 4 "exactly one polynomial of degree n" → at most n, distinct x_j).

Doubts (not changed): abstract/concept trap say coefficients → samples at arbitrary points is "Θ(n²)" — true of the
matrix–vector product, but fast multipoint evaluation does it in O(n log² n); "the same circuit with its stages grouped
differently" (§A.9) paraphrases the note's "same recursive structure, clustered differently" a little strongly.

## content/4-lecture-notes/b-fast-exponential-algorithms.md

Checked: every recurrence and characteristic polynomial, roots recomputed with numpy (1.8392868, complex pair
−0.4196433776 ± 0.6062907292i, modulus 0.7374; 1.7692924; φ; 1.4655712; 3^{1/3}; 1.3802776; 1.1673/1.1939; all 12
Tarjan–Trojanowski cases, max 1.2560202 for T(n−2)+T(n−8)+2T(n−10)), the characteristic-polynomial statement
(unique positive root, none of larger modulus — proved), 3Sat/Faster3Sat vs Figure B.1 and the branch variable counts,
pure-literal lemma, Local3Sat "iff" and call bound, Figure B.2 semantics, n/2 argument, the random-restart analysis
(P(r) ≥ V/2^n, failure ≤ e^{−n}, (3α)^α(1−α)^{1−α}, derivative, α = 1/4, base 3/2), MIS cases and Figure B.3, M(n)
values 1,2,3,4,6,9, B.3 drafts (3-coloring DP, Lawler, whatever-first 2^{n−2}, chromatic recurrence, Σ C(n,k)3^{k/3}),
unfinished parts summarized only (TSP warm-up line, the topics box), exercises list, both figures' numbers, copying.

Changes:
- Sources: the p. 9 "M(n) ≤ 2^n − 1" item moved out of "Errors in the note" into "Loose but not wrong" (the bound is
  true and the guess-and-confirm induction works: 2(2^{n−1}−1) ≤ 2^n−1; it is only weaker than 2^{n−1}).
- Sources: added p. 7, H(α) = (1/α)^α(1/(1−α))^{1−α} is called "the binary entropy function"; it is 2^{binary entropy}
  (the page text already said so; nb.py already checks it).
- nb.py: label of the Exercise 5(a) check corrected ("2^40 − 1.1e8 vs 6.0e9" → "2^40 − 3.7e8 = 1.1e12 vs 5.9e9").

Writer's reported note errors: confirmed — pp. 3, 5 no `return False`; p. 4 "non-increasing" with ≤ chain; p. 4 "exactly k
complex roots" (a_k); p. 4 −0.419643337 (true −0.4196433776, 8th decimal); p. 6 A_y, A_z undefined and wrong with one
shared array (right with copies); p. 11 1.25603² → ^n; p. 11 "O(2^{n/4} poly n) = O(1.1889^n)" — really backwards, not
just loose: the note's own convention (O(λ^n poly n) = O(1.83929^n), O(3^{n/3} poly n) = O(1.44225^n)) reads "=" left ⊆
right, and 2^{1/4} = 1.189207 > 1.1889; "can Rooij"; p. 12 3^{k/3} "of size k"; p. 13 Ex. 5(a) false for α > 1/2; typos
and "Figure ??" (pp. 4, 6, 10, 11). Refuted as an error: p. 9 2^n − 1 (true, weaker).

## content/concepts/fast-fourier-transform.md
Definition, recipe, traps and the squared example (samples [6, 1+3i, 0, 1−3i], wrap to [5,12,13,6], N = 8 exact) checked
by hand and by na.py. Aliases unique site-wide (case-insensitive). No change.

## content/concepts/np-hardness.md (link line only)
Note B link added to "Where it appears" and "Related:" — target and wording correct. (The note J / approximation-algorithms
links on the same lines belong to another writer; not reviewed.) No change.

Previews: A §A.7, Summary, exam box, Sources and B Sources, light mode — render correctly.
